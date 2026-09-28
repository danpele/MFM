"""
ai_discovery_case.py -- Capitolul 13, secțiunea "AI for Scientific Discovery": mini-studiul de caz
==================================================================================================
Scenariu: un asistent AI propune o familie largă de variabile tehnice pentru a prognoza randamentul S&P 500.
Testăm fiecare pereche (variabilă, orizont) cu o regresie predictivă și corectăm pentru testarea multiplă.
  * perioada de descoperire: 2001--2015; perioada de verificare (holdout): 2016--2026
  * y_{t,h} = log P_{t+h} - log P_t, h in {1, 5, 20}; x_t standardizat; t Newey--West cu max(h, 5) întârzieri
  * corecții: Holm (FWER 5%), Benjamini--Hochberg (FDR 10%), pragul |t| > 3 (Harvey, Liu & Zhu, 2016)
  * nulul comun: deplasări circulare ale țintei (păstrează dependența dintre variabile și autocorelația),
    cuantila de 95% a max |t| pe toate testele
Ieșire: ai_discovery_case.json
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_ml import load_data, rsi  # noqa: E402

SEED = 42
HORIZONS = (1, 5, 20)
DISC = ('2001-01-01', '2015-12-31')
HOLD = ('2016-01-01', '2026-09-18')


def features(close, vix):
    lp = np.log(close)
    r = lp.diff()
    f = pd.DataFrame(index=close.index)
    for h in (1, 2, 3, 5, 10, 20, 40, 60, 120, 250):
        f[f'mom_{h}'] = lp.diff(h)
    for w in (5, 10, 20, 50, 100, 200):
        f[f'dist_ma{w}'] = lp - lp.rolling(w).mean()
    vol = {w: r.rolling(w).std() * np.sqrt(252) for w in (5, 10, 20, 60, 120)}
    for w, v in vol.items():
        f[f'vol_{w}'] = v
    for a, b in ((5, 20), (10, 60), (20, 60), (20, 120)):
        f[f'volratio_{a}_{b}'] = vol[a] / vol[b]
    for n in (7, 14, 21, 28):
        f[f'rsi_{n}'] = rsi(close, n)
    lv = np.log(vix.reindex(close.index).ffill())
    f['vix_level'] = lv
    for h in (1, 5, 20):
        f[f'vix_chg_{h}'] = lv.diff(h)
    f['vix_minus_rv20'] = vix.reindex(close.index).ffill() / 100 - vol[20]
    return f


def nw_tstats(Y, X, lags):
    """t-uri Newey--West pentru pantele regresiilor univariate y_j ~ 1 + x_j (coloane aliniate)."""
    out = np.empty(X.shape[1])
    for j in range(X.shape[1]):
        x, y = X[:, j], Y
        m = ~(np.isnan(x) | np.isnan(y))
        x, y = x[m], y[m]
        xc = x - x.mean()
        b = (xc @ (y - y.mean())) / (xc @ xc)
        u = (y - y.mean()) - b * xc
        g = xc * u
        T = len(g)
        s = g @ g
        for L in range(1, lags + 1):
            s += 2 * (1 - L / (lags + 1)) * (g[L:] @ g[:-L])
        out[j] = b / (np.sqrt(s) / (xc @ xc))
    return out


def main():
    close = load_data('sp500')['Close']
    vix = load_data('vix')['Close']
    F = features(close, vix)
    lp = np.log(close)
    names = list(F.columns)
    res = {}
    rng = np.random.default_rng(SEED)
    tdisc, thold, maxnull = [], [], []
    shifts = rng.integers(250, 3000, size=500)
    for h in HORIZONS:
        y = (lp.shift(-h) - lp)
        lags = max(h, 5)
        d = F.loc[DISC[0]:DISC[1]]
        yd = y.loc[d.index].values
        Xd = ((d - d.mean()) / d.std()).values
        tdisc.append(nw_tstats(yd, Xd, lags))
        dh = F.loc[HOLD[0]:HOLD[1]]
        yh = y.loc[dh.index].values
        thold.append(nw_tstats(yh, ((dh - dh.mean()) / dh.std()).values, lags))
        # nul: ținta deplasată circular (fără valorile lipsă de la capăt)
        ok = ~np.isnan(yd)
        mx = []
        for s in shifts:
            ys = yd.copy()
            ys[ok] = np.roll(yd[ok], s)
            mx.append(np.nanmax(np.abs(nw_tstats(ys, Xd, lags))))
        maxnull.append(mx)
    tdisc = np.concatenate(tdisc)
    thold = np.concatenate(thold)
    maxnull = np.max(np.array(maxnull), axis=0)   # max pe toate orizonturile, pe fiecare replicare
    labels = [f'{n}|h{h}' for h in HORIZONS for n in names]
    M = len(tdisc)
    p = 2 * (1 - stats.norm.cdf(np.abs(tdisc)))
    order = np.argsort(p)
    # Holm
    holm = np.zeros(M, bool)
    for k, i in enumerate(order):
        if p[i] <= 0.05 / (M - k):
            holm[i] = True
        else:
            break
    # Benjamini--Hochberg, q = 10%
    ps = p[order]
    kmax = np.max(np.where(ps <= 0.10 * np.arange(1, M + 1) / M)[0], initial=-1)
    bh = np.zeros(M, bool)
    if kmax >= 0:
        bh[order[:kmax + 1]] = True
    crit = float(np.quantile(maxnull, 0.95))
    raw = np.abs(tdisc) > 1.96
    same = raw & (np.sign(thold) == np.sign(tdisc)) & (np.abs(thold) > 1.96)
    best = int(np.argmax(np.abs(tdisc)))
    res = {
        'n_features': len(names), 'n_tests': int(M), 'horizons': list(HORIZONS),
        'disc': list(DISC), 'hold': list(HOLD),
        'n_raw': int(raw.sum()), 'expected_false': float(0.05 * M),
        'n_holm': int(holm.sum()), 'n_bh': int(bh.sum()), 'n_t3': int((np.abs(tdisc) > 3).sum()),
        'maxt_crit95': crit, 'n_maxt': int((np.abs(tdisc) > crit).sum()),
        'n_replicate': int(same.sum()),
        'best': labels[best], 'best_t': float(tdisc[best]), 'best_t_hold': float(thold[best]),
        'best_p_raw': float(p[best]),
        'raw_list': [(labels[i], round(float(tdisc[i]), 2), round(float(thold[i]), 2)) for i in np.where(raw)[0]],
    }
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()

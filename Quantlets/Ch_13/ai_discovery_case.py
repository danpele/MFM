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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
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
        'labels': labels, 't_disc': [float(x) for x in tdisc], 't_hold': [float(x) for x in thold],
        'bh_t_cut': float(np.min(np.abs(tdisc[bh]))) if bh.any() else None,
        'holm_t_first': float(stats.norm.ppf(1 - 0.05 / (2 * M))),
    }
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k not in ('labels', 't_disc', 't_hold')}, indent=2))
    fig_ai_tstats(res)


def fig_ai_tstats(res):
    """Graficul mini-studiului de caz: |t| ordonate cu pragurile corecțiilor și verificarea pe holdout."""
    import matplotlib.pyplot as plt
    from generate_all_charts import MainBlue, IDAred, Forest, Amber, Purple, Orange, save_fig
    td, th = np.array(res['t_disc']), np.array(res['t_hold'])
    order = np.argsort(-np.abs(td))
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.3), gridspec_kw={'width_ratios': [1.35, 1]})
    ax = axes[0]
    k = np.arange(1, len(td) + 1)
    ax.bar(k, np.abs(td[order]), color=[MainBlue if abs(t) > 1.96 else Amber for t in td[order]], width=0.85)
    for y, c, ls, lab in ((1.96, 'black', ':', '|t| = 1.96: 21 of 102 pass'),
                          (res['bh_t_cut'], Forest, '--', 'BH, FDR 10%: 13 pass'),
                          (3.0, Purple, '-.', '|t| > 3: 4 pass'),
                          (res['maxt_crit95'], IDAred, '-', 'joint null, 95%% of max|t| = %.2f: 1 passes' % res['maxt_crit95']),
                          (res['holm_t_first'], Orange, '--', 'Holm first step, FWER 5%%: |t| > %.2f, none' % res['holm_t_first'])):
        ax.axhline(y, color=c, ls=ls, lw=1.0, label=lab)
    ax.set_xlabel('test rank (34 features x 3 horizons, ordered by |t|)'); ax.set_ylabel('|Newey-West t|, 2001-2015')
    ax.set_xlim(0, len(td) + 1)
    ax.set_title('Discovery sample: how many tests survive?', loc='left')
    ax = axes[1]
    raw = np.abs(td) > 1.96
    same = raw & (np.sign(th) == np.sign(td)) & (np.abs(th) > 1.96)
    ax.scatter(td[~raw], th[~raw], s=10, color=Amber, alpha=0.8, label='|t| < 1.96 in discovery')
    ax.scatter(td[raw & ~same], th[raw & ~same], s=16, color=MainBlue, label='discovery |t| > 1.96, fails in holdout')
    ax.scatter(td[same], th[same], s=26, color=IDAred, marker='D', label='replicates: same sign, |t| > 1.96')
    lim = 4.0
    ax.plot([-lim, lim], [-lim, lim], color='black', ls=':', lw=0.8)
    for v in (-1.96, 1.96):
        ax.axhline(v, color='black', lw=0.5, ls='--'); ax.axvline(v, color='black', lw=0.5, ls='--')
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel('t, discovery 2001-2015'); ax.set_ylabel('t, holdout 2016-2026')
    ax.set_title('Holdout check', loc='left')
    plt.tight_layout()
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=7.5)
    save_fig('ch13_ai_tstats')


if __name__ == '__main__':
    main()

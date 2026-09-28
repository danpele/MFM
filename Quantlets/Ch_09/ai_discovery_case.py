"""
ai_discovery_case.py -- Capitolul 9, secțiunea „AI pentru descoperire științifică”: mini-caz
============================================================================================
Întrebare: este H ~ 0,1 al log-volatilității SPY un fapt sau un efect al erorii de măsurare din RV?

  * Pasul 0 (replicare): H din legea de scalare Gatheral--Jaisson--Rosenbaum, Delta = 1..30 zile,
    q in {0.5, 1, 1.5, 2, 3} (cifra din curs), pe RV totală (intraday + randamentul peste noapte la pătrat)
  * Implicație testabilă a erorii de măsurare i.i.d. e_t în log sigma_t:
        m(2, Delta) = c * Delta^(2H) + 2 Var(e)   (termen constant, independent de Delta)
    => H estimat crește când renunțăm la întârzierile mici; un ajustaj neliniar cu termen constant îl corectează
  * Estimări: H pe Delta = 1..30, 5..30, 10..50; ajustaj neliniar m(2, Delta) = c Delta^(2H) + k pe Delta = 1..50;
    bootstrap pe blocuri (blocuri de 60 de zile, 300 de replicări) pentru H corectat
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rv_tools as T   # noqa: E402

QS = (0.5, 1.0, 1.5, 2.0, 3.0)
SEED = 42


def H_scaling(x, lags):
    """H = panta prin origine a lui zeta_q = q H (ca în curs)."""
    ro = T.roughness(x, QS, lags)
    q = np.array(QS)
    z = np.array([ro['zeta'][v] for v in QS])
    return float(np.sum(q * z) / np.sum(q * q))


def m2(x, lags):
    return np.array([np.mean((x[d:] - x[:-d]) ** 2) for d in lags])


def H_corrected(x, lags=range(1, 51)):
    """Ajustaj neliniar m(2, D) = c D^(2H) + k, k >= 0 (pătrate minime pe log m)."""
    lags = np.array(list(lags), dtype=float)
    y = m2(x, lags.astype(int))

    def res(p):
        c, H, k = np.exp(p[0]), p[1], np.exp(p[2])
        return np.log(c * lags ** (2 * H) + k) - np.log(y)
    best = None
    for H0 in (0.1, 0.3, 0.5):
        for f in (0.1, 0.5):
            p0 = [np.log((1 - f) * y[0]), H0, np.log(f * y[0])]
            s = optimize.least_squares(res, p0, bounds=([-50, 0.001, -50], [50, 1.5, 50]))
            if best is None or s.cost < best.cost:
                best = s
    c, H, k = np.exp(best.x[0]), best.x[1], np.exp(best.x[2])
    return dict(H=float(H), k=float(k), share_k_lag1=float(k / y[0]))


def main():
    rv = pd.read_csv(os.path.join(HERE, 'ch9_rv_spy.csv'), index_col=0, parse_dates=True)
    out = {}
    for col in ('rv_total', 'rv_intraday'):
        x = 0.5 * np.log(rv[col].values)
        d = dict(n=int(len(x)),
                 H_1_30=H_scaling(x, range(1, 31)),
                 H_5_30=H_scaling(x, range(5, 31)),
                 H_10_50=H_scaling(x, range(10, 51)))
        d.update({f'nls_{k}': v for k, v in H_corrected(x).items()})
        boot = T.block_bootstrap(x, lambda z: H_corrected(z)['H'], 60, 300, SEED)
        d['nls_H_lo'] = float(np.percentile(boot, 2.5))
        d['nls_H_hi'] = float(np.percentile(boot, 97.5))
        out[col] = d
    # verificarea puterii: mișcare browniană (H = 0,5) plus zgomot i.i.d., același design ca Seminarul 9 (B8)
    rng = np.random.default_rng(SEED)
    n = len(rv)
    x = np.cumsum(0.1 * rng.standard_normal(n))
    x = x - np.linspace(0, x[-1], n)
    xn = x + 0.25 * rng.standard_normal(n)
    out['sim_bm_noise'] = dict(H_1_30=H_scaling(xn, range(1, 31)), H_5_30=H_scaling(xn, range(5, 31)),
                               H_10_50=H_scaling(xn, range(10, 51)), nls_H=H_corrected(xn)['H'])
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()

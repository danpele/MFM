"""
ai_discovery_case.py -- Capitolul 17, mini-caz „AI pentru descoperire stiintifica”
==================================================================================
Ipoteza testata: un indicator de incredere LPPLS pozitiv anunta un crah.
  H0: P(scadere >= 20% in 90 de zile | indicator > 0) = P(scadere >= 20% in 90 de zile | indicator = 0)
  H1: probabilitatea este mai mare cand indicatorul este pozitiv (test unilateral)
  * indicatorul si evenimentul (definite ca in capitol) sunt ambele puternic autocorelate (ferestre suprapuse),
    deci testul exact al lui Fisher pentru proportii independente nu este valid;
  * inferenta prin permutari circulare: semnalul este rotit fata de seria evenimentelor (toate rotatiile
    cu cel putin 26 de observatii), ceea ce pastreaza autocorelatia ambelor serii.
  * grila de robustete: orizont 30/60/90/180 de zile x prag 10/20/30%, cu corectie Holm pentru 12 teste.
Datele: data/market (Bitcoin, Nasdaq 100) si indicatorii salvati in ch17_lppls_ci_btc.csv / ch17_lppls_ci_ndx.csv.
Iesire: ai_discovery_case.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import price  # noqa: E402

MIN_SHIFT = 26


def hits(ci, p, horizon, fall):
    out = []
    for d in ci.index:
        fut = p.loc[d:d + pd.Timedelta(days=horizon)]
        out.append(fut.min() / fut.iloc[0] - 1 <= -fall)
    return np.array(out, dtype=float)


def rotation_test(on, hit):
    """Diferenta p_on - p_off si valoarea p unilaterala prin rotatii circulare ale semnalului."""
    def stat(s):
        return hit[s].mean() - hit[~s].mean()
    obs = stat(on)
    n = len(on)
    null = np.array([stat(np.roll(on, k)) for k in range(MIN_SHIFT, n - MIN_SHIFT + 1)])
    return obs, float((np.sum(null >= obs) + 1) / (len(null) + 1)), len(null)


def holm(p):
    p = np.asarray(p)
    order = np.argsort(p)
    adj = np.empty_like(p)
    m = len(p)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (m - i) * p[j])
        adj[j] = min(1.0, run)
    return adj


def main():
    res = {}
    for key, fname in [('btc', 'ch17_lppls_ci_btc.csv'), ('ndx', 'ch17_lppls_ci_ndx.csv')]:
        ci = pd.read_csv(os.path.join(HERE, fname), index_col='date', parse_dates=True)['ci']
        p = price(key, 'D')
        on = (ci.values > 0)
        h = hits(ci, p, 90, 0.20)
        obs, pv, nrot = rotation_test(on, h)
        grid = []
        for hor in [30, 60, 90, 180]:
            for fall in [0.10, 0.20, 0.30]:
                hh = hits(ci, p, hor, fall)
                o, q, _ = rotation_test(on, hh)
                grid.append(dict(horizon=hor, fall=fall, diff=o, p=q))
        adj = holm([g['p'] for g in grid])
        for g, a in zip(grid, adj):
            g['p_holm'] = float(a)
        res[key] = dict(n=int(len(on)), n_on=int(on.sum()), p_on=float(h[on].mean()), p_off=float(h[~on].mean()),
                        diff=float(obs), p_rot=pv, n_rot=nrot,
                        grid_pos=int(sum(g['diff'] > 0 for g in grid)), grid_n=len(grid),
                        grid_min_p=float(min(g['p'] for g in grid)), grid_min_holm=float(min(adj)),
                        grid_rej_raw=int(sum(g['p'] < 0.05 for g in grid)), grid_rej_holm=int(sum(adj < 0.05)),
                        grid=grid)
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(res, f, indent=2)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'grid'} for k, v in res.items()}, indent=2))


if __name__ == '__main__':
    main()

"""
ai_discovery_case.py -- Capitolul 16, mini-caz „AI pentru descoperire stiintifica”
==================================================================================
Ipoteza testata: lansarea ETF-urilor spot pe Bitcoin (11 ian. 2024) a integrat Bitcoin cu actiunile.
  H0: corelatia Bitcoin--S&P 500 dupa 11 ian. 2024 = corelatia din 2020--2023
  * diferenta de corelatii, cu interval bootstrap pe blocuri circulare (blocuri de 20 de zile, 5000 de replicari)
  * scanare a datei de ruptura: statistica z Fisher intre 500 de zile comune inainte si 500 dupa fiecare data
    candidat; data ETF este comparata cu data aleasa de date (ruptura cea mai puternica)
Datele: data/market (Bitcoin, S&P 500), join pe PRETURI in zilele comune, apoi randamente log.
Iesire: ai_discovery_case.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import joint_returns, END  # noqa: E402

ETF_START = '2024-01-11'
PRE = ('2020-01-01', '2023-12-31')
BLOCK, B, WIN = 20, 5000, 500


def cbb_corr(x, rng):
    """Corelatia pe un esantion bootstrap cu blocuri circulare."""
    n = len(x)
    k = int(np.ceil(n / BLOCK))
    idx = (rng.integers(0, n, k)[:, None] + np.arange(BLOCK)[None, :]).ravel()[:n] % n
    y = x[idx]
    return np.corrcoef(y[:, 0], y[:, 1])[0, 1]


def main():
    r = joint_returns(['BTC', 'SPX'], '2016-01-01')
    pre = r.loc[PRE[0]:PRE[1]].values
    post = r.loc[ETF_START:END].values
    rho_pre = np.corrcoef(pre.T)[0, 1]
    rho_post = np.corrcoef(post.T)[0, 1]
    rng = np.random.default_rng(16)
    diff = np.array([cbb_corr(post, rng) - cbb_corr(pre, rng) for _ in range(B)])
    lo, hi = np.percentile(diff, [2.5, 97.5])

    # scanare locala a datei de ruptura
    z = {}
    a = r.values
    for i in range(WIN, len(r) - WIN + 1):
        b0, b1 = a[i - WIN:i], a[i:i + WIN]
        r0, r1 = np.corrcoef(b0.T)[0, 1], np.corrcoef(b1.T)[0, 1]
        z[r.index[i]] = (np.arctanh(r1) - np.arctanh(r0)) / np.sqrt(2 / (WIN - 3))
    z = pd.Series(z)
    i_etf = z.index.searchsorted(pd.Timestamp(ETF_START))
    z_etf = float(z.iloc[i_etf]) if i_etf < len(z) else None
    rank = float((z.abs() >= abs(z_etf)).mean()) if z_etf is not None else None
    res = dict(rho_pre=rho_pre, n_pre=len(pre), rho_post=rho_post, n_post=len(post), diff=rho_post - rho_pre,
               ci_lo=lo, ci_hi=hi, p_boot=float(2 * min((diff <= 0).mean(), (diff >= 0).mean())),
               block=BLOCK, B=B, win=WIN, z_max=float(z.abs().max()), z_max_date=str(z.abs().idxmax().date()),
               z_max_signed=float(z.loc[z.abs().idxmax()]), z_etf=z_etf,
               z_etf_date=str(z.index[i_etf].date()) if z_etf is not None else None,
               share_larger=rank, scan_start=str(z.index[0].date()), scan_end=str(z.index[-1].date()))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()

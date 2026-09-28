"""
ai_discovery_case.py -- Capitolul 15, secțiunea "AI for Scientific Discovery": mini-studiul de caz
==================================================================================================
Scenariu: după rezultatul Qwen2.5-7B (strategia zilnică, randamentul din d+2), un asistent AI propune rafinări:
alt scor, un prag pe |scor|, altă zi de deținere. Testăm toată grila de variante (grădina drumurilor care se bifurcă):
  * scor in {LM, FinBERT, Qwen2.5-7B}; prag |scor| > b, b in {0, 0.25, 0.5}; ziua câștigului in {d+2, d+3, d+4, d+5}
  * pentru fiecare variantă: media zilnică brută și t Newey--West (ca în capitol)
  * corecții: Holm (FWER 5%), Benjamini--Hochberg (FDR 10%), pragul t > 3 (Harvey, Liu & Zhu, 2016)
Folosește scorurile salvate (ch15_news_daily.csv); nu rulează din nou modelele de limbaj.
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
import mfm_text as M  # noqa: E402

SCORES = ('lm', 'finbert', 'qwen')
BANDS = (0.0, 0.25, 0.5)
HOLD = {'r2': 2, 'rp3': 3, 'rp4': 4, 'rp5': 5}


def portfolio(P, col, days, band, ret, lag):
    q = P[P[col].abs() > band]
    pos_day = pd.DatetimeIndex(days)
    idx = pos_day.get_indexer(q.index.get_level_values('day'))
    ok = (idx >= 0) & (idx + lag < len(pos_day))
    q = q[ok]
    x = pd.Series(np.sign(q[col].values) * q[ret].values, index=pos_day[idx[ok] + lag])
    return x.groupby(level=0).mean().reindex(pos_day).fillna(0.0)


def main():
    daily = pd.read_csv(os.path.join(HERE, 'ch15_news_daily.csv'), parse_dates=['day']).set_index(['day', 'ticker'])
    syms = sorted(set(M.TICKERS.values()))
    rets = M.stock_returns(syms + ['SPY.US'], start='2009-01-01')
    rets.columns = [c.replace('.US', '') for c in rets.columns]
    rets = rets.loc[:'2023-12-31']
    P = M.daily_panel(daily, rets)
    days = rets.index[rets.index >= P.index.get_level_values('day').min()]
    rows = []
    for c in SCORES:
        for b in BANDS:
            for ret, lag in HOLD.items():
                x = portfolio(P.dropna(subset=[ret]), c, days, b, ret, lag)
                mu, t = M.nw_t(x)
                rows.append({'score': c, 'band': b, 'day': lag, 'mean_bp': 1e2 * mu, 't': t})
    R = pd.DataFrame(rows)
    base = R[(R.score == 'qwen') & (R.band == 0) & (R.day == 2)].iloc[0]
    p = 2 * (1 - stats.norm.cdf(R['t'].abs().values))
    M_ = len(p)
    order = np.argsort(p)
    holm = np.zeros(M_, bool)
    for k, i in enumerate(order):
        if p[i] <= 0.05 / (M_ - k):
            holm[i] = True
        else:
            break
    ps = p[order]
    kk = np.where(ps <= 0.10 * np.arange(1, M_ + 1) / M_)[0]
    bh = np.zeros(M_, bool)
    if len(kk):
        bh[order[:kk.max() + 1]] = True
    best = R.iloc[int(np.argmax(R['t'].abs().values))]
    out = {
        'n_variants': int(M_), 'base_mean_bp': float(base.mean_bp), 'base_t': float(base.t),
        'n_sig': int((R['t'].abs() > 1.96).sum()), 'n_sig_pos': int((R['t'] > 1.96).sum()),
        'expected_false': float(0.05 * M_),
        'n_holm': int(holm.sum()), 'n_bh': int(bh.sum()), 'n_t3': int((R['t'].abs() > 3).sum()),
        'best': {k: (float(v) if not isinstance(v, str) else v) for k, v in best.items()},
        'bonf_crit': float(stats.norm.ppf(1 - 0.025 / M_)),
        'grid': R.round(3).to_dict(orient='records'),
    }
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != 'grid'}, indent=2))
    print(R.round(2).to_string())


if __name__ == '__main__':
    main()

"""Export the inputs of the Chapter 16 interactive page (MFM/interactive/ch16_data.js).

Uses the data loaders of mfm_data.py and the functions of generate_all_charts.py and ai_discovery_case.py, so the page
starts from the same numbers as the slides. Nothing is written to charts/, ch16_results.json or the CSV tables.
"""
import glob
import hashlib
import json
import os

import numpy as np
import pandas as pd

import generate_all_charts as g
import ai_discovery_case as ai
import case_pagnotta as cp
from mfm_data import (ASSETS, CRIX_UNIVERSE, STABLE, END, price, log_returns, joint_prices, joint_returns,
                      periods_per_year, market_values, defi_tvl, read_market)

g.save_fig = lambda name: None          # never rewrite slide charts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch16_data.js')
CHARTS = os.path.join(HERE, '..', '..', 'charts')


def files_hash():
    fs = sorted(glob.glob(os.path.join(CHARTS, 'ch16_*'))) + [os.path.join(HERE, f) for f in
         ('ch16_results.json', 'ch16_stylised_facts.csv', 'ch16_asset_features.csv', 'ai_discovery_case.json', 'ch16_pagnotta.json')]
    return {f: hashlib.md5(open(f, 'rb').read()).hexdigest() for f in fs}


def r(x, d=6):
    return [None if not np.isfinite(v) else v for v in np.round(np.asarray(x, float), d).tolist()]


def sig(x, n=7):
    """Values rounded to n significant digits."""
    return [float(f'{v:.{n}g}') for v in np.asarray(x, float)]


def days(idx):
    """First date and the gaps in calendar days between consecutive observations (compact date encoding)."""
    d = np.asarray(idx.values, dtype='datetime64[D]').astype(np.int64)
    return dict(d0=str(idx[0].date()), gap=np.diff(d).astype(int).tolist())


def close(a, b, tol=1e-6):
    assert abs(a - b) <= tol * max(1, abs(b)), (a, b)


def main():
    before = files_hash()
    res = json.load(open(os.path.join(HERE, 'ch16_results.json')))
    zres = json.load(open(os.path.join(HERE, 'ai_discovery_case.json')))
    d = dict(end=END, etf_start=g.ETF_START)

    # 1. market value of the five coins: month-end stack and daily Bitcoin share
    mv = market_values()
    m = mv.resample('ME').last()
    tot = mv.sum(axis=1)
    share = 100 * mv['BTC'] / tot
    close(tot.iloc[-1], res['market_value']['total_end'])
    close(share.min(), res['market_value']['btc_share_min'])
    d['mv'] = dict(keys=CRIX_UNIVERSE, months=[f'{t:%Y-%m}' for t in m.index], mv={k: r(m[k], 3) for k in CRIX_UNIVERSE},
                   share=dict(days(share.index), v=r(share, 2)), daily_tot=r(tot, 2),
                   ref={k: res['market_value'][k] for k in ('total_end', 'total_peak', 'total_peak_date', 'btc_share_end', 'btc_share_min',
                                                            'btc_share_min_date', 'btc_share_max', 'btc_share_max_date')})

    # 2. rolling volatility: daily log returns from 2018 on each series' own calendar
    d['vol'] = {}
    for k in ['BTC', 'ETH', 'SPX', 'GOLD']:
        x = log_returns(k, '2018-01-01')
        d['vol'][k] = dict(days(x.index), r=r(x, 6), ppy=periods_per_year(x))
    d['vol_ref'] = res['rolling_vol']

    # 3. weekday: the Bitcoin returns of block 2 (100 x log returns from 2018)
    d['weekday_ref'] = res['weekday']

    # 4. rolling correlation and 14. z scan: Bitcoin returns on the common days with each series, from 2016
    d['corr'] = {}
    for k in ['SPX', 'QQQ', 'GOLD']:
        x = joint_returns(['BTC', k], '2016-01-01')
        d['corr'][k] = dict(days(x.index), btc=r(x['BTC'], 6), other=r(x[k], 6))
    d['corr_ref'] = res['rolling_corr']
    d['zscan_ref'] = zres

    # 5. crypto indices: the four lines of the slide (chapter's crix_index)
    px = pd.concat([price(a) for a in CRIX_UNIVERSE], axis=1).reindex(mv.index)
    lv = {'tot': g.crix_index(None, 'cap', mv, px)[0], 'k2': g.crix_index(2, 'cap', mv, px)[0],
          'k1': g.crix_index(1, 'cap', mv, px)[0], 'ew': g.crix_index(None, 'equal', mv, px)[0]}
    close(lv['tot'].iloc[-1], res['crix']['tot_end'])
    close(lv['ew'].iloc[-1], res['crix']['ew_end'])
    assert all(v.index.equals(lv['tot'].index) for v in lv.values())
    d['crix'] = dict(days(lv['tot'].index), lev={k: sig(v, 7) for k, v in lv.items()},
                     ref={k: res['crix'][k] for k in ('tot_cagr', 'ew_cagr', 'tot_vol', 'ew_vol', 'years', 'ew_year', 'tot_year', 'k1_year')})

    # 6. peg deviations (bp), close and daily low, 2021 - END
    d['peg'] = {}
    for k in STABLE:
        x = read_market(ASSETS[k][0]).loc['2021-01-01':END]
        d['peg'][k] = dict(days(x.index), close=r(1e4 * (x['close'] - 1), 2), low=r(1e4 * (x['low'] - 1), 2))
    d['peg_ref'] = {k: {c: res['peg'][k][c] for c in ('N', 'sd', 'gt50', 'gt100', 'low_min', 'low_min_date', 'phi', 'half_life')} for k in STABLE}

    # 7. March 2023
    d['svb'] = {}
    for k in STABLE:
        x = read_market(ASSETS[k][0]).loc['2023-03-05':'2023-03-20']
        d['svb'][k] = dict(dates=[f'{t:%Y-%m-%d}' for t in x.index], close=r(x['close'], 6), low=r(x['low'], 6), high=r(x['high'], 6))
    d['svb_ref'] = res['depeg_2023']

    # 8. DeFi TVL and Ether, month ends from 2020
    tvl = defi_tvl().loc['2020-01-01':]
    eth = price('ETH', '2020-01-01')
    mm = pd.concat([tvl.resample('ME').last(), eth.resample('ME').last()], axis=1).dropna()
    mm.columns = ['TVL', 'ETH']
    if (pd.Timestamp(END) + pd.Timedelta(days=1)).day != 1:     # complete months only, as in the slides
        mm = mm.iloc[:-1]
    dl = np.log(mm).diff().dropna()
    reg = g.hac_ols(dl['TVL'], dl['ETH'], lags=3)
    close(reg.params['ETH'], res['defi']['beta'])
    d['tvl'] = dict(months=[f'{t:%Y-%m}' for t in mm.index], tvl=r(mm['TVL'], 4), eth=r(mm['ETH'], 3),
                    ref={k: res['defi'][k] for k in ('peak', 'peak_date', 'last', 'start', 'beta', 'se', 'r2', 'n')})

    # 9. liquidity provider in an ETH pool, from 2024-01-01
    p = price('ETH', '2024-01-01')
    d['lp'] = dict(days(p.index), p=r(p, 4), ref={k: res['lp'][k] for k in ('hodl', 'lp', 'reb', 'mmrz', 'lvr_level', 'il', 'sigma', 'lvr_theory', 'lvr_real', 'years')})

    # 10-11. spot ETFs: prices on common days, weekly (Friday) returns
    d['etf'] = {}
    for e, c in [('IBIT', 'BTC'), ('ETHA', 'ETH')]:
        jp = joint_prices([e, c])
        w = joint_returns([e, c], freq='W')
        d['etf'][e] = dict(coin=c, dates=[f'{t:%Y-%m-%d}' for t in jp.index], etf_p=r(jp[e], 4), coin_p=r(jp[c], 4),
                           w_etf=r(w[e], 6), w_coin=r(w[c], 6), w_dates=[f'{t:%Y-%m-%d}' for t in w.index],
                           ref={k: res['etf'][e.lower()][k] for k in ('beta_d', 'r2_d', 'beta_w', 'r2_w', 'te_d', 'te_w', 'drift', 'n_d', 'n_w')})

    # 12. asset-class map: the feature table of the chapter (standardised and projected in the browser)
    f = g.feature_table()
    X = f[g.FEATURES].values
    Z = (X - X.mean(0)) / X.std(0)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    if np.corrcoef((Z @ Vt[:2].T)[:, 0], f['ann_vol'])[0, 1] < 0:
        Vt[0] *= -1
    close(100 * S[0] ** 2 / (S ** 2).sum(), res['alt']['ev1'])
    d['alt'] = dict(features=g.FEATURES, symbol=f['symbol'].tolist(), label=f['label'].tolist(), cls=f['cls'].tolist(),
                    window=f['window'].tolist(), X=[r(row, 8) for row in X], V=[r(v, 8) for v in Vt[:2]],
                    ref={w: res['alt'][w] for w in ('W1', 'W2')}, ev=[res['alt']['ev1'], res['alt']['ev2']])

    # 13. Liu, Tsyvinski & Wu (2022), Table 1: weekly simple returns on the paper's calendar
    d['ltw'] = {}
    for k in g.LTW_T1:
        x = g.ltw_weekly(k).loc[g.LTW_START[k]:]
        d['ltw'][k] = dict(dates=[f'{t:%Y-%m-%d}' for t in x.index], r=r(x, 6), paper=list(g.LTW_T1[k]))
    d['ltw_ref'] = {k: {s: res['ltw'][k][s] for s in ('ins', 'oos')} for k in g.LTW_T1}
    d['ltw_end'] = g.LTW_END

    # 15. Pagnotta (2022): monthly means of price, hashrate, USD block reward; hashrate around the four halvings
    pres = json.load(open(os.path.join(HERE, 'ch16_pagnotta.json')))
    dd = cp.daily()
    lv, mlog = cp.levels(dd)
    for w in ('paper', 'oos'):
        close(lv[w]['b'], pres['levels'][w]['b'])
    ev, paths = cp.event(dd)
    mm = np.exp(mlog.loc[cp.PAPER[0]:])
    d['hr'] = dict(months=[f'{t:%Y-%m}' for t in mm.index], P=sig(mm['P'], 7), H=sig(mm['H'], 7), B=sig(mm['B'], 7),
                   paper=list(cp.PAPER), oos=list(cp.OOS), k=paths[cp.HALVINGS[0]]['k'].tolist(), halvings=cp.HALVINGS,
                   H_ev={h: r(paths[h]['H'], 3) for h in cp.HALVINGS}, B_ev={h: r(paths[h]['B'], 3) for h in cp.HALVINGS},
                   ref=dict(levels=pres['levels'], halvings=pres['halvings'], h_last=pres['h_last']))

    with open(OUT, 'w') as fh:
        fh.write('// Inputs of the Chapter 16 interactive page, exported by Quantlets/Ch_16/export_interactive.py.\n')
        fh.write('window.CH16_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    assert files_hash() == before, 'chart or results files changed'
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

"""Export the inputs of the Chapter 10 interactive page (MFM/interactive/ch10_data.js).

Uses the functions of generate_all_charts.py, micro.py, mfm_data.py and case_study_race.py, so the page starts from
the same numbers as the slides. save_fig is replaced by a no-op: no chart or results file of the chapter is rewritten.
Market data come from the local files in data/market; BVB traded values are converted to USD with the chapter's own
loader of the BNR USD/RON reference rate (mfm_data.read_reference_rate, official BNR archive), as in the lecture.
The cross-section of spreads and the three panels of the mini-case are read from ch10_results.json and sem10_results.json.
"""
import json
import os

import numpy as np
import pandas as pd

import mfm_data

import generate_all_charts as g          # noqa: E402
import case_study_race as cr             # noqa: E402

g.read_market = mfm_data.read_market
g.save_fig = lambda name: g.plt.close()
cr.save_fig = g.save_fig

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch10_data.js')


def r(x, d=6):
    a = np.round(np.asarray(x, float), d)
    return [None if not np.isfinite(v) else (int(v) if d == 0 else float(v)) for v in a]


def days(idx):
    return [f'{t:%Y-%m-%d}' for t in idx]


def main():
    res = json.load(open(os.path.join(HERE, 'ch10_results.json')))
    sem = json.load(open(os.path.join(HERE, 'sem10_results.json')))
    race = json.load(open(os.path.join(HERE, 'case_study_race.json')))
    keys = list(g.ASSETS)
    d = dict(assets=keys, labels={k: g.LABELS[k] for k in keys}, group={k: g.ASSETS[k][2] for k in keys})

    # 1. simulated order book (zero-intelligence): the 199 snapshots, mid and spread at each snapshot
    zb = g.zi_book()
    path = zb['path'].set_index('event')
    ev = [e for e in range(g.ZI_PARAMS['n_events']) if e > g.ZI_PARAMS['n_events'] // 3 and e % 1000 == 0]
    assert len(ev) == len(zb['snaps'])
    d['lob'] = dict(rel0=[float(s['rel'].iloc[0]) for s in zb['snaps']], bid=[s['bid'].astype(int).tolist() for s in zb['snaps']],
                    ask=[s['ask'].astype(int).tolist() for s in zb['snaps']], event=ev,
                    mid=r(path.loc[ev, 'mid'].values, 1), spread=r(path.loc[ev, 'spread'].values, 0),
                    sizes=zb['sizes'], res=res['lob'], impact=res['impact'])

    # 2. Roll model: the standard Normal draws and the trade signs of roll_sim (seed 42)
    m, q, p, out = g.roll_sim()
    rng = np.random.default_rng(g.SEED)
    z = rng.normal(0, 1, 5000)
    qq = np.where(rng.random(5000) < 0.5, 1, -1)
    assert np.allclose(100 + np.cumsum(0.02 * z), m) and (qq == q).all()
    d['roll'] = dict(z=r(z, 5), q=''.join('1' if v > 0 else '0' for v in q), res=res['roll'])

    # 3. spread estimators: SPY 5-minute estimates by day (ch10_spy_intraday_spreads.csv) and SPY daily OHLC
    E = pd.read_csv(os.path.join(HERE, 'ch10_spy_intraday_spreads.csv'), index_col=0, parse_dates=True)
    o = g.ohlc('SPY', '2020-10-01')
    d['freq'] = dict(days=days(E.index), cov=r(E['cov'] * 1e8, 4), cs=r(E['cs'] * 1e4, 4), ar2=r(E['ar2'] * 1e8, 4),
                     price=r(E['price'], 2), edge=r(E['edge'] * 1e4, 4),
                     d_days=days(o.index), o=r(o['open'], 4), h=r(o['high'], 4), l=r(o['low'], 4), c=r(o['close'], 4),
                     start2=g.START2, res=res['freq'], daily=res['spreads']['SPY'])

    # 4. cross-section of the 25 assets (two years of daily bars)
    tab = sem['B3']['table']
    d['cross'] = {k: dict(roll=res['spreads'][k]['roll'], cs=res['spreads'][k]['cs'], ar=res['spreads'][k]['ar'],
                          edge=res['spreads'][k]['edge'], vol=tab[k]['vol'], dv=tab[k]['dv'], illiq=res['amihud'][k]['illiq'])
                  for k in keys}
    d['b3'] = {k: v for k, v in sem['B3'].items() if k != 'table'}

    # 5. Amihud: monthly sums and counts of the daily ratios in the two-year window (the window starts on the 19th,
    #    so the first and the last month are partial and the totals reproduce the slide exactly)
    am = {}
    for k in keys:
        x = pd.concat([g.returns(k, g.START2).rename('r'), g.dollar_volume(k, g.START2).rename('dv')], axis=1, join='inner').dropna()
        x = x[x['dv'] > 0]
        ratio = 1e4 * x['r'].abs() / (x['dv'] / 1e6)
        mo = ratio.groupby(ratio.index.to_period('M'))
        am[k] = dict(s=r(mo.sum().values, 6), n=mo.size().astype(int).tolist(), m=[str(p) for p in mo.size().index])
        am[k]['check'] = float(ratio.mean())
    months = sorted({mm for v in am.values() for mm in v['m']})
    d['amihud'] = dict(months=months, s={k: [v['s'][v['m'].index(mm)] if mm in v['m'] else 0 for mm in months] for k, v in am.items()},
                       n={k: [v['n'][v['m'].index(mm)] if mm in v['m'] else 0 for mm in months] for k, v in am.items()},
                       res={k: res['amihud'][k]['illiq'] for k in keys})

    # 6. monthly Amihud ratio of each asset (group medians, without SPY and the BET ETF)
    mt = {}
    for grp in ('US', 'BVB', 'Crypto'):
        ks = [k for k in g.GROUPS[grp] if k not in ('SPY', 'TVBETETF')]
        mt[grp] = g.monthly_illiq(ks).loc['2017-01':'2026-08']
    idx = mt['US'].index
    d['amihud_time'] = dict(months=[f'{t:%Y-%m}' for t in idx], series={grp: {k: r(v[k].reindex(idx).values, 6) for k in v} for grp, v in mt.items()},
                            res=res['amihud_time'])

    # 7. SPY intraday: profile by time of day, all days and by year
    spy = mfm_data.intraday_spy()
    tods = {'all': g.spy_tod(spy)}
    for y in sorted(spy['date'].dt.year.unique()):
        tods[str(y)] = g.spy_tod(spy[spy['date'].dt.year == y])
    d['tod'] = dict(labels=list(tods['all'].index), periods=list(tods),
                    ndays={k: int((spy['date'] if k == 'all' else spy.loc[spy['date'].dt.year == int(k), 'date']).nunique()) for k in tods},
                    share={k: r(v['share'], 4) for k, v in tods.items()}, absr={k: r(v['absr'], 3) for k, v in tods.items()},
                    res=res['tod'])

    # 8. SPY intraday illiquidity and the VIX, by day
    ill = g.spy_illiq_daily(spy)
    vix = mfm_data.read_market('VIX.INDX')['close'].rename('vix')
    j = pd.concat([ill, vix], axis=1, join='inner').dropna()
    d['vix'] = dict(days=days(j.index), ill=r(j['illiq'], 4), vix=r(j['vix'], 2), res=res['illiq_vix'])

    # 9. Almgren-Chriss example
    d['ac'] = dict(par=g.AC, res=res['ac'])

    # 10. flash crash: SPY daily bars, 15 April - 28 May 2010
    sp = mfm_data.read_market('SPY.US')
    prev = sp['close'].shift(1)
    fl = sp.loc['2010-04-15':'2010-05-28']
    d['flash'] = dict(days=days(fl.index), o=r(fl['open'], 3), h=r(fl['high'], 3), l=r(fl['low'], 3), c=r(fl['close'], 3),
                      v=r(fl['volume'] / 1e6, 2), prev=r(prev.loc[fl.index], 3), res=res['flash'])

    # 11. latency arbitrage tax: daily annualised realised volatility of SPY, 2021-2025
    rd = cr.race_daily(spy)
    d['race'] = dict(days=days(rd.index), sigma=r(rd['sigma'], 3), V=r(rd['V'] / 1e9, 3), coef=cr.ABO, res=race['tax'],
                     prize={y: {k: v[k] for k in ('col2', 'col6', 'lo', 'hi', 'sigma_mean')} for y, v in race['prize'].items()})

    # 12. AI mini-case: leave-one-market-out values of ai_discovery_case.json
    ai = json.load(open(os.path.join(HERE, 'ai_discovery_case.json')))
    d['ai'] = {k: ai[k] for k in ('rho_cs_vol', 'rho_cs_illiq', 'diff', 'diff_lo', 'diff_hi', 'diff_s_lo', 'diff_s_hi',
                                  'partial_cs_illiq_given_vol', 'diff_lomo')}

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 10 interactive page, exported by Quantlets/Ch_10/export_interactive.py.\n')
        f.write('window.CH10_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
    for k in keys:                                    # the two-year means must equal the lecture values
        a, b = d['amihud']['res'][k], am[k]['check']
        assert abs(a / b - 1) < 1e-9, (k, a, b)


if __name__ == '__main__':
    main()

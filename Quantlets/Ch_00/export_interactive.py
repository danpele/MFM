"""Export the inputs of the Chapter 0 interactive page (MFM/interactive/ch0_data.js).

Uses the series and functions of generate_all_charts.py, ai_discovery_case.py and case_pflueger.py, so the page starts from the
same data and numbers as the slides. The chart functions are called with save_fig replaced by plt.close, so the
slide charts are not rewritten; their return values are exported as reference numbers ('ref').
Dates are exported as days since 1970-01-01; date arrays named t are delta-encoded (tdelta).
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import generate_all_charts as g
import ai_discovery_case as ai
import case_pflueger as pf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch0_data.js')
EPOCH = pd.Timestamp('1970-01-01')

g.save_fig = lambda name: plt.close()          # keep the slide charts untouched


def days(idx):
    return ((pd.DatetimeIndex(idx) - EPOCH).days).tolist()


def tdelta(idx):
    """Dates as the first day number followed by the gaps in days (decoded by a cumulative sum in ch0.js)."""
    t = days(idx)
    return [t[0]] + np.diff(t).tolist()


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def sig(x, n=7):
    """Round to n significant digits (prices of very different size)."""
    x = np.asarray(x, float)
    e = np.floor(np.log10(np.abs(x)))
    return [float(np.round(v, int(n - 1 - k))) for v, k in zip(x, e)]


def ser(s, n=7):
    s = s.dropna()
    return dict(t=tdelta(s.index), v=sig(s.values, n))


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (pd.Timestamp,)) or hasattr(o, 'isoformat'):
        return str(o)[:10]
    if isinstance(o, (np.floating, float)):
        return float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    return o


def main():
    d = {}

    # history of exchanges and crashes: the lanes of fig_market_history
    cap = {}
    orig = g._timeline
    g._timeline = lambda ax, rows, x0, x1, **kw: (cap.setdefault('rows', rows), orig(ax, rows, x0, x1, **kw))
    g.fig_market_history()
    g._timeline = orig
    lanes = []
    for lab, col, events in cap['rows']:
        ev = []
        for e in events:
            if len(e) == 4 and isinstance(e[1], (int, float)):     # interval (start, end, text, level)
                ev.append(dict(a=e[0], b=e[1], text=e[2], lv=e[3], dx=0))
            else:                                                     # point (year, text, level[, dx])
                ev.append(dict(a=e[0], b=e[0], text=e[1], lv=e[2], dx=e[3] if len(e) == 4 else 0))
        lanes.append(dict(label=lab, color=col, events=ev))
    d['history'] = dict(lanes=lanes)

    # risk and return, 2015-2026 (same series and annualisation as fig_risk_return)
    start = '2015-01-02'
    names = g.CROSS + ['Ethereum', 'EUR/USD', 'EUR/RON']
    cols = g.CROSS_COL + [g.Purple, g.Crimson, g.IDAred]
    panel = g.cross_panel()
    rr = {n: ser((g.eurron if n == 'EUR/RON' else panel[n]).loc[start:]) for n in names}
    res = g.fig_risk_return(start)
    d['risk_return'] = dict(names=names, colors=cols, series=rr,
                            ref={n: dict(cagr=float(res.loc[n, 'cagr']), vol=float(res.loc[n, 'vol'])) for n in names})

    # S&P 500 drawdowns
    s = g.px['S&P 500'].dropna()
    d['drawdowns'] = dict(sp=ser(s), episodes=g.EPISODES, ref=jsonable(g.fig_sp500_drawdowns()))

    # VIX
    v = g.px['VIX'].dropna()
    peaks, share = g.fig_vix_regimes()
    d['vix'] = dict(vix=ser(v, 5), ref=dict(peaks=jsonable(peaks), share=jsonable(share)))

    # rolling correlations: the two aligned return panels of fig_rolling_correlations
    eq = np.log(g.px['S&P 500'].dropna()).diff()
    bd = np.log(g.px['US Treasuries 20y+ (TLT)'].dropna()).diff()
    both = pd.concat([eq, bd], axis=1).dropna()
    pp = pd.concat([g.px['S&P 500'], g.px['Bitcoin']], axis=1).dropna()
    trio = np.log(pp).diff().dropna()
    d['corr'] = dict(sb=dict(t=tdelta(both.index), x=r(both.iloc[:, 0], 7), y=r(both.iloc[:, 1], 7)),
                     be=dict(t=tdelta(trio.index), x=r(trio.iloc[:, 0], 7), y=r(trio.iloc[:, 1], 7)),
                     ref=jsonable(g.fig_rolling_correlations()))

    # BET 1997-2026
    bet = g.load('BET', start='1997-01-01').dropna()
    events = [('1999-04-21', 'Apr 1999 low'), ('2007-07-24', 'Jul 2007 peak'), ('2009-02-25', 'Feb 2009 trough'),
              ('2018-12-18', 'Dec 2018 bank-tax announcement'), ('2020-03-16', 'Mar 2020 COVID-19'),
              ('2023-07-12', 'Jul 2023 Hidroelectrica IPO')]
    ev = [dict(t=days([bet.index[bet.index.searchsorted(pd.Timestamp(a))]])[0], text=b) for a, b in events]
    d['bet'] = dict(bet=ser(bet), events=ev, ref=jsonable(g.fig_bvb_history()))

    # Tether (USDT)
    u = g.load('Tether (USDT)', start='2019-01-01').dropna()
    d['usdt'] = dict(u=dict(t=tdelta(u.index), v=r(u.values, 6)), ref=jsonable(g.fig_usdt_peg()))

    # SPY and RSP
    p = g.px[['SPY', 'RSP']].dropna()
    d['conc'] = dict(t=tdelta(p.index), spy=sig(p['SPY'].values), rsp=sig(p['RSP'].values), ref=jsonable(g.fig_concentration()))

    # Haddad, Huebner and Loualiche (2025): eq. (5)
    d['hhl'] = dict(params=g.HHL, ref=jsonable(g.fig_hhl_elasticity()))

    # concentration premium: d_t = r_SPY - r_RSP (ai_discovery_case.py)
    d['ai'] = dict(t=tdelta(ai.d.index), d=r(ai.d.values, 9), ref=json.load(open(os.path.join(HERE, 'ai_discovery_case.json'))))

    # Pflueger (2025): bond-stock betas (case_pflueger.py); daily panel from June 2017 (windows ending in 2018)
    res, q, _, dd, _, _ = pf.fig_pflueger_betas(save=False)
    qt = q.index.to_timestamp(how='end').normalize()
    dd = dd.loc['2017-06-01':]
    d['pflueger'] = dict(q=dict(t=tdelta(qt), lab=[str(x) for x in q.index], eq=r(q['eq'], 7), bond=r(q['bond'], 7)),
                         d=dict(t=tdelta(dd.index), eq=r(dd['eq'], 7), nom=r(dd['nom'], 7), tips=r(dd['tips'], 7)),
                         ref=res)

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 0 interactive page, exported by Quantlets/Ch_00/export_interactive.py.\n')
        f.write('window.CH0_DATA = ' + json.dumps(jsonable(d), separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
    print(json.dumps(jsonable({k: v.get('ref') for k, v in d.items() if isinstance(v, dict) and 'ref' in v}), indent=0)[:4000])


if __name__ == '__main__':
    main()

"""Export the inputs of the Chapter 18 interactive page (MFM/interactive/ch18_data.js).

Calls the functions of generate_all_charts.py and systemic.py, so the page starts from the same numbers as the
slides. The chart files are not rewritten: save_fig is replaced by a function that only closes the figure, and the
Financial Risk Meter is read from the chapter's own cache (ch18_frm.csv), as generate_all_charts.py does with
MFM_FRM_CACHE set.
"""
import json
import os

os.environ['MFM_FRM_CACHE'] = '1'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import generate_all_charts as g
from systemic import covar_static, qreg, mes, var_fit, var_bic, gfevd, rolling_total

g.save_fig = lambda name: plt.close()

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch18_data.js')


def r(x, d=4):
    a = np.round(np.asarray(x, float), d)
    return [None if np.isnan(v) else (int(v) if d == 0 else float(v)) for v in a.ravel()] if a.ndim == 1 else \
        [r(row, d) for row in a]


def ints(x, k=1000):
    """Values times k, rounded to integers (compact daily series)."""
    a = np.asarray(x, float)
    return [None if np.isnan(v) else int(round(k * v)) for v in a]


def days(idx):
    return [f'{t:%Y-%m-%d}' for t in idx]


def main():
    res = json.load(open(os.path.join(HERE, 'ch18_results.json')))
    R, ALL, US, EU, RO, NAMES = g.R, g.ALL, g.US, g.EU, g.RO, g.NAMES
    reg = {k: g.region_of(k) for k in ALL}
    d = dict(banks=ALL, names=[NAMES[k] for k in ALL], region=[reg[k] for k in ALL], dates=days(R.index),
             events=[[a, b] for a, b in g.EVENTS])

    # 1. regional bank portfolios: mean simple return (daily rebalancing) and mean log return (volatility)
    d['idx'] = {rg: dict(simple=ints((np.exp(R[m] / 100) - 1).mean(axis=1), 1e5), logm=ints(R[m].mean(axis=1)))
                for rg, m in [('US', US), ('EU', EU), ('RO', RO)]}
    d['idx_vol'] = {k: res['index_vol'][k] for k in ('SPX', 'SX5E', 'BET')}

    # 2. MES at tail levels 1%..20%, against the regional index; bootstrap interval at 5%
    mt = g.mes_table()
    alphas = [a / 100 for a in range(1, 21)]
    d['mes'] = dict(alphas=alphas,
                    bank={k: r([mes(R[k].values, R[g.REGION_INDEX[reg[k]]].values, a) for a in alphas]) for k in ALL},
                    market={rg: r([-R[ix].values[R[ix].values <= np.quantile(R[ix].values, a)].mean() for a in alphas])
                            for rg, ix in g.REGION_INDEX.items()},
                    lo=r(mt.loc[ALL, 'lo']), hi=r(mt.loc[ALL, 'hi']))

    # 3. SRISK: shortcut LRMES of every bank, banks drawn on the slide
    order = mt['lrmes'].sort_values()
    d['srisk'] = dict(lrmes=r(mt.loc[ALL, 'lrmes'], 6), mes2=r(mt.loc[ALL, 'mes2']),
                      pick=[order.index[-1], order.index[len(order) // 2], order.index[0]])

    # 4. CoVaR at tail levels 1%..10% (contribution and exposure), for the 11 US and European banks
    ca = [a / 100 for a in range(1, 11)]
    CB = US + EU
    cv = {k: [] for k in CB}
    for k in CB:
        xs = g.system_ex(k, US if k in US else EU)
        for a in ca:
            c = covar_static(xs, R[k], a)
            e = covar_static(R[k], xs, a)
            cv[k].append([c['a'], c['b'], c['var_i'], c['covar'], c['covar_med'], c['dcovar'], c['var_sys'], e['dcovar']])
    d['covar'] = dict(alphas=ca, banks=CB, fields=['a', 'b', 'var_i', 'covar', 'covar_med', 'dcovar', 'var_sys', 'exp_dcovar'],
                      v={k: r(cv[k], 5) for k in CB},
                      ci={str(a): {k: [res[key][k]['lo'], res[key][k]['hi']] for k in CB} for a, key in ((0.01, 'covar1'), (0.05, 'covar5'))})
    xs, xi = g.system_ex('JPM', US), R['JPM']
    d['qr'] = dict(x=ints(xi), y=ints(xs), med=r(qreg(xs, xi, 0.5), 6))

    # 5. connectedness: full-sample VAR on the log range volatility, decomposition for H = 1..30
    V = g.V
    p = var_bic(V.values, 5)
    A, S = var_fit(V.values, p)
    d['spill'] = dict(p=p, H=list(range(1, 31)), theta=[r(100 * gfevd(A, S, H), 3) for H in range(1, 31)],
                      total_ret=res['spill']['total_ret'], start=f'{V.index[0]:%Y-%m-%d}', end=f'{V.index[-1]:%Y-%m-%d}')

    # 6. rolling connectedness (systemic.rolling_total) for three windows and three horizons
    roll = {}
    for w in (100, 250, 500):
        for H in (5, 10, 20):
            tot, net = rolling_total(V, window=w, step=5, p=2, H=H)
            roll[f'{w}_{H}'] = dict(total=r(tot.values, 2), **{rg: r(net[[k for k in ALL if reg[k] == rg]].sum(axis=1).values, 2)
                                                             for rg in ('US', 'EU', 'RO')})
            roll.setdefault('dates_' + str(w), days(tot.index))
    d['roll'] = roll

    # 7. Financial Risk Meter (chapter cache) and the VIX
    f, lam_fix = g.frm_series()
    vix = g.index_close('VIX').reindex(f.index)
    d['frm'] = dict(dates=days(f.index), frm=r(1e4 * f['frm'].values, 4), dens=r(f['density'].values, 4), vix=r(vix.values, 2),
                    lam_fix=float(lam_fix))

    # 8. historical stress scenarios: daily returns inside each episode, as in stress_historical
    Rl = g.joint_returns(g.INTL, start='2007-01-01')
    eps = []
    for name, a, b in g.EPISODES:
        keys = g.INTL + (RO if pd.Timestamp(a) >= pd.Timestamp('2010-01-01') else [])
        X = (Rl.loc[a:b] if keys == g.INTL else R.loc[a:b, keys]).reindex(columns=ALL)
        eps.append(dict(name=name, dates=days(X.index), X=[ints(X[k]) if k in keys else None for k in ALL]))
    d['stress'] = eps

    # 9. case study: spillover index by quantile, values reported by Ando, Greenwood-Nimmo and Shin (2022)
    d['ags'] = dict(fig4={str(k): v for k, v in g.AGS_FIG4.items()}, mean=g.AGS_MEAN, centre=list(g.AGS_CENTRE))

    with open(OUT, 'w') as fo:
        fo.write('// Inputs of the Chapter 18 interactive page, exported by Quantlets/Ch_18/export_interactive.py.\n')
        fo.write('window.CH18_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

"""Export the inputs of the Chapter 5 interactive page (MFM/interactive/ch5_data.js).

Uses the functions of generate_all_charts.py and garch_tools.py, so the page starts from the same numbers as the
slides. The chart functions are run with save_fig replaced by a recorder: the page receives the plotted series
themselves and no chart or results file of the chapter is rewritten. The EUR/RON reference rate is not loaded
(it comes from the BNR archive online); its GARCH(1,1)-t row is read from ch5_garch_table.csv.
"""
import json
import os

import numpy as np
import pandas as pd

import mfm_data

mfm_data.MARKETS.pop('eurron', None)          # no download: EUR/RON enters the page only through ch5_garch_table.csv
import generate_all_charts as g               # noqa: E402
from garch_tools import fit_garch, news_impact  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch5_data.js')

CAPTURED = {}


def capture(name):
    """Replacement of save_fig: keep the plotted lines of the current figure, write nothing."""
    import matplotlib.pyplot as plt
    CAPTURED[name] = [[(ln.get_label(), np.asarray(ln.get_xdata(), float), np.asarray(ln.get_ydata(), float))
                       for ln in ax.get_lines()] for ax in plt.gcf().axes]
    plt.close()


g.save_fig = capture


def r(x, d=6):
    a = np.round(np.asarray(x, float), d)
    return [None if not np.isfinite(v) else float(v) for v in a]


def days(idx):
    return [f'{t:%Y-%m-%d}' for t in idx]


def calendar(idx):
    """Compact daily calendar: first date and the gaps in calendar days (the page rebuilds the dates)."""
    return dict(d0=f'{idx[0]:%Y-%m-%d}', gaps=np.diff(idx.values.astype('datetime64[D]').astype(np.int64)).tolist())


def main():
    num = json.load(open(os.path.join(HERE, 'ch5_numbers.json')))
    inf = json.load(open(os.path.join(HERE, 'ch5_inference.json')))
    gt = pd.read_csv(os.path.join(HERE, 'ch5_garch_table.csv'), index_col='market')
    grid = pd.read_csv(os.path.join(HERE, 'ch5_model_grid.csv'))
    qsd = pd.read_csv(os.path.join(HERE, 'ch5_case_qsd.csv'), index_col='ticker').sort_index()
    rets, PPY, LAB = g.rets, g.PPY, mfm_data.LABELS
    d = dict(labels={k: LAB[k] for k in list(rets) + ['eurron']}, ppy={k: float(v) for k, v in PPY.items()},
             col=g.COL)

    # daily returns (%) of the five series read from data/market
    d['ret'] = {k: dict(calendar(v.index), r=r(v.values, 4)) for k, v in rets.items()}

    # GARCH(1,1)-t on each series (the fits behind ch5_garch_table.csv)
    fits = {k: fit_garch(rets[k], 'GARCH', 't') for k in rets}
    d['garch_t'] = {}
    for k, f in fits.items():
        p = f.params
        assert abs(p['alpha[1]'] - gt.loc[k, 'alpha']) < 1e-6 and abs(p['beta[1]'] - gt.loc[k, 'beta']) < 1e-6, k
        s2 = f.sigma.values ** 2
        eps = f.eps.values
        nxt = p['omega'] + p['alpha[1]'] * eps ** 2 + p['beta[1]'] * s2          # sigma^2_{t+1}, known at the close of t
        ends = pd.Series(np.arange(len(s2)), index=f.sigma.index).groupby(f.sigma.index.to_period('M')).last().values
        d['garch_t'][k] = dict(mu=float(p['mu']), omega=float(p['omega']), alpha=float(p['alpha[1]']), beta=float(p['beta[1]']),
                               nu=float(p['nu']), backcast=float(f.res.model._backcast) / f.c ** 2,
                               origin_dates=days(f.sigma.index[ends]), next_var=r(nxt[ends], 6))
    # the persistence chart includes EUR/RON
    d['persistence'] = {k: dict(p=float(gt.loc[k, 'persistence']), hl=float(gt.loc[k, 'half_life']))
                        for k in ['sp500', 'bet', 'btc', 'eurron', 'gold', 'bettr']}
    d['term'] = num['term']

    # S&P 500: filtered GARCH volatility and the VIX
    vol = fits['sp500'].sigma * np.sqrt(PPY['sp500'])
    vix = g.load_vix().reindex(vol.index)
    d['vix'] = dict(vix=r(vix.values, 2), num=num['vix'])

    # simulation: the plotted paths (same seed as the slide)
    g.fig_simulation()
    (iid,), (x, up, _lo) = CAPTURED['ch5_simulation']
    sd = up[2] / 2                                             # the band is 2 sigma_t
    d['sim'] = dict(omega=0.02, alpha=0.10, beta=0.88, iid=r(iid[2], 6), z=r(x[2] / sd, 8), x=r(x[2], 6), num=num['sim'])

    # news impact curves: S&P 500, t innovations
    nic = {}
    for vol_ in ('GARCH', 'GJR', 'EGARCH'):
        f = fit_garch(rets['sp500'], vol_, 't')
        p = f.params
        nic[vol_] = {k: float(p.get(k, 0.0)) for k in ('omega', 'alpha[1]', 'gamma[1]', 'beta[1]')}
        nic[vol_]['m3'] = float(news_impact(f, np.array([-3.0]))[0])
    d['nic'] = dict(models=nic, s2bar=float(rets['sp500'].var()), num=num['nic'])

    # innovations: standardised residuals of GARCH(1,1) with Normal innovations
    fn = fit_garch(rets['sp500'], 'GARCH', 'normal')
    z = fn.z.dropna()
    d['innov'] = dict(z=r(z.values, 5), nu_t=float(fits['sp500'].params['nu']), num=num['innov'])

    # half-life and long-run volatility near p = 1 (delta method, ch5_inference.json)
    d['delta'] = dict(inf['delta'], omega=float(gt.loc['sp500', 'omega']))

    # out-of-sample one-day forecasts, 2016-2026
    f1, _ = g.oos_forecasts('sp500', 2016, 22)
    sp = rets['sp500']
    i0 = sp.index.get_loc(f1.index[0])
    assert (sp.index[i0:i0 + len(f1)] == f1.index).all()
    fe = pd.read_csv(os.path.join(HERE, 'ch5_forecast_eval.csv'), index_col='model')
    d['oos'] = dict(i0=int(i0), n=len(f1), models=list(f1.columns), h={m: r(f1[m].values, 5) for m in f1.columns},
                    table={m: {c: float(fe.loc[m, c]) if pd.notna(fe.loc[m, c]) else None for c in ('qlike', 'mse', 'dm_diff', 'dm_t')}
                           for m in fe.index})

    # long memory: the plotted ACFs of |r_t|
    g.fig_long_memory({('sp500', 'GARCH', 't'): fits['sp500']})
    (emp, ga, fa, _zero), = CAPTURED['ch5_long_memory']
    d['longmem'] = dict(emp=r(emp[2], 6), garch=r(ga[2], 6), figarch=r(fa[2], 6), num=num['long_memory'],
                        pers=float(gt.loc['sp500', 'persistence']))

    # quasi score-driven case study: 11 stocks
    d['qsd'] = dict(tickers=list(qsd.index), names=list(qsd['name']),
                    **{c: r(qsd[c].values, 6) for c in ('xi', 'zeta', 'xi_beta', 'p_xi_zeta', 'lr_xi_zeta', 'p_zeta0', 'alpha', 'beta')})

    # BIC table, for the readout of the innovations block
    sp_grid = grid[grid.market == 'sp500']
    d['dbic'] = {f'{a}|{b}': float(v) for a, b, v in zip(sp_grid.vol, sp_grid.dist, sp_grid.dbic)}

    with open(OUT, 'w') as fh:
        fh.write('// Inputs of the Chapter 5 interactive page, exported by Quantlets/Ch_05/export_interactive.py.\n')
        fh.write('window.CH5_DATA = ' + json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null') + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

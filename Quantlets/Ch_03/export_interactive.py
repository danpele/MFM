"""Export the inputs of the Chapter 3 interactive page (MFM/interactive/ch3_data.js).

Uses the functions of generate_all_charts.py (and, for the two seminar figures shown in the lecture,
seminar3.py and seminar3_explainers.py), so the page starts from the same numbers as the slides.
"""
import json
import os
import sys

import numpy as np

import generate_all_charts as g
from mfm_data import prices, log_returns, factors, SECTORS, SECTORS_ALL, FACTOR_ETFS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch3_data.js')


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def ym(idx):
    return [f'{t:%Y-%m}' for t in idx]


def ymd(idx):
    return [f'{t:%Y-%m-%d}' for t in idx]


def export_tf():
    """Factor-momentum case study (factor_momentum_case.py): seven factors and MOM, July 1963 - July 2026, % a month."""
    import factor_momentum_case as fmc
    F = fmc.load()
    cols = fmc.FACS + ['MOM']
    return dict(dates=ym(F.index), names=fmc.FACS, f={c: r(F[c].values * 100, 4) for c in cols},
                res=json.load(open(os.path.join(HERE, 'ch3_factor_momentum.json'))))


def only(keys):
    """Update only the given keys of the existing ch3_data.js (no other export is re-run)."""
    txt = open(OUT, encoding='utf-8').read()
    head, body = txt.split('window.CH3_DATA = ', 1)
    d = json.loads(body.rstrip().rstrip(';'))
    for k in keys:
        d[k] = {'tf': export_tf}[k]()
    with open(OUT, 'w') as f:
        f.write(head + 'window.CH3_DATA = ' + json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null') + ';\n')
    print('updated', keys, 'in', OUT, os.path.getsize(OUT) // 1024, 'KB')


def main():
    res = json.load(open(os.path.join(HERE, 'ch3_results.json')))
    d = dict(sectors=SECTORS, sectors_all=SECTORS_ALL)

    # efficient frontier: monthly excess returns of the 9 sectors and SPY (same call as fig_frontier)
    S = [s + '.US' for s in SECTORS]
    ex, F = g.monthly_excess(S + ['SPY.US'])
    d['fr'] = dict(dates=ym(ex.index), R=r(ex[S].values), spy=r(ex['SPY.US'].values), res=res['frontier'])

    # XLK market model (Seminar 3, problem B1): XLK excess return on Mkt-RF, block-bootstrap draws of alpha
    import seminar3 as s3
    ex, F = g.monthly_excess(['XLK.US', 'SPY.US'])
    y, x = ex['XLK.US'].values, F['Mkt-RF'].values
    ci, bse, draws = s3.block_bootstrap_alpha(y, x, block=12, periods=12, draws=True)
    d['xlk'] = dict(dates=ym(ex.index), y=r(y, 7), x=r(x, 7), draws12=r(draws, 6), ci12=r(ci), se12=float(bse))

    # Dimson beta: the simulated draws of seminar3_explainers.fig_dimson (same seed and order)
    T = 5000
    rng = np.random.default_rng(23)
    rm = rng.normal(0, 1, T)
    eps = rng.normal(0, 1, T)
    u = rng.uniform(size=T)
    d['dim'] = dict(rm=r(rm, 5), eps=r(eps, 5), u=r(u, 5))

    # rolling betas: daily log returns of four sectors and SPY (same call as fig_rolling_beta)
    R4 = ['XLK.US', 'XLU.US', 'XLF.US', 'XLE.US']
    lr = log_returns(prices(R4 + ['SPY.US']))
    d['rb'] = dict(dates=ymd(lr.index), names=[s[:-3] for s in R4], R=r(lr[R4].values.T, 5), m=r(lr['SPY.US'].values, 5),
                   res=res['rolling_beta'])

    # 25 size x B/M portfolios and the factors, July 1963 - July 2026 (sml_data, fig_fama_macbeth)
    sres, ex25, mk = g.sml_data()
    Ff = factors('M').loc[ex25.index]
    d['p25'] = dict(dates=ym(ex25.index), names=list(ex25.columns), R=r(ex25.values.T, 6),
                    f={c: r(Ff[c].values, 6) for c in ['Mkt-RF', 'SMB_FF3', 'HML', 'SMB', 'RMW', 'CMA']},
                    avg=r(sres['avg'].values), alpha=r(sres['alpha'].values), t=r(sres['t_alpha'].values, 4),
                    beta=r(sres['beta'].values), sml=res['sml'], fm=res['fama_macbeth'])

    # cumulative factor returns (fig_factor_cum)
    Fc = factors('M').loc[:g.END]
    cols = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    d['fc'] = dict(dates=ym(Fc.index), f={c: r(Fc[c].values, 6) for c in cols}, res=res['factor_cum'])

    # PCA of the 11 sector ETFs, daily log returns (pca_sectors)
    vals, vecs, lr11, c1 = g.pca_sectors()
    S11 = [s + '.US' for s in SECTORS_ALL]
    d['pca'] = dict(dates=ymd(lr11.index), R=r(lr11[S11].values.T, 5), spy=r(lr11['SPY.US'].values, 5),
                    ev=r(vals), res=res['pca'])

    # factor ETFs: total-return prices relative to the first common day (fig_factor_etfs)
    E = [e + '.US' for e in FACTOR_ETFS] + ['SPY.US']
    p = prices(E)
    W = p / p.iloc[0]
    d['etf'] = dict(dates=ymd(p.index), names=[e[:-3] for e in E], W=r(W.values.T, 4), res=res['factor_etfs'])

    # AI mini-case: MOM and Mkt-RF, January 1965 - August 2026, in % a month (ai_discovery_case.py)
    Fa = factors('M').loc['1965-01-01':'2026-08-31']
    d['ai'] = dict(dates=ym(Fa.index), MOM=r(Fa['MOM'].values * 100, 4), MKT=r(Fa['Mkt-RF'].values * 100, 4),
                   res=json.load(open(os.path.join(HERE, 'ai_discovery_case.json'))))

    d['tf'] = export_tf()

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 3 interactive page, exported by Quantlets/Ch_03/export_interactive.py.\n')
        f.write('window.CH3_DATA = ' + json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null') + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    if '--only' in sys.argv:
        only(sys.argv[sys.argv.index('--only') + 1].split(','))
    else:
        main()

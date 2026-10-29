"""Export the inputs of the Chapter 6 interactive page (MFM/interactive/ch6_data.js).

Uses the data loaders and estimators of mfm_data.py, dep_tools.py and generate_all_charts.py, so the page starts from
the same data and numbers as the slides. No chart function is called and save_fig is replaced by plt.close, so the
slide charts and the results files are not rewritten. The numbers of ch6_numbers.json, ch6_inference_numbers.json and
ai_discovery_case.json are exported as reference values ('ref').

Encoding: dates as days since 1970-01-01, delta-encoded (first day, then the gaps); returns as integers in units of
1e-5, standardised residuals and volatilities in units of 1e-4 (divided back in ch6.js).
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import generate_all_charts as g
from mfm_data import joint_returns, joint_prices, weekly_returns, BANKS
from dep_tools import (garch_all, dcc_fit, pseudo_obs, simulate, fit_copula, empirical_tail_dep, theta_from_tau,
                       exceedance_corr, FAMILIES)
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch6_data.js')
EPOCH = pd.Timestamp('1970-01-01')

g.save_fig = lambda name: plt.close()          # keep the slide charts untouched


def tdelta(idx):
    t = ((pd.DatetimeIndex(idx) - EPOCH).days).tolist()
    return [t[0]] + np.diff(t).tolist()


def q(x, unit):
    """Integers in the given unit (x / unit, rounded)."""
    return np.round(np.asarray(x, float) / unit).astype(int).tolist()


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    return o


def panel(df, unit=1e-5):
    return dict(t=tdelta(df.index), cols=list(df.columns), v={c: q(df[c].values, unit) for c in df.columns})


def ai_inflation_frame():
    """The monthly frame of ai_discovery_case.py (same steps; CPIAUCSL read from FRED as in that script)."""
    R = joint_returns(['spy', 'tlt'])
    gr = R.groupby(R.index.to_period('M'))
    rho_m = gr.apply(lambda x: x['spy'].corr(x['tlt']) if len(x) >= 15 else np.nan).dropna()
    rho_m = rho_m.iloc[1:-1] if rho_m.index[-1] >= pd.Period('2026-09', 'M') else rho_m.iloc[1:]
    z_m = np.arctanh(rho_m)
    cpi = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL', index_col=0, parse_dates=True).iloc[:, 0]
    cpi.index = cpi.index.to_period('M')
    infl = 100 * (cpi / cpi.shift(12) - 1)
    x = infl.shift(2).reindex(z_m.index)
    return pd.DataFrame({'z': z_m, 'rho': rho_m, 'infl': x}).dropna()


def main():
    NUM = json.load(open(os.path.join(HERE, 'ch6_numbers.json')))
    INF = json.load(open(os.path.join(HERE, 'ch6_inference_numbers.json')))
    AI = json.load(open(os.path.join(HERE, 'ai_discovery_case.json')))
    d = {}

    # SPY-TLT daily log returns, GARCH(1,1) and DCC(1,1) (rolling, HAC, EWMA, DCC, minimum variance)
    R, P, V, Z, dc, rc, ll1 = g.dcc_pair(['spy', 'tlt'])
    assert len(R) == len(Z) == NUM['dcc_n'] and (R.index == Z.index).all()
    d['st'] = dict(t=tdelta(R.index), r1=q(R['spy'], 1e-5), r2=q(R['tlt'], 1e-5),
                   z1=q(Z['spy'], 1e-4), z2=q(Z['tlt'], 1e-4), v1=q(V['spy'], 1e-4), v2=q(V['tlt'], 1e-4),
                   a=dc['a'], b=dc['b'], Qbar=dc['Qbar'].tolist(), ll=dc['loglik'], ll_ccc=dc['ccc_loglik'])

    # asynchronous trading: SPY, Euro Stoxx 50, BET on common days from 2000; weekly returns on Friday closes
    Pa = joint_prices(['spy', 'stoxx', 'bet'], start='2000-01-01')
    d1 = np.log(Pa).diff().dropna()
    wk = np.log(Pa.resample('W-FRI').last()).diff().dropna()
    d['as'] = dict(daily=panel(d1), weekly=panel(wk), table=g.async_table().to_dict('records'))

    # Forbes-Rigobon: overlapping 2-day returns S&P 500, Euro Stoxx 50, BET (around the 2008 windows)
    r2 = g.two_day_returns(['sp500', 'stoxx', 'bet']).loc['2007-05-01':'2009-07-31']
    d['fr'] = dict(r2=panel(r2), calm=g.CALM08, crisis=g.CRISIS08,
                   table=pd.read_csv(os.path.join(HERE, 'ch6_forbes_rigobon_2008.csv')).to_dict('records'))

    # exceedance correlations: weekly S&P 500 and Euro Stoxx 50; Normal reference on a grid of quantiles
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    rho = np.corrcoef(W['sp500'].values, W['stoxx'].values)[0, 1]
    rng = np.random.default_rng(g.SEED)
    Zs = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], 2_000_000)     # same draws as fig_exceedance
    qg = np.round(np.arange(5, 51) / 100, 2)
    en = exceedance_corr(Zs[:, 0], Zs[:, 1], qg)
    d['ex'] = dict(w=panel(W), q=qg.tolist(), norm_low=r(en['rho_low']), norm_high=r(en['rho_high']))

    # five copulas with Kendall's tau = 0.5: the draws of fig_copula_zoo (same generator, same order)
    rng = np.random.default_rng(g.SEED)
    zoo = {}
    for fam in FAMILIES:
        th = theta_from_tau(fam, 0.5)
        par = [th, 4.0] if fam == 't' else [th]
        X = stats.norm.ppf(simulate(fam, par, 1500, rng))
        zoo[fam] = dict(par=float(th), x=q(X[:, 0], 1e-2), y=q(X[:, 1], 1e-2))
    d['zoo'] = zoo

    # JPM-BAC: GARCH standardised residuals, their ranks, the copula table, the tail-dependence band
    Rb, Zb, Ub = g.bank_copula_data()
    rk = np.column_stack([stats.rankdata(Zb.values[:, k]) for k in range(2)]).astype(int)
    tb = pd.read_csv(os.path.join(HERE, 'ch6_copula_jpm_bac.csv')).set_index('family')
    u, v = Ub[:, 0], Ub[:, 1]
    ft = fit_copula('t', u, v)
    qs = np.linspace(0.01, 0.20, 20)
    rng = np.random.default_rng(g.SEED)
    sims = []
    for _ in range(200):                                   # the band of fig_tail_dep (same generator)
        X = pseudo_obs(simulate('t', ft['par'], len(u), rng))
        sims.append([empirical_tail_dep(X[:, 0], X[:, 1], qq)[0] for qq in qs])
    sims = np.array(sims)
    d['bk'] = dict(t=tdelta(Zb.index), z1=q(Zb['jpm'], 1e-2), z2=q(Zb['bac'], 1e-2), r1=rk[:, 0].tolist(), r2=rk[:, 1].tolist(),
                   table={f: {k: (None if pd.isna(tb.loc[f, k]) else float(tb.loc[f, k])) for k in tb.columns} for f in tb.index},
                   t_par=ft['par'], t_ll=ft['loglik'], qs=r(qs), band_lo=r(np.percentile(sims, 5, axis=0)),
                   band_hi=r(np.percentile(sims, 95, axis=0)))

    # market integration: weekly S&P 500, Euro Stoxx 50, BET from 2000
    d['int'] = panel(weekly_returns(['sp500', 'stoxx', 'bet'], start='2000-01-01'))

    # banks: weekly returns from 2010
    d['banks'] = panel(weekly_returns(BANKS, start='2010-01-01'))

    # AI mini-case: monthly SPY-TLT correlation and the inflation known at the start of the month
    df = ai_inflation_frame()
    d['ai'] = dict(m=[str(p) for p in df.index], rho=r(df['rho'], 8), infl=r(df['infl'], 8))

    keep_inf = {k: v for k, v in INF.items() if k.startswith('hac_')}
    d['ref'] = dict(num=NUM, inf=keep_inf, ai=AI)

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 6 interactive page, exported by Quantlets/Ch_06/export_interactive.py.\n')
        f.write('window.CH6_DATA = ' + json.dumps(jsonable(d), separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
    # checks against the results files
    print('dcc a, b, ll:', dc['a'], dc['b'], dc['loglik'], '| json:', NUM['dcc_a'], NUM['dcc_b'], NUM['dcc_ll'])
    print('t copula:', ft['par'], ft['loglik'], '| csv:', tb.loc['t', 'par1'], tb.loc['t', 'par2'], tb.loc['t', 'loglik'])
    i5 = int(np.argmin(np.abs(qs - 0.05)))
    print('band at 5%:', np.percentile(sims[:, i5], 5), np.percentile(sims[:, i5], 95), '| json:', NUM['td_band05_lo'], NUM['td_band05_hi'])
    print('exceedance normal 10%, 20%:', en.loc[0.10, 'rho_low'], en.loc[0.20, 'rho_low'], '| json:', NUM['ex_norm10'], NUM['ex_norm20'])
    print('ai months:', len(df), df.index[0], df.index[-1], '| json:', AI['full']['n'])


if __name__ == '__main__':
    main()

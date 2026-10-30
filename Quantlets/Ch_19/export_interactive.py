"""Export the inputs of the Chapter 19 interactive page (MFM/interactive/ch19_data.js).

Uses the data loaders and functions of the chapter (mfm_data.py, case_study.py, inference19.py,
nonstandard_errors.py, generate_all_charts.py), so the page starts from the same numbers as the slides.
No chart or results file of the chapter is written: save_fig, save_nse_fig and plt.savefig are replaced by no-ops,
ch19_results.json and ch19_nse.json are only read, and the rolling VaR forecasts are read from
ch19_forecasts_bet.csv (written by generate_all_charts.part_var with case_study.rolling_var).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch19_data.js')
sys.path.insert(0, HERE)


# =============================================================================
# --only int: the three integrated case studies (29 Oct 2026). Reads the series written by integrated_cases.py
# (ch19_int_*.csv, ch19_integrated.json) and the daily Bitcoin returns through the Chapter 9 loader; adds the keys
# ip, ib, ir to interactive/ch19_data.js and keeps every other key unchanged. Runs before the imports below, which
# load the BET case study.
# =============================================================================
def export_integrated():
    import integrated_cases as IC
    js_path = OUT
    text = open(js_path).read()
    head, body = text.split('window.CH19_DATA = ', 1)
    d = json.loads(body.rstrip().rstrip(';'))
    old = {k: v for k, v in d.items() if k not in ('ip', 'ib', 'ir')}
    R = json.load(open(os.path.join(HERE, 'ch19_integrated.json')))
    rd = lambda f: pd.read_csv(os.path.join(HERE, f), index_col=0, parse_dates=True)   # noqa: E731
    cal = lambda idx: dict(d0=f'{idx[0]:%Y-%m-%d}', gaps=np.diff(idx.values.astype('datetime64[D]').astype(np.int64)).tolist())  # noqa: E731
    I = lambda x, k: [None if not np.isfinite(v) else int(v) for v in np.round(np.asarray(x, float) * 10 ** k)]   # noqa: E731
    # 1. portfolio
    F = rd('ch19_int_pf.csv')
    M = F[list(IC.CLASSES)].resample('ME').mean()
    P = R['pf']
    d['ip'] = dict(cal=cal(F.index), ret=I(F['ret'], 5), sig=I(F['sig'], 6), var_fhs=I(F['var_fhs'], 5),
                   var_hs=I(F['var_hs'], 5), vol_gmv=I(F['vol_gmv'], 4), vol_lw=I(F['vol_lw'], 4),
                   months=[f'{t:%Y-%m}' for t in M.index], shares={c: I(M[c], 4) for c in IC.CLASSES},
                   choice=P['step1']['choice'], ref={k: {c: P['step3'][k][c] for c in ('x', 'p_uc', 'p_ind', 'p_cc')}
                                                     for k in P['step3']},
                   vol=P['step1']['vol'], shares_mean=P['shares']['mean'])
    # 2. Bitcoin: forecast days, losses (UTC days), log-HAR variance forecasts; daily returns for the HS window
    D = rd('ch19_int_btc.csv').dropna(subset=['var_har'])
    M9 = IC.chapter(9, 'mfm_data')
    daily = M9.daily_returns('btc', start='2014-09-17')
    daily = daily.loc[D.index[0] - pd.Timedelta(days=900):D.index[-1]]
    fc_var = (D['var_har'] / IC.stats.norm.ppf(0.99)) ** 2
    W = rd('ch19_int_btc_weekly.csv').dropna(subset=['bsadf'])
    Mi = rd('ch19_int_btc_illiq.csv')
    B = R['btc']
    d['ib'] = dict(cal=cal(D.index), loss=I(D['loss'], 5), fvar=I(fc_var, 5), dcal=cal(daily.index), daily=I(daily, 5),
                   wcal=cal(W.index), bsadf=I(W['bsadf'], 4), cv95=I(W['cv95'], 4), episodes=B['step5']['episodes'],
                   months=[f'{t:%Y-%m}' for t in Mi.index], ill_btc=I(Mi['ill_btc'], 7), ill_spy=I(Mi['ill_spy'], 7),
                   ref={k: {c: B['step3'][k][c] for c in ('x', 'p_uc', 'p_ind', 'p_cc')} for k in ('har', 'hs')},
                   var_mean={'har': B['step3']['var_har_mean'], 'hs': B['step3']['var_hs_mean']},
                   gsadf=B['step5']['gsadf'], cv_gsadf=B['step5']['cv95'], amihud=B['step4']['amihud'],
                   amihud_spy=B['step4']['amihud_spy'])
    # 3. Romanian investor: daily log returns (variance ratios) and weekly log returns (hedge, ES)
    M2 = IC.chapter(2, 'mfm_data')
    dd = {}
    for k in ('eurron', 'bet', 'stoxx'):
        r = np.log(M2.load_close(k, start='2005-07-01')).diff().dropna()
        dd[k] = dict(cal=cal(r.index), r=I(r, 8))
    Wr = rd('ch19_int_ron.csv')
    Rr = R['ron']
    d['ir'] = dict(daily=dd, wcal=cal(Wr.index), stoxx=I(Wr['stoxx'], 8), bet=I(Wr['bet'], 8), fx=I(Wr['fx'], 8),
                   periods=Rr['periods'], window=Rr['window'],
                   ref=dict(z={k: Rr['step1'][k]['z'] for k in Rr['step1']},
                            es={p: {k: v['es'] for k, v in Rr['step5'][p].items()} for p in Rr['step5']},
                            h_full=Rr['step4']['h_full'], h_last=Rr['step4']['h_last']))
    assert all(d[k] == v for k, v in old.items())
    js = json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null').replace('Infinity', 'null')
    with open(js_path, 'w') as fh:
        fh.write(head + 'window.CH19_DATA = ' + js + ';\n')
    print('wrote', js_path, os.path.getsize(js_path) // 1024, 'KB (keys ip, ib, ir; other keys unchanged)')


if __name__ == '__main__' and sys.argv[1:] == ['--only', 'int']:
    export_integrated()
    sys.exit(0)

import matplotlib                                   # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                     # noqa: E402

import generate_all_charts as g                     # noqa: E402
import nonstandard_errors as nse                    # noqa: E402
from case_study import (MODELS, stylised_facts, garch_t_fit, garch_summary, backtest_table,  # noqa: E402
                        binom_band)
from inference19 import hill_k, hill, kupiec_power, kupiec_mde  # noqa: E402

g.save_fig = lambda name: plt.close('all')
nse.save_nse_fig = lambda name: plt.close('all')
plt.savefig = lambda *a, **k: None


def ints(x, k):
    """Values times 10^k, rounded to integers (compact JSON)."""
    return [int(v) for v in np.round(np.asarray(x, float) * 10 ** k)]


def calendar(idx):
    return dict(d0=f'{idx[0]:%Y-%m-%d}', gaps=np.diff(idx.values.astype('datetime64[D]').astype(np.int64)).tolist())


def close(a, b, tol, what):
    assert abs(a - b) <= tol, (what, a, b)


def main():
    R = json.load(open(os.path.join(HERE, 'ch19_results.json')))
    N = json.load(open(os.path.join(HERE, 'ch19_nse.json')))
    r = g.r                                                     # BET daily log returns in %, as in the chapter
    d = dict(models=MODELS, mcol=g.MODEL_COL)

    # ------------------------------------------------------------------ Step 1: stylised facts
    sf = stylised_facts(r)
    assert sf['N'] == R['facts']['N'] and sf['n4'] == R['facts']['n4']
    close(sf['q_r2'], R['facts']['q_r2'], 1e-6, 'Q(10)')
    k = hill_k(r.values)
    assert k == R['facts']['hill']['k']
    close(hill(-r.values, k), R['facts']['hill']['alpha'], 1e-12, 'Hill')
    d['cal'] = calendar(r.index)
    d['r'] = ints(r.values, 5)                                   # % with 5 decimals
    d['facts'] = {c: R['facts'][c] for c in ('N', 'n4', 'n4_normal', 'acf1_r', 'acf1_abs', 'q_r2', 'min', 'min_date')}
    d['facts']['hill'] = {c: R['facts']['hill'][c] for c in ('alpha', 'k', 'lo', 'hi')}

    # ------------------------------------------------------------------ Step 2: GARCH(1,1)-t on the full sample
    res = garch_t_fit(r)
    gs = garch_summary(res)
    p = res.params
    for c in ('alpha', 'beta', 'nu', 'pers', 'half_life'):
        close(gs[c], R['garch'][c], 1e-9, c)
    cv = res.conditional_volatility.values
    close(cv.max(), R['garch']['sigma_max'], 1e-9, 'sigma max')
    close(cv[-1], R['garch']['sigma_last'], 1e-9, 'sigma T')
    # the recursion of the page, started from the first conditional variance of the fit
    e = (r - p['mu']).values
    s2 = np.empty(len(e))
    s2[0] = cv[0] ** 2
    for t in range(1, len(e)):
        s2[t] = p['omega'] + p['alpha[1]'] * e[t - 1] ** 2 + p['beta[1]'] * s2[t - 1]
    assert np.abs(np.sqrt(s2) - cv).max() < 1e-9
    d['garch'] = dict(mu=p['mu'], omega=p['omega'], alpha=p['alpha[1]'], beta=p['beta[1]'], nu=p['nu'], s2_0=float(cv[0] ** 2),
                      se_alpha=gs['se_alpha'], se_beta=gs['se_beta'], half_life=gs['half_life'], uncond_vol=gs['uncond_vol'],
                      ppy=R['facts']['ppy'], sigma_max=R['garch']['sigma_max'], sigma_max_date=R['garch']['sigma_max_date'],
                      sigma_last=R['garch']['sigma_last'])

    # ------------------------------------------------------------------ Steps 3-4: rolling VaR forecasts and breaches
    fc = pd.read_csv(os.path.join(HERE, 'ch19_forecasts_bet.csv'), index_col='date', parse_dates=True)
    i0 = r.index.get_loc(fc.index[0])
    assert r.index[i0:].equals(fc.index), 'forecast days = return days from the start of the evaluation'
    assert np.allclose(fc['L'].values, -r.values[i0:], atol=1e-12)
    bt = backtest_table(fc)
    for m in MODELS:
        for c in ('x', 'T', 'p_uc', 'p_cc'):
            close(bt[m][c], R['backtest'][m][c], 1e-12, (m, c))
    lo, hi = binom_band(len(fc))
    close(lo, R['eval']['band'][0], 1e-15, 'band')
    close(hi, R['eval']['band'][1], 1e-15, 'band')
    d['i0'] = int(i0)
    d['var'], d['hits'] = {}, {}
    for lev, suf in (('1', ''), ('2.5', '_V25')):
        d['var'][lev], d['hits'][lev] = {}, {}
        for m in MODELS:
            v = fc[m + suf].values
            d['var'][lev][m] = ints(v, 4)                        # % with 4 decimals, for drawing
            d['hits'][lev][m] = np.flatnonzero(fc['L'].values > v).tolist()   # exact breaches
    d2 = fc.loc['2020-01-01':]
    v20 = R['var_2020']
    assert len(d2) == v20['n'] and int((d2['L'] > d2['FHS']).sum()) == v20['x_fhs'] and int((d2['L'] > d2['Normal']).sum()) == v20['x_normal']
    d['backtest'] = {m: {c: R['backtest'][m][c] for c in ('x', 'rate', 'p_uc')} for m in MODELS}
    d['eval'] = R['eval']
    d['var_2020'] = v20

    # ------------------------------------------------------------------ power of the Kupiec test (computed in the page)
    for T in (250, 1000, len(fc)):
        close(kupiec_power(T, 0.02)[0], R['power']['pw'][f'{T}_0.02'], 1e-12, ('power', T))
        close(kupiec_mde(T), R['power']['mde'][str(T)], 1e-12, ('mde', T))
    d['power'] = R['power']

    # ------------------------------------------------------------------ nonstandard errors: the mini-multiverse
    d['nse'] = {}
    for sym, lab in nse.NSE_INDICES.items():
        x = nse.index_returns(sym)
        tab = nse.multiverse(x)
        ref = pd.DataFrame(N[lab]['table'])
        assert len(x) == N[lab]['N'] and np.allclose(tab['est'].round(4).values, ref['est'].values, atol=1e-9)
        q25, q50, q75 = np.percentile(tab['est'], [25, 50, 75])
        close(q75 - q25, N[lab]['iqr'], 1e-9, 'iqr')
        years = x.index.year
        d['nse'][lab] = dict(x=ints(x.values, 9), years=sorted(set(years.tolist())), n=pd.Series(years).value_counts().sort_index().tolist(),
                             est=tab['est'].round(6).tolist(), se=tab['se'].round(6).tolist(),
                             median=N[lab]['median'], iqr=N[lab]['iqr'], med_se=N[lab]['med_se'], iqr_trend=N[lab]['iqr_trend'],
                             median_by_model=N[lab]['median_by_model'], max_rel=N[lab]['max_rel'])
    d['nse_forks'] = dict(outliers=nse.OUTLIERS, measures=nse.MEASURES, models=nse.FORK_MODELS)

    js = json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null').replace('Infinity', 'null')
    with open(OUT, 'w') as fh:
        fh.write('// Inputs of the Chapter 19 interactive page, exported by Quantlets/Ch_19/export_interactive.py.\n')
        fh.write('window.CH19_DATA = ' + js + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

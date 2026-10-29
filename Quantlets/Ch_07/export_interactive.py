"""Export the inputs of the Chapter 7 interactive page (MFM/interactive/ch7_data.js).

Uses the chapter's own functions (generate_all_charts.py, risk_measures.py, estimation_risk.py) and its results
files (ch7_results.json, ch7_inference.json, ai_discovery_case.json, ch7_rolling_sp500.csv), so the page starts
from the same numbers as the slides. No chart is drawn: the save function of the chapter is replaced by a no-op
and the chart files are checked to be unchanged.
"""
import glob
import hashlib
import json
import os

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

import generate_all_charts as g
import estimation_risk as er
from risk_measures import hs_var_es, gpd_fit, gpd_se, gpd_var_es, garch_filter, garch_next, fhs_mc, mean_excess
from mfm_data import joint_returns

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch7_data.js')
CHARTS = os.path.join(HERE, '..', '..', 'charts')
DAY0 = pd.Timestamp('2000-01-01')
A_GRID = [0.001, 0.0025, 0.005, 0.01, 0.025, 0.05]       # tail probabilities offered by the conditional blocks


def _noop(*a, **k):
    plt.close('all')


g.save_fig = er.save_fig = _noop


def r(x, d=4):
    return np.round(np.asarray(x, float), d).tolist()


def days(idx):
    return [int((t - DAY0).days) for t in idx]


def chart_hashes():
    return {f: hashlib.md5(open(f, 'rb').read()).hexdigest() for f in sorted(glob.glob(os.path.join(CHARTS, 'ch7_*')))}


def main():
    before = chart_hashes()
    res = json.load(open(os.path.join(HERE, 'ch7_results.json')))
    inf = json.load(open(os.path.join(HERE, 'ch7_inference.json')))
    ai = json.load(open(os.path.join(HERE, 'ai_discovery_case.json')))
    t = res['table']
    d = dict(order=g.ORDER, labels={k: g.LABELS[k].replace(' (reference rate)', '') for k in g.ORDER})

    # daily losses L = -r (%), all five series; S&P 500 dates as days since 2000-01-01
    d['loss'] = {k: r(g.loss[k].values, 4) for k in g.ORDER}
    d['sp_days'] = days(g.loss['sp500'].index)
    d['table'] = {k: {c: t[k][c] for c in ('N', 'mean', 'sd', 'skew', 'kurt', 'max', 'max_date', 't_nu', 't_loc', 't_scale',
                                           'gpd_u', 'gpd_xi', 'gpd_beta', 'gpd_nu', 'gpd_xi_se')} for k in g.ORDER}
    for k in g.ORDER:
        for c in ('HS|VaR 1%', 'HS|ES 2.5%', 'HS|ES 1%', 'HS|VaR 2.5%'):
            d['table'][k][c] = t[k][c]
    d['loss_dist'] = res['loss_dist']
    d['bonds'] = res['bonds']

    # VaR and ES against the tail probability, five methods (S&P 500)
    L = g.loss['sp500']
    levels = np.unique(np.concatenate([np.geomspace(0.05, 0.001, 50), A_GRID]))[::-1]
    f5, tp = gpd_fit(L, 0.05), g.t_fit(L)
    cur = {m: ([], []) for m in g.METHODS}
    for a in levels:
        for m, (v, e) in {'HS': hs_var_es(L, a), 'Normal': g.normal_var_es(L, a), 'Student-t': g.t_var_es(L, a, tp),
                          'Cornish-Fisher': g.cf_var_es(L, a), 'EVT (GPD)': gpd_var_es(f5, a)}.items():
            cur[m][0].append(v)
            cur[m][1].append(e)
    for m in g.METHODS:
        assert abs(cur[m][0][-1] - res['levels'][m]['var0_1']) < 1e-9
    d['levels'] = dict(alpha=r(levels, 6), var={m: r(cur[m][0]) for m in g.METHODS}, es={m: r(cur[m][1]) for m in g.METHODS})

    # precision: asymptotic and bootstrap 95% intervals, full sample and the last n days
    Lv = L.values
    prec = {}
    for n in (250, 500, 750, 1000, 1500, 2000, 3000, 4000, len(Lv)):
        x = Lv[-n:]
        s = er.var_es_se(x)
        ci_iid, _ = er.boot_ci(x, lambda y: hs_var_es(y, 0.025)[1])
        ci_blk, _ = er.boot_ci(x, lambda y: hs_var_es(y, 0.025)[1], block=20)
        prec[n] = dict(var=s['var1'], se_var=s['se_var'], se_var_hac=s['se_var_hac'], es=s['es'], se_es=s['se_es'],
                       se_es_hac=s['se_es_hac'], iid=list(ci_iid), blk=list(ci_blk), ntail=s['ntail'])
    for n, tag in ((len(Lv), 'sp500_full'), (500, 'sp500_w500')):
        for c in ('var1', 'se_var', 'se_var_hac', 'es', 'se_es', 'se_es_hac'):
            assert abs(prec[n]['var' if c == 'var1' else c] - inf['se'][tag][c]) < 1e-9
    d['prec'] = {str(n): {k: (r(v, 5) if isinstance(v, list) else round(float(v), 5)) for k, v in p.items()} for n, p in prec.items()}

    # conditional VaR/ES, S&P 500 2006-2026: AR(1)-GARCH(1,1) re-estimated every January (risk_measures.rolling_conditional)
    rs = g.rets['sp500']
    csv = pd.read_csv(os.path.join(HERE, 'ch7_rolling_sp500.csv'), index_col=0, parse_dates=True).loc['2006-01-01':]
    mu_all, sig_all, years = [], [], []
    for y in range(2006, rs.index[-1].year + 1):
        est = rs.loc[:f'{y - 1}-12-31']
        params, mu, sig = garch_filter(rs, last_obs=f'{y}-01-01')
        z = ((est - mu.loc[est.index]) / sig.loc[est.index]).dropna()
        nz = -z.values
        fz = gpd_fit(nz, 0.10)
        dd = rs.loc[f'{y}-01-01':f'{y}-12-31'].index
        mu_all.append(mu.loc[dd].values)
        sig_all.append(sig.loc[dd].values)
        q = [float(np.quantile(nz, 1 - a)) for a in A_GRID]
        years.append(dict(year=y, n=len(dd), fhs_q=r(q, 6), fhs_e=r([nz[nz >= qq].mean() for qq in q], 6),
                          gpd=dict(u=round(fz['u'], 8), xi=round(fz['xi'], 8), beta=round(fz['beta'], 8), nu=fz['nu'], n=fz['n'])))
    mu_all, sig_all = np.concatenate(mu_all), np.concatenate(sig_all)
    assert len(mu_all) == len(csv) and np.allclose(csv['sigma'].values, sig_all, atol=1e-9)
    k1 = A_GRID.index(0.01)
    q1 = np.concatenate([[yy['fhs_q'][k1]] * yy['n'] for yy in years])
    assert np.abs(-mu_all + sig_all * q1 - csv['fhs_var'].values).max() < 1e-4
    d['roll'] = dict(start=int(np.searchsorted(g.loss['sp500'].index, csv.index[0])), mu=r(mu_all, 5), sigma=r(sig_all, 5),
                     years=years, alphas=A_GRID, check=dict(fhs_var=r(csv['fhs_var'].values[:5], 6), cevt_var=r(csv['cevt_var'].values[:5], 6),
                                                            cevt_es=r(csv['cevt_es'].values[:5], 6), hs_var=r(csv['hs_var'].values[:5], 6)))
    d['roll_res'] = dict(sp=res['roll_sp'], evt2018=res['cond_evt_sp_2018'])

    # CAViaR (SAV), parameters estimated on 2000-2015 (estimation_risk.caviar_study)
    cs = inf['caviar_sp']
    rv = rs.values
    v0 = -np.quantile(rv[:cs['n_est']][:300], 0.01)
    vpath = er.caviar_path((cs['b0'], cs['b1'], cs['b2']), rv, v0)
    oos = rs.index >= '2016-01-01'
    assert int(((-rv)[oos] > vpath[oos]).sum()) == cs['n_hit_caviar']
    d['caviar'] = dict(b=[cs['b0'], cs['b1'], cs['b2']], v0=float(v0), n_est=cs['n_est'], res=cs, path_check=r(vpath[oos][:5], 6))

    # GEV on block maxima: week, month (the slide), quarter, half-year, year
    gev = {}
    grp = {'week': [L.index.isocalendar().year.values, L.index.isocalendar().week.values], 'month': [L.index.year, L.index.month],
           'quarter': [L.index.year, L.index.quarter], 'half': [L.index.year, (L.index.month - 1) // 6], 'year': [L.index.year]}
    for b, keys in grp.items():
        M = L.groupby(keys).max()
        nb = L.groupby(keys).size().mean()
        c, loc, sc = stats.genextreme.fit(M.values)
        gev[b] = dict(M=r(M.values, 4), c=float(c), mu=float(loc), sigma=float(sc), n_block=float(nb), per_year=float(len(M) / (len(L) / 251.526)))
    assert abs(-gev['month']['c'] - res['gev']['xi']) < 1e-9
    d['gev'] = gev

    # mean excess and GPD tails for several threshold choices
    us = np.quantile(Lv, np.linspace(0.80, 0.995, 60))
    me, nme = mean_excess(Lv, us)
    tails = [0.20, 0.15, 0.10, 0.075, 0.05, 0.04, 0.03, 0.025, 0.02, 0.015, 0.01]
    fits = {}
    for k in ('sp500', 'btc'):
        Lk = g.loss[k].values
        fits[k] = []
        for tl in tails:
            f = gpd_fit(Lk, tl)
            fits[k].append(dict(tail=tl, u=f['u'], xi=f['xi'], beta=f['beta'], nu=f['nu'], n=f['n'], se_xi=gpd_se(f)[0],
                                var1=gpd_var_es(f, 0.01)[0], es1=gpd_var_es(f, 0.01)[1]))
    assert abs(fits['sp500'][4]['u'] - res['me']['u']) < 1e-12
    d['me'] = dict(u=r(us, 5), me=r(me, 5), n=nme.tolist())
    gt = {}
    for k in ('sp500', 'btc'):
        Lk = g.loss[k].values
        xx = np.geomspace(fits[k][0]['u'], Lk.max() * 1.3, 160)
        nu, m, s = g.t_fit(Lk)
        gt[k] = dict(top=r(np.sort(Lk[Lk > fits[k][0]['u']]), 4), x=r(xx, 4), norm=r(stats.norm.sf(xx, Lk.mean(), Lk.std()), 12),
                     t=r(stats.t.sf(xx, nu, m, s), 10), nu=float(nu), n=len(Lk))
    d['gpd'] = dict(tails=tails, fits={k: [{c: (round(v, 6) if isinstance(v, float) else v) for c, v in f.items()} for f in fits[k]] for k in fits},
                    curves=gt)

    # horizon: empirical ratios for h = 1..20, FHS Monte Carlo of the h-day loss
    hr = g.horizon_ratios(hs=tuple(range(1, 21)))
    for k in g.ORDER:
        assert abs(hr[k][10] - res['horizon'][k]['10']) < 1e-12
    params, mu, sig = garch_filter(rs)
    z = ((rs - mu) / sig).dropna().values
    m1, s1 = garch_next(rs, params)
    v1 = -m1 + s1 * np.quantile(-z, 0.99)
    hs1 = hs_var_es(-rs, 0.01)[0]
    edges = np.linspace(-12, 16, 141)
    mc = []
    for h in range(1, 21):
        sim = fhs_mc(rs, params, z, h, n_paths=200_000, seed=g.SEED)
        cnt, _ = np.histogram(sim, edges)
        v, e = hs_var_es(sim, 0.01)
        mc.append(dict(h=h, dens=r(cnt / (len(sim) * (edges[1] - edges[0])), 5), mc_var=v, mc_es=e, sqrt_var=np.sqrt(h) * v1, uncond_var=np.sqrt(h) * hs1))
    assert abs(mc[9]['mc_var'] - res['mc']['mc_var']) < 1e-9
    d['horizon'] = dict(ratio={k: [hr[k][h] for h in range(1, 21)] for k in g.ORDER}, rho1={k: hr[k]['rho1'] for k in g.ORDER},
                        edges=r(edges, 3), mc=[{c: (round(float(v), 5) if not isinstance(v, list) else v) for c, v in x.items()} for x in mc])

    # portfolio 40/30/20/10: simple daily returns (%)
    lr = joint_returns(g.PORT, start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)
    assert len(R) == res['port']['N']
    d['port'] = dict(names=g.PORT, w=g.W.tolist(), R=r(R.values, 5), start=str(lr.index[0].date()), end=str(lr.index[-1].date()), res=res['port'])

    d['basel'] = res['basel']
    d['crk'] = dict(methods=g.CRK_METHODS, table=g.CRK_TABLE6_1PCT)
    d['ai'] = ai

    with open(OUT, 'w') as fo:
        fo.write('// Inputs of the Chapter 7 interactive page, exported by Quantlets/Ch_07/export_interactive.py.\n')
        fo.write('window.CH7_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    assert chart_hashes() == before, 'chart files changed'
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB; chart files unchanged:', len(before))


if __name__ == '__main__':
    main()

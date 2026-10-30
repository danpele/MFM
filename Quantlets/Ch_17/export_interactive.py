"""Export the inputs of the Chapter 17 interactive page (MFM/interactive/ch17_data.js).

Calls the chapter's own code (generate_all_charts.py, bubbles.py, inference17.py, case_study17.py,
case_study17_crises.py with case17_crises.json) with the figure
saving switched off, so the page starts from the same series and numbers as the slides. Heavy computations (BSADF
critical values, LPPLS fits, Markov-switching estimation) are done here; the page only recombines their outputs.
The LPPLS confidence indicator is read from the chapter's precomputed tables (ch17_lppls_ci_*.csv); the LR bootstrap
replications from inference17.json.
"""
import json
import os
import sys

os.environ['MFM_CH17_RECOMPUTE'] = '0'      # never recompute (and rewrite) the LPPLS indicator tables
os.environ['SLIDE_FIT'] = '0'

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_all_charts as g             # noqa: E402
import inference17 as inf                   # noqa: E402
import case_study17 as cs                   # noqa: E402
import case_study17_crises as gh            # noqa: E402
from bubbles import psy, psy_cv, lppls_fit, lppls_conditions, lppls_qualified   # noqa: E402

OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch17_data.js')

# figures are captured instead of saved: nothing is written to charts/
FIGS = {}


def _capture(name):
    FIGS[name] = g.plt.gcf()


for mod in (g, inf, cs, gh):
    mod.save_fig = _capture
g.plt.savefig = lambda *a, **k: None


def r(x, d=4):
    return np.round(np.asarray(x, float), d).tolist()


def rn(x, d=4):
    """Rounded list with NaN -> None."""
    return [None if not np.isfinite(v) else round(float(v), d) for v in np.asarray(x, float)]


def ds(idx, fmt='%Y-%m-%d'):
    return [f'{t:{fmt}}' for t in pd.DatetimeIndex(idx)]


def lines(name, ax=0):
    """(x, y, label) of the lines of a captured figure."""
    a = FIGS[name].axes[ax]
    return [(l.get_xdata(), l.get_ydata(), l.get_label()) for l in a.get_lines()]


def eps(ep):
    return [dict(start=g.d2s(s), end=g.d2s(e), n=int(n)) for s, e, n in ep]


def main():
    res = json.load(open(os.path.join(HERE, 'ch17_results.json')))
    infj = json.load(open(os.path.join(HERE, 'inference17.json')))
    D = {}

    # 1. simulated rational bubble (Evans form): the same draws as fig_rational_bubble (seed 48)
    out = g.fig_rational_bubble()
    Pp = lines('ch17_rational_bubble')[0][1]
    rng = np.random.default_rng(48)
    T, rr, b0, su = 400, 0.01, 5.0, 0.03
    Dv = 1 + np.cumsum(0.01 * rng.standard_normal(T))
    U = rng.random(T)
    u = np.exp(rng.normal(-su ** 2 / 2, su, T))
    F = Dv / rr
    B = np.empty(T)
    B[0] = b0
    for t in range(1, T):
        if B[t - 1] <= b0:                                  # small-bubble branch, threshold alpha = b0
            B[t] = (1 + rr) * B[t - 1] * u[t]
        else:
            B[t] = (b0 + (1 + rr) / 0.97 * (B[t - 1] - b0 / (1 + rr))) * u[t] if U[t] < 0.97 else b0 * u[t]
    assert np.allclose(F + B, Pp)
    D['rational'] = dict(F=r(F, 4), U=r(U, 6), u=r(u, 6), r=rr, pi=0.97, b0=b0, collapses=out['collapses'], max_mult=out['max_mult'])

    # 2. nine episodes aligned at the peak (daily prices, peak = 100)
    tab = g.episode_table()
    g.fig_episodes(tab)
    ep = []
    for (x, y, lab), row in zip([l for l in lines('ch17_episodes') if not l[2].startswith('_')], tab):
        ep.append(dict(label=lab, d=np.round(np.asarray(x, float) * 365.25).astype(int).tolist(), y=r(y, 2),
                       peak=row['peak'], runup=row['runup2y'], maxdd4=row['maxdd']))
    D['episodes'] = ep

    # 3. Bubbles for Fama: crash frequency for several crash definitions (fall from a previous peak)
    # the lecture's sample: the full Kenneth French files, as in generate_all_charts.fig_gsy
    falls = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
    thrs = [0.5, 0.75, 1.0, 1.25, 1.5]
    gs = dict(thr=thrs, falls=falls, crash={}, crash_ci={}, uncond={}, n=[], n_ind=[], ret2=[], ret2_ci=[])
    evs = {th: g.gsy_events(th) for th in thrs}
    for th in thrs:
        d = evs[th]
        gs['n'].append(int(len(d)))
        gs['n_ind'].append(int(d['ind'].nunique()))
        gs['ret2'].append(float(d['ret2'].mean()))
        gs['ret2_ci'].append(g.cluster_boot(d, 'ret2'))
    for c in falls:
        k = f'{c:.2f}'
        gs['crash'][k], gs['crash_ci'][k] = [], []
        for th in thrs:
            d = evs[th].copy()
            d['crash'] = d['mdd'] <= -c
            gs['crash'][k].append(float(d['crash'].mean()))
            gs['crash_ci'][k].append(g.cluster_boot(d, 'crash'))
        pu, _, nu = g.gsy_unconditional(crash=c)
        assert nu == res['gsy']['n_months']
        gs['uncond'][k] = float(pu)
    gs['uncond_ret2'] = res['gsy']['uncond_ret2']
    row = res['gsy']['rows'][2]
    assert gs['n'] == [rw['n'] for rw in res['gsy']['rows']] and gs['n_ind'] == [rw['n_ind'] for rw in res['gsy']['rows']]
    assert np.allclose(gs['ret2'], [rw['ret2'] for rw in res['gsy']['rows']])
    assert abs(gs['crash']['0.40'][2] - row['crash']) < 1e-12 and np.allclose(gs['crash_ci']['0.40'][2], row['crash_ci'])
    assert abs(gs['uncond']['0.40'] - res['gsy']['uncond_crash']) < 1e-12
    D['gsy'] = gs

    # 4-5. null distributions of ADF, SADF and GSADF for T = 440 (Nasdaq 100, monthly), several minimum windows
    y_ndx = np.log(g.price('ndx', 'M'))
    o = psy(y_ndx.values)
    Tn = o['n']
    bins = np.arange(-5, 8.0001, 0.1)
    null = dict(T=Tn, w0_rule=o['w0'], r0_rule=o['r0'], bins=r(bins, 2), rows=[])
    for w0 in sorted({int(np.floor(f * Tn)) for f in (0.05, 0.075, 0.15, 0.2, 0.25, 0.3)} | {o['w0']}):
        cv = psy_cv(Tn, w0, g.R_MC, g.SEED)
        null['rows'].append(dict(w0=w0, cv={k: cv[k] for k in ('adf', 'sadf', 'gsadf')},
                                 hist={k: np.histogram(cv['null'][k], bins)[0].tolist() for k in ('adf', 'sadf', 'gsadf')}))
        if w0 == o['w0']:
            assert abs(cv['gsadf']['95'] - res['ndx']['cv_gsadf']['95']) < 1e-12
        print('null w0', w0, {k: round(cv[k]['95'], 2) for k in ('adf', 'sadf', 'gsadf')})
    D['null'] = null

    # 6. Shiller price-dividend ratio, monthly from 1871
    sh = g.shiller()                                    # the lecture's sample: the full Shiller file
    assert g.d2s(sh.index[-1]) == res['sp_pd']['end'], 'Shiller file newer than the lecture: rerun the chapter'
    y_pd = np.log(sh['PD'])
    o_pd = g.run_psy(y_pd, R=1000)
    assert o_pd['res']['n'] == res['sp_pd']['T'] and abs(o_pd['res']['gsadf'] - res['sp_pd']['gsadf']) < 1e-9
    assert [e['start'] for e in eps(o_pd['ep'])] == [e['start'] for e in res['sp_pd']['episodes']]
    D['sp_pd'] = dict(dates=ds(sh.index, '%Y-%m'), pd=r(sh['PD'].values, 2), bsadf=rn(o_pd['res']['bsadf'], 3),
                      cv=rn(o_pd['cv']['bsadf95'], 3), w0=o_pd['res']['w0'], L=o_pd['L'], T=o_pd['res']['n'],
                      gsadf=o_pd['res']['gsadf'], cv_gsadf=o_pd['cv']['gsadf'], episodes=eps(o_pd['ep']))
    print('sp_pd', D['sp_pd']['episodes'])

    # 7. Bitcoin weekly: Monte Carlo and wild-bootstrap critical values
    y_btc = np.log(g.price('btc', 'W'))
    o_btc = g.run_psy(y_btc, wild=True)
    assert abs(o_btc['res']['gsadf'] - res['btc']['gsadf']) < 1e-9
    D['btc'] = dict(dates=ds(y_btc.index), p=r(np.exp(y_btc.values), 2), bsadf=rn(o_btc['res']['bsadf'], 3),
                    cv_mc=rn(o_btc['cv']['bsadf95'], 3), cv_wild=rn(o_btc['wild']['bsadf95'], 3), w0=o_btc['res']['w0'],
                    L=o_btc['L'], T=o_btc['res']['n'], gsadf=o_btc['res']['gsadf'], cv_gsadf=o_btc['cv']['gsadf']['95'],
                    cv_gsadf_wild=o_btc['wild']['gsadf95'], episodes=eps(o_btc['ep']), episodes_wild=eps(o_btc['ep_wild']))

    # 8. family-wise critical values (Phillips-Shi 2020) for several monitoring windows tau_b
    fw = dict(tau=[26, 52, 78, 104, 156, 208], q={}, fwer=infj['fwer'])
    for tb in fw['tau']:
        fw['q'][str(tb)] = inf.ps_fwer_cv(y_btc.values, o_btc['res']['w0'], tau_b=tb)
        print('ps tau', tb, fw['q'][str(tb)])
    assert abs(fw['q']['104']['q95'] - infj['fwer']['cv_ps']['q95']) < 1e-12
    D['fwer'] = fw

    # 9. LPPLS on Bitcoin 2017: fits on [1 Jan 2017, t2], t2 weekly (the slide fit ends on 15 Nov 2017)
    pb = g.price('btc', 'D')
    ex = res['lppls_btc2017']
    fits = []
    for t2 in pd.date_range('2017-08-02', '2018-01-17', freq='7D'):
        w = pb.loc['2017-01-01':t2]
        f = lppls_fit(g.yrs(w.index), np.log(w.values))
        c = lppls_conditions(f)
        fits.append(dict(t2=g.d2s(w.index[-1]), tc=f['tc'], tc_date=g.d2s(g.todate(f['tc'])), m=f['m'], w=f['w'], A=f['A'], B=f['B'],
                         C1=f['C1'], C2=f['C2'], rel_err=f['rel_err'], osc=f['osc'], damping=f['damping'],
                         cond=c, q=lppls_qualified(f)))
        if t2 == pd.Timestamp('2017-11-15'):
            assert abs(f['tc'] - ex['tc']) < 1e-9 and abs(f['m'] - ex['m']) < 1e-9
    D['lppls'] = dict(t1='2017-01-01', fits=fits, peak=ex['peak'])

    # 10. stability of t_c: the slide's window starts and two alternatives for each series
    tcp = {}
    for k, starts, a, b, (pa, pb_) in [('btc', ['2016-07-01', '2017-01-01', '2017-04-01'], '2017-08-01', '2018-01-15', ('2017-06-01', '2018-03-31')),
                                       ('ndx', ['1998-04-08', '1998-10-08', '1999-01-08'], '1999-09-01', '2000-06-30', ('1999-06-01', '2000-12-31'))]:
        pk = g.price(k, 'D').loc[pa:pb_].idxmax()
        tcp[k] = dict(peak=g.d2s(pk), starts=starts, paths={})
        for t1 in starts:
            d = g.tc_path(k, t1, a, b)
            tcp[k]['paths'][t1] = dict(t2=ds(d['t2']), tc=ds(d['tc']), err=(d['tc'] - pk).dt.days.astype(int).tolist(), q=d['q'].astype(bool).tolist())
        print('tc path', k)
    D['tc'] = tcp

    # 11-12. LPPLS confidence indicator (precomputed tables of the chapter) and Bitcoin daily prices
    ci_b = pd.read_csv(os.path.join(HERE, 'ch17_lppls_ci_btc.csv'), index_col=0, parse_dates=True)
    ci_n = pd.read_csv(os.path.join(HERE, 'ch17_lppls_ci_ndx.csv'), index_col=0, parse_dates=True)
    p15 = g.price('btc', 'D', '2015-01-01')
    D['btcd'] = dict(dates=ds(p15.index), p=r(p15.values, 2))
    D['ci'] = dict(dates=ds(ci_b.index), ci=r(ci_b['ci'].values, 5), eval=res['ci_btc'])
    keys = list(g.COND_LABELS)
    agg = {}
    for tag, tb in (('btc', ci_b), ('ndx', ci_n)):
        gy = tb.groupby(tb.index.year)
        agg[tag] = {str(y): dict(n=int(t['n'].sum()), **{k: int(t[f'pass_{k}'].sum()) for k in keys}) for y, t in gy}
    D['filters'] = dict(keys=keys, labels=g.COND_LABELS, years=agg, btc=res['cond_btc'], ndx=res['cond_ndx'])

    # 13. Markov switching, Nasdaq 100 weekly
    p, rt, mres, hi = g.ms_fit('ndx', '1990-01-01')
    lo = 1 - hi
    P = np.asarray(mres.regime_transition)[:, :, 0]          # P[i, j] = P(s_t = i | s_{t-1} = j)
    par = mres.params
    D['ms'] = dict(dates=ds(rt.index), p=r(p.reindex(rt.index).values, 2), r=r(rt.values, 5),
                   mu=[float(par[f'const[{lo}]']), float(par[f'const[{hi}]'])],
                   sd=[float(np.sqrt(par[f'sigma2[{lo}]'])), float(np.sqrt(par[f'sigma2[{hi}]']))],
                   p11=float(P[lo, lo]), p22=float(P[hi, hi]),
                   fp=r(mres.filtered_marginal_probabilities[hi].values, 4), sp=r(mres.smoothed_marginal_probabilities[hi].values, 4),
                   summary=res['ms_ndx'])

    # 14. LR bootstrap replications
    D['lr'] = {k: dict(lr=v['lr'], lrs=r(v['lrs'], 3), q95=v['q95'], chi2_95=v['chi2_95'], df=v['chi2_df'], B=v['B'])
               for k, v in infj['regimes'].items()}

    # 15. dot-com vs AI: monthly prices from the first explosive signal (dates from ch17_results.json)
    ai = {}
    for k, sk in [('csco', 'csco'), ('nvda', 'nvda'), ('ndx', 'ndx95'), ('ndx', 'ndx23')]:
        pm = g.price(k, 'M')
        s = pd.Timestamp(res['ai'][sk]['start'])
        w = pm.loc[s:s + pd.DateOffset(months=96)]
        ai[sk] = dict(start=res['ai'][sk]['start'], dates=ds(w.index, '%Y-%m'), y=r(100 * w.values / w.iloc[0], 2))
        assert abs(w.max() / w.iloc[0] - res['ai'][sk]['peak_mult']) < 1e-9
    D['ai'] = ai

    # 16. U.S. housing cycle (FRED): prices and new-home sales, 2000 average = 100
    cyc = cs.fig_dnz_cycle()
    L = {l[2]: l for l in lines('ch17_dnz_cycle')}
    pi_ = L['Case-Shiller U.S. National Home Price Index']
    vi_ = L['New one-family houses sold, calendar-month adjusted']
    sales = cs.fred('HSN1FNSA').loc['2000':'2011']
    D['dnz'] = dict(dates=ds(pd.DatetimeIndex(pi_[0]), '%Y-%m'), price=r(pi_[1], 2), vol=r(vi_[1], 2),
                    vol_raw=r(100 * sales.values / sales.loc['2000'].mean(), 2), summary=cyc)
    assert abs(max(vi_[1]) - cyc['vol_peak_idx']) < 1e-9

    # 17. second case study: Greenwood, Hanson, Shleifer & Sorensen (2022) on the JST Macrohistory data
    G = json.load(open(os.path.join(HERE, 'case17_crises.json')))
    p = gh.panel()
    countries = sorted(p['country'].unique())
    gd = dict(countries=countries, q_grid=gh.Q_GRID, q_price=gh.Q_PRICE, paper=G['paper'], sample=G['sample'])
    for s_ in gh.SECTORS:
        x = gh.sector_sample(p, s_).reset_index(drop=True)
        o = G[s_]
        gd[s_] = dict(c=[countries.index(c) for c in x['country']], y=x['year'].astype(int).tolist(),
                      debt=r(x['debt'], 4), price=r(x['price'], 4),
                      crisis=[x[f'c{h}'].astype(int).tolist() for h in range(1, gh.HMAX + 1)],
                      onsets=[[countries.index(c['country']), c['year']] for c in o['crises']],
                      p_all=o['p_all'], ci_all=o['ci_all'], n_countries=o['n_countries'],
                      grid=G['grid'][s_])
        k = gh.Q_GRID.index(gh.Q_DEBT)
        assert gd[s_]['grid'][k]['p_rzone'] == o['p_rzone'] and gd[s_]['grid'][k]['ci_rzone'] == o['ci_rzone']
    D['ghss'] = gd

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 17 interactive page, exported by Quantlets/Ch_17/export_interactive.py.\n')
        f.write('window.CH17_DATA = ' + json.dumps(g.jsonable(D), separators=(',', ':'), allow_nan=False) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

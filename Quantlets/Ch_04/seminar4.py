"""
seminar4.py -- Calculele pentru Seminarul 4 (MFM): optimizarea portofoliului
===========================================================================
Partea A (verificari numerice ale derivarilor), Partea B (date reale), Partea C (analiza de referinta).
Toate rezultatele se scriu in sem4_results.json (folosite in ambele versiuni ale seminarului).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import prices, french_rf, bnr_rate, SECTORS, MULTI, BVB
import generate_all_charts as g

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42


def sr_diff_iid(sr1, sr2, rho, T):
    """Diferenta de Sharpe sub randamente i.i.d. Normale (formula raportata de Ledoit-Wolf 2008).

    sr1, sr2: Sharpe lunar; rho: corelatia randamentelor; intoarce (z, p).
    """
    v = (2 - 2 * rho + 0.5 * (sr1 ** 2 + sr2 ** 2 - 2 * sr1 * sr2 * rho ** 2)) / T
    z = (sr1 - sr2) / np.sqrt(v)
    return z, 2 * (1 - stats.norm.cdf(abs(z))), np.sqrt(v)


def var_ratio_boot(r1, r2, block=6, B=5000, seed=SEED):
    """Raportul varianțelor out-of-sample var(r1)/var(r2), cu interval bootstrap circular pe blocuri."""
    rng = np.random.default_rng(seed)
    r1, r2 = np.asarray(r1, float), np.asarray(r2, float)
    T = len(r1)
    nb = int(np.ceil(T / block))
    e1, e2 = np.r_[r1, r1[:block]], np.r_[r2, r2[:block]]
    out = np.empty(B)
    for b in range(B):
        st = rng.integers(0, T, nb)
        idx = (st[:, None] + np.arange(block)).ravel()[:T]
        out[b] = e1[idx].var() / e2[idx].var()
    return r1.var() / r2.var(), np.percentile(out, [2.5, 97.5]), np.mean(out >= 1)


# =============================================================================
# PARTEA A
# =============================================================================
def part_a():
    R = {}
    # A1 [Rezolvat] GMV cu doua active: SPY si TLT
    Rm, mu, sd, rho = g.two_asset_stats()
    w = g.gmv_two(sd['SPY'], sd['TLT'], rho)
    v = np.sqrt(w ** 2 * sd['SPY'] ** 2 + (1 - w) ** 2 * sd['TLT'] ** 2 + 2 * w * (1 - w) * rho * sd['SPY'] * sd['TLT'])
    Sig2 = np.array([[sd['SPY'] ** 2, rho * sd['SPY'] * sd['TLT']], [rho * sd['SPY'] * sd['TLT'], sd['TLT'] ** 2]])
    A_ = float(np.ones(2) @ np.linalg.solve(Sig2, np.ones(2)))
    R['A1'] = dict(s1=sd['SPY'], s2=sd['TLT'], rho=rho, m1=mu['SPY'], m2=mu['TLT'], w=w, vol=v,
                   mean=w * mu['SPY'] + (1 - w) * mu['TLT'], T=len(Rm), A=A_, vol_from_A=float(1 / np.sqrt(A_)),
                   Sigma=Sig2.tolist(), w_matrix=(np.linalg.solve(Sig2, np.ones(2)) / A_).tolist())
    # A2 [Propus] GMV cu doua active: SPY si GLD (lunar, zile comune)
    r, rex, rf = g.us_monthly(['SPY', 'GLD'])
    s1, s2 = r['SPY'].std() * np.sqrt(12), r['GLD'].std() * np.sqrt(12)
    rh = r.corr().iloc[0, 1]
    w2 = g.gmv_two(s1, s2, rh)
    v2 = np.sqrt(w2 ** 2 * s1 ** 2 + (1 - w2) ** 2 * s2 ** 2 + 2 * w2 * (1 - w2) * rh * s1 * s2)
    R['A2'] = dict(s1=s1, s2=s2, rho=rh, w=w2, vol=v2, start=str(r.index[0].date()), T=len(r),
                   vol_if_rho1=abs(w2 * s1 + (1 - w2) * s2))
    # A3 [Rezolvat] ERC cu doua active = inversul volatilitatii (SPY, IEF)
    r, rex, rf = g.us_monthly(['SPY', 'IEF'])
    S = r.cov().values * 12
    s = np.sqrt(np.diag(S))
    w_iv = (1 / s) / (1 / s).sum()
    R['A3'] = dict(s1=s[0], s2=s[1], rho=r.corr().iloc[0, 1], w_spy=w_iv[0], w_erc_numeric=g.w_erc(S)[0],
                   rc=g.risk_contrib(w_iv, S).tolist(), T=len(r), start=str(r.index[0].date()))
    # A4 [Propus] contributiile la risc ale portofoliului 60/40
    w64 = np.array([0.6, 0.4])
    R['A4'] = dict(rc=g.risk_contrib(w64, S).tolist(), vol=float(np.sqrt(w64 @ S @ w64)),
                   vol_erc=float(np.sqrt(w_iv @ S @ w_iv)), cov=S[0, 1])
    # A5 [Rezolvat] Black-Litterman cu un activ: medie ponderata cu precizia
    pi, q, tau, sig = 0.05, 0.08, 0.05, 0.16
    om = 0.02 ** 2
    prec_p, prec_v = 1 / (tau * sig ** 2), 1 / om
    R['A5'] = dict(pi=pi, q=q, tau=tau, sigma=sig, omega=om, prior_var=tau * sig ** 2,
                   weight_view=prec_v / (prec_p + prec_v),
                   mu_bl=(prec_p * pi + prec_v * q) / (prec_p + prec_v),
                   post_sd=np.sqrt(1 / (prec_p + prec_v)))
    # A6 [Propus] opinia XLK - XLU din curs: Omega = tau P Sigma P' => media simpla
    r, rex, rf = g.us_monthly(SECTORS, start='2016-08-01')
    Sig = rex.cov().values * 12
    n = len(SECTORS)
    P = np.zeros((1, n))
    P[0, SECTORS.index('XLK')], P[0, SECTORS.index('XLU')] = 1, -1
    pi_v, mu_bl, w_bl = g.black_litterman(Sig, g.w_ew(n), P, np.array([0.03]))
    pv = (P @ (2.5 * Sig @ g.w_ew(n))).item()
    R['A6'] = dict(prior_view=pv, q=0.03, post_view=(P @ mu_bl).item(), simple_average=(pv + 0.03) / 2,
                   view_var=(P @ Sig @ P.T).item(), w_xlk=w_bl[SECTORS.index('XLK')], w_xlu=w_bl[SECTORS.index('XLU')])
    return R


def part_a_tests(bts):
    """A7 [Rezolvat], A8 [Propus]: testul i.i.d. al diferentei de Sharpe pe sectoare."""
    ret = bts['Sectors'][0]
    T = len(ret)
    out = {}
    for key, s in [('A7', 'GMV'), ('A8', 'ERC')]:
        sr1 = ret[s].mean() / ret[s].std()
        sr2 = ret['1/N'].mean() / ret['1/N'].std()
        rho = ret[[s, '1/N']].corr().iloc[0, 1]
        z, p, se = sr_diff_iid(sr1, sr2, rho, T)
        d, se_h, p_h = g.sr_diff_hac(ret[s], ret['1/N'])
        out[key] = dict(strategy=s, T=T, sr1=sr1, sr2=sr2, rho=rho, se=se, z=z, p=p,
                        sr1_ann=sr1 * np.sqrt(12), sr2_ann=sr2 * np.sqrt(12), p_hac=p_h)
    return out


# =============================================================================
# PARTEA B
# =============================================================================
def b_backtest_stats(bts, n_jobs=1):
    R = {}
    tab = g.summary(*bts['Sectors'][:2])
    ret, to, W = bts['Sectors']
    tests = {}
    res = g.run_tests({s: (ret[s], ret['1/N']) for s in ['MV', 'MV-LO', 'GMV']}, n_jobs)
    for s in ['MV', 'MV-LO', 'GMV']:
        r = res[s][0]
        tests[s] = dict(diff=r['diff'], se=r['se_hac'], p_hac=r['p_hac'], ci=r['ci_boot'], p_boot=r['p_boot'],
                        block=r['block'])
    R['B1'] = dict(table=tab.loc[['1/N', 'MV', 'MV-LO', 'GMV']].round(4).to_dict(orient='index'), tests=tests,
                   T=len(ret), start=f'{ret.index[0]:%Y-%m}', end=f'{ret.index[-1]:%Y-%m}')
    # B2 [Rezolvat] shrinkage pe sectoare: volatilitatea out-of-sample a GMV
    vr, ci, pgt = var_ratio_boot(ret['GMV-LW'], ret['GMV'])
    R['B2'] = dict(vol_gmv=ret['GMV'].std() * np.sqrt(12), vol_lw=ret['GMV-LW'].std() * np.sqrt(12),
                   vol_ew=ret['1/N'].std() * np.sqrt(12), var_ratio=vr, ci=ci.tolist(), share_boot_ge1=pgt,
                   to_gmv=to['GMV'].mean(), to_lw=to['GMV-LW'].mean())
    # B3 [Rezolvat] ERC si HRP pe sectoare
    X = g.us_monthly(SECTORS)[1].values[-g.WINDOW:]
    S = np.cov(X.T)
    w_e, w_h = g.w_erc(S), g.w_hrp(S)
    rc_ew = g.risk_contrib(g.w_ew(9), S)
    tests = {}
    for s in ['ERC', 'HRP']:
        d, se, p = g.sr_diff_hac(ret[s], ret['1/N'])
        tests[s] = dict(diff=d, p_hac=p, corr_with_ew=ret[[s, '1/N']].corr().iloc[0, 1])
    R['B3'] = dict(w_erc=dict(zip(SECTORS, w_e)), w_hrp=dict(zip(SECTORS, w_h)), rc_ew=dict(zip(SECTORS, rc_ew)),
                   rc_hrp=dict(zip(SECTORS, g.risk_contrib(w_h, S))), tests=tests,
                   sharpe=dict(ERC=g.sharpe(ret['ERC']), HRP=g.sharpe(ret['HRP']), EW=g.sharpe(ret['1/N'])),
                   turnover=dict(ERC=to['ERC'].mean(), HRP=to['HRP'].mean(), EW=to['1/N'].mean()))
    # B4 [Propus] shrinkage pe universul combinat (16 ETF-uri)
    retc, toc, Wc = bts['Combined']
    vr, ci, pgt = var_ratio_boot(retc['GMV-LW'], retc['GMV'])
    Xc = g.us_monthly(g.COMBINED)[1].values
    deltas = [g.lw_cc(Xc[t - g.WINDOW:t])[1] for t in range(g.WINDOW, len(Xc) + 1)]
    R['B4'] = dict(vol_gmv=retc['GMV'].std() * np.sqrt(12), vol_lw=retc['GMV-LW'].std() * np.sqrt(12),
                   var_ratio=vr, ci=ci.tolist(), to_gmv=toc['GMV'].mean(), to_lw=toc['GMV-LW'].mean(),
                   delta_mean=float(np.mean(deltas)), delta_last=float(deltas[-1]),
                   sr_gmv=g.sharpe(retc['GMV']), sr_lw=g.sharpe(retc['GMV-LW']),
                   cond_sample=float(np.linalg.cond(np.cov(Xc[-g.WINDOW:].T))),
                   cond_lw=float(np.linalg.cond(g.lw_cc(Xc[-g.WINDOW:])[0])))
    # B6 [Propus] HRP vs GMV pe universul combinat
    d, se, p = g.sr_diff_hac(retc['HRP'], retc['GMV'])
    rb = g.run_tests({'x': (retc['HRP'], retc['GMV'])})['x'][0]
    ci, pb = rb['ci_boot'], rb['p_boot']
    R['B6'] = dict(sr_hrp=g.sharpe(retc['HRP']), sr_gmv=g.sharpe(retc['GMV']), to_hrp=toc['HRP'].mean(),
                   to_gmv=toc['GMV'].mean(), diff=d, se=se, p_hac=p, ci=ci, p_boot=pb, block=rb['block'],
                   vol_hrp=retc['HRP'].std() * np.sqrt(12), vol_gmv=retc['GMV'].std() * np.sqrt(12),
                   net50_hrp=g.sharpe(retc['HRP'] - 0.005 * toc['HRP'].fillna(0)),
                   net50_gmv=g.sharpe(retc['GMV'] - 0.005 * toc['GMV'].fillna(0)))
    # B8 [Propus] costul de echilibru MV-LO vs 1/N pe universul combinat
    c = np.linspace(0, 200, 2001)
    gap = [g.sharpe(retc['MV-LO'] - cc / 1e4 * toc['MV-LO'].fillna(0))
           - g.sharpe(retc['1/N'] - cc / 1e4 * toc['1/N'].fillna(0)) for cc in c]
    be = float(c[np.argmax(np.array(gap) < 0)])
    d, se, p = g.sr_diff_hac(retc['MV-LO'], retc['1/N'])
    R['B8'] = dict(breakeven_bp=be, to_mvlo=toc['MV-LO'].mean(), to_ew=toc['1/N'].mean(),
                   sr_mvlo=g.sharpe(retc['MV-LO']), sr_ew=g.sharpe(retc['1/N']), p_hac=p, diff=d)
    return R


def b5_btc():
    """B5 [Propus] ERC pe multi-active, cu si fara Bitcoin (zile comune, apoi luni)."""
    syms = [s + '.US' for s in MULTI] + ['BTC-USD.CC']
    p = prices(syms).resample('ME').last()
    r = p.pct_change().dropna().loc[:g.US_END]
    r.columns = MULTI + ['BTC']
    rf = french_rf().reindex(r.index)
    rex = r.sub(rf, axis=0)
    ret_b, to_b, W_b = g.backtest(r, rex, strategies=['1/N', 'ERC', 'HRP'])
    ret_n, to_n, W_n = g.backtest(r[MULTI], rex[MULTI], strategies=['1/N', 'ERC', 'HRP'])
    S = rex.cov().values * 12
    rc_ew = g.risk_contrib(g.w_ew(len(MULTI) + 1), S)
    out = dict(start=f'{r.index[0]:%Y-%m}', oos_start=f'{ret_b.index[0]:%Y-%m}', end=f'{ret_b.index[-1]:%Y-%m}',
               T=len(ret_b), btc_vol=float(np.sqrt(S[-1, -1])), rc_btc_in_ew=float(rc_ew[-1]),
               w_btc_erc_mean=float(W_b['ERC']['BTC'].mean()), w_btc_erc_last=float(W_b['ERC']['BTC'].iloc[-1]),
               w_btc_hrp_mean=float(W_b['HRP']['BTC'].mean()))
    for s in ['1/N', 'ERC', 'HRP']:
        d, se, pv = g.sr_diff_hac(ret_b[s], ret_n[s])
        out[s] = dict(sr_with=g.sharpe(ret_b[s]), sr_without=g.sharpe(ret_n[s]), diff=d, p_hac=pv,
                      vol_with=ret_b[s].std() * np.sqrt(12), vol_without=ret_n[s].std() * np.sqrt(12),
                      mdd_with=g.max_drawdown(ret_b[s] + ret_b.attrs['rf']),
                      mdd_without=g.max_drawdown(ret_n[s] + ret_n.attrs['rf']))
    return out


def b7_bl_multi():
    """B7 [Propus] Black-Litterman pe multi-active: opinia GLD - TLT = +4% pe an."""
    r, rex, rf = g.us_monthly(MULTI, start='2016-08-01')
    Sig = rex.cov().values * 12
    n = len(MULTI)
    P = np.zeros((1, n))
    P[0, MULTI.index('GLD')], P[0, MULTI.index('TLT')] = 1, -1
    pi, mu_bl, w_bl = g.black_litterman(Sig, g.w_ew(n), P, np.array([0.04]))
    return dict(pi=dict(zip(MULTI, pi)), mu_bl=dict(zip(MULTI, mu_bl)), w_bl=dict(zip(MULTI, w_bl)),
                prior_view=(P @ pi).item(), post_view=(P @ mu_bl).item(),
                sample_view=float(rex['GLD'].mean() * 12 - rex['TLT'].mean() * 12), T=len(rex),
                view_var=(P @ Sig @ P.T).item(), corr_gld_tlt=float(rex[['GLD', 'TLT']].corr().iloc[0, 1]))


def master_level(bts):
    """A9, B2(d), B4(e), B9: exercitiile de nivel master."""
    out = {}
    # A9 [Propus] deplasarea lui theta_hat^2 (Kan & Zhou 2007), N = 9, T = 60, theta = Sharpe tangent din curs
    R_s, Rex_s, _ = g.us_monthly(SECTORS)
    mu, S = Rex_s.mean().values, Rex_s.cov().values
    wt = g.w_tan(mu, S)
    theta = float((wt @ mu) / np.sqrt(wt @ S @ wt) * np.sqrt(12))
    out['A9'] = dict(theta_ann=theta, **g.kz_bias(theta, 9, 60))
    # B2(d) [Rezolvat] Marchenko-Pastur pe fereastra de 60 de luni a sectoarelor
    X = Rex_s.values[-g.WINDOW:]
    ev = np.sort(np.linalg.eigvalsh(np.corrcoef(X.T)))[::-1]
    lo, hi = g.mp_bounds(9 / g.WINDOW)
    out['B2d'] = dict(ev=ev.tolist(), lo=lo, hi=hi, n_above=int((ev > hi).sum()), n_below=int((ev < lo).sum()))
    # B4(e) [Propus] shrinkage neliniar (Ledoit & Wolf 2020) pe universul combinat
    Rc, Rexc, _ = g.us_monthly(g.COMBINED)
    retn, ton, _ = g.backtest(Rc, Rexc, strategies=['GMV', 'GMV-LW', 'GMV-NL'])
    vr, ci, pgt = var_ratio_boot(retn['GMV-NL'], retn['GMV'])
    vr2, ci2, pgt2 = var_ratio_boot(retn['GMV-NL'], retn['GMV-LW'])
    out['B4e'] = dict(vol={s: float(retn[s].std() * np.sqrt(12)) for s in retn},
                      to={s: float(ton[s].mean()) for s in retn}, sr={s: g.sharpe(retn[s]) for s in retn},
                      vr_nl_gmv=vr, ci_nl_gmv=ci.tolist(), vr_nl_lw=vr2, ci_nl_lw=ci2.tolist())
    # B9 [Propus] testul Britten-Jones al ipotezei 'tangent = 1/N', esantion complet si doua jumatati
    h = len(Rex_s) // 2
    out['B9'] = {k: {q: v for q, v in g.britten_jones(x).items() if q in ('T', 'F', 'pF', 'wald_hac', 'p_wald_hac', 't', 't_hac', 'w')}
                 | dict(start=f'{x.index[0]:%Y-%m}', end=f'{x.index[-1]:%Y-%m}')
                 for k, x in [('full', Rex_s), ('first', Rex_s.iloc[:h]), ('second', Rex_s.iloc[h:])]}
    return out


# =============================================================================
# PARTEA C: blue chips BVB, cu si fara active externe (in RON)
# =============================================================================
FOREIGN = ['SPY', 'EFA', 'IEF', 'GLD']


def part_c_data():
    cols = [s + '.RO' for s in BVB] + ['BETTR.INDX'] + [s + '.US' for s in FOREIGN]
    p = prices(cols)
    fx = bnr_rate('USD', 2014, 2026)
    p = p.join(fx, how='inner')
    for s in FOREIGN:
        p[s + '.US'] = p[s + '.US'] * p['USDRON']
    p = p.drop(columns='USDRON')
    lr = g.log_returns(p)
    lr = lr.mask(lr.abs() > g.MAX_ABS_RET, 0.0)
    m = (np.exp(lr.resample('ME').sum()) - 1).loc[:g.BVB_END].iloc[1:]
    m.columns = BVB + ['BET-TR'] + FOREIGN
    return m


def part_c():
    m = part_c_data()
    strats = ['1/N', 'GMV-LW', 'ERC', 'HRP']
    ret_l, to_l, W_l = g.backtest(m[BVB], m[BVB], window=36, strategies=strats)
    A = BVB + FOREIGN
    ret_g, to_g, W_g = g.backtest(m[A], m[A], window=36, strategies=strats)
    bench = m.loc[ret_g.index, 'BET-TR']
    out = dict(start=f'{m.index[0]:%Y-%m}', oos_start=f'{ret_g.index[0]:%Y-%m}', end=f'{ret_g.index[-1]:%Y-%m}',
               T=len(ret_g), bet_tr=dict(sharpe=g.sharpe(bench), vol=bench.std() * np.sqrt(12),
                                         mean=bench.mean() * 12, mdd=g.max_drawdown(bench)),
               corr_foreign_bet=m[FOREIGN].corrwith(m['BET-TR']).to_dict())
    for s in strats:
        d1, se1, p1 = g.sr_diff_hac(ret_g[s], bench)
        d2, se2, p2 = g.sr_diff_hac(ret_g[s], ret_l[s])
        out[s] = dict(sr_local=g.sharpe(ret_l[s]), sr_global=g.sharpe(ret_g[s]),
                      vol_local=ret_l[s].std() * np.sqrt(12), vol_global=ret_g[s].std() * np.sqrt(12),
                      mdd_local=g.max_drawdown(ret_l[s]), mdd_global=g.max_drawdown(ret_g[s]),
                      diff_vs_bettr=d1, p_vs_bettr=p1, diff_vs_local=d2, p_vs_local=p2,
                      w_foreign_mean=float(W_g[s][FOREIGN].sum(1).mean()))
    # o singura familie de 8 teste (4 reguli x 2 repere), ajustarea Holm
    adj = g.holm({f'{s}|{k}': out[s][f'p_vs_{k}'] for s in strats for k in ('bettr', 'local')})
    for s in strats:
        out[s]['holm_vs_bettr'], out[s]['holm_vs_local'] = adj[f'{s}|bettr'], adj[f'{s}|local']
    fig_part_c(ret_l, ret_g, bench)
    return out


def fig_part_c(ret_l, ret_g, bench):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for s, c in [('1/N', g.EWcol), ('ERC', g.Forest), ('GMV-LW', g.MainBlue)]:
        ax.plot(ret_l.index, np.cumprod(1 + ret_l[s]), color=c, ls='--', lw=1.0,
                label=f'{s}, BVB only (SR {g.sharpe(ret_l[s]):.2f})')
        ax.plot(ret_g.index, np.cumprod(1 + ret_g[s]), color=c, lw=1.5,
                label=f'{s}, BVB + foreign (SR {g.sharpe(ret_g[s]):.2f})')
    ax.plot(bench.index, np.cumprod(1 + bench), color='black', lw=1.5, label=f'BET-TR (SR {g.sharpe(bench):.2f})')
    ax.set_ylabel('Growth of 1 RON')
    ax.set_title(f'Eight BVB blue chips with and without SPY, EFA, IEF, GLD in RON, '
                 f'{ret_g.index[0]:%b %Y} - {ret_g.index[-1]:%b %Y}', fontsize=9, loc='left')
    g.legend_outside_bottom(ax, ncol=3, y=-0.1)
    plt.tight_layout()
    g.save_fig('ch4_sem_bvb_global')


if __name__ == '__main__':
    R = {'A': part_a()}
    bts = g.run_backtests()
    R['A'].update(part_a_tests(bts))
    R['B'] = b_backtest_stats(bts, n_jobs=3)
    R['M'] = master_level(bts)
    R['B']['B5'] = b5_btc()
    R['B']['B7'] = b7_bl_multi()
    R['C'] = part_c()
    with open(os.path.join(HERE, 'sem4_results.json'), 'w') as f:
        json.dump(g.to_py(R), f, indent=1, default=str)
    print(json.dumps(g.to_py(R), indent=1, default=str))

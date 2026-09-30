"""
seminar4.py -- computations for Seminar 4 (MFM): portfolio optimisation
========================================================================
Part A (numerical checks of the derivations), Part B (real data), Part C (model solutions).
All results are written to sem4_results.json (used by both versions of the seminar).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
from scipy.cluster.hierarchy import leaves_list, dendrogram
from scipy.spatial.distance import pdist
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import prices, french_rf, bnr_rate, SECTORS, MULTI, BVB
import generate_all_charts as g

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42


def sr_diff_iid(sr1, sr2, rho, T):
    """Sharpe ratio difference under i.i.d. Normal returns (formula reported by Ledoit-Wolf 2008).

    sr1, sr2: monthly Sharpe ratios; rho: correlation of the returns; returns (z, p, se).
    """
    v = (2 - 2 * rho + 0.5 * (sr1 ** 2 + sr2 ** 2 - 2 * sr1 * sr2 * rho ** 2)) / T
    z = (sr1 - sr2) / np.sqrt(v)
    return z, 2 * (1 - stats.norm.cdf(abs(z))), np.sqrt(v)


def var_ratio_boot(r1, r2, block=6, B=5000, seed=SEED, return_draws=False):
    """Out-of-sample variance ratio var(r1)/var(r2), with a circular block bootstrap interval.
    Both series use the SAME indices (paired months), so their correlation is preserved."""
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
    if return_draws:
        return r1.var() / r2.var(), np.percentile(out, [2.5, 97.5]), np.mean(out >= 1), out
    return r1.var() / r2.var(), np.percentile(out, [2.5, 97.5]), np.mean(out >= 1)


# =============================================================================
# PART A
# =============================================================================
def part_a():
    R = {}
    # A1 [Solved] two-asset GMV: SPY and TLT
    Rm, mu, sd, rho = g.two_asset_stats()
    w = g.gmv_two(sd['SPY'], sd['TLT'], rho)
    v = np.sqrt(w ** 2 * sd['SPY'] ** 2 + (1 - w) ** 2 * sd['TLT'] ** 2 + 2 * w * (1 - w) * rho * sd['SPY'] * sd['TLT'])
    Sig2 = np.array([[sd['SPY'] ** 2, rho * sd['SPY'] * sd['TLT']], [rho * sd['SPY'] * sd['TLT'], sd['TLT'] ** 2]])
    A_ = float(np.ones(2) @ np.linalg.solve(Sig2, np.ones(2)))
    R['A1'] = dict(s1=sd['SPY'], s2=sd['TLT'], rho=rho, m1=mu['SPY'], m2=mu['TLT'], w=w, vol=v,
                   mean=w * mu['SPY'] + (1 - w) * mu['TLT'], T=len(Rm), A=A_, vol_from_A=float(1 / np.sqrt(A_)),
                   Sigma=Sig2.tolist(), w_matrix=(np.linalg.solve(Sig2, np.ones(2)) / A_).tolist())
    # A2 [Proposed] two-asset GMV: SPY and GLD (monthly, common days)
    r, rex, rf = g.us_monthly(['SPY', 'GLD'])
    s1, s2 = r['SPY'].std() * np.sqrt(12), r['GLD'].std() * np.sqrt(12)
    rh = r.corr().iloc[0, 1]
    w2 = g.gmv_two(s1, s2, rh)
    v2 = np.sqrt(w2 ** 2 * s1 ** 2 + (1 - w2) ** 2 * s2 ** 2 + 2 * w2 * (1 - w2) * rh * s1 * s2)
    R['A2'] = dict(s1=s1, s2=s2, rho=rh, w=w2, vol=v2, start=str(r.index[0].date()), T=len(r),
                   vol_if_rho1=abs(w2 * s1 + (1 - w2) * s2))
    # A3 [Solved] two-asset ERC = inverse volatility (SPY, IEF)
    r, rex, rf = g.us_monthly(['SPY', 'IEF'])
    S = r.cov().values * 12
    s = np.sqrt(np.diag(S))
    w_iv = (1 / s) / (1 / s).sum()
    R['A3'] = dict(s1=s[0], s2=s[1], rho=r.corr().iloc[0, 1], w_spy=w_iv[0], w_erc_numeric=g.w_erc(S)[0],
                   rc=g.risk_contrib(w_iv, S).tolist(), T=len(r), start=str(r.index[0].date()))
    # A4 [Proposed] risk contributions of the 60/40 portfolio
    w64 = np.array([0.6, 0.4])
    R['A4'] = dict(rc=g.risk_contrib(w64, S).tolist(), vol=float(np.sqrt(w64 @ S @ w64)),
                   vol_erc=float(np.sqrt(w_iv @ S @ w_iv)), cov=S[0, 1])
    # A5 [Solved] Black-Litterman with one asset: precision-weighted mean
    pi, q, tau, sig = 0.05, 0.08, 0.05, 0.16
    om = 0.02 ** 2
    prec_p, prec_v = 1 / (tau * sig ** 2), 1 / om
    R['A5'] = dict(pi=pi, q=q, tau=tau, sigma=sig, omega=om, prior_var=tau * sig ** 2,
                   weight_view=prec_v / (prec_p + prec_v),
                   mu_bl=(prec_p * pi + prec_v * q) / (prec_p + prec_v),
                   post_sd=np.sqrt(1 / (prec_p + prec_v)))
    # A6 [Proposed] the lecture view XLK - XLU: Omega = tau P Sigma P' => simple average
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
    """A7 [Solved], A8 [Proposed]: i.i.d. test of the Sharpe ratio difference on sectors."""
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
# PART B
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
    # B2 [Solved] shrinkage on sectors: out-of-sample volatility of GMV
    vr, ci, pgt = var_ratio_boot(ret['GMV-LW'], ret['GMV'])
    R['B2'] = dict(vol_gmv=ret['GMV'].std() * np.sqrt(12), vol_lw=ret['GMV-LW'].std() * np.sqrt(12),
                   vol_ew=ret['1/N'].std() * np.sqrt(12), var_ratio=vr, ci=ci.tolist(), share_boot_ge1=pgt,
                   to_gmv=to['GMV'].mean(), to_lw=to['GMV-LW'].mean())
    # B3 [Solved] ERC and HRP on sectors
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
    # B4 [Proposed] shrinkage on the combined universe (16 ETFs)
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
    # B6 [Proposed] HRP vs GMV on the combined universe
    d, se, p = g.sr_diff_hac(retc['HRP'], retc['GMV'])
    rb = g.run_tests({'x': (retc['HRP'], retc['GMV'])})['x'][0]
    ci, pb = rb['ci_boot'], rb['p_boot']
    R['B6'] = dict(sr_hrp=g.sharpe(retc['HRP']), sr_gmv=g.sharpe(retc['GMV']), to_hrp=toc['HRP'].mean(),
                   to_gmv=toc['GMV'].mean(), diff=d, se=se, p_hac=p, ci=ci, p_boot=pb, block=rb['block'],
                   vol_hrp=retc['HRP'].std() * np.sqrt(12), vol_gmv=retc['GMV'].std() * np.sqrt(12),
                   net50_hrp=g.sharpe(retc['HRP'] - 0.005 * toc['HRP'].fillna(0)),
                   net50_gmv=g.sharpe(retc['GMV'] - 0.005 * toc['GMV'].fillna(0)))
    # B8 [Proposed] break-even cost of MV-LO vs 1/N on the combined universe
    c = np.linspace(0, 200, 2001)
    gap = [g.sharpe(retc['MV-LO'] - cc / 1e4 * toc['MV-LO'].fillna(0))
           - g.sharpe(retc['1/N'] - cc / 1e4 * toc['1/N'].fillna(0)) for cc in c]
    be = float(c[np.argmax(np.array(gap) < 0)])
    d, se, p = g.sr_diff_hac(retc['MV-LO'], retc['1/N'])
    R['B8'] = dict(breakeven_bp=be, to_mvlo=toc['MV-LO'].mean(), to_ew=toc['1/N'].mean(),
                   sr_mvlo=g.sharpe(retc['MV-LO']), sr_ew=g.sharpe(retc['1/N']), p_hac=p, diff=d)
    return R


def b5_btc():
    """B5 [Proposed] ERC on the multi-asset set, with and without Bitcoin (common days, then months)."""
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
    """B7 [Proposed] Black-Litterman on the multi-asset set: the view GLD - TLT = +4% a year."""
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
    """A9, B2 Extended, B4 task 3, B9: the extension-pack exercises."""
    out = {}
    # A9 [Proposed] bias of theta_hat^2 (Kan & Zhou 2007), N = 9, T = 60, theta = tangency Sharpe of the lecture
    R_s, Rex_s, _ = g.us_monthly(SECTORS)
    mu, S = Rex_s.mean().values, Rex_s.cov().values
    wt = g.w_tan(mu, S)
    theta = float((wt @ mu) / np.sqrt(wt @ S @ wt) * np.sqrt(12))
    out['A9'] = dict(theta_ann=theta, **g.kz_bias(theta, 9, 60))
    # B2 Extended [Solved] Marchenko-Pastur on the 60-month sector window
    X = Rex_s.values[-g.WINDOW:]
    ev = np.sort(np.linalg.eigvalsh(np.corrcoef(X.T)))[::-1]
    lo, hi = g.mp_bounds(9 / g.WINDOW)
    out['B2d'] = dict(ev=ev.tolist(), lo=lo, hi=hi, n_above=int((ev > hi).sum()), n_below=int((ev < lo).sum()))
    # B4 task 3 [Proposed] nonlinear shrinkage (Ledoit & Wolf 2020) on the combined universe
    Rc, Rexc, _ = g.us_monthly(g.COMBINED)
    retn, ton, _ = g.backtest(Rc, Rexc, strategies=['GMV', 'GMV-LW', 'GMV-NL'])
    vr, ci, pgt = var_ratio_boot(retn['GMV-NL'], retn['GMV'])
    vr2, ci2, pgt2 = var_ratio_boot(retn['GMV-NL'], retn['GMV-LW'])
    out['B4e'] = dict(vol={s: float(retn[s].std() * np.sqrt(12)) for s in retn},
                      to={s: float(ton[s].mean()) for s in retn}, sr={s: g.sharpe(retn[s]) for s in retn},
                      vr_nl_gmv=vr, ci_nl_gmv=ci.tolist(), vr_nl_lw=vr2, ci_nl_lw=ci2.tolist())
    # B9 [Proposed] Britten-Jones test of 'tangency = 1/N', full sample and two halves
    h = len(Rex_s) // 2
    out['B9'] = {k: {q: v for q, v in g.britten_jones(x).items() if q in ('T', 'F', 'pF', 'wald_hac', 'p_wald_hac', 't', 't_hac', 'w')}
                 | dict(start=f'{x.index[0]:%Y-%m}', end=f'{x.index[-1]:%Y-%m}')
                 for k, x in [('full', Rex_s), ('first', Rex_s.iloc[:h]), ('second', Rex_s.iloc[h:])]}
    return out


# =============================================================================
# PART C: BVB blue chips, with and without foreign assets (in RON)
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
    # one family of 8 tests (4 rules x 2 benchmarks), Holm adjustment
    adj = g.holm({f'{s}|{k}': out[s][f'p_vs_{k}'] for s in strats for k in ('bettr', 'local')})
    for s in strats:
        out[s]['holm_vs_bettr'], out[s]['holm_vs_local'] = adj[f'{s}|bettr'], adj[f'{s}|local']
    fig_part_c(ret_l, ret_g, bench)
    return out


def fig_part_c(ret_l, ret_g, bench):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for s, c in [('1/N', g.EWcol), ('ERC', g.Forest), ('GMV-LW', g.MainBlue)]:
        ax.plot(ret_l.index, np.cumprod(1 + ret_l[s]), color=c, ls='--', lw=1.0,
                label=f'{s}, BVB only (Sharpe {g.sharpe(ret_l[s]):.2f})')
        ax.plot(ret_g.index, np.cumprod(1 + ret_g[s]), color=c, lw=1.5,
                label=f'{s}, BVB + foreign (Sharpe {g.sharpe(ret_g[s]):.2f})')
    ax.plot(bench.index, np.cumprod(1 + bench), color='black', lw=1.5, label=f'BET-TR (Sharpe {g.sharpe(bench):.2f})')
    ax.set_ylabel('Growth of 1 RON')
    ax.set_title(f'Eight BVB blue chips with and without SPY, EFA, IEF, GLD in RON, '
                 f'{ret_g.index[0]:%b %Y} - {ret_g.index[-1]:%b %Y}', fontsize=9, loc='left')
    g.legend_outside_bottom(ax, ncol=3, y=-0.1)
    plt.tight_layout()
    g.save_fig('ch4_sem_bvb_global')


# =============================================================================
# SEMINAR CHARTS: charts/ch4_sem_*.pdf|png (transparent background, English labels, legend at the bottom)
# Run:  python seminar4.py --charts   (uses sem4_results.json for the calibrated blocks)
# =============================================================================
W_IN = 5.6          # width of the seminar figures (inches), shown at ~0.5-0.85 of the slide width


def sem_style():
    plt.rcParams['font.size'] = 9
    plt.rcParams['axes.titlesize'] = 9
    plt.rcParams['axes.labelsize'] = 8.5
    plt.rcParams['legend.fontsize'] = 7.5
    plt.rcParams['xtick.labelsize'] = 7.5
    plt.rcParams['ytick.labelsize'] = 7.5


def bottom_legend(fig, ncol=3, handles=None, labels=None, fontsize=7.5):
    """Legend below the figure (outside the axes), after tight_layout."""
    plt.tight_layout()
    if handles is None:
        handles, labels, seen = [], [], set()
        for ax in fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in seen and not l.startswith('_'):
                    handles.append(h)
                    labels.append(l)
                    seen.add(l)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False,
               fontsize=fontsize)


def fmt_pct(ax, axis='y', dec=0):
    f = plt.FuncFormatter(lambda v, _: f'{v * 100:.{dec}f}%' if dec else f'{round(v * 100, 1):g}%')
    (ax.yaxis if axis == 'y' else ax.xaxis).set_major_formatter(f)


def fig_a1(A1):
    """A1: volatility of the SPY-TLT portfolio as a function of the SPY weight, and the risk-return curve."""
    s1, s2, rho, m1, m2 = A1['s1'], A1['s2'], A1['rho'], A1['m1'], A1['m2']
    w = np.linspace(-0.2, 1.2, 281)
    vol = lambda w, r: np.sqrt(w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * r * s1 * s2)
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.15, 1]})
    ax = axes[0]
    out = {}
    for r, c, lab in [(-0.5, g.Forest, 'rho = -0.50'), (0.0, g.Amber, 'rho = 0'), (rho, g.IDAred, f'rho = {rho:.2f} (actual)'),
                      (0.5, g.Purple, 'rho = +0.50')]:
        ax.plot(w, vol(w, r), color=c, lw=1.6 if r == rho else 1.0, label=lab)
        wg = g.gmv_two(s1, s2, r)
        ax.plot(wg, vol(wg, r), 'o', color=c, ms=4)
        out[f'{r:.2f}'] = dict(w=float(wg), vol=float(vol(wg, r)))
    wg = A1['w']
    ax.set_xlabel('Weight of SPY, $w$')
    ax.set_ylabel('Portfolio volatility')
    fmt_pct(ax)
    ax.set_title('Volatility against the SPY weight', loc='left')
    ax = axes[1]
    ax.plot(vol(w, rho), w * m1 + (1 - w) * m2, color=g.IDAred, lw=1.6)
    pts = [('TLT', 0.0, g.MainBlue), ('SPY', 1.0, g.Orange), ('50/50', 0.5, g.Forest), ('GMV', wg, g.IDAred)]
    for lab, x, c in pts:
        ax.plot(vol(x, rho), x * m1 + (1 - x) * m2, 'o', color=c, ms=5, label=f'{lab} ({vol(x, rho):.1%}, {x * m1 + (1 - x) * m2:.1%})')
    ax.set_xlabel('Volatility')
    ax.set_ylabel('Mean return')
    fmt_pct(ax)
    fmt_pct(ax, 'x')
    ax.set_title('Risk and return, actual correlation', loc='left')
    bottom_legend(fig, ncol=4, fontsize=7)
    g.save_fig('ch4_sem_a1_two_asset')
    out['vol_5050'] = float(vol(0.5, rho))
    out['mean_5050'] = float(0.5 * m1 + 0.5 * m2)
    return out


def fig_a3(A3):
    """A3: two-asset ERC; the weights do not depend on rho, the volatility does."""
    s1, s2, rho = A3['s1'], A3['s2'], A3['rho']
    w1 = (1 / s1) / (1 / s1 + 1 / s2)
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.2), gridspec_kw={'width_ratios': [1, 1.2]})
    ax = axes[0]
    x = np.arange(2)
    ax.bar(x - 0.18, [w1, 1 - w1], 0.34, color=g.MainBlue, label='Capital weight')
    ax.bar(x + 0.18, A3['rc'], 0.34, color=g.Orange, label='Share of variance')
    for i, (a, b) in enumerate(zip([w1, 1 - w1], A3['rc'])):
        ax.text(i - 0.18, a + 0.01, f'{a:.1%}', ha='center', va='bottom', fontsize=7, color='black')
        ax.text(i + 0.18, b + 0.01, f'{b:.0%}', ha='center', va='bottom', fontsize=7, color='black')
    ax.set_xticks(x, ['SPY', 'IEF'])
    ax.set_ylim(0, 0.85)
    fmt_pct(ax)
    ax.set_title('ERC: weights and risk shares', loc='left')
    ax = axes[1]
    r = np.linspace(-0.9, 0.9, 181)
    v = np.sqrt(w1 ** 2 * s1 ** 2 + (1 - w1) ** 2 * s2 ** 2 + 2 * w1 * (1 - w1) * r * s1 * s2)
    ax.plot(r, v, color=g.Forest, lw=1.4, label='ERC volatility')
    ax.plot(r, np.full_like(r, w1), color=g.MainBlue, lw=1.4, ls='--', label='ERC weight of SPY')
    vr = np.sqrt(w1 ** 2 * s1 ** 2 + (1 - w1) ** 2 * s2 ** 2 + 2 * w1 * (1 - w1) * rho * s1 * s2)
    ax.plot(rho, vr, 'o', color=g.IDAred, ms=5, label=f'Actual rho = {rho:.2f}: vol {vr:.2%}')
    ax.set_xlabel('Correlation rho')
    fmt_pct(ax)
    ax.set_ylim(0, 0.35)
    ax.set_title('Correlation moves the risk, not the weights', loc='left')
    bottom_legend(fig, ncol=3, fontsize=7)
    g.save_fig('ch4_sem_a3_erc')
    return dict(w1=float(w1), vol=float(vr))


def a_5050(A3, A4):
    """Worked example of the lecture: risk contributions of the 50/50 SPY-IEF portfolio."""
    S = np.array([[A3['s1'] ** 2, A4['cov']], [A4['cov'], A3['s2'] ** 2]])
    w = np.array([0.5, 0.5])
    Sw = S @ w
    v = w @ Sw
    return dict(Sw=Sw.tolist(), var=float(v), vol=float(np.sqrt(v)), shares=(w * Sw / v).tolist())


def fig_a4(A3, A4):
    """A4: 60/40 against ERC, capital weights and variance shares."""
    s1, s2 = A3['s1'], A3['s2']
    w1 = (1 / s1) / (1 / s1 + 1 / s2)
    fig, ax = plt.subplots(figsize=(W_IN * 0.8, 2.2))
    labels = ['60/40\ncapital', '60/40\nrisk', 'ERC\ncapital', 'ERC\nrisk']
    spy = [0.6, A4['rc'][0], w1, 0.5]
    ief = [0.4, A4['rc'][1], 1 - w1, 0.5]
    x = np.arange(4)
    ax.bar(x, spy, 0.55, color=g.Orange, label='SPY')
    ax.bar(x, ief, 0.55, bottom=spy, color=g.MainBlue, label='IEF')
    for i, (a, b) in enumerate(zip(spy, ief)):
        ax.text(i, a / 2, f'{a:.1%}', ha='center', va='center', fontsize=7, color='white')
        ax.text(i, a + b / 2, f'{b:.1%}', ha='center', va='center', fontsize=7, color='white')
    ax.set_xticks(x, labels)
    fmt_pct(ax)
    ax.text(0.5, 1.03, f"volatility {A4['vol']:.2%}", ha='center', fontsize=7.5, color='black')
    ax.text(2.5, 1.03, f"volatility {A4['vol_erc']:.2%}", ha='center', fontsize=7.5, color='black')
    ax.set_ylim(0, 1.12)
    ax.set_title('Who carries the risk? Capital versus variance shares', loc='left')
    bottom_legend(fig, ncol=2)
    g.save_fig('ch4_sem_a4_6040')


def fig_a5(A5):
    """A5: prior density, likelihood of the view and posterior density (one mean, one asset)."""
    x = np.linspace(-0.04, 0.16, 600)
    sd_p, sd_v, sd_q = np.sqrt(A5['prior_var']), A5['post_sd'], np.sqrt(A5['omega'])
    fig, ax = plt.subplots(figsize=(W_IN * 0.85, 2.1))
    for m, s, c, lab in [(A5['pi'], sd_p, g.MainBlue, f"Prior: mean {A5['pi']:.1%}, sd {sd_p:.2%}"),
                         (A5['q'], sd_q, g.Orange, f"View likelihood: mean {A5['q']:.1%}, sd {sd_q:.1%}"),
                         (A5['mu_bl'], sd_v, g.Forest, f"Posterior: mean {A5['mu_bl']:.2%}, sd {sd_v:.2%}")]:
        ax.plot(x, stats.norm.pdf(x, m, s), color=c, lw=1.5, label=lab)
        ax.axvline(m, color=c, lw=0.7, ls=':')
    ax.set_xticks(np.arange(-0.04, 0.161, 0.02))
    fmt_pct(ax, 'x')
    ax.set_xlabel('Expected return of the asset, $\\mu$ (uncertainty about the mean, not return volatility)')
    ax.set_ylabel('Density')
    ax.set_title('One asset, one view: precision-weighted update', loc='left')
    bottom_legend(fig, ncol=1)
    g.save_fig('ch4_sem_a5_bl')


def bl_setup(symbols, start, view, q):
    r, rex, rf = g.us_monthly(symbols, start=start)
    Sig = rex.cov().values * 12
    n = len(symbols)
    P = np.zeros((1, n))
    P[0, symbols.index(view[0])], P[0, symbols.index(view[1])] = 1, -1
    return rex, Sig, P, np.array([q])


def bl_confidence_curve(Sig, P, q, ks):
    n = Sig.shape[0]
    base = (P @ (0.05 * Sig) @ P.T).item()
    return np.array([g.black_litterman(Sig, g.w_ew(n), P, q, conf=np.array([[k * base]]))[2] for k in ks])


def fig_a6():
    """A6: Black-Litterman on sectors, view XLK - XLU = 3%: weights and sensitivity to confidence."""
    rex, Sig, P, q = bl_setup(SECTORS, '2016-08-01', ('XLK', 'XLU'), 0.03)
    n = len(SECTORS)
    pi, mu_bl, w_bl = g.black_litterman(Sig, g.w_ew(n), P, q)
    spread_var = (P @ Sig @ P.T).item()
    tilt = ((q - P @ pi).item()) / (2 * 2.5 * spread_var)
    ks = np.exp(np.linspace(np.log(0.05), np.log(20), 120))
    W = bl_confidence_curve(Sig, P, q, ks)
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.35, 1]})
    ax = axes[0]
    x = np.arange(n)
    ax.bar(x - 0.2, g.w_ew(n), 0.38, color=g.EWcol, label='Benchmark 1/N')
    ax.bar(x + 0.2, w_bl, 0.38, color=g.MainBlue, label='Black-Litterman')
    ax.set_xticks(x, SECTORS, rotation=90)
    fmt_pct(ax)
    ax.set_title('Weights before and after the view', loc='left')
    ax = axes[1]
    ax.plot(ks, W[:, SECTORS.index('XLK')], color=g.MainBlue, lw=1.4, label='XLK weight')
    ax.plot(ks, W[:, SECTORS.index('XLU')], color=g.Orange, lw=1.4, label='XLU weight')
    ax.axvline(1, color=g.Gray, lw=0.6, ls=':')
    ax.set_xscale('log')
    ax.set_xlabel(r'$\Omega / (\tau P \Sigma P^\top)$, log scale')
    fmt_pct(ax)
    ax.set_title('Lower confidence, smaller tilt', loc='left')
    bottom_legend(fig, ncol=4, fontsize=7)
    g.save_fig('ch4_sem_a6_bl_sectors')
    return dict(tilt=float(tilt), spread_var=spread_var, surprise=float((q - P @ pi).item()),
                w_xlk=float(w_bl[SECTORS.index('XLK')]), w_xlu=float(w_bl[SECTORS.index('XLU')]),
                sum_w=float(w_bl.sum()), order=SECTORS)


def fig_a7(A7):
    """A7: standard Normal distribution, 5% rejection regions and the observed statistic."""
    z = A7['z']
    x = np.linspace(-4, 4, 800)
    fig, ax = plt.subplots(figsize=(W_IN * 0.8, 2.0))
    ax.plot(x, stats.norm.pdf(x), color=g.MainBlue, lw=1.4, label='Standard Normal density under $H_0$')
    for side in (x <= -1.96, x >= 1.96):
        ax.fill_between(x[side], stats.norm.pdf(x[side]), color=g.IDAred, alpha=0.35, lw=0)
    ax.fill_between([], [], color=g.IDAred, alpha=0.35, label='Rejection region, 5% two-sided (|z| > 1.96)')
    ax.axvline(z, color=g.Forest, lw=1.5, label=f"Observed z = {z:.2f}, p = {A7['p']:.2f}")
    ax.axvline(-z, color=g.Forest, lw=0.8, ls='--')
    ax.set_xlabel('z')
    ax.set_ylabel('Density')
    ax.set_title('GMV minus 1/N, sectors, T = 271 months', loc='left')
    bottom_legend(fig, ncol=1)
    g.save_fig('ch4_sem_a7_normal')


def fig_a8(A7, A8):
    """A8: intervals of the annualised differences (i.i.d.) and the standard error as a function of the correlation."""
    T = A7['T']
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.2), gridspec_kw={'width_ratios': [1, 1.2]})
    ax = axes[0]
    res = {}
    for i, (d, lab, c) in enumerate([(A7, 'GMV - 1/N', g.Amber), (A8, 'ERC - 1/N', g.Forest)]):
        diff = (d['sr1'] - d['sr2']) * np.sqrt(12)
        se = d['se'] * np.sqrt(12)
        ax.errorbar(diff, i, xerr=1.96 * se, fmt='o', color=c, capsize=3, lw=1.3)
        ax.text(diff, i + 0.18, f'{diff:+.3f} [{diff - 1.96 * se:+.3f}, {diff + 1.96 * se:+.3f}]',
                ha='center', fontsize=7, color='black')
        res[lab] = dict(diff=float(diff), se=float(se), lo=float(diff - 1.96 * se), hi=float(diff + 1.96 * se))
    ax.axvline(0, color=g.Gray, lw=0.6)
    ax.set_yticks([0, 1], ['GMV - 1/N', 'ERC - 1/N'])
    ax.set_ylim(-0.5, 1.6)
    ax.set_xlabel('Annualised Sharpe difference, 95% interval')
    ax.set_title('Two gaps, two precisions', loc='left')
    ax = axes[1]
    r = np.linspace(0, 0.999, 400)
    for d, c, lab in [(A7, g.Amber, 'Sharpe ratios of GMV and 1/N'), (A8, g.Forest, 'Sharpe ratios of ERC and 1/N')]:
        v = (2 - 2 * r + 0.5 * (d['sr1'] ** 2 + d['sr2'] ** 2 - 2 * d['sr1'] * d['sr2'] * r ** 2)) / T
        ax.plot(r, np.sqrt(v * 12), color=c, lw=1.3, label=lab)
        ax.plot(d['rho'], d['se'] * np.sqrt(12), 'o', color=c, ms=5)
    ax.set_xlabel('Correlation of the two return series')
    ax.set_ylabel('Standard error (annualised)')
    ax.set_title(r'The standard error collapses as $\rho \to 1$', loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_a8_intervals')
    return res


def fig_a9(nsim=5000, T=60, seed=SEED):
    """A9: distribution of the estimated maximum Sharpe ratio (maximum-likelihood Sigma), N = 9, T = 60."""
    mu, S = g.sector_truth()
    N = len(mu)
    theta2 = mu @ np.linalg.solve(S, mu)
    rng = np.random.default_rng(seed)
    th = np.empty(nsim)
    for k in range(nsim):
        X = rng.multivariate_normal(mu, S, T)
        m, Sh = X.mean(0), np.cov(X.T, bias=True)
        th[k] = m @ np.linalg.solve(Sh, m)
    ann = np.sqrt(12 * th)
    e_an = np.sqrt(12 * (T * theta2 + N) / (T - N - 2))
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    ax.hist(ann, bins=60, color=g.MainBlue, alpha=0.75, density=True, label='Simulated estimated maximum Sharpe')
    lines = [(np.sqrt(12 * theta2), g.Forest, '-', f'True maximum Sharpe {np.sqrt(12 * theta2):.2f}'),
             (np.median(ann), g.Orange, '--', f'Simulated median {np.median(ann):.2f}'),
             (np.sqrt(np.mean(ann ** 2)), g.Purple, ':', f'Simulated root mean square {np.sqrt(np.mean(ann ** 2)):.2f}'),
             (e_an, g.IDAred, '-', f'Analytical root mean square {e_an:.2f}')]
    for v, c, ls, lab in lines:
        ax.axvline(v, color=c, ls=ls, lw=1.3, label=lab)
    ax.set_xlabel('Annualised estimated maximum Sharpe ratio')
    ax.set_ylabel('Density')
    ax.set_title(f'N = {N}, T = {T}, {nsim} Normal samples', loc='left')
    ax = axes[1]
    Ts = np.arange(N + 4, 601)
    ax.plot(Ts / 12, np.sqrt(12 * (Ts * theta2 + N) / (Ts - N - 2)), color=g.IDAred, lw=1.4)
    ax.axhline(np.sqrt(12 * theta2), color=g.Forest, lw=1.0)
    ax.set_xscale('log')
    ax.set_ylim(0, 3)
    ax.set_xlabel('Sample length (years, log scale)')
    ax.set_ylabel('Root mean square (annualised)')
    ax.set_title('The bias fades only slowly', loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_a9_bias')
    return dict(nsim=nsim, theta_ann=float(np.sqrt(12 * theta2)), median=float(np.median(ann)),
                rms_sim=float(np.sqrt(np.mean(ann ** 2))), rms_analytic=float(e_an),
                rms_10y=float(np.sqrt(12 * (120 * theta2 + N) / (120 - N - 2))),
                rms_27y=float(np.sqrt(12 * (331 * theta2 + N) / (331 - N - 2))))


def setup_check():
    """Setup: the sector panel (monthly returns) and its first values."""
    r, rex, rf = g.us_monthly(SECTORS)
    p = prices([s + '.US' for s in SECTORS]).resample('ME').last()
    return dict(T=len(r), first=f'{r.index[0]:%Y-%m-%d}', last=f'{r.index[-1]:%Y-%m-%d}',
                first_price_date=f'{p.index[0]:%Y-%m-%d}',
                row1={s: float(r[s].iloc[0]) for s in ['XLB', 'XLK', 'XLU']}, rf1=float(rf.iloc[0]),
                rf_last=float(rf.iloc[-1]), mean_rf_ann=float(rf.mean() * 12),
                T_multi=len(g.us_monthly(MULTI)[0]), multi_first=f'{g.us_monthly(MULTI)[0].index[0]:%Y-%m}',
                T_comb=len(g.us_monthly(g.COMBINED)[0]))


def b1_first_month(bts):
    """B1: the first out-of-sample month step by step (1/N and MV-LO): window, weights, return, drift, turnover."""
    R, Rex, rf = g.us_monthly(SECTORS)
    X = Rex.values
    t0 = g.WINDOW
    est = X[:t0]
    w_1n, w_lo = g.w_ew(9), g.weights('MV-LO', est)
    w_gmv, w_mv = g.weights('GMV', est), g.weights('MV', est)
    Rt, Xt = R.values[t0], X[t0]
    drift = lambda w: w * (1 + Rt) / (w @ (1 + Rt))
    w_1n2, w_lo2 = g.w_ew(9), g.weights('MV-LO', X[1:t0 + 1])
    ret, to, W = bts['Sectors']
    return dict(est_start=f'{Rex.index[0]:%Y-%m}', est_end=f'{Rex.index[t0 - 1]:%Y-%m}', hold=f'{Rex.index[t0]:%Y-%m}',
                hold2=f'{Rex.index[t0 + 1]:%Y-%m}', rf=float(rf.iloc[t0]),
                R=dict(zip(SECTORS, Rt.tolist())), Rex=dict(zip(SECTORS, Xt.tolist())),
                w_mvlo=dict(zip(SECTORS, w_lo.tolist())), w_mv_gross=float(np.abs(w_mv).sum()),
                w_gmv=dict(zip(SECTORS, w_gmv.tolist())),
                ret_ew=float(w_1n @ Xt), ret_mvlo=float(w_lo @ Xt), ret_gmv=float(w_gmv @ Xt), ret_mv=float(w_mv @ Xt),
                ret_ew_total=float(w_1n @ Rt),
                drift_ew=dict(zip(SECTORS, drift(w_1n).tolist())), drift_mvlo=dict(zip(SECTORS, drift(w_lo).tolist())),
                to_ew=float(np.abs(w_1n2 - drift(w_1n)).sum()), to_mvlo=float(np.abs(w_lo2 - drift(w_lo)).sum()),
                check_to_ew=float(to['1/N'].iloc[1]), check_to_mvlo=float(to['MV-LO'].iloc[1]),
                check_ret_ew=float(ret['1/N'].iloc[0]), check_ret_mvlo=float(ret['MV-LO'].iloc[0]),
                last_est=f'{Rex.index[-g.WINDOW - 1]:%Y-%m} - {Rex.index[-2]:%Y-%m}', last_hold=f'{Rex.index[-1]:%Y-%m}')


def fig_b1_timeline(info):
    """B1: estimation windows and holding months (the first two and the last)."""
    fig, ax = plt.subplots(figsize=(W_IN, 1.55))
    ts = lambda s: pd.Timestamp(s + '-01')
    rows = [(ts('1999-01'), ts('2003-12'), ts('2004-01'), 'Window 1: estimate Jan 1999 - Dec 2003, hold Jan 2004'),
            (ts('1999-02'), ts('2004-01'), ts('2004-02'), 'Window 2: estimate Feb 1999 - Jan 2004, hold Feb 2004'),
            (ts('2021-07'), ts('2026-06'), ts('2026-07'), 'Window 271: estimate Jul 2021 - Jun 2026, hold Jul 2026')]
    for i, (a, b, h, lab) in enumerate(rows):
        y = 2 - i
        ax.barh(y, (b - a).days + 30, left=a, height=0.5, color=g.MainBlue, alpha=0.85,
                label='60 estimation months' if i == 0 else None)
        ax.barh(y, 31, left=h, height=0.5, color=g.IDAred, label='Holding month (out of sample)' if i == 0 else None)
        ax.text(ts('2005-01') if i < 2 else ts('2000-01'), y, lab, va='center', fontsize=7, color='black')
    ax.set_yticks([])
    ax.set_xlim(ts('1998-06'), ts('2027-01'))
    ax.set_title('Rolling 60-month estimation, one-month holding: 271 out-of-sample months', loc='left')
    for sp in ['left']:
        ax.spines[sp].set_visible(False)
    bottom_legend(fig, ncol=2)
    g.save_fig('ch4_sem_b1_timeline')


def fig_b1_wealth(bts):
    """B1: wealth (total returns), drawdown, gross exposure and turnover of the four rules."""
    ret, to, W = bts['Sectors']
    rf = ret.attrs['rf']
    rules = ['1/N', 'MV', 'MV-LO', 'GMV']
    fig, axes = plt.subplots(2, 2, figsize=(W_IN, 3.0), sharex=True)
    info = {}
    for s in rules:
        tot = ret[s] + rf
        wealth = np.cumprod(1 + tot)
        ruin = np.flatnonzero(tot.values <= -1)
        if len(ruin):
            wealth.iloc[ruin[0]:] = np.nan
            info['mv_ruin'] = f'{ret.index[ruin[0]]:%Y-%m}'
            info['mv_ruin_ret'] = float(tot.iloc[ruin[0]])
        dd = wealth / np.maximum.accumulate(wealth.fillna(0).clip(lower=1)) - 1
        lw = 1.5 if s != 'MV' else 1.0
        axes[0, 0].plot(ret.index, wealth, color=g.SCOL[s], lw=lw, label=s)
        axes[0, 1].plot(ret.index, dd, color=g.SCOL[s], lw=lw)
        axes[1, 0].plot(ret.index, W[s].abs().sum(1), color=g.SCOL[s], lw=lw)
        axes[1, 1].plot(ret.index, to[s].rolling(12, min_periods=1).mean(), color=g.SCOL[s], lw=lw)
        info[s] = dict(final_wealth=float(wealth.dropna().iloc[-1]), median_gross=float(W[s].abs().sum(1).median()))
    axes[0, 0].set_yscale('log')
    axes[0, 0].set_title('Wealth of 1 USD (total return, log)', loc='left')
    axes[0, 1].set_title('Drawdown', loc='left')
    fmt_pct(axes[0, 1])
    axes[1, 0].set_yscale('log')
    axes[1, 0].set_title('Gross exposure sum |w| (log)', loc='left')
    axes[1, 1].set_yscale('log')
    axes[1, 1].set_title('Turnover, 12-month average (log)', loc='left')
    if 'mv_ruin' in info:
        t = pd.Timestamp(info['mv_ruin'] + '-28')
        axes[0, 0].axvline(t, color=g.IDAred, lw=0.6, ls=':')
        import matplotlib.transforms as mtrans
        axes[0, 0].text(t, 0.06, f" MV wealth ends {t:%b %Y}", fontsize=6.5, color=g.IDAred, va='bottom',
                        transform=mtrans.blended_transform_factory(axes[0, 0].transData, axes[0, 0].transAxes))
    bottom_legend(fig, ncol=4)
    g.save_fig('ch4_sem_b1_wealth')
    return info


def fig_b1_boot(bts, B1):
    """B1: studentized bootstrap for MV-LO minus 1/N (calibrated block) and the extrapolated sample length."""
    ret = bts['Sectors'][0]
    blk = B1['tests']['MV-LO']['block']
    res, tstar = g.sr_diff_boot(ret['MV-LO'], ret['1/N'], block=blk)
    d, se = B1['tests']['MV-LO']['diff'], B1['tests']['MV-LO']['se']
    Y0 = len(ret) / 12
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axes[0]
    ax.hist(tstar, bins=np.linspace(-5, 5, 61), density=True, color=g.Orange, alpha=0.8,
            label='Bootstrap studentized statistic')
    ax.axvline(res['t_obs'], color=g.IDAred, lw=1.5, label=f"Observed {res['t_obs']:+.2f}")
    ax.axvline(-res['z_star'], color='black', ls='--', lw=0.8, label=f"Critical values +/-{res['z_star']:.2f}")
    ax.axvline(res['z_star'], color='black', ls='--', lw=0.8)
    ax.set_xlabel(r'$(\Delta^* - \Delta)/s(\Delta^*)$')
    ax.set_ylabel('Density')
    ax.set_title(f"MV-LO minus 1/N, block {blk}: p = {res['p_boot']:.2f}", loc='left')
    ax = axes[1]
    Y = np.exp(np.linspace(np.log(10), np.log(1000), 200))
    ax.plot(Y, se * np.sqrt(Y0 / Y), color=g.MainBlue, lw=1.4, label='HAC standard error if it falls like 1/sqrt(years)')
    ax.axhline(d / 1.96, color=g.IDAred, lw=1.0, ls='--', label=f'Standard error needed for |z| = 1.96: {d / 1.96:.3f}')
    yreq = Y0 * (se / (d / 1.96)) ** 2
    ax.axvline(yreq, color=g.Gray, lw=0.6, ls=':')
    ax.text(yreq, se * 0.9, f' {yreq:.0f} years', fontsize=7, color='black')
    ax.set_xscale('log')
    ax.set_xlabel('Out-of-sample years (log)')
    ax.set_ylabel('Standard error (annualised)')
    ax.set_title('Extrapolation with the difference held at its estimate', loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_b1_boot')
    return dict(p_boot=res['p_boot'], ci=res['ci'], t_obs=res['t_obs'], z_star=res['z_star'], years_needed=float(yreq),
                Y0=float(Y0))


def b2_pipeline():
    """B2: from S to F, delta, Sigma_LW and the GMV weights on the last sector window."""
    R, Rex, rf = g.us_monthly(SECTORS)
    X = Rex.values[-g.WINDOW:]
    T, N = X.shape
    Y = X - X.mean(0)
    S = Y.T @ Y / T
    sd = np.sqrt(np.diag(S))
    rbar = (np.sum(S / np.outer(sd, sd)) - N) / (N * (N - 1))
    Slw, delta = g.lw_cc(X)
    w_s, w_l = g.w_gmv(np.cov(X.T)), g.w_gmv(Slw)
    return dict(start=f'{Rex.index[-g.WINDOW]:%Y-%m}', end=f'{Rex.index[-1]:%Y-%m}', rbar=float(rbar), delta=float(delta),
                cond_s=float(np.linalg.cond(S)), cond_lw=float(np.linalg.cond(Slw)),
                w_sample=dict(zip(SECTORS, w_s.tolist())), w_lw=dict(zip(SECTORS, w_l.tolist())),
                gross_sample=float(np.abs(w_s).sum()), gross_lw=float(np.abs(w_l).sum()),
                s_xlk_xlu=float(S[4, 6] / (sd[4] * sd[6])), vol_xlk=float(sd[4] * np.sqrt(12)))


def fig_b2(bts):
    """B2: bootstrap distribution of the variance ratio GMV-LW / GMV, and turnover."""
    ret, to, W = bts['Sectors']
    vr, ci, pge, draws = var_ratio_boot(ret['GMV-LW'], ret['GMV'], return_draws=True)
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.2), gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    ax.hist(draws, bins=60, color=g.MainBlue, alpha=0.75, density=True, label='Bootstrap variance ratios')
    ax.axvline(1, color='black', lw=1.0, label='Null value 1 (no change in risk)')
    ax.axvline(vr, color=g.IDAred, lw=1.4, label=f'Observed {vr:.3f}')
    for v in ci:
        ax.axvline(v, color=g.Orange, lw=1.0, ls='--')
    ax.plot([], [], color=g.Orange, ls='--', label=f'95% interval [{ci[0]:.3f}, {ci[1]:.3f}]')
    ax.set_xlabel('Var(GMV-LW) / Var(GMV), out of sample')
    ax.set_title('Paired circular block bootstrap, block 6', loc='left')
    ax = axes[1]
    for s in ['GMV', 'GMV-LW', '1/N']:
        ax.plot(to.index, to[s].rolling(12, min_periods=1).mean(), color=g.SCOL[s], lw=1.2,
                label=f'{s}: mean turnover {to[s].mean():.3f}')
    ax.set_title('Turnover, 12-month average', loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_b2_varratio')
    return dict(var_ratio=float(vr), ci=ci.tolist(), share_ge1=float(pge), T=len(ret), nblocks=int(np.ceil(len(ret) / 6)))


def fig_b2x():
    """B2 Extended: eigenvalues of the sector correlations on the last window, Marchenko-Pastur band."""
    R, Rex, rf = g.us_monthly(SECTORS)
    X = Rex.values[-g.WINDOW:]
    ev = np.sort(np.linalg.eigvalsh(np.corrcoef(X.T)))[::-1]
    N = len(SECTORS)
    lo, hi = g.mp_bounds(N / g.WINDOW)
    s2 = 1 - ev[0] / N
    lo2, hi2 = g.mp_bounds(N / g.WINDOW, s2)
    k = np.arange(1, N + 1)
    fig, ax = plt.subplots(figsize=(W_IN * 0.8, 2.1))
    ax.axhspan(lo, hi, color=g.MainBlue, alpha=0.15, label=f'Band, sigma^2 = 1: [{lo:.2f}, {hi:.2f}]')
    ax.axhspan(lo2, hi2, color=g.Orange, alpha=0.2, label=f'Band, sigma^2 = 1 - lambda1/N = {s2:.2f}: [{lo2:.2f}, {hi2:.2f}]')
    ax.plot(k, ev, 'o', color=g.IDAred, ms=5, label='Sample eigenvalues')
    for i, v in enumerate(ev):
        ax.text(k[i] + 0.12, v, f'{v:.2f}', fontsize=6.5, va='center', color='black')
    ax.set_yscale('log')
    ax.set_xticks(k)
    ax.set_xlabel('Eigenvalue rank')
    ax.set_ylabel('Eigenvalue (log)')
    ax.set_title(f'Nine sectors, {Rex.index[-g.WINDOW]:%b %Y} - {Rex.index[-1]:%b %Y}, c = {N / g.WINDOW:.2f}', loc='left')
    bottom_legend(fig, ncol=1)
    g.save_fig('ch4_sem_b2x_eigen')
    return dict(s2=float(s2), lo2=float(lo2), hi2=float(hi2), n_above2=int((ev > hi2).sum()),
                n_below2=int((ev < lo2).sum()))


def b3_worked():
    """B3: the four-asset HRP example (simulated covariance, fully transparent)."""
    vol = np.array([0.10, 0.12, 0.20, 0.25])
    C = np.array([[1, 0.8, 0.2, 0.2], [0.8, 1, 0.2, 0.2], [0.2, 0.2, 1, 0.7], [0.2, 0.2, 0.7, 1.0]])
    S = C * np.outer(vol, vol)
    D = np.sqrt((1 - C) / 2)
    from scipy.spatial.distance import squareform
    Dt = squareform(pdist(D, 'euclidean'))
    L = g.hrp_tree(S)
    order = list(leaves_list(L))

    def cvar(idx):
        s = S[np.ix_(idx, idx)]
        iv = 1 / np.diag(s)
        iv /= iv.sum()
        return float(iv @ s @ iv), iv

    a, b = order[:2], order[2:]
    va, iva = cvar(a)
    vb, ivb = cvar(b)
    alpha = 1 - va / (va + vb)
    w = g.w_hrp(S)
    iv = (1 / vol ** 2) / (1 / vol ** 2).sum()
    return dict(vol=vol.tolist(), C=C.tolist(), D=D.round(4).tolist(), Dt=Dt.round(4).tolist(), linkage=L.tolist(),
                order=order, va=va, vb=vb, iva=iva.tolist(), ivb=ivb.tolist(), alpha=float(alpha), w=w.tolist(),
                w_ivar=iv.tolist(), w_erc=g.w_erc(S).tolist(), vol_hrp=float(np.sqrt(w @ S @ w)),
                vol_ew=float(np.sqrt(np.ones(4) @ S @ np.ones(4)) / 4))


def fig_b3_worked(wk):
    names = ['A', 'B', 'C', 'D']
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.1), gridspec_kw={'width_ratios': [1, 1.3]})
    dendrogram(np.array(wk['linkage']), labels=names, ax=axes[0], color_threshold=0, above_threshold_color=g.MainBlue)
    axes[0].set_ylabel('Distance between columns of D')
    axes[0].set_title('Step 1: tree', loc='left')
    x = np.arange(4)
    axes[1].bar(x - 0.27, [0.25] * 4, 0.26, color=g.EWcol, label='1/N')
    axes[1].bar(x, wk['w_ivar'], 0.26, color=g.Amber, label='Inverse variance')
    axes[1].bar(x + 0.27, wk['w'], 0.26, color='#17A2B8', label='HRP')
    for i, v in enumerate(wk['w']):
        axes[1].text(i + 0.27, v + 0.01, f'{v:.1%}', ha='center', fontsize=6.5, color='black')
    axes[1].set_xticks(x, [f'{n}\nvol {v:.0%}' for n, v in zip(names, wk['vol'])])
    fmt_pct(axes[1])
    axes[1].set_title('Steps 2-3: weights after recursive bisection', loc='left')
    bottom_legend(fig, ncol=3)
    g.save_fig('ch4_sem_b3_worked')


def fig_b3_sectors(B3):
    """B3: the sector tree, the ordered correlations and the weights / risk shares."""
    R, Rex, rf = g.us_monthly(SECTORS)
    X = Rex.values[-g.WINDOW:]
    S = np.cov(X.T)
    L = g.hrp_tree(S)
    order = list(leaves_list(L))
    fig = plt.figure(figsize=(W_IN, 2.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.5])
    ax = fig.add_subplot(gs[0])
    dendrogram(L, labels=SECTORS, ax=ax, color_threshold=0, above_threshold_color=g.MainBlue, leaf_rotation=90)
    ax.set_title('Tree', loc='left')
    ax.tick_params(axis='x', labelsize=6.5)
    ax = fig.add_subplot(gs[1])
    Cr = np.corrcoef(X.T)[np.ix_(order, order)]
    im = ax.imshow(Cr, cmap='Blues', vmin=0, vmax=1)
    lab = [SECTORS[i] for i in order]
    ax.set_xticks(range(9), lab, rotation=90, fontsize=6)
    ax.set_yticks(range(9), lab, fontsize=6)
    ax.set_title('Correlations, tree order', loc='left')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03).ax.tick_params(labelsize=6)
    ax = fig.add_subplot(gs[2])
    x = np.arange(9)
    wE, wH = [B3['w_erc'][s] for s in SECTORS], [B3['w_hrp'][s] for s in SECTORS]
    rcE = g.risk_contrib(np.array(wE), S)
    ax.bar(x - 0.27, [1 / 9] * 9, 0.26, color=g.EWcol, label='1/N weight')
    ax.bar(x, wE, 0.26, color=g.Forest, label='ERC weight')
    ax.bar(x + 0.27, wH, 0.26, color='#17A2B8', label='HRP weight')
    ax.plot(x, [B3['rc_ew'][s] for s in SECTORS], 'D', color=g.IDAred, ms=3.5, label='1/N risk share')
    ax.plot(x, [B3['rc_hrp'][s] for s in SECTORS], 'o', color=g.MainBlue, ms=3.5, label='HRP risk share')
    ax.set_xticks(x, SECTORS, rotation=90, fontsize=6.5)
    fmt_pct(ax)
    ax.set_title('Weights and risk shares', loc='left')
    bottom_legend(fig, ncol=3, fontsize=7)
    g.save_fig('ch4_sem_b3_sectors')
    return dict(order=[SECTORS[i] for i in order], rc_erc=dict(zip(SECTORS, rcE.tolist())))


def fig_b4(bts):
    """B4: 16 ETFs: sample / LW / NL spectra on the last window and the variance-ratio intervals."""
    Rc, Rexc, _ = g.us_monthly(g.COMBINED)
    X = Rexc.values[-g.WINDOW:]
    N = X.shape[1]
    ev = lambda A: np.sort(np.linalg.eigvalsh(A))[::-1] * 12
    S = np.cov(X.T)
    Slw = g.lw_cc(X)[0]
    Snl = g.nl_shrink(X)
    retn, ton, _ = g.backtest(Rc, Rexc, strategies=['GMV', 'GMV-LW', 'GMV-NL'])
    pairs = [('GMV-LW', 'GMV'), ('GMV-NL', 'GMV'), ('GMV-NL', 'GMV-LW')]
    iv = {}
    for a, b in pairs:
        vr, ci, _ = var_ratio_boot(retn[a], retn[b])
        iv[f'{a}/{b}'] = dict(vr=float(vr), ci=ci.tolist())
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.2, 1]})
    ax = axes[0]
    k = np.arange(1, N + 1)
    for A_, c, m, lab in [(S, g.IDAred, 'o', 'Sample'), (Slw, g.MainBlue, 's', 'Linear, constant correlation'),
                          (Snl, g.Forest, '^', 'Nonlinear (analytical)')]:
        ax.plot(k, ev(A_), m + '-', color=c, ms=3, lw=0.9, label=f'{lab}: condition number {np.linalg.cond(A_):.0f}')
    ax.set_yscale('log')
    ax.set_xlabel('Eigenvalue rank')
    ax.set_ylabel('Eigenvalue (annualised, log)')
    ax.set_title(f'16 ETFs, {Rexc.index[-g.WINDOW]:%b %Y} - {Rexc.index[-1]:%b %Y}', loc='left')
    ax = axes[1]
    for i, (key, d) in enumerate(iv.items()):
        ax.errorbar(d['vr'], i, xerr=[[d['vr'] - d['ci'][0]], [d['ci'][1] - d['vr']]], fmt='o', color=g.MainBlue,
                    capsize=3)
        ax.text(d['ci'][1] + 0.01, i, f"{d['vr']:.2f}", va='center', fontsize=7, color='black')
    ax.axvline(1, color='black', lw=0.8)
    ax.set_yticks(range(3), list(iv))
    ax.tick_params(axis='y', labelsize=7)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel('Variance ratio, 95% interval')
    ax.set_title('Paired block bootstrap', loc='left')
    bottom_legend(fig, ncol=1, fontsize=7)
    g.save_fig('ch4_sem_b4_shrink')
    return dict(intervals=iv, cond=dict(sample=float(np.linalg.cond(S)), lw=float(np.linalg.cond(Slw)),
                                        nl=float(np.linalg.cond(Snl))),
                vol_ew=float(bts['Combined'][0]['1/N'].std() * np.sqrt(12)))


def fig_b5():
    """B5: Bitcoin weight in ERC and HRP, and wealth with / without Bitcoin (same months)."""
    syms = [s + '.US' for s in MULTI] + ['BTC-USD.CC']
    p = prices(syms).resample('ME').last()
    r = p.pct_change().dropna().loc[:g.US_END]
    r.columns = MULTI + ['BTC']
    rf = french_rf().reindex(r.index)
    rex = r.sub(rf, axis=0)
    ret_b, to_b, W_b = g.backtest(r, rex, strategies=['1/N', 'ERC', 'HRP'])
    ret_n, to_n, W_n = g.backtest(r[MULTI], rex[MULTI], strategies=['1/N', 'ERC', 'HRP'])
    rcs = []
    for t in range(g.WINDOW, len(rex)):
        S = np.cov(rex.values[t - g.WINDOW:t].T)
        rcs.append(g.risk_contrib(g.w_ew(9), S)[-1])
    rcs = pd.Series(rcs, index=ret_b.index)
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3))
    ax = axes[0]
    ax.plot(W_b['ERC'].index, W_b['ERC']['BTC'], color=g.Forest, lw=1.3, label='Bitcoin weight in ERC')
    ax.plot(W_b['HRP'].index, W_b['HRP']['BTC'], color='#17A2B8', lw=1.3, label='Bitcoin weight in HRP')
    ax.plot(rcs.index, rcs, color=g.IDAred, lw=1.1, ls='--', label='Bitcoin risk share in 1/N')
    ax.axhline(1 / 9, color=g.EWcol, lw=1.0, ls=':', label='1/N weight 11.1%')
    ax.set_yscale('log')
    fmt_pct(ax, dec=1)
    ax.set_title('Bitcoin: weight and risk share (log)', loc='left')
    ax = axes[1]
    rfo = ret_b.attrs['rf']
    for s in ['1/N', 'ERC', 'HRP']:
        ax.plot(ret_b.index, np.cumprod(1 + ret_b[s] + rfo), color=g.SCOL[s], lw=1.4, label=f'{s} with Bitcoin')
        ax.plot(ret_n.index, np.cumprod(1 + ret_n[s] + rfo), color=g.SCOL[s], lw=0.9, ls='--', label=f'{s} without')
    ax.set_title(f'Wealth of 1 USD, {ret_b.index[0]:%b %Y} - {ret_b.index[-1]:%b %Y}', loc='left')
    bottom_legend(fig, ncol=3, fontsize=7)
    g.save_fig('ch4_sem_b5_btc')
    pv = {s: g.sr_diff_hac(ret_b[s], ret_n[s])[2] for s in ['1/N', 'ERC', 'HRP']}
    return dict(holm=g.holm(pv), rc_btc_mean=float(rcs.mean()), rc_btc_last=float(rcs.iloc[-1]),
                oos_start=f'{ret_b.index[0]:%Y-%m}', desc_start=f'{r.index[0]:%Y-%m}')


def fig_b6(bts, B6):
    """B6: HRP against GMV on 16 ETFs: gross/net points and the bootstrap distribution."""
    ret, to, W = bts['Combined']
    res, tstar = g.sr_diff_boot(ret['HRP'], ret['GMV'], block=B6['block'])
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1, 1.2]})
    ax = axes[0]
    pts = {}
    for s in ['HRP', 'GMV']:
        g_ = ret[s]
        n_ = ret[s] - 0.005 * to[s].fillna(0)
        a = (g_.std() * np.sqrt(12), g_.mean() * 12)
        b = (n_.std() * np.sqrt(12), n_.mean() * 12)
        ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='->', color=g.SCOL[s], lw=1.2))
        ax.plot(*a, 'o', mfc='none', color=g.SCOL[s], ms=6, label=f'{s} gross (Sharpe {g.sharpe(g_):.2f})')
        ax.plot(*b, 'o', color=g.SCOL[s], ms=6, label=f'{s} net of 50 bp (Sharpe {g.sharpe(n_):.2f})')
        pts[s] = dict(gross=[float(v) for v in a], net=[float(v) for v in b])
    ax.axhline(0, color=g.Gray, lw=0.5)
    fmt_pct(ax)
    fmt_pct(ax, 'x')
    ax.set_xlim(0, 0.09)
    ax.set_xlabel('Volatility')
    ax.set_ylabel('Mean excess return')
    ax.set_title('Gross and net, May 2012 - Jul 2026', loc='left')
    ax = axes[1]
    ax.hist(tstar, bins=np.linspace(-5, 5, 61), density=True, color='#17A2B8', alpha=0.8,
            label='Bootstrap studentized statistic')
    ax.axvline(res['t_obs'], color=g.IDAred, lw=1.5, label=f"Observed {res['t_obs']:+.2f}")
    ax.axvline(res['z_star'], color='black', ls='--', lw=0.8, label=f"5% critical values +/-{res['z_star']:.2f}")
    ax.axvline(-res['z_star'], color='black', ls='--', lw=0.8)
    ax.set_title(f"HRP minus GMV, block {B6['block']}: p = {res['p_boot']:.2f}", loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_b6_hrp_gmv')
    z10 = np.quantile(np.abs(tstar), 0.90)
    return dict(points=pts, p_boot=res['p_boot'], ci=res['ci'], z_star=res['z_star'], z_star10=float(z10),
                t_obs=res['t_obs'])


def fig_b7():
    """B7: Black-Litterman on the eight ETFs, view GLD - TLT = 4%: weights, confidence, long-only variant."""
    rex, Sig, P, q = bl_setup(MULTI, '2016-08-01', ('GLD', 'TLT'), 0.04)
    n = len(MULTI)
    pi, mu_bl, w_bl = g.black_litterman(Sig, g.w_ew(n), P, q)
    ks = np.exp(np.linspace(np.log(0.05), np.log(50), 150))
    Wk = bl_confidence_curve(Sig, P, q, ks)
    f = lambda w: 1.25 * w @ Sig @ w - w @ mu_bl
    res = minimize(f, g.w_ew(n), method='SLSQP', bounds=[(0, 1)] * n,
                   constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1}], options={'ftol': 1e-14, 'maxiter': 500})
    w_lo = np.clip(res.x, 0, None)
    w_lo /= w_lo.sum()
    k10 = bl_confidence_curve(Sig, P, q, [10])[0]
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.35, 1]})
    ax = axes[0]
    x = np.arange(n)
    ax.bar(x - 0.27, g.w_ew(n), 0.26, color=g.EWcol, label='Benchmark 1/N')
    ax.bar(x, w_bl, 0.26, color=g.MainBlue, label='Black-Litterman, unconstrained')
    ax.bar(x + 0.27, w_lo, 0.26, color=g.Forest, label='Black-Litterman, long-only')
    ax.axhline(0, color=g.Gray, lw=0.5)
    ax.set_xticks(x, MULTI, rotation=90)
    fmt_pct(ax)
    ax.set_title('Weights (negative = short position)', loc='left')
    ax = axes[1]
    ax.plot(ks, Wk[:, MULTI.index('GLD')], color=g.Amber, lw=1.4, label='GLD weight')
    ax.plot(ks, Wk[:, MULTI.index('TLT')], color=g.Purple, lw=1.4, label='TLT weight')
    ax.axvline(1, color=g.Gray, lw=0.6, ls=':')
    ax.axhline(0, color=g.Gray, lw=0.5)
    ax.set_xscale('log')
    ax.set_xlabel(r'$\Omega / (\tau P \Sigma P^\top)$, log scale')
    fmt_pct(ax)
    ax.set_title('Tilt against confidence', loc='left')
    bottom_legend(fig, ncol=3, fontsize=7)
    g.save_fig('ch4_sem_b7_bl_multi')
    sv = (P @ Sig @ P.T).item()
    return dict(order=MULTI, spread_var=sv, spread_vol=float(np.sqrt(sv)), surprise=float((q - P @ pi).item()),
                tilt=float((q - P @ pi).item() / (2 * 2.5 * sv)), w_lo=dict(zip(MULTI, w_lo.tolist())),
                k10_gld=float(k10[MULTI.index('GLD')]), k10_tlt=float(k10[MULTI.index('TLT')]), sum_w=float(w_bl.sum()))


def fig_b8(bts, B8):
    """B8: net Sharpe ratio as a function of cost (0-200 bp), MV-LO and 1/N, the break-even point and its approximation."""
    ret, to, W = bts['Combined']
    c = np.linspace(0, 200, 2001)
    nets = {s: np.array([g.sharpe(ret[s] - cc / 1e4 * to[s].fillna(0)) for cc in c]) for s in ['MV-LO', '1/N']}
    s1, s2 = ret['MV-LO'].std() * np.sqrt(12), ret['1/N'].std() * np.sqrt(12)
    TO1, TO2 = to['MV-LO'].mean(), to['1/N'].mean()
    slope1, slope2 = 12 * TO1 * 1e-4 / s1, 12 * TO2 * 1e-4 / s2
    approx = (B8['sr_mvlo'] - B8['sr_ew']) / (slope1 - slope2)
    fig, ax = plt.subplots(figsize=(W_IN * 0.85, 2.2))
    for s in ['MV-LO', '1/N']:
        ax.plot(c, nets[s], color=g.SCOL[s], lw=1.5, label=f'{s}: mean turnover {to[s].mean():.3f}')
    be = B8['breakeven_bp']
    ax.axvline(be, color='black', lw=0.8, ls='--', label=f'Grid crossing {be:.1f} bp')
    ax.axvline(approx, color=g.Purple, lw=0.8, ls=':', label=f'Fixed-volatility approximation {approx:.1f} bp')
    ax.set_xlabel('Cost per unit of turnover (basis points)')
    ax.set_ylabel('Net Sharpe ratio (annualised)')
    ax.set_title('Combined universe, May 2012 - Jul 2026', loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_b8_breakeven')
    one = float(ret['MV-LO'].index[1].strftime('%Y%m'))
    return dict(s1=float(s1), s2=float(s2), slope1=float(slope1), slope2=float(slope2), approx=float(approx),
                net50_mvlo=float(nets['MV-LO'][500]), net50_ew=float(nets['1/N'][500]),
                net100_mvlo=float(nets['MV-LO'][1000]), net100_ew=float(nets['1/N'][1000]),
                month2=f"{ret.index[1]:%Y-%m}", to_month2=float(to['MV-LO'].iloc[1]),
                cost_month2_20bp=float(0.002 * to['MV-LO'].iloc[1]))


def fig_b9(nsim=2000, seed=SEED):
    """B9: Britten-Jones coefficients with intervals, p-values of the two tests and their size under H0."""
    R_s, Rex_s, _ = g.us_monthly(SECTORS)
    h = len(Rex_s) // 2
    samples = {'Full': Rex_s, 'First half': Rex_s.iloc[:h], 'Second half': Rex_s.iloc[h:]}
    bj = {k: g.britten_jones(v) for k, v in samples.items()}
    # size of the tests under H0: mu proportional to Sigma 1 (tangency = 1/N), i.i.d. Normal, T = 166
    X2 = Rex_s.iloc[h:].values
    S2 = np.cov(X2.T)
    one = np.ones(9)
    w_eq = one / 9
    sr_ew = (w_eq @ X2.mean(0)) / np.sqrt(w_eq @ S2 @ w_eq)
    mu0 = S2 @ one
    mu0 = mu0 * sr_ew / np.sqrt(mu0 @ np.linalg.solve(S2, mu0))
    rng = np.random.default_rng(seed)
    rej = {'F': 0, 'Wald': 0}
    T2 = len(X2)
    for k in range(nsim):
        Xs = rng.multivariate_normal(mu0, S2, T2)
        b = g.britten_jones(Xs)
        rej['F'] += b['pF'] < 0.05
        rej['Wald'] += b['p_wald_hac'] < 0.05
    size = {k: v / nsim for k, v in rej.items()}
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    full = bj['Full']
    b = np.array(full['b'])
    se = b / np.array(full['t'])
    seh = b / np.array(full['t_hac'])
    x = np.arange(9)
    ax.errorbar(x - 0.12, b, yerr=1.96 * se, fmt='o', color=g.MainBlue, capsize=2, ms=3, label='OLS 95% interval')
    ax.errorbar(x + 0.12, b, yerr=1.96 * seh, fmt='s', color=g.Orange, capsize=2, ms=3, label='HAC 95% interval')
    ax.axhline(0, color=g.Gray, lw=0.5)
    ax.set_xticks(x, SECTORS, rotation=90)
    ax.set_ylabel('Coefficient b (not a weight)')
    ax.set_title('Full sample, T = 331', loc='left')
    ax = axes[1]
    ks = list(samples)
    for i, k in enumerate(ks):
        ax.plot(bj[k]['pF'], i + 0.1, 'o', color=g.MainBlue, ms=5, label='Exact F test' if i == 0 else None)
        ax.plot(bj[k]['p_wald_hac'], i - 0.1, 's', color=g.Orange, ms=5, label='HAC Wald test' if i == 0 else None)
    ax.axvline(0.05, color=g.IDAred, lw=0.8, ls='--', label='5% level')
    ax.set_xscale('log')
    ax.set_yticks(range(3), ks)
    ax.set_xlabel('p-value of H0: tangency = 1/N (log)')
    ax.set_title('Three samples, two tests', loc='left')
    bottom_legend(fig, ncol=3, fontsize=7)
    g.save_fig('ch4_sem_b9_bj')
    return dict(size=size, nsim=nsim, T_null=T2, sr_ew_monthly=float(sr_ew),
                tests={k: dict(F=v['F'], pF=v['pF'], W=v['wald_hac'], pW=v['p_wald_hac'], T=v['T']) for k, v in bj.items()})


def c2_ai_answer():
    """C2: the assistant's code (full-sample window, sqrt(252), no risk-free rate) and the successive corrections."""
    p = prices([s + '.US' for s in SECTORS])
    r = p.resample('ME').last().pct_change().dropna().loc[:g.US_END]
    rf = french_rf().reindex(r.index)
    S = r.cov().values
    w = np.linalg.solve(S, np.ones(len(S)))
    w = w / w.sum()
    port = r.dot(w)
    ai = port.mean() / port.std() * np.sqrt(252)
    fix2 = port.mean() / port.std() * np.sqrt(12)                      # annualisation only
    ex_is = port - rf
    fix23 = ex_is.mean() / ex_is.std() * np.sqrt(12)                   # annualisation + risk-free rate, in sample
    rolled = {}
    for t in range(60, len(r)):
        St = r.iloc[t - 60:t].cov().values
        wt = np.linalg.solve(St, np.ones(len(St)))
        wt = wt / wt.sum()
        rolled[r.index[t]] = r.iloc[t].dot(wt)
    port_oos = pd.Series(rolled)
    ex = port_oos - rf.reindex(port_oos.index)
    fixed = ex.mean() / ex.std() * np.sqrt(12)
    only_la = port_oos.mean() / port_oos.std() * np.sqrt(12)
    vals = [('AI answer', ai), ('Monthly factor sqrt(12)', fix2), ('+ excess returns', fix23),
            ('+ rolling 60-month window\n(corrected)', fixed)]
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.3), gridspec_kw={'width_ratios': [1, 1.25]})
    ax = axes[0]
    ts = lambda s: pd.Timestamp(s)
    ax.barh(1, (r.index[-1] - r.index[0]).days, left=r.index[0], height=0.45, color=g.IDAred, alpha=0.8,
            label='AI: one covariance from all months')
    ax.barh(0, (ts('2003-12-31') - ts('1999-01-31')).days, left=ts('1999-01-31'), height=0.45, color=g.MainBlue,
            label='Corrected: months t-60 ... t-1')
    ax.barh(0, 31, left=ts('2004-01-01'), height=0.45, color=g.Forest, label='Month t evaluated')
    ax.plot([ts('2004-01-15')] * 2, [0.2, 0.8], color='black', lw=0.8)
    ax.text(ts('2005-01-01'), 0.5, 'Jan 2004 weights must not use later months', fontsize=6.5, va='center',
            color='black')
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_yticks([0, 1], ['Corrected', 'AI'])
    ax.set_title('Which months enter the weights?', loc='left')
    ax = axes[1]
    y = np.arange(len(vals))[::-1]
    ax.barh(y, [v for _, v in vals], color=[g.IDAred, g.Orange, g.Amber, g.Forest], height=0.55)
    for yi, (_, v) in zip(y, vals):
        ax.text(v + 0.05, yi, f'{v:.2f}', va='center', fontsize=7, color='black')
    ax.set_yticks(y, [l for l, _ in vals], fontsize=7)
    ax.set_xlim(0, max(v for _, v in vals) * 1.2)
    ax.set_xlabel('Reported annualised Sharpe ratio')
    ax.set_title('Fixing the errors one at a time', loc='left')
    bottom_legend(fig, ncol=2, fontsize=7)
    g.save_fig('ch4_sem_c2_correction')
    return dict(ai=float(ai), fix_ann=float(fix2), fix_ann_rf=float(fix23), fixed=float(fixed),
                oos_no_rf=float(only_la), T=len(r), T_oos=len(port_oos), start=f'{r.index[0]:%Y-%m}',
                oos_start=f'{port_oos.index[0]:%Y-%m}', w_is_max=float(w.max()), w_is_min=float(w.min()))


def fig_c1_tests(C):
    """C1: raw and Holm-adjusted p-values of the eight tests (4 rules x 2 benchmarks)."""
    strats = ['1/N', 'GMV-LW', 'ERC', 'HRP']
    rows = [(s, k) for s in strats for k in ('bettr', 'local')]
    fig, ax = plt.subplots(figsize=(W_IN * 0.85, 2.3))
    y = np.arange(len(rows))[::-1]
    for yi, (s, k) in zip(y, rows):
        ax.plot(C[s][f'p_vs_{k}'], yi, 'o', color=g.MainBlue, ms=5, label='Raw HAC p-value' if yi == y[0] else None)
        ax.plot(C[s][f'holm_vs_{k}'], yi, 's', color=g.Orange, ms=5, label='Holm-adjusted' if yi == y[0] else None)
    ax.axvline(0.05, color=g.IDAred, lw=0.8, ls='--', label='5% level')
    ax.set_xscale('log')
    ax.set_yticks(y, [f'{s}, global vs ' + ('BET-TR' if k == 'bettr' else 'BVB-only') for s, k in rows], fontsize=7)
    ax.set_xlabel('p-value (log)')
    ax.set_title('One family of eight tests', loc='left')
    bottom_legend(fig, ncol=3, fontsize=7)
    g.save_fig('ch4_sem_c1_tests')


def c1_extra():
    """C1: one USD -> RON conversion and the sensitivity to a RON risk-free rate of 5% a year (5%/12 a month)."""
    m = part_c_data()
    p = prices(['SPY.US'])
    fx = bnr_rate('USD', 2014, 2026)
    j = p.join(fx, how='inner')
    d = j.index[j.index >= '2017-10-02'][0]
    return dict(date=f'{d:%Y-%m-%d}', spy_usd=float(j.loc[d, 'SPY.US']), usdron=float(j.loc[d, 'USDRON']),
                spy_ron=float(j.loc[d, 'SPY.US'] * j.loc[d, 'USDRON']))


def seminar_charts(R):
    sem_style()
    bts = g.run_backtests()
    A, B, M = R['A'], R['B'], R['M']
    S = {}
    S['setup'] = setup_check()
    S['A1'] = fig_a1(A['A1'])
    S['A3'] = fig_a3(A['A3'])
    fig_a4(A['A3'], A['A4'])
    S['A_5050'] = a_5050(A['A3'], A['A4'])
    fig_a5(A['A5'])
    S['A6'] = fig_a6()
    fig_a7(A['A7'])
    S['A8'] = fig_a8(A['A7'], A['A8'])
    S['A9'] = fig_a9()
    S['B1_first'] = b1_first_month(bts)
    fig_b1_timeline(S['B1_first'])
    S['B1_wealth'] = fig_b1_wealth(bts)
    S['B1_boot'] = fig_b1_boot(bts, B['B1'])
    S['B2_pipe'] = b2_pipeline()
    S['B2'] = fig_b2(bts)
    S['B2x'] = fig_b2x()
    S['B3_worked'] = b3_worked()
    fig_b3_worked(S['B3_worked'])
    S['B3'] = fig_b3_sectors(B['B3'])
    S['B4'] = fig_b4(bts)
    S['B5'] = fig_b5()
    S['B6'] = fig_b6(bts, B['B6'])
    S['B7'] = fig_b7()
    S['B8'] = fig_b8(bts, B['B8'])
    S['B9'] = fig_b9()
    S['C2'] = c2_ai_answer()
    fig_c1_tests(R['C'])
    S['C1'] = c1_extra()
    C = R['C']
    S['C1']['rf5'] = {k: (C[k]['sr_global'] * C[k]['vol_global'] - 0.05) / C[k]['vol_global']
                      for k in ['1/N', 'GMV-LW', 'ERC', 'HRP']}
    S['C1']['rf5']['BET-TR'] = (C['bet_tr']['mean'] - 0.05) / C['bet_tr']['vol']
    return S


if __name__ == '__main__':
    if '--charts' in sys.argv:
        # seminar charts: base results (including the calibrated blocks) from sem4_results.json
        with open(os.path.join(HERE, 'sem4_results.json')) as f:
            R = json.load(f)
        R['S'] = seminar_charts(R)
        with open(os.path.join(HERE, 'sem4_results.json'), 'w') as f:
            json.dump(g.to_py(R), f, indent=1, default=str)
        print(json.dumps(g.to_py(R['S']), indent=1, default=str))
        sys.exit(0)
    R = {'A': part_a()}
    bts = g.run_backtests()
    R['A'].update(part_a_tests(bts))
    R['B'] = b_backtest_stats(bts, n_jobs=3)
    R['M'] = master_level(bts)
    R['B']['B5'] = b5_btc()
    R['B']['B7'] = b7_bl_multi()
    R['C'] = part_c()
    R['S'] = seminar_charts(R)
    with open(os.path.join(HERE, 'sem4_results.json'), 'w') as f:
        json.dump(g.to_py(R), f, indent=1, default=str)
    print(json.dumps(g.to_py(R), indent=1, default=str))

"""
seminar7.py -- Computations of Seminar 7 (MFM): VaR and Expected Shortfall
===========================================================================
Part A: VaR/ES for the Normal and Student-t distributions step by step, discrete losses, subadditivity,
        component VaR for two assets, Cornish-Fisher.
Part B: HS on BET with a bootstrap interval, GPD and EVT VaR on BET, FHS vs HS on Bitcoin, Cornish-Fisher vs
        empirical, component VaR for a portfolio, bootstrap interval for ES.
Part C: capital required by ES 2.5% for a BVB blue-chip portfolio vs an S&P 500 portfolio (2016-2026).
The numbers are written to sem7_results.json.
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
from mfm_data import log_returns, joint_returns, load_close   # noqa: E402
from risk_measures import (hs_var_es, normal_var_es, cf_quantile, cf_var_es, gpd_fit, gpd_var_es, gpd_se, mean_excess,  # noqa: E402
                           garch_filter, garch_next, fhs_mc, rolling_conditional)
from generate_all_charts import (save_fig, legend_outside_bottom, discrete_var_es, jsonable, MainBlue, IDAred,  # noqa: E402
                                 Forest, Amber, Orange, Teal, Gray, LightGray, Purple, SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
B_BOOT = 2000


# =============================================================================
# PART A
# =============================================================================
def a1_normal(mu=0.04, sigma=1.2, position=1_000_000):
    """VaR and ES for the Normal distribution, step by step: X ~ N(mu, sigma^2) (returns in %),
    VaR_alpha = -(mu + sigma z_alpha), ES_alpha = -mu + sigma phi(z_alpha) / alpha."""
    out = dict(mu=mu, sigma=sigma, position=position)
    for a, tag in [(0.01, '1'), (0.025, '2_5')]:
        z = stats.norm.ppf(a)                  # z_alpha < 0
        phi = stats.norm.pdf(z)
        out[f'z{tag}'] = z
        out[f'phi{tag}'] = phi
        out[f'k{tag}'] = phi / a
        out[f'var{tag}'] = -(mu + sigma * z)
        out[f'es{tag}'] = -mu + sigma * phi / a
    out['var1_10'] = -10 * mu - np.sqrt(10) * sigma * out['z1']   # 10 days, additive i.i.d. returns
    return out


def a2_student(nu=4, mu=0.04, sigma=1.2):
    """Student-t scaled to the same variance: X = mu + s T, s = sigma sqrt((nu-2)/nu);
    VaR_alpha = -(mu + s t_alpha), ES_alpha = -mu + s g(t_alpha)/alpha (nu + t_alpha^2)/(nu - 1)."""
    s = sigma * np.sqrt((nu - 2) / nu)
    out = dict(nu=nu, s=s)
    for a, tag in [(0.01, '1'), (0.025, '2_5')]:
        q = stats.t.ppf(a, nu)                 # t_alpha < 0
        g = stats.t.pdf(q, nu)
        k = g / a * (nu + q ** 2) / (nu - 1)
        out[f'q{tag}'] = q
        out[f'g{tag}'] = g
        out[f'k{tag}'] = k
        out[f'var{tag}'] = -(mu + s * q)
        out[f'es{tag}'] = -mu + s * k
    return out


def a3_bond(p=0.03, lgd=60.0):
    out = dict(p=p, lgd=lgd)
    for a, tag in [(0.05, '5'), (0.025, '2_5')]:
        v, e = discrete_var_es([0, lgd], [1 - p, p], a)
        out[f'var{tag}'] = v
        out[f'es{tag}'] = e
    return out


def a4_bonds(p=0.007, lgd=100.0):
    out = dict(p=p, lgd=lgd, p_any=1 - (1 - p) ** 2, p_both=p ** 2, p_one=2 * p * (1 - p))
    for a, tag in [(0.01, '1'), (0.015, '1_5')]:
        v1, e1 = discrete_var_es([0, lgd], [1 - p, p], a)
        vp, ep = discrete_var_es([0, lgd, 2 * lgd], [(1 - p) ** 2, 2 * p * (1 - p), p ** 2], a)
        out.update({f'varA_{tag}': v1, f'esA_{tag}': e1, f'varP_{tag}': vp, f'esP_{tag}': ep})
    return out


def a5_components(pos=(600_000, 400_000), sig=(1.2, 0.9), rho=-0.2, alpha=0.01):
    """Component VaR 1% for two assets, Normal distribution, zero mean."""
    w = np.array(pos, float)
    s = np.array(sig) / 100
    S = np.array([[s[0] ** 2, rho * s[0] * s[1]], [rho * s[0] * s[1], s[1] ** 2]])
    sp = np.sqrt(w @ S @ w)
    z = stats.norm.ppf(1 - alpha)              # z_{1-alpha} = -z_alpha > 0
    Sw = S @ w
    mvar = z * Sw / sp
    cvar = w * mvar
    return dict(w=w, s=s, rho=rho, z=z, var_p_amt=z * sp, sigma_p_amt=sp, sp2=sp ** 2, Sw=Sw, mvar=mvar, cvar=cvar,
                share=cvar / (z * sp), var_ind=z * s * w, undiv=(z * s * w).sum())


def a6_cf(S=-0.5, K=3.0, sigma=1.2, mu=0.0, alpha=0.01, K2=10.0):
    """Cornish-Fisher on returns: skewness S, excess kurtosis K; VaR_alpha = -(mu + sigma z~_alpha)."""
    z = stats.norm.ppf(alpha)                  # z_alpha < 0
    t1, t2, t3 = (z ** 2 - 1) * S / 6, (z ** 3 - 3 * z) * K / 24, -(2 * z ** 3 - 5 * z) * S ** 2 / 36
    zc = cf_quantile(z, S, K)
    zc2 = cf_quantile(z, S, K2)
    return dict(S=S, K=K, K2=K2, z=z, t1=t1, t2=t2, t3=t3, zcf=zc, var_cf=-(mu + sigma * zc), var_n=-(mu + sigma * z),
                zcf2=zc2, var_cf2=-(mu + sigma * zc2))


# =============================================================================
# PART B
# =============================================================================
def boot_ci(L, fun, B=B_BOOT, block=None, seed=SEED):
    """95% percentile bootstrap interval: i.i.d. (block=None) or moving blocks of length block."""
    rng = np.random.default_rng(seed)
    L = np.asarray(L)
    n = len(L)
    stats_ = np.empty(B)
    for b in range(B):
        if block is None:
            x = L[rng.integers(0, n, n)]
        else:
            starts = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
            x = np.concatenate([L[s:s + block] for s in starts])[:n]
        stats_[b] = fun(x)
    return np.percentile(stats_, [2.5, 97.5]), stats_


def b1_bet_hs():
    L = -100 * log_returns('bet')
    out = {}
    boots = {}
    for tag, x in [('full', L), ('w500', L.iloc[-500:])]:
        v1, e1 = hs_var_es(x, 0.01)
        v2, e2 = hs_var_es(x, 0.025)
        ci, bs = boot_ci(x.values, lambda y: hs_var_es(y, 0.01)[0])
        boots[tag] = bs
        out[tag] = dict(N=len(x), start=str(x.index[0].date()), var1=v1, es1=e1, var2_5=v2, es2_5=e2,
                        ci_lo=ci[0], ci_hi=ci[1], n_beyond=int((x >= v1).sum()))
    # chart: loss tail + bootstrap distributions
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.6))
    ax = axes[0]
    ax.hist(L[L > 1.5], bins=np.linspace(1.5, 13.5, 61), color=MainBlue, alpha=0.55, label='BET daily losses above 1.5%')
    ax.axvline(out['full']['var1'], color=IDAred, lw=1.3, label=f"VaR 1% = {out['full']['var1']:.2f}%")
    ax.axvline(out['full']['es1'], color=IDAred, ls='--', lw=1.3, label=f"ES 1% = {out['full']['es1']:.2f}%")
    ax.set_xlabel('Daily loss (%)')
    ax.set_ylabel('Number of days')
    ax.set_title('BET, 2000-2026: historical simulation')
    pass
    ax = axes[1]
    ax.hist(boots['full'], bins=40, density=True, color=MainBlue, alpha=0.55, label='Full sample (2000-2026)')
    ax.hist(boots['w500'], bins=40, density=True, color=Amber, alpha=0.55, label='Last 500 days')
    ax.set_xlabel('Bootstrap VaR 1% (%)')
    ax.set_ylabel('Density')
    ax.set_title('Sampling uncertainty of HS VaR 1%')
    bottom_legend(fig, ncol=3, fontsize=8.5)
    plt.tight_layout()
    save_fig('ch7_sem_bet_hs')
    return out


def b2_bet_gpd():
    L = (-100 * log_returns('bet')).values
    f = gpd_fit(L, 0.05)
    se_xi, se_beta = gpd_se(f)
    out = dict(u=f['u'], xi=f['xi'], beta=f['beta'], nu=f['nu'], n=f['n'], se_xi=se_xi, se_beta=se_beta)
    for a, tag in [(0.01, '1'), (0.005, '0_5'), (0.001, '0_1')]:
        v, e = gpd_var_es(f, a)
        hv, he = hs_var_es(L, a)
        out.update({f'evt_var{tag}': v, f'evt_es{tag}': e, f'hs_var{tag}': hv, f'hs_es{tag}': he,
                    f'n_beyond{tag}': int((L >= hv).sum())})
    # sensitivity to the threshold
    qs = np.linspace(0.10, 0.015, 18)          # share of losses above the threshold
    xis, lo, hi, v01 = [], [], [], []
    for q in qs:
        g = gpd_fit(L, q)
        s = gpd_se(g)[0]
        xis.append(g['xi'])
        lo.append(g['xi'] - 1.96 * s)
        hi.append(g['xi'] + 1.96 * s)
        v01.append(gpd_var_es(g, 0.001)[0])
    out['xi_range'] = [float(min(xis)), float(max(xis))]
    out['v0_1_range'] = [float(min(v01)), float(max(v01))]
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.6))
    ax = axes[0]
    xs = np.sort(L[L > f['u']])
    emp = (1 - np.arange(len(xs)) / len(xs)) * f['nu'] / f['n']
    ax.loglog(xs, emp, 'o', ms=2.5, color=MainBlue, label='Empirical P(L >= x)')
    xx = np.linspace(f['u'], xs[-1] * 1.3, 200)
    ax.loglog(xx, f['nu'] / f['n'] * stats.genpareto.sf(xx - f['u'], f['xi'], scale=f['beta']), color=IDAred,
              label=f"GPD fit, xi = {f['xi']:.2f}")
    ax.loglog(xx, stats.norm.sf(xx, L.mean(), L.std()), color=Orange, ls='--', label='Normal distribution')
    ax.set_ylim(1e-5, 0.08)
    ax.set_xlabel('Daily loss x (%)')
    ax.set_ylabel('Exceedance probability')
    ax.set_title('BET: largest 5% of daily losses')
    pass
    ax = axes[1]
    ax.fill_between(100 * qs, lo, hi, color=LightGray, label='95% confidence band')
    ax.plot(100 * qs, xis, 'o-', ms=3, color=IDAred, label='Estimated xi')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Share of losses above u (%)')
    ax.set_ylabel(r'Shape $\hat\xi$')
    ax.set_title(r'Stability of $\xi$ across thresholds')
    bottom_legend(fig, ncol=3, fontsize=8.5)
    plt.tight_layout()
    save_fig('ch7_sem_bet_gpd')
    return out


def b3_btc_fhs():
    r = 100 * log_returns('btc')
    params, mu, sig = garch_filter(r)
    z = ((r - mu) / sig).dropna().values
    m1, s1 = garch_next(r, params)
    nz = -z
    q = np.quantile(nz, 1 - 0.01)
    L = -r
    v500, e500 = hs_var_es(L.iloc[-500:], 0.01)
    vfull, efull = hs_var_es(L, 0.01)
    roll = pd.read_csv(os.path.join(HERE, 'ch7_rolling_btc.csv'), index_col=0, parse_dates=True)
    rec = roll.loc['2024-09-18':]
    out = dict(mu=m1, sigma=s1, sigma_uncond=r.std(), zq=q, zes=nz[nz >= q].mean(), fhs_var=-m1 + s1 * q,
               fhs_es=-m1 + s1 * nz[nz >= q].mean(), hs500_var=v500, hs500_es=e500, hsfull_var=vfull, hsfull_es=efull,
               n_rec=len(rec), exc_hs_rec=int((rec['loss'] > rec['hs_var']).sum()),
               exc_fhs_rec=int((rec['loss'] > rec['fhs_var']).sum()),
               exc_hs_all=float((roll['loss'] > roll['hs_var']).mean()),
               exc_fhs_all=float((roll['loss'] > roll['fhs_var']).mean()), n_all=len(roll),
               alpha=params.iloc[3], beta=params.iloc[4], sd500=r.iloc[-500:].std(), last_r=r.iloc[-1])
    out.update(fig_btc_fhs3(out))
    return out


def b4_cf_vs_empirical():
    t = pd.read_csv(os.path.join(HERE, 'ch7_var_es_table.csv'), index_col=0)
    out = {}
    for k in t.index:
        L = (-100 * log_returns(k)).values
        ci, _ = boot_ci(L, lambda y: hs_var_es(y, 0.01)[0], B=1000)
        out[k] = dict(skew=-t.loc[k, 'skew'], kurt=t.loc[k, 'kurt'], hs1=t.loc[k, 'HS|VaR 1%'],
                      cf1=t.loc[k, 'Cornish-Fisher|VaR 1%'], n1=t.loc[k, 'Normal|VaR 1%'],
                      hs2_5=t.loc[k, 'HS|VaR 2.5%'], cf2_5=t.loc[k, 'Cornish-Fisher|VaR 2.5%'],
                      n2_5=t.loc[k, 'Normal|VaR 2.5%'], ci_lo=ci[0], ci_hi=ci[1])
    return out


def b5_components(w=(0.25, 0.25, 0.25, 0.25)):
    W = np.array(w)
    lr = joint_returns(['SPY', 'TLT', 'GLD', 'BTC'], start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)
    S = np.cov(R.values.T)
    sp = np.sqrt(W @ S @ W)
    z = stats.norm.ppf(1 - 0.01)
    mvar = z * (S @ W) / sp
    cvar = W * mvar
    Lp = -(R.values @ W)
    v, e = hs_var_es(Lp, 0.025)
    ces = -(R.values[Lp >= v] * W).mean(axis=0)
    return dict(N=len(R), var_p=z * sp, mvar=mvar, cvar=cvar, share=cvar / (z * sp), es_p=e, ces=ces,
                ces_share=ces / e, undiv=(z * np.sqrt(np.diag(S)) * W).sum())


def b6_es_boot():
    out = {}
    for k in ['sp500', 'bet']:
        L = (-100 * log_returns(k)).values
        for tag, x in [('full', L), ('w500', L[-500:])]:
            es = hs_var_es(x, 0.025)[1]
            ci_iid, _ = boot_ci(x, lambda y: hs_var_es(y, 0.025)[1])
            ci_blk, _ = boot_ci(x, lambda y: hs_var_es(y, 0.025)[1], block=20)
            out[f'{k}_{tag}'] = dict(N=len(x), es=es, iid_lo=ci_iid[0], iid_hi=ci_iid[1], blk_lo=ci_blk[0],
                                     blk_hi=ci_blk[1])
    return out


# =============================================================================
# PART C: ES 2.5% capital: BVB vs S&P 500
# =============================================================================
BVB = ['TLV', 'SNP', 'BRD', 'TGN', 'SNG', 'SNN', 'EL', 'TEL']
C_START = '2016-09-19'                  # last ten years


def c1_capital(position=1_000_000, B=B_BOOT):
    """Simplified illustration inspired by FRTB (not the full regulatory capital).
    Daily SIMPLE returns (in %): equally weighted BVB basket rebalanced daily, SPY.
    h-day loss = 100 (1 - prod(1 + R_t)) (compounding), so ES in % of the position converts exactly into money.
    Stress window: the 250 consecutive days with the largest ONE-DAY HISTORICAL ES 2.5%; 10-day stressed ES =
    one-day stressed ES x sqrt(10); 20-day liquidity horizon: x sqrt(20/10) (MAR33). Capital = 1.5 x stressed ES.
    Uncertainty: moving-block bootstrap (20 days), with the stress window held FIXED."""
    lr_b = joint_returns(BVB, start=C_START)
    lr_b = lr_b[(lr_b != 0).any(axis=1)]                # drop the days on which no stock price changed
    start = str(lr_b.index[0].date())
    Rb = 100 * (np.exp(lr_b) - 1)
    Rp_b = Rb.mean(axis=1)                               # simple return of the basket, equal weights, rebalanced daily
    Rp_s = 100 * (np.exp(joint_returns(['SPY']).loc[start:]['SPY']) - 1)
    out = dict(start=start, stocks=BVB)
    series = {'bvb': Rp_b, 'spy': Rp_s}
    es25 = lambda y: hs_var_es(y, 0.025)[1]              # noqa: E731
    for k, R in series.items():
        L = -R
        v1, e1 = hs_var_es(L, 0.025)
        L10 = 100 * (1 - (1 + R / 100).rolling(10).apply(np.prod, raw=True)).dropna()   # compounded 10-day losses
        e10 = hs_var_es(L10, 0.025)[1]
        roll = pd.Series([es25(L.iloc[i - 250:i]) for i in range(250, len(L) + 1)], index=L.index[249:])
        es_stress = roll.max()
        end_s = roll.idxmax()
        i_end = L.index.get_loc(end_s)
        start_s = L.index[i_end - 249]
        Ls = L.iloc[i_end - 249:i_end + 1].values
        # FHS: AR(1)-GARCH(1,1) on the portfolio log returns; each path converted exactly
        r = 100 * np.log(1 + R / 100)
        params, mu, sig = garch_filter(r)
        z = ((r - mu) / sig).dropna().values
        m1, s1 = garch_next(r, params)
        sim_log = fhs_mc(r, params, z, 10, n_paths=100_000, seed=SEED)      # 10-day log losses
        fhs10 = hs_var_es(100 * (1 - np.exp(-sim_log / 100)), 0.025)[1]
        # uncertainty: moving-block bootstrap with 20-day blocks
        ci1, _ = boot_ci(L.values, es25, B=B, block=20)
        ci_s, _ = boot_ci(Ls, es25, B=B, block=20)
        out[k] = dict(N=len(R), sd=R.std(), es1=e1, var1=v1, es10_sqrt=np.sqrt(10) * e1, es10_hs=e10,
                      rho1=float(R.autocorr(1)),
                      es_stress1=es_stress, es_stress10=np.sqrt(10) * es_stress, es_stress20=np.sqrt(20) * es_stress,
                      stress_from=str(start_s.date()), stress_to=str(end_s.date()), fhs10=fhs10, sigma_now=s1,
                      es1_lo=ci1[0], es1_hi=ci1[1], es_stress1_lo=ci_s[0], es_stress1_hi=ci_s[1],
                      cap_hs=np.sqrt(10) * e1 / 100 * position, cap_stress=np.sqrt(10) * es_stress / 100 * position,
                      cap_stress_lh20=np.sqrt(20) * es_stress / 100 * position,
                      ima10=1.5 * np.sqrt(10) * es_stress / 100 * position,
                      ima20=1.5 * np.sqrt(20) * es_stress / 100 * position,
                      cap_fhs=fhs10 / 100 * position, zero_share=float((Rb == 0).mean().mean()) if k == 'bvb' else 0.0)
    # correlation: align the portfolio values (BVB wealth index, SPY price) on common days first, then returns
    W = pd.concat([(1 + Rp_b / 100).cumprod(), (1 + Rp_s / 100).cumprod()], axis=1, join='inner')
    out['corr_bvb_spy'] = float(W.pct_change().dropna().corr().iloc[0, 1])
    # chart
    _style()
    fig, ax = plt.subplots(figsize=(W_FIG, 2.6))
    labs = ['HS,\nsqrt(10) x 1-day', 'HS, 10-day\ncompounded', 'Stressed 250\ndays, sqrt(10)', 'FHS Monte\nCarlo, 10-day']
    keys = ['es10_sqrt', 'es10_hs', 'es_stress10', 'fhs10']
    xx = np.arange(len(labs))
    vb = [out['bvb'][c] for c in keys]
    vs = [out['spy'][c] for c in keys]
    ax.bar(xx - 0.2, vb, 0.38, color=IDAred, label='BVB blue chips, equal weights')
    ax.bar(xx + 0.2, vs, 0.38, color=MainBlue, label='S&P 500 (SPY)')
    for i in range(len(labs)):
        ax.text(xx[i] - 0.2, vb[i] + 0.2, f'{vb[i]:.1f}', ha='center', fontsize=7)
        ax.text(xx[i] + 0.2, vs[i] + 0.2, f'{vs[i]:.1f}', ha='center', fontsize=7)
    ax.set_xticks(xx)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylabel('10-day ES 2.5% (% of position)')
    ax.set_title(f'Capital per unit invested, {start[:4]}-2026')
    bottom_legend(fig, ncol=2, fontsize=9)
    save_fig('ch7_sem_capital')
    return out



# =============================================================================
# SEMINAR CHARTS (charts/ch7_sem_*.pdf|png)
# Run:  python seminar7.py charts   (the extra numbers are added to sem7_results.json, key 'X')
# =============================================================================
W_FIG = 5.6                                   # width of the seminar figures (inches), as in Seminar 0


def _style():
    plt.rcParams['font.size'] = 10.5
    plt.rcParams['axes.titlesize'] = 10.5
    plt.rcParams['axes.labelsize'] = 10.5
    plt.rcParams['xtick.labelsize'] = 9.5
    plt.rcParams['ytick.labelsize'] = 9.5
    plt.rcParams['legend.fontsize'] = 9.5


def bottom_legend(fig, ncol=3, handles=None, labels=None, fontsize=9):
    """Legend below the figure (outside the axes), after tight_layout."""
    plt.tight_layout()
    if handles is None:
        handles, labels, seen = [], [], set()
        for ax in fig.axes:
            for h, lab in zip(*ax.get_legend_handles_labels()):
                if lab not in seen and not lab.startswith('_'):
                    handles.append(h)
                    labels.append(lab)
                    seen.add(lab)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False,
               fontsize=fontsize)


def fig_bet_data():
    """B1, before estimation: BET price and daily losses, with the window of the last 500 days."""
    _style()
    P = load_close('bet')
    L = -100 * np.log(P).diff().dropna()
    w0 = L.index[-500]
    fig, axes = plt.subplots(2, 1, figsize=(W_FIG, 3.0), sharex=True, gridspec_kw={'height_ratios': [1, 1.1]})
    ax = axes[0]
    ax.plot(P.index, P.values, color=MainBlue, lw=0.8, label='BET close (log scale)')
    ax.set_yscale('log')
    ax.set_ylabel('Index points')
    ax.axvspan(w0, P.index[-1], color=Amber, alpha=0.18, lw=0, label='Last 500 returns')
    ax = axes[1]
    ax.vlines(L.index, 0, L.clip(lower=0).values, color=Teal, lw=0.5, label='Daily log loss (gains set to 0)')
    ax.axvspan(w0, L.index[-1], color=Amber, alpha=0.18, lw=0)
    top = L.nlargest(60)
    d08 = top.loc['2008'].idxmax()
    d20 = top.loc['2020'].idxmax()
    for d, lab in [(d08, 'Oct 2008'), (d20, 'Mar 2020')]:
        ax.annotate(f'{lab}: {L.loc[d]:.1f}%', xy=(d, L.loc[d]), xytext=(8, -2), textcoords='offset points',
                    fontsize=9, color=IDAred)
    ax.set_ylabel('Loss (%)')
    bottom_legend(fig, ncol=3)
    save_fig('ch7_sem_bet_data')
    return dict(first=str(P.index[0].date()), last=str(P.index[-1].date()), p_first=float(P.iloc[0]),
                p_last=float(P.iloc[-1]), n_ret=int(len(L)), w500_start=str(w0.date()),
                max08=float(L.loc[d08]), d08=str(d08.date()), max20=float(L.loc[d20]), d20=str(d20.date()),
                maxall=float(L.max()), dmax=str(L.idxmax().date()), head=[(str(d.date()), float(v)) for d, v in P.iloc[:3].items()],
                ret_head=[(str(d.date()), float(v)) for d, v in (-L).iloc[:2].items()])


def fig_a1a2_tails(A1, A2):
    """A1-A2: the loss under the Normal distribution and under a t4 with the same standard deviation; VaR and ES at 1% and 2.5%."""
    _style()
    mu, sig, s, nu = 0.04, 1.2, A2['s'], 4
    x = np.linspace(0.0, 8.0, 800)
    sn = stats.norm.sf(x, -mu, sig)                     # L = -X ~ N(-mu, sigma^2): P(L > x)
    st = stats.t.sf((x + mu) / s, nu)
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.3))
    ax = axes[0]
    ax.semilogy(x, sn, color=MainBlue, label='Normal distribution, sd 1.2%')
    ax.semilogy(x, st, color=IDAred, label='Student-t, 4 df, sd 1.2%')
    for a_, ls in [(0.025, '--'), (0.01, ':')]:
        ax.axhline(a_, color=Gray, lw=0.6, ls=ls)
    ax.plot([A1['var1']], [0.01], 'o', color=MainBlue, ms=4)
    ax.plot([A2['var1']], [0.01], 'o', color=IDAred, ms=4)
    ax.plot([A1['es1']], [0.01], 'x', color=MainBlue, ms=5, mew=1.2)
    ax.plot([A2['es1']], [0.01], 'x', color=IDAred, ms=5, mew=1.2)
    ax.plot([], [], 'o', color='black', ms=4, label='VaR 1%')
    ax.plot([], [], 'x', color='black', ms=5, mew=1.2, label='ES 1%')
    ax.text(0.2, 0.013, '1%', fontsize=9, color='black')
    ax.text(0.2, 0.031, '2.5%', fontsize=9, color='black')
    ax.set_xlim(0, 8)
    ax.set_ylim(1e-4, 0.6)
    ax.set_xlabel('Daily loss x (%)')
    ax.set_ylabel('P(L > x)')
    ax.set_title('Tail probability of the loss')
    ax = axes[1]
    labs = ['VaR 2.5%', 'ES 2.5%', 'VaR 1%', 'ES 1%']
    vn = [A1['var2_5'], A1['es2_5'], A1['var1'], A1['es1']]
    vt = [A2['var2_5'], A2['es2_5'], A2['var1'], A2['es1']]
    xx = np.arange(4)
    ax.bar(xx - 0.19, vn, 0.36, color=MainBlue)
    ax.bar(xx + 0.19, vt, 0.36, color=IDAred)
    for i in range(4):
        ax.text(xx[i] - 0.19, vn[i] + 0.05, f'{vn[i]:.2f}', ha='right', fontsize=8, color=MainBlue)
        ax.text(xx[i] + 0.19, vt[i] + 0.05, f'{vt[i]:.2f}', ha='left', fontsize=8, color=IDAred)
    ax.set_xticks(xx)
    ax.set_xticklabels(labs, fontsize=8.5)
    ax.set_ylabel('% of the position')
    ax.set_ylim(0, 4.6)
    ax.set_title('Risk measures')
    bottom_legend(fig, ncol=4)
    save_fig('ch7_sem_a1a2_tails')


def fig_a3_mass():
    """A3: which probability mass enters ES 5% and ES 2.5% (loss 60 with p = 3%, otherwise 0)."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.2), gridspec_kw={'width_ratios': [1, 1.35]})
    ax = axes[0]
    ax.bar([0, 60], [97, 3], width=9, color=[MainBlue, IDAred])
    ax.text(0, 99, '97%', ha='center', fontsize=9, color=MainBlue)
    ax.text(60, 5, '3%', ha='center', fontsize=9, color=IDAred)
    ax.set_xticks([0, 60])
    ax.set_xlabel('Loss (monetary units)')
    ax.set_ylabel('Probability (%)')
    ax.set_ylim(0, 110)
    ax.set_title('Loss distribution')
    ax = axes[1]
    rows = [('ES 5%', 3.0, 2.0, 36), ('ES 2.5%', 2.5, 0.0, 60)]
    for i, (lab, m60, m0, es) in enumerate(rows):
        ax.barh(i, m60, color=IDAred, height=0.5, label='mass at loss 60' if i == 0 else None)
        ax.barh(i, m0, left=m60, color=MainBlue, height=0.5, label='mass at loss 0' if i == 0 else None)
        ax.text(5.15, i, f'ES = {es}', va='center', fontsize=9, color='black')
    ax.set_yticks([0, 1])
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 6.6)
    ax.set_xlabel('Tail probability used (%)')
    ax.set_title('Probability mass in the worst α of outcomes')
    bottom_legend(fig, ncol=2)
    save_fig('ch7_sem_a3_mass')


def fig_a4_var_alpha(p=0.007):
    """A4: VaR and ES as functions of alpha for one bond (x2) and for the portfolio A + B."""
    _style()
    al = np.linspace(0.002, 0.03, 700)
    one = [discrete_var_es([0, 100], [1 - p, p], a) for a in al]
    por = [discrete_var_es([0, 100, 200], [(1 - p) ** 2, 2 * p * (1 - p), p ** 2], a) for a in al]
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.3), sharex=True)
    lo, hi = p, 1 - (1 - p) ** 2
    for ax, j, ttl in [(axes[0], 0, 'VaR'), (axes[1], 1, 'ES')]:
        ax.axvspan(100 * lo, 100 * hi, color=Amber, alpha=0.2, lw=0, label='VaR not subadditive')
        ax.plot(100 * al, [2 * v[j] for v in one], color=MainBlue, label='VaR(A) + VaR(B), ES(A) + ES(B)')
        ax.plot(100 * al, [v[j] for v in por], color=IDAred, ls='--', label='Portfolio A + B')
        ax.set_title(ttl)
        ax.set_xlabel('Tail probability alpha (%)')
    axes[0].set_ylabel('Loss (monetary units)')
    axes[0].axvline(1.0, color=Gray, lw=0.6, ls=':')
    axes[1].axvline(1.0, color=Gray, lw=0.6, ls=':')
    bottom_legend(fig, ncol=3)
    save_fig('ch7_sem_a4_var_alpha')
    return dict(p_one=2 * p * (1 - p), lo=lo, hi=hi)


def fig_a5_shares(A5):
    """A5: money weights vs VaR shares; summed stand-alone VaR vs diversified VaR."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.2), gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    xx = np.arange(2)
    wgt = 100 * np.array(A5['w']) / np.sum(A5['w'])
    sh = 100 * np.array(A5['share'])
    ax.bar(xx - 0.19, wgt, 0.36, color=Teal, label='Money weight')
    ax.bar(xx + 0.19, sh, 0.36, color=MainBlue, label='Share of Normal VaR 1%')
    for i in range(2):
        ax.text(xx[i] - 0.19, wgt[i] + 2, f'{wgt[i]:.0f}%', ha='center', fontsize=9, color='black')
        ax.text(xx[i] + 0.19, sh[i] + 2, f'{sh[i]:.1f}%', ha='center', fontsize=9, color='black')
    ax.set_xticks(xx)
    ax.set_xticklabels(['Equity', 'Bonds'])
    ax.set_ylim(0, 100)
    ax.set_ylabel('%')
    ax.set_title('Money versus risk')
    ax = axes[1]
    vals = [A5['var_ind'][0], A5['var_ind'][1], A5['var_p_amt']]
    ax.bar([0], [vals[0]], 0.5, color=Orange, label='Stand-alone VaR, equity')
    ax.bar([0], [vals[1]], 0.5, bottom=[vals[0]], color=Amber, label='Stand-alone VaR, bonds')
    ax.bar([1], [vals[2]], 0.5, color=IDAred, label='Portfolio VaR 1%')
    ax.text(0, vals[0] + vals[1] + 400, f'{vals[0] + vals[1]:,.0f}', ha='center', fontsize=9)
    ax.text(1, vals[2] + 400, f'{vals[2]:,.0f}', ha='center', fontsize=9)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Sum', 'Portfolio'])
    ax.set_ylabel('EUR')
    ax.set_ylim(0, 29000)
    ax.set_title('Diversification')
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_a5_shares')


def risk_parity(S, tol=1e-12):
    """Non-negative, fully invested weights with equal contributions to the Normal VaR: w_i (S w)_i = constant."""
    from scipy import optimize
    d = S.shape[0]

    def obj(y):
        w = np.exp(y) / np.exp(y).sum()
        rc = w * (S @ w)
        return ((rc / rc.sum() - 1 / d) ** 2).sum()
    res = optimize.minimize(obj, np.zeros(d), method='Nelder-Mead', options=dict(xatol=1e-10, fatol=tol, maxiter=20000))
    w = np.exp(res.x) / np.exp(res.x).sum()
    return w


def fig_b5_shares(B5):
    """B5: equal weights vs shares of the Normal VaR 1% and of the historical ES 2.5%; plus the risk-parity weights."""
    _style()
    names = ['SPY', 'TLT', 'GLD', 'Bitcoin']
    lr = joint_returns(['SPY', 'TLT', 'GLD', 'BTC'], start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)
    S = np.cov(R.values.T)
    w_rp = risk_parity(S)
    z = stats.norm.ppf(0.99)
    sp_rp = np.sqrt(w_rp @ S @ w_rp)
    Lp = -(R.values @ w_rp)
    v_rp, e_rp = hs_var_es(Lp, 0.025)
    ces_rp = -(R.values[Lp >= v_rp] * w_rp).mean(axis=0)
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.3), gridspec_kw={'width_ratios': [1.6, 1]})
    ax = axes[0]
    xx = np.arange(4)
    for k, (vals, c, lab) in enumerate([(25 * np.ones(4), Teal, 'Money weight'),
                                        (100 * np.array(B5['share']), MainBlue, 'Share of Normal VaR 1%'),
                                        (100 * np.array(B5['ces_share']), IDAred, 'Share of historical ES 2.5%')]):
        ax.bar(xx + (k - 1) * 0.27, vals, 0.25, color=c, label=lab)
    for i in range(4):
        ax.text(xx[i] + 0.27, 100 * B5['ces_share'][i] + 2, f"{100 * B5['ces_share'][i]:.0f}", ha='center', fontsize=9,
                color=IDAred)
    ax.set_xticks(xx)
    ax.set_xticklabels(names)
    ax.set_ylabel('%')
    ax.set_ylim(0, 95)
    ax.set_title('Equal weights, 2014-2026')
    ax = axes[1]
    ax.bar([0], [B5['undiv']], 0.5, color=Orange, label='Sum of stand-alone VaR 1%')
    ax.bar([1], [B5['var_p']], 0.5, color=MainBlue, label='Portfolio VaR 1% (Normal)')
    ax.bar([2], [B5['es_p']], 0.5, color=IDAred, label='Portfolio ES 2.5% (historical)')
    for i, v in enumerate([B5['undiv'], B5['var_p'], B5['es_p']]):
        ax.text(i, v + 0.08, f'{v:.2f}', ha='center', fontsize=9)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Sum', 'VaR', 'ES'])
    ax.set_ylabel('% of portfolio value')
    ax.set_ylim(0, 5)
    ax.set_title('Portfolio totals')
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_b5_shares')
    rc = w_rp * (S @ w_rp)
    return dict(w_rp=w_rp, var_rp=z * sp_rp, share_rp=rc / rc.sum(), es_rp=e_rp, ces_rp_share=ces_rp / e_rp,
                sd=np.sqrt(np.diag(S)), inv_vol=(1 / np.sqrt(np.diag(S))) / (1 / np.sqrt(np.diag(S))).sum(),
                Sw_spy=(S @ np.full(4, 0.25))[0], var_p=B5['var_p'])


def fig_a6_cf(S=-0.5):
    """A6: the Cornish-Fisher map z -> z~(z) and its derivative for K = 3 and K = 10."""
    _style()
    z = np.linspace(stats.norm.ppf(0.001), 1.0, 500)
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.3))
    for K, c in [(3.0, MainBlue), (10.0, IDAred)]:
        axes[0].plot(z, cf_quantile(z, S, K), color=c, label=f'K = {K:.0f}')
        d = 1 + z * S / 3 + (z ** 2 - 1) * K / 8 - (6 * z ** 2 - 5) * S ** 2 / 36
        axes[1].plot(z, d, color=c)
    axes[0].plot(z, z, color=Gray, lw=0.6, ls=':')
    axes[0].set_xlabel('Normal quantile z')
    axes[0].set_ylabel(r'Cornish-Fisher quantile $\tilde z$')
    axes[0].set_title(r'The map $z \mapsto \tilde z(z)$, $S = -0.5$')
    axes[1].axhline(0, color=Gray, lw=0.6)
    axes[1].axvspan(stats.norm.ppf(0.001), 0, color=Amber, alpha=0.15, lw=0, label=r'Interval $[z_{0.1\%}, 0]$')
    axes[1].set_xlabel('Normal quantile z')
    axes[1].set_ylabel(r'Derivative $d\tilde z/dz$')
    axes[1].set_title('Negative slope = not a quantile')
    bottom_legend(fig, ncol=3)
    save_fig('ch7_sem_a6_cf')


def fig_a7_ru(p=0.007, alpha=0.01):
    """A7: the Rockafellar-Uryasev function F(v) = v + E[(L - v)+]/alpha for the A4 portfolio and for one bond."""
    _style()
    v = np.linspace(-10, 220, 2301)
    vals_p, pr_p = np.array([0, 100, 200.]), np.array([(1 - p) ** 2, 2 * p * (1 - p), p ** 2])
    vals_a, pr_a = np.array([0, 100.]), np.array([1 - p, p])
    F = lambda vals, pr: v + (np.maximum(vals[None, :] - v[:, None], 0) * pr).sum(axis=1) / alpha   # noqa: E731
    Fp, Fa = F(vals_p, pr_p), F(vals_a, pr_a)
    fig, ax = plt.subplots(figsize=(W_FIG * 0.8, 2.3))
    ax.plot(v, Fp, color=IDAred, label=r'$F(v)$, portfolio A + B')
    ax.plot(v, 2 * Fa, color=MainBlue, ls='--', label=r'$F_A(v) + F_B(v)$, stand-alone bonds')
    vp = 100.0
    fp = vp + ((np.maximum(vals_p - vp, 0) * pr_p).sum()) / alpha
    ax.plot([vp], [fp], 'o', color=IDAred, ms=4)
    ax.annotate(f'minimum {fp:.2f} at v = VaR = 100', xy=(vp, fp), xytext=(8, -16), textcoords='offset points',
                fontsize=9, color=IDAred)
    ax.text(40, 92, 'slope -0.3951', fontsize=9, color=IDAred, ha='center')
    ax.text(185, 150, 'slope 0.9951', fontsize=9, color=IDAred, ha='left')
    ax.set_xlabel(r'$v$')
    ax.set_ylabel(r'$F(v)$')
    ax.set_ylim(70, 250)
    ax.set_xlim(-10, 220)
    bottom_legend(fig, ncol=2)
    save_fig('ch7_sem_a7_ru')
    return dict(fmin=fp, s1=1 - (1 - (1 - p) ** 2) / alpha, s2=1 - p ** 2 / alpha, fa_min=2 * (0 + 100 * p / alpha))


def fig_a8_sim(R=4000, alpha=0.025, seed=SEED):
    """A8 / B6: sampling distribution of the historical ES 2.5%, Monte Carlo simulation (i.i.d.) vs asymptotic SE."""
    _style()
    rng = np.random.default_rng(seed)
    sig, nu = 1.2, 4
    s_t = sig * np.sqrt((nu - 2) / nu)
    v_n = sig * stats.norm.ppf(1 - alpha)
    es_n = sig * stats.norm.pdf(stats.norm.ppf(1 - alpha)) / alpha
    q_t = stats.t.ppf(1 - alpha, nu)
    v_t = s_t * q_t
    es_t = s_t * stats.t.pdf(q_t, nu) / alpha * (nu + q_t ** 2) / (nu - 1)
    # asymptotic variance Var((L - v)+)/alpha^2, by numerical integration
    from scipy import integrate as _int
    def avar(pdf, v, lim):
        m1 = _int.quad(lambda x: (x - v) * pdf(x), v, lim, limit=400)[0]
        m2 = _int.quad(lambda x: (x - v) ** 2 * pdf(x), v, lim, limit=400)[0]
        return (m2 - m1 ** 2) / alpha ** 2
    av_n = avar(lambda x: stats.norm.pdf(x, 0, sig), v_n, np.inf)
    av_t = avar(lambda x: stats.t.pdf(x / s_t, nu) / s_t, v_t, np.inf)
    ns = [250, 500, 1000, 2500, 5000]
    sd_n, sd_t, draws = [], [], {}
    for n in ns:
        en = np.array([hs_var_es(rng.normal(0, sig, n), alpha)[1] for _ in range(R)])
        et = np.array([hs_var_es(s_t * rng.standard_t(nu, n), alpha)[1] for _ in range(R)])
        sd_n.append(en.std(ddof=1))
        sd_t.append(et.std(ddof=1))
        if n == 500:
            draws = dict(n=en, t=et)
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.3))
    ax = axes[0]
    bins = np.linspace(1.5, 5.0, 60)
    ax.hist(draws['n'], bins=bins, density=True, color=MainBlue, alpha=0.5, label='Normal distribution')
    ax.hist(draws['t'], bins=bins, density=True, color=IDAred, alpha=0.5, label='Student-t, 4 df')
    xx = np.linspace(1.5, 5.0, 300)
    ax.plot(xx, stats.norm.pdf(xx, es_n, np.sqrt(av_n / 500)), color=MainBlue, lw=1.2, label='Asymptotic Normal law')
    ax.axvline(es_n, color=MainBlue, lw=0.8, ls='--')
    ax.axvline(es_t, color=IDAred, lw=0.8, ls='--')
    ax.set_xlabel('Historical ES 2.5% (%), n = 500')
    ax.set_ylabel('Density')
    ax.set_title(f'{R} simulated samples')
    ax = axes[1]
    ax.loglog(ns, sd_n, 'o', color=MainBlue, ms=4)
    ax.loglog(ns, sd_t, 's', color=IDAred, ms=4)
    nn = np.array([200, 6000])
    ax.loglog(nn, np.sqrt(av_n / nn), color=MainBlue, lw=0.9)
    ax.loglog(nn, np.sqrt(av_t / nn), color=IDAred, lw=0.9, ls='--')
    ax.plot([], [], 'o', color='black', ms=4, label='Simulated SD')
    ax.plot([], [], color='black', lw=0.9, label='Asymptotic SE')
    ax.set_xlabel('Sample size n')
    ax.set_ylabel('SD of ES estimate (pp)')
    ax.set_title('Precision grows like sqrt(n)')
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_a8_sim')
    i5 = ns.index(500)
    return dict(R=R, es_n=es_n, es_t=es_t, se_n500=float(np.sqrt(av_n / 500)), se_t500=float(np.sqrt(av_t / 500)),
                sd_n500=float(sd_n[i5]), sd_t500=float(sd_t[i5]), sd_n5000=float(sd_n[-1]),
                se_n5000=float(np.sqrt(av_n / 5000)), mean_n500=float(draws['n'].mean()), mean_t500=float(draws['t'].mean()))


def _ci_panel(ax, rows, title, xlab, band=None):
    """Point-and-interval chart; rows = (label, estimate, lo, hi, colour, text on the right)."""
    for i, (lab, est, lo, hi, c, txt) in enumerate(rows):
        y = len(rows) - 1 - i
        if band is not None:
            ax.fill_betweenx([y - 0.3, y + 0.3], est - band, est + band, color=Amber, alpha=0.25, lw=0)
        ax.plot([lo, hi], [y, y], color=c, lw=2.2, solid_capstyle='butt')
        ax.plot([est], [y], 'o', color=c, ms=4.5)
        if txt:
            ax.text(hi + 0.04, y, txt, va='center', fontsize=9, color='black')
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=9)
    ax.set_xlabel(xlab)
    ax.set_title(title)


def fig_b1_ci(B1, SX):
    """B1: 95% intervals for the BET VaR 1% on two samples and four methods."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(W_FIG, 2.35), sharex=True)
    for ax, k, t in [(axes[0], 'full', f"2000-2026 ({B1['full']['n_beyond']} beyond VaR)"),
                     (axes[1], 'w500', f"Last 500 days ({B1['w500']['n_beyond']} beyond)")]:
        b, s = B1[k], SX[f'b1_{k}']
        rows = [('i.i.d. bootstrap', b['var1'], b['ci_lo'], b['ci_hi'], MainBlue, f"{b['ci_hi'] - b['ci_lo']:.2f}"),
                ('Block bootstrap', b['var1'], s['blk_lo'], s['blk_hi'], IDAred, f"{s['blk_hi'] - s['blk_lo']:.2f}"),
                ('Asymptotic i.i.d.', b['var1'], s['lo'], s['hi'], Teal, f"{s['hi'] - s['lo']:.2f}"),
                ('Asymptotic HAC', b['var1'], s['lo_hac'], s['hi_hac'], Purple, f"{s['hi_hac'] - s['lo_hac']:.2f}")]
        _ci_panel(ax, rows, t, 'VaR 1% of BET (%)')
    axes[1].set_yticklabels([])
    axes[0].set_xlim(1.8, 5.3)
    fig.text(0.5, -0.02, 'Dot: historical VaR 1%; bar: 95% interval; number: interval width in percentage points',
             ha='center', fontsize=9, color='black')
    plt.tight_layout()
    save_fig('ch7_sem_b1_ci')


def es_replicate_example(L, alpha=0.025, block=20, seed=SEED):
    """A single bootstrap resample (i.i.d. and by blocks), with VaR and tail membership recomputed."""
    rng = np.random.default_rng(seed)
    L = np.asarray(L)
    n = len(L)
    out = {}
    x = L[rng.integers(0, n, n)]
    v, e = hs_var_es(x, alpha)
    out['iid'] = dict(var=v, es=e, k=int((x >= v).sum()))
    starts = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
    x = np.concatenate([L[s:s + block] for s in starts])[:n]
    v, e = hs_var_es(x, alpha)
    out['blk'] = dict(var=v, es=e, k=int((x >= v).sum()), nblocks=int(len(starts)), first_starts=[int(s) for s in starts[:3]])
    v0, e0 = hs_var_es(L, alpha)
    out['orig'] = dict(var=v0, es=e0, k=int((L >= v0).sum()), nalpha=n * alpha)
    return out


def fig_b6_ci(B6):
    """B6: 95% intervals for ES 2.5% (i.i.d. vs blocks), with a band of +/-0.3 percentage points."""
    _style()
    fig, ax = plt.subplots(figsize=(W_FIG, 2.6))
    labs = {'sp500_full': 'S&P 500, 2000-2026', 'sp500_w500': 'S&P 500, last 500', 'bet_full': 'BET, 2000-2026',
            'bet_w500': 'BET, last 500'}
    rows = []
    for k in ['sp500_full', 'sp500_w500', 'bet_full', 'bet_w500']:
        b = B6[k]
        rows.append((labs[k] + ', i.i.d.', b['es'], b['iid_lo'], b['iid_hi'], MainBlue, f"{b['iid_hi'] - b['iid_lo']:.2f}"))
        rows.append((labs[k] + ', blocks', b['es'], b['blk_lo'], b['blk_hi'], IDAred, f"{b['blk_hi'] - b['blk_lo']:.2f}"))
    _ci_panel(ax, rows, '', 'ES 2.5% (%): dot = estimate, bar = 95% bootstrap interval', band=0.3)
    ax.fill_between([], [], color=Amber, alpha=0.25, label='Target precision: estimate +/- 0.3 pp')
    ax.plot([], [], color=MainBlue, lw=2.2, label='i.i.d. bootstrap')
    ax.plot([], [], color=IDAred, lw=2.2, label='Moving-block bootstrap, 20 days')
    ax.set_xlim(1.6, 5.8)
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_b6_ci')


def clusters_bet(L, tail=0.05):
    """Threshold exceedances, clusters (Ferro & Segers, 2003, tie rule) and cluster maxima."""
    L = np.asarray(L, float)
    u = np.quantile(L, 1 - tail)
    S = np.flatnonzero(L > u)
    T = np.diff(S).astype(float)
    N = len(S)
    th = min(1.0, 2 * (T - 1).sum() ** 2 / ((N - 1) * ((T - 1) * (T - 2)).sum()))
    C = min(int(np.floor(th * N)) + 1, N)
    cut = np.sort(T)[::-1][C - 2]
    breaks = np.flatnonzero(T > cut) if np.sum(T >= cut) > C - 1 else np.flatnonzero(T >= cut)
    groups = np.split(np.arange(N), breaks + 1)
    return u, S, groups, th, cut


def fig_b2_ext():
    """B2 Extended: timeline of exceedances and clusters, mean excess, stability of VaR 0.1% across thresholds."""
    _style()
    Ls = -100 * log_returns('bet')
    L = Ls.values
    u, S, groups, th, cut = clusters_bet(L)
    fig = plt.figure(figsize=(W_FIG, 3.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1])
    ax = fig.add_subplot(gs[0, :])
    dates = Ls.index[S]
    cols = [MainBlue, Teal]
    for j, g in enumerate(groups):
        ax.plot(dates[g], L[S[g]], 'o', ms=2.2, color=cols[j % 2], label='Exceedances (clusters alternate colour)' if j == 0 else None)
        m = g[np.argmax(L[S[g]])]
        ax.plot(dates[m], L[S[m]], 'o', ms=3.4, mfc='none', mec=IDAred, mew=0.8,
                label='Cluster maximum' if j == 0 else None)
    ax.axhline(u, color=Gray, lw=0.6, ls='--')
    ax.set_ylabel('Loss (%)')
    ax.set_title(f'BET losses above u = {u:.2f}%: {len(S)} exceedances, {len(groups)} clusters')
    ax2 = fig.add_subplot(gs[1, 0])
    us = np.quantile(L, np.linspace(0.80, 0.995, 40))
    me, cnt = mean_excess(L, us)
    ax2.plot(us, me, 'o', ms=2.5, color=Forest, label='Empirical mean excess')
    ax2.axvline(u, color=Gray, lw=0.6, ls='--')
    ax2.set_xlabel('Threshold u (%)')
    ax2.set_ylabel('Mean excess (%)')
    ax2.set_title('Mean excess plot')
    ax3 = fig.add_subplot(gs[1, 1])
    qs = np.linspace(0.10, 0.015, 18)
    v01 = [gpd_var_es(gpd_fit(L, q), 0.001)[0] for q in qs]
    ax3.plot(100 * qs, v01, 'o-', ms=2.5, color=IDAred, label='GPD VaR 0.1%')
    ax3.axhline(hs_var_es(L, 0.001)[0], color=Gray, lw=0.6, ls=':')
    ax3.set_xlabel('Share of losses above u (%)')
    ax3.set_ylabel('VaR 0.1% (%)')
    ax3.set_title('Extreme quantile vs threshold')
    ax3.set_ylim(8, 10.5)
    bottom_legend(fig, ncol=4, fontsize=9.5)
    save_fig('ch7_sem_b2_clusters')
    sizes = np.array([len(g) for g in groups])
    return dict(u=u, N=int(len(S)), n_clusters=int(len(groups)), theta=th, cut=float(cut), max_size=int(sizes.max()),
                n_single=int((sizes == 1).sum()), hs_var01=float(hs_var_es(L, 0.001)[0]))


def fig_btc_fhs3(B3):
    """B3: Bitcoin losses, 500-day HS VaR and FHS VaR with exceedances; conditional volatility; ACF of z^2."""
    _style()
    r = 100 * log_returns('btc')
    params, mu, sig = garch_filter(r)
    z = ((r - mu) / sig).dropna()
    roll = pd.read_csv(os.path.join(HERE, 'ch7_rolling_btc.csv'), index_col=0, parse_dates=True)
    rec = roll.loc['2024-09-18':]
    fig = plt.figure(figsize=(W_FIG, 3.5))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1])
    ax = fig.add_subplot(gs[0, :])
    ax.bar(rec.index, rec['loss'].clip(lower=0), width=1, color=Teal, alpha=0.55, label='Daily loss (gains set to 0)')
    ax.plot(rec.index, rec['hs_var'], color=MainBlue, lw=1.0, label='HS VaR 1% (rolling 500 days)')
    ax.plot(rec.index, rec['fhs_var'], color=IDAred, lw=0.8, label='FHS VaR 1%')
    bh = rec[rec['loss'] > rec['hs_var']]
    bf = rec[rec['loss'] > rec['fhs_var']]
    ax.plot(bh.index, bh['loss'] + 0.6, 'v', ms=4, color=MainBlue, label=f'HS exceedance ({len(bh)})')
    ax.plot(bf.index, bf['loss'] + 1.6, 'v', ms=4, color=IDAred, label=f'FHS exceedance ({len(bf)})')
    ax.set_ylabel('Loss (%)')
    ax.set_title('Bitcoin, 18 Sep 2024 - 18 Sep 2026: one-day-ahead VaR 1%')
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(sig.loc['2017':].index, sig.loc['2017':].values, color=Purple, lw=0.7, label=r'GARCH volatility $\sigma_t$')
    ax2.set_ylabel(r'$\sigma_t$ (%)')
    import matplotlib.dates as mdates
    ax2.xaxis.set_major_locator(mdates.YearLocator(3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.set_title('Conditional volatility')
    ax3 = fig.add_subplot(gs[1, 1])
    zz = z.values ** 2 - (z.values ** 2).mean()
    lags = np.arange(1, 21)
    acf2 = [np.corrcoef(zz[k:], zz[:-k])[0, 1] for k in lags]
    rr2 = (r.values - r.values.mean()) ** 2
    acf_raw = [np.corrcoef(rr2[k:], rr2[:-k])[0, 1] for k in lags]
    ax3.bar(lags - 0.2, acf_raw, 0.38, color=Orange, label='ACF of squared returns')
    ax3.bar(lags + 0.2, acf2, 0.38, color=Forest, label=r'ACF of squared residuals $\hat z_t^2$')
    band = 1.96 / np.sqrt(len(zz))
    ax3.axhspan(-band, band, color=LightGray, alpha=0.6, lw=0)
    ax3.set_xlabel('Lag (days)')
    ax3.set_title('Clustering removed?')
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_btc_fhs')
    return dict(n_hs=int(len(bh)), n_fhs=int(len(bf)), acf1_raw=float(acf_raw[0]), acf1_z=float(acf2[0]),
                max_acf_z=float(np.max(np.abs(acf2))), band=float(band), n_z=int(len(zz)))


def fig_b3_boot(draws, B3, boot):
    """B3 Extended: bootstrap distribution of tomorrow's FHS VaR 1% for Bitcoin."""
    _style()
    fig, ax = plt.subplots(figsize=(W_FIG * 0.85, 2.2))
    ax.hist(draws, bins=45, color=IDAred, alpha=0.55, label=f'{len(draws)} bootstrap forecasts')
    ax.axvspan(boot['lo'], boot['hi'], color=Amber, alpha=0.2, lw=0, label='90% percentile interval')
    ax.axvline(B3['fhs_var'], color=IDAred, lw=1.2, label=f"FHS VaR 1% = {B3['fhs_var']:.2f}%")
    ax.axvline(B3['hs500_var'], color=MainBlue, lw=1.2, ls='--', label=f"HS 500 days = {B3['hs500_var']:.2f}% (unconditional)")
    ax.set_xlabel('VaR 1% for 19 September 2026 (%)')
    ax.set_ylabel('Count')
    bottom_legend(fig, ncol=2, fontsize=9.5)
    save_fig('ch7_sem_b3_boot')


def fig_b4_methods(B4, B=1000):
    """B4: historical VaR with a bootstrap interval, Normal and Cornish-Fisher, by asset and level."""
    _style()
    keys = ['sp500', 'bet', 'btc', 'eurron', 'gold']
    labs = {'sp500': 'S&P 500', 'bet': 'BET', 'btc': 'Bitcoin', 'eurron': 'EUR/RON', 'gold': 'Gold'}
    ci25 = {}
    for k in keys:
        L = (-100 * log_returns(k)).values
        ci25[k] = boot_ci(L, lambda y: hs_var_es(y, 0.025)[0], B=B)[0]
    fig, axes = plt.subplots(1, 5, figsize=(W_FIG, 2.4))
    for ax, k in zip(axes, keys):
        b = B4[k]
        for j, (lvl, hs, lo, hi, n, cf) in enumerate([('1%', b['hs1'], b['ci_lo'], b['ci_hi'], b['n1'], b['cf1']),
                                                       ('2.5%', b['hs2_5'], ci25[k][0], ci25[k][1], b['n2_5'], b['cf2_5'])]):
            x = j
            ax.plot([x, x], [lo, hi], color=MainBlue, lw=2.4, solid_capstyle='butt')
            ax.plot([x], [hs], 'o', color=MainBlue, ms=4, label='Historical, 95% bootstrap CI' if (k == 'sp500' and j == 0) else None)
            ax.plot([x + 0.18], [n], 's', color=Orange, ms=3.5, label='Normal distribution' if (k == 'sp500' and j == 0) else None)
            ax.plot([x - 0.18], [cf], 'D', color=Purple, ms=3.5, label='Cornish-Fisher' if (k == 'sp500' and j == 0) else None)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['1%', '2.5%'], fontsize=9)
        ax.set_xlim(-0.5, 1.5)
        ax.set_title(labs[k], fontsize=9.5)
        ax.tick_params(axis='y', labelsize=7)
    axes[0].set_ylabel('Daily VaR (%)')
    axes[2].set_xlabel('Tail probability of VaR')
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_b4_methods')
    return {k: dict(lo=float(v[0]), hi=float(v[1])) for k, v in ci25.items()}


def fig_b7_caviar(CV):
    """B7: BET losses 2016-2026 with CAViaR, FHS and HS VaR; the COVID-19 window."""
    _style()
    try:
        from estimation_risk import caviar_path as _cp, pinball as _pb
    except ImportError:                              # in the Quantlet notebook these functions are already defined
        _cp, _pb = globals()['caviar_path'], globals()['pinball']
    r = 100 * log_returns('bet')
    v0 = -np.quantile(r.loc[:'2015-12-31'].values[:300], 0.01)
    v = pd.Series(_cp([CV['b0'], CV['b1'], CV['b2']], r.values, v0), index=r.index)
    fhs = rolling_conditional_bet()
    d = fhs.loc['2016-01-01':]
    L = d['loss']
    fig, axes = plt.subplots(2, 1, figsize=(W_FIG, 3.4), gridspec_kw={'height_ratios': [1.1, 1]})
    for ax, dd, ttl in [(axes[0], d, 'BET, 2016-2026: one-day-ahead VaR 1% out of sample'),
                        (axes[1], d.loc['2020-02-20':'2020-04-30'], 'COVID-19 window, 20 Feb - 30 Apr 2020')]:
        ax.bar(dd.index, dd['loss'].clip(lower=0), width=1 if ax is axes[1] else 2, color=Teal, alpha=0.55,
               label='Daily loss (gains set to 0)')
        ax.plot(dd.index, v.loc[dd.index], color=MainBlue, lw=0.9, label='CAViaR (SAV), parameters 2000-2015')
        ax.plot(dd.index, dd['fhs_var'], color=IDAred, lw=0.8, label='FHS, re-estimated every January')
        ax.plot(dd.index, dd['hs_var'], color=Orange, lw=0.9, label='HS, rolling 500 days')
        br = dd[dd['loss'] > v.loc[dd.index]]
        ax.plot(br.index, br['loss'] + 0.5, 'v', ms=3.5, color=MainBlue, label='CAViaR exceedance')
        ax.set_ylabel('Loss (%)')
        ax.set_title(ttl)
    bottom_legend(fig, ncol=3, fontsize=9.5)
    save_fig('ch7_sem_b7_caviar')
    return dict(n_hit_caviar=int((L > v.loc[d.index]).sum()), n_hit_fhs=int((L > d['fhs_var']).sum()),
                n_hit_hs=int((L > d['hs_var']).sum()), pin_caviar=float(_pb(-L.values, -v.loc[d.index].values, 0.01)),
                v0=float(v0), day1=str(d.index[0].date()), r1=float(-L.iloc[0]), v1=float(v.loc[d.index[0]]),
                rprev=float(r.iloc[r.index.get_loc(d.index[0]) - 1]), vprev=float(v.iloc[r.index.get_loc(d.index[0]) - 1]),
                term1=float((0.01 - (-L.iloc[0] < -v.loc[d.index[0]])) * (-L.iloc[0] + v.loc[d.index[0]])))


def rolling_conditional_bet():
    return rolling_conditional(100 * log_returns('bet'), 2016)


def c1_series():
    """The C1 portfolios (same code as c1_capital): daily simple returns in %."""
    lr_b = joint_returns(BVB, start=C_START)
    lr_b = lr_b[(lr_b != 0).any(axis=1)]
    start = str(lr_b.index[0].date())
    Rb = 100 * (np.exp(lr_b) - 1)
    Rp_b = Rb.mean(axis=1)
    Rp_s = 100 * (np.exp(joint_returns(['SPY']).loc[start:]['SPY']) - 1)
    return {'bvb': Rp_b, 'spy': Rp_s}


def fig_c1_stress(C1):
    """C1: historical ES 2.5% on rolling 250-day windows; the chosen stress windows (hatched)."""
    _style()
    ser = c1_series()
    es25 = lambda y: hs_var_es(y, 0.025)[1]   # noqa: E731
    fig, ax = plt.subplots(figsize=(W_FIG, 2.4))
    out = {}
    for k, c, lab in [('bvb', IDAred, 'BVB blue chips, equal weights'), ('spy', MainBlue, 'S&P 500 (SPY)')]:
        L = -ser[k]
        roll = pd.Series([es25(L.iloc[i - 250:i].values) for i in range(250, len(L) + 1)], index=L.index[249:])
        ax.plot(roll.index, roll.values, color=c, lw=1.0, label=f'{lab}: rolling 250-day ES 2.5%')
        a, b = pd.Timestamp(C1[k]['stress_from']), pd.Timestamp(C1[k]['stress_to'])
        ax.axvspan(a, b, color=c, alpha=0.12, lw=0, label=f'Stress window, {lab.split(",")[0].split(" (")[0]}')
        out[k] = dict(max=float(roll.max()), argmax=str(roll.idxmax().date()), last=float(roll.iloc[-1]))
    ax.set_ylabel('1-day ES 2.5% (%)')
    ax.set_title('Stress-window selection, 2017-2026')
    bottom_legend(fig, ncol=2, fontsize=9.5)
    save_fig('ch7_sem_c1_stress')
    return out


def fig_c2_horizon(B1):
    """C2: survival functions of one-day and overlapping 10-day BET losses; correct and wrong VaR 1%."""
    _style()
    r = 100 * log_returns('bet')
    L1 = (-r).values
    L10 = (-r.rolling(10).sum()).dropna().values
    v1 = np.quantile(L1, 0.99)
    v10 = np.quantile(L10, 0.99)
    fig, ax = plt.subplots(figsize=(W_FIG * 0.9, 2.4))
    for x, c, lab in [(L1, MainBlue, 'One-day log losses'), (L10, IDAred, 'Overlapping 10-day log losses')]:
        xs = np.sort(x)
        sf = 1 - np.arange(1, len(xs) + 1) / len(xs)
        m = sf > 0
        ax.semilogy(xs[m], sf[m], color=c, lw=1.1, label=lab)
    ax.axhline(0.01, color=Gray, lw=0.6, ls=':')
    marks = [(v1, MainBlue, '-', f'VaR 1%, 1 day: {v1:.2f}'), (np.sqrt(10) * v1, Forest, '--', f'sqrt(10) x VaR: {np.sqrt(10) * v1:.2f}'),
             (v10, IDAred, '-', f'VaR 1%, 10 days: {v10:.2f}'), (10 * 3.945843614767814, Purple, ':', 'AI answer: 10 x VaR = 39.46')]
    for v, c, ls, lab in marks:
        ax.axvline(v, color=c, ls=ls, lw=1.0, label=lab)
    ax.set_xlim(0, 42)
    ax.set_ylim(1e-4, 1)
    ax.set_xlabel('Loss x (%)')
    ax.set_ylabel('P(loss > x)')
    bottom_legend(fig, ncol=2, fontsize=9.5)
    save_fig('ch7_sem_c2_horizon')
    return dict(v1=v1, v10=v10, sqrt=np.sqrt(10) * v1, max10=float(L10.max()), n10=int(len(L10)),
                n_beyond10=int((L10 >= v10).sum()), es25=hs_var_es(L1, 0.025)[1], k25=int((L1 >= np.quantile(L1, 0.975)).sum()),
                k1=int((L1 >= v1).sum()))


def fig_c3_design():
    """C3: sample split (tuning / evaluation), cross-validation points with their exclusion windows, alignment t -> t + 10."""
    _style()
    r = log_returns('sp500', start='1990-01-01', end='2020-08-31')
    split = r.index[-2000]
    rng = np.random.default_rng(SEED)
    tune = r.loc[:split].iloc[:-1]
    cv = np.sort(rng.choice(np.arange(5, len(tune) - 5), 20, replace=False))
    fig, axes = plt.subplots(2, 1, figsize=(W_FIG, 2.9), gridspec_kw={'height_ratios': [1.2, 0.8]})
    ax = axes[0]
    ax.plot(tune.index, 100 * tune.values, color=MainBlue, lw=0.4, label=f'Tuning sample ({len(tune):,} days)')
    ev = r.loc[split:]
    ax.plot(ev.index, 100 * ev.values, color=IDAred, lw=0.4, label=f'Evaluation sample (last {len(ev):,} days)')
    for i in cv:
        ax.axvspan(tune.index[i - 5], tune.index[i + 5], color=Amber, alpha=0.5, lw=0)
    ax.plot([], [], color=Amber, lw=4, alpha=0.5, label='Cross-validation: 20 random test days, each with ±5 neighbouring days excluded')
    ax.set_ylabel('Log return (%)')
    ax.set_title(f'S&P 500, Jan 1990 - Aug 2020; evaluation from {split.date()}')
    ax = axes[1]
    ax.set_xlim(-1.5, 12)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.plot([-0.5, 11], [0.5, 0.5], color='black', lw=0.6)
    for t in range(0, 11):
        ax.plot([t, t], [0.46, 0.54], color='black', lw=0.6)
    ax.text(0, 0.36, '$t$', ha='center', fontsize=9, color='black')
    ax.text(1, 0.36, '$t+1$', ha='center', fontsize=9, color='black')
    ax.text(10, 0.36, '$t+10$', ha='center', fontsize=9, color='black')
    ax.annotate('', xy=(10, 0.66), xytext=(0, 0.66), arrowprops=dict(arrowstyle='->', color=Forest, lw=1.2))
    ax.text(5, 0.74, r'target: the daily return $r_{t+10}$, predicted from $x_t$', ha='center', fontsize=9, color=Forest)
    ax.plot([1, 1, 10, 10], [0.24, 0.18, 0.18, 0.24], color=Purple, lw=1.0)
    ax.text(5.5, 0.03, r'$r_{t+1} + \dots + r_{t+10}$: cumulative 10-day return, a different target', ha='center',
            fontsize=9, color=Purple)
    ax.text(-1.4, 0.92, 'Alignment of one training pair', fontsize=9, color='black')
    bottom_legend(fig, ncol=2, fontsize=9.5)
    save_fig('ch7_sem_c3_design')
    return dict(split=str(split.date()), n_tune=int(len(tune)), n_eval=int(len(ev)), first=str(r.index[0].date()))


def fig_b5_rp(B5, RP):
    """B5 Extended: risk-parity weights (Normal VaR) vs 1/sigma and the resulting risk shares."""
    _style()
    names = ['SPY', 'TLT', 'GLD', 'Bitcoin']
    xx = np.arange(4)
    fig, ax = plt.subplots(figsize=(W_FIG * 0.85, 2.3))
    for k, (vals, c, lab) in enumerate([(100 * np.array(RP['w_rp']), MainBlue, 'Risk-parity weight'),
                                        (100 * np.array(RP['inv_vol']), Teal, 'Inverse-volatility weight'),
                                        (100 * np.array(RP['ces_rp_share']), IDAred, 'Share of historical ES 2.5% at risk parity')]):
        ax.bar(xx + (k - 1) * 0.27, vals, 0.25, color=c, label=lab)
        for i in range(4):
            ax.text(xx[i] + (k - 1) * 0.27, vals[i] + 0.8, f'{vals[i]:.0f}', ha='center', fontsize=9, color='black')
    ax.axhline(25, color=Gray, lw=0.6, ls=':')
    ax.set_xticks(xx)
    ax.set_xticklabels(names)
    ax.set_ylabel('%')
    ax.set_ylim(0, 45)
    bottom_legend(fig, ncol=2, fontsize=9.5)
    save_fig('ch7_sem_b5_rp')


def extra_numbers(S):
    """Extra numbers for the solution steps (computed from the data)."""
    out = {}
    L = -100 * log_returns('bet')
    x = np.sort(L.iloc[-500:].values)
    n = len(x)
    pos = 1 + (n - 1) * 0.99                          # (1-indexed) position of the interpolated quantile
    lo = int(np.floor(pos))
    out['b1_w500'] = dict(pos=pos, l_lo=float(x[lo - 1]), l_hi=float(x[lo]), top5=[float(v) for v in x[-5:][::-1]],
                          var=float(np.quantile(x, 0.99)))
    xf = np.sort(L.values)
    posf = 1 + (len(xf) - 1) * 0.99
    out['b1_full'] = dict(pos=posf, l_lo=float(xf[int(np.floor(posf)) - 1]), l_hi=float(xf[int(np.floor(posf))]))
    # k for ES 2.5% on the four samples of B6
    ks = {}
    for k in ['sp500', 'bet']:
        Lk = (-100 * log_returns(k)).values
        for tag, xx in [('full', Lk), ('w500', Lk[-500:])]:
            v = np.quantile(xx, 0.975)
            ks[f'{k}_{tag}'] = dict(nalpha=0.025 * len(xx), k=int((xx >= v).sum()))
    out['b6_k'] = ks
    # B5: worst day of the equally weighted portfolio and its contributions
    lr = joint_returns(['SPY', 'TLT', 'GLD', 'BTC'], start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)
    Lp = -(R.values @ np.full(4, 0.25))
    i = int(np.argmax(Lp))
    out['b5_worst'] = dict(date=str(R.index[i].date()), Lp=float(Lp[i]), comp=[float(-0.25 * v) for v in R.values[i]])
    v25, e25 = hs_var_es(Lp, 0.025)
    out['b5_tail'] = dict(k=int((Lp >= v25).sum()), var=float(v25))
    # C1: number of tail losses in the stress windows and over ten years
    ser = c1_series()
    c1 = {}
    for k in ['bvb', 'spy']:
        Lk = -ser[k]
        a, b = pd.Timestamp(S['C1'][k]['stress_from']), pd.Timestamp(S['C1'][k]['stress_to'])
        Ls = Lk.loc[a:b].values
        v = np.quantile(Ls, 0.975)
        v1 = np.quantile(Lk.values, 0.975)
        c1[k] = dict(n_stress=int(len(Ls)), k_stress=int((Ls >= v).sum()), k_full=int((Lk.values >= v1).sum()),
                     n=int(len(Lk)))
    out['c1'] = c1
    # A1: the step-by-step table (already in S['A1']); A4: the probabilities
    return out


def run_charts():
    with open(os.path.join(HERE, 'sem7_results.json')) as f:
        S = json.load(f)
    with open(os.path.join(HERE, 'ch7_inference.json')) as f:
        INF = json.load(f)
    X = S.get('X', {})
    X['bet_data'] = fig_bet_data()
    fig_a1a2_tails(S['A1'], S['A2'])
    fig_a3_mass()
    X['a4'] = fig_a4_var_alpha()
    fig_a5_shares(S['A5'])
    X['b5'] = fig_b5_shares(S['B5'])
    fig_a6_cf()
    X['a7'] = fig_a7_ru()
    X['a8'] = fig_a8_sim()
    fig_b1_ci(S['B1'], INF['sem'])
    fig_b6_ci(S['B6'])
    L = (-100 * log_returns('sp500')).values
    X['b6_rep_sp500'] = es_replicate_example(L[-500:])
    X['b2x'] = fig_b2_ext()
    X['b3'] = fig_btc_fhs3(S['B3'])
    X['b4_ci25'] = fig_b4_methods(S['B4'])
    X['b7'] = fig_b7_caviar(INF['caviar_bet'])
    X['c1'] = fig_c1_stress(S['C1'])
    X['c2'] = fig_c2_horizon(S['B1'])
    X['c3'] = fig_c3_design()
    fig_b5_rp(S['B5'], X['b5'])
    X.update(extra_numbers(S))
    bt = os.path.join(HERE, 'ch7_btc_boot.csv')
    if os.path.exists(bt):
        draws = pd.read_csv(bt)['var'].values
        fig_b3_boot(draws, S['B3'], INF['fhs_boot_btc'])
    S['X'] = X
    with open(os.path.join(HERE, 'sem7_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print(json.dumps(jsonable(X), indent=1)[:6000])


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'charts':
    run_charts()
elif __name__ == '__main__':
    S = dict(A1=a1_normal(), A2=a2_student(), A3=a3_bond(), A4=a4_bonds(), A5=a5_components(), A6=a6_cf())
    S['B1'] = b1_bet_hs()
    S['B2'] = b2_bet_gpd()
    S['B3'] = b3_btc_fhs()
    S['B4'] = b4_cf_vs_empirical()
    S['B5'] = b5_components()
    S['B6'] = b6_es_boot()
    S['C1'] = c1_capital()
    with open(os.path.join(HERE, 'sem7_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print(json.dumps(jsonable(S), indent=1)[:12000])

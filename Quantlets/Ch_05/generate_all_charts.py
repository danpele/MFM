"""
Charts of Chapter 5: Conditional Volatility, GARCH Models
=========================================================
All charts: transparent background, English labels, legend outside, at the bottom.
Daily data: S&P 500, BET (2000-2026), BET-TR (2014-2026), Bitcoin (2014-2026), gold XAU/USD (2000-2026),
EUR/RON: the official BNR reference rate (July 2005-2026); the VIX for comparison.
Estimation: package arch (maximum likelihood, robust Bollerslev-Wooldridge standard errors).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from arch import arch_model
from arch.univariate import ARCHInMean, GARCH, FIGARCH, StudentsT, ZeroMean
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import MARKETS, LABELS, pct_returns, periods_per_year, load_vix   # noqa: E402
from garch_tools import (fit_garch, half_life, news_impact, sign_bias_test, ljung_box, arch_lm,  # noqa: E402
                         ewma_variance, qlike, mz_regression, dm_test, DISTS, VOL_SPEC)

# Chart style: transparent background, legend below the plot
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
# font sizes for slides (charts are 9-11 inches wide and shown at 8-14 cm)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 11.5
plt.rcParams['ytick.labelsize'] = 11.5
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.4
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 11

# Chart colours
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Navy     = '#1F2A44'   # reference lines (no grey in charts)
BandBlue = '#C5D2E8'   # light MainBlue tint for confidence / reference bands
Gray, LightGray = Navy, BandBlue   # legacy names kept for importing scripts
Teal     = '#17A2B8'
COL = {'sp500': MainBlue, 'bet': IDAred, 'bettr': Orange, 'btc': Amber, 'eurron': Forest, 'gold': Purple}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
TABLE_DIR = HERE
SEED = 42
NUM = {}


def save_fig(name):
    """Save the figure as transparent PDF and PNG."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Place the legend outside the plot, bottom centre."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def acf(x, nlags):
    x = np.asarray(x) - np.mean(x)
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, nlags + 1)])


# =============================================================================
# DATA
# =============================================================================
rets = {k: pct_returns(k) for k in MARKETS}
PPY = {k: periods_per_year(rets[k]) for k in MARKETS}
ORDER = list(MARKETS)
MAIN = ['sp500', 'bet', 'btc', 'eurron', 'gold']


# =============================================================================
# 1. ARCH EFFECTS IN RETURNS (before modelling)
# =============================================================================
def arch_effects_table():
    rows = []
    for k in ORDER:
        r = rets[k]
        q, qp = ljung_box(r ** 2, 10)
        q1, q1p = ljung_box(r, 10)
        lm, lmp = arch_lm(r - r.mean(), 5)
        rows.append(dict(market=k, label=LABELS[k], start=str(r.index[0].date()), N=len(r), ppy=PPY[k],
                         ann_vol=r.std() * np.sqrt(PPY[k]), kurt=stats.kurtosis(r), skew=stats.skew(r),
                         Q10_r=q1, Q10_r_p=q1p, Q10_r2=q, Q10_r2_p=qp, LM5=lm, LM5_p=lmp,
                         acf1_r2=acf(r ** 2, 1)[0], acf1_r=acf(r, 1)[0]))
    t = pd.DataFrame(rows).set_index('market')
    t.to_csv(os.path.join(TABLE_DIR, 'ch5_arch_effects.csv'))
    return t


def fig_clustering():
    fig, axes = plt.subplots(3, 1, figsize=(10, 5.6), sharex=False)
    for ax, k in zip(axes, ['sp500', 'bet', 'btc']):
        r = rets[k]
        ax.plot(r.index, r.values, color=COL[k], lw=0.45, label=f'{LABELS[k]} daily log return (%)')
        ax.set_ylabel('%')
        ax.axhline(0, color=Gray, lw=0.5)
    fig.tight_layout()
    h = [l for ax in axes for l in ax.get_lines() if not l.get_label().startswith('_')]
    fig.legend(h, [l.get_label() for l in h], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    save_fig('ch5_clustering')


def fig_acf_r_r2():
    r = rets['sp500']
    L = 50
    a1, a2 = acf(r, L), acf(r ** 2, L)
    fig, ax = plt.subplots(figsize=(9, 3.6))
    lags = np.arange(1, L + 1)
    ax.bar(lags - 0.2, a1, width=0.4, color=MainBlue, label='ACF of returns $r_t$')
    ax.bar(lags + 0.2, a2, width=0.4, color=IDAred, label='ACF of squared returns $r_t^2$')
    b = 1.96 / np.sqrt(len(r))
    ax.axhspan(-b, b, color=LightGray, alpha=0.6, label='95% band under i.i.d.')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag (trading days)')
    ax.set_ylabel('Autocorrelation')
    legend_outside_bottom(ax, ncol=3, y=-0.25)
    save_fig('ch5_acf_r_r2')
    NUM['acf_sp500'] = {'r_1': a1[0], 'r2_1': a2[0], 'r2_10': a2[9], 'r2_50': a2[49], 'band': b,
                        'n_r2_sig': int((np.abs(a2) > b).sum()), 'n_r_sig': int((np.abs(a1) > b).sum())}


# =============================================================================
# 2. ESTIMATION ON ALL SERIES
# =============================================================================
def model_grid():
    rows, fits = [], {}
    for k in ORDER:
        r = rets[k]
        for vol in VOL_SPEC:
            for dist in DISTS:
                f = fit_garch(r, vol, dist)
                fits[(k, vol, dist)] = f
                p = f.params
                rows.append(dict(market=k, vol=vol, dist=dist, loglik=f.loglik, aic=f.aic, bic=f.bic,
                                 k=len(p), converged=f.converged, persistence=f.persistence,
                                 **{f'p_{n}': v for n, v in p.items()}))
    g = pd.DataFrame(rows)
    g['dbic'] = g['bic'] - g.groupby('market')['bic'].transform('min')
    g.to_csv(os.path.join(TABLE_DIR, 'ch5_model_grid.csv'), index=False)
    return g, fits


def garch_table(fits):
    """GARCH(1,1)-t on each series: parameters, robust and classical errors, persistence, half-life."""
    rows = []
    for k in ORDER:
        f = fits[(k, 'GARCH', 't')]
        p, se = f.params, f.se
        classic = f.res.model.fit(disp='off', cov_type='classic', starting_values=f.res.params.values).std_err
        pers = p['alpha[1]'] + p['beta[1]']
        uv = f.uncond_var()
        rows.append(dict(market=k, mu=p['mu'], omega=p['omega'], alpha=p['alpha[1]'], beta=p['beta[1]'], nu=p['nu'],
                         se_alpha=se['alpha[1]'], se_beta=se['beta[1]'], se_nu=se['nu'],
                         se_alpha_classic=classic['alpha[1]'], se_beta_classic=classic['beta[1]'],
                         persistence=pers, half_life=half_life(pers),
                         uncond_ann_vol=np.sqrt(uv * PPY[k]) if pers < 0.999 else np.nan,
                         last_ann_vol=f.sigma.iloc[-1] * np.sqrt(PPY[k]), loglik=f.loglik, N=f.nobs, scale=f.c))
    t = pd.DataFrame(rows).set_index('market')
    t.to_csv(os.path.join(TABLE_DIR, 'ch5_garch_table.csv'))
    return t


def asym_table(fits):
    rows = []
    for k in ORDER:
        g, j, e = fits[(k, 'GARCH', 't')], fits[(k, 'GJR', 't')], fits[(k, 'EGARCH', 't')]
        lr = 2 * (j.loglik - g.loglik)
        rows.append(dict(market=k, gjr_alpha=j.params['alpha[1]'], gjr_gamma=j.params['gamma[1]'],
                         gjr_gamma_t=j.tvalues['gamma[1]'], gjr_beta=j.params['beta[1]'],
                         gjr_persistence=j.persistence, lr=lr, lr_p=1 - stats.chi2.cdf(lr, 1),
                         eg_alpha=e.params['alpha[1]'], eg_gamma=e.params['gamma[1]'], eg_gamma_t=e.tvalues['gamma[1]'],
                         eg_beta=e.params['beta[1]'], bic_garch=g.bic, bic_gjr=j.bic, bic_egarch=e.bic))
    t = pd.DataFrame(rows).set_index('market')
    t.to_csv(os.path.join(TABLE_DIR, 'ch5_asym_table.csv'))
    return t


# =============================================================================
# 3. SIMULATION: WHY GARCH PRODUCES VOLATILITY CLUSTERING
# =============================================================================
def fig_simulation():
    n = 2000
    rng = np.random.default_rng(SEED)
    om, al, be = 0.02, 0.10, 0.88
    s2 = np.empty(n)
    x = np.empty(n)
    s2[0] = om / (1 - al - be)
    z = rng.standard_normal(n)
    for t in range(n):
        if t > 0:
            s2[t] = om + al * x[t - 1] ** 2 + be * s2[t - 1]
        x[t] = np.sqrt(s2[t]) * z[t]
    iid = np.sqrt(om / (1 - al - be)) * rng.standard_normal(n)
    fig, axes = plt.subplots(2, 1, figsize=(10, 4.6), sharex=True, sharey=True)
    axes[0].plot(iid, color=Teal, lw=0.5, label='i.i.d. Normal, same unconditional variance')
    axes[1].plot(x, color=MainBlue, lw=0.5, label=r'GARCH(1,1): $\omega=0.02$, $\alpha=0.10$, $\beta=0.88$')
    axes[1].plot(2 * np.sqrt(s2), color=IDAred, lw=0.8, label=r'$\pm 2\sigma_t$')
    axes[1].plot(-2 * np.sqrt(s2), color=IDAred, lw=0.8)
    for ax in axes:
        ax.set_ylabel('Return (%)')
    axes[1].set_xlabel('Day')
    fig.tight_layout()
    h = [l for ax in axes for l in ax.get_lines() if not l.get_label().startswith('_')]
    fig.legend(h, [l.get_label() for l in h], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    save_fig('ch5_simulation')
    # statistics on a long path (one million days), not on the 2000 days of the chart
    N = 1_000_000
    zl = rng.standard_normal(N)
    xl = np.empty(N)
    s = om / (1 - al - be)
    for t in range(N):
        xl[t] = np.sqrt(s) * zl[t]
        s = om + al * xl[t] ** 2 + be * s
    NUM['sim'] = {'kurt_garch': float(stats.kurtosis(xl)), 'acf1_x2': float(acf(xl ** 2, 1)[0]),
                  'kurt_theory': float(3 * (1 - (al + be) ** 2) / (1 - (al + be) ** 2 - 2 * al ** 2) - 3),
                  'uvar': om / (1 - al - be)}


# =============================================================================
# 4. S&P 500: CONDITIONAL VOLATILITY AND THE VIX
# =============================================================================
def fig_sp500_vol(fits):
    f = fits[('sp500', 'GARCH', 't')]
    vol = f.sigma * np.sqrt(PPY['sp500'])
    vix = load_vix().reindex(vol.index).dropna()
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(vix.index, vix.values, color=Amber, lw=0.7, label='VIX (30-day implied volatility, % p.a.)')
    ax.plot(vol.index, vol.values, color=MainBlue, lw=0.7, label='GARCH(1,1)-t conditional volatility (% p.a.)')
    for d, lab in [('2008-10-15', 'Lehman'), ('2020-03-16', 'COVID-19'), ('2025-04-08', 'Tariffs')]:
        ax.annotate(lab, (pd.Timestamp(d), vol.loc[:d].iloc[-1]), xytext=(8, 0), textcoords='offset points',
                    fontsize=8, color='black')
    ax.set_ylabel('Annualised volatility (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    save_fig('ch5_sp500_vol')
    common = vol.reindex(vix.index)
    NUM['vix'] = {'corr': float(np.corrcoef(common, vix)[0, 1]), 'mean_vix': float(vix.mean()),
                  'mean_garch': float(common.mean()), 'max_garch': float(vol.max()), 'max_garch_date': str(vol.idxmax().date()),
                  'min_garch': float(vol.min()), 'min_garch_date': str(vol.idxmin().date()),
                  'share_vix_above': float((vix > common).mean())}


def fig_covid(fits):
    g, j = fits[('sp500', 'GARCH', 't')], fits[('sp500', 'GJR', 't')]
    a, b = '2020-01-15', '2020-07-31'
    ppy = np.sqrt(PPY['sp500'])
    vix = load_vix().loc[a:b]
    r = rets['sp500'].loc[a:b]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar(r.index, np.abs(r.values) * ppy, color=Teal, alpha=0.45, width=1.0, label=r'$|r_t|\sqrt{q}$ (% p.a.), $q$ = ' + f'{PPY["sp500"]:.1f}')
    ax.plot(g.sigma.loc[a:b] * ppy, color=MainBlue, label='GARCH(1,1)-t')
    ax.plot(j.sigma.loc[a:b] * ppy, color=IDAred, label='GJR-GARCH(1,1)-t')
    ax.plot(vix, color=Amber, label='VIX')
    ax.set_ylabel('Annualised volatility (%)')
    legend_outside_bottom(ax, ncol=4, y=-0.15)
    save_fig('ch5_covid')
    NUM['covid'] = {'garch_max': float(g.sigma.loc[a:b].max() * ppy), 'gjr_max': float(j.sigma.loc[a:b].max() * ppy),
                    'vix_max': float(vix.max()), 'vix_max_date': str(vix.idxmax().date()),
                    'garch_max_date': str(g.sigma.loc[a:b].idxmax().date()),
                    'rmin': float(r.min()), 'rmin_date': str(r.idxmin().date()),
                    'vix_0221': float(vix.loc['2020-02-21']), 'vix_0224': float(vix.loc['2020-02-24']),
                    'garch_0224': float(g.sigma.loc['2020-02-24'] * ppy), 'garch_0225': float(g.sigma.loc['2020-02-25'] * ppy),
                    'r_0224': float(rets['sp500'].loc['2020-02-24'])}


# =============================================================================
# 5. PERSISTENCE AND HALF-LIFE
# =============================================================================
def fig_persistence(gt):
    H = 250
    h = np.arange(0, H + 1)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    for k in MAIN + ['bettr']:
        pers = gt.loc[k, 'persistence']
        hl = gt.loc[k, 'half_life']
        lab = f'{LABELS[k]}: $\\alpha+\\beta$ = {pers:.4f}, half-life ' + (f'{hl:.0f} days' if np.isfinite(hl) and hl < 1e4 else '> 10000 days')
        ax.plot(h, pers ** h, color=COL[k], label=lab, ls='--' if k == 'btc' else '-')
    ax.axhline(0.5, color=Gray, lw=0.6, ls='--')
    ax.set_xlabel('Horizon $h$ (days)')
    ax.set_ylabel(r'Share of a variance shock left, $(\alpha+\beta)^h$')
    ax.set_ylim(0, 1.02)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch5_persistence')


# =============================================================================
# 6. ASYMMETRY: THE NEWS IMPACT CURVE
# =============================================================================
def fig_nic(fits):
    eps = np.linspace(-6, 6, 241)
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    for (vol, c, lab) in [('GARCH', MainBlue, 'GARCH(1,1)-t'), ('GJR', IDAred, 'GJR-GARCH(1,1)-t'),
                          ('EGARCH', Forest, 'EGARCH(1,1)-t')]:
        f = fits[('sp500', vol, 't')]
        ax.plot(eps, news_impact(f, eps), color=c, label=lab)
    ax.set_xlabel(r'Shock $\varepsilon_{t-1}$ (%)')
    ax.set_ylabel(r'Next-day variance $\sigma_t^2$ (%$^2$)')
    ax.axvline(0, color=Gray, lw=0.5)
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch5_nic')
    fj = fits[('sp500', 'GJR', 't')]
    s2 = rets['sp500'].var()
    NUM['nic'] = {'s2bar': float(s2), 'gjr_m3': float(news_impact(fj, np.array([-3.0]))[0]),
                  'gjr_p3': float(news_impact(fj, np.array([3.0]))[0]),
                  'eg_m3': float(news_impact(fits[('sp500', 'EGARCH', 't')], np.array([-3.0]))[0]),
                  'eg_p3': float(news_impact(fits[('sp500', 'EGARCH', 't')], np.array([3.0]))[0]),
                  'g_pm3': float(news_impact(fits[('sp500', 'GARCH', 't')], np.array([3.0]))[0])}


# =============================================================================
# 7. INNOVATIONS: THE NORMAL DISTRIBUTION IS NOT ENOUGH
# =============================================================================
def fig_resid_density(fits):
    fn = fits[('sp500', 'GARCH', 'normal')]
    z = fn.z.dropna().values
    ft = fits[('sp500', 'GJR', 'skewt')]
    nu_t = fits[('sp500', 'GARCH', 't')].params['nu']
    grid = np.linspace(-7, 5, 400)
    kde = stats.gaussian_kde(z, bw_method=0.25)
    st = stats.t(df=nu_t, scale=np.sqrt((nu_t - 2) / nu_t))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    ax = axes[0]
    ax.semilogy(grid, kde(grid), color=MainBlue, label='Standardised residuals $\\hat z_t$ (kernel density)')
    ax.semilogy(grid, stats.norm.pdf(grid), color=IDAred, ls='--', label='Normal N(0,1)')
    ax.semilogy(grid, st.pdf(grid), color=Forest, ls='-.', label=f'Student-t, $\\nu$ = {nu_t:.1f} (unit variance)')
    ax.set_ylim(1e-5, 1)
    ax.set_xlabel('$z$')
    ax.set_ylabel('Density (log scale)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    ax = axes[1]
    q = np.sort(z)
    pr = (np.arange(1, len(q) + 1) - 0.5) / len(q)
    ax.scatter(stats.norm.ppf(pr), q, s=3, color=IDAred, label='vs Normal quantiles')
    ax.scatter(st.ppf(pr), q, s=3, color=Forest, label=f'vs Student-t ($\\nu$ = {nu_t:.1f}) quantiles')
    lim = [-8, 6]
    ax.plot(lim, lim, color=Gray, lw=0.6)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel('Theoretical quantile')
    ax.set_ylabel('Empirical quantile of $\\hat z_t$')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    fig.tight_layout()
    save_fig('ch5_innovations')
    jb = stats.jarque_bera(z)
    NUM['innov'] = {'z_kurt': float(stats.kurtosis(z)), 'z_skew': float(stats.skew(z)), 'jb': float(jb[0]),
                    'z_min': float(z.min()), 'z_min_date': str(fn.z.idxmin().date()), 'nu_t': float(nu_t),
                    'r_kurt': float(stats.kurtosis(rets['sp500'])),
                    'n_below4': int((z < -4).sum()), 'exp_below4_normal': float(len(z) * stats.norm.cdf(-4)),
                    'exp_below4_t': float(len(z) * st.cdf(-4)),
                    'skewt_eta': float(ft.params['eta']), 'skewt_lambda': float(ft.params['lambda'])}


# =============================================================================
# 8. DIAGNOSTICS
# =============================================================================
def diagnostics(fits):
    rows = []
    for k in MAIN + ['bettr']:
        for vol, dist in [('GARCH', 'normal'), ('GARCH', 't'), ('GJR', 't'), ('EGARCH', 't'), ('GJR', 'skewt')]:
            f = fits[(k, vol, dist)]
            z = f.z.dropna()
            q, qp = ljung_box(z, 10)
            q2, q2p = ljung_box(z ** 2, 10)
            lm, lmp = arch_lm(z, 5)
            sb = sign_bias_test(z, f.eps)
            rows.append(dict(market=k, vol=vol, dist=dist, Q10_z=q, Q10_z_p=qp, Q10_z2=q2, Q10_z2_p=q2p,
                             LM5=lm, LM5_p=lmp, z_kurt=stats.kurtosis(z), z_skew=stats.skew(z), **sb))
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(TABLE_DIR, 'ch5_diagnostics.csv'), index=False)
    return t


def fig_diag_acf(fits):
    r = rets['sp500']
    f = fits[('sp500', 'GJR', 't')]
    z = f.z.dropna()
    L = 30
    lags = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.bar(lags - 0.2, acf(r ** 2, L), width=0.4, color=IDAred, label='ACF of $r_t^2$ (before the model)')
    ax.bar(lags + 0.2, acf(z ** 2, L), width=0.4, color=MainBlue, label=r'ACF of $\hat z_t^2$ (after GJR-GARCH-t)')
    b = 1.96 / np.sqrt(len(z))
    ax.axhspan(-b, b, color=LightGray, alpha=0.6, label='95% band under i.i.d.')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag (trading days)')
    ax.set_ylabel('Autocorrelation')
    legend_outside_bottom(ax, ncol=3, y=-0.25)
    save_fig('ch5_diag_acf')


# =============================================================================
# 9. OTHER MARKETS
# =============================================================================
def fig_markets_vol(fits):
    fig, axes = plt.subplots(2, 2, figsize=(10, 5.2))
    for ax, k in zip(axes.ravel(), ['bet', 'btc', 'eurron', 'gold']):
        f = fits[(k, 'GJR', 't')]
        v = f.sigma * np.sqrt(PPY[k])
        ax.plot(v.index, v.values, color=COL[k], lw=0.6, label=f'{LABELS[k]}, GJR-GARCH-t (% p.a.)')
        ax.set_ylabel('% p.a.')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), frameon=False)
    fig.tight_layout()
    save_fig('ch5_markets_vol')
    v = fits[('gold', 'GJR', 't')].sigma * np.sqrt(PPY['gold'])
    NUM['gold_peaks'] = {str(y): float(v.loc[str(y)].max()) for y in [2008, 2013, 2020, 2026]}


def fig_term_structure(fits, gt):
    H = 250
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    ts = {}
    for k in MAIN:
        f = fits[(k, 'GARCH', 't')]
        v = f.forecast_var(H)
        avg = np.sqrt(np.cumsum(v) / np.arange(1, H + 1) * PPY[k])
        ts[k] = {'h1': float(np.sqrt(v[0] * PPY[k])), 'h22': float(avg[21]), 'h250': float(avg[-1]),
                 'uncond': float(gt.loc[k, 'uncond_ann_vol'])}
        if k == 'eurron':
            continue
        ax = axes[1] if k == 'btc' else axes[0]
        ax.plot(np.arange(1, H + 1), avg, color=COL[k], label=LABELS[k])
        if np.isfinite(gt.loc[k, 'uncond_ann_vol']):
            ax.axhline(gt.loc[k, 'uncond_ann_vol'], color=COL[k], ls=':', lw=0.8)
    for ax in axes:
        ax.set_xlabel('Horizon $h$ (days)')
        ax.set_ylabel('Average volatility over $[T+1, T+h]$ (% p.a.)')
        legend_outside_bottom(ax, ncol=3, y=-0.2)
    axes[1].set_ylim(0, None)
    fig.tight_layout()
    save_fig('ch5_term_structure')
    NUM['term'] = ts


# =============================================================================
# 10. FORECAST EVALUATION (S&P 500, OUT OF SAMPLE, 2016-2026)
# =============================================================================
MODELS_OOS = [('GARCH', 'normal', 'GARCH-N'), ('GARCH', 't', 'GARCH-t'), ('GJR', 't', 'GJR-t'), ('EGARCH', 't', 'EGARCH-t')]


def oos_forecasts(k='sp500', first_year=2016, H=22):
    r = rets[k]
    idx = r.index
    last_year = idx[-1].year
    out1 = {lab: pd.Series(np.nan, index=idx) for *_, lab in MODELS_OOS}
    outH = {lab: pd.Series(np.nan, index=idx) for *_, lab in MODELS_OOS if lab != 'EGARCH-t'}
    for y in range(first_year, last_year + 1):
        start = idx[idx < f'{y}-01-01'][-1]
        end = idx[idx <= f'{y}-12-31'][-1]
        orig = idx[(idx >= start) & (idx < end)]
        for vol, dist, lab in MODELS_OOS:
            f = fit_garch(r, vol, dist, last_obs=idx[idx >= f'{y}-01-01'][0])
            hh = 1 if vol == 'EGARCH' else H
            fc = f.res.forecast(horizon=hh, start=start, reindex=False).variance / f.c ** 2
            fc = fc.loc[orig]
            pos = idx.get_indexer(fc.index)
            out1[lab].iloc[pos + 1] = fc.iloc[:, 0].values
            if hh == H and lab in outH:
                outH[lab].loc[fc.index] = fc.sum(axis=1).values      # cumulative variance over t+1..t+H, at origin t
    ew = ewma_variance(r)
    hist = (r ** 2).rolling(20).mean().shift(1)
    out1['EWMA'] = ew.reindex(idx)
    out1['Hist-20'] = hist
    outH['EWMA'] = (ew.shift(-1) * H).reindex(idx)       # the EWMA forecast is flat across horizons
    f1 = pd.DataFrame(out1).loc[f'{first_year}-01-01':].dropna()
    fH = pd.DataFrame(outH).dropna()
    return f1, fH


def forecast_eval(k='sp500', first_year=2016, H=22):
    r = rets[k]
    f1, fH = oos_forecasts(k, first_year, H)
    proxy = (r ** 2).reindex(f1.index)
    rows = []
    base = qlike(proxy, f1['GARCH-t'])
    for m in f1.columns:
        L = qlike(proxy, f1[m])
        mz = mz_regression(proxy, f1[m])
        dm = dm_test(L, base) if m != 'GARCH-t' else {'mean_diff': 0.0, 't': np.nan, 'p': np.nan}
        rows.append(dict(model=m, qlike=L.mean(), mse=((proxy - f1[m]) ** 2).mean(), dm_diff=dm['mean_diff'],
                         dm_t=dm['t'], dm_p=dm['p'], mz_a=mz['a'], mz_b=mz['b'], mz_b_se=mz['b_se'], mz_r2=mz['r2'],
                         mz_wald_p=mz['wald_p']))
    t = pd.DataFrame(rows).set_index('model')
    # horizon H: cumulative variances, non-overlapping origins (every H days)
    rH = (r ** 2).rolling(H).sum().shift(-H)
    origins = fH.index[::H]
    rows = []
    for m in fH.columns:
        y, x = rH.reindex(origins), fH[m].reindex(origins)
        okk = y.notna() & x.notna()
        mz = mz_regression(y[okk], x[okk], lags=2)
        lmz = mz_regression(np.log(y[okk]), np.log(x[okk]), lags=2)
        rows.append(dict(model=m, n=int(okk.sum()), mz_a=mz['a'], mz_b=mz['b'], mz_b_se=mz['b_se'], mz_r2=mz['r2'],
                         mz_wald_p=mz['wald_p'], lmz_a=lmz['a'], lmz_b=lmz['b'], lmz_b_se=lmz['b_se'], lmz_r2=lmz['r2'],
                         lmz_wald_p=lmz['wald_p'], qlike=qlike(y[okk], x[okk]).mean()))
    tH = pd.DataFrame(rows).set_index('model')
    t.to_csv(os.path.join(TABLE_DIR, 'ch5_forecast_eval.csv'))
    tH.to_csv(os.path.join(TABLE_DIR, 'ch5_forecast_eval_22d.csv'))
    NUM['oos'] = {'start': str(f1.index[0].date()), 'end': str(f1.index[-1].date()), 'n': len(f1),
                  'n22': int(tH['n'].iloc[0])}
    # chart 1: forecast vs |r|
    ppy = np.sqrt(PPY[k])
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.scatter(f1.index, np.sqrt(proxy) * ppy, s=2, color=Teal, alpha=0.5, label=r'Realised proxy $|r_t|\sqrt{q}$, $q$ = ' + f'{PPY[k]:.1f}')
    ax.plot(f1.index, np.sqrt(f1['GJR-t']) * ppy, color=IDAred, lw=0.7, label='GJR-GARCH-t one-day-ahead forecast')
    ax.plot(f1.index, np.sqrt(f1['EWMA']) * ppy, color=MainBlue, lw=0.6, alpha=0.8, label='EWMA ($\\lambda$ = 0.94)')
    ax.set_ylim(0, 110)
    ax.set_ylabel('Annualised volatility (%)')
    legend_outside_bottom(ax, ncol=3, y=-0.12)
    save_fig('ch5_forecast_oos')
    # chart 2: relative QLIKE
    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    order = t['qlike'].sort_values().index
    vals = t.loc[order, 'dm_diff']
    cols = [Forest if v < 0 else (MainBlue if v == 0 else IDAred) for v in vals]
    ax.bar(order, vals, color=cols)
    for i, m in enumerate(order):
        if m != 'GARCH-t':
            ax.annotate(f"DM t = {t.loc[m, 'dm_t']:.2f}", (i, vals[m]), ha='center',
                        va='bottom' if vals[m] >= 0 else 'top', fontsize=8, xytext=(0, 2 if vals[m] >= 0 else -2),
                        textcoords='offset points')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_ylabel('QLIKE minus GARCH-t\n(lower = better)')
    save_fig('ch5_qlike')
    # chart 3: 22-day Mincer-Zarnowitz, in logs
    fig, ax = plt.subplots(figsize=(7, 4))
    y, x = rH.reindex(origins), fH['GJR-t'].reindex(origins)
    okk = y.notna() & x.notna()
    ly, lx = np.log(y[okk]), np.log(x[okk])
    ax.scatter(lx, ly, s=10, color=IDAred, label='GJR-GARCH-t, non-overlapping 22-day windows')
    lim = [min(lx.min(), ly.min()) - 0.2, max(lx.max(), ly.max()) + 0.2]
    ax.plot(lim, lim, color=Gray, lw=0.7, ls='--', label='45-degree reference line (equal plotted values)')
    a, b = tH.loc['GJR-t', 'lmz_a'], tH.loc['GJR-t', 'lmz_b']
    xx = np.linspace(*lim, 10)
    ax.plot(xx, a + b * xx, color=MainBlue, label=f'Mincer-Zarnowitz fit in logs: a = {a:.2f}, b = {b:.2f}')
    ax.set_xlabel('ln forecast of 22-day variance')
    ax.set_ylabel('ln realised 22-day variance')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch5_mz')
    return t, tH


# =============================================================================
# 11. GARCH-IN-MEAN AND LONG MEMORY
# =============================================================================
def garch_in_mean():
    r = rets['sp500']
    out = {}
    for form in ['vol', 'var']:
        m = ARCHInMean(r, lags=0, form=form, volatility=GARCH(), distribution=StudentsT())
        res = m.fit(disp='off')
        out[form] = {'kappa': float(res.params['kappa']), 't': float(res.tvalues['kappa']),
                     'p': float(res.pvalues['kappa']), 'const': float(res.params['Const'])}
    NUM['garch_m'] = out


def fig_long_memory(fits):
    r = rets['sp500']
    L = 250
    emp = acf(np.abs(r), L)
    f = fits[('sp500', 'GARCH', 't')]
    p = f.params
    sim = ZeroMean(None, volatility=GARCH(), distribution=StudentsT(seed=np.random.default_rng(SEED)))
    x = sim.simulate([p['omega'], p['alpha[1]'], p['beta[1]'], p['nu']], nobs=400_000, burn=2000)['data'].values
    ga = acf(np.abs(x), L)
    ff = arch_model(r, vol='FIGARCH', p=1, q=1, dist='t').fit(disp='off')
    fp = ff.params
    simf = ZeroMean(None, volatility=FIGARCH(), distribution=StudentsT(seed=np.random.default_rng(SEED + 1)))
    xf = simf.simulate([fp['omega'], fp['phi'], fp['d'], fp['beta'], fp['nu']], nobs=400_000, burn=5000)['data'].values
    fa = acf(np.abs(xf), L)
    lags = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(lags, emp, color=MainBlue, marker='o', ms=2, lw=0, label='S&P 500 data, ACF of $|r_t|$')
    ax.plot(lags, ga, color=IDAred, label='Simulated from fitted GARCH(1,1)-t')
    ax.plot(lags, fa, color=Forest, ls='--', label='Simulated from fitted FIGARCH(1,d,1)-t')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('Lag (trading days, log scale)')
    ax.set_ylabel('Autocorrelation of $|r_t|$')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch5_long_memory')
    NUM['long_memory'] = {'emp_1': emp[0], 'emp_100': emp[99], 'emp_250': emp[249], 'garch_1': ga[0], 'garch_100': ga[99],
                          'garch_250': ga[249], 'fig_1': fa[0], 'fig_100': fa[99], 'fig_250': fa[249],
                          'd': float(fp['d']), 'd_se': float(ff.std_err['d']), 'fig_bic': float(ff.bic),
                          'garch_bic': float(f.bic)}


# =============================================================================
# 12. WORKED EXAMPLE: THE RECURSION AND THE FORECAST STEP BY STEP (S&P 500, last day)
# =============================================================================
def worked_example(fits):
    f = fits[('sp500', 'GARCH', 't')]
    p = f.params
    r = rets['sp500']
    T = r.index[-1]
    eps = r.iloc[-1] - p['mu']
    s2T = f.sigma.iloc[-1] ** 2
    s2n = p['omega'] + p['alpha[1]'] * eps ** 2 + p['beta[1]'] * s2T
    pers = p['alpha[1]'] + p['beta[1]']
    uv = p['omega'] / (1 - pers)
    h10 = uv + pers ** 9 * (s2n - uv)
    fc = f.forecast_var(10)
    NUM['worked'] = {'T': str(T.date()), 'rT': float(r.iloc[-1]), 'eps': float(eps), 's2T': float(s2T),
                     's2n': float(s2n), 'uv': float(uv), 'h10': float(h10), 'h10_arch': float(fc[-1]),
                     'h1_arch': float(fc[0]), 'sum10': float(fc.sum()), 'vol10_pct': float(np.sqrt(fc.sum()))}
    fn = fits[('sp500', 'GARCH', 'normal')]
    a, b = fn.params['alpha[1]'], fn.params['beta[1]']
    den = 1 - (a + b) ** 2 - 2 * a ** 2
    NUM['kurt_normal'] = {'alpha': float(a), 'beta': float(b), 'cond': float((a + b) ** 2 + 2 * a ** 2),
                          'K': float(3 * (1 - (a + b) ** 2) / den) if den > 0 else float('inf')}


if __name__ == '__main__':
    print('ARCH effects');         ae = arch_effects_table()
    fig_clustering(); fig_acf_r_r2()
    print('Model grid');           grid, FITS = model_grid()
    gt = garch_table(FITS);        at = asym_table(FITS)
    fig_simulation(); fig_sp500_vol(FITS); fig_covid(FITS); fig_persistence(gt); fig_nic(FITS)
    fig_resid_density(FITS);       dg = diagnostics(FITS); fig_diag_acf(FITS)
    fig_markets_vol(FITS);         fig_term_structure(FITS, gt)
    print('Forecast evaluation');  fe, fe22 = forecast_eval()
    garch_in_mean();               fig_long_memory(FITS); worked_example(FITS)
    NUM['ppy'] = PPY
    with open(os.path.join(TABLE_DIR, 'ch5_numbers.json'), 'w') as fh:
        json.dump(NUM, fh, indent=1, default=float)
    pd.set_option('display.width', 250)
    print(ae.round(3)); print(gt.round(4)); print(at.round(3)); print(fe.round(4)); print(fe22.round(3))
    print(dg.round(3)); print(json.dumps(NUM, indent=1, default=float))

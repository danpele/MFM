"""
Charts and numbers of Chapter 11: continuous-time models
=========================================================
All charts: transparent background, English labels, legend outside at the bottom; time series in palette colours.
Daily market data: S&P 500 (1990-2026), BET (2000-2026), Bitcoin (2014-2026), VIX (1990-2026);
3-month US Treasury bill rate (FRED, DTB3, 1954-2026).
Numbers are saved in ch11_results.json (used by the slide generators).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, optimize
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import LABELS, log_returns, load_close, load_vix, read_fred, periods_per_year, load_spy_5m  # noqa: E402
from ct_models import (scaled_random_walk, bm_paths, quadratic_variation, total_variation, ito_stratonovich,  # noqa: E402
                       max_prob, convergence_study, slope_ci, slope_boot, gbm_paths, gbm_mle, gbm_simulate_returns,
                       ou_exact_path, ou_mle, merton_logpdf, merton_mle, merton_moments, merton_simulate_returns,
                       lee_mykland, heston_paths, heston_from_vix, heston_simulate_returns, heston_smile, acf,
                       stylised, short_rate_fits, nw_drift_diffusion, hill)

# Chart style: transparent background, legend below the plot
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.1
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

# Brand colours
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Teal     = '#17A2B8'
Gray     = '#7F7F7F'   # reference lines, bands and grid only
LightGray = '#DADADA'
MODEL_COL = {'Data': MainBlue, 'GBM': Orange, 'Merton': Purple, 'Heston': Forest}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
DT = 1 / 252


def save_fig(name):
    """Save the figure as a transparent PDF and PNG."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Place the legend outside the plot, bottom centre."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def fig_legend_bottom(fig, handles=None, labels=None, ncol=4, y=0.0):
    """A single legend for a multi-panel figure, below the figure."""
    if handles is None:
        handles, labels = [], []
        for ax in fig.axes:
            h, l = ax.get_legend_handles_labels()
            for hh, ll in zip(h, l):
                if ll not in labels and not ll.startswith('_'):
                    handles.append(hh)
                    labels.append(ll)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.ndarray):
        return [jsonable(v) for v in x.tolist()]
    if isinstance(x, pd.Timestamp):
        return str(x.date())
    return x


# =============================================================================
# DATA: daily log returns (not in %), each series on its own calendar
# =============================================================================
rets = {k: log_returns(k) for k in ['sp500', 'bet', 'btc']}
DTS = {'sp500': 1 / 252, 'bet': 1 / 252, 'btc': 1 / 365}


# =============================================================================
# 1. FROM RANDOM WALK TO BROWNIAN MOTION
# =============================================================================
def fig_donsker():
    """Scaled random walk for n = 5, 50, 5000 and the probability P(max W > 1) (reflection principle)."""
    rng = np.random.default_rng(SEED)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={'width_ratios': [1.5, 1]})
    for n, c in zip([5, 50, 5000], [IDAred, Amber, MainBlue]):
        t, W = scaled_random_walk(n, 1, rng)
        axes[0].step(t, W[0], where='post', color=c, lw=1.2 if n < 5000 else 0.8, label=f'n = {n}')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_xlabel('Time t')
    axes[0].set_ylabel(r'$S_{\lfloor nt \rfloor}/\sqrt{n}$')
    axes[0].set_title('Scaled random walks', loc='left')
    ns = [5, 10, 20, 50, 100, 200, 500, 1000, 2000]
    M = 20000
    out = {'n': ns, 'p': [], 'se': []}
    for n in ns:
        _, W = scaled_random_walk(n, M, rng)
        p = max_prob(W, 1.0)
        out['p'].append(p)
        out['se'].append(np.sqrt(p * (1 - p) / M))
    exact = 2 * (1 - stats.norm.cdf(1.0))
    axes[1].errorbar(ns, out['p'], yerr=1.96 * np.array(out['se']), fmt='o-', color=MainBlue, ms=4, capsize=2,
                     label='Random walk, 20,000 paths (95% CI)')
    axes[1].axhline(exact, color=IDAred, ls='--', lw=1, label=f'Brownian motion: 2(1 - Φ(1)) = {exact:.4f}')
    axes[1].set_xscale('log')
    axes[1].set_xlabel('Number of steps n')
    axes[1].set_ylabel(r'$P(\max_{t \leq 1} W_n(t) > 1)$')
    axes[1].set_title('A path functional converges too', loc='left')
    legend_outside_bottom(axes[0], ncol=3, y=-0.2)
    legend_outside_bottom(axes[1], ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_donsker')
    out['exact'] = exact
    return out


def fig_bm_paths():
    """Brownian paths with the +-1.96 sqrt(t) band and self-similarity (zoom 100x in time, 10x in space)."""
    rng = np.random.default_rng(SEED + 1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    t, W = bm_paths(5, 2000, 1.0, rng)
    axes[0].fill_between(t, -1.96 * np.sqrt(t), 1.96 * np.sqrt(t), color=LightGray, alpha=0.8, lw=0,
                         label=r'$\pm 1.96\sqrt{t}$ (95% of paths at each t)')
    for w, c in zip(W, [MainBlue, IDAred, Forest, Amber, Purple]):
        axes[0].plot(t, w, color=c, lw=0.8)
    axes[0].set_xlabel('Time t')
    axes[0].set_ylabel(r'$W_t$')
    axes[0].set_title('Five Brownian paths on [0, 1]', loc='left')
    t2, W2 = bm_paths(1, 100000, 1.0, rng)
    w = W2[0]
    axes[1].plot(t2, w, color=MainBlue, lw=0.5, label='Path on [0, 1]')
    k = 1000                                             # [0, 0.01] rescaled: time x100, space x10
    axes[1].plot(t2[:k + 1] * 100, w[:k + 1] * 10, color=IDAred, lw=0.5,
                 label=r'Its first 1% of time, rescaled: $10\,W_{t/100}$')
    axes[1].set_xlabel('Time t')
    axes[1].set_title('Self-similarity: zoom in and the path looks the same', loc='left')
    legend_outside_bottom(axes[0], ncol=1, y=-0.2)
    legend_outside_bottom(axes[1], ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_bm_paths')


def fig_quadratic_variation():
    """Quadratic and total variation on ever finer grids; realised quadratic variation of the S&P 500."""
    rng = np.random.default_rng(SEED + 2)
    N = 2 ** 16
    _, W = bm_paths(1, N, 1.0, rng)
    w = W[0]
    ns = [2 ** k for k in range(4, 17)]
    qv = [quadratic_variation(w[::N // n]) for n in ns]
    tv = [total_variation(w[::N // n]) for n in ns]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    axes[0].plot(ns, qv, 'o-', color=MainBlue, ms=3.5, label=r'Quadratic variation $\sum (\Delta W)^2$')
    axes[0].plot(ns, tv, 's-', color=IDAred, ms=3.5, label=r'Total variation $\sum |\Delta W|$')
    axes[0].plot(ns, np.sqrt(2 * np.array(ns) / np.pi), color=Gray, ls=':', lw=0.9, label=r'$\sqrt{2n/\pi}$')
    axes[0].axhline(1.0, color=Gray, ls='--', lw=0.8, label='T = 1')
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Number of intervals n on [0, 1]')
    axes[0].set_title('One Brownian path, finer and finer grids', loc='left')
    r = rets['sp500']
    cum = (r ** 2).cumsum()
    years = (r.index - r.index[0]).days / 365.25
    lin = cum.iloc[-1] * years / years[-1]
    axes[1].plot(r.index, cum, color=MainBlue, lw=1.1, label=r'S&P 500: $\sum_{s \leq t} r_s^2$')
    axes[1].plot(r.index, lin, color=Orange, ls='--', lw=1.1, label=r'GBM: $\sigma^2 t$ (same end point)')
    axes[1].set_ylabel('Cumulative squared returns')
    axes[1].set_title('Realised quadratic variation, 1990-2026', loc='left')
    legend_outside_bottom(axes[0], ncol=2, y=-0.2)
    legend_outside_bottom(axes[1], ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_quadratic_variation')
    gaps = {}
    for a, b in [('2008-09-01', '2009-03-31'), ('2020-02-20', '2020-04-30')]:
        seg = r.loc[a:b]
        gaps[a[:4]] = dict(share_qv=float((seg ** 2).sum() / cum.iloc[-1]), share_time=len(seg) / len(r))
    return dict(qv=dict(zip(map(str, ns), qv)), tv=dict(zip(map(str, ns), tv)), total_qv=float(cum.iloc[-1]),
                sigma_implied=float(np.sqrt(cum.iloc[-1] / years[-1])), crises=gaps)


def fig_ito():
    """W_t^2 = 2 int W dW + t on one path; the Stratonovich - Ito difference over 5000 paths."""
    rng = np.random.default_rng(SEED + 3)
    n = 2000
    t, W = bm_paths(1, n, 1.0, rng)
    w = W[0]
    dW = np.diff(w)
    ito_path = np.concatenate([[0], np.cumsum(w[:-1] * dW)])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    axes[0].plot(t, w ** 2, color=MainBlue, lw=2.2, label=r'$W_t^2$')
    axes[0].plot(t, 2 * ito_path, color=IDAred, lw=0.9, label=r'$2\int_0^t W_s\,dW_s$ (Itô, left end points)')
    axes[0].plot(t, 2 * ito_path + t, color=Orange, lw=1.3, ls=(0, (4, 3)), label=r'$2\int_0^t W_s\,dW_s + t$')
    axes[0].set_xlabel('Time t')
    axes[0].set_title("Itô's formula on one path", loc='left')
    _, Wm = bm_paths(5000, 1000, 1.0, rng)
    ito, strat = ito_stratonovich(Wm)
    exact = 0.5 * (Wm[:, -1] ** 2 - 1.0)
    diff = strat - ito
    axes[1].hist(diff, bins=50, color=Teal, alpha=0.85, label='Stratonovich sum - Itô sum (5,000 paths)')
    axes[1].axvline(0.5, color=IDAred, ls='--', lw=1, label='T/2 = 0.5')
    axes[1].set_xlabel('Difference between the two Riemann-type sums, n = 1,000')
    axes[1].set_title('The evaluation point matters', loc='left')
    legend_outside_bottom(axes[0], ncol=2, y=-0.2)
    legend_outside_bottom(axes[1], ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_ito')
    return dict(diff_mean=float(diff.mean()), diff_sd=float(diff.std()), ito_err_mean=float(np.mean(ito - exact)),
                ito_err_sd=float(np.std(ito - exact)), ito_mean=float(ito.mean()), ito_var=float(ito.var()))


def fig_convergence():
    """Strong and weak errors of the Euler-Maruyama and Milstein schemes for Higham's test equation."""
    rng = np.random.default_rng(SEED + 4)
    d, P = convergence_study(rng, return_paths=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    axes[0].errorbar(d['dt'], d['strong_em'], yerr=1.96 * d['strong_em_se'], fmt='o-', color=MainBlue, ms=4,
                     capsize=2, label='Euler-Maruyama')
    axes[0].errorbar(d['dt'], d['strong_mil'], yerr=1.96 * d['strong_mil_se'], fmt='s-', color=IDAred, ms=4,
                     capsize=2, label='Milstein')
    x = d['dt'].values
    axes[0].plot(x, d['strong_em'].iloc[0] * (x / x[0]) ** 0.5, color=Gray, ls=':', label='Slope 1/2')
    axes[0].plot(x, d['strong_mil'].iloc[0] * (x / x[0]) ** 1.0, color=Gray, ls='--', label='Slope 1')
    axes[0].set_title(r'Strong error $E|X_T - X^{\Delta t}_T|$', loc='left')
    axes[1].plot(x, d['weak_em_exact'], 'o-', color=MainBlue, ms=4, label=r'Euler-Maruyama (exact $E X^{\Delta t}_T$)')
    axes[1].plot(x, d['weak_em_mc'], 'x', color=Teal, ms=6, label='Euler-Maruyama (Monte Carlo)')
    axes[1].plot(x, d['weak_em_exact'].iloc[0] * (x / x[0]), color=Gray, ls='--', label='Slope 1')
    axes[1].set_title(r'Weak error $|E X^{\Delta t}_T - E X_T|$', loc='left')
    for ax in axes:
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel(r'Step size $\Delta t$')
    legend_outside_bottom(axes[0], ncol=2, y=-0.2)
    legend_outside_bottom(axes[1], ncol=2, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_convergence')
    # log-log slopes; 95% intervals by whole-path bootstrap (all resolutions together)
    rb = np.random.default_rng(SEED + 40)
    se = slope_boot(d['dt'], P['abs_em'], rb)
    sm = slope_boot(d['dt'], P['abs_mil'], rb)
    # the exact weak error is deterministic: slope on the grid, no confidence interval
    we = dict(slope=float(np.polyfit(np.log(d['dt']), np.log(d['weak_em_exact']), 1)[0]))
    d.to_csv(os.path.join(HERE, 'ch11_convergence.csv'), index=False)
    return dict(table=d.to_dict('list'), slope_em=se, slope_mil=sm, slope_weak=we)


# =============================================================================
# 2. GEOMETRIC BROWNIAN MOTION
# =============================================================================
def gbm_estimates():
    """GBM estimates for the S&P 500, BET, Bitcoin."""
    out = {}
    for k, r in rets.items():
        g = gbm_mle(r.values, DTS[k])
        g['start'] = str(r.index[0].date())
        g['ppy'] = periods_per_year(r)
        out[k] = g
    return out


def fig_gbm_fan(g):
    """Ten years of GBM paths for the S&P 500 from the last close: mean vs median."""
    rng = np.random.default_rng(SEED + 5)
    S0 = float(load_close('sp500').iloc[-1])
    T, n = 10.0, 2520
    mu, sigma = g['mu'], g['sigma']
    t, S = gbm_paths(S0, mu, sigma, T, n, 20000, rng)
    fig, ax = plt.subplots(figsize=(9, 3.6))
    q05, q95 = np.quantile(S, [0.05, 0.95], axis=0)
    ax.fill_between(t, q05, q95, color=LightGray, alpha=0.8, lw=0, label='5%-95% band of 20,000 paths')
    cols = [Teal, Purple, Amber, Crimson, Forest]
    for i in range(5):
        ax.plot(t, S[i], color=cols[i], lw=0.6)
    ax.plot(t, S0 * np.exp(mu * t), color=IDAred, lw=1.6, label=r'Mean $S_0 e^{\mu t}$')
    ax.plot(t, S0 * np.exp((mu - 0.5 * sigma ** 2) * t), color=MainBlue, lw=1.6, ls='--',
            label=r'Median $S_0 e^{(\mu - \sigma^2/2) t}$')
    ax.set_yscale('log')
    ticks = [4000, 6000, 8000, 10000, 15000, 20000, 30000, 40000]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{v:,}' for v in ticks])
    ax.minorticks_off()
    ax.set_xlabel('Years after 18 September 2026')
    ax.set_ylabel('S&P 500 level (log scale)')
    legend_outside_bottom(ax, ncol=3)
    save_fig('ch11_gbm_fan')
    ST = S[:, -1]
    return dict(S0=S0, mean_T=float(S0 * np.exp(mu * T)), median_T=float(S0 * np.exp((mu - 0.5 * sigma ** 2) * T)),
                q05=float(np.quantile(ST, 0.05)), q95=float(np.quantile(ST, 0.95)),
                p_below=float(np.mean(ST < S0)), p_below_exact=float(stats.norm.cdf(-(mu - 0.5 * sigma ** 2) * np.sqrt(T) / sigma)),
                mean_sim=float(ST.mean()), share_below_mean=float(np.mean(ST < S0 * np.exp(mu * T))))


def fig_lognormal(g):
    """Lognormal distribution of S_T / S_0 after 10 years: mode < median < mean."""
    mu, sigma, T = g['mu'], g['sigma'], 10.0
    m, s = (mu - 0.5 * sigma ** 2) * T, sigma * np.sqrt(T)
    rng = np.random.default_rng(SEED + 6)
    x = np.exp(m + s * rng.standard_normal(200000))
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.hist(x, bins=np.linspace(0, 12, 121), density=True, color=Teal, alpha=0.7, label='Simulated $S_T/S_0$ (200,000 draws)')
    xx = np.linspace(0.01, 12, 600)
    ax.plot(xx, stats.lognorm.pdf(xx, s, scale=np.exp(m)), color=MainBlue, lw=1.4, label='Lognormal density')
    mode, med, mean = np.exp(m - s ** 2), np.exp(m), np.exp(m + 0.5 * s ** 2)
    for v, c, lab in [(mode, Forest, 'Mode'), (med, Amber, 'Median'), (mean, IDAred, 'Mean')]:
        ax.axvline(v, color=c, lw=1.3, ls='--', label=f'{lab} = {v:.2f}')
    ax.set_xlabel('Gross return over 10 years, $S_T / S_0$')
    ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=3)
    save_fig('ch11_lognormal')
    return dict(mode=float(mode), median=float(med), mean=float(mean), p_below1=float(stats.norm.cdf(-m / s)),
                p_below_mean=float(stats.norm.cdf(0.5 * s)))


def fig_gbm_vs_data(g):
    """S&P 500: QQ plot against the Normal distribution and autocorrelation of |r| against simulated GBM."""
    r = rets['sp500'].values
    z = (r - r.mean()) / r.std()
    n = len(z)
    q = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].scatter(q, np.sort(z), s=4, color=MainBlue, label='S&P 500 daily log returns, standardised')
    axes[0].plot([-5, 5], [-5, 5], color=Gray, lw=0.8, label='45-degree line (Normal distribution)')
    axes[0].set_xlabel('Quantiles of the standard Normal distribution')
    axes[0].set_ylabel('Sample quantiles')
    axes[0].set_title('Tails: returns are not Normal', loc='left')
    lags = np.arange(1, 51)
    rng = np.random.default_rng(SEED + 7)
    sims = np.array([acf(np.abs(gbm_simulate_returns(g['m'], g['sigma'], n, DT, rng)), lags) for _ in range(200)])
    lo, hi = np.quantile(sims, [0.025, 0.975], axis=0)
    a = acf(np.abs(r), lags)
    axes[1].fill_between(lags, lo, hi, color=LightGray, alpha=0.9, lw=0, label='GBM: 95% range of 200 simulations')
    axes[1].bar(lags, a, color=MainBlue, width=0.7, label='S&P 500: ACF of |r|')
    axes[1].set_xlabel('Lag (trading days)')
    axes[1].set_title('Clustering: |r| is autocorrelated', loc='left')
    legend_outside_bottom(axes[0], ncol=1, y=-0.2)
    legend_outside_bottom(axes[1], ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_gbm_vs_data')
    s = stylised(r)
    jb = stats.jarque_bera(r)
    return dict(exkurt=s['exkurt'], skew=s['skew'], acf1=float(a[0]), acf50=float(a[-1]), band_hi=float(hi.max()),
                n_out=int(np.sum(np.abs(z) > 4)), n_out_exp=float(n * 2 * stats.norm.sf(4)), jb=float(jb.statistic),
                zmin=float(z.min()))


def fig_drift_precision(g):
    """Precision of the drift estimate: width of the 95% interval vs span; estimates on 10-year windows."""
    years = np.linspace(1, 100, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    for k, c in [('sp500', MainBlue), ('btc', Amber)]:
        s = g[k]['sigma']
        axes[0].plot(years, 1.96 * s / np.sqrt(years) * 100, color=c, lw=1.4,
                     label=f"{LABELS[k]} ($\\sigma$ = {100 * s:.0f}%)")
    axes[0].axhline(1.0, color=Gray, ls='--', lw=0.8, label='+/- 1 percentage point')
    axes[0].set_xlabel('Years of data T')
    axes[0].set_ylabel('Half-width of 95% CI for the drift (pp)')
    axes[0].set_yscale('log')
    axes[0].set_title(r'Drift precision depends only on T: $1.96\,\sigma/\sqrt{T}$', loc='left')
    r = rets['sp500']
    w = 2520
    m = r.rolling(w).mean() / DT
    s = r.rolling(w).std() / np.sqrt(DT)
    ci = 1.96 * s / np.sqrt(w * DT)
    axes[1].fill_between(m.index, 100 * (m - ci), 100 * (m + ci), color=LightGray, alpha=0.8, lw=0,
                         label='95% CI for the log drift')
    axes[1].plot(m.index, 100 * m, color=MainBlue, lw=1.2, label=r'Log drift $\hat m = \hat\mu - \hat\sigma^2/2$ (% p.a.)')
    axes[1].plot(s.index, 100 * s, color=IDAred, lw=1.2, label=r'Volatility $\hat\sigma$ (% p.a.)')
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_title('S&P 500, rolling 10-year windows', loc='left')
    legend_outside_bottom(axes[0], ncol=2, y=-0.2)
    legend_outside_bottom(axes[1], ncol=2, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_drift_precision')
    mm = m.dropna()
    ss = s.dropna()
    return dict(T_1pp_sp=float((1.96 * g['sp500']['sigma'] / 0.01) ** 2), T_1pp_btc=float((1.96 * g['btc']['sigma'] / 0.01) ** 2),
                m_min=float(mm.min()), m_max=float(mm.max()), m_min_date=str(mm.idxmin().date()), m_max_date=str(mm.idxmax().date()),
                s_min=float(ss.min()), s_max=float(ss.max()))


# =============================================================================
# 3. ORNSTEIN-UHLENBECK
# =============================================================================
def fig_ou_paths():
    """Three OU processes with the same shocks and different mean-reversion speeds."""
    rng = np.random.default_rng(SEED + 8)
    dt, n = 1 / 252, 252 * 10
    z = rng.standard_normal(n)
    theta, sigma, x0 = 0.03, 0.01, 0.08
    fig, ax = plt.subplots(figsize=(9, 3.5))
    t = np.arange(n + 1) * dt
    out = {}
    for kappa, c in [(0.2, MainBlue), (1.0, Amber), (5.0, IDAred)]:
        x = ou_exact_path(x0, kappa, theta, sigma, dt, n, rng, z=z)
        ax.plot(t, 100 * x, color=c, lw=0.9, label=f'$\\kappa$ = {kappa}: half-life {np.log(2) / kappa:.2f} years')
        out[str(kappa)] = dict(half_life=np.log(2) / kappa, stat_sd=sigma / np.sqrt(2 * kappa))
    ax.axhline(100 * theta, color=Gray, ls='--', lw=0.8, label=r'Long-run mean $\theta$ = 3%')
    ax.set_xlabel('Years')
    ax.set_ylabel('x (%)')
    legend_outside_bottom(ax, ncol=2)
    save_fig('ch11_ou_paths')
    return out


def fig_vasicek():
    """3-month Treasury bill rate (FRED, DTB3): Vasicek estimates over the full period and over subperiods."""
    tb = read_fred('DTB3') / 100
    full = ou_mle(tb.values, DT)
    subs = [('1954', '1979'), ('1980', '2007'), ('2008', '2026')]
    res = {'1954-2026': full}
    for a, b in subs:
        res[f'{a}-{b}'] = ou_mle(tb.loc[a:b].values, DT)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={'width_ratios': [1.6, 1]})
    axes[0].plot(tb.index, 100 * tb, color=MainBlue, lw=0.8, label='3-month Treasury bill rate (% p.a.)')
    axes[0].axhline(100 * full['theta'], color=IDAred, ls='--', lw=1, label=rf"Vasicek $\hat\theta$ = {100 * full['theta']:.2f}%")
    axes[0].fill_between(tb.index, 100 * (full['theta'] - 2 * full['stat_sd']), 100 * (full['theta'] + 2 * full['stat_sd']),
                         color=LightGray, alpha=0.45, lw=0, label=r'$\hat\theta \pm 2$ stationary s.d.')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_title('Short rate, 1954-2026', loc='left')
    labs = list(res)
    k = np.array([res[l]['kappa'] for l in labs])
    se = np.array([res[l]['se_kappa'] for l in labs])
    cols = [MainBlue, Amber, Forest, Purple]
    for i, (l, c) in enumerate(zip(labs, cols)):
        axes[1].errorbar(i, k[i], yerr=1.96 * se[i], fmt='o', color=c, capsize=4, ms=6)
    axes[1].axhline(0, color=Gray, lw=0.6)
    axes[1].set_xticks(range(len(labs)))
    axes[1].set_xticklabels(labs, fontsize=8)
    axes[1].set_ylabel(r'$\hat\kappa$ with 95% CI (per year)')
    axes[1].set_title('Speed of mean reversion', loc='left')
    legend_outside_bottom(axes[0], ncol=2, y=-0.15)
    plt.tight_layout()
    save_fig('ch11_vasicek')
    out = {k2: {c: float(v) for c, v in d.items()} for k2, d in res.items()}
    out['last'] = float(tb.iloc[-1])
    out['min'] = float(tb.min())
    out['min_date'] = str(tb.idxmin().date())
    out['max'] = float(tb.max())
    out['max_date'] = str(tb.idxmax().date())
    out['share_zero'] = float(np.mean(tb < 0.0005))
    out['p_neg'] = float(stats.norm.cdf(-full['theta'] / full['stat_sd']))
    return out


def fig_vix_ou():
    """Log VIX as an OU process: long-run level, half-life, autocorrelation."""
    vix = load_vix()
    x = np.log(vix)
    f = ou_mle(x.values, DT)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={'width_ratios': [1.6, 1]})
    axes[0].plot(vix.index, vix, color=MainBlue, lw=0.7, label='VIX (% p.a.)')
    axes[0].axhline(np.exp(f['theta']), color=IDAred, ls='--', lw=1, label=rf"$e^{{\hat\theta}}$ = {np.exp(f['theta']):.1f}")
    axes[0].set_yscale('log')
    axes[0].set_yticks([10, 20, 40, 80])
    axes[0].set_yticklabels(['10', '20', '40', '80'])
    axes[0].minorticks_off()
    axes[0].set_title('VIX, 1990-2026 (log scale)', loc='left')
    lags = np.arange(1, 121)
    a = acf(x.values, lags)
    axes[1].plot(lags, a, color=MainBlue, lw=1.3, label='Sample ACF of ln VIX')
    axes[1].plot(lags, f['b'] ** lags, color=IDAred, ls='--', lw=1.2, label=r'OU: $e^{-\hat\kappa\,k\,\Delta t}$')
    axes[1].set_xlabel('Lag k (trading days)')
    axes[1].set_title('Memory decays more slowly than OU', loc='left')
    legend_outside_bottom(axes[0], ncol=2, y=-0.15)
    legend_outside_bottom(axes[1], ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_vix_ou')
    out = {c: float(v) for c, v in f.items()}
    out.update(hl_days=float(f['half_life'] * 252), level=float(np.exp(f['theta'])), acf60=float(a[59]), ou60=float(f['b'] ** 60),
               vix_last=float(vix.iloc[-1]), vix_max=float(vix.max()), vix_max_date=str(vix.idxmax().date()))
    return out


# =============================================================================
# 3b. ESTIMATING DIFFUSIONS: EXACT VS EULER LIKELIHOOD, CKLS, NONPARAMETRIC ESTIMATION
# =============================================================================
def diffusion_fits():
    """Vasicek, CIR (exact and Euler) and CKLS on the 3-month Treasury bill rate (FRED, DTB3), 1954-2007:
    daily and month-end data. 2008-2026 is excluded: it contains exact zeros and negative quotes (outside the
    domain of the CIR likelihood and of the Euler pseudo-likelihood with r^gamma) and a zero-lower-bound regime."""
    tb = read_fred('DTB3') / 100
    s = tb.loc['1954':'2007']
    out = {'daily': short_rate_fits(s.values, DT), 'monthly': short_rate_fits(s.resample('ME').last().values, 1 / 12)}
    out['min_rate'] = float(s.min())
    post = tb.loc['2008':]
    out['share_zero_post2008'] = float(np.mean(post < 0.0005))
    out['n_zero_post2008'] = int((post == 0).sum())
    out['n_neg_post2008'] = int((post < 0).sum())
    return out


def fig_np_diffusion(fits):
    """Nonparametric (Nadaraya-Watson) drift and diffusion of the 3-month rate, 1954-2007, against Vasicek, CIR, CKLS."""
    tb = (read_fred('DTB3') / 100).loc['1954':'2007']
    x = tb.values
    grid = np.linspace(np.quantile(x, 0.02), np.quantile(x, 0.98), 60)
    nw = nw_drift_diffusion(x, DT, grid)
    F = fits['daily']
    lo_a, hi_a = nw['drift'] - 1.96 * nw['drift_se'], nw['drift'] + 1.96 * nw['drift_se']
    b = np.sqrt(np.maximum(nw['diff2'], 0))
    lo_b = np.sqrt(np.maximum(nw['diff2'] - 1.96 * nw['diff2_se'], 0))
    hi_b = np.sqrt(nw['diff2'] + 1.96 * nw['diff2_se'])
    vas = F['vasicek_exact']
    par_a = vas['kappa'] * (vas['theta'] - grid)
    par_b = {'Vasicek': np.full_like(grid, F['vasicek_euler']['sigma']),
             'CIR': F['cir_euler']['sigma'] * np.sqrt(grid),
             'CKLS': F['ckls']['sigma'] * grid ** F['ckls']['gamma']}
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    g100 = 100 * grid
    axes[0].fill_between(g100, 100 * lo_a, 100 * hi_a, color=LightGray, alpha=0.6, lw=0, label='95% pointwise band')
    axes[0].plot(g100, 100 * nw['drift'], color=MainBlue, lw=1.5, label='Nadaraya-Watson estimate')
    axes[0].plot(g100, 100 * par_a, color=IDAred, ls='--', lw=1.2, label=r'Vasicek: $\hat\kappa(\hat\theta - r)$')
    axes[0].axhline(0, color=Gray, lw=0.6)
    axes[0].set_xlabel('Short rate r (% p.a.)')
    axes[0].set_ylabel('Drift a(r) (% points per year)')
    axes[0].set_title('Drift: estimated imprecisely', loc='left')
    axes[1].fill_between(g100, 100 * lo_b, 100 * hi_b, color=LightGray, alpha=0.6, lw=0)
    axes[1].plot(g100, 100 * b, color=MainBlue, lw=1.5)
    cols = {'Vasicek': Orange, 'CIR': Purple, 'CKLS': Forest}
    for k, v in par_b.items():
        lab = {'Vasicek': r'Vasicek: $\sigma$', 'CIR': r'CIR: $\sigma\sqrt{r}$',
               'CKLS': rf"CKLS: $\sigma r^{{\gamma}}$, $\hat\gamma$ = {F['ckls']['gamma']:.2f}"}[k]
        axes[1].plot(g100, 100 * v, color=cols[k], lw=1.2, ls='--', label=lab)
    axes[1].set_xlabel('Short rate r (% p.a.)')
    axes[1].set_ylabel('Diffusion b(r) (% points per year)')
    axes[1].set_title('Diffusion: estimated precisely', loc='left')
    fig_legend_bottom(fig, ncol=3, y=0.03)
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    save_fig('ch11_np_diffusion')
    inside = {k: float(np.mean((v >= lo_b) & (v <= hi_b))) for k, v in par_b.items()}
    rel = nw['diff2_se'] / nw['diff2']
    out = dict(h=float(nw['h']), inside=inside, zero_in_drift_band=float(np.mean((lo_a <= 0) & (hi_a >= 0))),
               vas_in_drift_band=float(np.mean((lo_a <= par_a) & (hi_a >= par_a))),
               drift_se_med=float(np.median(nw['drift_se'])), diff_relse_med=float(np.median(rel)),
               drift_ratio=float(np.median(nw['drift_se'] / np.abs(np.sqrt(nw['diff2'])))),
               b_lo=float(b[0]), b_hi=float(b[-1]), r_lo=float(grid[0]), r_hi=float(grid[-1]),
               slope=float(np.polyfit(np.log(grid), np.log(b), 1)[0]))
    return out


def measure_change(g, vs, hp):
    """Change of measure: the market price of risk for the S&P 500; Vasicek bond prices (Feynman-Kac);
    what the VIX identifies in the Heston model (VIX^2 affine in v_t, with parameters under the risk-neutral measure).
    The Vasicek yields use the parameters estimated under P with the explicit assumption lambda = 0 (no risk premium,
    so theta^Q = theta^P); the gap to DGS10 includes the omitted term premium.
    The xi / b correction is a local approximation, valid at v_t = theta^Q: the diffusion of y = a + b v is
    b xi sqrt(v) = xi sqrt(b (y - a)), so its ratio to xi_y sqrt(y) depends on the state."""
    tb = read_fred('DTB3') / 100
    sp = g['sp500']
    rbar = float(tb.loc[sp['start']:].mean())
    th = (sp['mu'] - rbar) / sp['sigma']
    out = {'rbar': rbar, 'theta_sp': th, 'se_theta_sp': 1 / np.sqrt(sp['years'])}
    F = vs['1954-2026']
    k, t, s, r0 = F['kappa'], F['theta'], F['sigma'], vs['last']
    ys = {}
    for tau in (1, 5, 10, 30):
        B = (1 - np.exp(-k * tau)) / k
        A = (t - s ** 2 / (2 * k ** 2)) * (B - tau) - s ** 2 * B ** 2 / (4 * k)
        ys[str(tau)] = float((B * r0 - A) / tau)
    out['vas_yields'] = ys
    out['vas_yinf'] = float(t - s ** 2 / (2 * k ** 2))
    dgs10 = read_fred('DGS10') / 100
    out['dgs10_last'] = float(dgs10.iloc[-1])
    out['dgs10_date'] = str(dgs10.index[-1].date())
    tau = 30 / 365
    out['vix_b'] = {str(kq): float((1 - np.exp(-kq * tau)) / (kq * tau)) for kq in (1.0, 2.5, 5.0, 10.0)}
    out['vix_xi_corr'] = {kq: float(hp['xi'] / b) for kq, b in out['vix_b'].items()}
    return out


# =============================================================================
# 4. JUMPS: MERTON
# =============================================================================
def merton_estimates():
    out = {}
    for k in ['sp500', 'btc', 'bet']:
        r = rets[k].values
        mf = merton_mle(r, DTS[k])
        mo = merton_moments(DTS[k], mf['sigma'], mf['lam'], mf['mu_j'], mf['s_j'], mf['m'])
        ll0 = float(stats.norm.logpdf(r, r.mean(), r.std()).sum())
        tot = mf['sigma'] ** 2 + mf['lam'] * (mf['mu_j'] ** 2 + mf['s_j'] ** 2)
        out[k] = dict(mf, moments=mo, ll_gbm=ll0, lr=2 * (mf['loglik'] - ll0), jump_share=mf['lam'] * (mf['mu_j'] ** 2 + mf['s_j'] ** 2) / tot,
                      data_exkurt=float(stats.kurtosis(r)), data_skew=float(stats.skew(r)))
    return out


def fig_merton_density(me):
    """Return density (log scale): data, the Normal distribution, Merton."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, k in zip(axes, ['sp500', 'btc']):
        r = rets[k].values
        dt = DTS[k]
        mf = me[k]
        h, e = np.histogram(r, bins=120, density=True)
        c = 0.5 * (e[1:] + e[:-1])
        ok = h > 0
        ax.plot(c[ok], h[ok], 'o', ms=3, color=MainBlue, label='Data (histogram)')
        xx = np.linspace(e[0], e[-1], 800)
        ax.plot(xx, stats.norm.pdf(xx, r.mean(), r.std()), color=Orange, lw=1.3, label='Normal distribution (GBM)')
        ax.plot(xx, np.exp(merton_logpdf(xx, dt, mf['m'], mf['sigma'], mf['lam'], mf['mu_j'], mf['s_j'])), color=IDAred,
                lw=1.3, label='Merton jump-diffusion (maximum likelihood)')
        ax.set_yscale('log')
        ax.set_ylim(h[ok].min() / 3, h.max() * 3)
        ax.set_xlabel('Daily log return')
        ax.set_title(LABELS[k], loc='left')
    fig_legend_bottom(plt.gcf(), ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch11_merton_density')


def fig_jumps():
    """Jumps detected by the Lee-Mykland test (alpha = 1%) for the S&P 500 and Bitcoin."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 4.6), sharex=False)
    out = {}
    for ax, k in zip(axes, ['sp500', 'btc']):
        d, crit = lee_mykland(rets[k], K=16, alpha=0.01)
        ax.plot(d.index, 100 * d['r'], color=MainBlue, lw=0.4, label='Daily log return (%)')
        j = d[d['jump']]
        ax.scatter(j.index, 100 * j['r'], s=14, color=IDAred, zorder=3, label='Jump detected (Lee-Mykland, 1% level)')
        ax.set_title(LABELS[k], loc='left')
        years = (d.index[-1] - d.index[0]).days / 365.25
        big = d['r'].abs().sort_values(ascending=False).head(10)
        out[k] = dict(n=int(len(d)), n_jumps=int(d['jump'].sum()), per_year=float(d['jump'].sum() / years), crit=float(crit),
                      share_neg=float((j['r'] < 0).mean()), top10_detected=int(d.loc[big.index, 'jump'].sum()),
                      largest=float(j['r'].abs().max()), smallest=float(j['r'].abs().min()),
                      smallest_date=str(j['r'].abs().idxmin().date()),
                      dates=[str(x.date()) for x in j.index])
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    save_fig('ch11_jumps')
    return out


# =============================================================================
# 5. HESTON
# =============================================================================
def heston_estimates():
    """Heston parameters from the VIX: S&P 500 price and VIX first aligned on common days (returns on the common grid)."""
    hp = heston_from_vix(load_vix(), load_close('sp500'), DT)
    return hp


def fig_heston_paths(hp, g):
    """Three Heston paths with the parameters estimated from the VIX (long-run mean = realised variance)."""
    rng = np.random.default_rng(SEED + 9)
    t, S, V = heston_paths(100.0, hp['theta_p'], g['mu'], hp['kappa'], hp['theta_p'], hp['xi'], hp['rho'], 5.0, 1260, 3, rng)
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.4), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    for i, c in enumerate([MainBlue, IDAred, Forest]):
        axes[0].plot(t, S[:, i], color=c, lw=0.8, label=f'Path {i + 1}')
        axes[1].plot(t, 100 * np.sqrt(V[:, i]), color=c, lw=0.8)
    axes[1].axhline(100 * np.sqrt(hp['theta_p']), color=Gray, ls='--', lw=0.8, label=r'$\sqrt{\theta}$ (long-run volatility)')
    axes[0].set_ylabel('Price')
    axes[1].set_ylabel(r'$\sqrt{v_t}$ (% p.a.)')
    axes[1].set_xlabel('Years')
    axes[0].set_title(rf"Heston: $\kappa$ = {hp['kappa']:.2f}, $\sqrt{{\theta}}$ = {100 * np.sqrt(hp['theta_p']):.1f}%, "
                      rf"$\xi$ = {hp['xi']:.2f}, $\rho$ = {hp['rho']:.2f}", loc='left')
    fig_legend_bottom(fig, ncol=4, y=0.02)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    save_fig('ch11_heston_paths')
    lr = np.diff(np.log(S), axis=0)
    dv = np.diff(V, axis=0)
    # Feller ratio of the simulated parameters (theta = realised variance), not of the VIX ones
    return dict(corr_sim=float(np.corrcoef(lr.ravel(), dv.ravel())[0, 1]),
                feller_sim=float(2 * hp['kappa'] * hp['theta_p'] / hp['xi'] ** 2),
                share_trunc=float(np.mean(V[1:] <= 0)))


def fig_heston_smile(hp):
    """Black-Scholes implied volatility of Heston prices: the effect of rho and of maturity.
    Illustrative: the parameters estimated from the VIX (P-dynamics of the proxy) are used as Q parameters;
    the historical regression does not identify kappa^Q, theta^Q (that would need calibration to option prices)."""
    rng = np.random.default_rng(SEED + 10)
    K = np.linspace(0.80, 1.20, 17)
    base = dict(kappa=hp['kappa'], theta=hp['theta'], xi=hp['xi'], rho=hp['rho'], v0=hp['theta'])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    out = {'K': K}
    for rho, c in [(hp['rho'], IDAred), (0.0, MainBlue), (0.5, Forest)]:
        p = dict(base, rho=rho)
        iv = heston_smile(p, 0.25, K, rng, n_paths=100000, n_steps=63)
        axes[0].plot(K, 100 * iv, 'o-', ms=3, color=c, label=rf'$\rho$ = {rho:.2f}')
        out[f'rho_{rho:.2f}'] = iv
    axes[0].axhline(100 * np.sqrt(hp['theta']), color=Gray, ls='--', lw=0.8, label=r'Black-Scholes: flat at $\sqrt{\theta}$')
    axes[0].set_title('Three months: the sign of the smile follows $\\rho$', loc='left')
    for T, c in [(1 / 12, Teal), (0.25, IDAred), (1.0, Purple)]:
        iv = heston_smile(base, T, K, rng, n_paths=100000, n_steps=max(int(252 * T), 21))
        axes[1].plot(K, 100 * iv, 'o-', ms=3, color=c, label=f'T = {"1 month" if T < 0.1 else ("3 months" if T < 0.5 else "1 year")}')
        out[f'T_{T:.3f}'] = iv
    axes[1].set_title(rf'Fitted $\rho$ = {hp["rho"]:.2f}: the skew flattens with maturity', loc='left')
    for ax in axes:
        ax.set_xlabel('Strike / spot, K/S')
        ax.set_ylabel('Implied volatility (%)')
    legend_outside_bottom(axes[0], ncol=2, y=-0.2)
    legend_outside_bottom(axes[1], ncol=3, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_heston_smile')
    return out


# =============================================================================
# 6. MODELS VS DATA
# =============================================================================
def simulate_stats(model, p, n, dt, n_sim, rng, mu=0.0):
    out = []
    for _ in range(n_sim):
        if model == 'GBM':
            x = gbm_simulate_returns(p['m'], p['sigma'], n, dt, rng)
        elif model == 'Merton':
            x = merton_simulate_returns(p['m'], p['sigma'], p['lam'], p['mu_j'], p['s_j'], n, dt, rng)
        else:
            x = heston_simulate_returns(p, n, dt, rng, mu=mu)
        out.append(stylised(x))
    return out


def fig_models_vs_data(g, me, hp):
    """ACF of |r|, kurtosis and tail index: S&P 500 vs GBM, Merton, Heston (100 simulations each)."""
    rng = np.random.default_rng(SEED + 11)
    r = rets['sp500'].values
    n = len(r)
    hpp = dict(hp, theta=hp['theta_p'])
    S = {'GBM': simulate_stats('GBM', g['sp500'], n, DT, 100, rng),
         'Merton': simulate_stats('Merton', me['sp500'], n, DT, 100, rng),
         'Heston': simulate_stats('Heston', hpp, n, DT, 100, rng, mu=g['sp500']['mu'])}
    d = stylised(r)
    lags = np.arange(1, 51)
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), gridspec_kw={'width_ratios': [1.6, 1, 1]})
    axes[0].plot(lags, d['acf_abs'], color=MODEL_COL['Data'], lw=1.8, label='S&P 500 data')
    for m, s in S.items():
        axes[0].plot(lags, np.median([x['acf_abs'] for x in s], axis=0), color=MODEL_COL[m], lw=1.3, label=m)
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_xlabel('Lag (trading days)')
    axes[0].set_title('ACF of |r| (median of 100 simulations)', loc='left')
    summ = {}
    for ax, key, title in [(axes[1], 'exkurt', 'Excess kurtosis'), (axes[2], 'hill', 'Hill statistic, largest losses (k = 5% of n)')]:
        names = ['Data'] + list(S)
        vals, lo, hi = [d[key]], [0], [0]
        for m in S:
            v = np.array([x[key] for x in S[m]])
            med = np.median(v)
            vals.append(med)
            lo.append(med - np.quantile(v, 0.05))
            hi.append(np.quantile(v, 0.95) - med)
        ax.bar(range(4), vals, color=[MODEL_COL[nm] for nm in names], yerr=[lo, hi], capsize=3, width=0.65)
        ax.set_xticks(range(4))
        ax.set_xticklabels(names, fontsize=8)
        ax.set_title(title, loc='left')
    fig_legend_bottom(fig, ncol=4, y=0.02)
    plt.tight_layout(rect=(0, 0.07, 1, 1))
    save_fig('ch11_models_vs_data')
    for m in S:
        summ[m] = {k: dict(med=float(np.median([x[k] for x in S[m]])), lo=float(np.quantile([x[k] for x in S[m]], 0.05)),
                           hi=float(np.quantile([x[k] for x in S[m]], 0.95)),
                           p_ge=float(np.mean([x[k] >= d[k] for x in S[m]])))
                   for k in ['exkurt', 'skew', 'hill', 'acf_abs1', 'acf_abs_sum20']}
    summ['Data'] = {k: float(d[k]) for k in ['exkurt', 'skew', 'hill', 'acf_abs1', 'acf_abs_sum20']}
    # sensitivity of the Hill statistic to the threshold (k = 2.5%, 5%, 10% of n) for the data
    summ['Data_hill'] = {f'{q:.3f}': float(hill(-r, q)) for q in (0.025, 0.05, 0.10)}
    return summ


# =============================================================================
# 8. CASE STUDY: Bennedsen, Lunde & Pakkanen (2022), rough and persistent volatility
#    Application to SPY (5-minute bars, 2020-2026), Delta = 1 day; benchmarks from Table 3, Panel A
#    (Journal of Financial Econometrics 20(5), 961-1006)
# =============================================================================
def variogram(x, ks):
    """Empirical variogram of order 2: the mean of (x_{i+k} - x_i)^2."""
    x = np.asarray(x)
    return np.array([np.mean((x[k:] - x[:-k]) ** 2) for k in ks])


def alpha_ols(x, m=6):
    """eq. (2.1): OLS of log gamma_2(k) on log k, k = 1..m; alpha = (a1 - 1)/2."""
    ks = np.arange(1, m + 1)
    a1 = np.polyfit(np.log(ks), np.log(variogram(x, ks)), 1)[0]
    return (a1 - 1) / 2


def alpha_nlls_m(x, m, delta=1.0):
    """Noise-robust NLLS (Section 3.1): gamma_2(k) = b0 + b1 (k Delta)^(2 alpha + 1), k = 1..m."""
    ks = np.arange(1, m + 1)
    g = variogram(x, ks)
    f = lambda p: np.sum((g - p[0] - p[1] * (ks * delta) ** (2 * p[2] + 1)) ** 2)
    best = None
    for a0 in (-0.4, -0.2, 0.0, 0.2):
        res = optimize.minimize(f, [g[0] / 4, g[0] / 2, a0], method='L-BFGS-B',
                                bounds=[(0, None), (1e-10, None), (-0.499, 0.499)])
        if best is None or res.fun < best.fun:
            best = res
    return best.x


def cauchy_acf(h, a, b):
    """ACF of the Cauchy class (Section 2.1.1): (1 + |h|^(2 alpha + 1))^(-beta/(2 alpha + 1))."""
    return (1 + np.abs(h) ** (2 * a + 1)) ** (-b / (2 * a + 1))


def rough_vol_spy():
    """Daily log sigma_t from the bipower variation of SPY 5-minute returns; alpha (OLS, NLLS) and beta (Cauchy)."""
    r = load_spy_5m()
    day = r.index.date
    bv = r.groupby(day).apply(lambda x: np.pi / 2 * np.sum(np.abs(x.values[1:]) * np.abs(x.values[:-1])))
    x = 0.5 * np.log(bv.values)                 # log sigma, Delta = 1 day (the constant 1/Delta does not change alpha, beta)
    n = len(x)
    a_ols = alpha_ols(x)
    nl = [alpha_nlls_m(x, m) for m in range(10, 21)]
    a_nl = float(np.mean([p[2] for p in nl]))
    H = int(np.ceil(n ** (1 / 3)))
    lags = np.arange(1, 101)
    rho = acf(x, lags)
    hh = np.arange(1, H + 1)
    b = optimize.minimize_scalar(lambda b: np.sum((rho[:H] - cauchy_acf(hh, a_ols, b)) ** 2),
                                 bounds=(0, 5), method='bounded').x
    rob = optimize.minimize(lambda p: np.sum((np.log(rho[:H]) - p[0] - np.log(cauchy_acf(hh, a_nl, p[1]))) ** 2),
                            [-0.1, 0.2], method='L-BFGS-B', bounds=[(None, 0), (0, 5)]).x
    # short-memory contrast (OU, alpha = 0): log rho(h) = c - lambda h, on the same H lags
    ou = np.polyfit(hh, np.log(rho[:H]), 1)
    return dict(n=n, start=str(bv.index[0]), end=str(bv.index[-1]), H=H, x=x, rho=rho,
                alpha_ols=a_ols, alpha_nlls=a_nl, alpha_nlls_m=[float(p[2]) for p in nl],
                nlls_m15=nl[5], beta_cau=b, beta_cau_star=rob[1], c_star=rob[0],
                ou_lambda=-ou[0], ou_c=ou[1], rho1=rho[0], rho20=rho[19], rho100=rho[99],
                half_life_ou=np.log(2) / -ou[0])


def fig_rough_vol(rv):
    """Left: log-log variogram of log sigma (SPY, Delta = 1 day) with the OLS line (k = 1..6) and NLLS;
    right: sample ACF against the Cauchy class (rough + persistent) and OU (short memory)."""
    x = rv['x']
    ks = np.arange(1, 31)
    g = variogram(x, ks)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    ax = axes[0]
    ax.loglog(ks, g, 'o', color=MainBlue, ms=4, label=r'Empirical variogram of $\log\hat\sigma_t$')
    a1 = 2 * rv['alpha_ols'] + 1
    c0 = np.exp(np.mean(np.log(g[:6]) - a1 * np.log(ks[:6])))
    ax.loglog(ks, c0 * ks ** a1, color=IDAred, lw=1.4,
              label=rf'OLS, k = 1..6: $\hat\alpha$ = {rv["alpha_ols"]:.2f}')
    b0, b1, a = rv['nlls_m15']
    ax.loglog(ks, b0 + b1 * ks ** (2 * a + 1), color=Forest, lw=1.4, ls='--',
              label=rf'NLLS fit, m = 15; mean over m = 10..20: $\hat\alpha^*$ = {rv["alpha_nlls"]:.2f}')
    k10 = ks[:10]
    ax.loglog(k10, g[0] * k10 ** 1.0, color=Orange, lw=1.1, ls=':', label=r'Brownian roughness, $\alpha$ = 0 (slope 1)')
    ax.set_xticks([1, 2, 5, 10, 20, 30])
    ax.set_xticklabels(['1', '2', '5', '10', '20', '30'])
    ax.set_yticks([0.1, 0.2, 0.5, 1.0])
    ax.set_yticklabels(['0.1', '0.2', '0.5', '1.0'])
    ax.minorticks_off()
    ax.set_xlabel('Lag k (trading days)')
    ax.set_ylabel(r'$\hat\gamma_2(k)$')
    ax.set_title('Roughness: variogram of daily log-volatility (log-log)', loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    ax = axes[1]
    lags = np.arange(1, len(rv['rho']) + 1)
    ax.plot(lags, rv['rho'], color=MainBlue, lw=1.6, label=r'Empirical ACF of $\log\hat\sigma_t$')
    ax.plot(lags, np.exp(rv['c_star']) * cauchy_acf(lags, rv['alpha_nlls'], rv['beta_cau_star']), color=Purple, lw=1.4,
            label=rf'Cauchy class, noise-robust: $\hat\beta^*$ = {rv["beta_cau_star"]:.2f} (long memory)')
    ax.plot(lags, np.exp(rv['ou_c'] - rv['ou_lambda'] * lags), color=Amber, lw=1.4, ls='--',
            label=rf'Exponential decay (OU, short memory): half-life {rv["half_life_ou"]:.0f} days')
    ax.axvline(rv['H'], color=Gray, lw=0.6, ls=':')
    ax.text(rv['H'] + 1.5, 0.85, rf'fit on lags 1..{rv["H"]} = $\lceil n^{{1/3}}\rceil$', fontsize=7.5, color='black')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylim(-0.1, 1.0)
    ax.set_xlabel('Lag h (trading days)')
    ax.set_title('Persistence: ACF of daily log-volatility', loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch11_case_rough_spy')


def fig_rough_vs_paper(rv):
    """Table 3, Panel A (E-mini S&P 500, 2011-2014) across scales Delta, against the SPY estimates on the course data, Delta = 1 day."""
    # Table 3, Panel A (E-mini S&P 500 log-volatility, 2011-2014): Delta in minutes (390 = one trading day)
    T = {'delta_min': [10, 15, 30, 65, 130, 390],
         'alpha_ols': [-0.38, -0.35, -0.31, -0.30, -0.32, -0.30],
         'alpha_nlls': [-0.38, -0.37, -0.35, -0.35, -0.35, -0.33],
         'beta_cau': [0.17, 0.18, 0.18, 0.18, 0.00, 0.00],
         'beta_cau_star': [0.18, 0.18, 0.18, 0.18, 0.17, 0.18]}
    xd = np.arange(len(T['delta_min']))
    labs = ['10 min', '15 min', '30 min', '65 min', '130 min', '1 day']
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    for ax, (k1, l1), (k2, l2), ttl, ours in [
            (axes[0], ('alpha_ols', r'Paper: $\hat\alpha_{OLS}$'), ('alpha_nlls', r'Paper: $\hat\alpha^*_{NLLS}$'),
             r'Roughness index $\hat\alpha$', ('alpha_ols', 'alpha_nlls')),
            (axes[1], ('beta_cau', r'Paper: $\hat\beta_{Cauchy}$'), ('beta_cau_star', r'Paper: $\hat\beta^*_{Cauchy}$'),
             r'Memory parameter $\hat\beta$ (Cauchy class)', ('beta_cau', 'beta_cau_star'))]:
        ax.plot(xd - 0.08, T[k1], 'o-', color=MainBlue, ms=5, lw=1, label=l1)
        ax.plot(xd + 0.08, T[k2], 's--', color=IDAred, ms=5, lw=1, label=l2)
        ax.plot([xd[-1] + 0.35], [rv[ours[0]]], 'D', color=Forest, ms=7, label='SPY 2020-2026, course data: OLS / plain')
        ax.plot([xd[-1] + 0.55], [rv[ours[1]]], '^', color=Orange, ms=8, label='SPY 2020-2026, course data: noise-robust')
        ax.annotate('SPY,\n1 day', xy=(xd[-1] + 0.45, max(rv[ours[0]], rv[ours[1]])), xytext=(0, 12),
                    textcoords='offset points', ha='center', fontsize=7.5, color=Forest)
        ax.set_xticks(xd)
        ax.set_xticklabels(labs, fontsize=8)
        ax.set_xlim(-0.4, xd[-1] + 0.9)
        ax.set_xlabel(r'Sampling interval $\Delta$')
        ax.set_title(ttl, loc='left')
    axes[0].axhline(0, color=Gray, lw=0.6, ls=':')
    axes[0].text(0, 0.02, r'$\alpha$ = 0: Brownian roughness', fontsize=7.5, color='black')
    axes[0].set_ylim(-0.5, 0.1)
    axes[1].axhline(1, color=Gray, lw=0.6, ls=':')
    axes[1].text(0, 1.03, r'$\beta$ = 1: long-memory boundary', fontsize=7.5, color='black')
    axes[1].set_ylim(-0.05, 1.2)
    fig_legend_bottom(fig, handles=axes[0].get_legend_handles_labels()[0],
                      labels=['Paper, Table 3A: OLS / plain', 'Paper, Table 3A: noise-robust (*)',
                              'SPY 2020-2026 (course data): OLS / plain', 'SPY 2020-2026 (course data): noise-robust (*)'],
                      ncol=2, y=0.1)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch11_case_rough_paper')


def rough_case():
    rv = rough_vol_spy()
    fig_rough_vol(rv)
    fig_rough_vs_paper(rv)
    return {k: v for k, v in rv.items() if k not in ('x', 'rho', 'nlls_m15')}


# =============================================================================
if __name__ == '__main__' and sys.argv[1:] == ['extra']:
    # only the new sections (estimating diffusions, change of measure), without recomputing the rest
    with open(os.path.join(HERE, 'ch11_results.json')) as f:
        R = json.load(f)
    R['diffusion'] = diffusion_fits()
    R['np_diffusion'] = fig_np_diffusion(R['diffusion'])
    R['measure'] = measure_change(R['gbm'], R['vasicek'], R['heston'])
    with open(os.path.join(HERE, 'ch11_results.json'), 'w') as f:
        json.dump(jsonable(R), f, indent=1)
    print('updated ch11_results.json')
elif __name__ == '__main__' and sys.argv[1:] == ['case']:
    # only the case study (rough and persistent volatility), without recomputing the rest
    with open(os.path.join(HERE, 'ch11_results.json')) as f:
        R = json.load(f)
    R['rough'] = rough_case()
    with open(os.path.join(HERE, 'ch11_results.json'), 'w') as f:
        json.dump(jsonable(R), f, indent=1)
    print('updated ch11_results.json')
elif __name__ == '__main__':
    R = {}
    print('1. Brownian motion')
    R['donsker'] = fig_donsker()
    fig_bm_paths()
    R['qv'] = fig_quadratic_variation()
    R['ito'] = fig_ito()
    R['conv'] = fig_convergence()
    print('2. GBM')
    g = gbm_estimates()
    R['gbm'] = g
    R['fan'] = fig_gbm_fan(g['sp500'])
    R['lognormal'] = fig_lognormal(g['sp500'])
    R['gbm_data'] = fig_gbm_vs_data(g['sp500'])
    R['drift'] = fig_drift_precision(g)
    print('3. OU')
    R['ou'] = fig_ou_paths()
    R['vasicek'] = fig_vasicek()
    R['vix'] = fig_vix_ou()
    print('4. Merton')
    me = merton_estimates()
    R['merton'] = me
    fig_merton_density(me)
    R['jumps'] = fig_jumps()
    print('5. Heston')
    hp = heston_estimates()
    hp['theta_p'] = hp['real_var']
    R['heston'] = hp
    R['heston_sim'] = fig_heston_paths(hp, g['sp500'])
    R['smile'] = fig_heston_smile(hp)
    print('6. Models vs data')
    R['compare'] = fig_models_vs_data(g, me, hp)
    print('7. Estimating diffusions, change of measure')
    R['diffusion'] = diffusion_fits()
    R['np_diffusion'] = fig_np_diffusion(R['diffusion'])
    R['measure'] = measure_change(g, R['vasicek'], hp)
    print('8. Case study: rough and persistent volatility')
    R['rough'] = rough_case()
    R['data'] = {k: dict(n=len(v), start=str(v.index[0].date()), end=str(v.index[-1].date())) for k, v in rets.items()}
    with open(os.path.join(HERE, 'ch11_results.json'), 'w') as f:
        json.dump(jsonable(R), f, indent=1)
    print('saved ch11_results.json')

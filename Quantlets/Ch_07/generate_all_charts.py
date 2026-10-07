"""
All charts and numbers of Chapter 7: Value-at-Risk and Expected Shortfall
==========================================================================
All charts: transparent background, English labels, legend below the plot.
Daily market data of the course: S&P 500, BET (2000-2026), Bitcoin (2014-2026), gold XAU/USD (2000-2026),
ETFs SPY, TLT, GLD; EUR/RON: official BNR reference rate (July 2005-2026).
Convention: level = tail probability alpha (VaR 1%, ES 2.5%); loss L = -r, in % of the position; VaR and ES positive.
The numbers are written to ch7_results.json (read by the slide generators).
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
from mfm_data import MARKETS, LABELS, log_returns, joint_returns, periods_per_year  # noqa: E402
from risk_measures import (hs_var_es, normal_var_es, t_fit, t_var_es, cf_var_es, cf_quantile, gpd_fit,  # noqa: E402
                           gpd_var_es, gpd_se, mean_excess, garch_filter, garch_next, fhs_mc,
                           rolling_conditional)

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
plt.rcParams['axes.titlesize'] = 11
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
Navy     = '#1F2A44'   # reference lines (no grey in charts)
BandBlue = '#C5D2E8'   # light MainBlue tint for confidence / reference bands
Gray, LightGray = Navy, BandBlue   # legacy names kept for importing scripts
Teal     = '#17A2B8'
METHOD_COL = {'HS': MainBlue, 'Normal': Orange, 'Student-t': Forest, 'Cornish-Fisher': Purple, 'EVT (GPD)': IDAred}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
ORDER = list(MARKETS)
METHODS = ['HS', 'Normal', 'Student-t', 'Cornish-Fisher', 'EVT (GPD)']


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


# =============================================================================
# DATA: daily log returns in %, each series on its own calendar; loss L = -r
# =============================================================================
rets = {k: 100 * log_returns(k) for k in MARKETS}
loss = {k: -v for k, v in rets.items()}


def all_methods(L, alpha):
    """VaR and ES at level alpha for all unconditional methods."""
    f = gpd_fit(L, 0.05)
    return {'HS': hs_var_es(L, alpha), 'Normal': normal_var_es(L, alpha), 'Student-t': t_var_es(L, alpha),
            'Cornish-Fisher': cf_var_es(L, alpha), 'EVT (GPD)': gpd_var_es(f, alpha)}


def summary_table():
    """Descriptive statistics and VaR/ES (1%, 2.5%) by method for the five series."""
    rows = {}
    for k in ORDER:
        L = loss[k]
        nu, m, s = t_fit(L)
        f = gpd_fit(L, 0.05)
        row = dict(N=len(L), start=str(L.index[0].date()), mean=L.mean(), sd=L.std(), skew=stats.skew(L),
                   kurt=stats.kurtosis(L), max=L.max(), max_date=str(L.idxmax().date()), t_nu=nu, t_loc=m, t_scale=s,
                   gpd_u=f['u'], gpd_xi=f['xi'], gpd_beta=f['beta'], gpd_nu=f['nu'],
                   gpd_xi_se=gpd_se(f)[0], ppy=periods_per_year(L))
        for a, tag in [(0.01, '1%'), (0.025, '2.5%')]:
            for meth, (v, e) in all_methods(L, a).items():
                row[f'{meth}|VaR {tag}'] = v
                row[f'{meth}|ES {tag}'] = e
        rows[k] = row
    t = pd.DataFrame(rows).T
    t.to_csv(os.path.join(HERE, 'ch7_var_es_table.csv'))
    return t


# =============================================================================
# 1. DEFINITIONS: S&P 500 loss distribution, VaR and ES
# =============================================================================
def fig_loss_distribution():
    L = loss['sp500']
    v, e = hs_var_es(L, 0.01)
    v2, e2 = hs_var_es(L, 0.025)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    bins = np.linspace(-8, 12, 161)
    ax.hist(L, bins=bins, density=True, color=MainBlue, alpha=0.55, label='S&P 500 daily losses, 2000-2026')
    x = np.linspace(-8, 12, 600)
    ax.plot(x, stats.norm.pdf(x, L.mean(), L.std()), color=Orange, lw=1.2, label='Normal distribution, same mean and s.d.')
    ax.axvline(v, color=IDAred, lw=1.3, label=f'VaR 1% = {v:.2f}%')
    ax.axvline(e, color=IDAred, lw=1.3, ls='--', label=f'ES 1% = {e:.2f}%')
    ax.set_xlim(-6, 10)
    ax.set_xlabel('Daily loss L = -r (%)')
    ax.set_ylabel('Density')
    ax.set_title('Loss distribution')
    legend_outside_bottom(ax, 2, -0.2)
    ax = axes[1]
    tail = L[L > 2]
    ax.hist(tail, bins=np.linspace(2, 12, 51), color=MainBlue, alpha=0.55, label='Losses above 2%')
    ax.axvline(v, color=IDAred, lw=1.3, label='VaR 1%')
    ax.axvline(e, color=IDAred, lw=1.3, ls='--', label='ES 1% (mean beyond VaR)')
    ax.axvline(e2, color=Amber, lw=1.3, ls='-.', label=f'ES 2.5% = {e2:.2f}%')
    ax.set_xlabel('Daily loss (%)')
    ax.set_ylabel('Number of days')
    ax.set_title('Right tail of the losses')
    legend_outside_bottom(ax, 2, -0.2)
    plt.tight_layout()
    save_fig('ch7_loss_distribution')
    return dict(var1=v, es1=e, var2_5=v2, es2_5=e2, n_beyond=int((L >= v).sum()), N=len(L))


# =============================================================================
# 2. SUBADDITIVITY: the two-bond counterexample
# =============================================================================
def discrete_var_es(values, probs, alpha):
    """VaR and ES at tail probability alpha for a discrete loss L = -X (Acerbi-Tasche formula).
    VaR_alpha = -inf{x : P(X <= x) > alpha}; ES_alpha = (E[L 1{L > VaR}] + VaR (alpha - P(L > VaR))) / alpha."""
    order = np.argsort(values)
    x, p = np.asarray(values)[order], np.asarray(probs)[order]
    cdf = np.cumsum(p)
    var = x[np.searchsorted(cdf, 1 - alpha - 1e-12)]
    tail = x > var
    es = ((x[tail] * p[tail]).sum() + var * (alpha - p[tail].sum())) / alpha
    return var, es


def bonds_example(p=0.009, lgd=100.0, alpha=0.01):
    """Two independent bonds; each loses lgd with probability p."""
    single = discrete_var_es([0, lgd], [1 - p, p], alpha)
    port = discrete_var_es([0, lgd, 2 * lgd], [(1 - p) ** 2, 2 * p * (1 - p), p ** 2], alpha)
    return dict(p=p, lgd=lgd, alpha=alpha, var1=single[0], es1=single[1], varP=port[0], esP=port[1],
                p_any=1 - (1 - p) ** 2, p_both=p ** 2)


def fig_subadditivity(ex):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    lab = ['VaR 1%', 'ES 1%']
    sums = [2 * ex['var1'], 2 * ex['es1']]
    port = [ex['varP'], ex['esP']]
    xx = np.arange(2)
    ax.bar(xx - 0.2, sums, 0.38, color=MainBlue, label='Bond A + bond B, measured separately')
    ax.bar(xx + 0.2, port, 0.38, color=IDAred, label='Portfolio A + B, measured jointly')
    for i in range(2):
        ax.text(xx[i] - 0.2, sums[i] + 3, f'{sums[i]:.1f}', ha='center', fontsize=8)
        ax.text(xx[i] + 0.2, port[i] + 3, f'{port[i]:.1f}', ha='center', fontsize=8)
    ax.set_xticks(xx)
    ax.set_xticklabels(lab)
    ax.set_ylabel('Risk (loss units)')
    ax.set_ylim(0, max(sums + port) * 1.2)
    ax.set_title('Two independent bonds, default probability 0.9% each')
    legend_outside_bottom(ax, 2, -0.15)
    save_fig('ch7_subadditivity')


# =============================================================================
# 3. VaR and ES as functions of the tail probability (S&P 500)
# =============================================================================
def fig_var_levels():
    L = loss['sp500']
    levels = np.geomspace(0.05, 0.001, 50)     # tail probability alpha, from 5% down to 0.1%
    f = gpd_fit(L, 0.05)
    tp = t_fit(L)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    curves = {}
    for meth in METHODS:
        vv, ee = [], []
        for a in levels:
            if meth == 'HS':
                v, e = hs_var_es(L, a)
            elif meth == 'Normal':
                v, e = normal_var_es(L, a)
            elif meth == 'Student-t':
                v, e = t_var_es(L, a, tp)
            elif meth == 'Cornish-Fisher':
                v, e = cf_var_es(L, a)
            else:
                v, e = gpd_var_es(f, a)
            vv.append(v)
            ee.append(e)
        curves[meth] = (vv, ee)
        axes[0].plot(100 * levels, vv, color=METHOD_COL[meth], lw=1.4 if meth == 'HS' else 1.1, label=meth)
        axes[1].plot(100 * levels, ee, color=METHOD_COL[meth], lw=1.4 if meth == 'HS' else 1.1, label=meth)
    for ax, t in zip(axes, ['Value-at-Risk', 'Expected Shortfall']):
        ax.set_xscale('log')
        ax.invert_xaxis()
        ax.set_xticks([5, 2.5, 1, 0.5, 0.1])
        ax.set_xticklabels(['5', '2.5', '1', '0.5', '0.1'])
        ax.set_xlabel('Tail probability alpha (%)')
        ax.set_ylabel('Daily loss (%)')
        ax.set_title(f'{t}, S&P 500 2000-2026')
        ax.set_ylim(0, 16)
        legend_outside_bottom(ax, 3, -0.2)
    plt.tight_layout()
    save_fig('ch7_var_levels')
    return {m: dict(var0_1=curves[m][0][-1], es0_1=curves[m][1][-1]) for m in METHODS}


# =============================================================================
# 4. METHODS x ASSETS
# =============================================================================
def fig_methods_assets(t):
    fig, axes = plt.subplots(1, 5, figsize=(12, 3.3))
    for ax, k in zip(axes, ORDER):
        vals = [t.loc[k, f'{m}|VaR 1%'] for m in METHODS]
        es = [t.loc[k, f'{m}|ES 2.5%'] for m in METHODS]
        xx = np.arange(len(METHODS))
        ax.bar(xx - 0.2, vals, 0.38, color=[METHOD_COL[m] for m in METHODS])
        ax.bar(xx + 0.2, es, 0.38, color=[METHOD_COL[m] for m in METHODS], alpha=0.45, hatch='///', edgecolor='white')
        ax.set_xticks(xx)
        ax.set_xticklabels(['HS', 'Normal', 't', 'CF', 'EVT'], fontsize=8)
        ax.set_title(LABELS[k].replace(' (reference rate)', ''), fontsize=9)
        if k == ORDER[0]:
            ax.set_ylabel('Daily loss (%)')
    from matplotlib.patches import Patch
    h = [Patch(color=MainBlue, label='Solid: VaR 1%'), Patch(facecolor=MainBlue, alpha=0.45, hatch='///', edgecolor='white',
                                                             label='Hatched: ES 2.5%')]
    h += [Patch(color=METHOD_COL[m], label=m) for m in METHODS]
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=7, frameon=False)
    plt.tight_layout()
    save_fig('ch7_methods_assets')


# =============================================================================
# 5. Rolling-window HS vs FHS (S&P 500 and Bitcoin)
# =============================================================================
def fig_rolling(name, d, fname, title, start):
    d = d.loc[start:]
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.bar(d.index, d['loss'].clip(lower=0), width=1.5, color=Teal, alpha=0.45, label='Daily loss (gains set to 0)')
    ax.plot(d.index, d['hs_var'], color=MainBlue, lw=1.1, label='HS VaR 1% (500-day window)')
    ax.plot(d.index, d['fhs_var'], color=IDAred, lw=0.8, label='FHS VaR 1% (GARCH-filtered)')
    exc_h = d['loss'] > d['hs_var']
    exc_f = d['loss'] > d['fhs_var']
    ax.scatter(d.index[exc_h], d['loss'][exc_h], s=6, color=MainBlue, zorder=3, label='Loss above HS VaR')
    ax.scatter(d.index[exc_f], d['loss'][exc_f], s=6, marker='x', color=IDAred, zorder=3, label='Loss above FHS VaR')
    ax.set_ylabel('Daily loss (%)')
    ax.set_title(title)
    ax.set_ylim(0, np.percentile(d['loss'], 99.95) * 1.1)
    legend_outside_bottom(ax, 3, -0.14)
    save_fig(fname)
    return dict(n=len(d), exc_hs=float(exc_h.mean()), exc_fhs=float(exc_f.mean()),
                exc_cevt=float((d['loss'] > d['cevt_var']).mean()), exc_ng=float((d['loss'] > d['ngarch_var']).mean()),
                hs_min=float(d['hs_var'].min()), hs_max=float(d['hs_var'].max()),
                fhs_min=float(d['fhs_var'].min()), fhs_max=float(d['fhs_var'].max()),
                fhs_max_date=str(d['fhs_var'].idxmax().date()), first=str(d.index[0].date()),
                last=str(d.index[-1].date()))


# =============================================================================
# 6. Conditional VaR/ES for the next day (21 September 2026)
# =============================================================================
def conditional_now():
    out = {}
    for k in ORDER:
        r = rets[k]
        params, mu, sig = garch_filter(r)
        z = ((r - mu) / sig).dropna()
        nz = -z.values
        m1, s1 = garch_next(r, params)
        fz = gpd_fit(nz, 0.10)
        row = dict(mu=m1, sigma=s1, sigma_uncond=r.std(), omega=params.iloc[2], alpha=params.iloc[3], beta=params.iloc[4],
                   phi=params.iloc[1], zxi=fz['xi'])
        for a, tag in [(0.01, '1'), (0.025, '2_5')]:
            q = np.quantile(nz, 1 - a)
            row[f'fhs_var{tag}'] = -m1 + s1 * q
            row[f'fhs_es{tag}'] = -m1 + s1 * nz[nz >= q].mean()
            v, e = gpd_var_es(fz, a)
            row[f'cevt_var{tag}'] = -m1 + s1 * v
            row[f'cevt_es{tag}'] = -m1 + s1 * e
            row[f'ng_var{tag}'] = -m1 + s1 * stats.norm.ppf(1 - a)
            row[f'ng_es{tag}'] = -m1 + s1 * stats.norm.pdf(stats.norm.ppf(a)) / a
            row[f'zq{tag}'] = q
        out[k] = row
    pd.DataFrame(out).T.to_csv(os.path.join(HERE, 'ch7_conditional_now.csv'))
    return out


# =============================================================================
# 7. THE HORIZON: square-root-of-time rule and FHS Monte Carlo
# =============================================================================
def horizon_ratios(hs=(1, 2, 5, 10, 20)):
    """Empirical h-day VaR 1% (overlapping sums) divided by sqrt(h) times the one-day VaR 1%."""
    out = {}
    for k in ORDER:
        r = rets[k]
        v1 = hs_var_es(-r, 0.01)[0]
        e1 = hs_var_es(-r, 0.025)[1]
        row = {}
        for h in hs:
            rh = r.rolling(h).sum().dropna()
            row[h] = hs_var_es(-rh, 0.01)[0] / (np.sqrt(h) * v1)
            row[f'es{h}'] = hs_var_es(-rh, 0.025)[1] / (np.sqrt(h) * e1)
        acf1 = r.autocorr(1)
        row['rho1'] = acf1
        out[k] = row
    return out


def fig_horizon(ratios, mc):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    ax = axes[0]
    cols = {'sp500': MainBlue, 'bet': IDAred, 'btc': Amber, 'eurron': Forest, 'gold': Purple}
    hs = [1, 2, 5, 10, 20]
    for k in ORDER:
        ax.plot(hs, [ratios[k][h] for h in hs], marker='o', ms=3, color=cols[k], label=LABELS[k])
    ax.axhline(1, color=Gray, ls=':', lw=1)
    ax.set_xlabel('Horizon h (days)')
    ax.set_ylabel('VaR 1%(h) / (sqrt(h) VaR 1%(1))')
    ax.set_title('Empirical h-day VaR vs square-root-of-time rule')
    legend_outside_bottom(ax, 2, -0.2)
    ax = axes[1]
    ax.hist(mc['sim'], bins=200, density=True, color=MainBlue, alpha=0.5, label='FHS Monte Carlo, 10-day loss')
    ax.axvline(mc['mc_var'], color=IDAred, lw=1.3, label=f"MC VaR 1% = {mc['mc_var']:.2f}%")
    ax.axvline(mc['sqrt_var'], color=Amber, lw=1.3, ls='--', label=f"sqrt(10) x 1-day FHS VaR = {mc['sqrt_var']:.2f}%")
    ax.axvline(mc['uncond_var'], color=Purple, lw=1.3, ls=':', label=f"sqrt(10) x 1-day HS VaR = {mc['uncond_var']:.2f}%")
    ax.set_xlim(-12, 16)
    ax.set_xlabel('10-day loss (%)')
    ax.set_ylabel('Density')
    ax.set_title('S&P 500: 10-day loss from 18 Sep 2026')
    legend_outside_bottom(ax, 1, -0.2)
    plt.tight_layout()
    save_fig('ch7_horizon')


def mc_horizon(k='sp500', h=10):
    r = rets[k]
    params, mu, sig = garch_filter(r)
    z = ((r - mu) / sig).dropna().values
    sim = fhs_mc(r, params, z, h, n_paths=200_000, seed=SEED)
    m1, s1 = garch_next(r, params)
    nz = -z
    v1 = -m1 + s1 * np.quantile(nz, 1 - 0.01)
    mc_var, mc_es = hs_var_es(sim, 0.01)
    return dict(sim=sim, mc_var=mc_var, mc_es=mc_es, mc_es2_5=hs_var_es(sim, 0.025)[1], sqrt_var=np.sqrt(h) * v1,
                one_day=v1, uncond_var=np.sqrt(h) * hs_var_es(-r, 0.01)[0], sigma_now=s1, sigma_uncond=r.std())


# =============================================================================
# 8. PORTFOLIO: marginal and component VaR (Euler allocation)
# =============================================================================
PORT = ['SPY', 'TLT', 'GLD', 'BTC']
W = np.array([0.40, 0.30, 0.20, 0.10])


def portfolio_components():
    lr = joint_returns(PORT, start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)           # simple returns (%), which aggregate across the portfolio
    rp = R.values @ W
    Lp = -rp
    z1 = stats.norm.ppf(1 - 0.01)         # z_{1-alpha}, alpha = 1%
    S = np.cov(R.values.T)
    sp = np.sqrt(W @ S @ W)
    mvar = z1 * (S @ W) / sp            # marginal VaR (Normal, mean ignored)
    cvar = W * mvar                      # component VaR; the sum equals the portfolio VaR
    var_p = z1 * sp
    var_ind = z1 * np.sqrt(np.diag(S)) * W
    # historical component ES: E[-w_i R_i | L_p >= VaR_p]
    v_hs, es_hs = hs_var_es(Lp, 0.025)
    tail = Lp >= v_hs
    ces = -(R.values[tail] * W).mean(axis=0)
    es_ind = np.array([hs_var_es(-R.values[:, i] * W[i], 0.025)[1] for i in range(len(W))])
    corr = np.corrcoef(R.values.T)
    return dict(start=str(lr.index[0].date()), N=len(lr), sd=np.sqrt(np.diag(S)), corr=corr, sigma_p=sp, var_p=var_p,
                mvar=mvar, cvar=cvar, cvar_share=cvar / var_p, var_undiv=var_ind.sum(), es_p=es_hs, var_hs=v_hs,
                ces=ces, ces_share=ces / es_hs, es_undiv=es_ind.sum())


def fig_components(pc):
    fig, ax = plt.subplots(figsize=(8, 3.3))
    xx = np.arange(len(PORT))
    ax.bar(xx - 0.27, 100 * W, 0.26, color=Teal, label='Weight')
    ax.bar(xx, 100 * pc['cvar_share'], 0.26, color=MainBlue, label='Share of VaR 1% (Normal, Euler)')
    ax.bar(xx + 0.27, 100 * pc['ces_share'], 0.26, color=IDAred, label='Share of ES 2.5% (historical, Euler)')
    for i in range(len(PORT)):
        ax.text(xx[i] + 0.27, 100 * pc['ces_share'][i] + 1, f"{100 * pc['ces_share'][i]:.0f}", ha='center', fontsize=7)
        ax.text(xx[i], 100 * pc['cvar_share'][i] + 1, f"{100 * pc['cvar_share'][i]:.0f}", ha='center', fontsize=7)
    ax.set_xticks(xx)
    ax.set_xticklabels(['SPY (US equity)', 'TLT (US Treasuries)', 'GLD (gold)', 'Bitcoin'])
    ax.set_ylabel('%')
    ax.axhline(0, color='black', lw=0.5)
    ax.set_title('Who contributes the risk? Portfolio 40/30/20/10, 2014-2026')
    legend_outside_bottom(ax, 3, -0.14)
    save_fig('ch7_components')


# =============================================================================
# 9. EVT: mean excess, GPD tail, monthly maxima (GEV)
# =============================================================================
def fig_mean_excess():
    L = loss['sp500'].values
    us = np.quantile(L, np.linspace(0.80, 0.995, 60))
    me, n = mean_excess(L, us)
    f = gpd_fit(L, 0.05)
    fig, ax = plt.subplots(figsize=(7.5, 3.3))
    ax.plot(us, me, 'o', ms=3, color=MainBlue, label='Empirical mean excess e(u)')
    uu = np.linspace(f['u'], us[-1], 50)
    ax.plot(uu, (f['beta'] + f['xi'] * (uu - f['u'])) / (1 - f['xi']), color=IDAred,
            label='GPD implied: (beta + xi (u - u0)) / (1 - xi)')
    ax.axvline(f['u'], color='black', ls=':', label=f"Threshold u0 = {f['u']:.2f}% (top 5% of losses above it)")
    ax.set_xlabel('Threshold u (daily loss, %)')
    ax.set_ylabel('Mean excess e(u) (%)')
    ax.set_title('S&P 500 losses: mean excess plot')
    legend_outside_bottom(ax, 2, -0.2)
    save_fig('ch7_mean_excess')
    return dict(u=f['u'], me_u=float(me[np.argmin(np.abs(us - f['u']))]))


def fig_gpd_tail(t):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    for ax, k in zip(axes, ['sp500', 'btc']):
        L = loss[k].values
        f = gpd_fit(L, 0.05)
        xs = np.sort(L[L > f['u']])
        emp = 1 - np.arange(len(xs)) / len(xs)
        emp = emp * f['nu'] / f['n']
        ax.loglog(xs, emp, 'o', ms=2.5, color=MainBlue, label='Empirical tail P(L >= x)')
        xx = np.linspace(f['u'], xs[-1] * 1.3, 200)
        gp = f['nu'] / f['n'] * stats.genpareto.sf(xx - f['u'], f['xi'], scale=f['beta'])
        ax.loglog(xx, gp, color=IDAred, label=f"GPD, xi = {f['xi']:.2f}")
        ax.loglog(xx, stats.norm.sf(xx, L.mean(), L.std()), color=Orange, ls='--', label='Normal distribution')
        nu, m, s = t_fit(L)
        ax.loglog(xx, stats.t.sf(xx, nu, m, s), color=Forest, ls='-.', label=f'Student-t, nu = {nu:.1f}')
        ax.set_ylim(1e-6, 0.08)
        ax.set_xlabel('Daily loss x (%)')
        ax.set_ylabel('Exceedance probability')
        ax.set_title(f'{LABELS[k]}: largest 5% of daily losses')
        legend_outside_bottom(ax, 2, -0.2)
    plt.tight_layout()
    save_fig('ch7_gpd_tail')


def fig_gev():
    L = loss['sp500']
    M = L.groupby([L.index.year, L.index.month]).max()
    n_block = L.groupby([L.index.year, L.index.month]).size().mean()
    c, loc, scale = stats.genextreme.fit(M.values)
    xi = -c
    rl10 = stats.genextreme.ppf(1 - 1 / 120, c, loc, scale)
    rl30 = stats.genextreme.ppf(1 - 1 / 360, c, loc, scale)
    var1 = stats.genextreme.ppf((1 - 0.01) ** n_block, c, loc, scale)       # VaR 1%
    var0_1 = stats.genextreme.ppf((1 - 0.001) ** n_block, c, loc, scale)    # VaR 0.1%
    fig, ax = plt.subplots(figsize=(7.5, 3.3))
    ax.hist(M.values, bins=50, density=True, color=MainBlue, alpha=0.5, label='Monthly maximum daily loss, S&P 500')
    x = np.linspace(M.min(), M.max() * 1.1, 400)
    ax.plot(x, stats.genextreme.pdf(x, c, loc, scale), color=IDAred, label=f'GEV fit, xi = {xi:.2f}')
    ax.axvline(rl10, color=Amber, ls='--', label=f'10-year return level = {rl10:.2f}%')
    ax.set_xlabel('Largest daily loss in the month (%)')
    ax.set_ylabel('Density')
    ax.set_title('Block maxima: one maximum per calendar month, 2000-2026')
    legend_outside_bottom(ax, 2, -0.2)
    save_fig('ch7_gev')
    return dict(n_blocks=len(M), n_block=n_block, xi=xi, mu=loc, sigma=scale, rl10=rl10, rl30=rl30, var1=var1,
                var0_1=var0_1, n_above_rl10=int((M > rl10).sum()), max=float(M.max()))


# =============================================================================
# 10. Conditional EVT (McNeil & Frey) vs HS on the S&P 500
# =============================================================================
def fig_cond_evt(d):
    d = d.loc['2018-01-01':]
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.bar(d.index, d['loss'].clip(lower=0), width=1.5, color=Teal, alpha=0.45, label='Daily loss (gains set to 0)')
    ax.plot(d.index, d['hs_var'], color=MainBlue, lw=1.1, label='HS VaR 1% (500 days)')
    ax.plot(d.index, d['ngarch_var'], color=Orange, lw=0.8, ls='--', label='GARCH with Normal shocks, VaR 1%')
    ax.plot(d.index, d['cevt_var'], color=IDAred, lw=0.8, label='Conditional EVT VaR 1% (McNeil-Frey)')
    ax.set_ylabel('Daily loss (%)')
    ax.set_ylim(0, 12)
    ax.set_title('S&P 500, 2018-2026: unconditional vs conditional VaR')
    legend_outside_bottom(ax, 2, -0.14)
    save_fig('ch7_cond_evt')


# =============================================================================
# 11. BASEL: VaR 1% vs ES 2.5%
# =============================================================================
def fig_basel(t):
    fig, ax = plt.subplots(figsize=(8, 3.3))
    xx = np.arange(len(ORDER))
    v = np.array([t.loc[k, 'HS|VaR 1%'] for k in ORDER], dtype=float)
    e = np.array([t.loc[k, 'HS|ES 2.5%'] for k in ORDER], dtype=float)
    ax.bar(xx - 0.2, v, 0.38, color=MainBlue, label='VaR 1% (Basel 1996)')
    ax.bar(xx + 0.2, e, 0.38, color=IDAred, label='ES 2.5% (FRTB, 2019)')
    for i in range(len(ORDER)):
        ax.text(xx[i] + 0.2, e[i] + 0.15, f'x{e[i] / v[i]:.2f}', ha='center', fontsize=8)
    ax.set_xticks(xx)
    ax.set_xticklabels([LABELS[k].replace(' (reference rate)', '') for k in ORDER])
    ax.set_ylabel('Daily loss (%), historical simulation')
    ax.set_title('From VaR 1% to ES 2.5%: ratio ES/VaR above each pair')
    legend_outside_bottom(ax, 2, -0.14)
    save_fig('ch7_basel')
    return {k: float(e[i] / v[i]) for i, k in enumerate(ORDER)}


# =============================================================================
# 12. LIQUIDITY: liquidity-adjusted VaR (Bangia et al.), an illustration
# =============================================================================
SPREAD_MEAN, SPREAD_SD, SPREAD_A = 0.5, 0.3, 3.0     # illustrative assumptions for the relative spread (%)


def liquidity(sym='TLV', position=1_000_000):
    """Historical VaR 1% over the last two years for a BVB stock + the cost of exiting the position at half the spread."""
    r = 100 * (np.exp(joint_returns([sym]).loc['2024-09-18':][sym]) - 1)   # simple returns: the exact money loss
    v = hs_var_es(-r, 0.01)[0]
    col = 0.5 * (SPREAD_MEAN + SPREAD_A * SPREAD_SD)
    return dict(sym=sym, N=len(r), var1=v, col=col, lvar=v + col, ratio=(v + col) / v,
                var_amt=v / 100 * position, col_amt=col / 100 * position, lvar_amt=(v + col) / 100 * position)


# =============================================================================
# 13. CASE STUDY: Chronopoulos, Raftapostolos & Kapetanios (2024), JFEc 22(3), Table 6 (alpha = 1%)
# RMSFE relative to linear quantile regression; values from Table 6 of the paper
# =============================================================================
CRK_METHODS = ['Polynomial', 'B-splines', 'Linear MIDAS', 'Deep', 'Deep LASSO', 'Deep ridge', 'Deep elastic net',
               'Deep MIDAS']
CRK_TABLE6_1PCT = {
    'GARCH(1,1)':        [0.909, 0.791, 1.083, 0.346, 0.236, 0.177, 0.146, 0.346],
    'RiskMetrics':       [0.780, 0.570, 1.066, 0.289, 0.141, 0.207, 0.239, 0.246],
    'CAViaR SAV':        [1.000, 1.511, 0.838, 0.198, 0.024, 0.225, 0.498, 0.850],
    'Asymmetric slope':  [1.000, 1.040, 4.918, 0.235, 0.096, 0.014, 0.037, 0.601],
}


def fig_crk_table6():
    """Table 6 of Chronopoulos et al. (2024), alpha = 1%: relative RMSFE by method and predictor set."""
    cols = [MainBlue, IDAred, Forest, Orange]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    xx = np.arange(len(CRK_METHODS))
    w = 0.2
    for i, (lab, v) in enumerate(CRK_TABLE6_1PCT.items()):
        ax.bar(xx + (i - 1.5) * w, v, w * 0.95, color=cols[i], label=f'Predictors: {lab}')
    ax.set_yscale('log')
    ax.set_ylim(0.007, 16)
    ax.axhline(1.0, color='black', lw=0.9, ls='--')
    ax.text(len(CRK_METHODS) - 0.5, 1.12, 'Linear quantile regression = 1', ha='right', va='bottom', fontsize=8,
            color='black')
    ax.axvline(2.5, color=Gray, lw=0.6, ls=':')
    ax.text(0.9, 11.0, 'Flexible, not deep', ha='center', fontsize=8.5, color=Orange, fontweight='bold')
    ax.text(5.0, 11.0, 'Deep neural network quantile regression', ha='center', fontsize=8.5, color=MainBlue,
            fontweight='bold')
    for i, v in enumerate(CRK_TABLE6_1PCT.values()):       # extreme values of Table 6
        for j, y in enumerate(v):
            if y > 2 or y < 0.03:
                ax.text(xx[j] + (i - 1.5) * w, y * 1.12, f'{y:.3f}', ha='center',
                        va='bottom', fontsize=7.5, color='black')
    ax.set_xticks(xx)
    ax.set_xticklabels([m.replace(' ', '\n', 1) if m.startswith('Deep ') or m.startswith('Linear') else m
                        for m in CRK_METHODS], fontsize=8)
    ax.set_yticks([0.01, 0.1, 1])
    ax.set_yticklabels(['0.01', '0.1', '1'])
    ax.set_ylabel('RMSFE relative to linear quantile regression (log scale)')
    ax.set_title('S&P 500, VaR 1%: relative RMSFE by method and predictor set (Chronopoulos et al., 2024, Table 6)')
    legend_outside_bottom(ax, 4, -0.2)
    save_fig('ch7_crk_table6')
    v = np.array(list(CRK_TABLE6_1PCT.values()))
    return dict(deep_min=float(v[:, 3:7].min()), deep_max=float(v[:, 3:7].max()),
                share_deep_below1=float((v[:, 3:] < 1).mean()), share_flex_above1=float((v[:, :3] >= 1).mean()))


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


if __name__ == '__main__':
    RES = {}
    t = summary_table()
    RES['table'] = {k: {c: (v if isinstance(v, str) else float(v)) for c, v in row.items()} for k, row in t.iterrows()}
    RES['loss_dist'] = fig_loss_distribution()
    ex = bonds_example()
    RES['bonds'] = ex
    fig_subadditivity(ex)
    RES['levels'] = fig_var_levels()
    fig_methods_assets(t)
    d_sp = rolling_conditional(rets['sp500'], 2004)
    d_btc = rolling_conditional(rets['btc'], 2017)
    d_sp.to_csv(os.path.join(HERE, 'ch7_rolling_sp500.csv'))
    d_btc.to_csv(os.path.join(HERE, 'ch7_rolling_btc.csv'))
    RES['roll_sp'] = fig_rolling('sp500', d_sp, 'ch7_hs_fhs_sp500', 'S&P 500, 2006-2026: historical vs filtered historical simulation', '2006-01-01')
    RES['roll_btc'] = fig_rolling('btc', d_btc, 'ch7_hs_fhs_btc', 'Bitcoin, 2017-2026: historical vs filtered historical simulation', '2017-01-01')
    fig_cond_evt(d_sp)
    RES['cond_evt_sp_2018'] = dict(exc_cevt=float((d_sp.loc['2018':, 'loss'] > d_sp.loc['2018':, 'cevt_var']).mean()),
                                   exc_ng=float((d_sp.loc['2018':, 'loss'] > d_sp.loc['2018':, 'ngarch_var']).mean()),
                                   exc_hs=float((d_sp.loc['2018':, 'loss'] > d_sp.loc['2018':, 'hs_var']).mean()),
                                   n=int(len(d_sp.loc['2018':])))
    RES['now'] = conditional_now()
    RES['horizon'] = horizon_ratios()
    mc = mc_horizon()
    fig_horizon(RES['horizon'], mc)
    RES['mc'] = {k: v for k, v in mc.items() if k != 'sim'}
    pc = portfolio_components()
    RES['port'] = pc
    fig_components(pc)
    RES['me'] = fig_mean_excess()
    fig_gpd_tail(t)
    RES['gev'] = fig_gev()
    RES['basel'] = fig_basel(t)
    RES['liq'] = liquidity()
    RES['crk'] = fig_crk_table6()
    with open(os.path.join(HERE, 'ch7_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved ch7_results.json')

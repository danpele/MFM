"""
Generator pentru graficele din Capitolul 3: Modele factoriale si evaluarea activelor
===================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date: ETF-uri sectoriale si factoriale SUA, S&P 500 (SPY), actiuni BVB si indicele BET
(data/market); factorii Fama-French, momentum si cele 25 de portofolii marime x B/M
(Kenneth French Data Library.
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
from mfm_data import (prices, price, log_returns, french, factors, ols_hac, grs_test,
                      SECTORS, SECTORS_ALL, SECTOR_NAMES, FACTOR_ETFS, BVB, BVB_NAMES)

# Stil standard MFM (identic cu SFM): transparent + ENG + legenda jos
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

# Culori brand
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Gray     = '#7F7F7F'
LightGray = '#DADADA'
PALETTE = [MainBlue, IDAred, Forest, Amber, Orange, Purple, Crimson, '#795548', '#17A2B8', '#6F42C1', '#20C997']

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
MAX_ABS_RET = 0.5        # prag pentru erori de date in seriile BVB (log-randament zilnic)


def save_fig(name):
    """Salveaza figura ca PDF si PNG transparent."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Plaseaza legenda in afara graficului, jos-centru."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


# =============================================================================
# DATE COMUNE
# =============================================================================
def monthly_excess(symbols, start='1999-01-01'):
    """Randamente lunare simple in exces fata de RF (T-bill la o luna), pe lunile comune."""
    p = prices(symbols).resample('ME').last()
    r = p.pct_change().dropna()
    F = factors('M')
    idx = r.index.intersection(F.index)
    r = r.loc[idx].loc[start:]
    F = F.loc[r.index]
    return r.sub(F['RF'], axis=0), F


def daily_excess_one(symbol, start=None):
    """Randamentul zilnic in exces al unui singur activ, pe calendarul factorilor.

    Se pastreaza doar zilele in care exista si pretul din ziua de tranzactionare precedenta
    (altfel randamentul ar acoperi mai multe zile, iar factorii doar una).
    """
    s = price(symbol)
    F = factors('D')
    s = s.loc[s.index.isin(F.index)]
    cal = pd.Series(np.arange(len(F)), index=F.index)
    pos = cal.loc[s.index].values
    r = s.pct_change()
    consecutive = np.r_[False, np.diff(pos) == 1]
    r = r[consecutive].dropna()
    if start:
        r = r.loc[start:]
    Fx = F.loc[r.index]
    return (r - Fx['RF']).rename(symbol), Fx


def daily_excess(symbols, start=None):
    """Compatibilitate: dictionar {simbol: (exces, factori)} pe calendarul fiecarui activ."""
    return {s: daily_excess_one(s, start) for s in symbols}


# =============================================================================
# FIG 1: Frontiera eficienta, CML si portofoliul tangent (ETF-uri sectoriale)
# =============================================================================
def fig_frontier():
    S = [s + '.US' for s in SECTORS]
    ex, F = monthly_excess(S + ['SPY.US'])
    mu = ex[S].mean().values * 12
    cov = ex[S].cov().values * 12
    ones = np.ones(len(S))
    inv = np.linalg.inv(cov)
    w_tan = inv @ mu / (ones @ inv @ mu)
    mu_t, sd_t = w_tan @ mu, np.sqrt(w_tan @ cov @ w_tan)
    # frontiera (fara restrictii) in spatiul excesului de randament
    A, B, C = ones @ inv @ ones, ones @ inv @ mu, mu @ inv @ mu
    targets = np.linspace(-0.02, 0.20, 200)
    sd_f = np.sqrt((A * targets ** 2 - 2 * B * targets + C) / (A * C - B ** 2))
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.plot(sd_f, targets, color=MainBlue, lw=1.2, label='Efficient frontier (risky sectors)')
    xs = np.linspace(0, 0.30, 50)
    ax.plot(xs, mu_t / sd_t * xs, color=IDAred, lw=1.0, ls='--', label='Capital market line (CML)')
    ax.plot(sd_t, mu_t, '*', ms=11, color=IDAred, label='Tangency portfolio')
    sd_i = np.sqrt(np.diag(cov))
    ax.scatter(sd_i, mu, s=18, color=Purple, zorder=3, label='Sector ETFs')
    for s, x, y in zip(SECTORS, sd_i, mu):
        ax.annotate(s, (x, y), xytext=(3, 2), textcoords='offset points', fontsize=6.5, color='black')
    spy_mu, spy_sd = ex['SPY.US'].mean() * 12, ex['SPY.US'].std() * np.sqrt(12)
    ax.plot(spy_sd, spy_mu, 'o', ms=6, color=Forest, label='S&P 500 (SPY)')
    ax.set_xlim(0, 0.32)
    ax.set_ylim(-0.02, 0.20)
    ax.set_xlabel('Volatility (annualised)')
    ax.set_ylabel('Mean excess return (annualised)')
    ax.set_title(f'US sector ETFs, monthly {ex.index[0]:%b %Y} - {ex.index[-1]:%b %Y}: in-sample frontier',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    plt.tight_layout()
    save_fig('ch3_frontier')
    w = pd.Series(w_tan, index=SECTORS)
    return dict(start=str(ex.index[0].date()), end=str(ex.index[-1].date()), T=len(ex),
                tan_mu=mu_t, tan_sd=sd_t, tan_sr=mu_t / sd_t, spy_sr=spy_mu / spy_sd,
                spy_mu=spy_mu, spy_sd=spy_sd, w_tan=w.round(3).to_dict(),
                w_neg=int((w < 0).sum()))


# =============================================================================
# FIG 2: Dreapta pietei de capital (SML) pe cele 25 de portofolii Fama-French
# =============================================================================
def sml_data(start='1963-07-31'):
    F = factors('M')
    P = french('p25', 'M').loc[start:F.index[-1]]
    Fx = F.loc[P.index]
    ex = P.sub(Fx['RF'], axis=0)
    mk = Fx['Mkt-RF']
    rows = []
    for c in ex.columns:
        b, se, t, e, r2 = ols_hac(ex[c].values, mk.values)
        rows.append((c, b[1], b[0] * 12, t[0], ex[c].mean() * 12))
    res = pd.DataFrame(rows, columns=['port', 'beta', 'alpha', 't_alpha', 'avg']).set_index('port')
    return res, ex, mk


def fig_sml():
    res, ex, mk = sml_data()
    prem = mk.mean() * 12
    slope, icpt = np.polyfit(res['beta'], res['avg'], 1)
    stat, pv, _, _ = grs_test(ex.values, mk.values)
    small = [c for c in res.index if c.startswith('SMALL') or c.startswith('ME1')]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
    ax = axes[0]
    ax.scatter(res['beta'], res['avg'], s=16, color=MainBlue, label='25 size x B/M portfolios')
    xs = np.linspace(0.8, 1.5, 10)
    ax.plot(xs, prem * xs, color=IDAred, ls='--', label=f'CAPM SML (slope = {prem:.1%})')
    ax.plot(xs, icpt + slope * xs, color=Gray, label=f'Fitted line (slope = {slope:.1%})')
    ax.set_xlabel('CAPM beta')
    ax.set_ylabel('Mean excess return (ann.)')
    ax.set_title('Security market line', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    ax = axes[1]
    col = [Crimson if c in small else MainBlue for c in res.index]
    ax.scatter(res['beta'], res['alpha'], s=16, c=col)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('CAPM beta')
    ax.set_ylabel('CAPM alpha (ann.)')
    ax.set_title(f'Alphas: GRS = {stat:.2f}, p < 0.001', fontsize=9, loc='left')
    ax.scatter([], [], s=16, color=Crimson, label='Smallest-size quintile')
    ax.scatter([], [], s=16, color=MainBlue, label='Other portfolios')
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    plt.tight_layout()
    save_fig('ch3_sml')
    return dict(start=str(ex.index[0].date()), end=str(ex.index[-1].date()), T=len(ex), prem=prem,
                slope=slope, icpt=icpt, beta_min=res['beta'].min(), beta_max=res['beta'].max(),
                avg_min=res['avg'].min(), avg_max=res['avg'].max(), grs=stat, grs_p=pv,
                n_sig=int((res['t_alpha'].abs() > 1.96).sum()),
                alpha_smallvalue=res.loc['SMALL HiBM', 'alpha'], alpha_smallgrowth=res.loc['SMALL LoBM', 'alpha'])


# =============================================================================
# FIG 3: Beta rulant (fereastra de un an) pentru patru sectoare
# =============================================================================
def fig_rolling_beta(window=252):
    S = ['XLK.US', 'XLU.US', 'XLF.US', 'XLE.US']
    r = log_returns(prices(S + ['SPY.US']))
    m = r['SPY.US']
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    out = {}
    for s, c in zip(S, [MainBlue, Forest, IDAred, Amber]):
        b = r[s].rolling(window).cov(m) / m.rolling(window).var()
        ax.plot(b.index, b.values, color=c, lw=0.8, label=f'{s[:-3]} ({SECTOR_NAMES[s[:-3]]})')
        out[s[:-3]] = dict(min=float(b.min()), max=float(b.max()), last=float(b.dropna().iloc[-1]))
    ax.axhline(1, color=Gray, lw=0.6, ls=':')
    ax.set_ylabel('252-day rolling beta vs SPY')
    ax.set_title('Betas are not constant: rolling one-year betas of sector ETFs', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.13)
    plt.tight_layout()
    save_fig('ch3_rolling_beta')
    return out


# =============================================================================
# FIG 4: Revenirea beta spre 1 (Blume) si ajustarea Vasicek
# =============================================================================
def beta_split():
    S = [s + '.US' for s in SECTORS]
    ex, F = monthly_excess(S + ['SPY.US'])
    halves = [ex.loc[:'2012-12-31'], ex.loc['2013-01-01':]]
    b = []
    for h in halves:
        b.append(pd.Series({s[:-3]: ols_hac(h[s].values, h['SPY.US'].values)[0][1] for s in S}))
    se1 = pd.Series({s[:-3]: ols_hac(halves[0][s].values, halves[0]['SPY.US'].values)[1][1] for s in S})
    return b[0], b[1], se1, halves


def fig_beta_shrink():
    b1, b2, se1, halves = beta_split()
    slope, icpt = np.polyfit(b1, b2, 1)
    # Vasicek: media si dispersia cross-sectionala a beta ca informatie a priori
    prior_m, prior_v = b1.mean(), b1.var(ddof=1)
    w = prior_v / (prior_v + se1 ** 2)
    b_vas = w * b1 + (1 - w) * prior_m
    b_blume = 0.67 * b1 + 0.33
    err = lambda x: float(np.sqrt(((x - b2) ** 2).mean()))
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.scatter(b1, b2, s=20, color=MainBlue, zorder=3, label='Sector ETFs')
    for s in b1.index:
        ax.annotate(s, (b1[s], b2[s]), xytext=(3, 2), textcoords='offset points', fontsize=6.5, color='black')
    xs = np.linspace(0.4, 1.6, 10)
    ax.plot(xs, xs, color=Gray, ls=':', label='No change (45 degree)')
    ax.plot(xs, icpt + slope * xs, color=IDAred, label=f'Fitted: b2 = {icpt:.2f} + {slope:.2f} b1')
    ax.set_xlabel('Beta, Jan 1999 - Dec 2012')
    ax.set_ylabel('Beta, Jan 2013 - Jul 2026')
    ax.set_title('Betas regress towards 1 (Blume, 1971)', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    plt.tight_layout()
    save_fig('ch3_beta_shrink')
    return dict(slope=slope, icpt=icpt, rmse_raw=err(b1), rmse_blume=err(b_blume), rmse_vasicek=err(b_vas),
                prior_mean=prior_m, betas1=b1.round(3).to_dict(), betas2=b2.round(3).to_dict(),
                vasicek=b_vas.round(3).to_dict())


# =============================================================================
# FIG 5: Randamentul cumulat al factorilor Fama-French si momentum
# =============================================================================
def fig_factor_cum():
    F = factors('M')
    cols = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    out = {}
    for c, col in zip(cols, [MainBlue, Amber, IDAred, Forest, Purple, Orange]):
        wealth = (1 + F[c]).cumprod()
        ax.plot(wealth.index, wealth.values, color=col, lw=0.9, label=c)
        out[c] = float(wealth.iloc[-1])
    ax.set_yscale('log')
    ax.set_ylabel('Growth of 1 USD (log scale)')
    ax.set_title(f'Long-short factor returns, {F.index[0]:%b %Y} - {F.index[-1]:%b %Y} (Kenneth French data)',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=6, y=-0.13)
    plt.tight_layout()
    save_fig('ch3_factor_cum')
    return out


# =============================================================================
# FIG 6: Statistici t ale primelor factoriale, inainte si dupa 2000
# =============================================================================
def factor_tstats(split='1999-12-31'):
    F = factors('M')
    cols = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    rows = []
    for c in cols:
        for lab, x in [('1963-1999', F[c].loc[:split]), ('2000-2026', F[c].loc[split:].iloc[1:])]:
            b, se, t, _, _ = ols_hac(x.values, np.zeros((len(x), 0)))
            rows.append((c, lab, x.mean() * 12, t[0]))
    return pd.DataFrame(rows, columns=['factor', 'period', 'mean', 't'])


def fig_factor_tstats():
    d = factor_tstats()
    cols = d['factor'].unique()
    x = np.arange(len(cols))
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    for k, (lab, c) in enumerate([('1963-1999', MainBlue), ('2000-2026', Amber)]):
        v = d[d['period'] == lab].set_index('factor').loc[cols, 't']
        ax.bar(x + (k - 0.5) * 0.36, v.values, 0.36, color=c, label=lab)
    ax.axhline(1.96, color=Gray, ls='--', lw=0.8, label='t = 1.96 (5%, single test)')
    ax.axhline(3.0, color=IDAred, ls='--', lw=0.8, label='t = 3.0 (Harvey, Liu & Zhu hurdle)')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(x, cols)
    ax.set_ylabel('t-statistic of the mean (Newey-West)')
    ax.set_title('Factor premia before and after 2000', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.15)
    plt.tight_layout()
    save_fig('ch3_factor_tstats')
    return d


# =============================================================================
# FIG 7: Gradina zoologica a factorilor: descoperiri false sub ipoteza nula
# =============================================================================
def fig_false_discoveries(M=300, T=600, reps=2000):
    rng = np.random.default_rng(SEED)
    # M factori fara prima (media 0), fiecare testat pe T luni
    t = rng.standard_normal((reps, M))                 # statistica t ~ N(0,1) sub H0, teste independente
    n196 = (np.abs(t) > 1.96).sum(1)
    n3 = (np.abs(t) > 3.0).sum(1)
    tmax = np.abs(t).max(1)
    bonf = stats.norm.ppf(1 - 0.05 / (2 * M))
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9))
    axes[0].hist(n196, bins=np.arange(n196.min(), n196.max() + 2) - 0.5, color=MainBlue, alpha=0.8)
    axes[0].set_xlabel('Number of |t| > 1.96 among 300 useless factors')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title(f'Mean: {n196.mean():.1f} false discoveries', fontsize=9, loc='left')
    axes[1].hist(tmax, bins=40, color=Amber, alpha=0.85)
    axes[1].axvline(bonf, color=IDAred, ls='--', lw=0.9, label=f'Bonferroni threshold {bonf:.2f}')
    axes[1].axvline(3.0, color=Gray, ls=':', lw=0.9, label='t = 3.0')
    axes[1].set_xlabel('Largest |t| among 300 useless factors')
    axes[1].set_title('The best "factor" always looks strong', fontsize=9, loc='left')
    legend_outside_bottom(axes[1], ncol=1, y=-0.25)
    plt.tight_layout()
    save_fig('ch3_false_discoveries')
    return dict(M=M, mean_n196=float(n196.mean()), mean_n3=float(n3.mean()), median_tmax=float(np.median(tmax)),
                bonf=float(bonf), p_any3=float((n3 > 0).mean()))


# =============================================================================
# FIG 8-9: PCA pe randamentele sectoarelor (11 ETF-uri, din iunie 2018)
# =============================================================================
def pca_sectors():
    S = [s + '.US' for s in SECTORS_ALL]
    r = log_returns(prices(S + ['SPY.US']))
    X = r[S]
    Z = (X - X.mean()) / X.std()
    C = np.corrcoef(Z.values.T)
    vals, vecs = np.linalg.eigh(C)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    for k in range(vecs.shape[1]):                      # semn: incarcare medie pozitiva
        if vecs[:, k].sum() < 0:
            vecs[:, k] *= -1
    pcs = Z.values @ vecs
    corr_pc1_spy = np.corrcoef(pcs[:, 0], r['SPY.US'].values)[0, 1]
    return vals, vecs, r, corr_pc1_spy


def fig_pca():
    vals, vecs, r, c1 = pca_sectors()
    share = vals / vals.sum()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={'width_ratios': [1, 1.3]})
    k = np.arange(1, len(vals) + 1)
    axes[0].bar(k, share, color=MainBlue, alpha=0.85, label='Share of variance')
    axes[0].plot(k, np.cumsum(share), color=IDAred, marker='o', ms=3, label='Cumulative')
    axes[0].set_xlabel('Principal component')
    axes[0].set_ylabel('Share of total variance')
    axes[0].set_xticks(k)
    axes[0].set_title('Scree plot', fontsize=9, loc='left')
    legend_outside_bottom(axes[0], ncol=2, y=-0.22)
    x = np.arange(len(SECTORS_ALL))
    for j, c in enumerate([MainBlue, IDAred, Forest]):
        axes[1].bar(x + (j - 1) * 0.27, vecs[:, j], 0.27, color=c, label=f'PC{j + 1}')
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_xticks(x, SECTORS_ALL, rotation=45, fontsize=7)
    axes[1].set_ylabel('Loading (eigenvector)')
    axes[1].set_title('Loadings of the first three components', fontsize=9, loc='left')
    legend_outside_bottom(axes[1], ncol=3, y=-0.3)
    plt.tight_layout()
    save_fig('ch3_pca')
    return dict(start=str(r.index[0].date()), end=str(r.index[-1].date()), T=len(r),
                share=[float(s) for s in share[:5]], cum3=float(share[:3].sum()), corr_pc1_spy=float(c1),
                load_pc2=dict(zip(SECTORS_ALL, np.round(vecs[:, 1], 3))),
                load_pc1=dict(zip(SECTORS_ALL, np.round(vecs[:, 0], 3))))


# =============================================================================
# FIG 10: ETF-uri factoriale, cresterea a 1 USD
# =============================================================================
def fig_factor_etfs():
    E = [e + '.US' for e in FACTOR_ETFS] + ['SPY.US']
    p = prices(E)
    wealth = p / p.iloc[0]
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    names = {'MTUM': 'Momentum', 'VLUE': 'Value', 'QUAL': 'Quality', 'USMV': 'Min. volatility',
             'IWM': 'Small caps', 'IWD': 'Large value', 'IWF': 'Large growth', 'SPY': 'S&P 500'}
    out = {}
    for e, c in zip(E, PALETTE):
        k = e[:-3]
        ax.plot(wealth.index, wealth[e].values, color=c if k != 'SPY' else 'black', lw=0.8 if k != 'SPY' else 1.2,
                label=f'{k} ({names[k]})')
        yrs = (p.index[-1] - p.index[0]).days / 365.25
        out[k] = float(wealth[e].iloc[-1] ** (1 / yrs) - 1)
    ax.set_ylabel('Growth of 1 USD (total return)')
    ax.set_title(f'Factor ETFs vs the S&P 500, {p.index[0]:%b %Y} - {p.index[-1]:%b %Y}', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.13)
    plt.tight_layout()
    save_fig('ch3_factor_etfs')
    return dict(start=str(p.index[0].date()), cagr=out)


# =============================================================================
# FIG 11: Alfa si expuneri FF5 + momentum ale ETF-urilor factoriale
# =============================================================================
def etf_regressions():
    E = [e + '.US' for e in FACTOR_ETFS]
    rows, span = [], []
    for e in E:
        y, F = daily_excess_one(e)
        X = F[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']].values
        b, se, t, _, r2 = ols_hac(y.values, X, lags=10)
        rows.append([e[:-3], b[0] * 252, se[0] * 252, t[0], r2, len(y)] + list(b[1:]))
        span.append((y.index[0], y.index[-1]))
    cols = ['etf', 'alpha', 'se_alpha', 't_alpha', 'r2', 'n', 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    return pd.DataFrame(rows, columns=cols).set_index('etf'), span


def fig_etf_alphas():
    res, span = etf_regressions()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={'width_ratios': [1, 1.6]})
    y = np.arange(len(res))
    axes[0].errorbar(res['alpha'], y, xerr=1.96 * res['se_alpha'], fmt='o', color=MainBlue, capsize=2, lw=0.8)
    axes[0].axvline(0, color=Gray, lw=0.6)
    axes[0].set_yticks(y, res.index)
    axes[0].set_xlabel('Annualised alpha, 95% CI')
    axes[0].set_title('FF5 + momentum alpha', fontsize=9, loc='left')
    L = res[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']]
    im = axes[1].imshow(L.values, cmap='RdBu_r', vmin=-1.2, vmax=1.2, aspect='auto')
    axes[1].set_xticks(range(L.shape[1]), L.columns, fontsize=7)
    axes[1].set_yticks(y, res.index)
    for i in range(L.shape[0]):
        for j in range(L.shape[1]):
            axes[1].text(j, i, f'{L.values[i, j]:.2f}', ha='center', va='center', fontsize=6.5,
                         color='white' if abs(L.values[i, j]) > 0.6 else 'black')
    axes[1].set_title('Factor loadings', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch3_etf_alphas')
    return dict(start=str(min(a for a, b in span).date()), end=str(max(b for a, b in span).date()),
                n_min=int(res['n'].min()), n_max=int(res['n'].max()),
                table=res.round(3).reset_index().to_dict(orient='records'))


# =============================================================================
# FIG 12: Beta CAPM ale actiunilor BVB fata de indicele BET
# =============================================================================
def bvb_betas(start='2015-01-01'):
    rows = []
    for s in BVB:
        p = prices([s + '.RO', 'BET']).loc[start:]
        r = log_returns(p)
        # erori de date (evenimente de capital neajustate): |r| > 50% intr-o zi se elimina
        bad = (r.abs() > MAX_ABS_RET).any(axis=1)
        r = r[~bad]
        b, se, t, e, r2 = ols_hac(r[s + '.RO'].values, r['BET'].values)
        rows.append((s, b[1], se[1], r2, len(r), str(r.index[0].date()), int(bad.sum())))
    res = pd.DataFrame(rows, columns=['stock', 'beta', 'se', 'r2', 'n', 'from', 'n_removed']).set_index('stock')
    prior_m, prior_v = res['beta'].mean(), res['beta'].var(ddof=1)
    w = prior_v / (prior_v + res['se'] ** 2)
    res['vasicek'] = w * res['beta'] + (1 - w) * prior_m
    return res.sort_values('beta')


def fig_bvb_betas():
    res = bvb_betas()
    y = np.arange(len(res))
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.errorbar(res['beta'], y, xerr=1.96 * res['se'], fmt='o', color=MainBlue, capsize=2, lw=0.8,
                label='OLS beta, 95% CI (Newey-West)')
    ax.plot(res['vasicek'], y, 'D', ms=4, color=IDAred, label='Vasicek-adjusted beta')
    ax.axvline(1, color=Gray, ls=':', lw=0.7)
    ax.set_yticks(y, [f'{s} ({BVB_NAMES[s]})' for s in res.index], fontsize=7)
    ax.set_xlabel('Beta vs BET (daily log returns)')
    ax.set_title('CAPM betas of BVB blue chips, 2015-2026 (or since listing)', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    plt.tight_layout()
    save_fig('ch3_bvb_betas')
    return res.round(3).reset_index().to_dict(orient='records')


# =============================================================================
# FIG 13: Fama-MacBeth pe 25 de portofolii: CAPM vs FF3 vs FF5
# =============================================================================
def fama_macbeth(ex, F, fac, nw_lags=6):
    """Prima etapa: beta pe toata perioada; a doua: regresii transversale lunare."""
    X = F[fac].values
    B = np.linalg.lstsq(np.column_stack([np.ones(len(X)), X]), ex.values, rcond=None)[0][1:].T   # N x K
    lam = []
    for t in range(len(ex)):
        Z = np.column_stack([np.ones(B.shape[0]), B])
        lam.append(np.linalg.lstsq(Z, ex.values[t], rcond=None)[0])
    lam = np.array(lam)                                   # T x (1+K)
    mean = lam.mean(0)
    se_fm = lam.std(0, ddof=1) / np.sqrt(len(lam))
    se_nw = np.array([ols_hac(lam[:, j], np.zeros((len(lam), 0)), lags=nw_lags)[1][0] for j in range(lam.shape[1])])
    # corectia Shanken (1992): (1 + lambda' Sigma_f^-1 lambda) pentru termenii de prima
    Sf = np.atleast_2d(np.cov(X.T))
    c = 1 + mean[1:] @ np.linalg.solve(Sf, mean[1:])
    se_sh = se_fm.copy()
    se_sh[1:] = np.sqrt(se_fm[1:] ** 2 * c + np.diag(Sf) / len(lam))
    return pd.DataFrame({'lambda': mean * 12, 'se_fm': se_fm * 12, 'se_nw': se_nw * 12, 'se_shanken': se_sh * 12,
                         'factor_mean': np.r_[np.nan, X.mean(0) * 12]}, index=['const'] + fac)


def fig_fama_macbeth():
    res, ex, mk = sml_data()
    F = factors('M').loc[ex.index]
    models = {'CAPM': ['Mkt-RF'], 'FF3': ['Mkt-RF', 'SMB', 'HML'], 'FF5': ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']}
    out = {k: fama_macbeth(ex, F, v) for k, v in models.items()}
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    labels, x0 = [], 0
    for k, c in zip(models, [MainBlue, Amber, Forest]):
        d = out[k]
        xs = np.arange(len(d)) + x0
        ax.errorbar(xs, d['lambda'], yerr=1.96 * d['se_shanken'], fmt='o', color=c, capsize=2, lw=0.8, label=k)
        ax.plot(xs[1:], d['factor_mean'].iloc[1:], 'x', color=Purple, ms=5)
        labels += [f'{k}: {n}' for n in d.index]
        x0 += len(d) + 1
    ax.plot([], [], 'x', color=Purple, label='Time-series mean of the factor')
    ax.axhline(0, color=Gray, lw=0.5)
    ticks = []
    x0 = 0
    for k in models:
        ticks += list(np.arange(len(out[k])) + x0)
        x0 += len(out[k]) + 1
    ax.set_xticks(ticks, [l.split(': ')[1] for l in labels], rotation=45, fontsize=7)
    ax.set_ylabel('Premium (ann.), 95% CI (Shanken)')
    ax.set_title('Fama-MacBeth risk premia on 25 size x B/M portfolios, 1963-2026', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.3)
    plt.tight_layout()
    save_fig('ch3_fama_macbeth')
    return {k: v.round(4).reset_index().to_dict(orient='records') for k, v in out.items()}


# =============================================================================
# MAIN
# =============================================================================
def to_py(o):
    if isinstance(o, dict):
        return {str(k): to_py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, pd.DataFrame):
        return to_py(o.to_dict(orient='records'))
    return o


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    print('Chapter 3 charts')
    R = {}
    R['frontier'] = fig_frontier()
    R['sml'] = fig_sml()
    R['rolling_beta'] = fig_rolling_beta()
    R['beta_shrink'] = fig_beta_shrink()
    R['factor_cum'] = fig_factor_cum()
    R['factor_tstats'] = fig_factor_tstats()
    R['false_disc'] = fig_false_discoveries()
    R['pca'] = fig_pca()
    R['factor_etfs'] = fig_factor_etfs()
    R['etf_alphas'] = fig_etf_alphas()
    R['bvb_betas'] = fig_bvb_betas()
    R['fama_macbeth'] = fig_fama_macbeth()
    with open(os.path.join(HERE, 'ch3_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print(json.dumps(to_py(R), indent=1, default=str)[:20000])

"""
Generator pentru toate graficele din Capitolul 2: Eficienta pietei, de la EMH la piete adaptive
=============================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date zilnice de piata (data/market): 13 indici bursieri (2000-2026), Bitcoin (2014-2026),
Ethereum (2016-2026); EUR/RON: cursul oficial de referinta BNR (iulie 2005-2026).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import MARKETS, LABELS, GROUPS, load_close, log_returns, complete_months   # noqa: E402
from eff_tests import (variance_ratio, chow_denning, runs_test, robust_ljung_box, rs_hurst,  # noqa: E402
                       lo_modified_rs, dfa_hurst, rolling_stat)

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

# Chart colours
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
GROUP_COL = {'Developed': MainBlue, 'Emerging/frontier': IDAred, 'Crypto': Amber, 'FX': Forest}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
TABLE_DIR = HERE
SEED = 42


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


# =============================================================================
# DATE
# =============================================================================
rets = {k: log_returns(k) for k in MARKETS}
ORDER = list(MARKETS)


# =============================================================================
# TABEL: testele de eficienta slaba pentru toate pietele
# =============================================================================
def efficiency_table():
    rows = []
    for k in ORDER:
        r = rets[k]
        e = r - r.mean()
        tau1 = (e.values[1:] ** 2 * e.values[:-1] ** 2).sum() / (e ** 2).sum() ** 2
        v2, v5, v10, v20 = (variance_ratio(r, q) for q in (2, 5, 10, 20))
        cd = chow_denning(r)
        rt = runs_test(r)
        lb = robust_ljung_box(r, 10)
        h, h_al, _ = rs_hurst(r)
        V, qv = lo_modified_rs(r)
        hd, _ = dfa_hurst(r)
        rows.append(dict(market=LABELS[k], group=GROUPS[k], start=r.index[0].date(), end=r.index[-1].date(),
                         N=len(r), rho1=r.autocorr(1), rho1_se_iid=1 / np.sqrt(len(r)), rho1_se_rob=np.sqrt(tau1),
                         VR2=v2[0], z2=v2[1], zstar2=v2[2], VR5=v5[0], z5=v5[1], zstar5=v5[2],
                         VR10=v10[0], zstar10=v10[2], VR20=v20[0], zstar20=v20[2],
                         CD=cd[0], CD_p=cd[1], runs_z=rt[2], runs_p=rt[3],
                         Q10=lb[0], Q10_p=lb[1], Q10rob=lb[2], Q10rob_p=lb[3],
                         H_rs=h, H_anis_lloyd=h_al, LoV=V, LoV_q=qv, H_dfa=hd))
    t = pd.DataFrame(rows, index=ORDER)
    t.to_csv(os.path.join(TABLE_DIR, 'ch2_efficiency_table.csv'), float_format='%.6g')
    return t


# =============================================================================
# FIG 1: Care serie este reala? (Roberts, 1959)
# =============================================================================
def fig_random_walk_game(seed=7):
    """S&P 500 2010-2026 among three random walks with the same drift and volatility."""
    p = load_close('sp500', start='2010-01-01')
    r = np.log(p).diff().dropna()
    rng = np.random.default_rng(seed)
    real_pos = rng.integers(0, 4)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 3.8), sharex=True)
    for i, ax in enumerate(axes.flat):
        if i == real_pos:
            path = np.log(p.values / p.values[0])
        else:
            sim = rng.normal(r.mean(), r.std(), len(r))
            path = np.concatenate([[0], np.cumsum(sim)])
        ax.plot(np.arange(len(path)), np.exp(path), color=MainBlue, lw=0.7)
        ax.set_title(f'Series {"ABCD"[i]}', fontsize=9, loc='left')
        ax.set_xticks([])
        ax.set_ylabel('Growth of 1', fontsize=8)
    fig.suptitle('One of these is the S&P 500 (2010-2026); three are simulated random walks with the same drift and volatility',
                 fontsize=8.5, x=0.02, ha='left')
    plt.tight_layout()
    save_fig('ch2_random_walk_game')
    pd.Series({'real_series': 'ABCD'[real_pos]}).to_csv(os.path.join(TABLE_DIR, 'ch2_random_walk_game_answer.csv'))
    return 'ABCD'[real_pos]


# =============================================================================
# FIG 2: Autocorelatia de ordinul 1, cu benzi i.i.d. si robuste
# =============================================================================
def _two_columns(n, figsize=(7.4, 3.6)):
    """Two panels side by side for a long list of markets (rows 0..h-1 left, h..n-1 right), shared x axis, so
    that the market names stay legible on a slide."""
    fig, axes = plt.subplots(1, 2, figsize=figsize, sharex=True)
    h = (n + 1) // 2
    return fig, axes, [range(0, h), range(h, n)], h


def fig_acf_markets(t):
    t = t.sort_values('rho1')
    fig, axes, parts, h = _two_columns(len(t))
    for ax, idx in zip(axes, parts):
        for j, i in enumerate(idx):
            row = t.iloc[i]
            c = GROUP_COL[row['group']]
            ax.errorbar(row['rho1'], j, xerr=1.96 * row['rho1_se_rob'], fmt='o', ms=4, color=c, capsize=2, lw=0.9)
            ax.plot([row['rho1'] - 1.96 * row['rho1_se_iid'], row['rho1'] + 1.96 * row['rho1_se_iid']], [j + 0.25] * 2,
                    color=Gray, lw=0.8)
        ax.axvline(0, color=Gray, lw=0.6)
        ax.set_yticks(range(len(idx)), [t['market'].iloc[i] for i in idx], fontsize=7.5)
        ax.set_ylim(-0.6, h - 0.4)
        ax.set_xlabel(r'Lag-1 autocorrelation $\hat\rho_1$')
    handles = [plt.Line2D([], [], color=c, marker='o', ls='', label=g) for g, c in GROUP_COL.items()]
    handles += [plt.Line2D([], [], color=Gray, lw=0.8, label=r'i.i.d. 95% band $\pm 1.96/\sqrt{T}$'),
                plt.Line2D([], [], color='k', lw=0.9, label='Robust 95% interval (bars)')]
    axes[0].set_title('Lag-1 autocorrelation of daily log returns across markets (full samples)', fontsize=9, loc='left')
    plt.tight_layout()
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    save_fig('ch2_acf_markets')


# =============================================================================
# FIG 3: Profilul VR(q) cu banda robusta
# =============================================================================
def vr_profile(r, qmax=60):
    out = []
    x = np.asarray(r, dtype=float)
    T = len(x)
    e = x - x.mean()
    den = (e ** 2).sum() ** 2
    deltas = np.array([T * (e[j:] ** 2 * e[:-j] ** 2).sum() / den for j in range(1, qmax)])
    for q in range(2, qmax + 1):
        vr = variance_ratio(r, q)[0]
        j = np.arange(1, q)
        theta = np.sum((2 * (q - j) / q) ** 2 * deltas[:q - 1])
        out.append((q, vr, 1.96 * np.sqrt(theta / T)))
    return pd.DataFrame(out, columns=['q', 'VR', 'band']).set_index('q')


def fig_vr_profile():
    sel = [('sp500', MainBlue), ('bet', IDAred), ('btc', Amber), ('eurron', Forest)]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.2), sharex=True)
    res = {}
    for ax, (k, c) in zip(axes.flat, sel):
        vp = vr_profile(rets[k])
        res[k] = vp
        ax.fill_between(vp.index, 1 - vp['band'], 1 + vp['band'], color=LightGray, alpha=0.8, lw=0,
                        label='Robust 95% band under a random walk')
        ax.plot(vp.index, vp['VR'], color=c, lw=1.1, label='VR(q)')
        ax.axhline(1, color=Gray, lw=0.6)
        ax.set_title(LABELS[k], fontsize=8.5, loc='left', color=c)
    for ax in axes[1]:
        ax.set_xlabel('Horizon q (days)')
    for ax in axes[:, 0]:
        ax.set_ylabel('Variance ratio')
    h, l = axes[0, 0].get_legend_handles_labels()
    axes[1, 0].legend(h, l, loc='upper center', bbox_to_anchor=(1.05, -0.3), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch2_vr_profile')
    return {k: v.loc[[2, 5, 10, 20, 60]] for k, v in res.items()}


# =============================================================================
# FIG 4: z*(5) pe piete
# =============================================================================
def fig_vr_markets(t):
    t = t.sort_values('zstar5')
    fig, axes, parts, h = _two_columns(len(t))
    for ax, idx in zip(axes, parts):
        tt = t.iloc[list(idx)]
        ax.barh(np.arange(len(tt)), tt['zstar5'], color=[GROUP_COL[g] for g in tt['group']], alpha=0.85)
        for x in (-1.96, 1.96):
            ax.axvline(x, color=Gray, ls='--', lw=0.8)
        ax.axvline(0, color=Gray, lw=0.5)
        ax.set_yticks(np.arange(len(tt)), tt['market'], fontsize=7.5)
        ax.set_ylim(-0.6, h - 0.4)
        ax.set_xlabel(r'Robust statistic $z^*(5)$')
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.85, label=g) for g, c in GROUP_COL.items()]
    handles.append(plt.Line2D([], [], color=Gray, ls='--', label=r'$\pm 1.96$ (5% two-sided)'))
    axes[0].set_title('Variance ratio at 5 days (Lo-MacKinlay, heteroskedasticity-robust): who rejects the random walk?',
                      fontsize=9, loc='left')
    plt.tight_layout()
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=5, frameon=False)
    save_fig('ch2_vr_markets')


# =============================================================================
# FIG 5: Analiza R/S (Hurst)
# =============================================================================
def fig_hurst_rs():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), sharey=True)
    out = {}
    for ax, (k, c) in zip(axes, [('sp500', MainBlue), ('bet', IDAred)]):
        h, h_al, d = rs_hurst(rets[k])
        out[k] = (h, h_al)
        ax.loglog(d['n'], d['rs'], 'o', ms=3.5, color=c, label=f'Observed R/S (slope H = {h:.2f})')
        ax.loglog(d['n'], d['expected_rs'], '-', color=Gray, lw=1, label='Expected R/S under i.i.d. (Anis-Lloyd)')
        ax.loglog(d['n'], d['rs'].iloc[0] * (d['n'] / d['n'].iloc[0]) ** 0.5, ':', color=Gray, lw=0.8,
                  label='Slope 0.5')
        ax.set_xlabel('Window length n (days)')
        ax.set_title(f'{LABELS[k]}: corrected H = {h_al:.2f}', fontsize=8.5, loc='left', color=c)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False, fontsize=7)
    axes[0].set_ylabel('Mean rescaled range R/S')
    plt.tight_layout()
    save_fig('ch2_hurst_rs')
    return out


# =============================================================================
# FIG 6: Exponentul DFA pe piete, cu banda de amestecare (ipoteza i.i.d.)
# =============================================================================
def shuffle_band(r, func, n_sim=200, seed=SEED):
    """95% band from permutations: destroys ALL dependence (including volatility clustering)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(r, dtype=float)
    sims = [func(rng.permutation(x)) for _ in range(n_sim)]
    return np.percentile(sims, [2.5, 97.5])


def wild_band(r, func, n_sim=199, seed=SEED):
    """95% wild-bootstrap band: Rademacher signs on the demeaned returns.
    Keeps the volatility path |e_t| (allowed under RW3), destroys the autocorrelation of returns."""
    rng = np.random.default_rng(seed)
    e = np.asarray(r, dtype=float)
    e = e - e.mean()
    sims = [func(e * rng.choice([-1.0, 1.0], len(e))) for _ in range(n_sim)]
    return np.percentile(sims, [2.5, 97.5])


def fig_hurst_markets(t):
    dfa = lambda x: dfa_hurst(x)[0]
    shuf = {k: shuffle_band(rets[k], dfa, n_sim=100) for k in ORDER}
    band = {k: wild_band(rets[k], dfa, n_sim=199) for k in ORDER}
    t = t.assign(band_lo=[band[k][0] for k in t.index], band_hi=[band[k][1] for k in t.index],
                 shuf_lo=[shuf[k][0] for k in t.index], shuf_hi=[shuf[k][1] for k in t.index]).sort_values('H_dfa')
    fig, axes, parts, h = _two_columns(len(t))
    for ax, idx in zip(axes, parts):
        tt = t.iloc[list(idx)]
        y = np.arange(len(tt))
        ax.hlines(y, tt['band_lo'], tt['band_hi'], color=LightGray, lw=6)
        ax.scatter(tt['H_dfa'], y, color=[GROUP_COL[g] for g in tt['group']], zorder=3, s=22)
        ax.axvline(0.5, color=Gray, ls='--', lw=0.8)
        ax.set_yticks(y, tt['market'], fontsize=7.5)
        ax.set_ylim(-0.6, h - 0.4)
        ax.set_xlabel(r'DFA exponent $\alpha_{DFA}$ (0.5 = no long memory)')
    handles = [plt.Line2D([], [], color=c, marker='o', ls='', label=g) for g, c in GROUP_COL.items()]
    handles.append(plt.Line2D([], [], color=LightGray, lw=6, label='Wild-bootstrap 95% band (RW3 null)'))
    axes[0].set_title('Long memory in returns? Detrended fluctuation analysis of daily log returns', fontsize=9, loc='left')
    plt.tight_layout()
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    save_fig('ch2_hurst_markets')
    return t[['H_dfa', 'band_lo', 'band_hi', 'shuf_lo', 'shuf_hi']]


# =============================================================================
# FIG 7-8: Eficienta variabila in timp (AMH): VR si DFA pe ferestre mobile
# =============================================================================
WINDOW, STEP = 500, 21
ROLL = [('sp500', MainBlue), ('bet', IDAred), ('btc', Amber)]


def fig_rolling_vr():
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    out = {}
    for k, c in ROLL:
        z = rolling_stat(rets[k], lambda x: variance_ratio(x, 5)[2], WINDOW, STEP)
        out[k] = z
        ax.plot(z.index, z.values, color=c, lw=0.9, label=LABELS[k])
    for x in (-1.96, 1.96):
        ax.axhline(x, color=Gray, ls='--', lw=0.8)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel(r'Rolling $z^*(5)$')
    ax.set_title(f'Time-varying efficiency: variance-ratio statistic on rolling {WINDOW}-day windows',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    plt.tight_layout()
    save_fig('ch2_rolling_vr')
    share = {k: float((z.abs() > 1.96).mean()) for k, z in out.items()}
    pd.DataFrame(out).to_csv(os.path.join(TABLE_DIR, 'ch2_rolling_vr.csv'))
    return share


def fig_rolling_hurst(n_sim=199):
    """Rolling DFA; wild-bootstrap null band computed separately for EACH window
    (keeps the window's volatility, allowed under RW3). For comparison: the i.i.d. Student-t4 band."""
    rng = np.random.default_rng(SEED)
    null = [dfa_hurst(rng.standard_t(4, WINDOW))[0] for _ in range(300)]
    lo_t, hi_t = np.percentile(null, [2.5, 97.5])
    dfa = lambda x: dfa_hurst(x)[0]
    fig, axes = plt.subplots(3, 1, figsize=(8.6, 4.2), sharex=True)
    out, share, share_t = {}, {}, {}
    for ax, (k, c) in zip(axes, ROLL):
        x = rets[k].values
        rows = []
        for end in range(WINDOW, len(x) + 1, STEP):
            w = x[end - WINDOW:end]
            lo, hi = wild_band(w, dfa, n_sim, SEED + end)
            rows.append((rets[k].index[end - 1], dfa(w), lo, hi))
        d = pd.DataFrame(rows, columns=['date', 'dfa', 'lo', 'hi']).set_index('date')
        out[k] = d
        share[k] = float(((d['dfa'] < d['lo']) | (d['dfa'] > d['hi'])).mean())
        share_t[k] = float(((d['dfa'] < lo_t) | (d['dfa'] > hi_t)).mean())
        ax.fill_between(d.index, d['lo'], d['hi'], color=LightGray, alpha=0.8, lw=0)
        ax.plot(d.index, d['dfa'], color=c, lw=0.9)
        ax.axhline(0.5, color=Gray, ls='--', lw=0.7)
        ax.set_ylabel(LABELS[k].split(' (')[0], fontsize=8)
    axes[0].set_title(f'Time-varying memory: DFA exponent on rolling {WINDOW}-day windows', fontsize=9, loc='left')
    handles = [plt.Line2D([], [], color=c, lw=1.2, label=LABELS[k]) for k, c in ROLL]
    handles.append(plt.Line2D([], [], color=LightGray, lw=6, label='Wild-bootstrap 95% band (per window)'))
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False)
    plt.tight_layout()
    save_fig('ch2_rolling_hurst')
    pd.concat(out, axis=1).to_csv(os.path.join(TABLE_DIR, 'ch2_rolling_hurst.csv'))
    band_mean = {k: [float(d['lo'].mean()), float(d['hi'].mean())] for k, d in out.items()}
    return (lo_t, hi_t), share, share_t, band_mean


# =============================================================================
# FIG 9: Eficienta cripto pe ani (Urquhart, 2016)
# =============================================================================
def crypto_yearly():
    rows = []
    for k, start in [('btc', '2011-01-01'), ('eth', '2016-01-01')]:
        r = log_returns(k, start=start)
        for y, ry in r.groupby(r.index.year):
            if len(ry) < 200:
                continue
            e = ry - ry.mean()
            tau1 = (e.values[1:] ** 2 * e.values[:-1] ** 2).sum() / (e ** 2).sum() ** 2
            vr, _, zs = variance_ratio(ry, 5)
            rows.append(dict(asset=LABELS[k], year=y, n=len(ry), rho1=ry.autocorr(1), rho1_se=np.sqrt(tau1),
                             VR5=vr, zstar5=zs))
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(TABLE_DIR, 'ch2_crypto_yearly.csv'), index=False, float_format='%.6g')
    return d


def fig_crypto_yearly():
    d = crypto_yearly()
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    for (a, c, off) in [('Bitcoin', Amber, -0.15), ('Ethereum', Purple, 0.15)]:
        s = d[d['asset'] == a]
        ax.errorbar(s['year'] + off, s['rho1'], yerr=1.96 * s['rho1_se'], fmt='o', ms=4, color=c, capsize=2,
                    lw=0.9, label=f'{a}: lag-1 autocorrelation, robust 95% interval')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Calendar year')
    ax.set_ylabel(r'$\hat\rho_1$ of daily log returns')
    ax.set_title('Crypto efficiency year by year: early Bitcoin (2011-2013) versus later years', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch2_crypto_yearly')
    return d


# =============================================================================
# FIG 10: Efecte de calendar cu erori HAC
# =============================================================================
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']


def dow_regression(r):
    """Daily return on weekday dummies (no constant), Newey-West errors."""
    r = complete_months(r)
    X = pd.get_dummies(r.index.dayofweek).astype(float)
    X.columns = DAYS
    X.index = r.index
    res = sm.OLS(r * 1e4, X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    # Wald test of equal means, with the same HAC errors
    R = np.zeros((4, 5))
    for i in range(4):
        R[i, 0], R[i, i + 1] = 1, -1
    w = res.wald_test(R, scalar=True)
    return res, float(w.pvalue)


def january_regression(r):
    m = np.exp(complete_months(r).groupby(pd.Grouper(freq='ME')).sum()) - 1
    X = sm.add_constant(pd.Series((m.index.month == 1).astype(float), index=m.index, name='January'))
    res = sm.OLS(m * 100, X).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    return res


def turn_of_month(r):
    """Dummy for the last trading day of the month and the first three days of the next month (Ariel, 1987)."""
    d = pd.DataFrame({'r': complete_months(r) * 1e4})
    ym = d.index.to_period('M')
    rank = d.groupby(ym).cumcount()
    rank_end = d.groupby(ym).cumcount(ascending=False)
    d['tom'] = ((rank < 3) | (rank_end == 0)).astype(float)
    res = sm.OLS(d['r'], sm.add_constant(d['tom'])).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    return res


def calendar_table():
    rows = []
    for k in ['sp500', 'bet', 'stoxx', 'wig20', 'bux']:
        r = rets[k]
        res, p_eq = dow_regression(r)
        jan = january_regression(r)
        tom = turn_of_month(r)
        rows.append(dict(market=LABELS[k], **{f'{d}_bp': res.params[d] for d in DAYS},
                         **{f'{d}_t': res.tvalues[d] for d in DAYS}, dow_equal_p=p_eq,
                         jan_extra_pct=jan.params['January'], jan_t=jan.tvalues['January'],
                         tom_extra_bp=tom.params['tom'], tom_t=tom.tvalues['tom'], tom_p=tom.pvalues['tom']))
    t = pd.DataFrame(rows).set_index('market')
    t.to_csv(os.path.join(TABLE_DIR, 'ch2_calendar_table.csv'), float_format='%.6g')
    return t


def fig_calendar():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    out = {}
    for ax, (k, c) in zip(axes, [('sp500', MainBlue), ('bet', IDAred)]):
        res, p_eq = dow_regression(rets[k])
        ci = res.conf_int()
        out[k] = p_eq
        ax.bar(DAYS, res.params.values, color=c, alpha=0.85)
        ax.errorbar(DAYS, res.params.values, yerr=[res.params - ci[0], ci[1] - res.params], fmt='none',
                    ecolor='k', capsize=3, lw=0.8)
        ax.axhline(0, color=Gray, lw=0.6)
        ax.set_title(f'{LABELS[k]}: equal-means p = {p_eq:.2f}', fontsize=8.5, loc='left', color=c)
    axes[0].set_ylabel('Mean daily log return (bp)\nwith HAC 95% interval')
    plt.tight_layout()
    save_fig('ch2_calendar')
    return out


# =============================================================================
# FIG 11: Testarea multipla -- anomalii false pe date reale
# =============================================================================
def fig_multiple_testing(n_rules=2000, seed=SEED):
    """Random calendar rules on the S&P 500: each picks 20% of the days at random as 'good days'."""
    rng = np.random.default_rng(seed)
    r = rets['sp500'] * 1e4
    x = r.values
    ts = []
    for _ in range(n_rules):
        mask = rng.random(len(x)) < 0.2
        d = x[mask].mean() - x[~mask].mean()
        se = np.sqrt(x[mask].var(ddof=1) / mask.sum() + x[~mask].var(ddof=1) / (~mask).sum())
        ts.append(d / se)
    ts = np.array(ts)
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.hist(ts, bins=60, color=MainBlue, alpha=0.8, density=True, label=f'{n_rules} random "anomalies" on the S&P 500')
    xx = np.linspace(-4.5, 4.5, 300)
    ax.plot(xx, np.exp(-xx ** 2 / 2) / np.sqrt(2 * np.pi), color=Gray, lw=1, label='Standard Normal distribution')
    for v, lab, c in [(1.96, r'$|t| > 1.96$', IDAred), (3.0, r'$|t| > 3.0$ (Harvey-Liu-Zhu)', Forest)]:
        ax.axvline(v, color=c, ls='--', lw=0.9, label=lab)
        ax.axvline(-v, color=c, ls='--', lw=0.9)
    ax.set_xlabel('t-statistic of "good days minus other days"')
    ax.set_title(f'Pure chance: {np.mean(np.abs(ts) > 1.96):.1%} of meaningless rules are "significant" at 5%',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    plt.tight_layout()
    save_fig('ch2_multiple_testing')
    return dict(share_196=float(np.mean(np.abs(ts) > 1.96)), share_3=float(np.mean(np.abs(ts) > 3.0)),
                max_abs_t=float(np.abs(ts).max()), n=n_rules)


# =============================================================================
# FIG 12: Momentum pe serii de timp (Moskowitz, Ooi & Pedersen, 2012) la nivel de indice
# =============================================================================
def tsmom_table():
    rows = []
    for k in [m for m in ORDER if m != 'eurron']:
        p = complete_months(load_close(k))
        pm = p.resample('ME').last()
        m = np.log(pm).diff().dropna()                          # monthly log returns: for the signal only
        R = pm.pct_change().dropna()                            # simple returns: the position's payoff
        sig = np.sign(m.rolling(12).sum().shift(1))            # sign of the past 12-month return
        s = (sig * R).dropna()                                  # long +1 / short -1, before funding and costs
        res = sm.OLS(s * 100, np.ones(len(s))).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
        bh = R.loc[s.index]
        rows.append(dict(market=LABELS[k], group=GROUPS[k], months=len(s),
                         tsmom_mean_pct=res.params.iloc[0], t_hac=res.tvalues.iloc[0],
                         sharpe_tsmom=np.sqrt(12) * s.mean() / s.std(), sharpe_bh=np.sqrt(12) * bh.mean() / bh.std(),
                         rho1_monthly=m.autocorr(1)))
    t = pd.DataFrame(rows, index=[m for m in ORDER if m != 'eurron'])
    t.to_csv(os.path.join(TABLE_DIR, 'ch2_tsmom_table.csv'), float_format='%.6g')
    return t


def fig_tsmom():
    t = tsmom_table().sort_values('t_hac')
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.barh(np.arange(len(t)), t['t_hac'], color=[GROUP_COL[g] for g in t['group']], alpha=0.85)
    for x in (-1.96, 1.96):
        ax.axvline(x, color=Gray, ls='--', lw=0.8)
    ax.axvline(0, color=Gray, lw=0.5)
    ax.set_yticks(np.arange(len(t)), t['market'], fontsize=7.5)
    ax.set_xlabel('HAC t-statistic of the mean monthly time-series momentum return')
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COL[g], alpha=0.85, label=g)
               for g in ['Developed', 'Emerging/frontier', 'Crypto']]
    handles.append(plt.Line2D([], [], color=Gray, ls='--', label=r'$\pm 1.96$'))
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
    ax.set_title('Index-level time-series momentum: long if the past 12 months were positive, else short',
                 fontsize=8.5, loc='left')
    plt.tight_layout()
    save_fig('ch2_tsmom')
    return t


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    import json
    pd.set_option('display.width', 250)
    print('Chapter 2 charts')
    N = {}
    t = efficiency_table()
    print(t.round(3).T)
    N['rw_game_real'] = fig_random_walk_game()
    fig_acf_markets(t)
    vp = fig_vr_profile()
    N['vr_profile'] = {k: {int(q): [float(v.loc[q, 'VR']), float(v.loc[q, 'band'])] for q in v.index} for k, v in vp.items()}
    fig_vr_markets(t)
    hr = fig_hurst_rs()
    N['hurst_rs'] = {k: [float(a), float(b)] for k, (a, b) in hr.items()}
    hm = fig_hurst_markets(t)
    hm.to_csv(os.path.join(TABLE_DIR, 'ch2_hurst_bands.csv'), float_format='%.6g')
    N['rolling_vr_share'] = fig_rolling_vr()
    band, share, share_t, band_mean = fig_rolling_hurst()
    N['rolling_dfa_band_t4'] = [float(band[0]), float(band[1])]
    N['rolling_dfa_share'] = share
    N['rolling_dfa_share_t4'] = share_t
    N['rolling_dfa_band_mean'] = band_mean
    fig_crypto_yearly()
    N['calendar_p'] = {k: float(v) for k, v in fig_calendar().items()}
    calendar_table()
    N['multiple_testing'] = fig_multiple_testing()
    fig_tsmom()
    with open(os.path.join(TABLE_DIR, 'ch2_numbers.json'), 'w') as f:
        json.dump(N, f, indent=1, default=str)
    print(json.dumps(N, indent=1, default=str)[:3000])

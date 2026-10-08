"""
Generator pentru toate graficele din Capitolul 6: Volatilitate multivariata si dependenta
=======================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date zilnice de piata (data/market): SPY, TLT, S&P 500, Euro Stoxx 50, BET, Bitcoin si sase banci
(JPMorgan, Bank of America, Deutsche Bank, BNP Paribas, Banca Transilvania, BRD).
Analizele comune: join pe preturi in zilele comune, apoi randamente.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import (LABELS, SHORT, BANKS, COVOL_ETFS, joint_returns, weekly_returns, joint_prices,  # noqa: E402
                      load_price)
from dep_tools import (ewma_cov, ewma_corr, rolling_corr, fisher_ci, garch_all, dcc_fit, fr_adjust,  # noqa: E402
                       fr_inflation, crisis_table, exceedance_corr, FAMILIES, FAM_LABEL, pseudo_obs,
                       kendall_tau, spearman_rho, theta_from_tau, tail_dep, simulate, fit_copula, gof_test,
                       empirical_tail_dep)

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

# Colours
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
FAM_COL = {'gaussian': MainBlue, 't': IDAred, 'clayton': Forest, 'gumbel': Amber, 'frank': Purple}

SIDE = (5.6, 3.5)   # size of the charts placed next to text
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


def shade_crises(ax, alpha=0.5):
    for a, b in (('2008-09-15', '2009-03-31'), ('2020-02-20', '2020-04-30'), ('2022-01-03', '2022-10-31')):
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=BandBlue, alpha=alpha, lw=0)


# =============================================================================
# 1. Why correlation matters: diversification of a 60/40 portfolio
# =============================================================================
def fig_diversification():
    R = joint_returns(['spy', 'tlt'])
    s1, s2 = R.std() * np.sqrt(252)
    w = 0.6
    rho = np.linspace(-1, 1, 201)
    vol = np.sqrt(w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * rho * s1 * s2)
    r_pre = R.loc[:'2021-12-31'].corr().iloc[0, 1]
    r_post = R.loc['2022-01-01':].corr().iloc[0, 1]
    v = lambda r: np.sqrt(w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * r * s1 * s2)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.plot(rho, 100 * vol, color=MainBlue, lw=1.6, label='60/40 SPY-TLT portfolio volatility')
    ax.axhline(100 * (w * s1 + (1 - w) * s2), color=Gray, ls='--', lw=0.9, label='No diversification (rho = 1)')
    ax.scatter([r_pre], [100 * v(r_pre)], color=Forest, zorder=5, s=36, label=f'2002-2021 correlation ({r_pre:.2f})')
    ax.scatter([r_post], [100 * v(r_post)], color=IDAred, zorder=5, s=36, label=f'2022-2026 correlation ({r_post:.2f})')
    ax.set_xlabel('Correlation between SPY and TLT daily returns')
    ax.set_ylabel('Annualised volatility (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    save_fig('ch6_diversification')
    NUM.update(div_s_spy=s1, div_s_tlt=s2, div_rho_pre=r_pre, div_rho_post=r_post, div_vol_pre=v(r_pre),
               div_vol_post=v(r_post), div_vol_undiv=w * s1 + (1 - w) * s2, div_vol_zero=v(0.0),
               div_start=str(R.index[0].date()), div_n=len(R))


# =============================================================================
# 2. SPY-TLT correlation on a one-year rolling window
# =============================================================================
def fig_spy_tlt_rolling():
    R = joint_returns(['spy', 'tlt'])
    rc = rolling_corr(R, 252).dropna()
    lo, hi = fisher_ci(rc, 252)
    fig, ax = plt.subplots(figsize=SIDE)
    shade_crises(ax)
    ax.fill_between(rc.index, lo, hi, color=MainBlue, alpha=0.15, lw=0, label='95% Fisher interval (i.i.d.)')
    ax.plot(rc.index, rc, color=MainBlue, label='252-day rolling correlation')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Correlation SPY-TLT')
    ax.plot([], [], color=LightGray, alpha=0.5, lw=6, label='2008-09, 2020 and 2022 stress windows')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch6_spy_tlt_rolling')
    NUM.update(roll_min=rc.min(), roll_min_date=str(rc.idxmin().date()), roll_max=rc.max(),
               roll_max_date=str(rc.idxmax().date()), roll_last=rc.iloc[-1], roll_last_date=str(rc.index[-1].date()),
               roll_share_pos_pre=(rc.loc[:'2021-12-31'] > 0).mean(), roll_share_pos_post=(rc.loc['2022-01-01':] > 0).mean(),
               roll_2022=rc.loc['2022-12-30':'2022-12-31'].iloc[-1] if len(rc.loc['2022-12-30':'2022-12-31']) else rc.loc[:'2022-12-31'].iloc[-1])


# =============================================================================
# 3. EWMA vs rolling window; a numerical EWMA update
# =============================================================================
def fig_ewma_rolling():
    R = joint_returns(['spy', 'tlt'])
    X = 100 * R
    e94 = ewma_corr(X, 0.94)
    e97 = ewma_corr(X, 0.97)
    r60 = rolling_corr(X, 60)
    r250 = rolling_corr(X, 250)
    sl = slice('2019-01-01', None)
    fig, ax = plt.subplots(figsize=SIDE)
    ax.plot(e94.loc[sl].index, e94.loc[sl], color=IDAred, lw=0.9, label='EWMA, lambda = 0.94')
    ax.plot(e97.loc[sl].index, e97.loc[sl], color=Amber, lw=1.0, label='EWMA, lambda = 0.97')
    ax.plot(r60.loc[sl].index, r60.loc[sl], color=Forest, lw=0.8, ls='--', label='60-day rolling')
    ax.plot(r250.loc[sl].index, r250.loc[sl], color=MainBlue, lw=1.5, label='250-day rolling')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Correlation SPY-TLT')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch6_ewma_rolling')
    # step-by-step example: the last day of the sample
    S = ewma_cov(X.values, 0.94)
    t = len(X) - 1
    r = X.values[t - 1]
    NUM.update(ew_date_prev=str(X.index[t - 1].date()), ew_date=str(X.index[t].date()),
               ew_s11_prev=S[t - 1, 0, 0], ew_s22_prev=S[t - 1, 1, 1], ew_s12_prev=S[t - 1, 0, 1],
               ew_r1=r[0], ew_r2=r[1], ew_s11=S[t, 0, 0], ew_s22=S[t, 1, 1], ew_s12=S[t, 0, 1],
               ew_rho_prev=S[t - 1, 0, 1] / np.sqrt(S[t - 1, 0, 0] * S[t - 1, 1, 1]),
               ew_rho=S[t, 0, 1] / np.sqrt(S[t, 0, 0] * S[t, 1, 1]),
               ew_sd94=e94.loc[sl].diff().std(), ew_sd97=e97.loc[sl].diff().std(), ew_sd250=r250.loc[sl].diff().std(),
               ew_halflife94=np.log(0.5) / np.log(0.94), ew_halflife97=np.log(0.5) / np.log(0.97))


# =============================================================================
# 4. Asynchronous trading: daily, 2-day and weekly correlations
# =============================================================================
def async_table():
    names = ['spy', 'stoxx', 'bet']
    P = joint_prices(names, start='2000-01-01')
    lp = np.log(P)
    d1 = lp.diff().dropna()
    d2 = (lp - lp.shift(2)).dropna().iloc[::2]                 # non-overlapping 2-day returns
    wk = np.log(P.resample('W-FRI').last()).diff().dropna()
    rows = []
    for a, b in (('spy', 'stoxx'), ('spy', 'bet'), ('stoxx', 'bet')):
        for lab, D in (('daily', d1), ('2-day', d2), ('weekly', wk)):
            r = D[a].corr(D[b])
            lo, hi = fisher_ci(r, len(D))
            rows.append(dict(pair=f'{SHORT[a]} / {SHORT[b]}', freq=lab, rho=r, lo=lo, hi=hi, n=len(D)))
        lead = d1[a].shift(1).corr(d1[b])                         # a yesterday -> b today
        rows.append(dict(pair=f'{SHORT[a]} / {SHORT[b]}', freq='lead', rho=lead, lo=np.nan, hi=np.nan, n=len(d1)))
    return pd.DataFrame(rows)


def fig_async():
    t = async_table()
    t.to_csv(os.path.join(TABLE_DIR, 'ch6_async_table.csv'), index=False, float_format='%.6g')
    pairs = t['pair'].unique()
    fig, ax = plt.subplots(figsize=SIDE)
    cols = {'daily': Forest, '2-day': Amber, 'weekly': MainBlue}
    for k, f in enumerate(['daily', '2-day', 'weekly']):
        s = t[t['freq'] == f].set_index('pair').loc[pairs]
        x = np.arange(len(pairs)) + (k - 1) * 0.26
        ax.bar(x, s['rho'], width=0.24, color=cols[f], label=f'{f} returns')
        ax.errorbar(x, s['rho'], yerr=[s['rho'] - s['lo'], s['hi'] - s['rho']], fmt='none', ecolor='black', lw=0.7, capsize=2)
    ax.set_xticks(np.arange(len(pairs)))
    ax.set_xticklabels(pairs)
    ax.set_ylabel('Correlation')
    legend_outside_bottom(ax, ncol=3, y=-0.1)
    save_fig('ch6_async')
    g = lambda p, f: float(t[(t.pair == p) & (t.freq == f)]['rho'].iloc[0])
    NUM.update(as_ss_d=g('SPY / Euro Stoxx 50', 'daily'), as_ss_2=g('SPY / Euro Stoxx 50', '2-day'),
               as_ss_w=g('SPY / Euro Stoxx 50', 'weekly'), as_ss_lead=g('SPY / Euro Stoxx 50', 'lead'),
               as_sb_d=g('SPY / BET', 'daily'), as_sb_w=g('SPY / BET', 'weekly'), as_sb_lead=g('SPY / BET', 'lead'),
               as_eb_d=g('Euro Stoxx 50 / BET', 'daily'), as_eb_w=g('Euro Stoxx 50 / BET', 'weekly'),
               as_n_d=int(t[t.freq == 'daily']['n'].iloc[0]), as_n_w=int(t[t.freq == 'weekly']['n'].iloc[0]))
    return t


# =============================================================================
# 5-7. DCC: SPY-TLT, the minimum-variance portfolio, Bitcoin-SPY
# =============================================================================
def dcc_pair(names, start=None):
    R = joint_returns(names, start=start)
    P, V, Z, ll1 = garch_all(R)
    d = dcc_fit(Z)
    rc = pd.Series(d['R'][:, 0, 1], index=Z.index)
    return R, P, V, Z, d, rc, ll1


def fig_dcc_spy_tlt():
    R, P, V, Z, d, rc, ll1 = dcc_pair(['spy', 'tlt'])
    roll = rolling_corr(R, 252)
    fig, ax = plt.subplots(figsize=SIDE)
    shade_crises(ax)
    ax.plot(rc.index, rc, color=IDAred, lw=0.7, label='DCC(1,1) conditional correlation')
    ax.plot(roll.index, roll, color=MainBlue, lw=1.5, label='252-day rolling correlation')
    ax.axhline(d['Qbar'][0, 1], color=Gray, ls='--', lw=0.9, label='DCC target $\\bar Q_{12}$ (sample correlation of standardised residuals)')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Correlation SPY-TLT')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch6_dcc_spy_tlt')
    lr = 2 * (d['loglik'] - d['ccc_loglik'])
    NUM.update(dcc_a=d['a'], dcc_b=d['b'], dcc_se_a=d['se_a'], dcc_se_b=d['se_b'], dcc_ab=d['a'] + d['b'],
               dcc_hl=np.log(0.5) / np.log(d['a'] + d['b']), dcc_qbar=d['Qbar'][0, 1], dcc_ll=d['loglik'],
               dcc_ll_ccc=d['ccc_loglik'], dcc_lr=lr, dcc_min=rc.min(), dcc_min_date=str(rc.idxmin().date()),
               dcc_max=rc.max(), dcc_max_date=str(rc.idxmax().date()), dcc_last=rc.iloc[-1], dcc_n=len(Z),
               dcc_start=str(Z.index[0].date()), dcc_end=str(Z.index[-1].date()),
               g_spy_omega=P.loc['omega', 'spy'], g_spy_alpha=P.loc['alpha[1]', 'spy'], g_spy_beta=P.loc['beta[1]', 'spy'],
               g_tlt_omega=P.loc['omega', 'tlt'], g_tlt_alpha=P.loc['alpha[1]', 'tlt'], g_tlt_beta=P.loc['beta[1]', 'tlt'],
               dcc_mean_2008=rc.loc['2008-09-15':'2008-12-31'].mean(), dcc_mean_2022=rc.loc['2022'].mean(),
               dcc_mean_2012=rc.loc['2012'].mean())
    return R, V, rc


def fig_dcc_minvar(R, V, rc):
    """SPY weight in the SPY-TLT minimum-variance portfolio: DCC vs constant correlation."""
    s1, s2 = V['spy'], V['tlt']
    c = rc * s1 * s2
    w_dcc = ((s2 ** 2 - c) / (s1 ** 2 + s2 ** 2 - 2 * c)).clip(0, 1)
    rho0 = R.corr().iloc[0, 1]
    c0 = rho0 * s1 * s2
    w_ccc = ((s2 ** 2 - c0) / (s1 ** 2 + s2 ** 2 - 2 * c0)).clip(0, 1)
    # simple asset returns (R holds log returns): the portfolio return is sum_i w_i (e^{r_i} - 1)
    X = 100 * np.expm1(R.loc[w_dcc.index])
    # the filters (GARCH volatilities, R_t) use only information up to day t-1, but the GARCH, DCC and
    # constant-correlation parameters are estimated on the full sample: an IN-sample illustration, not an out-of-sample evaluation
    p_dcc = w_dcc * X['spy'] + (1 - w_dcc) * X['tlt']
    p_ccc = w_ccc * X['spy'] + (1 - w_ccc) * X['tlt']
    p_6040 = 0.6 * X['spy'] + 0.4 * X['tlt']
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(5.6, 3.8), sharex=True, gridspec_kw=dict(height_ratios=[2, 1]))
    ax.plot(w_ccc.index, w_ccc, color=MainBlue, lw=0.6, label='GARCH + constant correlation')
    ax.plot(w_dcc.index, w_dcc, color=IDAred, lw=0.6, label='GARCH + DCC')
    ax.set_ylabel('Weight in SPY')
    ax.set_ylim(0, 1)
    ax2.plot(w_dcc.index, w_dcc - w_ccc, color=Forest, lw=0.6, label='Difference: DCC minus constant correlation')
    ax2.axhline(0, color='black', lw=0.5)
    ax2.set_ylabel('Difference')
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=2, frameon=False)
    save_fig('ch6_dcc_minvar')
    ann = lambda p: p.std() * np.sqrt(252)
    NUM.update(mv_vol_dcc=ann(p_dcc), mv_vol_ccc=ann(p_ccc), mv_vol_6040=ann(p_6040),
               mv_w_mean=w_dcc.mean(), mv_w_2022=w_dcc.loc['2022'].mean(), mv_w_2012=w_dcc.loc['2012'].mean(),
               mv_dmax=(w_dcc - w_ccc).abs().max(), mv_dmax_date=str((w_dcc - w_ccc).abs().idxmax().date()),
               mv_dmean=(w_dcc - w_ccc).abs().mean(), mv_rho0=rho0)


def fig_dcc_btc_spy():
    R, P, V, Z, d, rc, ll1 = dcc_pair(['btc', 'spy'])
    roll = rolling_corr(R, 252)
    fig, ax = plt.subplots(figsize=SIDE)
    ax.plot(rc.index, rc, color=Amber, lw=0.8, label='DCC(1,1) conditional correlation')
    ax.plot(roll.index, roll, color=MainBlue, lw=1.5, label='252-day rolling correlation')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Correlation Bitcoin-SPY')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch6_dcc_btc_spy')
    yr = rc.groupby(rc.index.year).mean()
    NUM.update(btc_a=d['a'], btc_b=d['b'], btc_se_a=d['se_a'], btc_se_b=d['se_b'], btc_ab=d['a'] + d['b'],
               btc_lr=2 * (d['loglik'] - d['ccc_loglik']), btc_n=len(Z), btc_start=str(Z.index[0].date()),
               btc_pre2020=rc.loc[:'2019-12-31'].mean(), btc_post2020=rc.loc['2020-01-01':].mean(),
               btc_2022=yr.loc[2022], btc_max=rc.max(), btc_max_date=str(rc.idxmax().date()),
               btc_last=rc.iloc[-1], btc_uncond=R.corr().iloc[0, 1])


# =============================================================================
# 8-9. Crises: Forbes-Rigobon and the bias of the correlation
# =============================================================================
CALM08, CRISIS08 = ('2007-09-14', '2008-09-12'), ('2008-09-15', '2009-03-31')
CALM20, CRISIS20 = ('2019-02-19', '2020-02-19'), ('2020-02-20', '2020-04-30')


def two_day_returns(names, start='2006-01-01', end='2021-12-31'):
    """2-day returns (moving sum, as in Forbes-Rigobon): log p_t - log p_{t-2}, from common prices."""
    lp = np.log(joint_prices(names, start=start, end=end))
    return (lp - lp.shift(2)).dropna()


def fig_forbes_rigobon():
    r2 = two_day_returns(['sp500', 'stoxx', 'bet'])
    t = crisis_table(r2, 'sp500', ['stoxx', 'bet'], CALM08, CRISIS08)
    t.to_csv(os.path.join(TABLE_DIR, 'ch6_forbes_rigobon_2008.csv'), float_format='%.6g')
    fig, ax = plt.subplots(figsize=SIDE)
    x = np.arange(len(t))
    ax.bar(x - 0.26, t['rho_calm'], 0.24, color=Forest, label='Calm year before (Sep 2007 - Sep 2008)')
    ax.bar(x, t['rho_crisis'], 0.24, color=IDAred, label='Crisis (15 Sep 2008 - 31 Mar 2009), raw')
    ax.bar(x + 0.26, t['rho_adj'], 0.24, color=MainBlue, label='Crisis, Forbes-Rigobon adjusted')
    ax.set_xticks(x)
    ax.set_xticklabels([f'S&P 500 / {SHORT[k]}' for k in t.index])
    ax.set_ylabel('Correlation of 2-day returns')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_forbes_rigobon')
    for k in t.index:
        for c in ('rho_calm', 'rho_crisis', 'rho_adj', 'z_raw', 'p_raw', 'z_adj', 'p_adj'):
            NUM[f'fr_{k}_{c}'] = t.loc[k, c]
    NUM.update(fr_delta=t['delta'].iloc[0], fr_n_calm=int(t['n_calm'].iloc[0]), fr_n_crisis=int(t['n_crisis'].iloc[0]),
               fr_vr=1 + t['delta'].iloc[0])
    return t


def fig_fr_bias():
    delta = np.linspace(0, 10, 201)
    fig, ax = plt.subplots(figsize=SIDE)
    for rho, c in ((0.2, Forest), (0.4, MainBlue), (0.6, IDAred)):
        ax.plot(delta, fr_inflation(rho, delta), color=c, lw=1.5, label=f'true correlation {rho}')
        ax.axhline(rho, color=c, lw=0.6, ls=':')
    ax.axvline(NUM['fr_delta'], color=Gray, ls='--', lw=0.9, label=f'S&P 500 in 2008: delta = {NUM["fr_delta"]:.1f}')
    ax.set_xlabel('delta = Var(crisis) / Var(calm) - 1 for the source market')
    ax.set_ylabel('Measured crisis correlation')
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch6_fr_bias')
    NUM.update(frb_04=fr_inflation(0.4, NUM['fr_delta']), frb_02=fr_inflation(0.2, NUM['fr_delta']))


def fig_exceedance():
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    x, y = W['sp500'].values, W['stoxx'].values
    qs = np.array([0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50])
    e = exceedance_corr(x, y, qs)
    rho = np.corrcoef(x, y)[0, 1]
    rng = np.random.default_rng(SEED)
    Zs = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], 2_000_000)
    en = exceedance_corr(Zs[:, 0], Zs[:, 1], qs)
    fig, ax = plt.subplots(figsize=SIDE)
    xl = np.concatenate([qs, 1 - qs[::-1]])
    ax.plot(qs, e['rho_low'], 'o-', color=IDAred, label='Data: both below quantile q (joint losses)')
    ax.plot(1 - qs, e['rho_high'], 's-', color=Forest, label='Data: both above quantile 1-q (joint gains)')
    ax.plot(qs, en['rho_low'], color=MainBlue, ls='--', lw=1.6, label='Bivariate Normal distribution with the same correlation')
    ax.plot(1 - qs, en['rho_high'], color=MainBlue, ls='--', lw=1.6)
    ax.set_xticks(xl)
    ax.set_xticklabels([f'{v:.2f}' for v in xl], fontsize=7)
    ax.set_xlabel('Threshold quantile')
    ax.set_ylabel('Exceedance correlation')
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch6_exceedance')
    e.to_csv(os.path.join(TABLE_DIR, 'ch6_exceedance.csv'), float_format='%.6g')
    NUM.update(ex_rho=rho, ex_n=len(W), ex_low10=e.loc[0.10, 'rho_low'], ex_high10=e.loc[0.10, 'rho_high'],
               ex_nlow10=int(e.loc[0.10, 'n_low']), ex_nhigh10=int(e.loc[0.10, 'n_high']),
               ex_norm10=en.loc[0.10, 'rho_low'], ex_low20=e.loc[0.20, 'rho_low'], ex_high20=e.loc[0.20, 'rho_high'],
               ex_norm20=en.loc[0.20, 'rho_low'])


# =============================================================================
# 10-14. Copulas: pseudo-observations, families, estimation, goodness of fit, tail dependence (JPM-BAC)
# =============================================================================
def bank_copula_data():
    R = joint_returns(['jpm', 'bac'])
    P, V, Z, ll = garch_all(R)
    U = pseudo_obs(Z.values)
    return R, Z, U


def fig_pseudo_obs(Z, U):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))
    axes[0].scatter(Z['jpm'], Z['bac'], s=2, color=MainBlue, alpha=0.35, label='GARCH standardised residuals')
    axes[0].set_xlabel('JPM')
    axes[0].set_ylabel('BAC')
    axes[1].scatter(U[:, 0], U[:, 1], s=2, color=IDAred, alpha=0.35, label='Pseudo-observations (ranks / (n+1))')
    axes[1].set_xlabel('JPM (uniform scale)')
    axes[1].set_ylabel('BAC (uniform scale)')
    h = [axes[0].collections[0], axes[1].collections[0]]
    fig.legend(h, [x.get_label() for x in h], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False,
               markerscale=4)
    plt.tight_layout()
    save_fig('ch6_pseudo_obs')


def fig_copula_zoo(tau=0.5, n=1500):
    rng = np.random.default_rng(SEED)
    fig, axes = plt.subplots(1, 5, figsize=(7.6, 1.9), sharex=True, sharey=True)
    for ax, fam in zip(axes, FAMILIES):
        th = theta_from_tau(fam, tau)
        par = [th, 4.0] if fam == 't' else [th]
        X = simulate(fam, par, n, rng)
        Zs = stats.norm.ppf(X)
        ax.scatter(Zs[:, 0], Zs[:, 1], s=1.2, color=FAM_COL[fam], alpha=0.5)
        lab = f'{FAM_LABEL[fam]}\n' + (f'rho = {th:.2f}, nu = 4' if fam == 't' else (f'rho = {th:.2f}' if fam == 'gaussian' else f'theta = {th:.2f}'))
        ax.set_title(lab, fontsize=8)
        ax.set_xlim(-3.8, 3.8)
        ax.set_ylim(-3.8, 3.8)
        ax.set_xticks([-3, 0, 3])
        ax.set_yticks([-3, 0, 3])
    fig.text(0.5, -0.06, "All with Kendall's tau = 0.5, shown on Normal-score margins", ha='center', fontsize=8)
    save_fig('ch6_copula_zoo')
    for fam in FAMILIES:
        th = theta_from_tau(fam, tau)
        NUM[f'zoo_{fam}'] = th
        lam = tail_dep(fam, [th, 4.0] if fam == 't' else [th])
        NUM[f'zoo_{fam}_lamL'], NUM[f'zoo_{fam}_lamU'] = lam


def copula_table(U, B=200, B_t=100):
    u, v = U[:, 0], U[:, 1]
    rows = []
    for fam in FAMILIES:
        f = fit_copula(fam, u, v)
        g = gof_test(fam, u, v, B=B_t if fam == 't' else B, seed=SEED, fit=f)
        rows.append(dict(family=fam, par1=f['par'][0], par2=f['par'][1] if fam == 't' else np.nan, loglik=f['loglik'],
                         aic=f['aic'], bic=f['bic'], tau_model=f['tau_model'], lamL=f['lamL'], lamU=f['lamU'],
                         gof_stat=g['stat'], gof_p=g['p'], gof_B=g['B']))
    return pd.DataFrame(rows).set_index('family')


def fig_copula_fit(U):
    t = copula_table(U)
    t.to_csv(os.path.join(TABLE_DIR, 'ch6_copula_jpm_bac.csv'), float_format='%.6g')
    fig, ax = plt.subplots(figsize=SIDE)
    d = t['aic'] - t['aic'].min()
    ax.bar(np.arange(5), d, color=[FAM_COL[f] for f in t.index])
    for i, (fam, val) in enumerate(d.items()):
        ax.text(i, val + d.max() * 0.02, f'p = {t.loc[fam, "gof_p"]:.3f}', ha='center', fontsize=7)
    ax.set_xticks(np.arange(5))
    ax.set_xticklabels([FAM_LABEL[f] for f in t.index])
    ax.set_ylabel('AIC minus best AIC')
    ax.plot([], [], ' ', label='Numbers above bars: goodness-of-fit p-value\n(Rosenblatt Cramer-von Mises, parametric bootstrap)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=1, frameon=False, handlelength=0)
    save_fig('ch6_copula_fit')
    u, v = U[:, 0], U[:, 1]
    NUM.update(cop_n=len(U), cop_tau=kendall_tau(u, v), cop_rhoS=spearman_rho(u, v))
    for fam in t.index:
        for c in ('par1', 'par2', 'loglik', 'aic', 'lamL', 'lamU', 'gof_stat', 'gof_p', 'tau_model'):
            NUM[f'cop_{fam}_{c}'] = t.loc[fam, c]
        NUM[f'cop_{fam}_daic'] = d[fam]
    NUM['cop_best'] = t['aic'].idxmin()
    return t


def fig_tail_dep(U, t):
    u, v = U[:, 0], U[:, 1]
    qs = np.linspace(0.01, 0.20, 20)
    emp = np.array([empirical_tail_dep(u, v, q) for q in qs])
    rng = np.random.default_rng(SEED)
    # reference band: the same estimate on data simulated from the fitted t copula (200 replications)
    par_t = [t.loc['t', 'par1'], t.loc['t', 'par2']]
    sims = []
    for _ in range(200):
        X = pseudo_obs(simulate('t', par_t, len(u), rng))
        sims.append([empirical_tail_dep(X[:, 0], X[:, 1], q)[0] for q in qs])
    sims = np.array(sims)
    fig, ax = plt.subplots(figsize=SIDE)
    ax.fill_between(qs, np.percentile(sims, 5, axis=0), np.percentile(sims, 95, axis=0), color=IDAred, alpha=0.15, lw=0,
                    label='90% band of the estimator under the fitted t copula')
    ax.plot(qs, emp[:, 0], 'o-', ms=3, color=IDAred, label='Empirical lower tail: P(U<=q, V<=q) / q')
    ax.plot(qs, emp[:, 1], 's-', ms=3, color=Forest, label='Empirical upper tail: P(U>1-q, V>1-q) / q')
    ax.axhline(t.loc['t', 'lamL'], color=IDAred, ls='--', lw=0.9, label=f't copula limit: {t.loc["t", "lamL"]:.2f}')
    ax.axhline(t.loc['clayton', 'lamL'], color=Forest, ls=':', lw=0.9, label=f'Clayton lower limit: {t.loc["clayton", "lamL"]:.2f}')
    ax.axhline(t.loc['gumbel', 'lamU'], color=Amber, ls=':', lw=0.9, label=f'Gumbel upper limit: {t.loc["gumbel", "lamU"]:.2f}')
    ax.set_xlabel('q')
    ax.set_ylabel('Tail dependence estimate')
    ax.set_ylim(0, 1)
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch6_tail_dep')
    i5 = np.argmin(np.abs(qs - 0.05))
    NUM.update(td_L05=emp[i5, 0], td_U05=emp[i5, 1], td_L01=emp[0, 0], td_U01=emp[0, 1],
               td_band05_lo=np.percentile(sims[:, i5], 5), td_band05_hi=np.percentile(sims[:, i5], 95))


# =============================================================================
# 15. Market integration: US, euro area, Romania (weekly returns)
# =============================================================================
def fig_integration():
    W = weekly_returns(['sp500', 'stoxx', 'bet'], start='2000-01-01')
    win = 104
    fig, ax = plt.subplots(figsize=SIDE)
    for (a, b), c in ((('sp500', 'stoxx'), MainBlue), (('stoxx', 'bet'), IDAred), (('sp500', 'bet'), Amber)):
        rc = W[a].rolling(win).corr(W[b])
        ax.plot(rc.index, rc, color=c, lw=1.2, label=f'{SHORT[a]} / {SHORT[b]}')
        NUM[f'int_{a}_{b}_pre'] = W.loc['2010-01-01':'2019-12-31', a].corr(W.loc['2010-01-01':'2019-12-31', b])
        NUM[f'int_{a}_{b}_post'] = W.loc['2020-01-01':, a].corr(W.loc['2020-01-01':, b])
        NUM[f'int_{a}_{b}_00s'] = W.loc[:'2009-12-31', a].corr(W.loc[:'2009-12-31', b])
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('104-week rolling correlation')
    legend_outside_bottom(ax, ncol=3, y=-0.1)
    save_fig('ch6_integration')
    NUM.update(int_n=len(W), int_start=str(W.index[0].date()))


# =============================================================================
# 16-18. Banks: correlations, the average correlation over time, the minimum spanning tree
# =============================================================================
def fig_banks():
    W = weekly_returns(BANKS, start='2010-01-01')
    C = W.corr()
    C.to_csv(os.path.join(TABLE_DIR, 'ch6_banks_corr.csv'), float_format='%.6g')
    lab = [SHORT[b] for b in BANKS]
    fig, ax = plt.subplots(figsize=(4.4, 3.6))
    im = ax.imshow(C.values, cmap='Blues', vmin=0, vmax=1)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f'{C.values[i, j]:.2f}', ha='center', va='center', fontsize=7,
                    color='white' if C.values[i, j] > 0.6 else 'black')
    ax.set_xticks(range(6))
    ax.set_xticklabels(lab)
    ax.set_yticks(range(6))
    ax.set_yticklabels(lab)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label('Correlation of weekly returns')
    save_fig('ch6_banks_heatmap')
    # 52-week average correlation: within the same region vs across regions
    region = {'jpm': 'US', 'bac': 'US', 'dbk': 'EA', 'bnp': 'EA', 'tlv': 'RO', 'brd': 'RO'}
    pairs = [(a, b) for i, a in enumerate(BANKS) for b in BANKS[i + 1:]]
    rc = {p: W[p[0]].rolling(52).corr(W[p[1]]) for p in pairs}
    grp = {'Within region (US-US, EA-EA, RO-RO)': [p for p in pairs if region[p[0]] == region[p[1]]],
           'US - euro area': [p for p in pairs if {region[p[0]], region[p[1]]} == {'US', 'EA'}],
           'Romania - US / euro area': [p for p in pairs if 'RO' in (region[p[0]], region[p[1]]) and region[p[0]] != region[p[1]]]}
    fig, ax = plt.subplots(figsize=SIDE)
    for (g, ps), c in zip(grp.items(), (MainBlue, Amber, IDAred)):
        m = pd.concat([rc[p] for p in ps], axis=1).mean(axis=1)
        ax.plot(m.index, m, color=c, lw=1.3, label=g)
        NUM[f'bk_{["within", "useu", "ro"][list(grp).index(g)]}_mean'] = m.mean()
        NUM[f'bk_{["within", "useu", "ro"][list(grp).index(g)]}_2020'] = m.loc['2020-03-01':'2020-06-30'].mean()
        NUM[f'bk_{["within", "useu", "ro"][list(grp).index(g)]}_last'] = m.dropna().iloc[-1]
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Average 52-week correlation')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_banks_avgcorr')
    # minimum spanning tree on the distance d = sqrt(2(1 - rho)) (Mantegna, 1999)
    G = nx.Graph()
    for a, b in pairs:
        G.add_edge(SHORT[a], SHORT[b], weight=np.sqrt(2 * (1 - C.loc[a, b])), rho=C.loc[a, b])
    T = nx.minimum_spanning_tree(G)
    pos = {'JPM': (-1.0, 0.6), 'BAC': (-1.0, -0.6), 'DBK': (0.3, 0.6), 'BNP': (0.3, -0.6), 'TLV': (1.6, 0.6), 'BRD': (1.6, -0.6)}
    colr = {'JPM': MainBlue, 'BAC': MainBlue, 'DBK': Amber, 'BNP': Amber, 'TLV': IDAred, 'BRD': IDAred}
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for a, b, dd in T.edges(data=True):
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=MainBlue, alpha=0.45, lw=1 + 5 * dd['rho'], zorder=1)
        vert = pos[a][0] == pos[b][0]
        ax.text((pos[a][0] + pos[b][0]) / 2 + (0.14 if vert else 0), (pos[a][1] + pos[b][1]) / 2 + (0 if vert else 0.1),
                f'{dd["rho"]:.2f}', ha='center', va='center', fontsize=8)
    for k, (x, y) in pos.items():
        ax.scatter(x, y, s=650, color=colr[k], zorder=2)
        ax.text(x, y, k, color='white', ha='center', va='center', fontsize=8, fontweight='bold', zorder=3)
    for lab_, c in (('US banks', MainBlue), ('Euro-area banks', Amber), ('Romanian banks', IDAred)):
        ax.scatter([], [], s=60, color=c, label=lab_)
    ax.set_xlim(-1.5, 2.1)
    ax.set_ylim(-1.0, 1.0)
    ax.axis('off')
    legend_outside_bottom(ax, ncol=3, y=0.0)
    save_fig('ch6_banks_mst')
    NUM.update(bk_n=len(W), bk_start=str(W.index[0].date()), bk_jpm_bac=C.loc['jpm', 'bac'], bk_dbk_bnp=C.loc['dbk', 'bnp'],
               bk_tlv_brd=C.loc['tlv', 'brd'], bk_bnp_tlv=C.loc['bnp', 'tlv'], bk_jpm_brd=C.loc['jpm', 'brd'],
               bk_mst_edges='; '.join(f'{a}--{b} ({d["rho"]:.2f})' for a, b, d in T.edges(data=True)))
    # the link between regions in the tree
    NUM['bk_bridge'] = [f'{a}--{b}' for a, b, d in T.edges(data=True) if {a, b} & {'TLV', 'BRD'} and not {a, b} <= {'TLV', 'BRD'}]


# =============================================================================
# 7. Case study: asset-class COVOL (Engle and Campos-Martins, 2023, Section 9)
# =============================================================================
# Table 15 of the paper: the 20 largest values of US COVOL x_t, data up to March 2021 (Section 9)
ECM_TABLE15 = [('2001-09-11', 73.16), ('2016-11-09', 43.04), ('2000-01-10', 41.46), ('2020-03-09', 40.47),
               ('2020-11-09', 34.12), ('2014-11-28', 24.92), ('2001-01-02', 24.89), ('2001-09-04', 24.62),
               ('2001-01-03', 24.51), ('2020-11-04', 22.23), ('2001-09-14', 19.61), ('2008-10-13', 19.12),
               ('2008-10-10', 18.42), ('2014-08-08', 17.51), ('2016-06-24', 17.25), ('2003-09-02', 16.21),
               ('2003-01-02', 15.45), ('2008-09-19', 14.56), ('2016-11-10', 14.19), ('2021-01-06', 13.58)]
# Table 8 of the paper: R^2 of the monthly regressions of the ACWI volatility shock (248 months)
ECM_TABLE8_R2 = [('Global COVOL$^2_m$', 0.404), ('Change in global EPU', 0.110), ('Change in GPR', 0.005),
                 ('All three together', 0.406)]
ECM_END = '2021-03-01'


def covol_panel():
    """Unbalanced panel of daily log returns (each ETF on its own calendar, from its first day)
    and the PC1 factor (Section 9): the least-squares score on the first principal component of the
    correlation matrix of the returns, computed each day from the ETFs available."""
    R = pd.concat([np.log(load_price('etf_' + e.lower())).diff().rename(e) for e in COVOL_ETFS], axis=1)
    R = R.loc['2000-01-01':].dropna(how='all')
    Zs = (R - R.mean()) / R.std()
    w_val, w_vec = np.linalg.eigh(Zs.corr().values)
    w = w_vec[:, -1] * np.sign(w_vec[:, -1].sum())
    avail = Zs.notna().values
    f = np.nansum(Zs.values * w, axis=1) / (avail * w ** 2).sum(axis=1)
    return R, pd.Series(f, index=R.index, name='PC1')


def covol_residuals(R, f):
    """AR(1) with the PC1 factor in the mean and GARCH(1,1) for each ETF; AR(1)-GARCH(1,1) for PC1.
    Returns the standardised residuals (unbalanced panel)."""
    E = {}
    for c in R.columns:
        r = 100 * R[c].dropna()
        x = f.reindex(r.index).to_frame()
        res = arch_model(r, x=x, mean='ARX', lags=1, vol='GARCH', p=1, q=1).fit(disp='off')
        E[c] = res.resid / res.conditional_volatility
    res = arch_model(f, mean='AR', lags=1, vol='GARCH', p=1, q=1).fit(disp='off')
    E['PC1'] = res.resid / res.conditional_volatility
    return pd.DataFrame(E).dropna(how='all')


def golden_min(obj, lo, hi, n=80):
    """Vectorised golden-section minimisation: obj(u) returns a vector, one value per element of u."""
    phi = (np.sqrt(5) - 1) / 2
    a, b = np.array(lo, float), np.array(hi, float)
    c, d = b - phi * (b - a), a + phi * (b - a)
    fc, fd = obj(c), obj(d)
    for _ in range(n):
        left = fc < fd
        b = np.where(left, d, b)
        a = np.where(left, a, c)
        c2 = np.where(left, b - phi * (b - a), d)
        d2 = np.where(left, c, a + phi * (b - a))
        fn = obj(np.where(left, c2, d2))
        fc, fd = np.where(left, fn, fd), np.where(left, fc, fn)
        c, d = c2, d2
    return (a + b) / 2


def covol_fit(E, tol=1e-6, maxit=500):
    """COVOL with unequal loadings (paper, Section 5.3): alternating maximisation of
    -1/2 sum [ln g + e^2/g], g = s x + 1 - s, over x_t (cross-sections) and s_i (time series),
    with 0 <= s_i <= 1, s's = 1 and mean x_t = 1 after each step (Remark 2). Starting values: the first
    principal component of the rank-correlation matrix of the squares."""
    Q = E.values ** 2
    M = ~np.isnan(Q)
    Q0 = np.where(M, Q, 0.0)
    C = (E ** 2).rank().corr().values
    val, vec = np.linalg.eigh(C)
    s = np.clip(np.abs(vec[:, -1]), 0, 1)
    s /= np.sqrt(s @ s)

    def x_step(s):
        def obj(lx):
            g = s[None, :] * np.exp(lx)[:, None] + 1 - s[None, :]
            return (M * (np.log(g) + Q0 / g)).sum(axis=1)
        T = len(Q)
        return np.exp(golden_min(obj, np.full(T, np.log(1e-4)), np.full(T, np.log(1e4))))

    def s_step(x):
        def obj(sv):
            g = x[:, None] * sv[None, :] + 1 - sv[None, :]
            return (M * (np.log(g) + Q0 / g)).sum(axis=0)
        N = Q.shape[1]
        return golden_min(obj, np.zeros(N), np.ones(N))

    for it in range(1, maxit + 1):
        x = x_step(s)
        x /= x.mean()
        s_new = np.clip(s_step(x), 0, 1)
        s_new /= np.sqrt(s_new @ s_new)
        done = np.max(np.abs(s_new - s)) < tol
        s = s_new
        if done:
            break
    x = x_step(s)
    x /= x.mean()
    return pd.Series(x, index=E.index, name='x'), pd.Series(s, index=E.columns, name='s'), it


def fig_covol():
    """Replication of US COVOL on the course ETFs: daily x_t 2000-2026 and the 20 days of Table 15."""
    R, f = covol_panel()
    E = covol_residuals(R, f)
    x, s, it = covol_fit(E)
    rbar = 100 * R.reindex(x.index).mean(axis=1)
    top = x.sort_values(ascending=False)
    pre = x.loc[:ECM_END].sort_values(ascending=False)
    post = x.loc[pd.Timestamp(ECM_END) + pd.Timedelta(days=1):].sort_values(ascending=False)
    paper = pd.Series({pd.Timestamp(d): v for d, v in ECM_TABLE15})
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(x.index, x.values, color=MainBlue, lw=0.5, label='Squared asset-class COVOL $\\hat x_t$ (20 US-listed ETFs + PC1)')
    ax.scatter(paper.index, paper.values, marker='D', s=16, facecolors='none', edgecolors=Orange, lw=0.9, zorder=4,
               label='Top 20 in Table 15 of Engle and Campos-Martins (2023)')
    ax.axvline(pd.Timestamp(ECM_END), color=Gray, ls='--', lw=0.8, label='End of the paper sample (1 March 2021)')
    for d, v in top.iloc[:6].items():
        left = d.year == 2020 and d.month == 3              # label on the left, so that it does not cover November 2020
        ax.annotate(f'{d.day} {d:%b %Y}', (d, v), xytext=(-4 if left else 4, 2), textcoords='offset points',
                    fontsize=7, color='black', ha='right' if left else 'left')
    ax.set_ylabel('Squared common volatility $\\hat x_t$')
    ax.set_xlim(pd.Timestamp('1999-10-01'), x.index[-1] + pd.Timedelta(days=90))
    ax.set_ylim(0, 1.08 * max(top.iloc[0], paper.max()))
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_covol_replication')
    common = set(pre.index[:20]) & set(paper.index)
    NUM.update(cv_n=E.shape[1], cv_T=len(x), cv_start=str(x.index[0].date()), cv_end=str(x.index[-1].date()),
               cv_iter=it, cv_common20=len(common),
               cv_common20_list='; '.join(d.strftime('%Y-%m-%d') for d in sorted(common)),
               cv_rank_20161109=int((pre > x.loc['2016-11-09']).sum() + 1),
               cv_rank_20200309=int((pre > x.loc['2020-03-09']).sum() + 1),
               cv_rank_20010917=int((pre > x.loc['2001-09-17']).sum() + 1),
               cv_x_20010917=x.loc['2001-09-17'], cv_x_20161109=x.loc['2016-11-09'], cv_x_20200309=x.loc['2020-03-09'],
               cv_s_max=s.idxmax(), cv_s_min=s.idxmin(), cv_s_pc1=s['PC1'])
    for k in range(6):
        d = top.index[k]
        NUM.update({f'cv_top{k + 1}_date': str(d.date()), f'cv_top{k + 1}_x': top.iloc[k],
                    f'cv_top{k + 1}_r': rbar.loc[d]})
    for k in range(3):
        d = pre.index[k]
        NUM.update({f'cv_pre{k + 1}_date': str(d.date()), f'cv_pre{k + 1}_x': pre.iloc[k]})
    for k in range(3):
        d = post.index[k]
        NUM.update({f'cv_post{k + 1}_date': str(d.date()), f'cv_post{k + 1}_x': post.iloc[k],
                    f'cv_post{k + 1}_r': rbar.loc[d]})
    return x, s, E


def fig_covol_paper():
    """Table 8 of Engle and Campos-Martins (2023): R^2 of the monthly ACWI volatility shock on COVOL^2,
    on the change in the GEPU index (economic policy uncertainty) and on the change in the GPR index (geopolitical risk)."""
    lab = [a for a, _ in ECM_TABLE8_R2][::-1]
    val = [b for _, b in ECM_TABLE8_R2][::-1]
    col = [Purple, Amber, Forest, MainBlue]
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    bars = ax.barh(lab, val, color=col, height=0.6)
    for b_, v in zip(bars, val):
        ax.text(v + 0.006, b_.get_y() + b_.get_height() / 2, f'{v:.3f}', va='center', fontsize=8, color='black')
    ax.set_xlim(0, 0.5)
    ax.set_xlabel('$R^2$: monthly ACWI volatility shock on each regressor (248 months)')
    save_fig('ch6_covol_table8')


# =============================================================================
# Example: the minimum-variance hedge ratio (a BET exposure hedged with the Euro Stoxx 50)
# =============================================================================
def hedge_example():
    W = weekly_returns(['bet', 'stoxx'], start='2020-01-01')
    s_b, s_s = W['bet'].std(), W['stoxx'].std()
    rho = W.corr().iloc[0, 1]
    h = rho * s_b / s_s
    NUM.update(hd_rho=rho, hd_sb=100 * s_b, hd_ss=100 * s_s, hd_h=h, hd_r2=rho ** 2, hd_n=len(W),
               hd_start=str(W.index[0].date()), hd_vol_red=1 - np.sqrt(1 - rho ** 2))


# =============================================================================
# Additional numbers for the interpretations
# =============================================================================
def first_persistent_positive(x, n=20):
    """First day after which the estimate stays positive for n consecutive days."""
    run = (x > 0).astype(int).rolling(n).sum()
    return run[run == n].index[0]


def extra_numbers():
    R = joint_returns(['spy', 'tlt'])
    X = 100 * R
    s = slice('2021-06-01', '2023-06-30')
    NUM.update(sw_e94=str(first_persistent_positive(ewma_corr(X, 0.94).loc[s]).date()),
               sw_r250=str(first_persistent_positive(rolling_corr(X, 250).loc[s]).date()))
    P, V, Z, _ = garch_all(R)
    d = dcc_fit(Z)
    rc = pd.Series(d['R'][:, 0, 1], index=Z.index)
    NUM.update(dcc_above_post=(rc.loc['2022-01-01':] > d['Qbar'][0, 1]).mean(),
               dcc_above_pre=(rc.loc[:'2021-12-31'] > d['Qbar'][0, 1]).mean())
    W = weekly_returns(['stoxx', 'bet'], start='2000-01-01')
    r = W['stoxx'].rolling(104).corr(W['bet']).dropna()
    NUM.update(int_last=r.iloc[-1], int_2021=r.loc[:'2021-12-31'].iloc[-1], int_2019=r.loc[:'2019-12-31'].iloc[-1],
               int_2007=r.loc[:'2007-12-31'].iloc[-1], int_2009=r.loc[:'2009-12-31'].iloc[-1])


def save_numbers(path='ch6_numbers.json'):
    out = {}
    for k, v in NUM.items():
        if isinstance(v, (np.floating, float)):
            out[k] = float(v)
        elif isinstance(v, (np.integer, int)):
            out[k] = int(v)
        else:
            out[k] = v
    with open(os.path.join(TABLE_DIR, path), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f'   saved {path} ({len(out)} numbers)')


if __name__ == '__main__':
    fig_diversification()
    fig_spy_tlt_rolling()
    fig_ewma_rolling()
    fig_async()
    R, V, rc = fig_dcc_spy_tlt()
    fig_dcc_minvar(R, V, rc)
    fig_dcc_btc_spy()
    fig_forbes_rigobon()
    fig_fr_bias()
    fig_exceedance()
    Rb, Zb, Ub = bank_copula_data()
    fig_pseudo_obs(Zb, Ub)
    fig_copula_zoo()
    tb = fig_copula_fit(Ub)
    fig_tail_dep(Ub, tb)
    fig_integration()
    fig_banks()
    fig_covol()
    fig_covol_paper()
    hedge_example()
    extra_numbers()
    save_numbers()

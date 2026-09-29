"""
Generator pentru toate graficele din Capitolul 1: Fapte stilizate si randamente
==============================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date zilnice de piata (data/market): S&P 500 (1990-2026), BET-TR (2014-2026), Bitcoin
(2014-2026), aur spot (1990-2026); EUR/RON: cursul oficial de referinta BNR (iulie 2005-2026).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import acf
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import (load_data, load_close, read_market, LABELS, vol_close_to_close, vol_parkinson,
                      vol_garman_klass, vol_rogers_satchell, vol_yang_zhang, drawdown)

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
Teal     = '#17A2B8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
TABLE_DIR = HERE

ASSETS = ['sp500', 'bettr', 'btc', 'eurron', 'gold']
COLORS = {'sp500': MainBlue, 'bettr': IDAred, 'btc': Amber, 'eurron': Forest, 'gold': Purple}
PERIODS = {'sp500': 252, 'bettr': 252, 'btc': 365, 'eurron': 252, 'gold': 252}


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
# DATE
# =============================================================================
closes = {a: load_close(a) for a in ASSETS}
rets = {a: np.log(c).diff().dropna() for a, c in closes.items()}
# aurul (doar zile lucratoare) se anualizeaza cu frecventa efectiva a observatiilor
_years_gold = (closes['gold'].index[-1] - closes['gold'].index[0]).days / 365.25
PERIODS['gold'] = len(rets['gold']) / _years_gold
spx_ohlc = load_data('sp500')


# =============================================================================
# TABEL: statistici descriptive si teste
# =============================================================================
def summary_table():
    rows = []
    for a in ASSETS:
        r = rets[a]
        jb = stats.jarque_bera(r)
        lb_r = acorr_ljungbox(r, lags=[10], return_df=True)
        lb_r2 = acorr_ljungbox(r ** 2, lags=[10], return_df=True)
        arch = het_arch(r - r.mean(), nlags=5)
        rows.append({
            'asset': LABELS[a], 'start': r.index[0].date(), 'end': r.index[-1].date(), 'N': len(r),
            'mean_daily_pct': 100 * r.mean(), 'sd_daily_pct': 100 * r.std(),
            'ann_vol_pct': 100 * r.std() * np.sqrt(PERIODS[a]),
            'skew': stats.skew(r), 'exkurt': stats.kurtosis(r),
            'min_pct': 100 * r.min(), 'max_pct': 100 * r.max(),
            'JB': jb.statistic, 'JB_p': jb.pvalue,
            'LB10_r': lb_r['lb_stat'].iloc[0], 'LB10_r_p': lb_r['lb_pvalue'].iloc[0],
            'LB10_r2': lb_r2['lb_stat'].iloc[0], 'LB10_r2_p': lb_r2['lb_pvalue'].iloc[0],
            'ARCH5': arch[0], 'ARCH5_p': arch[1],
        })
    t = pd.DataFrame(rows).set_index('asset')
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_summary_statistics.csv'), float_format='%.6g')
    return t


def risk_table():
    rows = []
    for a in ASSETS:
        # Sharpe si Sortino pe randamente SIMPLE (aritmetice), r_f = 0: aceeasi definitie in tot cursul
        c, P = closes[a], PERIODS[a]
        R = c.pct_change().dropna()
        years = (c.index[-1] - c.index[0]).days / 365.25
        cagr = (c.iloc[-1] / c.iloc[0]) ** (1 / years) - 1
        mu, vol = R.mean() * P, R.std() * np.sqrt(P)
        downside = np.sqrt((np.minimum(R, 0) ** 2).mean()) * np.sqrt(P)   # medie peste TOATE zilele
        mdd = drawdown(c).min()
        sr_d = R.mean() / R.std()
        rows.append({'asset': LABELS[a], 'CAGR_pct': 100 * cagr, 'mean_simple_pct': 100 * mu,
                     'ann_vol_pct': 100 * vol, 'downside_pct': 100 * downside,
                     'Sharpe': mu / vol, 'Sharpe_SE_Lo': np.sqrt(P * (1 + sr_d ** 2 / 2) / len(R)),
                     'years': years, 'Sortino': mu / downside,
                     'maxDD_pct': 100 * mdd, 'Calmar': cagr / abs(mdd)})
    t = pd.DataFrame(rows).set_index('asset')
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_risk_measures.csv'), float_format='%.6g')
    return t


# =============================================================================
# FIG 1: Randamente simple vs logaritmice
# =============================================================================
def fig_simple_vs_log():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    R = np.linspace(-0.5, 0.5, 400)
    axes[0].plot(R, R, color=Gray, ls='--', lw=0.8, label='$r = R$')
    axes[0].plot(R, np.log1p(R), color=MainBlue, label='$r = \\ln(1+R)$')
    axes[0].axhline(0, color=LightGray, lw=0.5); axes[0].axvline(0, color=LightGray, lw=0.5)
    axes[0].set_xlabel('Simple return $R$'); axes[0].set_ylabel('Log return $r$')
    axes[0].set_title('$r \\approx R$ only for small returns', fontsize=8.5, loc='left')
    axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.26), ncol=2, frameon=False)

    c = closes['btc']
    R_d = c.pct_change().dropna()
    axes[1].plot(c.index, c / c.iloc[0], color=MainBlue, lw=0.9, label='True wealth $\\prod(1+R_t)$')
    axes[1].plot(R_d.index, 1 + R_d.cumsum(), color=IDAred, lw=0.9, label='$1+\\sum R_t$ (wrong)')
    axes[1].set_yscale('log')
    axes[1].set_title('Bitcoin: simple returns do not add up over time', fontsize=8.5, loc='left')
    axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
    plt.tight_layout()
    save_fig('ch1_simple_vs_log')


# =============================================================================
# FIG 2: Preturi si randamente pentru 5 piete
# =============================================================================
def fig_prices_returns():
    fig, axes = plt.subplots(len(ASSETS), 2, figsize=(7.4, 6.4), sharex='row')
    for i, a in enumerate(ASSETS):
        c, r = closes[a], rets[a]
        axes[i, 0].plot(c.index, c.values, color=COLORS[a], lw=0.7)
        axes[i, 0].set_yscale('log')
        axes[i, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
        axes[i, 0].yaxis.set_minor_formatter(plt.NullFormatter())
        if a == 'eurron':
            axes[i, 0].set_yticks([3.5, 4, 4.5, 5])
        axes[i, 0].set_ylabel(LABELS[a].replace(' (Romania)', '').replace(' (BNR)', ''), fontsize=8)
        axes[i, 1].plot(r.index, 100 * r.values, color=COLORS[a], lw=0.4)
        for ax in axes[i]:
            ax.tick_params(labelsize=7)
    axes[0, 0].set_title('Price (log scale)', fontsize=9, loc='left')
    axes[0, 1].set_title('Daily log return (%)', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch1_prices_returns')


# =============================================================================
# FIG 3: Histograma + QQ-plot (cozi groase)
# =============================================================================
def fig_hist_qq():
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2))
    for j, a in enumerate(['sp500', 'btc']):
        r = rets[a]
        z = (r - r.mean()) / r.std()
        ax = axes[0, j]
        ax.hist(z, bins=200, density=True, color=COLORS[a], alpha=0.55, range=(-8, 8))
        x = np.linspace(-8, 8, 600)
        ax.plot(x, stats.norm.pdf(x), color=IDAred, lw=1.0, label='Normal distribution')
        nu, loc, sc = stats.t.fit(z)
        ax.plot(x, stats.t.pdf(x, nu, loc, sc), color=Forest, lw=1.0, label=f'Student-t ($\\nu$={nu:.1f})')
        ax.set_xlim(-6, 6)
        ax.set_title(f'{LABELS[a]}: standardised returns', fontsize=8.5, loc='left')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False, fontsize=7)
        ax2 = axes[1, j]
        (osm, osr), _ = stats.probplot(z, dist='norm')
        ax2.scatter(osm, osr, s=3, color=COLORS[a], alpha=0.6)
        lim = [min(osm.min(), osr.min()), max(osm.max(), osr.max())]
        ax2.plot(lim, lim, color=IDAred, lw=0.8)
        ax2.set_xlabel('Normal-distribution quantiles'); ax2.set_ylabel('Empirical quantiles')
        ax2.set_title('QQ-plot vs Normal distribution', fontsize=8.5, loc='left')
    plt.tight_layout(h_pad=2.2)
    save_fig('ch1_hist_qq')


# =============================================================================
# FIG 4: Gaussianitate prin agregare
# =============================================================================
HORIZONS = [1, 2, 5, 10, 20, 60]


def aggregation_kurtosis():
    out = {}
    for a in ASSETS:
        r = rets[a]
        ks = []
        for h in HORIZONS:
            m = (len(r) // h) * h                                # doar ferestre complete de h zile
            agg = r.iloc[:m].groupby(np.arange(m) // h).sum()   # sume nesuprapuse
            ks.append(stats.kurtosis(agg))
        out[a] = ks
    return pd.DataFrame(out, index=HORIZONS)


def aggregation_counts():
    """Numarul de randamente nesuprapuse pe h zile si eroarea standard aproximativa a excesului
    de kurtosis sub normalitate, sqrt(24/n)."""
    n = pd.DataFrame({a: [len(rets[a]) // h for h in HORIZONS] for a in ASSETS}, index=HORIZONS)
    se = np.sqrt(24 / n)
    n.to_csv(os.path.join(TABLE_DIR, 'ch1_aggregation_n.csv'))
    se.to_csv(os.path.join(TABLE_DIR, 'ch1_aggregation_se.csv'), float_format='%.3g')
    return n, se


def fig_aggregation():
    k = aggregation_kurtosis()
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    for a in ASSETS:
        ax.plot(HORIZONS, k[a], marker='o', ms=3.5, color=COLORS[a], label=LABELS[a])
    ax.axhline(0, color=Gray, ls='--', lw=0.8)
    ax.text(1.05, 0.5, 'Normal distribution', color='black', fontsize=7.5, ha='left')
    ax.set_xscale('log'); ax.set_xticks(HORIZONS, [str(h) for h in HORIZONS])
    ax.set_xlabel('Aggregation horizon (trading days, non-overlapping)')
    ax.set_ylabel('Excess kurtosis')
    ax.set_title('Aggregational Gaussianity: tails thin out as the horizon grows', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=5, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_aggregation_kurtosis')
    k.to_csv(os.path.join(TABLE_DIR, 'ch1_aggregation_kurtosis.csv'), float_format='%.4g')
    return k


# =============================================================================
# FIG 5: ACF pentru r, |r|, r^2 (S&P 500)
# =============================================================================
def fig_acf_sp500(nlags=100):
    r = rets['sp500']
    band = 1.96 / np.sqrt(len(r))
    series = [(r, 'Returns $r_t$', MainBlue), (r.abs(), 'Absolute returns $|r_t|$', Amber),
              (r ** 2, 'Squared returns $r_t^2$', IDAred)]
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), sharey=True)
    for ax, (s, t, c) in zip(axes, series):
        a = acf(s, nlags=nlags, fft=True)[1:]
        ax.bar(range(1, nlags + 1), a, color=c, width=0.8)
        ax.axhspan(-band, band, color=LightGray, alpha=0.7, lw=0, label='i.i.d. reference band $\\pm1.96/\\sqrt{T}$')
        ax.axhline(0, color=Gray, lw=0.4)
        ax.set_title(t, fontsize=8.5, loc='left')
        ax.set_xlabel('Lag (days)')
    axes[0].set_ylabel('Autocorrelation')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=1, frameon=False)
    plt.tight_layout()
    save_fig('ch1_acf_sp500')


# =============================================================================
# FIG 6: ACF |r| pentru toate pietele (memorie lunga)
# =============================================================================
def fig_acf_abs_assets(nlags=250):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    out = {}
    for a in ASSETS:
        ac = acf(rets[a].abs(), nlags=nlags, fft=True)[1:]
        out[a] = ac
        ax.plot(range(1, nlags + 1), ac, color=COLORS[a], lw=1.0, label=LABELS[a])
    ax.set_xscale('log')
    ax.axhline(0, color=Gray, lw=0.4)
    ax.set_xlabel('Lag (days, log scale)')
    ax.set_ylabel('ACF of $|r_t|$')
    ax.set_title('Volatility clustering and long memory: slow, hyperbolic-like decay', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=5, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_acf_abs_assets')
    return pd.DataFrame(out, index=range(1, nlags + 1))


# =============================================================================
# FIG 7: Efectul de levier
# =============================================================================
def leverage_corr(r, K=20):
    ks = np.arange(-K, K + 1)
    a = r.abs()
    return ks, np.array([r.corr(a.shift(-k)) for k in ks])     # corr(r_t, |r_{t+k}|)


def fig_leverage():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    out = {}
    for ax, a in zip(axes, ['sp500', 'btc']):
        ks, c = leverage_corr(rets[a])
        out[a] = pd.Series(c, index=ks)
        ax.bar(ks, c, color=np.where(c < 0, IDAred, Forest), width=0.8)
        band = 1.96 / np.sqrt(len(rets[a]))
        ax.axhspan(-band, band, color=LightGray, alpha=0.7, lw=0, label='i.i.d. reference band $\\pm1.96/\\sqrt{T}$')
        ax.axhline(0, color=Gray, lw=0.4)
        ax.set_xlabel('Lag $k$ (days)')
        ax.set_title(f'{LABELS[a]}: corr$(r_t, |r_{{t+k}}|)$', fontsize=8.5, loc='left')
    axes[0].set_ylabel('Correlation')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=1, frameon=False)
    plt.tight_layout()
    save_fig('ch1_leverage')
    return pd.DataFrame(out)


# =============================================================================
# FIG 8: Volum si volatilitate
# =============================================================================
def fig_volume_volatility():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    res = {}
    for ax, a in zip(axes, ['sp500', 'btc']):
        d = load_data(a)
        v = np.log(d['Volume'].replace(0, np.nan))
        v_rel = (v - v.rolling(250).mean()).dropna()               # volum anormal (detrended)
        r_abs = np.log(d['Close']).diff().abs()
        df = pd.DataFrame({'v': v_rel, 'a': r_abs}).dropna()
        df = df[df['a'] > 0]
        rho = stats.spearmanr(df['v'], df['a'])[0]
        res[a] = rho
        ax.scatter(df['v'], 100 * df['a'], s=2, color=COLORS[a], alpha=0.25)
        ax.set_yscale('log')
        ax.set_xlabel('Abnormal log volume (vs 250-day mean)')
        ax.set_title(f'{LABELS[a]}: Spearman $\\rho$ = {rho:.2f}', fontsize=8.5, loc='left')
    axes[0].set_ylabel('$|r_t|$ (%, log scale)')
    plt.tight_layout()
    save_fig('ch1_volume_volatility')
    return res


# =============================================================================
# FIG 9: Efectul Taylor
# =============================================================================
def fig_taylor():
    deltas = np.round(np.arange(0.25, 3.01, 0.25), 2)
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    out = {}
    for lag, c in zip([1, 5, 20], [MainBlue, Amber, IDAred]):
        vals = [acf(rets['sp500'].abs() ** d, nlags=lag, fft=True)[lag] for d in deltas]
        out[lag] = vals
        ax.plot(deltas, vals, marker='o', ms=3, color=c, label=f'lag {lag}')
        ax.plot(deltas[np.argmax(vals)], max(vals), marker='*', ms=10, color=c)
    ax.axvline(1, color=Gray, ls=':', lw=0.8)
    ax.set_xlabel('Power $\\delta$')
    ax.set_ylabel('corr$(|r_t|^\\delta, |r_{t-k}|^\\delta)$')
    ax.set_title('Taylor effect, S&P 500: the peak (stars) shifts towards $\\delta = 1$ as the lag grows',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_taylor_effect')
    return pd.DataFrame(out, index=deltas)


# =============================================================================
# FIG 10: Asimetrie castig/pierdere (cozi)
# =============================================================================
def fig_gain_loss():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={'width_ratios': [1.25, 1]})
    r = rets['sp500']
    for s, c, lab in [(-r[r < 0], IDAred, 'Losses $-r_t$'), (r[r > 0], Forest, 'Gains $r_t$')]:
        x = np.sort(s.values)[::-1]
        surv = np.arange(1, len(x) + 1) / len(r)
        axes[0].loglog(100 * x, surv, color=c, lw=1.0, label=lab)
    axes[0].set_xlim(0.5, 15)
    axes[0].set_xticks([0.5, 1, 2, 5, 10])
    axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    axes[0].xaxis.set_minor_formatter(plt.NullFormatter())
    axes[0].set_xlabel('Daily move $x$ (%, log scale)'); axes[0].set_ylabel('$P(X > x)$')
    axes[0].set_title('S&P 500 tails: losses are heavier', fontsize=8.5, loc='left')
    axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=2, frameon=False)
    q = pd.DataFrame({LABELS[a].replace(' (Romania)', '').replace(' (BNR)', ''): [-100 * rets[a].quantile(0.01), 100 * rets[a].quantile(0.99)]
                      for a in ASSETS}, index=['1% loss', '99% gain']).T
    x = np.arange(len(q))
    axes[1].bar(x - 0.18, q['1% loss'], 0.36, color=IDAred, label='$-q_{0.01}$')
    axes[1].bar(x + 0.18, q['99% gain'], 0.36, color=Forest, label='$q_{0.99}$')
    axes[1].set_xticks(x, q.index, fontsize=7, rotation=20)
    axes[1].set_ylabel('Daily move (%)')
    axes[1].set_title('1% tails by market', fontsize=8.5, loc='left')
    axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=2, frameon=False, fontsize=7)
    plt.tight_layout()
    save_fig('ch1_gain_loss')
    return q


# =============================================================================
# FIG 11: Estimatori de volatilitate (S&P 500 OHLC)
# =============================================================================
def fig_vol_estimators():
    # inainte de 2007 'open' este egal cu inchiderea precedenta (artefact de date) -> folosim 2008-2026
    d = spx_ohlc.loc['2008-01-01':]
    est = pd.DataFrame({
        'Close-to-close': vol_close_to_close(d), 'Parkinson': vol_parkinson(d),
        'Garman-Klass': vol_garman_klass(d), 'Rogers-Satchell': vol_rogers_satchell(d),
        'Yang-Zhang': vol_yang_zhang(d)}).dropna()
    seg = est.loc['2019-07-01':'2021-06-30']
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={'width_ratios': [1.6, 1]})
    cols = [Teal, MainBlue, Forest, Amber, IDAred]
    for c, col in zip(est.columns, cols):
        axes[0].plot(seg.index, 100 * seg[c], color=col, lw=0.9, label=c)
    import matplotlib.dates as mdates
    axes[0].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    axes[0].tick_params(axis='x', labelsize=7, rotation=30)
    axes[0].set_ylabel('Annualised volatility (%, 21-day)')
    axes[0].set_title('S&P 500 around the COVID-19 crash', fontsize=8.5, loc='left')
    axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.28), ncol=3, frameon=False, fontsize=7)
    # eficienta relativa: variabilitatea saptamanala a estimatorului (zgomot) vs close-to-close
    noise = est.diff().std()
    eff = (noise['Close-to-close'] / noise) ** 2
    axes[1].barh(eff.index, eff.values, color=cols, alpha=0.85)
    axes[1].axvline(1, color=Gray, ls=':', lw=0.8)
    axes[1].set_xlabel('Relative smoothness vs close-to-close')
    axes[1].set_title('Noise of daily updates', fontsize=8.5, loc='left')
    axes[1].tick_params(axis='y', labelsize=7.5)
    plt.tight_layout()
    save_fig('ch1_vol_estimators')
    means = 100 * est.mean()
    return pd.DataFrame({'mean_pct': means, 'rel_smoothness': eff})


# =============================================================================
# FIG 12: Drawdown-uri
# =============================================================================
def fig_drawdowns():
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for a in ASSETS:
        dd = drawdown(closes[a])
        ax.plot(dd.index, 100 * dd, color=COLORS[a], lw=0.8, label=f'{LABELS[a]} (max {100 * dd.min():.0f}%)')
    ax.set_ylabel('Drawdown from running peak (%)')
    ax.set_title('Underwater curves: depth and duration of losses', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.12)
    plt.tight_layout()
    save_fig('ch1_drawdowns')


# =============================================================================
# FIG 13: Randament vs risc
# =============================================================================
def fig_risk_return(t):
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    for a in ASSETS:
        row = t.loc[LABELS[a]]
        ax.scatter(row['ann_vol_pct'], row['CAGR_pct'], s=60, color=COLORS[a], zorder=3)
        off = {'sp500': (8, -14), 'gold': (-8, 14), 'bettr': (8, 0), 'btc': (-10, -18), 'eurron': (8, 2)}[a]
        ax.annotate(f"{LABELS[a]}\nSharpe {row['Sharpe']:.2f} (SE {row['Sharpe_SE_Lo']:.2f}), MDD {row['maxDD_pct']:.0f}%",
                    (row['ann_vol_pct'], row['CAGR_pct']), xytext=off, textcoords='offset points', fontsize=7,
                    ha='right' if off[0] < 0 else 'left')
    ax.set_xscale('log')
    ax.set_xticks([5, 10, 20, 50, 100])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel('Annualised volatility (%, log scale)')
    ax.set_ylabel('CAGR (%)')
    ax.set_xlim(3, 120)
    ax.axhline(0, color=Gray, lw=0.4)
    ax.set_title('Risk and return across markets (full samples; Sharpe SE for i.i.d. Normal returns)', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch1_risk_return')


# =============================================================================
# FIG 14: Volatilitate rulanta (clustering in timp)
# =============================================================================
def fig_rolling_vol():
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    for a in ASSETS:
        v = rets[a].rolling(63).std() * np.sqrt(PERIODS[a]) * 100
        ax.plot(v.index, v, color=COLORS[a], lw=0.8, label=LABELS[a])
    ax.set_yscale('log')
    ax.set_yticks([0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_ylabel('63-day volatility (%, ann., log)')
    ax.set_title('Volatility is time-varying and comes in regimes', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=5, y=-0.12)
    plt.tight_layout()
    save_fig('ch1_rolling_vol')


# =============================================================================
# MAIN
# =============================================================================
# =============================================================================
# FIG 12: Estimatorul Hill al indicelui de coada
# =============================================================================
def hill_estimator(x, k):
    """alpha_hat(k) = [ (1/k) sum_{i=1..k} ln(X_(i) / X_(k+1)) ]^{-1}, X_(1) >= X_(2) >= ..."""
    x = np.sort(np.asarray(x)[np.asarray(x) > 0])[::-1]
    return 1.0 / np.mean(np.log(x[:k] / x[k]))


HILL_FRACS = np.round(np.arange(0.005, 0.1001, 0.0025), 4)


def hill_table(frac=0.025):
    """Indicele de coada Hill pentru |r_t|, pierderi (-r_t) si castiguri (r_t) la k = frac * n."""
    rows = []
    for a in ASSETS:
        r = rets[a].values
        k = int(frac * len(r))
        rows.append({'asset': LABELS[a], 'n': len(r), 'k': k,
                     'alpha_abs': hill_estimator(np.abs(r), k),
                     'alpha_loss': hill_estimator(-r, k), 'alpha_gain': hill_estimator(r, k),
                     'alpha_abs_min_1to5pct': min(hill_estimator(np.abs(r), int(f * len(r))) for f in (0.01, 0.025, 0.05)),
                     'alpha_abs_max_1to5pct': max(hill_estimator(np.abs(r), int(f * len(r))) for f in (0.01, 0.025, 0.05))})
    t = pd.DataFrame(rows).set_index('asset')
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_hill.csv'), float_format='%.4g')
    return t


def fig_hill():
    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    for a in ASSETS:
        r = np.abs(rets[a].values)
        al = [hill_estimator(r, max(int(f * len(r)), 5)) for f in HILL_FRACS]
        ax.plot(100 * HILL_FRACS, al, color=COLORS[a], lw=1.1, label=LABELS[a])
    ax.axhspan(2, 4, color=LightGray, alpha=0.5, lw=0)
    ax.axhline(4, color=Gray, ls='--', lw=0.8)
    ax.axhline(2, color=Gray, ls=':', lw=0.8)
    ax.text(9.9, 4.05, r'$\alpha = 4$: kurtosis exists above', fontsize=7, color='black', ha='right', va='bottom')
    ax.text(0.6, 1.95, r'$\alpha = 2$: variance exists above', fontsize=7, color='black', ha='left', va='top')
    ax.set_xlabel('Tail fraction $k/n$ used by the estimator (%)')
    ax.set_ylabel(r'Hill estimate $\hat\alpha$')
    ax.set_ylim(1, 6)
    ax.set_title('Hill plots of $|r_t|$: tail index mostly between 2 and 4', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=5, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_hill_plot')


def moving_block_indices(T, block, rng):
    """Indicii unui esantion bootstrap pe blocuri mobile (moving-block) de lungime `block`."""
    nb = int(np.ceil(T / block))
    st = rng.integers(0, T - block + 1, nb)      # toate cele T - block + 1 inceputuri valide
    return (st[:, None] + np.arange(block)[None, :]).ravel()[:T]


def hill_threshold(x, u):
    """Hill cu prag fix u: k = #{x > u}, alpha_hat = k / sum ln(x_i / u) pe x_i > u."""
    x = np.asarray(x)
    e = x[x > u]
    return len(e) / np.sum(np.log(e / u))


def hill_inference(frac=0.025, n_boot=500, block=20, seed=42):
    """Hill pentru |r_t| la k = frac*n: IC i.i.d. alpha(1 +/- 1.96/sqrt(k)), EE bootstrap pe blocuri
    si comparatia cu cozile unilaterale la ACELASI prag u (min al pragurilor unilaterale)."""
    rng = np.random.default_rng(seed)
    rows = []
    for a in ASSETS:
        r = rets[a].values
        n = len(r)
        k = int(frac * n)
        al = hill_estimator(np.abs(r), k)
        boot = [hill_estimator(np.abs(r)[moving_block_indices(n, block, rng)], k) for _ in range(n_boot)]
        u = min(np.sort(-r)[::-1][k], np.sort(r)[::-1][k])
        kL, kG, kA = int((-r > u).sum()), int((r > u).sum()), int((np.abs(r) > u).sum())
        rows.append({'asset': LABELS[a], 'n': n, 'k': k, 'alpha_abs': al, 'se_iid': al / np.sqrt(k),
                     'se_block': np.std(boot, ddof=1), 'ci_lo': al * (1 - 1.96 / np.sqrt(k)),
                     'ci_hi': al * (1 + 1.96 / np.sqrt(k)), 'alpha_loss_k': hill_estimator(-r, k),
                     'alpha_gain_k': hill_estimator(r, k), 'u_common_pct': 100 * u, 'k_abs_u': kA,
                     'alpha_abs_u': hill_threshold(np.abs(r), u), 'alpha_loss_u': hill_threshold(-r, u),
                     'alpha_gain_u': hill_threshold(r, u)})
    t = pd.DataFrame(rows).set_index('asset')
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_hill_inference.csv'), float_format='%.4g')
    return t


def robust_moments(n_boot=1000, block=20, seed=42):
    """Asimetrie si aplatizare pe cuantile (Kim & White 2004): Hinkley (5%-95%) si Crow-Siddiqui
    (2.5%, 97.5% fata de quartile, minus 2.91, valoarea distributiei Normale); IC bootstrap pe blocuri."""
    def qstats(v):
        q = np.quantile(v, [0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975])
        return ((q[5] + q[1] - 2 * q[3]) / (q[5] - q[1]), (q[6] - q[0]) / (q[4] - q[2]) - 2.91)
    rng = np.random.default_rng(seed)
    rows = []
    for a in ASSETS:
        v = rets[a].values
        sk, ku = qstats(v)
        b = np.array([qstats(v[moving_block_indices(len(v), block, rng)]) for _ in range(n_boot)])
        rows.append({'asset': LABELS[a], 'skew_moment': stats.skew(v), 'skew_hinkley': sk,
                     'skew_lo': np.quantile(b[:, 0], 0.025), 'skew_hi': np.quantile(b[:, 0], 0.975),
                     'exkurt_moment': stats.kurtosis(v), 'kurt_cs': ku,
                     'kurt_lo': np.quantile(b[:, 1], 0.025), 'kurt_hi': np.quantile(b[:, 1], 0.975)})
    t = pd.DataFrame(rows).set_index('asset')
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_robust_moments.csv'), float_format='%.4g')
    return t


def acf_robust_lag1():
    """rho_1 cu banda i.i.d. 1.96/sqrt(T) si banda robusta 1.96 sqrt(tau_1) (Romano & Thombs 1996)."""
    rows = []
    for a in ASSETS:
        x = (rets[a] - rets[a].mean()).values
        T, s2 = len(x), np.sum(x ** 2)
        rho = np.sum(x[1:] * x[:-1]) / s2
        tau = np.sum(x[1:] ** 2 * x[:-1] ** 2) / s2 ** 2
        rows.append({'asset': LABELS[a], 'T': T, 'rho1': rho, 'T_tau1': T * tau, 'band_iid': 1.96 / np.sqrt(T),
                     'band_robust': 1.96 * np.sqrt(tau), 't_iid': rho * np.sqrt(T), 't_robust': rho / np.sqrt(tau)})
    return pd.DataFrame(rows).set_index('asset')


def periodogram(x):
    x = np.asarray(x) - np.mean(x)
    T = len(x)
    return 2 * np.pi * np.arange(T) / T, np.abs(np.fft.fft(x)) ** 2 / (2 * np.pi * T)


def local_whittle(x, m):
    """Robinson (1995): d minimizeaza R(d) = ln(mean(lambda_j^{2d} I_j)) - 2d mean(ln lambda_j); EE = 1/(2 sqrt m)."""
    from scipy.optimize import minimize_scalar
    lam, I = periodogram(x)
    l, Ij = lam[1:m + 1], I[1:m + 1]
    R = lambda d: np.log(np.mean(l ** (2 * d) * Ij)) - 2 * d * np.mean(np.log(l))
    return minimize_scalar(R, bounds=(-0.49, 0.99), method='bounded').x, 1 / (2 * np.sqrt(m))


def gph(x, m):
    """Geweke & Porter-Hudak (1983): panta lui ln I_j pe -2 ln(2 sin(lambda_j/2)); EE = pi/sqrt(24 m)."""
    lam, I = periodogram(x)
    X = -2 * np.log(2 * np.sin(lam[1:m + 1] / 2))
    return np.polyfit(X, np.log(I[1:m + 1]), 1)[0], np.pi / np.sqrt(24 * m)


def cusum_squares_break(r):
    """Data rupturii in varianta necoditionata: argmax |C_k/C_T - k/T| (Inclan & Tiao 1994)."""
    x = np.asarray(r) - np.mean(r)
    C = np.cumsum(x ** 2)
    T = len(x)
    D = C / C[-1] - np.arange(1, T + 1) / T
    j = int(np.argmax(np.abs(D)))
    return j, np.sqrt(T / 2) * np.abs(D[j])


def long_memory_table(power=0.65):
    """d pentru |r_t|: local Whittle si GPH cu m = T^0.65; apoi re-estimare de o parte si de alta
    a rupturii de varianta estimate (verificarea 'memorie lunga sau rupturi?')."""
    rows = []
    for a in ASSETS:
        r = rets[a]
        x = np.abs(r.values)
        T = len(x)
        m = int(T ** power)
        dlw, slw = local_whittle(x, m)
        dg, sg = gph(x, m)
        j, it = cusum_squares_break(r.values)
        pre, post = x[:j + 1], x[j + 1:]
        dpre, spre = local_whittle(pre, int(len(pre) ** power))
        dpost, spost = local_whittle(post, int(len(post) ** power))
        P = PERIODS[a]
        rows.append({'asset': LABELS[a], 'T': T, 'm': m, 'd_lw': dlw, 'se_lw': slw, 'd_gph': dg, 'se_gph': sg,
                     'break_date': r.index[j].date(), 'IT_stat': it,
                     'vol_pre_pct': 100 * r.values[:j + 1].std() * np.sqrt(P),
                     'vol_post_pct': 100 * r.values[j + 1:].std() * np.sqrt(P),
                     'd_pre': dpre, 'se_pre': spre, 'd_post': dpost, 'se_post': spost})
    t = pd.DataFrame(rows).set_index('asset')
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_long_memory.csv'), float_format='%.4g')
    return t


# =============================================================================
# VERIFICARE: deschideri "stale" ale indicelui S&P 500 (Yang-Zhang)
# =============================================================================
def stale_open_check(start='2008-01-01'):
    """Compara indicele S&P 500 cu ETF-ul SPY (deschidere = pret tranzactionat)."""
    g = spx_ohlc.loc[start:]
    spy = read_market('SPY.US').loc[start:]
    f = spy['adjusted_close'] / spy['close']
    s = pd.DataFrame({'Open': spy['open'] * f, 'High': spy['high'] * f, 'Low': spy['low'] * f,
                      'Close': spy['adjusted_close']})
    rows = []
    for name, d in [('S&P 500 index', g), ('SPY ETF', s)]:
        on = np.log(d['Open'] / d['Close'].shift(1))
        oc = np.log(d['Close'] / d['Open'])
        rows.append({'series': name, 'close_to_close': vol_close_to_close(d).mean(),
                     'yang_zhang': vol_yang_zhang(d).mean(), 'parkinson': vol_parkinson(d).mean(),
                     'overnight_vol': on.std() * np.sqrt(252), 'open_to_close_vol': oc.std() * np.sqrt(252),
                     'cov_share': 2 * on.cov(oc) / np.log(d['Close']).diff().var(),
                     'open_eq_prev_close': (np.abs(d['Open'] / d['Close'].shift(1) - 1) < 1e-6).mean()})
    t = pd.DataFrame(rows).set_index('series')
    o = spx_ohlc['Open']; c = spx_ohlc['Close'].shift(1)
    eq = (np.abs(o / c - 1) < 1e-6).groupby(spx_ohlc.index.year).mean()
    t.to_csv(os.path.join(TABLE_DIR, 'ch1_stale_open.csv'), float_format='%.4g')
    eq.to_csv(os.path.join(TABLE_DIR, 'ch1_stale_open_by_year.csv'), float_format='%.4g')
    return t, eq


# =============================================================================
# STUDIU DE CAZ: volatilitatea depinde de traiectorie (Guyon & Lekeufack, 2023)
# =============================================================================
PDV_LAGS = 1000                 # ultimele 1000 de randamente, Sectiunea 3.3
PDV_DT = 1 / 252
PDV_TABLE3_VIX = (0.057, -0.095, 0.82, 1.06, 0.020, 1.60, 0.052)   # b0, b1, b2, a1, d1, a2, d2 (Table 3)
PDV_TRAIN = ('2000-01-01', '2018-12-31')
PDV_TEST = ('2019-01-01', '2022-05-15')


def pdv_kernel(alpha, delta, n=PDV_LAGS):
    """Nucleul TSPL normalizat, eq. (3.9): K(tau) = (tau + delta)^(-alpha) / Z, tau = i * dt,
    cu Z ales astfel incat sum_i K(i dt) dt = 1 pe fereastra de n zile (normalizarea din Table 3)."""
    tau = np.arange(n) * PDV_DT
    w = (tau + delta) ** (-alpha)
    return w / (w.sum() * PDV_DT)


def pdv_predict(X, p):
    """Modelul (3.7): sigma_t = b0 + b1 R1_t + b2 Sigma_t; X[t, i] = r_{t-i}."""
    b0, b1, b2, a1, d1, a2, d2 = p
    R1 = X @ pdv_kernel(a1, d1)
    Sig = np.sqrt((X ** 2) @ pdv_kernel(a2, d2))
    return b0 + b1 * R1 + b2 * Sig


def pdv_data():
    """Matricea randamentelor simple trecute ale S&P 500 si VIX/100 pe zilele S&P 500."""
    spx = read_market('GSPC.INDX')['close']
    r = spx / spx.shift(1) - 1
    X = pd.DataFrame(np.column_stack([r.shift(i).values for i in range(PDV_LAGS)]), index=r.index)
    vix = read_market('VIX.INDX')['close'] / 100
    return X.join(vix.rename('vix'), how='inner').dropna()


def pdv_fit():
    """Celor mai mici patrate neliniare pe 2000-2018, pornind de la randul VIX din Table 3."""
    from scipy.optimize import least_squares
    df = pdv_data()
    tr = df.loc[PDV_TRAIN[0]:PDV_TRAIN[1]]
    lb = [-np.inf] * 3 + [1.0001, 1e-4, 1.0001, 1e-4]
    ub = [np.inf] * 3 + [20, 5, 20, 5]
    res = least_squares(lambda p: pdv_predict(tr.iloc[:, :PDV_LAGS].values, p) - tr['vix'].values,
                        x0=PDV_TABLE3_VIX, bounds=(lb, ub), method='trf')
    fit = pd.Series(pdv_predict(df.iloc[:, :PDV_LAGS].values, res.x), index=df.index)
    rows = []
    for name, (a, b) in [('train', PDV_TRAIN), ('test', PDV_TEST),
                         ('after test', ('2022-05-16', str(df.index[-1].date())))]:
        y, yh = df['vix'].loc[a:b], fit.loc[a:b]
        rows.append({'set': name, 'start': y.index[0].date(), 'end': y.index[-1].date(), 'N': len(y),
                     'RMSE': np.sqrt(np.mean((y - yh) ** 2)),
                     'r2': 1 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)})
    scores = pd.DataFrame(rows).set_index('set')
    params = pd.Series(res.x, index=['beta0', 'beta1', 'beta2', 'alpha1', 'delta1', 'alpha2', 'delta2'])
    params.to_csv(os.path.join(TABLE_DIR, 'ch1_pdv_parameters.csv'), float_format='%.4g')
    scores.to_csv(os.path.join(TABLE_DIR, 'ch1_pdv_scores.csv'), float_format='%.4g')
    return df['vix'], fit, params, scores


def fig_cs_pdv_vix(vix, fit, scores):
    """Figure 3.2 (top) replicat si extins: VIX observat vs. VIX prezis doar din traiectoria S&P 500."""
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.6, 3.7), sharex=True, gridspec_kw={'height_ratios': [2.3, 1]})
    v, f = 100 * vix.loc[PDV_TRAIN[0]:], 100 * fit.loc[PDV_TRAIN[0]:]
    ax.plot(v.index, v, color=MainBlue, lw=0.7, label='VIX (observed)')
    ax.plot(f.index, f, color=IDAred, lw=0.7, label='Predicted from past S&P 500 returns, eq. (3.7)')
    ratio = vix.loc[PDV_TRAIN[0]:] / fit.loc[PDV_TRAIN[0]:]
    ax2.plot(ratio.index, ratio, color=Forest, lw=0.6, label='Ratio observed / predicted VIX')
    ax2.axhline(1, color=Gray, lw=0.6, ls='--')
    for a in (ax, ax2):
        a.axvspan(pd.Timestamp(PDV_TEST[0]), pd.Timestamp(PDV_TEST[1]), color=Amber, alpha=0.15, lw=0)
        a.axvline(pd.Timestamp(PDV_TEST[1]), color=Gray, lw=0.6, ls=':')
    top = 0.97
    for (a, b), key, lab in [(PDV_TRAIN, 'train', 'Training 2000-2018'), (PDV_TEST, 'test', 'Test'),
                             (('2022-05-16', str(vix.index[-1].date())), 'after test', 'After test')]:
        mid = pd.Timestamp(a) + (pd.Timestamp(b) - pd.Timestamp(a)) / 2
        ax.text(mid, 99, f"{lab}\n$r^2$ = {scores.loc[key, 'r2']:.3f}", ha='center', va='top', fontsize=8, color='black')
    ax.set_ylim(0, 100)
    ax.set_ylabel('Volatility (%)')
    ax2.set_ylabel('Ratio')
    ax2.set_ylim(0.4, 1.8)
    ax.set_title('VIX explained by the S&P 500 path alone (test set shaded)')
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch1_cs_pdv_vix')


def fig_cs_pdv_kernels(params):
    """Figure 3.1 / B.1 replicat: ponderile zilnice K(i dt) dt ale celor doi nuclei, scala log-log."""
    lag = np.arange(1, PDV_LAGS)
    p3 = PDV_TABLE3_VIX
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.loglog(lag, pdv_kernel(params['alpha1'], params['delta1'])[1:] * PDV_DT, color=IDAred, lw=1.4,
              label=f"$K_1$ (trend $R_1$), ours: $\\alpha_1$ = {params['alpha1']:.2f}, $\\delta_1$ = {params['delta1']:.3f}")
    ax.loglog(lag, pdv_kernel(p3[3], p3[4])[1:] * PDV_DT, color=Orange, lw=1.2, ls='--',
              label=f"$K_1$, Table 3: $\\alpha_1$ = {p3[3]:.2f}, $\\delta_1$ = {p3[4]:.3f}")
    ax.loglog(lag, pdv_kernel(params['alpha2'], params['delta2'])[1:] * PDV_DT, color=MainBlue, lw=1.4,
              label=f"$K_2$ (volatility $\\Sigma$), ours: $\\alpha_2$ = {params['alpha2']:.2f}, $\\delta_2$ = {params['delta2']:.3f}")
    ax.loglog(lag, pdv_kernel(p3[5], p3[6])[1:] * PDV_DT, color=Teal, lw=1.4, ls=(0, (2, 2)),
              label=f"$K_2$, Table 3: $\\alpha_2$ = {p3[5]:.2f}, $\\delta_2$ = {p3[6]:.3f}")
    ax.set_xlabel('Lag i (trading days, log scale)')
    ax.set_ylabel('Weight $K(i\\Delta t)\\Delta t$ (log scale)')
    ax.set_title('Fitted kernels of the VIX model')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    plt.tight_layout()
    save_fig('ch1_cs_pdv_kernels')


def pdv_weight_shares(params):
    """Ponderea totala (din 1000 de zile) pe ultimele 5 zile si dincolo de 250 de zile."""
    out = {}
    for k, (a, d) in {'K1': (params['alpha1'], params['delta1']), 'K2': (params['alpha2'], params['delta2'])}.items():
        w = pdv_kernel(a, d) * PDV_DT
        out[k] = {'today': w[0], 'first5': w[:5].sum(), 'beyond250': w[250:].sum(), 'total1000': w.sum()}
    return pd.DataFrame(out)


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    print('Chapter 1 charts')
    print(summary_table().round(4).T)
    rt = risk_table(); print(rt.round(3))
    fig_simple_vs_log()
    fig_prices_returns()
    fig_hist_qq()
    print(fig_aggregation().round(2))
    n_agg, se_agg = aggregation_counts(); print(n_agg); print(se_agg.round(2))
    fig_acf_sp500()
    ac = fig_acf_abs_assets(); print(ac.loc[[1, 5, 20, 100, 250]].round(3))
    lev = fig_leverage(); print(lev.loc[[-5, -1, 0, 1, 5, 10]].round(3))
    print('   volume-volatility rho:', fig_volume_volatility())
    print(fig_taylor().round(3))
    print(fig_gain_loss().round(2))
    print(fig_vol_estimators().round(3))
    fig_drawdowns()
    fig_risk_return(rt)
    fig_rolling_vol()
    fig_hill(); print(hill_table().round(2))
    print(hill_inference().round(3).T)
    print(robust_moments().round(3).T)
    print(acf_robust_lag1().round(3).T)
    print(long_memory_table().round(3).T)
    so, so_y = stale_open_check(); print(so.round(3)); print(so_y.loc[[1995, 2000, 2005, 2006, 2007, 2008, 2010, 2020, 2026]].round(3))
    pvix, pfit, pparams, pscores = pdv_fit(); print(pparams.round(3)); print(pscores.round(3))
    fig_cs_pdv_vix(pvix, pfit, pscores)
    fig_cs_pdv_kernels(pparams)
    print(pdv_weight_shares(pparams).round(3))

"""
Generator pentru toate graficele din Capitolul 0: Financial Markets in 2026
==========================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date reale: date zilnice de piata (data/market), FRED, DefiLlama, BNR (EUR/RON).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import load, load_panel  # noqa: E402

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
Teal     = '#17A2B8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')


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


def bottom_legend(fig, ncol=3, handles=None, labels=None, fontsize=8):
    """Legend below the figure (outside the axes), after tight_layout; save_fig keeps it (bbox_inches='tight')."""
    plt.tight_layout()
    if handles is None:
        handles, labels, seen = [], [], set()
        for ax in fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in seen and not l.startswith('_'):
                    handles.append(h); labels.append(l); seen.add(l)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False, fontsize=fontsize)


def log_axis(ax, ticks):
    """Log axis with readable labels (no scientific notation)."""
    ax.set_yscale('log')
    ax.set_yticks(ticks)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    ax.yaxis.set_minor_formatter(plt.NullFormatter())


# =============================================================================
# DATE
# =============================================================================
ASSET_NAMES = ['S&P 500', 'Euro Stoxx 50', 'Nikkei 225', 'Gold', 'US Treasuries 20y+ (TLT)', 'Bitcoin',
               'Ethereum', 'VIX', 'SPY', 'RSP', 'IBIT', 'EUR/USD', 'BET-TR']
BVB_NAMES = ['Banca Transilvania', 'OMV Petrom', 'BRD', 'Transgaz', 'Romgaz', 'Hidroelectrica']

px = load_panel(ASSET_NAMES)                        # data/market (local sau din repo)
bvb = load_panel(BVB_NAMES)                         # data/market, adjusted_close
ibit_volume = load('IBIT volume')
fred = load_panel(['DGS10', 'DGS2', 'FEDFUNDS'])    # FRED
stable = load('Stablecoins')                        # DefiLlama (mld. USD)
eurron = load('EUR/RON')                            # BNR (curs oficial de referinta)
eurron_mkt = load('EUR/RON (EODHD)')          # seria EODHD: contine erori de cotatie (slide-ul Data pitfalls)
bonds = load_panel(['Romania 10y', 'Germany 10y'])  # curatate in fig_romania: 0.00% (24 Dec 2013), duminici 2022

CROSS = ['S&P 500 TR (SPY)', 'Euro Stoxx 50 (USD)', 'Nikkei 225 (USD)', 'Gold', 'US Treasuries 20y+ (TLT)', 'Bitcoin']
CROSS_COL = [MainBlue, Forest, Purple, Amber, Teal, Orange]
fx_usd = load_panel(['USD per EUR', 'JPY per USD'])   # FRED


def to_usd(local, fx, invert=False):
    """Convert a local-currency index to USD with the FRED rate of the same day
    (the last available rate, at most 5 days back, if the day is missing)."""
    f = fx.dropna().reindex(local.index, method='ffill', tolerance=pd.Timedelta(days=5))
    return (local / f if invert else local * f).dropna()


def cross_panel():
    """Cross-asset series, all in USD:
    S&P 500 = adjusted SPY (total return); Euro Stoxx 50 and Nikkei 225 = price indices converted to USD;
    TLT = total return; gold = spot; Bitcoin = price."""
    return {
        'S&P 500 TR (SPY)': px['SPY'].dropna(),
        'Euro Stoxx 50 (USD)': to_usd(px['Euro Stoxx 50'].dropna(), fx_usd['USD per EUR']),
        'Nikkei 225 (USD)': to_usd(px['Nikkei 225'].dropna(), fx_usd['JPY per USD'], invert=True),
        'Gold': px['Gold'].dropna(),
        'US Treasuries 20y+ (TLT)': px['US Treasuries 20y+ (TLT)'].dropna(),
        'Bitcoin': px['Bitcoin'].dropna(),
        'Ethereum': px['Ethereum'].dropna(),
        'EUR/USD': px['EUR/USD'].dropna(),
    }


def dividend_gap(start='2015-01-02'):
    """CAGR gap between the S&P 500 with dividends reinvested (adjusted SPY) and the price index."""
    c_tr, _ = ann_stats(px['SPY'].loc[start:])
    c_px, _ = ann_stats(px['S&P 500'].loc[start:])
    return c_tr, c_px, c_tr - c_px


def clean_series(y, max_dev=1.0, window=11):
    """Drop weekend rows and points more than max_dev from the centred rolling median."""
    y = y[y.index.dayofweek < 5]
    med = y.rolling(window, center=True, min_periods=3).median()
    return y[(y - med).abs() <= max_dev]


def drawdown(p):
    """Drawdown from the previous peak: P_t / max_{s<=t} P_s - 1."""
    return p / p.cummax() - 1


def ann_stats(p, periods=252):
    """Annualised return (CAGR) and annualised volatility from daily prices.

    periods='obs' uses the observed number of observations per year of the series.
    """
    p = p.dropna()
    years = (p.index[-1] - p.index[0]).days / 365.25
    cagr = (p.iloc[-1] / p.iloc[0]) ** (1 / years) - 1
    r = np.log(p).diff().dropna()
    if periods == 'obs':
        periods = len(r) / years
    return cagr, r.std() * np.sqrt(periods)


# =============================================================================
# FIG 1: Cresterea a 1 USD investit in 2015 (clase de active)
# =============================================================================
def fig_cross_asset_growth(start='2015-01-02'):
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    out = {}
    panel = cross_panel()
    for name, c in zip(CROSS, CROSS_COL):
        s = panel[name].loc[start:].dropna()
        g = s / s.iloc[0]
        ax.plot(g.index, g.values, color=c, lw=0.9 if name != 'Bitcoin' else 0.8,
                label=f'{name} (x{g.iloc[-1]:.1f})')
        out[name] = g.iloc[-1]
    log_axis(ax, [0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500])
    ax.axhline(1, color=Gray, lw=0.4, ls=':')
    ax.set_ylabel('Growth of 1 USD (log scale)')
    ax.set_title(f'{pd.Timestamp(start).year}-2026, all in USD: S&P 500 and TLT = total return, '
                 'Euro Stoxx 50 and Nikkei 225 = price, gold = spot',
                 fontsize=8.5, loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch0_cross_asset_growth')
    return pd.Series(out)


# =============================================================================
# FIG 2: Randament vs risc, 2015-2026
# =============================================================================
OFFSETS = {'Gold': (-7, 2, 'right'), 'S&P 500 TR (SPY)': (0, 8, 'center'), 'Nikkei 225 (USD)': (7, 2, 'left'),
           'Euro Stoxx 50 (USD)': (7, -7, 'left'), 'US Treasuries 20y+ (TLT)': (-7, -9, 'right'),
           'EUR/USD': (0, 7, 'center'), 'EUR/RON': (6, 3, 'left'), 'Bitcoin': (-6, 3, 'right'),
           'Ethereum': (-6, 3, 'right')}


def fig_risk_return(start='2015-01-02'):
    names = CROSS + ['Ethereum', 'EUR/USD', 'EUR/RON']
    cols = CROSS_COL + [Purple, Crimson, IDAred]
    rows = []
    panel = cross_panel()
    for n in names:
        s = (eurron if n == 'EUR/RON' else panel[n]).loc[start:].dropna()
        cagr, v = ann_stats(s, 'obs')          # q = observed number of trading days per year
        rows.append((n, cagr, v, s.index[0]))
    res = pd.DataFrame(rows, columns=['asset', 'cagr', 'vol', 'from']).set_index('asset')
    fig, ax = plt.subplots(figsize=(4.7, 3.1))
    for (n, r), c in zip(res.iterrows(), cols):
        ax.scatter(r['vol'], r['cagr'], s=40, color=c, zorder=3)
        late = r['from'] > pd.Timestamp(start) + pd.Timedelta(days=30)
        lab = f"{n} (from {r['from']:%b %Y})" if late else n
        dx, dy, ha = OFFSETS.get(n, (5, 3, 'left'))
        ax.annotate(lab, (r['vol'], r['cagr']), xytext=(dx, dy), textcoords='offset points',
                    fontsize=7.5, ha=ha)
    ax.set_xscale('log')
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.4, 0.8])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylim(-0.08, None)
    ax.set_xlabel('Annualised volatility (log scale)')
    ax.set_ylabel('Annualised return (CAGR)')
    ax.set_title('Risk and return, 2015-2026', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_risk_return')
    return res


# =============================================================================
# FIG 3: S&P 500 si drawdown-urile majore
# =============================================================================
EPISODES = [('Dot-com', '2000-01-01', '2003-12-31'),
            ('Global Financial Crisis', '2007-06-01', '2010-12-31'),
            ('COVID-19', '2020-01-01', '2020-12-31'),
            ('2022 inflation shock', '2022-01-01', '2023-12-31')]


def fig_sp500_drawdowns():
    s = px['S&P 500'].dropna()
    dd = drawdown(s)
    fig, axes = plt.subplots(2, 1, figsize=(4.7, 3.3), sharex=True, gridspec_kw={'height_ratios': [1.1, 1]})
    axes[0].plot(s.index, s.values, color=MainBlue, lw=0.8)
    pk, rc = pd.Timestamp('2007-10-09'), s.loc['2009-03-10':][s.loc['2009-03-10':] >= s.loc['2007-10-09']].index[0]
    axes[0].plot([pk, rc], [s[pk], s[pk]], color=Amber, lw=2.2, solid_capstyle='butt')
    axes[0].annotate(f'{(rc - pk).days / 365.25:.1f} years to regain\nthe Oct 2007 peak', (rc, s[pk]), xytext=(4, -3),
                     textcoords='offset points', fontsize=7, va='top', color='black')
    log_axis(axes[0], [1000, 2000, 4000, 8000])
    axes[0].set_ylabel('S&P 500 (log)')
    axes[1].fill_between(dd.index, dd.values, 0, color=IDAred, alpha=0.35, lw=0)
    axes[1].plot(dd.index, dd.values, color=IDAred, lw=0.5)
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
    axes[1].set_ylabel('Drawdown')
    res = {}
    for name, a, b in EPISODES:
        seg = dd.loc[a:b]
        t, v = seg.idxmin(), seg.min()
        res[name] = (t.date(), v)
        dx, ha = {'COVID-19': (-4, 'right'), '2022 inflation shock': (6, 'left')}.get(name, (0, 'center'))
        axes[1].annotate(f'{name}\n{v:.0%}', (t, v), xytext=(dx, -2), textcoords='offset points',
                         ha=ha, va='top', fontsize=7)
    axes[1].set_ylim(dd.min() * 1.45, 0.02)
    axes[0].set_title('S&P 500, 2000-2026: level (log) and drawdown', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_sp500_drawdowns')
    return res


# =============================================================================
# FIG 4: VIX -- regimuri de volatilitate
# =============================================================================
def fig_vix_regimes():
    v = px['VIX'].dropna()
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.plot(v.index, v.values, color=MainBlue, lw=0.5)
    ax.axhline(20, color=Amber, ls='--', lw=0.8)
    ax.axhline(30, color=IDAred, ls='--', lw=0.8)
    ax.text(1.005, 20 / (v.max() * 1.18), 'VIX = 20', fontsize=7, color=Amber, transform=ax.transAxes, va='center')
    ax.text(1.005, 30 / (v.max() * 1.18), 'VIX = 30', fontsize=7, color=IDAred, transform=ax.transAxes, va='center')
    # largest peaks, at least 2 years apart
    peaks = []
    for t in v.sort_values(ascending=False).index:
        if all(abs((t - p).days) > 730 for p in peaks):
            peaks.append(t)
        if len(peaks) == 5:
            break
    for t in peaks:
        ax.annotate(f'{t:%b %Y}\n{v.loc[t]:.0f}', (t, v.loc[t]), xytext=(0, 4), textcoords='offset points',
                    ha='center', fontsize=7)
    ax.set_ylim(0, v.max() * 1.18)
    ax.set_ylabel('VIX (implied volatility, %)')
    share = {'<20': (v < 20).mean(), '20-30': ((v >= 20) & (v < 30)).mean(), '>=30': (v >= 30).mean()}
    ax.set_title(f'VIX 2000-2026: calm most of the time (<20 on {share["<20"]:.0%} of days), '
                 f'with short violent spikes', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_vix_regimes')
    return {t.date(): round(v.loc[t], 2) for t in peaks}, share


# =============================================================================
# FIG 4b: VIX vs volatilitatea realizata ulterior (prima de risc de varianta)
# =============================================================================
def fig_vix_vrp(h=21):
    """VIX (implied, % a year) vs the realised volatility of the S&P 500 over the next h = 21 trading days:
    sqrt(252/h * sum r^2), without the incomplete windows at the end; bottom: implied minus realised variance."""
    v = px['VIX'].dropna(); s = px['S&P 500'].dropna()
    r = np.log(s).diff()
    rv = np.sqrt((r ** 2)[::-1].rolling(h).sum()[::-1].shift(-1) * 252 / h) * 100
    j = pd.concat([v, rv], axis=1, keys=['vix', 'rv']).dropna()
    gap = (j['vix'] / 100) ** 2 - (j['rv'] / 100) ** 2
    fig, axes = plt.subplots(2, 1, figsize=(4.7, 3.3), sharex=True, gridspec_kw={'height_ratios': [1.2, 1]})
    axes[0].plot(j.index, j['rv'], color=Orange, lw=0.5, label='Realised volatility, next 21 trading days')
    axes[0].plot(j.index, j['vix'], color=MainBlue, lw=0.5, label='VIX (implied, next 30 calendar days)')
    axes[0].set_ylabel('% per year'); axes[0].set_ylim(0, 110)
    axes[1].fill_between(gap.index, gap.values, 0, where=gap >= 0, color=Forest, alpha=0.6, lw=0,
                         label='Implied > realised variance')
    axes[1].fill_between(gap.index, gap.values, 0, where=gap < 0, color=IDAred, alpha=0.6, lw=0,
                         label='Implied < realised variance')
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_ylabel('Variance gap'); axes[1].set_ylim(-0.5, 0.2)
    axes[0].set_title('VIX vs subsequent realised volatility, S&P 500', fontsize=9, loc='left')
    bottom_legend(fig, ncol=2, fontsize=7.2)
    save_fig('ch0_vix_vrp')
    return dict(n=len(j), first=j.index[0].date(), last=j.index[-1].date(), mean_vix=j['vix'].mean(),
                mean_rv=j['rv'].mean(), share_vix_above=(j['vix'] > j['rv']).mean(), mean_gap=gap.mean(),
                share_gap_pos=(gap > 0).mean())


# =============================================================================
# FIG 5: Dobanzi SUA si inversarea curbei (10y - 2y)
# =============================================================================
def fig_rates():
    d = fred[['DGS10', 'DGS2']].dropna()
    ff = fred['FEDFUNDS'].dropna()
    spread = d['DGS10'] - d['DGS2']
    fig, axes = plt.subplots(2, 1, figsize=(4.7, 3.3), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    axes[0].plot(ff.index, ff.values, color=Teal, lw=0.9, label='Fed funds (monthly)')
    axes[0].plot(d.index, d['DGS2'], color=Amber, lw=0.7, label='2-year Treasury')
    axes[0].plot(d.index, d['DGS10'], color=MainBlue, lw=0.7, label='10-year Treasury')
    axes[0].set_ylabel('Yield (%)')
    axes[1].plot(spread.index, spread.values, color=MainBlue, lw=0.6)
    axes[1].fill_between(spread.index, spread.values, 0, where=spread < 0, color=IDAred, alpha=0.45, lw=0)
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_ylabel('10y - 2y (pp)')
    inv = spread.loc['2022':'2024']
    axes[0].set_title('US rates and the 10y - 2y spread (red = inverted)', fontsize=9, loc='left')
    bottom_legend(fig, ncol=3, fontsize=7.5)
    save_fig('ch0_rates')
    runs = (spread < 0).astype(int)
    neg = inv < 0                                   # consecutive spells of negative spread, 2022-2024
    spell_id = (neg != neg.shift()).cumsum()
    spells = [(g.index[0].date(), g.index[-1].date(), len(g)) for _, g in inv[neg].groupby(spell_id[neg])]
    longest = max(spells, key=lambda t: t[2])
    return dict(min_spread=round(spread.min(), 2), min_date=spread.idxmin().date(),
                inversion_spells_2022_24=spells, longest_inversion=longest,
                negative_days_2022_24=int(neg.sum()),
                last_10y=round(d['DGS10'].iloc[-1], 2), last_2y=round(d['DGS2'].iloc[-1], 2),
                last_date=d.index[-1].date(), last_ff=round(ff.iloc[-1], 2), share_inverted=runs.mean())


# =============================================================================
# FIG 6: Concentrarea pietei: ponderat dupa capitalizare vs ponderi egale
# =============================================================================
def fig_concentration():
    p = px[['SPY', 'RSP']].dropna()
    ratio = (p['SPY'] / p['SPY'].iloc[0]) / (p['RSP'] / p['RSP'].iloc[0])
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.2), gridspec_kw={'width_ratios': [1.25, 1]})
    for col, c, lab in [('SPY', MainBlue, 'SPY (cap-weighted)'), ('RSP', Amber, 'RSP (equal-weighted)')]:
        g = p[col] / p[col].iloc[0]
        axes[0].plot(g.index, g.values, color=c, lw=0.8, label=f'{lab}: x{g.iloc[-1]:.1f}')
    log_axis(axes[0], [0.5, 1, 2, 4, 8])
    axes[0].set_ylabel('Growth of 1 USD (log)')
    axes[1].plot(ratio.index, ratio.values, color=IDAred, lw=0.8, label='SPY / RSP (both rebased to 1 in Apr 2003)')
    axes[1].axhline(1, color=Gray, lw=0.5, ls=':')
    axes[1].set_title('SPY / RSP relative performance', fontsize=8.5, loc='left')
    axes[0].set_title(f'S&P 500 ETFs, {p.index[0]:%b %Y}-2026 (total return)', fontsize=8.5, loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch0_concentration')
    since23 = ratio.loc['2023-01-03':]
    return dict(start=p.index[0].date(), spy=(p['SPY'].iloc[-1] / p['SPY'].iloc[0]),
                rsp=(p['RSP'].iloc[-1] / p['RSP'].iloc[0]), ratio_min=round(ratio.min(), 3),
                ratio_min_date=ratio.idxmin().date(), ratio_last=round(ratio.iloc[-1], 3),
                ratio_change_since_2023=since23.iloc[-1] / since23.iloc[0] - 1)


# =============================================================================
# FIG 7: Corelatii rulante: actiuni-obligatiuni si Bitcoin-actiuni
# =============================================================================
def fig_rolling_correlations(window=252):
    eq = np.log(px['S&P 500'].dropna()).diff()              # dropna before diff: own calendar
    bd = np.log(px['US Treasuries 20y+ (TLT)'].dropna()).diff()
    btc = np.log(px['Bitcoin'].dropna()).diff()
    both = pd.concat([eq, bd], axis=1).dropna()
    c_sb = both.iloc[:, 0].rolling(window).corr(both.iloc[:, 1])
    # several series: join the PRICES on common days, then diff -> both returns cover
    # the same interval (e.g. Friday -> Monday); diff before the join would give Bitcoin Sunday -> Monday
    pp = pd.concat([px['S&P 500'], px['Bitcoin']], axis=1).dropna()
    trio = np.log(pp).diff().dropna()
    c_be = trio.iloc[:, 0].rolling(window).corr(trio.iloc[:, 1])
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.plot(c_sb.index, c_sb.values, color=MainBlue, lw=0.9, label='S&P 500 vs long Treasuries (TLT)')
    ax.plot(c_be.index, c_be.values, color=Orange, lw=0.9, label='S&P 500 vs Bitcoin')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylim(-0.8, 0.8)
    ax.set_ylabel('1-year rolling correlation')
    ax.set_title('Diversification is not constant: rolling correlations of daily log returns',
                 fontsize=9, loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch0_rolling_correlations')
    return dict(sb_2010_2020=c_sb.loc['2010':'2020'].mean(), sb_2022_2026=c_sb.loc['2022':].mean(),
                sb_last=c_sb.dropna().iloc[-1], be_2016_2019=c_be.loc['2016':'2019'].mean(),
                be_2022_2026=c_be.loc['2022':].mean(), be_last=c_be.dropna().iloc[-1])


# =============================================================================
# FIG 8: Volatilitate rulanta: Bitcoin vs S&P 500
# =============================================================================
def fig_rolling_vol(window=63):
    eq = np.log(px['S&P 500'].dropna()).diff()
    btc = np.log(px['Bitcoin'].dropna()).diff()
    v_eq = eq.rolling(window).std() * np.sqrt(252)
    v_btc = btc.rolling(window).std() * np.sqrt(365)
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.plot(v_btc.index, v_btc.values, color=Orange, lw=0.8, label='Bitcoin (365 days/year)')
    ax.plot(v_eq.loc['2014-09':].index, v_eq.loc['2014-09':].values, color=MainBlue, lw=0.8,
            label='S&P 500 (252 days/year)')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
    ax.set_ylabel('Volatility (63 obs.)')
    ratio = (v_btc.loc['2024':].mean() / v_eq.loc['2024':].mean())
    ax.set_title(f'Rolling volatility: Bitcoin is still about {ratio:.1f} times as volatile as the S&P 500 '
                 f'(2024-2026)', fontsize=9, loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch0_rolling_vol')
    return dict(btc_2015_17=v_btc.loc['2015':'2017'].mean(), btc_2024_26=v_btc.loc['2024':].mean(),
                eq_2024_26=v_eq.loc['2024':].mean(), ratio=ratio)


# =============================================================================
# FIG 9: Oferta de stablecoins (DefiLlama)
# =============================================================================
def fig_stablecoins():
    s = stable[stable > 0].loc['2018':]
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.fill_between(s.index, s.values, 0, color=Forest, alpha=0.25, lw=0)
    ax.plot(s.index, s.values, color=Forest, lw=0.9)
    ax.set_ylabel('bn USD')
    pts = {}
    peak = s.loc['2022'].idxmax()                         # 2022 peak
    trough = s.loc[peak:'2023-12-31'].idxmin()            # exact trough after the peak
    for tt in [s.loc['2020-01-01':].index[0], peak, trough, s.index[-1]]:
        pts[tt.date()] = s.loc[tt]
        ax.annotate(f'{s.loc[tt]:.1f} bn\n{tt:%d %b %Y}', (tt, s.loc[tt]), xytext=(0, 6),
                    textcoords='offset points', ha='center', fontsize=7)
    ax.set_ylim(0, s.max() * 1.25)
    ax.set_title('Total supply of USD-pegged stablecoins, 2018-2026 (source: DefiLlama)',
                 fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_stablecoins')
    return pts


# =============================================================================
# FIG 9b: Tether (USDT): abaterea fata de paritatea de 1 USD
# =============================================================================
def fig_usdt_peg():
    """USDT price (close) 2019-2026, deviation from 1 USD in %, bands of +-0.5% and +-1%, March 2020 detail."""
    u = load('Tether (USDT)', start='2019-01-01').dropna()
    dev = 100 * (u - 1)
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.plot(dev.index, dev.values, color=Forest, lw=0.6, label='USDT price minus 1 USD (%)')
    for b, c, lab in [(0.5, Amber, 'Band of 0.5%'), (1.0, IDAred, 'Band of 1%')]:
        ax.axhline(b, color=c, ls='--', lw=0.8, label=lab)
        ax.axhline(-b, color=c, ls='--', lw=0.8)
    ax.set_ylabel('Deviation (%)'); ax.set_ylim(-3.2, 6.0)
    for t in [dev.idxmin(), dev.idxmax()]:
        ax.annotate(f'{u[t]:.3f} USD\n{t:%d %b %Y}', (t, dev[t]), xytext=(14, 0), textcoords='offset points',
                    fontsize=7, va='center', color='black')
    ins = ax.inset_axes([0.62, 0.52, 0.34, 0.42])
    m = dev.loc['2020-02-24':'2020-04-10']
    ins.plot(m.index, m.values, color=Forest, lw=0.9)
    for b, c in [(0.5, Amber), (1.0, IDAred)]:
        ins.axhline(b, color=c, ls='--', lw=0.6); ins.axhline(-b, color=c, ls='--', lw=0.6)
    ins.set_title('March 2020', fontsize=7, loc='left', pad=2)
    ins.tick_params(labelsize=6); ins.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ins.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 15]))
    ax.set_title('Tether (USDT), 2019-2026: distance from the 1 USD peg', fontsize=9, loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch0_usdt_peg')
    return dict(n=len(u), first=u.index[0].date(), last=u.index[-1].date(), within05=(dev.abs() <= 0.5).mean(),
                within1=(dev.abs() <= 1.0).mean(), min=(u.idxmin().date(), u.min()), max=(u.idxmax().date(), u.max()))


# =============================================================================
# FIG 10: ETF-ul spot Bitcoin IBIT: valoarea tranzactionata
# =============================================================================
def fig_ibit():
    d = pd.concat([px['IBIT'], ibit_volume, px['Bitcoin']], axis=1, keys=['p', 'v', 'btc']).dropna()
    dv = (d['p'] * d['v'] / 1e9)
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.bar(dv.index, dv.values, width=1.0, color=MainBlue, alpha=0.35, label='IBIT daily traded value')
    ax.plot(dv.rolling(20).mean().index, dv.rolling(20).mean().values, color=MainBlue, lw=1.0,
            label='20-day average')
    ax.set_ylabel('Traded value (bn USD)')
    ax2 = ax.twinx()
    ax2.plot(d.index, d['btc'] / 1e3, color=Orange, lw=0.9, label='Bitcoin price (k USD, right)')
    ax2.set_ylabel('BTC (thousand USD)', color=Orange)
    ax2.spines['right'].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.set_title('iShares Bitcoin Trust (IBIT) since launch on 11 Jan 2024: price x volume',
                 fontsize=9, loc='left')
    bottom_legend(fig, ncol=3, handles=h1 + h2, labels=l1 + l2)
    save_fig('ch0_ibit')
    return dict(first=d.index[0].date(), mean_bn=dv.mean(), median_bn=dv.median(), max_bn=dv.max(),
                max_date=dv.idxmax().date(), total_bn=dv.sum())


# =============================================================================
# FIG 11: Piata romaneasca: BET, blue chips BVB, EUR/RON
# =============================================================================
def fig_romania():
    """BET-TR and BVB blue chips (dividend-adjusted), EUR/RON (BNR), 10-year yields Romania vs Germany."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), gridspec_kw={'width_ratios': [1.35, 0.9, 0.9]})
    start = '2015-01-05'
    out = {}
    b = px['BET-TR'].loc[start:].dropna()
    axes[0].plot(b.index, b / b.iloc[0], color='black', lw=1.1, label=f'BET-TR x{b.iloc[-1] / b.iloc[0]:.1f}')
    out['BET-TR'] = b.iloc[-1] / b.iloc[0]
    for n, c in zip(['Banca Transilvania', 'OMV Petrom', 'BRD', 'Transgaz', 'Romgaz'],
                    [MainBlue, Amber, Forest, Purple, Orange]):
        s_ = bvb[n].loc[start:].dropna()
        g = s_ / s_.iloc[0]
        out[n] = g.iloc[-1]
        axes[0].plot(g.index, g.values, color=c, lw=0.6, label=f'{n.split()[0]} x{g.iloc[-1]:.1f}')
    log_axis(axes[0], [0.5, 1, 2, 4, 8, 16])
    axes[0].set_ylabel('Growth of 1 RON (log)')
    axes[0].set_title('BET-TR and blue chips since 2015', fontsize=8, loc='left')
    axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=6, frameon=False)
    fx = eurron.loc['2005-07-01':]
    axes[1].plot(fx.index, fx.values, color=IDAred, lw=0.7)
    axes[1].set_title('EUR/RON (BNR)', fontsize=8, loc='left')
    y = pd.concat([clean_series(bonds[c].dropna()) for c in bonds], axis=1).dropna()
    axes[2].plot(y.index, y['Romania 10y'], color=MainBlue, lw=0.7, label='Romania (bonds in RON)')
    axes[2].plot(y.index, y['Germany 10y'], color=IDAred, lw=0.7, label='Germany (bonds in EUR)')
    axes[2].set_title('10-year yields (%)', fontsize=8, loc='left')
    axes[2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=6, frameon=False)
    for ax in axes:
        ax.tick_params(axis='x', labelsize=7)
        ax.xaxis.set_major_locator(mdates.YearLocator(4 if ax is axes[0] else 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.tight_layout()
    save_fig('ch0_romania')
    r_fx = np.log(fx).diff().dropna()
    spread = (y['Romania 10y'] - y['Germany 10y'])
    return dict(growth=out, bettr_first=b.index[0].date(), eurron_first=fx.iloc[0], eurron_first_date=fx.index[0].date(),
                eurron_last=fx.iloc[-1], eurron_last_date=fx.index[-1].date(),
                eurron_vol_2015_26=ann_stats(fx.loc['2015':], 'obs')[1],
                ro10y_last=y['Romania 10y'].iloc[-1], de10y_last=y['Germany 10y'].iloc[-1],
                spread_last=spread.iloc[-1], spread_max=spread.max(), spread_max_date=spread.idxmax().date(),
                bonds_first=y.index[0].date(), h2o_first=bvb['Hidroelectrica'].first_valid_index().date())


def fig_romania_split():
    """The three Romanian panels as separate full-width figures: equities, EUR/RON, 10-year yields."""
    start = '2015-01-05'
    # 1. BET-TR and blue chips, growth of 1 RON (dividend-adjusted), log scale
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    b = px['BET-TR'].loc[start:].dropna()
    ax.plot(b.index, b / b.iloc[0], color='black', lw=1.5, label=f'BET-TR x{b.iloc[-1] / b.iloc[0]:.1f}')
    for n, c in zip(['Banca Transilvania', 'OMV Petrom', 'BRD', 'Transgaz', 'Romgaz'],
                    [MainBlue, Amber, Forest, Purple, Orange]):
        g = bvb[n].loc[start:].dropna()
        g = g / g.iloc[0]
        ax.plot(g.index, g.values, color=c, lw=0.9, label=f'{n} x{g.iloc[-1]:.1f}')
    log_axis(ax, [0.5, 1, 2, 4, 8, 16])
    ax.set_ylabel('Growth of 1 RON (log scale)')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    bottom_legend(fig, ncol=3)
    save_fig('ch0_romania_equities')
    # 2. EUR/RON, BNR reference rate
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    fx = eurron.loc['2005-07-01':]
    ax.plot(fx.index, fx.values, color=IDAred, lw=1.0, label='EUR/RON, BNR reference rate (RON per EUR)')
    ax.set_ylabel('RON per EUR')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    bottom_legend(fig, ncol=1)
    save_fig('ch0_eurron')
    # 3. 10-year government yields, Romania (RON) vs Germany (EUR)
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    y = pd.concat([clean_series(bonds[c].dropna()) for c in bonds], axis=1).dropna()
    ax.plot(y.index, y['Romania 10y'], color=MainBlue, lw=1.0, label='Romania 10-year (bonds in RON)')
    ax.plot(y.index, y['Germany 10y'], color=IDAred, lw=1.0, label='Germany 10-year (bonds in EUR)')
    ax.axhline(0, color='black', lw=0.5)
    ax.set_ylabel('Yield (%)')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    bottom_legend(fig, ncol=2)
    save_fig('ch0_ro_yields')
    return dict(bettr=b.iloc[-1] / b.iloc[0], eurron_first=fx.iloc[0], eurron_last=fx.iloc[-1],
                ro10y_last=y['Romania 10y'].iloc[-1], de10y_last=y['Germany 10y'].iloc[-1])


def fig_bad_ticks():
    """EUR/RON: EODHD series (bad ticks) vs the BNR rate, 2015-2026, with annualised volatilities."""
    mk = eurron_mkt.loc['2015':]; bn = eurron.loc['2015':]
    res = data_pitfall()
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    ax.plot(mk.index, mk.values, color=IDAred, lw=0.6,
            label=f"EODHD EUR/RON series: volatility {res['vol_market']:.1%}")
    ax.plot(bn.index, bn.values, color=MainBlue, lw=0.9, label=f"BNR reference rate: volatility {res['vol_bnr']:.1%}")
    for d, dy in [('2025-08-13', 0), ('2022-01-05', 0)]:
        t = pd.Timestamp(d)
        ax.annotate(f'{t:%d %b %Y}: {mk[t]:.2f}', (t, mk[t]), xytext=(-8, 0), textcoords='offset points', ha='right',
                    va='center', fontsize=7, color='black')
    ax.set_ylabel('RON per EUR'); ax.set_ylim(4.2, 6.05)
    ax.set_title('EUR/RON 2015-2026 from two sources', fontsize=9, loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch0_bad_ticks')
    return res


def data_pitfall():
    """EUR/RON: EODHD series (with bad ticks) vs BNR, 2015-2026."""
    r_e = np.log(eurron_mkt).diff().dropna().loc['2015':]
    r_b = np.log(eurron).diff().dropna().loc['2015':]
    top = r_e.abs().sort_values(ascending=False).head(6)
    q = lambda r: len(r) / ((r.index[-1] - r.index[0]).days / 365.25)   # observed frequency (FX: not 252)
    return dict(vol_market=r_e.std() * np.sqrt(q(r_e)), vol_bnr=r_b.std() * np.sqrt(q(r_b)),
                largest={d.date(): round(r_e.loc[d], 4) for d in top.index})



# =============================================================================
# FIG: Istoria BVB - BET 1997-2011, BET-XT din 2011, BET-TR din 2014 (scara log)
# =============================================================================
def fig_bvb_history():
    """BET index 1997-2026 on a log scale, official closing values, with events marked."""
    bet = load('BET', start='1997-01-01').dropna()
    full = bet
    fig, ax = plt.subplots(figsize=(6.8, 2.45))
    ax.plot(bet.index, bet.values, color=MainBlue, lw=0.8, label='BET, official closing values (base 1,000 on 19 Sep 1997)')
    ax.set_yscale('log')
    ax.set_ylabel('Index level (log scale)')
    events = [('1999-04-21', 'Apr 1999\nlow', 0, 18), ('2007-07-24', 'Jul 2007\npeak', 0, 14),
              ('2009-02-25', 'Feb 2009\ntrough', 0, -26), ('2018-12-18', 'Dec 2018\nbank-tax\nannouncement', -34, -16),
              ('2020-03-16', 'Mar 2020\nCOVID-19', 16, -16), ('2023-07-12', 'Jul 2023\nHidroelectrica\nIPO', 0, -16)]
    for d, lab, dx, dy in events:
        t = full.index[full.index.searchsorted(pd.Timestamp(d))]
        ax.plot(t, full.loc[t], 'o', ms=3.5, color=IDAred)
        ax.annotate(lab, xy=(t, full.loc[t]), xytext=(dx, dy), textcoords='offset points', ha='center',
                    va='bottom' if dy > 0 else 'top', fontsize=6.5, color='black',
                    arrowprops=dict(arrowstyle='-', color=LightGray, lw=0.5))
    ax.set_ylim(150, 5e4)
    ax.set_title('The BET index, 1997-2026', fontsize=9, loc='left')
    bottom_legend(fig, ncol=1)
    save_fig('ch0_bvb_history')
    lvl = lambda s, d: s.loc[s.index[s.index.searchsorted(pd.Timestamp(d))]]
    return dict(bet_first=(bet.index[0].date(), bet.iloc[0]),                 bet_1999_min=(bet.loc['1999'].idxmin().date(), bet.loc['1999'].min()),
                bet_2007_max=(bet.loc[:'2008'].idxmax().date(), bet.loc[:'2008'].max()),
                bet_2009_min=(bet.loc['2008-06':'2009-12'].idxmin().date(), bet.loc['2008-06':'2009-12'].min()),
                dec2018=(lvl(bet, '2018-12-18'), lvl(bet, '2018-12-19'), lvl(bet, '2018-12-19') / lvl(bet, '2018-12-18') - 1),
                bet_last=(bet.index[-1].date(), bet.iloc[-1]), bet_max=(bet.idxmax().date(), bet.max()),
                multiple_1997_2026=bet.iloc[-1] / bet.iloc[0])

# =============================================================================
# STUDIU DE CAZ: Haddad, Huebner si Loualiche (2025), "How Competitive Is the Stock Market?"
# =============================================================================
HHL = dict(active0=0.81, chi=2.97, pass_through=0.33)   # Sectiunea V.A; Tabelul 2, randul 1; ec. (28)


def fig_hhl_elasticity():
    """Eq. (5): aggregate elasticity after a fraction 1 - alpha of investors turns passive,
    relative to the market without passive investors: alpha (1 + chi) / (1 + chi alpha)."""
    alpha = np.linspace(0, 1, 401)
    rel = lambda chi: alpha * (1 + chi) / (1 + chi * alpha)
    fig, ax = plt.subplots(figsize=(4.7, 3.0))
    passive = 100 * (1 - alpha)
    for chi, c, lab in [(0, IDAred, '$\\chi = 0$: no strategic response (Koijen and Yogo)'),
                        (HHL['chi'], MainBlue, '$\\chi = 2.97$: estimate (Table 2, row 1)'),
                        (10, Forest, '$\\chi = 10$: strong response')]:
        ax.plot(passive, rel(chi), color=c, lw=1.3, label=lab)
    ax.axvline(30, color=Gray, lw=0.5, ls=':')
    for chi, c, dy in [(0, IDAred, -5), (HHL['chi'], MainBlue, -5), (10, Forest, 5)]:
        v = 0.70 * (1 + chi) / (1 + chi * 0.70)
        ax.plot(30, v, 'o', ms=4, color=c)
        ax.annotate(f'{v:.2f}', xy=(30, v), xytext=(-6, dy), textcoords='offset points', ha='right',
                    va='top' if dy < 0 else 'bottom', fontsize=7.5, color='black')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.1)
    ax.set_xlabel('Share of investors turned passive, $1 - \\alpha$ (%)')
    ax.set_ylabel('$\\mathcal{E}_{agg}$ relative to all active')
    ax.set_title('Aggregate elasticity when investors turn passive, eq. (5)', fontsize=9, loc='left')
    bottom_legend(fig, ncol=1)
    save_fig('ch0_hhl_elasticity')
    return {chi: round(0.70 * (1 + chi) / (1 + chi * 0.70), 3) for chi in (0, HHL['chi'], 10)}


# =============================================================================
# ISTORIE: burse, crize si modele financiare (cronologii, fara date de piata)
# =============================================================================
def _timeline(ax, rows, x0, x1, levels=(0.22, -0.22, 0.40, -0.40), fs=6.3):
    """rows: list of (label, colour, [(year, text, level_index[, dx]), ...]); one horizontal lane per row."""
    for r, (lab, col, events) in enumerate(rows):
        y = -r
        ax.plot([x0, x1], [y, y], color=col, lw=0.6, alpha=0.5, zorder=1)
        ax.plot([], [], 'o', color=col, ms=5, label=lab)
        for ev in events:
            if len(ev) == 4 and isinstance(ev[1], (int, float)):   # interval (start, end, text, level)
                a, b, txt, lv = ev
                ax.plot([a, b], [y, y], color=col, lw=4, solid_capstyle='butt', zorder=2)
                xm = (a + b) / 2
            else:
                xm, txt, lv = ev[:3]
                ax.plot(xm, y, 'o', color=col, ms=4.5, zorder=3)
            dx = ev[3] if len(ev) == 4 and not isinstance(ev[1], (int, float)) else 0
            dy = levels[lv]
            ax.annotate(txt, xy=(xm, y), xytext=(xm + dx, y + dy), ha='center', va='bottom' if dy > 0 else 'top',
                        fontsize=fs, color='black', arrowprops=dict(arrowstyle='-', color=col, lw=0.5))
    ax.set_xlim(x0, x1)
    ax.set_ylim(-len(rows) + 0.4, 0.62)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)


def _timeline_auto(axes, rows, spans, fs=6.4, levels=(0.03, 0.52), reserved=()):
    """Lanes drawn across several axes (spans: one (x0, x1) per axes, e.g. a compressed early period and an
    expanded recent one); every label above its point, at the first free slot among two heights and a few
    horizontal shifts, checked against all the labels already placed (measured with the renderer)."""
    fig = axes[0].figure
    for ax, (x0, x1) in zip(axes, spans):
        ax.set_xlim(x0, x1)
        ax.set_ylim(-len(rows) + 0.7, 0.85)
        for sp in ('left', 'right', 'top'):
            ax.spines[sp].set_visible(False)
    renderer = fig.canvas.get_renderer()
    placed = list(reserved)
    for r, (lab, col, events) in enumerate(rows):
        y = -r
        for ax, (x0, x1) in zip(axes, spans):
            ax.plot([x0, x1], [y, y], color=col, lw=0.6, alpha=0.5, zorder=1)
        for ev in events:
            xm, txt = ev[0], ev[1]
            k = next(i for i, (x0, x1) in enumerate(spans) if x0 <= xm <= x1)
            ax = axes[k]
            x0, x1 = spans[k]
            step = 5.0 / (ax.get_window_extent(renderer).width * 72 / fig.dpi) * (x1 - x0)   # 5 pt
            ax.plot(xm, y, 'o', color=col, ms=3.5, zorder=3)
            best, cands = None, []
            for j in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8):
                for lv in levels:
                    t = ax.text(xm + j * step, y + lv, txt, ha='center', va='bottom', fontsize=fs)
                    bb = t.get_window_extent(renderer).expanded(1.08, 1.05)
                    t.remove()
                    out = max(0, fig.bbox.x0 - bb.x0) + max(0, bb.x1 - fig.bbox.x1)
                    ov = sum(max(0, min(bb.x1, p.x1) - max(bb.x0, p.x0)) * max(0, min(bb.y1, p.y1) - max(bb.y0, p.y0))
                             for p in placed)
                    cands.append((ov + 1e3 * out, abs(j), j * step, lv, bb))
                    if ov == 0 and out == 0:
                        best = (j * step, lv, bb)
                        break
                if best:
                    break
            if best is None:
                c = min(cands, key=lambda c: (c[0], c[1]))
                best = (c[2], c[3], c[4])
            dx, lv, bb = best
            ax.annotate(txt, xy=(xm, y), xytext=(xm + dx, y + lv), ha='center', va='bottom', fontsize=fs,
                        color='black', arrowprops=dict(arrowstyle='-', color=col, lw=0.5))
            if bb is not None:
                placed.append(bb)

def fig_market_history():
    """Exchanges (top lane) and bubbles/crashes (bottom lane), 1250-2026."""
    ex = [(1270, 1500, 'Bruges, Ter Beurze\n(13th-15th c.)', 0), (1531, 'Antwerp\n1531', 1), (1602, 'VOC shares\n1602', 0),
          (1698, "London,\nJonathan's\n1698", 2, -14), (1773, 'London\n"Stock Exchange"\n1773', 0),
          (1792, 'Buttonwood\n1792', 1), (1882, 'Bucharest\n1882', 0)]
    cr = [(1637, 'Tulips\n1637', 1), (1720, 'Mississippi,\nSouth Sea\n1720', 0), (1792, 'Panic\n1792', 1),
          (1873, '1873', 0), (1929, '1929', 1), (1987, '1987', 0), (2008, '2008', 1), (2020, '2020', 2)]
    rows = [('Exchanges and traded securities', MainBlue, ex), ('Bubbles, panics and crashes', IDAred, cr)]
    fig, ax = plt.subplots(figsize=(5.5, 2.2))
    _timeline(ax, rows, 1250, 2035, levels=(0.18, -0.18, 0.42, -0.42), fs=7)
    ax.set_ylim(-1.6, 0.85)
    ax.set_xticks(range(1300, 2001, 100))
    bottom_legend(fig, ncol=2)
    save_fig('ch0_market_history')


def fig_model_history():
    """Milestones of financial modelling, 1900-2026, one lane per family."""
    rows = [
        ('Random walk and efficiency', MainBlue,
         [(1900, 'Bachelier', 0), (1963, 'Mandelbrot', 1, -3), (1965, 'Samuelson', 0), (1970, 'Fama', 1, 2)]),
        ('Portfolio and equilibrium', Forest,
         [(1952, 'Markowitz', 0), (1958, 'Tobin', 1), (1964, 'CAPM', 0), (1976, 'APT', 1), (1993, 'Fama-French', 0)]),
        ('Derivatives, continuous time', Purple,
         [(1973, 'Black-Scholes-Merton', 0, -5), (1977, 'Vasicek', 1), (1985, 'CIR', 0), (1992, 'HJM', 1),
          (1993, 'Heston', 2), (2018, 'rough vol.', 0)]),
        ('Volatility and risk', IDAred,
         [(1982, 'ARCH', 0, -3), (1986, 'GARCH', 1, -2), (1994, 'RiskMetrics', 0, -2), (1999, 'coherent', 1, -4),
          (2000, 'copula', 2, 2), (2003, 'realised vol.', 3, 4), (2019, 'FRTB: ES', 1, 4)]),
        ('Machine learning', Orange,
         [(1994, 'neural nets', 0), (2019, 'deep hedging', 1, -3), (2020, 'ML asset pricing', 0, 2)]),
        ('Generative AI', Amber,
         [(2017, 'Transformer', 0, -4), (2023, 'BloombergGPT', 1), (2024, 'Chronos', 0, 3)]),
        ('Quantum computing', Teal,
         [(2015, 'quantum MC', 1, -8), (2018, 'option pricing', 0), (2021, 'advantage threshold', 3, 3)]),
    ]
    # drawn at the size it has on the slide (5.67 x 2.0 in) with a compressed axis before 1985 and an expanded
    # one after, so that the labels can be placed without overlaps
    fig, axes = plt.subplots(1, 2, figsize=(5.47, 1.93), gridspec_kw={'width_ratios': [1, 1.75], 'wspace': 0.03})
    fig._sf_manual = True
    fig.subplots_adjust(left=0.235, right=0.985, top=0.99, bottom=0.11)
    for ax in axes:
        ax.tick_params(axis='x', labelsize=6.6)
    # the family names on the left first, so that no label is placed over them
    axes[0].set_yticks([-r for r in range(len(rows))])
    axes[0].set_yticklabels([lab for lab, _, _ in rows], fontsize=6.8)
    fig.canvas.draw()
    names = [t.get_window_extent(fig.canvas.get_renderer()) for t in axes[0].get_yticklabels()]
    axes[1].set_yticks([])
    _timeline_auto(axes, rows, [(1895, 1985), (1985, 2036)], fs=6.4, reserved=names)
    axes[0].set_xticks([1900, 1920, 1940, 1960, 1980])
    axes[1].set_xticks([1990, 2000, 2010, 2020])
    # the families named on the left of their lanes (no legend: more height for the labels)
    for t, (_, col, _) in zip(axes[0].get_yticklabels(), rows):
        t.set_color(col)
    axes[0].tick_params(axis='y', length=0)
    axes[1].spines['bottom'].set_linestyle((0, (2, 1)))
    save_fig('ch0_model_history')

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print('Chapter 0 charts')
    print(fig_cross_asset_growth().round(2))
    print(fig_risk_return().round(3))
    print(fig_sp500_drawdowns())
    print(fig_vix_regimes())
    print(fig_vix_vrp())
    print(fig_rates())
    print(fig_concentration())
    print(fig_rolling_correlations())
    print(fig_rolling_vol())
    print(fig_stablecoins())
    print(fig_usdt_peg())
    print(fig_ibit())
    print(fig_romania())
    print(fig_romania_split())
    print(fig_bvb_history())
    print(fig_bad_ticks())
    print(fig_hhl_elasticity())
    fig_market_history()
    fig_model_history()

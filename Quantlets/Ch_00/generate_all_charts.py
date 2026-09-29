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
from mfm_data import load, load_panel  # noqa: E402

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


def log_axis(ax, ticks):
    """Axa logaritmica cu etichete lizibile (fara notatie stiintifica)."""
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
eurron_mkt = load('EUR/RON (market file)')          # fisierul de piata: contine erori de cotatie (slide-ul Data pitfalls)
bonds = load_panel(['Romania 10y', 'Germany 10y'])  # curatate in fig_romania: 0.00% (24 Dec 2013), duminici 2022

CROSS = ['S&P 500 TR (SPY)', 'Euro Stoxx 50 (USD)', 'Nikkei 225 (USD)', 'Gold', 'US Treasuries 20y+ (TLT)', 'Bitcoin']
CROSS_COL = [MainBlue, Forest, Purple, Amber, Teal, Orange]
fx_usd = load_panel(['USD per EUR', 'JPY per USD'])   # FRED


def to_usd(local, fx, invert=False):
    """Converteste un indice in moneda locala in USD cu cursul FRED din aceeasi zi
    (ultimul curs disponibil, cel mult 5 zile in urma, daca ziua lipseste)."""
    f = fx.dropna().reindex(local.index, method='ffill', tolerance=pd.Timedelta(days=5))
    return (local / f if invert else local * f).dropna()


def cross_panel():
    """Seriile comparate pe clase de active, toate in USD:
    S&P 500 = SPY ajustat (randament total); Euro Stoxx 50 si Nikkei 225 = indici de pret convertiti in USD;
    TLT = randament total; aur = spot; Bitcoin = pret."""
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
    """Diferenta de CAGR dintre S&P 500 cu dividende reinvestite (SPY ajustat) si indicele de pret."""
    c_tr, _ = ann_stats(px['SPY'].loc[start:])
    c_px, _ = ann_stats(px['S&P 500'].loc[start:])
    return c_tr, c_px, c_tr - c_px


def clean_series(y, max_dev=1.0, window=11):
    """Elimina weekend-urile si punctele aflate la peste max_dev de mediana mobila centrata."""
    y = y[y.index.dayofweek < 5]
    med = y.rolling(window, center=True, min_periods=3).median()
    return y[(y - med).abs() <= max_dev]


def drawdown(p):
    """Drawdown fata de maximul anterior: P_t / max_{s<=t} P_s - 1."""
    return p / p.cummax() - 1


def ann_stats(p, periods=252):
    """Randament anualizat (CAGR) si volatilitate anualizata din preturi zilnice.

    periods='obs' foloseste numarul efectiv de observatii pe an al seriei.
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
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
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
    legend_outside_bottom(ax, ncol=3, y=-0.12)
    plt.tight_layout()
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
        cagr, v = ann_stats(s, 'obs')          # q = numarul observat de zile de tranzactionare pe an
        rows.append((n, cagr, v, s.index[0]))
    res = pd.DataFrame(rows, columns=['asset', 'cagr', 'vol', 'from']).set_index('asset')
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
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
    ax.set_title('Risk and return, 2015-2026: assets in USD, EUR/RON in RON per EUR',
                 fontsize=9, loc='left')
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
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 3.6), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    axes[0].plot(s.index, s.values, color=MainBlue, lw=0.8)
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
        axes[1].annotate(f'{name}\n{v:.0%}', (t, v), xytext=(0, -2), textcoords='offset points',
                         ha='center', va='top', fontsize=7)
    axes[1].set_ylim(dd.min() * 1.45, 0.02)
    axes[0].set_title('S&P 500, 2000-2026: level (log scale) and drawdown from the running peak',
                      fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_sp500_drawdowns')
    return res


# =============================================================================
# FIG 4: VIX -- regimuri de volatilitate
# =============================================================================
def fig_vix_regimes():
    v = px['VIX'].dropna()
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(v.index, v.values, color=MainBlue, lw=0.5)
    ax.axhline(20, color=Amber, ls='--', lw=0.8)
    ax.axhline(30, color=IDAred, ls='--', lw=0.8)
    ax.text(1.005, 20 / (v.max() * 1.18), 'VIX = 20', fontsize=7, color=Amber, transform=ax.transAxes, va='center')
    ax.text(1.005, 30 / (v.max() * 1.18), 'VIX = 30', fontsize=7, color=IDAred, transform=ax.transAxes, va='center')
    # cele mai mari varfuri, separate prin cel putin 2 ani
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
# FIG 5: Dobanzi SUA si inversarea curbei (10y - 2y)
# =============================================================================
def fig_rates():
    d = fred[['DGS10', 'DGS2']].dropna()
    ff = fred['FEDFUNDS'].dropna()
    spread = d['DGS10'] - d['DGS2']
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 3.6), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    axes[0].plot(ff.index, ff.values, color=Teal, lw=0.9, label='Fed funds (monthly)')
    axes[0].plot(d.index, d['DGS2'], color=Amber, lw=0.7, label='2-year Treasury')
    axes[0].plot(d.index, d['DGS10'], color=MainBlue, lw=0.7, label='10-year Treasury')
    axes[0].set_ylabel('Yield (%)')
    h, l = axes[0].get_legend_handles_labels()
    axes[1].legend(h, l, loc='upper center', bbox_to_anchor=(0.5, -0.32), ncol=3, frameon=False, fontsize=7.5)
    axes[1].plot(spread.index, spread.values, color=MainBlue, lw=0.6)
    axes[1].fill_between(spread.index, spread.values, 0, where=spread < 0, color=IDAred, alpha=0.45, lw=0)
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_ylabel('10y - 2y (pp)')
    inv = spread.loc['2022':'2024']
    axes[0].set_title('US rates 2000-2026 and the yield-curve spread (red = inverted curve)',
                      fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_rates')
    runs = (spread < 0).astype(int)
    first_neg = inv[inv < 0].index.min()
    last_neg = inv[inv < 0].index.max()
    return dict(min_spread=round(spread.min(), 2), min_date=spread.idxmin().date(),
                inversion_2022_24=(first_neg.date(), last_neg.date(), int((inv < 0).sum())),
                last_10y=round(d['DGS10'].iloc[-1], 2), last_2y=round(d['DGS2'].iloc[-1], 2),
                last_date=d.index[-1].date(), last_ff=round(ff.iloc[-1], 2), share_inverted=runs.mean())


# =============================================================================
# FIG 6: Concentrarea pietei: ponderat dupa capitalizare vs ponderi egale
# =============================================================================
def fig_concentration():
    p = px[['SPY', 'RSP']].dropna()
    ratio = (p['SPY'] / p['SPY'].iloc[0]) / (p['RSP'] / p['RSP'].iloc[0])
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={'width_ratios': [1.25, 1]})
    for col, c, lab in [('SPY', MainBlue, 'SPY (cap-weighted)'), ('RSP', Amber, 'RSP (equal-weighted)')]:
        g = p[col] / p[col].iloc[0]
        axes[0].plot(g.index, g.values, color=c, lw=0.8, label=f'{lab}: x{g.iloc[-1]:.1f}')
    log_axis(axes[0], [0.5, 1, 2, 4, 8])
    axes[0].set_ylabel('Growth of 1 USD (log)')
    legend_outside_bottom(axes[0], ncol=1, y=-0.12)
    axes[1].plot(ratio.index, ratio.values, color=IDAred, lw=0.8)
    axes[1].axhline(1, color=Gray, lw=0.5, ls=':')
    axes[1].set_title('SPY / RSP relative performance', fontsize=8.5, loc='left')
    axes[0].set_title(f'S&P 500 ETFs, {p.index[0]:%b %Y}-2026 (total return)', fontsize=8.5, loc='left')
    plt.tight_layout()
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
    eq = np.log(px['S&P 500'].dropna()).diff()              # dropna inainte de diff: calendarul propriu
    bd = np.log(px['US Treasuries 20y+ (TLT)'].dropna()).diff()
    btc = np.log(px['Bitcoin'].dropna()).diff()
    both = pd.concat([eq, bd], axis=1).dropna()
    c_sb = both.iloc[:, 0].rolling(window).corr(both.iloc[:, 1])
    # analiza comuna: join pe PRETURI in zilele comune, apoi diff -> ambele randamente acopera
    # acelasi interval (de ex. vineri -> luni); diff inainte de join ar da Bitcoin duminica -> luni
    pp = pd.concat([px['S&P 500'], px['Bitcoin']], axis=1).dropna()
    trio = np.log(pp).diff().dropna()
    c_be = trio.iloc[:, 0].rolling(window).corr(trio.iloc[:, 1])
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(c_sb.index, c_sb.values, color=MainBlue, lw=0.9, label='S&P 500 vs long Treasuries (TLT)')
    ax.plot(c_be.index, c_be.values, color=Orange, lw=0.9, label='S&P 500 vs Bitcoin')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylim(-0.8, 0.8)
    ax.set_ylabel('1-year rolling correlation')
    ax.set_title('Diversification is not constant: rolling correlations of daily log returns',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    plt.tight_layout()
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
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.plot(v_btc.index, v_btc.values, color=Orange, lw=0.8, label='Bitcoin (365 days/year)')
    ax.plot(v_eq.loc['2014-09':].index, v_eq.loc['2014-09':].values, color=MainBlue, lw=0.8,
            label='S&P 500 (252 days/year)')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
    ax.set_ylabel('Annualised volatility (63 observations)')
    ratio = (v_btc.loc['2024':].mean() / v_eq.loc['2024':].mean())
    ax.set_title(f'Rolling volatility: Bitcoin is still about {ratio:.1f} times as volatile as the S&P 500 '
                 f'(2024-2026)', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    plt.tight_layout()
    save_fig('ch0_rolling_vol')
    return dict(btc_2015_17=v_btc.loc['2015':'2017'].mean(), btc_2024_26=v_btc.loc['2024':].mean(),
                eq_2024_26=v_eq.loc['2024':].mean(), ratio=ratio)


# =============================================================================
# FIG 9: Oferta de stablecoins (DefiLlama)
# =============================================================================
def fig_stablecoins():
    s = stable[stable > 0].loc['2018':]
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    ax.fill_between(s.index, s.values, 0, color=Forest, alpha=0.25, lw=0)
    ax.plot(s.index, s.values, color=Forest, lw=0.9)
    ax.set_ylabel('USD-pegged stablecoins (bn USD)')
    pts = {}
    peak = s.loc['2022'].idxmax()                         # maximul din 2022
    trough = s.loc[peak:'2023-12-31'].idxmin()            # minimul exact de dupa maxim
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
# FIG 10: ETF-ul spot Bitcoin IBIT: valoarea tranzactionata
# =============================================================================
def fig_ibit():
    d = pd.concat([px['IBIT'], ibit_volume, px['Bitcoin']], axis=1, keys=['p', 'v', 'btc']).dropna()
    dv = (d['p'] * d['v'] / 1e9)
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
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
    ax.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=3, frameon=False)
    ax.set_title('iShares Bitcoin Trust (IBIT) since launch on 11 Jan 2024: price x volume',
                 fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch0_ibit')
    return dict(first=d.index[0].date(), mean_bn=dv.mean(), median_bn=dv.median(), max_bn=dv.max(),
                max_date=dv.idxmax().date(), total_bn=dv.sum())


# =============================================================================
# FIG 11: Piata romaneasca: BET, blue chips BVB, EUR/RON
# =============================================================================
def fig_romania():
    """BET-TR si blue chips BVB (ajustate pentru dividende), EUR/RON (BNR), randamente 10 ani RO vs DE."""
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw={'width_ratios': [1.35, 0.9, 0.9]})
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


def data_pitfall():
    """EUR/RON: fisierul de piata (cu erori de cotatie) vs BNR, 2015-2026."""
    r_e = np.log(eurron_mkt).diff().dropna().loc['2015':]
    r_b = np.log(eurron).diff().dropna().loc['2015':]
    top = r_e.abs().sort_values(ascending=False).head(6)
    q = lambda r: len(r) / ((r.index[-1] - r.index[0]).days / 365.25)   # frecventa observata (FX: nu 252)
    return dict(vol_market=r_e.std() * np.sqrt(q(r_e)), vol_bnr=r_b.std() * np.sqrt(q(r_b)),
                largest={d.date(): round(r_e.loc[d], 4) for d in top.index})



# =============================================================================
# FIG: Istoria BVB - BET 1997-2011, BET-XT din 2011, BET-TR din 2014 (scara log)
# =============================================================================
def fig_bvb_history():
    """Indicele BET 1997-2026 pe scara log, valori oficiale de inchidere, cu evenimente marcate."""
    bet = load('BET', start='1997-01-01').dropna()
    full = bet
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
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
    legend_outside_bottom(ax, ncol=1, y=-0.13)
    plt.tight_layout()
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


def etf_share():
    """Ponderea ETF-urilor in actiunile corporative SUA (Financial Accounts of the US), trimestrial, 2001 Q1 - ultimul trimestru."""
    q = load_panel(['ETF equities', 'All equities'], start='2001-01-01').dropna()
    return (q['ETF equities'] / q['All equities']).rename('ETF share')


def fig_hhl_passive():
    """Stanga: ponderea ETF. Dreapta: regula din Sectiunea V.A (81% activi la start, transmisie 0,33):
    scaderea ponderii active si scaderea implicita a elasticitatii agregate E_agg fata de 2001 Q1."""
    s = etf_share()
    active = HHL['active0'] - (s - s.iloc[0])
    d_active = active / HHL['active0'] - 1
    d_elast = HHL['pass_through'] * d_active
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    axes[0].plot(s.index, 100 * s.values, color=Teal, lw=1.1, label='ETF share of US corporate equities')
    for d in [s.index[0], pd.Timestamp('2020-10-01'), s.index[-1]]:
        axes[0].plot(d, 100 * s.loc[d], 'o', ms=3.5, color=Teal)
        axes[0].annotate(f'{100 * s.loc[d]:.1f}%', xy=(d, 100 * s.loc[d]), xytext=(0, 6),
                         textcoords='offset points', ha='center', fontsize=7, color='black')
    axes[0].set_ylabel('Share of market value (%)')
    axes[0].set_ylim(0, 12.5)
    axes[0].set_xlim(pd.Timestamp('2000-01-01'), pd.Timestamp('2027-12-31'))
    axes[0].set_title('ETF share, 2001 Q1 - ' + f'{s.index[-1].year} Q{s.index[-1].quarter}', fontsize=9, loc='left')
    axes[1].plot(d_active.index, 100 * d_active.values, color=IDAred, lw=1.1,
                 label='Active share = elasticity if $\\chi = 0$')
    axes[1].plot(d_elast.index, 100 * d_elast.values, color=MainBlue, lw=1.1,
                 label='Elasticity, pass-through 0.33 ($\\chi = 2.97$)')
    axes[1].axhline(0, color=Gray, lw=0.5, ls=':')
    for d in [pd.Timestamp('2020-10-01'), s.index[-1]]:
        for ser, c in [(d_active, IDAred), (d_elast, MainBlue)]:
            axes[1].plot(d, 100 * ser.loc[d], 'o', ms=3.5, color=c)
            axes[1].annotate(f'{100 * ser.loc[d]:.1f}%', xy=(d, 100 * ser.loc[d]), xytext=(-4, -9),
                             textcoords='offset points', ha='right', fontsize=7, color='black')
    axes[1].set_ylabel('Change since 2001 Q1 (%)')
    axes[1].set_ylim(-15, 1.5)
    axes[1].set_title('Implied change (81% active in 2001)', fontsize=9, loc='left')
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.tick_params(axis='x', labelsize=7.5)
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=7.5)
    plt.tight_layout()
    save_fig('ch0_hhl_passive')
    pick = lambda d: dict(etf=round(s.loc[d], 4), active=round(d_active.loc[d], 4), elast=round(d_elast.loc[d], 4))
    return {str(d.date()): pick(d) for d in [s.index[0], pd.Timestamp('2020-10-01'), s.index[-1]]}


def fig_hhl_elasticity():
    """Ec. (5): elasticitatea agregata dupa ce o fractie 1 - alpha din investitori devine pasiva,
    relativ la piata fara investitori pasivi: alpha (1 + chi) / (1 + chi alpha)."""
    alpha = np.linspace(0, 1, 401)
    rel = lambda chi: alpha * (1 + chi) / (1 + chi * alpha)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
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
    legend_outside_bottom(ax, ncol=2, y=-0.27)
    plt.tight_layout()
    save_fig('ch0_hhl_elasticity')
    return {chi: round(0.70 * (1 + chi) / (1 + chi * 0.70), 3) for chi in (0, HHL['chi'], 10)}

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print('Chapter 0 charts')
    print(fig_cross_asset_growth().round(2))
    print(fig_risk_return().round(3))
    print(fig_sp500_drawdowns())
    print(fig_vix_regimes())
    print(fig_rates())
    print(fig_concentration())
    print(fig_rolling_correlations())
    print(fig_rolling_vol())
    print(fig_stablecoins())
    print(fig_ibit())
    print(fig_romania())
    print(fig_bvb_history())
    print(data_pitfall())
    print(fig_hhl_passive())
    print(fig_hhl_elasticity())

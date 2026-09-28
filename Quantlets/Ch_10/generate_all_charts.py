"""
Generator pentru toate graficele si cifrele din Capitolul 10: Microstructura pietei
==================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos; niciun text si nicio serie in gri.
Date: bare de 5 minute SPY (octombrie 2020 - septembrie 2026, sesiunea regulata) si Bitcoin (septembrie 2024 -
septembrie 2026); date zilnice OHLCV pentru actiuni americane, actiuni BVB si cripto-active (data/market);
cursul de referinta BNR USD/RON pentru conversia valorilor tranzactionate la BVB; indicele VIX.
Registrele de ordine din sectiunea 2 si modelul Roll sunt SIMULATE (etichetate ca atare).
Cifrele sunt salvate in ch10_results.json (folosite de generatoarele de slide-uri).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import (ASSETS, GROUPS, LABELS, read_market, ohlc, returns, dollar_volume,  # noqa: E402
                      intraday_spy, intraday_btc)
from micro import (roll_spread, cs_spread, ar_terms, amihud, walk_book, gm_quotes, gm_simulate,  # noqa: E402
                   kyle, ac_trajectory, ac_frontier, zi_simulate, edge_spread, roll_mc, price_discovery)

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
Teal     = '#17A2B8'
Gray     = '#7F7F7F'   # doar linii de referinta
GROUP_COL = {'US': MainBlue, 'BVB': IDAred, 'Crypto': Amber}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
START2 = '2024-09-19'          # ultimii doi ani (sectiunea transversala)
START10 = '2016-09-19'         # ultimii zece ani (serii de timp)
B_BOOT = 1000


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


def fig_legend_bottom(fig, handles, labels, ncol=3, y=0.0):
    """O singura legenda pentru o figura cu mai multe panouri, sub figura."""
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


# =============================================================================
# 1. REGISTRUL DE ORDINE SIMULAT
# =============================================================================
ZI_PARAMS = dict(n_events=300_000, L=40, rate_limit=0.1, rate_market=0.5, rate_cancel=0.02, seed=7)


def zi_book():
    """Simularea registrului de ordine si functia de impact a unui ordin la piata."""
    path, snaps, _ = zi_simulate(**ZI_PARAMS)
    prof = pd.concat(snaps).groupby('rel')[['bid', 'ask']].mean()
    sizes = [1, 2, 3, 5, 8, 12, 20, 30, 50, 80]
    imp, cost = {}, {}
    for q in sizes:
        last, vw = [], []
        for s in snaps:
            a = s[(s['rel'] > 0) & (s['ask'] > 0)]
            asks = list(zip(a['rel'], a['ask']))
            if sum(x for _, x in asks) < q:
                continue
            fills, vwap, _, _ = walk_book(asks, q)
            last.append(max(p for p, _ in fills))
            vw.append(vwap)
        imp[q], cost[q] = np.mean(last), np.mean(vw)
    slope = np.polyfit(np.log(sizes), np.log([imp[q] for q in sizes]), 1)[0]
    return dict(path=path, snaps=snaps, prof=prof, sizes=sizes, imp=imp, cost=cost, slope=slope)


def pooled_profile(p):
    """Adancimea medie la distanta k de mijloc: media dintre bid(-k) si ask(+k) (registrul este simetric in medie)."""
    ask = p['ask'][p.index > 0]
    bid = p['bid'][p.index < 0]
    bid.index = -bid.index
    return ((ask + bid.reindex(ask.index)) / 2).dropna()


def fig_lob(zb):
    snap = zb['snaps'][len(zb['snaps']) // 2]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    ax = axes[0]
    ax.bar(snap['rel'], snap['bid'], width=0.9, color=Forest, label='Buy limit orders (bids)')
    ax.bar(snap['rel'], snap['ask'], width=0.9, color=IDAred, label='Sell limit orders (asks)')
    ax.axvline(0, color=Gray, lw=0.8, ls='--')
    ax.set_xlabel('Distance from the mid-price (ticks)')
    ax.set_ylabel('Orders at the price level')
    ax.set_title('One snapshot of a simulated order book', fontsize=9, loc='left')
    ax = axes[1]
    p = zb['prof']
    pool = pooled_profile(p)
    ax.plot(pool.index, pool.values, color=Purple, lw=1.5, marker='o', ms=2.5, label='Average depth, bids and asks pooled')
    ax.set_xlabel('Distance from the mid-price (ticks)')
    ax.set_ylabel('Average depth (orders)')
    ax.set_title(f"Average depth over {len(zb['snaps'])} snapshots", fontsize=9, loc='left')
    h, l = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h + h2, l + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_lob_snapshot')
    sp = zb['path']['spread']
    return dict(spread_mean=float(sp.mean()), spread_med=float(sp.median()), spread_p90=float(sp.quantile(0.9)),
                n_snaps=len(zb['snaps']), depth1=float(pool.loc[0.5:1.5].mean()),
                depth10=float(pool.loc[9.5:10.5].mean()), depth25=float(pool.loc[24.5:25.5].mean()))


def fig_impact(zb):
    s = np.array(zb['sizes'])
    last = np.array([zb['imp'][q] for q in s])
    cost = np.array([zb['cost'][q] for q in s])
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.loglog(s, last, 'o-', color=IDAred, label='Deepest price level reached (ticks from mid)')
    ax.loglog(s, cost, 's-', color=MainBlue, label='Average execution price (ticks from mid)')
    c = last[0] / s[0] ** 0.5
    ax.loglog(s, c * s ** 0.5, ls='--', color=Gray, lw=0.8, label='Reference slope 1/2')
    ax.set_xlabel('Size of the market buy order (units)')
    ax.set_ylabel('Ticks above the mid-price')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch10_walk_book')
    return dict(slope=float(zb['slope']), imp1=float(last[0]), imp80=float(last[-1]), cost1=float(cost[0]),
                cost80=float(cost[-1]), impslope_cost=float(np.polyfit(np.log(s), np.log(cost), 1)[0]))


# =============================================================================
# 2. MODELUL ROLL (SIMULAT)
# =============================================================================
def roll_sim(n=5000, sigma=0.02, c=0.05, seed=SEED):
    """Pretul eficient m_t (mers aleator) si pretul tranzactiei p_t = m_t + c q_t, q_t = +1 / -1 (cumparare / vanzare)."""
    rng = np.random.default_rng(seed)
    m = 100 + np.cumsum(rng.normal(0, sigma, n))
    q = np.where(rng.random(n) < 0.5, 1, -1)
    p = m + c * q
    dp = np.diff(p)
    cov1 = np.mean((dp[1:] - dp.mean()) * (dp[:-1] - dp.mean()))
    return m, q, p, dict(c=c, sigma=sigma, cov1=cov1, s_hat=2 * np.sqrt(-cov1), s_true=2 * c,
                         var_dp=float(np.var(dp)), var_theory=sigma ** 2 + 2 * c ** 2,
                         rho1=float(cov1 / np.var(dp)), rho1_theory=-c ** 2 / (sigma ** 2 + 2 * c ** 2))


def fig_roll():
    m, q, p, out = roll_sim()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3), gridspec_kw={'width_ratios': [1.5, 1]})
    ax = axes[0]
    k = np.arange(80)
    ax.plot(k, m[:80], color=MainBlue, lw=1.4, label='Efficient price $m_t$')
    ax.plot(k, p[:80], color=IDAred, lw=0.9, marker='o', ms=2.5, label='Trade price $p_t = m_t + c\\,q_t$')
    ax.set_xlabel('Trade number')
    ax.set_ylabel('Price')
    ax.set_title('Simulated bid-ask bounce ($c$ = 0.05, $\\sigma$ = 0.02)', fontsize=9, loc='left')
    ax = axes[1]
    dp = np.diff(p)
    dm = np.diff(m)
    lags = np.arange(1, 9)
    acf_p = [np.corrcoef(dp[l:], dp[:-l])[0, 1] for l in lags]
    acf_m = [np.corrcoef(dm[l:], dm[:-l])[0, 1] for l in lags]
    ax.bar(lags - 0.18, acf_p, 0.36, color=IDAred, label='Trade price changes')
    ax.bar(lags + 0.18, acf_m, 0.36, color=MainBlue, label='Efficient price changes')
    b = 1.96 / np.sqrt(len(dp))
    ax.axhspan(-b, b, color='#DADADA', alpha=0.6, lw=0, zorder=0)
    ax.axhline(out['rho1_theory'], color=Gray, ls='--', lw=0.8)
    ax.set_xlabel('Lag')
    ax.set_ylabel('Autocorrelation')
    ax.set_title('Autocorrelation of price changes', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=4, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_roll_bounce')
    out['rho1_hat'] = float(acf_p[0])
    return out


# =============================================================================
# 3. TIPARE INTRAZILNICE
# =============================================================================
def spy_tod(s):
    """Profilul pe intervale de 5 minute: media |r| (pb), volumul median (milioane de actiuni), ponderea in volumul zilei."""
    x = s.dropna(subset=['r'])
    tod = x.groupby('tod').agg(absr=('r', lambda v: 1e4 * v.abs().mean()), vol=('volume', 'median'))
    share = (s['volume'] / s.groupby('date')['volume'].transform('sum')).groupby(s['tod']).mean()
    tod['share'] = 100 * share
    return tod


def fig_spy_intraday(s):
    tod = spy_tod(s)
    x = np.arange(len(tod))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    ax.bar(x, tod['share'], color=Teal, width=0.85, label='Share of daily volume (%)')
    ax.set_ylabel('Share of daily volume (%)')
    ax = axes[1]
    ax.plot(x, tod['absr'], color=IDAred, marker='o', ms=2.5, label='Mean absolute 5-minute return (bp)')
    ax.set_ylabel('Mean |return| (basis points)')
    for a in axes:
        a.set_xticks(x[::12])
        a.set_xticklabels(tod.index[::12], rotation=0, fontsize=7.5)
        a.set_xlabel('Start of the 5-minute bar (New York time)')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_spy_intraday')
    mid = tod.loc['11:30':'14:00']
    return dict(n_days=int(s['date'].nunique()), first=s['date'].min().strftime('%Y-%m-%d'),
                last=s['date'].max().strftime('%Y-%m-%d'),
                share_open=float(tod['share'].iloc[0]), share_close=float(tod['share'].iloc[-1]),
                share_last30=float(tod['share'].iloc[-6:].sum()), share_first30=float(tod['share'].iloc[:6].sum()),
                share_mid=float(mid['share'].mean()), absr_open=float(tod['absr'].iloc[0]),
                absr_mid=float(mid['absr'].mean()), absr_close=float(tod['absr'].iloc[-1]),
                ratio_open_mid=float(tod['absr'].iloc[0] / mid['absr'].mean()))


def btc_hours(b):
    x = b.dropna(subset=['r'])
    wk = x.index.dayofweek >= 5
    h = pd.DataFrame({'weekday': 1e4 * x.loc[~wk, 'r'].abs().groupby(x.index[~wk].hour).mean(),
                      'weekend': 1e4 * x.loc[wk, 'r'].abs().groupby(x.index[wk].hour).mean()})
    return h


def fig_btc_hours(b):
    h = btc_hours(b)
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.plot(h.index, h['weekday'], color=Amber, marker='o', ms=3, label='Monday to Friday')
    ax.plot(h.index, h['weekend'], color=Purple, marker='s', ms=3, label='Saturday and Sunday')
    ax.axvspan(13.5, 20, color='#DADADA', alpha=0.5, lw=0, label='US equity session (13:30-20:00 UTC in summer)')
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel('Hour of the day (UTC)')
    ax.set_ylabel('Mean |5-minute return| (bp)')
    legend_outside_bottom(ax, ncol=3, y=-0.22)
    save_fig('ch10_btc_hours')
    x = b.dropna(subset=['r'])
    wk = x.index.dayofweek >= 5
    return dict(first=b.index.min().strftime('%Y-%m-%d'), last=b.index.max().strftime('%Y-%m-%d'),
                n_bars=int(len(x)), peak_hour=int(h['weekday'].idxmax()), peak=float(h['weekday'].max()),
                low_hour=int(h['weekday'].idxmin()), low=float(h['weekday'].min()),
                wd=float(1e4 * x.loc[~wk, 'r'].abs().mean()), we=float(1e4 * x.loc[wk, 'r'].abs().mean()),
                ratio=float(x.loc[~wk, 'r'].abs().mean() / x.loc[wk, 'r'].abs().mean()))


# =============================================================================
# 4. ESTIMATORI DE SPREAD
# =============================================================================
def intraday_spreads(s):
    """Estimatorii Roll, Corwin-Schultz si Abdi-Ranaldo calculati pe barele de 5 minute ale fiecarei zile."""
    rows = {}
    for d, g in s.dropna(subset=['close', 'high', 'low']).groupby('date'):
        rs, cov = roll_spread(g['close'])
        rows[d] = dict(cov=cov, cs=cs_spread(g['high'], g['low']).mean(),
                       ar2=ar_terms(g['close'], g['high'], g['low']).mean(), price=g['close'].mean(),
                       edge=edge_spread(g['open'], g['high'], g['low'], g['close']),
                       var=np.var(np.diff(np.log(g['close'].values)), ddof=1))
    return pd.DataFrame(rows).T


def daily_spreads(key, start=START2):
    """Estimatorii din date zilnice pe ultimii doi ani (valori in puncte de baza)."""
    d = ohlc(key, start)
    rs, cov = roll_spread(d['close'])
    cs = cs_spread(d['high'], d['low'])
    ar2 = ar_terms(d['close'], d['high'], d['low'])
    return dict(roll=1e4 * rs if rs == rs else np.nan, roll_cov=float(cov), cs=1e4 * float(np.mean(cs)),
                edge=1e4 * edge_spread(d['open'], d['high'], d['low'], d['close']),
                ar=1e4 * float(np.sqrt(max(np.mean(ar2), 0))), ar_neg=bool(np.mean(ar2) <= 0), n=int(len(d)))


def fig_spread_frequency(E, sp_daily):
    tick = 1e4 * (0.01 / E['price']).mean()
    roll5 = 1e4 * 2 * np.sqrt(max(-E['cov'].mean(), 0))
    cs5 = 1e4 * E['cs'].mean()
    ar5 = 1e4 * np.sqrt(max(E['ar2'].mean(), 0))
    edge5 = 1e4 * E['edge'].mean()                  # media estimarilor EDGE cu semn (nedeplasata)
    vals = {'Roll': (sp_daily['roll'], roll5), 'Corwin-Schultz': (sp_daily['cs'], cs5), 'Abdi-Ranaldo': (sp_daily['ar'], ar5),
            'EDGE': (sp_daily['edge'], edge5)}
    fig, ax = plt.subplots(figsize=(6.8, 3.3))
    x = np.arange(4)
    ax.bar(x - 0.2, [v[0] for v in vals.values()], 0.38, color=MainBlue, label='From daily bars (last two years)')
    ax.bar(x + 0.2, [v[1] for v in vals.values()], 0.38, color=Teal, label='From 5-minute bars (average over days)')
    ax.axhline(tick, color=IDAred, ls='--', lw=1.1, label=f'One tick (USD 0.01) relative to the price: {tick:.2f} bp')
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(list(vals))
    ax.set_ylabel('Estimated relative spread (bp, log scale)')
    legend_outside_bottom(ax, ncol=1, y=-0.14)
    save_fig('ch10_spread_frequency')
    rng = np.random.default_rng(SEED)
    ev = E['edge'].values
    eb = [1e4 * ev[rng.integers(0, len(ev), len(ev))].mean() for _ in range(B_BOOT)]
    return dict(tick=float(tick), roll5=float(roll5), cs5=float(cs5), ar5=float(ar5), roll_d=float(sp_daily['roll']),
                cs_d=float(sp_daily['cs']), ar_d=float(sp_daily['ar']), edge5=float(edge5), edge_d=float(sp_daily['edge']),
                edge5_lo=float(np.percentile(eb, 2.5)), edge5_hi=float(np.percentile(eb, 97.5)),
                share_negcov=float((E['cov'] < 0).mean()), n_days=int(len(E)))


def spread_table():
    return {k: daily_spreads(k) for k in ASSETS}


def fig_spread_cross(T):
    keys = [k for g in ('US', 'BVB', 'Crypto') for k in GROUPS[g]]
    y = np.arange(len(keys))
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.barh(y + 0.2, [T[k]['cs'] for k in keys], 0.38, color=[GROUP_COL[ASSETS[k][2]] for k in keys],
            label='Corwin-Schultz')
    ax.barh(y - 0.2, [T[k]['ar'] for k in keys], 0.38, color=[GROUP_COL[ASSETS[k][2]] for k in keys], alpha=0.6,
            hatch='///', edgecolor='white', label='Abdi-Ranaldo')
    ax.set_yticks(y)
    ax.set_yticklabels([LABELS[k] for k in keys], fontsize=7.5)
    for t, k in zip(ax.get_yticklabels(), keys):
        t.set_color(GROUP_COL[ASSETS[k][2]])
    ax.invert_yaxis()
    ax.set_xlabel('Estimated relative spread from daily bars (bp), September 2024 - September 2026')
    from matplotlib.patches import Patch
    h = [Patch(color=MainBlue, label='US'), Patch(color=IDAred, label='BVB'), Patch(color=Amber, label='Crypto'),
         Patch(facecolor='white', edgecolor=MainBlue, hatch='///', label='Hatched: Abdi-Ranaldo; solid: Corwin-Schultz')]
    ax.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, -0.09), ncol=4, frameon=False)
    save_fig('ch10_spread_estimators')


# =============================================================================
# 5. ILICIDITATEA AMIHUD
# =============================================================================
def amihud_table(start=START2):
    out = {}
    for k in ASSETS:
        r = returns(k, start)
        dv = dollar_volume(k, start)
        out[k] = dict(illiq=amihud(r, dv), dv_med=float(dv.median() / 1e6), n=int(len(r)))
    return out


def fig_amihud(A):
    keys = sorted(ASSETS, key=lambda k: A[k]['illiq'])
    y = np.arange(len(keys))
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    ax.barh(y, [A[k]['illiq'] for k in keys], color=[GROUP_COL[ASSETS[k][2]] for k in keys])
    ax.set_xscale('log')
    ax.set_yticks(y)
    ax.set_yticklabels([LABELS[k] for k in keys], fontsize=7.5)
    for t, k in zip(ax.get_yticklabels(), keys):
        t.set_color(GROUP_COL[ASSETS[k][2]])
    ax.set_xlabel('Amihud illiquidity: mean |daily return| (bp) per USD 1 million traded (log scale)')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=g) for g, c in GROUP_COL.items()], loc='upper center',
              bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)
    save_fig('ch10_amihud')


def monthly_illiq(keys, start=START10):
    """Iliciditatea Amihud lunara (pb la 1 milion USD) pentru fiecare activ; mediana pe grup."""
    cols = {}
    for k in keys:
        x = pd.concat([returns(k, start).rename('r'), dollar_volume(k, start).rename('dv')], axis=1, join='inner').dropna()
        x = x[x['dv'] > 0]
        cols[k] = (1e4 * x['r'].abs() / (x['dv'] / 1e6)).resample('ME').mean()
    return pd.DataFrame(cols)


def fig_amihud_time():
    med = {}
    for g in ('US', 'BVB', 'Crypto'):
        keys = [k for k in GROUPS[g] if k not in ('SPY', 'TVBETETF')]
        med[g] = monthly_illiq(keys).median(axis=1)
    med = pd.DataFrame(med).loc['2017-01':'2026-08']
    fig, ax = plt.subplots(figsize=(9, 3.4))
    for g, c in GROUP_COL.items():
        ax.plot(med.index, med[g], color=c, lw=1.2, label=f'{g}: median across assets')
    ax.set_yscale('log')
    ax.set_ylabel('Amihud illiquidity (bp per USD 1 million)')
    ax.axvline(pd.Timestamp('2020-09-15'), color=Gray, ls=':', lw=0.9)
    ax.text(pd.Timestamp('2020-10-15'), 8, 'Romania becomes an emerging\nmarket (FTSE Russell), Sep 2020',
            fontsize=7, color='black', va='center')
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch10_amihud_time')
    r = med.resample('YE').mean()
    return dict(bvb_2017=float(r['BVB'].iloc[0]), bvb_2026=float(r['BVB'].iloc[-1]),
                us_2017=float(r['US'].iloc[0]), us_2026=float(r['US'].iloc[-1]),
                cr_2017=float(r['Crypto'].iloc[0]), cr_2026=float(r['Crypto'].iloc[-1]),
                ratio_bvb_us_2026=float(r['BVB'].iloc[-1] / r['US'].iloc[-1]))


def spy_illiq_daily(s):
    """Iliciditatea intrazilnica: media |r_5min| (pb) la 100 milioane USD tranzactionati, pe zi."""
    x = s.dropna(subset=['r', 'dv'])
    x = x[x['dv'] > 0]
    return (1e4 * x['r'].abs() / (x['dv'] / 1e8)).groupby(x['date']).mean().rename('illiq')


def fig_illiq_vix(s):
    ill = spy_illiq_daily(s)
    vix = read_market('VIX.INDX')['close'].rename('vix')
    j = pd.concat([ill, vix], axis=1, join='inner').dropna()
    m = j.resample('ME').mean()
    fig, ax = plt.subplots(figsize=(9, 3.3))
    l1 = ax.plot(m.index, m['illiq'], color=MainBlue, lw=1.4, label='SPY intraday illiquidity (bp per USD 100 million, monthly mean)')
    ax.set_ylabel('Illiquidity (bp per USD 100m)')
    ax2 = ax.twinx()
    ax2.spines['right'].set_visible(True)
    l2 = ax2.plot(m.index, m['vix'], color=IDAred, lw=1.1, ls='--', label='VIX (monthly mean, right axis)')
    ax2.set_ylabel('VIX')
    ax.legend(l1 + l2, [l.get_label() for l in l1 + l2], loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2,
              frameon=False)
    save_fig('ch10_spy_illiq_vix')
    X = sm.add_constant(np.log(j['vix']))
    fit = sm.OLS(np.log(j['illiq']), X).fit(cov_type='HAC', cov_kwds={'maxlags': 20})
    return dict(corr=float(j.corr().iloc[0, 1]), corr_m=float(m.corr().iloc[0, 1]), elast=float(fit.params.iloc[1]),
                elast_se=float(fit.bse.iloc[1]), n=int(len(j)), mean=float(j['illiq'].mean()),
                y2020=float(ill.loc['2020'].mean()), y2022=float(ill.loc['2022'].mean()),
                y2026=float(ill.loc['2026'].mean()), apr2025=float(ill.loc['2025-04'].mean()))


# =============================================================================
# 6. MODELE: GLOSTEN-MILGROM, KYLE
# =============================================================================
def fig_gm():
    mus = np.linspace(0, 0.95, 60)
    spreads = [gm_quotes(0.5, m, 90, 110)[0] - gm_quotes(0.5, m, 90, 110)[1] for m in mus]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    ax.plot(mus, spreads, color=MainBlue, lw=1.5, label='Initial spread ask - bid ($V_L$ = 90, $V_H$ = 110)')
    ax.set_xlabel('Share of informed traders $\\mu$')
    ax.set_ylabel('Spread')
    ax.set_title('Adverse selection widens the spread', fontsize=9, loc='left')
    ax = axes[1]
    sims = {}
    for mu, c in [(0.1, Amber), (0.3, IDAred)]:
        d = gm_simulate(mu, n=60, seed=3)
        sims[mu] = d
        ax.plot(d['t'], d['ask'], color=c, lw=1.2, label=f'Ask, $\\mu$ = {mu}')
        ax.plot(d['t'], d['bid'], color=c, lw=1.2, ls='--', label=f'Bid, $\\mu$ = {mu}')
    ax.axhline(110, color=Gray, lw=0.8, ls=':')
    ax.set_xlabel('Trade number')
    ax.set_ylabel('Quote')
    ax.set_title('Quotes learn the true value $V$ = 110', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch10_glosten_milgrom')
    first90 = {mu: int(next((i for i, r in d.iterrows() if r['bid'] > 108), -1)) for mu, d in sims.items()}
    return dict(spread_01=float(gm_quotes(0.5, 0.1, 90, 110)[0] - gm_quotes(0.5, 0.1, 90, 110)[1]),
                spread_03=float(gm_quotes(0.5, 0.3, 90, 110)[0] - gm_quotes(0.5, 0.3, 90, 110)[1]),
                t108_01=first90[0.1], t108_03=first90[0.3])


def fig_kyle():
    su = np.linspace(2, 40, 100)
    sv = 2.0
    lam = [kyle(sv, u)['lam'] for u in su]
    prof = [kyle(sv, u)['profit'] for u in su]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    axes[0].plot(su, lam, color=MainBlue, lw=1.5, label='Price impact $\\lambda = \\sigma_v / (2\\sigma_u)$')
    axes[0].set_xlabel('Noise-trader volume $\\sigma_u$ (thousand shares)')
    axes[0].set_ylabel('$\\lambda$ (price change per thousand shares)')
    axes[1].plot(su, prof, color=Forest, lw=1.5, label='Expected profit of the insider $\\sigma_v \\sigma_u / 2$')
    axes[1].set_xlabel('Noise-trader volume $\\sigma_u$ (thousand shares)')
    axes[1].set_ylabel('Expected profit (thousand USD)')
    for a in axes:
        a.set_title('$\\sigma_v$ = 2 USD', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_kyle')


# =============================================================================
# 7. IMPACTUL: RELATIA VOLUM - MISCARE DE PRET PE BARE SPY
# =============================================================================
def sqrt_relation(s, nb=20):
    x = s.dropna(subset=['r', 'volume']).copy()
    x = x[x['volume'] > 0]
    x['part'] = x['volume'] / x.groupby('tod')['volume'].transform('median')
    x['z'] = x['r'].abs() / x.groupby('date')['r'].transform('std')
    bins = np.quantile(x['part'], np.linspace(0, 1, nb + 1))
    g = x.groupby(pd.cut(x['part'], bins, include_lowest=True)).agg(v=('part', 'mean'), z=('z', 'mean'))
    slope, icpt = np.polyfit(np.log(g['v']), np.log(g['z']), 1)
    return x, g, slope, icpt


def fig_sqrt(s):
    x, g, slope, icpt = sqrt_relation(s)
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.loglog(g['v'], g['z'], 'o', color=IDAred, ms=5, label='SPY 5-minute bars, 20 groups by relative volume')
    vv = np.linspace(g['v'].min(), g['v'].max(), 50)
    ax.loglog(vv, np.exp(icpt) * vv ** slope, color=MainBlue, lw=1.3, label=f'Fitted power law, slope {slope:.2f}')
    ax.loglog(vv, np.exp(icpt) * vv ** 0.5, color=Gray, ls='--', lw=0.8, label='Slope 1/2 (square-root law)')
    ax.set_xlabel('Bar volume / median volume at that time of day')
    ax.set_ylabel('Mean |return| / daily s.d. of 5-min returns')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch10_sqrt_law')
    return dict(slope=float(slope), n=int(len(x)))


# =============================================================================
# 8. EXECUTIA OPTIMA: ALMGREN-CHRISS
# =============================================================================
AC = dict(X=1e6, T=5, N=5, sigma=0.95, eta=2.5e-6, gamma=2.5e-7)   # exemplul numeric din Almgren si Chriss (2001)


def fig_ac():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    res = {}
    for lam, c, lab in [(0, MainBlue, 'Risk-neutral, $\\lambda$ = 0 (sell evenly)'), (2e-6, Forest, '$\\lambda$ = 2e-6'),
                        (2e-5, Orange, '$\\lambda$ = 2e-5'), (1e-4, IDAred, '$\\lambda$ = 1e-4 (very risk averse)')]:
        t, x, E, V = ac_trajectory(lam=lam, N=50, **{k: v for k, v in AC.items() if k != 'N'})
        ax.plot(t, x / 1e3, color=c, lw=1.3, label=lab)
        t5, x5, E5, V5 = ac_trajectory(lam=lam, **AC)
        res[lam] = dict(x=list(x5), E=E5, sd=np.sqrt(V5))
    ax.set_xlabel('Time (days)')
    ax.set_ylabel('Shares still to sell (thousands)')
    ax.set_title('Optimal trading trajectories', fontsize=9, loc='left')
    ax = axes[1]
    lams = np.logspace(-8, -3.5, 60)
    fr = ac_frontier(lams=lams, **AC)
    ax.plot(fr['sd'] / 1e6, fr['E'] / 1e6, color=Purple, lw=1.5, label='Efficient frontier (N = 5 days)')
    for lam, c in [(0, MainBlue), (2e-6, Forest), (2e-5, Orange), (1e-4, IDAred)]:
        ax.plot(res[lam]['sd'] / 1e6, res[lam]['E'] / 1e6, 'o', color=c, ms=6)
    ax.set_xlabel('Standard deviation of cost (USD million)')
    ax.set_ylabel('Expected cost (USD million)')
    ax.set_title('Cost versus risk of the liquidation', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch10_almgren_chriss')
    return {str(k): v for k, v in res.items()}


# =============================================================================
# 9. EPISOADE: FLASH CRASH 2010, APRILIE 2025
# =============================================================================
def fig_flash():
    d = read_market('SPY.US').loc['2010-04-15':'2010-05-28']
    prev = d['close'].shift(1)
    fig, ax = plt.subplots(figsize=(8.4, 3.3))
    x = np.arange(len(d))
    ax.vlines(x, d['low'], d['high'], color=MainBlue, lw=2.2, label='Daily range: low to high')
    ax.plot(x, d['close'], 'o', color=IDAred, ms=3.5, label='Close')
    i = d.index.get_loc(pd.Timestamp('2010-05-06'))
    ax.annotate('6 May 2010: low of USD 105.00,\n10.1% below the previous close', xy=(i, d['low'].iloc[i]),
                xytext=(i - 13, d['low'].iloc[i] + 0.3), fontsize=7.5, color='black',
                arrowprops=dict(arrowstyle='->', color='black', lw=0.7))
    ax.set_xticks(x[::5])
    ax.set_xticklabels([t.strftime('%d %b') for t in d.index[::5]], fontsize=7.5)
    ax.set_ylabel('SPY price (USD)')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch10_flash_crash')
    r = d.loc['2010-05-06']
    return dict(low=float(r['low']), close=float(r['close']), prev=float(prev.loc['2010-05-06']),
                drop_low=float(r['low'] / prev.loc['2010-05-06'] - 1), drop_close=float(r['close'] / prev.loc['2010-05-06'] - 1),
                vol_ratio=float(r['volume'] / d['volume'].loc[:'2010-05-05'].median()))


def fig_april2025(s):
    days = ['2025-04-03', '2025-04-04', '2025-04-07', '2025-04-08', '2025-04-09']
    base = s.loc[s['date'] < pd.Timestamp(days[0])]
    prev_close = base['close'].dropna().iloc[-1]
    x = s.loc[s['date'].isin(pd.to_datetime(days))].copy()
    typical = s.loc['2025-01-01':'2025-03-31'].groupby('tod')['volume'].median()
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 4.2), sharex=True, gridspec_kw={'height_ratios': [1.6, 1]})
    k = np.arange(len(x))
    axes[0].plot(k, 100 * (x['close'] / prev_close - 1), color=MainBlue, lw=1.0, label='SPY, % change from the close of 2 April 2025')
    axes[1].bar(k, x['volume'] / 1e6, color=Teal, width=1.0, label='Volume per 5-minute bar (million shares)')
    axes[1].plot(k, typical.reindex(x['tod']).values / 1e6, color=IDAred, lw=0.9,
                 label='Median volume at the same time of day, January-March 2025')
    for j, dd in enumerate(days):
        axes[1].text(78 * j + 39, axes[1].get_ylim()[1] * 0.92 if j == 0 else axes[1].get_ylim()[1] * 0.92,
                     pd.Timestamp(dd).strftime('%d %b'), ha='center', fontsize=7.5, color='black')
        for a in axes:
            a.axvline(78 * j, color=Gray, lw=0.6, ls=':')
    axes[0].set_ylabel('% change')
    axes[1].set_ylabel('Million shares')
    axes[1].set_xticks([])
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.03)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch10_april2025')
    d7 = s.loc[s['date'] == pd.Timestamp('2025-04-07')]
    d9 = s.loc[s['date'] == pd.Timestamp('2025-04-09')]
    rv = s.groupby('date')['r'].apply(lambda v: np.sqrt((v ** 2).sum()))
    return dict(max_bar7=float(100 * d7['r'].max()), min_bar7=float(100 * d7['r'].min()),
                range7=float(100 * (d7['high'].max() / d7['low'].min() - 1)),
                oc9=float(100 * (d9['close'].iloc[-1] / d9['open'].iloc[0] - 1)),
                vol_ratio=float(x['volume'].sum() / (typical.sum() * len(days))),
                rv7=float(100 * rv.loc['2025-04-07']), rv_med=float(100 * rv.median()))


# =============================================================================
# 10. BVB: VALOAREA TRANZACTIONATA
# =============================================================================
def fig_bvb_turnover():
    keys = [k for k in GROUPS['BVB'] if k != 'TVBETETF']
    dv = pd.DataFrame({k: dollar_volume(k, START10) for k in keys}).fillna(0)
    m = dv.resample('ME').sum().loc['2017-01':'2026-08'] / 1e6
    top = ['TLV', 'SNP', 'H2O', 'BRD', 'SNG']
    fig, ax = plt.subplots(figsize=(9, 3.4))
    cols = [IDAred, MainBlue, Teal, Forest, Amber]
    ax.stackplot(m.index, [m[k] for k in top] + [m[[k for k in keys if k not in top]].sum(axis=1)],
                 colors=cols + [Purple], labels=[LABELS[k] for k in top] + ['Other five blue chips'], alpha=0.9)
    ax.set_ylabel('Monthly traded value (USD million)')
    ax.axvline(pd.Timestamp('2023-07-12'), color='black', lw=0.8, ls=':')
    ax.text(pd.Timestamp('2023-08-01'), ax.get_ylim()[1] * 0.93, 'Hidroelectrica IPO\n12 July 2023', fontsize=7, color='black', va='top')
    legend_outside_bottom(ax, ncol=6, y=-0.14)
    save_fig('ch10_bvb_turnover')
    y = m.sum(axis=1).resample('YE').sum()
    return dict(y2017=float(y.loc['2017'].iloc[0]), y2022=float(y.loc['2022'].iloc[0]), y2024=float(y.loc['2024'].iloc[0]),
                y2025=float(y.loc['2025'].iloc[0]), tlv_share=float(m['TLV'].loc['2025'].sum() / m.loc['2025'].sum().sum()),
                h2o_share=float(m['H2O'].loc['2025'].sum() / m.loc['2025'].sum().sum()))


# =============================================================================
# 11. PROPRIETATILE DE SELECTIE ALE ESTIMATORULUI ROLL (Harris, 1990)
# =============================================================================
def roll_small_sample(E):
    """Covarianta Roll pe zi (77 de randamente de 5 minute): ponderea zilelor cu covarianta pozitiva, observata si
    simulata sub modelul Roll adevarat (spread de un pas de cotare; fara spread), si deplasarea din demediere."""
    n = 77
    v = E['var'].mean()
    c_tick = (0.01 / E['price']).mean() / 2
    out = dict(pos_obs=float((E['cov'] > 0).mean()), n_days=int(len(E)), sd_bar=float(1e4 * np.sqrt(v)),
               c_tick=float(1e4 * c_tick))
    for tag, c in [('tick', c_tick), ('zero', 0.0)]:
        sig = np.sqrt(v - 2 * c ** 2)
        cov = np.array([roll_mc(c, sig, T=n + 1, R=len(E), seed=SEED + b) for b in range(200)])
        pos = (cov > 0).mean(axis=1)                        # 200 de "esantioane" de lungimea selectiei reale
        pooled = 1e4 * 2 * np.sqrt(np.clip(-cov.mean(axis=1), 0, None))
        out[f'pos_{tag}'] = float(pos.mean())
        out[f'pos_{tag}_lo'], out[f'pos_{tag}_hi'] = (float(x) for x in np.percentile(pos, [2.5, 97.5]))
        out[f'roll_{tag}'] = float(pooled.mean())
        out[f'roll_{tag}_lo'], out[f'roll_{tag}_hi'] = (float(x) for x in np.percentile(pooled, [2.5, 97.5]))
    # corectia deplasarii: E[cov_hat] ~ g1 - (g0 + 2 g1) / n  =>  g1 ~ (cov_mediu + var_medie / n) / (1 - 2 / n)
    g1 = (E['cov'].mean() + v / n) / (1 - 2 / n)
    out['roll_corr'] = float(1e4 * 2 * np.sqrt(max(-g1, 0)))
    out['roll5'] = float(1e4 * 2 * np.sqrt(max(-E['cov'].mean(), 0)))
    return out


# =============================================================================
# 12. DESCOPERIREA PRETULUI: ETF-UL PE BET SI INDICELE BET-TR (Hasbrouck, 1995; Gonzalo si Granger, 1995)
# =============================================================================
PD_START = START2


def bet_etf_pair(start=PD_START):
    """Logaritmul preturilor de inchidere: ETF-ul Patria-TVBETETF (zilele cu tranzactii) si indicele BET-TR, zile comune."""
    e = read_market('TVBETETF.RO')
    e = e[e['volume'] > 0]
    idx = read_market('BETTR.INDX')
    j = pd.concat([e['close'].rename('etf'), idx['close'].rename('idx')], axis=1, join='inner').dropna().loc[start:END_PD]
    return np.log(j)


END_PD = '2026-09-18'


def price_discovery_bet():
    from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_order
    y = bet_etf_pair()
    p = int(select_order(y.values, maxlags=10, deterministic='ci').bic)
    jo = coint_johansen(y.values, 0, max(p, 1))
    r = price_discovery(y.values, max(p, 1))
    sd = float(100 * (y['etf'] - y['idx']).std())
    return dict(n=int(len(y)), p=max(p, 1), trace=float(jo.lr1[0]), cv=float(jo.cvt[0, 1]), trace1=float(jo.lr1[1]),
                cv1=float(jo.cvt[1, 1]), a_etf=float(r['alpha'][0]), a_idx=float(r['alpha'][1]), t_etf=float(r['t'][0]),
                t_idx=float(r['t'][1]), cs_etf=float(r['cs'][0]), cs_idx=float(r['cs'][1]), is_etf_lo=float(r['is_lo'][0]),
                is_etf_hi=float(r['is_hi'][0]), is_idx_lo=float(r['is_lo'][1]), is_idx_hi=float(r['is_hi'][1]),
                corr=r['corr'], sd_basis=sd, start=y.index[0].strftime('%Y-%m-%d'), end=y.index[-1].strftime('%Y-%m-%d'))


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


if __name__ == '__main__':
    RES = {}
    zb = zi_book()
    RES['lob'] = fig_lob(zb)
    RES['impact'] = fig_impact(zb)
    RES['roll'] = fig_roll()
    spy = intraday_spy()
    btc = intraday_btc()
    RES['tod'] = fig_spy_intraday(spy)
    RES['btc'] = fig_btc_hours(btc)
    E = intraday_spreads(spy)
    E.to_csv(os.path.join(HERE, 'ch10_spy_intraday_spreads.csv'))
    T = spread_table()
    RES['spreads'] = T
    RES['freq'] = fig_spread_frequency(E, T['SPY'])
    fig_spread_cross(T)
    A = amihud_table()
    RES['amihud'] = A
    fig_amihud(A)
    RES['amihud_time'] = fig_amihud_time()
    RES['illiq_vix'] = fig_illiq_vix(spy)
    RES['gm'] = fig_gm()
    fig_kyle()
    RES['sqrt'] = fig_sqrt(spy)
    RES['ac'] = fig_ac()
    RES['flash'] = fig_flash()
    RES['apr2025'] = fig_april2025(spy)
    RES['bvb'] = fig_bvb_turnover()
    RES['roll_ss'] = roll_small_sample(E)
    RES['pdisc'] = price_discovery_bet()
    with open(os.path.join(HERE, 'ch10_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved ch10_results.json')

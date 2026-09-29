"""
seminar0.py -- Calculele si graficele Seminarului 0 (MFM): Pietele financiare in 2026
=====================================================================================
Fiecare functie calculeaza rezultatele unui exercitiu (numerele din slide-uri) si deseneaza
graficul rezolvarii in charts/ch0_sem_*.pdf|png (fundal transparent, etichete ENG, legenda jos).

Bootstrap: un singur generator, numpy.random.default_rng(42), folosit in ordinea exercitiilor
B1 extins -> B3 extins -> B5 extins -> C1 (aceeasi ordine ca in notebook-ul seminarului);
B2 extins foloseste default_rng(42) separat, perechile din B1 extins si saptamanile din A7 default_rng(2026).

Rulare:  python seminar0.py      (scrie seminar0_results.json)
Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import sys
import json
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from scipy import stats
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mfm_data                                                             # noqa: E402
from mfm_data import fetch_daily, read_market                              # noqa: E402
from functools import lru_cache                                            # noqa: E402


@lru_cache(maxsize=None)
def _load(name, start, end):
    return mfm_data.load(name, start, end)


def load(name, start=mfm_data.START, end=mfm_data.END):
    """mfm_data.load, memorata in timpul rularii (fiecare serie online se descarca o singura data)."""
    return _load(name, start, end).copy()


def load_panel(names, start=mfm_data.START, end=mfm_data.END):
    return pd.concat([load(n, start, end) for n in names], axis=1)
from generate_all_charts import (MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray,  # noqa: E402
                                 save_fig, legend_outside_bottom, log_axis, drawdown, clean_series,
                                 ann_stats, to_usd)

# graficele de seminar se afiseaza pe ~0,85 din latimea slide-ului: figuri de 5,6 inch, font 9
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 9.5
plt.rcParams['legend.fontsize'] = 8
W = 5.6

OUT = {}


def bottom_legend(fig, ncol=3, handles=None, labels=None, fontsize=7.5):
    """Legenda sub figura (in afara axelor), dupa tight_layout; save_fig o include (bbox_inches='tight')."""
    plt.tight_layout()
    if handles is None:
        handles, labels, seen = [], [], set()
        for ax in fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in seen and not l.startswith('_'):
                    handles.append(h); labels.append(l); seen.add(l)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False, fontsize=fontsize)


def fmt_pct(ax, axis='y', dec=0):
    f = plt.FuncFormatter(lambda v, _: f'{v:.{dec}%}')
    (ax.yaxis if axis == 'y' else ax.xaxis).set_major_formatter(f)


# =============================================================================
# FUNCTII AJUTATOARE (identice cu notebook-ul seminarului)
# =============================================================================
def sb_index(n, mean_block, rng):
    """Stationary bootstrap (Politis and Romano, 1994): blocks of random, geometric length with mean mean_block, wrapped around."""
    idx = np.empty(n, dtype=int); i = rng.integers(n)
    for t in range(n):
        i = rng.integers(n) if (t == 0 or rng.random() < 1 / mean_block) else (i + 1) % n
        idx[t] = i
    return idx


def obs_per_year(p):
    """Observed return intervals per year: n / Y, n = number of returns, Y = calendar days / 365.25."""
    return (len(p) - 1) / ((p.index[-1] - p.index[0]).days / 365.25)


def sharpe(R, q):
    """Annualised Sharpe ratio, r_f = 0: mean / sd of simple returns R times sqrt(q)."""
    return R.mean() / R.std(ddof=1) * np.sqrt(q)


def se_lo(R, q):
    """Lo (2002), iid Normal: SE of the annualised Sharpe from T daily returns, sqrt(q (1 + SR_d^2/2) / T)."""
    sr_d = R.mean() / R.std(ddof=1)
    return np.sqrt(q * (1 + sr_d ** 2 / 2) / len(R))


def se_opdyke(R, q):
    """Opdyke (2007): SE of the annualised Sharpe corrected for skewness and kurtosis of daily returns."""
    sr = R.mean() / R.std(ddof=1); g3 = stats.skew(R); g4 = stats.kurtosis(R, fisher=False)
    return np.sqrt((1 + sr ** 2 / 2 - g3 * sr + (g4 - 3) / 4 * sr ** 2) / len(R)) * np.sqrt(q)


def drawdown_spells(p):
    """Spells below a previous peak: a spell starts ON the (last) peak date and ends on the first close >= peak;
    a spell still open at the end of the sample is right-censored (end = None)."""
    peak = p.cummax(); spells, start = [], None
    for t, below in (p < peak).items():
        if below and start is None:
            start = p.loc[:t][p.loc[:t] == peak.loc[t]].index[-1]
        if not below and start is not None:
            spells.append((start, t)); start = None
    if start is not None:
        spells.append((start, None))
    return spells


def hampel_flags(x, c, floor=0.0, window=11):
    """Hampel filter (Hampel, 1974): flag |x_t - m_t| > max(c * 1.4826 * MAD_t, floor) over a centred window."""
    v, h = x.values, window // 2; med, mad = np.full(len(v), np.nan), np.full(len(v), np.nan)
    for t in range(len(v)):
        w = v[max(0, t - h):t + h + 1]
        med[t] = np.median(w); mad[t] = np.median(np.abs(w - med[t]))
    return pd.Series(np.abs(v - med) > np.maximum(c * 1.4826 * mad, floor), index=x.index)


def fisher_ci(r, n, z=1.96):
    """95% CI for a correlation with Fisher's z transform (iid pairs from a bivariate Normal distribution)."""
    se = 1 / np.sqrt(n - 3)
    return np.tanh(np.arctanh(r) - z * se), np.tanh(np.arctanh(r) + z * se)


def nw_lags(n):
    return int(4 * (n / 100) ** (2 / 9))


# =============================================================================
# A1, A2: exemple pe hartie
# =============================================================================
def a1_a2():
    P = np.array([100., 110., 99.])
    R = P[1:] / P[:-1] - 1; r = np.log(P[1:] / P[:-1])
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.0), gridspec_kw={'width_ratios': [1.1, 1]})
    ax = axes[0]
    ax.plot([0, 1, 2], P, 'o-', color=MainBlue, lw=1.3, ms=5, label='Price $P_t$')
    for t, (a, b) in enumerate(zip(R, r)):
        ax.annotate(f'R = {a:+.1%}\nr = {b:+.2%}', ((t + t + 1) / 2, (P[t] + P[t + 1]) / 2), xytext=(8, 0),
                    textcoords='offset points', fontsize=7.5, va='center', color='black')
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(['t = 0', 't = 1', 't = 2'])
    ax.set_ylim(95, 114); ax.set_ylabel('Price')
    ax.set_title('A1: path 100 -> 110 -> 99', loc='left')
    axes[1].plot([0], [0], marker='_', ms=22, mew=2.5, color=IDAred)
    vals = [R.sum(), (1 + R).prod() - 1, r.sum()]
    labs = ['Sum of simple\nreturns', 'Compounded\nsimple returns', 'Sum of log\nreturns']
    bars = axes[1].bar(labs, vals, color=[IDAred, MainBlue, Forest], width=0.55)
    for b_, v in zip(bars, vals):
        axes[1].annotate(f'{v:+.3%}', (b_.get_x() + b_.get_width() / 2, v), xytext=(0, -3 if v < 0 else 3),
                         textcoords='offset points', ha='center', va='top' if v < 0 else 'bottom', fontsize=8)
    axes[1].axhline(0, color=Gray, lw=0.6)
    axes[1].set_ylim(-0.0145, 0.004); fmt_pct(axes[1], dec=1)
    axes[1].tick_params(axis='x', labelsize=7.5)
    axes[1].set_title('Two-period return: which rule is right?', loc='left')
    plt.tight_layout()
    save_fig('ch0_sem_a1_returns')

    P2 = pd.Series([100., 120., 90., 110., 130., 100.])
    M = P2.cummax(); DD = P2 / M - 1
    fig, axes = plt.subplots(2, 1, figsize=(W, 2.5), sharex=True, gridspec_kw={'height_ratios': [1.2, 1]})
    axes[0].plot(P2.index, P2, 'o-', color=MainBlue, lw=1.2, ms=4, label='Price $P_t$')
    axes[0].step(M.index, M, where='post', color=Amber, lw=1.2, ls='--', label='Running peak $M_t$')
    axes[0].set_ylabel('Price'); axes[0].set_ylim(80, 142)
    axes[1].fill_between(DD.index, DD, 0, color=IDAred, alpha=0.3, lw=0)
    axes[1].plot(DD.index, DD, 'o-', color=IDAred, lw=1.0, ms=4, label='Drawdown $DD_t = P_t/M_t - 1$')
    axes[1].annotate('maximum drawdown -25.0%\n(day 2: 90 vs peak 120)', (2, -0.25), xytext=(-8, 0),
                     textcoords='offset points', fontsize=7.5, ha='right', va='center', color='black')
    axes[1].annotate('-23.1% from the\nnew peak 130', (5, DD[5]), xytext=(-8, 0), textcoords='offset points',
                     fontsize=7.5, ha='right', va='center', color='black')
    axes[1].set_ylim(-0.33, 0.04); fmt_pct(axes[1]); axes[1].set_ylabel('Drawdown')
    axes[1].set_xticks(range(6)); axes[1].set_xticklabels([f'day {i}' for i in range(6)])
    axes[0].set_title('A2: price, running peak and drawdown', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_a2_drawdown')
    OUT['A1'] = dict(R=R.tolist(), r=r.tolist(), sumR=R.sum(), comp=(1 + R).prod() - 1, sumr=r.sum())
    OUT['A2'] = dict(M=M.tolist(), DD=DD.round(4).tolist())
    OUT['A3A4'] = dict(v252=0.01 * np.sqrt(252), v365=0.01 * np.sqrt(365), Y=4277 / 365.25,
                       cagr=3.72 ** (365.25 / 4277) - 1)


# =============================================================================
# SETUP: previzualizarea datelor
# =============================================================================
def setup_preview():
    spy = load('SPY', start='2015-01-02')
    raw = read_market('SPY.US').loc['2015-01-02':'2015-01-08', ['close', 'adjusted_close']]
    OUT['setup'] = dict(first=str(spy.index[0].date()), last=str(spy.index[-1].date()), rows=len(spy),
                        preview=[(str(d.date()), round(c, 2), round(a, 2)) for d, (c, a) in raw.iterrows()])


# =============================================================================
# B6: cotatii eronate EUR/RON
# =============================================================================
def b6():
    m = load('EUR/RON (market file)', start='2015-01-01'); bnr = load('EUR/RON', start='2015-01-01')
    vol = lambda x: np.log(x).diff().dropna().std() * np.sqrt(obs_per_year(x))
    wd = m[m.index.dayofweek < 5]
    med = wd.rolling(11, center=True, min_periods=3).median()
    flagged = wd.index.difference(clean_series(m, max_dev=0.05).index)
    gap_bnr = pd.Series({d: abs(wd[d] - bnr.asof(d)) for d in flagged})
    confirmed = gap_bnr.index[gap_bnr > 0.05]; rule = wd.drop(confirmed)
    audit = []
    for d in flagged:
        audit.append(dict(date=str(d.date()), quote=round(wd[d], 4), median=round(med[d], 4),
                          bnr=round(bnr.asof(d), 4), bnr_date=str(bnr.index[bnr.index <= d][-1].date()),
                          gap=round(gap_bnr[d], 3), removed=bool(d in confirmed)))
    j = np.log(pd.concat([rule, bnr], axis=1, keys=['mkt', 'bnr']).dropna()).diff().dropna()
    ac = lambda x: np.log(x).diff().dropna().autocorr(1)
    dev = (m - m.rolling(11, center=True, min_periods=3).median()).abs()
    res = dict(rows=len(m), weekend=int((m.index.dayofweek >= 5).sum()), flagged=len(flagged),
               removed=len(confirmed), audit=audit, largest_dev=dev.max(), largest_dev_date=str(dev.idxmax().date()),
               vol_raw=vol(m), vol_clean=vol(rule), vol_bnr=vol(bnr), q_raw=obs_per_year(m), q_clean=obs_per_year(rule),
               q_bnr=obs_per_year(bnr), corr_changes=j['mkt'].corr(j['bnr']), n_common=len(j), ac_mkt=ac(rule),
               ac_bnr=ac(bnr), no_fixing=len(rule.index.difference(bnr.index)),
               rho1_raw=np.log(m).diff().dropna().autocorr(1))
    OUT['B6'] = res

    # grafic pentru cerinta: seria bruta si variatiile zilnice
    r = np.log(m).diff().dropna()
    fig, axes = plt.subplots(2, 1, figsize=(W, 2.5), sharex=True, gridspec_kw={'height_ratios': [1.2, 1]})
    axes[0].plot(m.index, m, color=IDAred, lw=0.6, label='EURRON.FOREX close (market file)')
    axes[0].set_ylabel('RON per EUR')
    axes[1].plot(r.index, r, color=MainBlue, lw=0.5, label='Daily log change')
    fmt_pct(axes[1]); axes[1].set_ylabel('Log change')
    axes[0].set_title('EUR/RON market file, 2015-2026: level and daily log changes', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_b6_raw')

    # grafic pentru rezolvare: vârful din aug. 2025 (eroare) vs mai 2026 (miscare reala) + volatilitati
    fig, axes = plt.subplots(1, 3, figsize=(W, 2.2), gridspec_kw={'width_ratios': [1, 1, 0.8]})
    for ax, (a, b, ttl) in zip(axes[:2], [('2025-07-28', '2025-08-29', 'Aug 2025: bad tick (removed)'),
                                           ('2026-04-22', '2026-05-22', 'May 2026: genuine move (kept)')]):
        seg = wd.loc[a:b]; bs = bnr.loc[a:b]
        ax.plot(seg.index, seg, 'o-', color=IDAred, lw=0.8, ms=2.5, label='Market file (weekdays)')
        ax.plot(med.loc[a:b].index, med.loc[a:b], color=Amber, lw=1.0, ls='--', label='11-day centred median')
        ax.plot(bs.index, bs, 's-', color=MainBlue, lw=0.8, ms=2.2, label='BNR fixing (13:00)')
        for d in flagged:
            if pd.Timestamp(a) <= d <= pd.Timestamp(b):
                ax.plot(d, wd[d], 'o', ms=7, mfc='none', mec='black', mew=0.9)
        ax.set_title(ttl, loc='left', fontsize=8.5)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.tick_params(axis='x', labelsize=7)
    axes[0].set_ylabel('RON per EUR')
    v = [res['vol_raw'], res['vol_clean'], res['vol_bnr']]
    bars = axes[2].bar(['Raw', 'Cleaned', 'BNR'], v, color=[IDAred, Amber, MainBlue], width=0.6)
    for b_, x in zip(bars, v):
        axes[2].annotate(f'{x:.1%}', (b_.get_x() + b_.get_width() / 2, x), xytext=(0, 2), textcoords='offset points',
                         ha='center', fontsize=8)
    axes[2].set_ylim(0, 0.145); axes[2].set_yticks([0, 0.04, 0.08, 0.12]); fmt_pct(axes[2])
    axes[2].tick_params(axis='x', labelsize=7.2)
    axes[2].set_title('Annualised volatility', loc='left', fontsize=8.5)
    h, l = axes[0].get_legend_handles_labels()
    h.append(plt.Line2D([], [], marker='o', ls='none', mfc='none', mec='black', ms=7)); l.append('Flagged quote')
    bottom_legend(fig, ncol=4, handles=h, labels=l)
    save_fig('ch0_sem_b6_audit')
    return m, bnr, wd, flagged


# =============================================================================
# B1: tabloul pe clase de active
# =============================================================================
def assets_b1():
    px = load_panel(['SPY', 'Euro Stoxx 50', 'Nikkei 225', 'Gold', 'US Treasuries 20y+ (TLT)', 'Bitcoin'])
    fx_usd = load_panel(['USD per EUR', 'JPY per USD'])
    assets = {'S&P 500 TR (SPY)': px['SPY'].dropna(),
              'Euro Stoxx 50 (USD)': to_usd(px['Euro Stoxx 50'].dropna(), fx_usd['USD per EUR']),
              'Nikkei 225 (USD)': to_usd(px['Nikkei 225'].dropna(), fx_usd['JPY per USD'], invert=True),
              'Gold': px['Gold'].dropna(), 'TLT': px['US Treasuries 20y+ (TLT)'].dropna(), 'Bitcoin': px['Bitcoin'].dropna()}
    assets = {k: v.loc['2015-01-02':] for k, v in assets.items()}
    # cate date folosesc un curs FRED din zilele anterioare (regula: ultimul curs, cel mult 5 zile calendaristice)
    carried = {}
    for n, loc, fx in [('Euro Stoxx 50 (USD)', px['Euro Stoxx 50'], fx_usd['USD per EUR']),
                       ('Nikkei 225 (USD)', px['Nikkei 225'], fx_usd['JPY per USD'])]:
        idx = assets[n].index
        carried[n] = int((~idx.isin(fx.dropna().index)).sum())
    return assets, carried


def b1(assets, carried):
    rows = {}
    for n, p in assets.items():
        q = obs_per_year(p); Y = (p.index[-1] - p.index[0]).days / 365.25
        r = np.log(p).diff().dropna()
        rows[n] = dict(first=str(p.index[0].date()), last=str(p.index[-1].date()), p0=p.iloc[0], p1=p.iloc[-1],
                       n=len(r), Y=Y, q=q, mult=p.iloc[-1] / p.iloc[0], cagr=(p.iloc[-1] / p.iloc[0]) ** (1 / Y) - 1,
                       sd=r.std(), vol=r.std() * np.sqrt(q), vol252=r.std() * np.sqrt(252))
    gld = fetch_daily('GLD.US', 'market', 'adjusted_close', start='2015-01-02')
    OUT['B1'] = dict(rows=rows, carried=carried,
                     gld_vol=np.log(gld).diff().dropna().std() * np.sqrt(252))
    cols = dict(zip(assets, [MainBlue, Forest, Purple, Amber, Teal, Orange]))
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.35), gridspec_kw={'width_ratios': [1.45, 1]})
    ends = {}
    for n, p in assets.items():
        g = p / p.iloc[0]
        axes[0].plot(g.index, g, color=cols[n], lw=0.8, label=n)
        ends[n] = (g.index[-1], g.iloc[-1])
    ypos, last = {}, None
    for n in sorted(ends, key=lambda k: ends[k][1]):             # etichete finale separate pe scara log
        y_ = np.log10(ends[n][1]) if last is None else max(np.log10(ends[n][1]), last + 0.16)
        ypos[n] = y_; last = y_
    for n, (t, v) in ends.items():
        axes[0].annotate(f'x{v:.2f}' if v < 10 else f'x{v:.0f}', (t, v), xytext=(t + pd.Timedelta(days=60), 10 ** ypos[n]),
                         fontsize=7, va='center', color=cols[n])
    log_axis(axes[0], [0.5, 1, 2, 5, 20, 100, 500])
    axes[0].axhline(1, color=Gray, lw=0.4, ls=':')
    axes[0].set_xlim(axes[0].get_xlim()[0], pd.Timestamp('2028-06-30'))
    axes[0].set_ylabel('Growth of 1 USD (log)')
    axes[0].set_title('Growth of 1 USD, 2 Jan 2015 - 18 Sep 2026', loc='left', fontsize=8.5)
    names = list(assets); y = np.arange(len(names))
    axes[1].barh(y + 0.2, [rows[n]['vol'] for n in names], 0.38, color=MainBlue, label='Volatility with observed q')
    axes[1].barh(y - 0.2, [rows[n]['vol252'] for n in names], 0.38, color=Orange, label='Volatility with q = 252')
    axes[1].set_yticks(y); axes[1].set_yticklabels([n.replace(' (USD)', '').replace(' TR (SPY)', ' (SPY)') for n in names],
                                                   fontsize=7.5)
    axes[1].invert_yaxis(); fmt_pct(axes[1], 'x')
    for n, yy in zip(names, y):
        axes[1].annotate(f"q = {rows[n]['q']:.0f}", (max(rows[n]['vol'], rows[n]['vol252']), yy), xytext=(3, 0),
                         textcoords='offset points', fontsize=6.8, va='center', color='black')
    axes[1].set_xlim(0, 0.85)
    axes[1].set_title('Annualised volatility', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=4, fontsize=7.2)
    save_fig('ch0_sem_b1_dashboard')


# =============================================================================
# B3: corelatii si calendare
# =============================================================================
def b3():
    eq, btc, tlt = load('S&P 500'), load('Bitcoin'), load('US Treasuries 20y+ (TLT)')
    # extras vineri -> luni: de ce facem join pe preturi inainte de randamente
    fri = pd.Timestamp('2024-03-08')
    days = pd.date_range(fri, fri + pd.Timedelta(days=3))
    exc = pd.concat([eq.reindex(days), btc.reindex(days)], axis=1, keys=['spx', 'btc'])
    excerpt = [(str(d.date()), d.strftime('%a'), None if np.isnan(a) else round(a, 2), round(b, 2))
               for d, (a, b) in exc.iterrows()]
    mon = fri + pd.Timedelta(days=3)
    align = dict(spx_fri_mon=np.log(eq[mon] / eq[fri]), btc_fri_mon=np.log(btc[mon] / btc[fri]),
                 btc_sun_mon=np.log(btc[mon] / btc[mon - pd.Timedelta(days=1)]))
    cb = np.log(pd.concat([eq, btc], axis=1).dropna()).diff().dropna()
    ffill = np.log(pd.concat([eq.reindex(btc.index).ffill(), btc], axis=1).loc['2021-12-31':]).diff().dropna().loc['2022':]
    wp = pd.concat([eq, btc], axis=1).dropna().resample('W-FRI').last()
    weekly = np.log(wp[wp.index <= cb.index[-1]]).diff().dropna().loc['2022':]
    roll_cb = cb.iloc[:, 0].rolling(252).corr(cb.iloc[:, 1])
    sb = np.log(pd.concat([eq, tlt], axis=1).dropna()).diff().dropna()
    roll_sb = sb.iloc[:, 0].rolling(252).corr(sb.iloc[:, 1])
    res = dict(excerpt=excerpt, align=align,
               common=cb.loc['2022':].corr().iloc[0, 1], n_common=len(cb.loc['2022':]),
               ffill=ffill.corr().iloc[0, 1], n_ffill=len(ffill), weekly=weekly.corr().iloc[0, 1], n_weekly=len(weekly),
               roll_mean=roll_cb.loc['2022':].mean(), n_roll=int(roll_cb.loc['2022':].notna().sum()),
               first_window_start=str(cb.index[cb.index.get_loc(roll_cb.loc['2022':].index[0]) - 251].date()),
               sb={f'{a}-{b}': dict(whole=sb.loc[a:b].corr().iloc[0, 1], roll=roll_sb.loc[a:b].mean(), n=len(sb.loc[a:b]))
                   for a, b in [('2010', '2020'), ('2022', '2026')]})
    OUT['B3'] = res
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.3), gridspec_kw={'width_ratios': [1.55, 1]})
    ax = axes[0]
    rc, rs = roll_cb.loc['2022':], roll_sb.loc['2022':]
    ax.plot(rc.index, rc, color=Orange, lw=0.9, label='Bitcoin - S&P 500, rolling 252')
    ax.plot(rs.index, rs, color=MainBlue, lw=0.9, label='S&P 500 - TLT, rolling 252')
    ax.hlines(res['common'], rc.index[0], rc.index[-1], color=Orange, ls='--', lw=1.0, label='Bitcoin - S&P 500, whole period')
    ax.hlines(res['sb']['2022-2026']['whole'], rs.index[0], rs.index[-1], color=MainBlue, ls='--', lw=1.0,
              label='S&P 500 - TLT, whole period')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylim(-0.45, 0.8); ax.set_ylabel('Correlation')
    ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_title('2022-2026: rolling vs whole-period estimates', loc='left', fontsize=8.5)
    labs = ['Common days', 'Forward-filled', 'Weekly (Fri)', 'Mean rolling 252']
    v = [res['common'], res['ffill'], res['weekly'], res['roll_mean']]
    bars = axes[1].bar(range(4), v, color=[Orange, Purple, Forest, Amber], width=0.6)
    for b_, x in zip(bars, v):
        axes[1].annotate(f'{x:.2f}', (b_.get_x() + b_.get_width() / 2, x), xytext=(0, 2), textcoords='offset points',
                         ha='center', fontsize=8)
    axes[1].set_xticks(range(4)); axes[1].set_xticklabels(labs, rotation=20, ha='right', fontsize=7.2)
    axes[1].set_ylim(0, 0.52)
    axes[1].set_title('Bitcoin - S&P 500, 2022-2026', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_b3_correlations')
    return eq, btc, tlt, cb, weekly, sb


# =============================================================================
# BOOTSTRAP: B1 extins -> B3 extins -> B5 extins -> C1 (un singur generator, seed 42)
# =============================================================================
def bootstraps(assets, cb, weekly, sb):
    rng = np.random.default_rng(42)
    # ---- B1 extins: Sharpe, SE, intervale bootstrap pe active
    rows, draws = {}, {}
    for n, p in assets.items():
        q = obs_per_year(p); years = (p.index[-1] - p.index[0]).days / 365.25
        r = np.log(p).diff().dropna().values; R = np.expm1(r); sr = sharpe(R, q)
        row = dict(sr=sr, se_lo=se_lo(R, q), se_op=se_opdyke(R, q), q=q, T=len(R), Y=years,
                   sr_d=R.mean() / R.std(ddof=1), skew=stats.skew(R), kurt=stats.kurtosis(R, fisher=False))
        for mb in (5, 20, 60):
            cs, ss = [], []
            for _ in range(2000 if mb == 20 else 1000):
                i = sb_index(len(r), mb, rng); cs.append(np.exp(r[i].sum() / years) - 1); ss.append(sharpe(R[i], q))
            row[f'sr_ci_{mb}'] = np.percentile(ss, [2.5, 97.5]).tolist()
            if mb == 20:
                row['cagr_ci_20'] = np.percentile(cs, [2.5, 97.5]).tolist()
                draws[n] = np.array(ss)
        rows[n] = row
    j = np.log(pd.concat([assets['S&P 500 TR (SPY)'], assets['Gold']], axis=1).dropna()).diff().dropna(); Rj = np.expm1(j.values)
    d0 = sharpe(Rj[:, 0], 252) - sharpe(Rj[:, 1], 252)
    first_idx = sb_index(len(Rj), 20, rng)          # prima reesantionare (afisata in slide-ul despre mecanism)
    ds = [sharpe(Rj[first_idx, 0], 252) - sharpe(Rj[first_idx, 1], 252)]
    ds += [sharpe(Rj[i, 0], 252) - sharpe(Rj[i, 1], 252) for i in (sb_index(len(Rj), 20, rng) for _ in range(1999))]
    ds = np.array(ds)
    OUT['B1x'] = dict(rows=rows, spy_gold=dict(n=len(Rj), d=d0, ci=np.percentile(ds, [2.5, 97.5]).tolist(),
                                               p=min(1, 2 * min((ds <= 0).mean(), (ds >= 0).mean())),
                                               share_pos=(ds > 0).mean(), sd=ds.std()))
    # prima reesantionare: blocurile (start, lungime)
    blocks, s0 = [], 0
    for t in range(1, len(first_idx) + 1):
        if t == len(first_idx) or first_idx[t] != (first_idx[t - 1] + 1) % len(Rj):
            blocks.append((int(first_idx[s0]), t - s0)); s0 = t
    OUT['B1x']['first_blocks'] = blocks[:6]; OUT['B1x']['n_blocks'] = len(blocks)
    OUT['B1x']['first_dates'] = [str(j.index[b].date()) for b, _ in blocks[:3]]
    # perechile (Bonferroni): generator separat 2026
    rng_pairs = np.random.default_rng(2026); pairs = []
    for a, b in itertools.combinations([k for k in assets if k != 'Bitcoin'], 2):
        jj = np.log(pd.concat([assets[a], assets[b]], axis=1).dropna()).diff().dropna(); Rp = np.expm1(jj.values)
        dd = np.array([sharpe(Rp[i, 0], 252) - sharpe(Rp[i, 1], 252) for i in (sb_index(len(Rp), 20, rng_pairs) for _ in range(2000))])
        pairs.append(dict(a=a, b=b, d=sharpe(Rp[:, 0], 252) - sharpe(Rp[:, 1], 252), ci=np.percentile(dd, [2.5, 97.5]).tolist(),
                          p=min(1, 2 * min((dd <= 0).mean(), (dd >= 0).mean()))))
    OUT['B1x']['pairs'] = pairs
    b1x_charts(rows, draws, ds, d0, j, first_idx)

    # ---- B3 extins: corelatia actiuni-obligatiuni
    a, c = sb.loc['2010':'2020'].values, sb.loc['2022':].values
    r1, r2 = np.corrcoef(a.T)[0, 1], np.corrcoef(c.T)[0, 1]
    se = np.sqrt(1 / (len(a) - 3) + 1 / (len(c) - 3))
    z = (np.arctanh(r2) - np.arctanh(r1)) / se
    se_iid = np.sqrt((1 - r1 ** 2) ** 2 / (len(a) - 3) + (1 - r2 ** 2) ** 2 / (len(c) - 3))
    dsb = np.array([np.corrcoef(c[sb_index(len(c), 20, rng)].T)[0, 1] - np.corrcoef(a[sb_index(len(a), 20, rng)].T)[0, 1]
                    for _ in range(2000)])
    lo, hi = np.percentile(dsb, [2.5, 97.5])
    b3x = dict(r1=r1, r2=r2, n1=len(a), n2=len(c), z1=np.arctanh(r1), z2=np.arctanh(r2), se=se, z=z,
               p=2 * stats.norm.sf(abs(z)), iid_ci=[r2 - r1 - 1.96 * se_iid, r2 - r1 + 1.96 * se_iid],
               boot_ci=[lo, hi], ratio=(hi - lo) / (3.92 * se_iid))
    for lab, x, mb in [('daily', cb.loc['2022':].values, 20), ('weekly', weekly.values, 4)]:
        r_ = np.corrcoef(x.T)[0, 1]; f = fisher_ci(r_, len(x))
        bs = np.percentile([np.corrcoef(x[sb_index(len(x), mb, rng)].T)[0, 1] for _ in range(2000)], [2.5, 97.5])
        b3x[lab] = dict(r=r_, n=len(x), fisher=list(f), boot=bs.tolist())
    OUT['B3x'] = b3x
    rng_w = np.random.default_rng(2026)
    cd = cb.loc['2022':]; wk = cd.index.to_period('W-FRI'); wf = weekly.copy(); wf.index = wf.index.to_period('W-FRI')
    weeks = [w for w in wk.unique() if w in wf.index]; Wv = wf.loc[weeks].values; Dv = [cd.values[wk == w] for w in weeks]
    gap = lambda idx: np.corrcoef(np.vstack([Dv[i] for i in idx]).T)[0, 1] - np.corrcoef(Wv[idx].T)[0, 1]
    gb = np.array([gap(sb_index(len(weeks), 4, rng_w)) for _ in range(2000)])
    OUT['A7gap'] = dict(gap=gap(np.arange(len(weeks))), weeks=len(weeks), ci=np.percentile(gb, [2.5, 97.5]).tolist(),
                        p=2 * min((gb <= 0).mean(), (gb >= 0).mean()))
    b3x_chart(dsb, b3x, gb)

    # ---- B5 extins: bootstrap pentru corelatia BET-TR / EUR-RON
    d = b5_data()
    arr = d.values
    bs = [np.corrcoef(arr[sb_index(len(arr), 20, rng)].T)[0, 1] for _ in range(2000)]
    OUT['B5x_boot'] = np.percentile(bs, [2.5, 97.5]).tolist()

    # ---- C1
    r = np.log(pd.concat([load('S&P 500'), load('Bitcoin')], axis=1).dropna()).diff().dropna()
    periods = {'2018-2019': ('2018-01-01', '2019-12-31'), '2020-2021': ('2020-01-01', '2021-12-31'),
               '2022 to 10 Jan 2024': ('2022-01-01', '2024-01-10'), '11 Jan 2024 to 18 Sep 2026': ('2024-01-11', '2026-09-18')}
    X, c1 = {}, {}
    for lab, (a_, b_) in periods.items():
        x = r.loc[a_:b_].values; X[lab] = x
        bsx = [np.corrcoef(x[sb_index(len(x), 20, rng)].T)[0, 1] for _ in range(2000)]
        c1[lab] = dict(r=np.corrcoef(x.T)[0, 1], ci=np.percentile(bsx, [2.5, 97.5]).tolist(), n=len(x))
    pre, post = X['2022 to 10 Jan 2024'], X['11 Jan 2024 to 18 Sep 2026']
    dd = np.array([np.corrcoef(post[sb_index(len(post), 20, rng)].T)[0, 1] - np.corrcoef(pre[sb_index(len(pre), 20, rng)].T)[0, 1]
                   for _ in range(2000)])
    OUT['C1'] = dict(periods=c1, diff=np.corrcoef(post.T)[0, 1] - np.corrcoef(pre.T)[0, 1],
                     diff_ci=np.percentile(dd, [2.5, 97.5]).tolist(), p=2 * min((dd <= 0).mean(), (dd >= 0).mean()))
    c1_chart(r, c1)


def b1x_charts(rows, draws, ds, d0, j, first_idx):
    names = list(rows)
    fig, ax = plt.subplots(figsize=(W, 2.1))
    y = np.arange(len(names))
    for k, n in enumerate(names):
        rw = rows[n]
        ax.errorbar(rw['sr'], k - 0.13, xerr=1.96 * rw['se_lo'], fmt='o', color=MainBlue, ms=4, capsize=2.5, lw=1.1,
                    label='iid Normal interval, $\\pm 1.96$ SE (Lo)' if k == 0 else None)
        lo, hi = rw['sr_ci_20']
        ax.errorbar(rw['sr'], k + 0.13, xerr=[[rw['sr'] - lo], [hi - rw['sr']]], fmt='s', color=Orange, ms=4, capsize=2.5,
                    lw=1.1, label='Stationary bootstrap, 95% percentile (block 20)' if k == 0 else None)
        ax.annotate(f"{rw['sr']:.2f}", (hi, k + 0.13), xytext=(4, 0), textcoords='offset points', fontsize=7, va='center')
    ax.axvline(0, color=Gray, lw=0.6)
    ax.set_yticks(y); ax.set_yticklabels([n.replace(' (USD)', '').replace(' TR (SPY)', ' (SPY)') for n in names], fontsize=7.8)
    ax.invert_yaxis(); ax.set_xlabel('Annualised Sharpe ratio (risk-free rate 0), 2015-2026')
    ax.set_xlim(-0.8, 2.0)
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_b1x_sharpe')

    fig, ax = plt.subplots(figsize=(W, 2.0))
    ax.hist(ds, bins=50, color=MainBlue, alpha=0.55, label='2,000 bootstrap differences (block 20, seed 42)')
    lo, hi = np.percentile(ds, [2.5, 97.5])
    ax.axvline(d0, color=IDAred, lw=1.4, label=f'Estimate {d0:+.2f}')
    ax.axvline(lo, color=Amber, lw=1.2, ls='--', label=f'95% percentile interval [{lo:+.2f}, {hi:+.2f}]')
    ax.axvline(hi, color=Amber, lw=1.2, ls='--')
    ax.axvline(0, color='black', lw=0.8, ls=':', label='Zero (no difference)')
    ax.set_xlabel('Sharpe(S&P 500 with dividends) - Sharpe(gold), common days')
    ax.set_ylabel('Count')
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_b1x_diff')

    # mecanismul: prima reesantionare, primele 120 de pozitii
    n_show = 120
    fig, ax = plt.subplots(figsize=(W, 1.75))
    idx = first_idx[:n_show]
    new = np.r_[True, idx[1:] != (idx[:-1] + 1) % len(j)]
    starts = np.where(new)[0]; ends = np.r_[starts[1:], n_show]
    palette = [MainBlue, Orange, Forest, Purple, Teal, IDAred, Amber]
    for k, (s_, e_) in enumerate(zip(starts, ends)):
        ax.plot(np.arange(s_, e_), idx[s_:e_], lw=2.2, color=palette[k % len(palette)])
        ax.annotate(f'{j.index[idx[s_]]:%d %b %Y}', (s_, idx[s_]), xytext=(2, 4), textcoords='offset points',
                    fontsize=6.8, color=palette[k % len(palette)])
    ax.set_xlabel('Position in the resampled series (first 120 of 2,944 days)')
    ax.set_ylabel('Original day index')
    ax.set_ylim(-100, len(j) + 250)
    ax.set_title('One stationary-bootstrap resample: blocks of consecutive days, each day keeps its (SPY, gold) pair',
                 loc='left', fontsize=8)
    plt.tight_layout()
    save_fig('ch0_sem_bootstrap_demo')


def b3x_chart(dsb, b3x, gb):
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.1))
    ax = axes[0]
    ax.hist(dsb, bins=40, color=MainBlue, alpha=0.55, label='Bootstrap changes (block 20)')
    ax.axvline(b3x['r2'] - b3x['r1'], color=IDAred, lw=1.3, label='Estimated change')
    for k, v in enumerate(b3x['boot_ci']):
        ax.axvline(v, color=Amber, ls='--', lw=1.1, label='Bootstrap 95% interval' if k == 0 else None)
    for k, v in enumerate(b3x['iid_ci']):
        ax.axvline(v, color=Forest, ls=':', lw=1.2, label='iid 95% interval' if k == 0 else None)
    ax.set_xlabel('Corr(2022-26) - Corr(2010-20)')
    ax.set_title('S&P 500 - TLT', loc='left', fontsize=8.5)
    ax = axes[1]
    ax.hist(gb, bins=40, color=Orange, alpha=0.55, label='Joint week-block bootstrap (block 4)')
    ax.axvline(0, color='black', ls=':', lw=0.9, label='Zero')
    ax.axvline(OUT['A7gap']['gap'], color=IDAred, lw=1.3)
    for v in OUT['A7gap']['ci']:
        ax.axvline(v, color=Amber, ls='--', lw=1.1)
    ax.set_xlabel('Daily - weekly correlation')
    ax.set_title('Bitcoin - S&P 500, 2022-2026', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=3, fontsize=7.2)
    save_fig('ch0_sem_b3x_change')


def c1_chart(r, c1):
    roll = r.iloc[:, 0].rolling(252).corr(r.iloc[:, 1]).loc['2017':]
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.1), gridspec_kw={'width_ratios': [1.5, 1]})
    axes[0].plot(roll.index, roll, color=MainBlue, lw=0.9, label='252-day rolling correlation')
    axes[0].axvline(pd.Timestamp('2024-01-11'), color=IDAred, ls='--', lw=1.0, label='First trading day of US spot Bitcoin ETFs')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_ylabel('Correlation'); axes[0].set_ylim(-0.3, 0.75)
    axes[0].set_title('Bitcoin - S&P 500, common days', loc='left', fontsize=8.5)
    axes[0].xaxis.set_major_locator(mdates.YearLocator(2)); axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    labs = list(c1)
    for k, lab in enumerate(labs):
        v = c1[lab]
        axes[1].errorbar(k, v['r'], yerr=[[v['r'] - v['ci'][0]], [v['ci'][1] - v['r']]], fmt='o',
                         color=IDAred if k == 3 else MainBlue, capsize=3, ms=4)
    axes[1].set_xticks(range(4))
    axes[1].set_xticklabels(['2018-19', '2020-21', '2022 -\n10 Jan 24', '11 Jan 24 -\nSep 26'], fontsize=7)
    axes[1].axhline(0, color=Gray, lw=0.5); axes[1].set_ylim(-0.3, 0.75)
    axes[1].set_title('Sub-periods, bootstrap 95%', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_c1_correlation')


# =============================================================================
# B2: drawdown-uri si timp de revenire
# =============================================================================
def b2():
    res, series = {}, {}
    for n, s in [('S&P 500', load('S&P 500')), ('Bitcoin', load('Bitcoin', start='2014-09-17'))]:
        dd = drawdown(s); spells = drawdown_spells(s)
        length = lambda x: ((x[1] or s.index[-1]) - x[0]).days
        longest = max(spells, key=length)
        deep_peak = s.loc[:dd.idxmin()].idxmax()
        rec = s.loc[dd.idxmin():][s.loc[dd.idxmin():] >= s[deep_peak]]
        res[n] = dict(first=str(s.index[0].date()), mdd=dd.min(), trough=str(dd.idxmin().date()), p_trough=s[dd.idxmin()],
                      peak=str(deep_peak.date()), p_peak=s[deep_peak], recovery=str(rec.index[0].date()) if len(rec) else None,
                      long_start=str(longest[0].date()), long_end=str(longest[1].date()) if longest[1] else None,
                      long_days=length(longest), long_tdays=int(((s.index > longest[0]) & (s.index <= (longest[1] or s.index[-1]))).sum()),
                      long_peak=s[longest[0]], current=dd.iloc[-1], last_peak=str(s.idxmax().date()), p_max=s.max(),
                      open_spell=spells[-1][1] is None, p_last=s.iloc[-1])
        series[n] = (s, dd, longest)
    # orizont comun: S&P 500 din 17 sep. 2014
    s = load('S&P 500', start='2014-09-17'); dd = drawdown(s); sp = drawdown_spells(s)
    lg = max(sp, key=lambda x: ((x[1] or s.index[-1]) - x[0]).days)
    res['S&P 500 (common horizon)'] = dict(mdd=dd.min(), trough=str(dd.idxmin().date()),
                                           long_days=((lg[1] or s.index[-1]) - lg[0]).days, long_start=str(lg[0].date()),
                                           long_end=str(lg[1].date()) if lg[1] else None)
    OUT['B2'] = res
    fig, axes = plt.subplots(2, 1, figsize=(W, 2.9), sharex=True)
    for ax, (n, c) in zip(axes, [('S&P 500', MainBlue), ('Bitcoin', Orange)]):
        s, dd, lg = series[n]
        ax.fill_between(dd.index, dd, 0, color=c, alpha=0.3, lw=0)
        ax.plot(dd.index, dd, color=c, lw=0.6, label=f'{n} drawdown')
        t = dd.idxmin()
        ax.plot(t, dd.min(), 'v', color=IDAred, ms=6)
        ax.annotate(f'deepest {dd.min():.1%} ({t:%b %Y})', (t, dd.min()), xytext=(8, 2), textcoords='offset points',
                    fontsize=7.5, color='black', va='center')
        end = lg[1] or s.index[-1]
        ax.plot([lg[0], end], [0.1, 0.1], color=Amber, lw=3, solid_capstyle='butt')
        ax.annotate(f'longest spell {lg[0]:%b %Y} - {end:%b %Y}: {(end - lg[0]).days:,} days', (end, 0.1),
                    xytext=(4, 0), textcoords='offset points', fontsize=7.2, va='center', color='black')
        ax.annotate(f'last close: {dd.iloc[-1]:.1%}\n(open spell, censored)', (dd.index[-1], dd.iloc[-1]), xytext=(4, -6),
                    textcoords='offset points', fontsize=6.8, ha='left', va='top', color='black')
        ax.set_ylim(-0.95, 0.2); ax.set_yticks([-0.8, -0.4, 0]); fmt_pct(ax); ax.set_ylabel('Drawdown')
        ax.set_title(n, loc='left', fontsize=8.5)
    axes[1].set_xlim(pd.Timestamp('1999-06-01'), pd.Timestamp('2030-06-30'))
    h = [plt.Rectangle((0, 0), 1, 1, color=MainBlue, alpha=0.3), plt.Rectangle((0, 0), 1, 1, color=Orange, alpha=0.3),
         plt.Line2D([], [], color=Amber, lw=3), plt.Line2D([], [], marker='v', ls='none', color=IDAred)]
    bottom_legend(fig, ncol=4, handles=h, labels=['S&P 500 drawdown', 'Bitcoin drawdown',
                                                   'Longest spell below a previous peak', 'Deepest trough'], fontsize=7.2)
    save_fig('ch0_sem_b2_underwater')


def b2x():
    r = np.log(load('S&P 500')).diff().dropna().values; n, B = len(r), 5000; rng2 = np.random.default_rng(42)

    def mdd_and_spell(paths):
        lp = np.concatenate([np.zeros((len(paths), 1)), np.cumsum(paths, axis=1)], axis=1)
        dd = lp - np.maximum.accumulate(lp, axis=1)
        spells = []
        for u in dd < 0:
            e = np.diff(np.r_[0, u.astype(int), 0]); st, en = np.where(e == 1)[0], np.where(e == -1)[0]
            spells.append((en - st + (en < len(u))).max(initial=0))
        return np.expm1(dd.min(axis=1)), np.array(spells)

    def sb_paths(n, b, B):
        new = rng2.random((B, n)) < 1 / b; new[:, 0] = True; t = np.broadcast_to(np.arange(n), (B, n))
        blk = np.maximum.accumulate(np.where(new, t, 0), axis=1); st = np.take_along_axis(rng2.integers(0, n, (B, n)), blk, axis=1)
        return (st + t - blk) % n

    m0, l0 = mdd_and_spell(r[None, :])
    res = dict(n=n, mdd=m0[0], spell=int(l0[0]))
    dist = {}
    for lab, idx in [('iid', rng2.integers(0, n, (B, n))), ('stationary', sb_paths(n, 20, B))]:
        m, l = mdd_and_spell(r[idx])
        dist[lab] = (m, l)
        res[lab] = dict(med=np.median(m), q05=np.quantile(m, 0.05), p=(m <= m0[0]).mean(), spell_med=np.median(l),
                        p_spell=(l >= l0[0]).mean())
    rs = pd.Series(r)
    res['rho1'] = rs.autocorr(1); res['vr20'] = pd.Series(np.cumsum(r)).diff(20).var() / (20 * rs.var())
    OUT['B2x'] = res
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.1))
    for lab, c in [('iid', MainBlue), ('stationary', Orange)]:
        m, l = dist[lab]
        axes[0].hist(m, bins=60, color=c, alpha=0.45, density=True,
                     label='iid bootstrap' if lab == 'iid' else 'Stationary bootstrap (block 20)')
        axes[1].hist(l, bins=60, color=c, alpha=0.45, density=True)
    axes[0].axvline(m0[0], color=IDAred, lw=1.4, label='Observed 2000-2026')
    axes[1].axvline(l0[0], color=IDAred, lw=1.4)
    fmt_pct(axes[0], 'x'); axes[0].set_xlabel('Maximum drawdown of the path')
    axes[1].set_xlabel('Longest spell below a peak (trading days)')
    axes[0].set_yticks([]); axes[1].set_yticks([])
    axes[0].set_title('5,000 paths per scheme', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_b2x_distributions')


# =============================================================================
# C2: critica unui raspuns AI
# =============================================================================
def c2():
    full = lambda sym: read_market(sym)
    spy_c = full('SPY.US')['close'].dropna(); spy_a = full('SPY.US')['adjusted_close'].dropna(); btc = full('BTC-USD.CC')['close'].dropna()
    def stats_(p, A, vol_rule):
        r = p.pct_change().dropna(); mu = r.mean() * A
        vol = r.std() * (A if vol_rule == 'wrong' else np.sqrt(A))
        return mu, vol, mu / vol
    ai = {'SPY': stats_(spy_c, 252, 'wrong'), 'BTC': stats_(btc, 252, 'wrong')}
    fix = {'SPY': stats_(spy_a, 252, 'right'), 'BTC': stats_(btc, 365, 'right')}
    step = {'SPY close, sqrt': stats_(spy_c, 252, 'right'), 'BTC 252, sqrt': stats_(btc, 252, 'right')}
    raw0 = full('SPY.US').iloc[0]
    OUT['C2'] = dict(ai={k: list(v) for k, v in ai.items()}, fix={k: list(v) for k, v in fix.items()},
                     step={k: list(v) for k, v in step.items()},
                     spy_range=[str(spy_a.index[0].date()), str(spy_a.index[-1].date())],
                     btc_range=[str(btc.index[0].date()), str(btc.index[-1].date())],
                     spy_first=[raw0['close'], raw0['adjusted_close']],
                     spy_sd=spy_c.pct_change().std(), btc_sd=btc.pct_change().std(), btc_mean=btc.pct_change().mean(),
                     btc_obs_2025=int((btc.index.year == 2025).sum()), spy_obs_2025=int((spy_a.index.year == 2025).sum()))
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.0))
    x = np.arange(2)
    for k, (lab, d, c) in enumerate([('AI answer', ai, IDAred), ('Corrected', fix, MainBlue)]):
        vv = [d['SPY'][1], d['BTC'][1]]; ss = [d['SPY'][2], d['BTC'][2]]
        b0 = axes[0].bar(x + (k - 0.5) * 0.36, vv, 0.34, color=c, label=lab)
        b1 = axes[1].bar(x + (k - 0.5) * 0.36, ss, 0.34, color=c)
        for bb, v in zip(b0, vv):
            axes[0].annotate(f'{v:.0%}', (bb.get_x() + bb.get_width() / 2, v), xytext=(0, 2), textcoords='offset points',
                             ha='center', fontsize=7.5)
        for bb, v in zip(b1, ss):
            axes[1].annotate(f'{v:.2f}', (bb.get_x() + bb.get_width() / 2, v), xytext=(0, 2), textcoords='offset points',
                             ha='center', fontsize=7.5)
    axes[0].set_yscale('log'); axes[0].set_ylim(0.08, 30)
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}'))
    axes[0].set_title('Annualised volatility (log scale)', loc='left', fontsize=8.5)
    axes[1].set_title('Sharpe ratio (risk-free rate 0)', loc='left', fontsize=8.5)
    axes[1].set_ylim(0, 1.75)
    for ax in axes:
        ax.set_xticks(x); ax.set_xticklabels(['SPY', 'Bitcoin'])
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_c2_correction')


# =============================================================================
# A5, A6, A7, A8, A9
# =============================================================================
def a5():
    btc = load('Bitcoin', start='2014-09-17')
    r = np.log(btc).diff().dropna(); R = np.expm1(r)
    m_d, s_d = r.mean(), r.std(); years = (btc.index[-1] - btc.index[0]).days / 365.25
    res = dict(first=str(btc.index[0].date()), last=str(btc.index[-1].date()), p0=btc.iloc[0], p1=btc.iloc[-1], n=len(r),
               Y=years, m_d=m_d, s_d=s_d, a_d=R.mean(), vR_d=R.var(), mu_log=m_d * 365, half_var=s_d ** 2 * 365 / 2,
               simple_ann=R.mean() * 365, cagr_mu=np.exp(m_d * 365) - 1,
               cagr_prices=(btc.iloc[-1] / btc.iloc[0]) ** (1 / years) - 1, q=obs_per_year(btc))
    OUT['A5'] = res
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.2), gridspec_kw={'width_ratios': [1.25, 1]})
    sig = np.linspace(0, 0.8, 200)
    axes[0].plot(sig, 0.10 - sig ** 2 / 2, color=MainBlue, lw=1.4, label='Approx. log growth $a - \\sigma^2/2$, $a$ = 10%')
    axes[0].plot(sig, np.log(1.10) - sig ** 2 / 2, color=Forest, lw=1.1, ls='--',
                 label='Exact if annual log returns are Normal: $\\ln 1.1 - \\sigma^2/2$')
    axes[0].axhline(0, color=Gray, lw=0.6)
    axes[0].plot(0.6, 0.10 - 0.18, 'o', color=IDAred, ms=5)
    axes[0].annotate('$\\sigma$ = 60%: -0.080', (0.6, -0.08), xytext=(-6, -10), textcoords='offset points', ha='right',
                     fontsize=7.5, color='black')
    axes[0].axvline(np.sqrt(0.2), color=Amber, lw=0.8, ls=':')
    axes[0].annotate('drag = mean\nat $\\sigma$ = 44.7%', (np.sqrt(0.2), 0.02), xytext=(4, 0), textcoords='offset points',
                     fontsize=7, color='black')
    fmt_pct(axes[0]); fmt_pct(axes[0], 'x'); axes[0].set_xlabel('Annual volatility $\\sigma$')
    axes[0].set_ylabel('Log growth'); axes[0].set_ylim(-0.25, 0.14)
    axes[0].set_title('Volatility drag, arithmetic mean 10%', loc='left', fontsize=8.5)
    vals = [res['mu_log'], res['half_var'], res['mu_log'] + res['half_var']]
    bars = axes[1].bar(['Log mean\n$365\\,m$', 'Drag\n$365\\,s^2/2$', 'Implied simple\nmean'], vals,
                       color=[MainBlue, IDAred, Forest], width=0.55)
    for b_, v in zip(bars, vals):
        axes[1].annotate(f'{v:.1%}', (b_.get_x() + b_.get_width() / 2, v), xytext=(0, 2), textcoords='offset points',
                         ha='center', fontsize=8)
    axes[1].set_ylim(0, 0.78); fmt_pct(axes[1]); axes[1].tick_params(axis='x', labelsize=7)
    axes[1].set_title('Bitcoin, annual, 2014-2026', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=2, fontsize=7.2)
    save_fig('ch0_sem_a5_drag')


def a6():
    fx = load('EUR/RON', start='2005-07-01'); rf = np.log(fx).diff().dropna()
    rho = rf.autocorr(1); vol = rf.std() * np.sqrt(252); f = np.sqrt((1 + rho) / (1 - rho))
    k = 252; exact = np.sqrt(1 + 2 * sum((1 - j / k) * rho ** j for j in range(1, k)))
    mk = load('EUR/RON (market file)', start='2015-01-01'); rm = np.log(mk).diff().dropna(); rm1 = rm.autocorr(1)
    mon = np.log(fx.resample('ME').last()).diff().dropna()
    acf = [rf.autocorr(j) for j in range(1, 11)]
    full_acf = np.sqrt(1 + 2 * sum((1 - j / k) * rf.autocorr(j) for j in range(1, 21)))
    res = dict(first=str(fx.index[0].date()), last=str(fx.index[-1].date()), n=len(rf), rho1=rho, vol=vol, factor=f,
               exact=exact, corrected=vol * f, rho1_mkt=rm1, factor_mkt=np.sqrt((1 + rm1) / (1 - rm1)), acf=acf,
               monthly=mon.std() * np.sqrt(12), n_months=len(mon), factor_acf20=full_acf,
               se_acf=1 / np.sqrt(len(rf)))
    OUT['A6'] = res
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.1), gridspec_kw={'width_ratios': [1.35, 1]})
    lags = np.arange(1, 11)
    axes[0].bar(lags - 0.18, acf, 0.36, color=MainBlue, label='BNR EUR/RON, sample ACF')
    axes[0].bar(lags + 0.18, rho ** lags, 0.36, color=Orange, label=f'Hypothetical AR(1), $\\rho^j$, $\\rho$ = {rho:.2f}')
    axes[0].axhspan(-1.96 / np.sqrt(len(rf)), 1.96 / np.sqrt(len(rf)), color=Gray, alpha=0.15, lw=0,
                    label='$\\pm 1.96/\\sqrt{n}$')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_xticks(lags); axes[0].set_xlabel('Lag $j$ (trading days)'); axes[0].set_ylabel('Autocorrelation')
    axes[0].set_title('Autocorrelation of daily log changes', loc='left', fontsize=8.5)
    v = [vol, vol * f, res['monthly']]
    bars = axes[1].bar(['Daily\nx $\\sqrt{252}$', 'AR(1)\ncorrection', 'Monthly\nx $\\sqrt{12}$'], v,
                       color=[MainBlue, Orange, Forest], width=0.55)
    for b_, x in zip(bars, v):
        axes[1].annotate(f'{x:.2%}', (b_.get_x() + b_.get_width() / 2, x), xytext=(0, 2), textcoords='offset points',
                         ha='center', fontsize=8)
    axes[1].set_ylim(0, 0.065); fmt_pct(axes[1], dec=0); axes[1].tick_params(axis='x', labelsize=7)
    axes[1].set_title('Annual volatility, 2005-2026', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_a6_acf')


def a7_a9(eq, btc):
    d = np.log(pd.concat([eq, btc], axis=1, keys=['x', 'y']).dropna()).diff().dropna().loc['2022':]
    x, y = d['x'] - d['x'].mean(), d['y'] - d['y'].mean(); sx, sy = x.std(), y.std()
    gam = lambda j: (x * y.shift(j)).mean() if j >= 0 else (x.shift(-j) * y).mean()
    rho1 = gam(0) / (sx * sy)
    lag = sum((5 - j) * (gam(j) + gam(-j)) for j in range(1, 5)) / (5 * sx * sy)
    contrib = {j: (5 - abs(j)) * gam(j) / (5 * sx * sy) for j in range(-4, 5) if j != 0}
    ov = d.rolling(5).sum().dropna()
    pc = pd.concat([eq, btc], axis=1).dropna(); anchors = {}
    for a in ['W-MON', 'W-TUE', 'W-WED', 'W-THU', 'W-FRI']:
        wp = pc.resample(a).last(); wp = wp[wp.index <= pc.index[-1]]
        w = np.log(wp).diff().dropna().loc['2022':]
        rw = w.corr().iloc[0, 1]; lo, hi = fisher_ci(rw, len(w))
        anchors[a[2:]] = dict(r=rw, lo=lo, hi=hi, n=len(w))
    OUT['A7'] = dict(n=len(d), rho1=rho1, lag=lag, implied=rho1 + lag, contrib=contrib,
                     overlap5=ov.corr().iloc[0, 1], ac_x=d['x'].autocorr(1), ac_y=d['y'].autocorr(1),
                     naive_se=(1 - 0.30 ** 2) / np.sqrt(246), anchors=anchors)
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.0), gridspec_kw={'width_ratios': [1, 1.1]})
    js = sorted(contrib)
    axes[0].bar(js, [contrib[j] for j in js], color=[MainBlue if j < 0 else Orange for j in js], width=0.6)
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_xticks(js); axes[0].set_xlabel('Lag $j$')
    axes[0].set_title(f'Lag terms $(5-|j|)\\gamma(j)/(5\\sigma_x\\sigma_y)$, sum {lag:+.3f}', loc='left', fontsize=8)
    for k, (a, v) in enumerate(anchors.items()):
        axes[1].errorbar(k, v['r'], yerr=[[v['r'] - v['lo']], [v['hi'] - v['r']]], fmt='o', color=Forest, capsize=3, ms=4,
                         label='Weekly, Fisher 95% interval' if k == 0 else None)
    axes[1].axhline(rho1, color=Orange, ls='--', lw=1.1, label=f'Daily, common days ({rho1:.2f})')
    axes[1].axhline(rho1 + lag, color=Purple, ls=':', lw=1.2, label=f'Implied 5-day ({rho1 + lag:.2f})')
    axes[1].set_xticks(range(5)); axes[1].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
    axes[1].set_xlabel('Weekly anchor day'); axes[1].set_ylim(0.1, 0.65)
    axes[1].set_title('Weekly correlation by anchor day', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_a7_weekly')

    c0 = d['x'].corr(d['y']); lead = d['x'].corr(d['y'].shift(1)); lagc = d['x'].shift(1).corr(d['y'])
    OUT['A9'] = dict(same=c0, spx_after_btc=lead, spx_before_btc=lagc, sum=c0 + lead + lagc,
                     theory={f'{dl:.3f}': dict(same=0.45 * (1 - dl), lead=0.45 * dl) for dl in (3 / 24, 4 / 24)})
    fig, ax = plt.subplots(figsize=(W, 1.9))
    labs = ['S&P 500 day $t$ with\nBitcoin day $t+1$', 'Same day $t$', 'S&P 500 day $t$ with\nBitcoin day $t-1$']
    obs = [lagc, c0, lead]
    th_s = [0, 0.45 * (1 - 4 / 24), 0.45 * 4 / 24]; th_w = [0, 0.45 * (1 - 3 / 24), 0.45 * 3 / 24]
    xx = np.arange(3)
    for k, (v, c, lab) in enumerate([(th_s, Amber, 'Model, summer ($\\delta$ = 4/24)'), (th_w, Purple, 'Model, winter ($\\delta$ = 3/24)'),
                                     (obs, MainBlue, 'Observed, 2022-2026')]):
        bb = ax.bar(xx + (k - 1) * 0.26, v, 0.24, color=c, label=lab)
        for b_, val in zip(bb, v):
            ax.annotate(f'{val:+.2f}', (b_.get_x() + b_.get_width() / 2, val), xytext=(0, 2 if val >= 0 else -9),
                        textcoords='offset points', ha='center', fontsize=6.8)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(xx); ax.set_xticklabels(labs, fontsize=7.2); ax.set_ylim(-0.1, 0.5)
    ax.set_ylabel('Correlation')
    ax.set_title('Model with $\\rho$ = 0.45 vs observed lead/lag correlations (X = Bitcoin, Y = S&P 500)', loc='left',
                 fontsize=8.2)
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_a9_leadlag')


def a8():
    spy = load('SPY', start='2015-01-02'); R = np.expm1(np.log(spy).diff().dropna()).values
    q = obs_per_year(spy); Y = (spy.index[-1] - spy.index[0]).days / 365.25
    sr_d = R.mean() / R.std(ddof=1); g3, g4 = stats.skew(R), stats.kurtosis(R, fisher=False)
    sr_a = sr_d * np.sqrt(q)
    res = dict(sr_a=sr_a, sr_d=sr_d, q=q, T=len(R), Y=Y, g3=g3, g4=g4,
               se_normal=np.sqrt(q * (1 + sr_d ** 2 / 2) / len(R)),
               se_general=np.sqrt(q * (1 - sr_d * g3 + sr_d ** 2 * (g4 - 1) / 4) / len(R)),
               se_annual=np.sqrt((1 + sr_a ** 2 / 2) / Y), term_skew=-sr_d * g3, term_kurt=sr_d ** 2 * (g4 - 3) / 4)
    OUT['A8'] = res
    fig, ax = plt.subplots(figsize=(W, 1.95))
    Ys = np.linspace(2, 40, 200)
    for qq, c, lab in [(252, MainBlue, 'Daily observations (q = 252)'), (12, Forest, 'Monthly observations (q = 12)'),
                       (1, IDAred, 'Annual observations (q = 1)')]:
        ax.plot(Ys, np.sqrt((1 + sr_a ** 2 / (2 * qq)) / Ys), color=c, lw=1.3, ls='-' if qq > 1 else '--', label=lab)
    ax.axvline(Y, color=Amber, lw=0.9, ls=':')
    ax.annotate(f'SPY sample: Y = {Y:.2f}, SE = {res["se_normal"]:.3f} (daily)', (Y, res['se_normal']), xytext=(6, 12),
                textcoords='offset points', fontsize=7.5, color='black')
    ax.set_xlabel('Sample span Y (years)'); ax.set_ylabel('SE of annual SR')
    ax.set_title(f'iid Normal returns, SR = {sr_a:.2f}: the span, not the frequency, sets the precision', loc='left',
                 fontsize=8.5)
    ax.set_ylim(0, 0.85)
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_a8_se_span')


# =============================================================================
# B4: stablecoin-uri
# =============================================================================
def b4():
    s = load('Stablecoins', start='2018-01-01'); s = s[s > 0]
    ye = s.resample('YE').last(); ye = ye[ye.index <= s.index[-1]]
    pk = s.loc['2022'].idxmax(); tr = s.loc[pk:'2023-12-31'].idxmin()
    s20 = s.loc['2020-01-01':]; yrs = (s20.index[-1] - s20.index[0]).days / 365.25
    res = dict(year_end={str(d.year): v for d, v in ye.loc['2019':].items()},
               growth={str(d.year): v for d, v in ye.pct_change().loc['2020':].items()},
               ytd=s.iloc[-1] / ye.iloc[-1] - 1, peak=str(pk.date()), v_peak=s[pk], trough=str(tr.date()), v_trough=s[tr],
               fall=s[tr] / s[pk] - 1, start=str(s20.index[0].date()), v_start=s20.iloc[0], last=str(s20.index[-1].date()),
               v_last=s20.iloc[-1], Y=yrs, cagr=(s20.iloc[-1] / s20.iloc[0]) ** (1 / yrs) - 1)
    OUT['B4'] = res
    s = s.loc['2019-06':]
    fig, ax = plt.subplots(figsize=(W, 2.0))
    ax.fill_between(s.index, s, 0, color=Forest, alpha=0.2, lw=0)
    ax.plot(s.index, s, color=Forest, lw=1.0, label='USD-pegged stablecoins in circulation (bn USD)')
    yy = ye.loc['2019':]
    ax.plot(yy.index, yy, 'o', color=MainBlue, ms=4, label='Year-end values')
    for d, v in yy.items():
        ax.annotate(f'{v:.1f}', (d, v), xytext=(0, -11) if d.year == 2025 else (0, 5), textcoords='offset points',
                    ha='center', fontsize=7, color=MainBlue)
    for d, lab, dy in [(pk, f'peak {s[pk]:.1f}\n{pk:%d %b %Y}', 8), (tr, f'trough {s[tr]:.1f}\n{tr:%d %b %Y}', -26)]:
        ax.plot(d, s[d], 'v' if dy < 0 else '^', color=IDAred, ms=5)
        ax.annotate(lab, (d, s[d]), xytext=(0, dy), textcoords='offset points', ha='center', fontsize=7, color='black')
    ax.annotate(f'{s.iloc[-1]:.1f}\n{s.index[-1]:%d %b %Y}', (s.index[-1], s.iloc[-1]), xytext=(4, 0),
                textcoords='offset points', ha='left', va='center', fontsize=7, color='black')
    ax.set_xlim(s.index[0], pd.Timestamp('2027-10-01'))
    ax.set_ylabel('bn USD'); ax.set_ylim(0, 370)
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_b4_supply')


def b4x():
    raw = load('Stablecoins', start='2020-01-01').pipe(lambda x: x[x > 0])
    g = np.log(raw).diff().dropna(); n, L = len(g), 8

    def hac_break(k):
        X = sm.add_constant(np.r_[np.zeros(k), np.ones(n - k)])
        return sm.OLS(g.values, X).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    k0 = int((g.index < '2022-05-09').sum()); f0 = hac_break(k0)
    W_ = {k: hac_break(k).tvalues[1] ** 2 for k in range(int(0.15 * n), int(0.85 * n))}; kh = max(W_, key=W_.get)
    ssr = {k: ((g.values[:k] - g.values[:k].mean()) ** 2).sum() + ((g.values[k:] - g.values[k:].mean()) ** 2).sum() for k in W_}
    kl = min(ssr, key=ssr.get)
    fit = sm.OLS(g.values, sm.add_constant(np.r_[np.zeros(kl), np.ones(n - kl)])).fit(); e = fit.resid - fit.resid.mean()
    lrv = e @ e / n + 2 * sum((1 - j / (L + 1)) * (e[j:] @ e[:-j]) / n for j in range(1, L + 1)); hw = 11 * lrv / fit.params[1] ** 2
    res = dict(n=n, first=str(g.index[0].date()), last=str(g.index[-1].date()),
               a=f0.params[0] * 365, b=f0.params[1] * 365, t=f0.tvalues[1], se_b=f0.bse[1] * 365,
               trim=[str(g.index[int(0.15 * n)].date()), str(g.index[int(0.85 * n) - 1].date())],
               supW=W_[kh], supW_date=str(g.index[kh].date()), pre_W=g.values[:kh].mean() * 365, post_W=g.values[kh:].mean() * 365,
               ls_date=str(g.index[kl].date()), pre_ls=g.values[:kl].mean() * 365, post_ls=g.values[kl:].mean() * 365,
               hw=hw, bai=[str(g.index[int(kl - hw)].date()), str(g.index[int(kl + hw)].date())],
               var_ratio=fit.resid[:kl].var() / fit.resid[kl:].var(), W_terra=W_[k0] if k0 in W_ else f0.tvalues[1] ** 2)
    OUT['B4x'] = res
    ks = np.array(sorted(W_)); dates = g.index[ks]
    fig, axes = plt.subplots(2, 1, figsize=(W, 2.8), sharex=True, gridspec_kw={'height_ratios': [1, 1]})
    gm = g.rolling(30).mean() * 365
    axes[0].plot(gm.index, gm, color=Forest, lw=0.8, label='30-day mean of daily log growth x 365')
    axes[0].hlines(res['pre_ls'], g.index[0], g.index[kl], color=MainBlue, lw=1.4, label='Fitted drift (least-squares break)')
    axes[0].hlines(res['post_ls'], g.index[kl], g.index[-1], color=MainBlue, lw=1.4)
    axes[0].set_ylabel('Log growth / year'); axes[0].set_ylim(-1.5, 6)
    axes[1].plot(dates, [W_[k] for k in ks], color=IDAred, lw=1.0, label='HAC Wald statistic (L = 8)')
    axes[1].axhline(8.85, color=Gray, lw=0.8, ls='--', label='Andrews 5% critical value 8.85')
    ax2 = axes[1].twinx(); ax2.plot(dates, [ssr[k] for k in ks], color=Purple, lw=1.0, label='Sum of squared residuals (right)')
    ax2.spines['right'].set_visible(True); ax2.set_yticks([])
    axes[1].set_ylabel('Wald')
    for ax in axes:
        for d, c, ls in [(pd.Timestamp('2022-05-09'), 'black', ':'), (g.index[kh], IDAred, '--'), (g.index[kl], Purple, '--')]:
            ax.axvline(d, color=c, ls=ls, lw=0.9)
    axes[0].annotate('Terra, 9 May 2022', (pd.Timestamp('2022-05-09'), 5.2), xytext=(3, 0), textcoords='offset points',
                     fontsize=7, color='black')
    h0, l0 = axes[0].get_legend_handles_labels(); h1, l1 = axes[1].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    axes[0].set_title('Stablecoin supply growth: known date (Terra) vs searched break dates', loc='left', fontsize=8.5)
    extra = [plt.Line2D([], [], color=IDAred, ls='--', lw=0.9), plt.Line2D([], [], color=Purple, ls='--', lw=0.9)]
    bottom_legend(fig, ncol=3, handles=h0 + h1 + h2 + extra,
                  labels=l0 + l1 + l2 + ['sup-Wald date', 'Least-squares date'], fontsize=7)
    save_fig('ch0_sem_b4x_break')


# =============================================================================
# B5: BET-TR in RON si in EUR
# =============================================================================
def b5_data():
    return np.log(pd.concat([load('BET-TR', start='2015-01-05'), load('EUR/RON', start='2015-01-01')], axis=1,
                            keys=['p', 's']).dropna()).diff().dropna()


def b5():
    lv = pd.concat([load('BET-TR', start='2015-01-05'), load('EUR/RON', start='2015-01-01')], axis=1, keys=['p', 's']).dropna()
    eur = lv['p'] / lv['s']; Y = (lv.index[-1] - lv.index[0]).days / 365.25
    d = b5_data(); q = len(d) / Y
    L = nw_lags(len(d))
    ex = lv.loc['2025-08-13']
    res = dict(first=str(lv.index[0].date()), last=str(lv.index[-1].date()), n=len(d), Y=Y, q=q,
               p0=lv['p'].iloc[0], p1=lv['p'].iloc[-1], s0=lv['s'].iloc[0], s1=lv['s'].iloc[-1],
               mult_ron=lv['p'].iloc[-1] / lv['p'].iloc[0], mult_eur=eur.iloc[-1] / eur.iloc[0],
               cagr_ron=(lv['p'].iloc[-1] / lv['p'].iloc[0]) ** (1 / Y) - 1, cagr_eur=(eur.iloc[-1] / eur.iloc[0]) ** (1 / Y) - 1,
               vol_ron=d.p.std() * np.sqrt(q), vol_eur=(d.p - d.s).std() * np.sqrt(q), corr=d.p.corr(d.s),
               var_ron=d.p.var() * q, var_s=d.s.var() * q, cov2=-2 * d.p.cov(d.s) * q, var_eur=(d.p - d.s).var() * q,
               drift_log=np.log(lv['s'].iloc[-1] / lv['s'].iloc[0]) / Y,
               example=dict(date='2025-08-13', p=ex['p'], s=ex['s'], eur=ex['p'] / ex['s']), L=L,
               b5_notebook_252=dict(vol_ron=d.p.std() * np.sqrt(252), vol_eur=(d.p - d.s).std() * np.sqrt(252)))
    b = sm.OLS(d.p.values, sm.add_constant(d.s.values)).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    m = sm.OLS(d.s.values, np.ones(len(d))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    res.update(slope=b.params[1], slope_t=b.tvalues[1], slope_p=b.pvalues[1], drift=m.params[0] * q, drift_se=m.bse[0] * q,
               drift_t=m.tvalues[0], drift_p=m.pvalues[0],
               drift_ci=[(m.params[0] - 1.96 * m.bse[0]) * q, (m.params[0] + 1.96 * m.bse[0]) * q])
    OUT['B5'] = res
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.1), gridspec_kw={'width_ratios': [1.45, 1]})
    axes[0].plot(lv.index, lv['p'] / lv['p'].iloc[0], color=MainBlue, lw=0.9, label=f"BET-TR in RON (x{res['mult_ron']:.2f})")
    axes[0].plot(eur.index, eur / eur.iloc[0], color=IDAred, lw=0.9, label=f"BET-TR in EUR (x{res['mult_eur']:.2f})")
    log_axis(axes[0], [1, 2, 4, 8, 12])
    axes[0].set_ylabel('Growth of 1 unit (log)')
    axes[0].set_title('BET-TR, common days, 2015-2026', loc='left', fontsize=8.5)
    comps = [res['var_ron'], res['var_s'], res['cov2'], res['var_eur']]
    labs = ['Var($r^{RON}$)', 'Var($\\Delta s$)', '$-2$Cov', 'Var($r^{EUR}$)']
    bars = axes[1].bar(labs, comps, color=[MainBlue, Amber, Purple, IDAred], width=0.6)
    for b_, v in zip(bars, comps):
        axes[1].annotate(f'{v:.4f}', (b_.get_x() + b_.get_width() / 2, v), xytext=(0, 2), textcoords='offset points',
                         ha='center', fontsize=7.2)
    axes[1].set_ylim(0, 0.029); axes[1].tick_params(axis='x', labelsize=7.2)
    axes[1].set_title('Annualised variances (decimal)', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=2)
    save_fig('ch0_sem_b5_currency')


# =============================================================================
# B6 extins: prag Hampel calibrat
# =============================================================================
def b6x(wd, bnr, flagged):
    rows = {c: hampel_flags(bnr, c).mean() for c in [3, 5, 10, 20]}
    b_med = pd.Series([np.median(bnr.values[max(0, t - 5):t + 6]) for t in range(len(bnr))], index=bnr.index)
    b_mad = pd.Series([np.median(np.abs(bnr.values[max(0, t - 5):t + 6] - b_med.iloc[t])) for t in range(len(bnr))], index=bnr.index)
    grid = np.arange(1, 60, 0.5); best = {}; curves = {}
    for floor in [0.0, 0.01, 0.02, 0.03]:
        rates = np.array([hampel_flags(bnr, c, floor).mean() for c in grid])
        curves[floor] = rates
        ok = grid[rates <= 0.001]; best[floor] = float(ok[0]) if len(ok) else None
    vol = lambda x: np.log(x).diff().dropna().std() * np.sqrt(obs_per_year(x))
    applied = {}
    for floor in [0.0, 0.01]:
        fl = hampel_flags(wd, best[floor], floor)
        applied[floor] = dict(c=best[floor], flagged=int(fl.sum()), common=len(set(wd.index[fl]) & set(flagged)),
                              vol=vol(wd[~fl]), kept_2022=bool(not fl.get(pd.Timestamp('2022-08-09'), False)))
    # fereastra lucrata: 11 cotatii in jurul 13 aug. 2025
    t = wd.index.get_loc(pd.Timestamp('2025-08-13')); w = wd.iloc[t - 5:t + 6]
    med = np.median(w.values); mad = np.median(np.abs(w.values - med))
    t2 = wd.index.get_loc(pd.Timestamp('2022-08-09')); w2 = wd.iloc[t2 - 5:t2 + 6]
    med2 = np.median(w2.values); mad2 = np.median(np.abs(w2.values - med2))
    OUT['B6x'] = dict(rows=rows, n_bnr=len(bnr), mad_small=(b_mad < 0.001).mean(), mad_zero=(b_mad == 0).mean(),
                      max_dev_bnr=(bnr - b_med).abs().max(), best=best,
                      best_rate={f: float(curves[f][grid == best[f]][0]) for f in best}, applied=applied,
                      window=dict(values=[round(v, 4) for v in w.values], dates=[str(d.date()) for d in w.index], med=med,
                                  mad=mad, x=wd.iloc[t], thr11=11 * 1.4826 * mad),
                      window2022=dict(x=wd.iloc[t2], med=med2, mad=mad2, thr11=11 * 1.4826 * mad2,
                                      dev=abs(wd.iloc[t2] - med2), bnr=bnr.asof(pd.Timestamp('2022-08-09'))))
    fig, ax = plt.subplots(figsize=(W, 1.95))
    for floor, c in zip([0.0, 0.01, 0.02, 0.03], [MainBlue, Forest, Amber, Purple]):
        ax.plot(grid, curves[floor], color=c, lw=1.2, label=f'floor {floor:.2f} RON (c* = {best[floor]:g})')
    ax.axhline(0.001, color=IDAred, lw=1.0, ls='--', label='Target: 0.1% of BNR days')
    ax.set_yscale('log'); ax.set_ylim(2e-4, 0.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.1%}' if v < 0.01 else f'{v:.0%}'))
    ax.set_xlim(1, 14); ax.set_xlabel('Hampel multiplier c'); ax.set_ylabel('BNR days flagged')
    ax.set_title('False-alarm rate on the BNR series, 2015-2026 (log scale; a zero rate is not drawn)', loc='left',
                 fontsize=8.2)
    bottom_legend(fig, ncol=3)
    save_fig('ch0_sem_b6x_calibration')


# =============================================================================
# B7, B8: studiu de eveniment, taxa bancara din decembrie 2018
# =============================================================================
def event(name, mkt):
    r = np.log(pd.concat([load(name, start='2017-01-01'), mkt], axis=1, keys=['i', 'm']).dropna()).diff().dropna()
    t0 = r.index.get_loc(pd.Timestamp('2018-12-19')); est, ev = r.iloc[t0 - 250:t0 - 10], r.iloc[t0:t0 + 6]
    X = np.column_stack([np.ones(len(est)), est['m']]); b = np.linalg.lstsq(X, est['i'], rcond=None)[0]
    sig = (est['i'] - X @ b).std(ddof=2); ar = ev['i'] - (b[0] + b[1] * ev['m']); L, T = len(ar), len(est)
    mb, Sxx = est['m'].mean(), ((est['m'] - est['m'].mean()) ** 2).sum()
    se0 = sig * np.sqrt(1 + 1 / T + (ev['m'].iloc[0] - mb) ** 2 / Sxx)
    seC = sig * np.sqrt(L + L ** 2 / T + (ev['m'].sum() - L * mb) ** 2 / Sxx)
    pv = lambda z: 2 * (1 - stats.t.cdf(abs(z), T - 2))
    # SE al CAR[0, tau] pentru fiecare tau (banda din grafic)
    se_path = [sig * np.sqrt(l + l ** 2 / T + (ev['m'].iloc[:l].sum() - l * mb) ** 2 / Sxx) for l in range(1, L + 1)]
    wide = r.iloc[t0 - 10:t0 + 6]
    pred = b[0] + b[1] * wide['m']
    return dict(a=b[0], b=b[1], sig=sig, T=T, L=L, est_first=str(est.index[0].date()), est_last=str(est.index[-1].date()),
                ev_last=str(ev.index[-1].date()), mbar=mb, Smm=Sxx, ri=ev['i'].tolist(), rm=ev['m'].tolist(),
                pred=(b[0] + b[1] * ev['m']).tolist(), ar=ar.tolist(), car=ar.sum(), se0=se0, seC=seC,
                t0=ar.iloc[0] / se0, p0=pv(ar.iloc[0] / se0), tC=ar.sum() / seC, pC=pv(ar.sum() / seC),
                lev0=(ev['m'].iloc[0] - mb) ** 2 / Sxx, levC=(ev['m'].sum() - L * mb) ** 2 / Sxx,
                dates=[str(d.date()) for d in ev.index], se_path=se_path,
                sum_rm=ev['m'].sum()), wide, pred


def b7_b8():
    mkt = fetch_daily('BET', 'market', 'close', start='2017-01-01')
    tlv, wide, pred = event('Banca Transilvania', mkt)
    brd, wide2, pred2 = event('BRD', mkt)
    OUT['B7'] = tlv; OUT['B8'] = brd
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.15), gridspec_kw={'width_ratios': [1.3, 1]})
    k = np.arange(-10, 6)
    axes[0].plot(k, wide['i'].values, 'o-', color=MainBlue, lw=0.9, ms=3, label='Banca Transilvania, observed')
    axes[0].plot(k, pred.values, 's--', color=Amber, lw=0.9, ms=3, label='Market-model prediction $\\hat a + \\hat b\\,r_{m,t}$')
    axes[0].plot(k, wide['m'].values, '^-', color=Forest, lw=0.7, ms=3, label='BET (market)')
    axes[0].axvline(0, color=IDAred, lw=0.8, ls=':')
    axes[0].axvspan(-0.5, 5.5, color=IDAred, alpha=0.06, lw=0)
    fmt_pct(axes[0]); axes[0].set_xlabel('Trading day relative to 19 Dec 2018'); axes[0].set_ylabel('Log return')
    axes[0].set_title('Returns around the event', loc='left', fontsize=8.5)
    for res, c, lab in [(tlv, MainBlue, 'Banca Transilvania'), (brd, Purple, 'BRD')]:
        car = np.cumsum(res['ar']); se = np.array(res['se_path'])
        axes[1].plot(range(6), car, 'o-', color=c, lw=1.2, ms=3.5, label=f'CAR, {lab}')
        axes[1].fill_between(range(6), car - 1.96 * se, car + 1.96 * se, color=c, alpha=0.12, lw=0)
    axes[1].axhline(0, color=Gray, lw=0.6)
    fmt_pct(axes[1]); axes[1].set_xlabel('Event day $\\tau$'); axes[1].set_ylabel('CAR[0, $\\tau$]')
    axes[1].set_title('CAR with $\\pm 1.96$ SE bands', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=3, fontsize=7.2)
    save_fig('ch0_sem_b7_event')


# =============================================================================
# C3: investitii pasive si elasticitatea cererii (simulare)
# =============================================================================
def c3_run(seed, chi=2.97, K=2000, N=40, mode='rep'):
    """Simulated cross-section: K stocks, N active investors each; A_k = active share of stock k (fraction of all shares),
    w_ik = holdings of investor i in stock k as a fraction of all shares (sum_i w_ik = A_k),
    E_agg,k = sum_i w_ik Ebar_ik / (1 + chi A_k) (footnote 53); a fraction f_k of A_k turns passive under a rule."""
    rng = np.random.default_rng(seed)
    A = rng.uniform(0.55, 0.85, K); f = rng.uniform(0, 0.2, K)
    dlE, dlA, pt, E0s = np.empty(K), np.empty(K), np.empty(K), np.empty(K)
    for k in range(K):
        s = rng.dirichlet(np.ones(N)) * A[k]; e = np.exp(np.log(1.6) + 0.6 * rng.standard_normal(N))
        E0 = (s * e).sum() / (1 + chi * A[k]); target = f[k] * A[k]
        if mode == 'rep':
            sw = f[k] * s
        else:
            order = np.argsort(-e) if mode == 'high' else np.argsort(e)
            sw = np.zeros(N); rem = target
            for i in order:
                x = min(s[i], rem); sw[i] = x; rem -= x
                if rem <= 1e-15:
                    break
        A1 = A[k] - sw.sum(); E1 = ((s - sw) * e).sum() / (1 + chi * A1)
        dlE[k] = np.log(E1 / E0); dlA[k] = np.log(A1 / A[k]); pt[k] = 1 / (1 + chi * A[k]); E0s[k] = E0
    X = np.c_[np.ones(K), dlA]; b = np.linalg.lstsq(X, dlE, rcond=None)[0]
    return b[1], pt.mean(), E0s.mean()


def c3():
    res = {}
    for chi in (2.97, 0.0):
        for mode in ('rep', 'high', 'low'):
            out = [c3_run(s, chi=chi, mode=mode) for s in range(1, 11)]
            bs = [o[0] for o in out]
            res[f'{chi}_{mode}'] = dict(mean=np.mean(bs), min=np.min(bs), max=np.max(bs), theory=out[0][1])
    res['E_level_seed1'] = c3_run(1, chi=2.97)[2]
    # exemplul cu doi investitori
    s = np.array([0.4, 0.3]); e = np.array([1.0, 3.0]); chi = 2.97; A = s.sum()
    E0 = (s * e).sum() / (1 + chi * A)
    ex = dict(A=A, E0=E0)
    for lab, sw in [('rep', 0.1 / A * s), ('high', np.array([0.0, 0.1])), ('low', np.array([0.1, 0.0]))]:
        A1 = A - sw.sum(); E1 = ((s - sw) * e).sum() / (1 + chi * A1)
        ex[lab] = dict(A1=A1, E1=E1, dlogE=np.log(E1 / E0), dlogA=np.log(A1 / A))
    res['example'] = ex
    OUT['C3'] = res
    fig, ax = plt.subplots(figsize=(W, 1.95))
    modes = [('rep', 'Representative switchers'), ('high', 'Most elastic first'), ('low', 'Least elastic first')]
    xx = np.arange(3)
    for k, (chi, c) in enumerate([(2.97, MainBlue), (0.0, IDAred)]):
        m = [res[f'{chi}_{md}']['mean'] for md, _ in modes]
        lo = [m_ - res[f'{chi}_{md}']['min'] for m_, (md, _) in zip(m, modes)]
        hi = [res[f'{chi}_{md}']['max'] - m_ for m_, (md, _) in zip(m, modes)]
        bb = ax.bar(xx + (k - 0.5) * 0.34, m, 0.32, color=c, alpha=0.8,
                    label=f'$\\chi$ = {chi:g}: mean slope over seeds 1-10 (min-max bar)')
        ax.errorbar(xx + (k - 0.5) * 0.34, m, yerr=[lo, hi], fmt='none', ecolor='black', capsize=2, lw=0.8)
        for b_, v in zip(bb, m):
            ax.annotate(f'{v:.2f}', (b_.get_x() + b_.get_width() / 2, v), xytext=(0, 3 if v >= 0 else -9),
                        textcoords='offset points', ha='center', fontsize=7.2)
        ax.axhline(res[f'{chi}_rep']['theory'], color=c, ls='--', lw=1.0,
                   label=f"eq. (27) pass-through, $\\chi$ = {chi:g}: {res[f'{chi}_rep']['theory']:.3f}")
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(xx); ax.set_xticklabels([m_[1] for m_ in modes])
    ax.set_ylabel('Slope'); ax.set_ylim(-0.5, 2.6)
    ax.set_title('Slope of $\\Delta\\log E_{agg,k}$ on $\\Delta\\log A_k$ across 2,000 simulated stocks', loc='left', fontsize=8.5)
    bottom_legend(fig, ncol=2, fontsize=7.2)
    save_fig('ch0_sem_c3_slopes')


# =============================================================================
# MAIN
# =============================================================================
def to_json(o):
    if isinstance(o, dict):
        return {str(k): to_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_json(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return o


if __name__ == '__main__':
    only = set(sys.argv[1:])
    path = os.path.join(HERE, 'seminar0_results.json')
    if only and os.path.exists(path):
        OUT.update(json.load(open(path)))
    run = lambda k: not only or k in only
    if run('A'):
        a1_a2(); setup_preview()
    if run('B6'):
        m, bnr, wd, flagged = b6()
        if run('B6x') or not only:
            b6x(wd, bnr, flagged)
    if run('B1') or run('boot') or run('B3'):
        assets, carried = assets_b1()
        b1(assets, carried)
        eq, btc, tlt, cb, weekly, sb = b3()
        a7_a9(eq, btc)
        if run('boot'):
            bootstraps(assets, cb, weekly, sb)
    if run('B2'):
        b2(); b2x()
    if run('C2'):
        c2()
    if run('Aext'):
        a5(); a6(); a8()
    if run('B4'):
        b4(); b4x()
    if run('B5'):
        b5()
    if run('B7'):
        b7_b8()
    if run('C3'):
        c3()
    json.dump(to_json(OUT), open(path, 'w'), indent=1)
    print('wrote', path)

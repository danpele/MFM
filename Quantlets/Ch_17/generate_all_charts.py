"""
Generator pentru toate graficele si cifrele din Capitolul 17: bule si crahuri
============================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date: data/market (Nasdaq 100, S&P 500, BET, BET-FI, Bitcoin, Ethereum, Dogecoin, NVIDIA, Cisco, Tesla, GameStop,
Strategy); S&P Composite lunar din 1871 (datele publice ale lui Robert J. Shiller); 49 de industrii americane
(Kenneth French Data Library).
Teste de explozivitate: ADF la dreapta, SADF (Phillips-Wu-Yu 2011), GSADF si BSADF (Phillips-Shi-Yu 2015),
fara lag-uri, fereastra minima r0 = 0.01 + 1.8/sqrt(T), valori critice Monte Carlo (2000 de replici).
Cifrele sunt salvate in ch17_results.json (folosite de generatoarele de slide-uri).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import MARKETS, LABELS, price, shiller, industries, industry_firms   # noqa: E402
from bubbles import (psy, psy_cv, wild_cv, episodes, adf_stat, min_window, blanchard_watson, evans_bubble,  # noqa: E402
                     lppls_fit, lppls_path, lppls_qualified, lppls_conditions, lomb_pvalue, lppls_confidence, drawdown,
                     LPPLS_WINDOWS, LPPLS_STEP, LPPLS_FILTER, LPPLS_SEARCH)

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

# Course colours
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
Magenta  = '#D63384'
Brown    = '#795548'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
R_MC = 2000            # Monte Carlo replications for the critical values
RECOMPUTE = os.environ.get('MFM_CH17_RECOMPUTE', '1') == '1'   # True: recompute the LPPLS indicators (tens of minutes); False: use the precomputed values
QL_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/Quantlets/Ch_17/'


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


def fig_legend(fig, axes, ncol=3, y=0.0):
    """One legend for a multi-panel figure, below the figure."""
    h, l = [], []
    for ax in np.atleast_1d(axes):
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l and not ll.startswith('_'):
                h.append(hh)
                l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    if isinstance(o, pd.Timestamp):
        return str(o.date())
    return o


def yrs(idx):
    """Date -> decimal years."""
    idx = pd.DatetimeIndex(idx)
    return np.asarray(idx.year + (idx.dayofyear - 1) / 365.25)


def todate(x):
    """Ani zecimali -> data."""
    y = int(np.floor(x))
    return pd.Timestamp(f'{y}-01-01') + pd.Timedelta(days=float((x - y) * 365.25))


def d2s(d):
    return None if d is None else str(pd.Timestamp(d).date())


# =============================================================================
# 1. SIMULATED RATIONAL BUBBLES (Blanchard-Watson; Evans)
# =============================================================================
def fig_rational_bubble():
    """Price = fundamental value (random-walk dividends, r = 1% per period) + a rational bubble that collapses
    and restarts at a positive value, in the Evans (1991) form: with probability pi = 0.97 it survives,
    B_t = [b0 + (1+r)/pi * (B_{t-1} - b0/(1+r))] u_t; otherwise B_t = b0 u_t, with E[u_t] = 1 exactly.
    The term -b0/(1+r) pays for the restart, so E_{t-1}[B_t] = (1+r) B_{t-1} exactly."""
    rng = np.random.default_rng(48)
    T, r, pi, b0, su = 400, 0.01, 0.97, 5.0, 0.03
    D = 1 + np.cumsum(0.01 * rng.standard_normal(T))
    F = D / r                                           # E_t sum D_{t+i}/(1+r)^i with random-walk dividends
    Bb = np.empty(T)
    Bb[0] = b0
    alive = rng.random(T) < pi
    u = np.exp(rng.normal(-su ** 2 / 2, su, T))         # lognormal with E[u] = 1 exactly
    for t in range(1, T):
        Bb[t] = (b0 + (1 + r) / pi * (Bb[t - 1] - b0 / (1 + r))) * u[t] if alive[t] else b0 * u[t]
    Pp = F + Bb
    collapses = int(sum(1 for t in range(1, T) if not alive[t] and Bb[t - 1] > 25))   # visible collapses (bubble > 25)
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(Pp, color=MainBlue, lw=1.0, label='Price = fundamental value + bubble')
    ax.plot(F, color=Forest, lw=1.2, label='Fundamental value $D_t / r$')
    ax.set_xlabel('Period')
    ax.set_ylabel('Price')
    ax.set_title('Simulated rational bubble (Evans form): survives with probability 0.97, restarts at a small positive value',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    save_fig('ch17_rational_bubble')
    return dict(T=T, r=r, pi=pi, b0=b0, growth=(1 + r) / pi - 1, life=1 / (1 - pi), collapses=collapses,
                max_share=float(np.max(Bb / Pp)), max_mult=float(np.max(Pp / F)))


def fig_evans():
    """Evans (1991) periodically collapsing bubble: full-sample ADF vs GSADF / BSADF."""
    T = 400
    B = evans_bubble(T=T, seed=11)
    rng = np.random.default_rng(5)
    D = 1 + np.cumsum(0.02 * rng.standard_normal(T))
    Pp = np.abs(D) / 0.02 + 20 * B
    y = np.log(Pp)
    res = psy(y)
    cv = psy_cv(res['n'], res['w0'], R_MC, SEED)
    L = int(np.ceil(np.log(res['n'])))
    ep = episodes(res['bsadf'], cv['bsadf95'], np.arange(1, T), L)
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True, gridspec_kw=dict(height_ratios=[1.2, 1]))
    axes[0].plot(Pp, color=MainBlue, lw=0.9, label='Simulated price with a periodically collapsing bubble')
    axes[0].set_ylabel('Price')
    axes[1].plot(np.arange(1, T), res['bsadf'], color=IDAred, lw=0.9, label='BSADF statistic')
    axes[1].plot(np.arange(1, T), cv['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% critical value (Monte Carlo)')
    for s, e, _ in ep:
        for ax in axes:
            ax.axvspan(s, e if e is not None else T, color=Amber, alpha=0.25, lw=0)
    axes[1].set_xlabel('Period')
    axes[1].set_ylabel('BSADF')
    axes[0].set_title('Evans (1991) bubble: collapses make the full-sample unit-root test look stationary',
                      fontsize=9, loc='left')
    fig.tight_layout()
    axes[1].fill_between([], [], color=Amber, alpha=0.25, label='Date-stamped explosive periods')
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_evans')
    return dict(adf=res['adf'], sadf=res['sadf'], gsadf=res['gsadf'], cv_adf=cv['adf']['95'],
                cv_sadf=cv['sadf']['95'], cv_gsadf=cv['gsadf']['95'], n_episodes=len(ep), w0=res['w0'], T=T)


# =============================================================================
# 2. HISTORICAL EPISODES IN THE DATA
# =============================================================================
EPISODES = [  # (key, label, window in which the peak is searched)
    ('ndx', 'Nasdaq 100, 2000', ('1999-01-01', '2000-12-31')),
    ('csco', 'Cisco, 2000', ('1999-01-01', '2000-12-31')),
    ('bet', 'BET, 2007', ('2006-01-01', '2008-06-30')),
    ('btc', 'Bitcoin, 2017', ('2017-06-01', '2018-03-31')),
    ('eth', 'Ethereum, 2018', ('2017-06-01', '2018-06-30')),
    ('btc', 'Bitcoin, 2021', ('2021-06-01', '2022-03-31')),
    ('doge', 'Dogecoin, 2021', ('2021-01-01', '2021-12-31')),
    ('gme', 'GameStop, 2021', ('2021-01-01', '2021-06-30')),
    ('tsla', 'Tesla, 2021', ('2021-06-01', '2022-06-30')),
]


def episode_table():
    """Peak, 2-year run-up before the peak, maximum drawdown, trough and recovery."""
    rows = []
    for k, lab, (a, b) in EPISODES:
        p = price(k, 'D')
        pk = p.loc[a:b].idxmax()
        pre = p.loc[:pk]
        start = pre.index[pre.index.searchsorted(pk - pd.DateOffset(years=2))]
        post = p.loc[pk:]
        dd = post / post.iloc[0] - 1
        tr = dd.loc[:pk + pd.DateOffset(years=4)].idxmin()
        rec = post.loc[tr:][post.loc[tr:] >= post.iloc[0]]
        rows.append(dict(key=k, label=lab, peak=d2s(pk), peak_price=float(p.loc[pk]), runup2y=float(p.loc[pk] / p.loc[start] - 1),
                         trough=d2s(tr), maxdd=float(dd.loc[tr]), days_to_trough=int((tr - pk).days),
                         recovered=d2s(rec.index[0]) if len(rec) else None,
                         years_to_recover=float((rec.index[0] - pk).days / 365.25) if len(rec) else None))
    return rows


def fig_episodes(tab):
    """Episodes aligned at the peak: price normalised to 100 at the peak, +/- 2 calendar years."""
    cols = [MainBlue, Teal, IDAred, Amber, Purple, Orange, Forest, Magenta, Brown]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for (k, lab, _), row, c in zip(EPISODES, tab, cols):
        p = price(k, 'D')
        pk = pd.Timestamp(row['peak'])
        w = p.loc[pk - pd.DateOffset(years=2):pk + pd.DateOffset(years=2)]
        x = (w.index - pk).days / 365.25
        ax.plot(x, 100 * w.values / p.loc[pk], color=c, lw=0.9, label=lab)
    ax.set_yscale('log')
    ax.axvline(0, color=Gray, lw=0.6, ls=':')
    ax.axhline(100, color=Gray, lw=0.5)
    ax.set_xlabel('Years from the peak')
    ax.set_ylabel('Price, peak = 100 (log scale)')
    ax.set_title('Nine run-ups and crashes aligned at the peak', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch17_episodes')


# =============================================================================
# 3. BUBBLES FOR FAMA (Greenwood-Shleifer-You 2019) ON 49 INDUSTRIES
# =============================================================================
def gsy_sample():
    """Sample of Greenwood, Shleifer & You (2019), Section 2: the first 48 Fama-French industries (without 'Other'),
    industry-months with at least ten firms."""
    ind, mkt = industries()
    firms = industry_firms().reindex(ind.index)
    ind = ind.loc[:, [c for c in ind.columns if c.strip().lower() != 'other' and ind[c].notna().mean() > 0]]
    ok = firms.reindex(columns=ind.columns) >= 10
    return ind, mkt, ok


def gsy_events(thr, H=24, crash=0.40, H5=60, r5=0.50, r5_from='1931-01-01'):
    """GSY (2019, Section 2) run-ups: 2-year return above thr, raw and net of the market, and a 5-year raw return
    of at least 50% (imposed from 1931); first month of the run-up, no new episode in the same industry for 2 years;
    crash = a 40% fall from a previous peak within the next 2 years."""
    ind, mkt, ok = gsy_sample()
    Pm = (1 + mkt.reindex(ind.index)).cumprod()
    runm = Pm / Pm.shift(H) - 1
    rows = []
    for c in ind.columns:
        r = ind[c]
        valid = r.notna()
        p = (1 + r.fillna(0)).cumprod()
        run = p / p.shift(H) - 1
        run5 = p / p.shift(H5) - 1
        five = (run5 >= r5) | (ind.index < pd.Timestamp(r5_from))
        cond = ((run > thr) & ((run - runm) > thr) & five & ok[c] & valid & valid.shift(H, fill_value=False))
        last = None
        for i in np.where(cond.values)[0]:
            if (last is not None and i - last < H) or i + H >= len(p):
                continue
            fut = p.iloc[i:i + H + 1].values
            rows.append(dict(ind=c, date=p.index[i], run=float(run.iloc[i]),
                             mdd=float((fut / np.maximum.accumulate(fut) - 1).min()), ret2=float(fut[-1] / fut[0] - 1)))
            last = i
    d = pd.DataFrame(rows)
    d['crash'] = d['mdd'] <= -crash
    return d


def gsy_unconditional(H=24, crash=0.40):
    """Unconditional probability of a 40% fall within 2 years (all industry-months of the GSY sample)."""
    ind, _, ok = gsy_sample()
    hits, n, rets = 0, 0, []
    for c in ind.columns:
        r = ind[c]
        p = (1 + r.fillna(0)).cumprod().values
        v = (r.notna() & ok[c]).values
        for i in range(len(p) - H):
            if not v[i]:
                continue
            fut = p[i:i + H + 1]
            hits += (fut / np.maximum.accumulate(fut) - 1).min() <= -crash
            rets.append(fut[-1] / fut[0] - 1)
            n += 1
    return hits / n, float(np.mean(rets)), n


def cluster_boot(d, col, B=2000, seed=SEED):
    """95% bootstrap interval resampling calendar years (episodes in the same year are correlated)."""
    rng = np.random.default_rng(seed)
    g = {y: grp[col].values for y, grp in d.groupby(d['date'].dt.year)}
    keys = list(g)
    stats = []
    for _ in range(B):
        pick = rng.choice(len(keys), len(keys), replace=True)
        v = np.concatenate([g[keys[j]] for j in pick])
        stats.append(v.mean())
    return [float(np.quantile(stats, 0.025)), float(np.quantile(stats, 0.975))]


def fig_gsy():
    thrs = [0.5, 0.75, 1.0, 1.25, 1.5]
    pu, ru, nu = gsy_unconditional()
    out = dict(uncond_crash=pu, uncond_ret2=ru, n_months=nu, rows=[])
    for th in thrs:
        d = gsy_events(th)
        out['rows'].append(dict(thr=th, n=int(len(d)), n_ind=int(d['ind'].nunique()), crash=float(d['crash'].mean()),
                                crash_ci=cluster_boot(d, 'crash'), ret2=float(d['ret2'].mean()),
                                ret2_ci=cluster_boot(d, 'ret2'), first=d2s(d['date'].min()), last=d2s(d['date'].max())))
    R = pd.DataFrame(out['rows'])
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0))
    x = 100 * R['thr']
    lo = np.array([c[0] for c in R['crash_ci']])
    hi = np.array([c[1] for c in R['crash_ci']])
    axes[0].errorbar(x, 100 * R['crash'], yerr=[100 * (R['crash'] - lo), 100 * (hi - R['crash'])], fmt='o-',
                     color=IDAred, capsize=3, label='After a run-up (95% CI, bootstrap by year)')
    axes[0].axhline(100 * pu, color=MainBlue, ls='--', lw=1.0, label='All industry-months (unconditional)')
    axes[0].set_xlabel('Run-up threshold (%)')
    axes[0].set_ylabel('P(40% drawdown in next 2 years), %')
    lo = np.array([c[0] for c in R['ret2_ci']])
    hi = np.array([c[1] for c in R['ret2_ci']])
    axes[1].errorbar(x, 100 * R['ret2'], yerr=[100 * (R['ret2'] - lo), 100 * (hi - R['ret2'])], fmt='o-',
                     color=IDAred, capsize=3)
    axes[1].axhline(100 * ru, color=MainBlue, ls='--', lw=1.0)
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_xlabel('Run-up threshold (%)')
    axes[1].set_ylabel('Mean return over next 2 years, %')
    fig.suptitle('Bubbles for Fama, 48 US industries 1926-2026: two-year run-ups above the threshold, raw and net of the market',
                 fontsize=8.5, x=0.02, ha='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_gsy')
    return out


# =============================================================================
# 4. EXPLOSIVENESS TESTS: WINDOWS, NULL DISTRIBUTIONS, APPLICATIONS
# =============================================================================
def fig_windows():
    """Schema ferestrelor: ADF (toata selectia), SADF (inceput fix, sfarsit variabil), GSADF (ambele variabile)."""
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), sharey=True)
    specs = [('ADF: one window', [(0, 1)]),
             ('SADF: start fixed, end grows', [(0, e) for e in np.linspace(0.25, 1, 7)]),
             ('GSADF: start and end both move', [(s, e) for e in np.linspace(0.25, 1, 4) for s in np.linspace(0, e - 0.25, 3)])]
    for ax, (title, wins) in zip(axes, specs):
        for i, (s, e) in enumerate(wins):
            ax.plot([s, e], [i, i], color=MainBlue if 'ADF:' in title else (Forest if 'SADF:' in title else IDAred), lw=3,
                    solid_capstyle='butt')
        ax.axvline(0.25, color=Gray, lw=0.6, ls=':')
        ax.set_title(title, fontsize=8.5, loc='left')
        ax.set_xlim(-0.02, 1.02)
        ax.set_xticks([0, 0.25, 1])
        ax.set_xticklabels(['0', '$r_0$', '1'])
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.set_xlabel('Fraction of the sample')
    fig.tight_layout()
    save_fig('ch17_windows')


def fig_null(cv, T):
    """Null (random-walk) distributions of ADF, SADF and GSADF, with their 95% critical values."""
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for k, c, lab in [('adf', MainBlue, 'ADF'), ('sadf', Forest, 'SADF'), ('gsadf', IDAred, 'GSADF')]:
        v = cv['null'][k]
        ax.hist(v, bins=80, density=True, histtype='step', color=c, lw=1.2, label=f'{lab} (95% critical value {cv[k]["95"]:.2f})')
        ax.axvline(cv[k]['95'], color=c, ls='--', lw=0.8)
    ax.set_xlabel('Test statistic under a random walk')
    ax.set_ylabel('Density')
    ax.set_title(f'Null distributions, T = {T}, minimum window {cv["w0"]}, {cv["R"]} Monte Carlo paths', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.22)
    save_fig('ch17_null')


def run_psy(y, R=R_MC, wild=False):
    """Full PSY analysis of a log-level series y (pd.Series): statistics, critical values, date-stamped episodes."""
    res = psy(y.values)
    cv = psy_cv(res['n'], res['w0'], R, SEED)
    L = int(np.ceil(np.log(res['n'])))
    idx = y.index[1:]
    ep = episodes(res['bsadf'], cv['bsadf95'], idx, L)
    ep_pwy = episodes(res['fwd'], cv['fwd95'], idx, L)
    out = dict(res=res, cv=cv, L=L, idx=idx, ep=ep, ep_pwy=ep_pwy)
    if wild:
        wc = wild_cv(y.values, res['w0'], 1000, SEED)
        out['wild'] = wc
        out['ep_wild'] = episodes(res['bsadf'], wc['bsadf95'], idx, L)
    return out


def _chg(y, s, e):
    """Price change over the episode (from the start to the end of the signal): > 0 rise, < 0 collapse."""
    e = y.index[-1] if e is None else e
    return float(np.exp(y.loc[e] - y.loc[s]) - 1)


def summarise(o, y):
    """JSON-serialisable summary of a PSY analysis."""
    r, cv = o['res'], o['cv']
    out = dict(T=r['n'], w0=r['w0'], r0=r['r0'], L=o['L'], adf=r['adf'], sadf=r['sadf'], gsadf=r['gsadf'],
               cv_adf=cv['adf'], cv_sadf=cv['sadf'], cv_gsadf=cv['gsadf'], start=d2s(y.index[0]), end=d2s(y.index[-1]),
               episodes=[dict(start=d2s(s), end=d2s(e), n=int(n), change=_chg(y, s, e)) for s, e, n in o['ep']],
               episodes_pwy=[dict(start=d2s(s), end=d2s(e), n=int(n), change=_chg(y, s, e)) for s, e, n in o['ep_pwy']],
               first_window_end=d2s(o['idx'][r['w0'] - 1]))
    if 'wild' in o:
        out['cv_gsadf_wild'] = o['wild']['gsadf95']
        out['episodes_wild'] = [dict(start=d2s(s), end=d2s(e), n=int(n), change=_chg(y, s, e)) for s, e, n in o['ep_wild']]
    return out


def _shade(ax, ep, end, y=None, alpha=0.25):
    """Date-stamped episodes: rise (Amber) or accelerating fall (Teal)."""
    for s, e, _ in ep:
        up = True if y is None else _chg(y, s, e) > 0
        ax.axvspan(s, e if e is not None else end, color=Amber if up else Teal, alpha=alpha, lw=0)


def fig_psy(y, o, name, title, ylab, logscale=True, level=None, pwy=False, wild=False, level_label=None):
    """Two panels: the level of the series (with the date-stamped episodes) and BSADF against its 95% critical value."""
    idx = o['idx']
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.4), sharex=True, gridspec_kw=dict(height_ratios=[1.2, 1]))
    lv = np.exp(y) if level is None else level
    axes[0].plot(lv.index, lv.values, color=MainBlue, lw=0.9, label=level_label or 'Level')
    if logscale:
        axes[0].set_yscale('log')
    axes[0].set_ylabel(ylab)
    axes[1].plot(idx, o['res']['bsadf'], color=IDAred, lw=0.9, label='BSADF statistic')
    axes[1].plot(idx, o['cv']['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% critical value (Monte Carlo)')
    if wild:
        axes[1].plot(idx, o['wild']['bsadf95'], color=Purple, lw=1.0, ls='-.', label='95% critical value (wild bootstrap)')
    if pwy:
        axes[1].plot(idx, o['res']['fwd'], color=Teal, lw=0.8, label='Recursive ADF (start fixed, PWY)')
        axes[1].plot(idx, o['cv']['fwd95'], color=Orange, lw=0.9, ls=':', label='95% critical value of the recursive ADF')
    end = idx[-1]
    for ax in axes:
        _shade(ax, o['ep'], end, y)
    axes[1].set_ylabel('Statistic')
    axes[0].set_title(title, fontsize=9, loc='left')
    dirs = [_chg(y, s, e) > 0 for s, e, _ in o['ep']]
    if any(dirs):
        axes[1].fill_between([], [], color=Amber, alpha=0.25, label='Explosive episode, price rising')
    if not all(dirs):
        axes[1].fill_between([], [], color=Teal, alpha=0.25, label='Explosive episode, price falling')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig(name)


def real_time(o, p, win_years=2):
    """For each episode: first signal (real time), price peak within and after the episode, end of the signal."""
    rows = []
    for s, e, n in o['ep']:
        e2 = e if e is not None else p.index[-1]
        seg = p.loc[s:e2 + pd.DateOffset(months=6)]
        pk = seg.idxmax()
        rows.append(dict(start=d2s(s), end=d2s(e), peak=d2s(pk), lead_days=int((pk - s).days),
                         change=float(p.loc[:e2].iloc[-1] / p.loc[:s].iloc[-1] - 1),
                         gain_to_peak=float(p.loc[pk] / p.loc[:s].iloc[-1] - 1),
                         dd_after=float((p.loc[pk:pk + pd.DateOffset(years=win_years)].min()) / p.loc[pk] - 1),
                         signal_end_after_peak_days=None if e is None else int((e - pk).days)))
    return rows


def signal_vs_peak(o, p, window, gap_days, dd_years=2):
    """First signal of the group of episodes preceding the peak in the given window vs the peak.
    The start of the episode is dated in hindsight (first exceedance); in real time the episode is confirmed only after
    L = ceil(ln T) consecutive exceedances, i.e. at observation start + L - 1 of the tested series ('confirm')."""
    pk = p.loc[window[0]:window[1]].idxmax()
    ep = sorted([(s, e if e is not None else p.index[-1]) for s, e, _ in o['ep'] if s <= pk])
    i = len(ep) - 1
    while i > 0 and (ep[i][0] - ep[i - 1][1]).days <= gap_days:
        i -= 1
    first = ep[i][0]
    conf = o['idx'][o['idx'].get_loc(first) + o['L'] - 1]
    p0 = p.loc[:first].iloc[-1]
    return dict(first=d2s(first), peak=d2s(pk), lead_days=int((pk - first).days), lead_months=float((pk - first).days / 30.44),
                confirm=d2s(conf), lead_confirm_days=int((pk - conf).days), lead_confirm_months=float((pk - conf).days / 30.44),
                gain=float(p.loc[pk] / p0 - 1), gain_confirm=float(p.loc[pk] / p.loc[:conf].iloc[-1] - 1), dd_after=float(p.loc[pk:pk + pd.DateOffset(years=dd_years)].min() / p.loc[pk] - 1),
                signal_end=d2s(ep[-1][1]) if ep[-1][1] != p.index[-1] else None)


# =============================================================================
# 5. LPPLS
# =============================================================================
COND_LABELS = {'B': 'B < 0', 'm': 'm in [0.01, 0.99]', 'w': 'omega in [2, 25]', 'tc': 'tc in [t2, t2 + (t2-t1)/5]',
               'osc': 'oscillations >= 2.5', 'damping': 'damping >= 1', 'rel_err': 'max relative error <= 0.15',
               'lomb': 'Lomb test, 10% (cumulative)', 'ar1': 'residual unit root rejected, 10% (cumulative)'}


def fig_lppls_btc2017():
    """LPPLS fitted to Bitcoin 2017-01-01 .. 2017-11-15 and the observed path up to March 2018."""
    p = price('btc', 'D')
    t1, t2 = '2017-01-01', '2017-11-15'
    w = p.loc[t1:t2]
    f = lppls_fit(yrs(w.index), np.log(w.values))
    full = p.loc[t1:'2018-03-31']
    tt = yrs(full.index)
    mask = tt < f['tc']
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(full.index, full.values, color=MainBlue, lw=0.9, label='Bitcoin (USD, log scale)')
    ax.plot(full.index[mask], np.exp(lppls_path(f, tt[mask])), color=IDAred, lw=1.2, label='LPPLS fit on data up to 15 Nov 2017')
    ax.axvline(pd.Timestamp(t2), color=Gray, ls=':', lw=0.8)
    ax.axvline(todate(f['tc']), color=Orange, ls='--', lw=1.0, label=f"Estimated critical time $t_c$ = {todate(f['tc']).date()}")
    pk = p.loc['2017'].idxmax()
    ax.axvline(pk, color=Forest, ls='-.', lw=1.0, label=f'Actual peak {pk.date()}')
    ax.set_yscale('log')
    ax.set_ylabel('USD')
    ax.set_title('LPPLS on the 2017 Bitcoin bubble (search space of Shu and Zhu 2020, eq. 11)', fontsize=9, loc='left')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch17_lppls_btc2017')
    cond = lppls_conditions(f)
    out = {k: v for k, v in f.items() if not k.startswith('_')}
    out.update(tc_date=d2s(todate(f['tc'])), peak=d2s(pk), t1=t1, t2=t2, qualified=lppls_qualified(f), cond=cond,
               lomb_p=lomb_pvalue(f), n=int(len(w)))
    return out


def tc_path(key, t1, t2_from, t2_to, step_days=7):
    """tc estimated on windows [t1, t2] with a moving t2 (every step_days days)."""
    p = price(key, 'D')
    rows = []
    for t2 in pd.date_range(t2_from, t2_to, freq=f'{step_days}D'):
        w = p.loc[t1:t2]
        f = lppls_fit(yrs(w.index), np.log(w.values))
        rows.append(dict(t2=w.index[-1], tc=todate(f['tc']), m=f['m'], w=f['w'], q=lppls_qualified(f)))
    return pd.DataFrame(rows)


def fig_tc_instability():
    cases = [('btc', 'Bitcoin: window from 1 Jan 2017', '2017-01-01', '2017-08-01', '2018-01-15', ('2017-06-01', '2018-03-31')),
             ('ndx', 'Nasdaq 100: window from 8 Oct 1998', '1998-10-08', '1999-09-01', '2000-06-30', ('1999-06-01', '2000-12-31'))]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2))
    out = {}
    for ax, (k, title, t1, a, b, (pa, pb)) in zip(axes, cases):
        d = tc_path(k, t1, a, b)
        pk = price(k, 'D').loc[pa:pb].idxmax()
        ax.plot(d['t2'], d['tc'], 'o-', color=IDAred, ms=2.5, lw=0.8, label='Estimated critical time $t_c$')
        ax.plot(d['t2'], d['t2'], color=Gray, lw=0.6, ls=':', label='Date of the estimate ($t_c = t_2$)')
        ax.axhline(pk, color=Forest, ls='--', lw=1.0, label='Actual peak')
        ax.set_title(title, fontsize=8.5, loc='left')
        ax.set_xlabel('End of the estimation window $t_2$')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m'))
        ax.yaxis.set_major_formatter(mdates.DateFormatter('%y-%m'))
        ax.tick_params(axis='x', rotation=30, labelsize=7)
        err = (d['tc'] - pk).dt.days
        before = d['t2'] < pk
        out[k] = dict(peak=d2s(pk), n=int(len(d)), n_before=int(before.sum()),
                      mae_days=float(err[before].abs().mean()), med_err_days=float(err[before].median()),
                      min_tc=d2s(d.loc[before, 'tc'].min()), max_tc=d2s(d.loc[before, 'tc'].max()),
                      share_within_30=float((err[before].abs() <= 30).mean()), share_qualified=float(d.loc[before, 'q'].mean()))
    axes[0].set_ylabel('Estimated $t_c$')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig('ch17_tc_instability')
    return out


def _ci_worker(args):
    """All 141 windows for one t2: the indicator and the number of windows passing each condition."""
    t, y, i = args
    cnt = dict.fromkeys(COND_LABELS, 0)
    q, n = 0, 0
    for L in LPPLS_WINDOWS:
        if i - L < 0:
            continue
        f = lppls_fit(t[i - L:i + 1], y[i - L:i + 1])
        c = lppls_conditions(f)
        n += 1
        if c is None:
            continue
        for k, v in c.items():
            cnt[k] += v is True
        q += all(v is True for v in c.values())
    return q / n, cnt, n


def confidence_series(key, start, t2_from, step=LPPLS_STEP, procs=None):
    """LPPLS confidence indicator (Shu & Zhu 2020): t2 every 5 observations, 141 windows of 750 to 50 observations."""
    from multiprocessing import Pool
    p = price(key, 'D', start)
    t, y = yrs(p.index), np.log(p.values)
    i0 = int(p.index.searchsorted(pd.Timestamp(t2_from)))
    idx = np.arange(max(i0, max(LPPLS_WINDOWS)), len(p), step)
    with Pool(procs or max(1, (os.cpu_count() or 2) - 2)) as pool:
        res = pool.map(_ci_worker, [(t, y, i) for i in idx], chunksize=4)
    df = pd.DataFrame([dict(ci=r[0], n=r[2], **{f'pass_{k}': v for k, v in r[1].items()}) for r in res], index=p.index[idx])
    df.index.name = 'date'
    return df


def ci_evaluation(ci, p, horizon=90, fall=0.20):
    """Signal (indicator > 0) vs a fall of at least 20% below the current price within the next 90 days;
    only dates whose 90 calendar days are fully observed."""
    rows = []
    for d, v in ci.items():
        if d + pd.Timedelta(days=horizon) > p.index[-1]:
            continue
        fut = p.loc[d:d + pd.Timedelta(days=horizon)]
        rows.append(dict(date=d, ci=v, hit=bool(fut.min() / fut.iloc[0] - 1 <= -fall)))
    r = pd.DataFrame(rows)
    on, off = r[r.ci > 0], r[r.ci == 0]
    return dict(n=int(len(r)), n_on=int(len(on)), p_on=float(on.hit.mean()) if len(on) else None,
                p_off=float(off.hit.mean()), base=float(r.hit.mean()), horizon=horizon, fall=fall)


def get_ci(key, start, t2_from, fname):
    """Indicator table (ci and the windows passing each condition): recomputed or precomputed."""
    path = os.path.join(HERE, fname)
    if RECOMPUTE or not os.path.exists(path):
        confidence_series(key, start, t2_from).to_csv(path)
    return pd.read_csv(path if os.path.exists(path) else QL_RAW + fname, index_col=0, parse_dates=True)


def condition_shares(tab):
    """Share of windows (over all t2 dates) passing each condition, taken separately."""
    n = tab['n'].sum()
    return {k: float(tab[f'pass_{k}'].sum() / n) for k in COND_LABELS}


def fig_lppls_ci(tab_btc, tab_ndx):
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0), gridspec_kw=dict(height_ratios=[1.2, 1]))
    p = price('btc', 'D', '2015-01-01')
    ax = axes[0]
    ax.plot(p.index, p.values, color=MainBlue, lw=0.8, label='Bitcoin (USD, log scale)')
    ax.set_yscale('log')
    ax2 = ax.twinx()
    ax2.bar(tab_btc.index, tab_btc['ci'], width=6, color=IDAred, label='LPPLS confidence indicator (right axis)')
    ax2.set_ylim(0, 1)
    ax2.spines['right'].set_visible(True)
    ax.set_title('Bitcoin: LPPLS confidence indicator, 141 windows of 50-750 days, every 5 days', fontsize=9, loc='left')
    keys = list(COND_LABELS)
    sb, sn = condition_shares(tab_btc), condition_shares(tab_ndx)
    x = np.arange(len(keys))
    axes[1].bar(x - 0.2, [100 * sb[k] for k in keys], 0.4, color=Amber, label='Bitcoin, all windows')
    axes[1].bar(x + 0.2, [100 * sn[k] for k in keys], 0.4, color=Teal, label='Nasdaq 100, all windows')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([COND_LABELS[k] for k in keys], rotation=20, ha='right', fontsize=6.5)
    axes[1].set_ylabel('% of windows passing')
    fig.tight_layout()
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    h3, l3 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2 + h3, l1 + l2 + l3, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    save_fig('ch17_lppls_ci')


# =============================================================================
# 6. REGIME-SWITCHING MODELS (Hamilton 1989)
# =============================================================================
def ms_fit(key, start, freq='W', k=2):
    """Markov switching: regime-specific mean and variance, weekly log returns in %."""
    import statsmodels.api as sm
    p = price(key, freq, start)
    r = 100 * np.log(p).diff().dropna()
    np.random.seed(SEED)                              # random search over starting values: reproducible
    res = sm.tsa.MarkovRegression(r, k_regimes=k, trend='c', switching_variance=True).fit(search_reps=20, disp=False)
    hi = int(np.argmax([res.params[f'sigma2[{j}]'] for j in range(k)]))
    return p, r, res, hi


def ms_summary(res, hi, r, k=2):
    par = res.params
    se = res.bse
    lo = 1 - hi if k == 2 else None
    P = np.asarray(res.regime_transition)[:, :, 0]         # statsmodels stores P[i, j] = P(s_t = i | s_{t-1} = j)
    out = dict(n=int(len(r)), start=d2s(r.index[0]), end=d2s(r.index[-1]), llf=float(res.llf), aic=float(res.aic),
               bic=float(res.bic))
    for j, tag in [(lo, 'calm'), (hi, 'turb')]:
        out[tag] = dict(mu=float(par[f'const[{j}]']), mu_se=float(se[f'const[{j}]']),
                        sd=float(np.sqrt(par[f'sigma2[{j}]'])), stay=float(P[j, j]),
                        dur=float(res.expected_durations[j]), share=float(res.smoothed_marginal_probabilities[j].mean()))
    return out


def fig_ms(key, start, name, title):
    p, r, res, hi = ms_fit(key, start)
    fp = res.filtered_marginal_probabilities[hi]
    sp = res.smoothed_marginal_probabilities[hi]
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0), sharex=True, gridspec_kw=dict(height_ratios=[1.2, 1]))
    axes[0].plot(p.index, p.values, color=MainBlue, lw=0.8, label=f'{LABELS[key]} (log scale)')
    axes[0].set_yscale('log')
    axes[1].plot(fp.index, fp.values, color=IDAred, lw=0.7, label='Filtered probability (full-sample parameters)')
    axes[1].plot(sp.index, sp.values, color=Forest, lw=1.0, label='Smoothed probability (full sample)')
    axes[1].set_ylabel('P(turbulent regime)')
    axes[1].set_ylim(-0.02, 1.02)
    axes[0].set_title(title, fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig(name)
    out = ms_summary(res, hi, r)
    # filtered probability at the peaks and 3 months later
    return out, fp, sp


# =============================================================================
# 7. CRYPTO AND AI: TIMELINE OF EXPLOSIVE EPISODES (weekly data)
# =============================================================================
TIMELINE = ['btc', 'eth', 'doge', 'mstr', 'nvda', 'tsla', 'gme', 'ndx', 'sp500']   # each series from its own start


def fig_timeline():
    out = {}
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    cols = [Amber, Purple, Orange, Brown, Forest, Teal, Magenta, MainBlue, IDAred]
    for i, (k, c) in enumerate(zip(TIMELINE, cols)):
        y = np.log(price(k, 'W'))
        o = run_psy(y, R=1000)
        out[k] = summarise(o, y)
        for s, e, _ in o['ep']:
            e2 = e if e is not None else y.index[-1]
            if e2 < pd.Timestamp('2014-01-01') or _chg(y, s, e) <= 0:
                continue                                   # rising episodes only, 2014-2026
            ax.plot([max(s, pd.Timestamp('2014-01-01')), e2], [i, i], color=c, lw=7, solid_capstyle='butt')
        ax.plot([], [], color=c, lw=5, label=LABELS[k])
    ax.set_yticks(range(len(TIMELINE)))
    ax.set_yticklabels([LABELS[k] for k in TIMELINE], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(pd.Timestamp('2014-01-01'), pd.Timestamp('2026-10-01'))
    ax.set_title('Upward explosive episodes date-stamped by BSADF, weekly data, 2014-2026 window (each series tested on its full history)',
                 fontsize=8, loc='left')
    legend_outside_bottom(ax, ncol=5, y=-0.12)
    save_fig('ch17_timeline')
    return out


def fig_ai_dotcom():
    """Cisco (dot-com) vs NVIDIA (AI) and Nasdaq 100 1995 vs 2023: price = 100 at the start of the explosive episode (monthly)."""
    res = {}
    for k in ['csco', 'nvda', 'ndx']:
        y = np.log(price(k, 'M'))
        res[k] = (y, run_psy(y))
    # start of the first dot-com episode (Cisco, Nasdaq 100) and of the current episode (NVIDIA, Nasdaq 100)
    def first_after(o, date):
        return next(s for s, e, n in o['ep'] if s >= pd.Timestamp(date))
    starts = {'csco': first_after(res['csco'][1], '1995-01-01'), 'nvda': first_after(res['nvda'][1], '2023-01-01'),
              'ndx95': first_after(res['ndx'][1], '1995-01-01'), 'ndx23': first_after(res['ndx'][1], '2023-01-01')}
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
    out = {}
    for ax, pairs in zip(axes, [[('csco', 'csco', 'Cisco from ', Teal), ('nvda', 'nvda', 'NVIDIA from ', Forest)],
                                [('ndx', 'ndx95', 'Nasdaq 100 from ', MainBlue), ('ndx', 'ndx23', 'Nasdaq 100 from ', IDAred)]]):
        for k, sk, lab, c in pairs:
            p = np.exp(res[k][0])
            s = starts[sk]
            w = p.loc[s:s + pd.DateOffset(months=96)]
            m = np.arange(len(w))
            ax.plot(m, 100 * w.values / w.iloc[0], color=c, lw=1.1, label=f'{lab}{s:%b %Y}')
            out[sk] = dict(start=d2s(s), months=int(len(w) - 1), peak_mult=float(w.max() / w.iloc[0]),
                           months_to_peak=int(np.argmax(w.values)), last_mult=float(w.iloc[-1] / w.iloc[0]))
        ax.set_yscale('log')
        ax.axhline(100, color=Gray, lw=0.5)
        ax.set_xlabel('Months since the first explosive signal')
    axes[0].set_ylabel('Price, first signal = 100 (log scale)')
    axes[0].set_title('Stocks: dot-com vs AI', fontsize=8.5, loc='left')
    axes[1].set_title('Nasdaq 100: 1990s vs 2020s', fontsize=8.5, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_ai_dotcom')
    for k in ['csco', 'nvda', 'ndx']:
        out[f'psy_{k}'] = summarise(res[k][1], res[k][0])
    return out


# =============================================================================
# MAIN
# =============================================================================
def main():
    RES = {}
    RES['rational'] = fig_rational_bubble()
    RES['evans'] = fig_evans()
    tab = episode_table()
    RES['episodes'] = tab
    fig_episodes(tab)
    RES['gsy'] = fig_gsy()
    fig_windows()
    # Shiller P/D, from 1871 to the latest month available
    sh = shiller()
    y_pd = np.log(sh['PD'])
    o_pd = run_psy(y_pd, R=1000)
    RES['sp_pd'] = summarise(o_pd, y_pd)
    RES['sp_pd']['pd_last'] = float(sh['PD'].iloc[-1])
    RES['sp_pd']['pd_mean'] = float(sh['PD'].mean())
    RES['sp_pd']['pd_max'] = float(sh['PD'].max())
    RES['sp_pd']['pd_max_date'] = d2s(sh['PD'].idxmax())
    RES['sp_pd']['pd_max_dotcom'] = float(sh['PD'].loc['1995':'2002'].max())
    RES['sp_pd']['pd_max_dotcom_date'] = d2s(sh['PD'].loc['1995':'2002'].idxmax())
    fig_psy(y_pd, o_pd, 'ch17_sp_pd', f'S&P Composite real price-dividend ratio, monthly {sh.index[0].year}-{sh.index[-1].year}',
            'Price / dividend (log scale)', level=sh['PD'], level_label='Real price-dividend ratio')
    # Nasdaq 100 monthly (with PWY date-stamping) and the null distributions for T = 440
    y_ndx = np.log(price('ndx', 'M'))
    o_ndx = run_psy(y_ndx)
    RES['ndx'] = summarise(o_ndx, y_ndx)
    RES['ndx']['real_time'] = real_time(o_ndx, price('ndx', 'D'))
    fig_psy(y_ndx, o_ndx, 'ch17_ndx', 'Nasdaq 100, monthly 1990-2026: GSADF date-stamping vs the recursive ADF (PWY)',
            'Index (log scale)', pwy=True, level_label='Nasdaq 100')
    fig_null(o_ndx['cv'], o_ndx['res']['n'])
    # Bitcoin weekly (MC and wild bootstrap)
    y_btc = np.log(price('btc', 'W'))
    o_btc = run_psy(y_btc, wild=True)
    RES['btc'] = summarise(o_btc, y_btc)
    RES['btc']['real_time'] = real_time(o_btc, price('btc', 'D'))
    fig_psy(y_btc, o_btc, 'ch17_btc', 'Bitcoin, weekly 2014-2026', 'USD (log scale)', level_label='Bitcoin')
    # BET monthly 1997-2026
    y_bet = np.log(price('bet', 'M'))
    o_bet = run_psy(y_bet)
    RES['bet'] = summarise(o_bet, y_bet)
    RES['bet']['real_time'] = real_time(o_bet, price('bet', 'D'))
    fig_psy(y_bet, o_bet, 'ch17_bet', 'BET index, monthly 1997-2026', 'Index points (log scale)', level_label='BET')
    # GameStop daily 2020-2021
    y_gme = np.log(price('gme', 'D', '2020-01-01', '2021-12-31'))
    o_gme = run_psy(y_gme)
    RES['gme'] = summarise(o_gme, y_gme)
    RES['gme']['real_time'] = real_time(o_gme, price('gme', 'D'), win_years=1)
    fig_psy(y_gme, o_gme, 'ch17_gme', 'GameStop, daily 2020-2021', 'USD, adjusted (log scale)', level_label='GameStop')
    # first signal (real time) vs peak
    RES['signal_peak'] = {
        'ndx': signal_vs_peak(o_ndx, price('ndx', 'D'), ('1999-01-01', '2000-12-31'), 93),
        'bet': signal_vs_peak(o_bet, price('bet', 'D'), ('2006-01-01', '2008-06-30'), 93),
        'btc17': signal_vs_peak(o_btc, price('btc', 'D'), ('2017-06-01', '2018-03-31'), 28),
        'btc21': signal_vs_peak(o_btc, price('btc', 'D'), ('2021-01-01', '2021-06-30'), 28),
        'gme': signal_vs_peak(o_gme, price('gme', 'D'), ('2021-01-01', '2021-06-30'), 10, dd_years=1)}
    # LPPLS
    RES['lppls_btc2017'] = fig_lppls_btc2017()
    RES['tc_path'] = fig_tc_instability()
    tab_btc = get_ci('btc', '2014-09-17', '2016-10-01', 'ch17_lppls_ci_btc.csv')
    tab_ndx = get_ci('ndx', '1994-01-01', '1997-01-01', 'ch17_lppls_ci_ndx.csv')
    ci_btc, ci_ndx = tab_btc['ci'], tab_ndx['ci']
    fig_lppls_ci(tab_btc, tab_ndx)
    RES['cond_btc'] = condition_shares(tab_btc)
    RES['cond_ndx'] = condition_shares(tab_ndx)
    RES['ci_btc'] = ci_evaluation(ci_btc, price('btc', 'D'))
    RES['ci_ndx'] = ci_evaluation(ci_ndx, price('ndx', 'D'))
    RES['ci_btc']['max'] = float(ci_btc.max())
    RES['ci_btc']['max_date'] = d2s(ci_btc.idxmax())
    RES['ci_ndx']['max'] = float(ci_ndx.max())
    RES['ci_ndx']['max_date'] = d2s(ci_ndx.idxmax())
    RES['ci_btc']['on_2017'] = float((ci_btc.loc['2017'] > 0).mean())
    RES['ci_btc']['on_2021'] = float((ci_btc.loc['2021'] > 0).mean())
    RES['ci_btc']['on_other'] = float((ci_btc[~ci_btc.index.year.isin([2017, 2021])] > 0).mean())
    # Markov-switching
    ms_ndx, fp_ndx, sp_ndx = fig_ms('ndx', '1990-01-01', 'ch17_ms_ndx',
                                    'Nasdaq 100, weekly log returns 1990-2026: two-regime Markov-switching model')
    ms_ndx['fp_at_peak'] = float(fp_ndx.loc[:'2000-03-31'].iloc[-1])
    ms_ndx['fp_2000_12'] = float(fp_ndx.loc[:'2000-12-31'].iloc[-1])
    ms_ndx['fp_first_2000'] = d2s(fp_ndx.loc['2000-01-01':][fp_ndx.loc['2000-01-01':] > 0.5].index[0])
    turb = sp_ndx > 0.5                                            # turbulent (smoothed) episode containing March 2000
    k = turb.index.searchsorted(pd.Timestamp('2000-03-31')) - 1
    j = k
    while j > 0 and turb.iloc[j - 1]:
        j -= 1
    ms_ndx['sp_spell_start'] = d2s(turb.index[j]) if turb.iloc[k] else None
    RES['ms_ndx'] = ms_ndx
    ms_btc, fp_btc, sp_btc = fig_ms('btc', '2014-09-17', 'ch17_ms_btc',
                                    'Bitcoin, weekly log returns 2014-2026: two-regime Markov-switching model')
    RES['ms_btc'] = ms_btc
    # crypto and AI
    RES['timeline'] = fig_timeline()
    RES['ai'] = fig_ai_dotcom()
    with open(os.path.join(HERE, 'ch17_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved ch17_results.json')


if __name__ == '__main__':
    main()

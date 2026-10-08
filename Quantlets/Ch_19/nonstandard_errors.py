"""
nonstandard_errors.py -- Case study of Chapter 19: nonstandard errors (Menkveld et al., 2024)
===========================================================================================
A mini-multiverse for the hypothesis "market efficiency has not changed over time" (Sec. I.A of the paper), on
the Euro Stoxx 50 index and the BET (daily closes from the course data), 2002-2018, the period of the paper.
Forks of Table V that daily data allow (Seminar 19, C3):
  * outliers: none; winsorised; trimmed (2.5 and 97.5 percentiles of the annual measure m_t, Table V)
  * annual measure m_t: |VR(5) - 1|, |VR(21) - 1| (variance ratio, overlapping q-day returns),
    R^2 of an AR(1) for daily returns
  * model of the average yearly change (in %): linear trend 100 b / mean(m); mean of 100 dln m_t;
    mean of 100 (m_t / m_{t-1} - 1)
3 x 3 x 3 = 27 paths per index. Nonstandard error = IQR of the 27 estimates (eq. 3 of the paper);
ranking of the forks: k-sample Anderson-Darling statistic (Sec. II.C, Fig. 6).
Output: charts/ch19_nse_multiverse, charts/ch19_nse_forks, ch19_nse.json
Modelling Financial Markets - Daniel Traian PELE
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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import read_market, drop_duplicate_records  # noqa: E402

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
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Orange = '#E67E22'
Purple = '#8E44AD'
Teal = '#17A2B8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

NSE_START, NSE_END = '2002', '2018'          # period of the paper (Sec. I.A)
NSE_INDICES = {'STOXX50E.INDX': 'Euro Stoxx 50', 'BET': 'BET'}
OUTLIERS = ['None', 'Winsorised', 'Trimmed']
MEASURES = ['|VR(5) - 1|', '|VR(21) - 1|', 'AR(1) R$^2$']
FORK_MODELS = ['Linear trend', 'Log difference', 'Relative difference']
NSE = {}


def save_nse_fig(name):
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def index_returns(symbol):
    """Daily log returns (closes, weekdays, no duplicate records), 2002-2018."""
    df = read_market(symbol).loc['2001-12-01':f'{NSE_END}-12-31']
    df = drop_duplicate_records(df[df.index.dayofweek < 5])
    s = df['close']
    s = s[s > 0].dropna()
    return np.log(s).diff().dropna().loc[NSE_START:NSE_END]


def variance_ratio(x, q):
    """VR(q) = Var(overlapping q-day return) / (q Var(daily return))."""
    xq = pd.Series(x).rolling(q).sum().dropna().values
    return np.var(xq, ddof=1) / (q * np.var(x, ddof=1))


def annual_measure(r, outlier, measure):
    """Annual (in)efficiency measure m_t, computed on the daily returns of each year; the outlier treatment is
    applied to the measure at the frequency of the analysis (annual), as in Table V (fork 3, note a): winsorised or
    trimmed at the 2.5 and 97.5 percentiles of the m_t; trimmed years stay missing (NaN), so calendar spacing
    is kept."""
    m = []
    for _, g in r.groupby(r.index.year):
        x = g.values
        if measure == '|VR(5) - 1|':
            m.append(abs(variance_ratio(x, 5) - 1))
        elif measure == '|VR(21) - 1|':
            m.append(abs(variance_ratio(x, 21) - 1))
        else:
            m.append(np.corrcoef(x[1:], x[:-1])[0, 1] ** 2)
    m = np.array(m)
    lo, hi = np.percentile(m, [2.5, 97.5])
    if outlier == 'Winsorised':
        m = np.clip(m, lo, hi)
    elif outlier == 'Trimmed':
        m = np.where((m >= lo) & (m <= hi), m, np.nan)
    return m


def yearly_change(m, model):
    """Average yearly change (%) and its SE, by the model fork. Missing years (NaN) stay on the calendar:
    the trend is estimated on the observed years, changes only between consecutive observed years.
    SE: OLS for the trend; sd / sqrt(n) for the mean of the changes (an approximation that ignores the MA(1)
    dependence between successive changes)."""
    t = np.arange(len(m))
    ok = ~np.isnan(m)
    if model == 'Linear trend':
        lr = stats.linregress(t[ok], m[ok])
        return 100 * lr.slope / m[ok].mean(), 100 * lr.stderr / m[ok].mean()
    d = 100 * (np.diff(np.log(m)) if model == 'Log difference' else m[1:] / m[:-1] - 1)
    d = d[~np.isnan(d)]
    return d.mean(), d.std(ddof=1) / np.sqrt(len(d))


def multiverse(r):
    rows = []
    for o in OUTLIERS:
        for ms in MEASURES:
            m = annual_measure(r, o, ms)
            for mo in FORK_MODELS:
                est, se = yearly_change(m, mo)
                rows.append(dict(outlier=o, measure=ms, model=mo, est=est, se=se))
    return pd.DataFrame(rows)


def part_nse():
    tabs = {}
    for sym, lab in NSE_INDICES.items():
        r = index_returns(sym)
        df = multiverse(r)
        tabs[lab] = df
        e = df['est']
        q10, q25, q50, q75, q90 = np.percentile(e, [10, 25, 50, 75, 90])
        ad = {}
        for fork in ('outlier', 'measure', 'model'):
            res = stats.anderson_ksamp([g['est'].values for _, g in df.groupby(fork)])
            ad[fork] = float(res.statistic)
            NSE['ad_crit5'] = float(res.critical_values[2])      # k = 3 groups at each fork
        byl = {mo: float(np.median(df.loc[df.model == mo, 'est'])) for mo in FORK_MODELS}
        NSE[lab] = dict(N=len(r), years=int(r.index.year.nunique()), start=str(r.index[0].date()),
                        end=str(r.index[-1].date()), median=q50, iqr=q75 - q25, p10_90=q90 - q10,
                        med_se=float(df['se'].median()), ad=ad, median_by_model=byl,
                        iqr_trend=float(np.subtract(*np.percentile(df.loc[df.model == 'Linear trend', 'est'], [75, 25]))),
                        max_rel=float(df.loc[df.model == 'Relative difference', 'est'].max()),
                        table=df.round(4).to_dict('records'))

    # --- chart 1: the multiverse, estimates grouped by the model fork ---
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.3), sharey=True)
    mcol = dict(zip(MEASURES, [MainBlue, Forest, IDAred]))
    mmark = dict(zip(OUTLIERS, ['o', 's', '^']))
    off = dict(zip(OUTLIERS, [-0.22, 0.0, 0.22]))
    moff = dict(zip(MEASURES, [-0.06, 0.0, 0.06]))
    for ax, (lab, df) in zip(axes, tabs.items()):
        q25, q50, q75 = np.percentile(df['est'], [25, 50, 75])
        ax.axhspan(q25, q75, color=Amber, alpha=0.18, lw=0)
        ax.axhline(q50, color=Amber, lw=1.2, ls='--')
        ax.axhline(0, color='black', lw=0.6)
        for _, row in df.iterrows():
            x = FORK_MODELS.index(row['model']) + off[row['outlier']] + moff[row['measure']]
            ax.scatter(x, row['est'], s=26, color=mcol[row['measure']], marker=mmark[row['outlier']],
                       edgecolor='black', linewidth=0.3, zorder=3)
        ax.set_yscale('symlog', linthresh=10)
        ax.set_xticks(range(3))
        ax.set_xticklabels(FORK_MODELS)
        ax.set_xlim(-0.5, 2.5)
        ax.set_title(f'{lab}: IQR = {q75 - q25:.1f} pp, median = {q50:.1f}%', fontsize=10)
    axes[0].set_ylabel('Average yearly change (%), log scale beyond ±10%')
    h = ([plt.Line2D([], [], ls='', marker='o', color=c, markeredgecolor='black', markeredgewidth=0.3, label=f'Measure: {m}')
          for m, c in mcol.items()]
         + [plt.Line2D([], [], ls='', marker=mk, color='white', markeredgecolor='black', label=f'Outliers: {o}')
            for o, mk in mmark.items()]
         + [plt.Line2D([], [], color=Amber, ls='--', label='Median of the 27 paths'),
            plt.Rectangle((0, 0), 1, 1, color=Amber, alpha=0.18, label='Interquartile range (nonstandard error)')])
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False)
    plt.tight_layout()
    save_nse_fig('ch19_nse_multiverse')

    # --- chart 2: ranking of the forks (k-sample Anderson-Darling) ---
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    forks = ['model', 'measure', 'outlier']
    names = ['Model (trend, log, relative)', 'Measure (VR(5), VR(21), AR(1) R$^2$)', 'Outliers (none, winsorised, trimmed)']
    y = np.arange(len(forks))
    for k, (lab, col) in enumerate(zip(NSE_INDICES.values(), [MainBlue, IDAred])):
        v = [NSE[lab]['ad'][f] for f in forks]
        ax.barh(y + (-0.18 if k == 0 else 0.18), v, 0.34, color=col, label=lab)
        for yi, vi in zip(y, v):
            ax.text(max(vi, 0) + 0.15, yi + (-0.18 if k == 0 else 0.18), f'{vi:.2f}', va='center', fontsize=8,
                    color='black')
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel('k-sample Anderson-Darling statistic (larger = bigger effect)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
    save_nse_fig('ch19_nse_forks')
    return NSE


if __name__ == '__main__':
    part_nse()
    with open(os.path.join(HERE, 'ch19_nse.json'), 'w') as f:
        json.dump(NSE, f, indent=1, default=float)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != 'table'} if isinstance(v, dict) else v)
                      for k, v in NSE.items()}, indent=1, default=float))

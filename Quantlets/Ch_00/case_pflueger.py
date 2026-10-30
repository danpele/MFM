"""
case_pflueger.py -- Chapter 0, second case study: Treasury bond-stock betas (Pflueger, 2025, JFE)
=================================================================================================
Pflueger, C. (2025). Back to the 1980s or not? The drivers of inflation and real risks in Treasury bonds.
Journal of Financial Economics, 167, 104027. https://doi.org/10.1016/j.jfineco.2025.104027

Figure 1 of the paper, on the course data:
  * Panel A: quarterly 10-year nominal Treasury excess returns regressed on quarterly US equity excess returns,
    5-year (20-quarter) rolling windows; excess over the 3-month T-bill.
  * Panel B: daily 10-year nominal and inflation-indexed (TIPS) bond log returns regressed on daily equity log
    returns, 120-trading-day rolling windows, January 2018 onwards (extended to September 2026).
Bond returns from FRED constant-maturity yields with a constant duration of 10 years:
  r = -10 * dy + y / k (k = 4 quarterly, 252 daily), the zero-coupon approximation with y(9.75) ~ y(10).
Equity: CRSP value-weighted US market (Kenneth French, monthly, compounded to quarters) and SPY (daily, total return).
Data: FRED (DGS10, DFII10, DTB3), Kenneth French Data Library, data/market/SPY.US.csv (via mfm_data.load).
Modelling Financial Markets - Daniel Traian PELE
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  chart drawn at the size it has on the slide
from mfm_data import load  # noqa: E402

plt.rcParams.update({
    'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none', 'savefig.transparent': True,
    'axes.grid': False, 'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 9, 'axes.labelsize': 10, 'axes.titlesize': 11, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.linewidth': 0.6, 'lines.linewidth': 1.1, 'legend.facecolor': 'none',
    'legend.framealpha': 0, 'legend.fontsize': 8})

# Chart colours (as in generate_all_charts.py)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Amber = '#B5853F'
Navy = '#1F2A44'      # reference lines (no grey in charts)

CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
OUT_JSON = os.path.join(HERE, 'ch0_pflueger_results.json')
DUR = 10.0                     # constant duration of the 10-year bond (years)
QWIN, DWIN = 20, 120           # 5-year rolling window (quarters), 120-trading-day window (days)
START_Q, END = '1962-01-01', '2026-09-18'
PANEL_B_START = '2018-01-01'
PAPER_PERIODS = [('1979Q4', '2001Q1'), ('2001Q2', '2019Q4'), ('2020Q1', None)]


# =============================================================================
# DATA
# =============================================================================
def quarterly_excess():
    """Quarterly log excess returns over the 3-month T-bill: US market (CRSP VW) and the 10-year Treasury."""
    mkt = load('US market excess (FF)', START_Q, END) + load('T-bill 1m (FF)', START_Q, END)   # total return
    eq = np.log1p(mkt).resample('QE').agg(['sum', 'count'])
    eq = eq.loc[eq['count'] == 3, 'sum']                                  # complete quarters only
    y10 = load('DGS10', START_Q, END).resample('QE').last() / 100
    tb = load('DTB3', START_Q, END).resample('QE').last() / 100
    rf = tb.shift(1) / 4                                                  # T-bill yield known at the start
    bond = -DUR * y10.diff() + y10 / 4                                    # 10-year zero: -n dy + y/4
    df = pd.concat([eq - rf, bond - rf], axis=1, keys=['eq', 'bond']).dropna()
    df.index = df.index.to_period('Q')
    return df


def quarterly_tips():
    """Quarterly 10-year TIPS excess return (DFII10 starts in January 2003)."""
    y_r = load('DFII10', '2002-10-01', END).resample('QE').last() / 100
    tb = load('DTB3', '2002-10-01', END).resample('QE').last() / 100
    rq = (-DUR * y_r.diff() + y_r / 4 - tb.shift(1) / 4).dropna()
    rq.index = rq.index.to_period('Q')
    return rq


def daily_returns():
    """Daily log returns on common days: SPY (total return), 10-year nominal and TIPS bonds (duration 10)."""
    p = pd.concat([load('SPY', '1999-01-01', END), load('DGS10', '1999-01-01', END) / 100,
                   load('DFII10', '1999-01-01', END) / 100], axis=1)
    p.columns = ['spy', 'nom', 'tips']
    p = p.dropna(subset=['spy', 'nom'])                                   # common days of SPY and FRED
    out = pd.DataFrame({'eq': np.log(p['spy']).diff(),
                        'nom': -DUR * p['nom'].diff() + p['nom'] / 252,
                        'tips': -DUR * p['tips'].diff() + p['tips'] / 252})
    return out.iloc[1:]


def rolling_beta(y, x, w):
    """Rolling OLS slope of y on x over w observations."""
    return y.rolling(w).cov(x) / x.rolling(w).var()


def ols_beta(y, x):
    """OLS slope with heteroskedasticity-robust (HC1) standard error."""
    d = pd.concat([y, x], axis=1).dropna()
    yv, xv = d.iloc[:, 0].values, d.iloc[:, 1].values
    X = np.column_stack([np.ones_like(xv), xv])
    b = np.linalg.lstsq(X, yv, rcond=None)[0]
    e = yv - X @ b
    n = len(yv)
    XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - 2)
    return float(b[1]), float(np.sqrt(V[1, 1])), n


# =============================================================================
# CHART + RESULTS
# =============================================================================
def fig_pflueger_betas(save=True):
    q = quarterly_excess()
    bq = rolling_beta(q['bond'], q['eq'], QWIN).dropna()
    d = daily_returns()
    bn = rolling_beta(d['nom'], d['eq'], DWIN)
    dt = d.dropna(subset=['tips'])
    bt = rolling_beta(dt['tips'], dt['eq'], DWIN)
    bn_b, bt_b = bn.loc[PANEL_B_START:], bt.loc[PANEL_B_START:]

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.3), gridspec_kw={'width_ratios': [1.25, 1]})
    xq = bq.index.to_timestamp(how='end')
    axes[0].plot(xq, bq.values, color=MainBlue, lw=1.0, label='Nominal 10y Treasury beta')
    axes[0].axhline(0, color=Navy, lw=0.5)
    for dline in ['2001-04-01', '2020-01-01']:
        axes[0].axvline(pd.Timestamp(dline), color=Navy, lw=0.6, ls=':')
    axes[0].set_ylabel('Bond-stock beta')
    axes[0].set_title(f'A: quarterly, 5-year windows, {bq.index[0].year}-{bq.index[-1].year}', fontsize=8.5,
                      loc='left')
    axes[1].plot(bn_b.index, bn_b.values, color=MainBlue, lw=0.8)
    axes[1].plot(bt_b.index, bt_b.values, color=Amber, lw=0.8, label='Inflation-indexed 10y (TIPS) beta')
    axes[1].axhline(0, color=Navy, lw=0.5)
    axes[1].axvline(pd.Timestamp('2020-03-11'), color=Navy, lw=0.6, ls=':')
    axes[1].set_title('B: daily, 120-day windows, 2018-2026', fontsize=8.5, loc='left')
    axes[1].xaxis.set_major_locator(mdates.YearLocator(2))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.tight_layout()
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, fontsize=8)
    if save:
        os.makedirs(CHART_DIR, exist_ok=True)
        for ext, kw in [('pdf', {}), ('png', {'dpi': 180})]:
            plt.savefig(os.path.join(CHART_DIR, f'ch0_pflueger_betas.{ext}'), bbox_inches='tight',
                        transparent=True, **kw)
    plt.close()

    res = {'quarterly_sample': [str(q.index[0]), str(q.index[-1])], 'n_quarters': int(len(q)),
           'daily_sample': [str(d.index[0].date()), str(d.index[-1].date())], 'subperiods': {}}
    for a, b in PAPER_PERIODS:
        sub = q.loc[a:b] if b else q.loc[a:]
        beta, se, n = ols_beta(sub['bond'], sub['eq'])
        res['subperiods'][f'{a}-{b or str(q.index[-1])}'] = {'beta': round(beta, 3), 'se': round(se, 3), 'n': n}
    qt = pd.concat([quarterly_tips(), q['eq']], axis=1, keys=['tips', 'eq']).dropna()
    for a, b in [('2003Q2', '2019Q4'), ('2020Q1', None)]:
        sub = qt.loc[a:b] if b else qt.loc[a:]
        beta, se, n = ols_beta(sub['tips'], sub['eq'])
        res['subperiods'][f'TIPS {a}-{b or str(sub.index[-1])}'] = {'beta': round(beta, 3), 'se': round(se, 3),
                                                                     'n': n}
    pre, postq = bq.loc[:'2001Q1'], bq.loc['2001Q2':]
    res['q_roll'] = {'max_pre2001': [str(pre.idxmax()), round(float(pre.max()), 2)],
                     'min_post2001': [str(postq.idxmin()), round(float(postq.min()), 2)],
                     'last': [str(bq.index[-1]), round(float(bq.iloc[-1]), 2)],
                     'first_positive_after_2001': str(postq[postq > 0].index.min()),
                     'share_positive_pre2001': round(float((pre > 0).mean()), 3)}
    post = bn.loc['2020-03-11':].dropna()
    post_t = bt.loc['2020-03-11':].dropna()
    common = pd.concat([post, post_t], axis=1).dropna()
    res['d_roll'] = {'nom_last': [str(bn.index[-1].date()), round(float(bn.iloc[-1]), 2)],
                     'tips_last': [str(bt.index[-1].date()), round(float(bt.iloc[-1]), 2)],
                     'nom_max_post_covid': [str(post.idxmax().date()), round(float(post.max()), 2)],
                     'nom_share_positive_post_covid': round(float((post > 0).mean()), 3),
                     'nom_below_tips_share_post_covid':
                         round(float((common.iloc[:, 0] < common.iloc[:, 1]).mean()), 3)}
    res['d_year'] = {}
    for yr in range(2018, 2027):
        s = d.loc[str(yr)]
        bnom, senom, n = ols_beta(s['nom'], s['eq'])
        btip, setip, _ = ols_beta(s['tips'], s['eq'])
        bdif, sedif, _ = ols_beta(s['nom'] - s['tips'], s['eq'])       # nominal minus TIPS = -10 x d(breakeven)
        res['d_year'][str(yr)] = {'nom': round(bnom, 3), 'nom_se': round(senom, 3), 'tips': round(btip, 3),
                                  'tips_se': round(setip, 3), 'diff': round(bdif, 3), 'diff_se': round(sedif, 3),
                                  'n': n}
    with open(OUT_JSON, 'w') as f:
        json.dump(res, f, indent=1)
    return res, q, bq, d, bn, bt


if __name__ == '__main__':
    print(json.dumps(fig_pflueger_betas()[0], indent=1))

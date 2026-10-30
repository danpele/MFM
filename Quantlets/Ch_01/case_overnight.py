"""
Case study 2, Chapter 1: the market return around the clock (Bondarenko & Muravyev, 2023, JFQA)
================================================================================================
The paper: on E-mini S&P 500 futures traded around the clock, the 4 hours around the European open account
for the entire average market return; the other 20 hours average a noisy zero.
Course replication on daily SPY prices (data/market/SPY.US.csv, the ETF: its open is a traded price, unlike the
stale open of the S&P 500 index):
  overnight  r_on_t = ln(O_t / C_{t-1})          (price only, close of day t-1 to open of day t)
  intraday   r_id_t = ln(C_t / O_t)               (open to close of day t)
  dividends  r_dv_t = ln(f_t / f_{t-1}),  f = adjusted close / close   (credited on the ex-dividend day)
  so that r_on + r_id + r_dv = ln(adjusted C_t / adjusted C_{t-1}), the total close-to-close return.
Means annualised x252, t statistics with the Newey-West long-run variance (Bartlett kernel,
L = floor(4 (T/100)^(2/9))), as for the leverage test of the chapter.
Extension: Bitcoin, 5-minute bars (data/market/intraday), daily return inside and outside the US regular session
(09:30-16:00 New York time, weekdays).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import read_market, MARKET_DIR  # noqa: E402

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

MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'

CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
OUT_JSON = os.path.join(HERE, 'ch1_overnight.json')
SUBPERIODS = [('1993', '2004'), ('2005', '2015'), ('2016', '2026')]
US_SESSION = (9 * 60 + 30, 16 * 60)        # 09:30-16:00 New York time (US regular session)


def save_fig(name):
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f'   saved {name}')


def nw_se(x):
    """Standard error of the mean with the Newey-West long-run variance (Bartlett, L = floor(4 (T/100)^(2/9)))."""
    x = np.asarray(x, float)
    T = len(x)
    u = x - x.mean()
    L = int(np.floor(4 * (T / 100) ** (2 / 9)))
    lrv = u @ u / T
    for k in range(1, L + 1):
        lrv += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / T
    return np.sqrt(lrv / T)


def spy_split():
    """Daily overnight, intraday and dividend log returns of SPY."""
    s = read_market('SPY.US')
    f = s['adjusted_close'] / s['close']
    d = pd.DataFrame({'overnight': np.log(s['open'] / s['close'].shift(1)),
                      'intraday': np.log(s['close'] / s['open']),
                      'dividend': np.log(f / f.shift(1))}).dropna()
    d['total'] = d.sum(axis=1)
    return d


def stats_of(x, periods=252):
    x = np.asarray(x, float)
    se = nw_se(x)
    return {'n': int(len(x)), 'mean_bp': 1e4 * x.mean(), 'ann_mean_pct': 100 * periods * x.mean(),
            'ann_vol_pct': 100 * x.std(ddof=1) * np.sqrt(periods),
            'sharpe': x.mean() / x.std(ddof=1) * np.sqrt(periods), 't_nw': x.mean() / se,
            'ci95_ann_pct': [100 * periods * (x.mean() - 1.96 * se), 100 * periods * (x.mean() + 1.96 * se)]}


def btc_sessions():
    """Bitcoin, 5-minute bars: daily (New York calendar day) log return inside and outside 09:30-16:00 New York."""
    b = pd.read_csv(os.path.join(MARKET_DIR, 'intraday', 'BTC-USD.CC_5m.csv'),
                    parse_dates=['datetime_utc']).set_index('datetime_utc')
    r = np.log(b['close']).diff().dropna()
    ny = r.index.tz_localize('UTC').tz_convert('America/New_York')
    start = ny.hour * 60 + ny.minute                          # each bar is labelled by its open time
    us = (start >= US_SESSION[0]) & (start < US_SESSION[1]) & (ny.dayofweek < 5)
    d = pd.DataFrame({'r': r.values, 'us': us, 'day': ny.date})
    dd = d.groupby(['day', 'us'])['r'].sum().unstack().fillna(0.0)    # weekends: no US session, return 0 there
    out = {'start': str(r.index[0].date()), 'end': str(r.index[-1].date()), 'days': int(len(dd)),
           'bars': int(len(r))}
    for key, col in [('us_session', True), ('outside', False)]:
        out[key] = stats_of(dd[col].values, periods=365)
    return out


def analyse():
    d = spy_split()
    res = {'start': str(d.index[0].date()), 'end': str(d.index[-1].date()), 'n': int(len(d)),
           'full': {k: stats_of(d[k]) for k in ['overnight', 'intraday', 'dividend', 'total']},
           'cum_log': {k: float(d[k].sum()) for k in ['overnight', 'intraday', 'dividend', 'total']},
           'overnight_share_price': float(d['overnight'].sum() / (d['overnight'] + d['intraday']).sum()),
           'subperiods': []}
    yr = d.groupby(d.index.year)[['overnight', 'intraday']].sum()
    res['years'] = int(len(yr))
    res['years_overnight_gt_intraday'] = int((yr['overnight'] > yr['intraday']).sum())
    res['years_overnight_pos'] = int((yr['overnight'] > 0).sum())
    res['years_intraday_pos'] = int((yr['intraday'] > 0).sum())
    for a, b in SUBPERIODS:
        x = d.loc[a:b]
        res['subperiods'].append({'from': a, 'to': b, 'overnight': stats_of(x['overnight']),
                                  'intraday': stats_of(x['intraday'])})
    res['corr_overnight_intraday'] = float(d['overnight'].corr(d['intraday']))
    res['btc'] = btc_sessions()
    return d, res


def fig_cs_overnight(d, res):
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={'width_ratios': [1.65, 1]})
    c = d.cumsum()
    ax.plot(c.index, 100 * c['total'], color=MainBlue, lw=0.9, label='Close to close, with dividends')
    ax.plot(c.index, 100 * c['overnight'], color=IDAred, lw=0.9, label='Overnight: close to next open')
    ax.plot(c.index, 100 * c['intraday'], color=Forest, lw=0.9, label='Intraday: open to close')
    ax.plot(c.index, 100 * c['dividend'], color=Amber, lw=0.9, label='Dividends')
    ax.axhline(0, color=Navy, lw=0.5, ls='--')
    ax.set_xlim(c.index[0], c.index[-1])
    ax.set_ylabel('Cumulative log return (%)')
    ax.set_title(f"SPY, {res['start'][:4]}-{res['end'][:4]}: cumulative log returns")
    labels = [f'{p["from"]}-{p["to"][2:]}' for p in res['subperiods']] + ['Full sample']
    on = [p['overnight'] for p in res['subperiods']] + [res['full']['overnight']]
    idd = [p['intraday'] for p in res['subperiods']] + [res['full']['intraday']]
    x = np.arange(len(labels))
    w = 0.38
    for off, vals, col in [(-w / 2, on, IDAred), (w / 2, idd, Forest)]:
        m = np.array([v['ann_mean_pct'] for v in vals])
        lo = m - np.array([v['ci95_ann_pct'][0] for v in vals])
        hi = np.array([v['ci95_ann_pct'][1] for v in vals]) - m
        ax2.bar(x + off, m, w, color=col, alpha=0.85)
        ax2.errorbar(x + off, m, yerr=[lo, hi], fmt='none', ecolor=Navy, elinewidth=0.7, capsize=2)
    ax2.axhline(0, color=Navy, lw=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel('Annualised mean (%)')
    ax2.set_title('Mean, 95% Newey-West interval')
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False)
    plt.tight_layout()
    save_fig('ch1_cs_overnight')


def export_daily(d):
    """Daily series for the interactive page (bp, 2 decimals)."""
    return {'dates': [t.strftime('%Y-%m-%d') for t in d.index],
            **{k: [round(1e4 * v, 2) for v in d[k].values] for k in ['overnight', 'intraday', 'dividend']}}


if __name__ == '__main__':
    d, res = analyse()
    with open(OUT_JSON, 'w') as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'subperiods'}, indent=1)[:4000])
    for p in res['subperiods']:
        print(p['from'], p['to'], {k: (round(p[k]['ann_mean_pct'], 2), round(p[k]['t_nw'], 2)) for k in ['overnight', 'intraday']})
    if os.environ.get('NO_CHART') != '1':
        fig_cs_overnight(d, res)

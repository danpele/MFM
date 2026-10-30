"""
case_intraday_momentum.py -- Chapter 10, second case study: market intraday momentum (Baltussen, Da, Lammers & Martens, 2021)
===========================================================================================================================
The paper (Journal of Financial Economics 142(1), 377-403): the return of the last 30 minutes before the close (r_LH) is
predicted by the return of the rest of the day (r_ROD, from the previous close to 30 minutes before the close),
  r_LH,t = alpha + beta_ROD r_ROD,t + e_t                                           (their eq. 7)
in futures on equity indices, bonds, commodities and currencies, December 1974 - May 2020; gamma hedging by option market
makers and leveraged ETFs is the proposed channel. Pooled equity futures (Table 2, Panel A, col. 3): 100 beta = 4.18
(t = 7.29), adjusted R2 = 2.45%; S&P 500 futures on days with negative net gamma exposure (Table 7): 100 beta = 6.63.

Course replication, out of sample: SPY 5-minute bars, regular session (bar start 09:30-15:55, New York time), days with
all 78 bars whose previous trading day (daily SPY calendar) also has all 78 bars, October 2020 - September 2026.
  previous close = close of the 15:55 bar of the previous trading day (16:00)
  r_ROD = log(P_15:30 / previous close) + dividend yield on ex-dividend days (from the adjusted daily close)
  r_LH  = log(P_16:00 / P_15:30); r_ONFH = log(P_10:00 / previous close) (+ dividend), the predictor of Gao et al. (2018)
  Newey-West standard errors, 5 lags; slopes and R2 x 100 as in the paper.
Also: the slope by year, on down and up days (sign of r_ROD), the timing strategy eta (long r_LH if r_ROD > 0, short
otherwise), the next-day reversal and the slope for other lengths of the last interval (10-60 minutes).
Chart: ch10_intraday_momentum. Output: case_intraday_momentum.json
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import intraday_spy, read_market   # noqa: E402
from generate_all_charts import MainBlue, IDAred, Navy, save_fig, jsonable   # noqa: E402

# Baltussen, Da, Lammers & Martens (2021): slopes and R2 x 100
BDLM = dict(beta_eq=4.18, t_eq=7.29, r2_eq=2.45, r2oos_eq=2.88, beta_onfh_eq=4.86, beta_nge_neg=6.63, t_nge_neg=4.78,
            beta_nge_pos=0.82, t_nge_pos=1.03, rev_t3=-27.98)
LAGS = 5
CUTS = ['14:55', '15:05', '15:15', '15:25', '15:35', '15:45']   # start of the last interval: 60, 50, 40, 30, 20, 10 minutes
CUT0 = '15:25'                                                  # bar 15:25-15:30: its close is P_15:30


def momentum_days():
    """One row per day: r_ROD, r_LH, r_ONFH, log prices at the cut points (relative to the previous close), next-day return."""
    s = intraday_spy()
    c = s.pivot_table(index='date', columns='tod', values='close', dropna=False)
    d = read_market('SPY.US').copy()
    d.index = pd.to_datetime(d.index)
    prev_cal = pd.Series(d.index[:-1], index=d.index[1:])
    f = d['adjusted_close'] / d['close']
    div = np.log(f / f.shift(1)).reindex(c.index).fillna(0.0)          # dividend yield on ex-dividend days
    prev_day = pd.Series(c.index, index=c.index).shift(1)
    ok = prev_day.eq(prev_cal.reindex(c.index))                       # previous trading day also complete
    pc = c['15:55'].shift(1)
    lp = np.log(c.div(pc, axis=0)).add(div, axis=0)                   # log price relative to the previous close
    out = pd.DataFrame({'rod': lp[CUT0], 'lh': lp['15:55'] - lp[CUT0], 'onfh': lp['09:55'], 'close': lp['15:55']})
    for k in CUTS:
        out['x' + k.replace(':', '')] = lp[k]
    out['next'] = np.log(c['15:55'].shift(-1) / c['15:55']) + div.shift(-1)   # close to next close
    nxt_ok = ok.shift(-1, fill_value=False)
    out.loc[~nxt_ok, 'next'] = np.nan
    out = out[ok.values].dropna(subset=['rod', 'lh', 'onfh', 'close'] + ['x' + k.replace(':', '') for k in CUTS])
    out['year'] = out.index.year
    return out


def nw(y, x):
    """OLS of y on a constant and x, Newey-West (LAGS) t; slope and R2 x 100, 95% interval of 100 beta."""
    m = sm.OLS(np.asarray(y, float), sm.add_constant(np.asarray(x, float))).fit(cov_type='HAC', cov_kwds={'maxlags': LAGS})
    b, se = 100 * m.params[1], 100 * m.bse[1]
    return dict(n=int(len(y)), beta=float(b), se=float(se), t=float(m.tvalues[1]), p=float(m.pvalues[1]),
                lo=float(b - 1.96 * se), hi=float(b + 1.96 * se), r2=float(100 * m.rsquared),
                r2adj=float(100 * m.rsquared_adj))


def holm(ps):
    """Holm (1979) step-down adjusted p-values for a dict of p-values."""
    ks = sorted(ps, key=ps.get)
    m, out, run = len(ks), {}, 0.0
    for i, k in enumerate(ks):
        run = max(run, min(1.0, (m - i) * ps[k]))
        out[k] = run
    return out


def mean_hac(x):
    """Mean of a daily series with a Newey-West (LAGS) 95% interval."""
    m = sm.OLS(np.asarray(x, float), np.ones(len(x))).fit(cov_type='HAC', cov_kwds={'maxlags': LAGS})
    return float(m.params[0]), float(m.bse[0])


def analysis(D):
    res = dict(paper=BDLM, n=int(len(D)), first=str(D.index[0].date()), last=str(D.index[-1].date()))
    res['rod'] = nw(D['lh'], D['rod'])
    res['onfh'] = nw(D['lh'], D['onfh'])
    res['down'] = nw(D.loc[D['rod'] < 0, 'lh'], D.loc[D['rod'] < 0, 'rod'])
    res['up'] = nw(D.loc[D['rod'] >= 0, 'lh'], D.loc[D['rod'] >= 0, 'rod'])
    # difference of the down-day and up-day slopes, on the common calendar (indicator and interaction, HAC on all days)
    dn = (D['rod'] < 0).astype(float)
    X = sm.add_constant(np.column_stack([D['rod'], dn, dn * D['rod']]))
    m = sm.OLS(D['lh'].values, X).fit(cov_type='HAC', cov_kwds={'maxlags': LAGS})
    res['diff_down_up'] = dict(beta=float(100 * m.params[3]), se=float(100 * m.bse[3]), t=float(m.tvalues[3]),
                               p=float(m.pvalues[3]))
    res['years'] = {}
    yb = D['year'].clip(lower=2021)                                     # Oct-Dec 2020 pooled with 2021
    for y, g in D.groupby(yb):
        res['years']['2020-21' if y == 2021 else str(y)] = nw(g['lh'], g['rod'])
    # timing strategy: simple return of a position with a fixed notional, w = +1 if r_ROD > 0, -1 otherwise,
    # R_t = w_t (exp(r_LH,t) - 1); gross of costs
    w = np.where(D['rod'] > 0, 1.0, -1.0)
    eta = w * np.expm1(D['lh'].values)
    mu, se = mean_hac(eta)
    res['eta'] = dict(mean_bp=float(1e4 * mu), lo_bp=float(1e4 * (mu - 1.96 * se)), hi_bp=float(1e4 * (mu + 1.96 * se)),
                      ann_pct=float(100 * 252 * mu), sr=float(mu / eta.std(ddof=1) * np.sqrt(252)), hit=float((eta > 0).mean()),
                      cum_pct=float(100 * (np.prod(1 + eta) - 1)))
    k = D['next'].notna()
    res['reversal'] = nw(D.loc[k, 'next'], D.loc[k, 'lh'])
    res['cuts'] = {}
    for c in CUTS:
        x = D['x' + c.replace(':', '')]
        res['cuts'][c] = nw(D['close'] - x, x)
    # multiple testing: Holm adjustment within each family of six tests (the 30-minute regression on all days is the
    # main test; the subperiods and the other interval lengths are exploratory)
    for fam in ('years', 'cuts'):
        hp = holm({k: v['p'] for k, v in res[fam].items()})
        for k in res[fam]:
            res[fam][k]['p_holm'] = float(hp[k])
    q = pd.qcut(D['rod'], 10, labels=False)
    g = D.groupby(q)
    res['bins'] = dict(x=list(100 * g['rod'].mean()), y=list(1e4 * g['lh'].mean()),
                       se=list(1e4 * g['lh'].std(ddof=1) / np.sqrt(g.size())))
    res['sd_rod'] = float(100 * D['rod'].std(ddof=1))
    res['sd_lh_bp'] = float(1e4 * D['lh'].std(ddof=1))
    res['mean_rod'] = float(100 * D['rod'].mean())
    res['mean_lh_bp'] = float(1e4 * D['lh'].mean())
    res['alpha_bp'] = float(1e4 * (D['lh'].mean() - res['rod']['beta'] / 100 * D['rod'].mean()))
    return res


def fig_intraday_momentum(R):
    from matplotlib.lines import Line2D
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.4), gridspec_kw=dict(width_ratios=[1.15, 1]))
    B = R['bins']
    x, y, se = np.array(B['x']), np.array(B['y']), np.array(B['se'])
    a1.errorbar(x, y, yerr=1.96 * se, fmt='o', color=MainBlue, ms=4, lw=0.9, capsize=2)
    xs = np.linspace(x.min() - 0.3, x.max() + 0.3, 50)
    a1.plot(xs, R['alpha_bp'] + R['rod']['beta'] * xs, color=MainBlue, lw=1.2)
    a1.plot(xs, R['mean_lh_bp'] + BDLM['beta_eq'] * (xs - R['mean_rod']), color=IDAred, lw=1.2, ls='--')
    a1.axhline(0, color=Navy, lw=0.6)
    a1.set_xlabel('Rest-of-day return, previous close to 15:30 (%)')
    a1.set_ylabel('Last-half-hour return,\n15:30 to 16:00 (bp)')
    yr = R['years']
    ks = list(yr)
    xx = np.arange(len(ks))
    b = np.array([yr[k]['beta'] for k in ks])
    a2.errorbar(xx, b, yerr=[b - np.array([yr[k]['lo'] for k in ks]), np.array([yr[k]['hi'] for k in ks]) - b],
                fmt='s', color=MainBlue, ms=4, lw=0.9, capsize=2)
    a2.axhline(BDLM['beta_eq'], color=IDAred, lw=1.2, ls='--')
    a2.axhline(0, color=Navy, lw=0.6)
    a2.set_xticks(xx)
    a2.set_xticklabels(ks)
    a2.set_ylabel('Slope 100 beta')
    r = R['rod']
    h = [Line2D([], [], color=MainBlue, marker='o', ls='none', ms=4),
         Line2D([], [], color=MainBlue, lw=1.2),
         Line2D([], [], color=MainBlue, marker='s', ls='none', ms=4),
         Line2D([], [], color=IDAred, lw=1.2, ls='--')]
    lab = ['SPY decile means of the last-half-hour return, 95% interval',
           f"SPY OLS fit: 100 beta = {r['beta']:.2f} (95% interval {r['lo']:.2f} to {r['hi']:.2f})",
           'SPY slope by year, Newey-West 95% interval',
           'Paper, pooled equity futures 1974-2020: 100 beta = 4.18']
    fig.legend(h, lab, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch10_intraday_momentum')


def main():
    D = momentum_days()
    R = analysis(D)
    fig_intraday_momentum(R)
    with open(os.path.join(HERE, 'case_intraday_momentum.json'), 'w') as f:
        json.dump(jsonable(R), f, indent=1)
    print(json.dumps(jsonable({k: v for k, v in R.items() if k not in ('bins',)}), indent=1))


if __name__ == '__main__':
    main()

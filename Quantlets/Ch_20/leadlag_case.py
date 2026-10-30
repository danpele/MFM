"""
leadlag_case.py -- second case study of Chapter 20: a signature lead-lag metric on intraday SPY and Bitcoin paths
==================================================================================================================
Bennett, Cucuringu & Reinert (2022, Machine Learning 111(12), 4497-4538, https://doi.org/10.1007/s10994-022-06250-4)
measure the lead-lag relation of two assets over [t - m, t] by the antisymmetric part of level 2 of the signature
of their (normalised) log-price path, i.e. twice its Levy area:
    S_ij = int int_{u<v} (dX_i(u) dX_j(v) - dX_j(u) dX_i(v)),
positive when moves of i are followed by moves of j in the same direction.

Course replication: five-minute bars of SPY (S&P 500 ETF) and Bitcoin (BTC-USD) from data/market/intraday. The
timestamps (UTC) are converted to America/New_York and label the start of a bar: the session grid is the 78 bars
09:30, 09:35, ..., 15:55. The separate 16:00 closing record of SPY (identical OHLC, no volume) and off-grid
timestamps are dropped. A day counts only if both assets have all 78 grid bars; the 78 returns of the day run from
the open of the 09:30 bar to the close of each bar (the first interval of the session is kept). In each day the two
return series are divided by their standard deviation in that day; the 2-D path is the cumulative sum. For a window of m
five-minute steps, the Levy area of the piecewise-linear path through m + 1 points is
    A = 1/2 sum_{l=1}^{m-1} sum_i (x_i y_{i+l} - y_i x_{i+l}),
a sum of lagged cross-products with weights m - l on lag l. The daily statistic is the mean area over all
rolling windows of m steps in the day; its mean over days is tested with a Newey-West t-statistic (sigvol.nw_var).
For comparison, the cross-correlations corr(SPY_{t-l}, BTC_t), l = -6..6, averaged over days; the error bars of
the chart are pointwise 95% intervals with the same Newey-West standard error as the tests. The scan over 12 non-zero
lags and 8 windows is exploratory: Holm-adjusted p-values over this family of 20 tests are reported, and the
direction is tested directly through the contrast CCF(+1) - CCF(-1).

Outputs: charts/ch20_leadlag.pdf/.png, Quantlets/Ch_20/ch20_leadlag.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sigvol as S   # noqa: E402

INTRA = os.path.join(HERE, '..', '..', 'data', 'market', 'intraday')
OUT_JSON = os.path.join(HERE, 'ch20_leadlag.json')
LAGS = list(range(-6, 7))
WINDOWS = [2, 3, 4, 6, 12, 24, 39, 78]        # five-minute steps: 10 minutes ... the whole session (78 steps)
GRID = [f'{h:02d}:{m:02d}' for h in range(9, 16) for m in range(0, 60, 5) if (h, m) >= (9, 30)]   # 78 bar starts
assert len(GRID) == 78 and GRID[-1] == '15:55'


def session_bars(f):
    """Bars on the New York session grid (start labels 09:30 ... 15:55), indexed by (date, HH:MM)."""
    d = pd.read_csv(os.path.join(INTRA, f), parse_dates=['datetime_utc'])
    ny = d['datetime_utc'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')
    d['day'], d['hm'] = ny.dt.date, ny.dt.strftime('%H:%M')
    d = d[d['hm'].isin(GRID)].dropna(subset=['open', 'close'])     # drops the 16:00 closing record
    return d.set_index(['day', 'hm'])[['open', 'close']]


def load_days():
    """Per-day arrays (78 x 2) of SPY and BTC five-minute log returns, each divided by its standard deviation.
    Returns also the number of common days dropped because a grid bar is missing."""
    spy, btc = session_bars('SPY.US_5m.csv'), session_bars('BTC-USD.CC_5m.csv')
    common = sorted(set(spy.index.get_level_values(0)) & set(btc.index.get_level_values(0)))
    days, dates, dropped = [], [], 0
    for day in common:
        gs, gb = spy.loc[day], btc.loc[day]
        if not (gs.index.is_unique and gb.index.is_unique):
            dropped += 1
            continue
        gs, gb = gs.reindex(GRID), gb.reindex(GRID)
        if gs.isna().any().any() or gb.isna().any().any():
            dropped += 1
            continue
        P = np.log(np.column_stack([np.r_[gs['open'].iloc[0], gs['close'].values],
                                    np.r_[gb['open'].iloc[0], gb['close'].values]]))
        r = np.diff(P, axis=0)                        # 78 returns: 09:30 open -> 09:35 close, ..., -> 16:00
        days.append(r / r.std(axis=0))
        dates.append(pd.Timestamp(day))
    return days, dates, dropped


def cross_corr(r, l):
    """corr(SPY_{t-l}, BTC_t): positive l = SPY moves first."""
    x, y = r[:, 0], r[:, 1]
    if l > 0:
        return np.corrcoef(x[:-l], y[l:])[0, 1]
    if l < 0:
        return np.corrcoef(x[-l:], y[:l])[0, 1]
    return np.corrcoef(x, y)[0, 1]


def window_area(r, m):
    """Mean Levy area of the path (cumulative normalised returns) over all rolling windows of m steps in the day."""
    X = np.vstack([np.zeros(2), np.cumsum(r, axis=0)])
    assert m <= len(r)                            # the last window (78 steps) is the whole session
    a = []
    for i in range(len(r) - m + 1):
        P = X[i:i + m + 1] - X[i]
        x, y = P[:, 0], P[:, 1]
        a.append(0.5 * np.sum(x[:-1] * np.diff(y) - y[:-1] * np.diff(x)))
    return float(np.mean(a))


def nw_se(v):
    """Newey-West standard error of the mean over days (Bartlett kernel, the bandwidth of the tests)."""
    v = np.asarray(v, float)
    T = len(v)
    return float(np.sqrt(S.nw_var(v, S.nw_lag(T, 1)) / T))


def nw_t(v):
    return float(np.mean(v) / nw_se(v))


def holm(p):
    """Holm step-down adjusted p-values."""
    p = np.asarray(p, float)
    order, m, run = np.argsort(p), len(p), 0.0
    adj = np.empty(m)
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * p[i]))
        adj[i] = run
    return adj


def compute():
    from scipy.stats import norm
    days, dates, dropped = load_days()
    # the discrete formula equals the Levy area of the chapter's signature code (sigvol.levy_area)
    r0 = days[0][:12]
    P0 = np.vstack([np.zeros(2), np.cumsum(r0, axis=0)])
    assert abs(window_area(r0, 12) - S.levy_area(P0)) < 1e-10
    C = np.array([[cross_corr(r, l) for l in LAGS] for r in days])
    A = np.array([[window_area(r, m) for m in WINDOWS] for r in days])
    T = len(days)
    years = sorted({d.year for d in dates})
    # exploratory family: 12 non-zero lags and 8 windows, two-sided normal p-values of the NW t-statistics
    fam = [(f'lag{l}', nw_t(C[:, j])) for j, l in enumerate(LAGS) if l != 0] + \
          [(f'window{m}', nw_t(A[:, j])) for j, m in enumerate(WINDOWS)]
    p_raw = 2 * norm.sf(np.abs([t for _, t in fam]))
    d1 = C[:, LAGS.index(1)] - C[:, LAGS.index(-1)]
    res = dict(
        n_days=T, n_common_days=T + dropped, n_dropped=dropped,
        start=f'{dates[0]:%Y-%m-%d}', end=f'{dates[-1]:%Y-%m-%d}',
        bars_median=int(np.median([len(r) for r in days])),
        lags=LAGS, windows=WINDOWS,
        ccf_mean=[float(v) for v in C.mean(axis=0)],
        ccf_se=[nw_se(C[:, j]) for j in range(len(LAGS))],
        ccf_se_iid=[float(v) for v in C.std(axis=0, ddof=1) / np.sqrt(T)],
        ccf_t={str(l): nw_t(C[:, j]) for j, l in enumerate(LAGS)},
        holm=dict(family=len(fam), p={k: float(p) for (k, _), p in zip(fam, p_raw)},
                  p_adj={k: float(a) for (k, _), a in zip(fam, holm(p_raw))}),
        lag1_diff=dict(mean=float(d1.mean()), t=nw_t(d1)),
        area={str(m): dict(mean=float(A[:, j].mean()), t=nw_t(A[:, j]), share_pos=float((A[:, j] > 0).mean()))
              for j, m in enumerate(WINDOWS)},
        by_year={str(y): dict(n=int(sum(d.year == y for d in dates)),
                              ccf1=float(C[[d.year == y for d in dates], LAGS.index(1)].mean()),
                              t2=nw_t(A[[d.year == y for d in dates], 0]))
                 for y in years},
        nw_lag=S.nw_lag(T, 1))
    return res, C, A, dates


def chart(res, save_fig, colours):
    import matplotlib.pyplot as plt
    MainBlue, IDAred, Forest, Navy = colours
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.2))
    L = np.array(res['lags'])
    mu, se = np.array(res['ccf_mean']), np.array(res['ccf_se'])
    k = L != 0
    pos, neg = L > 0, L < 0
    a1.bar(L[pos], mu[pos], color=MainBlue, width=0.7, label='Lag l > 0: SPY moves first')
    a1.bar(L[neg], mu[neg], color=IDAred, width=0.7, label='Lag l < 0: Bitcoin moves first')
    a1.errorbar(L[k], mu[k], yerr=1.96 * se[k], fmt='none', ecolor=Navy, elinewidth=0.8, capsize=2,
                label='Pointwise 95% interval (Newey-West)')
    a1.axhline(0, color=Navy, lw=0.6)
    a1.set_xticks(L[k])
    a1.set_xlabel('Lag l (five-minute steps)')
    a1.set_ylabel('Correlation')
    a1.set_title(f"SPY at t - l vs BTC at t (lag 0: {res['ccf_mean'][res['lags'].index(0)]:.2f})")
    W = np.array(res['windows'])
    t = np.array([res['area'][str(m)]['t'] for m in W])
    a2.plot(W * 5, t, '-o', color=Forest, ms=3.5, label='Mean daily Lévy area (SPY, BTC)')
    a2.axhline(1.96, color=Navy, ls='--', lw=0.8, label='t = 1.96 (pointwise)')
    a2.set_xscale('log')
    a2.set_xticks(W * 5)
    a2.set_xticklabels([f'{5 * m}' for m in W[:-1]] + ['390\n(session)'])
    a2.minorticks_off()
    a2.set_xlabel('Window length (minutes)')
    a2.set_ylabel('NW t-statistic')
    a2.set_ylim(0, max(t) * 1.1)
    a2.set_title('Signature lead-lag metric')
    h, lab = [], []
    for ax in (a1, a2):
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            h.append(hh)
            lab.append(ll)
    fig.legend(h, lab, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    fig.tight_layout()
    save_fig('ch20_leadlag')


def main(save_fig=None, colours=None):
    res, C, A, dates = compute()
    if save_fig is not None:
        chart(res, save_fig, colours)
    with open(OUT_JSON, 'w') as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == '__main__':
    import generate_all_charts as g
    out = main(g.save_fig, (g.MainBlue, g.IDAred, g.Forest, g.Navy))
    print(json.dumps({k: out[k] for k in ('n_days', 'n_dropped', 'start', 'end', 'bars_median', 'lag1_diff', 'area',
                                          'by_year', 'holm')},
                     indent=1))

"""
seminar10.py -- Computations of Seminar 10 (MFM): market microstructure
======================================================================
Part A: derivations -- moments and standard error of the Roll estimator, Glosten-Milgrom for general theta,
        the Kyle equilibrium, Almgren-Chriss via the Euler-Lagrange equation, the PIN likelihood (step by step).
Part B: the SPY intraday pattern, spread estimators at two frequencies (and a Monte Carlo of the Roll model),
        illiquidity and the VIX (with a break test), Amihud illiquidity in three markets, volume and price moves
        (with an instrumental variable), the Bitcoin hourly pattern, price discovery between the BET ETF and the index.
Part C: the illiquidity premium (Amihud, 2002) on the BVB, in the US and in crypto.
Results are written to sem10_results.json.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import ASSETS, GROUPS, LABELS, read_market, ohlc, returns, dollar_volume, intraday_spy, intraday_btc  # noqa: E402
from micro import (roll_spread, cs_spread, ar_terms, walk_book, gm_quotes, gm_simulate, kyle, ac_trajectory,  # noqa: E402
                   ac_frontier, roll_mc, price_discovery, pin_loglik)
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray, GROUP_COL, save_fig,  # noqa: E402
                                 legend_outside_bottom, fig_legend_bottom, spy_tod, intraday_spreads, spread_table,
                                 amihud_table, spy_illiq_daily, sqrt_relation, jsonable, AC, START2, START10,
                                 bet_etf_pair)

from case_study_race import race_daily, race_prize, ABO  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42
B = 1000


def boot_days(values_by_day, stat, B=B, seed=SEED, draws=False):
    """Day bootstrap (blocks = whole days): 95% percentile interval for stat(sample of days).
    draws=True also returns the values of the B resamples."""
    rng = np.random.default_rng(seed)
    days = np.array(list(values_by_day.keys()))
    out = []
    for _ in range(B):
        pick = rng.choice(days, len(days), replace=True)
        out.append(stat([values_by_day[d] for d in pick]))
    ci = (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)))
    return (ci + (np.array(out),)) if draws else ci


# =============================================================================
# PART A
# =============================================================================
def a1_roll(var=0.0520, cov=-0.0081, price=20.0, rho_q=0.3):
    """The Roll model: moments, the estimator and its bias when trade signs are autocorrelated.
    With Corr(q_t, q_{t-1}) = rho_q (Markov chain, m independent of q): Cov(dp_t, dp_{t-1}) = -c^2 (1 - rho_q)^2."""
    c = np.sqrt(-cov)
    cov_rho = -c ** 2 * (1 - rho_q) ** 2
    return dict(c=c, s=2 * c, s_pct=100 * 2 * c / price, sig2=var - 2 * c ** 2, share=2 * c ** 2 / var,
                rho=cov / var, var=var, cov=cov, price=price, rho_q=rho_q, cov_rho=cov_rho,
                c_roll_rho=np.sqrt(-cov_rho), bias_pct=100 * rho_q)


def a2_roll_se(var=0.0520, cov=-0.0081, Ts=(78, 250)):
    """Standard error of s_hat = 2 sqrt(-cov_hat) by the delta method; Var(cov_hat) from Bartlett's formula
    for an MA(1) (Gaussian approximation): T Var(cov_hat) -> g0^2 + 3 g1^2."""
    from scipy.stats import norm
    c = np.sqrt(-cov)
    out = dict(var=var, cov=cov, s=2 * c, avar=var ** 2 + 3 * cov ** 2)
    for T in Ts:
        se_g = np.sqrt((var ** 2 + 3 * cov ** 2) / T)
        se_s = se_g / c                               # ds/dg = -1 / sqrt(-g) = -1 / c
        out[T] = dict(se_g=se_g, se_s=se_s, cv=se_s / (2 * c), p_pos=norm.cdf(cov / se_g))
    return out


def gm_spread_formula(theta, mu, dv=20.0):
    """Glosten-Milgrom spread for general theta: a - b = 4 mu theta (1 - theta) dV / (1 - mu^2 (2 theta - 1)^2)."""
    return 4 * mu * theta * (1 - theta) * dv / (1 - mu ** 2 * (2 * theta - 1) ** 2)


def a3_gm(mu=0.3, theta=0.5, vl=90.0, vh=110.0):
    ask, bid, tb, ts = gm_quotes(theta, mu, vl, vh)
    ask2, bid2, tb2, ts2 = gm_quotes(tb, mu, vl, vh)          # after one buy
    a7, b7, _, _ = gm_quotes(0.7, mu, vl, vh)
    return dict(ask=ask, bid=bid, spread=ask - bid, pb_h=mu + (1 - mu) / 2, pb_l=(1 - mu) / 2, th_b=tb, th_s=ts,
                ask2=ask2, bid2=bid2, spread2=ask2 - bid2, th_b2=tb2, spread_07=a7 - b7,
                formula_07=gm_spread_formula(0.7, mu, vh - vl), formula_05=gm_spread_formula(0.5, mu, vh - vl))


def a4_gm_learning(mus=(0.1, 0.3, 0.5), level=108.0, vl=90.0, vh=110.0):
    """After k consecutive buys, the odds of V_H are multiplied by (1 + mu) / (1 - mu) at each buy;
    the bid after k buys is V_L + dV theta_{k-1}, so bid > level requires (k - 1) ln((1 + mu)/(1 - mu)) > ln(o*)."""
    q = (level - vl) / (vh - vl)
    out = {}
    for mu in mus:
        k = 1 + int(np.floor(np.log(q / (1 - q)) / np.log((1 + mu) / (1 - mu)))) + 1
        theta, kk = 0.5, 0
        while True:                                         # direct check with the quotes
            kk += 1
            ask, bid, tb, ts = gm_quotes(theta, mu, vl, vh)
            if bid > level:
                break
            theta = tb
        out[mu] = dict(k=kk - 1, k_formula=k, speed=np.log((1 + mu) / (1 - mu)))   # kk - 1 observed buys
    return out


def a5_kyle(sigma_v=2.0, sigma_u=10_000.0, y=15_000.0, sigma_u2=20_000.0):
    k = kyle(sigma_v, sigma_u)
    k2 = kyle(sigma_v, sigma_u2)
    k.update(sigma_v=sigma_v, sigma_u=sigma_u, y=y, dp=k['lam'] * y, lam100=100 * k['lam'],
             lam2=k2['lam'], profit2=k2['profit'], beta2=k2['beta'])
    return k


def a6_kyle_ols(sigma_v=2.0, sigma_u=10_000.0, p0=50.0, n=200_000, seed=SEED):
    """Simulated Kyle economy: the OLS slope of (p - p0) on y is lambda; an Amihud-type ratio |r| / (p0 |y|)
    estimates lambda / p0^2, and with total volume |x| + |u| instead of |y| it underestimates it."""
    rng = np.random.default_rng(seed)
    k = kyle(sigma_v, sigma_u)
    v = p0 + sigma_v * rng.standard_normal(n)
    x = k['beta'] * (v - p0)
    u = sigma_u * rng.standard_normal(n)
    y = x + u
    p = p0 + k['lam'] * y
    slope = np.polyfit(y, p - p0, 1)[0]
    slope_v = np.polyfit(y, v - p0, 1)[0]
    r = np.abs(p - p0) / p0
    am_net = np.mean(r / (p0 * np.abs(y)))
    am_vol = np.mean(r / (p0 * (np.abs(x) + np.abs(u))))
    return dict(lam=k['lam'], slope=slope, slope_v=slope_v, target=k['lam'] / p0 ** 2, am_net=am_net, am_vol=am_vol,
                am_ratio=am_vol / am_net, p0=p0, var_y=np.var(y), var_y_theory=2 * sigma_u ** 2)


def a7_ac(lam=2e-6):
    """Almgren-Chriss: the continuous-time solution (Euler-Lagrange: x'' = kappa^2 x) and the exact discrete schedule."""
    tau = AC['T'] / AC['N']
    eta_t = AC['eta'] - AC['gamma'] * tau / 2
    kt2 = lam * AC['sigma'] ** 2 / eta_t
    kappa = np.arccosh(kt2 * tau ** 2 / 2 + 1) / tau
    kc = np.sqrt(lam * AC['sigma'] ** 2 / AC['eta'])          # continuous time: eta_tilde -> eta as tau -> 0
    t, x, E, V = ac_trajectory(lam=lam, **AC)
    t0, x0, E0, V0 = ac_trajectory(lam=0, **AC)
    xc = AC['X'] * np.sinh(kc * (AC['T'] - t)) / np.sinh(kc * AC['T'])
    return dict(lam=lam, eta_t=eta_t, kt2=kt2, kappa=kappa, kc=kc, kc2=kc ** 2, x=list(x), xc=list(xc),
                n=list(-np.diff(x)), E=E, sd=np.sqrt(V), E0=E0, sd0=np.sqrt(V0), sinh5=np.sinh(5 * kappa))


def a8_ac():
    return a7_ac(lam=2e-5)


PIN_PAR = dict(alpha=0.3, delta=0.5, mu=400.0, eb=1000.0, es=1000.0)


def pin_posterior(B, S, alpha, delta, mu, eb, es):
    """Posterior probabilities of the three states (no news, bad news, good news) given (B, S)."""
    from scipy.special import softmax
    _, terms = pin_loglik(B, S, alpha, delta, mu, eb, es)
    return softmax(terms)


def a9_pin(B=1450, S=1000, **par):
    """EKOP likelihood of one day: direct evaluation fails numerically, the factorised form does not."""
    import warnings as _w
    par = par or PIN_PAR
    a, d, mu, eb, es = (par[k] for k in ('alpha', 'delta', 'mu', 'eb', 'es'))
    pin = a * mu / (a * mu + eb + es)
    with _w.catch_warnings():
        _w.simplefilter('ignore')
        naive = np.exp(-eb) * np.float64(eb) ** B                 # e^-1000 = 0 and 1000^1450 = inf: 0 * inf = nan
    ll, _ = pin_loglik(B, S, a, d, mu, eb, es)
    post = pin_posterior(B, S, a, d, mu, eb, es)
    return dict(pin=pin, naive=str(naive), exp_small=float(np.exp(-eb)), loglik=ll, p_none=post[0], p_bad=post[1],
                p_good=post[2], B=B, S=S, **par)


def a10_pin():
    """Same parameters: a likely bad-news day (B = 1000, S = 1420), a quiet day (B = S = 1000)
    and PIN when mu doubles."""
    x = a9_pin(B=1000, S=1420)
    q = a9_pin(B=1000, S=1000)
    par = dict(PIN_PAR, mu=800.0)
    pin2 = par['alpha'] * par['mu'] / (par['alpha'] * par['mu'] + par['eb'] + par['es'])
    return dict(bad=dict(p_none=x['p_none'], p_bad=x['p_bad'], p_good=x['p_good'], loglik=x['loglik']),
                quiet=dict(p_none=q['p_none'], p_bad=q['p_bad'], p_good=q['p_good']), pin=x['pin'], pin2=pin2)


# =============================================================================
# PART B
# =============================================================================
def b1_ushape():
    s = intraday_spy()
    x = s.dropna(subset=['r'])
    by_day = {}
    for d, g in x.groupby('date'):
        g = g.set_index('tod')
        by_day[d] = (abs(g['r'].get('09:30', np.nan)), g.loc['11:30':'14:00', 'r'].abs().mean(),
                     g['volume'].iloc[-6:].sum() / g['volume'].sum())
    arr = np.array(list(by_day.values()))
    ratio = np.nanmean(arr[:, 0]) / np.nanmean(arr[:, 1])
    lo, hi = boot_days(by_day, lambda v: np.nanmean([a[0] for a in v]) / np.nanmean([a[1] for a in v]))
    vs = np.nanmean(arr[:, 2])
    vlo, vhi = boot_days(by_day, lambda v: np.nanmean([a[2] for a in v]))
    tod = spy_tod(s)
    # one bootstrap step, explicitly: the first resample (same generator as boot_days)
    rng1 = np.random.default_rng(SEED)
    days = np.array(list(by_day.keys()))
    pick = rng1.choice(days, len(days), replace=True)
    a1 = np.array([by_day[d] for d in pick])
    first = dict(ratio=float(np.nanmean(a1[:, 0]) / np.nanmean(a1[:, 1])), n_unique=int(len(np.unique(pick))),
                 open=float(1e4 * np.nanmean(a1[:, 0])), mid=float(1e4 * np.nanmean(a1[:, 1])),
                 vshare=float(100 * np.nanmean(a1[:, 2])))
    # chart: mean |r| and share of the day's volume by interval, with pointwise day-bootstrap bands
    piv = x.pivot_table(index='date', columns='tod', values='r', aggfunc=lambda v: abs(v).mean())
    vsh = (s['volume'] / s.groupby('date')['volume'].transform('sum')).groupby([s['date'], s['tod']]).sum().unstack()
    rng = np.random.default_rng(SEED)
    bs = np.array([piv.iloc[rng.integers(0, len(piv), len(piv))].mean().values for _ in range(300)])
    lo_b, hi_b = 1e4 * np.nanpercentile(bs, 2.5, axis=0), 1e4 * np.nanpercentile(bs, 97.5, axis=0)
    rng = np.random.default_rng(SEED + 1)
    bv = np.array([vsh.iloc[rng.integers(0, len(vsh), len(vsh))].mean().values for _ in range(300)])
    lo_v, hi_v = 100 * np.percentile(bv, 2.5, axis=0), 100 * np.percentile(bv, 97.5, axis=0)
    k = np.arange(len(piv.columns))
    cols = list(piv.columns)
    i0, i1 = cols.index('11:30'), cols.index('14:00')
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
    ax = axes[0]
    ax.axvspan(i0 - 0.5, i1 + 0.5, color=Teal, alpha=0.12, lw=0, label='Midday window: bars starting 11:30-14:00')
    ax.fill_between(k, lo_b, hi_b, color='#DADADA', alpha=0.8, lw=0, label='Pointwise 95% bootstrap band (resampling days)')
    ax.plot(k, 1e4 * piv.mean().values, color=IDAred, lw=1.2, marker='o', ms=2.5, label='Mean |5-minute return| (bp)')
    ax.plot(0, 1e4 * piv.mean().values[0], 'o', color=MainBlue, ms=7, label='First bar (09:30)')
    ax.set_xticks(k[::12])
    ax.set_xticklabels(cols[::12], fontsize=7.5)
    ax.set_xlabel('Start of the 5-minute bar (New York time)')
    ax.set_ylabel('Mean |return| (bp)')
    ax.set_title('Volatility: high at the open, low at midday', fontsize=9, loc='left')
    ax = axes[1]
    ax.fill_between(k, lo_v, hi_v, color='#DADADA', alpha=0.8, lw=0)
    ax.plot(k, 100 * vsh.mean().values, color=MainBlue, lw=1.2, marker='o', ms=2.5, label='Mean share of daily volume (%)')
    ax.plot(k[-6:], 100 * vsh.mean().values[-6:], 'o', color=Amber, ms=5, label='Last six bars (15:30-15:55)')
    ax.axhline(100 / 78, color=Gray, lw=0.8, ls='--', label='Even volume, 1/78 = 1.28%')
    ax.set_xticks(k[::12])
    ax.set_xticklabels(cols[::12], fontsize=7.5)
    ax.set_xlabel('Start of the 5-minute bar (New York time)')
    ax.set_ylabel('Share of daily volume (%)')
    ax.set_title('Volume: U-shaped, heaviest at the close', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.13, 1, 1))
    save_fig('ch10_sem_ushape')
    return dict(ratio=ratio, lo=lo, hi=hi, open=1e4 * np.nanmean(arr[:, 0]), mid=1e4 * np.nanmean(arr[:, 1]),
                vshare=100 * vs, vlo=100 * vlo, vhi=100 * vhi, n=len(by_day), absr_close=float(tod['absr'].iloc[-1]),
                n_mid_bars=int(i1 - i0 + 1), first=first)


def b2_spreads():
    s = intraday_spy()
    E = intraday_spreads(s)
    by_day = {d: row for d, row in E.iterrows()}
    roll5 = 1e4 * 2 * np.sqrt(max(-E['cov'].mean(), 0))
    rlo, rhi = boot_days(by_day, lambda v: 1e4 * 2 * np.sqrt(max(-np.mean([r['cov'] for r in v]), 0)))
    cs5 = 1e4 * E['cs'].mean()
    clo, chi = boot_days(by_day, lambda v: 1e4 * np.mean([r['cs'] for r in v]))
    ar5 = 1e4 * np.sqrt(max(E['ar2'].mean(), 0))
    alo, ahi = boot_days(by_day, lambda v: 1e4 * np.sqrt(max(np.mean([r['ar2'] for r in v]), 0)))
    tick = 1e4 * (0.01 / E['price']).mean()
    # daily data: moving-block bootstrap with blocks of 20 days
    d = ohlc('SPY', START2)
    cs = cs_spread(d['high'], d['low'], d['close'])
    ar2 = ar_terms(d['close'], d['high'], d['low'])
    dp = np.diff(np.log(d['close'].values))
    pairs = np.column_stack([dp[1:], dp[:-1]])                # pairs (dp_t, dp_{t-1}) for the Roll covariance
    roll_cov = lambda x: np.mean(x[:, 0] * x[:, 1]) - x[:, 0].mean() * x[:, 1].mean()
    rng = np.random.default_rng(SEED)
    n, L = len(cs), 20
    csb, arb, rlb = [], [], []
    for _ in range(B):
        st = rng.integers(0, n - L + 1, n // L + 1)             # possible block starts: 0, ..., n - L
        idx = np.concatenate([np.arange(a, a + L) for a in st])[:n]
        csb.append(1e4 * cs[idx].mean())
        arb.append(1e4 * np.sqrt(max(ar2[idx].mean(), 0)))
        ip = np.minimum(idx, len(pairs) - 1)
        rlb.append(roll_cov(pairs[ip]))
    rlb = np.array(rlb)
    roll_d = 1e4 * 2 * np.sqrt(max(-roll_cov(pairs), 0))
    rlb_s = 1e4 * 2 * np.sqrt(np.maximum(-rlb, 0))
    sd_daily = 1e4 * np.log(d['close']).diff().std()
    res = dict(roll5=roll5, rlo=rlo, rhi=rhi, cs5=cs5, clo=clo, chi=chi, ar5=ar5, alo=alo, ahi=ahi, tick=tick,
               cs_d=1e4 * cs.mean(), cs_dlo=float(np.percentile(csb, 2.5)), cs_dhi=float(np.percentile(csb, 97.5)),
               ar_d=1e4 * np.sqrt(max(ar2.mean(), 0)), ar_dlo=float(np.percentile(arb, 2.5)),
               ar_dhi=float(np.percentile(arb, 97.5)), sd_daily=sd_daily, share_negcov=float((E['cov'] < 0).mean()),
               roll_d=float(roll_d), roll_dlo=float(np.percentile(rlb_s, 2.5)), roll_dhi=float(np.percentile(rlb_s, 97.5)),
               roll_d_pos=float((rlb >= 0).mean()))
    # how often each estimator is truncated at 0 across resamples (the averaged moment has the wrong sign)
    _, _, mc = boot_days(by_day, lambda v: np.mean([r['cov'] for r in v]), draws=True)
    _, _, ma = boot_days(by_day, lambda v: np.mean([r['ar2'] for r in v]), draws=True)
    res.update(trunc_roll5=float((mc >= 0).mean()), trunc_ar5=float((ma <= 0).mean()),
               trunc_ar_d=float((np.array(arb) == 0).mean()), trunc_roll_d=float((rlb >= 0).mean()),
               n_days5=int(len(E)), n_daily=int(len(d)), n_ret5=int(s.dropna(subset=['r']).groupby('date').size().iloc[0] - 1))
    # the same two-year window for the 5-minute bars (sensitivity: frequency without the period effect)
    Em = E.loc[START2:]
    bm = {dd: row for dd, row in Em.iterrows()}
    res.update(n_days5m=int(len(Em)),
               roll5m=float(1e4 * 2 * np.sqrt(max(-Em['cov'].mean(), 0))),
               cs5m=float(1e4 * Em['cs'].mean()), ar5m=float(1e4 * np.sqrt(max(Em['ar2'].mean(), 0))))
    res['roll5mlo'], res['roll5mhi'] = boot_days(bm, lambda v: 1e4 * 2 * np.sqrt(max(-np.mean([r['cov'] for r in v]), 0)))
    res['cs5mlo'], res['cs5mhi'] = boot_days(bm, lambda v: 1e4 * np.mean([r['cs'] for r in v]))
    res['ar5mlo'], res['ar5mhi'] = boot_days(bm, lambda v: 1e4 * np.sqrt(max(np.mean([r['ar2'] for r in v]), 0)))
    fig_b2_estimates(res)
    return res


def fig_b2_estimates(r):
    """Estimates and intervals on a log scale; intervals that reach 0 are cut at the left edge."""
    rows = [('Roll', 'roll5', 'rlo', 'rhi', 'roll5m', 'roll5mlo', 'roll5mhi', 'roll_d', 'roll_dlo', 'roll_dhi'),
            ('Corwin-Schultz', 'cs5', 'clo', 'chi', 'cs5m', 'cs5mlo', 'cs5mhi', 'cs_d', 'cs_dlo', 'cs_dhi'),
            ('Abdi-Ranaldo', 'ar5', 'alo', 'ahi', 'ar5m', 'ar5mlo', 'ar5mhi', 'ar_d', 'ar_dlo', 'ar_dhi')]
    series = [('5-minute bars, Oct 2020 - Sep 2026 (day bootstrap)', MainBlue, 1, -0.22),
              ('5-minute bars, Sep 2024 - Sep 2026 (day bootstrap)', Teal, 4, 0.0),
              ('Daily bars, Sep 2024 - Sep 2026 (20-day block bootstrap)', IDAred, 7, 0.22)]
    left = 0.1
    fig, ax = plt.subplots(figsize=(9, 3.4))
    for i, row in enumerate(rows):
        for lab, c, k, off in series:
            est, lo, hi = r[row[k]], r[row[k + 1]], r[row[k + 2]]
            y = i + off
            ax.hlines(y, max(lo, left), hi, color=c, lw=1.6)
            ax.plot(est, y, 'o', color=c, ms=6, label=lab if i == 0 else None)
            if lo <= left:
                ax.plot(left * 1.02, y, marker='<', color=c, ms=6)
            ax.text(hi * 1.12, y, f'{est:.2f}', va='center', fontsize=7.5, color='black')
    ax.axvline(r['tick'], color=Gray, ls='--', lw=0.9)
    ax.text(r['tick'] * 1.08, -0.42, f"one tick = {r['tick']:.2f} bp", fontsize=7.5, color='black')
    ax.set_xscale('log')
    ax.set_xlim(left, 400)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([x[0] for x in rows])
    ax.invert_yaxis()
    ax.set_xlabel('Relative spread estimate (bp, log scale); a triangle marks an interval that reaches 0')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch10_sem_b2_estimates')


def b2_mc(E):
    """Monte Carlo under the Roll model, calibrated to SPY (same settings as roll_small_sample): distributions of the
    share of days with a positive covariance and of the pooled Roll estimate, for a one-tick spread and no spread."""
    n = 77
    v = E['var'].mean()
    c_tick = (0.01 / E['price']).mean() / 2
    obs_pos = float((E['cov'] > 0).mean())
    obs_roll = float(1e4 * 2 * np.sqrt(max(-E['cov'].mean(), 0)))
    g1 = (E['cov'].mean() + v / n) / (1 - 2 / n)
    corr = float(1e4 * 2 * np.sqrt(max(-g1, 0)))
    sims = {}
    for tag, c in [('tick', c_tick), ('zero', 0.0)]:
        sig = np.sqrt(v - 2 * c ** 2)
        cov = np.array([roll_mc(c, sig, T=n + 1, R=len(E), seed=SEED + b) for b in range(200)])
        sims[tag] = dict(pos=(cov > 0).mean(axis=1), pooled=1e4 * 2 * np.sqrt(np.clip(-cov.mean(axis=1), 0, None)))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.3))
    for ax, key, xl, obs in [(axes[0], 'pos', 'Share of days with a positive covariance (%)', 100 * obs_pos),
                             (axes[1], 'pooled', 'Pooled Roll estimate (bp)', obs_roll)]:
        sc = 100 if key == 'pos' else 1
        for tag, c, lab in [('zero', MainBlue, 'Simulated, no spread (c = 0)'),
                            ('tick', Amber, f'Simulated, one-tick spread (c = {1e4 * c_tick:.2f} bp)')]:
            ax.hist(sc * sims[tag][key], bins=25, color=c, alpha=0.55, label=lab)
        ax.axvline(obs, color=IDAred, lw=1.6, label='Observed, SPY 5-minute bars')
        if key == 'pooled':
            ax.axvline(corr, color=Purple, lw=1.4, ls='--', label='Observed, bias-corrected')
        ax.set_xlabel(xl)
        ax.set_ylabel('Number of simulated samples (of 200)')
    axes[0].set_title('Positive covariances are common even under Roll', fontsize=9, loc='left')
    axes[1].set_title('Demeaning alone produces about 2 bp', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + [h2[-1]], l1 + [l2[-1]], ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.14, 1, 1))
    save_fig('ch10_sem_b2_mc')
    return dict(pos_tick=float(sims['tick']['pos'].mean()), pos_zero=float(sims['zero']['pos'].mean()),
                roll_tick=float(sims['tick']['pooled'].mean()), roll_zero=float(sims['zero']['pooled'].mean()),
                obs_pos=obs_pos, obs_roll=obs_roll, roll_corr=corr, var_bar=float(v), n=n, n_days=int(len(E)))


def b3_cross():
    T = spread_table()
    A = amihud_table()
    rows = []
    for k in ASSETS:
        r = returns(k, START2)
        ppy = 365 if ASSETS[k][2] == 'Crypto' else 252
        rows.append(dict(key=k, grp=ASSETS[k][2], cs=T[k]['cs'], ar=T[k]['ar'], vol=100 * r.std() * np.sqrt(ppy),
                         illiq=A[k]['illiq'], dv=A[k]['dv_med']))
    t = pd.DataFrame(rows).set_index('key')
    rho_cs_vol = stats.spearmanr(t['cs'], t['vol'])
    rho_il_vol = stats.spearmanr(t['illiq'], t['vol'])
    rho_cs_il = stats.spearmanr(t['cs'], t['illiq'])
    rho_il_dv = stats.spearmanr(t['illiq'], t['dv'])
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7))
    show = {'SPY', 'GME', 'MSTR', 'TLV', 'H2O', 'TEL', 'TVBETETF', 'BTC', 'DOGE'}
    for g, c in GROUP_COL.items():
        m = t['grp'] == g
        axes[0].scatter(t.loc[m, 'vol'], t.loc[m, 'cs'], color=c, s=26, label=g)
        axes[1].scatter(t.loc[m, 'dv'], t.loc[m, 'illiq'], color=c, s=26)
        axes[2].scatter(t.loc[m, 'illiq'], t.loc[m, 'cs'], color=c, s=26)
    for k in show:
        axes[0].annotate(LABELS[k], (t.loc[k, 'vol'], t.loc[k, 'cs']), fontsize=6.5, color='black',
                         xytext=(3, 2), textcoords='offset points')
        axes[1].annotate(LABELS[k], (t.loc[k, 'dv'], t.loc[k, 'illiq']), fontsize=6.5, color='black',
                         xytext=(3, 2), textcoords='offset points')
        axes[2].annotate(LABELS[k], (t.loc[k, 'illiq'], t.loc[k, 'cs']), fontsize=6.5, color='black',
                         xytext=(3, 2), textcoords='offset points')
    axes[0].set_xlabel('Annualised volatility (%)')
    axes[0].set_ylabel('Corwin-Schultz spread (bp)')
    axes[0].set_title(f'(1) Spearman {rho_cs_vol.statistic:.2f}: tracks volatility', fontsize=9, loc='left')
    for ax in axes[1:]:
        ax.set_xscale('log')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('Median daily traded value (USD million)')
    axes[1].set_ylabel('Amihud illiquidity (bp per USD 1m)')
    axes[1].set_title(f'(2) Spearman {rho_il_dv.statistic:.2f}: tracks traded value', fontsize=9, loc='left')
    axes[2].set_xlabel('Amihud illiquidity (bp per USD 1m)')
    axes[2].set_ylabel('Corwin-Schultz spread (bp)')
    axes[2].set_title(f'(3) Spearman {rho_cs_il.statistic:.2f}: the two disagree', fontsize=9, loc='left')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend_bottom(fig, h, [x + ' (daily bars, Sep 2024 - Sep 2026)' for x in l], ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_cross')
    grp_stats = {g: dict(cs_med=float(t.loc[t['grp'] == g, 'cs'].median()), ar_med=float(t.loc[t['grp'] == g, 'ar'].median()),
                         ar_zero=int((t.loc[t['grp'] == g, 'ar'] == 0).sum()), n=int((t['grp'] == g).sum()))
                 for g in ('US', 'BVB', 'Crypto')}
    return dict(rho_cs_vol=float(rho_cs_vol.statistic), p_cs_vol=float(rho_cs_vol.pvalue),
                rho_il_vol=float(rho_il_vol.statistic), rho_cs_il=float(rho_cs_il.statistic),
                rho_il_dv=float(rho_il_dv.statistic), p_il_dv=float(rho_il_dv.pvalue),
                n=int(len(t)), n_ar_zero=int((t['ar'] == 0).sum()),
                bvb_cs_med=float(t.loc[t['grp'] == 'BVB', 'cs'].median()), us_cs_med=float(t.loc[t['grp'] == 'US', 'cs'].median()),
                cr_cs_med=float(t.loc[t['grp'] == 'Crypto', 'cs'].median()), groups=grp_stats,
                p_cs_il=float(rho_cs_il.pvalue), table=t.round(4).to_dict(orient='index'))


def b4_illiq_vix():
    s = intraday_spy()
    ill = spy_illiq_daily(s)
    vix = read_market('VIX.INDX')['close'].rename('vix')
    j = pd.concat([ill, vix], axis=1, join='inner').dropna()
    y, X = np.log(j['illiq']), sm.add_constant(np.log(j['vix']))
    ols = sm.OLS(y, X).fit()
    hac = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 20})
    # control for the level of traded value (trend)
    dvd = s.groupby('date')['dv'].sum().rename('dv')
    j2 = pd.concat([j, dvd], axis=1, join='inner').dropna()
    X2 = sm.add_constant(pd.DataFrame({'lvix': np.log(j2['vix']), 't': np.arange(len(j2)) / 252}))
    hac2 = sm.OLS(np.log(j2['illiq']), X2).fit(cov_type='HAC', cov_kwds={'maxlags': 20})
    rho1 = float(np.corrcoef(ols.resid[1:], ols.resid[:-1])[0, 1])
    # sub-task 4, elasticity stability: break at the middle of the sample (date fixed before estimation), HAC Wald test
    mid = j.index[len(j) // 2]
    post = (j.index >= mid).astype(float)
    X3 = sm.add_constant(pd.DataFrame({'lvix': np.log(j['vix']), 'post': post, 'lvix_post': post * np.log(j['vix'])},
                                      index=j.index))
    hac3 = sm.OLS(y, X3).fit(cov_type='HAC', cov_kwds={'maxlags': 20})
    w = hac3.wald_test('lvix_post = 0', scalar=True)
    cv3 = hac3.cov_params()
    se_post = float(np.sqrt(cv3.loc['lvix', 'lvix'] + cv3.loc['lvix_post', 'lvix_post'] + 2 * cv3.loc['lvix', 'lvix_post']))
    fig_b4(j, ols, hac, hac2, hac3, se_post, mid)
    return dict(se_post=se_post, wald=float(w.statistic), se_pre=float(hac3.bse['lvix']), a=float(hac.params.iloc[0]),
                illiq_mean=float(j['illiq'].mean()), vix_mean=float(j['vix'].mean()),
                start=j.index[0].strftime('%Y-%m-%d'), end=j.index[-1].strftime('%Y-%m-%d'), b=float(hac.params.iloc[1]), se_ols=float(ols.bse.iloc[1]), se_hac=float(hac.bse.iloc[1]),
                brk=mid.strftime('%Y-%m-%d'), b_pre=float(hac3.params['lvix']),
                b_post=float(hac3.params['lvix'] + hac3.params['lvix_post']), d_brk=float(hac3.params['lvix_post']),
                se_brk=float(hac3.bse['lvix_post']), p_brk=float(w.pvalue),
                lo=float(hac.params.iloc[1] - 1.96 * hac.bse.iloc[1]), hi=float(hac.params.iloc[1] + 1.96 * hac.bse.iloc[1]),
                r2=float(ols.rsquared), n=int(len(j)), rho1=rho1, b2=float(hac2.params['lvix']),
                se2=float(hac2.bse['lvix']), trend=float(hac2.params['t']), se_trend=float(hac2.bse['t']))


def fig_b4(j, ols, hac, hac2, hac3, se_post, mid):
    """The log-log relation with the OLS line, the residual autocorrelation and the HAC intervals of the elasticity."""
    x, y = np.log(j['vix']), np.log(j['illiq'])
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), gridspec_kw=dict(width_ratios=[1.1, 1, 1.1]))
    ax = axes[0]
    ax.scatter(x, y, s=4, color=MainBlue, alpha=0.35, label='One trading day')
    xs = np.linspace(x.min(), x.max(), 20)
    ax.plot(xs, ols.params.iloc[0] + ols.params.iloc[1] * xs, color=IDAred, lw=1.6,
            label=f'OLS fit, slope {ols.params.iloc[1]:.2f}')
    ax.set_xlabel('log VIX')
    ax.set_ylabel('log intraday illiquidity')
    ax.set_title('(1) Elasticity close to 1', fontsize=9, loc='left')
    ax = axes[1]
    e = ols.resid.values
    lags = np.arange(1, 31)
    acf = [np.corrcoef(e[l:], e[:-l])[0, 1] for l in lags]
    ax.bar(lags, acf, color=Amber, width=0.7, label='Residual autocorrelation')
    b = 1.96 / np.sqrt(len(e))
    ax.axhspan(-b, b, color='#DADADA', alpha=0.8, lw=0)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag (trading days)')
    ax.set_ylabel('Autocorrelation')
    ax.set_title('(2) Residuals are persistent', fontsize=9, loc='left')
    ax = axes[2]
    rows = [('Baseline, OLS SE', ols.params.iloc[1], ols.bse.iloc[1], MainBlue),
            ('Baseline, HAC SE', hac.params.iloc[1], hac.bse.iloc[1], IDAred),
            ('With time trend, HAC', hac2.params['lvix'], hac2.bse['lvix'], Forest),
            (f'Before {mid:%d %b %Y}, HAC', hac3.params['lvix'], hac3.bse['lvix'], Purple),
            (f'From {mid:%d %b %Y}, HAC', hac3.params['lvix'] + hac3.params['lvix_post'], se_post, Teal)]
    for i, (lab, bb, se, c) in enumerate(rows):
        ax.hlines(i, bb - 1.96 * se, bb + 1.96 * se, color=c, lw=2)
        ax.plot(bb, i, 'o', color=c, ms=6)
        ax.text(bb + 1.96 * se + 0.03, i, f'{bb:.2f}', va='center', fontsize=7.5, color='black')
    ax.axvline(1, color=Gray, ls='--', lw=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.7)
    ax.set_xlabel('Elasticity with 95% interval')
    ax.set_title('(3) Specifications', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_b4')


def b5_amihud_groups():
    per = {}
    for a, b in [('2024-09-19', '2025-09-18'), ('2025-09-19', '2026-09-18')]:
        per[a[:4]] = {k: float((1e4 * returns(k, a, b).abs() / (dollar_volume(k, a, b) / 1e6)).dropna().mean())
                      for k in ASSETS}
    p1, p2 = pd.Series(per['2024']), pd.Series(per['2025'])
    rho = stats.spearmanr(p1, p2)
    A = amihud_table()
    il = pd.Series({k: v['illiq'] for k, v in A.items()})
    grp = pd.Series({k: v[2] for k, v in ASSETS.items()})
    rng = np.random.default_rng(SEED)
    ratios = []
    for _ in range(B):
        bb = il[grp == 'BVB'].sample(frac=1, replace=True, random_state=rng.integers(1e9)).median()
        uu = il[grp == 'US'].sample(frac=1, replace=True, random_state=rng.integers(1e9)).median()
        ratios.append(bb / uu)
    fig_b5(il, grp, np.array(ratios), p1, p2, float(il[grp == 'BVB'].median() / il[grp == 'US'].median()))
    return dict(rho=float(rho.statistic), p=float(rho.pvalue), med_bvb=float(il[grp == 'BVB'].median()),
                med_us=float(il[grp == 'US'].median()), med_cr=float(il[grp == 'Crypto'].median()),
                ratio=float(il[grp == 'BVB'].median() / il[grp == 'US'].median()),
                lo=float(np.percentile(ratios, 2.5)), hi=float(np.percentile(ratios, 97.5)))


def fig_b5(il, grp, ratios, p1, p2, ratio):
    """Amihud by asset (log scale), bootstrap distribution of the ratio of medians, rankings in the two years."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
    ax = axes[0]
    xpos = 0
    for g in ('US', 'Crypto', 'BVB'):
        v = il[grp == g].sort_values()
        xs = np.arange(xpos, xpos + len(v))
        ax.scatter(xs, v.values, color=GROUP_COL[g], s=24, label=g)
        ax.hlines(v.median(), xs[0] - 0.4, xs[-1] + 0.4, color=GROUP_COL[g], lw=1.4)
        xpos += len(v) + 1
    ax.set_yscale('log')
    ax.set_xticks([])
    ax.set_ylabel('Amihud ratio (bp per USD 1m, log)')
    ax.set_title('(1) Assets and group medians (lines)', fontsize=9, loc='left')
    ax = axes[1]
    ax.hist(np.log10(ratios), bins=30, color=Purple, alpha=0.7, label='Bootstrap draws of BVB median / US median')
    lo, hi = np.percentile(ratios, [2.5, 97.5])
    for v_, ls in [(lo, ':'), (hi, ':'), (ratio, '-')]:
        ax.axvline(np.log10(v_), color=IDAred, ls=ls, lw=1.3)
    ax.set_xlabel('log10 of the ratio (red: estimate and 95% interval)')
    ax.set_ylabel('Draws (of 1000)')
    ax.set_title('(2) Resampling assets within groups', fontsize=9, loc='left')
    ax = axes[2]
    for g in ('US', 'BVB', 'Crypto'):
        m = (grp == g)
        ax.scatter(p1[m.index[m]], p2[m.index[m]], color=GROUP_COL[g], s=22)
    lim = [min(p1.min(), p2.min()) / 2, max(p1.max(), p2.max()) * 2]
    ax.plot(lim, lim, color=Gray, lw=0.8, ls='--')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Sep 2024 - Sep 2025')
    ax.set_ylabel('Sep 2025 - Sep 2026')
    ax.set_title('(3) Year-on-year: stable ranking', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=4, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_b5')


def b6_sqrt():
    s = intraday_spy()
    x, g, slope, _ = sqrt_relation(s)
    days = x['date'].unique()
    by = {d: grp for d, grp in x.groupby('date')}
    bins = np.quantile(x['part'], np.linspace(0, 1, 21))
    rng = np.random.default_rng(SEED)
    sl = []
    for _ in range(300):
        pick = rng.choice(days, len(days), replace=True)
        xx = pd.concat([by[d] for d in pick])
        gg = xx.groupby(pd.cut(xx['part'], bins, include_lowest=True)).agg(v=('part', 'mean'), z=('z', 'mean')).dropna()
        sl.append(np.polyfit(np.log(gg['v']), np.log(gg['z']), 1)[0])
    lo, hi = np.percentile(sl, [2.5, 97.5])
    # on individual bars (not groups)
    y = np.log(x['r'].abs() + 1e-6) - np.log(x.groupby('date')['r'].transform('std'))
    raw = sm.OLS(y, sm.add_constant(np.log(x['part']))).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(x['date'])[0]})
    # zero returns: ln|r| is undefined; constant 1e-6 (0.01 bp) and, as a sensitivity check, dropping bars with r = 0
    nz = (x['r'] != 0).values
    raw_nz = sm.OLS(y[nz], sm.add_constant(np.log(x['part'][nz]))).fit(cov_type='cluster',
                                                                       cov_kwds={'groups': pd.factorize(x['date'][nz])[0]})
    # sub-task 3, instrumental variable: relative volume of the same bar (same time of day) on the previous day
    x = x.assign(ly=y, lv=np.log(x['part']))
    x['lv_lag'] = x.groupby('tod')['lv'].shift(1)             # bars are in time order; a shift within the time of day = the previous day
    x['ly_lag'] = x.groupby('tod')['ly'].shift(1)
    z = x.dropna(subset=['lv_lag', 'ly_lag'])
    gid = pd.factorize(z['date'])[0]
    fs = sm.OLS(z['lv'], sm.add_constant(z['lv_lag'])).fit(cov_type='cluster', cov_kwds={'groups': gid})
    Z = sm.add_constant(z['lv_lag']).values
    Xe = sm.add_constant(z['lv']).values
    Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ Xe)               # projection of the regressors on the instruments
    b_iv = np.linalg.solve(Pz.T @ Xe, Pz.T @ z['ly'].values)
    e = z['ly'].values - Xe @ b_iv
    A = np.linalg.inv(Pz.T @ Pz)
    meat = sum(np.outer(Pz[gid == gg].T @ e[gid == gg], Pz[gid == gg].T @ e[gid == gg]) for gg in np.unique(gid))
    se_iv = np.sqrt(np.diag(A @ meat @ A))
    red = np.corrcoef(z['ly'], z['ly_lag'])[0, 1]            # yesterday's |r| at the same time: the channel that violates exclusion
    fig_b6(g, slope, (lo, hi), raw, raw_nz, b_iv[1], se_iv[1])
    return dict(slope=float(slope), lo=float(lo), hi=float(hi), n=int(len(x)), n_days=int(len(days)),
                raw=float(raw.params.iloc[1]), raw_se=float(raw.bse.iloc[1]), zero_share=float(1 - nz.mean()),
                raw_nz=float(raw_nz.params.iloc[1]), raw_nz_se=float(raw_nz.bse.iloc[1]), fs=float(fs.params.iloc[1]),
                fs_t=float(fs.tvalues.iloc[1]), iv=float(b_iv[1]), iv_se=float(se_iv[1]), n_iv=int(len(z)),
                corr_absr_lag=float(red))


def fig_b6(g, slope, ci, raw, raw_nz, iv, iv_se):
    """The grouped relation (log-log) with the reference slope 0.5 and the intervals of the four slope estimates."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4))
    ax = axes[0]
    lx, lz = np.log(g['v'].values), np.log(g['z'].values)
    ax.plot(lx, lz, 'o', color=MainBlue, ms=5, label='20 groups of bars by relative volume')
    b0 = np.polyfit(lx, lz, 1)
    xs = np.linspace(lx.min(), lx.max(), 10)
    ax.plot(xs, b0[1] + b0[0] * xs, color=IDAred, lw=1.5, label=f'Fitted slope {slope:.2f}')
    ax.plot(xs, lz.mean() + 0.5 * (xs - lx.mean()), color=Gray, lw=1.0, ls='--', label='Reference slope 0.5')
    ax.set_xlabel('log mean relative volume')
    ax.set_ylabel('log mean normalised |return|')
    ax.set_title('(1) Concave, flatter than a square root', fontsize=9, loc='left')
    ax = axes[1]
    rows = [('Grouped OLS (day bootstrap)', slope, ci[0], ci[1], MainBlue),
            ('Bar-level OLS (clustered)', raw.params.iloc[1], raw.params.iloc[1] - 1.96 * raw.bse.iloc[1],
             raw.params.iloc[1] + 1.96 * raw.bse.iloc[1], IDAred),
            ('Bar-level OLS, r = 0 dropped', raw_nz.params.iloc[1], raw_nz.params.iloc[1] - 1.96 * raw_nz.bse.iloc[1],
             raw_nz.params.iloc[1] + 1.96 * raw_nz.bse.iloc[1], Amber),
            ('IV, lagged same-bar volume', iv, iv - 1.96 * iv_se, iv + 1.96 * iv_se, Purple)]
    for i, (lab, bb, l_, h_, c) in enumerate(rows):
        ax.hlines(i, l_, h_, color=c, lw=2)
        ax.plot(bb, i, 'o', color=c, ms=6)
        ax.text(h_ + 0.012, i, f'{bb:.3f}', va='center', fontsize=7.5, color='black')
    ax.axvline(0.5, color=Gray, ls='--', lw=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.6)
    ax.set_xlabel('Slope with 95% interval (dashed: 0.5)')
    ax.set_title('(2) Four estimates of the slope', fontsize=9, loc='left')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend_bottom(fig, h, l, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_b6')


def b7_btc():
    b = intraday_btc().dropna(subset=['r'])
    wk = b.index.dayofweek >= 5
    h = b.index.hour
    by_day = {}
    for d, g in b.groupby('date'):
        hh = g.index.hour
        by_day[d] = (g['r'].abs()[(hh >= 13) & (hh < 17)].mean(), g['r'].abs()[(hh >= 3) & (hh < 11)].mean(),
                     g['r'].abs().mean(), d.dayofweek >= 5)
    wd = {d: v for d, v in by_day.items() if not v[3]}
    ratio = np.nanmean([v[0] for v in wd.values()]) / np.nanmean([v[1] for v in wd.values()])
    lo, hi = boot_days(wd, lambda v: np.nanmean([a[0] for a in v]) / np.nanmean([a[1] for a in v]))
    wkr = np.nanmean([v[2] for v in by_day.values() if not v[3]]) / np.nanmean([v[2] for v in by_day.values() if v[3]])
    lo2, hi2 = boot_days(by_day, lambda v: np.nanmean([a[2] for a in v if not a[3]]) / np.nanmean([a[2] for a in v if a[3]]))
    nb = b.groupby('date').size()                                     # bars with a valid return per day (out of 288)
    cover = dict(full=int((nb == 288).sum()), min=int(nb.min()), med=float(nb.median()),
                 n_wd=int(sum(1 for v in by_day.values() if not v[3])), n_we=int(sum(1 for v in by_day.values() if v[3])))
    fig_b7(b, (ratio, lo, hi), (wkr, lo2, hi2))
    return dict(ratio=float(ratio), lo=lo, hi=hi, wk=float(wkr), wklo=lo2, wkhi=hi2, n_days=len(by_day), cover=cover,
                us_d=float(1e4 * np.nanmean([v[0] for v in wd.values()])), asia_d=float(1e4 * np.nanmean([v[1] for v in wd.values()])),
                wd_d=float(1e4 * np.nanmean([v[2] for v in by_day.values() if not v[3]])),
                we_d=float(1e4 * np.nanmean([v[2] for v in by_day.values() if v[3]])),
                us=float(1e4 * b['r'].abs()[(~wk) & (h >= 13) & (h < 17)].mean()),
                asia=float(1e4 * b['r'].abs()[(~wk) & (h >= 3) & (h < 11)].mean()))


def fig_b7(b, r1, r2):
    """Hourly profile of mean |r| (daily mean by hour, then mean over days), weekdays and weekends, with
    day-bootstrap bands; the two ratios with their intervals."""
    piv = b.assign(hour=b.index.hour).pivot_table(index='date', columns='hour', values='r', aggfunc=lambda v: v.abs().mean())
    we = piv.index.dayofweek >= 5
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.3), gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axes[0]
    for m, c, lab, sd in [(~we, MainBlue, 'Weekdays', 1), (we, Amber, 'Weekends', 2)]:
        P = piv[m]
        rng = np.random.default_rng(SEED + sd)
        bs = np.array([P.iloc[rng.integers(0, len(P), len(P))].mean().values for _ in range(300)])
        ax.fill_between(piv.columns, 1e4 * np.percentile(bs, 2.5, axis=0), 1e4 * np.percentile(bs, 97.5, axis=0),
                        color='#DADADA', alpha=0.8, lw=0)
        ax.plot(piv.columns, 1e4 * P.mean().values, color=c, lw=1.4, marker='o', ms=3, label=f'{lab}: mean |5-minute return|')
    ax.axvspan(12.6, 16.4, color=IDAred, alpha=0.08, lw=0, label='US morning, 13:00-17:00 UTC')
    ax.axvspan(2.6, 10.4, color=Forest, alpha=0.08, lw=0, label='Asian and European morning, 03:00-11:00 UTC')
    ax.set_xlabel('Hour (UTC)')
    ax.set_ylabel('Mean |return| (bp)')
    ax.set_title('Bitcoin keeps the clock of traditional markets', fontsize=9, loc='left')
    ax = axes[1]
    for i, (lab, (est, lo, hi), c) in enumerate([('US / Asian-European\nmorning (weekdays)', r1, IDAred),
                                                  ('Weekdays / weekends', r2, MainBlue)]):
        ax.hlines(i, lo, hi, color=c, lw=2)
        ax.plot(est, i, 'o', color=c, ms=6)
        ax.text(hi + 0.03, i, f'{est:.2f}', va='center', fontsize=8, color='black')
    ax.axvline(1, color=Gray, ls='--', lw=0.8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['US / Asian-European\nmorning (weekdays)', 'Weekdays / weekends'], fontsize=8)
    ax.set_ylim(-0.6, 1.6)
    ax.invert_yaxis()
    ax.set_xlim(0.9, 2.2)
    ax.set_xlabel('Ratio of mean |return| with 95% interval')
    ax.set_title('Both ratios exclude 1', fontsize=9, loc='left')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend_bottom(fig, h, l, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.14, 1, 1))
    save_fig('ch10_sem_b7')


def b8_price_discovery(B=B, L=20, seed=SEED):
    """The Patria-TVBETETF and the BET-TR index: VECM with the vector (1, -1), Hasbrouck share bounds, the
    Gonzalo-Granger share; moving-block bootstrap intervals (blocks of L days) over the VECM pairs (X_t, Y_t);
    then the two halves of the sample."""
    from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_order
    y = bet_etf_pair().values
    p = max(int(select_order(y, maxlags=10, deterministic='co').bic), 1)   # BIC over 1..10 lags of dy
    jo = coint_johansen(y, 0, p)                                           # unrestricted constant
    base = price_discovery(y, p)
    dy = np.diff(y, axis=0)
    z = (y[:, 0] - y[:, 1])[:-1]
    X = np.array([[1.0, z[t]] + [v for i in range(1, p + 1) for v in dy[t - i]] for t in range(p, len(dy))])
    Y = dy[p:]
    rng = np.random.default_rng(seed)
    n = len(Y)
    draws = []
    for _ in range(B):
        st = rng.integers(0, n - L + 1, n // L + 1)
        idx = np.concatenate([np.arange(a, a + L) for a in st])[:n]
        Xb, Yb = X[idx], Y[idx]
        Bb = np.linalg.lstsq(Xb, Yb, rcond=None)[0]
        U = Yb - Xb @ Bb
        Om = U.T @ U / (n - X.shape[1])
        al = Bb[1]
        ap = np.array([-al[1], al[0]])
        ISs = []
        for order in ([0, 1], [1, 0]):
            F = np.linalg.cholesky(Om[np.ix_(order, order)])
            v = (ap[order] @ F) ** 2 / (ap @ Om @ ap)
            ISs.append(v[np.argsort(order)][1])
        draws.append((al[0], al[1], ap[1] / ap.sum(), min(ISs), max(ISs)))
    d = np.array(draws)
    ci = lambda k: [float(x) for x in np.percentile(d[:, k], [2.5, 97.5])]
    half = len(y) // 2
    h1, h2 = price_discovery(y[:half], p), price_discovery(y[half:], p)
    fig_b8(bet_etf_pair(), base, d, h1, h2)
    return dict(basis_mean=float(100 * np.mean(y[:, 0] - y[:, 1])), start=bet_etf_pair().index[0].strftime('%Y-%m-%d'),
                end=bet_etf_pair().index[-1].strftime('%Y-%m-%d'), a_etf=float(base['alpha'][0]), a_idx=float(base['alpha'][1]), t_etf=float(base['t'][0]),
                t_idx=float(base['t'][1]), cs_idx=float(base['cs'][1]), is_idx_lo=float(base['is_lo'][1]),
                is_idx_hi=float(base['is_hi'][1]), ci_a_etf=ci(0), ci_a_idx=ci(1), ci_cs_idx=ci(2), ci_is_lo=ci(3),
                ci_is_hi=ci(4), h1_a_etf=float(h1['alpha'][0]), h1_t_etf=float(h1['t'][0]), h2_a_etf=float(h2['alpha'][0]),
                h2_t_etf=float(h2['t'][0]), h1_a_idx=float(h1['alpha'][1]), h2_a_idx=float(h2['alpha'][1]),
                h1_t_idx=float(h1['t'][1]), h2_t_idx=float(h2['t'][1]), corr=base['corr'], n=int(base['n']), p=p,
                trace=float(jo.lr1[0]), cv=float(jo.cvt[0, 1]), trace1=float(jo.lr1[1]), cv1=float(jo.cvt[1, 1]))


def fig_b8(yl, base, d, h1, h2):
    """Rebased prices and the ETF - index basis; adjustment coefficients and shares, with bootstrap intervals."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.2))
    ax = axes[0]
    ax.plot(yl.index, 100 * np.exp(yl['etf'] - yl['etf'].iloc[0]), color=IDAred, lw=1.1, label='Patria-TVBETETF (close)')
    ax.plot(yl.index, 100 * np.exp(yl['idx'] - yl['idx'].iloc[0]), color=MainBlue, lw=1.1, label='BET-TR index')
    ax.set_ylabel('Rebased, first day = 100')
    ax.set_title('(1) Two prices of one basket', fontsize=9, loc='left')
    ax = axes[1]
    bs = 100 * (yl['etf'] - yl['idx'])
    ax.plot(yl.index, bs - bs.mean(), color=Purple, lw=0.9, label='Basis: log ETF - log index, demeaned (%)')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_ylabel('Basis (%)')
    ax.set_title('(2) The basis mean-reverts: cointegration', fontsize=9, loc='left')
    for a in axes:
        a.tick_params(axis='x', labelsize=7.5)
    h1_, l1_ = axes[0].get_legend_handles_labels()
    h2_, l2_ = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1_ + h2_, l1_ + l2_, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch10_sem_b8_prices')
    ci = lambda k: np.percentile(d[:, k], [2.5, 97.5])
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.2))
    ax = axes[0]
    rows = [('ETF, full sample', base['alpha'][0], base['alpha'][0] / base['t'][0], ci(0), IDAred),
            ('Index, full sample', base['alpha'][1], base['alpha'][1] / base['t'][1], ci(1), MainBlue),
            ('ETF, first half', h1['alpha'][0], h1['alpha'][0] / h1['t'][0], None, Amber),
            ('ETF, second half', h2['alpha'][0], h2['alpha'][0] / h2['t'][0], None, Forest)]
    for i, (lab, a, se, c_, col) in enumerate(rows):
        ax.hlines(i - 0.12, a - 1.96 * se, a + 1.96 * se, color=col, lw=2, label='Asymptotic 95% interval' if i == 0 else None)
        if c_ is not None:
            ax.hlines(i + 0.12, c_[0], c_[1], color=col, lw=2, ls=':', label='Block-bootstrap 95% interval' if i == 0 else None)
        ax.plot(a, i - 0.12, 'o', color=col, ms=6)
    ax.axvline(0, color=Gray, ls='--', lw=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel('Adjustment coefficient $\\alpha$')
    ax.set_title('(1) Only the ETF adjusts, and weakly', fontsize=9, loc='left')
    ax = axes[1]
    lo, hi = base['is_lo'][1], base['is_hi'][1]
    ax.barh(0, hi - lo, left=lo, height=0.35, color=Teal, alpha=0.6, label='Index information share: ordering bounds')
    for k, v in [(3, lo), (4, hi)]:
        c_ = ci(k)
        ax.hlines(0.32, c_[0], c_[1], color=MainBlue if k == 3 else IDAred, lw=2,
                  label='Bootstrap 95% interval, lower bound' if k == 3 else 'Bootstrap 95% interval, upper bound')
    ax.plot(base['cs'][1], 1, 'o', color=Purple, ms=6, label='Index component share (point)')
    c_ = ci(2)
    ax.hlines(1, c_[0], c_[1], color=Purple, lw=2, ls=':')
    ax.axvline(0, color=Gray, lw=0.6)
    ax.axvline(1, color=Gray, lw=0.6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Information share', 'Component share'], fontsize=8)
    ax.set_ylim(-0.5, 1.5)
    ax.invert_yaxis()
    ax.set_xlabel('Share of price discovery attributed to the index')
    ax.set_title('(2) Bounds are wide at daily frequency', fontsize=9, loc='left')
    h1_, l1_ = axes[0].get_legend_handles_labels()
    h2_, l2_ = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1_ + h2_, l1_ + l2_, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.16, 1, 1))
    save_fig('ch10_sem_b8_shares')


# =============================================================================
# PART C: the illiquidity premium (Amihud 2002, time-series effect)
# =============================================================================
C_MARKETS = {
    'BVB': dict(ret=('BETTR.INDX', 'close'), keys=[k for k in GROUPS['BVB'] if k != 'TVBETETF']),
    'US': dict(ret=('SPY.US', 'adjusted_close'), keys=[k for k in GROUPS['US'] if k != 'SPY']),
    'Crypto': dict(ret=('BTC-USD.CC', 'close'), keys=[k for k in GROUPS['Crypto'] if k != 'BTC']),
}


def market_illiq(keys, start='2016-09-19'):
    """Monthly market illiquidity: cross-sectional mean of the log monthly Amihud ratio of each asset."""
    cols = {}
    for k in keys:
        x = pd.concat([returns(k, start).rename('r'), dollar_volume(k, start).rename('dv')], axis=1, join='inner').dropna()
        x = x[x['dv'] > 0]
        m = (1e4 * x['r'].abs() / (x['dv'] / 1e6)).resample('ME').agg(['mean', 'count'])
        cols[k] = np.log(m['mean'].where(m['count'] >= 10))
    return pd.DataFrame(cols).mean(axis=1).rename('lilliq')


def c1_premium():
    out, series = {}, {}
    for name, spec in C_MARKETS.items():
        sym, col = spec['ret']
        p = read_market(sym)[col].loc['2016-08-01':'2026-08-31']
        r = 100 * np.log(p.resample('ME').last()).diff().rename('r')
        li = market_illiq(spec['keys']).dropna()
        # illiquidity shock: the residual of an AR(1) on log illiquidity
        ar = sm.OLS(li.iloc[1:].values, sm.add_constant(li.shift(1).iloc[1:].values)).fit()
        shock = pd.Series(ar.resid, index=li.index[1:], name='shock')
        d = pd.concat([r, li.shift(1).rename('lag'), shock], axis=1, join='inner').dropna().loc['2016-11':'2026-08']
        fit = sm.OLS(d['r'], sm.add_constant(d[['lag', 'shock']])).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
        # Amihud and Hurvich (2004): regression augmented with the AR(1) residual computed with the bias-corrected phi,
        # phi_c = phi + (1 + 3 phi) / T + 3 (1 + 3 phi) / T^2; the standard error includes the uncertainty of phi_c
        T_ar = len(li) - 1
        phi = ar.params[1]
        phi_c = min(phi + (1 + 3 * phi) / T_ar + 3 * (1 + 3 * phi) / T_ar ** 2, 0.9999)   # capped at 0.9999
        psi_c = np.mean(li.values[1:] - phi_c * li.values[:-1])
        vc = pd.Series(li.values[1:] - psi_c - phi_c * li.values[:-1], index=li.index[1:], name='vc')
        dc = pd.concat([r, li.shift(1).rename('lag'), vc], axis=1, join='inner').dropna().loc['2016-11':'2026-08']
        fc = sm.OLS(dc['r'], sm.add_constant(dc[['lag', 'vc']])).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
        var_phic = (1 + 3 / T_ar + 9 / T_ar ** 2) ** 2 * ar.bse[1] ** 2
        se_c = float(np.sqrt(fc.params['vc'] ** 2 * var_phic + fc.bse['lag'] ** 2))
        ah = dict(phi_c=float(phi_c), b_lag_c=float(fc.params['lag']), se_lag_c=se_c, t_lag_c=float(fc.params['lag'] / se_c),
                  bias=float(fit.params['lag'] - fc.params['lag']))
        out[name] = dict(n=int(len(d)), b_lag=float(fit.params['lag']), se_lag=float(fit.bse['lag']),
                         t_lag=float(fit.tvalues['lag']), b_shock=float(fit.params['shock']),
                         se_shock=float(fit.bse['shock']), t_shock=float(fit.tvalues['shock']), r2=float(fit.rsquared),
                         phi=float(ar.params[1]), start=d.index[0].strftime('%Y-%m'), end=d.index[-1].strftime('%Y-%m'), **ah)
        series[name] = d
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    for ax, (name, d) in zip(axes, series.items()):
        c = GROUP_COL[name]
        ax.scatter(d['shock'], d['r'], s=12, color=c, label=f'{name}: monthly observations')
        xs = np.linspace(d['shock'].min(), d['shock'].max(), 20)
        f = sm.OLS(d['r'], sm.add_constant(d['shock'])).fit()
        ax.plot(xs, f.params.iloc[0] + f.params.iloc[1] * xs, color='black', lw=1.0)
        ax.axhline(0, color=Gray, lw=0.5)
        ax.set_xlabel('Illiquidity shock (AR(1) residual of log illiquidity)')
        ax.set_title(name, fontsize=9, loc='left', color=c)
    axes[0].set_ylabel('Market return in the same month (%)')
    h = [a.get_legend_handles_labels()[0][0] for a in axes]
    fig_legend_bottom(fig, h, [a.get_legend_handles_labels()[1][0] for a in axes] , ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_premium')
    # BVB cross-section: least liquid minus most liquid portfolio (annual rebalancing)
    keys = C_MARKETS['BVB']['keys']
    px = pd.concat({k: read_market(ASSETS[k][0])['adjusted_close'] for k in keys}, axis=1).loc['2017-01-01':'2026-08-31']
    mret = px.resample('ME').last().pct_change(fill_method=None)       # simple total returns (exact portfolio)
    spreads = []
    for y in range(2018, 2027):
        il = {}
        for k in keys:
            rr = returns(k, f'{y - 1}-01-01', f'{y - 1}-12-31')
            dv = dollar_volume(k, f'{y - 1}-01-01', f'{y - 1}-12-31')
            if len(rr) > 150:
                il[k] = float((rr.abs() / dv).dropna().mean())
        if len(il) < 6:
            continue
        srt = sorted(il, key=il.get)
        liq, ill = srt[:len(srt) // 2], srt[-(len(srt) // 2):]
        yr = mret.loc[str(y)]
        spreads.append((yr[ill].mean(axis=1) - yr[liq].mean(axis=1)).dropna())
    ls = 100 * pd.concat(spreads)
    tt = sm.OLS(ls, np.ones(len(ls))).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
    out['bvb_ls'] = dict(mean=float(ls.mean()), se=float(tt.bse.iloc[0]), t=float(tt.tvalues.iloc[0]), n=int(len(ls)),
                         ann=float(12 * ls.mean()), start=ls.index[0].strftime('%Y-%m'), end=ls.index[-1].strftime('%Y-%m'))
    fig_c1(out, ls)
    return out


def fig_c1(out, ls):
    """Coefficient of lagged illiquidity (HAC and reduced-bias) and the monthly illiquid-minus-liquid series (BVB)."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.3), gridspec_kw=dict(width_ratios=[1, 1.4]))
    ax = axes[0]
    for i, name in enumerate(('BVB', 'US', 'Crypto')):
        o = out[name]
        c = GROUP_COL[name]
        ax.hlines(i - 0.13, o['b_lag'] - 1.96 * o['se_lag'], o['b_lag'] + 1.96 * o['se_lag'], color=c, lw=2,
                  label='OLS with HAC SE' if i == 0 else None)
        ax.plot(o['b_lag'], i - 0.13, 'o', color=c, ms=6)
        ax.hlines(i + 0.13, o['b_lag_c'] - 1.96 * o['se_lag_c'], o['b_lag_c'] + 1.96 * o['se_lag_c'], color=c, lw=2,
                  ls=':', label='Reduced-bias (Amihud-Hurvich)' if i == 0 else None)
        ax.plot(o['b_lag_c'], i + 0.13, 's', color=c, ms=5)
    ax.axvline(0, color=Gray, ls='--', lw=0.8)
    ax.set_yticks(range(3))
    ax.set_yticklabels(['BVB', 'US', 'Crypto'])
    ax.invert_yaxis()
    ax.set_xlabel('Coefficient of lagged illiquidity, 95% interval')
    ax.set_title('(1) Predictive effect: crypto only, and fragile', fontsize=9, loc='left')
    ax = axes[1]
    ax.bar(ls.index, ls.values, width=20, color=[IDAred if v > 0 else MainBlue for v in ls.values],
           label='BVB illiquid-minus-liquid return, monthly (%)')
    ax.axhline(ls.mean(), color='black', lw=1.0, ls='--', label=f'Mean {ls.mean():.2f}% per month')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_ylabel('Return difference (%)')
    ax.set_title('(2) Annual sorts of the ten blue chips', fontsize=9, loc='left')
    ax.tick_params(axis='x', labelsize=7.5)
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.13, 1, 1))
    save_fig('ch10_sem_c1')


# =============================================================================
# CHARTS FOR PART A (models on paper) AND FOR C2
# =============================================================================
def fig_a1_bounce(c=0.09, sig2=0.0358, n_path=40, n_long=20000, seed=SEED):
    """A1 simulated: efficient price, trade price and autocorrelation of changes, with the parameters of A1 sub-task 2."""
    rng = np.random.default_rng(seed)
    m = 20 + np.cumsum(rng.normal(0, np.sqrt(sig2), n_long))
    q = np.where(rng.random(n_long) < 0.5, 1, -1)
    p = m + c * q
    dp = np.diff(p)
    dm = dp - dp.mean()
    acf = [float(np.mean(dm[k:] * dm[:-k]) / np.mean(dm ** 2)) for k in range(1, 9)]
    rho = -c ** 2 / (sig2 + 2 * c ** 2)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axes[0]
    k = np.arange(n_path)
    ax.plot(k, m[:n_path], color=MainBlue, lw=1.4, label='Efficient price $m_t$')
    ax.plot(k, p[:n_path], color=IDAred, lw=0.9, marker='o', ms=3, label='Trade price $p_t = m_t + c\\,q_t$, c = 0.09 lei')
    ax.set_xlabel('Trade number')
    ax.set_ylabel('Price (lei)')
    ax.set_title('Simulated: trades alternate between bid and ask', fontsize=9, loc='left')
    ax = axes[1]
    lags = np.arange(1, 9)
    ax.bar(lags, acf, color=IDAred, width=0.6, label=f'Sample autocorrelation of $\\Delta p_t$ ({n_long:,} trades)')
    ax.axhline(rho, color=MainBlue, ls='--', lw=1.1, label=f'Theory at lag 1: $-c^2/(\\sigma^2 + 2c^2)$ = {rho:.3f}')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag')
    ax.set_ylabel('Autocorrelation')
    ax.set_title('Only lag 1 is negative', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.14, 1, 1))
    save_fig('ch10_sem_a1_bounce')
    return dict(acf1=acf[0], rho=rho)


def fig_a2_sampling(var=0.0520, cov=-0.0081, Ts=(78, 250), R=20000):
    """A2: sampling distribution of the autocovariance (simulated under the Roll model, binary signs, demeaned) and
    Bartlett's Normal approximation; positive tail hatched."""
    from scipy.stats import norm
    c = np.sqrt(-cov)
    sig = np.sqrt(var - 2 * c ** 2)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.2), sharey=False)
    out = {}
    for ax, T, col in zip(axes, Ts, (IDAred, MainBlue)):
        g = roll_mc(c, sig, T=T + 1, R=R, seed=SEED)        # T price changes
        se = np.sqrt((var ** 2 + 3 * cov ** 2) / T)
        ax.hist(g, bins=60, density=True, color=col, alpha=0.45, label='Simulated under Roll (binary signs, demeaned)')
        xs = np.linspace(cov - 4.5 * se, cov + 4.5 * se, 300)
        ax.plot(xs, norm.pdf(xs, cov, se), color='black', lw=1.1, label='Normal approximation $N(\\gamma_1, (\\gamma_0^2 + 3\\gamma_1^2)/T)$')
        xp = xs[xs > 0]
        ax.fill_between(xp, 0, norm.pdf(xp, cov, se), color=Amber, alpha=0.6, lw=0, label='Positive tail: $\\hat\\gamma_1 > 0$')
        ax.axvline(cov, color=Gray, ls='--', lw=0.8)
        ax.set_xlabel('Sample autocovariance $\\hat\\gamma_1$ (lei$^2$)')
        ax.set_title(f'T = {T} price changes: P(positive) {100 * norm.cdf(cov / se):.1f}% (Normal), {100 * (g > 0).mean():.1f}% (simulated)',
                     fontsize=8.5, loc='left')
        out[T] = dict(p_sim=float((g > 0).mean()), mean_sim=float(g.mean()), sd_sim=float(g.std()),
                      bias_formula=float(-(var + 2 * cov) / T))
    axes[0].set_ylabel('Density')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend_bottom(fig, h, l, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch10_sem_a2_sampling')
    return out


def fig_a3_spread(dv=20.0):
    """A3: the Glosten-Milgrom spread as a function of the prior probability theta, for three shares mu."""
    th = np.linspace(0.005, 0.995, 200)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for mu, c in [(0.1, Amber), (0.3, IDAred), (0.5, MainBlue)]:
        ax.plot(th, gm_spread_formula(th, mu, dv), color=c, lw=1.5, label=f'$\\mu$ = {mu}: maximum $\\mu\\Delta V$ = {mu * dv:.0f} at $\\theta$ = 1/2')
    for t_, lab in [(0.5, 'prior'), (0.65, 'after one buy'), (0.7, '$\\theta$ = 0.7')]:
        v = gm_spread_formula(t_, 0.3, dv)
        ax.plot(t_, v, 'o', color='black', ms=4)
        ax.annotate(f'{lab}: {v:.2f}', (t_, v), xytext=(6, 4) if t_ != 0.65 else (-75, -14), textcoords='offset points',
                    fontsize=7.5, color='black')
    ax.set_xlabel('Probability of the high value, $\\theta$')
    ax.set_ylabel('Spread $a - b$ ($V_L$ = 90, $V_H$ = 110)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    plt.tight_layout()
    save_fig('ch10_sem_a3_spread')


def fig_a4_learning(mus=(0.1, 0.3, 0.5), level=108.0, vl=90.0, vh=110.0, kmax=14):
    """A4: the bid after k consecutive buys (conditional scenario) and the simulated paths of the lecture."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.3))
    ax = axes[0]
    for mu, c in zip(mus, (Amber, IDAred, MainBlue)):
        theta, bids = 0.5, []
        for k in range(kmax + 1):
            ask, bid, tb, ts = gm_quotes(theta, mu, vl, vh)
            bids.append(bid)
            theta = tb
        bids = np.array(bids)
        k1 = int(np.argmax(bids > level))
        ax.plot(range(kmax + 1), bids, color=c, lw=1.4, marker='o', ms=3, label=f'$\\mu$ = {mu}: bid > 108 after k = {k1} buys')
    ax.axhline(level, color=Gray, ls='--', lw=0.8)
    ax.set_xlabel('Number of consecutive buys k')
    ax.set_ylabel('Bid quoted after k buys')
    ax.set_title('(1) Conditioned scenario: every trade is a buy', fontsize=9, loc='left')
    ax = axes[1]
    for mu, c in [(0.1, Amber), (0.3, IDAred)]:
        d = gm_simulate(mu, n=60, seed=3)
        ax.plot(d['t'], d['bid'], color=c, lw=1.2, ls='--', label=f'Lecture path, $\\mu$ = {mu}: bid')
    ax.axhline(level, color=Gray, ls='--', lw=0.8)
    ax.set_xlabel('Trade number')
    ax.set_ylabel('Bid')
    ax.set_title('(2) Simulated order flow with uninformed sells', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.12, 1, 1))
    save_fig('ch10_sem_a4_learning')


def fig_a6_kyle(sigma_v=2.0, sigma_u=10_000.0, p0=50.0, n=200_000, seed=SEED, n_show=3000):
    """A6: lambda as a regression slope (the A6 simulation) and the Amihud-type ratio with two denominators."""
    rng = np.random.default_rng(seed)
    k = kyle(sigma_v, sigma_u)
    v = p0 + sigma_v * rng.standard_normal(n)
    x = k['beta'] * (v - p0)
    u = sigma_u * rng.standard_normal(n)
    y = x + u
    r1 = a6_kyle_ols(sigma_v, sigma_u, p0, n, seed)
    r2 = a6_kyle_ols(sigma_v, 2 * sigma_u, p0, n, seed)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.3))
    ax = axes[0]
    ax.scatter(y[:n_show] / 1e3, v[:n_show] - p0, s=4, color=MainBlue, alpha=0.4, label='$v - p_0$ (first 3,000 auctions)')
    ys = np.linspace(y.min(), y.max(), 10)
    ax.plot(ys / 1e3, k['lam'] * ys, color=IDAred, lw=1.6, label=f'$p - p_0 = \\lambda y$, $\\lambda$ = {k["lam"]:.4f} USD per share')
    ax.set_xlim(-45, 45)
    ax.set_xlabel('Net order flow $y$ (thousand shares)')
    ax.set_ylabel('USD')
    ax.set_title('(1) Both regressions on $y$ have slope $\\lambda$', fontsize=9, loc='left')
    ax = axes[1]
    labs = ['Theory $\\lambda/p_0^2$', 'Net flow $|y|$', 'Gross proxy $|x| + |u|$']
    xs = np.arange(3)
    w = 0.36
    v1 = [r1['target'] * 1e10, r1['am_net'] * 1e10, r1['am_vol'] * 1e10]
    v2 = [r2['target'] * 1e10, r2['am_net'] * 1e10, r2['am_vol'] * 1e10]
    b1 = ax.bar(xs - w / 2, v1, w, color=MainBlue, label='$\\sigma_u$ = 10,000 shares')
    b2 = ax.bar(xs + w / 2, v2, w, color=Amber, label='$\\sigma_u$ = 20,000 shares (doubled noise)')
    for bars in (b1, b2):
        for bb in bars:
            ax.text(bb.get_x() + bb.get_width() / 2, bb.get_height() + 6, f'{bb.get_height():.0f}', ha='center', fontsize=7.5, color='black')
    ax.set_xticks(xs)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylabel('bp per USD 1 million')
    ax.set_title('(2) Amihud-type ratio: the denominator matters', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.14, 1, 1))
    save_fig('ch10_sem_a6_kyle')
    return dict(target2=r2['target'] * 1e10, amnet2=r2['am_net'] * 1e10, amvol2=r2['am_vol'] * 1e10, ratio2=r2['am_ratio'])


def fig_ac_seminar():
    """A7-A8: holdings x_k after each day (discrete, N = 5) and the continuous solution; the cost - risk frontier."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.3))
    ax = axes[0]
    tt = np.linspace(0, AC['T'], 200)
    pts = {}
    for lam, c, lab in [(0, MainBlue, 'Even selling, $\\lambda$ = 0'), (2e-6, Forest, 'A7: $\\lambda$ = 2e-6'),
                        (2e-5, Orange, 'A8: $\\lambda$ = 2e-5')]:
        t, x, E, V = ac_trajectory(lam=lam, **AC)
        pts[lam] = (E, np.sqrt(V))
        ax.plot(t, x / 1e3, color=c, lw=0, marker='o', ms=5, label=lab + ': holdings $x_k$ after day k')
        if lam > 0:
            kc = np.sqrt(lam * AC['sigma'] ** 2 / AC['eta'])
            ax.plot(tt, AC['X'] * np.sinh(kc * (AC['T'] - tt)) / np.sinh(kc * AC['T']) / 1e3, color=c, lw=1, ls='--')
        else:
            ax.plot(tt, AC['X'] * (1 - tt / AC['T']) / 1e3, color=c, lw=1, ls='--')
    ax.set_xlabel('Day k')
    ax.set_ylabel('Shares still held (thousands)')
    ax.set_title('(1) Discrete schedule (dots), continuous solution (dashed)', fontsize=9, loc='left')
    ax = axes[1]
    fr = ac_frontier(lams=np.logspace(-8, -3.5, 60), **AC)
    ax.plot(fr['sd'] / 1e6, fr['E'] / 1e6, color=Purple, lw=1.5, label='Efficient frontier (N = 5 days)')
    for lam, c in [(0, MainBlue), (2e-6, Forest), (2e-5, Orange)]:
        E, sd = pts[lam]
        ax.plot(sd / 1e6, E / 1e6, 'o', color=c, ms=7)
        ax.annotate(f'({sd / 1e6:.2f}, {E / 1e6:.2f})', (sd / 1e6, E / 1e6), xytext=(6, 3), textcoords='offset points',
                    fontsize=7.5, color='black')
    ax.set_xlabel('Standard deviation of cost (USD million)')
    ax.set_ylabel('Expected cost (USD million)')
    ax.set_title('(2) Cost versus risk', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.14, 1, 1))
    save_fig('ch10_sem_ac')


PIN_DAYS = [('A9: B = 1450, S = 1000', 1450, 1000), ('A10(a): B = 1000, S = 1420', 1000, 1420),
            ('A10(b): B = S = 1000', 1000, 1000), ('A10(c): B = 1195, S = 1000', 1195, 1000)]


def fig_pin(**par):
    """A9-A10: the three states of the EKOP model (Poisson centres) and the posterior probabilities for four days."""
    par = par or PIN_PAR
    a, d_, mu, eb, es = (par[k] for k in ('alpha', 'delta', 'mu', 'eb', 'es'))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4), gridspec_kw=dict(width_ratios=[1, 1.5]))
    ax = axes[0]
    th = np.linspace(0, 2 * np.pi, 100)
    for (bx, sx), lab, c in [((eb, es), f'No news, prob. {1 - a:.2f}', MainBlue),
                             ((eb, es + mu), f'Bad news, prob. {a * d_:.2f}', IDAred),
                             ((eb + mu, es), f'Good news, prob. {a * (1 - d_):.2f}', Forest)]:
        ax.plot(bx + 2 * np.sqrt(bx) * np.cos(th), sx + 2 * np.sqrt(sx) * np.sin(th), color=c, lw=1.3, label=lab)
        ax.plot(bx, sx, '+', color=c, ms=8)
    for lab, B_, S_ in PIN_DAYS:
        ax.plot(B_, S_, 'o', color='black', ms=4)
        ax.annotate(lab.split(':')[0], (B_, S_), xytext=(4, 4), textcoords='offset points', fontsize=7, color='black')
    ax.set_xlabel('Buys B per day')
    ax.set_ylabel('Sells S per day')
    ax.set_title('(1) States: Poisson centres, 2 SD circles', fontsize=9, loc='left')
    ax = axes[1]
    post = {}
    xs = np.arange(len(PIN_DAYS))
    w = 0.26
    for j, (lab_, c) in enumerate([('No news', MainBlue), ('Bad news', IDAred), ('Good news', Forest)]):
        vals = []
        for lab, B_, S_ in PIN_DAYS:
            pp = pin_posterior(B_, S_, a, d_, mu, eb, es)
            post[lab] = [float(v) for v in pp]
            vals.append(pp[j])
        ax.bar(xs + (j - 1) * w, vals, w, color=c, label=f'Posterior: {lab_.lower()}')
    ax.set_xticks(xs)
    ax.set_xticklabels([l.split(': ')[1] for l, _, _ in PIN_DAYS], fontsize=7.5)
    ax.set_ylabel('Posterior probability')
    ax.set_title('(2) Posterior probability of each state', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.13, 1, 1))
    save_fig('ch10_sem_pin')
    return post


def fig_c2_roundtrip(mid=20.0, s=0.05):
    """C2: bid, mid-price and ask; half a spread each way, one spread for a round trip."""
    a, b = mid + s / 2, mid - s / 2
    fig, ax = plt.subplots(figsize=(7.5, 3.0))
    for y, lab, c in [(a, f'Ask a = {a:.3f} lei: you buy here', IDAred), (mid, f'Mid m = {mid:.3f} lei', Gray),
                      (b, f'Bid b = {b:.3f} lei: you sell here', MainBlue)]:
        ax.hlines(y, 0, 1, color=c, lw=2 if c != Gray else 1, ls='-' if c != Gray else '--')
        ax.text(1.03, y, lab, va='center', fontsize=8.5, color='black')
    ax.annotate('', xy=(0.25, a), xytext=(0.25, mid), arrowprops=dict(arrowstyle='<->', color=IDAred, lw=1.2))
    ax.text(0.27, (a + mid) / 2, f'buy leg: c = s/2 = {s / 2:.3f} lei ({100 * s / 2 / mid:.3f}%)', va='center', fontsize=8, color='black')
    ax.annotate('', xy=(0.25, b), xytext=(0.25, mid), arrowprops=dict(arrowstyle='<->', color=MainBlue, lw=1.2))
    ax.text(0.27, (b + mid) / 2, f'sell leg: c = {s / 2:.3f} lei ({100 * s / 2 / mid:.3f}%)', va='center', fontsize=8, color='black')
    ax.annotate('', xy=(0.8, a), xytext=(0.8, b), arrowprops=dict(arrowstyle='<->', color=Purple, lw=1.6))
    ax.text(0.83, mid + 0.012, f'round trip:\na - b = s = {s:.2f} lei\n= {100 * s / mid:.2f}% of the price', fontsize=8,
            color='black', va='center')
    ax.set_xlim(0, 1.6)
    ax.set_ylim(b - 0.008, a + 0.012)
    ax.set_xticks([])
    ax.set_ylabel('Price (lei)')
    ax.spines['bottom'].set_visible(False)
    plt.tight_layout()
    save_fig('ch10_sem_c2_roundtrip')


# =============================================================================
# C3: the price of the speed race for SPY (Aquilina, Budish and O'Neill, 2022), full tables
# =============================================================================
def c3_race(B=B, L=20, seed=SEED):
    """Daily V_t, sigma_t; yearly means and correlation with bootstrap intervals (independent days and moving blocks
    of L days); the annual prize; the daily tax at mean traded value and the effective ratio Pi_t / V_t."""
    d = race_daily(intraday_spy())
    P = race_prize(d)
    d['ratio6'] = ABO['col6_v'] + ABO['col6_s'] * d['sigma'] * d.groupby('year')['V'].transform('mean') / d['V']
    years = {}
    for y, g in d.groupby('year'):
        v, sg = g['V'].values, g['sigma'].values
        n = len(g)
        rng = np.random.default_rng(seed)
        iid = [np.corrcoef(v[i], sg[i])[0, 1] for i in (rng.integers(0, n, n) for _ in range(B))]
        rng = np.random.default_rng(seed)
        blk = []
        for _ in range(B):
            st = rng.integers(0, n - L + 1, n // L + 1)
            i = np.concatenate([np.arange(a_, a_ + L) for a_ in st])[:n]
            blk.append(np.corrcoef(v[i], sg[i])[0, 1])
        years[int(y)] = dict(V_mean=float(v.mean() / 1e9), sigma_mean=float(sg.mean()), corr=float(np.corrcoef(v, sg)[0, 1]),
                             ci_iid=[float(x) for x in np.percentile(iid, [2.5, 97.5])],
                             ci_blk=[float(x) for x in np.percentile(blk, [2.5, 97.5])], n=int(n), **{k: P[y][k] for k in ('col2', 'col6', 'lo', 'hi')})
    top = d['tax6'].sort_values(ascending=False)
    rtop = d['ratio6'].sort_values(ascending=False)
    a7 = pd.Timestamp('2025-04-07')
    fig, ax = plt.subplots(figsize=(10, 3.3))
    ax.plot(d.index, d['tax6'], color=MainBlue, lw=0.8, label='Tax at mean traded value: 0.3354 + 0.0066 $\\sigma_t$ (bp)')
    ax.plot(d.index, d['ratio6'], color=IDAred, lw=0.8, label='Realised ratio $\\Pi_t / V_t$ = 0.3354 + 0.0066 $\\sigma_t \\bar V / V_t$ (bp)')
    ax.axhline(ABO['hi'], color=Forest, lw=0.9, ls=':', label='Highest Table XIV scenario, 0.74 bp')
    ax.annotate(f"7 April 2025: {d.loc[a7, 'tax6']:.2f} bp at mean value,\n{d.loc[a7, 'ratio6']:.2f} bp realised (traded value USD {d.loc[a7, 'V'] / 1e9:.0f} billion)",
                xy=(a7, d.loc[a7, 'tax6']), xytext=(pd.Timestamp('2022-09-01'), 0.95), fontsize=7.5, color='black',
                arrowprops=dict(arrowstyle='->', color='black', lw=0.7))
    ax.set_ylabel('Implied tax (bp of traded value)')
    ax.set_ylim(0.1, 1.15)
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    plt.tight_layout()
    save_fig('ch10_sem_c3_tax')
    return dict(years=years, top5=[(str(t.date()), float(top[t])) for t in top.index[:5]],
                ratio_max=(str(rtop.index[0].date()), float(rtop.iloc[0])), ratio_a7=float(d.loc[a7, 'ratio6']),
                V_a7=float(d.loc[a7, 'V'] / 1e9), tax_a7=float(d.loc[a7, 'tax6']), sigma_a7=float(d.loc[a7, 'sigma']),
                n_above_hi_ratio=int((d['ratio6'] > ABO['hi']).sum()), tax_median=float(d['tax6'].median()),
                thr=float((ABO['col2'] - ABO['col6_v']) / ABO['col6_s']))


if __name__ == '__main__':
    R = {}
    R['A1'] = a1_roll()
    R['A2'] = a2_roll_se()
    R['A3'] = a3_gm()
    R['A4'] = a4_gm_learning()
    R['A5'] = a5_kyle()
    R['A6'] = a6_kyle_ols()
    R['A7'] = a7_ac()
    R['A8'] = a8_ac()
    R['A9'] = a9_pin()
    R['A10'] = a10_pin()
    R['B1'] = b1_ushape()
    R['B2'] = b2_spreads()
    R['B3'] = b3_cross()
    R['B4'] = b4_illiq_vix()
    R['B5'] = b5_amihud_groups()
    R['B6'] = b6_sqrt()
    R['B7'] = b7_btc()
    R['B8'] = b8_price_discovery()
    R['C1'] = c1_premium()
    R['A1']['fig'] = fig_a1_bounce()
    R['A2']['sim'] = fig_a2_sampling()
    fig_a3_spread()
    fig_a4_learning()
    R['A6']['noise2'] = fig_a6_kyle()
    fig_ac_seminar()
    R['PIN_days'] = fig_pin()
    R['B2']['mc'] = b2_mc(intraday_spreads(intraday_spy()))
    fig_c2_roundtrip()
    R['C3'] = c3_race()
    with open(os.path.join(HERE, 'sem10_results.json'), 'w') as f:
        json.dump(jsonable(R), f, indent=1)
    print('saved sem10_results.json')
    for k, v in R.items():
        if k not in ('B3', 'C3', 'PIN_days'):
            print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()} if isinstance(v, dict) else v)

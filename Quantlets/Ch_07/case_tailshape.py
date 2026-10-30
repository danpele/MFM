"""
case_tailshape.py -- Chapter 7, second case study: time-varying extreme tail shape
==================================================================================
D'Innocenzo, Lucas, Schwaab & Zhang (2024), Modeling extreme events: time-varying extreme tail shape,
Journal of Business & Economic Statistics 42(3), 903-917, https://doi.org/10.1080/07350015.2023.2260439.

Model (Sections 2.1-2.5 of the paper), for the daily S&P 500 loss y_t = -100 x log return:
  * dynamic threshold (eq. 9): tau_{t+1} = (1 - b_tau) q_kappa + a_tau (1{y_t > tau_t} - (1 - kappa)) + b_tau tau_t,
    kappa = 0.90, tau_1 = q_kappa; (a_tau, b_tau) minimise the quantile check loss (eq. 17);
  * exceedance x_t = y_t - tau_t > 0 ~ GPD(xi_t, delta_t); f_t = (ln xi_t, ln delta_t)';
    f_{t+1} = omega + A s_t + B f_t (eq. 3, lambda = 0 as for the S&P 500 in the paper), A and B diagonal,
    s_t = L_t' grad_t the score scaled by the square-root inverse Fisher information (eqs. 4-6), s_t = 0 if x_t <= 0;
    f_1 = (I - B)^{-1} omega; parameters by maximum likelihood (eq. 15), given the thresholds;
  * VaR and ES (Section 2.5): VaR_t = tau_t + delta_t/xi_t [((1 - gamma)/(t*/t))^{-xi_t} - 1],
    ES_t = VaR_t/(1 - xi_t) + (delta_t - xi_t tau_t)/(1 - xi_t); t*/t: share of exceedances up to t - 1.
Course convention: VaR 1% = gamma 0.99, ES 2.5% = gamma 0.975 (loss quantiles, positive numbers).

Course replication: course data (S&P 500, Jan 2000 - Sep 2026) instead of CRSP 1962-2020;
  (i) full sample, filtered as in the paper's Figure 5; (ii) parameters estimated on 2000-2015 and kept fixed,
  one-day-ahead forecasts for 2016-2026, compared with FHS VaR 1% of the chapter (ch7_rolling_sp500.csv) and
  with a static GPD fitted on the 10% largest losses of 2000-2015.
Output: ch7_tailshape.json, charts/ch7_tailshape.pdf/.png, ch7_tailshape_series.csv (for the interactive page).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import optimize, stats

try:
    from numba import njit
except ImportError:                 # plain Python if numba is missing (slower)
    def njit(*a, **k):
        return (lambda f: f) if not a or not callable(a[0]) else a[0]

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import log_returns   # noqa: E402

CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
KAPPA = 0.90                    # threshold = dynamic 90% quantile of the loss (paper: 1 - kappa = 10%)
G_VAR, G_ES = 0.99, 0.975       # VaR 1%, ES 2.5%
EST_END, OOS_START = '2015-12-31', '2016-01-01'

# chapter colours (generate_all_charts.py)
MainBlue, IDAred, Forest, Orange, Teal, Navy, BandBlue = ('#1A3A6E', '#CD0000', '#2E7D32', '#E67E22', '#17A2B8', '#1F2A44',
                                                    '#C5D2E8')

plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'], 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.6, 'legend.frameon': False})


# ----------------------------------------------------------------------------------------------------------------
# 1. dynamic threshold, eq. (9), estimated by the check loss, eq. (17)
@njit(cache=False)
def _tau_path(y, a, b, q, kappa):
    tau = np.empty(len(y))
    tau[0] = q
    for t in range(len(y) - 1):
        hit = 1.0 if y[t] > tau[t] else 0.0
        tau[t + 1] = (1 - b) * q + a * (hit - (1 - kappa)) + b * tau[t]
    return tau


def tau_path(y, a, b, q):
    return _tau_path(np.asarray(y, float), float(a), float(b), float(q), KAPPA)


def check_loss(y, tau):
    u = y - tau
    return float(np.mean(u * (KAPPA - (u < 0))))


def fit_tau(y):
    q = float(np.quantile(y, KAPPA))
    best = None
    for a0 in (0.05, 0.1, 0.2, 0.3, 0.5):
        for b0 in (0.9, 0.95, 0.98, 0.99, 0.995):
            obj = lambda p: (check_loss(y, tau_path(y, p[0], p[1], q))   # noqa: E731
                             if p[0] > 0 and 0 < p[1] < 1 else 1e9)
            r = optimize.minimize(obj, [a0, b0], method='Nelder-Mead',
                                  options={'xatol': 1e-6, 'fatol': 1e-10, 'maxiter': 4000})
            if best is None or r.fun < best.fun:
                best = r
    return dict(a=float(best.x[0]), b=float(best.x[1]), q=q, loss=float(best.fun))


# ----------------------------------------------------------------------------------------------------------------
# 2. score-driven GPD, eqs. (3)-(6), likelihood (15)
F_XI_LO, F_XI_HI = -6.0, 1.5     # numerical bounds of ln xi_t: xi_t in [e^-6, e^1.5] = [0.00248, 4.48]
F_DE_LO, F_DE_HI = -6.0, 4.0     # numerical bounds of ln delta_t


@njit(cache=False)
def _gpd_filter(x, fx, fd, ax, ad, bx, bd, lo1, hi1, lo2, hi2):
    n = len(x)
    xi, de = np.empty(n), np.empty(n)
    ox, od = (1 - bx) * fx, (1 - bd) * fd
    f1, f2 = fx, fd
    ll = 0.0
    for t in range(n):
        f1 = min(max(f1, lo1), hi1)
        f2 = min(max(f2, lo2), hi2)
        k, d = np.exp(f1), np.exp(f2)
        xi[t], de[t] = k, d
        s1, s2 = 0.0, 0.0
        if x[t] > 0:
            z = 1 + k * x[t] / d
            ll += -np.log(d) - (1 + 1 / k) * np.log(z)
            g1 = np.log(z) / k - (1 + 1 / k) * k * x[t] / (d + k * x[t])
            g2 = (x[t] - d) / (d + k * x[t])
            s1 = (1 + 1 / k) * g1 - g2            # L_t' grad_t, eq. (6)
            s2 = np.sqrt(1 + 2 * k) * g2
        f1 = ox + ax * s1 + bx * f1
        f2 = od + ad * s2 + bd * f2
    return xi, de, ll


def gpd_filter(x, theta, xi_bounds=(F_XI_LO, F_XI_HI)):
    """x: exceedances (<= 0 where there is none); theta = (fbar_xi, fbar_delta, a_xi, a_delta, b_xi, b_delta),
    omega = (I - B) fbar, f_1 = fbar. Returns xi_t, delta_t (known at t - 1) and the log-likelihood (eq. 15).
    ln xi_t is truncated to xi_bounds and ln delta_t to [F_DE_LO, F_DE_HI]."""
    return _gpd_filter(np.asarray(x, float), *[float(v) for v in theta], float(xi_bounds[0]), float(xi_bounds[1]),
                       F_DE_LO, F_DE_HI)


@njit(cache=False)
def _exp_filter(x, fd, ad, bd, lo2, hi2):
    """Exponential limit (xi = 0): exceedances ~ Exp(delta_t); score of ln delta_t, x/delta_t - 1 (unit information)."""
    n = len(x)
    de = np.empty(n)
    od = (1 - bd) * fd
    f2 = fd
    ll = 0.0
    for t in range(n):
        f2 = min(max(f2, lo2), hi2)
        d = np.exp(f2)
        de[t] = d
        s2 = 0.0
        if x[t] > 0:
            ll += -np.log(d) - x[t] / d
            s2 = x[t] / d - 1
        f2 = od + ad * s2 + bd * f2
    return de, ll


def fit_exponential_limit(x, n_starts=50, seed=11):
    """xi = 0 limit with score-driven delta_t; parameters (fbar_delta, a_delta, b_delta) by maximum likelihood."""
    ex = x[x > 0]
    neg = lambda p: (1e10 if (p[1] < 0 or not (0 < p[2] < 0.99999))   # noqa: E731
                     else -_exp_filter(np.asarray(x, float), p[0], p[1], p[2], F_DE_LO, F_DE_HI)[1])
    rng = np.random.default_rng(seed)
    starts = [[np.log(ex.mean()), 0.1, 0.99]]
    starts += [[rng.uniform(-1.5, 0.5), rng.uniform(0, 0.3), 1 - 10 ** rng.uniform(-4, -1)] for _ in range(n_starts)]
    best = None
    for p0 in starts:
        r = optimize.minimize(neg, p0, method='Nelder-Mead',
                              options={'xatol': 1e-8, 'fatol': 1e-9, 'maxiter': 20000, 'maxfev': 20000})
        if best is None or r.fun < best.fun:
            best = r
    return [float(v) for v in best.x], float(-best.fun), bool(best.success)


def fit_gpd_dynamic(x, n_starts=200, seed=42, xi_bounds=(F_XI_LO, F_XI_HI), info=None):
    """Maximum likelihood (eq. 15): Nelder-Mead from the static GPD fit and from n_starts random starting points.
    If info is a dict, it receives the convergence flag and message of the selected optimum and the number of
    starts whose optimum converged."""
    ex = x[x > 0]
    c, _, sc = stats.genpareto.fit(ex, floc=0)
    neg = lambda p: (1e10 if (p[2] < 0 or p[3] < 0 or not (0 < p[4] < 0.99999) or not (0 < p[5] < 0.99999))   # noqa: E731
                     else -gpd_filter(x, p, xi_bounds)[2])
    rng = np.random.default_rng(seed)
    starts = [[np.log(max(c, 0.05)), np.log(sc), 0.02, 0.1, 0.999, 0.99]]
    starts += [[rng.uniform(-4, -0.7), rng.uniform(-1.5, 0.5), rng.uniform(0, 0.3), rng.uniform(0, 0.3),
                1 - 10 ** rng.uniform(-4, -1), 1 - 10 ** rng.uniform(-4, -1)] for _ in range(n_starts)]
    best = None
    n_conv = 0
    for p0 in starts:
        r = optimize.minimize(neg, p0, method='Nelder-Mead',
                              options={'xatol': 1e-8, 'fatol': 1e-9, 'maxiter': 20000, 'maxfev': 20000})
        n_conv += bool(r.success)
        if best is None or r.fun < best.fun:
            best = r
    if info is not None:
        info.update(success=bool(best.success), message=str(best.message), n_starts=len(starts), n_converged=n_conv)
    return [float(v) for v in best.x], float(-best.fun), dict(xi=float(c), delta=float(sc),
                                                              loglik=float(stats.genpareto.logpdf(ex, c, 0, sc).sum()))


def fit_constant_shape(x, n_starts=100, seed=7):
    """Restricted model: xi constant (a_xi = 0), delta_t score-driven; parameters (fbar_xi, fbar_delta, a_delta, b_delta)."""
    ex = x[x > 0]
    c, _, sc = stats.genpareto.fit(ex, floc=0)
    neg = lambda p: (1e10 if (p[2] < 0 or not (0 < p[3] < 0.99999))   # noqa: E731
                     else -gpd_filter(x, [p[0], p[1], 0.0, p[2], 0.5, p[3]])[2])
    rng = np.random.default_rng(seed)
    starts = [[np.log(max(c, 0.05)), np.log(sc), 0.1, 0.99]]
    starts += [[rng.uniform(-4, -0.7), rng.uniform(-1.5, 0.5), rng.uniform(0, 0.3), 1 - 10 ** rng.uniform(-4, -1)]
               for _ in range(n_starts)]
    best = None
    for p0 in starts:
        r = optimize.minimize(neg, p0, method='Nelder-Mead',
                              options={'xatol': 1e-8, 'fatol': 1e-9, 'maxiter': 20000, 'maxfev': 20000})
        if best is None or r.fun < best.fun:
            best = r
    return [float(v) for v in best.x], float(-best.fun)


def risk(tau, xi, de, share, gamma):
    """VaR and ES at confidence gamma of the loss (Section 2.5 of the paper), element by element.
    xi_t = 0 (|xi_t| < 1e-8): exponential limit VaR = tau + delta log(share/(1 - gamma)), ES = VaR + delta;
    xi_t >= 1: the tail mean is infinite and ES is +inf. The level must lie in the modelled tail, 1 - gamma <= share."""
    tau, xi, de, share = np.broadcast_arrays(*[np.asarray(v, float) for v in (tau, xi, de, share)])
    if np.any(1 - gamma > share + 1e-12):
        raise ValueError('level outside the modelled tail: 1 - gamma > share of exceedances')
    small = np.abs(xi) < 1e-8
    xs = np.where(small, 1.0, xi)
    var = np.where(small, tau + de * np.log(share / (1 - gamma)),
                   tau + de / xs * (((1 - gamma) / share) ** (-xs) - 1))
    with np.errstate(divide='ignore', invalid='ignore'):
        es = np.where(small, var + de, var / (1 - xs) + (de - xs * tau) / (1 - xs))
    es = np.where(xi >= 1, np.inf, es)
    return var, es


def run(y, tp, theta):
    tau = tau_path(y, tp['a'], tp['b'], tp['q'])
    x = y - tau
    xi, de, ll = gpd_filter(x, theta)
    cnt = np.concatenate([[0.0], np.cumsum(x > 0)[:-1]])          # exceedances up to t - 1
    tt = np.arange(len(y), dtype=float)
    share = np.where(cnt > 0, cnt / np.maximum(tt, 1), 1 - KAPPA)  # t*/t
    v1, e1 = risk(tau, xi, de, share, G_VAR)
    v25, e25 = risk(tau, xi, de, share, G_ES)
    return dict(tau=tau, x=x, xi=xi, delta=de, var1=v1, es1=e1, var25=v25, es25=e25, ll=ll, share=share)


EVENTS = {'2001-09-17': '9/11 reopening', '2008-09-29': 'TARP vote', '2010-05-06': 'Flash crash',
          '2011-08-08': 'US downgrade', '2016-06-24': 'Brexit vote', '2018-02-05': 'Volmageddon',
          '2020-03-16': 'COVID-19', '2024-08-05': 'Yen carry unwind'}
NAMES = ['fbar_xi', 'fbar_delta', 'a_xi', 'a_delta', 'b_xi', 'b_delta']


def est2015_block(y, dates):
    """The same model on 2000-2015 only: estimate, convergence, how often ln xi_t sits on its numerical bounds,
    sensitivity to the lower bound, and the exponential limit (xi = 0) with score-driven delta_t."""
    n_est = int((dates <= EST_END).sum())
    ye = y[:n_est]
    tpe = fit_tau(ye)
    xe = ye - tau_path(ye, tpe['a'], tpe['b'], tpe['q'])
    info = {}
    the, lle, ste = fit_gpd_dynamic(xe, info=info)
    xie, dee, _ = gpd_filter(xe, the)
    lo, hi = np.exp(F_XI_LO), np.exp(F_XI_HI)
    cnt = np.concatenate([[0.0], np.cumsum(xe > 0)[:-1]])
    share = np.where(cnt > 0, cnt / np.maximum(np.arange(n_est, dtype=float), 1), 1 - KAPPA)
    _, es1 = risk(ye - xe, xie, dee, share, G_VAR)
    # sensitivity: lower bound of ln xi_t moved from -6 to -12
    info12 = {}
    th12, ll12, _ = fit_gpd_dynamic(xe, xi_bounds=(-12.0, F_XI_HI), info=info12)
    xi12, _, _ = gpd_filter(xe, th12, (-12.0, F_XI_HI))
    # exponential limit (xi = 0), score-driven delta_t
    thx, llx, okx = fit_exponential_limit(xe)
    return dict(n=n_est, n_exc=int((xe > 0).sum()), tau=tpe, theta=dict(zip(NAMES, the)), loglik=lle, static=ste,
                converged=info['success'], message=info['message'], n_starts=info['n_starts'],
                n_starts_converged=info['n_converged'],
                xi_median=float(np.median(xie)), xi_share_below_001=float(np.mean(xie < 0.01)),
                xi_max=float(xie.max()), xi_lower_bound=float(lo), xi_upper_bound=float(hi),
                n_at_lower=int(np.sum(np.isclose(xie, lo, rtol=1e-9, atol=0))),
                n_at_upper=int(np.sum(np.isclose(xie, hi, rtol=1e-9, atol=0))),
                n_es1_infinite=int(np.sum(~np.isfinite(es1))),
                lower12=dict(loglik=ll12, theta=dict(zip(NAMES, th12)), converged=info12['success'],
                             n_at_lower=int(np.sum(np.isclose(xi12, np.exp(-12.0), rtol=1e-9, atol=0))),
                             n_at_upper=int(np.sum(np.isclose(xi12, hi, rtol=1e-9, atol=0))),
                             xi_median=float(np.median(xi12))),
                exp_limit=dict(loglik=llx, theta=dict(zip(['fbar_delta', 'a_delta', 'b_delta'], thx)), converged=okx,
                               aic=2 * 3 - 2 * llx),
                aic_dyn=2 * 6 - 2 * lle, aic_static=2 * 2 - 2 * ste['loglik'])


def update_est2015():
    """Recompute only the 2000-2015 block of ch7_tailshape.json (the full-sample results and the chart are kept)."""
    r = log_returns('sp500')
    y_s = (-100 * r).astype(float)
    path = os.path.join(HERE, 'ch7_tailshape.json')
    with open(path) as f:
        res = json.load(f)
    res['est2015'] = est2015_block(y_s.values, y_s.index)
    with open(path, 'w') as f:
        json.dump(res, f, indent=1)
    return res['est2015']


def main():
    r = log_returns('sp500')
    y_s = (-100 * r).astype(float)
    dates = y_s.index
    y = y_s.values

    # full sample, as in the paper's Section 4.1: smoothed in-sample paths; parameters and the starting quantile use
    # the whole sample, and the recursion for xi_t, delta_t, tau_t is causal given those parameters
    tp = fit_tau(y)
    th, ll, st = fit_gpd_dynamic(y - tau_path(y, tp['a'], tp['b'], tp['q']))
    F = run(y, tp, th)
    xi_s, de_s = pd.Series(F['xi'], dates), pd.Series(F['delta'], dates)
    n_exc = int((F['x'] > 0).sum())
    k = 6
    aic_dyn, aic_st = 2 * k - 2 * ll, 2 * 2 - 2 * st['loglik']
    thc, llc = fit_constant_shape(y - tau_path(y, tp['a'], tp['b'], tp['q']))
    aic_const = 2 * 4 - 2 * llc

    # one-day changes of xi and delta after the event days (the filter reacts on t + 1)
    ev = {}
    for d0, lab in EVENTS.items():
        i = dates.get_loc(pd.Timestamp(d0))
        ev[d0] = dict(label=lab, loss=float(y[i]), exceed=bool(F['x'][i] > 0),
                      dxi=float(100 * (F['xi'][i + 1] / F['xi'][i] - 1)),
                      ddelta=float(100 * (F['delta'][i + 1] / F['delta'][i] - 1)))

    def chg(s, a, b):
        return float(100 * (s.loc[b:].iloc[0] / s.loc[:a].iloc[-1] - 1))

    h1 = y > F['var1']
    h25 = y > F['var25']
    dxi = xi_s.pct_change().shift(-1)        # change caused by day t
    top_xi = dxi.nlargest(1)


    res = dict(
        paper=dict(sample='1962-07-03 to 2020-12-31', T=14726, T_exc=1495, a_xi=0.025, a_delta=0.112, b_xi=0.9993,
                   b_delta=0.995, a_tau=0.241, b_tau=0.989, xi_range=[0.05, 0.25], delta_range=[0.2, 2.0],
                   exc_rate_var99=0.010, mean_loss_beyond_var99=3.54, mean_es99=3.12),
        sample=dict(first=str(dates[0].date()), last=str(dates[-1].date()), T=int(len(y)), T_exc=n_exc),
        tau=tp, theta=dict(zip(NAMES, th)), loglik=ll, static=st, aic_dyn=aic_dyn, aic_static=aic_st,
        lr=2 * (ll - st['loglik']), loglik_const_shape=llc, aic_const_shape=aic_const,
        theta_const_shape=dict(zip(['fbar_xi', 'fbar_delta', 'a_delta', 'b_delta'], thc)), xi_const_shape=float(np.exp(thc[0])),
        xi_min=float(xi_s.min()), xi_max=float(xi_s.max()), xi_min_date=str(xi_s.idxmin().date()),
        xi_max_date=str(xi_s.idxmax().date()), xi_p05=float(xi_s.quantile(0.05)), xi_p95=float(xi_s.quantile(0.95)),
        delta_min=float(de_s.min()), delta_max=float(de_s.max()), delta_max_date=str(de_s.idxmax().date()),
        top_dxi_date=str(top_xi.index[0].date()), top_dxi=float(100 * top_xi.iloc[0]),
        exc_rate_var1=float(h1.mean()), n_exc_var1=int(h1.sum()), mean_loss_beyond_var1=float(y[h1].mean()),
        mean_es1=float(F['es1'].mean()), mean_es1_exc_days=float(F['es1'][h1].mean()),
        exc_rate_var25=float(h25.mean()), n_exc_var25=int(h25.sum()), mean_loss_beyond_var25=float(y[h25].mean()),
        mean_es25_exc_days=float(F['es25'][h25].mean()),
        var1_min=float(F['var1'].min()), var1_max=float(F['var1'].max()), var1_max_date=str(dates[np.argmax(F['var1'])].date()),
        xi_last=float(F['xi'][-1]), var1_last=float(F['var1'][-1]), es25_last=float(F['es25'][-1]),
        events=ev, gfc=dict(dxi=chg(xi_s, '2008-08-29', '2009-03-31'), ddelta=chg(de_s, '2008-08-29', '2009-03-31')),
        covid=dict(dxi=chg(xi_s, '2020-02-19', '2020-04-30'), ddelta=chg(de_s, '2020-02-19', '2020-04-30')),
        est2015=est2015_block(y, dates),
    )
    with open(os.path.join(HERE, 'ch7_tailshape.json'), 'w') as f:
        json.dump(res, f, indent=1)
    pd.DataFrame({'loss': y, 'tau': F['tau'], 'xi': F['xi'], 'delta': F['delta'], 'var1': F['var1'],
                  'es25': F['es25'], 'share': F['share']}, index=dates).rename_axis('date') \
        .to_csv(os.path.join(HERE, 'ch7_tailshape_series.csv'), float_format='%.6f')
    chart(dates, y, F, st, res['paper'], res['xi_const_shape'])
    return res


def chart(dates, y, F, st, paper, xi_const):
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(5.9, 2.75), gridspec_kw=dict(width_ratios=[1.45, 1, 1]))
    a1.vlines(dates, 0, np.clip(y, 0, None), color=Teal, alpha=0.7, linewidth=0.35, label='Daily loss (gains set to 0)')
    a1.plot(dates, F['tau'], color=Forest, lw=0.6, label=r'Threshold $\tau_t$ (90% quantile)')
    a1.plot(dates, F['var1'], color=MainBlue, lw=0.8, label='VaR 1%')
    a1.plot(dates, F['es25'], color=IDAred, lw=0.6, ls=(0, (2, 1.2)), label='ES 2.5%')
    hit = y > F['var1']
    a1.scatter(dates[hit], y[hit], s=3, color=Orange, zorder=4, lw=0, label='Loss above VaR 1%')
    a1.set_ylabel('Daily loss (%)', fontsize=8)
    a1.set_title('S&P 500 losses, VaR and ES', fontsize=8.6)
    a1.set_ylim(0, 13.5)
    a2.axhspan(*paper['xi_range'], color=BandBlue, alpha=0.6, lw=0, label="Paper's range, 1962–2020")
    a2.plot(dates, F['xi'], color=MainBlue, lw=0.8, label=r'Score-driven $\xi_t$, $\delta_t$')
    a2.axhline(st['xi'], color=Navy, lw=0.7, ls='--', label='Static GPD, same thresholds')
    a2.axhline(xi_const, color=Orange, lw=0.9, ls='-.', label=r'Constant $\xi$, score-driven $\delta_t$')
    a2.set_title(r'Tail shape $\xi_t$', fontsize=8.6)
    a3.plot(dates, F['delta'], color=MainBlue, lw=0.8)
    a3.axhline(st['delta'], color=Navy, lw=0.7, ls='--')
    a3.set_title(r'Tail scale $\delta_t$ (%)', fontsize=8.6)
    for ax in (a1, a2, a3):
        ax.tick_params(labelsize=7.6)
        ax.xaxis.set_major_locator(mdates.YearLocator(10 if ax is not a1 else 5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    h1, l1 = a1.get_legend_handles_labels()
    h2, l2 = a2.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='lower center', ncol=3, fontsize=7.4, bbox_to_anchor=(0.5, -0.02),
               handlelength=1.2, columnspacing=0.7)
    fig.subplots_adjust(left=0.07, right=0.995, top=0.91, bottom=0.33, wspace=0.3)
    os.makedirs(CHART_DIR, exist_ok=True)
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(CHART_DIR, f'ch7_tailshape.{ext}'), transparent=True, dpi=200)
    plt.close(fig)
    print('   saved ch7_tailshape')


if __name__ == '__main__':
    if '--est2015' in sys.argv:
        print(json.dumps(update_est2015(), indent=1))
        sys.exit(0)
    out = main()
    print(json.dumps({k: v for k, v in out.items() if k != 'paper'}, indent=1))

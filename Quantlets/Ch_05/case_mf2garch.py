"""
case_mf2garch.py -- second case study of Chapter 5: the MF2-GARCH of Conrad & Engle (2025)
===========================================================================================
Conrad, C., Engle, R.F. (2025). Modelling volatility cycles: the MF2-GARCH model. Journal of Applied
Econometrics 40(4), 438-454, doi:10.1002/jae.3118.

Model (MF2-GARCH-rw-m, equations 4-6 of the paper), returns in %:
    r_t = mu + e_t,  e_t = sqrt(h_t tau_t) Z_t
    h_t   = (1 - phi) + (alpha + gamma 1{e_{t-1} < 0}) e_{t-1}^2 / tau_{t-1} + beta h_{t-1},  phi = alpha + gamma/2 + beta
    tau_t = lambda0 + lambda1 V^(m)_{t-1} + lambda2 tau_{t-1},  V^(m)_{t-1} = (1/m) sum_{j=1}^m e_{t-j}^2 / h_{t-j}
The nested one-component model is the GJR-GARCH(1,1). Both are estimated by Gaussian quasi-maximum likelihood with
Bollerslev-Wooldridge robust standard errors, as in the paper.

Course replication: daily S&P 500 log returns (course data, data/market/GSPC.INDX.csv), 2 January 1990 -
18 September 2026, instead of January 1971 - June 2023:
  1. m chosen by the BIC over m = 5, ..., 160 on the full sample (likelihoods on the same days for every m);
  2. the estimated conditional and long-term volatility (Figure 4 of the paper);
  3. out-of-sample forecasts, January 2010 - September 2026, rolling window of 20 years, parameters re-estimated
     every 21 trading days, m chosen once by the BIC on 1990-2009; horizons: one day, one week, and the forward
     variance of months 1 to 8 (21 trading days each); losses relative to the historical forecast (mean of r^2 over
     the 10 years before the origin), QLIKE and RMSE, as in Tables 4-5 of the paper. Proxy: squared daily returns
     (the paper uses 5-minute realised variances plus the overnight return, which the course data do not have
     before 2020).
Output: ch5_mf2_case.json, charts/ch5_mf2_garch.pdf/.png.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import optimize
from numba import njit
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
try:
    import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
except ImportError:
    pass
from mfm_data import pct_returns, periods_per_year   # noqa: E402

plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 11.5
plt.rcParams['ytick.labelsize'] = 11.5
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.4
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 11

MainBlue, IDAred, Forest, Navy, BandBlue = '#1A3A6E', '#CD0000', '#2E7D32', '#1F2A44', '#C5D2E8'
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
OUT_JSON = os.path.join(HERE, 'ch5_mf2_case.json')

START, END = '1990-01-01', '2026-09-18'
M_GRID = list(range(5, 161))
BURN = 160                      # likelihood summed from the same day for every m
OOS_START = '2010-01-01'
STEP = 21                       # re-estimation every 21 trading days
HOR = [('Day', 1, 1), ('Week', 1, 5)] + [(f'{k}m', 21 * (k - 1) + 1, 21 * k) for k in range(1, 9)]
SMAX = 168
NBER = [('1990-07-01', '1991-03-31'), ('2001-03-01', '2001-11-30'), ('2007-12-01', '2009-06-30'),
        ('2020-02-01', '2020-04-30')]
# the paper's numbers (Table 2: January 1971 - June 2023; Table 4: out of sample 2010-2019)
PAPER = dict(gjr=dict(alpha=0.023, gamma=0.115, beta=0.901, phi=0.982),
             mf2=dict(m=63, alpha=0.003, gamma=0.162, beta=0.840, lambda0=0.018, lambda1=0.112, lambda2=0.870,
                      phi=0.924, lam=0.982),
             t4_rmse=dict(gjr={'1m': 0.798, '8m': 0.866}, mf2={'1m': 0.685, '8m': 0.811}),
             t4_qlike=dict(gjr={'1m': 0.723, '8m': 0.918}, mf2={'1m': 0.708, '8m': 0.859}))


# ----------------------------------------------------------------------------- filters (numba)
@njit
def gjr_filter(e, omega, alpha, gamma, beta, h0):
    n = e.shape[0]
    h = np.empty(n + 1)
    h[0] = h0
    for t in range(1, n + 1):
        a = alpha + (gamma if e[t - 1] < 0 else 0.0)
        h[t] = omega + a * e[t - 1] ** 2 + beta * h[t - 1]
    return h            # h[t]: variance of e[t]; h[n]: one-day-ahead forecast after the last day


@njit
def mf2_filter(e, alpha, gamma, beta, l0, l1, l2, m, tau0):
    """h, tau and V = e^2/h for t = 0..n (index n: the values for the day after the last observation)."""
    n = e.shape[0]
    phi = alpha + gamma / 2 + beta
    h = np.empty(n + 1)
    tau = np.empty(n + 1)
    V = np.empty(n)
    h[0] = 1.0
    tau[0] = tau0
    run = 0.0
    for t in range(n):
        V[t] = e[t] ** 2 / h[t]
        run += V[t]
        if t >= m:
            run -= V[t - m]
        a = alpha + (gamma if e[t] < 0 else 0.0)
        h[t + 1] = (1 - phi) + a * e[t] ** 2 / tau[t] + beta * h[t]
        if t + 1 >= m:
            tau[t + 1] = l0 + l1 * run / m + l2 * tau[t]
        else:
            tau[t + 1] = tau0                     # the first m days: tau fixed at the sample variance
    return h, tau, V


@njit
def mf2_forecast(V_last, h1, tau1, alpha, gamma, beta, l0, l1, l2, m, kappa, S):
    """E_t[sigma^2_{t+s}], s = 1..S, given h_{t+1}, tau_{t+1} and the last m values V_{t-m+1..t} (oldest first).

    Derived from the recursions: with a_k = (alpha + gamma 1{Z_k<0}) Z_k^2 + beta, E a = phi and
    E[a Z^2] = phi_kappa = (alpha + gamma/2) kappa + beta for a symmetric density (Assumption 1 of the paper):
      E[h_{t+s} tau_{t+s-1}] = (1-phi) E tau_{t+s-1} + phi E sigma^2_{t+s-1}
      E[h_{t+s} V_{k}]       = (1-phi) (1 + phi + ... + phi^{j-1}) E tau_k + phi^{j-1} phi_kappa E sigma^2_k, k = t+s-j > t
      E[h_{t+s} V_{k}]       = V_k E h_{t+s}, k <= t
    """
    phi = alpha + gamma / 2 + beta
    phik = (alpha + gamma / 2) * kappa + beta
    Eh = np.empty(S + 1)
    Et = np.empty(S + 1)
    Es = np.empty(S + 1)
    Eh[1] = h1
    Et[1] = tau1
    Es[1] = h1 * tau1
    for s in range(2, S + 1):
        Eh[s] = 1 + phi ** (s - 1) * (h1 - 1)
        # E tau_{t+s}
        acc = 0.0
        for j in range(1, m + 1):
            k = s - j                      # k >= 1: future day t+k; k <= 0: known V_{t+k}
            acc += Et[k] if k >= 1 else V_last[m - 1 + k]
        Et[s] = l0 + l1 * acc / m + l2 * Et[s - 1]
        # E sigma^2_{t+s}
        acc = 0.0
        for j in range(1, m + 1):
            k = s - j
            if k >= 1:
                geo = (1 - phi ** j) / (1 - phi)
                acc += (1 - phi) * geo * Et[k] + phi ** (j - 1) * phik * Es[k]
            else:
                acc += V_last[m - 1 + k] * Eh[s]
        Es[s] = l0 * Eh[s] + l2 * ((1 - phi) * Et[s - 1] + phi * Es[s - 1]) + l1 * acc / m
    return Es[1:]


def gamma_m(alpha, gamma, beta, l1, l2, m, kappa):
    """Theorem 1 of the paper: covariance stationarity of the returns requires
    Gamma_m = l1 phi_kappa / m + l2 phi + (l1 phi_kappa / m) sum_{j=2}^m phi^{j-1} < 1,  phi_kappa = (alpha + gamma/2) kappa + beta
    (the coefficient of E sigma^2_{t+s-1} in the forecast recursion of mf2_forecast)."""
    phi = alpha + gamma / 2 + beta
    phik = (alpha + gamma / 2) * kappa + beta
    return float(l1 * phik / m + l2 * phi + l1 * phik / m * sum(phi ** (j - 1) for j in range(2, m + 1)))


def slow_dynamics(l1, l2, m, S=3000):
    """E_t tau_{t+s} - E tau follows an AR(m) recursion with c_1 = l2 + l1/m and c_j = l1/m (j = 2..m).
    Returns the dominant root, the asymptotic half-life ln(0.5)/ln(root), and the response of tau to a unit shock
    in one daily standardised error V_t (it enters V^(m) for m days): the day of the peak and the day on which the
    response has fallen to half of the peak."""
    c = np.full(m, l1 / m)
    c[0] += l2
    root = float(max(abs(np.roots(np.concatenate(([1.0], -c))))))
    x = np.zeros(S)
    for s in range(1, S):
        x[s] = sum(c[j] * x[s - 1 - j] for j in range(min(m, s))) + (l1 / m if s <= m else 0.0)
    pk = int(x.argmax())
    half = pk + int(np.argmax(x[pk:] <= x[pk] / 2))
    return dict(root=root, hl_asym=float(np.log(0.5) / np.log(root)), peak_day=pk, half_day=half)


# ----------------------------------------------------------------------------- likelihoods
def _ll_obs(s2, e):
    return -0.5 * (np.log(2 * np.pi) + np.log(s2) + e ** 2 / s2)


def gjr_llobs(theta, r, burn):
    mu, omega, alpha, gamma, beta = theta
    e = r - mu
    h = gjr_filter(e, omega, alpha, gamma, beta, np.var(r))[:-1]
    return _ll_obs(h[burn:], e[burn:])


def mf2_llobs(theta, r, m, burn):
    mu, alpha, gamma, beta, l0, l1, l2 = theta
    e = r - mu
    h, tau, _ = mf2_filter(e, alpha, gamma, beta, l0, l1, l2, m, np.var(r))
    return _ll_obs((h * tau)[:-1][burn:], e[burn:])


def _neg(f, *a):
    def g(theta):
        v = f(theta, *a).sum()
        return 1e10 if not np.isfinite(v) else -v
    return g


def fit_gjr(r, burn, x0=None):
    x0 = np.array(x0 if x0 is not None else [r.mean(), 0.02, 0.02, 0.12, 0.90])
    cons = [{'type': 'ineq', 'fun': lambda x: 0.9999 - x[2] - x[3] / 2 - x[4]}]
    b = [(-1, 1), (1e-6, 2), (0, 0.5), (0, 0.8), (0, 0.9999)]
    res = optimize.minimize(_neg(gjr_llobs, r, burn), x0, method='SLSQP', bounds=b, constraints=cons,
                            options=dict(maxiter=500, ftol=1e-10))
    return res.x, -res.fun


def fit_mf2(r, m, burn, x0=None):
    x0 = np.array(x0 if x0 is not None else [r.mean(), 0.01, 0.15, 0.84, 0.02, 0.10, 0.87])
    x0[4] = max(x0[4], 1e-4)
    cons = [{'type': 'ineq', 'fun': lambda x: 0.9999 - x[1] - x[2] / 2 - x[3]},
            {'type': 'ineq', 'fun': lambda x: 0.9999 - x[5] - x[6]}]
    b = [(-1, 1), (0, 0.5), (0, 0.8), (0, 0.9999), (1e-6, 5), (0, 1), (0, 0.9999)]
    res = optimize.minimize(_neg(mf2_llobs, r, m, burn), x0, method='SLSQP', bounds=b, constraints=cons,
                            options=dict(maxiter=500, ftol=1e-10))
    return res.x, -res.fun


def robust_se(llobs, theta, *a):
    """Bollerslev-Wooldridge sandwich: H^{-1} J H^{-1}, numerical scores and Hessian."""
    k = len(theta)
    eps = 1e-5 * np.maximum(np.abs(theta), 1e-2)
    G = np.empty((len(llobs(theta, *a)), k))
    for i in range(k):
        d = np.zeros(k); d[i] = eps[i]
        G[:, i] = (llobs(theta + d, *a) - llobs(theta - d, *a)) / (2 * eps[i])
    H = np.empty((k, k))
    for i in range(k):
        d = np.zeros(k); d[i] = eps[i]
        gp = np.array([((llobs(theta + d + dd, *a) - llobs(theta + d - dd, *a)).sum()) / (2 * eps[j])
                       for j, dd in ((j, np.eye(k)[j] * eps[j]) for j in range(k))])
        gm = np.array([((llobs(theta - d + dd, *a) - llobs(theta - d - dd, *a)).sum()) / (2 * eps[j])
                       for j, dd in ((j, np.eye(k)[j] * eps[j]) for j in range(k))])
        H[:, i] = (gp - gm) / (2 * eps[i])
    H = (H + H.T) / 2
    Hi = np.linalg.inv(-H)
    return np.sqrt(np.diag(Hi @ (G.T @ G) @ Hi))


# ----------------------------------------------------------------------------- full sample
def full_sample(r):
    x = r.values
    n_eff = len(x) - BURN
    th_g, ll_g = fit_gjr(x, BURN)
    bic_g = (-2 * ll_g + 5 * np.log(n_eff)) / n_eff
    rows, x0 = [], None
    for m in M_GRID:
        th, ll = fit_mf2(x, m, BURN, x0)
        if x0 is None or ll > -1e9:
            x0 = th
        rows.append(dict(m=m, ll=ll, bic=(-2 * ll + 7 * np.log(n_eff)) / n_eff, theta=th))
    # second pass from the neighbours' estimates, to avoid local optima along the grid
    for i in range(len(rows)):
        for j in (i - 1, i + 1):
            if 0 <= j < len(rows):
                th, ll = fit_mf2(x, rows[i]['m'], BURN, rows[j]['theta'].copy())
                if ll > rows[i]['ll'] + 1e-6:
                    rows[i].update(ll=ll, bic=(-2 * ll + 7 * np.log(n_eff)) / n_eff, theta=th)
    best = min(rows, key=lambda d: d['bic'])
    m = best['m']
    th = best['theta']
    se = robust_se(mf2_llobs, th, x, m, BURN)
    se_g = robust_se(gjr_llobs, th_g, x, BURN)
    e = x - th[0]
    h, tau, V = mf2_filter(e, *th[1:], m, np.var(x))
    z = e / np.sqrt(h[:-1] * tau[:-1])
    out = dict(n=len(x), n_eff=n_eff, start=str(r.index[0].date()), end=str(r.index[-1].date()), m=m,
               gjr=dict(zip(['mu', 'omega', 'alpha', 'gamma', 'beta'], th_g.tolist())),
               gjr_se=dict(zip(['mu', 'omega', 'alpha', 'gamma', 'beta'], se_g.tolist())),
               mf2=dict(zip(['mu', 'alpha', 'gamma', 'beta', 'lambda0', 'lambda1', 'lambda2'], th.tolist())),
               mf2_se=dict(zip(['mu', 'alpha', 'gamma', 'beta', 'lambda0', 'lambda1', 'lambda2'], se.tolist())),
               ll_gjr=ll_g, ll_mf2=best['ll'], bic_gjr=bic_g, bic_mf2=best['bic'],
               bic_grid=[dict(m=d['m'], bic=d['bic'], ll=d['ll']) for d in rows],
               grid_theta={str(d['m']): d['theta'].tolist() for d in rows},
               kappa=float(np.mean(z[BURN:] ** 4)))
    p = out['gjr']
    out['gjr']['phi'] = p['alpha'] + p['gamma'] / 2 + p['beta']
    q = out['mf2']
    out['mf2']['phi'] = q['alpha'] + q['gamma'] / 2 + q['beta']
    out['mf2']['lam'] = q['lambda1'] + q['lambda2']
    out['mf2']['Gamma_m'] = gamma_m(q['alpha'], q['gamma'], q['beta'], q['lambda1'], q['lambda2'], m, out['kappa'])
    out['mf2']['slow'] = slow_dynamics(q['lambda1'], q['lambda2'], m)
    for mm in (21, 63, 126):
        d = next(d for d in rows if d['m'] == mm)
        out[f'bic_m{mm}'] = d['bic']
    series = pd.DataFrame({'sigma': np.sqrt(h[:-1] * tau[:-1]), 'tau': np.sqrt(tau[:-1])}, index=r.index)
    return out, series


# ----------------------------------------------------------------------------- out of sample
def out_of_sample(r):
    x = r.values
    idx = r.index
    i0 = int(np.searchsorted(idx, pd.Timestamp(OOS_START)))
    W = i0                                            # rolling window: 20 years (1990-2009)
    # m chosen once, by the BIC on the first window
    xw = x[:W]
    nw = W - BURN
    best, x0 = None, None
    for m in M_GRID:
        th, ll = fit_mf2(xw, m, BURN, x0)
        x0 = th
        b = (-2 * ll + 7 * np.log(nw)) / nw
        if best is None or b < best[0]:
            best = (b, m)
    m = best[1]
    n = len(x)
    last_origin = n - 1                               # origins: days i0-1 .. n-2 (forecast for day i0 onwards)
    F = {k: np.full((n, len(HOR)), np.nan) for k in ('gjr', 'mf2', 'hist')}
    th_m, th_g = None, None
    G = []                                            # Theorem 1 diagnostic and persistences, one row per window
    for b0 in range(i0, n, STEP):
        lo = b0 - W
        win = x[lo:b0]
        th_m, _ = fit_mf2(win, m, BURN, th_m)
        th_g, _ = fit_gjr(win, BURN, th_g)
        b1 = min(b0 + STEP, n)
        seg = x[lo:b1]
        # MF2: filter with the parameters estimated on the window ending at b0-1
        e = seg - th_m[0]
        h, tau, V = mf2_filter(e, *th_m[1:], m, np.var(win))
        zz = (e / np.sqrt(h[:-1] * tau[:-1]))[BURN:W]
        kappa = float(np.mean(zz ** 4))
        G.append(dict(start=str(idx[b0].date()), Gamma_m=gamma_m(*th_m[1:4], th_m[5], th_m[6], m, kappa),
                      phi=float(th_m[1] + th_m[2] / 2 + th_m[3]), lam=float(th_m[5] + th_m[6]), kappa=kappa))
        eg = seg - th_g[0]
        hg = gjr_filter(eg, *th_g[1:], np.var(win))
        om, al, ga, be = th_g[1:]
        pg = al + ga / 2 + be
        ug = om / (1 - pg)
        for t in range(b0 - 1, b1 - 1):              # origin t (close of day t), forecasts for t+1, ...
            j = t - lo                                # position in seg
            fm = mf2_forecast(V[j - m + 1:j + 1].copy(), h[j + 1], tau[j + 1], *th_m[1:], m, kappa, SMAX)
            s = np.arange(1, SMAX + 1)
            fg = ug + pg ** (s - 1) * (hg[j + 1] - ug)
            hist = np.mean(x[max(0, t - 2519):t + 1] ** 2)
            for c, (_, a, bb) in enumerate(HOR):
                F['mf2'][t, c] = fm[a - 1:bb].sum()
                F['gjr'][t, c] = fg[a - 1:bb].sum()
                F['hist'][t, c] = hist * (bb - a + 1)
    # realised proxies: sums of squared returns over the same days
    r2 = x ** 2
    cs = np.concatenate([[0], np.cumsum(r2)])
    Y = np.full((n, len(HOR)), np.nan)
    for c, (_, a, bb) in enumerate(HOR):
        for t in range(i0 - 1, n):
            if t + bb < n:
                Y[t, c] = cs[t + bb + 1] - cs[t + a]
    return dict(m=m, F=F, Y=Y, idx=idx, i0=i0, G=G)


def evaluate(o, end=None):
    idx = o['idx']
    res = {}
    for c, (lab, a, bb) in enumerate(HOR):
        ok = ~np.isnan(o['Y'][:, c]) & ~np.isnan(o['F']['mf2'][:, c])
        if end is not None:
            ok &= np.asarray(idx + pd.Timedelta(0) <= pd.Timestamp(end))
            # the target window must end before the cut-off as well
            last = np.searchsorted(idx, pd.Timestamp(end), side='right') - 1
            ok &= np.arange(len(idx)) + bb <= last
        y = o['Y'][ok, c]
        row = {}
        L = {}
        for k in ('hist', 'gjr', 'mf2'):
            f = o['F'][k][ok, c]
            pos = y > 0
            ql = np.full_like(y, np.nan)
            ql[pos] = y[pos] / f[pos] - np.log(y[pos] / f[pos]) - 1
            L[k] = dict(se=(y - f) ** 2, ql=ql)
            row[k] = dict(rmse=float(np.sqrt(np.mean((y - f) ** 2))), qlike=float(np.nanmean(ql)))
        for k in ('gjr', 'mf2'):
            row[k]['rmse_rel'] = row[k]['rmse'] / row['hist']['rmse']
            row[k]['qlike_rel'] = row[k]['qlike'] / row['hist']['qlike']
        # Diebold-Mariano, MF2 minus GJR, Newey-West with as many lags as the overlap of the targets.
        # QLIKE difference from y/f + ln f, defined also when y = 0 (the normalised form y/f - ln(y/f) - 1 is not):
        # it differs from the normalised loss only by terms in y, which cancel in the difference.
        L['mf2']['ql_d'] = y / o['F']['mf2'][ok, c] + np.log(o['F']['mf2'][ok, c])
        L['gjr']['ql_d'] = y / o['F']['gjr'][ok, c] + np.log(o['F']['gjr'][ok, c])
        for loss in ('ql', 'se'):
            key = 'ql_d' if loss == 'ql' else loss
            d = L['mf2'][key] - L['gjr'][key]
            d = d[~np.isnan(d)]
            ols = sm.OLS(d, np.ones_like(d)).fit(cov_type='HAC', cov_kwds={'maxlags': int(bb)})
            row[f'dm_{loss}'] = float(ols.tvalues[0])
        row['n'] = int(ok.sum())                      # eligible forecast origins (DM tests, RMSE)
        row['zero_days'] = int((y <= 0).sum())        # excluded from the normalised QLIKE ratio only
        row['n_qlike_ratio'] = int((y > 0).sum())
        res[lab] = row
    return res


def fig_case(series, oos_full, oos_pre, ppy, m):
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw=dict(width_ratios=[1.55, 1]))
    A = np.sqrt(ppy)
    for k, (a, b) in enumerate(NBER):
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=BandBlue, alpha=0.7, lw=0,
                   label='NBER recessions' if k == 0 else None)
    ax.plot(series.index, series['sigma'] * A, color=MainBlue, lw=0.5, label=r'Conditional volatility $\sqrt{h_t\tau_t}$')
    ax.plot(series.index, series['tau'] * A, color=IDAred, lw=1.6, label=rf'Long-term volatility $\sqrt{{\tau_t}}$, m = {m}')
    ax.set_ylim(0, 80)
    ax.set_ylabel('Annualised volatility (%)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    labs = [h[0] for h in HOR]
    xx = np.arange(len(labs))
    for k, col, name in (('gjr', Navy, 'GJR-GARCH'), ('mf2', IDAred, 'MF2-GARCH')):
        bx.plot(xx, [oos_full[l][k]['qlike_rel'] for l in labs], color=col, marker='o', ms=3.5, lw=1.3,
                label=f'{name}, 2010-2026')
        bx.plot(xx, [oos_pre[l][k]['qlike_rel'] for l in labs], color=col, marker='s', ms=3, lw=1.0, ls='--',
                label=f'{name}, 2010-2019')
    bx.axhline(1, color=Navy, lw=0.6, ls=':')
    bx.set_xticks(xx)
    bx.set_xticklabels(['1d', '1w'] + [f'M{k}' for k in range(1, 9)])
    bx.set_xlabel('Horizon: next day, next week, forward month M1-M8')
    bx.set_ylabel('QLIKE / QLIKE of the\nhistorical forecast')
    bx.legend(loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=2, frameon=False)
    plt.tight_layout()
    os.makedirs(CHART_DIR, exist_ok=True)
    for ext, kw in (('pdf', {}), ('png', dict(dpi=180))):
        plt.savefig(os.path.join(CHART_DIR, f'ch5_mf2_garch.{ext}'), bbox_inches='tight', transparent=True, **kw)
    plt.close()
    print('   saved ch5_mf2_garch')


def main():
    r = pct_returns('sp500', start=START, end=END)
    ppy = periods_per_year(r)
    print('S&P 500', r.index[0].date(), r.index[-1].date(), len(r), 'days')
    fs, series = full_sample(r)
    print('full sample: m =', fs['m'], 'BIC MF2', round(fs['bic_mf2'], 5), 'GJR', round(fs['bic_gjr'], 5))
    o = out_of_sample(r)
    print('out of sample: m =', o['m'])
    ev_full = evaluate(o)
    ev_pre = evaluate(o, end='2019-12-31')
    # the share of days on which the long-term component is above its mean (volatility cycles)
    tmean = fs['mf2']['lambda0'] / (1 - fs['mf2']['lam'])
    J = dict(fs, ppy=ppy, paper=PAPER, oos=dict(m=o['m'], start=str(o['idx'][o['i0']].date()), full=ev_full, pre=ev_pre,
                                                  window_days=int(o['i0']), step=STEP),
             tau_mean_vol=float(np.sqrt(tmean * ppy)),
             tau_max=dict(date=str(series['tau'].idxmax().date()), vol=float(series['tau'].max() * np.sqrt(ppy))),
             tau_min=dict(date=str(series['tau'].iloc[BURN:].idxmin().date()), vol=float(series['tau'].iloc[BURN:].min() * np.sqrt(ppy))),
             tau_last=float(series['tau'].iloc[-1] * np.sqrt(ppy)),
             oos_gamma=dict(n_windows=len(o['G']), max=max(g['Gamma_m'] for g in o['G']),
                            min=min(g['Gamma_m'] for g in o['G']), n_ge1=sum(g['Gamma_m'] >= 1 for g in o['G']),
                            max_start=max(o['G'], key=lambda g: g['Gamma_m'])['start'], windows=o['G']),
             horizons=[h[0] for h in HOR])
    # weekly series for the interactive page
    wk = series.iloc[BURN:].resample('W-FRI').last().dropna()
    J['weekly'] = dict(dates=[f'{d:%Y-%m-%d}' for d in wk.index], sigma=np.round(wk['sigma'].values * np.sqrt(ppy), 3).tolist(),
                       tau=np.round(wk['tau'].values * np.sqrt(ppy), 3).tolist())
    with open(OUT_JSON, 'w') as f:
        json.dump(J, f, indent=1, default=float)
    fig_case(series, ev_full, ev_pre, ppy, fs['m'])
    print(json.dumps({k: J[k] for k in ('m', 'gjr', 'mf2', 'mf2_se', 'bic_gjr', 'bic_mf2', 'kappa', 'tau_max', 'tau_min', 'tau_mean_vol')}, indent=1))
    for lab in J['horizons']:
        a, b = ev_full[lab], ev_pre[lab]
        print(f"{lab:5s} full: GJR {a['gjr']['qlike_rel']:.3f} MF2 {a['mf2']['qlike_rel']:.3f} DMql {a['dm_ql']:.2f} | "
              f"RMSE GJR {a['gjr']['rmse_rel']:.3f} MF2 {a['mf2']['rmse_rel']:.3f} DMse {a['dm_se']:.2f} || pre: "
              f"GJR {b['gjr']['qlike_rel']:.3f} MF2 {b['mf2']['qlike_rel']:.3f} DMql {b['dm_ql']:.2f} RMSE {b['gjr']['rmse_rel']:.3f}/{b['mf2']['rmse_rel']:.3f}  zeros {a['zero_days']}")


if __name__ == '__main__':
    main()

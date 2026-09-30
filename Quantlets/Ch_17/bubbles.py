"""
bubbles.py -- instrumentele Capitolului 17 (MFM): teste de explozivitate, LPPLS, drawdown-uri
============================================================================================
  * adf_windows(y, w0)     -- statistica ADF la dreapta pentru toate ferestrele [s, e] cu lungime >= w0
                              (regresia Delta y_t = a + b y_{t-1} + e_t, fara lag-uri), vectorizat pe s
  * psy(y, r0)             -- ADF, SADF (Phillips-Wu-Yu), GSADF si sirul BSADF (Phillips-Shi-Yu)
  * psy_cv(T, w0, R)       -- valori critice Monte Carlo sub mers aleator cu drift slab (PSY 2015)
  * wild_cv(y, w0, R)      -- valori critice prin wild bootstrap (robuste la volatilitate variabila)
  * episodes(stat, cv, ..) -- datarea episoadelor: inceput, sfarsit, durata minima
  * lppls_fit(t, y, ...)   -- modelul LPPLS, calibrarea Filimonov-Sornette (4 parametri liniari + 3 neliniari);
                              spatiul de cautare, filtrele si ferestrele din Shu & Zhu (2020), ec. (11)-(12)
  * drawdown(p)            -- scaderea fata de maximul anterior
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import optimize


# =============================================================================
# EXPLOSIVENESS TESTS (PWY 2011, PSY 2015)
# =============================================================================
def _cums(y):
    """Cumulative sums for the regression Delta y_t = a + b y_{t-1} (rows t = 1..n); y may be (n+1,) or (R, n+1)."""
    y = np.atleast_2d(np.asarray(y, float))
    x, z = y[:, :-1], np.diff(y, axis=1)
    pad = lambda a: np.concatenate([np.zeros((a.shape[0], 1)), np.cumsum(a, axis=1)], axis=1)
    return pad(x), pad(x * x), pad(z), pad(z * z), pad(x * z)


def _adf_end(C, e, s):
    """t-statistic of b for the windows [s, e] (s a vector), over all replications (rows of C)."""
    Sx, Sxx, Sz, Szz, Sxz = (c[:, e + 1][:, None] - c[:, s] for c in C)
    n = (e + 1 - s).astype(float)
    den = n * Sxx - Sx ** 2
    b = (n * Sxz - Sx * Sz) / den
    a = (Sz - b * Sx) / n
    ssr = np.maximum(Szz - a * Sz - b * Sxz, 1e-300)
    return b / np.sqrt(ssr / (n - 2) * n / den)


def adf_stat(y):
    """Right-tailed ADF on the whole series (no lags)."""
    C = _cums(y)
    n = len(y) - 1
    return float(_adf_end(C, n - 1, np.array([0]))[0, 0])


def min_window(T, r0=None):
    """Fereastra minima PSY: r0 = 0.01 + 1.8 / sqrt(T)."""
    r0 = 0.01 + 1.8 / np.sqrt(T) if r0 is None else r0
    return int(np.floor(r0 * T)), r0


def psy(y, r0=None):
    """ADF, SADF, GSADF and the BSADF (sup over start points) and recursive ADF (PWY) sequences for y (log level)."""
    y = np.asarray(y, float)
    n = len(y) - 1                                  # number of regression rows
    w0, r0 = min_window(n, r0)
    C = _cums(y)
    bsadf = np.full(n, np.nan)
    fwd = np.full(n, np.nan)
    for e in range(w0 - 1, n):
        s = np.arange(0, e - w0 + 2)
        st = _adf_end(C, e, s)[0]
        bsadf[e] = st.max()
        fwd[e] = st[0]
    return dict(adf=float(fwd[-1]), sadf=float(np.nanmax(fwd)), gsadf=float(np.nanmax(bsadf)),
                bsadf=bsadf, fwd=fwd, w0=w0, r0=r0, n=n)


def _null_paths(T, R, rng):
    """Random walk with a weak drift (PSY 2015): y_t = T^{-1} + y_{t-1} + e_t, e_t ~ N(0, 1)."""
    e = rng.standard_normal((R, T))
    return np.concatenate([np.zeros((R, 1)), np.cumsum(1.0 / T + e, axis=1)], axis=1)


def _bsadf_paths(Y, w0, chunk=100):
    """BSADF and recursive ADF sequences for several paths (rows of Y)."""
    R, n = Y.shape[0], Y.shape[1] - 1
    bs = np.full((R, n), np.nan)
    fw = np.full((R, n), np.nan)
    for i in range(0, R, chunk):
        C = _cums(Y[i:i + chunk])
        for e in range(w0 - 1, n):
            st = _adf_end(C, e, np.arange(0, e - w0 + 2))
            bs[i:i + chunk, e] = st.max(axis=1)
            fw[i:i + chunk, e] = st[:, 0]
    return bs, fw


def psy_cv(T, w0, R=1000, seed=42, q=(0.90, 0.95, 0.99)):
    """Monte Carlo critical values: ADF, SADF, GSADF (quantiles) and the 95% BSADF / recursive ADF sequences."""
    rng = np.random.default_rng(seed)
    bs, fw = _bsadf_paths(_null_paths(T, R, rng), w0)
    out = dict(T=T, w0=w0, R=R,
               adf={f'{int(100 * a)}': float(np.quantile(fw[:, -1], a)) for a in q},
               sadf={f'{int(100 * a)}': float(np.quantile(np.nanmax(fw, axis=1), a)) for a in q},
               gsadf={f'{int(100 * a)}': float(np.quantile(np.nanmax(bs, axis=1), a)) for a in q})
    out['bsadf95'] = np.nanquantile(bs, 0.95, axis=0)
    out['fwd95'] = np.nanquantile(fw, 0.95, axis=0)
    out['null'] = dict(adf=fw[:, -1], sadf=np.nanmax(fw, axis=1), gsadf=np.nanmax(bs, axis=1))
    return out


def wild_cv(y, w0, R=500, seed=42):
    """Wild bootstrap (Rademacher signs on Delta y, no drift): 95% BSADF sequence and 95% GSADF value."""
    rng = np.random.default_rng(seed)
    dy = np.diff(np.asarray(y, float))
    dy = dy - dy.mean()
    W = rng.choice([-1.0, 1.0], size=(R, len(dy)))
    Y = np.concatenate([np.zeros((R, 1)), np.cumsum(W * dy, axis=1)], axis=1)
    bs, _ = _bsadf_paths(Y, w0)
    return dict(bsadf95=np.nanquantile(bs, 0.95, axis=0), gsadf95=float(np.quantile(np.nanmax(bs, axis=1), 0.95)))


def episodes(stat, cv, index, min_len):
    """Episodes in which stat > cv for at least min_len periods: (start, end) dated in real time."""
    above = np.asarray(stat > cv)
    above[np.isnan(stat) | np.isnan(cv)] = False
    out, i, n = [], 0, len(above)
    while i < n:
        if above[i]:
            j = i
            while j + 1 < n and above[j + 1]:
                j += 1
            if j - i + 1 >= min_len:
                out.append((index[i], index[j] if j + 1 < n else None, j - i + 1))
            i = j + 1
        else:
            i += 1
    return out


# =============================================================================
# SIMULATED RATIONAL BUBBLES
# =============================================================================
def blanchard_watson(T=400, r=0.01, pi=0.97, b0=1.0, sd=0.5, seed=7):
    """Blanchard-Watson bubble: survives with prob. pi and grows at (1+r)/pi, otherwise returns to noise."""
    rng = np.random.default_rng(seed)
    b = np.empty(T)
    b[0] = b0
    for t in range(1, T):
        eps = sd * rng.standard_normal()
        b[t] = (1 + r) / pi * b[t - 1] + eps if rng.random() < pi else eps
    return b


def evans_bubble(T=400, r=0.02, alpha=1.0, delta=0.5, pi=0.85, seed=11):
    """Periodically collapsing bubble (Evans 1991): grows at (1+r) below alpha, then explodes or restarts at delta."""
    rng = np.random.default_rng(seed)
    u = np.exp(rng.normal(-0.5 * 0.07 ** 2, 0.07, T))   # u_t > 0, E[u_t] = 1 exact (lognormal)
    B = np.empty(T)
    B[0] = delta
    for t in range(1, T):
        if B[t - 1] <= alpha:
            B[t] = (1 + r) * B[t - 1] * u[t]
        else:
            theta = rng.random() < pi
            B[t] = (delta + (1 + r) / pi * (B[t - 1] - delta / (1 + r)) * theta) * u[t]
    return B


# =============================================================================
# LPPLS (Johansen-Ledoit-Sornette; Filimonov-Sornette 2013 calibration)
# Search space, filters and windows: Shu & Zhu (2020), Physica A 557, 124892, Section 2.2,
# equations (11)-(12), following Sornette et al. (2015)
# =============================================================================
LPPLS_SEARCH = dict(m=(0.0, 1.0), w=(1.0, 50.0), tc_frac=(0.0, 1 / 3), damping_min=1.0)            # eq. (11)
LPPLS_FILTER = dict(m=(0.01, 0.99), w=(2.0, 25.0), tc_frac=(0.0, 1 / 5), osc_min=2.5,             # eq. (12)
                    rel_err_max=0.15, lomb_alpha=0.10, ar1_alpha=0.10)
LPPLS_WINDOWS = list(range(750, 45, -5))       # t2 - t1 from 750 down to 50 observations, step 5: 141 windows
LPPLS_STEP = 5                                 # t2 moves by 5 observations


def lppls_design(t, tc, m, w):
    dt = np.maximum(tc - t, 1e-9)
    f = dt ** m
    lg = np.log(dt)
    return np.column_stack([np.ones_like(t), f, f * np.cos(w * lg), f * np.sin(w * lg)])


def lppls_linear(t, y, tc, m, w):
    """For given (tc, m, omega): A, B, C1, C2 by OLS and the sum of squared residuals."""
    X = lppls_design(t, tc, m, w)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    return beta, float(res @ res)


def _damping(m, w, beta):
    C = np.hypot(beta[..., 2], beta[..., 3])
    return m * np.abs(beta[..., 1]) / (w * np.maximum(C, 1e-300))


def _grid(t, y, tcs, ms, ws):
    TC, M, W = (a.ravel() for a in np.meshgrid(tcs, ms, ws, indexing='ij'))
    dt = np.maximum(TC[:, None] - t[None, :], 1e-9)
    f = dt ** M[:, None]
    lg = np.log(dt)
    X = np.stack([np.ones_like(f), f, f * np.cos(W[:, None] * lg), f * np.sin(W[:, None] * lg)], axis=2)
    XtX = np.einsum('gni,gnj->gij', X, X) + 1e-10 * np.eye(4)
    Xty = np.einsum('gni,n->gi', X, y)
    beta = np.linalg.solve(XtX, Xty[..., None])[..., 0]
    ssr = y @ y - np.einsum('gi,gi->g', beta, Xty)
    return TC, M, W, beta, ssr


def lppls_fit(t, y, search=LPPLS_SEARCH, refine=True, grid=(8, 8, 16)):
    """LPPLS calibration on the window (t, y), t in years: minimum SSR over the search space of eq. (11)
    (tc in [t2, t2 + (t2 - t1)/3], m in [0, 1], omega in [1, 50], damping >= 1): grid + Nelder-Mead."""
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    t1, t2 = t[0], t[-1]
    D = t2 - t1
    lo = np.array([t2 + search['tc_frac'][0] * D + 1e-6, search['m'][0] + 1e-3, search['w'][0]])
    hi = np.array([t2 + search['tc_frac'][1] * D, search['m'][1] - 1e-3, search['w'][1]])
    TC, M, W, beta, ssr = _grid(t, y, np.linspace(lo[0], hi[0], grid[0]), np.linspace(lo[1], hi[1], grid[1]),
                                np.linspace(lo[2], hi[2], grid[2]))
    ok = _damping(M, W, beta) >= search['damping_min']
    if not ok.any():
        return None
    k = int(np.argmin(np.where(ok, ssr, np.inf)))
    x0 = np.array([TC[k], M[k], W[k]])
    if refine:
        def obj(p):
            q = np.clip(p, lo, hi)
            b, sr = lppls_linear(t, y, *q)
            return sr if _damping(q[1], q[2], b) >= search['damping_min'] else sr + 1e6
        from scipy import optimize
        r = optimize.minimize(obj, x0, method='Nelder-Mead', options=dict(xatol=1e-5, fatol=1e-10, maxiter=400))
        if r.fun < 1e6:
            x0 = np.clip(r.x, lo, hi)
    tc, m, w = x0
    (A, B, C1, C2), s = lppls_linear(t, y, tc, m, w)
    C = np.hypot(C1, C2)
    yhat = lppls_design(t, tc, m, w) @ np.array([A, B, C1, C2])
    return dict(tc=float(tc), m=float(m), w=float(w), A=float(A), B=float(B), C1=float(C1), C2=float(C2), C=float(C),
                ssr=float(s), rmse=float(np.sqrt(s / len(t))), damping=float(m * abs(B) / (w * C)) if C > 0 else np.inf,
                osc=float(w / np.pi * np.log((tc - t1) / (tc - t2))),
                rel_err=float(np.max(np.abs(np.exp(yhat) - np.exp(y)) / np.exp(y))), t1=float(t1), t2=float(t2),
                _t=t, _y=y, _yhat=yhat)


def lomb_pvalue(fit, wmin=2.0, wmax=25.0, nw=200):
    """Lomb test: the detrended residual r = (tc - t)^(-m) (ln p - A - B (tc - t)^m) as a function of ln(tc - t);
    probability that the highest peak of the normalised periodogram arises by chance."""
    from scipy.signal import lombscargle
    t, y = fit['_t'], fit['_y']
    dt = np.maximum(fit['tc'] - t, 1e-9)
    r = dt ** (-fit['m']) * (y - fit['A'] - fit['B'] * dt ** fit['m'])
    x = np.log(dt)
    r = r - r.mean()
    ws = np.linspace(wmin, wmax, nw)
    p = lombscargle(x, r, ws) / r.var()                          # normalised periodogram (Scargle 1982): P_N = P / var(r)
    z = p.max()
    M = min(nw, len(r))
    return float(1 - (1 - np.exp(-z)) ** M)


def ar1_pass(fit, alpha):
    """The residual ln(p_hat) - ln(p) is AR(1) (Ornstein-Uhlenbeck): the Dickey-Fuller and Phillips-Perron tests reject
    a unit root at level alpha."""
    from statsmodels.tsa.stattools import adfuller
    from arch.unitroot import PhillipsPerron
    e = fit['_yhat'] - fit['_y']
    return bool(adfuller(e, maxlag=0, autolag=None, regression='c')[1] < alpha and PhillipsPerron(e, trend='c').pvalue < alpha)


def lppls_conditions(fit, flt=LPPLS_FILTER, search=LPPLS_SEARCH):
    """Conditions of eq. (12) (plus the damping of eq. 11); positive bubble: B < 0. The parameter conditions and the relative
    error are evaluated separately; the Lomb test only if all of them pass, and the unit-root test of the residual only
    if Lomb passes too (cumulative shares for the last two)."""
    if fit is None:
        return None
    D = fit['t2'] - fit['t1']
    c = dict(B=fit['B'] < 0, m=flt['m'][0] <= fit['m'] <= flt['m'][1], w=flt['w'][0] <= fit['w'] <= flt['w'][1],
             tc=fit['t2'] + flt['tc_frac'][0] * D <= fit['tc'] <= fit['t2'] + flt['tc_frac'][1] * D,
             osc=fit['osc'] >= flt['osc_min'], damping=fit['damping'] >= search['damping_min'],
             rel_err=fit['rel_err'] <= flt['rel_err_max'])
    if all(c.values()):
        c['lomb'] = lomb_pvalue(fit) <= flt['lomb_alpha']
        c['ar1'] = ar1_pass(fit, flt['ar1_alpha']) if c['lomb'] else False
    else:
        c['lomb'] = c['ar1'] = None
    return c


def lppls_qualified(fit, flt=LPPLS_FILTER):
    c = lppls_conditions(fit, flt)
    return bool(c is not None and all(v is True for v in c.values()))


def lppls_path(fit, t):
    """Fitted LPPLS path (log price), for t < tc."""
    t = np.asarray(t, float)
    return lppls_design(t, fit['tc'], fit['m'], fit['w']) @ np.array([fit['A'], fit['B'], fit['C1'], fit['C2']])


def lppls_confidence(t, y, t2_idx, windows=LPPLS_WINDOWS):
    """LPPLS confidence indicator (positive bubbles) at t2: share of windows [t2 - L, t2] with qualified fits."""
    q = []
    for L in windows:
        i1 = t2_idx - L
        if i1 < 0:
            continue
        f = lppls_fit(t[i1:t2_idx + 1], y[i1:t2_idx + 1])
        q.append(lppls_qualified(f))
    return float(np.mean(q)) if q else np.nan


# =============================================================================
# DRAWDOWN
# =============================================================================
def drawdown(p):
    """Fall from the previous peak: p_t / max_{s<=t} p_s - 1."""
    return p / p.cummax() - 1

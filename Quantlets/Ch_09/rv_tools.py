"""
rv_tools.py -- estimatori realizati, modelul HAR-RV si evaluarea prognozelor (Capitolul 9, MFM)
==============================================================================================
Randamentele intraday sunt in %, o linie = o zi; varianțele zilnice sunt in %^2.
  * rv, bv, tq, rq, jump_test         -- varianta realizata, variatia bipower, testul de salturi
  * sparse_points, subsampled_rv       -- esantionare rara si medie peste grile decalate
  * tsrv, realized_kernel, noise_var   -- estimatori robusti la zgomotul de microstructura
  * har_design, ols_nw, har_expanding  -- HAR-RV (Corsi), MCO cu erori Newey-West, prognoze out-of-sample
  * garch_forecasts, ewma_forecasts    -- repere: GARCH(1,1)-t si EWMA pe randamente zilnice
  * qlike, mse, dm_test, mz_test       -- functii de pierdere, testul Diebold-Mariano, regresia Mincer-Zarnowitz
  * block_bootstrap, roughness         -- bootstrap pe blocuri, exponentul Hurst al log-volatilitatii

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gamma as G

MU1 = np.sqrt(2 / np.pi)                              # E|Z|, Z ~ N(0,1)
MU43 = 2 ** (2 / 3) * G(7 / 6) / G(1 / 2)             # E|Z|^{4/3}


# =============================================================================
# REALISED ESTIMATORS (one value per day)
# =============================================================================
def rv(R):
    """Realised variance: sum of squared intraday returns."""
    return (R ** 2).sum(axis=1, min_count=1)


def nret(R):
    """Number of intraday returns of each day."""
    return R.notna().sum(axis=1)


def bv(R):
    """Bipower variation (Barndorff-Nielsen and Shephard): robust to jumps."""
    a = R.abs().values
    M = nret(R).values
    s = np.nansum(a[:, 1:] * a[:, :-1], axis=1)
    return pd.Series(MU1 ** -2 * M / (M - 1) * s, index=R.index)


def tq(R):
    """Tripower quarticity: estimates integrated quarticity, robust to jumps."""
    a = R.abs().values ** (4 / 3)
    M = nret(R).values
    s = np.nansum(a[:, 2:] * a[:, 1:-1] * a[:, :-2], axis=1)
    return pd.Series(M * MU43 ** -3 * M / (M - 2) * s, index=R.index)


def rq(R):
    """Realised quarticity (M/3) * sum r^4."""
    return nret(R) / 3 * (R ** 4).sum(axis=1)


def rv_ci(R, level=0.95):
    """Asymptotic confidence interval for integrated variance, built on the log scale."""
    v = rv(R)
    se_log = np.sqrt(2 / 3 * (R ** 4).sum(axis=1)) / v
    z = stats.norm.ppf(0.5 + level / 2)
    return v * np.exp(-z * se_log), v * np.exp(z * se_log)


def jump_test(R, alpha=0.001):
    """Ratio jump test (RV - BV)/RV (Huang and Tauchen); significant jump if z > z_{1-alpha}."""
    v, b, t = rv(R), bv(R), tq(R)
    M = nret(R)
    theta = MU1 ** -4 + 2 * MU1 ** -2 - 5
    z = ((v - b) / v) / np.sqrt(theta / M * np.maximum(1, t / b ** 2))
    jump = z > stats.norm.ppf(1 - alpha)
    J = np.where(jump, np.maximum(v - b, 0), 0.0)
    return pd.DataFrame({'rv': v, 'bv': b, 'tq': t, 'z': z, 'jump': jump, 'J': J, 'C': v - J})


# =============================================================================
# MICROSTRUCTURE NOISE
# =============================================================================
def sparse_points(P, k, offset=0):
    """Prices at every k-th grid point, starting at offset; the open and the close are kept."""
    out = {}
    last = P.notna().values.cumsum(axis=1).argmax(axis=1)
    cols = np.arange(P.shape[1])
    X = P.values
    for i, day in enumerate(P.index):
        idx = cols[(cols >= offset) & ((cols - offset) % k == 0) & (cols <= last[i])]
        idx = np.unique(np.r_[0, idx, last[i]])
        out[day] = np.log(X[i, idx])
    return out


def sparse_rv(P, k, offset=0):
    """Realised variance from k x 5-minute returns (a single grid)."""
    pts = sparse_points(P, k, offset)
    return pd.Series({d: np.sum((100 * np.diff(x)) ** 2) for d, x in pts.items()})


def subsampled_rv(P, k):
    """Average of the realised variances on the k shifted grids (sparse sampling without discarding data)."""
    return pd.concat([sparse_rv(P, k, o) for o in range(k)], axis=1).mean(axis=1)


def signature(P, ks, scale):
    """Signature plot: mean annualised volatility (%) as a function of the sampling interval."""
    return pd.DataFrame({
        'sparse': [np.sqrt(scale * sparse_rv(P, k).mean()) for k in ks],
        'subsampled': [np.sqrt(scale * subsampled_rv(P, k).mean()) for k in ks]}, index=list(ks))


def tsrv(P, K=6, adjust=False):
    """Two-scale realised variance (Zhang, Mykland and Ait-Sahalia): average over K grids minus the noise correction.
    Grilele pastreaza deschiderea si inchiderea, deci nbar = numarul mediu EFECTIV de randamente pe grila
    (the noise bias of the average is 2 nbar omega^2); adjust=True divides by 1 - nbar/n (small samples)."""
    R = 100 * np.log(P).diff(axis=1).iloc[:, 1:]
    n = nret(R)
    nbar = pd.concat([pd.Series({d: len(x) - 1 for d, x in sparse_points(P, K, o).items()}) for o in range(K)],
                     axis=1).mean(axis=1)
    ts = subsampled_rv(P, K) - nbar / n * rv(R)
    return ts / (1 - nbar / n) if adjust else ts


def noise_var(R):
    """Noise variance: omega^2 = -cov(r_i, r_{i-1}) and the upper bound RV/(2n), averaged over days."""
    X = R.values
    cov1 = np.nanmean(X[:, 1:] * X[:, :-1])
    return {'omega2_cov': max(-cov1, 0.0), 'omega2_rv': float((rv(R) / (2 * nret(R))).mean()),
            'rho1': float(pd.Series(X[:, 1:].ravel()).corr(pd.Series(X[:, :-1].ravel())))}


def parzen(x):
    x = np.abs(x)
    return np.where(x <= 0.5, 1 - 6 * x ** 2 + 6 * x ** 3, np.where(x <= 1, 2 * (1 - x) ** 3, 0.0))


def realized_kernel(R, P, c=3.5134):
    """Parzen realised kernel (Barndorff-Nielsen, Hansen, Lunde and Shephard); bandwidth H from their rule."""
    out, Hs = {}, {}
    iv20 = sparse_rv(P, 4)                                  # variance on the 20-minute grid, for xi
    for i, day in enumerate(R.index):
        r = R.iloc[i].dropna().values
        n = len(r)
        om2 = np.sum(r ** 2) / (2 * n)
        xi2 = om2 / max(iv20[day], 1e-12)
        H = max(1, int(np.ceil(c * xi2 ** 0.4 * n ** 0.6)))
        g = [np.sum(r[h:] * r[:n - h]) for h in range(H + 1)]
        out[day] = g[0] + 2 * sum(parzen(h / (H + 1)) * g[h] for h in range(1, H + 1))
        Hs[day] = H
    return pd.Series(out), pd.Series(Hs)


# =============================================================================
# HAR-RV
# =============================================================================
def har_design(v, calendar=False):
    """HAR regressors: daily, weekly and monthly components (5 and 22 trading days;
    for crypto, calendar days: 7 and 30 days, with at least 5 and 20 observations)."""
    if calendar:
        full = v.asfreq('D')
        d = full.shift(1)
        w = full.rolling(7, min_periods=5).mean().shift(1)
        m = full.rolling(30, min_periods=20).mean().shift(1)
        X = pd.DataFrame({'d': d, 'w': w, 'm': m}).reindex(v.index)
    else:
        X = pd.DataFrame({'d': v.shift(1), 'w': v.rolling(5).mean().shift(1), 'm': v.rolling(22).mean().shift(1)})
    return X


def nw_lags(T):
    return int(np.floor(4 * (T / 100) ** (2 / 9)))


def ols_nw(y, X, lags=None):
    """OLS with intercept and Newey-West (HAC) standard errors."""
    Xc = np.column_stack([np.ones(len(X)), np.asarray(X, float)])
    y = np.asarray(y, float)
    T, k = Xc.shape
    XtX_inv = np.linalg.inv(Xc.T @ Xc)
    b = XtX_inv @ Xc.T @ y
    e = y - Xc @ b
    L = nw_lags(T) if lags is None else lags
    u = Xc * e[:, None]
    S = u.T @ u
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        g = u[l:].T @ u[:-l]
        S += w * (g + g.T)
    V = XtX_inv @ S @ XtX_inv
    r2 = 1 - e @ e / np.sum((y - y.mean()) ** 2)
    return {'b': b, 'se': np.sqrt(np.diag(V)), 'V': V, 'r2': r2, 'resid': e, 'T': T, 'lags': L}


def har_fit(v, calendar=False, log=False, jumps=None):
    """HAR-RV on the full sample; log=True: HAR on log RV; jumps: jump component as an extra regressor."""
    X = har_design(np.log(v) if log else v, calendar)
    if jumps is not None:
        X['J'] = jumps.shift(1).reindex(X.index) if not calendar else jumps.asfreq('D').shift(1).reindex(X.index)
    y = np.log(v) if log else v
    ok = X.notna().all(axis=1)
    return ols_nw(y[ok], X[ok]), X, ok


def har_expanding(v, start, calendar=False, log=False, min_obs=100):
    """HAR forecasts for day t, re-estimated daily on all observations before t (expanding window)."""
    y = np.log(v) if log else v
    X = har_design(y, calendar)
    ok = X.notna().all(axis=1)
    Xv, yv = X.values, y.values
    Xc = np.column_stack([np.ones(len(X)), Xv])
    out = {}
    for t in np.where((v.index >= pd.Timestamp(start)) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        if len(tr) < min_obs:
            continue
        b, *_ = np.linalg.lstsq(Xc[tr], yv[tr], rcond=None)
        f = Xc[t] @ b
        if log:
            s2 = np.var(yv[tr] - Xc[tr] @ b)
            f = np.exp(f + s2 / 2)
        out[v.index[t]] = f
    return pd.Series(out)


def har_weights(b, n=30):
    """Implied HAR weights on each lag 1..n (HAR = restricted AR(22))."""
    w = np.zeros(n)
    w[0] += b[1]
    w[:5] += b[2] / 5
    w[:22] += b[3] / 22
    return w


# =============================================================================
# BENCHMARKS: GARCH AND EWMA ON DAILY RETURNS
# =============================================================================
def garch_forecasts(r, dates, refit=21, dist='t'):
    """Forecast variance for each day in dates with GARCH(1,1), re-estimated every `refit` days
    on all earlier data; between re-estimations the parameters stay fixed and the variance is updated daily."""
    from arch import arch_model
    dates = pd.DatetimeIndex(dates)
    pos = r.index.get_indexer(dates)
    out = pd.Series(np.nan, index=dates)
    for i0 in range(0, len(dates), refit):
        blk = dates[i0:i0 + refit]
        p0 = pos[i0]
        fit = arch_model(r.iloc[:p0], mean='Constant', vol='GARCH', p=1, q=1, dist=dist).fit(disp='off')
        fixed = arch_model(r.iloc[:pos[min(i0 + refit, len(dates)) - 1] + 1], mean='Constant', vol='GARCH', p=1, q=1,
                           dist=dist).fix(fit.params)
        out[blk] = (fixed.conditional_volatility ** 2).reindex(blk).values
    return out


def ewma_forecasts(r, lam=0.94, burn=250):
    """RiskMetrics: sigma^2_t = lambda sigma^2_{t-1} + (1 - lambda) r^2_{t-1}."""
    x = r.values
    s = np.empty(len(x))
    s[0] = np.var(x[:burn])
    for t in range(1, len(x)):
        s[t] = lam * s[t - 1] + (1 - lam) * x[t - 1] ** 2
    return pd.Series(s, index=r.index)


# =============================================================================
# FORECAST EVALUATION
# =============================================================================
def qlike(v, f):
    """QLIKE: v/f - log(v/f) - 1 (robust to noise in the proxy, Patton 2011)."""
    return v / f - np.log(v / f) - 1


def mse(v, f):
    return (v - f) ** 2


def dm_test(l1, l2):
    """Diebold-Mariano: d = l1 - l2; t = mean(d)/se_NW; d < 0 => model 1 has the smaller loss."""
    d = (l1 - l2).dropna().values
    res = ols_nw(d, np.empty((len(d), 0)))
    t = res['b'][0] / res['se'][0]
    return {'mean_diff': float(d.mean()), 't': float(t), 'p': float(2 * stats.norm.sf(abs(t))), 'T': len(d)}


def mz_test(v, f):
    """Mincer-Zarnowitz regression v = a + b f + e; joint Wald test of (a, b) = (0, 1) with the NW covariance."""
    res = ols_nw(v.values, f.values[:, None])
    dlt = res['b'] - np.array([0.0, 1.0])
    W = float(dlt @ np.linalg.inv(res['V']) @ dlt)
    return {'a': res['b'][0], 'b': res['b'][1], 'se_a': res['se'][0], 'se_b': res['se'][1], 'r2': res['r2'],
            'wald': W, 'p': float(stats.chi2.sf(W, 2))}


def block_bootstrap(x, stat, block=20, B=2000, seed=42):
    """Moving-block bootstrap (Kunsch): distribution of `stat` on series rebuilt from blocks."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    n = len(x)
    nb = int(np.ceil(n / block))
    out = np.empty(B)
    for b in range(B):
        starts = rng.integers(0, n - block + 1, nb)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]
        out[b] = stat(x[idx])
    return out


def block_bootstrap_blocks(x, stat, block=60, B=300, seed=42):
    """Moving-block bootstrap that keeps the blocks separate: `stat` receives a matrix (blocks x length),
    so increments are computed only within each block (no artificial jumps at the joins)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    n = len(x)
    nb = int(np.ceil(n / block))
    out = np.empty(B)
    for b in range(B):
        starts = rng.integers(0, n - block + 1, nb)
        out[b] = stat(x[starts[:, None] + np.arange(block)[None, :]])
    return out


# =============================================================================
# ROUGH VOLATILITY
# =============================================================================
def roughness(logsig, qs=(0.5, 1.0, 1.5, 2.0, 3.0), lags=range(1, 31)):
    """m(q, D) = mean |log sigma_{t+D} - log sigma_t|^q ~ D^{q H}: slope zeta_q = q H on the log-log scale."""
    x = np.asarray(logsig, dtype=float)             # 1D: one series (NaN = missing day); 2D: blocks, increments only within a block
    lags = np.array(list(lags))
    M = {q: np.array([np.nanmean(np.abs(x[..., l:] - x[..., :-l]) ** q) for l in lags]) for q in qs}
    zeta = {q: np.polyfit(np.log(lags), np.log(M[q]), 1)[0] for q in qs}
    H = np.polyfit(list(qs), [zeta[q] for q in qs], 1)[0] if len(qs) > 1 else zeta[qs[0]] / qs[0]
    return {'lags': lags, 'm': M, 'zeta': zeta, 'H': float(H)}

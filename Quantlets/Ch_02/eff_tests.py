"""
eff_tests.py -- Teste de eficienta slaba pentru Capitolul 2 (MFM)
===============================================================
  * variance_ratio      -- Lo & MacKinlay (1988): VR(q), z omoscedastic, z* robust la heteroscedasticitate
  * chow_denning        -- testul multiplu Chow & Denning (1993): max |z*(q_i)|
  * runs_test           -- testul secventelor (Wald & Wolfowitz, 1940) pe semnele randamentelor
  * robust_ljung_box    -- Q(m) clasic si Q~(m) robust (varianta robusta a autocorelatiilor)
  * rs_hurst            -- R/S clasic (Hurst, 1951) si corectia Anis & Lloyd (1976)
  * lo_modified_rs      -- statistica V a lui Lo (1991), robusta la dependenta pe termen scurt
  * dfa_hurst           -- exponentul DFA (Peng et al., 1994)

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gammaln


# =============================================================================
# RAPORTUL DISPERSIILOR (VARIANCE RATIO)
# =============================================================================
def variance_ratio(r, q):
    """Overlapping VR(q) with the Lo-MacKinlay (1988) bias corrections.

    Returns (VR, homoskedastic z, heteroskedasticity-robust z*).
    """
    x = np.asarray(r, dtype=float)
    T = len(x)
    mu = x.mean()
    e = x - mu
    var_a = (e ** 2).sum() / (T - 1)
    agg = np.convolve(x, np.ones(q), mode='valid') - q * mu        # overlapping q-period sums
    m = q * (T - q + 1) * (1 - q / T)
    var_c = (agg ** 2).sum() / m
    vr = var_c / var_a
    z_homo = (vr - 1) / np.sqrt(2 * (2 * q - 1) * (q - 1) / (3 * q * T))
    den = (e ** 2).sum() ** 2
    theta = 0.0
    for j in range(1, q):
        delta = T * (e[j:] ** 2 * e[:-j] ** 2).sum() / den
        theta += (2 * (q - j) / q) ** 2 * delta
    z_star = np.sqrt(T) * (vr - 1) / np.sqrt(theta)
    return vr, z_homo, z_star


def chow_denning(r, qs=(2, 5, 10, 20)):
    """Chow-Denning multiple test: max |z*(q)|; p-value from the studentized maximum modulus (infinite df)."""
    zs = [variance_ratio(r, q)[2] for q in qs]
    zmax = np.max(np.abs(zs))
    p = 1 - (2 * stats.norm.cdf(zmax) - 1) ** len(qs)
    return zmax, p, zs


# =============================================================================
# TESTUL SECVENTELOR (RUNS TEST)
# =============================================================================
def runs_test(r):
    """Number of sign runs (zeros dropped), with its mean and variance under independence."""
    s = np.sign(np.asarray(r, dtype=float))
    s = s[s != 0]
    n1, n2 = (s > 0).sum(), (s < 0).sum()
    n = n1 + n2
    runs = 1 + (s[1:] != s[:-1]).sum()
    mean = 2 * n1 * n2 / n + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n ** 2 * (n - 1))
    z = (runs - mean) / np.sqrt(var)
    return runs, mean, z, 2 * (1 - stats.norm.cdf(abs(z)))


# =============================================================================
# LJUNG-BOX CLASIC SI ROBUST
# =============================================================================
def robust_ljung_box(r, m=10):
    """Ljung-Box Q(m) and Q~(m) with the robust variance tau_k = sum e_t^2 e_{t-k}^2 / (sum e_t^2)^2."""
    e = np.asarray(r, dtype=float) - np.mean(r)
    T = len(e)
    s2 = (e ** 2).sum()
    q_lb, q_rob = 0.0, 0.0
    for k in range(1, m + 1):
        rho = (e[k:] * e[:-k]).sum() / s2
        tau = (e[k:] ** 2 * e[:-k] ** 2).sum() / s2 ** 2
        q_lb += T * (T + 2) * rho ** 2 / (T - k)
        q_rob += rho ** 2 / tau
    return q_lb, 1 - stats.chi2.cdf(q_lb, m), q_rob, 1 - stats.chi2.cdf(q_rob, m)


# =============================================================================
# EXPONENTUL HURST
# =============================================================================
def _rs(x):
    y = np.cumsum(x - x.mean())
    s = x.std(ddof=0)
    return (y.max() - y.min()) / s if s > 0 else np.nan


def expected_rs(n):
    """E[R/S] for i.i.d. noise (Anis & Lloyd, 1976)."""
    if n <= 340:
        f = np.exp(gammaln((n - 1) / 2) - gammaln(n / 2)) / np.sqrt(np.pi)
    else:
        f = 1 / np.sqrt(n * np.pi / 2)
    i = np.arange(1, n)
    return f * np.sum(np.sqrt((n - i) / i))


def rs_hurst(r, min_n=10, n_sizes=20):
    """H from the slope of log(R/S) on log(n) (Hurst, 1951) and the Anis-Lloyd corrected H (slope of R/S - E[R/S], plus 0.5)."""
    x = np.asarray(r, dtype=float)
    T = len(x)
    sizes = np.unique(np.logspace(np.log10(min_n), np.log10(T // 4), n_sizes).astype(int))
    rs, ers = [], []
    for n in sizes:
        k = T // n
        vals = [_rs(x[i * n:(i + 1) * n]) for i in range(k)]
        rs.append(np.nanmean(vals))
        ers.append(expected_rs(n))
    ls, lrs, lers = np.log(sizes), np.log(rs), np.log(ers)
    h = np.polyfit(ls, lrs, 1)[0]
    h_al = 0.5 + np.polyfit(ls, lrs - lers, 1)[0]
    return h, h_al, pd.DataFrame({'n': sizes, 'rs': rs, 'expected_rs': ers})


def lo_modified_rs(r, q=None):
    """Lo's (1991) statistic V = Q_T / sqrt(T); under H0 (no long memory) V lies in [0.809, 1.862] with 95% probability."""
    x = np.asarray(r, dtype=float)
    T = len(x)
    e = x - x.mean()
    if q is None:                                   # Andrews (1991) bandwidth for an AR(1)
        rho = np.corrcoef(e[1:], e[:-1])[0, 1]
        q = int(np.floor((3 * T / 2) ** (1 / 3) * abs(2 * rho / (1 - rho ** 2)) ** (2 / 3)))
    s2 = (e ** 2).mean()
    for j in range(1, q + 1):
        w = 1 - j / (q + 1)
        s2 += 2 * w * (e[j:] * e[:-j]).sum() / T
    y = np.cumsum(e)
    Q = (y.max() - y.min()) / np.sqrt(s2)
    return Q / np.sqrt(T), q


def dfa_hurst(r, min_box=10, n_sizes=18, max_frac=0.25):
    """DFA-1 exponent: slope of log F(n) on log n for the cumulative profile of demeaned returns."""
    x = np.asarray(r, dtype=float)
    y = np.cumsum(x - x.mean())
    T = len(y)
    sizes = np.unique(np.logspace(np.log10(min_box), np.log10(int(T * max_frac)), n_sizes).astype(int))
    F = []
    for n in sizes:
        k = T // n
        seg = y[:k * n].reshape(k, n)
        t = np.arange(n)
        A = np.vstack([t, np.ones(n)]).T
        coef, *_ = np.linalg.lstsq(A, seg.T, rcond=None)
        resid = seg.T - A @ coef
        F.append(np.sqrt((resid ** 2).mean()))
    return np.polyfit(np.log(sizes), np.log(F), 1)[0], pd.DataFrame({'n': sizes, 'F': F})


# =============================================================================
# ROLLING
# =============================================================================
def rolling_stat(r, func, window=500, step=21):
    """Apply func on rolling windows of `window` observations, every `step` observations."""
    x = r.values
    idx, out = [], []
    for end in range(window, len(x) + 1, step):
        idx.append(r.index[end - 1])
        out.append(func(x[end - window:end]))
    return pd.Series(out, index=idx)

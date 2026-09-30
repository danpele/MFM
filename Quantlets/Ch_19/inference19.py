"""
inference19.py -- Master-level inference for the case study and the seminar of Chapter 19 (MFM)
==================================================================================================
  * hill / hill_ci              -- Hill tail index of losses, asymptotic CI and block-bootstrap CI
                                   (the sample kurtosis is not consistent when alpha < 4: Athreya, 1987)
  * garch_t_nll / profile_pers  -- profile-likelihood CI for the persistence alpha + beta of GARCH(1,1)-t,
                                   restricted to the stationary region (Andrews, 1999)
  * dq_test                     -- Dynamic Quantile test (Engle & Manganelli, 2004)
  * fz0 / dm_test / mcs         -- FZ0 score for (VaR, ES) (Patton, Ziegel & Chen, 2019), Diebold-Mariano tests
                                   with HAC errors, model confidence set (Hansen, Lunde & Nason, 2011)
  * comparative_backtest        -- comparative ES backtest with three zones (Nolde & Ziegel, 2017)
  * kupiec_power / kupiec_mde   -- exact (binomial) power of the Kupiec test and the minimum detectable effect
  * sup_wald_break              -- break at an unknown date (Andrews, 1993), p-values by simulating the limit

Convention: loss L = -r (in %); VaR and ES positive; alpha = tail probability.
Modelling Financial Markets - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize
import statsmodels.api as sm


# =============================================================================
# 1. HILL TAIL INDEX
# =============================================================================
def hill(losses, k):
    """Hill estimator of the tail index from the k largest (positive) losses."""
    x = np.sort(np.asarray(losses)[np.asarray(losses) > 0])[::-1]
    return 1.0 / np.mean(np.log(x[:k]) - np.log(x[k]))


def hill_k(r, share=0.05):
    """k = 5% of the loss days (the same rule as in Chapter 16)."""
    return int(round(share * np.sum(-np.asarray(r) > 0)))


def hill_ci(r, share=0.05, B=999, block=20, seed=0):
    """Hill on losses, asymptotic i.i.d. CI alpha(1 +/- 1.96/sqrt(k)) and moving-block bootstrap CI."""
    L = -np.asarray(r)
    k = hill_k(r, share)
    a = hill(L, k)
    rng = np.random.default_rng(seed)
    T = len(L)
    nb = int(np.ceil(T / block))
    bs = np.array([hill(L[(rng.integers(0, T - block + 1, nb)[:, None] + np.arange(block)).ravel()[:T]], k)
                   for _ in range(B)])
    return dict(alpha=a, k=k, se_iid=a / np.sqrt(k), lo_iid=a - 1.96 * a / np.sqrt(k), hi_iid=a + 1.96 * a / np.sqrt(k),
                lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5), se_boot=bs.std(ddof=1), draws=bs)


# =============================================================================
# 2. GARCH(1,1)-t: PROFILE-LIKELIHOOD CI FOR PERSISTENCE
# =============================================================================
def garch_t_nll(theta, r):
    """-log L for GARCH(1,1) with standardised Student-t innovations; theta = (mu, omega, alpha, beta, nu)."""
    mu, om, a, b, nu = theta
    if om <= 0 or a < 0 or b < 0 or a + b > 1 or nu <= 2.05:        # a + b = 1 (IGARCH) is allowed
        return 1e10
    e = r - mu
    T = len(e)
    s2 = np.empty(T)
    s2[0] = np.var(e)
    for t in range(1, T):
        s2[t] = om + a * e[t - 1] ** 2 + b * s2[t - 1]
    c = (stats.t.logpdf(e / np.sqrt(s2 * (nu - 2) / nu), nu) - 0.5 * np.log(s2 * (nu - 2) / nu))
    return -np.sum(c)


def profile_pers(r, grid, x0):
    """Maximum likelihood with the persistence fixed at p = alpha + beta (reparametrised alpha = p*s, beta = p*(1-s))."""
    r = np.asarray(r)
    out = []
    for p in grid:
        def f(th):
            mu, om, s, nu = th
            if not 0 < s < 1:
                return 1e10
            return garch_t_nll((mu, om, p * s, p * (1 - s), nu), r)
        best = optimize.minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-6, 'fatol': 1e-3, 'maxiter': 4000})
        out.append(-best.fun)
        x0 = best.x
    return np.array(out)


def profile_ci(r, res):
    """95% profile-likelihood CI for p = alpha + beta, on the grid 0.960-0.9999 and at p = 1 (IGARCH).
    Interior points p < 1: 2(l_max - l(p)) <= 3.84 (chi2(1)); p = 1 is on the boundary of the space p <= 1, where
    the LR statistic has the distribution 0.5 chi2(0) + 0.5 chi2(1) (Andrews, 1999): p = 1 is included if LR <= 2.71."""
    p = res.params
    pers = p['alpha[1]'] + p['beta[1]']
    lmax = -garch_t_nll((p['mu'], p['omega'], p['alpha[1]'], p['beta[1]'], p['nu']), np.asarray(r))
    x0 = np.array([p['mu'], p['omega'], p['alpha[1]'] / pers, p['nu']])
    grid = np.unique(np.concatenate([np.linspace(0.960, 0.998, 39), [0.999, 0.9995, 0.9999, 1.0, pers]]))
    lp = profile_pers(r, grid, x0)
    lr = 2 * (max(lmax, lp.max()) - lp)
    crit = np.where(grid < 1, stats.chi2.ppf(0.95, 1), stats.chi2.ppf(0.90, 1))
    ok = grid[lr <= crit]
    lr1 = float(lr[grid == 1.0][0])
    return dict(pers=pers, lmax=lmax, lo=ok.min(), hi=ok.max(), grid=list(grid), lr=list(lr),
                hl_lo=np.log(0.5) / np.log(ok.min()), hl_hi=(np.inf if ok.max() >= 1 else np.log(0.5) / np.log(ok.max())),
                lr_one=lr1, p_one=float(0.5 * stats.chi2.sf(lr1, 1)), cv_one=float(stats.chi2.ppf(0.90, 1)),
                hi_at_edge=bool(ok.max() >= 1.0))


# =============================================================================
# 3. TESTS FOR RISK FORECASTS
# =============================================================================
def dq_test(L, var, a=0.01, lags=4):
    """Dynamic Quantile (Engle & Manganelli, 2004): Hit_t - a on a constant, lagged breaches and VaR_t; DQ ~ chi2(lags+2)."""
    hit = (np.asarray(L) > np.asarray(var)).astype(float) - a
    X = [np.ones(len(hit))] + [np.roll(hit, l) for l in range(1, lags + 1)] + [np.asarray(var)]
    X = np.column_stack(X)[lags:]
    y = hit[lags:]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    dq = b @ X.T @ X @ b / (a * (1 - a))
    return dict(DQ=dq, df=X.shape[1], p=stats.chi2.sf(dq, X.shape[1]))


def fz0(r, var, es, a):
    """FZ0 score (Patton, Ziegel & Chen, 2019) for v = -VaR, e = -ES (negative quantiles), return r."""
    v, e, y = -np.asarray(var), -np.asarray(es), np.asarray(r)
    return -((y <= v) * (v - y)) / (a * e) + v / e + np.log(-e) - 1


def nw_var(d, lags=None):
    d = np.asarray(d) - np.mean(d)
    T = len(d)
    lags = int(np.floor(4 * (T / 100) ** (2 / 9))) if lags is None else lags
    v = d @ d / T
    for l in range(1, lags + 1):
        v += 2 * (1 - l / (lags + 1)) * (d[l:] @ d[:-l]) / T
    return v, lags


def dm_test(l1, l2):
    """Diebold-Mariano: d = l1 - l2; t = mean(d)/sqrt(HAC var/T); d < 0 => model 1 is better."""
    d = np.asarray(l1) - np.asarray(l2)
    v, lags = nw_var(d)
    t = d.mean() / np.sqrt(v / len(d))
    return dict(mean=d.mean(), t=t, p=2 * stats.norm.sf(abs(t)), lags=lags)


def mcs(losses, B=999, block=20, alpha=0.10, seed=0):
    """Model confidence set (Hansen, Lunde & Nason, 2011), T_max statistic, moving-block bootstrap.
    losses: DataFrame T x m. Returns the MCS p-value of each model."""
    rng = np.random.default_rng(seed)
    L = losses.values
    T, m = L.shape
    nb = int(np.ceil(T / block))
    idx = [(rng.integers(0, T - block + 1, nb)[:, None] + np.arange(block)).ravel()[:T] for _ in range(B)]
    alive = list(range(m))
    pvals = {}
    pmax = 0.0
    while len(alive) > 1:
        Lm = L[:, alive]
        dbar = Lm.mean(0) - Lm.mean()                       # d_i. = L_i - mean of the remaining models
        boot = np.array([Lm[ix].mean(0) - Lm[ix].mean() for ix in idx])
        se = np.sqrt(((boot - dbar) ** 2).mean(0))
        t = dbar / se
        tmax = t.max()
        tb = ((boot - dbar) / se).max(1)
        p = float((tb >= tmax).mean())
        pmax = max(pmax, p)
        worst = alive[int(np.argmax(t))]
        pvals[losses.columns[worst]] = pmax
        alive.remove(worst)
    pvals[losses.columns[alive[0]]] = 1.0
    return {k: pvals[k] for k in losses.columns}, [c for c in losses.columns if pvals[c] >= alpha]


def comparative_backtest(s_int, s_std, level=0.05):
    """Comparative backtest (Nolde & Ziegel, 2017) with FZ0 scores: d = S(internal) - S(standard).
    Red: H0- rejected, 'internal at least as good' (d > 0 significant);
    green: H0+ rejected, 'internal at most as good' (d < 0 significant); otherwise yellow."""
    t = dm_test(s_int, s_std)['t']
    z = stats.norm.ppf(1 - level)
    zone = 'red' if t > z else ('green' if t < -z else 'yellow')
    return dict(t=t, zone=zone)


def holm(p):
    """Holm-adjusted p-values (FWER)."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    m = len(p)
    adj = np.minimum(np.maximum.accumulate((m - np.arange(m)) * p[o]), 1)
    out = np.empty(m)
    out[o] = adj
    return out


def bh(p, q=0.05):
    """Benjamini-Hochberg: mask of rejections at FDR q."""
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    ok = p[o] <= q * np.arange(1, m + 1) / m
    k = np.max(np.nonzero(ok)[0]) + 1 if ok.any() else 0
    rej = np.zeros(m, bool)
    rej[o[:k]] = True
    return rej


# =============================================================================
# 4. POWER OF THE KUPIEC TEST
# =============================================================================
def kupiec_region(T, p0=0.01, level=0.05):
    """Breach counts x for which LR_uc rejects at the given level."""
    xs = np.arange(0, T + 1)
    ph = xs / T
    with np.errstate(divide='ignore', invalid='ignore'):
        ll1 = np.where(xs > 0, xs * np.log(np.where(ph > 0, ph, 1)), 0) + \
            np.where(xs < T, (T - xs) * np.log(np.where(ph < 1, 1 - ph, 1)), 0)
    ll0 = xs * np.log(p0) + (T - xs) * np.log(1 - p0)
    lr = -2 * (ll0 - ll1)
    return xs[lr > stats.chi2.ppf(1 - level, 1)]


def kupiec_power(T, p1, p0=0.01, level=0.05):
    rej = kupiec_region(T, p0, level)
    return float(stats.binom.pmf(rej, T, p1).sum()), rej


def kupiec_mde(T, p0=0.01, power=0.80, level=0.05):
    """Smallest true rate > p0 detected with the required power."""
    for p1 in np.arange(p0 + 0.0005, 0.2, 0.0005):
        if kupiec_power(T, p1, p0, level)[0] >= power:
            return float(p1)
    return np.nan


# =============================================================================
# 5. BREAK AT AN UNKNOWN DATE
# =============================================================================
def sup_wald_break(y, trim=0.15, nsim=2000, seed=0, hac=True):
    """sup-Wald test (Andrews, 1993) for a break in the mean of y at an unknown date, HAC errors;
    p-value by simulating the limit sup_pi B(pi)^2/(pi(1-pi)) (Brownian bridge)."""
    y = np.asarray(y, float)
    T = len(y)
    lo, hi = int(np.floor(trim * T)), int(np.ceil((1 - trim) * T))
    best = (-np.inf, None)
    v, _ = nw_var(y - y.mean()) if hac else (np.var(y), 0)
    cs = np.cumsum(y)
    ybar = y.mean()
    for k in range(lo, hi):
        m1, m2 = cs[k - 1] / k, (cs[-1] - cs[k - 1]) / (T - k)
        w = (m2 - m1) ** 2 / (v * (1 / k + 1 / (T - k)))
        if w > best[0]:
            best = (w, k)
    rng = np.random.default_rng(seed)
    n = 2000
    grid = np.arange(int(trim * n), int((1 - trim) * n))
    sims = []
    for _ in range(nsim):
        W = np.cumsum(rng.standard_normal(n)) / np.sqrt(n)
        pi = grid / n
        Bb = W[grid - 1] - pi * W[-1]
        sims.append(np.max(Bb ** 2 / (pi * (1 - pi))))
    sims = np.array(sims)
    return dict(stat=best[0], k=best[1], p=float((sims >= best[0]).mean()), cv5=float(np.percentile(sims, 95)))


# =============================================================================
# 6. FORMAL EVALUATION OF THE FOUR MODELS (case study)
# =============================================================================
def formal_eval(fc, models=('HS', 'Normal', 'GARCH-t', 'FHS'), a=0.01, a_es=0.025, standard='HS'):
    """DQ at VaR 1%; FZ0 at level 2.5% for the pair (VaR 2.5%, ES 2.5%); pairwise DM; MCS; comparative backtest."""
    out = {'dq': {}, 'fz0': {}, 'dm': {}, 'cb': {}}
    S = {}
    for m in models:
        out['dq'][m] = dq_test(fc['L'], fc[m], a)
        S[m] = fz0(fc['r'], fc[m + '_V25'], fc[m + '_ES'], a_es)
        out['fz0'][m] = float(np.mean(S[m]))
    for i, m1 in enumerate(models):
        for m2 in models[i + 1:]:
            out['dm'][f'{m1}|{m2}'] = dm_test(S[m1], S[m2])
    p, keep = mcs(pd.DataFrame(S))
    out['mcs_p'], out['mcs_set'] = p, keep
    for m in models:
        if m != standard:
            out['cb'][m] = comparative_backtest(S[m], S[standard])
    out['T'] = len(fc)
    return out

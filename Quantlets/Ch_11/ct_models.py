"""
ct_models.py -- Continuous-time models for Chapter 11 (MFM): simulation and estimation
======================================================================================
  * Brownian motion: scaled random walk (Donsker), paths, quadratic variation, the Ito integral
  * discretisation schemes: Euler-Maruyama, Milstein; strong and weak convergence
  * geometric Brownian motion (GBM): exact solution, maximum likelihood estimation
  * Ornstein-Uhlenbeck / Vasicek: exact AR(1) discretisation, estimation, half-life
  * Merton (jump-diffusion): density as a Poisson mixture, maximum likelihood, simulation
  * nonlinear diffusions: exact CIR likelihood, Euler pseudo-likelihood, CKLS, nonparametric drift and diffusion
  * the Lee-Mykland jump test
  * Heston (stochastic volatility): full-truncation simulation, parameters from the VIX, the volatility smile
  * stylised facts: kurtosis, the Hill tail index, autocorrelation of |r|

Convention: time in years; daily log returns (not in %) in the estimation functions.
Modelling Financial Markets - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize


# =============================================================================
# BROWNIAN MOTION
# =============================================================================
def scaled_random_walk(n, n_paths, rng):
    """Scaled random walk W_n(t) = S_[nt] / sqrt(n), with equally likely +1/-1 steps, on the grid t = k/n."""
    steps = rng.choice([-1.0, 1.0], size=(n_paths, n))
    S = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(steps, axis=1)], axis=1)
    return np.linspace(0, 1, n + 1), S / np.sqrt(n)


def bm_paths(n_paths, n_steps, T, rng):
    """Standard Brownian motion paths on [0, T]: W_0 = 0, independent N(0, dt) increments."""
    dt = T / n_steps
    dW = rng.standard_normal((n_paths, n_steps)) * np.sqrt(dt)
    W = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1)
    return np.linspace(0, T, n_steps + 1), W


def quadratic_variation(W):
    """Sum of squared increments (quadratic variation on the given grid)."""
    return np.sum(np.diff(W, axis=-1) ** 2, axis=-1)


def total_variation(W):
    """Sum of absolute increments (total variation on the given grid)."""
    return np.sum(np.abs(np.diff(W, axis=-1)), axis=-1)


def ito_stratonovich(W):
    """Ito (left endpoint) and Stratonovich (midpoint) sums for the integral of W with respect to W."""
    dW = np.diff(W, axis=-1)
    ito = np.sum(W[..., :-1] * dW, axis=-1)
    strat = np.sum(0.5 * (W[..., :-1] + W[..., 1:]) * dW, axis=-1)
    return ito, strat


def max_prob(W, level=1.0):
    """Share of paths whose maximum on [0, T] exceeds the given level."""
    return float(np.mean(W.max(axis=1) > level))


# =============================================================================
# DISCRETISATION SCHEMES (Higham's test equation: dX = lam X dt + mu X dW)
# =============================================================================
def em_milstein_gbm(x0, lam, mu, dW, dt):
    """Euler-Maruyama and Milstein for dX = lam X dt + mu X dW, with Brownian increments dW (n_paths x n)."""
    xe = np.full(dW.shape[0], x0, dtype=float)
    xm = xe.copy()
    for k in range(dW.shape[1]):
        d = dW[:, k]
        xe = xe + lam * xe * dt + mu * xe * d
        xm = xm + lam * xm * dt + mu * xm * d + 0.5 * mu ** 2 * xm * (d ** 2 - dt)
    return xe, xm


def convergence_study(rng, x0=1.0, lam=2.0, mu=1.0, T=1.0, n_fine=2 ** 11, n_paths=20000,
                      ratios=(1, 2, 4, 8, 16, 32, 64), return_paths=False):
    """Strong error E|X_T - X^h_T| and weak error |E X^h_T - E X_T| for steps dt = ratio * T / n_fine.
    With return_paths=True it also returns the path x step matrices (absolute EM and Milstein errors, EM X^h_T),
    used for the whole-path bootstrap (the same paths at every step size)."""
    dt_f = T / n_fine
    dW = rng.standard_normal((n_paths, n_fine)) * np.sqrt(dt_f)
    WT = dW.sum(axis=1)
    x_true = x0 * np.exp((lam - 0.5 * mu ** 2) * T + mu * WT)
    ex = x0 * np.exp(lam * T)                       # E X_T exact
    rows, ae, am, xs = [], [], [], []
    for r in ratios:
        dWr = dW.reshape(n_paths, n_fine // r, r).sum(axis=2)
        h = r * dt_f
        xe, xm = em_milstein_gbm(x0, lam, mu, dWr, h)
        ae.append(np.abs(x_true - xe))
        am.append(np.abs(x_true - xm))
        xs.append(xe)
        rows.append(dict(dt=h, strong_em=np.mean(np.abs(x_true - xe)), strong_mil=np.mean(np.abs(x_true - xm)),
                         strong_em_se=np.std(np.abs(x_true - xe)) / np.sqrt(n_paths),
                         strong_mil_se=np.std(np.abs(x_true - xm)) / np.sqrt(n_paths),
                         weak_em_exact=abs(x0 * (1 + lam * h) ** round(T / h) - ex),
                         weak_em_mc=abs(xe.mean() - ex), weak_mil_mc=abs(xm.mean() - ex)))
    d = pd.DataFrame(rows)
    if return_paths:
        return d, dict(abs_em=np.column_stack(ae), abs_mil=np.column_stack(am), x_em=np.column_stack(xs), ex=ex)
    return d


def slope_boot(dt, M, rng, n_boot=1000, level=0.95, target=None):
    """Log-log slope with a whole-path bootstrap interval: the rows of M (path x step) are resampled,
    keeping all resolutions together; the error at each step is the column mean
    (target=None, strong error) or |column mean - target| (Monte Carlo weak error)."""
    x = np.log(np.asarray(dt))
    f = (lambda A: A.mean(axis=0)) if target is None else (lambda A: np.abs(A.mean(axis=0) - target))
    slope = np.polyfit(x, np.log(f(M)), 1)[0]
    n = M.shape[0]
    b = np.empty(n_boot)
    for i in range(n_boot):
        b[i] = np.polyfit(x, np.log(np.maximum(f(M[rng.integers(0, n, n)]), 1e-300)), 1)[0]
    q = np.quantile(b, [(1 - level) / 2, (1 + level) / 2])
    return dict(slope=float(slope), se=float(b.std()), lo=float(q[0]), hi=float(q[1]))


def slope_ci(dt, err, level=0.95):
    """Slope of the regression of log(error) on log(dt), with standard error and t confidence interval."""
    x, y = np.log(np.asarray(dt)), np.log(np.asarray(err))
    res = stats.linregress(x, y)
    q = stats.t.ppf(0.5 + level / 2, len(x) - 2)
    return dict(slope=res.slope, se=res.stderr, lo=res.slope - q * res.stderr, hi=res.slope + q * res.stderr,
                intercept=res.intercept)


# =============================================================================
# GEOMETRIC BROWNIAN MOTION (GBM)
# =============================================================================
def gbm_paths(S0, mu, sigma, T, n_steps, n_paths, rng):
    """Exact solution S_t = S_0 exp((mu - sigma^2/2) t + sigma W_t) on a regular grid."""
    t, W = bm_paths(n_paths, n_steps, T, rng)
    return t, S0 * np.exp((mu - 0.5 * sigma ** 2) * t + sigma * W)


def gbm_mle(r, dt):
    """Maximum likelihood for GBM from log returns r (same frequency dt, in years).

    r_t ~ N((mu - sigma^2/2) dt, sigma^2 dt), i.i.d.  =>  sigma^2 = var(r)/dt,  mu = mean(r)/dt + sigma^2/2.
    Standard errors: se(sigma) = sigma / sqrt(2n); se(log drift) = sigma / sqrt(n dt) (depends only on the span)."""
    r = np.asarray(r)
    n = len(r)
    s2 = r.var() / dt
    sigma = np.sqrt(s2)
    m = r.mean() / dt                       # log drift (mu - sigma^2/2)
    return dict(n=n, years=n * dt, sigma=sigma, se_sigma=sigma / np.sqrt(2 * n), m=m, se_m=sigma / np.sqrt(n * dt),
                mu=m + 0.5 * s2)


def gbm_simulate_returns(m, sigma, n, dt, rng):
    """I.i.d. Normal log returns of a GBM (log drift m, volatility sigma)."""
    return m * dt + sigma * np.sqrt(dt) * rng.standard_normal(n)


# =============================================================================
# ORNSTEIN-UHLENBECK / VASICEK
# =============================================================================
def ou_exact_path(x0, kappa, theta, sigma, dt, n, rng, z=None):
    """Exact discretisation: x_{t+dt} = theta + (x_t - theta) e^{-kappa dt} + eps, eps ~ N(0, sigma^2 (1 - e^{-2 kappa dt}) / (2 kappa))."""
    b = np.exp(-kappa * dt)
    sd = sigma * np.sqrt((1 - b ** 2) / (2 * kappa))
    z = rng.standard_normal(n) if z is None else z
    x = np.empty(n + 1)
    x[0] = x0
    for k in range(n):
        x[k + 1] = theta + (x[k] - theta) * b + sd * z[k]
    return x


def ou_mle(x, dt):
    """Maximum likelihood estimator (conditional on x_0) of the OU process: the exact AR(1) regression.

    x_{t+1} = a + b x_t + e;  kappa = -ln b / dt;  theta = a / (1 - b);  sigma = s_e sqrt(2 kappa / (1 - b^2)).
    Standard errors of kappa, theta and the half-life: delta method from the OLS covariance of (a, b)."""
    x = np.asarray(x, dtype=float)
    y, z = x[1:], x[:-1]
    X = np.column_stack([np.ones_like(z), z])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b = coef
    e = y - X @ coef
    n = len(y)
    s2 = e @ e / n
    cov = s2 * np.linalg.inv(X.T @ X)
    kappa = -np.log(b) / dt
    theta = a / (1 - b)
    sigma = np.sqrt(s2 * 2 * kappa / (1 - b ** 2))
    g_k = np.array([0.0, -1 / (b * dt)])                       # d kappa / d(a, b)
    g_t = np.array([1 / (1 - b), a / (1 - b) ** 2])           # d theta / d(a, b)
    se_k = float(np.sqrt(g_k @ cov @ g_k))
    se_t = float(np.sqrt(g_t @ cov @ g_t))
    hl = np.log(2) / kappa
    return dict(n=n, a=a, b=b, kappa=kappa, se_kappa=se_k, theta=theta, se_theta=se_t, sigma=sigma,
                half_life=hl, se_half_life=hl / kappa * se_k, stat_sd=sigma / np.sqrt(2 * kappa))


def ou_bias_mc(kappa, theta, sigma, dt, n, n_sim, rng):
    """Sampling distribution of the estimated kappa: n_sim exact OU paths (started from the stationary distribution)."""
    from scipy.signal import lfilter
    b = np.exp(-kappa * dt)
    sd = sigma * np.sqrt((1 - b ** 2) / (2 * kappa))
    out = np.empty(n_sim)
    for i in range(n_sim):
        e = sd * rng.standard_normal(n)
        e[0] = sigma / np.sqrt(2 * kappa) * rng.standard_normal()
        x = theta + lfilter([1.0], [1.0, -b], e)
        out[i] = ou_mle(x, dt)['kappa']
    return out


# =============================================================================
# NONLINEAR DIFFUSIONS: EXACT (CIR) VS EULER LIKELIHOOD; CKLS; NONPARAMETRIC ESTIMATION
# =============================================================================
def vasicek_loglik(x, dt, kappa, theta, sigma, per_obs=False):
    """Exact Vasicek log-likelihood (Normal transition, exact AR(1))."""
    r0, r1 = x[:-1], x[1:]
    b = np.exp(-kappa * dt)
    ll = stats.norm.logpdf(r1, theta + (r0 - theta) * b, sigma * np.sqrt((1 - b * b) / (2 * kappa)))
    return ll if per_obs else ll.sum()


def cir_loglik(x, dt, kappa, theta, sigma, per_obs=False):
    """Exact CIR log-likelihood: 2c r_{t+dt} | r_t ~ noncentral chi-square with 4 kappa theta / sigma^2 degrees of freedom
    and noncentrality 2c r_t e^{-kappa dt}, c = 2 kappa / (sigma^2 (1 - e^{-kappa dt})) (Cox, Ingersoll, Ross 1985)."""
    r0, r1 = x[:-1], x[1:]
    c = 2 * kappa / (sigma ** 2 * (1 - np.exp(-kappa * dt)))
    ll = np.log(2 * c) + stats.ncx2.logpdf(2 * c * r1, 4 * kappa * theta / sigma ** 2, 2 * c * r0 * np.exp(-kappa * dt))
    return ll if per_obs else ll.sum()


def euler_loglik(x, dt, kappa, theta, sigma, gamma, per_obs=False):
    """Euler (Gaussian) pseudo-likelihood for dr = kappa (theta - r) dt + sigma r^gamma dW
    (gamma = 0: Vasicek, gamma = 1/2: CIR, free gamma: Chan, Karolyi, Longstaff, Sanders 1992)."""
    r0, r1 = x[:-1], x[1:]
    ll = stats.norm.logpdf(r1, r0 + kappa * (theta - r0) * dt, sigma * r0 ** gamma * np.sqrt(dt))
    return ll if per_obs else ll.sum()


def _fit(nll, p0):
    best = None
    for scale in (1.0, 0.5, 2.0):
        q0 = np.array(p0, dtype=float)
        q0[0] *= scale
        res = optimize.minimize(nll, q0, method='Nelder-Mead', options=dict(maxiter=40000, maxfev=40000, xatol=1e-10, fatol=1e-8))
        res = optimize.minimize(nll, res.x, method='Nelder-Mead', options=dict(maxiter=40000, maxfev=40000, xatol=1e-10, fatol=1e-8))
        if best is None or res.fun < best.fun:
            best = res
    return best


def short_rate_fits(x, dt):
    """Vasicek (exact and Euler), CIR (exact and Euler) and CKLS (Euler) on the same series; Hessian standard errors
    (for CKLS also robust sandwich errors, since the Gaussian Euler likelihood is only a quasi-likelihood)."""
    x = np.asarray(x, dtype=float)
    specs = {
        'vasicek_exact': (lambda p: vasicek_loglik(x, dt, p[0], p[1], p[2]), lambda q: (q[0], q[1], np.exp(q[2])), 0.0),
        'vasicek_euler': (lambda p: euler_loglik(x, dt, p[0], p[1], p[2], 0.0), lambda q: (q[0], q[1], np.exp(q[2])), 0.0),
        'cir_euler': (lambda p: euler_loglik(x, dt, p[0], p[1], p[2], 0.5), lambda q: (q[0], q[1], np.exp(q[2])), 0.5),
        'cir_exact': (lambda p: cir_loglik(x, dt, p[0], p[1], p[2]), lambda q: (q[0], q[1], np.exp(q[2])), 0.5),
    }
    out = {}
    m = x.mean()
    for name, (ll, unpack, g) in specs.items():
        s0 = 0.015 if g == 0 else 0.015 / np.sqrt(m)

        def nll(q, ll=ll, unpack=unpack):
            k, th, sg = unpack(q)
            if k <= 0 or th <= 0:
                return 1e18
            v = -ll((k, th, sg))
            return v if np.isfinite(v) else 1e18
        res = _fit(nll, [0.2, m, np.log(s0)])
        th = np.array(unpack(res.x))
        H = numerical_hessian(lambda t, ll=ll: -ll(t), th)
        se = np.sqrt(np.maximum(np.diag(np.linalg.inv(H)), 0))
        out[name] = dict(kappa=th[0], theta=th[1], sigma=th[2], gamma=g, se_kappa=se[0], se_theta=se[1], se_sigma=se[2],
                         loglik=-res.fun)
    # CKLS: free gamma
    best = None
    for g0 in (0.5, 1.0, 1.5):
        def nll(q):
            if q[0] <= 0 or q[1] <= 0:
                return 1e18
            v = -euler_loglik(x, dt, q[0], q[1], np.exp(q[2]), q[3])
            return v if np.isfinite(v) else 1e18
        res = _fit(nll, [0.2, m, np.log(0.015 * m ** (-g0)), g0])
        if best is None or res.fun < best.fun:
            best = res
    th = np.array([best.x[0], best.x[1], np.exp(best.x[2]), best.x[3]])
    f = lambda t: euler_loglik(x, dt, *t)
    H = -numerical_hessian(f, th)
    Hi = np.linalg.inv(H)
    h = 1e-5 * np.maximum(np.abs(th), 1e-2)
    sc = np.column_stack([(euler_loglik(x, dt, *(th + e), per_obs=True) - euler_loglik(x, dt, *(th - e), per_obs=True)) / (2 * hi)
                          for e, hi in zip(np.diag(h), h)])
    V = Hi @ (sc.T @ sc) @ Hi
    Vh = Hi @ hac_cov(sc) @ Hi
    out['ckls'] = dict(kappa=th[0], theta=th[1], sigma=th[2], gamma=th[3], se_gamma=float(np.sqrt(Hi[3, 3])),
                       se_gamma_rob=float(np.sqrt(V[3, 3])), se_gamma_hac=float(np.sqrt(Vh[3, 3])),
                       hac_lags=nw_lags(len(sc)), se_kappa=float(np.sqrt(Hi[0, 0])), loglik=-best.fun)
    c = out['ckls']
    c['lr_g0'] = 2 * (c['loglik'] - out['vasicek_euler']['loglik'])
    c['lr_g05'] = 2 * (c['loglik'] - out['cir_euler']['loglik'])
    c['wald_g0'] = (c['gamma'] / c['se_gamma_rob']) ** 2
    c['wald_g05'] = ((c['gamma'] - 0.5) / c['se_gamma_rob']) ** 2
    c['wald_g0_hac'] = (c['gamma'] / c['se_gamma_hac']) ** 2
    c['wald_g05_hac'] = ((c['gamma'] - 0.5) / c['se_gamma_hac']) ** 2
    L0 = nw_lags(len(sc))                   # sensitivity: five times as many lags
    se5 = float(np.sqrt((Hi @ hac_cov(sc, 5 * L0) @ Hi)[3, 3]))
    c.update(hac_lags5=5 * L0, se_gamma_hac5=se5, wald_g0_hac5=(c['gamma'] / se5) ** 2,
             wald_g05_hac5=((c['gamma'] - 0.5) / se5) ** 2)
    out['n'] = len(x) - 1
    return out


def nw_lags(n):
    """Newey-West number of lags: floor(4 (n / 100)^(2/9))."""
    return int(np.floor(4 * (n / 100) ** (2 / 9)))


def hac_cov(sc, L=None):
    """Long-run covariance of the scores (Newey and West, 1987): Bartlett kernel with L lags; accounts for
    autocorrelation of the scores (for example, from persistent volatility omitted from the model)."""
    sc = np.asarray(sc) - np.asarray(sc).mean(axis=0)
    L = nw_lags(len(sc)) if L is None else L
    S = sc.T @ sc
    for j in range(1, L + 1):
        G = sc[j:].T @ sc[:-j]
        S += (1 - j / (L + 1)) * (G + G.T)
    return S


def nw_drift_diffusion(x, dt, grid, h=None):
    """Nadaraya-Watson estimators (Gaussian kernel) of the drift a(r) = E[dr | r] / dt and the diffusion
    b^2(r) = E[(dr)^2 | r] / dt (Stanton 1997; Bandi and Phillips 2003); pointwise heteroskedasticity-robust standard errors
    (serial dependence of the errors is ignored)."""
    x = np.asarray(x, dtype=float)
    r0, d = x[:-1], np.diff(x)
    if h is None:
        h = 1.06 * r0.std() * len(r0) ** (-0.2)
    out = {'grid': np.asarray(grid), 'h': h}
    for name, y in [('drift', d / dt), ('diff2', d ** 2 / dt)]:
        m, se = [], []
        for g in grid:
            w = np.exp(-0.5 * ((r0 - g) / h) ** 2)
            w /= w.sum()
            mm = w @ y
            m.append(mm)
            se.append(np.sqrt((w ** 2) @ (y - mm) ** 2))
        out[name], out[name + '_se'] = np.array(m), np.array(se)
    return out


# =============================================================================
# MERTON: JUMP-DIFFUSION
# =============================================================================
def merton_logpdf(r, dt, m, sigma, lam, mu_j, s_j, kmax=12):
    """Log-density of log returns over a step dt:  r = m dt + sigma W_dt + the sum of N jumps N(mu_j, s_j^2),
    N ~ Poisson(lam dt). The density is a mixture of Normal distributions weighted by the Poisson probabilities."""
    r = np.asarray(r)[:, None]
    k = np.arange(kmax + 1)[None, :]
    w = stats.poisson.pmf(k, lam * dt)
    mean = m * dt + k * mu_j
    var = sigma ** 2 * dt + k * s_j ** 2
    dens = (w * np.exp(-0.5 * (r - mean) ** 2 / var) / np.sqrt(2 * np.pi * var)).sum(axis=1)
    return np.log(np.maximum(dens, 1e-300))


def _merton_unpack(p, sigma_min=0.0):
    return p[0], sigma_min + np.exp(p[1]), np.exp(p[2]), p[3], np.exp(p[4])


def merton_mle(r, dt, starts=None, sigma_min=0.0):
    """Maximum likelihood for Merton (m, sigma, lam, mu_j, s_j); several starting points.
    sigma_min > 0 restricts the parameter space to sigma >= sigma_min (sigma = sigma_min + e^q): the unrestricted
    likelihood is unbounded (sigma -> 0 with m dt equal to an observed return), the restricted one is bounded.
    Standard errors: inverse of the numerical Hessian in the original parameters (delta method)."""
    r = np.asarray(r)
    sd = r.std()
    unpack = lambda p: _merton_unpack(p, sigma_min)
    nll = lambda p: -merton_logpdf(r, dt, *unpack(p)).sum()
    if starts is None:
        starts = []
        s0 = np.log(max(0.7 * sd / np.sqrt(dt) - sigma_min, 1e-3))
        for lam0 in (2.0, 10.0, 40.0):
            for sj0 in (1.5, 3.0):
                starts.append([r.mean() / dt, s0, np.log(lam0), -0.5 * sd, np.log(sj0 * sd)])
    best = None
    for s0 in starts:
        res = optimize.minimize(nll, s0, method='Nelder-Mead', options=dict(maxiter=20000, maxfev=20000, xatol=1e-7, fatol=1e-7))
        res = optimize.minimize(nll, res.x, method='BFGS')
        if best is None or res.fun < best.fun:
            best = res
    m, sigma, lam, mu_j, s_j = unpack(best.x)
    theta = np.array([m, sigma, lam, mu_j, s_j])
    nll_orig = lambda th: -merton_logpdf(r, dt, *th).sum()
    H = numerical_hessian(nll_orig, theta)
    try:
        cov = np.linalg.inv(H)
        se = np.sqrt(np.maximum(np.diag(cov), 0))
    except np.linalg.LinAlgError:
        se = np.full(5, np.nan)
    return dict(m=m, sigma=sigma, lam=lam, mu_j=mu_j, s_j=s_j, se=dict(zip(['m', 'sigma', 'lam', 'mu_j', 's_j'], se)),
                loglik=-best.fun, n=len(r))


def numerical_hessian(f, x, rel=1e-4):
    """Hessian by central finite differences."""
    x = np.asarray(x, dtype=float)
    k = len(x)
    h = rel * np.maximum(np.abs(x), 1e-3)
    H = np.empty((k, k))
    for i in range(k):
        for j in range(i, k):
            ei, ej = np.zeros(k), np.zeros(k)
            ei[i], ej[j] = h[i], h[j]
            H[i, j] = H[j, i] = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * h[i] * h[j])
    return H


def merton_moments(dt, sigma, lam, mu_j, s_j, m=0.0):
    """Mean, variance, skewness and excess kurtosis of the Merton return over a step dt (cumulants)."""
    k1 = m * dt + lam * dt * mu_j
    k2 = sigma ** 2 * dt + lam * dt * (mu_j ** 2 + s_j ** 2)
    k3 = lam * dt * (mu_j ** 3 + 3 * mu_j * s_j ** 2)
    k4 = lam * dt * (mu_j ** 4 + 6 * mu_j ** 2 * s_j ** 2 + 3 * s_j ** 4)
    return dict(mean=k1, var=k2, skew=k3 / k2 ** 1.5, exkurt=k4 / k2 ** 2)


def merton_simulate_returns(m, sigma, lam, mu_j, s_j, n, dt, rng):
    """Log returns simulated from the Merton model."""
    N = rng.poisson(lam * dt, n)
    jumps = mu_j * N + s_j * np.sqrt(N) * rng.standard_normal(n)
    return m * dt + sigma * np.sqrt(dt) * rng.standard_normal(n) + jumps


def _lr_stat(r, dt, sigma_min):
    """LR statistic, GBM vs Merton, on the restricted space sigma >= sigma_min, with the same optimisation rule
    (the six default starting points of merton_mle) for every sample."""
    l0 = stats.norm.logpdf(r, r.mean(), r.std()).sum()
    mf = merton_mle(r, dt, sigma_min=sigma_min)
    return max(2 * (mf['loglik'] - l0), 0.0), mf


def _lr_boot_one(args):
    rb, dt, sigma_min = args
    return _lr_stat(rb, dt, sigma_min)[0]


def lr_bootstrap(r, dt, n_boot, rng, sigma_min=0.05, n_jobs=1):
    """Likelihood-ratio test of GBM (no jumps) against Merton, with a parametric-bootstrap p-value.
    Under the null, lam = 0 lies on the boundary and mu_j, s_j are unidentified: the chi-square distribution does not apply.
    The unrestricted Merton likelihood is unbounded, so the statistic is defined on the restricted space
    sigma >= sigma_min; the same restriction and the same starting points for the observed sample and for every
    bootstrap sample. p-value: (1 + number of exceedances) / (1 + n_boot), with a 95% binomial upper bound."""
    r = np.asarray(r)
    g = gbm_mle(r, dt)
    lr, mf = _lr_stat(r, dt, sigma_min)
    samples = [gbm_simulate_returns(g['m'], g['sigma'], len(r), dt, rng) for _ in range(n_boot)]
    jobs = [(rb, dt, sigma_min) for rb in samples]
    if n_jobs > 1:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(n_jobs) as pool:
            boot = np.array(pool.map(_lr_boot_one, jobs))
    else:
        boot = np.array([_lr_boot_one(j) for j in jobs])
    k = int(np.sum(boot >= lr))
    return dict(lr=lr, n_exceed=k, p_boot=(k + 1) / (n_boot + 1), p_upper95=float(stats.beta.ppf(0.95, k + 1, n_boot - k)),
                boot=boot, crit95=float(np.quantile(boot, 0.95)), merton=mf, sigma_min=sigma_min)


# =============================================================================
# THE LEE-MYKLAND JUMP TEST
# =============================================================================
def lee_mykland(r, K=16, alpha=0.01):
    """Statistic L_t = r_t / sigma_t, with sigma_t^2 = bipower variation over the previous K-1 returns;
    a jump is detected if (|L_t| - C_n) / S_n exceeds the 1 - alpha quantile of the Gumbel distribution (Lee & Mykland, 2008)."""
    r = pd.Series(r).dropna()
    a = r.abs()
    bpv = (a * a.shift(1)).rolling(K - 2).sum().shift(1) / (K - 2)
    L = (r / np.sqrt(bpv)).dropna()
    n = len(L)
    c = np.sqrt(2 / np.pi)
    ln = np.log(n)
    Cn = np.sqrt(2 * ln) / c - (np.log(np.pi) + np.log(ln)) / (2 * c * np.sqrt(2 * ln))
    Sn = 1 / (c * np.sqrt(2 * ln))
    crit = -np.log(-np.log(1 - alpha))
    stat = (L.abs() - Cn) / Sn
    return pd.DataFrame({'r': r.reindex(L.index), 'L': L, 'stat': stat, 'jump': stat > crit}), crit


# =============================================================================
# HESTON: STOCHASTIC VOLATILITY
# =============================================================================
def heston_paths(S0, v0, mu, kappa, theta, xi, rho, T, n_steps, n_paths, rng, antithetic=False):
    """Full-truncation Euler scheme (Lord et al., 2010) for log S and v.
    d ln S = (mu - v/2) dt + sqrt(v) dW1;  dv = kappa (theta - v) dt + xi sqrt(v) dW2;  corr(dW1, dW2) = rho."""
    dt = T / n_steps
    m = n_paths // 2 if antithetic else n_paths
    x = np.full(n_paths, np.log(S0))
    v = np.full(n_paths, v0, dtype=float)
    X = np.empty((n_steps + 1, n_paths))
    V = np.empty((n_steps + 1, n_paths))
    X[0], V[0] = x, v
    for k in range(n_steps):
        z1 = rng.standard_normal(m)
        z2 = rng.standard_normal(m)
        if antithetic:
            z1, z2 = np.concatenate([z1, -z1]), np.concatenate([z2, -z2])
        w2 = rho * z1 + np.sqrt(1 - rho ** 2) * z2
        vp = np.maximum(v, 0.0)
        x = x + (mu - 0.5 * vp) * dt + np.sqrt(vp * dt) * z1
        v = v + kappa * (theta - vp) * dt + xi * np.sqrt(vp * dt) * w2
        X[k + 1], V[k + 1] = x, np.maximum(v, 0.0)
    return np.linspace(0, T, n_steps + 1), np.exp(X), V


def heston_from_vix(vix, price, dt):
    """Heston parameters from the VIX: v_t = (VIX_t / 100)^2 as a variance proxy; the discretised CIR regression
    (v_{t+1} - v_t) / sqrt(v_t) = kappa theta dt / sqrt(v_t) - kappa dt sqrt(v_t) + xi sqrt(dt) eps;
    rho = correlation between return shocks and variance shocks.
    Price and VIX are first aligned on common days; returns are then computed on this common grid,
    so that the return and the change in v cover the same interval."""
    d = pd.concat([vix.rename('vix'), price.rename('p')], axis=1, join='inner').dropna()
    d['r'] = np.log(d['p']).diff()
    d = d.dropna()
    v = (d['vix'] / 100) ** 2
    y = (v.shift(-1) - v) / np.sqrt(v)
    X = np.column_stack([dt / np.sqrt(v), -dt * np.sqrt(v)])
    ok = y.notna().values
    beta, *_ = np.linalg.lstsq(X[ok], y.values[ok], rcond=None)
    kappa = beta[1]
    theta = beta[0] / kappa
    res = y.values[ok] - X[ok] @ beta
    xi = res.std() / np.sqrt(dt)
    dv = (v.shift(-1) - v - kappa * (theta - v) * dt) / np.sqrt(v)
    zr = (d['r'].shift(-1) - d['r'].mean()) / np.sqrt(v)
    rho = pd.concat([dv, zr], axis=1).dropna().corr().iloc[0, 1]
    return dict(kappa=kappa, theta=theta, xi=xi, rho=rho, v0=float(v.iloc[-1]), n=int(ok.sum()),
                feller=2 * kappa * theta / xi ** 2, mean_vix=float(d['vix'].mean()),
                real_var=float(d['r'].var() / dt))


def heston_from_proxy(logret, dt, window=21):
    """The same CIR regression, with the variance proxied by annualised realised variance over a rolling window
    (for markets without a volatility index, e.g. BET and Bitcoin)."""
    rv = (logret ** 2).rolling(window).mean() / dt          # RV_t = (1/21) sum_{j=0}^{20} r_{t-j}^2 / dt
    proxy = 100 * np.sqrt(rv)
    price = np.exp(logret.cumsum())                           # price rebuilt on the returns calendar
    return heston_from_vix(proxy.dropna(), price, dt)


def heston_simulate_returns(p, n, dt, rng, mu=0.0, burn=500):
    """Daily log returns simulated from Heston (with a burn-in of burn steps)."""
    T = (n + burn) * dt
    _, S, _ = heston_paths(1.0, p['theta'], mu, p['kappa'], p['theta'], p['xi'], p['rho'], T, n + burn, 1, rng)
    return np.diff(np.log(S[:, 0]))[burn:]


def bs_call(S, K, T, sigma, r=0.0):
    """Black-Scholes price of a European call option."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d1 - sigma * np.sqrt(T))


def implied_vol(price, S, K, T, r=0.0):
    """Black-Scholes implied volatility (root by Brent's method)."""
    intrinsic = max(S - K * np.exp(-r * T), 0.0)
    if price <= intrinsic + 1e-10:
        return np.nan
    return optimize.brentq(lambda s: bs_call(S, K, T, s, r) - price, 1e-4, 5.0)


def heston_smile(p, T, strikes, rng, n_paths=100000, n_steps=126):
    """Monte Carlo call prices under Heston (zero rate, mu = 0) and their implied volatilities."""
    _, S, _ = heston_paths(1.0, p['v0'], 0.0, p['kappa'], p['theta'], p['xi'], p['rho'], T, n_steps, n_paths, rng,
                           antithetic=True)
    ST = S[-1] / S[-1].mean()                 # martingale correction: E[S_T] = S_0 = 1
    return np.array([implied_vol(np.maximum(ST - K, 0).mean(), 1.0, K, T) for K in strikes])


# =============================================================================
# STYLISED FACTS
# =============================================================================
def acf(x, lags):
    x = np.asarray(x) - np.mean(x)
    d = x @ x
    return np.array([x[k:] @ x[:-k] / d for k in lags])


def hill(x, share=0.05):
    """Hill statistic for the largest k = share * n values of x (n = total number of observations);
    with x = -r: the largest losses, k = 5% of all returns. It estimates the tail index only under
    regular variation (a Pareto-type tail); for a Normal tail it is a descriptive statistic of the tail shape."""
    x = np.sort(np.asarray(x))[::-1]
    k = int(share * len(x))
    return 1 / np.mean(np.log(x[:k] / x[k]))


def stylised(r, lags=range(1, 51)):
    """Stylised facts used to compare the models with the data."""
    r = np.asarray(r)
    a = acf(np.abs(r), list(lags))
    return dict(exkurt=float(stats.kurtosis(r)), skew=float(stats.skew(r)), hill=float(hill(-r)),
                acf_abs1=float(a[0]), acf_abs_sum20=float(a[:20].sum()), acf_r1=float(acf(r, [1])[0]),
                acf_abs=a)

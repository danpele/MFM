"""
option_tools.py -- Instrumente pentru Capitolul 12 (MFM): evaluarea optiunilor si volatilitatea implicita
=====================================================================================================
  * bs_price, bs_greeks        -- Black-Scholes (actiune cu randament de dividend q) si senzitivitatile
  * implied_vol, newton_iv     -- volatilitatea implicita (Brent; pasii metodei Newton pentru exemplu)
  * crr_price                  -- arborele binomial Cox-Ross-Rubinstein (european si american)
  * merton_price               -- modelul cu salturi Merton (1976), serie Poisson
  * heston_price               -- modelul Heston (1993), prin functia caracteristica
  * svi_w, svi_fit             -- parametrizarea SVI a variantei totale implicite
  * variance_from_strip        -- varianta implicita din optiuni OTM (formula indicelui VIX)
  * delta_hedge                -- acoperire delta discreta pe traiectorii simulate sau istorice
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
from scipy import stats, optimize, integrate

N, n = stats.norm.cdf, stats.norm.pdf


def bs_price(S, K, T, r, sigma, kind='call', q=0.0):
    """Black-Scholes price of a European option."""
    S, K, T, sigma = map(np.asarray, (S, K, T, sigma))
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if kind == 'call':
        return S * np.exp(-q * T) * N(d1) - K * np.exp(-r * T) * N(d2)
    return K * np.exp(-r * T) * N(-d2) - S * np.exp(-q * T) * N(-d1)


def bs_greeks(S, K, T, r, sigma, kind='call', q=0.0):
    """Delta, gamma, vega (per volatility point), theta (per calendar day), rho; plus d1, d2."""
    S, K, T, sigma = map(np.asarray, (S, K, T, sigma))
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    gamma = np.exp(-q * T) * n(d1) / (S * sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * n(d1) * np.sqrt(T) / 100
    common = -S * np.exp(-q * T) * n(d1) * sigma / (2 * np.sqrt(T))
    if kind == 'call':
        delta = np.exp(-q * T) * N(d1)
        theta = common - r * K * np.exp(-r * T) * N(d2) + q * S * np.exp(-q * T) * N(d1)
        rho = K * T * np.exp(-r * T) * N(d2) / 100
    else:
        delta = -np.exp(-q * T) * N(-d1)
        theta = common + r * K * np.exp(-r * T) * N(-d2) - q * S * np.exp(-q * T) * N(-d1)
        rho = -K * T * np.exp(-r * T) * N(-d2) / 100
    return dict(d1=d1, d2=d2, delta=delta, gamma=gamma, vega=vega, theta=theta / 365, rho=rho)


def implied_vol(price, S, K, T, r, kind='call', q=0.0, lo=1e-4, hi=5.0):
    """Implied volatility: the unique solution of BS(sigma) = price (vega > 0)."""
    f = lambda s: bs_price(S, K, T, r, s, kind, q) - price
    if f(lo) > 0 or f(hi) < 0:
        return np.nan
    return optimize.brentq(f, lo, hi, xtol=1e-10)


def newton_iv(price, S, K, T, r, sigma0=0.2, kind='call', steps=4):
    """Newton steps: sigma_{k+1} = sigma_k - (BS(sigma_k) - price) / vega(sigma_k)."""
    out, s = [], sigma0
    for _ in range(steps):
        p = float(bs_price(S, K, T, r, s, kind))
        v = float(bs_greeks(S, K, T, r, s, kind)['vega']) * 100
        s_new = s - (p - price) / v
        out.append(dict(sigma=s, price=p, vega=v, sigma_next=s_new))
        s = s_new
    return out


def crr_price(S, K, T, r, sigma, steps, kind='call', american=False):
    """Cox-Ross-Rubinstein binomial tree: u = exp(sigma sqrt(dt)), d = 1/u, p = (e^{r dt} - d)/(u - d)."""
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt)); d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    j = np.arange(steps + 1)
    ST = S * u ** (steps - j) * d ** j
    V = np.maximum(ST - K, 0) if kind == 'call' else np.maximum(K - ST, 0)
    for i in range(steps - 1, -1, -1):
        V = disc * (p * V[:-1] + (1 - p) * V[1:])
        if american:
            Si = S * u ** (i - np.arange(i + 1)) * d ** np.arange(i + 1)
            V = np.maximum(V, (Si - K) if kind == 'call' else (K - Si))
    return float(V[0])


def merton_price(S, K, T, r, sigma, lam, mu_j, sig_j, kind='call', nmax=60):
    """Merton (1976): log-normal jumps ln(1+J) ~ N(mu_j, sig_j^2), intensity lam; Poisson series of BS prices."""
    kappa = np.exp(mu_j + 0.5 * sig_j ** 2) - 1
    lam2 = lam * (1 + kappa)
    tot = 0.0
    for k in range(nmax):
        s_k = np.sqrt(sigma ** 2 + k * sig_j ** 2 / T)
        r_k = r - lam * kappa + k * np.log(1 + kappa) / T
        w = stats.poisson.pmf(k, lam2 * T)
        tot = tot + w * bs_price(S, K, T, r_k, s_k, kind)
    return tot


def heston_price(S, K, T, r, v0, kappa, theta, xi, rho, kind='call'):
    """Heston (1993): call price by the Lewis (2001) formula, with the characteristic function of ln(S_T/F) (stable form)."""
    def phi(u):
        d = np.sqrt((rho * xi * 1j * u - kappa) ** 2 + xi ** 2 * (1j * u + u ** 2))
        g = (kappa - rho * xi * 1j * u - d) / (kappa - rho * xi * 1j * u + d)
        e = np.exp(-d * T)
        C = kappa * theta / xi ** 2 * ((kappa - rho * xi * 1j * u - d) * T - 2 * np.log((1 - g * e) / (1 - g)))
        D = (kappa - rho * xi * 1j * u - d) / xi ** 2 * (1 - e) / (1 - g * e)
        return np.exp(C + D * v0)
    x = np.log(S / K) + r * T
    f = lambda u: (np.exp(1j * u * x) * phi(u - 0.5j)).real / (u ** 2 + 0.25)
    # integral over [0, 2^14] in dyadic pieces: a cut at u = 200 leaves an error of about 1e-5 in the price, which
    # visibly moves deep out-of-the-money implied volatilities
    edges = np.r_[0.0, 2.0 ** np.arange(15)]
    integral = sum(integrate.quad(f, a, b, limit=200, epsabs=1e-14, epsrel=1e-12)[0] for a, b in zip(edges[:-1], edges[1:]))
    call = S - np.sqrt(S * K) * np.exp(-r * T / 2) / np.pi * integral
    return call if kind == 'call' else call - S + K * np.exp(-r * T)


def svi_w(k, a, b, rho, m, s):
    """SVI (Gatheral): total implied variance w(k) = a + b (rho (k - m) + sqrt((k - m)^2 + s^2)), k = ln(K/F)."""
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + s ** 2))


def svi_fit(k, w, weights=None, *, return_diagnostics=False):
    """Fit the original weighted total-variance SSE within the original SVI box.

    Six starts and an analytic Jacobian resolve the local numerical fit. Boundary
    solutions remain box-dependent; convergence is not proof of a global optimum.
    Optional diagnostics expose all attempts without changing the default result.
    """
    import hashlib
    import scipy
    svi_fit.last_diagnostics = None
    k, w = np.asarray(k, dtype=float), np.asarray(w, dtype=float)
    wt = np.ones_like(w) if weights is None else np.asarray(weights, dtype=float)
    if (k.ndim != 1 or k.size == 0 or w.shape != k.shape or wt.shape != k.shape
            or not np.all(np.isfinite(k)) or not np.all(np.isfinite(w))
            or not np.all(np.isfinite(wt)) or np.any(wt < 0) or not np.isfinite(wt.sum()) or wt.sum() <= 0):
        raise ValueError('SVI requires finite equal-length vectors and nonnegative weights with positive sum.')
    bounds = np.array([(-1, 5), (1e-6, 10), (-0.999, 0.999), (-2, 2), (1e-4, 3)]).T
    root_wt = np.sqrt(wt)
    def residual(p):
        return root_wt * (svi_w(k, *p) - w)
    def jacobian(p):
        a, b, rho, m, s = p
        u = k - m
        d = np.sqrt(u * u + s * s)
        return root_wt[:, None] * np.column_stack((np.ones_like(k), rho*u+d,
                    b*u, b*(-rho-u/d), b*s/d))
    def fingerprint(values):
        return hashlib.sha256(np.ascontiguousarray(values, dtype='<f8').tobytes()).hexdigest()
    diagnostics = dict(input_sha256={name: fingerprint(value) for name, value in
                       [('k', k), ('w', w), ('weights', wt)]},
                       numpy=np.__version__, scipy=scipy.__version__, bounds=bounds.tolist(),
                       method='trf', loss='linear', x_scale='jac', ftol=None,
                       xtol=1e-14, gtol=1e-14, max_nfev=20000, attempts=[])
    svi_fit.last_diagnostics = diagnostics
    candidates = []
    for rho0 in (-0.5, 0.0, 0.3):
        for s0 in (0.05, 0.2):
            x0 = [max(w.min() * 0.5, 1e-4), 0.1, rho0, 0.0, s0]
            row = dict(start=len(diagnostics['attempts']), x0=list(x0), valid=False)
            try:
                res = optimize.least_squares(residual, x0, jac=jacobian, bounds=bounds,
                    method='trf', loss='linear', x_scale='jac', ftol=None,
                    xtol=1e-14, gtol=1e-14, max_nfev=20000)
                p = np.asarray(res.x)
                r, J = residual(p), jacobian(p)
                sse = float(r @ r)
                grad = 2 * J.T @ r
                pg = grad.copy()
                pg[(p <= bounds[0] + 1e-10) & (grad > 0)] = 0
                pg[(p >= bounds[1] - 1e-10) & (grad < 0)] = 0
                denom = 2 * np.linalg.norm(J, 2) * np.linalg.norm(r)
                scaled_pg = float(np.max(np.abs(pg)) / max(denom, np.finfo(float).tiny))
                if np.linalg.norm(r) == 0:
                    scaled_pg = 0.0
                valid = bool(res.success and res.status > 0 and np.all(np.isfinite(p))
                    and np.isfinite(sse) and np.all(p >= bounds[0]) and np.all(p <= bounds[1])
                    and np.isclose(sse, 2*res.cost, rtol=1e-10, atol=1e-24)
                    and np.isfinite(scaled_pg)
                    and (float(np.max(np.abs(pg))) <= 1e-10 or scaled_pg <= 1e-6))
                singular = np.linalg.svd(J, compute_uv=False)
                row.update(x=p.tolist(), success=bool(res.success), status=int(res.status),
                    message=str(res.message), nfev=int(res.nfev), sse=sse,
                    projected_gradient_inf=float(np.max(np.abs(pg))),
                    scaled_projected_gradient=scaled_pg, optimality=float(res.optimality),
                    active_bounds=np.flatnonzero((p <= bounds[0]+1e-10) | (p >= bounds[1]-1e-10)).tolist(),
                    singular_values=singular.tolist(), valid=valid)
                if valid:
                    candidates.append((sse, row['start'], p.copy()))
            except (ValueError, FloatingPointError, np.linalg.LinAlgError) as exc:
                row['error'] = type(exc).__name__ + ': ' + str(exc)
            diagnostics['attempts'].append(row)
    if not candidates:
        raise RuntimeError('SVI: no finite, converged, stationary candidate within the original box; inspect svi_fit.last_diagnostics.')
    sse, selected, p = min(candidates, key=lambda item: item[0])
    a, b, rho, m, s = p
    result = dict(a=a, b=b, rho=rho, m=m, s=s, rmse=np.sqrt(sse / wt.sum()),
                  wmin=a + b*s*np.sqrt(1-rho**2))
    diagnostics.update(selected_start=selected, sse=sse,
                       boundary_solution=bool(diagnostics['attempts'][selected]['active_bounds']),
                       interpretation='Local minimum in the original parameter box; no global-optimum or box-insensitivity claim.')
    return (result, diagnostics) if return_diagnostics else result


def variance_from_strip(K, Q, F, T, r=0.0):
    """Implied variance (VIX formula): 2/T sum dK/K^2 e^{rT} Q(K) - 1/T (F/K0 - 1)^2, Q = OTM price (mid)."""
    K, Q = np.asarray(K, float), np.asarray(Q, float)
    o = np.argsort(K); K, Q = K[o], Q[o]
    dK = np.empty_like(K)
    dK[1:-1] = (K[2:] - K[:-2]) / 2
    dK[0], dK[-1] = K[1] - K[0], K[-1] - K[-2]
    K0 = K[K <= F].max()
    return 2 / T * np.sum(dK / K ** 2 * np.exp(r * T) * Q) - (F / K0 - 1) ** 2 / T


def delta_hedge(paths, K, T, r, sigma_imp, n_rebal, kind='call'):
    """Sell an option at BS(sigma_imp) and delta-hedge it n_rebal times until expiry.
    paths: price matrix (n_paths, n_steps+1) on a uniform grid; n_steps divisible by n_rebal.
    Returns the hedging error at expiry (hedge portfolio value minus the option pay-off)."""
    npath, nstep = paths.shape[0], paths.shape[1] - 1
    every = nstep // n_rebal
    dt = T / nstep
    S0 = paths[:, 0]
    V0 = bs_price(S0, K, T, r, sigma_imp, kind)
    delta = bs_greeks(S0, K, T, r, sigma_imp, kind)['delta']
    cash = V0 - delta * S0
    for i in range(1, nstep + 1):
        cash = cash * np.exp(r * dt)
        if i % every == 0 and i < nstep:
            tau = T - i * dt
            d_new = bs_greeks(paths[:, i], K, tau, r, sigma_imp, kind)['delta']
            cash -= (d_new - delta) * paths[:, i]
            delta = d_new
    ST = paths[:, -1]
    payoff = np.maximum(ST - K, 0) if kind == 'call' else np.maximum(K - ST, 0)
    return cash + delta * ST - payoff

"""
ct_models.py -- Modele in timp continuu pentru Capitolul 11 (MFM): simulare si estimare
======================================================================================
  * miscarea browniana: mers aleator scalat (Donsker), traiectorii, variatia patratica, integrala Ito
  * scheme de discretizare: Euler-Maruyama, Milstein; convergenta tare si slaba
  * miscarea browniana geometrica (GBM): solutie exacta, estimare de verosimilitate maxima
  * Ornstein-Uhlenbeck / Vasicek: discretizare exacta AR(1), estimare, timpul de injumatatire
  * Merton (difuzie cu salturi): densitate ca mixtura Poisson, verosimilitate maxima, simulare
  * testul de salturi Lee-Mykland
  * Heston (volatilitate stochastica): simulare cu trunchiere completa, parametri din VIX, zambetul volatilitatii
  * fapte stilizate: aplatizare, indicele de coada Hill, autocorelatia |r|

Conventie: timpul in ani; randamente log zilnice (nu in %) in functiile de estimare.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize


# =============================================================================
# MISCAREA BROWNIANA
# =============================================================================
def scaled_random_walk(n, n_paths, rng):
    """Mersul aleator scalat W_n(t) = S_[nt] / sqrt(n), cu pasi +1/-1 egal probabili, pe grila t = k/n."""
    steps = rng.choice([-1.0, 1.0], size=(n_paths, n))
    S = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(steps, axis=1)], axis=1)
    return np.linspace(0, 1, n + 1), S / np.sqrt(n)


def bm_paths(n_paths, n_steps, T, rng):
    """Traiectorii ale miscarii browniene standard pe [0, T]: W_0 = 0, cresteri N(0, dt) independente."""
    dt = T / n_steps
    dW = rng.standard_normal((n_paths, n_steps)) * np.sqrt(dt)
    W = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1)
    return np.linspace(0, T, n_steps + 1), W


def quadratic_variation(W):
    """Suma patratelor cresterilor (variatia patratica pe grila data)."""
    return np.sum(np.diff(W, axis=-1) ** 2, axis=-1)


def total_variation(W):
    """Suma valorilor absolute ale cresterilor (variatia totala pe grila data)."""
    return np.sum(np.abs(np.diff(W, axis=-1)), axis=-1)


def ito_stratonovich(W):
    """Sumele Ito (capatul stang) si Stratonovich (punctul de mijloc) pentru integrala lui W dupa W."""
    dW = np.diff(W, axis=-1)
    ito = np.sum(W[..., :-1] * dW, axis=-1)
    strat = np.sum(0.5 * (W[..., :-1] + W[..., 1:]) * dW, axis=-1)
    return ito, strat


def max_prob(W, level=1.0):
    """Proportia traiectoriilor al caror maxim pe [0, T] depaseste nivelul dat."""
    return float(np.mean(W.max(axis=1) > level))


# =============================================================================
# SCHEME DE DISCRETIZARE (ecuatia de test a lui Higham: dX = lam X dt + mu X dW)
# =============================================================================
def em_milstein_gbm(x0, lam, mu, dW, dt):
    """Euler-Maruyama si Milstein pentru dX = lam X dt + mu X dW, cu cresterile browniene dW (n_paths x n)."""
    xe = np.full(dW.shape[0], x0, dtype=float)
    xm = xe.copy()
    for k in range(dW.shape[1]):
        d = dW[:, k]
        xe = xe + lam * xe * dt + mu * xe * d
        xm = xm + lam * xm * dt + mu * xm * d + 0.5 * mu ** 2 * xm * (d ** 2 - dt)
    return xe, xm


def convergence_study(rng, x0=1.0, lam=2.0, mu=1.0, T=1.0, n_fine=2 ** 11, n_paths=20000,
                      ratios=(1, 2, 4, 8, 16, 32, 64)):
    """Eroarea tare E|X_T - X^h_T| si eroarea slaba |E X^h_T - E X_T| pentru pasi dt = ratio * T / n_fine."""
    dt_f = T / n_fine
    dW = rng.standard_normal((n_paths, n_fine)) * np.sqrt(dt_f)
    WT = dW.sum(axis=1)
    x_true = x0 * np.exp((lam - 0.5 * mu ** 2) * T + mu * WT)
    ex = x0 * np.exp(lam * T)                       # E X_T exact
    rows = []
    for r in ratios:
        dWr = dW.reshape(n_paths, n_fine // r, r).sum(axis=2)
        h = r * dt_f
        xe, xm = em_milstein_gbm(x0, lam, mu, dWr, h)
        rows.append(dict(dt=h, strong_em=np.mean(np.abs(x_true - xe)), strong_mil=np.mean(np.abs(x_true - xm)),
                         strong_em_se=np.std(np.abs(x_true - xe)) / np.sqrt(n_paths),
                         strong_mil_se=np.std(np.abs(x_true - xm)) / np.sqrt(n_paths),
                         weak_em_exact=abs(x0 * (1 + lam * h) ** round(T / h) - ex),
                         weak_em_mc=abs(xe.mean() - ex), weak_mil_mc=abs(xm.mean() - ex)))
    return pd.DataFrame(rows)


def slope_ci(dt, err, level=0.95):
    """Panta regresiei log(eroare) pe log(dt), cu eroare standard si interval de incredere t."""
    x, y = np.log(np.asarray(dt)), np.log(np.asarray(err))
    res = stats.linregress(x, y)
    q = stats.t.ppf(0.5 + level / 2, len(x) - 2)
    return dict(slope=res.slope, se=res.stderr, lo=res.slope - q * res.stderr, hi=res.slope + q * res.stderr,
                intercept=res.intercept)


# =============================================================================
# MISCAREA BROWNIANA GEOMETRICA (GBM)
# =============================================================================
def gbm_paths(S0, mu, sigma, T, n_steps, n_paths, rng):
    """Solutia exacta S_t = S_0 exp((mu - sigma^2/2) t + sigma W_t) pe o grila regulata."""
    t, W = bm_paths(n_paths, n_steps, T, rng)
    return t, S0 * np.exp((mu - 0.5 * sigma ** 2) * t + sigma * W)


def gbm_mle(r, dt):
    """Verosimilitate maxima pentru GBM din randamente log r (aceeasi frecventa dt, in ani).

    r_t ~ N((mu - sigma^2/2) dt, sigma^2 dt), i.i.d.  =>  sigma^2 = var(r)/dt,  mu = mean(r)/dt + sigma^2/2.
    Erori standard: se(sigma) = sigma / sqrt(2n); se(drift log) = sigma / sqrt(n dt) (depinde doar de durata)."""
    r = np.asarray(r)
    n = len(r)
    s2 = r.var() / dt
    sigma = np.sqrt(s2)
    m = r.mean() / dt                       # drift-ul logaritmului (mu - sigma^2/2)
    return dict(n=n, years=n * dt, sigma=sigma, se_sigma=sigma / np.sqrt(2 * n), m=m, se_m=sigma / np.sqrt(n * dt),
                mu=m + 0.5 * s2)


def gbm_simulate_returns(m, sigma, n, dt, rng):
    """Randamente log i.i.d. Normale ale unei GBM (drift log m, volatilitate sigma)."""
    return m * dt + sigma * np.sqrt(dt) * rng.standard_normal(n)


# =============================================================================
# ORNSTEIN-UHLENBECK / VASICEK
# =============================================================================
def ou_exact_path(x0, kappa, theta, sigma, dt, n, rng, z=None):
    """Discretizarea exacta: x_{t+dt} = theta + (x_t - theta) e^{-kappa dt} + eps, eps ~ N(0, sigma^2 (1 - e^{-2 kappa dt}) / (2 kappa))."""
    b = np.exp(-kappa * dt)
    sd = sigma * np.sqrt((1 - b ** 2) / (2 * kappa))
    z = rng.standard_normal(n) if z is None else z
    x = np.empty(n + 1)
    x[0] = x0
    for k in range(n):
        x[k + 1] = theta + (x[k] - theta) * b + sd * z[k]
    return x


def ou_mle(x, dt):
    """Estimatorul de verosimilitate maxima (conditionat de x_0) al procesului OU: regresia AR(1) exacta.

    x_{t+1} = a + b x_t + e;  kappa = -ln b / dt;  theta = a / (1 - b);  sigma = s_e sqrt(2 kappa / (1 - b^2)).
    Erorile standard ale lui kappa, theta si ale timpului de injumatatire: metoda delta din covarianta OLS a (a, b)."""
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
    """Distributia de selectie a lui kappa estimat: n_sim traiectorii OU exacte (start din distributia stationara)."""
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
# MERTON: DIFUZIE CU SALTURI
# =============================================================================
def merton_logpdf(r, dt, m, sigma, lam, mu_j, s_j, kmax=12):
    """Log-densitatea randamentelor log pe un pas dt:  r = m dt + sigma W_dt + suma a N salturi N(mu_j, s_j^2),
    N ~ Poisson(lam dt). Densitatea este o mixtura de distributii Normale ponderate cu probabilitatile Poisson."""
    r = np.asarray(r)[:, None]
    k = np.arange(kmax + 1)[None, :]
    w = stats.poisson.pmf(k, lam * dt)
    mean = m * dt + k * mu_j
    var = sigma ** 2 * dt + k * s_j ** 2
    dens = (w * np.exp(-0.5 * (r - mean) ** 2 / var) / np.sqrt(2 * np.pi * var)).sum(axis=1)
    return np.log(np.maximum(dens, 1e-300))


def _merton_unpack(p):
    return p[0], np.exp(p[1]), np.exp(p[2]), p[3], np.exp(p[4])


def merton_mle(r, dt, starts=None):
    """Verosimilitate maxima pentru Merton (m, sigma, lam, mu_j, s_j); mai multe puncte de start.
    Erorile standard: inversa hessianei numerice in parametrii originali (metoda delta)."""
    r = np.asarray(r)
    sd = r.std()
    nll = lambda p: -merton_logpdf(r, dt, *_merton_unpack(p)).sum()
    if starts is None:
        starts = []
        for lam0 in (2.0, 10.0, 40.0):
            for sj0 in (1.5, 3.0):
                starts.append([r.mean() / dt, np.log(0.7 * sd / np.sqrt(dt)), np.log(lam0), -0.5 * sd, np.log(sj0 * sd)])
    best = None
    for s0 in starts:
        res = optimize.minimize(nll, s0, method='Nelder-Mead', options=dict(maxiter=20000, maxfev=20000, xatol=1e-7, fatol=1e-7))
        res = optimize.minimize(nll, res.x, method='BFGS')
        if best is None or res.fun < best.fun:
            best = res
    m, sigma, lam, mu_j, s_j = _merton_unpack(best.x)
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
    """Hessiana prin diferente finite centrale."""
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
    """Media, dispersia, asimetria si excesul de aplatizare ale randamentului Merton pe un pas dt (cumulanti)."""
    k1 = m * dt + lam * dt * mu_j
    k2 = sigma ** 2 * dt + lam * dt * (mu_j ** 2 + s_j ** 2)
    k3 = lam * dt * (mu_j ** 3 + 3 * mu_j * s_j ** 2)
    k4 = lam * dt * (mu_j ** 4 + 6 * mu_j ** 2 * s_j ** 2 + 3 * s_j ** 4)
    return dict(mean=k1, var=k2, skew=k3 / k2 ** 1.5, exkurt=k4 / k2 ** 2)


def merton_simulate_returns(m, sigma, lam, mu_j, s_j, n, dt, rng):
    """Randamente log simulate din modelul Merton."""
    N = rng.poisson(lam * dt, n)
    jumps = mu_j * N + s_j * np.sqrt(N) * rng.standard_normal(n)
    return m * dt + sigma * np.sqrt(dt) * rng.standard_normal(n) + jumps


def lr_bootstrap(r, dt, n_boot, rng):
    """Testul raportului de verosimilitate GBM (fara salturi) vs Merton, cu valoarea p din bootstrap parametric.
    Sub ipoteza nula lam = 0 se afla pe frontiera, iar mu_j, s_j nu sunt identificati: distributia chi-patrat nu se aplica."""
    r = np.asarray(r)
    g = gbm_mle(r, dt)
    ll0 = stats.norm.logpdf(r, r.mean(), r.std()).sum()
    mf = merton_mle(r, dt)
    lr = 2 * (mf['loglik'] - ll0)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        rb = gbm_simulate_returns(g['m'], g['sigma'], len(r), dt, rng)
        l0 = stats.norm.logpdf(rb, rb.mean(), rb.std()).sum()
        mb = merton_mle(rb, dt, starts=[[rb.mean() / dt, np.log(rb.std() / np.sqrt(dt)), np.log(5.0), 0.0, np.log(2 * rb.std())],
                                        [rb.mean() / dt, np.log(0.8 * rb.std() / np.sqrt(dt)), np.log(30.0), 0.0, np.log(1.5 * rb.std())]])
        boot[i] = max(2 * (mb['loglik'] - l0), 0.0)
    return dict(lr=lr, p_boot=float(np.mean(boot >= lr)), boot=boot, crit95=float(np.quantile(boot, 0.95)), merton=mf)


# =============================================================================
# TESTUL DE SALTURI LEE-MYKLAND
# =============================================================================
def lee_mykland(r, K=16, alpha=0.01):
    """Statistica L_t = r_t / sigma_t, cu sigma_t^2 = variatia bipower pe cele K-1 randamente anterioare;
    salt detectat daca (|L_t| - C_n) / S_n depaseste cuantila 1 - alpha a distributiei Gumbel (Lee & Mykland, 2008)."""
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
# HESTON: VOLATILITATE STOCHASTICA
# =============================================================================
def heston_paths(S0, v0, mu, kappa, theta, xi, rho, T, n_steps, n_paths, rng, antithetic=False):
    """Schema Euler cu trunchiere completa (Lord et al., 2010) pentru log S si v.
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


def heston_from_vix(vix, logret, dt):
    """Parametrii Heston din VIX: v_t = (VIX_t / 100)^2 ca aproximare a variantei; regresia CIR discretizata
    (v_{t+1} - v_t) / sqrt(v_t) = kappa theta dt / sqrt(v_t) - kappa dt sqrt(v_t) + xi sqrt(dt) eps;
    rho = corelatia dintre socurile de randament si socurile de varianta."""
    d = pd.concat([vix.rename('vix'), logret.rename('r')], axis=1, join='inner').dropna()
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
    """Aceeasi regresie CIR, cu varianta aproximata prin varianta realizata anualizata pe o fereastra mobila
    (pentru piete fara un indice de volatilitate, de exemplu BET si Bitcoin)."""
    rv = (logret ** 2).rolling(window).mean() / dt
    proxy = 100 * np.sqrt(rv)
    return heston_from_vix(proxy.dropna(), logret, dt)


def heston_simulate_returns(p, n, dt, rng, mu=0.0, burn=500):
    """Randamente log zilnice simulate din Heston (cu o perioada de incalzire de burn pasi)."""
    T = (n + burn) * dt
    _, S, _ = heston_paths(1.0, p['theta'], mu, p['kappa'], p['theta'], p['xi'], p['rho'], T, n + burn, 1, rng)
    return np.diff(np.log(S[:, 0]))[burn:]


def bs_call(S, K, T, sigma, r=0.0):
    """Pretul Black-Scholes al unei optiuni call europene."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d1 - sigma * np.sqrt(T))


def implied_vol(price, S, K, T, r=0.0):
    """Volatilitatea implicita Black-Scholes (radacina prin metoda Brent)."""
    intrinsic = max(S - K * np.exp(-r * T), 0.0)
    if price <= intrinsic + 1e-10:
        return np.nan
    return optimize.brentq(lambda s: bs_call(S, K, T, s, r) - price, 1e-4, 5.0)


def heston_smile(p, T, strikes, rng, n_paths=100000, n_steps=126):
    """Preturi Monte Carlo ale optiunilor call sub Heston (rata zero, mu = 0) si volatilitatile implicite."""
    _, S, _ = heston_paths(1.0, p['v0'], 0.0, p['kappa'], p['theta'], p['xi'], p['rho'], T, n_steps, n_paths, rng,
                           antithetic=True)
    ST = S[-1] / S[-1].mean()                 # corectie de martingal: E[S_T] = S_0 = 1
    return np.array([implied_vol(np.maximum(ST - K, 0).mean(), 1.0, K, T) for K in strikes])


# =============================================================================
# FAPTE STILIZATE
# =============================================================================
def acf(x, lags):
    x = np.asarray(x) - np.mean(x)
    d = x @ x
    return np.array([x[k:] @ x[:-k] / d for k in lags])


def hill(x, share=0.05):
    """Estimatorul Hill al indicelui de coada pentru cele mai mari share din valori (pierderi)."""
    x = np.sort(np.asarray(x))[::-1]
    k = int(share * len(x))
    return 1 / np.mean(np.log(x[:k] / x[k]))


def stylised(r, lags=range(1, 51)):
    """Faptele stilizate folosite pentru compararea modelelor cu datele."""
    r = np.asarray(r)
    a = acf(np.abs(r), list(lags))
    return dict(exkurt=float(stats.kurtosis(r)), skew=float(stats.skew(r)), hill=float(hill(-r)),
                acf_abs1=float(a[0]), acf_abs_sum20=float(a[:20].sum()), acf_r1=float(acf(r, [1])[0]),
                acf_abs=a)

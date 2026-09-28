"""
risk_measures.py -- Masurile de risc ale Capitolului 7 (MFM): VaR si Expected Shortfall
=====================================================================================
Conventia nivelului (probabilitatea cozii alpha, ex. alpha = 1%):
  VaR_alpha(X) = -inf{x : P(X <= x) > alpha} = -q_alpha(X), pierderea depasita cu probabilitatea alpha;
  ES_alpha(X)  = -(1/alpha) * integrala_0^alpha q_u(X) du = -E[X | X <= q_alpha(X)] (distributii continue).
Codul lucreaza cu pierderea L = -X (in %): VaR_alpha = q_{1-alpha}(L), ES_alpha = E[L | L >= VaR_alpha];
VaR si ES sunt numere POZITIVE atunci cand reprezinta pierderi.

Metode: istorica (HS), distributia Normala, Student-t, Cornish-Fisher, FHS (GARCH filtrat),
EVT: POT/GPD (necondiționat) si EVT conditionat (McNeil & Frey, 2000); GEV pe maxime pe blocuri.

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats, integrate
from arch import arch_model


def hs_var_es(L, alpha):
    """Simulare istorica: VaR alpha = cuantila empirica 1 - alpha a pierderii; ES = media pierderilor de dincolo."""
    L = np.asarray(L)
    v = np.quantile(L, 1 - alpha)
    return v, L[L >= v].mean()


def normal_var_es(L, alpha):
    """Distributia Normala: VaR = -mu_X + sigma z_{1-alpha}, ES = -mu_X + sigma phi(z_alpha)/alpha (mu_L = -mu_X)."""
    mu, s = np.mean(L), np.std(L, ddof=1)
    z = stats.norm.ppf(1 - alpha)
    return mu + s * z, mu + s * stats.norm.pdf(z) / alpha


def t_fit(L):
    """Student-t cu locatie si scala, estimata prin verosimilitate maxima."""
    return stats.t.fit(np.asarray(L))


def t_var_es(L, alpha, params=None):
    """Student-t pe pierderi: VaR = m + s t_{1-alpha}, ES = m + s g(t_alpha)/alpha (nu + t_alpha^2)/(nu - 1)."""
    nu, m, s = params if params is not None else t_fit(L)
    q = stats.t.ppf(1 - alpha, nu)
    return m + s * q, m + s * stats.t.pdf(q, nu) / alpha * (nu + q ** 2) / (nu - 1)


def cf_quantile(z, S, K):
    """Cuantila Cornish-Fisher standardizata: z = cuantila Normala, S = asimetria, K = excesul de aplatizare."""
    return z + (z ** 2 - 1) * S / 6 + (z ** 3 - 3 * z) * K / 24 - (2 * z ** 3 - 5 * z) * S ** 2 / 36


def cf_var_es(L, alpha):
    """Cornish-Fisher pe randamente X = -L: VaR = -(mu_X + sigma z~_alpha); ES = media lui VaR_u pentru u in (0, alpha)."""
    X = -np.asarray(L)
    mu, s = X.mean(), X.std(ddof=1)
    S, K = stats.skew(X), stats.kurtosis(X)
    var = -(mu + s * cf_quantile(stats.norm.ppf(alpha), S, K))
    es = -integrate.quad(lambda u: mu + s * cf_quantile(stats.norm.ppf(u), S, K), 0, alpha, limit=200)[0] / alpha
    return var, es


def gpd_fit(L, tail=0.05):
    """POT: pragul u lasa deasupra proportia tail din pierderi; GPD estimata prin verosimilitate maxima pe excese."""
    L = np.asarray(L)
    u = np.quantile(L, 1 - tail)
    ex = L[L > u] - u
    xi, _, beta = stats.genpareto.fit(ex, floc=0)
    return dict(u=u, xi=xi, beta=beta, nu=len(ex), n=len(L))


def gpd_var_es(fit, alpha):
    """VaR si ES cu probabilitatea cozii alpha din coada GPD (estimatorul de tip Smith)."""
    u, xi, beta, nu, n = fit['u'], fit['xi'], fit['beta'], fit['nu'], fit['n']
    var = u + beta / xi * (((n / nu) * alpha) ** (-xi) - 1)
    return var, var / (1 - xi) + (beta - xi * u) / (1 - xi)


def gpd_se(fit):
    """Erori standard asimptotice ale MLE pentru GPD (xi > -1/2)."""
    xi, beta, nu = fit['xi'], fit['beta'], fit['nu']
    return np.sqrt((1 + xi) ** 2 / nu), np.sqrt(2 * beta ** 2 * (1 + xi) / nu)


def mean_excess(L, us):
    """Functia de exces mediu e(u) = E[L - u | L > u] pe o grila de praguri."""
    L = np.asarray(L)
    return np.array([(L[L > u] - u).mean() for u in us]), np.array([(L > u).sum() for u in us])


def garch_filter(r, params=None, last_obs=None):
    """AR(1)-GARCH(1,1) cu QML Normal (Capitolul 5); r in %.
    Intoarce modelul estimat (pana la last_obs) si seriile mu_t, sigma_t pentru toata selectia."""
    am = arch_model(r, mean='AR', lags=1, vol='GARCH', p=1, q=1, dist='normal', rescale=False)
    if params is None:
        params = am.fit(disp='off', last_obs=last_obs).params
    fx = am.fix(params)
    sig = fx.conditional_volatility
    mu = r - fx.resid
    return params, mu, sig


def garch_next(r, params):
    """Media si volatilitatea conditionate pentru ziua urmatoare ultimei observatii."""
    c, phi, om, al, be = params.values[:5]
    _, mu, sig = garch_filter(r, params)
    e = r.iloc[-1] - mu.iloc[-1]
    return c + phi * r.iloc[-1], np.sqrt(om + al * e ** 2 + be * sig.iloc[-1] ** 2)


def fhs_mc(r, params, z, h, n_paths=100_000, seed=42):
    """Monte Carlo FHS: traiectorii AR(1)-GARCH(1,1) pe h zile cu reziduuri standardizate reesantionate.
    Intoarce pierderile cumulate pe h zile (in %, randamente log)."""
    rng = np.random.default_rng(seed)
    c, phi, om, al, be = params.values[:5]
    _, mu, sig = garch_filter(r, params)
    r_prev = np.full(n_paths, r.iloc[-1])
    e_prev = np.full(n_paths, r.iloc[-1] - mu.iloc[-1])
    s2_prev = np.full(n_paths, sig.iloc[-1] ** 2)
    tot = np.zeros(n_paths)
    for _ in range(h):
        s2 = om + al * e_prev ** 2 + be * s2_prev
        e = np.sqrt(s2) * rng.choice(z, n_paths)
        r_new = c + phi * r_prev + e
        tot += r_new
        r_prev, e_prev, s2_prev = r_new, e, s2
    return -tot


def rolling_conditional(r, first_year, window_hs=500, alpha=0.01, tail_evt=0.10):
    """VaR/ES conditionat zi de zi: parametrii AR(1)-GARCH re-estimati la fiecare inceput de an
    pe toate datele anterioare; FHS si EVT conditionat folosesc reziduurile standardizate anterioare.
    Pentru comparatie: HS pe fereastra mobila de window_hs zile. Fara informatie din viitor."""
    out = []
    L = -r
    for y in range(first_year, r.index[-1].year + 1):
        est = r.loc[:f'{y - 1}-12-31']
        params, mu, sig = garch_filter(r, last_obs=f'{y}-01-01')
        z = ((est - mu.loc[est.index]) / sig.loc[est.index]).dropna()
        nz = -z.values
        fz = gpd_fit(nz, tail_evt)
        q_fhs, q_evt_v = np.quantile(nz, 1 - alpha), gpd_var_es(fz, alpha)[0]
        es_fhs = nz[nz >= q_fhs].mean()
        es_evt = gpd_var_es(fz, alpha)[1]
        days = r.loc[f'{y}-01-01':f'{y}-12-31'].index
        for d in days:
            i = r.index.get_loc(d)
            past = L.iloc[max(0, i - window_hs):i]
            out.append((d, L.loc[d], -mu.loc[d] + sig.loc[d] * q_fhs, -mu.loc[d] + sig.loc[d] * es_fhs,
                        -mu.loc[d] + sig.loc[d] * q_evt_v, -mu.loc[d] + sig.loc[d] * es_evt,
                        -mu.loc[d] + sig.loc[d] * stats.norm.ppf(1 - alpha), np.quantile(past, 1 - alpha), sig.loc[d]))
    return pd.DataFrame(out, columns=['date', 'loss', 'fhs_var', 'fhs_es', 'cevt_var', 'cevt_es', 'ngarch_var',
                                      'hs_var', 'sigma']).set_index('date')


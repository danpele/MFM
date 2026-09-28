"""
garch_tools.py -- Functii pentru Capitolul 5 (MFM): estimarea, diagnosticul si prognoza modelelor GARCH
=====================================================================================================
  * fit_garch(r, vol, dist)   -- GARCH / GJR-GARCH / EGARCH cu inovatii Normale, t, t asimetric sau GED
                                 (pachetul arch); seria este rescalata intern daca este prea putin volatila
  * half_life(persistence)    -- timpul de injumatatire al unui soc de volatilitate
  * news_impact(res, eps)     -- curba de impact a stirilor (Engle-Ng, 1993)
  * sign_bias_test(z, eps)    -- testele de asimetrie Engle-Ng (1993, ec. 18): z_t^2 pe S-, S- eps, S+ eps
  * ewma_variance(r, lam)     -- varianta EWMA (RiskMetrics, lambda = 0.94)
  * qlike, mz_regression, dm_test -- evaluarea prognozelor de volatilitate (Patton, 2011; Mincer-Zarnowitz; Diebold-Mariano)

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from arch import arch_model

VOL_SPEC = {'GARCH': dict(vol='GARCH', p=1, o=0, q=1),
            'GJR': dict(vol='GARCH', p=1, o=1, q=1),
            'EGARCH': dict(vol='EGARCH', p=1, o=1, q=1)}
DISTS = {'normal': 'Normal', 't': 'Student-t', 'skewt': 'Skewed-t', 'ged': 'GED'}


class Fit:
    """Rezultatul unei estimari, exprimat in unitatile seriei originale (randamente in %)."""

    def __init__(self, res, c, r, vol):
        self.res, self.c, self.r, self.vol = res, c, r, vol
        p = res.params.copy()
        p['mu'] = p['mu'] / c
        if vol == 'EGARCH':
            p['omega'] = p['omega'] - (1 - p['beta[1]']) * np.log(c ** 2)
        else:
            p['omega'] = p['omega'] / c ** 2
        self.params = p
        # covarianta robusta (Bollerslev-Wooldridge) transformata in unitatile originale cu jacobianul
        # transformarii: mu/c, omega/c^2 (GARCH, GJR) sau omega - (1 - beta) ln c^2 (EGARCH)
        names = list(res.params.index)
        J = np.eye(len(names))
        J[names.index('mu'), names.index('mu')] = 1 / c
        if vol == 'EGARCH':
            J[names.index('omega'), names.index('beta[1]')] = np.log(c ** 2)
        else:
            J[names.index('omega'), names.index('omega')] = 1 / c ** 2
        self.cov = pd.DataFrame(J @ res.param_cov.values @ J.T, index=names, columns=names)
        self.se = pd.Series(np.sqrt(np.diag(self.cov.values)), index=names)
        self.tvalues = p[names] / self.se
        self.pvalues = pd.Series(2 * stats.norm.sf(np.abs(self.tvalues.values)), index=names)
        n = res.nobs
        self.nobs = n
        self.loglik = res.loglikelihood + n * np.log(c)
        k = len(p)
        self.aic = -2 * self.loglik + 2 * k
        self.bic = -2 * self.loglik + k * np.log(n)
        self.sigma = res.conditional_volatility / c
        self.z = res.std_resid
        self.eps = res.resid / c                   # reziduuri nestandardizate, in unitatile seriei originale
        self.converged = res.convergence_flag == 0

    @property
    def persistence(self):
        p = self.params
        if self.vol == 'EGARCH':
            return p['beta[1]']
        g = p.get('gamma[1]', 0.0)
        return p['alpha[1]'] + p['beta[1]'] + g * self.neg_share()

    def neg_share(self):
        """E[z^2 1(z < 0)] pentru distributia inovatiilor (0.5 daca este simetrica); intra in persistenta GJR."""
        d = self.res.model.distribution
        if d.name.startswith('Standardized Skew'):
            from scipy import integrate
            par = self.res.params[d.parameter_names()].values
            pdf = lambda x: float(np.exp(d.loglikelihood(par, np.array([x]), np.array([1.0]), individual=True))[0])
            return float(integrate.quad(lambda x: x ** 2 * pdf(x), -np.inf, 0, limit=200)[0])
        return 0.5

    def uncond_var(self):
        p = self.params
        if self.vol == 'EGARCH':
            return np.nan
        return p['omega'] / (1 - self.persistence)

    def forecast_var(self, horizon):
        """Prognoza variantei zilnice pentru t+1, ..., t+h, in %^2."""
        f = self.res.forecast(horizon=horizon, reindex=False, method='analytic' if self.vol != 'EGARCH' else 'simulation',
                              simulations=2000)
        return f.variance.iloc[-1].values / self.c ** 2


def scale_for(r):
    """Factor de rescalare (putere a lui 10) astfel incat abaterea standard sa fie de ordinul 1."""
    s = r.std()
    return 10.0 if s < 0.5 else 1.0


def fit_garch(r, vol='GARCH', dist='t', mean='Constant', last_obs=None, c=None):
    c = scale_for(r) if c is None else c
    am = arch_model(c * r, mean=mean, dist=dist, **VOL_SPEC[vol])
    res = am.fit(disp='off', last_obs=last_obs, options={'maxiter': 1000})
    return Fit(res, c, r, vol)


def half_life(persistence):
    """Numarul de zile dupa care jumatate din socul asupra variantei s-a disipat."""
    return np.log(0.5) / np.log(persistence) if 0 < persistence < 1 else np.inf


def news_impact(fit, eps, sigma2_bar=None):
    """sigma^2_t ca functie de socul eps_{t-1}, cu sigma^2_{t-1} fixat la varianta de selectie."""
    p = fit.params
    s2 = fit.r.var() if sigma2_bar is None else sigma2_bar
    if fit.vol == 'EGARCH':
        z = eps / np.sqrt(s2)
        return np.exp(p['omega'] + p['alpha[1]'] * (np.abs(z) - np.sqrt(2 / np.pi)) + p['gamma[1]'] * z
                      + p['beta[1]'] * np.log(s2))
    g = p.get('gamma[1]', 0.0)
    return p['omega'] + (p['alpha[1]'] + g * (eps < 0)) * eps ** 2 + p['beta[1]'] * s2


def sign_bias_test(z, eps):
    """Engle-Ng (1993, ec. 18): z_t^2 pe S-_{t-1}, S-_{t-1} eps_{t-1}, S+_{t-1} eps_{t-1}, cu eps_{t-1} reziduul
    NESTANDARDIZAT si z_t reziduul standardizat; t-uri si testul comun T R^2 ~ chi2(3)."""
    d = pd.concat([pd.Series(z), pd.Series(eps)], axis=1, keys=['z', 'e']).dropna()
    z, e = d['z'].values, d['e'].values
    y = z[1:] ** 2
    el = e[:-1]
    sneg = (el < 0).astype(float)
    X = np.column_stack([np.ones_like(el), sneg, sneg * el, (1 - sneg) * el])
    ols = sm.OLS(y, X).fit()
    joint = len(y) * ols.rsquared
    return {'sign_t': ols.tvalues[1], 'neg_size_t': ols.tvalues[2], 'pos_size_t': ols.tvalues[3],
            'joint': joint, 'joint_p': 1 - stats.chi2.cdf(joint, 3)}


def ljung_box(x, lags=10):
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb = acorr_ljungbox(pd.Series(np.asarray(x)).dropna(), lags=[lags])
    return float(lb['lb_stat'].iloc[0]), float(lb['lb_pvalue'].iloc[0])


def arch_lm(x, lags=5):
    from statsmodels.stats.diagnostic import het_arch
    lm, lmp, _, _ = het_arch(pd.Series(np.asarray(x)).dropna(), nlags=lags)
    return float(lm), float(lmp)


def ewma_variance(r, lam=0.94, init=250):
    """Prognoza EWMA pentru ziua t+1 (aliniata la t+1): s2_{t+1} = lam s2_t + (1 - lam) r_t^2."""
    x = r.values
    s2 = np.empty(len(x) + 1)
    s2[0] = np.mean(x[:init] ** 2)
    for t in range(len(x)):
        s2[t + 1] = lam * s2[t] + (1 - lam) * x[t] ** 2
    return pd.Series(s2[1:-1], index=r.index[1:])


def qlike(proxy, h):
    """Pierderea QLIKE (Patton, 2011), forma folosita la comparatii: proxy/h + ln h."""
    return proxy / h + np.log(h)


def mz_regression(proxy, h, lags=5):
    """Mincer-Zarnowitz: proxy = a + b h + u, erori HAC; testul Wald a = 0, b = 1."""
    X = sm.add_constant(np.asarray(h))
    ols = sm.OLS(np.asarray(proxy), X).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    w = ols.wald_test((np.eye(2), np.array([0.0, 1.0])), scalar=True)
    return {'a': ols.params[0], 'b': ols.params[1], 'a_se': ols.bse[0], 'b_se': ols.bse[1],
            'r2': ols.rsquared, 'wald': float(w.statistic), 'wald_p': float(w.pvalue)}


def dm_test(loss_a, loss_b, lags=5):
    """Diebold-Mariano: d = L_a - L_b; t-statistic HAC pentru media lui d (negativ: A mai bun)."""
    d = np.asarray(loss_a) - np.asarray(loss_b)
    ols = sm.OLS(d, np.ones_like(d)).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    t = float(ols.tvalues[0])
    return {'mean_diff': float(d.mean()), 't': t, 'p': 2 * (1 - stats.norm.cdf(abs(t)))}

"""
inference5.py -- asymptotic inference for GARCH models (Chapter 5, MFM)
========================================================================
  * qmle_efficiency()     -- Gaussian QMLE: ratio of robust / classical standard errors and sqrt((kappa_z - 1)/2)
  * boundary_tests()      -- LR Normal vs Student-t (1/nu = 0 on the boundary): the mixture 1/2 chi2(0) + 1/2 chi2(1)
  * delta_method()        -- delta method for long-run volatility and half-life
  * moments_garch_n()     -- fourth-moment condition, kurtosis K and rho_1(eps^2) for GARCH-N
  * li_mak()              -- portmanteau on squared standardised residuals with estimated parameters (Li & Mak, 1994)
  * gjr_skew_persistence()-- GJR persistence with skewed-t innovations: alpha + gamma E[z^2 1(z<0)] + beta
  * gw_mcs(k)             -- Giacomini-White (rolling 1000-day window) and the 90% Model Confidence Set on QLIKE

Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats, integrate
from scipy.signal import lfilter
from arch.bootstrap import MCS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from garch_tools import fit_garch, half_life, qlike, dm_test, ewma_variance       # noqa: E402
from generate_all_charts import rets, oos_forecasts, MODELS_OOS, PPY, TABLE_DIR   # noqa: E402

SEED = 42
INF = {}


def qmle_efficiency():
    """Gaussian QMLE: avar = (kappa_z - 1) J^{-1}; classical (inverse Hessian) = 2 J^{-1}; s.e. ratio sqrt((kappa_z-1)/2)."""
    out = {}
    for k in ['sp500', 'btc']:
        f = fit_garch(rets[k], 'GARCH', 'normal')
        cl = f.res.model.fit(disp='off', cov_type='classic', starting_values=f.res.params.values)
        z = f.z.dropna()
        kz = float(stats.kurtosis(z, fisher=False))
        out[k] = {'kappa_z': kz, 'theory_ratio': float(np.sqrt((kz - 1) / 2)),
                  'ratio_alpha': float(f.se['alpha[1]'] / cl.std_err['alpha[1]']),
                  'ratio_beta': float(f.se['beta[1]'] / cl.std_err['beta[1]']),
                  'alpha': float(f.params['alpha[1]']), 'beta': float(f.params['beta[1]'])}
        # stability of the sample kurtosis: first half vs full sample
        out[k]['kappa_half'] = float(stats.kurtosis(z.iloc[:len(z) // 2], fisher=False))
    INF['qmle'] = out


def boundary_tests():
    """LR for Normal (1/nu = 0) against Student-t: 1/nu >= 0, so the limit law is 1/2 chi2(0) + 1/2 chi2(1)."""
    out = {'crit_mix': float(stats.chi2.ppf(0.90, 1)), 'crit_chi2': float(stats.chi2.ppf(0.95, 1))}
    for k in ['sp500', 'btc']:
        fn, ft = fit_garch(rets[k], 'GARCH', 'normal'), fit_garch(rets[k], 'GARCH', 't')
        lr = 2 * (ft.loglik - fn.loglik)
        out[k] = {'lr': float(lr), 'p_mix': float(0.5 * stats.chi2.sf(lr, 1)), 'nu': float(ft.params['nu'])}
    g = fit_garch(rets['sp500'], 'GJR', 't')
    out['gjr_alpha'] = float(g.params['alpha[1]'])
    INF['boundary'] = out


def delta_method():
    """Delta method from the robust covariance of (omega, alpha, beta), GARCH(1,1)-t, S&P 500."""
    f = fit_garch(rets['sp500'], 'GARCH', 't')
    p = f.params
    V = f.cov.loc[['omega', 'alpha[1]', 'beta[1]'], ['omega', 'alpha[1]', 'beta[1]']].values   # original units (Jacobian)
    om, a, b = p['omega'], p['alpha[1]'], p['beta[1]']
    pers = a + b
    se_p = float(np.sqrt(V[1:, 1:].sum()))
    s2 = om / (1 - pers)
    g = np.array([1 / (1 - pers), om / (1 - pers) ** 2, om / (1 - pers) ** 2])
    se_s2 = float(np.sqrt(g @ V @ g))
    vol = np.sqrt(PPY['sp500'] * s2)
    se_vol = PPY['sp500'] * se_s2 / (2 * vol)
    hl = half_life(pers)
    dh = -np.log(0.5) / (pers * np.log(pers) ** 2)
    lo, hi = pers - 1.96 * se_p, pers + 1.96 * se_p
    INF['delta'] = {'pers': float(pers), 'se_p': se_p, 's2': float(s2), 'se_s2': se_s2, 'vol': float(vol),
                    'se_vol': float(se_vol), 'hl': float(hl), 'dh': float(dh), 'se_hl': float(dh * se_p),
                    'p_lo': float(lo), 'p_hi': float(hi), 'hl_lo': float(half_life(lo)),
                    'grad_om': float(g[0]), 'grad_ab': float(g[1])}


def moments_garch_n():
    """GARCH(1,1) with Normal innovations: (alpha+beta)^2 + 2 alpha^2, K and rho_1(eps^2), at full precision and rounded."""
    f = fit_garch(rets['sp500'], 'GARCH', 'normal')
    a, b = f.params['alpha[1]'], f.params['beta[1]']

    def mom(a, b):
        c = (a + b) ** 2 + 2 * a ** 2
        K = 3 * (1 - (a + b) ** 2) / (1 - c)
        rho1 = a * (1 - b ** 2 - a * b) / (1 - b ** 2 - 2 * a * b)
        return float(c), float(K), float(rho1)
    c, K, rho1 = mom(a, b)
    c3, K3, rho13 = mom(round(a, 3), round(b, 3))
    e2 = (rets['sp500'] - rets['sp500'].mean()) ** 2
    INF['mom'] = {'alpha': float(a), 'beta': float(b), 'cond': c, 'K': K, 'rho1': rho1,
                  'cond3': c3, 'K3': K3, 'rho13': rho13, 'rho10': float(rho1 * (a + b) ** 9),
                  'dKda': float((K3 - K)), 'rho1_sample': float(e2.autocorr(1)), 'rho10_sample': float(e2.autocorr(10))}


def li_mak(M=10):
    """Autocorrelations of the squared standardised residuals after Gaussian QMLE (S&P 500, GARCH-N, constant mean).
    Li & Mak (1994): sqrt(n) r_hat -> N(0, C). All four parameters theta = (mu, omega, alpha, beta) are estimated, so
    the correction uses the joint expansion
        n^{-1} sum u_t u_{t-k} (estimated) = n^{-1} sum u_t u_{t-k} - H_k' (theta_hat - theta),  theta_hat - theta = A^{-1} s_bar,
    with u_t = z_t^2 - 1, g_t = d ln sigma_t^2 / d theta (the mu-component included), H_k = E[g_t u_{t-k}],
    the Gaussian quasi-score s_t = g_t u_t / 2 + (z_t / sigma_t) d_t, d_t = (1, 0, 0, 0)', and A = E[g g']/2 + E[d d'/sigma^2].
    Under the null (z_t i.i.d., mean 0, variance 1), with s_u^2 = E u^2 = kappa_z - 1 and k3 = E z^3:
        Var = s_u^4 I - E[u U s'] A^{-1} H' - H A^{-1} E[s u U'] + H A^{-1} E[s s'] A^{-1} H',
        E[u U s'] = s_u^2 H / 2 + k3 E[U / sigma_t] d',  E[s s'] = s_u^2 E[g g'] / 4 + k3 E[(g d' + d g') / sigma] / 2 + E[d d'/sigma^2],
    and C = Var / s_u^4. The cross terms with the mean score (through k3, residual skewness) are included.
    'c11_var', 'q_lm_var': the variance-parameters-only version C = I - H' J^{-1} H / (kappa_z - 1), for comparison."""
    f = fit_garch(rets['sp500'], 'GARCH', 'normal')
    p = f.params
    e = (rets['sp500'] - p['mu']).values
    s2 = (f.sigma ** 2).values
    n = len(e)
    a, b = p['alpha[1]'], p['beta[1]']
    e2l = np.concatenate(([np.mean(e ** 2)], e[:-1] ** 2))
    s2l = np.concatenate(([np.mean(e ** 2)], s2[:-1]))
    el = np.concatenate(([0.0], e[:-1]))
    # d sigma_t^2 / d(mu, omega, alpha, beta): sigma_t^2 = omega + alpha e_{t-1}^2 + beta sigma_{t-1}^2, e = r - mu
    D = np.column_stack([lfilter([1.0], [1.0, -b], x) for x in (-2 * a * el, np.ones(n), e2l, s2l)])
    g = D / s2[:, None]
    sig = np.sqrt(s2)
    z = e / sig
    u = z ** 2 - 1
    s2u = np.mean(u ** 2)
    k3 = float(np.mean(z ** 3))
    dv = np.zeros((n, 4)); dv[:, 0] = 1.0
    G = g.T @ g / n
    Dd = (dv / sig[:, None]).T @ (dv / sig[:, None]) / n
    Ai = np.linalg.inv(0.5 * G + Dd)
    H = np.array([(g[k:] * u[:-k, None]).mean(axis=0) for k in range(1, M + 1)])     # M x 4
    U = np.column_stack([np.concatenate((np.zeros(k), u[:-k])) for k in range(1, M + 1)])
    EUd = (U[M:] / sig[M:, None]).mean(axis=0)                                          # E[u_{t-k} / sigma_t]
    EUs = 0.5 * s2u * H + k3 * np.outer(EUd, dv[0])
    Egd = (g / sig[:, None]).mean(axis=0)
    Ess = 0.25 * s2u * G + 0.5 * k3 * (np.outer(Egd, dv[0]) + np.outer(dv[0], Egd)) + Dd
    C = (s2u ** 2 * np.eye(M) - EUs @ Ai @ H.T - H @ Ai @ EUs.T + H @ Ai @ Ess @ Ai @ H.T) / s2u ** 2
    H3, G3 = H[:, 1:], G[1:, 1:]
    C3 = np.eye(M) - H3 @ np.linalg.solve(G3, H3.T) / s2u
    rh = np.array([np.sum(u[k:] * u[:-k]) / np.sum(u ** 2) for k in range(1, M + 1)])
    q_lb = n * (n + 2) * np.sum(rh ** 2 / (n - np.arange(1, M + 1)))
    q_lm = n * rh @ np.linalg.solve(C, rh)
    q3 = n * rh @ np.linalg.solve(C3, rh)
    INF['limak'] = {'M': M, 'c11': float(C[0, 0]), 'c55': float(C[4, 4]), 'cMM': float(C[M - 1, M - 1]),
                    'q_lb': float(q_lb), 'p_lb': float(stats.chi2.sf(q_lb, M)), 'q_lm': float(q_lm),
                    'p_lm': float(stats.chi2.sf(q_lm, M)), 'r1': float(rh[0]), 'trace_loss': float(M - np.trace(C)),
                    'joint_mu': True, 'skew_z': k3, 'c11_var': float(C3[0, 0]), 'q_lm_var': float(q3),
                    'p_lm_var': float(stats.chi2.sf(q3, M))}


def gjr_skew_persistence():
    """GJR-GARCH with skewed-t innovations (Hansen, 1994), S&P 500: E[z^2 1(z<0)] instead of 1/2."""
    f = fit_garch(rets['sp500'], 'GJR', 'skewt')
    d = f.res.model.distribution
    par = f.res.params[d.parameter_names()].values
    pdf = lambda x: float(np.exp(d.loglikelihood(par, np.array([x]), np.array([1.0]), individual=True))[0])
    m_neg = integrate.quad(lambda x: x ** 2 * pdf(x), -np.inf, 0, limit=200)[0]
    p_neg = integrate.quad(pdf, -np.inf, 0, limit=200)[0]
    p = f.params
    INF['gjrskew'] = {'alpha': float(p['alpha[1]']), 'gamma': float(p['gamma[1]']), 'beta': float(p['beta[1]']),
                      'eta': float(par[0]), 'lam': float(par[1]), 'm_neg': float(m_neg), 'p_neg': float(p_neg),
                      'pers_sym': float(p['alpha[1]'] + p['gamma[1]'] / 2 + p['beta[1]']),
                      'pers_skew': float(p['alpha[1]'] + p['gamma[1]'] * m_neg + p['beta[1]'])}


def oos_rolling(k='sp500', first_year=2016, W=1000):
    """One-day forecasts with a ROLLING window of W days, refit every January (Giacomini-White setting)."""
    r = rets[k]
    idx = r.index
    out = {lab: pd.Series(np.nan, index=idx) for *_, lab in MODELS_OOS}
    for y in range(first_year, idx[-1].year + 1):
        start = idx[idx < f'{y}-01-01'][-1]
        end = idx[idx <= f'{y}-12-31'][-1]
        orig = idx[(idx >= start) & (idx < end)]
        pos0 = idx.get_loc(start)
        sub = r.iloc[pos0 - W + 1:]
        for vol, dist, lab in MODELS_OOS:
            f = fit_garch(sub, vol, dist, last_obs=idx[pos0 + 1])
            fc = f.res.forecast(horizon=1, start=start, reindex=False).variance / f.c ** 2
            fc = fc.loc[orig]
            pos = idx.get_indexer(fc.index)
            out[lab].iloc[pos + 1] = fc.iloc[:, 0].values
    out['EWMA'] = ewma_variance(r).reindex(idx)
    out['Hist-20'] = (r ** 2).rolling(20).mean().shift(1)
    return pd.DataFrame(out).loc[f'{first_year}-01-01':].dropna()


def gw_test(la, lb):
    """Giacomini-White (2006), conditional test, horizon 1: instruments x_t = (1, d_t); GW = n Zbar' Omega^{-1} Zbar ~ chi2(2)."""
    d = np.asarray(la) - np.asarray(lb)
    Z = np.column_stack([d[1:], d[:-1] * d[1:]])
    zb = Z.mean(axis=0)
    Om = Z.T @ Z / len(Z)
    stat = len(Z) * zb @ np.linalg.solve(Om, zb)
    return float(stat), float(stats.chi2.sf(stat, 2))


def gw_mcs(k='sp500'):
    r = rets[k]
    fr = oos_rolling(k)
    proxy = (r ** 2).reindex(fr.index)
    L = pd.DataFrame({m: qlike(proxy, fr[m]) for m in fr.columns})
    rows = {}
    for m in L.columns:
        if m == 'GARCH-t':
            continue
        dm = dm_test(L[m], L['GARCH-t'])
        gw, gp = gw_test(L[m], L['GARCH-t'])
        rows[m] = {'uncond_t': dm['t'], 'gw': gw, 'gw_p': gp, 'mean_diff': dm['mean_diff']}
    # MCS on the expanding-window forecasts (the table of the lecture and seminar)
    f1, _ = oos_forecasts(k, 2016, 1)
    px = (r ** 2).reindex(f1.index)
    Le = pd.DataFrame({m: qlike(px, f1[m]) for m in f1.columns})
    mcs = MCS(Le, size=0.10, reps=10000, block_size=10, method='R', bootstrap='stationary', seed=SEED)
    mcs.compute()
    pv = mcs.pvalues['Pvalue']
    INF[f'gw_{k}'] = {'n': len(fr), 'W': 1000, 'qlike_roll': L.mean().to_dict(), 'tests': rows,
                      'mcs_p': pv.to_dict(), 'mcs_in': list(mcs.included), 'n_mcs': len(Le)}


if __name__ == '__main__':
    qmle_efficiency(); boundary_tests(); delta_method(); moments_garch_n(); li_mak(); gjr_skew_persistence()
    for k in ['sp500', 'bet']:
        print('GW / MCS', k); gw_mcs(k)
    with open(os.path.join(TABLE_DIR, 'ch5_inference.json'), 'w') as fh:
        json.dump(INF, fh, indent=1, default=float)
    print(json.dumps(INF, indent=1, default=float))

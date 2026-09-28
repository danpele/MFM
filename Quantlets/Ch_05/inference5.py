"""
inference5.py -- Inferenta asimptotica pentru modelele GARCH (Capitolul 5, MFM)
==============================================================================
  * qmle_efficiency()     -- QMLE Gaussian: raportul erorilor standard robuste / clasice si sqrt((kappa_z - 1)/2)
  * boundary_tests()      -- LR Normal vs Student-t (1/nu = 0 pe frontiera): amestecul 1/2 chi2(0) + 1/2 chi2(1)
  * delta_method()        -- metoda delta pentru volatilitatea de termen lung si timpul de injumatatire
  * moments_garch_n()     -- conditia momentului de ordin patru, aplatizarea K si rho_1(eps^2) pentru GARCH-N
  * li_mak()              -- portmanteau pe patratele reziduurilor standardizate cu parametri estimati (Li & Mak, 1994)
  * gjr_skew_persistence()-- persistenta GJR cu inovatii t asimetrice: alpha + gamma E[z^2 1(z<0)] + beta
  * gw_mcs(k)             -- Giacomini-White (fereastra mobila de 1000 de zile) si Model Confidence Set (90%) pe QLIKE

Modelarea Pietelor Financiare - Daniel Traian PELE
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
    """Gaussian QMLE: avar = (kappa_z - 1) J^{-1}; clasic (inversa hessianei) = 2 J^{-1}; raport e.s. sqrt((kappa_z-1)/2)."""
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
        # stabilitatea aplatizarii de selectie: prima jumatate vs tot esantionul
        out[k]['kappa_half'] = float(stats.kurtosis(z.iloc[:len(z) // 2], fisher=False))
    INF['qmle'] = out


def boundary_tests():
    """LR pentru Normal (1/nu = 0) fata de Student-t: 1/nu >= 0, deci limita este 1/2 chi2(0) + 1/2 chi2(1)."""
    out = {'crit_mix': float(stats.chi2.ppf(0.90, 1)), 'crit_chi2': float(stats.chi2.ppf(0.95, 1))}
    for k in ['sp500', 'btc']:
        fn, ft = fit_garch(rets[k], 'GARCH', 'normal'), fit_garch(rets[k], 'GARCH', 't')
        lr = 2 * (ft.loglik - fn.loglik)
        out[k] = {'lr': float(lr), 'p_mix': float(0.5 * stats.chi2.sf(lr, 1)), 'nu': float(ft.params['nu'])}
    g = fit_garch(rets['sp500'], 'GJR', 't')
    out['gjr_alpha'] = float(g.params['alpha[1]'])
    INF['boundary'] = out


def delta_method():
    """Metoda delta din covarianta robusta a lui (omega, alpha, beta), GARCH(1,1)-t, S&P 500."""
    f = fit_garch(rets['sp500'], 'GARCH', 't')
    p = f.params
    V = f.res.param_cov.loc[['omega', 'alpha[1]', 'beta[1]'], ['omega', 'alpha[1]', 'beta[1]']].values / f.c ** 2
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
    """GARCH(1,1) cu inovatii Normale: (alpha+beta)^2 + 2 alpha^2, K si rho_1(eps^2), la precizie completa si rotunjit."""
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
    """Autocorelatiile patratelor reziduurilor standardizate dupa QMLE Gaussian (S&P 500, GARCH-N).
    sqrt(n) r_hat -> N(0, C), C = I - H' J^{-1} H / (kappa_z - 1), cu J = E[g g'], H_k = E[g_t (z_{t-k}^2 - 1)],
    g_t = d ln sigma_t^2 / d(omega, alpha, beta) (derivarea lui Li & Mak, 1994, pentru parametrii dispersiei)."""
    f = fit_garch(rets['sp500'], 'GARCH', 'normal')
    p = f.params
    e = (rets['sp500'] - p['mu']).values
    s2 = (f.sigma ** 2).values
    n = len(e)
    e2l = np.concatenate(([np.mean(e ** 2)], e[:-1] ** 2))
    s2l = np.concatenate(([np.mean(e ** 2)], s2[:-1]))
    D = np.column_stack([lfilter([1.0], [1.0, -p['beta[1]']], x) for x in (np.ones(n), e2l, s2l)])
    g = D / s2[:, None]
    z2 = e ** 2 / s2
    u = z2 - 1
    s2u = np.mean(u ** 2)
    J = g.T @ g / n
    H = np.array([(g[k:] * u[:-k, None]).mean(axis=0) for k in range(1, M + 1)])     # M x 3
    C = np.eye(M) - H @ np.linalg.solve(J, H.T) / s2u
    rh = np.array([np.sum(u[k:] * u[:-k]) / np.sum(u ** 2) for k in range(1, M + 1)])
    q_lb = n * (n + 2) * np.sum(rh ** 2 / (n - np.arange(1, M + 1)))
    q_lm = n * rh @ np.linalg.solve(C, rh)
    INF['limak'] = {'M': M, 'c11': float(C[0, 0]), 'c55': float(C[4, 4]), 'cMM': float(C[M - 1, M - 1]),
                    'q_lb': float(q_lb), 'p_lb': float(stats.chi2.sf(q_lb, M)), 'q_lm': float(q_lm),
                    'p_lm': float(stats.chi2.sf(q_lm, M)), 'r1': float(rh[0]), 'trace_loss': float(M - np.trace(C))}


def gjr_skew_persistence():
    """GJR-GARCH cu inovatii t asimetrice (Hansen, 1994), S&P 500: E[z^2 1(z<0)] in locul lui 1/2."""
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
    """Prognoze pe o zi cu fereastra MOBILA de W zile, reestimata in fiecare ianuarie (cadrul Giacomini-White)."""
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
    """Giacomini-White (2006), test conditional, orizont 1: instrumente h_t = (1, d_t); GW = n Zbar' Omega^{-1} Zbar ~ chi2(2)."""
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
    # MCS pe prognozele cu fereastra in expansiune (tabelul din curs / seminar)
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

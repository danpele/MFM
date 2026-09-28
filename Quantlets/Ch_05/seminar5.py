"""
seminar5.py -- Cifrele Seminarului 5 (MFM): modele GARCH
=======================================================
  A1  recursia GARCH(1,1) si prognoza pas cu pas (exemplu numeric)
  B2  GJR vs GARCH pe S&P 500 si pe BET: testul raportului de verosimilitate, AIC/BIC
  B4  Bitcoin: Student-t vs t asimetric (Hansen, 1994) vs GED
  B6  BET: comparatia prognozelor (QLIKE, Diebold-Mariano, Mincer-Zarnowitz), 2016-2026
  B7/B8 bootstrap parametric: incertitudinea persistentei si a timpului de injumatatire (S&P 500, BET),
        testul IGARCH prin bootstrap sub H0
  C   Volatilitatea BET si socurile S&P 500 din ziua precedenta: GARCH-t cu regresor in varianta

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.signal import lfilter
from scipy.special import gammaln
from arch.univariate import ConstantMean, GARCH, StudentsT
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import load_close                                              # noqa: E402
from garch_tools import fit_garch, half_life, qlike, dm_test, mz_regression    # noqa: E402
from generate_all_charts import (rets, oos_forecasts, save_fig, legend_outside_bottom,   # noqa: E402
                                 MainBlue, IDAred, Amber, TABLE_DIR)

SEED = 42
OUT = {}


# -----------------------------------------------------------------------------
# A1. Recursia si prognoza pas cu pas
# -----------------------------------------------------------------------------
def a1_recursion():
    om, al, be = 0.05, 0.10, 0.85
    eps = [-2.0, 0.5, 3.0, -1.0]
    s2 = [om / (1 - al - be)]
    for e in eps:
        s2.append(om + al * e ** 2 + be * s2[-1])
    uv = om / (1 - al - be)
    last = s2[-1]
    fc = [uv + (al + be) ** (h - 1) * (last - uv) for h in range(1, 11)]
    OUT['a1'] = {'omega': om, 'alpha': al, 'beta': be, 'eps': eps, 's2': s2, 'uv': uv, 'fc': fc,
                 'hl': half_life(al + be), 'sum5': float(np.sum(fc[:5])), 'sum10': float(np.sum(fc))}


# -----------------------------------------------------------------------------
# B2/B3. GJR vs GARCH, LR
# -----------------------------------------------------------------------------
def lr_tests():
    at = pd.read_csv(os.path.join(TABLE_DIR, 'ch5_asym_table.csv'), index_col=0)
    grid = pd.read_csv(os.path.join(TABLE_DIR, 'ch5_model_grid.csv'))
    res = {}
    for k in ['sp500', 'bet']:
        sub = grid[(grid.market == k) & (grid.dist == 't')].set_index('vol')
        res[k] = {'ll_garch': sub.loc['GARCH', 'loglik'], 'll_gjr': sub.loc['GJR', 'loglik'],
                  'aic_garch': sub.loc['GARCH', 'aic'], 'aic_gjr': sub.loc['GJR', 'aic'],
                  'bic_garch': sub.loc['GARCH', 'bic'], 'bic_gjr': sub.loc['GJR', 'bic'],
                  'lr': at.loc[k, 'lr'], 'lr_p': at.loc[k, 'lr_p'], 'gamma': at.loc[k, 'gjr_gamma'],
                  'gamma_t': at.loc[k, 'gjr_gamma_t'], 'alpha': at.loc[k, 'gjr_alpha'], 'beta': at.loc[k, 'gjr_beta']}
    OUT['lr'] = res


# -----------------------------------------------------------------------------
# B4. Bitcoin: distributia inovatiilor
# -----------------------------------------------------------------------------
def btc_innovations():
    r = rets['btc']
    out = {}
    for d in ['normal', 't', 'skewt', 'ged']:
        f = fit_garch(r, 'GARCH', d)
        out[d] = {'loglik': f.loglik, 'aic': f.aic, 'bic': f.bic,
                  **{k: float(v) for k, v in f.params.items()}, 'persistence': float(f.persistence)}
        if d == 'skewt':
            out[d]['lambda_se'] = float(f.se['lambda'])
            out[d]['lambda_t'] = float(f.tvalues['lambda'])
        if d == 't':
            out[d]['nu_se'] = float(f.se['nu'])
    out['lr_skew'] = 2 * (out['skewt']['loglik'] - out['t']['loglik'])
    out['lr_skew_p'] = float(1 - stats.chi2.cdf(max(out['lr_skew'], 0), 1))
    z = fit_garch(r, 'GARCH', 't').z.dropna()
    out['z_skew'] = float(stats.skew(z))
    out['z_kurt'] = float(stats.kurtosis(z))
    OUT['btc'] = out


# -----------------------------------------------------------------------------
# B5/B6. Comparatia prognozelor
# -----------------------------------------------------------------------------
def forecast_comparison(k):
    r = rets[k]
    f1, _ = oos_forecasts(k, 2016, 1)
    proxy = (r ** 2).reindex(f1.index)
    base = qlike(proxy, f1['GARCH-t'])
    rows = {}
    for m in f1.columns:
        L = qlike(proxy, f1[m])
        dm = dm_test(L, base) if m != 'GARCH-t' else {'mean_diff': 0.0, 't': float('nan'), 'p': float('nan')}
        mz = mz_regression(proxy, f1[m])
        rows[m] = {'qlike': float(L.mean()), 'dm_diff': dm['mean_diff'], 'dm_t': dm['t'], 'dm_p': dm['p'],
                   'mz_a': mz['a'], 'mz_b': mz['b'], 'mz_b_se': mz['b_se'], 'mz_r2': mz['r2'], 'mz_wald_p': mz['wald_p']}
    OUT[f'fc_{k}'] = {'n': len(f1), 'start': str(f1.index[0].date()), 'models': rows}


# -----------------------------------------------------------------------------
# B7/B8. Bootstrap parametric si testul IGARCH simulat sub H0
# -----------------------------------------------------------------------------
def tgarch_negll(theta, r, igarch=False):
    """Minus log-verosimilitatea GARCH(1,1)-t cu medie constanta mu.
    Parametrizare: p = alpha + beta in [0, 1], s = alpha / p in [0, 1]; IGARCH: p = 1.
    Pornirea ca in arch: sigma^2_0 = eps^2_0 = media ponderata EWMA (0.94) a primelor 75 de patrate."""
    if igarch:
        mu, om, s, nu = theta
        p = 1.0
    else:
        mu, om, p, s, nu = theta
    e = r - mu
    al, be = p * s, p * (1 - s)
    w = 0.94 ** np.arange(75)
    bc = np.sum(e[:75] ** 2 * w) / w.sum()
    drive = om + al * np.concatenate(([bc], e[:-1] ** 2))
    s2 = lfilter([1.0], [1.0, -be], drive, zi=[be * bc])[0]
    z2 = e ** 2 / s2
    ll = (gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(np.pi * (nu - 2)) - 0.5 * np.log(s2)
          - (nu + 1) / 2 * np.log1p(z2 / (nu - 2)))
    return -ll.sum()


def fit_tgarch(r, igarch=False, start=None):
    """GARCH(1,1)-t (sau IGARCH(1,1)-t, alpha + beta = 1) prin verosimilitate proprie, cu restrictia alpha + beta <= 1.
    Modelul nerestrictionat se porneste si din solutia IGARCH: l_GARCH >= l_IGARCH, deci LR >= 0."""
    r = np.asarray(r, dtype=float)
    m, v = np.mean(r), np.var(r)
    opts = {'ftol': 1e-12, 'gtol': 1e-7, 'maxiter': 3000}
    if igarch:
        x0 = [m, 0.01 * v, 0.1, 6.0] if start is None else start
        bnd = [(None, None), (1e-8 * v, 10 * v), (1e-4, 1.0), (2.05, 200.0)]
        o = optimize.minimize(tgarch_negll, x0, args=(r, True), method='L-BFGS-B', bounds=bnd, options=opts)
        mu, om, s, nu = o.x
        return {'mu': mu, 'omega': om, 'alpha': s, 'beta': 1 - s, 'nu': nu, 'pers': 1.0, 'loglik': -o.fun}
    g = fit_tgarch(r, igarch=True)
    bnd = [(None, None), (1e-8 * v, 10 * v), (0.0, 1.0), (1e-4, 1.0), (2.05, 200.0)]
    starts = [[m, 0.01 * v, 0.98, 0.1, 6.0], [g['mu'], g['omega'], 0.999, g['alpha'], g['nu']]]
    if start is not None:
        starts.append(start)
    best = min((optimize.minimize(tgarch_negll, x0, args=(r, False), method='L-BFGS-B', bounds=bnd, options=opts)
                for x0 in starts), key=lambda o: o.fun)
    mu, om, p, s, nu = best.x
    return {'mu': mu, 'omega': om, 'alpha': p * s, 'beta': p * (1 - s), 'nu': nu, 'pers': p,
            'loglik': max(-best.fun, g['loglik']), 'loglik_igarch': g['loglik']}


def sim_tgarch(par, n, B, rng, s2_start, burn=500):
    """B traiectorii GARCH(1,1)-t simultan (vectorizat pe coloane); functioneaza si pentru alpha + beta = 1."""
    nu = par['nu']
    z = rng.standard_t(nu, size=(n + burn, B)) * np.sqrt((nu - 2) / nu)
    s2 = np.full(B, s2_start)
    out = np.empty((n + burn, B))
    for t in range(n + burn):
        e = np.sqrt(s2) * z[t]
        out[t] = e
        s2 = par['omega'] + par['alpha'] * e ** 2 + par['beta'] * s2
    return par['mu'] + out[burn:]


def param_bootstrap(k, B=999):
    """Bootstrap parametric: B traiectorii din GARCH(1,1)-t estimat, reestimate; intervale percentile."""
    from joblib import Parallel, delayed
    r = rets[k]
    f = fit_garch(r, 'GARCH', 't')
    p = f.params
    par = {'mu': p['mu'], 'omega': p['omega'], 'alpha': p['alpha[1]'], 'beta': p['beta[1]'], 'nu': p['nu']}
    rng = np.random.default_rng(SEED)
    sims = sim_tgarch(par, len(r), B, rng, r.var())
    st = [par['mu'], par['omega'], par['alpha'] + par['beta'], par['alpha'] / (par['alpha'] + par['beta']), par['nu']]
    fits = Parallel(n_jobs=-1)(delayed(fit_tgarch)(sims[:, b], False, st) for b in range(B))
    pers = np.array([x['pers'] for x in fits])
    hls = np.array([half_life(x) for x in pers])
    hq = np.sort(np.where(np.isfinite(hls), hls, 1e9))
    est = p['alpha[1]'] + p['beta[1]']
    OUT[f'boot_{k}'] = {'B': B, 'est': float(est), 'hl': float(half_life(est)),
                        'pers_lo': float(np.quantile(pers, 0.025)), 'pers_hi': float(np.quantile(pers, 0.975)),
                        'pers_sd': float(pers.std()), 'pers_mean': float(pers.mean()),
                        'hl_lo': float(np.quantile(hq, 0.025)), 'hl_med': float(np.median(hq)),
                        'hl_hi': float(np.quantile(hq, 0.975)), 'share_inf': float((pers >= 1 - 1e-6).mean()),
                        'share_ge_0999': float((pers >= 0.999).mean()),
                        'se_robust_sum': float(np.sqrt(f.res.param_cov.loc[['alpha[1]', 'beta[1]'], ['alpha[1]', 'beta[1]']].values.sum()))}
    return pers, hls


def _null_rep(y):
    ub = fit_tgarch(y)
    return ub['pers'], 2 * (ub['loglik'] - ub['loglik_igarch'])


def igarch_test(k, B=999):
    """Testul H0: alpha + beta = 1 (IGARCH) prin bootstrap parametric SUB H0 (Andrews, 2000: un interval percentile
    trunchiat la 1 nu este un test valid). Statistici: persistenta estimata si LR = 2(l_GARCH - l_IGARCH)."""
    from joblib import Parallel, delayed
    r = rets[k]
    u = fit_tgarch(r)
    g0 = fit_tgarch(r, igarch=True)
    lr = 2 * (u['loglik'] - g0['loglik'])
    rng = np.random.default_rng(SEED + 1)
    sims = sim_tgarch(g0, len(r), B, rng, r.var())
    res = Parallel(n_jobs=-1)(delayed(_null_rep)(sims[:, b]) for b in range(B))
    pb, lrb = np.array([x[0] for x in res]), np.array([x[1] for x in res])
    OUT[f'igarch_{k}'] = {'B': B, 'pers': u['pers'], 'alpha0': g0['alpha'], 'omega0': g0['omega'], 'nu0': g0['nu'],
                          'lr': lr, 'p_chi2': float(stats.chi2.sf(lr, 1)), 'p_mix': float(0.5 * stats.chi2.sf(lr, 1)),
                          'p_boot_pers': float((1 + np.sum(pb <= u['pers'])) / (B + 1)),
                          'p_boot_lr': float((1 + np.sum(lrb >= lr)) / (B + 1)),
                          'share_bound': float(np.mean(pb >= 0.999)), 'lr_q95': float(np.quantile(lrb, 0.95)),
                          'pers_q05': float(np.quantile(pb, 0.05))}
    return pb


def fig_bootstrap(boots, nulls):
    """Distributia bootstrap a persistentei: din modelul estimat si sub H0 (IGARCH)."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, (k, lab, col) in zip(axes, [('sp500', 'S&P 500', MainBlue), ('bet', 'BET', IDAred)]):
        bins = np.linspace(min(boots[k].min(), nulls[k].min()), 1.0, 40)
        ax.hist(boots[k], bins=bins, color=col, alpha=0.75, label=f'{lab}: fitted GARCH-t (B = {len(boots[k])})')
        ax.hist(nulls[k], bins=bins, color=Amber, alpha=0.6, label=f'{lab}: IGARCH-t under H0 (B = {len(nulls[k])})')
        ax.axvline(OUT[f'boot_{k}']['est'], color='black', lw=1, label='Estimate on the data')
        ax.set_xlabel(r'$\hat\alpha+\hat\beta$')
        legend_outside_bottom(ax, ncol=1, y=-0.2)
    fig.tight_layout()
    save_fig('ch5_sem_bootstrap')


# -----------------------------------------------------------------------------
# C. BET si socurile S&P 500: GARCH-t cu regresor in varianta (verosimilitate proprie)
# -----------------------------------------------------------------------------
def join_bet_sp():
    """Join pe PRETURI in zilele comune, apoi randamente; socul american relevant pentru BET in ziua t
    este randamentul S&P 500 din ziua comuna precedenta (bursa americana inchide dupa BVB)."""
    px = pd.concat([load_close('bet'), load_close('sp500')], axis=1, join='inner').dropna()
    ret = 100 * np.log(px).diff().dropna()
    df = pd.DataFrame({'bet': ret['bet'], 'us_lag': ret['sp500'].shift(1)}).dropna()
    return df


def spill_negll(theta, y, x, delta_free=True):
    mu, phi, lw, la, lb, ld, lnu = theta
    om, al, be = np.exp(lw), np.exp(la), np.exp(lb)
    de = np.exp(ld) if delta_free else 0.0
    nu = 2.05 + np.exp(lnu)
    if al + be >= 0.9999:
        return 1e10
    e = y - mu - phi * x
    n = len(y)
    # s2_t = beta s2_{t-1} + (omega + alpha e_{t-1}^2 + delta x_{t-1}^2): filtru liniar recursiv
    drive = np.empty(n)
    drive[0] = np.var(y) * (1 - be)
    drive[1:] = om + al * e[:-1] ** 2 + de * x[:-1] ** 2
    s2 = lfilter([1.0], [1.0, -be], drive)
    z2 = e ** 2 / s2
    ll = (gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(np.pi * (nu - 2)) - 0.5 * np.log(s2)
          - (nu + 1) / 2 * np.log1p(z2 / (nu - 2)))
    return -ll.sum()


def fit_spill(df, delta_free=True):
    y, x = df['bet'].values, df['us_lag'].values
    th0 = np.array([0.05, 0.1, np.log(0.03), np.log(0.15), np.log(0.8), np.log(0.02), np.log(3.0)])
    best = None
    for start_ld in [np.log(0.02), np.log(0.1)]:
        th0[5] = start_ld
        o = optimize.minimize(spill_negll, th0, args=(y, x, delta_free), method='Nelder-Mead',
                              options={'maxiter': 20000, 'maxfev': 20000, 'xatol': 1e-7, 'fatol': 1e-7})
        o = optimize.minimize(spill_negll, o.x, args=(y, x, delta_free), method='L-BFGS-B')
        if best is None or o.fun < best.fun:
            best = o
    th = best.x
    par = {'mu': th[0], 'phi': th[1], 'omega': np.exp(th[2]), 'alpha': np.exp(th[3]), 'beta': np.exp(th[4]),
           'delta': np.exp(th[5]) if delta_free else 0.0, 'nu': 2.05 + np.exp(th[6]), 'loglik': -best.fun}
    return par


def spill_path(df, par):
    """Dispersia conditionata a BET si partea datorata socului american din ziua precedenta."""
    y, x = df['bet'].values, df['us_lag'].values
    e = y - par['mu'] - par['phi'] * x
    n = len(y)
    drive = np.empty(n)
    drive[0] = np.var(y) * (1 - par['beta'])
    drive[1:] = par['omega'] + par['alpha'] * e[:-1] ** 2 + par['delta'] * x[:-1] ** 2
    s2 = lfilter([1.0], [1.0, -par['beta']], drive)
    us = np.zeros(n)
    us[1:] = par['delta'] * x[:-1] ** 2
    us_total = lfilter([1.0], [1.0, -par['beta']], us)      # contributia cumulata a socurilor americane
    return pd.DataFrame({'s2': s2, 'us': us_total}, index=df.index)


def part_c():
    df = join_bet_sp()
    res = {'n': len(df), 'start': str(df.index[0].date()), 'end': str(df.index[-1].date()),
           'corr_same': float(np.corrcoef(df['bet'], df['us_lag'])[0, 1])}
    for name, sub in [('full', df), ('pre2013', df.loc[:'2012-12-31']), ('post2013', df.loc['2013-01-01':])]:
        u = fit_spill(sub, True)
        rr = fit_spill(sub, False)
        lr = 2 * (u['loglik'] - rr['loglik'])
        # delta >= 0: sub ipoteza nula parametrul este pe frontiera -> 0.5 chi2(0) + 0.5 chi2(1)
        p = 0.5 * (1 - stats.chi2.cdf(max(lr, 0), 1))
        x2 = (sub['us_lag'] ** 2).mean()
        share = u['delta'] * x2 / (u['omega'] + u['delta'] * x2)
        res[name] = {'u': u, 'r': rr, 'lr': lr, 'p': p, 'n': len(sub), 'share_intercept': share}
        if name == 'full':
            path = spill_path(sub, u)
    share = (path['us'] / path['s2']).clip(0, 1)
    res['share_mean'] = float(share.mean())
    m = share.resample('YE').mean()
    res['share_max_year'] = int(m.idxmax().year)
    res['share_max'] = float(m.max())
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(share.index, share.rolling(63).mean(), color=IDAred, lw=0.9,
            label='Share of BET conditional variance due to lagged S&P 500 shocks (3-month average)')
    ax.set_ylabel('Share')
    ax.set_ylim(0, None)
    legend_outside_bottom(ax, ncol=1, y=-0.15)
    save_fig('ch5_sem_spillover')
    OUT['partc'] = res


if __name__ == '__main__':
    a1_recursion(); lr_tests(); btc_innovations()
    print('forecast comparison'); forecast_comparison('sp500'); forecast_comparison('bet')
    print('bootstrap'); boots = {k: param_bootstrap(k)[0] for k in ['sp500', 'bet']}
    nulls = {k: igarch_test(k) for k in ['sp500', 'bet']}; fig_bootstrap(boots, nulls)
    print('part C'); part_c()
    with open(os.path.join(HERE, 'ch5_seminar_numbers.json'), 'w') as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print(json.dumps(OUT, indent=1, default=float))

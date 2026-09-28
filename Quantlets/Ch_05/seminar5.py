"""
seminar5.py -- Cifrele Seminarului 5 (MFM): modele GARCH
=======================================================
  A1  recursia GARCH(1,1) si prognoza pas cu pas (exemplu numeric)
  B2  GJR vs GARCH pe S&P 500 si pe BET: testul raportului de verosimilitate, AIC/BIC
  B4  Bitcoin: Student-t vs t asimetric (Hansen, 1994) vs GED
  B6  BET: comparatia prognozelor (QLIKE, Diebold-Mariano, Mincer-Zarnowitz), 2016-2026
  B7/B8 bootstrap parametric: incertitudinea persistentei si a timpului de injumatatire (S&P 500, BET)
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
                                 MainBlue, IDAred, TABLE_DIR)

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
# B7/B8. Bootstrap parametric
# -----------------------------------------------------------------------------
def param_bootstrap(k, B=200):
    r = rets[k]
    f = fit_garch(r, 'GARCH', 't')
    p = f.params
    n = len(r)
    rng = np.random.default_rng(SEED)
    pers, hls, alphas = [], [], []
    for b in range(B):
        mod = ConstantMean(None, volatility=GARCH(), distribution=StudentsT(seed=rng))
        sim = mod.simulate([p['mu'], p['omega'], p['alpha[1]'], p['beta[1]'], p['nu']], nobs=n, burn=500)['data']
        fb = fit_garch(pd.Series(sim.values), 'GARCH', 't', c=1.0)
        pb = fb.params['alpha[1]'] + fb.params['beta[1]']
        pers.append(pb)
        alphas.append(fb.params['alpha[1]'])
        hls.append(half_life(pb))
    pers, hls = np.minimum(np.array(pers), 1.0), np.array(hls)
    hq = np.sort(np.where(np.isfinite(hls), hls, 1e9))
    est = p['alpha[1]'] + p['beta[1]']
    OUT[f'boot_{k}'] = {'B': B, 'est': float(est), 'hl': float(half_life(est)),
                        'pers_lo': float(np.quantile(pers, 0.025)), 'pers_hi': float(np.quantile(pers, 0.975)),
                        'pers_sd': float(pers.std()), 'pers_mean': float(pers.mean()),
                        'hl_lo': float(hq[int(0.025 * B)]), 'hl_med': float(np.median(hq)),
                        'hl_hi': float(hq[int(0.975 * B) - 1]), 'share_inf': float((~np.isfinite(hls)).mean()), 'share_ge_0999': float((pers >= 0.999).mean()),
                        'se_robust_sum': float(np.sqrt(f.res.param_cov.loc[['alpha[1]', 'beta[1]'], ['alpha[1]', 'beta[1]']].values.sum()))}
    return pers, hls


def fig_bootstrap(boots):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, (k, lab, col) in zip(axes, [('sp500', 'S&P 500', MainBlue), ('bet', 'BET', IDAred)]):
        pers = boots[k]
        ax.hist(pers, bins=30, color=col, alpha=0.8, label=f'{lab}: bootstrap estimates of alpha+beta (B = {len(pers)})')
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
    print('bootstrap'); boots = {k: param_bootstrap(k)[0] for k in ['sp500', 'bet']}; fig_bootstrap(boots)
    print('part C'); part_c()
    with open(os.path.join(HERE, 'ch5_seminar_numbers.json'), 'w') as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print(json.dumps(OUT, indent=1, default=float))

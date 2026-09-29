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
  seminar_charts()  graficele ch5_sem_* pentru fiecare rezolvare (A1-A6, B1-B8, C1-C3) si cifrele lor
                    (ch5_seminar_charts.json); extragerile bootstrap se pastreaza in ch5_sem_draws.npz
Rulare: python seminar5.py (tot) sau python seminar5.py charts [quick] (doar graficele, din cifrele salvate)

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
from mfm_data import load_close, read_market, MARKETS, END                   # noqa: E402
from case_study5 import qsd_data, fit_qsd, qsd_filter, QSD_STOCKS             # noqa: E402
from garch_tools import fit_garch, half_life, qlike, dm_test, mz_regression    # noqa: E402
from generate_all_charts import (rets, oos_forecasts, save_fig, legend_outside_bottom,   # noqa: E402
                                 MainBlue, IDAred, Amber, TABLE_DIR)
from generate_all_charts import Forest, Orange, Purple, Teal, Gray, LightGray, acf, PPY   # noqa: E402
from garch_tools import news_impact                                            # noqa: E402

SEED = 42
OUT = {}
DRAWS = {}                     # bootstrap draws kept for the seminar charts (B7/B8)


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
    hq = np.sort(hls)                                          # np.inf pastrat: persistenta la limita 1
    DRAWS[f'boot_pers_{k}'] = pers
    est = p['alpha[1]'] + p['beta[1]']
    OUT[f'boot_{k}'] = {'B': B, 'est': float(est), 'hl': float(half_life(est)),
                        'pers_lo': float(np.quantile(pers, 0.025)), 'pers_hi': float(np.quantile(pers, 0.975)),
                        'pers_sd': float(pers.std()), 'pers_mean': float(pers.mean()),
                        'hl_lo': float(np.quantile(hq, 0.025)), 'hl_med': float(np.median(hq)),
                        # h(p) este crescatoare: capatul superior este h(cuantila 97,5% a lui p), infinit daca p = 1
                        'hl_hi': float(half_life(np.quantile(pers, 0.975))), 'share_inf': float((pers >= 1 - 1e-6).mean()),
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
    DRAWS[f'null_pers_{k}'], DRAWS[f'null_lr_{k}'] = pb, lrb
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
    # s2_t = beta s2_{t-1} + (omega + alpha e_{t-1}^2 + delta u_{t-1}^2): filtru liniar recursiv;
    # x_t = u_{t-1} (randamentul S&P 500 din ziua comuna precedenta), deci regresorul din dispersie este x_t^2
    drive = np.empty(n)
    drive[0] = np.var(y) * (1 - be)
    drive[1:] = om + al * e[:-1] ** 2 + de * x[1:] ** 2
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
    drive[1:] = par['omega'] + par['alpha'] * e[:-1] ** 2 + par['delta'] * x[1:] ** 2
    s2 = lfilter([1.0], [1.0, -par['beta']], drive)
    us = np.zeros(n)
    us[1:] = par['delta'] * x[1:] ** 2
    # contributia cumulata a termenului american prin recursia beta: sum_j beta^j delta u_{t-1-j}^2
    us_total = lfilter([1.0], [1.0, -par['beta']], us)
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
            label='Model-based share of BET conditional variance generated by the lagged S&P 500 term (3-month average)')
    ax.set_ylabel('Share')
    ax.set_ylim(0, None)
    legend_outside_bottom(ax, ncol=1, y=-0.15)
    save_fig('ch5_sem_spillover')
    OUT['partc'] = res


# =============================================================================
# GRAFICELE SEMINARULUI: cel putin unul pentru fiecare rezolvare (derivari A, calcule B, proiecte C)
# Cifrele folosite pe slide-uri se salveaza in ch5_seminar_charts.json (CH).
# =============================================================================
CH = {}
DRAW_FILE = os.path.join(HERE, 'ch5_sem_draws.npz')
INF_FILE = os.path.join(HERE, 'ch5_inference.json')


def _fig_legend(fig, axes, ncol=3, y=0.0):
    """Legenda comuna, in afara graficului, jos (fara duplicate)."""
    h, l = [], []
    for ax in np.atleast_1d(axes):
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l and not ll.startswith('_'):
                h.append(hh); l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def _inf():
    """Rezultatele din inference5.py (local sau din repository-ul cursului)."""
    if os.path.exists(INF_FILE):
        with open(INF_FILE) as fh:
            return json.load(fh)
    import urllib.request
    url = 'https://raw.githubusercontent.com/danpele/MFM/main/Quantlets/Ch_05/MFM_ch5_inference/ch5_inference.json'
    return json.loads(urllib.request.urlopen(url, timeout=60).read().decode())


def setup_check():
    """Fisierele, filtrele si primele randamente (slide-ul de pregatire)."""
    out = {}
    for k in ['sp500', 'bet', 'btc']:
        sym, _, group, start = MARKETS[k]
        raw = read_market(sym)['close'].loc[start:END]
        wk = raw[raw.index.dayofweek < 5] if group != 'Crypto' else raw
        kept = load_close(k)
        r = rets[k]
        out[k] = {'file': sym, 'rows_raw': int(len(raw)), 'weekday_rows': int(len(wk)),
                  'dropped_unchanged': int(len(wk) - len(kept)), 'n_prices': int(len(kept)), 'n_returns': int(len(r)),
                  'first_price_date': str(kept.index[0].date()), 'first_return_date': str(r.index[0].date()),
                  'last_date': str(r.index[-1].date()), 'first_returns': [float(x) for x in r.iloc[:3]],
                  'first_return_dates': [str(d.date()) for d in r.index[:3]], 'ppy': float(PPY[k])}
    CH['setup'] = out


# ---------------------------------------------------------------- A1
def fig_a1():
    a = OUT['a1']
    eps, s2, uv, fc = np.array(a['eps']), np.array(a['s2']), a['uv'], np.array(a['fc'])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    d = np.arange(1, 5)
    ax.bar(d[eps < 0], eps[eps < 0], width=0.5, color=IDAred, label=r'Negative shock $\varepsilon_t$')
    ax.bar(d[eps >= 0], eps[eps >= 0], width=0.5, color=MainBlue, label=r'Positive shock $\varepsilon_t$')
    for x, e in zip(d, eps):
        ax.text(x, e + (0.15 if e >= 0 else -0.35), f'{e:+.1f}', ha='center', color='black', fontsize=10.5)
    ax.set_ylim(-2.8, 3.6)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(d)
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Shock (%)')
    ax.set_title('Input: four shocks', color='black')
    ax = axes[1]
    t = np.arange(1, 6)
    ax.plot(t, s2, 'o-', color=Forest, label=r'Filtered variance $\sigma_t^2$')
    ax.axhline(uv, color=Gray, ls='--', lw=0.8, label=r'Long-run variance $\bar\sigma^2 = 1$')
    for x, v in zip(t, s2):
        ax.text(x, v + 0.07, f'{v:.4f}', ha='center', color='black', fontsize=10.5)
    ax.axvline(4.5, color=Gray, lw=0.6, ls=':')
    ax.text(1.0, s2.max() + 0.3, r'$\sigma_5^2$ is known at the close of day 4', color='black', fontsize=10.5, va='top', ha='left')
    ax.set_xticks(t)
    ax.set_xlabel('Day $t$')
    ax.set_ylabel(r'Variance (%$^2$)')
    ax.set_ylim(0.6, s2.max() + 0.35)
    ax.set_title(r'Output: $\sigma_{t}^2 = \omega + \alpha\varepsilon_{t-1}^2 + \beta\sigma_{t-1}^2$', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=4)
    save_fig('ch5_sem_a1_recursion')

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    h = np.arange(1, len(fc) + 1)
    ax.plot(h, fc, 'o-', color=Forest, label=r'Forecast $E_4\sigma_{4+h}^2$')
    ax.axhline(uv, color=Gray, ls='--', lw=0.8, label=r'Long-run variance $\bar\sigma^2$')
    for x, v in zip(h[:5], fc[:5]):
        ax.text(x, v + 0.04, f'{v:.3f}', ha='center', color='black', fontsize=10.5)
    ax.set_xlabel('Horizon $h$ (days after day 4)')
    ax.set_ylabel(r'Variance (%$^2$)')
    ax.set_title(r'The gap to $\bar\sigma^2$ shrinks by $p = 0.95$ per day', color='black')
    ax = axes[1]
    V = np.cumsum(fc)
    ax.plot(h, V, 'o-', color=MainBlue, label=r'$V_H = \sum_{h \leq H} E_4\sigma_{4+h}^2$')
    ax.plot(h, h * fc[0], '--', color=IDAred, label=r'Square-root-of-time rule $H\sigma_5^2$')
    ax.plot(h, h * uv, ':', color=Amber, lw=1.6, label=r'$H\bar\sigma^2$')
    ax.annotate(f'$V_5$ = {V[4]:.3f}', (5, V[4]), (5.6, V[4] - 1.2), color='black', fontsize=10.5,
                arrowprops=dict(arrowstyle='->', color='black', lw=0.6))
    ax.annotate(f'$5\\sigma_5^2$ = {5 * fc[0]:.3f}', (5, 5 * fc[0]), (2.0, 5 * fc[0] + 1.3), color='black', fontsize=10.5,
                arrowprops=dict(arrowstyle='->', color='black', lw=0.6))
    ax.set_xlabel('Horizon $H$ (days)')
    ax.set_ylabel(r'Cumulative variance (%$^2$)')
    ax.set_title('Five-day risk: the rule overstates after turbulence', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=3)
    save_fig('ch5_sem_a1_forecast')


# ---------------------------------------------------------------- A2
def fig_a2():
    from arch.univariate import SkewStudent
    from scipy import integrate
    g = _inf()['gjrskew']
    par = np.array([g['eta'], g['lam']])
    d = SkewStudent()
    pdf = lambda x: np.exp(d.loglikelihood(par, np.atleast_1d(x), np.ones_like(np.atleast_1d(x, ), dtype=float),  # noqa: E731
                                           individual=True))
    m_neg = integrate.quad(lambda x: x ** 2 * pdf(x)[0], -np.inf, 0, limit=200)[0]
    p_neg = integrate.quad(lambda x: pdf(x)[0], -np.inf, 0, limit=200)[0]
    tot = integrate.quad(lambda x: pdf(x)[0], -np.inf, np.inf, limit=200)[0]
    var = integrate.quad(lambda x: x ** 2 * pdf(x)[0], -np.inf, np.inf, limit=200)[0]
    assert abs(m_neg - g['m_neg']) < 1e-6 and abs(p_neg - g['p_neg']) < 1e-6
    CH['a2'] = {'m_neg': m_neg, 'p_neg': p_neg, 'total_prob': tot, 'variance': var,
                'hl_skew': float(half_life(g['pers_skew'])), 'hl_sym': float(half_life(g['pers_sym']))}
    z = np.linspace(-6, 6, 601)
    f = pdf(z)
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2))
    ax = axes[0]
    ax.plot(z, f, color=MainBlue, label=r'Skewed-t density $f(z)$, $\hat\eta$ = %.2f, $\hat\lambda$ = %.3f' % (g['eta'], g['lam']))
    ax.fill_between(z[z <= 0], f[z <= 0], color=IDAred, alpha=0.3, label=f'$P(z<0)$ = {p_neg:.3f}')
    ax.set_xlabel('$z$')
    ax.set_title(r'Probability of a negative shock', color='black')
    ax = axes[1]
    ax.plot(z, z ** 2 * f, color=Purple, label=r'$z^2 f(z)$ (integrates to 1)')
    ax.fill_between(z[z <= 0], (z ** 2 * f)[z <= 0], color=Amber, alpha=0.45, label=f'$m_-$ = {m_neg:.4f}')
    ax.set_xlabel('$z$')
    ax.set_title(r'Share of the variance from $z<0$', color='black')
    ax = axes[2]
    hh = np.arange(0, 401)
    ax.plot(hh, g['pers_skew'] ** hh, color=MainBlue,
            label=r'$\alpha + \gamma m_- + \beta$ = %.4f, half-life %.0f days' % (g['pers_skew'], CH['a2']['hl_skew']))
    ax.plot(hh, g['pers_sym'] ** hh, color=IDAred, ls='--',
            label=r'$\alpha + \gamma/2 + \beta$ = %.4f, half-life %.0f days' % (g['pers_sym'], CH['a2']['hl_sym']))
    ax.axhline(0.5, color=Gray, lw=0.6, ls=':')
    ax.set_xlabel('Horizon $h$ (days)')
    ax.set_ylabel('Share of a variance shock left')
    ax.set_title('Persistence with $m_-$ or with 1/2', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=3)
    save_fig('ch5_sem_a2_skewt')


# ---------------------------------------------------------------- A3
def a3_covariance():
    f = fit_garch(rets['sp500'], 'GARCH', 't')
    names = ['omega', 'alpha[1]', 'beta[1]']
    V = f.res.param_cov.loc[names, names].values / f.c ** 2
    p = f.params
    CH['a3'] = {'omega': float(p['omega']), 'alpha': float(p['alpha[1]']), 'beta': float(p['beta[1]']),
                'V': V.tolist(), 'se': np.sqrt(np.diag(V)).tolist(), 'se_p': float(np.sqrt(V[1:, 1:].sum()))}


def fig_a3():
    dl = _inf()['delta']
    om = CH['a3']['omega']
    ph, se, lo, hi, hl = dl['pers'], dl['se_p'], dl['p_lo'], dl['p_hi'], dl['hl']
    p = np.linspace(0.975, 0.99995, 800)
    h = np.log(0.5) / np.log(p)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4))
    ax = axes[0]
    ax.plot(p, h, color=MainBlue, label=r'Half-life $h(p) = \ln 0.5/\ln p$')
    ax.plot(p, hl + dl['dh'] * (p - ph), color=IDAred, ls='--', label='Delta-method tangent at $\\hat p$')
    ax.axvspan(lo, 1.0, color=Amber, alpha=0.18, label=r'95%% interval for $p$: [%.4f; %.4f]' % (lo, hi))
    ax.axvline(1.0, color=Gray, lw=0.7, ls=':')
    ax.plot([ph], [hl], 'o', color='black', label=r'$\hat p$ = %.4f, $\hat h$ = %.0f days' % (ph, hl))
    ax.plot([lo], [dl['hl_lo']], 's', color=Forest, label=r'$h$(lower end) = %.0f days' % dl['hl_lo'])
    ax.annotate('upper end > 1:\nno finite upper bound', (0.9995, 1300), (0.9805, 1250), color='black', fontsize=10.5,
                arrowprops=dict(arrowstyle='->', color='black', lw=0.6))
    ax.set_ylim(-300, 1500)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel(r'Persistence $p = \alpha + \beta$')
    ax.set_ylabel('Days')
    ax.set_title('Half-life: the tangent goes negative', color='black')
    ax = axes[1]
    v = np.sqrt(PPY['sp500'] * om / (1 - p))
    ax.plot(p, v, color=Purple, label=r'Long-run volatility $\sqrt{q\,\hat\omega/(1-p)}$, $\hat\omega$ fixed')
    ax.axvspan(lo, 1.0, color=Amber, alpha=0.18)
    ax.plot([ph], [dl['vol']], 'o', color='black', label=r'Estimate %.1f%% p.a. (s.e. %.1f)' % (dl['vol'], dl['se_vol']))
    ax.set_ylim(0, 80)
    ax.set_xlabel(r'Persistence $p = \alpha + \beta$')
    ax.set_ylabel('% per year')
    ax.set_title('Long-run volatility: division by $1 - p$', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=3)
    save_fig('ch5_sem_a3_halflife')


# ---------------------------------------------------------------- A4
def fig_a4():
    mo = _inf()['mom']
    gt = pd.read_csv(os.path.join(TABLE_DIR, 'ch5_garch_table.csv'), index_col=0).loc['sp500']
    a, b = mo['alpha'], mo['beta']
    nu = gt['nu']
    kz = 3 * (nu - 2) / (nu - 4)
    K = lambda al, be: 3 * (1 - (al + be) ** 2) / (1 - (al + be) ** 2 - 2 * al ** 2)  # noqa: E731
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4))
    ax = axes[0]
    for be, col, ls, lab in [(b, MainBlue, '-', r'$\beta$ = %.4f (full precision)' % b),
                             (round(b, 3), IDAred, '--', r'$\beta$ = %.3f (rounded)' % round(b, 3))]:
        astar = (-be + np.sqrt(3 - 2 * be ** 2)) / 3
        al = np.linspace(0.05, astar - 1e-5, 500)
        ax.plot(al, K(al, be), color=col, ls=ls, label='Implied kurtosis $K$, ' + lab)
        ax.axvline(astar, color=col, lw=0.6, ls=':')
    ax.plot([a], [K(a, b)], 'o', color=MainBlue, label=r'$\hat\alpha$ = %.4f: $K$ = %.1f' % (a, K(a, b)))
    ax.plot([round(a, 3)], [K(round(a, 3), round(b, 3))], 's', color=IDAred,
            label=r'rounded $\hat\alpha$ = %.3f: $K$ = %.1f' % (round(a, 3), K(round(a, 3), round(b, 3))))
    ax.set_ylim(0, 40)
    ax.set_xlim(0.05, 0.135)
    ax.set_xlabel(r'$\alpha$ (GARCH-N, $\beta$ fixed)')
    ax.set_ylabel('Kurtosis of returns')
    ax.set_title('Near the moment boundary, $K$ explodes', color='black')
    ax = axes[1]
    al = np.linspace(0, 0.2, 400)
    ax.plot(al, (al + b) ** 2 + 2 * al ** 2, color=MainBlue, label=r'Normal $z_t$: $(\alpha+\beta)^2 + 2\alpha^2$')
    bt = gt['beta']
    ax.plot(al, (al + bt) ** 2 + (kz - 1) * al ** 2, color=Forest, ls='-.',
            label=r'Student-t, $\hat\nu$ = %.2f: $(\alpha+\beta)^2 + (\kappa_z - 1)\alpha^2$' % nu)
    ax.axhline(1, color=Gray, lw=0.7, ls='--')
    ct = (gt['alpha'] + bt) ** 2 + (kz - 1) * gt['alpha'] ** 2
    ax.plot([a], [(a + b) ** 2 + 2 * a ** 2], 'o', color=MainBlue, label='GARCH-N estimate: %.4f < 1' % ((a + b) ** 2 + 2 * a ** 2))
    ax.plot([gt['alpha']], [ct], 'D', color=Forest, label='GARCH-t estimate: %.4f > 1 (no finite $K$)' % ct)
    ax.set_ylim(0.9, 1.1)
    ax.set_xlabel(r'$\alpha$ ($\beta$ fixed at its estimate)')
    ax.set_ylabel('Fourth-moment condition')
    ax.set_title('Finite fourth moment only below 1', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=2)
    save_fig('ch5_sem_a4_kurtosis')
    CH['a4'] = {'kz_t': float(kz), 'cond_t': float(ct)}


# ---------------------------------------------------------------- A5
def fig_a5():
    q = _inf()['qmle']['sp500']
    nu = np.linspace(4.05, 30, 600)
    kz = 3 * (nu - 2) / (nu - 4)
    r = np.sqrt((kz - 1) / 2)
    nu0 = 6.26
    k0 = 3 * (nu0 - 2) / (nu0 - 4)
    fig, ax = plt.subplots(figsize=(8.5, 3.3))
    ax.plot(nu, r, color=MainBlue, label=r'Robust / classical s.e. $\sqrt{(\kappa_z - 1)/2}$, $\kappa_z = 3(\nu-2)/(\nu-4)$')
    ax.axhline(1, color=Gray, lw=0.7, ls='--')
    ax.axvline(4, color=Gray, lw=0.7, ls=':')
    ax.text(4.3, 3.6, r'$\nu \leq 4$: $\kappa_z = \infty$', color='black', fontsize=10.5)
    ax.plot([nu0], [np.sqrt((k0 - 1) / 2)], 'o', color=IDAred, label=r'$\nu$ = %.2f: ratio %.2f' % (nu0, np.sqrt((k0 - 1) / 2)))
    ax.axhline(q['theory_ratio'], color=Forest, ls='-.', lw=1,
               label=r'S&P 500 GARCH-N residuals, $\hat\kappa_z$ = %.2f: ratio %.2f (observed for $\hat\alpha$: %.2f)'
               % (q['kappa_z'], q['theory_ratio'], q['ratio_alpha']))
    ax.set_ylim(0.8, 4)
    ax.set_xlabel(r'Degrees of freedom $\nu$ of the true Student-t innovations')
    ax.set_ylabel('Ratio of standard errors')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch5_sem_a5_ratio')


# ---------------------------------------------------------------- A6
def _acf_cols(X, L):
    """Autocorelatiile (corelatie Pearson, ca pandas autocorr) pentru fiecare coloana a lui X, decalaje 1..L."""
    out = np.empty((L, X.shape[1]))
    for k in range(1, L + 1):
        a, b = X[k:], X[:-k]
        a = a - a.mean(0); b = b - b.mean(0)
        out[k - 1] = (a * b).sum(0) / np.sqrt((a ** 2).sum(0) * (b ** 2).sum(0))
    return out


def fig_a6(R=200, L=50):
    f = fit_garch(rets['sp500'], 'GARCH', 'normal')
    p = f.params
    om, a, b = p['omega'], p['alpha[1]'], p['beta[1]']
    r = rets['sp500']
    e2 = ((r - r.mean()) ** 2).values
    obs = _acf_cols(e2[:, None], L)[:, 0]
    rho1 = a * (1 - b ** 2 - a * b) / (1 - b ** 2 - 2 * a * b)
    th = rho1 * (a + b) ** np.arange(L)
    rng = np.random.default_rng(SEED + 2)
    n, burn = len(r), 500
    s2 = np.full(R, om / (1 - a - b))
    X = np.empty((n, R))
    for t in range(n + burn):
        e = np.sqrt(s2) * rng.standard_normal(R)
        if t >= burn:
            X[t - burn] = e
        s2 = om + a * e ** 2 + b * s2
    A = _acf_cols(X ** 2, L)
    lo, med, hi = np.quantile(A, [0.025, 0.5, 0.975], axis=1)
    lags = np.arange(1, L + 1)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.fill_between(lags, lo, hi, color=LightGray, alpha=0.7, label=f'95% envelope of the sample ACF, {R} simulated GARCH-N paths of {n} days')
    ax.plot(lags, med, color=Forest, ls='-.', label='Median sample ACF of the simulated paths')
    ax.plot(lags, th, color=IDAred, lw=1.6, label=r'Theoretical GARCH-N ACF $\rho_k = \rho_1(\alpha+\beta)^{k-1}$')
    ax.plot(lags, obs, 'o', ms=3.5, color=MainBlue, label=r'S&P 500: sample ACF of $(r_t - \bar r)^2$')
    ax.set_xlabel('Lag $k$ (trading days)')
    ax.set_ylabel('Autocorrelation')
    ax.set_ylim(0, 0.6)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch5_sem_a6_acf')
    inside = (obs >= lo) & (obs <= hi)
    CH['a6'] = {'R': R, 'n': int(n), 'inside': int(inside.sum()), 'L': L, 'lo1': float(lo[0]), 'hi1': float(hi[0]),
                'lo10': float(lo[9]), 'hi10': float(hi[9]), 'med1': float(med[0]), 'med10': float(med[9]),
                'omega': float(om), 'obs50': float(obs[-1]), 'th50': float(th[-1]), 'n_above': int((obs > hi).sum()),
                'first_above': int(lags[obs > hi][0]) if (obs > hi).any() else 0}


# ---------------------------------------------------------------- B1
def fig_b1():
    from scipy.stats import t as tdist
    r = rets['sp500']
    f = fit_garch(r, 'GARCH', 't')
    cl = f.res.model.fit(disp='off', cov_type='classic', starting_values=f.res.params.values)
    names = ['mu', 'omega', 'alpha[1]', 'beta[1]', 'nu']
    CH['b1'] = {'est': {k: float(f.params[k]) for k in names}, 'se_rob': {k: float(f.se[k]) for k in names},
                'se_cl': {k: float(cl.std_err[k] / (1 if k == 'nu' else 1)) for k in names},
                'converged': bool(f.converged), 'loglik': float(f.loglik), 'n': int(f.nobs),
                'iterations': int(f.res.optimization_result.nit)}
    sig = f.sigma
    fig, ax = plt.subplots(figsize=(10, 3.3))
    ax.plot(r.index, r.values, color=MainBlue, lw=0.35, label='S&P 500 daily log return $r_t$ (%)')
    ax.plot(sig.index, 2 * sig.values, color=IDAred, lw=0.8, label=r'$\pm 2\hat\sigma_t$, GARCH(1,1)-t')
    ax.plot(sig.index, -2 * sig.values, color=IDAred, lw=0.8)
    ax.set_ylabel('%')
    outside = float((np.abs(r - f.params['mu']) > 2 * sig).mean())
    CH['b1']['share_outside'] = outside
    legend_outside_bottom(ax, ncol=2, y=-0.15)
    save_fig('ch5_sem_b1_fit')

    z = f.z.dropna()
    nu = f.params['nu']
    L = 20
    lags = np.arange(1, L + 1)
    band = 1.96 / np.sqrt(len(z))
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2))
    for ax, x, col, lab in [(axes[0], z, MainBlue, r'ACF of $\hat z_t$ (mean equation)'),
                            (axes[1], z ** 2, IDAred, r'ACF of $\hat z_t^2$ (variance equation)')]:
        ax.axhspan(-band, band, color=LightGray, alpha=0.7, label=r'$\pm 1.96/\sqrt{n}$', zorder=0)
        ax.bar(lags, acf(x, L), color=col, width=0.6, label=lab, zorder=3)
        ax.axhline(0, color=Gray, lw=0.5)
        ax.set_xlabel('Lag')
        ax.set_ylim(-0.06, 0.06)
    axes[0].set_ylabel('Autocorrelation')
    ax = axes[2]
    q = np.sort(z.values)
    pr = (np.arange(1, len(q) + 1) - 0.5) / len(q)
    th = tdist.ppf(pr, nu) * np.sqrt((nu - 2) / nu)
    ax.scatter(th, q, s=3, color=Forest, label=r'$\hat z_t$ vs fitted Student-t, $\hat\nu$ = %.2f' % nu)
    ax.plot([-8, 6], [-8, 6], color=Gray, lw=0.6)
    ax.set_xlim(-8, 6); ax.set_ylim(-8, 6)
    ax.set_xlabel('Theoretical quantile')
    ax.set_ylabel(r'Empirical quantile of $\hat z_t$')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=4)
    save_fig('ch5_sem_b1_diag')
    st = tdist(nu, scale=np.sqrt((nu - 2) / nu))
    CH['b1'].update({'n_below4': int((z < -4).sum()), 'exp_below4': float(len(z) * st.cdf(-4)),
                     'n_above4': int((z > 4).sum()), 'zmin': float(z.min()), 'zmin_date': str(z.idxmin().date()),
                     'acf1_z': float(acf(z, 1)[0]), 'acf1_z2': float(acf(z ** 2, 1)[0])})


# ---------------------------------------------------------------- B2 / B3
def fig_b2():
    eps = np.linspace(-6, 6, 241)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4))
    out = {}
    for ax, k, lab in [(axes[0], 'sp500', 'S&P 500'), (axes[1], 'bet', 'BET')]:
        g, j = fit_garch(rets[k], 'GARCH', 't'), fit_garch(rets[k], 'GJR', 't')
        s2 = rets[k].var()
        ax.plot(eps, news_impact(g, eps), color=MainBlue, label='GARCH(1,1)-t')
        ax.plot(eps, news_impact(j, eps), color=IDAred, label='GJR-GARCH(1,1)-t')
        v = {f'{nm}_{"m" if sh < 0 else "p"}3': float(news_impact(f, np.array([sh]))[0])
             for f, nm in [(g, 'garch'), (j, 'gjr')] for sh in [-3.0, 3.0]}
        for nm, col, other in [('garch', MainBlue, 'gjr'), ('gjr', IDAred, 'garch')]:
            for sh, tag in [(-3.0, 'm'), (3.0, 'p')]:
                y = v[f'{nm}_{tag}3']
                ax.plot([sh], [y], 'o', color=col)
                dy = 0.35 if y >= v[f'{other}_{tag}3'] else -0.35
                ax.text(sh + (0.25 if sh > 0 else -0.25), y + dy, f'{y:.2f}', color=col, fontsize=10.5,
                        ha='left' if sh > 0 else 'right', va='center')
        ax.axhline(s2, color=Gray, lw=0.6, ls='--', label=r'Starting variance $\sigma_{t-1}^2$ = sample variance')
        ax.axvline(0, color=Gray, lw=0.5)
        ax.set_title(f'{lab}: next-day variance after a shock', color='black')
        ax.set_xlabel(r'Shock $\varepsilon_{t-1}$ (%)')
        ax.set_ylabel(r'$\sigma_t^2$ (%$^2$)')
        out[k] = {'s2bar': float(s2), **v,
                  'garch': {n: float(g.params[n]) for n in g.params.index},
                  'gjr': {n: float(j.params[n]) for n in j.params.index},
                  'k_garch': int(len(g.params)), 'k_gjr': int(len(j.params)), 'n': int(g.nobs)}
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=3)
    save_fig('ch5_sem_b2_nic')
    CH['b2'] = out


def fig_b3():
    L = OUT['lr']['bet']
    n = len(rets['bet'])
    th = [(2.0, Forest, 'AIC: penalty 2 per parameter'), (stats.chi2.ppf(0.95, 1), MainBlue, r'LR test, 5%: $\chi^2_1$ critical value'),
          (stats.chi2.ppf(0.99, 1), Purple, r'LR test, 1%: $\chi^2_1$ critical value'),
          (np.log(n), IDAred, r'BIC: penalty $\ln n$ per parameter')]
    fig, ax = plt.subplots(figsize=(9, 2.6))
    for x, col, lab in th:
        ax.axvline(x, color=col, lw=1.6, label=f'{lab} = {x:.2f}')
        ax.text(x + 0.08, 1.05, f'{x:.2f}', color='black', ha='left', fontsize=10.5)
    ax.plot([L['lr']], [0.5], 'D', ms=11, color=Amber, label=r'BET: $LR = 2(\ell_{GJR} - \ell_{GARCH})$ = %.2f' % L['lr'])
    ax.text(L['lr'], 0.22, 'thresholds left of the marker: GJR kept\nthresholds right of the marker: GARCH kept', color='black',
            ha='center', fontsize=10.5)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([])
    ax.set_xlabel('Likelihood-ratio gain of one extra parameter')
    ax.spines['left'].set_visible(False)
    legend_outside_bottom(ax, ncol=2, y=-0.35)
    save_fig('ch5_sem_b3_thresholds')
    CH['b3'] = {'lnn': float(np.log(n)), 'n': int(n), 'c95': float(stats.chi2.ppf(0.95, 1)), 'c99': float(stats.chi2.ppf(0.99, 1))}


# ---------------------------------------------------------------- B4
def fig_b4():
    from scipy.stats import t as tdist
    r = rets['btc']
    fn, ft = fit_garch(r, 'GARCH', 'normal'), fit_garch(r, 'GARCH', 't')
    b = OUT['btc']
    nu = ft.params['nu']
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), gridspec_kw={'width_ratios': [1.5, 1, 1]})
    ax = axes[0]
    ax.plot(r.index, r.values, color=Amber, lw=0.4, label='Bitcoin daily log return (%)')
    ax.set_ylabel('%')
    ax.set_title(f'{r.index[0].date()} to {r.index[-1].date()}, {len(r)} days', color='black')
    ax = axes[1]
    for f, col, lab, ppf in [(fn, IDAred, 'GARCH-N residuals vs Normal', stats.norm.ppf),
                             (ft, MainBlue, r'GARCH-t residuals vs Student-t, $\hat\nu$ = %.2f' % nu,
                              lambda p: tdist.ppf(p, nu) * np.sqrt((nu - 2) / nu))]:
        q = np.sort(f.z.dropna().values)
        pr = (np.arange(1, len(q) + 1) - 0.5) / len(q)
        ax.scatter(ppf(pr), q, s=3, color=col, label=lab)
    ax.plot([-12, 8], [-12, 8], color=Gray, lw=0.6)
    ax.set_xlim(-12, 8); ax.set_ylim(-12, 8)
    ax.set_xlabel('Theoretical quantile')
    ax.set_ylabel(r'Quantile of $\hat z_t$')
    ax = axes[2]
    laws = ['normal', 't', 'skewt', 'ged']
    bic = np.array([b[d]['bic'] for d in laws])
    dbic = bic - bic.min()
    cols = [IDAred, MainBlue, Purple, Forest]
    ax.bar(range(4), dbic, color=cols, label='_nolegend_')
    for i, v in enumerate(dbic):
        ax.text(i, v + 15, f'{v:.1f}', ha='center', color='black', fontsize=10.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(['Normal', 'Student-t', 'Skewed-t', 'GED'], rotation=25)
    ax.set_ylabel(r'$\Delta$BIC (0 = preferred)')
    ax.set_ylim(0, dbic.max() * 1.15)
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=3)
    save_fig('ch5_sem_b4_btc')
    zt = ft.z.dropna()
    st = tdist(nu, scale=np.sqrt((nu - 2) / nu))
    CH['b4'] = {'n': int(len(r)), 'first': str(r.index[0].date()), 'last': str(r.index[-1].date()),
                'dbic': dict(zip(laws, map(float, dbic))), 'n_below8': int((zt < -8).sum()),
                'exp_below8_t': float(len(zt) * st.cdf(-8)), 'exp_below8_n': float(len(zt) * stats.norm.cdf(-8)),
                'zmin_t': float(zt.min()), 'zmin_date': str(zt.idxmin().date()),
                'eta_se': float(fit_garch(r, 'GARCH', 'skewt').se['eta']),
                'ged_se': float(fit_garch(r, 'GARCH', 'ged').se['nu'])}


# ---------------------------------------------------------------- B5 / B6
_FC = {}


def _fc(k):
    if k not in _FC:
        f1, _ = oos_forecasts(k, 2016, 1)
        _FC[k] = f1
    return _FC[k]


def fig_b5_timeline():
    r = rets['sp500']
    f1 = _fc('sp500')
    fig, axes = plt.subplots(2, 1, figsize=(10, 4.6), gridspec_kw={'height_ratios': [1, 1.4]})
    ax = axes[0]
    for i, y in enumerate([2016, 2017, 2018]):
        ax.barh(i, (pd.Timestamp(f'{y}-01-01') - pd.Timestamp('2000-01-01')).days, left=0, color=MainBlue, height=0.5,
                label='Estimation sample (expanding window, from 3 Jan 2000)' if i == 0 else '_nolegend_')
        x0 = (pd.Timestamp(f'{y}-01-01') - pd.Timestamp('2000-01-01')).days
        ax.barh(i, 365, left=x0, color=Amber, height=0.5,
                label='Forecast year: parameters fixed, variance updated daily' if i == 0 else '_nolegend_')
        ax.text(x0 + 380, i, f'refit on 1 Jan {y}', va='center', color='black', fontsize=10.5)
    ax.set_yticks([])
    ticks = [2000, 2005, 2010, 2015, 2019]
    ax.set_xticks([(pd.Timestamp(f'{t}-01-01') - pd.Timestamp('2000-01-01')).days for t in ticks])
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xlim(0, (pd.Timestamp('2020-06-01') - pd.Timestamp('2000-01-01')).days)
    ax.invert_yaxis()
    ax.set_title(r'Forecast made at the close of day $t$ with data up to $t$; evaluated against $r_{t+1}^2$', color='black')
    ax = axes[1]
    w = f1.loc['2020-02-03':'2020-04-30']
    rr = r.reindex(w.index)
    ax.plot(w.index, np.sqrt(w['GARCH-t']), color=MainBlue, label=r'$\sqrt{h_t}$, GARCH-t (daily %)')
    ax.plot(w.index, np.sqrt(w['EWMA']), color=Amber, ls='--', label=r'$\sqrt{h_t}$, EWMA')
    ax.scatter(w.index, np.abs(rr), s=9, color=Teal, label=r'$|r_t|$ (the square root of the proxy $r_t^2$)', zorder=3)
    ax.set_ylabel('Daily %')
    ax.set_title('February to April 2020: the forecast reacts one day after each shock', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch5_sem_b5_timeline')
    # QLIKE pas cu pas pe trei zile
    days = ['2020-03-13', '2020-03-16', '2020-03-17']
    rows = []
    for d in days:
        x = float(r.loc[d])
        hg, he = float(f1.loc[d, 'GARCH-t']), float(f1.loc[d, 'EWMA'])
        rows.append({'date': d, 'r': x, 'r2': x ** 2, 'h_g': hg, 'h_e': he,
                     'L_g': x ** 2 / hg + np.log(hg), 'L_e': x ** 2 / he + np.log(he)})
    i0 = r.index.get_loc(f1.index[0])
    CH['b5_hand'] = rows
    CH['b5_timing'] = {'first_target': str(f1.index[0].date()), 'origin': str(r.index[i0 - 1].date()),
                       'n': int(len(f1)), 'last_target': str(f1.index[-1].date())}


def fig_b56_losses(k):
    r = rets[k]
    f1 = _fc(k)
    proxy = (r ** 2).reindex(f1.index)
    L = pd.DataFrame({m: qlike(proxy, f1[m]) for m in f1.columns})
    D = L.sub(L['GARCH-t'], axis=0).drop(columns='GARCH-t')
    fc = OUT[f'fc_{k}']['models']
    cols = {'GARCH-N': Teal, 'GJR-t': IDAred, 'EGARCH-t': Forest, 'EWMA': Amber, 'Hist-20': Purple}
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), gridspec_kw={'width_ratios': [1, 1.6]})
    ax = axes[0]
    ms = list(D.columns)
    ax.bar(range(len(ms)), [D[m].mean() for m in ms], color=[cols[m] for m in ms])
    for i, m in enumerate(ms):
        v = D[m].mean()
        ax.text(i, v + (0.004 if v >= 0 else -0.004), f"t = {fc[m]['dm_t']:.2f}", ha='center',
                va='bottom' if v >= 0 else 'top', color='black', fontsize=10.5)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(range(len(ms)))
    ax.set_xticklabels(ms, rotation=20)
    lo_, hi_ = ax.get_ylim()
    ax.set_ylim(lo_ - 0.25 * (hi_ - lo_), hi_ + 0.1 * (hi_ - lo_))
    ax.set_ylabel('Mean QLIKE minus GARCH-t')
    ax.set_title('Mean loss differences (DM t)', color='black')
    ax = axes[1]
    for m in ms:
        ax.plot(D.index, D[m].cumsum(), color=cols[m], label=f'{m} minus GARCH-t')
    top = ax.get_ylim()[1]
    for d, lab in [('2020-03-16', 'Mar 2020'), ('2022-06-13', 'Jun 2022'), ('2025-04-07', 'Apr 2025')]:
        if pd.Timestamp(d) <= D.index[-1]:
            ax.axvline(pd.Timestamp(d), color=Gray, lw=0.6, ls=':')
            ax.text(pd.Timestamp(d), top, lab, rotation=90, color='black', fontsize=10.5, va='top', ha='right')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel(r'Cumulative loss difference $\sum d_t$')
    ax.set_title('Where the differences accumulate (above 0: worse than GARCH-t)', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=5)
    save_fig(f'ch5_sem_{"b5" if k == "sp500" else "b6"}_losses')
    cov = D.loc['2020-02-01':'2020-04-30'].sum()
    CH[f'loss_{k}'] = {m: {'total': float(D[m].sum()), 'covid': float(cov[m]), 'mean': float(D[m].mean())} for m in ms}


def fig_b56_mz(k, m='GARCH-t'):
    r = rets[k]
    f1 = _fc(k)
    h = f1[m]
    y = (r ** 2).reindex(f1.index)
    mz = mz_regression(y, h)
    top = y.sort_values(ascending=False).index[:3]
    mz_ex = mz_regression(y.drop(top), h.drop(top))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.5))
    ax = axes[0]
    ax.scatter(h, y, s=4, color=MainBlue, alpha=0.6, label=r'Days: $(h_t, r_t^2)$')
    xx = np.linspace(0, h.max(), 50)
    ax.plot(xx, mz['a'] + mz['b'] * xx, color=IDAred, label=r'MZ fit: $a$ = %.2f, $b$ = %.2f (s.e. %.2f)' % (mz['a'], mz['b'], mz['b_se']))
    ax.plot(xx, xx, color=Gray, ls='--', lw=0.8, label='45-degree line ($a = 0$, $b = 1$)')
    for d in top:
        ax.annotate(str(d.date()), (h[d], y[d]), (h[d] * 0.55, y[d] * 0.95), color='black', fontsize=10.5,
                    arrowprops=dict(arrowstyle='-', color='black', lw=0.4))
    ax.set_xlabel(r'Forecast $h_t$ (%$^2$)')
    ax.set_ylabel(r'Proxy $r_t^2$ (%$^2$)')
    ax.set_title('Levels: a few days dominate', color='black')
    ax = axes[1]
    bins = pd.qcut(h, 20, labels=False)
    gb = pd.DataFrame({'h': h, 'y': y, 'b': bins}).groupby('b').mean()
    ax.loglog(gb['h'], gb['y'], 'o', color=Forest, label=r'Mean $r_t^2$ within 20 bins of $h_t$ (5% of days each)')
    lim = [gb[['h', 'y']].min().min() * 0.8, gb[['h', 'y']].max().max() * 1.2]
    ax.plot(lim, lim, color=Gray, ls='--', lw=0.8)
    ax.set_xlabel(r'Mean forecast $h_t$ in the bin (log scale)')
    ax.set_ylabel(r'Mean $r_t^2$ (log scale)')
    ax.set_title('Binned calibration', color='black')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=2)
    save_fig(f'ch5_sem_{"b5" if k == "sp500" else "b6"}_mz')
    CH[f'mz_{k}'] = {'model': m, 'a': float(mz['a']), 'a_se': float(mz['a_se']), 'b': float(mz['b']),
                     'b_se': float(mz['b_se']), 'r2': float(mz['r2']), 'wald_p': float(mz['wald_p']),
                     'top': [str(d.date()) for d in top], 'b_ex': float(mz_ex['b']), 'b_ex_se': float(mz_ex['b_se']),
                     'a_ex': float(mz_ex['a']), 'wald_p_ex': float(mz_ex['wald_p'])}


def fig_b56_gwmcs():
    inf = _inf()
    ms = ['GARCH-N', 'GARCH-t', 'GJR-t', 'EGARCH-t', 'EWMA', 'Hist-20']
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)
    out = {}
    for ax, k, lab in [(axes[0], 'sp500', 'S&P 500'), (axes[1], 'bet', 'BET')]:
        g = inf[f'gw_{k}']
        x = np.arange(len(ms))
        gwp = [g['tests'][m]['gw_p'] if m != 'GARCH-t' else np.nan for m in ms]
        mcs = [g['mcs_p'][m] for m in ms]
        ax.bar(x - 0.2, np.maximum(gwp, 1e-4), width=0.4, color=MainBlue, label='GW p-value vs GARCH-t (rolling 1000-day window)')
        ax.bar(x + 0.2, np.maximum(mcs, 1e-4), width=0.4, color=Amber, label='MCS p-value (expanding window)')
        order = np.argsort(mcs)
        for rank, i in enumerate(order, 1):
            ax.text(x[i] + 0.2, max(mcs[i], 1e-4) * 1.25, str(rank), ha='center', color='black', fontsize=10.5)
        ax.axhline(0.10, color=IDAred, ls='--', lw=0.8, label='0.10: MCS size')
        ax.axhline(0.05, color=Forest, ls=':', lw=0.8, label='0.05: GW test level')
        ax.set_yscale('log')
        ax.set_ylim(1e-4, 3)
        ax.set_xticks(x)
        ax.set_xticklabels(ms, rotation=20)
        ax.set_title(f'{lab}: numbers above the MCS bars give the elimination order', color='black', fontsize=10.5)
        out[k] = {'order': [ms[i] for i in order], 'in': [m for m in ms if g['mcs_p'][m] > 0.10]}
    axes[0].set_ylabel('p-value (log scale)')
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=2)
    save_fig('ch5_sem_b56_gwmcs')
    CH['gwmcs'] = out


# ---------------------------------------------------------------- B7 / B8
def _draws():
    """Extragerile bootstrap: din rularea curenta (DRAWS) sau din fisierul salvat."""
    return dict(DRAWS) if DRAWS else dict(np.load(DRAW_FILE))


def fig_b7(k, D=None):
    D = D or _draws()
    col = MainBlue if k == 'sp500' else IDAred
    lab = 'S&P 500' if k == 'sp500' else 'BET'
    bs, ig = OUT[f'boot_{k}'], OUT[f'igarch_{k}']
    pers, lrb = D[f'boot_pers_{k}'], D[f'null_lr_{k}']
    zero = lrb < 1e-6
    CH[f'b7_{k}'] = {'share_bound': float((pers >= 1 - 1e-6).mean()), 'lr_zero': float(zero.mean()),
                     'n_ge': int((lrb >= ig['lr']).sum()), 'B': int(len(lrb)), 'q95': float(np.quantile(lrb, 0.95)),
                     'q025': float(np.quantile(pers, 0.025)), 'q975': float(np.quantile(pers, 0.975))}

    def persistence_panel(ax):
        bins = np.linspace(pers.min(), 1.0, 40)
        ax.hist(pers, bins=bins, color=col, alpha=0.85, label=r'$\hat p^*$ re-estimated on %d paths simulated from the fitted GARCH-t' % len(pers))
        ax.axvline(bs['est'], color='black', lw=1.2, label=r'Estimate on the data, $\hat p$ = %.4f' % bs['est'])
        for q in (bs['pers_lo'], min(bs['pers_hi'], 1.0)):
            ax.axvline(q, color=Amber, lw=1.2, ls='--')
        ax.plot([], [], color=Amber, ls='--', label='2.5%% and 97.5%% percentiles: [%.4f; %.4f]' % (bs['pers_lo'], min(bs['pers_hi'], 1)))
        ax.annotate('%.1f%% of draws\nat the bound $p = 1$' % (100 * CH[f'b7_{k}']['share_bound']), (1.0, ax.get_ylim()[1] * 0.6),
                    (pers.min() + 0.25 * (1 - pers.min()), ax.get_ylim()[1] * 0.8), color='black', fontsize=10.5,
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.6))
        ax.set_xlabel(r'Persistence $\hat\alpha^* + \hat\beta^*$')
        ax.set_ylabel('Number of draws')
        ax.set_title(f'{lab}: estimator variability (simulate from the fitted model)', color='black', fontsize=10.5)

    def lr_panel(ax):
        pos = lrb[~zero]
        bins = np.linspace(0, max(8, np.quantile(lrb, 0.995)), 40)
        ax.hist(pos, bins=bins, color=Purple, alpha=0.8, label=r'$LR^* > 0$ on %d paths simulated under $H_0$ (IGARCH-t)' % len(lrb))
        w = bins[1] - bins[0]
        ax.bar([-w / 2], [zero.sum()], width=w, color=Amber,
               label='$LR^* = 0$: %.1f%% of the draws (estimate at the bound)' % (100 * zero.mean()))
        ax.axvline(ig['lr'], color='black', lw=1.4, label='Observed $LR$ = %.2f' % ig['lr'])
        ax.axvline(ig['lr_q95'], color=IDAred, lw=1.2, ls='--', label='Bootstrap 95%% cutoff = %.2f' % ig['lr_q95'])
        ax.axvline(stats.chi2.ppf(0.95, 1), color=MainBlue, lw=1.0, ls=':', label=r'$\chi^2_1$ cutoff = 3.84')
        ax.axvline(stats.chi2.ppf(0.90, 1), color=Forest, lw=1.0, ls='-.', label=r'Mixture $\frac{1}{2}\chi^2_0 + \frac{1}{2}\chi^2_1$ cutoff = 2.71')
        ax.set_xlabel(r'$LR^* = 2(\ell^*_{GARCH} - \ell^*_{IGARCH})$')
        ax.set_ylabel('Number of draws')
        ax.set_title(f'{lab}: null distribution of the LR statistic', color='black', fontsize=10.5)

    if k == 'sp500':
        fig, ax = plt.subplots(figsize=(9, 3.3))
        persistence_panel(ax)
        legend_outside_bottom(ax, ncol=1, y=-0.22)
        save_fig('ch5_sem_b7_persistence')
        fig, ax = plt.subplots(figsize=(9, 3.3))
        lr_panel(ax)
        legend_outside_bottom(ax, ncol=2, y=-0.22)
        save_fig('ch5_sem_b7_lr')
    else:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.4))
        persistence_panel(axes[0])
        lr_panel(axes[1])
        fig.tight_layout()
        _fig_legend(fig, axes, ncol=2)
        save_fig('ch5_sem_b8_bet')


# ---------------------------------------------------------------- C1
def fig_c1():
    px = pd.concat([load_close('bet'), load_close('sp500')], axis=1)
    win = px.loc['2025-11-24':'2025-12-05']
    common = win.dropna().index
    df = join_bet_sp().loc['2025-11-24':'2025-12-05']
    fig, ax = plt.subplots(figsize=(10, 2.8))
    days = pd.date_range('2025-11-24', '2025-12-05')
    days = days[days.dayofweek < 5]
    for y, c, lab, s in [(2, IDAred, 'BET trading day', win['bet']), (1, MainBlue, 'S&P 500 trading day', win['sp500'])]:
        on = s.dropna().index
        ax.scatter(on, [y] * len(on), s=60, color=c, label=lab, zorder=3)
        off = days.difference(on)
        ax.scatter(off, [y] * len(off), s=60, facecolor='none', edgecolor=c, lw=1.2, zorder=3,
                   label=f'{lab.split()[0]} closed' if len(off) else '_nolegend_')
    ax.scatter(common, [0] * len(common), s=60, marker='s', color=Forest, label='Common day: kept after the join', zorder=3)
    for d in df.index:
        ax.text(d, -0.45, f'{df.loc[d, "us_lag"]:+.2f}', ha='center', color='black', fontsize=10.5)
    ax.text(days[0] - pd.Timedelta(days=1.6), -0.45, r'$u_{t-1}$ (%):', ha='left', color='black', fontsize=10.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Joined', 'S&P 500', 'BET'])
    ax.set_ylim(-0.8, 2.5)
    ax.set_xticks(days)
    ax.set_xticklabels([d.strftime('%a\n%d %b') for d in days], fontsize=10.5)
    ax.set_title('Thanksgiving (US closed, 27 Nov 2025) and Romania\'s National Day (BVB closed, 1 Dec 2025)', color='black', fontsize=10.5)
    legend_outside_bottom(ax, ncol=3, y=-0.3)
    save_fig('ch5_sem_c1_alignment')
    CH['c1_align'] = {'common': [str(d.date()) for d in common],
                      'us_lag': {str(d.date()): float(df.loc[d, 'us_lag']) for d in df.index},
                      'bet': {str(d.date()): float(df.loc[d, 'bet']) for d in df.index}}

    # descompunerea volatilitatii BET cu parametrii estimati (OUT['partc']['full']['u'])
    par = OUT['partc']['full']['u']
    dfa = join_bet_sp()
    path = spill_path(dfa, par)
    q = PPY['bet']
    vol = np.sqrt(path['s2'] * q)
    vol_ex = np.sqrt((path['s2'] - path['us']).clip(lower=1e-12) * q)
    share = (path['us'] / path['s2']).clip(0, 1)
    fig, axes = plt.subplots(2, 1, figsize=(10, 4.4), sharex=True)
    ax = axes[0]
    ax.plot(vol.index, vol.rolling(21).mean(), color=IDAred, lw=0.9, label='BET conditional volatility, full model (21-day average, % p.a.)')
    ax.plot(vol_ex.index, vol_ex.rolling(21).mean(), color=MainBlue, lw=0.9, ls='--',
            label='Without the accumulated US term $s_t$ (21-day average)')
    ax.set_ylabel('% p.a.')
    ax = axes[1]
    ax.plot(share.index, share.rolling(63).mean(), color=Purple, lw=0.9, label=r'Share $s_t/\sigma_t^2$ (3-month average)')
    ax.set_ylabel('Share')
    ax.set_ylim(0, None)
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=2)
    save_fig('ch5_sem_c1_decomp')
    CH['c1'] = {'vol_mean': float(vol.mean()), 'vol_ex_mean': float(vol_ex.mean()), 'q': float(q),
                'start': str(dfa.index[0].date()), 'end': str(dfa.index[-1].date())}


# ---------------------------------------------------------------- C2
def c2_ai_answer():
    """Ruleaza exact codul asistentului (randamente in zecimale) si varianta corectata."""
    import warnings as _w
    from arch import arch_model
    px = load_close('sp500')
    with _w.catch_warnings(record=True) as W:
        _w.simplefilter('always')
        r = np.log(px).diff().dropna()
        am = arch_model(r, vol='GARCH', p=1, q=1, dist='t')
        res = am.fit(disp='off')
    om, a, b = res.params['omega'], res.params['alpha[1]'], res.params['beta[1]']
    lr_var = om / (1 - a - b)
    wrong = {'omega': float(om), 'alpha': float(a), 'beta': float(b), 'ann_vol': float(lr_var * 252),
             'half_life': float(np.log(0.5) / np.log(b)), 'warnings': sorted({w.category.__name__ for w in W}),
             'loglik': float(res.loglikelihood), 'converged': int(res.convergence_flag)}
    r100 = 100 * np.log(px).diff().dropna()
    res2 = arch_model(r100, vol='GARCH', p=1, q=1, dist='t').fit(disp='off')
    om2, a2, b2 = res2.params['omega'], res2.params['alpha[1]'], res2.params['beta[1]']
    p = a2 + b2
    lr2 = om2 / (1 - p)
    right = {'omega': float(om2), 'alpha': float(a2), 'beta': float(b2), 'pers': float(p),
             'ann_vol_252': float(np.sqrt(252 * lr2)), 'ann_vol_q': float(np.sqrt(PPY['sp500'] * lr2)),
             'half_life': float(np.log(0.5) / np.log(p)), 'q': float(PPY['sp500'])}
    CH['c2'] = {'n_px': int(len(px)), 'first': str(px.index[0].date()), 'last': str(px.index[-1].date()),
                'wrong': wrong, 'right': right}


# ---------------------------------------------------------------- C3
def fig_c3(ticker='JPM'):
    from scipy.stats import t as tdist
    d = qsd_data(ticker)
    r, x = d.r.values, d.x.values
    g, llg = fit_qsd(r, x, 'GARCH-t')
    b, llb = fit_qsd(r, x, 'Beta-t-GARCH', start=[g[:7]])
    q, llq = fit_qsd(r, x, 'QSD', start=[np.r_[b[:7], b[6]]] + [np.r_[g[:7], z] for z in (0.01, 0.03, 0.06, 0.1)])
    g2, llg2 = fit_qsd(r, x, 'GARCH-t', start=[q[:7]])
    b2, llb2 = fit_qsd(r, x, 'Beta-t-GARCH', start=[q[:7]])
    if llg2 > llg:
        g, llg = g2, llg2
    if llb2 > llb:
        b, llb = b2, llb2
    idx = d.index[1:]
    res = {}
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
    e_g = qsd_filter(g, r, x)[2]
    t0 = int(np.argmax(np.abs(e_g)))
    lo, hi = max(t0 - 15, 0), min(t0 + 40, len(e_g))
    for th, ll, col, ls, nm in [(g, llg, Forest, '--', 'GARCH-t'), (b, llb, IDAred, ':', 'Beta-t-GARCH'), (q, llq, MainBlue, '-', 'QSD')]:
        y, f, e = qsd_filter(th, r, x)
        nu = 1 / th[6]
        u = tdist.cdf(e * np.sqrt(nu / (nu - 2)), nu)
        T = len(u)
        stat = (u.sum() - T / 2) / np.sqrt(T / 12)
        res[nm] = {'xi': float(th[6]), 'zeta': float(th[7]), 'loglik': float(ll), 'pit_stat': float(stat),
                   'pit_mean': float(u.mean())}
        axes[0].plot(idx[lo:hi], np.sqrt(f[lo:hi]), color=col, ls=ls, lw=1.4,
                     label=r'%s: $\sqrt{f_t}$ ($\hat\zeta$ = %.3f)' % (nm, th[7]))
        axes[1].hist(u, bins=20, range=(0, 1), density=True, histtype='step', color=col, ls=ls, lw=1.4,
                     label=f'{nm}: naive PIT-mean statistic {stat:+.2f}')
    axes[0].axvline(idx[t0 + 1] if t0 + 1 < len(idx) else idx[t0], color=Gray, lw=0.6, ls=':')
    axes[0].set_ylabel('Daily volatility (%)')
    axes[0].set_title(f'{QSD_STOCKS[ticker]}: largest shock on {idx[t0].date()} and the days after', color='black', fontsize=10.5)
    axes[0].tick_params(axis='x', labelrotation=20)
    axes[1].axhline(1, color=Gray, lw=0.6, ls='--')
    axes[1].set_xlabel(r'PIT $u_t = F(\epsilon_t)$')
    axes[1].set_ylabel('Density')
    axes[1].set_title('PIT histograms (uniform if the model is right)', color='black', fontsize=10.5)
    fig.tight_layout()
    _fig_legend(fig, axes, ncol=2)
    save_fig('ch5_sem_c3_pit')
    res['shock_date'] = str(idx[t0].date())
    res['T'] = int(len(e_g))
    res['lr_zeta0'] = float(2 * (llq - llg)); res['lr_xi_zeta'] = float(2 * (llq - llb))
    CH['c3'] = res


def seminar_charts(quick=False):
    """Toate graficele noi ale seminarului; cifrele intra in ch5_seminar_charts.json.
    quick=True pastreaza rezultatele C3 deja salvate (estimarea QSD dureaza cateva minute)."""
    setup_check()
    fig_a1(); fig_a2(); a3_covariance(); fig_a3(); fig_a4(); fig_a5(); fig_a6()
    fig_b1(); fig_b2(); fig_b3(); fig_b4()
    fig_b5_timeline()
    for k in ['sp500', 'bet']:
        fig_b56_losses(k); fig_b56_mz(k)
    fig_b56_gwmcs()
    D = _draws()
    fig_b7('sp500', D); fig_b7('bet', D)
    fig_c1(); c2_ai_answer()
    if quick and os.path.exists(os.path.join(HERE, 'ch5_seminar_charts.json')):
        with open(os.path.join(HERE, 'ch5_seminar_charts.json')) as fh:
            CH['c3'] = json.load(fh)['c3']
    else:
        fig_c3()
    with open(os.path.join(HERE, 'ch5_seminar_charts.json'), 'w') as fh:
        json.dump(CH, fh, indent=1, default=float)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'charts':
        # doar graficele seminarului, din cifrele si extragerile bootstrap salvate
        with open(os.path.join(HERE, 'ch5_seminar_numbers.json')) as fh:
            OUT.update(json.load(fh))
        seminar_charts(quick='quick' in sys.argv)
        print(json.dumps(CH, indent=1, default=float))
        sys.exit()
    a1_recursion(); lr_tests(); btc_innovations()
    print('forecast comparison'); forecast_comparison('sp500'); forecast_comparison('bet')
    print('bootstrap'); boots = {k: param_bootstrap(k)[0] for k in ['sp500', 'bet']}
    nulls = {k: igarch_test(k) for k in ['sp500', 'bet']}; fig_bootstrap(boots, nulls)
    np.savez(DRAW_FILE, **DRAWS)
    print('part C'); part_c()
    with open(os.path.join(HERE, 'ch5_seminar_numbers.json'), 'w') as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print(json.dumps(OUT, indent=1, default=float))
    seminar_charts()

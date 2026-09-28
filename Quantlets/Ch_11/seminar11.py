"""
seminar11.py -- Calculele Seminarului 11 (MFM): modele in timp continuu
======================================================================
Partea A: exercitii pe hartie (GBM si lema lui Ito, variatia patratica, OU/Vasicek, cumulantii Merton);
Partea B: estimare si inferenta pe date (ordine de convergenta, GBM, Vasicek si deplasarea lui kappa,
          Merton cu test LR prin bootstrap parametric, Heston din VIX);
Partea C: ce model in timp continuu reproduce cozile si gruparea volatilitatii pentru BET si Bitcoin?
Cifrele sunt salvate in sem11_results.json; graficele in charts/ch11_sem_*.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray, LightGray,  # noqa: E402
                                 MODEL_COL, save_fig, legend_outside_bottom, fig_legend_bottom, jsonable, rets, DTS,
                                 simulate_stats, SEED)
from mfm_data import LABELS, load_vix, read_fred  # noqa: E402
from ct_models import (convergence_study, slope_ci, gbm_mle, ou_mle, ou_bias_mc, merton_mle, merton_moments,  # noqa: E402
                       lr_bootstrap, lee_mykland, heston_from_vix, heston_from_proxy, stylised)

HERE = os.path.dirname(os.path.abspath(__file__))
DT = 1 / 252


# =============================================================================
# PARTEA A
# =============================================================================
def a1_gbm(mu=0.08, sigma=0.20, T=10.0):
    """A1: lema lui Ito pentru ln S; media, mediana si probabilitatea unei pierderi dupa T ani."""
    m = mu - 0.5 * sigma ** 2
    z = -m * np.sqrt(T) / sigma
    return dict(m=m, mean=np.exp(mu * T), median=np.exp(m * T), z=z, p_loss=stats.norm.cdf(z),
                p_below_mean=stats.norm.cdf(0.5 * sigma * np.sqrt(T)))


def a2_siegel(mu=0.02, sigma=0.044):
    """A2: cursul invers Y = 1/X pentru X o GBM (paradoxul lui Siegel)."""
    return dict(drift_y=-mu + sigma ** 2, logdrift_x=mu - 0.5 * sigma ** 2, logdrift_y=-(mu - 0.5 * sigma ** 2))


def a3_qv(T=1.0, n=252):
    """A3: media si dispersia variatiei patratice pe o grila de n intervale; media variatiei totale."""
    return dict(mean=T, var=2 * T ** 2 / n, sd=np.sqrt(2 * T ** 2 / n), tv=np.sqrt(2 * n * T / np.pi),
                tv_1000=np.sqrt(2 * 1000 * n * T / np.pi) / np.sqrt(1000))


def a4_ito_integral(T=1.0):
    """A4: integrala Ito a lui W dupa W: media, dispersia; integrala Stratonovich."""
    return dict(mean=0.0, var=T ** 2 / 2, sd=np.sqrt(T ** 2 / 2), strat_mean=T / 2)


def a5_ou(kappa=0.5, theta=0.03, sigma=0.01, r0=0.06, h=1.0):
    """A5: Vasicek: timpul de injumatatire, media si abaterea standard conditionate, distributia stationara."""
    e = np.exp(-kappa * h)
    cm = theta + (r0 - theta) * e
    cv = sigma ** 2 * (1 - e ** 2) / (2 * kappa)
    ssd = sigma / np.sqrt(2 * kappa)
    return dict(hl=np.log(2) / kappa, e=e, cmean=cm, csd=np.sqrt(cv), ssd=ssd, p_neg=stats.norm.cdf(-theta / ssd),
                p_neg_1y=stats.norm.cdf(-cm / np.sqrt(cv)))


def a6_ar_to_ou(a=0.0012, b=0.97, se=0.0025, dt=1 / 12):
    """A6: de la AR(1) lunar la parametrii OU."""
    kappa = -np.log(b) / dt
    return dict(kappa=kappa, theta=a / (1 - b), sigma=se * np.sqrt(2 * kappa / (1 - b ** 2)), hl=np.log(2) / kappa,
                ssd=se / np.sqrt(1 - b ** 2))


def a7_merton(sigma=0.15, lam=5.0, mu_j=-0.03, s_j=0.04, dt=1 / 252):
    """A7: cumulantii randamentului zilnic Merton."""
    mo = merton_moments(dt, sigma, lam, mu_j, s_j)
    diff_var = sigma ** 2 * dt
    jump_var = lam * dt * (mu_j ** 2 + s_j ** 2)
    return dict(mo, diff_var=diff_var, jump_var=jump_var, jump_share=jump_var / (diff_var + jump_var),
                k3=lam * dt * (mu_j ** 3 + 3 * mu_j * s_j ** 2), k4=lam * dt * (mu_j ** 4 + 6 * mu_j ** 2 * s_j ** 2 + 3 * s_j ** 4),
                p_jump_day=1 - np.exp(-lam * dt), p_jump_year=1 - np.exp(-lam))


def a8_rare(sigma=0.15, lam=0.5, mu_j=-0.10, s_j=0.05, dt=1 / 252):
    """A8: salturi rare si mari: aplatizarea zilnica si probabilitatea de a nu observa niciun salt."""
    mo = merton_moments(dt, sigma, lam, mu_j, s_j)
    return dict(mo, p_none_1y=np.exp(-lam), p_none_10y=np.exp(-10 * lam), exp_10y=10 * lam)


# =============================================================================
# PARTEA B
# =============================================================================
def b1_convergence():
    """B1: ordinele de convergenta estimate prin regresie log-log, cu intervale de incredere de 95%."""
    rng = np.random.default_rng(SEED + 4)
    d = convergence_study(rng)
    se = slope_ci(d['dt'], d['strong_em'])
    sm = slope_ci(d['dt'], d['strong_mil'])
    we = slope_ci(d['dt'], d['weak_em_exact'])
    wm = slope_ci(d['dt'], d['weak_em_mc'])
    x_sd = np.exp(2.0) * np.sqrt(np.exp(1.0) - 1)            # abaterea standard a lui X_T (lam = 2, mu = 1, T = 1)
    w_small = float(d['weak_em_exact'].iloc[0])
    return dict(em=se, mil=sm, weak=we, weak_mc=wm, x_sd=x_sd, se_mc=x_sd / np.sqrt(20000),
                weak_small=w_small, m_needed=(1.96 * x_sd / w_small) ** 2, dt_small=float(d['dt'].iloc[0]))


def b2_gbm(key='sp500'):
    """B2/B3: GBM pe date: estimari cu erori standard, testul Jarque-Bera, testul Ljung-Box pe |r|, ani necesari."""
    r = rets[key]
    dt = DTS[key]
    g = gbm_mle(r.values, dt)
    jb = stats.jarque_bera(r.values)
    a = np.abs(r.values) - np.abs(r.values).mean()
    n = len(a)
    ac = np.array([a[k:] @ a[:-k] / (a @ a) for k in range(1, 21)])
    lb = n * (n + 2) * np.sum(ac ** 2 / (n - np.arange(1, 21)))
    q20 = [r.values[i:i + 20].sum() for i in range(0, n - 19, 20)]
    vr = np.var(q20) / (20 * r.var())
    return dict(g, m_lo=g['m'] - 1.96 * g['se_m'], m_hi=g['m'] + 1.96 * g['se_m'], jb=float(jb.statistic),
                jb_p=float(jb.pvalue), lb=float(lb), lb_crit=float(stats.chi2.ppf(0.95, 20)), acf1=float(ac[0]),
                years_1pp=float((1.96 * g['sigma'] / 0.01) ** 2), start=str(r.index[0].date()), vr20=float(vr),
                exkurt=float(stats.kurtosis(r.values)))


def b4_vasicek(n_sim=500):
    """B4: Vasicek pe randamentul titlurilor de stat pe 3 luni; deplasarea lui kappa estimat prin simulare."""
    tb = read_fred('DTB3') / 100
    f = ou_mle(tb.values, DT)
    rng = np.random.default_rng(SEED + 20)
    k = ou_bias_mc(f['kappa'], f['theta'], f['sigma'], DT, len(tb), n_sim, rng)
    bias = k.mean() - f['kappa']
    kc = f['kappa'] - bias
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.hist(k, bins=40, color=Teal, alpha=0.85, label=rf'$\hat\kappa$ in {n_sim} simulated OU samples of the same length')
    ax.axvline(f['kappa'], color=IDAred, lw=1.5, label=rf"True $\kappa$ = {f['kappa']:.3f} (the estimate on the data)")
    ax.axvline(k.mean(), color=MainBlue, lw=1.5, ls='--', label=rf'Mean of $\hat\kappa$ = {k.mean():.3f}')
    ax.set_xlabel(r'$\hat\kappa$ (per year)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch11_sem_kappa_bias')
    years = len(tb) * DT
    return dict(f, n_obs=len(tb), years=years, start=str(tb.index[0].date()), k_mean=float(k.mean()),
                k_sd=float(k.std()), bias=float(bias), k_corr=float(kc), hl_corr=float(np.log(2) / kc) if kc > 0 else None,
                share_above=float(np.mean(k > f['kappa'])), approx_bias=4 / years,
                k_lo=f['kappa'] - 1.96 * f['se_kappa'], k_hi=f['kappa'] + 1.96 * f['se_kappa'])


def b5_vix(n_sim=300):
    """B5: OU pe ln VIX: timpul de injumatatire, intervalul de incredere, deplasarea."""
    x = np.log(load_vix())
    f = ou_mle(x.values, DT)
    rng = np.random.default_rng(SEED + 21)
    k = ou_bias_mc(f['kappa'], f['theta'], f['sigma'], DT, len(x), n_sim, rng)
    hl = f['half_life'] * 252
    lags = [1, 5, 20, 60, 120]
    xv = x.values - x.values.mean()
    ac = {str(L): float(xv[L:] @ xv[:-L] / (xv @ xv)) for L in lags}
    return dict(f, hl_days=hl, hl_lo=252 * np.log(2) / (f['kappa'] + 1.96 * f['se_kappa']),
                hl_hi=252 * np.log(2) / (f['kappa'] - 1.96 * f['se_kappa']), bias=float(k.mean() - f['kappa']),
                acf=ac, acf_ou={str(L): float(f['b'] ** L) for L in lags})


def b6_merton_lr(n_boot=200):
    """B6: Merton pe S&P 500: parametri cu erori standard; testul LR GBM vs Merton cu bootstrap parametric."""
    r = rets['sp500'].values
    rng = np.random.default_rng(SEED + 22)
    res = lr_bootstrap(r, DT, n_boot, rng)
    mf = res['merton']
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.hist(res['boot'], bins=30, color=Teal, alpha=0.85, label=f'LR statistic in {n_boot} samples simulated from the fitted GBM')
    ax.axvline(stats.chi2.ppf(0.95, 3), color=Orange, lw=1.5, ls='--', label=r'$\chi^2_3$ critical value, 5%')
    ax.axvline(res['crit95'], color=MainBlue, lw=1.5, label='Bootstrap critical value, 5%')
    ax.set_xlabel('Likelihood-ratio statistic under the null of no jumps')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch11_sem_lr_boot')
    mo = merton_moments(DT, mf['sigma'], mf['lam'], mf['mu_j'], mf['s_j'], mf['m'])
    return dict(lr=res['lr'], p_boot=res['p_boot'], crit95=res['crit95'], chi2=float(stats.chi2.ppf(0.95, 3)),
                boot_mean=float(res['boot'].mean()), boot_zero=float(np.mean(res['boot'] < 1e-6)),
                merton={k: v for k, v in mf.items()}, moments=mo, n_boot=n_boot)


def b7_btc():
    """B7: Merton pe Bitcoin si numarul de salturi Lee-Mykland pe an."""
    r = rets['btc']
    mf = merton_mle(r.values, DTS['btc'])
    d, crit = lee_mykland(r)
    years = (d.index[-1] - d.index[0]).days / 365.25
    mo = merton_moments(DTS['btc'], mf['sigma'], mf['lam'], mf['mu_j'], mf['s_j'], mf['m'])
    j = d[d['jump']]
    return dict(merton=mf, moments=mo, lm_per_year=float(d['jump'].sum() / years), lm_n=int(d['jump'].sum()),
                lm_mean_abs=float(j['r'].abs().mean()), lm_sd=float(j['r'].std()), data_exkurt=float(stats.kurtosis(r.values)),
                jump_var_share=float(mf['lam'] * (mf['mu_j'] ** 2 + mf['s_j'] ** 2) /
                                     (mf['sigma'] ** 2 + mf['lam'] * (mf['mu_j'] ** 2 + mf['s_j'] ** 2))))


def b8_heston():
    """B8: parametrii Heston din VIX, cu erori standard OLS pentru kappa si interval Fisher z pentru rho."""
    vix = load_vix()
    r = rets['sp500']
    hp = heston_from_vix(vix, r, DT)
    d = pd.concat([vix.rename('vix'), r.rename('r')], axis=1, join='inner').dropna()
    v = (d['vix'] / 100) ** 2
    y = ((v.shift(-1) - v) / np.sqrt(v)).values[:-1]
    X = np.column_stack([DT / np.sqrt(v), -DT * np.sqrt(v)])[:-1]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    cov = e @ e / (len(y) - 2) * np.linalg.inv(X.T @ X)
    se_k = float(np.sqrt(cov[1, 1]))
    z = np.arctanh(hp['rho'])
    zlo, zhi = z - 1.96 / np.sqrt(hp['n'] - 3), z + 1.96 / np.sqrt(hp['n'] - 3)
    halves = {}
    for a, b in [('1990', '2007'), ('2008', '2026')]:
        h = heston_from_vix(vix.loc[a:b], r.loc[a:b], DT)
        halves[f'{a}-{b}'] = {k: float(h[k]) for k in ['kappa', 'theta', 'xi', 'rho', 'feller']}
    return dict(hp, se_kappa=se_k, k_lo=hp['kappa'] - 1.96 * se_k, k_hi=hp['kappa'] + 1.96 * se_k,
                rho_lo=float(np.tanh(zlo)), rho_hi=float(np.tanh(zhi)), vrp=hp['theta'] - hp['real_var'],
                vol_q=float(np.sqrt(hp['theta'])), vol_p=float(np.sqrt(hp['real_var'])), halves=halves,
                hl_days=float(252 * np.log(2) / hp['kappa']))


# =============================================================================
# PARTEA C
# =============================================================================
def c1_models(n_sim=100):
    """C1: GBM, Merton si Heston (varianta aproximata prin varianta realizata pe 21 de zile) pentru BET si Bitcoin:
    distributiile simulate ale faptelor stilizate si pozitia datelor in aceste distributii."""
    rng = np.random.default_rng(SEED + 23)
    out = {}
    fig, axes = plt.subplots(2, 3, figsize=(11, 5.2))
    keys = ['exkurt', 'hill', 'acf_abs_sum20']
    titles = ['Excess kurtosis', 'Hill tail index (5% of losses)', 'Sum of ACF of |r|, lags 1-20']
    for row, k in enumerate(['bet', 'btc']):
        r = rets[k].values
        dt = DTS[k]
        n = len(r)
        g = gbm_mle(r, dt)
        mf = merton_mle(r, dt)
        hp = heston_from_proxy(rets[k], dt)
        hpp = dict(hp, theta=hp['real_var'])
        S = {'GBM': simulate_stats('GBM', g, n, dt, n_sim, rng),
             'Merton': simulate_stats('Merton', mf, n, dt, n_sim, rng),
             'Heston': simulate_stats('Heston', hpp, n, dt, n_sim, rng, mu=g['mu'])}
        dd = stylised(r)
        res = {'data': {c: float(dd[c]) for c in keys + ['skew', 'acf_abs1']},
               'heston': {c: float(hp[c]) for c in ['kappa', 'theta', 'xi', 'rho', 'feller', 'real_var']},
               'merton': {c: float(mf[c]) for c in ['m', 'sigma', 'lam', 'mu_j', 's_j']},
               'gbm': {c: float(g[c]) for c in ['mu', 'sigma']}, 'n': n}
        for m, s in S.items():
            res[m] = {c: dict(med=float(np.median([x[c] for x in s])), lo=float(np.quantile([x[c] for x in s], 0.05)),
                              hi=float(np.quantile([x[c] for x in s], 0.95)),
                              pct=float(np.mean([x[c] <= dd[c] for x in s]))) for c in keys + ['skew', 'acf_abs1']}
        out[k] = res
        for j, (c, t) in enumerate(zip(keys, titles)):
            ax = axes[row, j]
            names = ['Data', 'GBM', 'Merton', 'Heston']
            vals = [dd[c]] + [res[m][c]['med'] for m in names[1:]]
            lo = [0] + [res[m][c]['med'] - res[m][c]['lo'] for m in names[1:]]
            hi = [0] + [res[m][c]['hi'] - res[m][c]['med'] for m in names[1:]]
            ax.bar(range(4), vals, color=[MODEL_COL[nm] for nm in names], yerr=[lo, hi], capsize=3, width=0.65,
                   label=None)
            ax.set_xticks(range(4))
            ax.set_xticklabels(names, fontsize=8)
            ax.set_title(f'{LABELS[k]}: {t}', loc='left', fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=MODEL_COL[nm]) for nm in ['Data', 'GBM', 'Merton', 'Heston']]
    fig_legend_bottom(fig, handles, ['Data', 'GBM (median of 100 simulations, 90% range)', 'Merton', 'Heston'], ncol=4, y=0.02)
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    save_fig('ch11_sem_partC')
    return out


if __name__ == '__main__':
    S = {}
    S['A1'] = a1_gbm()
    S['A2'] = a2_siegel()
    S['A3'] = a3_qv()
    S['A4'] = a4_ito_integral()
    S['A5'] = a5_ou()
    S['A6'] = a6_ar_to_ou()
    S['A7'] = a7_merton()
    S['A8'] = a8_rare()
    print('B1'); S['B1'] = b1_convergence()
    print('B2'); S['B2'] = b2_gbm('sp500')
    print('B3'); S['B3'] = {k: b2_gbm(k) for k in ['bet', 'btc']}
    print('B4'); S['B4'] = b4_vasicek()
    print('B5'); S['B5'] = b5_vix()
    print('B6'); S['B6'] = b6_merton_lr()
    print('B7'); S['B7'] = b7_btc()
    print('B8'); S['B8'] = b8_heston()
    print('C1'); S['C1'] = c1_models()
    with open(os.path.join(HERE, 'sem11_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print('saved sem11_results.json')

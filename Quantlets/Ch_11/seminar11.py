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
from mfm_data import LABELS, load_vix, read_fred, load_close  # noqa: E402
from ct_models import (convergence_study, slope_ci, slope_boot, gbm_mle, ou_mle, ou_bias_mc, merton_mle, merton_moments,  # noqa: E402
                       lr_bootstrap, lee_mykland, heston_from_vix, heston_from_proxy, stylised, merton_logpdf,
                       nw_drift_diffusion, short_rate_fits)
from scipy import optimize  # noqa: E402

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
    """A2: cursul invers Y = 1/X pentru X o GBM (paradoxul lui Siegel); X = lei pentru un euro.
    (a)-(c): driftul procentual al lui Y este -mu + sigma^2; drifturile logaritmice sunt exact opuse.
    (d), simbolic, cu rate constante: sub Q^RON, X_t e^{(r_EUR - r_RON) t} (contul in euro, in lei, actualizat) este
    martingala, deci dX = (r_RON - r_EUR) X dt + sigma X dW~ si E^{Q^RON}[X_T] = X_0 e^{(r_RON - r_EUR) T} = F;
    schimbarea activului de referinta: dQ^EUR/dQ^RON = X_T e^{-(r_RON - r_EUR) T} / X_0 = exp(sigma W~_T - sigma^2 T / 2),
    iar sub Q^EUR driftul lui 1/X este r_EUR - r_RON, deci E^{Q^EUR}[1/X_T] = 1/F. Driftul real mu nu intra in forward."""
    return dict(drift_y=-mu + sigma ** 2, logdrift_x=mu - 0.5 * sigma ** 2, logdrift_y=-(mu - 0.5 * sigma ** 2))


def a3_qv(T=1.0, n=252):
    """A3: media si dispersia variatiei patratice pe o grila de n intervale; media variatiei totale."""
    return dict(mean=T, var=2 * T ** 2 / n, sd=np.sqrt(2 * T ** 2 / n), tv=np.sqrt(2 * n * T / np.pi),
                tv_1000=np.sqrt(2 * 1000 * n * T / np.pi) / np.sqrt(1000))


def a4_ito_integral(T=1.0):
    """A4: int_0^T W dW = (W_T^2 - T) / 2: media 0, dispersia T^2 / 2; Stratonovich W_T^2 / 2 are media T / 2.
    Din lema lui Ito pentru W^3: int_0^T W^2 dW = W_T^3 / 3 - int_0^T W_t dt, cu media 0 si, prin izometria Ito,
    dispersia int_0^T E[W_t^4] dt = int_0^T 3 t^2 dt = T^3."""
    return dict(mean=0.0, var=T ** 2 / 2, sd=np.sqrt(T ** 2 / 2), strat_mean=T / 2, var_w2dw=T ** 3)


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


def a8_rare(sigma=0.15, lam=0.5, mu_j=-0.10, s_j=0.05, dt=1 / 252, T=36.7, rel_target=0.20):
    """A8: salturi rare si mari: aplatizarea zilnica, probabilitatea de a nu observa niciun salt si, cu toate salturile
    observate, e.s. a lui lam_hat = N_T / T; e.s. relativa 1 / sqrt(lam T) = rel_target cere T = 1 / (rel_target^2 lam) ani."""
    mo = merton_moments(dt, sigma, lam, mu_j, s_j)
    return dict(mo, p_none_1y=np.exp(-lam), p_none_10y=np.exp(-10 * lam), exp_10y=10 * lam,
                se_lam=np.sqrt(lam / T), rel_se=1 / np.sqrt(lam * T), years_needed=1 / (rel_target ** 2 * lam))


# --- Partea A, probleme de derivare (schimbarea masurii, Feynman-Kac, CIR, VIX in Heston, informatia Fisher) ---
def a1_girsanov(mu=0.08, sigma=0.20, r=0.03, T=10.0):
    """A1: GBM sub P si sub Q: pretul de piata al riscului theta = (mu - r) / sigma, densitatea Radon-Nikodym,
    probabilitatea unei pierderi dupa T ani sub cele doua masuri."""
    th = (mu - r) / sigma
    mP, mQ = mu - 0.5 * sigma ** 2, r - 0.5 * sigma ** 2
    return dict(theta=th, mP=mP, mQ=mQ, zP=-mP * np.sqrt(T) / sigma, zQ=-mQ * np.sqrt(T) / sigma,
                p_loss_P=stats.norm.cdf(-mP * np.sqrt(T) / sigma), p_loss_Q=stats.norm.cdf(-mQ * np.sqrt(T) / sigma),
                eq_growth=np.exp(r * T), var_Z=np.exp(th ** 2 * T) - 1)


def a3_vasicek_bond(kappa=0.5, theta=0.03, sigma=0.01, r0=0.06, taus=(1, 5, 10)):
    """A3: pretul obligatiunii zero-cupon Vasicek din ecuatia Feynman-Kac: P = exp(A(tau) - B(tau) r)."""
    out = {}
    for tau in taus:
        B = (1 - np.exp(-kappa * tau)) / kappa
        A = (theta - sigma ** 2 / (2 * kappa ** 2)) * (B - tau) - sigma ** 2 * B ** 2 / (4 * kappa)
        out[str(tau)] = dict(B=B, A=A, P=np.exp(A - B * r0), y=(B * r0 - A) / tau)
    return dict(out, y_inf=theta - sigma ** 2 / (2 * kappa ** 2))


def a5_cir(kappa=0.11, theta=0.055, sigma=0.056, r0=0.03, t=1.0):
    """A5: CIR: momentele conditionate, tranzitia chi-patrat necentrala si conditia Feller (grade de libertate >= 2)."""
    e = np.exp(-kappa * t)
    m = theta + (r0 - theta) * e
    v = r0 * sigma ** 2 / kappa * (e - e ** 2) + theta * sigma ** 2 / (2 * kappa) * (1 - e) ** 2
    c = 2 * kappa / (sigma ** 2 * (1 - e))
    df = 4 * kappa * theta / sigma ** 2
    nc = 2 * c * r0 * e
    q = stats.ncx2.ppf([0.05, 0.95], df, nc) / (2 * c)
    vas_sd = sigma * np.sqrt(r0) * np.sqrt((1 - e ** 2) / (2 * kappa))
    # P(r_t < 1 punct de baza); cu nu >= 2 (Feller) zero nu este atins, deci P(r_t = 0) = 0
    return dict(cmean=m, csd=np.sqrt(v), c=c, df=df, nc=nc, feller=2 * kappa * theta / sigma ** 2, q05=q[0], q95=q[1],
                p_below_1bp=float(stats.ncx2.cdf(2 * c * 1e-4, df, nc)))


def a6_vix_heston(kappa_q=5.0, tau=30 / 365, xi_hat=0.56, theta_q=0.044):
    """A6: VIX^2 sub Heston: VIX^2 / 100^2 = a + b v_t, cu b = (1 - e^{-kappa^Q tau}) / (kappa^Q tau), a = theta^Q (1 - b).
    Difuzia lui y este xi sqrt(b (y - a)); raportata la sqrt(y), coeficientul xi_y(v) = b xi sqrt(v / (a + b v)) depinde
    de stare si este egal cu b xi doar la v = theta^Q: xi_hat / b este o corectie locala (aproximativa), nu un estimator."""
    b = (1 - np.exp(-kappa_q * tau)) / (kappa_q * tau)
    a = theta_q * (1 - b)
    ratio = {f'{v:.3f}': float(b * np.sqrt(v / (a + b * v))) for v in (0.01, theta_q, 0.10)}
    return dict(b=b, a=a, xi_corr=xi_hat / b, ktau=kappa_q * tau, xi_ratio=ratio)


def a7_fisher(lam=5.0, T=36.7, lam_mle=None, se_mle=None):
    """A7 (d): informatia Fisher pentru intensitatea Poisson cand salturile sunt observate: I(lam) = T / lam."""
    out = dict(se=np.sqrt(lam / T), rel=np.sqrt(lam / T) / lam)
    if lam_mle is not None:
        out.update(se_obs=np.sqrt(lam_mle / T), ratio=se_mle / np.sqrt(lam_mle / T))
    return out


def a9_ar_ou_delta(a=0.0012, b=0.97, se=0.0025, dt=1 / 12, n=600):
    """A9: AR(1) lunar -> OU, cu erorile standard prin metoda delta; aceeasi durata T cu date zilnice."""
    kappa = -np.log(b) / dt
    se_b = np.sqrt((1 - b ** 2) / n)
    se_k = se_b / (b * dt)
    T = n * dt
    hl = np.log(2) / kappa
    bd = np.exp(-kappa / 252)
    se_kd = np.sqrt((1 - bd ** 2) / (T * 252)) / (bd / 252)
    return dict(kappa=kappa, theta=a / (1 - b), sigma=se * np.sqrt(2 * kappa / (1 - b ** 2)), hl=hl, ssd=se / np.sqrt(1 - b ** 2),
                se_b=se_b, se_kappa=se_k, se_hl=hl / kappa * se_k, T=T, b_daily=bd, se_kappa_daily=se_kd,
                se_kappa_limit=np.sqrt(2 * kappa / T))


# =============================================================================
# PARTEA B
# =============================================================================
def b1_convergence():
    """B1: ordinele de convergenta estimate prin regresie log-log, cu intervale de incredere de 95%."""
    rng = np.random.default_rng(SEED + 4)
    d, P = convergence_study(rng, return_paths=True)
    rb = np.random.default_rng(SEED + 40)
    # intervale bootstrap pe traiectorii intregi: se reesantioneaza cele 20.000 de traiectorii, toti pasii impreuna
    se = slope_boot(d['dt'], P['abs_em'], rb)
    sm = slope_boot(d['dt'], P['abs_mil'], rb)
    wm = slope_boot(d['dt'], P['x_em'], rb, target=P['ex'])
    # media exacta (1 + 2 dt)^{1/dt}: eroare determinista, panta pe grila fara interval de incredere
    x = np.log(d['dt'].values)
    we = dict(slope=float(np.polyfit(x, np.log(d['weak_em_exact']), 1)[0]),
              slope_fine=float((np.log(d['weak_em_exact'].iloc[1]) - np.log(d['weak_em_exact'].iloc[0])) / (x[1] - x[0])))
    # pantele locale ale erorilor tari intre cei mai fini doi pasi (curbura pre-asimptotica)
    se['slope_fine'] = float((np.log(d['strong_em'].iloc[1]) - np.log(d['strong_em'].iloc[0])) / (x[1] - x[0]))
    sm['slope_fine'] = float((np.log(d['strong_mil'].iloc[1]) - np.log(d['strong_mil'].iloc[0])) / (x[1] - x[0]))
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
    # erori standard fara ipoteza GBM: (i) s.e.(sigma) robusta la aplatizare pentru randamente independente,
    # sigma sqrt((k + 2) / (4n)), k = excesul de aplatizare; (ii) bootstrap pe blocuri mobile (Kunsch, 1989), blocuri de
    # 63 de zile (un trimestru), care pastreaza gruparea volatilitatii si autocorelatia
    k = float(stats.kurtosis(r.values))
    se_s_kurt = g['sigma'] * np.sqrt((k + 2) / (4 * n))
    bm, bs = block_bootstrap_gbm(r.values, dt, block=63, n_boot=999, rng=np.random.default_rng(SEED + 30))
    return dict(g, m_lo=g['m'] - 1.96 * g['se_m'], m_hi=g['m'] + 1.96 * g['se_m'], jb=float(jb.statistic),
                se_sigma_kurt=float(se_s_kurt), se_sigma_block=float(bs.std()), se_m_block=float(bm.std()),
                m_lo_block=float(np.quantile(bm, 0.025)), m_hi_block=float(np.quantile(bm, 0.975)),
                s_lo_block=float(np.quantile(bs, 0.025)), s_hi_block=float(np.quantile(bs, 0.975)),
                jb_p=float(jb.pvalue), lb=float(lb), lb_crit=float(stats.chi2.ppf(0.95, 20)), acf1=float(ac[0]),
                years_1pp=float((1.96 * g['sigma'] / 0.01) ** 2), start=str(r.index[0].date()), vr20=float(vr),
                exkurt=float(stats.kurtosis(r.values)))


def block_bootstrap_gbm(r, dt, block=63, n_boot=999, rng=None):
    """Bootstrap pe blocuri mobile pentru sigma si driftul logaritmic m (estimatorii GBM), fara ipoteza i.i.d."""
    r = np.asarray(r)
    n = len(r)
    nb = int(np.ceil(n / block))
    starts_max = n - block + 1
    m, s = np.empty(n_boot), np.empty(n_boot)
    for i in range(n_boot):
        idx = (rng.integers(0, starts_max, nb)[:, None] + np.arange(block)[None, :]).ravel()[:n]
        x = r[idx]
        m[i] = x.mean() / dt
        s[i] = np.sqrt(x.var() / dt)
    return m, s


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
    # inferenta dupa corectie: (i) test al lui kappa = 0 (mers aleator, radacina unitara) cu distributia nula simulata
    # a lui kappa_hat (500 de mersuri aleatoare de aceeasi lungime, pornite din x_0, cu abaterea standard a reziduurilor);
    # (ii) interval aproximativ pentru kappa corectat: kappa_c +/- 1.96 * abaterea standard simulata a lui kappa_hat
    rw = np.random.default_rng(SEED + 24)
    sd = f['sigma'] * np.sqrt((1 - f['b'] ** 2) / (2 * f['kappa']))
    k0 = np.empty(n_sim)
    for i in range(n_sim):
        x = tb.values[0] + np.concatenate([[0.0], np.cumsum(sd * rw.standard_normal(len(tb) - 1))])
        k0[i] = -np.log(ou_mle(x, DT)['b']) / DT
    p_rw = (1 + np.sum(k0 >= f['kappa'])) / (1 + n_sim)
    return dict(f, n_obs=len(tb), years=years, start=str(tb.index[0].date()), k_mean=float(k.mean()),
                k0_mean=float(k0.mean()), k0_q95=float(np.quantile(k0, 0.95)), p_rw=float(p_rw),
                kc_lo=float(kc - 1.96 * k.std()), kc_hi=float(kc + 1.96 * k.std()),
                resid_after_72=float(np.exp(-kc * years)),
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


def b6_merton_lr(n_boot=200, sigma_min=0.05, n_jobs=None):
    """B6: Merton pe S&P 500: parametri cu erori standard; testul LR GBM vs Merton cu bootstrap parametric.
    Statistica este definita pe spatiul restrans sigma >= 5% (verosimilitatea nerestransa este nemarginita, B6 (d)),
    cu aceleasi sase puncte de start pentru esantionul observat si pentru fiecare esantion bootstrap."""
    r = rets['sp500'].values
    rng = np.random.default_rng(SEED + 22)
    n_jobs = os.cpu_count() if n_jobs is None else n_jobs
    res = lr_bootstrap(r, DT, n_boot, rng, sigma_min=sigma_min, n_jobs=n_jobs)
    mf = res['merton']
    fig, ax = plt.subplots(figsize=(8, 3.3))
    ax.hist(res['boot'], bins=30, color=Teal, alpha=0.85, label=f'LR statistic in {n_boot} samples simulated from the fitted GBM')
    ax.axvline(stats.chi2.ppf(0.95, 3), color=Orange, lw=1.5, ls='--', label=r'$\chi^2_3$ critical value, 5%')
    ax.axvline(res['crit95'], color=MainBlue, lw=1.5, label='Bootstrap critical value, 5%')
    ax.set_xlabel('Likelihood-ratio statistic under the null of no jumps')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch11_sem_lr_boot')
    mo = merton_moments(DT, mf['sigma'], mf['lam'], mf['mu_j'], mf['s_j'], mf['m'])
    return dict(lr=res['lr'], p_boot=res['p_boot'], n_exceed=res['n_exceed'], p_upper95=res['p_upper95'],
                sigma_min=sigma_min, crit95=res['crit95'], chi2=float(stats.chi2.ppf(0.95, 3)),
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
    p = load_close('sp500')
    hp = heston_from_vix(vix, p, DT)
    d = pd.concat([vix.rename('vix'), p.rename('p')], axis=1, join='inner').dropna().iloc[1:]
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
        h = heston_from_vix(vix.loc[a:b], p.loc[a:b], DT)
        halves[f'{a}-{b}'] = {k: float(h[k]) for k in ['kappa', 'theta', 'xi', 'rho', 'feller']}
    return dict(hp, se_kappa=se_k, k_lo=hp['kappa'] - 1.96 * se_k, k_hi=hp['kappa'] + 1.96 * se_k,
                rho_lo=float(np.tanh(zlo)), rho_hi=float(np.tanh(zhi)), vrp=hp['theta'] - hp['real_var'],
                vol_q=float(np.sqrt(hp['theta'])), vol_p=float(np.sqrt(hp['real_var'])), halves=halves,
                hl_days=float(252 * np.log(2) / hp['kappa']))


# --- Partea B, extinderi ---
def b4_likelihoods():
    """B4 (d)-(e): CIR exact vs Euler si CKLS pe DTB3, 1954-2007 (din Quantlets/Ch_11/generate_all_charts.py)."""
    tb = read_fred('DTB3') / 100
    s = tb.loc['1954':'2007']
    return {'daily': short_rate_fits(s.values, DT), 'monthly': short_rate_fits(s.resample('ME').last().values, 1 / 12)}


def b6_profile(sigmas=(0.05, 0.02, 0.01)):
    """B6 (d): verosimilitatea profil Merton in sigma (restul parametrilor reestimati) si MLE cu constrangerea sigma >= 5%."""
    r = rets['sp500'].values
    mf = merton_mle(r, DT)
    out = {'mle': dict(sigma=mf['sigma'], loglik=mf['loglik'])}
    x0 = np.array([mf['m'], np.log(mf['lam']), mf['mu_j'], np.log(mf['s_j'])])
    for sg in sigmas:
        nll = lambda q, sg=sg: -merton_logpdf(r, DT, q[0], sg, np.exp(q[1]), q[2], np.exp(q[3])).sum()
        best = None
        for lam0 in (np.exp(x0[1]), 2 * np.exp(x0[1]), 4 * np.exp(x0[1])):
            q0 = x0.copy()
            q0[1] = np.log(lam0)
            res = optimize.minimize(nll, q0, method='Nelder-Mead', options=dict(maxiter=20000, maxfev=20000, xatol=1e-8, fatol=1e-6))
            if best is None or res.fun < best.fun:
                best = res
        out[f'{sg:.2f}'] = dict(loglik=-best.fun, lam=float(np.exp(best.x[1])), s_j=float(np.exp(best.x[3])))
    # sup = +infinit: sigma -> 0 cu m dt egal cu un randament observat; contributia acelui randament
    i = int(np.argmin(np.abs(r - np.median(r))))
    w0 = np.exp(-mf['lam'] * DT)
    out['spike'] = {f'{sg:.0e}': float(np.log(w0) + stats.norm.logpdf(0, 0, sg * np.sqrt(DT))) for sg in (1e-2, 1e-4, 1e-8, 1e-16)}
    out['constrained_binding'] = bool(mf['sigma'] < 0.05)
    return out


def b8_affine_rv(kappa_q=5.0):
    """B8 (d)-(e): xi corectat pentru relatia afina VIX^2 = a + b v; rho din varianta realizata la 5 minute (SPY, Capitolul 9)
    fata de rho din VIX, pe aceleasi zile."""
    vix = load_vix()
    p = load_close('sp500')
    hp = heston_from_vix(vix, p, DT)
    b = (1 - np.exp(-kappa_q * 30 / 365)) / (kappa_q * 30 / 365)
    path = os.path.join(HERE, '..', 'Ch_09', 'ch9_rv_spy.csv')
    if not os.path.exists(path):
        path = 'https://raw.githubusercontent.com/danpele/MFM/main/Quantlets/Ch_09/ch9_rv_spy.csv'
    rv = pd.read_csv(path, index_col=0, parse_dates=True)['rv_total'] * 1e-4 / DT      # varianta anualizata
    # preturile, VIX si RV aliniate intai pe zilele comune; randamentele pe aceasta grila
    d = pd.concat([p.rename('p'), vix.rename('vix'), rv.rename('rv')], axis=1, join='inner').dropna()
    d['r'] = np.log(d['p']).diff()
    d = d.dropna()
    # xi / b: corectie locala, exacta doar la v = theta^Q (vezi A6)
    out = dict(b=b, xi=hp['xi'], xi_corr=hp['xi'] / b, n_rv=len(d), start_rv=str(d.index[0].date()))
    for name, v in [('vix', (d['vix'] / 100) ** 2), ('rv', d['rv'])]:
        dv = v.diff().shift(-1) / np.sqrt(v)
        zr = d['r'].shift(-1) / np.sqrt(v)
        same = pd.concat([v.diff(), d['r']], axis=1).dropna().corr().iloc[0, 1]
        rho = pd.concat([dv, zr], axis=1).dropna().corr().iloc[0, 1]
        n = int(pd.concat([dv, zr], axis=1).dropna().shape[0])
        z = np.arctanh(rho)
        out[name] = dict(rho=float(rho), lo=float(np.tanh(z - 1.96 / np.sqrt(n - 3))), hi=float(np.tanh(z + 1.96 / np.sqrt(n - 3))),
                         rho_raw=float(same))
    return out


def b9_np(mult=(0.5, 1.0, 2.0)):
    """B9: difuzia neparametrica a ratei pe 3 luni (1954-2007): sensibilitatea la latimea de banda h."""
    tb = (read_fred('DTB3') / 100).loc['1954':'2007']
    x = tb.values
    fits = short_rate_fits(x, DT)
    grid = np.linspace(np.quantile(x, 0.02), np.quantile(x, 0.98), 60)
    h0 = 1.06 * x[:-1].std() * (len(x) - 1) ** (-0.2)
    out = {'h0': h0}
    par = {'Vasicek': np.full_like(grid, fits['vasicek_euler']['sigma']), 'CIR': fits['cir_euler']['sigma'] * np.sqrt(grid),
           'CKLS': fits['ckls']['sigma'] * grid ** fits['ckls']['gamma']}
    for m in mult:
        nw = nw_drift_diffusion(x, DT, grid, h=m * h0)
        lo = np.sqrt(np.maximum(nw['diff2'] - 1.96 * nw['diff2_se'], 0))
        hi = np.sqrt(nw['diff2'] + 1.96 * nw['diff2_se'])
        b = np.sqrt(nw['diff2'])
        out[f'{m:g}'] = dict(inside={k: float(np.mean((v >= lo) & (v <= hi))) for k, v in par.items()},
                             slope=float(np.polyfit(np.log(grid), np.log(b), 1)[0]),
                             relse=float(np.median(nw['diff2_se'] / nw['diff2'])),
                             drift_zero=float(np.mean(np.abs(nw['drift']) <= 1.96 * nw['drift_se'])))
    return out


# =============================================================================
# PARTEA C
# =============================================================================
def c1_models(n_sim=100):
    """C1: GBM, Merton si Heston (varianta aproximata prin varianta realizata pe 21 de zile,
    RV_t = (1/21) sum_{j=0}^{20} r_{t-j}^2 / dt) pentru BET si Bitcoin: distributiile simulate ale faptelor stilizate
    si percentila q a datelor in aceste distributii (verificare descriptiva: parametrii sunt estimati pe aceleasi date
    si nu sunt reestimati pe esantioanele simulate, deci q nu este o valoare p calibrata).
    Fereastra mobila suprapusa induce singura persistenta: pentru randamente independente, autocorelatia de ordinul 1
    a lui RV_t este 20/21, deci kappa estimat reflecta si constructia ferestrei, nu doar dinamica variantei latente."""
    rng = np.random.default_rng(SEED + 23)
    out = {}
    fig, axes = plt.subplots(2, 3, figsize=(11, 5.2))
    keys = ['exkurt', 'hill', 'acf_abs_sum20']
    titles = ['Excess kurtosis', 'Hill statistic (k = 5% of n)', 'Sum of ACF of |r|, lags 1-20']
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


def extra(S):
    """Problemele noi (derivari in Partea A, extinderi in Partea B), adaugate la rezultatele existente."""
    S['A1g'] = a1_girsanov()
    S['A3b'] = a3_vasicek_bond()
    S['A4'] = a4_ito_integral()
    S['A5c'] = a5_cir()
    S['A6h'] = a6_vix_heston()
    me = json.load(open(os.path.join(HERE, 'ch11_results.json')))['merton']['sp500']
    S['A7f'] = a7_fisher(5.0, 36.7, me['lam'], me['se']['lam'])
    S['A8f'] = dict(a7_fisher(0.5, 36.7), years_20pct=a8_rare()['years_needed'])
    S['A9'] = a9_ar_ou_delta()
    print('B4 likelihoods'); S['B4L'] = b4_likelihoods()
    print('B6 profile'); S['B6P'] = b6_profile()
    print('B8 affine, RV'); S['B8R'] = b8_affine_rv()
    print('B9'); S['B9'] = b9_np()
    return S


if __name__ == '__main__' and sys.argv[1:] == ['extra']:
    with open(os.path.join(HERE, 'sem11_results.json')) as f:
        S = extra(json.load(f))
    with open(os.path.join(HERE, 'sem11_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print('updated sem11_results.json')
elif __name__ == '__main__':
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
    S = extra(S)
    with open(os.path.join(HERE, 'sem11_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print('saved sem11_results.json')

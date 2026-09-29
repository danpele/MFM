"""
inference_ch6.py -- Inferenta pentru Capitolul 6 (MFM): erorile standard din spatele estimatorilor de dependenta
===============================================================================================================
  * corr_delta_se, corr_hac_path   -- varianta HAC a corelatiei prin metoda delta (momentele x, y, x^2, y^2, xy)
  * wkd_test                       -- testul Wied, Kramer & Dehling (2012) pentru o schimbare a corelatiei
                                      la un moment necunoscut (fereastra Bartlett floor(T^(1/4)))
  * two_step_bootstrap             -- erorile standard ale DCC: doar pasul 2 versus ambii pasi (bootstrap parametric
                                      cu reziduuri, GARCH reestimat pe fiecare traiectorie simulata)
  * hedge_oos                      -- raportul de acoperire dinamic din DCC in afara esantionului (BET / Euro Stoxx 50)
  * fr_bootstrap                   -- Forbes-Rigobon cu delta aleator: bootstrap stationar in ferestrele calma si de criza
  * tau_se, cml_se                 -- eroarea standard a lui tau Kendall (proiectia Hoeffding) si erorile standard CML
                                      (Genest, Ghoudi & Rivest, 1995) fata de inversa hessienei
  * chen_fan_mc                    -- Monte Carlo: CML pe rangurile inovatiilor adevarate versus ale reziduurilor GARCH
  * tail_symmetry                  -- lambda_L(q) - lambda_U(q) cu bootstrap
  * gas_t_copula                   -- copula t cu corelatie dinamica GAS (Creal, Koopman & Lucas, 2013), scalare unitara
Iesire: ch6_inference_numbers.json si graficele ch6_corr_hac, ch6_wkd, ch6_gas_copula.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, optimize
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import joint_returns, weekly_returns   # noqa: E402
from dep_tools import (garch_all, dcc_fit, dcc_path, fr_adjust, pseudo_obs, kendall_tau, spearman_rho,  # noqa: E402
                       simulate, fit_copula, log_density, empirical_tail_dep, fisher_ci, njit)
from scipy.special import gammaln   # noqa: E402
from generate_all_charts import (save_fig, legend_outside_bottom, shade_crises, two_day_returns, MainBlue,  # noqa: E402
                                 IDAred, Forest, Amber, Purple, CALM08, CRISIS08, CALM20, CRISIS20, SEED,
                                 bank_copula_data)
from seminar6 import simulate_dcc2, stationary_bootstrap_idx   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
N = {}


# =============================================================================
# 1. Varianta HAC a unei corelatii (metoda delta pe momente)
# =============================================================================
def bartlett_lrv(M, L):
    """Varianta pe termen lung (Newey-West, nucleu Bartlett cu L decalaje) a coloanelor lui M (centrate)."""
    M = np.asarray(M, dtype=float)
    M = M - M.mean(0)
    T = len(M)
    S = M.T @ M / T
    for l in range(1, L + 1):
        G = M[l:].T @ M[:-l] / T
        S += (1 - l / (L + 1)) * (G + G.T)
    return S


def corr_grad(m):
    """Gradientul lui rho = (m5 - m1 m2) / sqrt((m3 - m1^2)(m4 - m2^2)), m = (Ex, Ey, Ex^2, Ey^2, Exy)."""
    m1, m2, m3, m4, m5 = m
    vx, vy, c = m3 - m1 ** 2, m4 - m2 ** 2, m5 - m1 * m2
    r = c / np.sqrt(vx * vy)
    return r, np.array([-m2 / np.sqrt(vx * vy) + r * m1 / vx, -m1 / np.sqrt(vx * vy) + r * m2 / vy,
                        -r / (2 * vx), -r / (2 * vy), 1 / np.sqrt(vx * vy)])


def corr_delta_se(x, y, L=None):
    """Corelatia si trei erori standard: Fisher (i.i.d. Normal), metoda delta fara decalaje (momente de ordin 4)
    si metoda delta HAC (Bartlett, L = floor(4 (T/100)^(2/9)) implicit)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    T = len(x)
    L = int(np.floor(4 * (T / 100) ** (2 / 9))) if L is None else L
    M = np.column_stack([x, y, x * x, y * y, x * y])
    r, g = corr_grad(M.mean(0))
    se_iid = np.sqrt(g @ bartlett_lrv(M, 0) @ g / T)
    se_hac = np.sqrt(g @ bartlett_lrv(M, L) @ g / T)
    return dict(rho=r, se_fisher=(1 - r ** 2) / np.sqrt(T - 3), se_iid=se_iid, se_hac=se_hac, T=T, L=L)


def hac_ci(r, se, level=0.95):
    """Interval pe scara Fisher z cu eroarea standard data (metoda delta: se_z = se / (1 - r^2))."""
    q = stats.norm.ppf(0.5 + level / 2)
    z, sz = np.arctanh(r), se / (1 - r ** 2)
    return np.tanh(z - q * sz), np.tanh(z + q * sz)


def corr_hac_path(R, window=252, step=5):
    out = []
    X = R.values
    for e in range(window, len(R) + 1, step):
        s = corr_delta_se(X[e - window:e, 0], X[e - window:e, 1])
        lo_f, hi_f = fisher_ci(s['rho'], window)
        lo_h, hi_h = hac_ci(s['rho'], s['se_hac'])
        out.append((R.index[e - 1], s['rho'], lo_f, hi_f, lo_h, hi_h))
    return pd.DataFrame(out, columns=['date', 'rho', 'lo_f', 'hi_f', 'lo_h', 'hi_h']).set_index('date')


def fig_corr_hac():
    R = joint_returns(['spy', 'tlt'])
    P = corr_hac_path(R)
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    shade_crises(ax)
    ax.fill_between(P.index, P['lo_h'], P['hi_h'], color=IDAred, alpha=0.18, lw=0, label='95% HAC delta-method interval')
    ax.fill_between(P.index, P['lo_f'], P['hi_f'], color=MainBlue, alpha=0.30, lw=0, label='95% Fisher interval (i.i.d. Normal)')
    ax.plot(P.index, P['rho'], color=MainBlue, lw=1.0, label='252-day rolling correlation SPY-TLT')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Correlation')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_corr_hac')
    ratio = (P['hi_h'] - P['lo_h']) / (P['hi_f'] - P['lo_f'])
    sig_f = (P['lo_f'] > 0) | (P['hi_f'] < 0)
    sig_h = (P['lo_h'] > 0) | (P['hi_h'] < 0)
    N.update(hac_ratio_med=ratio.median(), hac_ratio_q90=ratio.quantile(0.9), hac_ratio_max=ratio.max(),
             hac_share_flip=(sig_f & ~sig_h).mean(), hac_share_sig_f=sig_f.mean(), hac_share_sig_h=sig_h.mean(),
             hac_nwin=len(P))
    last = P.iloc[-1]
    N.update(hac_last_rho=last['rho'], hac_last_lo_f=last['lo_f'], hac_last_hi_f=last['hi_f'], hac_last_lo_h=last['lo_h'],
             hac_last_hi_h=last['hi_h'], hac_last_date=str(P.index[-1].date()))
    for lab, sl in (('pre', slice(None, '2021-12-31')), ('post', slice('2022-01-01', None))):
        s = corr_delta_se(100 * R.loc[sl, 'spy'], 100 * R.loc[sl, 'tlt'])
        for k in ('rho', 'se_fisher', 'se_iid', 'se_hac', 'T', 'L'):
            N[f'hac_{lab}_{k}'] = s[k]
    return P


# =============================================================================
# 2. Testul Wied-Kramer-Dehling (2012)
# =============================================================================
def wkd_test(x, y):
    """Q_T = max_j (j / sqrt(T)) |rho_j - rho_T| / D, D^2 = varianta pe termen lung a corelatiei prin metoda delta,
    nucleu Bartlett cu latimea floor(T^(1/4)) (Wied, Kramer & Dehling, 2012). Sub H0: sup |punte Brownian|."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    T = len(x)
    M = np.column_stack([x, y, x * x, y * y, x * y])
    r, g = corr_grad(M.mean(0))
    D = np.sqrt(g @ bartlett_lrv(M, int(np.floor(T ** 0.25))) @ g)
    C = np.cumsum(M, axis=0) / np.arange(1, T + 1)[:, None]
    m1, m2, m3, m4, m5 = C.T
    with np.errstate(invalid='ignore', divide='ignore'):
        rj = (m5 - m1 * m2) / np.sqrt((m3 - m1 ** 2) * (m4 - m2 ** 2))
    path = np.arange(1, T + 1) / np.sqrt(T) * np.abs(rj - r) / D
    path[:1] = 0
    j = int(np.nanargmax(path))
    Q = path[j]
    return dict(Q=Q, p=stats.kstwobign.sf(Q), j=j, path=path, D=D, rho=r)


def fig_wkd():
    R = joint_returns(['spy', 'tlt'])
    P, V, Z, _ = garch_all(R)
    w = wkd_test(Z['spy'], Z['tlt'])
    brk = Z.index[w['j']]
    z0, z1 = Z.loc[:brk], Z.loc[brk:].iloc[1:]
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(Z.index, w['path'], color=MainBlue, lw=1.0, label='WKD process (j / sqrt(T)) |rho_j - rho_T| / D')
    ax.axhline(stats.kstwobign.ppf(0.95), color='black', ls='--', lw=0.8, label='5% critical value (1.358)')
    ax.axvline(brk, color=IDAred, ls=':', lw=1.0, label=f'Estimated break: {brk.date()}')
    ax.set_ylabel('Scaled CUSUM of correlation')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_wkd')
    w0, w1 = wkd_test(z0['spy'], z0['tlt']), wkd_test(z1['spy'], z1['tlt'])
    N.update(wkd_Q=w['Q'], wkd_p=w['p'], wkd_break=str(brk.date()), wkd_T=len(Z), wkd_bw=int(np.floor(len(Z) ** 0.25)),
             wkd_r0=z0.corr().iloc[0, 1], wkd_r1=z1.corr().iloc[0, 1], wkd_crit=stats.kstwobign.ppf(0.95),
             wkd_Q_pre=w0['Q'], wkd_p_pre=w0['p'], wkd_break_pre=str(z0.index[w0['j']].date()),
             wkd_Q_post=w1['Q'], wkd_p_post=w1['p'])
    return w


# =============================================================================
# 3. DCC: erori standard pentru estimarea in doi pasi
# =============================================================================
def simulate_garch(mu, omega, alpha, beta, eps):
    """Randamente (in %) dintr-un GARCH(1,1) cu medie constanta si inovatiile standardizate eps."""
    T = len(eps)
    r = np.empty(T)
    s2 = omega / (1 - alpha - beta)
    for t in range(T):
        r[t] = mu + np.sqrt(s2) * eps[t]
        s2 = omega + alpha * (r[t] - mu) ** 2 + beta * s2
    return r


def two_step_bootstrap(B=199):
    """Bootstrap parametric cu reziduuri pentru (a, b): (i) doar pasul 2 (DCC reestimat pe reziduurile simulate),
    (ii) ambii pasi (randamente GARCH simulate, GARCH reestimat, apoi DCC). Aceleasi inovatii in (i) si (ii)."""
    R = joint_returns(['spy', 'tlt'])
    P, V, Z, _ = garch_all(R)
    d = dcc_fit(Z)
    X = Z.values
    L = np.linalg.cholesky(d['R'])
    eta = np.linalg.solve(L, X[:, :, None])[:, :, 0]
    eta = (eta - eta.mean(0)) / eta.std(0)
    rng = np.random.default_rng(SEED)
    one, two = [], []
    for _ in range(B):
        eps = simulate_dcc2(d['a'], d['b'], d['Qbar'], eta[rng.integers(0, len(eta), len(eta))])
        d1 = dcc_fit(pd.DataFrame(eps))
        one.append((d1['a'], d1['b']))
        sim = {c: simulate_garch(P.loc['mu', c], P.loc['omega', c], P.loc['alpha[1]', c], P.loc['beta[1]', c], eps[:, k])
               for k, c in enumerate(R.columns)}
        Rs = pd.DataFrame(sim, index=R.index) / 100
        _, _, Zs, _ = garch_all(Rs)
        d2 = dcc_fit(Zs)
        two.append((d2['a'], d2['b']))
    one, two = np.array(one), np.array(two)
    N.update(ts_a=d['a'], ts_b=d['b'], ts_se_a_hess=d['se_a'], ts_se_b_hess=d['se_b'],
             ts_se_a_one=one[:, 0].std(ddof=1), ts_se_b_one=one[:, 1].std(ddof=1),
             ts_se_a_two=two[:, 0].std(ddof=1), ts_se_b_two=two[:, 1].std(ddof=1),
             ts_se_ab_one=one.sum(1).std(ddof=1), ts_se_ab_two=two.sum(1).std(ddof=1),
             ts_mean_a_two=two[:, 0].mean(), ts_mean_b_two=two[:, 1].mean(), ts_B=B)
    return one, two


# =============================================================================
# 4. Raportul de acoperire dinamic in afara esantionului: BET acoperit cu Euro Stoxx 50
# =============================================================================
def garch_fixed(r_full, params):
    """Volatilitatea conditionala si reziduurile standardizate pe toata perioada, cu parametrii fixati."""
    res = arch_model(100 * r_full, mean='Constant', vol='GARCH', p=1, q=1).fix(params)
    return res.conditional_volatility, res.resid / res.conditional_volatility


def nw_tstat(d):
    """Statistica t a mediei cu eroare standard Newey-West (L = floor(4 (T/100)^(2/9)))."""
    d = np.asarray(d, float)
    T = len(d)
    L = int(np.floor(4 * (T / 100) ** (2 / 9)))
    return d.mean() / np.sqrt(bartlett_lrv(d[:, None], L)[0, 0] / T)


def fig_hedge_oos(h_all, h_static, h_expost, e_un, e_st, e_dc, split):
    """Raportul de hedge DCC (parametri estimati pana in 2019, apoi fixati) fata de hedge-ul static si
    suma cumulata a patratelor randamentelor cu hedge in perioada de evaluare."""
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 4.0))
    ax = axes[0]
    h = h_all.loc['2017-01-01':]
    ax.plot(h.index, h, color=IDAred, lw=0.7, label='DCC hedge ratio h_t (parameters frozen after 2019)')
    ax.axhline(h_static, color=MainBlue, lw=1.3, label=f'Static hedge, 2010-2019 slope = {h_static:.3f}')
    ax.axhline(h_expost, color=Forest, lw=1.1, ls='--', label=f'Best constant hedge chosen ex post = {h_expost:.2f}')
    ax.axvline(pd.Timestamp(split), color='black', lw=0.8, ls=':')
    ax.text(pd.Timestamp(split), ax.get_ylim()[1], ' evaluation starts', va='top', fontsize=7.5, color='black')
    ax.set_ylabel('Hedge ratio')
    ax = axes[1]
    for e, col, lab in ((e_un, Amber, 'Unhedged BET'), (e_st, MainBlue, 'Static hedge'), (e_dc, IDAred, 'DCC hedge')):
        ax.plot(e.index, np.cumsum((100 * e) ** 2), color=col, lw=1.1, label=f'{lab}: cumulative squared return')
    ax.set_ylabel('Cum. squared return (%^2)')
    hs, ls_ = [], []
    for a_ in axes:
        h_, l_ = a_.get_legend_handles_labels()
        hs += h_
        ls_ += l_
    fig.tight_layout()
    fig.legend(hs, ls_, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False, fontsize=7)
    save_fig('ch6_hedge_oos')


def hedge_oos(split='2019-12-31'):
    R = joint_returns(['bet', 'stoxx'], start='2010-01-01')
    est, oos = R.loc[R.index <= pd.Timestamp(split)], R.loc[R.index > pd.Timestamp(split)]
    h_static = np.cov(est['bet'], est['stoxx'])[0, 1] / est['stoxx'].var()
    vols, Zs = {}, {}
    for c in R.columns:
        p = arch_model(100 * est[c], mean='Constant', vol='GARCH', p=1, q=1).fit(disp='off').params
        vols[c], Zs[c] = garch_fixed(R[c], p)
    Z = pd.DataFrame(Zs)
    V = pd.DataFrame(vols)
    d = dcc_fit(Z.loc[:split])
    Rt = dcc_path(Z.values, d['a'], d['b'], d['Qbar'])
    h = pd.Series(Rt[:, 0, 1] * V['bet'].values / V['stoxx'].values, index=R.index).loc[oos.index]
    e_un = oos['bet']
    e_st = oos['bet'] - h_static * oos['stoxx']
    e_dc = oos['bet'] - h * oos['stoxx']
    b_oos = np.cov(oos['bet'], oos['stoxx'])[0, 1] / oos['stoxx'].var()
    e_ex = oos['bet'] - b_oos * oos['stoxx']
    vr = lambda e: 1 - e.var() / e_un.var()
    dm = nw_tstat((1e4 * e_st) ** 2 - (1e4 * e_dc) ** 2)
    fig_hedge_oos(pd.Series(Rt[:, 0, 1] * V['bet'].values / V['stoxx'].values, index=R.index), h_static, b_oos,
                  e_un, e_st, e_dc, split)
    N.update(ho_h_static=h_static, ho_h_mean=h.mean(), ho_h_min=h.min(), ho_h_max=h.max(), ho_vr_static=vr(e_st),
             ho_vr_dcc=vr(e_dc), ho_vr_expost=vr(e_ex), ho_h_expost=b_oos, ho_dm=dm, ho_dm_p=1 - stats.norm.cdf(dm),
             ho_n_est=len(est), ho_n_oos=len(oos), ho_a=d['a'], ho_b=d['b'], ho_start=str(R.index[0].date()))


# =============================================================================
# 5. Forbes-Rigobon cu delta aleator
# =============================================================================
def fr_delta_method(rc, delta, n_c, n_0):
    """Eroarea standard a lui rho* = rho_c / sqrt(1 + delta (1 - rho_c^2)): cu delta fixat si cu delta aleator.
    Aproximari i.i.d. Normale, ferestre independente: Var(rho_c) ~ (1 - rho_c^2)^2 / n_c,
    Var(delta) ~ 2 (1 + delta)^2 (1/(n_c-1) + 1/(n_0-1)) si covarianta Cov(rho_c, delta) ~ (1 + delta) rho_c (1 - rho_c^2) / n_c
    (corelatia si varianta sursei sunt estimate din aceeasi fereastra de criza)."""
    k = 1 + delta * (1 - rc ** 2)
    g_r, g_d = (1 + delta) / k ** 1.5, -rc * (1 - rc ** 2) / (2 * k ** 1.5)
    v_r, v_d = (1 - rc ** 2) ** 2 / n_c, 2 * (1 + delta) ** 2 * (1 / (n_c - 1) + 1 / (n_0 - 1))
    c_rd = (1 + delta) * rc * (1 - rc ** 2) / n_c
    return (np.sqrt(g_r ** 2 * v_r), np.sqrt(g_r ** 2 * v_r + g_d ** 2 * v_d + 2 * g_r * g_d * c_rd), g_r, g_d,
            np.sqrt(v_d), c_rd)


def fr_bootstrap(calm, crisis, tag, B=1999, block=10):
    r2 = two_day_returns(['sp500', 'stoxx', 'bet'])
    c0, c1 = r2.loc[calm[0]:calm[1]], r2.loc[crisis[0]:crisis[1]]
    rng = np.random.default_rng(SEED)
    delta = c1['sp500'].var() / c0['sp500'].var() - 1
    N[f'frb_{tag}_delta'] = delta
    for tg in ('stoxx', 'bet'):
        r0, rc = c0['sp500'].corr(c0[tg]), c1['sp500'].corr(c1[tg])
        adj = fr_adjust(rc, delta)
        dif = []
        for _ in range(B):
            a = c0.values[stationary_bootstrap_idx(len(c0), block, rng)]
            b = c1.values[stationary_bootstrap_idx(len(c1), block, rng)]
            j = list(r2.columns).index(tg)
            dl = b[:, 0].var(ddof=1) / a[:, 0].var(ddof=1) - 1
            dif.append((fr_adjust(np.corrcoef(b[:, 0], b[:, j])[0, 1], dl) - np.corrcoef(a[:, 0], a[:, j])[0, 1], dl,
                        fr_adjust(np.corrcoef(b[:, 0], b[:, j])[0, 1], dl)))
        dif = np.array(dif)
        se_fix, se_rand, g_r, g_d, se_d, c_rd = fr_delta_method(rc, delta, len(c1) // 2, len(c0) // 2)
        z_fix = (np.arctanh(adj) - np.arctanh(r0)) / np.sqrt(1 / (len(c1) // 2 - 3) + 1 / (len(c0) // 2 - 3))
        # test pe scara rho cu eroarea standard a diferentei (delta aleator), calm tratat ca i.i.d. Normal;
        # rho_calm si delta folosesc aceeasi fereastra calma: Cov(rho*, rho_calm) = g_d Cov(delta, rho_calm),
        # Cov(delta, rho_calm) ~ -(1 + delta) rho_calm (1 - rho_calm^2) / n_0
        se0 = (1 - r0 ** 2) / np.sqrt(len(c0) // 2)
        c_s0 = -g_d * (1 + delta) * r0 * (1 - r0 ** 2) / (len(c0) // 2)
        z_rand = (adj - r0) / np.sqrt(se_rand ** 2 + se0 ** 2 - 2 * c_s0)
        z_fixr = (adj - r0) / np.sqrt(se_fix ** 2 + se0 ** 2)
        N.update({f'frb_{tag}_{tg}_adj': adj, f'frb_{tag}_{tg}_r0': r0, f'frb_{tag}_{tg}_rc': rc,
                  f'frb_{tag}_{tg}_p_boot': np.mean(dif[:, 0] <= 0), f'frb_{tag}_{tg}_ci_lo': np.percentile(dif[:, 2], 5),
                  f'frb_{tag}_{tg}_ci_hi': np.percentile(dif[:, 2], 95), f'frb_{tag}_{tg}_se_boot': dif[:, 2].std(ddof=1),
                  f'frb_{tag}_{tg}_se_fix': se_fix, f'frb_{tag}_{tg}_se_rand': se_rand, f'frb_{tag}_{tg}_g_r': g_r,
                  f'frb_{tag}_{tg}_g_d': g_d, f'frb_{tag}_{tg}_z_fixr': z_fixr, f'frb_{tag}_{tg}_z_rand': z_rand,
                  f'frb_{tag}_{tg}_p_fixr': 1 - stats.norm.cdf(z_fixr), f'frb_{tag}_{tg}_p_rand': 1 - stats.norm.cdf(z_rand),
                  f'frb_{tag}_{tg}_z_fisher': z_fix, f'frb_{tag}_{tg}_c_rd': c_rd,
                  f'frb_{tag}_{tg}_z_fisher_k': (np.arctanh(adj) - np.arctanh(r0))
                  / np.sqrt(1 / ((len(c1) // 2) * (1 + delta * (1 - rc ** 2))) + 1 / (len(c0) // 2))})
        N[f'frb_{tag}_se_delta'] = se_d
        N[f'frb_{tag}_delta_boot_lo'], N[f'frb_{tag}_delta_boot_hi'] = np.percentile(dif[:, 1], [5, 95])
    N[f'frb_{tag}_nc'], N[f'frb_{tag}_n0'] = len(c1) // 2, len(c0) // 2
    N['frb_B'], N['frb_block'] = B, block


# =============================================================================
# 6. Estimatori de rang si erorile standard CML
# =============================================================================
def emp_copula_at_points(u, v, chunk=2000):
    n = len(u)
    out = np.empty(n)
    for i in range(0, n, chunk):
        out[i:i + chunk] = np.mean((u[None, :] <= u[i:i + chunk, None]) & (v[None, :] <= v[i:i + chunk, None]), axis=1)
    return out


def tau_se(u, v):
    """Eroarea standard a lui tau Kendall din proiectia Hoeffding: 4 sd(2 C_n(U, V) - U - V) / sqrt(n)."""
    W = 2 * emp_copula_at_points(u, v) - u - v
    return kendall_tau(u, v), 4 * W.std() / np.sqrt(len(u))


def cml_se(fam, par, u, v, hp=1e-5, hu=1e-6):
    """Erori standard CML: inversa hessienei (margini cunoscute) si sandwich-ul Genest-Ghoudi-Rivest (1995),
    in care scorul primeste termenii W1(U_i) + W2(V_i) datorati rangurilor."""
    par = np.asarray(par, float)
    k, n = len(par), len(u)

    def score(p, uu, vv):
        g = np.empty((len(uu), k))
        for j in range(k):
            e = np.zeros(k)
            e[j] = hp * max(1, abs(p[j]))
            g[:, j] = (log_density(fam, p + e, uu, vv) - log_density(fam, p - e, uu, vv)) / (2 * e[j])
        return g
    S = score(par, u, v)
    A = np.zeros((k, k))
    for j in range(k):
        e = np.zeros(k)
        e[j] = 1e-4 * max(1, abs(par[j]))
        A[:, j] = -(score(par + e, u, v) - score(par - e, u, v)).mean(0) / (2 * e[j])
    A = (A + A.T) / 2
    du = (score(par, u + hu, v) - score(par, u - hu, v)) / (2 * hu)
    dv = (score(par, u, v + hu) - score(par, u, v - hu)) / (2 * hu)

    def suffix(x, D):
        o = np.argsort(x)
        cs = np.cumsum(D[o][::-1], axis=0)[::-1] / n
        out = np.empty_like(D)
        out[o] = cs
        return out
    Ai = np.linalg.inv(A)
    Bg = np.atleast_2d(np.cov((S + suffix(u, du) + suffix(v, dv)).T))
    return np.sqrt(np.diag(Ai) / n), np.sqrt(np.diag(Ai @ Bg @ Ai) / n)


def rank_inference():
    Rb, Zb, U = bank_copula_data()
    u, v = U[:, 0], U[:, 1]
    tau, se_tau = tau_se(u, v)
    rho_tau = np.sin(np.pi * tau / 2)
    se_rho_tau = np.pi / 2 * np.cos(np.pi * tau / 2) * se_tau
    ft = fit_copula('t', u, v)
    naive, ggr = cml_se('t', ft['par'], u, v)
    N.update(ri_tau=tau, ri_se_tau=se_tau, ri_rho_tau=rho_tau, ri_se_rho_tau=se_rho_tau, ri_rho_cml=ft['par'][0],
             ri_nu_cml=ft['par'][1], ri_se_rho_naive=naive[0], ri_se_rho_ggr=ggr[0], ri_se_nu_naive=naive[1],
             ri_se_nu_ggr=ggr[1], ri_n=len(u))
    # asimetria in cozi: lambda_L(q) - lambda_U(q), bootstrap i.i.d. pe perechi de reziduuri (reranguite)
    rng = np.random.default_rng(SEED)
    X = Zb.values
    for q, tag in ((0.05, '05'), (0.01, '01')):
        L0, U0 = empirical_tail_dep(u, v, q)
        db = []
        for _ in range(999):
            Ub = pseudo_obs(X[rng.integers(0, len(X), len(X))])
            lb, ub = empirical_tail_dep(Ub[:, 0], Ub[:, 1], q)
            db.append(lb - ub)
        db = np.array(db)
        N.update({f'ts_diff{tag}': L0 - U0, f'ts_se{tag}': db.std(ddof=1), f'ts_lo{tag}': np.percentile(db, 2.5),
                  f'ts_hi{tag}': np.percentile(db, 97.5), f'ts_k{tag}': int(round(q * len(u)))})
    # S&P 500 / Euro Stoxx 50 saptamanal (seminarul, A2 si B2)
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    U2 = pseudo_obs(W.values)
    u2, v2 = U2[:, 0], U2[:, 1]
    t2, se2 = tau_se(u2, v2)
    rs_impl = lambda t: 6 / np.pi * np.arcsin(np.sin(np.pi * t / 2) / 2)
    diff = rs_impl(t2) - spearman_rho(u2, v2)
    bs = []
    for _ in range(1999):
        i = rng.integers(0, len(W), len(W))
        Ub = pseudo_obs(W.values[i])
        tb = kendall_tau(Ub[:, 0], Ub[:, 1])
        bs.append(rs_impl(tb) - spearman_rho(Ub[:, 0], Ub[:, 1]))
    bs = np.array(bs)
    fg, ft2 = fit_copula('gaussian', u2, v2), fit_copula('t', u2, v2)
    ng, gg = cml_se('gaussian', fg['par'], u2, v2)
    nt, gt = cml_se('t', ft2['par'], u2, v2)
    N.update(a2_se_tau=se2, a2_se_clayton=2 / (1 - t2) ** 2 * se2, a2_se_gauss=np.pi / 2 * np.cos(np.pi * t2 / 2) * se2,
             a2_W_sd=se2 * np.sqrt(len(W)) / 4, a2_diff=diff, a2_diff_se=bs.std(ddof=1), a2_diff_lo=np.percentile(bs, 2.5),
             a2_diff_hi=np.percentile(bs, 97.5), b2_se_rho_g_naive=ng[0], b2_se_rho_g_ggr=gg[0], b2_se_rho_t_naive=nt[0],
             b2_se_rho_t_ggr=gt[0], b2_se_nu_naive=nt[1], b2_se_nu_ggr=gt[1])


# =============================================================================
# 7. Chen & Fan (2006) in cifre: CML pe rangurile reziduurilor GARCH
# =============================================================================
def chen_fan_mc(R_=500, T=2000, rho=0.8, df=5):
    Rb, Zb, U = bank_copula_data()
    P, _, _, _ = garch_all(Rb)
    rng = np.random.default_rng(SEED)
    est_true, est_res, se_naive, se_ggr = [], [], [], []
    for _ in range(R_):
        Uc = simulate('gaussian', [rho], T, rng)
        eps = stats.t.ppf(Uc, df) / np.sqrt(df / (df - 2))
        Ut = pseudo_obs(eps)
        est_true.append(fit_copula('gaussian', Ut[:, 0], Ut[:, 1])['par'][0])
        sim = {c: simulate_garch(P.loc['mu', c], P.loc['omega', c], P.loc['alpha[1]', c], P.loc['beta[1]', c], eps[:, k])
               for k, c in enumerate(Rb.columns)}
        _, _, Zs, _ = garch_all(pd.DataFrame(sim) / 100)
        Ur = pseudo_obs(Zs.values)
        f = fit_copula('gaussian', Ur[:, 0], Ur[:, 1])
        est_res.append(f['par'][0])
        a, b = cml_se('gaussian', f['par'], Ur[:, 0], Ur[:, 1])
        se_naive.append(a[0])
        se_ggr.append(b[0])
    N.update(cf_sd_true=np.std(est_true, ddof=1), cf_sd_res=np.std(est_res, ddof=1), cf_se_naive=np.mean(se_naive),
             cf_se_ggr=np.mean(se_ggr), cf_theory_ggr=(1 - rho ** 2) / np.sqrt(T),
             cf_theory_naive=(1 - rho ** 2) / np.sqrt((1 + rho ** 2) * T), cf_R=R_, cf_T=T, cf_rho=rho, cf_df=df,
             cf_bias_res=np.mean(est_res) - rho)


# =============================================================================
# 8. Copula t dinamica: GAS (Creal, Koopman & Lucas, 2013), scalare unitara
# =============================================================================
def t_score_rho(rho, nu, x, y):
    """d log c_t / d rho pentru copula t (x, y = cuantilele t_nu ale pseudo-observatiilor)."""
    Q = x * x + y * y - 2 * rho * x * y
    D = nu * (1 - rho ** 2)
    dQD = (-2 * x * y * (1 - rho ** 2) + 2 * rho * Q) / (nu * (1 - rho ** 2) ** 2)
    return rho / (1 - rho ** 2) - (nu + 2) / 2 * dQD / (1 + Q / D)


@njit(cache=True)
def gas_t_nll(om, A, Bp, nu, x, y, cst):
    """Minus log-verosimilitatea copulei t GAS (aceeasi recursie ca gas_filter); x, y = cuantilele t_nu."""
    f = om / (1.0 - Bp)
    ll = 0.0
    for t in range(len(x)):
        r = np.tanh(f)
        if abs(r) >= 0.9999:
            return 1e10
        Q = x[t] * x[t] + y[t] * y[t] - 2.0 * r * x[t] * y[t]
        D = nu * (1.0 - r * r)
        ll += (cst - 0.5 * np.log(1.0 - r * r) - (nu + 2.0) / 2.0 * np.log1p(Q / D)
               + (nu + 1.0) / 2.0 * (np.log1p(x[t] * x[t] / nu) + np.log1p(y[t] * y[t] / nu)))
        dQD = (-2.0 * x[t] * y[t] * (1.0 - r * r) + 2.0 * r * Q) / (nu * (1.0 - r * r) ** 2)
        s = (r / (1.0 - r * r) - (nu + 2.0) / 2.0 * dQD / (1.0 + Q / D)) * (1.0 - r * r)
        f = om + A * s + Bp * f
    return -ll


def gas_filter(theta, u, v):
    om, A, Bp, nu = theta
    x, y = stats.t.ppf(u, nu), stats.t.ppf(v, nu)
    T = len(u)
    f = np.empty(T)
    f[0] = om / (1 - Bp)
    for t in range(T - 1):
        r = np.tanh(f[t])
        s = t_score_rho(r, nu, x[t], y[t]) * (1 - r * r)
        f[t + 1] = om + A * s + Bp * f[t]
    return np.tanh(f)


def gas_t_copula(u, v):
    fs = fit_copula('t', u, v)
    r0, nu0 = fs['par']

    uc, vc = np.clip(u, 1e-10, 1 - 1e-10), np.clip(v, 1e-10, 1 - 1e-10)

    def nll(p):
        om, A, Bp, lnu = p
        nu = 2.01 + np.exp(lnu)
        if not (0 <= Bp < 0.9995) or A < 0 or A > 1:
            return 1e10
        cst = gammaln((nu + 2) / 2) + gammaln(nu / 2) - 2 * gammaln((nu + 1) / 2)
        return gas_t_nll(om, A, Bp, nu, stats.t.ppf(uc, nu), stats.t.ppf(vc, nu), cst)
    best = None
    for Bp, A in ((0.98, 0.03), (0.95, 0.05), (0.99, 0.01)):
        p0 = [(1 - Bp) * np.arctanh(r0), A, Bp, np.log(nu0 - 2.01)]
        r = optimize.minimize(nll, p0, method='Nelder-Mead', options=dict(xatol=1e-6, fatol=1e-6, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
    om, A, Bp, lnu = best.x
    nu = 2.01 + np.exp(lnu)
    rho = gas_filter((om, A, Bp, nu), u, v)
    return dict(om=om, A=A, B=Bp, nu=nu, rho=rho, ll=-best.fun, ll_static=fs['loglik'], rho_static=r0, nu_static=nu0,
                lr=2 * (-best.fun - fs['loglik']))


def fig_gas_copula():
    Rb, Zb, U = bank_copula_data()
    g = gas_t_copula(U[:, 0], U[:, 1])
    rho = pd.Series(g['rho'], index=Zb.index)
    lam = pd.Series(2 * stats.t.cdf(-np.sqrt((g['nu'] + 1) * (1 - rho) / (1 + rho)), g['nu'] + 1), index=rho.index)
    lam_s = 2 * stats.t.cdf(-np.sqrt((g['nu_static'] + 1) * (1 - g['rho_static']) / (1 + g['rho_static'])),
                            g['nu_static'] + 1)
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    shade_crises(ax)
    ax.plot(rho.index, rho, color=IDAred, lw=0.9, label='GAS t copula: correlation rho_t')
    ax.plot(lam.index, lam, color=MainBlue, lw=0.9, label='Implied tail dependence lambda_t')
    ax.axhline(g['rho_static'], color=IDAred, ls='--', lw=0.8, label='Static t copula rho')
    ax.axhline(lam_s, color=MainBlue, ls='--', lw=0.8, label='Static t copula lambda')
    ax.set_ylabel('JPM-BAC dependence')
    ax.set_ylim(0, 1)
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch6_gas_copula')
    N.update(gas_om=g['om'], gas_A=g['A'], gas_B=g['B'], gas_nu=g['nu'], gas_ll=g['ll'], gas_ll_static=g['ll_static'],
             gas_lr=g['lr'], gas_rho_min=rho.min(), gas_rho_min_date=str(rho.idxmin().date()), gas_rho_max=rho.max(),
             gas_rho_max_date=str(rho.idxmax().date()), gas_rho_last=rho.iloc[-1], gas_rho_static=g['rho_static'],
             gas_nu_static=g['nu_static'], gas_lam_min=lam.min(), gas_lam_max=lam.max(), gas_lam_static=lam_s,
             gas_rho_2020=rho.loc['2020-03-01':'2020-06-30'].mean(), gas_rho_2019=rho.loc['2019'].mean())
    # seminarul, B6: S&P 500 / Euro Stoxx 50 saptamanal
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    U2 = pseudo_obs(W.values)
    g2 = gas_t_copula(U2[:, 0], U2[:, 1])
    r2 = pd.Series(g2['rho'], index=W.index)
    N.update(b6_A=g2['A'], b6_B=g2['B'], b6_nu=g2['nu'], b6_lr=g2['lr'], b6_rho_min=r2.min(),
             b6_rho_min_date=str(r2.idxmin().date()), b6_rho_max=r2.max(), b6_rho_max_date=str(r2.idxmax().date()),
             b6_rho_static=g2['rho_static'], b6_nu_static=g2['nu_static'], b6_om=g2['om'])
    return g


# =============================================================================
# 9. Calibrarea testelor sub ipoteza nula (bootstrap parametric): CCC contra DCC, simetria cozilor, GAS contra static
# =============================================================================
def ccc_null_bootstrap(names, tag, B=199):
    """p-valoarea statisticii DCC contra CCC sub H0: CCC. Inovatii cu corelatie constanta din reziduurile decorelate
    reesantionate, randamente GARCH(1,1) simulate cu parametrii estimati, apoi AMBII pasi reestimati pe fiecare traiectorie
    (GARCH univariat, tinta Qbar, (a, b)); statistica observata se calculeaza cu aceeasi procedura."""
    R = joint_returns(names)
    P, V, Z, _ = garch_all(R)
    d = dcc_fit(Z)
    lr_obs = 2 * (d['loglik'] - d['ccc_loglik'])
    X = Z.values
    Qbar = np.cov(X.T, bias=True)
    C = Qbar / np.sqrt(np.outer(np.diag(Qbar), np.diag(Qbar)))
    eta = np.linalg.solve(np.linalg.cholesky(C), X.T).T
    eta = (eta - eta.mean(0)) / eta.std(0)
    rng = np.random.default_rng(SEED)
    lrs = []
    for _ in range(B):
        eps = simulate_dcc2(0.0, 0.0, C, eta[rng.integers(0, len(eta), len(eta))])
        sim = {c: simulate_garch(P.loc['mu', c], P.loc['omega', c], P.loc['alpha[1]', c], P.loc['beta[1]', c], eps[:, k])
               for k, c in enumerate(R.columns)}
        _, _, Zs, _ = garch_all(pd.DataFrame(sim, index=R.index) / 100)
        ds = dcc_fit(Zs)
        lrs.append(2 * (ds['loglik'] - ds['ccc_loglik']))
    lrs = np.array(lrs)
    N.update({f'{tag}_lr_obs': lr_obs, f'{tag}_lr_null_q95': np.percentile(lrs, 95), f'{tag}_lr_null_max': lrs.max(),
              f'{tag}_lr_p_boot': (1 + np.sum(lrs >= lr_obs)) / (B + 1), f'{tag}_lr_B': B})


def tail_symmetry_block(q_list=((0.05, '05'), (0.01, '01')), B=999):
    """lambda_L(q) - lambda_U(q) la prag fixat q, cu bootstrap stationar pe blocuri (Politis & Romano, 1994); lungimea
    medie a blocului: regula automata a lui Politis & White (2004), aplicata indicatorului 1{colt inferior} - 1{colt superior}."""
    from arch.bootstrap import optimal_block_length
    Rb, Zb, U = bank_copula_data()
    u, v = U[:, 0], U[:, 1]
    X = Zb.values
    rng = np.random.default_rng(SEED)
    for q, tag in q_list:
        ind = ((u <= q) & (v <= q)).astype(float) - ((u > 1 - q) & (v > 1 - q)).astype(float)
        blk = max(1.0, float(optimal_block_length(ind)['stationary'].iloc[0]))
        L0, U0 = empirical_tail_dep(u, v, q)
        db = []
        for _ in range(B):
            Ub = pseudo_obs(X[stationary_bootstrap_idx(len(X), blk, rng)])
            lb, ub = empirical_tail_dep(Ub[:, 0], Ub[:, 1], q)
            db.append(lb - ub)
        db = np.array(db)
        ac = [np.corrcoef(ind[:-l], ind[l:])[0, 1] for l in range(1, 11)]
        N.update({f'tsb_blk{tag}': blk, f'tsb_lo{tag}': np.percentile(db, 2.5), f'tsb_hi{tag}': np.percentile(db, 97.5),
                  f'tsb_se{tag}': db.std(ddof=1), f'tsb_acmax{tag}': float(np.max(np.abs(ac)))})
    N['tsb_B'] = B


def gas_null_bootstrap(B=199):
    """Seminarul, B6: p-valoarea raportului de verosimilitate GAS contra t static, prin bootstrap parametric sub copula t
    statica estimata (n perechi simulate, transformate in pseudo-observatii, ambele modele reestimate)."""
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    U2 = pseudo_obs(W.values)
    g = gas_t_copula(U2[:, 0], U2[:, 1])
    lr_obs = g['lr']
    rng = np.random.default_rng(SEED)
    lrs = []
    for _ in range(B):
        Us = pseudo_obs(simulate('t', [g['rho_static'], g['nu_static']], len(U2), rng))
        lrs.append(gas_t_copula(Us[:, 0], Us[:, 1])['lr'])
    lrs = np.array(lrs)
    N.update(b6g_lr_obs=lr_obs, b6g_lr_null_q95=np.percentile(lrs, 95), b6g_lr_null_max=lrs.max(),
             b6g_p_boot=(1 + np.sum(lrs >= lr_obs)) / (B + 1), b6g_B=B)


def save(path='ch6_inference_numbers.json'):
    """Adauga cifrele calculate la fisierul existent (etapele pot fi rulate separat)."""
    fn = os.path.join(HERE, path)
    out = json.load(open(fn)) if os.path.exists(fn) else {}
    for k, v in N.items():
        out[k] = float(v) if isinstance(v, (np.floating, float)) else (int(v) if isinstance(v, (np.integer, int)) else v)
    with open(fn, 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f'saved {path} ({len(out)} numbers)')


STAGES = {
    'corr': lambda: (fig_corr_hac(), fig_wkd()),
    'hedge': hedge_oos,
    'fr': lambda: (fr_bootstrap(CALM08, CRISIS08, '08'), fr_bootstrap(CALM20, CRISIS20, '20')),
    'rank': rank_inference,
    'gas': fig_gas_copula,
    'chenfan': chen_fan_mc,
    'twostep': two_step_bootstrap,
    'cccboot': lambda: (ccc_null_bootstrap(['spy', 'tlt'], 'cccb'), ccc_null_bootstrap(['btc', 'spy'], 'cccb_btc')),
    'tailblock': tail_symmetry_block,
    'gasboot': gas_null_bootstrap,
}

if __name__ == '__main__':
    for st in (sys.argv[1:] or list(STAGES)):
        STAGES[st]()
        save()

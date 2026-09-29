"""
Calculele pentru Seminarul 6: volatilitate multivariata si dependenta
=====================================================================
Partea A: dependenta in cozi (Gaussian vs t) pas cu pas, tau Kendall <-> parametrul copulei,
          corectia Forbes-Rigobon pe un exemplu numeric
Partea B: DCC pentru SPY-TLT (rezolvat), copula Gaussian vs t pentru S&P 500 / Euro Stoxx 50 (rezolvat),
          Clayton vs Gumbel pentru pierderile BET / Euro Stoxx 50 (propus), Forbes-Rigobon 2008 si 2020 (propus),
          DCC Bitcoin / S&P 500 cu benzi bootstrap (propus)
Partea C: au devenit piata romaneasca si cea din zona euro mai integrate dupa 2020? (analiza de referinta)
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats, integrate
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import SHORT, joint_returns, weekly_returns, joint_prices   # noqa: E402
from dep_tools import (garch_all, dcc_fit, dcc_path, fr_adjust, crisis_table, pseudo_obs, kendall_tau,  # noqa: E402
                       spearman_rho, theta_from_tau, tail_dep, simulate, fit_copula, gof_test, empirical_tail_dep,
                       fisher_z_test, FAM_LABEL)
from generate_all_charts import (save_fig, legend_outside_bottom, shade_crises, two_day_returns, MainBlue,  # noqa: E402
                                 IDAred, Forest, Amber, Gray, Purple, CALM08, CRISIS08, CALM20, CRISIS20, SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE_DIR = HERE
S = {}


# =============================================================================
# PARTEA A
# =============================================================================
def joint_tail_prob(q, rho, nu=None):
    """P(U <= q, V <= q) pentru copula Gaussiana (nu=None) sau t (nu grade de libertate), prin cuadratura
    unidimensionala deterministica: Y | X = x este Normal(rho x, 1 - rho^2), respectiv
    t_{nu+1}(rho x, (nu + x^2)(1 - rho^2)/(nu + 1))."""
    if nu is None:
        a = stats.norm.ppf(q)
        f = lambda x: stats.norm.pdf(x) * stats.norm.cdf((a - rho * x) / np.sqrt(1 - rho ** 2))
    else:
        a = stats.t.ppf(q, nu)
        f = lambda x: stats.t.pdf(x, nu) * stats.t.cdf((a - rho * x) / np.sqrt((nu + x * x) * (1 - rho ** 2) / (nu + 1)), nu + 1)
    return integrate.quad(f, -np.inf, a, epsabs=1e-14, epsrel=1e-10, limit=200)[0]


def a_tail_gauss_t(rho=0.5, nus=(3, 4, 10, 30)):
    """A1: lambda pentru copula t si probabilitatea conditionata P(V<=q | U<=q) la nivel finit."""
    out = {}
    for nu in nus:
        arg = np.sqrt((nu + 1) * (1 - rho) / (1 + rho))
        out[nu] = dict(arg=arg, lam=2 * stats.t.cdf(-arg, nu + 1))
    qs = np.array([0.10, 0.05, 0.01, 0.001])
    gauss = np.array([joint_tail_prob(q, rho) / q for q in qs])
    t4 = np.array([joint_tail_prob(q, rho, 4) / q for q in qs])
    return out, qs, gauss, t4


def fig_tail_gauss_t(rho=0.5):
    qs = np.geomspace(0.001, 0.2, 30)
    g = [joint_tail_prob(q, rho) / q for q in qs]
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(qs, g, color=MainBlue, lw=1.6, label='Gaussian copula (rho = 0.5)')
    for nu, c in ((4, IDAred), (10, Amber)):
        ax.plot(qs, [joint_tail_prob(q, rho, nu) / q for q in qs], color=c, lw=1.6, label=f't copula (rho = 0.5, nu = {nu})')
        lam = 2 * stats.t.cdf(-np.sqrt((nu + 1) * (1 - rho) / (1 + rho)), nu + 1)
        ax.axhline(lam, color=c, ls=':', lw=0.9)
    ax.set_xscale('log')
    ax.set_xticks([0.01, 0.02, 0.05, 0.1, 0.2])
    ax.set_xticklabels(['1%', '2%', '5%', '10%', '20%'])
    ax.set_xlabel('q (log scale)')
    ax.set_ylabel('P(V <= q | U <= q)')
    ax.set_ylim(0, 0.8)
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch6_sem_tail_gauss_t')


def a_tau_to_theta():
    """A2: tau Kendall pentru S&P 500 / Euro Stoxx 50 (randamente saptamanale) si parametrii implicati."""
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    U = pseudo_obs(W.values)
    tau = kendall_tau(U[:, 0], U[:, 1])
    out = dict(tau=tau, n=len(W), rhoS=spearman_rho(U[:, 0], U[:, 1]), pearson=W.corr().iloc[0, 1])
    for fam in ('gaussian', 'clayton', 'gumbel', 'frank'):
        th = theta_from_tau(fam, tau)
        out[fam] = th
        out[fam + '_lam'] = tail_dep(fam, [th])
    out['gauss_rhoS'] = 6 / np.pi * np.arcsin(out['gaussian'] / 2)
    return out, W, U


def a_forbes_rigobon_example(rho_calm=0.40, rho_crisis=0.60, var_ratio=4.0):
    delta = var_ratio - 1
    return dict(delta=delta, adj=fr_adjust(rho_crisis, delta), infl=rho_calm * np.sqrt((1 + delta) / (1 + delta * rho_calm ** 2)))


# =============================================================================
# PARTEA B
# =============================================================================
def b_dcc_spy_tlt():
    """B1: DCC pe tot esantionul si pe doua subperioade; LR fata de CCC; schimbarea corelatiei medii a lui z."""
    R = joint_returns(['spy', 'tlt'])
    P, V, Z, ll = garch_all(R)
    full = dcc_fit(Z)
    sub = {}
    for lab, sl in (('pre', slice(None, '2019-12-31')), ('post', slice('2020-01-01', None))):
        Rs = R.loc[sl]
        Ps, Vs, Zs, _ = garch_all(Rs)
        sub[lab] = dcc_fit(Zs)
        sub[lab]['n'] = len(Zs)
    z0, z1 = Z.loc[:'2021-12-31'], Z.loc['2022-01-01':]
    r0, r1 = z0.corr().iloc[0, 1], z1.corr().iloc[0, 1]
    zt, _ = fisher_z_test(r1, len(z1), r0, len(z0))
    return dict(full=full, sub=sub, r0=r0, r1=r1, zt=zt, p2=2 * (1 - stats.norm.cdf(abs(zt))),
                lr=2 * (full['loglik'] - full['ccc_loglik']), n=len(Z), P=P)


def b_gauss_vs_t(W, U, B=200, B_test=499):
    """B2: Gaussian vs t pentru S&P 500 / Euro Stoxx 50 saptamanal: ML, LR pentru nu, adecvare, IC bootstrap pentru lambda.
    Testele (adecvare si LR) folosesc B_test = 499 replicari, deci p-valoarea minima posibila este 1/500 = 0.002."""
    u, v = U[:, 0], U[:, 1]
    fg, ft = fit_copula('gaussian', u, v), fit_copula('t', u, v)
    gg = gof_test('gaussian', u, v, B=B_test, seed=SEED, fit=fg)
    gt = gof_test('t', u, v, B=B_test, seed=SEED, fit=ft)
    lr = 2 * (ft['loglik'] - fg['loglik'])
    rng = np.random.default_rng(SEED)
    lam_b, nu_b = [], []
    for _ in range(B):
        X = pseudo_obs(simulate('t', ft['par'], len(u), rng))
        fb = fit_copula('t', X[:, 0], X[:, 1])
        lam_b.append(fb['lamL'])
        nu_b.append(fb['par'][1])
    lam_b, nu_b = np.array(lam_b), np.array(nu_b)
    # p-valoarea LR prin bootstrap parametric sub H0 (copula Gaussiana), pentru ca nu = infinit e pe frontiera
    lr_b = []
    for _ in range(B_test):
        X = pseudo_obs(simulate('gaussian', fg['par'], len(u), rng))
        lr_b.append(2 * (fit_copula('t', X[:, 0], X[:, 1])['loglik'] - fit_copula('gaussian', X[:, 0], X[:, 1])['loglik']))
    lr_b = np.array(lr_b)
    return dict(fg=fg, ft=ft, gg=gg, gt=gt, lr=lr, lr_p_boot=(1 + np.sum(lr_b >= lr)) / (len(lr_b) + 1),
                lr_p_chi2half=0.5 * (1 - stats.chi2.cdf(lr, 1)), lam_ci=np.percentile(lam_b, [5, 95]),
                nu_ci=np.percentile(nu_b, [5, 95]), emp=[empirical_tail_dep(u, v, q) for q in (0.05, 0.10)],
                lr_b=lr_b, lam_b=lam_b, nu_b=nu_b)


def b_losses_copula(B=200):
    """B3: pierderile zilnice BET / Euro Stoxx 50 (L = -r), filtrate GARCH: Clayton vs Gumbel (plus Gaussiana si t)
    cu test de adecvare. Gumbel pe pierderi = dependenta in coada superioara a pierderilor."""
    R = joint_returns(['bet', 'stoxx'], start='2010-01-01')
    P, V, Z, _ = garch_all(R)
    L = -Z
    U = pseudo_obs(L.values)
    u, v = U[:, 0], U[:, 1]
    res = {}
    for fam in ('clayton', 'gumbel', 'gaussian', 't'):
        f = fit_copula(fam, u, v)
        g = gof_test(fam, u, v, B=100 if fam == 't' else B, seed=SEED, fit=f)
        res[fam] = dict(fit=f, gof=g)
    emp = {q: empirical_tail_dep(u, v, q) for q in (0.05, 0.10)}
    return dict(res=res, tau=kendall_tau(u, v), n=len(U), start=str(R.index[0].date()), emp=emp, U=U)


def fig_losses_copula(U, res):
    u, v = U[:, 0], U[:, 1]
    fig, ax = plt.subplots(figsize=(4.2, 3.4))
    inner = ~((u > 0.9) & (v > 0.9)) & ~((u < 0.1) & (v < 0.1))
    ax.scatter(u[inner], v[inner], s=1.5, color=MainBlue, alpha=0.25, label='All days')
    m = (u > 0.9) & (v > 0.9)
    ax.scatter(u[m], v[m], s=3, color=IDAred, label='Joint large losses (both > 0.9)')
    m = (u < 0.1) & (v < 0.1)
    ax.scatter(u[m], v[m], s=3, color=Forest, label='Joint large gains (both < 0.1)')
    ax.set_xlabel('BET loss (uniform scale)')
    ax.set_ylabel('Euro Stoxx 50 loss (uniform scale)')
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch6_sem_losses_copula')


def b_forbes_rigobon():
    """B4: Forbes-Rigobon pentru 2008 si 2020, S&P 500 -> Euro Stoxx 50 si BET, plus sensibilitatea la fereastra."""
    r2 = two_day_returns(['sp500', 'stoxx', 'bet'])
    t08 = crisis_table(r2, 'sp500', ['stoxx', 'bet'], CALM08, CRISIS08)
    t20 = crisis_table(r2, 'sp500', ['stoxx', 'bet'], CALM20, CRISIS20)
    t20b = crisis_table(r2, 'sp500', ['stoxx', 'bet'], CALM20, ('2020-02-20', '2020-03-31'))
    t08b = crisis_table(r2, 'sp500', ['stoxx', 'bet'], CALM08, ('2008-09-15', '2008-12-31'))
    for t, n in ((t08, '2008'), (t20, '2020'), (t20b, '2020_short'), (t08b, '2008_short')):
        t.to_csv(os.path.join(TABLE_DIR, f'ch6_sem_fr_{n}.csv'), float_format='%.6g')
    return t08, t20, t20b, t08b


def stationary_bootstrap_idx(n, mean_block, rng):
    """Indicii unui bootstrap stationar (Politis-Romano): blocuri de lungime geometrica."""
    idx = np.empty(n, dtype=int)
    idx[0] = rng.integers(n)
    for t in range(1, n):
        idx[t] = rng.integers(n) if rng.uniform() < 1 / mean_block else (idx[t - 1] + 1) % n
    return idx


def simulate_dcc2(a, b, Qbar, eta):
    """Simuleaza reziduuri standardizate bivariate dintr-un DCC(1,1) cu inovatii decorelate eta (T x 2)."""
    T = len(eta)
    eps = np.empty_like(eta)
    q11, q22, q12 = Qbar[0, 0], Qbar[1, 1], Qbar[0, 1]
    c = 1 - a - b
    for t in range(T):
        r = q12 / np.sqrt(q11 * q22)
        eps[t, 0] = eta[t, 0]
        eps[t, 1] = r * eta[t, 0] + np.sqrt(1 - r * r) * eta[t, 1]
        q11 = c * Qbar[0, 0] + a * eps[t, 0] ** 2 + b * q11
        q22 = c * Qbar[1, 1] + a * eps[t, 1] ** 2 + b * q22
        q12 = c * Qbar[0, 1] + a * eps[t, 0] * eps[t, 1] + b * q12
    return eps


def b_btc_bands(B=200):
    """B5: DCC Bitcoin / S&P 500 cu benzi bootstrap pentru incertitudinea parametrilor (a, b).
    Bootstrap parametric cu reziduuri: inovatiile decorelate eta_t = L_t^{-1} eps_t (L_t Cholesky al lui R_t)
    se extrag cu intoarcere, se simuleaza un DCC cu parametrii estimati, se reestimeaza (a, b),
    iar traiectoria R_t se recalculeaza pe datele originale cu parametrii bootstrap."""
    R = joint_returns(['btc', 'sp500'], start='2014-09-17')
    P, V, Z, _ = garch_all(R)
    d = dcc_fit(Z)
    X = Z.values
    Rt = d['R']
    L = np.linalg.cholesky(Rt)
    eta = np.linalg.solve(L, X[:, :, None])[:, :, 0]
    eta = (eta - eta.mean(0)) / eta.std(0)
    rng = np.random.default_rng(SEED)
    paths, ab = [], []
    for _ in range(B):
        eb = eta[rng.integers(0, len(eta), len(eta))]
        Xb = simulate_dcc2(d['a'], d['b'], d['Qbar'], eb)
        db = dcc_fit(pd.DataFrame(Xb))
        Rb = dcc_path(X, db['a'], db['b'], d['Qbar'])       # traiectoria pe datele originale cu parametrii bootstrap
        paths.append(Rb[:, 0, 1])
        ab.append((db['a'], db['b']))
    paths, ab = np.array(paths), np.array(ab)
    rc = pd.Series(d['R'][:, 0, 1], index=Z.index)
    lo = pd.Series(np.percentile(paths, 5, axis=0), index=Z.index)
    hi = pd.Series(np.percentile(paths, 95, axis=0), index=Z.index)
    return dict(d=d, rc=rc, lo=lo, hi=hi, ab=ab, n=len(Z), start=str(Z.index[0].date()), paths=paths)


def fig_btc_bands(o):
    rc, lo, hi = o['rc'], o['lo'], o['hi']
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.fill_between(rc.index, lo, hi, color=Amber, alpha=0.3, lw=0, label='90% residual-bootstrap band (uncertainty in a and b)')
    ax.plot(rc.index, rc, color=IDAred, lw=0.7, label='DCC(1,1) correlation Bitcoin / S&P 500')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Conditional correlation')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_sem_btc_bands')


# =============================================================================
# PARTEA C: integrarea BET / Euro Stoxx 50 dupa 2020
# =============================================================================
def c_integration(B=2000, block=8):
    W = weekly_returns(['bet', 'stoxx'], start='2010-01-01')
    pre, post = W.loc[:'2019-12-31'], W.loc['2020-01-01':]
    r_pre, r_post = pre.corr().iloc[0, 1], post.corr().iloc[0, 1]
    # fara saptamanile de criza din martie-aprilie 2020
    post_x = post.drop(post.loc['2020-02-20':'2020-04-30'].index)
    r_post_x = post_x.corr().iloc[0, 1]
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(B):
        a = pre.values[stationary_bootstrap_idx(len(pre), block, rng)]
        b = post.values[stationary_bootstrap_idx(len(post), block, rng)]
        diffs.append(np.corrcoef(b.T)[0, 1] - np.corrcoef(a.T)[0, 1])
    diffs = np.array(diffs)
    # Forbes-Rigobon: volatilitatea Euro Stoxx 50 difera intre perioade
    delta = post['stoxx'].var() / pre['stoxx'].var() - 1
    adj = fr_adjust(r_post, delta)
    tau_pre = kendall_tau(pre['bet'], pre['stoxx'])
    tau_post = kendall_tau(post['bet'], post['stoxx'])
    Up, Uq = pseudo_obs(pre.values), pseudo_obs(post.values)
    lamL_pre = empirical_tail_dep(Up[:, 0], Up[:, 1], 0.10)[0]
    lamL_post = empirical_tail_dep(Uq[:, 0], Uq[:, 1], 0.10)[0]
    # DCC pe randamente saptamanale
    P, V, Z, _ = garch_all(W)
    d = dcc_fit(Z)
    rc = pd.Series(d['R'][:, 0, 1], index=Z.index)
    # beta al BET fata de Euro Stoxx 50 (canal de transmisie, independent de nivelul volatilitatii BET)
    beta = lambda D: np.cov(D['bet'], D['stoxx'])[0, 1] / D['stoxx'].var()
    # daily: sincron (ambele se inchid dupa-amiaza, ora Europei Centrale)
    Rd = joint_returns(['bet', 'stoxx'], start='2010-01-01')
    rd_pre, rd_post = Rd.loc[:'2019-12-31'].corr().iloc[0, 1], Rd.loc['2020-01-01':].corr().iloc[0, 1]
    return dict(n_pre=len(pre), n_post=len(post), r_pre=r_pre, r_post=r_post, r_post_x=r_post_x,
                diff=r_post - r_pre, ci=np.percentile(diffs, [2.5, 97.5]), p_boot=np.mean(diffs <= 0),
                delta=delta, adj=adj, tau_pre=tau_pre, tau_post=tau_post, lamL_pre=lamL_pre, lamL_post=lamL_post,
                dcc_a=d['a'], dcc_b=d['b'], dcc_pre=rc.loc[:'2019-12-31'].mean(), dcc_post=rc.loc['2020-01-01':].mean(),
                beta_pre=beta(pre), beta_post=beta(post), rd_pre=rd_pre, rd_post=rd_post, rc=rc, W=W, diffs=diffs)


def fig_integration_c(o):
    W, rc = o['W'], o['rc']
    roll = W['bet'].rolling(52).corr(W['stoxx'])
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(rc.index, rc, color=IDAred, lw=0.8, label='DCC(1,1), weekly returns')
    ax.plot(roll.index, roll, color=MainBlue, lw=1.3, label='52-week rolling correlation')
    ax.hlines(o['r_pre'], W.index[0], pd.Timestamp('2019-12-31'), color=Forest, lw=2, label='Sample correlation 2010-2019 / 2020-2026')
    ax.hlines(o['r_post'], pd.Timestamp('2020-01-01'), W.index[-1], color=Forest, lw=2)
    ax.axvline(pd.Timestamp('2020-09-21'), color=Gray, ls='--', lw=0.9, label='FTSE Russell upgrade effective (Sep 2020)')
    ax.set_ylabel('Correlation BET / Euro Stoxx 50')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch6_sem_integration')


# =============================================================================
# GRAFICE NOI: setup, B1, B2, A2, A3, A5, A6, B3, B4, B5, B6, C1
# =============================================================================
TEAL = '#17A2B8'


def s_manifest():
    """Numarul de randuri si perioada fiecarui set de date al seminarului (verificarea de la inceput)."""
    out = {}
    R = joint_returns(['spy', 'tlt'])
    out.update(man_b1_n=len(R), man_b1_start=str(R.index[0].date()), man_b1_end=str(R.index[-1].date()))
    for i in range(3):
        out[f'man_b1_date{i}'] = str(R.index[i].date())
        out[f'man_b1_spy{i}'] = 100 * R['spy'].iloc[i]
        out[f'man_b1_tlt{i}'] = 100 * R['tlt'].iloc[i]
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    out.update(man_a2_n=len(W), man_a2_start=str(W.index[0].date()), man_a2_end=str(W.index[-1].date()))
    Rb = joint_returns(['bet', 'stoxx'], start='2010-01-01')
    out.update(man_b3_n=len(Rb), man_b3_start=str(Rb.index[0].date()), man_b3_end=str(Rb.index[-1].date()))
    r2 = two_day_returns(['sp500', 'stoxx', 'bet'])
    out.update(man_b4_n=len(r2), man_b4_start=str(r2.index[0].date()), man_b4_end=str(r2.index[-1].date()))
    Rc = joint_returns(['btc', 'sp500'], start='2014-09-17')
    out.update(man_b5_n=len(Rc), man_b5_start=str(Rc.index[0].date()), man_b5_end=str(Rc.index[-1].date()))
    Wc = weekly_returns(['bet', 'stoxx'], start='2010-01-01')
    out.update(man_c1_n=len(Wc), man_c1_start=str(Wc.index[0].date()), man_c1_end=str(Wc.index[-1].date()))
    return out


def acf_sq(x, lags=20):
    """Autocorelatiile patratelor x_t^2 la decalajele 1..lags."""
    y = np.asarray(x, float) ** 2
    y = y - y.mean()
    return np.array([np.sum(y[k:] * y[:-k]) / np.sum(y * y) for k in range(1, lags + 1)])


def b1_filter_check(R):
    """B1, pasul 1: GARCH(1,1) pe fiecare serie; autocorelatia patratelor inainte si dupa filtrare;
    un pas al recursiei DCC (Q_2 din Q_1 = Qbar si z_1)."""
    P, V, Z, _ = garch_all(R)
    d = dcc_fit(Z)
    out = {}
    for c in R.columns:
        a_raw, a_z = acf_sq(R[c]), acf_sq(Z[c])
        out.update({f'b1c_{c}_acf1_raw': a_raw[0], f'b1c_{c}_acf1_z': a_z[0],
                    f'b1c_{c}_acfm_raw': a_raw.mean(), f'b1c_{c}_acfm_z': a_z.mean(),
                    f'b1c_{c}_vol_mean': V[c].mean() * np.sqrt(252), f'b1c_{c}_vol_max': V[c].max() * np.sqrt(252),
                    f'b1c_{c}_vol_max_date': str(V[c].idxmax().date()), f'b1c_{c}_zsd': Z[c].std()})
    Qb = d['Qbar']
    z1 = Z.values[0]
    Q2 = (1 - d['a'] - d['b']) * Qb + d['a'] * np.outer(z1, z1) + d['b'] * Qb
    out.update(b1c_q11=Qb[0, 0], b1c_q22=Qb[1, 1], b1c_q12=Qb[0, 1], b1c_z1a=z1[0], b1c_z1b=z1[1],
               b1c_Q2_11=Q2[0, 0], b1c_Q2_22=Q2[1, 1], b1c_Q2_12=Q2[0, 1],
               b1c_R2_12=Q2[0, 1] / np.sqrt(Q2[0, 0] * Q2[1, 1]), b1c_R2_12_path=d['R'][1, 0, 1],
               b1c_date1=str(Z.index[0].date()), b1c_date2=str(Z.index[1].date()))
    return P, V, Z, d, out


def fig_b1_returns(R):
    """B1: randamentele zilnice SPY si TLT pe zilele comune, cu ferestrele de stres."""
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 4.0), sharex=True)
    for ax, c, col, lab in ((axes[0], 'spy', MainBlue, 'SPY daily log return (%)'),
                            (axes[1], 'tlt', IDAred, 'TLT daily log return (%)')):
        shade_crises(ax)
        ax.plot(R.index, 100 * R[c], color=col, lw=0.4, label=lab)
        ax.axhline(0, color='black', lw=0.5)
        ax.set_ylabel('%')
    axes[1].plot([], [], color=Gray, alpha=0.35, lw=6, label='2008-09, 2020 and 2022 stress windows')
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.04), ncol=2, frameon=False)
    save_fig('ch6_sem_b1_returns')


def fig_b1_garch(R, V, Z):
    """B1: volatilitatea GARCH anualizata si autocorelatia patratelor inainte si dupa standardizare."""
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 4.8))
    ax = axes[0]
    shade_crises(ax)
    ax.plot(V.index, V['spy'] * np.sqrt(252), color=MainBlue, lw=0.7, label='SPY GARCH volatility')
    ax.plot(V.index, V['tlt'] * np.sqrt(252), color=IDAred, lw=0.7, label='TLT GARCH volatility')
    ax.set_ylabel('Annualised vol. (%)')
    ax = axes[1]
    k = np.arange(1, 21)
    ax.plot(k, acf_sq(R['spy']), color=MainBlue, lw=1.4, marker='o', ms=2.5, label='SPY returns squared')
    ax.plot(k, acf_sq(Z['spy']), color=MainBlue, lw=1.0, ls='--', marker='o', ms=2.5, label='SPY residuals squared')
    ax.plot(k, acf_sq(R['tlt']), color=IDAred, lw=1.4, marker='s', ms=2.5, label='TLT returns squared')
    ax.plot(k, acf_sq(Z['tlt']), color=IDAred, lw=1.0, ls='--', marker='s', ms=2.5, label='TLT residuals squared')
    ax.axhline(0, color='black', lw=0.5)
    ax.axhline(1.96 / np.sqrt(len(Z)), color=Gray, ls=':', lw=0.8)
    ax.set_xlabel('Lag (days)')
    ax.set_ylabel('Autocorrelation of squares')
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.tight_layout()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch6_sem_b1_garch')


def b1_ccc_null_lr(R, B=199):
    """B1: distributia statisticii LR (DCC contra CCC) sub H0: CCC, prin bootstrap parametric al ambilor pasi
    (aceeasi procedura si acelasi generator ca in inference_ch6.ccc_null_bootstrap)."""
    try:
        from inference_ch6 import simulate_garch
    except ImportError:   # notebook autonom: functia este definita mai sus
        simulate_garch = globals()['simulate_garch']
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
    return lr_obs, np.array(lrs)


def fig_b1_lr(lr_obs, lrs):
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    bins = np.linspace(0, max(lrs.max(), 1) * 1.05, 30)
    ax.hist(lrs, bins=bins, color=MainBlue, alpha=0.75, label=f'LR under H0: CCC ({len(lrs)} bootstrap paths)')
    q95 = np.percentile(lrs, 95)
    ax.axvline(q95, color=Amber, ls='--', lw=1.2, label=f'95% null quantile = {q95:.1f}')
    ax.annotate(f'observed LR = {lr_obs:.1f}\n(far off this scale)', xy=(bins[-1], 0), xytext=(0.72, 0.55),
                textcoords='axes fraction', color=IDAred, fontsize=8,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=1.0))
    ax.set_xlabel('LR = 2 (log-lik DCC - log-lik CCC)')
    ax.set_ylabel('Number of paths')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch6_sem_b1_lr')


def fig_b2_scatter(W, U, q=0.05):
    """A2/B2: randamentele saptamanale si pseudo-observatiile lor, cu colturile de 5% marcate."""
    u, v = U[:, 0], U[:, 1]
    fig, axes = plt.subplots(1, 2, figsize=(5.8, 3.0))
    ax = axes[0]
    ax.scatter(100 * W.iloc[:, 0], 100 * W.iloc[:, 1], s=3, color=MainBlue, alpha=0.45, label='Weekly returns')
    ax.set_xlabel('S&P 500 weekly log return (%)')
    ax.set_ylabel('Euro Stoxx 50 weekly log return (%)')
    ax = axes[1]
    low, up = (u <= q) & (v <= q), (u > 1 - q) & (v > 1 - q)
    mid = ~(low | up)
    ax.scatter(u[mid], v[mid], s=3, color=MainBlue, alpha=0.45)
    ax.scatter(u[low], v[low], s=5, color=IDAred, label=f'Both below {q:.0%}: {low.sum()} weeks')
    ax.scatter(u[up], v[up], s=5, color=Forest, label=f'Both above {1 - q:.0%}: {up.sum()} weeks')
    for x0 in (0, 1 - q):
        ax.add_patch(plt.Rectangle((x0, x0), q, q, fill=False, ec='black', lw=0.7))
    ax.set_xlabel('S&P 500 pseudo-observation u')
    ax.set_ylabel('Euro Stoxx 50 pseudo-observation v')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.tight_layout()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch6_sem_b2_scatter')
    return int(low.sum()), int(up.sum())


def fig_b2_tails(U, fg, ft):
    """B2: probabilitatile la prag finit C(q,q)/q, empirice si din copulele estimate, cu lambda separat."""
    u, v = U[:, 0], U[:, 1]
    qs = np.geomspace(0.01, 0.20, 25)
    emp = np.array([empirical_tail_dep(u, v, q) for q in qs])
    g = np.array([joint_tail_prob(q, fg['par'][0]) / q for q in qs])
    t = np.array([joint_tail_prob(q, ft['par'][0], ft['par'][1]) / q for q in qs])
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(qs, emp[:, 0], color=IDAred, lw=0, marker='o', ms=3, label='Empirical, joint losses (lower corner)')
    ax.plot(qs, emp[:, 1], color=Forest, lw=0, marker='s', ms=3, label='Empirical, joint gains (upper corner)')
    ax.plot(qs, g, color=MainBlue, lw=1.5, label=f'Fitted Gaussian copula (rho = {fg["par"][0]:.3f})')
    ax.plot(qs, t, color=Amber, lw=1.5, label=f'Fitted t copula (rho = {ft["par"][0]:.3f}, nu = {ft["par"][1]:.2f})')
    ax.axhline(ft['lamL'], color=Amber, ls=':', lw=1.0, label=f'Limit lambda of the t copula = {ft["lamL"]:.3f}')
    ax.set_xscale('log')
    ax.set_xticks([0.01, 0.02, 0.05, 0.1, 0.2])
    ax.set_xticklabels(['1%', '2%', '5%', '10%', '20%'])
    ax.set_xlabel('q (log scale)')
    ax.set_ylabel('C(q, q) / q')
    ax.set_ylim(0, 1)
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch6_sem_b2_tails')
    return joint_tail_prob(0.05, fg['par'][0]) / 0.05, joint_tail_prob(0.05, ft['par'][0], ft['par'][1]) / 0.05


def fig_b2_boot(lr, lr_b, nu_b, lam_b, nu_hat, lam_hat):
    """B2 (extensie): LR sub H0 (Gaussiana) si distributiile bootstrap ale lui nu si lambda."""
    fig = plt.figure(figsize=(5.6, 4.4))
    gs = fig.add_gridspec(2, 2)
    axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    ax = axes[0]
    ax.hist(lr_b, bins=30, color=MainBlue, alpha=0.75, label=f'LR under H0: Gaussian ({len(lr_b)} draws)')
    ax.annotate(f'observed LR = {lr:.1f}\n(off scale)', xy=(ax.get_xlim()[1], 0), xytext=(0.35, 0.6),
                textcoords='axes fraction', color=IDAred, fontsize=7.5, arrowprops=dict(arrowstyle='->', color=IDAred))
    ax.set_xlabel('LR, H0: nu = infinity')
    ax.set_ylabel('Draws')
    for ax, x, hat, lab, col in ((axes[1], nu_b, nu_hat, 'nu', Forest), (axes[2], lam_b, lam_hat, 'lambda', Amber)):
        lo, hi = np.percentile(x, [5, 95])
        ax.hist(x, bins=30, color=col, alpha=0.75, label=f'{lab}: fitted-t bootstrap ({len(x)} draws)')
        ax.axvline(hat, color='black', lw=1.0)
        ax.axvline(lo, color=IDAred, ls='--', lw=0.9)
        ax.axvline(hi, color=IDAred, ls='--', lw=0.9)
        ax.set_xlabel(f'Bootstrap {lab}')
    axes[2].plot([], [], color=IDAred, ls='--', label='90% percentile interval')
    axes[2].plot([], [], color='black', label='Estimate')
    hs, ls_ = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        hs += h
        ls_ += l
    fig.tight_layout()
    fig.legend(hs, ls_, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch6_sem_b2_boot')


def a2_gap_draws():
    """A2 (e): bootstrap i.i.d. al perechilor saptamanale pentru diferenta rho_S implicat (Gaussiana) - rho_S empiric.
    Acelasi generator ca inference_ch6.rank_inference: se consuma intai extragerile pentru bancile JPM-BAC."""
    try:
        from generate_all_charts import bank_copula_data
    except ImportError:   # notebook autonom: functia este definita mai sus
        bank_copula_data = globals()['bank_copula_data']
    _, Zb, _ = bank_copula_data()
    rng = np.random.default_rng(SEED)
    nb = len(Zb)
    for _ in range(2 * 999):
        rng.integers(0, nb, nb)
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    U2 = pseudo_obs(W.values)
    rs_impl = lambda t: 6 / np.pi * np.arcsin(np.sin(np.pi * t / 2) / 2)
    diff = rs_impl(kendall_tau(U2[:, 0], U2[:, 1])) - spearman_rho(U2[:, 0], U2[:, 1])
    bs = []
    for _ in range(1999):
        i = rng.integers(0, len(W), len(W))
        Ub = pseudo_obs(W.values[i])
        bs.append(rs_impl(kendall_tau(Ub[:, 0], Ub[:, 1])) - spearman_rho(Ub[:, 0], Ub[:, 1]))
    return diff, np.array(bs)


def fig_a2_gap(diff, bs):
    lo, hi = np.percentile(bs, [2.5, 97.5])
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.hist(bs, bins=40, color=MainBlue, alpha=0.75, label=f'Bootstrap gap ({len(bs)} draws of the weekly pairs)')
    ax.axvline(diff, color='black', lw=1.2, label=f'Sample gap = {diff:.4f}')
    ax.axvline(lo, color=IDAred, ls='--', lw=1.0, label=f'95% interval [{lo:.4f}, {hi:.4f}]')
    ax.axvline(hi, color=IDAred, ls='--', lw=1.0)
    ax.axvline(0, color=Amber, lw=1.4, label='Zero: no gap')
    ax.set_xlabel('Gaussian-implied Spearman rho minus sample Spearman rho')
    ax.set_ylabel('Draws')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch6_sem_a2_gap')


def fig_a3_curve(rho_calm=0.40, rho_crisis=0.60, var_ratio=4.0):
    """A3: corelatia masurata in criza in functie de delta; cifrele stilizate ale exercitiului."""
    delta = var_ratio - 1
    adj = fr_adjust(rho_crisis, delta)
    infl = rho_calm * np.sqrt((1 + delta) / (1 + delta * rho_calm ** 2))
    d = np.linspace(0, 6, 200)
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(d, rho_calm * np.sqrt((1 + d) / (1 + d * rho_calm ** 2)), color=MainBlue, lw=1.6,
            label=f'Measured correlation if the true one stays {rho_calm:.2f}')
    ax.plot(d, adj * np.sqrt((1 + d) / (1 + d * adj ** 2)), color=Forest, lw=1.4, ls='--',
            label=f'Measured correlation if the true one is {adj:.3f}')
    ax.scatter([0], [rho_calm], color=MainBlue, s=30, zorder=5, label=f'Calm: {rho_calm:.2f}')
    ax.scatter([delta], [rho_crisis], color=IDAred, s=36, zorder=5, label=f'Observed crisis: {rho_crisis:.2f}')
    ax.scatter([delta], [infl], color=MainBlue, marker='D', s=30, zorder=5, label=f'Volatility alone: {infl:.3f}')
    ax.axvline(delta, color=Gray, ls=':', lw=0.9)
    ax.set_xlabel('delta = Var(crisis) / Var(calm) - 1 of the source market')
    ax.set_ylabel('Measured correlation')
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch6_sem_a3_curve')
    return adj, infl


def fig_a3_se(INF):
    """A3 (extensie): intervale de 95% pentru rho* in 2008, cu delta fixat si cu delta aleator."""
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    for k, (tg, lab) in enumerate((('stoxx', 'Euro Stoxx 50'), ('bet', 'BET'))):
        adj, r0 = INF[f'frb_08_{tg}_adj'], INF[f'frb_08_{tg}_r0']
        for j, (key, col, name) in enumerate((('se_fix', MainBlue, 'delta fixed'), ('se_rand', IDAred, 'delta random'))):
            y = k + (j - 0.5) * 0.25
            se = INF[f'frb_08_{tg}_{key}']
            ax.errorbar(adj, y, xerr=1.96 * se, fmt='o', color=col, capsize=3, ms=4,
                        label=f'rho* with 95% interval, {name}' if k == 0 else None)
        ax.scatter([r0], [k], marker='|', s=300, color=Forest, label='Calm correlation' if k == 0 else None)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Euro Stoxx 50', 'BET'])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel('Correlation with the S&P 500, 2-day returns, 2008 crisis')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch6_sem_a3_se')


def a5_dcc_numbers(a, b, qbar, eps=(-2.0, 1.0), H=150, M=4000):
    """A5: o actualizare Q -> R cu tinta [[1, qbar], [qbar, 1]] si raspunsul la un soc: Monte Carlo condiționat
    (aceleasi inovatii cu si fara soc) comparat cu aproximarea geometrica (a + b)^k."""
    Qb = np.array([[1.0, qbar], [qbar, 1.0]])
    e = np.array(eps)
    Q1 = (1 - a - b) * Qb + a * np.outer(e, e) + b * Qb
    R1 = Q1[0, 1] / np.sqrt(Q1[0, 0] * Q1[1, 1])
    rng = np.random.default_rng(SEED)
    dev_r, dev_q = np.zeros(H), np.zeros(H)
    for _ in range(M):
        Qs, Qn = Q1.copy(), Qb.copy()
        z = rng.standard_normal((H, 2))
        for h in range(H):
            rs = Qs[0, 1] / np.sqrt(Qs[0, 0] * Qs[1, 1])
            rn = Qn[0, 1] / np.sqrt(Qn[0, 0] * Qn[1, 1])
            dev_r[h] += rs - rn
            dev_q[h] += Qs[0, 1] - Qn[0, 1]
            es = np.array([z[h, 0], rs * z[h, 0] + np.sqrt(1 - rs * rs) * z[h, 1]])
            en = np.array([z[h, 0], rn * z[h, 0] + np.sqrt(1 - rn * rn) * z[h, 1]])
            Qs = (1 - a - b) * Qb + a * np.outer(es, es) + b * Qs
            Qn = (1 - a - b) * Qb + a * np.outer(en, en) + b * Qn
    dev_r, dev_q = dev_r / M, dev_q / M
    hl_geo = np.log(0.5) / np.log(a + b)
    hl_mc = int(np.argmax(dev_r / dev_r[0] <= 0.5))
    return dict(Q1=Q1, R1=R1, dev_r=dev_r, dev_q=dev_q, hl_geo=hl_geo, hl_mc=hl_mc, eps=e, Qb=Qb, a=a, b=b)


def fig_a5_dcc(o):
    H = len(o['dev_r'])
    k = np.arange(H)
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot(k, o['dev_r'] / o['dev_r'][0], color=IDAred, lw=1.6, label='Correlation R12: average response (Monte Carlo)')
    ax.plot(k, o['dev_q'] / o['dev_q'][0], color=MainBlue, lw=1.2, ls='--', label='Proxy Q12: average response')
    ax.plot(k, (o['a'] + o['b']) ** k, color=Amber, lw=1.2, ls=':', label='Geometric approximation (a + b)^k')
    ax.axhline(0.5, color=Gray, lw=0.7, ls=':')
    ax.axvline(o['hl_geo'], color=Gray, lw=0.7, ls=':')
    ax.set_xlabel('Days after the shock')
    ax.set_ylabel('Share of the initial deviation')
    ax.set_ylim(0, 1.05)
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch6_sem_a5_dcc')


def fig_a6_lognormal(n=2000):
    """A6: X = e^Z, Y = e^{2Z} (comonoton) si Y = e^{-2Z} (contramonoton): corelatia Pearson nu atinge +/-1."""
    rng = np.random.default_rng(SEED)
    z = rng.standard_normal(n)
    x = np.exp(z)
    den = np.sqrt((np.e - 1) * (np.e ** 4 - 1))
    rmax, rmin = (np.e ** 2 - 1) / den, (np.e ** -2 - 1) / den
    fig, axes = plt.subplots(1, 2, figsize=(5.8, 3.0))
    out = {}
    for ax, sgn, col, r, name in ((axes[0], 1, MainBlue, rmax, 'Y = exp(2Z), comonotone'),
                                  (axes[1], -1, IDAred, rmin, 'Y = exp(-2Z), countermonotone')):
        y = np.exp(sgn * 2 * z)
        rs = np.corrcoef(x, y)[0, 1]
        out['max' if sgn > 0 else 'min'] = rs
        ax.scatter(x, y, s=3, color=col, alpha=0.5,
                   label=f'{name}: Pearson {r:.3f} (population), {rs:.3f} (sample); Spearman {sgn:+d}')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('X = exp(Z) (log scale)')
        ax.set_ylabel('Y (log scale)')
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.tight_layout()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=1, frameon=False, fontsize=7)
    save_fig('ch6_sem_a6_lognormal')
    return out


def fig_b3_tails(U, res, n_sim=400000):
    """B3: probabilitatea pierderilor comune P(U > 1-q, V > 1-q)/q, empiric si din copulele estimate (simulare)."""
    u, v = U[:, 0], U[:, 1]
    qs = np.geomspace(0.01, 0.20, 20)
    emp = np.array([empirical_tail_dep(u, v, q)[1] for q in qs])
    rng = np.random.default_rng(SEED)
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(qs, emp, color='black', lw=0, marker='o', ms=3.5, label='Empirical, joint large losses')
    fit05 = {}
    for fam, col in (('gumbel', Amber), ('clayton', Forest), ('gaussian', MainBlue), ('t', IDAred)):
        X = simulate(fam, res[fam]['fit']['par'], n_sim, rng)
        up = np.array([np.mean((X[:, 0] > 1 - q) & (X[:, 1] > 1 - q)) / q for q in qs])
        fit05[fam] = np.mean((X[:, 0] > 0.95) & (X[:, 1] > 0.95)) / 0.05
        ax.plot(qs, up, color=col, lw=1.4, label=f'Fitted {FAM_LABEL.get(fam, fam)} on losses')
    ax.set_xscale('log')
    ax.set_xticks([0.01, 0.02, 0.05, 0.1, 0.2])
    ax.set_xticklabels(['1%', '2%', '5%', '10%', '20%'])
    ax.set_xlabel('q (log scale)')
    ax.set_ylabel('P(both losses above 1 - q) / q')
    ax.set_ylim(0, 1)
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch6_sem_b3_tails')
    return fit05


def fig_b4_windows():
    """B4: randamentele pe 2 zile ale S&P 500 cu ferestrele calma si de criza, 2008 si 2020."""
    r2 = two_day_returns(['sp500', 'stoxx', 'bet'])['sp500'] * 100
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 4.4))
    for ax, (calm, crisis, lo, hi) in zip(axes, ((CALM08, CRISIS08, '2007-06-01', '2009-09-30'),
                                                  (CALM20, CRISIS20, '2018-12-01', '2020-09-30'))):
        x = r2.loc[lo:hi]
        ax.axvspan(pd.Timestamp(calm[0]), pd.Timestamp(calm[1]), color=Forest, alpha=0.12, lw=0)
        ax.axvspan(pd.Timestamp(crisis[0]), pd.Timestamp(crisis[1]), color=IDAred, alpha=0.12, lw=0)
        ax.plot(x.index, x, color=MainBlue, lw=0.6)
        ax.axhline(0, color='black', lw=0.5)
        sd0, sd1 = r2.loc[calm[0]:calm[1]].std(), r2.loc[crisis[0]:crisis[1]].std()
        ax.set_title(f'sd calm {sd0:.2f}%, crisis {sd1:.2f}%', fontsize=8.5, color='black')
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.tick_params(axis='x', labelrotation=0, labelsize=7.5)
    axes[0].set_ylabel('2-day return (%)')
    axes[1].set_ylabel('2-day return (%)')
    axes[1].plot([], [], color=MainBlue, lw=1, label='S&P 500 2-day return')
    axes[1].fill_between([], [], color=Forest, alpha=0.25, label='Calm window (year before)')
    axes[1].fill_between([], [], color=IDAred, alpha=0.25, label='Crisis window')
    h, l = axes[1].get_legend_handles_labels()
    fig.tight_layout()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch6_sem_b4_windows')


def b4_fr_draws(B=1999, block=10):
    """B4 (c): extragerile bootstrap ale lui rho* si D = rho* - rho_calm (acelasi generator ca inference_ch6.fr_bootstrap)."""
    r2 = two_day_returns(['sp500', 'stoxx', 'bet'])
    out = {}
    for tag, calm, crisis in (('08', CALM08, CRISIS08), ('20', CALM20, CRISIS20)):
        c0, c1 = r2.loc[calm[0]:calm[1]], r2.loc[crisis[0]:crisis[1]]
        rng = np.random.default_rng(SEED)
        for tg in ('stoxx', 'bet'):
            j = list(r2.columns).index(tg)
            dif = []
            for _ in range(B):
                a = c0.values[stationary_bootstrap_idx(len(c0), block, rng)]
                b = c1.values[stationary_bootstrap_idx(len(c1), block, rng)]
                dl = b[:, 0].var(ddof=1) / a[:, 0].var(ddof=1) - 1
                adj = fr_adjust(np.corrcoef(b[:, 0], b[:, j])[0, 1], dl)
                dif.append((adj - np.corrcoef(a[:, 0], a[:, j])[0, 1], adj))
            out[(tag, tg)] = np.array(dif)
    return out


def fig_forbes_rigobon_sem(t08, t20, draws=None):
    """B4: corelatii calme, brute si corectate, cu intervalele bootstrap de 90% ale lui rho* (sus)
    si diferenta D = rho* - rho_calm cu intervalul ei (jos)."""
    labels, calm, raw, adj, lo, hi, D, Dlo, Dhi = [], [], [], [], [], [], [], [], []
    for yr, tag, t in (('2008', '08', t08), ('2020', '20', t20)):
        for k in t.index:
            labels.append(f'{SHORT[k]}\n{yr}')
            calm.append(t.loc[k, 'rho_calm'])
            raw.append(t.loc[k, 'rho_crisis'])
            adj.append(t.loc[k, 'rho_adj'])
            if draws is not None:
                dd = draws[(tag, k)]
                lo.append(np.percentile(dd[:, 1], 5))
                hi.append(np.percentile(dd[:, 1], 95))
                D.append(t.loc[k, 'rho_adj'] - t.loc[k, 'rho_calm'])
                Dlo.append(np.percentile(dd[:, 0], 5))
                Dhi.append(np.percentile(dd[:, 0], 95))
    x = np.arange(len(labels))
    if draws is None:
        fig, ax = plt.subplots(figsize=(6.8, 3.0))
        axes = [ax]
    else:
        fig, axes = plt.subplots(2, 1, figsize=(5.6, 5.2), gridspec_kw=dict(height_ratios=[1.3, 1]))
    ax = axes[0]
    ax.bar(x - 0.26, calm, 0.24, color=Forest, label='Calm year before')
    ax.bar(x, raw, 0.24, color=IDAred, label='Crisis, raw')
    ax.bar(x + 0.26, adj, 0.24, color=MainBlue, label='Crisis, Forbes-Rigobon adjusted')
    if draws is not None:
        ax.errorbar(x + 0.26, adj, yerr=[np.array(adj) - lo, np.array(hi) - adj], fmt='none', ecolor='black',
                    capsize=2.5, lw=0.9, label='90% bootstrap interval of the adjusted value')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylabel('Correlation with the S&P 500')
    if draws is not None:
        ax = axes[1]
        ax.errorbar(D, x, xerr=[np.array(D) - Dlo, np.array(Dhi) - D], fmt='o', color=Purple, capsize=3, ms=4,
                    label='D = adjusted - calm, 90% interval')
        ax.axvline(0, color='black', lw=0.8)
        ax.set_yticks(x)
        ax.set_yticklabels([l.replace('\n', ' ') for l in labels], fontsize=7.5)
        ax.invert_yaxis()
        ax.set_xlabel('D (contagion needs D > 0)')
    hs, ls_ = [], []
    for a_ in axes:
        h, l = a_.get_legend_handles_labels()
        hs += h
        ls_ += l
    fig.tight_layout()
    fig.legend(hs, ls_, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch6_sem_forbes_rigobon')
    return dict(D=D, Dlo=Dlo, Dhi=Dhi, lo=lo, hi=hi, labels=labels)


def b5_mean_change(o):
    """B5: diferenta mediilor corelatiei (dupa 2020 minus inainte), pe fiecare traiectorie bootstrap."""
    idx = o['rc'].index
    pre, post = idx <= pd.Timestamp('2019-12-31'), idx >= pd.Timestamp('2020-01-01')
    dm = o['paths'][:, post].mean(1) - o['paths'][:, pre].mean(1)
    return o['rc'][post].mean() - o['rc'][pre].mean(), np.percentile(dm, [5, 95])


def b6_gas_path():
    """B6: copula t GAS pe perechile saptamanale S&P 500 / Euro Stoxx 50 (aceeasi estimare ca inference_ch6)."""
    try:
        from inference_ch6 import gas_t_copula
    except ImportError:   # notebook autonom: functia este definita mai sus
        gas_t_copula = globals()['gas_t_copula']
    W = weekly_returns(['sp500', 'stoxx'], start='2000-01-01')
    U2 = pseudo_obs(W.values)
    g = gas_t_copula(U2[:, 0], U2[:, 1])
    return g, pd.Series(g['rho'], index=W.index)


def fig_b6_gas(g, rho):
    lam = 2 * stats.t.cdf(-np.sqrt((g['nu'] + 1) * (1 - rho) / (1 + rho)), g['nu'] + 1)
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    shade_crises(ax)
    ax.plot(rho.index, rho, color=IDAred, lw=0.9, label='GAS t copula: rho_t')
    ax.plot(rho.index, lam, color=MainBlue, lw=0.9, label='Implied tail dependence lambda_t')
    ax.axhline(g['rho_static'], color=IDAred, ls='--', lw=0.8, label=f'Static t copula rho = {g["rho_static"]:.3f}')
    for d_, c_ in ((rho.idxmin(), Forest), (rho.idxmax(), Amber)):
        ax.scatter([d_], [rho.loc[d_]], color=c_, s=25, zorder=5,
                   label=f'{"Minimum" if d_ == rho.idxmin() else "Maximum"} {rho.loc[d_]:.2f} ({d_.date()})')
    ax.set_ylabel('S&P 500 / Euro Stoxx 50')
    ax.set_ylim(0, 1)
    ax.plot([], [], color=Gray, alpha=0.35, lw=6, label='2008-09, 2020 and 2022 stress windows')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch6_sem_b6_gas')


def fig_c1_change(o):
    """C1: distributia bootstrap a schimbarii corelatiei si cele doua verificari de robustete."""
    d = o['diffs']
    lo, hi = o['ci']
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 4.8), gridspec_kw=dict(height_ratios=[1.2, 1]))
    ax = axes[0]
    ax.hist(d, bins=40, color=MainBlue, alpha=0.75, label=f'Stationary-bootstrap changes ({len(d)} draws)')
    ax.axvline(o['diff'], color='black', lw=1.2, label=f'Estimated change {o["diff"]:+.3f}')
    ax.axvline(lo, color=IDAred, ls='--', lw=1.0, label=f'95% interval [{lo:.3f}, {hi:.3f}]')
    ax.axvline(hi, color=IDAred, ls='--', lw=1.0)
    ax.axvline(0, color=Amber, lw=1.4)
    ax.set_xlabel('Weekly correlation 2020-2026 minus 2010-2019')
    ax.set_ylabel('Draws')
    ax = axes[1]
    vals = [o['r_pre'], o['r_post'], o['adj'], o['r_post_x']]
    labs = ['2010-2019', '2020-2026', '2020-2026,\nForbes-Rigobon', '2020-2026 without\nFeb-Apr 2020']
    cols = [Forest, IDAred, MainBlue, Purple]
    ax.barh(np.arange(4), vals, color=cols, height=0.6)
    for i, v_ in enumerate(vals):
        ax.text(v_ + 0.01, i, f'{v_:.3f}', va='center', fontsize=7.5, color='black')
    ax.set_yticks(np.arange(4))
    ax.set_yticklabels(labs, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.8)
    ax.set_xlabel('BET / Euro Stoxx 50 weekly correlation')
    h, l = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch6_sem_c1_change')


def fnum(x):
    if isinstance(x, (np.floating, float)):
        return float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    return x


if __name__ == '__main__':
    INF = json.load(open(os.path.join(TABLE_DIR, 'ch6_inference_numbers.json')))
    S.update(s_manifest())
    lam, qs, g, t4 = a_tail_gauss_t()
    for nu, dct in lam.items():
        S[f'a1_arg_{nu}'], S[f'a1_lam_{nu}'] = dct['arg'], dct['lam']
    for q, a, b in zip(qs, g, t4):
        S[f'a1_g_{q}'], S[f'a1_t4_{q}'] = a, b
    fig_tail_gauss_t()
    a2, W2, U2 = a_tau_to_theta()
    for k, v in a2.items():
        if isinstance(v, tuple):
            S[f'a2_{k}_L'], S[f'a2_{k}_U'] = v
        else:
            S[f'a2_{k}'] = v
    for k, v in a_forbes_rigobon_example().items():
        S[f'a3_{k}'] = v
    fig_a3_curve()
    fig_a3_se(INF)
    gap, gap_b = a2_gap_draws()
    assert abs(gap_b.std(ddof=1) - INF['a2_diff_se']) < 1e-12, 'A2 gap bootstrap differs from inference_ch6'
    fig_a2_gap(gap, gap_b)
    a5 = a5_dcc_numbers(INF['ts_a'], INF['ts_b'], json.load(open(os.path.join(TABLE_DIR, 'ch6_numbers.json')))['dcc_qbar'])
    fig_a5_dcc(a5)
    S.update(a5_q11=a5['Q1'][0, 0], a5_q22=a5['Q1'][1, 1], a5_q12=a5['Q1'][0, 1], a5_r12=a5['R1'],
             a5_hl_geo=a5['hl_geo'], a5_hl_mc=a5['hl_mc'], a5_e1=a5['eps'][0], a5_e2=a5['eps'][1])
    a6 = fig_a6_lognormal()
    S.update(a6_sample_max=a6['max'], a6_sample_min=a6['min'])
    b1 = b_dcc_spy_tlt()
    S.update(b1_a=b1['full']['a'], b1_b=b1['full']['b'], b1_se_a=b1['full']['se_a'], b1_se_b=b1['full']['se_b'],
             b1_lr=b1['lr'], b1_n=b1['n'], b1_r0=b1['r0'], b1_r1=b1['r1'], b1_zt=b1['zt'], b1_p2=b1['p2'],
             b1_pre_a=b1['sub']['pre']['a'], b1_pre_b=b1['sub']['pre']['b'], b1_pre_q=b1['sub']['pre']['Qbar'][0, 1],
             b1_post_a=b1['sub']['post']['a'], b1_post_b=b1['sub']['post']['b'], b1_post_q=b1['sub']['post']['Qbar'][0, 1],
             b1_pre_n=b1['sub']['pre']['n'], b1_post_n=b1['sub']['post']['n'],
             b1_hl=np.log(0.5) / np.log(b1['full']['a'] + b1['full']['b']))
    R1 = joint_returns(['spy', 'tlt'])
    fig_b1_returns(R1)
    P1, V1, Z1, d1, chk = b1_filter_check(R1)
    S.update(chk)
    fig_b1_garch(R1, V1, Z1)
    lr_obs, lrs = b1_ccc_null_lr(R1)
    assert abs((1 + np.sum(lrs >= lr_obs)) / (len(lrs) + 1) - INF['cccb_lr_p_boot']) < 1e-12
    assert abs(lrs.max() - INF['cccb_lr_null_max']) < 1e-8, 'CCC-null bootstrap differs from inference_ch6'
    fig_b1_lr(lr_obs, lrs)
    b2 = b_gauss_vs_t(W2, U2)
    S.update(b2_rho_g=b2['fg']['par'][0], b2_ll_g=b2['fg']['loglik'], b2_aic_g=b2['fg']['aic'],
             b2_rho_t=b2['ft']['par'][0], b2_nu_t=b2['ft']['par'][1], b2_ll_t=b2['ft']['loglik'], b2_aic_t=b2['ft']['aic'],
             b2_lam_t=b2['ft']['lamL'], b2_lr=b2['lr'], b2_lr_p_boot=b2['lr_p_boot'], b2_lr_p_chi2half=b2['lr_p_chi2half'],
             b2_gof_g=b2['gg']['p'], b2_gof_t=b2['gt']['p'], b2_gof_stat_g=b2['gg']['stat'], b2_gof_stat_t=b2['gt']['stat'],
             b2_lam_lo=b2['lam_ci'][0], b2_lam_hi=b2['lam_ci'][1], b2_nu_lo=b2['nu_ci'][0], b2_nu_hi=b2['nu_ci'][1],
             b2_empL05=b2['emp'][0][0], b2_empU05=b2['emp'][0][1], b2_empL10=b2['emp'][1][0], b2_empU10=b2['emp'][1][1],
             b2_lr_null_q95=np.percentile(b2['lr_b'], 95), b2_lr_null_max=b2['lr_b'].max())
    nL, nU = fig_b2_scatter(W2, U2)
    fG, fT = fig_b2_tails(U2, b2['fg'], b2['ft'])
    S.update(b2_nL05=nL, b2_nU05=nU, b2_fitG05=fG, b2_fitT05=fT)
    fig_b2_boot(b2['lr'], b2['lr_b'], b2['nu_b'], b2['lam_b'], b2['ft']['par'][1], b2['ft']['lamL'])
    b3 = b_losses_copula()
    fig_losses_copula(b3['U'], b3['res'])
    S.update(b3_tau=b3['tau'], b3_n=b3['n'], b3_start=b3['start'],
             b3_empU05=b3['emp'][0.05][1], b3_empL05=b3['emp'][0.05][0], b3_empU10=b3['emp'][0.10][1], b3_empL10=b3['emp'][0.10][0])
    for fam, r in b3['res'].items():
        S.update({f'b3_{fam}_par': r['fit']['par'][0], f'b3_{fam}_ll': r['fit']['loglik'], f'b3_{fam}_aic': r['fit']['aic'],
                  f'b3_{fam}_lamL': r['fit']['lamL'], f'b3_{fam}_lamU': r['fit']['lamU'], f'b3_{fam}_p': r['gof']['p'],
                  f'b3_{fam}_stat': r['gof']['stat']})
        if fam == 't':
            S['b3_t_nu'] = r['fit']['par'][1]
    f05 = fig_b3_tails(b3['U'], b3['res'])
    S.update({f'b3_fitU05_{k}': v for k, v in f05.items()})
    t08, t20, t20b, t08b = b_forbes_rigobon()
    fig_b4_windows()
    fr_d = b4_fr_draws()
    for (tag, tg), dd in fr_d.items():
        assert abs(np.mean(dd[:, 0] <= 0) - INF[f'frb_{tag}_{tg}_p_boot']) < 1e-12, 'FR bootstrap differs'
    frs = fig_forbes_rigobon_sem(t08, t20, fr_d)
    for lab_, D_, lo_, hi_ in zip(('08_stoxx', '08_bet', '20_stoxx', '20_bet'), frs['D'], frs['Dlo'], frs['Dhi']):
        S.update({f'b4_D_{lab_}': D_, f'b4_Dlo_{lab_}': lo_, f'b4_Dhi_{lab_}': hi_})
    for lab, t in (('08', t08), ('20', t20), ('20s', t20b), ('08s', t08b)):
        S[f'b4_delta_{lab}'] = t['delta'].iloc[0]
        S[f'b4_ncr_{lab}'] = int(t['n_crisis'].iloc[0])
        S[f'b4_ncalm_{lab}'] = int(t['n_calm'].iloc[0])
        for k in t.index:
            for c in ('rho_calm', 'rho_crisis', 'rho_adj', 'p_raw', 'p_adj'):
                S[f'b4_{lab}_{k}_{c}'] = t.loc[k, c]
    b5 = b_btc_bands()
    fig_btc_bands(b5)
    dm, dm_ci = b5_mean_change(b5)
    S.update(b5_a=b5['d']['a'], b5_b=b5['d']['b'], b5_n=b5['n'], b5_start=b5['start'],
             b5_a_lo=np.percentile(b5['ab'][:, 0], 5), b5_a_hi=np.percentile(b5['ab'][:, 0], 95),
             b5_b_lo=np.percentile(b5['ab'][:, 1], 5), b5_b_hi=np.percentile(b5['ab'][:, 1], 95),
             b5_last=b5['rc'].iloc[-1], b5_last_lo=b5['lo'].iloc[-1], b5_last_hi=b5['hi'].iloc[-1],
             b5_width=(b5['hi'] - b5['lo']).mean(), b5_pre=b5['rc'].loc[:'2019-12-31'].mean(),
             b5_post=b5['rc'].loc['2020-01-01':].mean(), b5_share_lo_pos=(b5['lo'].loc['2020-01-01':] > 0).mean(),
             b5_share_lo_pos_pre=(b5['lo'].loc[:'2019-12-31'] > 0).mean(), b5_dm=dm, b5_dm_lo=dm_ci[0], b5_dm_hi=dm_ci[1])
    g6, rho6 = b6_gas_path()
    assert abs(g6['lr'] - INF['b6_lr']) < 1e-6, 'B6 GAS fit differs from inference_ch6'
    fig_b6_gas(g6, rho6)
    c = c_integration()
    fig_integration_c(c)
    fig_c1_change(c)
    S.update({f'c_{k}': v for k, v in c.items() if k not in ('rc', 'W', 'ci', 'diffs')})
    S['c_ci_lo'], S['c_ci_hi'] = c['ci']
    out = {k: fnum(v) for k, v in S.items()}
    with open(os.path.join(TABLE_DIR, 'ch6_seminar_numbers.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f'saved ch6_seminar_numbers.json ({len(out)} numbers)')

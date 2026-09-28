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
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import SHORT, joint_returns, weekly_returns, joint_prices   # noqa: E402
from dep_tools import (garch_all, dcc_fit, dcc_path, fr_adjust, crisis_table, pseudo_obs, kendall_tau,  # noqa: E402
                       spearman_rho, theta_from_tau, tail_dep, simulate, fit_copula, gof_test, empirical_tail_dep,
                       fisher_z_test, FAM_LABEL)
from generate_all_charts import (save_fig, legend_outside_bottom, two_day_returns, MainBlue, IDAred, Forest,  # noqa: E402
                                 Amber, Gray, Purple, CALM08, CRISIS08, CALM20, CRISIS20, SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE_DIR = HERE
S = {}


# =============================================================================
# PARTEA A
# =============================================================================
def a_tail_gauss_t(rho=0.5, nus=(3, 4, 10, 30)):
    """A1: lambda pentru copula t si probabilitatea conditionata P(V<=q | U<=q) la nivel finit."""
    out = {}
    for nu in nus:
        arg = np.sqrt((nu + 1) * (1 - rho) / (1 + rho))
        out[nu] = dict(arg=arg, lam=2 * stats.t.cdf(-arg, nu + 1))
    qs = np.array([0.10, 0.05, 0.01, 0.001])
    mvn = stats.multivariate_normal([0, 0], [[1, rho], [rho, 1]])
    gauss = np.array([mvn.cdf([stats.norm.ppf(q)] * 2) / q for q in qs])
    mvt = stats.multivariate_t([0, 0], [[1, rho], [rho, 1]], df=4)
    t4 = np.array([mvt.cdf([stats.t.ppf(q, 4)] * 2) / q for q in qs])
    return out, qs, gauss, t4


def fig_tail_gauss_t(rho=0.5):
    qs = np.geomspace(0.001, 0.2, 30)
    mvn = stats.multivariate_normal([0, 0], [[1, rho], [rho, 1]])
    g = [mvn.cdf([stats.norm.ppf(q)] * 2) / q for q in qs]
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    ax.plot(qs, g, color=MainBlue, lw=1.6, label='Gaussian copula (rho = 0.5)')
    for nu, c in ((4, IDAred), (10, Amber)):
        mvt = stats.multivariate_t([0, 0], [[1, rho], [rho, 1]], df=nu)
        ax.plot(qs, [mvt.cdf([stats.t.ppf(q, nu)] * 2) / q for q in qs], color=c, lw=1.6, label=f't copula (rho = 0.5, nu = {nu})')
        lam = 2 * stats.t.cdf(-np.sqrt((nu + 1) * (1 - rho) / (1 + rho)), nu + 1)
        ax.axhline(lam, color=c, ls=':', lw=0.9)
    ax.set_xscale('log')
    ax.set_xlabel('q (log scale)')
    ax.set_ylabel('P(V <= q | U <= q)')
    ax.set_ylim(0, 0.8)
    legend_outside_bottom(ax, ncol=3)
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
                nu_ci=np.percentile(nu_b, [5, 95]), emp=[empirical_tail_dep(u, v, q) for q in (0.05, 0.10)])


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


def fig_forbes_rigobon_sem(t08, t20):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    labels, calm, raw, adj = [], [], [], []
    for yr, t in (('2008', t08), ('2020', t20)):
        for k in t.index:
            labels.append(f'{SHORT[k]}\n{yr}')
            calm.append(t.loc[k, 'rho_calm'])
            raw.append(t.loc[k, 'rho_crisis'])
            adj.append(t.loc[k, 'rho_adj'])
    x = np.arange(len(labels))
    ax.bar(x - 0.26, calm, 0.24, color=Forest, label='Calm year before')
    ax.bar(x, raw, 0.24, color=IDAred, label='Crisis, raw')
    ax.bar(x + 0.26, adj, 0.24, color=MainBlue, label='Crisis, Forbes-Rigobon adjusted')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Correlation with the S&P 500 (2-day returns)')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch6_sem_forbes_rigobon')


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
    return dict(d=d, rc=rc, lo=lo, hi=hi, ab=ab, n=len(Z), start=str(Z.index[0].date()))


def fig_btc_bands(o):
    rc, lo, hi = o['rc'], o['lo'], o['hi']
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.fill_between(rc.index, lo, hi, color=Amber, alpha=0.3, lw=0, label='90% residual-bootstrap band (uncertainty in a and b)')
    ax.plot(rc.index, rc, color=IDAred, lw=0.7, label='DCC(1,1) correlation Bitcoin / S&P 500')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_ylabel('Conditional correlation')
    legend_outside_bottom(ax, ncol=2)
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
                beta_pre=beta(pre), beta_post=beta(post), rd_pre=rd_pre, rd_post=rd_post, rc=rc, W=W)


def fig_integration_c(o):
    W, rc = o['W'], o['rc']
    roll = W['bet'].rolling(52).corr(W['stoxx'])
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(rc.index, rc, color=IDAred, lw=0.8, label='DCC(1,1), weekly returns')
    ax.plot(roll.index, roll, color=MainBlue, lw=1.3, label='52-week rolling correlation')
    ax.hlines(o['r_pre'], W.index[0], pd.Timestamp('2019-12-31'), color=Forest, lw=2, label='Sample correlation 2010-2019 / 2020-2026')
    ax.hlines(o['r_post'], pd.Timestamp('2020-01-01'), W.index[-1], color=Forest, lw=2)
    ax.axvline(pd.Timestamp('2020-09-21'), color=Gray, ls='--', lw=0.9, label='FTSE Russell upgrade effective (Sep 2020)')
    ax.set_ylabel('Correlation BET / Euro Stoxx 50')
    legend_outside_bottom(ax, ncol=2)
    save_fig('ch6_sem_integration')


def fnum(x):
    if isinstance(x, (np.floating, float)):
        return float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    return x


if __name__ == '__main__':
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
    b1 = b_dcc_spy_tlt()
    S.update(b1_a=b1['full']['a'], b1_b=b1['full']['b'], b1_se_a=b1['full']['se_a'], b1_se_b=b1['full']['se_b'],
             b1_lr=b1['lr'], b1_n=b1['n'], b1_r0=b1['r0'], b1_r1=b1['r1'], b1_zt=b1['zt'], b1_p2=b1['p2'],
             b1_pre_a=b1['sub']['pre']['a'], b1_pre_b=b1['sub']['pre']['b'], b1_pre_q=b1['sub']['pre']['Qbar'][0, 1],
             b1_post_a=b1['sub']['post']['a'], b1_post_b=b1['sub']['post']['b'], b1_post_q=b1['sub']['post']['Qbar'][0, 1],
             b1_pre_n=b1['sub']['pre']['n'], b1_post_n=b1['sub']['post']['n'],
             b1_hl=np.log(0.5) / np.log(b1['full']['a'] + b1['full']['b']))
    b2 = b_gauss_vs_t(W2, U2)
    S.update(b2_rho_g=b2['fg']['par'][0], b2_ll_g=b2['fg']['loglik'], b2_aic_g=b2['fg']['aic'],
             b2_rho_t=b2['ft']['par'][0], b2_nu_t=b2['ft']['par'][1], b2_ll_t=b2['ft']['loglik'], b2_aic_t=b2['ft']['aic'],
             b2_lam_t=b2['ft']['lamL'], b2_lr=b2['lr'], b2_lr_p_boot=b2['lr_p_boot'], b2_lr_p_chi2half=b2['lr_p_chi2half'],
             b2_gof_g=b2['gg']['p'], b2_gof_t=b2['gt']['p'], b2_gof_stat_g=b2['gg']['stat'], b2_gof_stat_t=b2['gt']['stat'],
             b2_lam_lo=b2['lam_ci'][0], b2_lam_hi=b2['lam_ci'][1], b2_nu_lo=b2['nu_ci'][0], b2_nu_hi=b2['nu_ci'][1],
             b2_empL05=b2['emp'][0][0], b2_empU05=b2['emp'][0][1], b2_empL10=b2['emp'][1][0], b2_empU10=b2['emp'][1][1])
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
    t08, t20, t20b, t08b = b_forbes_rigobon()
    fig_forbes_rigobon_sem(t08, t20)
    for lab, t in (('08', t08), ('20', t20), ('20s', t20b), ('08s', t08b)):
        S[f'b4_delta_{lab}'] = t['delta'].iloc[0]
        S[f'b4_ncr_{lab}'] = int(t['n_crisis'].iloc[0])
        for k in t.index:
            for c in ('rho_calm', 'rho_crisis', 'rho_adj', 'p_raw', 'p_adj'):
                S[f'b4_{lab}_{k}_{c}'] = t.loc[k, c]
    b5 = b_btc_bands()
    fig_btc_bands(b5)
    S.update(b5_a=b5['d']['a'], b5_b=b5['d']['b'], b5_n=b5['n'], b5_start=b5['start'],
             b5_a_lo=np.percentile(b5['ab'][:, 0], 5), b5_a_hi=np.percentile(b5['ab'][:, 0], 95),
             b5_b_lo=np.percentile(b5['ab'][:, 1], 5), b5_b_hi=np.percentile(b5['ab'][:, 1], 95),
             b5_last=b5['rc'].iloc[-1], b5_last_lo=b5['lo'].iloc[-1], b5_last_hi=b5['hi'].iloc[-1],
             b5_width=(b5['hi'] - b5['lo']).mean(), b5_pre=b5['rc'].loc[:'2019-12-31'].mean(),
             b5_post=b5['rc'].loc['2020-01-01':].mean(), b5_share_lo_pos=(b5['lo'].loc['2020-01-01':] > 0).mean(),
             b5_share_lo_pos_pre=(b5['lo'].loc[:'2019-12-31'] > 0).mean())
    c = c_integration()
    fig_integration_c(c)
    S.update({f'c_{k}': v for k, v in c.items() if k not in ('rc', 'W', 'ci')})
    S['c_ci_lo'], S['c_ci_hi'] = c['ci']
    out = {k: fnum(v) for k, v in S.items()}
    with open(os.path.join(TABLE_DIR, 'ch6_seminar_numbers.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f'saved ch6_seminar_numbers.json ({len(out)} numbers)')

"""
inference18.py -- Inferenta pentru masurile de risc sistemic din Capitolul 18 (MFM)
==================================================================================
  * covar_tests         -- bootstrap comun pe blocuri: H0 Delta-CoVaR = 0, H0 b_alpha = b_50%, egalitatea contributiilor
                           (teste pe perechi, corectie Holm), erori standard kernel pentru regresia cuantila
  * euler_check         -- ES al portofoliului = suma ponderata a MES doar cand conditionam pe portofoliul insusi
  * ge_covar            -- CoVaR in definitia Girardi-Ergun (X_i <= -VaR_i), istoric, la 5%
  * srisk_simulation    -- LRMES prin simulare GJR-GARCH + DCC cu inovatii reesantionate (Brownlees & Engle, 2017,
                           Sectiunea 1 si Anexa A: h = 22 zile, C = -10%, k = 8%) si scenariul de 6 luni / -40%
                           (Acharya, Engle & Richardson, 2012, Sectiunea I) comparat cu aproximarea 1 - exp(-18 MES)
  * spill_bootstrap     -- intervale bootstrap (reziduuri pe blocuri) pentru conectivitatea totala si neta
  * enet_connectedness  -- VAR cu elastic net adaptiv (esantion complet) si elastic net pe ferestre de 150 de zile
                           (Demirer, Diebold, Liu & Yilmaz, 2018, ecuatia (9), Sectiunile 4-5)
  * granger_fdr         -- retea de cauzalitate Granger pe perechi: 156 de teste, Holm si Benjamini-Hochberg

Ruleaza dupa generate_all_charts.py; scrie ch18_inference.json si graficele ch18_lrmes_models, ch18_spill_ci,
ch18_spill_enet. Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, optimize
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from sklearn.linear_model import ElasticNetCV
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_all_charts import (R, V, US, EU, RO, ALL, NAMES, REGION_INDEX, REGION_COL, region_of, system_ex,  # noqa
                                 save_fig, legend_outside_bottom, jsonable, MainBlue, IDAred, Forest, Orange, Purple,
                                 Teal, Amber, Gray, HERE)
from systemic import (qreg, covar_static, block_bootstrap_idx, mes, mes_threshold, lrmes, breakeven_leverage,  # noqa
                      var_fit, var_bic, gfevd, spillover_table)

SEED = 42
B = 999
OUT = {}


# =============================================================================
# 1. Tests for Delta-CoVaR (joint bootstrap, blocks of 20 days)
# =============================================================================
def holm(p):
    """Holm correction (adjusted p-values) for a family of tests."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    m = len(p)
    adj = np.maximum.accumulate((m - np.arange(m)) * p[o])
    out = np.empty(m)
    out[o] = np.minimum(adj, 1)
    return out


def bh(p, q=0.05):
    """Benjamini-Hochberg: rejection mask at false discovery rate q."""
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    ok = p[o] <= q * np.arange(1, m + 1) / m
    k = np.max(np.nonzero(ok)[0]) + 1 if ok.any() else 0
    rej = np.zeros(m, bool)
    rej[o[:k]] = True
    return rej


def covar_tests(alpha=0.01, B=B, block=20, seed=SEED):
    """The same bootstrap draws for all banks -> joint distribution of Delta-CoVaR and of the slopes."""
    banks = US + EU
    sysr = {k: system_ex(k, US if k in US else EU).values for k in banks}
    x = {k: R[k].values for k in banks}
    n = len(R)
    point = {k: covar_static(sysr[k], x[k], alpha) for k in banks}
    b50 = {k: qreg(sysr[k], x[k], 0.5)[1] for k in banks}
    rng = np.random.default_rng(seed)
    D = np.zeros((B, len(banks)))
    DB = np.zeros((B, len(banks)))
    for r in range(B):
        idx = block_bootstrap_idx(n, block, rng)
        for j, k in enumerate(banks):
            c = covar_static(sysr[k][idx], x[k][idx], alpha)
            D[r, j] = c['dcovar']
            DB[r, j] = c['b'] - qreg(sysr[k][idx], x[k][idx], 0.5)[1]
    res = {'alpha': alpha, 'n': n, 'n_tail': n * alpha, 'banks': {}}
    for j, k in enumerate(banks):
        fit = QuantReg(sysr[k], sm.add_constant(x[k])).fit(q=alpha, max_iter=5000)     # kernel standard error (sandwich)
        dpt = point[k]['b'] - b50[k]
        se_db = DB[:, j].std(ddof=1)
        res['banks'][k] = {'dcovar': point[k]['dcovar'], 'b': point[k]['b'], 'b50': b50[k], 'se_b_kernel': fit.bse[1],
                           'se_b_boot': None, 'lo': np.percentile(D[:, j], 2.5), 'hi': np.percentile(D[:, j], 97.5),
                           'se_dcovar_boot': D[:, j].std(ddof=1), 'db': dpt, 'se_db': se_db,
                           'p_db': 2 * stats.norm.sf(abs(dpt) / se_db)}
    # equal contributions by pair, within each region: t = difference / bootstrap standard deviation of the difference
    pairs = []
    for mem in (US, EU):
        for a in range(len(mem)):
            for b_ in range(a + 1, len(mem)):
                i, j = banks.index(mem[a]), banks.index(mem[b_])
                d = point[mem[a]]['dcovar'] - point[mem[b_]]['dcovar']
                se = (D[:, i] - D[:, j]).std(ddof=1)
                pairs.append((mem[a], mem[b_], d, se, 2 * stats.norm.sf(abs(d) / se),
                              # overlap of the marginal intervals
                              not (res['banks'][mem[a]]['hi'] < res['banks'][mem[b_]]['lo'] or
                                   res['banks'][mem[b_]]['hi'] < res['banks'][mem[a]]['lo'])))
    p = np.array([q[4] for q in pairs])
    ph = holm(p)
    res['pairs'] = [{'a': q[0], 'b': q[1], 'd': q[2], 'se': q[3], 'p': q[4], 'p_holm': ph[i], 'overlap': q[5]}
                    for i, q in enumerate(pairs)]
    res['n_pairs'] = len(pairs)
    res['n_sig_raw'] = int((p < 0.05).sum())
    res['n_sig_holm'] = int((ph < 0.05).sum())
    res['n_sig_overlap'] = int(sum(1 for i, q in enumerate(pairs) if q[5] and p[i] < 0.05))
    res['n_db_sig'] = int(sum(v['p_db'] < 0.05 for v in res['banks'].values()))
    res['n_db_sig_holm'] = int((holm([v['p_db'] for v in res['banks'].values()]) < 0.05).sum())
    # joint Wald test: all Delta-CoVaR equal within a region (bootstrap covariance of the contrasts)
    for reg, mem in (('US', US), ('EU', EU)):
        ids = [banks.index(k) for k in mem]
        C = np.zeros((len(ids) - 1, len(banks)))
        for r_, i in enumerate(ids[1:]):
            C[r_, ids[0]], C[r_, i] = 1, -1
        dv = C @ np.array([point[k]['dcovar'] for k in banks])
        S = np.cov((D @ C.T).T)
        w = float(dv @ np.linalg.solve(S, dv))
        res[f'wald_{reg}'] = {'stat': w, 'df': len(ids) - 1, 'p': stats.chi2.sf(w, len(ids) - 1)}
    return res


# =============================================================================
# 2. Euler: ES of the portfolio = weighted sum of the MES (conditioning on the portfolio)
# =============================================================================
def euler_check(alpha=0.05):
    X = R[US]
    port = X.mean(axis=1)
    q = np.quantile(port, alpha)
    es_p = -port[port <= q].mean()
    mes_p = {k: -X[k][port <= q].mean() for k in US}
    m = R['SPX']
    mes_m = {k: mes(X[k].values, m.values, alpha) for k in US}
    return {'es_port': es_p, 'sum_mes_port': np.mean(list(mes_p.values())), 'sum_mes_spx': np.mean(list(mes_m.values())),
            'mes_port': mes_p, 'mes_spx': mes_m, 'n_tail': int((port <= q).sum())}


# =============================================================================
# 3. Girardi-Ergun CoVaR: conditioning on X_i <= -VaR_i (historical)
# =============================================================================
def ge_covar(alpha=0.05):
    out = {}
    for k in US + EU:
        xs = system_ex(k, US if k in US else EU).values
        xi = R[k].values
        qa, qm = np.quantile(xi, alpha), np.quantile(xi, 0.5)
        dist = xs[xi <= qa]
        med = xs[np.abs(xi - xi.mean()) <= xi.std()]                       # benchmark state: a one-standard-deviation event
        out[k] = {'ge_covar': -np.quantile(dist, alpha), 'ge_covar_med': -np.quantile(med, alpha),
                  'ab_covar': covar_static(xs, xi, alpha)['covar'], 'n_cond': int(len(dist))}
        out[k]['ge_dcovar'] = out[k]['ge_covar'] - out[k]['ge_covar_med']
    return out


def kupiec(x, n, p):
    """Kupiec test (unconditional coverage): likelihood-ratio statistic LR ~ chi2(1) under H0: hit rate = p."""
    ph = x / n
    ll0 = x * np.log(p) + (n - x) * np.log(1 - p)
    ll1 = (x * np.log(ph) if x > 0 else 0) + ((n - x) * np.log(1 - ph) if x < n else 0)
    lr = -2 * (ll0 - ll1)
    return lr, stats.chi2.sf(lr, 1)


def backtest_ge(alpha=0.05, start=1000):
    """Out-of-sample backtest of the Girardi-Ergun CoVaR (historical, expanding window):
    joint hit 1{X_sys <= -CoVaR_t, X_i <= -VaR_i,t}, with probability alpha^2 under H0."""
    out = {}
    for k in US + EU:
        xs = system_ex(k, US if k in US else EU).values
        xi = R[k].values
        hits, vh = [], []
        for t in range(start, len(xi)):
            a, s = xi[:t], xs[:t]
            q = np.quantile(a, alpha)
            cov = -np.quantile(s[a <= q], alpha)
            vh.append(xi[t] <= q)
            hits.append((xi[t] <= q) and (xs[t] <= -cov))
        n, x = len(hits), int(np.sum(hits))
        lr, p = kupiec(x, n, alpha ** 2)
        lrv, pv = kupiec(int(np.sum(vh)), n, alpha)
        out[k] = {'n': n, 'hits': x, 'expected': n * alpha ** 2, 'lr': lr, 'p': p,
                  'var_hits': int(np.sum(vh)), 'var_p': pv}
    return out


# =============================================================================
# 4. SRISK following Brownlees & Engle (2017): GJR-GARCH + DCC, simulation with resampled innovations
# =============================================================================
def gjr_fit(r):
    """GJR-GARCH(1,1) with zero mean (log returns in %), quasi-maximum likelihood (QML)."""
    m = arch_model(r, mean='Zero', vol='GARCH', p=1, o=1, q=1, dist='normal', rescale=False).fit(disp='off')
    om, a, g, b = m.params[['omega', 'alpha[1]', 'gamma[1]', 'beta[1]']]
    s2 = m.conditional_volatility ** 2
    s2_next = om + (a + g * (r[-1] < 0)) * r[-1] ** 2 + b * s2[-1]
    return {'omega': om, 'alpha': a, 'gamma': g, 'beta': b, 'sig': np.sqrt(s2), 's2_next': s2_next}


def dcc_fit(e):
    """Bivariate DCC(1,1), second QML step (Engle, 2002); e = standardised residuals T x 2."""
    S = np.corrcoef(e.T)
    T = len(e)

    def filt(a, b):
        Q = S.copy()
        rho = np.empty(T)
        for t in range(T):
            rho[t] = Q[0, 1] / np.sqrt(Q[0, 0] * Q[1, 1])
            Q = (1 - a - b) * S + a * np.outer(e[t], e[t]) + b * Q
        return rho, Q

    def nll(th):
        a, b = th
        if a <= 0 or b <= 0 or a + b >= 0.999:
            return 1e10
        rho, _ = filt(a, b)
        z1, z2 = e[:, 0], e[:, 1]
        return 0.5 * np.sum(np.log(1 - rho ** 2) + (z1 ** 2 + z2 ** 2 - 2 * rho * z1 * z2) / (1 - rho ** 2)
                            - (z1 ** 2 + z2 ** 2))

    best = min((optimize.minimize(nll, x0, method='Nelder-Mead', options={'xatol': 1e-5, 'fatol': 1e-4})
                for x0 in [(0.02, 0.95), (0.05, 0.90)]), key=lambda o: o.fun)
    a, b = best.x
    rho, Q = filt(a, b)
    return {'a': a, 'b': b, 'S': S, 'rho': rho, 'Q_next': Q}


def simulate_market(gm, eps_m, idx):
    """Market paths (GJR) from the resampled innovations eps_m[idx], idx: S x h."""
    Sn, h = idx.shape
    s2 = np.full(Sn, gm['s2_next'])
    cum = np.zeros(Sn)
    for t in range(h):
        r = np.sqrt(s2) * eps_m[idx[:, t]]
        cum += r
        s2 = gm['omega'] + (gm['alpha'] + gm['gamma'] * (r < 0)) * r ** 2 + gm['beta'] * s2
    return cum


def simulate_firm(gf, gm, dcc, eps_m, xi, idx):
    """Bank paths conditional on the same drawn dates (Appendix A of Brownlees & Engle, 2017)."""
    Sn, h = idx.shape
    s2i = np.full(Sn, gf['s2_next'])
    q11 = np.full(Sn, dcc['Q_next'][0, 0])
    q22 = np.full(Sn, dcc['Q_next'][1, 1])
    q12 = np.full(Sn, dcc['Q_next'][0, 1])
    cum = np.zeros(Sn)
    a, b, S = dcc['a'], dcc['b'], dcc['S']
    for t in range(h):
        rho = q12 / np.sqrt(q11 * q22)
        em = eps_m[idx[:, t]]
        ei = rho * em + np.sqrt(1 - rho ** 2) * xi[idx[:, t]]
        r = np.sqrt(s2i) * ei
        cum += r
        s2i = gf['omega'] + (gf['alpha'] + gf['gamma'] * (r < 0)) * r ** 2 + gf['beta'] * s2i
        q11 = (1 - a - b) * S[0, 0] + a * ei ** 2 + b * q11
        q22 = (1 - a - b) * S[1, 1] + a * em ** 2 + b * q22
        q12 = (1 - a - b) * S[0, 1] + a * ei * em + b * q12
    return cum


def lrmes_sim(end, h, C, Sn, seed=SEED, gaussian=False):
    """LRMES (fraction) for the 13 banks at date `end`, horizon h days, threshold C (arithmetic market return)."""
    rng = np.random.default_rng(seed)
    Rs = R.loc[:end]
    out, info = {}, {}
    for reg, mem in (('US', US), ('EU', EU), ('RO', RO)):
        rm = Rs[REGION_INDEX[reg]].values
        gm = gjr_fit(rm)
        eps_m = rm / gm['sig']
        T = len(rm)
        # 1) market paths; only the crisis scenarios are kept (algorithm of Appendix A of Brownlees & Engle, 2017)
        keep_idx, n_all = [], 0
        for _ in range(Sn // 20000):
            idx = rng.integers(0, T, size=(20000, h))
            n_all += 20000
            if gaussian:
                eps_draw = rng.standard_normal((20000, h))
                # Gaussian paths: indices into their own matrix of innovations
                cm = _sim_gauss_market(gm, eps_draw)
                keep_idx.append(eps_draw[np.exp(cm / 100) - 1 < C])
            else:
                cm = simulate_market(gm, eps_m, idx)
                keep_idx.append(idx[np.exp(cm / 100) - 1 < C])
        kept = np.concatenate(keep_idx)
        info[reg] = {'p_crisis': len(kept) / n_all, 'n_crisis': len(kept), 'market': gm}
        for k in mem:
            ri = Rs[k].values
            gf = gjr_fit(ri)
            e = np.column_stack([ri / gf['sig'], eps_m])
            dcc = dcc_fit(e)
            xi = (e[:, 0] - dcc['rho'] * e[:, 1]) / np.sqrt(1 - dcc['rho'] ** 2)
            if gaussian:
                ci = _sim_gauss_firm(gf, gm, dcc, kept, rng)
            else:
                ci = simulate_firm(gf, gm, dcc, eps_m, xi, kept)
            Ri = np.exp(ci / 100) - 1
            out[k] = {'lrmes': -Ri.mean(), 'mc_se': Ri.std(ddof=1) / np.sqrt(len(Ri)),
                      'q05': -np.quantile(Ri, 0.95), 'q95': -np.quantile(Ri, 0.05),
                      'rho_last': dcc['rho'][-1], 'dcc_a': dcc['a'], 'dcc_b': dcc['b'],
                      'gjr': [gf['alpha'], gf['gamma'], gf['beta']]}
    return out, info


def _sim_gauss_market(gm, eps):
    Sn, h = eps.shape
    s2 = np.full(Sn, gm['s2_next'])
    cum = np.zeros(Sn)
    for t in range(h):
        r = np.sqrt(s2) * eps[:, t]
        cum += r
        s2 = gm['omega'] + (gm['alpha'] + gm['gamma'] * (r < 0)) * r ** 2 + gm['beta'] * s2
    return cum


def _sim_gauss_firm(gf, gm, dcc, eps_m_paths, rng):
    """Variant with Normal innovations (the same crisis paths of the market, xi ~ N(0,1))."""
    Sn, h = eps_m_paths.shape
    xi = rng.standard_normal((Sn, h))
    s2i = np.full(Sn, gf['s2_next'])
    q11, q22, q12 = (np.full(Sn, dcc['Q_next'][i, j]) for i, j in [(0, 0), (1, 1), (0, 1)])
    a, b, S = dcc['a'], dcc['b'], dcc['S']
    cum = np.zeros(Sn)
    for t in range(h):
        rho = q12 / np.sqrt(q11 * q22)
        em = eps_m_paths[:, t]
        ei = rho * em + np.sqrt(1 - rho ** 2) * xi[:, t]
        r = np.sqrt(s2i) * ei
        cum += r
        s2i = gf['omega'] + (gf['alpha'] + gf['gamma'] * (r < 0)) * r ** 2 + gf['beta'] * s2i
        q11 = (1 - a - b) * S[0, 0] + a * ei ** 2 + b * q11
        q22 = (1 - a - b) * S[1, 1] + a * em ** 2 + b * q22
        q12 = (1 - a - b) * S[0, 1] + a * ei * em + b * q12
    return cum


def srisk_simulation():
    end = R.index[-1]
    be, be_info = lrmes_sim(end, 22, -0.10, 200000, SEED)                 # Brownlees & Engle (2017): h = 22, C = -10%
    v6, v6_info = lrmes_sim(end, 126, -0.40, 400000, SEED + 1)            # the 6-month / -40% scenario
    g6, _ = lrmes_sim(end, 126, -0.40, 400000, SEED + 2, gaussian=True)   # the same, with Normal innovations
    cv, cv_info = lrmes_sim(pd.Timestamp('2020-03-31'), 22, -0.10, 200000, SEED + 3)   # conditional on 31.03.2020
    short = {k: lrmes(mes_threshold(R[k].values, R[REGION_INDEX[region_of(k)]].values, -2.0)) for k in ALL}
    res = {'end': end, 'be': be, 'v6': v6, 'g6': g6, 'covid': cv, 'short': short,
           'p_crisis_be': {r: be_info[r]['p_crisis'] for r in be_info},
           'p_crisis_v6': {r: v6_info[r]['p_crisis'] for r in v6_info},
           'n_crisis_v6': {r: v6_info[r]['n_crisis'] for r in v6_info},
           'p_crisis_covid': {r: cv_info[r]['p_crisis'] for r in cv_info}}
    s = pd.DataFrame({'short': short, 'v6': {k: v['lrmes'] for k, v in v6.items()},
                      'g6': {k: v['lrmes'] for k, v in g6.items()}, 'be': {k: v['lrmes'] for k, v in be.items()}})
    res['spearman_short_v6'] = stats.spearmanr(s['short'], s['v6']).correlation
    res['spearman_v6_g6'] = stats.spearmanr(s['v6'], s['g6']).correlation
    res['ratio_range'] = [float((s['v6'] / s['short']).min()), float((s['v6'] / s['short']).max())]
    res['Lstar_v6'] = {k: breakeven_leverage(v['lrmes']) for k, v in v6.items()}
    res['Lstar_be'] = {k: breakeven_leverage(v['lrmes']) for k, v in be.items()}
    return res, s


def fig_lrmes_models(s):
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    xs = np.arange(len(ALL))
    w = 0.27
    ax.bar(xs - w, 100 * s.loc[ALL, 'short'], w, color=MainBlue, label='Shortcut 1 - exp(-18 MES), MES at the -2% threshold')
    ax.bar(xs, 100 * s.loc[ALL, 'v6'], w, color=IDAred, label='GJR-GARCH + DCC, resampled innovations')
    ax.bar(xs + w, 100 * s.loc[ALL, 'g6'], w, color=Orange, label='GJR-GARCH + DCC, Normal innovations')
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in ALL], rotation=35, ha='right', fontsize=7.5)
    ax.set_ylabel('LRMES: 6-month loss given\nmarket fall of 40% (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.42)
    save_fig('ch18_lrmes_models')


# =============================================================================
# 5. Uncertainty of connectedness: bootstrap of the VAR residuals (blocks of 20 days)
# =============================================================================
def var_simulate(A, c, E, Y0, idx):
    p = len(A)
    T = len(idx)
    k = A[0].shape[0]
    Y = np.zeros((T + p, k))
    Y[:p] = Y0
    for t in range(p, T + p):
        Y[t] = c + sum(A[l] @ Y[t - l - 1] for l in range(p)) + E[idx[t - p]]
    return Y


def var_fit_c(Y, p):
    Y = np.asarray(Y, float)
    T, k = Y.shape
    X = np.hstack([np.ones((T - p, 1))] + [Y[p - l - 1:T - l - 1] for l in range(p)])
    Bc = np.linalg.lstsq(X, Y[p:], rcond=None)[0]
    E = Y[p:] - X @ Bc
    return [Bc[1 + l * k:1 + (l + 1) * k].T for l in range(p)], Bc[0], E


def spill_bootstrap(Y, p, H=10, B=B, block=20, seed=SEED):
    """Percentile interval for total and net connectedness (residual block bootstrap, VAR re-estimated)."""
    Y = np.asarray(Y, float)
    A, c, E = var_fit_c(Y, p)
    rng = np.random.default_rng(seed)
    tot, net = [], []
    for _ in range(B):
        idx = block_bootstrap_idx(len(E), block, rng)
        Yb = var_simulate(A, c, E, Y[:p], idx)
        Ab, Sb = var_fit(Yb, p)
        st = spillover_table(gfevd(Ab, Sb, H), list(range(Y.shape[1])))
        tot.append(st['total'])
        net.append(st['net'].values)
    return np.array(tot), np.array(net)


def fig_spill_ci(point_net, net_draws):
    lo, hi = np.percentile(net_draws, [2.5, 97.5], axis=0)
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    xs = np.arange(len(ALL))
    ax.bar(xs, point_net, color=[REGION_COL[region_of(k)] for k in ALL], width=0.6)
    ax.errorbar(xs, point_net, yerr=[point_net - lo, hi - point_net], fmt='none', ecolor='black', capsize=2, lw=0.8)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in ALL], rotation=35, ha='right', fontsize=7.5)
    ax.set_ylabel('Net spillover (to - from, %)')
    h = [plt.Rectangle((0, 0), 1, 1, color=REGION_COL[r]) for r in ['US', 'EU', 'RO']] + \
        [plt.Line2D([], [], color='black', marker='|', ls='', ms=8)]
    ax.legend(h, ['US banks', 'European banks', 'Romanian banks', '95% residual block-bootstrap interval'],
              loc='upper center', bbox_to_anchor=(0.5, -0.42), ncol=2, frameon=False)
    save_fig('ch18_spill_ci')
    return lo, hi


# =============================================================================
# 6. Regularised VAR (Demirer et al., 2018): adaptive elastic net (full sample), elastic net on 150 days
# =============================================================================
def aenet_eq(X, y, w, lambdas, folds=10, seed=SEED):
    """min sum (y - Xb)^2 + lam sum w_i (|b_i|/2 + b_i^2/2)  (equation (9)); lambda by 10-fold cross-validation."""
    def fit(X, y, lam):
        Xc, yc = X - X.mean(0), y - y.mean()
        z = (Xc ** 2).sum(0)
        b = np.zeros(X.shape[1])
        r = yc.copy()
        for _ in range(200):
            b_old = b.copy()
            for j in range(len(b)):
                r += Xc[:, j] * b[j]
                rho = Xc[:, j] @ r
                b[j] = np.sign(rho) * max(abs(rho) - lam * w[j] / 4, 0) / (z[j] + lam * w[j] / 2)
                r -= Xc[:, j] * b[j]
            if np.max(np.abs(b - b_old)) < 1e-7:
                break
        return y.mean() - X.mean(0) @ b, b
    rng = np.random.default_rng(seed)
    fid = rng.permutation(len(y)) % folds
    cv = []
    for lam in lambdas:
        err = 0
        for f in range(folds):
            tr, te = fid != f, fid == f
            c0, b = fit(X[tr], y[tr], lam)
            err += ((y[te] - c0 - X[te] @ b) ** 2).sum()
        cv.append(err)
    lam = lambdas[int(np.argmin(cv))]
    return fit(X, y, lam), lam


def var_aenet(Y, p, lambdas=None):
    """VAR(p) with adaptive elastic net, equation by equation; weights w = 1/|b_OLS|."""
    Y = np.asarray(Y, float)
    T, k = Y.shape
    X = np.hstack([Y[p - l - 1:T - l - 1] for l in range(p)])
    Yt = Y[p:]
    lambdas = np.logspace(0, 5, 26) if lambdas is None else lambdas
    Bm = np.zeros((k * p, k))
    c = np.zeros(k)
    nz, lam_sel = 0, []
    for i in range(k):
        bols = np.linalg.lstsq(np.column_stack([np.ones(len(X)), X]), Yt[:, i], rcond=None)[0][1:]
        (c[i], Bm[:, i]), lam = aenet_eq(X, Yt[:, i], 1 / np.abs(bols), lambdas)
        nz += int((np.abs(Bm[:, i]) > 1e-10).sum())
        lam_sel.append(lam)
    E = Yt - c - X @ Bm
    S = E.T @ E / (len(Yt) - 1)
    A = [Bm[l * k:(l + 1) * k].T for l in range(p)]
    return A, S, nz / (k * k * p)


def var_enet_window(Y, p):
    """Elastic net (w_i = 1) for the rolling windows; the L1:L2 = 1:1 penalty of equation (9) <=> l1_ratio = 1/3."""
    T, k = Y.shape
    X = np.hstack([Y[p - l - 1:T - l - 1] for l in range(p)])
    Yt = Y[p:]
    Bm = np.zeros((k * p, k))
    c = np.zeros(k)
    for i in range(k):
        m = ElasticNetCV(l1_ratio=1 / 3, cv=10, n_alphas=30, max_iter=5000).fit(X, Yt[:, i])
        Bm[:, i], c[i] = m.coef_, m.intercept_
    E = Yt - c - X @ Bm
    S = E.T @ E / (len(Yt) - 1)
    return [Bm[l * k:(l + 1) * k].T for l in range(p)], S


def rolling_compare(Y, step=10, H=10):
    """Total connectedness: OLS VAR(2) on 250 days (baseline index) against elastic net and OLS on 150 days."""
    Y = pd.DataFrame(Y)
    rows = {}
    for end in range(250, len(Y) + 1, step):
        d = Y.index[end - 1]
        w250 = Y.iloc[end - 250:end].values
        w150 = Y.iloc[end - 150:end].values
        A, S = var_fit(w250, 2)
        c250 = spillover_table(gfevd(A, S, H), list(Y.columns))['total']
        A, S = var_fit(w150, 1)
        c150 = spillover_table(gfevd(A, S, H), list(Y.columns))['total']
        A, S = var_enet_window(w150, 1)
        ce = spillover_table(gfevd(A, S, H), list(Y.columns))['total']
        A1, S1 = var_fit(w250, 1)
        c250p1 = spillover_table(gfevd(A1, S1, H), list(Y.columns))['total']
        rows[d] = {'ols250_p2': c250, 'ols250_p1': c250p1, 'ols150': c150, 'enet150': ce,
                   'bic': var_bic(w250, 3)}
    return pd.DataFrame(rows).T


def fig_spill_enet(rc):
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(rc.index, rc['ols250_p2'], color=Purple, lw=1.0, label='OLS VAR(2), 250-day windows (baseline index)')
    ax.plot(rc.index, rc['ols150'], color=Orange, lw=0.8, label='OLS VAR(1), 150-day windows')
    ax.plot(rc.index, rc['enet150'], color=Forest, lw=1.0, label='Elastic-net VAR(1), 150-day windows, 10-fold CV')
    ax.set_ylabel('Total connectedness (%)')
    ax.set_xlim(rc.index[0], rc.index[-1])
    legend_outside_bottom(ax, ncol=1, y=-0.15)
    save_fig('ch18_spill_enet')


# =============================================================================
# 7. Granger-causality networks: 156 pairwise tests, multiple-testing control
# =============================================================================
def granger_pairs(Y, p=1, extra=0):
    """Robust (HC0) Wald test for j -> i: regression of y_i on p (+extra) lags of y_i and y_j;
    extra = 1 gives the lag-augmented test (Toda-Yamamoto), valid also for highly persistent series."""
    Y = pd.DataFrame(Y)
    L = p + extra
    out = []
    for i in Y.columns:
        for j in Y.columns:
            if i == j:
                continue
            d = pd.concat({f'{v}{l}': Y[v].shift(l) for v in (i, j) for l in range(1, L + 1)}, axis=1)
            d['y'] = Y[i]
            d = d.dropna()
            X = sm.add_constant(d.drop(columns='y'))
            f = sm.OLS(d['y'], X).fit(cov_type='HC0')
            names = [f'{j}{l}' for l in range(1, p + 1)]
            w = f.wald_test(' , '.join(f'{nm} = 0' for nm in names), scalar=True)
            out.append((j, i, float(w.pvalue)))
    return out


def granger_fdr():
    res = {}
    for lab, Y, p, ex in [('ret', R[ALL], 1, 0), ('vol', V, 1, 1)]:
        g = granger_pairs(Y, p, ex)
        pv = np.array([x[2] for x in g])
        res[lab] = {'m': len(pv), 'raw': int((pv < 0.05).sum()), 'bonf': int((pv < 0.05 / len(pv)).sum()),
                    'holm': int((holm(pv) < 0.05).sum()), 'bh': int(bh(pv, 0.05).sum()),
                    'expected_false_raw': 0.05 * len(pv)}
    return res


# =============================================================================
# RUN
# =============================================================================
def run_stage(stage):
    """The stages are independent (they can run in parallel); each writes ch18_inf_<stage>.json."""
    out = {}
    if stage == 'covar1':
        out['covar_tests'] = covar_tests(0.01)
    elif stage == 'covar5':
        out['covar_tests5'] = covar_tests(0.05)
    elif stage == 'misc':
        out['euler'] = euler_check()
        out['ge'] = ge_covar()
        out['backtest_ge'] = backtest_ge(0.05)
        out['granger'] = granger_fdr()
    elif stage == 'srisk':
        sr, s = srisk_simulation()
        fig_lrmes_models(s)
        out['srisk'] = sr
    elif stage == 'spill':
        p = var_bic(V.values, 5)
        tot, net = spill_bootstrap(V.values, p)
        st = spillover_table(gfevd(*var_fit(V.values, p), 10), ALL)
        lo, hi = fig_spill_ci(st['net'].values, net)
        out['spill_boot'] = {'p': p, 'total': st['total'], 'lo': np.percentile(tot, 2.5), 'hi': np.percentile(tot, 97.5),
                             'net_lo': dict(zip(ALL, lo)), 'net_hi': dict(zip(ALL, hi)),
                             'n_sig': int(((lo > 0) | (hi < 0)).sum()),
                             'sig': [k for k, a, b in zip(ALL, lo, hi) if a > 0 or b < 0]}
    elif stage == 'window':
        roll = pd.read_csv(os.path.join(HERE, 'ch18_spill_rolling.csv'), index_col=0, parse_dates=True).iloc[:, 0]
        dmax = roll.idxmax()
        end = V.index.get_loc(dmax) + 1
        tw, _ = spill_bootstrap(V.values[end - 250:end], 2, B=B, seed=SEED + 5)
        wA, wS = var_fit(V.values[end - 250:end], 2)
        out['spill_boot_window'] = {'date': dmax, 'total': spillover_table(gfevd(wA, wS, 10), ALL)['total'],
                                    'lo': np.percentile(tw, 2.5), 'hi': np.percentile(tw, 97.5), 'mean_boot': tw.mean()}
    elif stage == 'enet':
        p = var_bic(V.values, 5)
        A, S, share = var_aenet(V.values, p)
        out['aenet'] = {'total': spillover_table(gfevd(A, S, 10), ALL)['total'], 'share_nonzero': share}
        rc = rolling_compare(V, step=10)
        rc.to_csv(os.path.join(HERE, 'ch18_spill_enet.csv'))
        fig_spill_enet(rc)
        r = {c: {'mean': rc[c].mean(), 'min': rc[c].min(), 'max': rc[c].max()}
             for c in ['ols250_p2', 'ols250_p1', 'ols150', 'enet150']}
        r['corr_p1_p2'] = rc['ols250_p1'].corr(rc['ols250_p2'])
        r['corr_enet_ols250'] = rc['enet150'].corr(rc['ols250_p2'])
        r['gap_ols150_enet'] = (rc['ols150'] - rc['enet150']).mean()
        r['bic_share'] = {str(int(k)): v for k, v in rc['bic'].value_counts(normalize=True).items()}
        r['n'] = len(rc)
        out['roll_cmp'] = r
    with open(os.path.join(HERE, f'ch18_inf_{stage}.json'), 'w') as f:
        json.dump(jsonable(out), f, indent=1, default=str)
    print('done', stage)


STAGES = ['covar1', 'covar5', 'misc', 'srisk', 'spill', 'window', 'enet']


if __name__ == '__main__':
    # python3 inference18.py <stage>   -> one stage;   python3 inference18.py merge -> ch18_inference.json
    arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if arg == 'merge':
        for st in STAGES:
            with open(os.path.join(HERE, f'ch18_inf_{st}.json')) as f:
                OUT.update(json.load(f))
        with open(os.path.join(HERE, 'ch18_inference.json'), 'w') as f:
            json.dump(OUT, f, indent=1)
        print('saved ch18_inference.json')
    else:
        for st in (STAGES if arg == 'all' else [arg]):
            run_stage(st)

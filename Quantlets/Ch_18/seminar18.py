"""
seminar18.py -- Calculele Seminarului 18 (MFM): risc sistemic si retele
=======================================================================
Partea A: CoVaR si MES sub distributia Normala bivariata, SRISK, tabelul Diebold-Yilmaz, test de stres invers.
Partea B: Delta-CoVaR cu bootstrap pe blocuri, MES si LRMES, VaR vs Delta-CoVaR, sensibilitatea indicelui
          Diebold-Yilmaz, FRM intr-o fereastra, scenarii de stres pentru un portofoliu bancar BVB.
Partea C: expunerea bancilor romanesti la stresul bancar din zona euro.
Cifrele sunt salvate in sem18_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_all_charts import (plt, R, V, ALL, US, EU, RO, NAMES, MainBlue, IDAred, Forest, Amber, Orange,  # noqa: E402
                                 Purple, Teal, Gray, save_fig, legend_outside_bottom, jsonable, system_ex, mark_events,
                                 frm_design, frm_window, weekly_returns, SEED)
from systemic import (covar_static, covar_boot, block_bootstrap_idx, mes, mes_threshold, lrmes, breakeven_leverage,  # noqa: E402
                      srisk_ratio, var_fit, gfevd, spillover_table, ma_coefs)
from inference18 import spill_bootstrap  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEM = {}


# =============================================================================
# PARTEA A
# =============================================================================
def a1_covar_normal(s_sys=1.5, s_i=2.0, rho=0.6, alpha=0.01):
    """CoVaR sub distributia Normala bivariata cu medii zero."""
    z = stats.norm.ppf(alpha)
    return {'z': z, 'var_i': -s_i * z, 'var_sys': -s_sys * z, 'cond_sd': s_sys * np.sqrt(1 - rho ** 2),
            'covar': -s_sys * z * (rho + np.sqrt(1 - rho ** 2)), 'covar_med': -s_sys * np.sqrt(1 - rho ** 2) * z,
            'dcovar': -rho * s_sys * z}


def a2_covar_normal():
    """Doua banci: B are VaR dublu, dar corelatie mai mica cu sistemul."""
    return {'A': a1_covar_normal(rho=0.6, s_i=2.0), 'B': a1_covar_normal(rho=0.3, s_i=4.0)}


def a2_ge_covar(s_sys=1.5, rho=0.6, alpha=0.01):
    """CoVaR Girardi-Ergun sub distributia Normala: P(X_sys <= -c, X_i <= q_alpha(X_i)) = alpha^2."""
    from scipy.optimize import brentq
    z = stats.norm.ppf(alpha)
    mvn = stats.multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])
    f = lambda c: mvn.cdf([-c / s_sys, z]) - alpha ** 2
    c = brentq(f, 0.01, 20)
    ab = a1_covar_normal(s_sys=s_sys, rho=rho, alpha=alpha)
    return {'ge_covar': c, 'ab_covar': ab['covar'], 'ab_dcovar': ab['dcovar'], 'z': z}


def a3_euler(w=(0.5, 0.5), s=(2.0, 3.0), rho=0.5, alpha=0.05):
    """Descompunerea Euler a ES sub distributia Normala: ES_p = sum w_i MES_i, cu MES conditionat pe portofoliu."""
    w, s = np.asarray(w), np.asarray(s)
    C = np.array([[s[0] ** 2, rho * s[0] * s[1]], [rho * s[0] * s[1], s[1] ** 2]])
    sp = np.sqrt(w @ C @ w)
    k = stats.norm.pdf(stats.norm.ppf(alpha)) / alpha
    beta = C @ w / sp ** 2
    mes_i = beta * sp * k
    return {'sp': sp, 'k': k, 'es_p': sp * k, 'beta': beta, 'mes': mes_i, 'sum': w @ mes_i, 'cov': C @ w}


def a3_mes_srisk(beta=1.3, s_m=1.0, alpha=0.05, W=100.0, D=1100.0, k=0.08):
    """MES, LRMES si SRISK pentru o banca ilustrativa, cu randamente Normale bivariate."""
    z = stats.norm.ppf(alpha)
    es_m = s_m * stats.norm.pdf(z) / alpha
    tail2 = s_m * stats.norm.pdf(2 / s_m) / stats.norm.cdf(-2 / s_m)     # E[-R_m | R_m < -2]
    mes2 = beta * tail2
    lr = lrmes(mes2)
    return {'z': z, 'es_m': es_m, 'mes': beta * es_m, 'tail2': tail2, 'mes2': mes2, 'lrmes': lr,
            'kD': k * D, 'eq': (1 - k) * (1 - lr) * W, 'srisk': k * D - (1 - k) * (1 - lr) * W,
            'L': (D + W) / W, 'Lstar': breakeven_leverage(lr, k)}


def a4_lrmes_shortcut(beta=1.3, d=0.40):
    """De unde vine 18: LRMES = 1 - (1 - d)^beta = 1 - exp(-kappa MES^{2%}), kappa = -ln(1 - d) / ES^{2%}(pietei)."""
    m = R['SPX'].values
    es2 = -m[m < -2].mean() / 100                           # pierderea medie a S&P 500 in zilele sub -2% (fractie)
    kappa = -np.log(1 - d) / es2
    return {'es2': 100 * es2, 'n2': int((m < -2).sum()), 'kappa': kappa, 'ln': -np.log(1 - d),
            'exact': 1 - (1 - d) ** beta, 'short18': 1 - np.exp(-18 * beta * es2), 'shortk': 1 - np.exp(-kappa * beta * es2),
            'norm_tail2': stats.norm.pdf(2) / stats.norm.cdf(-2)}


def a4_srisk_k():
    """Aceeasi banca cu k = 5.5% (prag prudential mai mic) si pragul de levier."""
    r8 = a3_mes_srisk()
    r55 = a3_mes_srisk(k=0.055)
    return {'k8': r8, 'k55': r55}


def a5_gfevd(A=((0.5, 0.2), (0.1, 0.4)), S=((1.0, 0.5), (0.5, 1.0))):
    """GFEVD la H = 1 si 2 pentru un VAR(1) bivariat: nenormalizat, normalizat si Cholesky."""
    A, S = np.asarray(A), np.asarray(S)
    out = {}
    for H in (1, 2):
        Phi = ma_coefs([A], H)
        num = sum((P @ S) ** 2 for P in Phi) / np.diag(S)[None, :]
        den = np.array([sum((P @ S @ P.T)[i, i] for P in Phi) for i in range(2)])
        th = num / den[:, None]
        out[f'H{H}'] = {'raw': th, 'rowsum': th.sum(1), 'norm': th / th.sum(1, keepdims=True),
                        'C': 100 * (th / th.sum(1, keepdims=True))[[0, 1], [1, 0]].sum() / 2}
    L = np.linalg.cholesky(S)
    num = (L ** 2)
    out['chol_H1'] = num / num.sum(1, keepdims=True)
    return out


def a6_gfevd():
    return a5_gfevd(A=((0.5, 0.0), (0.4, 0.5)), S=((1.0, 0.3), (0.3, 1.0)))


A5_M = np.array([[70, 20, 10], [25, 60, 15], [5, 10, 85]], float)
A6_M = np.array([[55, 25, 15, 5], [20, 50, 20, 10], [10, 15, 65, 10], [5, 5, 10, 80]], float)


def dy_from_matrix(M):
    """Tabelul Diebold-Yilmaz dintr-o matrice de contributii (%, liniile insumeaza 100)."""
    off = M - np.diag(np.diag(M))
    frm, to = off.sum(1), off.sum(0)
    return {'from': frm, 'to': to, 'net': to - frm, 'total': off.sum() / len(M), 'pairwise': (off.T - off)}


def a5_dy():
    return dy_from_matrix(A5_M)


def a6_dy():
    return dy_from_matrix(A6_M)


def reverse_2f(b, S, target):
    b, S = np.asarray(b, float), np.asarray(S, float)
    sb2 = b @ S @ b
    f = -target * S @ b / sb2
    d = target / np.sqrt(sb2)
    return {'Sb': S @ b, 'sb2': sb2, 'sb': np.sqrt(sb2), 'f': f, 'd': d, 'p': stats.norm.cdf(-d)}


def a7_reverse():
    return reverse_2f([1.2, 0.8], [[16, 6], [6, 9]], 20)


def a8_reverse():
    """Scenariul A7 sub o distributie Student-t multivariata cu nu = 4 (aceeasi covarianta)."""
    r = reverse_2f([1.2, 0.8], [[16, 6], [6, 9]], 20)
    nu = 4
    out = {'nu': nu, 'd': r['d'], 'p_norm': r['p'], 'scale': np.sqrt(nu / (nu - 2)),
           'p_t': stats.t.sf(r['d'] * np.sqrt(nu / (nu - 2)), nu)}
    r30 = reverse_2f([1.2, 0.8], [[16, 6], [6, 9]], 30)
    out.update({'d30': r30['d'], 'p30_norm': r30['p'], 'p30_t': stats.t.sf(r30['d'] * np.sqrt(nu / (nu - 2)), nu)})
    out['ratio'] = out['p_t'] / out['p_norm']
    out['ratio30'] = out['p30_t'] / out['p30_norm']
    return out


# =============================================================================
# PARTEA B
# =============================================================================
def b1_us_dcovar5():
    """Delta-CoVaR 5% pentru bancile americane: interval bootstrap pe blocuri vs i.i.d."""
    out = {}
    rng = np.random.default_rng(SEED)
    for i, k in enumerate(US):
        xs, xi = system_ex(k, US).values, R[k].values
        c = covar_static(xs, xi, 0.05)
        lo, hi = covar_boot(xs, xi, 0.05, B=999, block=20, seed=SEED + i)
        iid = []
        for _ in range(999):
            idx = rng.integers(0, len(xi), len(xi))
            iid.append(covar_static(xs[idx], xi[idx], 0.05)['dcovar'])
        out[k] = {'b': c['b'], 'var_i': c['var_i'], 'covar': c['covar'], 'dcovar': c['dcovar'], 'lo': lo, 'hi': hi,
                  'iid_lo': np.percentile(iid, 2.5), 'iid_hi': np.percentile(iid, 97.5), 'var_sys': c['var_sys']}
    return out


def fig_b1(res):
    ks = list(res)
    xs = np.arange(len(ks))
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    d = np.array([res[k]['dcovar'] for k in ks])
    ax.errorbar(xs - 0.12, d, yerr=[d - [res[k]['lo'] for k in ks], np.array([res[k]['hi'] for k in ks]) - d],
                fmt='o', color=MainBlue, capsize=3, lw=1, label='Moving-block bootstrap (blocks of 20 days)')
    ax.errorbar(xs + 0.12, d, yerr=[d - [res[k]['iid_lo'] for k in ks], np.array([res[k]['iid_hi'] for k in ks]) - d],
                fmt='s', color=Orange, capsize=3, lw=1, ms=4, label='i.i.d. bootstrap')
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in ks], fontsize=8, rotation=20, ha='right')
    ax.set_ylabel('ΔCoVaR 5% with 95% interval (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.3)
    save_fig('ch18_sem_b1')


def b2_eu_dcovar():
    """Delta-CoVaR 1% si 5% pentru bancile europene si clasamentele lor."""
    out = {}
    for i, k in enumerate(EU):
        xs, xi = system_ex(k, EU).values, R[k].values
        c1, c5 = covar_static(xs, xi, 0.01), covar_static(xs, xi, 0.05)
        lo, hi = covar_boot(xs, xi, 0.01, B=999, block=20, seed=SEED + 10 + i)
        out[k] = {'d1': c1['dcovar'], 'd5': c5['dcovar'], 'lo1': lo, 'hi1': hi, 'var1': c1['var_i'], 'b1': c1['b']}
    t = pd.DataFrame(out).T
    return {'table': t.to_dict(orient='index'), 'rank1': list(t['d1'].sort_values(ascending=False).index),
            'rank5': list(t['d5'].sort_values(ascending=False).index),
            'spearman': stats.spearmanr(t['d1'], t['d5']).correlation}


def b4_rank_boot(B=999):
    """Corelatia Spearman intre VaR 1% si Delta-CoVaR 1% pe cele 11 banci, cu bootstrap pe blocuri pe zile."""
    ks = US + EU
    def stat(idx):
        v, d = [], []
        for k in ks:
            mem = US if k in US else EU
            xs = R[[j for j in mem if j != k]].mean(axis=1).values[idx]
            c = covar_static(xs, R[k].values[idx], 0.01)
            v.append(c['var_i'])
            d.append(c['dcovar'])
        return stats.spearmanr(v, d).correlation
    n = len(R)
    full = stat(np.arange(n))
    rng = np.random.default_rng(SEED)
    bs = [stat(block_bootstrap_idx(n, 20, rng)) for _ in range(B)]
    return {'rho': full, 'lo': np.percentile(bs, 2.5), 'hi': np.percentile(bs, 97.5), 'B': B}


def cholesky_fevd(A, S, H=10, order=None):
    """Descompunerea ortogonala (Cholesky) a dispersiei, pentru o ordine data a variabilelor."""
    k = S.shape[0]
    order = list(range(k)) if order is None else order
    P = np.eye(k)[order]
    Sp = P @ S @ P.T
    L = np.linalg.cholesky(Sp)
    Phi = [P @ F @ P.T for F in ma_coefs(A, H)]
    num = sum((F @ L) ** 2 for F in Phi)
    th = num / num.sum(axis=1, keepdims=True)
    inv = np.argsort(order)
    return th[np.ix_(inv, inv)]


def b5_dy_sensitivity():
    """Indicele total pentru orizonturi H si ordine VAR p; generalizat vs Cholesky in doua ordini."""
    Y = V.values
    grid = {}
    for p in [1, 2, 3, 4]:
        A, S = var_fit(Y, p)
        for H in [5, 10, 20]:
            grid[f'p{p}_H{H}'] = spillover_table(gfevd(A, S, H), ALL)['total']
    A, S = var_fit(Y, 1)
    ch_us = spillover_table(cholesky_fevd(A, S, 10), ALL)
    ch_ro = spillover_table(cholesky_fevd(A, S, 10, order=list(range(len(ALL)))[::-1]), ALL)
    g = spillover_table(gfevd(A, S, 10), ALL)
    return {'grid': grid, 'chol_us_first': ch_us['total'], 'chol_ro_first': ch_ro['total'], 'gen': g['total'],
            'net_us_first': ch_us['net'][US].sum(), 'net_ro_first': ch_ro['net'][US].sum(),
            'gen_net_us': g['net'][US].sum()}


def fig_b5(res):
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    for p, c in zip([1, 2, 3, 4], [MainBlue, IDAred, Forest, Purple]):
        ax.plot([5, 10, 20], [res['grid'][f'p{p}_H{H}'] for H in [5, 10, 20]], 'o-', color=c, label=f'VAR({p})')
    ax.set_xticks([5, 10, 20])
    ax.set_xlabel('Forecast horizon H (days)')
    ax.set_ylabel('Total connectedness (%)')
    legend_outside_bottom(ax, ncol=4, y=-0.25)
    save_fig('ch18_sem_b5')


def b6_rolling_test():
    """Media indicelui total 2020-2026 vs 2010-2019 (erori standard Newey-West pe seria cu pas de 5 zile)."""
    import statsmodels.api as sm
    tot = pd.read_csv(os.path.join(HERE, 'ch18_spill_rolling.csv'), index_col=0, parse_dates=True).iloc[:, 0]
    d = (tot.index >= '2020-01-01').astype(float)
    X = sm.add_constant(d)
    m = sm.OLS(tot.values, X).fit(cov_type='HAC', cov_kwds={'maxlags': 50})
    m0 = sm.OLS(tot.values, X).fit()
    return {'before': tot[tot.index < '2020-01-01'].mean(), 'after': tot[tot.index >= '2020-01-01'].mean(),
            'diff': m.params[1], 't_hac': m.tvalues[1], 't_ols': m0.tvalues[1], 'n': len(tot)}


def b6_subsample_boot(B=999):
    """Conectivitatea totala 2010-2019 fata de 2020-2026: VAR(1) pe fiecare subperioada, bootstrap pe blocuri de
    reziduuri in fiecare subperioada (extrageri independente) -> interval pentru diferenta."""
    Y1, Y2 = V.loc[:'2019-12-31'].values, V.loc['2020-01-01':].values
    t1, _ = spill_bootstrap(Y1, 1, B=B, seed=SEED + 61)
    t2, _ = spill_bootstrap(Y2, 1, B=B, seed=SEED + 62)
    c1 = spillover_table(gfevd(*var_fit(Y1, 1), 10), ALL)['total']
    c2 = spillover_table(gfevd(*var_fit(Y2, 1), 10), ALL)['total']
    d = t2 - t1
    return {'c1': c1, 'c2': c2, 'diff': c2 - c1, 'lo': np.percentile(d, 2.5), 'hi': np.percentile(d, 97.5),
            'lo1': np.percentile(t1, 2.5), 'hi1': np.percentile(t1, 97.5), 'lo2': np.percentile(t2, 2.5),
            'hi2': np.percentile(t2, 97.5), 'n1': len(Y1), 'n2': len(Y2), 'bias1': t1.mean() - c1, 'bias2': t2.mean() - c2}


def b7_frm_window():
    """FRM intr-o fereastra: lambda GACV si legaturile active pentru JPMorgan (calm vs COVID-19)."""
    D = frm_design()
    out = {}
    for end in ['2019-06-28', '2020-03-31']:
        w = D.loc[:end].iloc[-63:]
        r = frm_window(w, 'JPM')
        names = [j for j in ALL if j != 'JPM'] + ['S&P 500 (t-1)', 'Euro Stoxx 50 (t-1)', 'VIX (t-1)']
        coef = pd.Series(r['coef'], index=names)
        act = coef[coef.abs() > 1e-8].sort_values(key=np.abs, ascending=False)
        out[end] = {'lambda': r['lambda'], 'df': r['df_sel'], 'active': {NAMES.get(k, k): v for k, v in act.head(4).items()},
                    'n_active': len(act), 'first': w.index[0]}
    return out


def b8_ro_stress(value=1_000_000):
    """Portofoliu 50% Banca Transilvania / 50% BRD, rebalansat zilnic: scenarii istorice si un scenariu ipotetic pe factori.

    Randamentul log exact al portofoliului: 100 ln(1/2 e^{r_TLV/100} + 1/2 e^{r_BRD/100}) (nu media randamentelor log).
    Scenariul ipotetic: socurile factorilor sunt randamente log saptamanale; randamentul log prezis al fiecarei banci
    beta_k' f se transforma in randament simplu, apoi se aplica ponderile 50/50."""
    X = R[RO]
    port = 100 * np.log(np.exp(X / 100).mean(axis=1))
    out = {}
    for name, a, b in [('RO bank tax', '2018-12-10', '2019-01-31'), ('COVID-19', '2020-02-15', '2020-04-30')]:
        p = port.loc[a:b].rolling(10).sum()
        end = p.idxmin()
        i = port.index.get_loc(end)
        out[name] = {'loss': -100 * (np.exp(p.min() / 100) - 1), 'start': port.index[i - 9], 'end': end,
                     'loss_meanlog': -100 * (np.exp(X.mean(axis=1).loc[a:b].rolling(10).sum().min() / 100) - 1)}
        out[name]['amt'] = out[name]['loss'] / 100 * value
    W = weekly_returns(RO + ['SX5E', 'BET'])
    F = W[['SX5E', 'BET']]
    Xf = np.column_stack([np.ones(len(F)), F.values])
    coefs = {k: np.linalg.lstsq(Xf, W[k].values, rcond=None)[0] for k in RO}
    bet = np.mean([coefs[k][1:] for k in RO], axis=0)
    shock = np.array([-25.0, -20.0])                             # randamente log saptamanale (%)
    rhat = {k: coefs[k][1:] @ shock for k in RO}                 # randamentul log prezis al fiecarei banci (%)
    simple = {k: 100 * (np.exp(rhat[k] / 100) - 1) for k in RO}  # randamentul simplu corespunzator (%)
    loss = -np.mean([simple[k] for k in RO])                     # pierderea portofoliului 50/50 (%)
    out['hyp'] = {'b_sx5e': bet[0], 'b_bet': bet[1], 'loss': loss, 'amt': loss / 100 * value,
                  'loglin': -bet @ shock,
                  'b_bank': {k: list(coefs[k][1:]) for k in RO}, 'rhat': rhat, 'simple': simple,
                  'r2': np.mean([1 - np.var(W[k].values - Xf @ coefs[k]) / np.var(W[k].values) for k in RO])}
    return out


# =============================================================================
# PARTEA C
# =============================================================================
def c1_ro_exposure():
    """Expunerea bancilor romanesti la stresul bancar european: CoVaR de expunere, subperioade, conectivitate."""
    sys_eu = R[EU].mean(axis=1)
    out = {}
    for k in RO:
        row = {}
        for a in [0.05, 0.01]:
            e = covar_static(R[k], sys_eu, a)                   # banca romaneasca | sistemul european in criza
            lo, hi = covar_boot(R[k].values, sys_eu.values, a, B=999, block=20, seed=SEED + 30)
            row[f'e{int(a * 100)}'] = {'covar': e['covar'], 'dcovar': e['dcovar'], 'b': e['b'], 'var': -np.quantile(R[k], a),
                                       'lo': lo, 'hi': hi}
            dom = covar_static(R[k], R['BET'], a)
            row[f'bet{int(a * 100)}'] = {'dcovar': dom['dcovar'], 'b': dom['b']}
        for lab, a, b in [('p1', '2010-01-01', '2017-12-31'), ('p2', '2018-01-01', '2026-12-31')]:
            e = covar_static(R[k].loc[a:b], sys_eu.loc[a:b], 0.05)
            y_, x_ = R[k].loc[a:b].values, sys_eu.loc[a:b].values
            rng = np.random.default_rng(SEED + 31)
            dr = []
            for _ in range(999):
                idx = block_bootstrap_idx(len(y_), 20, rng)
                dr.append(covar_static(y_[idx], x_[idx], 0.05)['dcovar'])
            row[lab] = {'dcovar': e['dcovar'], 'b': e['b'], 'lo': np.percentile(dr, 2.5), 'hi': np.percentile(dr, 97.5),
                        'se': np.std(dr, ddof=1)}
        # subperioadele sunt disjuncte: extragerile bootstrap sunt independente, deci se(dif)^2 = se1^2 + se2^2
        dd = row['p2']['dcovar'] - row['p1']['dcovar']
        sd = np.sqrt(row['p1']['se'] ** 2 + row['p2']['se'] ** 2)
        row['diff'] = {'d': dd, 'se': sd, 'z': dd / sd, 'p': 2 * stats.norm.sf(abs(dd / sd))}
        row['corr'] = R[k].corr(sys_eu)
        row['corr_bet'] = R[k].corr(R['BET'])
        out[k] = row
    # conectivitatea (volatilitate): cat din dispersia bancilor romanesti vine de la bancile europene, pe ferestre mobile
    Y = V
    rows = {}
    for end in range(250, len(Y) + 1, 5):
        w = Y.iloc[end - 250:end]
        A, S = var_fit(w.values, 2)
        th = 100 * gfevd(A, S, 10)
        ro_i = [ALL.index(k) for k in RO]
        rows[Y.index[end - 1]] = {'EU': th[np.ix_(ro_i, [ALL.index(k) for k in EU])].sum(1).mean(),
                                  'US': th[np.ix_(ro_i, [ALL.index(k) for k in US])].sum(1).mean(),
                                  'RO_other': th[ro_i[0], ro_i[1]] / 2 + th[ro_i[1], ro_i[0]] / 2}
    f = pd.DataFrame(rows).T
    f.to_csv(os.path.join(HERE, 'ch18_ro_from_eu.csv'))
    out['roll'] = {'eu_mean': f['EU'].mean(), 'us_mean': f['US'].mean(), 'eu_max': f['EU'].max(),
                   'eu_max_date': f['EU'].idxmax(), 'eu_2019': f['EU'].loc['2019'].mean(),
                   'eu_2020': f['EU'].loc['2020-03':'2020-12'].mean(), 'eu_last': f['EU'].iloc[-1],
                   'eu_2022': f['EU'].loc['2022'].mean(), 'ro_other_mean': f['RO_other'].mean()}
    return out, f


def fig_c1(res, f):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9), gridspec_kw={'width_ratios': [1, 1.6]})
    ax = axes[0]
    xs = np.arange(2)
    for j, (lab, c) in enumerate([('p1', MainBlue), ('p2', IDAred)]):
        d = np.array([res[k][lab]['dcovar'] for k in RO])
        lo = np.array([res[k][lab]['lo'] for k in RO])
        hi = np.array([res[k][lab]['hi'] for k in RO])
        ax.bar(xs + (j - 0.5) * 0.36, d, 0.34, color=c, label='2010-2017' if lab == 'p1' else '2018-2026')
        ax.errorbar(xs + (j - 0.5) * 0.36, d, yerr=[d - lo, hi - d], fmt='none', ecolor='black', capsize=2, lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in RO], fontsize=8)
    ax.set_ylabel('Exposure ΔCoVaR 5% (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    ax = axes[1]
    ax.plot(f.index, f['EU'], color=IDAred, lw=0.9, label='From European banks')
    ax.plot(f.index, f['US'], color=MainBlue, lw=0.9, label='From US banks')
    ax.set_ylabel('Share of RO banks\' volatility\nforecast error variance (%)')
    ax.set_xlim(f.index[0], f.index[-1])
    mark_events(ax)
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    fig.tight_layout()
    save_fig('ch18_sem_c1')


if __name__ == '__main__':
    SEM['A1'] = a1_covar_normal()
    SEM['A2'] = a2_covar_normal()
    SEM['A2GE'] = a2_ge_covar()
    SEM['A3E'] = a3_euler()
    SEM['A4S'] = a4_lrmes_shortcut()
    SEM['A5G'] = a5_gfevd()
    SEM['A6G'] = a6_gfevd()
    SEM['A3'] = a3_mes_srisk()
    SEM['A4'] = a4_srisk_k()
    SEM['A5'] = a5_dy()
    SEM['A6'] = a6_dy()
    SEM['A7'] = a7_reverse()
    SEM['A8'] = a8_reverse()
    print('B1')
    SEM['B1'] = b1_us_dcovar5()
    fig_b1(SEM['B1'])
    print('B2')
    SEM['B2'] = b2_eu_dcovar()
    print('B4')
    SEM['B4'] = b4_rank_boot()
    print('B5')
    SEM['B5'] = b5_dy_sensitivity()
    fig_b5(SEM['B5'])
    SEM['B6'] = b6_rolling_test()
    print('B6 bootstrap')
    SEM['B6S'] = b6_subsample_boot()
    print('B7')
    SEM['B7'] = b7_frm_window()
    SEM['B8'] = b8_ro_stress()
    print('C1')
    SEM['C1'], f = c1_ro_exposure()
    fig_c1(SEM['C1'], f)
    with open(os.path.join(HERE, 'sem18_results.json'), 'w') as fjs:
        json.dump(jsonable(SEM), fjs, indent=1, default=str)
    print('saved sem18_results.json')

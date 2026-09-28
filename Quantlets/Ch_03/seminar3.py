"""
seminar3.py -- Calculele pentru Seminarul 3 (MFM): modele factoriale
===================================================================
Partea A (verificari numerice ale derivarilor), Partea B (date reale), Partea C (analiza de referinta).
Toate rezultatele se scriu in sem3_results.json (folosite in versiunea profesorului).
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
from mfm_data import (prices, log_returns, french, factors, ols_hac, grs_test,
                      SECTORS, SECTORS_ALL, FACTOR_ETFS, BVB)
import generate_all_charts as g

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42


def block_bootstrap_alpha(y, X, B=2000, block=20, periods=252, seed=SEED):
    """Bootstrap pe blocuri mobile (Kunsch) pentru alfa anualizat dintr-o regresie OLS."""
    rng = np.random.default_rng(seed)
    y, X = np.asarray(y), np.asarray(X)
    n = len(y)
    nb = int(np.ceil(n / block))
    out = np.empty(B)
    Z = np.column_stack([np.ones(n), X])
    for b in range(B):
        starts = rng.integers(0, n - block, nb)
        idx = (starts[:, None] + np.arange(block)).ravel()[:n]
        coef = np.linalg.lstsq(Z[idx], y[idx], rcond=None)[0]
        out[b] = coef[0] * periods
    return np.percentile(out, [2.5, 97.5]), out.std()


# =============================================================================
# PARTEA A
# =============================================================================
def part_a():
    R = {}
    # A3 [Rezolvat] Vasicek ca medie a posteriori; dispersia a priori estimata empiric (Bayes empiric)
    b1, b2, se1, halves = g.beta_split()
    pm, pv = g.vasicek_prior(b1, se1)
    w = pv / (pv + se1['XLK'] ** 2)
    R['A3'] = dict(beta=b1['XLK'], se=se1['XLK'], prior_mean=pm, var_cs=b1.var(ddof=1), mean_se2=(se1 ** 2).mean(),
                   prior_var=pv, w=w, vasicek=w * b1['XLK'] + (1 - w) * pm, beta_later=b2['XLK'],
                   blume=0.33 + 0.67 * b1['XLK'])
    # A4 [Propus] panta Blume ca pondere de contractie: plim = Var(beta) / (Var(beta) + se^2) daca beta e constant
    c, a = np.polyfit(b1, b2, 1)
    R['A4'] = dict(a=a, c=c, w_implied=pv / (pv + (se1 ** 2).mean()), a_implied=(1 - pv / (pv + (se1 ** 2).mean())) * pm)
    # A5 [Rezolvat] 10 valori p ipotetice
    p = np.array([0.001, 0.004, 0.009, 0.012, 0.021, 0.035, 0.048, 0.060, 0.20, 0.55])
    m = len(p)
    bonf = p < 0.05 / m
    holm, stop = [], False
    for k, pk in enumerate(np.sort(p)):
        ok = (not stop) and pk < 0.05 / (m - k)
        stop = stop or not ok
        holm.append(ok)
    bh_crit = 0.05 * np.arange(1, m + 1) / m
    ps = np.sort(p)
    kmax = max([k + 1 for k in range(m) if ps[k] <= bh_crit[k]], default=0)
    R['A5'] = dict(p=p.tolist(), naive=int((p < 0.05).sum()), bonferroni=int(bonf.sum()), holm=int(sum(holm)),
                   bh=kmax, bh_crit=bh_crit.round(4).tolist())
    # A2 [Propus] GRS = castigul de raport Sharpe patrat (valori din date: 25 de portofolii, CAPM)
    res, ex, mk = g.sml_data()
    R['A2'] = g.grs_sharpe(ex.values, mk.values)
    # A6 [Propus] factor inutil (Kan & Zhang, 1999) si A7 [Rezolvat] erori in variabile
    R['A6'] = g.useless_factor_sim()
    R['A7'] = g.eiv_attenuation()
    # A8 [Propus] active echicorelate
    R['A8'] = dict(rho=0.5, l1=1 + 2 * 0.5, l2=1 - 0.5, share1=(1 + 2 * 0.5) / 3)
    return R


# =============================================================================
# PARTEA B
# =============================================================================
def b1_xlk():
    ex, F = g.monthly_excess(['XLK.US', 'SPY.US'])
    y, x = ex['XLK.US'].values, F['Mkt-RF'].values
    lags = int(np.floor(4 * (len(y) / 100) ** (2 / 9)))           # regula Newey-West: T = 331 -> 5
    b, se, t, e, r2 = ols_hac(y, x, lags=lags)
    Z = np.column_stack([np.ones(len(y)), x])
    s2 = e @ e / (len(y) - 2)
    se_cl = np.sqrt(np.diag(s2 * np.linalg.inv(Z.T @ Z)))
    ci, bse = block_bootstrap_alpha(y, x, block=12, periods=12)
    return dict(T=len(y), lags=lags, start=str(ex.index[0].date()), end=str(ex.index[-1].date()),
                alpha=b[0] * 12, beta=b[1], se_alpha_cl=se_cl[0] * 12, se_alpha_nw=se[0] * 12,
                se_beta_cl=se_cl[1], se_beta_nw=se[1], t_alpha_nw=t[0], r2=r2, boot_ci=ci.tolist(), boot_se=bse)


def b2_grs():
    S = [s + '.US' for s in SECTORS]
    ex, F = g.monthly_excess(S)
    stat, p, alpha, beta = grs_test(ex.values, F['Mkt-RF'].values)
    return dict(T=len(ex), N=len(S), grs=stat, p=p, alphas=dict(zip(SECTORS, np.round(alpha * 12, 4))),
                betas=dict(zip(SECTORS, np.round(beta, 3))))


def b3_pca():
    vals, vecs, r, c1 = g.pca_sectors()
    share = vals / vals.sum()
    S = [s + '.US' for s in SECTORS_ALL]
    return dict(T=len(r), share1=share[0], share2=share[1], cum3=share[:3].sum(), corr_pc1_spy=c1,
                n_eig_gt1=int((vals > 1).sum()), nfac=g.n_factors(r[S].values, 5))


def dimson_beta(y, m, k=1):
    """Beta Dimson (1979): suma pantelor pe BET_{t+k}, ..., BET_t, ..., BET_{t-k} (tranzactionare rara)."""
    X = pd.concat({j: m.shift(j) for j in range(-k, k + 1)}, axis=1)
    d = pd.concat([y.rename('y'), X], axis=1).dropna()
    b, se, t, e, r2 = ols_hac(d['y'].values, d.drop(columns='y').values)
    return float(b[1:].sum())


def b4_bvb(start='2015-01-01'):
    res = g.bvb_betas()
    dims = {}
    for s in BVB:
        p = prices([s + '.RO', 'BET']).loc[start:]
        r = log_returns(p)
        r = r[~(r.abs() > g.MAX_ABS_RET).any(axis=1)]
        dims[s] = dimson_beta(r[s + '.RO'], r['BET'])
    res['dimson'] = pd.Series(dims)
    return res.round(3).reset_index().to_dict(orient='records')


def b5_fama_macbeth():
    E = [s + '.US' for s in SECTORS] + [e + '.US' for e in FACTOR_ETFS]
    ex, F = g.monthly_excess(E, start='2013-08-01')
    out = g.fm_krs_table(ex, F, ['Mkt-RF', 'SMB', 'HML'])
    return dict(T=len(ex), N=len(E), start=str(ex.index[0].date()), end=str(ex.index[-1].date()),
                table=out.round(4).reset_index().to_dict(orient='records'))


def b6_etf_bootstrap():
    E = ['MTUM.US', 'QUAL.US']
    out = {}
    for e in E:
        y, F = g.daily_excess_one(e)
        X = F[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']].values
        b, se, t, _, r2 = ols_hac(y.values, X, lags=10)
        ci, bse = block_bootstrap_alpha(y.values, X, B=1000, block=20)
        out[e[:-3]] = dict(n=len(y), alpha=b[0] * 252, se_nw=se[0] * 252, t=t[0], boot_ci=ci.tolist(), boot_se=bse)
    return out


def b7_multiple_testing():
    F = factors('M')
    P = french('p25', 'M').loc['1963-07-31':F.index[-1]]
    Fx = F.loc[P.index]
    ex = P.sub(Fx['RF'], axis=0)
    X = Fx[['Mkt-RF', 'SMB', 'HML']].values
    rows = []
    for c in ex.columns:
        b, se, t, _, _ = ols_hac(ex[c].values, X)
        rows.append((c, b[0] * 12, t[0], 2 * (1 - stats.norm.cdf(abs(t[0])))))
    d = pd.DataFrame(rows, columns=['port', 'alpha', 't', 'p']).set_index('port')
    m = len(d)
    ps = np.sort(d['p'].values)
    holm = 0
    for k, pk in enumerate(ps):
        if pk < 0.05 / (m - k):
            holm += 1
        else:
            break
    bh = max([k + 1 for k in range(m) if ps[k] <= 0.05 * (k + 1) / m], default=0)
    return dict(naive=int((d['p'] < 0.05).sum()), bonferroni=int((d['p'] < 0.05 / m).sum()), holm=holm, bh=bh,
                t_gt3=int((d['t'].abs() > 3).sum()), smallgrowth_alpha=d.loc['SMALL LoBM', 'alpha'],
                smallgrowth_t=d.loc['SMALL LoBM', 't'], max_abs_t=float(d['t'].abs().max()))


def b8_pca_bvb():
    names = [s for s in BVB if s != 'H2O']
    p = prices([s + '.RO' for s in names] + ['BET']).loc['2017-06-01':]
    r = log_returns(p)
    r = r[~(r.abs() > g.MAX_ABS_RET).any(axis=1)]
    X = r[[s + '.RO' for s in names]]
    Z = (X - X.mean()) / X.std()
    vals, vecs = np.linalg.eigh(np.corrcoef(Z.values.T))
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    if vecs[:, 0].sum() < 0:
        vecs[:, 0] *= -1
    pc1 = Z.values @ vecs[:, 0]
    return dict(T=len(r), start=str(r.index[0].date()), N=len(names), share1=vals[0] / vals.sum(),
                nfac=g.n_factors(X.values, 5),
                share2=vals[1] / vals.sum(), corr_pc1_bet=float(np.corrcoef(pc1, r['BET'].values)[0, 1]),
                load_pc1=dict(zip(names, np.round(vecs[:, 0], 3))))


def b9_lns(B=500, seed=SEED):
    """Lewellen-Nagel-Shanken: R^2 OLS si GLS, 25 portofolii vs 25 + 30 industrii; IC bootstrap i.i.d. pe luni."""
    rng = np.random.default_rng(seed)
    F = factors('M')
    P25 = french('p25', 'M').loc['1963-07-31':g.END]
    I30 = french('ind30', 'M').loc['1963-07-31':g.END]
    Fx = F.loc[P25.index]
    sets = {'25': P25, '25+30': pd.concat([P25, I30.add_prefix('IND_')], axis=1)}
    models = {'CAPM': ['Mkt-RF'], 'FF3': ['Mkt-RF', 'SMB', 'HML'], 'FF5': ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']}

    def r2s(ex, f):
        T, N = ex.shape
        mu = ex.mean(0)
        Z = np.column_stack([np.ones(T), f])
        Bm = np.linalg.lstsq(Z, ex, rcond=None)[0][1:].T
        X = np.column_stack([np.ones(N), Bm])
        e = mu - X @ np.linalg.lstsq(X, mu, rcond=None)[0]
        r2o = 1 - e @ e / ((mu - mu.mean()) @ (mu - mu.mean()))
        Vi = np.linalg.inv(np.cov(ex.T))
        eg = mu - X @ np.linalg.solve(X.T @ Vi @ X, X.T @ Vi @ mu)
        one = np.ones(N)
        d = mu - (one @ Vi @ mu) / (one @ Vi @ one)
        return r2o, 1 - (eg @ Vi @ eg) / (d @ Vi @ d)

    out = {}
    for sn, P in sets.items():
        ex = P.sub(Fx['RF'], axis=0).values
        T = len(ex)
        for mn, fac in models.items():
            f = Fx[fac].values
            o, gl = r2s(ex, f)
            bo = []
            for _ in range(B):
                i = rng.integers(0, T, T)
                bo.append(r2s(ex[i], f[i]))
            bo = np.array(bo)
            out[f'{mn} | {sn}'] = dict(r2_ols=o, r2_gls=gl, ci_ols=np.percentile(bo[:, 0], [2.5, 97.5]).tolist(),
                                       ci_gls=np.percentile(bo[:, 1], [2.5, 97.5]).tolist())
    return out


def b10_model_comparison():
    """Barillas-Shanken: SR^2 maxim al factorilor, 1963-2026 si 2000-2026 (bootstrap stationar)."""
    return g.model_comparison()


def b11_grs_robust(B=2000, lags=6, seed=SEED):
    """GRS pe 25 de portofolii fara normalitate: bootstrap pe reziduuri (H0 impus) si Wald GMM cu HAC."""
    rng = np.random.default_rng(seed)
    res, ex, mk = g.sml_data()
    R, f = ex.values, mk.values
    T, N = R.shape
    stat, p, alpha, beta = grs_test(R, f)
    Z = np.column_stack([np.ones(T), f])
    AB = np.linalg.lstsq(Z, R, rcond=None)[0]
    E = R - Z @ AB
    boot = np.empty(B)
    for b in range(B):
        i = rng.integers(0, T, T)
        Rb = np.outer(f, AB[1]) + E[i]                   # alfa = 0 impus; randuri intregi (corelatie transversala pastrata)
        boot[b] = grs_test(Rb, f)[0]
    # Wald GMM: momente e_t x (1, f_t); varianta HAC (Bartlett) a lui (alfa, beta)
    u = (Z[:, :, None] * E[:, None, :]).reshape(T, -1)     # T x 2N, ordine (1: alfa_1..N, f: beta_1..N)
    S = u.T @ u / T
    for l in range(1, lags + 1):
        C = u[l:].T @ u[:-l] / T
        S += (1 - l / (lags + 1)) * (C + C.T)
    D = np.kron(Z.T @ Z / T, np.eye(N))
    Di = np.linalg.inv(D)
    V = Di @ S @ Di / T
    Va = V[:N, :N]
    W = alpha @ np.linalg.solve(Va, alpha)
    S0 = u.T @ u / T
    V0 = (Di @ S0 @ Di / T)[:N, :N]
    W0 = alpha @ np.linalg.solve(V0, alpha)
    # reziduuri: asimetrie si aplatizare (motivul bootstrap-ului)
    kurt = float(np.mean(stats.kurtosis(E, axis=0, fisher=False)))
    return dict(T=T, N=N, grs=stat, p_F=p, p_boot=float((boot >= stat).mean()), boot_q95=float(np.percentile(boot, 95)),
                wald_hac=W, p_wald_hac=1 - stats.chi2.cdf(W, N), wald_white=W0, p_wald_white=1 - stats.chi2.cdf(W0, N),
                mean_kurtosis=kurt)


# =============================================================================
# PARTEA C: prime factoriale pe BVB (momentum si beta scazut), analiza de referinta
# =============================================================================
def part_c():
    names = [s for s in BVB if s not in ('H2O',)]
    px = pd.concat([g.price(s + '.RO') for s in names] + [g.price('BET')], axis=1)
    m = px.resample('ME').last().loc['2015-12-31':]
    rets = m.pct_change()
    # eliminarea lunilor cu erori de date (|r| > 50%)
    rets = rets.mask(rets.abs() > 0.5)
    stocks = [s + '.RO' for s in names]
    mom = m[stocks].shift(1) / m[stocks].shift(12) - 1          # 12-1 luni
    # beta pe 36 de luni, fata de BET
    rows = []
    for t in range(13, len(m)):
        date = m.index[t]
        avail = [s for s in stocks if pd.notna(mom[s].iloc[t - 1]) and pd.notna(rets[s].iloc[t])]
        if len(avail) < 6:
            continue
        ms = mom.iloc[t - 1][avail].sort_values()
        k = 3
        mom_ls = rets.iloc[t][ms.index[-k:]].mean() - rets.iloc[t][ms.index[:k]].mean()
        win = rets.iloc[max(0, t - 36):t]
        betas = {}
        for s in avail:
            d = win[[s, 'BET']].dropna()
            if len(d) >= 18:
                betas[s] = np.cov(d[s], d['BET'])[0, 1] / d['BET'].var()
        if len(betas) >= 6:
            bs = pd.Series(betas).sort_values()
            lowb = rets.iloc[t][bs.index[:k]].mean() - rets.iloc[t][bs.index[-k:]].mean()
        else:
            lowb = np.nan
        rows.append((date, mom_ls, lowb, len(avail)))
    d = pd.DataFrame(rows, columns=['date', 'mom', 'lowbeta', 'n']).set_index('date')
    out = {}
    for c in ['mom', 'lowbeta']:
        x = d[c].dropna()
        b, se, t, _, _ = ols_hac(x.values, np.zeros((len(x), 0)), lags=3)
        out[c] = dict(T=len(x), mean_ann=x.mean() * 12, t_nw=t[0], sd_ann=x.std() * np.sqrt(12))
    out['start'] = str(d.index[0].date())
    out['end'] = str(d.index[-1].date())
    out['n_median'] = float(d['n'].median())
    fig_part_c(d)
    return out


def fig_part_c(d):
    """Evolutia a 1 leu in cele doua strategii long-short pe blue chips BVB."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for c, col, lab in [('mom', g.MainBlue, 'Momentum 12-1: top 3 minus bottom 3'),
                        ('lowbeta', g.IDAred, 'Low beta: lowest 3 minus highest 3 (36-month beta vs BET)')]:
        x = d[c].dropna()
        ax.plot(x.index, (1 + x).cumprod(), color=col, lw=1.0, label=lab)
    ax.axhline(1, color=g.Gray, lw=0.6, ls=':')
    ax.set_ylabel('Growth of 1 RON (long-short)')
    ax.set_title('Long-short sorts on BVB blue chips, monthly', fontsize=9, loc='left')
    g.legend_outside_bottom(ax, ncol=1)
    plt.tight_layout()
    g.save_fig('ch3_sem_bvb_factors')


def to_py(o):
    return g.to_py(o)


if __name__ == '__main__':
    R = {'A': part_a(), 'B1': b1_xlk(), 'B2': b2_grs(), 'B3': b3_pca(), 'B4': b4_bvb(), 'B5': b5_fama_macbeth(),
         'B6': b6_etf_bootstrap(), 'B7': b7_multiple_testing(), 'B8': b8_pca_bvb(), 'B9': b9_lns(),
         'B10': b10_model_comparison(), 'B11': b11_grs_robust(), 'C': part_c()}
    with open(os.path.join(HERE, 'sem3_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print(json.dumps(to_py(R), indent=1, default=str))

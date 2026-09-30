"""
seminar3.py -- Computations for Seminar 3 (MFM): factor models
==============================================================
Part A (numerical checks of the derivations), Part B (real data), Part C (reference analysis).
All results are written to sem3_results.json (used in the instructor version).
Modelling Financial Markets - Daniel Traian PELE
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
from generate_all_charts import MainBlue, IDAred, Forest, Amber, Orange, Purple

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42


def block_bootstrap_alpha(y, X, B=2000, block=20, periods=252, seed=SEED, draws=False):
    """Moving-block bootstrap (Kunsch) for the annualised alpha of an OLS regression.

    The pairs (y, X) are resampled together (blocks of whole rows). draws=True also returns the draws.
    """
    rng = np.random.default_rng(seed)
    y, X = np.asarray(y), np.asarray(X)
    n = len(y)
    nb = int(np.ceil(n / block))
    out = np.empty(B)
    Z = np.column_stack([np.ones(n), X])
    for b in range(B):
        starts = rng.integers(0, n - block + 1, nb)          # the last valid block starts at n - block
        idx = (starts[:, None] + np.arange(block)).ravel()[:n]
        coef = np.linalg.lstsq(Z[idx], y[idx], rcond=None)[0]
        out[b] = coef[0] * periods
    if draws:
        return np.percentile(out, [2.5, 97.5]), out.std(), out
    return np.percentile(out, [2.5, 97.5]), out.std()


# =============================================================================
# PART A
# =============================================================================
def part_a():
    R = {}
    # A3 [Solved] Vasicek as a posterior mean; prior variance estimated from the data (empirical Bayes)
    b1, b2, se1, halves = g.beta_split()
    pm, pv = g.vasicek_prior(b1, se1)
    w = pv / (pv + se1['XLK'] ** 2)
    R['A3'] = dict(beta=b1['XLK'], se=se1['XLK'], prior_mean=pm, var_cs=b1.var(ddof=1), mean_se2=(se1 ** 2).mean(),
                   prior_var=pv, w=w, vasicek=w * b1['XLK'] + (1 - w) * pm, beta_later=b2['XLK'],
                   blume=0.33 + 0.67 * b1['XLK'])
    # A4 [Proposed] Blume slope as a shrinkage weight: plim = Var(beta) / (Var(beta) + se^2) if beta is constant
    fit = stats.linregress(b1, b2)
    c, a = fit.slope, fit.intercept
    w_imp = pv / (pv + (se1 ** 2).mean())
    t_gap = (c - w_imp) / fit.stderr                       # gap between the fitted slope and the implied value
    R['A4'] = dict(a=a, c=c, se_c=fit.stderr, w_implied=w_imp, a_implied=(1 - w_imp) * pm,
                   t_gap=t_gap, p_gap=2 * stats.t.sf(abs(t_gap), len(b1) - 2))
    # A5 [Solved] 10 hypothetical p-values
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
    # A2 [Proposed] GRS = gain in squared Sharpe ratio (values from the data: 25 portfolios, CAPM)
    res, ex, mk = g.sml_data()
    R['A2'] = g.grs_sharpe(ex.values, mk.values)
    # A6 [Proposed] useless factor (Kan & Zhang, 1999) and A7 [Solved] errors in variables
    R['A6'] = g.useless_factor_sim()
    R['A7'] = g.eiv_attenuation()
    # A8 [Proposed] assets with equal correlations
    R['A8'] = dict(rho=0.5, l1=1 + 2 * 0.5, l2=1 - 0.5, share1=(1 + 2 * 0.5) / 3)
    return R


# =============================================================================
# PART B
# =============================================================================
def b1_xlk():
    ex, F = g.monthly_excess(['XLK.US', 'SPY.US'])
    y, x = ex['XLK.US'].values, F['Mkt-RF'].values
    lags = int(np.floor(4 * (len(y) / 100) ** (2 / 9)))           # Newey-West lag rule: T = 331 -> 5
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


def dimson_beta(y, m, keep, k=1):
    """Dimson (1979) beta: sum of the slopes on BET_{t+k}, ..., BET_t, ..., BET_{t-k} (thin trading).

    The leads and lags of BET are built on the full calendar of the (stock, BET) pair,
    BEFORE the days with data errors are dropped (keep = False), so no dropped day is skipped over.
    """
    X = pd.concat({j: m.shift(j) for j in range(-k, k + 1)}, axis=1)
    d = pd.concat([y.rename('y'), X], axis=1)[keep].dropna()
    b, se, t, e, r2 = ols_hac(d['y'].values, d.drop(columns='y').values)
    return float(b[1:].sum())


def b4_bvb(start='2015-01-01'):
    res = g.bvb_betas()
    dims = {}
    for s in BVB:
        p = prices([s + '.RO', 'BET']).loc[start:]          # each stock aligned separately with BET
        r = log_returns(p)
        keep = ~(r.abs() > g.MAX_ABS_RET).any(axis=1)      # the threshold applies to the (stock, BET) pair
        dims[s] = dimson_beta(r[s + '.RO'], r['BET'], keep)
    res['dimson'] = pd.Series(dims)
    return res.round(3).reset_index().to_dict(orient='records')


def b5_fama_macbeth():
    E = [s + '.US' for s in SECTORS] + [e + '.US' for e in FACTOR_ETFS]
    ex, F = g.monthly_excess(E, start='2013-08-01')
    out = g.fm_krs_table(ex, F, g.FF3)
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
    P = french('p25', 'M').loc['1963-07-31':g.END]
    Fx = F.loc[P.index]
    ex = P.sub(Fx['RF'], axis=0)
    X = Fx[g.FF3].values
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
    # Benjamini-Yekutieli (2001): valid under any dependence, BH thresholds divided by sum_j 1/j
    cm = (1 / np.arange(1, m + 1)).sum()
    by = max([k + 1 for k in range(m) if ps[k] <= 0.05 * (k + 1) / (m * cm)], default=0)
    return dict(T=len(ex), naive=int((d['p'] < 0.05).sum()), bonferroni=int((d['p'] < 0.05 / m).sum()), holm=holm, bh=bh, by=by,
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
    # actual mean off-diagonal correlation, compared with the US sectors over the same period
    def avg_corr(Y):
        C = np.corrcoef(np.asarray(Y, float).T)
        n = C.shape[0]
        return float((C.sum() - n) / (n * (n - 1)))
    vals_us, vecs_us, r_us, _ = g.pca_sectors()
    a0 = r_us.index[0]
    us = r_us[[x + '.US' for x in SECTORS_ALL]]
    return dict(T=len(r), start=str(r.index[0].date()), N=len(names), share1=vals[0] / vals.sum(),
                avg_corr=avg_corr(X), avg_corr_common=avg_corr(X.loc[a0:]), common_from=str(a0.date()),
                avg_corr_us=avg_corr(us),
                nfac=g.n_factors(X.values, 5),
                share2=vals[1] / vals.sum(), corr_pc1_bet=float(np.corrcoef(pc1, r['BET'].values)[0, 1]),
                load_pc1=dict(zip(names, np.round(vecs[:, 0], 3))))


def b9_lns(B=500, seed=SEED):
    """Lewellen-Nagel-Shanken: OLS and GLS R^2, 25 portfolios vs 25 + 30 industries; i.i.d. bootstrap CIs over months."""
    rng = np.random.default_rng(seed)
    F = factors('M')
    P25 = french('p25', 'M').loc['1963-07-31':g.END]
    I30 = french('ind30', 'M').loc['1963-07-31':g.END]
    Fx = F.loc[P25.index]
    sets = {'25': P25, '25+30': pd.concat([P25, I30.add_prefix('IND_')], axis=1)}
    models = {'CAPM': ['Mkt-RF'], 'FF3': g.FF3, 'FF5': g.FF5}

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
    """Barillas-Shanken: maximum squared Sharpe ratio of the factors, 1963-2026 and 2000-2026 (stationary bootstrap)."""
    return g.model_comparison()


def b11_grs_robust(B=2000, lags=6, seed=SEED, draws=False):
    """GRS on 25 portfolios without normality: residual bootstrap (H0 imposed) and GMM Wald with HAC."""
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
        Rb = np.outer(f, AB[1]) + E[i]                   # alpha = 0 imposed; whole rows (cross-sectional correlation preserved)
        boot[b] = grs_test(Rb, f)[0]
    # GMM Wald: moments e_t x (1, f_t); HAC (Bartlett) variance of (alpha, beta)
    u = (Z[:, :, None] * E[:, None, :]).reshape(T, -1)     # T x 2N, order (1: alpha_1..N, f: beta_1..N)
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
    # residuals: skewness and kurtosis (the reason for the bootstrap)
    kurt = float(np.mean(stats.kurtosis(E, axis=0, fisher=False)))
    if draws:
        return boot, stat, E
    return dict(T=T, N=N, grs=stat, p_F=p, p_boot=float((boot >= stat).mean()), n_exceed=int((boot >= stat).sum()),
                p_boot_plus1=float(((boot >= stat).sum() + 1) / (B + 1)), boot_q95=float(np.percentile(boot, 95)),
                wald_hac=W, p_wald_hac=1 - stats.chi2.cdf(W, N), wald_white=W0, p_wald_white=1 - stats.chi2.cdf(W0, N),
                mean_kurtosis=kurt)


# =============================================================================
# PART C: factor premia on the BVB (momentum and low beta), reference analysis
# =============================================================================
def part_c(return_series=False):
    """Momentum 12-1 and low beta on BVB blue chips, using only information available at portfolio formation.

    * incomplete months (the last month, if the data stop before its end) are dropped;
    * |r| > 50% in a month = unadjusted capital event (FP, September 2023): the return is unavailable;
      the stock is left out of rankings whose signal contains that month, and out of the portfolio
      mean in the holding month (rule fixed in advance);
    * eligibility in month t uses only information from the end of month t-1 (signal and price available).
    """
    names = [s for s in BVB if s not in ('H2O',)]
    px = pd.concat([g.price(s + '.RO') for s in names] + [g.price('BET')], axis=1)
    m = px.resample('ME').last().loc['2015-12-31':]
    last = px.index[-1]
    if (last + pd.offsets.BDay(1)).month == last.month:          # the last month is incomplete
        m = m.iloc[:-1]
    stocks = [s + '.RO' for s in names]
    raw = m.pct_change()
    flag = raw.abs() > 0.5
    rets = raw.mask(flag)                                         # valid returns (NaN = error or missing)
    gross = 1 + rets[stocks]                                      # unavailable return -> unavailable signal
    mom = gross.rolling(11, min_periods=11).apply(np.prod, raw=True).shift(2) - 1   # months t-12 ... t-2
    hold = rets[stocks].fillna(0.0).where(m[stocks].shift(1).notna()).mask(flag[stocks])   # return of month t
    rows = []
    for t in range(13, len(m)):
        date = m.index[t]
        avail = [s for s in stocks if pd.notna(mom[s].iloc[t]) and pd.notna(m[s].iloc[t - 1])]
        if len(avail) < 6:
            continue
        ms = mom.iloc[t][avail].sort_values()
        k = 3
        mom_ls = hold.iloc[t][ms.index[-k:]].mean() - hold.iloc[t][ms.index[:k]].mean()
        win = rets.iloc[max(0, t - 36):t]                         # only months t-36 ... t-1
        betas = {}
        for s in avail:
            d = win[[s, 'BET']].dropna()
            if len(d) >= 18:
                betas[s] = np.cov(d[s], d['BET'])[0, 1] / d['BET'].var()
        if len(betas) >= 6:
            bs = pd.Series(betas).sort_values()
            lowb = hold.iloc[t][bs.index[:k]].mean() - hold.iloc[t][bs.index[-k:]].mean()
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
    out['n_flagged'] = int(flag[stocks].sum().sum())
    # instructor diagnostics on the same sample (variants of the signal timing and of the return aggregation)
    look = (1 + rets[stocks]).rolling(12, min_periods=12).apply(np.prod, raw=True) - 1
    logh = np.log1p(hold)
    var, ser = {}, {'corrected': d['mom']}
    for lab, sig, h in [('lookahead', look, hold), ('log', mom, logh), ('ai_answer', look, logh)]:
        v = []
        for t in d.index:
            avail = [s for s in stocks if pd.notna(sig.loc[t, s]) and pd.notna(h.loc[t, s])]
            ss = sig.loc[t, avail].sort_values()
            v.append(h.loc[t, ss.index[-3:]].mean() - h.loc[t, ss.index[:3]].mean())
        v = pd.Series(v, index=d.index)
        ser[lab] = v
        var[lab] = dict(mean_ann=v.mean() * 12, sd_ann=v.std() * np.sqrt(12),
                        t_nw=ols_hac(v.values, np.zeros((len(v), 0)), lags=3)[2][0])
    out['c2_variants'] = var
    # C1: example ranking for the last holding month (12-1 signal, eligibility at t-1)
    t = len(m) - 1
    avail = [s for s in stocks if pd.notna(mom[s].iloc[t]) and pd.notna(m[s].iloc[t - 1])]
    ms = mom.iloc[t][avail].sort_values(ascending=False)
    out['c1_example'] = dict(month=str(m.index[t].date()), signal={k[:-3]: float(v) for k, v in ms.items()},
                             hold={k[:-3]: float(hold.iloc[t][k]) for k in ms.index},
                             long=[k[:-3] for k in ms.index[:3]], short=[k[:-3] for k in ms.index[-3:]])
    fig_part_c(d)
    if return_series:
        return out, d, ser
    return out


def fig_part_c(d):
    """Growth of 1 leu in the two long-short strategies on BVB blue chips."""
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


# =============================================================================
# GRAFICELE SEMINARULUI (ch3_sem_*): cate un grafic pentru fiecare solutie
# =============================================================================
TEAL = '#17A2B8'


def _style():
    """Fonturi mai mari: graficele seminarului se afiseaza pe jumatate de slide."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10.5, 'axes.labelsize': 11, 'axes.titlesize': 10.5, 'legend.fontsize': 9.5,
                         'xtick.labelsize': 9.5, 'ytick.labelsize': 9.5})


def _ax_title(ax, text):
    ax.set_title(text, fontsize=10.5, loc='left')


def _fig_legend(fig, ncol=3, y=None):
    """Legenda comuna, in afara graficului, jos: imediat sub etichetele axelor (pozitie calculata)."""
    h, l = [], []
    for ax in fig.axes:
        hh, ll = ax.get_legend_handles_labels()
        for a, b in zip(hh, ll):
            if b not in l and not b.startswith('_'):
                h.append(a)
                l.append(b)
    fig.tight_layout()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    ymin = min(ax.get_tightbbox(r).transformed(fig.transFigure.inverted()).y0 for ax in fig.axes)
    leg = fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, ymin - 0.01), ncol=ncol, frameon=False)
    leg.set_in_layout(False)


def _ax_legend(ax, ncol=1, fontsize=None):
    """Legenda unui panou, in afara lui, jos: imediat sub eticheta axei x (pozitie calculata)."""
    fig = ax.figure
    fig.tight_layout()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    y0 = ax.get_tightbbox(r).transformed(ax.transAxes.inverted()).y0
    kw = dict(fontsize=fontsize) if fontsize else {}
    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, y0 - 0.02), ncol=ncol, frameon=False, **kw)
    leg.set_in_layout(False)


def _save(name):
    """Legendele (excluse din tight_layout) redevin parte din caseta salvata, apoi save_fig."""
    import matplotlib.pyplot as plt
    fig = plt.gcf()
    for lg in fig.legends + [a.get_legend() for a in fig.axes if a.get_legend() is not None]:
        lg.set_in_layout(True)
    g.save_fig(name)


def _label_points(ax, names, xs, ys, fs=6.5):
    """Etichete de puncte alternate deasupra/dedesubt (ordonate dupa x), ca sa nu se suprapuna."""
    order = np.argsort(xs)
    for k, i in enumerate(order):
        off = (3, 3) if k % 2 == 0 else (3, -9)
        ax.annotate(names[i], (xs[i], ys[i]), xytext=off, textcoords='offset points', fontsize=fs, color='black')


def setup_preview():
    """Pas cu pas: preturi de sfarsit de luna -> randament simplu -> minus RF -> join cu Mkt-RF (XLK)."""
    p = prices(['XLK.US', 'SPY.US']).resample('ME').last()
    r = p.pct_change()
    F = factors('M')
    ex, Fx = g.monthly_excess(['XLK.US', 'SPY.US'])
    rows = []
    for d in ex.index[:3]:
        prev = p.index[p.index.get_loc(d) - 1]
        rows.append(dict(month=str(d.date())[:7], p_prev=float(p.loc[prev, 'XLK.US']), p=float(p.loc[d, 'XLK.US']),
                         r=float(r.loc[d, 'XLK.US']), rf=float(F.loc[d, 'RF']), ex=float(ex.loc[d, 'XLK.US']),
                         mkt=float(F.loc[d, 'Mkt-RF'])))
    return dict(T=len(ex), first=str(ex.index[0].date())[:7], last=str(ex.index[-1].date())[:7], rows=rows,
                mean_ex=float(ex['XLK.US'].mean()), mean_mkt=float(Fx['Mkt-RF'].mean()))


def a1_chart():
    """A1: cu momentele de esantion, beta fata de portofoliul tangent evalueaza exact cele 9 sectoare."""
    import matplotlib.pyplot as plt
    S = [s + '.US' for s in SECTORS]
    ex, F = g.monthly_excess(S + ['SPY.US'])
    X = ex[S]
    mu, V = X.mean().values, X.cov().values
    w = np.linalg.solve(V, mu)
    w = w / w.sum()
    mu_t, var_t = mu @ w, w @ V @ w
    beta_t = V @ w / var_t
    spy = ex['SPY.US']
    beta_m = np.array([np.cov(X[s], spy)[0, 1] / spy.var() for s in S])
    mu_m = spy.mean()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    for ax, b, m, lab, ttl in [(axes[0], beta_t, mu_t, 'SML of the tangency portfolio: mean = beta x mean(tangency)',
                                'Beta on the in-sample tangency portfolio'),
                               (axes[1], beta_m, mu_m, 'SML of SPY: mean = beta x mean(SPY)', 'Beta on SPY')]:
        xs = np.linspace(0, max(b.max(), 1.6) * 1.05, 20)
        ax.plot(xs, 12 * m * xs, color=IDAred if ax is axes[0] else Forest, ls='--', lw=1.0, label=lab)
        ax.scatter(b, 12 * mu, s=18, color=MainBlue, zorder=3, label='Sector ETFs' if ax is axes[0] else '_s')
        if ax is axes[1]:
            _label_points(ax, SECTORS, b, 12 * mu)
        ax.set_xlabel(ttl)
        ax.axhline(0, color=g.Gray, lw=0.5)
    axes[0].set_ylabel('Mean excess return (ann.)')
    _ax_title(axes[0], 'Exact: every sector on the line')
    _ax_title(axes[1], 'SPY is not the tangency portfolio')
    plt.tight_layout()
    _fig_legend(fig, ncol=2)
    _save('ch3_sem_a1_sml')
    dev_t = np.abs(12 * mu - 12 * mu_t * beta_t).max()
    dev_m = 12 * mu - 12 * mu_m * beta_m
    return dict(T=len(ex), mu_t_ann=12 * mu_t, max_dev_tan=float(dev_t), max_abs_dev_spy=float(np.abs(dev_m).max()),
                dev_spy=dict(zip(SECTORS, np.round(dev_m, 4))), beta_tan=dict(zip(SECTORS, np.round(beta_t, 3))),
                mu_spy_ann=12 * mu_m)


def a3_chart(A3):
    """A3: prior, verosimilitate si posterior pentru beta XLK; prognozele fata de beta estimat ulterior."""
    import matplotlib.pyplot as plt
    pm, pv, b, se = A3['prior_mean'], A3['prior_var'], A3['beta'], A3['se']
    post_v = 1 / (1 / pv + 1 / se ** 2)
    post_m = post_v * (pm / pv + b / se ** 2)
    xs = np.linspace(0.0, 2.2, 400)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.35, 1]})
    ax = axes[0]
    ax.plot(xs, stats.norm.pdf(xs, pm, np.sqrt(pv)), color=Forest, label=f'Prior N({pm:.3f}, {pv:.3f})')
    ax.plot(xs, stats.norm.pdf(xs, b, se), color=MainBlue, ls='--', label=f'Likelihood of beta-hat = {b:.3f} (se {se:.3f})')
    ax.plot(xs, stats.norm.pdf(xs, post_m, np.sqrt(post_v)), color=IDAred, lw=1.4,
            label=f'Posterior N({post_m:.3f}, {post_v:.4f})')
    ax.set_xlabel('XLK beta')
    ax.set_ylabel('Density')
    _ax_title(ax, 'Prior x likelihood = posterior')
    _ax_legend(ax, ncol=1)
    ax = axes[1]
    labs = ['Raw OLS', 'Vasicek', 'Blume']
    vals = [b, A3['vasicek'], A3['blume']]
    cols = [MainBlue, IDAred, Amber]
    y = np.arange(3)[::-1]
    for yy, v, c, l in zip(y, vals, cols, labs):
        ax.plot(v, yy, 'o', color=c, ms=6)
        ax.annotate(f'{v:.3f} (error {abs(v - A3["beta_later"]):.3f})', (v, yy), xytext=(0, 6),
                    textcoords='offset points', fontsize=8.5, color='black', ha='center')
    ax.axvline(A3['beta_later'], color=Purple, ls=':', lw=1.0, label=f'Estimated beta 2013-2026 = {A3["beta_later"]:.3f}')
    ax.set_yticks(y, labs)
    ax.set_ylim(-0.6, 2.7)
    ax.set_xlim(1.05, 1.5)
    ax.set_xlabel('Forecast of the later XLK beta')
    _ax_title(ax, 'Forecasts from 1999-2012')
    _ax_legend(ax, ncol=1)
    plt.tight_layout()
    _save('ch3_sem_a3_bayes')
    return dict(post_mean=post_m, post_var=post_v, post_sd=np.sqrt(post_v))


def _mt_thresholds(M, alpha=0.05):
    j = np.arange(1, M + 1)
    cm = (1 / j).sum()
    return dict(bonferroni=np.full(M, alpha / M), holm=alpha / (M - j + 1), bh=j * alpha / M, by=j * alpha / (M * cm)), cm


def _pvalue_panel(ax, p, title, alpha=0.05):
    ps = np.sort(np.asarray(p))
    M = len(ps)
    j = np.arange(1, M + 1)
    th, cm = _mt_thresholds(M, alpha)
    ax.axhline(alpha, color=g.Gray, lw=0.7, ls=':', label='Naive: 0.05')
    ax.plot(j, th['bonferroni'], color=Purple, lw=1.0, label='Bonferroni: 0.05/M')
    ax.step(j, th['holm'], where='mid', color=Forest, lw=1.0, label='Holm: 0.05/(M-j+1)')
    ax.plot(j, th['bh'], color=IDAred, lw=1.0, ls='--', label='BH: j x 0.05/M')
    ax.plot(j, th['by'], color=Amber, lw=1.0, ls='-.', label=f'BY: j x 0.05/(M x {cm:.2f})')
    ax.scatter(j, ps, s=16, color=MainBlue, zorder=3, label='Sorted p-values')
    ax.set_yscale('log')
    ax.set_xlabel('Rank j of the p-value')
    ax.set_ylabel('p-value (log scale)')
    _ax_title(ax, title)


def a5_chart(p):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    _pvalue_panel(ax, p, 'Ten sorted p-values against four rejection rules')
    ax.set_xticks(np.arange(1, len(p) + 1))
    _ax_legend(ax, ncol=3)
    plt.tight_layout()
    _save('ch3_sem_a5_pvalues')
    ps = np.sort(p)
    th, cm = _mt_thresholds(len(p))
    by = max([k + 1 for k in range(len(p)) if ps[k] <= th['by'][k]], default=0)
    return dict(by=by, c_M=cm, by_thresholds=np.round(th['by'], 5).tolist(), holm_thresholds=np.round(th['holm'], 5).tolist())


def b1_chart():
    """B1: nor de puncte cu dreapta ajustata, reziduurile in timp, distributia bootstrap a lui alfa."""
    import matplotlib.pyplot as plt
    ex, F = g.monthly_excess(['XLK.US', 'SPY.US'])
    y, x = ex['XLK.US'].values, F['Mkt-RF'].values
    lags = int(np.floor(4 * (len(y) / 100) ** (2 / 9)))
    b, se, t, e, r2 = ols_hac(y, x, lags=lags)
    bw, sew, tw, _, _ = ols_hac(y, x, lags=0)                     # White (HC0)
    ci, bse, draws = block_bootstrap_alpha(y, x, block=12, periods=12, draws=True)
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), gridspec_kw={'width_ratios': [1.05, 1.25, 1]})
    ax = axes[0]
    ax.scatter(100 * x, 100 * y, s=5, color=MainBlue, alpha=0.7, label='Monthly excess returns')
    xs = np.linspace(x.min(), x.max(), 10)
    ax.plot(100 * xs, 100 * (b[0] + b[1] * xs), color=IDAred, lw=1.2, label=f'OLS: beta = {b[1]:.3f}')
    ax.set_xlabel('Mkt-RF (%)')
    ax.set_ylabel('XLK excess return (%)')
    _ax_title(ax, f'T = {len(y)} months')
    ax = axes[1]
    import matplotlib.dates as mdates
    ax.plot(ex.index, 100 * e, color=Forest, lw=0.7, label='OLS residual')
    ax.axhline(0, color=g.Gray, lw=0.5)
    ax.xaxis.set_major_locator(mdates.YearLocator(6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylabel('Residual (%)')
    _ax_title(ax, 'Residuals: 2000-02, 2008, 2020')
    ax = axes[2]
    ax.hist(100 * draws, bins=40, color=Amber, alpha=0.85, label='Bootstrap alpha (2000 draws)')
    for v in ci:
        ax.axvline(100 * v, color=IDAred, ls='--', lw=0.9)
    ax.axvline(0, color=g.Gray, lw=0.8, ls=':')
    ax.plot([], [], color=IDAred, ls='--', label='95% percentile interval')
    ax.set_xlabel('Annualised alpha (%)')
    _ax_title(ax, 'Moving-block bootstrap')
    plt.tight_layout()
    _fig_legend(fig, ncol=5)
    _save('ch3_sem_b1_xlk')
    return dict(se_alpha_white=sew[0] * 12, se_beta_white=sew[1], ratio_nw_cl=None)


def b2_details_chart():
    """B2: matrice E (T x 9), Sigma = E'E/T, forma patratica, GRS; comparatie pe aceeasi perioada cu 25 de portofolii."""
    import matplotlib.pyplot as plt
    S = [s + '.US' for s in SECTORS]
    ex, F = g.monthly_excess(S)
    R, f = ex.values, F['Mkt-RF'].values
    T, N = R.shape
    Z = np.column_stack([np.ones(T), f])
    AB = np.linalg.lstsq(Z, R, rcond=None)[0]
    E = R - Z @ AB
    Sig = E.T @ E / T
    a = AB[0]
    q = a @ np.linalg.solve(Sig, a)
    mu_m, s_m = f.mean(), f.std(ddof=0)
    W = (T - N - 1) / N * q / (1 + (mu_m / s_m) ** 2)
    crit = stats.f.ppf(0.95, N, T - N - 1)
    se_nw = np.array([ols_hac(R[:, i], f)[1][0] for i in range(N)])
    # 25 de portofolii pe aceleasi luni ca sectoarele
    P = french('p25', 'M')
    P = P.loc[P.index.intersection(ex.index)]
    ex25 = P.sub(F.loc[P.index, 'RF'], axis=0)
    st25, p25, _, _ = grs_test(ex25.values, F.loc[P.index, 'Mkt-RF'].values)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    ax = axes[0]
    order = np.argsort(a)
    yy = np.arange(N)
    ax.errorbar(1200 * a[order], yy, xerr=1.96 * 1200 * se_nw[order], fmt='o', color=MainBlue, capsize=2, lw=0.8,
                label='Annual alpha, 95% interval (Newey-West)')
    ax.axvline(0, color=g.Gray, lw=0.7, ls=':')
    ax.set_yticks(yy, [SECTORS[i] for i in order], fontsize=8.5)
    ax.set_xlabel('CAPM alpha (% a year)')
    _ax_title(ax, 'Nine sector alphas, 1999-2026')
    ax = axes[1]
    xs = np.linspace(0, 3.2, 400)
    dens = stats.f.pdf(xs, N, T - N - 1)
    ax.plot(xs, dens, color=Forest, label=f'F({N}, {T - N - 1}) under H0')
    ax.fill_between(xs[xs >= crit], dens[xs >= crit], color=IDAred, alpha=0.35, label=f'5% rejection region (> {crit:.2f})')
    ax.axvline(W, color=MainBlue, lw=1.4, label=f'Observed GRS = {W:.2f}')
    ax.set_xlabel('GRS statistic')
    ax.set_ylabel('Density')
    _ax_title(ax, f'p-value = {1 - stats.f.cdf(W, N, T - N - 1):.2f}')
    plt.tight_layout()
    _fig_legend(fig, ncol=2)
    _save('ch3_sem_b2_grs')
    return dict(T=T, N=N, q=q, mu_m=mu_m, sd_m=s_m, sr_m=mu_m / s_m, W=W, crit=crit,
                alpha_m=dict(zip(SECTORS, np.round(100 * a, 3))), se_alpha_nw_ann=dict(zip(SECTORS, np.round(1200 * se_nw, 2))),
                sig_diag=dict(zip(SECTORS, np.round(np.sqrt(np.diag(Sig)) * 100, 2))),
                grs25_same_period=st25, p25_same_period=p25, T25=len(P))


def b3_chart():
    """B3: scree + cumulativ, incarcarile PC1/PC2, criteriile Bai-Ng IC_p2 si Ahn-Horenstein."""
    import matplotlib.pyplot as plt
    vals, vecs, r, c1 = g.pca_sectors()
    S = [s + '.US' for s in SECTORS_ALL]
    X = r[S].values
    Xs = (X - X.mean(0)) / X.std(0)
    T, N = Xs.shape
    ev = np.sort(np.linalg.eigvalsh(Xs.T @ Xs / T))[::-1]
    kmax = 5
    V = np.array([ev[k:].sum() / N for k in range(kmax + 1)])
    pen = (N + T) / (N * T) * np.log(min(N, T))
    ic = np.log(V) + np.arange(kmax + 1) * pen
    er = ev[:kmax] / ev[1:kmax + 1]
    share = vals / vals.sum()
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), gridspec_kw={'width_ratios': [1, 1.35, 1]})
    ax = axes[0]
    k = np.arange(1, N + 1)
    ax.bar(k, share, color=MainBlue, alpha=0.85, label='Share of variance')
    ax.plot(k, np.cumsum(share), color=IDAred, marker='o', ms=2.5, label='Cumulative share')
    ax.axhline(1 / N, color=g.Gray, lw=0.6, ls=':')
    ax.set_xticks(k[::2])
    ax.tick_params(axis='x', labelsize=8)
    ax.set_xlabel('Component')
    _ax_title(ax, 'Scree plot')
    ax = axes[1]
    x = np.arange(N)
    ax.bar(x - 0.2, vecs[:, 0], 0.4, color=MainBlue, label='PC1 loading')
    ax.bar(x + 0.2, vecs[:, 1], 0.4, color=Amber, label='PC2 loading')
    ax.axhline(0, color=g.Gray, lw=0.5)
    ax.set_xticks(x, SECTORS_ALL, rotation=60, fontsize=8.5)
    _ax_title(ax, 'Eigenvector loadings')
    ax = axes[2]
    ax.plot(np.arange(kmax + 1), ic, color=Forest, marker='o', ms=3, label=r'Bai-Ng $IC_{p2}(k)$')
    ax.set_xlabel('k')
    ax.set_ylabel(r'$IC_{p2}$', color='black')
    ax2 = ax.twinx()
    ax2.plot(np.arange(1, kmax + 1), er, color=Purple, marker='s', ms=3, label='Ahn-Horenstein ratio')
    ax2.set_ylabel('Eigenvalue ratio', color='black')
    ax2.spines['right'].set_visible(True)
    _ax_title(ax, r'Choosing $k$ ($k_{\max} = 5$)')
    plt.tight_layout()
    _fig_legend(fig, ncol=3)
    _save('ch3_sem_b3_pca')
    return dict(T=T, N=N, ic=np.round(ic, 4).tolist(), er=np.round(er, 2).tolist(), pen=pen, eig=np.round(ev[:6], 3).tolist())


def b4_chart(b4rows, start='2015-01-01'):
    """B4: evenimentul de capital DIGI (pret) si betele OLS, Vasicek, Dimson cu intervale HAC."""
    import matplotlib.pyplot as plt
    res = pd.DataFrame(b4rows).set_index('stock').sort_values('beta')
    p = prices(['DIGI.RO', 'BET']).loc[start:]
    r = log_returns(p)
    bad = r.index[(r.abs() > g.MAX_ABS_RET).any(axis=1)]
    d0 = bad[0]
    i0 = r.index.get_loc(d0)
    tab = []
    for j in range(i0 - 2, i0 + 3):
        dt = r.index[j]
        tab.append(dict(date=str(dt.date()), r_digi=float(r['DIGI.RO'].iloc[j]),
                        bet_lag=float(r['BET'].iloc[j - 1]), bet=float(r['BET'].iloc[j]), bet_lead=float(r['BET'].iloc[j + 1]),
                        keep=bool(dt not in bad)))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={'width_ratios': [1, 1.6]})
    ax = axes[0]
    w = p['DIGI.RO'].loc[d0 - pd.Timedelta(days=45):d0 + pd.Timedelta(days=45)]
    ax.plot(w.index, w.values, color=MainBlue, lw=1.0, label='DIGI adjusted close')
    ax.plot([d0], [w.loc[d0]], 'o', color=IDAred, ms=6, label=f'Flagged day {d0:%d %b %Y}')
    import matplotlib.dates as mdates
    ax.set_yscale('log')
    ax.set_ylabel('RON (log scale)')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=8.5, rotation=30)
    _ax_title(ax, 'Unadjusted corporate event')
    ax = axes[1]
    y = np.arange(len(res))
    ax.errorbar(res['beta'], y, xerr=1.96 * res['se'], fmt='o', color=MainBlue, capsize=2, lw=0.8,
                label='OLS beta, 95% interval (Newey-West)')
    ax.plot(res['vasicek'], y + 0.18, 'D', ms=3.5, color=IDAred, label='Vasicek')
    ax.plot(res['dimson'], y - 0.18, 's', ms=3.5, color=Forest, label='Dimson (lags -1, 0, +1)')
    ax.axvline(1, color=g.Gray, ls=':', lw=0.7)
    ax.set_yticks(y, res.index, fontsize=8.5)
    ax.set_xlabel('Beta vs BET (daily log returns)')
    _ax_title(ax, 'Three betas per stock')
    plt.tight_layout()
    _fig_legend(fig, ncol=3)
    _save('ch3_sem_b4_bvb')
    return dict(event=tab, flagged=[str(x.date()) for x in bad])


def b5_chart():
    """B5: o luna de regresie transversala (efectiv vs ajustat) si primele estimate cu intervale KRS."""
    import matplotlib.pyplot as plt
    E = [s + '.US' for s in SECTORS] + [e + '.US' for e in FACTOR_ETFS]
    ex, F = g.monthly_excess(E, start='2013-08-01')
    fac = g.FF3
    Z = np.column_stack([np.ones(len(ex)), F[fac].values])
    B = np.linalg.lstsq(Z, ex.values, rcond=None)[0][1:].T            # 16 x 3
    X = np.column_stack([np.ones(len(E)), B])
    t = len(ex) - 1
    lam_t = np.linalg.lstsq(X, ex.values[t], rcond=None)[0]
    tab = g.fm_krs_table(ex, F, fac)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax = axes[0]
    fit = X @ lam_t
    ax.scatter(100 * fit, 100 * ex.values[t], s=18, color=MainBlue, zorder=3, label='16 ETFs')
    for nm, a_, b_ in zip([e[:-3] for e in E], 100 * fit, 100 * ex.values[t]):
        ax.annotate(nm, (a_, b_), xytext=(2, 2), textcoords='offset points', fontsize=7.5, color='black')
    lo, hi = min(fit.min(), ex.values[t].min()) * 100, max(fit.max(), ex.values[t].max()) * 100
    ax.plot([lo, hi], [lo, hi], color=g.Gray, ls=':', lw=0.8)
    ax.set_xlabel(r'Fitted $\hat\lambda_{0,t} + \hat\beta_i^\top \hat\lambda_t$ (%)')
    ax.set_ylabel('Actual excess return (%)')
    _ax_title(ax, f'Pass 2 in one month: {ex.index[t]:%b %Y}')
    ax = axes[1]
    names = ['Mkt-RF', 'SMB', 'HML']
    keys = ['Mkt-RF', 'SMB_FF3', 'HML']
    yy = np.arange(3)[::-1]
    ax.errorbar(100 * tab.loc[keys, 'lambda'], yy, xerr=1.96 * 100 * tab.loc[keys, 'se_krs'], fmt='o', color=MainBlue,
                capsize=3, lw=0.9, label='Estimated premium, 95% interval (KRS)')
    ax.plot(100 * tab.loc[keys, 'factor_mean'], yy, 'x', color=IDAred, ms=7, mew=1.5, label='Factor mean')
    ax.axvline(0, color=g.Gray, lw=0.6, ls=':')
    ax.set_yticks(yy, names)
    ax.set_xlabel('% a year')
    _ax_title(ax, f'Premia, T = {len(ex)} months')
    plt.tight_layout()
    _fig_legend(fig, ncol=3)
    _save('ch3_sem_b5_fm')
    return dict(month=str(ex.index[t].date())[:7], lam_t=(100 * lam_t).round(3).tolist(),
                B=dict(zip([e[:-3] for e in E], np.round(B, 2).tolist())))


def b6_chart(B6):
    """B6: alinierea calendarelor (numar de randamente) si alfa anual cu intervale HAC si bootstrap."""
    import matplotlib.pyplot as plt
    info = {}
    Fd = factors('D').loc[:g.END]
    for e in ['MTUM.US', 'QUAL.US']:
        s = g.price(e).loc[:g.END]
        s = s.loc[Fd.index[0]:]
        n_own = int(len(s) - 1)
        on = s.loc[s.index.isin(Fd.index)]
        cal = pd.Series(np.arange(len(Fd)), index=Fd.index)
        pos = cal.loc[on.index].values
        gap = np.where(np.diff(pos) > 1)[0]
        ex_ = None
        if len(gap):
            k = gap[0]
            ex_ = dict(prev=str(on.index[k].date()), next=str(on.index[k + 1].date()),
                       missing=[str(d.date()) for d in Fd.index[pos[k] + 1:pos[k + 1]]])
        y, F = g.daily_excess_one(e)
        info[e[:-3]] = dict(first=str(s.index[0].date()), last=str(s.index[-1].date()), n_own=n_own,
                            n_kept=int(len(y)), n_gaps=int(len(gap)), example=ex_)
    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    yy = np.array([1.0, 0.0])
    for j, (k, c) in enumerate([('MTUM', MainBlue), ('QUAL', Forest)]):
        d = B6[k]
        ax.errorbar(100 * d['alpha'], yy[j] + 0.12, xerr=1.96 * 100 * d['se_nw'], fmt='o', color=c, capsize=3, lw=0.9,
                    label=f'{k}: Newey-West 95% interval' )
        lo, hi = d['boot_ci']
        ax.errorbar(100 * d['alpha'], yy[j] - 0.12, xerr=[[100 * (d['alpha'] - lo)], [100 * (hi - d['alpha'])]],
                    fmt='s', color=Amber if k == 'MTUM' else Purple, capsize=3, lw=0.9, label=f'{k}: block-bootstrap 95% interval')
    ax.axvline(0, color=g.Gray, lw=0.7, ls=':')
    ax.set_yticks(yy, ['MTUM', 'QUAL'])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel('FF5 + MOM alpha (% a year)')
    _ax_title(ax, 'Daily six-factor alphas of two factor ETFs')
    _ax_legend(ax, ncol=2)
    plt.tight_layout()
    _save('ch3_sem_b6_alpha')
    return info


def b7_details_chart():
    """B7: alfa FF3 pentru 25 de portofolii (harta 5 x 5) si valorile p sortate fata de praguri."""
    import matplotlib.pyplot as plt
    F = factors('M')
    P = french('p25', 'M').loc['1963-07-31':g.END]
    Fx = F.loc[P.index]
    ex = P.sub(Fx['RF'], axis=0)
    X = Fx[g.FF3].values
    al, tt, pp = [], [], []
    for c in ex.columns:
        b, se, t, _, _ = ols_hac(ex[c].values, X)
        al.append(b[0] * 12)
        tt.append(t[0])
        pp.append(2 * (1 - stats.norm.cdf(abs(t[0]))))
    A = np.array(al).reshape(5, 5)
    Tm = np.array(tt).reshape(5, 5)
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={'width_ratios': [1, 1.25]})
    ax = axes[0]
    vmax = np.abs(100 * A).max()
    im = ax.imshow(100 * A, cmap='RdBu', vmin=-1.8 * vmax, vmax=1.8 * vmax)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f'{100 * A[i, j]:.1f}\n({Tm[i, j]:.1f})', ha='center', va='center', fontsize=7.5, color='black')
    ax.set_xticks(range(5), ['Low', '2', '3', '4', 'High'], fontsize=8.5)
    ax.set_yticks(range(5), ['Small', '2', '3', '4', 'Big'], fontsize=8.5)
    ax.set_xlabel('Book-to-market quintile')
    ax.set_ylabel('Size quintile')
    _ax_title(ax, 'FF3 alpha, % a year (NW t)')
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.ax.tick_params(labelsize=8)
    ax = axes[1]
    _pvalue_panel(ax, pp, '25 sorted p-values')
    ax.set_ylim(1e-8, 1.5)
    _ax_legend(ax, ncol=2, fontsize=8.5)
    plt.tight_layout()
    _save('ch3_sem_b7_alphas')
    ps = np.sort(pp)
    return dict(alpha=np.round(100 * A, 2).tolist(), t=np.round(Tm, 2).tolist(), p_sorted=[float(x) for x in ps[:8]],
                thresholds_rank=[dict(j=k + 1, bonf=0.05 / 25, holm=0.05 / (25 - k), bh=0.05 * (k + 1) / 25) for k in range(6)])


def b8_chart(B8):
    """B8: scree BVB vs sectoare SUA si incarcarile PC1 BVB; BVB pe perioada comuna cu SUA."""
    import matplotlib.pyplot as plt
    names = [s for s in BVB if s != 'H2O']
    p = prices([s + '.RO' for s in names] + ['BET']).loc['2017-06-01':]
    r = log_returns(p)
    r = r[~(r.abs() > g.MAX_ABS_RET).any(axis=1)]
    X = r[[s + '.RO' for s in names]]
    ev_b = np.sort(np.linalg.eigvalsh(np.corrcoef(X.values.T)))[::-1]
    vals_us, vecs_us, r_us, _ = g.pca_sectors()
    a0 = r_us.index[0]
    Xc = X.loc[a0:]
    ev_c = np.sort(np.linalg.eigvalsh(np.corrcoef(Xc.values.T)))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    ax = axes[0]
    k = np.arange(1, 11)
    ax.plot(k, ev_b / ev_b.sum(), color=MainBlue, marker='o', ms=3, label=f'BVB, 10 stocks, from {r.index[0]:%b %Y}')
    ax.plot(k, ev_c / ev_c.sum(), color=TEAL, marker='^', ms=3, ls='--', label=f'BVB, from {a0:%b %Y} (US period)')
    ax.plot(k, (vals_us / vals_us.sum())[:10], color=IDAred, marker='s', ms=3, label=f'US, 11 sector ETFs, from {a0:%b %Y}')
    ax.set_xticks(k)
    ax.set_xlabel('Component')
    ax.set_ylabel('Share of variance')
    _ax_title(ax, 'Scree plots')
    ax = axes[1]
    ld = pd.Series(B8['load_pc1']).sort_values()
    ax.barh(np.arange(len(ld)), ld.values, color=MainBlue)
    ax.set_yticks(np.arange(len(ld)), ld.index, fontsize=8.5)
    ax.set_xlabel('PC1 loading')
    _ax_title(ax, f'BVB PC1 (corr. with BET {B8["corr_pc1_bet"]:.3f})')
    plt.tight_layout()
    _fig_legend(fig, ncol=2)
    _save('ch3_sem_b8_bvb_pca')
    return dict(share1_common=float(ev_c[0] / ev_c.sum()), T_common=int(len(Xc)), share1_us=float(vals_us[0] / vals_us.sum()))


def b9_chart(B9):
    """B9: media efectiva vs ajustata FF3 pe 55 de active; R^2 OLS/GLS cu intervale bootstrap."""
    import matplotlib.pyplot as plt
    F = factors('M')
    P25 = french('p25', 'M').loc['1963-07-31':g.END]
    I30 = french('ind30', 'M').loc['1963-07-31':g.END]
    Fx = F.loc[P25.index]
    P = pd.concat([P25, I30.add_prefix('IND_')], axis=1)
    ex = P.sub(Fx['RF'], axis=0).values
    T, N = ex.shape
    mu = ex.mean(0)
    Z = np.column_stack([np.ones(T), Fx[g.FF3].values])
    Bm = np.linalg.lstsq(Z, ex, rcond=None)[0][1:].T
    X = np.column_stack([np.ones(N), Bm])
    fit = X @ np.linalg.lstsq(X, mu, rcond=None)[0]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={'width_ratios': [1, 1.3]})
    ax = axes[0]
    ax.scatter(1200 * fit[:25], 1200 * mu[:25], s=14, color=MainBlue, label='25 size x B/M')
    ax.scatter(1200 * fit[25:], 1200 * mu[25:], s=14, color=IDAred, marker='^', label='30 industries')
    lo, hi = 1200 * min(fit.min(), mu.min()), 1200 * max(fit.max(), mu.max())
    ax.plot([lo, hi], [lo, hi], color=g.Gray, ls=':', lw=0.8)
    ax.set_xlabel('FF3 fitted mean (% a year, OLS pass 2)')
    ax.set_ylabel('Actual mean (% a year)')
    _ax_title(ax, 'FF3 on 55 assets')
    ax = axes[1]
    labs = ['CAPM | 25', 'FF3 | 25', 'FF5 | 25', 'CAPM | 25+30', 'FF3 | 25+30', 'FF5 | 25+30']
    x = np.arange(len(labs))
    for off, key, ci, c, nm in [(-0.15, 'r2_ols', 'ci_ols', MainBlue, 'OLS'), (0.15, 'r2_gls', 'ci_gls', Forest, 'GLS')]:
        v = np.array([B9[l][key] for l in labs])
        lo_ = np.array([B9[l][ci][0] for l in labs])
        hi_ = np.array([B9[l][ci][1] for l in labs])
        ax.errorbar(x + off, v, yerr=[v - lo_, hi_ - v], fmt='o', color=c, capsize=2, lw=0.9, label=f'{nm} $R^2$, 95% bootstrap interval')
    ax.set_xticks(x, [l.replace(' | ', '\n') for l in labs], fontsize=8.5)
    ax.set_ylabel('Cross-sectional $R^2$')
    _ax_title(ax, 'Adding industries lowers the fit')
    plt.tight_layout()
    _fig_legend(fig, ncol=2)
    _save('ch3_sem_b9_lns')
    return dict(N=N)


def b10_chart(B10):
    """B10: raport Sharpe maxim pe modele si perioade; t de spanning pentru fiecare factor."""
    import matplotlib.pyplot as plt
    models = ['CAPM', 'FF3', 'Carhart', 'FF5', 'FF5+MOM']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    ax = axes[0]
    x = np.arange(len(models))
    for off, per, c in [(-0.2, '1963-2026', MainBlue), (0.2, '2000-2026', Amber)]:
        ax.bar(x + off, [B10[per]['sr_ann'][m] for m in models], 0.4, color=c, label=per)
    ax.set_xticks(x, models, fontsize=8.5)
    ax.set_ylabel('Maximum annual Sharpe ratio')
    _ax_title(ax, 'Sharpe ratio of each model\'s factors')
    ax = axes[1]
    fac = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    x = np.arange(len(fac))
    for off, per, c in [(-0.2, '1963-2026', MainBlue), (0.2, '2000-2026', Amber)]:
        ax.bar(x + off, [B10[per]['spanning'][f]['t'] for f in fac], 0.4, color=c, label='_' + per)
    ax.axhline(1.96, color=IDAred, ls='--', lw=0.8, label='|t| = 1.96')
    ax.axhline(-1.96, color=IDAred, ls='--', lw=0.8)
    ax.axhline(0, color=g.Gray, lw=0.5)
    ax.set_xticks(x, fac, fontsize=8.5)
    ax.set_ylabel('Newey-West t of spanning alpha')
    _ax_title(ax, 'Each factor on the other five')
    plt.tight_layout()
    _fig_legend(fig, ncol=3)
    _save('ch3_sem_b10_sharpe')
    return {}


def b11_chart():
    """B11: distributia bootstrap a GRS sub H0 fata de F(25, 731); graficul Q-Q al unui reziduu."""
    import matplotlib.pyplot as plt
    boot, stat, E = b11_grs_robust(draws=True)
    T, N = E.shape
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.35, 1]})
    ax = axes[0]
    ax.hist(boot, bins=50, density=True, color=Amber, alpha=0.8, label='Residual bootstrap under H0 (2000 draws)')
    xs = np.linspace(0, max(4.5, boot.max()), 400)
    ax.plot(xs, stats.f.pdf(xs, N, T - N - 1), color=Forest, label=f'F({N}, {T - N - 1})')
    ax.axvline(stats.f.ppf(0.95, N, T - N - 1), color=Forest, ls='--', lw=0.9, label='F 5% critical value')
    ax.axvline(np.percentile(boot, 95), color=Orange, ls='-.', lw=0.9, label='Bootstrap 5% critical value')
    ax.axvline(stat, color=MainBlue, lw=1.4, label=f'Observed GRS = {stat:.2f}')
    ax.set_xlabel('GRS statistic')
    ax.set_ylabel('Density')
    _ax_title(ax, 'Null distribution of GRS')
    ax = axes[1]
    kurt = stats.kurtosis(E, axis=0, fisher=False)
    i = int(np.argmax(kurt))
    z = np.sort((E[:, i] - E[:, i].mean()) / E[:, i].std())
    q = stats.norm.ppf((np.arange(1, T + 1) - 0.5) / T)
    ax.scatter(q, z, s=4, color=MainBlue, label=f'Most leptokurtic residual (kurtosis {kurt[i]:.1f})')
    ax.plot([-3.5, 3.5], [-3.5, 3.5], color=g.Gray, ls=':', lw=0.8)
    ax.set_xlabel('Normal quantile')
    ax.set_ylabel('Standardised residual')
    _ax_title(ax, 'Q-Q plot')
    plt.tight_layout()
    _fig_legend(fig, ncol=2)
    _save('ch3_sem_b11_boot')
    return dict(max_kurt=float(kurt.max()), max_kurt_port=int(i), boot_max=float(boot.max()))


def a2_chart(A2):
    """A2: castigul de raport Sharpe patrat si GRS fata de F(25, 731)."""
    import matplotlib.pyplot as plt
    T, N = A2['T'], A2['N']
    s2f, s2a = A2['sr_f_m'] ** 2, A2['sr_all_m'] ** 2
    exp_gain = N * (1 + s2f) / (T - N - 3)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax = axes[0]
    ax.bar([0, 1, 2], [s2f, s2a, s2f + exp_gain], color=[Forest, MainBlue, Amber], width=0.6)
    ax.set_xticks([0, 1, 2], ['Market', 'Market + 25\nportfolios', 'Expected\nunder H0'], fontsize=8.5)
    for x_, v in zip([0, 1, 2], [s2f, s2a, s2f + exp_gain]):
        ax.annotate(f'{v:.3f}', (x_, v), xytext=(0, 2), textcoords='offset points', ha='center', fontsize=8.5, color='black')
    ax.set_ylabel('Monthly squared Sharpe ratio')
    _ax_title(ax, 'Sharpe-ratio gain from the test assets')
    ax = axes[1]
    xs = np.linspace(0, 5, 500)
    d = stats.f.pdf(xs, N, T - N - 1)
    crit = stats.f.ppf(0.95, N, T - N - 1)
    ax.plot(xs, d, color=Forest, label=f'F({N}, {T - N - 1})')
    ax.fill_between(xs[xs >= crit], d[xs >= crit], color=IDAred, alpha=0.35, label=f'5% region (> {crit:.2f})')
    ax.axvline(A2['grs'], color=MainBlue, lw=1.4, label=f'W = {A2["grs"]:.2f}')
    ax.set_xlabel('GRS statistic W')
    _ax_title(ax, 'Decision at 5%')
    _ax_legend(ax, ncol=3)
    plt.tight_layout()
    _save('ch3_sem_a2_grs')
    return dict(exp_gain=exp_gain, crit=crit)


def a4_chart():
    """A4: betele sectoarelor 1999-2012 vs 2013-2026, dreapta ajustata si dreapta implicata de A3."""
    import matplotlib.pyplot as plt
    b1, b2, se1, halves = g.beta_split()
    pm, pv = g.vasicek_prior(b1, se1)
    fit = stats.linregress(b1, b2)
    w = pv / (pv + (se1 ** 2).mean())
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    ax.scatter(b1, b2, s=20, color=MainBlue, zorder=3, label='Sector ETFs')
    _label_points(ax, list(b1.index), b1.values, b2.values)
    xs = np.linspace(0.3, 1.6, 10)
    ax.plot(xs, xs, color=g.Gray, ls=':', lw=0.8, label='Identity')
    ax.plot(xs, fit.intercept + fit.slope * xs, color=IDAred, label=f'Fitted: later beta = {fit.intercept:.3f} + {fit.slope:.3f} x earlier beta')
    ax.plot(xs, (1 - w) * pm + w * xs, color=Forest, ls='--', label=f'Implied by A3: later beta = {(1 - w) * pm:.3f} + {w:.3f} x earlier beta')
    ax.set_xlabel('Beta, 1999-2012')
    ax.set_ylabel('Beta, 2013-2026')
    _ax_title(ax, 'Regression to the mean exceeds sampling noise')
    _ax_legend(ax, ncol=2)
    plt.tight_layout()
    _save('ch3_sem_a4_blume')
    return dict(betas1=b1.round(3).to_dict(), betas2=b2.round(3).to_dict(), se1=se1.round(3).to_dict())


def a6_chart(A6):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    labs = ['Fama-MacBeth t-test\nof $\\lambda_g = 0$', 'Shanken t-test\nof $\\lambda_g = 0$', 'First-pass Wald test\nof $\\beta_g = 0$']
    v = [A6['rej_fm'], A6['rej_shanken'], A6['rej_wald_beta']]
    ax.bar(range(3), v, color=[IDAred, Amber, Forest], width=0.55)
    for x_, y_ in zip(range(3), v):
        ax.annotate(f'{100 * y_:.1f}%', (x_, y_), xytext=(0, 2), textcoords='offset points', ha='center', fontsize=7.5, color='black')
    ax.axhline(0.05, color=MainBlue, ls='--', lw=0.9, label='Nominal level 5%')
    ax.set_xticks(range(3), labs, fontsize=8.5)
    ax.set_ylabel('Rejection rate')
    _ax_title(ax, f'Useless factor added to the CAPM, {A6["reps"]} replications')
    _ax_legend(ax, ncol=1)
    plt.tight_layout()
    _save('ch3_sem_a6_useless')
    return {}


def a7_chart(A7):
    """A7: factorul de atenuare Var(beta)/(Var(beta) + s2/(T s2_f)) in functie de T; punctele observate."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    Ts = np.arange(12, 1001)
    for k, c in [('25 size x B/M', MainBlue), ('9 sector ETFs', IDAred)]:
        d = A7[k]
        noise_T = d['noise'] * d['T']                          # s2_eps / var_ML(f), independent de T
        ax.plot(Ts, d['var_beta'] / (d['var_beta'] + noise_T / Ts), color=c, label=f'{k}')
        ax.plot([d['T']], [d['attenuation']], 'o', color=c, ms=6)
        ax.annotate(f"T = {d['T']}: {d['attenuation']:.3f}", (d['T'], d['attenuation']), xytext=(-20, 8),
                    textcoords='offset points', fontsize=8.5, color='black')
    ax.set_xlabel('Number of months T')
    ax.set_ylabel('Attenuation factor')
    ax.set_ylim(0.6, 1.01)
    _ax_title(ax, 'Pass-2 slope / realised premium as T grows')
    _ax_legend(ax, ncol=2)
    plt.tight_layout()
    _save('ch3_sem_a7_eiv')
    return {}


def a8_chart(B3, B8):
    """A8: ponderea PC1 pentru corelatie egala rho in functie de N; valorile observate BVB si SUA."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    Ns = np.arange(2, 41)
    for rho, c in [(0.36, MainBlue), (0.5, Forest), (0.63, IDAred)]:
        ax.plot(Ns, rho + (1 - rho) / Ns, color=c, label=rf'$\rho$ = {rho}')
        ax.axhline(rho, color=c, ls=':', lw=0.6)
    ax.plot([10], [B8['share1']], 's', color=MainBlue, ms=6, label=f'BVB: N = 10, share {B8["share1"]:.3f}')
    ax.plot([11], [B3['share1']], '^', color=IDAred, ms=6, label=f'US sectors: N = 11, share {B3["share1"]:.3f}')
    ax.set_xlabel('Number of assets N')
    ax.set_ylabel(r'PC1 share $= \rho + (1 - \rho)/N$')
    _ax_title(ax, r'Equicorrelation: the PC1 share falls towards $\rho$')
    _ax_legend(ax, ncol=3)
    plt.tight_layout()
    _save('ch3_sem_a8_equicorr')
    return {}


def c2_chart(ser):
    """C2: raspunsul AI (semnal cu luna t, randamente log) fata de versiunea corectata, aceleasi luni."""
    import matplotlib.pyplot as plt
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.4, 1]})
    ax = axes[0]
    for k, c, lab in [('corrected', MainBlue, 'Corrected: signal t-12..t-2, simple returns'),
                      ('lookahead', IDAred, 'Look-ahead: signal includes month t')]:
        x = ser[k]
        ax.plot(x.index, (1 + x).cumprod(), color=c, lw=1.0, label=lab)
    import matplotlib.dates as mdates
    ax.set_yscale('log')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_ylabel('Growth of 1 RON (log scale)')
    _ax_title(ax, 'Same months, same stocks')
    ax = axes[1]
    labs = ['Corrected', 'Log\nonly', 'Look-\nahead', 'AI\nanswer']
    keys = ['corrected', 'log', 'lookahead', 'ai_answer']
    v = [12 * ser[k].mean() for k in keys]
    ax.bar(range(4), 100 * np.array(v), color=[MainBlue, Forest, IDAred, Amber], width=0.6)
    for x_, y_ in zip(range(4), v):
        ax.annotate(f'{100 * y_:.1f}%', (x_, 100 * y_), xytext=(0, 2), textcoords='offset points', ha='center', fontsize=8.5, color='black')
    ax.set_xticks(range(4), labs, fontsize=8.5)
    ax.set_ylabel('Annual mean (%)')
    _ax_title(ax, 'Which error does the damage?')
    plt.tight_layout()
    _fig_legend(fig, ncol=1)
    _save('ch3_sem_c2_correction')
    return {k: float(12 * ser[k].mean()) for k in keys}


def seminar_charts(R):
    """Toate graficele seminarului; intoarce valorile folosite pe slide-uri."""
    _style()
    C = {}
    C['setup'] = setup_preview()
    C['A1'] = a1_chart()
    C['A2'] = a2_chart(R['A']['A2'])
    C['A3'] = a3_chart(R['A']['A3'])
    C['A4'] = a4_chart()
    C['A5'] = a5_chart(np.array(R['A']['A5']['p']))
    C['A6'] = a6_chart(R['A']['A6'])
    C['A7'] = a7_chart(R['A']['A7'])
    C['A8'] = a8_chart(R['B3'], R['B8'])
    C['B1'] = b1_chart()
    C['B2'] = b2_details_chart()
    C['B3'] = b3_chart()
    C['B4'] = b4_chart(R['B4'])
    C['B5'] = b5_chart()
    C['B6'] = b6_chart(R['B6'])
    C['B7'] = b7_details_chart()
    C['B8'] = b8_chart(R['B8'])
    C['B9'] = b9_chart(R['B9'])
    C['B10'] = b10_chart(R['B10'])
    C['B11'] = b11_chart()
    return C



def to_py(o):
    return g.to_py(o)


if __name__ == '__main__':
    R = {'A': part_a(), 'B1': b1_xlk(), 'B2': b2_grs(), 'B3': b3_pca(), 'B4': b4_bvb(), 'B5': b5_fama_macbeth(),
         'B6': b6_etf_bootstrap(), 'B7': b7_multiple_testing(), 'B8': b8_pca_bvb(), 'B9': b9_lns(),
         'B10': b10_model_comparison(), 'B11': b11_grs_robust()}
    R['C'], _, c2_series = part_c(return_series=True)
    R['charts'] = seminar_charts(R)
    R['charts']['C2'] = c2_chart(c2_series)
    with open(os.path.join(HERE, 'sem3_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print(json.dumps(to_py(R), indent=1, default=str))

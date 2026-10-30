"""
vol_managed_case.py -- Chapter 4, second case study: volatility-managed portfolios
=================================================================================
DeMiguel, Martin-Utrera & Uppal (2024), A multifactor perspective on volatility-managed portfolios,
Journal of Finance 79(6), 3859-3891, https://doi.org/10.1111/jofi.13395

Course replication on the chapter's four universes (US sectors, multi-asset, combined, BVB):
  * "factors" = the excess returns of the ETFs (zero-cost positions financed at the T-bill rate);
    BVB: returns in RON with Rf = 0, as in the chapter;
  * single-asset volatility management (paper eq. 1, Table I panel C): the mean-variance combination
    (gamma = 5, weights >= 0) of r_k and r_k / sigma^2_k,t, sigma^2_k,t = variance of the daily returns of
    asset k in month t;
  * UMV: max a'mu - gamma/2 a'Sigma a, a >= 0 (paper problem 6 with b = 0);
  * CFW (Moreira & Muir 2017): mean-variance combination (weights >= 0) of the UMV return and the UMV return
    scaled by the inverse of its past-month variance (daily returns of the current UMV weights);
  * CMV (paper eqs. 3-6): theta_k,t = a_k + b_k / sigma_t, sigma_t = realised volatility of the market in month t
    (SPY for the US universes, BET-TR for BVB), (a, b) >= 0;
  * expanding window; first window = the chapter's window (60 months US, 36 months BVB), so the out-of-sample
    periods are those of the chapter's backtest; optimised ignoring costs (paper Table III, columns 1-3);
  * costs: turnover at the asset level (trades netted across factors, the paper's "trading diversification"),
    net return = r - c TO, as in the chapter;
  * liquidation rule of the chapter: a total monthly return <= -100% ends the strategy;
  * tests: one-sided stationary bootstrap of the paper (footnote 15: Politis-Romano, mean block 5, 10,000 draws,
    p = share of draws with SR difference <= 0) and the chapter's two-sided HAC test (Ledoit & Wolf 2008).
Output: vol_managed_case.json, charts/ch4_vmp.pdf/.png
Modelling Financial Markets - Daniel Traian PELE
"""
import os
import sys
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_all_charts as g  # noqa: E402  (chart style, data, sharpe, tests of the chapter)
from mfm_data import prices, BVB  # noqa: E402

GAMMA = 5.0          # risk aversion (paper, Table I)
COST_BP = 10         # cost per unit of turnover (bp), as in the chapter's tables
NBOOT = 10000        # bootstrap draws (paper, footnote 15)
SB_BLOCK = 5         # mean block of the stationary bootstrap (paper, footnote 15)
SINGLE_FAMILY = ('Sectors', 'Multi-asset', 'BVB')   # one test per asset in the multiple-testing family
MV_POS_FAILS = []   # KKT residuals of the optimisations that did not converge (empty = all converged)
VCOL = {'UMV': g.MainBlue, 'CFW': g.Forest, 'CMV': g.IDAred, 'unmanaged': g.MainBlue, 'managed': g.IDAred}


# -----------------------------------------------------------------------------------------------------------------
# data: monthly (excess) returns and daily realised variances
# -----------------------------------------------------------------------------------------------------------------
def us_universe(syms):
    R, Rex, rf = g.us_monthly(syms)
    d = prices([s + '.US' for s in syms]).pct_change().dropna()
    d.columns = syms
    m = prices(['SPY.US']).pct_change().dropna()['SPY.US']
    return R, Rex, rf, d, m


def bvb_universe():
    mth, _ = g.bvb_monthly()
    R = mth[BVB]
    cols = [s + '.RO' for s in BVB] + ['BETTR.INDX']
    lr = g.log_returns(prices(cols))
    lr = lr.mask(lr.abs() > g.MAX_ABS_RET, 0.0)          # the chapter's filter of unadjusted corporate events
    d = np.exp(lr) - 1
    d.columns = BVB + ['BET-TR']
    rf = pd.Series(0.0, index=R.index)
    return R, R.copy(), rf, d[BVB], d['BET-TR']


def month_stat(d, f):
    """Statistic f of the daily returns inside each calendar month, indexed by month end."""
    return d.groupby(d.index.to_period('M')).agg(f).set_axis(
        d.groupby(d.index.to_period('M')).size().index.to_timestamp('M'))


# -----------------------------------------------------------------------------------------------------------------
# mean-variance with non-negative weights
# -----------------------------------------------------------------------------------------------------------------
def mv_pos(X, gamma=GAMMA):
    """argmax_{eta >= 0} eta'mu - gamma/2 eta'Sigma eta on the sample X (T x K)."""
    mu = X.mean(0)
    S = np.cov(X.T) if X.shape[1] > 1 else np.atleast_2d(X.var(ddof=1))
    K = len(mu)
    f = lambda e: -(e @ mu - gamma / 2 * e @ S @ e)
    gr = lambda e: -(mu - gamma * S @ e)
    x0 = np.full(K, 0.0)
    r = minimize(f, x0, jac=gr, method='L-BFGS-B', bounds=[(0, None)] * K,
                 options=dict(maxiter=5000, ftol=1e-14, gtol=1e-10))
    # convergence check: the KKT conditions of the bound-constrained problem (gradient of the objective ~ 0 where
    # eta > 0, >= 0 where eta = 0). L-BFGS-B often stops with an ABNORMAL line search at the optimum (ftol 1e-14),
    # so the KKT residual, not r.success, decides; a failure is reported and counted, the solution is kept.
    gk = gr(r.x)
    scale = max(1.0, float(np.abs(mu).max()))
    kkt = max(float(np.abs(gk[r.x > 1e-10]).max(initial=0.0)), float(-gk[r.x <= 1e-10].min(initial=0.0)))
    if kkt > 1e-6 * scale:
        print(f'   warning: mv_pos did not converge (KKT residual {kkt:.2e}, scale {scale:.1f}, {r.message})',
              file=sys.stderr)
        MV_POS_FAILS.append(dict(kkt=kkt, scale=scale, x=r.x.tolist(), msg=str(r.message)))
    return r.x


# -----------------------------------------------------------------------------------------------------------------
# out-of-sample strategies
# -----------------------------------------------------------------------------------------------------------------
def run_universe(R, Rex, rf, d, m, window):
    idx = Rex.index
    vk_all = month_stat(d, lambda x: x.var(ddof=1))                    # sigma^2_k,t, every month of daily data
    sm_all = month_stat(m, lambda x: x.std(ddof=1))                    # sigma_t (market)
    var_k = vk_all.reindex(idx)
    sig_m = sm_all.reindex(idx)
    X = Rex.values
    T, K = X.shape
    inv_m = 1 / sig_m.values
    # lagged conditioning variables: row t uses month t-1 (the month before the first return included)
    inv_m_lag = 1 / sm_all.shift(1).reindex(idx).values
    var_lag = vk_all.shift(1).reindex(idx).values
    first = max(window, int(np.argmax(~np.isnan(inv_m_lag) & ~np.isnan(var_lag).any(1))) + window)
    pos = {s: [] for s in ['UMV', 'CFW', 'CMV']}
    single = {c: [] for c in Rex.columns}
    out_idx = idx[first:]
    for t in range(first, T):
        lo = int(np.argmax(~np.isnan(inv_m_lag[:t]) & ~np.isnan(var_lag[:t]).any(1)))
        Xw, im, vl = X[lo:t], inv_m_lag[lo:t], var_lag[lo:t]
        # UMV
        a = mv_pos(Xw)
        pos['UMV'].append(a)
        # CMV: extended returns [r, r / sigma_m]
        eta = mv_pos(np.hstack([Xw, Xw * im[:, None]]))
        pos['CMV'].append(eta[:K] + eta[K:] * inv_m[t - 1])
        # CFW: UMV return and its managed version (variance of the daily UMV returns in the previous month)
        du = pd.Series(d.values @ a, index=d.index)
        vu_all = month_stat(du, lambda x: x.var(ddof=1))
        vu = vu_all.reindex(idx).values
        vu_lag = vu_all.shift(1).reindex(idx).values
        ru = Xw @ a
        ok = ~np.isnan(vu_lag[lo:t])
        ab = mv_pos(np.column_stack([ru[ok], ru[ok] / vu_lag[lo:t][ok]]))
        pos['CFW'].append(a * (ab[0] + ab[1] / vu[t - 1]))
        # single assets: [r_k, r_k / sigma^2_k]
        for k, c in enumerate(Rex.columns):
            e = mv_pos(np.column_stack([Xw[:, k], Xw[:, k] / vl[:, k]]))
            single[c].append(X[t, k] * (e[0] + e[1] / var_k.values[t - 1, k]))
    rets, tos, lev = {}, {}, {}
    Rv = R.values
    for s, P in pos.items():
        P = np.array(P)
        r = (P * X[first:]).sum(1)
        tot = rf.values[first:] + r
        # turnover at the asset level: positions drift with total returns, wealth with the total portfolio return
        drift = P[:-1] * (1 + Rv[first:-1]) / (1 + tot[:-1, None])
        to = np.r_[np.nan, np.abs(P[1:] - drift).sum(1)]
        rets[s] = pd.Series(r, index=out_idx)
        tos[s] = pd.Series(to, index=out_idx)
        lev[s] = float(np.abs(P).sum(1).mean())
    ret = pd.DataFrame(rets)
    ret.attrs['rf'] = pd.Series(rf.values[first:], index=out_idx)
    single = pd.DataFrame(single, index=out_idx)
    return ret, pd.DataFrame(tos), lev, single, Rex.iloc[first:], sig_m


# -----------------------------------------------------------------------------------------------------------------
# inference
# -----------------------------------------------------------------------------------------------------------------
def sb_pvalue(r1, r2, B=NBOOT, block=SB_BLOCK, seed=g.SEED):
    """Paper, footnote 15: stationary bootstrap of the pair, one-sided p = share of draws with SR1 - SR2 <= 0."""
    rng = np.random.default_rng(seed)
    r1, r2 = np.asarray(r1, float), np.asarray(r2, float)
    T = len(r1)
    cnt = 0
    for _ in range(B):
        i = g._sb_indices(T, T, block, rng)
        a, b = r1[i], r2[i]
        cnt += (a.mean() / a.std(ddof=1) - b.mean() / b.std(ddof=1)) <= 0
    return cnt / B


def evaluate(ret, to, lev, single, Xoos):
    rf = ret.attrs['rf']
    liq = {s: f'{g.ruin_month(ret, s):%Y-%m}' for s in ret if g.ruin_month(ret, s) is not None}
    rules = [s for s in ret if s not in liq]
    tab = {}
    for s in ret:
        net = ret[s] - COST_BP / 1e4 * to[s].fillna(0)
        tab[s] = dict(mean=ret[s].mean() * 12, vol=ret[s].std() * np.sqrt(12), sharpe=g.sharpe(ret[s]),
                      sharpe_net=g.sharpe(net), turnover=float(to[s].mean()), leverage=lev[s],
                      mdd=g.max_drawdown(ret[s] + rf))
    tests = {}
    for s in ['CMV', 'CFW']:
        if s in rules and 'UMV' in rules:
            net = lambda q: ret[q] - COST_BP / 1e4 * to[q].fillna(0)
            dg, se, ph = g.sr_diff_hac(ret[s], ret['UMV'])
            dn, sen, phn = g.sr_diff_hac(net(s), net('UMV'))
            # break-even cost: Sharpe(s, c) = Sharpe(UMV, c)
            cs = np.arange(0, 201, 0.5)
            gap = [g.sharpe(ret[s] - c / 1e4 * to[s].fillna(0)) - g.sharpe(ret['UMV'] - c / 1e4 * to['UMV'].fillna(0))
                   for c in cs]
            be = next((float(c) for c, x in zip(cs, gap) if x <= 0), None)
            tests[s] = dict(diff=dg, se_hac=se, p_hac=ph, p_sb=sb_pvalue(ret[s], ret['UMV']),
                            diff_net=dn, p_hac_net=phn, p_sb_net=sb_pvalue(net(s), net('UMV')), breakeven_bp=be)
    sing = {}
    for c in single:
        d_, se_, p_ = g.sr_diff_hac(single[c], Xoos[c])
        sing[c] = dict(sr_unmanaged=g.sharpe(Xoos[c]), sr_managed=g.sharpe(single[c]), diff=d_, p_hac=p_,
                       liquidated=bool((single[c] <= -1).any()))
    return dict(table=tab, tests=tests, single=sing, liquidated=liq,
                start=f'{ret.index[0]:%Y-%m}', end=f'{ret.index[-1]:%Y-%m}', T=len(ret))


# -----------------------------------------------------------------------------------------------------------------
# chart
# -----------------------------------------------------------------------------------------------------------------
UNI_LABEL = {'Sectors': 'Sectors', 'Multi-asset': 'Multi-asset', 'Combined': 'Combined', 'BVB': 'BVB (RON, Rf = 0)'}


def fig_vmp(res, single_universe='Multi-asset'):
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.8), gridspec_kw={'width_ratios': [1, 1.15]})
    ax = axes[0]
    sg = res[single_universe]['single']
    names = list(sg)
    x = np.arange(len(names))
    wd = 0.38
    ax.bar(x - wd / 2, [sg[n]['sr_unmanaged'] for n in names], wd, color=VCOL['unmanaged'], label='Unmanaged asset')
    ax.bar(x + wd / 2, [sg[n]['sr_managed'] for n in names], wd, color=VCOL['managed'],
           label=r'Managed: MV mix of $r_k$ and $r_k/\sigma^2_k$ (eq. 1)')
    ax.axhline(0, color=g.Navy, lw=0.5)
    ax.set_xticks(x, names)
    ax.set_ylabel('Out-of-sample Sharpe ratio')
    ax.set_title(f'{single_universe}: one asset at a time', fontsize=9, loc='left')
    g.legend_outside_bottom(ax, ncol=2, y=-0.14)
    ax = axes[1]
    us = list(res)
    x = np.arange(len(us))
    wd = 0.26
    for k, s in enumerate(['UMV', 'CFW', 'CMV']):
        v = [res[u]['table'][s]['sharpe'] if s not in res[u]['liquidated'] else np.nan for u in us]
        ax.bar(x + (k - 1) * wd, v, wd, color=VCOL[s], label=s)
        vn = [res[u]['table'][s]['sharpe_net'] if s not in res[u]['liquidated'] else np.nan for u in us]
        ax.scatter(x + (k - 1) * wd, vn, marker='_', s=90, color=g.Navy, zorder=3,
                   label=f'Net of {COST_BP} bp' if k == 2 else None)
    ax.axhline(0, color=g.Navy, lw=0.5)
    ax.set_xticks(x, [UNI_LABEL[u] for u in us])
    ax.set_ylabel('Out-of-sample Sharpe ratio')
    ax.set_title('All assets together, gamma = 5', fontsize=9, loc='left')
    g.legend_outside_bottom(ax, ncol=4, y=-0.14)
    plt.tight_layout()
    g.save_fig('ch4_vmp')


def compute():
    """Out-of-sample series (raw) and their evaluation (res) for the four universes."""
    res, raw = {}, {}
    for name, syms in g.UNIVERSES.items():
        R, Rex, rf, d, m = us_universe(syms)
        raw[name] = run_universe(R, Rex, rf, d, m, g.WINDOW)
    R, Rex, rf, d, m = bvb_universe()
    raw['BVB'] = run_universe(R, Rex, rf, d, m, 36)
    for name, (ret, to, lev, single, Xoos, sig_m) in raw.items():
        res[name] = evaluate(ret, to, lev, single, Xoos)
    single_holm(res)
    return res, raw


def single_holm(res):
    """Holm (1979) over the family of single-asset tests, each asset once (sectors, multi-asset, BVB: 25 tests; the
    combined universe repeats the US assets and is left out): adjusted HAC p-values p_holm next to p_hac."""
    keys = [(u, c) for u in SINGLE_FAMILY if u in res for c in res[u]['single']]
    adj = g.holm({k: res[k[0]]['single'][k[1]]['p_hac'] for k in keys})
    for u, c in keys:
        res[u]['single'][c]['p_holm'] = float(adj[(u, c)])
    raw = [res[u]['single'][c]['p_hac'] for u, c in keys]
    return dict(m=len(keys), n_raw_05=int(sum(p < 0.05 for p in raw)),
                n_holm_05=int(sum(adj[k] < 0.05 for k in keys)), min_holm=float(min(adj.values())))


def main():
    res, raw = compute()
    for name in raw:
        print(name, res[name]['start'], res[name]['end'], res[name]['T'], res[name]['liquidated'])
        print(pd.DataFrame(res[name]['table']).T.round(3))
        print(pd.DataFrame(res[name]['tests']).T.round(3))
        print(pd.DataFrame(res[name]['single']).T.round(3))
    fig_vmp(res)
    with open(os.path.join(HERE, 'vol_managed_case.json'), 'w') as f:
        json.dump(g.to_py(dict(gamma=GAMMA, cost_bp=COST_BP, nboot=NBOOT, sb_block=SB_BLOCK, results=res,
                               single_family=single_holm(res), mv_pos_fails=len(MV_POS_FAILS))), f,
                  indent=1, default=str)
    return res, raw


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    main()

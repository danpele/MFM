"""
factor_momentum_case.py -- Chapter 3, second case study: factor momentum (Ehsani & Linnainmaa, 2022)
====================================================================================================
Question (Ehsani & Linnainmaa, 2022, Journal of Finance 77(3), 1877-1919): are factor returns autocorrelated, and
does momentum in factors explain the momentum factor of individual stocks?

Data: seven factors of the Kenneth French Data Library, monthly, July 1963 - July 2026 (the chapter's sample):
Mkt-RF, SMB, HML, RMW, CMA (five-factor model), ST_Rev (short-term reversal) and LT_Rev (long-term reversal);
MOM (UMD, stock momentum) is kept out of the set and used as the series to explain.

  * signal of factor i in month t: its compounded return over months t-12 ... t-1 (lookback L = 12);
  * conditional means: mean return in month t after a positive and after a negative prior year, per factor and
    pooled over all factor-months (t-statistic of the difference clustered by month);
  * time-series factor momentum (TSFM): each month long the factors with a positive prior-year return and short the
    others, equal weights: TSFM_t = (1/N) sum_i sign(signal_i,t) r_i,t;
  * spanning regressions with Newey-West errors: MOM on FF5 and on FF5 + TSFM; TSFM on FF5 + MOM;
  * maximum drawdown of TSFM and MOM.
Output: ch3_factor_momentum.json, charts/ch3_factor_momentum.pdf/.png
Modelling Financial Markets - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import mfm_data as md  # noqa: E402

FACS = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'ST_Rev', 'LT_Rev']
FF5 = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
END = '2026-07-31'          # last month of the chapter's monthly sample
LOOKBACK = 12


def load():
    """Monthly factors (decimals) on the common months, July 1963 - July 2026."""
    F = pd.concat([md.factors('M'), md.french('strev', 'M'), md.french('ltrev', 'M')], axis=1).dropna()
    return F.loc[:END]


def signals(R, L=LOOKBACK):
    """Compounded return of every factor over months t-L ... t-1 (NaN in the first L months)."""
    return (1 + R).rolling(L).apply(np.prod, raw=True).shift(1) - 1


def factor_momentum(F, L=LOOKBACK):
    R = F[FACS]
    S = signals(R, L)
    ok = S.notna().all(axis=1)
    R, S = R[ok], S[ok]
    up, dn = R.where(S > 0), R.where(S <= 0)
    tsfm = (np.sign(S).replace(0, -1) * R).mean(axis=1).rename('TSFM')
    # pooled difference, standard errors clustered by month
    y = R.values.ravel() * 100
    d = (S.values.ravel() > 0).astype(float)
    g = np.repeat(np.arange(len(R)), len(FACS))
    X = np.column_stack([np.ones_like(d), d])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    Sg = np.zeros((2, 2))
    for k in range(len(R)):
        m = g == k
        s = X[m].T @ e[m]
        Sg += np.outer(s, s)
    se = np.sqrt(np.diag(XtXi @ Sg @ XtXi))
    return R, S, up, dn, tsfm, dict(pooled_dn=b[0], pooled_up=b[0] + b[1], diff=b[1], t_diff=b[1] / se[1],
                                    share_up=float((S > 0).values.mean()))


def max_dd(r):
    w = (1 + r).cumprod()
    dd = w / w.cummax() - 1
    return float(dd.min()), str(dd.idxmin().date())[:7]


def analyse(F, L=LOOKBACK):
    R, S, up, dn, tsfm, pooled = factor_momentum(F, L)
    mom = F.loc[R.index, 'MOM']
    ff5 = F.loc[R.index, FF5].values * 100
    out = dict(start=str(R.index[0].date())[:7], end=str(R.index[-1].date())[:7], T=int(len(R)), L=L, factors=FACS)
    out['mean_up'] = (up.mean() * 100).to_dict()
    out['mean_dn'] = (dn.mean() * 100).to_dict()
    out['n_up'] = up.notna().sum().astype(int).to_dict()
    out['pooled'] = pooled
    b, se, t, _, _ = md.ols_hac(tsfm.values * 100, np.zeros((len(tsfm), 0)))
    out['tsfm'] = dict(mean=b[0], t=t[0], sr=float(tsfm.mean() / tsfm.std() * np.sqrt(12)), sd=float(tsfm.std() * 100),
                       final=float((1 + tsfm).prod()))
    b, se, t, _, _ = md.ols_hac(mom.values * 100, np.zeros((len(mom), 0)))
    out['mom'] = dict(mean=b[0], t=t[0], sr=float(mom.mean() / mom.std() * np.sqrt(12)), sd=float(mom.std() * 100),
                      final=float((1 + mom).prod()))
    out['tsfm']['mdd'], out['tsfm']['mdd_month'] = max_dd(tsfm)
    out['mom']['mdd'], out['mom']['mdd_month'] = max_dd(mom)
    out['corr'] = float(np.corrcoef(tsfm, mom)[0, 1])
    b, se, t, _, r2 = md.ols_hac(mom.values * 100, ff5)
    out['mom_ff5'] = dict(alpha=b[0], t_alpha=t[0], r2=r2)
    b, se, t, _, r2 = md.ols_hac(mom.values * 100, np.column_stack([ff5, tsfm.values * 100]))
    out['mom_ff5_tsfm'] = dict(alpha=b[0], t_alpha=t[0], b_tsfm=b[-1], t_tsfm=t[-1], r2=r2)
    b, se, t, _, r2 = md.ols_hac(tsfm.values * 100, np.column_stack([ff5, mom.values * 100]))
    out['tsfm_ff5_mom'] = dict(alpha=b[0], t_alpha=t[0], b_mom=b[-1], t_mom=t[-1], r2=r2)
    out['alpha_drop_pct'] = 100 * (1 - out['mom_ff5_tsfm']['alpha'] / out['mom_ff5']['alpha'])
    return out, tsfm, mom


def fig_factor_momentum(F, res, tsfm, mom):
    import matplotlib.pyplot as plt
    import slide_fit  # noqa: F401  charts drawn at the size they have on the slides
    import generate_all_charts as g
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axes[0]
    names = FACS + ['Average factor']
    dn = [res['mean_dn'][c] for c in FACS] + [res['pooled']['pooled_dn']]
    up = [res['mean_up'][c] for c in FACS] + [res['pooled']['pooled_up']]
    x = np.arange(len(names))
    ax.bar(x - 0.19, dn, 0.38, color=g.IDAred, label='After a negative prior year')
    ax.bar(x + 0.19, up, 0.38, color=g.Forest, label='After a positive prior year')
    ax.axhline(0, color=g.Navy, lw=0.6)
    ax.axvline(len(FACS) - 0.5, color=g.Navy, lw=0.5, ls=':')
    ax.set_xticks(x, names, fontsize=7, rotation=30, ha='right')
    ax.set_ylabel('Mean return, % a month')
    ax.set_title('Factor returns after a positive or negative prior year', fontsize=9, loc='left')
    ax = axes[1]
    ax.plot(tsfm.index, (1 + tsfm).cumprod(), color=g.MainBlue, lw=1.0, label='Factor momentum (TSFM)')
    ax.plot(mom.index, (1 + mom).cumprod(), color=g.Orange, lw=1.0, label='Stock momentum (MOM)')
    ax.set_yscale('log')
    ax.set_ylabel('Growth of 1 (log scale)')
    ax.set_title(f'Growth of 1, {res["start"]} to {res["end"]}', fontsize=9, loc='left')
    plt.tight_layout()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    ymin = min(a.get_tightbbox(r).transformed(fig.transFigure.inverted()).y0 for a in fig.axes)
    h = axes[0].get_legend_handles_labels()
    h2 = axes[1].get_legend_handles_labels()
    fig.legend(h[0] + h2[0], h[1] + h2[1], loc='upper center', bbox_to_anchor=(0.5, ymin - 0.01), ncol=4, frameon=False)
    g.save_fig('ch3_factor_momentum')


if __name__ == '__main__':
    F = load()
    res, tsfm, mom = analyse(F)
    print(json.dumps(res, indent=1, default=float))
    with open(os.path.join(HERE, 'ch3_factor_momentum.json'), 'w') as f:
        json.dump(res, f, indent=1, default=float)
    if '--no-chart' not in sys.argv:
        fig_factor_momentum(F, res, tsfm, mom)

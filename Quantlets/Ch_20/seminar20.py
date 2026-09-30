"""
seminar20.py -- cifrele Seminarului 20 (signaturi si volatilitate realizata pe VOLARE)
=====================================================================================
Partea A: exemple numerice pentru derivari (signaturi pas cu pas, Chen, aria Levy, HAR ca AR(22), QLIKE, ponderi).
Partea B: JPM si ES pe VOLARE -- aria Levy ca predictor, familia HAR cu erori HAC, Sig-LK vs log-HAR cu DM, GW si
          bootstrap, corectii pentru testare multipla pe cele 50 de active.
Partea C: analiza de referinta pentru tema deschisa -- un nucleu care vede nivelul volatilitatii (punct de baza).
Iesire: sem20_results.json (folosit de build_seminar20.py) si graficele ch20_sem_*.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sigvol as S                    # noqa: E402
from generate_all_charts import (save_fig, legend_outside_bottom, fig_legend_bottom, MainBlue, IDAred, Forest, Orange, Purple,  # noqa: E402
                                 Teal, Gray, COL)

if not os.path.isdir(S.VOLARE_DIR):
    S.VOLARE_DIR = os.path.join(HERE, '..', '..', 'data', 'volare')
RES = {}


def lecture_results():
    """Results of the Lecture 20 case study (DM p-values and tuned kernel temperatures), loaded from the course repository."""
    f = os.path.join(HERE, 'ch20_results.json')
    if os.path.exists(f):
        return json.load(open(f))
    import urllib.request
    url = 'https://raw.githubusercontent.com/danpele/MFM/main/Quantlets/Ch_20/MFM_ch20_case_study/ch20_results.json'
    return json.load(urllib.request.urlopen(url))


# seminar charts sit next to the solution bullets: larger fonts than the lecture charts
BIG = {'font.size': 11, 'axes.labelsize': 11, 'axes.titlesize': 11, 'xtick.labelsize': 10.5,
       'ytick.labelsize': 10.5, 'legend.fontsize': 10.5}


def big(fn):
    def wrapped(*a, **k):
        with plt.rc_context(BIG):
            return fn(*a, **k)
    wrapped.__name__ = fn.__name__
    return wrapped


def ols_hac(y, X, lag):
    """OLS with Newey-West standard errors; X without constant."""
    Z = np.c_[np.ones(len(y)), X]
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    e = y - Z @ b
    T = len(y)
    Zi = np.linalg.inv(Z.T @ Z)
    G = (Z * e[:, None])
    Sg = G.T @ G / T
    for j in range(1, lag + 1):
        C = G[j:].T @ G[:-j] / T
        Sg += (1 - j / (lag + 1)) * (C + C.T)
    V = T * Zi @ Sg @ Zi
    return b, np.sqrt(np.diag(V)), V


# -----------------------------------------------------------------------------
# PART A
# -----------------------------------------------------------------------------
def part_a():
    A = {}
    # A1: time-augmented path of a series y = (0, 2, 3, 3) at t = (0, 1, 2, 3)
    P = np.array([[0, 0], [1, 2], [2, 3], [3, 3]], float)
    s = S.sig_path(P, 2)
    A['a1'] = {'lvl1': s[:2].tolist(), 'lvl2': s[2:].reshape(2, 2).tolist(), 'levy': S.levy_area(P)}
    # A2: path (0,0) -> (2,1) -> (3,-1) -> (4,2) in R^2 (proposed)
    P2 = np.array([[0, 0], [2, 1], [3, -1], [4, 2]], float)
    s2 = S.sig_path(P2, 2)
    A['a2'] = {'lvl1': s2[:2].tolist(), 'lvl2': s2[2:].reshape(2, 2).tolist(), 'levy': S.levy_area(P2)}
    # A3/A4: unit square loop and its translate
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], float)
    A['a4'] = {'levy_square': S.levy_area(sq), 'levy_square_shift': S.levy_area(sq + 5),
               'levy_square_cw': S.levy_area(sq[::-1])}
    # A5: HAR as a restricted AR(22) for log RV of JPM, regressors = arithmetic averages of log RV (daily, 5, 22 days);
    # the benchmark log-HAR of the lecture uses logs of averages of RV and has no exact AR(22) representation
    a = S.load_asset('stocks', 'JPM')
    D = S.build_design(a, 1)
    Xl = S.har_parts(np.log(a.rv.values))
    ok = np.isfinite(Xl).all(1) & np.isfinite(D['ly'])
    b, se, _ = ols_hac(D['ly'][ok], Xl[ok], 5)
    phi = np.r_[b[1] + b[2] / 5 + b[3] / 22, np.repeat(b[2] / 5 + b[3] / 22, 4), np.repeat(b[3] / 22, 17)]
    bl, _, _ = ols_hac(D['ly'][ok], D['X_loghar'][ok], 5)      # logs of averages, for comparison
    A['a5'] = {'b': b.tolist(), 'se': se.tolist(), 'phi1': phi[0], 'phi2': phi[1], 'phi6': phi[5], 'sum': phi.sum(),
               'N': int(ok.sum()), 'b_logavg': bl.tolist(), 'phi_min': float(phi.min())}
    # A7: QLIKE of +/-50% errors
    A['a7'] = {'under': float(S.qlike(1.0, 0.5)), 'over': float(S.qlike(1.0, 1.5)),
               'mse_under': 0.25, 'mse_over': 0.25}
    # A9: kernel weights for distances (0.2, 0.5, 1.0, 2.0), gamma = 1 and gamma = 3
    d = np.array([0.2, 0.5, 1.0, 2.0])
    for g in (1.0, 3.0):
        w = np.exp(-g * d) / np.exp(-g * d).sum()
        A[f'a9_g{int(g)}'] = {'w': w.tolist(), 'ess': float(1 / np.sum(w ** 2))}
    RES['A'] = A
    chart_a1(P)
    chart_a5(phi)
    chart_a7()
    chart_a9(d)


def setup_check():
    """What the setup cell must print: size and first rows of the JPM file."""
    a = S.load_asset('stocks', 'JPM')
    RES['setup'] = {'n': int(len(a)), 'start': str(a.index[0].date()), 'end': str(a.index[-1].date()),
                    'head': [[str(i.date()), float(r.rv), float(r.r)] for i, r in a.head(3).iterrows()],
                    'n_stocks': len(S.symbols('stocks')), 'n_futures': len(S.symbols('futures')),
                    'n_forex': len(S.symbols('forex'))}


@big
def chart_a1(P):
    """A1: the time-augmented path, its chord and the enclosed signed area."""
    fig, ax = plt.subplots(figsize=(4.2, 3.4))
    ax.fill(np.r_[P[:, 0], P[0, 0]], np.r_[P[:, 1], P[0, 1]], color=IDAred, alpha=0.18,
            label='Area between path and chord (2, run clockwise: A = -2)')
    ax.plot(P[:, 0], P[:, 1], color=MainBlue, lw=1.8, marker='o', label='Path X = (t, y)')
    ax.plot([P[0, 0], P[-1, 0]], [P[0, 1], P[-1, 1]], color=Gray, ls='--', lw=1.0, label='Chord from start to end')
    for t_, y_ in P:
        ax.annotate(f'({t_:.0f}, {y_:.0f})', (t_, y_), xytext=(4, -11), textcoords='offset points', fontsize=8,
                    color='black')
    ax.set_xlabel('Time t (channel 1)')
    ax.set_ylabel('y (channel 2)')
    ax.set_xlim(-0.3, 3.5)
    ax.set_ylim(-0.6, 3.6)
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch20_sem_a1_path')


@big
def chart_a5(phi):
    """A5: the AR(22) coefficients implied by the HAR with averages of logs (JPM)."""
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    lags = np.arange(1, 23)
    col = [IDAred] + [Orange] * 4 + [MainBlue] * 17
    ax.bar(lags, phi, color=col, width=0.7)
    for c_, lab in [(IDAred, 'Lag 1: daily + weekly + monthly terms'), (Orange, 'Lags 2-5: weekly + monthly terms'),
                    (MainBlue, 'Lags 6-22: monthly term only')]:
        ax.bar([np.nan], [np.nan], color=c_, label=lab)
    ax.set_xlabel('Lag j (days)')
    ax.set_ylabel('Implied coefficient phi_j')
    ax.set_xticks([1, 5, 10, 15, 22])
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    save_fig('ch20_sem_a5_phi')


@big
def chart_a7():
    """A7: QLIKE(1, F) against the squared error as functions of the forecast F."""
    F = np.linspace(0.25, 2.5, 400)
    fig, ax = plt.subplots(figsize=(5.0, 3.3))
    ax.plot(F, S.qlike(1.0, F), color=MainBlue, lw=1.6, label='QLIKE(RV = 1, F)')
    ax.plot(F, (1 - F) ** 2, color=Orange, lw=1.6, ls='-.', label='Squared error (1 - F)^2')
    for f_ in (0.5, 1.5):
        ax.plot([f_], [S.qlike(1.0, f_)], 'o', color=IDAred if f_ < 1 else Forest,
                label=f'F = {f_}: QLIKE {float(S.qlike(1.0, f_)):.3f}')
    ax.axvline(1, color=Gray, ls='--', lw=0.8)
    ax.set_xlabel('Forecast F (true RV = 1)')
    ax.set_ylabel('Loss')
    ax.set_ylim(0, 0.8)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch20_sem_a7_qlike')


@big
def chart_a9(d):
    """A9: softmax kernel weights for three temperatures and their effective sample sizes."""
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    x = np.arange(len(d))
    for i, (g, c_) in enumerate([(0.0, Teal), (1.0, MainBlue), (3.0, IDAred)]):
        w = np.exp(-g * d) / np.exp(-g * d).sum()
        ax.bar(x + (i - 1) * 0.26, w, width=0.26, color=c_,
               label=f'gamma = {g:.0f}: n_eff = {1 / np.sum(w ** 2):.2f}')
    ax.set_xticks(x)
    ax.set_xticklabels([f'window {k + 1}\ndistance {v}' for k, v in enumerate(d)])
    ax.set_ylabel('Weight w')
    legend_outside_bottom(ax, ncol=1, y=-0.28)
    save_fig('ch20_sem_a9_weights')


# -----------------------------------------------------------------------------
# PART B
# -----------------------------------------------------------------------------
def levy_regression(kind, sym, chart):
    """Does the Levy area (return, log RV) of the last 22 days predict the next-month change of log RV?"""
    a = S.load_asset(kind, sym)
    D = S.build_design(a, 22)
    P = D['path']                                   # (t, log RV, cumulative return)
    sig = S.sig_windows(P[:, [2, 1]], 22, 2)        # channels (return, log RV) only: level 2 gives the area
    levy = 0.5 * (sig[:, 3] - sig[:, 4])
    y = D['ly'] - D['X_loghar'][:, 2]               # log of next-month RV minus log of past-month mean RV
    X = np.c_[D['X_loghar'], levy / np.nanstd(levy)]
    ok = np.isfinite(X).all(1) & np.isfinite(y)
    b, se, _ = ols_hac(y[ok], X[ok], 22)
    b0, se0, _ = ols_hac(y[ok], X[ok][:, :3], 22)
    e1 = y[ok] - np.c_[np.ones(ok.sum()), X[ok]] @ b
    e0 = y[ok] - np.c_[np.ones(ok.sum()), X[ok][:, :3]] @ b0
    r2 = 1 - e1.var() / y[ok].var()
    r20 = 1 - e0.var() / y[ok].var()
    chart_levy(y[ok], X[ok][:, :3], X[ok][:, 3], b[4], se[4], sym, chart)
    return {'b_levy': b[4], 'se_levy': se[4], 't_levy': b[4] / se[4], 'r2': r2, 'r2_base': r20,
            'N': int(ok.sum()), 'mean_levy': float(np.nanmean(levy)),
            'frac_neg': float(np.mean(levy[np.isfinite(levy)] < 0))}


@big
def chart_levy(y, Xb, A, b, se, sym, name):
    """Binned scatter (Frisch-Waugh): target and Levy area, both residualised on the log-HAR terms."""
    Z = np.c_[np.ones(len(y)), Xb]
    res = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
    A = A - Z @ np.linalg.lstsq(Z, A, rcond=None)[0]
    q = pd.qcut(A, 20, labels=False)
    xb = pd.Series(A).groupby(q).mean()
    yb = pd.Series(res).groupby(q).mean()
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    ax.scatter(xb, yb, color=MainBlue, s=22, zorder=3, label=f'{sym}: mean of 20 equal-count bins')
    xx = np.linspace(xb.min(), xb.max(), 50)
    ax.plot(xx, b * xx, color=IDAred, lw=1.5, label=f'OLS slope {b:.3f} (HAC s.e. {se:.3f})')
    ax.fill_between(xx, (b - 1.96 * se) * xx, (b + 1.96 * se) * xx, color=Gray, alpha=0.2,
                    label='95% HAC band of the slope')
    ax.axhline(0, color=Gray, ls='--', lw=0.8)
    ax.set_xlabel('Standardised Levy area A_t, residual on log-HAR terms')
    ax.set_ylabel('Next-month change of log RV,\nresidual on log-HAR terms')
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    save_fig(name)


@big
def chart_coef(out, sym, name):
    """SHAR semivariance coefficients and the HARQ coefficient with 95% HAC intervals."""
    fig, axes = plt.subplots(1, 2, figsize=(5.8, 3.1), gridspec_kw={'width_ratios': [2, 1]})
    b, se = out['shar']['b'], out['shar']['se']
    ax = axes[0]
    for i, (k, lab, c_) in enumerate([(1, 'beta+ (positive semivariance)', Forest),
                                      (2, 'beta- (negative semivariance)', IDAred)]):
        ax.errorbar([i], [b[k]], yerr=[1.96 * se[k]], fmt='o', color=c_, capsize=4, label=f'SHAR {lab}')
    ax.axhline(0, color=Gray, ls='--', lw=0.8)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['beta+', 'beta-'])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel('Coefficient, 95% HAC interval')
    ax.set_title(f'{sym}: SHAR', fontsize=9)
    ax = axes[1]
    bq, sq = out['harq']['b'][2], out['harq']['se'][2]
    ax.errorbar([0], [bq], yerr=[1.96 * sq], fmt='s', color=Purple, capsize=4, label='HARQ beta_Q')
    ax.axhline(0, color=Gray, ls='--', lw=0.8)
    ax.set_xticks([0])
    ax.set_xticklabels(['beta_Q'])
    ax.set_xlim(-0.8, 0.8)
    ax.set_title(f'{sym}: HARQ', fontsize=9)
    fig_legend_bottom(fig, axes, ncol=1, y=0.0)
    plt.tight_layout(rect=(0, 0.2, 1, 1))
    save_fig(name)


@big
def chart_pvalues(p, h, comp, name):
    """Sorted one-sided DM p-values of the 50 assets against the 5%, Holm and BH thresholds."""
    m = len(p)
    k = np.arange(1, m + 1)
    ps = np.sort(p)
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    ax.scatter(k, ps, color=MainBlue, s=14, zorder=3, label=f'Sorted p-values, {comp}, h = {h}')
    ax.axhline(0.05, color=Orange, lw=1.2, label='5% without correction')
    ax.step(k, 0.05 / (m - k + 1), where='mid', color=IDAred, lw=1.2, label='Holm: 0.05 / (m - k + 1)')
    ax.plot(k, 0.05 * k / m, color=Forest, lw=1.2, ls='-.', label='BH: 0.05 k / m')
    ax.set_yscale('log')
    ax.set_xlabel('Rank k of the p-value (m = 50 assets)')
    ax.set_ylabel('One-sided DM p-value (log scale)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig(name)


def har_family(kind, sym):
    a = S.load_asset(kind, sym)
    D = S.build_design(a, 1)
    ok = np.isfinite(D['X_har']).all(1) & np.isfinite(D['y'])
    y = D['y'][ok]
    out = {'N': int(ok.sum())}
    b, se, _ = ols_hac(y, D['X_har'][ok], 5)
    out['har'] = {'b': b.tolist(), 'se': se.tolist()}
    b, se, V = ols_hac(y, D['X_shar'][ok], 5)
    diff = b[2] - b[1]
    sd = np.sqrt(V[2, 2] + V[1, 1] - 2 * V[1, 2])
    out['shar'] = {'b': b.tolist(), 'se': se.tolist(), 'diff': diff, 't_diff': diff / sd,
                   'p_diff': float(stats.norm.sf(diff / sd))}
    sq = D['sqrq'][ok]
    Xq = np.c_[D['X_har'][ok, 0], D['X_har'][ok, 0] * (sq - sq.mean()), D['X_har'][ok, 1:]]
    b, se, _ = ols_hac(y, Xq, 5)
    out['harq'] = {'b': b.tolist(), 'se': se.tolist(), 't_q': b[2] / se[2]}
    chart_coef(out, sym, f'ch20_sem_{"b3" if sym == "JPM" else "b4"}_coef')
    return out


def block_boot_ratio(la, lb, block=10, B=2000, seed=20):
    """Stationary-bootstrap CI for mean(la) / mean(lb)."""
    rng = np.random.default_rng(seed)
    T = len(la)
    p = 1.0 / block
    stats_ = []
    for _ in range(B):
        idx = np.empty(T, int)
        idx[0] = rng.integers(T)
        for i in range(1, T):
            idx[i] = rng.integers(T) if rng.random() < p else (idx[i - 1] + 1) % T
        stats_.append(la[idx].mean() / lb[idx].mean())
    return np.percentile(stats_, [2.5, 97.5]).tolist()


def sig_vs_loghar(kind, sym, h, c, cutoff=None):
    cfg = dict(S.CFG)
    a = S.load_asset(kind, sym)
    D = S.build_design(a, h, cfg)
    st = S.eval_start(D, cfg, cutoff)
    fc, info, _ = S.run_forecasts(D, cfg, c, c, st, len(a) - h, models=['logHAR', 'Sig-LK'])
    qa, qb = S.qlike(fc.y.values, fc['Sig-LK'].values), S.qlike(fc.y.values, fc['logHAR'].values)
    t, p1, p2 = S.dm_test(qa, qb, h)
    gw, pgw = S.gw_test(qa, qb, h)
    ci = block_boot_ratio(qa, qb, block=max(h, 10), B=1000)
    return {'T': len(fc), 'start': str(fc.index[0].date()), 'end': str(fc.index[-1].date()),
            'ql_sig': float(qa.mean()), 'ql_har': float(qb.mean()), 'ratio': float(qa.mean() / qb.mean()),
            'ci': ci, 't': float(t), 'p1': float(p1), 'p2': float(p2), 'gw': float(gw), 'p_gw': float(pgw),
            'k': float(info['k_Sig-LK'].mean()), 'ess': float(info['ess'].mean())}, fc


@big
def chart_cumloss(fc, sym, h, name):
    """Cumulative QLIKE difference Sig-LK minus log-HAR: upward = log-HAR better."""
    d = (S.qlike(fc.y, fc['Sig-LK']) - S.qlike(fc.y, fc['logHAR'])).cumsum()
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ax.plot(d.index, d, color=IDAred, lw=1.1, label=f'Cumulative QLIKE(Sig-LK) - QLIKE(log-HAR), {sym}, h = {h}')
    ax.axhline(0, color=Gray, ls='--', lw=0.8)
    ax.set_ylabel('Cumulative loss difference')
    legend_outside_bottom(ax, ncol=1, y=-0.14)
    save_fig(name)


def part_b():
    B = {}
    B['b1'] = levy_regression('stocks', 'JPM', 'ch20_sem_b1_levy')
    B['b2'] = levy_regression('futures', 'ES', 'ch20_sem_b2_levy')
    B['b3'] = har_family('stocks', 'JPM')
    B['b4'] = har_family('futures', 'CL')
    LR = lecture_results()
    c1, _, cut1 = S.tuned(LR, 'stocks', 1)
    c5, _, cut5 = S.tuned(LR, 'futures', 5)
    B['b5'], fc = sig_vs_loghar('stocks', 'JPM', 1, c1, cut1)
    B['b6'], fc6 = sig_vs_loghar('futures', 'ES', 5, c5, cut5)
    chart_cumloss(fc6, 'ES', 5, 'ch20_sem_b6_cumloss')
    # B5 chart: cumulative QLIKE difference
    chart_cumloss(fc, 'JPM', 1, 'ch20_sem_cumloss')
    # B7/B8: multiple testing on the lecture's 50 DM p-values
    for key, h, comp in [('b7', 1, 'Sig-LK|logHAR'), ('b8', 22, 'Sig-LK|HAR')]:
        dmp = LR['dm_p'][str(h)][comp]                      # {kind|sym: one-sided DM p-value}
        rows = [(k.split('|')[1], k.split('|')[0], v) for k, v in dmp.items()]
        p = np.array([r[2] for r in rows])
        o = np.argsort(p)
        fx = sorted([(r[0], r[2]) for r in rows if r[1] == 'forex'], key=lambda x: x[1])
        pf = np.array([pp for _, pp in fx])
        B[key] = {'n': len(p), 'raw': int((p < 0.05).sum()), 'holm': int((S.holm(p) < 0.05).sum()),
                  'bh': int((S.bh(p) < 0.05).sum()), 'smallest': [(rows[i][0], float(p[i])) for i in o[:5]],
                  'fx': fx, 'fx_holm': S.holm(pf).tolist(), 'fx_bh': S.bh(pf).tolist()}
        chart_pvalues(p, h, comp.replace('|', ' vs ').replace('logHAR', 'log-HAR'), f'ch20_sem_{key}_pvalues')
    RES['B'] = B


# -----------------------------------------------------------------------------
# PART C: basepoint kernel (sees the volatility level)
# -----------------------------------------------------------------------------
def _outer(A, B_):
    return (A[:, :, None] * B_[:, None, :]).reshape(A.shape[0], -1)


def prepend_segment(v, sig, d, depth):
    """Chen: signature of (segment with increment v) * path = exp(v) (x) Sig(path), rows vectorised."""
    m = sig.shape[0]
    lv = [np.ones((m, 1))]
    pos = 0
    for k in range(1, depth + 1):
        lv.append(sig[:, pos:pos + d ** k])
        pos += d ** k
    pw = [np.ones((m, 1))]
    for p in range(1, depth + 1):
        pw.append(_outer(pw[-1], v) / p)
    out = [sum(_outer(pw[p], lv[k - p]) for p in range(0, k + 1)) for k in range(1, depth + 1)]
    return np.concatenate(out, axis=1)


def basepoint_job(kind, sym, h, c, cutoff=None):
    """Sig-LK whose kernel distance uses the basepoint-augmented path (level of log RV relative to the window mean)."""
    cfg = dict(S.CFG)
    a = S.load_asset(kind, sym)
    D = S.build_design(a, h, cfg)
    st = S.eval_start(D, cfg, cutoff)
    stop = len(a) - h
    L, W = cfg['L'], cfg['W']
    lrv = np.log(a.rv.values)
    rows = []
    t = st
    while t < stop:
        tr = np.arange(t - h - W + 1, t - h + 1)
        inc = D['incr'][tr[0]:t + 1]
        sc = np.array([1.0] + [1.0 / (np.nanstd(inc[:, j]) * np.sqrt(L - 1)) for j in (1, 2)])
        scale = S.sig_scale(sc, cfg['DEPTH'])
        idx = np.r_[tr, t]
        start = idx - L + 1                                    # first point of each window
        mu, sd = lrv[tr].mean(), lrv[tr].std()
        v = np.c_[np.zeros(len(idx)), (lrv[start] - mu) / sd, np.zeros(len(idx))]
        sbp = prepend_segment(v, D['sig'][idx] * scale, 3, cfg['DEPTH'])
        dist = np.sum((sbp[:-1] - sbp[-1]) ** 2, axis=1)
        g = c / np.median(dist)
        w = np.exp(-g * (dist - dist.min()))
        w /= w.sum()
        Xsig = np.c_[D['X_loghar'][tr], D['sig'][tr] * scale]
        b0, beta, s2, sup = S.two_step_lasso(Xsig, D['ly'][tr], w)
        blk = np.arange(t, min(t + cfg['K'], stop))
        X = np.c_[D['X_loghar'][blk], D['sig'][blk] * scale]
        f = np.exp(b0 + X @ beta + 0.5 * s2)
        for i, s_ in enumerate(blk):
            rows.append([D['dates'][s_], D['y'][s_], f[i], 1 / np.sum(w ** 2)])
        t += cfg['K']
    fc = pd.DataFrame(rows, columns=['date', 'y', 'Sig-LK-bp', 'ess']).set_index('date')
    main, _, _ = S.run_forecasts(D, cfg, c, c, st, stop, models=['HAR', 'logHAR', 'Sig-LK'])
    main = main.reindex(fc.index)
    q = {m: S.qlike(fc.y.values, main[m].values) for m in ['logHAR', 'Sig-LK', 'HAR']}
    q['Sig-LK-bp'] = S.qlike(fc.y.values, fc['Sig-LK-bp'].values)
    covid = (fc.index >= '2020-02-20') & (fc.index <= '2020-04-30')
    t_, p1, _ = S.dm_test(q['Sig-LK-bp'], q['logHAR'], h)
    return {'sym': sym, 'ql': {m: float(v.mean()) for m, v in q.items()},
            'ql_covid': {m: float(v[covid].mean()) for m, v in q.items()} if covid.any() else None,
            'p_vs_loghar': float(p1), 'ess': float(fc.ess.mean())}


def part_c(syms=None):
    from joblib import Parallel, delayed
    c, _, cut = S.tuned(lecture_results(), 'stocks', 1)
    syms = syms or S.symbols('stocks')
    out = Parallel(n_jobs=int(os.environ.get('CH20_JOBS', '14')))(delayed(basepoint_job)('stocks', s, 1, c, cut)
                                                                  for s in syms)
    Q = pd.DataFrame({o['sym']: o['ql'] for o in out}).T
    QC = pd.DataFrame({o['sym']: o['ql_covid'] for o in out}).T
    p = np.array([o['p_vs_loghar'] for o in out])
    rel = Q.div(Q['logHAR'], axis=0)
    relc = QC.div(QC['logHAR'], axis=0)
    RES['C'] = {'c': c, 'rel': rel.mean().to_dict(), 'rel_covid': relc.mean().to_dict(),
                'wins_raw': int((p < 0.05).sum()), 'wins_holm': int((S.holm(p) < 0.05).sum()),
                'wins_bh': int((S.bh(p) < 0.05).sum()), 'n': len(p), 'ess': float(np.mean([o['ess'] for o in out])),
                'n_better': int((rel['Sig-LK-bp'] < rel['Sig-LK']).sum())}
    RES['C']['per_stock'] = rel[['Sig-LK', 'Sig-LK-bp']].round(4).to_dict('index')
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    ax.scatter(rel['Sig-LK'], rel['Sig-LK-bp'], color=MainBlue, s=16, label='One stock (h = 1)')
    lo = min(rel['Sig-LK'].min(), rel['Sig-LK-bp'].min()) - 0.01
    hi = max(rel['Sig-LK'].max(), rel['Sig-LK-bp'].max()) + 0.01
    ax.plot([lo, hi], [lo, hi], color=Gray, ls='--', lw=0.8)
    ax.axhline(1, color=Gray, lw=0.5)
    ax.axvline(1, color=Gray, lw=0.5)
    for s_ in rel.index:
        if abs(rel.loc[s_, 'Sig-LK-bp'] - rel.loc[s_, 'Sig-LK']) > 0.04:
            ax.annotate(s_, (rel.loc[s_, 'Sig-LK'], rel.loc[s_, 'Sig-LK-bp']), fontsize=7, color='black',
                        xytext=(3, 3), textcoords='offset points')
    ax.set_xlabel('Sig-LK, plain kernel: QLIKE / log-HAR')
    ax.set_ylabel('Sig-LK, basepoint kernel: QLIKE / log-HAR')
    legend_outside_bottom(ax, ncol=1, y=-0.16)
    save_fig('ch20_sem_basepoint')


if __name__ == '__main__':
    setup_check()
    part_a()
    part_b()
    if os.environ.get('SEM20_SKIP_C'):          # reuse the reference analysis of Part C (40 stocks, slow)
        RES['C'] = json.load(open(os.path.join(HERE, 'sem20_results.json')))['C']
    else:
        part_c()
    with open(os.path.join(HERE, 'sem20_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print(json.dumps(RES, indent=1, default=float)[:3000])

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
from generate_all_charts import (save_fig, legend_outside_bottom, MainBlue, IDAred, Forest, Orange, Purple,  # noqa: E402
                                 Teal, Gray, COL)

if not os.path.isdir(S.VOLARE_DIR):
    S.VOLARE_DIR = os.path.join(HERE, '..', '..', 'data', 'volare')
RES = {}


def lecture_results():
    """Published results of the lecture case study (ch20_results.json in this folder or on GitHub)."""
    f = os.path.join(HERE, 'ch20_results.json')
    if os.path.exists(f):
        return json.load(open(f))
    import urllib.request
    url = 'https://raw.githubusercontent.com/danpele/MFM/main/Quantlets/Ch_20/MFM_ch20_case_study/ch20_results.json'
    return json.load(urllib.request.urlopen(url))


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
# PARTEA A
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
    # A5: HAR as a restricted AR(22) with the full-sample log-HAR of JPM
    a = S.load_asset('stocks', 'JPM')
    D = S.build_design(a, 1)
    ok = np.isfinite(D['X_loghar']).all(1) & np.isfinite(D['ly'])
    b, se, _ = ols_hac(D['ly'][ok], D['X_loghar'][ok], 5)
    phi = np.r_[b[1] + b[2] / 5 + b[3] / 22, np.repeat(b[2] / 5 + b[3] / 22, 4), np.repeat(b[3] / 22, 17)]
    A['a5'] = {'b': b.tolist(), 'se': se.tolist(), 'phi1': phi[0], 'phi2': phi[1], 'phi6': phi[5], 'sum': phi.sum(),
               'N': int(ok.sum())}
    # A7: QLIKE of +/-50% errors
    A['a7'] = {'under': float(S.qlike(1.0, 0.5)), 'over': float(S.qlike(1.0, 1.5)),
               'mse_under': 0.25, 'mse_over': 0.25}
    # A9: kernel weights for distances (0.2, 0.5, 1.0, 2.0), gamma = 1 and gamma = 3
    d = np.array([0.2, 0.5, 1.0, 2.0])
    for g in (1.0, 3.0):
        w = np.exp(-g * d) / np.exp(-g * d).sum()
        A[f'a9_g{int(g)}'] = {'w': w.tolist(), 'ess': float(1 / np.sum(w ** 2))}
    RES['A'] = A


# -----------------------------------------------------------------------------
# PARTEA B
# -----------------------------------------------------------------------------
def levy_regression(kind, sym):
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
    return {'b_levy': b[4], 'se_levy': se[4], 't_levy': b[4] / se[4], 'r2': r2, 'r2_base': r20,
            'N': int(ok.sum()), 'mean_levy': float(np.nanmean(levy)), 'frac_neg': float(np.nanmean(levy < 0))}


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


def sig_vs_loghar(kind, sym, h, c):
    cfg = dict(S.CFG)
    a = S.load_asset(kind, sym)
    D = S.build_design(a, h, cfg)
    st = S.first_origin(D, cfg) + cfg['VAL'] + h
    fc, info, _ = S.run_forecasts(D, cfg, c, c, st, len(a) - h, models=['logHAR', 'Sig-LK'])
    qa, qb = S.qlike(fc.y.values, fc['Sig-LK'].values), S.qlike(fc.y.values, fc['logHAR'].values)
    t, p1, p2 = S.dm_test(qa, qb, h)
    gw, pgw = S.gw_test(qa, qb, h)
    ci = block_boot_ratio(qa, qb, block=max(h, 10), B=1000)
    return {'T': len(fc), 'start': str(fc.index[0].date()), 'end': str(fc.index[-1].date()),
            'ql_sig': float(qa.mean()), 'ql_har': float(qb.mean()), 'ratio': float(qa.mean() / qb.mean()),
            'ci': ci, 't': float(t), 'p1': float(p1), 'p2': float(p2), 'gw': float(gw), 'p_gw': float(pgw),
            'k': float(info['k_Sig-LK'].mean()), 'ess': float(info['ess'].mean())}, fc


def part_b():
    B = {}
    B['b1'] = levy_regression('stocks', 'JPM')
    B['b2'] = levy_regression('futures', 'ES')
    B['b3'] = har_family('stocks', 'JPM')
    B['b4'] = har_family('futures', 'CL')
    val = lecture_results()['validation']
    B['b5'], fc = sig_vs_loghar('stocks', 'JPM', 1, val['Sig-LK|1']['c'])
    B['b6'], _ = sig_vs_loghar('futures', 'ES', 5, val['Sig-LK|5']['c'])
    # B5 chart: cumulative QLIKE difference
    d = (S.qlike(fc.y, fc['Sig-LK']) - S.qlike(fc.y, fc['logHAR'])).cumsum()
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    ax.plot(d.index, d, color=IDAred, lw=1.0, label='Cumulative QLIKE(Sig-LK) - QLIKE(log-HAR), JPM, h = 1')
    ax.axhline(0, color=Gray, ls='--', lw=0.8)
    ax.set_ylabel('Cumulative loss difference')
    legend_outside_bottom(ax, ncol=1, y=-0.12)
    save_fig('ch20_sem_cumloss')
    # B7/B8: multiple testing on the lecture's 50 DM p-values
    LR = lecture_results()
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
    RES['B'] = B


# -----------------------------------------------------------------------------
# PARTEA C: nucleu cu punct de baza (vede nivelul volatilitatii)
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


def basepoint_job(kind, sym, h, c):
    """Sig-LK whose kernel distance uses the basepoint-augmented path (level of log RV relative to the window mean)."""
    cfg = dict(S.CFG)
    a = S.load_asset(kind, sym)
    D = S.build_design(a, h, cfg)
    st = S.first_origin(D, cfg) + cfg['VAL'] + h
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
    c = lecture_results()['validation']['Sig-LK|1']['c']
    syms = syms or S.symbols('stocks')
    out = Parallel(n_jobs=int(os.environ.get('CH20_JOBS', '14')))(delayed(basepoint_job)('stocks', s, 1, c) for s in syms)
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
    part_a()
    part_b()
    part_c()
    with open(os.path.join(HERE, 'sem20_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print(json.dumps(RES, indent=1, default=float)[:3000])

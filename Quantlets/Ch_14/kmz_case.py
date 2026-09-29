"""
kmz_case.py -- Capitolul 14, studiul de caz: Kelly, Malamud & Zhou (2024), The virtue of complexity in return prediction
=====================================================================================================================
Replicare pe datele cursului (lunar, din 1993) a Figurilor 7-8 (R^2 si raportul Sharpe al sincronizarii in functie de
complexitatea c = P/T) si a Figurii 10 (pozitiile strategiei si recesiunile NBER), cu specificatia din lucrare:
  * randamentul in exces al SPY (randament total lunar minus TB3MS), scalat cu abaterea standard necentrata din
    ultimele 12 luni; predictorii Welch-Goyal disponibili (tbl, lty, tms, dfy, infl, svar, randamentul intarziat),
    scalati cu abaterea standard pe fereastra extinsa, dupa 36 de luni de initializare (Sectiunea V.A)
  * trasaturi Fourier aleatoare S = (sin(gamma w'G), cos(gamma w'G)), w ~ N(0, I), gamma = 2 (ec. 20)
  * ridge fara termen liber pe ferestre mobile de T = 12 luni, P = 2 ... 12 000, log10 z = -3 ... 3,
    trasaturile scalate cu abaterea standard din fereastra de antrenare; statistici mediate pe 1 000 de extrageri
  * reperul: regresia liniara kitchen sink pe cei 7 predictori, z = 0+ si z = 10^3 (Sectiunea V.D)
Iesire: kmz_case.json, charts/ch14_kmz_complexity.pdf, charts/ch14_kmz_positions.pdf
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import io
import json
import os
import sys
import urllib.request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mfm_tsfm as M               # noqa: E402
import generate_all_charts as g    # noqa: E402  (stil MFM, culori, save_fig)

KMZ_T = 12                         # rolling training window (months)
KMZ_GAMMA = 2.0                    # RFF bandwidth
KMZ_PMAX = 12000
KMZ_P = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 90, 120, 240, 360, 600, 1200, 2400, 6000, 12000]
KMZ_LOGZ = [-3, -2, -1, 0, 1, 2, 3]
KMZ_DRAWS = 1000
KMZ_WARMUP = 36
KMZ_PRED = ['tbl', 'lty', 'tms', 'dfy', 'infl', 'svar', 'lag_ret']


def read_fred(series):
    """Monthly FRED series (Federal Reserve Bank of St. Louis)."""
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}'
    raw = urllib.request.urlopen(url, timeout=120).read().decode()
    df = pd.read_csv(io.StringIO(raw), index_col=0, parse_dates=True, na_values='.')
    s = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().rename(series)
    s.index = s.index.to_period('M')
    return s


def kmz_data():
    """Monthly excess returns R_{t+1} and predictors G_t, standardised as in Section V.A of the paper."""
    spy = M.read_market('SPY.US')['adjusted_close']
    last = spy.index[-1]
    spy = spy[spy.index.to_period('M') < last.to_period('M')]          # complete months only
    pm = spy.groupby(spy.index.to_period('M')).last()
    ret = pm.pct_change().dropna()
    gspc = M.read_market('GSPC.INDX')['close']
    gspc = gspc[gspc.index.to_period('M') < last.to_period('M')]
    dr = np.log(gspc).diff().dropna()
    svar = (dr ** 2).groupby(dr.index.to_period('M')).sum()
    f = {s: read_fred(s) for s in ('TB3MS', 'GS10', 'BAA', 'AAA', 'CPIAUCSL', 'USREC')}
    df = pd.DataFrame({'ret': ret})
    df['rf'] = (f['TB3MS'] / 1200).shift(1).reindex(df.index)          # bill rate known at the start of the month
    df['ex'] = df['ret'] - df['rf']
    df['tbl'] = (f['TB3MS'] / 100).reindex(df.index)
    df['lty'] = (f['GS10'] / 100).reindex(df.index)
    df['tms'] = df['lty'] - df['tbl']
    df['dfy'] = ((f['BAA'] - f['AAA']) / 100).reindex(df.index)
    df['infl'] = f['CPIAUCSL'].pct_change().shift(1).reindex(df.index)  # CPI released with a one-month delay
    df['svar'] = svar.reindex(df.index)
    df['lag_ret'] = df['ex']
    df = df.dropna()
    # predictors: expanding-window standard deviation, at least 36 months
    G = df[KMZ_PRED] / df[KMZ_PRED].expanding(KMZ_WARMUP).std()
    # target R_{t+1}, scaled by the uncentred standard deviation of the last 12 months (known at t)
    vol12 = np.sqrt((df['ex'] ** 2).rolling(12).mean())
    R = df['ex'].shift(-1) / vol12
    out = pd.concat([G, R.rename('R')], axis=1).dropna()
    rec = f['USREC'].reindex(out.index.map(lambda p: p + 1)).values    # recession in the month of R_{t+1}
    return out, pd.Series(rec, index=out.index, name='USREC')


def _ridge_paths(K, k, y, zs):
    """Forecasts and ||beta||^2 of ridge in dual form for a batch of windows.
    K: (W, T, T) = S S' ; k: (W, T) = S s_t ; y: (W, T). beta(z) = S'(zT I + S S')^{-1} y."""
    W, T, _ = K.shape
    fc, bn = [], []
    for z in zs:
        A = K + z * T * np.eye(T)[None]
        a = np.linalg.solve(A, y[..., None])[..., 0]
        fc.append(np.einsum('wt,wt->w', k, a))
        bn.append(np.einsum('wt,wts,ws->w', a, K, a))
    return np.stack(fc, -1), np.stack(bn, -1)


def kmz_stats(fc, R):
    """Out-of-sample R^2 = 1 - Var(error)/Var(R), annualised Sharpe ratio of pi_t R_{t+1} and its t-statistic."""
    e = R[:, None] - fc
    r2 = 1 - e.var(0) / R.var()
    tr = fc * R[:, None]
    sr = tr.mean(0) / tr.std(0, ddof=1)
    return r2, np.sqrt(12) * sr, sr * np.sqrt(len(R))


def kmz_run(draws=KMZ_DRAWS, seed=0):
    """RFF ridge over the P and z grids, averaged over independent draws of the features; linear benchmarks."""
    df, rec = kmz_data()
    G, R = df[KMZ_PRED].values, df['R'].values
    N, T = len(R), KMZ_T
    tidx = np.arange(T, N)                                   # forecast rows (training rows t-12 ... t-1)
    Rt = R[tidx]
    Y = np.stack([R[t - T:t] for t in tidx])                 # (W, T)
    zs = [10.0 ** e for e in KMZ_LOGZ]
    nP, nz = len(KMZ_P), len(zs)
    acc = {k: np.zeros((nP, nz)) for k in ('r2', 'sr', 'bn')}
    pos = np.zeros(len(tidx))
    iP, iZ = KMZ_P.index(12000), KMZ_LOGZ.index(3)
    rng = np.random.default_rng(seed)
    win = np.stack([np.arange(t - T, t) for t in tidx])      # (W, T)
    bounds = [0] + KMZ_P
    for d in range(draws):
        om = rng.standard_normal((G.shape[1], KMZ_PMAX // 2))
        X = KMZ_GAMMA * G @ om
        F = np.empty((N, KMZ_PMAX))
        F[:, 0::2], F[:, 1::2] = np.sin(X), np.cos(X)         # pairs (sin, cos) of the same frequency
        K = np.zeros((len(tidx), T, T))
        k = np.zeros((len(tidx), T))
        fcs, bns = [], []
        for j in range(nP):
            seg = slice(bounds[j], bounds[j + 1])
            Sw = F[win, seg]                                  # (W, T, p)
            sd = Sw.std(1, ddof=1)                            # training-window standard deviation
            sd[sd < 1e-12] = np.inf
            Sw = Sw / sd[:, None, :]
            st = F[tidx, seg] / sd
            K += Sw @ Sw.transpose(0, 2, 1)
            k += np.einsum('wtp,wp->wt', Sw, st)
            f_, b_ = _ridge_paths(K, k, Y, zs)
            fcs.append(f_)
            bns.append(b_)
        for j in range(nP):
            r2, sr, _ = kmz_stats(fcs[j], Rt)
            acc['r2'][j] += r2
            acc['sr'][j] += sr
            acc['bn'][j] += bns[j].mean(0)
        pos += fcs[iP][:, iZ]
        if (d + 1) % 50 == 0:
            print(f'   draw {d + 1}/{draws}')
    for key in acc:
        acc[key] /= draws
    pos /= draws
    # linear kitchen sink on the 7 predictors, no intercept (z = 0+ is least squares, P = 7 < T)
    lin = {}
    for name, z in (('lin0', 0.0), ('lin3', 1e3)):
        f_ = np.empty(len(tidx))
        for i, t in enumerate(tidx):
            Sx, y = G[t - T:t], R[t - T:t]
            b = np.linalg.solve(z * np.eye(Sx.shape[1]) + Sx.T @ Sx / T, Sx.T @ y / T) if z > 0 \
                else np.linalg.lstsq(Sx, y, rcond=None)[0]
            f_[i] = G[t] @ b
        lin[name] = f_
    dates = df.index[tidx] + 1                                # month of R_{t+1}
    return dict(dates=dates, R=Rt, acc=acc, pos=pos, lin=lin, rec=rec.values[tidx], zs=zs)


def kmz_table(out):
    """Table I-style statistics for the two linear models and RFF (c = 1000, z = 10^3, position averaged over draws)."""
    Rt = out['R']
    rows = {}
    for name, f_ in (('lin0', out['lin']['lin0']), ('lin3', out['lin']['lin3']), ('rff', out['pos'])):
        r2, sr, t = kmz_stats(f_[:, None], Rt)
        tr = f_ * Rt
        X = np.column_stack([np.ones_like(Rt), Rt])           # information ratio against the market
        b = np.linalg.lstsq(X, tr, rcond=None)[0]
        u = tr - X @ b
        se = np.sqrt(u.var(ddof=2) * np.linalg.inv(X.T @ X)[0, 0])
        rows[name] = dict(r2=100 * r2[0], sr=sr[0], t=t[0], ir=np.sqrt(12) * b[0] / u.std(ddof=2), ir_t=b[0] / se)
    return rows


def fig_kmz_complexity(out):
    """Figures 7-8 of the paper on course data: out-of-sample R^2 and Sharpe ratio against c = P/T."""
    c = np.array(KMZ_P) / KMZ_T
    cols = {-3: g.IDAred, -1: g.Orange, 1: g.Forest, 3: g.MainBlue}
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.1))
    for e, col in cols.items():
        j = KMZ_LOGZ.index(e)
        lbl = f'$z = 10^{{{e}}}$'
        axes[0].plot(c, 100 * out['acc']['r2'][:, j], color=col, marker='o', ms=2.5, label=lbl)
        axes[1].plot(c, out['acc']['sr'][:, j], color=col, marker='o', ms=2.5, label=lbl)
    lsr = kmz_stats(out['lin']['lin3'][:, None], out['R'])[1][0]
    for ax in axes:
        ax.set_xscale('log')
        ax.axvline(1, color=g.Gray, lw=0.8, ls='--')
        ax.set_xlabel('Complexity $c = P/T$ (log scale)')
    axes[0].axhline(0, color=g.Gray, lw=0.6)
    axes[0].set_ylim(-60, 5)
    axes[0].set_ylabel('Out-of-sample $R^2$ (%)')
    axes[0].set_title('Out-of-sample $R^2$ (clipped at $-60\\%$)', color='black')
    axes[1].axhline(lsr, color=g.Purple, lw=1.0, ls=':', label='Linear, 7 predictors, $z = 10^3$')
    axes[1].axhline(0, color=g.Gray, lw=0.6)
    axes[1].set_ylabel('Annualised Sharpe ratio')
    axes[1].set_title('Sharpe ratio of the timing strategy', color='black')
    h, lab = axes[1].get_legend_handles_labels()
    g.fig_legend_bottom(fig, h, lab, ncol=5, y=0.02)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    g.save_fig('ch14_kmz_complexity')


def fig_kmz_positions(out):
    """Figure 10 of the paper on course data: RFF timing position (c = 1000, z = 10^3) and NBER recessions."""
    d = out['dates'].to_timestamp()
    fig, ax = plt.subplots(figsize=(9.2, 3.0))
    rec = out['rec'] > 0
    lo, hi = np.min(out['pos']), np.max(out['pos'])
    pad = 0.1 * (hi - lo)
    ax.fill_between(d, lo - pad, hi + pad, where=rec, color=g.LightGray, step='mid', label='NBER recession')
    ax.plot(d, out['pos'], color=g.MainBlue, lw=1.0, label='RFF position $\\hat\\beta\' S_t$ ($c = 1000$, $z = 10^3$)')
    ax.plot(d, pd.Series(out['pos']).rolling(12, min_periods=1).mean(), color=g.IDAred, lw=1.3,
            label='12-month moving average')
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_ylabel('Position (average of 1,000 draws)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.13)
    g.save_fig('ch14_kmz_positions')


def kmz_positions_stats(out):
    """Share of long months; average position in recessions, in the 6 months before each recession, and otherwise."""
    p, rec = out['pos'], out['rec'] > 0
    starts = [i for i in range(1, len(rec)) if rec[i] and not rec[i - 1]]
    pre = np.zeros(len(p), bool)
    for s in starts:
        pre[max(0, s - 6):s] = True
    other = ~rec & ~pre
    return dict(long_share=100 * float(np.mean(p > 0)), mean=float(p.mean()), rec=float(p[rec].mean()),
                pre=float(p[pre].mean()), other=float(p[other].mean()), n_rec=len(starts),
                rec_start=[str(out['dates'][s]) for s in starts])


def main():
    out = kmz_run()
    fig_kmz_complexity(out)
    fig_kmz_positions(out)
    c = np.array(KMZ_P) / KMZ_T
    j3 = KMZ_LOGZ.index(3)
    res = dict(start=str(out['dates'][0]), end=str(out['dates'][-1]), n=len(out['R']), draws=KMZ_DRAWS,
               table=kmz_table(out), positions=kmz_positions_stats(out),
               curve={f'{e}': dict(r2=list(100 * out['acc']['r2'][:, KMZ_LOGZ.index(e)]),
                                   sr=list(out['acc']['sr'][:, KMZ_LOGZ.index(e)]),
                                   bn=list(out['acc']['bn'][:, KMZ_LOGZ.index(e)])) for e in KMZ_LOGZ},
               c=list(c), best_sr=float(out['acc']['sr'][:, j3].max()),
               best_c=float(c[int(np.argmax(out['acc']['sr'][:, j3]))]))
    with open(os.path.join(HERE, 'kmz_case.json'), 'w') as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps({k: res[k] for k in ('start', 'end', 'n', 'table', 'positions', 'best_sr', 'best_c')},
                     indent=1, default=float))


if __name__ == '__main__':
    main()

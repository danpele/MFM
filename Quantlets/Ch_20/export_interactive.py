"""Export the inputs of the Chapter 20 interactive page (MFM/interactive/ch20_data.js).

Uses sigvol.py and generate_all_charts.py: the forecast tables and the per-asset evaluation written by
forecast_panel.py and generate_all_charts.py (local cache data/volare/ch20_cache), the kernel weights saved at the
origin 16 March 2020, and the chapter's own signature, kernel and model-confidence-set functions. save_fig is
replaced by a no-op: no chart or results file of the chapter is rewritten.

VOLARE values are licensed for research use and are not redistributed, so the page receives summaries only:
per-asset mean losses and MCS p-values, kernel distances and weights, the cross-sectional mean volatility of the
40 stocks, weekly (non-overlapping 5-day) means of the volatility of the six assets on the data slide, and the
excerpt of the JPM forecasts of February-May 2020 shown on the COVID-19 slide. The second case study adds per-day
statistics of the public five-minute SPY and Bitcoin bars (data/market/intraday, leadlag_case.py).
"""
import json
import os

import numpy as np
import pandas as pd

import generate_all_charts as g
import sigvol as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch20_data.js')


def no_save(name):
    import matplotlib.pyplot as plt
    plt.close('all')


g.save_fig = no_save
M = S.MODELS
H = list(S.CFG['HORIZONS'])
CLS = list(S.CLASSES)


def r(x, d=4):
    a = np.round(np.asarray(x, float), d)
    if a.ndim > 1:
        return [r(row, d) for row in a]
    return [None if not np.isfinite(v) else float(v) for v in a]


def close(a, b, tol=1e-6):
    assert abs(a - b) <= tol * max(1.0, abs(b)), (a, b)


def main():
    res = json.load(open(os.path.join(HERE, 'ch20_results.json')))
    ev = json.load(open(os.path.join(g.CACHE, 'evaluation.json')))
    E = pd.DataFrame(ev)
    E['h'] = E.h.astype(int)
    order = g.assets()
    d = dict(models=M, horizons=H, classes=CLS,
             assets=[s for _, s in order], kinds=[k for k, _ in order],
             col=dict(g.COL, navy=g.Navy, band=g.BandBlue, blue=g.MainBlue, red=g.IDAred, green=g.Forest,
                      orange=g.Orange, purple=g.Purple, teal=g.Teal, amber=g.Amber))

    # ---------------------------------------------------------------- 1. VOLARE: six assets of the data slide
    picks = {'stocks': ['JPM', 'NVDA'], 'futures': ['ES', 'CL'], 'forex': ['EURUSD', 'USDJPY']}
    vr = {}
    for k, syms in picks.items():
        for s in syms:
            a = S.load_asset(k, s)
            vol = (np.sqrt(252 * a.rv).rolling(5).mean() * 100).iloc[4::5]       # non-overlapping 5-day means
            vr[s] = dict(kind=k, dates=[f'{t:%Y-%m-%d}' for t in vol.index], v=r(vol.values, 1))
    d['volare'] = dict(picks=picks, series=vr, data=res['data'])

    # ---------------------------------------------------------------- 2. per-asset mean losses (QLIKE, MSE)
    ql = {h: [] for h in H}
    se = {h: [] for h in H}
    sub = {h: {p: [] for p in ('covid', 'apr2025', 'rest')} for h in H}
    for h in H:
        Eh = E[E.h == h].set_index('sym').loc[[s for _, s in order]]
        for _, row in Eh.iterrows():
            ql[h].append([row.ql[m] for m in M])
            se[h].append([row.se[m] for m in M])
            for p in sub[h]:
                x = row['sub'][p]
                sub[h][p].append(None if x is None else [x[m] for m in M])
    d['ql'] = {h: [r(v, 7) for v in ql[h]] for h in H}
    d['sub'] = {h: {p: [None if v is None else r(v, 7) for v in sub[h][p]] for p in sub[h]} for h in H}
    # check against the pooled results of the lecture
    for h in H:
        q = np.array(ql[h])
        rq = q / q[:, [0]]
        for j, m in enumerate(M):
            close(rq[:, j].mean(), res['pooled'][str(h)]['all'][m]['rq_mean'])
            close((q[:, j] / q[:, 1]).mean(), res['pooled'][str(h)]['all'][m]['rq_vs_loghar'])
        for p in ('covid', 'apr2025', 'rest'):
            rows = [v for v in sub[h][p] if v is not None]
            v = np.array(rows)
            close((v[:, M.index('Sig-LK')] / v[:, 0]).mean(), res['sub'][str(h)]['all'][p]['Sig-LK'])

    # ---------------------------------------------------------------- 3. MCS p-values per asset (QLIKE and MSE)
    pv = {'ql': {h: [] for h in H}, 'se': {h: [] for h in H}}
    for k, s in order:
        for h in H:
            fc = g.read_fc(k, s, h)
            y = fc.y.values
            QL = pd.DataFrame({m: S.qlike(y, fc[m].values) for m in M}, index=fc.index)
            SE = pd.DataFrame({m: S.mse(y, fc[m].values) for m in M}, index=fc.index)
            inc_q, p_q = S.mcs(QL, block=max(h, 10))
            inc_s, p_s = S.mcs(SE / SE.values.mean(), block=max(h, 10))
            row = E[(E.sym == s) & (E.h == h)].iloc[0]
            assert sorted(inc_q) == sorted(row.mcs_ql) and sorted(inc_s) == sorted(row.mcs_se), (s, h)
            pv['ql'][h].append([round(float(p_q[m]), 4) for m in M])
            pv['se'][h].append([round(float(p_s[m]), 4) for m in M])
    for h in H:
        P = np.array(pv['ql'][h])
        for j, m in enumerate(M):
            close((P[:, j] > 0.10).mean(), res['mcs'][str(h)]['ql'][m])
    d['mcs'] = pv

    # ---------------------------------------------------------------- 4. JPM in the COVID-19 crash, h = 1, 5, 22
    cov = {}
    for h in H:
        fc = g.read_fc('stocks', 'JPM', h).loc['2020-02-03':'2020-05-29']
        y = fc.y.values
        cov[h] = dict(dates=[f'{t:%Y-%m-%d}' for t in fc.index], y=r(np.sqrt(252 * y) * 100, 1),
                      f={m: r(np.sqrt(252 * fc[m].values) * 100, 1) for m in M},
                      ql={m: r(S.qlike(y, fc[m].values), 4) for m in M},
                      # origins where the raw HAR forecast was <= 0 and the positivity rule used the training mean
                      har_rep=[int(i) for i in np.where(fc['HAR'].values == fc['mu'].values)[0]])
    d['covid'] = cov

    # ---------------------------------------------------------------- 5. kernel weights at the origin 16 March 2020
    date, h, L = pd.Timestamp('2020-03-16'), 1, S.CFG['L']
    c_lect = res['validation'][f'stocks|Sig-LK|{h}']['c']
    stocks = S.symbols('stocks')
    grid = [float(2 ** e) for e in np.arange(-2, 3.01, 0.5)]                      # c = 0.25 ... 8
    assert c_lect in grid
    avg = {}
    jpm = {}
    paths = {}
    ess = {}
    saved = {}
    for N in (1, 2, 3):
        cfg = dict(S.CFG, DEPTH=N)
        W_all = {c: [] for c in grid}
        for s in stocks:
            a = S.load_asset('stocks', s)
            D = S.build_design(a, h, cfg)
            t = int(D['dates'].get_loc(date))
            tr = np.arange(t - h - cfg['W'] + 1, t - h + 1)
            inc = D['incr'][tr[0]:t + 1]
            sc = [1.0 if cn == 't' else 1.0 / (np.nanstd(inc[:, j]) * np.sqrt(L - 1)) for j, cn in enumerate(cfg['CHANNELS'])]
            scale = S.sig_scale(np.array(sc), N)
            for c in grid:
                w, dist = S.kernel_weights(D['sig'][tr], D['sig'][t], scale, c)
                W_all[c].append(w)
            if N == 3:
                wl, _ = S.kernel_weights(D['sig'][tr], D['sig'][t], scale, c_lect)
                f = os.path.join(g.CACHE, 'main', f'w_stocks_{s}_h{h}.csv')
                Wc = pd.read_csv(f, index_col=0, parse_dates=True)['2020-03-16'].dropna()
                assert np.allclose(Wc.values, wl, rtol=1e-6, atol=1e-12), s
                saved[s] = Wc
            if s == 'JPM':
                dates_tr = D['dates'][tr]
                jpm[N] = r(dist / np.median(dist), 5)                                # distances relative to their median
                P = D['path']
                win = lambda e: np.c_[P[e - L + 1:e + 1, 2] - P[e - L + 1, 2], P[e - L + 1:e + 1, 1]]
                near, far = tr[int(np.argmin(dist))], tr[int(np.argmax(dist))]
                paths[N] = dict(near=f'{D["dates"][near]:%Y-%m-%d}', far=f'{D["dates"][far]:%Y-%m-%d}',
                                p_near=r(win(near), 4), p_far=r(win(far), 4))
                if N == 3:
                    o = win(t)
                    paths['origin'] = r(o, 5)
                    close(S.levy_area(o), res['sig_demo']['2020-03-16']['levy'])
        avg[N] = [r(len(tr) * np.mean(W_all[c], axis=0), 3) for c in grid]
        ess[N] = [float(np.mean([1 / np.sum(w ** 2) for w in W_all[c]])) for c in grid]
    Wsv = pd.concat(saved, axis=1)
    close(float((1 / (Wsv ** 2).sum()).mean()), res['weights']['2020-03-16']['ess_avg'])
    close(float(Wsv.mean(axis=1).max() * len(Wsv)), res['weights']['2020-03-16']['max_ratio'])
    close(ess[3][grid.index(c_lect)], res['weights']['2020-03-16']['ess_avg'])
    rvbar = pd.concat([np.sqrt(252 * S.load_asset('stocks', s).rv).rename(s) for s in Wsv.columns], axis=1).mean(axis=1)
    rv = rvbar.reindex(Wsv.index)
    d['weights'] = dict(dates=[f'{t:%Y-%m-%d}' for t in dates_tr], c_lect=c_lect, grid=grid, avg=avg, ess_avg=ess,
                        dist_jpm=jpm, vol40=r(100 * rv.values, 2), paths=paths, n=int(len(dates_tr)),
                        corr=res['weights']['2020-03-16']['corr_w_logvol'],
                        levy_origin=res['sig_demo']['2020-03-16']['levy'])

    # ---------------------------------------------------------------- 8. second case study: signature lead-lag, SPY and BTC
    # per-day statistics from leadlag_case.py (data/market/intraday, public); the page recomputes means and NW t-statistics
    import leadlag_case as LL
    resll, C, A, dates = LL.compute()
    saved = json.load(open(LL.OUT_JSON))
    for m in LL.WINDOWS:
        close(resll['area'][str(m)]['t'], saved['area'][str(m)]['t'])
    close(resll['ccf_mean'][LL.LAGS.index(1)], saved['ccf_mean'][LL.LAGS.index(1)])
    d['leadlag'] = dict(lags=LL.LAGS, windows=LL.WINDOWS, years=[int(t.year) for t in dates],
                        start=resll['start'], end=resll['end'], nw_lag=resll['nw_lag'],
                        ccf=r(C, 5), area=r(A, 6))

    # ---------------------------------------------------------------- results quoted on the slides
    d['res'] = dict(pooled={h: {g_: {m: res['pooled'][str(h)][g_][m]['rq_mean'] for m in M} for g_ in ('all',) + tuple(CLS)}
                            for h in H},
                    ess_sigLK=res['ess'])

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 20 interactive page, exported by Quantlets/Ch_20/export_interactive.py.\n')
        f.write('window.CH20_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

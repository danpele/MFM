"""Export the inputs of the Chapter 14 interactive page (MFM/interactive/ch14_data.js).

No model is trained or run here. The page uses the forecasts that run_forecasts.py saved (ch14_returns_*.csv,
ch14_risk_*.csv, ch14_rv.csv) and the results files (ch14_results.json, ch14_inference.json, kmz_case.json,
ai_discovery_case.json, m6_case.json with the forecasts in m6_case_probs.json). Statistics that need a bootstrap (block-bootstrap intervals for R^2, the model confidence
set) are computed here with the chapter's own functions (mfm_tsfm.py) for a grid of evaluation windows, so the
full-sample values are those of the slides. The PIT intervals of GARCH-t and FHS use inference_tests.garch_grid,
the cheap GARCH refit of the chapter. No chart is drawn: the save functions are replaced by a no-op and the chart
and results files are checked to be unchanged.
"""
import glob
import hashlib
import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mfm_tsfm as M
import generate_all_charts as g
import inference_tests as it

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch14_data.js')
CHARTS = os.path.join(HERE, '..', '..', 'charts')
DAY0 = pd.Timestamp('2000-01-01')
YEARS = list(range(2016, 2026))                      # evaluation windows: from 1 January of each year, then the post-release window


def _noop(*a, **k):
    plt.close('all')


g.save_fig = it.save_fig = _noop


def hashes():
    files = sorted(glob.glob(os.path.join(CHARTS, 'ch14_*')) + glob.glob(os.path.join(HERE, '*.json')) + glob.glob(os.path.join(HERE, '*.csv')))
    return {f: hashlib.md5(open(f, 'rb').read()).hexdigest() for f in files}


def r(x, d=4):
    return np.round(np.asarray(x, float), d).tolist()


def raw(x):
    """Values exactly as stored in the forecast files."""
    return [float(v) for v in np.asarray(x, float)]


def days(idx):
    return [int((t - DAY0).days) for t in idx]


def ddays(idx):
    """Days since 2000-01-01 of the first date, then the gaps between consecutive dates."""
    v = days(idx)
    return [v[0]] + [b - a for a, b in zip(v[:-1], v[1:])]


def window_starts(idx):
    """First position of each evaluation window: 1 January of each year (or the first day of the sample) and 3 Nov 2025."""
    out = [int(max(0, np.searchsorted(idx, pd.Timestamp(f'{y}-01-01')))) for y in YEARS]
    return out + [int(np.searchsorted(idx, pd.Timestamp(M.POST_FROM)))]


def main():
    before = hashes()
    res = json.load(open(os.path.join(HERE, 'ch14_results.json')))
    inf = json.load(open(os.path.join(HERE, 'ch14_inference.json')))
    kmz = json.load(open(os.path.join(HERE, 'kmz_case.json')))
    ai = json.load(open(os.path.join(HERE, 'ai_discovery_case.json')))
    d = dict(assets=M.ASSETS, labels=M.LABELS, years=YEARS, post=M.POST_FROM, day0=str(DAY0.date()))

    # ---------------------------------------------------------------- 1. ACF: S&P 500 daily returns since 1990
    x = M.load_returns('sp500')
    d['acf'] = dict(r=r(x.values, 5), y0=int(x.index[0].year),
                    ystart={int(y): int(np.searchsorted(x.index, pd.Timestamp(f'{y}-01-01'))) for y in range(x.index[0].year, 2021)},
                    res=res['acf'])
    # patching: the last 512 returns (the same context as on the slide)
    d['patch'] = dict(r=raw(x.values[-512:]), last=str(x.index[-1].date()))

    # ---------------------------------------------------------------- 2. Test 1: R^2, bootstrap interval, DM, per window
    d['ret'] = {}
    for a in M.ASSETS:
        df = g.load_csv(f'ch14_returns_{a}.csv')
        y = df['y'].values
        st = window_starts(df.index)
        W = []
        for i0 in st:
            yy = y[i0:]
            row = {}
            for k in g.RET_MODELS:
                f = df[k].values[i0:]
                lo, hi = M.block_bootstrap_ci(lambda a_, b_: M.r2_oos(a_, b_), [yy, f], B=1000)
                dm = M.diebold_mariano((yy - f) ** 2, yy ** 2)
                row[k] = [100 * M.r2_oos(yy, f), 100 * lo, 100 * hi, dm['DM'], dm['p']]
            W.append(dict(i0=i0, n=int(len(yy)), start=str(df.index[i0].date()), m=row))
        full = W[0] if st[0] == 0 else None
        if full:
            for k in g.RET_MODELS:
                assert abs(full['m'][k][0] - res['ret'][a][k]['r2']) < 1e-9 and abs(full['m'][k][1] - res['ret'][a][k]['lo']) < 1e-9
        d['ret'][a] = dict(win=W, end=str(df.index[-1].date()), sd=float(y.std()))
    d['ret_models'] = list(g.RET_MODELS)
    d['ret_lbl'] = g.RET_MODELS
    d['ret_col'] = g.RET_COL

    # ---------------------------------------------------------------- 3. Test 2: realised variance and the eight forecasts
    rv = g.load_csv('ch14_rv.csv')
    d['rv'] = dict(ddays=ddays(rv.index), RV=raw(rv['RV']), models=g.RV_MODELS, lbl=g.RV_LBL, col=g.RV_COL,
                   f={m: raw(rv[m]) for m in g.RV_MODELS}, res={m: res['rv'][m] for m in g.RV_MODELS},
                   n=res['rv']['n'], n_post=res['rv']['n_post'], peak=res['rv_path'])

    # ---------------------------------------------------------------- 4. Test 3: hits, VaR paths, conformal inputs, MCS per window
    d['risk'] = {}
    for a in M.ASSETS:
        rk = g.load_csv(f'ch14_risk_{a}.csv')
        L = -rk['y'].values
        st = window_starts(rk.index)
        hits = {m: ''.join('1' if v else '0' for v in (L > rk[f'{m}|VaR1'].values)) for m in g.RISK_MODELS + ['bolt-raw']}
        for m in g.RISK_MODELS + ['bolt-raw']:
            assert hits[m].count('1') == res['risk'][a][m]['x'], (a, m)
        # FZ0 losses of (VaR 2.5%, ES 2.5%), MCS p-values and DM against FHS for each window (seeded as in the chapter)
        F = pd.DataFrame({m: M.fz0(L, rk[f'{m}|VaR2.5'].values, np.maximum(rk[f'{m}|ES2.5'].values, 1e-6)) for m in g.RISK_MODELS})
        mc = []
        for i0 in st:
            Fw = F.iloc[i0:]
            p = M.mcs(Fw)
            dm = {m: M.diebold_mariano(Fw[m], Fw['FHS']) for m in g.RISK_MODELS if m != 'FHS'}
            mc.append(dict(i0=i0, n=int(len(Fw)), start=str(rk.index[i0].date()),
                           p={m: float(p[m]) for m in g.RISK_MODELS}, fz0={m: float(Fw[m].mean()) for m in g.RISK_MODELS},
                           dm={m: [v['DM'], v['p']] for m, v in dm.items()}))
        if st[0] == 0:
            for m in g.RISK_MODELS:
                assert abs(mc[0]['p'][m] - res['risk'][a][m]['mcs']) < 1e-12, (a, m)
        # y and the Chronos-2 1% quantile exactly as stored (the conformal recursion compares them); FHS VaR 1% to 3 decimals
        e = dict(ddays=ddays(rk.index), y=raw(rk['y']), hits=hits, starts=st, mcs=mc, n=int(len(rk)),
                 fhs=r(rk['FHS|VaR1'], 3), q1=raw(-rk['C2-raw|VaR1']))
        if a == 'sp500':   # VaR 1% paths for the COVID-19 block (breaches are taken from `hits`); C2-raw is -q1
            e['var'] = {m: r(rk[f'{m}|VaR1'], 3) for m in g.RISK_MODELS if m != 'C2-raw'}
        d['risk'][a] = e
    d['risk_models'] = g.RISK_MODELS
    d['risk_lbl'] = g.RISK_LBL
    d['risk_col'] = g.RISK_COL
    d['risk_res'] = {a: {m: {k: res['risk'][a][m][k] for k in ('x', 'rate', 'p_uc')} for m in g.RISK_MODELS} for a in M.ASSETS}
    d['covid'] = res['covid']
    d['conf_res'] = {a: {m: {k: inf['conf'][a][m][k] for k in ('x', 'rate', 'var', 'exp', 'p_cc', 'p_dq')} for m in ('FHS', 'C2-raw', 'C2-SCP', 'C2-ACI')}
                     for a in M.ASSETS}
    for a in M.ASSETS:
        d['conf_res'][a]['inf_005'] = inf['conf'][a]['inf_005']

    # ---------------------------------------------------------------- 5. PIT: interval of the 22 on the Chronos-2 grid, per day
    LV = it.LV
    d['pit'] = {}
    for a in M.ASSETS:
        rk = g.load_csv(f'ch14_risk_{a}.csv')
        dfr = g.load_csv(f'ch14_returns_{a}.csv').loc[rk.index]
        Qc = dfr[[f'chronos2_q{u:.2f}' for u in LV]].values
        y, (_, Qt), (_, Qf) = it.garch_grid(a, rk.index)
        e = {}
        for nm, Q in (('C2', Qc), ('GARCH-t', Qt), ('FHS', Qf)):
            u, lo, hi = it.pit_grid(y, Q)
            k = np.full(len(y), -1)
            fin = np.isfinite(u)
            k[fin] = np.clip(np.searchsorted(LV, u[fin], side='right'), 0, len(LV))
            k[lo] = 0
            k[hi] = len(LV)
            assert (k >= 0).all()
            c, w = it.bins_of(u, lo, hi)
            assert np.array_equal(np.bincount(k, minlength=len(LV) + 1), c)
            dens = c / (len(y) * w)
            ref = np.array(inf['calib'][a][nm]['dens'])
            e[nm] = ''.join(chr(97 + int(v)) for v in k)
            e[nm + '_maxdiff'] = float(np.max(np.abs(dens - ref)))
        e['starts'] = window_starts(rk.index)
        e['berk'] = {nm: inf['calib'][a][nm]['berk'] for nm in ('C2', 'GARCH-t', 'FHS')}
        d['pit'][a] = e
    d['pit_lv'] = list(LV)

    # ---------------------------------------------------------------- 6. case study and AI mini-case
    d['kmz'] = dict(c=kmz['c'], logz=[-3, -2, -1, 0, 1, 2, 3], curve=kmz['curve'], lin_sr=kmz['table']['lin3']['sr'],
                    n=kmz['n'], start=kmz['start'], end=kmz['end'], draws=kmz['draws'], table=kmz['table'])
    d['ai'] = ai
    # second case study (m6_case.py): realised fractional quintiles and the saved forecasts of each period
    m6 = json.load(open(os.path.join(HERE, 'm6_case.json')))
    pr = json.load(open(os.path.join(HERE, 'm6_case_probs.json')))
    per = pr['periods']
    # compact: q in fifths (with 19 assets every q_k is a multiple of 0.2), probabilities in units of 1e-4
    q5 = np.rint(5 * np.array([p_['q'] for p_ in per])).astype(int)
    assert np.abs(q5 / 5 - np.array([p_['q'] for p_ in per])).max() < 1e-3
    fi = {mdl: np.rint(10000 * np.array([p_['f'][mdl] for p_ in per])).astype(int) for mdl in ('HM', 'VOL', 'NN')}
    q = q5 / 5
    rU = ((np.cumsum(q, 2) - np.cumsum(np.full_like(q, 0.2), 2)) ** 2).mean(2).mean(1)
    for mdl in ('HM', 'VOL', 'NN'):
        f_ = fi[mdl] / 10000
        rm = ((np.cumsum(q, 2) - np.cumsum(f_, 2)) ** 2).mean(2).mean(1)
        for key, sel in (('m6', [p_['m6'] for p_ in per]), ('ext', [p_['ext'] for p_ in per])):
            gain = 100 * (1 - rm[sel].mean() / rU[sel].mean())
            assert abs(gain - m6[key][mdl]['gain']) < 0.02, (mdl, key, gain)
    d['m6'] = dict(assets=pr['assets'], start=[p_['start'] for p_ in per], end=[p_['end'] for p_ in per],
                   m6=[p_['m6'] for p_ in per], ext=[p_['ext'] for p_ in per], q5=q5.tolist(),
                   f10k={mdl: fi[mdl].tolist() for mdl in ('HM', 'VOL', 'NN')},
                   res={k: m6[k] for k in ('m6', 'ext')}, paper=m6['paper'], first=m6['m6_first'])

    after = hashes()
    assert before == after, 'chart or results files changed'
    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 14 interactive page, exported by Quantlets/Ch_14/export_interactive.py.\n')
        f.write('window.CH14_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
    print('PIT max |dens - ch14_inference.json|:', {a: {nm: d['pit'][a][nm + '_maxdiff'] for nm in ('C2', 'GARCH-t', 'FHS')} for a in M.ASSETS})


if __name__ == '__main__':
    main()

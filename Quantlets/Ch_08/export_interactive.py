"""Export the inputs of the Chapter 8 interactive page (MFM/interactive/ch8_data.js).

Uses the forecasts and test functions of generate_all_charts.py and mfm_data.py, so the page starts from the same
numbers as the slides. No chart or results file of the chapter is written: save_fig and plt.savefig are replaced by
no-ops, and ch8_results.json is only read. EUR/RON is loaded as in the chapter (BNR reference rate, mfm_data.read_reference_rate).
Run with TMPDIR set to a scratch folder: the forecast cache of mfm_data.get_forecasts goes there.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch8_data.js')

import matplotlib                                   # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                     # noqa: E402

import mfm_data as M                                # noqa: E402


import generate_all_charts as g                     # noqa: E402


def _no_save(name):
    plt.close('all')


g.save_fig = _no_save
plt.savefig = lambda *a, **k: None

LEV = {'VaR1': 0.01, 'VaR2.5': 0.025, 'VaR5': 0.05}


def bp(x):
    """Decimal losses or forecasts as integers in basis points (1 bp = 0.01%); NaN -> None."""
    a = np.asarray(x, float)
    return [None if not np.isfinite(v) else int(round(v * 1e4)) for v in a]


def r(x, d=6):
    a = np.round(np.asarray(x, float), d)
    return [None if not np.isfinite(v) else float(v) for v in a]


def calendar(idx):
    return dict(d0=f'{idx[0]:%Y-%m-%d}', gaps=np.diff(idx.values.astype('datetime64[D]').astype(np.int64)).tolist())


def runs(flag):
    """Start and end positions (inclusive) of the runs of True."""
    f = np.r_[False, np.asarray(flag, bool), False].astype(int)
    d = np.diff(f)
    return [[int(a), int(b) - 1] for a, b in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1))]


def main():
    R = json.load(open(os.path.join(HERE, 'ch8_results.json')))
    d = dict(assets=M.ASSETS, labels=M.LABELS, models=M.MODELS, mcol=g.MCOL)

    # ------------------------------------------------------------------ forecasts, losses, hits
    d['cal'], d['L'], d['first'], d['hits'], d['evt'] = {}, {}, {}, {}, {}
    d['es'] = {}
    for n in M.ASSETS:
        F = g.fc(n)[0]
        cal, losses = g.canonical_sample(n)
        assert len(cal) == R['assets'][n]['T'], (n, len(cal))
        d['cal'][n] = calendar(cal)
        d['L'][n] = bp(losses.values)
        avail = F['GARCH-t']['VaR1'].notna().values
        d['first'][n] = int(np.argmax(avail))
        assert int((~avail).sum()) == R['assets'][n]['unavailable_days'], n
        d['hits'][n] = {}
        d['es'][n] = {}
        for m in M.MODELS:
            df = F[m]
            d['hits'][n][m] = {k: np.flatnonzero((df['L'] > df[k]).values).tolist() for k in LEV}
            h = (df['L'] > df['VaR2.5']).values
            d['es'][n][m] = dict(term=r((df['L'] / df['ES2.5']).values[h], 5),
                                 res=r(((df['L'] - df['ES2.5']) / df['scale']).values[h], 4))
        d['evt'][n] = {k: bp(F['GARCH-EVT'][k].values) for k in LEV}
        # checks against the lecture results
        for m in M.MODELS:
            rec = R['var99'][f'{n}|{m}']
            if rec['status'] == 'computed':
                assert len(d['hits'][n][m]['VaR1']) == rec['result']['x'], (n, m)
    Fs = g.fc('sp500')[0]
    d['sp_var'] = {m: bp(Fs[m]['VaR1'].values) for m in ('HS', 'GARCH-t')}
    assert len(d['hits']['sp500']['HS']['VaR1']) == R['sp500_var']['HS']

    # ------------------------------------------------------------------ results of the lecture (tables, p-values)
    d['var99'] = {k: (v['result'] if v['status'] == 'computed' else None) for k, v in R['var99'].items()}
    d['dq'] = {k: (v['result']['p'] if v['status'] == 'computed' else None) for k, v in R['dq'].items()}
    d['esres'] = {k: ({c: v['result'][c] for c in ('MF_mean', 'MF_t', 'MF_p', 'Z2', 'p2', 'U_ES', 'p_U', 'n_hit')}
                      if v['status'] == 'computed' else None) for k, v in R['es'].items()}
    d['mcs'] = {n: (R['fz'][n]['result']['mcs'] if R['fz'][n]['status'] == 'computed' else None) for n in M.ASSETS}
    d['traffic'], d['z2r'], d['mf'] = R['traffic'], R['z2_rolling'], R['mf_resid']
    d['elicit'], d['pof'], d['kup'] = R['elicit'], R['pof_power'], R['kupiec_curve']
    d['worked'] = {k: R['worked'][k] for k in ('kupiec_2008', 'chr_hs')}

    # ------------------------------------------------------------------ FZ0 losses
    d['fz'] = {}
    for n in ('sp500', 'bet'):
        Lf = g.fz_losses(n)
        years = Lf.index.year
        d['fz'][n] = dict(years=sorted(set(years.tolist())),
                          sum={m: r(Lf[m].groupby(years).sum().values, 6) for m in M.MODELS},
                          cnt=Lf[M.MODELS[0]].groupby(years).size().tolist())
        means = Lf.mean()
        for m in M.MODELS:
            assert abs(means[m] - R['fz'][n]['result']['mean'][m]) < 1e-9, (n, m)
    Lf = g.fz_losses('sp500')
    e5 = lambda x: [int(v) for v in np.round(np.asarray(x, float) * 1e5)]        # units of 1e-5
    d['fz_sp'] = dict(fhs=e5(Lf['FHS'].values), diff={m: e5((Lf[m] - Lf['FHS']).values) for m in M.MODELS if m != 'FHS'})

    # ------------------------------------------------------------------ conformal VaR (S&P 500 path) and regimes
    rr = M.load_returns('sp500')
    sd = rr.rolling(250).std().shift(1)
    c = M.conformal_var(rr, a=0.01)
    i0 = rr.index.get_loc(c.index[0])                    # first ACI day
    w1 = rr.index.get_loc(rr.loc[:'2021-06-30'].index[-1])
    k0 = i0 - 250                                         # first calibration score
    s = (-rr / sd).values
    d['conf'] = dict(cal=calendar(rr.index[k0:w1 + 1]), i0=i0 - k0, s=r(s[k0:w1 + 1], 6), sd=r(100 * sd.values[k0:w1 + 1], 5),
                     win=['2019-07-01', '2021-06-30'], num=R['conf_path'])
    win = c.loc['2019-07-01':'2021-06-30'].index
    d['conf']['garch'] = {k: bp(Fs['GARCH-t'][k].loc[win].values) for k in LEV}
    d['conf']['w0'] = f'{win[0]:%Y-%m-%d}'
    d['reg'] = {}
    for n in M.ASSETS:
        rn = M.load_returns(n)
        cn = M.conformal_var(rn, a=0.05).loc[g.fc(n)[0]['HS'].index[0]:]
        assert cn.index.equals(g.canonical_sample(n)[0])
        hs, ha = (cn['L'] > cn['VaR_split']).values, (cn['L'] > cn['VaR_aci']).values
        d['reg'][n] = dict(split=np.flatnonzero(hs).tolist(), aci=np.flatnonzero(ha).tolist(),
                           crisis={f'{q:.2f}': runs(M.regimes(rn, cn.index, q=q).values) for q in (0.75, 0.80, 0.85, 0.90, 0.95)})
        cf = R['conformal5'][n]
        assert abs(hs.mean() - cf['split'][0]) < 1e-12 and abs(ha.mean() - cf['aci'][0]) < 1e-12, n

    # ------------------------------------------------------------------ case study: Table 3 of Bayer and Dimitriadis (2022)
    d['bd'] = dict(windows=list(g.BD_WINDOWS), refits=list(g.BD_REFITS), table=g.BD_TABLE3)

    js = json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null')
    with open(OUT, 'w') as fh:
        fh.write('// Inputs of the Chapter 8 interactive page, exported by Quantlets/Ch_08/export_interactive.py.\n')
        fh.write('window.CH8_DATA = ' + js + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

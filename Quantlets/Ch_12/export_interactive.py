"""Export the inputs of the Chapter 12 interactive page (MFM/interactive/ch12_data.js).

Calls the functions of generate_all_charts.py, so the page starts from the same numbers as the slides.
The chart files, ch12_results.json and the CSV files of the chapter are not rewritten: save_fig and
DataFrame.to_csv are neutralised while the chapter functions run. The case-study bounds and the daily
risk-free rate are read by the chapter's own loaders (generate_all_charts.bck_data: BCK_URL, the replication
package on GitHub, and ff_rf_daily, the Kenneth French Data Library), as for the slides.
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import generate_all_charts as g
from option_tools import svi_fit, delta_hedge

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch12_data.js')


def no_save(name):
    plt.close('all')


g.save_fig = no_save


def r(x, d=6):
    a = np.round(np.asarray(x, float), d)
    return [None if not np.isfinite(v) else float(v) for v in a]


def ints(x, k):
    """Values times 10^k as integers (None for missing): compact series."""
    a = np.asarray(x, float)
    return [None if not np.isfinite(v) else int(round(v * 10 ** k)) for v in a]


def ddays(idx):
    """First date and the day differences: compact daily calendar."""
    d = pd.DatetimeIndex(idx).normalize()
    n = (d - pd.Timestamp('1970-01-01')).days.values
    return dict(start=str(d[0].date()), diff=np.diff(n).astype(int).tolist())


def hist_density(e, bins):
    h, _ = np.histogram(e, bins=bins, density=True)
    return r(h, 4)


def main():
    res = json.load(open(os.path.join(HERE, 'ch12_results.json')))
    d = {}

    # delta hedging: the 20,000 paths of the chapter, eight rebalancing frequencies
    errs, prem = g.hedge_errors()
    bins = np.linspace(-4, 4, 121)
    Ns = sorted(errs)
    d['hedge'] = dict(premium=prem, N=Ns, bins=[-4, 4, 120], dens={str(n): hist_density(errs[n], bins) for n in Ns},
                      sd={str(n): float(errs[n].std()) for n in Ns}, mean={str(n): float(errs[n].mean()) for n in Ns},
                      q01={str(n): float(np.quantile(errs[n], 0.01)) for n in Ns}, slope=res['hedge']['slope'], **g.HEDGE)

    # selling volatility at 20%: realised volatility 10% to 30%, same paths seed as the slide
    h = g.HEDGE
    bins = np.linspace(-6, 6, 121)
    mm = {}
    for sr in range(10, 31):
        paths = g.gbm_paths(h['S0'], h['mu'], sr / 100, h['T'], 63, h['npath'], seed=11)
        e = delta_hedge(paths, h['K'], h['T'], h['r'], 0.20, 63)
        mm[str(sr)] = dict(dens=hist_density(e, bins), mean=float(e.mean()), sd=float(e.std()), win=float((e > 0).mean()))
    d['mismatch'] = dict(bins=[-6, 6, 120], vega=res['mismatch']['vega'], premium=res['mismatch']['premium'], runs=mm)

    # smiles: the historical S&P 500 smile (the Merton and Heston smiles are recomputed in the browser)
    S, T = 100.0, 21 / 252
    Ks = np.linspace(80, 120, 41)
    lr = np.log(g.load_close('sp500'))
    R = (lr.shift(-21) - lr).dropna().values
    ST = S * np.exp(R) / np.mean(np.exp(R))
    emp = lambda K, kind: np.mean(np.maximum(ST - K, 0)) if kind == 'call' else np.mean(np.maximum(K - ST, 0))
    d['smile'] = dict(K=r(Ks / S, 4), emp=r(100 * g.smile_from_prices(S, Ks, T, emp), 4), T=T, nR=int(len(R)),
                      skew=res['smile']['skew_R'], kurt=res['smile']['kurt_R'])

    # Bitcoin surface: quotes and SVI fits of every expiry
    orig_csv = pd.DataFrame.to_csv
    pd.DataFrame.to_csv = lambda *a, **k: None
    try:
        c, tab, t0 = g.btc_surface()
    finally:
        pd.DataFrame.to_csv = orig_csv
    P = ['a', 'b', 'rho', 'm', 's']
    exps = []
    for e, f in tab.iterrows():
        q = c[c['expiry'] == e].sort_values('k')
        exps.append(dict(date=str(pd.Timestamp(e).date()), days=float(f['days']), T=float(f['T']), F=float(f['F']),
                         p=[float(f[x]) for x in P], rmse=float(f['rmse_iv']), atm=float(f['atm']),
                         k=r(q['k'].values, 5), iv=r(q['mark_iv'].values, 3)))
    d['btc'] = dict(snapshot=str(t0), chosen=res['btc_expiries'], exps=exps)

    # risk-neutral density: same bootstrap as btc_rnd (seed, resampling rule, B = 300), the refitted parameters
    e = g.pick(tab, 30)
    q = c[c['expiry'] == e]
    kq, wq = q['k'].values, q['w'].values
    rng = np.random.default_rng(g.SEED)
    boot = []
    while len(boot) < 300:
        i = rng.integers(0, len(kq), len(kq))
        if len(np.unique(kq[i])) < 6:
            continue
        pb = svi_fit(kq[i], wq[i])
        boot.append([float(pb[x]) for x in P])
    f = tab.loc[e]
    d['rnd'] = dict(expiry=str(pd.Timestamp(e).date()), days=float(f['days']), F=float(f['F']), T=float(f['T']),
                    p=[float(f[x]) for x in P], boot=[r(b, 8) for b in boot], kf_min=float(np.exp(kq.min())),
                    kf_max=float(np.exp(kq.max())), n_quotes=int(len(kq)))

    # VIX history
    v = g.load_close('vix')
    d['vix'] = dict(dates=ddays(v.index), v=ints(v.values, 2), peaks=res['vix']['peaks'])

    # variance risk premium and Mincer-Zarnowitz: realised volatility of the next 21 days on the VRP calendar,
    # with the 21 earlier values that give the past realised variance
    vd = g.vrp_sp500()
    px = pd.concat([g.load_close('sp500'), g.load_close('vix')], axis=1, join='inner').dropna()
    lr2 = np.log(px['sp500']).diff()
    rv = 252 / 21 * (lr2 ** 2).rolling(21).sum().shift(-21) * 1e4
    i0 = rv.index.get_loc(vd.index[0])
    rv_ext = rv.iloc[i0 - 21:i0 + len(vd)]
    assert np.allclose(rv_ext.values[21:], vd['rv'].values) and np.allclose(rv_ext.values[:len(vd)], vd['rv_past'].values)
    d['vrp'] = dict(dates=ddays(vd.index), rv=ints(np.sqrt(rv_ext.values), 3))

    # case study: authors' daily bounds and the S&P 500 excess returns of the course data
    bd = g.bck_data()
    x = bd.loc[g.BCK_START:]
    d['bck'] = dict(dates=ddays(bd.index), m1=ints(bd['lb_m_1'], 2), cyl1=ints(bd['lb_cylr_1'], 2), start=g.BCK_START,
                    i0=int(bd.index.get_loc(x.index[0])),
                    f={str(hh): ints(x[f'f{hh}'], 2) for hh in g.BCK_H}, m={str(hh): ints(x[f'lb_m_{hh}'], 2) for hh in g.BCK_H},
                    paper=g.BCK_TABLE1_RET)

    with open(OUT, 'w') as fh:
        fh.write('// Inputs of the Chapter 12 interactive page, exported by Quantlets/Ch_12/export_interactive.py.\n')
        fh.write('window.CH12_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

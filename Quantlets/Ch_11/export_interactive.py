"""Export the inputs of the Chapter 11 interactive page (MFM/interactive/ch11_data.js).

Uses the data loaders, the model functions (ct_models.py) and the random-number sequences of generate_all_charts.py,
so the page starts from the same numbers as the slides. Nothing is saved to charts/ or to ch11_results.json.
"""
import json
import os

import numpy as np

import generate_all_charts as g
from ct_models import (scaled_random_walk, bm_paths, gbm_simulate_returns, acf)
from mfm_data import read_fred, load_spy_5m

g.save_fig = lambda name: None          # never rewrite slide charts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch11_data.js')
SEED, DT = g.SEED, g.DT


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def day_gaps(idx):
    """First date and the gaps in calendar days between consecutive observations (compact date encoding)."""
    d = np.asarray(idx.values, dtype='datetime64[D]').astype(np.int64)
    return str(idx[0].date()), np.diff(d).astype(int).tolist()


def donsker(res):
    """Same random sequence as fig_donsker: the three walks of the left panel, then the counts of max S_k per n."""
    rng = np.random.default_rng(SEED)
    walks = {}
    for n in [5, 50, 5000]:
        _, W = scaled_random_walk(n, 1, rng)
        steps = np.diff(np.round(W[0] * np.sqrt(n)).astype(int))
        walks[str(n)] = ''.join('1' if s > 0 else '0' for s in steps)
    ns, M, counts = [5, 10, 20, 50, 100, 200, 500, 1000, 2000], 20000, {}
    for n in ns:
        _, W = scaled_random_walk(n, M, rng)
        mx = np.round(W.max(axis=1) * np.sqrt(n)).astype(int)       # max of S_k, an integer >= 0
        counts[str(n)] = np.bincount(mx).tolist()
        p = float(np.mean(W.max(axis=1) > 1.0))
        assert abs(p - res['donsker']['p'][ns.index(n)]) < 1e-12, (n, p)
    return dict(walks=walks, ns=ns, M=M, counts=counts)


def qv_powers(res):
    """Same Brownian path as fig_quadratic_variation (2^16 steps): sums of |dW|^p on the coarser grids."""
    rng = np.random.default_rng(SEED + 2)
    N = 2 ** 16
    _, W = bm_paths(1, N, 1.0, rng)
    w = W[0]
    ns = [2 ** k for k in range(4, 17)]
    ps = [round(x, 2) for x in np.arange(0.5, 3.001, 0.1)]
    S = {f'{p:.1f}': [float(np.sum(np.abs(np.diff(w[::N // n])) ** p)) for n in ns] for p in ps}
    assert np.allclose(S['2.0'], [res['qv']['qv'][str(n)] for n in ns])
    assert np.allclose(S['1.0'], [res['qv']['tv'][str(n)] for n in ns])
    return dict(ns=ns, ps=[f'{p:.1f}' for p in ps], sums={k: r(v, 6) for k, v in S.items()})


def gbm_band(res):
    """Same random sequence as fig_gbm_vs_data: 200 GBM samples; ACF bands of |r|, r^2 and r."""
    gs = res['gbm']['sp500']
    n = len(g.rets['sp500'])
    lags = np.arange(1, 51)
    rng = np.random.default_rng(SEED + 7)
    A = {'abs': [], 'sq': [], 'raw': []}
    for _ in range(200):
        x = gbm_simulate_returns(gs['m'], gs['sigma'], n, DT, rng)
        A['abs'].append(acf(np.abs(x), lags))
        A['sq'].append(acf(x ** 2, lags))
        A['raw'].append(acf(x, lags))
    out = {}
    for k, v in A.items():
        lo, hi = np.quantile(np.array(v), [0.025, 0.975], axis=0)
        out[k] = dict(lo=r(lo, 5), hi=r(hi, 5))
    assert abs(float(np.max(np.quantile(np.array(A['abs']), 0.975, axis=0))) - res['gbm_data']['band_hi']) < 1e-12
    return out


def models(res):
    """Same random sequence as fig_models_vs_data: statistics of each of the 100 simulations per model."""
    rng = np.random.default_rng(SEED + 11)
    n = len(g.rets['sp500'])
    hp = res['heston']
    hpp = dict(hp, theta=hp['theta_p'])
    me = res['merton']['sp500']
    S = {'GBM': g.simulate_stats('GBM', res['gbm']['sp500'], n, DT, 100, rng),
         'Merton': g.simulate_stats('Merton', me, n, DT, 100, rng),
         'Heston': g.simulate_stats('Heston', hpp, n, DT, 100, rng, mu=res['gbm']['sp500']['mu'])}
    out = {}
    for m, s in S.items():
        out[m] = dict(exkurt=r([x['exkurt'] for x in s], 4), hill=r([x['hill'] for x in s], 4),
                      skew=r([x['skew'] for x in s], 4), acf=[r(x['acf_abs'], 4) for x in s])
        med = float(np.median([x['exkurt'] for x in s]))
        assert abs(med - res['compare'][m]['exkurt']['med']) < 1e-9, (m, med)
    return out


def main():
    res = json.load(open(os.path.join(HERE, 'ch11_results.json')))
    d = {}
    # daily log returns: S&P 500 (with dates) and Bitcoin
    sp = g.rets['sp500']
    start, gaps = day_gaps(sp.index)
    d['sp'] = dict(start=start, gaps=gaps, r=r(sp.values, 7))
    d['btc'] = dict(r=r(g.rets['btc'].values, 7))
    d['gbm'] = {k: {c: res['gbm'][k][c] for c in ('n', 'years', 'sigma', 'm', 'mu', 'se_m')} for k in ('sp500', 'btc')}
    d['donsker'] = donsker(res)
    d['donsker']['p'] = res['donsker']['p']
    d['donsker']['exact'] = res['donsker']['exact']
    d['qv'] = qv_powers(res)
    d['qv']['crises'] = res['qv']['crises']
    d['band'] = gbm_band(res)
    d['gbm_data'] = res['gbm_data']
    d['drift'] = res['drift']
    # 3-month Treasury bill rate (FRED, DTB3), in % with two decimals as published
    tb = read_fred('DTB3')
    start, gaps = day_gaps(tb.index)
    d['tb'] = dict(start=start, gaps=gaps, y=r(tb.values, 2))
    d['vasicek'] = {k: res['vasicek'][k] for k in ('1954-2026', '1954-1979', '1980-2007', '2008-2026')}
    d['merton'] = {k: {c: res['merton'][k][c] for c in ('m', 'sigma', 'lam', 'mu_j', 's_j', 'loglik', 'll_gbm', 'jump_share', 'data_exkurt', 'data_skew', 'moments')}
                   for k in ('sp500', 'btc')}
    d['models'] = models(res)
    d['compare'] = res['compare']
    # case study: daily log sigma of SPY from the bipower variation of 5-minute returns (as in rough_vol_spy)
    r5 = load_spy_5m()
    bv = r5.groupby(r5.index.date).apply(lambda x: np.pi / 2 * np.sum(np.abs(x.values[1:]) * np.abs(x.values[:-1])))
    x = 0.5 * np.log(bv.values)
    assert len(x) == res['rough']['n']
    assert abs(g.alpha_ols(x) - res['rough']['alpha_ols']) < 1e-12
    rough = {k: res['rough'][k] for k in ('n', 'start', 'end', 'H', 'alpha_ols', 'alpha_nlls', 'beta_cau', 'beta_cau_star', 'c_star',
                                          'ou_lambda', 'ou_c', 'half_life_ou', 'rho100')}
    rv = g.rough_vol_spy()
    rough['nlls_m15'] = r(rv['nlls_m15'], 8)
    rough['x'] = r(x, 6)
    d['rough'] = rough

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 11 interactive page, exported by Quantlets/Ch_11/export_interactive.py.\n')
        f.write('window.CH11_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

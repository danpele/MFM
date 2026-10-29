"""Export the inputs of the Chapter 1 interactive page (MFM/interactive/ch1_data.js).

Uses the data and the functions of generate_all_charts.py, so the page starts from the same numbers as the slides.
Prices are exported as they are stored (no rounding); the page computes the returns from them.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

import generate_all_charts as g

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch1_data.js')
EPOCH = pd.Timestamp('1970-01-01')


def days(idx):
    return ((idx - EPOCH) // pd.Timedelta('1D')).astype(int).tolist()


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def ohlc_day(seed=6, n=390, sigma_day=0.012, gap=0.006):
    """The simulated trading day of the slide (same generator, seed and parameters as the chapter chart)."""
    rng = np.random.default_rng(seed)
    return gap + np.cumsum(np.r_[0, rng.standard_normal(n - 1) * sigma_day / np.sqrt(n)])


def main():
    A = g.ASSETS
    d = dict(assets=A, labels={a: g.LABELS[a].replace(' (Romania)', '') for a in A}, colors=g.COLORS,
             periods={a: float(g.PERIODS[a]) for a in A})

    # daily closes of the five markets (returns are computed in the page)
    d['mk'] = {a: dict(t=days(g.closes[a].index), c=g.closes[a].values.tolist()) for a in A}
    for a in A:      # the page uses ln(c_t / c_{t-1}); check against the chapter returns
        c = np.asarray(d['mk'][a]['c'])
        assert np.allclose(np.diff(np.log(c)), g.rets[a].values, atol=1e-13)

    # volume of the S&P 500 and Bitcoin (same dates as the closes)
    d['vol'] = {}
    for a in ('sp500', 'btc'):
        v = g.load_data(a)['Volume'].reindex(g.closes[a].index)
        d['vol'][a] = [None if (not np.isfinite(x) or x <= 0) else int(x) for x in v.values]

    # Student-t fitted to the standardised returns (histogram slide)
    d['tfit'] = {}
    for a in A:
        z = (g.rets[a] - g.rets[a].mean()) / g.rets[a].std()
        nu, loc, sc = stats.t.fit(z)
        d['tfit'][a] = dict(nu=float(nu), loc=float(loc), scale=float(sc))

    # S&P 500 OHLC from 2008 (volatility estimators)
    o = g.spx_ohlc.loc['2008-01-01':]
    d['ohlc'] = dict(t=days(o.index), O=o['Open'].tolist(), H=o['High'].tolist(), L=o['Low'].tolist(), C=o['Close'].tolist())
    d['ohlc_day'] = r(ohlc_day(), 8)

    # case study: VIX on the S&P 500 days from 2000 and the fitted kernel parameters
    vix = g.read_market('VIX.INDX')['close'] / 100
    spx = g.closes['sp500']
    full = g.read_market('GSPC.INDX')['close']
    assert np.allclose(full.reindex(spx.index).values, spx.values)
    vv = vix.reindex(spx.index).loc[g.PDV_TRAIN[0]:]
    vv = vv[vv.notna()]
    pos = spx.index.get_indexer(vv.index)
    assert pos.min() >= g.PDV_LAGS
    params = pd.read_csv(os.path.join(HERE, 'ch1_pdv_parameters.csv'), index_col=0).iloc[:, 0]
    df = g.pdv_data()
    fit = pd.Series(g.pdv_predict(df.iloc[:, :g.PDV_LAGS].values, params.values), index=df.index)
    assert (df.index[df.index >= g.PDV_TRAIN[0]] == vv.index).all()
    d['pdv'] = dict(pos=pos.tolist(), vix=vv.values.tolist(), params=params.to_dict(), table3=list(g.PDV_TABLE3_VIX),
                    train=list(g.PDV_TRAIN), test=list(g.PDV_TEST), lags=g.PDV_LAGS)

    # numbers of the chapter tables used in the readouts
    li = pd.read_csv(os.path.join(HERE, 'ch1_long_memory.csv'), index_col=0)
    hi = pd.read_csv(os.path.join(HERE, 'ch1_hill_inference.csv'), index_col=0)
    ft = pd.read_csv(os.path.join(HERE, 'ch1_fact_tests.csv'))
    sc = pd.read_csv(os.path.join(HERE, 'ch1_pdv_scores.csv'), index_col=0)
    lab = {g.LABELS[a]: a for a in A}
    d['res'] = dict(d_lw={lab[k]: float(v) for k, v in li['d_lw'].items()},
                    hill_se_block={lab[k]: float(v) for k, v in hi['se_block'].items()},
                    gainloss_ci={lab[row.asset]: [row.lo, row.hi] for row in ft[ft.fact == 'gainloss_delta_pct'].itertuples()},
                    dd_p={lab[row.asset]: row.z for row in ft[ft.fact == 'drawdown_D'].itertuples()},
                    vol_ci={lab[row.asset]: [row.lo, row.hi] for row in ft[ft.fact == 'volume_spearman'].itertuples()},
                    pdv_scores={k: dict(r2=float(sc.loc[k, 'r2']), rmse=float(sc.loc[k, 'RMSE'])) for k in sc.index})

    # control numbers (printed, compared with the page in the check script)
    y_tr = df['vix'].loc[g.PDV_TRAIN[0]:g.PDV_TRAIN[1]]
    print('PDV R2 train with the csv parameters:', 1 - np.sum((y_tr - fit.loc[y_tr.index]) ** 2) / np.sum((y_tr - y_tr.mean()) ** 2))

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 1 interactive page, exported by Quantlets/Ch_01/export_interactive.py.\n')
        f.write('window.CH1_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

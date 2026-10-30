"""Export the inputs of the Chapter 2 interactive page (MFM/interactive/ch2_data.js).

Uses the chapter's own functions (generate_all_charts.py, eff_tests.py, predictability.py, crypto_momentum_case.py) and its results files,
so the page starts from the same numbers as the slides. The two illustrative random-walk figures use the
innovations of latex/ch2_concept_charts.py (numpy seed 203, 900 days).
"""
import json
import os

import numpy as np
import pandas as pd

import generate_all_charts as g
from eff_tests import variance_ratio, acf_se
from mfm_data import load_close, read_market

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch2_data.js')


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def game(seed=7):
    """The four panels of ch2_random_walk_game: the same draws as fig_random_walk_game."""
    p = load_close('sp500', start='2010-01-01')
    lr = np.log(p).diff().dropna()
    rng = np.random.default_rng(seed)
    real_pos = int(rng.integers(0, 4))
    paths = []
    for i in range(4):
        if i == real_pos:
            path = np.log(p.values / p.values[0])
        else:
            path = np.concatenate([[0], np.cumsum(rng.normal(lr.mean(), lr.std(), len(lr)))])
        paths.append(r(np.exp(path), 4))
    return dict(paths=paths, real=real_pos, mu=float(lr.mean()), sd=float(lr.std()), n=len(lr),
                start=str(p.index[0].date()), end=str(p.index[-1].date()))


def acf_lags(x, kmax=10):
    """Lag-k autocorrelation (pandas autocorr, as in efficiency_table) and two standard errors (eff_tests.acf_se):
    se = SE under H0 (robust test band centred at 0), hac = HAC SE of the estimator (interval around rho_k)."""
    s = pd.Series(np.asarray(x, float))
    rho = [float(s.autocorr(k)) for k in range(1, kmax + 1)]
    ses = [acf_se(s.values, k) for k in range(1, kmax + 1)]
    return rho, [a for a, _ in ses], [b for _, b in ses]


def main():
    res = json.load(open(os.path.join(HERE, 'ch2_numbers.json')))
    lev = json.load(open(os.path.join(HERE, 'ch2_level_numbers.json')))
    t = pd.read_csv(os.path.join(HERE, 'ch2_efficiency_table.csv'), index_col=0)
    d = dict(order=g.ORDER, labels=g.LABELS, groups=g.GROUPS)

    d['game'] = game()
    assert 'ABCD'[d['game']['real']] == res['rw_game_real']

    # illustrative RW1 / RW2 / GARCH figures: the innovations of ch2_concept_charts.py
    d['eps'] = r(np.random.default_rng(203).normal(size=900), 6)

    # autocorrelations at lags 1-10 and VR profiles for all markets
    d['acf'], d['vr'] = {}, {}
    for k in g.ORDER:
        x = g.rets[k]
        rho, se, hac = acf_lags(x.values)
        assert abs(rho[0] - t.loc[k, 'rho1']) < 1e-5 and abs(se[0] - t.loc[k, 'rho1_se_rob']) < 1e-5
        assert abs(hac[0] - t.loc[k, 'rho1_se_hac']) < 1e-5
        d['acf'][k] = dict(T=len(x), rho=r(rho), se=r(se), hac=r(hac), start=str(x.index[0].date()))
        vp = g.vr_profile(x)
        d['vr'][k] = dict(VR=r(vp['VR'].values), band=r(vp['band'].values),
                          zstar=r([variance_ratio(x, q)[2] for q in (2, 5, 10, 20)], 4), CD_p=float(t.loc[k, 'CD_p']))
    for k, v in res['vr_profile'].items():
        for q, (vr, band) in v.items():
            assert abs(d['vr'][k]['VR'][int(q) - 2] - vr) < 1e-5 and abs(d['vr'][k]['band'][int(q) - 2] - band) < 1e-5

    # out-of-sample forecasts with dp (predictability.oos_r2, saved in ch2_oos_dp.csv)
    o = pd.read_csv(os.path.join(HERE, 'ch2_oos_dp.csv'), index_col=0, parse_dates=True)
    d['oos'] = dict(dates=[f'{x:%Y-%m}' for x in o.index], y=r(o['y'].values, 7), mean=r(o['mean'].values, 7),
                    pred=r(o['pred'].values, 7), ct=r(o['ct'].values, 7), res={k: lev['oos'][k] for k in ('r2', 'r2_ct', 'cw_t', 'cw_p', 'n')})

    # bank tax event: daily log returns aligned as in predictability.event_study_bank_tax
    px = pd.concat({'TLV': read_market('TLV.RO')['adjusted_close'], 'BRD': read_market('BRD.RO')['adjusted_close'],
                    'BET': read_market('BET')['close']}, axis=1).dropna()
    px = px[px.index.dayofweek < 5]
    lr = np.log(px).diff().dropna()
    t0 = lr.index.get_loc(pd.Timestamp('2018-12-19'))
    w = lr.iloc[t0 - 250:t0 + 6]
    d['event'] = dict(day=list(range(-250, 6)), dates=[f'{x:%Y-%m-%d}' for x in w.index],
                      TLV=r(w['TLV'].values, 7), BRD=r(w['BRD'].values, 7), BET=r(w['BET'].values, 7),
                      res={k: lev['event']['firms'][k] for k in ('TLV', 'BRD', 'PORT')})

    # multiple testing: S&P 500 daily returns (bp) and the 2000 t-statistics of fig_multiple_testing
    x = (g.rets['sp500'] * 1e4).values
    rng = np.random.default_rng(g.SEED)
    ts = []
    for _ in range(2000):
        mask = rng.random(len(x)) < 0.2
        dd = x[mask].mean() - x[~mask].mean()
        se = np.sqrt(x[mask].var(ddof=1) / mask.sum() + x[~mask].var(ddof=1) / (~mask).sum())
        ts.append(dd / se)
    ts = np.array(ts)
    assert abs(np.mean(np.abs(ts) > 1.96) - res['multiple_testing']['share_196']) < 1e-9
    assert abs(np.abs(ts).max() - res['multiple_testing']['max_abs_t']) < 1e-9
    d['mt'] = dict(r_bp=r(x, 2), t=r(ts, 4), res=res['multiple_testing'])

    # case study (Liu & Tsyvinski, 2021): weekly Bitcoin and Ethereum returns of crypto_momentum_case.py
    import crypto_momentum_case as cmc
    wk = pd.read_csv(os.path.join(HERE, 'ch2_crypto_tsmom_weekly.csv'), index_col=0, parse_dates=True)
    cres = json.load(open(os.path.join(HERE, 'ch2_crypto_tsmom.json')))
    for k in ('btc', 'eth'):
        for p, (a, b) in cmc.PERIODS.items():
            if p in cres[k]:
                chk = cmc.period_stats(wk[k].dropna(), a, b)['reg'][1]
                assert abs(chk['b'] - cres[k][p]['reg']['1']['b']) < 1e-6 and abs(chk['t_hac'] - cres[k][p]['reg']['1']['t_hac']) < 1e-5
    col = lambda k: [None if np.isnan(v) else round(float(v), 8) for v in wk[k].values]
    d['cmom'] = dict(dates=[f'{x:%Y-%m-%d}' for x in wk.index], btc=col('btc'), eth=col('eth'), paper=cres['paper_numbers'],
                     window=cres['roll_window'], res={k: {p: dict(b1=v['reg']['1']['b'], t1=v['reg']['1']['t_hac'], weeks=v['weeks'])
                                                         for p, v in cres[k].items() if p != 'rolling'} for k in ('btc', 'eth')},
                     rolling=cres['btc']['rolling'])

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 2 interactive page, exported by Quantlets/Ch_02/export_interactive.py.\n')
        f.write('window.CH2_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

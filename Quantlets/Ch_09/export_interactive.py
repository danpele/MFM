"""Export the inputs of the Chapter 9 interactive page (MFM/interactive/ch9_data.js).

Uses the data and functions of generate_all_charts.py, mfm_data.py and rv_tools.py, so the page starts from the same
numbers as the slides. save_fig is replaced by a no-op: no chart or results file of the chapter is rewritten. The
out-of-sample forecasts are read from ch9_forecasts_spy.csv and ch9_forecasts_btc.csv (written by the chapter's
generator), so GARCH is not re-estimated here. All data come from the local data/market files.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

import generate_all_charts as g
import rv_tools as T

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch9_data.js')


def no_save(name):
    import matplotlib.pyplot as plt
    plt.close('all')


g.save_fig = no_save


def r(x, d=6):
    a = np.round(np.asarray(x, float), d)
    return [None if not np.isfinite(v) else float(v) for v in a]


def calendar(idx):
    """Compact daily calendar: first date and the gaps in calendar days (the page rebuilds the dates)."""
    return dict(d0=f'{idx[0]:%Y-%m-%d}', gaps=np.diff(idx.values.astype('datetime64[D]').astype(np.int64)).tolist())


def close(a, b, tol=1e-6):
    assert abs(a - b) <= tol * max(1.0, abs(b)), (a, b)


def main():
    res = json.load(open(os.path.join(HERE, 'ch9_results.json')))
    RV, ON, OC, RVT = g.RV_SPY, g.ON, g.OC, g.RVT_SPY
    RVB = g.RV_BTC
    d = dict(col=dict(blue=g.MainBlue, red=g.IDAred, green=g.Forest, amber=g.Amber, orange=g.Orange, purple=g.Purple,
                      teal=g.Teal, navy=g.Navy, band=g.BandBlue))

    # daily series: SPY (intraday RV, overnight and open-to-close returns), Bitcoin (24-hour RV, UTC daily return)
    ccb = g.CC_BTC_UTC()
    d['spy'] = dict(calendar(RV.index), rv=r(RV.values, 6), on=r(ON.values, 5), oc=r(OC.values, 5))
    d['btc'] = dict(calendar(RVB.index), rv=r(RVB.values, 6), cc=r(ccb.reindex(RVB.index).values, 5))

    # 1. one trading day: 5-minute returns of a few days (the open price rebuilds the path)
    rows = R = g.R_SPY
    full = R.notna().sum(axis=1) == 78
    rvd = RV[full]
    pick = list(rvd.sort_values(ascending=False).index[:8])
    for extra in ['2021-08-27', '2024-08-05', '2025-04-09']:
        t = pd.Timestamp(extra)
        if t in rvd.index and t not in pick:
            pick.append(t)
    pick.append(rvd.index[np.argsort(rvd.values)[len(rvd) // 2]])        # the median day
    pick.append(rvd.idxmin())                                            # the calmest day
    pick = sorted(set(pick))
    d['days'] = {f'{t:%Y-%m-%d}': dict(p0=float(g.P_SPY.loc[t, 0]), r=r(rows.loc[t].values, 6), on=float(ON[t]), oc=float(OC[t]))
                 for t in pick}
    dd = g.fig_intraday_day()
    for k in ('rv', 'max_ret', 'max_share', 'oc', 'on'):
        close(dd[k], res['day'][k])
    rr = np.array(d['days']['2025-04-07']['r'])
    close(float((rr ** 2).sum()), res['day']['rv'], 1e-5)

    # 2.-3. series and overnight: checks of the slide numbers
    s = g.fig_rv_series()
    close(s['spy_mean'], res['series']['spy_mean'])
    close(s['btc_mean'], res['series']['btc_mean'])
    o = g.fig_overnight()
    close(o['share'], res['overnight']['share'])

    # 4. signature plot: sums and counts of the per-day sparse and subsampled RV, by year (the page aggregates)
    sig = {}
    for key, P, ks, ppy in [('spy', g.P_SPY, g.KS_SPY, 252), ('btc', g.P_BTC, g.KS_BTC, 365)]:
        yrs = sorted(set(P.index.year))
        sp = {k: T.sparse_rv(P, k) for k in ks}
        ss = {k: T.subsampled_rv(P, k) for k in ks}
        tab = dict(ks=ks, ppy=ppy, years=yrs, n=[int((P.index.year == y).sum()) for y in yrs],
                   sparse=[[float(sp[k][sp[k].index.year == y].sum()) for y in yrs] for k in ks],
                   sub=[[float(ss[k][ss[k].index.year == y].sum()) for y in yrs] for k in ks])
        ref = T.signature(P, ks, ppy)
        for i, k in enumerate(ks):
            close(np.sqrt(ppy * sum(tab['sparse'][i]) / sum(tab['n'])), ref['sparse'].iloc[i])
            close(np.sqrt(ppy * sum(tab['sub'][i]) / sum(tab['n'])), ref['subsampled'].iloc[i])
        sig[key] = tab
    close(np.sqrt(252 * sum(sig['spy']['sub'][4]) / sum(sig['spy']['n'])), res['sig']['spy30'])
    sig['rho1'] = dict(spy=res['sig']['spy_rho1'], btc=res['sig']['btc_rho1'])
    d['sig'] = sig

    # 5. jumps: ratio statistic, RV and BV of each day
    js, jb = T.jump_test(g.R_SPY), T.jump_test(g.R_BTC)
    d['jumps'] = {k: dict(z=r(j['z'].values, 5), bv=r(j['bv'].values, 6), M=[int(x) for x in T.nret(R_).values])
                  for k, j, R_ in [('spy', js, g.R_SPY), ('btc', jb, g.R_BTC)]}
    assert int(js['jump'].sum()) == res['jumps']['spy']['n_jump'] and int(jb['jump'].sum()) == res['jumps']['btc']['n_jump']
    p = stats.norm.sf(js['z'].values)
    n5 = int((p < 0.05).sum())
    ps = np.sort(p)
    k = np.where(ps <= np.arange(1, len(ps) + 1) * 0.05 / len(ps))[0]
    print('SPY: rejections at 5%:', n5, ' BH 5%:', (k.max() + 1) if len(k) else 0)

    # 6.-7. distributions and ACF: checks
    di = g.fig_distributions()
    close(di['z_kurt'], res['dist']['z_kurt'])
    ac = g.fig_acf()
    close(ac['spy1'], res['acf']['spy1'])

    # 8. VIX on the SPY calendar (forward-filled, as on the slide)
    vix = g.M.daily_close('vix').reindex(RVT.index).ffill()
    d['vix'] = r(vix.values, 2)
    v = g.fig_vix()
    close(v['vix_mean'], res['vix']['vix_mean'])

    # 9. HAR coefficients (full sample), for the implied autocorrelation of log RV
    d['har'] = {k: res['har'][k]['b'] for k in ('spy_log', 'btc_log')}

    # 10. out-of-sample forecasts (the chapter's CSV files)
    fc = {}
    for key, fn, cal in [('spy', 'ch9_forecasts_spy.csv', RV.index), ('btc', 'ch9_forecasts_btc.csv', RVB.index)]:
        F = pd.read_csv(os.path.join(HERE, fn), index_col=0, parse_dates=True)
        pos = cal.get_indexer(F.index)
        assert (pos >= 0).all(), key
        fc[key] = dict(pos=[int(x) for x in pos], **{c: r(F[c].values, 6) for c in F.columns if c != 'proxy'})
        assert np.allclose(F['proxy'].values, (RVT if key == 'spy' else RVB).values[pos]), key
        ref = res['oos_' + key]
        for c in ('logHAR', 'HAR', 'GARCH-t', 'EWMA', 'RW'):
            close(float(T.qlike(F['proxy'], F[c]).mean()), ref[c]['qlike'])
        close(T.dm_test(T.qlike(F['proxy'], F['logHAR']), T.qlike(F['proxy'], F['GARCH-t']))['t'], ref['GARCH-t']['dm_q_t'])
    d['fc'] = fc

    # 11. rough volatility: checks (the page computes m(q, Delta) from the RV series)
    ro = g.fig_rough()
    close(ro['H_spy'], res['rough']['H_spy'])
    close(ro['H_btc'], res['rough']['H_btc'])

    # 12. case study: the paper's table (Tables 2-7)
    tab = g.csv_table()
    d['csv'] = dict(models=g.CSV_MODELS, labels=[g.csv_label(m) for m in g.CSV_MODELS],
                    family={m: f for f, _, ms in g.CSV_FAMILY for m in ms}, fcol={f: c for f, c, _ in g.CSV_FAMILY},
                    rel={f'{h}|{i}': [float(x) for x in tab.loc[(h, i)].values] for h in ('day', 'week', 'month') for i in ('HAR', 'ALL')})

    d['num'] = {k: res[k] for k in ('day', 'series', 'overnight', 'sig', 'jumps', 'dist', 'acf', 'vix', 'rough')}
    d['num']['oos_spy'] = res['oos_spy']
    d['num']['oos_btc'] = res['oos_btc']

    with open(OUT, 'w') as fh:
        fh.write('// Inputs of the Chapter 9 interactive page, exported by Quantlets/Ch_09/export_interactive.py.\n')
        fh.write('window.CH9_DATA = ' + json.dumps(d, separators=(',', ':'), default=float).replace('NaN', 'null') + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

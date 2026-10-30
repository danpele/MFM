"""Export the inputs of the Chapter 4 interactive page (MFM/interactive/ch4_data.js).

Uses the functions of generate_all_charts.py, so the page starts from the same numbers as the slides.
"""
import json
import os

import numpy as np

import generate_all_charts as g

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch4_data.js')


def r(x, d=6):
    return np.round(np.asarray(x, float), d).tolist()


def ym(idx):
    return [f'{t:%Y-%m}' for t in idx]


def main():
    res = json.load(open(os.path.join(HERE, 'ch4_results.json')))
    S = g.SECTORS
    d = dict(sectors=S, multi_assets=g.MULTI, combined=g.COMBINED, strategies=g.STRATS)

    # two assets
    R2, mu2, sd2, rho = g.two_asset_stats()
    d['two'] = dict(start=ym(R2.index[:1])[0], end=ym(R2.index[-1:])[0], T=len(R2),
                    mu=[float(mu2['SPY']), float(mu2['TLT'])], sd=[float(sd2['SPY']), float(sd2['TLT'])], rho=float(rho))

    # sectors: full-sample moments (frontier, estimation error, window length)
    R, Rex, rf = g.us_monthly(S)
    d['full'] = dict(start=ym(Rex.index[:1])[0], end=ym(Rex.index[-1:])[0], T=len(Rex),
                     mu=r(Rex.mean().values, 8), cov=r(Rex.cov().values, 10),
                     w_tan_lo=r(g.w_long_only(Rex.cov().values, Rex.mean().values)))
    d['window'] = res['window_length']

    # shrinkage: eigenvalues and rolling intensity
    X = Rex.values
    deltas = [g.lw_cc(X[t - g.WINDOW:t])[1] for t in range(g.WINDOW, len(X) + 1)]
    sh = res['shrinkage']
    last = X[-g.WINDOW:]
    S60 = np.cov(last.T, bias=True)
    sd60 = np.sqrt(np.diag(S60))
    C60 = S60 / np.outer(sd60, sd60)
    rbar = (C60.sum() - len(S)) / (len(S) * (len(S) - 1))
    F60 = rbar * np.outer(sd60, sd60)
    np.fill_diagonal(F60, np.diag(S60))
    S_lw, d_last = g.lw_cc(last)
    assert np.allclose(S_lw, d_last * F60 + (1 - d_last) * S60)
    d['shrink'] = dict(S60=r(S60 * 12, 10), F60=r(F60 * 12, 10), delta_lw=float(d_last), ev_sample=r(sh['ev_sample']), ev_lw=r(sh['ev_lw']), ev_full=r(sh['ev_full']),
                       dates=ym(Rex.index[g.WINDOW - 1:]), delta=r(deltas, 4))

    # Marchenko-Pastur: eigenvalues of the last 60-month correlation matrices
    d['mp'] = {u: dict(N=v['N'], T=v['T'], lo=v['lo'], hi=v['hi'], ev=r(v['ev']), start=v['start'][:7], end=v['end'][:7])
               for u, v in res['mp'].items()}

    # Black-Litterman: last 10 years
    Rb, Rexb, _ = g.us_monthly(S, start='2016-08-01')
    d['bl'] = dict(start=ym(Rexb.index[:1])[0], end=ym(Rexb.index[-1:])[0], T=len(Rexb),
                   cov_ann=r(Rexb.cov().values * 12, 10), mu_sample_ann=r(Rexb.mean().values * 12, 8), delta=2.5, tau=0.05)

    # risk contributions: multi-asset universe
    Rm, Rexm, _ = g.us_monthly(g.MULTI)
    Sm = Rexm.cov().values * 12
    d['multi'] = dict(start=ym(Rexm.index[:1])[0], end=ym(Rexm.index[-1:])[0], T=len(Rexm), cov_ann=r(Sm, 10),
                      hrp=r(g.w_hrp(Sm)))

    # HRP: combined universe, tree and weights
    Rc, Rexc, _ = g.us_monthly(g.COMBINED)
    Sc = Rexc.cov().values * 12
    Z = g.hrp_tree(Sc)
    d['hrp'] = dict(start=ym(Rexc.index[:1])[0], end=ym(Rexc.index[-1:])[0], T=len(Rexc), cov_ann=r(Sc, 10),
                    Z=r(Z, 6), w_hrp=r(g.w_hrp(Sc)), w_gmv_lo=r(g.w_long_only(Sc)))

    # out-of-sample backtests: returns, risk-free rate, turnover, weights (sectors)
    bts = g.run_backtests()
    d['oos'] = {}
    for u, (ret, to, W) in bts.items():
        d['oos'][u] = dict(dates=ym(ret.index), rf=r(ret.attrs['rf'].values, 6),
                           ret={s: r(ret[s].values, 6) for s in g.STRATS},
                           turnover={s: r(to[s].fillna(0).values, 5) for s in g.STRATS},
                           liquidated={s: f'{g.ruin_month(ret, s):%Y-%m}' for s in g.STRATS
                                       if g.ruin_month(ret, s) is not None})
    # a rule whose wealth reaches zero is liquidated and left out of the comparisons
    d['implementable'] = [s for s in g.STRATS if all(s in g.implementable(bts[u][0]) for u in bts)]
    ret, to, W = bts['Sectors']
    d['rolling'] = dict(dates=ym(W['MV'].index), MV=r(W['MV'].values, 4), GMV_LW=r(W['GMV-LW'].values, 4))
    d['tests'] = {u: {s: {k: v[k] for k in ('diff', 'se_hac', 'p_hac', 'p_boot', 'ci_boot', 'block', 't_obs', 'z_star')}
                      for s, v in tv.items()} for u, tv in res['sharpe_tests'].items()}

    # BVB blue chips against BET-TR
    ret, to, W, bench, removed, m = g.bvb_backtest()
    d['bvb'] = dict(dates=ym(ret.index), strategies=list(g.BVB_STRATS), ret={s: r(ret[s].values, 6) for s in g.BVB_STRATS},
                    bench={b: r(bench[b].reindex(ret.index).values, 6) for b in ('BET-TR', 'BET')},
                    tests={s: {k: v[k] for k in ('diff', 'p_hac', 'p_boot', 'ci_boot')} for s, v in res['bvb']['tests'].items()})

    # case study: volatility-managed portfolios (DeMiguel, Martin-Utrera & Uppal 2024), vol_managed_case.py
    import vol_managed_case as vm
    vres, vraw = vm.compute()
    d['vmp'] = dict(cost_bp=vm.COST_BP, universes=list(vraw), single_universe='Multi-asset')
    for u, (ret, to, lev, single, Xoos, sig_m) in vraw.items():
        d['vmp'][u] = dict(dates=ym(ret.index), T=len(ret),
                           ret={s: r(ret[s].values, 6) for s in ret}, turnover={s: r(to[s].fillna(0).values, 5) for s in ret},
                           leverage={s: round(v, 4) for s, v in lev.items()},
                           single={c: [round(v['sr_unmanaged'], 4), round(v['sr_managed'], 4), round(v['p_hac'], 4)]
                                   for c, v in vres[u]['single'].items()},
                           tests={s: {k: (round(v, 4) if v is not None else None) for k, v in t.items()}
                                  for s, t in vres[u]['tests'].items()})

    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 4 interactive page, exported by Quantlets/Ch_04/export_interactive.py.\n')
        f.write('window.CH4_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

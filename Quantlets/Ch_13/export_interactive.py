"""Export the inputs of the Chapter 13 interactive page (MFM/interactive/ch13_data.js).

Uses the data, models and estimators of generate_all_charts.py, mfm_ml.py and inference_tests.py, so the page starts
from the same numbers as the slides. No chart is drawn: save_fig is replaced by a no-op and the hashes of the chapter's
chart files are checked before and after. The heavy fits (purged CV of the four models, the walk-forward refits,
LASSO paths, the leakage experiment, the BTC grid, double selection and DML) are run here once;
the anomaly forecasts of the second case study come from anomaly_market.py (--only dlrz recomputes just them); the page moves
through the stored grids. Run time: about 10 minutes.
"""
import glob
import hashlib
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch13_data.js')
CHARTS = os.path.join(HERE, '..', '..', 'charts')

import generate_all_charts as g  # noqa: E402
import inference_tests as it  # noqa: E402
from mfm_ml import ffd_weights, frac_diff_ffd, PurgedKFold, sharpe_ratio, expected_max_sharpe, french_factors, tangency_portfolio  # noqa: E402

g.save_fig = lambda name: g.plt.close('all')
it.g = g

from statsmodels.tsa.stattools import adfuller  # noqa: E402
import statsmodels.api as sm  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, RandomForestRegressor  # noqa: E402
from sklearn.model_selection import KFold  # noqa: E402
from sklearn.metrics import accuracy_score, roc_auc_score  # noqa: E402

SEED = g.SEED


def r(x, d=6):
    a = np.round(np.asarray(x, float), d)
    return [None if not np.isfinite(v) else (int(v) if d == 0 else float(v)) for v in a.ravel()] if a.ndim == 1 else [r(row, d) for row in a]


def hashes():
    files = sorted(glob.glob(os.path.join(CHARTS, 'ch13_*')) + glob.glob(os.path.join(HERE, '*.json'))
                   + glob.glob(os.path.join(HERE, 'MFM_ch13_*', '*')))
    return {f: hashlib.md5(open(f, 'rb').read()).hexdigest() for f in files}


def load_existing():
    txt = open(OUT).read()
    return json.loads(txt[txt.index('=') + 1:].strip().rstrip(';'))


def main(keys=None):
    """keys = None: all blocks; otherwise only the named blocks are recomputed, the others are kept."""
    before = hashes()
    want = lambda k: keys is None or k in keys
    spx, d = g.spx, ({} if keys is None else load_existing())
    dates = [f'{t:%Y-%m-%d}' for t in spx.index]
    pos = {t: i for i, t in enumerate(spx.index)}
    if want('spx'):
        d['spx'] = dict(dates=dates, close=r(spx.values, 2))

    # ---------------------------------------------------------------- ACF of r and |r|
    rr = np.log(spx).diff().dropna()
    if want('acf'):
      d['acf'] = dict(T=len(rr), ac_r=r([rr.autocorr(l) for l in range(1, 41)], 5), ac_a=r([rr.abs().autocorr(l) for l in range(1, 41)], 5))

    # ---------------------------------------------------------------- FFD: ADF against d (1 lag and AIC lags)
    out, d_star = g.find_min_d(g.log_spx)
    assert abs(d_star - 0.25) < 1e-9, d_star
    aic = []
    for dd in out.index:
        x = frac_diff_ffd(g.log_spx, dd).dropna()
        a = adfuller(x, regression='c', autolag='AIC')
        aic.append((a[0], a[2]))
    if want('ffd'):
      d['ffd'] = dict(d=r(out.index, 2), adf=r(out['adf'], 4), crit=float(out['crit'].iloc[0]), corr=r(out['corr'], 4),
                    adf_aic=r([a[0] for a in aic], 4), lags_aic=[int(a[1]) for a in aic], d_star=float(d_star))

    # ---------------------------------------------------------------- triple barrier, 2022
    close = spx.loc['2021-10-01':'2023-03-31']
    vol = g.get_daily_vol(spx).reindex(close.index)
    ev = [close.index[close.index.searchsorted(pd.Timestamp(t))] for t in ['2022-01-18', '2022-03-15', '2022-05-19', '2022-08-01', '2022-11-01']]
    tb = g.triple_barrier(close, ev, vol, pt=1.0, sl=1.0, horizon=15)
    if want('tb'):
      d['tb'] = dict(i0=pos[close.index[0]], n=len(close), vol=r(vol.values, 6), events=[int(close.index.get_loc(t)) for t in ev],
                   labels=[int(v) for v in tb['label']], barriers=list(tb['barrier']))

    # ---------------------------------------------------------------- leakage experiment, label/feature length h
    def leakage(h, n=3000):
        rng = np.random.default_rng(SEED)
        p = pd.Series(np.cumsum(rng.normal(0, 0.01, n + h)))
        y = (p.shift(-h) - p > 0).astype(int).iloc[:n].values
        X = np.column_stack([pd.Series(rng.normal(size=n + h)).rolling(h).mean().bfill().iloc[:n] for _ in range(5)])
        t1 = pd.Series(np.arange(n) + h, index=np.arange(n))
        model = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1, random_state=SEED)
        schemes = {'shuffled': KFold(5, shuffle=True, random_state=SEED), 'contiguous': KFold(5, shuffle=False),
                   'purged': PurgedKFold(5, t1=t1, pct_embargo=0.01)}
        res = {}
        for name, cv in schemes.items():
            res[name] = [accuracy_score(y[te], model.fit(X[tr], y[tr]).predict(X[te])) for tr, te in cv.split(X)]
        return res
    hs = [1, 2, 5, 10, 20, 40, 60]
    if want('leak'):
        d['leak'] = dict(h=hs, acc={str(h): {k: r(v, 4) for k, v in leakage(h).items()} for h in hs})
        print('leakage h=20', {k: np.mean(v) for k, v in d['leak']['acc']['20'].items()})

    # ---------------------------------------------------------------- modelling frame
    df = g.modelling_frame(d_star)
    feat = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    X, y = df[feat].values, df['y'].values
    cv = PurgedKFold(5, t1=df['t1'], pct_embargo=0.01)
    folds = list(cv.split(X))
    fold_id = np.zeros(len(y), int)
    for k, (_, te) in enumerate(folds):
        fold_id[te] = k

    # LASSO (L1) path of the slide, and the L2 path with the same solver; purged-CV AUC along each path
    # (the path itself is the full-sample fit of the slide; in the CV the scaler is estimated on each training fold)
    Xs = StandardScaler().fit_transform(X)
    Cs = np.logspace(-4, 0, 40)
    paths, cvauc = {}, {}
    scalers = [StandardScaler().fit(X[tr]) for tr, _ in folds]
    for pen in ('l1', 'l2') if want('lasso') else ():
        coefs, aucs = [], []
        for C in Cs:
            m = LogisticRegression(penalty=pen, C=C, solver='liblinear', max_iter=5000)
            coefs.append(m.fit(Xs, y).coef_.ravel())
            a = []
            for (tr, te), sc in zip(folds, scalers):
                p = m.fit(sc.transform(X[tr]), y[tr]).predict_proba(sc.transform(X[te]))[:, 1]
                a.append(roc_auc_score(y[te], p) if np.ptp(p) > 0 else 0.5)
            aucs.append(np.mean(a))
        paths[pen], cvauc[pen] = r(coefs, 5), r(aucs, 4)
    if want('lasso'):
        d['lasso'] = dict(features=feat, lam=r(1 / Cs, 6), coef=paths, cv_auc=cvauc)

    # four models, purged 5-fold CV: out-of-fold probabilities (stored ×1e6: at 1e-4 a few values just above 0.5 round to 0.5)
    probs = {}
    for name, model in g.get_models().items() if want('models') else ():
        p = np.full(len(y), np.nan)
        for tr, te in folds:
            model.fit(X[tr], y[tr])
            p[te] = model.predict_proba(X[te])[:, 1]
        probs[name] = p
        print(name, 'fold acc', np.mean([accuracy_score(y[te], p[te] > 0.5) for _, te in folds]),
              'fold auc', np.mean([roc_auc_score(y[te], p[te]) for _, te in folds]))
    if want('models'):
      d['models'] = dict(names=list(probs), y=''.join(map(str, y)), fold=''.join(map(str, fold_id)),
                       p={k: [int(round(v * 1e6)) for v in p] for k, p in probs.items()}, n=len(y), start=f'{df.index[0]:%Y-%m-%d}', end=f'{df.index[-1]:%Y-%m-%d}')

    # walk-forward 2010-2026: yearly refit, purged training window; d of the FFD feature frozen on data up to 2009;
    # decision at the close of t, trade at the close of t+1 (ret = log return from the close of t+1 to that of t+2)
    if want('wf'):
        _, d_pre = g.find_min_d(g.log_spx.loc[:g.D_FROZEN_END])
        dfw = g.modelling_frame(d_pre)
        prob = g.walk_forward_signal(dfw, [c for c in dfw.columns if c not in ('fwd', 'y', 't1')])
        oos = prob.dropna().index
        ret2 = g.next_close_return(oos)
        st, bh_, sig = g.long_cash_returns(prob)
        print('walk-forward SR', sharpe_ratio(st), sharpe_ratio(bh_), sig.mean(), 'd frozen', d_pre)
        d['wf'] = dict(idx=[pos[t] for t in oos], p=[int(round(v * 1e4)) for v in prob.loc[oos]], ret=r(ret2.values, 7), d=float(d_pre))

    # ---------------------------------------------------------------- expected maximum Sharpe: the slide's Monte Carlo
    rng = np.random.default_rng(SEED)
    T = 252 * 5
    Ns = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    sims = []
    for N in Ns if want('emax') else ():
        mx = []
        for _ in range(10):                      # 10 chunks of 20 repetitions: same stream as one call of size (200, N, T)
            x = rng.normal(0, 0.01, size=(20, N, T))
            mx.append((np.sqrt(252) * x.mean(-1) / x.std(-1, ddof=1)).max(1))
        sims.append(np.concatenate(mx))
    if want('emax'):
        d['emax'] = dict(N=Ns, T=T, sims=r(sims, 4))
    if want('emax'):
        print('E max SR MC, N=1000:', np.mean(sims[-1]), 'theory', expected_max_sharpe(1000, np.sqrt(252 / T)))

    # ---------------------------------------------------------------- BTC grid: IS / OOS Sharpe ratios for several split dates
    M = g.btc_grid_returns()
    gkeys = list(M.columns)
    splits = {}
    for ys in range(2018, 2025) if want('grid') else ():
        m = M.index < f'{ys}-01-01'
        splits[str(ys)] = dict(is_=r([sharpe_ratio(M[k][m], 365) for k in gkeys], 4), oos=r([sharpe_ratio(M[k][~m], 365) for k in gkeys], 4))
    if want('grid'):
        # family fixed in sample: rules with a null IS Sharpe are dropped on the page; a null OOS Sharpe (always in cash) counts as 0
        d['grid'] = dict(fast=[k[0] for k in gkeys], slow=[k[1] for k in gkeys], band=[k[2] for k in gkeys], start=f'{M.index[0]:%Y-%m-%d}',
                         end=f'{M.index[-1]:%Y-%m-%d}', splits={k: {'is': v['is_'], 'oos': v['oos']} for k, v in splits.items()})

    # ---------------------------------------------------------------- VIX: double selection and DML (code of inference_tests.dml_section)
    if want('vix'):
        vix_section(d)
    if want('cpz'):
        cpz_section(d)
    if want('dlrz'):
        d['dlrz'] = dlrz_section()
    write(d)
    assert hashes() == before, 'chapter files changed'
    print('chart and results files unchanged')


def vix_section(d):
    lags = [0, 1, 2, 3, 4, 5, 8, 10, 15, 20]
    dfv = g.modelling_frame(0.25)
    yv = dfv['fwd'].values * 1e4
    base = [c for c in dfv.columns if c not in ('fwd', 'y', 't1', 'ffd_price', 'vix_level')]
    Z = (dfv[base] - dfv[base].mean()) / dfv[base].std()
    cols = {c: Z[c] for c in base}
    cols.update({c + '^2': Z[c] ** 2 for c in base})
    cols.update({a + '*' + b: Z[a] * Z[b] for a, b in itertools.combinations(base, 2)})
    XV = pd.DataFrame(cols)
    XV = ((XV - XV.mean()) / XV.std()).values
    dv = ((dfv['vix_level'] - dfv['vix_level'].mean()) / dfv['vix_level'].std()).values
    n, p_ = XV.shape
    ols = lambda yy, XX, L: sm.OLS(yy, sm.add_constant(XX)).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    est = {}
    est['OLS, VIX only'] = [ols(yv, dv, L) for L in lags]
    est[f'OLS, all {p_} controls'] = [ols(yv, np.column_stack([dv, XV]), L) for L in lags]
    est['OLS, VIX only'] = [(f.params[1], f.bse[1]) for f in est['OLS, VIX only']]
    est[f'OLS, all {p_} controls'] = [(f.params[1], f.bse[1]) for f in est[f'OLS, all {p_} controls']]
    Sy, Sd = it.rlasso(yv, XV), it.rlasso(dv, XV)
    U = sorted(set(Sy) | set(Sd))
    est['post-double selection'] = [(f.params[1], f.bse[1]) for f in (ols(yv, np.column_stack([dv, XV[:, U]]), L) for L in lags)]
    fo = np.array_split(np.arange(n), 5)
    h = 5
    for learner in ('lasso', 'rf'):
        ut, vt = np.empty(n), np.empty(n)
        for te in fo:
            tr = np.setdiff1d(np.arange(n), np.arange(max(te[0] - h, 0), min(te[-1] + h + 1, n)))
            for target, res in ((yv, ut), (dv, vt)):
                if learner == 'lasso':
                    s_ = it.rlasso(target[tr], XV[tr])
                    fit = sm.OLS(target[tr], sm.add_constant(XV[tr][:, s_])).fit()
                    pred = fit.predict(sm.add_constant(XV[te][:, s_], has_constant='add'))
                else:
                    pred = RandomForestRegressor(300, min_samples_leaf=50, max_features=0.3, n_jobs=-1, random_state=SEED).fit(XV[tr], target[tr]).predict(XV[te])
                res[te] = target[te] - pred
        theta = np.sum(vt * ut) / np.sum(vt * vt)
        est['DML, LASSO learners' if learner == 'lasso' else 'DML, random forests'] = [
            (theta, sm.OLS(ut, vt).fit(cov_type='HAC', cov_kwds={'maxlags': L}).bse[0]) for L in lags]
    d['vix'] = dict(lags=lags, names=list(est), theta=[round(float(v[0][0]), 3) for v in est.values()],
                    se=[r([s for _, s in v], 3) for v in est.values()], ny=len(Sy), nd=len(Sd), n=n, p=p_)
    for k, v in est.items():
        th, se = v[lags.index(4)]
        print(f'  {k}: {th:.1f} [{th - 1.96 * se:.1f}; {th + 1.96 * se:.1f}]')



def cpz_section(d):
    # ---------------------------------------------------------------- Chen, Pelger & Zhu: Kenneth French factors
    f5 = french_factors('ff5')[g.FF_COLS['ff5']]
    f3 = french_factors('ff3')[g.FF_COLS['ff3']]
    f5, f3 = f5.loc[f5.index.intersection(f3.index)], f3.loc[f5.index.intersection(f3.index)]
    rets = g.cpz_tangency_returns()
    test = rets.loc[g.CPZ_TEST[0]:g.CPZ_TEST[1]]
    print('CPZ replication', {k: g.monthly_sr(test[k])[:2] for k in ('FF5', 'FF3')})
    d['cpz'] = dict(dates=[f'{t:%Y-%m}' for t in f5.index], ff5=r(f5.values, 4), ff3=r(f3.values, 4), paper=g.CPZ_SR)


def dlrz_section():
    """Dong, Li, Rapach & Zhou (2022): recursive forecasts of Mkt-RF from anomaly_market.py (Kenneth French data)."""
    import anomaly_market as am
    fc, uni = am.dlrz_forecasts(am.anomaly_panel())
    res = am.summary(fc)
    print('DLRZ R2_OOS 1985-end', {m: res['1985-end'][m]['r2'] for m in ('OLS', 'ENet', 'Comb', 'C-ENet')})
    return dict(dates=[f'{t:%Y-%m}' for t in fc.index], names=list(uni.columns), nf=7,
                y=r(fc.MKT.values, 6), hm=r(fc.HM.values, 6), uni=r(uni.values, 6),
                cenet=r(fc['C-ENet'].values, 6), enet=r(fc.ENet.values, 6), ols=r(fc.OLS.values, 6),
                nsel=r(fc.nsel.values, 0), paper=am.DLRZ_R2, paper_end='2017-12')


def write(d):
    with open(OUT, 'w') as f:
        f.write('// Inputs of the Chapter 13 interactive page, exported by Quantlets/Ch_13/export_interactive.py.\n')
        f.write('window.CH13_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    # python3 export_interactive.py --only leak,lasso,models,wf,grid   (the other blocks of ch13_data.js are kept)
    if len(sys.argv) > 2 and sys.argv[1] == '--only':
        main(set(sys.argv[2].split(',')))
    else:
        main()

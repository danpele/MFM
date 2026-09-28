"""
inference_tests.py -- Inferenta asupra abilitatii predictive (Capitolul 13, MFM)
===============================================================================
Cifrele din sectiunile "Testing Predictive Ability", "Memory Estimation", "Data-Snooping Tests"
si "Machine Learning for Inference" ale cursului:
  1. FFD si memoria: suma ponderilor trunchiate, local Whittle / exact local Whittle cu CI,
     d* ales pe subesantioane, Monte Carlo: ADF pe FFD(d) al unui mers aleator
  2. Studiul de caz S&P 500: Pesaran-Timmermann, CI DeLong si bootstrap pe blocuri pentru AUC,
     walk-forward 2010-2026: Diebold-Mariano, Clark-West, Giacomini-White,
     Sharpe: eroarea standard Lo (2002) si testul Ledoit-Wolf (2008) al diferentei
  3. Grila BTC (1 279 reguli MA): White Reality Check, Hansen SPA, Romano-Wolf StepM
  4. Selectie dubla (Belloni-Chernozhukov-Hansen 2014) si DML (Chernozhukov et al. 2018):
     prezice nivelul VIX randamentul S&P 500 pe 5 zile, dat fiind 90 de variabile de control?
  5. Campbell-Thompson (2008): R^2 lunar -> castig de Sharpe
Rulare: python3 inference_tests.py      (aproximativ 3 minute)
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import os, sys, itertools, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.linear_model import LogisticRegression, Lasso
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_all_charts as g
from mfm_ml import (load_data, ffd_weights, frac_diff_ffd, PurgedKFold, sharpe_ratio,
                    local_whittle, exact_local_whittle)
SEED = 42


# =============================================================================
# 1. FFD SI MEMORIA
# =============================================================================
def memory_section():
    lp = g.log_spx
    r = lp.diff().dropna()
    print('== 1. FFD and memory ==')
    for d in (0.25, 0.3, 0.5):
        w = ffd_weights(d, 1e-4)
        print(f'  d={d}: K={len(w) - 1} lags, sum of weights = {w.sum():.3f}')
    x = frac_diff_ffd(lp, 0.25)
    print('  ADF on FFD(0.25), 1 lag:', np.round(adfuller(x, maxlag=1, regression='c', autolag=None)[:2], 3),
          '| AIC lags:', np.round(adfuller(x, regression='c', autolag='AIC')[:3], 3))
    for lab, v, est in (('log price', lp.values, exact_local_whittle), ('FFD(0.25)', x.values, exact_local_whittle),
                        ('returns', r.values, local_whittle), ('|returns|', r.abs().values, local_whittle)):
        dh, se = est(v)
        print(f'  {lab:10s}: d_hat = {dh:.3f}, 95% CI [{dh - 1.96 * se:.3f}, {dh + 1.96 * se:.3f}], m = {int(len(v) ** 0.65)}')
    for end in ('2009-12-31', '2014-12-31', None):
        _, ds = g.find_min_d(lp.loc[:end] if end else lp)
        print(f'  "minimum d*" (ADF 5%) on data up to {end or "2026"}: {ds}')
    rng = np.random.default_rng(SEED)
    for T, d in ((6274, 0.25), (2500, 0.25), (2500, 0.5)):
        w = ffd_weights(d, 1e-4)
        rej = []
        for _ in range(500):
            f = np.convolve(np.cumsum(rng.normal(size=T + len(w) - 1)), w, mode='valid')
            s = adfuller(f, maxlag=1, regression='c', autolag=None)
            rej.append(s[0] < s[4]['5%'])
        print(f'  Monte Carlo, random walk, T={T}, d={d}: ADF(1 lag) rejects in {np.mean(rej):.1%} of 500 samples')


# =============================================================================
# 2. STUDIUL DE CAZ S&P 500
# =============================================================================
def pesaran_timmermann(y, x):
    """Testul Pesaran-Timmermann (1992): H0 = semnul prognozat independent de cel realizat."""
    n = len(y); P = np.mean(y == x); py, px = y.mean(), x.mean()
    Ps = py * px + (1 - py) * (1 - px)
    VP = Ps * (1 - Ps) / n
    VPs = (2 * py - 1) ** 2 * px * (1 - px) / n + (2 * px - 1) ** 2 * py * (1 - py) / n \
        + 4 * py * px * (1 - py) * (1 - px) / n ** 2
    s = (P - Ps) / np.sqrt(VP - VPs)
    return P, Ps, s, 1 - stats.norm.cdf(s)


def hac_slope_t(y, x, lags=4):
    """Aceeasi ipoteza nula ca PT, cu erori Newey-West (etichete suprapuse)."""
    return sm.OLS(y, sm.add_constant(x)).fit(cov_type='HAC', cov_kwds={'maxlags': lags}).tvalues[1]


def delong_auc(y, s):
    pos, neg = s[y == 1], s[y == 0]
    V10 = np.array([(np.sum(p > neg) + 0.5 * np.sum(p == neg)) / len(neg) for p in pos])
    V01 = np.array([(np.sum(pos > q) + 0.5 * np.sum(pos == q)) / len(pos) for q in neg])
    return V10.mean(), np.sqrt(V10.var(ddof=1) / len(pos) + V01.var(ddof=1) / len(neg))


def cbb_index(n, L, rng):
    starts = rng.integers(0, n, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in starts])[:n] % n


def nw_mean(dvec, lags=4):
    r = sm.OLS(dvec, np.ones(len(dvec))).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    return r.params[0], r.tvalues[0], r.pvalues[0]


def giacomini_white(dL, tau=5):
    """Test conditionat GW, h_t = (1, dL_{t-tau}), varianta HAC cu tau-1 lag-uri (Bartlett)."""
    h = np.column_stack([np.ones(len(dL) - tau), dL[:-tau]])
    Z = h * dL[tau:, None]
    n = len(Z); Zb = Z.mean(0); Zc = Z - Zb
    Om = Zc.T @ Zc / n
    for l in range(1, tau):
        G = Zc[l:].T @ Zc[:-l] / n
        Om += (1 - l / tau) * (G + G.T)
    S = n * Zb @ np.linalg.solve(Om, Zb)
    return S, 1 - stats.chi2.cdf(S, Z.shape[1])


def ledoit_wolf_sharpe(a, b, lags=5, q=252):
    """Diferenta Sharpe (a - b), metoda delta cu varianta HAC (Ledoit & Wolf, 2008, sectiunea 3.1)."""
    T = len(a); Y = np.column_stack([a, b, a ** 2, b ** 2]); mu = Y.mean(0); Yc = Y - mu
    Psi = Yc.T @ Yc / T
    for l in range(1, lags + 1):
        G = Yc[l:].T @ Yc[:-l] / T
        Psi += (1 - l / (lags + 1)) * (G + G.T)
    m1, m2, g1, g2 = mu
    diff = m1 / np.sqrt(g1 - m1 ** 2) - m2 / np.sqrt(g2 - m2 ** 2)
    grad = np.array([g1 / (g1 - m1 ** 2) ** 1.5, -g2 / (g2 - m2 ** 2) ** 1.5,
                     -0.5 * m1 / (g1 - m1 ** 2) ** 1.5, 0.5 * m2 / (g2 - m2 ** 2) ** 1.5])
    se = np.sqrt(grad @ Psi @ grad / T)
    return diff * np.sqrt(q), se * np.sqrt(q), 2 * (1 - stats.norm.cdf(abs(diff / se)))


def case_study_section():
    print('== 2. S&P 500 case study ==')
    df = g.modelling_frame(0.25)
    feat = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    X, y = df[feat].values, df['y'].values
    cv = PurgedKFold(5, t1=df['t1'], pct_embargo=0.01)
    rng = np.random.default_rng(SEED)
    print(f'  n = {len(y)}, share up = {y.mean():.3f}')
    for name, model in g.get_models().items():
        p = np.full(len(y), np.nan)
        for tr, te in cv.split(X):
            model.fit(X[tr], y[tr]); p[te] = model.predict_proba(X[te])[:, 1]
        x = (p > 0.5).astype(int)
        P, Ps, s, pv = pesaran_timmermann(y, x)
        A, se = delong_auc(y, p)
        boots = [roc_auc_score(y[i], p[i]) for i in (cbb_index(len(y), 20, rng) for _ in range(1000))]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        print(f'  {name:18s}: acc {P:.3f}, P* {Ps:.3f}, PT {s:.2f} (p {pv:.2f}), HAC t {hac_slope_t(y, x):.2f}; '
              f'pooled AUC {A:.3f}, DeLong CI [{A - 1.96 * se:.3f}, {A + 1.96 * se:.3f}], block bootstrap CI [{lo:.3f}, {hi:.3f}]')
    # walk-forward 2010-2026
    wf = pd.DataFrame(index=df.index)
    for yr in range(2010, df.index[-1].year + 1):
        test = df.index[df.index.year == yr]; train = df.index[df['t1'] < test[0]]
        for nm, mdl in (('gbm', HistGradientBoostingClassifier(max_depth=3, learning_rate=0.03, max_iter=200,
                                                                min_samples_leaf=100, random_state=SEED)),
                        ('logit', make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000)))):
            mdl.fit(df.loc[train, feat], df.loc[train, 'y'])
            wf.loc[test, nm] = mdl.predict_proba(df.loc[test, feat])[:, 1]
        wf.loc[test, 'const'] = df.loc[train, 'y'].mean()
    wf = wf.dropna(); yw = df.loc[wf.index, 'y'].values
    ll = lambda p: -(yw * np.log(np.clip(p, 1e-6, 1)) + (1 - yw) * np.log(np.clip(1 - p, 1e-6, 1)))
    print(f'  walk-forward {wf.index[0].date()} - {wf.index[-1].date()}: n = {len(wf)}, share up = {yw.mean():.3f}')
    p0 = wf['const'].values
    for k in ('logit', 'gbm'):
        p1 = wf[k].values
        P, Ps, s, pv = pesaran_timmermann(yw, (p1 > 0.5).astype(int))
        m, t, pdm = nw_mean(ll(p1) - ll(p0))
        cw = (yw - p0) ** 2 - ((yw - p1) ** 2 - (p0 - p1) ** 2)
        _, tcw, _ = nw_mean(cw)
        S, pgw = giacomini_white(ll(p1) - ll(p0))
        print(f'  {k:5s}: acc {P:.3f} vs P* {Ps:.3f}, PT {s:.2f}; log loss {ll(p1).mean():.4f} vs constant {ll(p0).mean():.4f}; '
              f'DM t = {t:.2f} (p {pdm:.3f}); Clark-West t = {tcw:.2f} (one-sided p {1 - stats.norm.cdf(tcw):.2f}); '
              f'GW = {S:.2f} (p {pgw:.3f})')
    ret1 = np.log(g.spx).diff().shift(-1).reindex(wf.index)
    pos = (wf['gbm'] > 0.5).astype(float)
    strat = (pos * ret1 - pos.diff().abs().fillna(pos.iloc[0]) * 5 / 1e4).dropna()
    bh = ret1.loc[strat.index]
    for lab, rr in (('strategy', strat), ('buy-and-hold', bh)):
        sr = rr.mean() / rr.std(ddof=1)
        print(f'  {lab}: SR {sr * np.sqrt(252):.2f}, Lo (2002) iid SE {np.sqrt((1 + sr ** 2 / 2) / len(rr)) * np.sqrt(252):.2f}')
    diff, se, p = ledoit_wolf_sharpe(strat.values, bh.values)
    a, b = strat.values, bh.values
    bs = []
    for _ in range(2000):
        i = cbb_index(len(a), 20, rng)
        bs.append((a[i].mean() / a[i].std() - b[i].mean() / b[i].std()) * np.sqrt(252))
    print(f'  Sharpe difference {diff:.2f}, Ledoit-Wolf HAC SE {se:.3f}, p = {p:.3f}; '
          f'block bootstrap 95% CI {np.round(np.percentile(bs, [2.5, 97.5]), 2)}; corr = {np.corrcoef(a, b)[0, 1]:.3f}')


# =============================================================================
# 3. GRILA BTC: REALITY CHECK, SPA, ROMANO-WOLF
# =============================================================================
def stationary_bootstrap_index(n, q, rng):
    """Bootstrap stationar (Politis & Romano, 1994), lungime medie a blocului 1/q."""
    idx = np.empty(n, int); idx[0] = rng.integers(n)
    new = rng.random(n) < q; starts = rng.integers(0, n, n)
    for t in range(1, n):
        idx[t] = starts[t] if new[t] else (idx[t - 1] + 1) % n
    return idx


def snooping_tests(Dm, B=2000, q=1 / 20, seed=SEED, alpha=0.05):
    """White (2000) RC, Hansen (2005) SPA (p-valoare consistenta), Romano-Wolf (2005) StepM."""
    rng = np.random.default_rng(seed); n, K = Dm.shape
    dbar = Dm.mean(0)
    boots = np.array([Dm[stationary_bootstrap_index(n, q, rng)].mean(0) for _ in range(B)])
    omega = np.sqrt(n) * boots.std(0)
    tstat = np.sqrt(n) * dbar / omega
    p_rc = np.mean(np.max(np.sqrt(n) * (boots - dbar), 1) >= np.max(np.sqrt(n) * dbar))
    T_spa = max(tstat.max(), 0)
    mu_c = dbar * (tstat >= -np.sqrt(2 * np.log(np.log(n))))
    p_spa = np.mean(np.maximum((np.sqrt(n) * (boots - mu_c) / omega).max(1), 0) >= T_spa)
    Z = np.sqrt(n) * (boots - dbar) / omega
    active = np.ones(K, bool); rej = np.zeros(K, bool)
    while active.any():
        c = np.quantile(Z[:, active].max(1), 1 - alpha)
        new = active & (tstat > c)
        if not new.any():
            break
        rej |= new; active &= ~new
    return dict(max_t=float(tstat.max()), p_rc=float(p_rc), p_spa=float(p_spa), stepm=int(rej.sum()),
                naive=int((tstat > 1.645).sum()))


def btc_grid_section():
    print('== 3. BTC grid: data-snooping tests ==')
    btc = g.btc; r = np.log(btc).diff(); lp = np.log(btc)
    is_mask = btc.index < '2021-01-01'
    cols = {}
    for fast in range(2, 60, 3):
        for slow in range(10, 250, 10):
            if slow <= fast:
                continue
            for band in (0.0, 0.01, 0.03):
                sig = ((lp.rolling(fast).mean() - lp.rolling(slow).mean()) > band).astype(float).shift(1)
                cols[(fast, slow, band)] = sig * r
    M = pd.DataFrame(cols)
    Mis = M[is_mask].dropna()
    Mis = Mis.loc[:, (Mis.std() > 0) & (M[~is_mask].dropna().std() > 0)]
    bh = r.reindex(Mis.index)
    print(f'  {Mis.shape[1]} rules, in-sample n = {len(Mis)}')
    for lab, Dm in (('cash', Mis.values), ('buy-and-hold', Mis.values - bh.values[:, None])):
        print(f'  benchmark {lab}:', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in snooping_tests(Dm).items()})


# =============================================================================
# 4. SELECTIE DUBLA SI DML
# =============================================================================
def rlasso(y, X, c=1.1, iters=15):
    """LASSO cu penalizare plug-in si ponderi heteroscedastice (Belloni, Chernozhukov & Hansen, 2014)."""
    n, p = X.shape; gam = 0.1 / np.log(n)
    lam = 2 * c * np.sqrt(n) * stats.norm.ppf(1 - gam / (2 * p))
    yc = y - y.mean(); Xc = X - X.mean(0)
    psi = np.sqrt(np.mean((Xc ** 2) * (yc ** 2)[:, None], 0))
    sel = np.array([], int)
    for _ in range(iters):
        m = Lasso(alpha=lam / (2 * n), max_iter=50000).fit(Xc / psi, yc)
        sel = np.flatnonzero(m.coef_)
        e = yc - sm.OLS(yc, sm.add_constant(Xc[:, sel])).fit().fittedvalues if len(sel) else yc
        psi_new = np.sqrt(np.mean((Xc ** 2) * (e ** 2)[:, None], 0))
        if np.allclose(psi_new, psi, rtol=1e-4):
            break
        psi = psi_new
    return sel


def dml_section():
    print('== 4. Double selection and DML: log VIX -> 5-day S&P 500 return ==')
    df = g.modelling_frame(0.25)
    y = df['fwd'].values * 1e4
    base = [c for c in df.columns if c not in ('fwd', 'y', 't1', 'ffd_price', 'vix_level')]
    Z = (df[base] - df[base].mean()) / df[base].std()
    cols = {c: Z[c] for c in base}
    cols.update({c + '^2': Z[c] ** 2 for c in base})
    cols.update({a + '*' + b: Z[a] * Z[b] for a, b in itertools.combinations(base, 2)})
    X = pd.DataFrame(cols); X = ((X - X.mean()) / X.std()).values
    d = ((df['vix_level'] - df['vix_level'].mean()) / df['vix_level'].std()).values
    n, p = X.shape
    ols = lambda yv, Xv, lags=4: sm.OLS(yv, sm.add_constant(Xv)).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    r = ols(y, d)
    print(f'  n = {n}, controls p = {p}, sd(log VIX) = {df["vix_level"].std():.3f}; '
          f'OLS on log VIX alone: {r.params[1]:.1f} bp (HAC SE {r.bse[1]:.1f})')
    r = ols(y, np.column_stack([d, X]))
    print(f'  OLS with all {p} controls: {r.params[1]:.1f} bp (HAC SE {r.bse[1]:.1f})')
    sel = rlasso(y, np.column_stack([d, X]))
    print(f'  single LASSO of y on (VIX, controls): {len(sel)} regressors kept, VIX kept: {0 in sel}')
    Sy, Sd = rlasso(y, X), rlasso(d, X); U = sorted(set(Sy) | set(Sd))
    r = ols(y, np.column_stack([d, X[:, U]]))
    print(f'  post-double selection: |S_y| = {len(Sy)}, |S_d| = {len(Sd)}; theta = {r.params[1]:.1f} bp, '
          f'SE {r.bse[1]:.1f}, 95% CI [{r.params[1] - 1.96 * r.bse[1]:.1f}, {r.params[1] + 1.96 * r.bse[1]:.1f}]')
    folds = np.array_split(np.arange(n), 5); h = 5
    for learner in ('lasso', 'rf'):
        ut, vt = np.empty(n), np.empty(n)
        for te in folds:
            tr = np.setdiff1d(np.arange(n), np.arange(max(te[0] - h, 0), min(te[-1] + h + 1, n)))
            for target, res in ((y, ut), (d, vt)):
                if learner == 'lasso':
                    s_ = rlasso(target[tr], X[tr])
                    fit = sm.OLS(target[tr], sm.add_constant(X[tr][:, s_])).fit()
                    pred = fit.predict(sm.add_constant(X[te][:, s_], has_constant='add'))
                else:
                    pred = RandomForestRegressor(300, min_samples_leaf=50, max_features=0.3, n_jobs=-1,
                                                 random_state=SEED).fit(X[tr], target[tr]).predict(X[te])
                res[te] = target[te] - pred
        theta = np.sum(vt * ut) / np.sum(vt * vt)
        se = sm.OLS(ut, vt).fit(cov_type='HAC', cov_kwds={'maxlags': 4}).bse[0]
        print(f'  DML ({learner}, 5 contiguous folds, 5-day purge): theta = {theta:.1f} bp, SE {se:.1f}, '
              f'95% CI [{theta - 1.96 * se:.1f}, {theta + 1.96 * se:.1f}]')


# =============================================================================
# 5. CAMPBELL-THOMPSON
# =============================================================================
def campbell_thompson_section():
    print('== 5. Campbell-Thompson ==')
    s = g.spx.loc['2001-01-01':'2026-08-31']
    m = np.log(s.resample('ME').last()).diff().dropna()
    sr = m.mean() / m.std()
    print(f'  S&P 500 monthly log returns {m.index[0].date()} - {m.index[-1].date()}: SR {sr:.3f} ({sr * np.sqrt(12):.2f} annualised)')
    for R2 in (0.005, 0.01):
        s2 = np.sqrt((sr ** 2 + R2) / (1 - R2))
        print(f'  R2_OOS = {R2:.1%}: SR* = {s2 * np.sqrt(12):.2f} annualised (+{s2 / sr - 1:.0%})')


if __name__ == '__main__':
    memory_section()
    case_study_section()
    btc_grid_section()
    dml_section()
    campbell_thompson_section()

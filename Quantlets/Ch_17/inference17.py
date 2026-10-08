"""
inference17.py -- inferenta pentru afirmatiile in timp real din Capitolul 17 (MFM)
================================================================================
  1. size_study()     -- nivelul empiric (size) al testului GSADF la 5% sub ipoteza nula (mers aleator) cu
                         volatilitate variabila: valori critice Monte Carlo (dispersie constanta) vs wild bootstrap
                         (Harvey, Leybourne, Sollis & Taylor 2016); plus rata alarmelor false ale datarii BSADF.
  2. fwer_bitcoin()   -- multiplicitatea in datare: probabilitatea a cel putin unui episod fals cu valori critice
                         punctuale; valoarea critica bootstrap a maximului BSADF pe o fereastra de tau_b observatii
                         (Phillips & Shi 2020), aplicata la Bitcoin saptamanal.
  3. lppls_test()     -- indicatorul de incredere LPPLS: diferenta frecventelor scaderilor de 20% in 90 de zile dupa
                         semnal vs fara semnal; interval bootstrap pe blocuri circulare si regresie liniara de
                         probabilitate cu erori standard HAC (Newey-West).
  4. regimes_test()   -- numarul de regimuri Markov: LR 1 vs 2 regimuri (Bitcoin, Nasdaq 100) si 2 vs 3 regimuri
                         (Bitcoin), cu distributia nula prin bootstrap parametric (Hansen 1992; Carrasco, Hu &
                         Ploberger 2014: testul LR nu are distributie chi-patrat).
  5. gsy_ess()        -- marimea efectiva a esantionului pentru probabilitatea de crah dupa cresteri > 100%.
Rezultate: inference17.json; grafice: ch17_fwer_btc, ch17_ms_lr.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from multiprocessing import Pool
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import price   # noqa: E402
from bubbles import psy, psy_cv, wild_cv, episodes, min_window, _bsadf_paths   # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Purple, Orange, Teal, Amber, Gray, SEED, save_fig,  # noqa: E402
                                 legend_outside_bottom, fig_legend, jsonable, d2s, ci_evaluation, gsy_events, HERE, _chg)

PROCS = max(1, min(14, (os.cpu_count() or 2) - 2))


# =============================================================================
# 1. SIZE OF GSADF UNDER CHANGING VOLATILITY
# =============================================================================
SIZE_T = 400           # series length (T regression observations)
SIZE_N = 1000          # Monte Carlo paths per scenario
SIZE_B = 199           # wild bootstrap replications per path
SCENARIOS = {'iid': 'Constant volatility',
             'up': 'Volatility triples at T/2',
             'down': 'Volatility falls to one third at T/2',
             'garch': 'GARCH(1,1), alpha = 0.10, beta = 0.88'}


def null_shocks(kind, T, rng):
    """Shocks with unconditional variance 1 (i.i.d.) or with changing volatility."""
    z = rng.standard_normal(T)
    if kind == 'iid':
        return z
    if kind == 'up':
        return z * np.where(np.arange(T) < T // 2, 1.0, 3.0)
    if kind == 'down':
        return z * np.where(np.arange(T) < T // 2, 3.0, 1.0)
    if kind == 'garch':                               # sigma2_t = w + a e_{t-1}^2 + b sigma2_{t-1}, unconditional variance 1
        a, b = 0.10, 0.88
        w = 1 - a - b
        zz = rng.standard_normal(T + 500)
        e = np.empty(T + 500)
        s2 = 1.0
        for t in range(T + 500):
            e[t] = np.sqrt(s2) * zz[t]
            s2 = w + a * e[t] ** 2 + b * s2
        return e[500:]
    raise ValueError(kind)


def _size_worker(args):
    """One path under H0: GSADF, the decision with the MC and the wild-bootstrap critical value, false episodes (BSADF)."""
    kind, i, cv_mc, bs95_mc, L = args
    rng = np.random.default_rng([SEED, i, list(SCENARIOS).index(kind)])
    e = null_shocks(kind, SIZE_T, rng)
    y = np.concatenate([[0.0], np.cumsum(1.0 / SIZE_T + e)])        # random walk with an asymptotically negligible drift
    res = psy(y)
    wc = wild_cv(y, res['w0'], SIZE_B, seed=int(rng.integers(1 << 31)))
    ep_mc = episodes(res['bsadf'], bs95_mc, np.arange(len(res['bsadf'])), L)
    ep_w = episodes(res['bsadf'], wc['bsadf95'], np.arange(len(res['bsadf'])), L)
    return dict(rej_mc=res['gsadf'] > cv_mc, rej_wild=res['gsadf'] > wc['gsadf95'],
                ep_mc=len(ep_mc) > 0, ep_wild=len(ep_w) > 0,
                any_mc=bool(np.nanmax(res['bsadf'] - bs95_mc) > 0))


def size_study():
    w0, r0 = min_window(SIZE_T)
    cv = psy_cv(SIZE_T, w0, 2000, SEED)
    L = int(np.ceil(np.log(SIZE_T)))
    out = dict(T=SIZE_T, w0=w0, r0=r0, L=L, N=SIZE_N, B=SIZE_B, cv_mc=cv['gsadf']['95'], rows={})
    with Pool(PROCS) as pool:
        for kind in SCENARIOS:
            res = pool.map(_size_worker, [(kind, i, cv['gsadf']['95'], cv['bsadf95'], L) for i in range(SIZE_N)],
                           chunksize=8)
            d = pd.DataFrame(res)
            out['rows'][kind] = dict(label=SCENARIOS[kind], size_mc=float(d.rej_mc.mean()), size_wild=float(d.rej_wild.mean()),
                                     fp_mc=float(d.ep_mc.mean()), fp_wild=float(d.ep_wild.mean()),
                                     any_mc=float(d.any_mc.mean()))
            print('size', kind, out['rows'][kind])
    out['mc_se'] = float(np.sqrt(0.05 * 0.95 / SIZE_N))
    return out


# =============================================================================
# 2. MULTIPLICITY IN DATE-STAMPING: WEEKLY BITCOIN
# =============================================================================
TAU_B = 104            # window of family-wise type I error control: 2 years of weekly data
PS_B = 999             # bootstrap replications


def ps_fwer_cv(y, w0, tau_b=TAU_B, B=PS_B, seed=SEED):
    """Phillips & Shi (2020): residuals of the regression under H0 (Delta y_t = a + e_t), drawn with replacement and
    multiplied by N(0,1) weights, build paths of w0 + tau_b - 1 changes; the critical value is the 95% quantile of the
    maximum of BSADF over the last tau_b dates of each path."""
    rng = np.random.default_rng(seed)
    dy = np.diff(np.asarray(y, float))
    eps = dy - dy.mean()
    n = w0 + tau_b - 1
    E = eps[rng.integers(0, len(eps), size=(B, n))] * rng.standard_normal((B, n))
    Y = np.concatenate([np.zeros((B, 1)), np.cumsum(E, axis=1)], axis=1)
    bs, _ = _bsadf_paths(Y, w0)
    mx = np.nanmax(bs, axis=1)
    return dict(q90=float(np.quantile(mx, 0.90)), q95=float(np.quantile(mx, 0.95)), q99=float(np.quantile(mx, 0.99)))


def fwer_bitcoin(R=2000):
    y = np.log(price('btc', 'W'))
    res = psy(y.values)
    n, w0 = res['n'], res['w0']
    L = int(np.ceil(np.log(n)))
    idx = y.index[1:]
    # probability of a false alarm anywhere in the sample, with pointwise 95% critical values (Monte Carlo H0)
    rng = np.random.default_rng(SEED)
    e = rng.standard_normal((R, n))
    Y = np.concatenate([np.zeros((R, 1)), np.cumsum(1.0 / n + e, axis=1)], axis=1)
    bs, _ = _bsadf_paths(Y, w0)
    q95 = np.nanquantile(bs, 0.95, axis=0)
    any_exc = np.nanmax(bs - q95, axis=1) > 0
    ep_any = np.array([len(episodes(b, q95, np.arange(n), L)) > 0 for b in bs])
    # over a window of TAU_B consecutive dates (the last TAU_B)
    last = slice(n - TAU_B, n)
    any_last = np.nanmax(bs[:, last] - q95[last], axis=1) > 0
    ps = ps_fwer_cv(y.values, w0)
    wc = wild_cv(y.values, w0, 1000, SEED)
    cvmc = psy_cv(n, w0, 2000, SEED)
    ep_ps = episodes(res['bsadf'], np.full(n, ps['q95']), idx, L)
    ep_mc = episodes(res['bsadf'], cvmc['bsadf95'], idx, L)
    ep_w = episodes(res['bsadf'], wc['bsadf95'], idx, L)
    fmt = lambda eps: [dict(start=d2s(s), end=d2s(e_), n=int(k), change=_chg(y, s, e_)) for s, e_, k in eps]
    # chart: BSADF with three thresholds
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.plot(idx, res['bsadf'], color=IDAred, lw=0.9, label='BSADF statistic, Bitcoin weekly')
    ax.plot(idx, cvmc['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% pointwise critical value, Monte Carlo')
    ax.plot(idx, wc['bsadf95'], color=Purple, lw=1.0, ls='-.', label='95% pointwise critical value, wild bootstrap')
    ax.axhline(ps['q95'], color=Orange, lw=1.2, label=f'Family-wise 95% critical value over {TAU_B} weeks (Phillips-Shi)')
    for s, e_, _ in ep_ps:
        ax.axvspan(s, e_ if e_ is not None else idx[-1], color=Amber, alpha=0.25, lw=0)
    ax.fill_between([], [], color=Amber, alpha=0.25, label='Episodes with the family-wise critical value')
    ax.set_ylabel('Statistic')
    ax.set_title('Bitcoin, weekly 2014-2026: pointwise vs family-wise critical values for date-stamping', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch17_fwer_btc')
    return dict(T=n, w0=w0, L=L, R=R, tau_b=TAU_B, B=PS_B, fwer_any=float(any_exc.mean()), fwer_ep=float(ep_any.mean()),
                fwer_last_tau=float(any_last.mean()), cv_ps=ps, cv_mc_max=float(np.nanmax(cvmc['bsadf95'])),
                cv_mc_last=float(cvmc['bsadf95'][-1]), cv_w_max=float(np.nanmax(wc['bsadf95'])),
                episodes_ps=fmt(ep_ps), episodes_mc=fmt(ep_mc), episodes_wild=fmt(ep_w), gsadf=res['gsadf'])


# =============================================================================
# 3. LPPLS CONFIDENCE INDICATOR: SIGNAL VS NO SIGNAL
# =============================================================================
def lppls_hits(ci, p, horizon=90, fall=0.20):
    """Only dates whose `horizon` calendar days are fully observed (no censored outcomes at the end)."""
    rows = []
    for d, v in ci.items():
        if d + pd.Timedelta(days=horizon) > p.index[-1]:
            continue
        fut = p.loc[d:d + pd.Timedelta(days=horizon)]
        rows.append(dict(date=d, sig=float(v > 0), hit=float(fut.min() / fut.iloc[0] - 1 <= -fall)))
    return pd.DataFrame(rows).set_index('date')


def circular_block_ci(s, h, block, B=9999, seed=SEED):
    """Circular block bootstrap of the (signal, outcome) pairs: distribution of the difference p_on - p_off."""
    rng = np.random.default_rng(seed)
    n = len(s)
    k = int(np.ceil(n / block))
    st = rng.integers(0, n, size=(B, k))
    ix = ((st[:, :, None] + np.arange(block)[None, None, :]) % n).reshape(B, -1)[:, :n]
    S, H = s[ix], h[ix]
    non = S.sum(1)
    ok = (non > 0) & (non < n)
    d = (H * S).sum(1)[ok] / non[ok] - (H * (1 - S)).sum(1)[ok] / (n - non[ok])
    return d


def hac_lpm(s, h, lags):
    """Linear probability regression h = a + b s + u, Newey-West standard error with `lags` lags."""
    import statsmodels.api as sm
    X = sm.add_constant(s)
    r = sm.OLS(h, X).fit(cov_type='HAC', cov_kwds=dict(maxlags=lags))
    return dict(b=float(r.params[1]), se=float(r.bse[1]), t=float(r.tvalues[1]), p=float(r.pvalues[1]))


def lppls_test():
    out = {}
    for key, fname, start in [('btc', 'ch17_lppls_ci_btc.csv', '2014-09-17'), ('ndx', 'ch17_lppls_ci_ndx.csv', '1994-01-01')]:
        ci = pd.read_csv(os.path.join(HERE, fname), index_col=0, parse_dates=True)['ci']
        p = price(key, 'D', start)
        d = lppls_hits(ci, p)
        gap = float(np.median(np.diff(d.index.values).astype('timedelta64[D]').astype(float)))
        block = int(np.ceil(90 / gap))                      # one block = the 90-day horizon
        s, h = d['sig'].values, d['hit'].values
        diff = h[s == 1].mean() - h[s == 0].mean()
        bd = circular_block_ci(s, h, block)
        hac = hac_lpm(s, h, block)
        n_on = int(s.sum())
        # effective size: the number of independent 90-day blocks containing signals
        out[key] = dict(n=int(len(d)), n_on=n_on, p_on=float(h[s == 1].mean()), p_off=float(h[s == 0].mean()),
                        diff=float(diff), block=block, gap_days=gap, ci_lo=float(np.quantile(bd, 0.025)),
                        ci_hi=float(np.quantile(bd, 0.975)), boot_se=float(bd.std()),
                        naive_se=float(np.sqrt(h[s == 1].mean() * (1 - h[s == 1].mean()) / max(n_on, 1)
                                               + h[s == 0].mean() * (1 - h[s == 0].mean()) / (len(d) - n_on))),
                        hac=hac, first=d2s(d.index[0]), last=d2s(d.index[-1]))
        print('lppls', key, out[key])
    return out


# =============================================================================
# 4. NUMBER OF MARKOV REGIMES: PARAMETRIC-BOOTSTRAP LR
# =============================================================================
MS_B = 199
MS_REPS = 20


def ms_llf(r, k, reps=MS_REPS, seed=None):
    """Maximised log-likelihood: k = 1 (i.i.d. Normal distribution, closed form) or Markov switching with k regimes."""
    r = np.asarray(r, float)
    if k == 1:
        s2 = r.var()
        return float(-0.5 * len(r) * (np.log(2 * np.pi * s2) + 1)), None
    import statsmodels.api as sm
    if seed is not None:
        np.random.seed(seed)
    best = None
    try:
        res = sm.tsa.MarkovRegression(r, k_regimes=k, trend='c', switching_variance=True).fit(
            search_reps=reps, maxiter=500, disp=False)
        best = res
    except Exception:
        pass
    return (float(best.llf), best) if best is not None else (np.nan, None)


def ms_simulate(params, n, rng):
    """Simulate returns from a Markov-switching model: mu, sd (lists) and P[i, j] = P(s_t = j | s_{t-1} = i)."""
    mu, sd, P = np.asarray(params['mu']), np.asarray(params['sd']), np.asarray(params['P'])
    k = len(mu)
    w, v = np.linalg.eig(P.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    pi = pi / pi.sum()
    s = np.empty(n, int)
    s[0] = rng.choice(k, p=pi)
    u = rng.random(n)
    cum = np.cumsum(P, axis=1)
    for t in range(1, n):
        s[t] = min(int(np.searchsorted(cum[s[t - 1]], u[t])), k - 1)
    return mu[s] + sd[s] * rng.standard_normal(n)


def ms_params(res, k):
    P = np.asarray(res.regime_transition)[:, :, 0].T          # statsmodels stores [i, j] = P(s_t = i | s_{t-1} = j); transposed to P[i, j] = P(s_t = j | s_{t-1} = i)
    par = dict(zip(res.model.param_names, np.asarray(res.params)))
    return dict(mu=[float(par[f'const[{j}]']) for j in range(k)],
                sd=[float(np.sqrt(par[f'sigma2[{j}]'])) for j in range(k)], P=P.tolist())


def _lr_worker(args):
    k0, params, n, i = args
    rng = np.random.default_rng([SEED, k0, i])
    x = ms_simulate(params, n, rng)
    l0, _ = ms_llf(x, k0, seed=i)
    l1, _ = ms_llf(x, k0 + 1, seed=i)
    return 2 * (l1 - l0)


def lr_boot(r, k0, B=MS_B):
    l0, res0 = ms_llf(r, k0, seed=SEED)
    l1, _ = ms_llf(r, k0 + 1, seed=SEED)
    lr = 2 * (l1 - l0)
    if k0 == 1:
        params = dict(mu=[float(np.mean(r))], sd=[float(np.std(r))], P=[[1.0]])
    else:
        params = ms_params(res0, k0)
    with Pool(PROCS) as pool:
        lrs = np.array(pool.map(_lr_worker, [(k0, params, len(r), i) for i in range(B)], chunksize=2))
    lrs = lrs[np.isfinite(lrs)]
    from scipy import stats
    df = 4 if k0 == 1 else 6          # extra parameters: 1 vs 2: mu, sigma, p11, p22; 2 vs 3: mu, sigma + 4 transition probabilities
    return dict(k0=k0, llf0=l0, llf1=l1, lr=float(lr), B=int(len(lrs)), p_boot=float((1 + (lrs >= lr).sum()) / (len(lrs) + 1)),
                q95=float(np.quantile(lrs, 0.95)), q99=float(np.quantile(lrs, 0.99)), lr_max=float(lrs.max()),
                chi2_df=df, chi2_95=float(stats.chi2.ppf(0.95, df)), lrs=lrs.tolist())


def regimes_test(out=None):
    out = dict(out or {})
    for key, start in [('btc', '2014-09-17'), ('ndx', '1990-01-01')]:
        if f'{key}_1v2' in out:
            continue
        r = (100 * np.log(price(key, 'W', start)).diff().dropna()).values
        out[f'{key}_1v2'] = lr_boot(r, 1)
        print('regimes', key, '1v2', {k: v for k, v in out[f'{key}_1v2'].items() if k != 'lrs'})
    r = (100 * np.log(price('btc', 'W')).diff().dropna()).values
    if 'btc_2v3' not in out:
        out['btc_2v3'] = lr_boot(r, 2)
    print('regimes btc 2v3', {k: v for k, v in out['btc_2v3'].items() if k != 'lrs'})
    # chart: bootstrap distributions of LR and the chi-square quantile
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9))
    for ax, (tag, title) in zip(axes, [('btc_1v2', 'Bitcoin: one vs two regimes'), ('btc_2v3', 'Bitcoin: two vs three regimes')]):
        o = out[tag]
        ax.hist(o['lrs'], bins=30, color=MainBlue, alpha=0.7, label='Parametric-bootstrap LR under the null')
        ax.axvline(o['q95'], color=Forest, ls='--', lw=1.1, label='Bootstrap 95% critical value')
        ax.axvline(o['chi2_95'], color=Purple, ls=':', lw=1.3, label='Naive chi-square 95% value')
        if o['lr'] <= 3 * max(o['lr_max'], o['chi2_95']):
            ax.axvline(o['lr'], color=IDAred, lw=1.4, label='Observed LR')
        ax.set_title(title + (f' (observed LR = {o["lr"]:.0f})' if o['lr'] > 3 * max(o['lr_max'], o['chi2_95']) else ''),
                     fontsize=8.5, loc='left')
        ax.set_xlabel('LR statistic')
    axes[0].set_ylabel('Count')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_ms_lr')
    return out


# =============================================================================
# 5. BUBBLES FOR FAMA: EFFECTIVE SAMPLE SIZE
# =============================================================================
def gsy_ess(thr=1.0, B=2000):
    d = gsy_events(thr)
    rng = np.random.default_rng(SEED)
    g = {y: grp['crash'].values.astype(float) for y, grp in d.groupby(d['date'].dt.year)}
    keys = list(g)
    st = []
    for _ in range(B):
        pick = rng.choice(len(keys), len(keys), replace=True)
        st.append(np.concatenate([g[keys[j]] for j in pick]).mean())
    p = float(d['crash'].mean())
    se = float(np.std(st))
    # sensitivity: moving-block bootstrap of k consecutive calendar years (keeps the dependence between
    # the 2-year windows of events in neighbouring years), k = 2, 3, 5
    years = np.arange(d['date'].dt.year.min(), d['date'].dt.year.max() + 1)
    se_blocks = {}
    for k in (2, 3, 5):
        nb = int(np.ceil(len(years) / k))
        vals = []
        for _ in range(B):
            starts = rng.integers(0, len(years) - k + 1, nb)
            pick = np.concatenate([years[a:a + k] for a in starts])[:len(years)]
            v = np.concatenate([g[y] for y in pick if y in g] or [np.array([])])
            if len(v):
                vals.append(v.mean())
        se_blocks[str(k)] = float(np.std(vals))
    return dict(n=int(len(d)), n_years=int(len(keys)), n_ind=int(d['ind'].nunique()), p=p, se_boot=se, se_block=se_blocks,
                se_binom=float(np.sqrt(p * (1 - p) / len(d))), ess=float(p * (1 - p) / se ** 2),
                deff=float(se ** 2 / (p * (1 - p) / len(d))))


def main():
    what = sys.argv[1:] or ['size', 'fwer', 'lppls', 'regimes', 'gsy']
    path = os.path.join(HERE, 'inference17.json')
    OUT = json.load(open(path)) if os.path.exists(path) else {}
    if 'gsy' in what:
        OUT['gsy_ess'] = gsy_ess()
        print(OUT['gsy_ess'])
    if 'fwer' in what:
        OUT['fwer'] = fwer_bitcoin()
        print({k: v for k, v in OUT['fwer'].items()})
    if 'lppls' in what:
        OUT['lppls'] = lppls_test()
    if 'size' in what:
        OUT['size'] = size_study()
    if 'regimes' in what:
        OUT['regimes'] = regimes_test(OUT.get('regimes'))
    with open(path, 'w') as f:
        json.dump(jsonable(OUT), f, indent=1)
    print('saved inference17.json')


if __name__ == '__main__':
    main()

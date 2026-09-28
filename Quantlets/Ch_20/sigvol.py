"""
sigvol.py -- signatures, two-step adaptive LASSO with signature-kernel weights and HAR benchmarks
===================================================================================================
Chapter 20 (special chapter) of Modelling Financial Markets (MFM): the method of Gu, Guo, Jacobs, Kaminsky & Li
(2024, KDD; arXiv:2401.04857) transferred to forecasting daily realised variance on the VOLARE database.

Data: VOLARE (Cipollini, Cruciani, Gallo, Insana, Otranto & Spagnolo, 2026, arXiv:2602.19732), licensed for research
use and not redistributed: download the realised-variance files free from http://volare.unime.it and put
realized_variance_stocks.csv, realized_variance_futures.csv and realized_variance_forex.csv in a folder; set
VOLARE_DIR (environment variable or the constant below) to that folder.

Contents
  * truncated signatures of piecewise-linear paths in numpy (Chen's identity), rolling over windows
  * the signature kernel k(a, b) = <S^N(a), S^N(b)> and distance d(a, b) = k(a,a) - 2k(a,b) + k(b,b)
  * kernel weights w_tau = exp(-gamma d_tau) / sum exp(-gamma d_tau)          (Gu et al., 2024, Eq. 12)
  * two-step LASSO: weighted LASSO path (LARS), OLS refit on the support, lambda by BIC   (Eqs. 14-15)
  * benchmarks HAR, log-HAR, HARQ, SHAR; rolling window, re-estimation every K days
  * losses (QLIKE, MSE), Diebold-Mariano with HAC, Giacomini-White, model confidence set
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import itertools
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import lars_path

# -----------------------------------------------------------------------------
# DATA
# -----------------------------------------------------------------------------
VOLARE_DIR = os.environ.get('VOLARE_DIR', '')
if not VOLARE_DIR:
    VOLARE_DIR = next((os.path.join(d, 'data', 'volare') for d in ('.', '..', '../..', '../../..')
                       if os.path.isdir(os.path.join(d, 'data', 'volare'))), 'data/volare')
CLASSES = ('stocks', 'futures', 'forex')
COLS = ['date', 'symbol', 'open_price', 'close_price', 'rv5', 'rsp5', 'rsn5', 'rq5', 'rk']
_RAW = {}


def load_class(kind):
    """All realised measures of one VOLARE asset class (stocks, futures, forex)."""
    if kind not in _RAW:
        f = os.path.join(VOLARE_DIR, f'realized_variance_{kind}.csv')
        _RAW[kind] = pd.read_csv(f, usecols=COLS, parse_dates=['date'])
    return _RAW[kind]


def load_asset(kind, symbol):
    """Daily series of one asset: rv (5-minute RV), semivariances, quarticity, kernel, open-to-close return."""
    d = load_class(kind)
    d = d[d.symbol == symbol].sort_values('date').set_index('date')
    out = pd.DataFrame({'rv': d.rv5, 'rsp': d.rsp5, 'rsn': d.rsn5, 'rq': d.rq5, 'rk': d.rk,
                        'r': np.log(d.close_price / d.open_price)})
    out = out[(out.rv > 0) & (out.rsp >= 0) & (out.rsn >= 0) & (out.rq > 0) & np.isfinite(out.r)]
    return out[~out.index.duplicated()]


def symbols(kind):
    return sorted(load_class(kind).symbol.unique())


# -----------------------------------------------------------------------------
# SIGNATURES (numpy, Chen's identity)
# -----------------------------------------------------------------------------
def sig_words(d, depth):
    """Multi-indices (words) of the truncated signature, levels 1..depth, in the order of sig_windows."""
    return [w for k in range(1, depth + 1) for w in itertools.product(range(d), repeat=k)]


def sig_path(path, depth=3):
    """Truncated signature (levels 1..depth) of the piecewise-linear path through the rows of `path` (m x d)."""
    return sig_windows(np.asarray(path, float), len(path), depth)[-1]


def _outer(A, B):
    """Row-wise tensor product of flattened tensors: (m, d^a) x (m, d^b) -> (m, d^(a+b)), lexicographic order."""
    return (A[:, :, None] * B[:, None, :]).reshape(A.shape[0], -1)


def sig_windows(x, l, depth=3):
    """Signatures of all rolling windows of l points of the path x (n x d); row i = window ending at point i.

    Chen's identity: S(X * Y) = S(X) (x) S(Y); a linear segment with increment D has S = exp(D) =
    (1, D, D(x)D/2!, D(x)D(x)D/3!, ...), so level k of the updated signature is
    sum_{p=0..k} S_old^(k-p) (x) D^(x)p / p!.  Rows i < l-1 are NaN."""
    x = np.asarray(x, float)
    n, d = x.shape
    m = n - l + 1
    lev = [np.ones((m, 1))] + [np.zeros((m, d ** k)) for k in range(1, depth + 1)]
    for j in range(l - 1):
        D = x[j + 1:j + 1 + m] - x[j:j + m]                        # increment of segment j in every window
        pw = [np.ones((m, 1))]
        for p in range(1, depth + 1):
            pw.append(_outer(pw[-1], D) / p)                       # D^(x)p / p!
        lev = [lev[0]] + [sum(_outer(lev[k - p], pw[p]) for p in range(0, k + 1)) for k in range(1, depth + 1)]
    flat = np.concatenate(lev[1:], axis=1)
    out = np.full((n, flat.shape[1]), np.nan)
    out[l - 1:] = flat
    return out


def sig_scale(scales, depth=3):
    """Signature of a path whose channel c is multiplied by scales[c]: level-k word (i1..ik) scales by prod."""
    return np.array([np.prod([scales[i] for i in w]) for w in sig_words(len(scales), depth)])


def levy_area(path):
    """Levy area of the first two channels: (S^(1,2) - S^(2,1)) / 2."""
    S = sig_path(path, 2)
    d = np.asarray(path).shape[1]
    s2 = S[d:].reshape(d, d)
    return 0.5 * (s2[0, 1] - s2[1, 0])


def sig_kernel(Sa, Sb):
    """Truncated signature kernel <S^N(a), S^N(b)> including the level-0 term 1."""
    return 1.0 + np.dot(Sa, Sb)


def sig_distance(Sa, Sb):
    """d_Sig(a, b) = k(a,a) - 2 k(a,b) + k(b,b) = ||S^N(a) - S^N(b)||^2."""
    return sig_kernel(Sa, Sa) - 2 * sig_kernel(Sa, Sb) + sig_kernel(Sb, Sb)


# -----------------------------------------------------------------------------
# DESIGN (pre-registered, fixed before any out-of-sample result)
# -----------------------------------------------------------------------------
CFG = dict(
    W=1000,             # rolling estimation window (days of (x_tau, y_tau+h) pairs)
    K=5,                # re-estimation every K trading days (parameters fixed in between)
    L=22,               # signature lookback (points in the path), one trading month
    DEPTH=3,            # truncation depth N
    HORIZONS=(1, 5, 22),
    VAL=250,            # validation block: first 250 forecast days of every asset (only for choosing c)
    C_GRID=(0.5, 1.0, 2.0, 4.0),   # gamma = c / median(d_tau)
    CHANNELS=('t', 'logrv', 'cumret'),
)
MODELS = ['HAR', 'logHAR', 'HARQ', 'SHAR', 'logHAR-K', 'Sig-L', 'Sig-LK']
LABEL = {'HAR': 'HAR', 'logHAR': 'log-HAR', 'HARQ': 'HARQ', 'SHAR': 'SHAR', 'logHAR-K': 'log-HAR + kernel weights',
         'Sig-L': 'Signature LASSO', 'Sig-LK': 'Signature LASSO + kernel weights'}


def har_parts(v):
    """Daily, weekly (5-day) and monthly (22-day) averages of a series ending at each day."""
    s = pd.Series(v)
    return np.c_[s.values, s.rolling(5).mean().values, s.rolling(22).mean().values]


def build_design(a, h, cfg=CFG):
    """Features and targets of one asset for horizon h (arrays aligned on the asset's trading days)."""
    rv = a.rv.values
    n = len(rv)
    lrv = np.log(rv)
    y = pd.Series(rv).rolling(h).mean().shift(-h).values       # mean RV over days t+1..t+h
    H = har_parts(rv)
    D = dict(dates=a.index, rv=rv, y=y, ly=np.log(y), n=n, h=h)
    D['X_har'] = H
    D['X_loghar'] = np.log(H)
    D['sqrq'] = np.sqrt(a.rq.values)
    D['X_shar'] = np.c_[a.rsp.values, a.rsn.values, H[:, 1], H[:, 2]]
    # path for the signature: (time, log RV, cumulative open-to-close return), channels as in cfg
    chan = {'t': np.arange(n, dtype=float) / (cfg['L'] - 1), 'logrv': lrv, 'cumret': np.cumsum(a.r.values),
            'rsn': np.log(np.maximum(a.rsn.values, 1e-12))}
    P = np.column_stack([chan[c] for c in cfg['CHANNELS']])
    D['path'] = P
    D['sig'] = sig_windows(P, cfg['L'], cfg['DEPTH'])
    D['incr'] = np.r_[np.full((1, P.shape[1]), np.nan), np.diff(P, axis=0)]
    return D


# -----------------------------------------------------------------------------
# ESTIMATION
# -----------------------------------------------------------------------------
def wls(X, y, w):
    """Weighted least squares with intercept; returns coefficients (b0, b) and weighted residual variance."""
    Z = np.c_[np.ones(len(y)), X]
    sw = np.sqrt(w)
    b, *_ = np.linalg.lstsq(Z * sw[:, None], y * sw, rcond=None)
    e = y - Z @ b
    return b, float(np.sum(w * e ** 2) / np.sum(w))


def two_step_lasso(X, y, w, max_steps=60):
    """Weighted LASSO path (LARS) -> OLS refit on each support -> BIC with Kish effective sample size.

    Step 1 (Gu et al., 2024, Eq. 14): min_theta sum_tau w_tau (y - x theta)^2 + lambda ||theta||_1.
    Step 2 (Eq. 15): weighted OLS on supp(theta_LASSO).  lambda chosen by BIC inside the window."""
    w = w / w.sum()
    n_eff = 1.0 / np.sum(w ** 2)
    mx = w @ X
    my = w @ y
    sd = np.sqrt(w @ (X - mx) ** 2)
    keep = sd > 1e-12
    Xs = (X[:, keep] - mx[keep]) / sd[keep]
    sw = np.sqrt(w)
    _, _, coefs = lars_path(Xs * sw[:, None], (y - my) * sw, method='lasso', max_iter=max_steps)
    idx = np.where(keep)[0]
    best, seen = None, set()
    for j in range(coefs.shape[1]):
        S = tuple(idx[np.abs(coefs[:, j]) > 0])
        if S in seen:
            continue
        seen.add(S)
        b, s2 = wls(X[:, list(S)], y, w) if S else (np.array([my]), float(w @ (y - my) ** 2))
        bic = n_eff * np.log(s2) + (len(S) + 1) * np.log(n_eff)
        if best is None or bic < best[0]:
            best = (bic, S, b, s2)
    _, S, b, s2 = best
    beta = np.zeros(X.shape[1])
    beta[list(S)] = b[1:]
    return b[0], beta, s2, S


def kernel_weights(sig_train, sig_now, scale, c):
    """w_tau proportional to exp(-gamma d_Sig(window tau, current window)), gamma = c / median(d)."""
    diff = (sig_train - sig_now) * scale
    d = np.sum(diff ** 2, axis=1)
    g = c / np.median(d)
    z = -g * d
    w = np.exp(z - z.max())
    return w / w.sum(), d


def insanity(fc, models):
    """Bollerslev, Patton & Quaedvlieg (2016) filter: a forecast outside the range of the target in the estimation
    window is replaced by the window mean (columns lo, hi, mu of a forecast table)."""
    out = fc.copy()
    for m in models:
        bad = (fc[m] < fc.lo) | (fc[m] > fc.hi)
        out.loc[bad, m] = fc.mu[bad]
    return out


def fit_models(D, t, cfg, c_sig, c_har, models=MODELS, keep_weights=False):
    """Estimate every model at origin t (information up to day t); return a dict of forecast functions."""
    h, W, L = D['h'], cfg['W'], cfg['L']
    tr = np.arange(t - h - W + 1, t - h + 1)                     # tau with tau + h <= t
    y, ly = D['y'][tr], D['ly'][tr]
    uni = np.full(len(tr), 1.0 / len(tr))
    out, info = {}, {}
    if 'HAR' in models:
        b, _ = wls(D['X_har'][tr], y, uni)
        out['HAR'] = ('lvl', b, None, 0.0)
    if 'logHAR' in models:
        b, s2 = wls(D['X_loghar'][tr], ly, uni)
        out['logHAR'] = ('log', b, None, s2)
    if 'HARQ' in models:
        mq = D['sqrq'][tr].mean()
        X = np.c_[D['X_har'][tr, 0], D['X_har'][tr, 0] * (D['sqrq'][tr] - mq), D['X_har'][tr, 1:]]
        b, _ = wls(X, y, uni)
        out['HARQ'] = ('harq', b, mq, 0.0)
    if 'SHAR' in models:
        b, _ = wls(D['X_shar'][tr], y, uni)
        out['SHAR'] = ('shar', b, None, 0.0)
    need_sig = any(m in models for m in ('Sig-L', 'Sig-LK', 'logHAR-K'))
    if need_sig:
        # channel scales from the training window: each non-time channel / (sd of daily increments * sqrt(L-1))
        inc = D['incr'][tr[0]:t + 1]
        sc = []
        for j, cname in enumerate(cfg['CHANNELS']):
            sc.append(1.0 if cname == 't' else 1.0 / (np.nanstd(inc[:, j]) * np.sqrt(L - 1)))
        scale = sig_scale(np.array(sc), cfg['DEPTH'])
        Str = D['sig'][tr]
        Xsig = np.c_[D['X_loghar'][tr], Str * scale]
        if 'Sig-L' in models:
            b0, beta, s2, sup = two_step_lasso(Xsig, ly, uni)
            out['Sig-L'] = ('sig', np.r_[b0, beta], scale, s2)
            info['k_Sig-L'] = len(sup)
            info['S_Sig-L'] = ' '.join(map(str, sup))
        wk, dist = kernel_weights(Str, D['sig'][t], scale, c_sig)
        if 'Sig-LK' in models:
            b0, beta, s2, sup = two_step_lasso(Xsig, ly, wk)
            out['Sig-LK'] = ('sig', np.r_[b0, beta], scale, s2)
            info['k_Sig-LK'] = len(sup)
            info['S_Sig-LK'] = ' '.join(map(str, sup))
            info['ess'] = 1.0 / np.sum(wk ** 2)
            top = D['rv'][tr] >= np.quantile(D['rv'][tr], 0.9)
            info['hv_share'] = float(wk[top].sum())             # weight on the 10% most volatile training days
            info['date'] = D['dates'][t]
            if keep_weights:
                info['weights'] = pd.Series(wk, index=D['dates'][tr])
        if 'logHAR-K' in models:
            wh = wk if c_har == c_sig else kernel_weights(Str, D['sig'][t], scale, c_har)[0]
            b, s2 = wls(D['X_loghar'][tr], ly, wh)
            out['logHAR-K'] = ('log', b, None, s2)
    return out, info, (y.min(), y.max(), y.mean())


def predict(D, s, spec):
    kind, b, extra, s2 = spec
    if kind == 'lvl':
        return b[0] + D['X_har'][s] @ b[1:]
    if kind == 'shar':
        return b[0] + D['X_shar'][s] @ b[1:]
    if kind == 'harq':
        Xh = D['X_har'][s]
        X = np.c_[Xh[:, 0], Xh[:, 0] * (D['sqrq'][s] - extra), Xh[:, 1:]]
        return b[0] + X @ b[1:]
    if kind == 'log':
        return np.exp(b[0] + D['X_loghar'][s] @ b[1:] + 0.5 * s2)
    if kind == 'sig':
        X = np.c_[D['X_loghar'][s], D['sig'][s] * extra]
        return np.exp(b[0] + X @ b[1:] + 0.5 * s2)
    raise ValueError(kind)


def first_origin(D, cfg):
    """First forecast origin: HAR needs 22 days, the signature L points, the training window W pairs."""
    return max(22, cfg['L']) + cfg['W'] + D['h']


def eval_start(D, cfg, cutoff=None):
    """First evaluation origin: after the asset's validation block + h days and, if given, strictly after the date of
    the last validation target of its asset class (cutoff), so that no evaluated origin precedes a tuning target."""
    st = first_origin(D, cfg) + cfg['VAL'] + D['h']
    if cutoff is not None:
        st = max(st, int(D['dates'].searchsorted(pd.Timestamp(cutoff), side='right')))
    return st


def tuned(res, kind, h):
    """(c for Sig-LK, c for log-HAR-K, class cutoff date) chosen on the validation block of the asset class
    (from ch20_results.json: keys 'validation' and 'val_cutoff')."""
    v = res['validation']
    return v[f'{kind}|Sig-LK|{h}']['c'], v[f'{kind}|logHAR-K|{h}']['c'], res['val_cutoff'][f'{kind}|{h}']


def run_forecasts(D, cfg, c_sig, c_har, start, stop, models=MODELS, weight_dates=()):
    """Rolling forecasts for origins start..stop-1; re-estimation every cfg['K'] days.
    For a date in weight_dates the kernel weights are recomputed at that exact origin (diagnostic; the forecast of that
    day still uses the coefficients estimated at the start of its 5-day block)."""
    rows, ks, wsave = [], [], {}
    wd = set(pd.DatetimeIndex(weight_dates))
    t = start
    while t < stop:
        blk = np.arange(t, min(t + cfg['K'], stop))
        specs, info, (lo, hi, mu) = fit_models(D, t, cfg, c_sig, c_har, models)
        for s in blk:
            if D['dates'][s] in wd:
                _, inf_s, _ = fit_models(D, s, cfg, c_sig, c_har, ['Sig-LK'], keep_weights=True)
                wsave[D['dates'][s]] = inf_s.get('weights')
        f = {m: predict(D, blk, specs[m]) for m in models}
        for m in models:                                          # positivity: QLIKE needs f > 0
            v = f[m]
            f[m] = np.where((v <= 0) | ~np.isfinite(v), mu, v)
        for i, s in enumerate(blk):
            rows.append([D['dates'][s], D['y'][s], lo, hi, mu] + [f[m][i] for m in models])
        ks.append({k: v for k, v in info.items() if k != 'weights'})
        t += cfg['K']
    fc = pd.DataFrame(rows, columns=['date', 'y', 'lo', 'hi', 'mu'] + list(models)).set_index('date')
    return fc, pd.DataFrame(ks), wsave


# -----------------------------------------------------------------------------
# EVALUATION
# -----------------------------------------------------------------------------
def qlike(y, f):
    """QLIKE(y, f) = y/f - log(y/f) - 1 (Patton, 2011): y is the realised proxy, f the forecast."""
    r = y / f
    return r - np.log(r) - 1.0


def mse(y, f):
    return (y - f) ** 2


def nw_var(d, lag):
    """Newey-West (Bartlett) long-run variance of a series."""
    d = np.asarray(d, float) - np.mean(d)
    T = len(d)
    v = d @ d / T
    for j in range(1, lag + 1):
        v += 2 * (1 - j / (lag + 1)) * (d[j:] @ d[:-j]) / T
    return v


def nw_lag(T, h):
    return int(max(h, np.ceil(T ** (1 / 3))))


def dm_test(la, lb, h):
    """Diebold-Mariano: d = L_A - L_B; t = mean(d) / sqrt(NW var / T); one-sided p for 'A beats B' (d < 0)."""
    d = np.asarray(la) - np.asarray(lb)
    T = len(d)
    t = d.mean() / np.sqrt(nw_var(d, nw_lag(T, h)) / T)
    return t, stats.norm.cdf(t), 2 * stats.norm.sf(abs(t))


def gw_test(la, lb, h):
    """Giacomini-White conditional test, instruments (1, d_{t-h}); Wald ~ chi2(2)."""
    d = np.asarray(la) - np.asarray(lb)
    Z = np.c_[np.ones(len(d) - h), d[:-h]] * d[h:, None]
    T = len(Z)
    zb = Z.mean(0)
    Zc = Z - zb
    lag = nw_lag(T, h)
    O = Zc.T @ Zc / T
    for j in range(1, lag + 1):
        G = Zc[j:].T @ Zc[:-j] / T
        O += (1 - j / (lag + 1)) * (G + G.T)
    stat = T * zb @ np.linalg.solve(O, zb)
    return stat, stats.chi2.sf(stat, 2)


def holm(p):
    p = np.asarray(p)
    o = np.argsort(p)
    m = len(p)
    adj = np.maximum.accumulate((m - np.arange(m)) * p[o])
    out = np.empty(m)
    out[o] = np.minimum(adj, 1)
    return out


def bh(p):
    p = np.asarray(p)
    o = np.argsort(p)
    m = len(p)
    adj = np.minimum.accumulate((m / np.arange(m, 0, -1)) * p[o][::-1])[::-1]
    out = np.empty(m)
    out[o] = np.minimum(adj, 1)
    return out


def mcs(losses, size=0.10, reps=1000, block=None, seed=20):
    """Model confidence set (Hansen, Lunde & Nason, 2011), T_max statistic, stationary bootstrap."""
    from arch.bootstrap import MCS
    L = pd.DataFrame(losses)
    m = MCS(L, size=size, reps=reps, block_size=block or 10, method='max', bootstrap='stationary', seed=seed)
    m.compute()
    return list(m.included), m.pvalues['Pvalue'].to_dict()

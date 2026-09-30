"""
inference_tests.py -- Capitolul 14: inferenta pentru compararea prognozelor si calibrarea distributiilor predictive
===============================================================================================================
Foloseste DOAR prognozele salvate (ch14_returns_*.csv, ch14_risk_*.csv, ch14_rv.csv); modelele fundationale NU
sunt rulate din nou. GARCH-t/FHS sunt reestimate (ieftin) doar pentru grila completa de cuantile.
  1. Randamente: Clark--West (2007) pentru modele care includ prognoza zero; DM unilateral; Holm pe cele 18 teste;
     Romano--Wolf (2005) pas cu pas si SPA (Hansen, 2005) pe fiecare piata (bootstrap stationar, blocuri de 20 de zile)
  2. BET: tranzactionarea nesincrona (Lo & MacKinlay, 1990): autocorelatii, LSTM fata de ETF-ul pe BET
  3. Puterea exacta a testului Kupiec (binomial) pentru VaR 1%
  4. Calibrare: PIT pe grila de 21 de cuantile, test Berkowitz (2001) cenzurat in afara [1%, 99%],
     scorul cuantilic mediu (aproximarea CRPS, Gneiting & Raftery, 2007) cu DM
  5. Backtesting: testul DQ (Engle & Manganelli, 2004) pentru VaR 1%
  6. Inferenta conformala adaptiva (Gibbs & Candes, 2021) pentru cuantilele Chronos-2 de 1% si 2.5%
  7. Giacomini--White (2006) conditional pentru QLIKE fata de log-HAR
  8. Memoria: ACF-ul lui |r| fata de descresterea geometrica a unei celule LSTM cu poarta de uitare constanta
Rezultat: ch14_inference.json si graficele ch14_pit, ch14_conformal.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats, optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_tsfm as M   # noqa: E402
from generate_all_charts import (plt, mdates, MainBlue, IDAred, Forest, Orange, Purple, Teal, Gray,  # noqa: E402
                                 LightGray, save_fig, fig_legend_bottom, load_csv)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}
RET = {'hist': 'Historical mean', 'ar1': 'AR(1)', 'lstm': 'LSTM', 'chronos2_point': 'Chronos-2',
       'bolt_point': 'Chronos-Bolt', 'timesfm_point': 'TimesFM-2.5'}
LV = np.array(M.C2_LEVELS)
BLOCK, B = 20, 2000


def nw_se(x):
    x = np.asarray(x, float)
    return np.sqrt(M.nw_var(x) / len(x))


def stationary_idx(T, B, block, rng):
    """Indices of the stationary bootstrap (Politis & Romano): geometric block lengths with mean `block`."""
    idx = np.empty((B, T), int)
    for b in range(B):
        t = rng.integers(T)
        for i in range(T):
            if i > 0 and rng.random() < 1 / block:
                t = rng.integers(T)
            else:
                t = (t + 1) % T if i > 0 else t
            idx[b, i] = t
    return idx


def romano_wolf(D, B=2000, block=20, seed=7):
    """Romano--Wolf stepwise adjusted p-values (studentised statistics) for H0_k: E[d_k] <= 0,
    d_k = benchmark loss - loss of model k (positive = model k better)."""
    D = np.asarray(D, float)
    T, K = D.shape
    rng = np.random.default_rng(seed)
    idx = stationary_idx(T, B, block, rng)
    dbar = D.mean(0)
    se = np.array([nw_se(D[:, k]) for k in range(K)])
    t = dbar / se
    tb = np.stack([(D[i].mean(0) - dbar) / se for i in idx])
    order = np.argsort(-t)
    padj = np.empty(K)
    run = 0.0
    for j, k in enumerate(order):
        rest = order[j:]
        p = np.mean(tb[:, rest].max(1) >= t[k])
        run = max(run, p)
        padj[k] = run
    return t, padj


def spa_consistent(D, B=2000, block=20, seed=11):
    """Hansen's (2005) SPA test, consistent version: H0: no model beats the benchmark.
    d_k = benchmark loss - loss of model k; much worse models (t_k <= -sqrt(2 log log n)) are not
    recentred at zero."""
    D = np.asarray(D, float)
    T, K = D.shape
    rng = np.random.default_rng(seed)
    idx = stationary_idx(T, B, block, rng)
    dbar = D.mean(0)
    se = np.array([nw_se(D[:, k]) for k in range(K)])
    t = dbar / se
    mu_c = np.where(t <= -np.sqrt(2 * np.log(np.log(T))), dbar, 0.0)
    stat = max(t.max(), 0.0)
    tb = np.stack([np.maximum(((D[i].mean(0) - dbar + mu_c) / se).max(), 0.0) for i in idx])
    return float(np.mean(tb >= stat))


def holm(p):
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    adj = np.empty(m)
    run = 0.0
    for i, k in enumerate(o):
        run = max(run, min(1.0, (m - i) * p[k]))
        adj[k] = run
    return adj


# =============================================================================
# 1. RETURNS: CLARK-WEST, ONE-SIDED DM, HOLM, ROMANO-WOLF, SPA
# =============================================================================
def returns_inference():
    res, allp, keys = {}, [], []
    for a in M.ASSETS:
        d = load_csv(f'ch14_returns_{a}.csv')
        y = d['y'].values
        r = {}
        Dm = []
        for k in RET:
            f = d[k].values
            l0, l1 = y ** 2, (y - f) ** 2
            dm = (l1 - l0).mean() / nw_se(l1 - l0)
            adj = l0 - (l1 - f ** 2)               # Clark--West: adjusted MSPE, benchmark = zero forecast
            cw = adj.mean() / nw_se(adj)
            # with the zero benchmark adj = 2 y f: Clark--West tests the martingale-difference null E[y_t f_t] = 0,
            # valid for any forecast built from past data (Clark & West, 2006), including fixed pretrained models
            r[k] = dict(dm=float(dm), p_dm1=float(stats.norm.cdf(dm)), cw=float(cw), p_cw=float(stats.norm.sf(cw)))
            Dm.append(l0 - l1)
            allp.append(r[k]['p_dm1'])
            keys.append((a, k))
        Dm = np.column_stack(Dm)
        # mean forecasts from the quantile grids (trapezoid, tails held constant) instead of the medians
        r['r2_gridmean'] = {fm: float(100 * M.r2_oos(y, M.grid_mean(lv, d[[f'{fm}_q{u:.2f}' for u in lv]].values)))
                            for fm, lv in (('chronos2', M.C2_LEVELS), ('timesfm', M.DEC_LEVELS))}
        t, padj = romano_wolf(Dm)
        for j, k in enumerate(RET):
            r[k]['rw'] = float(padj[j])
        r['spa'] = spa_consistent(Dm)
        # AR(1) on the BET: mean slope and the yearly contribution to the squared-error gain
        if a == 'bet':
            x = M.load_returns('bet')
            pos = x.index.get_indexer(d.index)
            xv = x.values
            b1 = [np.linalg.lstsq(np.column_stack([np.ones(M.W - 1), xv[t - M.W:t - 1]]), xv[t - M.W + 1:t],
                                  rcond=None)[0][1] for t in pos]
            gy = pd.Series(y ** 2 - (y - d['ar1'].values) ** 2, index=d.index).groupby(d.index.year).sum()
            r['ar1_extra'] = dict(b1_mean=float(np.mean(b1)), b1_min=float(np.min(b1)), b1_max=float(np.max(b1)),
                                  sd_f=float(d['ar1'].std()), corr=float(np.corrcoef(y, d['ar1'])[0, 1]),
                                  gain_2020=float(gy.loc[2020]), gain_2026=float(gy.loc[2026]),
                                  gain_min_year=int(gy.idxmin()), gain_max_year=int(gy.idxmax()),
                                  r2_ex2020_2026=float(100 * M.r2_oos(y[~d.index.year.isin([2020, 2026])],
                                                                      d['ar1'].values[~d.index.year.isin([2020, 2026])])))
        res[a] = r
    h = holm(allp)
    for (a, k), v in zip(keys, h):
        res[a][k]['holm'] = float(v)
    res['n_tests'] = len(allp)
    res['bonf'] = 0.05 / len(allp)
    OUT['ret'] = res


# =============================================================================
# 2. BET: NON-SYNCHRONOUS TRADING
# =============================================================================
def nonsync():
    d = load_csv('ch14_returns_bet.csv')
    bet = M.read_market('BET')['close']
    etf = M.read_market('TVBETETF.RO')['adjusted_close']
    spx = M.load_returns('sp500')
    px = pd.concat([bet.rename('bet'), etf.rename('etf')], axis=1, join='inner').dropna()
    px = px[(px > 0).all(1)]
    rr = 100 * np.log(px).diff().dropna()
    rr = rr.loc[d.index[0]:]

    def ac1(v):
        v = np.asarray(v) - np.mean(v)
        return float(np.sum(v[1:] * v[:-1]) / np.sum(v * v))
    betr = d['y']
    f = d['lstm']
    j = pd.concat([rr, f.rename('f')], axis=1, join='inner').dropna()
    # one-day execution lag: the signal formed at the close of t-1 is applied to the return of day t+1
    j['etf_next'] = j['etf'].shift(-1)
    j2 = j.dropna()
    etf_nz = (j['etf'] != 0).mean()

    def r2(y, ff):
        return float(100 * M.r2_oos(np.asarray(y), np.asarray(ff)))

    def cwp(y, ff):
        y, ff = np.asarray(y), np.asarray(ff)
        adj = y ** 2 - ((y - ff) ** 2 - ff ** 2)
        c = adj.mean() / nw_se(adj)
        return float(c), float(stats.norm.sf(c))
    OUT['nonsync'] = dict(
        ac1_bet=ac1(betr), ac1_sp=ac1(spx.loc[d.index[0]:]), ac1_etf=ac1(j['etf']), ac1_bet_common=ac1(j['bet']),
        corr_f_lag=float(np.corrcoef(f.values[1:], betr.values[:-1])[0, 1]),
        n=int(len(j)), start=str(j.index[0].date()), zero_etf=float(100 * (1 - etf_nz)),
        r2_bet=r2(j['bet'], j['f']), r2_etf=r2(j['etf'], j['f']), r2_etf_next=r2(j2['etf_next'], j2['f']),
        cw_bet=cwp(j['bet'], j['f']), cw_etf=cwp(j['etf'], j['f']), cw_etf_next=cwp(j2['etf_next'], j2['f']))


# =============================================================================
# 3. POWER OF THE KUPIEC TEST
# =============================================================================
def kupiec_power():
    crit = stats.chi2.ppf(0.95, 1)
    p0 = 0.01

    def rej(T):
        x = np.arange(T + 1)
        ph = x / T
        with np.errstate(divide='ignore', invalid='ignore'):
            ll1 = np.where((x > 0) & (x < T), (T - x) * np.log(1 - ph) + x * np.log(np.where(ph > 0, ph, 1)), 0.0)
        ll0 = (T - x) * np.log(1 - p0) + x * np.log(p0)
        return -2 * (ll0 - ll1) > crit

    def power(T, p):
        return float(stats.binom.pmf(np.arange(T + 1), T, p)[rej(T)].sum())
    res = {'p1': 0.0167}
    for T in (220, 1000, 2693):
        res[f'pow_{T}'] = power(T, 0.0167)
        res[f'size_{T}'] = power(T, p0)
        res[f'exp_{T}'] = 0.01 * T
    Ts = np.arange(200, 6001, 1)
    pw = np.array([power(T, 0.0167) for T in Ts])
    res['T80'] = int(Ts[np.argmax(pw >= 0.8)])
    res['T80_stable'] = int(Ts[np.where(pw < 0.8)[0].max() + 1])
    res['pow2_220'] = power(220, 0.02)
    res['T80_p2'] = int(Ts[np.argmax(np.array([power(T, 0.02) for T in Ts]) >= 0.8)])
    OUT['power'] = res


# =============================================================================
# 4. CALIBRATION: PIT, CENSORED BERKOWITZ, QUANTILE SCORE
# =============================================================================
def garch_grid(a, dates):
    """GARCH-t and FHS on the same origins as in ch14_risk_*: PIT and the 21-quantile grid."""
    r = M.load_returns(a)
    x = r.values
    org = r.index.get_indexer(dates)
    gf, Z = M.garch_t(x, org)
    y = x[org]
    mu, s, nu = gf.mu.values, gf.sigma.values, gf.nu.values
    z = (y - mu) / s
    u_t = stats.t.cdf(z / np.sqrt((nu - 2) / nu), nu)
    q_t = mu[:, None] + s[:, None] * np.column_stack([M.t_std_q(nu, u) for u in LV])
    u_f = np.array([np.mean(Zi <= zi) for Zi, zi in zip(Z, z)])
    q_f = mu[:, None] + s[:, None] * np.stack([np.quantile(Zi, LV) for Zi in Z])
    return y, (u_t, q_t), (u_f, q_f)


def pit_grid(y, Q):
    """PIT by linear interpolation between the grid quantiles; NaN outside [q_1%, q_99%] (censored)."""
    u = np.full(len(y), np.nan)
    lo = y < Q[:, 0]
    hi = y > Q[:, -1]
    for i in np.where(~lo & ~hi)[0]:
        qi = np.maximum.accumulate(Q[i])
        u[i] = np.interp(y[i], qi, LV)
    return u, lo, hi


def berkowitz_cens(u, lo, hi):
    """LR for mu = 0, sigma = 1 in z = Phi^{-1}(u), censored below 1% and above 99% (Berkowitz, 2001)."""
    cL, cH = stats.norm.ppf(0.01), stats.norm.ppf(0.99)
    z = stats.norm.ppf(np.clip(u[np.isfinite(u)], 1e-9, 1 - 1e-9))
    nL, nH = int(lo.sum()), int(hi.sum())

    def ll(p):
        m, s = p[0], np.exp(p[1])
        return (np.sum(stats.norm.logpdf(z, m, s)) + nL * stats.norm.logcdf((cL - m) / s)
                + nH * stats.norm.logsf((cH - m) / s))
    o = optimize.minimize(lambda p: -ll(p), [0.0, 0.0], method='Nelder-Mead')
    lr = 2 * (-o.fun - ll([0.0, 0.0]))
    return dict(mu=float(o.x[0]), sigma=float(np.exp(o.x[1])), LR=float(lr), p=float(stats.chi2.sf(lr, 2)),
                tail_lo=float(100 * lo.mean()), tail_hi=float(100 * hi.mean()))


def qscore(y, Q, idx=None):
    """Equally weighted quantile score on the grid, (2/K) sum_k pinball_k (a grid analogue of the CRPS)."""
    idx = np.arange(len(LV)) if idx is None else np.asarray(idx)
    s = np.zeros(len(y))
    for k in idx:
        s += 2 * (((y < Q[:, k]).astype(float) - LV[k]) * (Q[:, k] - y))
    return s / len(idx)


def bins_of(u, lo, hi):
    edges = np.r_[0, LV, 1]
    c = np.zeros(len(edges) - 1)
    c[0] += lo.sum()
    c[-1] += hi.sum()
    uu = u[np.isfinite(u)]
    k = np.clip(np.searchsorted(LV, uu, side='right'), 0, len(LV))
    for kk in k:
        c[kk] += 1
    return c, np.diff(edges)


def calibration():
    res, pits = {}, {}
    centre = [k for k, u in enumerate(LV) if 0.1 - 1e-9 <= u <= 0.9 + 1e-9]
    tails = [k for k, u in enumerate(LV) if u < 0.1 - 1e-9 or u > 0.9 + 1e-9]
    for a in M.ASSETS:
        d = load_csv(f'ch14_returns_{a}.csv')
        rk = load_csv(f'ch14_risk_{a}.csv')
        dates = rk.index
        d = d.loc[dates]
        Qc = d[[f'chronos2_q{u:.2f}' for u in LV]].values
        y, (_, Qt), (_, Qf) = garch_grid(a, dates)
        assert np.allclose(y, d['y'].values)
        # check: the FHS VaR 1% of the recomputed grid equals the one in ch14_risk_*.csv
        assert np.allclose(-Qf[:, 0], rk['FHS|VaR1'].values, atol=1e-6)
        r = {}
        # one convention for all models: PIT by linear interpolation on the 21-level grid, censored outside
        # [q_1%, q_99%]; a return below q_1% is exactly a VaR 1% breach
        for nm, Q in (('C2', Qc), ('GARCH-t', Qt), ('FHS', Qf)):
            u, lo, hi = pit_grid(y, Q)
            c, w = bins_of(u, lo, hi)
            chi = float(np.sum((c - len(y) * w) ** 2 / (len(y) * w)))
            bk = berkowitz_cens(u, lo, hi)
            qs, qc, qt = qscore(y, Q), qscore(y, Q, centre), qscore(y, Q, tails)
            r[nm] = dict(berk=bk, chi2=chi, p_chi2=float(stats.chi2.sf(chi, len(c) - 1)), qs=float(qs.mean()),
                         qs_c=float(qc.mean()), qs_t=float(qt.mean()),
                         dens=(c / (len(y) * w)).tolist(), _qs=qs, _qc=qc, _qt=qt)
        for nm in ('GARCH-t', 'FHS'):
            for s, key in (('_qs', 'dm'), ('_qc', 'dm_c'), ('_qt', 'dm_t')):
                dd = r['C2'][s] - r[nm][s]
                t = dd.mean() / nw_se(dd)
                r['C2'][f'{key}_{nm}'] = float(t)
                r['C2'][f'p{key}_{nm}'] = float(2 * stats.norm.sf(abs(t)))
        for nm in r:
            for s in ('_qs', '_qc', '_qt'):
                r[nm].pop(s)
        res[a] = r
        pits[a] = {nm: r[nm]['dens'] for nm in r}
        res[a]['n'] = int(len(y))
    OUT['calib'] = res
    # chart: relative PIT density on the grid intervals (1 = perfect calibration)
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.5), sharey=True)
    edges = np.r_[0, LV, 1]
    hs = []
    for ax, a in zip(axs, M.ASSETS):
        for nm, col in (('C2', IDAred), ('FHS', Forest), ('GARCH-t', MainBlue)):
            v = np.r_[pits[a][nm], pits[a][nm][-1]]
            h, = ax.step(edges, v, where='post', color=col, lw=1.2)
            if a == 'sp500':
                hs.append(h)
        ax.axhline(1, color=Gray, lw=0.7, ls='--')
        ax.set_title(M.LABELS[a], color='black')
        ax.set_xlabel('PIT $u_t = \\hat F_t(r_t)$')
        ax.set_ylim(0, 2.0)
    axs[0].set_ylabel('Observed / expected frequency')
    fig_legend_bottom(fig, hs, ['Chronos-2 quantiles (zero-shot)', 'FHS (GARCH-t filter)', 'GARCH-t'], ncol=3,
                      y=0.04)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch14_pit')


# =============================================================================
# 5. THE DQ TEST (ENGLE & MANGANELLI, 2004)
# =============================================================================
def dq_test(L, var, a=0.01, lags=4):
    hit = (L > var).astype(float) - a
    T = len(hit)
    X = np.column_stack([np.ones(T - lags)] + [hit[lags - j - 1:T - j - 1] for j in range(lags)] + [var[lags:]])
    yv = hit[lags:]
    b = np.linalg.lstsq(X, yv, rcond=None)[0]
    stat = float(b @ X.T @ X @ b / (a * (1 - a)))
    return stat, float(stats.chi2.sf(stat, X.shape[1]))


def backtests():
    res = {}
    for a in M.ASSETS:
        d = load_csv(f'ch14_risk_{a}.csv')
        L = -d['y'].values
        res[a] = {}
        for m in ('HS', 'GARCH-t', 'FHS', 'C2-raw', 'C2-FHS', 'TFM-FHS'):
            s, p = dq_test(L, d[f'{m}|VaR1'].values)
            res[a][m] = dict(dq=s, p_dq=p)
    OUT['dq'] = res


# =============================================================================
# 6. ADAPTIVE CONFORMAL INFERENCE (GIBBS & CANDES, 2021)
# =============================================================================
def aci(y, q, alpha, gamma=0.001, n_cal=250):
    """Adaptive conformal inference (Gibbs & Candes, 2021) for a lower quantile q_t of level alpha.
    Scores E_i = q_i - y_i on the last n_cal days; corrected quantile q_t - Qhat_t, where Qhat_t is the
    ceil((1 - alpha_t)(n_cal + 1))-th smallest score. Published boundary rule: if alpha_t <= 0 or that rank exceeds
    n_cal, Qhat_t = +inf (the interval is the whole real line: VaR = +inf, no breach possible); if alpha_t >= 1,
    Qhat_t = -inf. Update alpha_{t+1} = alpha_t + gamma (alpha - err_t); gamma = 0: split conformal."""
    T = len(y)
    E = q - y
    at = alpha
    shift = np.full(T, np.nan)
    err = np.zeros(T)
    alphas = np.full(T, np.nan)
    for t in range(n_cal, T):
        cal = np.sort(E[t - n_cal:t])
        k = int(np.ceil((1 - at) * (n_cal + 1)))
        if at <= 0 or k > n_cal:
            Qh = np.inf
        elif at >= 1 or k < 1:
            Qh = -np.inf
        else:
            Qh = cal[k - 1]
        shift[t] = Qh
        alphas[t] = at
        err[t] = float(y[t] < q[t] - Qh)
        at = at + gamma * (alpha - err[t])
    return shift, alphas


def conformal():
    res = {}
    for a in M.ASSETS:
        rk = load_csv(f'ch14_risk_{a}.csv')
        d = load_csv(f'ch14_returns_{a}.csv').loc[rk.index]
        y = rk['y'].values
        L = -y
        Qc = d[[f'chronos2_q{u:.2f}' for u in LV]].values
        q1 = Qc[:, 0]
        q25 = M.quantile_at(M.C2_LEVELS, Qc, 0.025)
        out = {}
        # with gamma = 0.005 (the step of Gibbs & Candes' 10% experiments) the level alpha_t falls below the smallest
        # attainable rank and the published rule returns VaR = +inf: count those days
        s_big, _ = aci(y, q1, 0.01, 0.005)
        n_inf_005 = int(np.isinf(s_big[250:]).sum())
        for nm, g in (('C2-ACI', 0.001), ('C2-SCP', 0.0)):
            s1, al1 = aci(y, q1, 0.01, g)
            s25, _ = aci(y, q25, 0.025, g)
            assert np.isfinite(s1[250:]).all() and np.isfinite(s25[250:]).all(), (a, nm)
            v1 = -(q1 - s1)
            v25 = -(q25 - s25)
            es = np.maximum(rk['C2-raw|ES2.5'].values + s25, v25)
            out[nm] = (v1, v25, es)
            if nm == 'C2-ACI' and a == 'sp500':
                aci_path = pd.DataFrame({'alpha_t': al1, 'VaR_aci': v1, 'VaR_raw': -q1, 'FHS': rk['FHS|VaR1'].values,
                                         'loss': L}, index=rk.index)
        keep = np.arange(250, len(y))
        r = {'n': int(len(keep)), 'start': str(rk.index[keep[0]].date()), 'inf_005': n_inf_005,
             'bound': float((0.99 + 0.001) / (0.001 * len(keep)))}
        Fz = {}
        models = ['FHS', 'GARCH-t', 'C2-raw', 'C2-FHS', 'C2-SCP', 'C2-ACI']
        for m in models:
            if m in out:
                v1, v25, es = (x[keep] for x in out[m])
            else:
                v1, v25, es = (rk[f'{m}|{c}'].values[keep] for c in ('VaR1', 'VaR2.5', 'ES2.5'))
            Lk = L[keep]
            h = (Lk > v1).astype(int)
            k = M.kupiec(h, 0.01)
            c = M.christoffersen(h, 0.01)
            dq, pdq = dq_test(Lk, v1)
            Fz[m] = M.fz0(Lk, v25, np.maximum(es, 1e-6))
            r[m] = dict(x=k['x'], rate=100 * k['rate'], p_uc=k['p'], p_ind=c['p_ind'], p_cc=c['p_cc'], p_dq=pdq,
                        fz0=float(Fz[m].mean()), var=float(v1.mean()), exp=0.01 * len(keep))
        for m in models:
            if m != 'FHS':
                dm = M.diebold_mariano(Fz[m], Fz['FHS'])
                r[m]['dm'] = dm['DM']
                r[m]['pdm'] = dm['p']
        res[a] = r
        if a == 'sp500':
            path = aci_path
    OUT['conf'] = res
    # chart: adaptive level alpha_t and VaR 1% (S&P 500)
    p = path.iloc[250:]
    fig, axs = plt.subplots(2, 1, figsize=(7.0, 3.6), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.4]))
    h1, = axs[0].plot(p.index, 100 * p['alpha_t'], color=Purple, lw=0.9)
    axs[0].axhline(1, color=Gray, lw=0.7, ls='--')
    axs[0].set_ylabel('$\\alpha_t$ (%)')
    h2, = axs[1].plot(p.index, p['VaR_raw'], color=IDAred, lw=0.7)
    h3, = axs[1].plot(p.index, p['VaR_aci'], color=Orange, lw=0.7)
    h4, = axs[1].plot(p.index, p['FHS'], color=Forest, lw=0.7)
    axs[1].set_yscale('log')
    axs[1].set_ylabel('VaR 1% (%)')
    axs[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig_legend_bottom(fig, [h1, h2, h3, h4], ['Adaptive level $\\alpha_t$ (target 1%)', 'Chronos-2 direct quantile',
                                              'Chronos-2 + adaptive conformal', 'FHS'], ncol=2, y=0.06)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch14_conformal')


# =============================================================================
# 7. GIACOMINI-WHITE CONDITIONAL
# =============================================================================
def gw():
    d = load_csv('ch14_rv.csv')
    base = np.asarray(M.qlike(d['RV'], d['logHAR']))
    res = {}
    for m in ('RW', 'HAR', 'GARCH-t', 'LSTM', 'Chronos-2', 'Chronos-Bolt', 'TimesFM-2.5'):
        dd = np.asarray(M.qlike(d['RV'], d[m])) - base
        Z = np.column_stack([np.ones(len(dd) - 1), dd[:-1]]) * dd[1:, None]
        T = len(Z)
        zb = Z.mean(0)
        Om = (Z - zb).T @ (Z - zb) / T
        st = float(T * zb @ np.linalg.solve(Om, zb))
        res[m] = dict(gw=st, p=float(stats.chi2.sf(st, 2)))
    OUT['gw'] = res


# =============================================================================
# 8. MEMORY: ACF OF |r| VS GEOMETRIC DECAY
# =============================================================================
def memory():
    x = M.load_returns('sp500').loc['2000':].values
    v = np.abs(x) - np.abs(x).mean()
    acf = {L: float(np.sum(v[L:] * v[:-L]) / np.sum(v * v)) for L in (1, 50, 150)}
    f = (acf[50] / acf[1]) ** (1 / 49)
    OUT['mem'] = dict(acf1=acf[1], acf50=acf[50], acf150=acf[150], f=float(f), bf=float(np.log(f / (1 - f))),
                      half=float(np.log(0.5) / np.log(f)), pred150=float(acf[1] * f ** 149),
                      band=float(1.96 / np.sqrt(len(x))))


if __name__ == '__main__':
    memory()
    kupiec_power()
    gw()
    backtests()
    nonsync()
    returns_inference()
    calibration()
    conformal()
    with open(os.path.join(HERE, 'ch14_inference.json'), 'w') as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print(json.dumps({k: OUT[k] for k in ('mem', 'power', 'gw', 'nonsync')}, indent=1, default=float))

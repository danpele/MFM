"""
inference16.py -- Inference for Chapter 16 (MFM): digital assets and DeFi
=========================================================================
  * Hill tail index: asymptotic standard error k^(-1/2) alpha, 95% CI, block bootstrap,
    sensitivity to k (Drees, de Haan & Resnick, 2000);
  * the CRIX/ECRIX rule of Trimborn & Hardle (2018), Sections 3-5: base index with k1 = 1 constituent,
    s additional constituents with weights beta estimated by (11), likelihood from the Epanechnikov kernel density
    of the base-index residuals (Sheather-Jones plug-in bandwidth), AIC = -2 log L + 2 s,
    quarterly review on the last three months, stop at the first rise of the AIC (ECRIX, rule 26) and global minimum
    (EFCRIX, rule 27);
  * break in the Bitcoin -- S&P 500 correlation: sup-Wald (Andrews, 1993) with HAC errors for a break in the intercept
    and the slope, simulated asymptotic critical values, break date and Bai (1997) CI; the adjusted correlation of
    Forbes & Rigobon (2002);
  * stablecoin pegs: equilibrium threshold AR with a band (EQ-TAR, Balke & Fomby, 1997), heteroskedasticity-robust
    sup-Wald test with a fixed-regressor bootstrap (Hansen, 1996);
  * LVR: block-bootstrap interval for the realised rate and the identity with realised variance / 8;
  * asset-class map: block bootstrap for the change in the distances between class centroids;
  * crypto asset pricing: the GRS test (Gibbons, Ross & Shanken, 1989) with a wild-bootstrap p-value and
    Fama-MacBeth with Shanken (1992) errors, on eight coins and the crypto market factor of the total index;
  * Dimson (1979) beta for IBIT and ETHA.
Data: course market data; circulating supply: Coin Metrics Community Data; risk-free rate: FRED (DTB4WK).
Output: ch16_inference.json and the chart ch16_crix_rule.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import least_squares, brentq
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import (ASSETS, CRIX_UNIVERSE, STABLE, CLASS_ASSETS, END, price, joint_prices, joint_returns,  # noqa: E402
                      market_values, read_market, symbol_returns, periods_per_year)
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray,  # noqa: E402
                                 save_fig, fig_legend_bottom, jsonable, hill, crix_index, asset_features,
                                 STYL, WINDOWS, FEATURES, ETF_START, SEED)

TRIM = 0.15                       # fraction trimmed at each end (Andrews, 1993; Hansen, 1996)


# =============================================================================
# 1. HILL TAIL INDEX: INFERENCE
# =============================================================================
def hill_k(x, k):
    """Hill estimator from the k largest positive values of x."""
    x = np.sort(x[x > 0])[::-1]
    return 1 / np.mean(np.log(x[:k] / x[k]))


def hill_inference(start='2018-01-01', B=1000, block=20):
    """alpha_H from the largest 5% of losses, asymptotic standard error alpha/sqrt(k) (i.i.d. data),
    95% CI, moving-block bootstrap CI (dependence), and alpha for k = 2.5% and 10%."""
    rng = np.random.default_rng(SEED)
    out = {}
    for key in STYL:
        r = 100 * np.log(price(key, start)).diff().dropna().values
        L = -r
        nl = int((L > 0).sum())
        k = max(int(0.05 * nl), 10)
        a = hill(L)
        se = a / np.sqrt(k)
        n = len(r)
        nb = int(np.ceil(n / block))
        bs = []
        for _ in range(B):
            st = rng.integers(0, n - block + 1, nb)
            y = r[(st[:, None] + np.arange(block)[None, :]).ravel()[:n]]
            bs.append(hill(-y))
        out[key] = dict(alpha=a, k=k, n_loss=nl, se=se, lo=a - 1.96 * se, hi=a + 1.96 * se,
                        b_lo=float(np.percentile(bs, 2.5)), b_hi=float(np.percentile(bs, 97.5)), b_se=float(np.std(bs)),
                        a25=hill_k(L, max(int(0.025 * nl), 10)), a10=hill_k(L, int(0.10 * nl)))
    for a, b in [('BTC', 'SPX'), ('BTC', 'GOLD'), ('DOGE', 'SPX')]:
        d = out[a]['alpha'] - out[b]['alpha']
        out[f'z_{a}_{b}'] = d / np.sqrt(out[a]['se'] ** 2 + out[b]['se'] ** 2)
    out['alpha_min'] = min(out[k]['alpha'] for k in STYL)
    out['alpha_max'] = max(out[k]['alpha'] for k in STYL)
    out['hi_max'] = max(out[k]['hi'] for k in STYL)
    return out


# =============================================================================
# 2. THE CRIX RULE (Trimborn & Hardle, 2018): ECRIX and EFCRIX, quarterly review
# =============================================================================
def sj_bandwidth(x):
    """Sheather-Jones plug-in bandwidth ('solve-the-equation') for the Gaussian kernel (as bw.SJ in R),
    converted to the Epanechnikov kernel with variance 1 (factor (R(K_E)/R(K_G))^(1/5))."""
    x = np.asarray(x, float)
    n = len(x)
    d = (x[:, None] - x[None, :]).ravel()
    phi = lambda u: np.exp(-u ** 2 / 2) / np.sqrt(2 * np.pi)
    psi4 = lambda h: np.sum(((d / h) ** 4 - 6 * (d / h) ** 2 + 3) * phi(d / h)) / (n * (n - 1) * h ** 5)
    psi6 = lambda h: np.sum(((d / h) ** 6 - 15 * (d / h) ** 4 + 45 * (d / h) ** 2 - 15) * phi(d / h)) / (n * (n - 1) * h ** 7)
    scale = min(np.std(x, ddof=1), stats.iqr(x) / 1.349)
    a = 1.24 * scale * n ** (-1 / 7)
    b = 1.23 * scale * n ** (-1 / 9)
    c1 = 1 / (2 * np.sqrt(np.pi) * n)
    td = -psi6(b)
    alph2 = 1.357 * (psi4(a) / td) ** (1 / 7)
    f = lambda h: (c1 / psi4(alph2 * h ** (5 / 7))) ** 0.2 - h
    lo, hi = 0.1 * scale * n ** (-0.2), 3 * scale * n ** (-0.2)
    try:
        hg = brentq(f, lo, hi)
    except ValueError:
        hg = 1.06 * scale * n ** (-0.2)
    return hg * ((3 / (5 * np.sqrt(5))) / (1 / (2 * np.sqrt(np.pi)))) ** 0.2


def epa_loglik(base, x):
    """Log-likelihood of the values x under the Epanechnikov kernel density (support +-sqrt(5)) of the base residuals."""
    h = sj_bandwidth(base)
    u = (x[:, None] - base[None, :]) / h
    k = 3 / (4 * np.sqrt(5)) * (1 - u ** 2 / 5) * (np.abs(u) <= np.sqrt(5))
    f = k.mean(axis=1) / h
    return float(np.sum(np.log(np.maximum(f, 1e-300)))), h


def crix_window(mv, px, days):
    """For the days of a quarterly window: log returns of the total index (all coins, weight 1)
    and, for each day, the quantities Q = market value / price at the end of the previous month, ordered by
    market value (the top-down approach, eq. 23)."""
    rows = []
    for t in days:
        prevm = mv.loc[:t.to_period('M').start_time - pd.Timedelta(days=1)]
        if prevm.empty:
            return None
        base = prevm.iloc[-1]
        order = base.sort_values(ascending=False).index.tolist()
        q = (base * 1e9 / px.loc[prevm.index[-1]])[order]
        i = px.index.get_loc(t)
        rows.append((order, q.values, px.iloc[i][order].values, px.iloc[i - 1][order].values))
    return rows


def crix_residuals(rows, k, beta):
    """eps_hat(k, beta) = total-index return - CRIX(k, beta) return, eqs. (11) and (22): the first
    constituent with weight 1, the next k - 1 with weights beta."""
    e = []
    for order, q, p1, p0 in rows:
        tot = np.log((p1 * q).sum() / (p0 * q).sum())
        w = np.concatenate([[1.0], beta, np.zeros(len(q) - k)])
        a1, a0 = (w * p1 * q).sum(), (w * p0 * q).sum()
        e.append(tot - np.log(a1 / a0) if a1 > 0 and a0 > 0 else 1.0)
    return np.array(e)


def crix_rule(kmax=4):
    """Number of constituents chosen each quarter (window: last three months) by ECRIX (stop at the first rise
    of the AIC) and EFCRIX (global minimum), with k1 = 1 and step s = 1 (Trimborn & Hardle, 2018, Sections 3-5)."""
    mv = market_values()
    px = pd.concat([price(a) for a in CRIX_UNIVERSE], axis=1).reindex(mv.index)
    qends = pd.date_range('2018-06-30', END, freq='QE')
    res = []
    for qe in qends:
        days = mv.loc[qe.to_period('Q').start_time:qe].index      # the calendar quarter ending at qe
        rows = crix_window(mv, px, days)
        if rows is None or len(rows) < 60:
            continue
        base = crix_residuals(rows, 1, np.array([]))
        ll0, h = epa_loglik(base, base)
        aic = {1: -2 * ll0}
        for k in range(2, kmax + 1):
            fit = least_squares(lambda b: crix_residuals(rows, k, b), np.ones(k - 1))
            ll, _ = epa_loglik(base, crix_residuals(rows, k, fit.x))
            aic[k] = -2 * ll + 2 * (k - 1)
        ek = kmax
        for k in range(2, kmax + 1):
            if aic[k] > aic[k - 1]:
                ek = k - 1
                break
        res.append(dict(q=str(qe.date()), n=len(rows), h=h, aic=aic, ecrix=ek, efcrix=min(aic, key=aic.get)))
    ec = pd.Series([r['ecrix'] for r in res])
    ef = pd.Series([r['efcrix'] for r in res])
    return dict(quarters=res, n_q=len(res), first=res[0]['q'], last=res[-1]['q'],
                ecrix_counts={str(k): int((ec == k).sum()) for k in range(1, kmax + 1)},
                efcrix_counts={str(k): int((ef == k).sum()) for k in range(1, kmax + 1)},
                ecrix_mode=int(ec.mode().iloc[0]), efcrix_mode=int(ef.mode().iloc[0]),
                ecrix_last=int(ec.iloc[-1]), efcrix_last=int(ef.iloc[-1]))


def fig_crix_rule(cr, te):
    """Left: tracking error of the index with the first k constituents; right: number of quarters in which
    the ECRIX and EFCRIX rules choose k constituents."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    ks = [1, 2, 3, 4]
    axes[0].plot(ks, [te[str(k)] for k in ks], 'o-', color=MainBlue, label='Tracking error vs the 5-asset index (% p.a.)')
    axes[0].set_xlabel('Number of constituents k')
    axes[0].set_ylabel('% per year')
    axes[0].set_xticks(ks)
    x = np.arange(len(ks))
    axes[1].bar(x - 0.2, [cr['ecrix_counts'][str(k)] for k in ks], 0.38, color=Orange,
                label='ECRIX rule: stop at the first rise of the AIC')
    axes[1].bar(x + 0.2, [cr['efcrix_counts'][str(k)] for k in ks], 0.38, color=Purple,
                label='EFCRIX rule: global minimum of the AIC')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([str(k) for k in ks])
    axes[1].set_xlabel('Number of constituents chosen')
    axes[1].set_ylabel('Quarters')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_crix_rule')


# =============================================================================
# 3. STRUCTURAL BREAKS: sup-Wald (Andrews, 1993), CI for the break date (Bai, 1997)
# =============================================================================
def nw_lags(T):
    """Number of Newey-West lags: floor(4 (T/100)^(2/9))."""
    return int(np.floor(4 * (T / 100) ** (2 / 9)))


def hac_meat(Z, u, L):
    """Long-run variance matrix of z_t u_t, Bartlett kernel with L lags."""
    g = Z * u[:, None]
    S = g.T @ g
    for l in range(1, L + 1):
        G = g[l:].T @ g[:-l]
        S += (1 - l / (L + 1)) * (G + G.T)
    return S


def sup_wald_crit(p, trim=TRIM, reps=20000, grid=1000, seed=SEED):
    """Asymptotic null distribution of sup-Wald (Andrews, 1993): sup ||B(r) - r B(1)||^2 / (r (1 - r)),
    B a p-dimensional Brownian motion, r in [trim, 1 - trim]; simulation."""
    rng = np.random.default_rng(seed)
    r = np.arange(1, grid + 1) / grid
    sel = (r >= trim) & (r <= 1 - trim)
    out = np.empty(reps)
    for i in range(reps):
        W = np.cumsum(rng.standard_normal((grid, p)), axis=0) / np.sqrt(grid)
        BB = W - r[:, None] * W[-1]
        out[i] = np.max((BB[sel] ** 2).sum(axis=1) / (r[sel] * (1 - r[sel])))
    return out


def sup_wald(y, X, index, trim=TRIM, lags=None):
    """sup-Wald test for a break in all coefficients of y = X b + u at an unknown date, with a HAC (Bartlett)
    covariance matrix computed separately in each regime; estimated date = minimum SSR (Bai, 1997)."""
    y, X = np.asarray(y, float), np.asarray(X, float)
    T, p = X.shape
    L = nw_lags(T) if lags is None else lags
    lo, hi = int(np.floor(trim * T)), int(np.ceil((1 - trim) * T))
    W, SSR = np.full(T, np.nan), np.full(T, np.nan)
    for tb in range(lo, hi):
        res = []
        V = np.zeros((p, p))
        ssr = 0.0
        for a, b in [(0, tb), (tb, T)]:
            Xa, ya = X[a:b], y[a:b]
            XtX = Xa.T @ Xa
            bet = np.linalg.solve(XtX, Xa.T @ ya)
            u = ya - Xa @ bet
            ssr += u @ u
            Q = np.linalg.inv(XtX)
            V += Q @ hac_meat(Xa, u, L) @ Q
            res.append(bet)
        d = res[1] - res[0]
        W[tb] = d @ np.linalg.solve(V, d)
        SSR[tb] = ssr
    tb_w = int(np.nanargmax(W))
    tb_hat = int(np.nanargmin(SSR))
    # Bai (1997) CI: (d'Q d)^2 / (d'Omega d) (T_hat - T0) -> argmax(W(s) - |s|/2); 97.5% quantile = 11
    b0 = np.linalg.lstsq(X[:tb_hat], y[:tb_hat], rcond=None)[0]
    b1 = np.linalg.lstsq(X[tb_hat:], y[tb_hat:], rcond=None)[0]
    d = b1 - b0
    u = y - np.where(np.arange(T)[:, None] < tb_hat, X @ b0[:, None], X @ b1[:, None]).ravel()
    Qm = X.T @ X / T
    Om = hac_meat(X, u, L) / T
    Lm = (d @ Qm @ d) ** 2 / (d @ Om @ d)
    half = int(np.ceil(11 / Lm)) + 1
    idx = pd.DatetimeIndex(index)
    return dict(sup_w=float(np.nanmax(W)), date_w=str(idx[tb_w].date()), date=str(idx[tb_hat].date()),
                ci_lo=str(idx[max(tb_hat - half, 0)].date()), ci_hi=str(idx[min(tb_hat + half, T - 1)].date()),
                half=half, b_pre=b0.tolist(), b_post=b1.tolist(), T=T, lags=L, W=W)


def break_btc_spx(start='2016-01-01'):
    """Break in the regression r_BTC = a + b r_SPX + u (common days, daily log returns); correlations before /
    after the estimated date; Forbes-Rigobon adjusted correlation relative to 2017-2019."""
    r = 100 * joint_returns(['BTC', 'SPX'], start)
    X = np.column_stack([np.ones(len(r)), r['SPX'].values])
    sw = sup_wald(r['BTC'].values, X, r.index)
    crit = sup_wald_crit(2)
    sw['p'] = float((crit >= sw['sup_w']).mean())
    sw['cv5'] = float(np.percentile(crit, 95))
    sw['cv1'] = float(np.percentile(crit, 99))
    W = pd.Series(sw.pop('W'), index=r.index)
    sw['W_etf'] = float(W.loc[ETF_START:].iloc[0])
    sw['W_date'] = float(W.loc[sw['date']])
    sw['start'] = str(r.index[0].date())
    pre, post = r.loc[:sw['date']].iloc[:-1], r.loc[sw['date']:]
    sw['rho_pre'], sw['rho_post'] = pre['BTC'].corr(pre['SPX']), post['BTC'].corr(post['SPX'])
    # Forbes-Rigobon: rho* = rho / sqrt(1 + delta (1 - rho^2)), delta = var_high / var_low - 1 (source market: S&P 500)
    per = {'p1': ('2017-01-01', '2019-12-31'), 'p2': ('2020-01-01', '2023-12-31'), 'p3': (ETF_START, END)}
    x = {k: r.loc[a:b] for k, (a, b) in per.items()}
    fr = {}
    for k in per:
        rho = x[k]['BTC'].corr(x[k]['SPX'])
        delta = x[k]['SPX'].var() / x['p1']['SPX'].var() - 1
        fr[k] = dict(rho=rho, delta=delta, rho_star=rho / np.sqrt(1 + delta * (1 - rho ** 2)), n=len(x[k]),
                     vol_spx=x[k]['SPX'].std() * np.sqrt(252))
    # block bootstrap for rho*_p2 - rho_p1 (each period resampled separately)
    rng = np.random.default_rng(SEED)
    def cbb(z):
        n = len(z)
        nb = int(np.ceil(n / 20))
        st = rng.integers(0, n - 19, nb)
        return z[(st[:, None] + np.arange(20)[None, :]).ravel()[:n]]
    a1, a2 = x['p1'].values, x['p2'].values
    dd = []
    for _ in range(2000):
        z1, z2 = cbb(a1), cbb(a2)
        r1 = np.corrcoef(z1.T)[0, 1]
        r2 = np.corrcoef(z2.T)[0, 1]
        dl = z2[:, 1].var() / z1[:, 1].var() - 1
        dd.append(r2 / np.sqrt(1 + dl * (1 - r2 ** 2)) - r1)
    fr['diff'] = fr['p2']['rho_star'] - fr['p1']['rho']
    fr['diff_lo'], fr['diff_hi'] = np.percentile(dd, [2.5, 97.5])
    sw['fr'] = fr
    return sw


# =============================================================================
# 4. THE PEG: EQUILIBRIUM THRESHOLD AR (EQ-TAR) and the Hansen (1996) linearity test
# =============================================================================
def tar_fit(d, trim=TRIM, B=999, seed=SEED):
    """Equilibrium threshold AR (EQ-TAR, Balke & Fomby 1997): d_t = phi_in d_{t-1} + e_t if |d_{t-1}| <= c,
    d_t = phi_out d_{t-1} + e_t otherwise.
    Threshold c: grid search (values of |d_{t-1}| between the trim and 1 - trim quantiles), minimum SSR.
    Test H0: phi_in = phi_out (linear AR(1)), heteroskedasticity-robust sup-Wald; p-value by the fixed-regressor
    bootstrap y*_t = e_t eta_t, eta_t ~ N(0, 1), e_t the residuals of the linear model (H0) (Hansen, 1996).
    Only pairs (d_(t-1), d_t) on consecutive calendar days: if a period is removed from the series, no
    pair crosses the gap."""
    ok = np.diff(d.index.values).astype('timedelta64[D]') == np.timedelta64(1, 'D')
    y, x = d.values[1:][ok], d.values[:-1][ok]
    a = np.abs(x)
    order = np.argsort(a, kind='stable')
    xs, ys, as_ = x[order], y[order], a[order]
    n = len(y)
    x2 = xs ** 2
    lo, hi = int(np.floor(trim * n)), int(np.ceil((1 - trim) * n))
    # positions where the sample can be split (distinct values of |x|)
    cuts = np.array([i for i in range(lo, hi) if as_[i] < as_[i + 1]]) + 1   # the inner regime = the first i observations

    def wald(yy):
        c1 = np.cumsum(xs * yy)
        c2 = np.cumsum(x2)
        c3 = np.cumsum(x2 * yy ** 2)
        c4 = np.cumsum(xs ** 3 * yy)
        c5 = np.cumsum(xs ** 4)
        T1, T2, T3, T4, T5 = c1[-1], c2[-1], c3[-1], c4[-1], c5[-1]
        i = cuts - 1
        Sin, Sout = c2[i], T2 - c2[i]
        pin, pout = c1[i] / Sin, (T1 - c1[i]) / Sout
        vin = (c3[i] - 2 * pin * c4[i] + pin ** 2 * c5[i]) / Sin ** 2
        vout = ((T3 - c3[i]) - 2 * pout * (T4 - c4[i]) + pout ** 2 * (T5 - c5[i])) / Sout ** 2
        return (pin - pout) ** 2 / (vin + vout), pin, pout, vin, vout

    Wc, pin, pout, vin, vout = wald(ys)
    # threshold estimate: minimum SSR
    c1 = np.cumsum(xs * ys)
    c2 = np.cumsum(x2)
    i = cuts - 1
    ssr = np.sum(ys ** 2) - c1[i] ** 2 / c2[i] - (c1[-1] - c1[i]) ** 2 / (c2[-1] - c2[i])
    j = int(np.argmin(ssr))
    phi_lin = np.sum(x * y) / np.sum(x ** 2)
    e0 = ys - phi_lin * xs
    rng = np.random.default_rng(seed)
    sup0 = Wc.max()
    bs = np.array([wald(e0 * rng.standard_normal(n))[0].max() for _ in range(B)])
    hl = lambda p: float(np.log(0.5) / np.log(abs(p))) if 0 < abs(p) < 1 else None
    nin = int(cuts[j])
    return dict(n=n, c=float(as_[cuts[j] - 1]), n_in=nin, n_out=n - nin, share_out=100 * (n - nin) / n,
                phi_in=float(pin[j]), se_in=float(np.sqrt(vin[j])), phi_out=float(pout[j]), se_out=float(np.sqrt(vout[j])),
                hl_in=hl(pin[j]), hl_out=hl(pout[j]), phi_lin=float(phi_lin), hl_lin=hl(phi_lin),
                sup_w=float(sup0), p_boot=float((1 + (bs >= sup0).sum()) / (B + 1)), B=B,
                chi2_p=float(stats.chi2.sf(sup0, 1)), c_grid=[float(as_[cuts[0] - 1]), float(as_[cuts[-1] - 1])],
                share_var_out=float(100 * np.sum(x2[nin:]) / np.sum(x2)))


def peg_tar(start='2021-01-01'):
    """EQ-TAR for USDT, USDC, DAI: deviation of the daily close in basis points, 2021-2026."""
    out = {}
    for k in STABLE:
        d = 1e4 * (read_market(ASSETS[k][0]).loc[start:END, 'close'] - 1)
        out[k] = tar_fit(d)
    return out


# =============================================================================
# 5. LVR: bootstrap CI for the realised rate
# =============================================================================
def lvr_ci(start='2024-01-01', B=2000, block=20, seed=SEED):
    """Realised annual LVR rate (Milionis et al., 2022): the rebalancing portfolio holds every day the pool's
    ETH x = V/(2P); normalised daily loss (dR_t - dV_t)/V_(t-1) = R_t/2 - (sqrt(1 + R_t) - 1),
    R_t the simple return; rate = sum / years. sigma^2/8 from the variance of log returns; rv8 = sum R_t^2 / 8 / years;
    moving-block bootstrap interval for the realised rate, for sigma^2/8 and for the difference."""
    p = price('ETH', start)
    r = np.log(p).diff().dropna().values
    yrs = (p.index[-1] - p.index[0]).days / 365.25

    def rates(rr):
        R = np.expm1(rr)
        real = np.sum(R / 2 - (np.sqrt(1 + R) - 1)) / yrs
        theo = rr.var(ddof=1) * 365 / 8
        rv8 = np.sum(R ** 2) / 8 / yrs
        return 100 * real, 100 * theo, 100 * rv8
    real, theo, rv8 = rates(r)
    rng = np.random.default_rng(seed)
    n = len(r)
    nb = int(np.ceil(n / block))
    bs = []
    for _ in range(B):
        st = rng.integers(0, n - block + 1, nb)
        bs.append(rates(r[(st[:, None] + np.arange(block)[None, :]).ravel()[:n]]))
    bs = np.array(bs)
    return dict(real=real, theo=theo, rv8=rv8, lo=float(np.percentile(bs[:, 0], 2.5)), hi=float(np.percentile(bs[:, 0], 97.5)),
                t_lo=float(np.percentile(bs[:, 1], 2.5)), t_hi=float(np.percentile(bs[:, 1], 97.5)),
                d_lo=float(np.percentile(bs[:, 0] - bs[:, 1], 2.5)), d_hi=float(np.percentile(bs[:, 0] - bs[:, 1], 97.5)),
                corr=float(np.corrcoef(bs[:, 0], bs[:, 1])[0, 1]), n=n, years=yrs)


# =============================================================================
# 6. ASSET-CLASS MAP: bootstrap for the change in distances
# =============================================================================
def class_distances(f):
    """Centroid distances (crypto vs classes) and crypto dispersion, by window, in the common standardised space."""
    X = f[FEATURES].values
    Z = (X - X.mean(0)) / X.std(0)
    zc = pd.DataFrame(Z, columns=FEATURES)
    zc['cls'], zc['window'] = f['cls'].values, f['window'].values
    out = {}
    for w in WINDOWS:
        g = zc[zc.window == w]
        cen = g.groupby('cls')[FEATURES].mean()
        cr = g[g.cls == 'Crypto'][FEATURES].values
        out[w] = dict(eq=np.linalg.norm(cen.loc['Crypto'] - cen.loc['Equity']),
                      com=np.linalg.norm(cen.loc['Crypto'] - cen.loc['Commodity']),
                      fx=np.linalg.norm(cen.loc['Crypto'] - cen.loc['FX']),
                      bond=np.linalg.norm(cen.loc['Crypto'] - cen.loc['Bond']),
                      spread=np.mean(np.linalg.norm(cr - cr.mean(0), axis=1)))
    return out


def alt_bootstrap(B=500, block=28, seed=SEED):
    """Moving-block bootstrap common to all assets: in each window, blocks of 28 calendar days
    (4 weeks = 20 weekdays) are drawn and each asset takes its own returns (on its own calendar)
    from the same days, so the dependence between assets is kept; features recomputed, common
    standardisation, the change W2 - W1 in the distances; 95% percentile CI."""
    rng = np.random.default_rng(seed)
    base = []
    series = {}
    for s, (lab, cls, _) in CLASS_ASSETS.items():
        for w, (a, b) in WINDOWS.items():
            r = symbol_returns(s, a, b)
            series[(s, w)] = r
            base.append(dict(symbol=s, cls=cls, window=w, **asset_features(r)))
    f0 = pd.DataFrame(base)
    d0 = class_distances(f0)
    cal = {w: pd.date_range(min(r.index[0] for (s, ww), r in series.items() if ww == w),
                            max(r.index[-1] for (s, ww), r in series.items() if ww == w), freq='D') for w in WINDOWS}
    ppy = {k: periods_per_year(r) for k, r in series.items()}
    draws = []
    for _ in range(B):
        rows = []
        for w, days in cal.items():
            n = len(days)
            st = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
            sel = days[(st[:, None] + np.arange(block)[None, :]).ravel()[:n]]      # the same days for all assets
            for (s, ww), r in series.items():
                if ww != w:
                    continue
                rr = r.reindex(sel).dropna()
                rows.append(dict(symbol=s, cls=CLASS_ASSETS[s][1], window=w, **asset_features(rr, ppy[(s, w)])))
        d = class_distances(pd.DataFrame(rows))
        draws.append({k: d['W2'][k] - d['W1'][k] for k in d['W1']})
    D = pd.DataFrame(draws)
    out = {}
    for k in D:
        out[k] = dict(w1=d0['W1'][k], w2=d0['W2'][k], diff=d0['W2'][k] - d0['W1'][k],
                      lo=float(D[k].quantile(0.025)), hi=float(D[k].quantile(0.975)), share_pos=float((D[k] >= 0).mean()))
    hl = f0[f0.cls == 'Crypto'].groupby('window')['hill_left'].median()
    out['hill_crypto'] = {w: float(hl[w]) for w in WINDOWS}
    out['hill_crypto_n_below4'] = {w: int((f0[(f0.cls == 'Crypto') & (f0.window == w)]['hill_left'] < 4).sum())
                                   for w in WINDOWS}
    out['B'] = B
    return out


# =============================================================================
# 7. CRYPTO ASSET PRICING: GRS and Fama-MacBeth with the Shanken correction
# =============================================================================
COINS = ['BTC', 'ETH', 'XRP', 'BNB', 'ADA', 'DOGE', 'LTC', 'LINK']


def weekly_rf():
    """Weekly risk-free rate from the 4-week Treasury bill yield (FRED DTB4WK, % a year)."""
    s = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB4WK', index_col=0, parse_dates=True).iloc[:, 0]
    s = pd.to_numeric(s, errors='coerce').dropna()
    return (s / 100 / 52).resample('W-FRI').last().ffill()


def grs_test(R, f):
    """GRS = (T - N - K)/N * a' S^-1 a / (1 + m' O^-1 m) ~ F(N, T - N - K) under i.i.d. errors with the Normal
    distribution; S, O maximum-likelihood estimators (division by T)."""
    T, N = R.shape
    K = f.shape[1]
    X = np.column_stack([np.ones(T), f])
    B = np.linalg.lstsq(X, R, rcond=None)[0]
    E = R - X @ B
    S = E.T @ E / T
    m = f.mean(0)
    O = np.atleast_2d(np.cov(f.T, bias=True))
    a = B[0]
    stat = (T - N - K) / N * (a @ np.linalg.solve(S, a)) / (1 + m @ np.linalg.solve(O, m))
    return stat, B, E


def asset_pricing(start='2018-01-05', Bb=2000, seed=SEED):
    """Eight coins, weekly simple excess returns (Friday); market factor = the market-value weighted total index
    (5 coins with a public circulating supply), in excess of the risk-free rate.
    GRS with the F p-value and a wild-bootstrap p-value (Rademacher by row, under H0: alpha = 0);
    Fama-MacBeth: first-stage betas on the full sample, weekly cross-sectional regressions; FM and Shanken errors."""
    tot, _ = crix_index(None, 'cap')
    p = pd.concat([price(c) for c in COINS] + [tot.rename('MKT')], axis=1).dropna()
    w = p.resample('W-FRI').last().pct_change().dropna().loc[start:END]
    rf = weekly_rf().reindex(w.index).ffill()
    ex = w.sub(rf, axis=0).dropna()
    R, f = ex[COINS].values, ex[['MKT']].values
    T, N = R.shape
    K = 1
    stat, Bc, E = grs_test(R, f)
    p_f = float(stats.f.sf(stat, N, T - N - K))
    rng = np.random.default_rng(seed)
    X = np.column_stack([np.ones(T), f])
    fit0 = X[:, 1:] @ Bc[1:]
    bs = []
    for _ in range(Bb):
        eta = rng.choice([-1.0, 1.0], T)[:, None]
        bs.append(grs_test(fit0 + E * eta, f)[0])
    p_boot = float((1 + (np.array(bs) >= stat).sum()) / (Bb + 1))
    beta = Bc[1]
    alpha_ann = 52 * 100 * Bc[0]
    # Fama-MacBeth
    Xc = np.column_stack([np.ones(N), beta])
    G = np.array([np.linalg.lstsq(Xc, R[t], rcond=None)[0] for t in range(T)])
    gam = G.mean(0)
    se_fm = G.std(0, ddof=1) / np.sqrt(T)
    Sig = E.T @ E / T
    sf = f.var(ddof=1)
    lam = gam[1]
    A = np.linalg.inv(Xc.T @ Xc) @ Xc.T
    V = (A @ Sig @ A.T) * (1 + lam ** 2 / sf) / T + np.diag([0.0, sf]) / T
    se_sh = np.sqrt(np.diag(V))
    return dict(T=T, N=N, K=K, start=str(ex.index[0].date()), end=str(ex.index[-1].date()),
                grs=float(stat), p_f=p_f, p_boot=p_boot, B=Bb, beta={c: float(b) for c, b in zip(COINS, beta)},
                alpha={c: float(a) for c, a in zip(COINS, alpha_ann)},
                alpha_t={c: float(a / s) for c, a, s in zip(COINS, Bc[0], np.sqrt(np.diag(Sig) / T * (1 + (f.mean() ** 2) / f.var(ddof=0))))},
                g0=float(52 * 100 * gam[0]), g1=float(52 * 100 * gam[1]), se_fm0=float(52 * 100 * se_fm[0]),
                se_fm1=float(52 * 100 * se_fm[1]), se_sh0=float(52 * 100 * se_sh[0]), se_sh1=float(52 * 100 * se_sh[1]),
                t_fm1=float(gam[1] / se_fm[1]), t_sh1=float(gam[1] / se_sh[1]), mkt_ann=float(52 * 100 * f.mean()),
                mkt_t=float(f.mean() / (f.std(ddof=1) / np.sqrt(T))), shanken_c=float(lam ** 2 / sf),
                hill_mkt=float(hill(-f.ravel())), beta_min=float(beta.min()), beta_max=float(beta.max()))


# =============================================================================
# 8. DIMSON (1979) BETA for the spot ETFs
# =============================================================================
def dimson(etf='IBIT', coin='BTC'):
    """r_ETF,t = a + b_-1 r_coin,t-1 + b_0 r_coin,t + b_+1 r_coin,t+1 + u_t, on common days; Dimson beta = the sum,
    Newey-West standard error."""
    r = 100 * joint_returns([etf, coin])
    X = pd.concat([r[coin].shift(1).rename('lag'), r[coin].rename('now'), r[coin].shift(-1).rename('lead')], axis=1)
    d = pd.concat([r[etf], X], axis=1).dropna()
    m = sm.OLS(d[etf], sm.add_constant(d[['lag', 'now', 'lead']])).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    R = np.array([0, 1, 1, 1])
    s = float(R @ m.params.values)
    se = float(np.sqrt(R @ m.cov_params().values @ R))
    m0 = sm.OLS(d[etf], sm.add_constant(d['now'])).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    return dict(n=len(d), b_lag=float(m.params['lag']), b_now=float(m.params['now']), b_lead=float(m.params['lead']),
                se_lead=float(m.bse['lead']), sum=s, se=se, t1=(s - 1) / se, b_ols=float(m0.params['now']),
                se_ols=float(m0.bse['now']), r2=float(m.rsquared))


# =============================================================================
# 9. ROBUSTNESS OF THE INFERENCE (dependence, regime-specific break CI, joint bootstrap, multiple testing)
# =============================================================================
def holm(p):
    """Holm (1979) step-down adjusted p-values for a dict {name: p}."""
    ks = sorted(p, key=p.get)
    adj, run = {}, 0.0
    for i, k in enumerate(ks):
        run = max(run, min(1.0, (len(ks) - i) * p[k]))
        adj[k] = run
    return adj


def _tar_design(d, p):
    """Pairs on consecutive calendar days: y = d_t, x = d_(t-1), L = (Delta d_(t-1), ..., Delta d_(t-p))."""
    s = d.copy()
    full = pd.Series(s.values, index=s.index).asfreq('D')
    y, x = full, full.shift(1)
    L = pd.concat([full.diff().shift(j).rename(f'dd{j}') for j in range(1, p + 1)], axis=1) if p else None
    D = pd.concat([y.rename('y'), x.rename('x')] + ([L] if p else []), axis=1).dropna()
    return D['y'].values, D['x'].values, (D[[f'dd{j}' for j in range(1, p + 1)]].values if p else np.zeros((len(D), 0)))


def _tar_stats(ys, xs, Ls, cuts, A, Lx_cum, LtY, Lx_tot):
    """Heteroskedasticity-robust Wald statistics for phi_in = phi_out at every cut (sorted order; the common lag
    coefficients are partialled out, Frisch-Waugh-Lovell); returns W, phi_in, phi_out."""
    n = len(ys)
    i = cuts - 1
    S2 = np.cumsum(xs ** 2)
    Sxy = np.cumsum(xs * ys)
    a = Lx_cum[i]                       # L' x_in, one row per cut
    b = Lx_tot[None, :] - a             # L' x_out
    Aa, Ab = a @ A, b @ A
    m11 = S2[i] - np.einsum('ij,ij->i', Aa, a)
    m22 = (S2[-1] - S2[i]) - np.einsum('ij,ij->i', Ab, b)
    m12 = -np.einsum('ij,ij->i', Aa, b)
    r1 = Sxy[i] - Aa @ LtY
    r2 = (Sxy[-1] - Sxy[i]) - Ab @ LtY
    det = m11 * m22 - m12 ** 2
    pin = (m22 * r1 - m12 * r2) / det
    pout = (m11 * r2 - m12 * r1) / det
    inner = (np.arange(n)[None, :] < cuts[:, None])
    Xin = np.where(inner, xs[None, :], 0.0)
    Xout = np.where(inner, 0.0, xs[None, :])
    if Ls.shape[1]:
        gam = (LtY[None, :] - a * pin[:, None] - b * pout[:, None]) @ A            # cuts x p
        U = ys[None, :] - Xin * pin[:, None] - Xout * pout[:, None] - gam @ Ls.T
        Xin_t = Xin - Aa @ Ls.T
        Xout_t = Xout - Ab @ Ls.T
    else:
        U = ys[None, :] - Xin * pin[:, None] - Xout * pout[:, None]
        Xin_t, Xout_t = Xin, Xout
    U2 = U ** 2
    s11, s22, s12 = (U2 * Xin_t ** 2).sum(1), (U2 * Xout_t ** 2).sum(1), (U2 * Xin_t * Xout_t).sum(1)
    # V = M^-1 S M^-1 for the 2x2 block; variance of phi_in - phi_out
    Mi = np.stack([np.stack([m22, -m12], -1), np.stack([-m12, m11], -1)], -2) / det[:, None, None]
    Sm = np.stack([np.stack([s11, s12], -1), np.stack([s12, s22], -1)], -2)
    V = Mi @ Sm @ Mi
    c = np.array([1.0, -1.0])
    var = np.einsum('i,nij,j->n', c, V, c)
    return (pin - pout) ** 2 / var, pin, pout, U


def tar_robust(d, p=None, pmax=14, trim=TRIM, B=999, block=None, seed=SEED):
    """EQ-TAR with p lagged differences (common coefficients; if p is None, the smallest p in 0..pmax for which the
    Ljung-Box test with 10 lags does not reject at 5% the absence of autocorrelation in the residuals),
    threshold re-estimated by minimum SSR; sup-Wald (White) for phi_in = phi_out; p-value by the fixed-regressor
    bootstrap with block multipliers (dependent wild bootstrap: eta constant on blocks of consecutive pairs,
    length n^(1/3)), which keeps the serial dependence of the scores. Also: lag-1 autocorrelation of the score
    x_t e_t and the Ljung-Box p-value (10 lags) of the residuals at the estimated threshold."""
    from statsmodels.stats.diagnostic import acorr_ljungbox
    if p is None:
        for p in range(pmax + 1):
            if tar_robust(d, p=p, trim=trim, B=0)['lb10_p'] >= 0.05:
                break
    y, x, L = _tar_design(d, p)
    n = len(y)
    order = np.argsort(np.abs(x), kind='stable')
    xs, ys, Ls, as_ = x[order], y[order], L[order], np.abs(x)[order]
    lo, hi = int(np.floor(trim * n)), int(np.ceil((1 - trim) * n))
    cuts = np.array([i for i in range(lo, hi) if as_[i] < as_[i + 1]]) + 1
    A = np.linalg.inv(Ls.T @ Ls) if p else np.zeros((0, 0))
    Lx_cum = np.cumsum(Ls * xs[:, None], axis=0)
    Lx_tot = Lx_cum[-1]
    W, pin, pout, U = _tar_stats(ys, xs, Ls, cuts, A, Lx_cum, Ls.T @ ys, Lx_tot)
    ssr = (U ** 2).sum(1)
    j = int(np.argmin(ssr))
    e_hat = np.empty(n)
    e_hat[order] = U[j]
    xin = np.abs(x) <= as_[cuts[j] - 1]
    score = x * e_hat
    lb = float(acorr_ljungbox(e_hat, lags=[10])['lb_pvalue'].iloc[0])
    # restricted (linear) residuals, in time order, for the bootstrap
    Z = np.column_stack([x, L])
    e0 = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
    ell = block or int(np.ceil(n ** (1 / 3)))
    rng = np.random.default_rng(seed)
    sup0 = float(W.max())
    nb = int(np.ceil(n / ell))
    bs = np.empty(B)
    for bi in range(B):
        eta = np.repeat(rng.standard_normal(nb), ell)[:n]
        yb = (e0 * eta)[order]
        bs[bi] = _tar_stats(yb, xs, Ls, cuts, A, Lx_cum, Ls.T @ yb, Lx_tot)[0].max()
    return dict(n=n, lags=int(p), block=ell, c=float(as_[cuts[j] - 1]), phi_in=float(pin[j]), phi_out=float(pout[j]),
                sup_w=sup0, p_block=float((1 + (bs >= sup0).sum()) / (B + 1)) if B else None, B=B,
                score_ac1=float(pd.Series(score).autocorr(1)), lb10_p=lb, share_in=float(100 * xin.mean()))


def peg_robust(start='2021-01-01', B=999):
    """For USDT, USDC, DAI, full sample and without 9-16 March 2023: (i) AR(1) EQ-TAR with block multipliers;
    (ii) EQ-TAR with BIC-selected lagged differences and block multipliers; lag-1 autocorrelation of the score of
    the AR(1) EQ-TAR; Holm over the three coins for each sample and specification."""
    out = {}
    for k in STABLE:
        d = 1e4 * (read_market(ASSETS[k][0]).loc[start:END, 'close'] - 1)
        ex = d.drop(d.loc['2023-03-09':'2023-03-16'].index)
        out[k] = {}
        for lab, dd in (('full', d), ('ex', ex)):
            out[k][lab] = dict(ar1=tar_robust(dd, p=0, B=B), aug=tar_robust(dd, B=B), iid=tar_fit(dd))
            print('   tar', k, lab, out[k][lab]['ar1']['p_block'], out[k][lab]['aug']['p_block'], out[k][lab]['aug']['lags'])
    out['holm'] = {}
    for lab in ('full', 'ex'):
        for spec in ('ar1', 'aug'):
            out['holm'][f'{lab}_{spec}'] = holm({k: out[k][lab][spec]['p_block'] for k in STABLE})
        out['holm'][f'{lab}_iid'] = holm({k: out[k][lab]['iid']['p_boot'] for k in STABLE})
    return out


def _argmax_quantiles(xi, phi, reps=20000, h=0.02, S=150.0, seed=SEED):
    """2.5% and 97.5% quantiles of argmax_s Z(s), Z(s) = W1(-s) - |s|/2 (s <= 0), sqrt(phi) W2(s) - xi s/2 (s > 0)
    (Bai, 1997, regimes with different moments); simulation on a grid of step h over [-S, S]."""
    rng = np.random.default_rng(seed)
    m = int(S / h)
    s = np.arange(1, m + 1) * h
    out = []
    for _ in range(reps // 500):
        W1 = np.cumsum(rng.standard_normal((500, m)) * np.sqrt(h), axis=1) - s / 2
        W2 = np.sqrt(phi) * np.cumsum(rng.standard_normal((500, m)) * np.sqrt(h), axis=1) - xi * s / 2
        z = np.concatenate([W1[:, ::-1], np.zeros((500, 1)), W2], axis=1)
        grid = np.concatenate([-s[::-1], [0.0], s])
        out.append(grid[np.argmax(z, axis=1)])
    out = np.concatenate(out)
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def bai_ci(y, X, index, tb, L):
    """Bai (1997) 95% CI for the break date with regime-specific moments: Q_i = X_i'X_i / T_i and the long-run
    variance Omega_i of x_t u_t (Bartlett, L lags) in each regime; lambda = (d'Q_1 d)^2 / (d'Omega_1 d),
    xi = d'Q_2 d / d'Q_1 d, phi = d'Omega_2 d / d'Omega_1 d; CI = [tb - c_hi/lambda - 1, tb - c_lo/lambda + 1]."""
    T = len(y)
    Q, Om, bet, vu = [], [], [], []
    for a, b in [(0, tb), (tb, T)]:
        Xa, ya = X[a:b], y[a:b]
        bb = np.linalg.lstsq(Xa, ya, rcond=None)[0]
        u = ya - Xa @ bb
        Q.append(Xa.T @ Xa / (b - a))
        Om.append(hac_meat(Xa, u, L) / (b - a))
        bet.append(bb)
        vu.append(float(np.var(u, ddof=X.shape[1])))
    dlt = bet[1] - bet[0]
    q1, q2 = dlt @ Q[0] @ dlt, dlt @ Q[1] @ dlt
    o1, o2 = dlt @ Om[0] @ dlt, dlt @ Om[1] @ dlt
    lam = q1 ** 2 / o1
    xi, phi = q2 / q1, o2 / o1
    c_lo, c_hi = _argmax_quantiles(xi, phi)
    k_lo = max(tb - int(np.ceil(c_hi / lam)) - 1, 0)
    k_hi = min(tb - int(np.floor(c_lo / lam)) + 1, T - 1)
    idx = pd.DatetimeIndex(index)
    return dict(xi=float(xi), phi=float(phi), lam=float(lam), c_lo=c_lo, c_hi=c_hi, var_u=vu,
                ci_lo=str(idx[k_lo].date()), ci_hi=str(idx[k_hi].date()), n_lo=tb - k_lo, n_hi=k_hi - tb)


def break_robust(start='2016-01-01', B=2000, seed=SEED):
    """BTC-SPX: Bai (1997) CI with regime-specific Q and long-run variances; test for a second break
    (sup-Wald in each regime, Bai-Perron sequential statistic sup F(2|1) = max over the two regimes,
    P(max <= x) = G(x)^2); block-bootstrap CI for the change in the correlation at the estimated date; sample sizes."""
    r = 100 * joint_returns(['BTC', 'SPX'], start)
    y = r['BTC'].values
    X = np.column_stack([np.ones(len(r)), r['SPX'].values])
    T = len(y)
    sw = sup_wald(y, X, r.index)
    tb = int(np.where(r.index == pd.Timestamp(sw['date']))[0][0])
    seg = [(0, tb), (tb, T)]
    out = bai_ci(y, X, r.index, tb, sw['lags'])
    out.update(T=T, n_pre=tb, n_post=T - tb, date=sw['date'],
               var_spx=[float(r['SPX'].values[a:b].var(ddof=1)) for a, b in seg], ci_sym=[sw['ci_lo'], sw['ci_hi']])
    crit = sup_wald_crit(2)
    sub = []
    for a, b in seg:
        s2 = sup_wald(y[a:b], X[a:b], r.index[a:b])
        sub.append(dict(sup_w=s2['sup_w'], date=s2['date'], n=b - a))
    stat = max(z['sup_w'] for z in sub)
    G = (crit < stat).mean()
    out['second'] = dict(seg=sub, stat=float(stat), p=float(1 - G ** 2), cv5=float(np.percentile(crit, 100 * 0.95 ** 0.5)))
    # correlation before / after the estimated date: moving-block bootstrap within each regime
    rng = np.random.default_rng(seed)
    pre, post = r.values[:tb], r.values[tb:]
    def cbb(z, bl=20):
        n = len(z)
        st = rng.integers(0, n - bl + 1, int(np.ceil(n / bl)))
        return z[(st[:, None] + np.arange(bl)[None, :]).ravel()[:n]]
    rp, rq = np.corrcoef(pre.T)[0, 1], np.corrcoef(post.T)[0, 1]
    dd = [np.corrcoef(cbb(post).T)[0, 1] - np.corrcoef(cbb(pre).T)[0, 1] for _ in range(B)]
    out['rho'] = dict(pre=float(rp), post=float(rq), diff=float(rq - rp), lo=float(np.percentile(dd, 2.5)),
                      hi=float(np.percentile(dd, 97.5)))
    return out


def hill_joint(start='2018-01-01', B=1000, block=28, seed=SEED):
    """Differences of the Hill indices (left tail) for BTC-SPX, BTC-GOLD, DOGE-SPX: moving-block bootstrap common to
    both assets (blocks of 28 calendar days; each asset takes its own returns, on its own calendar, from the
    same days), at k = 2.5%, 5% and 10% of the losses; 95% percentile CI and the bootstrap SE."""
    rng = np.random.default_rng(seed)
    R = {k: 100 * np.log(price(k, start)).diff().dropna() for k in ['BTC', 'DOGE', 'SPX', 'GOLD']}
    days = pd.date_range(min(s.index[0] for s in R.values()), max(s.index[-1] for s in R.values()), freq='D')
    n = len(days)
    fr = {'k2.5': 0.025, 'k5': 0.05, 'k10': 0.10}
    pairs = [('BTC', 'SPX'), ('BTC', 'GOLD'), ('DOGE', 'SPX')]
    est = {(a, f): hill(-R[a].values, fr[f]) for a in R for f in fr}
    draws = {(a, b, f): [] for a, b in pairs for f in fr}
    for _ in range(B):
        st = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
        sel = days[(st[:, None] + np.arange(block)[None, :]).ravel()[:n]]
        hb = {}
        for a in R:
            x = -R[a].reindex(sel).dropna().values
            for f in fr:
                hb[(a, f)] = hill(x, fr[f])
        for a, b in pairs:
            for f in fr:
                draws[(a, b, f)].append(hb[(a, f)] - hb[(b, f)])
    out = {}
    for a, b in pairs:
        for f in fr:
            dv = np.array(draws[(a, b, f)])
            out[f'{a}_{b}_{f}'] = dict(diff=float(est[(a, f)] - est[(b, f)]), lo=float(np.percentile(dv, 2.5)),
                                       hi=float(np.percentile(dv, 97.5)), se=float(dv.std()))
    return out


def ap_robust(start='2018-01-05', Bb=2000, block=4, L=None, seed=SEED):
    """GRS and Fama-MacBeth with serial dependence: Ljung-Box (4 lags) of the time-series residuals; GRS p-value by
    the wild bootstrap with block multipliers (constant on 4 consecutive weeks); Newey-West SE of the mean
    cross-sectional slopes; moving-block bootstrap of weeks (blocks of 4) that re-estimates both stages."""
    from statsmodels.stats.diagnostic import acorr_ljungbox
    tot, _ = crix_index(None, 'cap')
    p = pd.concat([price(c) for c in COINS] + [tot.rename('MKT')], axis=1).dropna()
    w = p.resample('W-FRI').last().pct_change().dropna().loc[start:END]
    rf = weekly_rf().reindex(w.index).ffill()
    ex = w.sub(rf, axis=0).dropna()
    R, f = ex[COINS].values, ex[['MKT']].values
    T, N = R.shape
    stat, Bc, E = grs_test(R, f)
    lb = {c: float(acorr_ljungbox(E[:, i], lags=[4])['lb_pvalue'].iloc[0]) for i, c in enumerate(COINS)}
    lbsq = {c: float(acorr_ljungbox(E[:, i] ** 2, lags=[4])['lb_pvalue'].iloc[0]) for i, c in enumerate(COINS)}
    ac1 = {c: float(pd.Series(E[:, i]).autocorr(1)) for i, c in enumerate(COINS)}
    rng = np.random.default_rng(seed)
    X = np.column_stack([np.ones(T), f])
    fit0 = X[:, 1:] @ Bc[1:]
    nb = int(np.ceil(T / block))
    bs = []
    for _ in range(Bb):
        eta = np.repeat(rng.choice([-1.0, 1.0], nb), block)[:T][:, None]
        bs.append(grs_test(fit0 + E * eta, f)[0])
    p_block = float((1 + (np.array(bs) >= stat).sum()) / (Bb + 1))

    def fm(Rm, fm_):
        Tm = len(Rm)
        Xm = np.column_stack([np.ones(Tm), fm_])
        beta = np.linalg.lstsq(Xm, Rm, rcond=None)[0][1]
        Xc = np.column_stack([np.ones(N), beta])
        return np.array([np.linalg.lstsq(Xc, Rm[t], rcond=None)[0] for t in range(Tm)])
    G = fm(R, f)
    gam = G.mean(0)
    Lw = nw_lags(T) if L is None else L
    se_nw = np.sqrt(np.diag(hac_meat(np.ones((T, 1)), G[:, 1] - gam[1], Lw)))[0] / T
    se_nw0 = np.sqrt(np.diag(hac_meat(np.ones((T, 1)), G[:, 0] - gam[0], Lw)))[0] / T
    lam_b = []
    for _ in range(Bb):
        st = rng.integers(0, T - block + 1, nb)
        ix = (st[:, None] + np.arange(block)[None, :]).ravel()[:T]
        lam_b.append(fm(R[ix], f[ix]).mean(0)[1])
    lam_b = np.array(lam_b)
    return dict(T=T, grs=float(stat), p_block=p_block, block=block, lb4=lb, lb4_sq=lbsq, ac1=ac1,
                n_lb_rej=int(sum(v < 0.05 for v in lb.values())), n_lbsq_rej=int(sum(v < 0.05 for v in lbsq.values())),
                g1=float(52 * 100 * gam[1]), se_nw1=float(52 * 100 * se_nw), se_nw0=float(52 * 100 * se_nw0), lags=Lw,
                se_mbb1=float(52 * 100 * lam_b.std()), lo_mbb1=float(52 * 100 * np.percentile(lam_b, 2.5)),
                hi_mbb1=float(52 * 100 * np.percentile(lam_b, 97.5)), ac1_g1=float(pd.Series(G[:, 1]).autocorr(1)))


def robust():
    res = {}
    res['break'] = break_robust()
    print('break done')
    res['hill'] = hill_joint()
    print('hill done')
    res['ap'] = ap_robust()
    print('ap done')
    res['tar'] = peg_robust()
    print('tar done')
    with open(os.path.join(HERE, 'ch16_robust.json'), 'w') as fh:
        json.dump(jsonable(res), fh, indent=1)
    print(json.dumps(jsonable({k: v for k, v in res.items() if k != 'tar'}), indent=1))
    return res


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == '--robust':
    robust()
    sys.exit(0)


if __name__ == '__main__':
    print('Chapter 16: inference')
    res = {}
    res['hill'] = hill_inference()
    print('hill done')
    res['crix_rule'] = cr = crix_rule()
    with open(os.path.join(HERE, 'ch16_results.json')) as fh:
        te = json.load(fh)['crix']['te']
    fig_crix_rule(cr, te)
    print('crix done', cr['ecrix_counts'], cr['efcrix_counts'])
    res['break'] = break_btc_spx()
    print('break done')
    res['tar'] = peg_tar()
    print('tar done')
    res['lvr'] = lvr_ci()
    res['alt'] = alt_bootstrap()
    print('alt done')
    res['ap'] = asset_pricing()
    res['dimson'] = {'ibit': dimson('IBIT', 'BTC'), 'etha': dimson('ETHA', 'ETH')}
    robust()                     # ch16_robust.json
    with open(os.path.join(HERE, 'ch16_inference.json'), 'w') as fh:
        json.dump(jsonable(res), fh, indent=1)
    print(json.dumps(jsonable({k: v for k, v in res.items() if k != 'crix_rule'}), indent=1))
    print('saved ch16_inference.json')

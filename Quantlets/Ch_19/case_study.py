"""
case_study.py -- Integrated case study of Chapter 19 (MFM)
================================================================
One thread, on one series: stylised facts (Ch. 1) -> GARCH(1,1)-t (Ch. 5)
-> next-day VaR 1% and ES 2.5% (Ch. 7) -> backtesting (Ch. 8).

  * stylised_facts(r)        -- moments, Jarque-Bera and Ljung-Box tests on r and r^2, ACF
  * garch_t_fit(r)           -- GARCH(1,1) with Student-t innovations (constant mean), r in %
  * rolling_var(r, ...)      -- next-day VaR 1% (and ES 2.5%) forecasts, rolling window,
                                four models: HS, Normal, GARCH-t, FHS (filtered historical simulation)
  * kupiec / christoffersen  -- coverage and independence tests of the breaches
  * traffic_light            -- Basel zones for x breaches in 250 days

Convention: alpha = tail probability (VaR 1%); loss L = -r; VaR and ES are positive, in % of the position.
Modelling Financial Markets - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats
from arch import arch_model

ALPHA = 0.01          # VaR 1%
ALPHA_ES = 0.025      # ES 2.5%
WINDOW = 1000         # days in the estimation window
REFIT = 21            # GARCH re-estimated every 21 days
HS_WINDOW = 500       # window for HS and for the Normal distribution
MODELS = ['HS', 'Normal', 'GARCH-t', 'FHS']


# -----------------------------------------------------------------------------
# 1. STYLISED FACTS
# -----------------------------------------------------------------------------
def ljung_box(x, m=10):
    """Q(m) = T(T+2) sum rho_k^2/(T-k) and its chi2(m) p-value."""
    x = np.asarray(x) - np.mean(x)
    T = len(x)
    rho = np.array([np.sum(x[k:] * x[:-k]) for k in range(1, m + 1)]) / np.sum(x ** 2)
    q = T * (T + 2) * np.sum(rho ** 2 / (T - np.arange(1, m + 1)))
    return q, stats.chi2.sf(q, m)


def acf(x, nlags):
    x = np.asarray(x) - np.mean(x)
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, nlags + 1)])


def stylised_facts(r):
    """Summary of the stylised facts of the returns r (in %)."""
    jb, jbp = stats.jarque_bera(r)
    q_r, q_rp = ljung_box(r)
    q_r2, q_r2p = ljung_box(r ** 2)
    z = (r - r.mean()) / r.std()
    return dict(N=len(r), start=str(r.index[0].date()), end=str(r.index[-1].date()),
                mean=r.mean(), sd=r.std(), skew=stats.skew(r), kurt=stats.kurtosis(r),
                min=r.min(), min_date=str(r.idxmin().date()), max=r.max(),
                jb=jb, jb_p=jbp, q_r=q_r, q_r_p=q_rp, q_r2=q_r2, q_r2_p=q_r2p,
                acf1_r=acf(r, 1)[0], acf1_abs=acf(np.abs(r), 1)[0],
                n4=int(np.sum(np.abs(z) > 4)), n4_normal=len(r) * 2 * stats.norm.sf(4))


def kurtosis_boot_ci(r, B=2000, block=20, seed=0):
    """95% CI for the excess kurtosis by moving-block bootstrap (keeps volatility clustering)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(r)
    T = len(x)
    nb = int(np.ceil(T / block))
    ks = []
    for _ in range(B):
        idx = (rng.integers(0, T - block + 1, nb)[:, None] + np.arange(block)).ravel()[:T]
        ks.append(stats.kurtosis(x[idx]))
    return np.percentile(ks, [2.5, 97.5])


# -----------------------------------------------------------------------------
# 2. GARCH(1,1)-t
# -----------------------------------------------------------------------------
def garch_t_fit(r, last_obs=None):
    am = arch_model(r, mean='Constant', vol='GARCH', p=1, q=1, dist='t', rescale=False)
    return am.fit(disp='off', last_obs=last_obs)


def garch_summary(res, ppy=None):
    """Parameters, robust standard errors, persistence and half-life; long-run volatility
    annualised with the real frequency of the series (ppy = observations per year; by default from the estimation data)."""
    p, se = res.params, res.std_err
    if ppy is None:
        ix = res.resid.dropna().index
        ppy = len(ix) / ((ix[-1] - ix[0]).days / 365.25)
    pers = p['alpha[1]'] + p['beta[1]']
    return dict(mu=p['mu'], omega=p['omega'], alpha=p['alpha[1]'], beta=p['beta[1]'], nu=p['nu'],
                se_alpha=se['alpha[1]'], se_beta=se['beta[1]'], se_nu=se['nu'],
                pers=pers, half_life=np.log(0.5) / np.log(pers),
                uncond_vol=np.sqrt(ppy * p['omega'] / (1 - pers)))


def t_std_q(nu, a):
    """Quantile of order a of the standardised Student-t distribution (variance 1)."""
    return stats.t.ppf(a, nu) * np.sqrt((nu - 2) / nu)


def t_std_es(nu, a):
    """E[Z | Z <= q_a] for the standardised Student-t (negative)."""
    q = stats.t.ppf(a, nu)
    return -(stats.t.pdf(q, nu) / a) * (nu + q ** 2) / (nu - 1) * np.sqrt((nu - 2) / nu)


# -----------------------------------------------------------------------------
# 3. NEXT-DAY VaR 1% FORECASTS (rolling window)
# -----------------------------------------------------------------------------
def rolling_var(r, eval_from, window=WINDOW, refit=REFIT, a=ALPHA, a_es=ALPHA_ES):
    """VaR (level a) and ES (level a_es) forecasts for every day t >= eval_from, with information up to t-1.
    Returns a DataFrame with the loss L_t and VaR/ES for HS, Normal, GARCH-t and FHS."""
    r = r.dropna()
    idx = r.index
    start = idx.searchsorted(pd.Timestamp(eval_from))
    start = max(start, window)
    rows = []
    for b0 in range(start, len(r), refit):
        b1 = min(b0 + refit, len(r))
        est = r.iloc[b0 - window:b0]
        # estimation ONLY on the window (no data from the evaluation block); sigma_t for t >= b0 by the GARCH
        # recursion started from the last filtered variance of the window, with the returns already observed (up to t-1)
        res = arch_model(est, mean='Constant', vol='GARCH', p=1, q=1, dist='t', rescale=False).fit(disp='off')
        mu, nu = res.params['mu'], res.params['nu']
        om, al, be = res.params['omega'], res.params['alpha[1]'], res.params['beta[1]']
        s_tr = res.conditional_volatility.values
        s2 = np.empty(b1 - b0)
        prev_s2, prev_e = s_tr[-1] ** 2, est.iloc[-1] - mu
        for i in range(b1 - b0):
            s2[i] = om + al * prev_e ** 2 + be * prev_s2
            prev_s2, prev_e = s2[i], r.iloc[b0 + i] - mu
        sig = pd.Series(np.concatenate([s_tr, np.sqrt(s2)]), index=r.index[b0 - window:b1])
        z = ((est - mu) / sig.iloc[:window]).values   # standardised residuals of the window
        zq = np.quantile(z, a)
        zq_es = np.quantile(z, a_es)
        zes = z[z <= zq_es].mean()
        for j in range(b0, b1):
            hist = r.iloc[j - HS_WINDOW:j].values
            s = sig.iloc[j - (b0 - window)]
            L_hist = -hist
            q_hs = np.quantile(L_hist, 1 - a)
            q_hs_es = np.quantile(L_hist, 1 - a_es)
            m, sd = hist.mean(), hist.std(ddof=1)
            rows.append(dict(date=idx[j], r=r.iloc[j], L=-r.iloc[j], sigma=s,
                             HS=q_hs, HS_ES=L_hist[L_hist >= q_hs_es].mean(),
                             Normal=-(m + sd * stats.norm.ppf(a)),
                             Normal_ES=-(m - sd * stats.norm.pdf(stats.norm.ppf(a_es)) / a_es),
                             **{'GARCH-t': -(mu + s * t_std_q(nu, a)),
                                'GARCH-t_ES': -(mu + s * t_std_es(nu, a_es))},
                             FHS=-(mu + s * zq), FHS_ES=-(mu + s * zes),
                             # VaR at the ES level (2.5%): the (VaR, ES) pair at the same level, for the FZ0 score
                             HS_V25=q_hs_es, Normal_V25=-(m + sd * stats.norm.ppf(a_es)),
                             **{'GARCH-t_V25': -(mu + s * t_std_q(nu, a_es))}, FHS_V25=-(mu + s * zq_es)))
    return pd.DataFrame(rows).set_index('date')


# -----------------------------------------------------------------------------
# 4. BACKTESTING
# -----------------------------------------------------------------------------
def kupiec(hits, p=ALPHA):
    """Kupiec proportion-of-failures (POF) coverage test: LR_uc ~ chi2(1)."""
    hits = np.asarray(hits, int)
    T, x = len(hits), int(hits.sum())
    ph = x / T
    ll0 = (T - x) * np.log(1 - p) + x * np.log(p)
    ll1 = (T - x) * np.log(1 - ph) + x * np.log(ph) if 0 < x < T else 0.0
    lr = -2 * (ll0 - ll1)
    return dict(T=T, x=x, rate=ph, LR=lr, p=stats.chi2.sf(lr, 1))


def christoffersen(hits, p=ALPHA):
    """Independence test (first-order Markov chain) and the joint test LR_cc = LR_uc + LR_ind."""
    h = np.asarray(hits, int)
    a, b = h[:-1], h[1:]
    n00, n01 = np.sum((a == 0) & (b == 0)), np.sum((a == 0) & (b == 1))
    n10, n11 = np.sum((a == 1) & (b == 0)), np.sum((a == 1) & (b == 1))

    def xlogy(n, q):
        return n * np.log(q) if n > 0 else 0.0
    pi01 = n01 / (n00 + n01)
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    l1 = xlogy(n00, 1 - pi01) + xlogy(n01, pi01) + xlogy(n10, 1 - pi11) + xlogy(n11, pi11)
    l0 = xlogy(n00 + n10, 1 - pi) + xlogy(n01 + n11, pi)
    lr_ind = -2 * (l0 - l1)
    lr_uc = kupiec(h, p)['LR']
    return dict(n11=int(n11), pi01=pi01, pi11=pi11, LR_ind=lr_ind, p_ind=stats.chi2.sf(lr_ind, 1),
                LR_cc=lr_uc + lr_ind, p_cc=stats.chi2.sf(lr_uc + lr_ind, 2))


def traffic_light(x, T=250, p=ALPHA):
    """Basel zone for x breaches in T days: green (<5), yellow (5-9), red (>=10) at T=250, p=1%."""
    cum = stats.binom.cdf(x, T, p)
    return 'green' if cum < 0.95 else ('yellow' if cum < 0.9999 else 'red')


def backtest_table(fc, models=MODELS, a=ALPHA):
    out = {}
    for m in models:
        hits = (fc['L'] > fc[m]).astype(int)
        k, c = kupiec(hits, a), christoffersen(hits, a)
        roll = hits.rolling(250).sum().dropna()
        zones = roll.apply(lambda x: traffic_light(int(x)))
        out[m] = dict(T=k['T'], x=k['x'], rate=k['rate'], LR_uc=k['LR'], p_uc=k['p'],
                      LR_ind=c['LR_ind'], p_ind=c['p_ind'], p_cc=c['p_cc'], n11=c['n11'],
                      share_red=float((zones == 'red').mean()), share_yellow=float((zones == 'yellow').mean()),
                      mean_var=float(fc[m].mean()))
    return out


def binom_band(T, p=ALPHA, level=0.95):
    """Central binomial interval for the breach rate under H0: rate = p."""
    lo, hi = stats.binom.ppf([(1 - level) / 2, 1 - (1 - level) / 2], T, p)
    return lo / T, hi / T

"""
seminar2.py -- Calculele pentru Seminarul 2 (MFM): eficienta pietei
===================================================================
Partea A: exemple pe hartie (VR pas cu pas, testul secventelor, Hurst din VR).
Partea B: VR/Chow-Denning pe piete, DFA rulant, AMH pe Bitcoin cu benzi bootstrap,
          anomalii de calendar cu corectii Bonferroni/Holm, autocorelatia fara zilele de criza.
Partea C: a devenit BVB mai eficienta dupa reclasificarea FTSE din septembrie 2020?
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import MARKETS, LABELS, load_close, log_returns, read_market, complete_months   # noqa: E402
from eff_tests import variance_ratio, chow_denning, runs_test, dfa_hurst, rolling_stat   # noqa: E402

from generate_all_charts import (plt, MainBlue, IDAred, Amber, Forest, Orange, Purple, Gray, LightGray,  # noqa: E402
                                 save_fig, legend_outside_bottom, calendar_table, vr_profile)
from scipy.special import comb   # noqa: E402

Teal = '#17A2B8'

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42

# -----------------------------------------------------------------------------
# PARTEA A
# -----------------------------------------------------------------------------
A_RETURNS = np.array([1.0, -0.5, 0.8, 0.3, -1.2, 0.6, 0.9, -0.4])          # %
A_SIGNS = '++-+++--+-++---+-+++'                                            # 20 days
A4_SIGNS = '+++++-----+++++-----'


def a_vr_by_hand(r=A_RETURNS, q=2):
    """VR(q) without bias corrections: var(overlapping q-day sums) / (q * daily var)."""
    mu = r.mean()
    var1 = ((r - mu) ** 2).mean()
    sums = np.convolve(r, np.ones(q), mode='valid')
    varq = ((sums - q * mu) ** 2).mean()
    e = r - mu
    rho = [(e[j:] * e[:-j]).sum() / (e ** 2).sum() for j in range(1, q)]
    approx = 1 + 2 * sum((1 - j / q) * rho[j - 1] for j in range(1, q))
    return dict(mean=mu, var1=var1, sums=sums, varq=varq, VR=varq / (q * var1), rho=rho, approx=approx)


def a_runs(signs=A_SIGNS):
    n1, n2 = signs.count('+'), signs.count('-')
    n = n1 + n2
    runs = 1 + sum(signs[i] != signs[i - 1] for i in range(1, n))
    mean = 2 * n1 * n2 / n + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n ** 2 * (n - 1))
    z = (runs - mean) / np.sqrt(var)
    return dict(n1=n1, n2=n2, runs=runs, mean=mean, var=var, z=z, p=2 * (1 - stats.norm.cdf(abs(z))))


def h_from_vr(vr, q):
    """For self-similar increments, VR(q) = q^(2H-1), so H = 0.5 + ln VR(q) / (2 ln q)."""
    return 0.5 + np.log(vr) / (2 * np.log(q))


# -----------------------------------------------------------------------------
# PARTEA B
# -----------------------------------------------------------------------------
def b_vr_table(names):
    rows = []
    for k in names:
        r = log_returns(k) if k != 'bettr' else np.log(read_market('BETTR.INDX')['close']).diff().dropna()
        v2, v5, v10, v20 = (variance_ratio(r, q) for q in (2, 5, 10, 20))
        cd = chow_denning(r)
        rows.append(dict(market=LABELS.get(k, 'BET-TR (Romania)'), N=len(r),
                         VR2=v2[0], z2=v2[1], zstar2=v2[2], VR5=v5[0], z5=v5[1], zstar5=v5[2],
                         VR10=v10[0], z10=v10[1], zstar10=v10[2],
                         VR20=v20[0], z20=v20[1], zstar20=v20[2], CD=cd[0], CD_p=cd[1]))
    return pd.DataFrame(rows).set_index('market')


def b_rolling_dfa(k='sp500', window=500, step=21, n_boot=199, seed=SEED):
    """Rolling DFA; wild-bootstrap null band (Rademacher signs) computed for EACH window:
    keeps the window's volatility (allowed under RW3) and destroys the autocorrelation of returns.
    For comparison: the i.i.d. Student-t4 band (the same for all windows)."""
    rng = np.random.default_rng(seed)
    null = [dfa_hurst(rng.standard_t(4, window))[0] for _ in range(300)]
    lo_t, hi_t = np.percentile(null, [2.5, 97.5])
    r = log_returns(k)
    x = r.values
    rows = []
    for end in range(window, len(x) + 1, step):
        e = x[end - window:end] - x[end - window:end].mean()
        g = np.random.default_rng(seed + end)
        sims = [dfa_hurst(e * g.choice([-1.0, 1.0], window))[0] for _ in range(n_boot)]
        lo, hi = np.percentile(sims, [2.5, 97.5])
        rows.append((r.index[end - 1], dfa_hurst(e)[0], lo, hi))
    d = pd.DataFrame(rows, columns=['date', 'dfa', 'lo', 'hi']).set_index('date')
    d.to_csv(os.path.join(HERE, 'ch2_sem_rolling_dfa.csv'))
    h = d['dfa']
    return dict(lo_t=lo_t, hi_t=hi_t, share_t=float(((h < lo_t) | (h > hi_t)).mean()),
                share_out=float(((h < d['lo']) | (h > d['hi'])).mean()), n=len(d),
                band_lo_mean=float(d['lo'].mean()), band_hi_mean=float(d['hi'].mean()),
                width_min=float((d['hi'] - d['lo']).min()), width_max=float((d['hi'] - d['lo']).max()),
                argwide=(d['hi'] - d['lo']).idxmax().date(), min=h.min(), max=h.max(),
                argmin=h.idxmin().date(), argmax=h.idxmax().date(), mean=h.mean())


def wild_bootstrap_vr_band(x, q=5, n_boot=999, seed=SEED, sims=False):
    """95% band for z*(q) under a heteroskedastic random walk: Rademacher signs.
    sims=True also returns the n_boot simulated statistics."""
    rng = np.random.default_rng(seed)
    e = x - x.mean()
    zs = np.array([variance_ratio(e * rng.choice([-1, 1], len(e)), q)[2] for _ in range(n_boot)])
    band = np.percentile(zs, [2.5, 97.5])
    return (band, zs) if sims else band


def b_amh_bitcoin(window=365, step=30, q=5, n_boot=999, seed=SEED):
    """z*(q) on one-year windows (Bitcoin from 1 Jan 2011 to 18 Sep 2026); wild-bootstrap band
    with n_boot replications in each window (999: the 2.5% and 97.5% quantiles are stable)."""
    r = log_returns('btc', start='2011-01-01')
    rows = []
    x = r.values
    for end in range(window, len(x) + 1, step):
        w = x[end - window:end]
        z = variance_ratio(w, q)[2]
        lo, hi = wild_bootstrap_vr_band(w, q, n_boot, seed + end)
        rows.append((r.index[end - 1], z, lo, hi, end))
    d = pd.DataFrame(rows, columns=['date', 'zstar', 'lo', 'hi', 'end']).set_index('date')
    d['reject'] = (d['zstar'] < d['lo']) | (d['zstar'] > d['hi'])
    return d


def b_tom_ols_hac(k='sp500'):
    """Turn-of-the-month effect: the same regression with classical OLS errors and with HAC errors (Newey-West, 5 lags)."""
    r = complete_months(log_returns(k)) * 1e4
    d = pd.DataFrame({'r': r})
    ym = d.index.to_period('M')
    rank = d.groupby(ym).cumcount()
    rank_end = d.groupby(ym).cumcount(ascending=False)
    d['tom'] = ((rank < 3) | (rank_end == 0)).astype(float)
    X = sm.add_constant(d['tom'])
    ols = sm.OLS(d['r'], X).fit()
    hac = sm.OLS(d['r'], X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    return dict(N=len(d), share_tom=float(d['tom'].mean()), const=float(ols.params['const']),
                beta=float(ols.params['tom']), se_ols=float(ols.bse['tom']), t_ols=float(ols.tvalues['tom']),
                se_hac=float(hac.bse['tom']), t_hac=float(hac.tvalues['tom']), p_hac=float(hac.pvalues['tom']),
                mean_tom=float(d.loc[d['tom'] == 1, 'r'].mean()), mean_other=float(d.loc[d['tom'] == 0, 'r'].mean()))


def b_calendar_multiple(t):
    """5 markets x 3 effects (day of the week, January, turn of the month) from calendar_table(); Bonferroni and Holm."""
    rows = []
    for m, row in t.iterrows():
        rows.append((m, 'day of week (equal means)', row['dow_equal_p']))
        rows.append((m, 'January', 2 * (1 - stats.norm.cdf(abs(row['jan_t'])))))
        rows.append((m, 'turn of month', row['tom_p']))
    d = pd.DataFrame(rows, columns=['market', 'effect', 'p'])
    m = len(d)
    d['bonferroni_reject'] = d['p'] < 0.05 / m
    order = d['p'].sort_values().index
    holm = pd.Series(False, index=d.index)
    for i, ix in enumerate(order):
        if d.loc[ix, 'p'] < 0.05 / (m - i):
            holm[ix] = True
        else:
            break
    d['holm_reject'] = holm
    d['raw_reject'] = d['p'] < 0.05
    return d


def _segment_stats(x, keep, q=5):
    """rho1, tau1 and the Lo-MacKinlay z*(q) computed ONLY within the contiguous retained segments:
    pairs (t, t-k) and q-day sums that cross a removed period are not used.
    With keep = True everywhere, the result equals variance_ratio(x, q)."""
    x = np.asarray(x, dtype=float)
    keep = np.asarray(keep, dtype=bool)
    T = keep.sum()
    mu = x[keep].mean()
    e = np.where(keep, x - mu, 0.0)
    s2 = (e ** 2).sum()

    def pair(k):                          # both ends retained and every day between them retained
        ok = np.convolve(keep.astype(int), np.ones(k + 1, dtype=int), mode='valid') == k + 1
        return ok, e[k:] * ok, e[:-k] * ok
    ok1, a1, b1 = pair(1)
    rho1 = (a1 * b1).sum() / s2
    tau1 = (a1 ** 2 * b1 ** 2).sum() / s2 ** 2
    okq = np.convolve(keep.astype(int), np.ones(q, dtype=int), mode='valid') == q
    agg = (np.convolve(np.where(keep, x, 0.0), np.ones(q), mode='valid') - q * mu)[okq]
    m = q * len(agg) * (1 - q / T)
    vr = ((agg ** 2).sum() / m) / (s2 / (T - 1))
    theta = 0.0
    for j in range(1, q):
        _, a, b = pair(j)
        theta += (2 * (q - j) / q) ** 2 * T * (a ** 2 * b ** 2).sum() / s2 ** 2
    return dict(N=int(T), rho1=rho1, t_iid=rho1 * np.sqrt(T), t_robust=rho1 / np.sqrt(tau1),
                zstar5=np.sqrt(T) * (vr - 1) / np.sqrt(theta), n_pairs=int(ok1.sum()), n_windows=int(okq.sum()))


def b_crisis_robustness():
    """S&P 500 autocorrelation with and without 2008-2009 and 2020; without the crises, the statistics are computed only
    within the remaining contiguous segments (no pair of days and no 5-day sum crosses a removed crisis)."""
    r = log_returns('sp500')
    mask = ~(((r.index >= '2008-09-01') & (r.index <= '2009-06-30')) |
             ((r.index >= '2020-02-15') & (r.index <= '2020-06-30')))
    out = {'all days': _segment_stats(r.values, np.ones(len(r), bool)),
           'without 2008-09 and 2020 crises': _segment_stats(r.values, mask)}
    return pd.DataFrame(out).T


def b_bet_common_period():
    """BET vs BET-TR on the common period (from the start of BET-TR): separates the sample effect from the dividend effect."""
    tr = np.log(read_market('BETTR.INDX')['close']).diff().dropna()
    b = log_returns('bet')
    out = {}
    for lab, r in [('BET, full sample', b), ('BET, BET-TR period', b.loc[tr.index[0]:tr.index[-1]]),
                   ('BET-TR', tr)]:
        v2 = variance_ratio(r, 2)
        cd = chow_denning(r)
        out[lab] = dict(start=str(r.index[0].date()), N=len(r), rho1=r.autocorr(1), VR2=v2[0], z2=v2[1],
                        zstar2=v2[2], zstar5=variance_ratio(r, 5)[2], CD=cd[0], CD_p=cd[1])
    return out


# -----------------------------------------------------------------------------
# PARTEA C
# -----------------------------------------------------------------------------
def rho1_robust(x):
    """rho1 and its robust standard error sqrt(tau1)."""
    x = np.asarray(x, dtype=float)
    e = x - x.mean()
    s2 = (e ** 2).sum()
    return (e[1:] * e[:-1]).sum() / s2, np.sqrt((e[1:] ** 2 * e[:-1] ** 2).sum() / s2 ** 2)


def c_bvb_before_after(split='2020-09-21', years=5, n_boot=999, block=20, seed=SEED, k='bet'):
    """rho1 and z*(5) over the 5 years before and after the upgrade; moving-block bootstrap, independent in each
    period, for the difference rho1(after) - rho1(before). k = 'bet' (treated), 'wig20' or 'bux' (comparison)."""
    r = log_returns(k)
    s = pd.Timestamp(split)
    before = r.loc[s - pd.DateOffset(years=years):s - pd.Timedelta(days=1)]
    after = r.loc[s:s + pd.DateOffset(years=years)]
    rng = np.random.default_rng(seed)

    def block_boot(x):
        n = len(x)
        starts = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
        return np.concatenate([x[s0:s0 + block] for s0 in starts])[:n]

    def rho1(x):
        return np.corrcoef(x[1:], x[:-1])[0, 1]

    diffs = [rho1(block_boot(after.values)) - rho1(block_boot(before.values)) for _ in range(n_boot)]
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return dict(before=(before.index[0].date(), before.index[-1].date(), len(before), rho1(before.values),
                        variance_ratio(before, 5)[2]),
                after=(after.index[0].date(), after.index[-1].date(), len(after), rho1(after.values),
                       variance_ratio(after, 5)[2]),
                diff=rho1(after.values) - rho1(before.values), ci=(lo, hi),
                se_before=rho1_robust(before.values)[1], se_after=rho1_robust(after.values)[1])


# -----------------------------------------------------------------------------
# CALCULE SUPLIMENTARE PENTRU GRAFICELE SEMINARULUI
# -----------------------------------------------------------------------------
def a2_null(T=1000, n_sim=2000, seed=SEED):
    """Simulated z(2) and z*(2): i.i.d. N(0,1) returns and GARCH(1,1) returns (volatility clustering, RW3 true)."""
    rng = np.random.default_rng(seed)
    z_iid, z_g, zs_g = [], [], []
    for _ in range(n_sim):
        z_iid.append(variance_ratio(rng.standard_normal(T), 2)[1])
        eps = rng.standard_normal(T + 200)
        h, x = 1.0, np.empty(T + 200)
        for t in range(T + 200):                       # h_t = 0.02 + 0.10 x_{t-1}^2 + 0.88 h_{t-1}
            x[t] = np.sqrt(h) * eps[t]
            h = 0.02 + 0.10 * x[t] ** 2 + 0.88 * h
        _, z, zs = variance_ratio(x[200:], 2)
        z_g.append(z)
        zs_g.append(zs)
    z_iid, z_g, zs_g = map(np.array, (z_iid, z_g, zs_g))
    share = lambda z: float((np.abs(z) > 1.96).mean())
    return dict(T=T, n_sim=n_sim, z_iid=z_iid, z_garch=z_g, zstar_garch=zs_g,
                rej_iid=share(z_iid), rej_garch=share(z_g), rej_star_garch=share(zs_g))


def a3_exact(n1=12, n2=8, runs=11):
    """Exact distribution of the number of runs given n1 and n2 (Wald and Wolfowitz, 1940)."""
    n = n1 + n2
    tot = comb(n, n1)
    pmf = {}
    for r in range(2, n + 1):
        k = r // 2
        if r % 2 == 0:
            pr = 2 * comb(n1 - 1, k - 1) * comb(n2 - 1, k - 1) / tot
        else:
            pr = (comb(n1 - 1, k - 1) * comb(n2 - 1, k) + comb(n1 - 1, k) * comb(n2 - 1, k - 1)) / tot
        if pr > 0:
            pmf[r] = float(pr)
    lo = sum(v for r, v in pmf.items() if r <= runs)
    hi = sum(v for r, v in pmf.items() if r >= runs)
    return dict(pmf=pmf, p_le=lo, p_ge=hi, p_exact=min(1.0, 2 * min(lo, hi)))


def a4_sim(rho=0.98, T=60, corr=-0.9, su=0.17, sv=0.14, n_sim=10000, seed=SEED):
    """Sampling distribution of the predictive slope under beta = 0 (the A4 system, illustrative annual data)."""
    rng = np.random.default_rng(seed)
    b, t = np.empty(n_sim), np.empty(n_sim)
    sx = sv / np.sqrt(1 - rho ** 2)
    for i in range(n_sim):
        z1, z2 = rng.standard_normal((2, T))
        v = sv * z1
        u = su * (corr * z1 + np.sqrt(1 - corr ** 2) * z2)
        x = np.empty(T + 1)
        x[0] = sx * rng.standard_normal()
        for j in range(T):
            x[j + 1] = rho * x[j] + v[j]
        X = np.column_stack([np.ones(T), x[:-1]])
        coef, res, *_ = np.linalg.lstsq(X, u, rcond=None)
        s2 = ((u - X @ coef) ** 2).sum() / (T - 2)
        se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
        b[i], t[i] = coef[1], coef[1] / se
    return dict(beta=b, t=t, mean=float(b.mean()), median=float(np.median(b)),
                rej=float((np.abs(t) > 1.96).mean()), rej_up=float((t > 1.645).mean()))


def ar1_vr(rho, q):
    """VR(q) of an AR(1) with rho_k = rho^k."""
    k = np.arange(1, q)
    return 1 + 2 * np.sum((1 - k / q) * rho ** k)


def b1_worked(k='sp500', q=2):
    """Step-by-step computation of VR(q), z(q) and z*(q) (Lo and MacKinlay, 1988), returns in %."""
    x = log_returns(k).values * 100
    T = len(x)
    mu = x.mean()
    e = x - mu
    var_a = (e ** 2).sum() / (T - 1)
    agg = np.convolve(x, np.ones(q), mode='valid') - q * mu
    m = q * (T - q + 1) * (1 - q / T)
    var_c = (agg ** 2).sum() / m
    vr = var_c / var_a
    den = (e ** 2).sum() ** 2
    deltas = [T * (e[j:] ** 2 * e[:-j] ** 2).sum() / den for j in range(1, q)]
    theta = sum((2 * (q - j) / q) ** 2 * deltas[j - 1] for j in range(1, q))
    zstar = np.sqrt(T) * (vr - 1) / np.sqrt(theta)
    z = (vr - 1) / np.sqrt(2 * (2 * q - 1) * (q - 1) / (3 * q * T))
    return dict(T=T, mu=mu, var_a=var_a, m=m, var_c=var_c, VR=vr, delta1=deltas[0], theta=theta,
                z=z, zstar=zstar, p=2 * (1 - stats.norm.cdf(abs(zstar))), n_sums=len(agg))


def b3_window(k='sp500', window=500, box=50):
    """DFA on a single window (the last `window` returns): profile, segment trends, log F(n) on log n."""
    r = log_returns(k)
    w = r.iloc[-window:]
    x = w.values
    y = np.cumsum(x - x.mean())
    slope, tab = dfa_hurst(x)
    fit = np.polyfit(np.log(tab['n']), np.log(tab['F']), 1)
    return dict(start=w.index[0].date(), end=w.index[-1].date(), T=len(x), slope=slope,
                sizes=tab['n'].tolist(), F=tab['F'].tolist(), icpt=float(fit[1]), y=y, box=box, index=w.index,
                n_sizes=len(tab), n_min=int(tab['n'].min()), n_max=int(tab['n'].max()))


def b5_strip(k='sp500', month_end='2026-07'):
    """Trading days around a month change, with the TOM indicator and the return in bp."""
    r = complete_months(log_returns(k)) * 1e4
    d = pd.DataFrame({'r': r})
    ym = d.index.to_period('M')
    rank = d.groupby(ym).cumcount()
    rank_end = d.groupby(ym).cumcount(ascending=False)
    d['tom'] = ((rank < 3) | (rank_end == 0)).astype(int)
    p = pd.Period(month_end, 'M')
    sel = pd.concat([d[ym == p].iloc[-5:], d[ym == p + 1].iloc[:5]])
    return sel


def b9_event_path(event='2018-12-19', est=(-250, -11), days=(-10, 5)):
    """Daily abnormal returns, prediction standard errors and CAR for TLV, BRD and the equally weighted portfolio."""
    px = pd.concat({'TLV': read_market('TLV.RO')['adjusted_close'], 'BRD': read_market('BRD.RO')['adjusted_close'],
                    'BET': read_market('BET')['close']}, axis=1).dropna()        # align prices on common trading days
    px = px[px.index.dayofweek < 5]
    r = np.log(px).diff().dropna()
    t0 = r.index.get_loc(pd.Timestamp(event))
    E = r.iloc[t0 + est[0]:t0 + est[1] + 1]
    W = r.iloc[t0 + days[0]:t0 + days[1] + 1]
    mu_m, var_m, T0 = E['BET'].mean(), E['BET'].var(ddof=1), len(E)
    out = {}
    for k in ['TLV', 'BRD', 'PORT']:
        yE = E[['TLV', 'BRD']].mean(axis=1) if k == 'PORT' else E[k]
        yW = W[['TLV', 'BRD']].mean(axis=1) if k == 'PORT' else W[k]
        f = sm.OLS(yE, sm.add_constant(E['BET'])).fit()
        ar = yW - f.params['const'] - f.params['BET'] * W['BET']
        se = np.sqrt(f.mse_resid * (1 + 1 / T0 + (W['BET'] - mu_m) ** 2 / ((T0 - 1) * var_m)))
        out[k] = pd.DataFrame({'day': np.arange(days[0], days[1] + 1), 'AR': ar.values, 'se': se.values},
                              index=W.index)
    return out


def c1_rolling(keys=('bet', 'wig20', 'bux'), window=250, start='2014-01-01'):
    """rho1 on rolling windows of `window` days, with its robust standard error."""
    out = {}
    for k in keys:
        x = log_returns(k, start=start)
        vals = [rho1_robust(x.values[i - window:i]) for i in range(window, len(x) + 1)]
        out[k] = pd.DataFrame(vals, columns=['rho1', 'se'], index=x.index[window - 1:])
    return out


# -----------------------------------------------------------------------------
# GRAFICE PENTRU SEMINAR
# -----------------------------------------------------------------------------
CRISES = [('2008-09-01', '2009-06-30'), ('2020-02-15', '2020-06-30')]


def fig_b2(t2, b1, b2c):
    """B2: classical z(2) vs robust z*(2) across markets and the Chow-Denning p-value (joint test over q = 2, 5, 10, 20)."""
    rows = [(LABELS['bet'].split(' (')[0] + ', 2000-2026', b1.loc[LABELS['bet'], 'z2'], b1.loc[LABELS['bet'], 'zstar2'],
             b1.loc[LABELS['bet'], 'CD_p']),
            ('BET, BET-TR period', b2c['BET, BET-TR period']['z2'], b2c['BET, BET-TR period']['zstar2'],
             b2c['BET, BET-TR period']['CD_p'])]
    rows += [(m.split(' (')[0], r['z2'], r['zstar2'], r['CD_p']) for m, r in t2.iterrows()]
    d = pd.DataFrame(rows, columns=['m', 'z2', 'zs2', 'cdp']).iloc[::-1]
    y = np.arange(len(d))
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.4), sharey=True)
    ax = axes[0]
    ax.barh(y + 0.2, d['z2'], 0.38, color=MainBlue, alpha=0.4, label='Classical z(2), RW1')
    ax.barh(y - 0.2, d['zs2'], 0.38, color=MainBlue, label='Robust z*(2), RW3')
    for v in (-1.96, 1.96):
        ax.axvline(v, color=Gray, ls='--', lw=0.7)
    ax.axvline(0, color=Gray, lw=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(d['m'], fontsize=7.5)
    ax.set_title('One horizon, q = 2 (dashed: 1.96)', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    ax = axes[1]
    ax.barh(y, d['cdp'], 0.5, color=[IDAred if p < 0.05 else Forest for p in d['cdp']])
    ax.axvline(0.05, color=Purple, ls='--', lw=1.0)
    ax.set_xscale('log')
    ax.set_xlabel('Chow-Denning p-value (log scale)')
    ax.set_title('Joint test over q = 2, 5, 10, 20', fontsize=8.5, loc='left')
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=IDAred, label='p < 0.05'),
                       plt.Rectangle((0, 0), 1, 1, color=Forest, label='p >= 0.05'),
                       plt.Line2D([], [], color=Purple, ls='--', label='5%')],
              loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_b2')


def setup_check():
    """Data check: the first S&P 500 closes and returns and the number of returns."""
    p = load_close('sp500')
    r = np.log(p).diff()
    rows = [dict(date=i.date(), close=float(p.loc[i]), r=float(r.loc[i]) if i != p.index[0] else None)
            for i in p.index[:4]]
    return dict(rows=rows, N_sp=int(r.notna().sum()), N_bet=len(log_returns('bet')), first=p.index[0].date(),
                last=p.index[-1].date())


def fig_sem_data():
    """Prices (log scale) and daily log returns for the S&P 500 and BET, 2000 -- 18 Sep 2026."""
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 3.6), sharex=True)
    for j, (k, c) in enumerate([('sp500', MainBlue), ('bet', IDAred)]):
        p = load_close(k)
        r = np.log(p).diff().dropna() * 100
        axes[0, j].plot(p.index, p.values, color=c, lw=0.9)
        axes[0, j].set_yscale('log')
        axes[0, j].set_title(f'{LABELS[k]}: close (log scale)', fontsize=8.5, loc='left', color=c)
        axes[1, j].plot(r.index, r.values, color=c, lw=0.4)
        axes[1, j].set_title('Daily log return (%)', fontsize=8.5, loc='left', color=c)
        for a, b in CRISES:
            for i in range(2):
                axes[i, j].axvspan(pd.Timestamp(a), pd.Timestamp(b), color=Amber, alpha=0.25, lw=0)
    h = [plt.Line2D([], [], color=MainBlue, lw=1.2, label='S&P 500 (US)'),
         plt.Line2D([], [], color=IDAred, lw=1.2, label='BET (Romania)'),
         plt.Rectangle((0, 0), 1, 1, color=Amber, alpha=0.25, label='Sep 2008 - Jun 2009 and Feb - Jun 2020')]
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_data')


def fig_a1(a1):
    """A1: the eight returns and the overlapping two-day sums."""
    r = A_RETURNS
    t = np.arange(1, len(r) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.8))
    ax = axes[0]
    ax.bar(t, r, color=[Forest if v > 0 else IDAred for v in r], width=0.55)
    ax.axhline(a1['mean'], color=MainBlue, ls='--', lw=0.9, label=r'Mean $\hat\mu$ = %.4f' % a1['mean'])
    ax.axhline(0, color=Gray, lw=0.5)
    for i, v in zip(t, r):
        ax.text(i, v + (0.06 if v > 0 else -0.06), f'{v:+.1f}', ha='center', va='bottom' if v > 0 else 'top',
                fontsize=7.5, color='black')
    ax.set_ylim(-1.7, 1.4)
    ax.set_xticks(t)
    ax.set_xlabel('Day t')
    ax.set_ylabel('Return (%)')
    ax.set_title('Eight daily returns', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.3)
    ax = axes[1]
    s2 = a1['sums']
    ts = np.arange(2, len(r) + 1)
    ax.bar(ts, s2, color=Purple, width=0.55, label=r'$s_t = r_{t-1} + r_t$')
    ax.axhline(2 * a1['mean'], color=MainBlue, ls='--', lw=0.9, label=r'$2\hat\mu$ = %.3f' % (2 * a1['mean']))
    ax.axhline(0, color=Gray, lw=0.5)
    for i, v in zip(ts, s2):
        ax.text(i, v + (0.06 if v > 0 else -0.06), f'{v:+.1f}', ha='center', va='bottom' if v > 0 else 'top',
                fontsize=7.5, color='black')
    ax.set_ylim(-1.4, 1.9)
    ax.set_xticks(ts)
    ax.set_xticklabels([f'{i - 1}+{i}' for i in ts])
    ax.set_xlabel('Days summed')
    ax.set_title(r'Seven overlapping two-day sums: $\widehat{VR}(2)$ = %.3f' % a1['VR'], fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.3)
    plt.tight_layout()
    save_fig('ch2_sem_a1')


def fig_a2(sim):
    """A2: the covariance pairs for q = 3 and the distribution of z(2) under i.i.d. and under GARCH."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.0), gridspec_kw={'width_ratios': [1, 2.3]})
    ax = axes[0]
    col = {0: MainBlue, 1: Forest, 2: Amber}
    for i in range(3):
        for j in range(3):
            lag = abs(i - j)
            ax.add_patch(plt.Rectangle((j, 2 - i), 0.95, 0.95, color=col[lag], alpha=0.85))
            ax.text(j + 0.47, 2 - i + 0.47, rf'$\gamma_{lag}$', ha='center', va='center', color='white', fontsize=11)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.set_xticks([0.47, 1.47, 2.47])
    ax.set_xticklabels([r'$r_t$', r'$r_{t-1}$', r'$r_{t-2}$'])
    ax.set_yticks([0.47, 1.47, 2.47])
    ax.set_yticklabels([r'$r_{t-2}$', r'$r_{t-1}$', r'$r_t$'])
    ax.set_title(r'Var$(r_t + r_{t-1} + r_{t-2})$: 3 $\gamma_0$ + 4 $\gamma_1$ + 2 $\gamma_2$', fontsize=8.5, loc='left')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax = axes[1]
    bins = np.linspace(-6, 6, 61)
    ax.hist(sim['z_iid'], bins=bins, density=True, color=MainBlue, alpha=0.55,
            label=f"z(2), i.i.d. returns: |z| > 1.96 in {100 * sim['rej_iid']:.1f}%")
    ax.hist(sim['z_garch'], bins=bins, density=True, histtype='step', color=IDAred, lw=1.4,
            label=f"z(2), GARCH returns: {100 * sim['rej_garch']:.1f}%")
    ax.hist(sim['zstar_garch'], bins=bins, density=True, histtype='step', color=Forest, lw=1.4,
            label=f"z*(2), GARCH returns: {100 * sim['rej_star_garch']:.1f}%")
    g = np.linspace(-6, 6, 300)
    ax.plot(g, stats.norm.pdf(g), color='black', lw=1.0, label='N(0,1) density')
    for v in (-1.96, 1.96):
        ax.axvline(v, color=Gray, ls='--', lw=0.7)
    ax.set_xlabel('Statistic')
    ax.set_title(f"Null distributions, T = {sim['T']}, {sim['n_sim']} simulations", fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    plt.tight_layout()
    save_fig('ch2_sem_a2')


def fig_a3(a3, ex):
    """A3: the numbered signs with the run boundaries and the exact distribution of the number of runs."""
    fig, axes = plt.subplots(2, 1, figsize=(8.6, 3.4), gridspec_kw={'height_ratios': [1, 2.2]})
    ax = axes[0]
    run = 1
    for i, c in enumerate(A_SIGNS):
        if i > 0 and c != A_SIGNS[i - 1]:
            run += 1
            ax.axvline(i - 0.5, color='black', lw=1.2)
        ax.add_patch(plt.Rectangle((i - 0.45, 0), 0.9, 1, color=Forest if c == '+' else IDAred, alpha=0.85))
        ax.text(i, 0.5, '+' if c == '+' else '−', ha='center', va='center', color='white', fontsize=12)
        ax.text(i, -0.35, str(i + 1), ha='center', va='center', fontsize=7, color='black')
    ax.set_xlim(-0.6, len(A_SIGNS) - 0.4)
    ax.set_ylim(-0.6, 1.1)
    ax.axis('off')
    ax.set_title(f"Signs of 20 returns: n1 = {ex['n1']} plus, n2 = {ex['n2']} minus, R = {ex['runs']} runs "
                 "(black lines: run boundaries)", fontsize=8.5, loc='left')
    ax = axes[1]
    rr = np.array(list(a3['pmf'].keys()))
    pp = np.array(list(a3['pmf'].values()))
    ax.bar(rr, pp, color=[IDAred if v == ex['runs'] else MainBlue for v in rr], width=0.7,
           label='Exact P(R = r | n1, n2)')
    g = np.linspace(rr.min(), rr.max(), 200)
    ax.plot(g, stats.norm.pdf(g, ex['mean'], np.sqrt(ex['var'])), color=Amber, lw=1.3,
            label=f"Normal approximation, mean {ex['mean']:.1f}, SD {np.sqrt(ex['var']):.2f}")
    ax.set_xlabel('Number of runs R')
    ax.set_ylabel('Probability')
    ax.set_xticks(rr)
    hs, ls = ax.get_legend_handles_labels()
    hs.append(plt.Rectangle((0, 0), 1, 1, color=IDAred))
    ls.append(f"Observed R = {ex['runs']}: exact P(R >= {ex['runs']}) = {a3['p_ge']:.3f}")
    ax.legend(hs, ls, loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_a3')


def fig_a4(sim, bias):
    """A4: distribution of the OLS slope under beta = 0, T = 60, rho = 0.98, corr(u, v) = -0.9."""
    fig, ax = plt.subplots(figsize=(8.6, 2.9))
    ax.hist(sim['beta'], bins=80, density=True, color=MainBlue, alpha=0.6, label=r'Simulated $\hat\beta$ (10,000 samples)')
    ax.axvline(0, color='black', lw=1.0, label=r'True $\beta = 0$')
    ax.axvline(sim['mean'], color=IDAred, lw=1.4, label=r'Monte Carlo mean of $\hat\beta$ = %.3f' % sim['mean'])
    ax.axvline(bias, color=Forest, ls='--', lw=1.4, label=r'Approximate bias $-\phi(1 + 3\rho)/T$ = %.3f' % bias)
    ax.set_xlabel(r'Estimated predictive slope $\hat\beta$')
    ax.set_title(r'Nominal 5%% $t$-test under $\beta = 0$ rejects in %.1f%% of samples (one-sided, $\beta > 0$: %.1f%%)'
                 % (100 * sim['rej'], 100 * sim['rej_up']), fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch2_sem_a4')


def fig_a56(rho_pos, rho_neg, h_bet, h_sp, qmax=500):
    """A5-A6: VR(q) and the implied H(q) for two AR(1) processes (short memory) and the empirical values at q = 20."""
    q = np.unique(np.logspace(np.log10(2), np.log10(qmax), 80).astype(int))
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.0))
    for rho, c, lab in [(rho_pos, IDAred, r'AR(1), $\rho_1$ = %.3f (BET)' % rho_pos),
                        (rho_neg, MainBlue, r'AR(1), $\rho_1$ = %.1f' % rho_neg)]:
        vr = np.array([ar1_vr(rho, k) for k in q])
        axes[0].plot(q, vr, color=c, lw=1.3, label=lab)
        axes[1].plot(q, 0.5 + np.log(vr) / (2 * np.log(q)), color=c, lw=1.3, label=lab)
        axes[0].axhline((1 + rho) / (1 - rho), color=c, ls=':', lw=0.8)
    axes[1].scatter([20], [h_bet], color=IDAred, marker='D', s=30, zorder=3, label='BET, implied H(20) = %.3f' % h_bet)
    axes[1].scatter([20], [h_sp], color=MainBlue, marker='D', s=30, zorder=3,
                    label='S&P 500, implied H(20) = %.3f' % h_sp)
    for ax in axes:
        ax.set_xscale('log')
        ax.set_xlabel('Horizon q (days, log scale)')
    axes[0].axhline(1, color=Gray, lw=0.6)
    axes[1].axhline(0.5, color=Gray, lw=0.6)
    axes[0].set_title(r'VR(q): dotted line = limit $(1+\rho_1)/(1-\rho_1)$', fontsize=8.5, loc='left')
    axes[1].set_title('Implied H(q) = 0.5 + ln VR(q) / (2 ln q) tends to 0.5', fontsize=8.5, loc='left')
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_a56')


def fig_b1(t):
    """B1: the VR(q) profile with the robust band and classical z(q) vs robust z*(q), S&P 500 and BET."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.1))
    ax = axes[0]
    for k, c in [('sp500', MainBlue), ('bet', IDAred)]:
        vp = vr_profile(log_returns(k))
        ax.fill_between(vp.index, 1 - vp['band'], 1 + vp['band'], color=c, alpha=0.12, lw=0)
        ax.plot(vp.index, vp['VR'], color=c, lw=1.3, label=LABELS[k])
    ax.axhline(1, color=Gray, lw=0.6)
    ax.set_xlabel('Horizon q (days)')
    ax.set_ylabel(r'$\widehat{VR}(q)$')
    ax.set_title('VR(q) with robust 95% bands around 1 (shaded)', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    ax = axes[1]
    qs = [2, 5, 10, 20]
    xpos = np.arange(len(qs))
    w = 0.2
    for i, (m, c) in enumerate([(LABELS['sp500'], MainBlue), (LABELS['bet'], IDAred)]):
        z = [t.loc[m, f'z{q}'] for q in qs]
        zs = [t.loc[m, f'zstar{q}'] for q in qs]
        ax.bar(xpos + (2 * i - 1.5) * w, z, w, color=c, alpha=0.35, label=f"{m.split(' (')[0]}: classical z(q)")
        ax.bar(xpos + (2 * i - 0.5) * w, zs, w, color=c, label=f"{m.split(' (')[0]}: robust z*(q)")
    for v in (-1.96, 1.96):
        ax.axhline(v, color=Gray, ls='--', lw=0.7)
    for v in (-2.49, 2.49):
        ax.axhline(v, color=Purple, ls=':', lw=1.0)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(xpos)
    ax.set_xticklabels([f'q = {q}' for q in qs])
    ax.set_title('Dashed: single-test 5% value 1.96; dotted: Chow-Denning 2.49', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    plt.tight_layout()
    save_fig('ch2_sem_b1')


def fig_b3_window(w):
    """B3: DFA on a 500-day window: the profile with the segment trends and the line log F(n) on log n."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.0))
    ax = axes[0]
    y, n = w['y'], w['box']
    t = np.arange(len(y))
    ax.plot(w['index'], y, color=MainBlue, lw=0.9, label=r'Profile $y_k = \sum_{i \leq k} (r_i - \bar r)$')
    for b in range(len(y) // n):
        seg = slice(b * n, (b + 1) * n)
        c = np.polyfit(t[seg], y[seg], 1)
        ax.plot(w['index'][seg], np.polyval(c, t[seg]), color=IDAred, lw=1.2,
                label=f'Linear trend in each box of n = {n} days' if b == 0 else None)
        ax.axvline(w['index'][b * n], color=Gray, lw=0.4, ls=':')
    ax.set_title(f"S&P 500, {w['start']} to {w['end']} ({w['T']} returns)", fontsize=8.5, loc='left')
    ax.tick_params(axis='x', labelsize=7)
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    ax = axes[1]
    ln, lf = np.log(w['sizes']), np.log(w['F'])
    ax.scatter(ln, lf, color=MainBlue, s=18, zorder=3, label=f"log F(n), {w['n_sizes']} box sizes from {w['n_min']} to {w['n_max']}")
    ax.plot(ln, w['icpt'] + w['slope'] * ln, color=IDAred, lw=1.2, label=r'OLS slope $\hat\alpha_{DFA}$ = %.3f' % w['slope'])
    ax.plot(ln, w['icpt'] + 0.5 * (ln - ln[0]) + w['slope'] * ln[0], color=Forest, ls='--', lw=1.0,
            label='Slope 0.5 (no memory), same start')
    ax.set_xlabel('log n (box length)')
    ax.set_ylabel('log F(n)')
    ax.set_title('Fluctuation function and its slope', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch2_sem_b3_window')


def fig_b3_rolling(d, lo_t, hi_t):
    """B3: rolling DFA exponent of the S&P 500, with the per-window wild-bootstrap band and the fixed t4 band."""
    fig, ax = plt.subplots(figsize=(8.6, 3.0))
    ax.fill_between(d.index, d['lo'], d['hi'], color=LightGray, alpha=0.9, lw=0,
                    label='Sign-flip 95% band, recomputed in each window (199 draws)')
    ax.plot(d.index, d['dfa'], color=MainBlue, lw=1.1, label=r'S&P 500 $\hat\alpha_{DFA}$, 500-day windows, step 21')
    ax.axhline(lo_t, color=Purple, ls='--', lw=1.0, label=f'Fixed i.i.d. Student-t4 band [{lo_t:.3f}, {hi_t:.3f}]')
    ax.axhline(hi_t, color=Purple, ls='--', lw=1.0)
    ax.axhline(0.5, color=Gray, lw=0.6)
    out = d[(d['dfa'] < d['lo']) | (d['dfa'] > d['hi'])]
    ax.scatter(out.index, out['dfa'], color=IDAred, s=16, zorder=3, label='Outside its own band')
    ax.set_ylabel(r'$\hat\alpha_{DFA}$')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    plt.tight_layout()
    save_fig('ch2_sem_b3_rolling')


def fig_amh_btc(d, sims=None, z0=None, date0=None):
    """B4: Bitcoin z*(5) on 365-day windows, the per-window wild-bootstrap band and +-1.96;
    right panel: the bootstrap distribution in one flagged window."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.1), gridspec_kw={'width_ratios': [2.6, 1]})
    ax = axes[0]
    ax.fill_between(d.index, d['lo'], d['hi'], color=LightGray, alpha=0.9, lw=0,
                    label='Sign-flip 95% band per window (999 draws)')
    ax.plot(d.index, d['zstar'], color=Amber, lw=1.1, label=r'Bitcoin $z^*(5)$, 365-day windows, step 30')
    for x in (-1.96, 1.96):
        ax.axhline(x, color=Purple, ls='--', lw=0.9)
    ax.plot([], [], color=Purple, ls='--', lw=0.9, label=r'$\pm 1.96$')
    r = d[d['reject']]
    ax.scatter(r.index, r['zstar'], color=IDAred, zorder=3, s=22, label='Outside its band')
    for i, row in r.iterrows():
        ax.annotate(str(i.date()), (i, row['zstar']), xytext=(4, 4), textcoords='offset points', fontsize=7,
                    color=IDAred)
    ax.set_ylabel(r'$z^*(5)$')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    ax = axes[1]
    if sims is not None:
        ax.hist(sims, bins=40, color=MainBlue, alpha=0.6, density=True, label='Bootstrap z*(5)')
        lo, hi = np.percentile(sims, [2.5, 97.5])
        for v in (lo, hi):
            ax.axvline(v, color=Gray, ls='--', lw=0.8)
        ax.axvline(z0, color=IDAred, lw=1.4, label=f'Observed {z0:.2f}')
        ax.set_title(f'Window ending {date0}', fontsize=8.5, loc='left')
        legend_outside_bottom(ax, ncol=1, y=-0.12)
    plt.tight_layout()
    save_fig('ch2_sem_amh_btc')


def fig_b5(strip, res):
    """B5: the TOM days at a month change and the TOM effect with OLS and HAC intervals."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.9), gridspec_kw={'width_ratios': [1.5, 1]})
    ax = axes[0]
    x = np.arange(len(strip))
    ax.bar(x, strip['r'], color=[Orange if t else MainBlue for t in strip['tom']], width=0.65)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%d %b') for d in strip.index], rotation=45, fontsize=7)
    ax.set_ylabel('S&P 500 log return (bp)')
    ax.set_title('Month boundary July/August 2026', fontsize=8.5, loc='left')
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=Orange, label='TOM = 1 (last day, first three days)'),
                       plt.Rectangle((0, 0), 1, 1, color=MainBlue, label='TOM = 0')],
              loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=2, frameon=False)
    ax = axes[1]
    for i, (k, c) in enumerate([('sp500', MainBlue), ('bet', IDAred)]):
        b = res[k]
        ax.errorbar(i - 0.1, b['beta'], yerr=1.96 * b['se_ols'], fmt='o', color=c, capsize=3, alpha=0.5)
        ax.errorbar(i + 0.1, b['beta'], yerr=1.96 * b['se_hac'], fmt='s', color=c, capsize=3)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['S&P 500', 'BET'])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel(r'$\hat b$ (bp per TOM day)')
    ax.set_title('TOM coefficient, 95% intervals', fontsize=8.5, loc='left')
    ax.legend(handles=[plt.Line2D([], [], marker='o', ls='', color='black', alpha=0.5, label='OLS'),
                       plt.Line2D([], [], marker='s', ls='', color='black', label='HAC, 5 lags')],
              loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_b5')


def fig_b6(cm):
    """B6: the sorted p-values (log scale) with the raw, Bonferroni and Holm thresholds."""
    d = cm.sort_values('p').reset_index(drop=True)
    m = len(d)
    j = np.arange(1, m + 1)
    fig, ax = plt.subplots(figsize=(8.6, 3.0))
    ax.axhline(0.05, color=Amber, ls='--', lw=1.0, label='Raw 5%')
    ax.axhline(0.05 / m, color=IDAred, ls='--', lw=1.0, label=f'Bonferroni 0.05/{m}')
    ax.step(j, 0.05 / (m - j + 1), where='mid', color=Forest, lw=1.2, label='Holm threshold 0.05/(M - j + 1)')
    col = [IDAred if h else (Amber if rr else MainBlue) for h, rr in zip(d['holm_reject'], d['raw_reject'])]
    ax.scatter(j, d['p'], color=col, s=30, zorder=3)
    for i, row in d.iterrows():
        lab = f"{row['market'].split(' (')[0]}, {row['effect'].replace(' (equal means)', '')}"
        ax.annotate(lab, (i + 1, row['p']), xytext=(3, -3 if i % 2 else 5), textcoords='offset points', fontsize=6,
                    rotation=30, color='black')
    first_fail = int((~d['holm_reject']).idxmax()) + 1
    ax.axvline(first_fail, color=Purple, ls=':', lw=1.0, label=f'Holm stops at rank {first_fail}')
    ax.set_yscale('log')
    ax.set_xticks(j)
    ax.set_xlabel('Rank j of the p-value')
    ax.set_ylabel('p-value (log scale)')
    ax.set_ylim(d['p'].min() / 5, 40)
    hs, ls = ax.get_legend_handles_labels()
    hs += [plt.Line2D([], [], marker='o', ls='', color=IDAred), plt.Line2D([], [], marker='o', ls='', color=Amber),
           plt.Line2D([], [], marker='o', ls='', color=MainBlue)]
    ls += ['Rejected by Holm', 'Rejected only without correction', 'Not rejected']
    ax.legend(hs, ls, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_b6')


def fig_b7(b7):
    """B7: S&P 500 returns with the crises removed and rho1 with robust intervals in the two samples."""
    r = log_returns('sp500') * 100
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.9), gridspec_kw={'width_ratios': [2.2, 1]})
    ax = axes[0]
    ax.plot(r.index, r.values, color=MainBlue, lw=0.4)
    for a, b in CRISES:
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=IDAred, alpha=0.2, lw=0)
    ax.set_ylabel('Daily log return (%)')
    ax.set_title('S&P 500; shaded: days removed (Sep 2008 - Jun 2009, 15 Feb - 30 Jun 2020)', fontsize=8.5, loc='left')
    ax = axes[1]
    for i, (lab, c) in enumerate([('all days', MainBlue), ('without 2008-09 and 2020 crises', Forest)]):
        b = b7[lab]
        se = b['rho1'] / b['t_robust']
        ax.errorbar(i, b['rho1'], yerr=1.96 * se, fmt='o', color=c, capsize=4)
        ax.text(i + 0.08, b['rho1'], f"{b['rho1']:.3f}\nz*(5) = {b['zstar5']:.2f}", fontsize=7, va='center',
                color='black')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['All days', 'Without crises'])
    ax.set_xlim(-0.4, 1.7)
    ax.set_ylabel(r'$\hat\rho_1$, robust 95% interval')
    plt.tight_layout()
    save_fig('ch2_sem_b7')


def fig_b8():
    """B8: the log dividend-price ratio and the cumulative reduction in squared errors of the recursive forecasts."""
    import predictability as PRD
    df, _ = PRD.monthly_data()
    o = pd.read_csv(os.path.join(HERE, 'ch2_oos_dp.csv'), index_col=0, parse_dates=True)
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.9))
    ax = axes[0]
    ax.plot(df.index, df['dp'], color=MainBlue, lw=0.9, label=r'$dp_t = \ln D_t - \ln P_t$ (S&P 500, monthly)')
    ax.axvline(pd.Timestamp('1970-01-31'), color=IDAred, ls='--', lw=0.9, label='First forecast: January 1970')
    ax.set_title('Predictor: log dividend-price ratio', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.14)
    ax = axes[1]
    ax.plot(o.index, o['cum_dsse'], color=Forest, lw=1.1, label='Cumulative reduction in squared forecast errors vs historical mean')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_title('Rising: dp beats the historical mean', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.14)
    plt.tight_layout()
    save_fig('ch2_sem_b8')


def fig_b9(ev):
    """B9: daily abnormal returns (+-1.96 portfolio prediction standard errors) and CAR from day 0."""
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.0))
    ax = axes[0]
    w = 0.27
    for i, (k, c) in enumerate([('TLV', MainBlue), ('BRD', Forest), ('PORT', IDAred)]):
        d = ev[k]
        ax.bar(d['day'] + (i - 1) * w, 100 * d['AR'], w, color=c,
               label={'TLV': 'Banca Transilvania', 'BRD': 'BRD', 'PORT': 'Equal-weighted portfolio'}[k])
    p = ev['PORT']
    ax.fill_between(p['day'], -196 * p['se'], 196 * p['se'], color=LightGray, alpha=0.7, lw=0, step='mid',
                    label=r'Portfolio $\pm 1.96$ prediction-error SE', zorder=0)
    ax.axvline(0, color=Gray, ls='--', lw=0.7)
    ax.set_xlabel('Event day (0 = 19 Dec 2018)')
    ax.set_ylabel('Abnormal return (%)')
    ax.set_title('Daily abnormal returns', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    ax = axes[1]
    for k, c in [('TLV', MainBlue), ('BRD', Forest), ('PORT', IDAred)]:
        d = ev[k][ev[k]['day'] >= 0]
        ax.plot(d['day'], 100 * d['AR'].cumsum(), color=c, marker='o', ms=3, lw=1.2)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Event day')
    ax.set_ylabel('CAR from day 0 (%)')
    ax.set_title('Cumulative abnormal return, days 0 to +5', fontsize=8.5, loc='left')
    plt.tight_layout()
    save_fig('ch2_sem_b9')


def fig_c1(roll, res, split='2020-09-21', announce='2019-09-26'):
    """C1: 250-day rho1 with robust intervals (BET, WIG20, BUX) and the before/after change with a block bootstrap."""
    fig = plt.figure(figsize=(8.6, 3.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[2.3, 1])
    cols = {'bet': IDAred, 'wig20': MainBlue, 'bux': Forest}
    end = pd.Timestamp(res['bet']['after'][1])
    for i, k in enumerate(['bet', 'wig20', 'bux']):
        ax = fig.add_subplot(gs[i, 0])
        d = roll[k]
        ax.fill_between(d.index, d['rho1'] - 1.96 * d['se'], d['rho1'] + 1.96 * d['se'], color=cols[k], alpha=0.15, lw=0)
        ax.plot(d.index, d['rho1'], color=cols[k], lw=0.9)
        ax.axhline(0, color=Gray, lw=0.5)
        ax.axvline(pd.Timestamp(announce), color=Purple, ls=':', lw=0.9)
        ax.axvline(pd.Timestamp(split), color='black', ls='--', lw=0.9)
        ax.axvspan(end, d.index[-1], color=Amber, alpha=0.2, lw=0)
        ax.set_ylabel(LABELS[k].split(' (')[0], fontsize=8, color=cols[k])
        if i < 2:
            ax.set_xticklabels([])
    ax = fig.add_subplot(gs[:, 1])
    for i, k in enumerate(['bet', 'wig20', 'bux']):
        r = res[k]
        lo, hi = r['ci']
        ax.errorbar(r['diff'], i, xerr=[[r['diff'] - lo], [hi - r['diff']]], fmt='o', color=cols[k], capsize=3)
    ax.axvline(0, color=Gray, lw=0.6)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['BET', 'WIG20', 'BUX'])
    ax.invert_yaxis()
    ax.set_xlabel(r'Change in $\hat\rho_1$ (after - before)')
    ax.set_title('Block-bootstrap 95% CI', fontsize=8.5, loc='left')
    h = [plt.Rectangle((0, 0), 1, 1, color=Gray, alpha=0.3, label=r'Rolling 250-day $\hat\rho_1$ $\pm 1.96$ robust SE'),
         plt.Line2D([], [], color=Purple, ls=':', label='Announcement 26 Sep 2019'),
         plt.Line2D([], [], color='black', ls='--', label='Upgrade effective 21 Sep 2020'),
         plt.Rectangle((0, 0), 1, 1, color=Amber, alpha=0.2, label='After the formal five-year window')]
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch2_sem_c1')


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if hasattr(o, 'isoformat'):
        return o.isoformat()
    return o


if __name__ == '__main__':
    import json
    pd.set_option('display.width', 220)
    S = {}
    S['A1'] = a_vr_by_hand()
    S['A2'] = a_vr_by_hand(q=3)
    S['A3'] = a_runs()
    S['A4'] = a_runs(A4_SIGNS)
    t = b_vr_table(['sp500', 'bet'])
    S['A5'] = dict(vr=float(t.loc[LABELS['bet'], 'VR20']), H=float(h_from_vr(t.loc[LABELS['bet'], 'VR20'], 20)))
    S['A6'] = dict(vr=float(t.loc[LABELS['sp500'], 'VR20']), H=float(h_from_vr(t.loc[LABELS['sp500'], 'VR20'], 20)))
    S['B1'] = t.to_dict(orient='index')
    S['B1w'] = b1_worked('sp500', 2)
    t2 = b_vr_table(['bettr', 'wig20', 'bux', 'px', 'xu100', 'bvsp', 'mxx', 'nsei', 'ssec'])
    t2.to_csv(os.path.join(HERE, 'ch2_sem_vr_emerging.csv'))
    S['B2'] = t2.to_dict(orient='index')
    S['B3'] = b_rolling_dfa()
    d = b_amh_bitcoin()
    d.to_csv(os.path.join(HERE, 'ch2_sem_amh_btc.csv'))
    rej = d[d['reject']]
    x_btc = log_returns('btc', start='2011-01-01').values
    sims, z0, date0 = None, None, None
    if len(rej):
        e0 = int(rej['end'].iloc[0])
        _, sims = wild_bootstrap_vr_band(x_btc[e0 - 365:e0], 5, 999, SEED + e0, sims=True)
        z0, date0 = float(rej['zstar'].iloc[0]), rej.index[0].date()
    fig_amh_btc(d, sims, z0, date0)
    S['B4'] = dict(n=len(d), share=float(d['reject'].mean()), first=d.index[0].date(), last=d.index[-1].date(),
                   rejections=[dict(date=i.date(), z=float(r.zstar), lo=float(r.lo), hi=float(r.hi)) for i, r in rej.iterrows()],
                   band_lo_mean=float(d['lo'].mean()), band_hi_mean=float(d['hi'].mean()),
                   share_naive=float((d['zstar'].abs() > 1.96).mean()),
                   n_naive=int((d['zstar'].abs() > 1.96).sum()), n_boot=999)
    S['B5'] = {k: b_tom_ols_hac(k) for k in ['sp500', 'bet']}
    strip = b5_strip()
    S['B5strip'] = [dict(date=i.date(), r=float(v.r), tom=int(v.tom)) for i, v in strip.iterrows()]
    cm = b_calendar_multiple(calendar_table())
    cm.to_csv(os.path.join(HERE, 'ch2_sem_calendar_multiple.csv'), index=False)
    S['B6'] = cm.to_dict(orient='records')
    S['B7'] = b_crisis_robustness().to_dict(orient='index')
    S['B2c'] = b_bet_common_period()
    fig_b2(t2, t, S['B2c'])
    S['setup'] = setup_check()
    S['C1'] = c_bvb_before_after()
    S['C1c'] = {k: c_bvb_before_after(k=k) for k in ['wig20', 'bux']}
    # new charts
    fig_sem_data()
    fig_a1(S['A1'])
    sim = a2_null()
    S['A2sim'] = {k: v for k, v in sim.items() if not isinstance(v, np.ndarray)}
    fig_a2(sim)
    a3 = a3_exact(S['A3']['n1'], S['A3']['n2'], S['A3']['runs'])
    S['A3exact'] = dict(p_exact=a3['p_exact'], p_le=a3['p_le'], p_ge=a3['p_ge'], p11=a3['pmf'][S['A3']['runs']])
    fig_a3(a3, S['A3'])
    a4 = a4_sim()
    phi = -0.9 * 0.17 / 0.14
    S['A4sim'] = dict(mean=a4['mean'], median=a4['median'], rej=a4['rej'], rej_up=a4['rej_up'],
                      bias=phi * (-(1 + 3 * 0.98) / 60))
    fig_a4(a4, S['A4sim']['bias'])
    rho_bet = float(log_returns('bet').autocorr(1))
    S['A56'] = dict(rho_bet=rho_bet, vr20_pos=ar1_vr(rho_bet, 20), H20_pos=h_from_vr(ar1_vr(rho_bet, 20), 20),
                    vr250_pos=ar1_vr(rho_bet, 250), H250_pos=h_from_vr(ar1_vr(rho_bet, 250), 250))
    fig_a56(rho_bet, -0.1, S['A5']['H'], S['A6']['H'])
    fig_b1(t)
    w = b3_window()
    S['B3w'] = {k: v for k, v in w.items() if k not in ('y', 'index')}
    fig_b3_window(w)
    dr = pd.read_csv(os.path.join(HERE, 'ch2_sem_rolling_dfa.csv'), index_col=0, parse_dates=True)
    fig_b3_rolling(dr, S['B3']['lo_t'], S['B3']['hi_t'])
    fig_b5(strip, S['B5'])
    fig_b6(cm)
    fig_b7(S['B7'])
    fig_b8()
    ev = b9_event_path()
    S['B9'] = {k: v.assign(date=v.index.date).to_dict(orient='records') for k, v in ev.items()}
    fig_b9(ev)
    res_c1 = {'bet': S['C1'], **S['C1c']}
    roll = c1_rolling()
    fig_c1(roll, res_c1)
    S = _clean(S)
    with open(os.path.join(HERE, 'ch2_seminar_numbers.json'), 'w') as f:
        json.dump(S, f, indent=1)
    print(json.dumps({k: S[k] for k in ['A1', 'A3', 'A3exact', 'A4sim', 'A2sim', 'A56', 'B1w', 'B3w', 'B4', 'C1', 'C1c']},
                     indent=1, default=str)[:8000])

"""
seminar16.py -- Computations of Seminar 16 (MFM): digital assets and DeFi
=========================================================================
Part A: market-value weighted index and its divisor (A1, A2), the no-arbitrage band and the optimal arbitrage
in a pool with a fee (A3) and in a weighted pool (A4), impermanent loss of a weighted pool (A5),
LVR by Ito (A6), algebra of the threshold AR with a band (A7, A8).
Part B: Bitcoin vs S&P 500 and the weekend effect with a block bootstrap (B1, B2), the peg as an equilibrium
threshold AR (EQ-TAR, Balke & Fomby 1997) with the sup-Wald test and a fixed-regressor bootstrap (B3, B4), the fee
drift with HAC errors, ADF/KPSS and the Dimson beta for IBIT / ETHA (B5, B6), a break at an unknown date in the
beta of Strategy / Coinbase (B7, B8).
Part C: is Bitcoin an alternative asset, a risk asset or a hedge? (C1), with the Forbes-Rigobon correlation
and quantile regression; the AI critique (C2); crypto factors after July 2020 (C3).
The numbers are saved in sem16_results.json.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import price, log_returns, joint_returns, read_market, ASSETS, END   # noqa: E402
import statsmodels.api as sm                                                        # noqa: E402
import inference16 as I                                                             # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray, COL,  # noqa: E402,F811
                                 save_fig, legend_outside_bottom, fig_legend_bottom, jsonable, hac_ols,
                                 amm_swap, impermanent_loss, etf_tracking, ETF_START, SEED, B_BOOT,
                                 crix_index, ltw_weekly_series)

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCK = 20          # block length for the bootstrap (days)


# =============================================================================
# PART A
# =============================================================================
def a1_index():
    """Laspeyres index with three coins: level, divisor, reweighting at the end of the month."""
    p0 = np.array([60000.0, 3000.0, 150.0])          # prices on the base date
    q0 = np.array([19.5e6, 120e6, 500e6])            # circulating supply on the base date
    mv0 = p0 * q0
    D0 = mv0.sum() / 1000                            # divisor: the index starts at 1000
    p1 = np.array([66000.0, 2700.0, 180.0])          # prices at the end of the month
    I1 = (p1 * q0).sum() / D0
    w0 = mv0 / mv0.sum()
    q1 = np.array([19.52e6, 120.1e6, 560e6])         # new supply at reweighting
    D1 = (p1 * q1).sum() / I1                        # new divisor: the same level before and after
    return dict(mv0=mv0.tolist(), D0=D0, w0=w0.tolist(), I1=I1, ret=I1 / 1000 - 1, D1=D1,
                w1=((p1 * q1) / (p1 * q1).sum()).tolist(), rets=(p1 / p0 - 1).tolist())


def a2_replace():
    """Replacing a constituent: coin C leaves, coin D enters; the new divisor keeps the level."""
    p = np.array([66000.0, 2700.0, 180.0])
    q = np.array([19.52e6, 120.1e6, 560e6])
    I = 1000 * 1.0
    base = a1_index()
    I = base['I1']
    D = base['D1']
    pD, qD = 0.5, 40e9
    new_mv = p[0] * q[0] + p[1] * q[1] + pD * qD
    D_new = new_mv / I
    return dict(old_mv=(p * q).sum(), new_mv=new_mv, D_old=D, D_new=D_new, I=I, mvD=pD * qD, mvC=p[2] * q[2])


def a3_band(x=1000.0, y=3_000_000.0, P=3300.0, fee=0.003):
    """No-arbitrage band of a pool x*y = k with fee f: gamma P <= p <= P / gamma; optimal size of the
    arbitrage when the outside price P leaves the band: effective reserve y' = y + gamma dy* = sqrt(gamma P k),
    dy* = (y' - y) / gamma. The fee stays in the pool (Uniswap v2 convention): the actual reserves after the trade are
    x' and y + dy*, so the pool price is (y + dy*) / x'. Profit per unit of pool value: relative to the
    pool value before the trade, at the pool price (p x + y)."""
    g = 1 - fee
    k = x * y
    p = y / x
    y1 = np.sqrt(g * P * k)
    x1 = k / y1
    dy = (y1 - y) / g
    dx = x - x1
    profit = dx * P - dy
    V0 = p * x + y
    y_act = y + dy
    return dict(k=k, p=p, lo=g * P, hi=P / g, y1=y1, x1=x1, dy=dy, dx=dx, profit=profit, p_eff=y1 / x1,
                y_act=y_act, p_new=y_act / x1, band_lo=g * y_act / x1, band_hi=y_act / x1 / g,
                avg=dy / dx, profit_nofee=a4_nofee(x, y, P), V0=V0, rel=100 * profit / V0)


def a4_nofee(x, y, P):
    """Arbitrage profit without a fee (same pool): P (x - x1) - (y1 - y), x1 = sqrt(k/P), y1 = sqrt(kP)."""
    k = x * y
    return P * (x - np.sqrt(k / P)) - (np.sqrt(k * P) - y)


def a4_weighted(w=0.8, x=1000.0, p=3000.0, P=3300.0, fee=0.003):
    """Weighted pool x^w y^(1-w) = k (Balancer type): marginal price p = (w/(1-w)) y/x; effective reserves after
    arbitrage x' = k (w/(gamma P (1-w)))^(1-w), y' = k (gamma P (1-w)/w)^w; dy* = (y' - y)/gamma. The fee stays in the
    pool: actual reserve y + dy*, pool price (w/(1-w)) (y + dy*)/x'. Profit per unit of value: relative to the
    pool value before the trade, p x + y = y / (1 - w)."""
    g = 1 - fee
    y = p * x * (1 - w) / w
    k = x ** w * y ** (1 - w)
    x1 = k * (w / (g * P * (1 - w))) ** (1 - w)
    y1 = k * (g * P * (1 - w) / w) ** w
    dy = (y1 - y) / g
    dx = x - x1
    V0 = p * x + y
    y_act = y + dy
    return dict(w=w, y=y, k=k, x1=x1, y1=y1, dy=dy, dx=dx, profit=dx * P - dy, p_eff=(w / (1 - w)) * y1 / x1,
                y_act=y_act, p_new=(w / (1 - w)) * y_act / x1, V0=V0, rel=100 * (dx * P - dy) / V0)


def il_weighted(r, w):
    """Impermanent loss of a weighted pool: r^w / (w r + 1 - w) - 1."""
    return r ** w / (w * r + 1 - w) - 1


def a5_il():
    """IL for w = 0.5 and w = 0.8 at r = 0.5, 2, 4; second-order approximation -w(1-w)(ln r)^2 / 2."""
    out = {}
    for w in [0.5, 0.8]:
        for r in [0.5, 2.0, 4.0]:
            out[f'w{w:g}_r{r:g}'] = 100 * il_weighted(r, w)
            out[f'q{w:g}_r{r:g}'] = -100 * w * (1 - w) * np.log(r) ** 2 / 2
    return out


def a6_lvr(sig=0.70):
    """LVR rate of a weighted pool: sigma^2 w (1 - w) / 2; w = 1/2 gives sigma^2 / 8."""
    return {f'w{w:g}': 100 * sig ** 2 * w * (1 - w) / 2 for w in [0.5, 0.8, 0.95]}


def a7_tar(tar):
    """Algebra of the equilibrium threshold AR (EQ-TAR, Balke & Fomby 1997) on the USDC estimates of B3: half-lives
    in each regime and the number of days until a deviation of -285 bp (the close of 11 March 2023) re-enters the band."""
    d0 = 285.0
    n_out = np.log(tar['c'] / d0) / np.log(tar['phi_out'])
    return dict(d0=d0, n_out=n_out, n_days=int(np.ceil(n_out)), hl_in=tar['hl_in'], hl_out=tar['hl_out'])


def a8_mix(tar):
    """Probability limit of linear OLS on EQ-TAR data: phi_lin = phi_in (1 - s) + phi_out s,
    s = share of sum d_{t-1}^2 outside the band."""
    s = tar['share_var_out'] / 100
    return dict(s=100 * s, mix=tar['phi_in'] * (1 - s) + tar['phi_out'] * s, phi_lin=tar['phi_lin'])


# =============================================================================
# PART B
# =============================================================================
def block_boot(x, stat, B=B_BOOT, block=BLOCK, seed=SEED):
    """Moving-block bootstrap (Kunsch, 1989) for a statistic of a DataFrame/Series; 95% percentile interval."""
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    vals = []
    for _ in range(B):
        st = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in st])[:n]
        vals.append(stat(x.iloc[idx]))
    vals = np.array(vals)
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5), vals


def weekend_ratio(r):
    """Ratio of (centred) variances: weekend (Saturday, Sunday) / weekdays."""
    we = r[r.index.dayofweek >= 5]
    wd = r[r.index.dayofweek < 5]
    return we.var(ddof=1) / wd.var(ddof=1)


def b1_btc_facts(key='BTC'):
    """Annualised volatility relative to the S&P 500 and the weekend effect before / after the ETFs, with a block bootstrap."""
    r = 100 * log_returns(key, '2018-01-01')
    s = 100 * log_returns('SPX', str(r.index[0].date()))
    vc = r.std() * np.sqrt(365)
    vs = s.std() * np.sqrt(252)
    lo, hi, _ = block_boot(r, lambda x: x.std() * np.sqrt(365))
    pre, post = r.loc[:'2024-01-10'], r.loc[ETF_START:]
    rp, rq = weekend_ratio(pre), weekend_ratio(post)
    plo, phi_, dpre = block_boot(pre, weekend_ratio, block=21)
    qlo, qhi, dpost = block_boot(post, weekend_ratio, block=21, seed=SEED + 1)
    diff = dpost - dpre
    return dict(start=str(r.index[0].date()), n=len(r), vol=vc, vol_lo=lo, vol_hi=hi, vol_spx=vs, ratio=vc / vs,
                wr_pre=rp, wr_pre_lo=plo, wr_pre_hi=phi_, wr_post=rq, wr_post_lo=qlo, wr_post_hi=qhi,
                diff=rq - rp, diff_lo=np.percentile(diff, 2.5), diff_hi=np.percentile(diff, 97.5),
                n_pre=len(pre), n_post=len(post), kurt=float(pd.Series(r).kurt()), _dpre=dpre, _dpost=dpost)


def fig_sem_weekend(b1):
    """Bootstrap distributions of the weekend / weekday ratio, before and after the ETFs."""
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    ax.hist(b1['_dpre'], bins=50, color=MainBlue, alpha=0.75, density=True, label='2018 - 10 Jan 2024')
    ax.hist(b1['_dpost'], bins=50, color=Orange, alpha=0.75, density=True, label='11 Jan 2024 - Sep 2026')
    ax.axvline(1, color=Gray, lw=0.7, ls='--')
    ax.set_xlabel('Weekend variance / weekday variance (Bitcoin), block bootstrap draws')
    ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch16_sem_weekend')


def b3_usdc(key='USDC', start='2021-01-01'):
    """Daily peg deviation (bp): statistics, equilibrium threshold AR (EQ-TAR) with the sup-Wald test and a
    fixed-regressor bootstrap (Hansen, 1996), with and without the week of 9-16 March 2023."""
    d = read_market(ASSETS[key][0]).loc[start:END]
    dev = 1e4 * (d['close'] - 1)
    ex = dev.drop(dev.loc['2023-03-09':'2023-03-16'].index)
    return dict(key=key, n=len(dev), sd=dev.std(), sd_ex=ex.std(), out50=int((dev.abs() > 50).sum()),
                out50_ex=int((ex.abs() > 50).sum()), min=dev.min(), min_date=str(dev.idxmin().date()),
                low=1e4 * (d['low'].min() - 1), low_date=str(d['low'].idxmin().date()),
                full=I.tar_fit(dev), ex=I.tar_fit(ex), kurt=float(dev.kurt()))


def fig_sem_usdc(tar):
    """USDC: peg deviation in 2023 and today's deviation against yesterday's, with the EQ-TAR lines of each
    regime (estimated threshold c) and the linear AR(1) line."""
    d = read_market(ASSETS['USDC'][0]).loc['2021-01-01':END]
    dev = 1e4 * (d['close'] - 1)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    z = dev.loc['2023-01-01':'2023-06-30']
    axes[0].plot(z.index, z.values, color=MainBlue, lw=0.9, label='USDC close deviation (bp)')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].tick_params(axis='x', labelsize=7, rotation=30)
    axes[0].set_ylabel('bp')
    z1 = pd.concat([dev.shift(1), dev], axis=1).dropna()
    z1.columns = ['lag', 'now']
    zz = z1[(z1.abs() <= 12).all(axis=1)]
    axes[1].scatter(zz['lag'], zz['now'], s=5, color=Teal, alpha=0.6, label='Pairs of days (within 12 bp)')
    c = tar['c']
    xi = np.array([-c, c])
    axes[1].plot(xi, tar['phi_in'] * xi, color=Forest, lw=1.8, label=f'Inside the band: slope {tar["phi_in"]:.2f}')
    for xo in [np.array([-12, -c]), np.array([c, 12])]:
        axes[1].plot(xo, tar['phi_out'] * xo, color=IDAred, lw=1.8)
    axes[1].plot([], [], color=IDAred, lw=1.8, label=f'Outside the band: slope {tar["phi_out"]:.2f}')
    for v in [-c, c]:
        axes[1].axvline(v, color=Gray, lw=0.6, ls='--')
    axes[1].set_xlim(-12, 12)
    axes[1].set_ylim(-12, 12)
    axes[1].set_xlabel('Deviation yesterday (bp)')
    axes[1].set_ylabel('Deviation today (bp)')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_sem_usdc')


def b5_etf(etf='IBIT', coin='BTC'):
    """Tracking: daily vs weekly beta (HAC); the fee drift as the mean of Delta ln(P_ETF/P_coin) with a HAC
    error; ADF (H0: unit root) and KPSS (H0: stationarity around a trend) tests on the level of the ratio;
    comparison with the slope of the level on time; Dimson (1979) beta with one lag and one lead."""
    from statsmodels.tsa.stattools import adfuller, kpss
    t = etf_tracking(etf, coin)
    p = pd.concat([price(etf), price(coin)], axis=1, join='inner').dropna()
    lr = np.log(p[etf] / p[coin])
    yrs = (lr.index[-1] - lr.index[0]).days / 365.25
    dl = lr.diff().dropna()
    ppy = len(dl) / yrs
    L = I.nw_lags(len(dl))
    m0 = sm.OLS(dl.values, np.ones(len(dl))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    tt = pd.Series((lr.index - lr.index[0]).days / 365.25, index=lr.index)
    m = hac_ols(lr, tt, lags=20)
    adf = adfuller(lr.values, regression='ct', autolag='AIC')
    kp = kpss(lr.values, regression='ct', nlags='auto')
    adf_d = adfuller(dl.values, regression='c', autolag='AIC')
    t.update(drift_mean=100 * ppy * m0.params[0], drift_mse=100 * ppy * m0.bse[0],
             drift_mlo=100 * ppy * (m0.params[0] - 1.96 * m0.bse[0]), drift_mhi=100 * ppy * (m0.params[0] + 1.96 * m0.bse[0]),
             drift_hac=100 * m.params.iloc[1], drift_se=100 * m.bse.iloc[1],
             drift_lo=100 * (m.params.iloc[1] - 1.96 * m.bse.iloc[1]), drift_hi=100 * (m.params.iloc[1] + 1.96 * m.bse.iloc[1]),
             adf=adf[0], adf_p=adf[1], kpss=kp[0], kpss_p=kp[1], adf_d=adf_d[0], adf_d_p=adf_d[1],
             t_beta_w=(t['beta_w'] - 1) / t['se_w'], lags=L, dimson=I.dimson(etf, coin))
    return t


def b7_equity(key='MSTR'):
    """Weekly two-factor regression, the test b_BTC = 1 in subperiods and the sup-Wald test (Andrews, 1993)
    for a break at an unknown date in all three coefficients, with HAC errors and the Bai (1997) CI."""
    out = {}
    # the subperiods partition the full sample: p1 ends the day before the ETFs, p2 starts with them
    for lab, a, b in [('full', '2021-04-16', END), ('p1', '2021-04-16', '2024-01-10'), ('p2', ETF_START, END)]:
        w = joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc[a:b]
        m = hac_ols(w[key], w[['BTC', 'SPX']])
        out[lab] = dict(n=len(w), b_btc=m.params['BTC'], se_btc=m.bse['BTC'], b_spx=m.params['SPX'],
                        se_spx=m.bse['SPX'], r2=m.rsquared, t1=(m.params['BTC'] - 1) / m.bse['BTC'],
                        alpha=52 * 100 * m.params['const'], alpha_t=m.tvalues['const'])
    w = 100 * joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc['2021-04-16':END]
    X = np.column_stack([np.ones(len(w)), w['BTC'].values, w['SPX'].values])
    sw = I.sup_wald(w[key].values, X, w.index)
    Wser = pd.Series(sw.pop('W'), index=w.index)
    crit = I.sup_wald_crit(3)
    sw.update(p=float((crit >= sw['sup_w']).mean()), cv5=float(np.percentile(crit, 95)),
              W_etf=float(Wser.loc[ETF_START:].iloc[0]), W_date=float(Wser.loc[sw['date']]))
    out['sw'] = sw
    # test of the change: full-sample regression with interactions D_t = 1 after the ETF launch, HAC errors (same lags)
    w = joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc['2021-04-16':END]
    D = (w.index >= pd.Timestamp(ETF_START)).astype(float)
    Xi = pd.DataFrame({'BTC': w['BTC'], 'SPX': w['SPX'], 'D': D, 'D_BTC': D * w['BTC'], 'D_SPX': D * w['SPX']}, index=w.index)
    m = hac_ols(w[key], Xi)
    out['chg'] = dict(d_btc=m.params['D_BTC'], se=m.bse['D_BTC'], t=m.tvalues['D_BTC'], p=m.pvalues['D_BTC'])
    return out


# =============================================================================
# C3: crypto factors after July 2020 (instructor reference; Liu, Tsyvinski & Wu, 2022)
# =============================================================================
C3_COINS = ['BTC', 'ETH', 'XRP', 'BNB', 'ADA', 'SOL', 'DOGE', 'LTC', 'LINK']
FX_FRED = {'DEXCAUS': -1, 'DEXSIUS': -1, 'DEXUSAL': 1, 'DEXUSEU': 1, 'DEXUSUK': 1}   # -1: units per USD; 1: USD per unit


def paper_week(idx):
    """Week of the paper's calendar: 52 a year, the first 51 of 7 days, the last one up to 31 December."""
    idx = pd.DatetimeIndex(idx)
    return pd.MultiIndex.from_arrays([idx.year, np.minimum((idx.dayofyear - 1) // 7 + 1, 52)])


def compound_weekly(r):
    """Compound daily simple returns (weekdays) into the paper's weeks; index = end of the week."""
    g = (1 + r).groupby(paper_week(r.index)).prod() - 1
    ends = [pd.Timestamp(y, 12, 31) if w == 52 else pd.Timestamp(y, 1, 1) + pd.Timedelta(days=7 * w - 1) for y, w in g.index]
    g.index = pd.DatetimeIndex(ends)
    return g


def c3_factors():
    """The five global factors (developed markets) and the one-month bill rate, daily, from the Kenneth French Data
    Library; USD returns of holding five currencies (FRED)."""
    import io, zipfile, urllib.request
    url = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_5_Factors_Daily_CSV.zip'
    raw = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url).read()))
    txt = raw.read(raw.namelist()[0]).decode('latin-1').splitlines()
    rows = [l.split(',') for l in txt if l[:8].strip().isdigit() and len(l.split(',')) == 7]
    ff = pd.DataFrame([[float(x) for x in r[1:]] for r in rows], columns=['MKT', 'SMB', 'HML', 'RMW', 'CMA', 'RF'],
                      index=pd.to_datetime([r[0].strip() for r in rows], format='%Y%m%d')) / 100
    fx = {}
    for sid, sign in FX_FRED.items():
        s = pd.read_csv(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}', index_col=0, parse_dates=True).iloc[:, 0]
        s = pd.to_numeric(s, errors='coerce').dropna()
        fx[sid] = (s if sign > 0 else 1 / s).pct_change().dropna()
    return ff, pd.DataFrame(fx)


def c3_ltw(split='2020-07-31'):
    """C3 (reference): (b) segmentation: excess return of the five-coin index on the five global factors
    and five currencies; (c) three-week momentum: the three coins with the highest return over the last
    three weeks minus the three with the lowest, equal weights, held one week; crypto CAPM; (d) full-sample
    regression with D_t (after July 2020) and D_t * CMKT, the sup-Wald test for (alpha, beta) at an unknown date; Holm."""
    ff, fx = c3_factors()
    tot, _ = crix_index(None, 'cap')
    mkt = ltw_weekly_series(tot)
    rf = compound_weekly(ff['RF'])
    fw = pd.DataFrame({'MKT': compound_weekly(ff['MKT'] + ff['RF']) - rf,
                       **{c: compound_weekly(ff[c]) for c in ['SMB', 'HML', 'RMW', 'CMA']},
                       **{c: compound_weekly(fx[c]) for c in fx}})
    last_wk = rf.index[rf.index <= ff.index[-1]][-1]        # last week fully covered by the factors
    mkt, rf, fw = mkt.loc[:last_wk], rf.loc[:last_wk], fw.loc[:last_wk]
    out = dict(start=str(mkt.index[0].date()), ff_end=str(ff.index[-1].date()), last=str(last_wk.date()))
    # (b)
    d = pd.concat([(mkt - rf).rename('y'), fw], axis=1, join='inner').dropna()
    X = d.drop(columns='y')
    rng = np.random.default_rng(SEED)
    for lab, a, b in [('ins', None, split), ('oos', '2020-08-01', None)]:
        dd = d.loc[a:b]
        m = hac_ols(dd['y'], X.loc[dd.index], lags=I.nw_lags(len(dd)))
        T, bl = len(dd), 8
        r2 = []
        for _ in range(999):
            st = rng.integers(0, T - bl + 1, int(np.ceil(T / bl)))
            ix = np.concatenate([np.arange(s0, s0 + bl) for s0 in st])[:T]
            yb, Xb = dd['y'].values[ix], sm.add_constant(X.loc[dd.index].values[ix])
            r2.append(sm.OLS(yb, Xb).fit().rsquared)
        out['b_' + lab] = dict(n=T, first=str(dd.index[0].date()), last=str(dd.index[-1].date()), r2=m.rsquared,
                               r2_lo=float(np.percentile(r2, 2.5)), r2_hi=float(np.percentile(r2, 97.5)),
                               n_sig=int((m.pvalues.drop('const') < 0.05).sum()),
                               t_mkt=m.tvalues['MKT'], b_mkt=m.params['MKT'])
    # (c)
    W = pd.concat([ltw_weekly_series(price(k)).rename(k) for k in C3_COINS], axis=1)
    past = (1 + W).rolling(3, min_periods=3).apply(np.prod, raw=True) - 1
    mom = {}
    for t in range(3, len(W) - 1):
        ok = past.iloc[t].notna() & W.iloc[t + 1].notna()
        if ok.sum() < 6:
            continue
        srt = past.iloc[t][ok].sort_values()
        nxt = W.iloc[t + 1]
        mom[W.index[t + 1]] = nxt[srt.index[-3:]].mean() - nxt[srt.index[:3]].mean()
    mom = pd.Series(mom).loc[out['start']:]
    n_coins = W.notna().sum(axis=1)
    c = pd.concat([mom.rename('mom'), (mkt - rf).rename('m')], axis=1, join='inner').dropna()
    for lab, a, b in [('ins', None, split), ('oos', '2020-08-01', None), ('full', None, None)]:
        cc = c.loc[a:b]
        L = I.nw_lags(len(cc))
        m0 = sm.OLS(cc['mom'].values, np.ones(len(cc))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
        m1 = hac_ols(cc['mom'], cc[['m']], lags=L)
        out['c_' + lab] = dict(n=len(cc), first=str(cc.index[0].date()), last=str(cc.index[-1].date()),
                               mean=100 * m0.params[0], t_mean=m0.tvalues[0], alpha=100 * m1.params['const'],
                               t_alpha=m1.tvalues['const'], p_alpha=m1.pvalues['const'], beta=m1.params['m'],
                               t_beta=m1.tvalues['m'], r2=m1.rsquared)
    out['c_ncoins_start'] = int(n_coins.loc[c.index[0]])
    # (d) full-sample regression: alpha and beta may change after July 2020
    D = (c.index > pd.Timestamp(split)).astype(float)
    Xi = pd.DataFrame({'m': c['m'], 'D': D, 'Dm': D * c['m']}, index=c.index)
    L = I.nw_lags(len(c))
    m2 = hac_ols(c['mom'], Xi, lags=L)
    out['d_chg'] = dict(d=100 * m2.params['D'], t=m2.tvalues['D'], p=m2.pvalues['D'], e=m2.params['Dm'], t_e=m2.tvalues['Dm'])
    Xs = np.column_stack([np.ones(len(c)), 100 * c['m'].values])
    sw = I.sup_wald(100 * c['mom'].values, Xs, c.index)
    Wser = pd.Series(sw.pop('W'), index=c.index)
    crit = I.sup_wald_crit(2)
    lo_d, hi_d = Wser.dropna().index[0], Wser.dropna().index[-1]
    sw.update(p=float((crit >= sw['sup_w']).mean()), cv5=float(np.percentile(crit, 95)),
              trim_lo=str(lo_d.date()), trim_hi=str(hi_d.date()),
              W_split=float(Wser.loc[:split].dropna().iloc[-1]) if Wser.loc[:split].notna().any() else float('nan'))
    out['d_sw'] = sw
    # Holm for the family of alpha tests: (c) in, (c) out, (d) change, (d) sup-Wald
    fam = {'c_ins': out['c_ins']['p_alpha'], 'c_oos': out['c_oos']['p_alpha'], 'd_chg': out['d_chg']['p'], 'd_sw': sw['p']}
    ks = sorted(fam, key=fam.get)
    adj, run = {}, 0.0
    for i, k in enumerate(ks):
        run = max(run, min(1.0, (len(ks) - i) * fam[k]))
        adj[k] = run
    out['holm'] = adj
    out['holm_raw'] = fam
    return out


# =============================================================================
# PART C: is Bitcoin an alternative asset, a risk asset or a hedge?
# =============================================================================
def c1_hedge():
    """Correlations before / after the ETFs (block bootstrap) and the Baur-Lucey regression for hedge and safe haven."""
    out = {}
    per = {'pre': ('2021-01-01', '2024-01-10'), 'post': (ETF_START, END)}
    for k in ['SPX', 'QQQ', 'GLD', 'TLT']:
        r = joint_returns(['BTC', k], '2021-01-01')
        res = {}
        draws = {}
        for lab, (a, b) in per.items():
            x = r.loc[a:b]
            lo, hi, dr = block_boot(x, lambda z: z.iloc[:, 0].corr(z.iloc[:, 1]), block=20,
                                    seed=SEED + len(lab))
            res[lab] = x['BTC'].corr(x[k])
            res[lab + '_lo'], res[lab + '_hi'] = lo, hi
            draws[lab] = dr
        dd = draws['post'] - draws['pre']
        res['diff_lo'], res['diff_hi'] = np.percentile(dd, [2.5, 97.5])
        out[k] = res
    # Baur-Lucey: r_BTC = a + b r_SPX + sum_q c_q r_SPX 1{r_SPX <= q-quantile}
    bl = {}
    for lab, (a, b) in per.items():
        r = 100 * joint_returns(['BTC', 'SPX'], a).loc[a:b]
        X = pd.DataFrame({'SPX': r['SPX']})
        for q in [0.10, 0.05, 0.01]:
            thr = r['SPX'].quantile(q)
            X[f'q{int(100 * q)}'] = r['SPX'] * (r['SPX'] <= thr)
        m = hac_ols(r['BTC'], X)
        b0 = m.params['SPX']
        # the indicators are nested: b = slope above the 10% quantile, b + c10 between 5% and 10%, b + c10 + c5 between 1% and 5%,
        # b + c10 + c5 + c1 in the worst 1%; SEs of the sums from the full HAC covariance matrix
        Vc = m.cov_params()
        def tot(names):
            R = pd.Series(0.0, index=m.params.index)
            R[names] = 1.0
            return float(R @ m.params), float(np.sqrt(R @ Vc @ R))
        (t10, s10), (t5, s5), (t1, s1) = tot(['SPX', 'q10']), tot(['SPX', 'q10', 'q5']), tot(['SPX', 'q10', 'q5', 'q1'])
        mall = hac_ols(r['BTC'], r[['SPX']])          # hedge regression on all days
        bl[lab] = dict(n=len(r), b=b0, se=m.bse['SPX'], c10=m.params['q10'], c5=m.params['q5'], c1=m.params['q1'],
                       tot10=t10, tot5=t5, tot1=t1, se_tot10=s10, se_tot5=s5, se_tot1=s1,
                       lo_tot1=t1 - 1.96 * s1, hi_tot1=t1 + 1.96 * s1,
                       b_all=mall.params['SPX'], se_all=mall.bse['SPX'],
                       se10=m.bse['q10'], se5=m.bse['q5'], se1=m.bse['q1'])
        # beta on down / up days
        dn, up = r[r['SPX'] < 0], r[r['SPX'] > 0]
        bl[lab]['beta_dn'] = np.polyfit(dn['SPX'], dn['BTC'], 1)[0]
        bl[lab]['beta_up'] = np.polyfit(up['SPX'], up['BTC'], 1)[0]
        worst = r.nsmallest(10, 'SPX')
        bl[lab]['worst10_spx'] = worst['SPX'].mean()
        bl[lab]['worst10_btc'] = worst['BTC'].mean()
    out['bl'] = bl
    # Forbes-Rigobon: post-ETF correlation adjusted for the volatility of the S&P 500 (relative to the 'pre' period)
    r = joint_returns(['BTC', 'SPX'], '2021-01-01')
    x0, x1 = r.loc[per['pre'][0]:per['pre'][1]].values, r.loc[per['post'][0]:per['post'][1]].values
    def rstar(z0, z1):
        r0, r1 = np.corrcoef(z0.T)[0, 1], np.corrcoef(z1.T)[0, 1]
        dl = z1[:, 1].var() / z0[:, 1].var() - 1
        return r1 / np.sqrt(1 + dl * (1 - r1 ** 2)) - r0, dl, r1 / np.sqrt(1 + dl * (1 - r1 ** 2))
    d_fr, delta, rs = rstar(x0, x1)
    rng = np.random.default_rng(SEED)
    def mbb(z):
        n = len(z)
        st = rng.integers(0, n - 19, int(np.ceil(n / 20)))
        return z[(st[:, None] + np.arange(20)[None, :]).ravel()[:n]]
    dd = [rstar(mbb(x0), mbb(x1))[0] for _ in range(B_BOOT)]
    out['fr'] = dict(delta=delta, rho_star=rs, diff=d_fr, lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5))
    # quantile regression (Koenker & Bassett, 1978): quantile tau of r_BTC conditional on r_SPX, block bootstrap
    from statsmodels.regression.quantile_regression import QuantReg
    qr = {}
    for lab, (a, b) in per.items():
        z = 100 * joint_returns(['BTC', 'SPX'], a).loc[a:b]
        Xq = sm.add_constant(z['SPX'].values)
        for tau in [0.01, 0.05, 0.5]:
            bq = QuantReg(z['BTC'].values, Xq).fit(q=tau).params[1]
            bs = []
            zz = z.values
            for _ in range(300):
                y = mbb(zz)
                bs.append(QuantReg(y[:, 0], sm.add_constant(y[:, 1])).fit(q=tau).params[1])
            qr[f'{lab}_{int(100 * tau)}'] = dict(b=bq, se=float(np.std(bs)))
    out['qr'] = qr
    # volatility and the largest drawdown in the two periods
    p = price('BTC', '2021-01-01')
    for lab, (a, b) in per.items():
        x = p.loc[a:b]
        r = np.log(x).diff().dropna()
        out[lab + '_vol'] = 100 * r.std() * np.sqrt(365)
        out[lab + '_mdd'] = 100 * (x / x.cummax() - 1).min()
    return out


def fig_sem_hedge(c1):
    """Slope of Bitcoin on the S&P 500 in the four disjoint regimes of the nested-indicator regression (S&P 500 days
    above the 10% quantile, between 5% and 10%, between 1% and 5%, the worst 1%), before and after the ETFs; +- 1.96 SE."""
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    labs = ['Above 10th percentile', '5th-10th percentile', '1st-5th percentile', 'Bottom 1%']
    x = np.arange(4)
    for i, (lab, c) in enumerate([('pre', MainBlue), ('post', Orange)]):
        b = c1['bl'][lab]
        ax.bar(x + (i - 0.5) * 0.38, [b['b'], b['tot10'], b['tot5'], b['tot1']], 0.36, color=c,
               yerr=1.96 * np.array([b['se'], b['se_tot10'], b['se_tot5'], b['se_tot1']]), capsize=2,
               error_kw=dict(ecolor='black', lw=0.7),
               label='Jan 2021 - 10 Jan 2024' if lab == 'pre' else '11 Jan 2024 - Sep 2026')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_xlabel('S&P 500 daily return regime')
    ax.set_ylabel('Bitcoin slope on the S&P 500')
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch16_sem_hedge')


def c2_ai(start='2021', end='2025'):
    """C2: the AI assistant's answer (log returns from prices cut to 2021-2025, annualised with 252,
    r_f = 5%) and the correction steps: 365; returns computed before selecting the period; simple excess
    returns for the Sharpe ratio; r_f = mean yield of the 3-month Treasury bill (FRED DTB3)."""
    btc = read_market(ASSETS['BTC'][0])['close']
    r = np.log(btc.loc[start:end]).diff().dropna()                  # the AI code: the first day of 2021 is lost
    out = dict(n_ai=len(r), per_year={str(k): int(v) for k, v in r.groupby(r.index.year).size().items()})
    for m in [252, 365]:
        mu, sd = r.mean() * m, r.std() * np.sqrt(m)
        out[f'mu{m}'], out[f'sd{m}'], out[f'sh{m}'] = 100 * mu, 100 * sd, (mu - 0.05) / sd
    rs = btc.pct_change().loc[start:end].dropna()                      # simple returns, computed before the selection
    tb = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3', index_col=0, parse_dates=True).iloc[:, 0]
    rf = float(pd.to_numeric(tb, errors='coerce').dropna().loc[start:end].mean() / 100)
    mu, sd = rs.mean() * 365, rs.std() * np.sqrt(365)
    rl = np.log1p(rs)
    out.update(n=len(rs), mu_log=100 * rl.mean() * 365, mu_s=100 * mu, sd_s=100 * sd, rf=100 * rf,
               sh_s=(mu - rf) / sd, gap=100 * (mu - rl.mean() * 365), half_var=100 * sd ** 2 / 2)
    return out


# =============================================================================
# CHARTS OF THE SOLUTIONS (A1, A3, A5, A7, B2, B4, B5, B6, B7, B8, C2)
# =============================================================================
def fig_sem_a1(a1):
    """A1: market-value weights of the three coins on the base date and after the reallocation."""
    fig, ax = plt.subplots(figsize=(5.6, 2.7))
    x = np.arange(3)
    ax.bar(x - 0.19, 100 * np.array(a1['w0']), 0.36, color=MainBlue, label='Base day (weights of $D_0$)')
    ax.bar(x + 0.19, 100 * np.array(a1['w1']), 0.36, color=Orange, label='After the reallocation (weights of $D_1$)')
    for i in range(3):
        ax.text(x[i] - 0.19, 100 * a1['w0'][i] + 1.5, f"{100 * a1['w0'][i]:.1f}", ha='center', fontsize=7, color='black')
        ax.text(x[i] + 0.19, 100 * a1['w1'][i] + 1.5, f"{100 * a1['w1'][i]:.1f}", ha='center', fontsize=7, color='black')
    ax.set_xticks(x)
    ax.set_xticklabels([f"Coin {c}: return {100 * r:+.0f}%" for c, r in zip('ABC', a1['rets'])], fontsize=8)
    ax.set_ylabel('Index weight (%)')
    ax.set_ylim(0, 90)
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch16_sem_a1_index')


def fig_sem_a3(a3, x=1000.0, y=3_000_000.0, P=3300.0, fee=0.003):
    """A3: arbitrage profit pi(dy) = P [x - k/(y + gamma dy)] - dy, with and without a fee; the optimum is marked."""
    k = x * y
    dy = np.linspace(0, 300_000, 400)
    fig, ax = plt.subplots(figsize=(5.8, 2.8))
    for g, c, lab in [(1 - fee, MainBlue, 'Fee 0.3%'), (1.0, Orange, 'No fee')]:
        prof = P * (x - k / (y + g * dy)) - dy
        ax.plot(dy / 1000, prof / 1000, color=c, lw=1.6, label=f'{lab}: profit of buying Ether with $\\Delta y$')
    ax.scatter([a3['dy'] / 1000], [a3['profit'] / 1000], color=IDAred, s=26, zorder=3,
               label=f"Optimum with fee: $\\Delta y^*$ = {a3['dy'] / 1000:.1f}k, profit {a3['profit']:,.0f} USD")
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('USD Coin paid into the pool, $\\Delta y$ (thousand)')
    ax.set_ylabel('Profit (thousand USD)')
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    save_fig('ch16_sem_a3_profit')


def fig_sem_a5():
    """A5: impermanent loss IL_w(r) for w = 0.5 and 0.8, with the second-order approximation."""
    r = np.exp(np.linspace(np.log(0.2), np.log(5), 400))
    fig, ax = plt.subplots(figsize=(5.8, 2.8))
    for w, c in [(0.5, MainBlue), (0.8, Orange)]:
        ax.plot(r, 100 * il_weighted(r, w), color=c, lw=1.7, label=f'Exact, w = {w}')
        ax.plot(r, 100 * (np.exp(-w * (1 - w) * np.log(r) ** 2 / 2) - 1), color=c, lw=1.1, ls='--',
                label=f'Second-order approximation, w = {w}')
        for rr in [2.0, 4.0]:
            ax.scatter([rr], [100 * il_weighted(rr, w)], color=c, s=18, zorder=3)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xscale('log')
    ax.set_xticks([0.25, 0.5, 1, 2, 4])
    ax.set_xticklabels(['0.25', '0.5', '1', '2', '4'])
    ax.set_xlabel('Price ratio $r = P_1/P_0$ (log scale)')
    ax.set_ylabel('Impermanent loss (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch16_sem_a5_il')


def fig_sem_a7(tar, d0=285.0):
    """A7: deterministic path of |d_t| from 285 bp: phi_out outside the band, phi_in inside; band c."""
    d, path = d0, [d0]
    for _ in range(10):
        d = d * (tar['phi_out'] if d > tar['c'] else tar['phi_in'])
        path.append(d)
    path = np.array(path)
    fig, ax = plt.subplots(figsize=(5.8, 2.7))
    t = np.arange(len(path))
    ax.plot(t, path, color=MainBlue, lw=1.4, marker='o', ms=4, label='Deterministic path of $|d_t|$ ($\\varepsilon_t = 0$), bp')
    ax.axhline(tar['c'], color=IDAred, lw=1.2, ls='--', label=f"Band edge $\\hat c$ = {tar['c']:.2f} bp")
    ax.set_yscale('log')
    ax.set_xlabel('Days after the close of 11 March 2023')
    ax.set_ylabel('Deviation from 1 USD (bp, log scale)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch16_sem_a7_path')


def fig_sem_b2(S):
    """B2: annualised volatility with bootstrap CI and the weekend / weekday ratio before and after the ETFs."""
    rows = [('Bitcoin', S['B1']), ('Ether', S['B2']['ETH']), ('Solana', S['B2']['SOL'])]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    x = np.arange(3)
    v = np.array([b['vol'] for _, b in rows])
    lo = np.array([b['vol_lo'] for _, b in rows])
    hi = np.array([b['vol_hi'] for _, b in rows])
    axes[0].bar(x, v, 0.55, color=[Orange, Purple, Teal], yerr=[v - lo, hi - v], capsize=3,
                error_kw=dict(ecolor='black', lw=0.8))
    for i, (_, b) in enumerate(rows):
        axes[0].text(i, hi[i] + 3, f"{b['vol']:.0f}%\n{b['ratio']:.1f}x S&P 500", ha='center', fontsize=7, color='black')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([n for n, _ in rows])
    axes[0].set_ylabel('Annualised volatility (%)')
    axes[0].set_ylim(0, 165)
    for j, (per, c, lab) in enumerate([('pre', MainBlue, 'Before 11 Jan 2024'), ('post', Orange, 'From 11 Jan 2024')]):
        m = np.array([b[f'wr_{per}'] for _, b in rows])
        l_ = np.array([b[f'wr_{per}_lo'] for _, b in rows])
        h_ = np.array([b[f'wr_{per}_hi'] for _, b in rows])
        axes[1].bar(x + (j - 0.5) * 0.36, m, 0.34, color=c, yerr=[m - l_, h_ - m], capsize=3,
                    error_kw=dict(ecolor='black', lw=0.8), label=lab)
    axes[1].axhline(1, color=Gray, lw=0.7, ls='--')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([n for n, _ in rows])
    axes[1].set_ylabel('Weekend / weekday variance')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_sem_b2_vol')


def fig_sem_b4(S):
    """B4: threshold-AR slopes inside and outside the band, with 95% intervals, for Tether, USD Coin, Dai."""
    rows = [('Tether', S['B4']['USDT']['full']), ('USD Coin', S['B3']['full']), ('Dai', S['B4']['DAI']['full'])]
    fig, ax = plt.subplots(figsize=(5.8, 2.8))
    x = np.arange(3)
    for j, (k, c, lab) in enumerate([('in', MainBlue, 'Inside the band, $\\hat\\phi_{in}$'),
                                     ('out', IDAred, 'Outside the band, $\\hat\\phi_{out}$')]):
        m = np.array([t[f'phi_{k}'] for _, t in rows])
        se = np.array([t[f'se_{k}'] for _, t in rows])
        ax.bar(x + (j - 0.5) * 0.36, m, 0.34, color=c, yerr=1.96 * se, capsize=3,
               error_kw=dict(ecolor='black', lw=0.8), label=lab)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}\n$\\hat c$ = {t['c']:.1f} bp, bootstrap p = {t['p_boot']:.3f}" for n, t in rows], fontsize=7.5)
    ax.set_ylabel('AR slope (95% interval)')
    ax.set_ylim(0, 1.05)
    legend_outside_bottom(ax, ncol=2, y=-0.3)
    save_fig('ch16_sem_b4_tar')


def fig_sem_b56(etf, coin, name):
    """B5 / B6: log of the ETF / coin price ratio (in %, relative to the first day) with the estimated trend and
    the trend implied by the fee of 0.25% a year."""
    p = pd.concat([price(etf), price(coin)], axis=1, join='inner').dropna()
    lr = 100 * np.log(p[etf] / p[coin])
    lr = lr - lr.iloc[0]
    t = (lr.index - lr.index[0]).days / 365.25
    b, a = np.polyfit(t, lr.values, 1)
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    ax.plot(lr.index, lr.values, color=MainBlue, lw=0.6, alpha=0.8, label=f'$\\ell_t$ = ln({etf} / {coin} price), change since day 1 (%)')
    ax.plot(lr.index, lr.rolling(20).mean().values, color=Teal, lw=1.3, label='20-day moving average of $\\ell_t$')
    ax.plot(lr.index, a + b * t, color=IDAred, lw=1.6, label=f'Fitted trend: {b:.3f}% a year')
    ax.plot(lr.index, a - 0.25 * t, color=Forest, lw=1.2, ls='--', label='Slope of the 0.25% sponsor fee')
    ax.set_ylabel('%')
    ax.tick_params(axis='x', labelsize=8)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig(name)


def fig_sem_b78(key, b, name):
    """B7 / B8: Wald statistic W(tau) for a break in all coefficients, at each candidate week."""
    w = 100 * joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc['2021-04-16':END]
    X = np.column_stack([np.ones(len(w)), w['BTC'].values, w['SPX'].values])
    sw = I.sup_wald(w[key].values, X, w.index)
    Wser = pd.Series(sw['W'], index=w.index).dropna()
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    ax.plot(Wser.index, Wser.values, color=MainBlue, lw=1.2, label='$W(\\tau)$, HAC, break in $(a, \\beta_{BTC}, \\beta_{SPX})$')
    ax.axhline(b['sw']['cv5'], color=IDAred, lw=1.1, ls='--', label=f"5% critical value of sup W: {b['sw']['cv5']:.2f}")
    d = pd.Timestamp(b['sw']['date'])
    ax.axvspan(pd.Timestamp(b['sw']['ci_lo']), pd.Timestamp(b['sw']['ci_hi']), color=Amber, alpha=0.2,
               label=f"Break date {d.strftime('%d %b %Y')} and 95% interval")
    ax.axvline(d, color=Amber, lw=1.2)
    ax.axvline(pd.Timestamp(ETF_START), color=Forest, lw=1.1, ls=':', label='Spot ETF launch, 11 Jan 2024')
    ax.set_ylabel('Wald statistic')
    ax.tick_params(axis='x', labelsize=8)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig(name)
    return float(np.nanmax(sw['W']))


def fig_sem_c2(c2):
    """C2: Bitcoin's volatility and Sharpe ratio after each correction of the AI answer."""
    labs = ['AI answer\n(252, log returns, $r_f$ = 5%)', 'Annualised with 365\n(same $r_f$)',
            'Corrected\n(365, simple returns, T-bill $r_f$)']
    vol = [c2['sd252'], c2['sd365'], c2['sd_s']]
    sh = [c2['sh252'], c2['sh365'], c2['sh_s']]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))
    x = np.arange(3)
    axes[0].bar(x, vol, 0.55, color=[IDAred, Amber, Forest])
    axes[1].bar(x, sh, 0.55, color=[IDAred, Amber, Forest])
    for i in range(3):
        axes[0].text(i, vol[i] + 1, f'{vol[i]:.1f}%', ha='center', fontsize=7.5, color='black')
        axes[1].text(i, sh[i] + 0.01, f'{sh[i]:.2f}', ha='center', fontsize=7.5, color='black')
    for ax, yl in [(axes[0], 'Annualised volatility (%)'), (axes[1], 'Sharpe ratio')]:
        ax.set_xticks(x)
        ax.set_xticklabels(labs, fontsize=6.5)
        ax.set_ylabel(yl)
    axes[0].set_ylim(0, 70)
    axes[1].set_ylim(0, 0.75)
    fig.tight_layout()
    save_fig('ch16_sem_c2_correction')


def make_solution_charts(S):
    """All new charts of the solutions, from the saved numbers (sem16_results.json) and the local data."""
    fig_sem_a1(S['A1'])
    fig_sem_a3(S['A3'])
    fig_sem_a5()
    fig_sem_a7(S['B3']['full'])
    fig_sem_b2(S)
    fig_sem_b4(S)
    fig_sem_b56('IBIT', 'BTC', 'ch16_sem_b5_ratio')
    fig_sem_b56('ETHA', 'ETH', 'ch16_sem_b6_ratio')
    for key, lab, name in [('MSTR', 'B7', 'ch16_sem_b7_break'), ('COIN', 'B8', 'ch16_sem_b8_break')]:
        m = fig_sem_b78(key, S[lab], name)
        assert abs(m - S[lab]['sw']['sup_w']) < 1e-6, (lab, m, S[lab]['sw']['sup_w'])
    fig_sem_c2(S['C2'])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--charts':
        with open(os.path.join(HERE, 'sem16_results.json')) as fh:
            make_solution_charts(json.load(fh))
        sys.exit(0)
    print('Seminar 16')
    S = {}
    S['A1'], S['A2'], S['A3'], S['A4'] = a1_index(), a2_replace(), a3_band(), a4_weighted()
    S['A5'], S['A6'] = a5_il(), a6_lvr()
    b1 = b1_btc_facts('BTC')
    fig_sem_weekend(b1)
    S['B1'] = {k: v for k, v in b1.items() if not k.startswith('_')}
    S['B2'] = {k: {kk: vv for kk, vv in b1_btc_facts(k).items() if not kk.startswith('_')} for k in ['ETH', 'SOL']}
    S['B3'] = b3_usdc('USDC')
    fig_sem_usdc(S['B3']['full'])
    S['A7'], S['A8'] = a7_tar(S['B3']['full']), a8_mix(S['B3']['full'])
    S['B4'] = {k: b3_usdc(k) for k in ['USDT', 'DAI']}
    S['B5'] = b5_etf('IBIT', 'BTC')
    S['B6'] = b5_etf('ETHA', 'ETH')
    S['B7'] = b7_equity('MSTR')
    S['B8'] = b7_equity('COIN')
    c1 = c1_hedge()
    fig_sem_hedge(c1)
    S['C1'] = c1
    S['C2'] = c2_ai()
    S['C3'] = c3_ltw()
    with open(os.path.join(HERE, 'sem16_results.json'), 'w') as fh:
        json.dump(jsonable(S), fh, indent=1)
    print('saved sem16_results.json')
    make_solution_charts(json.loads(json.dumps(jsonable(S))))

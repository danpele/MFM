"""
predictability.py -- Extensii de nivel master pentru Capitolul 2 (MFM)
======================================================================
  * predictive_regression  -- r_{t+1} = a + b dp_t + u, dp_{t+1} = c + rho dp_t + v (Stambaugh, 1999)
  * oos_r2                 -- R^2 in afara selectiei fata de media istorica (Welch & Goyal, 2008),
                              testul MSPE-ajustat Clark & West (2007), restrictiile Campbell & Thompson (2008)
  * local_whittle          -- estimatorul Whittle local al lui d = H - 0,5 (Robinson, 1995)
  * el_autoportmanteau     -- testul portmanteau automat, robust la heteroscedasticitate (Escanciano & Lobato, 2009)
  * event_study_bank_tax   -- TLV si BRD, 19 dec. 2018: dispersia erorii de predictie, portofoliu vs independenta
  * stepm_calendar         -- Romano & Wolf (2005) StepM pe cele 15 teste de calendar (bootstrap pe blocuri de luni)
  * amh_regression         -- z*(5) pe ferestre mobile explicat prin volatilitate si crize (erori HAC)

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import log_returns, read_market, sp500_monthly, fred, complete_months   # noqa: E402
from eff_tests import variance_ratio, rolling_stat                    # noqa: E402
from generate_all_charts import plt, MainBlue, IDAred, Gray, save_fig   # noqa: E402  (stilul MFM)

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42


# =============================================================================
# 1. REGRESIA PREDICTIVA SI DEPLASAREA STAMBAUGH
# =============================================================================
def monthly_data(start='1934-01-31', end='2026-08-31'):
    """S&P 500 monthly excess log return (with dividends) and log D/P at the end of the previous month."""
    d = sp500_monthly(end)
    rf = fred('TB3MS') / 100                                   # annualised 3-month T-bill rate
    r = np.log((d['P'] + d['D'] / 12) / d['P'].shift(1))
    rf_m = np.log(1 + rf / 12).reindex(d.index).shift(1)       # known at the start of the month
    out = pd.DataFrame({'ex': r - rf_m, 'dp': np.log(d['D'] / d['P'])})
    out['dp_lag'] = out['dp'].shift(1)
    return out.loc[start:end].dropna(), d.attrs


def predictive_regression(df, nw_lags=12):
    """OLS with Newey-West errors, AR(1) regression of the predictor, innovation correlation and the Stambaugh correction."""
    y, x = df['ex'].values, df['dp_lag'].values
    X = sm.add_constant(x)
    ols = sm.OLS(y, X).fit()
    hac = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': nw_lags})
    ar = sm.OLS(df['dp'].values, X).fit()                      # dp_t on dp_{t-1}
    u, v = ols.resid, ar.resid
    T = len(y)
    rho = ar.params[1]
    s_uv, s_vv = np.cov(u, v)[0, 1], np.var(v, ddof=1)
    bias_rho = -(1 + 3 * rho) / T                               # Kendall (1954)
    bias_beta = s_uv / s_vv * bias_rho                          # Stambaugh (1999)
    return dict(T=T, start=str(df.index[0].date()), end=str(df.index[-1].date()),
                beta=ols.params[1], se_ols=ols.bse[1], t_ols=ols.tvalues[1], se_nw=hac.bse[1], t_nw=hac.tvalues[1],
                r2=ols.rsquared, rho=rho, corr_uv=np.corrcoef(u, v)[0, 1], ratio_uv=s_uv / s_vv,
                bias_rho=bias_rho, bias_beta=bias_beta, beta_adj=ols.params[1] - bias_beta,
                t_adj=(ols.params[1] - bias_beta) / hac.bse[1])


def simulate_stambaugh(rho, corr_uv, T, n_sim=2000, seed=SEED):
    """Bias of beta and size of the 5% t-test when beta = 0 (persistent predictor, correlated innovations)."""
    rng = np.random.default_rng(seed)
    betas, rej = [], 0
    for _ in range(n_sim):
        e = rng.multivariate_normal([0, 0], [[1, corr_uv], [corr_uv, 1]], T + 1)
        x = np.zeros(T + 1)
        for t in range(1, T + 1):
            x[t] = rho * x[t - 1] + e[t, 1]
        y = e[1:, 0]                                             # beta = 0
        f = sm.OLS(y, sm.add_constant(x[:-1])).fit()
        betas.append(f.params[1] / 1.0)
        rej += abs(f.tvalues[1]) > 1.96
    return dict(mean_beta=float(np.mean(betas)), size=rej / n_sim)


def oos_r2(df, oos_start='1970-01-31', nw_lags=12):
    """Recursive (expanding-window) forecasts: predictive regression vs historical mean.
    R2_OS (Welch-Goyal), Clark-West, and the version with Campbell-Thompson restrictions."""
    rows = []
    idx = df.index
    first = idx.get_loc(idx[idx >= oos_start][0])
    for i in range(first, len(df)):
        est = df.iloc[:i]
        b = np.polyfit(est['dp_lag'], est['ex'], 1)
        f_pred = b[1] + b[0] * df['dp_lag'].iloc[i]
        f_ct = max(b[1] + max(b[0], 0.0) * df['dp_lag'].iloc[i], 0.0) if b[0] > 0 else max(est['ex'].mean(), 0.0)
        rows.append((idx[i], df['ex'].iloc[i], est['ex'].mean(), f_pred, f_ct))
    o = pd.DataFrame(rows, columns=['date', 'y', 'mean', 'pred', 'ct']).set_index('date')
    e0, e1, e2 = o['y'] - o['mean'], o['y'] - o['pred'], o['y'] - o['ct']
    r2 = 1 - (e1 ** 2).sum() / (e0 ** 2).sum()
    r2_ct = 1 - (e2 ** 2).sum() / (e0 ** 2).sum()
    f = e0 ** 2 - (e1 ** 2 - (o['mean'] - o['pred']) ** 2)            # Clark-West
    cw = sm.OLS(f.values, np.ones(len(f))).fit(cov_type='HAC', cov_kwds={'maxlags': nw_lags})
    dm = sm.OLS((e0 ** 2 - e1 ** 2).values, np.ones(len(f))).fit(cov_type='HAC', cov_kwds={'maxlags': nw_lags})
    o['cum_dsse'] = (e0 ** 2 - e1 ** 2).cumsum()
    o['cum_dsse_ct'] = (e0 ** 2 - e2 ** 2).cumsum()
    sr_m = df['ex'].mean() / df['ex'].std()                       # unconditional monthly Sharpe ratio
    binds = float(((o['ct'] - o['pred']).abs() > 1e-12).mean())       # how often the restrictions bind
    ct_gain = lambda r2_: r2_ / (1 - r2_) * (1 + sr_m ** 2) / sr_m ** 2
    return o, dict(n=len(o), start=str(o.index[0].date()), r2=r2, r2_ct=r2_ct, cw_t=cw.tvalues[0],
                   cw_p=1 - stats.norm.cdf(cw.tvalues[0]), dm_t=dm.tvalues[0], sr_m=sr_m,
                   gain_05=ct_gain(0.005), ct_binds=binds, gain_ct=ct_gain(r2_ct) if r2_ct > 0 else float('nan'))


def fig_oos(o):
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(o.index, o['cum_dsse'], color=IDAred, lw=1.0, label='Predictive regression on log D/P vs historical mean')
    ax.axhline(0, color=Gray, lw=0.7, ls='--')
    ax.set_ylabel('Cumulative reduction in squared\nforecast errors vs historical mean')
    ax.set_title('Out-of-sample: does the dividend-price ratio beat the historical mean? (S&P 500, monthly)',
                 fontsize=9, loc='left')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=1, frameon=False)
    plt.tight_layout()
    save_fig('ch2_oos_dp')


# =============================================================================
# 2. MEMORIE LUNGA: WHITTLE LOCAL
# =============================================================================
def local_whittle(x, m):
    """d estimated by minimising the local Whittle function (Robinson, 1995); asymptotic SE 1/(2 sqrt(m))."""
    x = np.asarray(x, dtype=float)
    T = len(x)
    w = np.fft.fft(x - x.mean())
    lam = 2 * np.pi * np.arange(1, m + 1) / T
    I = np.abs(w[1:m + 1]) ** 2 / (2 * np.pi * T)
    from scipy.optimize import minimize_scalar
    R = lambda d: np.log(np.mean(lam ** (2 * d) * I)) - 2 * d * np.mean(np.log(lam))
    d = minimize_scalar(R, bounds=(-0.49, 0.99), method='bounded').x
    return d, 1 / (2 * np.sqrt(m))


# =============================================================================
# 3. TESTUL PORTMANTEAU AUTOMAT (ESCANCIANO-LOBATO)
# =============================================================================
def el_autoportmanteau(x, d_max=10, q=2.4):
    """AQ = T sum_{j<=p~} rho~_j^2 with rho~_j^2 = gamma_j^2 / tau_j (robust); p~ chosen from the data; AQ ~ chi2(1)."""
    y = np.asarray(x, dtype=float)
    T = len(y)
    e = y - y.mean()
    g0 = (e ** 2).mean()
    rt = []
    rho_raw = []
    for j in range(1, d_max + 1):
        gj = (e[j:] * e[:-j]).sum() / (T - j)
        tj = (e[j:] ** 2 * e[:-j] ** 2).sum() / (T - j)
        rt.append(gj ** 2 / tj)
        rho_raw.append(gj / g0)
    rt = np.array(rt)
    Q = T * np.cumsum(rt)
    p = np.arange(1, d_max + 1)
    pen = p * np.log(T) if np.sqrt(T * np.max(rt)) <= np.sqrt(q * np.log(T)) else 2 * p   # switch based on the robust correlations
    L = Q - pen
    pt = int(p[np.argmax(L)])
    AQ = Q[pt - 1]
    return AQ, pt, 1 - stats.chi2.cdf(AQ, 1)


# =============================================================================
# 4. STUDIU DE EVENIMENT: TAXA BANCARA, TLV SI BRD
# =============================================================================
def event_study_bank_tax(event='2018-12-19', est=(-250, -11), win=(0, 5)):
    """Market model on [-250, -11]; abnormal returns with the prediction-error variance; portfolio test vs independence."""
    px = pd.concat({'TLV': read_market('TLV.RO')['adjusted_close'], 'BRD': read_market('BRD.RO')['adjusted_close'],
                    'BET': read_market('BET')['close']}, axis=1).dropna()        # align prices on common trading days
    px = px[px.index.dayofweek < 5]
    r = np.log(px).diff().dropna()
    t0 = r.index.get_loc(pd.Timestamp(event))
    E = r.iloc[t0 + est[0]:t0 + est[1] + 1]
    W = r.iloc[t0 + win[0]:t0 + win[1] + 1]
    rm, mu_m, var_m, T0 = W['BET'], E['BET'].mean(), E['BET'].var(ddof=1), len(E)
    out, resid = {}, {}
    for k in ['TLV', 'BRD', 'PORT']:
        yE = E[['TLV', 'BRD']].mean(axis=1) if k == 'PORT' else E[k]
        yW = W[['TLV', 'BRD']].mean(axis=1) if k == 'PORT' else W[k]
        f = sm.OLS(yE, sm.add_constant(E['BET'])).fit()
        s2 = f.mse_resid
        resid[k] = f.resid
        ar = yW - f.params['const'] - f.params['BET'] * rm
        pe = s2 * (1 + 1 / T0 + (rm - mu_m) ** 2 / ((T0 - 1) * var_m))          # prediction-error variance
        car = ar.sum()
        # CAR: sum of prediction variances + covariance induced by parameter estimation (MacKinlay, 1997)
        Xs = np.column_stack([np.ones(len(rm)), rm.values])
        XE = np.column_stack([np.ones(T0), E['BET'].values])
        V = s2 * (np.eye(len(rm)) + Xs @ np.linalg.inv(XE.T @ XE) @ Xs.T)
        out[k] = dict(beta=f.params['BET'], sigma=np.sqrt(s2), ar0=ar.iloc[0], t0_naive=ar.iloc[0] / np.sqrt(s2),
                      t0=ar.iloc[0] / np.sqrt(pe.iloc[0]), infl0=pe.iloc[0] / s2, car=car,
                      t_car=car / np.sqrt(V.sum()), t_car_naive=car / np.sqrt(s2 * len(rm)),
                      var_car=V.sum(), car_post=ar.iloc[1:].sum(), t_car_post=ar.iloc[1:].sum() / np.sqrt(V[1:, 1:].sum()))
    rbar = np.corrcoef(resid['TLV'], resid['BRD'])[0, 1]
    # joint test assuming independence: mean AR0 / (sqrt(s1^2 + s2^2)/2)
    # under independence: the same prediction-error variances as for the portfolio, no covariance between firms
    s_ind = np.sqrt(out['TLV']['sigma'] ** 2 * out['TLV']['infl0'] + out['BRD']['sigma'] ** 2 * out['BRD']['infl0']) / 2
    ar0_mean = (out['TLV']['ar0'] + out['BRD']['ar0']) / 2
    car_mean = (out['TLV']['car'] + out['BRD']['car']) / 2
    s_car_ind = np.sqrt(out['TLV']['var_car'] + out['BRD']['var_car']) / 2
    return dict(event=event, rm0=float(rm.iloc[0]), T0=T0, rbar=rbar, firms=out,
                ar0_mean=ar0_mean, t_indep=ar0_mean / s_ind, t_port=out['PORT']['t0'],
                car_mean=car_mean, tcar_indep=car_mean / s_car_ind, tcar_port=out['PORT']['t_car'],
                kp_factor=np.sqrt((1 - rbar) / (1 + rbar)),
                varmean10=1 + 9 * rbar,                       # Var(mean of 10 ARs) / Var under independence
                kp_inflation10=(1 + 9 * rbar) / (1 - rbar))  # overstatement of the variance of the cross-sectional statistic


# =============================================================================
# 5. STEPM (ROMANO-WOLF) PE CELE 15 TESTE DE CALENDAR
# =============================================================================
CAL_MARKETS = ['sp500', 'bet', 'stoxx', 'wig20', 'bux']


def _nw_se(X, u, L=5):
    """Newey-West covariance matrix (Bartlett kernel, L lags) for OLS."""
    T = len(u)
    Xu = X * u[:, None]
    S = Xu.T @ Xu / T
    for j in range(1, L + 1):
        G = Xu[j:].T @ Xu[:-j] / T
        S += (1 - j / (L + 1)) * (G + G.T)
    XX = np.linalg.inv(X.T @ X / T)
    return XX @ S @ XX / T


def _cal_est(r, dow, month):
    """Estimates and HAC covariances of the 3 effects for one market.
    dow: weekday of each observation; month: integer month label, (block or year) * 100 + month."""
    D = np.column_stack([(dow == d).astype(float) for d in range(5)])
    grp = pd.Series(np.arange(len(r))).groupby(month)
    rank = grp.cumcount().values
    rank_end = grp.cumcount(ascending=False).values
    tom = ((rank < 3) | (rank_end == 0)).astype(float)
    bd = np.linalg.lstsq(D, r, rcond=None)[0]
    Vd = _nw_se(D, r - D @ bd, 5)
    X = np.column_stack([np.ones(len(r)), tom])
    bt = np.linalg.lstsq(X, r, rcond=None)[0]
    Vt = _nw_se(X, r - X @ bt, 5)
    ms = np.expm1(pd.Series(r).groupby(month).sum())          # simple monthly returns, as in january_regression
    jan = (np.asarray(ms.index) % 100 == 1).astype(float)
    Xm = np.column_stack([np.ones(len(ms)), jan])
    bj = np.linalg.lstsq(Xm, ms.values, rcond=None)[0]
    Vj = _nw_se(Xm, ms.values - Xm @ bj, 3)
    return dict(dow=(bd, Vd), tom=(bt[1], Vt[1, 1]), jan=(bj[1], Vj[1, 1]))


_R = np.column_stack([np.ones(4), -np.eye(4)])


def _cal_p(est, center=None):
    """p-values: Wald (4 df) for the day of the week, two-sided z for January and TOM.
    center: the estimates on the original data (bootstrap statistic centred, as in Romano-Wolf)."""
    out = {}
    bd, Vd = est['dow']
    d = _R @ (bd - (center['dow'][0] if center else 0))
    out['dow'] = 1 - stats.chi2.cdf(float(d @ np.linalg.solve(_R @ Vd @ _R.T, d)), 4)
    for e in ['jan', 'tom']:
        b, v = est[e]
        z = (b - (center[e][0] if center else 0)) / np.sqrt(v)
        out[e] = 2 * (1 - stats.norm.cdf(abs(z)))
    return out


def stepm_calendar(n_boot=999, block=3, alpha=0.05, seed=SEED):
    """Romano-Wolf StepM with the min-p statistic: the SAME blocks of calendar months are resampled for
    all markets (keeps the dependence across markets and the calendar structure within the month);
    the bootstrap statistics are centred at the original estimates."""
    rets = {k: complete_months(log_returns(k)) for k in CAL_MARKETS}
    months = pd.period_range('2000-01', max(r.index[-1] for r in rets.values()).to_period('M'), freq='M')
    orig, p0, pos = {}, {}, {}
    for k, r in rets.items():
        mlab = r.index.to_period('M')
        orig[k] = _cal_est(r.values, r.index.dayofweek.values, r.index.year.values * 100 + r.index.month.values)
        for e, pv in _cal_p(orig[k]).items():
            p0[(k, e)] = pv
        pos[k] = {m: np.where(mlab == m)[0] for m in months}
    keys = [(k, e) for k in CAL_MARKETS for e in ['dow', 'jan', 'tom']]
    mnum = np.array([m.month for m in months])
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(len(months) / block))
    boot_p = np.zeros((n_boot, len(keys)))
    for b in range(n_boot):
        starts = rng.integers(0, len(months) - block + 1, nb)
        msel = np.concatenate([np.arange(s0, s0 + block) for s0 in starts])[:len(months)]
        for k, r in rets.items():
            parts = [pos[k][months[m]] for m in msel]
            idx = np.concatenate(parts)
            lab = np.concatenate([np.full(len(pp), j) for j, pp in enumerate(parts)])
            newlab = lab * 100 + mnum[msel][lab]          # label = block position * 100 + original month
            est = _cal_est(r.values[idx], r.index.dayofweek.values[idx], newlab)
            for e, pv in _cal_p(est, orig[k]).items():
                boot_p[b, keys.index((k, e))] = pv
    p = np.array([p0[k] for k in keys])
    active = np.ones(len(keys), bool)
    rejected = np.zeros(len(keys), bool)
    steps = []
    while active.any():
        crit = np.quantile(boot_p[:, active].min(axis=1), alpha)
        new = active & (p <= crit)
        steps.append(float(crit))
        if not new.any():
            break
        rejected |= new
        active &= ~new
    holm = np.zeros(len(keys), bool)
    for i, ix in enumerate(np.argsort(p)):
        if p[ix] < alpha / (len(p) - i):
            holm[ix] = True
        else:
            break
    return pd.DataFrame({'market': [k for k, _ in keys], 'effect': [e for _, e in keys], 'p': p,
                         'holm_reject': holm, 'stepm_reject': rejected,
                         'boot_size5': (boot_p < 0.05).mean(axis=0)}), steps


# =============================================================================
# 6. AMH TESTAT: z*(5) PE FERESTRE MOBILE, EXPLICAT PRIN VOLATILITATE SI CRIZE
# =============================================================================
def amh_regression(k, window=500, step=21):
    r = log_returns(k)
    z = rolling_stat(r, lambda x: variance_ratio(x, 5)[2], window, step)
    vol = rolling_stat(r, lambda x: np.std(x, ddof=1) * np.sqrt(252), window, step)
    starts = [r.index[r.index.get_loc(d) - window + 1] for d in z.index]
    crisis = [((s <= pd.Timestamp('2009-06-30')) & (e >= pd.Timestamp('2008-09-01'))) |
              ((s <= pd.Timestamp('2020-06-30')) & (e >= pd.Timestamp('2020-02-15'))) for s, e in zip(starts, z.index)]
    X = sm.add_constant(pd.DataFrame({'vol': 100 * vol.values, 'crisis': np.array(crisis, float)}))
    f = sm.OLS(z.values, X).fit(cov_type='HAC', cov_kwds={'maxlags': int(np.ceil(window / step))})
    return dict(n=len(z), b_vol=f.params['vol'], t_vol=f.tvalues['vol'], b_crisis=f.params['crisis'],
                t_crisis=f.tvalues['crisis'], r2=f.rsquared, lags=int(np.ceil(window / step)))


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    return o


if __name__ == '__main__':
    from mfm_data import MARKETS
    N = {}
    df, attrs = monthly_data()
    N['splice'] = attrs
    N['pred'] = predictive_regression(df)
    N['pred_sim'] = simulate_stambaugh(N['pred']['rho'], N['pred']['corr_uv'], 360)
    o, N['oos'] = oos_r2(df)
    fig_oos(o)
    o.to_csv(os.path.join(HERE, 'ch2_oos_dp.csv'))
    N['lw'] = {}
    N['el'] = {}
    for k in MARKETS:
        r = log_returns(k)
        T = len(r)
        N['lw'][k] = {str(a): list(local_whittle(r.values, int(T ** a))) + [int(T ** a)] for a in (0.5, 0.65)}
        N['el'][k] = list(el_autoportmanteau(r.values))
    N['event'] = event_study_bank_tax()
    N['amh'] = {k: amh_regression(k) for k in ['sp500', 'bet']}
    sm_tab, steps = stepm_calendar()
    sm_tab.to_csv(os.path.join(HERE, 'ch2_stepm_calendar.csv'), index=False)
    N['stepm'] = dict(n_reject=int(sm_tab['stepm_reject'].sum()), steps=steps,
                      rejected=[f"{a}/{b}" for a, b in sm_tab.loc[sm_tab['stepm_reject'], ['market', 'effect']].values],
                      size5=sm_tab.groupby('effect')['boot_size5'].mean().to_dict())
    N = _clean(N)
    with open(os.path.join(HERE, 'ch2_level_numbers.json'), 'w') as f:
        json.dump(N, f, indent=1)
    print(json.dumps(N, indent=1)[:6000])

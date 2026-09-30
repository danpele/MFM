"""
seminar9.py -- calculele Seminarului 9 (MFM): volatilitate realizata
====================================================================
Partea A: exercitii pas cu pas (RV, BV, zgomot, TSRV, HAR, QLIKE/MSE, DM).
Partea B: SPY si Bitcoin, bare de 5 minute: salturi, frecventa de esantionare, randamente standardizate,
HAR in esantion, prognoze pe 5 zile, HAR-CJ, asprimea volatilitatii.
Partea C: este volatilitatea Bitcoin mai previzibila decat a SPY? (analiza de referinta pentru profesor)
Cifrele sunt salvate in sem9_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_data as M                                                           # noqa: E402
import rv_tools as T                                                           # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Black, LightGray,  # noqa: E402
                                 save_fig, legend_outside_bottom, fig_legend_bottom, jsonable, ann, rough_H,
                                 P_SPY, R_SPY, ON, OC, RV_SPY, RVT_SPY, P_BTC, R_BTC, RV_BTC, D_SPY, D_BTC, SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
B_BOOT = 2000
C_START = '2025-03-01'


# =============================================================================
# PART A
# =============================================================================
A1_R = np.array([0.08, -0.15, 0.03, 0.10, -0.04, 0.12])


def a1_rv_bv(r=A1_R):
    """RV, BV and the share of variation not captured by BV for six 5-minute returns (%)."""
    M_ = len(r)
    v = np.sum(r ** 2)
    s = np.sum(np.abs(r[1:]) * np.abs(r[:-1]))
    b = (np.pi / 2) * M_ / (M_ - 1) * s
    sparse = np.sum(np.array([r[:3].sum(), r[3:].sum()]) ** 2)
    return {'rv': v, 's': s, 'bv': b, 'ratio': (v - b) / v, 'sparse15': sparse,
            'vol_ann': np.sqrt(252 * v * 78 / M_), 'sq': list(r ** 2), 'prod': list(np.abs(r[1:]) * np.abs(r[:-1]))}


def a2_jump(r=A1_R):
    """The same returns, but the last one is a jump of -0.90%: RV, BV, ratio statistic."""
    x = r.copy()
    x[-1] = -0.90
    out = a1_rv_bv(x)
    M_ = len(x)
    a43 = np.abs(x) ** (4 / 3)
    tq = M_ * T.MU43 ** -3 * M_ / (M_ - 2) * np.sum(a43[2:] * a43[1:-1] * a43[:-2])
    theta = T.MU1 ** -4 + 2 * T.MU1 ** -2 - 5
    z = out['ratio'] / np.sqrt(theta / M_ * max(1, tq / out['bv'] ** 2))
    out.update({'tq': tq, 'theta': theta, 'z': z, 'crit': stats.norm.ppf(0.999), 'jump_part': out['rv'] - out['bv']})
    return out


def a3_noise(iv=1.0, omega=0.01):
    """Noise bias: E[RV] = IV + 2 n omega^2; optimal frequency n* = (IQ / (4 omega^4))^(1/3) with IQ = IV^2."""
    rows = {n: {'bias': 2 * n * omega ** 2, 'erv': iv + 2 * n * omega ** 2} for n in (78, 390, 23400)}
    nstar = (iv ** 2 / (4 * omega ** 4)) ** (1 / 3)
    return {'rows': rows, 'nstar': nstar, 'secs': 23400 / nstar, 'omega2': omega ** 2}


def a4_tsrv(rv_all=1.70, rv_avg=1.10, n=390, K=5, iv=1.0):
    """Less liquid BVB stock: omega = 0.03%; TSRV from the 1-minute RV and the average over 5 five-minute grids."""
    om = 0.03
    nbar = (n - K + 1) / K
    ts = rv_avg - nbar / n * rv_all
    return {'bias5': 2 * 78 * om ** 2, 'bias1': 2 * n * om ** 2, 'nstar': (iv ** 2 / (4 * om ** 4)) ** (1 / 3),
            'secs': 23400 / (iv ** 2 / (4 * om ** 4)) ** (1 / 3), 'nbar': nbar, 'ratio': nbar / n, 'tsrv': ts,
            'tsrv_adj': ts / (1 - nbar / n), 'omega2_hat': (rv_all - iv) / (2 * n)}


def a5_har(b=(-0.08, 0.36, 0.34, 0.17), d=np.log(2.0), w=np.log(1.2), m=np.log(0.9)):
    """log-HAR forecast for tomorrow; implied lag weights; persistence."""
    lf = b[0] + b[1] * d + b[2] * w + b[3] * m
    return {'lf': lf, 'f': np.exp(lf), 'w1': b[1] + b[2] / 5 + b[3] / 22, 'w2': b[2] / 5 + b[3] / 22, 'w6': b[3] / 22,
            'pers': b[1] + b[2] + b[3], 'geo_mean': np.exp(b[0] / (1 - sum(b[1:]))), 'd': d, 'w': w, 'm': m}


def a6_losses():
    """QLIKE and MSE for two forecasts over three days."""
    v = np.array([0.8, 1.5, 0.6])
    fa = np.array([1.0, 1.0, 1.0])
    fb = np.array([0.6, 1.6, 0.4])
    out = {}
    for k, f in [('A', fa), ('B', fb)]:
        q = v / f - np.log(v / f) - 1
        e = (v - f) ** 2
        out[k] = {'q': list(q), 'qm': q.mean(), 'e': list(e), 'em': e.mean()}
    # forecast 2 times too small vs 2 times too large (v = 1)
    out['under'] = 1 / 0.5 - np.log(1 / 0.5) - 1
    out['over'] = 1 / 2.0 - np.log(1 / 2.0) - 1
    out['under_mse'] = (1 - 0.5) ** 2
    out['over_mse'] = (1 - 2.0) ** 2
    return out


def a7_har2(b=(-0.08, 0.36, 0.34, 0.17), days=(2.0, 1.6, 1.3, 1.1, 1.0), m=0.9):
    """Two-day log-HAR forecast, iterated: tomorrow's forecast becomes the 'observed' value for the day after."""
    L = np.log(np.array(days))           # log RV over the last 5 days (today first)
    lm = np.log(m)
    f1 = b[0] + b[1] * L[0] + b[2] * L.mean() + b[3] * lm
    L2 = np.r_[f1, L[:4]]
    lm2 = (21 * lm + f1) / 22            # approximation: monthly mean updated with the new value
    f2 = b[0] + b[1] * f1 + b[2] * L2.mean() + b[3] * lm2
    return {'lw': L.mean(), 'f1': f1, 'F1': np.exp(f1), 'lw2': L2.mean(), 'lm2': lm2, 'f2': f2, 'F2': np.exp(f2), 'lm': lm}


def a8_dm(mean_d=-0.0327, se=0.0142, b=0.70, se_b=0.24, a=0.24, se_a=0.23):
    """DM statistic from the mean loss differential and its HAC standard error; separate MZ tests for a and b."""
    t = mean_d / se
    return {'t': t, 'p': 2 * stats.norm.sf(abs(t)), 'tb': (b - 1) / se_b, 'ta': a / se_a,
            'pb': 2 * stats.norm.sf(abs((b - 1) / se_b)), 'pa': 2 * stats.norm.sf(abs(a / se_a))}


# =============================================================================
# PART B
# =============================================================================
def b1_spy_jumps():
    """Jump test on SPY at three levels; time of the largest return on jump days."""
    j = T.jump_test(R_SPY)
    out = {'N': int(len(j))}
    for a, tag in [(0.05, '5'), (0.01, '1'), (0.001, '0_1')]:
        k = int((j['z'] > stats.norm.ppf(1 - a)).sum())
        out[f'n{tag}'] = k
        out[f'share{tag}'] = k / len(j)
        out[f'exp{tag}'] = a * len(j)
    jd = j[j['jump']].index
    slot = R_SPY.loc[jd].abs().idxmax(axis=1).astype(int)          # column 1..78 = interval ending at 09:30 + 5*col
    end = pd.Timestamp('2000-01-01 09:30') + pd.to_timedelta(5 * slot.values, unit='min')
    hours = pd.Series([t.strftime('%H:%M') for t in end], index=jd)
    at10 = float(np.mean([(t.hour == 10 and t.minute <= 5) for t in end]))
    at14 = float(np.mean([(t.hour == 14 and t.minute <= 5) or (t.hour == 14 and t.minute == 0) for t in end]))
    fig, ax = plt.subplots(figsize=(8.2, 3.0))
    mins = np.array([(t.hour - 9) * 60 + t.minute - 30 for t in end])
    ax.hist(mins, bins=np.arange(0, 391, 15), color=MainBlue, label='Days with a significant jump: time of the largest 5-minute return')
    ax.set_xticks([0, 30, 90, 150, 210, 270, 330, 390])
    ax.set_xticklabels(['09:30', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'])
    ax.set_ylabel('Number of days')
    legend_outside_bottom(ax, ncol=1, y=-0.15)
    save_fig('ch9_sem_jump_times')
    top = j.sort_values('z', ascending=False).head(3)
    out.update({'at10': at10, 'at14': at14, 'n_jump': int(len(jd)),
                'top': [{'date': str(d.date()), 'z': float(r['z']), 'jshare': float(r['J'] / r['rv']),
                         'time': hours[d]} for d, r in top.iterrows()],
                'jshare': float(j['J'].sum() / j['rv'].sum()), 'z_mean': float(j['z'].mean()), 'z_sd': float(j['z'].std())})
    return out


def b2_btc_jumps():
    """Jump test on Bitcoin; weekend days vs weekdays."""
    j = T.jump_test(R_BTC)
    wk = j.index.dayofweek >= 5
    return {'N': int(len(j)), 'n': int(j['jump'].sum()), 'share': float(j['jump'].mean()),
            'share_we': float(j.loc[wk, 'jump'].mean()), 'share_wd': float(j.loc[~wk, 'jump'].mean()),
            'jshare': float(j['J'].sum() / j['rv'].sum()), 'exp': 0.001 * len(j),
            'p_binom': float(stats.binomtest(int(j['jump'].sum()), len(j), 0.001, alternative='greater').pvalue),
            'bv_rv_we': float((j.loc[wk, 'bv'] / j.loc[wk, 'rv']).mean()),
            'bv_rv_wd': float((j.loc[~wk, 'bv'] / j.loc[~wk, 'rv']).mean()),
            'z_zero_share': float((R_BTC == 0).mean().mean())}


def b3_frequency():
    """SPY: RV at 5, 15, 30 and 65 minutes; block bootstrap for the ratio of means; predictive power."""
    base = RV_SPY
    out = {}
    fig, ax = plt.subplots(figsize=(8.2, 3.0))
    for k, col in [(1, MainBlue), (3, Forest), (6, Amber), (13, IDAred)]:
        v = T.sparse_rv(P_SPY, k)
        vs = T.subsampled_rv(P_SPY, k)
        ratio = v.mean() / base.mean()
        boot = T.block_bootstrap(np.c_[v.values, base.values], lambda x: x[:, 0].mean() / x[:, 1].mean(), 20, B_BOOT, SEED)
        lv = np.log(v)
        nxt = np.log(base).shift(-1)
        c = pd.concat([lv, nxt], axis=1).dropna().corr().iloc[0, 1]
        rel = np.log(v / base)
        out[str(5 * k)] = {'vol': float(ann(v.mean(), 252)), 'vol_sub': float(ann(vs.mean(), 252)), 'ratio': float(ratio),
                           'lo': float(np.percentile(boot, 2.5)), 'hi': float(np.percentile(boot, 97.5)),
                           'corr_next': float(c), 'sd_rel': float(rel.std()),
                           'corr_next_sub': float(pd.concat([np.log(vs), nxt], axis=1).dropna().corr().iloc[0, 1])}
        if k > 1:
            ax.hist(rel.clip(-2, 2), bins=np.linspace(-2, 2, 61), histtype='step', color=col, lw=1.3,
                    label=f'log(RV at {5 * k} min / RV at 5 min)')
    ax.set_xlabel('Log ratio to the 5-minute RV, same day')
    ax.set_ylabel('Number of days')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch9_sem_frequency')
    return out


def b4_standardised():
    """Returns standardised by RV (Andersen, Bollerslev, Diebold and Labys): kurtosis with a bootstrap interval."""
    out = {}
    btc_oc = 100 * np.log(P_BTC.iloc[:, -1] / P_BTC[0])
    for k, r, v in [('spy', OC, RV_SPY), ('btc', btc_oc, RV_BTC)]:
        z = (r / np.sqrt(v)).values
        u = (r / r.std()).values
        kz = T.block_bootstrap(z, lambda x: stats.kurtosis(x) + 3, 20, B_BOOT, SEED)
        ku = T.block_bootstrap(u, lambda x: stats.kurtosis(x) + 3, 20, B_BOOT, SEED)
        out[k] = {'kz': float(stats.kurtosis(z) + 3), 'kz_lo': float(np.percentile(kz, 2.5)), 'kz_hi': float(np.percentile(kz, 97.5)),
                  'ku': float(stats.kurtosis(u) + 3), 'ku_lo': float(np.percentile(ku, 2.5)), 'ku_hi': float(np.percentile(ku, 97.5)),
                  'sdz': float(z.std()), 'jbz': float(stats.jarque_bera(z).statistic), 'jbz_p': float(stats.jarque_bera(z).pvalue),
                  'skz': float(stats.skew(z)), 'N': int(len(z)),
                  'tail3': float(np.mean(np.abs(z) > 3)), 'tail3u': float(np.mean(np.abs(u) > 3))}
    out['normal_tail3'] = float(2 * stats.norm.sf(3))
    return out


def b5_har_insample():
    """log-HAR on SPY (total variance), OLS with ordinary and Newey-West errors; Wald: beta_w = beta_m; Ljung-Box on residuals."""
    res, X, ok = T.har_fit(RVT_SPY, log=True)
    y = np.log(RVT_SPY)[ok]
    Xc = np.column_stack([np.ones(ok.sum()), X[ok].values])
    e = res['resid']
    s2 = e @ e / (len(e) - 4)
    se_ols = np.sqrt(np.diag(s2 * np.linalg.inv(Xc.T @ Xc)))
    R = np.array([0, 0, 1, -1.0])
    wald = float((R @ res['b']) ** 2 / (R @ res['V'] @ R))
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb = acorr_ljungbox(e, lags=[10, 22])
    lb2 = acorr_ljungbox(y.values - y.mean(), lags=[10, 22])
    ar1 = T.ols_nw(y.values[1:], y.values[:-1, None])
    return {'b': res['b'], 'se_nw': res['se'], 'se_ols': se_ols, 'r2': res['r2'], 'T': res['T'], 'lags': res['lags'],
            'wald_wm': wald, 'p_wm': float(stats.chi2.sf(wald, 1)), 'lb10': float(lb['lb_stat'].iloc[0]), 'lb10_p': float(lb['lb_pvalue'].iloc[0]),
            'lb22': float(lb['lb_stat'].iloc[1]), 'lb22_p': float(lb['lb_pvalue'].iloc[1]), 'lby22': float(lb2['lb_stat'].iloc[1]),
            'pers': float(sum(res['b'][1:])), 'ar1_b': float(ar1['b'][1]), 'ar1_r2': float(ar1['r2']),
            't_nw': list(res['b'] / res['se']), 'ratio_se': list(res['se'] / se_ols)}


def garch_params_blocks(r, dates, refit=21, window=None):
    """GARCH(1,1)-t parameters re-estimated every `refit` days and the conditional variance for each day;
    window=None: expanding window (all earlier returns); window=m: last m returns (rolling window)."""
    from arch import arch_model
    dates = pd.DatetimeIndex(dates)
    pos = r.index.get_indexer(dates)
    rows = []
    for i0 in range(0, len(dates), refit):
        blk = dates[i0:i0 + refit]
        s0 = 0 if window is None else max(0, pos[i0] - window)
        fit = arch_model(r.iloc[s0:pos[i0]], mean='Constant', vol='GARCH', p=1, q=1, dist='t').fit(disp='off')
        fixed = arch_model(r.iloc[s0:pos[min(i0 + refit, len(dates)) - 1] + 1], mean='Constant', vol='GARCH', p=1, q=1,
                           dist='t').fix(fit.params)
        s2 = (fixed.conditional_volatility ** 2).reindex(blk)
        for d in blk:
            rows.append((d, s2[d], fit.params['omega'], fit.params['alpha[1]'], fit.params['beta[1]']))
    return pd.DataFrame(rows, columns=['date', 's2', 'omega', 'alpha', 'beta']).set_index('date')


def b6_week():
    """Forecast of the variance over the next 5 days (SPY): direct log-HAR vs GARCH(1,1)-t with the h-step formula."""
    v = RVT_SPY
    y5 = v[::-1].rolling(5).sum()[::-1]                     # sum of RV over days t..t+4 (target of the forecast made at t-1)
    X = T.har_design(np.log(v))
    ok = X.notna().all(axis=1) & y5.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    ly = np.log(y5).values
    idx = np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]
    fh = {}
    for t in idx:
        tr = np.where(ok.values[:t - 4])[0]                 # only targets fully observed before t
        b, *_ = np.linalg.lstsq(Xc[tr], ly[tr], rcond=None)
        s2 = np.var(ly[tr] - Xc[tr] @ b)
        fh[v.index[t]] = np.exp(Xc[t] @ b + s2 / 2)
    fh = pd.Series(fh)
    G = garch_params_blocks(D_SPY, fh.index)
    pers = G['alpha'] + G['beta']
    lr = G['omega'] / (1 - pers)
    fg = sum(lr + pers ** h * (G['s2'] - lr) for h in range(5))
    yy = y5.reindex(fh.index)
    out = {'T': int(len(fh))}
    for k, f in [('har', fh), ('garch', fg)]:
        mz = T.mz_test(yy, f)
        out[k] = {'qlike': float(T.qlike(yy, f).mean()), 'mse': float(T.mse(yy, f).mean()), 'mz_b': mz['b'], 'mz_a': mz['a'],
                  'mz_r2': mz['r2'], 'mz_p': mz['p'], 'mz_se_b': mz['se_b']}
    dq = T.dm_test(T.qlike(yy, fh), T.qlike(yy, fg))
    out.update({'dm_t': dq['t'], 'dm_p': dq['p'], 'pers_med': float(pers.median()),
                'note_overlap': 'overlapping 5-day targets: HAC lags set by the rule of thumb'})
    return out


def b7_harcj():
    """HAR-CJ in logs (Andersen, Bollerslev and Diebold, 2007): target ln(total variance of day t), regressors from day t-1;
    in sample (Newey-West) and out of sample."""
    j = T.jump_test(R_SPY)
    C = j['C'] + ON ** 2                                    # continuous part of the total variance (overnight included)
    Jc = j['J']
    v = RVT_SPY
    # log specification of Andersen, Bollerslev and Diebold (2007): log of the arithmetic means of C and
    # log(1 + J) for the daily, weekly and monthly jump components; all known on the evening of day t-1
    X = pd.DataFrame({'cd': np.log(C).shift(1), 'cw': np.log(C.rolling(5).mean()).shift(1),
                      'cm': np.log(C.rolling(22).mean()).shift(1), 'jd': np.log1p(Jc).shift(1),
                      'jw': np.log1p(Jc.rolling(5).mean()).shift(1), 'jm': np.log1p(Jc.rolling(22).mean()).shift(1)})
    y = np.log(v)
    ok = X.notna().all(axis=1)
    res = T.ols_nw(y[ok], X[ok])
    base, *_ = T.har_fit(v, log=True)
    # out of sample from 2022, expanding window
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        f[v.index[t]] = np.exp(Xc[t] @ b + np.var(y.values[tr] - Xc[tr] @ b) / 2)
    f = pd.Series(f)
    fl = T.har_expanding(v, '2022-01-03', log=True).reindex(f.index)
    yy = v.reindex(f.index)
    dq = T.dm_test(T.qlike(yy, f), T.qlike(yy, fl))
    Rj = np.zeros((3, 7))
    Rj[0, 4] = Rj[1, 5] = Rj[2, 6] = 1.0                   # H0: beta_Jd = beta_Jw = beta_Jm = 0
    dj = Rj @ res['b']
    wj = float(dj @ np.linalg.solve(Rj @ res['V'] @ Rj.T, dj))
    return {'b': res['b'], 'se': res['se'], 'r2': res['r2'], 'r2_base': base['r2'], 'T': res['T'],
            'wald_j': wj, 'p_j': float(stats.chi2.sf(wj, 3)),
            'q_cj': float(T.qlike(yy, f).mean()), 'q_har': float(T.qlike(yy, fl).mean()), 'dm_t': dq['t'], 'dm_p': dq['p']}


def b8_rough():
    """Exponent H of log-volatility (SPY): total RV, intraday RV, BV, RV subsampled at 30 minutes; block bootstrap."""
    series = {'rv_total': RVT_SPY, 'rv_intraday': RV_SPY, 'bv': T.bv(R_SPY), 'rv30_sub': T.subsampled_rv(P_SPY, 6)}
    out = {}
    for k, s in series.items():
        x = 0.5 * np.log(s.values)
        H = rough_H(x)['H']
        boot = T.block_bootstrap_blocks(x, lambda z: rough_H(z)['H'], 60, 300, SEED)
        out[k] = {'H': H, 'lo': float(np.percentile(boot, 2.5)), 'hi': float(np.percentile(boot, 97.5))}
    # H for a process with H = 0.5 measured with noise (simulation): how far does the estimate fall?
    rng = np.random.default_rng(SEED)
    n = len(RVT_SPY)
    x = np.cumsum(0.1 * rng.standard_normal(n))
    x = x - np.linspace(0, x[-1], n)
    out['sim_bm'] = rough_H(x)['H']
    out['sim_bm_noise'] = rough_H(x + 0.25 * rng.standard_normal(n))['H']
    return out


# =============================================================================
# PART C: IS BITCOIN VOLATILITY MORE PREDICTABLE THAN THAT OF SPY?
# =============================================================================
def c1_predictability():
    """Same out-of-sample period (March 2025 - September 2026): log-HAR, GARCH-t, yesterday's RV; MZ R^2,
    QLIKE gain over yesterday's RV, block bootstrap for the R^2 difference; log-HAR with a weekend effect for Bitcoin."""
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True).loc[C_START:]
    Fb = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_btc.csv'), index_col=0, parse_dates=True).loc[C_START:]
    out = {}
    for k, D in [('spy', F), ('btc', Fb)]:
        y = D['proxy']
        o = {'T': int(len(D))}
        for m in ['logHAR', 'GARCH-t', 'RW']:
            o[m] = {'r2': T.mz_test(y, D[m])['r2'], 'qlike': float(T.qlike(y, D[m]).mean())}
            o[m]['r2log'] = float(np.corrcoef(np.log(y), np.log(D[m]))[0, 1] ** 2)
        o['gain_rw'] = 1 - o['logHAR']['qlike'] / o['RW']['qlike']
        o['gain_garch'] = 1 - o['logHAR']['qlike'] / o['GARCH-t']['qlike']
        out[k] = o
    # block bootstrap for the R^2 difference (log scale) between Bitcoin and SPY: the same calendar-time blocks
    # (28 days, about 20 SPY trading days) for both assets, so their covariance is preserved
    a = np.c_[np.log(F['proxy']), np.log(F['logHAR'])]
    b = np.c_[np.log(Fb['proxy']), np.log(Fb['logHAR'])]
    cal = pd.date_range(min(F.index[0], Fb.index[0]), max(F.index[-1], Fb.index[-1]), freq='D')
    rowa = np.full(len(cal), -1)
    rowa[cal.get_indexer(F.index)] = np.arange(len(F))
    rowb = np.full(len(cal), -1)
    rowb[cal.get_indexer(Fb.index)] = np.arange(len(Fb))
    rng = np.random.default_rng(SEED)
    block, ncal = 28, len(cal)
    nb = int(np.ceil(ncal / block))

    def r2(x, rows):
        rows = rows[rows >= 0]
        return np.corrcoef(x[rows, 0], x[rows, 1])[0, 1] ** 2
    d = np.empty(B_BOOT)
    for i in range(B_BOOT):
        st = rng.integers(0, ncal - block + 1, nb)
        days = (st[:, None] + np.arange(block)[None, :]).ravel()[:ncal]
        d[i] = r2(b, rowb[days]) - r2(a, rowa[days])
    out['r2diff'] = float(out['btc']['logHAR']['r2log'] - out['spy']['logHAR']['r2log'])
    out['r2diff_lo'] = float(np.percentile(d, 2.5))
    out['r2diff_hi'] = float(np.percentile(d, 97.5))
    # log-HAR with a weekend dummy for Bitcoin (expanding window)
    v = RV_BTC
    X = T.har_design(np.log(v), calendar=True)
    X['we'] = (v.index.dayofweek >= 5).astype(float)
    ok = X.notna().all(axis=1)
    y = np.log(v)
    res = T.ols_nw(y[ok], X[ok])
    base, *_ = T.har_fit(v, calendar=True, log=True)
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((v.index >= pd.Timestamp(C_START)) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        bb, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        f[v.index[t]] = np.exp(Xc[t] @ bb + np.var(y.values[tr] - Xc[tr] @ bb) / 2)
    f = pd.Series(f).reindex(Fb.index)
    yb = Fb['proxy']
    dq = T.dm_test(T.qlike(yb, f), T.qlike(yb, Fb['logHAR']))
    out['we'] = {'b_we': float(res['b'][4]), 'se_we': float(res['se'][4]), 'r2': res['r2'], 'r2_base': base['r2'],
                 'qlike': float(T.qlike(yb, f).mean()), 'r2log': float(np.corrcoef(np.log(yb), np.log(f))[0, 1] ** 2),
                 'dm_t': dq['t'], 'dm_p': dq['p'], 'mult': float(np.exp(res['b'][4]))}
    # chart: log-scale R^2 and QLIKE gain, SPY vs Bitcoin
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.1))
    labs = ['logHAR', 'GARCH-t', 'RW']
    x = np.arange(3)
    axes[0].bar(x - 0.2, [out['spy'][m]['r2log'] for m in labs], 0.4, color=MainBlue, label='SPY (with overnight)')
    axes[0].bar(x + 0.2, [out['btc'][m]['r2log'] for m in labs], 0.4, color=Amber, label='Bitcoin (24 hours)')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(['log-HAR', 'GARCH(1,1)-t', "Yesterday's RV"])
    axes[0].set_ylabel(r'$R^2$ of log RV on log forecast')
    axes[1].bar(x - 0.2, [out['spy'][m]['qlike'] for m in labs], 0.4, color=MainBlue)
    axes[1].bar(x + 0.2, [out['btc'][m]['qlike'] for m in labs], 0.4, color=Amber)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(['log-HAR', 'GARCH(1,1)-t', "Yesterday's RV"])
    axes[1].set_ylabel('Mean QLIKE loss')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch9_sem_c1')
    return out


# =============================================================================
# EXTENSIONS: jump inference, HAR as a restricted AR(22), HARQ, SHAR, MCS
# =============================================================================
def bh_count(p, q=0.05):
    """Benjamini-Hochberg: number of rejected hypotheses with the false discovery rate controlled at q."""
    p = np.sort(np.asarray(p))
    n = len(p)
    ok = np.where(p <= q * np.arange(1, n + 1) / n)[0]
    return int(ok[-1] + 1) if len(ok) else 0


def periodicity_sd(R, bv_day):
    """Intraday periodicity factor (SD estimator of Boudt, Croux and Laurent, 2011):
    returns standardised by sqrt(BV_t / M_t), root mean square per interval, normalised to a mean square of 1."""
    M_ = R.notna().sum(axis=1)
    rb = R.div(np.sqrt(bv_day / M_), axis=0)
    sd = np.sqrt((rb ** 2).mean(axis=0))
    return sd / np.sqrt((sd ** 2).mean())


def ex_jump_inference(K=270, alpha_lm=0.01, c_trunc=3.0, varpi=0.49):
    """SPY jumps: FDR (Benjamini-Hochberg), Bonferroni, ratio test on periodicity-adjusted returns,
    Lee-Mykland intraday test (K = 270 for 5 minutes), truncated RV (Mancini) and MedRV (Andersen, Dobrev, Schaumburg)."""
    j = T.jump_test(R_SPY)
    N = len(j)
    p = stats.norm.sf(j['z'].values)
    out = {'N': N, 'n5': int((p < 0.05).sum()), 'bh5': bh_count(p, 0.05), 'bh1': bh_count(p, 0.01),
           'bonf5': int((p < 0.05 / N).sum()), 'n0_1': int(j['jump'].sum())}
    f = periodicity_sd(R_SPY, j['bv'])
    Rs = R_SPY / f.values[None, :]
    js = T.jump_test(Rs)
    ps = stats.norm.sf(js['z'].values)
    out.update({'per_n5': int((ps < 0.05).sum()), 'per_n0_1': int(js['jump'].sum()), 'per_bh5': bh_count(ps, 0.05),
                'f_first': float(f.iloc[0]), 'f_min': float(f.min()), 'f_last': float(f.iloc[-1])})
    # Lee-Mykland: L = r / sigma_hat, sigma_hat^2 = mean of the products |r_j||r_{j-1}| over the K-1 previous returns (concatenated series)
    x = Rs.values.ravel()
    day = np.repeat(np.arange(N), Rs.shape[1])
    slot = np.tile(np.arange(Rs.shape[1]), N)
    ok = ~np.isnan(x)
    x, day, slot = x[ok], day[ok], slot[ok]
    prod = np.r_[np.nan, np.abs(x[1:]) * np.abs(x[:-1])]
    bvl = pd.Series(prod).rolling(K - 2).mean().shift(1).values
    L = x / np.sqrt(bvl * np.pi / 2)     # mu_1^{-2} = pi/2: local BV estimates the per-interval variance, so L ~ N(0, 1)
    n = int(np.isfinite(L).sum())
    # Lee and Mykland (2008) divide by local BV without pi/2 and use c = sqrt(2/pi) in C_n, S_n;
    # with the corrected denominator (standardised L) the same thresholds are obtained with c = 1
    c = 1.0
    Cn = np.sqrt(2 * np.log(n)) / c - (np.log(np.pi) + np.log(np.log(n))) / (2 * c * np.sqrt(2 * np.log(n)))
    Sn = 1 / (c * np.sqrt(2 * np.log(n)))
    beta = -np.log(-np.log(1 - alpha_lm))
    hit = np.isfinite(L) & ((np.abs(L) - Cn) / Sn > beta)
    jd = np.unique(day[hit])
    out.update({'lm_K': K, 'lm_n': n, 'lm_crit': float(Cn + Sn * beta), 'lm_hits': int(hit.sum()), 'lm_days': int(len(jd)),
                'lm_open': int((slot[hit] == 0).sum()), 'lm_10': int((slot[hit] == 6).sum()),
                'lm_slots': [int(x) for x in slot[hit]],
                'lm_wed14': int(np.sum(hit & (np.asarray(Rs.index.dayofweek)[day] == 2) & (slot >= 54) & (slot <= 65))),
                'lm_top': {'date': str(Rs.index[day[hit]][np.argmax(np.abs(L[hit]))].date()),
                           'L': float(L[hit][np.argmax(np.abs(L[hit]))])},
                'lm_in_ratio': float(np.mean(j['jump'].values[jd])) if len(jd) else float('nan'),
                'ratio_in_lm': float(np.mean(np.isin(np.where(j['jump'].values)[0], jd)))})
    # truncated RV and MedRV (on raw returns; the threshold accounts for periodicity)
    Mt = R_SPY.notna().sum(axis=1).values
    thr = c_trunc * np.sqrt(j['bv'].values)[:, None] * (1 / Mt[:, None]) ** varpi * f.values[None, :]
    A = R_SPY.values
    trv = np.nansum(np.where(np.abs(A) <= thr, A ** 2, 0.0), axis=1)
    a = np.abs(A)
    med = np.median(np.stack([a[:, :-2], a[:, 1:-1], a[:, 2:]]), axis=0)   # only windows with three observed returns
    medrv = np.pi / (6 - 4 * np.sqrt(3) + np.pi) * Mt / (Mt - 2) * np.nansum(med ** 2, axis=1)
    rvs = j['rv'].values
    out.update({'trv_share': float(1 - trv.sum() / rvs.sum()), 'bv_share': float(1 - j['bv'].sum() / rvs.sum()),
                'medrv_share': float(1 - medrv.sum() / rvs.sum()), 'trunc_days': float(np.mean(trv < rvs)),
                'c_trunc': c_trunc, 'varpi': varpi})
    return out


def ex_har_ar22():
    """log-HAR as a restricted AR(22): Wald test (Newey-West) of the 19 linear restrictions."""
    y = np.log(RVT_SPY)
    X = pd.concat({f'l{k}': y.shift(k) for k in range(1, 23)}, axis=1)
    ok = X.notna().all(axis=1)
    res = T.ols_nw(y[ok].values, X[ok].values)
    Rm = []
    for k in (2, 3, 4):                                   # phi_k = phi_{k+1}, k = 2..4
        r = np.zeros(23); r[k] = 1; r[k + 1] = -1; Rm.append(r)
    for k in range(6, 22):                                # phi_k = phi_{k+1}, k = 6..21
        r = np.zeros(23); r[k] = 1; r[k + 1] = -1; Rm.append(r)
    Rm = np.array(Rm)
    d = Rm @ res['b']
    W = float(d @ np.linalg.solve(Rm @ res['V'] @ Rm.T, d))
    har, Xh, okh = T.har_fit(RVT_SPY, log=True)
    # same sample for the R^2 comparison
    return {'q': int(Rm.shape[0]), 'wald': W, 'p': float(stats.chi2.sf(W, Rm.shape[0])), 'r2_ar22': float(res['r2']),
            'r2_har': float(har['r2']), 'T': int(res['T']), 'lags': int(res['lags'])}


def _expanding_ols(y, X, start, filt=True):
    """Expanding-window OLS forecasts with the "insanity filter" of Bollerslev, Patton and Quaedvlieg (2016):
    a forecast outside the [min, max] range of the estimation-sample values is replaced by the sample mean."""
    ok = X.notna().all(axis=1) & y.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((y.index >= pd.Timestamp(start)) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        v = Xc[t] @ b
        if filt and (v < y.values[tr].min() or v > y.values[tr].max()):
            v = y.values[tr].mean()
        f[y.index[t]] = v
    return pd.Series(f)


def ex_harq_shar(start='2022-01-03'):
    """HARQ (Bollerslev, Patton, Quaedvlieg 2016) and SHAR (Patton, Sheppard 2015) on SPY total variance, in levels;
    in sample with Newey-West errors; out-of-sample forecasts; MCS (Hansen, Lunde, Nason 2011) on QLIKE."""
    v = RVT_SPY
    rqd = T.rq(R_SPY)
    Xh = T.har_design(v)
    XQ = Xh.copy()
    XQ['dq'] = (np.sqrt(rqd) * v).shift(1)
    okq = XQ.notna().all(axis=1)
    rQ = T.ols_nw(v[okq].values, XQ[okq].values)
    rH = T.ols_nw(v[okq].values, Xh[okq].values)
    # semivariances: intraday returns plus the overnight return as one extra return of the day
    A = np.c_[ON.reindex(R_SPY.index).values, R_SPY.values]
    rsp = pd.Series(np.nansum(np.where(A > 0, A ** 2, 0), axis=1), index=R_SPY.index)
    rsn = pd.Series(np.nansum(np.where(A < 0, A ** 2, 0), axis=1), index=R_SPY.index)
    XS = pd.DataFrame({'rsp': rsp.shift(1), 'rsn': rsn.shift(1), 'w': Xh['w'], 'm': Xh['m']})
    oks = XS.notna().all(axis=1)
    rS = T.ols_nw(v[oks].values, XS[oks].values)
    Rr = np.array([0, 1, -1.0, 0, 0])
    w_pm = float((Rr @ rS['b']) ** 2 / (Rr @ rS['V'] @ Rr))
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True)
    fQ = _expanding_ols(v, XQ, start).reindex(F.index)
    fS = _expanding_ols(v, XS, start).reindex(F.index)
    fH = _expanding_ols(v, Xh, start).reindex(F.index)
    y = F['proxy']
    L = pd.DataFrame({m: T.qlike(y, F[m]) for m in ['logHAR', 'HAR', 'GARCH-t', 'EWMA', 'RW']})
    L['HARQ'] = T.qlike(y, fQ)
    L['SHAR'] = T.qlike(y, fS)
    L['HARf'] = T.qlike(y, fH)
    out = {'harq': {'b': list(rQ['b']), 'se': list(rQ['se']), 'r2': float(rQ['r2']), 'r2_har': float(rH['r2']),
                    'bd_at': {}},
           'shar': {'b': list(rS['b']), 'se': list(rS['se']), 'r2': float(rS['r2']), 'wald_pm': w_pm,
                    'p_pm': float(stats.chi2.sf(w_pm, 1))},
           'qlike': {m: float(L[m].mean()) for m in L}}
    # effective daily slope beta_d + beta_Q sqrt(RQ) at quantiles of sqrt(RQ)
    s = np.sqrt(rqd.reindex(v[okq].index).values)
    for qq in (0.5, 0.99):
        out['harq']['bd_at'][str(qq)] = float(rQ['b'][1] + rQ['b'][4] * np.quantile(s, qq))
    # HARQ on intraday RV (setting of the original paper: RQ and RV from the same returns)
    vi = RV_SPY
    Xi = T.har_design(vi)
    Xi['dq'] = (np.sqrt(rqd) * vi).shift(1)
    oki = Xi.notna().all(axis=1)
    rI = T.ols_nw(vi[oki].values, Xi[oki].values)
    si = np.sqrt(rqd.reindex(vi[oki].index).values)
    out['harq_intra'] = {'b': list(rI['b']), 'se': list(rI['se']), 'r2': float(rI['r2']),
                         'bd_at': {str(qq): float(rI['b'][1] + rI['b'][4] * np.quantile(si, qq)) for qq in (0.5, 0.99)},
                         'sq': {str(qq): float(np.quantile(si, qq)) for qq in (0.5, 0.99)}}
    for m in ['HARQ', 'SHAR']:
        for base in ['HARf', 'logHAR']:
            dq = T.dm_test(L[m], L[base])
            out[f'dm_{m}_{base}'] = {'t': dq['t'], 'p': dq['p']}
    from arch.bootstrap import MCS
    mods = ['logHAR', 'HAR', 'GARCH-t', 'EWMA', 'RW', 'HARQ', 'SHAR']
    mcs = MCS(L[mods].dropna(), size=0.10, reps=10000, block_size=20, method='R', seed=SEED)
    mcs.compute()
    pv = mcs.pvalues['Pvalue']
    out['mcs'] = {'included': [str(m) for m in mcs.included], 'pvalues': {str(k): float(x) for k, x in pv.items()},
                  'T': int(len(L[mods].dropna()))}
    return out


GW_WIN_HAR = 250      # rolling window of the direct log-HAR (last 250 fully observed targets)
GW_WIN_GARCH = 1000   # rolling window of GARCH(1,1)-t (last 1000 daily returns)


def ex_gw_week():
    """Conditional Giacomini-White (2006) test for the 5-day forecasts (B6). Their theory requires fixed-length (rolling)
    estimation windows, so both methods are re-estimated on rolling windows: direct log-HAR on the last 250
    targets, GARCH(1,1)-t on the last 1000 returns (every 21 days). Instruments (1, d_{t-5}); under the null
    Z_t d_{t+5} is uncorrelated beyond 4 lags, so Omega = unweighted sum of the autocovariances 0..4."""
    v = RVT_SPY
    y5 = v[::-1].rolling(5).sum()[::-1]
    X = T.har_design(np.log(v))
    ok = X.notna().all(axis=1) & y5.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    ly = np.log(y5).values
    idx = np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]
    fh = {}
    for t in idx:
        tr = np.where(ok.values[:t - 4])[0][-GW_WIN_HAR:]
        b, *_ = np.linalg.lstsq(Xc[tr], ly[tr], rcond=None)
        fh[v.index[t]] = np.exp(Xc[t] @ b + np.var(ly[tr] - Xc[tr] @ b) / 2)
    fh = pd.Series(fh)
    G = garch_params_blocks(D_SPY, fh.index, window=GW_WIN_GARCH)
    pers = G['alpha'] + G['beta']
    # E[sigma^2_{t+h}] = omega (1 + p + ... + p^{h-1}) + p^h sigma^2_t: also valid at p = 1 (IGARCH), frequent on short windows
    fg = sum(G['omega'] * sum(pers ** j for j in range(h)) + pers ** h * G['s2'] for h in range(5))
    yy = y5.reindex(fh.index)
    lh, lg = T.qlike(yy, fh), T.qlike(yy, fg)
    d = (lh - lg).values
    tau = 5
    Z = np.column_stack([np.ones(len(d) - tau), d[:-tau]]) * d[tau:, None]
    n = len(Z)
    zbar = Z.mean(axis=0)
    U = Z - zbar
    S = U.T @ U / n
    for l in range(1, tau):
        g = U[l:].T @ U[:-l] / n
        S += g + g.T
    if np.min(np.linalg.eigvalsh(S)) <= 0:          # fallback: Newey-West with the bandwidth rule, if S is not positive definite
        L_ = T.nw_lags(n)
        S = U.T @ U / n
        for l in range(1, L_ + 1):
            g = U[l:].T @ U[:-l] / n
            S += (1 - l / (L_ + 1)) * (g + g.T)
    stat = float(n * zbar @ np.linalg.solve(S, zbar))
    dm = T.dm_test(lh, lg)                           # unconditional test: Newey-West with the bandwidth rule
    return {'gw': stat, 'p': float(stats.chi2.sf(stat, 2)), 'T': n, 't_unc': dm['t'], 'p_unc': dm['p'],
            'q_har': float(lh.mean()), 'q_garch': float(lg.mean()), 'win_har': GW_WIN_HAR, 'win_garch': GW_WIN_GARCH}


def ex_rk_ratio():
    """Realised kernel on 5-minute bars: ratio of means RK/RV with a block bootstrap CI (20-day blocks)."""
    rk, H = T.realized_kernel(R_SPY, P_SPY)
    rk = rk.reindex(RV_SPY.index)
    boot = T.block_bootstrap(np.c_[rk.values, RV_SPY.values], lambda x: x[:, 0].mean() / x[:, 1].mean(), 20, B_BOOT, SEED)
    return {'ratio': float(rk.mean() / RV_SPY.mean()), 'lo': float(np.percentile(boot, 2.5)),
            'hi': float(np.percentile(boot, 97.5)), 'H_med': float(H.median())}


def ex_a8_mz():
    """A8: MZ for GARCH(1,1)-t (SPY, 2022-2026): coefficients, NW errors and the covariance for the joint Wald test."""
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True)
    res = T.ols_nw(F['proxy'].values, F['GARCH-t'].values[:, None])
    V = res['V']
    dl = res['b'] - np.array([0, 1.0])
    W = float(dl @ np.linalg.solve(V, dl))
    d = (T.qlike(F['proxy'], F['logHAR']) - T.qlike(F['proxy'], F['GARCH-t']))
    dm = T.dm_test(T.qlike(F['proxy'], F['logHAR']), T.qlike(F['proxy'], F['GARCH-t']))
    return {'a': float(res['b'][0]), 'b': float(res['b'][1]), 'se_a': float(res['se'][0]), 'se_b': float(res['se'][1]),
            'cov': float(V[0, 1]), 'corr': float(V[0, 1] / np.sqrt(V[0, 0] * V[1, 1])), 'wald': W,
            'p': float(stats.chi2.sf(W, 2)), 'ta': float(res['b'][0] / res['se'][0]), 'tb': float((res['b'][1] - 1) / res['se'][1]),
            'dbar': float(d.mean()), 'se_d': float(dm['mean_diff'] / dm['t']), 'dm_t': dm['t'], 'dm_p': dm['p']}


def ex_a6_jensen():
    """A6: minimiser of the MSE on volatility with a proxy RV = IV chi2_M / M: F* = IV (E sqrt(chi2_M/M))^2."""
    from scipy.special import gammaln
    out = {}
    for m in (1, 6, 78):
        out[str(m)] = float(2 / m * np.exp(2 * (gammaln((m + 1) / 2) - gammaln(m / 2))))
    return out



# =============================================================================
# SEMINAR CHARTS (one per exercise; new numbers go to the SC block of sem9_results.json)
# =============================================================================
DAY = '2025-04-07'


def sc_day(day=DAY):
    """From bars to returns: SPY price grid on one day (open + 78 closes), the returns and cumulative RV."""
    d = pd.Timestamp(day)
    p = P_SPY.loc[d].dropna().values
    r = 100 * np.diff(np.log(p))
    on = float(ON[d])
    prev = p[0] * np.exp(-on / 100)
    t = pd.date_range(d + pd.Timedelta('09:30:00'), periods=len(p), freq='5min')
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.0))
    axes[0].plot(t[1:], p[1:], color=MainBlue, lw=1.0, label='Bar closes $P_1, \\ldots, P_{78}$')
    axes[0].scatter([t[0]], [p[0]], color=Orange, s=26, zorder=3, label='Opening price $P_0$ (09:30)')
    axes[0].axhline(prev, color=Black, lw=0.8, ls='--', label=f'Previous close (overnight return {on:+.2f}%)')
    axes[0].set_ylabel('USD')
    axes[0].set_title('Price grid: 79 prices', fontsize=9, loc='left')
    axes[1].bar(t[1:], r, width=0.0028, color=np.where(r > 0, Forest, IDAred), label='5-minute log return $r_i$ (%): green up, red down')
    axes[1].axhline(0, color=Black, lw=0.6)
    axes[1].set_title('78 returns', fontsize=9, loc='left')
    axes[1].set_ylabel('%')
    cum = np.cumsum(r ** 2)
    axes[2].step(t[1:], cum, where='post', color=IDAred, lw=1.2, label='Cumulative $\\sum r_i^2$ = RV (%$^2$)')
    axes[2].axhline(cum[-1] + on ** 2, color=Purple, lw=1.0, ls='-.', label='RV + squared overnight return (total variance)')
    axes[2].set_title('Realised variance', fontsize=9, loc='left')
    axes[2].set_ylabel('%$^2$')
    for ax in axes:
        ax.tick_params(axis='x', labelsize=7)
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_day')
    nr = R_SPY.notna().sum(axis=1)
    return {'spy_days': int(len(P_SPY)), 'spy_cols': int(P_SPY.shape[1]), 'full': int((nr == 78).sum()),
            'half': int((nr == 43).sum()), 'other': int(((nr != 78) & (nr != 43)).sum()),
            'first': str(P_SPY.index[0].date()), 'last': str(P_SPY.index[-1].date()),
            'btc_days': int(len(P_BTC)), 'btc_cols': int(P_BTC.shape[1]),
            'btc_first': str(P_BTC.index[0].date()), 'btc_last': str(P_BTC.index[-1].date()),
            'p': [float(x) for x in p[:3]], 'r': [float(x) for x in r[:2]], 'p_last': float(p[-1]), 'n': int(len(r)),
            'rv': float(cum[-1]), 'on': on, 'total': float(cum[-1] + on ** 2)}


def sc_a1(B=200000):
    """A1: exact distribution of RV/IV = chi2_M / M for M = 6 and 78; simulated coverage of the log CI with RQ."""
    rng = np.random.default_rng(SEED)
    x = np.linspace(0.01, 2.6, 600)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.0))
    cov = {}
    for M_, col in [(6, Amber), (78, MainBlue)]:
        axes[0].plot(x, stats.chi2.pdf(x * M_, M_) * M_, color=col, lw=1.3, label=f'Density of RV/IV, M = {M_}')
        Z = rng.standard_normal((B, M_)) / np.sqrt(M_)             # r_i = sigma sqrt(Delta) Z_i with IV = 1
        rv = (Z ** 2).sum(axis=1)
        se = np.sqrt(2 / 3 * (Z ** 4).sum(axis=1)) / rv
        cov[str(M_)] = float(np.mean((rv * np.exp(-1.96 * se) <= 1) & (1 <= rv * np.exp(1.96 * se))))
    axes[0].axvline(1, color=Black, lw=0.8, ls=':', label='True IV = 1')
    axes[0].set_xlabel('RV / IV')
    lo, hi = np.exp(-1.96 * np.sqrt(2 / 78)), np.exp(1.96 * np.sqrt(2 / 78))
    lo6, hi6 = np.exp(-1.96 * np.sqrt(2 / 6)), np.exp(1.96 * np.sqrt(2 / 6))
    axes[1].plot([lo6, hi6], [0.3, 0.3], color=Amber, lw=3, label=f'M = 6: [{lo6:.2f}, {hi6:.2f}]')
    axes[1].plot([lo, hi], [0.7, 0.7], color=MainBlue, lw=3, label=f'M = 78: [{lo:.2f}, {hi:.2f}]')
    axes[1].scatter([1, 1], [0.3, 0.7], color=IDAred, zorder=3, s=18, label='Observed RV = 1')
    axes[1].set_ylim(0, 1)
    axes[1].set_yticks([])
    axes[1].set_xlabel('IV (log-scale interval $\\mathrm{RV}\\,e^{\\pm 1.96\\sqrt{2/M}}$)')
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        handles += h
        labels += l
    plt.tight_layout()
    fig_legend_bottom(fig, handles, labels, ncol=3, y=0.0)
    save_fig('ch9_sem_a1')
    return {'cov6': cov['6'], 'cov78': cov['78'], 'lo6': lo6, 'hi6': hi6, 'lo78': lo, 'hi78': hi}


def sc_a2(A2):
    """A2: contributions of the six returns to RV and BV; the z statistic against the critical value."""
    r = np.array([0.08, -0.15, 0.03, 0.10, -0.04, -0.90])
    M_ = len(r)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.0))
    i = np.arange(1, M_ + 1)
    axes[0].bar(i - 0.2, r ** 2, 0.4, color=MainBlue, label='$r_i^2$ (contribution to RV)')
    bvc = np.r_[0, (np.pi / 2) * M_ / (M_ - 1) * np.abs(r[1:] * r[:-1])]
    axes[0].bar(i + 0.2, bvc, 0.4, color=Amber, label='$\\frac{\\pi}{2}\\frac{M}{M-1}|r_i r_{i-1}|$ (contribution to BV)')
    axes[0].set_xticks(i)
    axes[0].set_xlabel('Interval $i$ (the jump is in interval 6)')
    axes[0].set_ylabel('%$^2$')
    x = np.linspace(-4, 4.5, 400)
    axes[1].plot(x, stats.norm.pdf(x), color=MainBlue, lw=1.2, label='N(0,1) under no jump')
    axes[1].axvline(A2['z'], color=IDAred, lw=1.4, label=f"Observed z = {A2['z']:.2f}")
    axes[1].axvline(A2['crit'], color=Forest, lw=1.2, ls='--', label=f"Critical value 0.1%: {A2['crit']:.2f}")
    axes[1].axvline(np.sqrt(M_ / A2['theta']), color=Purple, lw=1.2, ls='-.',
                    label=f"Largest possible z with M = 6: {np.sqrt(M_ / A2['theta']):.2f}")
    axes[1].set_xlabel('z')
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_a2')
    return {'bvc': [float(v) for v in bvc]}


def _mse_parts(omega, iq=1.0):
    n = np.unique(np.round(np.logspace(np.log10(6), np.log10(23400), 400))).astype(float)
    return n, 2 * iq / n, 4 * n ** 2 * omega ** 4


def sc_a3():
    """A3: MSE(n) = 2 IQ/n + 4 n^2 omega^4 with omega = 0.01%: decomposition and optimum."""
    n, disc, bias2 = _mse_parts(0.01)
    secs = 23400 / n
    nstar = (1 / (4 * 0.01 ** 4)) ** (1 / 3)
    fig, ax = plt.subplots(figsize=(7.6, 3.1))
    ax.plot(secs, disc, color=MainBlue, lw=1.2, label='Discretisation variance $2\\,\\mathrm{IQ}/n$')
    ax.plot(secs, bias2, color=Amber, lw=1.2, label='Squared noise bias $4n^2\\omega^4$')
    ax.plot(secs, disc + bias2, color=IDAred, lw=1.6, label='MSE')
    for s_, lab, c in [(23400 / nstar, f'Optimum: one return every {23400 / nstar:.0f} s', Forest), (60, '1 minute', Purple),
                       (300, '5 minutes', Teal)]:
        nn = 23400 / s_
        ax.scatter([s_], [2 / nn + 4 * nn ** 2 * 1e-8], color=c, zorder=3, s=26, label=lab)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Sampling interval (seconds, 6.5-hour session)')
    ax.set_ylabel('%$^4$')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch9_sem_a3')
    tab = {}
    for lab, nn in [('5min', 78), ('1min', 390), ('1s', 23400), ('opt', nstar)]:
        tab[lab] = {'n': float(nn), 'bias': float(2 * nn * 1e-4), 'erv': float(1 + 2 * nn * 1e-4),
                    'mse': float(2 / nn + 4 * nn ** 2 * 1e-8), 'disc': float(2 / nn), 'bias2': float(4 * nn ** 2 * 1e-8)}
    return tab


def sc_a4(A4):
    """A4: MSE with omega = 0.03% and the estimators of the day: RV on all data, average of shifted grids, TSRV."""
    n, disc, bias2 = _mse_parts(0.03)
    secs = 23400 / n
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.0))
    axes[0].plot(secs, disc, color=MainBlue, lw=1.2, label='$2\\,\\mathrm{IQ}/n$')
    axes[0].plot(secs, bias2, color=Amber, lw=1.2, label='$4n^2\\omega^4$, $\\omega = 0.03\\%$')
    axes[0].plot(secs, disc + bias2, color=IDAred, lw=1.6, label='MSE')
    axes[0].scatter([A4['secs']], [2 / A4['nstar'] + 4 * A4['nstar'] ** 2 * 0.03 ** 4], color=Forest, s=26, zorder=3,
                    label=f"Optimum: every {A4['secs']:.0f} s")
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Sampling interval (seconds)')
    vals = [1.70, 1.10, A4['tsrv'], A4['tsrv_adj']]
    labs = ['RV, all 1-min', 'RV avg., 5 grids', 'TSRV', 'TSRV, adjusted']
    axes[1].bar(labs, vals, color=[IDAred, Amber, Purple, Forest], label='Estimates of IV on the day (%$^2$)')
    axes[1].axhline(1.0, color=Black, lw=0.9, ls='--', label='True IV = 1')
    axes[1].tick_params(axis='x', labelsize=7)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_a4')
    return {'om2_oracle': float((1.70 - 1) / 780), 'om2_all': float(1.70 / 780)}


def sc_a5(b=(-0.08, 0.36, 0.34, 0.17)):
    """A5: HAR lag weights, split by component (daily, weekly, monthly)."""
    k = np.arange(1, 26)
    dd = np.where(k == 1, b[1], 0.0)
    ww = np.where(k <= 5, b[2] / 5, 0.0)
    mm = np.where(k <= 22, b[3] / 22, 0.0)
    fig, ax = plt.subplots(figsize=(7.8, 3.0))
    ax.bar(k, mm, color=MainBlue, label='Monthly: $\\beta_m/22$ on lags 1-22')
    ax.bar(k, ww, bottom=mm, color=Amber, label='Weekly: $\\beta_w/5$ on lags 1-5')
    ax.bar(k, dd, bottom=mm + ww, color=IDAred, label='Daily: $\\beta_d$ on lag 1')
    ax.set_xlabel('Lag $k$ (trading days)')
    ax.set_ylabel('Implied AR weight $\\phi_k$')
    ax.set_xticks([1, 2, 5, 6, 10, 15, 22, 25])
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch9_sem_a5')
    return {}


def sc_a6(XA6):
    """A6: QLIKE and MSE on variance as functions of F/IV; the minimiser of the MSE on volatility."""
    f = np.linspace(0.2, 3.0, 300)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.0))
    axes[0].plot(f, 1 / f - np.log(1 / f) - 1, color=IDAred, lw=1.4, label='QLIKE$(1, F)$')
    axes[0].plot(f, (1 - f) ** 2, color=MainBlue, lw=1.4, label='Variance MSE $(1 - F)^2$')
    for x_, c in [(0.5, Forest), (2.0, Purple)]:
        axes[0].scatter([x_, x_], [1 / x_ - np.log(1 / x_) - 1, (1 - x_) ** 2], color=c, s=22, zorder=3,
                        label=f'Forecast F = {x_}')
    axes[0].set_xlabel('Forecast / true variance')
    axes[0].set_ylim(0, 1.2)
    ms = ['1', '6', '78']
    axes[1].bar([f'M = {m}' for m in ms], [XA6[m] for m in ms], color=Amber, label='Volatility-MSE optimum $F^*/\\mathrm{IV}$')
    axes[1].axhline(1, color=Black, lw=0.9, ls='--', label='Unbiased: $F = \\mathrm{IV}$')
    axes[1].set_ylim(0, 1.1)
    for i, m in enumerate(ms):
        axes[1].text(i, XA6[m] + 0.02, f'{XA6[m]:.3f}', ha='center', fontsize=8, color='black')
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_a6')
    return {}


def sc_a7(beta=0.8, s_eta=0.3, n=20000):
    """A7: errors-in-variables simulation: the OLS slope of RV_{t+1} on RV_t falls with the error variance; conditional weight."""
    rng = np.random.default_rng(SEED)
    iv = np.empty(n)
    iv[0] = 1.0
    eta = s_eta * rng.standard_normal(n)
    for t in range(1, n):
        iv[t] = (1 - beta) + beta * iv[t - 1] + eta[t]
    viv = s_eta ** 2 / (1 - beta ** 2)
    su = np.linspace(0, 0.6, 13)
    slope = []
    for s2 in su:
        rv = iv + np.sqrt(s2) * rng.standard_normal(n)
        slope.append(np.polyfit(rv[:-1], rv[1:], 1)[0])
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.0))
    axes[0].plot(su, slope, 'o', color=IDAred, ms=4, label='Simulated OLS slope')
    g = np.linspace(0, 0.6, 100)
    axes[0].plot(g, beta * viv / (viv + g), color=MainBlue, lw=1.3, label='plim: $\\beta\\,\\mathrm{Var(IV)}/(\\mathrm{Var(IV)} + \\sigma_u^2)$')
    axes[0].axhline(beta, color=Black, lw=0.8, ls='--', label=f'True slope $\\beta$ = {beta}')
    axes[0].set_xlabel('Measurement-error variance $\\sigma_u^2$')
    iq = np.linspace(0, 40, 200)
    axes[1].plot(iq, viv / (viv + 2 * iq / 78), color=Forest, lw=1.4,
                 label='Weight $\\lambda = \\sigma^2_{IV}/(\\sigma^2_{IV} + 2\\,\\mathrm{IQ}_t/M)$, M = 78 (illustration)')
    axes[1].set_xlabel('$\\mathrm{IQ}_t$')
    axes[1].set_ylim(0, 1.05)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch9_sem_a7')
    k = int(np.argmin(np.abs(su - 0.25)))
    return {'viv': float(viv), 'slope25': float(slope[k]), 'plim25': float(beta * viv / (viv + 0.25))}


def sc_a8(X):
    """A8: the DM test against N(0,1) and the 95% confidence ellipse for (a, b) from the MZ regression."""
    V = np.array([[X['se_a'] ** 2, X['cov']], [X['cov'], X['se_b'] ** 2]])
    est = np.array([X['a'], X['b']])
    c2 = stats.chi2.ppf(0.95, 2)
    w, U = np.linalg.eigh(V)
    th = np.linspace(0, 2 * np.pi, 400)
    ell = est[:, None] + U @ (np.sqrt(w * c2)[:, None] * np.vstack([np.cos(th), np.sin(th)]))
    v = U[:, 0]                                                      # direction of the minor axis
    s_ = np.sqrt(25.0 / (v @ np.linalg.solve(V, v)))                  # hypothetical point with W = 25
    hyp = est + s_ * v
    t_h = (hyp - est) / np.sqrt(np.diag(V))
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.2), gridspec_kw={'width_ratios': [1, 1.3]})
    x = np.linspace(-4, 4, 300)
    axes[0].plot(x, stats.norm.pdf(x), color=MainBlue, lw=1.2, label='N(0,1) under equal accuracy')
    axes[0].axvline(X['dm_t'], color=IDAred, lw=1.4, label=f"DM t = {X['dm_t']:.2f}")
    for s in (-1.96, 1.96):
        axes[0].axvline(s, color=Forest, lw=1.0, ls='--', label='$\\pm 1.96$' if s > 0 else None)
    axes[0].set_xlabel('DM statistic')
    axes[1].plot(ell[0], ell[1], color=MainBlue, lw=1.4, label='95% joint confidence ellipse')
    axes[1].scatter(*est, color=MainBlue, s=22, zorder=3, label=f"Estimate ({X['a']:.2f}, {X['b']:.2f})")
    axes[1].scatter([0], [1], color=IDAred, marker='x', s=40, zorder=3, label='Null (0, 1): inside, W = %.2f' % X['wald'])
    axes[1].scatter(*hyp, color=Purple, marker='D', s=20, zorder=3, label='Hypothetical null: W = 25, both |t| < 1.96')
    for k, (e, se) in enumerate([(X['a'], X['se_a']), (X['b'], X['se_b'])]):
        f = axes[1].axvline if k == 0 else axes[1].axhline
        for s in (-1, 1):
            f(e + s * 1.96 * se, color=Black, lw=0.7, ls=':')
    axes[1].set_xlabel('Intercept $a$')
    axes[1].set_ylabel('Slope $b$')
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_a8')
    return {'hyp_a': float(hyp[0]), 'hyp_b': float(hyp[1]), 'hyp_ta': float(t_h[0]), 'hyp_tb': float(t_h[1])}


def sc_b1(day='2021-08-27'):
    """B1: one day computed step by step; raw vs periodicity-adjusted z; ordered p-values vs the BH threshold; factors f_i."""
    j = T.jump_test(R_SPY)
    N = len(j)
    p = np.sort(stats.norm.sf(j['z'].values))
    f = periodicity_sd(R_SPY, j['bv'])
    js = T.jump_test(R_SPY / f.values[None, :])
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.0))
    bins = np.linspace(-4, 8, 61)
    axes[0].hist(j['z'], bins=bins, density=True, histtype='step', color=IDAred, lw=1.2, label='z, raw returns')
    axes[0].hist(js['z'], bins=bins, density=True, histtype='step', color=MainBlue, lw=1.2, label='z, returns divided by $f_i$')
    xx = np.linspace(-4, 8, 300)
    axes[0].plot(xx, stats.norm.pdf(xx), color=Forest, lw=1.0, ls='--', label='N(0,1)')
    axes[0].set_xlabel('Daily ratio statistic z')
    k = np.arange(1, 121)
    axes[1].plot(k, p[:120], 'o', ms=2.5, color=MainBlue, label='Ordered p-values $p_{(k)}$')
    axes[1].plot(k, 0.05 * k / N, color=IDAred, lw=1.2, label='BH line $0.05\\,k/N$')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('Rank $k$ (first 120 of %d)' % N)
    kbh = bh_count(p, 0.05)
    axes[1].axvline(kbh, color=Purple, lw=0.9, ls='-.', label=f'Largest k below the line: {kbh}')
    lab = pd.date_range('2000-01-01 09:35', periods=78, freq='5min')
    axes[2].bar(np.arange(78), f.values, color=Amber, width=0.8, label='Periodicity factor $f_i$ (mean of $f_i^2$ = 1)')
    ticks = [0, 12, 24, 36, 48, 60, 72]
    axes[2].set_xticks(ticks)
    axes[2].set_xticklabels([lab[i].strftime('%H:%M') for i in ticks], fontsize=7)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=4, y=0.0)
    save_fig('ch9_sem_b1')
    d = pd.Timestamp(day)
    r = R_SPY.loc[d].dropna().values
    M_ = len(r)
    row = j.loc[d]
    big = int(np.argmax(np.abs(r)))
    return {'day': day, 'M': M_, 'rv': float(row['rv']), 'bv': float(row['bv']), 'tq': float(row['tq']),
            'tqbv': float(row['tq'] / row['bv'] ** 2), 'ratio': float((row['rv'] - row['bv']) / row['rv']),
            'z': float(row['z']), 'p': float(stats.norm.sf(row['z'])), 'J': float(row['J']), 'rmax': float(r[big]),
            'rmax_share': float(r[big] ** 2 / row['rv']), 'kbh': int(kbh), 'bh_thr': float(0.05 * kbh / N),
            'p_k': float(p[kbh - 1]), 'N': int(N)}


def sc_b2():
    """B2: Bitcoin, weekend vs weekdays: rejection rate, BV/RV, daily series with the missing days."""
    j = T.jump_test(R_BTC)
    wk = j.index.dayofweek >= 5
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.0), gridspec_kw={'width_ratios': [0.8, 1, 1.6]})
    grp = {'Weekdays': ~wk, 'Weekends': wk}
    rates = [j.loc[m, 'jump'].mean() for m in grp.values()]
    axes[0].bar(list(grp), rates, color=[MainBlue, Amber], label='Share of jump days (0.1% level)')
    for i, m in enumerate(grp.values()):
        axes[0].text(i, rates[i] + 0.005, f"{int(j.loc[m, 'jump'].sum())}/{int(m.sum())}", ha='center', fontsize=8, color='black')
    axes[0].axhline(0.001, color=Black, lw=0.8, ls='--', label='Nominal level 0.001')
    bins = np.linspace(0.4, 1.3, 46)
    axes[1].hist((j['bv'] / j['rv'])[~wk], bins=bins, density=True, histtype='step', color=MainBlue, lw=1.2, label='BV/RV, weekdays')
    axes[1].hist((j['bv'] / j['rv'])[wk], bins=bins, density=True, histtype='step', color=Amber, lw=1.2, label='BV/RV, weekends')
    axes[1].set_xlabel('BV / RV')
    full = j['rv'].asfreq('D')
    axes[2].plot(full.index, np.sqrt(365 * full), color=MainBlue, lw=0.6, label='Bitcoin realised volatility (% p.a.)')
    jj = j[j['jump']]
    axes[2].scatter(jj.index, np.sqrt(365 * jj['rv']), color=IDAred, s=8, zorder=3, label='Jump day (0.1%)')
    miss = full.index[full.isna()]
    for dd in miss:
        axes[2].axvspan(dd, dd + pd.Timedelta('1D'), color=LightGray, lw=0, alpha=0.8)
    axes[2].axvspan(miss[0], miss[0], color=LightGray, label='Dropped day (< 95% of bars)')
    axes[2].tick_params(axis='x', labelsize=7)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_b2')
    return {'n_wd': int((~wk).sum()), 'n_we': int(wk.sum()), 'j_wd': int(j.loc[~wk, 'jump'].sum()),
            'j_we': int(j.loc[wk, 'jump'].sum()), 'missing': int(len(miss))}


def sc_b3(B3, XRK):
    """B3: volatility from the mean RV on one grid vs the average over grids; ratio of means with a bootstrap CI."""
    ks = ['5', '15', '30', '65']
    x = [int(k) for k in ks]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.0))
    axes[0].plot(x, [B3[k]['vol'] for k in ks], 'o-', color=MainBlue, label='One grid (sparse sampling)')
    axes[0].plot(x, [B3[k]['vol_sub'] for k in ks], 's--', color=IDAred, label='Average over shifted grids')
    axes[0].set_xticks(x)
    axes[0].set_xlabel('Sampling interval (minutes)')
    axes[0].set_ylabel('$\\sqrt{252\\,\\overline{\\mathrm{RV}}}$ (% p.a.)')
    axes[0].set_ylim(11.5, 14)
    lab = ['15 min', '30 min', '65 min', 'Kernel (5 min)']
    est = [B3[k]['ratio'] for k in ks[1:]] + [XRK['ratio']]
    lo = [B3[k]['lo'] for k in ks[1:]] + [XRK['lo']]
    hi = [B3[k]['hi'] for k in ks[1:]] + [XRK['hi']]
    yy = np.arange(len(lab))
    axes[1].errorbar(est, yy, xerr=[np.subtract(est, lo), np.subtract(hi, est)], fmt='o', color=MainBlue, capsize=3,
                     label='Ratio of means to 5-minute RV, 95% block-bootstrap CI')
    axes[1].axvline(1, color=Black, lw=0.9, ls='--', label='Ratio = 1')
    axes[1].set_yticks(yy)
    axes[1].set_yticklabels(lab)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch9_sem_b3')
    return {}


def sc_b4(day=DAY):
    """B4: returns standardised by sd(r) and by sqrt(RV): histograms and QQ plots, SPY and Bitcoin."""
    btc_oc = 100 * np.log(P_BTC.iloc[:, -1] / P_BTC[0])
    fig, axes = plt.subplots(1, 4, figsize=(10.6, 2.9))
    xx = np.linspace(-5, 5, 300)
    for c, (name, r, v) in enumerate([('SPY', OC, RV_SPY), ('Bitcoin', btc_oc, RV_BTC)]):
        z = (r / np.sqrt(v)).values
        u = (r / r.std()).values
        ax = axes[2 * c]
        ax.hist(np.clip(u, -6, 6), bins=np.linspace(-6, 6, 49), density=True, color=Amber, alpha=0.6, label='$r_t/\\mathrm{sd}(r)$')
        ax.hist(z, bins=np.linspace(-6, 6, 49), density=True, histtype='step', color=MainBlue, lw=1.2, label='$r_t/\\sqrt{\\mathrm{RV}_t}$')
        ax.plot(xx, stats.norm.pdf(xx), color=IDAred, lw=1.0, ls='--', label='N(0,1)')
        ax.set_title(name, fontsize=9, loc='left')
        ax = axes[2 * c + 1]
        q = stats.norm.ppf((np.arange(1, len(z) + 1) - 0.5) / len(z))
        ax.plot(q, np.sort(u), '.', ms=2, color=Amber, label=None)
        ax.plot(q, np.sort(z), '.', ms=2, color=MainBlue, label=None)
        ax.plot([-4, 4], [-4, 4], color=Black, lw=0.8, ls=':', label='45-degree line')
        ax.set_xlim(-4, 4)
        ax.set_ylim(-8, 8)
        ax.set_title(f'{name}: QQ plot', fontsize=9, loc='left')
        ax.set_xlabel('Normal quantile')
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=4, y=0.0)
    save_fig('ch9_sem_b4')
    d = pd.Timestamp(day)
    return {'day': day, 'r': float(OC[d]), 'rv': float(RV_SPY[d]), 'z': float(OC[d] / np.sqrt(RV_SPY[d])),
            'kbench': 3 * 78 / 80}


def sc_b5(day='2025-04-08'):
    """B5: one row of the design matrix (log-HAR), OLS vs Newey-West coefficient intervals, raw and residual ACF."""
    res, X, ok = T.har_fit(RVT_SPY, log=True)
    y = np.log(RVT_SPY)
    Xc = np.column_stack([np.ones(ok.sum()), X[ok].values])
    e = res['resid']
    se_ols = np.sqrt(np.diag(e @ e / (len(e) - 4) * np.linalg.inv(Xc.T @ Xc)))
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.0))
    names = ['$\\beta_0$', '$\\beta_d$', '$\\beta_w$', '$\\beta_m$']
    yy = np.arange(4)
    axes[0].errorbar(res['b'], yy - 0.12, xerr=1.96 * se_ols, fmt='o', color=Amber, capsize=3, label='95% CI, OLS standard errors')
    axes[0].errorbar(res['b'], yy + 0.12, xerr=1.96 * res['se'], fmt='s', color=MainBlue, capsize=3, label='95% CI, Newey-West standard errors')
    axes[0].axvline(0, color=Black, lw=0.8, ls='--')
    axes[0].set_yticks(yy)
    axes[0].set_yticklabels(names)
    axes[0].invert_yaxis()
    lags = np.arange(1, 41)
    yv = y[ok].values - y[ok].mean()
    ac_y = [np.corrcoef(yv[l:], yv[:-l])[0, 1] for l in lags]
    ac_e = [np.corrcoef(e[l:], e[:-l])[0, 1] for l in lags]
    axes[1].bar(lags - 0.2, ac_y, 0.4, color=MainBlue, label='ACF of $\\ln V_t$')
    axes[1].bar(lags + 0.2, ac_e, 0.4, color=IDAred, label='ACF of log-HAR residuals')
    band = 1.96 / np.sqrt(len(e))
    axes[1].axhspan(-band, band, color=LightGray, alpha=0.7, lw=0, zorder=0, label='$\\pm 1.96/\\sqrt{T}$')
    axes[1].set_xlabel('Lag (trading days)')
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch9_sem_b5')
    d = pd.Timestamp(day)
    xr = X.loc[d]
    return {'day': day, 'y': float(y[d]), 'xd': float(xr['d']), 'xw': float(xr['w']), 'xm': float(xr['m']),
            'fit': float(res['b'][0] + res['b'][1:] @ xr.values), 'T': int(res['T']), 'N': int(len(RVT_SPY)),
            'ac_e1': float(ac_e[0]), 'ac_y1': float(ac_y[0])}


def sc_b6():
    """B6: 5-day target, direct log-HAR and GARCH(1,1)-t forecasts, cumulative QLIKE difference."""
    v = RVT_SPY
    y5 = v[::-1].rolling(5).sum()[::-1]
    X = T.har_design(np.log(v))
    ok = X.notna().all(axis=1) & y5.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    ly = np.log(y5).values
    idx = np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]
    fh = {}
    for t in idx:
        tr = np.where(ok.values[:t - 4])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], ly[tr], rcond=None)
        fh[v.index[t]] = np.exp(Xc[t] @ b + np.var(ly[tr] - Xc[tr] @ b) / 2)
    fh = pd.Series(fh)
    G = garch_params_blocks(D_SPY, fh.index)
    pers = G['alpha'] + G['beta']
    lr = G['omega'] / (1 - pers)
    fg = sum(lr + pers ** h * (G['s2'] - lr) for h in range(5))
    yy = y5.reindex(fh.index)
    fig, axes = plt.subplots(2, 1, figsize=(9.4, 4.2), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    axes[0].plot(yy.index, yy, color=MainBlue, lw=0.6, label='Realised 5-day variance $Y_t$ (%$^2$)')
    axes[0].plot(fh.index, fh, color=IDAred, lw=0.9, label='Direct log-HAR forecast')
    axes[0].plot(fg.index, fg, color=Forest, lw=0.9, label='GARCH(1,1)-t forecast')
    axes[0].set_yscale('log')
    cd = (T.qlike(yy, fg) - T.qlike(yy, fh)).cumsum()
    axes[1].plot(cd.index, cd, color=Purple, lw=1.1, label='Cumulative QLIKE: GARCH minus log-HAR (rising = log-HAR better)')
    axes[1].axhline(0, color=Black, lw=0.7)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch9_sem_b6')
    return {'cum_end': float(cd.iloc[-1]), 'first': str(fh.index[0].date()), 'last': str(fh.index[-1].date())}


def sc_b7():
    """B7: continuous and jump components of SPY variance; jump coefficients; cumulative QLIKE HAR-CJ minus log-HAR."""
    j = T.jump_test(R_SPY)
    C = j['C'] + ON ** 2
    Jc = j['J']
    v = RVT_SPY
    X = pd.DataFrame({'cd': np.log(C).shift(1), 'cw': np.log(C.rolling(5).mean()).shift(1),
                      'cm': np.log(C.rolling(22).mean()).shift(1), 'jd': np.log1p(Jc).shift(1),
                      'jw': np.log1p(Jc.rolling(5).mean()).shift(1), 'jm': np.log1p(Jc.rolling(22).mean()).shift(1)})
    y = np.log(v)
    ok = X.notna().all(axis=1)
    res = T.ols_nw(y[ok], X[ok])
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        f[v.index[t]] = np.exp(Xc[t] @ b + np.var(y.values[tr] - Xc[tr] @ b) / 2)
    f = pd.Series(f)
    fl = T.har_expanding(v, '2022-01-03', log=True).reindex(f.index)
    yy = v.reindex(f.index)
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.0), gridspec_kw={'width_ratios': [1.6, 0.9, 1.2]})
    axes[0].plot(C.index, C, color=MainBlue, lw=0.5, label='Continuous part $C_t$ (incl. overnight, %$^2$)')
    jj = Jc[Jc > 0]
    axes[0].scatter(jj.index, jj, color=IDAred, s=8, zorder=3, label='Jump part $J_t > 0$ (%$^2$)')
    axes[0].set_yscale('log')
    axes[0].tick_params(axis='x', labelsize=7)
    nm = ['$\\beta_{Jd}$', '$\\beta_{Jw}$', '$\\beta_{Jm}$']
    axes[1].errorbar(res['b'][4:], np.arange(3), xerr=1.96 * res['se'][4:], fmt='o', color=IDAred, capsize=3,
                     label='Jump coefficients, 95% Newey-West CI')
    axes[1].axvline(0, color=Black, lw=0.8, ls='--')
    axes[1].set_yticks(range(3))
    axes[1].set_yticklabels(nm)
    axes[1].invert_yaxis()
    cd = (T.qlike(yy, f) - T.qlike(yy, fl)).cumsum()
    axes[2].plot(cd.index, cd, color=Purple, lw=1.1, label='Cumulative QLIKE: HAR-CJ minus log-HAR (rising = log-HAR better)')
    axes[2].axhline(0, color=Black, lw=0.7)
    axes[2].tick_params(axis='x', labelsize=7)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch9_sem_b7')
    return {'n_jump_days': int((Jc > 0).sum()), 'cum_end': float(cd.iloc[-1])}


def sc_b8():
    """B8: log m(q, D) against log D (SPY, total variance), slopes zeta_q for four measures, simulated check with and without noise."""
    series = {'Total variance': RVT_SPY, 'Intraday RV': RV_SPY, 'BV': T.bv(R_SPY), 'RV 30 min, subsampled': T.subsampled_rv(P_SPY, 6)}
    qs = (0.5, 1.0, 1.5, 2.0, 3.0)
    x = 0.5 * np.log(RVT_SPY.values)
    ro = T.roughness(x, qs)
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.1))
    cols = [MainBlue, Forest, Amber, IDAred, Purple]
    L = np.log(ro['lags'])
    for q, c in zip(qs, cols):
        axes[0].plot(L, np.log(ro['m'][q]), 'o', ms=2.5, color=c, label=f'q = {q}')
        a1, a0 = np.polyfit(L, np.log(ro['m'][q]), 1)
        axes[0].plot(L, a0 + a1 * L, color=c, lw=0.9)
    axes[0].set_xlabel('$\\ln \\Delta$ (trading days)')
    axes[0].set_ylabel('$\\ln m(q, \\Delta)$')
    axes[0].set_title('SPY, total variance', fontsize=9, loc='left')
    for (name, s), c in zip(series.items(), [MainBlue, Forest, Amber, Purple]):
        r = rough_H(0.5 * np.log(s.values))
        axes[1].plot(qs, [r['zeta'][q] for q in qs], 'o-', color=c, ms=3, lw=0.9, label=f"{name}: H = {r['H']:.2f}")
    axes[1].plot(qs, [0.5 * q for q in qs], color=Black, lw=0.8, ls=':', label='H = 0.5')
    axes[1].set_xlabel('q')
    axes[1].set_ylabel('Slope $\\zeta_q$')
    rng = np.random.default_rng(SEED)
    n = len(RVT_SPY)
    z = np.cumsum(0.1 * rng.standard_normal(n))
    z = z - np.linspace(0, z[-1], n)
    zn = z + 0.25 * rng.standard_normal(n)
    for arr, c, lab in [(z, Teal, 'Simulated bridge, H = 0.5'), (zn, Orange, 'Same bridge plus i.i.d. noise')]:
        rr = T.roughness(arr, (2.0,))
        axes[2].plot(np.log(rr['lags']), np.log(rr['m'][2.0]), 'o-', ms=2.5, lw=0.8, color=c, label=lab)
    axes[2].plot(L, np.log(ro['m'][2.0]), 'o-', ms=2.5, lw=0.8, color=MainBlue, label='SPY total variance')
    axes[2].set_xlabel('$\\ln \\Delta$')
    axes[2].set_ylabel('$\\ln m(2, \\Delta)$')
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=4, y=0.0)
    save_fig('ch9_sem_b8')
    a1, a0 = np.polyfit(L, np.log(ro['m'][2.0]), 1)
    return {'m21': float(ro['m'][2.0][0]), 'zeta2': float(a1), 'icpt2': float(a0), 'n_pairs1': int(np.isfinite(x).sum() - 1)}


def sc_b9(XQS):
    """B9: MCS p-values (lines at 0.10 and 0.25) and mean QLIKE by model."""
    pv = XQS['mcs']['pvalues']
    order = sorted(pv, key=lambda m: pv[m])
    lab = {'logHAR': 'log-HAR', 'GARCH-t': 'GARCH(1,1)-t', 'RW': "Yesterday's RV"}
    names = [lab.get(m, m) for m in order]
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.0))
    yy = np.arange(len(order))
    axes[0].scatter([pv[m] for m in order], yy, color=[IDAred if m in XQS['mcs']['included'] else MainBlue for m in order],
                    s=26, zorder=3, label='MCS p-value (red: in the 90% set)')
    axes[0].axvline(0.10, color=Forest, lw=1.0, ls='--', label='Size 0.10 (90% set)')
    axes[0].axvline(0.25, color=Purple, lw=1.0, ls='-.', label='Size 0.25 (75% set)')
    axes[0].set_yticks(yy)
    axes[0].set_yticklabels(names)
    axes[0].set_xlabel('MCS p-value (elimination order from top)')
    axes[1].barh(yy, [XQS['qlike'][m] for m in order], color=Amber, label=f"Mean QLIKE, {XQS['mcs']['T']:,} days")
    axes[1].set_yticks(yy)
    axes[1].set_yticklabels(names)
    axes[1].set_xlim(0.25, 0.52)
    plt.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch9_sem_b9')
    return {'order': order}


def sc_c1(C1):
    """C1: bootstrap distribution (28-day calendar blocks) of the R^2 difference, Bitcoin minus SPY."""
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True).loc[C_START:]
    Fb = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_btc.csv'), index_col=0, parse_dates=True).loc[C_START:]
    a = np.c_[np.log(F['proxy']), np.log(F['logHAR'])]
    b = np.c_[np.log(Fb['proxy']), np.log(Fb['logHAR'])]
    cal = pd.date_range(min(F.index[0], Fb.index[0]), max(F.index[-1], Fb.index[-1]), freq='D')
    rowa = np.full(len(cal), -1)
    rowa[cal.get_indexer(F.index)] = np.arange(len(F))
    rowb = np.full(len(cal), -1)
    rowb[cal.get_indexer(Fb.index)] = np.arange(len(Fb))
    rng = np.random.default_rng(SEED)
    block, ncal = 28, len(cal)
    nb = int(np.ceil(ncal / block))

    def r2(x, rows):
        rows = rows[rows >= 0]
        return np.corrcoef(x[rows, 0], x[rows, 1])[0, 1] ** 2
    d = np.empty(B_BOOT)
    for i in range(B_BOOT):
        st = rng.integers(0, ncal - block + 1, nb)
        days = (st[:, None] + np.arange(block)[None, :]).ravel()[:ncal]
        d[i] = r2(b, rowb[days]) - r2(a, rowa[days])
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    ax.hist(d, bins=50, color=Amber, alpha=0.8, label=f'Bootstrap $R^2$ difference, Bitcoin minus SPY ({B_BOOT:,} resamples)')
    ax.axvline(0, color=Black, lw=0.9, ls='--', label='No difference')
    ax.axvline(C1['r2diff'], color=IDAred, lw=1.4, label=f"Observed difference {C1['r2diff']:.2f}")
    for q in (2.5, 97.5):
        ax.axvline(np.percentile(d, q), color=MainBlue, lw=1.0, ls=':', label='95% percentile interval' if q < 50 else None)
    ax.set_xlabel('$R^2$ difference (log RV on log forecast)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch9_sem_c1_boot')
    return {'lo': float(np.percentile(d, 2.5)), 'hi': float(np.percentile(d, 97.5)), 'cal_days': int(ncal),
            'spy_T': int(len(F)), 'btc_T': int(len(Fb))}


def sem_charts():
    """All seminar charts; uses the results already saved in sem9_results.json for the expensive blocks."""
    with open(os.path.join(HERE, 'sem9_results.json')) as fh:
        R_ = json.load(fh)
    out = {'day': sc_day(), 'a1': sc_a1(), 'a2': sc_a2(R_['A2']), 'a3': sc_a3(), 'a4': sc_a4(R_['A4']), 'a5': sc_a5(),
           'a6': sc_a6(R_['XA6']), 'a7': sc_a7(), 'a8': sc_a8(R_['XA8']), 'b1': sc_b1(), 'b2': sc_b2(),
           'b3': sc_b3(R_['B3'], R_['XRK']), 'b4': sc_b4(), 'b5': sc_b5(), 'b6': sc_b6(), 'b7': sc_b7(), 'b8': sc_b8(),
           'b9': sc_b9(R_['XQS']), 'c1': sc_c1(R_['C1'])}
    return out


if __name__ == '__main__':
    ONLY = sys.argv[1:]                              # optional: recompute only the named blocks, the rest are read from the json
    S = {}
    if ONLY:
        with open(os.path.join(HERE, 'sem9_results.json')) as fh:
            S = json.load(fh)
    for name, f in [('A1', a1_rv_bv), ('A2', a2_jump), ('A3', a3_noise), ('A4', a4_tsrv), ('A5', a5_har), ('A6', a6_losses),
                    ('A7', a7_har2), ('A8', a8_dm), ('B1', b1_spy_jumps), ('B2', b2_btc_jumps), ('B3', b3_frequency),
                    ('B4', b4_standardised), ('B5', b5_har_insample), ('B6', b6_week), ('B7', b7_harcj), ('B8', b8_rough),
                    ('C1', c1_predictability), ('XJ', ex_jump_inference), ('XAR', ex_har_ar22),
                    ('XQS', ex_harq_shar), ('XGW', ex_gw_week), ('XRK', ex_rk_ratio), ('XA8', ex_a8_mz),
                    ('XA6', ex_a6_jensen), ('SC', sem_charts)]:
        if ONLY and name not in ONLY:
            continue
        print(name)
        S[name] = f()
    with open(os.path.join(HERE, 'sem9_results.json'), 'w') as fh:
        json.dump(jsonable(S), fh, indent=1)
    print('saved sem9_results.json')

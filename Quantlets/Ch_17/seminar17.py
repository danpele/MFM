"""
seminar17.py -- calculele Seminarului 17 (MFM): bule si crahuri
===============================================================
Partea A: valoarea prezenta si bula rationala, bula Blanchard-Watson, ADF la dreapta pas cu pas, ferestrele PSY,
          modelul Markov-switching (durate, probabilitati stationare, un pas al filtrului Hamilton), LPPLS (filtre).
Partea B: GSADF pe raportul P/D Shiller (sensibilitatea la fereastra minima), SADF vs GSADF, Bitcoin cu valori
          critice Monte Carlo vs wild bootstrap, BET si BET-FI, instabilitatea lui tc (LPPLS), indicatorul de incredere
          pentru Nasdaq 100, Markov-switching pe S&P 500 si pe Bitcoin (2 vs 3 regimuri).
Partea C: exista o bula AI? NVIDIA si Nasdaq 100 vs episodul dot-com Cisco.
Cifrele sunt salvate in sem17_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import LABELS, price, shiller   # noqa: E402
from bubbles import (psy, psy_cv, wild_cv, episodes, min_window, lppls_fit, lppls_qualified,   # noqa: E402
                     lppls_confidence, drawdown, LPPLS_WINDOWS, LPPLS_SEARCH, LPPLS_FILTER)
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Magenta, Gray,  # noqa: E402
                                 SEED, save_fig, legend_outside_bottom, fig_legend, jsonable, yrs, todate, d2s,
                                 run_psy, summarise, real_time, ms_fit, ms_summary, ci_evaluation, HERE,
                                 QL_RAW, _chg)


# =============================================================================
# PART A
# =============================================================================
def a1_present_value(D1=2.0, r=0.06, g=0.02, P=65.0):
    """Gordon: F = D1 / (r - g); the bubble B = P - F grows at r, the fundamental at g."""
    F = D1 / (r - g)
    B = P - F
    out = dict(F=F, B=B, share0=B / P)
    for h in (5, 30, 100):
        Fh, Bh = F * (1 + g) ** h, B * (1 + r) ** h
        out[f'F{h}'], out[f'B{h}'], out[f'share{h}'] = Fh, Bh, Bh / (Fh + Bh)
    return out


def a2_blanchard_watson(B0=15.0, r=0.06, pi=0.9, h=5):
    """Blanchard-Watson bubble: survives with probability pi per year; conditional on survival it grows at (1+r)/pi."""
    return dict(growth=(1 + r) / pi - 1, surv=pi ** h, life=1 / (1 - pi), EB=B0 * (1 + r) ** h,
                B_surv=B0 * ((1 + r) / pi) ** h, pi=pi, h=h,
                csd=B0 * (1 + r) * np.sqrt((1 - pi) / pi),          # conditional standard deviation (no noise)
                log_slope=-(1 - pi))                                # slope of E[Delta y | y] in logs


def _df_t(Y):
    """t-statistic of b in Delta y_t = a + b y_{t-1} + e_t, for each row of Y."""
    X, Z = Y[:, :-1], np.diff(Y, axis=1)
    n = Z.shape[1]
    sx, sxx, sz, sxz, szz = X.sum(1), (X * X).sum(1), Z.sum(1), (X * Z).sum(1), (Z * Z).sum(1)
    dd = n * sxx - sx ** 2
    bb = (n * sxz - sx * sz) / dd
    aa = (sz - bb * sx) / n
    return bb / np.sqrt((szz - aa * sz - bb * sxz) / (n - 2) * n / dd)


def a3_df_limit(T=1000, R=20_000):
    """Dickey-Fuller distribution with a constant: simulation for large T; mean of the limit numerator = -1/2."""
    rng = np.random.default_rng(SEED)
    tt = np.concatenate([_df_t(np.cumsum(rng.standard_normal((2000, T + 1)), axis=1)) for _ in range(R // 2000)])
    # limit functional approximated on a grid of T points: numerator 1/2 (W(1)^2 - 1) - W(1) int W
    W = np.cumsum(rng.standard_normal((5000, T)), axis=1) / np.sqrt(T)
    num = 0.5 * (W[:, -1] ** 2 - 1) - W[:, -1] * W.mean(1)
    return dict(T=T, R=R, q05=float(np.quantile(tt, 0.05)), q50=float(np.quantile(tt, 0.50)),
                q95=float(np.quantile(tt, 0.95)), q99=float(np.quantile(tt, 0.99)),
                p_neg=float((tt < 0).mean()), num_mean=float(num.mean()))


def a4_mild(Ts=(100, 400, 1600), alpha=0.8, c=1.0, R=4000):
    """Mildly explosive root rho_T = 1 + c / T^alpha: the median ADF statistic grows with T (diverges to +inf)."""
    rng = np.random.default_rng(SEED)
    out = []
    for T in Ts:
        rho = 1 + c / T ** alpha
        e = rng.standard_normal((R, T))
        Y = np.zeros((R, T + 1))
        for t in range(T):
            Y[:, t + 1] = rho * Y[:, t] + e[:, t]
        tt = _df_t(Y)
        out.append(dict(T=T, rho=rho, rhoT=float(rho ** T), med=float(np.median(tt)), rej=float((tt > 1.28).mean())))
    return out


def a4_windows(T=440):
    """PSY windows for T = 440."""
    w0, r0 = min_window(T)
    n_sadf = T - w0 + 1
    return dict(T=T, r0=r0, w0=w0, n_sadf=n_sadf, n_gsadf=n_sadf * (n_sadf + 1) // 2, logT=float(np.log(T)),
                L=int(np.ceil(np.log(T))))


def _ms_step(P, mu, sd, prev_turb, r):
    """One step of the two-regime Hamilton filter (0 = calm, 1 = turbulent)."""
    prev = np.array([1 - prev_turb, prev_turb])
    pred = P.T @ prev                          # here P[i, j] = P(s_t = j | s_{t-1} = i): rows are the previous regime (the transpose of the statsmodels layout)
    lik = stats.norm.pdf(r, mu, sd)
    post = pred * lik / (pred * lik).sum()
    return pred, lik, post


def a5_markov(P=((0.98, 0.02), (0.10, 0.90)), mu=(0.3, -0.5), sd=(2.0, 5.0), prev_turb=0.2, r=-6.0):
    P, mu, sd = np.array(P), np.array(mu), np.array(sd)
    dur = 1 / (1 - np.diag(P))
    pi_turb = P[0, 1] / (P[0, 1] + P[1, 0])
    pi = np.array([1 - pi_turb, pi_turb])
    m = pi @ mu
    v = pi @ (sd ** 2) + pi @ (mu - m) ** 2
    pred, lik, post = _ms_step(P, mu, sd, prev_turb, r)
    return dict(dur_calm=dur[0], dur_turb=dur[1], pi_calm=pi[0], pi_turb=pi[1], mean=m, var=v, sd=np.sqrt(v),
                pred_turb=pred[1], lik_calm=lik[0], lik_turb=lik[1], post_turb=post[1], r=r, prev=prev_turb)


def a6_markov(P=((0.95, 0.05), (0.20, 0.80)), mu=(0.4, -1.0), sd=(2.0, 6.0), prev_turb=0.1, r=1.0):
    out = a5_markov(P, mu, sd, prev_turb, r)
    P = np.array(P)
    two = np.array([1 - out['post_turb'], out['post_turb']]) @ np.linalg.matrix_power(P, 2)
    out['two_step_turb'] = two[1]
    return out


def _lppls_diag(t1, t2, tc, m, w, B, C1, C2):
    """The conditions of Shu & Zhu (2020), eqs. (11)-(12), that can be checked from the parameters (no data)."""
    C = np.hypot(C1, C2)
    D = t2 - t1
    O = w / np.pi * np.log((tc - t1) / (tc - t2))          # number of half-periods (Shu & Zhu 2020, eq. 12)
    damp = m * abs(B) / (w * C)
    exact = m * abs(B) / (C * np.hypot(m, w))              # hazard rate >= 0 for every phase: m|B| >= |C| sqrt(m^2 + w^2)
    slope = -B * m * (tc - t2) ** (m - 1)          # d/dt [B (tc - t)^m] at t2, without oscillations
    return dict(C=C, D=D, O=O, damping=damp, exact=exact, dtc=tc - t2, dtc_days=(tc - t2) * 365.25, tc_lim=D / 5,
                slope=slope, m=m, w=w, B=B, ok_B=B < 0, ok_m=0.01 <= m <= 0.99, ok_w=2 <= w <= 25,
                ok_tc=0 <= tc - t2 <= D / 5, ok_O=O >= 2.5, ok_D=damp >= 1, ok_exact=exact >= 1)


def a7_lppls():
    return _lppls_diag(2025.0, 2026.0, 2026.08, 0.5, 8.0, -1.2, 0.06, -0.02)


def a8_lppls():
    return _lppls_diag(2025.0, 2026.0, 2026.45, 0.95, 3.5, -0.8, 0.25, 0.0)


# =============================================================================
# PART B
# =============================================================================
def b1_pd_windows(r0s=(0.03, None, 0.08)):
    """GSADF on the Shiller P/D ratio for three minimum windows (the PSY rule in the middle)."""
    sh = shiller()
    y = np.log(sh['PD'])
    out = []
    for r0 in r0s:
        res = psy(y.values, r0)
        cv = psy_cv(res['n'], res['w0'], 1000, SEED)
        L = int(np.ceil(np.log(res['n'])))
        ep = episodes(res['bsadf'], cv['bsadf95'], y.index[1:], L)
        out.append(dict(r0=res['r0'], w0=res['w0'], gsadf=res['gsadf'], cv95=cv['gsadf']['95'], cv99=cv['gsadf']['99'],
                        episodes=[dict(start=d2s(s), end=d2s(e), n=int(n), change=_chg(y, s, e)) for s, e, n in ep]))
    return out


def b2_sadf_vs_gsadf():
    """Nasdaq 100 and S&P 500 monthly: PWY date-stamping (fixed start) vs PSY (moving start)."""
    out = {}
    for k in ['ndx', 'sp500']:
        y = np.log(price(k, 'M'))
        o = run_psy(y)
        out[k] = summarise(o, y)
    return out


def b3_btc_wild():
    """Bitcoin weekly: Monte Carlo critical values (Gaussian random walk) vs wild bootstrap."""
    y = np.log(price('btc', 'W'))
    o = run_psy(y, wild=True)
    idx = o['idx']
    dy = np.diff(y.values)
    vol = pd.Series(dy, index=idx).rolling(26).std() * np.sqrt(52)
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.2]))
    axes[0].plot(vol.index, 100 * vol.values, color=Teal, lw=0.9, label='Annualised volatility, 26-week window (%)')
    axes[0].set_ylabel('%')
    axes[1].plot(idx, o['res']['bsadf'], color=IDAred, lw=0.9, label='BSADF statistic')
    axes[1].plot(idx, o['cv']['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% critical value, Monte Carlo')
    axes[1].plot(idx, o['wild']['bsadf95'], color=Purple, lw=1.0, ls='-.', label='95% critical value, wild bootstrap')
    axes[1].set_ylabel('Statistic')
    axes[0].set_title('Bitcoin, weekly 2014-2026: volatility changes the critical values', fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_sem_btc_wild')
    s = summarise(o, y)
    s['vol_first'] = float(vol.dropna().iloc[:52].mean())
    s['vol_last'] = float(vol.dropna().iloc[-52:].mean())
    s['wild_bs_max'] = float(np.nanmax(o['wild']['bsadf95']))
    s['mc_bs_max'] = float(np.nanmax(o['cv']['bsadf95']))
    return s


def b4_bvb():
    """BET monthly 1997-2026 and BET-FI weekly 2012-2026: GSADF, episodes (Monte Carlo and wild bootstrap)."""
    out = {}
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.2))
    for ax, (k, f, title) in zip(axes, [('bet', 'M', 'BET, monthly 1997-2026'), ('betfi', 'W', 'BET-FI, weekly 2012-2026')]):
        y = np.log(price(k, f))
        o = run_psy(y, wild=True)
        out[k] = summarise(o, y)
        out[k]['real_time'] = real_time(o, price(k, 'D'))
        ax.plot(o['idx'], o['res']['bsadf'], color=IDAred, lw=0.9, label='BSADF statistic')
        ax.plot(o['idx'], o['cv']['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% critical value, Monte Carlo')
        ax.plot(o['idx'], o['wild']['bsadf95'], color=Purple, lw=1.0, ls='-.', label='95% critical value, wild bootstrap')
        ax.set_title(title, fontsize=8.5, loc='left')
        ax.set_ylabel('Statistic')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig('ch17_sem_bvb')
    return out


def b5_tc_windows(t2='2017-11-15', starts=('2016-06-01', '2017-08-01')):
    """LPPLS on Bitcoin with a fixed t2 and a moving window start t1 (weekly): the distribution of tc."""
    p = price('btc', 'D')
    rows = []
    for t1 in pd.date_range(starts[0], starts[1], freq='7D'):
        w = p.loc[t1:t2]
        f = lppls_fit(yrs(w.index), np.log(w.values))
        rows.append(dict(t1=w.index[0], tc=todate(f['tc']), m=f['m'], w=f['w'], q=lppls_qualified(f),
                         at_bound=bool(f['m'] <= 0.002 or f['m'] >= 0.998 or f['w'] <= 1.01 or f['w'] >= 49.9)))
    d = pd.DataFrame(rows)
    pk = p.loc['2017'].idxmax()
    err = (d['tc'] - pk).dt.days
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(d['t1'], d['tc'], 'o', color=IDAred, ms=3.5, label='Estimated $t_c$ (window start $t_1$ on the x-axis)')
    ax.plot(d.loc[d['q'], 't1'], d.loc[d['q'], 'tc'], 'o', mfc='none', mec=MainBlue, ms=7, label='Qualified fit')
    ax.axhline(pk, color=Forest, ls='--', lw=1.0, label=f'Actual peak {pk.date()}')
    ax.axhline(pd.Timestamp(t2), color=Gray, ls=':', lw=0.8)
    ax.set_xlabel('Start of the estimation window $t_1$')
    ax.set_ylabel('Estimated $t_c$')
    ax.set_title(f'Bitcoin, estimation window ends on {t2}: $t_c$ depends on where the window starts', fontsize=9, loc='left')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch17_sem_tc_windows')
    return dict(n=int(len(d)), t2=t2, peak=d2s(pk), tc_min=d2s(d['tc'].min()), tc_max=d2s(d['tc'].max()),
                tc_med=d2s(d['tc'].sort_values().iloc[len(d) // 2]), iqr_days=float(np.subtract(*np.percentile(err, [75, 25]))),
                share_q=float(d['q'].mean()), share_bound=float(d['at_bound'].mean()),
                share_30=float((err.abs() <= 30).mean()), med_err=float(err.median()))


def b6_ci_ndx():
    """LPPLS confidence indicator for the Nasdaq 100, 1997-2002 (precomputed in the lecture), and its evaluation."""
    path = os.path.join(HERE, 'ch17_lppls_ci_ndx.csv')
    ci = pd.read_csv(path if os.path.exists(path) else QL_RAW + 'ch17_lppls_ci_ndx.csv', index_col=0, parse_dates=True)['ci']
    p = price('ndx', 'D', '1994-01-01')
    ev = ci_evaluation(ci, p)
    w = ci.loc['1997':'2002']
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.8), sharex=True, gridspec_kw=dict(height_ratios=[1.3, 1]))
    pp = p.loc['1997':'2002']
    axes[0].plot(pp.index, pp.values, color=MainBlue, lw=0.8, label='Nasdaq 100 (log scale)')
    axes[0].set_yscale('log')
    axes[1].bar(w.index, w.values, width=12, color=IDAred, label='LPPLS confidence indicator')
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel('Share')
    axes[0].set_title('Nasdaq 100, 1997-2002: real-time LPPLS confidence indicator', fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_sem_ci_ndx')
    ev['on_1999_2000'] = float((ci.loc['1999-01-01':'2000-03-27'] > 0).mean())
    ev['first_on'] = d2s(ci[ci > 0].index[0]) if (ci > 0).any() else None
    ev['max'] = float(ci.max())
    ev['max_date'] = d2s(ci.idxmax())
    ev['on_dates'] = [d2s(d) for d in ci[ci > 0].index]
    return ev


def b7_ms_sp():
    """Two-regime Markov switching on the weekly S&P 500, 1990-2026."""
    p, r, res, hi = ms_fit('sp500', '1990-01-01')
    out = ms_summary(res, hi, r)
    fp = res.filtered_marginal_probabilities[hi]
    sp = res.smoothed_marginal_probabilities[hi]
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.8), sharex=True, gridspec_kw=dict(height_ratios=[1.2, 1]))
    axes[0].plot(p.index, p.values, color=MainBlue, lw=0.8, label='S&P 500 (log scale)')
    axes[0].set_yscale('log')
    axes[1].plot(fp.index, fp.values, color=IDAred, lw=0.7, label='Filtered probability (full-sample parameters)')
    axes[1].plot(sp.index, sp.values, color=Forest, lw=1.0, label='Smoothed probability (full sample)')
    axes[1].set_ylabel('P(turbulent regime)')
    axes[0].set_title('S&P 500, weekly log returns 1990-2026: two-regime Markov-switching model', fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig('ch17_sem_ms_sp')
    for tag, a, b in [('dotcom', '2000-01-01', '2000-12-31'), ('gfc', '2008-09-01', '2008-12-31'), ('covid', '2020-02-15', '2020-04-30')]:
        x = fp.loc[a:b]
        out[f'first_{tag}'] = d2s(x[x > 0.5].index[0]) if (x > 0.5).any() else None
    ssp = sp > 0.5
    out['share_turb_smoothed'] = float(ssp.mean())
    out['agree'] = float(((fp > 0.5) == ssp).mean())
    # one regime: the same mean and variance
    ll1 = float(stats.norm.logpdf(r, r.mean(), r.std(ddof=0)).sum())
    out['llf1'] = ll1
    out['lr'] = 2 * (out['llf'] - ll1)
    return out


def b8_ms_btc():
    """Bitcoin weekly: two vs three regimes (AIC, BIC), mean and volatility of each regime."""
    import statsmodels.api as sm
    p = price('btc', 'W')
    r = 100 * np.log(p).diff().dropna()
    out = {}
    for k in (2, 3):
        np.random.seed(SEED + k)                      # random search over starting values: reproducible
        res = sm.tsa.MarkovRegression(r, k_regimes=k, trend='c', switching_variance=True).fit(search_reps=30, maxiter=1000, disp=False)
        order = np.argsort([res.params[f'sigma2[{j}]'] for j in range(k)])
        out[f'k{k}'] = dict(llf=float(res.llf), aic=float(res.aic), bic=float(res.bic),
                            mu=[float(res.params[f'const[{j}]']) for j in order],
                            sd=[float(np.sqrt(res.params[f'sigma2[{j}]'])) for j in order],
                            dur=[float(res.expected_durations[j]) for j in order],
                            share=[float(res.smoothed_marginal_probabilities[j].mean()) for j in order])
        if k == 3:
            sp = res.smoothed_marginal_probabilities
            fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.8), sharex=True, gridspec_kw=dict(height_ratios=[1.2, 1]))
            axes[0].plot(p.index, p.values, color=MainBlue, lw=0.8, label='Bitcoin (log scale)')
            axes[0].set_yscale('log')
            for j, c, lab in zip(order, [Forest, Amber, IDAred], ['calm', 'intermediate', 'turbulent']):
                axes[1].plot(sp.index, sp[j].values, color=c, lw=0.8, label=f'Smoothed probability, {lab} regime')
            axes[1].set_ylabel('Probability')
            axes[0].set_title('Bitcoin, weekly 2014-2026: three-regime Markov-switching model', fontsize=9, loc='left')
            fig.tight_layout()
            fig_legend(fig, axes, ncol=2, y=0.0)
            save_fig('ch17_sem_ms_btc3')
    out['n'] = int(len(r))
    return out


# =============================================================================
# PART C: IS THERE AN AI BUBBLE?
# =============================================================================
def c1_ai():
    """NVIDIA and the Nasdaq 100 (monthly and weekly) vs Cisco in the dot-com episode: BSADF, run-ups, LPPLS today."""
    out = {}
    fig, axes = plt.subplots(3, 1, figsize=(7.4, 5.0))
    for ax, (k, a, b) in zip(axes, [('csco', '1990-01-01', '2003-12-31'), ('nvda', '1999-01-01', '2026-09-18'),
                                    ('ndx', '1990-01-01', '2026-09-18')]):
        y = np.log(price(k, 'M'))
        o = run_psy(y, wild=True)
        s = summarise(o, y)
        s['real_time'] = real_time(o, price(k, 'D'))
        out[k] = s
        m = (o['idx'] >= pd.Timestamp(a)) & (o['idx'] <= pd.Timestamp(b))
        ax.plot(o['idx'][m], o['res']['bsadf'][m], color=IDAred, lw=0.9, label='BSADF statistic')
        ax.plot(o['idx'][m], o['cv']['bsadf95'][m], color=Forest, lw=1.0, ls='--', label='95% critical value, Monte Carlo')
        ax.plot(o['idx'][m], o['wild']['bsadf95'][m], color=Purple, lw=1.0, ls='-.', label='95% critical value, wild bootstrap')
        ax.set_title(f'{LABELS[k]}, monthly', fontsize=8.5, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig('ch17_sem_ai')
    # 2-year run-ups (Greenwood-Shleifer-You), raw and net of the Nasdaq 100
    pn = price('nvda', 'M')
    pnd, pcd, pqd = price('nvda', 'D'), price('csco', 'D'), price('ndx', 'D')
    # from daily prices: last close up to date d vs last close up to the same date two years earlier
    run = lambda p, d: float(p.loc[:d].iloc[-1] / p.loc[:pd.Timestamp(d) - pd.DateOffset(years=2)].iloc[-1] - 1)
    out['run_nvda_now'] = run(pnd, pnd.index[-1])
    out['run_ndx_now'] = run(pqd, pqd.index[-1])
    out['run_csco_peak'] = run(pcd, '2000-03-31')
    out['run_ndx_2000'] = run(pqd, '2000-03-31')
    out['run_nvda_max'] = float((pn / pn.shift(24) - 1).max())
    out['run_nvda_max_date'] = d2s((pn / pn.shift(24) - 1).idxmax())
    pdd = price('csco', 'D')
    pk = pdd.loc['1999':'2001'].idxmax()
    out['csco_peak'] = d2s(pk)
    out['csco_dd'] = float(pdd.loc[pk:].min() / pdd.loc[pk] - 1)
    out['csco_trough'] = d2s(pdd.loc[pk:].idxmin())
    after = pdd.loc[pdd.loc[pk:].idxmin():]                  # after the trough: first day back at the peak level
    out['csco_recover'] = d2s(after[after >= pdd.loc[pk]].index[0]) if (after >= pdd.loc[pk]).any() else None
    nd = price('nvda', 'D')
    out['nvda_ath'] = d2s(nd.idxmax())
    out['nvda_dd_now'] = float(nd.iloc[-1] / nd.max() - 1)
    out['nvda_maxdd_2y'] = float(drawdown(nd.loc['2024-09-18':]).min())
    # LPPLS today: the confidence indicator over the last 26 weeks (NVIDIA and Nasdaq 100)
    for k in ['nvda', 'ndx']:
        p = price(k, 'D', '2022-01-01')
        t, yy = yrs(p.index), np.log(p.values)
        idx = np.arange(len(p) - 1, len(p) - 1 - 26 * 5, -10)
        ci = [lppls_confidence(t, yy, i, LPPLS_WINDOWS) for i in idx]
        out[f'ci_{k}_mean'] = float(np.mean(ci))
        out[f'ci_{k}_max'] = float(np.max(ci))
        out[f'ci_{k}_last'] = float(ci[0])
    return out



# =============================================================================
# CHARTS FOR THE TASKS AND SOLUTIONS
# =============================================================================
def fig_sem_data():
    """Seminar data: Shiller P/D ratio, Nasdaq 100 monthly, S&P 500 weekly, Bitcoin weekly."""
    sh = shiller()
    series = [(sh['PD'], 'S&P Composite real price-dividend ratio, monthly', MainBlue),
              (price('ndx', 'M'), 'Nasdaq 100, month-end close', IDAred),
              (price('sp500', 'W', '1990-01-01'), 'S&P 500, week-end close', Forest),
              (price('btc', 'W'), 'Bitcoin (USD), week-end close', Purple)]
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 4.2))
    out = {}
    for ax, (x, lab, col) in zip(axes.ravel(), series):
        x = x.dropna()
        ax.plot(x.index, x.values, color=col, lw=0.8, label=lab)
        ax.set_yscale('log')
        ax.set_title(f'{x.index[0]:%b %Y} - {x.index[-1]:%b %Y}, {len(x)} observations', fontsize=8, loc='left')
        out[lab] = dict(n=int(len(x)), start=d2s(x.index[0]), end=d2s(x.index[-1]))
    fig.tight_layout()
    fig_legend(fig, axes.ravel(), ncol=2, y=0.0)
    save_fig('ch17_sem_data')
    return out


def fig_sem_a1(D1=2.0, r=0.06, g=0.02, P=65.0):
    """A1: fundamental value F_h, expected bubble E[B_h] and the bubble share of the expected price."""
    a = a1_present_value(D1, r, g, P)
    h = np.arange(0, 101)
    F, B = a['F'] * (1 + g) ** h, a['B'] * (1 + r) ** h
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9))
    axes[0].plot(h, F, color=MainBlue, label='Fundamental value $F_h$')
    axes[0].plot(h, B, color=IDAred, label='Expected bubble $E[B_h]$')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Years ahead $h$')
    axes[0].set_ylabel('Value (log scale)')
    axes[1].plot(h, 100 * B / (F + B), color=Purple, label='Bubble share of the expected price (%)')
    for k in (5, 30, 100):
        axes[1].plot(k, 100 * a[f'share{k}'], 'o', color=Purple, ms=4)
        axes[1].annotate(f'{100 * a[f"share{k}"]:.1f}%', (k, 100 * a[f'share{k}']), textcoords='offset points',
                         xytext=(-10, 6), fontsize=7.5, color='black', ha='right' if k == 100 else 'left')
    axes[1].set_ylim(0, 100)
    axes[1].set_xlabel('Years ahead $h$')
    axes[1].set_ylabel('%')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig('ch17_sem_a1')
    return {k: a[k] for k in ('F', 'B', 'share5', 'share30', 'share100')}


def fig_sem_a2(B0=15.0, r=0.06, pi=0.9, delta=1.0, T=300, seed=SEED):
    """A2(d): Evans bubble (positive restart delta), no noise; in logs the collapses look like mean reversion."""
    rng = np.random.default_rng(seed)
    B = np.empty(T + 1)
    B[0] = B0
    for t in range(T):
        B[t + 1] = delta + (1 + r) / pi * (B[t] - delta / (1 + r)) if rng.random() < pi else delta
    y = np.log(B)
    dy, yl = np.diff(y), y[:-1]
    X = np.column_stack([np.ones_like(yl), yl])
    coef = np.linalg.lstsq(X, dy, rcond=None)[0]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9))
    axes[0].plot(np.arange(T + 1), B, color=IDAred, lw=0.8, label='Simulated bubble $B_t$ (log scale)')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Year $t$')
    axes[1].scatter(yl, dy, s=6, color=MainBlue, label=r'$(y_t, \Delta y_{t+1})$, $y = \ln B$')
    xs = np.linspace(yl.min(), yl.max(), 50)
    axes[1].plot(xs, coef[0] + coef[1] * xs, color=Orange, lw=1.2, label=f'OLS fit on all years, slope {coef[1]:.3f}')
    c = np.log(delta)
    axes[1].plot(xs, pi * np.log((1 + r) / pi) + (1 - pi) * (c - xs), color=Forest, lw=1.2, ls='--',
                 label=f'Approximation for $B \\gg \\delta$, slope $-(1-\\pi)$ = {-(1 - pi):.2f}')
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_xlabel('$y_t = \\ln B_t$')
    axes[1].set_ylabel('$\\Delta y_{t+1}$')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=3, y=0.0)
    save_fig('ch17_sem_a2')
    return dict(delta=delta, T=T, slope=float(coef[1]), theory=-(1 - pi), collapses=int((np.diff(B) < 0).sum()))


def fig_sem_a3(T=1000, R=20_000):
    """A3: simulated distribution of the t-statistic (Dickey-Fuller with a constant) and its quantiles."""
    rng = np.random.default_rng(SEED)
    tt = np.concatenate([_df_t(np.cumsum(rng.standard_normal((2000, T + 1)), axis=1)) for _ in range(R // 2000)])
    q05, q95 = np.quantile(tt, [0.05, 0.95])
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    ax.hist(tt, bins=80, density=True, color=MainBlue, alpha=0.8, label=f'Simulated $t_b$, {R:,} random walks, T = {T}')
    ax.axvline(q05, color=Forest, ls='--', lw=1.0, label=f'5% quantile {q05:.2f}')
    ax.axvline(q95, color=IDAred, ls='--', lw=1.2, label=f'95% quantile {q95:.2f} (right-tail critical value)')
    ax.axvline(1.645, color=Orange, ls='-.', lw=1.2, label='1.645, the Normal 95% quantile')
    ax.set_xlabel('$t_b$')
    ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    save_fig('ch17_sem_a3')
    return dict(q05=float(q05), q95=float(q95), share_neg=float((tt < 0).mean()))


def fig_sem_a4(Ts=(100, 400, 1600), alpha=0.8, c=1.0, R=4000):
    """A4: distribution of the t-statistic under a mildly explosive root: it shifts right as T grows."""
    rng = np.random.default_rng(SEED)
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    out = []
    for T, col in zip(Ts, [MainBlue, Orange, IDAred]):
        rho = 1 + c / T ** alpha
        e = rng.standard_normal((R, T))
        Y = np.zeros((R, T + 1))
        for t in range(T):
            Y[:, t + 1] = rho * Y[:, t] + e[:, t]
        tt = _df_t(Y)
        ax.hist(np.clip(tt, -4, 40), bins=np.linspace(-4, 40, 89), density=True, histtype='step', lw=1.3, color=col,
                label=f'T = {T}: median {np.median(tt):.1f}')
        out.append(dict(T=T, med=float(np.median(tt))))
    ax.axvline(-0.09, color=Forest, ls='--', lw=1.0, label='Unit-root 95% critical value (A3)')
    ax.set_xlabel('Right-tailed ADF t-statistic (values above 40 shown at 40)')
    ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    save_fig('ch17_sem_a4')
    return out


def _fig_filter(name, P, mu, sd, prev_turb, r):
    a = a5_markov(P, mu, sd, prev_turb, r)
    x = np.linspace(min(mu) - 4 * max(sd), max(mu) + 4 * max(sd), 400)
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
    axes[0].plot(x, stats.norm.pdf(x, mu[0], sd[0]), color=Forest, label=f'Calm density, N({mu[0]}, {sd[0]}$^2$)')
    axes[0].plot(x, stats.norm.pdf(x, mu[1], sd[1]), color=IDAred, label=f'Turbulent density, N({mu[1]}, {sd[1]}$^2$)')
    axes[0].axvline(r, color=MainBlue, ls='--', lw=1.1, label=f'Observed return {r:+.0f}%')
    axes[0].set_xlabel('Weekly return (%)')
    vals = [prev_turb, a['pred_turb'], a['post_turb']]
    bars = axes[1].bar(['Last week', 'Predicted', 'Filtered'], vals, color=[Amber, Orange, Purple],
                       label='P(turbulent regime)')
    for b_, v in zip(bars, vals):
        axes[1].text(b_.get_x() + b_.get_width() / 2, v + 0.02, f'{v:.3f}', ha='center', fontsize=8, color='black')
    axes[1].set_ylim(0, 1.05)
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig(name)
    return dict(pred=a['pred_turb'], post=a['post_turb'])


def fig_sem_a5():
    return _fig_filter('ch17_sem_a5', ((0.98, 0.02), (0.10, 0.90)), (0.3, -0.5), (2.0, 5.0), 0.2, -6.0)


def fig_sem_a6():
    return _fig_filter('ch17_sem_a6', ((0.95, 0.05), (0.20, 0.80)), (0.4, -1.0), (2.0, 6.0), 0.1, 1.0)


def _lppls_trend(t, tc, m, w, B, C1, C2, osc=True):
    tau = tc - t
    f = tau ** m
    return B * f + (C1 * f * np.cos(w * np.log(tau)) + C2 * f * np.sin(w * np.log(tau)) if osc else 0)


def fig_sem_a7(t1=2025.0, t2=2026.0, tc=2026.08, m=0.5, w=8.0, B=-1.2, C1=0.06, C2=-0.02):
    """A7: LPPLS trend implied by the parameters (A = 0): the power law and the log-periodic oscillations."""
    t = np.linspace(t1, tc - 1e-4, 2000)
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    ax.plot(t, _lppls_trend(t, tc, m, w, B, C1, C2, False), color=MainBlue, lw=1.1, label='Power law $B(t_c - t)^m$')
    ax.plot(t, _lppls_trend(t, tc, m, w, B, C1, C2, True), color=IDAred, lw=1.0, label='With log-periodic oscillations')
    ax.axvspan(t1, t2, color=Amber, alpha=0.15, lw=0, label='Estimation window $[t_1, t_2]$')
    ax.axvline(tc, color=Forest, ls='--', lw=1.0, label=f'Critical time $t_c$ = {tc}')
    ax.set_xlabel('Time (years)')
    ax.set_ylabel('$\\ln p - A$')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    save_fig('ch17_sem_a7')
    d = _lppls_diag(t1, t2, tc, m, w, B, C1, C2)
    return dict(O=d['O'], damping=d['damping'])


def fig_sem_a8():
    """A8: at which phases is the drift (hazard rate) negative? A7 vs A8 parameters, drift normalised by tau^(1-m)."""
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    out = {}
    for tag, (t1, t2, tc, m, w, B, C1, C2), col in [('A7', (2025.0, 2026.0, 2026.08, 0.5, 8.0, -1.2, 0.06, -0.02), MainBlue),
                                                   ('A8', (2025.0, 2026.0, 2026.45, 0.95, 3.5, -0.8, 0.25, 0.0), IDAred)]:
        t = np.linspace(t1, t2, 2000)
        tau = tc - t
        C, phi = np.hypot(C1, C2), np.arctan2(C2, C1)
        th = w * np.log(tau) - phi
        drift = -B * m - C * (m * np.cos(th) - w * np.sin(th))       # mu(t) / tau^(m-1)
        ax.plot(t, drift, color=col, lw=1.1, label=f'{tag} parameters: $\\mu(t)\\,\\tau^{{1-m}}$')
        out[tag] = dict(min=float(drift.min()), share_neg=float((drift < 0).mean()))
    ax.axhline(0, color=Gray, lw=0.7)
    ax.set_xlabel('Time (years), estimation window')
    ax.set_ylabel('Normalised drift')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    save_fig('ch17_sem_a8')
    return out


def fig_sem_b1(r0s=(0.03, None, 0.08)):
    """B1: BSADF on the P/D ratio for three minimum windows, with the critical values and the date-stamped episodes."""
    sh = shiller()
    y = np.log(sh['PD'])
    fig, axes = plt.subplots(3, 1, figsize=(7.4, 5.0), sharex=True)
    out = []
    for ax, r0 in zip(axes, r0s):
        res = psy(y.values, r0)
        cv = psy_cv(res['n'], res['w0'], 1000, SEED)
        L = int(np.ceil(np.log(res['n'])))
        idx = y.index[1:]
        ep = episodes(res['bsadf'], cv['bsadf95'], idx, L)
        ax.plot(idx, res['bsadf'], color=IDAred, lw=0.7, label='BSADF statistic')
        ax.plot(idx, cv['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% critical value (Monte Carlo)')
        for s0, s1, n in ep:
            up = _chg(y, s0, s1) is None or _chg(y, s0, s1) >= 0
            ax.axvspan(s0, s1 if s1 is not None else idx[-1], color=Amber if up else Teal, alpha=0.35, lw=0,
                       label='Episode, ratio rising' if up else 'Episode, ratio falling')
        ax.set_title(f'$r_0$ = {res["r0"]:.3f}, minimum window {res["w0"]} months: GSADF {res["gsadf"]:.2f}, '
                     f'95% critical value {cv["gsadf"]["95"]:.2f}', fontsize=8.5, loc='left')
        ax.set_ylim(-3, 5)
        out.append(dict(r0=res['r0'], w0=res['w0'], gsadf=res['gsadf'], cv95=cv['gsadf']['95'], n_ep=len(ep)))
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_sem_b1')
    return out


def fig_sem_b2():
    """B2: S&P 500 monthly, recursive ADF (PWY, fixed start) vs BSADF (PSY), with the critical values."""
    y = np.log(price('sp500', 'M'))
    o = run_psy(y)
    idx = o['idx']
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.0), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.3]))
    axes[0].plot(y.index, np.exp(y.values), color=MainBlue, lw=0.8, label='S&P 500 (log scale)')
    axes[0].set_yscale('log')
    for s0, s1, n in o['ep']:
        axes[0].axvspan(s0, s1 if s1 is not None else idx[-1], color=Amber, alpha=0.3, lw=0, label='BSADF episode (PSY)')
    axes[1].plot(idx, o['res']['bsadf'], color=IDAred, lw=0.8, label='BSADF (PSY)')
    axes[1].plot(idx, o['cv']['bsadf95'], color=Forest, lw=1.0, ls='--', label='95% critical value of BSADF')
    axes[1].plot(idx, o['res']['fwd'], color=Purple, lw=0.8, label='Recursive ADF, start fixed (PWY)')
    axes[1].plot(idx, o['cv']['fwd95'], color=Orange, lw=1.0, ls='-.', label='95% critical value of the recursive ADF')
    axes[1].set_ylabel('Statistic')
    axes[0].set_title('S&P 500, monthly 1990-2026: PSY and PWY date-stamping', fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig('ch17_sem_b2')
    s = summarise(o, y)
    return dict(gsadf=s['gsadf'], sadf=s['sadf'], n_ep=len(s['episodes']), n_pwy=len(s['episodes_pwy']))


def fig_sem_size(keys, labs, name):
    """B9 / B10: size of GSADF and the false-episode rate (from the lecture size study)."""
    with open(os.path.join(HERE, 'inference17.json')) as f:
        sz = json.load(f)['size']
    x = np.arange(len(keys))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9))
    for ax, (a, b, ttl) in zip(axes, [('size_mc', 'size_wild', 'Rejection rate of GSADF at 5%'),
                                      ('fp_mc', 'fp_wild', 'Paths with a false date-stamped episode')]):
        v1 = [100 * sz['rows'][k][a] for k in keys]
        v2 = [100 * sz['rows'][k][b] for k in keys]
        ax.bar(x - 0.2, v1, 0.4, color=MainBlue, label='Monte Carlo critical values')
        ax.bar(x + 0.2, v2, 0.4, color=IDAred, label='Wild bootstrap critical values')
        for xi, a1, a2 in zip(x, v1, v2):
            ax.text(xi - 0.2, a1 + 1, f'{a1:.1f}', ha='center', fontsize=7.5, color='black')
            ax.text(xi + 0.2, a2 + 1, f'{a2:.1f}', ha='center', fontsize=7.5, color='black')
        if a == 'size_mc':
            ax.axhline(5, color=Gray, ls='--', lw=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(labs, fontsize=8)
        ax.set_ylabel('%')
        ax.set_ylim(0, 100 if a == 'fp_mc' else max(v1 + v2) * 1.25)
        ax.set_title(ttl, fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend(fig, axes, ncol=2, y=0.0)
    save_fig(name)
    return {k: sz['rows'][k] for k in keys}


def charts():
    """Seminar charts for the tasks and solutions."""
    with open(os.path.join(HERE, 'sem17_results.json')) as f:
        S = json.load(f)
    out = dict(data=fig_sem_data(), A1=fig_sem_a1(), A2=fig_sem_a2(), A3=fig_sem_a3(), A4=fig_sem_a4(),
               A5=fig_sem_a5(), A6=fig_sem_a6(), A7=fig_sem_a7(), A8=fig_sem_a8(),
               B9=fig_sem_size(['iid', 'up'], ['Constant volatility', 'Volatility x3 at T/2'], 'ch17_sem_b9'),
               B10=fig_sem_size(['garch', 'down'], ['GARCH(1,1)', 'Volatility x1/3 at T/2'], 'ch17_sem_b10'))
    assert abs(out['A3']['q95'] - S['A3']['q95']) < 1e-12 and abs(out['A3']['q05'] - S['A3']['q05']) < 1e-12
    assert all(abs(a['med'] - b['med']) < 1e-12 for a, b in zip(out['A4'], S['A4']))
    assert abs(out['A5']['post'] - S['A5']['post_turb']) < 1e-12 and abs(out['A6']['post'] - S['A6']['post_turb']) < 1e-12
    out['B2'] = fig_sem_b2()
    assert abs(out['B2']['gsadf'] - S['B2']['sp500']['gsadf']) < 1e-9
    out['B1'] = fig_sem_b1()
    for a, b in zip(out['B1'], S['B1']):
        assert abs(a['gsadf'] - b['gsadf']) < 1e-9 and abs(a['cv95'] - b['cv95']) < 1e-9, (a, b)
    with open(os.path.join(HERE, 'sem17_charts.json'), 'w') as f:
        json.dump(jsonable(out), f, indent=1)
    return out

def main():
    S = {}
    S['A1'] = a1_present_value()
    S['A2'] = a2_blanchard_watson()
    S['A3'] = a3_df_limit()
    S['A4'] = a4_mild()
    S['A4w'] = a4_windows()
    S['A5'] = a5_markov()
    S['A6'] = a6_markov()
    S['A7'] = a7_lppls()
    S['A8'] = a8_lppls()
    S['B1'] = b1_pd_windows()
    S['B2'] = b2_sadf_vs_gsadf()
    S['B3'] = b3_btc_wild()
    S['B4'] = b4_bvb()
    S['B5'] = b5_tc_windows()
    S['B6'] = b6_ci_ndx()
    S['B7'] = b7_ms_sp()
    S['B8'] = b8_ms_btc()
    S['C1'] = c1_ai()
    with open(os.path.join(HERE, 'sem17_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print('saved sem17_results.json')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'charts':
        print(jsonable(charts()))
    else:
        main()

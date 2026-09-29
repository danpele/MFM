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
# PARTEA A
# =============================================================================
def a1_present_value(D1=2.0, r=0.06, g=0.02, P=65.0):
    """Gordon: F = D1 / (r - g); bula B = P - F creste cu r, fundamentalul cu g."""
    F = D1 / (r - g)
    B = P - F
    out = dict(F=F, B=B, share0=B / P)
    for h in (5, 30, 100):
        Fh, Bh = F * (1 + g) ** h, B * (1 + r) ** h
        out[f'F{h}'], out[f'B{h}'], out[f'share{h}'] = Fh, Bh, Bh / (Fh + Bh)
    return out


def a2_blanchard_watson(B0=15.0, r=0.06, pi=0.9, h=5):
    """Bula Blanchard-Watson: supravietuieste cu pi pe an; conditionat de supravietuire creste cu (1+r)/pi."""
    return dict(growth=(1 + r) / pi - 1, surv=pi ** h, life=1 / (1 - pi), EB=B0 * (1 + r) ** h,
                B_surv=B0 * ((1 + r) / pi) ** h, pi=pi, h=h,
                csd=B0 * (1 + r) * np.sqrt((1 - pi) / pi),          # abaterea standard conditionata (fara zgomot)
                log_slope=-(1 - pi))                                # panta E[Delta y | y] in logaritmi


def _df_t(Y):
    """Statistica t a lui b din Delta y_t = a + b y_{t-1} + e_t, pe fiecare rand al lui Y."""
    X, Z = Y[:, :-1], np.diff(Y, axis=1)
    n = Z.shape[1]
    sx, sxx, sz, sxz, szz = X.sum(1), (X * X).sum(1), Z.sum(1), (X * Z).sum(1), (Z * Z).sum(1)
    dd = n * sxx - sx ** 2
    bb = (n * sxz - sx * sz) / dd
    aa = (sz - bb * sx) / n
    return bb / np.sqrt((szz - aa * sz - bb * sxz) / (n - 2) * n / dd)


def a3_df_limit(T=1000, R=20_000):
    """Distributia Dickey-Fuller cu termen liber: simulare pentru T mare; media numaratorului limita = -1/2."""
    rng = np.random.default_rng(SEED)
    tt = np.concatenate([_df_t(np.cumsum(rng.standard_normal((2000, T + 1)), axis=1)) for _ in range(R // 2000)])
    # functionala limita aproximata pe grila de T puncte: numarator 1/2 (W(1)^2 - 1) - W(1) int W
    W = np.cumsum(rng.standard_normal((5000, T)), axis=1) / np.sqrt(T)
    num = 0.5 * (W[:, -1] ** 2 - 1) - W[:, -1] * W.mean(1)
    return dict(T=T, R=R, q05=float(np.quantile(tt, 0.05)), q50=float(np.quantile(tt, 0.50)),
                q95=float(np.quantile(tt, 0.95)), q99=float(np.quantile(tt, 0.99)),
                p_neg=float((tt < 0).mean()), num_mean=float(num.mean()))


def a4_mild(Ts=(100, 400, 1600), alpha=0.8, c=1.0, R=4000):
    """Radacina usor exploziva rho_T = 1 + c / T^alpha: mediana statisticii ADF creste cu T (divergenta la +inf)."""
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
    """(pastrat pentru notebook) ferestrele PSY pentru T = 440."""
    w0, r0 = min_window(T)
    n_sadf = T - w0 + 1
    return dict(T=T, r0=r0, w0=w0, n_sadf=n_sadf, n_gsadf=n_sadf * (n_sadf + 1) // 2, logT=float(np.log(T)),
                L=int(np.ceil(np.log(T))))


def _ms_step(P, mu, sd, prev_turb, r):
    """Un pas al filtrului Hamilton cu doua regimuri (0 = calm, 1 = turbulent)."""
    prev = np.array([1 - prev_turb, prev_turb])
    pred = P.T @ prev                          # P[i, j] = P(s_t = j | s_{t-1} = i)
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
    """Conditiile din Shu & Zhu (2020), ec. (11)-(12), care se pot verifica din parametri (fara date)."""
    C = np.hypot(C1, C2)
    D = t2 - t1
    O = w / np.pi * np.log((tc - t1) / (tc - t2))          # numarul de semiperioade (Shu & Zhu 2020, ec. 12)
    damp = m * abs(B) / (w * C)
    exact = m * abs(B) / (C * np.hypot(m, w))              # rata de hazard >= 0 pentru orice faza: m|B| >= |C| sqrt(m^2 + w^2)
    slope = -B * m * (tc - t2) ** (m - 1)          # d/dt [B (tc - t)^m] la t2, fara oscilatii
    return dict(C=C, D=D, O=O, damping=damp, exact=exact, dtc=tc - t2, dtc_days=(tc - t2) * 365.25, tc_lim=D / 5,
                slope=slope, m=m, w=w, B=B, ok_B=B < 0, ok_m=0.01 <= m <= 0.99, ok_w=2 <= w <= 25,
                ok_tc=0 <= tc - t2 <= D / 5, ok_O=O >= 2.5, ok_D=damp >= 1, ok_exact=exact >= 1)


def a7_lppls():
    return _lppls_diag(2025.0, 2026.0, 2026.08, 0.5, 8.0, -1.2, 0.06, -0.02)


def a8_lppls():
    return _lppls_diag(2025.0, 2026.0, 2026.45, 0.95, 3.5, -0.8, 0.25, 0.0)


# =============================================================================
# PARTEA B
# =============================================================================
def b1_pd_windows(r0s=(0.03, None, 0.08)):
    """GSADF pe raportul P/D Shiller pentru trei ferestre minime (regula PSY in mijloc)."""
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
    """Nasdaq 100 si S&P 500 lunar: datarea PWY (inceput fix) vs PSY (inceput mobil)."""
    out = {}
    for k in ['ndx', 'sp500']:
        y = np.log(price(k, 'M'))
        o = run_psy(y)
        out[k] = summarise(o, y)
    return out


def b3_btc_wild():
    """Bitcoin saptamanal: valori critice Monte Carlo (mers aleator gaussian) vs wild bootstrap."""
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
    """BET lunar 1997-2026 si BET-FI saptamanal 2012-2026: GSADF, episoade (Monte Carlo si wild bootstrap)."""
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
    """LPPLS pe Bitcoin cu t2 fix si inceputul ferestrei t1 mobil (saptamanal): distributia lui tc."""
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
    """Indicatorul de incredere LPPLS pentru Nasdaq 100, 1997-2002 (din fisierul publicat de capitol) si evaluarea."""
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
    """Markov-switching cu doua regimuri pe S&P 500 saptamanal 1990-2026."""
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
    # un regim: aceeasi medie si dispersie
    ll1 = float(stats.norm.logpdf(r, r.mean(), r.std(ddof=0)).sum())
    out['llf1'] = ll1
    out['lr'] = 2 * (out['llf'] - ll1)
    return out


def b8_ms_btc():
    """Bitcoin saptamanal: doua vs trei regimuri (AIC, BIC), media si volatilitatea fiecarui regim."""
    import statsmodels.api as sm
    p = price('btc', 'W')
    r = 100 * np.log(p).diff().dropna()
    out = {}
    for k in (2, 3):
        np.random.seed(SEED + k)                      # cautarea aleatoare a punctelor de start: reproductibila
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
# PARTEA C: EXISTA O BULA AI?
# =============================================================================
def c1_ai():
    """NVIDIA si Nasdaq 100 (lunar si saptamanal) vs Cisco in episodul dot-com: BSADF, cresteri, LPPLS azi."""
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
    # cresteri pe 2 ani (Greenwood-Shleifer-You), brut si peste Nasdaq 100
    pn = price('nvda', 'M')
    pnd, pcd, pqd = price('nvda', 'D'), price('csco', 'D'), price('ndx', 'D')
    # din preturi zilnice: ultima inchidere pana la data d vs ultima inchidere pana la aceeasi data cu doi ani inainte
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
    after = pdd.loc[pdd.loc[pk:].idxmin():]                  # dupa minim: prima zi inapoi la nivelul varfului
    out['csco_recover'] = d2s(after[after >= pdd.loc[pk]].index[0]) if (after >= pdd.loc[pk]).any() else None
    nd = price('nvda', 'D')
    out['nvda_ath'] = d2s(nd.idxmax())
    out['nvda_dd_now'] = float(nd.iloc[-1] / nd.max() - 1)
    out['nvda_maxdd_2y'] = float(drawdown(nd.loc['2024-09-18':]).min())
    # LPPLS azi: indicatorul de incredere pe ultimele 26 de saptamani (NVIDIA si Nasdaq 100)
    for k in ['nvda', 'ndx']:
        p = price(k, 'D', '2022-01-01')
        t, yy = yrs(p.index), np.log(p.values)
        idx = np.arange(len(p) - 1, len(p) - 1 - 26 * 5, -10)
        ci = [lppls_confidence(t, yy, i, LPPLS_WINDOWS) for i in idx]
        out[f'ci_{k}_mean'] = float(np.mean(ci))
        out[f'ci_{k}_max'] = float(np.max(ci))
        out[f'ci_{k}_last'] = float(ci[0])
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
    main()

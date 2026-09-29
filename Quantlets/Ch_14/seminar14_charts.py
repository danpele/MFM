"""
seminar14_charts.py -- graficele rezolvarilor din Seminarul 14 (deep learning si modele fundationale)
=====================================================================================================
Cate un grafic pentru fiecare rezolvare din Partea A (A1, A3, A5, A8, A9) si din Partea B (B1-B7, B10, B11).
Cifrele deja calculate se citesc din sem14_results.json (seminar14.py) si ch14_inference.json (inference_tests.py);
intervalele HAC, depasirile cumulate si probabilitatile binomiale se calculeaza aici, din tabelele ch14_*.csv.
Rezultat: graficele ch14_sem_* (charts/) si sem14_charts.json (cifrele noi citate pe slide-uri).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_tsfm as M   # noqa: E402
from generate_all_charts import (plt, mdates, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Brown,  # noqa: E402
                                 Magenta, Gray, LightGray, save_fig, legend_outside_bottom, fig_legend_bottom,
                                 load_csv, RISK_COL, RISK_LBL, RV_COL, RV_LBL)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}


def load_json(name):
    """A results file of Chapter 14 (sem14_results.json, ch14_inference.json)."""
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


# =============================================================================
# PARTEA A
# =============================================================================
def sem_a1():
    """A1: ||W^k||_2 against the norm bound ||W||_2^k and rho(W)^k, W = [[0.5, 0.8], [0, 0.5]]."""
    W = np.array([[0.5, 0.8], [0.0, 0.5]])
    k = np.arange(1, 61)
    exact = [np.linalg.norm(np.linalg.matrix_power(W, j), 2) for j in k]
    nrm, rho = np.linalg.norm(W, 2), max(abs(np.linalg.eigvals(W)))
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    ax.semilogy(k, nrm ** k, color=IDAred, lw=1.4, label=r'Bound $\|W\|_2^k$ (grows)')
    ax.semilogy(k, exact, color=MainBlue, lw=1.6, label=r'Exact $\|W^k\|_2$ (gradient norm)')
    ax.semilogy(k, rho ** k, color=Forest, lw=1.2, ls='--', label=r'$\rho(W)^k = 0.5^k$')
    ax.axhline(1, color=Gray, lw=0.6, ls=':')
    ax.set_xlabel('Horizon $k$ (time steps back)')
    ax.set_ylabel('Norm (log scale)')
    legend_outside_bottom(ax, ncol=3, y=-0.24)
    save_fig('ch14_sem_a1_norms')


def sem_a3():
    """A3: the four scaled values z = x/s on the token axis [-15, 15], before and after a crash of -9%."""
    x = np.array([0.8, -1.2, 0.4, 2.0])
    x6 = np.array([0.8, -1.2, 0.4, -9.0])
    z, z6 = x / np.mean(np.abs(x)), x6 / np.mean(np.abs(x6))
    fig, ax = plt.subplots(figsize=(5.6, 2.4))
    ax.scatter(z, np.ones(4), color=MainBlue, s=36, zorder=3, label='A3 context (last return +2.0%)')
    ax.scatter(z6, np.zeros(4), color=IDAred, s=36, zorder=3, label='Last return replaced by -9.0% (A4)')
    for row, (zz, xs) in enumerate(((z6, x6), (z, x))):
        for i, (v, lab) in enumerate(sorted(zip(zz, xs))):
            ax.annotate(f'{lab:+.1f}%', (v, row), textcoords='offset points', xytext=(0, 7 if i % 2 == 0 else -13),
                        ha='center', fontsize=7, color='black')
    ax.axvline(0, color=Gray, lw=0.6, ls=':')
    ax.set_xlim(-3.6, 2.4)
    ax.set_ylim(-0.6, 1.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Scaled value $z = x/s$ (the token range runs from $-15$ to $+15$, 4,093 bins)')
    legend_outside_bottom(ax, ncol=2, y=-0.32)
    save_fig('ch14_sem_a3_tokens')


def sem_a5():
    """A5: the Chronos-2 quantile grid of the last S&P 500 forecast, the linear piece on [1%, 5%] and the ES area."""
    d = load_csv('ch14_returns_sp500.csv')
    last = d.iloc[-1]
    lv = [u for u in M.C2_LEVELS if u <= 0.25]
    q = np.array([float(last[f'chronos2_q{u:.2f}']) for u in lv])
    q01, q05 = q[0], q[1]
    q025 = q01 + (0.025 - 0.01) / 0.04 * (q05 - q01)
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    ax.fill_between([0, 0.01, 0.025], [q01, q01, q025], 0, color=IDAred, alpha=0.18, lw=0,
                    label='Area whose average gives $-$ES 2.5%')
    ax.plot([0, 0.01], [q01, q01], color=IDAred, lw=1.4, ls='--', label='Held at $q_{0.01}$ below the grid')
    ax.plot(lv, q, color=MainBlue, lw=1.4, marker='o', ms=4, label='Chronos-2 grid quantiles $q_u$')
    ax.scatter([0.025], [q025], color=Orange, s=40, zorder=4, label='Interpolated $q_{0.025}$')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.annotate(f'VaR 1% = {-q01:.2f}%', (0.01, q01), textcoords='offset points', xytext=(10, 2), fontsize=7,
                color='black')
    ax.annotate(f'VaR 2.5% = {-q025:.2f}%', (0.025, q025), textcoords='offset points', xytext=(8, -4), fontsize=7,
                color='black')
    ax.set_xlabel('Probability level $u$')
    ax.set_ylabel('Return quantile (%)')
    ax.set_xlim(0, 0.26)
    legend_outside_bottom(ax, ncol=2, y=-0.24)
    save_fig('ch14_sem_a5_grid')


def kupiec_region(T, p=0.01):
    """Rejection region of the two-sided Kupiec test at 5%: numbers of breaches x with LR_uc > 3.84."""
    crit = stats.chi2.ppf(0.95, 1)
    return [x for x in range(0, min(T, int(0.06 * T) + 15) + 1) if M.kupiec(np.r_[np.ones(x), np.zeros(T - x)], p)['LR'] > crit]


def kupiec_power(T, pi, p=0.01):
    rej = kupiec_region(T, p)
    return float(sum(stats.binom.pmf(x, T, pi) for x in rej))


def sem_a8():
    """A8: Bin(220, 1%) and Bin(220, 1.67%) with the Kupiec rejection region at T = 220."""
    T = 220
    rej = set(kupiec_region(T))
    x = np.arange(0, 13)
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    w = 0.38
    ax.bar(x - w / 2, stats.binom.pmf(x, T, 0.01), width=w, color=MainBlue, label='True rate 1% (model correct)')
    ax.bar(x + w / 2, stats.binom.pmf(x, T, 0.0167), width=w, color=Orange, label='True rate 1.67% (raw Chronos-2)')
    for xx in x:
        if xx in rej:
            ax.axvspan(xx - 0.5, xx + 0.5, color=IDAred, alpha=0.12, lw=0)
    ax.axvspan(-10, -9, color=IDAred, alpha=0.12, lw=0, label='Kupiec rejects at 5%')
    ax.set_xlim(-0.6, 12.6)
    ax.set_xticks(x)
    ax.set_xlabel('Number of VaR 1% breaches in $T = 220$ days')
    ax.set_ylabel('Probability')
    legend_outside_bottom(ax, ncol=3, y=-0.24)
    save_fig('ch14_sem_a8_binom')


def sem_a9():
    """A9: exact Kupiec power against the window length T, true breach rate 1.67% and 2%."""
    Ts = np.arange(100, 3001, 10)
    p167 = [kupiec_power(T, 0.0167) for T in Ts]
    p2 = [kupiec_power(T, 0.02) for T in Ts]
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    ax.plot(Ts, p167, color=IDAred, lw=1.2, label='True breach rate 1.67%')
    ax.plot(Ts, p2, color=MainBlue, lw=1.2, label='True breach rate 2%')
    ax.axhline(0.8, color=Gray, lw=0.6, ls='--')
    ax.axvline(220, color=Gray, lw=0.6, ls=':')
    ax.text(235, 0.05, 'post-release\nwindow, 220 days', fontsize=7, color='black')
    ax.set_xlabel('Backtest length $T$ (days)')
    ax.set_ylabel('Power of Kupiec test (5%)')
    ax.set_ylim(0, 1)
    legend_outside_bottom(ax, ncol=2, y=-0.24)
    save_fig('ch14_sem_a9_power')


# =============================================================================
# PARTEA B
# =============================================================================
RET_ORDER = ['Historical mean', 'AR(1)', 'LSTM', 'Chronos-2', 'Chronos-Bolt', 'TimesFM-2.5']


def _r2_panel(ax, tab, title=None):
    """R^2 (%) with the 95% block-bootstrap interval; red: DM rejects at 5%."""
    for i, m in enumerate(RET_ORDER):
        x = tab[m]
        c = IDAred if x['p (DM)'] < 0.05 else MainBlue
        ax.plot([x['CI low'], x['CI high']], [i, i], color=c, lw=2.2, solid_capstyle='butt')
        ax.scatter(x['R2 (%)'], i, color=c, s=26, zorder=3)
    ax.axvline(0, color=Gray, lw=0.7, ls='--')
    ax.set_yticks(range(len(RET_ORDER)), RET_ORDER, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(r'Out-of-sample $R^2$ against zero (%)')
    if title:
        ax.set_title(title, fontsize=9, color='black')


def _r2_legend(fig_or_ax, fig=False, y=-0.26):
    from matplotlib.lines import Line2D
    h = [Line2D([0], [0], color=MainBlue, lw=2.2, marker='o'), Line2D([0], [0], color=IDAred, lw=2.2, marker='o')]
    lab = ['95% block-bootstrap interval, DM not significant', 'DM rejects equal accuracy at 5%']
    if fig:
        fig_legend_bottom(fig_or_ax, h, lab, ncol=2, y=0.0)
    else:
        fig_or_ax.legend(h, lab, loc='upper center', bbox_to_anchor=(0.5, y), ncol=2, frameon=False)


def sem_b1():
    S = load_json('sem14_results.json')
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    _r2_panel(ax, S['B1'])
    _r2_legend(ax, y=-0.26)
    save_fig('ch14_sem_b1_r2')


def sem_b2():
    S = load_json('sem14_results.json')
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True)
    _r2_panel(axs[0], S['B2']['btc'], 'Bitcoin (from 2019)')
    _r2_panel(axs[1], S['B2']['bet'], 'BET (from 2016)')
    fig.tight_layout()
    _r2_legend(fig, fig=True)
    save_fig('ch14_sem_b2_r2')


def _dm_ci(la, lb):
    """Mean loss difference with the 95% HAC interval (Newey-West, as in the DM test)."""
    dm = M.diebold_mariano(la, lb)
    se = abs(dm['dbar'] / dm['DM'])
    return dm['dbar'], dm['dbar'] - 1.96 * se, dm['dbar'] + 1.96 * se, dm['p']


def sem_b3():
    d = load_csv('ch14_rv.csv')
    models = ['RW', 'HAR', 'GARCH-t', 'LSTM', 'Chronos-2', 'Chronos-Bolt', 'TimesFM-2.5']
    res = {}
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    for j, (tag, dd, col) in enumerate((('full', d, MainBlue), ('post', d[d.index >= M.POST_FROM], Orange))):
        L0 = M.qlike(dd['RV'], dd['logHAR'])
        for i, m in enumerate(models):
            est, lo, hi, p = _dm_ci(M.qlike(dd['RV'], dd[m]), L0)
            res[f'{tag}|{m}'] = dict(d=est, lo=lo, hi=hi, p=p)
            y = i + (j - 0.5) * 0.3
            ax.plot([lo, hi], [y, y], color=col, lw=2.0, solid_capstyle='butt')
            ax.scatter(est, y, color=col, s=18, zorder=3)
    ax.axvline(0, color=Gray, lw=0.7, ls='--')
    ax.set_yticks(range(len(models)), [RV_LBL[m] for m in models], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Mean QLIKE minus log-HAR QLIKE (negative: better than log-HAR)')
    from matplotlib.lines import Line2D
    ax.legend([Line2D([0], [0], color=MainBlue, lw=2, marker='o'), Line2D([0], [0], color=Orange, lw=2, marker='o')],
              [f'Full test period ({len(d)} days), 95% HAC interval',
               f'After 3 Nov 2025 ({int((d.index >= M.POST_FROM).sum())} days)'],
              loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=2, frameon=False)
    save_fig('ch14_sem_b3_qlike')
    OUT['B3'] = res


def sem_b4():
    S = load_json('sem14_results.json')
    ctx = {int(k): v for k, v in S['B4']['ctx'].items()}
    lhar = S['B3']['logHAR']['QLIKE']
    med = S['B4']['median']
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6), gridspec_kw=dict(width_ratios=[1.3, 1]))
    ax = axs[0]
    ks = sorted(ctx)
    ax.plot(ks, [ctx[k] for k in ks], color=IDAred, marker='o', ms=4, lw=1.3, label='Chronos-2, grid mean')
    ax.axhline(lhar, color=Purple, lw=1.1, ls='--', label='log-HAR')
    ax.set_xscale('log', base=2)
    ax.set_xticks(ks, [str(k) for k in ks])
    ax.set_xlabel('Context length (days)')
    ax.set_ylabel('Mean QLIKE')
    ax = axs[1]
    labs = ['Chronos-2', 'TimesFM-2.5']
    x = np.arange(2)
    ax.bar(x - 0.19, [med[f'{m}, grid mean']['QLIKE'] for m in labs], width=0.38, color=MainBlue,
           label=r'Grid mean $\int_0^1 \exp(q_u)\,du$')
    ax.bar(x + 0.19, [med[f'{m}, exp(median)']['QLIKE'] for m in labs], width=0.38, color=Orange,
           label=r'$\exp(q_{0.5})$, the median')
    ax.axhline(lhar, color=Purple, lw=1.1, ls='--')
    ax.set_xticks(x, labs)
    ax.set_ylim(0.2, 0.27)
    ax.set_ylabel('Mean QLIKE')
    fig.tight_layout()
    h1, l1 = axs[0].get_legend_handles_labels()
    h2, l2 = axs[1].get_legend_handles_labels()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=4, y=0.0)
    save_fig('ch14_sem_b4_context')


def sem_b5():
    d = load_csv('ch14_risk_sp500.csv')
    L = -d['y']
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    for m in ('HS', 'GARCH-t', 'FHS', 'C2-raw', 'C2-FHS', 'TFM-FHS'):
        h = (L > d[f'{m}|VaR1']).astype(int).cumsum()
        ax.step(d.index, h, where='post', color=RISK_COL[m], lw=1.1, label=RISK_LBL[m])
    ax.plot(d.index, 0.01 * np.arange(1, len(d) + 1), color='black', lw=1.0, ls='--', label='Expected, 1% of days')
    ax.set_ylabel('Cumulative VaR 1% breaches')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    legend_outside_bottom(ax, ncol=4, y=-0.14)
    save_fig('ch14_sem_b5_breaches')


def sem_b6():
    S = load_json('sem14_results.json')
    R = load_json('ch14_results.json')
    models = ['HS', 'FHS', 'Chronos-2', 'Chronos-Bolt', 'TimesFM-2.5']
    cols = [RISK_COL['HS'], RISK_COL['FHS'], RISK_COL['C2-raw'], RISK_COL['bolt-raw'], RISK_COL['timesfm-raw']]
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    w = 0.16
    for j, a in enumerate(M.ASSETS):
        T = R['risk'][a]['n']
        lo, hi = stats.binom.ppf(0.025, T, 0.1) / T * 100, stats.binom.ppf(0.975, T, 0.1) / T * 100
        ax.fill_between([j - 0.45, j + 0.45], lo, hi, color=LightGray, alpha=0.6, lw=0,
                        label='95% range if the model is correct' if j == 0 else None)
        for i, m in enumerate(models):
            ax.bar(j + (i - 2) * w, S['B6_v10'][a][m]['rate (%)'], width=w, color=cols[i], label=m if j == 0 else None)
    ax.axhline(10, color=Gray, lw=0.7, ls='--')
    ax.set_xticks(range(3), [M.LABELS[a] for a in M.ASSETS])
    ax.set_ylim(6, 15)
    ax.set_ylabel('VaR 10% breach rate (%)')
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch14_sem_b6_var10')


def sem_b7():
    S = load_json('sem14_results.json')
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    for i, a in enumerate(('S&P 500', 'Bitcoin', 'BET')):
        x = S['B7'][a]
        v = [x[f'seed {s}'] for s in range(5)]
        ax.scatter(v, [i] * 5, color=MainBlue, s=28, zorder=3, label='Single seed (0-4)' if i == 0 else None)
        ax.scatter(x['average of 5 seeds'], i, color=IDAred, marker='D', s=40, zorder=4,
                   label='Average of the five forecasts' if i == 0 else None)
        ax.plot([min(v), max(v)], [i, i], color=MainBlue, lw=0.8, alpha=0.5)
    ax.axvline(0, color=Gray, lw=0.7, ls='--')
    ax.set_yticks(range(3), ['S&P 500', 'Bitcoin', 'BET'])
    ax.invert_yaxis()
    ax.set_xlabel(r'Out-of-sample $R^2$ against zero (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.26)
    save_fig('ch14_sem_b7_seeds')


def sem_b10():
    C = load_json('ch14_inference.json')['conf']
    meth = [('FHS', 'FHS', RISK_COL['FHS']), ('C2-raw', 'Chronos-2 raw', RISK_COL['C2-raw']),
            ('C2-SCP', 'Split conformal', Purple), ('C2-ACI', 'Adaptive conformal (ACI)', MainBlue)]
    fig, ax = plt.subplots(figsize=(6.0, 2.7))
    w = 0.2
    for j, a in enumerate(M.ASSETS):
        for i, (k, lab, col) in enumerate(meth):
            ax.bar(j + (i - 1.5) * w, C[a][k]['x'], width=w, color=col, label=lab if j == 0 else None)
        e = 0.01 * C[a]['n']
        ax.plot([j - 0.45, j + 0.45], [e, e], color='black', lw=1.1, ls='--',
                label='Expected, 1% of days' if j == 0 else None)
    ax.set_xticks(range(3), [M.LABELS[a] for a in M.ASSETS])
    ax.set_ylabel('VaR 1% breaches')
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch14_sem_b10_conformal')


def sem_b11():
    """B11: QLIKE differential Chronos-2 minus log-HAR, 60-day rolling mean, pre/post means with HAC intervals."""
    d = load_csv('ch14_rv.csv')
    dd = pd.Series(M.qlike(d['RV'], d['Chronos-2']) - M.qlike(d['RV'], d['logHAR']), index=d.index)
    post = dd.index >= M.POST_FROM
    res = {}
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    ax.plot(dd.index, dd.rolling(60).mean(), color=MainBlue, lw=1.1, label='60-day rolling mean of $d_t$')
    for tag, m, col in (('pre', ~post, Forest), ('post', post, Orange)):
        x = dd[m].values
        se = np.sqrt(M.nw_var(x) / len(x))
        mu = x.mean()
        res[tag] = dict(mean=float(mu), lo=float(mu - 1.96 * se), hi=float(mu + 1.96 * se), n=int(len(x)))
        idx = dd.index[m]
        ax.fill_between(idx, mu - 1.96 * se, mu + 1.96 * se, color=col, alpha=0.2, lw=0)
        ax.plot(idx, np.full(len(idx), mu), color=col, lw=1.6,
                label=('Mean before 3 Nov 2025' if tag == 'pre' else 'Mean after 3 Nov 2025') + ', 95% HAC band')
    ax.axhline(0, color=Gray, lw=0.6, ls='--')
    ax.axvline(pd.Timestamp(M.POST_FROM), color=Gray, lw=0.6, ls=':')
    ax.set_ylabel('QLIKE Chronos-2 minus log-HAR')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch14_sem_b11_prepost')
    OUT['B11'] = res


if __name__ == '__main__':
    for f in (sem_a1, sem_a3, sem_a5, sem_a8, sem_a9, sem_b1, sem_b2, sem_b3, sem_b4, sem_b5, sem_b6, sem_b7,
              sem_b10, sem_b11):
        f()
    with open(os.path.join(HERE, 'sem14_charts.json'), 'w') as fh:
        json.dump(OUT, fh, indent=1)
    print('wrote sem14_charts.json')

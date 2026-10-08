"""
seminar20_explainers.py -- Explanatory (primer) charts for Seminar 20 (MFM): signatures and realised volatility
================================================================================================================
Teaching charts for the primer slides "Prerequisites for Today" / "Noțiuni necesare azi" of Seminar 20,
which takes place BEFORE Lecture 20. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (the Lévy area of a path, signature kernel weights and the effective sample size, realised variance
and semivariances, the HAR averages and their implied lag weights, the QLIKE loss under a noisy proxy, the
Diebold--Mariano test with naive and Newey--West variances, Holm and BH thresholds) and contain no exercise answers.

Output: charts/ch20_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_20/seminar20_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon
from scipy import stats

# course palette (no grey)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'
BandBlue = '#C5D2E8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

# drawn at the size of their box on the slide (full width: 5.6 x 1.9 in; one column: 2.75 x 2.3 in),
# so that 1 pt in the figure is about 1 pt on the slide: texts 7-7.5 pt, never below 6.5 pt
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'lines.markersize': 3.5, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.size': 2.5,
                     'ytick.major.size': 2.5, 'axes.titlepad': 3, 'axes.labelpad': 2,
                     'axes.facecolor': 'none', 'figure.facecolor': 'none', 'savefig.facecolor': 'none',
                     'text.color': 'black', 'axes.labelcolor': 'black', 'xtick.color': 'black',
                     'ytick.color': 'black', 'axes.edgecolor': Navy})

FULL = (5.6, 1.55)    # full slide width
HALF = (2.75, 1.85)   # half slide width (two-column layout)


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=300)
    plt.close(fig)
    print(f'   saved {name}')


def bottom_legend(fig, axes=None, ncol=3, handles=None, labels=None):
    """Legend outside the plot, centred below the figure (after tight_layout)."""
    if handles is None:
        handles, labels = [], []
        for ax in np.atleast_1d(axes).ravel():
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels and not l.startswith('_'):
                    handles.append(h); labels.append(l)
    fig.tight_layout()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False,
               handlelength=1.6, columnspacing=1.2, handletextpad=0.5, borderaxespad=0.2)


def levy_area(x, y):
    """Lévy area A^{12} of the piecewise-linear path through the points (x_k, y_k): (S^{12} - S^{21})/2."""
    dx, dy = np.diff(x), np.diff(y)
    x0, y0 = x[:-1] - x[0], y[:-1] - y[0]
    s12 = np.sum(x0 * dy + 0.5 * dx * dy)
    s21 = np.sum(y0 * dx + 0.5 * dx * dy)
    return 0.5 * (s12 - s21)


# =============================================================================
# (i) the Lévy area: early against late rise, and a price--volatility loop
# =============================================================================
def fig_levy(L=22, seed=3):
    t = np.arange(L + 1, dtype=float)
    early = 1 - (1 - t / L) ** 3
    late = (t / L) ** 3
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    out = {}
    for y, col, lab in ((early, IDAred, 'early rise'), (late, MainBlue, 'late rise')):
        a = levy_area(t, y)
        out[lab] = float(a)
        ax.add_patch(Polygon(np.c_[t, y], closed=True, color=col, alpha=0.25, lw=0))
        ax.plot(t, y, color=col, lw=1.4, label=f'{lab}: $A^{{12}}$ = {a:+.2f}')
    ax.plot([0, L], [0, 1], color=Navy, lw=0.9, ls='--', label='chord')
    ax.set_xlabel('Channel 1: time $t$ (days)')
    ax.set_ylabel('Channel 2: $y_t$')
    ax.set_title('Same start and end, different order', loc='left')
    # right: a simulated price--volatility episode (price falls, then volatility rises and slowly decays)
    rng = np.random.default_rng(seed)
    k = np.arange(L + 1)
    cumr = np.r_[0, np.cumsum(np.where(k[1:] <= 8, -0.9, 0.15) + 0.25 * rng.standard_normal(L))]
    lrv = np.r_[0, np.cumsum(np.where((k[1:] > 4) & (k[1:] <= 12), 0.25, -0.08) + 0.08 * rng.standard_normal(L))]
    a = levy_area(cumr, lrv)
    out['loop'] = float(a)
    ax = axes[1]
    ax.add_patch(Polygon(np.c_[cumr, lrv], closed=True, color=Amber, alpha=0.3, lw=0))
    ax.plot(cumr, lrv, '-o', color=Amber, lw=1.2, ms=2.2, label=f'22-day window: $A^{{12}}$ = {a:+.2f}')
    ax.plot([cumr[0], cumr[-1]], [lrv[0], lrv[-1]], color=Navy, lw=0.9, ls='--')
    ax.plot(cumr[0], lrv[0], 'o', color=Forest, ms=4.5, label='start')
    ax.plot(cumr[-1], lrv[-1], 's', color=IDAred, ms=4.5, label='end')
    ax.set_xlabel('Channel 1: cumulative return (%)')
    ax.set_ylabel(r'Ch. 2: change in $\ln\mathrm{RV}$')
    ax.set_title('Price falls first, volatility rises after', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch20_sem_primer_levy')
    return out


# =============================================================================
# (ii) kernel weights and the Kish effective sample size
# =============================================================================
def fig_kernel(n=1000, seed=7):
    rng = np.random.default_rng(seed)
    delta = rng.chisquare(6, n)                    # simulated squared signature distances
    med = np.median(delta)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    u = np.linspace(0, 4, 300)
    for c, col in ((0.5, Forest), (1.0, MainBlue), (3.0, IDAred)):
        ax.plot(u, np.exp(-c * u), color=col, lw=1.4, label=f'$c$ = {c:g}')
    ax.axvline(1, color=Navy, lw=0.7, ls=':')
    ax.text(1.05, 0.9, 'median distance', fontsize=7, color=Navy)
    ax.set_xlabel(r'Distance $\delta_\tau$ / median($\delta$)')
    ax.set_ylabel(r'Relative weight $e^{-\gamma\delta_\tau}$')
    ax.set_title('Similar windows weigh more', loc='left')
    ax = axes[1]
    cs = np.linspace(0, 5, 101)
    ne = []
    for c in cs:
        w = np.exp(-c * delta / med); w /= w.sum()
        ne.append(1 / np.sum(w ** 2))
    ax.plot(cs, ne, color=Navy, lw=1.4, label=r'$n_{\mathrm{eff}} = 1/\sum_\tau w_\tau^2$')
    for c, col in ((0.5, Forest), (1.0, MainBlue), (3.0, IDAred)):
        v = np.interp(c, cs, ne)
        ax.plot(c, v, 'o', color=col, ms=4)
        ax.annotate(f'{v:.0f}', (c, v), xytext=(4, 3), textcoords='offset points', fontsize=7, color=col)
    ax.set_ylim(0, n * 1.08)
    ax.set_xlabel('Constant $c$ (temperature $\\gamma = c$/median)')
    ax.set_ylabel('Effective sample size')
    ax.set_title(f'{n:,} training days', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch20_sem_primer_kernel')
    return dict(neff={c: float(np.interp(c, cs, ne)) for c in (0.5, 1.0, 3.0)})


# =============================================================================
# (iii) realised variance and semivariances of one simulated day (78 five-minute returns)
# =============================================================================
def fig_realized(seed=11, m=78, sd_day=1.2):
    rng = np.random.default_rng(seed)
    s = sd_day / np.sqrt(m) * (1 + 0.8 * np.exp(-np.arange(m) / 8) + 0.5 * np.exp(-(m - 1 - np.arange(m)) / 6))
    r = s * rng.standard_t(5, m) * np.sqrt(3 / 5)
    r[40] = -1.1                                  # one large negative jump
    rv = np.sum(r ** 2); rp = np.sum(r[r > 0] ** 2); rn = np.sum(r[r < 0] ** 2)
    rq = m / 3 * np.sum(r ** 4)
    fig, ax = plt.subplots(figsize=(2.75, 1.85))
    k = np.arange(1, m + 1)
    ax.bar(k[r > 0], r[r > 0], color=Forest, width=0.8, label=f'$r_{{t,i}} > 0$: RV$^+$ = {rp:.2f}')
    ax.bar(k[r < 0], r[r < 0], color=IDAred, width=0.8, label=f'$r_{{t,i}} < 0$: RV$^-$ = {rn:.2f}')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlim(0, m + 1)
    ax.set_xlabel('Five-minute interval $i$')
    ax.set_ylabel('Return $r_{t,i}$ (%)')
    ax.set_title(f'RV = {rv:.2f} (%$^2$), RQ = {rq:.2f}', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch20_sem_primer_realized')
    return dict(rv=float(rv), rp=float(rp), rn=float(rn), rq=float(rq))


# =============================================================================
# (iv) the HAR averages on a simulated RV series and the implied lag weights
# =============================================================================
def fig_har(T=400, seed=2, bd=0.4, bw=0.35, bm=0.15):
    rng = np.random.default_rng(seed)
    # simulate log RV from a log-HAR with these coefficients
    burn = 300
    x = np.zeros(T + burn)
    for t in range(22, T + burn):
        x[t] = (0.1 * np.log(1.0) + bd * x[t - 1] + bw * x[t - 5:t].mean() + bm * x[t - 22:t].mean()
                + 0.35 * rng.standard_normal())
    rv = np.exp(x[burn:] - 0.5)
    w = np.convolve(rv, np.ones(5) / 5)[:T]
    mth = np.convolve(rv, np.ones(22) / 22)[:T]
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axes[0]
    tt = np.arange(T)
    ax.plot(tt, rv, color=BandBlue, lw=0.8, label=r'daily $\mathrm{RV}_t$')
    ax.plot(tt[5:], w[5:], color=MainBlue, lw=1.0, label=r'weekly $\mathrm{RV}^{(w)}_t$ (5 days)')
    ax.plot(tt[22:], mth[22:], color=IDAred, lw=1.3, label=r'monthly $\mathrm{RV}^{(m)}_t$ (22 days)')
    ax.set_xlim(22, T)
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Realised variance')
    ax.set_title('Simulated RV and its HAR averages', loc='left')
    ax = axes[1]
    j = np.arange(1, 23)
    phi = bm / 22 + np.where(j <= 5, bw / 5, 0) + np.where(j == 1, bd, 0)
    ax.bar(j, phi, color=Amber, width=0.75)
    ax.text(2.2, phi[0] * 0.92, rf'$\beta_d + \beta_w/5 + \beta_m/22$', fontsize=7, color=Navy)
    ax.text(6.5, phi[2] * 1.15, r'$\beta_w/5 + \beta_m/22$', fontsize=7, color=Navy)
    ax.text(10, phi[10] * 2.2, r'$\beta_m/22$', fontsize=7, color=Navy)
    ax.set_xlabel('Lag $j$ (days)')
    ax.set_ylabel(r'Weight of $\mathrm{RV}_{t+1-j}$')
    ax.set_title(f'Implied AR(22) weights', loc='left')
    bottom_legend(fig, axes[0], ncol=3)
    save_fig(fig, 'ch20_sem_primer_har')
    return dict(phi1=float(phi[0]), phi2=float(phi[1]), phi6=float(phi[5]), sum=float(phi.sum()))


# =============================================================================
# (v) QLIKE: the loss for one day and the expected loss under a noisy proxy
# =============================================================================
def fig_qlike(nu=8, n=400_000, seed=4):
    F = np.linspace(0.3, 2.5, 400)
    ql = lambda rv, f: rv / f - np.log(rv / f) - 1
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(F, ql(1.0, F), color=IDAred, lw=1.5, label='QLIKE')
    ax.plot(F, (1 - F) ** 2, color=MainBlue, lw=1.3, ls='--', label='squared error $(\\mathrm{RV} - F)^2$')
    ax.plot(F, (np.log(F)) ** 2, color=Forest, lw=1.2, ls=':', label='log error $(\\ln\\mathrm{RV} - \\ln F)^2$')
    ax.axvline(1, color=Navy, lw=0.6)
    ax.set_ylim(0, 1.2)
    ax.set_xlabel('Forecast $F$ (true RV = 1)')
    ax.set_ylabel('Loss')
    ax.set_title('One day: under-forecasting costs more', loc='left')
    rng = np.random.default_rng(seed)
    proxy = rng.chisquare(nu, n) / nu                # unbiased noisy proxy: E[RV] = 1
    ax = axes[1]
    eql = np.array([np.mean(ql(proxy, f)) for f in F])
    elog = np.array([np.mean((np.log(proxy) - np.log(f)) ** 2) for f in F])
    emse = np.array([np.mean((proxy - f) ** 2) for f in F])
    for e, col, ls in ((eql, IDAred, '-'), (emse, MainBlue, '--'), (elog, Forest, ':')):
        ax.plot(F, e - e.min(), color=col, lw=1.4 if ls == '-' else 1.2, ls=ls)
        ax.plot(F[np.argmin(e)], 0, 'o', color=col, ms=4)
    ax.axvline(1, color=Navy, lw=0.6)
    ax.set_ylim(-0.02, 0.6)
    ax.set_xlabel('Forecast $F$ (true $E[\\mathrm{RV}]$ = 1)')
    ax.set_ylabel('Excess expected loss')
    ax.set_title(f'Noisy proxy: minimisers', loc='left')
    bottom_legend(fig, axes[0], ncol=3)
    save_fig(fig, 'ch20_sem_primer_qlike')
    return dict(argmin_ql=float(F[np.argmin(eql)]), argmin_mse=float(F[np.argmin(emse)]),
                argmin_log=float(F[np.argmin(elog)]), q05=float(ql(1, 0.5)), q15=float(ql(1, 1.5)))


# =============================================================================
# (vi) the Diebold--Mariano test with autocorrelated loss differences: naive against Newey--West variance
# =============================================================================
def nw_var(d, L):
    d = d - d.mean()
    T = len(d)
    g = [np.dot(d[l:], d[:T - l]) / T for l in range(L + 1)]
    return g[0] + 2 * sum((1 - l / (L + 1)) * g[l] for l in range(1, L + 1))


def fig_dm(T=500, R=4000, h=5, seed=9):
    rng = np.random.default_rng(seed)
    naive, nw = [], []
    for _ in range(R):
        e = rng.standard_normal(T + h - 1)
        d = np.convolve(e, np.ones(h) / np.sqrt(h), mode='valid')     # MA(h-1): overlapping h-day targets
        naive.append(d.mean() / np.sqrt(d.var(ddof=1) / T))
        nw.append(d.mean() / np.sqrt(nw_var(d, h) / T))
    naive, nw = np.array(naive), np.array(nw)
    rej_n = float(np.mean(np.abs(naive) > 1.96)); rej_w = float(np.mean(np.abs(nw) > 1.96))
    # one path of cumulative loss differences
    e = rng.standard_normal(T + h - 1)
    d0 = np.convolve(e, np.ones(h) / np.sqrt(h), mode='valid')
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(np.cumsum(d0), color=MainBlue, lw=1.1, label='equal accuracy, $E[d_t] = 0$')
    ax.plot(np.cumsum(d0 - 0.15), color=IDAred, lw=1.1, label='model 1 better, $E[d_t] = -0.15$')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Forecast day $t$')
    ax.set_ylabel(r'Cumulative $\sum_{s \leq t} d_s$')
    ax.set_title('Loss differences, overlapping 5-day targets', loc='left')
    ax = axes[1]
    bins = np.linspace(-6, 6, 61)
    ax.hist(naive, bins=bins, density=True, color=Amber, alpha=0.55, label=f'naive variance: rejects {100 * rej_n:.0f}%')
    ax.hist(nw, bins=bins, density=True, color=Forest, alpha=0.55, label=f'Newey–West ({h} lags): rejects {100 * rej_w:.0f}%')
    g = np.linspace(-6, 6, 300)
    ax.plot(g, stats.norm.pdf(g), color=Navy, lw=1.1, ls='--', label='$N(0, 1)$')
    for v in (-1.96, 1.96):
        ax.axvline(v, color=IDAred, lw=0.8, ls=':')
    ax.set_xlabel('DM statistic under $H_0$')
    ax.set_ylabel('Density')
    ax.set_title(f'{R:,} simulated tests at 5% (two-sided)', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch20_sem_primer_dm')
    return dict(rej_naive=rej_n, rej_nw=rej_w)


# =============================================================================
# (vii) Holm and BH on 50 simulated p-values
# =============================================================================
def fig_holm_bh(m=50, seed=6):
    rng = np.random.default_rng(seed)
    z = np.r_[rng.normal(3.2, 1, 5), rng.normal(0, 1, m - 5)]
    p = np.sort(stats.norm.sf(z))
    k = np.arange(1, m + 1)
    holm = 0.05 / (m - k + 1)
    bh = 0.05 * k / m
    n_holm = int(np.argmax(p > holm)) if (p > holm).any() else m
    ok = np.where(p <= bh)[0]
    n_bh = int(ok.max() + 1) if len(ok) else 0
    fig, ax = plt.subplots(figsize=(2.75, 1.95))
    ax.plot(k, p, 'o', color=Navy, ms=2.6, label='sorted $p_{(k)}$')
    ax.plot(k, holm, color=IDAred, lw=1.1, ls='--', label='Holm')
    ax.plot(k, bh, color=Forest, lw=1.1, label='BH')
    ax.axhline(0.05, color=Amber, lw=0.9, ls='-.', label='0.05')
    ax.set_yscale('log'); ax.set_ylim(max(p.min() / 3, 1e-9), 1.5)
    ax.set_xlabel('Rank $k$')
    ax.set_ylabel('$p$-value (log)')
    ax.set_title(f'$m$ = {m}: raw {int((p <= 0.05).sum())}, Holm {n_holm}, BH {n_bh}', loc='left')
    bottom_legend(fig, ax, ncol=4)
    save_fig(fig, 'ch20_sem_primer_holm_bh')
    return dict(raw=int((p <= 0.05).sum()), holm=n_holm, bh=n_bh, p5=p[:8].round(5).tolist())


def run_all():
    res = {}
    res['levy'] = fig_levy()
    res['kernel'] = fig_kernel()
    res['realized'] = fig_realized()
    res['har'] = fig_har()
    res['qlike'] = fig_qlike()
    res['dm'] = fig_dm()
    res['holm_bh'] = fig_holm_bh()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

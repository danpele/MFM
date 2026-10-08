"""
seminar7_explainers.py -- Explanatory (primer) charts for Seminar 7 (MFM): Value-at-Risk and Expected Shortfall
==============================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 7, which takes
place BEFORE Lecture 7. All charts use SIMULATED or textbook-distribution data only (fixed seeds): they illustrate
the concepts (VaR and ES on a loss density, Normal against Student-t, a loss with an atom, ES as a minimum,
historical simulation, i.i.d. against block bootstrap, filtered VaR, longer horizons, the GPD tail, clustered
exceedances, Euler risk contributions, the Cornish--Fisher transform, the pinball loss and CAViaR) and contain
no exercise answers.

Output: charts/ch7_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom), drawn at the
size of their box on the slide (1 pt in the figure = 1 pt on the slide, text >= 7 pt).

Run:  python3 Quantlets/Ch_07/seminar7_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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

plt.rcParams.update({'font.size': 7.6, 'axes.labelsize': 7.6, 'axes.titlesize': 7.6, 'xtick.labelsize': 7.2,
                     'ytick.labelsize': 7.2, 'legend.fontsize': 7.2, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
                     'legend.handlelength': 1.6, 'legend.columnspacing': 1.2, 'axes.titlepad': 3})

FULL = (5.55, 1.32)    # full slide width, chart above a few bullets
HALF = (2.78, 1.85)    # half slide width (two-column layout)


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', pad_inches=0.02, transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', pad_inches=0.02, transparent=True,
                dpi=220)
    plt.close(fig)
    print(f'   saved {name}')


def bottom_legend(fig, axes=None, ncol=3, handles=None, labels=None):
    if handles is None:
        handles, labels = [], []
        for ax in np.atleast_1d(axes).ravel():
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels and not l.startswith('_'):
                    handles.append(h); labels.append(l)
    fig.tight_layout(pad=0.3, w_pad=1.0)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


def unit_t(nu):
    """Student-t with nu degrees of freedom, rescaled to unit variance (nu > 2)."""
    return stats.t(nu, scale=np.sqrt((nu - 2) / nu))


def es_t(alpha, nu):
    """ES of the unit-variance Student-t loss at tail probability alpha."""
    t = stats.t.ppf(alpha, nu)
    s = np.sqrt((nu - 2) / nu)
    return s * stats.t.pdf(t, nu) / alpha * (nu + t ** 2) / (nu - 1)


def sim_garch_t(T, omega=0.02, a=0.08, b=0.90, nu=5, seed=0, burn=500):
    rng = np.random.default_rng(seed)
    z = unit_t(nu).rvs(T + burn, random_state=rng)
    r = np.empty(T + burn); s2 = np.empty(T + burn)
    s2[0] = omega / (1 - a - b)
    for t in range(T + burn):
        if t > 0:
            s2[t] = omega + a * r[t - 1] ** 2 + b * s2[t - 1]
        r[t] = np.sqrt(s2[t]) * z[t]
    return r[burn:], np.sqrt(s2[burn:]), z[burn:]


# =============================================================================
# (1) VaR and ES on a loss density
# =============================================================================
def fig_var_es_density(alpha=0.05, nu=4):
    d = unit_t(nu)
    var = d.ppf(1 - alpha)
    es = es_t(alpha, nu)
    x = np.linspace(-4.5, 6.5, 1101)
    f = d.pdf(x)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, f, color=MainBlue, lw=1.4, label=f'Loss density, Student-$t$({nu}), sd 1')
    m = x >= var
    ax.fill_between(x[m], 0, f[m], color=IDAred, alpha=0.55, lw=0, label=rf'Tail, probability $\alpha$ = {alpha:.0%}')
    ax.axvline(var, color=IDAred, lw=1.1, ls='--')
    ax.axvline(es, color=Forest, lw=1.1, ls='-.')
    ax.text(var - 0.15, 0.56, f'VaR = {var:.2f}', ha='right', color=IDAred, fontsize=7.2)
    ax.text(es + 0.1, 0.30, f'ES = {es:.2f}\n(mean of\nthe red tail)', ha='left', color=Forest, fontsize=7.2)
    ax.set_xlim(-4.5, 6.5); ax.set_ylim(0, 0.64)
    ax.set_xlabel('Loss $L = -X$ (standard deviations)')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch7_sem_primer_var_es_density')
    return dict(var=float(var), es=float(es))


# =============================================================================
# (2) Normal against Student-t with the same standard deviation: VaR and ES across levels
# =============================================================================
def fig_normal_t(nu=4):
    al = np.geomspace(0.001, 0.1, 200)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    x = np.linspace(1.5, 6, 300)
    ax.plot(x, stats.norm.pdf(x), color=MainBlue, lw=1.3, label='Normal, sd 1')
    ax.plot(x, unit_t(nu).pdf(x), color=IDAred, lw=1.3, label=f'Student-$t$({nu}), sd 1')
    ax.set_yscale('log'); ax.set_ylim(1e-6, 0.3)
    ax.set_xlabel('Loss (standard deviations)'); ax.set_ylabel('Density (log)')
    ax.set_title('Right tail of the loss', loc='left')
    ax = axes[1]
    zN = -stats.norm.ppf(al)
    ax.plot(al, zN, color=MainBlue, lw=1.3, ls='--')
    ax.plot(al, stats.norm.pdf(stats.norm.ppf(al)) / al, color=MainBlue, lw=1.3)
    ax.plot(al, unit_t(nu).ppf(1 - al), color=IDAred, lw=1.3, ls='--')
    ax.plot(al, es_t(al, nu), color=IDAred, lw=1.3)
    ax.set_xscale('log'); ax.invert_xaxis()
    ax.set_xlabel(r'Tail probability $\alpha$ (log scale)')
    ax.set_ylabel('In sd units')
    ax.set_title(r'VaR$_\alpha$ (dashed) and ES$_\alpha$ (solid)', loc='left')
    for a in (0.01, 0.025):
        ax.axvline(a, color=Navy, lw=0.5, ls=':')
    bottom_legend(fig, axes[0], ncol=2)
    fig.subplots_adjust(wspace=0.38)
    save_fig(fig, 'ch7_sem_primer_normal_t')


# =============================================================================
# (3) a loss with an atom: distribution function, VaR as generalised inverse, ES filling the tail
# =============================================================================
def fig_discrete(p=0.04, lgd=50):
    fig, ax = plt.subplots(figsize=HALF)
    ax.hlines(1 - p, -10, lgd, color=MainBlue, lw=1.6)
    ax.hlines(1.0, lgd, 70, color=MainBlue, lw=1.6, label=r'$F_L(x) = P(L \leq x)$')
    ax.plot([lgd], [1 - p], 'o', mfc='white', color=MainBlue, ms=3.5)
    ax.plot([lgd], [1.0], 'o', color=MainBlue, ms=3.5)
    ax.vlines(lgd, 1 - p, 1, color=MainBlue, lw=0.6, ls=':')
    for a, col in ((0.05, Forest), (0.02, IDAred)):
        ax.axhline(1 - a, color=col, lw=0.9, ls='--', label=rf'level $1-\alpha$, $\alpha$ = {a:.0%}')
    ax.annotate(r'$\alpha$ = 5%: VaR = 0', xy=(0, 0.95), xytext=(5, 0.935), fontsize=7.2, color=Forest)
    ax.annotate(r'$\alpha$ = 2%: VaR = 50', xy=(lgd, 0.98), xytext=(14, 0.985), fontsize=7.2, color=IDAred,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.7))
    ax.text(lgd + 1.5, 0.975, f'jump of\n{p:.0%} at {lgd}', fontsize=7.0, color=MainBlue)
    ax.set_xlim(-10, 70); ax.set_ylim(0.92, 1.005)
    ax.set_xlabel('Loss $x$')
    ax.set_ylabel('$P(L \\leq x)$')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch7_sem_primer_discrete')
    # ES at 5% with the discrete formula: (E[L 1{L > VaR}] + VaR (alpha - P(L > VaR))) / alpha
    return dict(es5=(lgd * p + 0 * (0.05 - p)) / 0.05, es2=(0 + lgd * 0.02) / 0.02)


# =============================================================================
# (4) ES as the minimum of G(v) = v + E[(L - v)+] / alpha (Normal loss)
# =============================================================================
def fig_es_min(alpha=0.025):
    v = np.linspace(0.5, 3.5, 300)
    EL = stats.norm.pdf(v) - v * stats.norm.sf(v)            # E[(L - v)+] for L ~ N(0, 1)
    G = v + EL / alpha
    var = stats.norm.ppf(1 - alpha); es = stats.norm.pdf(var) / alpha
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(v, G, color=MainBlue, lw=1.5, label=r'$G(v) = v + \mathrm{E}[(L-v)_+]/\alpha$')
    ax.plot(var, es, 'o', color=IDAred, ms=4.5, label='minimum')
    ax.vlines(var, 1.9, es, color=IDAred, lw=0.8, ls='--')
    ax.hlines(es, 0.5, var, color=Forest, lw=0.8, ls='--')
    ax.text(var + 0.06, 1.95, f'argmin = VaR = {var:.2f}', color=IDAred, fontsize=7.2)
    ax.text(0.55, es + 0.05, f'min = ES = {es:.2f}', color=Forest, fontsize=7.2)
    ax.set_xlim(0.5, 3.5); ax.set_ylim(1.9, 3.6)
    ax.set_xlabel('Candidate threshold $v$')
    ax.set_ylabel('$G(v)$')
    ax.set_title(r'$L \sim N(0, 1)$, $\alpha$ = 2.5%', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch7_sem_primer_es_min')
    return dict(var=float(var), es=float(es))


# =============================================================================
# (5) historical simulation: sorted losses, interpolated quantile, tail mean
# =============================================================================
def fig_hs(n=40, alpha=0.10, seed=75):
    rng = np.random.default_rng(seed)
    L = np.sort(unit_t(4).rvs(n, random_state=rng))
    pos = 1 + (n - 1) * (1 - alpha)                          # np.quantile, linear interpolation (1-based)
    var = float(np.quantile(L, 1 - alpha))
    tail = L[L >= var]
    es = float(tail.mean())
    k = np.arange(1, n + 1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(k, L, 'o', color=MainBlue, ms=2.6, label='sorted losses $L_{(1)} \\leq \\dots \\leq L_{(n)}$')
    ax.plot(k[L >= var], tail, 'o', color=IDAred, ms=3.2, label=f'the $k$ = {len(tail)} losses $\\geq$ VaR')
    ax.axhline(var, color=IDAred, lw=0.9, ls='--')
    ax.axhline(es, color=Forest, lw=0.9, ls='-.')
    ax.axvline(pos, color=Navy, lw=0.6, ls=':')
    ax.text(1, var + 0.12, f'VaR 10% = {var:.2f} (position {pos:.1f})', color=IDAred, fontsize=7.0)
    ax.text(1, es + 0.12, f'ES 10% = {es:.2f}', color=Forest, fontsize=7.0)
    ax.set_xlabel(f'Rank $i$ ($n$ = {n})')
    ax.set_ylabel('Loss')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch7_sem_primer_hs')
    return dict(var=var, es=es, pos=pos, k=len(tail))


# =============================================================================
# (6) i.i.d. against moving-block bootstrap on a volatility-clustered series
# =============================================================================
def fig_bootstrap(T=1500, block=20, B=1000, alpha=0.01, seed=76):
    r, _, _ = sim_garch_t(T, a=0.12, b=0.87, seed=seed)
    rng = np.random.default_rng(seed + 1)
    iid = r[rng.integers(0, T, T)]
    starts = rng.integers(0, T - block + 1, T // block + 1)
    blk = np.concatenate([r[s:s + block] for s in starts])[:T]
    v_iid, v_blk = [], []
    for _ in range(B):
        v_iid.append(np.quantile(-r[rng.integers(0, T, T)], 1 - alpha))
        st = rng.integers(0, T - block + 1, T // block + 1)
        v_blk.append(np.quantile(-np.concatenate([r[s:s + block] for s in st])[:T], 1 - alpha))
    fig, axes = plt.subplots(1, 3, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1, 0.9]))
    lim = 1.05 * np.abs(r).max()
    for ax, x, ttl, col in ((axes[0], iid, 'i.i.d. resample', IDAred), (axes[1], blk, f'{block}-day block resample', Forest)):
        ax.plot(x, color=col, lw=0.35)
        ax.set_ylim(-lim, lim); ax.set_xlim(0, T)
        ax.set_title(ttl, loc='left'); ax.set_xlabel('Day')
    axes[0].set_ylabel('Return (%)')
    ax = axes[2]
    bins = np.linspace(min(v_iid + v_blk), max(v_iid + v_blk), 40)
    ax.hist(v_iid, bins=bins, color=IDAred, alpha=0.55, label='i.i.d.')
    ax.hist(v_blk, bins=bins, color=Forest, alpha=0.55, label='block')
    ax.axvline(np.quantile(-r, 1 - alpha), color=Navy, lw=1.0, label='sample VaR 1%')
    ax.set_xlabel('Bootstrap VaR 1%'); ax.set_title(f'{B} resamples', loc='left')
    bottom_legend(fig, axes[2], ncol=3)
    save_fig(fig, 'ch7_sem_primer_bootstrap')
    return dict(sd_iid=float(np.std(v_iid)), sd_blk=float(np.std(v_blk)))


# =============================================================================
# (7) filtered (FHS) VaR against a rolling historical VaR, with exceedances
# =============================================================================
def fig_fhs(T=2000, win=500, alpha=0.01, seed=77):
    r, s, z = sim_garch_t(T + win, seed=seed)
    xi = np.quantile(-z, 1 - alpha)                          # quantile of the (here: true) standardised shocks
    fhs = s * xi
    hs = np.array([np.quantile(-r[t - win:t], 1 - alpha) for t in range(win, T + win)])
    rr = r[win:]; fhs = fhs[win:]
    t = np.arange(T)
    e_f = -rr > fhs; e_h = -rr > hs
    fig, ax = plt.subplots(figsize=(5.55, 1.45))
    ax.plot(t, -rr, color=MainBlue, lw=0.35, label='loss $L_t$')
    ax.plot(t, fhs, color=Forest, lw=1.0, label=f'FHS VaR 1%: {e_f.sum()} exceedances')
    ax.plot(t, hs, color=Amber, lw=1.0, label=f'HS VaR 1%, rolling {win} days: {e_h.sum()} exceedances')
    ax.plot(t[e_h], -rr[e_h], 'v', color=IDAred, ms=3, label='HS exceedance')
    ax.set_xlim(0, T); ax.set_xlabel('Day $t$ (forecast for $t$ uses data up to $t-1$)'); ax.set_ylabel('Loss (%)')
    ax.set_title(f'Simulated GARCH returns; expected exceedances $n\\alpha$ = {T * alpha:.0f}', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch7_sem_primer_fhs')
    return dict(exc_fhs=int(e_f.sum()), exc_hs=int(e_h.sum()))


# =============================================================================
# (8) longer horizons: h-day VaR against the square-root-of-time rule
# =============================================================================
def fig_horizon(n=400_000, alpha=0.01, seed=78, hs=(1, 2, 5, 10, 20)):
    rng = np.random.default_rng(seed)
    series = {}
    series['i.i.d. Normal'] = rng.standard_normal(n)
    series['i.i.d. Student-$t$(4)'] = unit_t(4).rvs(n, random_state=rng)
    e = rng.standard_normal(n); ar = np.empty(n); ar[0] = e[0]
    for t in range(1, n):
        ar[t] = 0.2 * ar[t - 1] + e[t]
    series['AR(1), $\\phi$ = 0.2'] = ar / ar.std()
    g, _, _ = sim_garch_t(n, seed=seed)
    series['GARCH'] = g / g.std()
    cols = [MainBlue, Amber, IDAred, Forest]
    fig, ax = plt.subplots(figsize=HALF)
    hh = np.array(hs)
    ax.plot(hh, np.sqrt(hh), color=Navy, lw=1.0, ls='--', label=r'$\sqrt{h}$ rule')
    out = {}
    for (lab, x), col in zip(series.items(), cols):
        v1 = np.quantile(-x, 1 - alpha)
        ratio = []
        for h in hs:
            c = np.cumsum(np.r_[0, x])
            sh = c[h:] - c[:-h]                                  # overlapping h-day sums
            ratio.append(np.quantile(-sh, 1 - alpha) / v1)
        ax.plot(hh, ratio, 'o-', color=col, lw=1.1, ms=2.5, label=lab)
        out[lab] = ratio
    ax.set_xlabel('Horizon $h$ (days)')
    ax.set_ylabel(r'VaR$^{(h)}$ / VaR$^{(1)}$')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch7_sem_primer_horizon')
    return out


# =============================================================================
# (9) the generalised Pareto tail
# =============================================================================
def fig_gpd(n=5000, q=0.95, seed=79):
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    y = np.linspace(0, 6, 400)
    for xi, col in ((-0.2, Forest), (0.0, MainBlue), (0.3, IDAred)):
        ax.plot(y, stats.genpareto.pdf(y, xi), color=col, lw=1.3, label=rf'$\xi$ = {xi}')
    ax.set_yscale('log'); ax.set_ylim(1e-4, 1.2)
    ax.set_xlabel(r'Excess $y$ ($\beta$ = 1)'); ax.set_ylabel('Density (log)')
    ax.set_title('GPD densities', loc='left')
    ax.legend(frameon=False, loc='lower left', fontsize=7.0)
    rng = np.random.default_rng(seed)
    L = unit_t(3).rvs(n, random_state=rng)
    u = np.quantile(L, q)
    ex = L[L > u] - u
    xi, _, beta = stats.genpareto.fit(ex, floc=0)
    ax = axes[1]
    ax.hist(ex, bins=40, density=True, color=BandBlue, ec=MainBlue, lw=0.3, label=f'{len(ex)} excesses over $u$')
    yy = np.linspace(0, ex.max(), 300)
    ax.plot(yy, stats.genpareto.pdf(yy, xi, scale=beta), color=IDAred, lw=1.3,
            label=rf'fitted GPD, $\hat\xi$ = {xi:.2f}, $\hat\beta$ = {beta:.2f}')
    ax.set_yscale('log')
    ax.set_xlabel(f'Excess $L - u$, $u$ = 95% quantile = {u:.2f}')
    ax.set_title(f'Simulated Student-$t$(3) losses, $n$ = {n:,}', loc='left')
    bottom_legend(fig, axes[1], ncol=2)
    save_fig(fig, 'ch7_sem_primer_gpd')
    return dict(xi=float(xi), beta=float(beta), u=float(u), Nu=int(len(ex)))


# =============================================================================
# (10) exceedances: independent against clustered
# =============================================================================
def fig_extremal(T=3000, seed=80, q=0.98):
    rng = np.random.default_rng(seed)
    iid = unit_t(5).rvs(T, random_state=rng)
    g, _, _ = sim_garch_t(T, a=0.12, b=0.86, seed=seed)
    fig, ax = plt.subplots(figsize=(5.55, 1.05))
    out = {}
    for y0, (lab, x, col) in enumerate((('GARCH (clustered)', g, IDAred), ('i.i.d.', iid, MainBlue))):
        u = np.quantile(-x, q)
        S = np.where(-x > u)[0]
        ax.vlines(S, y0 + 0.1, y0 + 0.9, color=col, lw=0.8)
        Ti = np.diff(S)
        th = min(1, 2 * np.sum(Ti - 1) ** 2 / ((len(Ti)) * np.sum((Ti - 1) * (Ti - 2)))) if Ti.max() > 2 else 1
        ax.text(T + 30, y0 + 0.5, f'{lab}: $N$ = {len(S)}, $\\hat\\theta$ = {th:.2f}', va='center', fontsize=7.2,
                color=col)
        out[lab] = (len(S), th)
    ax.set_xlim(0, T); ax.set_ylim(0, 2)
    ax.set_yticks([])
    ax.set_xlabel('Day (vertical line: loss above the 98% quantile)')
    fig.tight_layout(pad=0.3)
    save_fig(fig, 'ch7_sem_primer_extremal')
    return out


# =============================================================================
# (11) Euler allocation: capital shares against risk shares (three hypothetical assets)
# =============================================================================
def fig_euler():
    w = np.array([0.5, 0.3, 0.2])
    sd = np.array([0.15, 0.06, 0.60])
    C = np.array([[1, -0.2, 0.3], [-0.2, 1, 0.0], [0.3, 0.0, 1]])
    S = C * np.outer(sd, sd)
    sp = np.sqrt(w @ S @ w)
    share = w * (S @ w) / sp ** 2
    fig, ax = plt.subplots(figsize=HALF)
    x = np.arange(3); bw = 0.38
    ax.bar(x - bw / 2, 100 * w, bw, color=BandBlue, ec=MainBlue, lw=0.6, label='capital weight $w_i$')
    ax.bar(x + bw / 2, 100 * share, bw, color=IDAred, label=r'risk share $w_i(\Sigma w)_i / w^\top\Sigma w$')
    for i in range(3):
        ax.text(x[i] + bw / 2, 100 * share[i] + 1.5, f'{100 * share[i]:.0f}%', ha='center', fontsize=7.0, color=IDAred)
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xticks(x); ax.set_xticklabels([f'equity\nsd {sd[0]:.0%}', f'bonds\nsd {sd[1]:.0%}', f'crypto\nsd {sd[2]:.0%}'])
    ax.set_ylabel('% of total')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch7_sem_primer_euler')
    return dict(share=share.round(3).tolist())


# =============================================================================
# (12) Cornish-Fisher transform: monotone or not
# =============================================================================
def fig_cornish_fisher(S=0.0):
    z = np.linspace(-3.5, 0.5, 400)
    fig, ax = plt.subplots(figsize=HALF)
    for K, col in ((0, MainBlue), (4, Forest), (12, IDAred)):
        zt = z + (z ** 2 - 1) * S / 6 + (z ** 3 - 3 * z) * K / 24 - (2 * z ** 3 - 5 * z) * S ** 2 / 36
        ax.plot(z, zt, color=col, lw=1.4, label=f'$K$ = {K}')
    ax.plot(z, z, color=Navy, lw=0.6, ls=':')
    ax.set_ylim(-9, 1.5)
    ax.annotate('decreasing near 0:\nnot a quantile function', xy=(-0.5, 0.1), xytext=(-1.9, -6.5), fontsize=7.0,
                color=IDAred, arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.7))
    ax.set_xlabel(r'Normal quantile $z$')
    ax.set_ylabel(r'$\tilde z(z)$')
    ax.set_title('$S$ = 0; dotted: $\\tilde z = z$', loc='left')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch7_sem_primer_cornish_fisher')


# =============================================================================
# (13) pinball loss and a CAViaR path
# =============================================================================
def fig_pinball_caviar(T=1000, seed=81, alpha=0.01, b=(0.02, 0.90, 0.30)):
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.5]))
    ax = axes[0]
    e = np.linspace(-3, 3, 300)                              # e = r + VaR: the return relative to -VaR
    for a, col in ((0.01, IDAred), (0.10, Amber), (0.50, MainBlue)):
        ax.plot(e, (a - (e < 0)) * e, color=col, lw=1.3, label=rf'$\alpha$ = {a:.0%}')
    ax.set_xlabel(r'$r_t + \mathrm{VaR}_t$ (return minus quantile $-\mathrm{VaR}_t$)')
    ax.set_ylabel('Pinball loss')
    ax.set_title('Slope $\\alpha - 1$ left of 0, $\\alpha$ right', loc='left')
    ax.legend(frameon=False, loc='upper center', fontsize=7.0)
    r, _, _ = sim_garch_t(T, seed=seed)
    v = np.empty(T); v[0] = np.quantile(-r[:300], 1 - alpha)
    for t in range(1, T):
        v[t] = b[0] + b[1] * v[t - 1] + b[2] * abs(r[t - 1])
    ax = axes[1]
    ax.plot(r, color=MainBlue, lw=0.35, label='return $r_t$')
    ax.plot(-v, color=IDAred, lw=1.0, label=r'$-\mathrm{VaR}_t$, SAV: $\beta_0 + \beta_1\mathrm{VaR}_{t-1} + \beta_2|r_{t-1}|$')
    ax.set_xlim(0, T); ax.set_xlabel('Day $t$')
    ax.set_title(rf'Simulated; $\beta$ = {b}', loc='left')
    bottom_legend(fig, axes[1], ncol=2)
    save_fig(fig, 'ch7_sem_primer_pinball_caviar')


def run_all():
    res = {}
    res['density'] = fig_var_es_density()
    fig_normal_t()
    res['discrete'] = fig_discrete()
    res['es_min'] = fig_es_min()
    res['hs'] = fig_hs()
    res['boot'] = fig_bootstrap()
    res['fhs'] = fig_fhs()
    res['horizon'] = fig_horizon()
    res['gpd'] = fig_gpd()
    res['extremal'] = fig_extremal()
    res['euler'] = fig_euler()
    fig_cornish_fisher()
    fig_pinball_caviar()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

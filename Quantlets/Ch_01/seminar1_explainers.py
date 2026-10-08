"""
seminar1_explainers.py -- Explanatory (primer) charts for Seminar 1 (MFM): stylised facts and returns
=====================================================================================================
Teaching charts for the primer slides "Prerequisites for Today" / "Noțiuni necesare azi" of Seminar 1,
which takes place BEFORE Lecture 1. All charts use SIMULATED data only (fixed seeds): they illustrate
the concepts (Brownian motion, heavy tails, quantiles and VaR, QQ plots, ACF and volatility clustering,
mixtures of Normals, aggregation, drawdown, daily range) and contain no exercise answers.

Output: charts/ch1_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom), drawn at the
exact size of their box on the slides (1 pt in the figure = 1 pt on the slide; tick labels 6.8 pt, no text below
6.3 pt apart from math sub- and superscripts).

Run:  python3 Quantlets/Ch_01/seminar1_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

# drawn at the size of the slide box: fonts in pt as they appear on the slide
plt.rcParams.update({'font.size': 7.2, 'axes.labelsize': 7.2, 'axes.titlesize': 7.2, 'xtick.labelsize': 6.8,
                     'ytick.labelsize': 6.8, 'legend.fontsize': 6.8, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
                     'xtick.minor.width': 0.4, 'ytick.minor.width': 0.4, 'xtick.minor.size': 1.5,
                     'ytick.minor.size': 1.5, 'xtick.major.pad': 2.0, 'ytick.major.pad': 2.0,
                     'axes.labelpad': 2.0, 'axes.titlepad': 3, 'legend.handlelength': 1.6,
                     'legend.columnspacing': 1.2, 'legend.handletextpad': 0.5, 'legend.borderaxespad': 0.2})

# box of every chart on the slides of Seminar 1 (EN and RO decks identical):
# \includegraphics[width=\textwidth, height=c\textheight, keepaspectratio] with \textwidth = 409.72 pt and
# \textheight = 212.40 pt (TeX points, 72.27 per inch) in the seminar decks; the two-column slides use a column of
# 0.50 or 0.49 \textwidth. Matplotlib works in PostScript points (72 per inch): the box is converted.
PT = 72 / 72.27
TW, TH = 409.72 * PT, 212.40 * PT
BOX = {'brownian': (TW, 0.56 * TH), 'drawdown': (0.50 * TW, 0.80 * TH), 'fourth_power': (TW, 0.56 * TH),
       'var_density': (0.49 * TW, 0.80 * TH), 'normal_t': (TW, 0.56 * TH), 'acf_clustering': (TW, 0.62 * TH),
       'mixture': (TW, 0.56 * TH), 'aggregation': (TW, 0.52 * TH), 'qq': (TW, 0.47 * TH),
       'ohlc': (0.49 * TW, 0.80 * TH)}


def new_fig(key, nrows=1, ncols=1, **kw):
    """Figure with the exact size of the box of chart `key` on the slide."""
    w, h = BOX[key]
    return plt.subplots(nrows, ncols, figsize=(w / 72, h / 72), **kw)


def save_fig(fig, name):
    """The whole figure is saved (no tight bounding box): the PDF has exactly the size of the slide box."""
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.canvas.draw()
    tb = fig.get_tightbbox(fig.canvas.get_renderer())          # inches, everything that is drawn
    w, h = fig.get_size_inches()
    if tb.x0 < -0.005 or tb.y0 < -0.005 or tb.x1 > w + 0.005 or tb.y1 > h + 0.005:
        print(f'   WARNING {name}: drawing outside the figure: {tb} vs {w:.3f} x {h:.3f} in')
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), transparent=True, dpi=300)
    plt.close(fig)
    print(f'   saved {name}')


def bottom_legend(fig, axes=None, ncol=3, handles=None, labels=None, w_pad=1.2, h_pad=0.6):
    """Legend outside the plot, centred at the bottom of the figure; the axes fill the space above it."""
    if handles is None:
        handles, labels = [], []
        for ax in np.atleast_1d(axes).ravel():
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels and not l.startswith('_'):
                    handles.append(h); labels.append(l)
    leg = fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)
    fig.canvas.draw()
    lb = leg.get_window_extent()
    if lb.width > fig.bbox.width:
        print(f'   WARNING: legend wider than the figure ({lb.width:.0f} > {fig.bbox.width:.0f} px)')
    gap = 1.5 / 72 * fig.dpi                    # 1.5 pt between the x-axis labels and the legend
    fig.tight_layout(pad=0.25, w_pad=w_pad, h_pad=h_pad, rect=(0, (lb.height + gap) / fig.bbox.height, 1, 1))
    return leg


def _pct(p):
    """Probability as a readable percentage (no scientific notation)."""
    v = 100 * p
    if v >= 0.01:
        return f'{v:.2g}%'
    d = int(np.ceil(-np.log10(v)))          # first significant decimal
    return f'{v:.{d}f}%'


def unit_t(nu):
    """Student-t with nu degrees of freedom, rescaled to unit variance (nu > 2)."""
    return stats.t(nu, scale=np.sqrt((nu - 2) / nu))


# =============================================================================
# (i) Brownian motion and geometric Brownian motion
# =============================================================================
def fig_brownian(seed=42, n_paths=5, years=5, q=252, mu=0.05, sigma=0.20):
    rng = np.random.default_rng(seed)
    n = years * q
    t = np.arange(n + 1) / q
    W = np.concatenate([np.zeros((n_paths, 1)),
                        np.cumsum(rng.standard_normal((n_paths, n)) / np.sqrt(q), axis=1)], axis=1)
    cols = [MainBlue, IDAred, Forest, Amber, Navy]
    fig, axes = new_fig('brownian', 1, 2)
    ax = axes[0]
    ax.fill_between(t, -1.96 * np.sqrt(t), 1.96 * np.sqrt(t), color=BandBlue, alpha=0.8,
                    label=r'95% band $\pm 1.96\sqrt{t}$', lw=0)
    for i in range(n_paths):
        ax.plot(t, W[i], color=cols[i], lw=0.54, label='Simulated paths' if i == 0 else '_')
    ax.axhline(0, color=Navy, lw=0.36, ls=':')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('$W_t$')
    ax.set_title('Brownian motion $W_t$', loc='left')
    ax = axes[1]
    P = 100 * np.exp(mu * t + sigma * W)
    for i in range(n_paths):
        ax.plot(t, P[i], color=cols[i], lw=0.54)
    ax.plot(t, 100 * np.exp(mu * t), color=Navy, lw=0.78, ls='--', label=r'Median price $100\,e^{\mu t}$')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('Price $P_t$')
    ax.set_title(r'Price $P_t = 100\,e^{\mu t + \sigma W_t}$', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch1_sem_primer_brownian')
    return dict(final_W=W[:, -1].round(3).tolist(), final_P=P[:, -1].round(1).tolist())


# =============================================================================
# (ix) drawdown of a simulated price path
# =============================================================================
def fig_drawdown(seed=13, years=3, q=252, mu=0.06, sigma=0.22):
    rng = np.random.default_rng(seed)
    n = years * q
    t = np.arange(n + 1) / q
    x = np.concatenate([[0.0], np.cumsum(mu / q + sigma / np.sqrt(q) * rng.standard_normal(n))])
    V = 100 * np.exp(x)
    M = np.maximum.accumulate(V)
    DD = V / M - 1
    i_min = int(np.argmin(DD))
    i_peak = int(np.argmax(V[:i_min + 1]))
    fig, axes = new_fig('drawdown', 2, 1, sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1]))
    ax = axes[0]
    ax.plot(t, V, color=MainBlue, lw=0.6, label='Value $V_t$')
    ax.plot(t, M, color=Amber, lw=0.78, ls='--', label=r'Running max $M_t$')
    ax.fill_between(t, V, M, color=BandBlue, alpha=0.8, lw=0)
    ax.plot(t[i_peak], V[i_peak], 'o', color=Forest, ms=3, label='Peak')
    ax.plot(t[i_min], V[i_min], 'o', color=IDAred, ms=3, label='Trough')
    ax.set_ylabel('$V_t$')
    ax.set_title('Value and running maximum', loc='left')
    ax = axes[1]
    ax.fill_between(t, 100 * DD, 0, color=IDAred, alpha=0.35, lw=0)
    ax.plot(t, 100 * DD, color=IDAred, lw=0.54, label='Drawdown $DD_t$')
    ax.annotate(f'MDD = {100 * DD[i_min]:.1f}%', (t[i_min], 100 * DD[i_min]),
                xytext=(-60, -4), textcoords='offset points', fontsize=6.8, color=IDAred,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.48))
    ax.set_ylim(100 * DD.min() * 1.35, 3)
    ax.set_xlabel('Time (years)')
    ax.set_ylabel('$DD_t$ (%)')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch1_sem_primer_drawdown')
    return dict(mdd=float(DD[i_min]), peak=float(V[i_peak]), trough=float(V[i_min]))


# =============================================================================
# (iii) why the fourth power: contributions of z^2 and z^4
# =============================================================================
def fig_fourth_power(seed=3, T=2500, nu=4.5, top=10):
    z_vals = np.arange(1, 6)
    fig, axes = new_fig('fourth_power', 1, 2)
    ax = axes[0]
    w = 0.38
    ax.bar(z_vals - w / 2, z_vals ** 2, width=w, color=MainBlue, label='$z^2$ (variance)')
    ax.bar(z_vals + w / 2, z_vals ** 4, width=w, color=IDAred, label='$z^4$ (kurtosis)')
    for z in z_vals:
        ax.text(z - w / 2, z ** 2 * 1.15, f'{z ** 2}', ha='center', fontsize=6.4, color=MainBlue)
        ax.text(z + w / 2, z ** 4 * 1.15, f'{z ** 4}', ha='center', fontsize=6.4, color=IDAred)
    ax.set_yscale('log'); ax.set_ylim(0.6, 2500)
    ax.set_xticks(z_vals)
    ax.set_xlabel('Size of the day $|z_t|$')
    ax.set_ylabel('Contribution (log)')
    ax.set_title('One day: $z^2$ against $z^4$', loc='left')
    # share of the sums coming from the largest days of a simulated heavy-tailed sample
    rng = np.random.default_rng(seed)
    r = unit_t(nu).rvs(T, random_state=rng)
    z = (r - r.mean()) / r.std(ddof=1)
    srt = np.sort(np.abs(z))[::-1]
    ks = np.arange(0, 51)
    s2 = np.r_[0, np.cumsum(srt ** 2)][ks] / np.sum(srt ** 2)
    s4 = np.r_[0, np.cumsum(srt ** 4)][ks] / np.sum(srt ** 4)
    ax = axes[1]
    ax.plot(ks, 100 * s2, color=MainBlue, lw=0.9)
    ax.plot(ks, 100 * s4, color=IDAred, lw=0.9)
    ax.plot(ks, 100 * ks / T, color=Navy, lw=0.6, ls=':', label='Share of days')
    ax.axvline(top, color=Navy, lw=0.36, ls='--')
    ax.annotate(f'{100 * s4[top]:.0f}%', (top, 100 * s4[top]), xytext=(4, -2), textcoords='offset points',
                color=IDAred, fontsize=6.6, va='top')
    ax.annotate(f'{100 * s2[top]:.0f}%', (top, 100 * s2[top]), xytext=(3, 2), textcoords='offset points',
                color=MainBlue, fontsize=6.6, va='bottom')
    ax.set_ylim(0, 100)
    ax.set_xlabel('Largest days counted')
    ax.set_ylabel('Share of the sum (%)')
    ax.set_title(f'Sample, $T$ = {T:,}', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch1_sem_primer_fourth_power')
    return dict(share4_top=float(s4[top]), share2_top=float(s2[top]), kurt=float(np.mean(z ** 4)))


# =============================================================================
# (iv) quantile and VaR on a density
# =============================================================================
def fig_var_density(mu=0.05, sigma=1.0, alpha=0.01):
    q = stats.norm.ppf(alpha, mu, sigma)
    x = np.linspace(-4.2, 4.2, 801)
    f = stats.norm.pdf(x, mu, sigma)
    fig, ax = new_fig('var_density')
    ax.plot(x, f, color=MainBlue, lw=0.9, label=r'Density of $r_t \sim N(\mu, \sigma^2)$')
    m = x <= q
    ax.fill_between(x[m], 0, f[m], color=IDAred, alpha=0.6, lw=0, label=r'Left tail, probability $\alpha$ = 1%')
    ax.axvline(q, color=IDAred, lw=0.72, ls='--', label=rf'Quantile $q_{{0.01}}$ = {q:.2f}%')
    ax.axvline(mu, color=Forest, lw=0.6, ls=':', label=rf'Mean $\mu$ = {mu:.2f}%')
    ax.annotate('', xy=(q, 0.44), xytext=(0, 0.44), arrowprops=dict(arrowstyle='<->', color=Navy, lw=0.6))
    ax.text(q / 2, 0.455, f'VaR = {-q:.2f}%', ha='center', fontsize=6.8, color=Navy)
    ax.annotate('area 1%', xy=(q - 0.25, 0.006), xytext=(-3.9, 0.08), fontsize=6.8, color=IDAred,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.54))
    ax.set_xlim(-4.2, 4.2); ax.set_ylim(0, 0.51)
    ax.set_xlabel('Daily return $r_t$ (%)')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch1_sem_primer_var_density')
    return dict(q=float(q))


# =============================================================================
# (ii) Normal against Student-t(3), same variance; tail probabilities on a log scale
# =============================================================================
def fig_normal_t(nu=3):
    td = unit_t(nu)
    x = np.linspace(-5, 5, 1001)
    fig, axes = new_fig('normal_t', 1, 2)
    ax = axes[0]
    ax.plot(x, stats.norm.pdf(x), color=MainBlue, lw=0.9, label='Normal $N(0,1)$')
    ax.plot(x, td.pdf(x), color=IDAred, lw=0.9, label=f'Student-$t$({nu}), variance 1')
    ax.set_xlabel('$x$ (standard deviations)')
    ax.set_ylabel('Density')
    ax.set_title('Densities, same variance', loc='left')
    ins = ax.inset_axes([0.70, 0.45, 0.28, 0.38])
    xx = np.linspace(2.5, 5, 200)
    ins.plot(xx, stats.norm.pdf(xx), color=MainBlue, lw=0.78)
    ins.plot(xx, td.pdf(xx), color=IDAred, lw=0.78)
    ins.set_xlim(2.5, 5); ins.set_ylim(0, 0.03); ins.set_xticks([3, 4, 5])
    ins.set_title('tail zoom', fontsize=6.3, pad=1.5)
    ins.set_yticks([0, 0.02])
    ins.tick_params(labelsize=6.3, length=1.5, pad=1)
    ax = axes[1]
    k = np.linspace(0, 8, 401)
    pn, pt = 2 * stats.norm.sf(k), 2 * td.sf(k)
    ax.plot(k, pn, color=MainBlue, lw=0.9)
    ax.plot(k, pt, color=IDAred, lw=0.9)
    for kk in (3, 5):
        a, b = 2 * stats.norm.sf(kk), 2 * td.sf(kk)
        ax.plot([kk, kk], [a, b], 'o', color=Navy, ms=2.1)
        ax.annotate(_pct(b), (kk, b), xytext=(1, 3), textcoords='offset points', fontsize=6.4, va='bottom',
                    color=IDAred)
        ax.annotate(_pct(a), (kk, a), xytext=(-3, -2), textcoords='offset points', fontsize=6.4,
                    color=MainBlue, ha='right', va='top')
    ax.set_yscale('log'); ax.set_ylim(1e-12, 1.5)
    ax.set_xlabel('Threshold $k$ (st. dev.)')
    ax.set_ylabel(r'$P(|X| > k)$')
    ax.set_title('Tail probabilities, log scale', loc='left')
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch1_sem_primer_normal_t')
    return dict(p3_norm=float(2 * stats.norm.sf(3)), p3_t=float(2 * td.sf(3)),
                p5_norm=float(2 * stats.norm.sf(5)), p5_t=float(2 * td.sf(5)))


# =============================================================================
# (vi) ACF: i.i.d. noise against a series with volatility clustering
# =============================================================================
def _acf(x, K):
    x = x - x.mean()
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, K + 1)])


def simulate_garch(T, omega=0.05, a=0.10, b=0.85, seed=11, burn=500):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(T + burn)
    r = np.empty(T + burn)
    s2 = omega / (1 - a - b)
    for t in range(T + burn):
        r[t] = np.sqrt(s2) * e[t]
        s2 = omega + a * r[t] ** 2 + b * s2
    return r[burn:]


def fig_acf_clustering(T=2500, K=40, seed=10):
    rng = np.random.default_rng(seed + 1)
    iid = rng.standard_normal(T)
    g = simulate_garch(T, seed=seed)
    band = 1.96 / np.sqrt(T)
    lags = np.arange(1, K + 1)
    fig, axes = new_fig('acf_clustering', 2, 2, gridspec_kw=dict(height_ratios=[1, 1.15]))
    axes[0, 0].plot(iid, color=MainBlue, lw=0.24)
    axes[0, 0].set_title('i.i.d. Normal noise', loc='left')
    axes[0, 1].plot(g, color=IDAred, lw=0.24)
    axes[0, 1].set_title('Volatility clustering (GARCH)', loc='left')
    lim = 1.05 * max(np.abs(iid).max(), np.abs(g).max())
    for ax in axes[0]:
        ax.set_ylim(-lim, lim); ax.set_xlim(0, T)
    axes[0, 0].set_ylabel('$r_t$')
    for ax, x, col in ((axes[1, 0], iid, MainBlue), (axes[1, 1], g, IDAred)):
        ax.axhspan(-band, band, color=BandBlue, alpha=0.9, lw=0, label=r'i.i.d. band $\pm 1.96/\sqrt{T}$')
        ax.vlines(lags - 0.15, 0, _acf(x, K), color=col, lw=0.96)
        ax.vlines(lags + 0.2, 0, _acf(np.abs(x), K), color=Amber, lw=0.96)
        ax.axhline(0, color=Navy, lw=0.36)
        ax.set_ylim(-0.08, 0.32); ax.set_xlabel('Lag $k$ (days)')
    axes[1, 0].set_ylabel(r'$\hat\rho_k$')
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([], [], color=MainBlue, lw=1.2), Line2D([], [], color=IDAred, lw=1.2),
               Line2D([], [], color=Amber, lw=1.2), Patch(color=BandBlue)]
    labels = ['ACF of $r_t$ (i.i.d.)', 'ACF of $r_t$ (GARCH)', r'ACF of $|r_t|$',
              r'band $\pm 1.96/\sqrt{T}$']
    bottom_legend(fig, ncol=4, handles=handles, labels=labels)
    save_fig(fig, 'ch1_sem_primer_acf_clustering')
    return dict(band=band, rho1_abs_garch=float(_acf(np.abs(g), 1)[0]), rho1_abs_iid=float(_acf(np.abs(iid), 1)[0]),
                rho1_garch=float(_acf(g, 1)[0]))


# =============================================================================
# (vii) a mixture of two Normals against the Normal with the same variance
# =============================================================================
def fig_mixture(p=(0.7, 0.3), s=(0.6, 1.6)):
    x = np.linspace(-7, 7, 1401)
    comp = [pi * stats.norm.pdf(x, 0, si) for pi, si in zip(p, s)]
    mix = comp[0] + comp[1]
    var = p[0] * s[0] ** 2 + p[1] * s[1] ** 2
    K = 3 * (p[0] * s[0] ** 4 + p[1] * s[1] ** 4) / var ** 2
    nor = stats.norm.pdf(x, 0, np.sqrt(var))
    fig, axes = new_fig('mixture', 1, 2)
    for ax in axes:
        ax.plot(x, comp[0], color=Forest, lw=0.66, ls='--', label=rf'calm days: {p[0]}$\times N(0, {s[0]}^2)$')
        ax.plot(x, comp[1], color=Amber, lw=0.66, ls='--', label=rf'turbulent days: {p[1]}$\times N(0, {s[1]}^2)$')
        ax.plot(x, mix, color=MainBlue, lw=0.96, label=f'Mixture (kurtosis {K:.1f})')
        ax.plot(x, nor, color=IDAred, lw=0.72, label=f'Normal, same variance {var:.2f} (kurtosis 3)')
        ax.set_xlabel('Return $r_t$')
    axes[0].set_xlim(-4, 4); axes[0].set_ylabel('Density')
    axes[0].set_title('Centre: more peaked', loc='left')
    axes[1].set_yscale('log'); axes[1].set_xlim(0, 7); axes[1].set_ylim(1e-8, 1)
    axes[1].set_title('Right tail, log scale', loc='left')
    bottom_legend(fig, axes[0], ncol=2)
    save_fig(fig, 'ch1_sem_primer_mixture')
    return dict(var=var, K=K, p4_mix=float(2 * sum(pi * stats.norm.sf(4, 0, si) for pi, si in zip(p, s))),
                p4_norm=float(2 * stats.norm.sf(4, 0, np.sqrt(var))))


# =============================================================================
# (viii) aggregation: sums of 1, 5, 20 heavy-tailed daily returns
# =============================================================================
def fig_aggregation(nu=5, n_days=2_000_000, hs=(1, 5, 20), seed=5):
    rng = np.random.default_rng(seed)
    r = unit_t(nu).rvs(n_days, random_state=rng)
    kappa = 6 / (nu - 4)
    cols = {1: IDAred, 5: Amber, 20: Forest}
    bins = np.linspace(-8, 8, 161)
    mid = 0.5 * (bins[1:] + bins[:-1])
    fig, axes = new_fig('aggregation', 1, 2)
    out = {}
    for h in hs:
        s = r[: (n_days // h) * h].reshape(-1, h).sum(1)
        z = (s - s.mean()) / s.std()
        dens, _ = np.histogram(z, bins=bins, density=True)
        out[h] = float(np.mean(z ** 4) - 3)
        lab = f'$h$ = {h}: excess kurtosis {kappa / h:.2f}'
        axes[0].plot(mid, dens, color=cols[h], lw=0.84, label=lab)
        a = np.sort(np.abs(z))
        xs = np.linspace(0, 7, 141)
        cnt = len(a) - np.searchsorted(a, xs)
        m = cnt >= 20
        axes[1].plot(xs[m], cnt[m] / len(a), color=cols[h], lw=0.84)
    axes[0].plot(mid, stats.norm.pdf(mid), color=MainBlue, lw=0.72, ls='--', label='Normal $N(0,1)$')
    xs = np.linspace(0, 7, 141)
    axes[1].plot(xs, 2 * stats.norm.sf(xs), color=MainBlue, lw=0.72, ls='--')
    for ax in axes:
        ax.set_xlabel('Standardised $h$-day return')
    axes[1].set_xlabel('Threshold $k$ (st. dev.)')
    axes[0].set_xlim(-4, 4); axes[0].set_ylabel('Density')
    axes[0].set_title('Centre: density', loc='left')
    axes[1].set_yscale('log'); axes[1].set_xlim(0, 7); axes[1].set_ylim(1e-5, 1)
    axes[1].set_ylabel(r'$P(|z| > k)$')
    axes[1].set_title('Tails, log scale', loc='left')
    bottom_legend(fig, axes[0], ncol=2)
    save_fig(fig, 'ch1_sem_primer_aggregation')
    return dict(kappa=kappa, sim_excess=out)


# =============================================================================
# (v) QQ plot: Normal sample against a heavy-tailed sample
# =============================================================================
def fig_qq(T=1000, nu=3, seed=21):
    rng = np.random.default_rng(seed)
    samples = [('Normal sample', rng.standard_normal(T), MainBlue),
               (f'Student-$t$({nu}) sample', stats.t(nu).rvs(T, random_state=rng), IDAred)]
    theo = stats.norm.ppf((np.arange(1, T + 1) - 0.5) / T)
    fig, axes = new_fig('qq', 1, 2, sharey=True)
    for ax, (title, x, col) in zip(axes, samples):
        z = np.sort((x - x.mean()) / x.std(ddof=1))
        ax.plot([-4, 4], [-4, 4], color=Navy, lw=0.6, ls='--', label='45-degree line: Normal')
        ax.plot(theo, z, 'o', color=col, ms=1.44, mfc='none', mew=0.42)
        ax.set_title(title, loc='left')
        ax.set_xlabel('Normal quantile')
        ax.set_xlim(-4, 4); ax.set_ylim(-9, 9)
    axes[0].set_ylabel('Sorted $z_{(i)}$')
    axes[1].annotate('left tail below the line:\nextreme losses larger\nthan under the Normal', xy=(-3.1, -6.5),
                     xytext=(-1.0, -7.8), fontsize=6.4, color=IDAred,
                     arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.48))
    axes[1].annotate('right tail above the line', xy=(3.1, 6.0), xytext=(-3.7, 5.5), fontsize=6.4, color=IDAred,
                     arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.48))
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=Navy, ls='--'),
               Line2D([], [], color=MainBlue, marker='o', ls='', mfc='none'),
               Line2D([], [], color=IDAred, marker='o', ls='', mfc='none')]
    bottom_legend(fig, ncol=3, handles=handles,
                  labels=['45-degree line: perfect Normal fit', 'Normal: points on the line',
                          'Heavy tails: S-shape'], w_pad=2.5)
    save_fig(fig, 'ch1_sem_primer_qq')


# =============================================================================
# (x) one trading day: open, high, low, close and the range
# =============================================================================
def fig_ohlc(seed=4, n=390, sigma_day=0.012):
    rng = np.random.default_rng(seed)
    x = 100 * np.cumsum(np.r_[0, rng.standard_normal(n - 1) * sigma_day / np.sqrt(n)])
    m = np.arange(n)
    ih, il = int(np.argmax(x)), int(np.argmin(x))
    fig, ax = new_fig('ohlc')
    ax.plot(m, x, color=MainBlue, lw=0.6, label='Intraday log price (%)')
    ax.axhline(x[ih], color=Forest, lw=0.48, ls='--')
    ax.axhline(x[il], color=IDAred, lw=0.48, ls='--')
    pts = [(0, x[0], 'open $o_t$', Amber, (3, 4)), (ih, x[ih], 'high $h_t$', Forest, (-36, 3)),
           (il, x[il], 'low $l_t$', IDAred, (3, -8)), (n - 1, x[-1], 'close $c_t$', Navy, (-38, -13))]
    for mm, v, lab, c, off in pts:
        ax.plot(mm, v, 'o', color=c, ms=3.3)
        ax.annotate(lab, (mm, v), xytext=off, textcoords='offset points', fontsize=6.8, color=c)
    # candlestick of the same day, drawn to the right
    xc = n + 45
    ax.vlines(xc, x[il], x[ih], color=Navy, lw=0.72)
    lo, hi = sorted([x[0], x[-1]])
    ax.add_patch(plt.Rectangle((xc - 12, lo), 24, hi - lo, color=Forest if x[-1] > x[0] else IDAred, alpha=0.8))
    ax.text(xc, x[il] - 0.08, 'candle', ha='center', va='top', fontsize=6.6, color=Navy)
    ax.annotate('', xy=(n + 12, x[ih]), xytext=(n + 12, x[il]), arrowprops=dict(arrowstyle='<->', color=Navy, lw=0.6))
    ax.text(n + 6, x[il] + 0.45, 'range\n$h_t - l_t$', ha='right', va='center', fontsize=6.6, color=Navy)
    ax.set_xlim(-10, n + 85)
    ax.set_ylim(x[il] - 0.35, x[ih] + 0.3)
    ax.set_xlabel('Minutes after the open')
    ax.set_ylabel('Log price vs open (%)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch1_sem_primer_ohlc')
    return dict(open=x[0], high=x[ih], low=x[il], close=x[-1], range=x[ih] - x[il])


def run_all():
    res = {}
    res['brownian'] = fig_brownian()
    res['drawdown'] = fig_drawdown()
    res['fourth_power'] = fig_fourth_power()
    res['var_density'] = fig_var_density()
    res['normal_t'] = fig_normal_t()
    res['acf_clustering'] = fig_acf_clustering()
    res['mixture'] = fig_mixture()
    res['aggregation'] = fig_aggregation()
    fig_qq()
    res['ohlc'] = fig_ohlc()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

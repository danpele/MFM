"""
seminar8_explainers.py -- Explanatory (primer) charts for Seminar 8 (MFM): backtesting risk forecasts
=====================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 8,
which takes place BEFORE Lecture 8. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (VaR and ES on a loss density, breaches of a filtered and of an unconditional VaR, the Binomial
count of breaches, the Kupiec likelihood ratio with size and power, clustered breaches and durations, the
null distribution of Z2, consistent scores, HAC standard errors for Diebold--Mariano, split conformal VaR)
and contain no exercise answers (other sample sizes and parameters than in the tasks).

Output: charts/ch8_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_08/seminar8_explainers.py

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

# drawn at slide size: text 7-7.5 pt on the slide (>= 6.3 pt)
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'lines.linewidth': 1.0,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'legend.handlelength': 1.6})

FULL = (5.6, 1.5)     # full slide width, chart above two or three bullets (box 5.69 x 1.86 in)
HALF = (2.55, 1.95)   # one column (0.45 \\textwidth) of a two-column frame (box 2.56 x 2.4 in)
BOX = {'full': (5.69, 1.86), 'half': (2.56, 2.40)}
SCALES = {}


def save_fig(fig, name, box='half'):
    os.makedirs(CHART_DIR, exist_ok=True)
    bb = fig.get_tightbbox(fig.canvas.get_renderer()).padded(0.1)
    w, h = BOX[box]
    SCALES[name] = round(min(1.0, w / bb.width, h / bb.height), 2)   # scale on the slide (fonts 7 pt x scale)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=220)
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
    fig.tight_layout(pad=0.3)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False,
               columnspacing=1.2)


def unit_t(nu):
    """Student-t with nu degrees of freedom, rescaled to unit variance (nu > 2)."""
    return stats.t(nu, scale=np.sqrt((nu - 2) / nu))


def t_es(nu, a):
    """ES (as a positive loss) of the unit-variance Student-t at tail probability a."""
    c = np.sqrt((nu - 2) / nu)
    q = stats.t.ppf(1 - a, nu)
    return c * stats.t.pdf(q, nu) / a * (nu + q ** 2) / (nu - 1)


def simulate_garch(T, seed, omega=0.02, a=0.08, b=0.90, nu=5):
    """GARCH(1,1) losses (in %) with unit-variance Student-t shocks; returns losses and sigma_t."""
    rng = np.random.default_rng(seed)
    z = unit_t(nu).rvs(size=T, random_state=rng)
    s2 = np.empty(T)
    L = np.empty(T)
    s2[0] = omega / (1 - a - b)
    for t in range(T):
        if t > 0:
            s2[t] = omega + a * L[t - 1] ** 2 + b * s2[t - 1]
        L[t] = np.sqrt(s2[t]) * z[t]
    return L, np.sqrt(s2)


# =============================================================================
# (1) VaR and ES on the loss density
# =============================================================================
def fig_var_es(nu=4, a=0.025):
    d = unit_t(nu)
    x = np.linspace(-4.5, 6.5, 800)
    var = d.ppf(1 - a)
    es = t_es(nu, a)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, d.pdf(x), color=MainBlue, lw=1.2, label='Loss density $f$')
    xt = x[x >= var]
    ax.fill_between(xt, d.pdf(xt), color=IDAred, alpha=0.35, lw=0, label=rf'Tail area $\alpha$ = {100 * a:.1f}%')
    ax.axvline(var, color=IDAred, lw=1.0, ls='--', label=f'VaR = {var:.2f}')
    ax.axvline(es, color=Forest, lw=1.2, ls='-', label=f'ES = {es:.2f}')
    ax.annotate('ES: mean loss\nbeyond VaR', xy=(es, 0.012), xytext=(3.0, 0.2), fontsize=7,
                color=Forest, arrowprops=dict(arrowstyle='->', color=Forest, lw=0.7))
    ax.set_xlim(-4.5, 6.5)
    ax.set_ylim(0, 0.62)
    ax.set_xlabel('Daily loss $L_t$ (%), $\\sigma = 1\\%$')
    ax.set_ylabel('Density')
    ax.set_title(rf'Student-$t_{nu}$ losses, $\alpha$ = 2.5%', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch8_sem_primer_var_es')
    return dict(VaR=float(var), ES=float(es))


# =============================================================================
# (2) breaches of an unconditional and of a filtered VaR on a GARCH path
# =============================================================================
def fig_hits(seed=8, T=1500, W=500, a=0.01, nu=5):
    L, sig = simulate_garch(T + W, seed, nu=nu)
    q = unit_t(nu).ppf(1 - a)
    var_f = sig * q                                       # true conditional VaR (filtered)
    var_h = np.array([np.quantile(L[t - W:t], 1 - a) for t in range(W, T + W)])   # HS on the last W days
    L, var_f = L[W:], var_f[W:]
    t = np.arange(T)
    I_h = L > var_h
    I_f = L > var_f
    fig, ax = plt.subplots(figsize=(5.6, 1.4))
    ax.plot(t, L, color=MainBlue, lw=0.45, label='Simulated loss $L_t$ (GARCH)')
    ax.plot(t, var_h, color=Amber, lw=1.1, label=f'HS VaR 1% ({W}-day window)')
    ax.plot(t, var_f, color=Forest, lw=0.8, label='Filtered VaR 1% ($\\sigma_t q$)')
    ax.plot(t[I_h], L[I_h], 'o', color=IDAred, ms=3.2, mfc='none', mew=0.9, label=f'HS breaches ({I_h.sum()})')
    ax.plot(t[I_f], L[I_f] + 0.0, 'x', color=Navy, ms=3.2, mew=0.9, label=f'Filtered breaches ({I_f.sum()})')
    ax.set_xlim(0, T)
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Loss (%)')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch8_sem_primer_hits', 'full')
    return dict(T=T, expected=T * a, hs=int(I_h.sum()), filtered=int(I_f.sum()))


# =============================================================================
# (3) Binomial count of breaches
# =============================================================================
def fig_binomial(T=500, a0=0.01, a1=0.02):
    x = np.arange(0, 22)
    p0 = stats.binom.pmf(x, T, a0)
    p1 = stats.binom.pmf(x, T, a1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.bar(x - 0.2, p0, width=0.4, color=MainBlue, label=rf'Correct VaR: $\pi$ = {100 * a0:.0f}%')
    ax.bar(x + 0.2, p1, width=0.4, color=IDAred, alpha=0.75, label=rf'Too low VaR: $\pi$ = {100 * a1:.0f}%')
    ax.axvline(T * a0, color=MainBlue, lw=0.8, ls='--')
    ax.axvline(T * a1, color=IDAred, lw=0.8, ls='--')
    ax.text(T * a0 + 0.3, 0.172, rf'$T\pi$ = {T * a0:.0f}', color=MainBlue, fontsize=7)
    ax.text(T * a1 + 0.3, 0.172, rf'$T\pi$ = {T * a1:.0f}', color=IDAred, fontsize=7)
    ax.set_ylim(0, 0.19)
    ax.set_xlabel(f'Number of breaches $X$ in $T$ = {T} days')
    ax.set_ylabel('$P(X = x)$')
    ax.set_title(r'$X \sim$ Binomial$(T, \pi)$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch8_sem_primer_binomial')
    overlap = float(stats.binom.cdf(int(T * a1) - 1, T, a0))
    return dict(mean0=T * a0, sd0=float(np.sqrt(T * a0 * (1 - a0))), mean1=T * a1)


# =============================================================================
# (4) Kupiec LR as a function of the observed rate; size and power
# =============================================================================
def lr_uc(ph, T, a):
    ph = np.clip(ph, 1e-12, 1 - 1e-12)
    return 2 * T * (ph * np.log(ph / a) + (1 - ph) * np.log((1 - ph) / (1 - a)))


def fig_lr(T=1000, a=0.01, lam=4.0):
    ph = np.linspace(0.0005, 0.03, 400)
    lr = lr_uc(ph, T, a)
    crit = stats.chi2.ppf(0.95, 1)
    acc = ph[lr <= crit]
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 1.3))
    ax = axes[0]
    ax.axvspan(100 * acc.min(), 100 * acc.max(), color=BandBlue, alpha=0.8, lw=0, label='Not rejected at 5%')
    ax.plot(100 * ph, lr, color=MainBlue, lw=1.2, label=r'$\mathrm{LR}_{uc}(\hat\pi)$')
    ax.axhline(crit, color=IDAred, lw=0.9, ls='--', label='Critical value 3.84')
    ax.axvline(100 * a, color=Navy, lw=0.7, ls=':')
    ax.set_ylim(0, 20)
    ax.set_xlabel(r'Observed breach rate $\hat\pi$ (%)')
    ax.set_ylabel(r'$\mathrm{LR}_{uc}$')
    ax.set_title(rf'$T$ = {T}, $\alpha$ = {100 * a:.0f}%', loc='left')
    ax = axes[1]
    x = np.linspace(0.02, 16, 600)
    f0 = stats.chi2.pdf(x, 1)
    f1 = stats.ncx2.pdf(x, 1, lam)
    ax.plot(x, f0, color=MainBlue, lw=1.2, label=r'$H_0$: $\chi^2_1$')
    ax.plot(x, f1, color=Forest, lw=1.2, label=rf'$H_1$: $\chi^2_1(\lambda)$, $\lambda$ = {lam:.0f}')
    xs = x[x >= crit]
    ax.fill_between(xs, stats.chi2.pdf(xs, 1), color=IDAred, alpha=0.55, lw=0, label='Size (5%)')
    ax.fill_between(xs, stats.ncx2.pdf(xs, 1, lam), color=Forest, alpha=0.25, lw=0,
                    label=f'Power ({100 * stats.ncx2.sf(crit, 1, lam):.0f}%)')
    ax.axvline(crit, color=IDAred, lw=0.9, ls='--')
    ax.set_ylim(0, 0.6)
    ax.set_xlabel('Value of the statistic')
    ax.set_ylabel('Density')
    ax.set_title('Rejection region $> 3.84$', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch8_sem_primer_lr', 'full')
    return dict(acc_lo=float(acc.min()), acc_hi=float(acc.max()), power=float(stats.ncx2.sf(crit, 1, lam)))


# =============================================================================
# (5) independent and clustered breach sequences
# =============================================================================
def markov_hits(T, p01, p11, rng):
    h = np.zeros(T, int)
    for t in range(1, T):
        h[t] = rng.random() < (p11 if h[t - 1] else p01)
    return h


def counts(h):
    a, b = h[:-1], h[1:]
    n = {k: int(np.sum((a == i) & (b == j))) for k, (i, j) in
         dict(n00=(0, 0), n01=(0, 1), n10=(1, 0), n11=(1, 1)).items()}
    p01 = n['n01'] / (n['n00'] + n['n01'])
    p11 = n['n11'] / max(n['n10'] + n['n11'], 1)
    return p01, p11


def fig_markov(seed=32, T=1000):
    rng = np.random.default_rng(seed)
    h_ind = (rng.random(T) < 0.02).astype(int)
    h_cl = markov_hits(T, 0.012, 0.40, rng)
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 1.45), sharex=True)
    for ax, h, col, lab in ((axes[0], h_ind, MainBlue, 'Independent breaches'),
                            (axes[1], h_cl, IDAred, 'Clustered breaches (Markov chain)')):
        p01, p11 = counts(h)
        pos = np.flatnonzero(h)
        ax.vlines(pos, 0, 1, color=col, lw=0.9)
        ax.set_yticks([])
        ax.set_ylim(0, 1.05)
        ax.text(1.0, 1.08, rf'{lab}: {h.sum()} breaches, $\hat\pi_{{01}}$ = {p01:.3f}, $\hat\pi_{{11}}$ = {p11:.2f}',
                transform=ax.transAxes, ha='right', va='bottom', fontsize=7, color=col)
    axes[1].set_xlim(0, T)
    axes[1].set_xlabel('Day $t$ (a vertical line marks $I_t = 1$)')
    fig.tight_layout(pad=0.3, h_pad=0.9)
    save_fig(fig, 'ch8_sem_primer_markov', 'full')
    return dict(ind=counts(h_ind), cl=counts(h_cl), n_ind=int(h_ind.sum()), n_cl=int(h_cl.sum()))


# =============================================================================
# (6) survival functions of durations: memoryless and clustered
# =============================================================================
def fig_durations(a=0.02, b=0.6):
    d = np.arange(1, 301)
    S_geo = (1 - a) ** d
    # Weibull with the same mean 1/a: mean = Gamma(1 + 1/b) / lam
    from scipy.special import gamma
    lam = gamma(1 + 1 / b) * a
    S_w = np.exp(-(lam * d) ** b)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(d, S_geo, color=MainBlue, lw=1.3, label=rf'Geometric ($b$ = 1), mean {1 / a:.0f} days')
    ax.plot(d, S_w, color=IDAred, lw=1.3, ls='--', label=rf'Weibull $b$ = {b}, same mean')
    ax.set_yscale('log')
    ax.set_ylim(1e-3, 1.1)
    ax.set_xlim(0, 300)
    ax.annotate('many short gaps', xy=(8, S_w[7]), xytext=(45, 0.5), fontsize=7, color=IDAred,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.7))
    ax.annotate('and some very long ones', xy=(250, S_w[249]), xytext=(95, 0.006), fontsize=7, color=IDAred,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.7))
    ax.set_xlabel('Duration $d$ between breaches (days)')
    ax.set_ylabel('$S(d) = P(D > d)$, log scale')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch8_sem_primer_durations')
    return dict(lam=float(lam))


# =============================================================================
# (7) null distribution of Z2 for a correct (VaR, ES) forecast
# =============================================================================
def z2_null(T, a, nu, reps, rng):
    d = unit_t(nu)
    var = d.ppf(1 - a)
    es = t_es(nu, a)
    L = d.rvs(size=(reps, T), random_state=rng)
    return 1 - (L * (L > var)).sum(axis=1) / (es * T * a)


def fig_z2(a=0.025, nu=5, reps=20000, seed=1):
    rng = np.random.default_rng(seed)
    fig, ax = plt.subplots(figsize=(2.55, 1.75))
    out = {}
    bins = np.linspace(-2.2, 1.05, 80)
    for T, col in ((250, IDAred), (1000, MainBlue)):
        z = z2_null(T, a, nu, reps, rng)
        q5 = np.quantile(z, 0.05)
        out[T] = dict(mean=float(z.mean()), q5=float(q5))
        ax.hist(z, bins=bins, density=True, color=col, alpha=0.45, lw=0, label=rf'$T$ = {T}')
        ax.axvline(q5, color=col, lw=1.0, ls='--', label=f'5% quantile: ' + f'{q5:.2f}'.replace('-', '\u2212'))
    ax.axvline(0, color=Navy, lw=0.8, ls=':')
    ax.text(0.33, 1.8, '$E[Z_2] = 0$', fontsize=7, color=Navy)
    ax.set_xlim(-2.2, 1.05)
    ax.set_xlabel('$Z_2$ under a correct forecast')
    ax.set_ylabel('Density')
    ax.set_title(rf'i.i.d. Student-$t_{nu}$ losses, $\alpha$ = 2.5%', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch8_sem_primer_z2')
    return out


# =============================================================================
# (8) consistent scores: expected pinball loss and expected FZ0 loss
# =============================================================================
def fig_scores(nu=4, n=400000, seed=2):
    rng = np.random.default_rng(seed)
    d = unit_t(nu)
    L = d.rvs(size=n, random_state=rng)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    v = np.linspace(1.0, 5.0, 161)
    out = {}
    for a, col in ((0.01, MainBlue), (0.025, Forest)):
        S = np.array([np.mean(((L > vv) - a) * (L - vv)) for vv in v])
        q = d.ppf(1 - a)
        out[a] = float(q)
        ax.plot(v, S, color=col, lw=1.2, label=rf'Pinball, $\alpha$ = {100 * a:g}%')
        ax.plot(q, np.mean(((L > q) - a) * (L - q)), 'o', color=col, ms=4)
    ax.set_xlabel('VaR forecast $v$ (%)')
    ax.set_ylabel('Mean score')
    ax.set_title('Minimum at the true VaR (dots)', loc='left')
    ax = axes[1]
    a = 0.025
    vt = d.ppf(1 - a)
    et = t_es(nu, a)
    e = np.linspace(1.6, 6.0, 161)
    for vv, col, lab in ((vt, IDAred, 'true VaR'), (0.8 * vt, Amber, '0.8 x true VaR')):
        tail = np.mean((L > vv) * (L - vv))
        F = tail / (a * e) + vv / e + np.log(e) - 1
        ax.plot(e, F, color=col, lw=1.2, label=f'FZ0, $v$ = {lab}')
    ax.axvline(et, color=IDAred, lw=0.8, ls='--', label=f'true ES = {et:.2f}')
    ax.set_xlabel('ES forecast $e$ (%)')
    ax.set_ylabel('Mean score')
    ax.set_title(r'FZ0, $\alpha$ = 2.5%', loc='left')
    bottom_legend(fig, axes, ncol=5)
    save_fig(fig, 'ch8_sem_primer_scores', 'full')
    return dict(var=out, es=float(et))


# =============================================================================
# (9) Diebold--Mariano: autocorrelated score differences, naive and HAC intervals
# =============================================================================
def nw_lrv(d, q):
    d = d - d.mean()
    T = len(d)
    g = [np.dot(d[k:], d[:T - k]) / T for k in range(q + 1)]
    return g[0] + 2 * sum((1 - k / (q + 1)) * g[k] for k in range(1, q + 1)), g


def fig_dm(seed=4, T=1000, phi=0.6, mu=0.17):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(T + 200)
    x = np.zeros(T + 200)
    for t in range(1, T + 200):
        x[t] = phi * x[t - 1] + e[t]
    d = mu + x[200:]
    q = int(np.floor(4 * (T / 100) ** (2 / 9)))
    lrv, g = nw_lrv(d, q)
    acf = np.array(g) / g[0]
    dbar = d.mean()
    se_n = np.sqrt(g[0] / T)
    se_h = np.sqrt(lrv / T)
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 1.35), gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax = axes[0]
    k = np.arange(1, q + 1)
    ax.bar(k, acf[1:], width=0.55, color=MainBlue, label=r'ACF of $d_t$ at lag $k$')
    ax.axhline(1.96 / np.sqrt(T), color=IDAred, lw=0.8, ls='--', label=r'$\pm 1.96/\sqrt{T}$')
    ax.axhline(-1.96 / np.sqrt(T), color=IDAred, lw=0.8, ls='--')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Lag $k$')
    ax.set_ylabel('Autocorrelation')
    ax.set_title(rf'AR(1) score differences, $T$ = {T}, $q$ = {q}', loc='left')
    ax = axes[1]
    for y, se, col, lab in ((1, se_n, Amber, 'Naive: $\\sqrt{\\gamma_0/T}$'),
                            (0, se_h, Forest, 'HAC: $\\sqrt{\\widehat{\\mathrm{LRV}}/T}$')):
        ax.errorbar(dbar, y, xerr=1.96 * se, fmt='o', color=col, ms=4, capsize=3, lw=1.3, label=lab)
    ax.axvline(0, color=IDAred, lw=0.9, ls='--', label='$H_0$: $E[d_t] = 0$')
    ax.set_ylim(-0.7, 1.7)
    ax.set_yticks([])
    ax.set_xlabel(r'95% interval for $\bar d$')
    ax.set_title(f'DM = {dbar / se_h:.2f}, naive $t$ = {dbar / se_n:.2f}', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch8_sem_primer_dm', 'full')
    return dict(q=q, dbar=float(dbar), se_n=float(se_n), se_h=float(se_h), ratio=float(lrv / g[0]),
                dm=float(dbar / se_h), t_naive=float(dbar / se_n))


# =============================================================================
# (10) split conformal VaR: calibration scores and the k-th order statistic
# =============================================================================
def fig_conformal(seed=6, n=250, a=0.05, nu=5):
    rng = np.random.default_rng(seed)
    s = unit_t(nu).rvs(size=n, random_state=rng)          # scores s_j = L_j / sigma_j
    k = int(np.ceil((n + 1) * (1 - a)))
    ss = np.sort(s)
    sk = ss[k - 1]
    fig, ax = plt.subplots(figsize=(2.55, 1.65))
    bins = np.linspace(-4, 5, 37)
    sc = np.clip(s, -3.99, 4.99)
    ax.hist(sc[s <= sk], bins=bins, color=MainBlue, alpha=0.8, lw=0, label=f'Scores $s_j \\leq s_{{(k)}}$ ({k} of {n})')
    ax.hist(sc[s > sk], bins=bins, color=IDAred, alpha=0.8, lw=0, label=f'Scores above $s_{{(k)}}$ ({n - k})')
    ax.axvline(sk, color=IDAred, lw=1.1, ls='--', label=rf'$s_{{(k)}}$ = {sk:.2f}, $k = \lceil (n+1)(1-\alpha) \rceil$ = {k}')
    ax.set_xlim(-4, 5)
    ax.set_xlabel('Standardised loss $s_j = L_j/\\hat\\sigma_j$')
    ax.set_ylabel('Count')
    ax.set_title(rf'VaR {100 * a:.0f}%, $n$ = {n}: $\mathrm{{VaR}}_t = \hat\sigma_t\, s_{{(k)}}$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch8_sem_primer_conformal')
    return dict(k=k, sk=float(sk), above=int(n - k))


def run_all():
    res = {}
    res['var_es'] = fig_var_es()
    res['hits'] = fig_hits()
    res['binomial'] = fig_binomial()
    res['lr'] = fig_lr()
    res['markov'] = fig_markov()
    res['durations'] = fig_durations()
    res['z2'] = fig_z2()
    res['scores'] = fig_scores()
    res['dm'] = fig_dm()
    res['conformal'] = fig_conformal()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())
    print('scale on the slide:', SCALES)

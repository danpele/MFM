"""
seminar6_explainers.py -- Explanatory (primer) charts for Seminar 6 (MFM): multivariate volatility and dependence
================================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 6, which takes
place BEFORE Lecture 6. All charts use SIMULATED data only (fixed seeds): they illustrate the concepts (Sklar's
theorem and pseudo-observations, rank correlations, copula families, tail dependence, the Rosenblatt transform,
the parametric bootstrap p-value, GARCH filtering, DCC dynamics, the Forbes--Rigobon bias, the Fisher z
transform, the stationary bootstrap, attainable correlations, the fluctuation test) and contain no exercise answers.

Output: charts/ch6_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom), drawn at the
size of their box on the slide (1 pt in the figure = 1 pt on the slide, text >= 7 pt).

Run:  python3 Quantlets/Ch_06/seminar6_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
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
    """Legend outside the plot, centred below the figure (after tight_layout)."""
    if handles is None:
        handles, labels = [], []
        for ax in np.atleast_1d(axes).ravel():
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels and not l.startswith('_'):
                    handles.append(h); labels.append(l)
    fig.tight_layout(pad=0.3, w_pad=1.0)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


# =============================================================================
# copula samplers (simulation only)
# =============================================================================
def r_gauss(n, rho, rng):
    z = rng.standard_normal((n, 2))
    z[:, 1] = rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]
    return stats.norm.cdf(z)


def r_t(n, rho, nu, rng):
    z = rng.standard_normal((n, 2))
    z[:, 1] = rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]
    w = np.sqrt(nu / rng.chisquare(nu, n))[:, None]
    return stats.t.cdf(z * w, nu)


def r_clayton(n, theta, rng):
    v = rng.gamma(1 / theta, 1.0, n)[:, None]
    e = rng.exponential(1.0, (n, 2))
    return (1 + e / v) ** (-1 / theta)


def r_gumbel(n, theta, rng):
    a = 1 / theta                                  # positive stable with Laplace transform exp(-s^a) (Kanter)
    u = rng.uniform(0, np.pi, n)
    w = rng.exponential(1.0, n)
    s = (np.sin(a * u) / np.sin(u) ** (1 / a)) * (np.sin((1 - a) * u) / w) ** ((1 - a) / a)
    e = rng.exponential(1.0, (n, 2))
    return np.exp(-(e / s[:, None]) ** (1 / theta))


def pseudo(x):
    n = len(x)
    return np.column_stack([stats.rankdata(x[:, j]) / (n + 1) for j in range(x.shape[1])])


def corner_box(ax, q=0.05, both=True):
    ax.add_patch(Rectangle((0, 0), q * 2, q * 2, fill=False, ec=IDAred, lw=0.8))
    if both:
        ax.add_patch(Rectangle((1 - 2 * q, 1 - 2 * q), 2 * q, 2 * q, fill=False, ec=Forest, lw=0.8))


# =============================================================================
# (1) Sklar: returns with heavy-tailed margins, and their pseudo-observations
# =============================================================================
def fig_sklar(n=1000, rho=0.6, nu_m=4, seed=61):
    rng = np.random.default_rng(seed)
    uv = r_gauss(n, rho, rng)
    x = stats.t.ppf(uv, nu_m) * np.sqrt((nu_m - 2) / nu_m)     # unit-variance Student-t margins
    u = pseudo(x)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(x[:, 0], x[:, 1], 'o', ms=1.6, mfc='none', mew=0.4, color=MainBlue, label='simulated pairs')
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6)
    ax.set_xlabel('$x_1$ (Student-$t$ margin, axes cut at $\\pm 6$)')
    ax.set_ylabel('$x_2$')
    ax.set_title(r'Returns $(x_{1i}, x_{2i})$: margins + dependence', loc='left')
    ax = axes[1]
    ax.plot(u[:, 0], u[:, 1], 'o', ms=1.6, mfc='none', mew=0.4, color=MainBlue)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
    corner_box(ax)
    ax.set_xlabel(r'$\hat u_i = \mathrm{rank}(x_{1i})/(n+1)$')
    ax.set_ylabel(r'$\hat v_i$')
    ax.set_title('Pseudo-observations: copula only', loc='left')
    handles = [Line2D([], [], color=MainBlue, marker='o', ls='', mfc='none', ms=3),
               Line2D([], [], color=IDAred, lw=1), Line2D([], [], color=Forest, lw=1)]
    bottom_legend(fig, ncol=3, handles=handles,
                  labels=[f'{n} simulated pairs', 'lower-tail corner (joint lows)', 'upper-tail corner (joint highs)'])
    save_fig(fig, 'ch6_sem_primer_sklar')
    return dict(pearson=float(np.corrcoef(x.T)[0, 1]), tau=float(stats.kendalltau(x[:, 0], x[:, 1])[0]))


# =============================================================================
# (2) rank measures are invariant to increasing transforms, Pearson is not
# =============================================================================
def fig_rank_invariance(n=1000, rho=0.7, s=1.5, seed=62):
    rng = np.random.default_rng(seed)
    z = stats.norm.ppf(r_gauss(n, rho, rng))
    y = np.exp(s * z)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    out = {}
    for ax, d, ttl, col in ((axes[0], z, r'Normal pair $(Z_1, Z_2)$', MainBlue),
                            (axes[1], y, rf'Lognormal pair $(e^{{{s}Z_1}}, e^{{{s}Z_2}})$', IDAred)):
        p = np.corrcoef(d.T)[0, 1]
        t = stats.kendalltau(d[:, 0], d[:, 1])[0]
        sp = stats.spearmanr(d[:, 0], d[:, 1])[0]
        ax.plot(d[:, 0], d[:, 1], 'o', ms=1.6, mfc='none', mew=0.4, color=col)
        ax.text(0.97, 0.04, f'Pearson {p:.2f}\nKendall $\\tau$ {t:.2f}\nSpearman $\\rho_S$ {sp:.2f}',
                transform=ax.transAxes, va='bottom', ha='right', fontsize=7.2, color=Navy)
        ax.set_title(ttl, loc='left')
        out[ttl] = (p, t, sp)
    axes[1].set_xscale('log'); axes[1].set_yscale('log')
    axes[0].set_xlabel('$Z_1$'); axes[0].set_ylabel('$Z_2$')
    axes[1].set_xlabel('$X_1$ (log scale)'); axes[1].set_ylabel('$X_2$ (log scale)')
    fig.tight_layout(pad=0.3, w_pad=1.0)
    save_fig(fig, 'ch6_sem_primer_rank_invariance')
    return out


# =============================================================================
# (3) four copula families with the same Kendall tau
# =============================================================================
def fig_families(n=1500, tau=0.5, nu=3, seed=63):
    rng = np.random.default_rng(seed)
    rho = np.sin(np.pi * tau / 2)
    samples = [('Gaussian', r_gauss(n, rho, rng)), (f'Student $t$, $\\nu$ = {nu}', r_t(n, rho, nu, rng)),
               ('Clayton', r_clayton(n, 2 * tau / (1 - tau), rng)), ('Gumbel', r_gumbel(n, 1 / (1 - tau), rng))]
    fig, axes = plt.subplots(1, 4, figsize=(5.55, 1.40))
    out = {}
    for ax, (ttl, uv) in zip(axes, samples):
        ax.plot(uv[:, 0], uv[:, 1], 'o', ms=1.0, mfc='none', mew=0.3, color=MainBlue)
        corner_box(ax)
        lo = np.mean((uv[:, 0] <= 0.1) & (uv[:, 1] <= 0.1)) / 0.1
        hi = np.mean((uv[:, 0] > 0.9) & (uv[:, 1] > 0.9)) / 0.1
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
        ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
        ax.set_xticklabels(['0', '0.5', '1']); ax.set_yticklabels(['0', '0.5', '1'])
        ax.set_title(ttl, loc='left')
        ax.set_xlabel('$u$')
        out[ttl] = (float(stats.kendalltau(uv[:, 0], uv[:, 1])[0]), lo, hi)
    axes[0].set_ylabel('$v$')
    handles = [Line2D([], [], color=IDAred, lw=1), Line2D([], [], color=Forest, lw=1)]
    bottom_legend(fig, ncol=2, handles=handles,
                  labels=['corner $u, v \\leq 0.1$ (joint lows)', 'corner $u, v > 0.9$ (joint highs)'])
    save_fig(fig, 'ch6_sem_primer_families')
    return out


# =============================================================================
# (4) tail probability C(q,q)/q against q, and the t-copula limit as a function of rho
# =============================================================================
def lam_t(rho, nu):
    return 2 * stats.t.cdf(-np.sqrt((nu + 1) * (1 - rho) / (1 + rho)), nu + 1)


def fig_tail_q(tau=0.5, nu=4):
    rho = np.sin(np.pi * tau / 2)
    qs = np.geomspace(1e-3, 0.2, 40)
    th_c, th_g = 2 * tau / (1 - tau), 1 / (1 - tau)
    mvn = stats.multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])
    mvt = stats.multivariate_t(loc=[0, 0], shape=[[1, rho], [rho, 1]], df=nu)
    g = np.array([mvn.cdf([stats.norm.ppf(q)] * 2) / q for q in qs])
    t = np.array([mvt.cdf([stats.t.ppf(q, nu)] * 2, random_state=np.random.default_rng(1)) / q for q in qs])
    c = (2 * qs ** (-th_c) - 1) ** (-1 / th_c) / qs
    gu = qs ** (2 ** (1 / th_g)) / qs                       # Gumbel, lower corner
    fig, axes = plt.subplots(1, 2, figsize=(5.55, 1.40))
    ax = axes[0]
    for y, col, lab, lim in ((c, Forest, 'Clayton', 2 ** (-1 / th_c)), (t, IDAred, f'$t$, $\\nu$ = {nu}', lam_t(rho, nu)),
                             (g, MainBlue, 'Gaussian', 0.0), (gu, Amber, 'Gumbel (lower corner)', 0.0)):
        ax.plot(qs, y, color=col, lw=1.3, label=lab)
        if lim > 0:
            ax.axhline(lim, color=col, lw=0.7, ls=':')
    ax.set_xscale('log'); ax.set_ylim(0, 1)
    ax.set_xlabel('Tail probability $q$ (log scale)')
    ax.set_ylabel('$C(q,q)/q$')
    ax.set_title(rf'Same $\tau$ = {tau}: $P(V \leq q \mid U \leq q)$', loc='left')
    ax.text(1.1e-3, 0.88, 'dotted: limit $\\lambda_L$ as $q \\to 0$', fontsize=7.0, color=Navy)
    ax = axes[1]
    r = np.linspace(-0.5, 0.99, 200)
    for nn, col in ((2, IDAred), (4, Amber), (10, Forest), (30, MainBlue)):
        ax.plot(r, lam_t(r, nn), color=col, lw=1.3, label=f'$\\nu$ = {nn}')
    ax.legend(loc='upper left', frameon=False, fontsize=7.0, handlelength=1.2)
    ax.set_xlabel(r'Copula correlation $\rho$')
    ax.set_ylabel(r'$\lambda_L = \lambda_U$')
    ax.set_title(r'$t$ copula: $2\,t_{\nu+1}(-\sqrt{(\nu+1)(1-\rho)/(1+\rho)})$', loc='left')
    ax.set_ylim(0, 1)
    bottom_legend(fig, axes[0], ncol=4)
    save_fig(fig, 'ch6_sem_primer_tail_q')
    return dict(rho=rho, g001=float(g[0]), t001=float(t[0]), c_lim=2 ** (-1 / th_c), t_lim=float(lam_t(rho, nu)))


# =============================================================================
# (5) Rosenblatt transform: right copula -> independent uniforms; wrong copula -> structure left
# =============================================================================
def fig_rosenblatt(n=2000, rho=0.5, nu=2, seed=65):
    rng = np.random.default_rng(seed)
    uv = pseudo(r_t(n, rho, nu, rng))
    x, y = stats.t.ppf(uv[:, 0], nu), stats.t.ppf(uv[:, 1], nu)
    e2_t = stats.t.cdf((y - rho * x) / np.sqrt((nu + x ** 2) * (1 - rho ** 2) / (nu + 1)), nu + 1)
    rg = np.sin(np.pi * stats.kendalltau(uv[:, 0], uv[:, 1])[0] / 2)
    a, b = stats.norm.ppf(uv[:, 0]), stats.norm.ppf(uv[:, 1])
    e2_g = stats.norm.cdf((b - rg * a) / np.sqrt(1 - rg ** 2))
    fig, axes = plt.subplots(1, 2, figsize=(5.55, 1.62))
    out = {}
    for ax, e2, ttl, col in ((axes[0], e2_t, 'Fitted copula = true ($t$)', Forest),
                             (axes[1], e2_g, 'Fitted copula wrong (Gaussian)', IDAred)):
        ax.plot(uv[:, 0], e2, 'o', ms=1.0, mfc='none', mew=0.3, color=col)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
        ax.set_title(ttl, loc='left')
        ax.set_xlabel(r'$e_{1i} = \hat u_i$')
        # Cramer-von Mises distance between the empirical copula of (e1, e2) and independence
        e = np.column_stack([uv[:, 0], e2])
        D = np.array([np.mean((e[:, 0] <= e[i, 0]) & (e[:, 1] <= e[i, 1])) for i in range(n)])
        S = float(np.sum((D - e[:, 0] * e[:, 1]) ** 2))
        ax.text(1.04, 0.02, f'$S_n$ = {S:.2f}', transform=ax.transAxes, fontsize=7.2, color=col)
        out[ttl] = S
        corner_box(ax, 0.05)
    axes[0].set_ylabel(r'$e_{2i} = \hat C(\hat v_i \mid \hat u_i)$')
    fig.tight_layout(pad=0.3, w_pad=4.0)
    save_fig(fig, 'ch6_sem_primer_rosenblatt')
    return out


# =============================================================================
# (6) parametric bootstrap p-value of a likelihood ratio with the null on the boundary
# =============================================================================
def fig_boot_p(B=499, seed=66, S_obs=3.4):
    rng = np.random.default_rng(seed)
    S = np.where(rng.uniform(size=B) < 0.5, 0.0, rng.chisquare(1, B))      # 1/2 chi2_0 + 1/2 chi2_1 (illustration)
    n_ge = int(np.sum(S >= S_obs))
    p = (1 + n_ge) / (B + 1)
    fig, ax = plt.subplots(figsize=HALF)
    bins = np.linspace(0, 10, 41)
    ax.hist(S[S < S_obs], bins=bins, color=BandBlue, ec=MainBlue, lw=0.4, label='$S^{(b)} < S$')
    ax.hist(S[S >= S_obs], bins=bins, color=IDAred, alpha=0.8, lw=0, label=f'$S^{{(b)}} \\geq S$: {n_ge} draws')
    xs = np.linspace(0.05, 10, 300)
    ax.plot(xs, B * 0.25 * stats.chi2.pdf(xs, 1), color=Navy, lw=1.0, ls='--', label=r'$\chi^2_1$ density (scaled)')
    ax.set_ylim(0, 40)
    ax.annotate(f'{int(np.sum(S < 0.25))} draws in the first bar\n({int(np.sum(S == 0))} with $S^{{(b)}}$ = 0)',
                xy=(0.25, 39), xytext=(4.6, 33), fontsize=7.0, color=MainBlue,
                arrowprops=dict(arrowstyle='->', color=MainBlue, lw=0.7))
    ax.axvline(S_obs, color=IDAred, lw=1.2)
    ax.text(S_obs + 0.2, 16, f'observed $S$ = {S_obs}\n$p$ = (1 + {n_ge})/{B + 1}\n   = {p:.3f}',
            fontsize=7.2, color=IDAred)
    ax.set_xlabel(r'Statistic under $H_0$, $B$ = 499 draws')
    ax.set_ylabel('Number of draws')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch6_sem_primer_boot_p')
    return dict(p=p, n_ge=n_ge, p_chi2=float(stats.chi2.sf(S_obs, 1)), share_zero=float(np.mean(S == 0)))


# =============================================================================
# (7) GARCH filtering: returns, volatility, ACF of squares before and after
# =============================================================================
def sim_garch(T, omega, a, b, rng, burn=500):
    e = rng.standard_normal(T + burn)
    r = np.empty(T + burn); s2 = np.empty(T + burn)
    s2[0] = omega / (1 - a - b)
    for t in range(T + burn):
        if t > 0:
            s2[t] = omega + a * r[t - 1] ** 2 + b * s2[t - 1]
        r[t] = np.sqrt(s2[t]) * e[t]
    return r[burn:], np.sqrt(s2[burn:])


def _acf(x, K):
    x = x - x.mean()
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, K + 1)])


def fig_garch_filter(T=2500, omega=0.02, a=0.10, b=0.88, seed=67, K=30):
    rng = np.random.default_rng(seed)
    r, s = sim_garch(T, omega, a, b, rng)
    eps = r / s
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax = axes[0]
    ax.plot(r, color=MainBlue, lw=0.35, label='return $r_t$')
    ax.plot(2 * s, color=IDAred, lw=0.8, label=r'$\pm 2\sigma_t$ (GARCH volatility)')
    ax.plot(-2 * s, color=IDAred, lw=0.8)
    ax.set_xlim(0, T); ax.set_xlabel('Day $t$')
    ax.set_title(r'$\sigma_t^2 = \omega + \alpha r_{t-1}^2 + \beta\sigma_{t-1}^2$', loc='left')
    ax = axes[1]
    lags = np.arange(1, K + 1)
    band = 1.96 / np.sqrt(T)
    ax.axhspan(-band, band, color=BandBlue, lw=0, label=r'band $\pm 1.96/\sqrt{T}$')
    ax.vlines(lags - 0.2, 0, _acf(r ** 2, K), color=MainBlue, lw=1.4, label='ACF of $r_t^2$')
    ax.vlines(lags + 0.2, 0, _acf(eps ** 2, K), color=Forest, lw=1.4, label=r'ACF of $\varepsilon_t^2$')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Lag $k$ (days)')
    ax.set_title(r'Filtering removes the clustering', loc='left')
    bottom_legend(fig, axes, ncol=5)
    save_fig(fig, 'ch6_sem_primer_garch_filter')
    return dict(acf1_r2=float(_acf(r ** 2, 1)[0]), acf1_e2=float(_acf(eps ** 2, 1)[0]))


# =============================================================================
# (8) DCC: a simulated correlation path, and the decay of a shock (half-life)
# =============================================================================
def fig_dcc(T=2500, q12=-0.3, a=0.04, b=0.95, seed=68, win=250):
    rng = np.random.default_rng(seed)
    Qbar = np.array([[1, q12], [q12, 1]])
    Q = Qbar.copy()
    eps = np.empty((T, 2)); rho = np.empty(T)
    for t in range(T):
        d = 1 / np.sqrt(np.diag(Q))
        R = Q * np.outer(d, d)
        rho[t] = R[0, 1]
        eps[t] = np.linalg.cholesky(R) @ rng.standard_normal(2)
        Q = (1 - a - b) * Qbar + a * np.outer(eps[t], eps[t]) + b * Q
    roll = np.array([np.corrcoef(eps[t - win:t].T)[0, 1] if t >= win else np.nan for t in range(T)])
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax = axes[0]
    ax.plot(rho, color=MainBlue, lw=0.7, label=r'DCC $\rho_{12,t}$')
    ax.plot(roll, color=Amber, lw=1.0, label=f'rolling {win}-day correlation')
    ax.axhline(q12, color=IDAred, lw=0.9, ls='--', label=r'target $\bar Q_{12}$')
    ax.set_xlim(0, T); ax.set_xlabel('Day $t$')
    ax.set_title(f'Simulated DCC, $a$ = {a}, $b$ = {b}', loc='left')
    ax = axes[1]
    h = np.arange(0, 121)
    for ab, col in ((0.90, Forest), (0.95, Amber), (0.985, IDAred)):
        hl = np.log(0.5) / np.log(ab)
        ax.plot(h, ab ** h, color=col, lw=1.3, label=f'$a+b$ = {ab}: {hl:.0f} days')
        ax.plot(hl, 0.5, 'o', color=col, ms=3)
    ax.legend(loc='upper right', frameon=False, fontsize=7.0, handlelength=1.2)
    ax.set_ylim(0, 1.75); ax.set_yticks([0, 0.5, 1])
    ax.axhline(0.5, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel('Days after the shock $h$')
    ax.set_ylabel('Share left')
    ax.set_title(r'$(a+b)^h$; half-life $\ln 0.5/\ln(a+b)$', loc='left')
    bottom_legend(fig, axes[0], ncol=3)
    save_fig(fig, 'ch6_sem_primer_dcc')
    return dict(rho_min=float(rho.min()), rho_max=float(rho.max()))


# =============================================================================
# (9) Forbes-Rigobon: the measured crisis correlation rises with delta for a fixed link
# =============================================================================
def fig_fr_bias():
    d = np.linspace(0, 20, 300)
    fig, ax = plt.subplots(figsize=HALF)
    for r, col in ((0.2, Forest), (0.4, MainBlue), (0.6, Amber)):
        rc = r * np.sqrt((1 + d) / (1 + d * r ** 2))
        ax.plot(d, rc, color=col, lw=1.4, label=f'_{r}')
        ax.axhline(r, color=col, lw=0.6, ls=':')
        up = r > 0.5
        xt = 8 if up else 14
        ax.text(xt, r * np.sqrt((1 + xt) / (1 + xt * r ** 2)) + (0.02 if up else -0.035), rf'$\rho$ = {r}', color=col,
                fontsize=7.2, ha='left', va='bottom' if up else 'top')
    ax.set_xlabel(r'Rise of the source variance $\delta$')
    ax.set_ylabel(r'Measured crisis correlation $\rho_c$')
    ax.set_xlim(0, 20); ax.set_ylim(0, 1.06)
    handles = [Line2D([], [], color=Navy, lw=1.4), Line2D([], [], color=Navy, lw=0.6, ls=':')]
    bottom_legend(fig, ncol=1, handles=handles,
                  labels=[r'$\rho_c = \rho\sqrt{(1+\delta)/(1+\delta\rho^2)}$', r'unchanged link $\rho$'])
    save_fig(fig, 'ch6_sem_primer_fr_bias')


# =============================================================================
# (10) Fisher z: the sampling distribution of r is skewed, artanh(r) is close to Normal
# =============================================================================
def fig_fisher_z(n=40, rho=0.7, R=20000, seed=70):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((R, n)); e = rng.standard_normal((R, n))
    y = rho * x + np.sqrt(1 - rho ** 2) * e
    xc = x - x.mean(1, keepdims=True); yc = y - y.mean(1, keepdims=True)
    r = np.sum(xc * yc, 1) / np.sqrt(np.sum(xc ** 2, 1) * np.sum(yc ** 2, 1))
    z = np.arctanh(r)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.hist(r, bins=60, density=True, color=BandBlue, ec=MainBlue, lw=0.3, label=f'{R:,} simulated samples, $n$ = {n}')
    ax.axvline(rho, color=IDAred, lw=1.0, label=rf'true $\rho$ = {rho}')
    ax.set_xlabel(r'Sample correlation $\hat\rho$')
    ax.set_ylabel('Density')
    ax.set_title(r'$\hat\rho$: skewed, bounded by 1', loc='left')
    ax = axes[1]
    ax.hist(z, bins=60, density=True, color=BandBlue, ec=MainBlue, lw=0.3)
    xs = np.linspace(z.min(), z.max(), 300)
    ax.plot(xs, stats.norm.pdf(xs, np.arctanh(rho), 1 / np.sqrt(n - 3)), color=Forest, lw=1.4,
            label=r'$N(\mathrm{artanh}\,\rho,\ 1/(n-3))$')
    ax.axvline(np.arctanh(rho), color=IDAred, lw=1.0)
    ax.set_xlabel(r'$\mathrm{artanh}\,\hat\rho = \frac{1}{2}\ln\frac{1+\hat\rho}{1-\hat\rho}$')
    ax.set_title('After the transform: close to Normal', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch6_sem_primer_fisher_z')
    return dict(skew_r=float(stats.skew(r)), skew_z=float(stats.skew(z)), sd_z=float(z.std()),
                sd_theory=1 / np.sqrt(n - 3))


# =============================================================================
# (11) stationary bootstrap: blocks of random (geometric) length glued together
# =============================================================================
def fig_stationary_bootstrap(n=60, L=8, seed=71):
    rng = np.random.default_rng(seed)
    idx, blocks = [], []
    while len(idx) < n:
        start = int(rng.integers(0, n)); length = int(rng.geometric(1 / L))
        blk = [(start + k) % n for k in range(length)]
        blocks.append(blk[: n - len(idx)]); idx += blk[: n - len(idx)]
    cols = [MainBlue, IDAred, Forest, Amber, Navy]
    nb = len(blocks)
    top = 0.75 + 0.09 * nb
    fig, ax = plt.subplots(figsize=(5.55, 1.30))
    for k in range(n):
        ax.add_patch(Rectangle((k, top), 0.92, 0.45, color=BandBlue, lw=0))
        if (k + 1) % 10 == 0 or k == 0:
            ax.text(k + 0.46, top + 0.22, f'{k + 1}', ha='center', va='center', fontsize=6.4, color=Navy)
    pos = 0
    for j, blk in enumerate(blocks):
        c = cols[j % len(cols)]
        y = top - 0.09 * (j + 1)
        runs, cur = [], [blk[0]]
        for i in blk[1:]:
            if i == cur[-1] + 1:
                cur.append(i)
            else:
                runs.append(cur); cur = [i]
        runs.append(cur)
        for rn in runs:                                   # where the block comes from (wrap-around: two pieces)
            ax.plot([rn[0] + 0.05, rn[-1] + 0.87], [y, y], color=c, lw=1.8, solid_capstyle='butt')
        ax.add_patch(Rectangle((pos, 0), len(blk) - 0.08, 0.45, color=c, alpha=0.9, lw=0))
        ax.text(pos + len(blk) / 2, 0.22, f'{blk[0] + 1}', ha='center', va='center', fontsize=6.4, color='white')
        pos += len(blk)
    ax.text(-1, top + 0.22, 'original days $1, \\dots, n$', ha='right', va='center', fontsize=7.2)
    ax.text(-1, top - 0.045 * (nb + 1), 'blocks drawn', ha='right', va='center', fontsize=7.2)
    ax.text(-1, 0.22, 'bootstrap sample', ha='right', va='center', fontsize=7.2)
    ax.set_xlim(-17, n + 0.5); ax.set_ylim(-0.05, top + 0.5)
    ax.axis('off')
    ax.set_title(f'{nb} blocks: random start, geometric length (mean {L}), wrap-around after day {n};'
                 ' number = first day', loc='left', fontsize=7.2)
    fig.tight_layout(pad=0.2)
    save_fig(fig, 'ch6_sem_primer_stationary_bootstrap')
    return dict(n_blocks=len(blocks), lengths=[len(b) for b in blocks])


# =============================================================================
# (12) Frechet-Hoeffding bounds and the attainable Pearson correlations of two lognormals
# =============================================================================
def fig_attainable(s1=0.5):
    s2 = np.linspace(0.05, 3, 300)
    den = np.sqrt((np.exp(s1 ** 2) - 1) * (np.exp(s2 ** 2) - 1))
    rmax = (np.exp(s1 * s2) - 1) / den
    rmin = (np.exp(-s1 * s2) - 1) / den
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.5]))
    ax = axes[0]
    u = np.linspace(0, 1, 50)
    ax.plot(u, u, color=Forest, lw=1.4, label=r'$M$: $V = U$ (comonotone)')
    ax.plot(u, 1 - u, color=IDAred, lw=1.4, label=r'$W$: $V = 1 - U$ (countermonotone)')
    rng = np.random.default_rng(72)
    w = rng.uniform(size=(300, 2))
    ax.plot(w[:, 0], w[:, 1], 'o', ms=1.0, mfc='none', mew=0.3, color=MainBlue, label=r'$\Pi$: independence')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
    ax.set_xlabel('$u$'); ax.set_ylabel('$v$')
    ax.set_title(r'$W \leq C \leq M$', loc='left')
    ax = axes[1]
    ax.fill_between(s2, rmin, rmax, color=BandBlue, lw=0, label='attainable Pearson correlations')
    ax.plot(s2, rmax, color=Forest, lw=1.3)
    ax.plot(s2, rmin, color=IDAred, lw=1.3)
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel(rf'$\sigma_2$ (with $\sigma_1$ = {s1})')
    ax.set_ylabel(r'$\rho(e^{\sigma_1 Z_1}, e^{\sigma_2 Z_2})$')
    ax.set_title(r'Lognormal pair: the range shrinks as $\sigma_2$ grows', loc='left')
    ax.set_ylim(-1, 1)
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch6_sem_primer_attainable')


# =============================================================================
# (13) fluctuation test of a constant correlation (Wied-Kraemer-Dehling type), simulated break
# =============================================================================
def fig_fluctuation(T=2000, r0=-0.3, r1=0.1, seed=73):
    rng = np.random.default_rng(seed)
    out = {}
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    for ax, (ttl, rr, col) in zip(axes, (('No break', np.full(T, r0), MainBlue),
                                          (f'Break at $t$ = {T // 2}', np.r_[np.full(T // 2, r0), np.full(T - T // 2, r1)],
                                           IDAred))):
        z = rng.standard_normal((T, 2))
        x = z[:, 0]; y = rr * z[:, 0] + np.sqrt(1 - rr ** 2) * z[:, 1]
        j = np.arange(20, T + 1)
        cx, cy = np.cumsum(x), np.cumsum(y)
        cxx, cyy, cxy = np.cumsum(x * x), np.cumsum(y * y), np.cumsum(x * y)
        jj = j.astype(float)
        mx, my = cx[j - 1] / jj, cy[j - 1] / jj
        rj = (cxy[j - 1] / jj - mx * my) / np.sqrt((cxx[j - 1] / jj - mx ** 2) * (cyy[j - 1] / jj - my ** 2))
        rT = rj[-1]
        D = np.sqrt(np.mean(((x - x.mean()) * (y - y.mean()) / (x.std() * y.std()) - rT) ** 2))  # simple scale
        stat = jj / (np.sqrt(T) * D) * np.abs(rj - rT)
        ax.plot(j, stat, color=col, lw=0.9)
        ax.axhline(1.358, color=Navy, lw=0.9, ls='--')
        jm = int(j[np.argmax(stat)])
        ax.plot(jm, stat.max(), 'o', color=col, ms=3.5)
        ax.text(jm, stat.max() * 1.04 + 0.05, f'max = {stat.max():.2f}', ha='right' if jm > 0.7 * T else 'center',
                fontsize=7.0, color=col)
        ax.set_title(ttl, loc='left')
        ax.set_xlabel('Sample size used $j$')
        ax.set_xlim(0, T)
        out[ttl] = (float(stat.max()), jm)
    axes[0].set_ylabel(r'$\frac{j}{\sqrt{T}\hat D}\,|\hat\rho_j - \hat\rho_T|$')
    ymax = max(a.get_ylim()[1] for a in axes)
    for a in axes:
        a.set_ylim(0, ymax * 1.1)
    handles = [Line2D([], [], color=Navy, lw=0.9, ls='--')]
    bottom_legend(fig, ncol=1, handles=handles, labels=['5% critical value 1.358 (supremum of a Brownian bridge)'])
    save_fig(fig, 'ch6_sem_primer_fluctuation')
    return out


def run_all():
    res = {}
    res['sklar'] = fig_sklar()
    res['rank'] = fig_rank_invariance()
    res['families'] = fig_families()
    res['tail_q'] = fig_tail_q()
    res['rosenblatt'] = fig_rosenblatt()
    res['boot_p'] = fig_boot_p()
    res['garch'] = fig_garch_filter()
    res['dcc'] = fig_dcc()
    fig_fr_bias()
    res['fisher'] = fig_fisher_z()
    res['sb'] = fig_stationary_bootstrap()
    fig_attainable()
    res['fluct'] = fig_fluctuation()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

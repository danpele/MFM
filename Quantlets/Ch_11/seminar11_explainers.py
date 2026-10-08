"""
seminar11_explainers.py -- Explanatory (primer) charts for Seminar 11 (MFM): continuous-time models
==================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 11,
which takes place BEFORE Lecture 11. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (Brownian motion, quadratic variation, the Itô correction, GBM, diagnostic tests, the moving-block
bootstrap, the OU process, the bias of the mean-reversion speed, Merton jumps, discretisation schemes,
likelihood ratio tests on a boundary, the CIR process) and contain no exercise answers.

Output: charts/ch11_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_11/seminar11_explainers.py

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

# fonts in pt on the slide: the figures below have the size of their box on the slide
plt.rcParams.update({'font.size': 8.2, 'axes.labelsize': 8.2, 'axes.titlesize': 8.2, 'xtick.labelsize': 7.8,
                     'ytick.labelsize': 7.8, 'legend.fontsize': 7.8, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'lines.linewidth': 1.0, 'legend.handlelength': 1.6,
                     'legend.columnspacing': 1.2})

FULL = (5.6, 1.75)    # full slide width, chart above the bullets
HALF = (2.75, 2.15)   # one column of a two-column slide
COLS = [MainBlue, IDAred, Forest, Amber, Navy]


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
    fig.tight_layout(pad=0.3)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


def acf(x, K):
    x = np.asarray(x, float) - np.mean(x)
    d = np.sum(x * x)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, K + 1)])


# =============================================================================
# 1. Brownian motion and its random-walk approximation
# =============================================================================
def fig_bm(seed=7, n_paths=5, q=252):
    rng = np.random.default_rng(seed)
    t = np.arange(q + 1) / q
    W = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(rng.standard_normal((n_paths, q)) / np.sqrt(q), 1)], 1)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.fill_between(t, -1.96 * np.sqrt(t), 1.96 * np.sqrt(t), color=BandBlue, lw=0, label=r'95% band $\pm1.96\sqrt{t}$')
    for i in range(n_paths):
        ax.plot(t, W[i], color=COLS[i], lw=0.8, label='Simulated paths of $W_t$' if i == 0 else '_')
    ax.axhline(0, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('$W_t$')
    ax.set_title(r'Brownian motion: $W_t \sim N(0, t)$', loc='left')
    # random walk with steps +-sqrt(Delta): coarse to fine
    ax = axes[1]
    rng = np.random.default_rng(seed + 1)
    fine = rng.choice([-1.0, 1.0], size=4 * q)              # one path of coin tosses on the finest grid
    for k, (m, c, lab) in enumerate([(12, Amber, r'$\Delta = 1/12$'), (52, Forest, r'$\Delta = 1/52$'),
                                     (4 * q, MainBlue, r'$\Delta = 1/1008$')]):
        dW = fine[:m] / np.sqrt(m)
        x = np.concatenate([[0], np.cumsum(dW)])
        ax.step(np.arange(m + 1) / m, x, where='post', color=c, lw=0.9 if k < 2 else 0.7,
                label=f'Steps $\\pm\\sqrt{{\\Delta}}$, {lab}')
    ax.axhline(0, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('Random walk')
    ax.set_title(r'Random walk with steps $\pm\sqrt{\Delta}$', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch11_sem_primer_bm')
    return dict(final_W=W[:, -1].round(2).tolist())


# =============================================================================
# 2. Quadratic variation: Brownian path versus a smooth path
# =============================================================================
def fig_qv(seed=3, N=2 ** 14):
    rng = np.random.default_rng(seed)
    t = np.arange(N + 1) / N
    W = np.concatenate([[0], np.cumsum(rng.standard_normal(N) / np.sqrt(N))])
    g = 0.6 * np.sin(2 * np.pi * t) * t                    # a smooth (differentiable) path
    ns = 2 ** np.arange(2, 15)
    qv_w = [np.sum(np.diff(W[::N // n]) ** 2) for n in ns]
    qv_g = [np.sum(np.diff(g[::N // n]) ** 2) for n in ns]
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(t, W, color=MainBlue, lw=0.7, label='Brownian path $W_t$')
    ax.plot(t, g, color=Amber, lw=1.3, label='Smooth path $g(t)$')
    ax.set_xlabel('Time $t$')
    ax.set_ylabel('Value')
    ax.set_title('Two paths on $[0, 1]$', loc='left')
    ax = axes[1]
    ax.fill_between(ns, 1 - 1.96 * np.sqrt(2 / ns), 1 + 1.96 * np.sqrt(2 / ns), color=BandBlue, lw=0,
                    label=r'$T \pm 1.96\sqrt{2T\Delta}$')
    ax.plot(ns, qv_w, 'o-', color=MainBlue, ms=2.8, lw=0.9, label=r'$\sum_i (\Delta W_i)^2$')
    ax.plot(ns, qv_g, 's-', color=Amber, ms=2.8, lw=0.9, label=r'$\sum_i (\Delta g_i)^2$')
    ax.axhline(1, color=IDAred, lw=0.8, ls='--', label='$T = 1$')
    ax.set_xscale('log', base=2)
    ax.set_xlabel(r'Number of steps $n = T/\Delta$')
    ax.set_ylabel(r'$\sum_i (\Delta x_i)^2$')
    ax.set_title('Quadratic variation as the grid is refined', loc='left')
    ax.set_ylim(-0.05, 2.2)
    bottom_legend(fig, axes, ncol=6)
    save_fig(fig, 'ch11_sem_primer_qv')
    return dict(qv_w_finest=float(qv_w[-1]), qv_g_finest=float(qv_g[-1]), qv_w_n4=float(qv_w[0]))


# =============================================================================
# 3. The Itô correction: E[W_t^2] = t although dW has mean zero
# =============================================================================
def fig_ito_drift(seed=11, n_paths=4000, q=250):
    rng = np.random.default_rng(seed)
    t = np.arange(q + 1) / q
    W = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(rng.standard_normal((n_paths, q)) / np.sqrt(q), 1)], 1)
    Y = W ** 2
    fig, ax = plt.subplots(figsize=HALF)
    for i in range(4):
        ax.plot(t, Y[i], color=COLS[i + 1], lw=0.6, alpha=0.9, label='Paths of $W_t^2$' if i == 0 else '_')
    ax.plot(t, Y.mean(0), color=MainBlue, lw=1.6, label=f'Average of {n_paths:,} paths')
    ax.plot(t, t, color=IDAred, lw=1.0, ls='--', label=r'Itô drift: $\int_0^t 1\,\mathrm{d}s = t$')
    ax.set_xlabel('Time $t$')
    ax.set_ylabel('$W_t^2$')
    ax.set_ylim(0, 2.0)
    ax.set_title(r'$\mathrm{d}(W^2) = 2W\,\mathrm{d}W + \mathrm{d}t$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch11_sem_primer_ito_drift')
    return dict(mean_W1sq=float(Y[:, -1].mean()))


# =============================================================================
# 4. GBM: paths, mean versus median, lognormal law and the probability of a loss
# =============================================================================
def fig_gbm(seed=5, mu=0.10, sigma=0.30, T=5, q=252, n_paths=2000):
    rng = np.random.default_rng(seed)
    n = T * q
    t = np.arange(n + 1) / q
    m = mu - sigma ** 2 / 2
    lnS = np.concatenate([np.zeros((n_paths, 1)),
                          np.cumsum(m / q + sigma / np.sqrt(q) * rng.standard_normal((n_paths, n)), 1)], 1)
    S = 100 * np.exp(lnS)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    lo, hi = 100 * np.exp(m * t - 1.645 * sigma * np.sqrt(t)), 100 * np.exp(m * t + 1.645 * sigma * np.sqrt(t))
    ax.fill_between(t, lo, hi, color=BandBlue, lw=0, label='5%--95% quantiles')
    for i, c in enumerate([Forest, Amber, Navy]):
        ax.plot(t, S[i], color=c, lw=0.6, label='Simulated paths' if i == 0 else '_')
    ax.plot(t, 100 * np.exp(mu * t), color=IDAred, lw=1.3, label=r'Mean $S_0e^{\mu t}$')
    ax.plot(t, 100 * np.exp(m * t), color=MainBlue, lw=1.3, ls='--', label=r'Median $S_0e^{mt}$')
    ax.set_yscale('log')
    ax.set_yticks([25, 50, 100, 200, 400])
    ax.set_yticklabels(['25', '50', '100', '200', '400'])
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('$S_t$ (log scale)')
    ax.set_title(rf'GBM, $\mu = {mu:.0%}$, $\sigma = {sigma:.0%}$'.replace('%', r'\%'), loc='left')
    ax = axes[1]
    x = np.linspace(1, 600, 1500)
    dens = stats.lognorm(s=sigma * np.sqrt(T), scale=100 * np.exp(m * T))
    ax.plot(x, dens.pdf(x), color=MainBlue, lw=1.2, label=f'Density of $S_T$, $T = {T}$')
    xl = x[x < 100]
    ax.fill_between(xl, 0, dens.pdf(xl), color=IDAred, alpha=0.3, lw=0, label='$P(S_T < S_0)$')
    med, mean = 100 * np.exp(m * T), 100 * np.exp(mu * T)
    ax.axvline(med, color=MainBlue, ls='--', lw=0.9)
    ax.axvline(mean, color=IDAred, lw=0.9)
    ymax = dens.pdf(x).max()
    ax.text(med + 6, 1.03 * ymax, f'median {med:.0f}', ha='left', va='bottom', fontsize=7.4, color=MainBlue)
    ax.text(mean + 6, 0.90 * ymax, f'mean {mean:.0f}', ha='left', va='bottom', fontsize=7.4, color=IDAred)
    ax.set_ylim(0, 1.18 * ymax)
    ax.set_xlabel('$S_T$')
    ax.set_ylabel('Density')
    ax.set_title(r'$\ln(S_T/S_0) \sim N(mT, \sigma^2T)$', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch11_sem_primer_gbm')
    p_loss = stats.norm.cdf(-m * np.sqrt(T) / sigma)
    return dict(m=m, median=med, mean=mean, p_loss_T=p_loss, sim_p_loss=float((S[:, -1] < 100).mean()))


# =============================================================================
# 5. Diagnostics: QQ plot and ACF of |r| for i.i.d. Normal returns versus GARCH returns
# =============================================================================
def sim_garch_t(T, omega=0.02, a=0.07, b=0.90, nu=6, seed=21, burn=500):
    rng = np.random.default_rng(seed)
    z = rng.standard_t(nu, T + burn) * np.sqrt((nu - 2) / nu)
    h = np.empty(T + burn); r = np.empty(T + burn)
    h[0] = omega / (1 - a - b)
    for i in range(T + burn):
        if i:
            h[i] = omega + a * r[i - 1] ** 2 + b * h[i - 1]
        r[i] = np.sqrt(h[i]) * z[i]
    return r[burn:]


def jb(x):
    z = (x - x.mean()) / x.std()
    S, K = np.mean(z ** 3), np.mean(z ** 4)
    return len(x) / 6 * (S ** 2 + (K - 3) ** 2 / 4), S, K


def ljung_box(x, h):
    n = len(x)
    rho = acf(x, h)
    return n * (n + 2) * np.sum(rho ** 2 / (n - np.arange(1, h + 1)))


def fig_diag(T=2500, K=40, seed=28):
    r_g = sim_garch_t(T, seed=seed)
    r_n = np.random.default_rng(seed + 1).standard_normal(T) * r_g.std()
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    p = (np.arange(1, T + 1) - 0.5) / T
    q = stats.norm.ppf(p)
    for x, c, lab, mk in [(r_n, MainBlue, 'i.i.d. Normal (GBM)', 'o'), (r_g, IDAred, 'GARCH, Student-$t$ shocks', 's')]:
        ax.plot(q, np.sort((x - x.mean()) / x.std()), mk, color=c, ms=1.6, label=lab)
    ax.plot([-4, 4], [-4, 4], color=Navy, lw=0.8, ls='--', label='45-degree line')
    ax.set_xlim(-4, 4); ax.set_ylim(-7, 7)
    ax.set_xlabel('Normal quantile $\\Phi^{-1}(p_i)$')
    ax.set_ylabel('Sorted standardised return')
    ax.set_title('QQ plot', loc='left')
    ax = axes[1]
    k = np.arange(1, K + 1)
    band = 1.96 / np.sqrt(T)
    ax.fill_between(k, -band, band, color=BandBlue, lw=0, label=r'$\pm1.96/\sqrt{n}$')
    ax.bar(k - 0.2, acf(np.abs(r_n), K), width=0.4, color=MainBlue)
    ax.bar(k + 0.2, acf(np.abs(r_g), K), width=0.4, color=IDAred)
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Lag $k$ (days)')
    ax.set_ylabel(r'$\hat\rho_k$ of $|r_t|$')
    ax.set_title('Autocorrelation of absolute returns', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch11_sem_primer_diag')
    out = {}
    for nm, x in [('normal', r_n), ('garch', r_g)]:
        J, S, Kk = jb(x)
        out[nm] = dict(JB=J, S=S, K=Kk, LB20=ljung_box(np.abs(x), 20), acf1=acf(np.abs(x), 1)[0])
    return out


# =============================================================================
# 6. Moving-block bootstrap: blocks of the series glued together
# =============================================================================
def fig_blocks(seed=8, n=60, L=12):
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for i in range(1, n):                                  # a persistent series
        x[i] = 0.7 * x[i - 1] + rng.standard_normal()
    starts = np.array([31, 4, 44, 17, 26])                 # block starts (drawn at random in practice)
    cols = [MainBlue, IDAred, Forest, Amber, Navy]
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 2.0), sharex=True, gridspec_kw=dict(height_ratios=[1.6, 1]))
    ax = axes[0]
    ax.plot(np.arange(n), x, color=Navy, lw=0.7, marker='o', ms=1.6, label='Original series $x_1, \\dots, x_n$')
    lo = x.min() - 0.6
    for j, s0 in enumerate(starts):
        yb = lo - 0.95 * j
        ax.plot([s0, s0 + L - 1], [yb, yb], color=cols[j], lw=2.2, solid_capstyle='butt')
        ax.text(s0 + L - 0.4, yb, f'block {j + 1}', ha='left', va='center', fontsize=7.4, color=cols[j])
    ax.set_ylim(lo - 0.95 * len(starts), x.max() + 0.5)
    ax.set_yticks([-2, 0, 2])
    ax.set_ylabel('$x_t$')
    ax.set_title(f'Draw {len(starts)} block starts at random, blocks of $L = {L}$ consecutive observations', loc='left')
    ax = axes[1]
    for j, s0 in enumerate(starts):
        ax.plot(np.arange(j * L, (j + 1) * L), x[s0:s0 + L], color=cols[j], lw=1.0, marker='o', ms=1.6,
                label='Resampled series $x^*$, coloured by block' if j == 0 else '_')
        if j:
            ax.axvline(j * L - 0.5, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel('Position $t$')
    ax.set_ylabel('$x^*_t$')
    ax.set_title('Glue the blocks in the order drawn: the dependence inside each block is kept', loc='left')
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch11_sem_primer_blocks')
    return dict(starts=starts.tolist())


# =============================================================================
# 7. OU process: speed of mean reversion, half-life and stationary law
# =============================================================================
def fig_ou(seed=2, theta=0.04, x0=0.10, sigma=0.02, T=6, q=252):
    rng = np.random.default_rng(seed)
    n = T * q
    t = np.arange(n + 1) / q
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axes[0]
    for kap, c in [(0.3, Amber), (1.0, Forest), (3.0, MainBlue)]:
        b = np.exp(-kap / q)
        s = sigma * np.sqrt((1 - b ** 2) / (2 * kap))
        x = np.empty(n + 1); x[0] = x0
        e = rng.standard_normal(n)
        for i in range(n):
            x[i + 1] = theta + b * (x[i] - theta) + s * e[i]
        ax.plot(t, 100 * x, color=c, lw=0.6, alpha=0.8)
        ax.plot(t, 100 * (theta + (x0 - theta) * np.exp(-kap * t)), color=c, lw=1.4,
                label=f'$\\kappa = {kap:g}$, half-life {np.log(2) / kap:.2f} y')
        hl = np.log(2) / kap
        ax.plot(hl, 100 * (theta + (x0 - theta) / 2), 'o', color=c, ms=3.5)
    ax.axhline(100 * theta, color=IDAred, lw=0.8, ls='--', label=r'Long-run level $\theta$')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('$x_t$ (%)')
    ax.set_title(r'Expected path $\theta + (x_0 - \theta)e^{-\kappa t}$ and one simulated path', loc='left')
    ax = axes[1]
    xs = np.linspace(-0.02, 0.10, 400)
    for kap, c in [(0.3, Amber), (1.0, Forest), (3.0, MainBlue)]:
        sd = sigma / np.sqrt(2 * kap)
        ax.plot(100 * xs, stats.norm.pdf(xs, theta, sd) / 100, color=c, lw=1.2)
    ax.axvline(100 * theta, color=IDAred, lw=0.8, ls='--')
    ax.set_xlabel('$x$ (%)')
    ax.set_ylabel('Density')
    ax.set_title(r'Stationary law $N(\theta, \sigma^2/(2\kappa))$', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch11_sem_primer_ou')
    return dict(half_lives=[np.log(2) / k for k in (0.3, 1.0, 3.0)])


# =============================================================================
# 8. Small-sample bias of kappa-hat and the Monte Carlo null distribution
# =============================================================================
def _kappa_hat(x, dt):
    X, Y = x[:-1], x[1:]
    Xc = X - X.mean()
    b = np.sum(Xc * (Y - Y.mean())) / np.sum(Xc * Xc)
    return -np.log(b) / dt if b > 0 else np.nan


def fig_kappa_bias(seed=4, kappa=0.3, T=20, q=12, sigma=0.02, R=2000):
    rng = np.random.default_rng(seed)
    n = T * q
    dt = 1 / q
    b = np.exp(-kappa * dt)
    s = sigma * np.sqrt((1 - b ** 2) / (2 * kappa))
    est_ou, est_rw = [], []
    for _ in range(R):
        e = rng.standard_normal(n + 1)
        x = np.empty(n + 1); x[0] = sigma / np.sqrt(2 * kappa) * e[0]
        for i in range(n):
            x[i + 1] = b * x[i] + s * e[i + 1]
        est_ou.append(_kappa_hat(x, dt))
        rw = np.cumsum(sigma * np.sqrt(dt) * rng.standard_normal(n + 1))
        est_rw.append(_kappa_hat(rw, dt))
    est_ou, est_rw = np.array(est_ou), np.array(est_rw)
    est_rw = np.where(np.isnan(est_rw), 0, est_rw)
    fig, ax = plt.subplots(figsize=HALF)
    bins = np.linspace(-0.05, 1.2, 50)
    ax.hist(est_rw, bins=bins, density=True, histtype='step', color=Amber, lw=1.3,
            label=r'$\hat\kappa$ under a random walk ($\kappa = 0$)')
    ax.hist(est_ou, bins=bins, density=True, histtype='step', color=MainBlue, lw=1.3,
            label=rf'$\hat\kappa$ under OU, $\kappa = {kappa}$')
    ax.axvline(kappa, color=MainBlue, lw=1.0, ls='--', label='True $\\kappa = 0.3$')
    ax.axvline(est_ou.mean(), color=MainBlue, lw=1.4, label=f'Mean of $\\hat\\kappa$ (OU): {est_ou.mean():.2f}')
    q95 = np.quantile(est_rw, 0.95)
    ax.axvline(q95, color=IDAred, lw=1.2, label=f'95% quantile under $\\kappa = 0$: {q95:.2f}')
    ax.set_xlabel(r'$\hat\kappa = -\ln\hat b/\Delta$ (per year)')
    ax.set_ylabel('Density')
    ax.set_title(f'{R:,} samples of {T} years, monthly', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch11_sem_primer_kappa_bias')
    return dict(mean_ou=float(est_ou.mean()), bias=float(est_ou.mean() - kappa), four_over_T=4 / T,
                mean_rw=float(est_rw.mean()), q95_rw=float(q95), sd_ou=float(est_ou.std()))


# =============================================================================
# 9. Merton jump diffusion: a path with jumps and the daily density
# =============================================================================
def fig_merton(seed=6, sigma=0.15, lam=5, muJ=-0.03, sJ=0.04, T=2, q=252):
    rng = np.random.default_rng(seed)
    n = T * q
    dt = 1 / q
    t = np.arange(n + 1) / q
    z = rng.standard_normal(n)
    N = rng.poisson(lam * dt, n)
    J = np.array([rng.normal(muJ, sJ, k).sum() for k in N])
    diff = sigma * np.sqrt(dt) * z
    x_gbm = np.concatenate([[0], np.cumsum(diff)])
    x_mer = np.concatenate([[0], np.cumsum(diff + J)])
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(t, 100 * np.exp(x_gbm), color=MainBlue, lw=0.8, label='Same shocks, no jumps (GBM)')
    ax.plot(t, 100 * np.exp(x_mer), color=IDAred, lw=0.8, label='Merton: GBM plus jumps')
    idx = np.where(N > 0)[0]
    ax.plot(t[idx + 1], 100 * np.exp(x_mer[idx + 1]), 'v', color=IDAred, ms=3.5, label=f'Jump days ({len(idx)})')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('Price')
    ax.set_title(rf'$\lambda = {lam}$ a year, $\mu_J = {muJ:.0%}$, $\sigma_J = {sJ:.0%}$'.replace('%', r'\%'), loc='left')
    ax = axes[1]
    xs = np.linspace(-0.12, 0.08, 800)
    pk = stats.poisson.pmf(np.arange(8), lam * dt)
    dens = sum(pk[k] * stats.norm.pdf(xs, k * muJ, np.sqrt(sigma ** 2 * dt + k * sJ ** 2)) for k in range(8))
    var = sigma ** 2 * dt + lam * dt * (muJ ** 2 + sJ ** 2)
    mean = lam * dt * muJ
    ax.plot(100 * xs, dens, color=IDAred, lw=1.2, label='Merton mixture density')
    ax.plot(100 * xs, stats.norm.pdf(xs, mean, np.sqrt(var)), color=MainBlue, lw=1.0, ls='--',
            label='Normal, same mean and variance')
    ax.set_yscale('log')
    ax.set_ylim(1e-3, 80)
    ax.set_xlabel('Daily log return (%)')
    ax.set_ylabel('Density (log scale)')
    ax.set_title('Daily density: a Poisson mixture of Normals', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch11_sem_primer_merton')
    return dict(n_jump_days=int(len(idx)), share_jump_days=lam * dt, p0=float(pk[0]))


# =============================================================================
# 10. Euler-Maruyama and Milstein on a coarse grid against the exact GBM path
# =============================================================================
def fig_schemes(seed=9, mu=0.5, sigma=0.8, T=1.0, N=2 ** 10, m=8):
    rng = np.random.default_rng(seed)
    dWf = rng.standard_normal(N) * np.sqrt(T / N)
    Wf = np.concatenate([[0], np.cumsum(dWf)])
    tf = np.linspace(0, T, N + 1)
    exact = np.exp((mu - sigma ** 2 / 2) * tf + sigma * Wf)
    h = T / m
    dW = Wf[::N // m][1:] - Wf[::N // m][:-1]
    em, mil = [1.0], [1.0]
    for d in dW:
        em.append(em[-1] + mu * em[-1] * h + sigma * em[-1] * d)
        mil.append(mil[-1] + mu * mil[-1] * h + sigma * mil[-1] * d + 0.5 * sigma ** 2 * mil[-1] * (d ** 2 - h))
    tc = np.linspace(0, T, m + 1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(tf, exact, color=Navy, lw=0.9, label='Exact solution')
    ax.plot(tc, em, 'o-', color=IDAred, ms=3, lw=1.0, label=f'Euler--Maruyama, $\\Delta = 1/{m}$')
    ax.plot(tc, mil, 's-', color=Forest, ms=3, lw=1.0, label=f'Milstein, $\\Delta = 1/{m}$')
    ax.plot(tc, exact[::N // m], 'x', color=Navy, ms=4)
    ax.set_xlabel('Time $t$')
    ax.set_ylabel('$X_t$')
    ax.set_title(rf'GBM, $\mu = {mu}$, $\sigma = {sigma}$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch11_sem_primer_schemes')
    return dict(err_em=abs(em[-1] - exact[-1]), err_mil=abs(mil[-1] - exact[-1]))


# =============================================================================
# 11. Likelihood ratio test with a parameter on the boundary
# =============================================================================
def fig_boundary():
    x = np.linspace(0.01, 10, 600)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, stats.chi2.pdf(x, 1), color=MainBlue, lw=1.2, label=r'$\chi^2_1$: interior parameter (Wilks)')
    ax.plot(x, 0.5 * stats.chi2.pdf(x, 1), color=IDAred, lw=1.2,
            label=r'$\frac{1}{2}\chi^2_0 + \frac{1}{2}\chi^2_1$ (mass $\frac{1}{2}$ at 0): parameter on the boundary')
    ax.plot(x, stats.chi2.pdf(x, 3), color=Forest, lw=1.0, ls='--', label=r'$\chi^2_3$')
    for v, c in [(stats.chi2.ppf(0.95, 1), MainBlue), (stats.chi2.ppf(0.90, 1), IDAred), (stats.chi2.ppf(0.95, 3), Forest)]:
        ax.axvline(v, color=c, lw=0.8, ls=':')
        ax.text(v + 0.1, 0.62, f'{v:.2f}', color=c, fontsize=7.4, rotation=90, va='top')
    ax.set_ylim(0, 0.7)
    ax.set_xlabel('$LR$')
    ax.set_ylabel('Density')
    ax.set_title('Null distributions and 5% critical values', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch11_sem_primer_boundary')
    return dict(c1=stats.chi2.ppf(0.95, 1), cmix=stats.chi2.ppf(0.90, 1), c3=stats.chi2.ppf(0.95, 3))


# =============================================================================
# 12. Vasicek versus CIR near zero (Feller condition)
# =============================================================================
def fig_cir(seed=12, kappa=0.5, theta=0.03, T=10, q=252):
    rng = np.random.default_rng(seed)
    n = T * q
    dt = 1 / q
    t = np.arange(n + 1) / q
    z = rng.standard_normal(n)
    sig_v = 0.02
    fig, ax = plt.subplots(figsize=HALF)
    x = np.empty(n + 1); x[0] = theta
    for i in range(n):
        x[i + 1] = x[i] + kappa * (theta - x[i]) * dt + sig_v * np.sqrt(dt) * z[i]
    ax.plot(t, 100 * x, color=Amber, lw=0.7, label=r'Vasicek, $\sigma = 0.02$: can be negative')
    for sc, c in [(0.10, MainBlue), (0.25, IDAred)]:
        r = np.empty(n + 1); r[0] = theta
        for i in range(n):                                   # full truncation Euler, same shocks
            rp = max(r[i], 0)
            r[i + 1] = r[i] + kappa * (theta - rp) * dt + sc * np.sqrt(rp * dt) * z[i]
        feller = 2 * kappa * theta / sc ** 2
        ax.plot(t, 100 * np.maximum(r, 0), color=c, lw=0.7,
                label=f'CIR, $\\sigma = {sc}$: $2\\kappa\\theta/\\sigma^2 = {feller:.1f}$')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('Short rate (%)')
    ax.set_title(r'$\kappa = 0.5$, $\theta = 3\%$, same shocks', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch11_sem_primer_cir')
    return dict(feller=[2 * kappa * theta / s ** 2 for s in (0.10, 0.25)])


def run_all():
    res = {}
    res['bm'] = fig_bm()
    res['qv'] = fig_qv()
    res['ito_drift'] = fig_ito_drift()
    res['gbm'] = fig_gbm()
    res['diag'] = fig_diag()
    res['blocks'] = fig_blocks()
    res['ou'] = fig_ou()
    res['kappa_bias'] = fig_kappa_bias()
    res['merton'] = fig_merton()
    res['schemes'] = fig_schemes()
    res['boundary'] = fig_boundary()
    res['cir'] = fig_cir()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

"""
seminar17_explainers.py -- Explanatory (primer) charts for Seminar 17 (MFM): bubbles and crashes
================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 17, which
takes place BEFORE Lecture 17. All charts use SIMULATED data only (fixed seeds): they illustrate the concepts
(a rational bubble that bursts, stationary / unit / explosive roots, the Dickey-Fuller distribution and the right
tail, the windows of SADF and BSADF, date-stamping an episode, the wild bootstrap, a two-regime Markov-switching
model with its filtered probability, one Hamilton filter step, an LPPLS trajectory) and contain no exercise answers.

The charts are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide), so that every
text is at least 6.3 pt on the slide.

Output: charts/ch17_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_17/seminar17_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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

# drawn at slide size: the full text width of the slides is 5.67 in, half a column 2.84 in
plt.rcParams.update({'font.size': 7.2, 'axes.labelsize': 7.2, 'axes.titlesize': 7.4, 'xtick.labelsize': 6.8,
                     'ytick.labelsize': 6.8, 'legend.fontsize': 6.8, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.5,
                     'ytick.major.width': 0.5, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
                     'lines.linewidth': 1.1, 'legend.handlelength': 1.6, 'legend.columnspacing': 1.2})

FULL = (5.6, 1.62)    # full slide width, shown at height 0.55\textheight
HALF = (2.84, 2.30)   # one column of a two-column frame


def figure(size, ncols=1, **kw):
    fig, axes = plt.subplots(1, ncols, figsize=size, layout='constrained', **kw)
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02, wspace=0.06)
    return fig, axes


def legend_below(fig, handles, labels, ncol):
    fig.legend(handles, labels, loc='outside lower center', ncol=ncol, frameon=False)


def all_handles(axes):
    hs, ls = [], []
    for ax in np.atleast_1d(axes):
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in ls and not l.startswith('_'):
                hs.append(h); ls.append(l)
    return hs, ls


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), transparent=True, dpi=220)
    plt.close(fig)
    print(f'   saved {name}')


# -----------------------------------------------------------------------------
# ADF t-statistics (constant, no lags) on every window, from prefix sums
# -----------------------------------------------------------------------------
def bsadf_path(y, w0):
    """BSADF_e for every end e (in observations of the changes), and the full matrix not stored."""
    dy = np.diff(y)
    x = y[:-1]
    N = len(dy)
    c = lambda v: np.r_[0.0, np.cumsum(v)]
    Sx, Sy, Sxx, Sxy, Syy = c(x), c(dy), c(x * x), c(x * dy), c(dy * dy)
    out = np.full(N, np.nan)
    for e in range(w0 - 1, N):
        s = np.arange(0, e - w0 + 2)                 # window [s, e]
        n = e - s + 1.0
        sx, sy = Sx[e + 1] - Sx[s], Sy[e + 1] - Sy[s]
        sxx, sxy, syy = Sxx[e + 1] - Sxx[s], Sxy[e + 1] - Sxy[s], Syy[e + 1] - Syy[s]
        Cxx = sxx - sx * sx / n
        Cxy = sxy - sx * sy / n
        Cyy = syy - sy * sy / n
        b = Cxy / Cxx
        ss = np.maximum(Cyy - b * Cxy, 1e-12)
        t = b / np.sqrt(ss / (n - 2) / Cxx)
        out[e] = t.max()
    return out


def adf_t(y):
    dy = np.diff(y)
    x = y[:-1]
    X = np.column_stack([np.ones_like(x), x])
    b, res, *_ = np.linalg.lstsq(X, dy, rcond=None)
    u = dy - X @ b
    s2 = u @ u / (len(dy) - 2)
    V = s2 * np.linalg.inv(X.T @ X)
    return b[1] / np.sqrt(V[1, 1])


# =============================================================================
# (1) a rational bubble that bursts (Blanchard-Watson), on top of growing fundamentals
# =============================================================================
def fig_bubble(seed=21, n=60, r=0.06, g=0.02, pi=0.9, B0=15.0, F0=50.0):
    rng = np.random.default_rng(seed)
    t = np.arange(n + 1)
    F = F0 * (1 + g) ** t
    paths = []
    for _ in range(3):
        B = np.empty(n + 1)
        B[0] = B0
        for i in range(n):
            eps = rng.normal(0, 0.5)
            B[i + 1] = (1 + r) / pi * B[i] + eps if rng.random() < pi else 2.0 + abs(eps)
            B[i + 1] = max(B[i + 1], 0.5)
        paths.append(B)
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    cols = [IDAred, Amber, MainBlue]
    for B, c in zip(paths, cols):
        ax.plot(t, F + B, color=c, lw=0.9)
    ax.plot(t, F, color=Forest, lw=1.4, ls='--', label='fundamental value $F_t = F_0(1 + g)^t$')
    ax.plot([], [], color=IDAred, label='price $P_t = F_t + B_t$, three simulated paths')
    ax.set_xlabel('Year $t$')
    ax.set_ylabel('Price')
    ax.set_title('Bubble on top of the fundamentals', loc='left')
    ax = axes[1]
    for B, c in zip(paths, cols):
        ax.plot(t, B / (F + B), color=c, lw=0.9)
    ax.plot(t, B0 * (1 + r) ** t / (F + B0 * (1 + r) ** t), color=Navy, lw=1.2, ls=':',
            label='expected share $\\mathrm{E}B_t/(F_t + \\mathrm{E}B_t)$')
    ax.set_ylim(0, 1)
    ax.set_xlabel('Year $t$')
    ax.set_ylabel('Bubble share $B_t/P_t$')
    ax.set_title(f'Bursts with probability {1 - pi:.1f} a year', loc='left')
    h, l = all_handles(axes)
    legend_below(fig, h, l, 2)
    save_fig(fig, 'ch17_sem_primer_bubble')


# =============================================================================
# (2) stationary, unit and explosive roots
# =============================================================================
def fig_roots(seed=2, n=200):
    rng = np.random.default_rng(seed)
    e = rng.normal(0, 1, n)
    fig, ax = figure(HALF)
    for rho, c, lab in ((0.9, Forest, 'stationary, $\\rho = 0.9$'), (1.0, MainBlue, 'unit root, $\\rho = 1$'),
                        (1.02, IDAred, 'explosive, $\\rho = 1.02$')):
        y = np.zeros(n)
        y[0] = 1.0
        for t in range(1, n):
            y[t] = rho * y[t - 1] + e[t]
        ax.plot(y, color=c, lw=0.9, label=lab)
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Period $t$')
    ax.set_ylabel('$y_t$')
    ax.set_title('$y_t = \\rho\\,y_{t-1} + e_t$, same shocks $e_t$', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch17_sem_primer_roots')


# =============================================================================
# (3) the Dickey-Fuller distribution of t_b under a random walk, and the right tail
# =============================================================================
def fig_df_dist(seed=3, n=200, R=5000):
    rng = np.random.default_rng(seed)
    t = np.array([adf_t(np.cumsum(rng.normal(0, 1, n))) for _ in range(R)])
    q05, q95 = np.quantile(t, [0.05, 0.95])
    fig, ax = figure(HALF)
    ax.hist(t, bins=70, density=True, color=BandBlue, label=f'$t_b$ under a random walk ({R} paths, $T = {n}$)')
    xs = np.linspace(-5, 4, 300)
    ax.plot(xs, stats.norm.pdf(xs), color=Forest, lw=1.0, label='$N(0, 1)$: not the right reference')
    ax.axvline(q05, color=MainBlue, lw=0.9, ls='--', label=f'5% quantile {q05:.2f}: left-tailed test')
    ax.axvline(q95, color=IDAred, lw=0.9, ls='--', label=f'95% quantile {q95:.2f}: right-tailed test')
    ax.axvline(1.645, color=Amber, lw=0.9, ls=':', label='1.645: almost never exceeded')
    ax.set_xlabel('ADF statistic $t_b = \\hat b/\\mathrm{SE}(\\hat b)$')
    ax.set_ylabel('Density')
    ax.set_title('Dickey-Fuller distribution (with a constant)', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch17_sem_primer_df_dist')
    return dict(q05=q05, q95=q95, share_neg=float(np.mean(t < 0)))


# =============================================================================
# (4) the windows of SADF (fixed start) and of BSADF (fixed end)
# =============================================================================
def mix(c0, c1, a):
    from matplotlib.colors import to_rgb
    return tuple((1 - a) * x + a * y for x, y in zip(to_rgb(c0), to_rgb(c1)))


def fig_windows():
    fig, axes = figure(HALF, 2, sharey=False)
    for ax, kind in zip(axes, ('SADF', 'BSADF')):
        T, w0, e = 1.0, 0.25, 0.8
        k = 6
        for i in range(k):
            yy = k - i
            if kind == 'SADF':
                s0, s1 = 0.0, w0 + i * (T - w0) / (k - 1)
            else:
                s0, s1 = i * (e - w0) / (k - 1), e
            c0, c1 = ((BandBlue, MainBlue) if kind == 'SADF' else ('#F4C2C2', IDAred))
            ax.add_patch(Rectangle((s0, yy - 0.35), s1 - s0, 0.7, color=mix(c0, c1, i / (k - 1)), lw=0))
            ax.plot([s1], [yy], 'o' if kind == 'SADF' else 's', color=Navy, ms=2.5)
        if kind == 'BSADF':
            ax.axvline(e, color=Navy, lw=0.8, ls='--')
            ax.text(e + 0.02, 0.45, '$r_2$', color=Navy, fontsize=7)
        ax.set_xlim(0, 1.0)
        ax.set_ylim(0.3, k + 0.8)
        ax.set_yticks([])
        ax.set_xticks([0, 0.5, 1], ['0', '0.5', '1'])
        ax.set_xlabel('Fraction of the sample')
        ax.set_title('SADF: start at 0,\nend $r_2$ grows' if kind == 'SADF' else 'BSADF$_{r_2}$: end at $r_2$,\nstart $r_1$ moves',
                     loc='left')
    save_fig(fig, 'ch17_sem_primer_windows')


# =============================================================================
# (5) date-stamping a simulated bubble with BSADF and Monte Carlo critical values
# =============================================================================
def fig_bsadf(seed=7, n=300, R=300):
    rng = np.random.default_rng(seed)
    r0 = 0.01 + 1.8 / np.sqrt(n)
    w0 = int(np.floor(r0 * n))
    e = rng.normal(0, 1, n)
    y = np.zeros(n + 1)
    t1, t2 = int(0.55 * n), int(0.70 * n)
    for t in range(1, n + 1):
        if t1 <= t < t2:
            y[t] = 1.04 * y[t - 1] + e[t - 1] if y[t - 1] > 0 else y[t - 1] + 1.5 + e[t - 1]
        elif t == t2:
            y[t] = y[t1 - 5] + e[t - 1]                  # collapse back
        else:
            y[t] = y[t - 1] + e[t - 1]
    y = y - y[:t1].min() + 5
    bs = bsadf_path(y, w0)
    sims = np.array([bsadf_path(np.r_[0.0, np.cumsum(rng.normal(0, 1, n))] + 1.0 / n * np.arange(n + 1), w0)
                     for _ in range(R)])
    cv = np.nanquantile(sims, 0.95, axis=0)
    L = int(np.ceil(np.log(n)))
    above = bs > cv
    runs, i = [], w0 - 1
    while i < n:
        if above[i]:
            j = i
            while j < n and above[j]:
                j += 1
            if j - i >= L:
                runs.append((i, j - 1))
            i = j
        else:
            i += 1
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    ax.plot(np.arange(n + 1), y, color=MainBlue, lw=0.9, label='log price $y_t$')
    ax.axvspan(t1, t2, color=Amber, alpha=0.2, lw=0, label='explosive phase')
    ax.set_xlabel('Period $t$')
    ax.set_ylabel('$y_t$')
    ax.set_title('Random walk with one bubble', loc='left')
    ax = axes[1]
    tt = np.arange(1, n + 1)
    ax.plot(tt, bs, color=IDAred, lw=0.9, label='$\\mathrm{BSADF}_t$')
    ax.plot(tt, cv, color=Forest, lw=0.9, ls='--', label='95% critical value')
    for a, b in runs:
        ax.axvspan(a + 1, b + 1, color=BandBlue, lw=0, label='episode ($\\geq L$ periods above)')
    ax.set_xlabel('End of the window $t$')
    ax.set_ylabel('ADF statistic')
    ax.set_title(f'$T = {n}$, $w_0 = {w0}$, $L = {L}$', loc='left')
    h, l = all_handles(axes)
    legend_below(fig, h, l, 3)
    save_fig(fig, 'ch17_sem_primer_bsadf')
    return dict(w0=w0, L=L, runs=runs, gsadf=float(np.nanmax(bs)))


# =============================================================================
# (6) wild bootstrap: random signs keep where the large changes were
# =============================================================================
def fig_wild(seed=9, n=300):
    rng = np.random.default_rng(seed)
    sig = np.where(np.arange(n) < n // 2, 1.0, 3.0)
    dy = sig * rng.normal(0, 1, n)
    w = rng.choice([-1.0, 1.0], n)
    dy_star = w * (dy - dy.mean())
    iid = rng.choice(dy - dy.mean(), n)
    fig, axes = plt.subplots(3, 1, figsize=HALF, layout='constrained', sharex=True)
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.01, hspace=0.02)
    for ax, v, c, lab in zip(axes, (dy, dy_star, iid), (MainBlue, IDAred, Amber),
                             ('observed changes $\\Delta y_t$', 'wild: $w_t(\\Delta y_t - \\overline{\\Delta y})$, $w_t = \\pm 1$',
                              'resampled at random (iid)')):
        ax.plot(v, color=c, lw=0.6)
        ax.set_ylim(-11, 11)
        ax.set_yticks([-8, 0, 8])
        ax.text(0.01, 0.97, lab, transform=ax.transAxes, va='top', fontsize=6.8, color=c)
    axes[-1].set_xlabel('Period $t$ (volatility triples halfway)')
    save_fig(fig, 'ch17_sem_primer_wild')


# =============================================================================
# (7) two-regime Markov switching: simulated returns and the filtered probability
# =============================================================================
def hamilton_filter(r, mu, sig, P):
    n = len(r)
    xi = np.zeros((n, 2))
    pred = np.array([P[1, 0], P[0, 1]]) / (P[0, 1] + P[1, 0])     # stationary probabilities
    for t in range(n):
        f = stats.norm.pdf(r[t], mu, sig)
        post = pred * f
        xi[t] = post / post.sum()
        pred = xi[t] @ P
    return xi


def fig_ms(seed=4, n=400, mu=(0.3, -0.5), sig=(1.5, 4.0), p11=0.98, p22=0.92):
    rng = np.random.default_rng(seed)
    P = np.array([[p11, 1 - p11], [1 - p22, p22]])
    s = np.zeros(n, int)
    for t in range(1, n):
        s[t] = rng.choice(2, p=P[s[t - 1]])
    r = np.array(mu)[s] + np.array(sig)[s] * rng.normal(0, 1, n)
    xi = hamilton_filter(r, np.array(mu), np.array(sig), P)
    fig, axes = figure(FULL, 2)
    tt = np.arange(n)
    for ax in axes:
        for t0 in np.where(np.diff(np.r_[0, s, 0]) == 1)[0]:
            t1 = t0 + np.argmax(s[t0:] == 0) if (s[t0:] == 0).any() else n
            ax.axvspan(t0, t1, color=Amber, alpha=0.18, lw=0, label='true turbulent regime')
    axes[0].plot(tt, r, color=MainBlue, lw=0.6, label='weekly return $r_t$ (%)')
    axes[0].set_xlabel('Week')
    axes[0].set_ylabel('$r_t$')
    axes[0].set_title('$r_t = \\mu_{s_t} + \\sigma_{s_t}\\varepsilon_t$', loc='left')
    axes[1].plot(tt, xi[:, 1], color=IDAred, lw=0.9, label='filtered $P(s_t = 2 \\mid r_1, \\dots, r_t)$')
    axes[1].axhline(0.5, color=Navy, lw=0.6, ls=':')
    axes[1].set_ylim(-0.02, 1.02)
    axes[1].set_xlabel('Week')
    axes[1].set_ylabel('Probability')
    axes[1].set_title(f'Durations: {1 / (1 - p11):.0f} and {1 / (1 - p22):.1f} weeks', loc='left')
    h, l = all_handles(axes)
    legend_below(fig, h, l, 3)
    save_fig(fig, 'ch17_sem_primer_ms')


# =============================================================================
# (8) one filter step: the two regime densities at the observed return
# =============================================================================
def fig_filter_step(r_obs=-4.0, sig=(1.0, 3.0), prior2=0.108):
    xs = np.linspace(-10, 10, 400)
    f1, f2 = stats.norm.pdf(xs, 0, sig[0]), stats.norm.pdf(xs, 0, sig[1])
    fig, ax = figure(HALF)
    ax.plot(xs, (1 - prior2) * f1, color=MainBlue, label=f'calm: $(1 - {prior2})\\,\\varphi(r; 0, 1)$')
    ax.plot(xs, prior2 * f2, color=IDAred, label=f'turbulent: ${prior2}\\,\\varphi(r; 0, 9)$')
    a = (1 - prior2) * stats.norm.pdf(r_obs, 0, sig[0])
    b = prior2 * stats.norm.pdf(r_obs, 0, sig[1])
    ax.axvline(r_obs, color=Navy, lw=0.8, ls='--', label=f'observed $r_t = {r_obs:.0f}$')
    ax.plot([r_obs], [a], 'o', color=MainBlue, ms=3.5)
    ax.plot([r_obs], [b], 'o', color=IDAred, ms=3.5)
    ax.set_yscale('log')
    ax.set_ylim(1e-5, 1)
    ax.set_xlabel('Return $r$')
    ax.set_ylabel('Prediction $\\times$ density (log scale)')
    ax.set_title(f'Posterior turbulent: {b / (a + b):.2f}', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch17_sem_primer_filter_step')
    return dict(post=b / (a + b))


# =============================================================================
# (9) an LPPLS trajectory: power-law acceleration with log-periodic oscillations
# =============================================================================
def fig_lppls(tc=1.0, m=0.5, omega=8.0, A=1.0, B=-1.0, C1=0.08, C2=0.03):
    t = np.linspace(0.0, 0.995, 500)
    tau = tc - t
    trend = A + B * tau ** m
    lp = trend + tau ** m * (C1 * np.cos(omega * np.log(tau)) + C2 * np.sin(omega * np.log(tau)))
    fig, ax = figure(HALF)
    ax.plot(t, lp, color=IDAred, label='LPPLS: power law + log-periodic oscillations')
    ax.plot(t, trend, color=MainBlue, ls='--', label='power law $A + B(t_c - t)^m$ only')
    ax.axvline(tc, color=Navy, lw=0.8, ls=':', label='critical time $t_c$')
    ax.set_xlabel('Time $t$ (years)')
    ax.set_ylabel('$\\ln p_t$')
    ax.set_title(f'$m = {m}$, $\\omega = {omega:.0f}$, $B = {B:.0f}$, $C = {np.hypot(C1, C2):.2f}$', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch17_sem_primer_lppls')


def run_all():
    res = {}
    fig_bubble()
    fig_roots()
    res['df'] = fig_df_dist()
    fig_windows()
    res['bsadf'] = fig_bsadf()
    fig_wild()
    fig_ms()
    res['filter'] = fig_filter_step()
    fig_lppls()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

"""
seminar14_explainers.py -- Explanatory (primer) charts for Seminar 14 (MFM): deep learning and foundation models
===============================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 14,
which takes place BEFORE Lecture 14. All charts use SIMULATED data or textbook formulas only (fixed seeds,
parameters different from those of the exercises): they illustrate the concepts (vanishing gradients, the
LSTM cell state as an AR(1), Chronos mean scaling, VaR and ES from a quantile grid, the Kupiec test and its
power, clustered VaR breaches, the QLIKE loss, filtered historical simulation) and contain no exercise answers.

Output: charts/ch14_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_14/seminar14_explainers.py

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

plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'lines.linewidth': 1.0, 'legend.handlelength': 1.6,
                     'legend.columnspacing': 1.2})

HALF = (2.75, 2.1)


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
    fig.tight_layout(pad=0.3)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


# =============================================================================
# 1. vanishing and exploding gradients: |w|^k
# =============================================================================
def fig_vanishing():
    k = np.arange(0, 61)
    fig, ax = plt.subplots(figsize=HALF)
    for w, col in [(1.1, IDAred), (1.0, Navy), (0.9, MainBlue), (0.7, Forest)]:
        ax.plot(k, w ** k, color=col, lw=1.2, label=f'$w = {w}$')
    ax.set_yscale('log')
    ax.axhline(1e-2, color=Amber, lw=0.8, ls=':')
    ax.set_xlabel('Steps back $k$')
    ax.set_ylabel(r'$|\partial h_T/\partial h_{T-k}| = |w|^k$')
    ax.set_ylim(1e-9, 1e3)
    bottom_legend(fig, ax, ncol=4)
    save_fig(fig, 'ch14_sem_primer_vanishing')


# =============================================================================
# 2. the LSTM cell state with a constant forget gate: AR(1) memory
# =============================================================================
def fig_lstm():
    k = np.arange(0, 81)
    fig, ax = plt.subplots(figsize=HALF)
    for f, col in [(0.5, Forest), (0.9, MainBlue), (0.97, IDAred), (0.995, Amber)]:
        hl = np.log(0.5) / np.log(f)
        ax.plot(k, f ** k, color=col, lw=1.2, label=f'$f = {f}$, half-life {hl:.1f}')
    ax.axhline(0.5, color=Navy, lw=0.6, ls=':')
    ax.set_xlabel('Steps after a unit input $k$')
    ax.set_ylabel(r'Effect on the cell state $f^{\,k}$')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch14_sem_primer_lstm')


# =============================================================================
# 3. Chronos mean scaling: how much a crash moves the scale, by context length
# =============================================================================
def fig_tokens(seed=3, crash=-8.0):
    rng = np.random.default_rng(seed)
    r = 0.9 * rng.standard_t(4, 2048) / np.sqrt(2)
    Cs = np.array([8, 16, 32, 64, 128, 256, 512, 1024])
    ratio = []
    for C in Cs:
        ctx = r[-C:]
        s_old = np.mean(np.abs(ctx))
        s_new = s_old + (abs(crash) - abs(ctx[0])) / C
        ratio.append(s_old / s_new)
    fig, axes = plt.subplots(2, 1, figsize=(2.75, 2.6), gridspec_kw=dict(height_ratios=[1, 1]))
    ax = axes[0]
    ctx = r[-40:]
    s = np.mean(np.abs(ctx))
    ax.bar(np.arange(40), ctx / s, color=MainBlue, width=0.8, label=r'$z_t = x_t/s$, 40-day context')
    ax.axhline(0, color=Navy, lw=0.4)
    for b in np.linspace(-3, 3, 13):
        ax.axhline(b, color=BandBlue, lw=0.4, zorder=0)
    ax.set_ylabel('$z_t$')
    ax.set_xlabel('Day in the context')
    ax.set_ylim(-3.2, 3.2)
    ax = axes[1]
    ax.plot(Cs, ratio, 'o-', color=IDAred, lw=1.1, ms=3.5, label=r'Shrink factor $s_{old}/s_{new}$ after a $-8\%$ day')
    ax.set_xscale('log', base=2)
    ax.set_xticks(Cs); ax.set_xticklabels([str(c) for c in Cs])
    ax.set_xlabel('Context length $C$ (days)')
    ax.set_ylabel(r'$s_{old}/s_{new}$')
    ax.set_ylim(0, 1.05)
    bottom_legend(fig, axes, ncol=1)
    save_fig(fig, 'ch14_sem_primer_tokens')
    return dict(zip([int(c) for c in Cs], [round(x, 3) for x in ratio]))


# =============================================================================
# 4. VaR and ES from a quantile grid
# =============================================================================
def fig_quantiles(nu=4, scale=1.0):
    dist = stats.t(nu, scale=scale * np.sqrt((nu - 2) / nu))
    u = np.linspace(0.001, 0.999, 999)
    grid = np.array([0.01, 0.05] + [k / 10 for k in range(1, 10)] + [0.95, 0.99])
    qg = dist.ppf(grid)
    alpha = 0.025
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(u, dist.ppf(u), color=MainBlue, lw=1.1, label='True quantile function $q_u$')
    ax.plot(grid, qg, 'o--', color=Forest, lw=0.8, ms=3, label='Model grid, linear interpolation')
    uu = np.linspace(0.001, alpha, 100)
    ax.fill_between(uu, dist.ppf(uu), 0, color=IDAred, alpha=0.3, lw=0, label=r'Area $\int_0^{\alpha} q_u\,du$ (ES)')
    ax.axvline(alpha, color=IDAred, lw=0.8, ls=':')
    ax.plot(alpha, dist.ppf(alpha), 'o', color=IDAred, ms=4, label=r'$q_{\alpha} = -\mathrm{VaR}_{\alpha}$')
    ax.set_xlim(0, 0.2)
    ax.set_ylim(-5, 0.5)
    ax.set_xlabel('Probability level $u$')
    ax.set_ylabel(r'Return quantile $q_u$ (%)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch14_sem_primer_quantiles')
    var = -dist.ppf(alpha)
    es = -dist.expect(lambda x: x, ub=dist.ppf(alpha)) / alpha
    return dict(var=float(var), es=float(es))


# =============================================================================
# 5. Kupiec: the LR statistic and the binomial distributions of breaches
# =============================================================================
def lr_uc(x, T, a):
    p = x / T
    ll0 = (T - x) * np.log(1 - a) + x * np.log(a)
    ll1 = (T - x) * np.log(1 - p) + (x * np.log(p) if x > 0 else 0.0)
    return -2 * (ll0 - ll1)


def fig_kupiec(T=500, a=0.01, pi1=0.02):
    xs = np.arange(0, 21)
    lr = np.array([lr_uc(x, T, a) for x in xs])
    rej = lr > stats.chi2.ppf(0.95, 1)
    p0 = stats.binom.pmf(xs, T, a)
    p1 = stats.binom.pmf(xs, T, pi1)
    fig, axes = plt.subplots(2, 1, figsize=(2.75, 2.6), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.1]))
    ax = axes[0]
    ax.bar(xs, lr, color=np.where(rej, IDAred, MainBlue), width=0.7)
    ax.axhline(3.84, color=Amber, lw=1.0, ls='--', label=r'$\chi^2_1$ 5% critical value 3.84')
    ax.set_ylabel(r'$\mathrm{LR}_{uc}$')
    ax.set_ylim(0, 20)
    ax = axes[1]
    ax.bar(xs - 0.2, p0, width=0.4, color=MainBlue, label=r'Breaches if $\pi = 1\%$ ($H_0$)')
    ax.bar(xs + 0.2, p1, width=0.4, color=IDAred, label=r'Breaches if $\pi = 2\%$')
    ax.set_xlabel(f'Number of breaches $x$ in $T = {T}$ days')
    ax.set_ylabel('Probability')
    bottom_legend(fig, axes, ncol=1)
    save_fig(fig, 'ch14_sem_primer_kupiec')
    size = float(p0[rej].sum() + stats.binom.sf(xs[-1], T, a))
    power = float(p1[rej].sum() + stats.binom.sf(xs[-1], T, pi1))
    return dict(region=[int(x) for x in xs[rej]], size=size, power=power)


# =============================================================================
# 6. independent and clustered VaR breaches
# =============================================================================
def fig_christoffersen(seed=6, T=500):
    rng = np.random.default_rng(seed)
    ind = rng.random(T) < 0.02
    cl = np.zeros(T, bool)
    # clustered: calm and turbulent regimes (breaches concentrated in turbulent spells)
    state = 0
    for t in range(T):
        if rng.random() < (0.006 if state == 0 else 0.15):
            state = 1 - state
        cl[t] = rng.random() < (0.003 if state == 0 else 0.35)

    def trans(I):
        n = np.zeros((2, 2), int)
        for a, b in zip(I[:-1], I[1:]):
            n[int(a), int(b)] += 1
        return n
    fig, ax = plt.subplots(figsize=(2.75, 1.7))
    for row, (I, col, lab) in enumerate([(ind, MainBlue, 'Independent'), (cl, IDAred, 'Clustered')]):
        t = np.where(I)[0]
        n = trans(I)
        p01 = n[0, 1] / max(n[0].sum(), 1); p11 = n[1, 1] / max(n[1].sum(), 1)
        ax.vlines(t, 1 - row - 0.35, 1 - row + 0.35, color=col, lw=1.0,
                  label=f'{lab}: $x = {I.sum()}$, $\\hat\\pi_{{01}} = {p01:.3f}$, $\\hat\\pi_{{11}} = {p11:.2f}$')
    ax.set_yticks([1, 0]); ax.set_yticklabels(['Indep.', 'Clustered'])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel('Day $t$ (a mark = a VaR breach, $I_t = 1$)')
    for sp in ('left', 'right', 'top'):
        ax.spines[sp].set_visible(False)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch14_sem_primer_christoffersen')
    return dict(ind=trans(ind).tolist(), cl=trans(cl).tolist())


# =============================================================================
# 7. QLIKE and squared error
# =============================================================================
def fig_qlike():
    x = np.linspace(0.2, 3.0, 400)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, 1 / x + np.log(x) - 1, color=MainBlue, lw=1.3, label=r'QLIKE $\mathrm{RV}/\hat h - \log(\mathrm{RV}/\hat h) - 1$')
    ax.plot(x, (x - 1) ** 2 / 2, color=IDAred, lw=1.1, ls='--', label=r'Squared error $(\hat h - \mathrm{RV})^2/2$')
    ax.axvline(1, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel(r'Forecast / realised variance $\hat h/\mathrm{RV}$')
    ax.set_ylabel(r'Loss ($\mathrm{RV} = 1$)')
    ax.set_ylim(0, 2.0)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch14_sem_primer_qlike')


# =============================================================================
# 8. historical simulation and filtered historical simulation
# =============================================================================
def fig_fhs(seed=9, n=1500, W=500, a=0.01, lam=0.94):
    rng = np.random.default_rng(seed)
    om, al, be = 0.02, 0.08, 0.90
    h = np.empty(n); r = np.empty(n); h[0] = om / (1 - al - be)
    z = rng.standard_t(5, n) * np.sqrt(3 / 5)
    for t in range(n):
        if t > 0:
            h[t] = om + al * r[t - 1] ** 2 + be * h[t - 1]
        r[t] = np.sqrt(h[t]) * z[t]
    s2 = np.empty(n); s2[0] = r[:50].var()
    for t in range(1, n):
        s2[t] = lam * s2[t - 1] + (1 - lam) * r[t - 1] ** 2
    sig = np.sqrt(s2)
    hs = np.full(n, np.nan); fhs = np.full(n, np.nan)
    for t in range(W, n):
        hs[t] = -np.quantile(r[t - W:t], a)
        fhs[t] = -sig[t] * np.quantile(r[t - W:t] / sig[t - W:t], a)
    tt = np.arange(W, n)
    fig, ax = plt.subplots(figsize=(2.75, 2.2))
    ax.plot(tt, r[W:], color=BandBlue, lw=0.6, label='Return $r_t$ (%)')
    br_hs = (r[W:] < -hs[W:]).sum(); br_f = (r[W:] < -fhs[W:]).sum()
    ax.plot(tt, -hs[W:], color=Amber, lw=1.1, label=f'HS: $-$VaR 1% ({br_hs} breaches)')
    ax.plot(tt, -fhs[W:], color=IDAred, lw=0.9, label=f'FHS: $-$VaR 1% ({br_f} breaches)')
    ax.set_xlabel(f'Day $t$ (simulated; {0.01 * (n - W):.0f} breaches expected)')
    ax.set_ylabel('%')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch14_sem_primer_fhs')
    return dict(br_hs=int(br_hs), br_fhs=int(br_f))


if __name__ == '__main__':
    print('Seminar 14 primer charts')
    fig_vanishing()
    fig_lstm()
    print('   tokens', fig_tokens())
    print('   quantiles', fig_quantiles())
    print('   kupiec', fig_kupiec())
    print('   christoffersen', fig_christoffersen())
    fig_qlike()
    print('   fhs', fig_fhs())

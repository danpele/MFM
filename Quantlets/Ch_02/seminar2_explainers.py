"""
seminar2_explainers.py -- Explanatory (primer) charts for Seminar 2 (MFM): market efficiency
==========================================================================================
Teaching charts for the primer slides "Prerequisites for Today" / "Noțiuni necesare azi" of Seminar 2,
which takes place BEFORE Lecture 2. All charts use SIMULATED data only (fixed seeds): they illustrate
the concepts (the three random walks, autocorrelation bands, the variance ratio as a weighted sum,
the null distribution of z and z*, the Hurst exponent, short and long memory, DFA, the sign-flip
(wild) bootstrap, rolling estimates, multiple testing and the Kendall bias) and contain no exercise answers.

Output: charts/ch2_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_02/seminar2_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
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

# drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide): text >= 7 pt
FS = 7.5
plt.rcParams.update({'font.size': FS, 'axes.labelsize': FS, 'axes.titlesize': FS, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'lines.linewidth': 1.0, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.size': 2.5,
                     'ytick.major.size': 2.5, 'legend.handlelength': 1.8, 'legend.columnspacing': 1.2, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy})

# boxes on the slide (inches): text width 5.69 in, text height 3.03 in
FULL = (5.6, 1.3)     # full slide width
HALF = (2.8, 1.75)    # one column of a two-column frame


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
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
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


def acf(x, K):
    x = x - x.mean()
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, K + 1)])


def tau(x, K):
    """Robust variance of rho_k: sum e_t^2 e_{t-k}^2 / (sum e_t^2)^2."""
    e = x - x.mean()
    d = np.sum(e ** 2) ** 2
    return np.array([np.sum(e[k:] ** 2 * e[:-k] ** 2) / d for k in range(1, K + 1)])


def garch(T, omega=0.05, a=0.10, b=0.85, seed=11, burn=500, reps=None):
    """GARCH(1,1) with Normal shocks; reps=None -> one series, else array (reps, T)."""
    rng = np.random.default_rng(seed)
    R = 1 if reps is None else reps
    e = rng.standard_normal((R, T + burn))
    r = np.empty((R, T + burn))
    s2 = np.full(R, omega / (1 - a - b))
    for t in range(T + burn):
        r[:, t] = np.sqrt(s2) * e[:, t]
        s2 = omega + a * r[:, t] ** 2 + b * s2
    out = r[:, burn:]
    return out[0] if reps is None else out


def fgn_cov(n, H):
    k = np.arange(n)
    return 0.5 * (np.abs(k + 1) ** (2 * H) - 2 * np.abs(k) ** (2 * H) + np.abs(k - 1) ** (2 * H))


def fgn(n, H, seed):
    """Fractional Gaussian noise by Cholesky (exact, n up to a few thousand)."""
    from scipy.linalg import toeplitz, cholesky
    L = cholesky(toeplitz(fgn_cov(n, H)), lower=True)
    return L @ np.random.default_rng(seed).standard_normal(n)


# =============================================================================
# (i) RW1, RW2, RW3: three return series
# =============================================================================
def fig_rw(T=1500, seed=3):
    rng = np.random.default_rng(seed)
    r1 = rng.standard_normal(T)
    sig = np.where(np.arange(T) < T // 2, 0.7, 1.4)
    r2 = sig * rng.standard_normal(T)
    r3 = garch(T, seed=seed + 1)
    r3 = r3 / r3.std()
    fig, axes = plt.subplots(1, 3, figsize=(5.6, 1.3), sharey=True)
    for ax, x, col, tit in ((axes[0], r1, MainBlue, 'RW1: i.i.d.'), (axes[1], r2, Amber, r'RW2: $\sigma_t$ shifts'),
                            (axes[2], r3, IDAred, 'RW3: GARCH')):
        ax.plot(x, color=col, lw=0.35)
        ax.set_title(tit, loc='left')
        ax.set_xlabel('Day $t$')
        ax.set_xticks([0, 750, 1500])
    axes[0].set_ylabel(r'Shock $\varepsilon_t$')
    lim = 1.05 * max(np.abs(r1).max(), np.abs(r2).max(), np.abs(r3).max())
    axes[0].set_ylim(-lim, lim)
    fig.tight_layout()
    save_fig(fig, 'ch2_sem_primer_rw')
    return dict(rho1=[float(acf(x, 1)[0]) for x in (r1, r2, r3)],
                rho1_sq=[float(acf(x ** 2, 1)[0]) for x in (r1, r2, r3)])


# =============================================================================
# (ii) ACF with the i.i.d. band and the robust band
# =============================================================================
def fig_acf_bands(T=2500, K=20, seed=7):
    r = garch(T, a=0.12, b=0.85, seed=seed)
    rho = acf(r, K)
    tk = tau(r, K)
    lags = np.arange(1, K + 1)
    fig, ax = plt.subplots(figsize=HALF)
    b = 1.96 / np.sqrt(T)
    ax.axhspan(-b, b, color=BandBlue, alpha=0.9, lw=0, label=r'i.i.d. band $\pm 1.96/\sqrt{T}$')
    ax.plot(lags, 1.96 * np.sqrt(tk), color=IDAred, lw=1.3, ls='--', label=r'robust band $\pm 1.96\sqrt{\hat\tau_k}$')
    ax.plot(lags, -1.96 * np.sqrt(tk), color=IDAred, lw=1.3, ls='--')
    ax.vlines(lags, 0, rho, color=MainBlue, lw=1.4, label=r'$\hat\rho_k$ of a GARCH series')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Lag $k$ (days)')
    ax.set_ylabel(r'$\hat\rho_k$')
    ax.set_xticks([1, 5, 10, 15, 20])
    out_iid = int(np.sum(np.abs(rho) > b))
    out_rob = int(np.sum(np.abs(rho) > 1.96 * np.sqrt(tk)))
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch2_sem_primer_acf_bands')
    return dict(band_iid=b, band_rob_mean=float(1.96 * np.sqrt(tk).mean()), delta=float(T * tk.mean()),
                out_iid=out_iid, out_rob=out_rob)


# =============================================================================
# (iii) VR(q) as a weighted sum of autocorrelations
# =============================================================================
def vr_ar1(phi, q):
    k = np.arange(1, q)
    return 1 + 2 * np.sum((1 - k / q) * phi ** k)


def fig_vr_weights(qs=(5, 10, 20), phis=(0.3, 0.15, 0.0, -0.15, -0.3)):
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    cols = [Forest, IDAred, Amber]
    for q, c in zip(qs, cols):
        k = np.arange(1, q)
        ax.plot(k, 2 * (1 - k / q), 'o-', color=c, ms=2.5, lw=1.0, label=f'$q$ = {q}')
    ax.set_xlabel('Lag $k$')
    ax.set_ylabel(r'Weight $2(1 - k/q)$')
    ax.set_title(r'Weight of $\rho_k$ in VR($q$)', loc='left')
    ax.set_ylim(0, 2.1)
    ax = axes[1]
    qq = np.arange(1, 41)
    pc = {0.3: Forest, 0.15: Amber, 0.0: Navy, -0.15: MainBlue, -0.3: IDAred}
    for p in phis:
        lab = r'AR(1), $\phi = 0$' if p == 0 else rf'AR(1), $\phi = {p:+.2f}$'
        ax.plot(qq, [vr_ar1(p, q) for q in qq], color=pc[p], lw=1.5, ls='--' if p == 0 else '-', label=lab)
    ax.axhline(1, color=Navy, lw=0.6, ls=':')
    ax.set_xlabel('Horizon $q$ (days)')
    ax.set_ylabel('VR($q$)')
    ax.set_title(r'VR($q$) for AR(1), $\rho_k = \phi^k$', loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    bottom_legend(fig, ncol=4, handles=h1 + h2, labels=l1 + l2)
    save_fig(fig, 'ch2_sem_primer_vr_weights')
    return {p: (round(vr_ar1(p, 5), 3), round(vr_ar1(p, 40), 3)) for p in phis}


# =============================================================================
# (iv) null distribution of z(2) and z*(2) under GARCH
# =============================================================================
def fig_z_null(T=2500, reps=1000, seed=21):
    R = garch(T, a=0.12, b=0.86, seed=seed, reps=reps)
    z, zs = np.empty(reps), np.empty(reps)
    for i in range(reps):
        x = R[i]
        e = x - x.mean()
        rho = np.sum(e[1:] * e[:-1]) / np.sum(e ** 2)
        # Lo--MacKinlay VR(2) with the bias-corrected denominators
        va = np.sum(e ** 2) / (T - 1)
        s = x[1:] + x[:-1] - 2 * x.mean()
        m = 2 * (T - 1) * (1 - 2 / T)
        vr = np.sum(s ** 2) / m / va
        d1 = T * np.sum(e[1:] ** 2 * e[:-1] ** 2) / np.sum(e ** 2) ** 2
        z[i] = np.sqrt(T) * (vr - 1)
        zs[i] = np.sqrt(T) * (vr - 1) / np.sqrt(d1)
    rej = float(np.mean(np.abs(z) > 1.96)); rej_s = float(np.mean(np.abs(zs) > 1.96))
    fig, ax = plt.subplots(figsize=HALF)
    bins = np.linspace(-6, 6, 49)
    ax.hist(z, bins=bins, density=True, color=IDAred, alpha=0.45, label=f'$z(2)$: rejects {100 * rej:.1f}%')
    ax.hist(zs, bins=bins, density=True, histtype='step', color=MainBlue, lw=1.6,
            label=f'$z^*(2)$: rejects {100 * rej_s:.1f}%')
    x = np.linspace(-6, 6, 400)
    ax.plot(x, stats.norm.pdf(x), color=Navy, lw=1.3, ls='--', label='$N(0, 1)$')
    for c in (-1.96, 1.96):
        ax.axvline(c, color=Forest, lw=1.0, ls=':')
    ax.text(2.1, 0.40, r'$\pm 1.96$', color=Forest, fontsize=FS)
    ax.set_xlabel(r'Statistic under $H_0$ ($\rho_k = 0$)')
    ax.set_ylabel('Density')
    ax.set_ylim(0, 0.45)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch2_sem_primer_z_null')
    return dict(rej=rej, rej_star=rej_s, sd_z=float(z.std()), sd_zs=float(zs.std()))


# =============================================================================
# (v) Hurst exponent: fractional Brownian paths and the scaling of the variance
# =============================================================================
def fig_hurst(n=1000, Hs=(0.3, 0.5, 0.75), seed=5):
    cols = {0.3: Forest, 0.5: MainBlue, 0.75: IDAred}
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    for j, H in enumerate(Hs):
        x = fgn(n, H, seed + j)
        axes[0].plot(np.cumsum(x) / n ** H, color=cols[H], lw=0.9, label=f'$H$ = {H}')
    axes[0].set_xlabel('Day $t$')
    axes[0].set_ylabel(r'$\sum_{s \leq t} x_s \,/\, n^H$')
    axes[0].set_title('Paths, rescaled', loc='left')
    q = np.array([1, 2, 5, 10, 20, 50, 100])
    for H in Hs:
        axes[1].plot(q, q ** (2 * H - 1), 'o-', color=cols[H], ms=2.5, lw=1.4)
    axes[1].set_xscale('log'); axes[1].set_yscale('log')
    axes[1].set_xticks([1, 10, 100]); axes[1].set_xticklabels(['1', '10', '100'])
    axes[1].set_xlabel('Horizon $q$ (log)')
    axes[1].set_ylabel(r'VR($q$) $= q^{2H-1}$')
    axes[1].set_title('Slope $2H - 1$ on log axes', loc='left')
    bottom_legend(fig, axes[0], ncol=3)
    save_fig(fig, 'ch2_sem_primer_hurst')
    return {H: float(100 ** (2 * H - 1)) for H in Hs}


# =============================================================================
# (vi) short against long memory: geometric against hyperbolic decay of rho_k
# =============================================================================
def fig_memory(phi=0.4, H=0.75, K=60):
    k = np.arange(1, K + 1)
    r_ar = phi ** k
    r_fg = 0.5 * ((k + 1) ** (2 * H) - 2 * k ** (2 * H) + (k - 1) ** (2 * H))
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(k, r_ar, 'o-', color=MainBlue, ms=3, lw=1.2, label=rf'AR(1), $\phi$ = {phi}: $\rho_k = \phi^k$')
    ax.plot(k, r_fg, 's-', color=IDAred, ms=3, lw=1.2, label=rf'fGn, $H$ = {H}: $\rho_k \approx H(2H-1)k^{{2H-2}}$')
    ax.set_yscale('log')
    ax.set_ylim(1e-6, 1)
    ax.set_xlabel('Lag $k$')
    ax.set_ylabel(r'$\rho_k$ (log scale)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch2_sem_primer_memory')
    return dict(ar_k20=float(phi ** 20), fg_k20=float(r_fg[19]))


# =============================================================================
# (vii) DFA: profile, local trends and the log-log slope
# =============================================================================
def dfa(x, ns):
    y = np.cumsum(x - x.mean())
    F = []
    for n in ns:
        k = len(y) // n
        seg = y[:k * n].reshape(k, n)
        t = np.arange(n)
        res = []
        for s in seg:
            c = np.polyfit(t, s, 1)
            res.append(np.mean((s - np.polyval(c, t)) ** 2))
        F.append(np.sqrt(np.mean(res)))
    return np.array(F)


def fig_dfa(n=1000, seed=9):
    x = np.random.default_rng(seed).standard_normal(n)
    xl = fgn(n, 0.75, seed + 1)
    y = np.cumsum(x - x.mean())
    seglen = 100
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(y, color=MainBlue, lw=0.9, label='Profile $y_k$')
    t = np.arange(seglen)
    for j in range(n // seglen):
        s = y[j * seglen:(j + 1) * seglen]
        c = np.polyfit(t, s, 1)
        ax.plot(j * seglen + t, np.polyval(c, t), color=IDAred, lw=1.4, label='Local linear trend' if j == 0 else '_')
        ax.axvline(j * seglen, color=Amber, lw=0.6, ls=':')
    ax.set_xlabel('$k$')
    ax.set_ylabel('$y_k$')
    ax.set_title(f'Segments of length $n$ = {seglen}', loc='left')
    ax = axes[1]
    ns = np.unique(np.round(np.exp(np.linspace(np.log(10), np.log(250), 12))).astype(int))
    out = {}
    for xx, col, lab in ((x, MainBlue, 'i.i.d.'), (xl, IDAred, 'fGn, $H$ = 0.75')):
        F = dfa(xx, ns)
        b = np.polyfit(np.log(ns), np.log(F), 1)
        out[lab] = float(b[0])
        ax.plot(np.log(ns), np.log(F), 'o', color=col, ms=2.5)
        ax.plot(np.log(ns), np.polyval(b, np.log(ns)), color=col, lw=1.2,
                label=rf'{lab}: slope $\hat\alpha_{{DFA}}$ = {b[0]:.2f}')
    ax.set_xlabel(r'$\ln n$')
    ax.set_ylabel(r'$\ln F(n)$')
    ax.set_title('Fluctuation function', loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    bottom_legend(fig, ncol=2, handles=h1 + h2, labels=l1 + l2)
    save_fig(fig, 'ch2_sem_primer_dfa')
    return out


# =============================================================================
# (viii) sign-flip (wild) bootstrap
# =============================================================================
def fig_wild(T=1000, B=999, seed=31):
    r = garch(T, a=0.12, b=0.85, seed=seed)
    e = r - r.mean()
    rng = np.random.default_rng(seed + 1)
    eta = rng.choice([-1.0, 1.0], size=(B, T))
    star = eta * e
    rho_b = np.array([np.sum(s[1:] * s[:-1]) / np.sum(s ** 2) for s in star])
    lo, hi = np.quantile(rho_b, [0.025, 0.975])
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(e, color=MainBlue, lw=0.4, label='Original $e_t$')
    off = 2.2 * np.abs(e).max()
    ax.plot(star[0] - off, color=IDAred, lw=0.4, label=r'One copy $e_t\eta_t$')
    ax.set_yticks([0, -off]); ax.set_yticklabels(['$e_t$', r'$e_t\eta_t$'])
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Return (shifted)')
    ax.set_title('Same $|e_t|$, random signs', loc='left')
    ax = axes[1]
    ax.hist(rho_b, bins=35, color=BandBlue, edgecolor=MainBlue, lw=0.4, label=r'999 values $\hat\rho_1^*$')
    for v in (lo, hi):
        ax.axvline(v, color=IDAred, lw=1.4, ls='--')
    for v in (-1.96 / np.sqrt(T), 1.96 / np.sqrt(T)):
        ax.axvline(v, color=Forest, lw=1.2, ls=':')
    ax.set_xlabel(r'$\hat\rho_1^*$')
    ax.set_ylabel('Count')
    ax.set_title('Null distribution of $\\hat\\rho_1$', loc='left')
    handles = [Line2D([], [], color=MainBlue, lw=1.5), Line2D([], [], color=IDAred, lw=1.5),
               Patch(facecolor=BandBlue, edgecolor=MainBlue), Line2D([], [], color=IDAred, ls='--', lw=1.4),
               Line2D([], [], color=Forest, ls=':', lw=1.2)]
    labels = ['Original $e_t$', r'One copy $e_t\eta_t$', r'999 values $\hat\rho_1^*$',
              'Bootstrap band (2.5%, 97.5%)', r'i.i.d. band $\pm 1.96/\sqrt{T}$']
    bottom_legend(fig, ncol=3, handles=handles, labels=labels)
    save_fig(fig, 'ch2_sem_primer_wild')
    return dict(lo=float(lo), hi=float(hi), iid=float(1.96 / np.sqrt(T)))


# =============================================================================
# (ix) rolling-window estimate of rho_1 when predictability fades (adaptive markets)
# =============================================================================
def fig_rolling(T=3000, W=250, step=21, seed=17):
    rng = np.random.default_rng(seed)
    phi = np.where(np.arange(T) < 1000, 0.25, np.where(np.arange(T) < 1500, 0.25 * (1500 - np.arange(T)) / 500, 0.0))
    u = rng.standard_normal(T)
    r = np.empty(T); r[0] = u[0]
    for t in range(1, T):
        r[t] = phi[t] * r[t - 1] + u[t]
    ends = np.arange(W, T + 1, step)
    est = np.array([acf(r[e - W:e], 1)[0] for e in ends])
    fig, ax = plt.subplots(figsize=(5.6, 1.25))
    ax.axhspan(-1.96 / np.sqrt(W), 1.96 / np.sqrt(W), color=BandBlue, alpha=0.9, lw=0,
               label=r'band $\pm 1.96/\sqrt{W}$ if $\rho_1 = 0$')
    ax.plot(np.arange(T), phi, color=IDAred, lw=1.4, ls='--', label=r'true $\rho_1$')
    ax.plot(ends, est, 'o-', color=MainBlue, ms=3, lw=1.0, label=fr'$\hat\rho_1$ on the last $W$ = {W} days')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Last day of the window')
    ax.set_ylabel(r'$\rho_1$')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch2_sem_primer_rolling')
    out_late = float(np.mean(np.abs(est[ends > 1750]) > 1.96 / np.sqrt(W)))
    return dict(share_out_late=out_late, n_windows=len(ends))


# =============================================================================
# (x) multiple testing: FWER and the Bonferroni / Holm thresholds
# =============================================================================
def fig_holm(M=10, alpha=0.05):
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    m = np.arange(1, 51)
    axes[0].plot(m, 100 * (1 - (1 - alpha) ** m), color=IDAred, lw=1.6, label=r'FWER $= 1 - 0.95^M$')
    axes[0].axhline(5, color=Forest, lw=1.0, ls=':', label='Target 5%')
    axes[0].set_xlabel('Number of tests $M$')
    axes[0].set_ylabel('FWER (%)')
    axes[0].set_title('Independent tests at 5%', loc='left')
    axes[0].set_ylim(0, 100)
    p = np.array([0.001, 0.004, 0.006, 0.007, 0.03, 0.12, 0.25, 0.4, 0.6, 0.85])   # an illustrative family
    j = np.arange(1, M + 1)
    holm = alpha / (M - j + 1)
    ax = axes[1]
    ax.plot(j, p, 'o', color=MainBlue, ms=3.5, label='Sorted p-values $p_{(j)}$')
    ax.step(j, holm, where='mid', color=IDAred, lw=1.4, label=r'Holm $\alpha/(M - j + 1)$')
    ax.axhline(alpha / M, color=Amber, lw=1.4, ls='--', label=r'Bonferroni $\alpha/M$')
    ax.set_yscale('log')
    ax.set_ylim(1e-4, 1.2)
    ax.set_xticks(j)
    ax.set_xlabel('Rank $j$')
    ax.set_ylabel('p-value (log)')
    ax.set_title(f'$M$ = {M} tests, $\\alpha$ = 5%', loc='left')
    stop = int(np.argmax(p >= holm)) if np.any(p >= holm) else M
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    bottom_legend(fig, ncol=3, handles=h1 + h2, labels=l1 + l2)
    save_fig(fig, 'ch2_sem_primer_holm')
    return dict(p=p.round(4).tolist(), holm_rej=stop, bonf_rej=int(np.sum(p < alpha / M)),
                fwer10=1 - 0.95 ** 10)


# =============================================================================
# (xi) Kendall bias of the AR(1) coefficient of a persistent predictor
# =============================================================================
def fig_kendall(rho=0.95, T=50, reps=20000, seed=8):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal((reps, T + 200))
    x = np.zeros((reps, T + 200))
    for t in range(1, T + 200):
        x[:, t] = rho * x[:, t - 1] + v[:, t]
    x = x[:, 200:]
    a, b = x[:, :-1], x[:, 1:]
    ac = a - a.mean(1, keepdims=True)
    bc = b - b.mean(1, keepdims=True)
    rh = np.sum(ac * bc, 1) / np.sum(ac ** 2, 1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.hist(rh, bins=60, density=True, color=BandBlue, edgecolor=MainBlue, lw=0.3, label=r'OLS $\hat\rho$, 20 000 samples')
    ax.axvline(rho, color=Forest, lw=1.6, label=rf'true $\rho$ = {rho}')
    ax.axvline(rh.mean(), color=IDAred, lw=1.6, ls='--', label=rf'mean of $\hat\rho$ = {rh.mean():.3f}')
    ax.axvline(rho - (1 + 3 * rho) / T, color=Amber, lw=1.4, ls=':',
               label=rf'Kendall: $\rho - (1 + 3\rho)/T$ = {rho - (1 + 3 * rho) / T:.3f}')
    ax.set_xlim(0.55, 1.05)
    ax.set_xlabel(rf'$\hat\rho$ ($T$ = {T})')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch2_sem_primer_kendall')
    return dict(mean=float(rh.mean()), kendall=rho - (1 + 3 * rho) / T)


def run_all():
    res = {}
    res['rw'] = fig_rw()
    res['acf_bands'] = fig_acf_bands()
    res['vr_weights'] = fig_vr_weights()
    res['z_null'] = fig_z_null()
    res['hurst'] = fig_hurst()
    res['memory'] = fig_memory()
    res['dfa'] = fig_dfa()
    res['wild'] = fig_wild()
    res['rolling'] = fig_rolling()
    res['holm'] = fig_holm()
    res['kendall'] = fig_kendall()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

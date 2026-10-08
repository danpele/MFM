"""
seminar13_explainers.py -- Explanatory (primer) charts for Seminar 13 (MFM): machine learning in finance
=======================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 13,
which takes place BEFORE Lecture 13. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (the logistic link and the L1 path, ROC curves and the AUC, the log loss, the block bootstrap,
fractional differencing, the triple barrier, purged K-fold validation, the best Sharpe ratio among N
zero-skill trials) and contain no exercise answers.

Output: charts/ch13_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_13/seminar13_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score

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

HALF = (2.75, 2.1)    # one column of a two-column slide


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
# 1. logistic link and the L1 coefficient path
# =============================================================================
def fig_logit(seed=1, n=600, p=6):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, p))
    beta = np.array([1.0, -0.6, 0.3, 0, 0, 0])
    y = (rng.random(n) < 1 / (1 + np.exp(-X @ beta))).astype(int)
    Cs = np.logspace(-3, 1, 40)
    path = []
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for C in Cs:
            m = LogisticRegression(penalty='l1', C=C, solver='liblinear').fit(X, y)
            path.append(m.coef_[0].copy())
    path = np.array(path)
    fig, axes = plt.subplots(2, 1, figsize=(2.75, 2.5), gridspec_kw=dict(height_ratios=[1, 1.2]))
    s = np.linspace(-6, 6, 300)
    ax = axes[0]
    ax.plot(s, 1 / (1 + np.exp(-s)), color=MainBlue, lw=1.3, label=r'$\hat p = 1/(1 + e^{-\mathbf{x}^\top\beta})$')
    ax.axhline(0.5, color=IDAred, lw=0.7, ls='--', label='Threshold 0.5')
    ax.set_xlabel(r'Linear score $\mathbf{x}^\top\beta$')
    ax.set_ylabel(r'$\hat p$')
    ax = axes[1]
    cols = [MainBlue, IDAred, Forest]
    for j in range(p):
        if beta[j] != 0:
            ax.plot(Cs, path[:, j], color=cols[j], lw=1.0, label=f'$\\beta_{j + 1} = {beta[j]:g}$')
        else:
            ax.plot(Cs, path[:, j], color=Amber, lw=0.9, ls='--', label=r'$\beta_4, \beta_5, \beta_6$ (true 0)' if j == 3 else '_')
    ax.set_xscale('log')
    ax.axhline(0, color=Navy, lw=0.4)
    ax.set_xlabel(r'$C = 1/\lambda$ (log scale; left: strong penalty)')
    ax.set_ylabel('Coefficient')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch13_sem_primer_logit')


# =============================================================================
# 2. ROC curves and the AUC
# =============================================================================
def fig_roc(seed=2, n=4000):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, n)
    fig, ax = plt.subplots(figsize=(2.75, 2.3))
    for shift, col in [(0.0, Amber), (0.55, MainBlue), (1.5, IDAred)]:
        s = rng.standard_normal(n) + shift * y
        fpr, tpr, _ = roc_curve(y, s)
        auc = roc_auc_score(y, s)
        ax.plot(fpr, tpr, color=col, lw=1.2, label=f'AUC = {auc:.2f}')
    ax.plot([0, 1], [0, 1], color=Navy, lw=0.6, ls=':', label='No skill')
    ax.set_xlabel('False-positive rate FPR$(c)$')
    ax.set_ylabel('True-positive rate TPR$(c)$')
    ax.set_aspect('equal')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch13_sem_primer_roc')


# =============================================================================
# 3. log loss
# =============================================================================
def fig_logloss():
    p = np.linspace(0.01, 0.99, 400)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(p, -np.log(p), color=MainBlue, lw=1.3, label=r'Up day ($y = 1$): $-\ln\hat p$')
    ax.plot(p, -np.log(1 - p), color=IDAred, lw=1.3, label=r'Down day ($y = 0$): $-\ln(1 - \hat p)$')
    ax.plot(0.5, np.log(2), 'o', color=Forest, ms=4, label=r'$\hat p = 0.5$: $\ln 2 = 0.693$')
    ax.set_xlabel(r'Predicted probability of up, $\hat p$')
    ax.set_ylabel(r'Loss $\ell$')
    ax.set_ylim(0, 4.2)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch13_sem_primer_logloss')


# =============================================================================
# 4. block bootstrap: the standard error of a mean of dependent observations
# =============================================================================
def fig_bootstrap(seed=4, n=2000, h=5, B=600):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n + h - 1)
    x = np.convolve(e, np.ones(h), mode='valid')        # overlapping 5-day sums: MA(4)
    true_se = np.sqrt(h ** 2 / n)                        # long-run variance h^2 (unit shocks)
    Ls = [1, 2, 3, 5, 8, 12, 20, 30, 45, 60]
    ses = []
    for L in Ls:
        k = int(np.ceil(n / L))
        starts = rng.integers(0, n, (B, k))
        idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n
        idx = idx.reshape(B, -1)[:, :n]
        ses.append(x[idx].mean(axis=1).std())
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(Ls, ses, 'o-', color=MainBlue, lw=1.1, ms=3.5, label='Circular block bootstrap s.e.')
    ax.axhline(true_se, color=IDAred, lw=1.0, ls='--', label='True s.e. of the mean')
    ax.axhline(x.std() / np.sqrt(n), color=Amber, lw=1.0, ls=':', label=r'Naive s.e. $s/\sqrt{n}$')
    ax.set_xscale('log')
    ax.set_xticks([1, 2, 5, 10, 20, 50])
    ax.set_xticklabels(['1', '2', '5', '10', '20', '50'])
    ax.set_xlabel('Block length $L$ (days)')
    ax.set_ylabel('Standard error of the mean')
    ax.set_ylim(0, 0.14)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch13_sem_primer_bootstrap')


# =============================================================================
# 5. fractional differencing: weights and a filtered random walk
# =============================================================================
def ffd_w(d, thr=1e-4, kmax=5000):
    w = [1.0]
    for k in range(1, kmax):
        wk = -w[-1] * (d - k + 1) / k
        if abs(wk) < thr:
            break
        w.append(wk)
    return np.array(w)


def fig_ffd(seed=5, n=1500, d_show=0.4):
    fig, axes = plt.subplots(2, 1, figsize=(2.75, 2.6), gridspec_kw=dict(height_ratios=[1, 1]))
    ax = axes[0]
    for d, col in [(0.2, MainBlue), (0.5, IDAred), (0.8, Forest)]:
        w = ffd_w(d, thr=1e-6, kmax=400)
        k = np.arange(1, len(w))
        ax.plot(k, np.abs(w[1:]), color=col, lw=1.1, label=f'$d = {d}$')
    ax.axhline(1e-4, color=Amber, lw=0.8, ls='--', label=r'threshold $10^{-4}$')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Lag $k$ (days)')
    ax.set_ylabel(r'$|w_k|$')
    rng = np.random.default_rng(seed)
    x = np.cumsum(0.02 * rng.standard_normal(n))
    w = ffd_w(d_show)
    K = len(w) - 1
    xt = np.array([w @ x[t - K:t + 1][::-1] for t in range(K, n)])
    ax = axes[1]
    ax.plot(np.arange(n), x - x[0], color=MainBlue, lw=0.8, label='Random walk $x_t$')
    ax.plot(np.arange(K, n), xt, color=IDAred, lw=0.8, label=f'FFD, $d = {d_show}$')
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Level')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch13_sem_primer_ffd')
    return dict(K=K)


# =============================================================================
# 6. the triple barrier on a simulated path
# =============================================================================
def fig_barrier(seed=30, P0=100.0, sig=0.02, h=10, pt=1.0, sl=1.0):
    rng = np.random.default_rng(seed)
    steps = 40
    t = np.arange(steps + 1) / 4.0                         # four observations a day, closes at integers
    P = P0 * np.exp(np.concatenate([[0], np.cumsum(sig / 2 * rng.standard_normal(steps))]))
    up, lo = P0 * np.exp(pt * sig * np.sqrt(h)), P0 * np.exp(-sl * sig * np.sqrt(h))
    closes = P[::4]
    days = np.arange(len(closes))
    hit = None
    for i in range(1, len(closes)):
        if closes[i] >= up or closes[i] <= lo:
            hit = i; break
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(t, P, color=MainBlue, lw=0.9, label='Price path')
    ax.plot(days, closes, 'o', color=MainBlue, ms=2.5, label='Daily closes')
    ax.axhline(up, color=Forest, lw=1.1, label=r'Upper $P_{t_0}e^{pt\,\sigma\sqrt{h}}$')
    ax.axhline(lo, color=IDAred, lw=1.1, label=r'Lower $P_{t_0}e^{-sl\,\sigma\sqrt{h}}$')
    ax.axvline(h, color=Amber, lw=1.1, label=r'Vertical $t_0 + h$')
    if hit is not None:
        ax.plot(days[hit], closes[hit], '*', color=IDAred if closes[hit] <= lo else Forest, ms=9,
                label=f'First touch: day {hit}')
    ax.set_xlabel('Days after the entry $t_0$')
    ax.set_ylabel('Price')
    ax.set_xlim(-0.3, h + 0.5)
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch13_sem_primer_barrier')
    return dict(up=up, lo=lo, hit=hit, closes=[round(c, 2) for c in closes[:hit + 1 if hit else None]])


# =============================================================================
# 7. purged K-fold with an embargo
# =============================================================================
def fig_purged(n=30, K=5, h=2, e=1):
    L = n // K
    fig, ax = plt.subplots(figsize=(2.75, 2.0))
    for f in range(K):
        test = np.arange(f * L, (f + 1) * L)
        t_lo, t_hi = test[0], test[-1] + h            # days covered by the test labels
        for i in range(n):
            if i in test:
                col = IDAred
            elif i < test[0] and i + h >= t_lo:
                col = Amber                              # purged before
            elif test[-1] < i <= test[-1] + e:
                col = Forest                             # embargo
            elif test[-1] + e < i <= t_hi:
                col = Amber                              # purged after: starts before the test labels end
            else:
                col = MainBlue
            ax.add_patch(Rectangle((i, K - 1 - f), 0.9, 0.75, color=col, lw=0))
    ax.set_xlim(0, n); ax.set_ylim(-0.2, K)
    ax.set_yticks(np.arange(K) + 0.37)
    ax.set_yticklabels([f'Fold {K - k}' for k in range(K)])
    ax.set_xlabel('Observation $i$')
    for sp in ('left', 'right', 'top'):
        ax.spines[sp].set_visible(False)
    hd = [Rectangle((0, 0), 1, 1, color=c) for c in (MainBlue, IDAred, Amber, Forest)]
    bottom_legend(fig, ax, ncol=4, handles=hd, labels=['Train', 'Test', 'Purged', 'Embargo'])
    save_fig(fig, 'ch13_sem_primer_purged')


# =============================================================================
# 8. the best Sharpe ratio among N zero-skill strategies
# =============================================================================
def fig_maxsr(seed=8, T=400, reps=4000):
    rng = np.random.default_rng(seed)
    gE = 0.5772156649
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for N, col in [(1, Amber), (10, MainBlue), (100, IDAred)]:
        sr = rng.standard_normal((reps, N)) / np.sqrt(T)       # per-day SR of zero-skill trials, V = 1/T
        best = sr.max(axis=1)
        ax.hist(best, bins=50, density=True, histtype='step', color=col, lw=1.1, label=f'Best of $N = {N}$')
        if N > 1:
            sr0 = np.sqrt(1 / T) * ((1 - gE) * stats.norm.ppf(1 - 1 / N) + gE * stats.norm.ppf(1 - 1 / (N * np.e)))
            ax.axvline(sr0, color=col, lw=0.9, ls='--')
            out[N] = (float(sr0), float(best.mean()))
    ax.plot([], [], color=Navy, lw=0.9, ls='--', label=r'$SR_0$ formula')
    ax.set_xlabel(r'Per-day SR of the best trial')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch13_sem_primer_maxsr')
    return out


if __name__ == '__main__':
    print('Seminar 13 primer charts')
    fig_logit()
    fig_roc()
    fig_logloss()
    fig_bootstrap()
    print('   ffd', fig_ffd())
    print('   barrier', fig_barrier())
    fig_purged()
    print('   maxsr', fig_maxsr())

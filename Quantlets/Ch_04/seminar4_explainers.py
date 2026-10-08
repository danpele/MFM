"""
seminar4_explainers.py -- Explanatory (primer) charts for Seminar 4 (MFM): portfolio optimisation
==================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 4,
which takes place BEFORE Lecture 4. All charts use SIMULATED or textbook numbers only (fixed seeds): they
illustrate the concepts (two-asset diversification, the efficient frontier, estimation error in the weights,
risk contributions, the rolling backtest, trading costs, the z-test, the precision of a Sharpe difference,
the block bootstrap, covariance shrinkage, hierarchical clustering) and contain no exercise answers.

Output: charts/ch4_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_04/seminar4_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform

# course palette (no grey)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'
BandBlue = '#C5D2E8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

# drawn at slide size: text 6.8-7.6 pt on the slide
plt.rcParams.update({'font.size': 7.4, 'axes.labelsize': 7.4, 'axes.titlesize': 7.6, 'xtick.labelsize': 6.9,
                     'ytick.labelsize': 6.9, 'legend.fontsize': 7.0, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
                     'legend.handlelength': 1.6, 'legend.columnspacing': 1.2})

FULL = (5.55, 1.85)   # full text width (about 408 pt) of a 16:9 slide
HALF = (2.75, 1.62)   # one column of a two-column frame
ANN = 6.9             # annotations


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True, pad_inches=0.03)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=200,
                pad_inches=0.03)
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


# =============================================================================
# (1) two assets: portfolio volatility against the weight, for several correlations
# =============================================================================
def fig_two_asset(s1=0.20, s2=0.10):
    w = np.linspace(-0.2, 1.2, 281)
    fig, ax = plt.subplots(figsize=HALF)
    cols = {-0.5: Forest, 0.0: MainBlue, 0.5: Amber, 1.0: IDAred}
    out = {}
    for rho, c in cols.items():
        v = w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * rho * s1 * s2
        ax.plot(w, 100 * np.sqrt(v), color=c, lw=1.2, label=rf'$\rho$ = {rho:+.1f}' if rho else r'$\rho$ = 0')
        s12 = rho * s1 * s2
        den = s1 ** 2 + s2 ** 2 - 2 * s12
        ws = (s2 ** 2 - s12) / den
        vs = ws ** 2 * s1 ** 2 + (1 - ws) ** 2 * s2 ** 2 + 2 * ws * (1 - ws) * s12
        if rho < 1:
            ax.plot(ws, 100 * np.sqrt(vs), 'o', color=c, ms=3.5)
        out[rho] = (round(ws, 3), round(100 * np.sqrt(vs), 2))
    ax.plot([], [], 'o', color=Navy, ms=3.5, label='GMV of each curve')
    ax.axvline(0, color=Navy, lw=0.5, ls=':'); ax.axvline(1, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel('Weight $w$ of asset 1 ($\\sigma_1$ = 20%)')
    ax.set_ylabel('$\\sigma_p$ (% a year)')
    ax.set_ylim(0, 25)
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch4_sem_primer_two_asset')
    return out


# =============================================================================
# (2) efficient frontier of four simulated assets: GMV, tangency, capital market line, 1/N
# =============================================================================
MU4 = np.array([0.04, 0.06, 0.08, 0.10])
VOL4 = np.array([0.08, 0.12, 0.16, 0.22])
CORR4 = np.array([[1.0, 0.3, 0.2, 0.1], [0.3, 1.0, 0.4, 0.3], [0.2, 0.4, 1.0, 0.5], [0.1, 0.3, 0.5, 1.0]])
SIG4 = np.outer(VOL4, VOL4) * CORR4


def fig_frontier():
    mu, S = MU4, SIG4
    Si = np.linalg.inv(S)
    one = np.ones(4)
    A, B, C = one @ Si @ one, one @ Si @ mu, mu @ Si @ mu
    m = np.linspace(0.0, 0.14, 300)
    sd = np.sqrt((A * m ** 2 - 2 * B * m + C) / (A * C - B ** 2))
    w_g = Si @ one / A
    w_t = Si @ mu / B
    pts = {'GMV': w_g, 'Tangency': w_t, '1/N': one / 4}
    fig, ax = plt.subplots(figsize=HALF)
    eff = m >= B / A
    ax.plot(100 * sd[eff], 100 * m[eff], color=MainBlue, lw=1.3, label='Frontier')
    ax.plot(100 * sd[~eff], 100 * m[~eff], color=MainBlue, lw=1.0, ls='--', label='Inefficient part')
    sr_t = (w_t @ mu) / np.sqrt(w_t @ S @ w_t)
    xs = np.linspace(0, 24, 10)
    ax.plot(xs, sr_t * xs, color=Amber, lw=1.0, label='Max-Sharpe line')
    ax.plot(100 * VOL4, 100 * MU4, 's', color=Navy, ms=3.2, label='Assets')
    out = {}
    for (nm, w), c, mk in zip(pts.items(), [Forest, IDAred, Amber], ['o', 'D', '^']):
        s, r = np.sqrt(w @ S @ w), w @ mu
        ax.plot(100 * s, 100 * r, mk, color=c, ms=4.5, label=nm)
        out[nm] = dict(vol=round(100 * s, 2), mean=round(100 * r, 2), sharpe=round(r / s, 3),
                       w=np.round(w, 3).tolist())
    ax.set_xlim(0, 24); ax.set_ylim(0, 13)
    ax.set_xlabel('Volatility $\\sigma_p$ (% a year)')
    ax.set_ylabel('Excess mean $\\mu_p$ (%)')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch4_sem_primer_frontier')
    return out


# =============================================================================
# (3) estimation error: sample tangency and GMV weights over 500 simulated 60-month windows
# =============================================================================
def fig_estimation_error(T=60, n_sim=500, seed=7):
    rng = np.random.default_rng(seed)
    mu_m, S_m = MU4 / 12, SIG4 / 12
    one = np.ones(4)
    true_t = np.linalg.solve(S_m, mu_m); true_t /= true_t.sum()
    true_g = np.linalg.solve(S_m, one); true_g /= true_g.sum()
    L = np.linalg.cholesky(S_m)
    wt, wg = [], []
    for _ in range(n_sim):
        X = mu_m + rng.standard_normal((T, 4)) @ L.T
        m, S = X.mean(0), np.cov(X, rowvar=False)
        a = np.linalg.solve(S, m); wt.append(a / a.sum())
        g = np.linalg.solve(S, one); wg.append(g / g.sum())
    wt, wg = np.array(wt), np.array(wg)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(wt[:, 0], wt[:, 3], 'o', color=IDAred, ms=1.6, alpha=0.55, label='Sample MV')
    ax.plot(wg[:, 0], wg[:, 3], 'o', color=Forest, ms=2.2, alpha=0.9, label='Sample GMV')
    ax.plot(*true_t[[0, 3]], 'D', color=Navy, ms=3.2, mfc='none', mew=0.9, label='True tangency')
    ax.plot(*true_g[[0, 3]], '*', color=Navy, ms=4.0, mfc='none', mew=0.7, label='True GMV')
    ax.plot(0.25, 0.25, '^', color=Amber, ms=4.5, label='1/N')
    ax.set_xlim(-3, 4); ax.set_ylim(-2, 3)
    ax.axhline(0, color=Navy, lw=0.4, ls=':'); ax.axvline(0, color=Navy, lw=0.4, ls=':')
    ax.set_xlabel('Weight of asset 1 ($\\sigma_1$ = 8%; $\\sigma_4$ = 22%)')
    ax.set_ylabel('Weight of asset 4')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch4_sem_primer_estimation_error')
    iqr = lambda x: float(np.subtract(*np.percentile(x, [75, 25])))
    return dict(true_t=np.round(true_t, 3).tolist(), true_g=np.round(true_g, 3).tolist(),
                iqr_t1=round(iqr(wt[:, 0]), 2), iqr_g1=round(iqr(wg[:, 0]), 2),
                share_t_out=round(float(np.mean((np.abs(wt) > 1).any(1))), 3))


# =============================================================================
# (4) capital weights against risk shares: 1/N and ERC, sigma = 20% and 10%, rho = 0
# =============================================================================
def fig_risk_shares(s1=0.20, s2=0.10):
    S = np.diag([s1 ** 2, s2 ** 2])
    rows = {'1/N': np.array([0.5, 0.5]), 'ERC': np.array([1 / 3, 2 / 3])}
    fig, ax = plt.subplots(figsize=HALF)
    y = 0
    labels, ticks = [], []
    out = {}
    for nm, w in rows.items():
        v = w @ S @ w
        share = w * (S @ w) / v
        out[nm] = dict(share=np.round(share, 3).tolist(), vol=round(100 * np.sqrt(v), 2))
        for kind, vals in [('capital', w), ('risk', share)]:
            left = 0
            for i, (val, c) in enumerate(zip(vals, [IDAred, MainBlue])):
                ax.barh(y, 100 * val, left=left, color=c, height=0.62,
                        label=['Asset 1 ($\\sigma$ = 20%)', 'Asset 2 ($\\sigma$ = 10%)'][i] if y == 0 else '_')
                ax.text(left + 50 * val, y, f'{100 * val:.0f}%', ha='center', va='center', color='white',
                        fontsize=ANN, fontweight='bold')
                left += 100 * val
            labels.append(f'{nm}: {kind}'); ticks.append(y)
            y -= 1
        y -= 0.4
    ax.set_yticks(ticks); ax.set_yticklabels(labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Share (%)')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch4_sem_primer_risk_shares')
    return out


# =============================================================================
# (5) the rolling backtest: estimation windows and the month held; drift of 1/N weights
# =============================================================================
def fig_rolling(window=60, n_show=4):
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.55, 1]))
    ax = axes[0]
    for k in range(n_show):
        t0 = k * 6
        y = n_show - k
        ax.add_patch(Rectangle((t0, y - 0.32), window, 0.64, color=BandBlue, lw=0))
        ax.add_patch(Rectangle((t0 + window, y - 0.32), 1, 0.64, color=IDAred, lw=0))
        ax.text(t0 + window / 2, y, 'window: months $t-60, \\dots, t-1$' if k == 0 else '',
                ha='center', va='center', fontsize=ANN, color=Navy)
        ax.text(t0 + window + 2.5, y, f'hold in $t$' if k == 0 else f'$t+{6 * k}$', va='center',
                fontsize=ANN, color=IDAred)
    ax.add_patch(Rectangle((0, -1), 1, 1, color=BandBlue, lw=0, label='Estimation window (60 months)'))
    ax.add_patch(Rectangle((0, -1), 1, 1, color=IDAred, lw=0, label='Out-of-sample month'))
    ax.set_xlim(-2, 100); ax.set_ylim(0.3, n_show + 0.7)
    ax.set_yticks([])
    ax.set_xlabel('Month')
    ax.set_title('Rolling window: no month is used to choose its own weights', loc='left')
    ax = axes[1]
    w0 = np.array([0.5, 0.5]); R = np.array([0.10, -0.10])
    wp = w0 * (1 + R) / (w0 * (1 + R)).sum()
    x = np.arange(2)
    ax.bar(x - 0.2, 100 * w0, width=0.36, color=MainBlue, label='Target $w_i$ (start of month)')
    ax.bar(x + 0.2, 100 * wp, width=0.36, color=Amber, label='Drifted $w_i^+$ (end of month)')
    for i in range(2):
        ax.text(i - 0.2, 100 * w0[i] + 1, f'{100 * w0[i]:.0f}%', ha='center', fontsize=ANN, color=MainBlue)
        ax.text(i + 0.2, 100 * wp[i] + 1, f'{100 * wp[i]:.0f}%', ha='center', fontsize=ANN, color=Amber)
    ax.set_xticks(x); ax.set_xticklabels(['Asset 1\n$R_1$ = +10%', 'Asset 2\n$R_2$ = $-$10%'])
    ax.set_ylim(0, 68)
    ax.set_ylabel('Weight (%)')
    ax.set_title(f'Drift of 1/N; turnover $TO$ = {np.abs(w0 - wp).sum():.2f}', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch4_sem_primer_rolling')
    return dict(w_plus=np.round(wp, 3).tolist(), TO=float(np.abs(w0 - wp).sum()))


# =============================================================================
# (6) trading costs: net Sharpe ratio against the cost per unit traded, break-even cost
# =============================================================================
def fig_costs(T=240, seed=11):
    rng = np.random.default_rng(seed)
    std = lambda x: (x - x.mean()) / x.std(ddof=1)
    # two simulated monthly excess-return series (moments fixed exactly): an optimised rule with high turnover
    # and a 1/N-like rule with low turnover
    r1 = 0.0090 + 0.040 * std(rng.standard_normal(T))
    r2 = 0.0075 + 0.042 * std(rng.standard_normal(T))
    to1 = np.clip(0.30 + 0.10 * rng.standard_normal(T), 0, None)
    to2 = np.clip(0.03 + 0.01 * rng.standard_normal(T), 0, None)
    c_bp = np.linspace(0, 150, 1501)
    sr = lambda x: np.sqrt(12) * x.mean() / x.std(ddof=1)
    s1 = np.array([sr(r1 - c / 1e4 * to1) for c in c_bp])
    s2 = np.array([sr(r2 - c / 1e4 * to2) for c in c_bp])
    i = int(np.argmax(s1 < s2))
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(c_bp, s1, color=IDAred, lw=1.3, label=f'High turnover (mean $TO$ = {to1.mean():.2f})')
    ax.plot(c_bp, s2, color=MainBlue, lw=1.3, label=f'Low turnover (mean $TO$ = {to2.mean():.2f})')
    ax.axvline(c_bp[i], color=Navy, lw=0.7, ls='--')
    ax.annotate(f'$c^*$ = {c_bp[i]:.0f} bp', (c_bp[i], s1[i]), xytext=(8, 22),
                textcoords='offset points', fontsize=ANN, color=Navy,
                arrowprops=dict(arrowstyle='->', color=Navy, lw=0.7))
    ax.set_xlim(0, 150)
    ax.set_xlabel('Cost $c$ per unit traded (bp)')
    ax.set_ylabel('Net Sharpe (annual)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch4_sem_primer_costs')
    return dict(c_star=float(c_bp[i]), sr1_0=round(s1[0], 3), sr2_0=round(s2[0], 3),
                sr1_50=round(s1[500], 3), sr2_50=round(s2[500], 3),
                to1=round(to1.mean(), 3), to2=round(to2.mean(), 3))


# =============================================================================
# (7) the two-sided z-test: rejection region and p-value on the standard Normal density
# =============================================================================
def fig_ztest(z_obs=1.47):
    x = np.linspace(-4, 4, 801)
    f = stats.norm.pdf(x)
    p = 2 * stats.norm.sf(abs(z_obs))
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, f, color=MainBlue, lw=1.3, label='$N(0,1)$, law under $H_0$')
    for side in (-1, 1):
        m = side * x >= 1.96
        ax.fill_between(x[m], 0, f[m], color=IDAred, alpha=0.75, lw=0,
                        label='Rejection, 5%' if side == 1 else '_')
        m2 = side * x >= abs(z_obs)
        ax.fill_between(x[m2], 0, f[m2], color=Amber, alpha=0.35, lw=0,
                        label=f'$p$ = {p:.2f}' if side == 1 else '_')
    ax.axvline(z_obs, color=Navy, lw=1.0, ls='--', label=f'Observed $z$ = {z_obs:.2f}')
    ax.axvline(-z_obs, color=Navy, lw=0.6, ls=':')
    ax.set_xlim(-4, 4); ax.set_ylim(0, 0.45)
    ax.set_xlabel('$z = \\hat\\Delta / \\mathrm{SE}(\\hat\\Delta)$')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch4_sem_primer_ztest')
    return dict(p=round(p, 3))


# =============================================================================
# (8) precision of a Sharpe difference: annualised standard error against the correlation
# =============================================================================
def fig_se_rho(sr=0.2):
    rho = np.linspace(0, 0.995, 400)
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for T, c in [(120, IDAred), (240, MainBlue), (480, Forest)]:
        br = 2 - 2 * rho + 0.5 * (2 * sr ** 2 - 2 * sr ** 2 * rho ** 2)
        se = np.sqrt(12) * np.sqrt(br / T)
        ax.plot(rho, se, color=c, lw=1.3, label=f'$T$ = {T}')
        out[T] = round(float(np.sqrt(12) * np.sqrt((2 - 1 + 0.5 * (2 * sr ** 2 - 2 * sr ** 2 * 0.25)) / T)), 3)
    ax.plot(0.5, out[240], 'o', color=Navy, ms=3.5)
    ax.annotate(f'$\\rho$ = 0.5, $T$ = 240: {out[240]:.2f}', (0.5, out[240]), xytext=(-62, 12),
                textcoords='offset points', fontsize=ANN, color=Navy)
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.5)
    ax.set_xlabel('Correlation $\\rho$ of the two strategies')
    ax.set_ylabel('SE of $\\hat\\Delta$ (annual)')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch4_sem_primer_se_rho')
    return out


# =============================================================================
# (9) circular block bootstrap: blocks of consecutive months, resampled with wrap-around
# =============================================================================
def fig_block_bootstrap(T=24, b=4, starts=(19, 3, 11, 23, 3, 14)):
    """Circular block bootstrap, one resample drawn by hand: start months (1-based) of the T/b blocks."""
    cols = [MainBlue, IDAred, Forest, Amber, Navy, IDAred]
    first = {}
    for k, s in enumerate(starts):
        for j in range(b):
            first.setdefault((s - 1 + j) % T, k)
    fig, axes = plt.subplots(2, 1, figsize=(5.55, 1.5), sharex=True)
    ax = axes[0]
    for t in range(T):
        c = cols[first[t]] if t in first else BandBlue
        ax.add_patch(Rectangle((t, 0), 0.92, 1, color=c, lw=0))
        ax.text(t + 0.46, 0.5, str(t + 1), ha='center', va='center', fontsize=6.5,
                color='white' if t in first else Navy)
    ax.set_ylim(0, 1); ax.set_yticks([0.5]); ax.set_yticklabels(['Sample'])
    ax.set_title(f'Original months 1, ..., {T}; light: months not drawn in this resample', loc='left')
    ax = axes[1]
    pos = 0
    for k, s in enumerate(starts):
        for j in range(b):
            t = (s - 1 + j) % T
            ax.add_patch(Rectangle((pos, 0), 0.92, 1, color=cols[first[(s - 1) % T]], lw=0))
            ax.text(pos + 0.46, 0.5, str(t + 1), ha='center', va='center', fontsize=6.5, color='white')
            pos += 1
        if k < len(starts) - 1:
            ax.axvline(pos - 0.04, color=Navy, lw=1.0)
    ax.set_ylim(0, 1); ax.set_yticks([0.5]); ax.set_yticklabels(['Resample'])
    ax.set_xlim(0, T)
    ax.set_xticks([])
    ax.set_title(f'One resample: {T // b} random start months, $b$ = {b} consecutive months each, '
                 f'month {T} followed by month 1', loc='left')
    for a in axes:
        for sp in a.spines.values():
            sp.set_visible(False)
    fig.tight_layout(pad=0.3)
    save_fig(fig, 'ch4_sem_primer_block_bootstrap')
    return dict(starts=list(starts))


def fig_boot_dist(B=4999, T=240, seed=5, block=1):
    """Studentized bootstrap distribution of z* for a simulated pair of strategies (H0 true by centring)."""
    rng = np.random.default_rng(seed)
    C = np.array([[1, 0.7], [0.7, 1]]) * 0.04 ** 2
    X = np.array([0.006, 0.005]) + rng.multivariate_normal([0, 0], C, T) * (1 + 0.8 * rng.standard_t(4, (T, 1)) ** 2) ** 0.5 / 1.6

    def delta_se(Y):
        m, s = Y.mean(0), Y.std(0, ddof=1)
        d = m[0] / s[0] - m[1] / s[1]
        rho = np.corrcoef(Y.T)[0, 1]
        sr = m / s
        br = 2 - 2 * rho + 0.5 * (sr[0] ** 2 + sr[1] ** 2 - 2 * sr[0] * sr[1] * rho ** 2)
        return d, np.sqrt(br / len(Y))

    d0, se0 = delta_se(X)
    z0 = d0 / se0
    zs = np.empty(B)
    for k in range(B):
        idx = rng.integers(0, T, T)
        d, se = delta_se(X[idx])
        zs[k] = (d - d0) / se
    p = (1 + np.sum(np.abs(zs) >= abs(z0))) / (B + 1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.hist(zs, bins=60, density=True, color=BandBlue, edgecolor=MainBlue, lw=0.3,
            label='Bootstrap $z^*_m$')
    x = np.linspace(-4, 4, 400)
    ax.plot(x, stats.norm.pdf(x), color=Navy, lw=1.0, ls='--', label='$N(0,1)$')
    ax.axvline(z0, color=IDAred, lw=1.2, label=f'Observed $z$ = {z0:.2f}; $p$ = {p:.2f}')
    ax.axvline(-z0, color=IDAred, lw=0.7, ls=':')
    ax.set_xlim(-4, 4)
    ax.set_xlabel('$z^*$'); ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch4_sem_primer_boot_dist')
    return dict(z0=round(float(z0), 3), p=round(float(p), 3), p_norm=round(float(2 * stats.norm.sf(abs(z0))), 3))


# =============================================================================
# (10) shrinkage: eigenvalues of the sample, shrunk and true correlation matrices; Marchenko-Pastur band
# =============================================================================
def fig_shrinkage(N=20, T=60, rbar=0.3, delta=0.5, seed=8):
    rng = np.random.default_rng(seed)
    R = np.full((N, N), rbar); np.fill_diagonal(R, 1.0)
    L = np.linalg.cholesky(R)
    X = rng.standard_normal((T, N)) @ L.T
    S = np.corrcoef(X, rowvar=False)
    rb = (S.sum() - N) / (N * (N - 1))
    F = np.full((N, N), rb); np.fill_diagonal(F, 1.0)
    Sh = delta * F + (1 - delta) * S
    ev = lambda M: np.sort(np.linalg.eigvalsh(M))[::-1]
    e_true, e_s, e_sh = ev(R), ev(S), ev(Sh)
    c = N / T
    lo, hi = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    k = np.arange(1, N + 1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.axhspan(lo, hi, color=BandBlue, alpha=0.7, lw=0, label='Marchenko--Pastur band')
    ax.plot(k, e_s, 'o-', color=IDAred, ms=2.6, lw=0.9, label='Sample $\\mathbf{S}$')
    ax.plot(k, e_sh, 's-', color=Forest, ms=2.6, lw=0.9, label=f'Shrunk, $\\delta$ = {delta}')
    ax.plot(k, e_true, '--', color=Navy, lw=1.0, label='True matrix')
    ax.set_yscale('log')
    ax.set_yticks([0.1, 0.2, 0.5, 1, 2, 5]); ax.set_yticklabels(['0.1', '0.2', '0.5', '1', '2', '5'])
    ax.minorticks_off()
    ax.set_xlabel(f'Eigenvalue rank ($N$ = {N}, $T$ = {T})')
    ax.set_ylabel('Eigenvalue (log scale)')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch4_sem_primer_shrinkage')
    cond = lambda e: float(e[0] / e[-1])
    return dict(rbar=round(float(rb), 3), cond_true=round(cond(e_true), 1), cond_S=round(cond(e_s), 1),
                cond_sh=round(cond(e_sh), 1), band=(round(lo, 3), round(hi, 3)),
                smallest=(round(float(e_true[-1]), 3), round(float(e_s[-1]), 3), round(float(e_sh[-1]), 3)))


# =============================================================================
# (11) hierarchical clustering: correlation-based distance, single-linkage tree, ordered matrix
# =============================================================================
def fig_hrp():
    names = ['A', 'B', 'C', 'D', 'E', 'F']
    # two blocks of related assets and one loosely related asset
    R = np.array([[1.0, 0.8, 0.7, 0.2, 0.2, 0.1],
                  [0.8, 1.0, 0.75, 0.2, 0.25, 0.1],
                  [0.7, 0.75, 1.0, 0.3, 0.2, 0.15],
                  [0.2, 0.2, 0.3, 1.0, 0.7, 0.2],
                  [0.2, 0.25, 0.2, 0.7, 1.0, 0.25],
                  [0.1, 0.1, 0.15, 0.2, 0.25, 1.0]])
    perm = [3, 0, 5, 1, 4, 2]          # shown in a scrambled order, as data arrive
    Rp = R[np.ix_(perm, perm)]
    nm = [names[i] for i in perm]
    D = np.sqrt((1 - Rp) / 2)
    Dt = np.sqrt(((D[:, None, :] - D[None, :, :]) ** 2).sum(-1))
    Z = linkage(squareform(Dt, checks=False), method='single')
    fig, axes = plt.subplots(1, 3, figsize=FULL, gridspec_kw=dict(width_ratios=[1, 1.15, 1]))
    for ax, M, labs, ttl in [(axes[0], Rp, nm, 'Correlations, input order')]:
        ax.imshow(M, cmap='Blues', vmin=0, vmax=1)
        ax.set_xticks(range(6)); ax.set_xticklabels(labs); ax.set_yticks(range(6)); ax.set_yticklabels(labs)
        ax.set_title(ttl, loc='left')
        for i in range(6):
            for j in range(6):
                ax.text(j, i, f'{M[i, j]:.1f}'.replace('1.0', '1'), ha='center', va='center', fontsize=6.3,
                        color='white' if M[i, j] > 0.6 else Navy)
    dn = dendrogram(Z, labels=nm, ax=axes[1], color_threshold=0, above_threshold_color=MainBlue,
                    link_color_func=lambda k: MainBlue)
    axes[1].set_title('Single-linkage tree', loc='left')
    axes[1].set_ylabel('Merge distance $\\tilde d$')
    axes[1].tick_params(axis='x', labelsize=7)
    order = [nm.index(x) for x in dn['ivl']]
    Ro = Rp[np.ix_(order, order)]
    labs = dn['ivl']
    ax = axes[2]
    ax.imshow(Ro, cmap='Blues', vmin=0, vmax=1)
    ax.set_xticks(range(6)); ax.set_xticklabels(labs); ax.set_yticks(range(6)); ax.set_yticklabels(labs)
    ax.set_title('Same matrix, tree order', loc='left')
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f'{Ro[i, j]:.1f}'.replace('1.0', '1'), ha='center', va='center', fontsize=6.3,
                    color='white' if Ro[i, j] > 0.6 else Navy)
    fig.tight_layout(pad=0.3)
    save_fig(fig, 'ch4_sem_primer_hrp')
    return dict(order=labs, merges=np.round(Z[:, 2], 3).tolist())


def run_all():
    res = {}
    res['two_asset'] = fig_two_asset()
    res['frontier'] = fig_frontier()
    res['estimation_error'] = fig_estimation_error()
    res['risk_shares'] = fig_risk_shares()
    res['rolling'] = fig_rolling()
    res['costs'] = fig_costs()
    res['ztest'] = fig_ztest()
    res['se_rho'] = fig_se_rho()
    res['block_bootstrap'] = fig_block_bootstrap()
    res['boot_dist'] = fig_boot_dist()
    res['shrinkage'] = fig_shrinkage()
    res['hrp'] = fig_hrp()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

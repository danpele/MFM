"""
seminar18_explainers.py -- Explanatory (primer) charts for Seminar 18 (MFM): systemic risk and networks
=======================================================================================================
Teaching charts for the primer slides "Prerequisites for Today" / "Noțiuni necesare azi" of Seminar 18,
which takes place BEFORE Lecture 18. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (CoVaR and quantile regression, the check function, MES, SRISK and leverage, Parkinson volatility,
impulse responses and variance decompositions, a connectedness table and its network, the block bootstrap,
Holm and Wald tests) and contain no exercise answers.

Output: charts/ch18_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_18/seminar18_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch, Circle
from scipy import stats
from scipy.signal import lfilter
import statsmodels.api as sm

# course palette (no grey)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'
BandBlue = '#C5D2E8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

# drawn at the size of their box on the slide (full width: 5.67 x 1.95 in; one column: 2.75 x 2.4 in),
# so that 1 pt in the figure is about 1 pt on the slide: texts 7-7.5 pt, never below 6.5 pt
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'lines.markersize': 3.5, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.size': 2.5,
                     'ytick.major.size': 2.5, 'axes.titlepad': 3, 'axes.labelpad': 2, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy})

FULL = (5.6, 1.55)    # full slide width
HALF = (2.75, 1.85)   # half slide width (two-column layout)


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
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False,
               handlelength=1.6, columnspacing=1.2, handletextpad=0.5, borderaxespad=0.2)


def simulate_garch(T, omega=0.05, a=0.10, b=0.85, seed=11, burn=500):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(T + burn)
    r = np.empty(T + burn)
    s2 = omega / (1 - a - b)
    for t in range(T + burn):
        r[t] = np.sqrt(s2) * e[t]
        s2 = omega + a * r[t] ** 2 + b * s2
    return r[burn:]


# =============================================================================
# (i) CoVaR: quantile regression on a simulated bank--system scatter, and the two conditional densities
# =============================================================================
def fig_covar(seed=18, n=4000, s_i=2.0, s_sys=1.0, rho=0.55, alpha=0.05):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, 2))
    xi = s_i * z[:, 0]
    xs = s_sys * (rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1])
    X = sm.add_constant(xi)
    a5, b5 = sm.QuantReg(xs, X).fit(q=alpha).params
    q5, q50 = np.quantile(xi, alpha), np.quantile(xi, 0.5)
    covar = -(a5 + b5 * q5)
    covar50 = -(a5 + b5 * q50)
    dcovar = b5 * (q50 - q5)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(xi, xs, 'o', color=MainBlue, ms=1.0, alpha=0.35, mew=0)
    xx = np.linspace(-7, 7, 50)
    ax.plot(xx, a5 + b5 * xx, color=IDAred, lw=1.6, label=r'5% line $\hat a + \hat b X_i$')
    ax.axvline(q5, color=Amber, lw=1.0, ls='--', label=r'distress $\hat q_{5\%}(X_i)$')
    ax.axvline(q50, color=Forest, lw=1.0, ls='--', label=r'median $\hat q_{50\%}(X_i)$')
    ax.plot(q5, -covar, 'o', color=IDAred, ms=4, zorder=5)
    ax.plot(q50, -covar50, 'o', color=Forest, ms=4, zorder=5)
    ax.annotate('', xy=(q50 + 0.25, -covar), xytext=(q50 + 0.25, -covar50),
                arrowprops=dict(arrowstyle='<->', color=Navy, lw=1.1))
    ax.plot([q5, q50 + 0.25], [-covar, -covar], color=Navy, lw=0.6, ls=':')
    ax.annotate(r'$\Delta$CoVaR', xy=(q50 + 0.35, -0.5 * (covar + covar50)), xytext=(q50 + 1.6, -3.75),
                color=Navy, fontsize=7, va='center', arrowprops=dict(arrowstyle='->', color=Navy, lw=0.8))
    ax.set_xlim(-7, 7); ax.set_ylim(-4.5, 4)
    ax.set_xlabel('Bank return $X_i$ (%)')
    ax.set_ylabel('System return $X^{sys}$ (%)')
    ax.set_title('Quantile regression at 5%', loc='left')
    # right: conditional densities (Normal theory, true parameters)
    ax = axes[1]
    y = np.linspace(-5, 3.5, 600)
    sc = s_sys * np.sqrt(1 - rho ** 2)
    out = {}
    for x0, col, lab in ((0.0, Forest, r'$X^{sys}$ | median'), (s_i * stats.norm.ppf(alpha), IDAred,
                                                                    r'$X^{sys}$ | distress')):
        m = rho * s_sys / s_i * x0
        f = stats.norm.pdf(y, m, sc)
        qq = m + sc * stats.norm.ppf(alpha)
        out[lab] = -qq
        ax.plot(y, f, color=col, lw=1.5, label=lab)
        k = y <= qq
        ax.fill_between(y[k], 0, f[k], color=col, alpha=0.35, lw=0)
        ax.axvline(qq, color=col, lw=0.9, ls='--')
    q_lo, q_hi = -max(out.values()), -min(out.values())
    ax.annotate('', xy=(q_lo, 0.52), xytext=(q_hi, 0.52), arrowprops=dict(arrowstyle='<->', color=Navy, lw=1.1))
    ax.text(0.5 * (q_lo + q_hi), 0.55, r'$\Delta$CoVaR', ha='center', color=Navy, fontsize=7)
    ax.set_ylim(0, 0.62)
    ax.set_xlabel('System return $X^{sys}$ (%)')
    ax.set_ylabel('Conditional density')
    ax.set_title('5% tails shaded', loc='left')
    bottom_legend(fig, axes, ncol=5)
    save_fig(fig, 'ch18_sem_primer_covar')
    return dict(b5=float(b5), q5=float(q5), q50=float(q50), covar=float(covar), covar50=float(covar50),
                dcovar=float(dcovar), dcovar_theory=float(rho * s_sys * -stats.norm.ppf(alpha)))


# =============================================================================
# (ii) the check function and why its expected value is minimised at the quantile
# =============================================================================
def fig_check(alphas=(0.05, 0.5)):
    cols = {0.05: IDAred, 0.5: MainBlue}
    u = np.linspace(-3, 3, 601)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    for a in alphas:
        ax.plot(u, u * (a - (u < 0)), color=cols[a], lw=1.6, label=rf'$\alpha$ = {a:g}')
    ax.axhline(0, color=Navy, lw=0.5); ax.axvline(0, color=Navy, lw=0.5)
    ax.text(-1.5, 2.25, r'slope $\alpha - 1$', color=IDAred, fontsize=7)
    ax.text(0.9, 0.42, r'slope $\alpha$', color=IDAred, fontsize=7)
    ax.set_xlabel('Residual $u$')
    ax.set_ylabel(r'$\rho_\alpha(u)$')
    ax.set_title('Check function', loc='left')
    ax = axes[1]
    q = np.linspace(-3, 2, 401)
    xg = np.linspace(-8, 8, 4001)
    w = stats.norm.pdf(xg) * (xg[1] - xg[0])
    for a in alphas:
        el = np.array([np.sum(w * (xg - qq) * (a - (xg - qq < 0))) for qq in q])
        ax.plot(q, el, color=cols[a], lw=1.6)
        qa = stats.norm.ppf(a)
        ax.plot(qa, np.interp(qa, q, el), 'o', color=cols[a], ms=4)
        ax.annotate(rf'$z_{{{a:g}}}$ = {qa:.2f}', (qa, np.interp(qa, q, el)),
                    xytext=(12, -16) if a == 0.5 else (-6, 16), textcoords='offset points', fontsize=7,
                    color=cols[a], ha='left' if a == 0.5 else 'center')
    ax.set_ylim(0, 1.35)
    ax.set_xlabel('Candidate value $q$')
    ax.set_ylabel(r'$E[\rho_\alpha(X - q)]$')
    ax.set_title(r'$X \sim N(0,1)$: expected loss', loc='left')
    bottom_legend(fig, axes[0], ncol=2)
    save_fig(fig, 'ch18_sem_primer_check')


# =============================================================================
# (iii) MES: the bank's average return on the market's worst 5% days
# =============================================================================
def fig_mes(seed=7, n=2500, beta=1.2, s_m=1.0, s_e=1.0, alpha=0.05):
    rng = np.random.default_rng(seed)
    xm = s_m * rng.standard_normal(n)
    xi = beta * xm + s_e * rng.standard_normal(n)
    qm = np.quantile(xm, alpha)
    tail = xm <= qm
    mes = -xi[tail].mean()
    es = -xm[tail].mean()
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(xm[~tail], xi[~tail], 'o', color=MainBlue, ms=1.2, alpha=0.35, mew=0, label='Other days')
    ax.plot(xm[tail], xi[tail], 'o', color=IDAred, ms=1.8, alpha=0.8, mew=0, label="market's worst 5%")
    ax.axvline(qm, color=IDAred, lw=1.0, ls='--', label=rf'$q_{{5\%}}(X_m)$ = {qm:.2f}%')
    ax.plot([-4.2, qm], [-mes, -mes], color=Navy, lw=1.6, label=rf'Mean of $X_i$ on those days = $-$MES')
    ax.annotate(f'MES = {mes:.2f}%', xy=(-3.4, -mes), xytext=(-4.0, 4.6), fontsize=7, color=Navy,
                arrowprops=dict(arrowstyle='->', color=Navy, lw=0.9))
    ax.set_xlim(-4.2, 4); ax.set_ylim(-8, 8)
    ax.set_xlabel('Market return $X_m$ (%)')
    ax.set_ylabel('Bank return $X_i$ (%)')
    handles = [Line2D([], [], color=MainBlue, marker='o', ls='', ms=5, alpha=0.6),
               Line2D([], [], color=IDAred, marker='o', ls='', ms=5),
               Line2D([], [], color=IDAred, ls='--'), Line2D([], [], color=Navy, lw=1.6)]
    bottom_legend(fig, ncol=2, handles=handles,
                  labels=['other days', "market's worst 5%", rf'$q_{{5\%}}(X_m)$ = {qm:.2f}%',
                          r'mean of $X_i$ there = $-$MES'])
    save_fig(fig, 'ch18_sem_primer_mes')
    return dict(mes=float(mes), es=float(es), beta_es=float(beta * es))


# =============================================================================
# (iv) SRISK per unit of equity as a function of leverage; zero at L*
# =============================================================================
def fig_srisk(k=0.08, lrmes=(0.2, 0.3, 0.5)):
    L = np.linspace(1, 20, 400)
    cols = [Forest, Amber, IDAred]
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for lr, c in zip(lrmes, cols):
        s = k * (L - 1) - (1 - k) * (1 - lr)          # SRISK / W, with D = (L - 1) W
        Ls = 1 + (1 - k) * (1 - lr) / k
        out[lr] = Ls
        ax.plot(L, s, color=c, lw=1.6, label=f'LRMES {100 * lr:.0f}%: $L^*$ = {Ls:.1f}')
        ax.plot(Ls, 0, 'o', color=c, ms=4)
    ax.axhline(0, color=Navy, lw=0.8)
    ax.fill_between(L, 0, 0.75, color=BandBlue, alpha=0.6, lw=0)
    ax.text(1.6, 0.6, 'capital shortfall', color=Navy, fontsize=7)
    ax.text(12.5, -0.62, 'surplus', color=Navy, fontsize=7)
    ax.set_xlim(1, 20); ax.set_ylim(-0.8, 0.75)
    ax.set_xlabel('Leverage $L = (D + W)/W$')
    ax.set_ylabel('SRISK / $W$')
    ax.set_title('$k$ = 8%', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch18_sem_primer_srisk')
    return out


# =============================================================================
# (v) Parkinson volatility from the daily range, and why it is used in logs
# =============================================================================
def fig_parkinson(seed=5, days=500, m=390):
    rng = np.random.default_rng(seed)
    # log-volatility AR(1) (annualised, %): stochastic volatility path
    h = np.empty(days)
    h[0] = np.log(25)
    for t in range(1, days):
        h[t] = np.log(25) + 0.97 * (h[t - 1] - np.log(25)) + 0.12 * rng.standard_normal()
    sig = np.exp(h)                                      # annualised volatility, %
    sd_day = sig / 100 / np.sqrt(252)
    paths = np.cumsum(rng.standard_normal((days, m)) * (sd_day[:, None] / np.sqrt(m)), axis=1)
    paths = np.concatenate([np.zeros((days, 1)), paths], axis=1)
    rng_ = paths.max(1) - paths.min(1)                  # ln H - ln L
    park = 100 * np.sqrt(252 * rng_ ** 2 / (4 * np.log(2)))
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(park, color=MainBlue, lw=0.6, label=r'Parkinson $\hat\sigma_t$')
    ax.plot(sig, color=IDAred, lw=1.4, label=r'true $\sigma_t$')
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Volatility (% p.a.)')
    ax.set_title('Noisy, right-skewed in levels', loc='left')
    ax = axes[1]
    for x, col, lab in ((park, Amber, r'$\hat\sigma_t$ std.'), (np.log(park), Forest, r'$\ln\hat\sigma_t$ std.')):
        zz = (x - x.mean()) / x.std()
        ax.hist(zz, bins=np.linspace(-4, 5, 37), density=True, color=col, alpha=0.55, label=lab)
    g = np.linspace(-4, 5, 300)
    ax.plot(g, stats.norm.pdf(g), color=Navy, lw=1.3, ls='--', label='Normal')
    ax.set_xlim(-4, 5)
    ax.set_xlabel('Standardised value')
    ax.set_ylabel('Density')
    ax.set_title('Logs: nearly symmetric', loc='left')
    bottom_legend(fig, axes, ncol=5)
    save_fig(fig, 'ch18_sem_primer_parkinson')
    sk = lambda x: float(stats.skew(x))
    return dict(skew_level=sk(park), skew_log=sk(np.log(park)), corr=float(np.corrcoef(np.log(park), h)[0, 1]))


# =============================================================================
# VAR helpers: moving-average matrices, generalized and Cholesky decompositions
# =============================================================================
def ma_matrices(A, H):
    N = A.shape[0]
    Phi = [np.eye(N)]
    for _ in range(1, H):
        Phi.append(A @ Phi[-1])
    return Phi


def gfevd(A, S, H):
    Phi = ma_matrices(A, H)
    num = sum((P @ S) ** 2 for P in Phi) / np.diag(S)[None, :]
    den = sum(np.diag(P @ S @ P.T) for P in Phi)
    return num / den[:, None]


def chol_fevd(A, S, H, order):
    o = np.array(order)
    P_ = np.linalg.cholesky(S[np.ix_(o, o)])
    Pm = np.zeros_like(S)
    Pm[np.ix_(o, o)] = P_
    Phi = ma_matrices(A, H)
    num = sum((P @ Pm) ** 2 for P in Phi)
    den = sum(np.diag(P @ S @ P.T) for P in Phi)
    # column j of Pm is the orthogonalised shock of variable j (placed at position order.index(j))
    return num / den[:, None]


# =============================================================================
# (vi) impulse responses and the variance decomposition of a bivariate VAR(1): generalized against Cholesky
# =============================================================================
def fig_irf(A=((0.7, 0.1), (0.2, 0.6)), S=((1.0, 0.4), (0.4, 1.0)), Hmax=15):
    A, S = np.array(A), np.array(S)
    Phi = ma_matrices(A, Hmax)
    h = np.arange(Hmax)
    g = np.array([(P @ S[:, 0]) / np.sqrt(S[0, 0]) for P in Phi])        # generalized shock to variable 1
    P12 = np.linalg.cholesky(S)                                           # order (1, 2)
    c1 = np.array([P @ P12[:, 0] for P in Phi])
    P21 = np.linalg.cholesky(S[::-1, ::-1])[::-1, ::-1]                  # order (2, 1): variable 2 first
    c2 = np.array([P @ P21[:, 0] for P in Phi])
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(h, g[:, 1], 'o-', color=IDAred, lw=2.6, ms=4, label='Generalized')
    ax.plot(h, c1[:, 1], 's--', color=MainBlue, lw=1.2, ms=3.0, label='Cholesky, variable 1 first')
    ax.plot(h, c2[:, 1], '^-', color=Amber, lw=1.2, ms=3.2, label='Cholesky, variable 2 first')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Horizon $h$ (days)')
    ax.set_ylabel('Response of $y_2$')
    ax.set_title('Response of $y_2$ to a shock in $y_1$', loc='left')
    ax = axes[1]
    Hs = np.arange(1, Hmax + 1)
    gen = [gfevd(A, S, H) for H in Hs]
    gen = [t / t.sum(1, keepdims=True) for t in gen]
    ch1 = [chol_fevd(A, S, H, (0, 1)) for H in Hs]
    ch2 = [chol_fevd(A, S, H, (1, 0)) for H in Hs]
    ax.plot(Hs, [100 * t[1, 0] for t in gen], 'o-', color=IDAred, lw=1.4, ms=3.5)
    ax.plot(Hs, [100 * t[1, 0] for t in ch1], 's-', color=MainBlue, lw=1.2, ms=3.2)
    ax.plot(Hs, [100 * t[1, 0] for t in ch2], '^-', color=Amber, lw=1.2, ms=3.2)
    ax.set_ylim(0, 60)
    ax.set_xlabel('Horizon $H$ (days)')
    ax.set_ylabel(r'Share $\theta_{21}(H)$ (%)')
    ax.set_title('Share of $y_2$ due to $y_1$', loc='left')
    bottom_legend(fig, axes[0], ncol=3)
    save_fig(fig, 'ch18_sem_primer_irf')
    return dict(gen_H10=float(100 * gen[9][1, 0]), ch1_H10=float(100 * ch1[9][1, 0]), ch2_H10=float(100 * ch2[9][1, 0]))


# =============================================================================
# (vii) a connectedness table (4 banks) and the network of net pairwise spillovers
# =============================================================================
def fig_network(H=10):
    A = np.array([[0.55, 0.00, 0.00, 0.00],
                  [0.25, 0.50, 0.00, 0.05],
                  [0.20, 0.10, 0.45, 0.00],
                  [0.05, 0.00, 0.20, 0.50]])
    S = np.array([[1.0, 0.5, 0.4, 0.3],
                  [0.5, 1.0, 0.4, 0.3],
                  [0.4, 0.4, 1.0, 0.3],
                  [0.3, 0.3, 0.3, 1.0]])
    th = gfevd(A, S, H)
    tt = th / th.sum(1, keepdims=True)
    N = len(A)
    F = tt.sum(1) - np.diag(tt)
    T_ = tt.sum(0) - np.diag(tt)
    net = T_ - F
    C = 100 * (tt.sum() - np.trace(tt)) / N
    names = ['Bank 1', 'Bank 2', 'Bank 3', 'Bank 4']
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 1.8), gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax = axes[0]
    M = np.zeros((N + 1, N + 1))
    M[:N, :N] = 100 * tt
    ax.imshow(np.where(np.eye(N + 1, dtype=bool) | (np.arange(N + 1)[:, None] == N) |
                       (np.arange(N + 1)[None, :] == N), np.nan, M), cmap='Blues', vmin=0, vmax=45, aspect='auto')
    for i in range(N):
        for j in range(N):
            ax.text(j, i, f'{100 * tt[i, j]:.0f}', ha='center', va='center', fontsize=7,
                    color='white' if (i != j and 100 * tt[i, j] > 25) else Navy)
        ax.text(N, i, f'{100 * F[i]:.0f}', ha='center', va='center', fontsize=7, color=IDAred)
        ax.text(i, N, f'{100 * T_[i]:.0f}', ha='center', va='center', fontsize=7, color=Forest)
    ax.text(N, N, f'C {C:.0f}', ha='center', va='center', fontsize=7, color=Navy)
    ax.set_xticks(range(N + 1)); ax.set_xticklabels(['1', '2', '3', '4', 'From'])
    ax.set_yticks(range(N + 1)); ax.set_yticklabels(['1', '2', '3', '4', 'To'])
    ax.set_xlabel('Shock in bank $j$')
    ax.set_ylabel('Variance of bank $i$')
    ax.set_title(r'$100\,\tilde\theta_{ij}(10)$ (%)', loc='left')
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axhline(N - 0.5, color=Navy, lw=0.8); ax.axvline(N - 0.5, color=Navy, lw=0.8)
    ax = axes[1]
    ang = np.pi / 2 - np.arange(N) * 2 * np.pi / N
    pos = np.c_[np.cos(ang), np.sin(ang)]
    for i in range(N):
        for j in range(N):
            d = tt[i, j] - tt[j, i]           # j -> i, net
            if j != i and d > 0.02:
                a = FancyArrowPatch(pos[j], pos[i], arrowstyle='-|>', mutation_scale=8,
                                    lw=0.5 + 15 * d, color=Navy, shrinkA=10, shrinkB=10,
                                    connectionstyle='arc3,rad=0.22', zorder=1)
                ax.add_patch(a)
    for i in range(N):
        col = IDAred if net[i] > 0 else MainBlue
        ax.add_patch(Circle(pos[i], 0.26, color=col, alpha=0.9, zorder=2))
        ax.text(pos[i, 0], pos[i, 1], f'{i + 1}', ha='center', va='center', color='white', fontsize=7,
                zorder=3, fontweight='bold')
        lx, ly = (pos[i, 0] * 1.78, pos[i, 1]) if abs(pos[i, 0]) > 0.5 else (pos[i, 0] + 0.62, pos[i, 1])
        ax.text(lx, ly, f'net\n{100 * net[i]:+.0f}', ha='center', va='center', fontsize=7, color=col,
                linespacing=0.9)
    ax.set_xlim(-2.15, 2.15); ax.set_ylim(-2.0, 2.0)
    ax.set_aspect('equal', adjustable='datalim'); ax.axis('off')
    ax.set_title('Net pairwise spillovers', loc='left')
    handles = [Patch(color=IDAred), Patch(color=MainBlue), Line2D([], [], color=Navy, lw=1.5, marker='>')]
    bottom_legend(fig, ncol=3, handles=handles,
                  labels=['Net transmitter ($T_i - F_i > 0$)', 'Net receiver', r'Arrow $j \to i$: $\tilde\theta_{ij} > \tilde\theta_{ji}$'])
    save_fig(fig, 'ch18_sem_primer_network')
    return dict(C=float(C), net=(100 * net).round(1).tolist(), F=(100 * F).round(1).tolist(),
                T=(100 * T_).round(1).tolist())


# =============================================================================
# (viii) the moving-block bootstrap against the i.i.d. bootstrap on a series with volatility clustering
# =============================================================================
def _acf(x, K):
    x = x - x.mean()
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, K + 1)])


def fig_bootstrap(T=2000, ell=20, B=999, K=30, seed=3):
    r = simulate_garch(T, omega=0.04, a=0.12, b=0.86, seed=seed)
    rng = np.random.default_rng(seed + 100)
    nb = int(np.ceil(T / ell))

    def block(rng):
        st = rng.integers(0, T - ell + 1, nb)
        return np.concatenate([r[s:s + ell] for s in st])[:T]

    def iid(rng):
        return r[rng.integers(0, T, T)]

    stat = lambda x: np.std(x, ddof=1)
    qb = np.array([stat(block(rng)) for _ in range(B)])
    qi = np.array([stat(iid(rng)) for _ in range(B)])
    acf_o = _acf(np.abs(r), K)
    acf_b = np.mean([_acf(np.abs(block(rng)), K) for _ in range(100)], axis=0)
    acf_i = np.mean([_acf(np.abs(iid(rng)), K) for _ in range(100)], axis=0)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    lags = np.arange(1, K + 1)
    ax.plot(lags, acf_o, 'o-', color=Navy, lw=1.2, ms=3, label='original')
    ax.plot(lags, acf_b, 's-', color=Forest, lw=1.2, ms=3, label=f'block bootstrap ($\\ell$ = {ell})')
    ax.plot(lags, acf_i, '^-', color=Amber, lw=1.2, ms=3, label='i.i.d. bootstrap')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Lag $k$ (days)')
    ax.set_ylabel(r'ACF of $|r_t|$')
    ax.set_title('Clustering kept by blocks', loc='left')
    ax = axes[1]
    bins = np.linspace(min(qb.min(), qi.min()), max(qb.max(), qi.max()), 30)
    ax.hist(qi, bins=bins, color=Amber, alpha=0.6, density=True)
    ax.hist(qb, bins=bins, color=Forest, alpha=0.5, density=True)
    for x, col in ((qi, Amber), (qb, Forest)):
        lo, hi = np.quantile(x, [0.025, 0.975])
        for v in (lo, hi):
            ax.axvline(v, color=col, lw=1.2, ls='--')
    ax.axvline(stat(r), color=IDAred, lw=1.4, label='sample estimate')
    ax.set_xlabel(r'Bootstrap standard deviation $\hat\sigma^*$ (%)')
    ax.set_ylabel('Density')
    ax.set_title('95% percentile intervals (dashed)', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch18_sem_primer_bootstrap')
    return dict(est=float(stat(r)), block_ci=np.quantile(qb, [0.025, 0.975]).round(3).tolist(),
                iid_ci=np.quantile(qi, [0.025, 0.975]).round(3).tolist(),
                block_sd=float(qb.std()), iid_sd=float(qi.std()))


# =============================================================================
# (ix) Holm's step-down thresholds and the chi-squared reference distribution of a Wald test
# =============================================================================
def fig_tests(m=15, seed=12, W=8.0, df=5):
    rng = np.random.default_rng(seed)
    # 4 false nulls (small p-values) and 11 true nulls (uniform p-values)
    p = np.sort(np.r_[rng.uniform(0, 0.012, 4), rng.uniform(0, 1, m - 4)])
    k = np.arange(1, m + 1)
    holm = 0.05 / (m - k + 1)
    rej = np.zeros(m, bool)
    for i in range(m):
        if p[i] <= holm[i]:
            rej[i] = True
        else:
            break
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(k, holm, 'o--', color=IDAred, lw=1.2, ms=3.5, label=r'Holm $0.05/(m-k+1)$')
    ax.axhline(0.05, color=Amber, lw=1.2, ls=':', label='0.05')
    ax.plot(k[rej], p[rej], 'o', color=Forest, ms=4.5, label='Rejected')
    ax.plot(k[~rej], p[~rej], 'o', color=MainBlue, ms=5, mfc='none', mew=1.2, label='Not rejected')
    ax.set_yscale('log'); ax.set_ylim(1e-4, 1.2)
    ax.set_xticks([1, 5, 10, 15])
    ax.set_xlabel('Rank $k$ of the $p$-value')
    ax.set_ylabel('$p_{(k)}$ (log scale)')
    ax.set_title(f'Holm, $m$ = {m} tests', loc='left')
    ax = axes[1]
    x = np.linspace(0, 22, 500)
    f = stats.chi2.pdf(x, df)
    crit = stats.chi2.ppf(0.95, df)
    ax.plot(x, f, color=MainBlue, lw=1.6, label=rf'$\chi^2_{df}$ density')
    m_ = x >= crit
    ax.fill_between(x[m_], 0, f[m_], color=IDAred, alpha=0.55, lw=0, label=f'5% region $W$ > {crit:.2f}')
    m2 = x >= W
    ax.fill_between(x[m2], 0, f[m2], color=BandBlue, alpha=0.6, lw=0)
    ax.axvline(W, color=Navy, lw=1.2, ls='--', label=f'$W$ = {W:.1f}: $p$ = {stats.chi2.sf(W, df):.3f}')
    ax.set_xlim(0, 22); ax.set_ylim(0, 0.17)
    ax.set_xlabel('Wald statistic $W$')
    ax.set_ylabel('Density')
    ax.set_title(f'Reference distribution, {df} restrictions', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch18_sem_primer_tests')
    return dict(p=p.round(4).tolist(), n_rej=int(rej.sum()), n_raw=int((p <= 0.05).sum()), crit=float(crit),
                pW=float(stats.chi2.sf(W, df)))


def run_all():
    res = {}
    res['covar'] = fig_covar()
    fig_check()
    res['mes'] = fig_mes()
    res['srisk'] = fig_srisk()
    res['parkinson'] = fig_parkinson()
    res['irf'] = fig_irf()
    res['network'] = fig_network()
    res['bootstrap'] = fig_bootstrap()
    res['tests'] = fig_tests()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

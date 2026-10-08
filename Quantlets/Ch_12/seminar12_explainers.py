"""
seminar12_explainers.py -- Explanatory (primer) charts for Seminar 12 (MFM): options and the volatility surface
==============================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 12,
which takes place BEFORE Lecture 12. All charts use SIMULATED or textbook (Black--Scholes) inputs only, with
fixed seeds and parameters different from those of the exercises: they illustrate the concepts (pay-offs,
convexity in the strike and the risk-neutral density, the Greeks, delta hedging, the binomial tree, implied
volatility by Newton's method, the SVI smile, the variance strip, the variance risk premium, overlapping
windows, the joint Wald test, the QLIKE loss) and contain no exercise answers.

Output: charts/ch12_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_12/seminar12_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
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
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'lines.linewidth': 1.0, 'legend.handlelength': 1.6,
                     'legend.columnspacing': 1.2})

FULL = (5.6, 1.6)     # full slide width, chart above the bullets
HALF = (2.75, 2.1)    # one column of a two-column slide


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


# Black--Scholes (no dividends)
def bs_d(S, K, tau, r, sig):
    d1 = (np.log(S / K) + (r + 0.5 * sig ** 2) * tau) / (sig * np.sqrt(tau))
    return d1, d1 - sig * np.sqrt(tau)


def bs_call(S, K, tau, r, sig):
    d1, d2 = bs_d(S, K, tau, r, sig)
    return S * stats.norm.cdf(d1) - K * np.exp(-r * tau) * stats.norm.cdf(d2)


def bs_put(S, K, tau, r, sig):
    return bs_call(S, K, tau, r, sig) - S + K * np.exp(-r * tau)


def bs_vega(S, K, tau, r, sig):
    d1, _ = bs_d(S, K, tau, r, sig)
    return S * stats.norm.pdf(d1) * np.sqrt(tau)


# =============================================================================
# 1. pay-offs at expiry
# =============================================================================
def fig_payoffs(K=100.0):
    ST = np.linspace(60, 140, 401)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(ST, np.maximum(ST - K, 0), color=MainBlue, lw=2.2, label=r'Call $(S_T - K)^+$', zorder=1)
    ax.plot(ST, np.maximum(K - ST, 0), color=IDAred, lw=1.4, label=r'Put $(K - S_T)^+$')
    ax.plot(ST, ST - K, color=Forest, lw=1.0, ls='--', label=r'Call $-$ put $= S_T - K$')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.axvline(K, color=Amber, lw=0.8, ls=':')
    ax.text(K + 1.5, 33, r'$K = 100$', color=Amber, fontsize=7)
    ax.set_xlabel(r'Price at expiry $S_T$')
    ax.set_ylabel('Pay-off at expiry')
    ax.set_ylim(-42, 42)
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch12_sem_primer_payoffs')


# =============================================================================
# 2. convexity in the strike and the risk-neutral density (butterflies)
# =============================================================================
def fig_butterfly(S=100.0, tau=0.5, r=0.02, sig=0.30, h=5.0):
    K = np.linspace(40, 200, 801)
    C = bs_call(S, K, tau, r, sig)
    # log-normal risk-neutral density of S_T
    mu = np.log(S) + (r - 0.5 * sig ** 2) * tau
    s = sig * np.sqrt(tau)
    q = stats.lognorm.pdf(K, s=s, scale=np.exp(mu))
    Kb = np.arange(50, 196, h)
    bfly = bs_call(S, Kb - h, tau, r, sig) - 2 * bs_call(S, Kb, tau, r, sig) + bs_call(S, Kb + h, tau, r, sig)
    qb = np.exp(r * tau) * bfly / h ** 2
    fig, axes = plt.subplots(2, 1, figsize=(2.75, 2.35), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.15]))
    ax = axes[0]
    ax.plot(K, C, color=MainBlue, lw=1.3, label=r'Call price $C(K)$')
    k1, k3 = 90.0, 130.0
    ax.plot([k1, k3], bs_call(S, np.array([k1, k3]), tau, r, sig), color=IDAred, lw=1.0, ls='--',
            label='Chord: convexity')
    ax.set_ylabel('$C(K)$')
    ax = axes[1]
    ax.bar(Kb, qb, width=h * 0.8, color=BandBlue, edgecolor=MainBlue, lw=0.4,
           label=r'Butterflies $e^{r\tau}\Delta^2 C/h^2$')
    ax.plot(K, q, color=IDAred, lw=1.2, label=r'Density $q(K)$')
    ax.set_xlabel('Strike $K$')
    ax.set_ylabel('$q(K)$')
    ax.set_xlim(40, 200)
    bottom_legend(fig, axes, ncol=1)
    save_fig(fig, 'ch12_sem_primer_butterfly')


# =============================================================================
# 3. price and Greeks of a call as functions of S
# =============================================================================
def fig_greeks(K=100.0, r=0.02, sig=0.30):
    S = np.linspace(60, 140, 401)
    fig, axes = plt.subplots(1, 4, figsize=FULL)
    taus = [(1.0, MainBlue, r'$\tau = 1$ year'), (0.25, IDAred, r'$\tau = 3$ months'),
            (1 / 52, Forest, r'$\tau = 1$ week')]
    for tau, col, lab in taus:
        d1, d2 = bs_d(S, K, tau, r, sig)
        axes[0].plot(S, bs_call(S, K, tau, r, sig), color=col, lw=1.0, label=lab)
        axes[1].plot(S, stats.norm.cdf(d1), color=col, lw=1.0)
        axes[2].plot(S, stats.norm.pdf(d1) / (S * sig * np.sqrt(tau)), color=col, lw=1.0)
        axes[3].plot(S, S * stats.norm.pdf(d1) * np.sqrt(tau) / 100, color=col, lw=1.0)
    axes[0].plot(S, np.maximum(S - K, 0), color=Navy, lw=0.8, ls=':', label='Pay-off $(S - K)^+$')
    titles = ['Price $C$', r'Delta $\Delta = \Phi(d_1)$', r'Gamma $\Gamma$', r'Vega per vol point']
    for ax, t in zip(axes, titles):
        ax.set_title(t, loc='left')
        ax.axvline(K, color=Amber, lw=0.6, ls=':')
        ax.set_xlabel('$S$')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch12_sem_primer_greeks')


# =============================================================================
# 4. delta hedging: distribution of the hedging error for few and many rebalancing dates
# =============================================================================
def hedge_errors(N, n_paths=20000, S0=100.0, K=100.0, T=1.0, r=0.03, mu=0.07, sig=0.30, seed=7):
    rng = np.random.default_rng(seed)
    dt = T / N
    S = np.full(n_paths, S0)
    prem = bs_call(S0, K, T, r, sig)
    d1, _ = bs_d(S, K, T, r, sig)
    delta = stats.norm.cdf(d1)
    cash = prem - delta * S
    for i in range(1, N + 1):
        z = rng.standard_normal(n_paths)
        S = S * np.exp((mu - 0.5 * sig ** 2) * dt + sig * np.sqrt(dt) * z)
        cash = cash * np.exp(r * dt)
        tau = T - i * dt
        if i < N:
            d1, _ = bs_d(S, K, tau, r, sig)
            new = stats.norm.cdf(d1)
            cash -= (new - delta) * S
            delta = new
    return delta * S + cash - np.maximum(S - K, 0), prem


def fig_hedge():
    e4, prem = hedge_errors(4)
    e52, _ = hedge_errors(52)
    fig, ax = plt.subplots(figsize=HALF)
    bins = np.linspace(-15, 15, 61)
    ax.hist(e4, bins=bins, density=True, color=BandBlue, edgecolor=MainBlue, lw=0.3,
            label=f'$N = 4$ (quarterly), s.d. {e4.std():.2f}')
    ax.hist(e52, bins=bins, density=True, histtype='step', color=IDAred, lw=1.1,
            label=f'$N = 52$ (weekly), s.d. {e52.std():.2f}')
    ax.axvline(0, color=Navy, lw=0.6, ls=':')
    ax.set_xlabel('Hedging error at expiry')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch12_sem_primer_hedge')
    return dict(prem=float(prem), sd4=float(e4.std()), sd52=float(e52.std()))


# =============================================================================
# 5. a three-step Cox--Ross--Rubinstein tree
# =============================================================================
def fig_tree(S0=50.0, K=50.0, T=0.5, r=0.04, sig=0.30, N=3):
    dt = T / N
    u = np.exp(sig * np.sqrt(dt)); d = 1 / u
    q = (np.exp(r * dt) - d) / (u - d)
    Sx = [[S0 * u ** j * d ** (i - j) for j in range(i + 1)] for i in range(N + 1)]
    V = [None] * (N + 1)
    V[N] = [max(s - K, 0) for s in Sx[N]]
    for i in range(N - 1, -1, -1):
        V[i] = [np.exp(-r * dt) * (q * V[i + 1][j + 1] + (1 - q) * V[i + 1][j]) for j in range(i + 1)]
    fig, ax = plt.subplots(figsize=(2.75, 2.25))
    for i in range(N + 1):
        for j in range(i + 1):
            x, y = i, j - i / 2
            if i < N:
                ax.plot([x, x + 1], [y, y + 0.5], color=Forest, lw=0.8)
                ax.plot([x, x + 1], [y, y - 0.5], color=IDAred, lw=0.8)
            ax.plot(x, y, 'o', color=MainBlue, ms=3.5)
            ax.text(x, y + 0.13, f'{Sx[i][j]:.1f}', ha='center', va='bottom', fontsize=7, color=MainBlue)
            ax.text(x, y - 0.13, f'{V[i][j]:.2f}', ha='center', va='top', fontsize=7, color=IDAred)
    ax.plot([], [], color=Forest, lw=0.8, label=f'Up: $\\times u = {u:.3f}$, prob. $q = {q:.3f}$')
    ax.plot([], [], color=IDAred, lw=0.8, label=f'Down: $\\times d = {d:.3f}$')
    ax.plot([], [], 'o', color=MainBlue, ms=3.5, label='Node: price $S$ (blue), call value (red)')
    ax.set_xticks(range(N + 1))
    ax.set_xticklabels([f'{i * dt * 12:.0f}' for i in range(N + 1)])
    ax.set_xlabel('Time (months)')
    ax.set_yticks([])
    for sp in ('left', 'right', 'top'):
        ax.spines[sp].set_visible(False)
    ax.set_xlim(-0.35, N + 0.35)
    ax.set_ylim(-N / 2 - 0.45, N / 2 + 0.45)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch12_sem_primer_tree')
    return dict(u=u, d=d, q=q, C0=V[0][0])


# =============================================================================
# 6. implied volatility by Newton's method
# =============================================================================
def fig_newton(S=100.0, K=100.0, tau=0.5, r=0.01, cmkt=9.0, s0=0.10):
    sig = np.linspace(0.005, 0.6, 400)
    P = bs_call(S, K, tau, r, sig)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(sig * 100, P, color=MainBlue, lw=1.3, label=r'$BS(\sigma)$')
    ax.axhline(cmkt, color=IDAred, lw=0.9, ls='--', label=f'Market price $C^{{mkt}} = {cmkt:.0f}$')
    s = s0
    steps = []
    for k in range(3):
        p, v = bs_call(S, K, tau, r, s), bs_vega(S, K, tau, r, s)
        s_new = s - (p - cmkt) / v
        xs = np.array([s, s_new])
        ax.plot(xs * 100, p + v * (xs - s), color=Forest, lw=0.9, label='Tangent (Newton step)' if k == 0 else '_')
        ax.plot(s * 100, p, 'o', color=Forest, ms=3.5)
        if k < 2:
            ax.text(s * 100 + 0.8, p - 1.4, f'$\\sigma_{k}$', color=Forest, fontsize=7)
        steps.append(s)
        s = s_new
    ax.plot(s * 100, bs_call(S, K, tau, r, s), 'o', color=IDAred, ms=3.5)
    ax.set_xlabel(r'Volatility $\sigma$ (%)')
    ax.set_ylabel('Call price')
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 18)
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch12_sem_primer_newton')
    return dict(steps=[float(x) for x in steps], final=float(s))


# =============================================================================
# 7. the SVI smile and the role of its parameters
# =============================================================================
def svi(k, a, b, rho, m, s):
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + s ** 2))


def fig_svi(tau=0.25):
    k = np.linspace(-0.6, 0.6, 401)
    base = dict(a=0.004, b=0.08, rho=-0.4, m=0.0, s=0.15)
    fig, ax = plt.subplots(figsize=HALF)
    for (lab, kw, col, ls) in [(r'$\rho = -0.4$ (base)', {}, MainBlue, '-'),
                               (r'$\rho = 0$', dict(rho=0.0), Forest, '-'),
                               (r'$\rho = -0.8$', dict(rho=-0.8), IDAred, '-'),
                               (r'$b = 0.12$ (steeper wings)', dict(b=0.12), Amber, '--')]:
        p = dict(base, **kw)
        ax.plot(k, 100 * np.sqrt(svi(k, **p) / tau), color=col, lw=1.1, ls=ls, label=lab)
    ax.axvline(0, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel(r'Log-moneyness $k = \ln(K/F)$')
    ax.set_ylabel(r'Implied volatility $\sqrt{w(k)/\tau}$ (%)')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch12_sem_primer_svi')


# =============================================================================
# 8. the variance strip: OTM prices and their 1/K^2 weights
# =============================================================================
def fig_strip(F=100.0, T=30 / 365, r=0.0, dK=2.5):
    Ks = np.arange(70, 130 + dK / 2, dK)
    a, b, rho, m, s = 0.003, 0.03, -0.5, 0.0, 0.08
    w = svi(np.log(Ks / F), a, b, rho, m, s)
    iv = np.sqrt(w / T)
    Q = np.where(Ks < F, bs_put(F, Ks, T, r, iv), bs_call(F, Ks, T, r, iv))
    Q[Ks == F] = 0.5 * (bs_put(F, F, T, r, iv[Ks == F]) + bs_call(F, F, T, r, iv[Ks == F]))
    contrib = 2 / T * dK / Ks ** 2 * np.exp(r * T) * Q
    fig, ax = plt.subplots(figsize=HALF)
    put = Ks < F
    ax.bar(Ks[put], Q[put], width=dK * 0.8, color=IDAred, alpha=0.75, label='OTM puts $Q(K)$')
    ax.bar(Ks[~put], Q[~put], width=dK * 0.8, color=MainBlue, alpha=0.75, label='OTM calls $Q(K)$')
    ax.set_xlabel('Strike $K$ ($F = 100$, 30 days)')
    ax.set_ylabel('Option price $Q(K)$')
    ax2 = ax.twinx()
    ax2.plot(Ks, 1e4 * np.cumsum(contrib), color=Forest, lw=1.2, label=r'Running sum $\times 10^4$ (right axis)')
    ax2.set_ylabel(r'$\frac{2}{T}\sum \frac{\Delta K}{K^2}Q(K)$, $\times 10^{4}$')
    ax2.spines['right'].set_color(Navy)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    bottom_legend(fig, ncol=2, handles=h1 + h2, labels=l1 + l2)
    save_fig(fig, 'ch12_sem_primer_strip')
    return dict(var=float(contrib.sum()), vol=float(100 * np.sqrt(contrib.sum())))


# =============================================================================
# 9. implied and realised variance: a simulated variance risk premium
# =============================================================================
def sim_vol_path(seed=11, n=2520, A=252):
    rng = np.random.default_rng(seed)
    lv = np.empty(n); lv[0] = np.log(0.16)
    for t in range(1, n):
        lv[t] = np.log(0.16) + 0.985 * (lv[t - 1] - np.log(0.16)) + 0.06 * rng.standard_normal()
    sig_d = np.exp(lv) / np.sqrt(A)
    r = sig_d * rng.standard_t(5, n) * np.sqrt(3 / 5)
    return np.exp(lv), r


def fig_vrp(h=21, A=252):
    vol, r = sim_vol_path()
    n = len(r) - h
    rv = np.array([A / h * np.sum((100 * r[t + 1:t + 1 + h]) ** 2) for t in range(n)])
    # implied variance: the expected variance plus a premium of 20 % of it
    iv2 = (100 * vol[:n]) ** 2 * 1.2
    t = np.arange(n) / A
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(t, np.sqrt(iv2), color=MainBlue, lw=0.9, label=r'Implied $IV_t$')
    ax.plot(t, np.sqrt(rv), color=IDAred, lw=0.7, label=r'Realised $\sqrt{RV_{t,t+21}}$')
    ax.set_xlabel('Time (years, simulated)')
    ax.set_ylabel('Volatility (% per year)')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch12_sem_primer_vrp')
    vrp = iv2 - rv
    return dict(mean_vrp=float(vrp.mean()), share_pos=float((vrp > 0).mean()))


# =============================================================================
# 10. overlapping windows: autocorrelation of a 21-day sum of i.i.d. shocks
# =============================================================================
def fig_overlap(h=21, n=20000, seed=3, K=40):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n + h)
    x = np.convolve(e, np.ones(h), mode='valid')[:n]
    x = x - x.mean()
    acf = np.array([np.sum(x[k:] * x[:n - k]) / np.sum(x * x) for k in range(1, K + 1)])
    ks = np.arange(1, K + 1)
    fig, ax = plt.subplots(figsize=HALF)
    ax.bar(ks, acf, width=0.7, color=BandBlue, edgecolor=MainBlue, lw=0.3, label='Sample ACF')
    ax.plot(ks, np.maximum(1 - ks / h, 0), color=IDAred, lw=1.2, label=r'Theory $\max(1 - j/21,\ 0)$')
    ax.axvline(h, color=Amber, lw=0.8, ls=':')
    ax.text(h + 0.7, 0.8, '$j = 21$', color=Amber, fontsize=7)
    ax.set_xlabel('Lag $j$ (days)')
    ax.set_ylabel('Autocorrelation')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch12_sem_primer_overlap')


# =============================================================================
# 11. a joint Wald test can reject although each t-test does not
# =============================================================================
def fig_wald(seed=5):
    a_hat, b_hat = 0.9, 1.08
    se_a, se_b, corr = 0.6, 0.085, -0.9
    cov = np.array([[se_a ** 2, corr * se_a * se_b], [corr * se_a * se_b, se_b ** 2]])
    rng = np.random.default_rng(seed)
    draws = rng.multivariate_normal([a_hat, b_hat], cov, 400)
    vals, vecs = np.linalg.eigh(cov)
    c = stats.chi2.ppf(0.95, 2)
    ang = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(draws[:, 0], draws[:, 1], '.', color=BandBlue, ms=2.0, label='Estimates in repeated samples')
    ax.add_patch(Ellipse((a_hat, b_hat), 2 * np.sqrt(c * vals[1]), 2 * np.sqrt(c * vals[0]), angle=ang,
                         fill=False, color=MainBlue, lw=1.2, label='95% joint region (Wald)'))
    ax.add_patch(Rectangle((a_hat - 1.96 * se_a, b_hat - 1.96 * se_b), 2 * 1.96 * se_a, 2 * 1.96 * se_b,
                           fill=False, color=Amber, lw=1.0, ls='--', label='Two separate 95% intervals'))
    ax.plot(a_hat, b_hat, 'o', color=MainBlue, ms=3.5)
    ax.plot(0, 1, '*', color=IDAred, ms=8, label=r'$H_0$: $(\alpha, \beta) = (0, 1)$')
    ax.set_xlabel(r'$\hat\alpha$')
    ax.set_ylabel(r'$\hat\beta$')
    d = np.array([a_hat - 0, b_hat - 1])
    W = float(d @ np.linalg.solve(cov, d))
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch12_sem_primer_wald')
    return dict(W=W, p=float(stats.chi2.sf(W, 2)), t_a=a_hat / se_a, t_b=(b_hat - 1) / se_b)


# =============================================================================
# 12. QLIKE against squared error: losses of a variance forecast
# =============================================================================
def fig_qlike():
    x = np.linspace(0.2, 3.0, 400)          # forecast / realised variance
    ql = 1 / x + np.log(x) - 1              # RV/h - ln(RV/h) - 1 with RV = 1, h = x
    mse = (x - 1) ** 2 / 2
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, ql, color=MainBlue, lw=1.3, label=r'QLIKE: $RV/\hat h - \ln(RV/\hat h) - 1$')
    ax.plot(x, mse, color=IDAred, lw=1.1, ls='--', label=r'Squared error $(\hat h - RV)^2/2$')
    ax.axvline(1, color=Navy, lw=0.5, ls=':')
    ax.set_xlabel(r'Forecast / realised variance $\hat h / RV$')
    ax.set_ylabel('Loss ($RV = 1$)')
    ax.set_ylim(0, 2.0)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch12_sem_primer_qlike')


if __name__ == '__main__':
    print('Seminar 12 primer charts')
    fig_payoffs()
    fig_butterfly()
    fig_greeks()
    print('   hedge', fig_hedge())
    print('   tree', fig_tree())
    print('   newton', fig_newton())
    fig_svi()
    print('   strip', fig_strip())
    print('   vrp', fig_vrp())
    fig_overlap()
    print('   wald', fig_wald())
    fig_qlike()

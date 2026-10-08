"""
seminar16_explainers.py -- Explanatory (primer) charts for Seminar 16 (MFM): digital assets and DeFi
=====================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 16, which
takes place BEFORE Lecture 16. All charts use SIMULATED data only (fixed seeds): they illustrate the concepts
(log against simple returns, the divisor of a market-value index, a constant-product pool and its price impact,
the no-arbitrage band of a pool with fees, a threshold AR and half-lives, the block bootstrap, trend-stationary
against unit-root series, asynchronous closes and the Dimson beta, a break at an unknown date and the sup-Wald
statistic) and contain no exercise answers.

The charts are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide), so that every
text is at least 6.3 pt on the slide.

Output: charts/ch16_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_16/seminar16_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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


# =============================================================================
# (1) log against simple returns: the gap of the annual means grows like sigma^2 / 2
# =============================================================================
def fig_log_simple(seed=1, A=365, years=200):
    rng = np.random.default_rng(seed)
    sig = np.linspace(0.0, 1.0, 101)
    fig, ax = figure(HALF)
    ax.plot(100 * sig, 100 * sig ** 2 / 2, color=MainBlue, label='$\\sigma_a^2/2$ (Itô / lognormal)')
    pts_s, pts_g = [], []
    for s in (0.2, 0.4, 0.6, 0.8):
        R = np.exp(rng.normal(0.30 / A - s ** 2 / (2 * A), s / np.sqrt(A), A * years)) - 1   # simple returns
        r = np.log1p(R)
        pts_s.append(100 * s); pts_g.append(100 * (A * R.mean() - A * r.mean()))
    ax.plot(pts_s, pts_g, 'o', color=IDAred, ms=4, label='simulated: $A\\,\\bar R - A\\,\\bar r$')
    for s, lab in ((0.19, 'shares'), (0.60, 'Bitcoin-like')):
        ax.axvline(100 * s, color=Amber, lw=0.7, ls='--')
        ax.text(100 * s + 1.5, 46, lab, color=Amber, fontsize=6.8, va='top')
    ax.set_xlabel('Annualised volatility $\\sigma_a$ (%)')
    ax.set_ylabel('Simple minus log mean (pp)')
    ax.set_title('Mean log return is lower by about $\\sigma_a^2/2$', loc='left')
    ax.set_ylim(0, 50)
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_log_simple')


# =============================================================================
# (2) market-value index: the divisor keeps the level continuous at a reallocation
# =============================================================================
def fig_index_divisor(seed=4, n=60, k=30):
    rng = np.random.default_rng(seed)
    P = np.exp(np.cumsum(rng.normal(0.001, 0.03, (n, 2)), axis=0)) * np.array([100.0, 20.0])
    Q_old, Q_new = np.array([10.0, 50.0]), np.array([10.0, 80.0])   # coin 2's supply rises at day k
    M_old = P @ Q_old
    D0 = M_old[0] / 1000
    I = M_old / D0
    D1 = (P[k] @ Q_new) / I[k]                                        # new divisor: same level at k
    I_good = np.r_[I[:k + 1], (P[k + 1:] @ Q_new) / D1]
    I_bad = np.r_[I[:k + 1], (P[k + 1:] @ Q_new) / D0]
    fig, ax = figure(HALF)
    ax.plot(np.arange(n), I_bad, color=IDAred, ls='--', label='divisor kept at $D_0$: a fake jump')
    ax.plot(np.arange(n), I_good, color=MainBlue, label='divisor reset to $D_1$: continuous')
    ax.axvline(k + 0.5, color=Amber, lw=0.8, ls=':', label='reallocation: supplies $Q$ change')
    ax.set_xlabel('Day')
    ax.set_ylabel('Index level $I_t$')
    ax.set_title('Two simulated coins, base level 1000', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_index_divisor')
    return dict(D0=D0, D1=D1, jump=I_bad[k + 1] / I_good[k + 1] - 1)


# =============================================================================
# (3) constant-product pool: the curve xy = k, one trade, and the average price against trade size
# =============================================================================
def fig_amm(x=10.0, y=30000.0, f=0.003):
    k = x * y
    g = 1 - f
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    xs = np.linspace(4, 20, 300)
    ax.plot(xs, k / xs / 1000, color=MainBlue, label='$xy = k$')
    dx = 3.0
    x1 = x - dx
    ax.plot([x], [y / 1000], 'o', color=Forest, ms=4, label='before: $p = y/x = 3000$')
    ax.plot([x1], [k / x1 / 1000], 'o', color=IDAred, ms=4, label=f'after buying {dx:.0f} Ether: $p\' = {k / x1 ** 2:.0f}$')
    tt = np.linspace(6, 14, 10)
    ax.plot(tt, (y - (y / x) * (tt - x)) / 1000, color=Forest, lw=0.8, ls='--')
    ax.annotate('', xy=(x1, k / x1 / 1000), xytext=(x, y / 1000), arrowprops=dict(arrowstyle='->', color=Navy, lw=0.8))
    ax.set_xlabel('Ether in the pool $x$')
    ax.set_ylabel('$y$ (thousand USDC)')
    ax.set_title('Pool price $p = y/x$ = minus the slope', loc='left')
    ax.set_ylim(0, 80)
    ax = axes[1]
    d = np.linspace(0.005, 1, 200)
    avg_nofee = (k / (x - d) - y) / d
    avg_fee = avg_nofee / g
    p0 = y / x
    ax.axhline(0, color=Forest, lw=0.9, ls='--', label='pool price before the trade $p$')
    ax.plot(d, 100 * (avg_nofee / p0 - 1), color=MainBlue, label='average price, no fee: $p\\,x/(x - \\Delta x)$')
    ax.plot(d, 100 * (avg_fee / p0 - 1), color=IDAred, label=f'average price, fee {100 * f:.1f}%: divided by $\\gamma$')
    ax.set_xlabel('Ether bought $\\Delta x$')
    ax.set_ylabel('Premium over $p$ (%)')
    ax.set_title(f'Price impact: $x = {x:.0f}$, $y = {y:,.0f}$', loc='left')
    h, l = all_handles(axes)
    legend_below(fig, h, l, 3)
    save_fig(fig, 'ch16_sem_primer_amm')


# =============================================================================
# (4) the no-arbitrage band: the pool price follows the outside price only when it leaves the band
# =============================================================================
def fig_arb_band(seed=8, n=300, f=0.003):
    rng = np.random.default_rng(seed)
    g = 1 - f
    P = 3000 * np.exp(np.cumsum(rng.normal(0, 0.0012, n)))
    p = np.empty(n)
    p[0] = P[0]
    for t in range(1, n):
        p[t] = p[t - 1]
        if p[t] < g * P[t]:          # pool too cheap: arbitrageurs buy Ether until p = gamma P
            p[t] = g * P[t]
        elif p[t] > P[t] / g:        # pool too dear: they sell Ether until p = P / gamma
            p[t] = P[t] / g
    fig, ax = figure(HALF)
    t = np.arange(n)
    ax.fill_between(t, g * P, P / g, color=BandBlue, lw=0, label='band $[\\gamma P_t,\\ P_t/\\gamma]$: no trade pays')
    ax.plot(t, P, color=Navy, lw=0.8, label='outside price $P_t$')
    ax.plot(t, p, color=IDAred, lw=1.0, label='pool price $p_t$ after arbitrage')
    ax.set_xlabel('Block (simulated)')
    ax.set_ylabel('USD Coin per Ether')
    ax.set_title(f'Fee $f = {100 * f:.1f}\\%$, $\\gamma = 1 - f$', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_arb_band')
    return dict(share_moves=float(np.mean(np.diff(p) != 0)))


# =============================================================================
# (5) threshold AR: a simulated deviation path and the decay phi^n with its half-life
# =============================================================================
def fig_tar(seed=3, n=250, c=10.0, phi_in=0.9, phi_out=0.4, sd=3.0):
    rng = np.random.default_rng(seed)
    d = np.zeros(n)
    eps = rng.normal(0, sd, n)
    eps[120] = -80                    # one large shock
    eps[60] = 35
    for t in range(1, n):
        phi = phi_in if abs(d[t - 1]) <= c else phi_out
        d[t] = phi * d[t - 1] + eps[t]
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    ax.axhspan(-c, c, color=BandBlue, lw=0, label=f'band $|d_{{t-1}}| \\leq c$, $c = {c:.0f}$ bp')
    ax.plot(np.arange(n), d, color=MainBlue, lw=0.8, label='deviation $d_t$ (bp)')
    ax.set_xlabel('Day')
    ax.set_ylabel('$d_t = 10^4(P_t - 1)$')
    ax.set_title(f'Simulated TAR: $\\phi_{{\\mathrm{{in}}}} = {phi_in}$, $\\phi_{{\\mathrm{{out}}}} = {phi_out}$', loc='left')
    ax = axes[1]
    h = np.arange(0, 11)
    for phi, col in ((0.3, IDAred), (0.6, Amber), (0.9, Forest)):
        hl = np.log(0.5) / np.log(phi)
        ax.plot(h, phi ** h, 'o-', color=col, ms=2.5, label=f'$\\phi = {phi}$: half-life {hl:.2f} days')
        ax.plot(hl, 0.5, 'D', color=col, ms=3.5)
    ax.axhline(0.5, color=Navy, lw=0.7, ls=':', label='half of the deviation left')
    ax.set_xlabel('Days $n$ without shocks')
    ax.set_ylabel('$d_n/d_0 = \\phi^n$')
    ax.set_title('Decay in one regime', loc='left')
    hh, ll = all_handles(axes)
    legend_below(fig, hh, ll, 3)
    save_fig(fig, 'ch16_sem_primer_tar')


# =============================================================================
# (6) block bootstrap: resampling single days destroys volatility clusters, blocks keep them
# =============================================================================
def acf(x, L):
    x = x - x.mean()
    return np.array([np.sum(x[l:] * x[:-l]) / np.sum(x * x) for l in range(1, L + 1)])


def fig_block_bootstrap(seed=6, n=3000, b=20, R=200, L=20):
    rng = np.random.default_rng(seed)
    r = np.zeros(n)
    s2 = np.ones(n)
    z = rng.standard_normal(n)
    for t in range(1, n):
        s2[t] = 0.05 + 0.10 * r[t - 1] ** 2 + 0.85 * s2[t - 1]
        r[t] = np.sqrt(s2[t]) * z[t]
    a_orig = acf(r ** 2, L)
    a_iid, a_blk = [], []
    for _ in range(R):
        a_iid.append(acf(r[rng.integers(0, n, n)] ** 2, L))
        starts = rng.integers(0, n - b, n // b)
        rb = np.concatenate([r[s:s + b] for s in starts])
        a_blk.append(acf(rb ** 2, L))
    a_iid, a_blk = np.mean(a_iid, 0), np.mean(a_blk, 0)
    lags = np.arange(1, L + 1)
    fig, ax = figure(HALF)
    w = 0.28
    ax.bar(lags - w, a_orig, w, color=Amber, label='original series')
    ax.bar(lags, a_blk, w, color=MainBlue, label=f'blocks of {b} days (mean of {R})')
    ax.bar(lags + w, a_iid, w, color=IDAred, label=f'single days (mean of {R})')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Lag (days)')
    ax.set_ylabel('ACF of $r_t^2$')
    ax.set_title('Volatility clusters in resampled series', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_block_bootstrap')


# =============================================================================
# (7) trend-stationary against unit-root series, with ADF and KPSS
# =============================================================================
def fig_trend_stationary(seed=12, n=700):
    from statsmodels.tsa.stattools import adfuller, kpss
    rng = np.random.default_rng(seed)
    t = np.arange(n) / 252
    e = np.zeros(n)
    u = rng.normal(0, 0.12, n)
    for i in range(1, n):
        e[i] = 0.5 * e[i - 1] + u[i]
    ts = -0.25 * t + e                          # fee trend (% a year) + stationary noise, in %
    rw = -0.25 * t + np.cumsum(rng.normal(0, 0.06, n))
    fig, ax = figure(HALF)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = {}
        for y, lab in ((ts, 'trend-stationary'), (rw, 'unit root')):
            res[lab] = (adfuller(y, regression='ct', autolag='AIC')[1], kpss(y, regression='ct', nlags='auto')[1])
    ax.plot(t, rw, color=IDAred, lw=0.8,
            label=f'unit root: ADF $p = {res["unit root"][0]:.2f}$, KPSS $p {"<" if res["unit root"][1] <= 0.01 else "="} {max(res["unit root"][1], 0.01):.2f}$')
    ax.plot(t, ts, color=MainBlue, lw=0.8,
            label=f'trend-stationary: ADF $p < 0.01$, KPSS $p {">" if res["trend-stationary"][1] >= 0.1 else "="} {min(res["trend-stationary"][1], 0.1):.2f}$')
    ax.plot(t, -0.25 * t, color=Forest, lw=1.1, ls='--', label='trend: $-0.25\\%$ a year')
    ax.set_xlabel('Years')
    ax.set_ylabel('$\\ell_t$ (%)')
    ax.set_title('Simulated log price ratio $\\ell_t$', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_trend_stationary')
    return res


# =============================================================================
# (8) asynchronous closes: daily OLS beta, Dimson beta and weekly beta
# =============================================================================
def fig_dimson(seed=5, n=1400, share_today=0.6):
    rng = np.random.default_rng(seed)
    rb = rng.normal(0, 3.0, n + 1)
    etf = share_today * rb[1:] + (1 - share_today) * rb[:-1] + rng.normal(0, 0.4, n)
    x = rb[1:]
    X = np.column_stack([np.ones(n - 2), x[1:-1], x[:-2], x[2:]])     # today, lag, lead
    y = etf[1:-1]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    b_daily = np.polyfit(x, etf, 1)[0]
    W = n // 5
    xw = x[:W * 5].reshape(W, 5).sum(1)
    yw = etf[:W * 5].reshape(W, 5).sum(1)
    b_week = np.polyfit(xw, yw, 1)[0]
    fig, ax = figure(HALF)
    labels = ['daily\nOLS $b_0$', 'lag\n$b_{-1}$', 'lead\n$b_{1}$', 'Dimson\nsum', 'weekly\nOLS']
    vals = [b_daily, b[2], b[3], b[1] + b[2] + b[3], b_week]
    cols = [IDAred, Amber, Amber, MainBlue, Forest]
    ax.bar(range(5), vals, color=cols, width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f'{v:.2f}', ha='center', va='bottom', fontsize=6.8)
    ax.axhline(1, color=Navy, lw=0.8, ls='--', label='true exposure: 1')
    ax.set_xticks(range(5), labels)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel('Estimated beta')
    ax.set_title(f'Simulated: {int(100 * share_today)}% today, {100 - int(100 * share_today)}% next day', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_dimson')
    return dict(daily=b_daily, b0=b[1], lag=b[2], lead=b[3], week=b_week)


# =============================================================================
# (9) a break at an unknown date: W(tau) over the middle 70% and the two critical values
# =============================================================================
def fig_supwald(seed=10, n=280, brk=0.35):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 4, n)
    tb = int(brk * n)
    beta = np.where(np.arange(n) < tb, 0.8, 1.4)
    y = 0.1 + beta * x + rng.normal(0, 5, n)
    taus = np.arange(int(0.15 * n), int(0.85 * n))
    W = []
    for tau in taus:
        d = (np.arange(n) >= tau).astype(float)
        X = np.column_stack([np.ones(n), x, d, d * x])
        XtXi = np.linalg.inv(X.T @ X)
        b = XtXi @ X.T @ y
        u = y - X @ b
        V = XtXi @ (X.T * u ** 2) @ X @ XtXi      # White covariance
        R = np.array([[0, 0, 1, 0], [0, 0, 0, 1]])
        rb = R @ b
        W.append(float(rb @ np.linalg.solve(R @ V @ R.T, rb)))
    W = np.array(W)
    fig, ax = figure(HALF)
    ax.plot(taus, W, color=MainBlue, label='$W(\\tau)$ for each candidate date')
    ax.axhline(stats.chi2.ppf(0.95, 2), color=Amber, ls='--', lw=0.9, label='$\\chi^2_2$ 5% value 5.99: one known date')
    ax.axhline(11.70, color=IDAred, ls='--', lw=0.9, label='$\\sup W$ 5% value 11.70 (Andrews, $q = 2$)')
    ax.axvline(tb, color=Forest, lw=0.8, ls=':', label='true break')
    ax.plot(taus[np.argmax(W)], W.max(), 'o', color=IDAred, ms=4)
    ax.set_xlabel('Candidate break $\\tau$ (middle 70% of the sample)')
    ax.set_ylabel('Wald statistic')
    ax.set_title('Simulated slope 0.8 $\\to$ 1.4', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch16_sem_primer_supwald')
    return dict(supW=W.max(), tau_hat=int(taus[np.argmax(W)]), tb=tb)


def run_all():
    res = {}
    fig_log_simple()
    res['index'] = fig_index_divisor()
    fig_amm()
    res['band'] = fig_arb_band()
    fig_tar()
    fig_block_bootstrap()
    res['trend'] = fig_trend_stationary()
    res['dimson'] = fig_dimson()
    res['supwald'] = fig_supwald()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

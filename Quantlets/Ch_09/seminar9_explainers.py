"""
seminar9_explainers.py -- Explanatory (primer) charts for Seminar 9 (MFM): realised volatility
==============================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 9,
which takes place BEFORE Lecture 9. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (a trading day with intraday volatility, the sampling error of RV, microstructure noise and the
signature plot, the bias-variance trade-off of the sampling frequency, a jump in RV but not in BV, the null
distribution of the ratio jump test, the HAR cascade and its memory, QLIKE and MSE losses, the
Mincer--Zarnowitz regression) and contain no exercise answers (other parameters than in the tasks).

Output: charts/ch9_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_09/seminar9_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import gamma

# course palette (no grey)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'
BandBlue = '#C5D2E8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

# drawn at slide size: text 7-7.5 pt on the slide (>= 6.3 pt)
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'lines.linewidth': 1.0,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'legend.handlelength': 1.6})

FULL = (5.6, 1.4)     # full slide width, chart above two or three bullets (box 5.69 x 1.86 in)
HALF = (2.55, 1.85)   # one column (0.45 \textwidth) of a two-column frame (box 2.56 x 2.4 in)
BOX = {'full': (5.69, 1.86), 'half': (2.56, 2.40)}
SCALES = {}
SESSION = 23400        # seconds in a 6.5-hour session


def save_fig(fig, name, box='half'):
    os.makedirs(CHART_DIR, exist_ok=True)
    bb = fig.get_tightbbox(fig.canvas.get_renderer()).padded(0.1)
    w, h = BOX[box]
    SCALES[name] = round(min(1.0, w / bb.width, h / bb.height), 2)   # scale on the slide (fonts 7 pt x scale)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=220)
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
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False,
               columnspacing=1.2)


def u_shape(n):
    """Intraday volatility pattern (U shape), normalised so that its mean square is 1."""
    s = np.linspace(0, 1, n)
    f = 0.75 + 1.6 * (s - 0.5) ** 2 + 0.6 * np.exp(-s / 0.04)
    return f / np.sqrt(np.mean(f ** 2))


def efficient_day(rng, sigma_day=1.0, n=SESSION, jump=0.0, t_jump=None):
    """Efficient log price (in %) on a 1-second grid; returns prices and the spot variance per second."""
    spot = (sigma_day * u_shape(n)) ** 2 / n            # variance per second, sums to sigma_day^2
    dp = np.sqrt(spot) * rng.standard_normal(n)
    if jump:
        dp[t_jump] += jump
    return np.r_[0.0, np.cumsum(dp)], spot


def sample(p, step):
    """Prices every `step` seconds (first and last included) -> returns."""
    idx = np.r_[np.arange(0, len(p) - 1, step), len(p) - 1]
    return np.diff(p[np.unique(idx)])


# =============================================================================
# (1) one simulated day: price, spot volatility, cumulative RV and IV
# =============================================================================
def fig_day(seed=1, sigma_day=1.0):
    rng = np.random.default_rng(seed)
    p, spot = efficient_day(rng, sigma_day)
    h = np.arange(len(p)) / 3600 + 9.5
    r5 = sample(p, 300)
    t5 = 9.5 + np.arange(1, len(r5) + 1) * 300 / 3600
    fig, axes = plt.subplots(2, 1, figsize=(2.55, 1.62), sharex=True, gridspec_kw=dict(height_ratios=[1, 1]))
    ax = axes[0]
    ax.plot(h, p, color=MainBlue, lw=0.6, label='Log price (%), 1-second path')
    ax.plot(np.r_[9.5, t5], np.r_[0, np.cumsum(r5)], 'o', color=Amber, ms=1.6, label='5-minute prices')
    ax.set_ylabel('Price (%)')
    ax = axes[1]
    ax.plot(h[1:], np.cumsum(spot), color=Forest, lw=1.3, label=r'Cumulative IV $\int\sigma_s^2 ds$')
    ax.step(t5, np.cumsum(r5 ** 2), where='post', color=IDAred, lw=1.0, label=r'Cumulative RV, $M$ = 78')
    ax.set_ylabel('%$^2$')
    ax.set_xlabel('Time of day (hours)')
    ax.set_xlim(9.5, 16)
    bottom_legend(fig, axes, ncol=1)
    save_fig(fig, 'ch9_sem_primer_day')
    return dict(IV=float(spot.sum()), RV=float((r5 ** 2).sum()))


# =============================================================================
# (2) sampling distribution of RV/IV under constant volatility: chi2_M / M
# =============================================================================
def fig_rv_dist():
    x = np.linspace(0.01, 2.6, 600)
    fig, ax = plt.subplots(figsize=(2.55, 1.5))
    out = {}
    for M, col, ls in ((13, Amber, '--'), (78, MainBlue, '-'), (390, Forest, '-')):
        f = stats.chi2.pdf(x * M, M) * M
        lo, hi = stats.chi2.ppf([0.025, 0.975], M) / M
        out[M] = (float(lo), float(hi))
        ax.plot(x, f, color=col, lw=1.2, ls=ls, label=rf'$M$ = {M}: sd $\sqrt{{2/M}}$ = {np.sqrt(2 / M):.2f}')
    ax.axvline(1, color=IDAred, lw=0.8, ls=':', label=r'RV = IV')
    ax.set_xlim(0, 2.6)
    ax.set_xlabel(r'$\mathrm{RV}/\mathrm{IV} = \chi^2_M/M$')
    ax.set_ylabel('Density')
    ax.set_title('One day, constant volatility', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch9_sem_primer_rv_dist')
    return out


# =============================================================================
# (3) noise: observed and efficient prices; signature plot
# =============================================================================
def fig_noise(seed=5, omega=0.02, days=150, sigma_day=1.0):
    rng = np.random.default_rng(seed)
    steps = np.array([1, 2, 5, 10, 20, 30, 60, 120, 300, 600, 900, 1800])
    rv_obs = np.zeros(len(steps))
    rv_eff = np.zeros(len(steps))
    for d in range(days):
        p, spot = efficient_day(rng, sigma_day)
        q = p + omega * rng.standard_normal(len(p))
        for j, s in enumerate(steps):
            rv_obs[j] += np.sum(sample(q, s) ** 2) / days
            rv_eff[j] += np.sum(sample(p, s) ** 2) / days
    rng2 = np.random.default_rng(seed + 1)
    p, _ = efficient_day(rng2, sigma_day)
    q = p + omega * rng2.standard_normal(len(p))
    w = slice(11700, 11700 + 300)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    tt = np.arange(300)
    ax.plot(tt, q[w], color=IDAred, lw=0.5, label=r'Observed $p^{\mathrm{obs}} = p^* + \varepsilon$')
    ax.plot(tt, p[w], color=MainBlue, lw=1.2, label=r'Efficient price $p^*$')
    ax.set_xlabel('Seconds (a 5-minute window)')
    ax.set_ylabel('Log price (%)')
    ax.set_title(rf'Noise $\omega$ = {omega}%', loc='left')
    ax = axes[1]
    ax.loglog(steps, rv_obs, 'o-', color=IDAred, ms=3, label='Mean RV, noisy prices')
    ax.loglog(steps, rv_eff, 's-', color=MainBlue, ms=2.5, label='Mean RV, efficient prices')
    n = SESSION / steps
    ax.loglog(steps, sigma_day ** 2 + 2 * n * omega ** 2, color=Amber, lw=1.0, ls='--',
                label=r'$\mathrm{IV} + 2n\omega^2$')
    ax.axhline(sigma_day ** 2, color=Forest, lw=0.9, ls=':', label='IV = 1')
    ax.set_xlabel('Sampling interval (seconds, log scale)')
    ax.set_ylabel('Mean RV (%$^2$, log)')
    ax.set_title('Signature plot', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch9_sem_primer_noise', 'full')
    return dict(steps=steps.tolist(), rv_obs=np.round(rv_obs, 3).tolist())


# =============================================================================
# (4) bias-variance trade-off of the number of returns
# =============================================================================
def fig_mse(omega=0.02, IQ=1.0):
    n = np.logspace(1, 4.4, 300)
    var = 2 * IQ / n
    bias2 = 4 * n ** 2 * omega ** 4
    nstar = (IQ / (4 * omega ** 4)) ** (1 / 3)
    fig, ax = plt.subplots(figsize=HALF)
    ax.loglog(n, var, color=MainBlue, lw=1.2, label=r'Variance $2\,\mathrm{IQ}/n$')
    ax.loglog(n, bias2, color=Amber, lw=1.2, label=r'Squared bias $4n^2\omega^4$')
    ax.loglog(n, var + bias2, color=IDAred, lw=1.4, label='MSE = sum')
    ax.axvline(nstar, color=Forest, lw=0.9, ls='--', label=rf'$n^*$ = {nstar:.0f}')
    ax.set_ylim(1e-4, 10)
    ax.set_xlabel('Returns per day $n$ (log scale)')
    ax.set_ylabel(r'%$^4$ (log scale)')
    ax.set_title(rf'IQ = 1, $\omega$ = {omega}%', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch9_sem_primer_mse')
    return dict(nstar=float(nstar))


# =============================================================================
# (5) a jump: cumulative RV jumps, cumulative BV does not
# =============================================================================
def fig_jump(seed=0, jump=-0.8, t_jump=16200):
    rng = np.random.default_rng(seed)
    p, spot = efficient_day(rng, 0.8, jump=jump, t_jump=t_jump)
    r = sample(p, 300)
    M = len(r)
    t5 = 9.5 + np.arange(1, M + 1) * 300 / 3600
    rv = np.cumsum(r ** 2)
    bv = np.r_[0, np.cumsum(np.pi / 2 * M / (M - 1) * np.abs(r[1:]) * np.abs(r[:-1]))]
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(9.5 + np.arange(len(p)) / 3600, p, color=MainBlue, lw=0.6, label='Log price (%)')
    ax.annotate(f'jump {jump}%', xy=(9.5 + t_jump / 3600, p[t_jump + 1]), xytext=(11.0, p.min() + 0.05),
                fontsize=7, color=IDAred, arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.7))
    ax.set_xlabel('Time of day (hours)')
    ax.set_ylabel('Log price (%)')
    ax = axes[1]
    ax.step(t5, rv, where='post', color=IDAred, lw=1.2, label=r'Cumulative RV')
    ax.step(t5, bv, where='post', color=Forest, lw=1.2, label=r'Cumulative BV')
    ax.plot(9.5 + np.arange(1, len(spot) + 1) / 3600, np.cumsum(spot), color=Navy, lw=0.8, ls=':',
            label='Cumulative IV')
    ax.set_xlabel('Time of day (hours)')
    ax.set_ylabel('Variance (%$^2$)')
    ax.set_title(rf'RV $-$ BV = {rv[-1] - bv[-1]:.2f}, $J^2$ = {jump ** 2:.2f}', loc='left')
    for a in axes:
        a.set_xlim(9.5, 16)
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch9_sem_primer_jump', 'full')
    return dict(RV=float(rv[-1]), BV=float(bv[-1]), IV=float(spot.sum()))


# =============================================================================
# (6) ratio jump test: null distribution and jump days
# =============================================================================
def ratio_z(r):
    M = len(r)
    a = np.abs(r)
    rv = np.sum(r ** 2)
    bv = np.pi / 2 * M / (M - 1) * np.sum(a[1:] * a[:-1])
    mu43 = 2 ** (2 / 3) * gamma(7 / 6) / gamma(0.5)          # E|Z|^{4/3}, Z ~ N(0,1)
    tq = M * mu43 ** -3 * M / (M - 2) * np.sum((a[2:] * a[1:-1] * a[:-2]) ** (4 / 3))
    theta = np.pi ** 2 / 4 + np.pi - 5
    return (rv - bv) / rv / np.sqrt(theta / M * max(1, tq / bv ** 2))


def fig_ztest(seed=12, days=4000, M=78):
    rng = np.random.default_rng(seed)
    f = u_shape(M) / np.sqrt(M)
    z0 = np.array([ratio_z(f * rng.standard_normal(M)) for _ in range(days)])
    z1 = []
    for _ in range(days // 4):
        r = f * rng.standard_normal(M)
        r[rng.integers(M)] += rng.choice([-1, 1]) * 0.8
        z1.append(ratio_z(r))
    z1 = np.array(z1)
    x = np.linspace(-4, 9, 400)
    fig, ax = plt.subplots(figsize=HALF)
    bins = np.linspace(-4, 9, 66)
    ax.hist(z0, bins=bins, density=True, color=MainBlue, alpha=0.55, lw=0, label='No jump (U-shaped volatility)')
    ax.hist(z1, bins=bins, density=True, color=IDAred, alpha=0.45, lw=0, label='One jump of 0.8 daily sd')
    ax.plot(x, stats.norm.pdf(x), color=Navy, lw=1.0, label='$N(0,1)$')
    for c, lab in ((1.645, '5%'), (3.09, '0.1%')):
        ax.axvline(c, color=Forest, lw=0.9, ls='--')
        ax.text(c + 0.1, 0.47, lab, fontsize=7, color=Forest)
    ax.set_ylim(0, 0.52)
    ax.set_xlabel('Ratio statistic $z_t$, $M$ = 78')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch9_sem_primer_ztest')
    return dict(rej5_null=float(np.mean(z0 > 1.645)), rej5_jump=float(np.mean(z1 > 1.645)),
                rej01_jump=float(np.mean(z1 > 3.09)), mean0=float(z0.mean()))


# =============================================================================
# (7) HAR: components and long memory
# =============================================================================
def simulate_har(T, b, seed, burn=500, s=0.45):
    rng = np.random.default_rng(seed)
    y = np.zeros(T + burn)
    mu = b[0] / (1 - sum(b[1:]))
    y[:22] = mu
    for t in range(22, T + burn):
        y[t] = b[0] + b[1] * y[t - 1] + b[2] * y[t - 5:t].mean() + b[3] * y[t - 22:t].mean() + s * rng.standard_normal()
    return y[burn:]


def acf(x, K):
    x = x - x.mean()
    return np.array([np.dot(x[k:], x[:len(x) - k]) / np.dot(x, x) for k in range(K + 1)])


def fig_har(b=(0.0, 0.40, 0.30, 0.22), seed=3, T=20000):
    y = simulate_har(T, b, seed)
    K = 100
    a = acf(y, K)
    phi = a[1]
    w = 400
    ys = y[-w:]
    yw = np.convolve(y, np.ones(5) / 5, 'valid')[-w:]
    ym = np.convolve(y, np.ones(22) / 22, 'valid')[-w:]
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 1.3))
    ax = axes[0]
    tt = np.arange(w)
    ax.plot(tt, ys, color=MainBlue, lw=0.5, label=r'$y_t = \ln \mathrm{RV}_t$')
    ax.plot(tt, yw, color=Amber, lw=1.0, label='5-day mean')
    ax.plot(tt, ym, color=IDAred, lw=1.3, label='22-day mean')
    ax.set_xlabel('Day')
    ax.set_ylabel('$y_t$')
    ax.set_title(r'Simulated log-HAR, $\beta$ = (0.40, 0.30, 0.22)', loc='left')
    ax = axes[1]
    k = np.arange(K + 1)
    ax.plot(k[1:], a[1:], color=MainBlue, lw=1.3, label='ACF of the HAR process')
    ax.plot(k[1:], phi ** k[1:], color=Forest, lw=1.1, ls='--', label=rf'AR(1), same lag-1 value {phi:.2f}')
    ax.set_xlabel('Lag $k$ (days)')
    ax.set_ylabel('Autocorrelation')
    ax.set_ylim(0, 1)
    ax.set_title('Slow decay from three averages', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch9_sem_primer_har', 'full')
    return dict(acf1=float(a[1]), acf22=float(a[22]), acf50=float(a[50]), ar50=float(phi ** 50))


# =============================================================================
# (8) QLIKE and variance MSE as functions of the forecast
# =============================================================================
def fig_losses(V=2.0):
    F = np.linspace(0.4, 6, 400)
    q = V / F - np.log(V / F) - 1
    m = (V - F) ** 2
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(F, q, color=IDAred, lw=1.3, label=r'QLIKE $V/F - \ln(V/F) - 1$')
    ax.plot(F, m / 4, color=MainBlue, lw=1.3, ls='--', label=r'MSE $(V-F)^2$, divided by 4')
    ax.axvline(V, color=Forest, lw=0.9, ls=':', label=f'True variance $V$ = {V:g}')
    ax.set_ylim(0, 2.2)
    ax.set_xlim(0.4, 6)
    ax.annotate('under-prediction:\nQLIKE rises fast', xy=(0.75, 1.3), xytext=(1.3, 1.75), fontsize=7, color=IDAred,
                arrowprops=dict(arrowstyle='->', color=IDAred, lw=0.7))
    ax.set_xlabel('Forecast $F$ (%$^2$)')
    ax.set_ylabel('Loss')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch9_sem_primer_losses')
    return dict(q_half=float(V / (V / 2) - np.log(2) - 1), q_double=float(0.5 + np.log(2) - 1))


# =============================================================================
# (9) Mincer--Zarnowitz regression of a noisy proxy on a forecast
# =============================================================================
def fig_mz(seed=7, T=600):
    rng = np.random.default_rng(seed)
    h = np.exp(0.5 * rng.standard_normal(T))                       # true conditional variance
    F = 0.3 + 1.4 * h * np.exp(0.15 * rng.standard_normal(T))       # too extreme forecasts (b < 1)
    V = h * stats.chi2.rvs(5, size=T, random_state=rng) / 5          # noisy, conditionally unbiased proxy
    X = np.c_[np.ones(T), F]
    a, b = np.linalg.lstsq(X, V, rcond=None)[0]
    fig, ax = plt.subplots(figsize=(2.55, 1.65))
    ax.plot(F, V, 'o', color=MainBlue, ms=1.8, alpha=0.6, label='Days: $(F_t, V_t)$')
    xx = np.linspace(0, F.max(), 10)
    ax.plot(xx, xx, color=Navy, lw=1.0, ls='--', label='$a = 0$, $b = 1$ (unbiased)')
    ax.plot(xx, a + b * xx, color=IDAred, lw=1.4, label=rf'OLS fit: $\hat a$ = {a:.2f}, $\hat b$ = {b:.2f}')
    ax.set_xlim(0, F.max())
    ax.set_ylim(0, np.quantile(V, 0.995))
    ax.set_xlabel('Forecast $F_t$')
    ax.set_ylabel('Proxy $V_t$')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch9_sem_primer_mz')
    return dict(a=float(a), b=float(b))


def run_all():
    res = {}
    res['day'] = fig_day()
    res['rv_dist'] = fig_rv_dist()
    res['noise'] = fig_noise()
    res['mse'] = fig_mse()
    res['jump'] = fig_jump()
    res['ztest'] = fig_ztest()
    res['har'] = fig_har()
    res['losses'] = fig_losses()
    res['mz'] = fig_mz()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())
    print('scale on the slide:', SCALES)

"""
seminar5_explainers.py -- Explanatory (primer) charts for Seminar 5 (MFM): GARCH models
=======================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 5,
which takes place BEFORE Lecture 5. All charts use SIMULATED data or textbook parameter values only (fixed
seeds): they illustrate the concepts (volatility clustering, the roles of alpha and beta, mean reversion of
the forecasts and the half-life, chi-square critical values, Student-t innovations, standardised residuals,
the news impact curve, the boundary law of the LR test, the QLIKE loss, simple benchmark forecasts, skewed
innovations) and contain no exercise answers.

Output: charts/ch5_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_05/seminar5_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import gammaln

# course palette (no grey)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'
BandBlue = '#C5D2E8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

plt.rcParams.update({'font.size': 7.4, 'axes.labelsize': 7.4, 'axes.titlesize': 7.6, 'xtick.labelsize': 6.9,
                     'ytick.labelsize': 6.9, 'legend.fontsize': 7.0, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
                     'legend.handlelength': 1.6, 'legend.columnspacing': 1.2})

FULL = (5.55, 1.75)   # full text width (about 408 pt) of a 16:9 slide
HALF = (2.75, 1.62)   # one column of a two-column frame
ANN = 6.9


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True, pad_inches=0.03)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=200,
                pad_inches=0.03)
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


def std_t(nu, size, rng):
    """Student-t draws rescaled to variance 1."""
    return rng.standard_t(nu, size) * np.sqrt((nu - 2) / nu)


def simulate_garch(n, omega, alpha, beta, nu=None, seed=1, gamma=0.0, burn=500):
    rng = np.random.default_rng(seed)
    z = std_t(nu, n + burn, rng) if nu else rng.standard_normal(n + burn)
    s2 = np.empty(n + burn); e = np.empty(n + burn)
    p = alpha + beta + gamma / 2
    s2[0] = omega / (1 - p)
    for t in range(n + burn):
        if t > 0:
            s2[t] = omega + (alpha + gamma * (e[t - 1] < 0)) * e[t - 1] ** 2 + beta * s2[t - 1]
        e[t] = np.sqrt(s2[t]) * z[t]
    return e[burn:], s2[burn:], z[burn:]


def acf(x, L):
    x = x - x.mean()
    d = x @ x
    return np.array([x[k:] @ x[:-k] / d for k in range(1, L + 1)])


# =============================================================================
# (1) volatility clustering: a GARCH path with its bands; ACF of r and of r^2
# =============================================================================
def fig_clustering(n=2000, L=30):
    e, s2, _ = simulate_garch(n, 0.05, 0.10, 0.85, nu=6, seed=3)
    fig, axes = plt.subplots(1, 2, figsize=FULL, gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axes[0]
    t = np.arange(n)
    ax.fill_between(t, -2 * np.sqrt(s2), 2 * np.sqrt(s2), color=BandBlue, lw=0, label=r'$\pm 2\sigma_t$')
    ax.plot(t, e, color=MainBlue, lw=0.4, label=r'$r_t$ (%), GARCH(1,1)')
    ax.set_xlabel('Day $t$'); ax.set_ylabel('Return (%)')
    ax.set_title(r'$\omega$ = 0.05, $\alpha$ = 0.10, $\beta$ = 0.85, Student-$t$(6)', loc='left')
    ax.set_xlim(0, n)
    ax = axes[1]
    k = np.arange(1, L + 1)
    a1, a2 = acf(e, L), acf(e ** 2, L)
    ax.bar(k - 0.2, a1, width=0.4, color=MainBlue, label=r'ACF of $r_t$')
    ax.bar(k + 0.2, a2, width=0.4, color=IDAred, label=r'ACF of $r_t^2$')
    b = 1.96 / np.sqrt(n)
    ax.axhspan(-b, b, color=Amber, alpha=0.3, lw=0, label=r'$\pm 1.96/\sqrt{n}$')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Lag $k$'); ax.set_ylabel(r'$\hat\rho_k$')
    ax.set_title('Uncorrelated returns, correlated squares', loc='left')
    bottom_legend(fig, axes, ncol=5)
    save_fig(fig, 'ch5_sem_primer_clustering')
    return dict(acf1_r=round(float(a1[0]), 3), acf1_r2=round(float(a2[0]), 3), acf10_r2=round(float(a2[9]), 3),
                share_out=round(float(np.mean(np.abs(e) > 2 * np.sqrt(s2))), 3))


# =============================================================================
# (2) roles of alpha and beta: same shocks, same persistence, different reaction
# =============================================================================
def fig_alpha_beta(n=250, seed=12):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n)
    z[60] = -4.5
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for (a, b), c in [((0.20, 0.75), IDAred), ((0.05, 0.90), MainBlue)]:
        om = 0.05
        s2 = np.empty(n); e = np.empty(n)
        s2[0] = om / (1 - a - b)
        for t in range(n):
            if t > 0:
                s2[t] = om + a * e[t - 1] ** 2 + b * s2[t - 1]
            e[t] = np.sqrt(s2[t]) * z[t]
        ax.plot(np.sqrt(s2), color=c, lw=1.1, label=rf'$\alpha$ = {a:.2f}, $\beta$ = {b:.2f}')
        out[f'{a}_{b}'] = dict(peak=round(float(np.sqrt(s2).max()), 2), sd_sig=round(float(np.sqrt(s2).std()), 3))
    ax.axvline(61, color=Navy, lw=0.6, ls=':')
    ax.annotate('shock $z_{61}$ = $-$4.5', (61, 2.2), xytext=(10, 0), textcoords='offset points', fontsize=ANN,
                color=Navy)
    ax.axhline(1, color=Forest, lw=0.8, ls='--', label=r'$\bar\sigma$ = 1')
    ax.set_xlabel('Day $t$'); ax.set_ylabel(r'$\sigma_t$ (%)')
    ax.set_xlim(0, n)
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch5_sem_primer_alpha_beta')
    return out


# =============================================================================
# (3) forecasts revert to the long-run variance; half-life
# =============================================================================
def fig_forecast(s2_next=2.0, s2bar=1.0, H=60):
    h = np.arange(1, H + 1)
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for p, c in [(0.90, IDAred), (0.95, MainBlue), (0.99, Forest)]:
        f = s2bar + p ** (h - 1) * (s2_next - s2bar)
        hl = np.log(0.5) / np.log(p)
        ax.plot(h, f, color=c, lw=1.2, label=rf'$p$ = {p:.2f}, $h_{{1/2}}$ = {hl:.1f} days')
        ax.plot(1 + hl, s2bar + 0.5 * (s2_next - s2bar), 'o', color=c, ms=3.2)
        out[p] = round(float(hl), 1)
    ax.axhline(s2bar, color=Navy, lw=0.7, ls='--')
    ax.axhline(s2bar + 0.5 * (s2_next - s2bar), color=Amber, lw=0.7, ls=':')
    ax.text(H, s2bar + 0.47 * (s2_next - s2bar), 'half of the gap', ha='right', va='top', fontsize=ANN, color=Amber)
    ax.text(H, s2bar - 0.03, r'$\bar\sigma^2$ = 1', ha='right', va='top', fontsize=ANN, color=Navy)
    ax.set_xlim(0, H); ax.set_ylim(0.85, 2.05)
    ax.set_xlabel('Horizon $h$ (days)'); ax.set_ylabel(r'$E_t\sigma^2_{t+h}$')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch5_sem_primer_forecast')
    return out


# =============================================================================
# (4) chi-square laws and 5% critical values
# =============================================================================
def fig_chi2():
    x = np.linspace(0.01, 30, 600)
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for q, c in [(5, MainBlue), (10, IDAred)]:
        f = stats.chi2.pdf(x, q)
        cv = stats.chi2.ppf(0.95, q)
        ax.plot(x, f, color=c, lw=1.2, label=rf'$\chi^2_{{{q}}}$, 5% critical value {cv:.2f}')
        m = x >= cv
        ax.fill_between(x[m], 0, f[m], color=c, alpha=0.3, lw=0)
        ax.axvline(cv, color=c, lw=0.7, ls='--')
        out[q] = round(float(cv), 2)
    ax.set_xlim(0, 30); ax.set_ylim(0, 0.17)
    ax.set_xlabel('Statistic ($LM$ or $Q$)'); ax.set_ylabel('Density')
    ax.text(29, 0.03, 'shaded: 5% of $H_0$', ha='right', fontsize=ANN, color=Navy)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch5_sem_primer_chi2')
    return out


# =============================================================================
# (5) standardised Student-t densities against the Normal, linear and log scale
# =============================================================================
def t_std_pdf(z, nu):
    s = np.sqrt((nu - 2) / nu)
    return stats.t.pdf(z / s, nu) / s


def fig_student_t():
    z = np.linspace(-6, 6, 801)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    out = {}
    for ax, log in zip(axes, [False, True]):
        ax.plot(z, stats.norm.pdf(z), color=MainBlue, lw=1.2, label='Normal')
        for nu, c in [(30, Forest), (6, Amber), (4, IDAred)]:
            ax.plot(z, t_std_pdf(z, nu), color=c, lw=1.1, label=rf'Student-$t$, $\nu$ = {nu}')
            out[nu] = round(float(2 * stats.t.sf(4 / np.sqrt((nu - 2) / nu), nu)), 5)
        if log:
            ax.set_yscale('log'); ax.set_ylim(1e-7, 1)
            ax.set_title('Log scale: the tails', loc='left')
        else:
            ax.set_title('Densities, all with variance 1', loc='left')
        ax.set_xlabel('$z$'); ax.set_ylabel('$f(z)$')
    out['normal'] = round(float(2 * stats.norm.sf(4)), 6)
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch5_sem_primer_student_t')
    return out


# =============================================================================
# (6) standardised residuals: clustering removed; QQ plot against Normal and Student-t
# =============================================================================
def fig_std_resid(n=2000, L=30):
    e, s2, z = simulate_garch(n, 0.05, 0.10, 0.85, nu=6, seed=3)
    zh = e / np.sqrt(s2)
    fig, axes = plt.subplots(1, 2, figsize=(5.55, 1.45))
    ax = axes[0]
    k = np.arange(1, L + 1)
    ax.bar(k - 0.2, acf(e ** 2, L), width=0.4, color=IDAred, label=r'ACF of $r_t^2$')
    ax.bar(k + 0.2, acf(zh ** 2, L), width=0.4, color=Forest, label=r'ACF of $\hat z_t^2$')
    b = 1.96 / np.sqrt(n)
    ax.axhspan(-b, b, color=Amber, alpha=0.3, lw=0, label=r'$\pm 1.96/\sqrt{n}$')
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Lag $k$'); ax.set_ylabel(r'$\hat\rho_k$')
    ax.set_title(r'Dividing by $\sigma_t$ removes the clustering', loc='left')
    ax = axes[1]
    zs = np.sort((zh - zh.mean()) / zh.std())
    pp = (np.arange(1, n + 1) - 0.5) / n
    qn = stats.norm.ppf(pp)
    qt = stats.t.ppf(pp, 6) * np.sqrt(4 / 6)
    ax.plot([-7, 7], [-7, 7], color=Navy, lw=0.8, ls='--', label='45-degree line')
    ax.plot(qn, zs, 'o', color=IDAred, ms=1.4, label='against Normal')
    ax.plot(qt, zs, 'o', color=MainBlue, ms=1.4, label=r'against Student-$t$(6)')
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6)
    ax.set_xlabel('Theoretical quantile'); ax.set_ylabel(r'Sorted $\hat z_t$')
    ax.set_title(r'QQ plot of $\hat z_t$ ($\nu$ = 6 in the simulation)', loc='left')
    bottom_legend(fig, axes, ncol=3)
    save_fig(fig, 'ch5_sem_primer_std_resid')
    return dict(acf1_r2=round(float(acf(e ** 2, 1)[0]), 3), acf1_z2=round(float(acf(zh ** 2, 1)[0]), 3))


# =============================================================================
# (7) news impact curve: GARCH against GJR
# =============================================================================
def fig_nic(omega=0.02, alpha=0.02, gamma=0.15, beta=0.88, s2prev=1.0):
    e = np.linspace(-4, 4, 401)
    g = omega + alpha * e ** 2 + beta * s2prev
    j = omega + (alpha + gamma * (e < 0)) * e ** 2 + beta * s2prev
    a_sym = alpha + gamma / 2
    gs = omega + a_sym * e ** 2 + beta * s2prev
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(e, j, color=IDAred, lw=1.3, label=rf'GJR: $\alpha$ = {alpha}, $\gamma$ = {gamma}')
    ax.plot(e, gs, color=MainBlue, lw=1.3, label=rf'GARCH: $\alpha$ = {a_sym:.3f}')
    for x in (-3, 3):
        y = omega + (alpha + gamma * (x < 0)) * x ** 2 + beta * s2prev
        ax.plot(x, y, 'o', color=IDAred, ms=3.2)
        ax.annotate(f'{y:.2f}', (x, y), xytext=(4, -9) if x < 0 else (-4, 5), textcoords='offset points',
                    ha='left' if x < 0 else 'right', fontsize=ANN, color=IDAred)
    ax.set_xlabel(r'Yesterday’s shock $\varepsilon_{t-1}$ (%)')
    ax.set_ylabel(r'$\sigma_t^2$')
    ax.set_xlim(-4, 4)
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch5_sem_primer_nic')
    return dict(m3=round(omega + (alpha + gamma) * 9 + beta, 2), p3=round(omega + alpha * 9 + beta, 2),
                garch3=round(omega + a_sym * 9 + beta, 3))


# =============================================================================
# (8) likelihood-ratio test: chi2(1) and the boundary mixture 1/2 chi2(0) + 1/2 chi2(1)
# =============================================================================
def fig_lr_boundary():
    x = np.linspace(0, 8, 500)
    fig, ax = plt.subplots(figsize=HALF)
    s1 = stats.chi2.sf(x, 1)
    ax.plot(x, s1, color=MainBlue, lw=1.3, label=r'$\chi^2_1$: $P(LR > x)$')
    ax.plot(x, 0.5 * s1, color=IDAred, lw=1.3, label=r'$\frac{1}{2}\chi^2_0 + \frac{1}{2}\chi^2_1$')
    ax.axhline(0.05, color=Navy, lw=0.7, ls=':')
    for cv, c in [(stats.chi2.ppf(0.95, 1), MainBlue), (stats.chi2.ppf(0.90, 1), IDAred)]:
        ax.axvline(cv, color=c, lw=0.7, ls='--')
        ax.text(cv + 0.1, 0.55, f'{cv:.2f}', color=c, fontsize=ANN)
    ax.text(7.9, 0.07, '5% level', ha='right', fontsize=ANN, color=Navy)
    ax.set_xlim(0, 8); ax.set_ylim(0, 1)
    ax.set_xlabel('$x$'); ax.set_ylabel(r'$P(LR > x)$ under $H_0$')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch5_sem_primer_lr_boundary')
    return dict(cv1=round(float(stats.chi2.ppf(0.95, 1)), 2), cvmix=round(float(stats.chi2.ppf(0.90, 1)), 2))


# =============================================================================
# (9) expected QLIKE and squared-error loss as functions of the forecast, true variance 1
# =============================================================================
def fig_qlike(s2=1.0):
    h = np.linspace(0.25, 3, 400)
    q = s2 / h + np.log(h)
    m = (h - s2) ** 2
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(h, q - (1 + np.log(s2)), color=IDAred, lw=1.3, label=r'QLIKE: $\sigma^2/h + \ln h$')
    ax.plot(h, m, color=MainBlue, lw=1.3, label=r'MSE: $(h - \sigma^2)^2$')
    ax.axvline(s2, color=Navy, lw=0.7, ls='--')
    for x in (0.5, 2.0):
        y = s2 / x + np.log(x) - 1
        ax.plot(x, y, 'o', color=IDAred, ms=3.2)
        ax.annotate(f'{y:.2f}', (x, y), xytext=(6, 2), textcoords='offset points', ha='left', fontsize=ANN,
                    color=IDAred)
    ax.set_xlim(0.25, 3); ax.set_ylim(0, 1.2)
    ax.set_xlabel(r'Forecast $h$ (true variance $\sigma^2$ = 1)')
    ax.set_ylabel('Excess expected loss')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch5_sem_primer_qlike')
    return dict(q_half=round(float(1 / 0.5 + np.log(0.5) - 1), 3), q_two=round(float(0.5 + np.log(2) - 1), 3))


# =============================================================================
# (10) benchmark forecasts on a simulated GARCH path: true variance, EWMA, Hist-20
# =============================================================================
def fig_benchmarks(n=400, lam=0.94, seed=31):
    e, s2, _ = simulate_garch(n, 0.05, 0.10, 0.85, nu=6, seed=seed)
    r2 = e ** 2
    ew = np.empty(n); ew[0] = r2[:20].mean()
    for t in range(1, n):
        ew[t] = lam * ew[t - 1] + (1 - lam) * r2[t - 1]
    hist = np.array([r2[max(0, t - 20):t].mean() if t >= 20 else np.nan for t in range(n)])
    fig, ax = plt.subplots(figsize=(5.55, 1.35))
    t = np.arange(n)
    ax.plot(t, r2, color=BandBlue, lw=0.6, label=r'Proxy $r_t^2$')
    ax.plot(t, s2, color=Navy, lw=1.2, label=r'True $\sigma_t^2$ = GARCH forecast')
    ax.plot(t, ew, color=IDAred, lw=1.0, label=rf'EWMA, $\lambda$ = {lam}')
    ax.plot(t, hist, color=Forest, lw=1.0, label='Hist-20')
    ax.set_ylim(0, np.nanpercentile(r2, 99.5))
    ax.set_xlim(0, n)
    ax.set_xlabel('Day $t$'); ax.set_ylabel('Variance (%$^2$)')
    bottom_legend(fig, ax, ncol=4)
    save_fig(fig, 'ch5_sem_primer_benchmarks')
    qlike = lambda h: float(np.nanmean((r2 / h + np.log(h))[20:]))
    return dict(qlike_true=round(qlike(s2), 4), qlike_ewma=round(qlike(ew), 4), qlike_hist=round(qlike(hist), 4))


# =============================================================================
# (11) Hansen's skewed Student-t against the symmetric one
# =============================================================================
def hansen_pdf(z, nu, lam):
    c = np.exp(gammaln((nu + 1) / 2) - gammaln(nu / 2)) / np.sqrt(np.pi * (nu - 2))
    a = 4 * lam * c * (nu - 2) / (nu - 1)
    b = np.sqrt(1 + 3 * lam ** 2 - a ** 2)
    s = np.where(z < -a / b, 1 - lam, 1 + lam)
    return b * c * (1 + ((b * z + a) / s) ** 2 / (nu - 2)) ** (-(nu + 1) / 2)


def fig_skewt(nu=7.7, lam=-0.15):
    z = np.linspace(-5, 5, 2001)
    f0, f1 = hansen_pdf(z, nu, 0.0), hansen_pdf(z, nu, lam)
    from scipy.integrate import quad
    m0 = quad(lambda x: x ** 2 * hansen_pdf(x, nu, 0.0), -np.inf, 0)[0]
    m1 = quad(lambda x: x ** 2 * hansen_pdf(x, nu, lam), -np.inf, 0)[0]
    p1 = quad(lambda x: hansen_pdf(x, nu, lam), -np.inf, 0)[0]
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(z, f0, color=MainBlue, lw=1.2, label=rf'$\lambda$ = 0 (symmetric)')
    ax.plot(z, f1, color=IDAred, lw=1.2, label=rf'$\lambda$ = {lam}')
    ax.fill_between(z[z < 0], 0, f1[z < 0], color=IDAred, alpha=0.18, lw=0)
    ax.axvline(0, color=Navy, lw=0.5, ls=':')
    ax.set_xlim(-5, 5); ax.set_ylim(0, 0.5)
    ax.set_xlabel('$z$'); ax.set_ylabel('$f(z)$')
    ax.set_title(rf'Hansen skewed-$t$, $\nu$ = {nu}, variance 1', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch5_sem_primer_skewt')
    return dict(m_minus_sym=round(m0, 3), m_minus=round(m1, 3), p_neg=round(p1, 3))


def run_all():
    res = {}
    res['clustering'] = fig_clustering()
    res['alpha_beta'] = fig_alpha_beta()
    res['forecast'] = fig_forecast()
    res['chi2'] = fig_chi2()
    res['student_t'] = fig_student_t()
    res['std_resid'] = fig_std_resid()
    res['nic'] = fig_nic()
    res['lr_boundary'] = fig_lr_boundary()
    res['qlike'] = fig_qlike()
    res['benchmarks'] = fig_benchmarks()
    res['skewt'] = fig_skewt()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

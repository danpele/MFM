"""
seminar19_explainers.py -- Explanatory (primer) charts for Seminar 19 (MFM): review, backtesting and projects
=============================================================================================================
Teaching charts for the primer slides "Prerequisites for Today" / "Noțiuni necesare azi" of Seminar 19,
which takes place BEFORE Lecture 19. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (the Hill estimator, a profile likelihood at a boundary and the half-life of a shock, rolling VaR
forecasts and their breaches, VaR and ES on a density, size and power of the Kupiec test, Bonferroni, Holm and
Benjamini--Hochberg thresholds, the look-ahead trap) and contain no exercise answers.

Output: charts/ch19_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_19/seminar19_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy import stats, optimize
from scipy.signal import lfilter

# course palette (no grey)
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Navy = '#1F2A44'
BandBlue = '#C5D2E8'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

# drawn at the size of their box on the slide (full width: 5.6 x 1.9 in; one column: 2.75 x 2.3 in),
# so that 1 pt in the figure is about 1 pt on the slide: texts 7-7.5 pt, never below 6.5 pt
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'axes.titlesize': 7.5, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'lines.markersize': 3.5, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.size': 2.5,
                     'ytick.major.size': 2.5, 'axes.titlepad': 3, 'axes.labelpad': 2,
                     'axes.facecolor': 'none', 'figure.facecolor': 'none', 'savefig.facecolor': 'none',
                     'text.color': 'black', 'axes.labelcolor': 'black', 'xtick.color': 'black',
                     'ytick.color': 'black', 'axes.edgecolor': Navy})

FULL = (5.6, 1.55)    # full slide width
HALF = (2.75, 1.85)   # half slide width (two-column layout)


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=300)
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


def unit_t(nu):
    """Student-t with nu degrees of freedom, rescaled to unit variance (nu > 2)."""
    return stats.t(nu, scale=np.sqrt((nu - 2) / nu))


def simulate_garch_t(T, omega=0.02, a=0.08, b=0.905, nu=6, seed=1, burn=1000):
    rng = np.random.default_rng(seed)
    z = unit_t(nu).rvs(T + burn, random_state=rng)
    r = np.empty(T + burn); s2 = np.empty(T + burn)
    v = omega / (1 - a - b)
    for t in range(T + burn):
        s2[t] = v
        r[t] = np.sqrt(v) * z[t]
        v = omega + a * r[t] ** 2 + b * v
    return r[burn:], np.sqrt(s2[burn:])


# =============================================================================
# (i) the Hill estimator: Hill plot and the log-log tail
# =============================================================================
def hill(losses, k):
    x = np.sort(losses)[::-1]
    return 1.0 / (np.mean(np.log(x[:k])) - np.log(x[k]))


def fig_hill(T=20000, nu=3, seed=4):
    rng = np.random.default_rng(seed)
    lt = stats.t(nu).rvs(T, random_state=rng)
    ln = rng.standard_normal(T)
    ks = np.arange(20, 601, 5)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    for x, col, lab in ((lt, IDAred, f'Student-$t$({nu}) losses, true $\\alpha$ = {nu}'), (ln, MainBlue, 'Normal losses')):
        L = x[x > 0]
        a = np.array([hill(L, k) for k in ks])
        ax.plot(ks, a, color=col, lw=1.3, label=lab)
        if col == IDAred:
            ax.fill_between(ks, a * (1 - 1.96 / np.sqrt(ks)), a * (1 + 1.96 / np.sqrt(ks)), color=BandBlue,
                            alpha=0.8, lw=0, label=r'95% band $\hat\alpha(1 \pm 1.96/\sqrt{k})$')
    ax.axhline(nu, color=Navy, lw=0.8, ls='--')
    ax.set_ylim(0, 8)
    ax.set_xlabel('Number $k$ of largest losses used')
    ax.set_ylabel(r'$\hat\alpha$')
    ax.set_title('Hill plot', loc='left')
    ax = axes[1]
    for x, col in ((lt, IDAred), (ln, MainBlue)):
        L = np.sort(x[x > 0])[::-1]
        sf = np.arange(1, len(L) + 1) / T
        ax.loglog(L, sf, '.', color=col, ms=1.5)
    g = np.logspace(np.log10(2), np.log10(40), 50)
    Lt_ = np.sort(lt[lt > 0])[::-1]
    anchor = np.mean(Lt_ > 4) * len(Lt_) / T            # empirical P(L > 4)
    ax.loglog(g, anchor * (g / 4) ** (-nu), color=Navy, lw=1.0, ls='--',
              label=rf'slope $-\alpha = -{nu}$')
    ax.set_xlim(0.5, 60); ax.set_ylim(3e-5, 1)
    ax.set_xlabel('Loss threshold $u$ (log)')
    ax.set_ylabel(r'$P(L > u)$ (log)')
    ax.set_title('Power-law tail: a straight line', loc='left')
    bottom_legend(fig, axes, ncol=4)
    save_fig(fig, 'ch19_sem_primer_hill')
    L = lt[lt > 0]
    return dict(hill_100=float(hill(L, 100)), hill_400=float(hill(L, 400)))


# =============================================================================
# (ii) profile likelihood of GARCH persistence near the boundary, and the half-life of a shock
# =============================================================================
def _garch_nll(params, r):
    mu, lw, s, p = params
    w = np.exp(lw); a, b = s * p, (1 - s) * p
    e = r - mu
    e2 = np.r_[np.var(e), e[:-1] ** 2]
    # sigma2_t = w + a e2_{t-1} + b sigma2_{t-1}: a linear filter
    s2 = lfilter([1.0], [1.0, -b], w + a * e2, zi=[b * np.var(e)])[0]
    s2 = np.maximum(s2, 1e-10)
    return 0.5 * np.sum(np.log(2 * np.pi * s2) + e ** 2 / s2)


def fig_profile(T=2000, seed=21):
    r, _ = simulate_garch_t(T, omega=0.01, a=0.075, b=0.92, nu=1000, seed=seed)   # Normal innovations, p = 0.995
    def prof(p):
        best = None
        for s0 in (0.05, 0.1, 0.2):
            res = optimize.minimize(lambda q: _garch_nll([q[0], q[1], q[2], p], r),
                                    [r.mean(), np.log(0.02), s0], method='L-BFGS-B',
                                    bounds=[(-1, 1), (-12, 2), (0.001, 0.6)])
            if best is None or res.fun < best.fun:
                best = res
        return best.fun
    full = optimize.minimize(lambda q: _garch_nll(q, r), [r.mean(), np.log(0.02), 0.08, 0.98], method='L-BFGS-B',
                             bounds=[(-1, 1), (-12, 2), (0.001, 0.6), (0.5, 0.99999)])
    phat = full.x[3]
    # Wald standard error of p from the inverse of the numerical Hessian of all four parameters
    xs = full.x.copy()
    hstep = np.array([1e-4, 1e-3, 1e-3, 1e-4])
    Hm = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            ei = np.eye(4)[i] * hstep[i]; ej = np.eye(4)[j] * hstep[j]
            Hm[i, j] = (_garch_nll(xs + ei + ej, r) - _garch_nll(xs + ei - ej, r) - _garch_nll(xs - ei + ej, r)
                        + _garch_nll(xs - ei - ej, r)) / (4 * hstep[i] * hstep[j])
    se = float(np.sqrt(np.linalg.inv(Hm)[3, 3]))
    grid = np.r_[np.linspace(0.965, 0.999, 69), 0.9995, 0.9999, 1.0]
    lp = np.array([prof(p) for p in grid])
    lmax = min(full.fun, lp.min())
    stat = 2 * (lp - lmax)
    inside = grid[((stat <= 3.84) & (grid < 1)) | ((grid == 1) & (stat <= 2.71))]
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(grid, stat, color=MainBlue, lw=1.4, label=r'LR stat.')
    ax.axhline(3.84, color=IDAred, lw=0.9, ls='--', label='3.84')
    ax.plot([1], [2.71], marker='D', color=IDAred, ms=3.5, ls='', label='2.71 ($p$ = 1)')
    ax.axvline(1, color=Navy, lw=0.8)
    ax.text(1.0022, 2.2, 'boundary\n$p = 1$', fontsize=7, color=Navy, va='top')
    ax.plot([phat - 1.96 * se, phat + 1.96 * se], [6.0, 6.0], color=Amber, lw=2.2, label='Wald CI')
    ax.plot([inside.min(), inside.max()], [5.0, 5.0], color=Forest, lw=2.2,
            label='profile CI')
    ax.set_xlim(0.965, 1.012); ax.set_ylim(0, 8)
    ax.set_xlabel('Persistence $p = \\alpha + \\beta$')
    ax.set_ylabel('LR statistic')
    ax.set_title(f'Simulated GARCH, $T$ = {T:,}', loc='left')
    ax = axes[1]
    hh = np.arange(0, 201)
    for p, col in ((0.95, Forest), (0.98, Amber), (0.99, MainBlue), (0.999, IDAred)):
        hl = np.log(0.5) / np.log(p)
        ax.plot(hh, p ** hh, color=col, lw=1.3, label=f'$p$ = {p:g} ({hl:.0f} days)')
    ax.axhline(0.5, color=Navy, lw=0.7, ls=':')
    ax.set_xlabel('Days $h$ after a variance shock')
    ax.set_ylabel('Remaining share $p^h$')
    ax.set_title('Decay of a shock', loc='left')
    bottom_legend(fig, axes, ncol=5)
    save_fig(fig, 'ch19_sem_primer_profile')
    return dict(phat=float(phat), se=float(se), wald=[float(phat - 1.96 * se), float(phat + 1.96 * se)],
                prof_lo=float(inside.min()), stat_at_1=float(stat[-1]))


# =============================================================================
# (iii) rolling VaR forecasts on a simulated GARCH-t path and their breaches
# =============================================================================
def fig_var_paths(T=1500, win=500, nu=5, seed=8, alpha=0.01):
    r, sig = simulate_garch_t(T + win, omega=0.02, a=0.09, b=0.90, nu=nu, seed=seed)
    L = -r
    t_ = np.arange(win, T + win)
    hs = np.array([np.quantile(L[t - win:t], 1 - alpha) for t in t_])
    nm = np.array([-(r[t - win:t].mean() + r[t - win:t].std(ddof=1) * stats.norm.ppf(alpha)) for t in t_])
    ga = -sig[t_] * unit_t(nu).ppf(alpha)
    Lt = L[t_]
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 1.6), gridspec_kw=dict(width_ratios=[2, 1]))
    ax = axes[0]
    ax.plot(np.arange(T), Lt, color=BandBlue, lw=0.5, label='loss $L_t$')
    out = {}
    for v, col, lab in ((hs, Amber, 'HS (500 days)'), (nm, Forest, 'Normal (500 days)'), (ga, IDAred, 'GARCH-$t$')):
        ax.plot(np.arange(T), v, color=col, lw=0.9, label=lab)
        hit = Lt > v
        out[lab] = int(hit.sum())
        ax.plot(np.arange(T)[hit], Lt[hit], 'o', color=col, ms=2.2)
    ax.set_xlim(0, T)
    ax.set_xlabel('Forecast day $t$')
    ax.set_ylabel('Loss and VaR 1% (%)')
    ax.set_title('Breaches: dots above the VaR line', loc='left')
    ax = axes[1]
    for v, col in ((hs, Amber), (nm, Forest), (ga, IDAred)):
        ax.plot(np.arange(T), np.cumsum(Lt > v) - alpha * np.arange(1, T + 1), color=col, lw=1.1)
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Forecast day $t$')
    ax.set_ylabel('Breaches $-$ expected')
    ax.set_title('Cumulative excess', loc='left')
    bottom_legend(fig, axes[0], ncol=4)
    save_fig(fig, 'ch19_sem_primer_var_paths')
    out['expected'] = alpha * T
    return out


# =============================================================================
# (iv) VaR 1% and ES 2.5% on a Normal and a Student-t density with the same variance
# =============================================================================
def fig_var_es(nu=5):
    td = unit_t(nu)
    x = np.linspace(-4.5, 1, 900)
    fig, ax = plt.subplots(figsize=(2.75, 1.9))
    out = {}
    for dist, col, lab in ((stats.norm(), MainBlue, 'Normal'), (td, IDAred, f'Student-$t$({nu})')):
        ax.plot(x, dist.pdf(x), color=col, lw=1.3, label=f'{lab}, variance 1')
        v = -dist.ppf(0.01)
        q = dist.ppf(0.025)
        es = -dist.expect(lambda y: y, ub=q) / 0.025
        out[lab] = dict(var1=float(v), es25=float(es))
        ax.axvline(-v, color=col, lw=0.9, ls='--')
        ax.axvline(-es, color=col, lw=0.9, ls=':')
    ax.set_xlim(-4.5, 1); ax.set_yscale('log'); ax.set_ylim(1e-3, 1)
    ax.set_xlabel('Return $r$ (standard deviations)')
    ax.set_ylabel('Density (log)')
    ax.set_title('Left tail, same variance', loc='left')
    handles = [Line2D([], [], color=MainBlue, lw=1.3), Line2D([], [], color=IDAred, lw=1.3),
               Line2D([], [], color=Navy, lw=0.9, ls='--'), Line2D([], [], color=Navy, lw=0.9, ls=':')]
    n_, t_ = out['Normal'], out[f'Student-$t$({nu})']
    bottom_legend(fig, ncol=2, handles=handles,
                  labels=[f"Normal: VaR {n_['var1']:.2f}, ES {n_['es25']:.2f}",
                          f"Student-$t$({nu}): VaR {t_['var1']:.2f}, ES {t_['es25']:.2f}", '$-$VaR 1%', '$-$ES 2.5%'])
    save_fig(fig, 'ch19_sem_primer_var_es')
    return out


# =============================================================================
# (v) size and power of the Kupiec test: the binomial distribution and power curves
# =============================================================================
def kupiec_lr(T, x, p=0.01):
    ph = x / T
    l0 = (T - x) * np.log(1 - p) + x * np.log(p)
    l1 = ((T - x) * np.log(1 - ph) if x < T else 0) + (x * np.log(ph) if x > 0 else 0)
    return -2 * (l0 - l1)


def region(T, p=0.01):
    xs = np.arange(0, int(T * 0.1) + 1)
    return xs[np.array([kupiec_lr(T, x, p) for x in xs]) > stats.chi2.ppf(0.95, 1)]


def fig_kupiec(T=500, pi1=0.025):
    R = region(T)
    xs = np.arange(0, 26)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    w = 0.4
    for pi, col, off in ((0.01, MainBlue, -w / 2), (pi1, IDAred, w / 2)):
        pm = stats.binom.pmf(xs, T, pi)
        ax.bar(xs + off, pm, width=w, color=col, alpha=0.85,
               label=f'true rate {100 * pi:g}%')
    for x in R[R <= 25]:
        ax.axvspan(x - 0.5, x + 0.5, color=BandBlue, alpha=0.6, lw=0, zorder=0)
    size = stats.binom.pmf(R, T, 0.01).sum()
    power = stats.binom.pmf(R, T, pi1).sum()
    ax.set_xlim(-0.6, 25.5)
    ax.set_xlabel(f'Number of breaches $x$ in $T$ = {T} days')
    ax.set_ylabel('$P(X = x)$')
    ax.set_title(f'Size {size:.3f}, power {power:.2f} (shaded: reject)', loc='left')
    ax = axes[1]
    Ts = np.arange(100, 2001, 25)
    for pi, col in ((0.01, Navy), (0.015, Forest), (0.02, Amber), (0.03, IDAred)):
        pw = [stats.binom.pmf(region(t), t, pi).sum() for t in Ts]
        ax.plot(Ts, pw, color=col, lw=1.2, label=f'_{pi}')
        xl = {0.01: 1700, 0.015: 1500, 0.02: 1000, 0.03: 330}[pi]
        ax.text(xl, np.interp(xl, Ts, pw) + 0.06, f'{100 * pi:g}%', fontsize=7, color=col, va='bottom', ha='center')
    ax.axhline(0.05, color=Navy, lw=0.6, ls=':')
    ax.set_xlim(100, 2000); ax.set_ylim(0, 1.1)
    ax.set_xlabel('Backtest length $T$ (days)')
    ax.set_ylabel('Rejection probability')
    ax.set_title('Power by true rate (1%: size)', loc='left')
    bottom_legend(fig, axes[0], ncol=3, handles=[Patch(color=MainBlue), Patch(color=IDAred), Patch(color=BandBlue)],
                  labels=['true rate 1% (model correct)', f'true rate {100 * pi1:g}%', 'rejection region $LR_{uc} > 3.84$'])
    save_fig(fig, 'ch19_sem_primer_kupiec')
    return dict(R=R.tolist()[:12], size=float(size), power=float(power))


# =============================================================================
# (vi) Bonferroni, Holm and Benjamini--Hochberg thresholds on simulated p-values
# =============================================================================
def fig_holm_bh(m=20, seed=5):
    rng = np.random.default_rng(seed)
    z = np.r_[rng.normal(2.8, 1, 6), rng.normal(0, 1, m - 6)]
    p = np.sort(stats.norm.sf(z))
    k = np.arange(1, m + 1)
    holm = 0.05 / (m - k + 1)
    bh = 0.05 * k / m
    n_holm = int(np.argmax(p > holm)) if (p > holm).any() else m
    ok = np.where(p <= bh)[0]
    n_bh = int(ok.max() + 1) if len(ok) else 0
    n_bonf = int((p <= 0.05 / m).sum())
    fig, ax = plt.subplots(figsize=(2.75, 1.95))
    ax.plot(k, p, 'o', color=Navy, ms=3.2, label='sorted $p_{(k)}$')
    ax.plot(k, np.full(m, 0.05 / m), color=MainBlue, lw=1.0, ls=':', label='Bonferroni')
    ax.plot(k, holm, color=IDAred, lw=1.1, ls='--', label='Holm')
    ax.plot(k, bh, color=Forest, lw=1.1, label='BH')
    ax.axhline(0.05, color=Amber, lw=0.9, ls='-.', label='0.05')
    ax.set_yscale('log'); ax.set_ylim(1e-5, 1.5)
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Rank $k$')
    ax.set_ylabel('$p$-value (log)')
    ax.set_title(f'Rejections: Bonf. {n_bonf}, Holm {n_holm}, BH {n_bh}, raw {int((p <= 0.05).sum())}', loc='left')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch19_sem_primer_holm_bh')
    return dict(p=p.round(4).tolist(), bonf=n_bonf, holm=n_holm, bh=n_bh, raw=int((p <= 0.05).sum()))


# =============================================================================
# (vii) the look-ahead trap: rolling against full-sample historical simulation
# =============================================================================
def fig_lookahead(T=2500, win=500, seed=14, alpha=0.01):
    r, _ = simulate_garch_t(T + win, omega=0.02, a=0.09, b=0.90, nu=5, seed=seed)
    L = -r
    t_ = np.arange(win, T + win)
    Lt = L[t_]
    roll = np.array([np.quantile(L[t - win:t], 1 - alpha) for t in t_])
    full = np.quantile(Lt, 1 - alpha)
    fig, ax = plt.subplots(figsize=(2.75, 1.85))
    c_roll = np.cumsum(Lt > roll) - alpha * np.arange(1, T + 1)
    c_full = np.cumsum(Lt > full) - alpha * np.arange(1, T + 1)
    ax.plot(c_roll, color=MainBlue, lw=1.2, label=f'rolling HS: {int((Lt > roll).sum())} breaches')
    ax.plot(c_full, color=IDAred, lw=1.2, label=f'full-sample HS: {int((Lt > full).sum())} breaches')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Forecast day $t$')
    ax.set_ylabel('Breaches $-$ expected')
    ax.set_title(f'{alpha * T:.0f} breaches expected', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch19_sem_primer_lookahead')
    return dict(roll=int((Lt > roll).sum()), full=int((Lt > full).sum()), expected=alpha * T)


def run_all():
    res = {}
    res['hill'] = fig_hill()
    res['profile'] = fig_profile()
    res['var_paths'] = fig_var_paths()
    res['var_es'] = fig_var_es()
    res['kupiec'] = fig_kupiec()
    res['holm_bh'] = fig_holm_bh()
    res['lookahead'] = fig_lookahead()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

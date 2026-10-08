"""
seminar15_explainers.py -- Explanatory (primer) charts for Seminar 15 (MFM): LLMs and sentiment analysis
=========================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 15, which
takes place BEFORE Lecture 15. All charts use SIMULATED or textbook data only (fixed seeds): they illustrate the
concepts (softmax with temperature, confusion-matrix metrics, attenuation from misclassification, the McNemar test
and its power, the paired bootstrap, AUC and the ROC curve, timing of news and returns, clustered standard errors,
break-even costs, calibration) and contain no exercise answers.

The charts are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide), so that every
text is at least 6.3 pt on the slide.

Output: charts/ch15_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).

Run:  python3 Quantlets/Ch_15/seminar15_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch
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


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), transparent=True, dpi=220)
    plt.close(fig)
    print(f'   saved {name}')


def softmax(z, T):
    e = np.exp((z - z.max()) / T)
    return e / e.sum()


# =============================================================================
# (1) softmax with temperature: probabilities and net score as functions of T
# =============================================================================
def fig_softmax():
    z = np.array([2.0, 1.0, 0.0])               # logits of (pos, neu, neg)
    Ts = np.exp(np.linspace(np.log(0.25), np.log(20), 300))
    P = np.array([softmax(z, T) for T in Ts])
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    for k, (lab, c) in enumerate([('$p_{\\mathrm{pos}}$ (logit 2)', Forest), ('$p_{\\mathrm{neu}}$ (logit 1)', Amber),
                                   ('$p_{\\mathrm{neg}}$ (logit 0)', IDAred)]):
        ax.plot(Ts, P[:, k], color=c, label=lab)
    ax.axhline(1 / 3, color=Navy, lw=0.7, ls=':', label='$1/3$: all answers equally likely')
    for T in (1, 2):
        ax.axvline(T, color=MainBlue, lw=0.6, ls='--')
    ax.set_xscale('log')
    ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20], ['0.25', '0.5', '1', '2', '5', '10', '20'])
    ax.set_xlabel('Temperature $T$ (log scale)')
    ax.set_ylabel('Probability $p_k(T)$')
    ax.set_title('Same logits $z = (2, 1, 0)$, different $T$', loc='left')
    ax = axes[1]
    s = P[:, 0] - P[:, 2]
    ax.plot(Ts, s, color=MainBlue, label='Net score $s = p_{\\mathrm{pos}} - p_{\\mathrm{neg}}$')
    for T, c in ((1, Navy), (2, Navy)):
        v = softmax(z, T)
        ax.plot(T, v[0] - v[2], 'o', color=IDAred, ms=3.5)
        ax.annotate(f'$T = {T}$: $s = {v[0] - v[2]:.3f}$', (T, v[0] - v[2]), xytext=(6, 2),
                    textcoords='offset points', fontsize=6.8, color=IDAred)
    ax.set_xscale('log')
    ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20], ['0.25', '0.5', '1', '2', '5', '10', '20'])
    ax.set_ylim(0, 1)
    ax.set_xlabel('Temperature $T$ (log scale)')
    ax.set_ylabel('$s$')
    ax.set_title('Larger $T$ pulls the score towards 0', loc='left')
    h, l = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    legend_below(fig, h + h2, l + l2, 3)
    save_fig(fig, 'ch15_sem_primer_softmax')
    return {T: softmax(z, T).round(3).tolist() for T in (1, 2)}


# =============================================================================
# (2) confusion matrix of the primer example and the metrics it gives
# =============================================================================
def fig_metrics():
    # 100 headlines, 20 truly negative; flagged: 18 of them and 8 of the other 80
    cm = np.array([[18, 2], [8, 72]])            # rows: truth (neg, other); columns: predicted (neg, other)
    fig, axes = figure(FULL, 2, gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax = axes[0]
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('b', ['#FFFFFF', BandBlue, MainBlue])
    ax.imshow(cm, cmap=cmap, vmin=0, vmax=90, aspect='auto')
    names = [['TP = 18\nhit', 'FN = 2\nmiss'], ['FP = 8\nfalse alarm', 'TN = 72\ncorrect rejection']]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, names[i][j], ha='center', va='center', fontsize=6.8,
                    color='white' if cm[i, j] > 50 else Navy)
    ax.set_xticks([0, 1], ['negative', 'other'])
    ax.set_yticks([0, 1], ['negative', 'other'])
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('Human label (truth)')
    ax.set_title('Confusion matrix, 100 headlines', loc='left')
    ax.tick_params(length=0)
    ax = axes[1]
    acc = (18 + 72) / 100
    prec_n, rec_n = 18 / 26, 18 / 20
    f1_n = 2 * prec_n * rec_n / (prec_n + rec_n)
    prec_o, rec_o = 72 / 74, 72 / 80
    f1_o = 2 * prec_o * rec_o / (prec_o + rec_o)
    macro = (f1_n + f1_o) / 2
    f1_o_never = 2 * 0.8 * 1 / (0.8 + 1)
    vals = [(acc, 0.80), (macro, (0 + f1_o_never) / 2)]
    x = np.arange(2)
    w = 0.36
    ax.bar(x - w / 2, [v[0] for v in vals], w, color=MainBlue, label='Model of the example')
    ax.bar(x + w / 2, [v[1] for v in vals], w, color=Amber, label='"Never negative" (majority class)')
    for xi, (a, b) in zip(x, vals):
        ax.text(xi - w / 2, a + 0.02, f'{a:.2f}', ha='center', va='bottom', fontsize=6.8, color=MainBlue)
        ax.text(xi + w / 2, b + 0.02, f'{b:.2f}', ha='center', va='bottom', fontsize=6.8, color=Amber)
    ax.set_xticks(x, ['Accuracy', 'Macro-F1'])
    ax.set_ylim(0, 1.12)
    ax.set_ylabel('Score')
    ax.set_title('The trivial rule fools accuracy', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 2)
    save_fig(fig, 'ch15_sem_primer_metrics')
    return dict(acc=acc, f1_neg=f1_n, f1_other=f1_o, macro=macro, macro_never=(0 + f1_o_never) / 2)


# =============================================================================
# (3) attenuation: slope on a misclassified dummy, simulated, and lambda against the error rate
# =============================================================================
def lam(pi, a0, a1):
    p = pi * (1 - a1) + (1 - pi) * a0
    return pi * (1 - pi) * (1 - a0 - a1) / (p * (1 - p))


def fig_attenuation(seed=7, n=400, pi=0.25, a0=0.15, a1=0.25, beta=1.0):
    rng = np.random.default_rng(seed)
    s = (rng.random(n) < pi).astype(float)
    flip = np.where(s == 1, rng.random(n) < a1, rng.random(n) < a0)
    sh = np.where(flip, 1 - s, s)
    r = beta * s + rng.normal(0, 0.8, n)
    b_true = np.polyfit(s, r, 1)[0]
    b_obs = np.polyfit(sh, r, 1)[0]
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    jit = rng.uniform(-0.12, 0.12, n)
    ax.plot(s - 0.17 + jit * 0.7, r, 'o', ms=1.6, color=MainBlue, alpha=0.55)
    ax.plot(sh + 0.17 + jit * 0.7, r, 'o', ms=1.6, color=IDAred, alpha=0.55)
    xx = np.array([-0.1, 1.1])
    ax.plot(xx - 0.17, r[s == 0].mean() + b_true * (xx), color=MainBlue, lw=1.3,
            label=f'on the truth $s^*$: slope {b_true:.2f}')
    ax.plot(xx + 0.17, r[sh == 0].mean() + b_obs * (xx), color=IDAred, lw=1.3,
            label=f'on the label $\\hat s$: slope {b_obs:.2f}')
    ax.set_xticks([0, 1], ['0 (not negative)', '1 (negative)'])
    ax.set_ylabel('Outcome $r$')
    ax.set_title(f'Simulated, true $\\beta = 1$, $\\lambda = {lam(pi, a0, a1):.2f}$', loc='left')
    ax = axes[1]
    a = np.linspace(0, 0.5, 200)
    for pi_, c in ((0.5, Forest), (0.15, Navy)):
        ax.plot(a, [lam(pi_, x, x) for x in a], color=c, label=f'$\\lambda$, $\\pi = {pi_}$, $\\alpha_0 = \\alpha_1$')
    ax.plot(a, [lam(0.15, x, 0.0) for x in a], color=Amber, ls='--', label='$\\lambda$, $\\pi = 0.15$, only false alarms')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Error rate')
    ax.set_ylabel('$\\lambda = \\mathrm{plim}\\,\\hat b / \\beta$')
    ax.set_ylim(-0.05, 1.05)
    ax.set_title('Share of the true slope that survives', loc='left')
    h, l = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    legend_below(fig, h + h2, l + l2, 3)
    save_fig(fig, 'ch15_sem_primer_attenuation')
    return dict(b_true=b_true, b_obs=b_obs, lam=lam(pi, a0, a1))


# =============================================================================
# (4) McNemar: exact null distribution of n01 and power against n
# =============================================================================
def fig_mcnemar(nd=40, n01=27, d=0.03, q=0.30):
    fig, axes = figure(FULL, 2)
    ax = axes[0]
    k = np.arange(nd + 1)
    pmf = stats.binom.pmf(k, nd, 0.5)
    tail = (k >= n01) | (k <= nd - n01)
    ax.bar(k[~tail], pmf[~tail], width=0.85, color=BandBlue, label=f'$P(n_{{01}} = k)$ under $H_0$: Bin$({nd}, 0.5)$')
    ax.bar(k[tail], pmf[tail], width=0.85, color=IDAred, label='as or more extreme than observed')
    ax.axvline(n01, color=Navy, lw=0.8, ls='--')
    p = min(1, 2 * stats.binom.sf(n01 - 1, nd, 0.5))
    ax.annotate(f'observed $n_{{01}} = {n01}$\nexact $p = {p:.3f}$', (n01, pmf.max() * 0.55), xytext=(6, 0),
                textcoords='offset points', fontsize=6.8, color=Navy)
    ax.set_xlabel('$k$, among $n_{01} + n_{10} = %d$ discordant texts' % nd)
    ax.set_ylabel('Probability')
    ax.set_title('Exact McNemar test: a Binomial with $p = 1/2$', loc='left')
    ax = axes[1]
    n = np.linspace(50, 4000, 400)
    for d_, c in ((0.03, MainBlue), (0.05, Forest), (0.12, Amber)):
        pw = stats.norm.cdf(d_ * np.sqrt(n) / np.sqrt(q - d_ ** 2) - 1.96)
        n80 = (1.96 + 0.8416) ** 2 * (q - d_ ** 2) / d_ ** 2
        ax.plot(n, pw, color=c, label=f'$d = {d_:.2f}$, $n_{{80}} = {n80:.0f}$')
    ax.axhline(0.8, color=IDAred, lw=0.7, ls='--', label='80% power')
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('Number of texts $n$')
    ax.set_ylabel('Power')
    ax.set_title(f'Power of the paired test, $q = {q}$', loc='left')
    h, l = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    legend_below(fig, h + h2, l + l2, 3)
    save_fig(fig, 'ch15_sem_primer_mcnemar')
    return dict(p=p)


# =============================================================================
# (5) paired bootstrap: accuracy difference of two classifiers on the same simulated texts
# =============================================================================
def fig_bootstrap(seed=3, n=600, B=2000):
    rng = np.random.default_rng(seed)
    u = rng.random(n)                            # difficulty of each text: shared by both classifiers
    okA = u > 0.35
    okB = np.where(rng.random(n) < 0.2, rng.random(n) > 0.30, u > 0.30)   # B agrees with A on most texts
    idx = rng.integers(0, n, (B, n))
    dA, dB = okA[idx].mean(1), okB[idx].mean(1)
    paired = dB - dA
    # unpaired: independent resamples for each classifier
    idx2 = rng.integers(0, n, (B, n))
    unpaired = okB[idx2].mean(1) - dA
    fig, ax = figure(HALF)
    bins = np.arange(-0.06, 0.14, 3 / n) + 0.5 / n     # aligned with the steps 1/n of an accuracy
    ax.hist(unpaired, bins=bins, color=BandBlue, label='Independent resamples (ignores pairing)')
    ax.hist(paired, bins=bins, color=MainBlue, alpha=0.75, label='Paired: same texts for A and B')
    lo, hi = np.percentile(paired, [2.5, 97.5])
    for v in (lo, hi):
        ax.axvline(v, color=IDAred, lw=0.9, ls='--')
    ax.axvline(0, color=Navy, lw=0.7)
    ax.text(hi, ax.get_ylim()[1] * 0.92, f' 95% CI\n [{lo:.3f}; {hi:.3f}]', color=IDAred, fontsize=6.8, va='top')
    ax.set_xlabel('Bootstrap $\\mathrm{acc}^*_B - \\mathrm{acc}^*_A$')
    ax.set_ylabel('Resamples')
    ax.set_title(f'$B = {B}$ resamples of $n = {n}$ simulated texts', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h + [Line2D([], [], color=IDAred, ls='--')], l + ['2.5% and 97.5% percentiles'], 1)
    save_fig(fig, 'ch15_sem_primer_bootstrap')
    return dict(lo=lo, hi=hi, sd_paired=paired.std(), sd_unpaired=unpaired.std())


# =============================================================================
# (6) AUC: score densities of the two groups and the ROC curve
# =============================================================================
def fig_auc(seed=5, n1=150, n0=100, shift=0.8):
    rng = np.random.default_rng(seed)
    up = rng.normal(shift, 1, n1)
    down = rng.normal(0, 1, n0)
    U = (up[:, None] > down[None, :]).sum() + 0.5 * (up[:, None] == down[None, :]).sum()
    auc = U / (n1 * n0)
    fig, axes = figure(FULL, 2, gridspec_kw=dict(width_ratios=[1.3, 1]))
    ax = axes[0]
    xs = np.linspace(-3.5, 4.5, 300)
    ax.fill_between(xs, stats.gaussian_kde(down)(xs), color=IDAred, alpha=0.22, lw=0, label='"down" months')
    ax.fill_between(xs, stats.gaussian_kde(up)(xs), color=Forest, alpha=0.22, lw=0, label='"up" months')
    ax.plot(xs, stats.gaussian_kde(down)(xs), color=IDAred, lw=0.9)
    ax.plot(xs, stats.gaussian_kde(up)(xs), color=Forest, lw=0.9)
    thr = 0.5
    ax.axvline(thr, color=Navy, lw=0.8, ls='--', label='a threshold $c$')
    ax.set_xlabel('Model score (e.g. $P(\\mathrm{rise})$, any monotone scale)')
    ax.set_ylabel('Density')
    ax.set_title('Simulated scores of the two groups', loc='left')
    ax = axes[1]
    thr_grid = np.r_[np.inf, np.sort(np.r_[up, down])[::-1], -np.inf]
    tpr = [(up >= c).mean() for c in thr_grid]
    fpr = [(down >= c).mean() for c in thr_grid]
    ax.fill_between(fpr, tpr, color=BandBlue, lw=0, label=f'area = AUC = {auc:.2f}')
    ax.plot(fpr, tpr, color=MainBlue, lw=1.1, label='ROC curve')
    ax.plot([0, 1], [0, 1], color=Navy, lw=0.7, ls=':', label='no information: AUC = 0.5')
    c_fpr, c_tpr = (down >= thr).mean(), (up >= thr).mean()
    ax.plot(c_fpr, c_tpr, 'o', color=IDAred, ms=3.5)
    ax.annotate('threshold $c$', (c_fpr, c_tpr), xytext=(-48, 5), textcoords='offset points', fontsize=6.8,
                color=IDAred)
    ax.set_xlabel('False-positive rate ("down" above $c$)')
    ax.set_ylabel('True-positive rate')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('ROC curve over all thresholds', loc='left')
    h, l = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    legend_below(fig, h + h2, l + l2, 3)
    save_fig(fig, 'ch15_sem_primer_auc')
    return dict(auc=auc, U=U)


# =============================================================================
# (7) timing of a headline and an event study with a pure reaction
# =============================================================================
def fig_timing(seed=11, n_ev=400):
    fig, axes = figure(FULL, 2, gridspec_kw=dict(width_ratios=[1.45, 1]))
    ax = axes[0]
    days = ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu']
    for i, dname in enumerate(days):
        trade = dname not in ('Sat', 'Sun')
        ax.add_patch(plt.Rectangle((i - 0.42, 0.62), 0.84, 0.36, fc=BandBlue if trade else 'white', ec=Navy, lw=0.6))
        ax.text(i, 0.8, dname, ha='center', va='center', fontsize=7)
    labels = {0: ('headline\n(date\nonly)', Amber), 2: ('day $d$\n$h = 0$', IDAred), 3: ('$d + 1$\nbuy at\nclose', MainBlue),
              4: ('$d + 2$\nfirst\ntradable\nreturn', Forest)}
    for i, (t, c) in labels.items():
        ax.text(i, 0.55, t, ha='center', va='top', fontsize=6.5, color=c, linespacing=1.05)
    ax.annotate('', xy=(2, 1.12), xytext=(0, 1.12), arrowprops=dict(arrowstyle='->', color=Amber, lw=0.9))
    ax.annotate('', xy=(4, 1.12), xytext=(3, 1.12), arrowprops=dict(arrowstyle='->', color=Forest, lw=0.9))
    ax.text(1, 1.2, 'next trading day', ha='center', fontsize=6.5, color=Amber)
    ax.text(3.5, 1.2, 'held one day', ha='center', fontsize=6.5, color=Forest)
    ax.set_xlim(-0.55, 5.55)
    ax.set_ylim(-0.02, 1.32)
    ax.axis('off')
    ax.set_title('From a calendar date to the tradable return', loc='left')
    ax = axes[1]
    rng = np.random.default_rng(seed)
    h = np.arange(-5, 6)
    for sign, c, lab in ((1, Forest, 'positive news'), (-1, IDAred, 'negative news')):
        ret = rng.normal(0, 1.2, (n_ev, h.size)) / np.sqrt(n_ev) * 4
        ret[:, h == 0] += sign * 0.8                     # the whole reaction on day 0
        car = np.cumsum(ret.mean(0))
        ax.plot(h, car, 'o-', color=c, ms=2.5, label=f'CAR, {lab}')
    ax.axvspan(-0.5, 0.5, color=BandBlue, lw=0, label='day $d$: reaction')
    ax.axvspan(1.5, 5.5, color=Amber, alpha=0.15, lw=0, label='$h \\geq 2$: prediction')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.set_xlabel('Trading days $h$ after day $d$')
    ax.set_ylabel('CAR (%)')
    ax.set_title('Simulated: all news priced on day $d$', loc='left')
    hh, ll = ax.get_legend_handles_labels()
    legend_below(fig, hh, ll, 4)
    save_fig(fig, 'ch15_sem_primer_timing')


# =============================================================================
# (8) clustered errors: t-statistics of a zero slope with OLS and with clustered standard errors
# =============================================================================
def cluster_t(y, x, g):
    X = np.column_stack([np.ones_like(x), x])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    u = y - X @ b
    n = len(y)
    s2 = u @ u / (n - 2)
    se_ols = np.sqrt(s2 * XtXi[1, 1])
    meat = np.zeros((2, 2))
    for k in np.unique(g):
        m = g == k
        v = X[m].T @ u[m]
        meat += np.outer(v, v)
    G = len(np.unique(g))
    V = XtXi @ meat @ XtXi * G / (G - 1) * (n - 1) / (n - 2)
    return b[1] / se_ols, b[1] / np.sqrt(V[1, 1])


def fig_cluster(seed=2, G=16, Tg=60, R=2000):
    rng = np.random.default_rng(seed)
    g = np.repeat(np.arange(G), Tg)
    t_ols, t_cl = [], []
    for _ in range(R):
        x = rng.normal(0, 1, G)[g] * 0.8 + rng.normal(0, 0.6, G * Tg)     # regressor persistent within a stock
        e = rng.normal(0, 1, G)[g] * 0.7 + rng.normal(0, 1, G * Tg)        # error shared within a stock
        a, b = cluster_t(e, x, g)                                          # true slope 0
        t_ols.append(a)
        t_cl.append(b)
    t_ols, t_cl = np.array(t_ols), np.array(t_cl)
    fig, ax = figure(HALF)
    bins = np.linspace(-8, 8, 61)
    ax.hist(t_ols, bins=bins, density=True, color=BandBlue, label=f'OLS SE: rejects {100 * np.mean(abs(t_ols) > 1.96):.0f}%')
    ax.hist(t_cl, bins=bins, density=True, color=MainBlue, alpha=0.6,
            label=f'clustered SE, $t_{{15}}$ value: rejects {100 * np.mean(abs(t_cl) > stats.t.ppf(0.975, G - 1)):.0f}%')
    xs = np.linspace(-8, 8, 300)
    ax.plot(xs, stats.norm.pdf(xs), color=IDAred, lw=1.0, label='$N(0, 1)$, the reference')
    ax.plot(xs, stats.t.pdf(xs, G - 1), color=Amber, lw=1.0, ls='--', label='$t_{15}$, $G = 16$ clusters')
    ax.set_xlabel('$t$-statistic of a slope that is truly 0')
    ax.set_ylabel('Density')
    ax.set_title(f'Simulated panel: {G} stocks $\\times$ {Tg} days', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch15_sem_primer_cluster')
    return dict(rej_ols=np.mean(abs(t_ols) > 1.96), rej_cl=np.mean(abs(t_cl) > stats.t.ppf(0.975, G - 1)),
                rej_cl_norm=np.mean(abs(t_cl) > 1.96))


# =============================================================================
# (9) costs: net Sharpe ratio against the cost per trade, break-even cost and its delta-method interval
# =============================================================================
def fig_cost(mu=4.0, t=1.6, a=1.0, sigma=150.0, A=252):
    c = np.linspace(0, 6, 300)
    sr = np.sqrt(A) * (mu - 4 * a * c) / sigma
    cstar = mu / (4 * a)
    se = (mu / t) / (4 * a)
    fig, ax = figure(HALF)
    ax.axvspan(cstar - 1.96 * se, cstar + 1.96 * se, color=BandBlue, lw=0, label='95% CI of $c^*$ (delta method)')
    ax.plot(c, sr, color=MainBlue, label='$SR_{\\mathrm{net}}(c) = \\sqrt{A}\\,(\\mu - 4ac)/\\sigma$')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.axvline(cstar, color=IDAred, lw=0.9, ls='--', label=f'break-even $c^* = \\mu/(4a) = {cstar:.1f}$ bp')
    ax.set_xlabel('Cost per trade $c$ (bp)')
    ax.set_ylabel('Annualised net Sharpe ratio')
    ax.set_title(f'Illustration: $\\mu = {mu:.0f}$ bp, $t = {t}$, $a = 1$, $\\sigma = {sigma:.0f}$ bp', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch15_sem_primer_cost')
    return dict(cstar=cstar, se=se)


# =============================================================================
# (10) calibration: reliability diagram of an overconfident model, before and after temperature scaling
# =============================================================================
def fig_calibration(seed=9, n=6000, T_true=2.5):
    rng = np.random.default_rng(seed)
    z_true = rng.normal(0, 1.4, (n, 3))
    p_true = np.exp(z_true) / np.exp(z_true).sum(1, keepdims=True)
    y = np.array([rng.choice(3, p=pi) for pi in p_true])
    z_model = z_true * T_true                     # overconfident: logits too large
    from scipy.optimize import minimize_scalar

    def probs(T):
        e = np.exp(z_model / T - (z_model / T).max(1, keepdims=True))
        return e / e.sum(1, keepdims=True)

    nll = lambda T: -np.log(probs(T)[np.arange(n), y]).mean()
    Tstar = minimize_scalar(nll, bounds=(0.5, 20), method='bounded').x

    def reliability(P):
        conf = P.max(1)
        corr = (P.argmax(1) == y).astype(float)
        edges = np.linspace(1 / 3, 1, 9)
        mids, accs, ws = [], [], []
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
            if m.sum() > 20:
                mids.append(conf[m].mean()); accs.append(corr[m].mean()); ws.append(m.mean())
        ece = sum(w * abs(a - c) for w, a, c in zip(ws, accs, mids))
        return np.array(mids), np.array(accs), ece

    fig, ax = figure(HALF)
    ax.plot([1 / 3, 1], [1 / 3, 1], color=Navy, lw=0.7, ls=':', label='perfect calibration')
    for P, c, lab in ((probs(1.0), IDAred, 'raw, $T = 1$'), (probs(Tstar), Forest, f'rescaled, $T^* = {Tstar:.1f}$')):
        m, a_, ece = reliability(P)
        ax.plot(m, a_, 'o-', color=c, ms=3, label=f'{lab}: ECE = {100 * ece:.1f}%')
    ax.set_xlabel('Confidence: largest probability of the text')
    ax.set_ylabel('Accuracy in the bin')
    ax.set_xlim(0.3, 1.02)
    ax.set_ylim(0.3, 1.02)
    ax.set_title('Simulated overconfident classifier', loc='left')
    h, l = ax.get_legend_handles_labels()
    legend_below(fig, h, l, 1)
    save_fig(fig, 'ch15_sem_primer_calibration')
    return dict(Tstar=Tstar)


def run_all():
    res = {}
    res['softmax'] = fig_softmax()
    res['metrics'] = fig_metrics()
    res['attenuation'] = fig_attenuation()
    res['mcnemar'] = fig_mcnemar()
    res['bootstrap'] = fig_bootstrap()
    res['auc'] = fig_auc()
    fig_timing()
    res['cluster'] = fig_cluster()
    res['cost'] = fig_cost()
    res['calibration'] = fig_calibration()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

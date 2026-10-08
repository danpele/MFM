"""
seminar3_explainers.py -- Explanatory (primer) charts for Seminar 3 (MFM): factor models and asset pricing
========================================================================================================
Teaching charts for the primer slides "Prerequisites for Today" / "Noțiuni necesare azi" of Seminar 3,
which takes place BEFORE Lecture 3. All charts use SIMULATED or textbook-example data only (fixed seeds):
they illustrate the concepts (market model, efficient frontier and tangency portfolio, security market
line, robust standard errors, block bootstrap, the GRS F distribution, multiple-testing thresholds,
Bayesian shrinkage of beta, principal components, stale prices and the Dimson beta, errors in variables
in the second pass) and contain no exercise answers.

Output: charts/ch3_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom),
drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_03/seminar3_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
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

FS = 7.5
plt.rcParams.update({'font.size': FS, 'axes.labelsize': FS, 'axes.titlesize': FS, 'xtick.labelsize': 7,
                     'ytick.labelsize': 7, 'legend.fontsize': 7, 'lines.linewidth': 1.0, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.size': 2.5,
                     'ytick.major.size': 2.5, 'legend.handlelength': 1.8, 'legend.columnspacing': 1.2,
                     'axes.facecolor': 'none', 'figure.facecolor': 'none', 'savefig.facecolor': 'none',
                     'text.color': 'black', 'axes.labelcolor': 'black', 'xtick.color': 'black',
                     'ytick.color': 'black', 'axes.edgecolor': Navy})

# boxes on the slide (inches): text width 5.69 in, text height 3.03 in
FULL = (5.6, 1.3)
HALF = (2.8, 1.75)


def save_fig(fig, name):
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    fig.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=220)
    plt.close(fig)
    print(f'   saved {name}')


def bottom_legend(fig, axes=None, ncol=3, handles=None, labels=None):
    if handles is None:
        handles, labels = [], []
        for ax in np.atleast_1d(axes).ravel():
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels and not l.startswith('_'):
                    handles.append(h); labels.append(l)
    fig.tight_layout()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


# =============================================================================
# (i) the market model: scatter, OLS line, alpha and a residual
# =============================================================================
def fig_market_model(T=120, alpha=0.4, beta=1.3, seed=2):
    rng = np.random.default_rng(seed)
    f = rng.normal(0.6, 4.5, T)
    y = alpha + beta * f + rng.normal(0, 3.0, T)
    b, a = np.polyfit(f, y, 1)
    r2 = np.corrcoef(f, y)[0, 1] ** 2
    fig, ax = plt.subplots(figsize=HALF)
    ax.scatter(f, y, s=6, color=MainBlue, alpha=0.8, lw=0, label='Months $(f_t, R^e_{i,t})$')
    xx = np.linspace(f.min() - 1, f.max() + 1, 2)
    ax.plot(xx, a + b * xx, color=IDAred, lw=1.4, label=rf'OLS: $\hat\alpha$ = {a:.2f}, $\hat\beta$ = {b:.2f}, $R^2$ = {r2:.2f}')
    ax.axhline(0, color=Navy, lw=0.5, ls=':'); ax.axvline(0, color=Navy, lw=0.5, ls=':')
    ax.plot(0, a, 'o', color=Forest, ms=4, label=r'$\hat\alpha$: the line at $f_t = 0$')
    i = int(np.argmax(y - (a + b * f)))
    ax.plot([f[i], f[i]], [a + b * f[i], y[i]], color=Amber, lw=1.4, label=r'one residual $\hat\varepsilon_t$')
    ax.set_xlabel(r'Market excess return $f_t$ (%)')
    ax.set_ylabel(r'$R^e_{i,t}$ (%)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_market_model')
    return dict(a=a, b=b, r2=r2)


# =============================================================================
# (ii) mean-variance frontier, CML and the tangency portfolio
# =============================================================================
def fig_frontier():
    mu = np.array([4.0, 6.0, 8.0, 10.0]) / 100        # expected excess returns
    sd = np.array([12.0, 16.0, 22.0, 30.0]) / 100
    C = np.array([[1, .3, .2, .1], [.3, 1, .4, .2], [.2, .4, 1, .3], [.1, .2, .3, 1]])
    S = np.outer(sd, sd) * C
    Si = np.linalg.inv(S)
    one = np.ones(4)
    # frontier of risky assets (excess returns; the risk-free asset has excess return 0)
    A, B, Cc = one @ Si @ one, one @ Si @ mu, mu @ Si @ mu
    m = np.linspace(0.02, 0.14, 200)
    var = (A * m ** 2 - 2 * B * m + Cc) / (A * Cc - B ** 2)
    wT = Si @ mu / (one @ Si @ mu)
    mT, sT = wT @ mu, np.sqrt(wT @ S @ wT)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(100 * np.sqrt(var), 100 * m, color=MainBlue, lw=1.5, label='Frontier of the risky assets')
    ss = np.linspace(0, 32, 2)
    ax.plot(ss, ss * mT / sT, color=IDAred, lw=1.3, label=rf'CML, slope $SR_T$ = {mT / sT:.2f}')
    ax.plot(100 * sd, 100 * mu, 's', color=Amber, ms=4, label=r'Single assets ($SR$ = $\mu_i/\sigma_i$)')
    ax.plot(100 * sT, 100 * mT, 'o', color=Forest, ms=5, label='Tangency portfolio')
    ax.set_xlim(0, 32); ax.set_ylim(0, 14)
    ax.set_xlabel(r'Volatility $\sigma$ (% per year)')
    ax.set_ylabel(r'$\mu$ (% per year)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_frontier')
    return dict(wT=wT.round(3).tolist(), SRT=mT / sT, SR=(mu / sd).round(3).tolist())


# =============================================================================
# (iii) the security market line and alpha
# =============================================================================
def fig_sml(mu_m=6.0):
    betas = np.array([0.5, 0.8, 1.0, 1.25, 1.5])
    alphas = np.array([1.5, -0.8, 0.0, 1.0, -1.8])
    mus = betas * mu_m + alphas
    fig, ax = plt.subplots(figsize=HALF)
    bb = np.linspace(0, 1.8, 2)
    ax.plot(bb, mu_m * bb, color=MainBlue, lw=1.5, label=rf'SML: $\mu_i = \beta_i\mu_m$, $\mu_m$ = {mu_m:.0f}%')
    for b, m, a in zip(betas, mus, alphas):
        ax.plot([b, b], [b * mu_m, m], color=IDAred if a < 0 else Forest, lw=1.2)
    ax.plot(betas, mus, 'o', color=Navy, ms=4, label='Assets: average excess return')
    ax.plot(1, mu_m, 'D', color=Amber, ms=5, label=r'Market: $\beta = 1$')
    ax.annotate(r'$\alpha > 0$', (betas[0], mus[0]), xytext=(4, 2), textcoords='offset points', color=Forest)
    ax.annotate(r'$\alpha < 0$', (betas[4], mus[4]), xytext=(4, -6), textcoords='offset points', color=IDAred)
    ax.set_xlim(0, 1.8); ax.set_ylim(0, 11)
    ax.set_xlabel(r'Beta $\beta_i$')
    ax.set_ylabel(r'$\mu_i$ (% per year)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_sml')


# =============================================================================
# (iv) classical, White and Newey--West standard errors in a simulation
# =============================================================================
def nw_se(X, u, L):
    T = len(u)
    XtXi = np.linalg.inv(X.T @ X)
    g = X * u[:, None]
    S = g.T @ g
    for j in range(1, L + 1):
        w = 1 - j / (L + 1)
        G = g[j:].T @ g[:-j]
        S += w * (G + G.T)
    return np.sqrt(np.diag(XtXi @ S @ XtXi))


def fig_hac(T=331, reps=2000, seed=6, L=5):
    rng = np.random.default_rng(seed)
    bh, se_c, se_w, se_n = [], [], [], []
    for _ in range(reps):
        # factor with volatility clustering, residuals larger when the factor moves a lot, and autocorrelated
        h = np.exp(np.convolve(rng.normal(0, 0.35, T + 12), np.ones(12) / np.sqrt(12), 'valid')[:T])
        f = rng.standard_normal(T) * h
        v = rng.standard_normal(T + 1)
        e = (v[1:] + 0.5 * v[:-1]) * (0.6 + 0.8 * np.abs(f))
        y = 1.0 * f + e
        X = np.c_[np.ones(T), f]
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        u = y - X @ b
        XtXi = np.linalg.inv(X.T @ X)
        bh.append(b[1])
        se_c.append(np.sqrt(u @ u / (T - 2) * XtXi[1, 1]))
        se_w.append(nw_se(X, u, 0)[1])
        se_n.append(nw_se(X, u, L)[1])
    vals = [np.std(bh), np.mean(se_c), np.mean(se_w), np.mean(se_n)]
    labs = ['True SD\n(simulated)', 'Classical', 'White', f'NW, $L$ = {L}']
    fig, ax = plt.subplots(figsize=HALF)
    cols = [Navy, IDAred, Amber, Forest]
    ax.bar(range(4), vals, color=cols, width=0.6)
    for k, v in enumerate(vals):
        ax.text(k, v * 1.02, f'{v:.3f}', ha='center', va='bottom', fontsize=FS)
    ax.set_xticks(range(4)); ax.set_xticklabels(labs)
    ax.set_ylabel(r'SE of $\hat\beta$')
    ax.set_ylim(0, max(vals) * 1.22)
    fig.tight_layout()
    save_fig(fig, 'ch3_sem_primer_hac')
    return dict(sd=vals[0], classical=vals[1], white=vals[2], nw=vals[3])


# =============================================================================
# (v) the moving-block bootstrap
# =============================================================================
def fig_block(T=24, b=4, seed=12):
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, T - b + 1, T // b)
    cmap = [MainBlue, IDAred, Forest, Amber]
    fig, ax = plt.subplots(figsize=(5.6, 1.15))
    for t in range(T):
        ax.add_patch(Rectangle((t, 1.3), 0.92, 0.8, facecolor=BandBlue, edgecolor=MainBlue, lw=0.5))
        ax.text(t + 0.46, 1.7, str(t + 1), ha='center', va='center', fontsize=7)
    for k, s in enumerate(starts):
        c = cmap[k % len(cmap)]
        ax.add_patch(Rectangle((s - 0.04, 1.26), b, 0.88, fill=False, edgecolor=c, lw=1.3))
        for j in range(b):
            x = k * b + j
            ax.add_patch(Rectangle((x, 0), 0.92, 0.8, facecolor='none', edgecolor=c, lw=1.0))
            ax.text(x + 0.46, 0.4, str(s + j + 1), ha='center', va='center', fontsize=7, color=c)
    ax.text(-0.4, 1.7, 'original', ha='right', va='center')
    ax.text(-0.4, 0.4, 'bootstrap', ha='right', va='center')
    ax.set_xlim(-4.5, T + 0.2); ax.set_ylim(-0.1, 2.2)
    ax.axis('off')
    fig.tight_layout()
    save_fig(fig, 'ch3_sem_primer_block')
    return dict(starts=(starts + 1).tolist())


# =============================================================================
# (vi) the GRS statistic and its F distribution (primer example)
# =============================================================================
def fig_grs(T=121, N=2, W=2.84):
    d1, d2 = N, T - N - 1
    x = np.linspace(0, 8, 500)
    c = stats.f.ppf(0.95, d1, d2)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, stats.f.pdf(x, d1, d2), color=MainBlue, lw=1.5, label=rf'$F({d1}, {d2})$ density under $H_0$')
    m = x >= c
    ax.fill_between(x[m], 0, stats.f.pdf(x[m], d1, d2), color=IDAred, alpha=0.5, lw=0,
                    label=rf'rejection region, 5%: $W > {c:.2f}$')
    ax.axvline(W, color=Forest, lw=1.4, ls='--', label=rf'example $W$ = {W}, $p$ = {stats.f.sf(W, d1, d2):.3f}')
    ax.set_xlim(0, 8); ax.set_ylim(0, 1.05)
    ax.set_xlabel('$W$')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_grs')
    return dict(crit=c, p=stats.f.sf(W, d1, d2))


# =============================================================================
# (vii) Bonferroni, Holm and Benjamini--Hochberg on 50 simulated tests
# =============================================================================
def fig_pvalues(M=50, M1=12, seed=26, alpha=0.05):
    rng = np.random.default_rng(seed)
    z = np.r_[rng.normal(3.0, 1.0, M1), rng.standard_normal(M - M1)]
    p = 2 * stats.norm.sf(np.abs(z))
    true = np.r_[np.ones(M1, bool), np.zeros(M - M1, bool)]
    o = np.argsort(p); ps = p[o]; tr = true[o]
    j = np.arange(1, M + 1)
    bonf, holm, bh = np.full(M, alpha / M), alpha / (M - j + 1), alpha * j / M
    n_bonf = int(np.sum(ps <= alpha / M))
    n_holm = int(np.argmax(ps > holm)) if np.any(ps > holm) else M
    kbh = np.where(ps <= bh)[0]
    n_bh = int(kbh.max() + 1) if len(kbh) else 0
    fig, ax = plt.subplots(figsize=(5.6, 1.2))
    ax.plot(j[tr], ps[tr], 'o', color=Forest, ms=3, label='true effect')
    ax.plot(j[~tr], ps[~tr], 'o', color=Navy, ms=3, mfc='none', label='null true')
    ax.plot(j, bonf, color=Amber, lw=1.3, ls='--', label=rf'Bonferroni $\alpha/M$: {n_bonf} rejections')
    ax.step(j, holm, where='mid', color=IDAred, lw=1.2, label=rf'Holm $\alpha/(M - j + 1)$: {n_holm}')
    ax.plot(j, bh, color=MainBlue, lw=1.3, label=rf'Benjamini–Hochberg $\alpha j/M$: {n_bh}')
    ax.axhline(alpha, color=Forest, lw=1.0, ls=':', label=rf'naive $p < \alpha$: {int(np.sum(ps < alpha))}')
    ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5); ax.set_xlim(0, M + 1)
    ax.set_xlabel('Rank $j$ of the sorted p-value')
    ax.set_ylabel('$p_{(j)}$ (log)')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch3_sem_primer_pvalues')
    false_bh = int(np.sum(~tr[:n_bh]))
    return dict(bonf=n_bonf, holm=n_holm, bh=n_bh, false_bh=false_bh)


# =============================================================================
# (viii) Bayesian shrinkage of a noisy beta
# =============================================================================
def fig_shrinkage(bbar=1.0, sb=0.30, bhat=1.6, se=0.35):
    w = sb ** 2 / (sb ** 2 + se ** 2)
    pm = w * bhat + (1 - w) * bbar
    ps = np.sqrt(1 / (1 / sb ** 2 + 1 / se ** 2))
    x = np.linspace(-0.2, 2.8, 500)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(x, stats.norm.pdf(x, bbar, sb), color=Amber, lw=1.4, label=rf'prior $N(\bar\beta, \sigma_\beta^2)$, $\bar\beta$ = {bbar}')
    ax.plot(x, stats.norm.pdf(x, bhat, se), color=MainBlue, lw=1.4, ls='--', label=rf'likelihood, $\hat\beta$ = {bhat}, se = {se}')
    ax.plot(x, stats.norm.pdf(x, pm, ps), color=IDAred, lw=1.6, label=rf'posterior, mean {pm:.2f}, weight $w$ = {w:.2f}')
    ax.set_xlabel(r'$\beta$')
    ax.set_ylabel('Density')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_shrinkage')
    return dict(w=w, pm=pm, ps=ps)


# =============================================================================
# (ix) PCA: scree plot and loadings of 11 simulated sector returns
# =============================================================================
def fig_pca(N=11, T=2000, seed=19):
    rng = np.random.default_rng(seed)
    m = rng.standard_normal(T)
    g = rng.standard_normal(T)
    lam_m = rng.uniform(0.7, 1.0, N)
    lam_g = np.linspace(0.45, -0.45, N)
    X = np.outer(m, lam_m) + np.outer(g, lam_g) + rng.standard_normal((T, N)) * 0.55
    Z = (X - X.mean(0)) / X.std(0)
    ev, V = np.linalg.eigh(Z.T @ Z / T)
    ev, V = ev[::-1], V[:, ::-1]
    V = V * np.sign(V.sum(0))
    noise = np.linalg.eigvalsh(np.corrcoef(rng.standard_normal((T, N)).T))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 1.1))
    k = np.arange(1, N + 1)
    axes[0].plot(k, ev, 'o-', color=MainBlue, ms=3, label='Eigenvalues $\\lambda_k$')
    axes[0].plot(k, noise, 's--', color=Amber, ms=2.5, label='Pure noise, same $N$, $T$')
    axes[0].axhline(1, color=IDAred, lw=1.0, ls=':', label='Kaiser: $\\lambda_k = 1$')
    axes[0].set_xticks(k)
    axes[0].set_xlabel('Component $k$')
    axes[0].set_ylabel('$\\lambda_k$')
    axes[0].set_title(f'Scree plot: PC1 explains {100 * ev[0] / N:.0f}%', loc='left')
    w = 0.38
    axes[1].bar(k - w / 2, V[:, 0], width=w, color=MainBlue, label='PC1 loadings')
    axes[1].bar(k + w / 2, V[:, 1], width=w, color=IDAred, label='PC2 loadings')
    axes[1].axhline(0, color=Navy, lw=0.5)
    axes[1].set_xticks(k)
    axes[1].set_xlabel('Asset')
    axes[1].set_ylabel('Loading')
    axes[1].set_title('PC2 opposes two groups', loc='left')
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    bottom_legend(fig, ncol=5, handles=h1 + h2, labels=l1 + l2)
    save_fig(fig, 'ch3_sem_primer_pca')
    return dict(ev=ev.round(2).tolist(), share=(ev / N).round(3).tolist())


# =============================================================================
# (x) stale prices and the Dimson beta
# =============================================================================
def fig_dimson(T=5000, beta=1.0, p_trade=0.75, seed=23):
    rng = np.random.default_rng(seed)
    rm = rng.normal(0, 1, T)
    true = beta * rm + rng.normal(0, 1, T)
    # the stock trades on a day with probability p_trade; when it does not trade, the price is stale
    trade = rng.uniform(size=T) < p_trade
    obs = np.zeros(T); acc = 0.0
    for t in range(T):
        acc += true[t]
        if trade[t]:
            obs[t] = acc; acc = 0.0
    y = obs[1:-1]
    X = np.c_[np.ones(T - 2), rm[:-2], rm[1:-1], rm[2:]]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    b_ols = np.polyfit(rm[1:-1], y, 1)[0]
    fig, ax = plt.subplots(figsize=HALF)
    labs = ['$t-1$', '$t$', '$t+1$', 'Dimson\nsum']
    vals = [b[1], b[2], b[3], b[1:].sum()]
    ax.bar(range(4), vals, color=[Amber, MainBlue, Amber, Forest], width=0.6)
    ax.axhline(beta, color=IDAred, lw=1.2, ls='--', label=rf'true $\beta$ = {beta}')
    for k, v in enumerate(vals):
        lab = f'{abs(v):.2f}' if abs(v) < 0.005 else f'{v:.2f}'
        if v > 0.3:
            ax.text(k, v / 2, lab, ha='center', va='center', fontsize=FS, color='white')
        else:
            ax.text(k, max(v, 0) + 0.02, lab, ha='center', va='bottom', fontsize=FS)
    ax.set_xticks(range(4)); ax.set_xticklabels(labs)
    ax.set_xlabel('Market return of day')
    ax.set_ylabel('Slope')
    ax.set_ylim(0, 1.25)
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_dimson')
    return dict(b_ols=b_ols, b=b[1:].round(3).tolist(), dimson=b[1:].sum())


# =============================================================================
# (xi) errors in variables: second-pass slope on estimated betas
# =============================================================================
def fig_eiv(N=200, T=60, lam=0.5, sig_e=6.0, sig_f=4.5, seed=29):
    rng = np.random.default_rng(seed)
    beta = rng.normal(1.0, 0.3, N)
    mean_r = lam * beta + rng.normal(0, 0.12, N)
    bhat = beta + rng.normal(0, sig_e / (np.sqrt(T) * sig_f), N)
    s_true = np.polyfit(beta, mean_r, 1)[0]
    s_hat = np.polyfit(bhat, mean_r, 1)[0]
    fig, ax = plt.subplots(figsize=HALF)
    ax.scatter(beta, mean_r, s=5, color=MainBlue, lw=0, alpha=0.7, label=rf'true $\beta_i$: slope {s_true:.2f}')
    ax.scatter(bhat, mean_r, s=5, color=IDAred, lw=0, alpha=0.6, label=rf'estimated $\hat\beta_i$: slope {s_hat:.2f}')
    xx = np.linspace(0, 2.2, 2)
    ax.plot(xx, np.polyval(np.polyfit(beta, mean_r, 1), xx), color=MainBlue, lw=1.3)
    ax.plot(xx, np.polyval(np.polyfit(bhat, mean_r, 1), xx), color=IDAred, lw=1.3, ls='--')
    ax.set_xlim(0, 2.2)
    ax.set_xlabel('Beta')
    ax.set_ylabel(r'Average return $\bar R_i$ (%)')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch3_sem_primer_eiv')
    return dict(true=s_true, est=s_hat, lam=lam)


def run_all():
    res = {}
    res['market_model'] = fig_market_model()
    res['frontier'] = fig_frontier()
    fig_sml()
    res['hac'] = fig_hac()
    res['block'] = fig_block()
    res['grs'] = fig_grs()
    res['pvalues'] = fig_pvalues()
    res['shrinkage'] = fig_shrinkage()
    res['pca'] = fig_pca()
    res['dimson'] = fig_dimson()
    res['eiv'] = fig_eiv()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

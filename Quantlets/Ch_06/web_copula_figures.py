"""
web_copula_figures.py -- explanatory charts of the copula section of the Chapter 6 web page (MFM)
==================================================================================================
Simulations and closed forms only (no market data); every number quoted in the web text comes from
ch6_web_copula.json written here.
  ch6_web_corr_traps   two variables that are functions of each other, yet Pearson correlation is near zero
  ch6_web_sklar        Sklar's theorem: the same copula with different margins; two copulas with the same margins
  ch6_web_taildep      P(V <= q | U <= q) as the threshold q becomes extreme, five copulas with Kendall tau = 0.5
  ch6_web_cdo          number of defaults in a pool of 100 loans: Gaussian against t copula, same correlation
  ch6_web_cml_steps    the four steps from returns to a fitted copula (diagram)
  kendall toy example  concordant and discordant pairs of five days (numbers only)
Run:  python3 Quantlets/Ch_06/web_copula_figures.py
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy import stats, integrate

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from dep_tools import FAMILIES, FAM_LABEL, simulate, theta_from_tau, tail_dep, kendall_tau   # noqa: E402

CHARTS = os.path.join(HERE, '..', '..', 'charts')
OUT_JSON = os.path.join(HERE, 'ch6_web_copula.json')
SEED = 42

plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'], 'font.size': 9,
                     'axes.labelsize': 10, 'axes.titlesize': 10.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.6, 'lines.linewidth': 1.3,
                     'legend.facecolor': 'none', 'legend.framealpha': 0, 'legend.fontsize': 8.5})
MainBlue, IDAred, Forest, Amber, Orange, Purple, Navy = ('#1A3A6E', '#CD0000', '#2E7D32', '#B5853F', '#E67E22',
                                                        '#8E44AD', '#1F2A44')
FCOL = {'gaussian': MainBlue, 't': IDAred, 'clayton': Forest, 'gumbel': Orange, 'frank': Purple}
TAU, NU = 0.5, 4.0


def save(name):
    plt.savefig(os.path.join(CHARTS, name + '.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHARTS, name + '.png'), bbox_inches='tight', transparent=True, dpi=170)
    plt.close()


def par_of(fam, tau=TAU):
    th = theta_from_tau(fam, tau)
    return (th, NU) if fam == 't' else (th,)


# ---------------------------------------------------------------- 1. traps of linear correlation
def fig_corr_traps(rng):
    n = 1000
    x = rng.standard_normal(n)
    y = x ** 2
    r_sq = float(np.corrcoef(x, y)[0, 1])
    z = rng.standard_normal(n)
    a, b = np.exp(z), np.exp(3 * z)
    s1, s2 = 1.0, 3.0
    rmax = (np.exp(s1 * s2) - 1) / np.sqrt((np.exp(s1 ** 2) - 1) * (np.exp(s2 ** 2) - 1))
    tau_ab = float(kendall_tau(a, b))
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.6))
    ax[0].scatter(x, y, s=5, color=MainBlue, alpha=0.5, lw=0)
    ax[0].set_xlabel('$X$ (standard Normal)')
    ax[0].set_ylabel('$Y = X^2$')
    ax[0].set_title(f'Y is a function of X, yet Pearson correlation is close to 0 ({r_sq:.2f})')
    ax[1].scatter(a, b, s=5, color=IDAred, alpha=0.5, lw=0)
    ax[1].set_xscale('log')
    ax[1].set_yscale('log')
    ax[1].set_xlabel('$X = e^{Z}$ (log scale)')
    ax[1].set_ylabel('$Y = e^{3Z}$ (log scale)')
    ax[1].set_title(f'Y rises whenever X rises: Kendall tau = {tau_ab:.0f},\nyet the largest possible Pearson '
                    f'correlation is {rmax:.3f}')
    plt.tight_layout()
    save('ch6_web_corr_traps')
    return {'pearson_x_x2': round(r_sq, 3), 'rho_max_lognormal': round(float(rmax), 3), 'tau_lognormal': tau_ab}


# ---------------------------------------------------------------- 2. Sklar: copula + margins
def fig_sklar(rng):
    n = 1500
    U = {f: simulate(f, par_of(f), n, rng) for f in ('gaussian', 't')}
    margins = [('Uniform margins: the copula itself', lambda u: u[:, 0], lambda u: u[:, 1], (0, 1)),
               ('Normal margins', lambda u: stats.norm.ppf(u[:, 0]), lambda u: stats.norm.ppf(u[:, 1]), (-4, 4)),
               ('Student t(3) and lognormal margins', lambda u: stats.t.ppf(u[:, 0], 3),
                lambda u: stats.lognorm.ppf(u[:, 1], 0.8), None)]
    fig, ax = plt.subplots(2, 3, figsize=(10.2, 6.6))
    joint = {}
    for i, f in enumerate(('gaussian', 't')):
        for j, (ttl, fx, fy, lim) in enumerate(margins):
            a = ax[i, j]
            x, y = fx(U[f]), fy(U[f])
            q = 0.05
            low = (U[f][:, 0] <= q) & (U[f][:, 1] <= q)
            a.scatter(x[~low], y[~low], s=4, color=FCOL[f], alpha=0.35, lw=0)
            a.scatter(x[low], y[low], s=9, color=Navy, lw=0, label='both in their worst 5%')
            if j == 2:
                a.set_xlim(-8, 8)
                a.set_yscale('log')
            elif lim:
                a.set_xlim(*lim)
                a.set_ylim(*lim)
            if i == 0:
                a.set_title(ttl)
            if j == 0:
                a.set_ylabel(f'{FAM_LABEL[f]} copula' + (f', nu = {NU:.0f}' if f == 't' else '') + '\n\nsecond asset')
            if i == 1:
                a.set_xlabel('first asset')
        joint[f] = int(((U[f][:, 0] <= 0.05) & (U[f][:, 1] <= 0.05)).sum())
    h, l = ax[1, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=1, frameon=False, bbox_to_anchor=(0.5, -0.02))
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    save('ch6_web_sklar')
    return {'n': n, 'tau': TAU, 'nu': NU, 'joint_worst5_count': joint}


# ---------------------------------------------------------------- 3. tail dependence as the threshold shrinks
def c_diag(fam, par, q):
    """C(q, q) in closed form (Archimedean) or by one-dimensional integration (Gaussian, t)."""
    if fam == 'clayton':
        th = par[0]
        return (2 * q ** (-th) - 1) ** (-1 / th)
    if fam == 'gumbel':
        th = par[0]
        return np.exp(-(2 * (-np.log(q)) ** th) ** (1 / th))
    if fam == 'frank':
        th = par[0]
        return -np.log1p(np.expm1(-th * q) ** 2 / np.expm1(-th)) / th
    rho = par[0]
    if fam == 'gaussian':
        x = stats.norm.ppf(q)
        f = lambda z: stats.norm.pdf(z) * stats.norm.cdf((x - rho * z) / np.sqrt(1 - rho ** 2))
        return integrate.quad(f, -np.inf, x, epsabs=1e-14, epsrel=1e-10, limit=200)[0]
    nu = par[1]
    x = stats.t.ppf(q, nu)

    def f(z):
        sc = np.sqrt((nu + z ** 2) * (1 - rho ** 2) / (nu + 1))
        return stats.t.pdf(z, nu) * stats.t.cdf((x - rho * z) / sc, nu + 1)
    return integrate.quad(f, -np.inf, x, epsabs=1e-14, epsrel=1e-10, limit=200)[0]


def fig_taildep():
    qs = np.geomspace(1e-4, 0.25, 120)
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    out = {}
    for f in FAMILIES:
        p = par_of(f)
        cond = np.array([c_diag(f, p, q) / q for q in qs])
        lam = tail_dep(f, p)[0]
        ax.plot(qs, cond, color=FCOL[f], label=FAM_LABEL[f] + (f' (nu = {NU:.0f})' if f == 't' else ''))
        if lam > 0:
            ax.axhline(lam, color=FCOL[f], ls=':', lw=1)
        out[f] = {'lambda_L': round(float(lam), 3),
                  **{f'q{q}': round(float(c_diag(f, p, q) / q), 3) for q in (0.1, 0.05, 0.01, 0.001)}}
    ax.plot(qs, qs, color=Navy, ls='--', lw=1, label='independence ($P = q$)')
    ax.set_xscale('log')
    ax.invert_xaxis()
    ax.set_ylim(0, 1)
    ax.set_xlabel('threshold $q$ (share of worst days), log scale: more extreme to the right')
    ax.set_ylabel('$P(V \\leq q \\mid U \\leq q)$')
    ax.set_title(f'If asset 1 has one of its worst days, how likely is asset 2 to have one too? (Kendall tau = {TAU})')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
    plt.tight_layout()
    save('ch6_web_taildep')
    return out


# ---------------------------------------------------------------- 4. pool of loans: Gaussian vs t copula
def fig_cdo(rng):
    n_loans, pd_, rho, nu, sims = 100, 0.02, 0.3, 4.0, 400_000
    M = rng.standard_normal(sims)
    eps = rng.standard_normal((sims, n_loans))
    Z = np.sqrt(rho) * M[:, None] + np.sqrt(1 - rho) * eps
    D_g = (Z < stats.norm.ppf(pd_)).sum(1)
    W = np.sqrt(nu / rng.chisquare(nu, sims))
    D_t = (Z * W[:, None] < stats.t.ppf(pd_, nu)).sum(1)
    k = np.arange(0, n_loans + 1)
    pg = np.bincount(D_g, minlength=n_loans + 1) / sims
    pt = np.bincount(D_t, minlength=n_loans + 1) / sims
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.7))
    ax[0].bar(k - 0.2, pg, width=0.4, color=MainBlue, label='Gaussian copula')
    ax[0].bar(k + 0.2, pt, width=0.4, color=IDAred, label=f't copula, nu = {nu:.0f}')
    ax[0].set_xlim(-1, 21)
    ax[0].set_xlabel('number of defaults out of 100 loans')
    ax[0].set_ylabel('probability')
    ax[0].set_title('Same average (2 defaults), different shape')
    ax[0].set_xticks(range(0, 21, 2))
    sg = np.array([(D_g >= j).mean() for j in k])
    st = np.array([(D_t >= j).mean() for j in k])
    ax[1].semilogy(k, sg, color=MainBlue, label='Gaussian copula')
    ax[1].semilogy(k, st, color=IDAred, label=f't copula, nu = {nu:.0f}')
    ax[1].set_xlim(0, 60)
    ax[1].set_ylim(1e-5, 1.2)
    ax[1].set_xlabel('at least this many defaults')
    ax[1].set_ylabel('probability (log scale)')
    ax[1].set_title('The bad tail: very different')
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.03))
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    save('ch6_web_cdo')
    out = {'p_zero': {'gaussian': round(float(pg[0]), 2), 't': round(float(pt[0]), 2)}, 'n_loans': n_loans, 'pd': pd_, 'rho': rho, 'nu': nu, 'sims': sims,
           'mean_defaults': {'gaussian': round(float(D_g.mean()), 2), 't': round(float(D_t.mean()), 2)}}
    for j in (10, 20, 30):
        out[f'p_ge_{j}'] = {'gaussian': float(f'{(D_g >= j).mean():.2g}'), 't': float(f'{(D_t >= j).mean():.2g}')}
    return out


# ---------------------------------------------------------------- 5. steps from returns to a copula
def fig_cml_steps():
    steps = [('1. Returns', 'daily returns of\nJPM and BAC'),
             ('2. GARCH filter', 'divide by today\'s\nvolatility: standardised\nresiduals'),
             ('3. Ranks', 'rank / (T + 1):\nwhere is today in its\nown history? (in [0, 1])'),
             ('4. Copula', 'fit Gaussian, t, Clayton,\nGumbel, Frank on the\nranks; compare by AIC')]
    fig, ax = plt.subplots(figsize=(10, 1.9))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1)
    ax.axis('off')
    for i, (h, b) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.06), 0.8, 0.88, boxstyle='round,pad=0.02', fc='none',
                                    ec=MainBlue, lw=1.2))
        ax.text(i + 0.46, 0.8, h, ha='center', va='center', fontsize=10, fontweight='bold', color=MainBlue)
        ax.text(i + 0.46, 0.4, b, ha='center', va='center', fontsize=8.5, color=Navy)
        if i < 3:
            ax.annotate('', xy=(i + 1.05, 0.5), xytext=(i + 0.88, 0.5),
                        arrowprops=dict(arrowstyle='->', color=IDAred, lw=1.4))
    save('ch6_web_cml_steps')


# ---------------------------------------------------------------- 6. Kendall's tau by hand
def kendall_toy():
    a = np.array([-2.0, 1.0, 3.0, -1.0, 0.5])      # five days, returns in %, illustrative
    b = np.array([-3.0, 2.0, 1.0, -0.5, -1.0])
    conc = disc = 0
    pairs = []
    for i in range(5):
        for j in range(i + 1, 5):
            s = np.sign((a[i] - a[j]) * (b[i] - b[j]))
            conc += s > 0
            disc += s < 0
            pairs.append((i + 1, j + 1, 'C' if s > 0 else 'D'))
    return {'a': a.tolist(), 'b': b.tolist(), 'concordant': int(conc), 'discordant': int(disc),
            'tau': (conc - disc) / 10, 'tau_scipy': float(stats.kendalltau(a, b)[0]),
            'discordant_pairs': [p[:2] for p in pairs if p[2] == 'D']}


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    res = {'corr_traps': fig_corr_traps(rng), 'sklar': fig_sklar(rng), 'taildep': fig_taildep(),
           'cdo': fig_cdo(rng), 'kendall_toy': kendall_toy()}
    fig_cml_steps()
    with open(OUT_JSON, 'w') as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

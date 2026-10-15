"""
seminar2_concepts.py -- Concept charts for the definitions added to the Seminar 2 primer (MFM)
===========================================================================================
Four teaching charts that put a picture next to definitions that were text only:
  ch2_sem_concept_garch   GARCH(1,1): clustering and the variance path after one large shock (1 -> 1.64 -> 1)
  ch2_sem_concept_chi2    the chi-squared(4) reference distribution of the Wald test and its 5% threshold 9.49
  ch2_sem_concept_blocks  the moving-block bootstrap: blocks of l = 5 consecutive days drawn and glued together
  ch2_sem_concept_kp      the Kolari-Pynnonen correction factor against the average residual correlation

Simulated or closed-form values only (fixed seeds); no exercise answers. Same style as seminar2_explainers.py
(course palette, transparent background, legend outside at the bottom, chart text in English).

Run:  python3 Quantlets/Ch_02/seminar2_concepts.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seminar2_explainers import (MainBlue, IDAred, Forest, Amber, Navy, BandBlue,   # noqa: E402
                                 save_fig, bottom_legend)

plt.rcParams.update({'font.size':11,'axes.labelsize':11,'axes.titlesize':11,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10})

W = 5.6     # full text width of a slide, inches


def garch():
    """Left: simulated GARCH(1,1) returns with clusters; right: expected variance after a shock of 3."""
    om, a, b = 0.02, 0.08, 0.90
    rng = np.random.default_rng(7)
    T = 1000
    z = rng.standard_normal(T)
    s2, e = np.empty(T), np.empty(T)
    s2[0] = om / (1 - a - b)
    e[0] = np.sqrt(s2[0]) * z[0]
    for t in range(1, T):
        s2[t] = om + a * e[t - 1] ** 2 + b * s2[t - 1]
        e[t] = np.sqrt(s2[t]) * z[t]
    fig, ax = plt.subplots(1, 2, figsize=(W, 1.55))
    ax[0].plot(e, color=MainBlue, lw=0.5, label='GARCH shock $\\varepsilon_t$')
    ax[0].plot(2 * np.sqrt(s2), color=IDAred, lw=0.8, label='$\\pm 2\\sigma_t$')
    ax[0].plot(-2 * np.sqrt(s2), color=IDAred, lw=0.8, label='_')
    ax[0].set_xlabel('Day $t$')
    ax[0].set_ylabel('Shock')
    h = np.arange(0, 121)
    path = np.where(h == 0, 1.0, 1 + 0.64 * (a + b) ** np.clip(h - 1, 0, None))
    ax[1].plot(h, path, color=MainBlue, lw=1.2, marker='o', markevery=[1], ms=4,
               label='$\\sigma^2_{t+h}$ after shock 3')
    ax[1].axhline(1, color=Forest, lw=0.9, ls='--', label='Long-run variance = 1')
    ax[1].annotate('1.64', (1, 1.64), xytext=(12, 1.6), color='black', fontsize=11,
                   arrowprops=dict(arrowstyle='-', color=Navy, lw=0.5))
    ax[1].set_xlabel('Days after the shock $h$')
    ax[1].set_ylabel('Variance')
    ax[1].set_ylim(0.9, 1.75)
    for x in ax:
        x.spines[['top', 'right']].set_visible(False)
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch2_sem_concept_garch')


def chi2():
    """The chi-squared(4) density, the 5% rejection region beyond 9.49."""
    x = np.linspace(0, 16, 400)
    f = stats.chi2.pdf(x, 4)
    c = stats.chi2.ppf(0.95, 4)
    fig, ax = plt.subplots(figsize=(W, 1.45))
    ax.plot(x, f, color=MainBlue, lw=1.2, label='$\\chi^2_4$ density')
    ax.fill_between(x[x >= c], f[x >= c], color=IDAred, alpha=0.35, lw=0,
                    label=f'$W > {c:.2f}$: reject at 5%')
    ax.axvline(c, color=IDAred, lw=0.9, ls='--')
    ax.axvline(4, color=Forest, lw=0.9, ls=':', label='Mean = 4')
    ax.set_xlabel('Value of the Wald statistic $W$')
    ax.set_ylabel('Density')
    ax.set_ylim(0, None)
    ax.spines[['top', 'right']].set_visible(False)
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch2_sem_concept_chi2')


def blocks():
    """Top: 40 simulated days cut into blocks of 5; bottom: one bootstrap series glued from drawn blocks."""
    rng = np.random.default_rng(11)
    T, l = 40, 5
    r = np.round(rng.standard_normal(T), 2)
    starts = rng.integers(0, T - l + 1, size=T // l)
    rb = np.concatenate([r[s:s + l] for s in starts])
    fig, ax = plt.subplots(2, 1, figsize=(W, 2.1), sharex=True)
    ax[0].bar(np.arange(1, T + 1), r, color=MainBlue, width=0.8, label='Original series')
    ax[1].bar(np.arange(1, T + 1), rb, color=Amber, width=0.8, label='One bootstrap series')
    for k, s in enumerate(starts):
        lo = k * l + 0.5
        ax[1].axvline(lo, color=Navy, lw=0.5)
        ax[1].text(lo + l / 2, 2.7 if k % 2 == 0 else -3.1, f'{s + 1}–{s + l}', ha='center', fontsize=10, color='black')
        if k < 2:
            ax[0].axvspan(s + 0.5, s + l + 0.5, color=BandBlue, alpha=0.6, lw=0, zorder=0)
    ax[0].set_ylabel('Return')
    ax[1].set_ylabel('Return')
    ax[1].set_xlabel('Position in the series (day)')
    for x in ax:
        x.set_ylim(-3.8, 3.8)
        x.spines[['top', 'right']].set_visible(False)
    ax[0].fill_between([], [], color=BandBlue, alpha=0.6, label='Two of the drawn blocks')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch2_sem_concept_blocks')


def kp():
    """Kolari-Pynnonen factor sqrt((1 - rho)/(1 + (N - 1) rho)) against the average residual correlation."""
    rho = np.linspace(0, 0.5, 200)
    fig, ax = plt.subplots(figsize=(W, 1.5))
    for N, col in [(2, MainBlue), (10, IDAred), (50, Forest)]:
        ax.plot(rho, np.sqrt((1 - rho) / (1 + (N - 1) * rho)), color=col, lw=1.2, label=f'$N = {N}$ firms')
    r0 = 0.153
    f0 = np.sqrt((1 - r0) / (1 + r0))
    ax.plot([r0], [f0], 'o', color=MainBlue, ms=5, markeredgecolor='white', markeredgewidth=1.0,
            label=f'B9: factor {f0:.3f}')
    ax.set_xlabel('Average correlation of the abnormal returns $\\bar\\varrho$')
    ax.set_ylabel('KP factor')
    ax.set_ylim(0, 1.05)
    ax.spines[['top', 'right']].set_visible(False)
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch2_sem_concept_kp')


if __name__ == '__main__':
    garch()
    chi2()
    blocks()
    kp()

"""
seminar0_explainers.py -- Explanatory charts for Seminar 0 (MFM): prices, returns, growth, risk and drawdowns
==========================================================================================================
Teaching charts for the definition slides of the core route of Seminar 0, which takes place BEFORE Lecture 0.
All charts use SIMULATED data only (fixed seeds): they illustrate the concepts (simple and log returns,
compounding, CAGR, the square-root-of-time rule, drawdown and recovery, a bad tick, the Sharpe ratio) and
contain no exercise answers.

Output: charts/ch0_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_00/seminar0_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
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
plt.rcParams.update({'font.size': 8.2, 'axes.labelsize': 8.2, 'axes.titlesize': 8.2, 'xtick.labelsize': 7.8,
                     'ytick.labelsize': 7.8, 'legend.fontsize': 7.8, 'axes.facecolor': 'none',
                     'figure.facecolor': 'none', 'savefig.facecolor': 'none', 'text.color': 'black',
                     'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black',
                     'axes.edgecolor': Navy, 'axes.linewidth': 0.6, 'xtick.major.width': 0.6,
                     'ytick.major.width': 0.6, 'lines.linewidth': 1.0, 'legend.handlelength': 1.6,
                     'legend.columnspacing': 1.2})

FULL = (5.6, 1.75)    # full slide width, chart above the bullets
HALF = (2.75, 2.15)   # one column of a two-column slide


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


# =============================================================================
# 1. Simple against log returns, and compounding
# =============================================================================
def fig_returns(n=10, step=0.20):
    R = np.linspace(-0.6, 0.6, 400)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(100 * R, 100 * R, color=Navy, lw=0.8, ls='--', label='Simple return $R$ (45-degree line)')
    ax.plot(100 * R, 100 * np.log1p(R), color=IDAred, lw=1.4, label=r'Log return $r = \ln(1 + R)$')
    for x in (-0.5, 0.5):
        ax.plot([100 * x, 100 * x], [100 * np.log1p(x), 100 * x], color=Amber, lw=1.2)
    ax.text(52, 25, f'{100 * (0.5 - np.log1p(0.5)):.1f} pp', color=Amber, fontsize=7.4, va='center')
    ax.text(-48, -75, f'{100 * (np.log1p(-0.5) + 0.5):.1f} pp', color=Amber, fontsize=7.4, va='center')
    ax.axhline(0, color=Navy, lw=0.4); ax.axvline(0, color=Navy, lw=0.4)
    ax.set_xlabel('Simple return $R$ (%)')
    ax.set_ylabel('Return (%)')
    ax.set_title('Close for small moves, apart for large ones', loc='left')
    ax = axes[1]
    Rs = np.array([step if i % 2 == 0 else -step for i in range(n)])
    P = 100 * np.concatenate([[1], np.cumprod(1 + Rs)])
    t = np.arange(n + 1)
    ax.plot(t, P, 'o-', color=MainBlue, ms=3, label=r'Price, alternating $+20\%$ and $-20\%$')
    ax.plot(t, 100 + 100 * np.concatenate([[0], np.cumsum(Rs)]), 's--', color=Amber, ms=2.5,
            label=r'$100\,(1 + \sum R_t)$: the sum of simple returns')
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Price')
    ax.set_title(rf'After {n} days: {P[-1]:.1f}, not 100', loc='left')
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch0_sem_primer_returns')
    return dict(final=P[-1], sum_log=float(np.sum(np.log1p(Rs))), gap50=0.5 - np.log1p(0.5))


# =============================================================================
# 2. CAGR: the constant growth rate through the first and the last price
# =============================================================================
def fig_cagr(seed=4, years=10, q=252, mu=0.08, sigma=0.20):
    rng = np.random.default_rng(seed)
    n = years * q
    t = np.arange(n + 1) / q
    x = np.concatenate([[0], np.cumsum((mu - sigma ** 2 / 2) / q + sigma / np.sqrt(q) * rng.standard_normal(n))])
    P = 100 * np.exp(x)
    cagr = (P[-1] / P[0]) ** (1 / years) - 1
    R = np.diff(P) / P[:-1]
    arith = q * R.mean()
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(t, P, color=MainBlue, lw=0.7, label='Simulated price $P_t$')
    ax.plot(t, 100 * (1 + cagr) ** t, color=IDAred, lw=1.3, label=f'Constant growth at CAGR = {100 * cagr:.1f}%')
    ax.plot(t, 100 * (1 + arith) ** t, color=Forest, lw=1.0, ls='--',
            label=f'Growth at the mean simple return, {100 * arith:.1f}% a year')
    ax.set_yscale('log')
    ax.set_ylim(80, 260)
    ax.set_yticks([100, 150, 200, 250])
    ax.set_yticklabels(['100', '150', '200', '250'])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel('Years')
    ax.set_ylabel('Price (log scale)')
    ax.set_title(r'CAGR $= (P_{\mathrm{end}}/P_{\mathrm{start}})^{1/Y} - 1$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch0_sem_primer_cagr')
    return dict(cagr=cagr, arith=arith, mult=P[-1] / P[0])


# =============================================================================
# 3. The square-root-of-time rule
# =============================================================================
def fig_sqrt_rule(seed=3, sd=0.01, n=252 * 400):
    rng = np.random.default_rng(seed)
    r = sd * rng.standard_normal(n)
    hs = np.array([1, 5, 10, 21, 42, 63, 126, 252])
    emp = [r[: n // h * h].reshape(-1, h).sum(1).std(ddof=1) for h in hs]
    hh = np.linspace(1, 252, 200)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(hh, 100 * sd * hh, color=IDAred, lw=1.0, ls='--', label=r'Wrong: $\sigma_d \times h$')
    ax.plot(hh, 100 * sd * np.sqrt(hh), color=MainBlue, lw=1.3, label=r'$\sigma_d\sqrt{h}$')
    ax.plot(hs, 100 * np.array(emp), 'o', color=Forest, ms=3.5, label='s.d. of simulated $h$-day sums')
    ax.set_ylim(0, 25)
    ax.set_xlabel('Horizon $h$ (days)')
    ax.set_ylabel('Standard deviation (%)')
    ax.set_title(r'i.i.d. daily returns, $\sigma_d = 1\%$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch0_sem_primer_sqrt_rule')
    return dict(emp252=emp[-1])


# =============================================================================
# 4. Drawdown, maximum drawdown and the longest period under water
# =============================================================================
def fig_drawdown(seed=13, years=4, q=252, mu=0.06, sigma=0.22):
    rng = np.random.default_rng(seed)
    n = years * q
    t = np.arange(n + 1) / q
    x = np.concatenate([[0.0], np.cumsum(mu / q + sigma / np.sqrt(q) * rng.standard_normal(n))])
    V = 100 * np.exp(x)
    M = np.maximum.accumulate(V)
    DD = V / M - 1
    i_min = int(np.argmin(DD)); i_peak = int(np.argmax(V[:i_min + 1]))
    under = DD < 0
    best, cur, start, bs = 0, 0, 0, 0
    for i, u in enumerate(under):
        if u:
            if cur == 0:
                start = i
            cur += 1
            if cur > best:
                best, bs = cur, start
        else:
            cur = 0
    fig, axes = plt.subplots(2, 1, figsize=(2.75, 2.0), sharex=True, gridspec_kw=dict(height_ratios=[1.4, 1]))
    ax = axes[0]
    ax.plot(t, V, color=MainBlue, lw=0.8, label='Price $P_t$')
    ax.plot(t, M, color=Amber, lw=1.1, ls='--', label='Running peak $M_t$')
    ax.plot(t[i_peak], V[i_peak], 'o', color=Forest, ms=3.5, label='Peak')
    ax.plot(t[i_min], V[i_min], 'o', color=IDAred, ms=3.5, label='Trough')
    ax.set_ylabel('$P_t$')
    ax = axes[1]
    ax.axvspan(t[bs], t[bs + best - 1], color=BandBlue, lw=0, label='Longest period under water')
    ax.fill_between(t, 100 * DD, 0, color=IDAred, alpha=0.35, lw=0)
    ax.plot(t, 100 * DD, color=IDAred, lw=0.8, label='Drawdown $DD_t$ (underwater)')
    ax.annotate(f'MDD {100 * DD[i_min]:.1f}%', (t[i_min], 100 * DD[i_min]), xytext=(8, 2),
                textcoords='offset points', fontsize=7.4, color=IDAred)
    ax.set_ylim(100 * DD.min() * 1.3, 3)
    ax.set_xlabel('Years')
    ax.set_ylabel('$DD_t$ (%)')
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch0_sem_primer_drawdown')
    return dict(mdd=DD[i_min], longest_days=best, longest_years=best / q)


# =============================================================================
# 5. The gain needed to recover a loss
# =============================================================================
def fig_recovery():
    L = np.linspace(0, 0.85, 300)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(100 * L, 100 * L, color=Navy, lw=0.8, ls='--', label='Same size as the loss')
    ax.plot(100 * L, 100 * L / (1 - L), color=IDAred, lw=1.4, label=r'Gain needed $L/(1 - L)$')
    for l, ha, dx in ((0.25, 'right', -3), (0.5, 'right', -3), (0.8, 'right', -3)):
        g = l / (1 - l)
        ax.plot(100 * l, 100 * g, 'o', color=IDAred, ms=3.5)
        ax.text(100 * l + dx, 100 * g + 30, f'{100 * l:.0f}% loss: +{100 * g:.0f}%', fontsize=7.4, ha=ha,
                color=IDAred)
    ax.set_ylim(0, 480)
    ax.set_xlabel('Loss from the peak $L$ (%)')
    ax.set_ylabel('Gain needed (%)')
    ax.set_title('Back to the peak', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch0_sem_primer_recovery')
    return {}


# =============================================================================
# 6. A bad tick in a simulated exchange-rate series
# =============================================================================
def fig_badtick(seed=5, n=60, level=4.97, sd=0.0013, bad_day=34, bad_val=5.37):
    rng = np.random.default_rng(seed)
    ref = level * np.exp(np.cumsum(sd * rng.standard_normal(n)))
    mkt = ref * np.exp(0.0006 * rng.standard_normal(n))
    mkt[bad_day] = bad_val
    days = np.arange(n)
    med = np.array([np.median(mkt[max(0, i - 5):i + 6]) for i in range(n)])
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.fill_between(days, med - 0.05, med + 0.05, color=BandBlue, lw=0, label='11-day rolling median $\\pm$ 0.05')
    ax.plot(days, mkt, 'o-', color=MainBlue, ms=1.8, lw=0.7, label='Market series')
    ax.plot(days, ref, color=Forest, lw=1.3, ls='--', label='Reference rate (official source)')
    ax.plot(bad_day, mkt[bad_day], 'o', color=IDAred, ms=4.5, label='Bad tick')
    ax.set_xlabel('Day')
    ax.set_ylabel('Lei per euro')
    ax.set_title('Far from the reference and from its neighbours', loc='left')
    ax = axes[1]
    lr = 100 * np.diff(np.log(mkt))
    cols = [IDAred if i in (bad_day - 1, bad_day) else MainBlue for i in range(n - 1)]
    ax.bar(days[1:], lr, color=cols, width=0.8)
    ax.axhline(0, color=Navy, lw=0.5)
    ax.set_xlabel('Day')
    ax.set_ylabel('Daily log change (%)')
    ax.set_title('A jump and its reversal', loc='left')
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch0_sem_primer_badtick')
    v_all = np.std(lr, ddof=1) * np.sqrt(252)
    clean = mkt.copy(); clean[bad_day] = med[bad_day]
    v_clean = np.std(100 * np.diff(np.log(clean)), ddof=1) * np.sqrt(252)
    return dict(jump=lr[bad_day - 1], rev=lr[bad_day], vol_raw=v_all, vol_clean=v_clean)


# =============================================================================
# 7. The Sharpe ratio as a slope
# =============================================================================
def fig_sharpe():
    assets = [('Asset A', 0.16, 0.08, MainBlue), ('Asset B', 0.30, 0.12, Forest), ('Asset C', 0.60, 0.42, IDAred)]
    fig, ax = plt.subplots(figsize=HALF)
    for name, v, m, c in assets:
        ax.plot([0, 0.7], [0, 0.7 * m / v], color=c, lw=0.8, ls='--')
        ax.plot(v, m, 'o', color=c, ms=5, label=f'{name}: SR = {m:.2f}/{v:.2f} = {m / v:.2f}')
    ax.set_xlim(0, 0.7); ax.set_ylim(0, 0.5)
    ax.set_xlabel(r'Annualised volatility $\sqrt{A}\,s_R$')
    ax.set_ylabel(r'Annualised mean $A\bar R$')
    ax.set_title('SR = slope of the line from the origin', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch0_sem_primer_sharpe')
    return {}


def run_all():
    res = {}
    res['returns'] = fig_returns()
    res['cagr'] = fig_cagr()
    res['sqrt'] = fig_sqrt_rule()
    res['drawdown'] = fig_drawdown()
    fig_recovery()
    res['badtick'] = fig_badtick()
    fig_sharpe()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

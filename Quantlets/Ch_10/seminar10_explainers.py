"""
seminar10_explainers.py -- Explanatory (primer) charts for Seminar 10 (MFM): market microstructure
=================================================================================================
Teaching charts for the primer slides "What You Need for Today" / "Noțiuni necesare azi" of Seminar 10,
which takes place BEFORE Lecture 10. All charts use SIMULATED data only (fixed seeds): they illustrate the
concepts (the limit order book and the spread, the delta method for the Roll estimator, the high-low and
close-range spread estimators, the Amihud ratio, HAC standard errors, a break in a regression slope) and
contain no exercise answers.

Output: charts/ch10_sem_primer_*.pdf and .png (transparent background, legend outside at the bottom).
The figures are drawn at the size of their box on the slide (1 pt in the figure = 1 pt on the slide).

Run:  python3 Quantlets/Ch_10/seminar10_explainers.py

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
# 1. A limit order book: best bid, best ask, mid-price, spread, tick
# =============================================================================
def fig_book(seed=1, tick=0.05, bid=19.95, n_lvl=4):
    rng = np.random.default_rng(seed)
    ask = bid + 2 * tick
    bids = bid - tick * np.arange(n_lvl)
    asks = ask + tick * np.arange(n_lvl)
    qb = np.round(rng.uniform(2, 9, n_lvl) * (1 + 0.25 * np.arange(n_lvl))) * 100
    qa = np.round(rng.uniform(2, 9, n_lvl) * (1 + 0.25 * np.arange(n_lvl))) * 100
    fig, ax = plt.subplots(figsize=HALF)
    ax.barh(bids, -qb, height=0.8 * tick, color=MainBlue, label='Buy limit orders (bids)')
    ax.barh(asks, qa, height=0.8 * tick, color=IDAred, label='Sell limit orders (asks)')
    mid = (bid + ask) / 2
    ax.axhline(mid, color=Forest, lw=1.0, ls='--', label=f'Mid-price $m = (a + b)/2 = {mid:.2f}$')
    ax.axvline(0, color=Navy, lw=0.6)
    ax.annotate('', xy=(2500, ask), xytext=(2500, bid), arrowprops=dict(arrowstyle='<->', color=Navy, lw=0.9))
    ax.text(2350, mid + 0.004, f'spread $a - b = {ask - bid:.2f}$', va='bottom', ha='right', fontsize=7.4, color=Navy)
    ax.text(qa[0] + 100, ask, f'best ask $a$', va='center', ha='left', fontsize=7.4, color=IDAred)
    ax.text(-qb[0] - 100, bid, f'best bid $b$', va='center', ha='right', fontsize=7.4, color=MainBlue)
    lv = np.concatenate([bids, asks])
    ax.set_yticks(lv)
    ax.set_yticklabels([f'{v:.2f}' for v in lv])
    ax.set_xlabel('Depth (shares)')
    ax.set_ylabel('Price (lei)')
    ax.set_xlim(-3200, 3200)
    ax.set_xticks([-3000, -1500, 0, 1500, 3000])
    ax.set_xticklabels(['3000', '1500', '0', '1500', '3000'])
    ax.set_title(f'Order book, tick = {tick:.2f} lei', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch10_sem_primer_book')
    return dict(bid=bid, ask=ask, mid=mid, spread_bp=1e4 * (ask - bid) / mid)


# =============================================================================
# 2. The delta method for s = 2 sqrt(-gamma_1)
# =============================================================================
def fig_delta(g1=-0.0016, se=0.0009):
    g = lambda x: 2 * np.sqrt(np.maximum(-x, 0))
    gp = lambda x: -1 / np.sqrt(-x)                      # derivative of 2 sqrt(-x)
    x = np.linspace(-0.0046, 0.0012, 600)
    fig, ax = plt.subplots(figsize=HALF)
    ax.plot(1e3 * x, g(x), color=MainBlue, lw=1.4, label=r'$g(\gamma_1) = 2\sqrt{-\gamma_1}$')
    tang = g(g1) + gp(g1) * (x - g1)
    ax.plot(1e3 * x, tang, color=IDAred, lw=1.0, ls='--', label=r"Tangent: $g(\gamma_1) + g'(\gamma_1)(\hat\gamma_1 - \gamma_1)$")
    # sampling density of gamma-hat drawn on the x axis
    d = stats.norm.pdf(x, g1, se)
    ax.fill_between(1e3 * x, 0, 0.022 * d / d.max(), color=BandBlue, lw=0, label=r'Sampling density of $\hat\gamma_1$')
    xp = x[x > 0]
    ax.fill_between(1e3 * xp, 0, 0.022 * stats.norm.pdf(xp, g1, se) / d.max(), color=IDAred, alpha=0.5, lw=0,
                    label=r'$\hat\gamma_1 > 0$: $\hat s$ undefined')
    ax.plot([1e3 * g1, 1e3 * g1], [0, g(g1)], color=Navy, lw=0.6, ls=':')
    ax.plot([1e3 * x[0], 1e3 * g1], [g(g1), g(g1)], color=Navy, lw=0.6, ls=':')
    for k in (-1, 1):
        xx = g1 + k * se
        ax.plot([1e3 * xx, 1e3 * xx], [0, tang[np.argmin(abs(x - xx))]], color=IDAred, lw=0.6, ls=':')
    ax.set_xlim(1e3 * x[0], 1e3 * x[-1])
    ax.set_ylim(0, 0.15)
    ax.set_xlabel(r'Autocovariance $\gamma_1$ ($\times 10^{-3}$)')
    ax.set_ylabel(r'Spread $s$')
    ax.set_title(r'$\mathrm{s.e.}(\hat s) \approx |g^{\prime}(\gamma_1)|\,\mathrm{s.e.}(\hat\gamma_1)$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch10_sem_primer_delta')
    return dict(s=g(g1), slope=gp(g1), se_s=abs(gp(g1)) * se, p_pos=stats.norm.sf(0, g1, se))


# =============================================================================
# 3. Corwin-Schultz: the high is a buy at the ask, the low a sell at the bid
# =============================================================================
def fig_cs(seed=5, n=390, sig_day=0.010, c=0.004):
    rng = np.random.default_rng(seed)
    t = np.arange(2 * n)
    m = np.concatenate([[0], np.cumsum(sig_day / np.sqrt(n) * rng.standard_normal(2 * n - 1))])
    q = rng.choice([-1, 1], 2 * n)
    p = m + c * q
    fig, ax = plt.subplots(figsize=(5.6, 1.9))
    ax.fill_between(t, 100 * (m - c), 100 * (m + c), color=BandBlue, lw=0, label='Quotes: bid $m_t - c$ to ask $m_t + c$')
    ax.plot(t, 100 * m, color=MainBlue, lw=0.8, label='Efficient log price $m_t$')
    ax.plot(t[::6], 100 * p[::6], '.', color=Navy, ms=1.5, label='Trades (every 6th shown)')
    for d, col in [(0, Forest), (1, Amber)]:
        sl = slice(d * n, (d + 1) * n)
        ih, il = d * n + np.argmax(p[sl]), d * n + np.argmin(p[sl])
        ax.plot(t[ih], 100 * p[ih], '^', color=col, ms=5)
        ax.plot(t[il], 100 * p[il], 'v', color=col, ms=5)
        x0 = d * n + n - 12
        ax.annotate('', xy=(x0, 100 * p[ih]), xytext=(x0, 100 * p[il]),
                    arrowprops=dict(arrowstyle='<->', color=col, lw=0.9))
        ax.text(x0, 100 * p[ih] + 0.08, f'day {d + 1}', ha='center', va='bottom', fontsize=7.4, color=col)
    ih, il = np.argmax(p), np.argmin(p)
    ax.annotate('', xy=(2 * n + 60, 100 * p[ih]), xytext=(2 * n + 60, 100 * p[il]),
                arrowprops=dict(arrowstyle='<->', color=IDAred, lw=1.0))
    ax.text(2 * n + 60, 100 * p[ih] + 0.08, 'two days', ha='center', va='bottom', fontsize=7.4, color=IDAred)
    ax.set_ylim(100 * p.min() - 0.15, 100 * p.max() + 0.45)
    ax.plot([], [], '^', color=Navy, ms=4, label='High (a buy at the ask)')
    ax.plot([], [], 'v', color=Navy, ms=4, label='Low (a sell at the bid)')
    ax.axvline(n - 0.5, color=Navy, lw=0.5, ls=':')
    ax.set_xlim(-5, 2 * n + 95)
    ax.set_xlabel('Minutes (two trading days)')
    ax.set_ylabel('Log price (%)')
    ax.set_title(r'Arrows: ranges $\ln(H/L)$ of day 1, day 2 and both days; each contains the spread once', loc='left')
    bottom_legend(fig, ax, ncol=3)
    save_fig(fig, 'ch10_sem_primer_cs')
    return {}


# =============================================================================
# 4. Abdi-Ranaldo: the close against the mid-range of today and tomorrow
# =============================================================================
def fig_ar(seed=3, days=8, n=390, sig_day=0.012, c=0.003):
    rng = np.random.default_rng(seed)
    fig, ax = plt.subplots(figsize=HALF)
    m0 = 0.0
    for d in range(days):
        m = m0 + np.concatenate([[0], np.cumsum(sig_day / np.sqrt(n) * rng.standard_normal(n - 1))])
        q = rng.choice([-1, 1], n)
        p = m + c * q
        H, L, C = p.max(), p.min(), p[-1]
        eta = (H + L) / 2
        ax.plot([d, d], [100 * L, 100 * H], color=MainBlue, lw=2.2, solid_capstyle='butt',
                label='Daily range $[\\ln L_t, \\ln H_t]$' if d == 0 else '_')
        ax.plot([d - 0.28, d + 0.28], [100 * eta, 100 * eta], color=Forest, lw=1.4,
                label=r'Mid-range $\eta_t$' if d == 0 else '_')
        ax.plot(d + 0.18, 100 * C, 'o', color=IDAred if q[-1] > 0 else Amber, ms=3.6,
                label='_')
        m0 = m[-1] + 0.004 * rng.standard_normal()
    ax.plot([], [], 'o', color=IDAred, ms=3.6, label='Close $c_t$ at the ask')
    ax.plot([], [], 'o', color=Amber, ms=3.6, label='Close $c_t$ at the bid')
    ax.set_xlabel('Day $t$')
    ax.set_ylabel('Log price (%)')
    ax.set_title(r'$\hat S^2 = 4\,\overline{(c_t - \eta_t)(c_t - \eta_{t+1})}$', loc='left')
    bottom_legend(fig, ax, ncol=2)
    save_fig(fig, 'ch10_sem_primer_ar')
    return {}


# =============================================================================
# 5. Amihud: absolute return against traded value for a liquid and an illiquid stock
# =============================================================================
def fig_amihud(seed=7, D=250):
    rng = np.random.default_rng(seed)
    fig, ax = plt.subplots(figsize=HALF)
    out = {}
    for name, med_dv, lam, col in [('Liquid', 50e6, 5.0, MainBlue), ('Illiquid', 0.5e6, 150.0, IDAred)]:
        dv = med_dv * np.exp(0.6 * rng.standard_normal(D))
        # |r| in bp grows with the traded value (price impact) plus noise
        r = lam * dv / 1e6 * np.exp(0.5 * rng.standard_normal(D)) ** 0.7 * 0.6 + 8 * np.abs(rng.standard_normal(D))
        illiq = np.mean(r / (dv / 1e6))
        out[name] = illiq
        ax.loglog(dv / 1e6, r, 'o', color=col, ms=1.8, alpha=0.8,
                  label=f'{name}: ILLIQ = {illiq:.1f} bp per USD 1m')
    xs = np.logspace(-1.3, 2.6, 50)
    for lv in (1, 10, 100):
        ax.loglog(xs, lv * xs, color=Navy, lw=0.5, ls=':', label='$|r|/$DVOL = 1, 10, 100 bp per USD 1m' if lv == 1 else '_')
    ax.set_xlim(0.05, 400)
    ax.set_ylim(0.5, 2000)
    ax.set_xlabel('Daily traded value DVOL (USD million)')
    ax.set_ylabel('$|r_d|$ (bp)')
    ax.set_title('One dot per day, 250 days per stock', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch10_sem_primer_amihud')
    return out


# =============================================================================
# 6. HAC standard errors: persistent residuals make OLS standard errors too small
# =============================================================================
def fig_hac(seed=4, n=1500, rho=0.75, R=600):
    rng = np.random.default_rng(seed)

    def ar1(n):
        e = rng.standard_normal(n)
        u = np.empty(n); u[0] = e[0] / np.sqrt(1 - rho ** 2)
        for i in range(1, n):
            u[i] = rho * u[i - 1] + e[i]
        return u * np.sqrt(1 - rho ** 2)

    # one sample: regressor x persistent too (as ln VIX), residual persistent
    x = ar1(n)
    u = ar1(n)
    fig, axes = plt.subplots(1, 2, figsize=FULL)
    ax = axes[0]
    ax.plot(np.arange(300), u[:300], color=IDAred, lw=0.7, label=r'Persistent residual, $\rho = 0.75$')
    ax.plot(np.arange(300), rng.standard_normal(300), color=MainBlue, lw=0.5, alpha=0.7, label='Independent residual')
    ax.set_xlabel('Day')
    ax.set_ylabel('$e_d$')
    ax.set_title('Residuals: persistent against independent', loc='left')
    # standard errors of the slope: OLS, HAC(L) and the true sampling s.d. (simulation)
    ax = axes[1]
    Ls = np.arange(0, 41, 2)

    def ses(x, u):
        X = np.column_stack([np.ones(n), x])
        y = 1 + 0.5 * x + u
        XtXi = np.linalg.inv(X.T @ X)
        b = XtXi @ X.T @ y
        e = y - X @ b
        s2 = e @ e / (n - 2)
        ols = np.sqrt(s2 * XtXi[1, 1])
        g = X * e[:, None]
        out = []
        for L in Ls:
            S = g.T @ g
            for l in range(1, L + 1):
                w = 1 - l / (L + 1)
                G = g[l:].T @ g[:-l]
                S += w * (G + G.T)
            V = XtXi @ S @ XtXi
            out.append(np.sqrt(V[1, 1]))
        return b[1], ols, np.array(out)

    b0, ols0, hac0 = ses(x, u)
    bs = [ses(ar1(n), ar1(n))[0] for _ in range(R)]
    true_sd = np.std(bs)
    ax.axhline(ols0, color=MainBlue, lw=1.1, ls='--', label='OLS s.e.')
    ax.plot(Ls, hac0, 'o-', color=IDAred, ms=2.6, lw=1.0, label='HAC (Newey--West) s.e. with $L$ lags')
    ax.axhline(true_sd, color=Forest, lw=1.1, label=f'True s.d. of $\\hat b$ ({R} simulated samples)')
    ax.set_xlabel('Number of lags $L$ in the HAC estimator')
    ax.set_ylabel(r's.e. of the slope $\hat b$')
    ax.set_ylim(0, 1.25 * max(hac0.max(), true_sd))
    ax.set_title(f'Slope standard errors, $n = {n}$', loc='left')
    bottom_legend(fig, axes, ncol=2)
    save_fig(fig, 'ch10_sem_primer_hac')
    return dict(ols=ols0, hac20=hac0[Ls == 20][0], true_sd=true_sd, ratio=true_sd / ols0)


# =============================================================================
# 7. A break in a slope: interaction with a dummy and the Wald test
# =============================================================================
def fig_break(seed=8, n=600):
    rng = np.random.default_rng(seed)
    x = 2.9 + 0.3 * rng.standard_normal(n)
    D = (np.arange(n) >= n // 2).astype(float)
    y = 0.2 + 1.0 * x - 0.1 * D - 0.4 * D * x + 0.25 * rng.standard_normal(n)
    fig, ax = plt.subplots(figsize=HALF)
    for dv, col, lab in [(0, MainBlue, 'Before the break, $D_d = 0$'), (1, IDAred, 'After the break, $D_d = 1$')]:
        sel = D == dv
        ax.plot(x[sel], y[sel], 'o', color=col, ms=1.6, alpha=0.6)
        bb = np.polyfit(x[sel], y[sel], 1)
        xs = np.linspace(x.min(), x.max(), 10)
        ax.plot(xs, np.polyval(bb, xs), color=col, lw=1.4, label=f'{lab}: slope {bb[0]:.2f}')
    ax.set_xlabel(r'$x_d$ (e.g. $\ln\mathrm{VIX}_d$)')
    ax.set_ylabel(r'$y_d$ (e.g. $\ln\mathrm{ILLIQ}_d$)')
    ax.set_title(r'$y = a + bx + gD + h\,Dx + e$: slope $b$, then $b + h$', loc='left')
    bottom_legend(fig, ax, ncol=1)
    save_fig(fig, 'ch10_sem_primer_break')
    return {}


def run_all():
    res = {}
    res['book'] = fig_book()
    res['delta'] = fig_delta()
    fig_cs()
    fig_ar()
    res['amihud'] = fig_amihud()
    res['hac'] = fig_hac()
    fig_break()
    return res


if __name__ == '__main__':
    import pprint
    pprint.pprint(run_all())

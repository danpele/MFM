"""
Generator pentru toate graficele si cifrele din Capitolul 18: risc sistemic si retele
===================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos; fara serii sau text gri.
Date zilnice de piata (data/market), 2010-2026: 6 banci americane, 5 banci europene, 2 banci romanesti (BVB),
S&P 500, Euro Stoxx 50, BET, VIX. Scenariile istorice pentru bancile internationale incep in 2007.
Conventie: randamente log zilnice in %; nivelul alpha = probabilitatea cozii (CoVaR 1%, MES 5%); pierderi pozitive.
Cifrele sunt salvate in ch18_results.json (folosite de generatoarele de slide-uri).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import (BANKS, US, EU, RO, ALL, NAMES, REGION_INDEX, joint_returns, bank_range_vol,  # noqa: E402
                      index_close, prices)
from systemic import (mes, mes_threshold, lrmes, srisk_ratio, breakeven_leverage, qreg, covar_static,  # noqa: E402
                      block_bootstrap_idx, covar_boot, covar_dynamic, var_fit, var_bic, gfevd, spillover_table,
                      rolling_total, lasso_qr_gacv)

# Stil standard MFM (identic cu SFM): transparent + ENG + legenda jos
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.1
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

# Culori brand
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Teal     = '#17A2B8'
Gray     = '#7F7F7F'   # doar linii de referinta, benzi, grila
REGION_COL = {'US': MainBlue, 'EU': IDAred, 'RO': Forest}
REGION_LAB = {'US': 'US banks', 'EU': 'European banks', 'RO': 'Romanian banks (BVB)'}
EVENTS = [('2011-08-08', 'Euro crisis'), ('2016-06-24', 'Brexit vote'), ('2018-12-19', 'RO bank tax'),
          ('2020-03-16', 'COVID-19'), ('2023-03-13', 'SVB'), ('2025-04-07', 'Tariffs')]

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
B_BOOT = 999
RESULTS = {}


def save_fig(name):
    """Salveaza figura ca PDF si PNG transparent."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Plaseaza legenda in afara graficului, jos-centru."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return [jsonable(v) for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, pd.Timestamp):
        return str(x.date())
    return x


def mark_events(ax, ymax=None):
    """Linii verticale de referinta pentru evenimente, cu eticheta neagra."""
    for d, lab in EVENTS:
        t = pd.Timestamp(d)
        if ax.get_xlim()[0] <= mdates.date2num(t) <= ax.get_xlim()[1]:
            ax.axvline(t, color=Gray, lw=0.5, ls=':')
            ax.text(t, ax.get_ylim()[1] if ymax is None else ymax, lab, rotation=90, fontsize=6.5, color='black',
                    ha='right', va='top')


# =============================================================================
# DATE: randamente log zilnice in % pentru banci si indici, zile comune (join pe preturi)
# =============================================================================
R = joint_returns(ALL + ['SPX', 'SX5E', 'BET', 'VIX'])
RB = R[ALL]


def system_ex(k, members):
    """Randamentul sistemului regional fara banca k (portofoliu cu ponderi egale)."""
    return R[[j for j in members if j != k]].mean(axis=1)


def region_of(k):
    return BANKS[k][2]


# =============================================================================
# 1. Indicii bancari regionali
# =============================================================================
def fig_bank_indices():
    """Portofoliile bancare cu ponderi egale (SUA, Europa, Romania), baza 100 la inceputul lui 2010."""
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    out = {}
    for reg, mem in [('US', US), ('EU', EU), ('RO', RO)]:
        s = 100 * (1 + (np.exp(R[mem] / 100) - 1).mean(axis=1)).cumprod()     # rebalansare zilnica
        ax.plot(s.index, s.values, color=REGION_COL[reg], lw=0.9, label=f'{REGION_LAB[reg]} (equal weights)')
        dd = s / s.cummax() - 1
        out[reg] = {'last': s.iloc[-1], 'maxdd': dd.min(), 'maxdd_date': dd.idxmin(),
                    'vol': R[mem].mean(axis=1).std() * np.sqrt(252), 'peak_date': s.idxmax()}
    ax.axhline(100, color=Gray, lw=0.5)
    ax.set_ylabel('Value of 100 invested\nin January 2010 (daily rebalancing)')
    ax.set_xlim(R.index[0], R.index[-1])
    mark_events(ax)
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    save_fig('ch18_bank_indices')
    return out


# =============================================================================
# 2. MES si SRISK
# =============================================================================
def mes_table():
    """MES 5% (fata de indicele regional), MES la pragul de -2% si LRMES, cu interval bootstrap pe blocuri."""
    rows = {}
    rng = np.random.default_rng(SEED)
    for k in ALL:
        m = R[REGION_INDEX[region_of(k)]].values
        x = R[k].values
        boot = []
        for _ in range(B_BOOT):
            idx = block_bootstrap_idx(len(x), 20, rng)
            boot.append(mes(x[idx], m[idx], 0.05))
        m2 = mes_threshold(x, m, -2.0)
        rows[k] = {'mes5': mes(x, m, 0.05), 'lo': np.percentile(boot, 2.5), 'hi': np.percentile(boot, 97.5),
                   'mes2': m2, 'n2': int((m < -2).sum()), 'lrmes': lrmes(m2), 'Lstar': breakeven_leverage(lrmes(m2)),
                   'Lstar55': breakeven_leverage(lrmes(m2), 0.055),
                   'beta': np.cov(x, m)[0, 1] / np.var(m, ddof=1), 'es5_m': -m[m <= np.quantile(m, 0.05)].mean(),
                   'var1': -np.quantile(x, 0.01)}
    return pd.DataFrame(rows).T


def fig_mes(t):
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    xs = np.arange(len(ALL))
    cols = [REGION_COL[region_of(k)] for k in ALL]
    ax.bar(xs, t['mes5'], color=cols, width=0.6)
    ax.errorbar(xs, t['mes5'], yerr=[t['mes5'] - t['lo'], t['hi'] - t['mes5']], fmt='none', ecolor='black',
                capsize=2, lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in ALL], rotation=35, ha='right', fontsize=7.5)
    ax.set_ylabel('MES 5% (daily loss, %)')
    h = [plt.Rectangle((0, 0), 1, 1, color=REGION_COL[r]) for r in ['US', 'EU', 'RO']]
    lab = ['US banks (market: S&P 500)', 'European banks (market: Euro Stoxx 50)', 'Romanian banks (market: BET)']
    h.append(plt.Line2D([], [], color='black', marker='|', ls='', ms=8))
    lab.append('95% block-bootstrap interval')
    ax.legend(h, lab, loc='upper center', bbox_to_anchor=(0.5, -0.42), ncol=2, frameon=False)
    save_fig('ch18_mes')


def fig_srisk(t):
    """SRISK / capitalul de piata in functie de levier, pentru bancile cu LRMES maxim, median si minim."""
    order = t['lrmes'].sort_values()
    pick = [order.index[-1], order.index[len(order) // 2], order.index[0]]
    L = np.linspace(2, 20, 200)
    fig, ax = plt.subplots(figsize=(6.6, 3.1))
    for k, c in zip(pick, [IDAred, Amber, MainBlue]):
        lr = t.loc[k, 'lrmes']
        ax.plot(L, 100 * srisk_ratio(lr, L), color=c, lw=1.3,
                label=f'{NAMES[k]}: LRMES {100 * lr:.0f}%, break-even leverage {t.loc[k, "Lstar"]:.1f}')
        ax.plot(t.loc[k, 'Lstar'], 0, 'o', color=c, ms=5)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Quasi-market leverage L = (debt + market equity) / market equity (assumed)')
    ax.set_ylabel('SRISK / market equity (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch18_srisk')
    return pick


# =============================================================================
# 3. CoVaR
# =============================================================================
def covar_table(alpha):
    """CoVaR si Delta-CoVaR pentru bancile americane si europene (sistemul = restul bancilor din regiune)."""
    rows = {}
    for i, k in enumerate(US + EU):
        mem = US if k in US else EU
        xs = system_ex(k, mem)
        c = covar_static(xs, R[k], alpha)
        lo, hi = covar_boot(xs, R[k], alpha, B=B_BOOT, block=20, seed=SEED + i)
        e = covar_static(R[k], xs, alpha)                      # expunerea: banca in conditiile unei crize a sistemului
        rows[k] = {**c, 'lo': lo, 'hi': hi, 'exp_covar': e['covar'], 'exp_dcovar': e['dcovar'], 'exp_b': e['b']}
    return pd.DataFrame(rows).T


def fig_covar_qr():
    """Regresia cuantila a sistemului pe JPMorgan: dreptele de 1% si 50%."""
    xs, xi = system_ex('JPM', US), R['JPM']
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.scatter(xi, xs, s=3, color=Teal, alpha=0.45, label='Daily returns, 2010-2026')
    grid = np.linspace(xi.min(), xi.max(), 50)
    out = {}
    for q, c, ls in [(0.01, IDAred, '-'), (0.5, MainBlue, '--')]:
        a, b = qreg(xs, xi, q)
        ax.plot(grid, a + b * grid, color=c, ls=ls, lw=1.3, label=f'{q:.0%} quantile regression: {a:.2f} + {b:.2f} x')
        out[q] = (a, b)
    qa = np.quantile(xi, 0.01)
    ax.axvline(qa, color=Gray, lw=0.6, ls=':')
    ax.text(qa, xs.max(), ' JPMorgan at its VaR 1%', fontsize=7, color='black', va='top')
    ax.set_xlabel('JPMorgan daily return (%)')
    ax.set_ylabel('Other US banks (equal weights, %)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch18_covar_qr')
    return out


def fig_dcovar(t):
    ks = list(t.index)
    xs = np.arange(len(ks))
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.bar(xs, t['dcovar'], color=[REGION_COL[region_of(k)] for k in ks], width=0.6)
    ax.errorbar(xs, t['dcovar'], yerr=[t['dcovar'] - t['lo'], t['hi'] - t['dcovar']], fmt='none', ecolor='black',
                capsize=2, lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in ks], rotation=35, ha='right', fontsize=7.5)
    ax.set_ylabel('ΔCoVaR 1% (system loss, %)')
    h = [plt.Rectangle((0, 0), 1, 1, color=REGION_COL[r]) for r in ['US', 'EU']] + \
        [plt.Line2D([], [], color='black', marker='|', ls='', ms=8)]
    ax.legend(h, ['US banks (system: other US banks)', 'European banks (system: other European banks)',
                  '95% block-bootstrap interval'], loc='upper center', bbox_to_anchor=(0.5, -0.42), ncol=2,
              frameon=False)
    save_fig('ch18_dcovar')


def fig_var_vs_dcovar(t):
    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    for reg in ['US', 'EU']:
        s = t[[region_of(k) == reg for k in t.index]]
        ax.scatter(s['var_i'], s['dcovar'], s=28, color=REGION_COL[reg], label=REGION_LAB[reg], zorder=3)
        for k in s.index:
            ax.annotate(NAMES[k], (s.loc[k, 'var_i'], s.loc[k, 'dcovar']), xytext=(4, 2), textcoords='offset points',
                        fontsize=6.5, color='black')
    ax.set_xlabel('VaR 1% of the bank (daily loss, %)')
    ax.set_ylabel('ΔCoVaR 1% (system loss, %)')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch18_var_vs_dcovar')
    from scipy.stats import spearmanr
    return spearmanr(t['var_i'], t['dcovar']).correlation


def dynamic_covar():
    """Delta-CoVaR 1% variabil in timp; stare: log VIX, randamentul indicelui regional si al sistemului (t-1)."""
    out, betas = {}, {}
    for k in ['JPM', 'C', 'GS', 'DBK', 'SAN', 'HSBA']:
        mem = US if k in US else EU
        xs = system_ex(k, mem)
        Mv = pd.concat([np.log(index_close('VIX')).reindex(R.index).ffill(), R[REGION_INDEX[region_of(k)]], xs],
                       axis=1).shift(1)
        d = pd.concat([xs.rename('sys'), R[k].rename('x'), Mv], axis=1).dropna()
        f, b = covar_dynamic(d['sys'], d['x'], d.iloc[:, 2:].values, 0.01)
        f.index = d.index
        out[k], betas[k] = f, b
    return out, betas


def fig_dcovar_dynamic(dyn):
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    cols = {'JPM': MainBlue, 'C': Teal, 'GS': Purple, 'DBK': IDAred, 'SAN': Orange, 'HSBA': Forest}
    for k, f in dyn.items():
        s = f['dcovar'].rolling(21).mean()
        ax.plot(s.index, s.values, color=cols[k], lw=0.8, label=NAMES[k])
    ax.set_ylabel('ΔCoVaR 1% (%, 21-day average)')
    ax.set_xlim(R.index[0], R.index[-1])
    ax.set_ylim(bottom=0)
    mark_events(ax)
    legend_outside_bottom(ax, ncol=6, y=-0.13)
    save_fig('ch18_dcovar_dynamic')


def fig_exposure(t):
    ks = list(t.index)
    xs = np.arange(len(ks))
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.bar(xs - 0.2, t['dcovar'], 0.38, color=MainBlue, label='ΔCoVaR 1%: loss of the system when the bank is in distress')
    ax.bar(xs + 0.2, t['exp_dcovar'], 0.38, color=Orange, label='Exposure ΔCoVaR 1%: loss of the bank when the system is in distress')
    ax.set_xticks(xs)
    ax.set_xticklabels([NAMES[k] for k in ks], rotation=35, ha='right', fontsize=7.5)
    ax.set_ylabel('Daily loss (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.42)
    save_fig('ch18_exposure')


# =============================================================================
# 4. Diebold-Yilmaz
# =============================================================================
V = np.log(bank_range_vol(ALL))


def spill_static(H=10):
    p = var_bic(V.values, 5)
    A, S = var_fit(V.values, p)
    st = spillover_table(gfevd(A, S, H), ALL)
    ret = R[ALL]
    pr = var_bic(ret.values, 5)
    Ar, Sr = var_fit(ret.values, pr)
    st_r = spillover_table(gfevd(Ar, Sr, H), ALL)
    return st, p, st_r, pr


def fig_spill_table(st):
    tab = st['table']
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    im = ax.imshow(tab.values, cmap='Blues', vmin=0, vmax=40)
    for i in range(len(ALL)):
        for j in range(len(ALL)):
            v = tab.values[i, j]
            ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=6.3, color='white' if v > 25 else 'black')
    ax.set_xticks(range(len(ALL)))
    ax.set_yticks(range(len(ALL)))
    ax.set_xticklabels([NAMES[k] for k in ALL], rotation=45, ha='right', fontsize=7)
    ax.set_yticklabels([NAMES[k] for k in ALL], fontsize=7)
    ax.set_xlabel('Shock from (column)')
    ax.set_ylabel('Forecast error variance of (row)')
    cb = fig.colorbar(im, ax=ax, orientation='horizontal', fraction=0.04, pad=0.28)
    cb.set_label('Share of the 10-day forecast error variance (%)', fontsize=8)
    save_fig('ch18_spill_table')


def fig_spill_network(st):
    """Reteaua conectivitatii nete pe perechi: sageata de la emitator la receptor, grosime ~ efectul net."""
    pn = st['pairwise_net']                     # pn[i, j] > 0: i transmite net catre j
    n = len(ALL)
    ang = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi, n, endpoint=False)
    pos = {k: (np.cos(a), np.sin(a)) for k, a in zip(ALL, ang)}
    thr = np.quantile(pn.values[pn.values > 0], 0.75)
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    for i in ALL:
        for j in ALL:
            v = pn.loc[i, j]
            if v > thr:
                (x0, y0), (x1, y1) = pos[i], pos[j]
                ax.annotate('', xy=(x1 * 0.9, y1 * 0.9), xytext=(x0 * 0.9, y0 * 0.9),
                            arrowprops=dict(arrowstyle='-|>', color=Purple, lw=0.4 + 0.9 * v, alpha=0.75,
                                            shrinkA=6, shrinkB=6))
    to = st['to']
    for k in ALL:
        x, y = pos[k]
        ax.scatter(x, y, s=60 + 6 * to[k], color=REGION_COL[region_of(k)], zorder=3)
        ax.text(1.2 * x, 1.14 * y, NAMES[k], ha='left' if x > 0.2 else ('right' if x < -0.2 else 'center'),
                va='center', fontsize=7, color='black')
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.35, 1.35)
    ax.axis('off')
    h = [plt.Line2D([], [], marker='o', ls='', color=REGION_COL[r], ms=7) for r in ['US', 'EU', 'RO']]
    h.append(plt.Line2D([], [], color=Purple, lw=1.2))
    ax.legend(h, [REGION_LAB[r] for r in ['US', 'EU', 'RO']] + ['Net pairwise spillover (top 25% of links)'],
              loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
    save_fig('ch18_spill_network')
    return thr


def spill_rolling():
    tot, net = rolling_total(V, window=250, step=5, p=2, H=10)
    return tot, net


def fig_spill_rolling(tot, net):
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=True, gridspec_kw={'height_ratios': [1.2, 1]})
    axes[0].plot(tot.index, tot.values, color=Purple, lw=1.0, label='Total connectedness index (250-day window)')
    axes[0].set_ylabel('Total index (%)')
    axes[0].set_xlim(tot.index[0], tot.index[-1])
    mark_events(axes[0])
    for reg in ['US', 'EU', 'RO']:
        mem = [k for k in ALL if region_of(k) == reg]
        s = net[mem].sum(axis=1)
        axes[1].plot(s.index, s.values, color=REGION_COL[reg], lw=0.9, label=f'Net spillover of {REGION_LAB[reg]}')
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_ylabel('Net (to - from, %)')
    fig.tight_layout()
    h = axes[0].get_lines()[:1] + axes[1].get_lines()[:3]
    fig.legend(h, [l.get_label() for l in h], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    save_fig('ch18_spill_rolling')


# =============================================================================
# 5. Financial Risk Meter
# =============================================================================
MACRO = ['SPX', 'SX5E', 'VIX']
LAMBDAS = np.logspace(-6, -1.5, 20)


def frm_design():
    """Randamente zilnice (fractii) ale bancilor si variabilele macro intarziate cu o zi."""
    Rf = R / 100
    Mac = Rf[MACRO].shift(1).add_suffix('_lag')
    return Rf[ALL].join(Mac).dropna()


def frm_window(D, k, tau=0.05):
    X = D[[j for j in ALL if j != k] + [c for c in D.columns if c.endswith('_lag')]]
    return lasso_qr_gacv(D[k].values, X.values, tau, LAMBDAS)


def frm_series(window=63, step=10, lam_fixed=2e-4):
    """FRM = media lambda (GACV) pe banci, pe ferestre mobile de 63 de zile; si densitatea legaturilor la lambda fix."""
    D = frm_design()
    rows = {}
    cache = os.path.join(HERE, 'ch18_frm.csv')
    if os.environ.get('MFM_FRM_CACHE') and os.path.exists(cache):
        return pd.read_csv(cache, index_col=0, parse_dates=True), LAMBDAS[int(np.argmin(np.abs(LAMBDAS - lam_fixed)))]
    j_fix = int(np.argmin(np.abs(LAMBDAS - lam_fixed)))
    for end in range(window, len(D) + 1, step):
        w = D.iloc[end - window:end]
        lam, dens = [], []
        for k in ALL:
            r = frm_window(w, k)
            lam.append(r['lambda'])
            dens.append(r['df'][j_fix] / (len(ALL) - 1 + len(MACRO)))
        rows[D.index[end - 1]] = {'frm': np.mean(lam), 'density': np.mean(dens)}
    f = pd.DataFrame(rows).T
    f.to_csv(os.path.join(HERE, 'ch18_frm.csv'))
    return f, LAMBDAS[j_fix]


def fig_frm_gacv():
    """Curba GACV pentru JPMorgan intr-o fereastra calma si intr-una de criza."""
    D = frm_design()
    out = {}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for ax, (end, lab, c) in zip(axes, [('2019-06-28', 'Calm window ending 28 Jun 2019', MainBlue),
                                        ('2020-03-31', 'COVID-19 window ending 31 Mar 2020', IDAred)]):
        w = D.loc[:end].iloc[-63:]
        r = frm_window(w, 'JPM')
        ax.plot(LAMBDAS, 1e3 * np.array(r['gacv']), 'o-', color=c, ms=3, lw=1, label=lab)
        ax.axvline(r['lambda'], color=Gray, lw=0.6, ls=':')
        ax.set_xscale('log')
        ax.set_xlabel('Penalty λ')
        ax.set_ylabel('GACV(λ) × 1000')
        ax2 = ax.twinx()
        ax2.step(LAMBDAS, r['df'], where='mid', color=Orange, lw=0.9, label='Active coefficients')
        ax2.set_ylabel('Active coefficients')
        ax2.spines['right'].set_visible(True)
        h = ax.get_lines()[:1] + ax2.get_lines()[:1]
        ax.legend(h, [l.get_label() for l in h], loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=1, frameon=False)
        out[end] = {'lambda': r['lambda'], 'df': r['df_sel'], 'gacv_min': min(r['gacv'])}
    fig.tight_layout()
    save_fig('ch18_frm_gacv')
    return out


def fig_frm_rolling(f, lam_fix):
    vix = index_close('VIX').reindex(f.index)
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.4), sharex=True)
    axes[0].plot(f.index, 1e4 * f['frm'], color=MainBlue, lw=0.9, label='FRM: average GACV penalty λ × 10,000 (13 banks)')
    axes[0].set_ylabel('λ × 10,000')
    axes[1].plot(f.index, 100 * f['density'], color=Purple, lw=0.9,
                 label=f'Share of active tail links at a fixed penalty λ = {lam_fix:.1e}')
    axes[1].set_ylabel('Active links (%)')
    ax3 = axes[1].twinx()
    ax3.plot(vix.index, vix.values, color=Orange, lw=0.7, label='VIX (right axis)')
    ax3.spines['right'].set_visible(True)
    ax3.set_ylabel('VIX')
    axes[0].set_xlim(f.index[0], f.index[-1])
    mark_events(axes[0])
    fig.tight_layout()
    h = axes[0].get_lines()[:1] + axes[1].get_lines()[:1] + ax3.get_lines()[:1]
    fig.legend(h, [l.get_label() for l in h], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=1, frameon=False)
    save_fig('ch18_frm_rolling')
    return {'corr_frm_vix': f['frm'].corr(vix), 'corr_dens_vix': f['density'].corr(vix),
            'frm_mean': f['frm'].mean(), 'dens_mean': f['density'].mean(),
            'dens_max': f['density'].max(), 'dens_max_date': f['density'].idxmax(),
            'dens_min': f['density'].min(), 'dens_min_date': f['density'].idxmin(), 'n_windows': len(f)}


# =============================================================================
# 6. Teste de stres
# =============================================================================
EPISODES = [('GFC: Lehman', '2008-09-01', '2008-11-30'), ('Euro crisis', '2011-07-01', '2011-10-31'),
            ('Brexit vote', '2016-06-20', '2016-07-15'), ('RO bank tax', '2018-12-10', '2019-01-31'),
            ('COVID-19', '2020-02-15', '2020-04-30'), ('SVB / Credit Suisse', '2023-03-01', '2023-04-15'),
            ('Tariff shock', '2025-03-25', '2025-04-30')]
INTL = US + EU


def stress_historical():
    """Pentru fiecare episod: cea mai proasta fereastra de 10 zile a portofoliului bancar cu ponderi egale."""
    Rl = joint_returns(INTL, start='2007-01-01')
    rows, port = {}, {}
    for name, a, b in EPISODES:
        keys = INTL + (RO if pd.Timestamp(a) >= pd.Timestamp('2010-01-01') else [])
        X = (Rl.loc[a:b] if keys == INTL else R.loc[a:b, keys])
        p = X.mean(axis=1).rolling(10).sum()
        end = p.idxmin()
        i = X.index.get_loc(end)
        win = X.iloc[i - 9:i + 1]
        cum = 100 * (np.exp(win.sum() / 100) - 1)
        rows[name] = cum.reindex(ALL)
        port[name] = {'loss': -100 * (np.exp(p.min() / 100) - 1), 'start': win.index[0], 'end': win.index[-1],
                      'n_banks': len(keys)}
    return pd.DataFrame(rows).T, port


def fig_stress_hist(H):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    im = ax.imshow(H.values, cmap='RdBu', vmin=-60, vmax=60, aspect='auto')
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            v = H.values[i, j]
            ax.text(j, i, '' if np.isnan(v) else f'{v:.0f}', ha='center', va='center', fontsize=6.5,
                    color='white' if abs(v) > 35 else 'black')
    ax.set_xticks(range(H.shape[1]))
    ax.set_xticklabels([NAMES[k] for k in H.columns], rotation=40, ha='right', fontsize=7)
    ax.set_yticks(range(H.shape[0]))
    ax.set_yticklabels(H.index, fontsize=7.5)
    cb = fig.colorbar(im, ax=ax, orientation='horizontal', fraction=0.05, pad=0.32)
    cb.set_label('Return over the worst 10 days of the equal-weighted bank portfolio (%)', fontsize=8)
    save_fig('ch18_stress_hist')


def weekly_returns(keys):
    p = prices(keys)
    w = p.resample('W-FRI').last().dropna()
    return 100 * np.log(w).diff().dropna()


def reverse_stress(target=25.0, weeks=4):
    """Testul de stres invers: cel mai plauzibil scenariu al factorilor care produce o pierdere data.

    Model: randamentele saptamanale ale bancilor = beta' f + eroare, f = (S&P 500, Euro Stoxx 50, BET);
    pe orizontul de h saptamani f ~ N(0, h Sigma). Pierderea portofoliului L = -b'f, b = media beta.
    Scenariul cel mai probabil cu L = target: f* = -target Sigma b / (b' Sigma b); distanta Mahalanobis target / sqrt(b' Sigma b)."""
    W = weekly_returns(ALL + ['SPX', 'SX5E', 'BET'])
    F = W[['SPX', 'SX5E', 'BET']]
    Xf = np.column_stack([np.ones(len(F)), F.values])
    betas = {k: np.linalg.lstsq(Xf, W[k].values, rcond=None)[0][1:] for k in ALL}
    b = np.mean([betas[k] for k in ALL], axis=0)
    S = weeks * F.cov().values
    sb = np.sqrt(b @ S @ b)
    fstar = -target * S @ b / sb ** 2
    d = target / sb
    from scipy.stats import norm
    # miscarile realizate ale factorilor in cele mai proaste 4 saptamani ale portofoliului (2020)
    port = W[ALL].mean(axis=1).rolling(weeks).sum()
    end = port.loc['2020'].idxmin()
    real = F.loc[:end].iloc[-weeks:].sum()
    return {'b': b, 'fstar': fstar, 'd': d, 'p': norm.cdf(-d), 'sigma_p': sb, 'target': target,
            'betas': {k: v for k, v in betas.items()}, 'real': real.values, 'real_loss': -port.loc[end],
            'real_end': end, 'real_model_loss': -b @ real.values, 'n_weeks': len(W)}


def fig_reverse(rv):
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    xs = np.arange(3)
    ax.bar(xs - 0.2, rv['fstar'], 0.38, color=IDAred,
           label=f'Most plausible scenario for a {rv["target"]:.0f}% loss of the bank portfolio in 4 weeks')
    ax.bar(xs + 0.2, rv['real'], 0.38, color=MainBlue, label=f'Realised: 4 weeks to {rv["real_end"].date()} (COVID-19)')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(xs)
    ax.set_xticklabels(['S&P 500', 'Euro Stoxx 50', 'BET'])
    ax.set_ylabel('4-week log return (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.15)
    save_fig('ch18_reverse_stress')


# =============================================================================
# RULARE
# =============================================================================
if __name__ == '__main__':
    print('1. bank indices')
    RESULTS['indices'] = fig_bank_indices()
    RESULTS['sample'] = {'start': R.index[0], 'end': R.index[-1], 'N': len(R)}
    RESULTS['index_vol'] = {k: R[k].std() * np.sqrt(252) for k in ['SPX', 'SX5E', 'BET']}
    print('2. MES / SRISK')
    mt = mes_table()
    fig_mes(mt)
    pick = fig_srisk(mt)
    mt.to_csv(os.path.join(HERE, 'ch18_mes_table.csv'))
    RESULTS['mes'] = mt.to_dict(orient='index')
    RESULTS['srisk_pick'] = pick
    print('3. CoVaR')
    RESULTS['qr_jpm'] = {str(k): v for k, v in fig_covar_qr().items()}
    c1 = covar_table(0.01)
    c5 = covar_table(0.05)
    c1.to_csv(os.path.join(HERE, 'ch18_covar1.csv'))
    c5.to_csv(os.path.join(HERE, 'ch18_covar5.csv'))
    fig_dcovar(c1)
    RESULTS['spearman_var_dcovar'] = fig_var_vs_dcovar(c1)
    fig_exposure(c1)
    RESULTS['covar1'] = c1.to_dict(orient='index')
    RESULTS['covar5'] = c5.to_dict(orient='index')
    from scipy.stats import spearmanr
    RESULTS['spearman_1_5'] = spearmanr(c1['dcovar'], c5['dcovar']).correlation
    dyn, betas = dynamic_covar()
    fig_dcovar_dynamic(dyn)
    RESULTS['dyn'] = {k: {'mean': f['dcovar'].mean(), 'max': f['dcovar'].max(), 'max_date': f['dcovar'].idxmax(),
                          'min': f['dcovar'].min(), 'b': betas[k],
                          'covid': f['dcovar'].loc['2020-03'].mean(), 'calm': f['dcovar'].loc['2017'].mean()}
                      for k, f in dyn.items()}
    print('4. Diebold-Yilmaz')
    st, p, st_r, pr = spill_static()
    fig_spill_table(st)
    RESULTS['thr_net'] = fig_spill_network(st)
    st['table'].to_csv(os.path.join(HERE, 'ch18_spill_table.csv'))
    RESULTS['spill'] = {'p': p, 'total': st['total'], 'to': st['to'].to_dict(), 'from': st['from'].to_dict(),
                        'net': st['net'].to_dict(), 'own': dict(zip(ALL, np.diag(st['table'].values))),
                        'p_ret': pr, 'total_ret': st_r['total'],
                        'pn_top': st['pairwise_net'].stack().sort_values(ascending=False).head(5).to_dict(),
                        'region_block': {f'{a}->{b}': st['table'].loc[[k for k in ALL if region_of(k) == b],
                                                                      [k for k in ALL if region_of(k) == a]].values.sum()
                                         / sum(region_of(k) == b for k in ALL)
                                         for a in ['US', 'EU', 'RO'] for b in ['US', 'EU', 'RO']}}
    tot, net = spill_rolling()
    tot.to_csv(os.path.join(HERE, 'ch18_spill_rolling.csv'))
    fig_spill_rolling(tot, net)
    RESULTS['spill_roll'] = {'min': tot.min(), 'min_date': tot.idxmin(), 'max': tot.max(), 'max_date': tot.idxmax(),
                             'mean': tot.mean(), 'last': tot.iloc[-1], 'last_date': tot.index[-1],
                             'covid': tot.loc['2020-03':'2020-06'].max(), 'y2019': tot.loc['2019'].mean(),
                             'svb': tot.loc['2023-03':'2023-06'].max(), 'y2024': tot.loc['2024'].mean(),
                             'ro_net_mean': net[RO].sum(axis=1).mean(), 'us_net_mean': net[US].sum(axis=1).mean(),
                             'eu_net_mean': net[EU].sum(axis=1).mean(),
                             'us_net_pos': (net[US].sum(axis=1) > 0).mean()}
    print('5. FRM')
    RESULTS['frm_gacv'] = fig_frm_gacv()
    f, lam_fix = frm_series()
    RESULTS['frm'] = {**fig_frm_rolling(f, lam_fix), 'lam_fix': lam_fix}
    print('6. stress tests')
    H, port = stress_historical()
    H.to_csv(os.path.join(HERE, 'ch18_stress_hist.csv'))
    fig_stress_hist(H)
    RESULTS['stress'] = {'port': port, 'table': H.to_dict(orient='index')}
    rv = reverse_stress()
    fig_reverse(rv)
    RESULTS['reverse'] = rv
    with open(os.path.join(HERE, 'ch18_results.json'), 'w') as fjs:
        json.dump(jsonable(RESULTS), fjs, indent=1, default=str)
    print('saved ch18_results.json')

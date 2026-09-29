"""
Generator pentru graficele si cifrele Capitolului 19: recapitulare si studiu de caz integrat
==========================================================================================
Studiul de caz: indicele BET (valori oficiale de inchidere, 2000-2026), un singur fir:
fapte stilizate -> GARCH(1,1)-t -> VaR 1% pentru ziua urmatoare -> backtesting.
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Conventie: nivelul = probabilitatea cozii alpha (VaR 1%); pierderea L = -r, in % din pozitie.
Cifrele sunt salvate in ch19_results.json (folosite de generatoarele de slide-uri).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import log_returns  # noqa: E402
from case_study import (ALPHA, MODELS, stylised_facts, kurtosis_boot_ci, garch_t_fit, garch_summary,  # noqa: E402
                        rolling_var, backtest_table, kupiec, binom_band, t_std_q, acf)
from inference19 import hill_ci, profile_ci, formal_eval, kupiec_power, kupiec_mde  # noqa: E402

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
Gray     = '#7F7F7F'   # doar linii de referinta, benzi, grila
Teal     = '#17A2B8'
MODEL_COL = {'HS': MainBlue, 'Normal': Orange, 'GARCH-t': Forest, 'FHS': IDAred}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
EVAL_FROM = '2005-01-01'


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


def fig_legend_bottom(fig, axes, ncol=3):
    """O singura legenda sub o figura cu mai multe panouri."""
    h, l = [], []
    for ax in axes:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh)
                l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=ncol, frameon=False)


# =============================================================================
# DATE: randamente log zilnice ale BET, in %
# =============================================================================
r = 100 * log_returns('bet')
RES = {}


# =============================================================================
# 1. FAPTE STILIZATE
# =============================================================================
def part_facts():
    sf = stylised_facts(r)
    h = hill_ci(r.values)                     # indicele de coada (kurtosis-ul nu este consistent daca alpha < 4)
    sf['hill'] = {k: v for k, v in h.items() if k != 'draws'}
    sf['ppy'] = len(r) / ((r.index[-1] - r.index[0]).days / 365.25)
    sf['ann_vol'] = r.std() * np.sqrt(sf['ppy'])
    RES['facts'] = sf

    z = np.sort(((r - r.mean()) / r.std()).values)
    p = (np.arange(1, len(z) + 1) - 0.5) / len(z)
    zn = stats.norm.ppf(p)
    lags = np.arange(1, 51)
    a_r, a_abs = acf(r.values, 50), acf(np.abs(r.values), 50)
    band = 1.96 / np.sqrt(len(r))
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.3))
    ax = axes[0]
    ax.scatter(zn, z, s=4, color=MainBlue, label='BET standardised daily log returns')
    ax.plot([-5, 5], [-5, 5], color=Gray, lw=0.8, ls='--', label='Normal distribution (45-degree line)')
    ax.set_xlabel('Normal quantile')
    ax.set_ylabel('Empirical quantile')
    ax.set_title('Quantile-quantile plot', fontsize=9, loc='left')
    ax = axes[1]
    ax.bar(lags - 0.2, a_r, width=0.4, color=MainBlue, label='ACF of returns $r_t$')
    ax.bar(lags + 0.2, a_abs, width=0.4, color=IDAred, label='ACF of absolute returns $|r_t|$')
    ax.axhspan(-band, band, color=Gray, alpha=0.25, lw=0, label='95% band under i.i.d.')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag (trading days)')
    ax.set_ylabel('Autocorrelation')
    ax.set_title('Autocorrelation function', fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend_bottom(fig, axes, ncol=2)
    save_fig('ch19_bet_facts')


# =============================================================================
# 2. GARCH(1,1)-t PE TOATA SELECTIA
# =============================================================================
def part_garch():
    res = garch_t_fit(r)
    g = garch_summary(res)
    RES['garch'] = g
    RES['garch']['profile'] = profile_ci(r.values, res)   # CI profil pentru alpha + beta, restrans la < 1
    sig = res.conditional_volatility
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(r.index, r.values, color=MainBlue, lw=0.4, label='BET daily log return (%)')
    ax.plot(sig.index, 2 * sig.values, color=IDAred, lw=0.7, label=r'$\pm 2\hat\sigma_t$, GARCH(1,1)-t')
    ax.plot(sig.index, -2 * sig.values, color=IDAred, lw=0.7)
    ax.axhline(0, color=Gray, lw=0.4)
    ax.set_xlim(r.index[0], r.index[-1])
    ax.set_ylabel('%')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch19_bet_garch')
    s = sig.copy()
    RES['garch']['sigma_last'] = float(s.iloc[-1])                                   # sigma_T
    RES['garch']['sigma_next'] = float(np.sqrt(res.forecast(horizon=1).variance.iloc[-1, 0]))   # sigma_{T+1}
    RES['garch']['mu'] = float(res.params['mu'])
    RES['garch']['r_last'] = float(r.iloc[-1])
    RES['garch']['sigma_max'] = float(s.max())
    RES['garch']['sigma_max_date'] = str(s.idxmax().date())
    return res


# =============================================================================
# 3-4. VaR 1% PENTRU ZIUA URMATOARE SI BACKTESTING
# =============================================================================
def part_var(full_res):
    fc = rolling_var(r, EVAL_FROM)
    fc.to_csv(os.path.join(HERE, 'ch19_forecasts_bet.csv'))
    bt = backtest_table(fc)
    RES['backtest'] = bt
    RES['eval'] = dict(start=str(fc.index[0].date()), end=str(fc.index[-1].date()), T=len(fc))
    lo, hi = binom_band(len(fc))
    RES['eval']['band'] = [lo, hi]
    RES['es'] = {m: float(fc[m + '_ES'].mean()) for m in MODELS}
    RES['formal'] = formal_eval(fc)
    pw = {f'{T}_{p1}': kupiec_power(T, p1)[0] for T in (250, 1000, len(fc)) for p1 in (0.013, 0.015, 0.02)}
    RES['power'] = dict(pw=pw, mde={str(T): kupiec_mde(T) for T in (250, 1000, len(fc))}, T=len(fc),
                        rej250=[int(x) for x in kupiec_power(250, 0.02)[1][:12]])
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    grid = np.arange(0.002, 0.0405, 0.0005)
    for T, c in [(250, Orange), (1000, MainBlue), (len(fc), IDAred)]:
        ax.plot(100 * grid, [kupiec_power(T, p1)[0] for p1 in grid], color=c, lw=1.2, label=f'T = {T} days')
    ax.axhline(0.8, color=Gray, lw=0.6, ls='--')
    ax.axhline(0.05, color=Gray, lw=0.6, ls=':')
    ax.axvline(1.0, color='black', lw=0.6, ls='--', label='Null: 1%')
    ax.set_xlabel('True breach rate of the VaR 1% model (%)')
    ax.set_ylabel('Rejection probability of\nthe 5% Kupiec test')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch19_kupiec_power')

    # grafic: pierderi si VaR 1% (2020-2026)
    d = fc.loc['2020-01-01':]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(d.index, d['L'].clip(lower=0), width=1.5, color=Teal, alpha=0.7, label='Daily loss (gains set to 0)')
    ax.plot(d.index, d['Normal'], color=Orange, lw=0.9, label='Normal VaR 1% (500 days)')
    ax.plot(d.index, d['FHS'], color=IDAred, lw=0.9, label='FHS VaR 1% (GARCH-t filter)')
    exc = d['L'] > d['FHS']
    ax.scatter(d.index[exc], d['L'][exc], s=12, color='black', zorder=3, label='Loss above FHS VaR 1%')
    ax.set_ylabel('Loss = negative log return (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch19_bet_var')
    RES['var_2020'] = dict(n=len(d), x_fhs=int(exc.sum()), x_normal=int((d['L'] > d['Normal']).sum()),
                          fhs_max=float(d['FHS'].max()), fhs_max_date=str(d['FHS'].idxmax().date()),
                          fhs_last=float(fc['FHS'].iloc[-1]), normal_last=float(fc['Normal'].iloc[-1]))

    # grafic: ratele depasirilor
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    x = np.arange(len(MODELS))
    rates = [100 * bt[m]['rate'] for m in MODELS]
    ax.bar(x, rates, width=0.55, color=[MODEL_COL[m] for m in MODELS])
    ax.axhspan(100 * lo, 100 * hi, color=Gray, alpha=0.25, lw=0, label='95% binomial band if the rate is 1%')
    ax.axhline(1.0, color='black', lw=0.8, ls='--', label='Target: 1%')
    for i, v in enumerate(rates):
        ax.text(i, v + 0.04, f'{v:.2f}%', ha='center', va='bottom', fontsize=8, color='black')
    ax.set_xticks(x)
    ax.set_xticklabels(MODELS)
    ax.set_ylabel('Share of days with loss > VaR 1% (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch19_breach_rates')

    # grafic: depasiri pe 250 de zile si zonele Basel
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.axhspan(-0.5, 4.5, color=Forest, alpha=0.08, lw=0, label='Green zone (0-4)')
    ax.axhspan(4.5, 9.5, color=Amber, alpha=0.15, lw=0, label='Yellow zone (5-9)')
    top = 0
    for m in MODELS:
        roll = (fc['L'] > fc[m]).astype(int).rolling(250).sum()
        top = max(top, roll.max())
        ax.plot(roll.index, roll.values, color=MODEL_COL[m], lw=0.9, label=m)
    ax.axhspan(9.5, top + 2, color=IDAred, alpha=0.08, lw=0, label='Red zone (10+)')
    ax.set_ylim(-0.5, top + 2)
    ax.set_xlim(fc.index[0], fc.index[-1])
    ax.set_ylabel('Breaches in the last 250 days')
    legend_outside_bottom(ax, ncol=4, y=-0.1)
    save_fig('ch19_rolling_breaches')

    # capcana: informatie din viitor (parametri estimati pe toata selectia)
    p = full_res.params
    sig_full = full_res.conditional_volatility.loc[fc.index]
    var_full = -(p['mu'] + sig_full * t_std_q(p['nu'], ALPHA))
    hs_full = np.quantile(fc['L'], 1 - ALPHA)
    k_full = kupiec((fc['L'] > var_full).astype(int))
    k_hsfull = kupiec((fc['L'] > hs_full).astype(int))
    RES['lookahead'] = dict(garch_full_rate=k_full['rate'], garch_full_p=k_full['p'], garch_full_x=k_full['x'],
                            hs_full_rate=k_hsfull['rate'], hs_full_x=k_hsfull['x'], hs_full_var=float(hs_full))
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    lab = ['HS', 'GARCH-t']
    oos = [100 * bt['HS']['rate'], 100 * bt['GARCH-t']['rate']]
    ins = [100 * k_hsfull['rate'], 100 * k_full['rate']]
    x = np.arange(2)
    ax.bar(x - 0.18, oos, 0.34, color=MainBlue, label='Rolling estimation (only past data)')
    ax.bar(x + 0.18, ins, 0.34, color=Amber, label='Parameters from the full sample (look-ahead)')
    ax.axhline(1.0, color='black', lw=0.8, ls='--', label='Target: 1%')
    for i in range(2):
        ax.text(i - 0.18, oos[i] + 0.03, f'{oos[i]:.2f}%', ha='center', va='bottom', fontsize=8, color='black')
        ax.text(i + 0.18, ins[i] + 0.03, f'{ins[i]:.2f}%', ha='center', va='bottom', fontsize=8, color='black')
    ax.set_xticks(x)
    ax.set_xticklabels(lab)
    ax.set_ylabel('Breach rate of VaR 1% (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.1)
    save_fig('ch19_lookahead')


if __name__ == '__main__':
    part_facts()
    full = part_garch()
    part_var(full)
    with open(os.path.join(HERE, 'ch19_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print('saved ch19_results.json')

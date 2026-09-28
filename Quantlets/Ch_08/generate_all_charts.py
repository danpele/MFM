"""
Generator pentru graficele din Capitolul 8: Backtesting si evaluarea prognozelor de risc
======================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date: S&P 500, BET si Bitcoin (data/market), EUR/RON (cursul de referinta BNR).
Prognoze VaR/ES la o zi pe fereastra mobila (1000 de observatii): HS, Normal, Student-t,
GARCH-t, FHS, GARCH-EVT; evaluare din 2007 (EUR/RON din 2009, Bitcoin din 2017).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.dates as mdates
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_data as M   # noqa: E402

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
Gray     = '#7F7F7F'
LightGray = '#DADADA'
Teal = '#17A2B8'
MCOL = {'HS': Teal, 'Normal': Amber, 'Student-t': Purple, 'GARCH-t': MainBlue, 'FHS': Forest, 'GARCH-EVT': IDAred}
PV_CMAP = LinearSegmentedColormap.from_list('pv', [IDAred, '#F4B6B6', '#FFFFFF', '#BFD8BF', Forest])

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')


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


def pv_heatmap(ax, P, fmt='{:.2f}', title=None):
    """Harta valorilor p: rosu = respingere, verde = nerespingere (scala log)."""
    Z = np.log10(np.clip(P.values.astype(float), 1e-4, 1))
    ax.imshow(Z, cmap=PV_CMAP, vmin=-4, vmax=0, aspect='auto')
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            v = P.values[i, j]
            txt = '<0.001' if v < 0.001 else (f'{v:.3f}' if v < 0.01 else fmt.format(v))
            ax.text(j, i, txt, ha='center', va='center', fontsize=7)
    ax.set_xticks(range(P.shape[1]), P.columns, fontsize=7.5)
    ax.set_yticks(range(P.shape[0]), P.index, fontsize=7.5)
    for s in ax.spines.values():
        s.set_visible(False)
    if title:
        ax.set_title(title, fontsize=9)


# =============================================================================
# DATE: prognozele tuturor modelelor pentru cele patru active
# =============================================================================
_FC = {}


def fc(name):
    if name not in _FC:
        _FC[name] = M.get_forecasts(name)
    return _FC[name]


def hits(name, model, col='VaR1'):
    df = fc(name)[0][model]
    return (df['L'] > df[col]).astype(int)


# =============================================================================
# FIG 1: patru active, pierderi si VaR 1% GARCH-EVT
# =============================================================================
def fig_four_assets():
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 3.9), sharex=False)
    out = {}
    for ax, n in zip(axs.flat, M.ASSETS):
        df = fc(n)[0]['GARCH-EVT']
        ax.plot(df.index, 100 * df['L'], color=Orange, lw=0.5, alpha=0.7, label='Daily loss')
        ax.plot(df.index, 100 * df['VaR1'], color=IDAred, lw=0.7, label='VaR 1% (GARCH-EVT)')
        h = df['L'] > df['VaR1']
        ax.scatter(df.index[h], 100 * df['L'][h], s=4, color=MainBlue, zorder=3, label='Breach')
        ax.set_title(M.LABELS[n], fontsize=9)
        ax.set_ylabel('Loss (%)', fontsize=8)
        ax.tick_params(labelsize=7)
        ax.xaxis.set_major_locator(mdates.YearLocator(4 if n != 'btc' else 2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        out[n] = dict(start=str(df.index[0].date()), end=str(df.index[-1].date()), T=len(df))
    axs[1, 0].legend(loc='upper center', bbox_to_anchor=(1.1, -0.18), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch8_four_assets')
    return out


# =============================================================================
# FIG 2: S&P 500 -- pierderi, VaR 1% HS si GARCH-t, depasiri
# =============================================================================
def fig_sp500_var():
    F = fc('sp500')[0]
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    L = F['HS']['L']
    ax.plot(L.index, 100 * L, color=Orange, lw=0.5, alpha=0.6, label='Daily loss of the S&P 500')
    for m, ls in (('HS', '-'), ('GARCH-t', '-')):
        ax.plot(L.index, 100 * F[m]['VaR1'], color=MCOL[m], lw=0.8, ls=ls, label=f'VaR 1%, {m}')
    for m, mk in (('HS', 'o'), ('GARCH-t', 'x')):
        h = F[m]['L'] > F[m]['VaR1']
        ax.scatter(L.index[h], 100 * L[h] + (0.4 if m == 'GARCH-t' else 0), s=7, marker=mk, color=MCOL[m],
                   zorder=3, label=f'Breach, {m}')
    ax.set_ylabel('Loss (%)')
    ax.set_ylim(-4, 13)
    legend_outside_bottom(ax, ncol=3, y=-0.12)
    save_fig('ch8_sp500_var')
    return {m: int(hits('sp500', m).sum()) for m in ('HS', 'GARCH-t')}


# =============================================================================
# FIG 3: zoom COVID-19 (feb.-iun. 2020), toate modelele
# =============================================================================
def fig_covid_zoom():
    F = fc('sp500')[0]
    a, b = '2020-02-01', '2020-06-30'
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    L = F['HS']['L'].loc[a:b]
    ax.bar(L.index, 100 * L, color=Orange, alpha=0.5, width=1.0, label='Daily loss')
    out = {}
    for m in M.MODELS:
        v = F[m]['VaR1'].loc[a:b]
        ax.plot(v.index, 100 * v, color=MCOL[m], lw=1.0, label=m)
        out[m] = int((L > v).sum())
    ax.set_ylabel('Loss / VaR 1% (%)')
    legend_outside_bottom(ax, ncol=7, y=-0.12)
    save_fig('ch8_covid_zoom')
    out['max_loss'] = float(100 * L.max())
    out['max_loss_day'] = str(L.idxmax().date())
    out['T'] = len(L)
    return out


# =============================================================================
# FIG 4: rata depasirilor VaR 1% pe modele si active
# =============================================================================
def breach_table(col='VaR1', p=0.01):
    rows = {}
    for n in M.ASSETS:
        for m in M.MODELS:
            h = hits(n, m, col).values
            k = M.kupiec(h, p)
            c = M.christoffersen(h, p)
            d = M.duration_test(h)
            rows[(n, m)] = dict(T=k['T'], x=k['x'], rate=k['rate'], LR_uc=k['LR'], p_uc=k['p'], LR_ind=c['LR_ind'],
                                p_ind=c['p_ind'], LR_cc=c['LR_cc'], p_cc=c['p_cc'], pi01=c['pi01'], pi11=c['pi11'],
                                b=d['b'], LR_dur=d['LR'], p_dur=d['p'])
    return rows


def fig_breach_rates(tab):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    w = 0.13
    for i, m in enumerate(M.MODELS):
        y = [100 * tab[(n, m)]['rate'] for n in M.ASSETS]
        ax.bar(np.arange(4) + (i - 2.5) * w, y, w, color=MCOL[m], label=m)
    ax.axhline(1.0, color='black', lw=0.8, ls='--', label='Nominal 1%')
    ax.set_xticks(range(4), [M.LABELS[n] for n in M.ASSETS])
    ax.set_ylabel('Breach rate of VaR 1% (%)')
    legend_outside_bottom(ax, ncol=7, y=-0.13)
    save_fig('ch8_breach_rates')


# =============================================================================
# FIG 5: statistica Kupiec in functie de numarul de depasiri
# =============================================================================
def fig_kupiec_curve():
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.8))
    out = {}
    for ax, T in zip(axs, (250, 1000)):
        xs = np.arange(0, int(0.03 * T) + 1)
        lr = np.array([M.kupiec(np.r_[np.ones(x), np.zeros(T - x)], 0.01)['LR'] for x in xs])
        acc = lr < stats.chi2.ppf(0.95, 1)
        ax.bar(xs[acc], lr[acc], color=Forest, width=0.8, label='Not rejected at 5%')
        ax.bar(xs[~acc], lr[~acc], color=IDAred, width=0.8, label='Rejected at 5%')
        ax.axhline(stats.chi2.ppf(0.95, 1), color='black', ls='--', lw=0.8, label=r'$\chi^2_1$ 5% critical value 3.84')
        ax.set_title(f'T = {T} days, p = 1%', fontsize=9)
        ax.set_xlabel('Number of breaches x')
        ax.set_ylim(0, 25)
        out[T] = dict(lo=int(xs[acc].min()), hi=int(xs[acc].max()))
    axs[0].set_ylabel(r'LR$_{uc}$')
    axs[0].legend(loc='upper center', bbox_to_anchor=(1.1, -0.2), ncol=3, frameon=False)
    save_fig('ch8_kupiec_curve')
    return out


# =============================================================================
# FIG 6: valori p ale testelor VaR (Kupiec, Christoffersen, durate)
# =============================================================================
def fig_var_pvalues(tab):
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=True)
    for ax, (key, title) in zip(axs, (('p_uc', 'Kupiec POF'), ('p_cc', 'Christoffersen CC'),
                                      ('p_dur', 'Duration (Weibull)'))):
        P = pd.DataFrame({M.LABELS[n]: [tab[(n, m)][key] for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
        pv_heatmap(ax, P, title=title)
        ax.tick_params(axis='x', rotation=30)
    plt.tight_layout()
    save_fig('ch8_var_pvalues')


# =============================================================================
# FIG 7: cronologia depasirilor (S&P 500)
# =============================================================================
def fig_breach_timeline():
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    ms = ['HS', 'Normal', 'Student-t', 'GARCH-t', 'FHS', 'GARCH-EVT']
    for i, m in enumerate(ms):
        h = hits('sp500', m)
        d = h.index[h.values == 1]
        ax.vlines(d, i - 0.35, i + 0.35, color=MCOL[m], lw=0.8)
    ax.set_yticks(range(len(ms)), ms)
    ax.invert_yaxis()
    ax.set_xlabel('Breach days of VaR 1%, S&P 500')
    save_fig('ch8_breach_timeline')
    F = fc('sp500')[0]
    by_year = {m: {str(y): int(v) for y, v in hits('sp500', m).groupby(F[m].index.year).sum().items()} for m in ms}
    return by_year


# =============================================================================
# FIG 8: functia de supravietuire a duratelor dintre depasiri
# =============================================================================
def fig_durations(tab):
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    out = {}
    for m in ('HS', 'Normal', 'GARCH-t', 'GARCH-EVT'):
        D, _, _ = M.durations(hits('sp500', m).values)
        Ds = np.sort(D)
        surv = 1 - np.arange(1, len(Ds) + 1) / (len(Ds) + 1)
        ax.step(Ds, surv, where='post', color=MCOL[m], label=f'{m} (b = {tab[("sp500", m)]["b"]:.2f})')
        out[m] = dict(n=len(D), median=float(np.median(D)), share_le5=float(np.mean(D <= 5)))
    d = np.linspace(1, 800, 200)
    ax.plot(d, (1 - 0.01) ** d, color='black', ls='--', lw=0.9, label='No memory, p = 1% (geometric)')
    ax.set_yscale('log')
    ax.set_xlabel('Days between consecutive breaches of VaR 1% (S&P 500)')
    ax.set_ylabel('Share of durations > d')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch8_durations')
    return out


# =============================================================================
# FIG 9: semaforul Basel -- exceptii pe 250 de zile (S&P 500)
# =============================================================================
def rolling_exceptions(name, model, col='VaR1', n=250):
    return hits(name, model, col).rolling(n).sum().dropna()


def fig_traffic_light():
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.axhspan(-0.5, 4.5, color=Forest, alpha=0.10, lw=0)
    ax.axhspan(4.5, 9.5, color='#F1C40F', alpha=0.15, lw=0)
    ax.axhspan(9.5, 40, color=IDAred, alpha=0.10, lw=0)
    out = {}
    for m in ('HS', 'Normal', 'GARCH-t', 'FHS'):
        x = rolling_exceptions('sp500', m)
        ax.plot(x.index, x, color=MCOL[m], lw=0.9, label=m)
        out[m] = dict(max=int(x.max()), max_day=str(x.idxmax().date()), share_red=float(np.mean(x >= 10)),
                      share_yellow=float(np.mean((x >= 5) & (x <= 9))), last=int(x.iloc[-1]))
    ax.text(1.01, 2 / 36.5, 'green', color=Forest, fontsize=8, transform=ax.transAxes)
    ax.text(1.01, 7.5 / 36.5, 'yellow /\namber', color=Amber, fontsize=8, transform=ax.transAxes)
    ax.text(1.01, 20 / 36.5, 'red', color=IDAred, fontsize=8, transform=ax.transAxes)
    ax.set_ylim(-0.5, 36)
    ax.set_ylabel('Exceptions of VaR 1%\nin the last 250 days')
    legend_outside_bottom(ax, ncol=4, y=-0.13)
    save_fig('ch8_traffic_light')
    return out


# =============================================================================
# TESTE ES: McNeil-Frey, Acerbi-Szekely, Du-Escanciano
# =============================================================================
def es_table():
    rows = {}
    for n in M.ASSETS:
        F, tails = fc(n)
        for m in M.MODELS:
            df = F[m]
            mf = M.mcneil_frey(df['L'].values, df['VaR2.5'].values, df['ES2.5'].values, df['scale'].values)
            z = M.z_pvalues(df, m, tails, M=2000)
            de = M.du_escanciano(df['pit'].values)
            rows[(n, m)] = dict(n_hit=mf['n'], MF_mean=mf['mean'], MF_t=mf['t'], MF_p=mf['p'], Z1=z['Z1'], p1=z['p1'],
                                Z2=z['Z2'], p2=z['p2'], Z2_crit=z['crit2'], U_ES=de['U'], p_U=de['pU'], C_ES=de['C'],
                                p_C=de['pC'], meanH=de['meanH'])
    return rows


def fig_es_pvalues(tab):
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=True)
    for ax, (key, title) in zip(axs, (('MF_p', 'McNeil-Frey'), ('p2', 'Acerbi-Szekely Z2'),
                                      ('p_U', 'Du-Escanciano U'))):
        P = pd.DataFrame({M.LABELS[n]: [tab[(n, m)][key] for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
        pv_heatmap(ax, P, title=title)
        ax.tick_params(axis='x', rotation=30)
    plt.tight_layout()
    save_fig('ch8_es_pvalues')


def rolling_z2(name, model, n=250):
    df = fc(name)[0][model]
    L, v, e = df['L'].values, df['VaR2.5'].values, df['ES2.5'].values
    term = np.where(L > v, L / e, 0.0)
    z2 = 1 - pd.Series(term, index=df.index).rolling(n).sum() / (n * M.A_ES)
    return z2.dropna()


def fig_z2_rolling():
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    out = {}
    for m in ('HS', 'Normal', 'GARCH-t', 'FHS'):
        z = rolling_z2('sp500', m)
        ax.plot(z.index, z, color=MCOL[m], lw=0.9, label=m)
        out[m] = dict(min=float(z.min()), min_day=str(z.idxmin().date()), share_below07=float(np.mean(z < -0.7)),
                      share_below18=float(np.mean(z < -1.8)), last=float(z.iloc[-1]))
    ax.axhline(-0.70, color=Amber, ls='--', lw=0.9, label='Threshold -0.70 (5%)')
    ax.axhline(-1.8, color=IDAred, ls='--', lw=0.9, label='Threshold -1.8 (0.01%)')
    ax.set_ylabel(r'$Z_2$ over the last 250 days')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    save_fig('ch8_z2_rolling')
    return out


def fig_mf_residuals():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    data, out = [], {}
    for m in M.MODELS:
        df = fc('sp500')[0][m]
        h = df['L'] > df['VaR2.5']
        e = ((df['L'] - df['ES2.5']) / df['scale'])[h]
        data.append(e.values)
        out[m] = float(e.mean())
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=True,
                    flierprops=dict(marker='.', markersize=3, markeredgecolor=Gray))
    for b, m in zip(bp['boxes'], M.MODELS):
        b.set_facecolor(MCOL[m]); b.set_alpha(0.5)
    for i, m in enumerate(M.MODELS):
        ax.plot(i + 1, out[m], 'D', color='black', ms=4, label='Mean' if i == 0 else None)
    ax.axhline(0, color='black', lw=0.8, ls='--', label='Expected under a correct ES (mean 0)')
    ax.set_xticks(range(1, 7), M.MODELS)
    ax.set_ylabel('Exceedance residual (L - ES) / scale')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    save_fig('ch8_mf_residuals')
    return out


# =============================================================================
# FIG: elicitabilitate -- pierderea cuantila si FZ0 in medie
# =============================================================================
def fig_elicitability(nu=4, a=0.025, n=2_000_000, seed=3):
    rng = np.random.default_rng(seed)
    L = rng.standard_t(nu, n) * np.sqrt((nu - 2) / nu)
    q_true, es_true = M.t_std_q(nu, a), M.t_std_es(nu, a)
    vs = np.linspace(1.2, 3.6, 121)
    m_plus = np.array([np.mean(np.maximum(L - v, 0)) for v in vs])      # E[(L - v)+]
    pin = m_plus - a * (np.mean(L) - vs)                                 # E[(1{L>v} - a)(L - v)]
    es_grid = np.linspace(1.6, 5.0, 121)
    V, E = np.meshgrid(vs, es_grid)
    FZ = np.interp(V, vs, m_plus) / (a * E) + V / E + np.log(E) - 1
    FZ = np.where(E >= V, FZ, np.nan)
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axs[0]
    ax.plot(vs, pin, color=MainBlue, label='Expected pinball loss')
    ax.axvline(q_true, color=IDAred, ls='--', lw=0.9, label=f'True VaR 2.5% = {q_true:.2f}')
    ax.set_xlabel('Reported VaR v')
    ax.set_ylabel('Expected loss')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    ax = axs[1]
    cs = ax.contour(V, E, FZ, levels=np.nanquantile(FZ, [0.01, 0.03, 0.08, 0.15, 0.3, 0.5]), colors=MainBlue,
                    linewidths=0.8)
    ax.clabel(cs, fontsize=6, fmt='%.3f')
    i = np.nanargmin(FZ)
    ax.plot(V.flat[i], E.flat[i], 'o', color=Forest, ms=5, label='Minimum of expected FZ0')
    ax.plot(q_true, es_true, 'x', color=IDAred, ms=8, label=f'True (VaR, ES) = ({q_true:.2f}, {es_true:.2f})')
    ax.set_xlabel('Reported VaR v')
    ax.set_ylabel('Reported ES e')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch8_elicitability')
    return dict(nu=nu, q=q_true, es=es_true, v_min=float(vs[np.argmin(pin)]), fz_v=float(V.flat[i]),
                fz_e=float(E.flat[i]))


# =============================================================================
# PIERDEREA FZ0, DIEBOLD-MARIANO, MCS
# =============================================================================
def fz_losses(name):
    F = fc(name)[0]
    return pd.DataFrame({m: M.fz0(F[m]['L'].values, F[m]['VaR2.5'].values, F[m]['ES2.5'].values)
                         for m in M.MODELS}, index=F['HS'].index)


def fz_table():
    out = {}
    for n in M.ASSETS:
        Lf = fz_losses(n)
        best = Lf.mean().idxmin()
        dm = {m: M.diebold_mariano(Lf[m], Lf[best]) for m in M.MODELS if m != best}
        mc = M.mcs(Lf)
        out[n] = dict(mean={m: float(v) for m, v in Lf.mean().items()}, best=best,
                      dm={m: dict(DM=d['DM'], p=d['p'], dbar=d['dbar']) for m, d in dm.items()},
                      mcs={m: float(v) for m, v in mc.items()},
                      pin={m: float(M.pinball(fc(n)[0][m]['L'].values, fc(n)[0][m]['VaR1'].values, 0.01).mean())
                           for m in M.MODELS})
    return out


def fig_fz0(tab):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    w = 0.13
    for i, m in enumerate(M.MODELS):
        y = [tab[n]['mean'][m] - tab[n]['mean'][tab[n]['best']] for n in M.ASSETS]
        ax.bar(np.arange(4) + (i - 2.5) * w, y, w, color=MCOL[m], label=m)
    ax.set_xticks(range(4), [M.LABELS[n] for n in M.ASSETS])
    ax.set_ylabel('Mean FZ0 loss minus\nthat of the best model')
    legend_outside_bottom(ax, ncol=6, y=-0.13)
    save_fig('ch8_fz0')


def fig_dm_matrix(name='sp500'):
    Lf = fz_losses(name)
    D = pd.DataFrame(index=M.MODELS, columns=M.MODELS, dtype=float)
    for a in M.MODELS:
        for b in M.MODELS:
            D.loc[a, b] = np.nan if a == b else M.diebold_mariano(Lf[a], Lf[b])['DM']
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    im = ax.imshow(D.values.astype(float), cmap=LinearSegmentedColormap.from_list('dm', [Forest, '#FFFFFF', IDAred]),
                   vmin=-6, vmax=6)
    for i in range(6):
        for j in range(6):
            if i != j:
                ax.text(j, i, f'{D.values[i, j]:.1f}', ha='center', va='center', fontsize=7.5)
    ax.set_xticks(range(6), M.MODELS, rotation=30, fontsize=7.5)
    ax.set_yticks(range(6), M.MODELS, fontsize=7.5)
    ax.set_xlabel('Model B')
    ax.set_ylabel('Model A')
    cb = plt.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label('DM statistic (A minus B)', fontsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    save_fig('ch8_dm_matrix')
    return {f'{a}|{b}': float(D.loc[a, b]) for a in M.MODELS for b in M.MODELS if a != b}


def fig_mcs(tab):
    P = pd.DataFrame({M.LABELS[n]: [tab[n]['mcs'][m] for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    pv_heatmap(ax, P)
    ax.set_title('MCS p-values (FZ0 loss); models with p >= 0.10 are in the 90% MCS', fontsize=8.5)
    save_fig('ch8_mcs')


# =============================================================================
# PREDICTIE CONFORMALA
# =============================================================================
def conformal_table(a=0.01):
    out = {}
    for n in M.ASSETS:
        r = M.load_returns(n)
        c = M.conformal_var(r, a=a).loc[fc(n)[0]['HS'].index[0]:]
        reg = M.regimes(r, c.index)
        g = fc(n)[0]['GARCH-t'].reindex(c.index)
        col = {0.01: 'VaR1', 0.05: 'VaR5', 0.025: 'VaR2.5'}[a]
        hs, ha, hg = c['L'] > c['VaR_split'], c['L'] > c['VaR_aci'], g['L'] > g[col]
        out[n] = dict(T=len(c), n_crisis=int(reg.sum()),
                      split=[float(hs.mean()), float(hs[~reg].mean()), float(hs[reg].mean())],
                      aci=[float(ha.mean()), float(ha[~reg].mean()), float(ha[reg].mean())],
                      garch=[float(hg.mean()), float(hg[~reg].mean()), float(hg[reg].mean())],
                      inf_share=float(np.isinf(c['VaR_aci']).mean()),
                      kup_split=M.kupiec(hs.values, a)['p'], kup_aci=M.kupiec(ha.values, a)['p'])
    return out


def fig_conformal_path():
    r = M.load_returns('sp500')
    c = M.conformal_var(r, a=0.01).loc['2019-07-01':'2021-06-30']
    g = fc('sp500')[0]['GARCH-t']['VaR1'].loc[c.index]
    fig, axs = plt.subplots(2, 1, figsize=(6.8, 3.6), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1]))
    ax = axs[0]
    ax.bar(c.index, 100 * c['L'], color=Orange, alpha=0.5, width=1.0, label='Daily loss')
    ax.plot(c.index, 100 * c['VaR_split'], color=MainBlue, lw=1.0, label='Split conformal VaR 1%')
    va = np.where(np.isinf(c['VaR_aci']), np.nan, c['VaR_aci'])
    ax.plot(c.index, 100 * va, color=IDAred, lw=1.0, label='ACI VaR 1% (gaps: infinite)')
    ax.plot(c.index, 100 * g, color=Forest, lw=0.9, ls='--', label='GARCH-t VaR 1%')
    ax.set_ylabel('Loss (%)')
    ax.set_ylim(-3, 20)
    ax = axs[1]
    ax.plot(c.index, 100 * c['alpha_t'], color=IDAred, lw=1.0, label=r'ACI level $\alpha_t$')
    ax.axhline(1.0, color='black', ls='--', lw=0.8, label=r'Target $\alpha$ = 1%')
    ax.set_ylabel(r'$\alpha_t$ (%)')
    h1, l1 = axs[0].get_legend_handles_labels()
    h2, l2 = axs[1].get_legend_handles_labels()
    axs[1].legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=3, frameon=False)
    save_fig('ch8_conformal_path')
    cc = c.loc['2020-02-20':'2020-04-30']
    return dict(covid_split=int((cc['L'] > cc['VaR_split']).sum()), covid_aci=int((cc['L'] > cc['VaR_aci']).sum()),
                covid_T=len(cc), covid_inf=int(np.isinf(cc['VaR_aci']).sum()), alpha_min=float(c['alpha_t'].min()))


def fig_conformal_regimes(tab):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    labels, x = [], 0
    for n in M.ASSETS:
        for j, (k, col) in enumerate((('split', MainBlue), ('aci', IDAred), ('garch', Forest))):
            ax.bar(x + j * 0.27 - 0.27, 100 * tab[n][k][1], 0.12, color=col, alpha=0.45,
                   label={'split': 'Split conformal', 'aci': 'ACI', 'garch': 'GARCH-t'}[k] + ', calm' if n == 'sp500' else None)
            ax.bar(x + j * 0.27 - 0.27 + 0.12, 100 * tab[n][k][2], 0.12, color=col,
                   label={'split': 'Split conformal', 'aci': 'ACI', 'garch': 'GARCH-t'}[k] + ', crisis' if n == 'sp500' else None)
        labels.append(M.LABELS[n])
        x += 1
    ax.axhline(5.0, color='black', ls='--', lw=0.8, label='Nominal 5%')
    ax.set_xticks(np.arange(4) - 0.2, labels)
    ax.set_ylabel('Breach rate of VaR 5% (%)')
    legend_outside_bottom(ax, ncol=4, y=-0.13)
    save_fig('ch8_conformal_regimes')


# =============================================================================
# EXEMPLE LUCRATE PENTRU CURS
# =============================================================================
def worked_examples():
    out = {}
    h = hits('sp500', 'GARCH-t').loc['2008']
    out['kupiec_2008'] = dict(M.kupiec(h.values, 0.01), zone=M.traffic_light(int(h.sum()), len(h))[0])
    h = hits('sp500', 'HS').loc['2007':'2010']
    out['chr_hs'] = dict(**M.transitions(h.values), **M.christoffersen(h.values, 0.01))
    h = hits('sp500', 'GARCH-t').loc['2007':'2010']
    out['chr_garch'] = dict(**M.transitions(h.values), **M.christoffersen(h.values, 0.01))
    # FRTB: exceptii la nivel de desk in ultimele 250 de zile
    out['desk'] = {n: {m: dict(x99=int(hits(n, m, 'VaR1').iloc[-250:].sum()),
                                x975=int(hits(n, m, 'VaR2.5').iloc[-250:].sum())) for m in M.MODELS}
                   for n in M.ASSETS}
    out['last_window'] = {n: [str(hits(n, 'HS').index[-250].date()), str(hits(n, 'HS').index[-1].date())]
                          for n in M.ASSETS}
    out['binom250'] = [float(stats.binom.cdf(k, 250, 0.01)) for k in range(0, 11)]
    # parametrii medii ai modelelor
    out['params'] = {n: dict(nu_garch=float(fc(n)[0]['GARCH-t']['nu'].median()),
                             nu_t=float(fc(n)[0]['Student-t']['nu'].median()),
                             xi=float(fc(n)[0]['GARCH-EVT']['xi'].median())) for n in M.ASSETS}
    return out


def to_py(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, str) else '|'.join(map(str, k)) if isinstance(k, tuple) else str(k)): to_py(v)
                for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


if __name__ == '__main__':
    R = {}
    R['assets'] = fig_four_assets()
    R['sp500_var'] = fig_sp500_var()
    R['covid'] = fig_covid_zoom()
    tab = breach_table()
    tab975 = breach_table('VaR2.5', 0.025)
    R['var99'] = tab
    R['var975'] = tab975
    fig_breach_rates(tab)
    R['kupiec_curve'] = fig_kupiec_curve()
    fig_var_pvalues(tab)
    R['timeline'] = fig_breach_timeline()
    R['durations'] = fig_durations(tab)
    R['traffic'] = fig_traffic_light()
    est = es_table()
    R['es'] = est
    fig_es_pvalues(est)
    R['z2_rolling'] = fig_z2_rolling()
    R['mf_resid'] = fig_mf_residuals()
    R['elicit'] = fig_elicitability()
    fz = fz_table()
    R['fz'] = fz
    fig_fz0(fz)
    R['dm_sp500'] = fig_dm_matrix()
    fig_mcs(fz)
    R['conformal'] = conformal_table(0.01)
    R['conformal5'] = conformal_table(0.05)
    R['conf_path'] = fig_conformal_path()
    fig_conformal_regimes(R['conformal5'])
    R['worked'] = worked_examples()
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('done')

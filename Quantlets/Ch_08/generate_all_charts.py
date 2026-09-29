"""
Chart generator for Chapter 8: Backtesting and Evaluating Risk Forecasts
========================================================================
All charts: transparent background, English labels, legend outside at the bottom.
Data: S&P 500, BET and Bitcoin (data/market), EUR/RON (BNR reference rate).
One-day-ahead VaR/ES forecasts on a rolling window (1000 observations): HS, Normal, Student-t,
GARCH-t, FHS, GARCH-EVT; evaluation from 2007 (EUR/RON from 2009, Bitcoin from 2017).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import tempfile
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

# MFM standard style (as in SFM): transparent + English labels + legend at the bottom
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

# Brand colours
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
    """Save the figure as transparent PDF and PNG."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Place the legend outside the plot, bottom centre."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def pv_heatmap(ax, P, fmt='{:.2f}', title=None):
    """Heat map of p-values: red = rejection, green = no rejection (log scale)."""
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
# DATA: forecasts of all models for the four assets
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
# FIG 1: four assets, losses and GARCH-EVT VaR 1%
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
# FIG 2: S&P 500 -- losses, VaR 1% of HS and GARCH-t, breaches
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
# FIG 3: COVID-19 zoom (Feb.-June 2020), all models
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
# FIG 4: VaR 1% breach rates by model and asset
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
# FIG 5: Kupiec statistic as a function of the number of breaches
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
# FIG 6: p-values of the VaR tests (Kupiec, Christoffersen, durations)
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
# FIG 7: breach timeline (S&P 500)
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
# FIG 8: survival function of the durations between breaches
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
# FIG 9: Basel traffic light -- exceptions over 250 days (S&P 500)
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
# ES TESTS: McNeil-Frey, Acerbi-Szekely, Du-Escanciano
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
# FIG: elicitability -- expected quantile (pinball) and FZ0 losses
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
# FZ0 LOSS, DIEBOLD-MARIANO, MCS
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
# CONFORMAL PREDICTION
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
# WORKED EXAMPLES FOR THE LECTURE
# =============================================================================
def worked_examples():
    out = {}
    h = hits('sp500', 'GARCH-t').loc['2008']
    out['kupiec_2008'] = dict(M.kupiec(h.values, 0.01), zone=M.traffic_light(int(h.sum()), len(h))[0])
    h = hits('sp500', 'HS').loc['2007':'2010']
    out['chr_hs'] = dict(**M.transitions(h.values), **M.christoffersen(h.values, 0.01))
    h = hits('sp500', 'GARCH-t').loc['2007':'2010']
    out['chr_garch'] = dict(**M.transitions(h.values), **M.christoffersen(h.values, 0.01))
    # FRTB: desk-level exceptions in the last 250 days
    out['desk'] = {n: {m: dict(x99=int(hits(n, m, 'VaR1').iloc[-250:].sum()),
                                x975=int(hits(n, m, 'VaR2.5').iloc[-250:].sum())) for m in M.MODELS}
                   for n in M.ASSETS}
    out['last_window'] = {n: [str(hits(n, 'HS').index[-250].date()), str(hits(n, 'HS').index[-1].date())]
                          for n in M.ASSETS}
    out['binom250'] = [float(stats.binom.cdf(k, 250, 0.01)) for k in range(0, 11)]
    # average model parameters
    out['params'] = {n: dict(nu_garch=float(fc(n)[0]['GARCH-t']['nu'].median()),
                             nu_t=float(fc(n)[0]['Student-t']['nu'].median()),
                             xi=float(fc(n)[0]['GARCH-EVT']['xi'].median())) for n in M.ASSETS}
    return out


# =============================================================================
# INFERENCE: DQ test, size and power (Monte Carlo), estimation risk,
# Giacomini-White, Nolde-Ziegel zones, Murphy diagram, multinomial test
# =============================================================================
def dq_test(hit, var, a, lags=4):
    """Dynamic Quantile test (Engle & Manganelli, 2004): Hit_t = I_t - a regressed on
    X_t = (1, Hit_{t-1..t-lags}, VaR_t); DQ = b'X'Xb / (a(1-a)) ~ chi2(k)."""
    h = np.asarray(hit, float) - a
    v = np.asarray(var, float)
    y = h[lags:]
    X = np.column_stack([np.ones(len(y))] + [h[lags - j:len(h) - j] for j in range(1, lags + 1)] + [v[lags:]])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    dq = float(b @ X.T @ X @ b / (a * (1 - a)))
    return dict(DQ=dq, df=X.shape[1], p=float(stats.chi2.sf(dq, X.shape[1])))


def dq_table(col='VaR1', a=0.01):
    out = {}
    for n in M.ASSETS:
        for m in M.MODELS:
            df = fc(n)[0][m]
            out[f'{n}|{m}'] = dq_test((df['L'] > df[col]).astype(int).values, df[col].values, a)
    return out


def fig_var_pvalues4(tab, dq):
    """Heat map of p-values: Kupiec, CC, durations and DQ (VaR 1%)."""
    fig, axs = plt.subplots(1, 4, figsize=(8.6, 2.7), sharey=True)
    for ax, (key, title) in zip(axs, (('p_uc', 'Kupiec POF'), ('p_cc', 'Christoffersen CC'),
                                      ('p_dur', 'Duration (Weibull)'), ('dq', 'Dynamic Quantile'))):
        if key == 'dq':
            P = pd.DataFrame({M.LABELS[n]: [dq[f'{n}|{m}']['p'] for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
        else:
            P = pd.DataFrame({M.LABELS[n]: [(tab[f'{n}|{m}'] if f'{n}|{m}' in tab else tab[(n, m)])[key]
                                            for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
        pv_heatmap(ax, P, title=title)
        ax.tick_params(axis='x', rotation=30)
    plt.tight_layout()
    save_fig('ch8_var_pvalues')


def pof_power(T, pis, a=0.01, level=0.05):
    """Exact power of the Kupiec test (LR, 5% level) under Binomial(T, pi) and the local
    noncentral chi2 approximation with parameter T (pi - a)^2 / (a(1-a))."""
    x = np.arange(T + 1)
    lr = np.array([M.kupiec(np.r_[np.ones(k), np.zeros(T - k)], a)['LR'] for k in x])
    rej = lr > stats.chi2.ppf(1 - level, 1)
    exact = np.array([stats.binom.pmf(x, T, p)[rej].sum() for p in pis])
    lam = T * (pis - a) ** 2 / (a * (1 - a))
    asym = stats.ncx2.sf(stats.chi2.ppf(1 - level, 1), 1, np.maximum(lam, 1e-12))
    return exact, asym, rej


def fig_pof_power():
    pis = np.linspace(0.0, 0.04, 401)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    out = {}
    for T, col in ((250, MainBlue), (1000, IDAred)):
        ex, asy, rej = pof_power(T, pis)
        ax.plot(100 * pis, ex, color=col, lw=1.4, label=f'Exact power, T = {T}')
        ax.plot(100 * pis, asy, color=col, lw=1.1, ls='--', label=f'Local asymptotic power, T = {T}')
        up = pis > 0.01
        half = float(pis[up][np.argmax(ex[up] >= 0.5)])
        eighty = float(pis[up][np.argmax(ex[up] >= 0.8)])
        i2 = int(np.argmin(abs(pis - 0.02)))
        out[str(T)] = dict(pi50=half, pi80=eighty, pow2=float(ex[i2]), asy2=float(asy[i2]),
                           size=float(ex[int(np.argmin(abs(pis - 0.01)))]))
    ax.axhline(0.05, color=Gray, lw=0.7, ls=':')
    ax.axvline(1.0, color=Gray, lw=0.7, ls=':')
    ax.set_xlabel('True breach probability (%) of a VaR 1% forecast')
    ax.set_ylabel('Rejection probability at 5%')
    ax.set_ylim(0, 1.02)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch8_pof_power')
    return out


def sim_garch_t(par, n, reps, rng, burn=500):
    """GARCH(1,1)-t paths (standardised t innovations); returns the returns and sigma_t."""
    mu, om, a, b, nu = par
    z = rng.standard_t(nu, size=(reps, n + burn)) * np.sqrt((nu - 2) / nu)
    r = np.empty((reps, n + burn))
    s2 = np.full(reps, om / (1 - a - b))
    S = np.empty((reps, n + burn))
    for t in range(n + burn):
        S[:, t] = np.sqrt(s2)
        r[:, t] = mu + S[:, t] * z[:, t]
        s2 = om + a * (r[:, t] - mu) ** 2 + b * s2
    return r[:, burn:], S[:, burn:]


def mc_size_power(reps=1000, seed=8, Ts=(250, 1000, 5000), a=0.01, w=1000):
    """Monte Carlo: GARCH(1,1)-t DGP with the parameters estimated on the S&P 500, 1990-2026.
    VaR 1% forecasts: correct model (true parameters), Normal-GARCH (true sigma, Normal tail), HS (1000 days).
    Rejection rate at 5% for POF, CC, durations (Weibull) and DQ; undefined p (too few breaches) = no rejection."""
    r = M.load_returns('sp500').values
    par = M.garch_fit(r)
    mu, om, al, be, nu = par
    rng = np.random.default_rng(seed)
    Tmax = max(Ts)
    R, S = sim_garch_t(par, Tmax + w, reps, rng)
    L = -R[:, w:]
    q_t, q_n = M.t_std_q(nu, a), stats.norm.ppf(1 - a)
    out = {}
    for m in ('Correct', 'Normal-GARCH', 'HS'):
        rej = {T: {k: 0 for k in ('POF', 'CC', 'DUR', 'DQ')} for T in Ts}
        nan_dur = {T: 0 for T in Ts}
        for i in range(reps):
            if m == 'Correct':
                v = -mu + S[i, w:] * q_t
            elif m == 'Normal-GARCH':
                v = -mu + S[i, w:] * q_n
            else:
                v = pd.Series(-R[i]).rolling(w).quantile(1 - a).shift(1).values[w:]
            I = (L[i] > v).astype(int)
            for T in Ts:
                h, vv = I[:T], v[:T]
                rej[T]['POF'] += M.kupiec(h, a)['p'] < 0.05
                rej[T]['CC'] += M.christoffersen(h, a)['p_cc'] < 0.05 if h.sum() > 0 else 0
                d = M.duration_test(h)['p']
                nan_dur[T] += np.isnan(d)
                rej[T]['DUR'] += (d < 0.05) if not np.isnan(d) else 0
                rej[T]['DQ'] += dq_test(h, vv, a)['p'] < 0.05
        out[m] = {str(T): dict({k: v / reps for k, v in rej[T].items()}, dur_nan=nan_dur[T] / reps) for T in Ts}
    out['par'] = dict(mu=mu, omega=om, alpha=al, beta=be, nu=nu)
    out['reps'] = reps
    return out


def mc_estimation_risk(reps=400, seed=9, Rw=1000, Ps=(250, 1000, 5000), a=0.01):
    """Estimation risk: GARCH-t estimated once on R = 1000 days (fixed scheme), VaR 1% over P days.
    POF rejection rate at 5% with estimated versus true parameters, on the same paths."""
    r0 = M.load_returns('sp500').values
    par = M.garch_fit(r0)
    rng = np.random.default_rng(seed)
    Pm = max(Ps)
    R, S = sim_garch_t(par, Rw + Pm, reps, rng)
    mu0, _, _, _, nu0 = par
    rej_est = {P: 0 for P in Ps}
    rej_true = {P: 0 for P in Ps}
    rate_est = {P: [] for P in Ps}
    for i in range(reps):
        x = R[i, :Rw]
        mu, om, al, be, nu = M.garch_fit(x)
        nu = max(nu, 2.2)
        s2 = M.garch_filter(R[i], mu, om, al, be, np.var(x[:50]))
        v_est = -mu + np.sqrt(s2[Rw:Rw + Pm]) * M.t_std_q(nu, a)
        v_true = -mu0 + S[i, Rw:] * M.t_std_q(nu0, a)
        L = -R[i, Rw:]
        for P in Ps:
            he = (L[:P] > v_est[:P]).astype(int)
            ht = (L[:P] > v_true[:P]).astype(int)
            rej_est[P] += M.kupiec(he, a)['p'] < 0.05
            rej_true[P] += M.kupiec(ht, a)['p'] < 0.05
            rate_est[P].append(he.mean())
    return {str(P): dict(est=rej_est[P] / reps, true=rej_true[P] / reps,
                         sd_rate=float(np.std(rate_est[P])), sd_binom=float(np.sqrt(a * (1 - a) / P)))
            for P in Ps} | dict(reps=reps)


def gw_test(la, lb):
    """Giacomini-White (2006) test of conditional predictive ability, horizon 1:
    Z_t = h_{t-1} d_t with h_{t-1} = (1, d_{t-1}); W = T Zbar' Omega^{-1} Zbar ~ chi2(2)."""
    d = np.asarray(la) - np.asarray(lb)
    Z = np.column_stack([d[1:], d[:-1] * d[1:]])
    T = len(Z)
    zb = Z.mean(0)
    Om = Z.T @ Z / T
    W = float(T * zb @ np.linalg.solve(Om, zb))
    u = d.mean() / np.sqrt(np.mean(d ** 2) / len(d))
    return dict(W=W, p=float(stats.chi2.sf(W, 2)), unc=float(u), p_unc=float(2 * stats.norm.sf(abs(u))))


def gw_table():
    Lf = fz_losses('sp500')
    return {f'{a}|FHS': gw_test(Lf[a], Lf['FHS']) for a in ('GARCH-t', 'HS', 'GARCH-EVT', 'Normal')}


def nz_zones(standard='HS', internals=('GARCH-t', 'FHS', 'GARCH-EVT'), level=0.05):
    """Three-zone comparative backtesting (Nolde & Ziegel, 2017): two one-sided DM tests on FZ0
    of the internal model against the standard model. Green: internal significantly better; red: significantly worse."""
    z = stats.norm.ppf(1 - level)
    out = {}
    for n in M.ASSETS:
        Lf = fz_losses(n)
        for m in internals:
            dm = M.diebold_mariano(Lf[m], Lf[standard])['DM']
            out[f'{n}|{m}'] = dict(DM=float(dm), zone='green' if dm < -z else ('red' if dm > z else 'yellow'))
    return out


def elementary_scores(L, v, thetas, tau):
    """Elementary scores for the quantile of order tau (Ehm et al., 2016):
    S_theta(v, y) = (1{y < v} - tau)(1{theta < v} - 1{theta < y}); matrix T x len(thetas)."""
    L = np.asarray(L)[:, None]
    v = np.asarray(v)[:, None]
    th = np.asarray(thetas)[None, :]
    return ((L < v) - tau) * ((th < v).astype(float) - (th < L).astype(float))


def murphy(name, mA, mB, col='VaR1', a=0.01, n=240):
    F = fc(name)[0]
    L = F[mA]['L'].values
    lo, hi = np.nanquantile(np.r_[F[mA][col], F[mB][col]], [0.01, 0.99])   # range covered by the forecasts
    th = np.linspace(0.8 * lo, hi, n)
    SA = elementary_scores(L, F[mA][col].values, th, 1 - a)
    SB = elementary_scores(L, F[mB][col].values, th, 1 - a)
    D = SA - SB
    se = np.array([np.sqrt(M.nw_var(D[:, j]) / len(D)) for j in range(n)])
    return th, SA.mean(0), SB.mean(0), D.mean(0), se


def fig_murphy(name='sp500', mA='GARCH-t', mB='FHS'):
    th, a_, b_, d, se = murphy(name, mA, mB)
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.8))
    axs[0].plot(100 * th, 1e4 * a_, color=MCOL[mA], lw=1.3, label=mA)
    axs[0].plot(100 * th, 1e4 * b_, color=MCOL[mB], lw=1.3, label=mB)
    axs[0].set_xlabel('Threshold θ (daily loss, %)')
    axs[0].set_ylabel('Mean elementary score (×10⁴)')
    axs[0].set_title('Murphy diagram, VaR 1%, S&P 500', fontsize=9)
    axs[1].fill_between(100 * th, 1e4 * (d - 1.96 * se), 1e4 * (d + 1.96 * se), color=LightGray, alpha=0.8,
                        label='95% pointwise band (HAC)')
    axs[1].plot(100 * th, 1e4 * d, color=Purple, lw=1.3, label=f'{mA} minus {mB}')
    axs[1].axhline(0, color=Gray, lw=0.7)
    axs[1].set_xlabel('Threshold θ (daily loss, %)')
    axs[1].set_ylabel('Score difference (×10⁴)')
    axs[1].set_title('Difference: above 0 means FHS better', fontsize=9)
    h0, l0 = axs[0].get_legend_handles_labels()
    h1, l1 = axs[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False)
    plt.tight_layout()
    save_fig('ch8_murphy')
    sig_pos = (d - 1.96 * se) > 0
    sig_neg = (d + 1.96 * se) < 0
    lo5 = th < 0.05
    return dict(neg_ge5=float(np.mean(d[~lo5] < 0)), zero_lt5=float(np.mean(~sig_pos[lo5] & ~sig_neg[lo5])), share_pos_lt5=float(np.mean(d[lo5] > 0)),
                share_pos=float(np.mean(d > 0)), share_sig_pos=float(np.mean(sig_pos)),
                share_sig_neg=float(np.mean(sig_neg)), share_neg=float(np.mean(d < 0)),
                th_min=float(th[0]), th_max=float(th[-1]),
                th_sig_lo=float(th[sig_pos].min()) if sig_pos.any() else None,
                th_sig_hi=float(th[sig_pos].max()) if sig_pos.any() else None)


def murphy_summary(name, mA, mB, col, a):
    th, a_, b_, d, se = murphy(name, mA, mB, col, a)
    return dict(share_pos=float(np.mean(d > 0)), share_neg=float(np.mean(d < 0)),
                share_sig_pos=float(np.mean((d - 1.96 * se) > 0)), share_sig_neg=float(np.mean((d + 1.96 * se) < 0)),
                crosses=bool((d > 0).any() and (d < 0).any()))


def multinomial_table(N=4, a=0.025):
    """Multinomial VaR test (Kratz, Lok & McNeil, 2018), Pearson statistic, N = 4 tail levels
    a_j = a (1 - (j-1)/N): 2.5%, 1.875%, 1.25%, 0.625%; cells are defined through the PIT."""
    lev = np.array([1 - a * (1 - j / N) for j in range(N)])      # 0.975, 0.98125, 0.9875, 0.99375
    probs = np.diff(np.r_[0.0, lev, 1.0])
    out = {}
    for n in M.ASSETS:
        for m in M.MODELS:
            u = fc(n)[0][m]['pit'].values
            cell = np.sum(u[:, None] > lev[None, :], axis=1)
            O = np.bincount(cell, minlength=N + 1)
            E = len(u) * probs
            S = float(((O - E) ** 2 / E).sum())
            out[f'{n}|{m}'] = dict(S=S, p=float(stats.chi2.sf(S, N)), O=O.tolist())
    out['probs'] = probs.tolist()
    return out


def extras(R):
    """Inference blocks of the lecture (DQ, power, estimation risk, GW, Nolde-Ziegel, Murphy, multinomial)."""
    R['dq'] = dq_table()
    fig_var_pvalues4(R['var99'], R['dq'])
    R['pof_power'] = fig_pof_power()
    R['gw'] = gw_table()
    R['nz'] = nz_zones()
    R['murphy'] = fig_murphy()
    R['murphy_btc'] = murphy_summary('btc', 'HS', 'GARCH-EVT', 'VaR2.5', 0.025)
    R['multinomial'] = multinomial_table()
    R['mc'] = mc_size_power()
    R['estrisk'] = mc_estimation_risk()
    return R


# =============================================================================
# CASE STUDY: Bayer & Dimitriadis (2022), regression-based ES backtesting
# =============================================================================
# Table 3 of the paper (accepted version, arXiv:1801.04112v2): share of the 200 largest S&P 500 stocks for which
# the one-sided Intercept ESR test rejects the ES 2.5% forecasts at 5%; out-of-sample Jan 2010 - Aug 2019.
BD_WINDOWS = (250, 500, 1000, 1500, 2000)
BD_REFITS = (5, 21, 62, 125, 250)
BD_TABLE3 = {
    'GARCH-N': [[1.00, 1.00, 1.00, 1.00, 1.00], [0.99, 0.99, 0.99, 0.99, 0.99], [0.98, 0.97, 0.98, 0.96, 0.96],
                [0.97, 0.97, 0.97, 0.97, 0.96], [0.96, 0.96, 0.94, 0.95, 0.94]],
    'GJR-GARCH-N': [[1.00, 1.00, 1.00, 1.00, 1.00], [1.00, 1.00, 1.00, 0.99, 1.00], [0.99, 0.99, 0.99, 0.99, 0.99],
                    [0.98, 0.99, 0.99, 0.99, 0.99], [0.98, 0.98, 0.98, 0.98, 0.97]],
    'GARCH-t': [[0.26, 0.32, 0.32, 0.36, 0.59], [0.10, 0.09, 0.12, 0.12, 0.20], [0.07, 0.07, 0.07, 0.08, 0.09],
                [0.09, 0.09, 0.09, 0.10, 0.09], [0.10, 0.08, 0.08, 0.08, 0.09]],
    'GJR-GARCH-t': [[0.28, 0.32, 0.29, 0.37, 0.42], [0.13, 0.17, 0.17, 0.22, 0.25], [0.14, 0.11, 0.11, 0.12, 0.14],
                    [0.08, 0.10, 0.09, 0.09, 0.09], [0.09, 0.09, 0.10, 0.09, 0.10]],
}
# large S&P 500 stocks in data/market with daily prices from 2002 (2000-day window before January 2010)
BD_STOCKS = ['AAPL.US', 'MSFT.US', 'AMZN.US', 'NVDA.US', 'CSCO.US', 'JPM.US', 'BAC.US', 'C.US', 'WFC.US', 'GS.US',
             'MS.US']
BD_OOS = ('2010-01-01', '2019-08-31')
BD_TAU = 0.025


ESBACK_R = r"""
lib <- Sys.getenv('MFM_RLIB'); dir.create(lib, showWarnings = FALSE, recursive = TRUE); .libPaths(c(lib, .libPaths()))
if (!requireNamespace('esback', quietly = TRUE))
  install.packages('esback', lib = lib, repos = 'https://cloud.r-project.org', quiet = TRUE)
args <- commandArgs(trailingOnly = TRUE)
d <- read.csv(args[1]); tau <- as.numeric(args[3])
RNGkind("L'Ecuyer-CMRG"); set.seed(8)
p <- parallel::mclapply(split(d, d$id), function(s) {
  b <- suppressWarnings(esback::esr_backtest(r = s$r, e = s$e, alpha = tau, version = 3))
  data.frame(id = s$id[1], p = b$pvalue_onesided_asymptotic, p2 = b$pvalue_twosided_asymptotic)
}, mc.cores = max(1, parallel::detectCores() - 1))
write.csv(do.call(rbind, p), args[2], row.names = FALSE)
"""


def esr_intercept(series, tau=BD_TAU):
    """One-sided Intercept ESR test of Bayer-Dimitriadis (Eq. 2.14-2.15) with the authors' R package esback:
    joint regression of r_t - e_t on (1, e_t) for the quantile and on a constant for the ES, FZ0-type loss
    (esreg, G1 = 2, G2 = 1), misspecification-robust covariance (sparsity 'nid', 'scl_sp'); H0: gamma_1 >= 0.
    series: dict id -> DataFrame with columns r (return) and e (ES forecast, return units). Needs R (Rscript)."""
    import subprocess
    tmp = tempfile.mkdtemp()
    d = pd.concat([df.assign(id=k)[['id', 'r', 'e']] for k, df in series.items()])
    d.to_csv(os.path.join(tmp, 'in.csv'), index=False)
    with open(os.path.join(tmp, 'esback.R'), 'w') as f:
        f.write(ESBACK_R)
    env = dict(os.environ, MFM_RLIB=os.path.join(tempfile.gettempdir(), 'mfm_rlib'))
    subprocess.run(['Rscript', os.path.join(tmp, 'esback.R'), os.path.join(tmp, 'in.csv'),
                    os.path.join(tmp, 'out.csv'), str(tau)], check=True, env=env)
    return pd.read_csv(os.path.join(tmp, 'out.csv')).set_index('id')


def garch_es_forecasts(r, dist, w, refit, oos):
    """Rolling one-day-ahead ES_tau forecasts (return units, negative) of a constant-mean GARCH(1,1) with Normal
    or Student-t innovations: window of w days, parameters re-estimated every `refit` days, volatility updated
    daily with the last parameters. r: log returns in percent (Series); oos: (start, end)."""
    from arch import arch_model
    idx = np.where((r.index >= oos[0]) & (r.index <= oos[1]))[0]
    x = r.values
    e = np.full(len(idx), np.nan)
    for j0 in range(0, len(idx), refit):
        s = idx[j0]
        res = arch_model(x[s - w:s], mean='Constant', vol='GARCH', p=1, q=1,
                         dist='t' if dist == 't' else 'normal').fit(disp='off', show_warning=False)
        mu, om, al, be = (res.params[k] for k in ('mu', 'omega', 'alpha[1]', 'beta[1]'))
        esz = (M.t_std_es(res.params['nu'], BD_TAU) if dist == 't'
               else stats.norm.pdf(stats.norm.ppf(BD_TAU)) / BD_TAU)
        s2 = res.conditional_volatility[-1] ** 2
        eps = x[s - 1] - mu
        for j in range(j0, min(j0 + refit, len(idx))):
            s2 = om + al * eps ** 2 + be * s2
            e[j] = mu - np.sqrt(s2) * esz
            eps = x[idx[j]] - mu
    return pd.Series(e, index=r.index[idx])


def _bd_one(sym, dist, w, refit):
    r = 100 * np.log(M.read_market(sym)['adjusted_close']).diff().dropna()
    e = garch_es_forecasts(r, dist, w, refit, BD_OOS)
    return f'{sym}|{dist}|{w}|{refit}', pd.DataFrame({'r': r.loc[e.index].values, 'e': e.values})


def bd_replication(n_jobs=-1):
    """Table 3 design on the course data: GARCH(1,1)-N and GARCH(1,1)-t, five windows x five refit frequencies,
    one-sided Intercept ESR at 5%; share of the stocks rejected."""
    from joblib import Parallel, delayed
    jobs = [(s, d, w, k) for s in BD_STOCKS for d in ('normal', 't') for w in BD_WINDOWS for k in BD_REFITS]
    series = dict(Parallel(n_jobs=n_jobs)(delayed(_bd_one)(*j) for j in jobs))
    pv = esr_intercept(series)
    rows = pd.DataFrame([dict(zip(('sym', 'dist', 'w', 'refit'), k.split('|')), T=len(series[k]),
                              p=pv.loc[k, 'p'], p2=pv.loc[k, 'p2']) for k in series])
    rows[['w', 'refit']] = rows[['w', 'refit']].astype(int)
    rows['reject'] = rows['p'] < 0.05
    share = {d: rows[rows.dist == d].pivot_table(index='w', columns='refit', values='reject', aggfunc='mean')
             for d in ('normal', 't')}
    return rows, share


def fig_bd_table3():
    """Table 3 of Bayer-Dimitriadis: rejection shares by estimation window, weekly and yearly refit."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    x = np.arange(len(BD_WINDOWS))
    for ax, fam in zip(axs, ('GARCH', 'GJR-GARCH')):
        for d, col in (('N', IDAred), ('t', MainBlue)):
            tab = np.array(BD_TABLE3[f'{fam}-{d}'])
            lab = 'Normal' if d == 'N' else 'Student-t'
            ax.plot(x, tab[:, 0], '-o', color=col, ms=4, label=f'{lab} innovations, weekly refit (5 days)')
            ax.plot(x, tab[:, 4], '--s', color=col, ms=4, label=f'{lab} innovations, yearly refit (250 days)')
        ax.axhline(0.05, color=Gray, lw=0.8, ls=':', label='Nominal size 5%')
        ax.set_xticks(x, [str(v) for v in BD_WINDOWS])
        ax.set_xlabel('Rolling estimation window (days)')
        ax.set_title(f'{fam}(1,1)', fontsize=10)
        ax.set_ylim(0, 1.05)
    axs[0].set_ylabel('Share of stocks rejected')
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch8_bd_table3')


def fig_bd_replication(rows, share):
    """Course-data replication of Table 3 (GARCH(1,1)): share of stocks rejected, Normal versus Student-t."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    x = np.arange(len(BD_WINDOWS))
    paperN, papert = np.array(BD_TABLE3['GARCH-N']), np.array(BD_TABLE3['GARCH-t'])
    for ax, k, ttl in zip(axs, (0, 4), ('Weekly refit (5 days)', 'Yearly refit (250 days)')):
        ref = BD_REFITS[k]
        ax.plot(x, share['normal'][ref].values, '-o', color=IDAred, ms=4,
                label=f'Normal innovations, {len(BD_STOCKS)} stocks (course data)')
        ax.plot(x, share['t'][ref].values, '-o', color=MainBlue, ms=4,
                label=f'Student-t innovations, {len(BD_STOCKS)} stocks (course data)')
        ax.plot(x, paperN[:, k], '--s', color=Orange, ms=3.5, label='Normal innovations, 200 stocks (Table 3)')
        ax.plot(x, papert[:, k], '--s', color=Teal, ms=3.5, label='Student-t innovations, 200 stocks (Table 3)')
        ax.axhline(0.05, color=Gray, lw=0.8, ls=':', label='Nominal size 5%')
        ax.set_xticks(x, [str(v) for v in BD_WINDOWS])
        ax.set_xlabel('Rolling estimation window (days)')
        ax.set_title(ttl, fontsize=10)
        ax.set_ylim(-0.03, 1.05)
    axs[0].set_ylabel('Share of stocks rejected')
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch8_bd_replication')
    t = rows[rows.dist == 't']
    n = rows[rows.dist == 'normal']
    return dict(T=int(rows['T'].iloc[0]), n_stocks=len(BD_STOCKS),
                share_n={str(w): {str(k): float(share['normal'].loc[w, k]) for k in BD_REFITS} for w in BD_WINDOWS},
                share_t={str(w): {str(k): float(share['t'].loc[w, k]) for k in BD_REFITS} for w in BD_WINDOWS},
                n_min=float(share['normal'].values.min()), n_max=float(share['normal'].values.max()),
                t_min=float(share['t'].values.min()), t_max=float(share['t'].values.max()),
                p_n_median=float(n['p'].median()), p_t_median=float(t['p'].median()),
                t_250_250=float(share['t'].loc[250, 250]),
                t_long=float(share['t'].loc[[1500, 2000], [5, 21, 62]].values.mean()),
                t_long_max=float(share['t'].loc[[1500, 2000], [5, 21, 62]].values.max()))


def case_study(R):
    """Case study (Bayer-Dimitriadis, 2022): Table 3 chart and its replication on the course data."""
    fig_bd_table3()
    rows, share = bd_replication()
    R['bd'] = fig_bd_replication(rows, share)
    return R


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


if __name__ == '__main__' and '--case' in sys.argv:
    # only the case study block, added to the existing results
    R = json.load(open(os.path.join(HERE, 'ch8_results.json')))
    case_study(R)
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('case study done')
elif __name__ == '__main__' and '--extras' in sys.argv:
    # only the inference blocks, added to the existing results
    R = json.load(open(os.path.join(HERE, 'ch8_results.json')))
    extras(R)
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('extras done')
elif __name__ == '__main__':
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
    extras(R)
    case_study(R)
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('done')

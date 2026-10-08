"""
Generator pentru graficele din Capitolul 14: Deep learning si modele fundationale pentru serii de timp
===================================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date: S&P 500, Bitcoin, BET (randamente zilnice) si varianta realizata a SPY (date la 5 minute).
Prognozele la o zi sunt produse de run_forecasts.py (ch14_*.csv); aici se evalueaza si se deseneaza.
Rezultat numeric: ch14_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
import mfm_tsfm as M   # noqa: E402

# Standard MFM style: transparent, English labels, legend at the bottom
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.1
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

# Brand colours
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Orange = '#E67E22'
Purple = '#8E44AD'
Crimson = '#DC3545'
Teal = '#17A2B8'
Magenta = '#D63384'
Brown = '#795548'
Navy     = '#1F2A44'   # reference lines (no grey in charts)
BandBlue = '#C5D2E8'   # light MainBlue tint for confidence / reference bands
Gray, LightGray = Navy, BandBlue   # legacy names kept for importing scripts
PV_CMAP = LinearSegmentedColormap.from_list('pv', [IDAred, '#F4B6B6', '#FFFFFF', '#BFD8BF', Forest])

RET_MODELS = {'hist': 'Historical mean', 'ar1': 'AR(1)', 'lstm': 'LSTM (5 seeds)',
              'chronos2_point': 'Chronos-2', 'bolt_point': 'Chronos-Bolt', 'timesfm_point': 'TimesFM-2.5'}
RET_COL = {'hist': Amber, 'ar1': Purple, 'lstm': Forest, 'chronos2_point': IDAred, 'bolt_point': Orange,
           'timesfm_point': MainBlue}
RV_MODELS = ['RW', 'HAR', 'logHAR', 'GARCH-t', 'LSTM', 'Chronos-2', 'Chronos-Bolt', 'TimesFM-2.5']
RV_LBL = {'RW': 'Random walk', 'HAR': 'HAR', 'logHAR': 'log-HAR', 'GARCH-t': 'GARCH-t', 'LSTM': 'LSTM',
          'Chronos-2': 'Chronos-2', 'Chronos-Bolt': 'Chronos-Bolt', 'TimesFM-2.5': 'TimesFM-2.5'}
RV_COL = {'RW': Amber, 'HAR': Brown, 'logHAR': Purple, 'GARCH-t': Magenta, 'LSTM': Forest, 'Chronos-2': IDAred,
          'Chronos-Bolt': Orange, 'TimesFM-2.5': MainBlue}
RISK_MODELS = ['HS', 'GARCH-t', 'FHS', 'C2-raw', 'C2-FHS', 'TFM-FHS']
RISK_LBL = {'HS': 'HS', 'GARCH-t': 'GARCH-t', 'FHS': 'FHS', 'C2-raw': 'Chronos-2 quantiles',
            'C2-FHS': 'FHS + Chronos-2 volatility', 'TFM-FHS': 'FHS + TimesFM volatility',
            'bolt-raw': 'Chronos-Bolt quantiles', 'timesfm-raw': 'TimesFM quantiles'}
RISK_COL = {'HS': Teal, 'GARCH-t': MainBlue, 'FHS': Forest, 'C2-raw': IDAred, 'C2-FHS': Orange,
            'TFM-FHS': Purple, 'bolt-raw': Amber, 'timesfm-raw': Magenta}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
RES = {}


def save_fig(name):
    """Save the figure as transparent PDF and PNG."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f'   saved {name}')


def legend_outside_bottom(ax, ncol=2, y=-0.22, **kw):
    """Place the legend outside the plot, bottom centre."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False, **kw)


def fig_legend_bottom(fig, handles, labels, ncol=3, y=0.0):
    """One legend for the whole figure, below the panels."""
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def load_csv(name):
    return pd.read_csv(os.path.join(HERE, name), index_col=0, parse_dates=True)


# =============================================================================
# FIG 1: vanishing gradient (RNN vs LSTM) by automatic differentiation
# =============================================================================
def fig_vanishing(T=150, H=16, seeds=50):
    import torch
    import torch.nn as nn

    def grads(kind, seed, fb=None):
        torch.manual_seed(seed)
        net = nn.RNN(1, H, nonlinearity='tanh', batch_first=True) if kind == 'rnn' else nn.LSTM(1, H, batch_first=True)
        if fb is not None:
            with torch.no_grad():
                net.bias_ih_l0[H:2 * H].fill_(fb)
                net.bias_hh_l0[H:2 * H].fill_(0.0)
        x = torch.randn(1, T, 1, requires_grad=True)
        h, _ = net(x)
        h[0, -1].sum().backward()
        return x.grad[0, :, 0].abs().numpy()[::-1]
    cases = [('rnn', None, 'Simple RNN (tanh)', MainBlue), ('lstm', 0.0, 'LSTM, forget-gate bias 0', Orange),
             ('lstm', 3.0, 'LSTM, forget-gate bias 3', IDAred)]
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    out = {}
    k = np.arange(T)
    for kind, fb, lab, col in cases:
        G = np.mean([grads(kind, s, fb) for s in range(seeds)], axis=0)
        G = G / G[0]
        ax.semilogy(k[1:101], G[1:101], color=col, label=lab)
        out[f'{kind}_{fb}'] = {str(j): float(G[j]) for j in (1, 5, 10, 20, 50, 100)}
    ax.set_xlabel('Lag $k$ (steps back from the last input)')
    ax.set_ylabel(r'$|\partial h_T / \partial x_{T-k}|$, relative to $k=0$')
    legend_outside_bottom(ax, ncol=3, y=-0.24)
    save_fig('ch14_vanishing_gradient')
    RES['vanish'] = out


# =============================================================================
# FIG 2: autocorrelation of returns and absolute returns (why volatility is forecastable)
# =============================================================================
def fig_acf():
    r = M.load_returns('sp500')
    x = r.loc['2000':].values
    lags = np.arange(1, 51)

    def acf(v, L):
        v = v - v.mean()
        return np.array([np.sum(v[l:] * v[:-l]) / np.sum(v * v) for l in L])
    a_r, a_abs = acf(x, lags), acf(np.abs(x), lags)
    band = 1.96 / np.sqrt(len(x))
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.axhspan(-band, band, color=LightGray, alpha=0.8, lw=0, label='95% band under i.i.d.')
    ax.bar(lags - 0.2, a_r, 0.4, color=MainBlue, label='Returns $r_t$')
    ax.bar(lags + 0.2, a_abs, 0.4, color=IDAred, label='Absolute returns $|r_t|$')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag (trading days)')
    ax.set_ylabel('Autocorrelation')
    legend_outside_bottom(ax, ncol=3, y=-0.24)
    save_fig('ch14_acf_signal')
    RES['acf'] = dict(r1=float(a_r[0]), abs1=float(a_abs[0]), abs20=float(a_abs[19]), abs50=float(a_abs[49]),
                      band=float(band), n=int(len(x)), start=str(r.loc['2000':].index[0].date()),
                      n_sig_r=int(np.sum(np.abs(a_r) > band)), n_sig_abs=int(np.sum(np.abs(a_abs) > band)))


# =============================================================================
# FIG 3: Chronos tokenisation (mean-absolute scaling + uniform quantisation)
# =============================================================================
def fig_tokenization():
    r = M.load_returns('sp500')
    ctx = r.values[-512:]
    s = np.mean(np.abs(ctx))
    z = ctx / s
    delta = 30 / 4092                           # 4093 equally spaced centres in [-15, 15] (Chronos: MeanScaleUniformBins)
    tok = np.round((np.clip(z, -15, 15) + 15) / delta).astype(int)
    used = len(np.unique(tok))
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.5, 1]})
    ax = axes[0]
    ax.plot(r.index[-512:], z, color=MainBlue, lw=0.6, label=r'Scaled return $r_t / s$')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel(r'$r_t / s$')
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.tick_params(axis='x', labelsize=7, rotation=30)
    ax.set_title('Context: last 512 S&P 500 returns', fontsize=9, loc='left')
    ax = axes[1]
    ax.hist(z, bins=np.linspace(-15, 15, 121), color=IDAred, label='Scaled values in the context')
    ax.axvspan(-15, 15, color=LightGray, alpha=0.3, lw=0, label='Range of the 4,093 bins')
    ax.set_xlim(-16, 16)
    ax.set_xlabel(r'$r_t / s$')
    ax.set_ylabel('Count')
    ax.set_title('Where the tokens fall', fontsize=9, loc='left')
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    fig.tight_layout()
    fig_legend_bottom(fig, h1 + h2, l1 + l2, ncol=3, y=0.02)
    save_fig('ch14_tokenization')
    RES['tok'] = dict(scale=float(s), used=int(used), zmin=float(z.min()), zmax=float(z.max()),
                      share_inside1=float(np.mean(np.abs(z) <= 1)), width=float(delta),
                      share_inside3=float(np.mean(np.abs(z) <= 3)), bins_pm3=int(round(6 / delta)))


# =============================================================================
# FIG 4: patching the context (Chronos-2: 16 days, TimesFM-2.5: 32 days)
# =============================================================================
def fig_patching():
    r = M.load_returns('sp500')
    ctx = r.values[-512:]
    t = np.arange(-512, 0)
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 3.3), sharex=True)
    for ax, P, name in ((axes[0], 16, 'Chronos-2: 32 patches of 16 days'),
                        (axes[1], 32, 'TimesFM-2.5: 16 patches of 32 days')):
        for j in range(512 // P):
            ax.axvspan(-512 + j * P, -512 + (j + 1) * P, color=(Teal if j % 2 == 0 else Amber), alpha=0.18, lw=0)
        ax.plot(t, ctx, color=MainBlue, lw=0.6)
        ax.set_title(name, fontsize=9, loc='left')
        ax.set_ylabel('Return (%)')
    axes[1].set_xlabel('Day relative to the forecast origin')
    from matplotlib.patches import Patch
    h = [plt.Line2D([], [], color=MainBlue, lw=0.8), Patch(color=Teal, alpha=0.3), Patch(color=Amber, alpha=0.3)]
    fig.tight_layout()
    fig_legend_bottom(fig, h, ['S&P 500 daily return (context of 512 days)', 'Patch (even)', 'Patch (odd)'],
                      ncol=3, y=0.02)
    save_fig('ch14_patching')


# =============================================================================
# FIG 5: Chronos-2 fan chart for log RV (22 days) from the last day of the sample
# =============================================================================
def fig_fan():
    rv = M.load_rv()
    lx = np.log(rv.values)
    import torch
    m = M.load_fm('chronos2')
    q, _ = m.predict_quantiles([torch.tensor(lx[-512:], dtype=torch.float32)[None, :]], prediction_length=22,
                               quantile_levels=M.C2_LEVELS)
    Q = q[0][0].numpy()                         # 22 x 21
    ann = lambda v: np.sqrt(252 * np.exp(v))    # annualised volatility (%) from daily log RV
    hist = rv.iloc[-120:]
    fut = pd.bdate_range(rv.index[-1] + pd.Timedelta(days=1), periods=22)
    lv = M.C2_LEVELS
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(hist.index, np.sqrt(252 * hist.values), color=MainBlue, lw=0.9, label='SPY realised volatility (annualised)')
    ax.fill_between(fut, ann(Q[:, lv.index(0.05)]), ann(Q[:, lv.index(0.95)]), color=IDAred, alpha=0.15, lw=0,
                    label='Chronos-2: 5%-95% band')
    ax.fill_between(fut, ann(Q[:, lv.index(0.25)]), ann(Q[:, lv.index(0.75)]), color=IDAred, alpha=0.30, lw=0,
                    label='Chronos-2: 25%-75% band')
    ax.plot(fut, ann(Q[:, lv.index(0.5)]), color=IDAred, lw=1.1, label='Chronos-2: median')
    ax.set_ylabel('Volatility (% p.a.)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch14_fan_chart')
    RES['fan'] = dict(last=str(rv.index[-1].date()), last_vol=float(np.sqrt(252 * rv.values[-1])),
                      mean20=float(np.sqrt(252 * rv.values[-20:].mean())),
                      med22=float(ann(Q[-1, lv.index(0.5)])), lo22=float(ann(Q[-1, lv.index(0.05)])),
                      hi22=float(ann(Q[-1, lv.index(0.95)])))


# =============================================================================
# EVALUATION: returns (point forecasts)
# =============================================================================
def eval_returns():
    out, series = {}, {}
    for a in M.ASSETS:
        d = load_csv(f'ch14_returns_{a}.csv')
        y = d['y'].values
        post = d.index >= M.POST_FROM
        res = {'n': int(len(d)), 'start': str(d.index[0].date()), 'end': str(d.index[-1].date()),
               'n_post': int(post.sum()), 'sd': float(y.std())}
        for k in RET_MODELS:
            f = d[k].values
            e0, e1 = y ** 2, (y - f) ** 2
            lo, hi = M.block_bootstrap_ci(lambda yy, ff: M.r2_oos(yy, ff), [y, f], B=1000)
            dm = M.diebold_mariano(e1, e0)
            st = M.sign_test(y, f)
            res[k] = dict(r2=100 * M.r2_oos(y, f), lo=100 * lo, hi=100 * hi, dm=dm['DM'], p=dm['p'],
                          hit=100 * st['rate'], hit_p=st['p'], r2_post=100 * M.r2_oos(y[post], f[post]),
                          sd_f=float(f.std()))
        res['lstm_seeds'] = [100 * M.r2_oos(y, d[f'lstm_s{s}'].values) for s in range(5)]
        out[a] = res
        series[a] = d
    RES['ret'] = out
    return series


def fig_return_r2(series):
    R = RES['ret']
    keys = list(RET_MODELS)
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    w = 0.13
    x = np.arange(len(M.ASSETS))
    for j, k in enumerate(keys):
        v = np.array([R[a][k]['r2'] for a in M.ASSETS])
        lo = np.array([R[a][k]['lo'] for a in M.ASSETS])
        hi = np.array([R[a][k]['hi'] for a in M.ASSETS])
        ax.bar(x + (j - 2.5) * w, v, w, color=RET_COL[k], label=RET_MODELS[k])
        ax.errorbar(x + (j - 2.5) * w, v, yerr=[v - lo, hi - v], fmt='none', ecolor='black', lw=0.6, capsize=1.5)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(x, [M.LABELS[a] for a in M.ASSETS])
    ax.set_ylabel(r'Out-of-sample $R^2$ vs zero forecast (%)')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    save_fig('ch14_return_r2')


def fig_cum_sse(series):
    d = series['sp500']
    y = d['y'].values
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    for k in RET_MODELS:
        c = np.cumsum(y ** 2 - (y - d[k].values) ** 2)
        ax.plot(d.index, c, color=RET_COL[k], lw=0.9, label=RET_MODELS[k])
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_ylabel('Cumulative SSE(zero) - SSE(model)')
    legend_outside_bottom(ax, ncol=3, y=-0.12)
    save_fig('ch14_cum_sse')


def fig_lstm_training():
    h = load_csv('ch14_lstm_hist_sp500_s0.csv').reset_index(drop=True)
    best = int(h['val'].idxmin())
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.plot(h.index + 1, h['train'], color=MainBlue, label='Training MSE')
    ax.plot(h.index + 1, h['val'], color=IDAred, label='Validation MSE (last 20% of the training period)')
    ax.axvline(best + 1, color=Gray, ls='--', lw=0.7, label='Selected epoch (early stopping)')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('MSE (standardised returns)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch14_lstm_training')
    RES['lstm_train'] = dict(epochs=int(len(h)), best=best + 1, train_best=float(h['train'][best]),
                             val_best=float(h['val'][best]), val_first=float(h['val'][0]))


def fig_lstm_seeds():
    R = RES['ret']
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    for i, a in enumerate(M.ASSETS):
        s = R[a]['lstm_seeds']
        ax.scatter(np.full(5, i) + np.linspace(-0.12, 0.12, 5), s, color=Forest, s=18, zorder=3,
                   label='Single seed' if i == 0 else None)
        ax.scatter([i], [R[a]['lstm']['r2']], color=IDAred, marker='D', s=30, zorder=4,
                   label='Average of the 5 seeds' if i == 0 else None)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(range(3), [M.LABELS[a] for a in M.ASSETS])
    ax.set_ylabel(r'Out-of-sample $R^2$ (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch14_lstm_seeds')


# =============================================================================
# EVALUATION: realised volatility (SPY)
# =============================================================================
def eval_rv():
    d = load_csv('ch14_rv.csv')
    post = d.index >= M.POST_FROM
    L = pd.DataFrame({m: M.qlike(d['RV'], d[m]) for m in RV_MODELS})
    E = pd.DataFrame({m: (d['RV'] - d[m]) ** 2 for m in RV_MODELS})
    p_mcs = M.mcs(L)
    out = {'n': int(len(d)), 'start': str(d.index[0].date()), 'end': str(d.index[-1].date()),
           'n_post': int(post.sum()), 'rv_mean': float(d['RV'].mean()),
           'vol_mean': float(np.sqrt(252 * d['RV'].mean()))}
    for m in RV_MODELS:
        dm = M.diebold_mariano(L[m], L['logHAR']) if m != 'logHAR' else dict(DM=np.nan, p=np.nan)
        dmp = M.diebold_mariano(L[m][post], L['logHAR'][post]) if m != 'logHAR' else dict(DM=np.nan, p=np.nan)
        out[m] = dict(qlike=float(L[m].mean()), mse=float(E[m].mean()), dm=float(dm['DM']), p=float(dm['p']),
                      mcs=float(p_mcs[m]), qlike_post=float(L[m][post].mean()), dm_post=float(dmp['DM']),
                      p_post=float(dmp['p']), ratio=float(d[m].mean() / d['RV'].mean()))
    for m in ('Chronos-2', 'TimesFM-2.5'):
        lm = M.qlike(d['RV'], d[m + '|median'])
        out[m + '|median'] = dict(qlike=float(lm.mean()), ratio=float(d[m + '|median'].mean() / d['RV'].mean()),
                                  dm_vs_mean=float(M.diebold_mariano(lm, L[m])['DM']))
    c = load_csv('ch14_ctx.csv')
    out['ctx'] = {k: float(M.qlike(c['RV'], c[k]).mean()) for k in c.columns[1:]}
    p_post = M.mcs(L[post])
    for m in RV_MODELS:
        out[m]['mcs_post'] = float(p_post[m])
    RES['rv'] = out
    return d, L


def fig_rv_path(d):
    s = d.loc['2025-02-01':'2025-07-31']
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(s.index, np.sqrt(252 * s['RV']), color=Teal, lw=1.2, label='Realised volatility (target)')
    for m in ('logHAR', 'GARCH-t', 'Chronos-2', 'TimesFM-2.5'):
        ax.plot(s.index, np.sqrt(252 * s[m]), color=RV_COL[m], lw=0.9, label=RV_LBL[m] + ' forecast')
    ax.set_ylabel('Volatility (% p.a.)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch14_rv_forecasts')
    RES['rv_path'] = dict(peak_day=str(s['RV'].idxmax().date()), peak_vol=float(np.sqrt(252 * s['RV'].max())))


def fig_qlike():
    R = RES['rv']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, key, title in ((axes[0], 'qlike', f'Full test period ({R["n"]} days)'),
                           (axes[1], 'qlike_post', f'After 3 Nov 2025 ({R["n_post"]} days)')):
        v = [R[m][key] for m in RV_MODELS]
        ax.barh(range(len(RV_MODELS)), v, color=[RV_COL[m] for m in RV_MODELS])
        for i, m in enumerate(RV_MODELS):
            ax.text(v[i] + 0.004, i, f'{v[i]:.3f}', va='center', fontsize=7, color='black')
        ax.set_yticks(range(len(RV_MODELS)), [RV_LBL[m] for m in RV_MODELS])
        ax.invert_yaxis()
        ax.set_xlabel('Mean QLIKE loss (lower is better)')
        ax.set_title(title, fontsize=9, loc='left')
        ax.set_xlim(0, max(v) * 1.2)
    fig.tight_layout()
    save_fig('ch14_qlike')


def fig_context():
    R = RES['rv']
    Ls = sorted(int(k) for k in R['ctx'])
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    ax.plot(Ls, [R['ctx'][str(L)] for L in Ls], 'o-', color=IDAred, label='Chronos-2 on log RV')
    ax.axhline(R['logHAR']['qlike'], color=Purple, ls='--', lw=0.9, label='log-HAR (500-day window)')
    ax.set_xscale('log', base=2)
    ax.set_xticks(Ls, [str(L) for L in Ls])
    ax.set_xlabel('Context length (days)')
    ax.set_ylabel('Mean QLIKE loss')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch14_context_length')


# =============================================================================
# EVALUATION: VaR 1%, ES 2.5%
# =============================================================================
def eval_risk():
    out, series = {}, {}
    for a in M.ASSETS:
        d = load_csv(f'ch14_risk_{a}.csv')
        L = -d['y'].values
        post = d.index >= M.POST_FROM
        res = {'n': int(len(d)), 'start': str(d.index[0].date()), 'n_post': int(post.sum())}
        fz = {}
        for m in RISK_MODELS:
            v1, v25, es = d[f'{m}|VaR1'].values, d[f'{m}|VaR2.5'].values, d[f'{m}|ES2.5'].values
            h = (L > v1).astype(int)
            k = M.kupiec(h, 0.01)
            c = M.christoffersen(h, 0.01)
            kp = M.kupiec(h[post], 0.01)
            fz[m] = M.fz0(L, v25, np.maximum(es, 1e-6))
            res[m] = dict(x=k['x'], rate=100 * k['rate'], p_uc=k['p'], p_ind=c['p_ind'], p_cc=c['p_cc'],
                          n11=c['n11'], x_post=kp['x'], rate_post=100 * kp['rate'], p_post=kp['p'],
                          fz0=float(fz[m].mean()), var_mean=float(v1.mean()), es_mean=float(es.mean()),
                          es_ratio=float(np.mean(es / v1)), x25=int(np.sum(L > v25)),
                          pin1=float(np.mean(M.pinball(-L, -v1, 0.01))))
        F = pd.DataFrame(fz)
        p = M.mcs(F)
        for m in RISK_MODELS:
            res[m]['mcs'] = float(p[m])
            dm = M.diebold_mariano(F[m], F['FHS']) if m != 'FHS' else dict(DM=np.nan, p=np.nan)
            res[m]['dm_fhs'] = float(dm['DM'])
            res[m]['p_dm_fhs'] = float(dm['p'])
        # raw 1% quantiles for Bolt and TimesFM (clamped at the 10% decile) and VaR 10%
        for fm in ('bolt', 'timesfm'):
            h = (L > d[f'{fm}-raw|VaR1'].values).astype(int)
            res[f'{fm}-raw'] = dict(rate=100 * h.mean(), x=int(h.sum()))
        v10 = {}
        for m, col in (('HS', 'HS|VaR10'), ('FHS', 'FHS|VaR10'), ('C2-raw', 'C2-raw|VaR10'),
                       ('bolt-raw', 'bolt-raw|VaR10'), ('timesfm-raw', 'timesfm-raw|VaR10')):
            h = (L > d[col].values).astype(int)
            k = M.kupiec(h, 0.10)
            c = M.christoffersen(h, 0.10)
            v10[m] = dict(rate=100 * k['rate'], p_uc=k['p'], p_ind=c['p_ind'],
                          pin=float(np.mean(M.pinball(-L, -d[col].values, 0.10))))
        res['v10'] = v10
        out[a] = res
        series[a] = d
    RES['risk'] = out
    return series


def fig_breaches():
    R = RES['risk']
    models = RISK_MODELS + ['bolt-raw']
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    w = 0.11
    x = np.arange(len(M.ASSETS))
    for i, a in enumerate(M.ASSETS):
        n = R[a]['n']
        lo, hi = stats.binom.ppf([0.025, 0.975], n, 0.01) / n * 100
        ax.fill_between([i - 0.45, i + 0.45], lo, hi, color=LightGray, alpha=0.8, lw=0, zorder=0,
                        label='95% range of the breach rate under a correct model' if i == 0 else None)
    for j, m in enumerate(models):
        v = [R[a][m]['rate'] for a in M.ASSETS]
        ax.bar(x + (j - (len(models) - 1) / 2) * w, v, w, color=RISK_COL[m], label=RISK_LBL[m], zorder=3)
    ax.axhline(1, color=Gray, ls='--', lw=0.7)
    ax.set_yscale('log')
    ax.set_yticks([0.5, 1, 2, 5, 10], ['0.5', '1', '2', '5', '10'])
    ax.set_xticks(x, [M.LABELS[a] for a in M.ASSETS])
    ax.set_ylabel('Breach rate of VaR 1% (%)')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    save_fig('ch14_breach_rates')


def fig_var_path(series):
    d = series['sp500'].loc['2020-02-01':'2020-06-30']
    L = -d['y']
    fig, ax = plt.subplots(figsize=(7.0, 3.1))
    ax.bar(d.index, L.clip(lower=0), width=1.0, color=Teal, alpha=0.7, label='Daily loss (gains set to 0)')
    for m in ('FHS', 'C2-raw', 'C2-FHS'):
        ax.plot(d.index, d[f'{m}|VaR1'], color=RISK_COL[m], lw=1.0, label=f'VaR 1%: {RISK_LBL[m]}')
        hit = L > d[f'{m}|VaR1']
        ax.scatter(d.index[hit], L[hit], color=RISK_COL[m], s=14, zorder=3)
    ax.set_ylabel('Loss (%)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch14_var_path')
    RES['covid'] = {m: int(np.sum(L > d[f'{m}|VaR1'])) for m in RISK_MODELS}
    RES['covid']['T'] = int(len(d))
    RES['covid']['maxloss'] = float(L.max())
    for m in ('FHS', 'C2-raw', 'C2-FHS'):
        RES['covid'][m + '|max'] = float(d[f'{m}|VaR1'].max())


def fig_var10():
    R = RES['risk']
    models = ['HS', 'FHS', 'C2-raw', 'bolt-raw', 'timesfm-raw']
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    w = 0.15
    x = np.arange(len(M.ASSETS))
    for j, m in enumerate(models):
        v = [R[a]['v10'][m]['rate'] for a in M.ASSETS]
        ax.bar(x + (j - 2) * w, v, w, color=RISK_COL[m], label=RISK_LBL[m])
    ax.axhline(10, color=Gray, ls='--', lw=0.7)
    ax.set_xticks(x, [M.LABELS[a] for a in M.ASSETS])
    ax.set_ylabel('Breach rate of VaR 10% (%)')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    save_fig('ch14_var10')


def fig_mcs():
    R = RES['risk']
    P = pd.DataFrame({M.LABELS[a]: [R[a][m]['mcs'] for m in RISK_MODELS] for a in M.ASSETS},
                     index=[RISK_LBL[m] for m in RISK_MODELS])
    Z = np.log10(np.clip(P.values.astype(float), 1e-4, 1))
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    ax.imshow(Z, cmap=PV_CMAP, vmin=-4, vmax=0, aspect='auto')
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            v = P.values[i, j]
            ax.text(j, i, '<0.001' if v < 0.001 else f'{v:.3f}', ha='center', va='center', fontsize=7.5, color='black')
    ax.set_xticks(range(P.shape[1]), P.columns)
    ax.set_yticks(range(P.shape[0]), P.index)
    for s in ax.spines.values():
        s.set_visible(False)
    save_fig('ch14_mcs')


if __name__ == '__main__':
    fig_vanishing()
    fig_acf()
    fig_tokenization()
    fig_patching()
    fig_fan()
    ser = eval_returns()
    fig_return_r2(ser)
    fig_cum_sse(ser)
    fig_lstm_training()
    fig_lstm_seeds()
    d, L = eval_rv()
    fig_rv_path(d)
    fig_qlike()
    fig_context()
    rs = eval_risk()
    fig_breaches()
    fig_var_path(rs)
    fig_var10()
    fig_mcs()
    RES['params'] = dict(lstm_ret=M.lstm_param_count(1, 16) + 17, lstm_rv=M.lstm_param_count(1, 8) + 9,
                         chronos2=119477664, bolt=47718016, timesfm=231289280, t5small=46154240)
    with open(os.path.join(HERE, 'ch14_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print('wrote ch14_results.json')

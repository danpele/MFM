"""
Generator pentru toate graficele si cifrele din Capitolul 9: volatilitate realizata
===================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos; seriile de timp nu sunt gri.
Date: SPY, bare de 5 minute, sesiunea regulata din SUA (octombrie 2020 - septembrie 2026); Bitcoin, bare de 5 minute,
zile UTC complete (septembrie 2024 - septembrie 2026); randamente zilnice SPY (ajustate) si Bitcoin; indicele VIX.
Varianțe zilnice in %^2; volatilitati anualizate in % (252 de zile pentru SPY, 365 pentru Bitcoin).
Cifrele sunt salvate in ch9_results.json (folosite de generatoarele de slide-uri).
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
import mfm_data as M      # noqa: E402
import rv_tools as T      # noqa: E402

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

# Culori brand (gri doar pentru linii de referinta si benzi)
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Teal     = '#17A2B8'
Gray     = '#7F7F7F'
LightGray = '#DADADA'
MODEL_COL = {'logHAR': IDAred, 'HAR': Orange, 'GARCH-t': MainBlue, 'EWMA': Purple, 'RW': Forest}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
OOS_SPY = '2022-01-03'
OOS_BTC = '2025-03-01'


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


def fig_legend_bottom(fig, handles=None, labels=None, ncol=3, y=0.0):
    """O singura legenda pentru o figura cu mai multe panouri, sub figura."""
    if handles is None:
        handles, labels = [], []
        for ax in fig.axes:
            h, l = ax.get_legend_handles_labels()
            for hh, ll in zip(h, l):
                if ll not in labels:
                    handles.append(hh)
                    labels.append(ll)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, pd.Timestamp):
        return str(x.date())
    return x


# =============================================================================
# DATE
# =============================================================================
P_SPY = M.spy_intraday()
R_SPY = M.intraday_returns(P_SPY)
ON, OC, CC = M.spy_overnight(P_SPY)
RV_SPY = T.rv(R_SPY)                       # varianta realizata intraday (%^2)
RVT_SPY = RV_SPY + ON ** 2                 # varianta zilnica totala: intraday + randamentul peste noapte la patrat
P_BTC = M.btc_intraday()
R_BTC = M.intraday_returns(P_BTC)
RV_BTC = T.rv(R_BTC)
D_SPY = M.daily_returns('spy', start='2000-01-01')
D_BTC = M.daily_returns('btc', start='2014-09-17')


def ann(v, ppy):
    """Volatilitatea anualizata (%) dintr-o varianta zilnica (%^2)."""
    return np.sqrt(ppy * v)


# =============================================================================
# 1. O ZI DE TRANZACTIONARE: PRET SI VARIANTA REALIZATA CUMULATA
# =============================================================================
def fig_intraday_day(day='2025-04-07'):
    """Pretul SPY pe bare de 5 minute intr-o zi agitata si suma cumulata a patratelor randamentelor."""
    d = pd.Timestamp(day)
    p = P_SPY.loc[d].dropna()
    r = R_SPY.loc[d].dropna()
    times = pd.date_range(d + pd.Timedelta('09:30:00'), periods=len(p), freq='5min')
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.1))
    axes[0].plot(times, p.values, color=MainBlue, lw=1.1, label='SPY price, 5-minute bars')
    axes[0].set_ylabel('USD')
    axes[0].set_title('SPY on 7 April 2025', fontsize=9, loc='left')
    cum = (r ** 2).cumsum()
    axes[1].step(times[1:], cum.values, where='post', color=IDAred, lw=1.2, label=r'Cumulative $\sum r_i^2$ (%$^2$)')
    big = int(np.argmax(np.abs(r.values)))
    axes[1].scatter(times[1 + big], cum.values[big], color=Amber, zorder=3, s=22,
                    label=f'Largest 5-minute return ({r.values[big]:+.2f}%)')
    axes[1].set_ylabel('%$^2$')
    axes[1].set_title('Realised variance accumulates over the day', fontsize=9, loc='left')
    for ax in axes:
        ax.tick_params(axis='x', labelsize=7)
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    fig_legend_bottom(fig, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch9_intraday_day')
    return {'day': day, 'rv': float(r.pow(2).sum()), 'vol': float(ann(r.pow(2).sum(), 252)), 'n': int(len(r)),
            'max_ret': float(r.values[big]), 'max_time': str(times[1 + big].time())[:5],
            'max_share': float(r.values[big] ** 2 / r.pow(2).sum()), 'oc': float(OC[d]), 'on': float(ON[d])}


# =============================================================================
# 2. SERIILE DE VARIANTA REALIZATA
# =============================================================================
def fig_rv_series():
    """Volatilitatea realizata zilnica anualizata: SPY (intraday) si Bitcoin (24 de ore)."""
    fig, axes = plt.subplots(2, 1, figsize=(9.6, 4.6), sharex=False)
    axes[0].plot(RV_SPY.index, ann(RV_SPY, 252), color=MainBlue, lw=0.6, label='SPY, daily realised volatility (09:30-16:00, % p.a.)')
    axes[1].plot(RV_BTC.asfreq('D').index, ann(RV_BTC.asfreq('D'), 365), color=Amber, lw=0.6, label='Bitcoin, daily realised volatility (24 hours UTC, % p.a.)')
    for ax in axes:
        ax.set_ylabel('% p.a.')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    save_fig('ch9_rv_series')
    vs, vb = ann(RV_SPY, 252), ann(RV_BTC, 365)
    return {'spy_mean': float(ann(RV_SPY.mean(), 252)), 'spy_med': float(vs.median()), 'spy_max': float(vs.max()),
            'spy_maxdate': str(vs.idxmax().date()), 'spy_min': float(vs.min()), 'spy_n': int(len(vs)),
            'btc_mean': float(ann(RV_BTC.mean(), 365)), 'btc_med': float(vb.median()), 'btc_max': float(vb.max()),
            'btc_maxdate': str(vb.idxmax().date()), 'btc_n': int(len(vb)),
            'spy_start': str(RV_SPY.index[0].date()), 'btc_start': str(RV_BTC.index[0].date()),
            'btc_calendar': int((RV_BTC.index[-1] - RV_BTC.index[0]).days + 1)}


def fig_overnight():
    """Descompunerea variantei zilnice SPY pe ani: partea intraday si randamentul peste noapte."""
    df = pd.DataFrame({'intraday': RV_SPY, 'overnight': ON ** 2})
    y = df.groupby(df.index.year).mean()
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    ax.bar(y.index, 252 * y['intraday'], color=MainBlue, width=0.6, label='Intraday realised variance (09:30-16:00)')
    ax.bar(y.index, 252 * y['overnight'], bottom=252 * y['intraday'], color=Amber, width=0.6,
           label='Squared overnight return (close to next open)')
    ax.set_ylabel('Annualised variance (%$^2$)')
    ax.set_xticks(y.index)
    ax.set_xticklabels([f'{k}*' if k in (2020, 2026) else str(k) for k in y.index])
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch9_overnight')
    share = (ON ** 2).sum() / (RV_SPY.sum() + (ON ** 2).sum())
    sh_y = (y['overnight'] / (y['intraday'] + y['overnight']))
    return {'share': float(share), 'share_by_year': {int(k): float(v) for k, v in sh_y.items()},
            'cc_vol': float(CC.std() * np.sqrt(252)), 'rvt_vol': float(ann(RVT_SPY.mean(), 252)),
            'oc_vol': float(OC.std() * np.sqrt(252)), 'on_vol': float(ON.std() * np.sqrt(252)),
            'max_on': float(ON.abs().max()), 'max_on_date': str(ON.abs().idxmax().date()), 'max_on_val': float(ON[ON.abs().idxmax()])}


# =============================================================================
# 3. INCERTITUDINEA RV: INTERVAL DE INCREDERE ASIMPTOTIC
# =============================================================================
def fig_rv_ci(a='2025-03-01', b='2025-05-30'):
    """RV zilnica SPY cu intervalul de incredere de 95% (Barndorff-Nielsen si Shephard), martie-mai 2025."""
    lo, hi = T.rv_ci(R_SPY)
    s = slice(a, b)
    fig, ax = plt.subplots(figsize=(9.0, 3.2))
    ax.fill_between(RV_SPY.loc[s].index, ann(lo.loc[s], 252), ann(hi.loc[s], 252), color=LightGray, alpha=0.9, lw=0,
                    label='95% confidence interval for integrated volatility')
    ax.plot(RV_SPY.loc[s].index, ann(RV_SPY.loc[s], 252), 'o-', color=MainBlue, ms=2.5, lw=0.9,
            label='Realised volatility (% p.a.)')
    ax.set_ylabel('% p.a.')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch9_rv_ci')
    width = (ann(hi, 252) - ann(lo, 252)) / ann(RV_SPY, 252)
    d = pd.Timestamp('2025-04-09')
    return {'rel_width_med': float(width.median()), 'd': str(d.date()), 'd_vol': float(ann(RV_SPY[d], 252)),
            'd_lo': float(ann(lo[d], 252)), 'd_hi': float(ann(hi[d], 252)),
            'q_med': float(np.sqrt(2 / 3 * (R_SPY ** 4).sum(axis=1) / RV_SPY ** 2).median())}


# =============================================================================
# 4. SEZONALITATEA INTRADAY
# =============================================================================
def fig_seasonality():
    """Media |r| pe intervale de 5 minute: SPY (forma de U) si Bitcoin pe ore UTC."""
    full = R_SPY[R_SPY.notna().sum(axis=1) == 78]
    s = full.abs().mean()
    tb = R_BTC.abs().mean().values.reshape(24, 12).mean(axis=1)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.1))
    lab = pd.date_range('2000-01-01 09:35', periods=78, freq='5min')
    axes[0].bar(np.arange(78), s.values, color=MainBlue, width=0.8, label='SPY: mean |5-minute return| (%), New York time')
    ticks = [0, 12, 24, 36, 48, 60, 72]
    axes[0].set_xticks(ticks)
    axes[0].set_xticklabels([lab[i].strftime('%H:%M') for i in ticks], fontsize=7)
    axes[1].bar(np.arange(24), tb, color=Amber, width=0.8, label='Bitcoin: mean |5-minute return| (%) by UTC hour')
    axes[1].axvspan(13.5, 20.5, color=LightGray, alpha=0.6, lw=0, zorder=0, label='US equity session (13:30-21:00 UTC, depending on daylight saving)')
    axes[1].set_xticks(range(0, 24, 3))
    axes[1].set_xlabel('Hour (UTC)')
    for ax in axes:
        ax.set_ylabel('%')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch9_seasonality')
    return {'spy_first': float(s.iloc[0]), 'spy_mid': float(s.iloc[30:50].mean()), 'spy_last': float(s.iloc[-1]),
            'spy_ratio': float(s.iloc[0] / s.iloc[30:50].mean()), 'btc_max_hour': int(np.argmax(tb)),
            'btc_min_hour': int(np.argmin(tb)), 'btc_ratio': float(tb.max() / tb.min())}


# =============================================================================
# 5. ZGOMOTUL DE MICROSTRUCTURA: SIMULARE SI GRAFICUL SEMNATURII
# =============================================================================
def simulate_noise(days=100, n=23400, sigma=1.0, omega=0.01, seed=SEED):
    """Pret eficient (miscare browniana, volatilitate zilnica variabila) + zgomot i.i.d. N(0, omega^2), 1 secunda."""
    rng = np.random.default_rng(seed)
    sig_d = sigma * np.exp(0.3 * rng.standard_normal(days) - 0.045)
    X = np.cumsum(rng.standard_normal((days, n)) * (sig_d[:, None] / np.sqrt(n)), axis=1)
    X = np.c_[np.zeros(days), X]
    Y = X + omega * rng.standard_normal(X.shape)        # pretul observat (log x 100)
    return X, Y, sig_d ** 2


def fig_noise_simulation():
    """Graficul semnaturii pentru date simulate: RV explodeaza la frecvente mari; TSRV si nucleul realizat corecteaza."""
    X, Y, iv = simulate_noise()
    secs = [1, 2, 5, 10, 30, 60, 120, 300, 600, 900, 1800]
    sig = [np.mean(np.sum(np.diff(Y[:, ::k], axis=1) ** 2, axis=1)) for k in secs]
    sig_eff = [np.mean(np.sum(np.diff(X[:, ::k], axis=1) ** 2, axis=1)) for k in secs]
    n = Y.shape[1] - 1
    # TSRV: scara rapida 1 secunda, scara lenta 300 de secunde (K = 300)
    K = 300
    rv_all = np.sum(np.diff(Y, axis=1) ** 2, axis=1)
    rv_avg = np.mean([np.sum(np.diff(Y[:, o::K], axis=1) ** 2, axis=1) for o in range(K)], axis=0)
    nbar = (n - K + 1) / K
    tsrv = (rv_avg - nbar / n * rv_all) / (1 - nbar / n)
    # nucleu realizat Parzen pe randamente de 1 secunda
    rk = []
    for i in range(Y.shape[0]):
        r = np.diff(Y[i])
        om2 = np.sum(r ** 2) / (2 * n)
        iv20 = np.sum(np.diff(Y[i, ::1200]) ** 2)
        H = int(np.ceil(3.5134 * (om2 / iv20) ** 0.4 * n ** 0.6))
        g = [np.sum(r[h:] * r[:n - h]) for h in range(H + 1)]
        rk.append(g[0] + 2 * sum(T.parzen(h / (H + 1)) * g[h] for h in range(1, H + 1)))
    rk = np.array(rk)
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    ax.plot(secs, sig, 'o-', color=IDAred, ms=4, label='RV of observed prices (efficient price + noise)')
    ax.plot(secs, sig_eff, 's--', color=MainBlue, ms=3.5, label='RV of the efficient price (no noise)')
    ax.axhline(iv.mean(), color=Gray, lw=0.8, ls=':', label='True integrated variance (mean)')
    ax.axhline(tsrv.mean(), color=Forest, lw=1.1, label='Two-scale RV, 1 s and 5 min')
    ax.axhline(np.mean(rk), color=Purple, lw=1.1, ls='-.', label='Realised kernel (Parzen), 1 s')
    ax.set_xscale('log')
    ax.set_xticks(secs)
    ax.set_xticklabels(['1s', '2s', '5s', '10s', '30s', '1m', '2m', '5m', '10m', '15m', '30m'], fontsize=7)
    ax.set_xlabel('Sampling interval')
    ax.set_ylabel('Mean daily RV (%$^2$)')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch9_noise_simulation')
    return {'iv': float(iv.mean()), 'rv1s': float(sig[0]), 'rv1m': float(sig[5]), 'rv5m': float(sig[7]), 'rv30m': float(sig[-1]),
            'bias1s': float(2 * n * 0.01 ** 2), 'bias1m': float(2 * 390 * 0.01 ** 2), 'bias5m': float(2 * 78 * 0.01 ** 2),
            'tsrv': float(tsrv.mean()), 'rk': float(rk.mean()), 'omega': 0.01, 'n': n,
            'sd_rv5m': float(np.std(np.sum(np.diff(Y[:, ::300], axis=1) ** 2, axis=1) - iv)),
            'sd_tsrv': float(np.std(tsrv - iv)), 'sd_rk': float(np.std(rk - iv))}


KS_SPY = [1, 2, 3, 4, 6, 8, 12, 16, 20, 26]
KS_BTC = [1, 2, 3, 4, 6, 12, 24, 36, 48, 72]


def fig_signature():
    """Graficul semnaturii empiric: SPY (5-130 de minute) si Bitcoin (5-360 de minute)."""
    ss = T.signature(P_SPY, KS_SPY, 252)
    sb = T.signature(P_BTC, KS_BTC, 365)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.1))
    for ax, s, ks, col, name in [(axes[0], ss, KS_SPY, MainBlue, 'SPY'), (axes[1], sb, KS_BTC, Amber, 'Bitcoin')]:
        m = [5 * k for k in ks]
        ax.plot(m, s['sparse'], 'o-', color=col, ms=3.5, label='One grid (sparse sampling)')
        ax.plot(m, s['subsampled'], 's--', color=IDAred, ms=3, label='Average over shifted grids (subsampling)')
        ax.set_xlabel('Sampling interval (minutes)')
        ax.set_ylabel('Mean realised volatility (% p.a.)')
        ax.set_title(name, fontsize=9, loc='left')
        lo, hi = s.values.min(), s.values.max()
        ax.set_ylim(lo - 0.12 * lo, hi + 0.12 * hi)
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch9_signature')
    nz_s, nz_b = T.noise_var(R_SPY), T.noise_var(R_BTC)
    ts = T.tsrv(P_SPY, 6)
    nbar = (T.nret(R_SPY) - 5) / 6
    ts_adj = ts / (1 - nbar / T.nret(R_SPY))
    rk, H = T.realized_kernel(R_SPY, P_SPY)
    return {'spy5': float(ss['sparse'].iloc[0]), 'spy30': float(ss['subsampled'].loc[6]), 'spy130': float(ss['subsampled'].iloc[-1]),
            'spy_range': float(ss.values.max() - ss.values.min()),
            'btc5': float(sb['sparse'].iloc[0]), 'btc60': float(sb['subsampled'].loc[12]), 'btc360': float(sb['subsampled'].iloc[-1]),
            'spy_rho1': nz_s['rho1'], 'btc_rho1': nz_b['rho1'], 'spy_om2rv': nz_s['omega2_rv'],
            'tsrv_ratio': float(ts_adj.mean() / RV_SPY.mean()), 'rk_ratio': float(rk.mean() / RV_SPY.mean()),
            'rk_H_med': float(H.median()), 'corr_rk_rv': float(np.corrcoef(rk, RV_SPY)[0, 1]),
            'corr_ts_rv': float(np.corrcoef(ts_adj, RV_SPY)[0, 1])}


# =============================================================================
# 6. SALTURI: VARIATIA BIPOWER SI TESTUL DE SALTURI
# =============================================================================
def fig_jumps():
    """Zilele cu salt semnificativ (nivel 0,1%): SPY si Bitcoin; marimea punctului = componenta de salt."""
    js, jb = T.jump_test(R_SPY), T.jump_test(R_BTC)
    fig, axes = plt.subplots(2, 1, figsize=(9.6, 4.6))
    for ax, j, col, ppy, name in [(axes[0], js, MainBlue, 252, 'SPY'), (axes[1], jb, Amber, 365, 'Bitcoin')]:
        jv = j['rv'].asfreq('D') if name == 'Bitcoin' else j['rv']
        ax.plot(jv.index, ann(jv, ppy), color=col, lw=0.6, label=f'{name}: realised volatility (% p.a.)')
        jj = j[j['jump']]
        ax.scatter(jj.index, ann(jj['rv'], ppy), s=8 + 400 * jj['J'] / j['rv'].max(), color=IDAred, zorder=3,
                   label='Day with a significant jump (0.1% level)')
        ax.set_ylabel('% p.a.')
    fig_legend_bottom(fig, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    save_fig('ch9_jumps')
    out = {}
    for k, j, R in [('spy', js, R_SPY), ('btc', jb, R_BTC)]:
        top = j.loc[j['z'].idxmax()]
        out[k] = {'share': float(j['jump'].mean()), 'n_jump': int(j['jump'].sum()), 'N': int(len(j)),
                  'jshare': float(j['J'].sum() / j['rv'].sum()), 'bv_rv': float((j['bv'] / j['rv']).mean()),
                  'top_date': str(j['z'].idxmax().date()), 'top_z': float(top['z']),
                  'top_jshare': float(top['J'] / top['rv']), 'top_rv_vol': float(ann(top['rv'], 252 if k == 'spy' else 365)),
                  'mean_jshare_on_jump': float((j.loc[j['jump'], 'J'] / j.loc[j['jump'], 'rv']).mean())}
    return out


# =============================================================================
# 7. FAPTE STILIZATE ALE RV: LOG RV APROAPE NORMALA, RANDAMENTE STANDARDIZATE
# =============================================================================
def fig_distributions():
    """Stanga: log RV (SPY) si distributia Normala; dreapta: r/sd(r) vs r/sqrt(RV) (Andersen et al.)."""
    lv = np.log(RV_SPY)
    z = OC / np.sqrt(RV_SPY)
    u = OC / OC.std()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.2))
    axes[0].hist(lv, bins=50, density=True, color=MainBlue, alpha=0.8, label='log RV, SPY (daily)')
    x = np.linspace(lv.min(), lv.max(), 200)
    axes[0].plot(x, stats.norm.pdf(x, lv.mean(), lv.std()), color=IDAred, lw=1.3, label='Normal distribution, same mean and s.d.')
    axes[0].set_xlabel('log RV')
    bins = np.linspace(-6, 6, 61)
    axes[1].hist(u.clip(-6, 6), bins=bins, density=True, color=Amber, alpha=0.55, label=r'Open-to-close return / its s.d.')
    axes[1].hist(z.clip(-6, 6), bins=bins, density=True, histtype='step', color=MainBlue, lw=1.4, label=r'Open-to-close return / $\sqrt{RV}$')
    xx = np.linspace(-6, 6, 300)
    axes[1].plot(xx, stats.norm.pdf(xx), color=IDAred, lw=1.2, ls='--', label='Standard Normal distribution')
    axes[1].set_xlabel('Standardised return')
    fig_legend_bottom(fig, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch9_distributions')
    lvb = np.log(RV_BTC)
    zb = CC_BTC_UTC() / np.sqrt(RV_BTC)
    return {'lv_skew': float(stats.skew(lv)), 'lv_kurt': float(stats.kurtosis(lv) + 3),
            'v_skew': float(stats.skew(RV_SPY)), 'v_kurt': float(stats.kurtosis(RV_SPY) + 3),
            'lvb_skew': float(stats.skew(lvb)), 'lvb_kurt': float(stats.kurtosis(lvb) + 3),
            'u_kurt': float(stats.kurtosis(u) + 3), 'z_kurt': float(stats.kurtosis(z) + 3), 'z_sd': float(z.std()),
            'jb_u': float(stats.jarque_bera(u).statistic), 'jb_z': float(stats.jarque_bera(z).statistic),
            'jb_z_p': float(stats.jarque_bera(z).pvalue),
            'ub_kurt': float(stats.kurtosis(CC_BTC_UTC() / CC_BTC_UTC().std()) + 3), 'zb_kurt': float(stats.kurtosis(zb) + 3)}


def CC_BTC_UTC():
    """Randamentul zilnic Bitcoin (UTC) din barele de 5 minute: deschiderea de 00:00 -> ultima inchidere."""
    return 100 * np.log(P_BTC.iloc[:, -1] / P_BTC[0])


def acf(x, lags):
    x = np.asarray(x) - np.mean(x)
    return np.array([np.sum(x[l:] * x[:-l]) / np.sum(x * x) for l in range(1, lags + 1)])


def fig_acf():
    """Autocorelatiile log RV (SPY, Bitcoin) si ale randamentelor zilnice la patrat (SPY): memorie lunga."""
    L = 100
    a1 = acf(np.log(RVT_SPY), L)
    b = np.log(RV_BTC.asfreq('D')).interpolate()
    a2 = acf(b.values, L)
    a3 = acf((CC ** 2).values, L)
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    lg = np.arange(1, L + 1)
    ax.plot(lg, a1, color=MainBlue, lw=1.3, label='log RV, SPY (trading days)')
    ax.plot(lg, a2, color=Amber, lw=1.3, label='log RV, Bitcoin (calendar days)')
    ax.plot(lg, a3, color=Purple, lw=1.0, ls='--', label='Squared daily return, SPY')
    band = 1.96 / np.sqrt(len(RVT_SPY))
    ax.axhspan(-band, band, color=LightGray, alpha=0.7, lw=0, label='95% band under independence (SPY)')
    ax.set_xlabel('Lag (days)')
    ax.set_ylabel('Autocorrelation')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch9_acf')
    dow = RV_BTC.groupby(RV_BTC.index.dayofweek).mean()
    return {'btc_weekend_ratio': float(dow[[5, 6]].mean() / dow[[0, 1, 2, 3, 4]].mean()),
            'btc_sat': float(ann(dow[5], 365)), 'btc_wed': float(ann(dow[2], 365)), 'btc7': float(a2[6]), 'btc3': float(a2[2]),
            'spy1': float(a1[0]), 'spy22': float(a1[21]), 'spy100': float(a1[99]), 'btc1': float(a2[0]),
            'btc30': float(a2[29]), 'btc100': float(a2[99]), 'sq1': float(a3[0]), 'sq22': float(a3[21]),
            'band': float(band)}


# =============================================================================
# 8. VIX SI VOLATILITATEA REALIZATA ULTERIOARA: PRIMA DE RISC A VARIANTEI
# =============================================================================
def fig_vix():
    """VIX (volatilitatea implicita pe 30 de zile) vs volatilitatea realizata in urmatoarele 21 de zile (SPY, cu noaptea)."""
    vix = M.daily_close('vix').reindex(RVT_SPY.index).ffill()
    fut = RVT_SPY[::-1].rolling(21).sum()[::-1].shift(-1)          # suma RV pe zilele t+1..t+21
    fvol = np.sqrt(252 / 21 * fut)
    df = pd.DataFrame({'vix': vix, 'fvol': fvol}).dropna()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.2), gridspec_kw={'width_ratios': [1.8, 1]})
    axes[0].plot(df.index, df['vix'], color=IDAred, lw=0.8, label='VIX (implied volatility, next 30 calendar days)')
    axes[0].plot(df.index, df['fvol'], color=MainBlue, lw=0.8, label='Realised volatility over the next 21 trading days')
    axes[0].set_ylabel('% p.a.')
    vrp = df['vix'] ** 2 - df['fvol'] ** 2
    gap = df['vix'] - df['fvol']
    axes[1].hist(gap, bins=np.arange(-30, 31, 1.5), color=Teal, alpha=0.85,
                 label='VIX minus future realised volatility (percentage points)')
    axes[1].axvline(0, color=Gray, lw=0.8)
    axes[1].set_xlabel('Percentage points')
    fig_legend_bottom(fig, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch9_vix')
    mz = T.mz_test(df['fvol'] ** 2, df['vix'] ** 2)
    return {'vix_mean': float(df['vix'].mean()), 'fvol_mean': float(df['fvol'].mean()),
            'vrp_mean': float(vrp.mean()), 'vrp_pos': float((vrp > 0).mean()), 'corr': float(df['vix'].corr(df['fvol'])),
            'mz_b': mz['b'], 'mz_se_b': mz['se_b'], 'mz_r2': mz['r2'], 'N': int(len(df)),
            'vrp_min_date': str(vrp.idxmin().date()), 'vrp_min': float(vrp.min()),
            'gap_mean': float(gap.mean()), 'gap_med': float(gap.median()), 'gap_out': int(((gap < -30) | (gap > 30)).sum())}


# =============================================================================
# 9. MODELUL HAR-RV
# =============================================================================
def har_tables():
    """HAR si log-HAR pe esantionul complet: SPY (varianta totala) si Bitcoin (24 de ore)."""
    out = {}
    for k, v, cal in [('spy', RVT_SPY, False), ('btc', RV_BTC, True)]:
        for tag, log in [('lev', False), ('log', True)]:
            res, X, ok = T.har_fit(v, calendar=cal, log=log)
            out[f'{k}_{tag}'] = {'b': res['b'], 'se': res['se'], 'r2': res['r2'], 'T': res['T'], 'lags': res['lags'],
                                 'pers': float(sum(res['b'][1:]))}
    return out


def fig_har(tab):
    """Stanga: ponderile implicite ale log-HAR pe intarzieri (SPY, Bitcoin); dreapta: log-HAR SPY in esantion, ultimele 250 de zile."""
    ws = T.har_weights(tab['spy_log']['b'], 30)
    wb = T.har_weights(tab['btc_log']['b'], 30)
    # Bitcoin: saptamana = 7 zile, luna = 30 de zile calendaristice
    b = tab['btc_log']['b']
    wb = np.zeros(30)
    wb[0] += b[1]
    wb[:7] += b[2] / 7
    wb[:30] += b[3] / 30
    res, X, ok = T.har_fit(RVT_SPY, log=True)
    fit = pd.Series(np.column_stack([np.ones(ok.sum()), X[ok].values]) @ res['b'], index=X[ok].index)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.2), gridspec_kw={'width_ratios': [1, 1.5]})
    lg = np.arange(1, 31)
    axes[0].bar(lg - 0.2, ws, 0.4, color=MainBlue, label='SPY: implied weight on lag')
    axes[0].bar(lg + 0.2, wb, 0.4, color=Amber, label='Bitcoin: implied weight on lag')
    axes[0].axhline(0, color=Gray, lw=0.6)
    axes[0].set_xlabel('Lag (days)')
    last = fit.index[-250:]
    axes[1].plot(last, ann(RVT_SPY.loc[last], 252), color=Teal, lw=0.9, label='SPY realised volatility incl. overnight (% p.a.)')
    axes[1].plot(last, ann(np.exp(fit.loc[last] + res['resid'].var() / 2), 252), color=IDAred, lw=1.2,
                 label='log-HAR fitted value (% p.a.)')
    axes[1].tick_params(axis='x', labelsize=7)
    axes[1].set_ylabel('% p.a.')
    axes[0].set_ylabel('Weight')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.12, 1, 1))
    save_fig('ch9_har')
    return {'w1_spy': float(ws[0]), 'w5_spy': float(ws[4]), 'w6_spy': float(ws[5]), 'w22_spy': float(ws[21]), 'w23_spy': float(ws[22]),
            'w1_btc': float(wb[0]), 'w7_btc': float(wb[6]), 'w8_btc': float(wb[7])}


# =============================================================================
# 10. PROGNOZE OUT-OF-SAMPLE: HAR vs GARCH vs EWMA
# =============================================================================
def oos_forecasts(v, r, start, calendar):
    """Prognoze pentru ziua urmatoare: HAR, log-HAR (fereastra extinsa), GARCH(1,1)-t si EWMA pe randamente zilnice, RV de ieri."""
    idx = v.loc[start:].index
    F = pd.DataFrame({
        'logHAR': T.har_expanding(v, start, calendar=calendar, log=True),
        'HAR': T.har_expanding(v, start, calendar=calendar),
        'GARCH-t': T.garch_forecasts(r, idx),
        'EWMA': T.ewma_forecasts(r).reindex(idx),
        'RW': (v.asfreq('D').shift(1).reindex(idx) if calendar else v.shift(1).reindex(idx))}).dropna()
    return F, v.reindex(F.index)


def evaluate(F, y):
    """Pierderi medii QLIKE si MSE, R^2 Mincer-Zarnowitz, teste DM fata de log-HAR."""
    out = {}
    for c in F:
        mz = T.mz_test(y, F[c])
        out[c] = {'qlike': float(T.qlike(y, F[c]).mean()), 'mse': float(T.mse(y, F[c]).mean()),
                  'mz_a': mz['a'], 'mz_b': mz['b'], 'mz_se_a': mz['se_a'], 'mz_se_b': mz['se_b'], 'mz_r2': mz['r2'],
                  'mz_p': mz['p']}
        if c != 'logHAR':
            dq = T.dm_test(T.qlike(y, F['logHAR']), T.qlike(y, F[c]))
            dm = T.dm_test(T.mse(y, F['logHAR']), T.mse(y, F[c]))
            out[c].update({'dm_q_t': dq['t'], 'dm_q_p': dq['p'], 'dm_m_t': dm['t'], 'dm_m_p': dm['p']})
    out['T'] = int(len(F))
    out['start'] = str(F.index[0].date())
    return out


def fig_oos(F, y, Fb, yb):
    """SPY 2022-2026: volatilitatea realizata (inclusiv noaptea) si prognozele log-HAR si GARCH-t; pierderea QLIKE cumulata."""
    fig, axes = plt.subplots(2, 1, figsize=(9.6, 5.0), gridspec_kw={'height_ratios': [1.5, 1]})
    axes[0].plot(y.index, ann(y, 252), color=Teal, lw=0.6, label='SPY realised volatility incl. overnight (% p.a.)')
    axes[0].plot(F.index, ann(F['GARCH-t'], 252), color=MainBlue, lw=1.0, label='GARCH(1,1)-t forecast')
    axes[0].plot(F.index, ann(F['logHAR'], 252), color=IDAred, lw=1.0, label='log-HAR forecast')
    axes[0].set_ylabel('% p.a.')
    axes[0].set_ylim(0, 80)
    for c in ['GARCH-t', 'EWMA', 'HAR']:
        d = (T.qlike(y, F[c]) - T.qlike(y, F['logHAR'])).cumsum()
        axes[1].plot(d.index, d.values, color=MODEL_COL[c], lw=1.1, label=f'Cumulative QLIKE: {c} minus log-HAR (SPY)')
    for c in ['GARCH-t']:
        d = (T.qlike(yb, Fb[c]) - T.qlike(yb, Fb['logHAR'])).cumsum()
        axes[1].plot(d.index, d.values, color=Amber, lw=1.1, ls='--', label='Cumulative QLIKE: GARCH-t minus log-HAR (Bitcoin)')
    axes[1].axhline(0, color=Gray, lw=0.6)
    axes[1].set_ylabel('Cumulative loss difference')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    save_fig('ch9_oos')


def fig_mz(F, y):
    """Regresiile Mincer-Zarnowitz pe scara log: log-HAR si GARCH-t (SPY, 2022-2026)."""
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.3), sharey=True)
    for ax, c in zip(axes, ['logHAR', 'GARCH-t']):
        ax.scatter(F[c], y, s=4, color=MODEL_COL[c], alpha=0.5, label=f'{c}: forecast vs realised variance')
        lim = [min(F[c].min(), y.min()), max(F[c].max(), y.max())]
        ax.plot(lim, lim, color=Gray, lw=0.8, ls='--', label='45-degree line (unbiased forecast)')
        mz = T.mz_test(y, F[c])
        xx = np.linspace(F[c].min(), F[c].max(), 50)
        ax.plot(xx, mz['a'] + mz['b'] * xx, color='black', lw=1.0, label='Mincer-Zarnowitz fitted line')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Forecast (%$^2$)')
        ax.set_title(c, fontsize=9, loc='left')
    axes[0].set_ylabel('Realised variance (%$^2$)')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.12, 1, 1))
    save_fig('ch9_mz')


# =============================================================================
# 11. VOLATILITATE ASPRA
# =============================================================================
def rough_H(logsig, qs=(0.5, 1.0, 1.5, 2.0, 3.0), lags=range(1, 31)):
    """H = panta dreptei zeta_q = q H, prin origine."""
    ro = T.roughness(logsig, qs, lags)
    q = np.array(qs)
    z = np.array([ro['zeta'][x] for x in qs])
    ro['H'] = float(np.sum(q * z) / np.sum(q * q))
    return ro


def fig_rough():
    """log m(q, Delta) vs log Delta pentru log-volatilitatea SPY; pantele zeta_q = q H."""
    ro = rough_H(0.5 * np.log(RVT_SPY.values))
    rb = rough_H(0.5 * np.log(RV_BTC.asfreq('D').interpolate().values))
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.2), gridspec_kw={'width_ratios': [1.4, 1]})
    cols = [MainBlue, Forest, Amber, Purple, IDAred]
    for q, c in zip(ro['m'], cols):
        axes[0].plot(np.log(ro['lags']), np.log(ro['m'][q]), 'o', ms=2.5, color=c, label=f'q = {q:g}')
        fit = np.polyfit(np.log(ro['lags']), np.log(ro['m'][q]), 1)
        axes[0].plot(np.log(ro['lags']), np.polyval(fit, np.log(ro['lags'])), color=c, lw=0.8)
    axes[0].set_xlabel(r'log $\Delta$ (days)')
    axes[0].set_ylabel(r'log $m(q, \Delta)$')
    qs = np.array(list(ro['zeta']))
    axes[1].plot(qs, [ro['zeta'][q] for q in qs], 'o-', color=MainBlue, label=f'SPY: slopes, H = {ro["H"]:.2f}')
    axes[1].plot(qs, [rb['zeta'][q] for q in qs], 's--', color=Amber, label=f'Bitcoin: slopes, H = {rb["H"]:.2f}')
    axes[1].plot(qs, 0.5 * qs, color=Gray, ls=':', lw=0.9, label='Brownian motion: H = 0.5')
    axes[1].set_xlabel('q')
    axes[1].set_ylabel(r'Slope $\zeta_q$')
    fig_legend_bottom(fig, ncol=4, y=0.02)
    plt.tight_layout(rect=(0, 0.12, 1, 1))
    save_fig('ch9_rough')
    return {'H_spy': ro['H'], 'H_btc': rb['H'], 'zeta2_spy': float(ro['zeta'][2.0]), 'zeta1_spy': float(ro['zeta'][1.0])}


# =============================================================================
if __name__ == '__main__':
    res = {}
    print('1. intraday day');   res['day'] = fig_intraday_day()
    print('2. rv series');      res['series'] = fig_rv_series()
    print('   overnight');      res['overnight'] = fig_overnight()
    print('3. rv ci');          res['ci'] = fig_rv_ci()
    print('4. seasonality');    res['season'] = fig_seasonality()
    print('5. noise sim');      res['noise'] = fig_noise_simulation()
    print('   signature');      res['sig'] = fig_signature()
    print('6. jumps');          res['jumps'] = fig_jumps()
    print('7. distributions');  res['dist'] = fig_distributions()
    print('   acf');            res['acf'] = fig_acf()
    print('8. vix');            res['vix'] = fig_vix()
    print('9. har');            res['har'] = har_tables(); res['harw'] = fig_har(res['har'])
    print('10. oos')
    F, y = oos_forecasts(RVT_SPY, D_SPY, OOS_SPY, False)
    Fb, yb = oos_forecasts(RV_BTC, D_BTC, OOS_BTC, True)
    res['oos_spy'] = evaluate(F, y)
    res['oos_btc'] = evaluate(Fb, yb)
    F.assign(proxy=y).to_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'))
    Fb.assign(proxy=yb).to_csv(os.path.join(HERE, 'ch9_forecasts_btc.csv'))
    fig_oos(F, y, Fb, yb)
    fig_mz(F, y)
    print('11. rough');         res['rough'] = fig_rough()
    pd.DataFrame({'rv_intraday': RV_SPY, 'overnight': ON, 'rv_total': RVT_SPY}).to_csv(os.path.join(HERE, 'ch9_rv_spy.csv'))
    RV_BTC.rename('rv').to_csv(os.path.join(HERE, 'ch9_rv_btc.csv'))
    with open(os.path.join(HERE, 'ch9_results.json'), 'w') as f:
        json.dump(jsonable(res), f, indent=1)
    print('saved ch9_results.json')

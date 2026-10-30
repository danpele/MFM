"""
integrated_cases.py -- three integrated case studies of Chapter 19 (MFM)
=======================================================================
Each study takes one question from the data to a decision with the code of several chapters of the course.
The chapters' own modules are imported read-only (their folders are put on sys.path one at a time, their save
functions are replaced by no-ops, so no chart or result file of another chapter is written).

  1. portfolio_case()  -- eight multi-asset ETFs: sample vs Ledoit-Wolf GMV weights (Ch. 4), GARCH + DCC conditional
                          covariance (Ch. 6), portfolio VaR 1% / ES 2.5% and Euler risk contributions (Ch. 7),
                          Kupiec and Christoffersen backtests (Ch. 8)
  2. bitcoin_case()    -- stylised facts (Ch. 1), realised variance from 5-minute bars and log-HAR forecasts (Ch. 9),
                          VaR 1% backtest (Ch. 8), spreads and Amihud illiquidity (Ch. 10), PSY bubble test (Ch. 17)
  3. romania_case()    -- a RON investor holding the BET and the Euro Stoxx 50: variance-ratio tests (Ch. 2),
                          factor exposures with Newey-West errors (Ch. 3), GARCH volatility (Ch. 5), rolling
                          minimum-variance currency hedge (Ch. 6), historical VaR / ES of the hedging choices (Ch. 7)

Output: Quantlets/Ch_19/ch19_integrated.json, ch19_int_{pf,btc,ron}.csv, charts/ch19_int_{portfolio,bitcoin,romania}.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import importlib.util
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
QL = os.path.dirname(HERE)
CHART_DIR = os.environ.get('MFM_CHART_DIR', os.path.join(QL, '..', 'charts'))   # notebooks: their own output folder
OUT_DIR = os.environ.get('MFM_OUT_DIR', HERE)                                       # CSV and JSON results
sys.path.insert(0, QL)
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides

plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'], 'font.size': 9,
                     'axes.labelsize': 9, 'axes.titlesize': 9, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.6, 'lines.linewidth': 1.1,
                     'legend.facecolor': 'none', 'legend.framealpha': 0, 'legend.fontsize': 8})
MainBlue, IDAred, Forest, Amber, Orange = '#1A3A6E', '#CD0000', '#2E7D32', '#B5853F', '#E67E22'
Purple, Navy, BandBlue, Teal, Brown = '#8E44AD', '#1F2A44', '#C5D2E8', '#17A2B8', '#795548'

A_VAR, A_ES = 0.01, 0.025
END = '2026-09-18'


# =============================================================================
# Importing the chapters' modules read-only
# =============================================================================
_MODS = {}


def chapter(ch, name):
    """Module `name` of Quantlets/Ch_<ch>, imported under a private name; its sibling imports (mfm_data, ...) are
    resolved inside its own folder and then removed from sys.modules so that chapters do not collide."""
    key = (ch, name)
    if key in _MODS:
        return _MODS[key]
    folder = os.path.join(QL, f'Ch_{ch:02d}')
    local = {f[:-3] for f in os.listdir(folder) if f.endswith('.py')}
    saved = {k: sys.modules.pop(k) for k in list(sys.modules) if k in local}
    sys.path.insert(0, folder)
    try:
        spec = importlib.util.spec_from_file_location(f'_mfm_ch{ch}_{name}', os.path.join(folder, name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(folder)
        for k in list(sys.modules):
            if k in local:
                _MODS.setdefault((ch, k), sys.modules[k])
                del sys.modules[k]
        sys.modules.update(saved)
    for f in ('save_fig', 'savefig', 'save'):
        if hasattr(mod, f):
            setattr(mod, f, lambda *a, **k: None)      # never write another chapter's charts or results
    _MODS[key] = mod
    return mod


def save_fig(name):
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print('   saved', name)


def backtest(loss, var, ch8, calendar=False):
    """Kupiec (coverage) and Christoffersen (independence, conditional coverage), Chapter 8 code.
    calendar=True: the evaluation days have gaps (days without a forecast); the independence test then uses only
    the transitions between consecutive calendar days, so no pair spans a gap."""
    hit = (loss > var).astype(int)
    k = ch8.kupiec(hit.values, A_VAR)
    if calendar:
        d = hit.index
        ok = np.asarray((d[1:] - d[:-1]) == pd.Timedelta('1D'))
        a, b = hit.values[:-1][ok], hit.values[1:][ok]
        n = dict(n00=int(np.sum((a == 0) & (b == 0))), n01=int(np.sum((a == 0) & (b == 1))),
                 n10=int(np.sum((a == 1) & (b == 0))), n11=int(np.sum((a == 1) & (b == 1))))
        c = ch8.christoffersen_from_counts(**n, p=A_VAR)
        c['p_cc'] = float(stats.chi2.sf(k['LR'] + c['LR_ind'], 2))      # LR_uc on all days + LR_ind on the pairs
        extra = dict(pairs=int(ok.sum()), gaps=int((~ok).sum()))
    else:
        c, extra = ch8.christoffersen(hit.values, A_VAR), {}
    return dict(T=int(k['T']), x=int(k['x']), rate=float(k['rate']), p_uc=float(k['p']),
                p_ind=float(c['p_ind']), p_cc=float(c['p_cc']), expected=float(A_VAR * k['T']), **extra)


# =============================================================================
# 1. MULTI-ASSET PORTFOLIO: Ch. 4 -> Ch. 6 -> Ch. 7 -> Ch. 8
# =============================================================================
CLASSES = {'Equities': ['SPY', 'EFA', 'EEM'], 'Treasuries': ['TLT', 'IEF'], 'Credit': ['LQD', 'HYG'], 'Gold': ['GLD']}
FHS_WINDOW = 1000          # days of standardised portfolio returns behind the FHS quantile
HS_WINDOW = 500            # days behind the historical-simulation benchmark


def _garch_fixed(r100, params, ch6):
    """GARCH(1,1) of Chapter 6 (constant mean, Normal QML) run with fixed parameters on r100 (returns in %)."""
    from arch import arch_model
    res = arch_model(r100, mean='Constant', vol='GARCH', p=1, q=1, dist='normal').fix(params)
    return res.conditional_volatility, res.resid / res.conditional_volatility


def portfolio_case():
    G4 = chapter(4, 'generate_all_charts')
    D6 = chapter(6, 'dep_tools')
    M8 = chapter(8, 'mfm_data')
    RM = chapter(7, 'risk_measures')
    assets = list(G4.MULTI)
    # Step 1 (Ch. 4): monthly 60-month rolling GMV weights, sample covariance vs Ledoit-Wolf shrinkage
    R, Rex, rf = G4.us_monthly(assets)
    ret, to, Wd = G4.backtest(R, Rex, strategies=['GMV', 'GMV-LW'])
    deltas = pd.Series([G4.lw_cc(Rex.values[t - G4.WINDOW:t])[1] for t in range(G4.WINDOW, len(Rex))],
                       index=Rex.index[G4.WINDOW:])
    # daily simple returns of the eight ETFs (adjusted close, common days)
    P = G4.prices([a + '.US' for a in assets]).loc[:END]
    P.columns = assets
    lr = np.log(P).diff().dropna()
    sr = np.exp(lr) - 1
    first = Wd['GMV'].index[0].to_period('M').start_time
    last = Wd['GMV'].index[-1]
    days = sr.loc[first:last].index
    month = days.to_period('M')
    W = {s: Wd[s].copy() for s in Wd}
    for s in W:
        W[s].index = W[s].index.to_period('M')
    # monthly rebalancing: the target weights on the first day of each month, then the weights drift with the prices
    # until the next rebalancing; Wt[s][i] = weights at the start of day i (known before the day's returns)
    Rd = sr.loc[days].values
    Wt, rp = {}, {}
    for s in W:
        cur, prev_m, ws, g = None, None, np.empty_like(Rd), np.empty(len(days))
        for i, m in enumerate(month):
            if m != prev_m:
                cur, prev_m = W[s].loc[m].values.copy(), m
            ws[i] = cur
            g[i] = cur @ Rd[i]
            cur = cur * (1 + Rd[i]) / (1 + g[i])
        Wt[s], rp[s] = ws, 100 * g
    rp = pd.DataFrame(rp, index=days)
    # the comparison of the two GMV variants on the whole evaluation is retrospective; an operational choice uses
    # only earlier data: here the first half of the evaluation selects, the second half tests
    split = '2019-01-01'
    halves = {'select': rp.loc[rp.index < split], 'test': rp.loc[rp.index >= split]}
    step1 = dict(start=str(days[0].date()), end=str(days[-1].date()), n_days=int(len(days)),
                 months=int(len(Wd['GMV'])), window=int(G4.WINDOW),
                 vol={s: float(rp[s].std() * np.sqrt(252)) for s in rp},
                 vol_m={s: float(ret[s].std() * np.sqrt(12) * 100) for s in ret},
                 turnover={s: float(to[s].mean()) for s in to},
                 maxw={s: float(Wd[s].abs().max(axis=1).mean()) for s in Wd},
                 delta_mean=float(deltas.mean()), delta_min=float(deltas.min()), delta_max=float(deltas.max()),
                 gross={s: float(Wd[s].abs().sum(axis=1).mean()) for s in Wd},
                 gross_max={s: float(Wd[s].abs().sum(axis=1).max()) for s in Wd},
                 gross_max_daily={s: float(np.abs(Wt[s]).sum(axis=1).max()) for s in Wd},
                 w_last={s: {a: float(v) for a, v in Wd[s].iloc[-1].items()} for s in Wd},
                 split=split, select_end=str(halves['select'].index[-1].date()),
                 vol_select={s: float(halves['select'][s].std() * np.sqrt(252)) for s in rp},
                 vol_test={s: float(halves['test'][s].std() * np.sqrt(252)) for s in rp})
    choice = 'GMV-LW' if step1['vol']['GMV-LW'] <= step1['vol']['GMV'] else 'GMV'
    step1['choice'] = choice                  # retrospective: lower volatility over the whole evaluation
    step1['choice_select'] = 'GMV-LW' if step1['vol_select']['GMV-LW'] <= step1['vol_select']['GMV'] else 'GMV'
    # Step 2 (Ch. 6): GARCH(1,1) + DCC(1,1), re-estimated each January on all earlier data, filtered with fixed
    # parameters through the year: one-day-ahead conditional covariance H_t
    years = sorted(set(days.year))
    H = pd.Series(dtype=object)
    Hd = {}
    fits = {}
    r100 = 100 * lr
    for y in [years[0] - 1] + years:
        est = lr.loc[:f'{y}-12-31'] if y == years[0] - 1 else lr.loc[:f'{y - 1}-12-31']
        Pg, V, Z, ll = D6.garch_all(est)
        dcc = D6.dcc_fit(Z)
        fits[y] = dict(a=float(dcc['a']), b=float(dcc['b']), n=int(len(est)))
        if y == years[0] - 1:          # in-sample covariances before the first evaluation year (FHS history)
            Rt = dcc['R']
            for i, d in enumerate(est.index):
                Hd[d] = np.outer(V.iloc[i].values, V.iloc[i].values) * Rt[i]
            continue
        upto = r100.loc[:f'{y}-12-31']
        vols, zs = {}, {}
        for a in assets:
            v, z = _garch_fixed(upto[a], Pg[a], D6)
            vols[a], zs[a] = v, z
        Vf, Zf = pd.DataFrame(vols)[assets], pd.DataFrame(zs)[assets]
        Rt = D6.dcc_path(Zf.values, dcc['a'], dcc['b'], dcc['Qbar'])
        sel = np.where(Zf.index.year == y)[0]
        for i in sel:
            Hd[Zf.index[i]] = np.outer(Vf.iloc[i].values, Vf.iloc[i].values) * Rt[i]
        print('   DCC', y, round(dcc['a'], 4), round(dcc['b'], 4))
    hdates = pd.DatetimeIndex(sorted(Hd))
    Harr = np.array([Hd[d] for d in hdates])
    hpos = {d: i for i, d in enumerate(hdates)}
    # Step 3 (Ch. 7): portfolio VaR 1% / ES 2.5%: DCC-Normal, DCC-FHS (quantile of standardised portfolio returns
    # with today's weights over the last 1000 days) and historical simulation (500 days); Euler contributions
    zq, zes = stats.norm.ppf(1 - A_VAR), stats.norm.pdf(stats.norm.ppf(A_ES)) / A_ES
    rows = []
    u_sd = []                  # in-window sd of the standardised portfolio returns (today's weights on past data)
    share_rows = []
    w_all = W[choice]
    hidx = {d: i for i, d in enumerate(hdates)}
    sidx = {d: i for i, d in enumerate(sr.index)}
    SR = sr.values
    for i, d in enumerate(days):
        w = Wt[choice][i]                      # weights at the start of day d
        Hm = Harr[hpos[d]]
        sig = float(np.sqrt(w @ Hm @ w))
        k = hidx[d]
        Hp = Harr[max(0, k - FHS_WINDOW):k]
        past = hdates[max(0, k - FHS_WINDOW):k]
        sp = np.sqrt(np.einsum('i,tij,j->t', w, Hp, w))
        u = (100 * (sr.loc[past].values @ w)) / sp
        Lu = -u
        v_u, e_u = RM.hs_var_es(Lu, A_VAR)[0], RM.hs_var_es(Lu, A_ES)[1]
        j = sidx[d]
        Lh = -100 * (SR[max(0, j - HS_WINDOW):j] @ w)
        v_h, e_h = RM.hs_var_es(Lh, A_VAR)[0], RM.hs_var_es(Lh, A_ES)[1]
        u_sd.append(float(np.std(u, ddof=1)))
        sh = G4.risk_contrib(w, Hm)
        share_rows.append({c: float(sum(sh[assets.index(a)] for a in A)) for c, A in CLASSES.items()})
        rows.append(dict(date=d, ret=rp.loc[d, choice], sig=sig, var_n=zq * sig, es_n=zes * sig,
                         var_fhs=v_u * sig, es_fhs=e_u * sig, var_hs=v_h, es_hs=e_h))
    F = pd.DataFrame(rows).set_index('date')
    S = pd.DataFrame(share_rows, index=days)
    F = F.join(S)
    loss = -F['ret']
    step3 = {}
    for k in ('n', 'fhs', 'hs'):
        step3[k] = backtest(loss, F['var_' + k], M8)
        step3[k].update(var_mean=float(F['var_' + k].mean()), var_last=float(F['var_' + k].iloc[-1]),
                        es_last=float(F['es_' + k].iloc[-1]), es_mean=float(F['es_' + k].mean()))
    peak = F['sig'].idxmax()
    wpk = dict(zip(assets, Wt[choice][days.get_loc(peak)]))
    shares = dict(mean={c: float(S[c].mean()) for c in CLASSES}, last={c: float(S[c].iloc[-1]) for c in CLASSES},
                  peak={c: float(S.loc[peak, c]) for c in CLASSES}, peak_date=str(peak.date()),
                  w_peak={c: float(sum(wpk[a] for a in A)) for c, A in CLASSES.items()},
                  w_mean={c: float(sum(w_all[a].mean() for a in A)) for c, A in CLASSES.items()})
    a_b = {str(y): fits[y] for y in fits}
    out = dict(step1=step1, dcc=a_b, dcc_last=fits[years[-1]], step3=step3, shares=shares,
               sig_peak=float(F['sig'].max()), sig_last=float(F['sig'].iloc[-1]),
               last_date=str(days[-1].date()), worst=float(loss.max()), worst_date=str(loss.idxmax().date()),
               u_sd_mean=float(np.mean(u_sd)), u_sd_min=float(np.min(u_sd)), u_sd_max=float(np.max(u_sd)),
               oos_z_sd=float((F['ret'] / F['sig']).std()))
    rp_roll = rp.rolling(252).std() * np.sqrt(252)
    F = F.join(rp_roll.rename(columns={'GMV': 'vol_gmv', 'GMV-LW': 'vol_lw'}))
    F.to_csv(os.path.join(OUT_DIR, 'ch19_int_pf.csv'), float_format='%.6g')
    return out, F


def fig_portfolio(F, R):
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))
    a = ax[0]
    a.plot(F.index, F['vol_gmv'], color=Orange, lw=0.9, label='GMV, sample covariance')
    a.plot(F.index, F['vol_lw'], color=MainBlue, lw=0.9, label='GMV, Ledoit-Wolf shrinkage')
    a.set_ylabel('1-year volatility (%)')
    a.set_title('(a) Ch. 4: GMV risk', loc='left')
    a = ax[1]
    L = -F['ret']
    a.plot(F.index, L.clip(lower=0), color=BandBlue, lw=0.5, label=f'Daily loss of {R["step1"]["choice"]}')
    a.plot(F.index, F['var_n'], color=IDAred, lw=0.8, label='VaR 1%, DCC-Normal')
    a.plot(F.index, F['var_fhs'], color=Forest, lw=0.8, label='VaR 1%, DCC-FHS')
    hit = L > F['var_n']
    a.scatter(F.index[hit], L[hit], s=6, color=Navy, zorder=3, label='Loss above DCC-Normal VaR')
    a.set_ylabel('Loss, VaR (%)')
    a.set_title('(b) Ch. 6-8: VaR 1%', loc='left')
    a = ax[2]
    m = F[list(CLASSES)].resample('ME').mean()
    for c, col in zip(CLASSES, (Purple, Teal, Amber, Brown)):
        a.plot(m.index, 100 * m[c], color=col, lw=1.0, label=f'{c}')
    a.axhline(0, color=Navy, lw=0.5)
    a.set_ylabel('Share of risk (%)')
    a.set_title('(c) Ch. 7: Euler shares', loc='left')
    for a in ax:
        a.tick_params(labelsize=7)
    h, l = [], []
    for a in ax:
        for hh, ll in zip(*a.get_legend_handles_labels()):
            h.append(hh)
            l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=5, frameon=False, fontsize=7)
    plt.tight_layout()
    save_fig('ch19_int_portfolio')


# =============================================================================
# 2. BITCOIN: Ch. 1 -> Ch. 9 -> Ch. 8 -> Ch. 10 -> Ch. 17
# =============================================================================
def bitcoin_case():
    G1 = chapter(1, 'generate_all_charts')
    M1 = chapter(1, 'mfm_data')
    M9 = chapter(9, 'mfm_data')
    T9 = chapter(9, 'rv_tools')
    M8 = chapter(8, 'mfm_data')
    RM = chapter(7, 'risk_measures')
    G10 = chapter(10, 'generate_all_charts')
    M10 = chapter(10, 'mfm_data')
    U10 = chapter(10, 'micro')
    G17 = chapter(17, 'generate_all_charts')
    # Step 1 (Ch. 1): stylised facts of daily Bitcoin returns, 2014-2026
    close = M1.load_data('btc')['Close'].loc[:END]
    r = 100 * M1.log_returns(close)
    k = int(0.025 * len(r))
    hill = float(G1.hill_estimator(-r.values, k))
    z = r - r.mean()
    acf_abs = float(np.corrcoef(np.abs(r.values[1:]), np.abs(r.values[:-1]))[0, 1])
    acf_r = float(np.corrcoef(r.values[1:], r.values[:-1])[0, 1])
    step1 = dict(T=int(len(r)), start=str(r.index[0].date()), end=str(r.index[-1].date()), hill=hill, k=k,
                 vol=float(r.std() * np.sqrt(365)), acf_abs=acf_abs, acf_r=acf_r,
                 n4=int((np.abs(z / r.std()) > 4).sum()), n4_normal=float(len(r) * 2 * stats.norm.sf(4)))
    # Step 2 (Ch. 9): realised variance from 5-minute bars (UTC days) and log-HAR forecasts, expanding window
    P = M9.btc_intraday()
    RV = T9.rv(M9.intraday_returns(P))
    rday = 100 * np.log(P.iloc[:, -1] / P[0])
    OOS = '2025-03-01'
    fc = T9.har_expanding(RV, OOS, calendar=True, log=True)
    ref = pd.read_csv(os.path.join(QL, 'Ch_09', 'ch9_forecasts_btc.csv'), index_col=0, parse_dates=True)['logHAR']
    common = fc.index.intersection(ref.index)
    fit, X, ok = T9.har_fit(RV, calendar=True, log=True)
    step2 = dict(rv_start=str(RV.index[0].date()), rv_end=str(RV.index[-1].date()), n_rv=int(len(RV)),
                 rv_vol_mean=float(np.sqrt(365 * RV).mean()), b=[float(x) for x in fit['b']],
                 se=[float(x) for x in fit['se']], r2=float(fit['r2']), oos=OOS, n_oos=int(len(fc)),
                 max_diff_ch9=float((fc.loc[common] - ref.loc[common]).abs().max()), n_ch9=int(len(common)))
    # Step 3 (Ch. 7-8): VaR 1% = z_0.99 sqrt(forecast) against historical simulation on 500 UTC days, backtested
    zq = stats.norm.ppf(1 - A_VAR)
    var_har = zq * np.sqrt(fc)
    daily = M9.daily_returns('btc', start='2014-09-17')        # daily closes (UTC days) for the HS history
    var_hs = pd.Series({d: RM.hs_var_es(-daily.loc[:d - pd.Timedelta('1D')].values[-500:], A_VAR)[0]
                        for d in fc.index})
    corr_day = float(pd.concat([rday, daily], axis=1).dropna().corr().iloc[0, 1])
    idx = var_har.index.intersection(rday.dropna().index).intersection(var_hs.index)
    L = -rday.loc[idx]
    stdz = (rday.loc[idx] / np.sqrt(fc.loc[idx]))
    # the evaluation days are the days with a log-HAR forecast (complete 5-minute bars): calendar days without one
    # are missing; on those days the limit falls back to the HS VaR, backtested on daily (close-to-close) losses
    cal = pd.date_range(idx[0], idx[-1], freq='D')
    lim = var_har.reindex(cal).fillna(var_hs.reindex(cal))
    if lim.isna().any():
        lim = lim.fillna(pd.Series({d: RM.hs_var_es(-daily.loc[:d - pd.Timedelta('1D')].values[-500:], A_VAR)[0]
                                    for d in cal[lim.isna()]}))
    Lc = -daily.reindex(cal)
    step3 = dict(har=backtest(L, var_har.loc[idx], M8, calendar=True), hs=backtest(L, var_hs.loc[idx], M8, calendar=True),
                 n_cal=int(len(cal)), n_missing=int(len(cal) - len(idx)),
                 fallback=backtest(Lc.dropna(), lim.loc[Lc.dropna().index], M8, calendar=True),
                 var_har_mean=float(var_har.loc[idx].mean()), var_hs_mean=float(var_hs.loc[idx].mean()),
                 var_har_last=float(var_har.iloc[-1]), var_hs_last=float(var_hs.iloc[-1]),
                 var_har_min=float(var_har.loc[idx].min()), var_har_max=float(var_har.loc[idx].max()),
                 last=str(var_har.index[-1].date()), z_sd=float(stdz.std()), z_kurt=float(stats.kurtosis(stdz)),
                 z_q01=float(np.quantile(stdz, 0.01)), n_hs=int(len(var_hs)), corr_day=corr_day,
                 first=str(idx[0].date()))
    # Step 4 (Ch. 10): spread estimators from daily data and Amihud illiquidity, last two years; monthly Amihud
    sp = G10.daily_spreads('BTC', start=G10.START2)
    ami = U10.amihud(M10.returns('BTC', G10.START2), M10.dollar_volume('BTC', G10.START2))
    ami_spy = U10.amihud(M10.returns('SPY', G10.START2), M10.dollar_volume('SPY', G10.START2))
    ill = G10.monthly_illiq(['BTC', 'SPY'], start=G10.START10)
    step4 = dict(roll=float(sp['roll']), cs=float(sp['cs']), edge=float(sp['edge']), ar=float(sp['ar']),
                 amihud=float(ami), amihud_spy=float(ami_spy),
                 ill_first=float(ill['BTC'].iloc[:12].mean()), ill_last=float(ill['BTC'].iloc[-12:].mean()),
                 ill_first_year=str(ill.index[0].year), ill_last_year=str(ill.index[-1].year))
    # Step 5 (Ch. 17): PSY GSADF test and BSADF date-stamping on weekly log prices, Monte Carlo critical values
    # two calibrations of the critical values, as in Chapter 17: Monte Carlo under a homoskedastic random walk and
    # the wild bootstrap (robust to the changes in volatility); the robust reading uses the wild bootstrap
    y = np.log(G17.price('btc', 'W'))
    o = G17.run_psy(y, wild=True)
    summ = G17.summarise(o, y)
    bs = pd.Series(o['res']['bsadf'], index=o['idx'])
    cv_mc = pd.Series(o['cv']['bsadf95'], index=o['idx'])
    cv = pd.Series(o['wild']['bsadf95'], index=o['idx'])
    step5 = dict(T=summ['T'], gsadf=summ['gsadf'], cv95=summ['cv_gsadf_wild'], cv95_mc=summ['cv_gsadf']['95'],
                 episodes=summ['episodes_wild'], episodes_mc=summ['episodes'],
                 bsadf_last=float(bs.iloc[-1]), cv_last=float(cv.iloc[-1]), cv_last_mc=float(cv_mc.iloc[-1]),
                 start=summ['start'], end=summ['end'],
                 weeks_above_since_2022=int(((bs > cv) & (bs.index >= '2022-01-01')).sum()),
                 weeks_above_since_2022_mc=int(((bs > cv_mc) & (bs.index >= '2022-01-01')).sum()),
                 bsadf_max_since_2022=float(bs.loc['2022':].max()),
                 bsadf_max_date_since_2022=str(bs.loc['2022':].idxmax().date()))
    out = dict(step1=step1, step2=step2, step3=step3, step4=step4, step5=step5)
    D = pd.DataFrame({'rv_vol': np.sqrt(365 * RV), 'fc_vol': np.sqrt(365 * fc), 'var_har': var_har,
                      'var_hs': var_hs, 'loss': -rday}).loc[RV.index[0]:]
    W = pd.DataFrame({'logp': y, 'bsadf': bs, 'cv95': cv, 'cv95_mc': cv_mc})
    M = ill.rename(columns={'BTC': 'ill_btc', 'SPY': 'ill_spy'})
    D.to_csv(os.path.join(OUT_DIR, 'ch19_int_btc.csv'), float_format='%.6g')
    W.to_csv(os.path.join(OUT_DIR, 'ch19_int_btc_weekly.csv'), float_format='%.6g')
    M.to_csv(os.path.join(OUT_DIR, 'ch19_int_btc_illiq.csv'), float_format='%.6g')
    return out, D, W, M


def fig_bitcoin(D, W, M, ep):
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))
    a = ax[0]
    a.plot(W.index, W['bsadf'], color=MainBlue, lw=0.8, label='BSADF statistic (weekly)')
    a.plot(W.index, W['cv95'], color=IDAred, lw=0.8, ls='--', label='95% critical value, wild bootstrap')
    a.plot(W.index, W['cv95_mc'], color=Purple, lw=0.7, ls=':', label='95% critical value, Monte Carlo')
    for e in ep:
        a.axvspan(pd.Timestamp(e['start']), pd.Timestamp(e['end'] or W.index[-1]), color=BandBlue, lw=0,
                  label='Explosive episode' if e is ep[0] else None)
    a.set_ylabel('ADF statistic')
    a.set_title('(a) Ch. 17: BSADF', loc='left')
    a = ax[1]
    x = D.loc[D['var_har'].first_valid_index():].asfreq('D')        # missing days stay as gaps in the lines
    a.plot(x.index, x['loss'].clip(lower=0), color=BandBlue, lw=0.6, label='Daily loss (UTC day)')
    a.plot(x.index, x['var_har'], color=IDAred, lw=0.9, label='VaR 1%, log-HAR forecast')
    a.plot(x.index, x['var_hs'], color=Forest, lw=0.9, label='VaR 1%, HS 500 days')
    hit = x['loss'] > x['var_har']
    a.scatter(x.index[hit], x['loss'][hit], s=8, color=Navy, zorder=3, label='Loss above log-HAR VaR')
    a.set_ylabel('Loss, VaR (%)')
    a.set_title('(b) Ch. 8-9: VaR 1%', loc='left')
    import matplotlib.dates as mdates
    a.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(3, 9)))
    a.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    a = ax[2]
    a.semilogy(M.index, M['ill_btc'], color=Orange, lw=1.0, label='Bitcoin')
    a.semilogy(M.index, M['ill_spy'], color=MainBlue, lw=1.0, label='SPY')
    a.set_ylabel('bp per USD 1M (log)')
    a.set_title('(c) Ch. 10: Amihud', loc='left')
    for a in ax:
        a.tick_params(labelsize=7)
    h, l = [], []
    for a in ax:
        for hh, ll in zip(*a.get_legend_handles_labels()):
            h.append(hh)
            l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=5, frameon=False, fontsize=7)
    plt.tight_layout()
    save_fig('ch19_int_bitcoin')


# =============================================================================
# 3. ROMANIAN INVESTOR: Ch. 2 -> Ch. 3 -> Ch. 5 -> Ch. 6 -> Ch. 7
# =============================================================================
HEDGE_WINDOW = 156          # weeks behind the rolling minimum-variance hedge ratio (three years)
QS = list(range(2, 21))


def weekly(close):
    return np.log(close.resample('W-FRI').last().dropna()).diff().dropna()


def romania_case():
    M2 = chapter(2, 'mfm_data')
    E2 = chapter(2, 'eff_tests')
    M3 = chapter(3, 'mfm_data')
    G5 = chapter(5, 'garch_tools')
    RM = chapter(7, 'risk_measures')
    names = {'eurron': 'EUR/RON (BNR)', 'bet': 'BET', 'stoxx': 'Euro Stoxx 50'}
    cl = {k: M2.load_close(k, start='2005-07-01') for k in names}
    # Step 1 (Ch. 2): variance ratios with the heteroskedasticity-robust z*, daily returns; Chow-Denning
    vr = {}
    for k in names:
        r = np.log(cl[k]).diff().dropna()
        rows = [E2.variance_ratio(r.values, q) for q in QS]
        cd = E2.chow_denning(r.values)
        vr[k] = dict(T=int(len(r)), vr={str(q): float(v[0]) for q, v in zip(QS, rows)},
                     z={str(q): float(v[2]) for q, v in zip(QS, rows)}, cd=float(cd[0]), cd_p=float(cd[1]),
                     ac1=float(np.corrcoef(r.values[1:], r.values[:-1])[0, 1]))
    # weekly log returns (Friday closes): the three markets close at different times, so the weekly frequency
    # removes most of the non-synchronous trading
    w = pd.concat({k: weekly(cl[k]) for k in names}, axis=1).dropna()
    f = w['eurron']                          # EUR/RON change: > 0 = the leu depreciates
    s_ron = w['stoxx'] + f                   # Euro Stoxx 50 held by a RON investor, unhedged
    # Step 2 (Ch. 3): exposures, OLS with Newey-West errors
    b1, se1, t1, _, r21 = M3.ols_hac(w['stoxx'].values, f.values)
    b2, se2, t2, _, r22 = M3.ols_hac(w['bet'].values, np.column_stack([w['stoxx'].values, f.values]))
    step2 = dict(T=int(len(w)), start=str(w.index[0].date()), end=str(w.index[-1].date()),
                 stoxx_on_fx=dict(b=float(b1[1]), se=float(se1[1]), t=float(t1[1]), r2=float(r21)),
                 bet_on=dict(b_stoxx=float(b2[1]), se_stoxx=float(se2[1]), t_stoxx=float(t2[1]),
                             b_fx=float(b2[2]), se_fx=float(se2[2]), t_fx=float(t2[2]), r2=float(r22)),
                 corr_stoxx_fx=float(np.corrcoef(w['stoxx'], f)[0, 1]),
                 corr_bet_stoxx=float(np.corrcoef(w['bet'], w['stoxx'])[0, 1]))
    # Step 3 (Ch. 5): GARCH(1,1)-t on daily returns in %, persistence and annualised volatility today
    g = {}
    for k in names:
        r = 100 * np.log(cl[k]).diff().dropna()
        fit = G5.fit_garch(r, dist='t')
        g[k] = dict(persistence=float(fit.persistence), vol_now=float(fit.sigma.iloc[-1] * np.sqrt(252)),
                    vol_mean=float(r.std() * np.sqrt(252)), nu=float(fit.params['nu']),
                    half_life=float(G5.half_life(fit.persistence)))
    # Step 4 (Ch. 6): minimum-variance hedge of the euro leg: hedged return s_ron - h f, h* = Cov(s_ron, f)/Var(f),
    # on a rolling three-year window (known at the start of each week)
    cov = s_ron.rolling(HEDGE_WINDOW).cov(f)
    h_roll = (cov / f.rolling(HEDGE_WINDOW).var()).shift(1)
    h_full = float(np.cov(s_ron, f)[0, 1] / f.var())
    corr_roll = w['stoxx'].rolling(HEDGE_WINDOW).corr(f)
    # minimum-variance hedge of the whole 50/50 portfolio (linear approximation): Cov(b + s + f, f)/Var(f)
    h_pf = float(np.cov(w['bet'] + s_ron, f)[0, 1] / f.var())
    # Step 5 (Ch. 7): 50/50 portfolio of the BET and the Euro Stoxx 50 in RON, rebalanced weekly; three choices.
    # Exact simple returns: a forward on h times the euro leg's notional at the start of the week, zero carry,
    #   R_p = 0.5 (e^b - 1) + 0.5 [e^(s + f) - 1 - h (e^f - 1)],
    # and the loss in log points of the portfolio, L = -100 ln(1 + R_p)
    def port_ret(h):
        return 0.5 * np.expm1(w['bet']) + 0.5 * (np.expm1(w['stoxx'] + f) - h * np.expm1(f))
    port = {'Unhedged': np.log1p(port_ret(0.0)),
            'Hedged': np.log1p(port_ret(1.0)),
            'Min-variance hedge': np.log1p(port_ret(h_roll))}
    periods = {'full': (str(w.index[HEDGE_WINDOW + 1].date()), None), '2008': ('2008-08-01', '2012-12-31'),
               '2020': ('2020-01-01', None)}
    risk = {}
    for p, (a, b) in periods.items():
        risk[p] = {}
        for k, x in port.items():
            L = -100 * x.loc[a:b].dropna()
            L = L.loc[periods['full'][0]:]
            v, e = RM.hs_var_es(L.values, A_VAR)[0], RM.hs_var_es(L.values, A_ES)[1]
            risk[p][k] = dict(var=float(v), es=float(e), vol=float(L.std() * np.sqrt(52)), n=int(len(L)),
                              mean=float(-L.mean() * 52))
    risk_period = {p: [periods[p][0], periods[p][1] or str(w.index[-1].date())] for p in periods}
    cr = corr_roll.dropna()
    last_neg = cr.index[cr < 0][-1]
    step4 = dict(h_full=h_full, h_pf=h_pf, h_last=float(h_roll.iloc[-1]),
                 last_neg_corr_date=str(last_neg.date()), weeks_pos_since=int((cr.index > last_neg).sum()),
                 exit_date=str(cr.index[cr.index > last_neg][25].date()) if (cr.index > last_neg).sum() >= 26 else None, h_min=float(h_roll.min()), h_max=float(h_roll.max()),
                 h_min_date=str(h_roll.idxmin().date()), h_max_date=str(h_roll.idxmax().date()),
                 corr_last=float(corr_roll.iloc[-1]), share_neg_corr=float((corr_roll.dropna() < 0).mean()),
                 fx_vol=float(f.std() * np.sqrt(52) * 100), stoxx_vol=float(w['stoxx'].std() * np.sqrt(52) * 100),
                 fx_drift=float(f.mean() * 52 * 100))
    out = dict(step1=vr, step2=step2, step3=g, step4=step4, step5=risk, periods=risk_period,
               window=HEDGE_WINDOW)
    D = pd.DataFrame({'stoxx': w['stoxx'], 'bet': w['bet'], 'fx': f, 'h_roll': h_roll, 'corr_roll': corr_roll})
    D.to_csv(os.path.join(OUT_DIR, 'ch19_int_ron.csv'), float_format='%.6g')
    return out, D


BAR_LABEL = {'Unhedged': 'ES: unhedged (h = 0)', 'Min-variance hedge': 'ES: rolling h*', 'Hedged': 'ES: full hedge (h = 1)'}


def fig_romania(R, D):
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))
    a = ax[0]
    for k, col, lab in (('eurron', IDAred, 'EUR/RON (BNR)'), ('bet', MainBlue, 'BET'), ('stoxx', Forest, 'Euro Stoxx 50')):
        a.plot(QS, [R['step1'][k]['z'][str(q)] for q in QS], color=col, marker='o', ms=2.5, lw=0.9, label=lab)
    a.axhspan(-1.96, 1.96, color=BandBlue, lw=0, label='|z*| < 1.96')
    a.axhline(0, color=Navy, lw=0.5)
    a.set_xticks([2, 5, 10, 15, 20])
    a.set_xlabel('Horizon q (days)')
    a.set_ylabel('z*(q)')
    a.set_title('(a) Ch. 2: variance ratios', loc='left')
    a = ax[1]
    a.plot(D.index, D['h_roll'], color=Purple, lw=1.0, label='h*: min-variance, 3-year rolling')
    a.axhline(1, color=Navy, lw=0.6, ls='--', label='Full hedge (h = 1)')
    a.axhline(0, color=Navy, lw=0.5)
    a.set_ylabel('Hedge ratio h')
    a.set_title('(b) Ch. 3, 6: hedge ratio', loc='left')
    a = ax[2]
    ks = ['Unhedged', 'Min-variance hedge', 'Hedged']
    cols = [Orange, Purple, MainBlue]
    per = [('full', '2008-26'), ('2008', '2008-12'), ('2020', '2020-26')]
    xx = np.arange(len(per))
    for i, (k, c) in enumerate(zip(ks, cols)):
        a.bar(xx + (i - 1) * 0.26, [R['step5'][p][k]['es'] for p, _ in per], width=0.24, color=c, label=BAR_LABEL[k])
    a.set_xticks(xx, [lab for _, lab in per])
    a.set_ylabel('Weekly ES 2.5% (%)')
    a.set_title('(c) Ch. 7: ES in RON', loc='left')
    for a in ax:
        a.tick_params(labelsize=7)
    h, l = [], []
    for a in ax:
        for hh, ll in zip(*a.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh)
                l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=7)
    plt.tight_layout()
    save_fig('ch19_int_romania')


def add_power(RES):
    """Minimum detectable breach rate of the 5% Kupiec test at 80% power (Chapter 19, inference19.kupiec_mde)."""
    I19 = chapter(19, 'inference19')
    for key, steps in (('pf', ('n', 'fhs', 'hs')), ('btc', ('har', 'hs'))):
        if key in RES:
            for k in steps:
                b = RES[key]['step3'][k]
                b['mde'] = I19.kupiec_mde(b['T'])
                b['power2'] = I19.kupiec_power(b['T'], 0.02)[0]
    if 'btc' in RES:                          # longest run of weeks with BSADF above its critical value since 2022
        W = pd.read_csv(os.path.join(OUT_DIR, 'ch19_int_btc_weekly.csv'), index_col=0, parse_dates=True).loc['2022':]
        for col, key in (('cv95', 'max_run_since_2022'), ('cv95_mc', 'max_run_since_2022_mc')):
            if col not in W:
                continue
            run = best = 0
            for above in (W['bsadf'] > W[col]).values:
                run = run + 1 if above else 0
                best = max(best, run)
            RES['btc']['step5'][key] = int(best)


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, pd.Timestamp):
        return str(o.date())
    return o


if __name__ == '__main__':
    which = sys.argv[1:] if len(sys.argv) > 1 else ['pf', 'btc', 'ron']
    path = os.path.join(OUT_DIR, 'ch19_integrated.json')
    RES = json.load(open(path)) if os.path.exists(path) else {}
    if 'pf' in which:
        print('1. portfolio')
        RES['pf'], F = portfolio_case()
        fig_portfolio(F, RES['pf'])
    if 'btc' in which:
        print('2. bitcoin')
        RES['btc'], D, W, M = bitcoin_case()
        fig_bitcoin(D, W, M, RES['btc']['step5']['episodes'])
    if 'ron' in which:
        print('3. romania')
        RES['ron'], D = romania_case()
        fig_romania(RES['ron'], D)
    if 'plot' in which:                       # charts only, from the saved series
        rd = lambda f: pd.read_csv(os.path.join(OUT_DIR, f), index_col=0, parse_dates=True)
        fig_portfolio(rd('ch19_int_pf.csv'), RES['pf'])
        fig_bitcoin(rd('ch19_int_btc.csv'), rd('ch19_int_btc_weekly.csv'), rd('ch19_int_btc_illiq.csv'),
                    RES['btc']['step5']['episodes'])
        fig_romania(RES['ron'], rd('ch19_int_ron.csv'))
    add_power(RES)
    with open(path, 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved', path)

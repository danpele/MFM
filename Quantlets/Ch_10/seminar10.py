"""
seminar10.py -- Calculele Seminarului 10 (MFM): microstructura pietei
=====================================================================
Partea A: registrul de ordine, modelul Roll, Glosten-Milgrom, Kyle, Almgren-Chriss (pas cu pas).
Partea B: tiparul intrazilnic SPY, estimatori de spread la doua frecvente, iliciditatea si VIX,
          iliciditatea Amihud pe trei piete, relatia volum - miscare de pret, tiparul orar Bitcoin.
Partea C: prima de iliciditate (Amihud, 2002) pe BVB, in SUA si pe piata cripto.
Cifrele sunt salvate in sem10_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import ASSETS, GROUPS, LABELS, read_market, ohlc, returns, dollar_volume, intraday_spy, intraday_btc  # noqa: E402
from micro import roll_spread, cs_spread, ar_terms, walk_book, gm_quotes, kyle, ac_trajectory  # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Purple, Teal, Gray, GROUP_COL, save_fig,  # noqa: E402
                                 legend_outside_bottom, fig_legend_bottom, spy_tod, intraday_spreads, spread_table,
                                 amihud_table, spy_illiq_daily, sqrt_relation, jsonable, AC, START2, START10)

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42
B = 1000


def boot_days(values_by_day, stat, B=B, seed=SEED):
    """Bootstrap pe zile (blocuri = zile intregi): interval percentil de 95% pentru stat(esantion de zile)."""
    rng = np.random.default_rng(seed)
    days = np.array(list(values_by_day.keys()))
    out = []
    for _ in range(B):
        pick = rng.choice(days, len(days), replace=True)
        out.append(stat([values_by_day[d] for d in pick]))
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


# =============================================================================
# PARTEA A
# =============================================================================
BOOK_ASKS = [(100.02, 300), (100.03, 500), (100.05, 400), (100.08, 1000)]
BOOK_BIDS = [(99.98, 400), (99.97, 600), (99.95, 800), (99.90, 1500)]


def a1_walk():
    fills, vwap, rest, _ = walk_book(BOOK_ASKS, 1000)
    mid = (BOOK_ASKS[0][0] + BOOK_BIDS[0][0]) / 2
    return dict(fills=fills, vwap=vwap, mid=mid, spread=BOOK_ASKS[0][0] - BOOK_BIDS[0][0],
                spread_bp=1e4 * (BOOK_ASKS[0][0] - BOOK_BIDS[0][0]) / mid, cost_mid=vwap - mid,
                cost_mid_bp=1e4 * (vwap - mid) / mid, cost_ask=vwap - BOOK_ASKS[0][0], new_ask=rest[0][0],
                new_ask_q=rest[0][1], new_spread=rest[0][0] - BOOK_BIDS[0][0], total=vwap * 1000)


def a2_walk():
    fills, vwap, rest, _ = walk_book([(-p, q) for p, q in BOOK_BIDS], 1500)
    fills = [(-p, q) for p, q in fills]
    vwap = -vwap
    rest = [(-p, q) for p, q in rest]
    mid = (BOOK_ASKS[0][0] + BOOK_BIDS[0][0]) / 2
    # apoi: ordin limita de cumparare 500 @ 99.99 (in interiorul spread-ului)
    new_bid = 99.99
    return dict(fills=fills, vwap=vwap, cost_mid=mid - vwap, cost_mid_bp=1e4 * (mid - vwap) / mid,
                best_after=rest[0][0], best_after_q=rest[0][1], spread_after=BOOK_ASKS[0][0] - rest[0][0],
                new_bid=new_bid, spread_final=BOOK_ASKS[0][0] - new_bid, mid_final=(BOOK_ASKS[0][0] + new_bid) / 2)


def a3_roll(var=0.0520, cov=-0.0081, price=20.0):
    c = np.sqrt(-cov)
    return dict(c=c, s=2 * c, s_pct=100 * 2 * c / price, sig2=var - 2 * c ** 2, share=2 * c ** 2 / var,
                rho=cov / var, var=var, cov=cov, price=price)


def a4_roll():
    x = a3_roll(var=0.0300, cov=-0.0030, price=12.0)
    x['cov_pos'] = 0.0020
    return x


def a5_gm(mu=0.3, theta=0.5, vl=90.0, vh=110.0):
    ask, bid, tb, ts = gm_quotes(theta, mu, vl, vh)
    ask2, bid2, tb2, ts2 = gm_quotes(tb, mu, vl, vh)          # dupa o cumparare
    return dict(ask=ask, bid=bid, spread=ask - bid, pb_h=mu + (1 - mu) / 2, pb_l=(1 - mu) / 2, th_b=tb, th_s=ts,
                ask2=ask2, bid2=bid2, spread2=ask2 - bid2, th_b2=tb2)


def a6_gm():
    x = a5_gm(mu=0.5, theta=0.7)
    ask3, bid3, tb3, _ = gm_quotes(x['th_b2'], 0.5, 90.0, 110.0)
    x.update(ask3=ask3, bid3=bid3, th_b3=tb3)
    return x


def a7_kyle(sigma_v=2.0, sigma_u=10_000.0, y=15_000.0):
    k = kyle(sigma_v, sigma_u)
    k.update(sigma_v=sigma_v, sigma_u=sigma_u, y=y, dp=k['lam'] * y, lam100=100 * k['lam'])
    return k


def a8_ac(lam=2e-6):
    tau = AC['T'] / AC['N']
    eta_t = AC['eta'] - AC['gamma'] * tau / 2
    kt2 = lam * AC['sigma'] ** 2 / eta_t
    kappa = np.arccosh(kt2 * tau ** 2 / 2 + 1) / tau
    t, x, E, V = ac_trajectory(lam=lam, **AC)
    t0, x0, E0, V0 = ac_trajectory(lam=0, **AC)
    return dict(lam=lam, eta_t=eta_t, kt2=kt2, kappa=kappa, x=list(x), n=list(-np.diff(x)), E=E, sd=np.sqrt(V),
                E0=E0, sd0=np.sqrt(V0), sinh5=np.sinh(5 * kappa))


def a9_ac():
    return a8_ac(lam=2e-5)


# =============================================================================
# PARTEA B
# =============================================================================
def b1_ushape():
    s = intraday_spy()
    x = s.dropna(subset=['r'])
    by_day = {}
    for d, g in x.groupby('date'):
        g = g.set_index('tod')
        by_day[d] = (abs(g['r'].get('09:30', np.nan)), g.loc['11:30':'14:00', 'r'].abs().mean(),
                     g['volume'].iloc[-6:].sum() / g['volume'].sum())
    arr = np.array(list(by_day.values()))
    ratio = np.nanmean(arr[:, 0]) / np.nanmean(arr[:, 1])
    lo, hi = boot_days(by_day, lambda v: np.nanmean([a[0] for a in v]) / np.nanmean([a[1] for a in v]))
    vs = np.nanmean(arr[:, 2])
    vlo, vhi = boot_days(by_day, lambda v: np.nanmean([a[2] for a in v]))
    tod = spy_tod(s)
    # grafic: media |r| pe intervale, cu benzi bootstrap pe zile
    piv = x.pivot_table(index='date', columns='tod', values='r', aggfunc=lambda v: abs(v).mean())
    rng = np.random.default_rng(SEED)
    bs = np.array([piv.iloc[rng.integers(0, len(piv), len(piv))].mean().values for _ in range(300)])
    lo_b, hi_b = 1e4 * np.nanpercentile(bs, 2.5, axis=0), 1e4 * np.nanpercentile(bs, 97.5, axis=0)
    k = np.arange(len(piv.columns))
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    ax.fill_between(k, lo_b, hi_b, color='#DADADA', alpha=0.8, lw=0, label='95% bootstrap band (resampling days)')
    ax.plot(k, 1e4 * piv.mean().values, color=IDAred, lw=1.2, marker='o', ms=2.5, label='Mean |5-minute return| (bp)')
    ax.set_xticks(k[::12])
    ax.set_xticklabels(piv.columns[::12], fontsize=7.5)
    ax.set_xlabel('Start of the 5-minute bar (New York time)')
    ax.set_ylabel('Mean |return| (bp)')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch10_sem_ushape')
    return dict(ratio=ratio, lo=lo, hi=hi, open=1e4 * np.nanmean(arr[:, 0]), mid=1e4 * np.nanmean(arr[:, 1]),
                vshare=100 * vs, vlo=100 * vlo, vhi=100 * vhi, n=len(by_day), absr_close=float(tod['absr'].iloc[-1]))


def b2_spreads():
    s = intraday_spy()
    E = intraday_spreads(s)
    by_day = {d: row for d, row in E.iterrows()}
    roll5 = 1e4 * 2 * np.sqrt(max(-E['cov'].mean(), 0))
    rlo, rhi = boot_days(by_day, lambda v: 1e4 * 2 * np.sqrt(max(-np.mean([r['cov'] for r in v]), 0)))
    cs5 = 1e4 * E['cs'].mean()
    clo, chi = boot_days(by_day, lambda v: 1e4 * np.mean([r['cs'] for r in v]))
    ar5 = 1e4 * np.sqrt(max(E['ar2'].mean(), 0))
    alo, ahi = boot_days(by_day, lambda v: 1e4 * np.sqrt(max(np.mean([r['ar2'] for r in v]), 0)))
    tick = 1e4 * (0.01 / E['price']).mean()
    # date zilnice: bootstrap pe blocuri mobile de 20 de zile
    d = ohlc('SPY', START2)
    cs = cs_spread(d['high'], d['low'])
    ar2 = ar_terms(d['close'], d['high'], d['low'])
    rng = np.random.default_rng(SEED)
    n, L = len(cs), 20
    csb, arb = [], []
    for _ in range(B):
        st = rng.integers(0, n - L, n // L + 1)
        idx = np.concatenate([np.arange(a, a + L) for a in st])[:n]
        csb.append(1e4 * cs[idx].mean())
        arb.append(1e4 * np.sqrt(max(ar2[idx].mean(), 0)))
    sd_daily = 1e4 * np.log(d['close']).diff().std()
    return dict(roll5=roll5, rlo=rlo, rhi=rhi, cs5=cs5, clo=clo, chi=chi, ar5=ar5, alo=alo, ahi=ahi, tick=tick,
                cs_d=1e4 * cs.mean(), cs_dlo=float(np.percentile(csb, 2.5)), cs_dhi=float(np.percentile(csb, 97.5)),
                ar_d=1e4 * np.sqrt(max(ar2.mean(), 0)), ar_dlo=float(np.percentile(arb, 2.5)),
                ar_dhi=float(np.percentile(arb, 97.5)), sd_daily=sd_daily, share_negcov=float((E['cov'] < 0).mean()))


def b3_cross():
    T = spread_table()
    A = amihud_table()
    rows = []
    for k in ASSETS:
        r = returns(k, START2)
        ppy = 365 if ASSETS[k][2] == 'Crypto' else 252
        rows.append(dict(key=k, grp=ASSETS[k][2], cs=T[k]['cs'], ar=T[k]['ar'], vol=100 * r.std() * np.sqrt(ppy),
                         illiq=A[k]['illiq'], dv=A[k]['dv_med']))
    t = pd.DataFrame(rows).set_index('key')
    rho_cs_vol = stats.spearmanr(t['cs'], t['vol'])
    rho_il_vol = stats.spearmanr(t['illiq'], t['vol'])
    rho_cs_il = stats.spearmanr(t['cs'], t['illiq'])
    rho_il_dv = stats.spearmanr(t['illiq'], t['dv'])
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    for g, c in GROUP_COL.items():
        m = t['grp'] == g
        axes[0].scatter(t.loc[m, 'vol'], t.loc[m, 'cs'], color=c, s=22, label=g)
        axes[1].scatter(t.loc[m, 'dv'], t.loc[m, 'illiq'], color=c, s=22)
    axes[0].set_xlabel('Annualised volatility (%)')
    axes[0].set_ylabel('Corwin-Schultz spread (bp)')
    axes[0].set_title(f'Spearman correlation {rho_cs_vol.statistic:.2f}', fontsize=9, loc='left')
    axes[1].set_xscale('log')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('Median daily traded value (USD million)')
    axes[1].set_ylabel('Amihud illiquidity (bp per USD 1m)')
    axes[1].set_title(f'Spearman correlation {rho_il_dv.statistic:.2f}', fontsize=9, loc='left')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend_bottom(fig, h, l, ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_cross')
    return dict(rho_cs_vol=float(rho_cs_vol.statistic), p_cs_vol=float(rho_cs_vol.pvalue),
                rho_il_vol=float(rho_il_vol.statistic), rho_cs_il=float(rho_cs_il.statistic),
                rho_il_dv=float(rho_il_dv.statistic), p_il_dv=float(rho_il_dv.pvalue),
                n=int(len(t)), n_ar_zero=int((t['ar'] == 0).sum()),
                bvb_cs_med=float(t.loc[t['grp'] == 'BVB', 'cs'].median()), us_cs_med=float(t.loc[t['grp'] == 'US', 'cs'].median()),
                cr_cs_med=float(t.loc[t['grp'] == 'Crypto', 'cs'].median()),
                table=t.round(4).to_dict(orient='index'))


def b4_illiq_vix():
    s = intraday_spy()
    ill = spy_illiq_daily(s)
    vix = read_market('VIX.INDX')['close'].rename('vix')
    j = pd.concat([ill, vix], axis=1, join='inner').dropna()
    y, X = np.log(j['illiq']), sm.add_constant(np.log(j['vix']))
    ols = sm.OLS(y, X).fit()
    hac = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 20})
    # control pentru nivelul valorii tranzactionate (tendinta)
    dvd = s.groupby('date')['dv'].sum().rename('dv')
    j2 = pd.concat([j, dvd], axis=1, join='inner').dropna()
    X2 = sm.add_constant(pd.DataFrame({'lvix': np.log(j2['vix']), 't': np.arange(len(j2)) / 252}))
    hac2 = sm.OLS(np.log(j2['illiq']), X2).fit(cov_type='HAC', cov_kwds={'maxlags': 20})
    rho1 = float(np.corrcoef(ols.resid[1:], ols.resid[:-1])[0, 1])
    return dict(b=float(hac.params.iloc[1]), se_ols=float(ols.bse.iloc[1]), se_hac=float(hac.bse.iloc[1]),
                lo=float(hac.params.iloc[1] - 1.96 * hac.bse.iloc[1]), hi=float(hac.params.iloc[1] + 1.96 * hac.bse.iloc[1]),
                r2=float(ols.rsquared), n=int(len(j)), rho1=rho1, b2=float(hac2.params['lvix']),
                se2=float(hac2.bse['lvix']), trend=float(hac2.params['t']), se_trend=float(hac2.bse['t']))


def b5_amihud_groups():
    per = {}
    for a, b in [('2024-09-19', '2025-09-18'), ('2025-09-19', '2026-09-18')]:
        per[a[:4]] = {k: float((1e4 * returns(k, a, b).abs() / (dollar_volume(k, a, b) / 1e6)).dropna().mean())
                      for k in ASSETS}
    p1, p2 = pd.Series(per['2024']), pd.Series(per['2025'])
    rho = stats.spearmanr(p1, p2)
    A = amihud_table()
    il = pd.Series({k: v['illiq'] for k, v in A.items()})
    grp = pd.Series({k: v[2] for k, v in ASSETS.items()})
    rng = np.random.default_rng(SEED)
    ratios = []
    for _ in range(B):
        bb = il[grp == 'BVB'].sample(frac=1, replace=True, random_state=rng.integers(1e9)).median()
        uu = il[grp == 'US'].sample(frac=1, replace=True, random_state=rng.integers(1e9)).median()
        ratios.append(bb / uu)
    return dict(rho=float(rho.statistic), p=float(rho.pvalue), med_bvb=float(il[grp == 'BVB'].median()),
                med_us=float(il[grp == 'US'].median()), med_cr=float(il[grp == 'Crypto'].median()),
                ratio=float(il[grp == 'BVB'].median() / il[grp == 'US'].median()),
                lo=float(np.percentile(ratios, 2.5)), hi=float(np.percentile(ratios, 97.5)))


def b6_sqrt():
    s = intraday_spy()
    x, g, slope, _ = sqrt_relation(s)
    days = x['date'].unique()
    by = {d: grp for d, grp in x.groupby('date')}
    bins = np.quantile(x['part'], np.linspace(0, 1, 21))
    rng = np.random.default_rng(SEED)
    sl = []
    for _ in range(300):
        pick = rng.choice(days, len(days), replace=True)
        xx = pd.concat([by[d] for d in pick])
        gg = xx.groupby(pd.cut(xx['part'], bins, include_lowest=True)).agg(v=('part', 'mean'), z=('z', 'mean')).dropna()
        sl.append(np.polyfit(np.log(gg['v']), np.log(gg['z']), 1)[0])
    lo, hi = np.percentile(sl, [2.5, 97.5])
    # pe barele individuale (nu pe grupe)
    y = np.log(x['r'].abs() + 1e-6) - np.log(x.groupby('date')['r'].transform('std'))
    raw = sm.OLS(y, sm.add_constant(np.log(x['part']))).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(x['date'])[0]})
    return dict(slope=float(slope), lo=float(lo), hi=float(hi), n=int(len(x)), n_days=int(len(days)),
                raw=float(raw.params.iloc[1]), raw_se=float(raw.bse.iloc[1]))


def b7_btc():
    b = intraday_btc().dropna(subset=['r'])
    wk = b.index.dayofweek >= 5
    h = b.index.hour
    by_day = {}
    for d, g in b.groupby('date'):
        hh = g.index.hour
        by_day[d] = (g['r'].abs()[(hh >= 13) & (hh < 17)].mean(), g['r'].abs()[(hh >= 3) & (hh < 11)].mean(),
                     g['r'].abs().mean(), d.dayofweek >= 5)
    wd = {d: v for d, v in by_day.items() if not v[3]}
    ratio = np.nanmean([v[0] for v in wd.values()]) / np.nanmean([v[1] for v in wd.values()])
    lo, hi = boot_days(wd, lambda v: np.nanmean([a[0] for a in v]) / np.nanmean([a[1] for a in v]))
    wkr = np.nanmean([v[2] for v in by_day.values() if not v[3]]) / np.nanmean([v[2] for v in by_day.values() if v[3]])
    lo2, hi2 = boot_days(by_day, lambda v: np.nanmean([a[2] for a in v if not a[3]]) / np.nanmean([a[2] for a in v if a[3]]))
    return dict(ratio=float(ratio), lo=lo, hi=hi, wk=float(wkr), wklo=lo2, wkhi=hi2, n_days=len(by_day),
                us=float(1e4 * b['r'].abs()[(~wk) & (h >= 13) & (h < 17)].mean()),
                asia=float(1e4 * b['r'].abs()[(~wk) & (h >= 3) & (h < 11)].mean()))


# =============================================================================
# PARTEA C: prima de iliciditate (Amihud 2002, efectul in serie de timp)
# =============================================================================
C_MARKETS = {
    'BVB': dict(ret=('BETTR.INDX', 'close'), keys=[k for k in GROUPS['BVB'] if k != 'TVBETETF']),
    'US': dict(ret=('SPY.US', 'adjusted_close'), keys=[k for k in GROUPS['US'] if k != 'SPY']),
    'Crypto': dict(ret=('BTC-USD.CC', 'close'), keys=[k for k in GROUPS['Crypto'] if k != 'BTC']),
}


def market_illiq(keys, start='2016-09-19'):
    """Iliciditatea agregata lunara: media transversala a logaritmului Amihud lunar al fiecarui activ."""
    cols = {}
    for k in keys:
        x = pd.concat([returns(k, start).rename('r'), dollar_volume(k, start).rename('dv')], axis=1, join='inner').dropna()
        x = x[x['dv'] > 0]
        m = (1e4 * x['r'].abs() / (x['dv'] / 1e6)).resample('ME').agg(['mean', 'count'])
        cols[k] = np.log(m['mean'].where(m['count'] >= 10))
    return pd.DataFrame(cols).mean(axis=1).rename('lilliq')


def c1_premium():
    out, series = {}, {}
    for name, spec in C_MARKETS.items():
        sym, col = spec['ret']
        p = read_market(sym)[col].loc['2016-08-01':'2026-08-31']
        r = 100 * np.log(p.resample('ME').last()).diff().rename('r')
        li = market_illiq(spec['keys']).dropna()
        # socul de iliciditate: rezidul unui AR(1) pe logaritmul iliciditatii
        ar = sm.OLS(li.iloc[1:].values, sm.add_constant(li.shift(1).iloc[1:].values)).fit()
        shock = pd.Series(ar.resid, index=li.index[1:], name='shock')
        d = pd.concat([r, li.shift(1).rename('lag'), shock], axis=1, join='inner').dropna().loc['2016-11':'2026-08']
        fit = sm.OLS(d['r'], sm.add_constant(d[['lag', 'shock']])).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
        out[name] = dict(n=int(len(d)), b_lag=float(fit.params['lag']), se_lag=float(fit.bse['lag']),
                         t_lag=float(fit.tvalues['lag']), b_shock=float(fit.params['shock']),
                         se_shock=float(fit.bse['shock']), t_shock=float(fit.tvalues['shock']), r2=float(fit.rsquared),
                         phi=float(ar.params[1]), start=d.index[0].strftime('%Y-%m'), end=d.index[-1].strftime('%Y-%m'))
        series[name] = d
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    for ax, (name, d) in zip(axes, series.items()):
        c = GROUP_COL[name]
        ax.scatter(d['shock'], d['r'], s=12, color=c, label=f'{name}: monthly observations')
        xs = np.linspace(d['shock'].min(), d['shock'].max(), 20)
        f = sm.OLS(d['r'], sm.add_constant(d['shock'])).fit()
        ax.plot(xs, f.params.iloc[0] + f.params.iloc[1] * xs, color='black', lw=1.0)
        ax.axhline(0, color=Gray, lw=0.5)
        ax.set_xlabel('Illiquidity shock (AR(1) residual of log illiquidity)')
        ax.set_title(name, fontsize=9, loc='left', color=c)
    axes[0].set_ylabel('Market return in the same month (%)')
    h = [a.get_legend_handles_labels()[0][0] for a in axes]
    fig_legend_bottom(fig, h, [a.get_legend_handles_labels()[1][0] for a in axes] , ncol=3, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch10_sem_premium')
    # sectiunea transversala BVB: portofoliul celor mai putin lichide vs cele mai lichide (reechilibrare anuala)
    keys = C_MARKETS['BVB']['keys']
    px = pd.concat({k: read_market(ASSETS[k][0])['adjusted_close'] for k in keys}, axis=1).loc['2017-01-01':'2026-08-31']
    mret = np.log(px.resample('ME').last()).diff()
    spreads = []
    for y in range(2018, 2027):
        il = {}
        for k in keys:
            rr = returns(k, f'{y - 1}-01-01', f'{y - 1}-12-31')
            dv = dollar_volume(k, f'{y - 1}-01-01', f'{y - 1}-12-31')
            if len(rr) > 150:
                il[k] = float((rr.abs() / dv).dropna().mean())
        if len(il) < 6:
            continue
        srt = sorted(il, key=il.get)
        liq, ill = srt[:len(srt) // 2], srt[-(len(srt) // 2):]
        yr = mret.loc[str(y)]
        spreads.append((yr[ill].mean(axis=1) - yr[liq].mean(axis=1)).dropna())
    ls = 100 * pd.concat(spreads)
    tt = sm.OLS(ls, np.ones(len(ls))).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
    out['bvb_ls'] = dict(mean=float(ls.mean()), se=float(tt.bse.iloc[0]), t=float(tt.tvalues.iloc[0]), n=int(len(ls)),
                         ann=float(12 * ls.mean()))
    return out


if __name__ == '__main__':
    R = {}
    R['A1'] = a1_walk()
    R['A2'] = a2_walk()
    R['A3'] = a3_roll()
    R['A4'] = a4_roll()
    R['A5'] = a5_gm()
    R['A6'] = a6_gm()
    R['A7'] = a7_kyle()
    R['A8'] = a8_ac()
    R['A9'] = a9_ac()
    R['B1'] = b1_ushape()
    R['B2'] = b2_spreads()
    R['B3'] = b3_cross()
    R['B4'] = b4_illiq_vix()
    R['B5'] = b5_amihud_groups()
    R['B6'] = b6_sqrt()
    R['B7'] = b7_btc()
    R['C1'] = c1_premium()
    with open(os.path.join(HERE, 'sem10_results.json'), 'w') as f:
        json.dump(jsonable(R), f, indent=1)
    print('saved sem10_results.json')
    for k, v in R.items():
        if k != 'B3':
            print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()} if isinstance(v, dict) else v)

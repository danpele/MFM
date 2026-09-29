"""
Generator pentru toate graficele si cifrele din Capitolul 16: active digitale si DeFi
====================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos; fara serii gri.
Date zilnice de piata (data/market): Bitcoin, Ethereum, Solana, XRP, Cardano, Dogecoin, Litecoin, Chainlink, BNB,
stablecoin-urile USDT, USDC, DAI; ETF-urile IBIT, ETHA, QQQ, GLD, TLT; actiunile COIN, MSTR; S&P 500; aurul XAU/USD.
Surse publice: oferta curenta a cripto-activelor (Coin Metrics Community Data); TVL si stablecoin-uri (DefiLlama).
Cifrele sunt salvate in ch16_results.json (folosite de generatoarele de slide-uri).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import (ASSETS, LABELS, CRIX_UNIVERSE, STABLE, CLASS_ASSETS, END, price, log_returns,  # noqa: E402
                      joint_prices, joint_returns, periods_per_year, market_values, defi_tvl,
                      stablecoin_chart, stablecoin_list, chain_tvl, chain_tvl_at, symbol_returns, read_market)

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

# Culori brand (gri doar pentru linii de referinta si grila)
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Teal     = '#17A2B8'
Magenta  = '#D63384'
Brown    = '#795548'
Gray     = '#7F7F7F'
COL = {'BTC': Orange, 'ETH': Purple, 'XRP': MainBlue, 'ADA': Forest, 'DOGE': Amber, 'LTC': Teal, 'LINK': IDAred,
       'SOL': Magenta, 'BNB': Brown, 'SPX': MainBlue, 'GOLD': Amber, 'QQQ': Teal, 'USDT': Forest, 'USDC': MainBlue,
       'DAI': Orange, 'IBIT': MainBlue, 'ETHA': Purple, 'COIN': MainBlue, 'MSTR': IDAred, 'TLT': Forest}
CLASS_COL = {'Crypto': Orange, 'Equity': MainBlue, 'FX': Forest, 'Commodity': Amber, 'Bond': Purple}

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
ETF_START = '2024-01-11'          # prima zi de tranzactionare a ETF-urilor spot pe Bitcoin din date (IBIT)
B_BOOT = 2000


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


def fig_legend_bottom(fig, handles=None, labels=None, ncol=4, y=0.0):
    """O singura legenda sub o figura cu mai multe panouri."""
    if handles is None:
        handles, labels = [], []
        for ax in fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels and not l.startswith('_'):
                    handles.append(h)
                    labels.append(l)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def jsonable(x):
    """Converteste recursiv numerele numpy si datele in tipuri JSON."""
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (pd.Timestamp,)):
        return str(x.date())
    return x


def max_drawdown(p):
    """Cea mai mare scadere de la un maxim anterior (in %) si data minimului."""
    dd = p / p.cummax() - 1
    return 100 * dd.min(), dd.idxmin()


def hill(x, frac=0.05):
    """Estimatorul Hill al indicelui de coada pentru cele mai mari frac din valorile pozitive ale lui x."""
    x = np.sort(x[x > 0])[::-1]
    k = max(int(frac * len(x)), 10)
    return 1 / np.mean(np.log(x[:k] / x[k]))


def hac_ols(y, X, lags=4):
    """Regresie OLS cu erori standard Newey-West (HAC)."""
    return sm.OLS(y, sm.add_constant(X)).fit(cov_type='HAC', cov_kwds={'maxlags': lags})


# =============================================================================
# 1. PIATA CRIPTO: valoare de piata si dominanta Bitcoin
# =============================================================================
def fig_market_value():
    """Valoarea de piata (pret x oferta curenta) a activelor din universul indicelui, 2018-2026."""
    mv = market_values()
    m = mv.resample('ME').last()
    tot = mv.sum(axis=1)
    share = 100 * mv['BTC'] / tot
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    axes[0].stackplot(m.index, [m[k] for k in CRIX_UNIVERSE], labels=[LABELS[k] for k in CRIX_UNIVERSE],
                      colors=[COL[k] for k in CRIX_UNIVERSE], alpha=0.85, lw=0)
    axes[0].set_ylabel('Market value (USD bn)')
    axes[1].plot(share.index, share.values, color=Orange, lw=0.9, label=f'Bitcoin share of the {len(CRIX_UNIVERSE)} assets (%)')
    axes[1].set_ylabel('%')
    axes[1].set_ylim(40, 100)
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=4, y=0.0)
    save_fig('ch16_market_value')
    hhi = ((mv.div(tot, axis=0)) ** 2).sum(axis=1)
    return dict(start=str(mv.index[0].date()), total_end=tot.iloc[-1], total_peak=tot.max(),
                total_peak_date=str(tot.idxmax().date()), btc_share_end=share.iloc[-1], btc_share_min=share.min(),
                btc_share_min_date=str(share.idxmin().date()), btc_share_max=share.max(),
                btc_share_max_date=str(share.idxmax().date()), eth_share_end=100 * mv['ETH'].iloc[-1] / tot.iloc[-1],
                hhi_end=hhi.iloc[-1], neff_end=1 / hhi.iloc[-1], mv_end={k: mv[k].iloc[-1] for k in CRIX_UNIVERSE},
                btc_price_end=price('BTC').iloc[-1], btc_supply_end=1e9 * mv['BTC'].iloc[-1] / price('BTC').iloc[-1],
                eth_price_end=price('ETH').iloc[-1], eth_supply_end=1e9 * mv['ETH'].iloc[-1] / price('ETH').iloc[-1],
                end=str(mv.index[-1].date()))


# =============================================================================
# 2. FAPTE STILIZATE: cripto vs actiuni si aur
# =============================================================================
STYL = ['BTC', 'ETH', 'SOL', 'DOGE', 'SPX', 'GOLD']


def stylised_table(start='2018-01-01'):
    """Momente, cozi, autocorelatii, scaderi maxime si VaR 1% / ES 2.5% istorice, fiecare serie pe calendarul ei."""
    rows = {}
    for k in STYL:
        p = price(k, start)
        r = 100 * np.log(p).diff().dropna()
        ppy = periods_per_year(r)
        q = np.quantile(r, 0.01)
        q25 = np.quantile(r, 0.025)
        mdd, mdd_date = max_drawdown(p)
        rows[k] = dict(N=len(r), start=str(r.index[0].date()), ppy=ppy, ann_mean=r.mean() * ppy,
                       ann_vol=r.std() * np.sqrt(ppy), skew=stats.skew(r), kurt=stats.kurtosis(r),
                       acf1=r.autocorr(1), acf1_abs=r.abs().autocorr(1), var1=-q, es2_5=-r[r <= q25].mean(),
                       min=r.min(), min_date=str(r.idxmin().date()), mdd=mdd, mdd_date=str(mdd_date.date()),
                       hill_left=hill(-r.values), share5sd=100 * (np.abs(r - r.mean()) > 5 * r.std()).mean(),
                       # aceleasi masuri ca pierderi simple, in % din pozitie: 1 - exp(r/100)
                       var1_simple=100 * (1 - np.exp(q / 100)),
                       es2_5_simple=100 * (1 - np.exp(r[r <= q25] / 100)).mean(),
                       min_simple=100 * (np.exp(r.min() / 100) - 1))
    t = pd.DataFrame(rows).T
    t.to_csv(os.path.join(HERE, 'ch16_stylised_facts.csv'))
    return t


def fig_rolling_vol(start='2018-01-01'):
    """Volatilitatea anualizata pe ferestre mobile de un an calendaristic."""
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    out = {}
    for k in ['BTC', 'ETH', 'SPX', 'GOLD']:
        r = log_returns(k, start)
        ppy = periods_per_year(r)
        v = 100 * r.rolling('365D', min_periods=int(0.9 * ppy)).std() * np.sqrt(ppy)
        v = v.loc['2019-01-01':]
        ax.plot(v.index, v.values, color=COL[k], lw=1.0, label=LABELS[k])
        out[k] = dict(last=v.iloc[-1], min=v.min(), max=v.max(), min_date=str(v.idxmin().date()))
    ax.set_ylabel('Annualised volatility (%), 1-year window')
    legend_outside_bottom(ax, ncol=4, y=-0.14)
    save_fig('ch16_rolling_vol')
    out['btc_eth_ratio_last'] = out['ETH']['last'] / out['BTC']['last']
    out['btc_spx_ratio_last'] = out['BTC']['last'] / out['SPX']['last']
    return out


def fig_drawdowns(start='2018-01-01'):
    """Scaderea de la maximul anterior pentru Bitcoin, Ethereum si S&P 500."""
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    out = {}
    for k in ['BTC', 'ETH', 'SPX']:
        p = price(k, start)
        dd = 100 * (p / p.cummax() - 1)
        ax.plot(dd.index, dd.values, color=COL[k], lw=0.9, label=LABELS[k])
        out[k] = dict(min=dd.min(), min_date=str(dd.idxmin().date()), last=dd.iloc[-1],
                      share_below50=100 * (dd < -50).mean())
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel('Drawdown from previous peak (%)')
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch16_drawdowns')
    return out


def fig_weekday(start='2018-01-01'):
    """Dispersia randamentelor Bitcoin pe zile ale saptamanii, inainte si dupa lansarea ETF-urilor spot."""
    r = 100 * log_returns('BTC', start)
    pre, post = r.loc[:'2024-01-10'], r.loc[ETF_START:]
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    v_pre = pre.groupby(pre.index.dayofweek).apply(lambda x: np.sqrt((x ** 2).mean()))
    v_post = post.groupby(post.index.dayofweek).apply(lambda x: np.sqrt((x ** 2).mean()))
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    x = np.arange(7)
    ax.bar(x - 0.2, v_pre.values, 0.38, color=MainBlue, label='2018 - 10 Jan 2024')
    ax.bar(x + 0.2, v_post.values, 0.38, color=Orange, label='11 Jan 2024 - Sep 2026 (spot ETF era)')
    ax.set_xticks(x)
    ax.set_xticklabels(days)
    ax.set_ylabel('Root mean squared return (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch16_weekday')

    def ratio(x):
        """Raportul dispersiilor (centrate): weekend / zile lucratoare."""
        we = x[x.index.dayofweek >= 5]
        wd = x[x.index.dayofweek < 5]
        return we.var(ddof=1) / wd.var(ddof=1)
    return dict(ratio_pre=ratio(pre), ratio_post=ratio(post), pre=v_pre.tolist(), post=v_post.tolist(),
                wd_pre=np.sqrt((pre[pre.index.dayofweek < 5] ** 2).mean()),
                we_pre=np.sqrt((pre[pre.index.dayofweek >= 5] ** 2).mean()),
                wd_post=np.sqrt((post[post.index.dayofweek < 5] ** 2).mean()),
                we_post=np.sqrt((post[post.index.dayofweek >= 5] ** 2).mean()))


def fig_rolling_corr():
    """Corelatia pe 250 de zile comune: Bitcoin cu S&P 500, Nasdaq 100 si aurul (join pe preturi)."""
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    out = {}
    for k, c in [('SPX', MainBlue), ('QQQ', Teal), ('GOLD', Amber)]:
        r = joint_returns(['BTC', k], '2016-01-01')
        rc = r['BTC'].rolling(250).corr(r[k]).loc['2018-01-01':]
        ax.plot(rc.index, rc.values, color=c, lw=1.0, label=f'Bitcoin vs {LABELS[k]}')
        per = {}
        for lab, a, b in [('p1', '2017-01-01', '2019-12-31'), ('p2', '2020-01-01', '2023-12-31'),
                          ('p3', ETF_START, END)]:
            x = r.loc[a:b]
            per[lab] = x['BTC'].corr(x[k])
            per[lab + '_n'] = len(x)
        out[k] = dict(per, last=rc.iloc[-1], max=rc.max(), max_date=str(rc.idxmax().date()))
    ax.axhline(0, color=Gray, lw=0.5)
    ax.axvline(pd.Timestamp(ETF_START), color=Gray, lw=0.6, ls='--')
    ax.text(pd.Timestamp(ETF_START), 0.72, ' spot ETFs', fontsize=7.5, color='black')
    ax.set_ylabel('Correlation of daily returns')
    ax.set_ylim(-0.4, 0.8)
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch16_rolling_corr')
    return out


# =============================================================================
# 3. INDICI CRIPTO: indice ponderat cu valoarea de piata, numarul de constituenti ales prin AIC
# =============================================================================
def crix_index(k=None, weighting='cap', mv=None, px=None):
    """Indice Laspeyres cu reponderare lunara: primii k constituenti dupa valoarea de piata la sfarsitul lunii
    anterioare; cantitatile sunt fixe in cursul lunii, iar divizorul pastreaza continuitatea la reponderare."""
    if mv is None:
        mv = market_values()
    if px is None:
        px = pd.concat([price(a) for a in CRIX_UNIVERSE], axis=1).reindex(mv.index)
    months = mv.index.to_period('M')
    level = pd.Series(np.nan, index=mv.index)
    wts = {}
    val = 1000.0
    first = True
    for per in months.unique():
        idx = mv.index[months == per]
        prev = mv.loc[:idx[0] - pd.Timedelta(days=1)]
        if prev.empty:
            continue
        base = prev.iloc[-1]
        members = base.sort_values(ascending=False).index[:(k or len(base))]
        w = base[members] / base[members].sum() if weighting == 'cap' else pd.Series(1 / len(members), index=members)
        p0 = px.loc[prev.index[-1], members]
        rel = (px.loc[idx, members] / p0).mul(w, axis=1).sum(axis=1)
        if first:
            level.loc[prev.index[-1]] = val
            first = False
        level.loc[idx] = val * rel
        val = level.loc[idx[-1]]
        wts[str(per)] = w.reindex(CRIX_UNIVERSE).fillna(0)
    return level.dropna(), pd.DataFrame(wts).T


def crix_aic(mv=None, px=None):
    """AIC(k) = n ln(s2_k) + 2k, cu s2_k media patratelor diferentelor dintre randamentele log ale indicelui total
    (toti cei 7 constituenti) si ale indicelui cu k constituenti; pe intreaga perioada si pe fiecare an."""
    if mv is None:
        mv = market_values()
    if px is None:
        px = pd.concat([price(a) for a in CRIX_UNIVERSE], axis=1).reindex(mv.index)
    tot, _ = crix_index(None, 'cap', mv, px)
    rt = np.log(tot).diff().dropna()
    res = {}
    te = {}
    for k in range(1, len(CRIX_UNIVERSE)):
        lk, _ = crix_index(k, 'cap', mv, px)
        d = (np.log(lk).diff() - np.log(tot).diff()).dropna()
        res[k] = d
        te[k] = 100 * d.std() * np.sqrt(365)
    n = len(rt)
    aic = {k: n * np.log((d ** 2).mean()) + 2 * k for k, d in res.items()}
    bic = {k: n * np.log((d ** 2).mean()) + k * np.log(n) for k, d in res.items()}
    yearly = {}
    for y in sorted(set(rt.index.year)):
        a = {k: len(d.loc[str(y)]) * np.log((d.loc[str(y)] ** 2).mean()) + 2 * k for k, d in res.items()}
        yearly[y] = min(a, key=a.get)
    return dict(aic=aic, bic=bic, te=te, k_aic=min(aic, key=aic.get), k_bic=min(bic, key=bic.get), n=n,
                yearly=yearly)


def fig_crix():
    """Indicele total (7 active), Bitcoin singur (k = 1), indicele cu ponderi egale; AIC(k) si ponderile in timp."""
    mv = market_values()
    px = pd.concat([price(a) for a in CRIX_UNIVERSE], axis=1).reindex(mv.index)
    tot, w = crix_index(None, 'cap', mv, px)
    k1, _ = crix_index(1, 'cap', mv, px)
    k2, _ = crix_index(2, 'cap', mv, px)
    ew, _ = crix_index(None, 'equal', mv, px)
    a = crix_aic(mv, px)
    # indicele
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for s, lab, c, lw in [(tot, f'Cap-weighted, all {len(CRIX_UNIVERSE)} assets (total market)', Orange, 1.3), (k2, 'Cap-weighted, top 2', Purple, 0.9),
                          (k1, 'Top 1 (Bitcoin)', MainBlue, 0.9), (ew, f'Equally weighted, {len(CRIX_UNIVERSE)} assets', Forest, 0.9)]:
        ax.plot(s.index, s.values, color=c, lw=lw, label=lab)
    ax.set_yscale('log')
    ax.set_ylabel('Index level (1000 at start, log scale)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch16_crix_index')
    # eroarea de urmarire si castigul AIC la adaugarea fiecarui constituent
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    ks = list(a['te'])
    axes[0].plot(ks, [a['te'][k] for k in ks], 'o-', color=MainBlue, label=f'Tracking error vs the {len(CRIX_UNIVERSE)}-asset index (% p.a.)')
    axes[0].set_xlabel('Number of constituents k')
    axes[0].set_ylabel('% per year')
    axes[0].set_xticks(ks)
    # imbunatatirea ajustarii n ln(s2_k / s2_(k+1)) = AIC(k) - AIC(k+1) + 2, comparata cu penalizarea 2
    fit = [a['aic'][k] - a['aic'][k + 1] + 2 for k in ks[:-1]]
    axes[1].bar([f'{k} to {k + 1}' for k in ks[:-1]], fit, color=Orange,
                label='Fit improvement n ln(s2(k) / s2(k+1)) when one constituent is added')
    axes[1].axhline(2, color=IDAred, lw=1.0, ls='--', label='AIC penalty per constituent (2)')
    axes[1].set_yscale('log')
    axes[1].set_xlabel('k')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_crix_aic')
    # ponderile
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    wi = w.copy()
    wi.index = pd.PeriodIndex(wi.index, freq='M').to_timestamp()
    ax.stackplot(wi.index, [100 * wi[c] for c in CRIX_UNIVERSE], labels=[LABELS[c] for c in CRIX_UNIVERSE],
                 colors=[COL[c] for c in CRIX_UNIVERSE], alpha=0.85, lw=0, step='post')
    ax.set_ylim(0, 100)
    ax.set_ylabel('Index weight (%)')
    legend_outside_bottom(ax, ncol=5, y=-0.14)
    save_fig('ch16_crix_weights')
    rt = np.log(tot).diff().dropna()
    re_ = np.log(ew).diff().dropna()
    yrs = (tot.index[-1] - tot.index[0]).days / 365.25
    return dict(aic={str(k): v for k, v in a['aic'].items()}, te={str(k): v for k, v in a['te'].items()},
                k_aic=a['k_aic'], k_bic=a['k_bic'], n=a['n'], yearly={str(k): v for k, v in a['yearly'].items()},
                gain={str(k): a['aic'][k] - a['aic'][k + 1] for k in list(a['aic'])[:-1]},
                tot_end=tot.iloc[-1], k1_end=k1.iloc[-1], k2_end=k2.iloc[-1], ew_end=ew.iloc[-1],
                tot_cagr=100 * ((tot.iloc[-1] / 1000) ** (1 / yrs) - 1), ew_cagr=100 * ((ew.iloc[-1] / 1000) ** (1 / yrs) - 1),
                tot_vol=100 * rt.std() * np.sqrt(365), ew_vol=100 * re_.std() * np.sqrt(365),
                w_btc_mean=100 * w['BTC'].mean(), w_btc_min=100 * w['BTC'].min(), w_btc_max=100 * w['BTC'].max(),
                w_last={c: 100 * w[c].iloc[-1] for c in CRIX_UNIVERSE}, start=str(tot.index[0].date()), years=yrs,
                ew_year={str(d.year): 100 * v for d, v in ew.resample('YE').last().pct_change().dropna().items()},
                tot_year={str(d.year): 100 * v for d, v in tot.resample('YE').last().pct_change().dropna().items()},
                k1_year={str(d.year): 100 * v for d, v in k1.resample('YE').last().pct_change().dropna().items()})


# =============================================================================
# 4. STABLECOIN-URI: oferta, abateri de la paritate, USDC in martie 2023, prabusirea UST
# =============================================================================
def fig_stablecoin_supply():
    """Oferta stablecoin-urilor ancorate la USD: total, USDT, USDC, DAI (miliarde USD)."""
    tot = stablecoin_chart()['value'].loc['2019-01-01':]
    parts = {'USDT': stablecoin_chart(1)['value'], 'USDC': stablecoin_chart(2)['value'], 'DAI': stablecoin_chart(5)['value']}
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(tot.index, tot.values, color=IDAred, lw=1.3, label='All USD stablecoins')
    for k, s in parts.items():
        s = s.loc['2019-01-01':]
        ax.plot(s.index, s.values, color=COL[k], lw=1.0, label=LABELS[k])
    ax.set_ylabel('Supply (USD bn)')
    legend_outside_bottom(ax, ncol=4, y=-0.14)
    save_fig('ch16_stablecoin_supply')
    # clasificarea pe mecanisme la aceeasi data ca totalul (END): valoarea fiecarei monede de peste 100 mil. USD,
    # restul monedelor = totalul minus suma lor
    lst = stablecoin_list()
    lst = lst.assign(mechanism=lst['mechanism'].replace({'crytpo-backed': 'crypto-backed'}))
    big = lst[lst['supply'] >= 0.1].copy()
    vals = []
    for i in big['id']:
        v = stablecoin_chart(int(i))['value'].loc[:END].dropna()
        vals.append(float(v.iloc[-1]) if len(v) and v.index[-1] >= pd.Timestamp(END) - pd.Timedelta(days=3) else 0.0)
    big['value'] = vals
    big = big[big['value'] > 0].sort_values('value', ascending=False)
    mech = big.groupby('mechanism')['value'].sum()
    return dict(total_end=tot.iloc[-1], total_2020=tot.loc[:'2020-01-01'].iloc[-1],
                n_big=int(len(big)), other=float(tot.iloc[-1] - big['value'].sum()),
                usdt_end=parts['USDT'].iloc[-1], usdc_end=parts['USDC'].iloc[-1], dai_end=parts['DAI'].iloc[-1],
                usdt_share=100 * parts['USDT'].iloc[-1] / tot.iloc[-1], usdc_share=100 * parts['USDC'].iloc[-1] / tot.iloc[-1],
                usdc_peak=parts['USDC'].max(), usdc_peak_date=str(parts['USDC'].idxmax().date()),
                n_coins=int(len(lst)), mech={k: float(v) for k, v in mech.items()},
                top=[dict(symbol=r.symbol, name=r.name, mechanism=r.mechanism, supply=r.value) for r in big.head(12).itertuples()],
                end=str(tot.index[-1].date()),
                tot_peak22=tot.loc[:'2022-12-31'].max(), tot_peak22_date=str(tot.loc[:'2022-12-31'].idxmax().date()),
                tot_trough=tot.loc['2022-06-01':'2024-06-30'].min(),
                tot_trough_date=str(tot.loc['2022-06-01':'2024-06-30'].idxmin().date()),
                usdc_peak22=parts['USDC'].loc[:'2022-12-31'].max(),
                usdc_peak22_date=str(parts['USDC'].loc[:'2022-12-31'].idxmax().date()),
                usdc_trough=parts['USDC'].loc['2022-06-01':'2024-06-30'].min(),
                usdc_trough_date=str(parts['USDC'].loc['2022-06-01':'2024-06-30'].idxmin().date()))


def peg_stats(key, start='2021-01-01'):
    """Abaterea de la paritate (puncte de baza) pe preturile de inchidere si pe minimele zilnice."""
    d = read_market(ASSETS[key][0]).loc[start:END]
    dev = 1e4 * (d['close'] - 1)
    low = 1e4 * (d['low'] - 1)
    high = 1e4 * (d['high'] - 1)
    x = dev.values
    phi = np.corrcoef(x[1:], x[:-1])[0, 1]
    return dict(N=len(dev), sd=dev.std(), mad=np.median(np.abs(dev)), gt50=100 * (dev.abs() > 50).mean(),
                gt100=100 * (dev.abs() > 100).mean(), low_min=low.min(), low_min_date=str(low.idxmin().date()),
                high_max=high.max(), high_max_date=str(high.idxmax().date()), close_min=dev.min(),
                close_min_date=str(dev.idxmin().date()), phi=phi, half_life=np.log(0.5) / np.log(abs(phi)))


def fig_peg_deviation(start='2021-01-01'):
    """Abaterea zilnica de la 1 USD pentru USDT, USDC si DAI (inchidere si minimul zilei)."""
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 4.6), sharex=True)
    out = {}
    for ax, k in zip(axes, STABLE):
        d = read_market(ASSETS[k][0]).loc[start:END]
        dev = 1e4 * (d['close'] - 1)
        low = 1e4 * (d['low'] - 1)
        ax.plot(low.index, low.clip(lower=-1500).values, color=IDAred, lw=0.5, alpha=0.7, label='Daily low')
        ax.plot(dev.index, dev.values, color=COL[k], lw=0.8, label=f'Daily close')
        ax.axhline(0, color=Gray, lw=0.5)
        ax.set_ylim(-400, 100)
        ax.set_ylabel(f'{k} (bp)')
        out[k] = peg_stats(k, start)
    h = [plt.Line2D([], [], color=COL[k], lw=1.2) for k in STABLE] + [plt.Line2D([], [], color=IDAred, lw=0.8)]
    fig.tight_layout()
    fig_legend_bottom(fig, h, ['USDT daily close', 'USDC daily close', 'DAI daily close',
                               'Daily low (clipped at -400 bp in the panels)'], ncol=4, y=0.0)
    save_fig('ch16_peg_deviation')
    return out


def fig_depeg_2023():
    """Martie 2023: USDC si DAI sub paritate dupa inchiderea Silicon Valley Bank; USDT peste paritate."""
    a, b = '2023-03-05', '2023-03-20'
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    out = {}
    for k in STABLE:
        d = read_market(ASSETS[k][0]).loc[a:b]
        ax.plot(d.index, d['close'], 'o-', color=COL[k], ms=3, lw=1.0, label=f'{k} close')
        ax.plot(d.index, d['low'], 'v', color=COL[k], ms=4, alpha=0.8, label=f'{k} daily low')
        out[k] = dict(low=d['low'].min(), low_date=str(d['low'].idxmin().date()), close_min=d['close'].min(),
                      high=d['high'].max(), close_max=d['close'].max())
    ax.axhline(1, color=Gray, lw=0.6, ls='--')
    ax.set_ylabel('Price (USD)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch16_depeg_2023')
    return out


def fig_ust():
    """TerraUSD (UST), aprilie-mai 2022: oferta si pretul implicit (valoare / oferta), DefiLlama."""
    u = stablecoin_chart(3).loc['2022-03-01':'2022-05-31'].copy()
    u = u[u['supply'] > 0]
    u['px'] = u['value'] / u['supply']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    axes[0].plot(u.index, u['supply'], color=MainBlue, lw=1.2, label='UST supply (bn)')
    axes[0].set_ylabel('Supply (bn UST)')
    axes[1].plot(u.index, u['px'], 'o-', color=IDAred, ms=2.5, lw=1.0, label='UST implied price (USD)')
    axes[1].axhline(1, color=Gray, lw=0.6, ls='--')
    axes[1].set_ylabel('USD')
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.tick_params(axis='x', labelsize=7, rotation=30)
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_ust_collapse')
    last = u.index[-1]
    return dict(supply_peak=u['supply'].max(), supply_peak_date=str(u['supply'].idxmax().date()),
                supply_last=u['supply'].iloc[-1], last_date=str(last.date()), px_min=u['px'].min(),
                px_min_date=str(u['px'].idxmin().date()),
                drop_pct=100 * (1 - u['supply'].iloc[-1] / u['supply'].max()))


# =============================================================================
# 5. FORMATORI AUTOMATI DE PIATA (AMM): alunecare, pierdere impermanenta, simulare pe ETH
# =============================================================================
def amm_swap(x, y, dx, fee=0.003):
    """Schimb dx din activul X intr-un fond x*y = k cu comision fee: cantitatea primita si pretul efectiv."""
    g = 1 - fee
    dy = y * g * dx / (x + g * dx)
    return dy, dy / dx


def impermanent_loss(r):
    """Pierderea impermanenta a unui furnizor de lichiditate 50/50 x*y = k, pentru raportul de pret r = P1/P0."""
    return 2 * np.sqrt(r) / (1 + r) - 1


def fig_amm_theory():
    """Alunecarea pretului in functie de marimea ordinului si pierderea impermanenta."""
    delta = np.logspace(-4, np.log10(0.3), 200)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    out = {}
    for fee, c in [(0.0005, Forest), (0.003, MainBlue), (0.01, IDAred)]:
        g = 1 - fee
        slip = 100 * (1 - g / (1 + g * delta))
        axes[0].plot(100 * delta, slip, color=c, lw=1.2, label=f'Fee {100 * fee:g}%')
        out[f'fee{fee}'] = {f'{d:g}': float(100 * (1 - g / (1 + g * d))) for d in [0.001, 0.01, 0.05, 0.1]}
    axes[0].set_xscale('log')
    axes[0].set_xlabel('Trade size / pool reserve (%)')
    axes[0].set_ylabel('Shortfall vs pool price (%)')
    rr = np.linspace(0.05, 5, 300)
    axes[1].plot(rr, 100 * impermanent_loss(rr), color=Purple, lw=1.4, label='Impermanent loss (%)')
    axes[1].axvline(1, color=Gray, lw=0.5, ls='--')
    axes[1].set_xlabel('Price ratio r = P1 / P0')
    axes[1].set_ylabel('LP value vs holding (%)')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=4, y=0.0)
    save_fig('ch16_amm_theory')
    out['il'] = {f'{r:g}': float(100 * impermanent_loss(r)) for r in [0.25, 0.5, 0.8, 1.25, 2, 4]}
    return out


def fig_lp_vs_hodl(start='2024-01-01'):
    """Fond ETH/USD x*y = k fara comisioane: furnizorul de lichiditate vs pastrarea activelor, vs portofoliul de
    reechilibrare din Milionis et al. (2022) (detine in fiecare zi cantitatea de ETH a fondului, x = V/(2P), si
    tranzactioneaza la pretul pietei) si vs un portofoliu 50/50 reechilibrat zilnic (pondere constanta)."""
    p = price('ETH', start)
    rel = p / p.iloc[0]
    hodl = 100 * (1 + rel) / 2
    lp = 100 * np.sqrt(rel)
    R = p.pct_change().fillna(0)
    reb = 100 * (1 + 0.5 * R).cumprod()
    x_pool = lp / (2 * p)                                         # ETH detinut de fond (V'(P) = V / 2P)
    dR = (x_pool.shift(1) * p.diff()).fillna(0)
    mmrz = 100 + dR.cumsum()                                      # R_t = R_(t-1) + x(P_(t-1)) (P_t - P_(t-1))
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(hodl.index, hodl.values, color=MainBlue, lw=1.1, label='Hold 50% ETH + 50% USD')
    ax.plot(reb.index, reb.values, color=Forest, lw=1.1, label='Constant 50/50 mix, rebalanced daily')
    ax.plot(mmrz.index, mmrz.values, color=Orange, lw=1.1, ls='--', label="Rebalancing benchmark: the pool's ETH, daily")
    ax.plot(lp.index, lp.values, color=IDAred, lw=1.3, label='Liquidity provider, x*y = k, no fees')
    ax.set_ylabel('Value (100 at start)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch16_lp_vs_hodl')
    r = np.log(p).diff().dropna()
    sig2 = r.var() * 365
    yrs = (p.index[-1] - p.index[0]).days / 365.25
    # LVR realizata (Milionis et al., 2022): suma pierderilor zilnice (dR_t - dV_t) / V_(t-1), anualizata
    lvr_real = ((dR - lp.diff()) / lp.shift(1)).dropna().sum() / yrs
    return dict(start=str(p.index[0].date()), p0=p.iloc[0], p1=p.iloc[-1], ratio=rel.iloc[-1], hodl=hodl.iloc[-1],
                lp=lp.iloc[-1], reb=reb.iloc[-1], mmrz=mmrz.iloc[-1], lvr_level=mmrz.iloc[-1] - lp.iloc[-1],
                il=100 * (lp.iloc[-1] / hodl.iloc[-1] - 1), sigma=100 * np.sqrt(sig2),
                lvr_theory=100 * sig2 / 8, lvr_real=100 * lvr_real, cm_gap=100 * np.log(reb.iloc[-1] / lp.iloc[-1]) / yrs,
                years=yrs, fee_apr_hodl=100 * np.log(hodl.iloc[-1] / lp.iloc[-1]) / yrs)


# =============================================================================
# 6. ETF-URI SPOT: IBIT si ETHA fata de activul suport
# =============================================================================
def etf_tracking(etf='IBIT', coin='BTC'):
    """Randamente ETF vs activ suport in zilele de tranzactionare ale ETF-ului: zilnic (aceeasi data si data urmatoare)
    si saptamanal (vineri); abaterea de urmarire; deriva raportului ETF / activ (comisionul anual)."""
    p = joint_prices([etf, coin])
    r = np.log(p).diff().dropna()
    c_next = np.log(price(coin)).diff().shift(-1).reindex(r.index)
    d_same = hac_ols(r[etf], r[coin])
    xx = pd.concat([r[coin], c_next.rename('next')], axis=1).dropna()
    d_two = hac_ols(r[etf].reindex(xx.index), xx)
    w = joint_returns([etf, coin], freq='W')
    wk = hac_ols(w[etf], w[coin])
    te_d = 100 * (r[etf] - r[coin]).std() * np.sqrt(252)
    te_w = 100 * (w[etf] - w[coin]).std() * np.sqrt(52)
    lr = np.log(p[etf] / p[coin])
    t = (lr.index - lr.index[0]).days / 365.25
    drift = np.polyfit(t, lr.values, 1)[0]
    vol = read_market(ASSETS[etf][0])
    dv = (vol['close'] * vol['volume']).loc[:END] / 1e9
    return dict(start=str(p.index[0].date()), n_d=len(r), n_w=len(w), beta_d=d_same.params[coin], r2_d=d_same.rsquared,
                beta_d_next=d_two.params['next'], beta_d_same=d_two.params[coin], r2_d_two=d_two.rsquared,
                beta_w=wk.params[coin], se_w=wk.bse[coin], r2_w=wk.rsquared, te_d=te_d, te_w=te_w,
                drift=100 * drift, corr_next=r[etf].corr(c_next), dv_mean=dv.mean(), dv_last60=dv.iloc[-60:].mean(),
                dv_max=dv.max(), dv_max_date=str(dv.idxmax().date()))


def fig_etf():
    """IBIT si Bitcoin: nivelurile normalizate si randamentele zilnice vs saptamanale."""
    p = joint_prices(['IBIT', 'BTC'])
    n = 100 * p / p.iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.plot(n.index, n['BTC'], color=Orange, lw=1.2, label='Bitcoin (on ETF trading days)')
    ax.plot(n.index, n['IBIT'], color=MainBlue, lw=1.0, ls='--', label='IBIT (spot Bitcoin ETF)')
    ax.set_ylabel('Level (100 on 11 Jan 2024)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch16_etf_tracking')
    r = np.log(p).diff().dropna() * 100
    w = joint_returns(['IBIT', 'BTC'], freq='W') * 100
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, x, lab in [(axes[0], r, 'Daily returns (%)'), (axes[1], w, 'Weekly returns, Friday to Friday (%)')]:
        ax.scatter(x['BTC'], x['IBIT'], s=6, color=MainBlue, alpha=0.6, label='Observations')
        lim = [min(x.min()), max(x.max())]
        ax.plot(lim, lim, color=Gray, lw=0.6, ls='--', label='45-degree line')
        b = np.polyfit(x['BTC'], x['IBIT'], 1)
        ax.plot(lim, np.polyval(b, lim), color=IDAred, lw=1.0, label='OLS fit')
        ax.set_xlabel('Bitcoin')
        ax.set_ylabel('IBIT')
        ax.set_title(lab, fontsize=9, loc='left')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=3, y=0.0)
    save_fig('ch16_etf_timing')
    return dict(ibit=etf_tracking('IBIT', 'BTC'), etha=etf_tracking('ETHA', 'ETH'),
                ibit_end=n['IBIT'].iloc[-1], btc_end=n['BTC'].iloc[-1])


# =============================================================================
# 7. ACTIUNI "CRIPTO": COIN si MSTR, beta fata de Bitcoin si S&P 500 (saptamanal)
# =============================================================================
def fig_crypto_equities(start='2021-04-16'):
    """Regresii saptamanale cu doi factori (Bitcoin, S&P 500) si beta mobil pe 52 de saptamani fata de Bitcoin."""
    out = {}
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    for k in ['COIN', 'MSTR']:
        w = joint_returns([k, 'BTC', 'SPX'], start, freq='W')
        m = hac_ols(w[k], w[['BTC', 'SPX']])
        m1 = hac_ols(w[k], w['BTC'])
        cov = w[k].rolling(52).cov(w['BTC'])
        beta = (cov / w['BTC'].rolling(52).var()).dropna()
        ax.plot(beta.index, beta.values, color=COL[k], lw=1.1, label=f'{LABELS[k]}: 52-week beta to Bitcoin')
        out[k] = dict(n=len(w), a=52 * 100 * m.params['const'], b_btc=m.params['BTC'], se_btc=m.bse['BTC'],
                      b_spx=m.params['SPX'], se_spx=m.bse['SPX'], r2=m.rsquared, b1=m1.params['BTC'], r2_1=m1.rsquared,
                      vol=100 * w[k].std() * np.sqrt(52), beta_last=beta.iloc[-1], beta_min=beta.min(),
                      beta_max=beta.max(), corr=w[k].corr(w['BTC']))
    ax.axhline(1, color=Gray, lw=0.5, ls='--')
    ax.set_ylabel('Beta to Bitcoin')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch16_crypto_equities')
    wb = joint_returns(['BTC', 'SPX'], start, freq='W')
    out['btc_vol'] = 100 * wb['BTC'].std() * np.sqrt(52)
    return out


# =============================================================================
# 8. DEFI: valoarea totala blocata (TVL) si Ethereum; TVL pe blockchain-uri
# =============================================================================
def fig_defi_tvl():
    """TVL total (DefiLlama) si pretul Ethereum, lunar, 2020-2026; TVL pe blockchain-uri azi."""
    tvl = defi_tvl().loc['2020-01-01':]
    eth = price('ETH', '2020-01-01')
    m = pd.concat([tvl.resample('ME').last(), eth.resample('ME').last()], axis=1).dropna()
    m.columns = ['TVL', 'ETH']
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(m.index, 100 * m['TVL'] / m['TVL'].iloc[0], color=Forest, lw=1.3, label='DeFi total value locked')
    ax.plot(m.index, 100 * m['ETH'] / m['ETH'].iloc[0], color=Purple, lw=1.1, label='Ethereum price')
    ax.set_yscale('log')
    ax.set_ylabel('Index (100 in Jan 2020, log scale)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch16_defi_tvl')
    d = np.log(m).diff().dropna()
    reg = hac_ols(d['TVL'], d['ETH'], lags=3)
    # TVL pe blockchain-uri la aceeasi data ca seria totala (END): cele mai mari 10 dintre primele 15 de azi
    ch = pd.Series({c: chain_tvl_at(c, END) for c in chain_tvl().head(15).index}).sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.barh(ch.index[::-1], ch.values[::-1], color=Teal, label='Total value locked (USD bn)')
    ax.set_xlabel('USD bn')
    legend_outside_bottom(ax, ncol=1, y=-0.18)
    save_fig('ch16_tvl_chains')
    tot_now = tvl.iloc[-1]
    return dict(peak=tvl.max(), peak_date=str(tvl.idxmax().date()), last=tvl.iloc[-1], last_date=str(tvl.index[-1].date()),
                start=tvl.iloc[0], beta=reg.params['ETH'], se=reg.bse['ETH'], r2=reg.rsquared, n=len(d),
                corr=d['TVL'].corr(d['ETH']), chains={k: float(v) for k, v in ch.items()},
                eth_share=100 * ch.iloc[0] / tot_now, chains_total=tot_now)


# =============================================================================
# 9. SUNT CRIPTO-ACTIVELE O CLASA ALTERNATIVA? (replicare restransa a abordarii Pele et al., 2023)
# =============================================================================
WINDOWS = {'W1': ('2019-01-01', '2021-06-30'), 'W2': (ETF_START, END)}
FEATURES = ['ann_vol', 'skew', 'kurt', 'acf1', 'acf1_sq', 'hill_left', 'hill_right', 'mdd']


def asset_features(r, ppy=None):
    """Caracteristicile statistice ale unei serii de randamente log zilnice (ppy: observatii pe an, implicit
    frecventa reala a seriei)."""
    ppy = periods_per_year(r) if ppy is None else ppy
    p = np.exp(r.cumsum())
    return dict(ann_vol=np.log(r.std() * np.sqrt(ppy)), skew=stats.skew(r), kurt=np.log1p(max(stats.kurtosis(r), 0)),
                acf1=r.autocorr(1), acf1_sq=(r ** 2).autocorr(1), hill_left=hill(-r.values - (-r).median()),
                hill_right=hill(r.values - r.median()), mdd=(p / p.cummax() - 1).min())


def feature_table():
    """Tabelul caracteristicilor pe active si ferestre (W1: 2019 - iunie 2021; W2: era ETF-urilor spot)."""
    rows = []
    for s, (lab, cls, _) in CLASS_ASSETS.items():
        for w, (a, b) in WINDOWS.items():
            r = symbol_returns(s, a, b)
            rows.append(dict(symbol=s, label=lab, cls=cls, window=w, **asset_features(r)))
    return pd.DataFrame(rows)


def fig_alt_assets():
    """Componente principale ale caracteristicilor standardizate; distanta cripto - clasele traditionale."""
    f = feature_table()
    X = f[FEATURES].values
    Z = (X - X.mean(0)) / X.std(0)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    pc = Z @ Vt[:2].T
    if np.corrcoef(pc[:, 0], f['ann_vol'])[0, 1] < 0:
        pc[:, 0] *= -1
        Vt[0] *= -1          # incarcarile PC1 cu acelasi semn ca axa din grafic
    f['pc1'], f['pc2'] = pc[:, 0], pc[:, 1]
    ev = S ** 2 / (S ** 2).sum()
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for cls, c in CLASS_COL.items():
        for w, mk, fc in [('W1', 'o', 'none'), ('W2', 'o', c)]:
            x = f[(f.cls == cls) & (f.window == w)]
            ax.scatter(x['pc1'], x['pc2'], s=26, marker=mk, facecolors=fc, edgecolors=c, lw=1.0,
                       label=f'{cls}, ' + ('2019 - Jun 2021' if w == 'W1' else 'Jan 2024 - Sep 2026'))
    for s in f[f.cls == 'Crypto'].symbol.unique():
        a = f[(f.symbol == s) & (f.window == 'W1')].iloc[0]
        b = f[(f.symbol == s) & (f.window == 'W2')].iloc[0]
        ax.annotate('', xy=(b.pc1, b.pc2), xytext=(a.pc1, a.pc2),
                    arrowprops=dict(arrowstyle='->', color=Orange, lw=0.7, alpha=0.8))
    for s, w, dx, dy in [('BTC-USD.CC', 'W1', 4, 4), ('BTC-USD.CC', 'W2', -30, -10), ('GSPC.INDX', 'W2', 4, 3),
                         ('XAUUSD.FOREX', 'W2', 4, 3)]:
        b = f[(f.symbol == s) & (f.window == w)].iloc[0]
        lab = b.label + (' (2019-21)' if w == 'W1' else '')
        ax.annotate(lab, (b.pc1, b.pc2), xytext=(dx, dy), textcoords='offset points', fontsize=7, color='black')
    ax.axhline(0, color=Gray, lw=0.4)
    ax.axvline(0, color=Gray, lw=0.4)
    ax.set_xlabel(f'PC1 ({100 * ev[0]:.0f}% of variance)')
    ax.set_ylabel(f'PC2 ({100 * ev[1]:.0f}% of variance)')
    legend_outside_bottom(ax, ncol=4, y=-0.16)
    save_fig('ch16_alt_assets')
    # distante in spatiul complet standardizat
    f[[f'z_{c}' for c in FEATURES]] = Z
    zc = [f'z_{c}' for c in FEATURES]
    out = dict(ev1=100 * ev[0], ev2=100 * ev[1], loadings={c: float(v) for c, v in zip(FEATURES, Vt[0])})
    for w in WINDOWS:
        g = f[f.window == w]
        cen = g.groupby('cls')[zc].mean()
        cr = g[g.cls == 'Crypto'][zc].values
        out[w] = dict(dist_equity=float(np.linalg.norm(cen.loc['Crypto'] - cen.loc['Equity'])),
                      dist_commodity=float(np.linalg.norm(cen.loc['Crypto'] - cen.loc['Commodity'])),
                      dist_fx=float(np.linalg.norm(cen.loc['Crypto'] - cen.loc['FX'])),
                      dist_bond=float(np.linalg.norm(cen.loc['Crypto'] - cen.loc['Bond'])),
                      spread_crypto=float(np.mean(np.linalg.norm(cr - cr.mean(0), axis=1))),
                      btc_vol=float(np.exp(g[g.symbol == 'BTC-USD.CC']['ann_vol'].iloc[0]) * 100),
                      crypto_kurt=float(np.expm1(g[g.cls == 'Crypto']['kurt']).median()))
    f.drop(columns=zc).to_csv(os.path.join(HERE, 'ch16_asset_features.csv'), index=False)
    return out


if __name__ == '__main__':
    print('Chapter 16: digital assets and DeFi')
    res = {}
    res['market_value'] = fig_market_value()
    t = stylised_table()
    res['stylised'] = {k: t.loc[k].to_dict() for k in t.index}
    res['rolling_vol'] = fig_rolling_vol()
    res['drawdowns'] = fig_drawdowns()
    res['weekday'] = fig_weekday()
    res['rolling_corr'] = fig_rolling_corr()
    res['crix'] = fig_crix()
    res['stable_supply'] = fig_stablecoin_supply()
    res['peg'] = fig_peg_deviation()
    res['depeg_2023'] = fig_depeg_2023()
    res['ust'] = fig_ust()
    res['amm'] = fig_amm_theory()
    res['lp'] = fig_lp_vs_hodl()
    res['etf'] = fig_etf()
    res['equities'] = fig_crypto_equities()
    res['defi'] = fig_defi_tvl()
    res['alt'] = fig_alt_assets()
    with open(os.path.join(HERE, 'ch16_results.json'), 'w') as fh:
        json.dump(jsonable(res), fh, indent=1)
    print('saved ch16_results.json')

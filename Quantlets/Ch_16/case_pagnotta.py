"""
case_pagnotta.py -- Chapter 16, second case study: Pagnotta (2022, Review of Financial Studies),
"Decentralizing Money: Bitcoin Prices and Blockchain Security"
=================================================================================================
Lemma 1 of the paper (linear mining cost c per unit of hashrate, m identical miners):
    H* = (m - 1)/m * delta * R * E_t[p_{t+1}] / c,
so the system hashrate is proportional to the expected USD value of the block reward R * p:
  * unit elasticity of the hashrate to the USD block reward (given the cost c);
  * a halving of R halves H* at a given expected price.
The paper's evidence is the joint path of price and hashrate, August 2010 - January 2020 (its Figure 1).

Course replication
  * Bitcoin closing price: course data (data/market/BTC-USD.CC.csv);
  * hashrate (HashRate, TH/s), new issuance (IssTotNtv, BTC per day), fees (FeeTotNtv, BTC per day) and the
    number of blocks (BlkCnt): Coin Metrics Community Data;
  * per block: subsidy S_t = IssTotNtv/BlkCnt and fees F_t = FeeTotNtv/BlkCnt (BTC); USD reward per block
    B_t = price_t x (S_t + F_t), the R p of Lemma 1; daily miner revenue D_t = price_t x (IssTotNtv + FeeTotNtv)
    (it also moves with the number of blocks found that day, which enters the hashrate estimate);
  * share of the subsidy in the miners' revenue, daily, July 2010 - January 2020 (Section 1.1 of the paper);
  * levels: monthly means, log H on log B and a linear trend (hardware efficiency lowers c over time), Newey-West
    standard errors (12 lags), Engle-Granger test of no cointegration (constant and trend); paper window
    (Aug 2010 - Jan 2020) and out of sample (Feb 2020 - Aug 2026);
  * halvings (blocks 210,000, 420,000, 630,000, 840,000): change of the 7-day mean hashrate and of the 7-day mean
    USD block reward from the 7 days before the halving, -30 to +90 days.
Output: charts/ch16_pagnotta_hashrate (.pdf, .png) and ch16_pagnotta.json.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import price, coin_metrics, END  # noqa: E402

plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'], 'font.size': 9,
                     'axes.labelsize': 10, 'axes.titlesize': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.6, 'lines.linewidth': 1.1,
                     'legend.facecolor': 'none', 'legend.framealpha': 0, 'legend.fontsize': 8})
MainBlue, IDAred, Forest, Orange, Purple, Teal, Navy = ('#1A3A6E', '#CD0000', '#2E7D32', '#E67E22', '#8E44AD',
                                                       '#17A2B8', '#1F2A44')

CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
HALVINGS = ['2012-11-28', '2016-07-09', '2020-05-11', '2024-04-20']
HCOL = {'2012-11-28': Teal, '2016-07-09': Forest, '2020-05-11': Purple, '2024-04-20': IDAred}
PAPER = ('2010-08', '2020-01')          # Figure 1 of the paper: August 2010 - January 2020
OOS = ('2020-02', '2026-08')            # complete months after the paper's window, up to END
K_MIN, K_MAX, LAGS = -30, 90, 12


def daily():
    """Daily price (course data), hashrate (TH/s), issuance (BTC) and USD block reward, on common days."""
    cm = coin_metrics('btc', ['HashRate', 'IssTotNtv', 'FeeTotNtv', 'BlkCnt'], '2010-07-01', END)
    d = pd.concat([price('BTC').rename('P'), cm['HashRate'].rename('H'), cm['IssTotNtv'].rename('R'),
                   cm['FeeTotNtv'].rename('F'), cm['BlkCnt'].rename('N')], axis=1, join='inner').dropna()
    d = d[(d.H > 0) & (d.R > 0) & (d.N > 0)]
    d['B'] = d.P * (d.R + d.F) / d.N        # USD reward per block, subsidy plus fees
    d['BS'] = d.P * d.R / d.N               # USD subsidy per block
    d['D'] = d.P * (d.R + d.F)              # daily miner revenue, USD
    return d


def subsidy_share(d, a='2010-07-01', b='2020-01-31'):
    """Daily share of the subsidy in the miners' revenue (subsidy plus fees): median and mean, in %."""
    c = 100 * d.R / (d.R + d.F)
    return dict(median=float(c.loc[a:b].median()), mean=float(c.loc[a:b].mean()),
                median_last=float(c.iloc[-365:].median()), mean_last=float(c.iloc[-365:].mean()))


def levels(d):
    """log H on log B and a trend, monthly means; HAC errors; Engle-Granger p-value."""
    m = np.log(d[['P', 'H', 'B', 'BS', 'D']].resample('ME').mean())
    out = {}
    for name, (a, b) in [('paper', PAPER), ('oos', OOS)]:
        z = m.loc[a:b]
        t = np.arange(len(z)) / 12
        X = sm.add_constant(pd.DataFrame({'B': z.B, 't': t}, index=z.index))
        r = sm.OLS(z.H, X).fit(cov_type='HAC', cov_kwds={'maxlags': LAGS})
        r0 = sm.OLS(z.H, sm.add_constant(z.B)).fit()
        out[name] = dict(first=str(z.index[0].date())[:7], last=str(z.index[-1].date())[:7], n=len(z),
                         b=r.params['B'], se=r.bse['B'], trend=100 * r.params['t'], r2=r.rsquared,
                         b_notrend=r0.params['B'], r2_notrend=r0.rsquared,
                         eg_p=coint(z.H, z.B, trend='ct')[1])
        for v in ('BS', 'D'):       # subsidy only, per block; daily revenue
            Xv = sm.add_constant(pd.DataFrame({v: z[v], 't': t}, index=z.index))
            rv = sm.OLS(z.H, Xv).fit(cov_type='HAC', cov_kwds={'maxlags': LAGS})
            out[name]['b_' + v], out[name]['se_' + v] = rv.params[v], rv.bse[v]
    return out, m


def event(d):
    """Change (%) of the 7-day mean hashrate and USD reward per block from the 7 days before each halving
    (the UTC day of the halving block: heights 210,000, 420,000, 630,000, 840,000)."""
    H7, B7 = d.H.rolling(7).mean(), d.B.rolling(7).mean()
    ks = np.arange(K_MIN, K_MAX + 1)
    paths, out = {}, {}
    for h in HALVINGS:
        t0 = pd.Timestamp(h)
        base = t0 - pd.Timedelta(days=1)
        idx = [t0 + pd.Timedelta(days=int(k)) for k in ks]
        ph = 100 * (H7.reindex(idx).values / H7[base] - 1)
        pb = 100 * (B7.reindex(idx).values / B7[base] - 1)
        paths[h] = dict(k=ks, H=ph, B=pb)
        out[h] = {f'H{k}': ph[k - K_MIN] for k in (30, 90)}
        out[h].update({f'B{k}': pb[k - K_MIN] for k in (30, 90)})
        post = ks >= 0
        j = int(np.nanargmin(np.where(post, ph, np.nan)))
        out[h]['H_min'], out[h]['H_min_day'] = ph[j], int(ks[j])
        out[h]['R_cut'] = 100 * (d.R.loc[t0 + pd.Timedelta(days=1):t0 + pd.Timedelta(days=7)].mean() /
                                 d.R.loc[t0 - pd.Timedelta(days=7):base].mean() - 1)
    return out, paths


def fig(m, paths):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axes[0]
    mm = np.exp(m)
    ax.plot(mm.index, mm.P, color=Orange, lw=1.1, label='Bitcoin price (USD, left axis, monthly mean)')
    ax.set_yscale('log')
    ax.set_ylabel('Price (USD)')
    ax2 = ax.twinx()
    ax2.spines['right'].set_visible(True)
    ax2.plot(mm.index, mm.H / 1e6, color=MainBlue, lw=1.1, label='Hashrate (EH/s, right axis, monthly mean)')
    ax2.set_yscale('log')
    for h in HALVINGS:
        ax.axvline(pd.Timestamp(h), color=Navy, lw=0.6, ls=':')
    ax.axvline(pd.Timestamp('2020-01-31'), color=Navy, lw=0.8, ls='--')
    ax.text(pd.Timestamp('2020-01-31'), 0.04, ' end of the\n paper\'s Figure 1', transform=ax.get_xaxis_transform(),
            fontsize=7, color='black', va='bottom')
    ax.set_title('Price and hashrate, log scales; dotted: halvings', fontsize=9)
    ax = axes[1]
    for h in HALVINGS:
        p = paths[h]
        ax.plot(p['k'], p['H'], color=HCOL[h], lw=1.1, label=f'Hashrate, halving of {h[:4]}')
    ax.axhline(-50, color=Navy, lw=0.8, ls='--', label='Lemma 1, static benchmark: -50%')
    ax.axhline(0, color=Navy, lw=0.4)
    ax.axvline(0, color=Navy, lw=0.6, ls=':')
    ax.set_xlabel('Days from the halving')
    ax.set_ylabel('Change (%)')
    ax.set_title('Hashrate around the halvings, change\nfrom the week before (7-day means)', fontsize=9)
    ax.set_xlim(K_MIN, K_MAX)
    fig.tight_layout(w_pad=2.5)
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    h3, l3 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2 + h3, l1 + l2 + l3, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    os.makedirs(CHART_DIR, exist_ok=True)
    for ext, kw in (('pdf', {}), ('png', {'dpi': 180})):
        plt.savefig(os.path.join(CHART_DIR, f'ch16_pagnotta_hashrate.{ext}'), bbox_inches='tight', transparent=True, **kw)
    plt.close()
    print('   saved ch16_pagnotta_hashrate')


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    return x


def main():
    d = daily()
    lv, m = levels(d)
    ev, paths = event(d)
    fig(m.loc[PAPER[0]:], paths)
    res = dict(levels=lv, halvings=ev, share=subsidy_share(d), first=str(d.index[0].date()), last=str(d.index[-1].date()),
               h_last=d.H.iloc[-7:].mean() / 1e6, reward_last=d.R.iloc[-7:].mean())
    with open(os.path.join(HERE, 'ch16_pagnotta.json'), 'w') as fh:
        json.dump(jsonable(res), fh, indent=1)
    print(json.dumps(jsonable(res), indent=1))
    return res


if __name__ == '__main__':
    main()

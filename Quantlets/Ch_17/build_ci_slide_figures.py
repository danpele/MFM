"""Render two slide panels from the existing LPPLS confidence caches; no fitting."""
from pathlib import Path
import pandas as pd
import matplotlib.dates as mdates
import generate_all_charts as g


def build():
    here = Path(__file__).resolve().parent
    btc = pd.read_csv(here / 'ch17_lppls_ci_btc.csv', index_col=0, parse_dates=True)
    ndx = pd.read_csv(here / 'ch17_lppls_ci_ndx.csv', index_col=0, parse_dates=True)
    p = g.price('btc', 'D', '2015-01-01')
    fig, ax = g.plt.subplots(figsize=(7.4, 3.0))
    ax.plot(p.index, p.values, color=g.MainBlue, lw=0.8, label='Bitcoin (USD, log scale)')
    ax.set_yscale('log')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2 = ax.twinx()
    ax2.bar(btc.index, btc['ci'], width=6, color=g.IDAred, label='LPPLS confidence indicator (right axis)')
    ax2.set_ylim(0, 0.2)  # the indicator never exceeds 0.18 here
    ax2.spines['right'].set_visible(True)
    ax.set_title('Bitcoin: 141 windows of 50-750 observations, every 5 observations', fontsize=9, loc='left')
    fig.tight_layout()
    h1,l1=ax.get_legend_handles_labels();h2,l2=ax2.get_legend_handles_labels()
    fig.legend(h1+h2,l1+l2,loc='upper center',bbox_to_anchor=(0.5,0),ncol=2,frameon=False)
    g.save_fig('ch17_lppls_ci_price')
    keys=list(g.COND_LABELS);sb=g.condition_shares(btc);sn=g.condition_shares(ndx)
    y=g.np.arange(len(keys))[::-1]
    fig,ax=g.plt.subplots(figsize=(7.4,3.6))
    ax.barh(y+0.2,[100*sb[k] for k in keys],0.4,color=g.Amber,label='Bitcoin, all windows')
    ax.barh(y-0.2,[100*sn[k] for k in keys],0.4,color=g.Teal,label='Nasdaq 100, all windows')
    ax.set_yticks(y);ax.set_yticklabels([g.COND_LABELS[k] for k in keys],fontsize=8)
    ax.set_xlabel('% of windows passing');ax.set_xlim(0,100)
    fig.tight_layout()
    ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.18),ncol=2,frameon=False)
    g.save_fig('ch17_lppls_ci_filters')

if __name__ == '__main__':
    build()

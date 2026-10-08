"""
ai_discovery_case.py -- Capitolul 0, sectiunea "AI for Scientific Discovery": mini-caz
=====================================================================================
Ipoteza: indicele ponderat cu capitalizarea (SPY) bate indicele echiponderat (RSP) -- o prima de concentrare.
H0: E[d_t] = 0, d_t = r_SPY,t - r_RSP,t (randamente log zilnice din preturile ajustate, join pe zilele comune).
Test: t Newey-West pe esantionul complet si pe doua sub-esantioane (robustete la alegerea ferestrei).
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
MARKET = os.path.join(HERE, '..', '..', 'data', 'market')
RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'


def price(sym):
    p = os.path.join(MARKET, sym + '.csv')
    d = pd.read_csv(p if os.path.exists(p) else RAW + sym + '.csv', index_col='date', parse_dates=True)
    return d['adjusted_close'].rename(sym)


def nw_mean(x):
    """Media si t-ul Newey-West (Bartlett, L = floor(4 (T/100)^(2/9)))."""
    x = np.asarray(x, float)
    T = len(x)
    L = int(np.floor(4 * (T / 100) ** (2 / 9)))
    e = x - x.mean()
    s = (e @ e) / T
    for l in range(1, L + 1):
        s += 2 * (1 - l / (L + 1)) * (e[l:] @ e[:-l]) / T
    return x.mean(), x.mean() / np.sqrt(s / T)


p = pd.concat([price('SPY.US'), price('RSP.US')], axis=1).dropna()     # join pe PRETURI, apoi randamente
r = np.log(p).diff().dropna()
d = r['SPY.US'] - r['RSP.US']
out = {'start': str(d.index[0].date()), 'end': str(d.index[-1].date()), 'n': int(len(d))}
for lab, x in [('full', d), ('a', d.loc[:'2014-12-31']), ('b', d.loc['2015-01-01':])]:
    m, t = nw_mean(x.values)
    out[lab] = {'start': str(x.index[0].date()), 'end': str(x.index[-1].date()), 'n': int(len(x)),
                'mean_ann_pct': 100 * 252 * m, 't_nw': t, 'te_ann_pct': 100 * np.sqrt(252) * x.std()}
# putere: diferenta anuala minima detectabila (test bilateral 5%, putere 80%: (1.96 + 0.84) x SE)
for lab in ['full', 'b']:
    out[lab]['mde_ann_pct'] = 2.8 * abs(out[lab]['mean_ann_pct'] / out[lab]['t_nw'])

def fig_ai_spread(out):
    """Media anualizata a diferentei SPY - RSP cu intervale HAC de 95% si MDE (grafic pentru slide-ul mini-cazului)."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                         'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
                         'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})
    MainBlue, IDAred, Amber, Forest = '#1A3A6E', '#CD0000', '#B5853F', '#2E7D32'
    labs = [('full', 'May 2003 - Sep 2026'), ('a', '2003 - 2014'), ('b', '2015 - 2026')]
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    for k, (key, lab) in enumerate(labs):
        m, t = out[key]['mean_ann_pct'], out[key]['t_nw']; se = abs(m / t)
        ax.errorbar(m, k, xerr=1.96 * se, fmt='o', color=[MainBlue, Forest, Forest][k], capsize=3, ms=5, lw=1.3,
                    label='Estimate with HAC 95% interval' if k == 0 else None)
        ax.annotate(f'{m:+.2f}% (t = {t:.2f})', (m, k), xytext=(0, 7), textcoords='offset points', ha='center',
                    fontsize=7.5, color='black')
        if 'mde_ann_pct' in out[key]:
            ax.plot([out[key]['mde_ann_pct'], -out[key]['mde_ann_pct']], [k, k], '|', color=IDAred, ms=12, mew=2,
                    label='Minimum detectable effect, $\\pm 2.8$ SE' if key == 'full' else None)
    ax.axvline(0, color='black', lw=0.7, ls=':')
    ax.set_yticks(range(3)); ax.set_yticklabels([l for _, l in labs])
    ax.invert_yaxis(); ax.set_ylim(2.6, -0.6)
    ax.set_xlabel('Mean of $r_{SPY} - r_{RSP}$ (% per year)')
    ax.set_title('Is there a concentration premium?', loc='left', fontsize=9)
    plt.tight_layout()
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=1, fontsize=7.5)
    charts = os.path.join(HERE, '..', '..', 'charts')
    for ext, kw in [('pdf', {}), ('png', {'dpi': 180})]:
        plt.savefig(os.path.join(charts, f'ch0_ai_spread.{ext}'), bbox_inches='tight', transparent=True, **kw)
    plt.close()


if __name__ == '__main__':
    print(json.dumps(out, indent=1))
    fig_ai_spread(out)
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)

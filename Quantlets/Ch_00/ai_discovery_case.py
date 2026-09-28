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

if __name__ == '__main__':
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)

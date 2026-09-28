"""
ai_discovery_case.py -- Capitolul 1, sectiunea "AI for Scientific Discovery": mini-caz
=====================================================================================
Ipoteza: dupa aprobarea ETF-urilor spot pe Bitcoin (10 ian. 2024) coada lui Bitcoin s-a subtiat (alfa mai mare).
H0: alfa_post = alfa_pre (indicele de coada Hill al |r_t|, k = 2.5% din n, ca in capitol).
Test: z asimptotic (var(alfa_hat) = alfa^2 / k sub i.i.d.) si bootstrap pe blocuri mobile (dependenta GARCH).
Placebo: acelasi test pe S&P 500 la aceeasi data.
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import load_close  # noqa: E402

BREAK = '2024-01-11'          # prima zi de tranzactionare a ETF-urilor spot (aprobare: 10 ian. 2024)
FRAC = 0.025
B, BLOCK = 2000, 20
rng = np.random.default_rng(2026)


def hill(x, k):
    x = np.sort(x[x > 0])[::-1]
    return 1.0 / np.mean(np.log(x[:k] / x[k]))


def block_boot(x, stat):
    n = len(x)
    nb = int(np.ceil(n / BLOCK))
    out = np.empty(B)
    for b in range(B):
        idx = (rng.integers(0, n - BLOCK + 1, nb)[:, None] + np.arange(BLOCK)).ravel()[:n]
        out[b] = stat(x[idx])
    return out


res = {}
for name in ['btc', 'sp500']:
    r = np.log(load_close(name)).diff().dropna()
    pre = r.loc[:'2024-01-10']
    post = r.loc[BREAK:]
    if name == 'sp500':                        # aceeasi lungime ca la Bitcoin: ultimii ~9 ani inainte de ruptura
        pre = pre.loc['2014-09-17':]
    a = {}
    for lab, x in [('pre', pre), ('post', post)]:
        v = np.abs(x.values)
        k = int(FRAC * len(v))
        al = hill(v, k)
        bs = block_boot(v, lambda z, k=k: hill(z, k))
        a[lab] = dict(start=str(x.index[0].date()), end=str(x.index[-1].date()), n=len(v), k=k, alpha=al,
                      se_iid=al / np.sqrt(k), se_boot=float(bs.std(ddof=1)), boot=bs)
    diff = a['post']['alpha'] - a['pre']['alpha']
    z_iid = diff / np.hypot(a['pre']['se_iid'], a['post']['se_iid'])
    z_boot = diff / np.hypot(a['pre']['se_boot'], a['post']['se_boot'])
    for lab in a:
        a[lab].pop('boot')
    # diferenta minima detectabila (test bilateral 5%, putere 80%) cu erorile bootstrap
    mde = 2.8 * np.hypot(a['pre']['se_boot'], a['post']['se_boot'])
    res[name] = dict(pre=a['pre'], post=a['post'], diff=diff, z_iid=z_iid, z_boot=z_boot, mde=mde)

if __name__ == '__main__':
    print(json.dumps(res, indent=1))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(res, f, indent=1)

"""
ai_discovery_case.py -- Capitolul 2, sectiunea "AI for Scientific Discovery": mini-caz
=====================================================================================
Ipoteza: ETF-urile spot pe Bitcoin (tranzactionate din 11 ian. 2024) au facut Bitcoin mai eficient (forma slaba).
H0: rho1_post = rho1_pre si VR(5)_post = VR(5)_pre; ferestre simetrice de aceeasi lungime in jurul datei.
Statistici ca in capitol: rho1 cu eroare standard robusta la heteroscedasticitate, VR(5) cu z* (Lo-MacKinlay).
Test de diferenta: z = (rho_post - rho_pre) / sqrt(se_pre^2 + se_post^2).
Placebo: aceeasi statistica la date false (11 ianuarie 2016-2023, ferestre de aceeasi lungime).
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import log_returns  # noqa: E402
from eff_tests import variance_ratio  # noqa: E402

BREAK = pd.Timestamp('2024-01-11')


def stats_win(x):
    e = x - x.mean()
    tau1 = (e.values[1:] ** 2 * e.values[:-1] ** 2).sum() / (e ** 2).sum() ** 2
    vr, _, zs = variance_ratio(x, 5)
    return dict(start=str(x.index[0].date()), end=str(x.index[-1].date()), n=len(x),
                rho1=float(x.autocorr(1)), se=float(np.sqrt(tau1)), vr5=float(vr), zstar5=float(zs))


def split(r, date):
    post = r.loc[date:]
    return r.loc[:date - pd.Timedelta(days=1)].iloc[-len(post):], post


r = log_returns('btc', start='2011-01-01')
post_full = r.loc[BREAK:]
L = len(post_full)
pre, post = r.loc[:BREAK - pd.Timedelta(days=1)].iloc[-L:], post_full
a, b = stats_win(pre), stats_win(post)
z = (b['rho1'] - a['rho1']) / np.hypot(a['se'], b['se'])
out = dict(pre=a, post=b, drho=b['rho1'] - a['rho1'], z_diff=float(z),
           mde_rho=float(2.8 * np.hypot(a['se'], b['se'])))
# placebo: date false, aceeasi lungime a ferestrelor, ambele ferestre inainte de data reala
plac = []
for y in range(2016, 2024):
    d = pd.Timestamp(f'{y}-01-11')
    q = r.loc[d:].iloc[:L]
    p = r.loc[:d - pd.Timedelta(days=1)].iloc[-L:]
    if len(p) < L or q.index[-1] >= BREAK:      # fereastra placebo nu atinge data reala
        continue
    sp, sq = stats_win(p), stats_win(q)
    plac.append(dict(date=str(d.date()), drho=sq['rho1'] - sp['rho1'],
                     z=(sq['rho1'] - sp['rho1']) / np.hypot(sp['se'], sq['se'])))
out['placebo'] = plac
out['placebo_n'] = len(plac)
out['placebo_nsig'] = int(sum(abs(p['z']) > 1.96 for p in plac))
out['placebo_maxabsz'] = float(max(abs(p['z']) for p in plac))

if __name__ == '__main__':
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)

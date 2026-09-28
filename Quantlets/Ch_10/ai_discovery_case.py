"""
ai_discovery_case.py -- Capitolul 10, secțiunea „AI pentru descoperire științifică”: mini-caz
=============================================================================================
Întrebare: măsoară estimatorul Corwin--Schultz (CS) din bare zilnice costul tranzacționării sau volatilitatea?

  * Pasul 0 (replicare): mediana CS pe grupuri (US, BVB, cripto), cifrele din curs (ch10_results.json)
  * Implicații testabile, pe secțiunea transversală a celor 25 de active (septembrie 2024 -- septembrie 2026):
      H_spread: rangul CS urmează rangul ilichidității Amihud (costul real al tranzacționării)
      H_vol:    rangul CS urmează rangul volatilității zilnice (abaterea standard a randamentelor log)
  * Statistici: corelații Spearman, corelația parțială Spearman CS--Amihud controlând volatilitatea,
    bootstrap pe active (10 000 de replicări) pentru diferența rho(CS, vol) - rho(CS, Amihud)
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import ASSETS, GROUPS, returns   # noqa: E402

START2 = '2024-09-19'
SEED = 7


def partial_spearman(x, y, z):
    """Corelația parțială Spearman dintre x și y, controlând z (pe ranguri)."""
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return float(np.corrcoef(ex, ey)[0, 1])


def main():
    R = json.load(open(os.path.join(HERE, 'ch10_results.json')))
    keys = list(ASSETS)
    cs = np.array([R['spreads'][k]['cs'] for k in keys])
    il = np.array([R['amihud'][k]['illiq'] for k in keys])
    vol = np.array([1e4 * returns(k, START2).std() for k in keys])         # bp pe zi
    rep = {g: float(np.median([R['spreads'][k]['cs'] for k in GROUPS[g]])) for g in GROUPS}
    r_cs_vol = stats.spearmanr(cs, vol)
    r_cs_il = stats.spearmanr(cs, il)
    r_vol_il = stats.spearmanr(vol, il)
    rng = np.random.default_rng(SEED)
    diff = []
    for _ in range(10000):
        i = rng.integers(0, len(keys), len(keys))
        diff.append(stats.spearmanr(cs[i], vol[i])[0] - stats.spearmanr(cs[i], il[i])[0])
    diff = np.array(diff)
    # robustete: bootstrap stratificat pe piete (reesantionam activele in interiorul fiecarei piete, compozitia ramane fixa)
    grp = np.array([ASSETS[k][2] for k in keys])
    strata = [np.flatnonzero(grp == g) for g in GROUPS]
    diff_s = []
    for _ in range(10000):
        i = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in strata])
        diff_s.append(stats.spearmanr(cs[i], vol[i])[0] - stats.spearmanr(cs[i], il[i])[0])
    diff_s = np.array(diff_s)
    # excluderea pe rand a cate unei piete
    lomo = {}
    for g in GROUPS:
        m = grp != g
        lomo[g] = float(stats.spearmanr(cs[m], vol[m])[0] - stats.spearmanr(cs[m], il[m])[0])
    out = dict(n=len(keys), replicated_median_cs=rep,
               rho_cs_vol=float(r_cs_vol[0]), p_cs_vol=float(r_cs_vol[1]),
               rho_cs_illiq=float(r_cs_il[0]), p_cs_illiq=float(r_cs_il[1]),
               rho_vol_illiq=float(r_vol_il[0]), p_vol_illiq=float(r_vol_il[1]),
               partial_cs_illiq_given_vol=partial_spearman(cs, il, vol),
               partial_cs_vol_given_illiq=partial_spearman(cs, vol, il),
               diff=float(r_cs_vol[0] - r_cs_il[0]),
               diff_lo=float(np.nanpercentile(diff, 2.5)), diff_hi=float(np.nanpercentile(diff, 97.5)),
               diff_s_lo=float(np.nanpercentile(diff_s, 2.5)), diff_s_hi=float(np.nanpercentile(diff_s, 97.5)),
               diff_lomo=lomo,
               vol_bp={k: float(v) for k, v in zip(keys, vol)})
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'vol_bp'}, indent=1))


if __name__ == '__main__':
    main()

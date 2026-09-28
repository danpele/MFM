"""
ai_discovery_case.py -- Capitolul 5, sectiunea "AI for Scientific Discovery": mini-studiu de caz
================================================================================================
Ipoteza H1: asimetria (GJR-t) imbunatateste prognoza QLIKE pe o zi fata de GARCH-t (S&P 500, 2016-2026).
Pasul 1 (replicare): aceleasi prognoze OOS ca in capitol (parametri reestimati la inceputul fiecarui an,
fereastra in expansiune din 2000); statistica Diebold-Mariano pe QLIKE, HAC cu 5 decalaje.
Pasul 2 (implicatie testabila): daca H1 vine din efectul de levier, castigul d_t = QLIKE(GJR) - QLIKE(GARCH)
trebuie sa fie concentrat in zilele de dupa un randament negativ (r_{t-1} < 0).
Pasul 3 (robustete pre-inregistrata): fara 2020; subperioadele 2016-2020 si 2021-2026.
Date: data/market/GSPC.INDX.csv (prin mfm_data). Iesire: ai_discovery_case.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import pct_returns            # noqa: E402
from garch_tools import fit_garch, qlike, dm_test   # noqa: E402

FIRST = 2016
MODELS = [('GARCH', 't', 'GARCH-t'), ('GJR', 't', 'GJR-t')]

r = pct_returns('sp500')
idx = r.index
out1 = {lab: pd.Series(np.nan, index=idx) for *_, lab in MODELS}
for y in range(FIRST, idx[-1].year + 1):
    start = idx[idx < f'{y}-01-01'][-1]
    end = idx[idx <= f'{y}-12-31'][-1]
    orig = idx[(idx >= start) & (idx < end)]
    for vol, dist, lab in MODELS:
        f = fit_garch(r, vol, dist, last_obs=idx[idx >= f'{y}-01-01'][0])
        fc = f.res.forecast(horizon=1, start=start, reindex=False).variance / f.c ** 2
        fc = fc.loc[orig]
        pos = idx.get_indexer(fc.index)
        out1[lab].iloc[pos + 1] = fc.iloc[:, 0].values
f1 = pd.DataFrame(out1).loc[f'{FIRST}-01-01':].dropna()
proxy = (r ** 2).reindex(f1.index)
LG, LJ = qlike(proxy, f1['GARCH-t']), qlike(proxy, f1['GJR-t'])
prev = r.shift(1).reindex(f1.index)          # randamentul zilei t-1, cunoscut la momentul prognozei


def dm(mask):
    d = dm_test(LJ[mask], LG[mask])
    return {'n': int(mask.sum()), 'mean_diff': d['mean_diff'], 't': d['t'], 'p': d['p']}


allm = pd.Series(True, index=f1.index)
yrs = f1.index.year
res = {
    'n': len(f1), 'first': str(f1.index[0].date()), 'last': str(f1.index[-1].date()),
    'qlike_garch_t': float(LG.mean()), 'qlike_gjr_t': float(LJ.mean()),
    'full': dm(allm),
    'after_neg': dm(prev < 0), 'after_pos': dm(prev >= 0),
    'ex2020': dm(pd.Series(yrs != 2020, index=f1.index)),
    'y2016_2020': dm(pd.Series(yrs <= 2020, index=f1.index)),
    'y2021_2026': dm(pd.Series(yrs >= 2021, index=f1.index)),
}
with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))

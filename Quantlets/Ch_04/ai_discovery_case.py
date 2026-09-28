"""
ai_discovery_case.py -- Capitolul 4, sectiunea "AI for Scientific Discovery": mini-studiu de caz
================================================================================================
Ipoteza: o regula de optimizare bate 1/N out of sample (diferenta de Sharpe > 0).
Pasul 1 (replicare): diferenta MV-LO minus 1/N pe universul multi-activ si valoarea p bootstrap.
Pasul 2 (inferenta pe familia de teste): cele 21 de teste ale capitolului (7 reguli x 3 universuri),
corectii Holm (FWER) si Benjamini-Hochberg (FDR) pe valorile p HAC (Ledoit-Wolf, 2008).
Intrare: ch4_results.json (produs de generate_all_charts.py din data/market); iesire: ai_discovery_case.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, 'ch4_results.json')) as f:
    ST = json.load(f)['sharpe_tests']

rows = [(u, r, v['diff'], v['p_hac'], v['p_boot']) for u in ST for r, v in ST[u].items()]
m = len(rows)
p = np.array([x[3] for x in rows])
order = np.argsort(p)
# Holm (FWER): p_(k) * (m - k + 1), maxim cumulat
holm = np.empty(m)
holm[order] = np.minimum(1, np.maximum.accumulate(p[order] * (m - np.arange(m))))
# Benjamini-Hochberg (FDR): p_(k) * m / k, minim cumulat de la coada
bh_sorted = np.minimum.accumulate((p[order] * m / np.arange(1, m + 1))[::-1])[::-1]
bh = np.empty(m)
bh[order] = np.minimum(1, bh_sorted)
i_mvlo = [i for i, x in enumerate(rows) if x[:2] == ('Multi-asset', 'MV-LO')][0]

mvlo = ST['Multi-asset']['MV-LO']
# Putere: eroarea standard implicata de testul HAC si lungimea OOS necesara pentru putere 80% la 5% bilateral
from scipy import stats   # noqa: E402
with open(os.path.join(HERE, 'ch4_results.json')) as f:
    T_OOS = json.load(f)['oos']['Multi-asset']['T']            # luni OOS, universul multi-activ (mai 2012 - iulie 2026)
se = mvlo['diff'] / stats.norm.ppf(1 - mvlo['p_hac'] / 2)
T80 = T_OOS * ((stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) * se / mvlo['diff']) ** 2
out = {
    'se_hac': float(se), 'T_oos': T_OOS, 'T80_months': float(T80), 'T80_years': float(T80 / 12),
    'm_tests': m,
    'replicate': {'diff': mvlo['diff'], 'p_boot': mvlo['p_boot'], 'p_hac': mvlo['p_hac']},
    'n_p_below_05': int((p < 0.05).sum()),
    'expected_below_05': 0.05 * m,
    'n_positive_diff': int(sum(x[2] > 0 for x in rows)),
    'min_p': float(p.min()),
    'min_holm': float(holm.min()),
    'min_bh': float(bh.min()),
    'bh_discoveries_10': int((bh <= 0.10).sum()),
    'mvlo_holm': float(holm[i_mvlo]),
    'mvlo_bh': float(bh[i_mvlo]),
    'table': [dict(universe=u, rule=r, diff=d, p_hac=ph, holm=float(h), bh=float(b))
              for (u, r, d, ph, pb), h, b in zip(rows, holm, bh)],
}
with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'table'}, indent=1))

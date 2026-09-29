"""
ai_discovery_case.py -- Capitolul 3, sectiunea "AI for Scientific Discovery": mini-caz
=====================================================================================
Ipoteza (McLean & Pontiff, 2016): prima de momentum scade dupa publicare.
Momentum: factorul MOM (Kenneth French Data Library), lunar. Jegadeesh & Titman (1993): esantion 1965-1989,
publicat in martie 1993. Regresia MOM_t = a + b1 PostSample_t + b2 PostPub_t + e_t, erori Newey-West,
PostSample = 1 in ianuarie 1990 - martie 1993, PostPub = 1 din aprilie 1993; esantion din ianuarie 1965.
H0: b2 = 0 (nicio scadere fata de media din esantion). Scaderea relativa = -b2 / a.
b2 masoara scaderea TOTALA fata de esantionul original; efectul incremental al publicarii fata de
perioada post-esantion este b2 - b1, cu eroarea standard din covarianta Newey-West a lui (b1, b2).
Placebo: aceeasi regresie pentru Mkt-RF (nicio publicare in 1993).
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import factors, ols_hac  # noqa: E402

F = factors('M').loc['1965-01-01':'2026-08-31']      # esantion fixat: ianuarie 1965 - august 2026
ps = ((F.index >= '1990-01-01') & (F.index < '1993-04-01')).astype(float)
pp = (F.index >= '1993-04-01').astype(float)
X = np.column_stack([ps, pp])
out = {'start': str(F.index[0].date())[:7], 'end': str(F.index[-1].date())[:7], 'T': int(len(F))}


def hac_cov(y, X, lags):
    """Covarianta Newey-West (Bartlett) a coeficientilor OLS, cu termen liber."""
    Z = np.column_stack([np.ones(len(y)), X])
    Zi = np.linalg.inv(Z.T @ Z)
    e = y - Z @ (Zi @ Z.T @ y)
    u = Z * e[:, None]
    S = u.T @ u
    for l in range(1, lags + 1):
        G = u[l:].T @ u[:-l]
        S += (1 - l / (lags + 1)) * (G + G.T)
    return Zi @ S @ Zi


for c in ['MOM', 'Mkt-RF']:
    y = F[c].values * 100
    b, se, t, _, _ = ols_hac(y, X)
    lags = int(np.floor(4 * (len(y) / 100) ** (2 / 9)))
    V = hac_cov(y, X, lags)
    d = b[2] - b[1]
    se_d = np.sqrt(V[2, 2] + V[1, 1] - 2 * V[1, 2])
    out[c] = dict(a=b[0], t_a=t[0], b_ps=b[1], t_ps=t[1], b_pp=b[2], t_pp=t[2],
                  a_ann=12 * b[0], post_ann=12 * (b[0] + b[2]), decay_pct=-100 * b[2] / b[0],
                  incr=d, se_incr=se_d, t_incr=d / se_d,
                  ci_pp=[b[2] - 1.96 * se[2], b[2] + 1.96 * se[2]], ci_incr=[d - 1.96 * se_d, d + 1.96 * se_d])

if __name__ == '__main__':
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)

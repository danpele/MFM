"""
ai_discovery_case.py -- Capitolul 6, sectiunea "AI for Scientific Discovery": mini-studiu de caz
================================================================================================
Ipoteza H1 (canalul inflatiei, Campbell, Pflueger & Viceira, 2020): corelatia actiuni--obligatiuni
este mai mare cand inflatia este mare.
Pasul 1 (replicare): corelatia zilnica SPY--TLT 2002-2021 si 2022-2026 (cifrele capitolului).
Pasul 2 (test): corelatia realizata lunara (din randamentele zilnice ale lunii, transformata Fisher)
regresata pe inflatia anuala CPI cunoscuta la inceputul lunii (luna t-2, din cauza intarzierii publicarii);
erori HAC Newey-West cu 12 decalaje.
Pasul 3 (identificare): acelasi test doar pe 2002-2021, fara ruptura din 2022.
Date: data/market (SPY.US, TLT.US) prin mfm_data; CPIAUCSL (U.S. Bureau of Labor Statistics) din FRED.
Iesire: ai_discovery_case.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import joint_returns   # noqa: E402

R = joint_returns(['spy', 'tlt'])
rep = {'rho_pre': float(R.loc[:'2021-12-31'].corr().iloc[0, 1]),
       'rho_post': float(R.loc['2022-01-01':].corr().iloc[0, 1])}

# corelatia realizata lunara (cel putin 15 zile in luna)
g = R.groupby(R.index.to_period('M'))
rho_m = g.apply(lambda x: x['spy'].corr(x['tlt']) if len(x) >= 15 else np.nan).dropna()
rho_m = rho_m.iloc[1:-1] if rho_m.index[-1] >= pd.Period('2026-09', 'M') else rho_m.iloc[1:]  # fara lunile incomplete
z_m = np.arctanh(rho_m)

cpi = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL', index_col=0, parse_dates=True).iloc[:, 0]
cpi.index = cpi.index.to_period('M')
infl = 100 * (cpi / cpi.shift(12) - 1)
x = infl.shift(2).reindex(z_m.index)        # inflatia publicata inainte de inceputul lunii t
df = pd.DataFrame({'z': z_m, 'rho': rho_m, 'infl': x}).dropna()


def reg(d):
    ols = sm.OLS(d['z'], sm.add_constant(d['infl'])).fit(cov_type='HAC', cov_kwds={'maxlags': 12})
    return {'n': int(len(d)), 'first': str(d.index[0]), 'last': str(d.index[-1]),
            'a': float(ols.params['const']), 'b': float(ols.params['infl']), 'b_se': float(ols.bse['infl']),
            't': float(ols.tvalues['infl']), 'p': float(ols.pvalues['infl']), 'r2': float(ols.rsquared)}


hi = df['infl'] > 3
res = {'replicate': rep,
       'full': reg(df), 'pre2022': reg(df.loc[:'2021-12']),
       'mean_rho_hi': float(df.loc[hi, 'rho'].mean()), 'mean_rho_lo': float(df.loc[~hi, 'rho'].mean()),
       'n_hi': int(hi.sum()), 'n_lo': int((~hi).sum()),
       'n_hi_pre2022': int(hi.loc[:'2021-12'].sum())}
with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))

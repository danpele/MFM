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
Iesire: ai_discovery_case.json si graficul ch6_ai_inflation.
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
import matplotlib.pyplot as plt   # noqa: E402
from generate_all_charts import save_fig, MainBlue, IDAred, Forest, Amber   # noqa: E402

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


def fig_ai_inflation(df, res):
    """Corelatia lunara SPY-TLT fata de inflatia cunoscuta la inceputul lunii, inainte si dupa 2022, cu dreptele
    estimate (pe scara Fisher, transformate inapoi) si intervalele HAC de 95% ale pantei."""
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 4.2), gridspec_kw=dict(height_ratios=[2.2, 1]))
    ax = axes[0]
    pre = df.index <= pd.Period('2021-12', 'M')
    ax.scatter(df.loc[pre, 'infl'], df.loc[pre, 'rho'], s=6, color=MainBlue, alpha=0.6, label='Months 2002-2021')
    ax.scatter(df.loc[~pre, 'infl'], df.loc[~pre, 'rho'], s=8, color=IDAred, alpha=0.8, label='Months 2022-2026')
    xg = np.linspace(df['infl'].min(), df['infl'].max(), 100)
    for k, col, ls, lab in (('full', Amber, '-', 'Fitted, full sample'), ('pre2022', Forest, '--', 'Fitted, 2002-2021 only')):
        ax.plot(xg, np.tanh(res[k]['a'] + res[k]['b'] * xg), color=col, ls=ls, lw=1.6, label=lab)
    ax.axhline(0, color='black', lw=0.5)
    ax.set_xlabel('US CPI inflation known at the start of the month (%)')
    ax.set_ylabel('Monthly SPY-TLT correlation')
    ax = axes[1]
    for i, (k, col, lab) in enumerate((('full', Amber, 'full sample'), ('pre2022', Forest, '2002-2021'))):
        b, se = res[k]['b'], res[k]['b_se']
        ax.errorbar(b, i, xerr=1.96 * se, fmt='o', color=col, capsize=3, label=f'Slope b, {lab}, 95% HAC interval')
    ax.axvline(0, color='black', lw=0.8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Full', '2002-2021'])
    ax.set_ylim(-0.7, 1.7)
    ax.set_xlabel('b per percentage point of inflation')
    hs, ls_ = [], []
    for a_ in axes:
        h_, l_ = a_.get_legend_handles_labels()
        hs += h_
        ls_ += l_
    fig.tight_layout()
    fig.legend(hs, ls_, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False, fontsize=7)
    save_fig('ch6_ai_inflation')


fig_ai_inflation(df, res)
with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))

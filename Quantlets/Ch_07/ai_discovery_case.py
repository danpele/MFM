"""
ai_discovery_case.py -- Capitolul 7, sectiunea "AI for Scientific Discovery": mini-studiu de caz
================================================================================================
Intrebare: putem ordona statistic modelele de (VaR 1%, ES 1%) desi ES singur nu este elicitabil?
Pasul 1 (replicare): rata de depasire a VaR 1% FHS pe S&P 500, 2006-2026 (cifra capitolului), dupa ce
pierderile din ch7_rolling_sp500.csv sunt recalculate din data/market/GSPC.INDX.csv.
Pasul 2 (test): pierderea FZ0 a lui Patton, Ziegel & Chen (2019) pentru perechea (VaR, ES), test
Diebold-Mariano cu erori HAC (5 decalaje): FHS vs GARCH cu socuri Normale; EVT conditionat vs FHS.
Pasul 3 (putere): zile in coada si subperioade 2006-2015 / 2016-2026.
Iesire: ai_discovery_case.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import log_returns   # noqa: E402

ALPHA = 0.01
d = pd.read_csv(os.path.join(HERE, 'ch7_rolling_sp500.csv'), index_col='date', parse_dates=True).loc['2006-01-01':]
r = log_returns('sp500')
max_gap = float((d["loss"] + 100 * r.reindex(d.index)).abs().max())  # pierderea = -100 x randamentul log

# GARCH cu socuri Normale: ES din aceeasi medie si volatilitate ca VaR-ul salvat
z = stats.norm.ppf(1 - ALPHA)
m_neg = d['ngarch_var'] - d['sigma'] * z                            # = -mu_t
d['ngarch_es'] = m_neg + d['sigma'] * stats.norm.pdf(z) / ALPHA

Y = -d['loss']                                                       # randamentul


def fz0(var, es):
    """Pierderea FZ0 (Patton, Ziegel & Chen, 2019) cu v = -VaR < 0, e = -ES < 0."""
    v, e = -var, -es
    return -((Y <= v) * (v - Y)) / (ALPHA * e) + v / e + np.log(-e) - 1


L = {'FHS': fz0(d['fhs_var'], d['fhs_es']), 'cEVT': fz0(d['cevt_var'], d['cevt_es']),
     'GARCH-N': fz0(d['ngarch_var'], d['ngarch_es'])}


def dm(a, b, mask=None):
    x = (L[a] - L[b]) if mask is None else (L[a] - L[b])[mask]
    ols = sm.OLS(x.values, np.ones(len(x))).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    return {'n': int(len(x)), 'mean_diff': float(x.mean()), 't': float(ols.tvalues[0]), 'p': float(ols.pvalues[0])}


early = pd.Series(d.index.year <= 2015, index=d.index)
res = {
    'n': int(len(d)), 'first': str(d.index[0].date()), 'last': str(d.index[-1].date()),
    'max_abs_gap_loss': max_gap,
    'exc_fhs': float((d['loss'] > d['fhs_var']).mean()),
    'exc_cevt': float((d['loss'] > d['cevt_var']).mean()),
    'exc_ng': float((d['loss'] > d['ngarch_var']).mean()),
    'n_exc_fhs': int((d['loss'] > d['fhs_var']).sum()),
    'mean_fz0': {k: float(v.mean()) for k, v in L.items()},
    'fhs_vs_ng': dm('FHS', 'GARCH-N'), 'cevt_vs_fhs': dm('cEVT', 'FHS'),
    'fhs_vs_ng_early': dm('FHS', 'GARCH-N', early), 'fhs_vs_ng_late': dm('FHS', 'GARCH-N', ~early),
    'cevt_vs_fhs_early': dm('cEVT', 'FHS', early), 'cevt_vs_fhs_late': dm('cEVT', 'FHS', ~early),
}
with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))


# Graficul mini-studiului de caz: diferentele medii FZ0 si intervalele HAC de 95%, pe perechi si subperioade
sys.path.insert(0, HERE)
from generate_all_charts import save_fig, MainBlue, IDAred, Forest  # noqa: E402
plt.rcParams['font.size'] = 9
fig, ax = plt.subplots(figsize=(5.4, 2.4))
rows = [('FHS - GARCH-N, 2006-2026', 'fhs_vs_ng', MainBlue), ('FHS - GARCH-N, 2006-2015', 'fhs_vs_ng_early', MainBlue),
        ('FHS - GARCH-N, 2016-2026', 'fhs_vs_ng_late', MainBlue), ('cEVT - FHS, 2006-2026', 'cevt_vs_fhs', IDAred),
        ('cEVT - FHS, 2006-2015', 'cevt_vs_fhs_early', IDAred), ('cEVT - FHS, 2016-2026', 'cevt_vs_fhs_late', IDAred)]
for i, (lab, k, c) in enumerate(rows):
    y = len(rows) - 1 - i
    m, se = res[k]['mean_diff'], abs(res[k]['mean_diff'] / res[k]['t'])
    ax.plot([m - 1.96 * se, m + 1.96 * se], [y, y], color=c, lw=2.4, solid_capstyle='butt')
    ax.plot([m], [y], 'o', color=c, ms=4.5)
    ax.text(m + 1.96 * se + 0.012, y, f"t = {res[k]['t']:.2f}", va='center', fontsize=7.5, color='black')
ax.axvline(0, color='#1F2A44', lw=0.7, ls='--')
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
ax.set_xlabel('Mean FZ0 score difference (negative favours the first model)')
ax.set_xlim(-0.38, 0.08)
ax.plot([], [], color=MainBlue, lw=2.4, label='Shape of the shocks: FHS vs GARCH with Normal shocks')
ax.plot([], [], color=IDAred, lw=2.4, label='Tail model: conditional EVT vs FHS')
plt.tight_layout()
fig.legend(*ax.get_legend_handles_labels(), loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=1, frameon=False, fontsize=8)
save_fig('ch7_ai_fz0')

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

def fig_momentum_decay():
    """Media MOM in cele trei perioade (IC 95% Newey-West) si scaderea totala vs incrementala, cu placebo Mkt-RF."""
    import matplotlib.pyplot as plt
    import generate_all_charts as g
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.1, 1]})
    y = F['MOM'].values * 100
    lags = int(np.floor(4 * (len(y) / 100) ** (2 / 9)))
    b = np.linalg.lstsq(np.column_stack([np.ones(len(y)), X]), y, rcond=None)[0]
    V = hac_cov(y, X, lags)
    per = [('In sample\n1965-1989', np.array([1, 0, 0])), ('Post-sample\n1990-Mar 1993', np.array([1, 1, 0])),
           ('Post-publication\nApr 1993-2026', np.array([1, 0, 1]))]
    ax = axes[0]
    for k, (lab, c) in enumerate(per):
        m, se = c @ b, np.sqrt(c @ V @ c)
        ax.errorbar(k, m, yerr=1.96 * se, fmt='o', color=[g.MainBlue, g.Amber, g.IDAred][k], capsize=4, lw=1.1, ms=6)
        ax.annotate(f'{m:.2f}%', (k, m), xytext=(8, -3), textcoords='offset points', fontsize=7, color='black')
    ax.axhline(0, color=g.Gray, lw=0.6, ls=':')
    ax.set_xticks(range(3), [p[0] for p in per], fontsize=7)
    ax.set_xlim(-0.5, 2.6)
    ax.set_ylabel('MOM mean, % a month')
    ax.set_title('Momentum by period, 95% intervals (Newey-West)', fontsize=9, loc='left')
    ax = axes[1]
    rows = [(r'Total decline $b_2$', 'ci_pp', 'b_pp'), (r'Incremental $b_2 - b_1$', 'ci_incr', 'incr')]
    for j, (fac, col, off) in enumerate([('MOM', g.MainBlue, 0.12), ('Mkt-RF', g.Forest, -0.12)]):
        for k, (lab, ci, est) in enumerate(rows):
            e, (lo, hi) = out[fac][est], out[fac][ci]
            ax.errorbar(e, 1 - k + off, xerr=[[e - lo], [hi - e]], fmt='o' if fac == 'MOM' else 's', color=col,
                        capsize=3, lw=1.0, label=(f'{fac}' + (' (placebo)' if fac == 'Mkt-RF' else '')) if k == 0 else '_n')
    ax.axvline(0, color=g.Gray, lw=0.7, ls=':')
    ax.set_yticks([1, 0], [r[0] for r in rows], fontsize=7)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel('% a month')
    ax.set_title('Decline estimates, 95% intervals', fontsize=9, loc='left')
    plt.tight_layout()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    ymin = min(a.get_tightbbox(r).transformed(fig.transFigure.inverted()).y0 for a in fig.axes)
    fig.legend(*axes[1].get_legend_handles_labels(), loc='upper center', bbox_to_anchor=(0.5, ymin - 0.01), ncol=2,
               frameon=False)
    g.save_fig('ch3_ai_momentum')


if __name__ == '__main__':
    fig_momentum_decay()
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)

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
# placebo: false dates, same window length, both windows before the real date
plac = []
for y in range(2016, 2024):
    d = pd.Timestamp(f'{y}-01-11')
    q = r.loc[d:].iloc[:L]
    p = r.loc[:d - pd.Timedelta(days=1)].iloc[-L:]
    if len(p) < L or q.index[-1] >= BREAK:      # the placebo window does not reach the real date
        continue
    sp, sq = stats_win(p), stats_win(q)
    plac.append(dict(date=str(d.date()), drho=sq['rho1'] - sp['rho1'],
                     z=(sq['rho1'] - sp['rho1']) / np.hypot(sp['se'], sq['se'])))
out['placebo'] = plac
out['placebo_n'] = len(plac)
out['placebo_nsig'] = int(sum(abs(p['z']) > 1.96 for p in plac))
out['placebo_maxabsz'] = float(max(abs(p['z']) for p in plac))



def fig_ai_etf(o):
    """rho1 before/after the spot ETFs with robust intervals, the difference with +-MDE and the placebo comparison."""
    from generate_all_charts import plt, MainBlue, IDAred, Amber, Forest, Purple, Gray, save_fig
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.0), gridspec_kw={'width_ratios': [1.1, 1.4]})
    ax = axes[0]
    rows = [('Before', o['pre']['rho1'], o['pre']['se'], MainBlue), ('After', o['post']['rho1'], o['post']['se'], Forest),
            ('After - before', o['drho'], np.hypot(o['pre']['se'], o['post']['se']), IDAred)]
    for i, (lab, v, se, c) in enumerate(rows):
        ax.errorbar(i, v, yerr=1.96 * se, fmt='o', color=c, capsize=4)
        ax.text(i + 0.08, v, f'{v:+.3f}', fontsize=7.5, va='center', color='black')
    ax.errorbar(2.3, 0, yerr=o['mde_rho'], fmt='none', ecolor=Purple, capsize=6, lw=1.6)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(range(3))
    ax.set_xticklabels([r[0] for r in rows], fontsize=8)
    ax.set_xlim(-0.5, 2.7)
    ax.set_ylabel(r'Lag-1 autocorrelation $\hat\rho_1$')
    ax.set_title(f"Two windows of {o['post']['n']} days around 11 Jan 2024", fontsize=8.5, loc='left')
    ax = axes[1]
    pz = [p['z'] for p in o['placebo']]
    yrs = [p['date'][:4] for p in o['placebo']]
    ax.bar(range(len(pz)), pz, color=Amber, width=0.6)
    ax.bar(len(pz), o['z_diff'], color=IDAred, width=0.6)
    for v in (-1.96, 1.96):
        ax.axhline(v, color=Gray, ls='--', lw=0.7)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(range(len(pz) + 1))
    ax.set_xticklabels(yrs + ['2024\n(ETF)'], fontsize=7.5)
    ax.set_ylabel(r'$z$ of the change in $\hat\rho_1$')
    ax.set_title('Placebo dates (11 January) and the ETF date', fontsize=8.5, loc='left')
    h = [plt.Line2D([], [], marker='o', ls='', color='black', label='Estimate with robust 95% interval'),
         plt.Line2D([], [], color=Purple, lw=1.6, label=f"Minimum detectable change $\\pm${o['mde_rho']:.2f}"),
         plt.Rectangle((0, 0), 1, 1, color=Amber, label='Placebo z'), plt.Rectangle((0, 0), 1, 1, color=IDAred, label='ETF z'),
         plt.Line2D([], [], color=Gray, ls='--', label=r'$\pm 1.96$')]
    fig.legend(handles=h, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch2_ai_etf')


if __name__ == '__main__':
    print(json.dumps(out, indent=1))
    fig_ai_etf(out)
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)

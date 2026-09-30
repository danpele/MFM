"""
case_study_race.py -- Chapter 10 case study: what the speed race is worth (Aquilina, Budish & O'Neill, 2022)
===========================================================================================================
The extrapolation of the paper's Section VI (Table XV), applied to SPY:
  * col. 2:  Pi_t = 0.4213 bp x V_t
  * col. 6:  Pi_t = 0.3354 bp x V_t + 0.0066 bp x sigma_t x Vbar   (sigma_t = annualised realised volatility, %)
  * the extreme scenarios of Table XIV: a tax between 0.20 and 0.74 bp of traded value
Data: SPY 5-minute bars, regular session (09:30-16:00, New York time), days with all 78 bars, 2021-2025.
  V_t     = sum (close x volume) over the 78 bars
  sigma_t = 100 sqrt(252 sum r^2), from 5-minute log returns (first bar: from the open)
Charts: ch10_race_tax (implied daily tax, col. 6, at mean traded value V_t = Vbar), ch10_race_prize (implied annual prize, col. 2 and col. 6)
Output: case_study_race.json
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import intraday_spy   # noqa: E402
from generate_all_charts import (MainBlue, IDAred, Forest,  # noqa: E402
                                 save_fig, legend_outside_bottom, jsonable)

# coefficients of Aquilina, Budish & O'Neill (2022), Table XV col. 2 and 6; Table XIV; in bp
ABO = dict(col2=0.4213, col6_v=0.3354, col6_s=0.0066, lo=0.20, hi=0.74, tax_lse=0.419)
YEARS = (2021, 2025)


def race_daily(s):
    """V_t (USD) and sigma_t (%, annualised) for each complete day; implied daily tax by col. 6 at V_t = Vbar (bp)."""
    s = s.loc[s['date'].dt.year.between(*YEARS)]
    d = pd.DataFrame({'V': s.groupby('date')['dv'].sum(),
                      'sigma': 100 * np.sqrt(252 * s.groupby('date')['r'].apply(lambda v: (v ** 2).sum()))})
    d['tax6'] = ABO['col6_v'] + ABO['col6_s'] * d['sigma']
    d['year'] = d.index.year
    return d


def race_prize(d):
    """Implied annual prize (USD million) by col. 2, col. 6 and the extreme scenarios of Table XIV."""
    out = {}
    for y, g in d.groupby('year'):
        V, Vbar = g['V'].sum(), g['V'].mean()
        out[int(y)] = dict(n=int(len(g)), V_tot=float(V), V_mean=float(Vbar), sigma_mean=float(g['sigma'].mean()),
                           col2=float(1e-4 * ABO['col2'] * V / 1e6),
                           col6=float(1e-4 * (ABO['col6_v'] * V + ABO['col6_s'] * Vbar * g['sigma'].sum()) / 1e6),
                           lo=float(1e-4 * ABO['lo'] * V / 1e6), hi=float(1e-4 * ABO['hi'] * V / 1e6))
    return out


def fig_race_tax(d):
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.plot(d.index, d['tax6'], color=MainBlue, lw=0.8, label='Implied daily tax at mean traded value, Table XV col. 6: 0.3354 + 0.0066 x annualised realised volatility of the day (%), in bp')
    ax.axhline(ABO['col2'], color=IDAred, lw=1.0, ls='--', label='Table XV col. 2: 0.4213 bp')
    ax.axhline(ABO['lo'], color=Forest, lw=1.0, ls=':', label='Table XIV lowest and highest scenarios: 0.20 and 0.74 bp')
    ax.axhline(ABO['hi'], color=Forest, lw=1.0, ls=':')
    top = d['tax6'].idxmax()
    ax.annotate(f"{top.day} {top.strftime('%B %Y')}: {d.loc[top, 'tax6']:.2f} bp\n(volatility {d.loc[top, 'sigma']:.1f}%)",
                xy=(top, d.loc[top, 'tax6']), xytext=(pd.Timestamp('2023-06-01'), 0.98), fontsize=8, color='black',
                arrowprops=dict(arrowstyle='->', color='black', lw=0.7))
    ax.set_ylabel('Latency arbitrage tax (bp)')
    ax.set_ylim(0.1, 1.15)
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    plt.tight_layout()
    save_fig('ch10_race_tax')
    t = d['tax6'].sort_values(ascending=False)
    return dict(n=int(len(d)), median=float(d['tax6'].median()), max=float(t.iloc[0]), max_day=str(t.index[0].date()),
                max_sigma=float(d.loc[t.index[0], 'sigma']), top5=[str(x.date()) for x in t.index[:5]],
                share_above_col2=float((d['tax6'] > ABO['col2']).mean()), share_above_hi=float((d['tax6'] > ABO['hi']).mean()))


def fig_race_prize(P):
    ys = sorted(P)
    x = np.arange(len(ys))
    w = 0.36
    fig, ax = plt.subplots(figsize=(9, 3.4))
    b2 = ax.bar(x - w / 2, [P[y]['col2'] for y in ys], w, color=MainBlue, label='Table XV col. 2 (traded value)')
    b6 = ax.bar(x + w / 2, [P[y]['col6'] for y in ys], w, color=IDAred, label='Table XV col. 6 (traded value and volatility)')
    xr = x + w + 0.08                                             # range of the scenarios, to the right of each pair of bars
    ax.vlines(xr, [P[y]['lo'] for y in ys], [P[y]['hi'] for y in ys], color=Forest, lw=1.6,
              label='Range between the Table XIV lowest and highest scenarios (0.20 to 0.74 bp)')
    ax.scatter(np.r_[xr, xr], [P[y]['lo'] for y in ys] + [P[y]['hi'] for y in ys], color=Forest, marker='_', s=120, zorder=3)
    for bars in (b2, b6):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 12, f'{b.get_height():.0f}', ha='center',
                    va='bottom', fontsize=7.5, color='black')
    ax.set_xticks(x + 0.04)
    ax.set_xticklabels([f"{y}\n(mean volatility {P[y]['sigma_mean']:.1f}%)" for y in ys])
    ax.set_ylabel('Implied annual prize, SPY (USD million)')
    legend_outside_bottom(ax, ncol=3, y=-0.22)
    plt.tight_layout()
    save_fig('ch10_race_prize')
    return {y: {k: P[y][k] for k in ('col2', 'col6', 'lo', 'hi', 'sigma_mean')} for y in ys}


def main():
    spy = intraday_spy()
    d = race_daily(spy)
    P = race_prize(d)
    out = dict(coef=ABO, tax=fig_race_tax(d), prize=P)
    fig_race_prize(P)
    with open(os.path.join(HERE, 'case_study_race.json'), 'w') as f:
        json.dump(jsonable(out), f, indent=1)
    print(json.dumps(jsonable(out), indent=1))


if __name__ == '__main__':
    main()

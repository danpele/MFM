"""
crypto_momentum_case.py -- Capitolul 2, studiul de caz Liu & Tsyvinski (2021, RFS): time-series momentum in Bitcoin
==================================================================================================================
Specificatia din sectiunea despre momentum a lucrarii (randamente saptamanale, duminica la duminica, UTC):
  * R_t: randamentul simplu saptamanal al lui Bitcoin (si Ethereum), din preturile zilnice de inchidere (data/market);
  * regresia predictiva R_{t+h} = a + b_h R_t + e, h = 1, ..., 4 saptamani, pe fiecare perioada;
  * sortarea saptamanilor in quintile dupa R_t si media lui R_{t+1} in fiecare quintila (pragurile din perioada);
  * erori standard Newey-West (Bartlett, L = floor(4 (T/100)^(2/9)), fara corectie de esantion mic), ca in Capitolul 1.
Perioadele: esantionul lucrarii (1 ianuarie 2011 - 31 mai 2018; versiunea de lucru NBER w24877), aceeasi perioada de
la 1 ianuarie 2013 (lucrarea, Tabelul 16) si perioada de dupa esantion (1 iunie 2018 - 18 septembrie 2026).
Coeficientul b_1 pe ferestre rolling de 104 saptamani, cu benzi de 1,96 erori standard Newey-West.
Iesire: ch2_crypto_tsmom.json, ch2_crypto_tsmom_weekly.csv, ch2_crypto_tsmom_rolling.csv, graficul
ch2_case_crypto_tsmom (PDF/PNG in charts/).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import matplotlib                                    # noqa: E402
import matplotlib.pyplot as plt                      # noqa: E402
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import load_close, END                 # noqa: E402

# chart style and colours of the chapter (generate_all_charts.py)
plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'], 'font.size': 9,
                     'axes.labelsize': 10, 'axes.titlesize': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.6, 'lines.linewidth': 1.1,
                     'legend.facecolor': 'none', 'legend.framealpha': 0, 'legend.fontsize': 8})
MainBlue, IDAred, Amber, Navy, BandBlue = '#1A3A6E', '#CD0000', '#B5853F', '#1F2A44', '#C5D2E8'
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')

START = {'btc': '2011-01-01', 'eth': '2016-01-01'}          # Bitcoin as in the paper; Ethereum as in the chapter
PERIODS = {'paper': ('2011-01-01', '2018-05-31'),           # sample of the paper (NBER w24877)
           'since2013': ('2013-01-01', '2018-05-31'),       # the paper's Table 16
           'after': ('2018-06-01', END)}                    # after the paper's sample
HORIZONS = (1, 2, 3, 4)
ROLL = 104                                                  # rolling window: two years of weeks
# the paper's numbers, NBER working paper w24877 (Bitcoin, 2011 - May 2018): Table 14 Panel B, Table 15
PAPER = dict(beta=[0.19, 0.22, 0.21, 0.09], t_ols=[3.73, 4.52, 4.26, 1.72], sd_pct=16.64, per_sd_pct=3.16,
             top_pct=11.22, top_sharpe=0.45, bottom_pct=2.60, bottom_sharpe=0.19)


def nw_lag(T):
    return int(np.floor(4 * (T / 100) ** (2 / 9)))


def ols_hac(y, x, L=None):
    """OLS y = a + b x; slope, OLS t, Newey-West t (Bartlett weights, no small-sample correction), R^2."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    T = len(y)
    L = nw_lag(T) if L is None else L
    X = np.column_stack([np.ones(T), x])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    s2 = e @ e / (T - 2)
    u = X * e[:, None]
    S = u.T @ u
    for l in range(1, L + 1):
        G = u[l:].T @ u[:-l]
        S += (1 - l / (L + 1)) * (G + G.T)
    V = XtXi @ S @ XtXi
    se_hac = np.sqrt(V[1, 1])
    r2 = 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))
    return dict(b=float(b[1]), t_ols=float(b[1] / np.sqrt(s2 * XtXi[1, 1])), t_hac=float(b[1] / se_hac),
                se_hac=float(se_hac), r2=float(r2), T=T, L=L)


def weekly_returns(name):
    """Simple weekly returns, Sunday close to Sunday close (UTC daily closes); only complete weeks."""
    p = load_close(name, start=START[name])
    w = p.resample('W-SUN').last()
    w = w[w.index <= p.index[-1]]
    return w.pct_change().dropna().rename(name)


def period_stats(R, a, b):
    r = R.loc[a:b]
    out = dict(start=str(r.index[0].date()), end=str(r.index[-1].date()), weeks=len(r), sd=float(r.std()), reg={})
    for h in HORIZONS:
        y = r.shift(-h).dropna()
        out['reg'][h] = ols_hac(y.values, r.loc[y.index].values)
    x, y = r.iloc[:-1], r.shift(-1).iloc[:-1]
    q = pd.qcut(x, 5, labels=False)
    g = y.groupby(q.values).agg(['mean', 'std', 'count'])
    top, bot = y[q.values == 4], y[q.values == 0]
    out['quintiles'] = dict(mean=g['mean'].tolist(), sharpe=(g['mean'] / g['std']).tolist(), n=g['count'].tolist(),
                            spread=float(top.mean() - bot.mean()),
                            spread_t=float((top.mean() - bot.mean()) / np.sqrt(top.var() / len(top) + bot.var() / len(bot))))
    return out


def rolling_beta(R, window=ROLL):
    rows = []
    x, y = R.iloc[:-1].values, R.shift(-1).iloc[:-1].values
    for i in range(window, len(x) + 1):
        f = ols_hac(y[i - window:i], x[i - window:i])
        rows.append((R.index[i], f['b'], f['se_hac']))     # date of the last R_{t+1} in the window
    return pd.DataFrame(rows, columns=['date', 'beta', 'se_hac']).set_index('date')


def figure(res, roll):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={'width_ratios': [1, 1.45]})
    P, A = res['btc']['paper'], res['btc']['after']
    for k, (d, col, lab, dx) in enumerate([(P, MainBlue, 'Jan 2011 - May 2018 (paper\'s sample)', -0.13),
                                           (A, IDAred, 'Jun 2018 - Sep 2026 (after the sample)', 0.13)]):
        b = np.array([d['reg'][h]['b'] for h in HORIZONS])
        se = np.array([d['reg'][h]['se_hac'] for h in HORIZONS])
        a1.errorbar(np.array(HORIZONS) + dx, b, yerr=1.96 * se, fmt='o', color=col, ms=4, capsize=2.5, lw=1, label=lab)
    a1.plot(HORIZONS, PAPER['beta'], 'D', color=Amber, ms=4.5, label='Liu & Tsyvinski (working paper)')
    a1.axhline(0, color=Navy, lw=0.6)
    a1.set_xticks(HORIZONS, [f'{h}' for h in HORIZONS])
    a1.set_xlabel('Horizon h (weeks)')
    a1.set_ylabel('Slope b_h')
    a1.set_title('Slope of R(t+h) on R(t), 95% NW intervals', fontsize=8.5, loc='left')
    a2.fill_between(roll.index, roll['beta'] - 1.96 * roll['se_hac'], roll['beta'] + 1.96 * roll['se_hac'],
                    color=BandBlue, lw=0, label='95% NW band')
    a2.plot(roll.index, roll['beta'], color=MainBlue, lw=1.1, label='Rolling b_1 (104 weeks)')
    a2.axhline(0, color=Navy, lw=0.6)
    a2.axvline(pd.Timestamp('2018-05-31'), color=IDAred, ls='--', lw=0.9, label="End of paper's sample")
    a2.set_ylabel('Slope b_1')
    a2.set_title('Bitcoin: one-week slope b_1, rolling two-year windows', fontsize=8.5, loc='left')
    plt.tight_layout()
    h1, l1 = a1.get_legend_handles_labels()
    h2, l2 = a2.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    os.makedirs(CHART_DIR, exist_ok=True)
    for ext in ('pdf', 'png'):
        plt.savefig(os.path.join(CHART_DIR, f'ch2_case_crypto_tsmom.{ext}'), bbox_inches='tight', transparent=True,
                    **({'dpi': 180} if ext == 'png' else {}))
    plt.close()
    print('   saved ch2_case_crypto_tsmom')


def main():
    R = {k: weekly_returns(k) for k in START}
    res = {'paper_numbers': PAPER, 'roll_window': ROLL}
    for k in R:
        res[k] = {p: period_stats(R[k], a, b) for p, (a, b) in PERIODS.items() if not (k == 'eth' and p == 'since2013')}
    roll = rolling_beta(R['btc'])
    after = roll.loc['2018-06-01':]
    res['btc']['rolling'] = dict(share_sig=float(np.mean(np.abs(roll['beta'] / roll['se_hac']) > 1.96)),
                                 share_sig_after=float(np.mean(np.abs(after['beta'] / after['se_hac']) > 1.96)),
                                 max_beta=float(roll['beta'].max()), max_date=str(roll['beta'].idxmax().date()),
                                 last_beta=float(roll['beta'].iloc[-1]), last_date=str(roll.index[-1].date()),
                                 n=len(roll))
    json.dump(res, open(os.path.join(HERE, 'ch2_crypto_tsmom.json'), 'w'), indent=1)
    pd.concat(R, axis=1).to_csv(os.path.join(HERE, 'ch2_crypto_tsmom_weekly.csv'), float_format='%.8g')
    roll.to_csv(os.path.join(HERE, 'ch2_crypto_tsmom_rolling.csv'), float_format='%.8g')
    figure(res, roll)
    for k in R:
        for p, d in res[k].items():
            if p == 'rolling':
                continue
            print(k, p, d['start'], d['end'], d['weeks'], 'sd %.4f' % d['sd'],
                  ' '.join('h%d b=%.3f t=%.2f tNW=%.2f' % (h, v['b'], v['t_ols'], v['t_hac']) for h, v in d['reg'].items()),
                  'Q', np.round(100 * np.array(d['quintiles']['mean']), 2), 'spread t %.2f' % d['quintiles']['spread_t'])
    print(res['btc']['rolling'])


if __name__ == '__main__':
    main()

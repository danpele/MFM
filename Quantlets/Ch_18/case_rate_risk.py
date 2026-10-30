"""
case_rate_risk.py -- Capitolul 18, al doilea studiu de caz: riscul de dobanda al bancilor americane si SVB (2023)
================================================================================================================
Studiul: Jiang, E.X., Matvos, G., Piskorski, T., Seru, A. (2024). Monetary tightening and U.S. bank fragility in 2023:
mark-to-market losses and uninsured depositor runs? Journal of Financial Economics 159, 103899.

Logica lucrarii, pe datele cursului (data/market, EODHD): cresterea dobanzilor reduce valoarea de piata a activelor
cu durata lunga; capitalul bancii o absoarbe doar daca valoarea depozitelor (deposit franchise) nu o compenseaza.
  1. doua ETF-uri de titluri de stat americane (IEF: 7-10 ani, TLT: peste 20 de ani) intre 31 decembrie 2021 si
     31 martie 2023, intervalul lucrarii (T1 2022 - T1 2023): randamentul total (pretul ajustat, distributii
     reinvestite) si variatia pretului de inchidere (reperul mark-to-market); ETF-urile sunt portofolii cu
     compozitie schimbatoare, nu reevaluarea bilanturilor bancare;
  2. sensibilitatea la dobanda a actiunilor bancare americane (portofoliul egal ponderat al celor sase banci din
     capitol, reechilibrat zilnic): regresia rolling pe 252 de zile a randamentului zilnic pe randamentul S&P 500 si
     pe variatia randamentului titlului de stat pe 10 ani (in puncte de baza); panta pe dobanda este raportata la
     +100 bp, cu interval de 95% Newey-West (5 lag-uri). Aceeasi regresie pentru IEF da reperul de durata.
  3. schimbarea pantei in 2022: interactiunea variatiei randamentului cu perioada (ian. 2022 - 9 mar. 2023, fata de
     sept. 2012 - dec. 2021), estimata direct, cu erori standard Newey-West; panta este o asociere conditionata, nu
     valoarea deposit franchise.
Iesire: charts/ch18_case_rate_risk.pdf/.png si ch18_case_rate_risk.json.
Rulare: python3 case_rate_risk.py
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import US, prices, read_market  # noqa: E402

plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'], 'font.size': 9, 'axes.labelsize': 10,
                     'axes.titlesize': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.linewidth': 0.6, 'lines.linewidth': 1.1, 'legend.facecolor': 'none',
                     'legend.framealpha': 0, 'legend.fontsize': 8})

# course colours (generate_all_charts.py)
MainBlue, IDAred, Forest, Amber, Purple, Navy, BandBlue = ('#1A3A6E', '#CD0000', '#2E7D32', '#B5853F', '#8E44AD',
                                                           '#1F2A44', '#C5D2E8')
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
OUT_JSON = os.path.join(HERE, 'ch18_case_rate_risk.json')

WINDOW = 252          # rolling window (trading days)
NW_LAGS = 5           # Newey-West lags
BASE, MTM_END = '2021-12-31', '2023-03-31'          # the paper's interval: Q1 2022 to Q1 2023
SVB = '2023-03-10'                                    # FDIC takes over Silicon Valley Bank
PERIODS = [('2012-2019', '2012-01-01', '2019-12-31'), ('2020-2021', '2020-01-01', '2021-12-31'),
           ('Tightening', '2022-01-01', '2023-03-09'), ('SVB to First Republic', '2023-03-10', '2023-05-31'),
           ('After', '2023-06-01', '2026-12-31')]


def load_data():
    """Common trading days of the six US banks, the S&P 500, IEF, TLT and the US 2Y and 10Y yields."""
    P = prices(US + ['SPX'])
    extra = {'IEF': read_market('IEF.US')['adjusted_close'], 'TLT': read_market('TLT.US')['adjusted_close'],
             'IEFc': read_market('IEF.US')['close'], 'TLTc': read_market('TLT.US')['close'],
             'Y10': read_market('US10Y.GBOND')['close'], 'Y2': read_market('US2Y.GBOND')['close']}
    X = pd.concat([P] + [s.rename(k) for k, s in extra.items()], axis=1, join='inner').dropna()
    y10 = read_market('US10Y.GBOND').reindex(X.index)
    stale = (X['Y10'].diff() == 0) & (y10['open'] == y10['high']) & (y10['high'] == y10['low']) & (y10['low'] == y10['close'])
    X = X[~stale]      # a repeated 10Y quote with no intraday range: bond market closed, previous yield carried forward
    D = pd.DataFrame(index=X.index)
    D['bank'] = 100 * (np.exp(np.log(X[US]).diff()) - 1).mean(axis=1)          # equal weights, daily rebalancing
    D['spx'] = 100 * X['SPX'].pct_change()
    D['ief'] = 100 * X['IEF'].pct_change()
    D['tlt'] = 100 * X['TLT'].pct_change()
    D['ief_px'] = 100 * X['IEFc'].pct_change()                                    # price only (closing prices)
    D['tlt_px'] = 100 * X['TLTc'].pct_change()
    D['d10'] = 100 * X['Y10'].diff()                                              # basis points
    D['y10'] = X['Y10']
    D['y2'] = X['Y2']
    return D.dropna()


def ols_nw(y, X, lags=NW_LAGS):
    """OLS coefficients and Newey-West (Bartlett) standard errors."""
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    g = X * u[:, None]
    S = g.T @ g
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = g[L:].T @ g[:-L]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return b, np.sqrt(np.diag(V))


def rate_beta(D, dep='bank', market=True):
    """Return (%) per +100 bp in the 10Y yield, controlling for the S&P 500 if market=True."""
    cols = ['spx', 'd10'] if market else ['d10']
    X = np.column_stack([np.ones(len(D))] + [D[c].values for c in cols])
    b, se = ols_nw(D[dep].values, X)
    return 100 * b[-1], 100 * se[-1]


def rolling_beta(D, dep='bank', market=True, window=WINDOW):
    out = []
    for t in range(window, len(D) + 1):
        b, se = rate_beta(D.iloc[t - window:t], dep, market)
        out.append((D.index[t - 1], b, se))
    return pd.DataFrame(out, columns=['date', 'b', 'se']).set_index('date')


def main():
    D = load_data()
    res = {'start': str(D.index[0].date()), 'end': str(D.index[-1].date()), 'n': int(len(D)), 'window': WINDOW,
           'nw_lags': NW_LAGS, 'periods': {}}
    for lab, a, b in PERIODS:
        S = D.loc[a:b]
        bb, se = rate_beta(S)
        bi, sei = rate_beta(S, 'ief', market=False)
        res['periods'][lab] = {'start': str(S.index[0].date()), 'end': str(S.index[-1].date()), 'n': int(len(S)),
                               'b': bb, 'se': se, 't': bb / se, 'b_ief': bi, 'se_ief': sei}
    # mark-to-market interval of the paper
    M = D.loc[BASE:MTM_END]
    cum = {k: 100 * ((1 + M[k].iloc[1:] / 100).prod() - 1) for k in ['bank', 'spx', 'ief', 'tlt', 'ief_px', 'tlt_px']}
    res['mtm'] = {'base': str(M.index[0].date()), 'end': str(M.index[-1].date()), **cum,
                  'y10_0': M['y10'].iloc[0], 'y10_1': M['y10'].iloc[-1], 'y2_0': M['y2'].iloc[0], 'y2_1': M['y2'].iloc[-1]}
    # SVB week: 8 March (last close before the run) to 17 March 2023
    W = D.loc['2023-03-09':'2023-03-17']
    res['svb_week'] = {k: 100 * ((1 + W[k] / 100).prod() - 1) for k in ['bank', 'spx', 'ief']}
    res['svb_week']['d10'] = W['d10'].sum()
    res['svb_week']['d2'] = 100 * (D.loc['2023-03-17', 'y2'] - D.loc['2023-03-08', 'y2'])

    # direct test of the change in 2022: d10 x 1{Jan 2022 - 9 Mar 2023}, against Sep 2012 - Dec 2021, Newey-West
    S = D.loc[:'2023-03-09']
    T22 = (S.index >= '2022-01-01').astype(float)
    Xi = np.column_stack([np.ones(len(S)), S['spx'], S['d10'], T22, T22 * S['spx'], T22 * S['d10']])
    bi_, sei_ = ols_nw(S['bank'].values, Xi)
    from scipy.stats import norm
    res['interaction'] = {'b_pre': 100 * bi_[2], 'se_pre': 100 * sei_[2], 'diff': 100 * bi_[5], 'se_diff': 100 * sei_[5],
                          't_diff': bi_[5] / sei_[5], 'p_diff': 2 * norm.sf(abs(bi_[5] / sei_[5])),
                          'b_2022': 100 * (bi_[2] + bi_[5]), 'n': int(len(S)), 'n_2022': int(T22.sum())}

    rb = rolling_beta(D)
    ri = rolling_beta(D, 'ief', market=False)
    pre = rb.loc[:'2021-12-31']
    res['roll'] = {'mean_pre2022': pre['b'].mean(), 'min_pre2022': pre['b'].min(),
                   'share_sig_pre2022': float(((pre['b'] - 1.96 * pre['se']) > 0).mean()),
                   'at_svb': float(rb.loc[:SVB, 'b'].iloc[-1]), 'at_svb_lo': float((rb.loc[:SVB, 'b'] - 1.96 * rb.loc[:SVB, 'se']).iloc[-1]),
                   'at_svb_hi': float((rb.loc[:SVB, 'b'] + 1.96 * rb.loc[:SVB, 'se']).iloc[-1]),
                   'min_2022_23': float(rb.loc['2022':'2023', 'b'].min()),
                   'min_2022_23_date': str(rb.loc['2022':'2023', 'b'].idxmin().date()),
                   'last': float(rb['b'].iloc[-1]), 'last_date': str(rb.index[-1].date()),
                   'ief_mean': float(ri['b'].mean()),
                   'first_date': str(rb.index[0].date()),
                   'min_2013_15': float(rb.loc[:'2015-12-31', 'b'].min()), 'max_2013_15': float(rb.loc[:'2015-12-31', 'b'].max()),
                   'max_2021': float(rb.loc['2021', 'b'].max()), 'max_2021_date': str(rb.loc['2021', 'b'].idxmax().date()),
                   'end_2021': float(rb.loc[:'2021-12-31', 'b'].iloc[-1])}

    # ---------------------------------------------------------------- chart
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={'width_ratios': [1, 1.25]})
    ax = axes[0]
    V = D.loc[BASE:'2023-12-31']
    for k, col, lab in [('ief', Amber, 'IEF: Treasuries 7-10y, total return'), ('tlt', Purple, 'TLT: Treasuries 20y+, total return'),
                        ('bank', MainBlue, 'Six US banks, total return'), ('spx', Forest, 'S&P 500 price index')]:
        s = 100 * (1 + V[k].iloc[1:] / 100).cumprod()
        s = pd.concat([pd.Series([100.0], index=[V.index[0]]), s])
        ax.plot(s.index, s.values, color=col, lw=1.1, label=lab)
    for k, col, lab in [('ief_px', Amber, 'IEF price only'), ('tlt_px', Purple, 'TLT price only')]:
        s = 100 * (1 + V[k].iloc[1:] / 100).cumprod()
        s = pd.concat([pd.Series([100.0], index=[V.index[0]]), s])
        ax.plot(s.index, s.values, color=col, lw=0.8, ls='--', label=lab)
    ax.axvspan(pd.Timestamp(BASE), pd.Timestamp(MTM_END), color=BandBlue, alpha=0.45, lw=0,
               label='Q1 2022 to Q1 2023')
    ax.axhline(100, color=Navy, lw=0.5)
    ax.axvline(pd.Timestamp(SVB), color=Navy, lw=0.6, ls=':')
    ax.text(pd.Timestamp(SVB), ax.get_ylim()[1], 'SVB', rotation=90, fontsize=7, color='black', ha='right', va='top')
    ax.set_ylabel('Value of 100 on 31 Dec 2021')
    ax.set_title('Treasury ETFs and bank equity', fontsize=9.5)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    ax = axes[1]
    ax.fill_between(rb.index, rb['b'] - 1.96 * rb['se'], rb['b'] + 1.96 * rb['se'], color=BandBlue, lw=0,
                    label='Bank beta: 95% Newey-West interval')
    ax.plot(rb.index, rb['b'], color=MainBlue, lw=1.1, label='Bank beta, given the S&P 500')
    ax.plot(ri.index, ri['b'], color=Amber, lw=1.0, label='IEF beta')
    ax.axhline(0, color=Navy, lw=0.6)
    ax.axvline(pd.Timestamp('2022-03-16'), color=IDAred, lw=0.7, ls='--', label='First Fed hike')
    ax.axvline(pd.Timestamp(SVB), color=Navy, lw=0.6, ls=':')
    ax.text(pd.Timestamp(SVB), ax.get_ylim()[1], 'SVB', rotation=90, fontsize=7, color='black', ha='right', va='top')
    ax.set_ylabel('Return (%) per +100 bp\nin the US 10Y yield')
    ax.set_title(f'Rolling {WINDOW}-day rate beta', fontsize=9.5)
    ax.set_xlim(rb.index[0], rb.index[-1])
    fig.tight_layout()
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    os.makedirs(CHART_DIR, exist_ok=True)
    for ext, kw in [('pdf', {}), ('png', {'dpi': 180})]:
        plt.savefig(os.path.join(CHART_DIR, f'ch18_case_rate_risk.{ext}'), bbox_inches='tight', transparent=True, **kw)
    plt.close()

    def js(x):
        if isinstance(x, dict):
            return {k: js(v) for k, v in x.items()}
        if isinstance(x, (np.floating, np.integer)):
            return x.item()
        return x
    with open(OUT_JSON, 'w') as f:
        json.dump(js(res), f, indent=1)
    print(json.dumps(js(res), indent=1))
    return D


if __name__ == '__main__':
    main()

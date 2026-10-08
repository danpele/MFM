"""
big_data_case.py -- Capitolul 2, studiul de caz Martin & Nagel (2022, JFE): replicare pe 49 de portofolii sectoriale
====================================================================================================================
Specificatia din sectiunea 7 a lucrarii (Fig. 7 si 8), aplicata portofoliilor sectoriale din Kenneth French
Data Library (randamente lunare ponderate cu capitalizarea, din iulie 1926):
  * predictori: randamentele simple si la patrat din lunile t-2 ... t-120 (238 de predictori);
  * variabila dependenta si predictorii centrati transversal in fiecare luna, predictorii scalati la abaterea
    standard transversala 1; fiecare luna primeste aceeasi pondere in regresia panel (ponderea 1/N_t);
  * r_OOS,t+1 = (1/N) h_t' X_{t+1}' r_{t+1}, cu h_t din OLS pe fereastra mobila de 20 de ani care se incheie in t;
    r_IS = randamentul in selectie al aceleiasi ferestre; media mobila pe 10 ani a lui r_OOS cu benzi de doua erori
    standard din media patratelor randamentelor lunare ale portofoliului (Fig. 8);
  * regresie ridge pe tot esantionul (din ianuarie 1971), penalizarea aleasa prin validare incrucisata cu cate un an
    exclus (media R^2 din anii exclusi, maximizata pe o grila), coeficientii pe decalaje (Fig. 7).
Limita datelor: 49 de portofolii in loc de actiunile individuale din CRSP; filtrele de capitalizare si de pret nu
se aplica portofoliilor. Un portofoliu intra in luna t doar cu istoric complet t-120 ... t.
Iesire: ch2_big_data_numbers.json, ch2_mn_rolling.csv, ch2_mn_ridge.csv, graficele ch2_mn_rolling, ch2_mn_ridge.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import io
import json
import os
import sys
import urllib.request
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from generate_all_charts import plt, MainBlue, IDAred, Forest, Amber, Gray, save_fig   # noqa: E402  (stilul MFM)

FF49_URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/49_Industry_Portfolios_CSV.zip'
MN_LAGS = 120            # lags t-2 ... t-120
MN_WINDOW = 240          # estimation window: 20 years
MN_MA = 120              # moving average of r_OOS: 10 years
MN_RIDGE_START = '1971-01-01'


def french_industries49():
    """49 Industry Portfolios (Kenneth French Data Library): value-weighted average monthly returns,
    as fractions; missing values (-99.99, -999) become NaN."""
    raw = urllib.request.urlopen(urllib.request.Request(FF49_URL, headers={'User-Agent': 'Mozilla/5.0'}),
                                 timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    lines = z.read(z.namelist()[0]).decode('latin-1').splitlines()
    i0 = next(i for i, l in enumerate(lines) if 'Average Value Weighted Returns -- Monthly' in l) + 1
    i1 = next(i for i in range(i0 + 1, len(lines)) if not lines[i].strip())
    d = pd.read_csv(io.StringIO('\n'.join(lines[i0:i1])), index_col=0)
    d.columns = [c.strip() for c in d.columns]
    d.index = pd.to_datetime(d.index.astype(str).str.strip(), format='%Y%m') + pd.offsets.MonthEnd(0)
    d = d.apply(pd.to_numeric, errors='coerce')
    return d.where(d > -99) / 100


def mn_panel(R, lags=MN_LAGS):
    """For each month t: X_t (N_t x 238), the returns t-2..t-120 and their squares, demeaned and standardised
    across portfolios; y_t = r_t demeaned across portfolios. Returns the months, the X, the y and the portfolios used."""
    A = R.values
    months, XS, YS, NS = [], [], [], []
    for t in range(lags, len(A)):
        ok = ~np.isnan(A[t - lags:t + 1]).any(axis=0)            # complete history t-120 ... t
        if ok.sum() < 10:
            continue
        past = np.column_stack([A[t - k, ok] for k in range(2, lags + 1)])
        X = np.hstack([past, past ** 2])
        X = (X - X.mean(axis=0)) / X.std(axis=0)
        y = A[t, ok] - A[t, ok].mean()
        months.append(R.index[t])
        XS.append(X)
        YS.append(y)
        NS.append(int(ok.sum()))
    return pd.DatetimeIndex(months), XS, YS, np.array(NS)


def mn_moments(XS, YS):
    """Monthly weighted moments (weight 1/N_t): G_t = X'X/N, b_t = X'y/N, v_t = y'y/N."""
    G = np.array([X.T @ X / len(y) for X, y in zip(XS, YS)])
    b = np.array([X.T @ y / len(y) for X, y in zip(XS, YS)])
    v = np.array([y @ y / len(y) for y in YS])
    return G, b, v


def mn_rolling(months, XS, YS, G, b, v, window=MN_WINDOW, ma=MN_MA):
    """OLS on rolling 20-year windows: r_IS (in sample) and r_OOS,t+1 (Martin & Nagel, eq. 19; Fig. 8)."""
    rows = []
    for e in range(window - 1, len(months) - 1):
        Gs, bs = G[e - window + 1:e + 1].sum(axis=0), b[e - window + 1:e + 1].sum(axis=0)
        h = np.linalg.solve(Gs, bs)
        r_is = h @ bs / window                                   # mean of (1/N) h'X_s'y_s in the window
        X1, y1 = XS[e + 1], YS[e + 1]
        r2_is = r_is / v[e - window + 1:e + 1].mean()           # in-sample R^2 of the window
        rows.append((months[e + 1], r_is, r2_is, (X1 @ h) @ y1 / len(y1)))
    o = pd.DataFrame(rows, columns=['date', 'r_is', 'r2_is', 'r_oos']).set_index('date')
    o['oos_ma'] = o['r_oos'].rolling(ma).mean()
    o['oos_se'] = np.sqrt((o['r_oos'] ** 2).rolling(ma).mean() / ma)
    return o


def mn_ridge(months, G, b, v, start=MN_RIDGE_START, grid=np.logspace(0, 7, 57)):
    """Full-sample ridge from `start`; penalty: maximises the mean R^2 of the left-out years (leave-one-year-out)."""
    sel = months >= start
    yrs = months.year[sel]
    Gs, bs, vs = G[sel], b[sel], v[sel]
    U = np.unique(yrs)
    Gy = {u: Gs[yrs == u].sum(axis=0) for u in U}
    by = {u: bs[yrs == u].sum(axis=0) for u in U}
    vy = {u: vs[yrs == u].sum() for u in U}
    GT, bT, I = sum(Gy.values()), sum(by.values()), np.eye(G.shape[1])

    def cv_r2(lam):
        r2 = []
        for u in U:
            beta = np.linalg.solve(GT - Gy[u] + lam * I, bT - by[u])
            sse = vy[u] - 2 * beta @ by[u] + beta @ Gy[u] @ beta
            r2.append(1 - sse / vy[u])
        return float(np.mean(r2))

    cv = np.array([cv_r2(l) for l in grid])
    lam = float(grid[cv.argmax()])
    beta = np.linalg.solve(GT + lam * I, bT)
    L = G.shape[1] // 2
    coef = pd.DataFrame({'lag': np.arange(2, L + 2), 'b_ret': beta[:L], 'b_sq': beta[L:]})
    return coef, dict(lam=lam, cv_r2=float(cv.max()), cv_r2_ols=cv_r2(1e-8), start=str(months[sel][0].date()),
                      end=str(months[sel][-1].date()), years=len(U))


def fig_mn_rolling(o):
    """Martin & Nagel Fig. 8 on 49 portfolios: 10-year moving average of r_OOS with 2-standard-error bands, and r_IS."""
    x = o.dropna()
    s = 1e5
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.fill_between(x.index, s * (x['oos_ma'] - 2 * x['oos_se']), s * (x['oos_ma'] + 2 * x['oos_se']),
                    color=MainBlue, alpha=0.18, lw=0, label=r'$\pm 2$ standard errors')
    ax.plot(x.index, s * x['oos_ma'], color=MainBlue, lw=1.5,
            label=r'$r_{OOS}$: out-of-sample, 10-year moving average')
    ax.plot(x.index, s * x['r_is'], color=IDAred, lw=1.3, label=r'$r_{IS}$: in-sample, 20-year window')
    ax.axhline(0, color=Gray, lw=0.7)
    ax.set_ylabel(r'Return per month ($\times 10^{-5}$)')
    ax.set_title('49 US industry portfolios, 238 lagged-return predictors: in-sample vs out-of-sample',
                 fontsize=9, loc='left')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=7.5)
    plt.tight_layout()
    save_fig('ch2_mn_rolling')


def fig_mn_ridge(coef):
    """Martin & Nagel Fig. 7 on 49 portfolios: ridge coefficients on past returns and on their squares."""
    lag = coef['lag'].values
    m12 = lag % 12 == 0
    short = (lag <= 12) & ~m12
    col = np.where(m12, IDAred, np.where(short, Forest, MainBlue))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharex=True)
    axes[0].bar(lag, 1e5 * coef['b_ret'], color=col, width=0.8)
    axes[0].set_title('(a) Past returns', fontsize=9, loc='left')
    axes[1].bar(lag, 1e5 * coef['b_sq'], color=Amber, width=0.8)
    axes[1].set_title('(b) Past squared returns', fontsize=9, loc='left')
    for ax in axes:
        ax.axhline(0, color=Gray, lw=0.6)
        ax.set_xlabel('Lag (months)')
    axes[0].set_ylabel(r'Ridge coefficient ($\times 10^{-5}$)')
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=l) for c, l in
               [(Forest, 'Lags 2-11'), (IDAred, 'Multiples of 12'), (MainBlue, 'Other lags above 12'),
                (Amber, 'Squared returns')]]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=4, frameon=False)
    plt.tight_layout()
    save_fig('ch2_mn_ridge')


def mn_summary(o, coef, ridge, months, NS, R):
    """The numbers shown on the slides."""
    x = o.dropna()
    t = x['oos_ma'] / x['oos_se']
    above = t[t > 2]
    se_all = np.sqrt((o['r_oos'] ** 2).mean() / len(o))
    half = o.index[0] + pd.DateOffset(years=30)
    early, late = o.loc[:half - pd.DateOffset(days=1)], o.loc[half:]
    lag = coef['lag']
    m12, short = lag % 12 == 0, (lag <= 11)
    other = (lag > 12) & ~m12
    return dict(
        data_start=str(R.index[0].date()), data_end=str(R.index[-1].date()),
        panel_start=str(months[0].date()), n_min=int(NS.min()), n_max=int(NS.max()), n_last=int(NS[-1]),
        oos_start=str(o.index[0].date()), oos_end=str(o.index[-1].date()), n_oos=len(o),
        r_is_mean=float(o['r_is'].mean()), r_is_min=float(o['r_is'].min()), r_is_max=float(o['r_is'].max()),
        r2_is=float(o['r2_is'].mean()),
        r_oos_mean=float(o['r_oos'].mean()), r_oos_t=float(o['r_oos'].mean() / se_all),
        early_end=str(early.index[-1].date()), early_mean=float(early['r_oos'].mean()),
        early_t=float(early['r_oos'].mean() / np.sqrt((early['r_oos'] ** 2).mean() / len(early))),
        late_mean=float(late['r_oos'].mean()),
        late_t=float(late['r_oos'].mean() / np.sqrt((late['r_oos'] ** 2).mean() / len(late))),
        share_above_2se=float((t > 2).mean()), last_above_2se=str(above.index[-1].date()) if len(above) else '',
        ma_last=float(x['oos_ma'].iloc[-1]), ma_last_t=float(t.iloc[-1]), ma_first=str(x.index[0].date()),
        max_t_2014_2019=float(t.loc['2014':'2019'].max()),
        ridge=ridge,
        b_short_mean=float(coef.loc[short, 'b_ret'].mean()), b_short_pos=int((coef.loc[short, 'b_ret'] > 0).sum()),
        b_m12_mean=float(coef.loc[m12, 'b_ret'].mean()), b_m12_pos=int((coef.loc[m12, 'b_ret'] > 0).sum()),
        n_m12=int(m12.sum()),
        b_other_mean=float(coef.loc[other, 'b_ret'].mean()), b_other_neg=float((coef.loc[other, 'b_ret'] < 0).mean()),
        sq_above50_pos=float((coef.loc[lag > 50, 'b_sq'] > 0).mean()))


if __name__ == '__main__':
    R = french_industries49()
    months, XS, YS, NS = mn_panel(R)
    G, b, v = mn_moments(XS, YS)
    o = mn_rolling(months, XS, YS, G, b, v)
    coef, ridge = mn_ridge(months, G, b, v)
    fig_mn_rolling(o)
    fig_mn_ridge(coef)
    o.to_csv(os.path.join(HERE, 'ch2_mn_rolling.csv'), float_format='%.6g')
    coef.to_csv(os.path.join(HERE, 'ch2_mn_ridge.csv'), index=False, float_format='%.6g')
    N = mn_summary(o, coef, ridge, months, NS, R)
    with open(os.path.join(HERE, 'ch2_big_data_numbers.json'), 'w') as f:
        json.dump(N, f, indent=1)
    print(json.dumps(N, indent=1))

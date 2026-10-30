"""
anomaly_market.py -- al doilea studiu de caz din Capitolul 13
=============================================================
Dong, Li, Rapach & Zhou (2022), Anomalies and the Expected Market Return, Journal of Finance 77(1), 639-681.
Intrebarea lucrarii: prezic randamentele long-short ale anomaliilor transversale randamentul in exces al pietei
luna urmatoare? Replicarea logicii pe Kenneth French Data Library (prin french_factors din mfm_ml):

  * 15 anomalii long-short lunare: SMB, HML, RMW, CMA, Mom, ST_Rev, LT_Rev (factori) si diferentele
    decila 10 - decila 1 (VW) pentru accruals, net share issues, beta, varianta, varianta reziduala (low - high)
    si E/P, CF/P, D/P (high - low);
  * tinta: Mkt-RF in luna t+1; predictorii: randamentele anomaliilor in luna t;
  * esantionul lucrarii: antrenare 1970-1979, validare 1980-1984, out-of-sample 1985-01 - 2017-12;
    aici out-of-sample pina la ultima luna disponibila (extensie dupa 2017);
  * fereastra extinsa, reestimare lunara; reperul: media istorica a Mkt-RF;
  * metode: OLS cu toti predictorii, elastic net (ENet, AICc), combinatia simpla a celor 15 prognoze univariate
    (Comb) si C-ENet (media prognozelor univariate selectate de ENet intr-o regresie Granger-Ramanathan pe
    prognozele din 1980 pina in luna anterioara; fara selectie -> media istorica);
  * R^2_OOS Campbell-Thompson si testul Clark-West (unilateral): regresia diferentei ajustate pe constanta,
    erori Newey-West cu floor(4 (T/100)^(2/9)) laguri (regula fixata inainte de rezultate); sensibilitate 3/6/12 laguri.

Rulare: python3 anomaly_market.py  -> charts/ch13_dlrz_oos.pdf/.png si ch13_dlrz_results.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_ml import french_factors  # noqa: E402

START, FIRST_FC, OOS_START, PAPER_END = '1969-12', '1980-01-31', '1985-01-31', '2017-12-31'
# Tabelul 2 din lucrare (anomalii long-short, out-of-sample 1985-2017), R^2_OOS in %
DLRZ_R2 = {'OLS': -2513.86, 'ENet': 2.03, 'Comb': 0.89, 'C-ENet': 2.81}
LOW_MINUS_HIGH = ('AC', 'NI', 'BETA', 'VAR', 'RESVAR')
HIGH_MINUS_LOW = ('E-P', 'CF-P', 'D-P')
L1_RATIO = 0.5


def anomaly_panel():
    """Mkt-RF (tinta, luna t) si cele 15 anomalii long-short (luna t), lunar, in zecimal."""
    ff5 = french_factors('ff5')
    a = pd.DataFrame({'SMB': ff5['SMB'], 'HML': ff5['HML'], 'RMW': ff5['RMW'], 'CMA': ff5['CMA'],
                      'MOM': french_factors('mom').iloc[:, 0], 'STREV': french_factors('strev').iloc[:, 0],
                      'LTREV': french_factors('ltrev').iloc[:, 0]})
    for k in LOW_MINUS_HIGH:
        p = french_factors(k)
        a[k] = p['Lo 10'] - p['Hi 10']
    for k in HIGH_MINUS_LOW:
        p = french_factors(k)
        a[k.replace('-', '')] = p['Hi 10'] - p['Lo 10']
    return pd.concat([ff5['Mkt-RF'].rename('MKT'), a], axis=1).loc[START:].dropna()


def _aicc(n, rss, df):
    return n * np.log(rss / n) + 2 * (df + 1) + 2 * (df + 1) * (df + 2) / max(n - df - 2, 1)


def _enet_aicc(Z, y, positive=False, n_grid=40):
    """Elastic net (l1_ratio = 0.5) cu penalizarea aleasa prin AICc pe o grila logaritmica."""
    n = len(y)
    lam_max = np.max(np.abs((Z - Z.mean(0)).T @ (y - y.mean()))) / n / L1_RATIO
    best = None
    for lam in lam_max * np.logspace(0, -4, n_grid):
        m = ElasticNet(alpha=lam, l1_ratio=L1_RATIO, positive=positive, max_iter=20000).fit(Z, y)
        crit = _aicc(n, ((y - m.predict(Z)) ** 2).sum(), int((m.coef_ != 0).sum()))
        if best is None or crit < best[0]:
            best = (crit, m)
    return best[1]


def dlrz_forecasts(panel):
    """Prognoze recursive (fereastra extinsa) ale Mkt-RF: media istorica, 15 univariate, OLS, Comb, ENet, C-ENet."""
    y, X = panel['MKT'].values, panel.drop(columns='MKT').values
    dates, names = panel.index, list(panel.columns[1:])
    T, K = X.shape
    f0, oos = dates.get_loc(pd.Timestamp(FIRST_FC)), dates.get_loc(pd.Timestamp(OOS_START))
    hm, ols, enet, cenet = (np.full(T, np.nan) for _ in range(4))
    uni, nsel = np.full((T, K), np.nan), np.full(T, np.nan)
    for t in range(f0, T):                          # prognoza pentru luna t, cu date pina in t-1
        yy, xx = y[1:t], X[:t - 1]
        hm[t] = y[1:t].mean()
        for j in range(K):
            b, a = np.polyfit(xx[:, j], yy, 1)
            uni[t, j] = a + b * X[t - 1, j]
        Z = np.column_stack([np.ones(t - 1), xx])
        beta = np.linalg.lstsq(Z, yy, rcond=None)[0]
        ols[t] = beta[0] + X[t - 1] @ beta[1:]
        if t >= oos:
            sc = StandardScaler().fit(xx)
            enet[t] = _enet_aicc(sc.transform(xx), yy).predict(sc.transform(X[t - 1:t]))[0]
            sel = _enet_aicc(uni[f0:t], y[f0:t], positive=True).coef_ != 0
            nsel[t] = sel.sum()
            cenet[t] = uni[t, sel].mean() if sel.any() else hm[t]
    out = pd.DataFrame({'MKT': y, 'HM': hm, 'OLS': ols, 'ENet': enet, 'Comb': uni.mean(axis=1),
                        'C-ENet': cenet, 'nsel': nsel}, index=dates)
    return out.iloc[oos:], pd.DataFrame(uni, index=dates, columns=names).iloc[oos:]


def r2_oos(y, f, hm):
    """R^2_OOS Campbell-Thompson (2008), in %: 1 - SSE(model) / SSE(media istorica)."""
    return 100 * (1 - ((y - f) ** 2).sum() / ((y - hm) ** 2).sum())


def nw_lags(T):
    """Regula Newey-West (1994): floor(4 (T/100)^(2/9))."""
    return int(np.floor(4 * (T / 100) ** (2 / 9)))


def clark_west(y, f, hm, lags=None):
    """Clark-West (2007): diferenta ajustata de MSFE regresata pe constanta, t cu erori Newey-West (HAC, Bartlett),
    p unilateral. lags = None: regula nw_lags(T)."""
    import statsmodels.api as sm
    d = np.asarray((y - hm) ** 2 - ((y - f) ** 2 - (hm - f) ** 2), float)
    L = nw_lags(len(d)) if lags is None else lags
    t = sm.OLS(d, np.ones(len(d))).fit(cov_type='HAC', cov_kwds={'maxlags': L}).tvalues[0]
    return t, 1 - stats.norm.cdf(t)


def summary(fc):
    res = {}
    for per, sl in (('1985-2017', slice(None, PAPER_END)), ('2018-end', slice('2018-01-31', None)),
                    ('1985-end', slice(None, None))):
        s = fc.loc[sl]
        res[per] = {m: dict(r2=round(r2_oos(s.MKT, s[m], s.HM), 3),
                            cw_t=round(clark_west(s.MKT, s[m], s.HM)[0], 3),
                            cw_p=round(clark_west(s.MKT, s[m], s.HM)[1], 3))
                    for m in ('OLS', 'ENet', 'Comb', 'C-ENet')}
        res[per]['T'] = len(s)
        res[per]['cw_lags'] = nw_lags(len(s))
        res[per]['cw_p_sensitivity'] = {m: {str(L): round(clark_west(s.MKT, s[m], s.HM, L)[1], 4) for L in (0, 3, 6, 12)}
                                        for m in ('Comb', 'C-ENet')}
    res['cenet_selected_mean'] = round(float(fc.nsel.mean()), 3)
    res['cenet_none_share'] = round(float((fc.nsel == 0).mean()), 3)
    res['first'], res['last'] = f'{fc.index[0]:%Y-%m}', f'{fc.index[-1]:%Y-%m}'
    return res


def fig_dlrz_oos(fc, res, save=True):
    """Cistigul cumulat de erori patratice fata de media istorica (in %^2): Comb si C-ENet, 1985 - ultima luna."""
    import generate_all_charts as g
    plt = g.plt
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    e0 = (fc.MKT - fc.HM) ** 2
    full = res['1985-end']
    for m, col, lab in (('Comb', g.MainBlue, 'Comb: mean of 15 univariate forecasts'),
                        ('C-ENet', g.IDAred, 'C-ENet: mean of the forecasts selected by elastic net')):
        gain = 1e4 * (e0 - (fc.MKT - fc[m]) ** 2).cumsum()
        ax.plot(fc.index, gain, color=col, lw=1.0,
                label=f'{lab} (R²OOS {full[m]["r2"]:.2f}%, {res["first"][:4]}-{res["last"][:4]})')
    ax.axhline(0, color=g.Navy, lw=0.5)
    ax.axvline(pd.Timestamp(PAPER_END), color=g.Navy, lw=0.7, ls='--')
    lo, hi = ax.get_ylim()
    ax.text(pd.Timestamp('2017-06-30'), lo + 0.04 * (hi - lo), "end of the paper's sample ",
            ha='right', va='bottom', fontsize=8, color='black')
    ax.set_ylabel('Cumulative gain in squared\nerrors vs. historical mean (%²)')
    ax.set_title(f'Anomaly returns forecasting the market excess return: out-of-sample '
                 f'{fc.index[0]:%b %Y} - {fc.index[-1]:%b %Y}', fontsize=9, loc='left')
    g.legend_outside_bottom(ax, ncol=1, y=-0.13)
    plt.tight_layout()
    if save:
        g.save_fig('ch13_dlrz_oos')
    else:
        plt.close('all')


def main():
    panel = anomaly_panel()
    fc, uni = dlrz_forecasts(panel)
    res = summary(fc)
    res['univariate_r2_1985_end'] = {k: round(r2_oos(fc.MKT, uni[k], fc.HM), 3) for k in uni}
    res['paper_table2'] = DLRZ_R2
    with open(os.path.join(HERE, 'ch13_dlrz_results.json'), 'w') as f:
        json.dump(res, f, indent=1)
    fig_dlrz_oos(fc, res)
    print(json.dumps(res, indent=1))
    return fc, uni, res


if __name__ == '__main__':
    main()

"""
seminar19.py -- Cifrele si graficele Seminarului 19 (atelier de proiect, MFM)
=============================================================================
  B1-B2  fapte stilizate cu inferenta robusta: BET (rezolvat) si Bitcoin (propus)
  B3-B4  GARCH(1,1)-t si GJR-GARCH(1,1)-t pe BET, cu CI pentru timpul de injumatatire
  B5-B6  VaR 1% pentru ziua urmatoare si backtesting: BET (rezolvat) si Bitcoin (propus)
  B7     capcana informatiei din viitor (parametri din toata selectia)
  B8     capcana calendarului: corelatia Bitcoin-SPY cu join pe randamente vs join pe preturi
  C1     analiza de referinta: s-a schimbat riscul de coada al BET dupa reclasificarea FTSE (septembrie 2020)?
Cifrele sunt salvate in sem19_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import log_returns, asset_price  # noqa: E402
from case_study import (ALPHA, MODELS, stylised_facts, kurtosis_boot_ci, garch_t_fit, garch_summary,  # noqa: E402
                        rolling_var, backtest_table)
from generate_all_charts import (plt, MainBlue, IDAred, Orange, Teal, Gray, Forest, save_fig,  # noqa: E402
                                 legend_outside_bottom)

HERE = os.path.dirname(os.path.abspath(__file__))
FTSE = '2020-09-21'      # BVB inclusa in indicii FTSE Russell pentru piete emergente secundare
RES = {}

bet = 100 * log_returns('bet')
btc = 100 * log_returns('btc')


def half_life_ci(res):
    """Timpul de injumatatire ln(0.5)/ln(alpha+beta) cu CI 95% prin metoda delta (covarianta robusta)."""
    p = res.params
    cov = res.param_cov.loc[['alpha[1]', 'beta[1]'], ['alpha[1]', 'beta[1]']].values
    pers = p['alpha[1]'] + p['beta[1]']
    se_pers = np.sqrt(np.ones(2) @ cov @ np.ones(2))
    hl = np.log(0.5) / np.log(pers)
    d = -np.log(0.5) / (pers * np.log(pers) ** 2)
    se_hl = abs(d) * se_pers
    lo = pers - 1.96 * se_pers
    return dict(pers=pers, se_pers=se_pers, pers_lo=lo, pers_hi=pers + 1.96 * se_pers,
                hl=hl, se_hl=se_hl, hl_at_lo=np.log(0.5) / np.log(lo))


def part_facts():
    for k, r in [('bet', bet), ('btc', btc)]:
        sf = stylised_facts(r)
        sf['kurt_ci'] = list(kurtosis_boot_ci(r))
        RES[f'facts_{k}'] = sf


def part_garch():
    res = garch_t_fit(bet)
    g = garch_summary(res)
    g.update(half_life_ci(res))
    g['loglik'] = res.loglikelihood
    RES['garch_bet'] = g
    gjr = arch_model(bet, mean='Constant', vol='GARCH', p=1, o=1, q=1, dist='t', rescale=False).fit(disp='off')
    lr = 2 * (gjr.loglikelihood - res.loglikelihood)
    RES['gjr_bet'] = dict(alpha=gjr.params['alpha[1]'], gamma=gjr.params['gamma[1]'], beta=gjr.params['beta[1]'],
                          se_gamma=gjr.std_err['gamma[1]'], t_gamma=gjr.tvalues['gamma[1]'],
                          LR=lr, p=stats.chi2.sf(lr, 1), aic_garch=res.aic, aic_gjr=gjr.aic,
                          bic_garch=res.bic, bic_gjr=gjr.bic)


def part_var_btc():
    fc = rolling_var(btc, '2019-01-01')
    RES['bt_btc'] = backtest_table(fc)
    RES['eval_btc'] = dict(start=str(fc.index[0].date()), end=str(fc.index[-1].date()), T=len(fc))
    d = fc.loc['2022-01-01':]
    fig, ax = plt.subplots(figsize=(9.6, 3.3))
    ax.bar(d.index, d['L'].clip(lower=0), width=1.2, color=Teal, alpha=0.7, label='Daily loss (gains set to 0)')
    ax.plot(d.index, d['HS'], color=MainBlue, lw=0.9, label='HS VaR 1% (500 days)')
    ax.plot(d.index, d['FHS'], color=IDAred, lw=0.9, label='FHS VaR 1% (GARCH-t filter)')
    exc = d['L'] > d['FHS']
    ax.scatter(d.index[exc], d['L'][exc], s=12, color='black', zorder=3, label='Loss above FHS VaR 1%')
    ax.set_ylabel('Loss (% of position)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch19_sem_btc_var')


def part_join():
    """Corelatia Bitcoin-SPY: (gresit) randamente pe calendare proprii, apoi join; (corect) join pe preturi."""
    spy = asset_price('SPY')
    b = asset_price('BTC')
    r_spy = np.log(spy).diff().dropna()
    r_btc = np.log(b).diff().dropna()
    wrong = pd.concat([r_btc, r_spy], axis=1, join='inner').dropna()
    p = pd.concat([b, spy], axis=1, join='inner').dropna()
    right = np.log(p).diff().dropna()
    out = {}
    for lab, a, z in [('2015_2019', '2015-01-01', '2019-12-31'), ('2020_2026', '2020-01-01', '2026-09-18')]:
        w, rr = wrong.loc[a:z], right.loc[a:z]
        mon_w = w[w.index.dayofweek == 0]
        mon_r = rr[rr.index.dayofweek == 0]
        out[lab] = dict(wrong=w.corr().iloc[0, 1], right=rr.corr().iloc[0, 1],
                        wrong_mon=mon_w.corr().iloc[0, 1], right_mon=mon_r.corr().iloc[0, 1], n=len(rr),
                        sd_btc_wrong=100 * w.iloc[:, 0].std(), sd_btc_right=100 * rr.iloc[:, 0].std(),
                        sd_btc_mon_wrong=100 * mon_w.iloc[:, 0].std(), sd_btc_mon_right=100 * mon_r.iloc[:, 0].std(),
                        cum_btc_wrong=float(np.exp(w.iloc[:, 0].sum()) - 1), cum_btc_right=float(np.exp(rr.iloc[:, 0].sum()) - 1))
    RES['join'] = out
    rw = wrong.loc['2016-01-01':]
    rr = right.loc['2016-01-01':]
    cw = rw.iloc[:, 0].rolling(250).corr(rw.iloc[:, 1]).dropna()
    cr = rr.iloc[:, 0].rolling(250).corr(rr.iloc[:, 1]).dropna()
    fig, ax = plt.subplots(figsize=(9.6, 3.2))
    ax.plot(cr.index, cr.values, color=MainBlue, lw=1.0, label='Join on prices, then returns (correct)')
    ax.plot(cw.index, cw.values, color=Orange, lw=1.0, label='Returns on own calendars, then join (wrong)')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel('250-day correlation, Bitcoin vs SPY')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch19_sem_join')


def part_c():
    """Analiza de referinta pentru C1: BET inainte si dupa reclasificarea FTSE (21.09.2020)."""
    pre, post = bet.loc['2014-09-22':FTSE].iloc[:-1], bet.loc[FTSE:]
    out = {}
    for lab, r in [('pre', pre), ('post', post)]:
        res = garch_t_fit(r)
        g = garch_summary(res)
        ci = kurtosis_boot_ci(r, B=1000)
        out[lab] = dict(N=len(r), start=str(r.index[0].date()), end=str(r.index[-1].date()),
                        vol=r.std() * np.sqrt(252), kurt=stats.kurtosis(r), kurt_lo=ci[0], kurt_hi=ci[1],
                        pers=g['pers'], nu=g['nu'], hs_var=float(np.quantile(-r, 0.99)))
    # diferenta de kurtosis: bootstrap pe blocuri, independent in cele doua perioade
    rng = np.random.default_rng(3)

    def boot(x, B=1000, block=20):
        x = np.asarray(x)
        T = len(x)
        nb = int(np.ceil(T / block))
        return np.array([stats.kurtosis(x[(rng.integers(0, T - block, nb)[:, None] + np.arange(block)).ravel()[:T]])
                         for _ in range(B)])
    dk = boot(post) - boot(pre)
    out['dkurt'] = stats.kurtosis(post) - stats.kurtosis(pre)
    # sensibilitate: kurtosis-ul perioadei de dinainte fara cele mai mari una si doua zile (in valoare absoluta)
    top = pre.abs().nlargest(2).index
    out['pre']['top_days'] = [str(d.date()) for d in top]
    out['pre']['top_returns'] = [float(pre.loc[d]) for d in top]
    out['pre']['kurt_ex1'] = stats.kurtosis(pre.drop(top[:1]))
    out['pre']['kurt_ex2'] = stats.kurtosis(pre.drop(top))
    out['dkurt_ci'] = list(np.percentile(dk, [2.5, 97.5]))
    fc = rolling_var(bet, '2014-09-22')
    for lab, a, z in [('pre', '2014-09-22', '2020-09-18'), ('post', FTSE, '2026-09-18')]:
        d = fc.loc[a:z]
        out[lab]['fhs_rate'] = float((d['L'] > d['FHS']).mean())
        out[lab]['hs_rate'] = float((d['L'] > d['HS']).mean())
        out[lab]['T_fc'] = len(d)
    RES['c1'] = out


if __name__ == '__main__':
    part_facts()
    part_garch()
    part_var_btc()
    part_join()
    part_c()
    with open(os.path.join(HERE, 'sem19_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print('saved sem19_results.json')

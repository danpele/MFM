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
from mfm_data import log_returns, asset_price, load_close  # noqa: E402
from case_study import (ALPHA, MODELS, stylised_facts, kurtosis_boot_ci, garch_t_fit, garch_summary,  # noqa: E402
                        rolling_var, backtest_table, ljung_box)
from inference19 import hill, hill_k, hill_ci, holm, profile_ci, formal_eval, sup_wald_break, kupiec_region  # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Orange, Teal, Gray, Forest, Amber, Purple, save_fig,  # noqa: E402
                                 legend_outside_bottom, fig_legend_bottom, MODEL_COL)
from case_study import t_std_q  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FTSE = '2020-09-21'      # BVB inclusa in indicii FTSE Russell pentru piete emergente secundare
RES = {}
CH = {}          # intrari pentru graficele solutiilor (nu se salveaza in JSON)

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


def robust_q(x, m=10):
    """Portmanteau robust la heteroscedasticitate conditionata (Lobato, Nankervis & Savin, 2001):
    Q* = T sum_k rho_k^2 / tau_k, tau_k = mean(x_t^2 x_{t-k}^2) / gamma_0^2, ~ chi2(m) sub H0 (necorelare)."""
    x = np.asarray(x) - np.mean(x)
    T = len(x)
    g0 = np.mean(x ** 2)
    q = 0.0
    for k in range(1, m + 1):
        rho = np.mean(x[k:] * x[:-k]) / g0
        tau = np.mean((x[k:] * x[:-k]) ** 2) / g0 ** 2
        q += T * rho ** 2 / tau
    return q, stats.chi2.sf(q, m)


def part_facts():
    for k, r in [('bet', bet), ('btc', btc)]:
        sf = stylised_facts(r)
        h = hill_ci(r.values, seed=0)
        CH[f'hill_draws_{k}'] = h['draws']
        sf['hill'] = {kk: v for kk, v in h.items() if kk != 'draws'}
        sf['q_robust'], sf['q_robust_p'] = robust_q(r.values)
        sf['q_r_raw'], sf['q_r_raw_p'] = ljung_box(r.values)
        RES[f'facts_{k}'] = sf
    d = RES['facts_btc']['hill']['alpha'] - RES['facts_bet']['hill']['alpha']
    se = np.sqrt(RES['facts_btc']['hill']['se_boot'] ** 2 + RES['facts_bet']['hill']['se_boot'] ** 2)
    RES['hill_diff'] = dict(d=d, se=se, p=2 * stats.norm.sf(abs(d / se)))


def part_garch():
    res = garch_t_fit(bet)
    g = garch_summary(res)
    g.update(half_life_ci(res))
    g['loglik'] = res.loglikelihood
    g['profile'] = profile_ci(bet.values, res)
    RES['garch_bet'] = g
    gjr = arch_model(bet, mean='Constant', vol='GARCH', p=1, o=1, q=1, dist='t', rescale=False).fit(disp='off')
    lr = 2 * (gjr.loglikelihood - res.loglikelihood)
    CH['garch_res'], CH['gjr_res'] = res, gjr
    RES['gjr_bet'] = dict(alpha=gjr.params['alpha[1]'], gamma=gjr.params['gamma[1]'], beta=gjr.params['beta[1]'],
                          se_gamma=gjr.std_err['gamma[1]'], t_gamma=gjr.tvalues['gamma[1]'],
                          LR=lr, p=stats.chi2.sf(lr, 1), aic_garch=res.aic, aic_gjr=gjr.aic,
                          bic_garch=res.bic, bic_gjr=gjr.bic)


def part_var_btc():
    fc = rolling_var(btc, '2019-01-01')
    RES['bt_btc'] = backtest_table(fc)
    RES['formal_btc'] = formal_eval(fc)
    fc.to_csv(os.path.join(HERE, 'ch19_forecasts_btc.csv'))
    RES['eval_btc'] = dict(start=str(fc.index[0].date()), end=str(fc.index[-1].date()), T=len(fc))
    d = fc.loc['2022-01-01':]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(d.index, d['L'].clip(lower=0), width=1.2, color=Teal, alpha=0.7, label='Daily loss (gains set to 0)')
    ax.plot(d.index, d['HS'], color=MainBlue, lw=0.9, label='HS VaR 1% (500 days)')
    ax.plot(d.index, d['FHS'], color=IDAred, lw=0.9, label='FHS VaR 1% (GARCH-t filter)')
    exc = d['L'] > d['FHS']
    ax.scatter(d.index[exc], d['L'][exc], s=12, color='black', zorder=3, label='Loss above FHS VaR 1%')
    ax.set_ylabel('Loss = negative log return (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
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
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(cr.index, cr.values, color=MainBlue, lw=1.0, label='Join on prices, then returns (correct)')
    ax.plot(cw.index, cw.values, color=Orange, lw=1.0, label='Returns on own calendars, then join (wrong)')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel('250-day correlation, Bitcoin vs SPY')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch19_sem_join')


def joint_hill_boot(R, share=0.05, B=999, block=20, rng=None):
    """Hill pe pierderile fiecarei coloane din R (T x m, zile comune) si bootstrap pe blocuri mobile COMUN:
    aceleasi blocuri de zile pentru toate coloanele, deci dependenta dintre piete este pastrata."""
    R = np.asarray(R)
    T, m = R.shape
    ks = [hill_k(R[:, j], share) for j in range(m)]
    est = np.array([hill(-R[:, j], ks[j]) for j in range(m)])
    nb = int(np.ceil(T / block))
    draws = np.empty((B, m))
    for b in range(B):
        ix = (rng.integers(0, T - block + 1, nb)[:, None] + np.arange(block)).ravel()[:T]
        draws[b] = [hill(-R[ix, j], ks[j]) for j in range(m)]
    return est, draws, ks


def part_c():
    """Analiza de referinta pentru C1: BET inainte si dupa reclasificarea FTSE (21.09.2020), control WIG20."""
    rngs = iter(np.random.SeedSequence(2020).spawn(64))   # fluxuri aleatoare independente pentru fiecare extragere
    pre, post = bet.loc['2014-09-22':FTSE].iloc[:-1], bet.loc[FTSE:]
    out = {}
    hd = {}
    for lab, r in [('pre', pre), ('post', post)]:
        res = garch_t_fit(r)
        g = garch_summary(res)
        h = hill_ci(r.values, seed=next(rngs))
        hd[lab] = h['draws']
        out[lab] = dict(N=len(r), start=str(r.index[0].date()), end=str(r.index[-1].date()),
                        vol=r.std() * np.sqrt(252), kurt=stats.kurtosis(r), hill=h['alpha'], hill_lo=h['lo'],
                        hill_hi=h['hi'], k=h['k'], pers=g['pers'], nu=g['nu'], hs_var=float(np.quantile(-r, 0.99)))
    # diferenta indicilor Hill: extrageri independente (fluxuri aleatoare distincte) in cele doua perioade disjuncte
    dd = hd['post'] - hd['pre']
    CH['c1_dd'] = dd
    out['dhill'] = out['post']['hill'] - out['pre']['hill']
    out['dhill_ci'] = list(np.percentile(dd, [2.5, 97.5]))
    out['dhill_se'] = float(dd.std(ddof=1))
    # sensibilitatea kurtosis-ului (necontrolat cand alpha < 4) la cele mai mari zile
    top = pre.abs().nlargest(2).index
    out['pre']['top_days'] = [str(d.date()) for d in top]
    out['pre']['top_returns'] = [float(pre.loc[d]) for d in top]
    out['pre']['kurt_ex1'] = stats.kurtosis(pre.drop(top[:1]))
    out['pre']['kurt_ex2'] = stats.kurtosis(pre.drop(top))
    out['dkurt'] = stats.kurtosis(post) - stats.kurtosis(pre)
    # control: WIG20 (neafectat de reclasificarea BVB); diferenta-in-diferente pe indicele Hill:
    # join pe PRETURI in zilele comune BET-WIG20, apoi randamente; in fiecare perioada aceleasi blocuri pentru
    # ambele piete (pastreaza dependenta dintre ele), extrageri independente intre cele doua perioade
    P = pd.concat([load_close('bet', '2014-09-01', '2026-09-18'), asset_price('WIG20', '2026-09-18')],
                  axis=1, join='inner').dropna()
    J = (100 * np.log(P).diff().dropna()).loc['2014-09-22':'2026-09-18']
    Jpre, Jpost = J[J.index < FTSE], J[J.index >= FTSE]
    out['joint_N'] = dict(pre=len(Jpre), post=len(Jpost))

    def did_spec(share, block, B=999):
        e1, d1, k1 = joint_hill_boot(Jpre.values, share, B, block, np.random.default_rng(next(rngs)))
        e2, d2, k2 = joint_hill_boot(Jpost.values, share, B, block, np.random.default_rng(next(rngs)))
        est = (e2[0] - e1[0]) - (e2[1] - e1[1])
        dr = (d2[:, 0] - d1[:, 0]) - (d2[:, 1] - d1[:, 1])
        se = float(dr.std(ddof=1))
        return dict(draws=dr, share=share, block=block, bet_pre=e1[0], bet_post=e2[0], wig_pre=e1[1], wig_post=e2[1],
                    k_pre=k1, k_post=k2, did=est, se=se, lo=float(np.percentile(dr, 2.5)),
                    hi=float(np.percentile(dr, 97.5)), p=float(2 * stats.norm.sf(abs(est) / se)),
                    cov_pre=float(np.cov(d1.T)[0, 1]), cov_post=float(np.cov(d2.T)[0, 1]))
    base = did_spec(0.05, 20)
    out['wig'] = dict(pre=base['wig_pre'], post=base['wig_post'], d=base['wig_post'] - base['wig_pre'],
                      bet_pre=base['bet_pre'], bet_post=base['bet_post'], bet_d=base['bet_post'] - base['bet_pre'],
                      cov_pre=base['cov_pre'], cov_post=base['cov_post'])
    out['did'] = base['did']
    CH['c1_did_draws'] = base['draws']
    out['did_ci'] = [base['lo'], base['hi']]
    out['did_se'] = base['se']
    out['did_mde'] = (stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) * base['se']   # efectul minim detectabil, putere 80%
    # grila de specificatii: k = 2.5%, 5%, 10% din zilele cu pierdere x blocuri de 10, 20, 40 de zile; corectia Holm
    grid = [base if (sh, bl) == (0.05, 20) else did_spec(sh, bl) for sh in (0.025, 0.05, 0.10) for bl in (10, 20, 40)]
    pg = np.array([g['p'] for g in grid])
    out['grid'] = dict(specs=[{k: g[k] for k in ('share', 'block', 'did', 'se', 'p')} for g in grid],
                       n=len(grid), rej_raw=int((pg < 0.05).sum()), rej_holm=int((holm(pg) < 0.05).sum()),
                       did_min=float(min(g['did'] for g in grid)), did_max=float(max(g['did'] for g in grid)),
                       p_min=float(pg.min()))
    # ruptura cu data necunoscuta in log|r| (toate momentele finite), 2014-2026
    y = np.log(np.abs(bet.loc['2014-09-22':'2026-09-18']))
    sw = sup_wald_break(y.values)
    out['supwald'] = dict(stat=sw['stat'], p=sw['p'], cv5=sw['cv5'], date=str(y.index[sw['k']].date()))
    # date placebo: aceeasi analiza Hill la +/- un an
    out['placebo'] = {}
    for lab, d0 in [('m1', '2019-09-23'), ('p1', '2021-09-20')]:
        a1, a2 = bet.loc['2014-09-22':d0].iloc[:-1], bet.loc[d0:'2026-09-18']
        h1, h2 = hill_ci(a1.values, seed=next(rngs)), hill_ci(a2.values, seed=next(rngs))
        dpl = h2['draws'] - h1['draws']
        out['placebo'][lab] = dict(date=d0, d=h2['alpha'] - h1['alpha'], lo=float(np.percentile(dpl, 2.5)),
                                   hi=float(np.percentile(dpl, 97.5)))
    fc = rolling_var(bet, '2014-09-22')
    for lab, a, z in [('pre', '2014-09-22', '2020-09-18'), ('post', FTSE, '2026-09-18')]:
        d = fc.loc[a:z]
        out[lab]['fhs_rate'] = float((d['L'] > d['FHS']).mean())
        out[lab]['hs_rate'] = float((d['L'] > d['HS']).mean())
        out[lab]['T_fc'] = len(d)
    RES['c1'] = out


# =============================================================================
# GRAFICE PENTRU SOLUTIILE SEMINARULUI (A3, A7, A9, A11, B1-B5, B7, C1)
# =============================================================================
QL_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/Quantlets/Ch_19/'


def ql_file(name):
    """Fisier produs de generate_all_charts.py (studiul de caz): copia locala sau cea din repository."""
    local = os.path.join(HERE, name)
    return local if os.path.exists(local) else QL_RAW + name


def case_results():
    src = ql_file('ch19_results.json')
    if src.startswith('http'):
        import urllib.request
        with urllib.request.urlopen(src) as f:
            return json.load(f)
    with open(src) as f:
        return json.load(f)


def chart_a3():
    """A3: prognoza variantei GARCH(1,1) pentru BET, cu parametrii rotunjiti afisati in enunt."""
    G = case_results()['garch']
    om, al, be = round(G['omega'], 4), round(G['alpha'], 4), round(G['beta'], 4)
    p = al + be
    s2bar = om / (1 - p)
    s2_1 = round(G['sigma_next'] ** 2, 2)
    h = np.arange(1, 121)
    s2h = s2bar + p ** (h - 1) * (s2_1 - s2bar)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.3))
    ax = axes[0]
    ax.plot(h, s2h, color=MainBlue, lw=1.3, label=r'Forecast $\sigma^2_{T+h}$')
    ax.axhline(s2bar, color=IDAred, lw=1.0, ls='--', label=r'Long-run variance $\bar\sigma^2$')
    ax.scatter([10], [s2h[9]], color='black', s=18, zorder=3, label='Day 10')
    ax.set_xlabel('Horizon h (trading days)')
    ax.set_ylabel(r'Daily variance (%$^2$)')
    hh = np.arange(1, 61)
    ax = axes[1]
    ax.plot(hh, np.sqrt(np.cumsum(s2h[:60])), color=Forest, lw=1.3, label='h-day volatility from the GARCH path')
    ax.plot(hh, np.sqrt(hh) * np.sqrt(s2_1), color=Orange, lw=1.3, ls='--', label=r'Square-root-of-time rule $\sqrt{h}\,\sigma_{T+1}$')
    ax.set_xlabel('Horizon h (trading days)')
    ax.set_ylabel('h-day volatility (%)')
    fig.tight_layout()
    fig_legend_bottom(fig, axes, ncol=2)
    save_fig('ch19_sem_a3_forecast')


def chart_a7():
    """A7: distributia binomiala a numarului de depasiri la T = 250 si regiunea de respingere Kupiec."""
    T = 250
    rej = set(kupiec_region(T).tolist())
    x = np.arange(0, 16)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    for xi in x:
        if xi in rej:
            ax.axvspan(xi - 0.5, xi + 0.5, color=IDAred, alpha=0.10, lw=0)
    ax.bar(x - 0.2, stats.binom.pmf(x, T, 0.01), 0.4, color=MainBlue, label='True rate 1% (size)')
    ax.bar(x + 0.2, stats.binom.pmf(x, T, 0.02), 0.4, color=Orange, label='True rate 2% (power)')
    ax.axvspan(0, 0, color=IDAred, alpha=0.10, lw=0, label='Rejection region of the 5% Kupiec test')
    ax.set_xlim(-0.6, 15.6)
    ax.set_xticks(x)
    ax.set_xlabel('Number of breaches x in T = 250 days')
    ax.set_ylabel('Probability')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch19_sem_a7_power')


def chart_a9():
    """A9: valorile p ordonate fata de pragurile Holm si Benjamini-Hochberg."""
    P = np.array([0.001, 0.004, 0.012, 0.019, 0.028, 0.041, 0.09, 0.20, 0.46, 0.73])
    m = len(P)
    i = np.arange(1, m + 1)
    holm_thr = 0.05 / (m - i + 1)
    bh_thr = 0.05 * i / m
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(i, holm_thr, color=Forest, lw=1.2, marker='_', ms=10, label='Holm threshold 0.05/(m - i + 1)')
    ax.plot(i, bh_thr, color=Orange, lw=1.2, ls='--', label='BH threshold 0.05 i/m')
    ax.axhline(0.05, color=Gray, lw=0.7, ls=':')
    ax.text(10.4, 0.05, 'unadjusted 0.05', va='center', fontsize=7, color='black')
    ax.scatter(i, P, color=MainBlue, s=22, zorder=3, label='Sorted p-values')
    ax.set_yscale('log')
    ax.set_xticks(i)
    ax.set_xlim(0.5, 11.8)
    ax.set_xlabel('Rank i of the p-value')
    ax.set_ylabel('p-value (log scale)')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch19_sem_a9_pvalues')


def chart_a11():
    """A11: kurtosis-ul de selectie pentru Student-t cu 3 grade de libertate (aceeasi simulare ca in enunt)."""
    rng = np.random.default_rng(11)
    Ts = (1000, 10000, 100000)
    sims = {T: np.array([stats.kurtosis(rng.standard_t(3, T)) for _ in range(200)]) for T in Ts}
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    jit = np.random.default_rng(0)
    for j, T in enumerate(Ts):
        k = sims[T]
        ax.scatter(np.full(k.size, j) + jit.uniform(-0.18, 0.18, k.size), k, s=6, color=MainBlue, alpha=0.5,
                   label='Sample excess kurtosis (200 samples per T)' if j == 0 else None)
        ax.plot([j - 0.3, j + 0.3], [np.median(k)] * 2, color=IDAred, lw=2, label='Median' if j == 0 else None)
        ax.plot([j - 0.3, j + 0.3], [np.percentile(k, 90)] * 2, color=Orange, lw=2, ls='--',
                label='90% quantile' if j == 0 else None)
    ax.set_yscale('log')
    ax.set_xticks(range(len(Ts)))
    ax.set_xticklabels([f'T = {T:,}' for T in Ts])
    ax.set_ylabel('Excess kurtosis (log scale)')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    save_fig('ch19_sem_a11_kurtosis')


def hill_path(r, kmax):
    L = -np.asarray(r)
    ks = np.arange(10, kmax + 1, 2)
    return ks, np.array([hill(L, k) for k in ks])


def chart_b1():
    """B1: graficul Hill pentru BET si distributia bootstrap pe blocuri a estimatorului."""
    H = RES['facts_bet']['hill']
    ks, a = hill_path(bet.values, 800)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.3))
    ax = axes[0]
    ax.fill_between(ks, a * (1 - 1.96 / np.sqrt(ks)), a * (1 + 1.96 / np.sqrt(ks)), color=Gray, alpha=0.25, lw=0,
                    label='Asymptotic 95% band')
    ax.plot(ks, a, color=MainBlue, lw=1.2, label=r'Hill estimate $\hat\alpha(k)$')
    ax.axvline(H['k'], color=IDAred, lw=1.0, ls='--', label=f"Chosen k = {H['k']} (5% of loss days)")
    ax.axhline(4, color='black', lw=0.7, ls=':', label=r'$\alpha = 4$: finite fourth moment above')
    ax.set_xlabel('Number of largest losses k')
    ax.set_ylabel('Tail index')
    ax = axes[1]
    ax.hist(CH['hill_draws_bet'], bins=40, color=Teal, alpha=0.8, label='Block-bootstrap estimates (999)')
    ax.axvline(H['alpha'], color=MainBlue, lw=1.4, label='Estimate')
    for v in (H['lo_iid'], H['hi_iid']):
        ax.axvline(v, color=Orange, lw=1.1, ls='--', label='Asymptotic 95% CI' if v == H['lo_iid'] else None)
    for v in (H['lo'], H['hi']):
        ax.axvline(v, color=IDAred, lw=1.1, ls='-.', label='Block-bootstrap 95% CI' if v == H['lo'] else None)
    ax.set_xlabel('Tail index of BET losses')
    ax.set_ylabel('Frequency')
    fig.tight_layout()
    fig_legend_bottom(fig, axes, ncol=2)
    save_fig('ch19_sem_b1_hill')


def chart_b2():
    """B2: grafice Hill pentru BET si Bitcoin, k ca pondere din zilele cu pierdere."""
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.3))
    ax = axes[0]
    for key, lab, c in [('bet', 'BET', MainBlue), ('btc', 'Bitcoin', Orange)]:
        r = bet if key == 'bet' else btc
        nloss = int(np.sum(-r.values > 0))
        ks, a = hill_path(r.values, int(0.2 * nloss))
        ax.plot(100 * ks / nloss, a, color=c, lw=1.2, label=f'{lab}: Hill estimate')
    ax.axvline(5, color=IDAred, lw=1.0, ls='--', label='Chosen k: 5% of loss days')
    ax.axhline(4, color='black', lw=0.7, ls=':', label=r'$\alpha = 4$')
    ax.set_xlabel('k as % of loss days')
    ax.set_ylabel('Tail index')
    ax = axes[1]
    for key, lab, c in [('bet', 'BET', MainBlue), ('btc', 'Bitcoin', Orange)]:
        ax.hist(CH[f'hill_draws_{key}'], bins=40, color=c, alpha=0.55, label=f'{lab}: block-bootstrap estimates')
    ax.set_xlabel('Tail index of losses')
    ax.set_ylabel('Frequency')
    fig.tight_layout()
    fig_legend_bottom(fig, axes, ncol=2)
    save_fig('ch19_sem_b2_hill')


def chart_b3():
    """B3: statistica profil pentru persistenta, intervalul Wald si intervalul profil."""
    G = RES['garch_bet']
    P = G['profile']
    g, lr = np.array(P['grid']), np.array(P['lr'])
    o = np.argsort(g)
    g, lr = g[o], lr[o]
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    ax.axvspan(P['lo'], 1.0, color=Forest, alpha=0.12, lw=0, label=f"Profile 95% CI [{P['lo']:.3f}, 1]")
    ax.plot(g, lr, color=MainBlue, lw=1.3, marker='o', ms=2.5, label=r'Profile statistic $2(\ell_{\max} - \ell(p))$')
    ax.axhline(3.84, color=Gray, lw=0.8, ls='--')
    ax.axhline(2.71, color=Gray, lw=0.8, ls=':')
    ax.text(0.9602, 3.84 + 0.25, '3.84: interior critical value', fontsize=7, color='black')
    ax.text(0.9602, 2.71 - 0.75, '2.71: boundary critical value at p = 1', fontsize=7, color='black')
    ax.axvline(1.0, color='black', lw=0.8)
    ax.plot([G['pers_lo'], G['pers_hi']], [-0.6, -0.6], color=IDAred, lw=3, solid_capstyle='butt',
            label=f"Wald 95% CI [{G['pers_lo']:.3f}, {G['pers_hi']:.3f}]")
    ax.scatter([G['pers']], [0], color='black', s=20, zorder=4, label=f"Estimate {G['pers']:.4f}")
    ax.set_xlim(0.959, max(1.003, G['pers_hi'] + 0.002))
    ax.set_ylim(-1.2, min(15, lr.max() + 1))
    ax.set_xlabel(r'Persistence $p = \alpha + \beta$')
    ax.set_ylabel('Likelihood-ratio statistic')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch19_sem_b3_profile')


def chart_b4():
    """B4: curbele de impact al stirilor pentru GARCH(1,1)-t si GJR-GARCH(1,1)-t (BET)."""
    g, j = CH['garch_res'].params, CH['gjr_res'].params
    s2g = g['omega'] / (1 - g['alpha[1]'] - g['beta[1]'])
    s2j = j['omega'] / (1 - j['alpha[1]'] - 0.5 * j['gamma[1]'] - j['beta[1]'])
    e = np.linspace(-6, 6, 241)
    nic_g = g['omega'] + g['alpha[1]'] * e ** 2 + g['beta[1]'] * s2g
    nic_j = j['omega'] + (j['alpha[1]'] + j['gamma[1]'] * (e < 0)) * e ** 2 + j['beta[1]'] * s2j
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(e, nic_g, color=MainBlue, lw=1.3, label='GARCH(1,1)-t')
    ax.plot(e, nic_j, color=IDAred, lw=1.3, ls='--', label='GJR-GARCH(1,1)-t')
    ax.axvline(0, color=Gray, lw=0.5)
    ax.set_xlabel(r'Shock $\varepsilon_{t-1}$ (daily return in %, around the mean)')
    ax.set_ylabel(r'Next-day variance $\sigma_t^2$ (%$^2$)')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch19_sem_b4_nic')


def load_bet_forecasts():
    return pd.read_csv(ql_file('ch19_forecasts_bet.csv'), index_col='date', parse_dates=True)


def chart_b5():
    """B5: depasiri cumulate minus depasirile asteptate (0,01 t), patru modele, BET 2005-2026."""
    fc = load_bet_forecasts()
    t = np.arange(1, len(fc) + 1)
    band = 1.96 * np.sqrt(ALPHA * (1 - ALPHA) * t)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.fill_between(fc.index, -band, band, color=Gray, alpha=0.22, lw=0, label='95% band if the rate is 1%')
    for m in MODELS:
        ax.plot(fc.index, np.cumsum((fc['L'] > fc[m]).values) - ALPHA * t, color=MODEL_COL[m], lw=1.1, label=m)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlim(fc.index[0], fc.index[-1])
    ax.set_ylabel('Cumulative breaches minus 0.01 t')
    legend_outside_bottom(ax, ncol=3, y=-0.1)
    save_fig('ch19_sem_b5_breaches')


def chart_b7():
    """B7: depasiri cumulate, estimare pe fereastra mobila vs parametri din tot esantionul (informatie din viitor)."""
    fc = load_bet_forecasts()
    res = CH['garch_res']
    p = res.params
    sig_full = res.conditional_volatility.loc[fc.index]
    var_full = -(p['mu'] + sig_full * t_std_q(p['nu'], ALPHA))
    hs_full = np.quantile(fc['L'], 1 - ALPHA)
    LA = case_results()['lookahead']
    assert int((fc['L'] > var_full).sum()) == LA['garch_full_x'] and int((fc['L'] > hs_full).sum()) == LA['hs_full_x']
    t = np.arange(1, len(fc) + 1)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(fc.index, ALPHA * t, color='black', lw=0.9, ls='--', label='Expected: 0.01 t')
    ax.plot(fc.index, np.cumsum((fc['L'] > fc['HS']).values), color=MainBlue, lw=1.1, label='HS, rolling 500 days')
    ax.plot(fc.index, np.cumsum((fc['L'] > hs_full).values), color=Teal, lw=1.1, ls=':', label='HS, full-sample quantile (look-ahead)')
    ax.plot(fc.index, np.cumsum((fc['L'] > fc['GARCH-t']).values), color=Forest, lw=1.1, label='GARCH-t, rolling 1000 days')
    ax.plot(fc.index, np.cumsum((fc['L'] > var_full).values), color=Amber, lw=1.1, ls=':', label='GARCH-t, full-sample parameters (look-ahead)')
    ax.set_xlim(fc.index[0], fc.index[-1])
    ax.set_ylabel('Cumulative breaches of VaR 1%')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    save_fig('ch19_sem_b7_lookahead')


def chart_c1():
    """C1: distributiile bootstrap ale schimbarii indicelui Hill BET si ale diferentei in diferente (BET - WIG20)."""
    c = RES['c1']
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.3))
    ax = axes[0]
    ax.hist(CH['c1_dd'], bins=40, color=Teal, alpha=0.8, label='Block-bootstrap draws')
    ax.axvline(0, color='black', lw=0.8, ls=':', label='No change')
    ax.axvline(c['dhill'], color=MainBlue, lw=1.5, label='Estimate at the reclassification date')
    for lab, col in [('m1', Orange), ('p1', Purple)]:
        q = c['placebo'][lab]
        ax.axvline(q['d'], color=col, lw=1.2, ls='--', label=f"Placebo date {q['date']}")
    ax.set_xlabel('BET Hill index after minus before')
    ax.set_ylabel('Frequency')
    ax = axes[1]
    ax.hist(CH['c1_did_draws'], bins=40, color=Teal, alpha=0.8)
    ax.axvline(0, color='black', lw=0.8, ls=':')
    ax.axvline(c['did'], color=MainBlue, lw=1.5)
    ax.set_xlabel('Difference-in-differences, BET minus WIG20')
    ax.set_ylabel('Frequency')
    fig.tight_layout()
    fig_legend_bottom(fig, axes, ncol=2)
    save_fig('ch19_sem_c1_did')


def part_charts():
    chart_a3()
    chart_a7()
    chart_a9()
    chart_a11()
    chart_b1()
    chart_b2()
    chart_b3()
    chart_b4()
    chart_b5()
    chart_b7()
    chart_c1()


if __name__ == '__main__':
    part_facts()
    part_garch()
    part_var_btc()
    part_join()
    part_c()
    part_charts()
    with open(os.path.join(HERE, 'sem19_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print('saved sem19_results.json')

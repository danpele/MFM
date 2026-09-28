"""
seminar16.py -- Calculele Seminarului 16 (MFM): active digitale si DeFi
======================================================================
Partea A: indice ponderat cu valoarea de piata si divizorul (A1, A2), schimb intr-un fond x*y = k (A3, A4),
pierderea impermanenta si comisioanele (A5, A6), arbitrajul de rascumparare al unui stablecoin (A7) si
al unui ETF (A8).
Partea B: Bitcoin vs S&P 500 si efectul de weekend cu bootstrap pe blocuri (B1, B2), dinamica abaterilor de la
paritate (B3, B4), urmarirea IBIT / ETHA (B5, B6), beta Strategy / Coinbase (B7, B8).
Partea C: este Bitcoin un activ alternativ, un activ de risc sau o acoperire? (C1)
Cifrele sunt salvate in sem16_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import lfilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import price, log_returns, joint_returns, read_market, ASSETS, END   # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray, COL,  # noqa: E402,F811
                                 save_fig, legend_outside_bottom, fig_legend_bottom, jsonable, hac_ols,
                                 amm_swap, impermanent_loss, etf_tracking, ETF_START, SEED, B_BOOT)

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCK = 20          # lungimea blocului pentru bootstrap (zile)


# =============================================================================
# PARTEA A
# =============================================================================
def a1_index():
    """Indice Laspeyres cu trei monede: nivel, divizor, reponderare la sfarsitul lunii."""
    p0 = np.array([60000.0, 3000.0, 150.0])          # preturi la data de baza
    q0 = np.array([19.5e6, 120e6, 500e6])            # oferta in circulatie la data de baza
    mv0 = p0 * q0
    D0 = mv0.sum() / 1000                            # divizor: indicele porneste de la 1000
    p1 = np.array([66000.0, 2700.0, 180.0])          # preturi la sfarsitul lunii
    I1 = (p1 * q0).sum() / D0
    w0 = mv0 / mv0.sum()
    q1 = np.array([19.52e6, 120.1e6, 560e6])         # oferta noua la reponderare
    D1 = (p1 * q1).sum() / I1                        # divizor nou: acelasi nivel inainte si dupa
    return dict(mv0=mv0.tolist(), D0=D0, w0=w0.tolist(), I1=I1, ret=I1 / 1000 - 1, D1=D1,
                w1=((p1 * q1) / (p1 * q1).sum()).tolist(), rets=(p1 / p0 - 1).tolist())


def a2_replace():
    """Inlocuirea unui constituent: moneda C iese, moneda D intra; divizorul nou pastreaza nivelul."""
    p = np.array([66000.0, 2700.0, 180.0])
    q = np.array([19.52e6, 120.1e6, 560e6])
    I = 1000 * 1.0
    base = a1_index()
    I = base['I1']
    D = base['D1']
    pD, qD = 0.5, 40e9
    new_mv = p[0] * q[0] + p[1] * q[1] + pD * qD
    D_new = new_mv / I
    return dict(old_mv=(p * q).sum(), new_mv=new_mv, D_old=D, D_new=D_new, I=I, mvD=pD * qD, mvC=p[2] * q[2])


def a3_swap():
    """Vanzarea a 50 ETH intr-un fond cu 1000 ETH si 3 milioane USDC, comision 0.3%."""
    x, y, dx, fee = 1000.0, 3_000_000.0, 50.0, 0.003
    dy, pe = amm_swap(x, y, dx, fee)
    dy0, pe0 = amm_swap(x, y, dx, 0.0)
    p_new = (y - dy) / (x + dx)
    return dict(k=x * y, dy=dy, pe=pe, shortfall=100 * (1 - pe / (y / x)), dy_nofee=dy0,
                fee_cost=dy0 - dy, p_new=p_new, move=100 * (p_new / (y / x) - 1), g_dx=(1 - fee) * dx)


def a4_arbitrage():
    """Pretul extern creste la 3300 USDC: cati USDC trebuie adaugati (fara comision) si profitul arbitrajului."""
    x, y, P = 1000.0, 3_000_000.0, 3300.0
    k = x * y
    x1, y1 = np.sqrt(k / P), np.sqrt(k * P)
    dUSDC, dETH = y1 - y, x - x1
    profit = dETH * P - dUSDC
    lp_before, lp_after = x * P + y, x1 * P + y1
    return dict(x1=x1, y1=y1, dUSDC=dUSDC, dETH=dETH, profit=profit, avg=dUSDC / dETH, lp_hold=lp_before,
                lp_after=lp_after, loss=lp_before - lp_after)


def a5_il():
    """Pierderea impermanenta pentru r = 2, 0.5, 4; valoarea furnizorului vs pastrarea activelor."""
    out = {f'{r:g}': 100 * impermanent_loss(r) for r in [0.5, 1.5, 2, 4]}
    V0 = 20000.0
    r = 2.0
    hold = V0 / 2 * (1 + r)
    lp = V0 * np.sqrt(r)
    return dict(il=out, hold=hold, lp=lp, diff=lp - hold)


def a6_fees():
    """Comisioanele anuale care compenseaza pierderea impermanenta (r = 2 intr-un an) si LVR = sigma^2 / 8."""
    il2 = -impermanent_loss(2.0)
    sig = 0.70
    return dict(il2=100 * il2, fee_needed=100 * (1 / (1 - il2) - 1), lvr=100 * sig ** 2 / 8, sig=100 * sig,
                vol_tvl=100 * (sig ** 2 / 8) / 0.003 / 365)


def a7_stablecoin():
    """Arbitrajul de rascumparare: pret de piata 0.97, rascumparare la 1 USD cu comision 0.1% si cost fix."""
    m, fee, fixed, N = 0.97, 0.001, 25.0, 1_000_000
    buy = m * N
    redeem = N * (1 - fee)
    profit = redeem - buy - fixed
    lower = 1 - fee
    return dict(buy=buy, redeem=redeem, profit=profit, ret=100 * profit / buy, lower=lower,
                breakeven=(redeem - fixed) / N)


def a8_etf():
    """ETF spot pe Bitcoin: NAV pe unitate dupa comisionul anual 0.25% si prima / discountul."""
    btc0 = 0.000568                  # bitcoin detinut pe unitate la lansare (ipoteza de lucru)
    fee = 0.0025
    t = 2.5
    btc_t = btc0 * (1 - fee) ** t
    P_btc = 95000.0
    nav = btc_t * P_btc
    px = 53.10
    prem = 100 * (px / nav - 1)
    cost = 0.0010
    return dict(btc_t=btc_t, nav=nav, prem=prem, band=100 * cost, lost=100 * (1 - (1 - fee) ** t))


# =============================================================================
# PARTEA B
# =============================================================================
def block_boot(x, stat, B=B_BOOT, block=BLOCK, seed=SEED):
    """Bootstrap cu blocuri mobile (Kunsch, 1989) pentru o statistica a unui DataFrame/Series; 95% percentile."""
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    vals = []
    for _ in range(B):
        st = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in st])[:n]
        vals.append(stat(x.iloc[idx]))
    vals = np.array(vals)
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5), vals


def weekend_ratio(r):
    """Raportul dispersiilor: weekend (sambata, duminica) / zile lucratoare."""
    we = r[r.index.dayofweek >= 5]
    wd = r[r.index.dayofweek < 5]
    return (we ** 2).mean() / (wd ** 2).mean()


def b1_btc_facts(key='BTC'):
    """Volatilitatea anualizata fata de S&P 500 si efectul de weekend inainte / dupa ETF-uri, cu bootstrap pe blocuri."""
    r = 100 * log_returns(key, '2018-01-01')
    s = 100 * log_returns('SPX', str(r.index[0].date()))
    vc = r.std() * np.sqrt(365)
    vs = s.std() * np.sqrt(252)
    lo, hi, _ = block_boot(r, lambda x: x.std() * np.sqrt(365))
    pre, post = r.loc[:'2024-01-10'], r.loc[ETF_START:]
    rp, rq = weekend_ratio(pre), weekend_ratio(post)
    plo, phi_, dpre = block_boot(pre, weekend_ratio, block=21)
    qlo, qhi, dpost = block_boot(post, weekend_ratio, block=21, seed=SEED + 1)
    diff = dpost - dpre
    return dict(start=str(r.index[0].date()), n=len(r), vol=vc, vol_lo=lo, vol_hi=hi, vol_spx=vs, ratio=vc / vs,
                wr_pre=rp, wr_pre_lo=plo, wr_pre_hi=phi_, wr_post=rq, wr_post_lo=qlo, wr_post_hi=qhi,
                diff=rq - rp, diff_lo=np.percentile(diff, 2.5), diff_hi=np.percentile(diff, 97.5),
                n_pre=len(pre), n_post=len(post), kurt=float(pd.Series(r).kurt()), _dpre=dpre, _dpost=dpost)


def fig_sem_weekend(b1):
    """Distributiile bootstrap ale raportului weekend / zile lucratoare, inainte si dupa ETF-uri."""
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    ax.hist(b1['_dpre'], bins=50, color=MainBlue, alpha=0.75, density=True, label='2018 - 10 Jan 2024')
    ax.hist(b1['_dpost'], bins=50, color=Orange, alpha=0.75, density=True, label='11 Jan 2024 - Sep 2026')
    ax.axvline(1, color=Gray, lw=0.7, ls='--')
    ax.set_xlabel('Weekend variance / weekday variance (Bitcoin), block bootstrap draws')
    ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch16_sem_weekend')


def ar1_boot(dev, B=B_BOOT, seed=SEED):
    """AR(1) pe abateri: phi, timpul de injumatatire si interval bootstrap pe reziduuri."""
    x = dev.values
    X = np.column_stack([np.ones(len(x) - 1), x[:-1]])
    b = np.linalg.lstsq(X, x[1:], rcond=None)[0]
    e = x[1:] - X @ b
    rng = np.random.default_rng(seed)
    phis = []
    for _ in range(B):
        es = rng.choice(e, len(e), replace=True)
        # x_t = c + phi x_{t-1} + e_t, pornind de la x_0 observat (filtru recursiv)
        xs = np.concatenate([[x[0]], lfilter([1.0], [1.0, -b[1]], b[0] + es, zi=[b[1] * x[0]])[0]])
        Xs = np.column_stack([np.ones(len(xs) - 1), xs[:-1]])
        phis.append(np.linalg.lstsq(Xs, xs[1:], rcond=None)[0][1])
    lo, hi = np.percentile(phis, [2.5, 97.5])
    hl = lambda p: np.log(0.5) / np.log(p) if 0 < p < 1 else np.inf
    return dict(phi=b[1], mu=b[0] / (1 - b[1]), phi_lo=lo, phi_hi=hi, hl=hl(b[1]), hl_lo=hl(lo), hl_hi=hl(hi),
                sd_e=e.std(), n=len(x))


def b3_usdc(key='USDC', start='2021-01-01'):
    """Abaterea zilnica de la paritate (bp): AR(1) cu si fara martie 2023; zile in afara benzii de +-50 bp."""
    d = read_market(ASSETS[key][0]).loc[start:END]
    dev = 1e4 * (d['close'] - 1)
    full = ar1_boot(dev)
    ex = dev.drop(dev.loc['2023-03-09':'2023-03-16'].index)
    exl = ar1_boot(ex, seed=SEED + 1)
    return dict(key=key, n=len(dev), sd=dev.std(), sd_ex=ex.std(), out50=int((dev.abs() > 50).sum()),
                out50_ex=int((ex.abs() > 50).sum()), min=dev.min(), min_date=str(dev.idxmin().date()),
                low=1e4 * (d['low'].min() - 1), low_date=str(d['low'].idxmin().date()), full=full, ex=exl,
                kurt=float(dev.kurt()))


def fig_sem_usdc():
    """USDC: abaterea de la paritate in 2023 si graficul de dispersie x_t vs x_{t-1} (AR(1))."""
    d = read_market(ASSETS['USDC'][0]).loc['2021-01-01':END]
    dev = 1e4 * (d['close'] - 1)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    z = dev.loc['2023-01-01':'2023-06-30']
    axes[0].plot(z.index, z.values, color=MainBlue, lw=0.9, label='USDC close deviation (bp)')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].tick_params(axis='x', labelsize=7, rotation=30)
    axes[0].set_ylabel('bp')
    z1 = pd.concat([dev.shift(1), dev], axis=1).dropna()
    z1.columns = ['lag', 'now']
    zz = z1[(z1.abs() <= 30).all(axis=1)]
    axes[1].scatter(zz['lag'], zz['now'], s=5, color=Teal, alpha=0.6, label='Pairs of days (within 30 bp)')
    b = np.polyfit(z1['lag'], z1['now'], 1)
    xs = np.array([-30, 30])
    axes[1].plot(xs, np.polyval(b, xs), color=IDAred, lw=1.2, label=f'AR(1) fit on all days, slope {b[0]:.2f}')
    axes[1].set_xlim(-30, 30)
    axes[1].set_ylim(-30, 30)
    axes[1].set_xlabel('Deviation yesterday (bp)')
    axes[1].set_ylabel('Deviation today (bp)')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_sem_usdc')


def b5_etf(etf='IBIT', coin='BTC'):
    """Urmarirea: beta zilnic vs saptamanal (HAC), abaterea de urmarire si deriva anuala a raportului ETF / activ."""
    t = etf_tracking(etf, coin)
    p = pd.concat([price(etf), price(coin)], axis=1, join='inner').dropna()
    lr = np.log(p[etf] / p[coin])
    tt = pd.Series((lr.index - lr.index[0]).days / 365.25, index=lr.index)
    m = hac_ols(lr, tt, lags=20)
    t.update(drift_hac=100 * m.params.iloc[1], drift_se=100 * m.bse.iloc[1],
             drift_lo=100 * (m.params.iloc[1] - 1.96 * m.bse.iloc[1]), drift_hi=100 * (m.params.iloc[1] + 1.96 * m.bse.iloc[1]),
             t_beta_w=(t['beta_w'] - 1) / t['se_w'])
    return t


def b7_equity(key='MSTR'):
    """Regresie saptamanala cu doi factori, testul b_BTC = 1 si stabilitatea pe doua subperioade."""
    out = {}
    for lab, a, b in [('full', '2021-04-16', END), ('p1', '2021-04-16', '2023-12-31'), ('p2', ETF_START, END)]:
        w = joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc[a:b]
        m = hac_ols(w[key], w[['BTC', 'SPX']])
        out[lab] = dict(n=len(w), b_btc=m.params['BTC'], se_btc=m.bse['BTC'], b_spx=m.params['SPX'],
                        se_spx=m.bse['SPX'], r2=m.rsquared, t1=(m.params['BTC'] - 1) / m.bse['BTC'],
                        alpha=52 * 100 * m.params['const'], alpha_t=m.tvalues['const'])
    return out


# =============================================================================
# PARTEA C: este Bitcoin un activ alternativ, un activ de risc sau o acoperire?
# =============================================================================
def c1_hedge():
    """Corelatii inainte / dupa ETF-uri (bootstrap pe blocuri) si regresia Baur-Lucey pentru acoperire si refugiu."""
    out = {}
    per = {'pre': ('2021-01-01', '2024-01-10'), 'post': (ETF_START, END)}
    for k in ['SPX', 'QQQ', 'GLD', 'TLT']:
        r = joint_returns(['BTC', k], '2021-01-01')
        res = {}
        draws = {}
        for lab, (a, b) in per.items():
            x = r.loc[a:b]
            lo, hi, dr = block_boot(x, lambda z: z.iloc[:, 0].corr(z.iloc[:, 1]), block=20,
                                    seed=SEED + len(lab))
            res[lab] = x['BTC'].corr(x[k])
            res[lab + '_lo'], res[lab + '_hi'] = lo, hi
            draws[lab] = dr
        dd = draws['post'] - draws['pre']
        res['diff_lo'], res['diff_hi'] = np.percentile(dd, [2.5, 97.5])
        out[k] = res
    # Baur-Lucey: r_BTC = a + b r_SPX + sum_q c_q r_SPX 1{r_SPX <= q-cuantila}
    bl = {}
    for lab, (a, b) in per.items():
        r = 100 * joint_returns(['BTC', 'SPX'], a).loc[a:b]
        X = pd.DataFrame({'SPX': r['SPX']})
        for q in [0.10, 0.05, 0.01]:
            thr = r['SPX'].quantile(q)
            X[f'q{int(100 * q)}'] = r['SPX'] * (r['SPX'] <= thr)
        m = hac_ols(r['BTC'], X)
        b0 = m.params['SPX']
        bl[lab] = dict(n=len(r), b=b0, se=m.bse['SPX'], c10=m.params['q10'], c5=m.params['q5'], c1=m.params['q1'],
                       tot10=b0 + m.params['q10'], tot5=b0 + m.params['q10'] + m.params['q5'],
                       tot1=b0 + m.params['q10'] + m.params['q5'] + m.params['q1'],
                       se10=m.bse['q10'], se5=m.bse['q5'], se1=m.bse['q1'])
        # beta in zilele de scadere / crestere
        dn, up = r[r['SPX'] < 0], r[r['SPX'] > 0]
        bl[lab]['beta_dn'] = np.polyfit(dn['SPX'], dn['BTC'], 1)[0]
        bl[lab]['beta_up'] = np.polyfit(up['SPX'], up['BTC'], 1)[0]
        worst = r.nsmallest(10, 'SPX')
        bl[lab]['worst10_spx'] = worst['SPX'].mean()
        bl[lab]['worst10_btc'] = worst['BTC'].mean()
    out['bl'] = bl
    # volatilitatea si cea mai mare scadere in cele doua perioade
    p = price('BTC', '2021-01-01')
    for lab, (a, b) in per.items():
        x = p.loc[a:b]
        r = np.log(x).diff().dropna()
        out[lab + '_vol'] = 100 * r.std() * np.sqrt(365)
        out[lab + '_mdd'] = 100 * (x / x.cummax() - 1).min()
    return out


def fig_sem_hedge(c1):
    """Beta Bitcoin fata de S&P 500: normal, in cele mai rele 10%, 5%, 1% zile; inainte si dupa ETF-uri."""
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    labs = ['All days', 'Worst 10% of S&P 500 days', 'Worst 5%', 'Worst 1%']
    x = np.arange(4)
    for i, (lab, c) in enumerate([('pre', MainBlue), ('post', Orange)]):
        b = c1['bl'][lab]
        ax.bar(x + (i - 0.5) * 0.38, [b['b'], b['tot10'], b['tot5'], b['tot1']], 0.36, color=c,
               label='Jan 2021 - 10 Jan 2024' if lab == 'pre' else '11 Jan 2024 - Sep 2026')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylabel('Bitcoin beta to the S&P 500')
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch16_sem_hedge')


if __name__ == '__main__':
    print('Seminar 16')
    S = {}
    S['A1'], S['A2'], S['A3'], S['A4'] = a1_index(), a2_replace(), a3_swap(), a4_arbitrage()
    S['A5'], S['A6'], S['A7'], S['A8'] = a5_il(), a6_fees(), a7_stablecoin(), a8_etf()
    b1 = b1_btc_facts('BTC')
    fig_sem_weekend(b1)
    S['B1'] = {k: v for k, v in b1.items() if not k.startswith('_')}
    S['B2'] = {k: {kk: vv for kk, vv in b1_btc_facts(k).items() if not kk.startswith('_')} for k in ['ETH', 'SOL']}
    S['B3'] = b3_usdc('USDC')
    fig_sem_usdc()
    S['B4'] = {k: b3_usdc(k) for k in ['USDT', 'DAI']}
    S['B5'] = b5_etf('IBIT', 'BTC')
    S['B6'] = b5_etf('ETHA', 'ETH')
    S['B7'] = b7_equity('MSTR')
    S['B8'] = b7_equity('COIN')
    c1 = c1_hedge()
    fig_sem_hedge(c1)
    S['C1'] = c1
    with open(os.path.join(HERE, 'sem16_results.json'), 'w') as fh:
        json.dump(jsonable(S), fh, indent=1)
    print('saved sem16_results.json')

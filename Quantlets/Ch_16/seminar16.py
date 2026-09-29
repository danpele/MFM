"""
seminar16.py -- Calculele Seminarului 16 (MFM): active digitale si DeFi
======================================================================
Partea A: indice ponderat cu valoarea de piata si divizorul (A1, A2), banda de ne-arbitraj si arbitrajul optim
intr-un fond cu comision (A3) si intr-un fond ponderat (A4), pierderea impermanenta a unui fond ponderat (A5),
LVR prin Ito (A6), algebra AR cu prag si banda (A7, A8).
Partea B: Bitcoin vs S&P 500 si efectul de weekend cu bootstrap pe blocuri (B1, B2), paritatea ca AR cu prag
(EQ-TAR) cu testul sup-Wald si bootstrap cu regresori ficsi (B3, B4), deriva din comision cu HAC, ADF/KPSS si beta
Dimson pentru IBIT / ETHA (B5, B6), ruptura la data necunoscuta pentru beta Strategy / Coinbase (B7, B8).
Partea C: este Bitcoin un activ alternativ, un activ de risc sau o acoperire? (C1), cu corelatia Forbes-Rigobon
si regresia cuantila.
Cifrele sunt salvate in sem16_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import price, log_returns, joint_returns, read_market, ASSETS, END   # noqa: E402
import statsmodels.api as sm                                                        # noqa: E402
import inference16 as I                                                             # noqa: E402
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


def a3_band(x=1000.0, y=3_000_000.0, P=3300.0, fee=0.003):
    """Banda de ne-arbitraj a unui fond x*y = k cu comision f: gamma P <= p <= P / gamma; marimea optima a
    arbitrajului cand pretul extern P depaseste banda: rezerva efectiva y' = y + gamma dy* = sqrt(gamma P k),
    dy* = (y' - y) / gamma. Comisionul ramane in fond (convenția Uniswap v2): rezervele reale dupa tranzactie sunt
    x' si y + dy*, deci pretul fondului este (y + dy*) / x'. Profitul pe unitatea de valoare a fondului: raportat la
    valoarea fondului inainte de tranzactie, la pretul fondului (p x + y)."""
    g = 1 - fee
    k = x * y
    p = y / x
    y1 = np.sqrt(g * P * k)
    x1 = k / y1
    dy = (y1 - y) / g
    dx = x - x1
    profit = dx * P - dy
    V0 = p * x + y
    y_act = y + dy
    return dict(k=k, p=p, lo=g * P, hi=P / g, y1=y1, x1=x1, dy=dy, dx=dx, profit=profit, p_eff=y1 / x1,
                y_act=y_act, p_new=y_act / x1, band_lo=g * y_act / x1, band_hi=y_act / x1 / g,
                avg=dy / dx, profit_nofee=a4_nofee(x, y, P), V0=V0, rel=100 * profit / V0)


def a4_nofee(x, y, P):
    """Profitul arbitrajului fara comision (acelasi fond): P (x - x1) - (y1 - y), x1 = sqrt(k/P), y1 = sqrt(kP)."""
    k = x * y
    return P * (x - np.sqrt(k / P)) - (np.sqrt(k * P) - y)


def a4_weighted(w=0.8, x=1000.0, p=3000.0, P=3300.0, fee=0.003):
    """Fond ponderat x^w y^(1-w) = k (tip Balancer): pretul marginal p = (w/(1-w)) y/x; rezervele efective dupa
    arbitraj x' = k (w/(gamma P (1-w)))^(1-w), y' = k (gamma P (1-w)/w)^w; dy* = (y' - y)/gamma. Comisionul ramane in
    fond: rezerva reala y + dy*, pretul fondului (w/(1-w)) (y + dy*)/x'. Profitul pe unitatea de valoare: raportat la
    valoarea fondului inainte de tranzactie, p x + y = y / (1 - w)."""
    g = 1 - fee
    y = p * x * (1 - w) / w
    k = x ** w * y ** (1 - w)
    x1 = k * (w / (g * P * (1 - w))) ** (1 - w)
    y1 = k * (g * P * (1 - w) / w) ** w
    dy = (y1 - y) / g
    dx = x - x1
    V0 = p * x + y
    y_act = y + dy
    return dict(w=w, y=y, k=k, x1=x1, y1=y1, dy=dy, dx=dx, profit=dx * P - dy, p_eff=(w / (1 - w)) * y1 / x1,
                y_act=y_act, p_new=(w / (1 - w)) * y_act / x1, V0=V0, rel=100 * (dx * P - dy) / V0)


def il_weighted(r, w):
    """Pierderea impermanenta a unui fond ponderat: r^w / (w r + 1 - w) - 1."""
    return r ** w / (w * r + 1 - w) - 1


def a5_il():
    """IL pentru w = 0.5 si w = 0.8 la r = 0.5, 2, 4; aproximarea de ordinul doi -w(1-w)(ln r)^2 / 2."""
    out = {}
    for w in [0.5, 0.8]:
        for r in [0.5, 2.0, 4.0]:
            out[f'w{w:g}_r{r:g}'] = 100 * il_weighted(r, w)
            out[f'q{w:g}_r{r:g}'] = -100 * w * (1 - w) * np.log(r) ** 2 / 2
    return out


def a6_lvr(sig=0.70):
    """Rata LVR a unui fond ponderat: sigma^2 w (1 - w) / 2; w = 1/2 da sigma^2 / 8."""
    return {f'w{w:g}': 100 * sig ** 2 * w * (1 - w) / 2 for w in [0.5, 0.8, 0.95]}


def a7_tar(tar):
    """Algebra EQ-TAR pe estimarile USDC din B3: timpii de injumatatire in fiecare regim si numarul de zile pana cand
    o abatere de -285 pb (inchiderea din 11 martie 2023) reintra in banda."""
    d0 = 285.0
    n_out = np.log(tar['c'] / d0) / np.log(tar['phi_out'])
    return dict(d0=d0, n_out=n_out, n_days=int(np.ceil(n_out)), hl_in=tar['hl_in'], hl_out=tar['hl_out'])


def a8_mix(tar):
    """Limita in probabilitate a OLS liniar pe date EQ-TAR: phi_lin = phi_in (1 - s) + phi_out s,
    s = ponderea lui sum d_{t-1}^2 din afara benzii."""
    s = tar['share_var_out'] / 100
    return dict(s=100 * s, mix=tar['phi_in'] * (1 - s) + tar['phi_out'] * s, phi_lin=tar['phi_lin'])


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
    """Raportul dispersiilor (centrate): weekend (sambata, duminica) / zile lucratoare."""
    we = r[r.index.dayofweek >= 5]
    wd = r[r.index.dayofweek < 5]
    return we.var(ddof=1) / wd.var(ddof=1)


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


def b3_usdc(key='USDC', start='2021-01-01'):
    """Abaterea zilnica de la paritate (pb): statistici, EQ-TAR cu testul sup-Wald si bootstrap cu regresori ficsi
    (Hansen, 1996), cu si fara saptamana 9-16 martie 2023."""
    d = read_market(ASSETS[key][0]).loc[start:END]
    dev = 1e4 * (d['close'] - 1)
    ex = dev.drop(dev.loc['2023-03-09':'2023-03-16'].index)
    return dict(key=key, n=len(dev), sd=dev.std(), sd_ex=ex.std(), out50=int((dev.abs() > 50).sum()),
                out50_ex=int((ex.abs() > 50).sum()), min=dev.min(), min_date=str(dev.idxmin().date()),
                low=1e4 * (d['low'].min() - 1), low_date=str(d['low'].idxmin().date()),
                full=I.tar_fit(dev), ex=I.tar_fit(ex), kurt=float(dev.kurt()))


def fig_sem_usdc(tar):
    """USDC: abaterea de la paritate in 2023 si abaterea de azi fata de cea de ieri cu dreptele EQ-TAR din fiecare
    regim (pragul estimat c) si dreapta AR(1) liniara."""
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
    zz = z1[(z1.abs() <= 12).all(axis=1)]
    axes[1].scatter(zz['lag'], zz['now'], s=5, color=Teal, alpha=0.6, label='Pairs of days (within 12 bp)')
    c = tar['c']
    xi = np.array([-c, c])
    axes[1].plot(xi, tar['phi_in'] * xi, color=Forest, lw=1.8, label=f'Inside the band: slope {tar["phi_in"]:.2f}')
    for xo in [np.array([-12, -c]), np.array([c, 12])]:
        axes[1].plot(xo, tar['phi_out'] * xo, color=IDAred, lw=1.8)
    axes[1].plot([], [], color=IDAred, lw=1.8, label=f'Outside the band: slope {tar["phi_out"]:.2f}')
    for v in [-c, c]:
        axes[1].axvline(v, color=Gray, lw=0.6, ls='--')
    axes[1].set_xlim(-12, 12)
    axes[1].set_ylim(-12, 12)
    axes[1].set_xlabel('Deviation yesterday (bp)')
    axes[1].set_ylabel('Deviation today (bp)')
    fig.tight_layout()
    fig_legend_bottom(fig, ncol=2, y=0.0)
    save_fig('ch16_sem_usdc')


def b5_etf(etf='IBIT', coin='BTC'):
    """Urmarirea: beta zilnic vs saptamanal (HAC); deriva din comision ca medie a lui Delta ln(P_ETF/P_coin) cu eroare
    HAC; teste ADF (H0: radacina unitara) si KPSS (H0: stationaritate in jurul unei tendinte) pe nivelul raportului;
    comparatie cu panta regresiei nivelului pe timp; beta Dimson (1979) cu un decalaj si un avans."""
    from statsmodels.tsa.stattools import adfuller, kpss
    t = etf_tracking(etf, coin)
    p = pd.concat([price(etf), price(coin)], axis=1, join='inner').dropna()
    lr = np.log(p[etf] / p[coin])
    yrs = (lr.index[-1] - lr.index[0]).days / 365.25
    dl = lr.diff().dropna()
    ppy = len(dl) / yrs
    L = I.nw_lags(len(dl))
    m0 = sm.OLS(dl.values, np.ones(len(dl))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    tt = pd.Series((lr.index - lr.index[0]).days / 365.25, index=lr.index)
    m = hac_ols(lr, tt, lags=20)
    adf = adfuller(lr.values, regression='ct', autolag='AIC')
    kp = kpss(lr.values, regression='ct', nlags='auto')
    adf_d = adfuller(dl.values, regression='c', autolag='AIC')
    t.update(drift_mean=100 * ppy * m0.params[0], drift_mse=100 * ppy * m0.bse[0],
             drift_mlo=100 * ppy * (m0.params[0] - 1.96 * m0.bse[0]), drift_mhi=100 * ppy * (m0.params[0] + 1.96 * m0.bse[0]),
             drift_hac=100 * m.params.iloc[1], drift_se=100 * m.bse.iloc[1],
             drift_lo=100 * (m.params.iloc[1] - 1.96 * m.bse.iloc[1]), drift_hi=100 * (m.params.iloc[1] + 1.96 * m.bse.iloc[1]),
             adf=adf[0], adf_p=adf[1], kpss=kp[0], kpss_p=kp[1], adf_d=adf_d[0], adf_d_p=adf_d[1],
             t_beta_w=(t['beta_w'] - 1) / t['se_w'], lags=L, dimson=I.dimson(etf, coin))
    return t


def b7_equity(key='MSTR'):
    """Regresie saptamanala cu doi factori, testul b_BTC = 1 pe subperioade si testul sup-Wald (Andrews, 1993)
    pentru o ruptura la o data necunoscuta in toti cei trei coeficienti, cu erori HAC si CI Bai (1997)."""
    out = {}
    # subperioadele partitioneaza esantionul complet: p1 se incheie in ajunul ETF-urilor, p2 incepe cu ele
    for lab, a, b in [('full', '2021-04-16', END), ('p1', '2021-04-16', '2024-01-10'), ('p2', ETF_START, END)]:
        w = joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc[a:b]
        m = hac_ols(w[key], w[['BTC', 'SPX']])
        out[lab] = dict(n=len(w), b_btc=m.params['BTC'], se_btc=m.bse['BTC'], b_spx=m.params['SPX'],
                        se_spx=m.bse['SPX'], r2=m.rsquared, t1=(m.params['BTC'] - 1) / m.bse['BTC'],
                        alpha=52 * 100 * m.params['const'], alpha_t=m.tvalues['const'])
    w = 100 * joint_returns([key, 'BTC', 'SPX'], None, freq='W').loc['2021-04-16':END]
    X = np.column_stack([np.ones(len(w)), w['BTC'].values, w['SPX'].values])
    sw = I.sup_wald(w[key].values, X, w.index)
    Wser = pd.Series(sw.pop('W'), index=w.index)
    crit = I.sup_wald_crit(3)
    sw.update(p=float((crit >= sw['sup_w']).mean()), cv5=float(np.percentile(crit, 95)),
              W_etf=float(Wser.loc[ETF_START:].iloc[0]), W_date=float(Wser.loc[sw['date']]))
    out['sw'] = sw
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
        # indicatorii sunt imbricati: b = panta peste cuantila 10%, b + c10 intre 5% si 10%, b + c10 + c5 intre 1% si 5%,
        # b + c10 + c5 + c1 in cel mai rau 1%; SE ale sumelor din matricea de covarianta HAC completa
        Vc = m.cov_params()
        def tot(names):
            R = pd.Series(0.0, index=m.params.index)
            R[names] = 1.0
            return float(R @ m.params), float(np.sqrt(R @ Vc @ R))
        (t10, s10), (t5, s5), (t1, s1) = tot(['SPX', 'q10']), tot(['SPX', 'q10', 'q5']), tot(['SPX', 'q10', 'q5', 'q1'])
        mall = hac_ols(r['BTC'], r[['SPX']])          # regresia de acoperire pe toate zilele
        bl[lab] = dict(n=len(r), b=b0, se=m.bse['SPX'], c10=m.params['q10'], c5=m.params['q5'], c1=m.params['q1'],
                       tot10=t10, tot5=t5, tot1=t1, se_tot10=s10, se_tot5=s5, se_tot1=s1,
                       lo_tot1=t1 - 1.96 * s1, hi_tot1=t1 + 1.96 * s1,
                       b_all=mall.params['SPX'], se_all=mall.bse['SPX'],
                       se10=m.bse['q10'], se5=m.bse['q5'], se1=m.bse['q1'])
        # beta in zilele de scadere / crestere
        dn, up = r[r['SPX'] < 0], r[r['SPX'] > 0]
        bl[lab]['beta_dn'] = np.polyfit(dn['SPX'], dn['BTC'], 1)[0]
        bl[lab]['beta_up'] = np.polyfit(up['SPX'], up['BTC'], 1)[0]
        worst = r.nsmallest(10, 'SPX')
        bl[lab]['worst10_spx'] = worst['SPX'].mean()
        bl[lab]['worst10_btc'] = worst['BTC'].mean()
    out['bl'] = bl
    # Forbes-Rigobon: corelatia de dupa ETF-uri ajustata pentru volatilitatea S&P 500 (relativ la perioada 'pre')
    r = joint_returns(['BTC', 'SPX'], '2021-01-01')
    x0, x1 = r.loc[per['pre'][0]:per['pre'][1]].values, r.loc[per['post'][0]:per['post'][1]].values
    def rstar(z0, z1):
        r0, r1 = np.corrcoef(z0.T)[0, 1], np.corrcoef(z1.T)[0, 1]
        dl = z1[:, 1].var() / z0[:, 1].var() - 1
        return r1 / np.sqrt(1 + dl * (1 - r1 ** 2)) - r0, dl, r1 / np.sqrt(1 + dl * (1 - r1 ** 2))
    d_fr, delta, rs = rstar(x0, x1)
    rng = np.random.default_rng(SEED)
    def mbb(z):
        n = len(z)
        st = rng.integers(0, n - 19, int(np.ceil(n / 20)))
        return z[(st[:, None] + np.arange(20)[None, :]).ravel()[:n]]
    dd = [rstar(mbb(x0), mbb(x1))[0] for _ in range(B_BOOT)]
    out['fr'] = dict(delta=delta, rho_star=rs, diff=d_fr, lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5))
    # regresie cuantila (Koenker & Bassett, 1978): cuantila tau a lui r_BTC conditionata de r_SPX, bootstrap pe blocuri
    from statsmodels.regression.quantile_regression import QuantReg
    qr = {}
    for lab, (a, b) in per.items():
        z = 100 * joint_returns(['BTC', 'SPX'], a).loc[a:b]
        Xq = sm.add_constant(z['SPX'].values)
        for tau in [0.01, 0.05, 0.5]:
            bq = QuantReg(z['BTC'].values, Xq).fit(q=tau).params[1]
            bs = []
            zz = z.values
            for _ in range(300):
                y = mbb(zz)
                bs.append(QuantReg(y[:, 0], sm.add_constant(y[:, 1])).fit(q=tau).params[1])
            qr[f'{lab}_{int(100 * tau)}'] = dict(b=bq, se=float(np.std(bs)))
    out['qr'] = qr
    # volatilitatea si cea mai mare scadere in cele doua perioade
    p = price('BTC', '2021-01-01')
    for lab, (a, b) in per.items():
        x = p.loc[a:b]
        r = np.log(x).diff().dropna()
        out[lab + '_vol'] = 100 * r.std() * np.sqrt(365)
        out[lab + '_mdd'] = 100 * (x / x.cummax() - 1).min()
    return out


def fig_sem_hedge(c1):
    """Panta Bitcoin fata de S&P 500 in cele patru regimuri disjuncte ale regresiei cu indicatori imbricati (zilele
    S&P 500 peste cuantila 10%, intre 5% si 10%, intre 1% si 5%, cel mai rau 1%), inainte si dupa ETF-uri; +- 1.96 SE."""
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    labs = ['Above 10th percentile', '5th-10th percentile', '1st-5th percentile', 'Bottom 1%']
    x = np.arange(4)
    for i, (lab, c) in enumerate([('pre', MainBlue), ('post', Orange)]):
        b = c1['bl'][lab]
        ax.bar(x + (i - 0.5) * 0.38, [b['b'], b['tot10'], b['tot5'], b['tot1']], 0.36, color=c,
               yerr=1.96 * np.array([b['se'], b['se_tot10'], b['se_tot5'], b['se_tot1']]), capsize=2,
               error_kw=dict(ecolor='black', lw=0.7),
               label='Jan 2021 - 10 Jan 2024' if lab == 'pre' else '11 Jan 2024 - Sep 2026')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_xlabel('S&P 500 daily return regime')
    ax.set_ylabel('Bitcoin slope on the S&P 500')
    legend_outside_bottom(ax, ncol=2, y=-0.18)
    save_fig('ch16_sem_hedge')


def c2_ai(start='2021', end='2025'):
    """C2: raspunsul asistentului AI (randamente log din preturile taiate la 2021-2025, anualizare cu 252,
    r_f = 5%) si pasii corectarii: 365; randamente calculate inainte de selectarea perioadei; randamente simple
    in exces pentru raportul Sharpe; r_f = media randamentului bonurilor de trezorerie la 3 luni (FRED DTB3)."""
    btc = read_market(ASSETS['BTC'][0])['close']
    r = np.log(btc.loc[start:end]).diff().dropna()                  # codul AI: prima zi din 2021 se pierde
    out = dict(n_ai=len(r), per_year={str(k): int(v) for k, v in r.groupby(r.index.year).size().items()})
    for m in [252, 365]:
        mu, sd = r.mean() * m, r.std() * np.sqrt(m)
        out[f'mu{m}'], out[f'sd{m}'], out[f'sh{m}'] = 100 * mu, 100 * sd, (mu - 0.05) / sd
    rs = btc.pct_change().loc[start:end].dropna()                      # randamente simple, calculate inainte de selectie
    tb = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3', index_col=0, parse_dates=True).iloc[:, 0]
    rf = float(pd.to_numeric(tb, errors='coerce').dropna().loc[start:end].mean() / 100)
    mu, sd = rs.mean() * 365, rs.std() * np.sqrt(365)
    rl = np.log1p(rs)
    out.update(n=len(rs), mu_log=100 * rl.mean() * 365, mu_s=100 * mu, sd_s=100 * sd, rf=100 * rf,
               sh_s=(mu - rf) / sd, gap=100 * (mu - rl.mean() * 365), half_var=100 * sd ** 2 / 2)
    return out


if __name__ == '__main__':
    print('Seminar 16')
    S = {}
    S['A1'], S['A2'], S['A3'], S['A4'] = a1_index(), a2_replace(), a3_band(), a4_weighted()
    S['A5'], S['A6'] = a5_il(), a6_lvr()
    b1 = b1_btc_facts('BTC')
    fig_sem_weekend(b1)
    S['B1'] = {k: v for k, v in b1.items() if not k.startswith('_')}
    S['B2'] = {k: {kk: vv for kk, vv in b1_btc_facts(k).items() if not kk.startswith('_')} for k in ['ETH', 'SOL']}
    S['B3'] = b3_usdc('USDC')
    fig_sem_usdc(S['B3']['full'])
    S['A7'], S['A8'] = a7_tar(S['B3']['full']), a8_mix(S['B3']['full'])
    S['B4'] = {k: b3_usdc(k) for k in ['USDT', 'DAI']}
    S['B5'] = b5_etf('IBIT', 'BTC')
    S['B6'] = b5_etf('ETHA', 'ETH')
    S['B7'] = b7_equity('MSTR')
    S['B8'] = b7_equity('COIN')
    c1 = c1_hedge()
    fig_sem_hedge(c1)
    S['C1'] = c1
    S['C2'] = c2_ai()
    with open(os.path.join(HERE, 'sem16_results.json'), 'w') as fh:
        json.dump(jsonable(S), fh, indent=1)
    print('saved sem16_results.json')

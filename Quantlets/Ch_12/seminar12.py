"""
seminar12.py -- Calculele Seminarului 12 (MFM): optiuni si suprafata de volatilitate
==================================================================================
Partea A: paritate put-call, arbore binomial, Black-Scholes si senzitivitati, volatilitate implicita (Newton),
          varianta implicita dintr-o banda de optiuni.
Partea B: acoperire delta simulata cu intervale bootstrap, SVI pe optiuni Bitcoin, prima de risc a variantei
          (S&P 500 si Bitcoin) cu erori standard Newey-West, regresia Mincer-Zarnowitz.
Partea C: este prima de risc a variantei un semnal tranzactionabil? (swap de varianta sintetic, lunar)
Cifrele sunt salvate in sem12_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, integrate
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import load_close, deribit_chain, dvol_history  # noqa: E402
from option_tools import (bs_price, bs_greeks, implied_vol, newton_iv, crr_price, svi_w, svi_fit,  # noqa: E402
                          variance_from_strip, delta_hedge)
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray, LightGray,  # noqa: E402
                                 save_fig, legend_outside_bottom, fig_legend_bottom, nw_mean, gbm_paths, btc_surface,
                                 pick, vrp_sp500, vrp_btc, delta_hedged_history, jsonable, SEED, HERE,
                                 rnd_from_svi)

B_BOOT = 1000


# =============================================================================
# PARTEA A
# =============================================================================
def a1_parity():
    """Arbitraj de paritate: S = 50, K = 50, T = 6 luni, r = 4%, call 4.20, put 2.80."""
    S, K, T, r, C, P = 50.0, 50.0, 0.5, 0.04, 4.20, 2.80
    pvk = K * np.exp(-r * T)
    return dict(pvk=pvk, lhs=C - P, rhs=S - pvk, p_fair=C - S + pvk, cash=C - P - S + pvk,
                profit100=100 * (C - P - S + pvk))


def a2_parity_div():
    """Paritate cu randament de dividend q: S = 80, K = 75, T = 3 luni, r = 5%, q = 2%, call 7.10, put 1.20."""
    S, K, T, r, q, C, P = 80.0, 75.0, 0.25, 0.05, 0.02, 7.10, 1.20
    se, pvk = S * np.exp(-q * T), K * np.exp(-r * T)
    return dict(se=se, pvk=pvk, lhs=C - P, rhs=se - pvk, gap=C - P - (se - pvk))


def a3_binomial():
    """Un pas binomial: S = 100, u = 1.2, d = 0.9, R = 1.05, call K = 105."""
    S, u, d, R, K = 100.0, 1.2, 0.9, 1.05, 105.0
    Cu, Cd = max(S * u - K, 0), max(S * d - K, 0)
    delta = (Cu - Cd) / (S * (u - d))
    B = (u * Cd - d * Cu) / ((u - d) * R)
    q = (R - d) / (u - d)
    return dict(Cu=Cu, Cd=Cd, delta=delta, B=B, C=delta * S + B, q=q, C_rn=(q * Cu + (1 - q) * Cd) / R)


def a4_american():
    """Doi pasi binomiali, put american si european: S = 100, u = 1.2, d = 0.9, R = 1.05, K = 105."""
    S, u, d, R, K = 100.0, 1.2, 0.9, 1.05, 105.0
    q = (R - d) / (u - d)
    S2 = {'uu': S * u * u, 'ud': S * u * d, 'dd': S * d * d}
    P2 = {k: max(K - v, 0) for k, v in S2.items()}
    Pu_e = (q * P2['uu'] + (1 - q) * P2['ud']) / R
    Pd_e = (q * P2['ud'] + (1 - q) * P2['dd']) / R
    Pu_a, Pd_a = max(Pu_e, K - S * u), max(Pd_e, K - S * d)
    return dict(q=q, Suu=S2['uu'], Sud=S2['ud'], Sdd=S2['dd'], Puu=P2['uu'], Pud=P2['ud'], Pdd=P2['dd'],
                Pu_e=Pu_e, Pd_e=Pd_e, ex_u=max(K - S * u, 0), ex_d=K - S * d, Pu_a=Pu_a, Pd_a=Pd_a,
                P_e=(q * Pu_e + (1 - q) * Pd_e) / R, P_a=max((q * Pu_a + (1 - q) * Pd_a) / R, K - S),
                early=Pd_a > Pd_e)


def a5_bs():
    """Black-Scholes pas cu pas: S = K = 100, T = 6 luni, r = 3%, sigma = 25%."""
    S, K, T, r, s = 100.0, 100.0, 0.5, 0.03, 0.25
    g = bs_greeks(S, K, T, r, s)
    return dict(d1=float(g['d1']), d2=float(g['d2']), Nd1=float(stats.norm.cdf(g['d1'])), Nd2=float(stats.norm.cdf(g['d2'])),
                pvk=K * np.exp(-r * T), C=float(bs_price(S, K, T, r, s)), P=float(bs_price(S, K, T, r, s, 'put')),
                delta=float(g['delta']), gamma=float(g['gamma']), vega=float(g['vega']), theta=float(g['theta']),
                nd1=float(stats.norm.pdf(g['d1'])))


def a6_delta_gamma():
    """Acoperire delta-gamma: vandut 1000 de call-uri A5; instrumente: call K = 110 (aceeasi scadenta) si actiunea."""
    S, T, r, s = 100.0, 0.5, 0.03, 0.25
    g1 = bs_greeks(S, 100, T, r, s); g2 = bs_greeks(S, 110, T, r, s)
    pos_delta, pos_gamma = -1000 * float(g1['delta']), -1000 * float(g1['gamma'])
    n2 = -pos_gamma / float(g2['gamma'])
    shares = -(pos_delta + n2 * float(g2['delta']))
    return dict(delta1=float(g1['delta']), gamma1=float(g1['gamma']), delta2=float(g2['delta']), gamma2=float(g2['gamma']),
                pos_delta=pos_delta, pos_gamma=pos_gamma, n2=n2, shares=shares, c2=float(bs_price(S, 110, T, r, s)),
                vega_left=-1000 * float(g1['vega']) + n2 * float(g2['vega']))


def a7_newton():
    """Volatilitatea implicita prin Newton: call S = K = 100, T = 3 luni, r = 2%, pret de piata 4.50, sigma_0 = 20%."""
    steps = newton_iv(4.50, 100.0, 100.0, 0.25, 0.02, sigma0=0.20, steps=3)
    return dict(steps=steps, exact=implied_vol(4.50, 100.0, 100.0, 0.25, 0.02))


A8_K = [80, 85, 90, 95, 100, 105, 110, 115, 120]


def a8_strip():
    """Varianta implicita pe 90 de zile dintr-o banda de 9 optiuni OTM (F = 100, r = 0), preturi rotunjite la 0.01."""
    F, T = 100.0, 90 / 365
    iv = lambda K: 0.18 - 0.35 * np.log(K / F) + 0.9 * np.log(K / F) ** 2
    Q = []
    for K in A8_K:
        kind = 'put' if K < F else 'call'
        if K == F:
            Q.append(round(0.5 * (float(bs_price(F, K, T, 0.0, iv(K), 'call')) + float(bs_price(F, K, T, 0.0, iv(K), 'put'))), 2))
        else:
            Q.append(round(float(bs_price(F, K, T, 0.0, iv(K), kind)), 2))
    var = variance_from_strip(A8_K, Q, F, T)
    contrib = [2 / T * 5 / K ** 2 * q for K, q in zip(A8_K, Q)]
    return dict(Q=Q, iv=[float(100 * iv(K)) for K in A8_K], var=var, vol=100 * np.sqrt(var), atm=100 * iv(100.0),
                contrib=contrib, share_puts=sum(contrib[:4]) / sum(contrib))


# =============================================================================
# PARTEA A (derivari, cu cifre de verificare)
# =============================================================================
BFLY_EXPIRY = '2026-10-30 08:00:00'


def a1_butterfly(h=1000.0, K0=85000.0):
    """Convexitatea in K pe lantul Bitcoin: fluture C(K-h) - 2C(K) + C(K+h) din preturile de marcare in USD (prima in BTC
    x indicele S, conventia Deribit) si costul executabil (aripile la ask, corpul la bid); densitatea
    q(K) ~ e^{r tau} fluture / h^2, cu e^{r tau} = F/S (rata implicita in forward-ul Deribit)."""
    c = deribit_chain()
    g = c[(c['expiry'] == pd.Timestamp(BFLY_EXPIRY)) & (c['type'] == 'call')].set_index('strike').sort_index()
    F, S = float(g['forward'].iloc[0]), float(g['index'].iloc[0])
    usd = lambda col: g[col] * S
    m, b, a = usd('mark_price'), usd('bid'), usd('ask')
    out = dict(F=F, S=S, growth=F / S, h=h, K=K0, Cm=float(m[K0 - h]), C0=float(m[K0]), Cp=float(m[K0 + h]),
               bid0=float(b[K0]), askm=float(a[K0 - h]), askp=float(a[K0 + h]))
    out['bf_mark'] = out['Cm'] - 2 * out['C0'] + out['Cp']
    out['bf_exec'] = out['askm'] - 2 * out['bid0'] + out['askp']
    out['q'] = F / S * out['bf_mark'] / h ** 2
    out['mass'] = F / S * out['bf_mark'] / h                 # E^Q[(h - |S_T - K|)^+]/h: masa ponderata triunghiular ~ h q(K)
    out['p_int'] = 2 * h * out['q']                           # ~ P(K - h < S_T < K + h), fara ponderare
    # toate tripletele echidistante din lantul acestei scadente
    Ks = list(g.index)
    n_tr = n_neg_mark = n_neg_exec = 0
    neg, spr = [], []
    for i in range(1, len(Ks) - 1):
        for j in range(i + 1, len(Ks)):
            hh = Ks[j] - Ks[i]
            if Ks[i] - hh in g.index:
                n_tr += 1
                bm = m[Ks[i] - hh] - 2 * m[Ks[i]] + m[Ks[j]]
                n_neg_mark += int(bm < 0)
                if bm < 0:
                    neg.append(float(bm)); spr.append(float(a[Ks[i]] - b[Ks[i]]))
                if np.isfinite(a[Ks[i] - hh]) and np.isfinite(b[Ks[i]]) and np.isfinite(a[Ks[j]]) and b[Ks[i]] > 0:
                    n_neg_exec += int(a[Ks[i] - hh] - 2 * b[Ks[i]] + a[Ks[j]] < 0)
    out.update(n_triples=n_tr, n_neg_mark=n_neg_mark, n_neg_exec=n_neg_exec, worst_neg=float(min(neg)) if neg else 0.0,
               spread_neg=float(np.median(spr)) if spr else 0.0)
    return out


def a2_implied_forward():
    """Paritatea ca regresie: C - P = D F - D K pe toate preturile de exercitare cu call si put cotate
    (mid in USD = prima in BTC x indicele S, conventia Deribit)."""
    c = deribit_chain()
    g = c[(c['expiry'] == pd.Timestamp(BFLY_EXPIRY)) & (c['bid'] > 0) & (c['ask'] > 0)].copy()
    F0, S0 = float(g['forward'].iloc[0]), float(g['index'].iloc[0])
    tau = float((g['expiry'].iloc[0] - g['snapshot_utc'].iloc[0]).total_seconds() / (365 * 86400))
    g['mid'] = 0.5 * (g['bid'] + g['ask']) * S0
    p = g.pivot_table(index='strike', columns='type', values='mid').dropna()
    y = p['call'] - p['put']
    X = sm.add_constant(pd.Series(p.index.values, index=p.index, name='K'))
    m = sm.OLS(y, X).fit(cov_type='HC1')
    D = -m.params['K']
    Fh = m.params['const'] / D
    # metoda delta: F = -a / b
    a_, b_ = m.params['const'], m.params['K']
    grad = np.array([-1 / b_, a_ / b_ ** 2])
    seF = float(np.sqrt(grad @ m.cov_params().values @ grad))
    return dict(n=int(len(p)), D=float(D), D_se=float(m.bse['K']), F=float(Fh), F_se=seF, F_exch=F0, S=S0, tau=tau,
                D_exch=S0 / F0, r_impl=float(-np.log(D) / tau), r_exch=float(np.log(F0 / S0) / tau),
                kmin=float(p.index.min()), kmax=float(p.index.max()), r2=float(m.rsquared))


def a4_crr_error():
    """Eroarea CRR fata de Black-Scholes, inmultita cu N: oscilatie par/impar, ordinul 1/N."""
    S, K, T, r, s = 100.0, 100.0, 1.0, 0.05, 0.20
    bs = float(bs_price(S, K, T, r, s))
    return {str(N): dict(price=float(crr_price(S, K, T, r, s, N)), nerr=float(N * (crr_price(S, K, T, r, s, N) - bs)))
            for N in [50, 51, 100, 101, 200, 201, 400, 401]} | dict(bs=bs)


def a8_lognormal_strip():
    """Banda de optiuni pentru o distributie log-normala (sigma = 20%, 90 de zile, F = 100, r = 0): valoarea exacta
    sigma^2 = 0.04; formula Cboe cu Delta K = 5 pe [80, 120]; grila densa pe [80, 120]; grila densa pe (0, infinit)."""
    F, T, s = 100.0, 90 / 365, 0.20
    q = lambda K: np.where(K < F, bs_price(F, K, T, 0.0, s, 'put'), bs_price(F, K, T, 0.0, s, 'call'))
    K5 = np.arange(80.0, 120.1, 5.0)
    Q5 = np.where(K5 == F, 0.5 * (bs_price(F, K5, T, 0.0, s, 'put') + bs_price(F, K5, T, 0.0, s, 'call')), q(K5))
    v5 = variance_from_strip(K5, Q5, F, T)
    Kd = np.linspace(80, 120, 40001)
    vd = 2 / T * integrate.trapezoid(q(Kd) / Kd ** 2, Kd)
    Kw = F * np.exp(np.linspace(-3, 3, 60001))
    vw = 2 / T * integrate.trapezoid(q(Kw) / Kw ** 2, Kw)
    return dict(exact=s ** 2, cboe=float(v5), dense=float(vd), wide=float(vw), vol_cboe=float(100 * np.sqrt(v5)),
                vol_dense=float(100 * np.sqrt(vd)), vol_wide=float(100 * np.sqrt(vw)),
                trunc=float(vd - s ** 2), disc=float(v5 - vd))


def b8_rnd_band(days=90, B=300):
    """Densitatea neutra la risc pentru scadenta BTC cea mai apropiata de 90 de zile: banda bootstrap pe perechi,
    probabilitatile P(S_T < 0.8F) si P(S_T > 1.2F) cu intervale, fata de densitatea log-normala ATM."""
    c, tab, t0 = btc_surface()
    e = pick(tab, days); f = tab.loc[e]
    F, T = float(f['F']), float(f['T'])
    p0 = [float(f[x]) for x in ['a', 'b', 'rho', 'm', 's']]
    K = F * np.exp(np.linspace(-1.5, 1.2, 2701))
    g = c[c['expiry'] == e]
    kq, wq = g['k'].values, g['w'].values
    def probs(q):
        A = integrate.trapezoid(q, K)
        lo = integrate.trapezoid(q[K <= 0.8 * F], K[K <= 0.8 * F]) / A
        hi = 1 - integrate.trapezoid(q[K <= 1.2 * F], K[K <= 1.2 * F]) / A
        return lo, hi
    q0 = rnd_from_svi(p0, F, T, K)
    p80, p120 = probs(q0)
    atm = np.sqrt(svi_w(0.0, *p0) / T)
    ln = lambda x: float(stats.lognorm.cdf(x * F, s=atm * np.sqrt(T), scale=F * np.exp(-0.5 * atm ** 2 * T)))
    rng = np.random.default_rng(SEED)
    P80, P120, D80, D120 = [], [], [], []   # D: SVI minus log-normal, cu volatilitatea ATM a fiecarei reestimari
    while len(P80) < B:
        i = rng.integers(0, len(kq), len(kq))
        if len(np.unique(kq[i])) < 6:
            continue
        pb = svi_fit(kq[i], wq[i])
        pbv = [pb[x] for x in ['a', 'b', 'rho', 'm', 's']]
        a_, b_ = probs(rnd_from_svi(pbv, F, T, K))
        P80.append(a_); P120.append(b_)
        sb = np.sqrt(svi_w(0.0, *pbv) / T)
        lnb = lambda x: float(stats.lognorm.cdf(x * F, s=sb * np.sqrt(T), scale=F * np.exp(-0.5 * sb ** 2 * T)))
        D80.append(a_ - lnb(0.8)); D120.append(b_ - (1 - lnb(1.2)))
    kmin, kmax = float(np.exp(kq.min())), float(np.exp(kq.max()))
    A0 = integrate.trapezoid(q0, K)
    ext_lo = float(integrate.trapezoid(q0[K <= kmin * F], K[K <= kmin * F]) / A0)       # masa sub ultima cotatie
    ext_hi = float(1 - integrate.trapezoid(q0[K <= kmax * F], K[K <= kmax * F]) / A0)   # masa peste ultima cotatie
    return dict(expiry=str(pd.Timestamp(e).date()), days=float(f['days']), n=int(len(kq)), atm=float(100 * atm),
                ext_lo=ext_lo, ext_hi=ext_hi, ext_lo_share=ext_lo / float(p80), ext_hi_share=ext_hi / float(p120),
                p80=float(p80), p80_lo=float(np.quantile(P80, 0.025)), p80_hi=float(np.quantile(P80, 0.975)),
                p120=float(p120), p120_lo=float(np.quantile(P120, 0.025)), p120_hi=float(np.quantile(P120, 0.975)),
                ln80=ln(0.8), ln120=1 - ln(1.2),
                d80_lo=float(np.quantile(D80, 0.025)), d80_hi=float(np.quantile(D80, 0.975)),
                d120_lo=float(np.quantile(D120, 0.025)), d120_hi=float(np.quantile(D120, 0.975)), kf_min=float(np.exp(kq.min())), kf_max=float(np.exp(kq.max())))


# =============================================================================
# PARTEA B
# =============================================================================
def b1_hedge_boot():
    """Eroarea de acoperire (abaterea standard) pentru N reechilibrari, cu interval bootstrap de 95%; panta log-log."""
    rng = np.random.default_rng(SEED)
    S0, K, T, r, s, mu = 100.0, 100.0, 0.25, 0.04, 0.20, 0.08
    paths = gbm_paths(S0, mu, s, T, 252, 10000, seed=SEED)
    prem = float(bs_price(S0, K, T, r, s))
    Ns = [6, 12, 21, 63, 126, 252]
    E = {n: delta_hedge(paths, K, T, r, s, n) for n in Ns}
    idx = rng.integers(0, paths.shape[0], size=(B_BOOT, paths.shape[0]))
    sd = {n: float(E[n].std()) for n in Ns}
    boot = {n: np.array([E[n][i].std() for i in idx]) for n in Ns}
    ci = {n: (float(np.quantile(boot[n], 0.025)), float(np.quantile(boot[n], 0.975))) for n in Ns}
    x = np.log(Ns)
    slope = float(np.polyfit(x, np.log([sd[n] for n in Ns]), 1)[0])
    bs_slopes = np.array([np.polyfit(x, np.log([boot[n][b] for n in Ns]), 1)[0] for b in range(B_BOOT)])
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    y = np.array([sd[n] for n in Ns]); lo = np.array([ci[n][0] for n in Ns]); hi = np.array([ci[n][1] for n in Ns])
    ax.errorbar(Ns, y, yerr=[y - lo, hi - y], fmt='o-', color=MainBlue, ms=4, capsize=3,
                label='Standard deviation of the hedging error, 95% bootstrap interval')
    ax.plot(Ns, y[0] * np.sqrt(Ns[0] / np.array(Ns)), color=Gray, lw=0.8, ls='--', label='Slope $-1/2$')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Number of rebalancings $N$'); ax.set_ylabel('Standard deviation (per option)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch12_sem_hedge')
    return dict(prem=prem, sd=sd, ci=ci, slope=slope, slope_lo=float(np.quantile(bs_slopes, 0.025)),
                slope_hi=float(np.quantile(bs_slopes, 0.975)), ratio_63_252=sd[63] / sd[252])


def b2_delta_hedged():
    """Vanzatorul unei optiuni call pe o luna pe S&P 500, acoperita zilnic la VIX: media P&L, Newey-West, bootstrap pe blocuri."""
    d = delta_hedged_history()
    x = d['pnl'].values
    m, se = nw_mean(x, 3)
    rng = np.random.default_rng(SEED)
    n, L = len(x), 6
    means = []
    for _ in range(2000):
        st = rng.integers(0, n - L + 1, size=int(np.ceil(n / L)))   # toate blocurile, inclusiv ultimul
        means.append(np.concatenate([x[s:s + L] for s in st])[:n].mean())
    worst5 = np.sort(x)[:5]
    return dict(n=n, mean=m, se=se, t=m / se, lo=float(np.quantile(means, 0.025)), hi=float(np.quantile(means, 0.975)),
                win=float((x > 0).mean()), mean_ex5=float(np.sort(x)[5:].mean()), worst5_sum=float(worst5.sum()),
                total=float(x.sum()), share_worst5=float(-worst5.sum() / x.sum()))


def b3_svi():
    """SVI pe scadenta BTC cea mai apropiata de 30 de zile; bootstrap pe perechi pentru volatilitatea ATM si asimetrie."""
    c, tab, t0 = btc_surface()
    e = pick(tab, 30)
    g = c[c['expiry'] == e]
    f = tab.loc[e]
    T = float(f['T'])
    k, w = g['k'].values, g['w'].values
    rng = np.random.default_rng(SEED)
    atm, rr, curves = [], [], []
    kk = np.linspace(k.min(), k.max(), 120)
    for _ in range(300):
        i = rng.integers(0, len(k), len(k))
        if len(np.unique(k[i])) < 6:
            continue
        p = svi_fit(k[i], w[i])
        iv = lambda x: 100 * np.sqrt(np.clip(svi_w(x, p['a'], p['b'], p['rho'], p['m'], p['s']), 1e-8, None) / T)
        atm.append(float(iv(0.0))); rr.append(float(iv(0.15) - iv(-0.15))); curves.append(iv(kk))
    curves = np.array(curves)
    # conditia de absenta a arbitrajului de tip fluture (Gatheral-Jacquier): g(k) >= 0
    a, b, rho, m, s = (float(f[x]) for x in ['a', 'b', 'rho', 'm', 's'])
    kg = np.linspace(-1.5, 1.5, 3001)
    W = svi_w(kg, a, b, rho, m, s)
    W1 = b * (rho + (kg - m) / np.sqrt((kg - m) ** 2 + s ** 2))
    W2 = b * s ** 2 / ((kg - m) ** 2 + s ** 2) ** 1.5
    gk = (1 - kg * W1 / (2 * W)) ** 2 - W1 ** 2 / 4 * (1 / W + 0.25) + W2 / 2
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    ax.fill_between(kk, np.quantile(curves, 0.025, axis=0), np.quantile(curves, 0.975, axis=0), color=LightGray,
                    label='95% bootstrap band of the SVI fit')
    ax.scatter(k, g['mark_iv'], s=10, color=IDAred, label='Quotes (mark implied volatility)', zorder=3)
    ax.plot(kk, 100 * np.sqrt(svi_w(kk, a, b, rho, m, s) / T), color=MainBlue, lw=1.4, label='SVI fit')
    ax.set_xlabel('Log-moneyness $k = \\ln(K/F)$'); ax.set_ylabel('Implied volatility (%)')
    ax.set_title(f"Bitcoin, expiry {pd.Timestamp(e).strftime('%d %b %Y')} ({f['days']:.0f} days)", fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch12_sem_svi')
    return dict(expiry=str(pd.Timestamp(e).date()), days=float(f['days']), n=int(len(k)), a=a, b=b, rho=rho, m=m, s=s,
                rmse=float(f['rmse_iv']), atm=float(f['atm']), rr=float(f['rr']),
                atm_lo=float(np.quantile(atm, 0.025)), atm_hi=float(np.quantile(atm, 0.975)),
                rr_lo=float(np.quantile(rr, 0.025)), rr_hi=float(np.quantile(rr, 0.975)), gmin=float(gk.min()),
                snapshot=str(t0))


def b5_vrp():
    """Prima de risc a variantei S&P 500: media, eroarea Newey-West (21 de lag-uri), subperioade."""
    d = vrp_sp500()
    out = {}
    for tag, x in [('all', d), ('p1', d.loc[:'2007-12-31']), ('p2', d.loc['2008-01-01':])]:
        m, se = nw_mean(x['vrp'], 21)
        mv, sev = nw_mean(x['vrp_vol'], 21)
        out[tag] = dict(n=int(len(x)), mean=m, se=se, t=m / se, lo=m - 1.96 * se, hi=m + 1.96 * se, mean_vol=mv, se_vol=sev,
                        share=float((x['vrp'] > 0).mean()), iv=float(x['vix'].mean()), rv=float(np.sqrt(x['rv']).mean()))
    # stabilitatea intre subperioade: VRP pe constanta si un indicator 2008-2026, erori Newey-West (21 de lag-uri)
    X = sm.add_constant(pd.Series((d.index >= '2008-01-01').astype(float), index=d.index, name='post'))
    for col, tag in [('vrp', 'diff'), ('vrp_vol', 'diff_vol')]:
        m = sm.OLS(d[col], X).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
        out[tag] = dict(d=float(m.params['post']), se=float(m.bse['post']), t=float(m.tvalues['post']),
                        p=float(m.pvalues['post']))
    naive = d['vrp'].std() / np.sqrt(len(d))
    out['naive_se'] = float(naive)
    out['ratio_se'] = out['all']['se'] / float(naive)
    return out


def b6_mz():
    """Mincer-Zarnowitz: varianta realizata pe urmatoarele 21 de zile pe VIX^2; test comun a = 0, b = 1 (HAC)."""
    d = vrp_sp500()
    m = sm.OLS(d['rv'], sm.add_constant(d[['iv2']])).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
    w = m.wald_test('const = 0, iv2 = 1', scalar=True)
    m2 = sm.OLS(d['rv'], sm.add_constant(d[['iv2', 'rv_past']])).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
    return dict(a=float(m.params['const']), a_se=float(m.bse['const']), b=float(m.params['iv2']), b_se=float(m.bse['iv2']),
                r2=float(m.rsquared), wald=float(w.statistic), wald_p=float(w.pvalue),
                b2=float(m2.params['iv2']), b2_se=float(m2.bse['iv2']), c2=float(m2.params['rv_past']),
                c2_se=float(m2.bse['rv_past']), r2_2=float(m2.rsquared))


def b7_vrp_btc():
    d = vrp_btc()
    m, se = nw_mean(d['vrp_vol'], 30)
    ratio = float(d['dvol'].mean() / np.sqrt(d['rv']).mean())
    s = vrp_sp500()
    return dict(n=int(len(d)), mean_vol=m, se_vol=se, t=m / se, share=float((d['vrp'] > 0).mean()), ratio=ratio,
                ratio_sp=float(s['vix'].mean() / np.sqrt(s['rv']).mean()),
                dvol=float(d['dvol'].mean()), rv=float(np.sqrt(d['rv']).mean()))


# =============================================================================
# PARTEA C: swap de varianta sintetic, vandut lunar
# =============================================================================
def monthly_swap(iv, r, H, ppy):
    """P&L lunar al vanzatorului unui swap de varianta cu notional vega 1: (IV^2 - RV) / (2 IV), in puncte de volatilitate."""
    rows = []
    iv, r = iv.align(r, join='inner')
    for i0 in range(0, len(iv) - H, H):
        k = iv.iloc[i0]
        rv = ppy / H * np.sum(r.iloc[i0 + 1:i0 + H + 1].values ** 2) * 1e4
        rows.append(dict(date=iv.index[i0], iv=k, rv=np.sqrt(rv), pnl=(k ** 2 - rv) / (2 * k)))
    return pd.DataFrame(rows).set_index('date')


def perf(p, per_year=12):
    x = p['pnl']
    cum = x.cumsum()
    sr = x.mean() / x.std() * np.sqrt(per_year)
    rng = np.random.default_rng(SEED)
    n, L = len(x), 3
    srs = []
    xv = x.values
    for _ in range(2000):
        st = rng.integers(0, n - L + 1, size=int(np.ceil(n / L)))   # toate blocurile, inclusiv ultimul
        y = np.concatenate([xv[s:s + L] for s in st])[:n]
        srs.append(y.mean() / y.std() * np.sqrt(per_year))
    return dict(n=int(n), mean=float(x.mean()), sd=float(x.std()), sharpe=float(sr), sr_lo=float(np.quantile(srs, 0.025)),
                sr_hi=float(np.quantile(srs, 0.975)), win=float((x > 0).mean()), worst=float(x.min()),
                worst_date=x.idxmin().strftime('%Y-%m'), maxdd=float((cum - cum.cummax()).min()), skew=float(stats.skew(x)),
                start=x.index[0].strftime('%Y-%m'), end=x.index[-1].strftime('%Y-%m'))


def c1_vrp_signal():
    px = pd.concat([load_close('sp500'), load_close('vix'), load_close('vix3m')], axis=1, join='inner')
    sp = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    r_sp = np.log(sp['sp500']).diff().dropna()
    p_sp = monthly_swap(sp['vix'].loc[r_sp.index], r_sp, 21, 252)
    ratio = (px['vix'] / px['vix3m']).dropna()
    p_sp3 = p_sp.loc[ratio.index[0]:]
    active = ratio.reindex(p_sp3.index) <= 1
    cond = p_sp3.assign(pnl=p_sp3['pnl'].where(active, 0.0))   # lunile sarite: P&L 0 (numerar), acelasi calendar lunar
    dv = dvol_history()
    b = load_close('btc')
    r_b = np.log(b).diff().dropna()
    p_b = monthly_swap(dv, r_b, 30, 365)
    # sensibilitatea la calendarul lunar: aceeasi strategie, cu grila de 21 de zile pornita in fiecare dintre primele 21 de zile
    grid = []
    for o in range(21):
        x = monthly_swap(sp['vix'].loc[r_sp.index].iloc[o:], r_sp.iloc[o:], 21, 252)['pnl']
        grid.append((x.mean() / x.std() * np.sqrt(12), x.min()))
    grid = np.array(grid)
    res = dict(grid_sr_min=float(grid[:, 0].min()), grid_sr_max=float(grid[:, 0].max()),
               grid_worst_min=float(grid[:, 1].min()), grid_worst_max=float(grid[:, 1].max()))
    res.update(sp=perf(p_sp), sp_since=perf(p_sp3), sp_cond=perf(cond), sp_active=perf(p_sp3[active]), btc=perf(p_b),
               skipped=int((~active).sum()), skipped_mean=float(p_sp3.loc[~active, 'pnl'].mean()))

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    axes[0].plot(p_sp.index, p_sp['pnl'].cumsum(), color=MainBlue, lw=1.1, label='S&P 500, every month (VIX)')
    axes[0].plot(cond.index, cond['pnl'].cumsum() + p_sp['pnl'].cumsum().reindex(cond.index).iloc[0] - cond['pnl'].iloc[0],
                 color=Forest, lw=1.0, ls='--', label='S&P 500, skip months that start in backwardation')
    axes[0].set_ylabel('Cumulative P&L (volatility points)')
    axes[0].axhline(0, color=Gray, lw=0.5)
    legend_outside_bottom(axes[0], ncol=1, y=-0.14)
    axes[1].plot(p_b.index, p_b['pnl'].cumsum(), color=Amber, lw=1.1, label='Bitcoin, every 30 days (DVOL)')
    axes[1].axhline(0, color=Gray, lw=0.5)
    legend_outside_bottom(axes[1], ncol=1, y=-0.14)
    plt.tight_layout()
    save_fig('ch12_sem_vrp_signal')
    return res


if __name__ == '__main__':
    RES = dict(A1=a1_parity(), A2=a2_parity_div(), A3=a3_binomial(), A4=a4_american(), A5=a5_bs(), A6=a6_delta_gamma(),
               A7=a7_newton(), A8=a8_strip(), A1b=a1_butterfly(), A2b=a2_implied_forward(), A4b=a4_crr_error(),
               A8b=a8_lognormal_strip())
    RES['B1'] = b1_hedge_boot()
    RES['B2'] = b2_delta_hedged()
    RES['B3'] = b3_svi()
    RES['B5'] = b5_vrp()
    RES['B6'] = b6_mz()
    RES['B7'] = b7_vrp_btc()
    RES['B8'] = b8_rnd_band()
    RES['C1'] = c1_vrp_signal()
    with open(os.path.join(HERE, 'sem12_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved sem12_results.json')

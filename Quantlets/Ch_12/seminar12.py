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
                                 rnd_from_svi, cboe_strip)

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
    P80, P120, D80, D120, QB = [], [], [], [], []   # D: SVI minus log-normal, cu volatilitatea ATM a fiecarei reestimari
    while len(P80) < B:
        i = rng.integers(0, len(kq), len(kq))
        if len(np.unique(kq[i])) < 6:
            continue
        pb = svi_fit(kq[i], wq[i])
        pbv = [pb[x] for x in ['a', 'b', 'rho', 'm', 's']]
        qb = rnd_from_svi(pbv, F, T, K)
        a_, b_ = probs(qb)
        P80.append(a_); P120.append(b_); QB.append(qb / integrate.trapezoid(qb, K))
        sb = np.sqrt(svi_w(0.0, *pbv) / T)
        lnb = lambda x: float(stats.lognorm.cdf(x * F, s=sb * np.sqrt(T), scale=F * np.exp(-0.5 * sb ** 2 * T)))
        D80.append(a_ - lnb(0.8)); D120.append(b_ - (1 - lnb(1.2)))
    kmin, kmax = float(np.exp(kq.min())), float(np.exp(kq.max()))
    A0 = integrate.trapezoid(q0, K)
    # grafic: densitatea cu banda bootstrap, densitatea log-normala, pragurile 0.8F si 1.2F si intervalul cotat
    QB = np.array(QB); x = K / F
    lnd = stats.lognorm.pdf(K, s=atm * np.sqrt(T), scale=F * np.exp(-0.5 * atm ** 2 * T)) * F
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    ax.axvspan(x.min(), kmin, color=Amber, alpha=0.15, lw=0, label='Outside the quoted strikes (SVI extrapolation)')
    ax.axvspan(kmax, x.max(), color=Amber, alpha=0.15, lw=0)
    ax.fill_between(x, np.quantile(QB, 0.025, axis=0) * F, np.quantile(QB, 0.975, axis=0) * F, color=Teal, alpha=0.35,
                    lw=0, label='95% pairs-bootstrap band (300 SVI refits)')
    ax.plot(x, q0 / A0 * F, color=MainBlue, lw=1.4, label='Risk-neutral density from the SVI smile')
    ax.plot(x, lnd, color=IDAred, lw=1.1, ls='--', label=f'Log-normal density, ATM volatility {100 * atm:.1f}%')
    for thr in (0.8, 1.2):
        ax.axvline(thr, color=Gray, lw=0.8, ls=':')
    ax.text(0.8, ax.get_ylim()[1] * 0.92, ' $0.8F$', color='black', fontsize=8)
    ax.text(1.2, ax.get_ylim()[1] * 0.92, ' $1.2F$', color='black', fontsize=8)
    ax.set_xlim(0.3, 2.0)
    ax.set_xlabel('$S_T/F$ at expiry'); ax.set_ylabel('Density (per unit of $S_T/F$)')
    ax.set_title(f"Bitcoin, expiry {pd.Timestamp(e).strftime('%d %b %Y')} ({f['days']:.0f} days)", fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch12_sem_b8_density')
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



# =============================================================================
# GRAFICE SUPLIMENTARE PENTRU SEMINAR (aceleasi cifre ca in functiile de mai sus)
# =============================================================================
def setup_check():
    """Verificarea datelor: S&P 500 si VIX imbinate pe zilele comune; lantul Deribit al cursului."""
    px = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    c = deribit_chain()
    return dict(n=int(len(px)), first=str(px.index[0].date()), last=str(px.index[-1].date()),
                sp0=float(px['sp500'].iloc[0]), vix0=float(px['vix'].iloc[0]), sp1=float(px['sp500'].iloc[-1]),
                vix1=float(px['vix'].iloc[-1]), n_opt=int(len(c)), n_exp=int(c['expiry'].nunique()),
                snap=str(c['snapshot_utc'].iloc[0]))


def a1_chart():
    """Densitatea implicita din tripletele de call-uri vecine (preturi de referinta in USD) pentru scadenta din A1."""
    c = deribit_chain()
    g = c[(c['expiry'] == pd.Timestamp(BFLY_EXPIRY)) & (c['type'] == 'call')].set_index('strike').sort_index()
    F, S = float(g['forward'].iloc[0]), float(g['index'].iloc[0])
    K = g.index.values.astype(float); C = g['mark_price'].values * S
    Km, qd = [], []
    for i in range(1, len(K) - 1):
        h1, h2 = K[i] - K[i - 1], K[i + 1] - K[i]
        d2 = 2 * (C[i - 1] / (h1 * (h1 + h2)) - C[i] / (h1 * h2) + C[i + 1] / (h2 * (h1 + h2)))
        Km.append(K[i]); qd.append(F / S * d2)
    Km, qd = np.array(Km), np.array(qd)
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.bar(Km / 1000, qd * 1e5, width=0.8, color=np.where(qd >= 0, MainBlue, IDAred))
    i85 = np.argmin(abs(Km - 85000))
    ax.bar([85], [qd[i85] * 1e5], width=0.8, color=Amber)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Strike $K$ (thousand USD)'); ax.set_ylabel('$e^{r\\tau}\\,\\partial^2 C/\\partial K^2$ ($10^{-5}$ per USD)')
    from matplotlib.patches import Patch
    fig_legend_bottom(fig, [Patch(color=MainBlue, label='Adjacent strikes, convex (density $\\geq 0$)'),
                            Patch(color=IDAred, label='Adjacent strikes, not convex at mark prices'),
                            Patch(color=Amber, label='The 84/85/86 thousand butterfly of the task')], ncol=1, y=-0.02)
    save_fig('ch12_sem_a1_butterfly')
    return dict(n_adj=int(len(qd)), n_adj_neg=int((qd < 0).sum()))


def a4_chart():
    """N x (C_N - C_BS) pentru arborele CRR, N par vs impar."""
    S, K, T, r, s = 100.0, 100.0, 1.0, 0.05, 0.20
    bs = float(bs_price(S, K, T, r, s))
    Ns = np.arange(20, 301)
    e = np.array([N * (float(crr_price(S, K, T, r, s, int(N))) - bs) for N in Ns])
    avg = np.array([N * (0.5 * (float(crr_price(S, K, T, r, s, int(N))) + float(crr_price(S, K, T, r, s, int(N) + 1))) - bs)
                    for N in Ns[Ns % 2 == 0]])
    fig, ax = plt.subplots(figsize=(6.6, 3.1))
    ax.plot(Ns[Ns % 2 == 0], e[Ns % 2 == 0], 'o', ms=2.5, color=MainBlue, label='Even $N$ (strike on a node)')
    ax.plot(Ns[Ns % 2 == 1], e[Ns % 2 == 1], 'o', ms=2.5, color=IDAred, label='Odd $N$ (strike between two nodes)')
    ax.plot(Ns[Ns % 2 == 0], avg, color=Forest, lw=1.2, label='Average of $N$ and $N + 1$')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Number of steps $N$'); ax.set_ylabel('$N\\,(C_N - C_{BS})$')
    legend_outside_bottom(ax, ncol=3, y=-0.22)
    save_fig('ch12_sem_a4_crr')
    return {}


def a5_chart():
    """Delta, gamma si vega ale call-ului din A5 in functie de S, cu punctul S = 100 marcat."""
    K, T, r, sg = 100.0, 0.5, 0.03, 0.25
    Sg = np.linspace(60, 140, 401)
    gk = bs_greeks(Sg, K, T, r, sg)
    g0 = bs_greeks(100.0, K, T, r, sg)
    fig, axes = plt.subplots(1, 3, figsize=(10, 2.9))
    for ax, key, lab, col in zip(axes, ['delta', 'gamma', 'vega'],
                                 ['Delta $\\Phi(d_1)$', 'Gamma $\\varphi(d_1)/(S\\sigma\\sqrt{\\tau})$',
                                  'Vega per vol point $S\\varphi(d_1)\\sqrt{\\tau}/100$'], [MainBlue, IDAred, Forest]):
        ax.plot(Sg, gk[key], color=col, lw=1.4)
        ax.plot([100], [float(g0[key])], 'o', color=Amber, ms=6)
        ax.annotate(f"{float(g0[key]):.4f}", (100, float(g0[key])), textcoords='offset points', xytext=(6, -12),
                    fontsize=8, color='black')
        ax.axvline(100, color=Gray, lw=0.6, ls=':')
        ax.set_title(lab, fontsize=9, loc='left'); ax.set_xlabel('$S$')
    from matplotlib.lines import Line2D
    fig_legend_bottom(fig, [Line2D([], [], color=MainBlue, label='Delta'), Line2D([], [], color=IDAred, label='Gamma'),
                            Line2D([], [], color=Forest, label='Vega'),
                            Line2D([], [], marker='o', ls='', color=Amber, label='The A5 option: $S = K = 100$, $\\tau = 0.5$')],
                      ncol=4, y=0.0)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch12_sem_a5_greeks')
    return {}


def a7_chart():
    """Pretul Black-Scholes ca functie de sigma, pretul de piata 4.50, valorile de pornire si pasul Newton."""
    S, K, T, r, P = 100.0, 100.0, 0.25, 0.02, 4.50
    sg = np.linspace(0.02, 0.40, 300)
    price = bs_price(S, K, T, r, sg)
    pvk = K * np.exp(-r * T)
    s_bs0 = P * np.sqrt(2 * np.pi) / (S * np.sqrt(T))
    s_bs1 = (P - (S - pvk) / 2) * np.sqrt(2 * np.pi) / (S * np.sqrt(T))
    s0 = 0.20
    p0 = float(bs_price(S, K, T, r, s0)); v0 = float(bs_greeks(S, K, T, r, s0)['vega']) * 100
    s1 = s0 - (p0 - P) / v0
    ex = implied_vol(P, S, K, T, r)
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.plot(100 * sg, price, color=MainBlue, lw=1.5, label='Black–Scholes price $BS(\\sigma)$')
    ax.axhline(P, color=Gray, lw=0.8, ls='--')
    ax.text(14.3, P + 0.08, 'market price 4.50', color='black', fontsize=8)
    tt = np.linspace(0.17, 0.25, 20)
    ax.plot(100 * tt, p0 + v0 * (tt - s0), color=IDAred, lw=1.2, label='Tangent at $\\sigma_0 = 20\\%$ (Newton step)')
    ax.plot([100 * s0], [p0], 'o', color=IDAred, ms=5)
    ax.plot([100 * s1], [P], 'o', color=Forest, ms=6, label=f'Newton $\\sigma_1 = {100 * s1:.2f}\\%$ (exact {100 * ex:.2f}%)')
    ax.plot([100 * s_bs0], [float(bs_price(S, K, T, r, s_bs0))], 's', color=Purple, ms=5,
            label=f'Start without correction {100 * s_bs0:.2f}%')
    ax.plot([100 * s_bs1], [float(bs_price(S, K, T, r, s_bs1))], 'D', color=Amber, ms=5,
            label=f'Start with correction {100 * s_bs1:.2f}%')
    ax.set_xlim(14, 28); ax.set_ylim(3, 6.2)
    ax.set_xlabel('Volatility $\\sigma$ (%)'); ax.set_ylabel('Call price')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch12_sem_a7_newton')
    return dict(s1=float(s1), s_bs0=float(s_bs0), s_bs1=float(s_bs1))


def a8_chart():
    """Integrandul benzii de varianta (log-normal, 90 de zile): dreptunghiurile Cboe pe [80, 120] si cozile trunchiate."""
    F, T, s = 100.0, 90 / 365, 0.20
    q = lambda K: np.where(K < F, bs_price(F, K, T, 0.0, s, 'put'), bs_price(F, K, T, 0.0, s, 'call'))
    Kd = np.linspace(50, 160, 2201)
    f = 2 / T * q(Kd) / Kd ** 2
    K5 = np.arange(80.0, 120.1, 5.0)
    Q5 = np.where(K5 == F, 0.5 * (bs_price(F, K5, T, 0.0, s, 'put') + bs_price(F, K5, T, 0.0, s, 'call')), q(K5))
    fig, ax = plt.subplots(figsize=(6.6, 3.1))
    ax.bar(K5, 2 / T * Q5 / K5 ** 2, width=5, color=Teal, alpha=0.45, edgecolor=MainBlue, lw=0.6,
           label='Cboe rectangles, $\\Delta K = 5$ on $[80, 120]$')
    ax.plot(Kd, f, color=MainBlue, lw=1.4, label='Integrand $2\\,Q(K)/(T K^2)$')
    ax.fill_between(Kd, 0, f, where=(Kd < 80) | (Kd > 120), color=IDAred, alpha=0.3, lw=0,
                    label='Truncated tails (outside $[80, 120]$)')
    ax.set_xlabel('Strike $K$'); ax.set_ylabel('Contribution to $\\sigma^2$ per unit of $K$')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch12_sem_a8_strip')
    return {}


def b2_chart():
    """P&L cumulat al vanzatorului de optiuni acoperite delta (S&P 500), cu cele mai rele cinci luni marcate."""
    d = delta_hedged_history()
    cum = d['pnl'].cumsum()
    w5 = d['pnl'].nsmallest(5)
    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    ax.plot(cum.index, cum, color=MainBlue, lw=1.3, label='Cumulative P&L of the seller (% of the index, summed)')
    ax.plot(w5.index, cum.loc[w5.index], 'o', color=IDAred, ms=6, label='The five worst months')
    for dt in w5.index:
        ax.annotate(f"{dt.strftime('%Y-%m')}: {w5[dt]:.2f}%", (dt, cum[dt]), textcoords='offset points', xytext=(-20, -14),
                    fontsize=7, color='black')
    ax.set_ylabel('Cumulative P&L (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch12_sem_b2_cum')
    return {}


def b4_chart():
    """Contributia fiecarui pret de exercitare la varianta implicita (formula Cboe), cele doua scadente din jurul a 30 de zile."""
    c = deribit_chain()
    t0 = c['snapshot_utc'].iloc[0]
    c = c.assign(T=(c['expiry'] - t0).dt.total_seconds() / (365 * 86400))
    exps = sorted(c['expiry'].unique())
    Td = {e: c.loc[c['expiry'] == e, 'T'].iloc[0] * 365 for e in exps}
    near = max(e for e in exps if Td[e] < 30); nxt = min(e for e in exps if Td[e] >= 30)
    fig, ax = plt.subplots(figsize=(6.6, 3.1))
    out = {}
    for tag, e, col in [('near', near, MainBlue), ('next', nxt, IDAred)]:
        g = c[c['expiry'] == e]
        F = float(g['forward'].iloc[0]); S = float(g['index'].iloc[0]); T = float(g['T'].iloc[0])
        K, Q, K0 = cboe_strip(g, F, S)
        dK = np.empty_like(K); dK[1:-1] = (K[2:] - K[:-2]) / 2; dK[0], dK[-1] = K[1] - K[0], K[-1] - K[-2]
        R = np.log(F / S) / T
        contrib = 2 / T * dK / K ** 2 * np.exp(R * T) * Q
        share = contrib / contrib.sum()
        ax.plot(K / F, 100 * share, 'o-', ms=3, lw=1.0, color=col,
                label=f"{pd.Timestamp(e).strftime('%d %b %Y')} ({T * 365:.0f} days, {len(K)} options)")
        out[tag] = dict(put_share=float(share[K < K0].sum()), atm_share=float(share[K == K0].sum()))
    ax.axvline(1, color=Gray, lw=0.6, ls=':')
    ax.set_xlabel('Strike / forward $K/F$'); ax.set_ylabel('Share of the strip variance (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch12_sem_b4_strip')
    return out


def b5_chart():
    """VRP zilnica S&P 500 in puncte de volatilitate, cu mediile pe subperioade si intervalele Newey-West de 95%."""
    d = vrp_sp500()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw={'width_ratios': [2.2, 1]})
    ax = axes[0]
    ax.plot(d.index, d['vrp_vol'], color=MainBlue, lw=0.4, label='Daily premium $VIX_t - \\sqrt{RV_{t,t+21}}$')
    for (a, b), col in [(('1990', '2007'), IDAred), (('2008', '2026'), Forest)]:
        x = d.loc[a:b, 'vrp_vol']
        m, se = nw_mean(x, 21)
        ax.hlines(m, x.index[0], x.index[-1], color=col, lw=2, label=f'Mean {a}–{b}: {m:.2f} (NW 95%: $\\pm${1.96 * se:.2f})')
        ax.fill_between([x.index[0], x.index[-1]], m - 1.96 * se, m + 1.96 * se, color=col, alpha=0.25, lw=0)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylim(-45, 30); ax.set_ylabel('Volatility points')
    legend_outside_bottom(ax, ncol=1, y=-0.12)
    ax = axes[1]
    m, se = nw_mean(d['vrp'], 21)
    naive = d['vrp'].std() / np.sqrt(len(d))
    ax.errorbar([0], [m], yerr=[[1.96 * naive], [1.96 * naive]], fmt='o', color=Amber, capsize=6, label='Naive $s/\\sqrt{n}$ interval')
    ax.errorbar([1], [m], yerr=[[1.96 * se], [1.96 * se]], fmt='o', color=Purple, capsize=6, label='Newey–West (21 lags) interval')
    ax.set_xlim(-0.8, 1.8); ax.set_xticks([0, 1]); ax.set_xticklabels(['naive', 'Newey–West'])
    ax.set_ylabel('Mean VRP (%$^2$), 95% interval')
    legend_outside_bottom(ax, ncol=1, y=-0.12)
    plt.tight_layout()
    save_fig('ch12_sem_b5_vrp')
    return {}


def b6_chart():
    """Elipsa de incredere comuna de 95% pentru (alpha, beta) in regresia Mincer-Zarnowitz, cu punctul (0, 1)."""
    d = vrp_sp500()
    m = sm.OLS(d['rv'], sm.add_constant(d[['iv2']])).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
    b = m.params.values; V = m.cov_params().values
    c2 = stats.chi2.ppf(0.95, 2)
    th = np.linspace(0, 2 * np.pi, 400)
    L = np.linalg.cholesky(V)
    ell = b[:, None] + np.sqrt(c2) * L @ np.vstack([np.cos(th), np.sin(th)])
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    ax.plot(ell[0], ell[1], color=MainBlue, lw=1.5, label='Joint 95% confidence ellipse (Wald, HAC 21 lags)')
    se = np.sqrt(np.diag(V))
    ax.axvspan(b[0] - 1.96 * se[0], b[0] + 1.96 * se[0], color=Teal, alpha=0.12, lw=0, label='Marginal 95% interval for $\\alpha$')
    ax.axhspan(b[1] - 1.96 * se[1], b[1] + 1.96 * se[1], color=Amber, alpha=0.15, lw=0, label='Marginal 95% interval for $\\beta$')
    ax.plot([b[0]], [b[1]], 'o', color=MainBlue, ms=5, label=f'Estimate ({b[0]:.1f}, {b[1]:.2f})')
    ax.plot([0], [1], '*', color=IDAred, ms=11, label='Unbiased forecast (0, 1)')
    ax.set_xlabel('Intercept $\\alpha$ (%$^2$)'); ax.set_ylabel('Slope $\\beta$')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch12_sem_b6_ellipse')
    return dict(corr=float(V[0, 1] / np.sqrt(V[0, 0] * V[1, 1])))


def b7_chart():
    """Prima Bitcoin zilnica (DVOL minus volatilitatea realizata pe 30 de zile), cu media si intervalul Newey-West."""
    d = vrp_btc()
    m, se = nw_mean(d['vrp_vol'], 30)
    s = vrp_sp500()
    ms_, ses = nw_mean(s['vrp_vol'], 21)
    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    ax.plot(d.index, d['vrp_vol'], color=Amber, lw=0.7, label='Bitcoin: DVOL$_t - \\sqrt{RV_{t,t+30}}$')
    ax.hlines(m, d.index[0], d.index[-1], color=MainBlue, lw=2, label=f'Bitcoin mean {m:.1f}, Newey–West 95% $\\pm${1.96 * se:.1f}')
    ax.fill_between([d.index[0], d.index[-1]], m - 1.96 * se, m + 1.96 * se, color=MainBlue, alpha=0.2, lw=0)
    ax.hlines(ms_, d.index[0], d.index[-1], color=Forest, lw=1.5, ls='--', label=f'S&P 500 mean premium 1990–2026: {ms_:.1f}')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel('Volatility points')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch12_sem_b7_btc')
    return {}

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
    RES['SETUP'] = setup_check()
    RES['CH'] = dict(a1=a1_chart(), a4=a4_chart(), a5=a5_chart(), a7=a7_chart(), a8=a8_chart(), b2=b2_chart(),
                     b4=b4_chart(), b5=b5_chart(), b6=b6_chart(), b7=b7_chart())
    with open(os.path.join(HERE, 'sem12_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved sem12_results.json')

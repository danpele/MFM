"""
Seminar 8: Backtesting and Evaluating Risk Forecasts -- computations for all problems
=========================================================================================
Part A: Kupiec, Christoffersen, Basel traffic light, FZ0, Z2 and the conformal quantile, step by step.
Part B: backtesting on the S&P 500, BET, Bitcoin and EUR/RON (BNR rate): VaR tests, ES tests with
simulation and bootstrap, Diebold-Mariano (HAC), MCS, conformal VaR in calm and crisis periods.
Part C: RON portfolio 50% BET + 50% EUR, rebalanced daily (reference analysis for the instructor).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_data as M              # noqa: E402
import generate_all_charts as g   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# PART A
# =============================================================================
def a1_kupiec(T=250, x=7, p=0.01):
    """Kupiec step by step."""
    ph = x / T
    l0 = (T - x) * np.log(1 - p) + x * np.log(p)
    l1 = (T - x) * np.log(1 - ph) + x * np.log(ph)
    lr = -2 * (l0 - l1)
    return dict(T=T, x=x, p=p, ph=ph, l0=l0, l1=l1, LR=lr, pval=stats.chi2.sf(lr, 1),
                exact=float(stats.binom.sf(x - 1, T, p)), expected=T * p)


def a3_counts(name, model, a='2007', b='2010', p=0.01):
    h = g.hits(name, model).loc[a:b]
    c = M.transitions(h.values)
    return dict(**c, **M.christoffersen_from_counts(**c, p=p), T=len(h))


def a5_traffic(T=250, p=0.01):
    cum = [float(stats.binom.cdf(k, T, p)) for k in range(0, 13)]
    return dict(cum=cum, green_max=int(np.max(np.flatnonzero(np.array(cum) < 0.95))),
                red_min=int(np.min(np.flatnonzero(np.array(cum) >= 0.9999))), p97=float(stats.binom.cdf(5, T, 0.03)))


A6_L = np.array([0.8, -1.1, 3.4, 2.3, -0.5])          # losses (%) on five days
A6_FC = {'A': (2.0, 2.6), 'B': (2.6, 3.4), 'C': (2.0, 4.0)}   # (VaR 2.5%, ES 2.5%), in %


def a6_fz0(a=0.025):
    out = {}
    for k, (v, e) in A6_FC.items():
        terms = M.fz0(A6_L, v, e, a)
        out[k] = dict(VaR=v, ES=e, terms=[float(t) for t in terms], mean=float(terms.mean()),
                      const=float(v / e + np.log(e) - 1), hit=[int(l > v) for l in A6_L])
    return out


A7_L = np.array([3.9, 2.8, 4.6, 3.1, 5.2, 2.9, 3.6, 7.4])      # losses (%) on the breach days
A7_ES = np.array([3.4, 3.3, 3.6, 3.2, 3.5, 3.3, 3.4, 3.8])      # ES forecast (%) on those days


def a7_z2(T=250, a=0.025):
    r = A7_L / A7_ES
    z2 = 1 - r.sum() / (T * a)
    z1 = 1 - r.mean()
    return dict(ratios=[float(x) for x in r], sum=float(r.sum()), Z2=float(z2), Z1=float(z1), n=len(r), Ta=T * a)


A8_S = np.array([1.12, 0.35, 2.41, 0.88, 1.95, 0.52, 3.10, 1.47, 0.73, 2.02,
                 0.19, 1.66, 2.75, 0.94, 1.28, 0.61, 1.83, 2.28, 1.05])   # 19 calibration scores
A8_SD = 1.4          # standard deviation (%) forecast for the next day


def a8_conformal(a=0.10, gamma=0.02):
    n = len(A8_S)
    k = int(np.ceil((n + 1) * (1 - a)))
    s = np.sort(A8_S)
    q = s[k - 1]
    a_next_hit = a + gamma * (a - 1)
    a_next_nohit = a + gamma * a
    k_hit = int(np.ceil((n + 1) * (1 - a_next_hit)))
    return dict(n=n, k=k, q=float(q), VaR=float(A8_SD * q), sorted=[float(x) for x in s],
                a_hit=a_next_hit, a_nohit=a_next_nohit, k_hit=k_hit, q_hit=float(s[min(k_hit, n) - 1]) if k_hit <= n else None,
                k_nohit=int(np.ceil((n + 1) * (1 - a_next_nohit))))


# --- derivations (Part A, master level) ---
def a1_pof_power(T=250, pi=0.02, a=0.01):
    """Local (noncentral chi2) and exact (Binomial) power of the 5% Kupiec test; exact size."""
    lam = T * (pi - a) ** 2 / (a * (1 - a))
    crit = stats.chi2.ppf(0.95, 1)
    ex, asy, rej = g.pof_power(T, np.array([pi, a]), a)
    return dict(T=T, pi=pi, a=a, lam=float(lam), asym=float(stats.ncx2.sf(crit, 1, lam)), exact=float(ex[0]),
                size=float(ex[1]), accept=[int(k) for k in np.flatnonzero(~rej)[[0, -1]]])


def a2_days_for_power(pi=0.05, a=0.025, power=0.80):
    """Number of days for a given power: from lambda* (asymptotic) and by exact search."""
    from scipy.optimize import brentq
    crit = stats.chi2.ppf(0.95, 1)
    lam = brentq(lambda l: stats.ncx2.sf(crit, 1, l) - power, 0.1, 50)
    T_asy = lam * a * (1 - a) / (pi - a) ** 2
    T_ex = next(T for T in range(20, 2000) if g.pof_power(T, np.array([pi]), a)[0][0] >= power)
    return dict(lam=float(lam), T_asy=float(T_asy), T_exact=int(T_ex))


def a4_dq_constant(T=250, x=7, a=0.01):
    """DQ with X_t = 1: score form (Wald with the null variance) of the Kupiec test, versus LR."""
    ph = x / T
    dq = T * (ph - a) ** 2 / (a * (1 - a))
    k = a1_kupiec(T, x, a)
    return dict(DQ=float(dq), p=float(stats.chi2.sf(dq, 1)), LR=float(k['LR']), p_LR=float(k['pval']))


def a6_consistency(nu=4, a=0.025, n=1_000_000, seed=5):
    """Numerical check: minimisers of the average pinball and FZ0 losses on unit-variance t(nu) losses."""
    from scipy.optimize import minimize, minimize_scalar
    rng = np.random.default_rng(seed)
    L = rng.standard_t(nu, n) * np.sqrt((nu - 2) / nu)
    v_pin = minimize_scalar(lambda v: M.pinball(L, v, a).mean(), bounds=(0.5, 5), method='bounded').x
    r = minimize(lambda p: M.fz0(L, p[0], p[1], a).mean() if p[1] >= p[0] > 0 else 1e9, [2.0, 2.5],
                 method='Nelder-Mead', options=dict(xatol=1e-5, fatol=1e-9))
    return dict(v_pin=float(v_pin), v_fz=float(r.x[0]), e_fz=float(r.x[1]),
                VaR=float(M.t_std_q(nu, a)), ES=float(M.t_std_es(nu, a)))


def es_discrete(vals, probs, a):
    """ES at tail probability a for a discrete loss distribution."""
    o = np.argsort(vals)[::-1]
    v, p = np.asarray(vals, float)[o], np.asarray(probs, float)[o]
    take = np.minimum(p, np.maximum(a - np.r_[0, np.cumsum(p)[:-1]], 0))
    return float((v * take).sum() / a)


def a9_es_not_elicitable(a=0.025):
    """Two distributions with the same ES whose mixture has a different ES: level sets are not convex."""
    F0 = ([1.0], [1.0])
    F1 = ([2.0, 0.0], [a / 2, 1 - a / 2])
    mix = ([2.0, 1.0, 0.0], [a / 4, 0.5, 0.5 - a / 4])
    return dict(es0=es_discrete(*F0, a), es1=es_discrete(*F1, a), es_mix=es_discrete(*mix, a))


def a10_de_moments(a=0.025, n=4_000_000, seed=6, T=250):
    """Moments of the cumulative violation H = (u - (1 - a))/a 1{u > 1 - a} under H0 (u uniform)."""
    u = np.random.default_rng(seed).uniform(size=n)
    H = (u - (1 - a)) / a * (u > 1 - a)
    return dict(mean=float(H.mean()), var=float(H.var()), mean_th=a / 2, var_th=a * (1 / 3 - a / 4),
                se_T=float(np.sqrt(a * (1 / 3 - a / 4) / T)))


def part_a_extras():
    return dict(a1p=a1_pof_power(), a2p=a1_pof_power(250, 0.05, 0.025), a2T=a2_days_for_power(),
                a4dq=a4_dq_constant(), a6c=a6_consistency(), a9=a9_es_not_elicitable(), a10=a10_de_moments())


def part_a():
    return dict(a1=a1_kupiec(), a2=a1_kupiec(250, 11, 0.025), a3=a3_counts('bet', 'HS'), a4=a3_counts('bet', 'GARCH-t'),
                a5=a5_traffic(), a6=a6_fz0(), a7=a7_z2(), a8=a8_conformal())


# =============================================================================
# PART B
# =============================================================================
def b1_sp500_var():
    """VaR 1% tests on the S&P 500; asymptotic versus exact (Binomial) p-value."""
    out = {}
    for m in M.MODELS:
        h = g.hits('sp500', m).values
        k, c, d = M.kupiec(h, 0.01), M.christoffersen(h, 0.01), M.duration_test(h)
        exact = 2 * min(stats.binom.cdf(k['x'], k['T'], 0.01), stats.binom.sf(k['x'] - 1, k['T'], 0.01))
        out[m] = dict(x=k['x'], T=k['T'], rate=k['rate'], p_uc=k['p'], p_exact=float(min(exact, 1)),
                      p_ind=c['p_ind'], p_cc=c['p_cc'], b=d['b'], p_dur=d['p'])
    # small sample: one year (2008) for GARCH-t
    h = g.hits('sp500', 'GARCH-t').loc['2008'].values
    k = M.kupiec(h, 0.01)
    out['small'] = dict(T=k['T'], x=k['x'], p_asy=k['p'],
                        p_exact=float(min(1, 2 * min(stats.binom.cdf(k['x'], k['T'], 0.01),
                                                     stats.binom.sf(k['x'] - 1, k['T'], 0.01)))))
    return out


def b2_traffic_bet():
    """Basel traffic light for the GARCH-t VaR 1% on the BET: last 250 days and share of time in each zone."""
    x = g.rolling_exceptions('bet', 'GARCH-t')
    last = int(x.iloc[-1])
    zone, cum = M.traffic_light(last)
    mult = {0: 1.5, 1: 1.5, 2: 1.5, 3: 1.5, 4: 1.5, 5: 1.7, 6: 1.76, 7: 1.83, 8: 1.88, 9: 1.92}.get(last, 2.0)
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    ax.axhspan(-0.5, 4.5, color=g.Forest, alpha=0.10, lw=0)
    ax.axhspan(4.5, 9.5, color='#F1C40F', alpha=0.15, lw=0)
    ax.axhspan(9.5, 30, color=g.IDAred, alpha=0.10, lw=0)
    for m in ('HS', 'GARCH-t', 'GARCH-EVT'):
        xm = g.rolling_exceptions('bet', m)
        ax.plot(xm.index, xm, color=g.MCOL[m], lw=0.9, label=m)
    ax.set_ylim(-0.5, 26)
    ax.set_ylabel('Exceptions of VaR 1%\nin the last 250 days (BET)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.13)
    g.save_fig('ch8_sem_traffic_bet')
    h = g.hits('bet', 'GARCH-t')
    return dict(last=last, zone=zone, cum=cum, mult=mult, window=[str(h.index[-250].date()), str(h.index[-1].date())],
                share_green=float(np.mean(x <= 4)), share_yellow=float(np.mean((x >= 5) & (x <= 9))),
                share_red=float(np.mean(x >= 10)), max=int(x.max()), max_day=str(x.idxmax().date()),
                x975=int(g.hits('bet', 'GARCH-t', 'VaR2.5').iloc[-250:].sum()))


def z2_null(name, model, M_sim=5000, seed=11, last=None):
    """Simulated distribution of Z2 under H0 (the model's forecast distribution)."""
    F, tails = g.fc(name)
    df = F[model]
    tl = {k: v for k, v in tails.items()}
    if last:
        df = df.iloc[-last:]
        tl = {k: v[-last:] for k, v in tails.items()}
    L, var, es = df['L'].values, df['VaR2.5'].values, df['ES2.5'].values
    z1, z2 = M.acerbi_szekely(L, var, es)
    rng = np.random.default_rng(seed)
    T = len(L)
    sims = []
    for m0 in range(0, M_sim, 500):
        U = rng.uniform(size=(T, min(500, M_sim - m0)))
        hit = U > 1 - M.A_ES
        Ls = M.tail_sampler(df, model, tl, np.where(hit, U, 1 - M.A_ES / 2))
        sims.append(1 - np.where(hit, Ls / es[:, None], 0).sum(0) / (T * M.A_ES))
    sims = np.concatenate(sims)
    return dict(Z1=float(z1), Z2=float(z2), p=float(np.mean(sims <= z2)), crit5=float(np.quantile(sims, 0.05)),
                crit01=float(np.quantile(sims, 0.0001)), T=T, n_hit=int((L > var).sum()), sims=sims)


def b3_es_sp500():
    out = {}
    for m in ('GARCH-t', 'FHS', 'HS'):
        df = g.fc('sp500')[0][m]
        mf = M.mcneil_frey(df['L'].values, df['VaR2.5'].values, df['ES2.5'].values, df['scale'].values)
        z = z2_null('sp500', m)
        zl = z2_null('sp500', m, last=250)
        out[m] = dict(MF_n=mf['n'], MF_mean=mf['mean'], MF_t=mf['t'], MF_p=mf['p'],
                      MF_p_normal=float(stats.t.sf(mf['t'], mf['n'] - 1)),
                      Z1=z['Z1'], Z2=z['Z2'], p2=z['p'], crit5=z['crit5'], T=z['T'],
                      Z2_last=zl['Z2'], p2_last=zl['p'], crit5_last=zl['crit5'], n_last=zl['n_hit'])
        if m == 'GARCH-t':
            fig, ax = plt.subplots(figsize=(6.4, 2.9))
            ax.hist(zl['sims'], bins=60, color=g.MainBlue, alpha=0.45, edgecolor='white', label='Simulated $Z_2$ under H0 (5000 simulations)')
            ax.axvline(zl['Z2'], color=g.IDAred, lw=1.4, label=f'Observed $Z_2$ = {zl["Z2"]:.2f}')
            ax.axvline(zl['crit5'], color=g.Amber, ls='--', lw=1.0, label=f'Simulated 5% critical value = {zl["crit5"]:.2f}')
            ax.axvline(-0.70, color='black', ls=':', lw=1.0, label='Acerbi-Szekely fixed threshold -0.70')
            ax.set_xlabel(r'$Z_2$, GARCH-t, S&P 500, last 250 days')
            ax.set_ylabel('Frequency')
            g.legend_outside_bottom(ax, ncol=2, y=-0.2)
            g.save_fig('ch8_sem_z2_sim')
    return out


def b4_z2_bet_btc():
    out = {}
    for n in ('bet', 'btc'):
        for m in ('GARCH-t', 'GARCH-EVT'):
            z = z2_null(n, m)
            zl = z2_null(n, m, last=250)
            out[f'{n}|{m}'] = dict(Z2=z['Z2'], p=z['p'], crit5=z['crit5'], n_hit=z['n_hit'], T=z['T'],
                                   Z2_last=zl['Z2'], p_last=zl['p'], crit5_last=zl['crit5'], n_last=zl['n_hit'])
    return out


def b5_dm_sp500():
    Lf = g.fz_losses('sp500')
    out = {}
    for a, b in (('GARCH-t', 'FHS'), ('HS', 'FHS'), ('GARCH-EVT', 'FHS')):
        d = Lf[a] - Lf[b]
        dm = M.diebold_mariano(Lf[a], Lf[b])
        naive = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
        out[f'{a}|{b}'] = dict(dbar=float(d.mean()), DM=dm['DM'], p=dm['p'], naive=float(naive),
                               lrv_ratio=float(M.nw_var(d.values) / d.var()))
    out['mean'] = {m: float(v) for m, v in Lf.mean().items()}
    out['T'] = len(Lf)
    out['lags'] = int(np.floor(4 * (len(Lf) / 100) ** (2 / 9)))
    return out


def b6_dm_btc_eurron():
    out = {}
    for n in ('btc', 'eurron'):
        Lf = g.fz_losses(n)
        best = Lf.mean().idxmin()
        out[n] = dict(best=best, mean={m: float(v) for m, v in Lf.mean().items()},
                      dm={m: M.diebold_mariano(Lf[m], Lf[best])['DM'] for m in M.MODELS if m != best},
                      p={m: M.diebold_mariano(Lf[m], Lf[best])['p'] for m in M.MODELS if m != best},
                      mcs={m: float(v) for m, v in M.mcs(Lf).items()})
    return out


def b7_conformal_sp500():
    out = {}
    for a in (0.05, 0.01):
        r = M.load_returns('sp500')
        c = M.conformal_var(r, a=a).loc[g.fc('sp500')[0]['HS'].index[0]:]
        reg = M.regimes(r, c.index)
        hs = c['L'] > c['VaR_split']
        # simulation: same procedure on i.i.d. Student-t returns (exchangeable returns; rolling scores only approximately)
        rng = np.random.default_rng(5)
        x = pd.Series(rng.standard_t(4, len(r)) * 0.01, index=r.index)
        ci = M.conformal_var(x, a=a).loc[c.index[0]:]
        regi = M.regimes(x, ci.index)
        hi = ci['L'] > ci['VaR_split']
        out[str(a)] = dict(T=len(c), rate=float(hs.mean()), calm=float(hs[~reg].mean()), crisis=float(hs[reg].mean()),
                           kup=M.kupiec(hs.values, a)['p'], iid_rate=float(hi.mean()), iid_calm=float(hi[~regi].mean()),
                           iid_crisis=float(hi[regi].mean()), n_crisis=int(reg.sum()),
                           ind=M.christoffersen(hs.values, a)['p_ind'], ind_iid=M.christoffersen(hi.values, a)['p_ind'])
    return out


def b8_conformal_bet_btc():
    out = {}
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.8), sharey=True)
    for ax, n in zip(axs, ('bet', 'btc')):
        r = M.load_returns(n)
        c = M.conformal_var(r, a=0.05).loc[g.fc(n)[0]['HS'].index[0]:]
        reg = M.regimes(r, c.index)
        res = {}
        for k in ('split', 'aci'):
            h = c['L'] > c['VaR_' + k]
            res[k] = [float(h.mean()), float(h[~reg].mean()), float(h[reg].mean())]
        gg = g.fc(n)[0]['GARCH-t'].reindex(c.index)
        hg = gg['L'] > gg['VaR5']
        res['garch'] = [float(hg.mean()), float(hg[~reg].mean()), float(hg[reg].mean())]
        out[n] = res
        for j, (k, col, lab) in enumerate((('split', g.MainBlue, 'Split conformal'), ('aci', g.IDAred, 'ACI'),
                                           ('garch', g.Forest, 'GARCH-t'))):
            ax.bar(np.arange(3) + (j - 1) * 0.26, 100 * np.array(res[k]), 0.26, color=col, label=lab)
        ax.axhline(5, color='black', ls='--', lw=0.8, label='Nominal 5%')
        ax.set_xticks(range(3), ['All days', 'Calm', 'Crisis'])
        ax.set_title(M.LABELS[n], fontsize=9)
    axs[0].set_ylabel('Breach rate of VaR 5% (%)')
    axs[0].legend(loc='upper center', bbox_to_anchor=(1.05, -0.12), ncol=4, frameon=False)
    g.save_fig('ch8_sem_conformal')
    return out


# =============================================================================
# PART C: RON portfolio 50% BET + 50% EUR
# =============================================================================
def portfolio_returns():
    """RON position: half in the BET index, half in euro (valued in lei at the BNR rate), rebalanced daily.
    Join PRICES on common days, then simple returns, then the portfolio log return."""
    P = pd.concat([M.load_price('bet').rename('BET'), M.load_price('eurron').rename('EUR')], axis=1, join='inner').dropna()
    R = P.pct_change().dropna()
    rp = np.log1p(0.5 * R['BET'] + 0.5 * R['EUR'])
    return rp


def part_c():
    rp = portfolio_returns()
    F, tails = M.rolling_forecasts(rp)
    out = {'start': str(F['HS'].index[0].date()), 'end': str(F['HS'].index[-1].date()), 'T': len(F['HS'])}
    rows = {}
    fz = {}
    for m in M.MODELS:
        df = F[m]
        h = (df['L'] > df['VaR1']).astype(int)
        h975 = (df['L'] > df['VaR2.5']).astype(int)
        k, c, d = M.kupiec(h.values, 0.01), M.christoffersen(h.values, 0.01), M.duration_test(h.values)
        z = M.z_pvalues(df, m, tails, M=2000)
        x250 = h.rolling(250).sum().dropna()
        fz[m] = M.fz0(df['L'].values, df['VaR2.5'].values, df['ES2.5'].values)
        rows[m] = dict(rate=k['rate'], p_uc=k['p'], p_cc=c['p_cc'], p_dur=d['p'], Z2=z['Z2'], p2=z['p2'],
                       last99=int(h.iloc[-250:].sum()), last975=int(h975.iloc[-250:].sum()),
                       share_red=float(np.mean(x250 >= 10)), max250=int(x250.max()), FZ=float(fz[m].mean()))
    Lf = pd.DataFrame(fz, index=F['HS'].index)
    mc = M.mcs(Lf)
    for m in M.MODELS:
        rows[m]['mcs'] = float(mc[m])
    out['rows'] = rows
    # chart: VaR 1% of FHS and HS on the portfolio
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    L = F['HS']['L']
    ax.plot(L.index, 100 * L, color=g.Orange, lw=0.5, alpha=0.6, label='Daily loss, 50% BET + 50% EUR (RON)')
    for m in ('HS', 'FHS', 'GARCH-EVT'):
        ax.plot(L.index, 100 * F[m]['VaR1'], color=g.MCOL[m], lw=0.8, label=f'VaR 1%, {m}')
    ax.set_ylabel('Loss (%)')
    ax.set_ylim(-3, 9)
    g.legend_outside_bottom(ax, ncol=2, y=-0.13)
    g.save_fig('ch8_sem_partc')
    out['vol'] = float(rp.std() * np.sqrt(252))
    return out


# --- Part B: additional inference ---
def b1_dq_sp500():
    """DQ test (Engle & Manganelli, 2004) for the six VaR 1% models on the S&P 500."""
    F = g.fc('sp500')[0]
    return {m: g.dq_test((F[m]['L'] > F[m]['VaR1']).astype(int).values, F[m]['VaR1'].values, 0.01) for m in M.MODELS}


def b5_gw_sp500():
    """Conditional Giacomini-White test on the FZ0 differentials against FHS."""
    Lf = g.fz_losses('sp500')
    return {f'{a}|FHS': g.gw_test(Lf[a], Lf['FHS']) for a in ('GARCH-t', 'HS', 'GARCH-EVT')}


def b6_murphy_btc():
    """Murphy diagram on Bitcoin, VaR 2.5%: HS versus GARCH-EVT (elementary scores)."""
    return g.murphy_summary('btc', 'HS', 'GARCH-EVT', 'VaR2.5', 0.025)


def b9_estimation_risk(reps=400):
    """Parametric bootstrap under estimation risk: GARCH-t re-estimated on every simulated path."""
    return g.mc_estimation_risk(reps=reps)


def part_b_extras():
    return dict(b1dq=b1_dq_sp500(), b5gw=b5_gw_sp500(), b6mu=b6_murphy_btc(), b9=b9_estimation_risk())


def run_all():
    R = dict(A=part_a(), AX=part_a_extras(), BX=part_b_extras(), b1=b1_sp500_var(), b2=b2_traffic_bet(), b3=b3_es_sp500(), b4=b4_z2_bet_btc(),
             b5=b5_dm_sp500(), b6=b6_dm_btc_eurron(), b7=b7_conformal_sp500(), b8=b8_conformal_bet_btc(), C=part_c())
    return R


# =============================================================================
# CHARTS AND WORKED NUMBERS FOR THE SEMINAR SOLUTIONS (python3 seminar8.py --charts)
# Every solution of a Part B exercise, and every Part A solution, has at least one chart.
# Results: key 'CH' of sem8_results.json.
# =============================================================================
def _bars_legend(fig, axs, ncol=4, y=0.0):
    hs, ls = [], []
    for ax in np.atleast_1d(axs):
        h, l = ax.get_legend_handles_labels()
        for hh, ll in zip(h, l):
            if ll not in ls:
                hs.append(hh)
                ls.append(ll)
    fig.legend(hs, ls, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def ch_setup():
    """Expected output of the setup cell: first rows of the S&P 500 GARCH-t forecast panel."""
    df = g.fc('sp500')[0]['GARCH-t']
    rows = [dict(date=str(d.date()), L=float(r['L']), VaR1=float(r['VaR1']), VaR25=float(r['VaR2.5']),
                 ES25=float(r['ES2.5']), scale=float(r['scale'])) for d, r in df.head(3).iterrows()]
    return dict(rows=rows, T=len(df), start=str(df.index[0].date()), end=str(df.index[-1].date()),
                T_bet=len(g.fc('bet')[0]['HS']), T_btc=len(g.fc('btc')[0]['HS']), T_eur=len(g.fc('eurron')[0]['HS']),
                start_btc=str(g.fc('btc')[0]['HS'].index[0].date()), start_eur=str(g.fc('eurron')[0]['HS'].index[0].date()),
                start_bet=str(g.fc('bet')[0]['HS'].index[0].date()))


def ch_a1():
    """A1: Binomial probabilities under the null (1%) and the alternative (2%), LR rejection region; power curves."""
    T, a = 250, 0.01
    xs = np.arange(0, 13)
    ex, asy, rej = g.pof_power(T, np.array([0.02, a]), a)
    pis = np.linspace(0.0, 0.04, 161)
    exc, asyc, _ = g.pof_power(T, pis, a)
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.8))
    ax = axs[0]
    for x in xs[rej[:13]]:
        ax.axvspan(x - 0.5, x + 0.5, color=g.IDAred, alpha=0.08, lw=0)
    ax.bar(xs - 0.2, stats.binom.pmf(xs, T, a), 0.4, color=g.MainBlue, label='P(x), correct model, π = 1%')
    ax.bar(xs + 0.2, stats.binom.pmf(xs, T, 0.02), 0.4, color=g.IDAred, label='P(x), true π = 2%')
    ax.set_xticks(xs)
    ax.set_xlabel('Breaches x in T = 250 days (shaded: LR rejects at 5%)')
    ax.set_ylabel('Probability')
    ax = axs[1]
    ax.plot(100 * pis, exc, color=g.MainBlue, lw=1.4, label='Exact rejection probability')
    ax.plot(100 * pis, asyc, color=g.Orange, lw=1.2, ls='--', label='Local asymptotic power')
    ax.axhline(0.05, color=g.Gray, lw=0.7, ls=':')
    ax.plot([1, 2, 2], [ex[1], ex[0], asy[0]], 'o', color='black', ms=3.5)
    ax.annotate(f'size {100 * ex[1]:.1f}%', (1, ex[1]), xytext=(1.15, 0.22), fontsize=7.5, color='black',
                arrowprops=dict(arrowstyle='-', lw=0.6, color='black'))
    ax.annotate(f'exact {100 * ex[0]:.0f}%', (2, ex[0]), xytext=(2.35, 0.12), fontsize=7.5, color='black',
                arrowprops=dict(arrowstyle='-', lw=0.6, color='black'))
    ax.annotate(f'local {100 * asy[0]:.0f}%', (2, asy[0]), xytext=(2.35, 0.45), fontsize=7.5, color='black',
                arrowprops=dict(arrowstyle='-', lw=0.6, color='black'))
    ax.set_xlabel('True breach probability π (%)')
    ax.set_ylabel('Rejection probability, T = 250')
    ax.set_ylim(0, 1.02)
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=4)
    g.save_fig('ch8_sem_a1_power')
    return dict(p0=float(stats.binom.pmf(0, T, a)), p7=float(stats.binom.sf(6, T, a)),
                pmf7_0=float(stats.binom.pmf(7, T, a)), pmf7_1=float(stats.binom.pmf(7, T, 0.02)))


def ch_a2():
    """A2: exact power against the sample size T (VaR 2.5%, true rate 5%); first 80% crossing."""
    a, pi = 0.025, 0.05
    Ts = np.arange(100, 701)
    ex = np.array([g.pof_power(T, np.array([pi]), a)[0][0] for T in Ts])
    lam = Ts * (pi - a) ** 2 / (a * (1 - a))
    asy = stats.ncx2.sf(stats.chi2.ppf(0.95, 1), 1, lam)
    first = int(Ts[np.argmax(ex >= 0.8)])
    below_after = Ts[(Ts > first) & (ex < 0.8)]
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    ax.plot(Ts, ex, color=g.MainBlue, lw=1.0, label='Exact power (Binomial, LR rule at 5%)')
    ax.plot(Ts, asy, color=g.Orange, lw=1.2, ls='--', label='Local asymptotic power')
    ax.axhline(0.8, color=g.Gray, lw=0.7, ls=':')
    ax.axvline(first, color=g.IDAred, lw=0.9, ls='--', label=f'First exact crossing of 80%: T = {first}')
    T_asy = int(np.ceil(Ts[np.argmax(asy >= 0.8)]))
    ax.axvline(T_asy, color=g.Forest, lw=0.9, ls='--', label=f'Asymptotic 80%: T = {T_asy}')
    ax.set_xlabel('Number of days T')
    ax.set_ylabel('Power against π = 5%')
    g.legend_outside_bottom(ax, ncol=2, y=-0.2)
    g.save_fig('ch8_sem_a2_power')
    return dict(first=first, T_asy=T_asy, n_below_after=int(len(below_after)),
                last_below=int(below_after.max()) if len(below_after) else None,
                pow_first=float(ex[Ts == first][0]), pow_prev=float(ex[Ts == first - 1][0]))


A3_SEQ = [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0]      # short teaching sequence for A3


def ch_a3():
    """A3: BET, HS VaR 1% in 2007-2010: losses, VaR and breaches; breach probability after a calm day and after a breach."""
    F = g.fc('bet')[0]['HS'].loc['2007':'2010']
    h = (F['L'] > F['VaR1'])
    c = M.transitions(h.astype(int).values)
    toy = M.transitions(A3_SEQ)
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8), gridspec_kw=dict(width_ratios=[2.6, 1]))
    ax = axs[0]
    ax.plot(F.index, 100 * F['L'], color=g.Orange, lw=0.5, label='Daily loss, BET')
    ax.plot(F.index, 100 * F['VaR1'], color=g.Teal, lw=1.1, label='HS VaR 1% (1000 days)')
    ax.plot(F.index[h], 100 * F['L'][h], 'o', color=g.IDAred, ms=3, label=f'Breach ({int(h.sum())} days)')
    ax.set_ylabel('Loss (%)')
    ax.set_ylim(-8, 14)
    ax = axs[1]
    p01, p11 = c['n01'] / (c['n00'] + c['n01']), c['n11'] / (c['n10'] + c['n11'])
    ax.bar([0], [100 * p01], 0.6, color=g.MainBlue, label=f'After no breach: {c["n01"]}/{c["n00"] + c["n01"]}')
    ax.bar([1], [100 * p11], 0.6, color=g.IDAred, label=f'After a breach: {c["n11"]}/{c["n10"] + c["n11"]}')
    ax.axhline(1.0, color='black', ls='--', lw=0.8, label='Target 1%')
    ax.set_xticks([0, 1], [r'$\hat\pi_{01}$', r'$\hat\pi_{11}$'])
    ax.set_ylabel('Breach probability (%)')
    for x, v in ((0, p01), (1, p11)):
        ax.text(x, 100 * v + 0.3, f'{100 * v:.1f}%', ha='center', fontsize=8, color='black')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=3)
    g.save_fig('ch8_sem_a3_bet')
    return dict(toy=toy, toy_seq=A3_SEQ, nb=int(h.sum()), start=str(F.index[0].date()), end=str(F.index[-1].date()))


def ch_a4():
    """A4: LR_uc and the intercept-only DQ (score form) against the number of breaches, T = 250, alpha = 1%."""
    T, a = 250, 0.01
    xs = np.arange(0, 16)
    lr = np.array([M.kupiec(np.r_[np.ones(x), np.zeros(T - x)], a)['LR'] for x in xs])
    dq = T * (xs / T - a) ** 2 / (a * (1 - a))
    c = stats.chi2.ppf(0.95, 1)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.plot(xs, lr, 'o-', color=g.MainBlue, ms=3.5, lw=1.1, label=r'LR$_{uc}$ (likelihood ratio)')
    ax.plot(xs, dq, 's-', color=g.Orange, ms=3.5, lw=1.1, label='DQ with a constant only (score form)')
    ax.axhline(c, color='black', ls='--', lw=0.8, label='5% critical value 3.84')
    ax.axvline(7, color=g.IDAred, lw=0.8, ls=':', label='x = 7')
    ax.set_xlabel('Breaches x in T = 250 days')
    ax.set_ylabel('Statistic')
    ax.set_ylim(0, 25)
    ax.set_xticks(xs)
    g.legend_outside_bottom(ax, ncol=2, y=-0.2)
    g.save_fig('ch8_sem_a4_dq')
    acc_lr = xs[lr <= c]
    acc_dq = xs[dq <= c]
    return dict(acc_lr=[int(acc_lr.min()), int(acc_lr.max())], acc_dq=[int(acc_dq.min()), int(acc_dq.max())],
                dq0=float(dq[0]), lr0=float(lr[0]), dq6=float(dq[6]), lr6=float(lr[6]))


def ch_a5():
    """A5: Binomial(250, p) cumulative probabilities, p = 1% and 3%, with the Basel zone cut-offs."""
    T = 250
    xs = np.arange(0, 16)
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    ax.axvspan(-0.5, 4.5, color=g.Forest, alpha=0.10, lw=0)
    ax.axvspan(4.5, 9.5, color='#F1C40F', alpha=0.15, lw=0)
    ax.axvspan(9.5, 15.5, color=g.IDAred, alpha=0.10, lw=0)
    ax.step(xs, stats.binom.cdf(xs, T, 0.01), where='mid', color=g.MainBlue, lw=1.4, label='P(X ≤ x), correct model, α = 1%')
    ax.step(xs, stats.binom.cdf(xs, T, 0.03), where='mid', color=g.IDAred, lw=1.4, label='P(X ≤ x), true π = 3%')
    ax.axhline(0.95, color='black', ls='--', lw=0.8, label='95% (yellow from here)')
    ax.axhline(0.9999, color='black', ls=':', lw=0.9, label='99.99% (red from here)')
    ax.set_xticks(xs)
    ax.set_xlabel('Exceptions x in 250 days (background: green, yellow, red zone)')
    ax.set_ylabel('Cumulative probability')
    g.legend_outside_bottom(ax, ncol=2, y=-0.2)
    g.save_fig('ch8_sem_a5_zones')
    return dict(cdf={int(x): float(stats.binom.cdf(x, T, 0.01)) for x in range(0, 12)})


def ch_a6(ax6=None, nu=4, a=0.025, n=1_000_000, seed=5):
    """A6: expected pinball loss against v and the expected FZ0 loss over (v, e), same draws as a6_consistency."""
    rng = np.random.default_rng(seed)
    L = rng.standard_t(nu, n) * np.sqrt((nu - 2) / nu)
    vq, eq = M.t_std_q(nu, a), M.t_std_es(nu, a)
    vs = np.linspace(1.0, 3.0, 81)
    Ls = np.sort(L)
    csum = np.r_[0, np.cumsum(Ls[::-1])][::-1]            # sum of the losses at or above index i
    def tail(v):
        i = np.searchsorted(Ls, v, side='right')
        k = n - i
        return (csum[i] - v * k) / n, k / n                 # E[(L-v)+], P(L > v)
    # expected pinball: E[(1{L>v} - a)(L - v)] = E[(L-v)+] - a E[L - v]
    mL = L.mean()
    pin = np.array([tail(v)[0] - a * (mL - v) for v in vs])
    ves = np.linspace(1.3, 2.6, 60)
    ees = np.linspace(1.8, 3.6, 60)
    Z = np.empty((len(ees), len(ves)))
    for j, v in enumerate(ves):
        ep, _ = tail(v)
        Z[:, j] = ep / (a * ees) + v / ees + np.log(ees) - 1
    Z[ees[:, None] < ves[None, :]] = np.nan
    ax6 = ax6 or a6_consistency()
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.9))
    ax = axs[0]
    ax.plot(vs, pin, color=g.MainBlue, lw=1.4, label='Mean pinball loss')
    ax.axvline(vq, color=g.IDAred, ls='--', lw=0.9, label=f'True VaR 2.5% = {vq:.3f}')
    ax.set_xlabel('Reported VaR v')
    ax.set_ylabel('Mean pinball loss')
    ax = axs[1]
    cs = ax.contour(ves, ees, Z, levels=14, cmap='viridis', linewidths=0.8)
    ax.plot(vq, eq, '*', color=g.IDAred, ms=11, label=f'Truth ({vq:.3f}, {eq:.3f})')
    ax.plot(ax6['v_fz'], ax6['e_fz'], 'o', mfc='none', mec='black', ms=8, label='Numerical minimiser')
    ax.set_xlabel('Reported VaR v')
    ax.set_ylabel('Reported ES e (e ≥ v)')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=4)
    g.save_fig('ch8_sem_a6_scores')
    return dict(VaR=float(vq), ES=float(eq), v_grid_min=float(vs[np.argmin(pin)]))


def ch_a7():
    """A7: ratio L/ES of the eight breach days and the added breach; Z2 before and after."""
    r = A7_L / A7_ES
    z2 = 1 - r.sum() / 6.25
    z2b = 1 - (r.sum() + 2.0) / 6.25
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.7), gridspec_kw=dict(width_ratios=[2, 1]))
    ax = axs[0]
    ax.bar(np.arange(1, 9), r, 0.6, color=g.MainBlue, label='L/ES on the 8 breach days')
    ax.bar([9], [2.0], 0.6, color=g.IDAred, label='Added breach: 7/3.5 = 2')
    ax.axhline(1.0, color='black', ls='--', lw=0.8, label='L = ES')
    for i, v in enumerate(np.r_[r, 2.0], 1):
        ax.text(i, v + 0.04, f'{v:.2f}', ha='center', fontsize=7, color='black')
    ax.set_xticks(range(1, 10))
    ax.set_xlabel('Breach day')
    ax.set_ylabel('L / ES')
    ax.set_ylim(0, 2.3)
    ax = axs[1]
    ax.axhspan(-0.70, 0.5, color=g.Forest, alpha=0.10, lw=0)
    ax.axhspan(-1.8, -0.70, color='#F1C40F', alpha=0.15, lw=0)
    ax.axhspan(-2.5, -1.8, color=g.IDAred, alpha=0.10, lw=0)
    ax.bar([0], [z2], 0.5, color=g.MainBlue, label=f'Z2, 8 breaches = {z2:.2f}')
    ax.bar([1], [z2b], 0.5, color=g.IDAred, label=f'Z2, 9 breaches = {z2b:.2f}')
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_xticks([0, 1], ['8 breaches', '9 breaches'])
    ax.set_ylim(-2.0, 0.4)
    ax.set_ylabel('Z2 (zones: -0.70, -1.8)')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=3)
    g.save_fig('ch8_sem_a7_z2')
    return dict(contrib=[float(x / 6.25) for x in r], z2=float(z2), z2b=float(z2b))


def ch_a8():
    """A8: the 19 sorted scores with ranks 18 and 19; conformal VaR as a step function of the working level."""
    s = np.sort(A8_S)
    n = len(s)
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.7))
    ax = axs[0]
    ax.plot(np.arange(1, n + 1), s, 'o', color=g.MainBlue, ms=4, label='Sorted score s(k)')
    for k, col in ((18, g.Forest), (19, g.IDAred)):
        ax.plot([k], [s[k - 1]], 'o', color=col, ms=8, mfc='none', mew=1.5, label=f's({k}) = {s[k - 1]:.2f}')
    ax.set_xticks(range(1, n + 1, 2))
    ax.set_xlabel('Rank k')
    ax.set_ylabel('Score s = L / σ')
    ax = axs[1]
    al = np.linspace(0.04, 0.20, 801)
    ks = np.ceil((n + 1) * (1 - al)).astype(int)
    var = np.where(ks <= n, 1.4 * s[np.minimum(ks, n) - 1], np.nan)
    ax.plot(100 * al, var, color=g.MainBlue, lw=1.3, label='VaR = 1.4 × s(k), k = ceil(20(1 − α))')
    for a_, col, lab in ((0.082, g.IDAred, 'α after a breach = 8.2%'), (0.10, 'black', 'α = 10%'),
                         (0.102, g.Forest, 'α after no breach = 10.2%')):
        k = int(np.ceil((n + 1) * (1 - a_)))
        ax.plot(100 * a_, 1.4 * s[k - 1], 'o', color=col, ms=5, label=lab)
    ax.axvspan(0.04 * 100, 100 / (n + 1), color=g.IDAred, alpha=0.08, lw=0)
    ax.text(0.02, 0.05, 'shaded: k > 19,\nVaR = ∞', transform=ax.transAxes, fontsize=7, color=g.IDAred)
    ax.set_xlabel('Working level α_t (%)')
    ax.set_ylabel('Conformal VaR (%)')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=3)
    g.save_fig('ch8_sem_a8_aci')
    return dict(s18=float(s[17]), s19=float(s[18]), inf_below=float(1 / (n + 1)))


def ch_a9(a=0.025):
    """A9: tail quantile functions on (1 - a, 1] of F0, F1 and their mixture; ES = area / a."""
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.4), sharey=True)
    u0 = 1 - a
    cases = (('F0: loss 1 for sure', [(u0, 1, 1.0)]),
             ('F1: P(L=2) = α/2, P(L=0) = 1 − α/2', [(u0, 1 - a / 2, 0.0), (1 - a / 2, 1, 2.0)]),
             ('Mixture ½F0 + ½F1', [(u0, 1 - a / 4, 1.0), (1 - a / 4, 1, 2.0)]))
    es = []
    for ax, (title, segs) in zip(axs, cases):
        for lo, hi, q in segs:
            ax.fill_between([100 * (lo - u0) / a, 100 * (hi - u0) / a], 0, q, color=g.MainBlue, alpha=0.3, lw=0)
            ax.plot([100 * (lo - u0) / a, 100 * (hi - u0) / a], [q, q], color=g.MainBlue, lw=1.6)
        e = sum((hi - lo) * q for lo, hi, q in segs) / a
        es.append(e)
        ax.axhline(e, color=g.IDAred, ls='--', lw=1.0, label='ES = mean of the tail quantiles')
        ax.text(3, e + 0.08, f'ES = {e:.2f}', color=g.IDAred, fontsize=8)
        ax.set_title(title, fontsize=8)
        ax.set_xlabel('Position in the upper α tail (%)')
        ax.set_ylim(0, 2.3)
    axs[0].set_ylabel('Tail quantile q_u')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=2)
    g.save_fig('ch8_sem_a9_mass')
    return dict(es=es)


def ch_a10(a=0.025, T=250, reps=20000, seed=12):
    """A10: H(u) and the sampling distribution of the mean of H over T = 250 i.i.d. uniform PITs."""
    rng = np.random.default_rng(seed)
    U = rng.uniform(size=(reps, T))
    Hb = ((U - (1 - a)) / a * (U > 1 - a)).mean(1)
    se = np.sqrt(a * (1 / 3 - a / 4) / T)
    crit_n = a / 2 + 1.645 * se
    crit_s = float(np.quantile(Hb, 0.95))
    rej = float(np.mean(Hb > crit_n))
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.7))
    ax = axs[0]
    u = np.linspace(0.9, 1, 400)
    ax.plot(u, (u - (1 - a)) / a * (u > 1 - a), color=g.MainBlue, lw=1.5, label='H(u) = (u − (1 − α))/α · 1{u > 1 − α}')
    ax.axvline(1 - a, color=g.Gray, lw=0.7, ls=':')
    ax.set_xlabel('PIT u')
    ax.set_ylabel('H(u)')
    ax = axs[1]
    ax.hist(Hb, bins=60, color=g.MainBlue, alpha=0.45, edgecolor='white', label=f'Mean of H over T = 250 ({reps} samples)')
    ax.axvline(crit_n, color=g.IDAred, lw=1.2, label=f'Normal 95% cut-off {crit_n:.4f}')
    ax.axvline(crit_s, color=g.Forest, lw=1.2, ls='--', label=f'Simulated 95th percentile {crit_s:.4f}')
    ax.set_xlabel('Mean of H')
    ax.set_ylabel('Frequency')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=2)
    g.save_fig('ch8_sem_a10_h')
    return dict(crit_n=float(crit_n), crit_s=crit_s, rej=rej, reps=reps, share_zero=float(np.mean(Hb == 0)))


def ch_b1(b1=None, dq=None, MC=None):
    """B1: ten dated days of GARCH-t; breach raster and duration survival; p-value heat map and simulated size."""
    F = g.fc('sp500')[0]
    gt = F['GARCH-t']
    h = (gt['L'] > gt['VaR1']).astype(int)
    h8 = h.loc['2008']
    roll = h8.rolling(10).sum()
    end = roll.idxmax()
    i = h8.index.get_loc(end)
    w = gt.loc[h8.index[i - 9]:end]
    ten = [dict(date=str(d.date()), L=float(100 * r['L']), VaR=float(100 * r['VaR1']), hit=int(r['L'] > r['VaR1']))
           for d, r in w.iterrows()]
    b1 = b1 or b1_sp500_var()
    dq = dq or b1_dq_sp500()
    MC = MC or g.mc_size_power()
    # timing chart
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axs[0]
    for k, m in enumerate(M.MODELS):
        hm = (F[m]['L'] > F[m]['VaR1'])
        ax.vlines(F[m].index[hm], k - 0.38, k + 0.38, color=g.MCOL[m], lw=0.7, label=m)
    ax.set_yticks(range(6), [f'{m} ({b1[m]["x"]})' for m in M.MODELS], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel('Breach days of VaR 1%, S&P 500 (count in brackets)')
    ax = axs[1]
    for m in M.MODELS:
        D, _, _ = M.durations((F[m]['L'] > F[m]['VaR1']).astype(int).values)
        Ds = np.sort(D)
        ax.step(Ds, 1 - np.arange(1, len(Ds) + 1) / (len(Ds) + 1), where='post', color=g.MCOL[m], lw=1.0)
    d = np.linspace(1, 900, 200)
    ax.plot(d, 0.99 ** d, color='black', ls='--', lw=0.9, label='No memory (geometric, 1%)')
    ax.set_yscale('log')
    ax.set_xlabel('Days between breaches d')
    ax.set_ylabel('Share of durations > d')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=7)
    g.save_fig('ch8_sem_b1_timing')
    # results chart
    P = pd.DataFrame({'Kupiec': [b1[m]['p_uc'] for m in M.MODELS], 'exact': [b1[m]['p_exact'] for m in M.MODELS],
                      'indep.': [b1[m]['p_ind'] for m in M.MODELS], 'CC': [b1[m]['p_cc'] for m in M.MODELS],
                      'duration': [b1[m]['p_dur'] for m in M.MODELS], 'DQ': [dq[m]['p'] for m in M.MODELS]},
                     index=M.MODELS)
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8), gridspec_kw=dict(width_ratios=[1.35, 1]))
    g.pv_heatmap(axs[0], P, title='p-values, VaR 1%, S&P 500 (log colour scale)')
    ax = axs[1]
    tests = ('POF', 'CC', 'DUR', 'DQ')
    reps = MC['reps']
    for j, (T, col) in enumerate((('250', g.MainBlue), ('5000', g.IDAred))):
        v = np.array([MC['Correct'][T][t] for t in tests])
        se = np.sqrt(v * (1 - v) / reps)
        ax.bar(np.arange(4) + (j - 0.5) * 0.36, 100 * v, 0.36, color=col, yerr=196 * se, capsize=2,
               error_kw=dict(lw=0.7), label=f'Simulated size, T = {T}')
    ax.axhline(5, color='black', ls='--', lw=0.8, label='Nominal 5%')
    ax.set_xticks(range(4), ['Kupiec', 'CC', 'duration', 'DQ'])
    ax.set_ylabel('Rejection rate of a correct model (%)')
    ax.set_title('Size of the set of tests (bars: ±1.96 Monte Carlo standard errors)', fontsize=9)
    plt.tight_layout()
    _bars_legend(fig, axs[1:], ncol=3)
    g.save_fig('ch8_sem_b1_results')
    return dict(ten=ten, x10=int(sum(t['hit'] for t in ten)))


def ch_b3():
    """B3: one residual and one Z2 contribution by hand; Z2 null distributions (full sample, last 250 days) and the
    bootstrap distribution of the McNeil-Frey t statistic, GARCH-t, S&P 500."""
    df = g.fc('sp500')[0]['GARCH-t']
    L, v, e, sc = (df[c].values for c in ('L', 'VaR2.5', 'ES2.5', 'scale'))
    hit = L > v
    j = int(np.argmax(np.where(hit, L, -np.inf)))
    T = len(L)
    worked = dict(date=str(df.index[j].date()), L=float(100 * L[j]), VaR=float(100 * v[j]), ES=float(100 * e[j]),
                  sigma=float(100 * sc[j]), resid=float((L[j] - e[j]) / sc[j]), ratio=float(L[j] / e[j]),
                  contrib=float(L[j] / e[j] / (T * M.A_ES)), T=T, Ta=float(T * M.A_ES), n=int(hit.sum()))
    zf = z2_null('sp500', 'GARCH-t')
    zl = z2_null('sp500', 'GARCH-t', last=250)
    # McNeil-Frey bootstrap distribution (same seed as M.mcneil_frey)
    res = ((L - e) / sc)[hit]
    n = len(res)
    tstat = res.mean() / (res.std(ddof=1) / np.sqrt(n))
    rng = np.random.default_rng(0)
    bs = rng.choice(res - res.mean(), (5000, n), replace=True)
    tb = bs.mean(1) / (bs.std(1, ddof=1) / np.sqrt(n))
    fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.6))
    for ax, z, lab in ((axs[0], zf, f'full sample, T = {T}'), (axs[1], zl, 'last 250 days')):
        ax.hist(z['sims'], bins=60, color=g.MainBlue, alpha=0.45, edgecolor='white', label='Simulated Z2 under H0')
        ax.axvline(z['Z2'], color=g.IDAred, lw=1.4, label='Observed Z2')
        ax.axvline(z['crit5'], color=g.Amber, lw=1.1, ls='--', label='Simulated 5% critical value')
        ax.set_xlabel(f'Z2, GARCH-t, {lab}')
        ax.text(0.03, 0.92, f'obs {z["Z2"]:.2f}\ncrit {z["crit5"]:.2f}', transform=ax.transAxes, fontsize=7,
                va='top', color='black')
    axs[1].axvline(-0.70, color='black', ls=':', lw=1.0, label='Fixed threshold −0.70')
    axs[0].set_ylabel('Frequency')
    ax = axs[2]
    ax.hist(tb, bins=60, color=g.Forest, alpha=0.45, edgecolor='white', label='Bootstrap t (centred residuals)')
    ax.axvline(tstat, color=g.IDAred, lw=1.4)
    ax.set_xlabel('McNeil–Frey t statistic, GARCH-t')
    ax.text(0.03, 0.92, f'obs t = {tstat:.2f}', transform=ax.transAxes, fontsize=7, va='top', color='black')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=3)
    g.save_fig('ch8_sem_b3_null')
    return dict(worked=worked, sd_full=float(zf['sims'].std()), sd_last=float(zl['sims'].std()))


def ch_b4():
    """B4: simulated Z2 null distributions and observed values, BET and Bitcoin, GARCH-t and GARCH-EVT (full sample)."""
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 3.6))
    out = {}
    for i, n in enumerate(('bet', 'btc')):
        for j, m in enumerate(('GARCH-t', 'GARCH-EVT')):
            z = z2_null(n, m)
            ax = axs[i, j]
            ax.hist(z['sims'], bins=50, color=g.MCOL[m], alpha=0.45, edgecolor='white', label='Simulated Z2 under H0')
            ax.axvline(z['Z2'], color='black', lw=1.3, label='Observed Z2')
            ax.axvline(z['crit5'], color=g.Amber, lw=1.0, ls='--', label='Simulated 5% critical value')
            ax.set_title(f'{M.LABELS[n]}, {m}: Z2 = {z["Z2"]:.3f}, p ' + ('< 0.001' if z['p'] < 0.001 else f'= {z["p"]:.3f}'), fontsize=8)
            ax.tick_params(labelsize=7)
            out[f'{n}|{m}'] = dict(Z2=z['Z2'], p=z['p'], crit5=z['crit5'])
    plt.tight_layout()
    _bars_legend(fig, axs.ravel(), ncol=3)
    g.save_fig('ch8_sem_b4_null')
    return out


def ch_b5(maxlag=20):
    """B5: one DM calculation step by step (GARCH-t minus FHS), score differentials over time, ACF, intervals."""
    Lf = g.fz_losses('sp500')
    d = (Lf['GARCH-t'] - Lf['FHS']).values
    T = len(d)
    lags = int(np.floor(4 * (T / 100) ** (2 / 9)))
    dc = d - d.mean()
    gam = [float(np.dot(dc[k:], dc[:len(dc) - k]) / T) for k in range(lags + 1)]
    lrv = gam[0] + 2 * sum((1 - k / (lags + 1)) * gam[k] for k in range(1, lags + 1))
    se = np.sqrt(lrv / T)
    worked = dict(T=T, lags=lags, dbar=float(d.mean()), gam=gam, lrv=float(lrv), se=float(se), dm=float(d.mean() / se),
                  se_naive=float(np.sqrt(gam[0] / T)), sum_w=float(2 * sum((1 - k / (lags + 1)) * gam[k] for k in range(1, lags + 1))))
    fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.7), gridspec_kw=dict(width_ratios=[1.5, 1, 1]))
    ax = axs[0]
    pairs = (('GARCH-t', g.MainBlue), ('HS', g.Teal), ('GARCH-EVT', g.IDAred))
    for m, col in pairs:
        dd = Lf[m] - Lf['FHS']
        ax.plot(dd.index, dd.cumsum(), color=col, lw=1.1, label=f'{m} minus FHS')
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_ylabel('Cumulative FZ0 difference')
    ax.tick_params(axis='x', labelsize=7)
    ax = axs[1]
    acf = [np.dot(dc[k:], dc[:T - k]) / T / gam[0] for k in range(1, maxlag + 1)]
    ax.bar(range(1, maxlag + 1), acf, color=g.MainBlue, width=0.7, label='ACF of d_t, GARCH-t minus FHS')
    ax.axhline(1.96 / np.sqrt(T), color=g.Gray, lw=0.7, ls=':')
    ax.axhline(-1.96 / np.sqrt(T), color=g.Gray, lw=0.7, ls=':')
    ax.set_xlabel('Lag k')
    ax.set_ylabel('Autocorrelation')
    ax = axs[2]
    ci = {}
    for i, (m, col) in enumerate(pairs):
        dd = (Lf[m] - Lf['FHS']).values
        s_n = dd.std(ddof=1) / np.sqrt(T)
        s_h = np.sqrt(M.nw_var(dd) / T)
        ax.errorbar([i - 0.12], [dd.mean()], yerr=[1.96 * s_n], fmt='o', color=col, ms=4, capsize=3, lw=1.0)
        ax.errorbar([i + 0.12], [dd.mean()], yerr=[1.96 * s_h], fmt='s', color=col, ms=4, capsize=3, lw=1.0,
                    mfc='white')
        ci[m] = dict(mean=float(dd.mean()), naive=float(1.96 * s_n), hac=float(1.96 * s_h))
    ax.plot([], [], 'o', color='black', ms=4, label='95% interval, naive standard error')
    ax.plot([], [], 's', color='black', mfc='white', ms=4, label='95% interval, HAC standard error')
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_xticks(range(3), ['GARCH-t', 'HS', 'GARCH-EVT'], fontsize=7.5)
    ax.set_ylabel('Mean FZ0 difference vs FHS')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=4)
    g.save_fig('ch8_sem_b5_dm')
    return dict(worked=worked, ci=ci, acf1=float(acf[0]), n_acf_out=int(np.sum(np.abs(acf) > 1.96 / np.sqrt(T))))


def mcs_steps(losses, alpha=0.10, B=1000, block=10, seed=2):
    """Same algorithm as M.mcs, recording each elimination: (model removed, T_max p-value, running p-value)."""
    rng = np.random.default_rng(seed)
    X = losses.values
    T, m = X.shape
    nb = int(np.ceil(T / block))
    idx = (rng.integers(0, T, (B, nb))[:, :, None] + np.arange(block)) % T
    idx = idx.reshape(B, -1)[:, :T]
    Lbar = X.mean(0)
    Lb = np.stack([X[i].mean(0) for i in idx])
    alive = list(range(m))
    steps, p_run = [], 0.0
    while len(alive) > 1:
        a = np.array(alive)
        d = Lbar[a] - Lbar[a].mean()
        db = Lb[:, a] - Lb[:, a].mean(1, keepdims=True)
        se = np.sqrt(np.mean((db - d) ** 2, axis=0))
        t = d / se
        tb = ((db - d) / se).max(1)
        p = float(np.mean(tb >= t.max()))
        p_run = max(p_run, p)
        worst = a[np.argmax(t)]
        steps.append(dict(removed=losses.columns[worst], tmax=float(t.max()), p=p, p_mcs=p_run, size=len(a)))
        alive.remove(worst)
    return steps


def ch_b6(S=None):
    """B6: MCS p-values on Bitcoin and EUR/RON; Bitcoin Murphy diagram, VaR 2.5%, HS minus GARCH-EVT."""
    S = S or b6_dm_btc_eurron()
    steps = {n: mcs_steps(g.fz_losses(n)) for n in ('btc', 'eurron')}
    th, a_, b_, dd, se = g.murphy('btc', 'HS', 'GARCH-EVT', 'VaR2.5', 0.025)
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8))
    ax = axs[0]
    for j, (n, col) in enumerate((('btc', g.Amber), ('eurron', g.MainBlue))):
        ax.bar(np.arange(6) + (j - 0.5) * 0.36, [S[n]['mcs'][m] for m in M.MODELS], 0.36, color=col,
               label=f'MCS p-value, {M.LABELS[n]}')
    ax.axhline(0.10, color='black', ls='--', lw=0.8, label='10%: models above stay in the 90% MCS')
    ax.set_xticks(range(6), M.MODELS, rotation=30, fontsize=7.5)
    ax.set_ylabel('MCS p-value (FZ0)')
    ax = axs[1]
    ax.fill_between(100 * th, 1e4 * (dd - 1.96 * se), 1e4 * (dd + 1.96 * se), color=g.LightGray, alpha=0.8,
                    label='95% pointwise HAC band')
    ax.plot(100 * th, 1e4 * dd, color=g.Purple, lw=1.3, label='HS minus GARCH-EVT, Bitcoin VaR 2.5%')
    ax.axhline(0, color=g.Gray, lw=0.7)
    ax.set_xlabel('Threshold θ (daily loss, %)')
    ax.set_ylabel('Elementary score difference (×10⁴)')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=2)
    g.save_fig('ch8_sem_b6_mcs')
    return dict(steps=steps, th_lo=float(th[0]), th_hi=float(th[-1]), n_th=len(th))


def ch_b7():
    """B7: split conformal VaR 5% on the S&P 500 with ex-ante crisis days and breaches; rates with counts."""
    r = M.load_returns('sp500')
    c = M.conformal_var(r, a=0.05).loc[g.fc('sp500')[0]['HS'].index[0]:]
    reg = M.regimes(r, c.index)
    hit = c['L'] > c['VaR_split']
    rng = np.random.default_rng(5)
    x = pd.Series(rng.standard_t(4, len(r)) * 0.01, index=r.index)
    ci = M.conformal_var(x, a=0.05).loc[c.index[0]:]
    regi = M.regimes(x, ci.index)
    hi = ci['L'] > ci['VaR_split']
    w = c.loc['2019-07-01':'2021-06-30']
    fig, axs = plt.subplots(1, 2, figsize=(7.8, 2.9), gridspec_kw=dict(width_ratios=[1.7, 1]))
    ax = axs[0]
    rw = reg.loc[w.index]
    ax.fill_between(w.index, -6, 16, where=rw.values, color=g.IDAred, alpha=0.10, lw=0, step='mid',
                    label='Crisis day (known ex ante)')
    ax.bar(w.index, 100 * w['L'], color=g.Orange, alpha=0.6, width=1.0, label='Daily loss')
    ax.plot(w.index, 100 * w['VaR_split'], color=g.MainBlue, lw=1.0, label='Split conformal VaR 5%')
    hw = w['L'] > w['VaR_split']
    ax.plot(w.index[hw], 100 * w['L'][hw], 'o', color=g.IDAred, ms=2.5, label='Breach')
    ax.set_ylim(-6, 13)
    ax.set_ylabel('Loss (%)')
    ax.tick_params(axis='x', labelsize=7)
    ax = axs[1]
    out = {}
    for j, (lab, hh, rr, col) in enumerate((('S&P 500', hit, reg, g.MainBlue), ('i.i.d. t4', hi, regi, g.Forest))):
        vals, errs, ns = [], [], []
        for sel in (np.ones(len(hh), bool), ~rr.values, rr.values):
            k, nn = int(hh.values[sel].sum()), int(sel.sum())
            p = k / nn
            vals.append(100 * p)
            errs.append(196 * np.sqrt(p * (1 - p) / nn))
            ns.append((k, nn))
        ax.bar(np.arange(3) + (j - 0.5) * 0.36, vals, 0.36, yerr=errs, capsize=2, color=col,
               error_kw=dict(lw=0.7), label=f'{lab} (±1.96 binomial standard errors)')
        out[lab] = ns
    ax.axhline(5, color='black', ls='--', lw=0.8, label='Nominal 5%')
    ax.set_xticks(range(3), ['All', 'Calm', 'Crisis'])
    ax.set_ylabel('Breach rate of VaR 5% (%)')
    plt.tight_layout()
    _bars_legend(fig, axs, ncol=3)
    g.save_fig('ch8_sem_b7_conformal')
    return dict(counts=out, first=str(c.index[0].date()))


def ch_b9(b9=None):
    """B9: Kupiec rejection rates of a correct GARCH-t model, estimated versus true parameters, against P/R."""
    b9 = b9 or b9_estimation_risk()
    reps = b9['reps']
    Ps = ('250', '1000', '5000')
    x = np.array([int(P) / 1000 for P in Ps])
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    for key, col, lab, mk in (('est', g.IDAred, 'Estimated parameters (R = 1000)', 'o'),
                              ('true', g.MainBlue, 'True parameters', 's')):
        v = np.array([b9[P][key] for P in Ps])
        se = np.sqrt(v * (1 - v) / reps)
        ax.errorbar(x, 100 * v, yerr=196 * se, fmt=mk + '-', color=col, capsize=3, ms=4, lw=1.1, label=lab)
    ax.axhline(5, color='black', ls='--', lw=0.8, label='Nominal 5%')
    ax.set_xscale('log')
    ax.set_xticks(x, ['0.25', '1', '5'])
    ax.set_xlabel('P / R (out-of-sample days / estimation days)')
    ax.set_ylabel('Kupiec rejection rate at 5% (%)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.2)
    g.save_fig('ch8_sem_b9_estrisk')
    return {P: dict(se_est=float(np.sqrt(b9[P]['est'] * (1 - b9[P]['est']) / reps)),
                    se_true=float(np.sqrt(b9[P]['true'] * (1 - b9[P]['true']) / reps))) for P in Ps}


def c2_fixture(n=400, day=320, shock=-0.08, seed=8):
    """C2 test price series: 400 prices from 100, daily log returns 1% x standardised Student-t4, seed 8,
    with a return of -8% on day 320."""
    rng = np.random.default_rng(seed)
    r = 0.01 * rng.standard_t(4, n) / np.sqrt(2)
    r[day] = shock
    P = 100 * np.exp(np.r_[0, np.cumsum(r)])
    return P


def ch_c2(W=250, p=0.01):
    """C2: VaR from the wrong window r[t-W:t+1] (includes the day forecast) versus the lagged window r[t-W:t]."""
    P = c2_fixture()
    r = np.diff(np.log(P))
    idx = np.arange(W, len(r))
    v_bad = np.array([-np.quantile(r[t - W:t + 1], p) for t in idx])
    v_ok = np.array([-np.quantile(r[t - W:t], p) for t in idx])
    L = -r[W:]
    I_bad, I_ok = (L > v_bad).astype(int), (L > v_ok).astype(int)
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    sel = slice(300 - W, 345 - W)
    days = idx[sel]
    ax.bar(days, 100 * L[sel], color=g.Orange, alpha=0.6, width=0.8, label='Daily loss (test series)')
    ax.step(days, 100 * v_bad[sel], where='mid', color=g.IDAred, lw=1.2, label='VaR from r[t−W : t+1] (includes day t)')
    ax.step(days, 100 * v_ok[sel], where='mid', color=g.MainBlue, lw=1.2, ls='--', label='VaR from r[t−W : t] (lagged)')
    ax.annotate('−8% on day 320: the wrong VaR already\nuses it (3.84%); the lagged VaR (2.28%)\nmoves only on day 321', (320.4, 3.84), xytext=(326, 5.6),
                fontsize=7.5, color='black', arrowprops=dict(arrowstyle='->', lw=0.7, color='black'))
    ax.set_xlabel('Day of the test series')
    ax.set_ylabel('Loss / VaR (%)')
    g.legend_outside_bottom(ax, ncol=2, y=-0.2)
    g.save_fig('ch8_sem_c2_lookahead')
    rs = M.load_returns('sp500')
    rr = rs.values
    jj = np.arange(W, len(rr))
    vb = np.array([-np.quantile(rr[t - W:t + 1], p) for t in jj])
    vo = np.array([-np.quantile(rr[t - W:t], p) for t in jj])
    Ls = -rr[W:]
    return dict(x_bad=int(I_bad.sum()), x_ok=int(I_ok.sum()), T=len(L), sp_bad=int((Ls > vb).sum()),
                sp_ok=int((Ls > vo).sum()), sp_T=len(Ls), sp_from=str(rs.index[W].date()), var_bad=float(100 * v_bad[320 - W]),
                var_ok=float(100 * v_ok[320 - W]), var_ok_after=float(100 * v_ok[321 - W]),
                P0=float(P[0]), P320=float(P[320]), P321=float(P[321]))


def ch_c3():
    """C3 reference results: Strict ESR (two-sided) and Intercept ESR (one-sided) p-values, 6 models x 4 markets,
    ES 2.5% forecasts in the returns convention, authors' R package esback."""
    ser1, ser3 = {}, {}
    for n in M.ASSETS:
        F = g.fc(n)[0]
        for m in M.MODELS:
            df = F[m]
            ser1[f'{n}|{m}'] = pd.DataFrame({'r': -df['L'].values, 'e': -df['ES2.5'].values})
    ESBACK_V = r"""
lib <- Sys.getenv('MFM_RLIB'); .libPaths(c(lib, .libPaths()))
args <- commandArgs(trailingOnly = TRUE)
d <- read.csv(args[1]); tau <- as.numeric(args[3]); ver <- as.integer(args[4])
set.seed(8)
out <- lapply(split(d, d$id), function(s) {
  b <- tryCatch(suppressWarnings(esback::esr_backtest(r = s$r, e = s$e, alpha = tau, version = ver)),
                error = function(e) NULL)
  if (is.null(b)) return(data.frame(id = s$id[1], p2 = NA, p1 = NA))
  p1 <- if (!is.null(b$pvalue_onesided_asymptotic)) b$pvalue_onesided_asymptotic else NA
  data.frame(id = s$id[1], p2 = b$pvalue_twosided_asymptotic, p1 = p1)
})
write.csv(do.call(rbind, out), args[2], row.names = FALSE)
"""
    import subprocess
    import tempfile
    tmp = tempfile.mkdtemp()
    d = pd.concat([df.assign(id=k)[['id', 'r', 'e']] for k, df in ser1.items()])
    d.to_csv(os.path.join(tmp, 'in.csv'), index=False)
    with open(os.path.join(tmp, 'esr.R'), 'w') as f:
        f.write(ESBACK_V)
    env = dict(os.environ, MFM_RLIB=os.path.join(tempfile.gettempdir(), 'mfm_rlib'))
    res = {}
    for ver in (1, 3):
        out = os.path.join(tmp, f'out{ver}.csv')
        subprocess.run(['Rscript', os.path.join(tmp, 'esr.R'), os.path.join(tmp, 'in.csv'), out, '0.025', str(ver)],
                       check=True, env=env)
        res[ver] = pd.read_csv(out).set_index('id')
    P1 = pd.DataFrame({M.LABELS[n]: [res[1].loc[f'{n}|{m}', 'p2'] for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
    P3 = pd.DataFrame({M.LABELS[n]: [res[3].loc[f'{n}|{m}', 'p1'] for m in M.MODELS] for n in M.ASSETS}, index=M.MODELS)
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8), sharey=True)
    g.pv_heatmap(axs[0], P1, title='Strict ESR, two-sided p-value')
    g.pv_heatmap(axs[1], P3, title='Intercept ESR, one-sided p-value')
    for ax in axs:
        ax.tick_params(axis='x', rotation=20)
    plt.tight_layout()
    g.save_fig('ch8_sem_c3_esr')
    return dict(strict={k: (None if pd.isna(v) else float(v)) for k, v in res[1]['p2'].items()},
                intercept={k: (None if pd.isna(v) else float(v)) for k, v in res[3]['p1'].items()})


def ch_b8_b2():
    """B8: counts, crisis days and infinite ACI forecasts (VaR 5%) on BET and Bitcoin; B2: rolling-window bookkeeping."""
    out = {}
    for n in ('bet', 'btc'):
        r = M.load_returns(n)
        c = M.conformal_var(r, a=0.05).loc[g.fc(n)[0]['HS'].index[0]:]
        reg = M.regimes(r, c.index)
        out[n] = dict(T=len(c), n_crisis=int(reg.sum()), first=str(c.index[0].date()),
                      inf_aci=int(np.isinf(c['VaR_aci']).sum()), inf_split=int(np.isinf(c['VaR_split']).sum()),
                      x_split=int((c['L'] > c['VaR_split']).sum()), x_aci=int((c['L'] > c['VaR_aci']).sum()))
    x = g.rolling_exceptions('bet', 'GARCH-t')
    h = g.hits('bet', 'GARCH-t')
    out['b2'] = dict(T=len(h), n_windows=len(x), first_end=str(x.index[0].date()), start=str(h.index[0].date()))
    return out


def seminar_charts():
    J = json.load(open(os.path.join(HERE, 'sem8_results.json')))
    MC = json.load(open(os.path.join(HERE, 'ch8_results.json')))['mc']
    out = dict(setup=ch_setup(), a1=ch_a1(), a2=ch_a2(), a3=ch_a3(), a4=ch_a4(), a5=ch_a5(), a6=ch_a6(J['AX']['a6c']),
               a7=ch_a7(), a8=ch_a8(), a9=ch_a9(), a10=ch_a10(), b1=ch_b1(J['b1'], J['BX']['b1dq'], MC), b3=ch_b3(),
               b4=ch_b4(), b5=ch_b5(), b6=ch_b6(J['b6']), b7=ch_b7(), b9=ch_b9(J['BX']['b9']), c2=ch_c2(),
               b8=ch_b8_b2())
    try:
        out['c3'] = ch_c3()
    except Exception as exc:                              # R or esback not available
        print('C3 reference results skipped:', exc)
    return out


if __name__ == '__main__' and '--charts' in sys.argv:
    R = json.load(open(os.path.join(HERE, 'sem8_results.json')))
    R['CH'] = seminar_charts()
    with open(os.path.join(HERE, 'sem8_results.json'), 'w') as f:
        json.dump(g.to_py(R), f, indent=1, default=str)
    print(json.dumps(g.to_py(R['CH']), indent=1, default=str)[:20000])
    sys.exit(0)
if __name__ == '__main__' and '--extras' in sys.argv:
    R = json.load(open(os.path.join(HERE, 'sem8_results.json')))
    R['AX'] = part_a_extras()
    R['BX'] = part_b_extras()
    with open(os.path.join(HERE, 'sem8_results.json'), 'w') as f:
        json.dump(g.to_py(R), f, indent=1, default=str)
    print(json.dumps(g.to_py(dict(AX=R['AX'], BX={k: v for k, v in R['BX'].items() if k != 'b9'})), indent=1))
elif __name__ == '__main__':
    R = run_all()
    with open(os.path.join(HERE, 'sem8_results.json'), 'w') as f:
        json.dump(g.to_py(R), f, indent=1, default=str)
    print(json.dumps(g.to_py(R), indent=1, default=str)[:30000])

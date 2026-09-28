"""
Seminarul 8: Backtesting si evaluarea prognozelor de risc -- calcule pentru toate problemele
=========================================================================================
Partea A: Kupiec, Christoffersen, semaforul Basel, FZ0, Z2 si cuantila conformala, pas cu pas.
Partea B: backtesting pe S&P 500, BET, Bitcoin si EUR/RON (curs BNR): teste VaR, teste ES cu
simulare si bootstrap, Diebold-Mariano (HAC), MCS, VaR conformal in perioade calme si de criza.
Partea C: portofoliu RON 50% BET + 50% EUR (analiza de referinta pentru profesor).
Modelarea Pietelor Financiare - Daniel Traian PELE
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
# PARTEA A
# =============================================================================
def a1_kupiec(T=250, x=7, p=0.01):
    """Kupiec pas cu pas."""
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


A6_L = np.array([0.8, -1.1, 3.4, 2.3, -0.5])          # pierderi (%) in cinci zile
A6_FC = {'A': (2.0, 2.6), 'B': (2.6, 3.4), 'C': (2.0, 4.0)}   # (VaR 2.5%, ES 2.5%), in %


def a6_fz0(a=0.025):
    out = {}
    for k, (v, e) in A6_FC.items():
        terms = M.fz0(A6_L, v, e, a)
        out[k] = dict(VaR=v, ES=e, terms=[float(t) for t in terms], mean=float(terms.mean()),
                      const=float(v / e + np.log(e) - 1), hit=[int(l > v) for l in A6_L])
    return out


A7_L = np.array([3.9, 2.8, 4.6, 3.1, 5.2, 2.9, 3.6, 7.4])      # pierderi (%) in zilele cu depasire
A7_ES = np.array([3.4, 3.3, 3.6, 3.2, 3.5, 3.3, 3.4, 3.8])      # ES prognozat (%) in acele zile


def a7_z2(T=250, a=0.025):
    r = A7_L / A7_ES
    z2 = 1 - r.sum() / (T * a)
    z1 = 1 - r.mean()
    return dict(ratios=[float(x) for x in r], sum=float(r.sum()), Z2=float(z2), Z1=float(z1), n=len(r), Ta=T * a)


A8_S = np.array([1.12, 0.35, 2.41, 0.88, 1.95, 0.52, 3.10, 1.47, 0.73, 2.02,
                 0.19, 1.66, 2.75, 0.94, 1.28, 0.61, 1.83, 2.28, 1.05])   # 19 scoruri de calibrare
A8_SD = 1.4          # abaterea standard (%) prognozata pentru ziua urmatoare


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


def part_a():
    return dict(a1=a1_kupiec(), a2=a1_kupiec(250, 11, 0.025), a3=a3_counts('bet', 'HS'), a4=a3_counts('bet', 'GARCH-t'),
                a5=a5_traffic(), a6=a6_fz0(), a7=a7_z2(), a8=a8_conformal())


# =============================================================================
# PARTEA B
# =============================================================================
def b1_sp500_var():
    """Teste VaR 1% pe S&P 500; valoarea p asimptotica vs exacta (binomiala)."""
    out = {}
    for m in M.MODELS:
        h = g.hits('sp500', m).values
        k, c, d = M.kupiec(h, 0.01), M.christoffersen(h, 0.01), M.duration_test(h)
        exact = 2 * min(stats.binom.cdf(k['x'], k['T'], 0.01), stats.binom.sf(k['x'] - 1, k['T'], 0.01))
        out[m] = dict(x=k['x'], T=k['T'], rate=k['rate'], p_uc=k['p'], p_exact=float(min(exact, 1)),
                      p_ind=c['p_ind'], p_cc=c['p_cc'], b=d['b'], p_dur=d['p'])
    # esantion mic: un an (2008) pentru GARCH-t
    h = g.hits('sp500', 'GARCH-t').loc['2008'].values
    k = M.kupiec(h, 0.01)
    out['small'] = dict(T=k['T'], x=k['x'], p_asy=k['p'],
                        p_exact=float(min(1, 2 * min(stats.binom.cdf(k['x'], k['T'], 0.01),
                                                     stats.binom.sf(k['x'] - 1, k['T'], 0.01)))))
    return out


def b2_traffic_bet():
    """Semaforul Basel pentru VaR 1% GARCH-t pe BET: ultimele 250 de zile si ponderea timpului pe zone."""
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
    """Distributia simulata a lui Z2 sub H0 (distributia prognozata de model)."""
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
        U = rng.uniform(size=(T, 500))
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
            ax.hist(zl['sims'], bins=60, color=g.MainBlue, alpha=0.45, edgecolor='white', label='Simulated $Z_2$ under H0 (5000 paths)')
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
        # simulare: aceeasi procedura pe date i.i.d. Student-t (schimbabile)
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
# PARTEA C: portofoliu RON 50% BET + 50% EUR
# =============================================================================
def portfolio_returns():
    """Pozitie in lei: jumatate in indicele BET, jumatate in euro (valoare in lei la cursul BNR).
    Join pe PRETURI in zilele comune, apoi randamente simple, apoi randamentul log al portofoliului."""
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
    # grafic: VaR 1% FHS si HS pe portofoliu
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


def run_all():
    R = dict(A=part_a(), b1=b1_sp500_var(), b2=b2_traffic_bet(), b3=b3_es_sp500(), b4=b4_z2_bet_btc(),
             b5=b5_dm_sp500(), b6=b6_dm_btc_eurron(), b7=b7_conformal_sp500(), b8=b8_conformal_bet_btc(), C=part_c())
    return R


if __name__ == '__main__':
    R = run_all()
    with open(os.path.join(HERE, 'sem8_results.json'), 'w') as f:
        json.dump(g.to_py(R), f, indent=1, default=str)
    print(json.dumps(g.to_py(R), indent=1, default=str)[:30000])

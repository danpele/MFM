"""
seminar7.py -- Calculele Seminarului 7 (MFM): VaR si Expected Shortfall
======================================================================
Partea A: VaR/ES pentru distributia Normala si Student-t pas cu pas, pierderi discrete, subaditivitate,
          VaR pe componente pentru doua active, Cornish-Fisher.
Partea B: HS pe BET cu interval bootstrap, GPD si EVT-VaR pe BET, FHS vs HS pe Bitcoin, Cornish-Fisher vs
          empiric, VaR pe componente pentru un portofoliu, interval bootstrap pentru ES.
Partea C: capitalul cerut de ES 2,5% pentru un portofoliu BVB de blue-chips vs un portofoliu S&P 500 (2016-2026).
Cifrele sunt salvate in sem7_results.json.
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
from mfm_data import log_returns, joint_returns   # noqa: E402
from risk_measures import (hs_var_es, normal_var_es, cf_quantile, cf_var_es, gpd_fit, gpd_var_es, gpd_se,  # noqa: E402
                           garch_filter, garch_next, fhs_mc)
from generate_all_charts import (save_fig, legend_outside_bottom, discrete_var_es, jsonable, MainBlue, IDAred,  # noqa: E402
                                 Forest, Amber, Orange, Teal, Gray, LightGray, Purple, SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
B_BOOT = 2000


# =============================================================================
# PARTEA A
# =============================================================================
def a1_normal(mu=0.04, sigma=1.2, position=1_000_000):
    """VaR si ES pentru distributia Normala, pas cu pas: X ~ N(mu, sigma^2) (randamente in %),
    VaR_alpha = -(mu + sigma z_alpha), ES_alpha = -mu + sigma phi(z_alpha) / alpha."""
    out = dict(mu=mu, sigma=sigma, position=position)
    for a, tag in [(0.01, '1'), (0.025, '2_5')]:
        z = stats.norm.ppf(a)                  # z_alpha < 0
        phi = stats.norm.pdf(z)
        out[f'z{tag}'] = z
        out[f'phi{tag}'] = phi
        out[f'k{tag}'] = phi / a
        out[f'var{tag}'] = -(mu + sigma * z)
        out[f'es{tag}'] = -mu + sigma * phi / a
    out['var1_10'] = -np.sqrt(10) * sigma * out['z1']
    return out


def a2_student(nu=4, mu=0.04, sigma=1.2):
    """Student-t standardizata la aceeasi dispersie: X = mu + s T, s = sigma sqrt((nu-2)/nu);
    VaR_alpha = -(mu + s t_alpha), ES_alpha = -mu + s g(t_alpha)/alpha (nu + t_alpha^2)/(nu - 1)."""
    s = sigma * np.sqrt((nu - 2) / nu)
    out = dict(nu=nu, s=s)
    for a, tag in [(0.01, '1'), (0.025, '2_5')]:
        q = stats.t.ppf(a, nu)                 # t_alpha < 0
        g = stats.t.pdf(q, nu)
        k = g / a * (nu + q ** 2) / (nu - 1)
        out[f'q{tag}'] = q
        out[f'g{tag}'] = g
        out[f'k{tag}'] = k
        out[f'var{tag}'] = -(mu + s * q)
        out[f'es{tag}'] = -mu + s * k
    return out


def a3_bond(p=0.03, lgd=60.0):
    out = dict(p=p, lgd=lgd)
    for a, tag in [(0.05, '5'), (0.025, '2_5')]:
        v, e = discrete_var_es([0, lgd], [1 - p, p], a)
        out[f'var{tag}'] = v
        out[f'es{tag}'] = e
    return out


def a4_bonds(p=0.007, lgd=100.0):
    out = dict(p=p, lgd=lgd, p_any=1 - (1 - p) ** 2, p_both=p ** 2, p_one=2 * p * (1 - p))
    for a, tag in [(0.01, '1'), (0.015, '1_5')]:
        v1, e1 = discrete_var_es([0, lgd], [1 - p, p], a)
        vp, ep = discrete_var_es([0, lgd, 2 * lgd], [(1 - p) ** 2, 2 * p * (1 - p), p ** 2], a)
        out.update({f'varA_{tag}': v1, f'esA_{tag}': e1, f'varP_{tag}': vp, f'esP_{tag}': ep})
    return out


def a5_components(pos=(600_000, 400_000), sig=(1.2, 0.9), rho=-0.2, alpha=0.01):
    """VaR 1% pe componente pentru doua active, distributia Normala, media zero."""
    w = np.array(pos, float)
    s = np.array(sig) / 100
    S = np.array([[s[0] ** 2, rho * s[0] * s[1]], [rho * s[0] * s[1], s[1] ** 2]])
    sp = np.sqrt(w @ S @ w)
    z = stats.norm.ppf(1 - alpha)              # z_{1-alpha} = -z_alpha > 0
    Sw = S @ w
    mvar = z * Sw / sp
    cvar = w * mvar
    return dict(w=w, s=s, rho=rho, z=z, var_p_amt=z * sp, sigma_p_amt=sp, sp2=sp ** 2, Sw=Sw, mvar=mvar, cvar=cvar,
                share=cvar / (z * sp), var_ind=z * s * w, undiv=(z * s * w).sum())


def a6_cf(S=-0.5, K=3.0, sigma=1.2, mu=0.0, alpha=0.01, K2=10.0):
    """Cornish-Fisher pe randamente: asimetria S, excesul de aplatizare K; VaR_alpha = -(mu + sigma z~_alpha)."""
    z = stats.norm.ppf(alpha)                  # z_alpha < 0
    t1, t2, t3 = (z ** 2 - 1) * S / 6, (z ** 3 - 3 * z) * K / 24, -(2 * z ** 3 - 5 * z) * S ** 2 / 36
    zc = cf_quantile(z, S, K)
    zc2 = cf_quantile(z, S, K2)
    return dict(S=S, K=K, K2=K2, z=z, t1=t1, t2=t2, t3=t3, zcf=zc, var_cf=-(mu + sigma * zc), var_n=-(mu + sigma * z),
                zcf2=zc2, var_cf2=-(mu + sigma * zc2))


# =============================================================================
# PARTEA B
# =============================================================================
def boot_ci(L, fun, B=B_BOOT, block=None, seed=SEED):
    """Interval bootstrap percentil 95%: i.i.d. (block=None) sau pe blocuri mobile de lungime block."""
    rng = np.random.default_rng(seed)
    L = np.asarray(L)
    n = len(L)
    stats_ = np.empty(B)
    for b in range(B):
        if block is None:
            x = L[rng.integers(0, n, n)]
        else:
            starts = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
            x = np.concatenate([L[s:s + block] for s in starts])[:n]
        stats_[b] = fun(x)
    return np.percentile(stats_, [2.5, 97.5]), stats_


def b1_bet_hs():
    L = -100 * log_returns('bet')
    out = {}
    boots = {}
    for tag, x in [('full', L), ('w500', L.iloc[-500:])]:
        v1, e1 = hs_var_es(x, 0.01)
        v2, e2 = hs_var_es(x, 0.025)
        ci, bs = boot_ci(x.values, lambda y: hs_var_es(y, 0.01)[0])
        boots[tag] = bs
        out[tag] = dict(N=len(x), start=str(x.index[0].date()), var1=v1, es1=e1, var2_5=v2, es2_5=e2,
                        ci_lo=ci[0], ci_hi=ci[1], n_beyond=int((x >= v1).sum()))
    # graficul: coada pierderilor + distributiile bootstrap
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    ax.hist(L[L > 1.5], bins=np.linspace(1.5, 13.5, 61), color=MainBlue, alpha=0.55, label='BET daily losses above 1.5%')
    ax.axvline(out['full']['var1'], color=IDAred, lw=1.3, label=f"VaR 1% = {out['full']['var1']:.2f}%")
    ax.axvline(out['full']['es1'], color=IDAred, ls='--', lw=1.3, label=f"ES 1% = {out['full']['es1']:.2f}%")
    ax.set_xlabel('Daily loss (%)')
    ax.set_ylabel('Number of days')
    ax.set_title('BET, 2000-2026: historical simulation')
    legend_outside_bottom(ax, 1, -0.2)
    ax = axes[1]
    ax.hist(boots['full'], bins=40, density=True, color=MainBlue, alpha=0.55, label='Full sample (2000-2026)')
    ax.hist(boots['w500'], bins=40, density=True, color=Amber, alpha=0.55, label='Last 500 days')
    ax.set_xlabel('Bootstrap VaR 1% (%)')
    ax.set_ylabel('Density')
    ax.set_title('Sampling uncertainty of HS VaR 1%')
    legend_outside_bottom(ax, 2, -0.2)
    plt.tight_layout()
    save_fig('ch7_sem_bet_hs')
    return out


def b2_bet_gpd():
    L = (-100 * log_returns('bet')).values
    f = gpd_fit(L, 0.05)
    se_xi, se_beta = gpd_se(f)
    out = dict(u=f['u'], xi=f['xi'], beta=f['beta'], nu=f['nu'], n=f['n'], se_xi=se_xi, se_beta=se_beta)
    for a, tag in [(0.01, '1'), (0.005, '0_5'), (0.001, '0_1')]:
        v, e = gpd_var_es(f, a)
        hv, he = hs_var_es(L, a)
        out.update({f'evt_var{tag}': v, f'evt_es{tag}': e, f'hs_var{tag}': hv, f'hs_es{tag}': he,
                    f'n_beyond{tag}': int((L >= hv).sum())})
    # sensibilitatea la prag
    qs = np.linspace(0.10, 0.015, 18)          # proportia pierderilor peste prag
    xis, lo, hi, v01 = [], [], [], []
    for q in qs:
        g = gpd_fit(L, q)
        s = gpd_se(g)[0]
        xis.append(g['xi'])
        lo.append(g['xi'] - 1.96 * s)
        hi.append(g['xi'] + 1.96 * s)
        v01.append(gpd_var_es(g, 0.001)[0])
    out['xi_range'] = [float(min(xis)), float(max(xis))]
    out['v0_1_range'] = [float(min(v01)), float(max(v01))]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3))
    ax = axes[0]
    xs = np.sort(L[L > f['u']])
    emp = (1 - np.arange(len(xs)) / len(xs)) * f['nu'] / f['n']
    ax.loglog(xs, emp, 'o', ms=2.5, color=MainBlue, label='Empirical P(L > x)')
    xx = np.linspace(f['u'], xs[-1] * 1.3, 200)
    ax.loglog(xx, f['nu'] / f['n'] * stats.genpareto.sf(xx - f['u'], f['xi'], scale=f['beta']), color=IDAred,
              label=f"GPD fit, xi = {f['xi']:.2f}")
    ax.loglog(xx, stats.norm.sf(xx, L.mean(), L.std()), color=Orange, ls='--', label='Normal distribution')
    ax.set_ylim(1e-5, 0.08)
    ax.set_xlabel('Daily loss x (%)')
    ax.set_ylabel('Exceedance probability')
    ax.set_title('BET: largest 5% of daily losses')
    legend_outside_bottom(ax, 2, -0.2)
    ax = axes[1]
    ax.fill_between(100 * qs, lo, hi, color=LightGray, label='95% confidence band')
    ax.plot(100 * qs, xis, 'o-', ms=3, color=IDAred, label='Estimated xi')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Share of losses above the threshold (%)')
    ax.set_ylabel('Shape parameter xi')
    ax.set_title('Stability of xi across thresholds')
    legend_outside_bottom(ax, 2, -0.2)
    plt.tight_layout()
    save_fig('ch7_sem_bet_gpd')
    return out


def b3_btc_fhs():
    r = 100 * log_returns('btc')
    params, mu, sig = garch_filter(r)
    z = ((r - mu) / sig).dropna().values
    m1, s1 = garch_next(r, params)
    nz = -z
    q = np.quantile(nz, 1 - 0.01)
    L = -r
    v500, e500 = hs_var_es(L.iloc[-500:], 0.01)
    vfull, efull = hs_var_es(L, 0.01)
    roll = pd.read_csv(os.path.join(HERE, 'ch7_rolling_btc.csv'), index_col=0, parse_dates=True)
    rec = roll.loc['2024-09-18':]
    out = dict(mu=m1, sigma=s1, sigma_uncond=r.std(), zq=q, zes=nz[nz >= q].mean(), fhs_var=-m1 + s1 * q,
               fhs_es=-m1 + s1 * nz[nz >= q].mean(), hs500_var=v500, hs500_es=e500, hsfull_var=vfull, hsfull_es=efull,
               n_rec=len(rec), exc_hs_rec=int((rec['loss'] > rec['hs_var']).sum()),
               exc_fhs_rec=int((rec['loss'] > rec['fhs_var']).sum()),
               exc_hs_all=float((roll['loss'] > roll['hs_var']).mean()),
               exc_fhs_all=float((roll['loss'] > roll['fhs_var']).mean()), n_all=len(roll),
               alpha=params.iloc[3], beta=params.iloc[4], sd500=r.iloc[-500:].std(), last_r=r.iloc[-1])
    fig, ax = plt.subplots(figsize=(10, 3.3))
    ax.bar(rec.index, rec['loss'].clip(lower=0), width=1, color=Teal, alpha=0.45, label='Daily loss (gains set to 0)')
    ax.plot(rec.index, rec['hs_var'], color=MainBlue, label='HS VaR 1% (500 days)')
    ax.plot(rec.index, rec['fhs_var'], color=IDAred, lw=0.9, label='FHS VaR 1%')
    ax.set_ylabel('Daily loss (%)')
    ax.set_title('Bitcoin, Sep 2024 - Sep 2026')
    legend_outside_bottom(ax, 3, -0.14)
    save_fig('ch7_sem_btc_fhs')
    return out


def b4_cf_vs_empirical():
    t = pd.read_csv(os.path.join(HERE, 'ch7_var_es_table.csv'), index_col=0)
    out = {}
    for k in t.index:
        L = (-100 * log_returns(k)).values
        ci, _ = boot_ci(L, lambda y: hs_var_es(y, 0.01)[0], B=1000)
        out[k] = dict(skew=-t.loc[k, 'skew'], kurt=t.loc[k, 'kurt'], hs1=t.loc[k, 'HS|VaR 1%'],
                      cf1=t.loc[k, 'Cornish-Fisher|VaR 1%'], n1=t.loc[k, 'Normal|VaR 1%'],
                      hs2_5=t.loc[k, 'HS|VaR 2.5%'], cf2_5=t.loc[k, 'Cornish-Fisher|VaR 2.5%'],
                      n2_5=t.loc[k, 'Normal|VaR 2.5%'], ci_lo=ci[0], ci_hi=ci[1])
    return out


def b5_components(w=(0.25, 0.25, 0.25, 0.25)):
    W = np.array(w)
    lr = joint_returns(['SPY', 'TLT', 'GLD', 'BTC'], start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)
    S = np.cov(R.values.T)
    sp = np.sqrt(W @ S @ W)
    z = stats.norm.ppf(1 - 0.01)
    mvar = z * (S @ W) / sp
    cvar = W * mvar
    Lp = -(R.values @ W)
    v, e = hs_var_es(Lp, 0.025)
    ces = -(R.values[Lp >= v] * W).mean(axis=0)
    return dict(N=len(R), var_p=z * sp, mvar=mvar, cvar=cvar, share=cvar / (z * sp), es_p=e, ces=ces,
                ces_share=ces / e, undiv=(z * np.sqrt(np.diag(S)) * W).sum())


def b6_es_boot():
    out = {}
    for k in ['sp500', 'bet']:
        L = (-100 * log_returns(k)).values
        for tag, x in [('full', L), ('w500', L[-500:])]:
            es = hs_var_es(x, 0.025)[1]
            ci_iid, _ = boot_ci(x, lambda y: hs_var_es(y, 0.025)[1])
            ci_blk, _ = boot_ci(x, lambda y: hs_var_es(y, 0.025)[1], block=20)
            out[f'{k}_{tag}'] = dict(N=len(x), es=es, iid_lo=ci_iid[0], iid_hi=ci_iid[1], blk_lo=ci_blk[0],
                                     blk_hi=ci_blk[1])
    return out


# =============================================================================
# PARTEA C: capitalul pentru ES 2,5%: BVB vs S&P 500
# =============================================================================
BVB = ['TLV', 'SNP', 'BRD', 'TGN', 'SNG', 'SNN', 'EL', 'TEL']
C_START = '2016-09-19'                  # ultimii zece ani


def c1_capital(position=1_000_000):
    lr_b = joint_returns(BVB, start=C_START)
    lr_b = lr_b[(lr_b != 0).any(axis=1)]                # fara zilele in care nicio actiune nu s-a schimbat
    start = str(lr_b.index[0].date())
    Rb = 100 * (np.exp(lr_b) - 1)
    rb = np.log(1 + Rb.mean(axis=1) / 100) * 100          # portofoliu cu ponderi egale, rebalansat zilnic
    rs = 100 * joint_returns(['SPY']).loc[start:]['SPY']
    out = dict(start=start, stocks=BVB)
    series = {'bvb': rb, 'spy': rs}
    for k, r in series.items():
        L = -r
        v1, e1 = hs_var_es(L, 0.025)
        L10 = -r.rolling(10).sum().dropna()
        e10 = hs_var_es(L10, 0.025)[1]
        # perioada de stres: fereastra de 250 de zile cu cel mai mare ES 2,5%
        roll = pd.Series([hs_var_es(L.iloc[i - 250:i], 0.025)[1] for i in range(250, len(L) + 1)],
                         index=L.index[249:])
        es_stress = roll.max()
        end_s = roll.idxmax()
        start_s = L.index[L.index.get_loc(end_s) - 249]
        params, mu, sig = garch_filter(r)
        z = ((r - mu) / sig).dropna().values
        m1, s1 = garch_next(r, params)
        nz = -z
        q = np.quantile(nz, 1 - 0.025)
        fhs1 = -m1 + s1 * nz[nz >= q].mean()
        sim = fhs_mc(r, params, z, 10, n_paths=100_000, seed=SEED)
        fhs10 = hs_var_es(sim, 0.025)[1]
        out[k] = dict(N=len(r), sd=r.std(), es1=e1, var1=v1, es10_sqrt=np.sqrt(10) * e1, es10_hs=e10,
                      es_stress1=es_stress, es_stress10=np.sqrt(10) * es_stress, stress_from=str(start_s.date()),
                      stress_to=str(end_s.date()), fhs1=fhs1, fhs10=fhs10, sigma_now=s1,
                      cap_hs=np.sqrt(10) * e1 / 100 * position, cap_stress=np.sqrt(10) * es_stress / 100 * position,
                      cap_stress_lh20=np.sqrt(20) * es_stress / 100 * position,
                      cap_fhs=fhs10 / 100 * position, zero_share=float((Rb == 0).mean().mean()) if k == 'bvb' else 0.0)
    out['corr_bvb_spy'] = float(pd.concat([rb, rs], axis=1, join='inner').corr().iloc[0, 1])
    # grafic
    fig, ax = plt.subplots(figsize=(8.5, 3.3))
    labs = ['HS, sqrt(10) x 1-day', 'HS, 10-day sums', 'Stressed 250 days, sqrt(10)', 'FHS Monte Carlo, 10-day']
    keys = ['es10_sqrt', 'es10_hs', 'es_stress10', 'fhs10']
    xx = np.arange(len(labs))
    vb = [out['bvb'][c] for c in keys]
    vs = [out['spy'][c] for c in keys]
    ax.bar(xx - 0.2, vb, 0.38, color=IDAred, label='BVB blue chips, equal weights')
    ax.bar(xx + 0.2, vs, 0.38, color=MainBlue, label='S&P 500 (SPY)')
    for i in range(len(labs)):
        ax.text(xx[i] - 0.2, vb[i] + 0.2, f'{vb[i]:.1f}', ha='center', fontsize=7)
        ax.text(xx[i] + 0.2, vs[i] + 0.2, f'{vs[i]:.1f}', ha='center', fontsize=7)
    ax.set_xticks(xx)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylabel('10-day ES 2.5% (% of position)')
    ax.set_title(f'Capital per unit invested, {start[:4]}-2026')
    legend_outside_bottom(ax, 2, -0.14)
    save_fig('ch7_sem_capital')
    return out


if __name__ == '__main__':
    S = dict(A1=a1_normal(), A2=a2_student(), A3=a3_bond(), A4=a4_bonds(), A5=a5_components(), A6=a6_cf())
    S['B1'] = b1_bet_hs()
    S['B2'] = b2_bet_gpd()
    S['B3'] = b3_btc_fhs()
    S['B4'] = b4_cf_vs_empirical()
    S['B5'] = b5_components()
    S['B6'] = b6_es_boot()
    S['C1'] = c1_capital()
    with open(os.path.join(HERE, 'sem7_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1)
    print(json.dumps(jsonable(S), indent=1)[:12000])

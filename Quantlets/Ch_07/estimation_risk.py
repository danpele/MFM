"""
estimation_risk.py -- Inferenta pentru masurile de risc (Capitolul 7, MFM)
=========================================================================
  * erori standard asimptotice pentru VaR si ES istorice (cuantila empirica; ES: Chen, 2008), i.i.d. si HAC;
  * reprezentarea Rockafellar-Uryasev a ES si portofoliul cu ES minim (program liniar pe scenarii);
  * agregarea VaR sub incertitudinea dependentei: algoritmul de rearanjare (Embrechts, Puccetti & Rueschendorf, 2013);
  * riscul de estimare in VaR-ul FHS: bootstrap pe reziduuri (Christoffersen & Goncalves, 2005);
  * CAViaR cu valoare absoluta simetrica (Engle & Manganelli, 2004), estimat prin pierderea pinball;
  * indicele extremal (estimatorul pe intervale, Ferro & Segers, 2003) si declusterizarea.
Conventie: pierderea L = -r in %, VaR_alpha = q_{1-alpha}(L) = -q_alpha(r), ES_alpha = E[L | L >= VaR_alpha].
Cifrele sunt salvate in ch7_inference.json; graficul ch7_caviar.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, optimize, signal
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import log_returns, joint_returns   # noqa: E402
from risk_measures import hs_var_es, gpd_fit, gpd_se, gpd_var_es, garch_filter, garch_next, rolling_conditional  # noqa: E402
from seminar7 import boot_ci   # noqa: E402
from generate_all_charts import save_fig, legend_outside_bottom, jsonable, MainBlue, IDAred, Teal, Amber, SEED  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# 1. Distributia de selectie a VaR si ES istorice
# =============================================================================
def nw_lrv(x):
    """Dispersia de termen lung (Newey-West, nucleu Bartlett, decalaj floor(4 (n/100)^(2/9)))."""
    x = np.asarray(x, float) - np.mean(x)
    n = len(x)
    m = int(np.floor(4 * (n / 100) ** (2 / 9)))
    s = x @ x / n
    for j in range(1, m + 1):
        s += 2 * (1 - j / (m + 1)) * (x[j:] @ x[:-j]) / n
    return s, m


def var_es_se(L, a_var=0.01, a_es=0.025):
    """VaR istoric: avar = a(1-a)/f(q)^2 (densitate prin nucleu Gaussian, regula lui Silverman);
    ES istoric (Chen, 2008): functia de influenta VaR + (L - VaR)_+/a - ES, avar = Var((L - VaR)_+)/a^2.
    Varianta HAC: dispersia de termen lung a indicatorului, respectiv a lui (L - VaR)_+."""
    L = np.asarray(L, float)
    n = len(L)
    v = np.quantile(L, 1 - a_var)
    f = stats.gaussian_kde(L, bw_method='silverman')(v)[0]
    ind = (L > v).astype(float)
    se_v = np.sqrt(a_var * (1 - a_var) / n) / f
    se_v_hac = np.sqrt(nw_lrv(ind)[0] / n) / f
    v2, e2 = hs_var_es(L, a_es)
    ex = np.maximum(L - v2, 0)
    se_e = ex.std(ddof=1) / (a_es * np.sqrt(n))
    lrv, m = nw_lrv(ex)
    se_e_hac = np.sqrt(lrv / n) / a_es
    return dict(n=n, var1=v, f=f, se_var=se_v, se_var_hac=se_v_hac, es=e2, var_es=v2, se_es=se_e,
                se_es_hac=se_e_hac, lag=m, ntail=a_es * n)


def se_theory(sigma=1.2, n=500, nu=4, alpha=0.01):
    """SE asimptotic al VaR 1% istoric sub distributia Normala si sub Student-t (aceeasi abatere standard)."""
    z = stats.norm.ppf(1 - alpha)
    f_n = stats.norm.pdf(z) / sigma
    s = sigma * np.sqrt((nu - 2) / nu)
    q = stats.t.ppf(1 - alpha, nu)
    f_t = stats.t.pdf(q, nu) / s
    c = np.sqrt(alpha * (1 - alpha) / n)
    return dict(se_normal=c / f_n, se_t=c / f_t, q_normal=sigma * z, q_t=s * q)


# =============================================================================
# 2. Rockafellar-Uryasev: ES ca problema de optimizare
# =============================================================================
def ru_objective(L, v, alpha):
    return v + np.maximum(np.asarray(L) - v, 0).mean() / alpha


def ru_check(L, alpha=0.025):
    L = np.asarray(L, float)
    res = optimize.minimize_scalar(lambda v: ru_objective(L, v, alpha), bounds=(0, L.max()), method='bounded',
                                   options=dict(xatol=1e-8))
    v, e = hs_var_es(L, alpha)
    return dict(argmin=res.x, min=res.fun, var=v, es=e)


def min_es_portfolio(R, alpha=0.025):
    """ES minim pe scenarii (Rockafellar & Uryasev, 2000): min v + 1/(alpha N) sum u_s,
    u_s >= -R_s w - v, u_s >= 0, sum w = 1, w >= 0 (fara vanzari in lipsa)."""
    N, d = R.shape
    c = np.concatenate([np.zeros(d), [1.0], np.full(N, 1 / (alpha * N))])
    from scipy.sparse import csr_matrix, hstack as sh, identity
    A = sh([csr_matrix(-R), csr_matrix(-np.ones((N, 1))), -identity(N)]).tocsr()
    b = np.zeros(N)
    Aeq = np.concatenate([np.ones(d), [0.0], np.zeros(N)])[None, :]
    bounds = [(0, None)] * d + [(None, None)] + [(0, None)] * N
    out = optimize.linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=[1.0], bounds=bounds, method='highs')
    return out.x[:d], out.x[d], out.fun


def min_var_portfolio(R):
    S = np.cov(R.T)
    d = S.shape[0]
    res = optimize.minimize(lambda w: w @ S @ w, np.full(d, 1 / d), bounds=[(0, 1)] * d,
                            constraints=[dict(type='eq', fun=lambda w: w.sum() - 1)], method='SLSQP',
                            options=dict(ftol=1e-14, maxiter=500))
    return res.x


def drop_largest(L, alpha_var=0.01, alpha_es=0.025):
    """Sensibilitatea la o singura observatie: VaR 1% si ES 2,5% istorice cu si fara cea mai mare pierdere."""
    L = np.asarray(L, float)
    L2 = np.delete(L, np.argmax(L))
    return dict(max=L.max(), var=np.quantile(L, 1 - alpha_var), var_drop=np.quantile(L2, 1 - alpha_var),
                es=hs_var_es(L, alpha_es)[1], es_drop=hs_var_es(L2, alpha_es)[1])


# =============================================================================
# 3. Agregare sub incertitudinea dependentei: algoritmul de rearanjare
# =============================================================================
def rearrangement(X, tol=1e-10, max_iter=1000):
    X = X.copy()
    for _ in range(max_iter):
        old = X.copy()
        for j in range(X.shape[1]):
            rest = X.sum(axis=1) - X[:, j]
            X[np.argsort(rest), j] = np.sort(X[:, j])[::-1]    # ordonare opusa fata de suma celorlalte coloane
        if np.max(np.abs(X - old)) < tol:
            break
    return X


def worst_var_ra(Lcols, alpha=0.01, N=2000):
    """VaR 1% maxim al sumei cu marginale date (Embrechts, Puccetti & Rueschendorf, 2013):
    discretizam coada de probabilitate alpha a fiecarei marginale in N puncte (jos / sus) si rearanjam;
    VaR-ul cel mai rau ~ minimul sumelor pe randuri."""
    lo = np.column_stack([np.quantile(x, 1 - alpha + alpha * np.arange(N) / N) for x in Lcols])
    hi = np.column_stack([np.quantile(x, 1 - alpha + alpha * np.arange(1, N + 1) / N) for x in Lcols])
    return rearrangement(lo).sum(axis=1).min(), rearrangement(hi).sum(axis=1).min()


def aggregation(alpha=0.01):
    W = np.array([0.40, 0.30, 0.20, 0.10])
    lr = joint_returns(['SPY', 'TLT', 'GLD', 'BTC'], start='2014-09-18')
    R = 100 * (np.exp(lr) - 1)
    Lw = [-(R.values[:, i] * W[i]) for i in range(4)]
    como = sum(np.quantile(x, 1 - alpha) for x in Lw)
    hist = np.quantile(-(R.values @ W), 1 - alpha)
    lo, hi = worst_var_ra(Lw, alpha)
    # ES minim (LP) si portofoliul de dispersie minima, alpha = 2.5%
    w_es, v_es, es_min = min_es_portfolio(R.values, 0.025)
    w_mv = min_var_portfolio(R.values)
    es_mv = hs_var_es(-(R.values @ w_mv), 0.025)[1]
    es_ew = hs_var_es(-(R.values @ W), 0.025)[1]
    sd_es = np.std(R.values @ w_es, ddof=1)
    sd_mv = np.std(R.values @ w_mv, ddof=1)
    return dict(N=len(R), var_hist=hist, var_como=como, var_worst_lo=lo, var_worst_hi=hi,
                w_es=w_es, es_min=es_min, v_es=v_es, w_mv=w_mv, es_mv=es_mv, es_4030=es_ew, sd_es=sd_es, sd_mv=sd_mv)


# =============================================================================
# 4. Riscul de estimare in VaR-ul FHS (bootstrap pe reziduuri)
# =============================================================================
def fhs_bootstrap(r, alpha=0.01, B=999, seed=SEED, level=0.90):
    """Christoffersen & Goncalves (2005): traiectorii AR(1)-GARCH(1,1) cu reziduuri reesantionate;
    re-estimam parametrii pe fiecare traiectorie; sigma_{T+1} din datele ORIGINALE cu parametrii bootstrap;
    cuantila din reziduurile standardizate ale traiectoriei bootstrap."""
    rng = np.random.default_rng(seed)
    params, mu, sig = garch_filter(r)
    z = ((r - mu) / sig).dropna().values
    m1, s1 = garch_next(r, params)
    var0 = -m1 + s1 * np.quantile(-z, 1 - alpha)
    c, phi, om, al, be = params.values[:5]
    n = len(r)
    out = np.empty(B)
    parts = np.empty((B, 2))
    for b in range(B):
        zz = rng.choice(z, n)
        rs = np.empty(n)
        s2 = om / (1 - al - be)
        rp, ep = r.iloc[0], 0.0
        for t in range(n):
            s2 = om + al * ep ** 2 + be * s2 if t > 0 else s2
            e = np.sqrt(s2) * zz[t]
            rs[t] = c + phi * rp + e
            rp, ep = rs[t], e
        rs = pd.Series(rs, index=r.index)
        pb, mub, sgb = garch_filter(rs)
        zb = ((rs - mub) / sgb).dropna().values
        mb, sb = garch_next(r, pb)                    # istoria ORIGINALA, parametrii bootstrap
        qb = np.quantile(-zb, 1 - alpha)
        out[b] = -mb + sb * qb
        parts[b] = [sb, qb]
    lo, hi = np.quantile(out, [(1 - level) / 2, (1 + level) / 2])
    # descompunere: doar incertitudinea cuantilei (sigma fixat) vs doar a lui sigma (cuantila fixata)
    q0 = np.quantile(-z, 1 - alpha)
    only_q = np.quantile(-m1 + s1 * parts[:, 1], [(1 - level) / 2, (1 + level) / 2])
    only_s = np.quantile(-m1 + parts[:, 0] * q0, [(1 - level) / 2, (1 + level) / 2])
    return dict(var=var0, lo=lo, hi=hi, sd=out.std(ddof=1), B=B, level=level, sigma=s1,
                sig_lo=np.quantile(parts[:, 0], (1 - level) / 2), sig_hi=np.quantile(parts[:, 0], (1 + level) / 2),
                q=q0, q_lo=np.quantile(parts[:, 1], (1 - level) / 2), q_hi=np.quantile(parts[:, 1], (1 + level) / 2),
                onlyq_lo=only_q[0], onlyq_hi=only_q[1], onlys_lo=only_s[0], onlys_hi=only_s[1])


# =============================================================================
# 5. CAViaR (valoare absoluta simetrica), estimat prin pierderea pinball
# =============================================================================
def caviar_path(beta, r, v0):
    """VaR_t = b0 + b1 VaR_{t-1} + b2 |r_{t-1}| (VaR pozitiv; cuantila q_t = -VaR_t)."""
    b0, b1, b2 = beta
    x = b0 + b2 * np.abs(np.asarray(r, float)[:-1])
    rest = signal.lfilter([1.0], [1.0, -b1], x, zi=[b1 * v0])[0]
    return np.concatenate([[v0], rest])


def pinball(r, q, alpha):
    """Pierderea pinball (tick) medie pentru cuantila q a randamentului: (alpha - 1{r < q})(r - q)."""
    return np.mean((alpha - (r < q)) * (r - q))


def caviar_fit(r, alpha=0.01, n_rand=10_000, n_best=10, seed=SEED):
    """Engle & Manganelli (2004): 10^4 vectori initiali U(0,1), cei mai buni 10 rafinati alternand simplex
    si quasi-Newton pana la convergenta; VaR initial = cuantila empirica a primelor 300 de observatii."""
    r = np.asarray(r, float)
    v0 = -np.quantile(r[:300], alpha)
    obj = lambda b: pinball(r, -caviar_path(b, r, v0), alpha) if abs(b[1]) < 1 else 1e6  # noqa: E731
    rng = np.random.default_rng(seed)
    cand = rng.uniform(0, 1, (n_rand, 3))
    vals = np.array([obj(b) for b in cand])
    best = []
    for b in cand[np.argsort(vals)[:n_best]]:
        f_old = np.inf
        for _ in range(20):
            b = optimize.minimize(obj, b, method='Nelder-Mead', options=dict(xatol=1e-8, fatol=1e-12, maxiter=4000)).x
            b = optimize.minimize(obj, b, method='BFGS').x
            f = obj(b)
            if f_old - f < 1e-12:
                break
            f_old = f
        best.append((obj(b), b))
    f, b = min(best, key=lambda x: x[0])
    return b, v0, f


def caviar_study(name, est_end='2015-12-31', oos_start='2016-01-01', alpha=0.01, fhs=None):
    r = 100 * log_returns(name)
    b, v0, f = caviar_fit(r.loc[:est_end].values, alpha)
    v = pd.Series(caviar_path(b, r.values, v0), index=r.index)
    L = -r
    oos = r.loc[oos_start:].index
    out = dict(b0=b[0], b1=b[1], b2=b[2], n_est=int(len(r.loc[:est_end])), n_oos=int(len(oos)),
               hit_caviar=float((L.loc[oos] > v.loc[oos]).mean()),
               n_hit_caviar=int((L.loc[oos] > v.loc[oos]).sum()),
               pin_caviar=pinball(r.loc[oos].values, -v.loc[oos].values, alpha))
    if fhs is not None:
        d = fhs.loc[oos_start:]
        out.update(hit_fhs=float((d['loss'] > d['fhs_var']).mean()), n_hit_fhs=int((d['loss'] > d['fhs_var']).sum()),
                   pin_fhs=pinball(-d['loss'].values, -d['fhs_var'].values, alpha),
                   hit_hs=float((d['loss'] > d['hs_var']).mean()), n_hit_hs=int((d['loss'] > d['hs_var']).sum()),
                   pin_hs=pinball(-d['loss'].values, -d['hs_var'].values, alpha))
        cov = d.loc['2020-02-20':'2020-04-30']
        vc = v.loc[cov.index]
        out.update(covid_hit_caviar=int((cov['loss'] > vc).sum()), covid_hit_fhs=int((cov['loss'] > cov['fhs_var']).sum()),
                   covid_hit_hs=int((cov['loss'] > cov['hs_var']).sum()),
                   covid_max_caviar=float(vc.max()), covid_max_fhs=float(cov['fhs_var'].max()),
                   covid_max_hs=float(cov['hs_var'].max()), covid_days=int(len(cov)))
    return out, v


def fig_caviar(v, fhs, name='sp500', title='S&P 500', start='2016-01-01'):
    d = fhs.loc[start:]
    fig, ax = plt.subplots(figsize=(10, 3.3))
    ax.bar(d.index, d['loss'].clip(lower=0), width=1.5, color=Teal, alpha=0.45, label='Daily loss (gains set to 0)')
    ax.plot(d.index, v.loc[d.index], color=MainBlue, lw=0.9, label='CAViaR (SAV) VaR 1%, parameters from 2000-2015')
    ax.plot(d.index, d['fhs_var'], color=IDAred, lw=0.8, label='FHS VaR 1%, re-estimated every January')
    ax.set_ylabel('Daily loss (%)')
    ax.set_title(f'{title}, 2016-2026: one-day-ahead VaR 1% out of sample')
    legend_outside_bottom(ax, 3, -0.14)
    save_fig(f'ch7_caviar' if name == 'sp500' else f'ch7_sem_caviar_{name}')


# =============================================================================
# 6. Indicele extremal (Ferro & Segers, 2003) si declusterizarea
# =============================================================================
def extremal_index(L, tail=0.05):
    """Estimatorul pe intervale: timpii dintre depasiri T_i; declusterizare cu cei mai mari C - 1 timpi,
    C = floor(theta N) + 1; GPD pe maximele clusterelor."""
    L = np.asarray(L, float)
    u = np.quantile(L, 1 - tail)
    S = np.flatnonzero(L > u)
    T = np.diff(S).astype(float)
    N = len(S)
    if T.max() <= 2:
        th = 2 * T.sum() ** 2 / ((N - 1) * (T ** 2).sum())
    else:
        th = 2 * (T - 1).sum() ** 2 / ((N - 1) * ((T - 1) * (T - 2)).sum())
    th = min(1.0, th)
    C = int(np.floor(th * N)) + 1
    cut = np.sort(T)[::-1][C - 2] if C > 1 else np.inf           # al (C-1)-lea cel mai mare timp
    breaks = np.flatnonzero(T > cut) if np.sum(T >= cut) > C - 1 else np.flatnonzero(T >= cut)
    groups = np.split(np.arange(N), breaks + 1)
    cmax = np.array([L[S[g]].max() for g in groups])
    xi, _, beta = stats.genpareto.fit(cmax - u, floc=0)
    fc = dict(u=u, xi=xi, beta=beta, nu=len(cmax), n=len(L))
    f = gpd_fit(L, tail)
    return dict(u=u, N=N, theta=th, n_clusters=len(groups), mean_size=N / len(groups),
                xi=f['xi'], se_xi=gpd_se(f)[0], xi_c=xi, se_xi_c=gpd_se(fc)[0], beta_c=beta,
                se_xi_eff=(1 + f['xi']) / np.sqrt(th * N))


def gev_theta(theta):
    """VaR 1% zilnic din maximele lunare cu corectia indicelui extremal: H^{-1}((1-alpha)^{n theta})."""
    r = 100 * log_returns('sp500')
    L = -r
    M = L.groupby([L.index.year, L.index.month]).max()
    n_block = L.groupby([L.index.year, L.index.month]).size().mean()
    c, loc, scale = stats.genextreme.fit(M.values)
    return dict(var1=stats.genextreme.ppf(0.99 ** n_block, c, loc, scale),
                var1_theta=stats.genextreme.ppf(0.99 ** (n_block * theta), c, loc, scale),
                pow_theta=0.99 ** (n_block * theta))


# =============================================================================
# 7. Cifre pentru seminar (A1', A6', A8, B1(c))
# =============================================================================
def seminar_extras():
    out = {}
    # A8: dispersia asimptotica a ES 2,5% istoric sub N(0, 1): Var((L - v)_+) / alpha^2, momente de Normala trunchiata
    a = 0.025
    v = stats.norm.ppf(1 - a)
    m1 = stats.norm.pdf(v) - v * a                       # E[(L - v)_+]
    m2 = (1 + v ** 2) * a - v * stats.norm.pdf(v)        # E[(L - v)_+^2]
    avar = (m2 - m1 ** 2) / a ** 2
    out['a8'] = dict(v=v, phi=stats.norm.pdf(v), m1=m1, m2=m2, var=m2 - m1 ** 2, avar=avar,
                     se500=np.sqrt(avar / 500), se500_pct=1.2 * np.sqrt(avar / 500), es=stats.norm.pdf(v) / a)
    # A6': monotonia hartii Cornish-Fisher pe z in [z_0.1%, 0]: derivata a z^2 + b z + c > 0
    def dmin(S, K):
        z = np.linspace(stats.norm.ppf(0.001), 0, 20001)
        return (1 + z * S / 3 + (3 * z ** 2 - 3) * K / 24 - (6 * z ** 2 - 5) * S ** 2 / 36).min()
    S = -0.5
    kmax = optimize.brentq(lambda K: dmin(S, K), 0.1, 30)
    kmax0 = optimize.brentq(lambda K: dmin(0.0, K), 0.1, 30)
    out['a6'] = dict(kmax=kmax, kmax0=kmax0, d3=dmin(S, 3.0), d10=dmin(S, 10.0))
    # A1': SE asimptotic al VaR 1% istoric sub N(0.04, 1.2^2)
    z = stats.norm.ppf(0.01)
    out['a1'] = dict(f=stats.norm.pdf(z) / 1.2, se500=1.2 * np.sqrt(0.01 * 0.99 / 500) / stats.norm.pdf(z),
                     se6670=1.2 * np.sqrt(0.01 * 0.99 / 6670) / stats.norm.pdf(z))
    # B1(c): BET, VaR 1%: interval asimptotic (densitate prin nucleu) si bootstrap pe blocuri (20 de zile)
    L = (-100 * log_returns('bet')).values
    for tag, x in [('full', L), ('w500', L[-500:])]:
        se = var_es_se(x)
        ci_blk, _ = boot_ci(x, lambda y: hs_var_es(y, 0.01)[0], block=20)
        out[f'b1_{tag}'] = dict(var1=se['var1'], f=se['f'], se=se['se_var'], se_hac=se['se_var_hac'],
                                lo=se['var1'] - 1.96 * se['se_var'], hi=se['var1'] + 1.96 * se['se_var'],
                                lo_hac=se['var1'] - 1.96 * se['se_var_hac'], hi_hac=se['var1'] + 1.96 * se['se_var_hac'],
                                blk_lo=ci_blk[0], blk_hi=ci_blk[1])
    return out


# =============================================================================
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'extras':
    with open(os.path.join(HERE, 'ch7_inference.json')) as f:
        OUT = json.load(f)
    L_sp = (-100 * log_returns('sp500')).values
    L_bet = (-100 * log_returns('bet')).values
    OUT['ei_sp1'] = extremal_index(L_sp, 0.01)
    OUT['ei_bet1'] = extremal_index(L_bet, 0.01)
    OUT['gev1'] = gev_theta(OUT['ei_sp1']['theta'])
    OUT['sem'] = seminar_extras()
    r_ = 100 * log_returns('sp500')
    _p, _mu, _sg = garch_filter(r_)
    OUT['ei_z'] = extremal_index(-((r_ - _mu) / _sg).dropna().values, 0.05)
    r_sp = -100 * log_returns('sp500')
    OUT['drop_full'] = drop_largest(r_sp.values)
    OUT['drop_w500'] = drop_largest(r_sp.values[-500:])
    OUT['drop_w500']['date'] = str(r_sp.iloc[-500:].idxmax().date())
    print(OUT['ei_sp1'], OUT['ei_bet1'], OUT['gev1'], OUT['sem'])
    with open(os.path.join(HERE, 'ch7_inference.json'), 'w') as f:
        json.dump(jsonable(OUT), f, indent=1)
elif __name__ == '__main__':
    OUT = {}
    L_sp = (-100 * log_returns('sp500')).values
    L_bet = (-100 * log_returns('bet')).values
    OUT['se'] = {'sp500_full': var_es_se(L_sp), 'sp500_w500': var_es_se(L_sp[-500:]),
                 'bet_full': var_es_se(L_bet), 'bet_w500': var_es_se(L_bet[-500:])}
    OUT['se_theory'] = {'n500': se_theory(n=500), 'n6670': se_theory(n=6670), 'n6714': se_theory(n=6714)}
    OUT['ru'] = ru_check(L_sp, 0.025)
    OUT['agg'] = aggregation()
    print('aggregation', OUT['agg'])
    OUT['ei_sp'] = extremal_index(L_sp)
    OUT['ei_bet'] = extremal_index(L_bet)
    OUT['gev'] = gev_theta(OUT['ei_sp']['theta'])
    print('EI', OUT['ei_sp'], OUT['ei_bet'], OUT['gev'])
    fhs_sp = pd.read_csv(os.path.join(HERE, 'ch7_rolling_sp500.csv'), index_col=0, parse_dates=True)
    OUT['caviar_sp'], v_sp = caviar_study('sp500', fhs=fhs_sp)
    fig_caviar(v_sp, fhs_sp)
    print('CAViaR', OUT['caviar_sp'])
    r_bet = 100 * log_returns('bet')
    fhs_bet = rolling_conditional(r_bet, 2016)
    OUT['caviar_bet'], v_bet = caviar_study('bet', fhs=fhs_bet)
    print('CAViaR BET', OUT['caviar_bet'])
    OUT['fhs_boot_sp'] = fhs_bootstrap(100 * log_returns('sp500'))
    print('boot sp', OUT['fhs_boot_sp'])
    OUT['fhs_boot_btc'] = fhs_bootstrap(100 * log_returns('btc'))
    print('boot btc', OUT['fhs_boot_btc'])
    with open(os.path.join(HERE, 'ch7_inference.json'), 'w') as f:
        json.dump(jsonable(OUT), f, indent=1)
    print('saved ch7_inference.json')

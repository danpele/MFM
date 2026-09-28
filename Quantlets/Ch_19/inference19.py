"""
inference19.py -- Inferenta de nivel master pentru studiul de caz si seminarul Capitolului 19 (MFM)
==================================================================================================
  * hill / hill_ci              -- indicele de coada Hill pe pierderi, CI asimptotic si CI bootstrap pe blocuri
                                   (kurtosis-ul de selectie nu este consistent cand alpha < 4: Athreya, 1987)
  * garch_t_nll / profile_pers  -- CI prin verosimilitatea profil pentru persistenta alpha + beta a GARCH(1,1)-t,
                                   restrans la regiunea stationara (Andrews, 1999)
  * dq_test                     -- testul Dynamic Quantile (Engle & Manganelli, 2004)
  * fz0 / dm_test / mcs         -- scorul FZ0 pentru (VaR, ES) (Patton, Ziegel & Chen, 2019), teste Diebold-Mariano
                                   cu erori HAC, setul de modele de incredere (Hansen, Lunde & Nason, 2011)
  * comparative_backtest        -- backtest comparativ pentru ES cu trei zone (Nolde & Ziegel, 2017)
  * kupiec_power / kupiec_mde   -- puterea exacta (binomiala) a testului Kupiec si efectul minim detectabil
  * sup_wald_break              -- ruptura cu data necunoscuta (Andrews, 1993), valori p prin simularea limitei

Conventie: pierderea L = -r (in %); VaR si ES pozitive; alpha = probabilitatea cozii.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize
import statsmodels.api as sm


# =============================================================================
# 1. INDICELE DE COADA HILL
# =============================================================================
def hill(losses, k):
    """Estimatorul Hill al indicelui de coada din cele mai mari k pierderi (pozitive)."""
    x = np.sort(np.asarray(losses)[np.asarray(losses) > 0])[::-1]
    return 1.0 / np.mean(np.log(x[:k]) - np.log(x[k]))


def hill_k(r, share=0.05):
    """k = 5% din zilele cu pierdere (aceeasi regula ca in Capitolul 16)."""
    return int(round(share * np.sum(-np.asarray(r) > 0)))


def hill_ci(r, share=0.05, B=999, block=20, seed=0):
    """Hill pe pierderi, CI asimptotic i.i.d. alpha(1 +/- 1.96/sqrt(k)) si CI bootstrap pe blocuri mobile."""
    L = -np.asarray(r)
    k = hill_k(r, share)
    a = hill(L, k)
    rng = np.random.default_rng(seed)
    T = len(L)
    nb = int(np.ceil(T / block))
    bs = np.array([hill(L[(rng.integers(0, T - block, nb)[:, None] + np.arange(block)).ravel()[:T]], k)
                   for _ in range(B)])
    return dict(alpha=a, k=k, se_iid=a / np.sqrt(k), lo_iid=a - 1.96 * a / np.sqrt(k), hi_iid=a + 1.96 * a / np.sqrt(k),
                lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5), se_boot=bs.std(ddof=1), draws=bs)


# =============================================================================
# 2. GARCH(1,1)-t: CI PRIN VEROSIMILITATEA PROFIL PENTRU PERSISTENTA
# =============================================================================
def garch_t_nll(theta, r):
    """-log L pentru GARCH(1,1) cu inovatii Student-t standardizate; theta = (mu, omega, alpha, beta, nu)."""
    mu, om, a, b, nu = theta
    if om <= 0 or a < 0 or b < 0 or a + b >= 1 or nu <= 2.05:
        return 1e10
    e = r - mu
    T = len(e)
    s2 = np.empty(T)
    s2[0] = np.var(e)
    for t in range(1, T):
        s2[t] = om + a * e[t - 1] ** 2 + b * s2[t - 1]
    c = (stats.t.logpdf(e / np.sqrt(s2 * (nu - 2) / nu), nu) - 0.5 * np.log(s2 * (nu - 2) / nu))
    return -np.sum(c)


def profile_pers(r, grid, x0):
    """Maximul verosimilitatii cu persistenta fixata p = alpha + beta (reparametrizare alpha = p*s, beta = p*(1-s))."""
    r = np.asarray(r)
    out = []
    for p in grid:
        def f(th):
            mu, om, s, nu = th
            if not 0 < s < 1:
                return 1e10
            return garch_t_nll((mu, om, p * s, p * (1 - s), nu), r)
        best = optimize.minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-6, 'fatol': 1e-3, 'maxiter': 4000})
        out.append(-best.fun)
        x0 = best.x
    return np.array(out)


def profile_ci(r, res):
    """CI 95% {p < 1 : 2(l_max - l(p)) <= 3.84}; l_max din estimarea nerestrictionata."""
    p = res.params
    pers = p['alpha[1]'] + p['beta[1]']
    lmax = -garch_t_nll((p['mu'], p['omega'], p['alpha[1]'], p['beta[1]'], p['nu']), np.asarray(r))
    x0 = np.array([p['mu'], p['omega'], p['alpha[1]'] / pers, p['nu']])
    grid = np.unique(np.concatenate([np.linspace(0.960, 0.998, 39), [0.999, 0.9995, 0.9999, pers]]))
    lp = profile_pers(r, grid, x0)
    lr = 2 * (max(lmax, lp.max()) - lp)
    ok = grid[lr <= stats.chi2.ppf(0.95, 1)]
    return dict(pers=pers, lmax=lmax, lo=ok.min(), hi=ok.max(), grid=list(grid), lr=list(lr),
                hl_lo=np.log(0.5) / np.log(ok.min()), hl_hi=np.log(0.5) / np.log(ok.max()),
                hi_at_edge=bool(ok.max() >= grid.max()))


# =============================================================================
# 3. TESTE PENTRU PROGNOZELE DE RISC
# =============================================================================
def dq_test(L, var, a=0.01, lags=4):
    """Dynamic Quantile (Engle & Manganelli, 2004): Hit_t - a pe constanta, lags depasiri si VaR_t; DQ ~ chi2(lags+2)."""
    hit = (np.asarray(L) > np.asarray(var)).astype(float) - a
    X = [np.ones(len(hit))] + [np.roll(hit, l) for l in range(1, lags + 1)] + [np.asarray(var)]
    X = np.column_stack(X)[lags:]
    y = hit[lags:]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    dq = b @ X.T @ X @ b / (a * (1 - a))
    return dict(DQ=dq, df=X.shape[1], p=stats.chi2.sf(dq, X.shape[1]))


def fz0(r, var, es, a):
    """Scorul FZ0 (Patton, Ziegel & Chen, 2019) pentru v = -VaR, e = -ES (cuantile negative), randamentul r."""
    v, e, y = -np.asarray(var), -np.asarray(es), np.asarray(r)
    return -((y <= v) * (v - y)) / (a * e) + v / e + np.log(-e) - 1


def nw_var(d, lags=None):
    d = np.asarray(d) - np.mean(d)
    T = len(d)
    lags = int(np.floor(4 * (T / 100) ** (2 / 9))) if lags is None else lags
    v = d @ d / T
    for l in range(1, lags + 1):
        v += 2 * (1 - l / (lags + 1)) * (d[l:] @ d[:-l]) / T
    return v, lags


def dm_test(l1, l2):
    """Diebold-Mariano: d = l1 - l2; t = mean(d)/sqrt(HAC var/T); d < 0 => modelul 1 mai bun."""
    d = np.asarray(l1) - np.asarray(l2)
    v, lags = nw_var(d)
    t = d.mean() / np.sqrt(v / len(d))
    return dict(mean=d.mean(), t=t, p=2 * stats.norm.sf(abs(t)), lags=lags)


def mcs(losses, B=999, block=20, alpha=0.10, seed=0):
    """Setul de modele de incredere (Hansen, Lunde & Nason, 2011), statistica T_max, bootstrap pe blocuri mobile.
    losses: DataFrame T x m. Intoarce valorile p MCS pentru fiecare model."""
    rng = np.random.default_rng(seed)
    L = losses.values
    T, m = L.shape
    nb = int(np.ceil(T / block))
    idx = [(rng.integers(0, T - block, nb)[:, None] + np.arange(block)).ravel()[:T] for _ in range(B)]
    alive = list(range(m))
    pvals = {}
    pmax = 0.0
    while len(alive) > 1:
        Lm = L[:, alive]
        dbar = Lm.mean(0) - Lm.mean()                       # d_i. = L_i - media modelelor ramase
        boot = np.array([Lm[ix].mean(0) - Lm[ix].mean() for ix in idx])
        se = np.sqrt(((boot - dbar) ** 2).mean(0))
        t = dbar / se
        tmax = t.max()
        tb = ((boot - dbar) / se).max(1)
        p = float((tb >= tmax).mean())
        pmax = max(pmax, p)
        worst = alive[int(np.argmax(t))]
        pvals[losses.columns[worst]] = pmax
        alive.remove(worst)
    pvals[losses.columns[alive[0]]] = 1.0
    return {k: pvals[k] for k in losses.columns}, [c for c in losses.columns if pvals[c] >= alpha]


def comparative_backtest(s_int, s_std, level=0.05):
    """Backtest comparativ (Nolde & Ziegel, 2017) cu scoruri FZ0: d = S(intern) - S(standard).
    Rosu: se respinge H0-, 'intern cel putin la fel de bun' (d > 0 semnificativ);
    verde: se respinge H0+, 'intern cel mult la fel de bun' (d < 0 semnificativ); altfel galben."""
    t = dm_test(s_int, s_std)['t']
    z = stats.norm.ppf(1 - level)
    zone = 'red' if t > z else ('green' if t < -z else 'yellow')
    return dict(t=t, zone=zone)


def holm(p):
    """Valori p ajustate Holm (FWER)."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    m = len(p)
    adj = np.minimum(np.maximum.accumulate((m - np.arange(m)) * p[o]), 1)
    out = np.empty(m)
    out[o] = adj
    return out


def bh(p, q=0.05):
    """Benjamini-Hochberg: masca respingerilor la FDR q."""
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    ok = p[o] <= q * np.arange(1, m + 1) / m
    k = np.max(np.nonzero(ok)[0]) + 1 if ok.any() else 0
    rej = np.zeros(m, bool)
    rej[o[:k]] = True
    return rej


# =============================================================================
# 4. PUTEREA TESTULUI KUPIEC
# =============================================================================
def kupiec_region(T, p0=0.01, level=0.05):
    """Numerele de depasiri x pentru care LR_uc respinge la nivelul dat."""
    xs = np.arange(0, T + 1)
    ph = xs / T
    with np.errstate(divide='ignore', invalid='ignore'):
        ll1 = np.where(xs > 0, xs * np.log(np.where(ph > 0, ph, 1)), 0) + \
            np.where(xs < T, (T - xs) * np.log(np.where(ph < 1, 1 - ph, 1)), 0)
    ll0 = xs * np.log(p0) + (T - xs) * np.log(1 - p0)
    lr = -2 * (ll0 - ll1)
    return xs[lr > stats.chi2.ppf(1 - level, 1)]


def kupiec_power(T, p1, p0=0.01, level=0.05):
    rej = kupiec_region(T, p0, level)
    return float(stats.binom.pmf(rej, T, p1).sum()), rej


def kupiec_mde(T, p0=0.01, power=0.80, level=0.05):
    """Cea mai mica rata adevarata > p0 detectata cu puterea ceruta."""
    for p1 in np.arange(p0 + 0.0005, 0.2, 0.0005):
        if kupiec_power(T, p1, p0, level)[0] >= power:
            return float(p1)
    return np.nan


# =============================================================================
# 5. RUPTURA CU DATA NECUNOSCUTA
# =============================================================================
def sup_wald_break(y, trim=0.15, nsim=2000, seed=0, hac=True):
    """Test sup-Wald (Andrews, 1993) pentru o ruptura in media lui y la o data necunoscuta, erori HAC;
    valoarea p prin simularea limitei sup_pi B(pi)^2/(pi(1-pi)) (punte browniana)."""
    y = np.asarray(y, float)
    T = len(y)
    lo, hi = int(np.floor(trim * T)), int(np.ceil((1 - trim) * T))
    best = (-np.inf, None)
    v, _ = nw_var(y - y.mean()) if hac else (np.var(y), 0)
    cs = np.cumsum(y)
    ybar = y.mean()
    for k in range(lo, hi):
        m1, m2 = cs[k - 1] / k, (cs[-1] - cs[k - 1]) / (T - k)
        w = (m2 - m1) ** 2 / (v * (1 / k + 1 / (T - k)))
        if w > best[0]:
            best = (w, k)
    rng = np.random.default_rng(seed)
    n = 2000
    grid = np.arange(int(trim * n), int((1 - trim) * n))
    sims = []
    for _ in range(nsim):
        W = np.cumsum(rng.standard_normal(n)) / np.sqrt(n)
        pi = grid / n
        Bb = W[grid - 1] - pi * W[-1]
        sims.append(np.max(Bb ** 2 / (pi * (1 - pi))))
    sims = np.array(sims)
    return dict(stat=best[0], k=best[1], p=float((sims >= best[0]).mean()), cv5=float(np.percentile(sims, 95)))


# =============================================================================
# 6. EVALUAREA FORMALA A CELOR PATRU MODELE (studiul de caz)
# =============================================================================
def formal_eval(fc, models=('HS', 'Normal', 'GARCH-t', 'FHS'), a=0.01, a_es=0.025, standard='HS'):
    """DQ la VaR 1%; FZ0 la nivelul 2.5% pentru perechea (VaR 2.5%, ES 2.5%); DM pe perechi; MCS; backtest comparativ."""
    out = {'dq': {}, 'fz0': {}, 'dm': {}, 'cb': {}}
    S = {}
    for m in models:
        out['dq'][m] = dq_test(fc['L'], fc[m], a)
        S[m] = fz0(fc['r'], fc[m + '_V25'], fc[m + '_ES'], a_es)
        out['fz0'][m] = float(np.mean(S[m]))
    for i, m1 in enumerate(models):
        for m2 in models[i + 1:]:
            out['dm'][f'{m1}|{m2}'] = dm_test(S[m1], S[m2])
    p, keep = mcs(pd.DataFrame(S))
    out['mcs_p'], out['mcs_set'] = p, keep
    for m in models:
        if m != standard:
            out['cb'][m] = comparative_backtest(S[m], S[standard])
    out['T'] = len(fc)
    return out

"""
case_study.py -- Studiul de caz integrat al Capitolului 19 (MFM)
================================================================
Un singur fir, pe o singura serie: fapte stilizate (Cap. 1) -> GARCH(1,1)-t (Cap. 5)
-> VaR 1% si ES 2.5% pentru ziua urmatoare (Cap. 7) -> backtesting (Cap. 8).

  * stylised_facts(r)        -- momente, testele Jarque-Bera si Ljung-Box pe r si r^2, ACF
  * garch_t_fit(r)           -- GARCH(1,1) cu inovatii Student-t (medie constanta), r in %
  * rolling_var(r, ...)      -- prognoze VaR 1% (si ES 2.5%) pentru ziua urmatoare, fereastra mobila,
                                patru modele: HS, Normal, GARCH-t, FHS (simulare istorica filtrata)
  * kupiec / christoffersen  -- testele de acoperire si de independenta ale depasirilor
  * traffic_light            -- zonele Basel pentru x depasiri in 250 de zile

Conventie: alpha = probabilitatea cozii (VaR 1%); pierderea L = -r; VaR si ES sunt pozitive, in % din pozitie.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
from scipy import stats
from arch import arch_model

ALPHA = 0.01          # VaR 1%
ALPHA_ES = 0.025      # ES 2.5%
WINDOW = 1000         # zile in fereastra de estimare
REFIT = 21            # reestimare GARCH la fiecare 21 de zile
HS_WINDOW = 500       # fereastra pentru HS si pentru distributia Normala
MODELS = ['HS', 'Normal', 'GARCH-t', 'FHS']


# -----------------------------------------------------------------------------
# 1. FAPTE STILIZATE
# -----------------------------------------------------------------------------
def ljung_box(x, m=10):
    """Q(m) = T(T+2) sum rho_k^2/(T-k) si p-valoarea chi2(m)."""
    x = np.asarray(x) - np.mean(x)
    T = len(x)
    rho = np.array([np.sum(x[k:] * x[:-k]) for k in range(1, m + 1)]) / np.sum(x ** 2)
    q = T * (T + 2) * np.sum(rho ** 2 / (T - np.arange(1, m + 1)))
    return q, stats.chi2.sf(q, m)


def acf(x, nlags):
    x = np.asarray(x) - np.mean(x)
    d = np.sum(x ** 2)
    return np.array([np.sum(x[k:] * x[:-k]) / d for k in range(1, nlags + 1)])


def stylised_facts(r):
    """Rezumatul faptelor stilizate pentru randamentele r (in %)."""
    jb, jbp = stats.jarque_bera(r)
    q_r, q_rp = ljung_box(r)
    q_r2, q_r2p = ljung_box(r ** 2)
    z = (r - r.mean()) / r.std()
    return dict(N=len(r), start=str(r.index[0].date()), end=str(r.index[-1].date()),
                mean=r.mean(), sd=r.std(), skew=stats.skew(r), kurt=stats.kurtosis(r),
                min=r.min(), min_date=str(r.idxmin().date()), max=r.max(),
                jb=jb, jb_p=jbp, q_r=q_r, q_r_p=q_rp, q_r2=q_r2, q_r2_p=q_r2p,
                acf1_r=acf(r, 1)[0], acf1_abs=acf(np.abs(r), 1)[0],
                n4=int(np.sum(np.abs(z) > 4)), n4_normal=len(r) * 2 * stats.norm.sf(4))


def kurtosis_boot_ci(r, B=2000, block=20, seed=0):
    """CI 95% pentru excesul de kurtosis prin bootstrap pe blocuri mobile (pastreaza gruparea volatilitatii)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(r)
    T = len(x)
    nb = int(np.ceil(T / block))
    ks = []
    for _ in range(B):
        idx = (rng.integers(0, T - block, nb)[:, None] + np.arange(block)).ravel()[:T]
        ks.append(stats.kurtosis(x[idx]))
    return np.percentile(ks, [2.5, 97.5])


# -----------------------------------------------------------------------------
# 2. GARCH(1,1)-t
# -----------------------------------------------------------------------------
def garch_t_fit(r, last_obs=None):
    am = arch_model(r, mean='Constant', vol='GARCH', p=1, q=1, dist='t', rescale=False)
    return am.fit(disp='off', last_obs=last_obs)


def garch_summary(res):
    """Parametri, erori standard robuste, persistenta si timpul de injumatatire."""
    p, se = res.params, res.std_err
    pers = p['alpha[1]'] + p['beta[1]']
    return dict(mu=p['mu'], omega=p['omega'], alpha=p['alpha[1]'], beta=p['beta[1]'], nu=p['nu'],
                se_alpha=se['alpha[1]'], se_beta=se['beta[1]'], se_nu=se['nu'],
                pers=pers, half_life=np.log(0.5) / np.log(pers),
                uncond_vol=np.sqrt(252 * p['omega'] / (1 - pers)))


def t_std_q(nu, a):
    """Cuantila de ordin a a distributiei Student-t standardizate (varianta 1)."""
    return stats.t.ppf(a, nu) * np.sqrt((nu - 2) / nu)


def t_std_es(nu, a):
    """E[Z | Z <= q_a] pentru Student-t standardizata (negativ)."""
    q = stats.t.ppf(a, nu)
    return -(stats.t.pdf(q, nu) / a) * (nu + q ** 2) / (nu - 1) * np.sqrt((nu - 2) / nu)


# -----------------------------------------------------------------------------
# 3. PROGNOZE VaR 1% PENTRU ZIUA URMATOARE (fereastra mobila)
# -----------------------------------------------------------------------------
def rolling_var(r, eval_from, window=WINDOW, refit=REFIT, a=ALPHA, a_es=ALPHA_ES):
    """Prognoze VaR (nivel a) si ES (nivel a_es) pentru fiecare zi t >= eval_from, cu informatia pana la t-1.
    Intoarce un DataFrame cu pierderea L_t si VaR/ES pentru HS, Normal, GARCH-t si FHS."""
    r = r.dropna()
    idx = r.index
    start = idx.searchsorted(pd.Timestamp(eval_from))
    start = max(start, window)
    rows = []
    for b0 in range(start, len(r), refit):
        b1 = min(b0 + refit, len(r))
        est = r.iloc[b0 - window:b0]
        am = arch_model(r.iloc[b0 - window:b1], mean='Constant', vol='GARCH', p=1, q=1, dist='t', rescale=False)
        res = am.fit(disp='off', last_obs=window)
        fx = am.fix(res.params)
        sig = fx.conditional_volatility          # sigma_t foloseste informatia pana la t-1
        mu = res.params['mu']
        nu = res.params['nu']
        z = ((est - mu) / sig.iloc[:window]).values   # reziduuri standardizate din fereastra
        zq = np.quantile(z, a)
        zq_es = np.quantile(z, a_es)
        zes = z[z <= zq_es].mean()
        for j in range(b0, b1):
            hist = r.iloc[j - HS_WINDOW:j].values
            s = sig.iloc[j - (b0 - window)]
            L_hist = -hist
            q_hs = np.quantile(L_hist, 1 - a)
            q_hs_es = np.quantile(L_hist, 1 - a_es)
            m, sd = hist.mean(), hist.std(ddof=1)
            rows.append(dict(date=idx[j], r=r.iloc[j], L=-r.iloc[j], sigma=s,
                             HS=q_hs, HS_ES=L_hist[L_hist >= q_hs_es].mean(),
                             Normal=-(m + sd * stats.norm.ppf(a)),
                             Normal_ES=-(m - sd * stats.norm.pdf(stats.norm.ppf(a_es)) / a_es),
                             **{'GARCH-t': -(mu + s * t_std_q(nu, a)),
                                'GARCH-t_ES': -(mu + s * t_std_es(nu, a_es))},
                             FHS=-(mu + s * zq), FHS_ES=-(mu + s * zes),
                             # VaR la nivelul ES (2.5%): perechea (VaR, ES) la acelasi nivel, pentru scorul FZ0
                             HS_V25=q_hs_es, Normal_V25=-(m + sd * stats.norm.ppf(a_es)),
                             **{'GARCH-t_V25': -(mu + s * t_std_q(nu, a_es))}, FHS_V25=-(mu + s * zq_es)))
    return pd.DataFrame(rows).set_index('date')


# -----------------------------------------------------------------------------
# 4. BACKTESTING
# -----------------------------------------------------------------------------
def kupiec(hits, p=ALPHA):
    """Testul de acoperire (POF) al lui Kupiec: LR_uc ~ chi2(1)."""
    hits = np.asarray(hits, int)
    T, x = len(hits), int(hits.sum())
    ph = x / T
    ll0 = (T - x) * np.log(1 - p) + x * np.log(p)
    ll1 = (T - x) * np.log(1 - ph) + x * np.log(ph) if 0 < x < T else 0.0
    lr = -2 * (ll0 - ll1)
    return dict(T=T, x=x, rate=ph, LR=lr, p=stats.chi2.sf(lr, 1))


def christoffersen(hits, p=ALPHA):
    """Testul de independenta (lant Markov de ordinul 1) si testul combinat LR_cc = LR_uc + LR_ind."""
    h = np.asarray(hits, int)
    a, b = h[:-1], h[1:]
    n00, n01 = np.sum((a == 0) & (b == 0)), np.sum((a == 0) & (b == 1))
    n10, n11 = np.sum((a == 1) & (b == 0)), np.sum((a == 1) & (b == 1))

    def xlogy(n, q):
        return n * np.log(q) if n > 0 else 0.0
    pi01 = n01 / (n00 + n01)
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    l1 = xlogy(n00, 1 - pi01) + xlogy(n01, pi01) + xlogy(n10, 1 - pi11) + xlogy(n11, pi11)
    l0 = xlogy(n00 + n10, 1 - pi) + xlogy(n01 + n11, pi)
    lr_ind = -2 * (l0 - l1)
    lr_uc = kupiec(h, p)['LR']
    return dict(n11=int(n11), pi01=pi01, pi11=pi11, LR_ind=lr_ind, p_ind=stats.chi2.sf(lr_ind, 1),
                LR_cc=lr_uc + lr_ind, p_cc=stats.chi2.sf(lr_uc + lr_ind, 2))


def traffic_light(x, T=250, p=ALPHA):
    """Zona Basel pentru x depasiri in T zile: verde (<5), galben (5-9), rosu (>=10) la T=250, p=1%."""
    cum = stats.binom.cdf(x, T, p)
    return 'green' if cum < 0.95 else ('yellow' if cum < 0.9999 else 'red')


def backtest_table(fc, models=MODELS, a=ALPHA):
    out = {}
    for m in models:
        hits = (fc['L'] > fc[m]).astype(int)
        k, c = kupiec(hits, a), christoffersen(hits, a)
        roll = hits.rolling(250).sum().dropna()
        zones = roll.apply(lambda x: traffic_light(int(x)))
        out[m] = dict(T=k['T'], x=k['x'], rate=k['rate'], LR_uc=k['LR'], p_uc=k['p'],
                      LR_ind=c['LR_ind'], p_ind=c['p_ind'], p_cc=c['p_cc'], n11=c['n11'],
                      share_red=float((zones == 'red').mean()), share_yellow=float((zones == 'yellow').mean()),
                      mean_var=float(fc[m].mean()))
    return out


def binom_band(T, p=ALPHA, level=0.95):
    """Intervalul binomial central pentru rata depasirilor, sub H0: rata = p."""
    lo, hi = stats.binom.ppf([(1 - level) / 2, 1 - (1 - level) / 2], T, p)
    return lo / T, hi / T

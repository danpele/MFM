"""
systemic.py -- Masurile de risc sistemic din Capitolul 18 (MFM)
===============================================================
  * mes / lrmes / srisk_ratio   -- Marginal Expected Shortfall, pierderea pe termen lung, SRISK pe unitate de capital
  * covar_static / covar_dynamic -- CoVaR si Delta-CoVaR prin regresie cuantila (Adrian & Brunnermeier)
  * block_bootstrap_idx          -- indici pentru bootstrap pe blocuri mobile
  * var_fit / gfevd / spillover_table -- conectivitatea Diebold-Yilmaz (VAR + descompunerea generalizata a dispersiei)
  * lasso_qr_gacv                -- regresie cuantila penalizata L1 cu lambda ales prin GACV (Financial Risk Meter)

Conventii: randamente log zilnice in %; X = randament, pierderea L = -X; nivelul alpha = probabilitatea cozii.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from sklearn.linear_model import QuantileRegressor
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# MES, LRMES, SRISK
# =============================================================================
def mes(r_i, r_m, alpha=0.05):
    """MES (%): pierderea medie a bancii in zilele in care piata este in coada de probabilitate alpha."""
    q = np.quantile(r_m, alpha)
    return -np.mean(np.asarray(r_i)[np.asarray(r_m) <= q])


def mes_threshold(r_i, r_m, c=-2.0):
    """MES (%) in zilele in care piata scade cu mai mult de |c|% (definitia folosita pentru LRMES)."""
    return -np.mean(np.asarray(r_i)[np.asarray(r_m) < c])


def lrmes(mes2_pct):
    """Pierderea pe termen lung intr-o criza (piata -40% in sase luni): LRMES = 1 - exp(-18 MES), MES in fractii."""
    return 1 - np.exp(-18 * mes2_pct / 100)


def srisk_ratio(lrm, leverage, k=0.08):
    """SRISK / capitalul de piata W: k(L - 1) - (1 - k)(1 - LRMES), cu L = (D + W)/W."""
    return k * (leverage - 1) - (1 - k) * (1 - lrm)


def breakeven_leverage(lrm, k=0.08):
    """Levierul L* peste care SRISK > 0: L* = 1 + (1 - k)(1 - LRMES)/k."""
    return 1 + (1 - k) * (1 - lrm) / k


# =============================================================================
# CoVaR
# =============================================================================
def qreg(y, X, q):
    """Regresie cuantila (Koenker-Bassett); intoarce coeficientii [termen liber, pante]."""
    return QuantReg(np.asarray(y), sm.add_constant(np.asarray(X), has_constant='add')).fit(q=q, max_iter=5000).params


def covar_static(x_sys, x_i, alpha=0.01):
    """CoVaR si Delta-CoVaR necondiționate (%, pozitive = pierderi).

    Regresia cuantila la nivelul alpha: X_sys = a + b X_i;
    CoVaR_alpha = -(a + b q_alpha(X_i)); Delta-CoVaR = b (q_50(X_i) - q_alpha(X_i))."""
    x_sys, x_i = np.asarray(x_sys), np.asarray(x_i)
    a, b = qreg(x_sys, x_i, alpha)
    qa, qm = np.quantile(x_i, alpha), np.quantile(x_i, 0.5)
    return {'a': a, 'b': b, 'var_i': -qa, 'covar': -(a + b * qa), 'covar_med': -(a + b * qm),
            'dcovar': b * (qm - qa), 'var_sys': -np.quantile(x_sys, alpha)}


def block_bootstrap_idx(n, block=20, rng=None):
    """Indici pentru bootstrap pe blocuri mobile (Künsch), blocuri de lungime fixa."""
    rng = rng or np.random.default_rng(0)
    starts = rng.integers(0, n - block + 1, size=int(np.ceil(n / block)))
    return (starts[:, None] + np.arange(block)[None, :]).ravel()[:n]


def covar_boot(x_sys, x_i, alpha=0.01, B=200, block=20, seed=0):
    """Interval percentil de 95% pentru Delta-CoVaR prin bootstrap pe blocuri mobile."""
    x_sys, x_i = np.asarray(x_sys), np.asarray(x_i)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        idx = block_bootstrap_idx(len(x_i), block, rng)
        d.append(covar_static(x_sys[idx], x_i[idx], alpha)['dcovar'])
    return np.percentile(d, [2.5, 97.5])


def covar_dynamic(x_sys, x_i, M, alpha=0.01):
    """Delta-CoVaR variabil in timp cu variabile de stare M_{t-1} (Adrian & Brunnermeier, 2016).

    X_i,t = a + c'M_{t-1} la nivelurile alpha si 50%  ->  VaR_i,t;
    X_sys,t = a + b X_i,t + c'M_{t-1} la nivelul alpha  ->  Delta-CoVaR_t = b (q50_i,t - qalpha_i,t)."""
    ci_a = qreg(x_i, M, alpha)
    ci_m = qreg(x_i, M, 0.5)
    cs = qreg(x_sys, np.column_stack([x_i, M]), alpha)
    Mc = sm.add_constant(np.asarray(M), has_constant='add')
    qa, qm = Mc @ ci_a, Mc @ ci_m
    return pd.DataFrame({'var_i': -qa, 'dcovar': cs[1] * (qm - qa)}, index=getattr(x_i, 'index', None)), cs[1]


# =============================================================================
# Diebold-Yilmaz
# =============================================================================
def var_fit(Y, p):
    """VAR(p) estimat prin OLS; intoarce coeficientii A_1..A_p (k x k) si matricea de covarianta a reziduurilor."""
    Y = np.asarray(Y, float)
    T, k = Y.shape
    X = np.hstack([np.ones((T - p, 1))] + [Y[p - l - 1:T - l - 1] for l in range(p)])
    Yt = Y[p:]
    B = np.linalg.lstsq(X, Yt, rcond=None)[0]
    E = Yt - X @ B
    S = E.T @ E / (len(Yt) - X.shape[1])
    A = [B[1 + l * k:1 + (l + 1) * k].T for l in range(p)]
    return A, S


def var_bic(Y, pmax=5):
    """Ordinul VAR ales prin criteriul BIC."""
    Y = np.asarray(Y, float)
    T, k = Y.shape
    best = None
    for p in range(1, pmax + 1):
        A, S = var_fit(Y[pmax - p:], p)
        n = T - pmax
        bic = np.log(np.linalg.det(S)) + np.log(n) * p * k * k / n
        if best is None or bic < best[1]:
            best = (p, bic)
    return best[0]


def ma_coefs(A, H):
    """Coeficientii reprezentarii medie mobila Phi_0..Phi_{H-1}."""
    k = A[0].shape[0]
    Phi = [np.eye(k)]
    for h in range(1, H):
        Phi.append(sum(A[l] @ Phi[h - l - 1] for l in range(min(h, len(A)))))
    return Phi


def gfevd(A, S, H=10):
    """Descompunerea generalizata a dispersiei erorii de prognoza (Pesaran-Shin), normalizata pe linii."""
    Phi = ma_coefs(A, H)
    k = S.shape[0]
    num = np.zeros((k, k))
    den = np.zeros(k)
    for P in Phi:
        PS = P @ S
        num += PS ** 2
        den += np.diag(P @ S @ P.T)
    theta = num / np.diag(S)[None, :] / den[:, None]
    return theta / theta.sum(axis=1, keepdims=True)


def spillover_table(theta, names):
    """Tabelul de conectivitate: contributii (%), FROM, TO, NET si indicele total."""
    k = theta.shape[0]
    D = 100 * theta
    off = D - np.diag(np.diag(D))
    frm, to = off.sum(axis=1), off.sum(axis=0)
    tab = pd.DataFrame(D, index=names, columns=names)
    return {'table': tab, 'from': pd.Series(frm, index=names), 'to': pd.Series(to, index=names),
            'net': pd.Series(to - frm, index=names), 'total': off.sum() / k,
            'pairwise_net': pd.DataFrame(off.T - off, index=names, columns=names)}


def rolling_total(Y, window=250, step=5, p=2, H=10):
    """Indicele total de conectivitate pe ferestre mobile."""
    Y = pd.DataFrame(Y)
    out, frm_to = {}, {}
    for end in range(window, len(Y) + 1, step):
        w = Y.iloc[end - window:end]
        A, S = var_fit(w.values, p)
        st = spillover_table(gfevd(A, S, H), list(Y.columns))
        out[Y.index[end - 1]] = st['total']
        frm_to[Y.index[end - 1]] = st['net']
    return pd.Series(out), pd.DataFrame(frm_to).T


# =============================================================================
# Financial Risk Meter
# =============================================================================
def check_loss(u, tau):
    return u * (tau - (u < 0))


def lasso_qr_gacv(y, X, tau=0.05, lambdas=None):
    """Regresie cuantila penalizata L1; lambda ales prin GACV = sum rho_tau(rez) / (n - df)."""
    y, X = np.asarray(y, float), np.asarray(X, float)
    n = len(y)
    lambdas = np.logspace(-4, -0.5, 15) if lambdas is None else lambdas
    rows = []
    for lam in lambdas:
        m = QuantileRegressor(quantile=tau, alpha=lam, solver='highs').fit(X, y)
        res = y - m.predict(X)
        df = int(np.sum(np.abs(m.coef_) > 1e-8))
        g = check_loss(res, tau).sum() / max(n - df, 1)
        rows.append((lam, g, df, m.coef_.copy()))
    i = int(np.argmin([r[1] for r in rows]))
    return {'lambda': rows[i][0], 'gacv': [r[1] for r in rows], 'df': [r[2] for r in rows],
            'lambdas': list(lambdas), 'coef': rows[i][3], 'df_sel': rows[i][2]}

"""
Generator pentru graficele din Capitolul 4: Optimizarea portofoliului
=====================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date: ETF-uri sectoriale SUA, ETF-uri multi-active (actiuni, obligatiuni, credit, aur),
actiuni BVB, indicii BET si BET-TR (data/market); rata fara risc lunara
(Kenneth French Data Library); cursul USD/RON (BNR).
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
from scipy.cluster.hierarchy import linkage, leaves_list, dendrogram
from scipy.spatial.distance import pdist
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import (read_market, prices, price, log_returns, french_rf, monthly_returns, bnr_rate,
                      SECTORS, SECTOR_NAMES, MULTI, MULTI_NAMES, BVB, BVB_NAMES)

# Stil standard MFM (identic cu SFM): transparent + ENG + legenda jos
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.1
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

# Culori brand
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Gray     = '#7F7F7F'
LightGray = '#DADADA'
PALETTE = [MainBlue, IDAred, Forest, Amber, Orange, Purple, Crimson, '#795548', '#17A2B8', '#6F42C1', '#20C997']
EWcol    = '#D63384'   # culoarea portofoliului 1/N (niciodata gri pentru serii)

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42
MAX_ABS_RET = 0.5        # prag pentru erori de date in seriile BVB (log-randament zilnic)
US_END = '2026-07-31'    # ultima luna cu rata fara risc publicata
BVB_END = '2026-08-31'   # ultima luna completa
WINDOW = 60              # fereastra de estimare (luni)
STRATS = ['1/N', 'MV', 'MV-LO', 'GMV', 'GMV-LO', 'GMV-LW', 'ERC', 'HRP']
SCOL = {'1/N': EWcol, 'MV': IDAred, 'MV-LO': Orange, 'GMV': Amber, 'GMV-LO': Purple,
        'GMV-LW': MainBlue, 'ERC': Forest, 'HRP': '#17A2B8'}


def save_fig(name):
    """Salveaza figura ca PDF si PNG transparent."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Plaseaza legenda in afara graficului, jos-centru."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


# =============================================================================
# DATE COMUNE
# =============================================================================
def us_monthly(symbols, start=None, end=US_END):
    """Randamente lunare simple (totale) si in exces fata de RF, pe lunile comune."""
    r = monthly_returns([s + '.US' for s in symbols]).loc[start:end]
    r.columns = symbols
    rf = french_rf().reindex(r.index)
    ok = rf.notna()
    r, rf = r[ok], rf[ok]
    return r, r.sub(rf, axis=0), rf


def bvb_monthly(symbols=BVB, bench=('BETTR.INDX', 'BET'), end=BVB_END):
    """Randamente lunare BVB (RON) din randamente zilnice filtrate (|r| > 0.5 = eveniment neajustat)."""
    cols = [s + '.RO' for s in symbols] + list(bench)
    p = prices(cols)
    lr = log_returns(p)
    bad = lr.abs() > MAX_ABS_RET
    lr = lr.mask(bad, 0.0)
    m = np.exp(lr.resample('ME').sum()) - 1
    m = m.loc[:end].iloc[1:]                     # prima luna este incompleta
    m.columns = list(symbols) + ['BET-TR' if b.startswith('BETTR') else b for b in bench]
    removed = {c.replace('.RO', ''): [str(d.date()) for d in lr.index[bad[c]]] for c in cols if bad[c].any()}
    return m, removed


# =============================================================================
# ESTIMATORI SI PONDERI
# =============================================================================
def lw_cc(X):
    """Ledoit-Wolf (2004): shrinkage spre tinta cu corelatie constanta. Intoarce (Sigma, delta)."""
    X = np.asarray(X, float)
    T, N = X.shape
    Y = X - X.mean(0)
    S = Y.T @ Y / T
    var = np.diag(S).reshape(-1, 1)
    sd = np.sqrt(var)
    rbar = (np.sum(S / (sd @ sd.T)) - N) / (N * (N - 1))
    F = rbar * (sd @ sd.T)
    np.fill_diagonal(F, np.diag(S))
    Y2 = Y ** 2
    pi_mat = Y2.T @ Y2 / T - S ** 2
    pi_hat = pi_mat.sum()
    gamma_hat = np.linalg.norm(S - F, 'fro') ** 2
    theta = (Y ** 3).T @ Y / T - np.tile(var, (1, N)) * S
    np.fill_diagonal(theta, 0.0)
    rho_hat = np.trace(pi_mat) + rbar * np.sum(((1 / sd) @ sd.T) * theta)
    kappa = (pi_hat - rho_hat) / gamma_hat
    delta = max(0.0, min(1.0, kappa / T))
    return delta * F + (1 - delta) * S, delta


def w_ew(n):
    """Portofoliul 1/N."""
    return np.ones(n) / n


def w_gmv(S):
    """Portofoliul de varianta minima globala: S^-1 1 / 1' S^-1 1."""
    x = np.linalg.solve(S, np.ones(len(S)))
    return x / x.sum()


def w_tan(mu, S):
    """Portofoliul tangent (Sharpe maxim) cu vanzari in lipsa: S^-1 mu / 1' S^-1 mu."""
    x = np.linalg.solve(S, mu)
    return x / x.sum()


def w_long_only(S, mu=None):
    """Varianta minima (mu=None) sau Sharpe maxim cu ponderi 0 <= w <= 1, suma 1 (SLSQP)."""
    n = len(S)
    if mu is None:
        f = lambda w: w @ S @ w
    else:
        f = lambda w: -(w @ mu) / np.sqrt(w @ S @ w)
    res = minimize(f, np.ones(n) / n, method='SLSQP', bounds=[(0, 1)] * n,
                   constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1}],
                   options={'ftol': 1e-12, 'maxiter': 500})
    w = np.clip(res.x, 0, None)
    return w / w.sum()


def w_erc(S):
    """Contributii egale la risc (Maillard, Roncalli, Teiletche 2010): min 0.5 y'Sy - sum(log y)/n."""
    n = len(S)
    b = np.ones(n) / n
    f = lambda y: 0.5 * y @ S @ y - b @ np.log(y)
    grad = lambda y: S @ y - b / y
    y0 = 1 / np.sqrt(np.diag(S))
    res = minimize(f, y0 / y0.sum(), jac=grad, method='L-BFGS-B', bounds=[(1e-12, None)] * n,
                   options={'ftol': 1e-15, 'gtol': 1e-12, 'maxiter': 2000})
    return res.x / res.x.sum()


def hrp_tree(S):
    """Arborele HRP (Lopez de Prado 2016, Stage 1): d_ij = sqrt((1 - rho_ij)/2); apoi distanta euclidiana
    intre coloanele matricei D, d~_ij = sqrt(sum_n (d_ni - d_nj)^2); legatura simpla (single linkage) pe d~."""
    sd = np.sqrt(np.diag(S))
    C = S / np.outer(sd, sd)
    D = np.sqrt(np.clip((1 - C) / 2, 0, None))
    np.fill_diagonal(D, 0)
    return linkage(pdist(D, 'euclidean'), 'single')


def w_hrp(S):
    """Hierarchical Risk Parity (Lopez de Prado 2016): ordonare dupa arbore + bisectie recursiva."""
    S = np.asarray(S)
    order = list(leaves_list(hrp_tree(S)))
    w = np.ones(len(S))

    def cvar(idx):
        s = S[np.ix_(idx, idx)]
        iv = 1 / np.diag(s)
        iv /= iv.sum()
        return iv @ s @ iv

    clusters = [order]
    while clusters:
        nxt = []
        for c in clusters:
            if len(c) < 2:
                continue
            h = len(c) // 2
            a, b = c[:h], c[h:]
            va, vb = cvar(a), cvar(b)
            alpha = 1 - va / (va + vb)
            w[a] *= alpha
            w[b] *= 1 - alpha
            nxt += [a, b]
        clusters = nxt
    return w / w.sum()


def risk_contrib(w, S):
    """Contributiile procentuale la varianta: w_i (S w)_i / w'Sw."""
    w = np.asarray(w)
    return w * (S @ w) / (w @ S @ w)


def weights(name, Rw):
    """Ponderile strategiei `name` estimate pe fereastra Rw (randamente in exces, T x N)."""
    X = np.asarray(Rw, float)
    n = X.shape[1]
    mu = X.mean(0)
    S = np.cov(X.T)
    if name == '1/N':
        return w_ew(n)
    if name == 'MV':
        return w_tan(mu, S)
    if name == 'MV-LO':
        return w_long_only(S, mu)
    if name == 'GMV':
        return w_gmv(S)
    if name == 'GMV-LO':
        return w_long_only(S)
    if name == 'GMV-LW':
        return w_gmv(lw_cc(X)[0])
    if name == 'GMV-NL':
        return w_gmv(nl_shrink(X))
    if name == 'ERC':
        return w_erc(S)
    if name == 'HRP':
        return w_hrp(S)
    raise ValueError(name)


# =============================================================================
# BACKTEST OUT-OF-SAMPLE CU FEREASTRA RULANTA
# =============================================================================
def backtest(R, Rex, window=WINDOW, strategies=STRATS):
    """Reechilibrare lunara: ponderi din ultimele `window` luni, aplicate in luna urmatoare.

    R: randamente totale, Rex: randamente in exces (acelasi index). Intoarce randamentele in exces
    ale portofoliilor, turnover-ul (suma |w_nou - w_derivat|) si istoricul ponderilor.
    """
    R, Rex = R.values, Rex
    idx = Rex.index[window:]
    X = Rex.values
    out = {s: [] for s in strategies}
    turn = {s: [] for s in strategies}
    W = {s: [] for s in strategies}
    prev = {s: None for s in strategies}
    for t in range(window, len(X)):
        est = X[t - window:t]
        for s in strategies:
            w = weights(s, est)
            if prev[s] is not None:
                turn[s].append(np.abs(w - prev[s]).sum())
            else:
                turn[s].append(np.nan)
            out[s].append(w @ X[t])
            gross = 1 + R[t]
            prev[s] = w * gross / (w @ gross)
            W[s].append(w)
    ret = pd.DataFrame(out, index=idx)
    ret.attrs['rf'] = pd.Series(R[window:, 0] - X[window:, 0], index=idx)   # rata fara risc (0 daca R = Rex)
    to = pd.DataFrame(turn, index=idx)
    Wd = {s: pd.DataFrame(np.array(W[s]), index=idx, columns=Rex.columns) for s in strategies}
    return ret, to, Wd


def sharpe(r, periods=12):
    r = np.asarray(r)
    return r.mean() / r.std(ddof=1) * np.sqrt(periods)


def summary(ret, to, costs=(0, 10, 50)):
    """Medie, volatilitate, Sharpe (anualizate, randamente in exces), turnover mediu lunar, scaderea maxima
    a averii din randamente totale (exces + rata fara risc), Sharpe net de costuri (bp)."""
    rows = {}
    rf = ret.attrs.get('rf', 0.0)
    for s in ret.columns:
        r = ret[s]
        d = dict(mean=r.mean() * 12, vol=r.std() * np.sqrt(12), sharpe=sharpe(r),
                 turnover=to[s].mean(), mdd=max_drawdown(r + rf))
        for c in costs[1:]:
            d[f'sharpe_{c}bp'] = sharpe(r - c / 1e4 * to[s].fillna(0))
        rows[s] = d
    return pd.DataFrame(rows).T


def max_drawdown(r):
    """Scaderea maxima a averii; o pierdere lunara >= 100% anuleaza averea (drawdown -100%)."""
    r = np.asarray(r, float)
    if (r <= -1).any():
        return -1.0
    w = np.r_[1.0, np.cumprod(1 + r)]                          # averea initiala 1 intra in maximul curent
    return float((w / np.maximum.accumulate(w) - 1).min())


# =============================================================================
# INFERENTA PENTRU DIFERENTE DE SHARPE
# =============================================================================
def sr_diff_hac(r1, r2, lags=None):
    """Ledoit-Wolf (2008), Sectiunea 3.1: Delta = SR1 - SR2 (lunar), eroare standard prin metoda delta,
    covarianta HAC cu nucleul Bartlett (Newey-West) si lag floor(4 (T/100)^(2/9))."""
    r1, r2 = np.asarray(r1, float), np.asarray(r2, float)
    T = len(r1)
    m1, m2 = r1.mean(), r2.mean()
    g1, g2 = (r1 ** 2).mean(), (r2 ** 2).mean()
    d = m1 / np.sqrt(g1 - m1 ** 2) - m2 / np.sqrt(g2 - m2 ** 2)
    grad = np.array([g1 / (g1 - m1 ** 2) ** 1.5, -g2 / (g2 - m2 ** 2) ** 1.5,
                     -m1 / (2 * (g1 - m1 ** 2) ** 1.5), m2 / (2 * (g2 - m2 ** 2) ** 1.5)])
    Y = np.column_stack([r1 - m1, r2 - m2, r1 ** 2 - g1, r2 ** 2 - g2])
    if lags is None:
        lags = int(np.floor(4 * (T / 100) ** (2 / 9)))
    Psi = Y.T @ Y / T
    for l in range(1, lags + 1):
        G = Y[l:].T @ Y[:-l] / T
        Psi += (1 - l / (lags + 1)) * (G + G.T)
    se = np.sqrt(grad @ Psi @ grad / T)
    p = 2 * (1 - stats.norm.cdf(abs(d / se)))
    return d * np.sqrt(12), se * np.sqrt(12), p


# Ledoit-Wolf (2008), Sectiunea 3.2.2: bootstrap studentizat, circular pe blocuri
LW_BLOCKS = (1, 2, 4, 6, 8, 10)     # grila de blocuri din LW (2008), Sectiunea 3.2.2 si Sectiunea 5
LW_K = 5000                         # secvente pseudo pentru calibrare (LW 2008, Sectiunea 5)
LW_M = 4999                         # replicari bootstrap pentru valoarea p (LW 2008, Sectiunea 5)
LW_M_CAL = 499                      # replicari bootstrap in calibrare (LW 2008, Sectiunea 4)
LW_SB_MEAN = 5                      # bootstrap stationar al reziduurilor VAR(1), bloc mediu 5


def _lw_parts(r1, r2):
    """Delta = SR1 - SR2 (lunar), gradientul lui f si seriile y_t (LW 2008, ec. 1-5)."""
    m1, m2 = r1.mean(-1), r2.mean(-1)
    g1, g2 = (r1 ** 2).mean(-1), (r2 ** 2).mean(-1)
    v1, v2 = g1 - m1 ** 2, g2 - m2 ** 2
    d = m1 / np.sqrt(v1) - m2 / np.sqrt(v2)
    grad = np.stack([g1 / v1 ** 1.5, -g2 / v2 ** 1.5, -m1 / (2 * v1 ** 1.5), m2 / (2 * v2 ** 1.5)], -1)
    Y = np.stack([r1 - m1[..., None], r2 - m2[..., None], r1 ** 2 - g1[..., None], r2 ** 2 - g2[..., None]], -1)
    return d, grad, Y


def qs_kernel(x):
    """Nucleul Quadratic Spectral (Andrews 1991)."""
    x = np.asarray(x, float)
    out = np.ones_like(x)
    nz = x != 0
    z = 6 * np.pi * x[nz] / 5
    out[nz] = 25 / (12 * np.pi ** 2 * x[nz] ** 2) * (np.sin(z) / z - np.cos(z))
    return out


def hac_qs_pw(Y):
    """Covarianta HAC cu nucleul QS prealbit (Andrews & Monahan 1992), latime de banda automata
    (Andrews 1991, AR(1)), factorul T/(T-4) din LW (2008, ec. 5). Y: T x 4, centrat."""
    T, k = Y.shape
    X0, X1 = Y[:-1], Y[1:]
    A = np.linalg.lstsq(X0, X1, rcond=None)[0].T                # VAR(1) fara termen liber
    U, s, Vt = np.linalg.svd(A)                                  # Andrews-Monahan: valori singulare <= 0.97
    A = U @ np.diag(np.minimum(s, 0.97)) @ Vt
    E = X1 - X0 @ A.T
    n = len(E)
    rho = np.array([np.sum(E[1:, a] * E[:-1, a]) / np.sum(E[:-1, a] ** 2) for a in range(k)])
    sig2 = np.array([np.mean((E[1:, a] - rho[a] * E[:-1, a]) ** 2) for a in range(k)])
    num = np.sum(4 * rho ** 2 * sig2 ** 2 / (1 - rho) ** 8)
    den = np.sum(sig2 ** 2 / (1 - rho) ** 4)
    ST = 1.3221 * (num / den * n) ** 0.2
    Psi = E.T @ E / n
    for j in range(1, n):
        w = qs_kernel(j / ST)
        G = E[j:].T @ E[:-j] / n
        Psi += w * (G + G.T)
    B = np.linalg.inv(np.eye(k) - A)
    return T / (T - 4) * B @ Psi @ B.T


def lw_se(r1, r2):
    """Delta (lunar) si eroarea standard s(Delta) din datele originale (LW 2008, ec. 5)."""
    d, grad, Y = _lw_parts(np.asarray(r1, float), np.asarray(r2, float))
    Psi = hac_qs_pw(Y)
    return float(d), float(np.sqrt(grad @ Psi @ grad / len(r1)))


def cbb_stat(r1, r2, b, M, rng):
    """M replicari bootstrap circular pe blocuri de lungime b: Delta* si s(Delta*) 'natural'
    (Goetze & Kuensch 1996; LW 2008, Sectiunea 3.2.2)."""
    T = len(r1)
    nb = -(-T // b)
    st = rng.integers(0, T, (M, nb))
    idx = ((st[:, :, None] + np.arange(b)) % T).reshape(M, -1)[:, :T]
    x1, x2 = r1[idx], r2[idx]
    d, grad, Y = _lw_parts(x1, x2)
    l = T // b
    Z = Y[:, :l * b].reshape(M, l, b, 4).sum(2) / np.sqrt(b)
    Psi = np.einsum('mjk,mjl->mkl', Z, Z) / l
    se = np.sqrt(np.einsum('mk,mkl,ml->m', grad, Psi, grad) / T)
    return d, se


def _sb_indices(T, n, mean_block, rng):
    """Indicii unui bootstrap stationar (Politis & Romano 1994), bloc mediu `mean_block`."""
    idx = np.empty(n, int)
    idx[0] = rng.integers(T)
    new = rng.random(n) < 1 / mean_block
    starts = rng.integers(0, T, n)
    for t in range(1, n):
        idx[t] = starts[t] if new[t] else (idx[t - 1] + 1) % T
    return idx


def lw_block_calibration(r1, r2, blocks=LW_BLOCKS, K=LW_K, M=LW_M_CAL, alpha=0.05, seed=SEED):
    """Algoritmul 3.1 din LW (2008): VAR(1) + bootstrap stationar al reziduurilor, K secvente pseudo,
    acoperirea intervalului studentizat simetric pentru fiecare b; alege b cu acoperirea cea mai apropiata de 1-alpha."""
    rng = np.random.default_rng(seed)
    r1, r2 = np.asarray(r1, float), np.asarray(r2, float)
    X = np.column_stack([r1, r2])
    T = len(X)
    d0, _ = lw_se(r1, r2)
    Z = np.column_stack([np.ones(T - 1), X[:-1]])
    coef = np.linalg.lstsq(Z, X[1:], rcond=None)[0]
    U = X[1:] - Z @ coef
    U = U - U.mean(0)
    cover = np.zeros(len(blocks))
    for k in range(K):
        u = U[_sb_indices(len(U), T - 1, LW_SB_MEAN, rng)]
        Xs = np.empty_like(X)
        Xs[0] = X[0]
        for t in range(1, T):
            Xs[t] = coef[0] + Xs[t - 1] @ coef[1:] + u[t - 1]
        dk, sk = lw_se(Xs[:, 0], Xs[:, 1])
        for j, b in enumerate(blocks):
            ds, ss = cbb_stat(Xs[:, 0], Xs[:, 1], b, M, rng)
            z = np.quantile(np.abs(ds - dk) / ss, 1 - alpha)
            cover[j] += abs(dk - d0) <= z * sk
    g_hat = cover / K
    return blocks[int(np.argmin(np.abs(g_hat - (1 - alpha))))], dict(zip(map(str, blocks), g_hat.tolist()))


def sr_diff_boot(r1, r2, block=None, M=LW_M, K=LW_K, alpha=0.05, seed=SEED):
    """Testul Ledoit-Wolf (2008, Sectiunea 3.2.2 si Remarca 3.2) pentru H0: SR1 = SR2:
    bootstrap studentizat circular pe blocuri; blocul din Algoritmul 3.1 (daca block=None).
    Intoarce Delta (anualizat), intervalul 95% simetric (anualizat), valoarea p (ec. 9), statisticile
    studentizate bootstrap, blocul ales si functia de calibrare."""
    r1, r2 = np.asarray(r1, float), np.asarray(r2, float)
    cal = None
    if block is None:
        block, cal = lw_block_calibration(r1, r2, K=K, alpha=alpha, seed=seed)
    d, s = lw_se(r1, r2)
    ds, ss = cbb_stat(r1, r2, block, M, np.random.default_rng(seed + 1))
    tstar = (ds - d) / ss
    z = np.quantile(np.abs(tstar), 1 - alpha)
    p = (np.sum(np.abs(tstar) >= abs(d) / s) + 1) / (M + 1)
    a = np.sqrt(12)
    return dict(diff=d * a, se=s * a, ci=[(d - z * s) * a, (d + z * s) * a], p_boot=float(p),
                t_obs=d / s, z_star=float(z), block=int(block), calibration=cal), tstar


# =============================================================================
# FIG 1: Frontiera cu doua active (SPY, TLT) pentru mai multe corelatii
# =============================================================================
def two_asset_stats():
    R, Rex, rf = us_monthly(['SPY', 'TLT'], start='2002-08-01')
    mu = R.mean() * 12
    sd = R.std() * np.sqrt(12)
    rho = R.corr().iloc[0, 1]
    return R, mu, sd, rho


def gmv_two(s1, s2, rho):
    """Ponderea primului activ in GMV cu doua active."""
    return (s2 ** 2 - rho * s1 * s2) / (s1 ** 2 + s2 ** 2 - 2 * rho * s1 * s2)


def fig_two_asset():
    R, mu, sd, rho = two_asset_stats()
    w = np.linspace(-0.2, 1.2, 400)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for r, c in zip([-0.5, 0.0, rho, 0.5, 1.0], [Forest, Amber, IDAred, Purple, '#17A2B8']):
        m = w * mu['SPY'] + (1 - w) * mu['TLT']
        v = np.sqrt(w ** 2 * sd['SPY'] ** 2 + (1 - w) ** 2 * sd['TLT'] ** 2 + 2 * w * (1 - w) * r * sd['SPY'] * sd['TLT'])
        lab = f'rho = {r:.2f}' + (' (actual, 2002-2026)' if r == rho else ' (hypothetical)')
        ax.plot(v, m, color=c, lw=1.6 if r == rho else 1.0, ls='-' if r == rho else '--', label=lab)
    wg = gmv_two(sd['SPY'], sd['TLT'], rho)
    vg = np.sqrt(wg ** 2 * sd['SPY'] ** 2 + (1 - wg) ** 2 * sd['TLT'] ** 2 + 2 * wg * (1 - wg) * rho * sd['SPY'] * sd['TLT'])
    mg = wg * mu['SPY'] + (1 - wg) * mu['TLT']
    ax.plot(vg, mg, 'o', color=IDAred, ms=6)
    ax.annotate(f'GMV: {wg:.0%} SPY', (vg, mg), xytext=(8, -12), textcoords='offset points', fontsize=8)
    for s in ['SPY', 'TLT']:
        ax.plot(sd[s], mu[s], 's', color=MainBlue, ms=6)
        ax.annotate(s, (sd[s], mu[s]), xytext=(6, 2), textcoords='offset points', fontsize=8)
    ax.set_xlabel('Volatility (annualised)')
    ax.set_ylabel('Mean return (annualised)')
    ax.set_xlim(0, None)
    ax.set_title('Two-asset frontier: SPY and TLT, monthly 2002-2026', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.16)
    plt.tight_layout()
    save_fig('ch4_two_asset')
    return dict(mu=mu.to_dict(), sd=sd.to_dict(), rho=rho, w_gmv=wg, sd_gmv=vg, mu_gmv=mg,
                T=len(R), start=str(R.index[0].date()), end=str(R.index[-1].date()))


# =============================================================================
# FIG 2: Frontiera sectoarelor: cu si fara vanzari in lipsa, 1/N, GMV, tangent
# =============================================================================
def frontier_curve(mu, S, targets):
    """Frontiera analitica (vanzari in lipsa permise): sigma(m) pentru fiecare medie tinta m."""
    Si = np.linalg.inv(S)
    one = np.ones(len(mu))
    A, B, C = one @ Si @ one, one @ Si @ mu, mu @ Si @ mu
    D = A * C - B ** 2
    return np.sqrt((A * targets ** 2 - 2 * B * targets + C) / D)


def frontier_lo(mu, S, targets):
    """Frontiera cu ponderi nenegative (SLSQP), pentru mediile tinta realizabile."""
    n = len(mu)
    out = []
    for m in targets:
        res = minimize(lambda w: w @ S @ w, np.ones(n) / n, method='SLSQP', bounds=[(0, 1)] * n,
                       constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1},
                                    {'type': 'eq', 'fun': lambda w, m=m: w @ mu - m}])
        out.append(np.sqrt(res.fun) if res.success else np.nan)
    return np.array(out)


def fig_frontier():
    R, Rex, rf = us_monthly(SECTORS)
    mu, S = Rex.mean().values * 12, Rex.cov().values * 12
    t = np.linspace(-0.02, 0.20, 200)
    s_u = frontier_curve(mu, S, t)
    t_lo = np.linspace(mu.min(), mu.max(), 60)
    s_lo = frontier_lo(mu, S, t_lo)
    wg, wt, wtl = w_gmv(S), w_tan(mu, S), w_long_only(S, mu)
    pt = lambda w: (np.sqrt(w @ S @ w), w @ mu)
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.plot(s_u, t, color=MainBlue, lw=1.4, label='Frontier, short sales allowed')
    ax.plot(s_lo, t_lo, color=Forest, lw=1.4, ls='--', label='Frontier, long-only')
    for k, s in enumerate(SECTORS):
        ax.plot(np.sqrt(S[k, k]), mu[k], 's', color='#17A2B8', ms=4)
        ax.annotate(s, (np.sqrt(S[k, k]), mu[k]), xytext=(-18, 3) if s == 'XLI' else (4, 2),
                    textcoords='offset points', fontsize=7)
    for w, lab, c, mk in [(wg, 'GMV', Amber, 'o'), (wt, 'Tangency (MV)', IDAred, '*'),
                          (wtl, 'Tangency, long-only', Orange, 'D'), (w_ew(9), '1/N', Purple, '^')]:
        x, y = pt(w)
        ax.plot(x, y, mk, color=c, ms=8 if mk == '*' else 6, label=f'{lab}: Sharpe {y / x:.2f}')
    sm = max(np.sqrt(np.diag(S)).max(), pt(wt)[0]) * 1.1
    ax.plot([0, sm], [0, sm * pt(wt)[1] / pt(wt)[0]], color=IDAred, lw=0.7, ls=':')
    ax.set_xlim(0, sm)
    ax.set_ylim(-0.02, 0.2)
    ax.set_xlabel('Volatility (annualised)')
    ax.set_ylabel('Mean excess return (annualised)')
    ax.set_title(f'Nine sector ETFs, monthly excess returns {Rex.index[0]:%b %Y} - {Rex.index[-1]:%b %Y} (in-sample)',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.15)
    plt.tight_layout()
    save_fig('ch4_frontier')
    sr = lambda w: pt(w)[1] / pt(w)[0]
    return dict(T=len(Rex), start=str(Rex.index[0].date()), end=str(Rex.index[-1].date()),
                sharpe=dict(gmv=sr(wg), tan=sr(wt), tan_lo=sr(wtl), ew=sr(w_ew(9))),
                w_tan=dict(zip(SECTORS, wt)), w_gmv=dict(zip(SECTORS, wg)), w_tan_lo=dict(zip(SECTORS, wtl)),
                gmv_vol=pt(wg)[0], mu=dict(zip(SECTORS, mu)), vol=dict(zip(SECTORS, np.sqrt(np.diag(S)))))


# =============================================================================
# FIG 3: Eroarea de estimare: frontiere estimate vs realizate (simulare)
# =============================================================================
def sector_truth():
    """Parametrii 'adevarati' ai simularilor: media si covarianta lunara din tot esantionul."""
    R, Rex, rf = us_monthly(SECTORS)
    return Rex.mean().values, Rex.cov().values


def fig_estimation_error(T=60, nsim=25, seed=SEED):
    mu, S = sector_truth()
    rng = np.random.default_rng(seed)
    t = np.linspace(-0.01, 0.06, 150) / 1          # medii lunare tinta
    fig, ax = plt.subplots(figsize=(7, 4.4))
    s_true = frontier_curve(mu, S, t)
    ax.plot(s_true * np.sqrt(12), t * 12, color=MainBlue, lw=2, label='True frontier (known parameters)')
    est_sr, true_sr, neg_b = [], [], []
    for k in range(nsim):
        X = rng.multivariate_normal(mu, S, T)
        m_hat, S_hat = X.mean(0), np.cov(X.T)
        Si = np.linalg.inv(S_hat)
        one = np.ones(len(mu))
        s_hat = frontier_curve(m_hat, S_hat, t)
        # portofoliile frontierei estimate, evaluate cu parametrii adevarati
        A, B, C = one @ Si @ one, one @ Si @ m_hat, m_hat @ Si @ m_hat
        D = A * C - B ** 2
        real_m, real_s = [], []
        for m in t:
            lam, gam = (C - m * B) / D, (m * A - B) / D
            w = Si @ (lam * one + gam * m_hat)
            real_m.append(w @ mu)
            real_s.append(np.sqrt(w @ S @ w))
        ax.plot(s_hat * np.sqrt(12), t * 12, color=IDAred, lw=0.5, alpha=0.5,
                label='Estimated frontier (in-sample, 60 months)' if k == 0 else None)
        ax.plot(np.array(real_s) * np.sqrt(12), np.array(real_m) * 12, color=Forest, lw=0.5, alpha=0.5,
                label='Realised frontier (same weights, true parameters)' if k == 0 else None)
    for k in range(2000):
        X = rng.multivariate_normal(mu, S, T)
        m_hat, S_hat = X.mean(0), np.cov(X.T)
        w = w_tan(m_hat, S_hat)
        est_sr.append((w @ m_hat) / np.sqrt(w @ S_hat @ w) * np.sqrt(12))   # = sign(B) theta_hat
        neg_b.append(np.linalg.solve(S_hat, m_hat).sum() < 0)
        true_sr.append((w @ mu) / np.sqrt(w @ S @ w) * np.sqrt(12))
    wt = w_tan(mu, S)
    sr_opt = (wt @ mu) / np.sqrt(wt @ S @ wt) * np.sqrt(12)
    we = w_ew(len(mu))
    sr_ew = (we @ mu) / np.sqrt(we @ S @ we) * np.sqrt(12)
    ax.set_xlim(0, 0.35)
    ax.set_ylim(-0.12, 0.72)
    ax.set_xlabel('Volatility (annualised)')
    ax.set_ylabel('Mean excess return (annualised)')
    ax.set_title('Estimation error: 25 simulated 60-month samples, nine sector ETFs, Normal returns',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.15)
    plt.tight_layout()
    save_fig('ch4_estimation_error')
    # theta_hat = |Sharpe in esantion| = radacina lui mu' S^-1 mu (Sharpe-ul maxim estimat, Kan & Zhou 2007)
    est_sr, true_sr = np.abs(np.array(est_sr)), np.array(true_sr)
    return dict(T=T, nsim=2000, sr_opt=sr_opt, sr_ew=sr_ew, share_B_negative=float(np.mean(neg_b)),
                est_sr_median=float(np.median(est_sr)), true_sr_median=float(np.median(true_sr)),
                share_true_below_ew=float(np.mean(true_sr < sr_ew)), share_true_neg=float(np.mean(true_sr < 0)))


# =============================================================================
# FIG 4: Cat de lunga trebuie sa fie fereastra? (simulare, DeMiguel-Garlappi-Uppal)
# =============================================================================
def fig_window_length(nsim=300, seed=SEED):
    mu, S = sector_truth()
    n = len(mu)
    rng = np.random.default_rng(seed)
    Ts = [36, 60, 120, 240, 480, 960, 1920, 3840]
    names = ['MV', 'MV-LO', 'GMV', 'GMV-LW', 'ERC']
    res = {k: [] for k in names}
    true_sr = lambda w: (w @ mu) / np.sqrt(w @ S @ w) * np.sqrt(12)
    for T in Ts:
        vals = {k: [] for k in names}
        for i in range(nsim):
            X = rng.multivariate_normal(mu, S, T)
            for k in names:
                vals[k].append(true_sr(weights(k, X)))
        for k in names:
            res[k].append(np.median(vals[k]))
    sr_ew = true_sr(w_ew(n))
    sr_opt = true_sr(w_tan(mu, S))
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for k in names:
        ax.plot(Ts, res[k], 'o-', color=SCOL[k], ms=4, label=k)
    ax.axhline(sr_ew, color=EWcol, ls='--', lw=1, label=f'1/N (true Sharpe {sr_ew:.2f})')
    ax.axhline(sr_opt, color='black', ls=':', lw=1, label=f'True tangency (Sharpe {sr_opt:.2f})')
    ax.set_xscale('log')
    ax.set_xticks(Ts, [str(T) for T in Ts])
    ax.set_xlabel('Estimation window (months, log scale)')
    ax.set_ylabel('True Sharpe ratio of the estimated portfolio (median)')
    ax.set_title(f'How long must the window be? {nsim} simulations per window, nine sectors', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.16)
    plt.tight_layout()
    save_fig('ch4_window_length')
    cross = next((T for T, v in zip(Ts, res['MV']) if v > sr_ew), None)
    return dict(Ts=Ts, median_true_sr={k: dict(zip(map(str, Ts), v)) for k, v in res.items()},
                sr_ew=sr_ew, sr_opt=sr_opt, mv_beats_ew_at=cross)


# =============================================================================
# FIG 5: Ponderi rulante: MV vs GMV-LW (sectoare)
# =============================================================================
def fig_rolling_weights(bt):
    ret, to, W = bt
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True)
    for ax, s in zip(axes, ['MV', 'GMV-LW']):
        for k, c in enumerate(W[s].columns):
            ax.plot(W[s].index, W[s][c], color=PALETTE[k % len(PALETTE)], lw=0.8, label=c)
        ax.axhline(0, color=Gray, lw=0.5)
        ax.set_ylabel('Weight')
        ax.set_title(f'{s}: weights re-estimated each month on the last 60 months', fontsize=9, loc='left')
    axes[0].set_ylim(-6, 6)
    legend_outside_bottom(axes[1], ncol=9, y=-0.2)
    plt.tight_layout()
    save_fig('ch4_rolling_weights')
    mv, lw = W['MV'], W['GMV-LW']
    X = us_monthly(list(W['MV'].columns))[1].values
    B = np.array([np.linalg.solve(np.cov(X[t - WINDOW:t].T), X[t - WINDOW:t].mean(0)).sum()
                  for t in range(WINDOW, len(X))])                      # 1' S^-1 mu pe fiecare fereastra
    return dict(n_windows=len(B), n_B_negative=int((B < 0).sum()),
                mv_max_abs=float(mv.abs().max().max()), mv_median_gross=float(mv.abs().sum(1).median()),
                lw_max_abs=float(lw.abs().max().max()), lw_median_gross=float(lw.abs().sum(1).median()),
                mv_share_months_gross_gt3=float((mv.abs().sum(1) > 3).mean()))


# =============================================================================
# FIG 6: Shrinkage: valori proprii si intensitatea delta in timp
# =============================================================================
def fig_shrinkage():
    R, Rex, rf = us_monthly(SECTORS)
    X = Rex.values
    last = X[-WINDOW:]
    S = np.cov(last.T, bias=True)
    Slw, d_last = lw_cc(last)
    Sfull = np.cov(X.T, bias=True)
    ev = lambda A: np.sort(np.linalg.eigvalsh(A))[::-1] * 12
    deltas = pd.Series([lw_cc(X[t - WINDOW:t])[1] for t in range(WINDOW, len(X) + 1)],
                       index=Rex.index[WINDOW - 1:])
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6))
    k = np.arange(1, 10)
    axes[0].plot(k, ev(S), 'o-', color=IDAred, ms=4, label='Sample, last 60 months')
    axes[0].plot(k, ev(Slw), 's-', color=MainBlue, ms=4, label='Ledoit-Wolf, last 60 months')
    axes[0].plot(k, ev(Sfull), '^--', color=Forest, ms=4, label=f'Sample, all {len(X)} months')
    axes[0].set_yscale('log')
    axes[0].set_xlabel('Eigenvalue rank')
    axes[0].set_ylabel('Eigenvalue (annualised, log)')
    axes[0].set_title('Eigenvalues', fontsize=9, loc='left')
    legend_outside_bottom(axes[0], ncol=1, y=-0.2)
    axes[1].plot(deltas.index, deltas.values, color=MainBlue)
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel('Shrinkage intensity delta')
    axes[1].set_title('Rolling 60-month delta', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch4_shrinkage')
    cond = lambda A: np.linalg.cond(A)
    return dict(delta_last=d_last, delta_mean=deltas.mean(), delta_min=deltas.min(), delta_max=deltas.max(),
                cond_sample=cond(S), cond_lw=cond(Slw), cond_full=cond(Sfull),
                ev_sample=ev(S).tolist(), ev_lw=ev(Slw).tolist(), ev_full=ev(Sfull).tolist(),
                end=str(Rex.index[-1].date()))


# =============================================================================
# FIG 7: Black-Litterman: randamente implicite, o opinie relativa, ponderi
# =============================================================================
def black_litterman(Sigma, w_b, P, q, delta=2.5, tau=0.05, conf=None):
    """Black-Litterman (1992), forma He-Litterman: Omega = diag(P tau Sigma P') daca nu e data."""
    pi = delta * Sigma @ w_b
    Om = np.diag(np.diag(P @ (tau * Sigma) @ P.T)) if conf is None else conf
    A = np.linalg.inv(tau * Sigma) + P.T @ np.linalg.inv(Om) @ P
    mu_bl = np.linalg.solve(A, np.linalg.inv(tau * Sigma) @ pi + P.T @ np.linalg.inv(Om) @ q)
    w_bl = np.linalg.solve(delta * Sigma, mu_bl)
    return pi, mu_bl, w_bl


def fig_black_litterman():
    R, Rex, rf = us_monthly(SECTORS, start='2016-08-01')
    Sigma = Rex.cov().values * 12
    n = len(SECTORS)
    w_b = w_ew(n)
    P = np.zeros((1, n))
    P[0, SECTORS.index('XLK')], P[0, SECTORS.index('XLU')] = 1, -1
    q = np.array([0.03])
    pi, mu_bl, w_bl = black_litterman(Sigma, w_b, P, q)
    mu_s = Rex.mean().values * 12
    w_s = w_tan(mu_s, Sigma)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.8))
    x = np.arange(n)
    axes[0].bar(x - 0.27, pi, 0.27, color=EWcol, label='Implied prior pi (1/N benchmark)')
    axes[0].bar(x, mu_bl, 0.27, color=MainBlue, label='Black-Litterman posterior')
    axes[0].bar(x + 0.27, mu_s, 0.27, color=IDAred, label='Sample mean, 10 years')
    axes[0].set_xticks(x, SECTORS, rotation=45, fontsize=7)
    axes[0].set_ylabel('Expected excess return (ann.)')
    axes[0].set_title('Expected returns', fontsize=9, loc='left')
    legend_outside_bottom(axes[0], ncol=1, y=-0.25)
    axes[1].bar(x - 0.27, w_b, 0.27, color=EWcol, label='Benchmark 1/N')
    axes[1].bar(x, w_bl, 0.27, color=MainBlue, label='Black-Litterman weights')
    axes[1].bar(x + 0.27, w_s, 0.27, color=IDAred, label='MV on sample means')
    axes[1].axhline(0, color=Gray, lw=0.5)
    axes[1].set_xticks(x, SECTORS, rotation=45, fontsize=7)
    axes[1].set_ylim(-1.6, 1.6)
    axes[1].set_ylabel('Weight')
    axes[1].set_title('Portfolio weights', fontsize=9, loc='left')
    legend_outside_bottom(axes[1], ncol=1, y=-0.25)
    plt.tight_layout()
    save_fig('ch4_black_litterman')
    return dict(start=str(Rex.index[0].date()), end=str(Rex.index[-1].date()), T=len(Rex), delta=2.5, tau=0.05,
                view='XLK - XLU = 3% p.a.', prior_view=(P @ pi).item(), post_view=(P @ mu_bl).item(),
                pi=dict(zip(SECTORS, pi)), mu_bl=dict(zip(SECTORS, mu_bl)), mu_sample=dict(zip(SECTORS, mu_s)),
                w_bl=dict(zip(SECTORS, w_bl)), w_sample_mv=dict(zip(SECTORS, w_s)),
                w_bl_sum=float(w_bl.sum()))


# =============================================================================
# FIG 8: Contributii la risc: 1/N, GMV-LO, ERC, HRP (multi-active)
# =============================================================================
def fig_risk_contrib():
    R, Rex, rf = us_monthly(MULTI)
    S = Rex.cov().values * 12
    ws = {'1/N': w_ew(len(MULTI)), 'GMV-LO': w_long_only(S), 'ERC': w_erc(S), 'HRP': w_hrp(S)}
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.8), sharey=True)
    for ax, what in zip(axes, ['Weights', 'Risk contributions']):
        bottom = np.zeros(len(ws))
        for k, a in enumerate(MULTI):
            vals = np.array([w[k] if what == 'Weights' else risk_contrib(w, S)[k] for w in ws.values()])
            ax.bar(list(ws), vals, bottom=bottom, color=PALETTE[k], label=a, width=0.6)
            bottom += vals
        ax.set_title(what, fontsize=9, loc='left')
        ax.set_ylim(0, 1)
    axes[0].set_ylabel('Share')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=8, frameon=False)
    plt.suptitle(f'Eight multi-asset ETFs, monthly {Rex.index[0]:%b %Y} - {Rex.index[-1]:%b %Y}', fontsize=9, x=0.02, ha='left')
    plt.tight_layout(rect=[0, 0.07, 1, 1])
    save_fig('ch4_risk_contrib')
    out = {}
    for k, w in ws.items():
        rc = risk_contrib(w, S)
        out[k] = dict(w=dict(zip(MULTI, w)), rc=dict(zip(MULTI, rc)), vol=float(np.sqrt(w @ S @ w)),
                      rc_equity=float(rc[:3].sum() + rc[MULTI.index('HYG')]))
    out['vol'] = dict(zip(MULTI, np.sqrt(np.diag(S))))
    out['T'] = len(Rex)
    return out


# =============================================================================
# FIG 9: HRP: dendrograma si ponderi (universul combinat, 16 ETF-uri)
# =============================================================================
COMBINED = SECTORS + [a for a in MULTI if a != 'SPY']


def fig_hrp():
    R, Rex, rf = us_monthly(COMBINED)
    S = Rex.cov().values * 12
    Z = hrp_tree(S)
    w = w_hrp(S)
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.9), gridspec_kw={'width_ratios': [1.4, 1]})
    dn = dendrogram(Z, labels=COMBINED, ax=axes[0], color_threshold=0.6 * Z[:, 2].max(), above_threshold_color=Gray,
                    leaf_font_size=7)
    axes[0].set_ylabel('Euclidean distance between columns of D')
    axes[0].set_title('Single-linkage tree', fontsize=9, loc='left')
    order = dn['ivl']
    wi = pd.Series(w, index=COMBINED)[order]
    wg = pd.Series(w_long_only(S), index=COMBINED)[order]
    y = np.arange(len(order))
    axes[1].barh(y + 0.2, wi.values, 0.4, color='#17A2B8', label='HRP')
    axes[1].barh(y - 0.2, wg.values, 0.4, color=Purple, label='GMV long-only')
    axes[1].set_yticks(y, order, fontsize=7)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('Weight')
    axes[1].set_title('Weights', fontsize=9, loc='left')
    legend_outside_bottom(axes[1], ncol=2, y=-0.14)
    plt.tight_layout()
    save_fig('ch4_hrp')
    merges = [dict(a=[COMBINED[int(i)] for i in (Z[k, 0], Z[k, 1]) if i < len(COMBINED)], height=float(Z[k, 2]))
              for k in range(len(Z))]
    last = [COMBINED[int(i)] for i in Z[-1, :2] if i < len(COMBINED)]
    return dict(order=order, merges=merges, last_single=last, first_pair=merges[0],
                w_hrp=dict(zip(COMBINED, w)), w_gmv_lo=dict(zip(COMBINED, w_long_only(S))),
                n_nonzero_gmv_lo=int((w_long_only(S) > 1e-4).sum()), T=len(Rex),
                start=str(Rex.index[0].date()))


# =============================================================================
# FIG 10-13: Backtest out-of-sample pe trei universuri
# =============================================================================
UNIVERSES = {'Sectors': SECTORS, 'Multi-asset': MULTI, 'Combined': COMBINED}


def run_backtests():
    out = {}
    for name, syms in UNIVERSES.items():
        R, Rex, rf = us_monthly(syms)
        out[name] = backtest(R, Rex)
        print(f'   backtest {name}: {len(out[name][0])} months')
    return out


def fig_oos_cum(bts, universe='Multi-asset'):
    ret, to, W = bts[universe]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for s in STRATS:
        rf = ret.attrs['rf']
        total = ret[s] + rf                                       # randamentul total al portofoliului
        wealth = np.cumprod(1 + total) / np.cumprod(1 + rf)       # averea relativa la contul de titluri de stat
        ruin = np.flatnonzero(total.values <= -1)                 # o pierdere >= 100% anuleaza averea
        if len(ruin):
            wealth.iloc[ruin[0]:] = np.nan                        # traiectoria se opreste la ruina
        ax.plot(ret.index, wealth, color=SCOL[s], lw=1.6 if s in ('1/N', 'GMV-LW', 'ERC', 'HRP') else 0.8,
                label=f'{s} (Sharpe {sharpe(ret[s]):.2f})')
    ax.set_yscale('log')
    ax.set_ylabel('Wealth relative to T-bills (log scale)')
    ax.set_title(f'{universe}: out-of-sample, 60-month rolling window, monthly rebalancing, no costs',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.1)
    plt.tight_layout()
    save_fig('ch4_oos_cum')


def fig_oos_sharpe(tabs):
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    x = np.arange(len(STRATS))
    wd = 0.27
    for k, (u, c) in enumerate(zip(UNIVERSES, [MainBlue, Forest, Amber])):
        v = tabs[u].loc[STRATS, 'sharpe'].values
        ax.bar(x + (k - 1) * wd, v, wd, color=c, label=f'{u} (OOS {tabs[u].attrs["start"]} - {tabs[u].attrs["end"]})')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(x, STRATS)
    ax.set_ylabel('Out-of-sample Sharpe ratio (annualised)')
    ax.set_title('Out-of-sample Sharpe ratios, before costs', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.1)
    plt.tight_layout()
    save_fig('ch4_oos_sharpe')


def fig_costs(bts, universe='Combined'):
    ret, to, W = bts[universe]
    c = np.arange(0, 101, 5)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.8), gridspec_kw={'width_ratios': [1.3, 1]})
    for s in STRATS:
        axes[0].plot(c, [sharpe(ret[s] - cc / 1e4 * to[s].fillna(0)) for cc in c], color=SCOL[s], label=s)
    axes[0].set_xlabel('Cost per unit of turnover (basis points)')
    axes[0].set_ylabel('Net Sharpe ratio (annualised)')
    axes[0].set_title(f'{universe}: Sharpe after costs', fontsize=9, loc='left')
    axes[0].axhline(0, color=Gray, lw=0.5)
    legend_outside_bottom(axes[0], ncol=4, y=-0.18)
    tv = to[STRATS].mean()
    axes[1].barh(STRATS, tv.values, color=[SCOL[s] for s in STRATS])
    axes[1].set_xscale('log')
    axes[1].invert_yaxis()
    axes[1].set_xlabel('Mean monthly turnover (log scale)')
    axes[1].set_title('Turnover', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch4_costs')


def _test_pair(args):
    """Un test de diferenta Sharpe: HAC (Sectiunea 3.1) si bootstrap studentizat (Sectiunea 3.2.2)."""
    r1, r2, block = args
    d, se, p = sr_diff_hac(r1, r2)
    res, tstar = sr_diff_boot(r1, r2, block=block)
    return dict(diff=d, se_hac=se, p_hac=p, ci_boot=res['ci'], p_boot=res['p_boot'], block=res['block'],
                calibration=res['calibration'], se_qs=res['se'], t_obs=res['t_obs'], z_star=res['z_star']), tstar


def run_tests(pairs, n_jobs=1, blocks=None):
    """pairs: dict {cheie: (r1, r2)}; blocks: dict {cheie: bloc} deja calibrat (altfel Algoritmul 3.1);
    n_jobs > 1 foloseste procese paralele (calibrarea e costisitoare)."""
    keys = list(pairs)
    blocks = blocks or {}
    args = [(np.asarray(pairs[k][0], float), np.asarray(pairs[k][1], float), blocks.get(k)) for k in keys]
    if n_jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(n_jobs) as ex:
            res = list(ex.map(_test_pair, args))
    else:
        res = [_test_pair(a) for a in args]
    return dict(zip(keys, res))


def sharpe_tests(bts, bench='1/N', n_jobs=1, blocks=None):
    """Toate regulile contra 1/N in cele trei universuri; intoarce rezultatele si statisticile bootstrap.
    blocks: {(univers, regula): bloc} din calibrarea anterioara (optional)."""
    pairs = {(u, s): (bts[u][0][s], bts[u][0][bench]) for u in bts for s in STRATS if s != bench}
    res = run_tests(pairs, n_jobs, blocks)
    out = {u: {s: res[(u, s)][0] for s in STRATS if s != bench} for u in bts}
    draws = {k: v[1] for k, v in res.items()}
    return out, draws


def holm(pvals):
    """Holm (1979): valori p ajustate pas cu pas descendent, valide sub orice dependenta intre teste."""
    keys = list(pvals)
    p = np.array([pvals[k] for k in keys], float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (m - i) * p[j]))
        adj[j] = run
    return dict(zip(keys, adj.tolist()))


def holm_sharpe(tests):
    """Ajustarea Holm pe toate testele regula minus 1/N (3 universuri x 7 reguli), HAC si bootstrap."""
    out = {}
    for kind in ['p_hac', 'p_boot']:
        adj = holm({f'{u}: {s}': tests[u][s][kind] for u in tests for s in tests[u]})
        out[kind] = adj
    out['m'] = len(adj)
    out['n_raw_05'] = {kind: int(sum(tests[u][s][kind] < 0.05 for u in tests for s in tests[u]))
                       for kind in ['p_hac', 'p_boot']}
    out['n_holm_05'] = {kind: int(sum(v < 0.05 for v in out[kind].values())) for kind in ['p_hac', 'p_boot']}
    out['min_holm'] = {kind: float(min(out[kind].values())) for kind in ['p_hac', 'p_boot']}
    return out


def fig_sharpe_test(tests, draws):
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), sharey=True)
    res = {}
    for ax, (u, s) in zip(axes, [('Sectors', 'GMV-LW'), ('Multi-asset', 'ERC')]):
        r = tests[u][s]
        ts = draws[(u, s)]
        ax.hist(ts, bins=np.linspace(-6, 6, 61), color=SCOL[s], alpha=0.8, density=True,
                label='Bootstrap studentized statistic')
        ax.axvline(r['t_obs'], color=IDAred, lw=1.4, label=f"Observed statistic {r['t_obs']:+.2f}")
        ax.axvline(-r['z_star'], color='black', ls='--', lw=0.8, label=f"Critical values +/-{r['z_star']:.2f} (5%)")
        ax.axvline(r['z_star'], color='black', ls='--', lw=0.8)
        ax.set_title(f"{u}: {s} minus 1/N, block {r['block']}\nHAC p = {r['p_hac']:.2f}, bootstrap p = {r['p_boot']:.2f}",
                     fontsize=9, loc='left')
        ax.set_xlabel('(Delta* - Delta) / s(Delta*)')
        legend_outside_bottom(ax, ncol=1, y=-0.2)
        res[u] = dict(strategy=s, **r)
    axes[0].set_ylabel('Density')
    plt.tight_layout()
    save_fig('ch4_sharpe_test')
    return res


# =============================================================================
# INFERENTA PE PORTOFOLII ESTIMATE (nivel master)
# =============================================================================
def britten_jones(Rex):
    """Britten-Jones (1999): regresia lui 1 pe randamentele in exces, fara termen liber.
    b ~ Sigma^-1 mu; testul t al lui b_i = 0 (pondere tangenta nula) si testul F al lui b proportional cu 1 (1/N)."""
    X = np.asarray(Rex, float)
    T, N = X.shape
    y = np.ones(T)
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    s2 = u @ u / (T - N)
    se = np.sqrt(np.diag(s2 * XtX_inv))
    t = b / se
    R = np.hstack([np.eye(N - 1), np.zeros((N - 1, 1))]) - np.hstack([np.zeros((N - 1, N - 1)), np.ones((N - 1, 1))])
    Rb = R @ b
    F = Rb @ np.linalg.solve(R @ XtX_inv @ R.T, Rb) / (N - 1) / s2
    pF = 1 - stats.f.cdf(F, N - 1, T - N)
    # varianta HAC (Bartlett, Newey-West), pentru abateri de la i.i.d. Normal
    L = int(np.floor(4 * (T / 100) ** (2 / 9)))
    Xu = X * u[:, None]
    Om = Xu.T @ Xu / T
    for l in range(1, L + 1):
        G = Xu[l:].T @ Xu[:-l] / T
        Om += (1 - l / (L + 1)) * (G + G.T)
    Vh = T * XtX_inv @ Om @ XtX_inv
    W = Rb @ np.linalg.solve(R @ Vh @ R.T, Rb)
    pW = 1 - stats.chi2.cdf(W, N - 1)
    w = b / b.sum()
    return dict(T=T, N=N, b=b.tolist(), w=w.tolist(), t=t.tolist(), F=float(F), pF=float(pF), df=(N - 1, T - N),
                wald_hac=float(W), p_wald_hac=float(pW), t_hac=(b / np.sqrt(np.diag(Vh))).tolist(),
                w_check=w_tan(X.mean(0), np.cov(X.T)).tolist())


def kz_bias(theta_ann, N, T):
    """Kan & Zhou (2007): E[theta_hat^2] = (T theta^2 + N)/(T - N - 2) pentru Sigma_hat de verosimilitate maxima,
    i.i.d. Normal; intoarce valorile anualizate."""
    th2 = (theta_ann / np.sqrt(12)) ** 2
    e2 = (T * th2 + N) / (T - N - 2)
    return dict(theta2_m=th2, E_theta2_m=e2, E_theta_ann_approx=float(np.sqrt(e2 * 12)),
                inv_bias=T / (T - N - 2))


def theta2_unbiased(Rex):
    """Estimatorul nedeplasat al lui theta^2 (Kan & Zhou 2007): ((T-N-2) theta_hat^2 - N)/T, Sigma_hat MV."""
    X = np.asarray(Rex, float)
    T, N = X.shape
    mu, S = X.mean(0), np.cov(X.T, bias=True)
    th2 = mu @ np.linalg.solve(S, mu)
    u = ((T - N - 2) * th2 - N) / T
    return dict(T=T, N=N, theta_hat_ann=float(np.sqrt(th2 * 12)), theta2_u=float(u),
                theta_u_ann=float(np.sqrt(max(u, 0) * 12)))


def mp_bounds(c, s2=1.0):
    """Suportul legii Marchenko-Pastur pentru raportul c = N/T < 1."""
    return s2 * (1 - np.sqrt(c)) ** 2, s2 * (1 + np.sqrt(c)) ** 2


def mp_density(x, c, s2=1.0):
    a, b = mp_bounds(c, s2)
    out = np.zeros_like(x)
    ok = (x > a) & (x < b)
    out[ok] = np.sqrt((b - x[ok]) * (x[ok] - a)) / (2 * np.pi * s2 * c * x[ok])
    return out


def fig_mp():
    """Valorile proprii ale matricei de corelatie pe ultima fereastra de 60 de luni vs banda Marchenko-Pastur."""
    res = {}
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), sharey=True)
    for ax, (u, syms) in zip(axes, [('Combined', COMBINED), ('Sectors', SECTORS)]):
        R, Rex, rf = us_monthly(syms)
        X = Rex.values[-WINDOW:]
        ev = np.sort(np.linalg.eigvalsh(np.corrcoef(X.T)))[::-1]
        N = len(syms)
        c = N / WINDOW
        lo, hi = mp_bounds(c)
        k = np.arange(1, N + 1)
        ax.axhspan(lo, hi, color=LightGray, alpha=0.6, label='Marchenko-Pastur noise band')
        ax.axhline(1, color=Gray, lw=0.6, ls=':')
        inside = (ev >= lo) & (ev <= hi)
        ax.plot(k[inside], ev[inside], 'o', color=MainBlue, ms=5, label='Eigenvalue inside the band')
        ax.plot(k[~inside], ev[~inside], 'D', color=IDAred, ms=5, label='Eigenvalue outside the band')
        ax.set_yscale('log')
        ax.set_xticks(k if N < 10 else k[::3])
        ax.set_xlabel('Eigenvalue rank')
        ax.set_title(f'{u}: N = {N}, T = {WINDOW}, c = N/T = {c:.2f}', fontsize=9, loc='left')
        res[u] = dict(N=N, T=WINDOW, c=c, lo=lo, hi=hi, ev=ev.tolist(), n_above=int((ev > hi).sum()),
                      n_below=int((ev < lo).sum()), share_top=float(ev[0] / N),
                      start=str(Rex.index[-WINDOW].date()), end=str(Rex.index[-1].date()))
    axes[0].set_ylabel('Eigenvalue of the correlation matrix (log)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False)
    fig.suptitle(f'Last 60-month window, {Rex.index[-WINDOW]:%b %Y} - {Rex.index[-1]:%b %Y}', fontsize=9, x=0.02, ha='left')
    plt.tight_layout()
    save_fig('ch4_mp')
    return res


def nl_shrink(X):
    """Shrinkage neliniar analitic (Ledoit & Wolf 2020, Annals of Statistics), cazul N <= T-1."""
    X = np.asarray(X, float)
    X = X - X.mean(0)
    n, p = X.shape
    n = n - 1                                               # corectie pentru centrare
    S = X.T @ X / n
    lam, U = np.linalg.eigh(S)
    lam = np.maximum(lam, 1e-18)
    L = np.tile(lam[:, None], (1, p))
    h = n ** (-1 / 3)
    H = h * L.T
    x = (L - L.T) / H
    ft = (3 / 4 / np.sqrt(5)) * np.mean(np.maximum(1 - x ** 2 / 5, 0) / H, axis=1)
    with np.errstate(divide='ignore', invalid='ignore'):
        Hf = (-3 / 10 / np.pi) * x + (3 / 4 / np.sqrt(5) / np.pi) * (1 - x ** 2 / 5) * \
            np.log(np.abs((np.sqrt(5) - x) / (np.sqrt(5) + x)))
    edge = np.isclose(np.abs(x), np.sqrt(5))
    Hf[edge] = (-3 / 10 / np.pi) * x[edge]
    Hft = np.mean(Hf / H, axis=1)
    c = p / n
    d = lam / ((np.pi * c * lam * ft) ** 2 + (1 - c - np.pi * c * lam * Hft) ** 2)
    return U @ np.diag(d) @ U.T


def gmv_nl_backtests():
    """GMV cu shrinkage neliniar (LW 2020) vs GMV si GMV-LW, aceeasi fereastra rulanta de 60 de luni."""
    out = {}
    for u in ['Sectors', 'Combined']:
        R, Rex, rf = us_monthly(UNIVERSES[u])
        ret, to, W = backtest(R, Rex, strategies=['GMV', 'GMV-LW', 'GMV-NL'])
        out[u] = {s: dict(vol=float(ret[s].std() * np.sqrt(12)), sharpe=float(sharpe(ret[s])),
                          turnover=float(to[s].mean())) for s in ret.columns}
        out[u]['var_ratio_nl_gmv'] = float(ret['GMV-NL'].var() / ret['GMV'].var())
        out[u]['var_ratio_nl_lw'] = float(ret['GMV-NL'].var() / ret['GMV-LW'].var())
    return out


def lo_sharpe(r, q=12):
    """Lo (2002): eroarea standard i.i.d. a raportului Sharpe lunar si factorul de anualizare cu autocorelatii."""
    r = np.asarray(r, float)
    T = len(r)
    sr = r.mean() / r.std()
    se_iid = np.sqrt((1 + sr ** 2 / 2) / T)
    rc = r - r.mean()
    rho = np.array([np.sum(rc[k:] * rc[:-k]) / np.sum(rc ** 2) for k in range(1, q)])
    eta = q / np.sqrt(q + 2 * np.sum((q - np.arange(1, q)) * rho))
    return dict(T=T, sr_m=float(sr), se_m=float(se_iid), sr_ann_sqrt=float(sr * np.sqrt(q)),
                se_ann=float(se_iid * np.sqrt(q)), eta=float(eta), sr_ann_lo=float(sr * eta),
                rho1=float(rho[0]), rho_sum=float(rho.sum()))


def deflated_sharpe(rets):
    """Bailey & Lopez de Prado (2014): raportul Sharpe deflatat al celei mai bune reguli din N incercari.
    rets: dict {nume: serie de randamente lunare in exces}."""
    names = list(rets)
    srs = np.array([np.mean(rets[k]) / np.std(rets[k], ddof=1) for k in names])
    N = len(srs)
    gam = 0.5772156649
    sr0 = np.sqrt(srs.var(ddof=1)) * ((1 - gam) * stats.norm.ppf(1 - 1 / N) + gam * stats.norm.ppf(1 - 1 / (N * np.e)))
    k = int(np.argmax(srs))
    r = np.asarray(rets[names[k]], float)
    T = len(r)
    g3, g4 = stats.skew(r), stats.kurtosis(r, fisher=False)
    s = srs[k]
    z = (s - sr0) * np.sqrt(T - 1) / np.sqrt(1 - g3 * s + (g4 - 1) / 4 * s ** 2)
    psr0 = stats.norm.cdf(s * np.sqrt(T - 1) / np.sqrt(1 - g3 * s + (g4 - 1) / 4 * s ** 2))
    sens = {}
    for n_eff in (3, 8, N):                  # numarul efectiv de incercari independente (N brut = limita superioara)
        s0 = np.sqrt(srs.var(ddof=1)) * ((1 - gam) * stats.norm.ppf(1 - 1 / n_eff) + gam * stats.norm.ppf(1 - 1 / (n_eff * np.e)))
        zz = (s - s0) * np.sqrt(T - 1) / np.sqrt(1 - g3 * s + (g4 - 1) / 4 * s ** 2)
        sens[n_eff] = dict(sr0_ann=float(s0 * np.sqrt(12)), dsr=float(stats.norm.cdf(zz)))
    return dict(N=N, best=names[k], sr_best_ann=float(s * np.sqrt(12)), sr0_ann=float(sr0 * np.sqrt(12)), n_eff=sens,
                T=T, skew=float(g3), kurt=float(g4), dsr=float(stats.norm.cdf(z)), psr0=float(psr0),
                sd_sr_ann=float(np.sqrt(srs.var(ddof=1)) * np.sqrt(12)))


# =============================================================================
# FIG 14: Portofoliu de blue chips BVB vs BET-TR si BET (RON)
# =============================================================================
BVB_STRATS = ['1/N', 'MV-LO', 'GMV-LO', 'GMV-LW', 'ERC', 'HRP']


def bvb_backtest(window=36):
    m, removed = bvb_monthly()
    R = m[BVB]
    ret, to, W = backtest(R, R, window=window, strategies=BVB_STRATS)
    bench = m.loc[ret.index, ['BET-TR', 'BET']]
    return ret, to, W, bench, removed, m


def fig_bvb(bb, n_jobs=1, blocks=None):
    ret, to, W, bench, removed, m = bb
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for s in BVB_STRATS:
        ax.plot(ret.index, np.cumprod(1 + ret[s]), color=SCOL[s], lw=1.2, label=f'{s} (SR {sharpe(ret[s]):.2f})')
    for b, c, ls in [('BET-TR', 'black', '-'), ('BET', 'black', ':')]:
        ax.plot(bench.index, np.cumprod(1 + bench[b]), color=c, ls=ls, lw=1.4, label=f'{b} (SR {sharpe(bench[b]):.2f})')
    ax.set_ylabel('Growth of 1 RON')
    ax.set_title(f'Eight BVB blue chips, out-of-sample {ret.index[0]:%b %Y} - {ret.index[-1]:%b %Y}, '
                 '36-month window', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.1)
    plt.tight_layout()
    save_fig('ch4_bvb')
    tab = summary(ret, to)
    for b in ['BET-TR', 'BET']:
        tab.loc[b] = dict(mean=bench[b].mean() * 12, vol=bench[b].std() * np.sqrt(12), sharpe=sharpe(bench[b]),
                          turnover=0, mdd=max_drawdown(bench[b]), sharpe_10bp=sharpe(bench[b]),
                          sharpe_50bp=sharpe(bench[b]))
    res = run_tests({s: (ret[s], bench['BET-TR']) for s in BVB_STRATS}, n_jobs, blocks)
    tests = {s: res[s][0] for s in BVB_STRATS}
    return dict(table=tab.round(4).to_dict(orient='index'), tests=tests, removed=removed,
                start=str(ret.index[0].date()), end=str(ret.index[-1].date()), T=len(ret),
                corr_mean=float(m[BVB].corr().values[np.triu_indices(len(BVB), 1)].mean()),
                w_last={s: W[s].iloc[-1].round(3).to_dict() for s in BVB_STRATS})


# =============================================================================
# STUDIU DE CAZ: FRONTIERA EFICIENTA IMPLEMENTABILA (Jensen, Kelly, Malamud & Pedersen 2026)
# =============================================================================
JKMP_STOCKS = ['JPM', 'BAC', 'C', 'GS', 'MS', 'WFC', 'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'CSCO', 'GME', 'MSTR']
JKMP_ASSETS = [s + '.US' for s in JKMP_STOCKS + SECTORS]
JKMP_MKT = 'SPY.US'
JKMP_GAMMA = 10.0                 # aversiunea la risc (Sectiunea 5.1)
JKMP_W2020 = 1e10                 # averea la sfarsitul lui 2020, creste odata cu piata
JKMP_NLAG = 12
JKMP_LAMBDAS = np.r_[0.0, np.exp(np.arange(-10, 10.0001, 0.2))]      # Tabelul 1
JKMP_PS = [2 ** 6, 2 ** 7, 2 ** 8, 2 ** 9]
JKMP_ETAS = [np.exp(-3), np.exp(-2)]
JKMP_VAL_START, JKMP_TEST_START, JKMP_END = 2011, 2014, '2026-08-31'
JKMP_SEED = 20260929
# Tabelul 2 din Jensen, Kelly, Malamud & Pedersen (2026): raportul Sharpe net si utilitatea (gamma = 10)
JKMP_TABLE2 = {'Portfolio-ML': (1.33, 0.086), 'Multiperiod-ML*': (0.83, 0.020), 'Static-ML*': (0.81, 0.030),
               '1/N': (0.54, -0.051), 'Market': (0.51, -0.033)}
JKMP_COL = {'Portfolio-ML': MainBlue, 'Multiperiod-ML*': Forest, 'Static-ML*': Orange, 'Static-ML': Orange,
            '1/N': EWcol, 'Market': Purple, 'Minimum variance': Amber, 'Markowitz-ML': IDAred}


def jkmp_split_adjusted(d):
    """Pretul ajustat doar pentru split-uri (pentru volumul in dolari)."""
    raw = d['close'].astype(float)
    adj = d['adjusted_close'].astype(float)
    ratio = (adj / adj.shift(1)) / (raw / raw.shift(1))
    fac = ratio.where((ratio > 1.4) | (ratio < 0.7), 1.0).fillna(1.0).round(3)
    cum_future = fac[::-1].cumprod()[::-1].shift(-1).fillna(1.0)
    return raw / cum_future


def jkmp_ew_cov(R, hl_corr=378, hl_var=126):
    """Covarianta cu ponderi exponentiale: timp de injumatatire 378 zile (corelatii), 126 zile (variante)."""
    j = np.arange(len(R))[::-1]
    def wts(hl):
        w = 0.5 ** (j / hl)
        return w / w.sum()
    X = R.values - R.values.mean(0)
    wc, wv = wts(hl_corr), wts(hl_var)
    C = (X * wc[:, None]).T @ X
    sd_c = np.sqrt(np.diag(C))
    corr = C / np.outer(sd_c, sd_c)
    sd = np.sqrt((X ** 2 * wv[:, None]).sum(0))
    return corr * np.outer(sd, sd)


def jkmp_replication():
    """Portfolio-ML, Static-ML, Markowitz-ML, varianta minima si 1/N cu costul eq. (35), pe datele cursului."""
    A, N, GAMMA = JKMP_ASSETS, len(JKMP_ASSETS), JKMP_GAMMA
    frames, dv = {}, {}
    for s in A + [JKMP_MKT]:
        d = read_market(s)
        frames[s] = d['adjusted_close'].astype(float).rename(s)
        dv[s] = (jkmp_split_adjusted(d) * d['volume'].astype(float)).rename(s)
    P = pd.concat(frames.values(), axis=1).dropna()                  # join pe preturi, zile comune
    DV = pd.concat(dv.values(), axis=1).reindex(P.index)
    rd = P.pct_change().dropna()
    me = P.resample('ME').last()
    rm = me.pct_change().dropna()
    rf = french_rf().reindex(rm.index, method='ffill').ffill()
    last_full = pd.Timestamp(JKMP_END)
    months = rm.index[rm.index <= last_full]
    rx = rm[A].sub(rf, axis=0)
    mret = rm[JKMP_MKT]
    # semnale: ranguri transversale in [0, 1] (Sectiunea 5.1.2)
    lp = np.log(me[A])
    sig = {'ret_1_0': lp - lp.shift(1), 'ret_6_1': lp.shift(1) - lp.shift(6),
           'ret_12_1': lp.shift(1) - lp.shift(12),
           'rvol_252d': rd[A].rolling(252).std().resample('ME').last(),
           'dolvol_126d': np.log(DV[A].rolling(126).mean().resample('ME').last())}
    names = list(sig)
    K = len(names)
    S = {}
    for t in months:
        vals = np.column_stack([sig[k].reindex([t]).values.ravel() for k in names])
        if not np.isnan(vals).any():
            S[t] = (pd.DataFrame(vals).rank(axis=0).values - 1) / (N - 1)
    smonths = [t for t in months if t in S]
    # Sigma lunar, Lambda (eq. 35), averea, g (eq. 6), m (Lema 1, eq. 14)
    dvm = DV[A].rolling(126).mean().resample('ME').last()
    cum = (1 + mret).cumprod()
    w = JKMP_W2020 * cum / cum.loc['2020-12-31']
    g = pd.DataFrame((1 + rf.values[:, None] + rx.values) / (1 + mret.values[:, None]), index=rm.index, columns=A)
    Sig, Lam, Mmat = {}, {}, {}
    for t in smonths:
        Sig[t] = jkmp_ew_cov(rd[A].loc[:t].iloc[-2520:]) * 21
        Lam[t] = 0.2 / dvm.loc[t].values
        wl = w.loc[t] * Lam[t]
        Lh = 1 / np.sqrt(wl)
        X = GAMMA * (Lh[:, None] * Sig[t] * Lh[None, :])
        gh = g.loc[:t].values
        G = gh.T @ gh / len(gh)
        mt = np.eye(N) * 0.5
        for _ in range(500):
            new = np.linalg.inv(X + np.eye(N) + (np.eye(N) - mt) * G)
            new = (new + new.T) / 2
            done = np.abs(new - mt).max() < 1e-12
            mt = new
            if done:
                break
        sl = np.sqrt(wl)
        Mmat[t] = (1 / sl)[:, None] * mt * sl[None, :]
    idx = list(rm.index)
    nxt = {t: idx[idx.index(t) + 1] for t in smonths
           if idx.index(t) + 1 < len(idx) and idx[idx.index(t) + 1] <= last_full}
    dec = [t for t in smonths if t in nxt]

    def evaluate(pis, months_eval):
        rows = []
        for t in months_eval:
            p = pis[t]
            pprev = pis.get(idx[idx.index(t) - 1], np.zeros(N))
            trade = p - g.loc[t].values * pprev
            tc = 0.5 * w.loc[t] * float(trade @ (Lam[t] * trade))
            rows.append((float(rx.loc[nxt[t]].values @ p), tc, np.abs(trade).sum(), np.abs(p).sum()))
        a = np.array(rows)
        net = a[:, 0] - a[:, 1]
        return dict(R=12 * a[:, 0].mean(), Vol=np.sqrt(12) * a[:, 0].std(ddof=1),
                    SRg=np.sqrt(12) * a[:, 0].mean() / a[:, 0].std(ddof=1), TC=12 * a[:, 1].mean(),
                    RTC=12 * net.mean(), VolN=np.sqrt(12) * net.std(ddof=1),
                    SRn=np.sqrt(12) * net.mean() / net.std(ddof=1),
                    U=12 * net.mean() - GAMMA / 2 * 12 * net.var(ddof=1),
                    Turn=a[:, 2].mean(), Lev=a[:, 3].mean(), n=len(a)), net

    def util_flow(pis, months_eval):
        _, net = evaluate(pis, months_eval)
        return 12 * net - GAMMA / 2 * 12 * (net - net.mean()) ** 2

    test = [t for t in dec if t.year >= JKMP_TEST_START]
    val_all = [t for t in dec if t.year >= JKMP_VAL_START]
    rng = np.random.default_rng(JKMP_SEED)
    Wdraw = {(p, e): rng.normal(0, 1, (K, p // 2)) * e for p in JKMP_PS for e in JKMP_ETAS}

    def rf_feat(s, p, e):
        z = s @ Wdraw[(p, e)]
        return np.hstack([np.sin(z), np.cos(z)]) / np.sqrt(p)

    # Portfolio-ML (Propozitia 4, eq. 24-26, 40)
    pml_val = {}
    for p in JKMP_PS:
        for e in JKMP_ETAS:
            F = {}
            for t in smonths:
                Z = rf_feat(S[t], p, e)
                Z = Z - Z.mean(0)
                Z = np.hstack([Z / np.sqrt((Z ** 2).sum(0)), np.ones((N, 1)) / np.sqrt(N)])
                F[t] = Z / np.sqrt(np.diag(Sig[t]))[:, None]
            St = {}
            for k, t in enumerate(smonths):
                if k < JKMP_NLAG - 1:
                    continue
                m = Mmat[t]
                Im = np.eye(N) - m
                acc = Im @ F[t]
                Mprod = np.eye(N)
                for th in range(1, JKMP_NLAG):
                    Mprod = Mprod @ (m * g.loc[smonths[k - th + 1]].values[None, :])
                    acc = acc + Mprod @ Im @ F[smonths[k - th]]
                St[t] = acc
            tl = [t for t in dec if t in St]
            rt, Sg = {}, {}
            for t in tl:
                s_ = St[t]
                D = s_ - g.loc[t].values[:, None] * St.get(idx[idx.index(t) - 1], np.zeros_like(s_))
                rt[t] = s_.T @ rx.loc[nxt[t]].values
                Sg[t] = GAMMA * s_.T @ Sig[t] @ s_ + w.loc[t] * D.T @ (Lam[t][:, None] * D)
            for y in range(JKMP_VAL_START, 2027):
                tr = [t for t in tl if nxt[t].year < y]
                if len(tr) < 24:
                    continue
                Abar = sum(Sg[t] for t in tr) / len(tr)
                bbar = sum(rt[t] for t in tr) / len(tr)
                ev, V = np.linalg.eigh((Abar + Abar.T) / 2)
                Vb = V.T @ bbar
                ym = [t for t in tl if t.year == y]
                for lam in JKMP_LAMBDAS:
                    beta = V @ (Vb / np.maximum(ev + lam, 1e-18))
                    d = pml_val.setdefault((p, e, lam), {})
                    for t in ym:
                        d[t] = St[t] @ beta
    pml, choice = {}, {}
    for y in range(JKMP_TEST_START, 2027):
        best, bh = -np.inf, None
        vm = [t for t in val_all if t.year < y]
        for h, d in pml_val.items():
            if all(t in d for t in vm):
                u = util_flow(d, vm).mean()
                if u > best:
                    best, bh = u, h
        choice[y] = bh
        for t in [t for t in dec if t.year == y]:
            pml[t] = pml_val[bh][t]
    prev0 = idx[idx.index(test[0]) - 1]
    pml[prev0] = pml_val[choice[JKMP_TEST_START]].get(prev0, np.zeros(N))
    # prognoza randamentelor (Markowitz-ML, Static-ML): ridge pe caracteristici Fourier aleatoare
    mu = {}
    for y in range(JKMP_VAL_START - 1, 2027):
        best, bh = np.inf, None
        trm = [t for t in dec if nxt[t].year < y - 3]
        vam = [t for t in dec if y - 3 <= nxt[t].year < y]
        if len(trm) < 24:
            continue
        for p in JKMP_PS:
            for e in JKMP_ETAS:
                Xtr = np.vstack([rf_feat(S[t], p, e) for t in trm])
                ytr = np.concatenate([rx.loc[nxt[t]].values for t in trm])
                Xva = np.vstack([rf_feat(S[t], p, e) for t in vam])
                yva = np.concatenate([rx.loc[nxt[t]].values for t in vam])
                U_, s_, Vt = np.linalg.svd(Xtr, full_matrices=False)
                Uy = U_.T @ ytr
                for lam in JKMP_LAMBDAS:
                    b = Vt.T @ (s_ / (s_ ** 2 + lam + 1e-18) * Uy)
                    mse = np.mean((yva - Xva @ b) ** 2)
                    if mse < best:
                        best, bh = mse, (p, e, lam)
        p, e, lam = bh
        trf = [t for t in dec if nxt[t].year < y]
        Xtr = np.vstack([rf_feat(S[t], p, e) for t in trf])
        ytr = np.concatenate([rx.loc[nxt[t]].values for t in trf])
        U_, s_, Vt = np.linalg.svd(Xtr, full_matrices=False)
        b = Vt.T @ (s_ / (s_ ** 2 + lam + 1e-18) * (U_.T @ ytr))
        for t in [t for t in smonths if t.year == y]:
            mu[t] = rf_feat(S[t], p, e) @ b
    mk, st, mv, ew = {}, {}, {}, {}
    one = np.ones(N)
    prev = None
    for t in [prev0] + test:
        Si = np.linalg.inv(Sig[t])
        mk[t] = Si @ mu[t] / GAMMA                                   # eq. (32)
        mv[t] = Si @ one / (one @ Si @ one)
        ew[t] = one / N
        wl = w.loc[t] * np.diag(Lam[t])                              # eq. (34), phi = 1
        pp = np.zeros(N) if prev is None else g.loc[t].values * st[prev]
        st[t] = np.linalg.solve(GAMMA * Sig[t] + wl, mu[t] + wl @ pp)
        prev = t
    res, flows = {}, {}
    for name, d in [('Portfolio-ML', pml), ('Static-ML', st), ('Markowitz-ML', mk),
                    ('Minimum variance', mv), ('1/N', ew)]:
        res[name], _ = evaluate(d, test)
        flows[name] = util_flow(d, test)
    prob = {}
    for a_ in flows:
        for b_ in flows:
            if a_ != b_:
                dd = flows[a_] - flows[b_]
                prob[f'{a_} > {b_}'] = float(stats.norm.cdf(dd.mean() / (dd.std(ddof=1) / np.sqrt(len(dd)))))
    return dict(start=f'{nxt[test[0]]:%Y-%m}', end=f'{nxt[test[-1]]:%Y-%m}', n_months=len(test), res=res,
                prob=prob, choice={y: [float(v) for v in h] for y, h in choice.items()})


def fig_jkmp_paper():
    """Tabelul 2 din Jensen, Kelly, Malamud & Pedersen (2026): raportul Sharpe net si utilitatea."""
    names = list(JKMP_TABLE2)
    cols = [JKMP_COL[n] for n in names]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3))
    for ax, j, lab in [(axes[0], 0, 'Net Sharpe ratio'), (axes[1], 1, r'Utility, $\gamma = 10$')]:
        v = [JKMP_TABLE2[n][j] for n in names]
        bars = ax.barh(range(len(names)), v, color=cols, height=0.62)
        ax.axvline(0, color=Gray, lw=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names if j == 0 else [])
        ax.invert_yaxis()
        ax.set_xlabel(lab)
        span = max(v) - min(0, min(v))
        for b, x in zip(bars, v):
            ax.text(x + (0.02 * span if x >= 0 else -0.02 * span), b.get_y() + b.get_height() / 2,
                    f'{x:.2f}' if j == 0 else f'{x:.3f}', va='center', ha='left' if x >= 0 else 'right',
                    fontsize=8, color='black')
        ax.set_xlim(min(0, min(v)) - 0.25 * span if min(v) < 0 else 0, max(v) + 0.22 * span)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cols]
    fig.legend(handles, names, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=5, frameon=False)
    fig.suptitle('Out of sample 1981-2020, US stocks, wealth \\$10 billion (Markowitz-ML off scale)',
                 fontsize=9, x=0.02, ha='left')
    plt.tight_layout()
    save_fig('ch4_jkmp_paper')
    return JKMP_TABLE2


def fig_jkmp_replication(out):
    """Planul risc-randament: brut (gol) si net de costuri (plin), cu curbe de utilitate constanta."""
    res = out['res']
    names = ['Portfolio-ML', 'Static-ML', 'Minimum variance', '1/N']
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    s = np.linspace(0, 0.34, 200)
    for u, ls in [(res['Portfolio-ML']['U'], '--'), (0.0, ':')]:
        ax.plot(s, u + JKMP_GAMMA / 2 * s ** 2, color=MainBlue, ls=ls, lw=0.9,
                label=f'Utility = {u:.3f} ($\\gamma = 10$)')
    ax.axhline(0, color=Gray, lw=0.5)
    for n in names:
        r = res[n]
        c = JKMP_COL[n]
        ax.annotate('', xy=(r['VolN'], r['RTC']), xytext=(r['Vol'], r['R']),
                    arrowprops=dict(arrowstyle='->', color=c, lw=1.0))
        ax.scatter(r['Vol'], r['R'], s=40, facecolors='none', edgecolors=c, lw=1.2, zorder=3)
        ax.scatter(r['VolN'], r['RTC'], s=40, color=c, zorder=3,
                   label=f"{n}: net SR {r['SRn']:.2f}, utility {r['U']:.3f}")
    ax.scatter([], [], s=40, facecolors='none', edgecolors='black', label='Gross of costs (hollow)')
    ax.set_xlim(0, 0.34)
    ax.set_ylim(-0.42, 0.30)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    ax.set_xlabel('Annualised volatility')
    ax.set_ylabel('Annualised excess return')
    ax.set_title(f"14 US stocks + 9 sector ETFs, out of sample {pd.Timestamp(out['start']):%b %Y} - "
                 f"{pd.Timestamp(out['end']):%b %Y}, wealth \\$10 billion in 2020 (Markowitz-ML off scale)",
                 fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    plt.tight_layout()
    save_fig('ch4_jkmp_replication')
    return {n: {k: res[n][k] for k in ('R', 'Vol', 'RTC', 'VolN', 'SRg', 'SRn', 'U', 'TC')} for n in res}


# =============================================================================
# MAIN
# =============================================================================
def to_py(o):
    if isinstance(o, dict):
        return {str(k): to_py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return to_py(o.tolist())
    if isinstance(o, pd.DataFrame):
        return to_py(o.to_dict(orient='index'))
    return o


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    print('Chapter 4 charts')
    R = {}
    R['two_asset'] = fig_two_asset()
    R['frontier'] = fig_frontier()
    R['estimation_error'] = fig_estimation_error()
    R['window_length'] = fig_window_length()
    R['shrinkage'] = fig_shrinkage()
    R['black_litterman'] = fig_black_litterman()
    R['risk_contrib'] = fig_risk_contrib()
    R['hrp'] = fig_hrp()
    bts = run_backtests()
    tabs = {}
    for u, (ret, to, W) in bts.items():
        t = summary(ret, to)
        t.attrs = dict(start=f'{ret.index[0]:%Y-%m}', end=f'{ret.index[-1]:%Y-%m}')
        tabs[u] = t
        print(u, t.attrs)
        print(t.round(3))
    R['oos'] = {u: dict(table=t.round(4).to_dict(orient='index'), **t.attrs, T=len(bts[u][0])) for u, t in tabs.items()}
    R['rolling_weights'] = fig_rolling_weights(bts['Sectors'])
    fig_oos_cum(bts)
    fig_oos_sharpe(tabs)
    fig_costs(bts)
    NJ = max(1, (os.cpu_count() or 2) - 2)
    R['sharpe_tests'], draws = sharpe_tests(bts, n_jobs=NJ)
    R['sharpe_test_fig'] = fig_sharpe_test(R['sharpe_tests'], draws)
    R['holm'] = holm_sharpe(R['sharpe_tests'])
    R['bvb'] = fig_bvb(bvb_backtest(), n_jobs=NJ)
    # nivel master: inferenta pe portofolii estimate
    R_s, Rex_s, _ = us_monthly(SECTORS)
    R['britten_jones'] = britten_jones(Rex_s)
    R['kz_bias'] = kz_bias(R['frontier']['sharpe']['tan'], len(SECTORS), 60)
    R['theta2_unbiased'] = theta2_unbiased(Rex_s)
    R['mp'] = fig_mp()
    R['gmv_nl'] = gmv_nl_backtests()
    R['lo_sharpe'] = {u: lo_sharpe(bts[u][0]['1/N']) for u in bts}
    R['deflated_sharpe'] = deflated_sharpe({f'{u}: {s}': bts[u][0][s].values for u in bts for s in STRATS})
    R['jkmp_paper'] = fig_jkmp_paper()
    R['jkmp'] = jkmp_replication()
    R['jkmp']['chart'] = fig_jkmp_replication(R['jkmp'])
    with open(os.path.join(HERE, 'ch4_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print(json.dumps(to_py(R), indent=1, default=str)[:30000])

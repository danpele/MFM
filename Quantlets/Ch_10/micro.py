"""
micro.py -- Estimatori de lichiditate si modele de microstructura (Capitolul 10, MFM)
====================================================================================
  * roll_spread            -- Roll (1984): s = 2 sqrt(-Cov(dp_t, dp_{t-1}))
  * cs_spread              -- Corwin si Schultz (2012): din maximele si minimele a doua perioade consecutive
  * ar_spread              -- Abdi si Ranaldo (2017): din inchidere si mijlocul intervalului maxim-minim
  * amihud                 -- Amihud (2002): |r| / valoarea tranzactionata
  * walk_book              -- executia unui ordin la piata pe un registru de ordine dat
  * gm_quotes, gm_simulate -- Glosten si Milgrom (1985): cotatiile unui formator de piata care invata
  * kyle                   -- Kyle (1985): echilibrul cu un singur interval de tranzactionare
  * ac_trajectory, ac_frontier -- Almgren si Chriss (2001): executia optima a unui ordin mare
  * zi_simulate            -- registru de ordine simulat cu fluxuri aleatoare (model cu inteligenta zero)

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import numpy as np
import pandas as pd


# =============================================================================
# ESTIMATORI DE SPREAD SI DE LICHIDITATE
# =============================================================================
def roll_spread(close):
    """Spread-ul relativ Roll din covarianta de ordinul 1 a randamentelor log; NaN daca covarianta este pozitiva."""
    r = np.log(np.asarray(close, float))
    dp = np.diff(r)
    c = np.mean((dp[1:] - dp.mean()) * (dp[:-1] - dp.mean()))
    return (2 * np.sqrt(-c) if c < 0 else np.nan), c


def cs_spread(high, low):
    """Estimatorul Corwin-Schultz pentru fiecare pereche de perioade consecutive (valorile negative devin 0)."""
    h, l = np.log(np.asarray(high, float)), np.log(np.asarray(low, float))
    beta = (h[:-1] - l[:-1]) ** 2 + (h[1:] - l[1:]) ** 2
    gamma = (np.maximum(h[:-1], h[1:]) - np.minimum(l[:-1], l[1:])) ** 2
    k = 3 - 2 * np.sqrt(2)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / k - np.sqrt(gamma / k)
    return np.clip(2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha)), 0, None)


def ar_terms(close, high, low):
    """Termenii Abdi-Ranaldo: 4 (c_t - eta_t)(c_t - eta_{t+1}); media lor estimeaza s^2."""
    c = np.log(np.asarray(close, float))
    eta = (np.log(np.asarray(high, float)) + np.log(np.asarray(low, float))) / 2
    return 4 * (c[:-1] - eta[:-1]) * (c[:-1] - eta[1:])


def ar_spread(close, high, low):
    """Spread-ul relativ Abdi-Ranaldo: sqrt(max(media termenilor, 0))."""
    m = np.mean(ar_terms(close, high, low))
    return np.sqrt(max(m, 0.0)), m


def amihud(r, dv, scale=1e6):
    """Iliciditatea Amihud: media |r| (puncte de baza) la 1 milion USD tranzactionat."""
    x = pd.concat([r.rename('r'), dv.rename('dv')], axis=1, join='inner').dropna()
    x = x[x['dv'] > 0]
    return float((1e4 * x['r'].abs() / (x['dv'] / scale)).mean())


def daily_estimates(d):
    """Estimatorii de spread pe o fereastra de bare (o zi de bare intraday sau o perioada de date zilnice)."""
    rs, cov = roll_spread(d['close'])
    cs = cs_spread(d['high'], d['low'])
    ar2 = ar_terms(d['close'], d['high'], d['low'])
    return pd.Series(dict(cov=cov, roll=rs, cs=cs.mean(), ar2=ar2.mean()))


# =============================================================================
# REGISTRUL DE ORDINE
# =============================================================================
def walk_book(asks, qty):
    """Ordin de cumparare la piata de marime qty pe ofertele de vanzare asks = [(pret, cantitate), ...] crescator.
    Intoarce executiile, pretul mediu ponderat si ofertele ramase."""
    fills, left, rest = [], qty, []
    for p, q in asks:
        if left <= 0:
            rest.append((p, q))
            continue
        take = min(q, left)
        fills.append((p, take))
        left -= take
        if q > take:
            rest.append((p, q - take))
    vwap = sum(p * q for p, q in fills) / sum(q for _, q in fills)
    return fills, vwap, rest, left


# =============================================================================
# GLOSTEN-MILGROM (1985)
# =============================================================================
def gm_quotes(theta, mu, vl, vh):
    """Cotatiile ask si bid: asteptarea valorii conditionat de o cumparare, respectiv de o vanzare.
    theta = P(V = vh), mu = ponderea investitorilor informati; cei neinformati cumpara sau vand cu prob. 1/2."""
    pb_h, pb_l = mu + (1 - mu) / 2, (1 - mu) / 2               # P(cumparare | V = vh), P(cumparare | V = vl)
    th_b = pb_h * theta / (pb_h * theta + pb_l * (1 - theta))   # P(V = vh | cumparare)
    th_s = pb_l * theta / (pb_l * theta + pb_h * (1 - theta))   # P(V = vh | vanzare)
    return vl + th_b * (vh - vl), vl + th_s * (vh - vl), th_b, th_s


def gm_simulate(mu, vl=90.0, vh=110.0, v=110.0, n=60, seed=1):
    """Un sir de tranzactii cand valoarea adevarata este v; formatorul de piata invata din fluxul de ordine."""
    rng = np.random.default_rng(seed)
    theta, rows = 0.5, []
    for t in range(n):
        ask, bid, th_b, th_s = gm_quotes(theta, mu, vl, vh)
        informed = rng.random() < mu
        buy = (v == vh) if informed else (rng.random() < 0.5)
        rows.append(dict(t=t, ask=ask, bid=bid, theta=theta, buy=buy))
        theta = th_b if buy else th_s
    return pd.DataFrame(rows)


# =============================================================================
# KYLE (1985), o singura perioada
# =============================================================================
def kyle(sigma_v, sigma_u):
    """Echilibrul Kyle: v ~ N(p0, sigma_v^2), cererea zgomotoasa u ~ N(0, sigma_u^2).
    Strategia informatului x = beta (v - p0), pretul p = p0 + lambda (x + u)."""
    beta = sigma_u / sigma_v
    lam = sigma_v / (2 * sigma_u)
    profit = sigma_v * sigma_u / 2
    return dict(beta=beta, lam=lam, profit=profit, post_var=sigma_v ** 2 / 2)


# =============================================================================
# ALMGREN-CHRISS (2001)
# =============================================================================
def ac_trajectory(X, T, N, sigma, eta, gamma, lam, eps=0.0):
    """Traiectoria optima de lichidare (formulele exacte in timp discret).
    X actiuni de vandut in T zile, N intervale; sigma = volatilitatea pretului (USD / zi^0.5);
    impact temporar h(v) = eps sgn + eta v; impact permanent g(v) = gamma v; lam = aversiunea la risc."""
    tau = T / N
    eta_t = eta - gamma * tau / 2
    t = np.arange(N + 1) * tau
    if lam == 0:
        x = X * (1 - t / T)
    else:
        kt2 = lam * sigma ** 2 / eta_t                       # kappa_tilde^2
        kappa = np.arccosh(kt2 * tau ** 2 / 2 + 1) / tau
        x = X * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)
    n = -np.diff(x)
    E = 0.5 * gamma * X ** 2 + eps * X + eta_t / tau * np.sum(n ** 2)
    V = sigma ** 2 * tau * np.sum(x[1:] ** 2)
    return t, x, E, V


def ac_frontier(X, T, N, sigma, eta, gamma, lams):
    """Frontiera eficienta (abaterea standard, costul asteptat) pentru mai multe aversiuni la risc."""
    out = []
    for lam in lams:
        _, _, E, V = ac_trajectory(X, T, N, sigma, eta, gamma, lam)
        out.append((lam, E, np.sqrt(V)))
    return pd.DataFrame(out, columns=['lam', 'E', 'sd'])


# =============================================================================
# REGISTRU DE ORDINE SIMULAT (model cu inteligenta zero, Farmer, Patelli si Zovko 2005)
# =============================================================================
def zi_simulate(n_events=300_000, L=40, rate_limit=1.0, rate_market=0.25, rate_cancel=0.025, n_ticks=4000, seed=7):
    """Ordine limita (uniform pe L tick-uri de la cotatia opusa), ordine la piata si anulari, toate de o unitate.
    Intoarce seria (mijloc, spread) si instantanee ale registrului."""
    rng = np.random.default_rng(seed)
    bid_q = np.zeros(n_ticks, int)
    ask_q = np.zeros(n_ticks, int)
    mid0 = n_ticks // 2
    bid_q[mid0 - 20:mid0] = 3
    ask_q[mid0 + 1:mid0 + 21] = 3
    rows, snaps, offset = [], [], 0
    for e in range(n_events):
        bb = np.flatnonzero(bid_q)[-1]
        ba = np.flatnonzero(ask_q)[0]
        n_orders = bid_q.sum() + ask_q.sum()
        w = np.array([2 * L * rate_limit, 2 * rate_market, rate_cancel * n_orders])
        u = rng.random() * w.sum()
        side = rng.random() < 0.5
        if u < w[0]:                                   # ordin limita
            k = rng.integers(1, L + 1)
            if side:
                p = ba - k
                bid_q[p] += 1
            else:
                p = bb + k
                ask_q[p] += 1
        elif u < w[0] + w[1]:                          # ordin la piata
            if side:
                ask_q[ba] -= 1 if ask_q[ba] > 0 else 0
            else:
                bid_q[bb] -= 1 if bid_q[bb] > 0 else 0
        else:                                          # anulare a unui ordin existent, ales uniform
            if side and bid_q.sum() > 1:
                idx = rng.choice(np.flatnonzero(bid_q), p=bid_q[bid_q > 0] / bid_q.sum())
                bid_q[idx] -= 1
            elif (not side) and ask_q.sum() > 1:
                idx = rng.choice(np.flatnonzero(ask_q), p=ask_q[ask_q > 0] / ask_q.sum())
                ask_q[idx] -= 1
        if not bid_q.any():
            bid_q[bb] = 1
        if not ask_q.any():
            ask_q[ba] = 1
        bb = np.flatnonzero(bid_q)[-1]
        ba = np.flatnonzero(ask_q)[0]
        if bb < 5 * L or ba > n_ticks - 5 * L:         # recentrare: registrul ramane in mijlocul grilei
            sh = int((bb + ba) / 2 - n_ticks // 2)
            bid_q, ask_q = np.roll(bid_q, -sh), np.roll(ask_q, -sh)
            if sh > 0:
                bid_q[-sh:] = 0
                ask_q[-sh:] = 0
            else:
                bid_q[:-sh] = 0
                ask_q[:-sh] = 0
            offset += sh
        if e % 50 == 0:
            bb = np.flatnonzero(bid_q)[-1]
            ba = np.flatnonzero(ask_q)[0]
            rows.append((e, (bb + ba) / 2 - mid0 + offset, ba - bb))
        if e > n_events // 3 and e % 1000 == 0:
            bb = np.flatnonzero(bid_q)[-1]
            ba = np.flatnonzero(ask_q)[0]
            m = (bb + ba) / 2
            rel = np.arange(n_ticks) - m
            sel = np.abs(rel) <= 30
            snaps.append(pd.DataFrame({'rel': rel[sel], 'bid': bid_q[sel], 'ask': ask_q[sel]}))
    path = pd.DataFrame(rows, columns=['event', 'mid', 'spread'])
    return path, snaps, (bid_q, ask_q)

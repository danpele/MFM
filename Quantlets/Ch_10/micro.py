"""
micro.py -- Estimatori de lichiditate si modele de microstructura (Capitolul 10, MFM)
====================================================================================
  * roll_spread            -- Roll (1984): s = 2 sqrt(-Cov(dp_t, dp_{t-1}))
  * cs_spread              -- Corwin si Schultz (2012): din maximele si minimele a doua perioade consecutive
  * ar_spread              -- Abdi si Ranaldo (2017): din inchidere si mijlocul intervalului maxim-minim
  * edge_spread            -- Ardia, Guidotti si Kroencke (2024): estimatorul EDGE din deschidere, maxim, minim, inchidere
  * amihud                 -- Amihud (2002): |r| / valoarea tranzactionata
  * roll_mc                -- Harris (1990): distributia de selectie a covariantei Roll sub modelul adevarat
  * price_discovery        -- Hasbrouck (1995), Gonzalo si Granger (1995): ponderile informationale dintr-un VECM
  * pin_loglik             -- Easley, Kiefer, O'Hara si Paperman (1996): verosimilitatea PIN, factorizata (Lin si Ke, 2011)
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


def cs_spread(high, low, close=None):
    """Estimatorul Corwin-Schultz pentru fiecare pereche de perioade consecutive (valorile negative devin 0).
    Cu close (date zilnice): ajustarea pentru miscarea de peste noapte din Corwin si Schultz (2012): daca minimul zilei t+1
    este peste inchiderea zilei t, maximul si minimul lui t+1 scad cu diferenta; daca maximul lui t+1 este sub
    inchiderea lui t, ambele cresc cu diferenta. Barele intraday ale aceleiasi sesiuni nu se ajusteaza."""
    H, L = np.asarray(high, float), np.asarray(low, float)
    h0, l0, h1, l1 = H[:-1], L[:-1], H[1:].copy(), L[1:].copy()
    if close is not None:
        c0 = np.asarray(close, float)[:-1]
        up = l1 > c0
        d = np.where(up, l1 - c0, 0.0)
        h1, l1 = h1 - d, l1 - d
        dn = h1 < c0
        d = np.where(dn, c0 - h1, 0.0)
        h1, l1 = h1 + d, l1 + d
    beta = np.log(h0 / l0) ** 2 + np.log(h1 / l1) ** 2
    gamma = np.log(np.maximum(h0, h1) / np.minimum(l0, l1)) ** 2
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


def edge_spread(open_, high, low, close, sign=True):
    """EDGE (Ardia, Guidotti si Kroencke, 2024, JFE 161, 103916): spread-ul relativ din preturile OHLC.
    Transcrierea implementarii de referinta a autorilor (pachetul bidask, licenta MIT). sign=True intoarce estimarea
    cu semn; pentru medii pe mai multe ferestre, autorii recomanda estimarile cu semn cu valorile negative puse la zero."""
    o, h, l, c = (np.log(np.asarray(x, float)) for x in (open_, high, low, close))
    if len(o) < 3:
        return np.nan
    m = (h + l) / 2.
    h1, l1, c1, m1 = h[:-1], l[:-1], c[:-1], m[:-1]
    o, h, l, c, m = o[1:], h[1:], l[1:], c[1:], m[1:]
    r1, r2, r3, r4, r5 = m - o, o - m1, m - c1, c1 - m1, o - c1
    tau = np.where(np.isnan(h) | np.isnan(l) | np.isnan(c1), np.nan, (h != l) | (l != c1))
    po1 = tau * np.where(np.isnan(o) | np.isnan(h), np.nan, o != h)
    po2 = tau * np.where(np.isnan(o) | np.isnan(l), np.nan, o != l)
    pc1 = tau * np.where(np.isnan(c1) | np.isnan(h1), np.nan, c1 != h1)
    pc2 = tau * np.where(np.isnan(c1) | np.isnan(l1), np.nan, c1 != l1)
    pt = np.nanmean(tau)
    po = np.nanmean(po1) + np.nanmean(po2)
    pc = np.nanmean(pc1) + np.nanmean(pc2)
    if np.nansum(tau) < 2 or po == 0 or pc == 0:
        return np.nan
    d1 = r1 - np.nanmean(r1) / pt * tau
    d3 = r3 - np.nanmean(r3) / pt * tau
    d5 = r5 - np.nanmean(r5) / pt * tau
    x1 = -4. / po * d1 * r2 - 4. / pc * d3 * r4
    x2 = -4. / po * d1 * r5 - 4. / pc * d5 * r4
    e1, e2 = np.nanmean(x1), np.nanmean(x2)
    v1, v2 = np.nanmean(x1 ** 2) - e1 ** 2, np.nanmean(x2 ** 2) - e2 ** 2
    vt = v1 + v2
    s2 = (v2 * e1 + v1 * e2) / vt if vt > 0 else (e1 + e2) / 2.
    s = np.sqrt(np.abs(s2))
    return float(s * np.sign(s2)) if sign else float(s)


def roll_mc(c, sigma, T=78, R=20000, seed=42):
    """Harris (1990): simulam modelul Roll (m_t mers aleator cu pasi N(0, sigma^2), q_t = +-1 cu prob. 1/2)
    pe T preturi si calculam covarianta de ordinul 1 a variatiilor (demediate), ca pe date reale."""
    rng = np.random.default_rng(seed)
    p = np.cumsum(rng.normal(0, sigma, (R, T)), axis=1) + c * np.where(rng.random((R, T)) < 0.5, 1, -1)
    dp = np.diff(p, axis=1)
    dm = dp - dp.mean(axis=1, keepdims=True)
    return (dm[:, 1:] * dm[:, :-1]).mean(axis=1)


def price_discovery(y, p=1):
    """VECM bivariat cu vectorul de cointegrare (1, -1) impus: dy_t = a0 + alpha (y1 - y2)_{t-1} + sum Gamma_i dy_{t-i} + e_t.
    Intoarce alpha, statisticile t, ponderea componentei Gonzalo-Granger (alpha_perp normalizat) si limitele
    ponderii informationale Hasbrouck (cele doua ordonari Cholesky)."""
    y = np.asarray(y, float)
    dy = np.diff(y, axis=0)
    z = (y[:, 0] - y[:, 1])[:-1]
    X = np.array([[1.0, z[t]] + [v for i in range(1, p + 1) for v in dy[t - i]] for t in range(p, len(dy))])
    Y = dy[p:]
    B = np.linalg.lstsq(X, Y, rcond=None)[0]
    U = Y - X @ B
    Om = U.T @ U / (len(U) - X.shape[1])
    alpha = B[1]
    se = np.sqrt(np.linalg.inv(X.T @ X)[1, 1] * np.diag(Om))
    ap = np.array([-alpha[1], alpha[0]])                       # alpha_perp: alpha' alpha_perp = 0
    cs = ap / ap.sum()
    psi = ap                                                    # randul comun al impactului pe termen lung (pana la o scala)
    IS = []
    for order in ([0, 1], [1, 0]):
        F = np.linalg.cholesky(Om[np.ix_(order, order)])
        v = (psi[order] @ F) ** 2 / (psi @ Om @ psi)
        IS.append(v[np.argsort(order)])
    IS = np.array(IS)
    return dict(alpha=alpha, t=alpha / se, cs=cs, is_lo=IS.min(axis=0), is_hi=IS.max(axis=0),
                corr=float(Om[0, 1] / np.sqrt(Om[0, 0] * Om[1, 1])), resid=U, n=len(U))


def pin_loglik(B, S, alpha, delta, mu, eb, es):
    """Log-verosimilitatea EKOP pentru o zi cu B cumparari si S vanzari, in forma factorizata care evita
    depasirea numerica (Lin si Ke, 2011): ln L = -eb - es + B ln(mu + eb) + S ln(mu + es) - ln B! - ln S!
    + ln[(1 - alpha) xb^B xs^S + alpha delta e^-mu xb^B + alpha (1 - delta) e^-mu xs^S], xb = eb / (mu + eb)."""
    from scipy.special import gammaln, logsumexp
    lxb, lxs = np.log(eb / (mu + eb)), np.log(es / (mu + es))
    terms = [np.log(1 - alpha) + B * lxb + S * lxs, np.log(alpha * delta) - mu + B * lxb,
             np.log(alpha * (1 - delta)) - mu + S * lxs]
    base = -eb - es + B * np.log(mu + eb) + S * np.log(mu + es) - gammaln(B + 1) - gammaln(S + 1)
    return float(base + logsumexp(terms)), terms


def amihud(r, dv, scale=1e6):
    """Ilichiditatea Amihud: media |r| (puncte de baza) la 1 milion USD tranzactionat."""
    x = pd.concat([r.rename('r'), dv.rename('dv')], axis=1, join='inner').dropna()
    x = x[x['dv'] > 0]
    return float((1e4 * x['r'].abs() / (x['dv'] / scale)).mean())


def daily_estimates(d, overnight=True):
    """Estimatorii de spread pe o fereastra de bare: overnight=True pentru date zilnice (ajustarea Corwin-Schultz
    pentru miscarea de peste noapte), overnight=False pentru barele intraday ale unei sesiuni."""
    rs, cov = roll_spread(d['close'])
    cs = cs_spread(d['high'], d['low'], d['close'] if overnight else None)
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
        else:                                          # anulare a unui ordin existent, ales uniform dintre toate ordinele
            side = rng.random() < bid_q.sum() / n_orders   # partea aleasa proportional cu numarul de ordine in asteptare
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

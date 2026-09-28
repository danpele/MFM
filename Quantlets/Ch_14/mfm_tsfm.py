"""
mfm_tsfm.py -- date, modele de baza, modele fundationale si teste pentru Capitolul 14
====================================================================================
  * load_returns(name)  -- randamente log zilnice in %: S&P 500, Bitcoin, BET (data/market)
  * load_rv()           -- varianta realizata zilnica a SPY (suma patratelor randamentelor la 5 minute, %^2)
  * fm_forecast(...)    -- prognoze zero-shot la o zi: Chronos-2, Chronos-Bolt (small), TimesFM-2.5
  * baseline: medie istorica, AR(1), GARCH(1,1)-t, HS, FHS, HAR-RV, LSTM
  * teste: Kupiec, Christoffersen, pierderea cuantila, FZ0, QLIKE, Diebold-Mariano (HAC), MCS
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')

# nume -> (simbol, data de start); indici si cripto: pretul de inchidere
SOURCES = {'sp500': ('GSPC.INDX', '1990-01-01'), 'btc': ('BTC-USD.CC', '2014-09-17'), 'bet': ('BET', '1997-09-19')}
LABELS = {'sp500': 'S&P 500', 'btc': 'Bitcoin', 'bet': 'BET'}
ASSETS = list(SOURCES)
TEST_FROM = {'sp500': '2016-01-01', 'btc': '2019-01-01', 'bet': '2016-01-01'}
POST_FROM = '2025-11-03'   # dupa publicarea ponderilor tuturor celor trei modele fundationale
CTX = 512                  # lungimea contextului (observatii) pentru modelele fundationale
W = 1000                   # fereastra de estimare pentru HS, GARCH-t, FHS
REFIT = 20                 # reestimarea parametrilor GARCH la fiecare 20 de zile
A_VAR, A_ES = 0.01, 0.025  # VaR 1%, ES 2.5%
FM_NAMES = {'chronos2': 'Chronos-2', 'bolt': 'Chronos-Bolt', 'timesfm': 'TimesFM-2.5'}
FM_REPO = {'chronos2': 'amazon/chronos-2', 'bolt': 'amazon/chronos-bolt-small',
           'timesfm': 'google/timesfm-2.5-200m-pytorch'}
C2_LEVELS = [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
             0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
DEC_LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


# =============================================================================
# DATE
# =============================================================================
def read_market(symbol):
    """Citeste data/market/<SIMBOL>.csv local sau din repo-ul GitHub."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def load_returns(name):
    """Randamente log zilnice in %, pe calendarul propriu al seriei."""
    symbol, start = SOURCES[name]
    p = read_market(symbol)['close'].loc[start:]
    p = p[p > 0].dropna()
    return (100 * np.log(p).diff()).dropna().rename(LABELS[name])


def load_rv():
    """Varianta realizata zilnica a SPY (sesiunea regulata, randamente la 5 minute, %^2)
    si randamentul zilnic close-to-close al SPY (%), pe aceleasi zile."""
    fname = 'intraday/SPY.US_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    d = pd.read_csv(path if os.path.exists(path) else REPO_RAW + fname, parse_dates=['datetime_utc'])
    d['day'] = d['datetime_utc'].dt.normalize()
    d['r'] = 100 * np.log(d['close']).groupby(d['day']).diff()
    rv = (d['r'] ** 2).groupby(d['day']).sum()
    n = d.groupby('day').size()
    rv = rv[n >= 70]                       # fara zilele cu program redus
    rv.index = rv.index.tz_localize(None) if rv.index.tz is not None else rv.index
    rv.name = 'RV'
    return rv


def load_spy_daily():
    """Randamentele zilnice close-to-close ale SPY (%, pret ajustat)."""
    p = read_market('SPY.US')['adjusted_close']
    return (100 * np.log(p).diff()).dropna().rename('SPY')


# =============================================================================
# MODELE FUNDATIONALE (zero-shot)
# =============================================================================
_FM = {}


def load_fm(name):
    """Incarca o singura data modelul fundational (CPU)."""
    if name in _FM:
        return _FM[name]
    import torch
    if name in ('chronos2', 'bolt'):
        from chronos import BaseChronosPipeline
        _FM[name] = BaseChronosPipeline.from_pretrained(FM_REPO[name], device_map='cpu', torch_dtype=torch.float32)
    elif name == 'timesfm':
        import timesfm
        m = timesfm.TimesFM_2p5_200M_torch.from_pretrained(FM_REPO[name])
        m.compile(timesfm.ForecastConfig(max_context=1024, max_horizon=128, normalize_inputs=True,
                                         use_continuous_quantile_head=True, force_flip_invariance=True,
                                         infer_is_positive=False, fix_quantile_crossing=True,
                                         per_core_batch_size=128))
        _FM[name] = m
    else:
        raise ValueError(name)
    return _FM[name]


def fm_forecast(name, contexts, batch=256):
    """Prognoza la o zi pentru o lista de contexte (np.array 1D).
    Rezultat: (levels, Q, point), Q = matrice n x len(levels) de cuantile, point = prognoza punctuala
    (mediana pentru Chronos, media pentru TimesFM)."""
    import torch
    m = load_fm(name)
    Qs, P = [], []
    for i in range(0, len(contexts), batch):
        cb = [np.asarray(c, dtype='float32') for c in contexts[i:i + batch]]
        if name == 'chronos2':
            q, _ = m.predict_quantiles([torch.tensor(c)[None, :] for c in cb], prediction_length=1,
                                       quantile_levels=C2_LEVELS)
            Q = np.stack([qi[0, 0].numpy() for qi in q])
            Qs.append(Q)
            P.append(Q[:, C2_LEVELS.index(0.5)])
        elif name == 'bolt':
            L = max(len(c) for c in cb)
            x = torch.full((len(cb), L), float('nan'))
            for j, c in enumerate(cb):
                x[j, L - len(c):] = torch.tensor(c)
            q, _ = m.predict_quantiles(x, prediction_length=1, quantile_levels=DEC_LEVELS)
            Q = q[:, 0, :].numpy()
            Qs.append(Q)
            P.append(Q[:, DEC_LEVELS.index(0.5)])
        else:
            pf, qf = m.forecast(horizon=1, inputs=cb)
            Qs.append(np.asarray(qf)[:, 0, 1:10])
            P.append(np.asarray(pf)[:, 0])
    levels = C2_LEVELS if name == 'chronos2' else DEC_LEVELS
    return levels, np.vstack(Qs), np.concatenate(P)


def contexts_at(x, origins, ctx=CTX):
    """Contextul x[t-ctx:t] pentru fiecare origine t (pozitie in x)."""
    x = np.asarray(x, float)
    return [x[max(0, t - ctx):t] for t in origins]


def quantile_at(levels, Q, u):
    """Cuantila de nivel u prin interpolare liniara intre nivelurile disponibile; in afara grilei:
    valoarea de la capat (modelul nu ofera cuantile mai extreme)."""
    lv = np.asarray(levels)
    return np.array([np.interp(u, lv, row) for row in Q])


def grid_mean(levels, Q, g=lambda v: v):
    """Aproximarea E[g(Y)] = integrala din g(q_u) pe [0, 1], cu q_u liniar intre niveluri si constant
    in afara grilei (subestimeaza cozile)."""
    lv = np.r_[0.0, levels, 1.0]
    G = g(np.column_stack([Q[:, :1], Q, Q[:, -1:]]))
    return np.trapezoid(G, lv, axis=1)


def es_from_grid(levels, Q, a=A_ES, n=200):
    """ES_a = -(1/a) * integrala_0^a q_u du, pe grila modelului (sub cel mai mic nivel: constant)."""
    u = (np.arange(n) + 0.5) / n * a
    return -np.mean(np.column_stack([quantile_at(levels, Q, ui) for ui in u]), axis=1)


# =============================================================================
# MODELE DE BAZA PENTRU RANDAMENTE
# =============================================================================
def hist_mean(r, origins):
    x = np.asarray(r, float)
    cs = np.r_[0, np.cumsum(x)]
    return np.array([cs[t] / t for t in origins])


def ar1(r, origins, w=W):
    """AR(1) estimat prin MCO pe fereastra mobila de w observatii."""
    x = np.asarray(r, float)
    out = []
    for t in origins:
        y = x[max(0, t - w):t]
        X = np.column_stack([np.ones(len(y) - 1), y[:-1]])
        b = np.linalg.lstsq(X, y[1:], rcond=None)[0]
        out.append(b[0] + b[1] * y[-1])
    return np.array(out)


def garch_t(r, origins, w=W, refit=REFIT):
    """GARCH(1,1) cu inovatii Student-t (medie constanta), fereastra mobila de w observatii,
    parametrii reestimati la fiecare `refit` zile. Rezultat: DataFrame cu mu, sigma, nu la fiecare origine
    si reziduurile standardizate din fereastra (pentru FHS)."""
    from arch import arch_model
    x = np.asarray(r, float)
    rows, Z = [], []
    par = None
    for k, t in enumerate(origins):
        y = x[t - w:t]
        if k % refit == 0 or par is None:
            res = arch_model(y, mean='Constant', vol='GARCH', p=1, q=1, dist='t', rescale=False).fit(
                disp='off', show_warning=False)
            par = res.params.values        # mu, omega, alpha, beta, nu
        mu, om, al, be, nu = par
        e = y - mu
        s2 = np.empty(len(y) + 1)
        s2[0] = e.var()
        for i in range(len(y)):
            s2[i + 1] = om + al * e[i] ** 2 + be * s2[i]
        rows.append((mu, np.sqrt(s2[-1]), nu))
        Z.append(e / np.sqrt(s2[:-1]))
    return pd.DataFrame(rows, columns=['mu', 'sigma', 'nu']), Z


def t_std_q(nu, a):
    """Cuantila de nivel a a distributiei Student-t standardizate (dispersie 1)."""
    return stats.t.ppf(a, nu) * np.sqrt((nu - 2) / nu)


def t_std_es(nu, a):
    """ES_a (pozitiv) al distributiei Student-t standardizate: -E[Z | Z <= q_a]."""
    q = stats.t.ppf(a, nu)
    return stats.t.pdf(q, nu) / a * (nu + q ** 2) / (nu - 1) * np.sqrt((nu - 2) / nu)


def emp_var_es(z, a_var=A_VAR, a_es=A_ES):
    """VaR si ES empirice (pozitive) dintr-un esantion: VaR_a = -q_a, ES_a = -media cozii de probabilitate a."""
    z = np.sort(np.asarray(z))
    n = len(z)
    k = int(np.ceil(a_es * n))
    return -np.quantile(z, a_var), -np.quantile(z, a_es), -z[:k].mean()


def risk_table(r, origins, fm_sigma=None):
    """VaR 1%, VaR 2.5%, ES 2.5% la o zi pentru HS, GARCH-t, FHS si (optional) FHS filtrat cu volatilitatea
    unui model fundational: z = r / sigma_FM pe fereastra de W zile."""
    x = np.asarray(r, float)
    g, Z = garch_t(r, origins)
    out = {}
    hs = np.array([emp_var_es(x[t - W:t]) for t in origins])
    out['HS'] = hs
    gt = np.column_stack([-(g.mu + g.sigma * t_std_q(g.nu, A_VAR)), -(g.mu + g.sigma * t_std_q(g.nu, A_ES)),
                          -g.mu + g.sigma * t_std_es(g.nu, A_ES)])
    out['GARCH-t'] = gt
    fhs = np.array([emp_var_es(z) for z in Z])
    out['FHS'] = np.column_stack([-g.mu.values + g.sigma.values * fhs[:, 0],
                                  -g.mu.values + g.sigma.values * fhs[:, 1],
                                  -g.mu.values + g.sigma.values * fhs[:, 2]])
    if fm_sigma is not None:
        for nm, sig in fm_sigma.items():   # sig: serie aliniata cu x (NaN unde lipseste)
            s = np.asarray(sig, float)
            rows = []
            for t in origins:
                zz = x[t - W:t] / s[t - W:t]
                rows.append(s[t] * np.array(emp_var_es(zz[np.isfinite(zz)])))
            out[nm] = np.array(rows)
    return {k: pd.DataFrame(v, columns=['VaR1', 'VaR2.5', 'ES2.5']) for k, v in out.items()}


# =============================================================================
# VOLATILITATE REALIZATA: HAR
# =============================================================================
def har_design(y):
    """Regresorii HAR: nivelul de ieri, media pe 5 zile si media pe 22 de zile."""
    s = pd.Series(y)
    d = s.shift(1)
    wk = s.rolling(5).mean().shift(1)
    mo = s.rolling(22).mean().shift(1)
    return np.column_stack([np.ones(len(s)), d, wk, mo])


def har(rv, origins, w=500, log=False):
    """Prognoza HAR la o zi (MCO pe fereastra mobila de w zile). log=True: HAR pe log RV,
    cu corectia exp(s^2/2) pentru media."""
    y = np.log(np.asarray(rv, float)) if log else np.asarray(rv, float)
    X = har_design(y)
    out = []
    for t in origins:
        idx = np.arange(max(22, t - w), t)
        b, *_ = np.linalg.lstsq(X[idx], y[idx], rcond=None)
        f = X[t] @ b
        if log:
            s2 = np.var(y[idx] - X[idx] @ b, ddof=4)
            f = np.exp(f + s2 / 2)
        out.append(f)
    return np.array(out)


# =============================================================================
# LSTM (PyTorch, CPU)
# =============================================================================
def make_windows(x, L):
    """Ferestre de lungime L ca intrari si valoarea urmatoare ca tinta."""
    x = np.asarray(x, float)
    idx = np.arange(L, len(x))
    return np.stack([x[i - L:i] for i in idx]), x[idx]


def train_lstm(X, y, hidden=16, epochs=300, lr=3e-3, seed=0, val_frac=0.2, patience=25, weight_decay=1e-4):
    """LSTM cu un strat (intrare univariata, lungime L) + strat liniar; MSE, Adam, oprire timpurie
    pe ultimele val_frac din esantion (ordinea in timp se pastreaza). Rezultat: (functie de prognoza, istoric)."""
    import torch
    import torch.nn as nn
    torch.manual_seed(seed)
    np.random.seed(seed)

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(1, hidden, batch_first=True)
            self.out = nn.Linear(hidden, 1)

        def forward(self, z):
            h, _ = self.lstm(z.unsqueeze(-1))
            return self.out(h[:, -1]).squeeze(-1)

    n = len(y)
    nv = int(val_frac * n)
    Xt, yt = torch.tensor(X[:n - nv], dtype=torch.float32), torch.tensor(y[:n - nv], dtype=torch.float32)
    Xv, yv = torch.tensor(X[n - nv:], dtype=torch.float32), torch.tensor(y[n - nv:], dtype=torch.float32)
    net = Net()
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=weight_decay)
    best, best_state, wait, hist = np.inf, None, 0, []
    for ep in range(epochs):
        net.train()
        perm = torch.randperm(len(yt))
        for i in range(0, len(yt), 256):
            b = perm[i:i + 256]
            opt.zero_grad()
            loss = ((net(Xt[b]) - yt[b]) ** 2).mean()
            loss.backward()
            opt.step()
        net.eval()
        with torch.no_grad():
            lt = float(((net(Xt) - yt) ** 2).mean())
            lv = float(((net(Xv) - yv) ** 2).mean())
        hist.append((lt, lv))
        if lv < best - 1e-7:
            best, wait = lv, 0
            best_state = {k: v.clone() for k, v in net.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                break
    net.load_state_dict(best_state)
    net.eval()

    def predict(Xn):
        with torch.no_grad():
            return net(torch.tensor(np.asarray(Xn), dtype=torch.float32)).numpy()
    return predict, np.array(hist)


def lstm_param_count(d, h, torch_bias=True):
    """Numarul de parametri ai unui strat LSTM: 4 blocuri (3 porti + candidatul) x (h*d + h*h + h);
    PyTorch foloseste doi vectori de deplasare (b_ih, b_hh), deci 4 x (h*d + h*h + 2h)."""
    return 4 * (h * d + h * h + (2 if torch_bias else 1) * h)


# =============================================================================
# FUNCTII DE PIERDERE SI TESTE
# =============================================================================
def qlike(y, f):
    """QLIKE = y/f - log(y/f) - 1 (Patton, 2011): robusta la zgomotul aproximarii volatilitatii."""
    ratio = np.asarray(y) / np.asarray(f)
    return ratio - np.log(ratio) - 1


def pinball(r, q, a):
    """Pierderea cuantila pentru cuantila q de nivel a a randamentului r: (a - 1{r < q})(r - q)."""
    r, q = np.asarray(r), np.asarray(q)
    return (a - (r < q)) * (r - q)


def fz0(L, var, es, a=A_ES):
    """Pierderea FZ0 (Patton, Ziegel & Chen, 2019) pentru pierderi L = -r pozitive, VaR si ES > 0."""
    L, var, es = map(np.asarray, (L, var, es))
    return (L > var) * (L - var) / (a * es) + var / es + np.log(es) - 1


def kupiec(hits, p):
    """Testul POF al lui Kupiec: LR_uc ~ chi2(1)."""
    hits = np.asarray(hits, int)
    T, x = len(hits), hits.sum()
    ph = x / T
    ll0 = (T - x) * np.log(1 - p) + x * np.log(p)
    ll1 = (T - x) * np.log(1 - ph) + x * np.log(ph) if 0 < x < T else 0.0
    lr = -2 * (ll0 - ll1)
    return dict(T=int(T), x=int(x), rate=float(ph), LR=float(lr), p=float(stats.chi2.sf(lr, 1)))


def christoffersen(hits, p):
    """Testul de independenta (lant Markov de ordinul 1) si testul acoperirii conditionate."""
    h = np.asarray(hits, int)
    a, b = h[:-1], h[1:]
    n00, n01 = np.sum((a == 0) & (b == 0)), np.sum((a == 0) & (b == 1))
    n10, n11 = np.sum((a == 1) & (b == 0)), np.sum((a == 1) & (b == 1))

    def xlogy(n, q):
        return n * np.log(q) if n > 0 else 0.0
    pi01 = n01 / max(n00 + n01, 1)
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    l_ind = xlogy(n00, 1 - pi01) + xlogy(n01, pi01) + xlogy(n10, 1 - pi11) + xlogy(n11, pi11)
    l_0 = xlogy(n00 + n10, 1 - pi) + xlogy(n01 + n11, pi)
    lr_ind = -2 * (l_0 - l_ind)
    lr_uc = kupiec(h, p)['LR']
    return dict(n11=int(n11), pi01=float(pi01), pi11=float(pi11), LR_ind=float(lr_ind),
                p_ind=float(stats.chi2.sf(lr_ind, 1)), LR_cc=float(lr_uc + lr_ind),
                p_cc=float(stats.chi2.sf(lr_uc + lr_ind, 2)))


def nw_var(d, lags=None):
    """Varianta pe termen lung (Newey-West, nucleu Bartlett)."""
    d = np.asarray(d, float) - np.mean(d)
    T = len(d)
    if lags is None:
        lags = int(np.floor(4 * (T / 100) ** (2 / 9)))
    v = np.mean(d ** 2)
    for j in range(1, lags + 1):
        v += 2 * (1 - j / (lags + 1)) * np.mean(d[j:] * d[:-j])
    return v


def diebold_mariano(la, lb, lags=None):
    """DM = media(d) / sqrt(LRV/T), d = la - lb; negativ => A are pierderea medie mai mica."""
    d = np.asarray(la, float) - np.asarray(lb, float)
    dm = d.mean() / np.sqrt(nw_var(d, lags) / len(d))
    return dict(dbar=float(d.mean()), DM=float(dm), p=float(2 * stats.norm.sf(abs(dm))))


def mcs(losses, B=1000, block=10, seed=2):
    """Multimea de modele de incredere (Hansen, Lunde & Nason, 2011), statistica T_max,
    bootstrap circular pe blocuri. losses: DataFrame T x m. Rezultat: valorile p ale MCS."""
    rng = np.random.default_rng(seed)
    X = losses.values
    T, m = X.shape
    nb = int(np.ceil(T / block))
    idx = (rng.integers(0, T, (B, nb))[:, :, None] + np.arange(block)) % T
    idx = idx.reshape(B, -1)[:, :T]
    Lbar = X.mean(0)
    Lb = np.stack([X[i].mean(0) for i in idx])
    alive = list(range(m))
    pvals, p_run = {}, 0.0
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
        pvals[losses.columns[worst]] = p_run
        alive.remove(worst)
    pvals[losses.columns[alive[0]]] = 1.0
    return pd.Series(pvals)[losses.columns]


def r2_oos(y, f, bench=None):
    """R^2 in afara esantionului fata de un reper (implicit: prognoza zero)."""
    y, f = np.asarray(y), np.asarray(f)
    b = np.zeros_like(y) if bench is None else np.asarray(bench)
    return 1 - np.sum((y - f) ** 2) / np.sum((y - b) ** 2)


def block_bootstrap_ci(stat, arrays, B=2000, block=20, seed=0, level=0.95):
    """Interval bootstrap pe blocuri circulare (percentile) pentru o statistica a mai multor serii aliniate."""
    rng = np.random.default_rng(seed)
    T = len(arrays[0])
    nb = int(np.ceil(T / block))
    vals = []
    for _ in range(B):
        idx = ((rng.integers(0, T, nb)[:, None] + np.arange(block)) % T).ravel()[:T]
        vals.append(stat(*[np.asarray(a)[idx] for a in arrays]))
    lo, hi = np.quantile(vals, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(lo), float(hi)


def sign_test(y, f):
    """Rata semnelor corecte si valoarea p binomiala bilaterala (H0: 50%)."""
    y, f = np.asarray(y), np.asarray(f)
    keep = (y != 0) & (f != 0)
    k = int(np.sum(np.sign(y[keep]) == np.sign(f[keep])))
    n = int(keep.sum())
    return dict(rate=k / n, n=n, p=float(stats.binomtest(k, n, 0.5).pvalue))

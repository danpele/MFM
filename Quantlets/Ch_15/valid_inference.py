"""
valid_inference.py -- Capitolul 15: scorurile de sentiment sunt estimari; inferenta valida cu ele
=================================================================================================
Foloseste doar tabelele salvate (ch15_twitter_scores.csv, ch15_phrasebank_scores.csv, ch15_news_daily.csv,
ch15_memory_monthly.csv, ai_discovery_case.json); nu ruleaza din nou niciun model de limbaj.
  * atenuarea: corelatia dintre eticheta umana s* si scorul masurat (Twitter), factorul Aigner (1973) pentru
    etichete discrete, corectia pantelor din panelul FNSPID; modelul cu un factor (trei scoruri) si IV
  * inferenta cu etichete LLM: prediction-powered inference (Angelopoulos et al., 2023) pe Twitter
  * calibrarea probabilitatilor: ECE, Brier, log loss, scalarea temperaturii
  * panelul cu 16 actiuni: grupare pe doua dimensiuni, wild cluster bootstrap restrictionat (Cameron, Gelbach &
    Miller, 2008), corectia Holm pe cele 9 regresii si pe cele 3 strategii
  * studiul de eveniment: diferenta pozitiv - negativ cu CI grupat pe zile; testul Boehmer, Musumeci & Poulsen (1991)
  * curba specificatiilor (Simonsohn, Simmons & Nelson, 2020) pe grila de 36 de strategii, cu nul prin schimbarea
    semnului pe blocuri de 10 zile de semnal (bootstrap salbatic dependent, Shao, 2010)
  * testul formal AUC inainte vs dupa publicare (DeLong et al., 1988) si diferenta minima detectabila
  * diferenta diferentelor pentru scurgerea datelor de antrenare, cu CI bootstrap
Iesire: ch15_inference.json si graficele ch15_ppi, ch15_calibration, ch15_spec_curve.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
import mfm_text as M              # noqa: E402
import generate_all_charts as g   # noqa: E402
import ai_discovery_case as A     # noqa: E402

VI = {}
SIGN = {'negative': -1, 'neutral': 0, 'positive': 1}


def net(d, tag):
    return d[f'{tag}_positive'].values - d[f'{tag}_negative'].values


def label_num(d, tag):
    P = d[[f'{tag}_{l}' for l in M.LABELS]].values
    return P.argmax(1) - 1


# =============================================================================
# 1. ATTENUATION: THE SCORE MEASURES TRUE SENTIMENT WITH ERROR
# =============================================================================
def attenuation():
    tw = g.load_csv('ch15_twitter_scores.csv')
    s = tw['label'].map(SIGN).values.astype(float)
    sc = {'lm': tw['LM_tone'].values, 'finbert': net(tw, 'finbert'), 'qwen': net(tw, 'qwen7B')}
    lab = {'lm': M.tone_label(tw['LM_tone'].values), 'finbert': label_num(tw, 'finbert'), 'qwen': label_num(tw, 'qwen7B')}
    lab['lm'] = pd.Series(lab['lm']).map(SIGN).values
    out = {'rho': {}, 'lam_label': {}, 'aigner_neg': {}}
    for c in sc:
        out['rho'][c] = float(np.corrcoef(s, sc[c])[0, 1])
        L = lab[c].astype(float)
        out['lam_label'][c] = float(np.cov(s, L)[0, 1] / np.var(L, ddof=1))
        # Aigner (1973): binary "negative news" variable, misclassification
        t, h = (s == -1), (L == -1)
        pi, p = t.mean(), h.mean()
        a1 = np.mean(~h[t])          # P(predicted non-negative | truly negative)
        a0 = np.mean(h[~t])          # P(predicted negative | truly non-negative)
        lam = pi * (1 - pi) * (1 - a0 - a1) / (p * (1 - p))
        out['aigner_neg'][c] = {'pi': float(pi), 'p': float(p), 'a0': float(a0), 'a1': float(a1), 'lam': float(lam),
                                'lam_direct': float(np.cov(t, h)[0, 1] / np.var(h, ddof=1))}
    VI['atten'] = out
    return out


def news_setup():
    P, rets = g.news_panel()
    return P, rets


def factor_iv(P):
    """One-factor model for the three daily scores and IV with one score as the instrument for another."""
    Z = {c: P[f'z_{c}'].values for c in ('lm', 'finbert', 'qwen')}
    C = np.corrcoef(np.vstack([Z['lm'], Z['finbert'], Z['qwen']]))
    r = {('lm', 'finbert'): C[0, 1], ('lm', 'qwen'): C[0, 2], ('finbert', 'qwen'): C[1, 2]}
    rr = lambda a, b: r[(a, b)] if (a, b) in r else r[(b, a)]    # noqa: E731
    lam = {}
    for c in Z:
        o = [x for x in Z if x != c]
        lam[c] = float(np.sqrt(rr(c, o[0]) * rr(c, o[1]) / rr(o[0], o[1])))
    days = P.index.get_level_values('day')
    codes, uniq = pd.factorize(days)
    y = P['r0'].values
    rng = np.random.default_rng(15)
    out = {'lam_factor': lam, 'corr': {f'{a}|{b}': float(v) for (a, b), v in r.items()}, 'iv': {}}
    B = 999
    Gs = len(uniq)
    # sums by day for the cluster (day) bootstrap
    def sums(v):
        return np.bincount(codes, weights=v, minlength=Gs)
    raw = {'n': np.ones_like(y), 'y': y}
    raw.update({f'z{c}': Z[c] for c in Z})
    raw.update({f'yz{c}': y * Z[c] for c in Z})
    raw.update({f'{a}{b}': Z[a] * Z[b] for a in Z for b in Z})
    base = {k: sums(v) for k, v in raw.items()}

    def iv_from(S, x, zi):
        n = S['n']
        mx, mz, my = S[f'z{x}'] / n, S[f'z{zi}'] / n, S['y'] / n
        return (S[f'yz{zi}'] / n - my * mz) / (S[f'{x}{zi}'] / n - mx * mz)
    pairs = [('qwen', 'finbert'), ('qwen', 'lm'), ('finbert', 'qwen'), ('finbert', 'lm')]
    tot = {k: v.sum() for k, v in base.items()}
    est = {f'{x}|{zi}': float(iv_from(tot, x, zi)) for x, zi in pairs}
    boots = {k: [] for k in est}
    for _ in range(B):
        w = np.bincount(rng.integers(0, Gs, Gs), minlength=Gs)
        Sb = {k: (v * w).sum() for k, v in base.items()}
        for x, zi in pairs:
            boots[f'{x}|{zi}'].append(iv_from(Sb, x, zi))
    for k in est:
        v = np.array(boots[k])
        out['iv'][k] = {'b_bp': 100 * est[k], 'se_bp': 100 * float(v.std(ddof=1)),
                        'lo_bp': 100 * float(np.quantile(v, 0.025)), 'hi_bp': 100 * float(np.quantile(v, 0.975))}
    for x in ('qwen', 'finbert'):
        o = 'finbert' if x == 'qwen' else 'qwen'
        d = np.array(boots[f'{x}|{o}']) - np.array(boots[f'{x}|lm'])
        dd = est[f'{x}|{o}'] - est[f'{x}|lm']
        out['iv'][f'diff_{x}'] = {'d_bp': 100 * dd, 'se_bp': 100 * float(d.std(ddof=1)),
                                  'z': float(dd / d.std(ddof=1))}
    VI['factor'] = out
    return out


# =============================================================================
# 2. PREDICTION-POWERED INFERENCE ON TWITTER
# =============================================================================
def ppi_sim(ns=(100, 200, 400, 800), R=2000, seed=15):
    """PPI (Angelopoulos et al., 2023): labelled sample (n) and unlabelled sample (N - n) INDEPENDENT, predictor
    f fixed (trained on other data). The simulation treats the N validation headlines as the population: in each replication
    both samples are drawn independently, with replacement, so the variance Var(f)/(N - n) + Var(f - Y)/n is exact,
    and theta (the mean of the N labels) is the population mean."""
    tw = g.load_csv('ch15_twitter_scores.csv')
    y = tw['label'].map(SIGN).values.astype(float)
    theta = y.mean()
    F = {'finbert': net(tw, 'finbert'), 'qwen': net(tw, 'qwen7B')}
    N = len(y)
    rng = np.random.default_rng(seed)
    z = stats.norm.ppf(0.975)
    out = {'theta': float(theta), 'N': N, 'naive': {c: float(F[c].mean()) for c in F}, 'by_n': {}}
    for n in ns:
        res = {'classical': [], 'ppi_finbert': [], 'ppi_qwen': []}
        for _ in range(R):
            L, U = rng.integers(0, N, n), rng.integers(0, N, N - n)
            m, se = y[L].mean(), y[L].std(ddof=1) / np.sqrt(n)
            res['classical'].append((m, se))
            for c in F:
                f = F[c]
                rect = f[L] - y[L]
                est = f[U].mean() - rect.mean()
                se_p = np.sqrt(f[U].var(ddof=1) / len(U) + rect.var(ddof=1) / n)
                res[f'ppi_{c}'].append((est, se_p))
        r = {}
        for k, v in res.items():
            v = np.array(v)
            r[k] = {'cover': float(np.mean(np.abs(v[:, 0] - theta) <= z * v[:, 1])), 'width': float(np.mean(2 * z * v[:, 1])),
                    'bias': float(v[:, 0].mean() - theta)}
        out['by_n'][str(n)] = r
    # a concrete example with n = 200 (a random split of the headlines: n labelled, the rest unlabelled)
    idx = np.random.default_rng(1).permutation(N)
    L, U = idx[:200], idx[200:]
    ex = {'classical': (y[L].mean(), y[L].std(ddof=1) / np.sqrt(200))}
    for c in F:
        rect = F[c][L] - y[L]
        ex[c] = (F[c][U].mean() - rect.mean(), np.sqrt(F[c][U].var(ddof=1) / len(U) + rect.var(ddof=1) / 200),
                 rect.mean())
    out['example'] = {k: [float(x) for x in v] for k, v in ex.items()}
    # variance of the rectifier vs variance of the labels: the efficiency gain
    out['var_ratio'] = {c: float((F[c] - y).var() / y.var()) for c in F}
    VI['ppi'] = out
    return out


def fig_ppi():
    R = VI['ppi']
    ns = [int(n) for n in R['by_n']]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9))
    lab = {'classical': 'Human labels only', 'ppi_finbert': 'PPI with FinBERT scores',
           'ppi_qwen': 'PPI with Qwen2.5-7B scores'}
    col = {'classical': g.MainBlue, 'ppi_finbert': g.Forest, 'ppi_qwen': g.IDAred}
    for k in lab:
        axes[0].plot(ns, [R['by_n'][str(n)][k]['width'] for n in ns], 'o-', color=col[k], label=lab[k], ms=4)
        axes[1].plot(ns, [100 * R['by_n'][str(n)][k]['cover'] for n in ns], 'o-', color=col[k], ms=4)
    axes[1].axhline(95, color=g.Gray, ls='--', lw=0.8)
    axes[0].set_xscale('log')
    axes[1].set_xscale('log')
    from matplotlib.ticker import NullFormatter, NullLocator
    for ax in axes:
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel('Human-labelled headlines $n$')
    axes[0].set_ylabel('Mean width of the 95% CI')
    axes[1].set_ylabel('Coverage of the 95% CI (%)')
    axes[1].set_ylim(85, 100)
    h, l = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    g.fig_legend_bottom(fig, h, l, ncol=3, y=0.0)
    g.save_fig('ch15_ppi')


# =============================================================================
# 3. CALIBRATION OF THE PROBABILITIES
# =============================================================================
def calib_stats(P, y, bins=10):
    conf = P.max(1)
    pred = P.argmax(1)
    hit = (pred == y).astype(float)
    edges = np.linspace(1 / 3, 1, bins + 1)
    k = np.clip(np.digitize(conf, edges[1:-1]), 0, bins - 1)
    ece = sum(np.abs(hit[k == b].mean() - conf[k == b].mean()) * np.mean(k == b) for b in range(bins) if np.any(k == b))
    Y = np.eye(3)[y]
    brier = float(np.mean(np.sum((P - Y) ** 2, 1)))
    ll = float(-np.mean(np.log(np.clip(P[np.arange(len(y)), y], 1e-12, 1))))
    rel = [(float(conf[k == b].mean()), float(hit[k == b].mean()), int(np.sum(k == b))) for b in range(bins) if np.any(k == b)]
    return {'ece': float(ece), 'brier': brier, 'logloss': ll, 'acc': float(hit.mean()), 'rel': rel}


def temp_scale(P, T):
    L = np.log(np.clip(P, 1e-12, 1)) / T
    L -= L.max(1, keepdims=True)
    E = np.exp(L)
    return E / E.sum(1, keepdims=True)


def calibration(seed=15):
    tw = g.load_csv('ch15_twitter_scores.csv')
    y = tw['label'].map({'negative': 0, 'neutral': 1, 'positive': 2}).values
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    A, B = idx[:len(y) // 2], idx[len(y) // 2:]
    out = {}
    for name, tag in (('finbert', 'finbert'), ('qwen7', 'qwen7B'), ('qwen14', 'qwen14B'),
                      ('qwen7_P2', 'qwen7B_P2'), ('qwen7_P3', 'qwen7B_P3')):
        P = tw[[f'{tag}_{l}' for l in M.LABELS]].values.astype(float)
        P = P / P.sum(1, keepdims=True)
        nll = lambda T: -np.mean(np.log(np.clip(temp_scale(P[A], T)[np.arange(len(A)), y[A]], 1e-12, 1)))  # noqa: E731
        T = float(minimize_scalar(nll, bounds=(0.05, 50), method='bounded').x)
        out[name] = {'raw': calib_stats(P[B], y[B]), 'T': T, 'scaled': calib_stats(temp_scale(P[B], T), y[B]),
                     'all': calib_stats(P, y)}
    VI['calib'] = out
    return out


def fig_calibration():
    R = VI['calib']
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
    for ax, key, title in ((axes[0], 'raw', 'Raw probabilities'), (axes[1], 'scaled', 'After temperature scaling')):
        ax.plot([1 / 3, 1], [1 / 3, 1], color=g.Gray, ls='--', lw=0.8)
        for m, c, lab in (('finbert', g.MainBlue, 'FinBERT'), ('qwen7', g.IDAred, 'Qwen2.5-7B'),
                          ('qwen14', g.Orange, 'Qwen2.5-14B')):
            rel = np.array(R[m][key]['rel'])
            ax.scatter(rel[:, 0], rel[:, 1], s=8 + 60 * rel[:, 2] / rel[:, 2].max(), color=c, alpha=0.85,
                       label=f"{lab}, ECE {100 * R[m][key]['ece']:.1f}%" if key == 'raw' else lab, lw=0)
            ax.plot(rel[:, 0], rel[:, 1], color=c, lw=0.8)
        ax.set_title(title, fontsize=8.5, loc='left')
        ax.set_xlabel('Predicted probability of the chosen label')
        ax.set_xlim(0.3, 1.02)
    axes[0].set_ylabel('Share correct')
    h, l = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    g.fig_legend_bottom(fig, h, l, ncol=3, y=0.0)
    g.save_fig('ch15_calibration')


# =============================================================================
# 4. THE 16-STOCK PANEL: CLUSTERING, WILD CLUSTER BOOTSTRAP, HOLM
# =============================================================================
def wcr_boot(y, x, cl, B=9999, seed=15):
    """Restricted wild cluster bootstrap (b = 0), Rademacher weights, t with CR1 clustered SE."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    codes, uniq = pd.factorize(np.asarray(cl))
    G, n = len(uniq), len(y)
    xd = x - x.mean()
    Sxx = xd @ xd
    cr1 = G / (G - 1) * (n - 1) / (n - 2)

    def tstat(yy):
        b = xd @ yy / Sxx
        e = yy - yy.mean() - b * xd
        s = np.bincount(codes, weights=xd * e, minlength=G)
        return b / np.sqrt(cr1 * (s @ s) / Sxx ** 2)
    t0 = tstat(y)
    et = y - y.mean()                      # residuals of the restricted model
    Ag = np.bincount(codes, weights=xd * et, minlength=G)
    Bg = np.bincount(codes, weights=xd * xd, minlength=G)
    Cg = np.bincount(codes, weights=et, minlength=G)
    Dg = np.bincount(codes, weights=xd, minlength=G)
    rng = np.random.default_rng(seed)
    W = rng.choice([-1.0, 1.0], size=(B, G))
    b = W @ Ag / Sxx
    dm = W @ Cg / n                        # deviation of the mean of y*
    S = W * Ag[None, :] - dm[:, None] * Dg[None, :] - b[:, None] * Bg[None, :]
    t = b / np.sqrt(cr1 * np.sum(S ** 2, 1) / Sxx ** 2)
    return float(t0), float(np.mean(np.abs(t) >= abs(t0)))


def twoway_se(y, x, c1, c2):
    """Two-way clustered SE (Cameron, Gelbach & Miller, 2011): V1 + V2 - V12."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    xd = x - x.mean()
    Sxx = xd @ xd
    b = xd @ y / Sxx
    e = y - y.mean() - b * xd
    u = xd * e

    def V(cl):
        codes = pd.factorize(np.asarray(cl))[0]
        s = np.bincount(codes, weights=u)
        G = len(s)
        return G / (G - 1) * (s @ s) / Sxx ** 2
    inter = pd.Series(list(zip(c1, c2))).astype(str).values
    v = V(c1) + V(c2) - V(inter)
    return float(b), float(np.sqrt(max(v, 0)))


def holm(p):
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    adj = np.empty(m)
    run = 0
    for k, i in enumerate(o):
        run = max(run, (m - k) * p[i])
        adj[i] = min(1.0, run)
    return adj


def panel_inference(P, strat=None):
    days = P.index.get_level_values('day')
    tic = P.index.get_level_values('ticker')
    rows = {}
    for c in ('lm', 'finbert', 'qwen'):
        for h in ('r0', 'r1', 'r2'):
            y, x = P[h].values, P[f'z_{c}'].values
            t_tic, p_wcr = wcr_boot(y, x, tic)
            b, se2 = twoway_se(y, x, days, tic)
            rows[f'{c}|{h}'] = {'b_bp': 100 * b, 't_tic': t_tic, 'p_t15': float(2 * stats.t.sf(abs(t_tic), 15)),
                                'p_wcr': p_wcr, 't_2way': b / se2, 'p_2way': float(2 * stats.t.sf(abs(b / se2), 15))}
    keys = list(rows)
    adj = holm([rows[k]['p_wcr'] for k in keys])
    for k, a in zip(keys, adj):
        rows[k]['p_wcr_holm'] = float(a)
    # the d+2 strategies: Newey-West t, Normal p-value, Holm over 3 scores
    if strat is None:
        with open(os.path.join(HERE, 'ch15_results.json')) as f:
            strat = json.load(f)['news']['strat']
    st = strat
    ps = {c: float(2 * stats.norm.sf(abs(st[c]['t']))) for c in ('lm', 'finbert', 'qwen')}
    ha = holm(list(ps.values()))
    VI['panel'] = {'reg': rows, 'strat_p': ps, 'strat_holm': dict(zip(ps, map(float, ha)))}
    return VI['panel']


# =============================================================================
# 5. EVENT STUDY: POSITIVE - NEGATIVE DIFFERENCE AND THE BMP TEST
# =============================================================================
def event_inference(P, rets, col='finbert'):
    neg, pos = g.event_groups(P[col])
    sub = P[neg | pos].copy()
    sub['pos'] = pos[neg | pos].astype(float)
    sub['post'] = sub[['r2', 'rp3', 'rp4', 'rp5']].sum(1, min_count=4)
    sub['pre'] = sub[['rm5', 'rm4', 'rm3', 'rm2', 'rm1']].sum(1, min_count=5)
    out = {}
    for w in ('pre', 'r0', 'r1', 'post'):
        s = sub.dropna(subset=[w])
        r = M.cluster_ols(s[w].values, s['pos'].values, s.index.get_level_values('day'))
        out[w] = {'d': float(r['b']), 'lo': float(r['b'] - 1.96 * r['se_cl']), 'hi': float(r['b'] + 1.96 * r['se_cl']),
                  't': float(r['t_cl'])}
    # BMP: CAR standardised by the standard deviation of the excess return over the 250 days ending at -6
    ex = rets.drop(columns='SPY').sub(rets['SPY'], axis=0)
    sd = ex.rolling(250, min_periods=120).std().shift(6)
    sds = sd.stack()
    sds.index.names = ['day', 'ticker']
    sub = sub.join(sds.rename('sig'), how='left').dropna(subset=['sig', 'post'])
    sub['scar'] = sub['post'] / (sub['sig'] * np.sqrt(4))
    for grp, sel in (('pos', sub['pos'] == 1), ('neg', sub['pos'] == 0)):
        v = sub.loc[sel, 'scar'].values
        out[f'bmp_{grp}'] = {'mean_scar': float(v.mean()), 'z': float(v.mean() * np.sqrt(len(v)) / v.std(ddof=1)),
                             'n': int(len(v))}
    VI['event'] = out
    return out


# =============================================================================
# 6. SPECIFICATION CURVE WITH A SIGN-FLIP NULL BY DAYS
# =============================================================================
def nw_t_mat(X, L):
    n = X.shape[1]
    mu = X.mean(1)
    U = X - mu[:, None]
    v = np.sum(U * U, 1) / n
    for l in range(1, L + 1):
        v += 2 * (1 - l / (L + 1)) * np.sum(U[:, l:] * U[:, :-l], 1) / n
    return mu / np.sqrt(v / n)


def spec_curve(P, rets, B=2000, seed=15, block=10):
    """Joint null: Rademacher weights constant over blocks of `block` consecutive signal days (dependent wild
    bootstrap, Shao, 2010), the same for all specifications. Assumptions: under the null, the signed returns of each
    block are symmetric around 0 and the blocks are roughly independent; the dependence between
    specifications and the serial dependence within a block are preserved."""
    days = rets.index[rets.index >= P.index.get_level_values('day').min()]
    series = []
    meta = []
    for c in A.SCORES:
        for b in A.BANDS:
            for ret, lag in A.HOLD.items():
                x = A.portfolio(P.dropna(subset=[ret]), c, days, b, ret, lag)
                # indexed by the signal day (return day minus lag): the same sign flip for all
                s = pd.Series(x.values, index=pd.DatetimeIndex(days)).shift(-lag).reindex(days).fillna(0.0)
                series.append(s.values)
                meta.append({'score': c, 'band': b, 'day': lag})
    X = np.vstack(series)
    n = X.shape[1]
    L = int(np.floor(4 * (n / 100) ** (2 / 9)))
    t_obs = nw_t_mat(X, L)
    rng = np.random.default_rng(seed)
    cnt, med = [], []
    for _ in range(B):
        w = np.repeat(rng.choice([-1.0, 1.0], size=int(np.ceil(n / block))), block)[:n]
        tb = nw_t_mat(X * w[None, :], L)
        cnt.append(np.sum(tb > 1.96))
        med.append(np.median(tb))
    cnt, med = np.array(cnt), np.array(med)
    k_obs = int(np.sum(t_obs > 1.96))
    out = {'t': t_obs.tolist(), 'meta': meta, 'n_pos_sig': k_obs, 'median_t': float(np.median(t_obs)),
           'p_count': float(np.mean(cnt >= k_obs)), 'p_median': float(np.mean(med >= np.median(t_obs))),
           'null_q95_count': float(np.quantile(cnt, 0.95)), 'n_neg_sig': int(np.sum(t_obs < -1.96)), 'B': B,
           'block': block}
    VI['spec'] = out
    return out


def fig_spec_curve():
    R = VI['spec']
    t = np.array(R['t'])
    meta = R['meta']
    o = np.argsort(t)
    col = {'lm': g.Orange, 'finbert': g.MainBlue, 'qwen': g.IDAred}
    lab = {'lm': 'Loughran-McDonald', 'finbert': 'FinBERT', 'qwen': 'Qwen2.5-7B'}
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    for c in col:
        k = [j for j, i in enumerate(o) if meta[i]['score'] == c]
        ax.scatter(k, t[o][k], color=col[c], s=16, label=lab[c], zorder=3)
    ax.axhline(1.96, color=g.Gray, ls='--', lw=0.8)
    ax.axhline(-1.96, color=g.Gray, ls='--', lw=0.8)
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_xlabel('36 specifications, sorted by t (score x threshold x holding day)')
    ax.set_ylabel('Newey-West t, mean daily return')
    g.legend_outside_bottom(ax, ncol=3, y=-0.2)
    g.save_fig('ch15_spec_curve')


# =============================================================================
# 7. AUC BEFORE vs AFTER RELEASE: DELONG TEST AND POWER
# =============================================================================
def delong_var(p, up):
    p, up = np.asarray(p, float), np.asarray(up, bool)
    X, Y = p[up], p[~up]
    psi = (X[:, None] > Y[None, :]).astype(float) + 0.5 * (X[:, None] == Y[None, :])
    V10, V01 = psi.mean(1), psi.mean(0)
    a = psi.mean()
    return float(a), float(V10.var(ddof=1) / len(X) + V01.var(ddof=1) / len(Y))


def auc_test():
    mm = g.load_csv('ch15_memory_monthly.csv', index_col=0, parse_dates=True)
    out = {}
    z80 = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)
    for s in ('7B', '14B'):
        pre = mm.loc[:'2024-08-31']
        post = mm.loc['2024-10-01':]
        a1, v1 = delong_var(pre[f'qwen{s}'], pre['ret'] > 0)
        a2, v2 = delong_var(post[f'qwen{s}'], post['ret'] > 0)
        m, n = int((post['ret'] > 0).sum()), int((post['ret'] <= 0).sum())
        v0 = (m + n + 1) / (12 * m * n)       # variance of the AUC when AUC = 0.5 (Hanley & McNeil)
        z = (a1 - a2) / np.sqrt(v1 + v2)
        out[s] = {'auc_pre': a1, 'auc_post': a2, 'se_pre': np.sqrt(v1), 'se_post': np.sqrt(v2), 'z': float(z),
                  'p': float(2 * stats.norm.sf(abs(z))), 'mde': float(z80 * np.sqrt(v1 + v0)),
                  'se0_post': float(np.sqrt(v0)), 'n_up': m, 'n_down': n}
        # months needed after release to detect the fall to 0.5 with 80% power (same share of up months)
        share = m / (m + n)
        need = None
        for T in range(20, 2000):
            mu, nd = max(1, round(share * T)), max(1, T - round(share * T))
            if z80 * np.sqrt(v1 + (mu + nd + 1) / (12 * mu * nd)) <= a1 - 0.5:
                need = T
                break
        out[s]['months_needed'] = need
    VI['auc'] = out
    return out


# =============================================================================
# 8. TRAINING-DATA LEAKAGE: DIFFERENCE IN DIFFERENCES WITH CI
# =============================================================================
def leakage_did(B=2000, seed=15):
    pb = g.load_csv('ch15_phrasebank_scores.csv')
    tw = g.load_csv('ch15_twitter_scores.csv')
    hit = {}
    for name, d in (('pb', pb), ('tw', tw)):
        pr = g.predictions(d)
        hit[name] = {m: (pr[m] == d['label'].values).astype(float) for m in ('FinBERT', 'Qwen 7B')}
    did = lambda a, b: (a['FinBERT'].mean() - b['FinBERT'].mean()) - (a['Qwen 7B'].mean() - b['Qwen 7B'].mean())  # noqa
    est = did(hit['pb'], hit['tw'])
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(B):
        i = rng.integers(0, len(pb), len(pb))
        j = rng.integers(0, len(tw), len(tw))
        v.append(did({k: x[i] for k, x in hit['pb'].items()}, {k: x[j] for k, x in hit['tw'].items()}))
    VI['did'] = {'did': float(est), 'lo': float(np.quantile(v, 0.025)), 'hi': float(np.quantile(v, 0.975)),
                 'drop_fb': float(hit['pb']['FinBERT'].mean() - hit['tw']['FinBERT'].mean()),
                 'drop_q7': float(hit['pb']['Qwen 7B'].mean() - hit['tw']['Qwen 7B'].mean())}
    return VI['did']


def timing():
    """Time per headline: one pass for each prompt; median of the three prompts."""
    t = g.load_csv('ch15_llm_time.csv', index_col=0)['sec_per_text']
    out = {}
    for s in ('0.5B', '1.5B', '3B', '7B', '14B'):
        v = t[[k for k in t.index if k.startswith(f'time_qwen{s}')]].values
        out[s] = {'median': float(np.median(v)), 'min': float(v.min()), 'max': float(v.max()), 'k': int(len(v))}
    VI['time'] = out
    return out


if __name__ == '__main__':
    attenuation()
    ppi_sim()
    fig_ppi()
    calibration()
    fig_calibration()
    leakage_did()
    auc_test()
    timing()
    P, rets = news_setup()
    factor_iv(P)
    panel_inference(P)
    event_inference(P, rets)
    spec_curve(P, rets)
    fig_spec_curve()
    with open(os.path.join(HERE, 'ch15_inference.json'), 'w') as f:
        json.dump(g.jsonable(VI), f, indent=1, default=float)
    print(json.dumps({k: v for k, v in g.jsonable(VI).items() if k not in ('spec',)}, indent=1, default=float)[:12000])
    print({k: v for k, v in VI['spec'].items() if k not in ('t', 'meta')})

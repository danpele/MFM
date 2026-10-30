"""
colour_words.py -- Capitolul 15, al doilea studiu de caz: Garcia, Hu & Rohrer (2023), The colour of finance words
================================================================================================================
Garcia, D., Hu, X., Rohrer, M. (2023). Journal of Financial Economics 147(3), 525-549,
https://doi.org/10.1016/j.jfineco.2022.11.006

Dictionare pozitive / negative invatate din reactia preturilor (robust MNIR, sectiunea 2.2 din lucrare), aplicate
titlurilor FNSPID din acest capitol (ch15_c3_headlines.csv.gz, aceleasi 106 820 de titluri ca ch15_news_daily.csv):
  * document = toate titlurile unei actiuni intr-o zi de tranzactionare (ca la articolele WSJ din lucrare);
  * randamentul = buy-and-hold al actiunii minus buy-and-hold SPY, de la inchiderea din d-1 la inchiderea din d+2
    (fereastra de 4 zile din lucrare), in procente, winsorizat la 1/99%;
  * curatarea textului din anexa lucrarii: litere mici, fara cifre si punctuatie, contractii desfacute, lista de
    cuvinte de legatura Snowball cu exceptiile lucrarii, fara termeni de 1-2 litere (cu exceptia no, up, go);
    in locul etichetarii POS a numelor proprii (titlurile sint scrise cu majuscule la fiecare cuvant) se elimina
    numele si simbolurile celor 16 firme;
  * vocabularul: cele mai frecvente p = 2^14 = 16 384 de cuvinte din textele de antrenare (doar ele; daca sint mai
    putine tipuri de cuvinte, toate); pragurile de winsorizare ale randamentului de antrenare: cuantilele 1/99% ale
    esantionului de antrenare; textele de antrenare a caror fereastra de randament (pina la d+2) trece de 31 dec. 2019
    sint eliminate;
  * robust MNIR: k = 500 de subesantioane de q = 5 000 de documente, extrase fara intoarcere din esantionul de
    antrenare; in fiecare, regresia Poisson inversa a fiecarui cuvant pe randamentul standardizat (offset: lungimea
    documentului); semnul cuvantului = semnul statisticii score daca z^2 > 2, altfel 0: o aproximare prin testul score
    a selectiei AIC, nu penalizarea gamma-lasso cu AICc din textir; D+ = % pozitiv - % negativ; pragul 80% (unigrame,
    ca in lucrare);
  * antrenare: zilele pina la 31 dec. 2019; testare in afara esantionului: 2020-2023;
  * regresiile din tabelul 2, pe perioada de test: R = a + b'S + e, S = frecventa cuvintelor din lista / numarul de
    cuvinte, scalat la varianta 1 (nu winsorizat: vezi zscore); coeficientii sint estimati pe perioada de test, deci
    R^2 este o asociere pe texte rezervate evaluarii dictionarului, nu R^2 al unor prognoze cu coeficienti fixati;
    fara variabilele de control ale lucrarii;
  * inferenta, conditionata de dictionarul invatat: erori standard Driscoll-Kraay (HAC Newey-West, nucleu Bartlett,
    pe contributiile la ecuatiile de estimare agregate pe fiecare zi a calendarului de tranzactionare, zilele fara
    texte cu contributie 0), pentru ca randamentele pe 4 zile ale textelor din zile apropiate se suprapun;
    intervalele diferentelor de R^2: bootstrap pe blocuri de 10 zile consecutive (toate firmele unei zile si toate
    specificatiile raman impreuna), 1 999 de extrageri.
Iesire: ch15_colour_results.json, charts/ch15_colour_words.pdf/.png
Rulare:  python3 colour_words.py
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import re
import sys

import numpy as np
import pandas as pd
import scipy.sparse as sp
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_all_charts as G  # noqa: E402  chapter style, colours and save_fig
import mfm_text as M  # noqa: E402

PAPER = {'doi': '10.1016/j.jfineco.2022.11.006',
         # Table 2 (earnings calls, out of sample 2016-2020; controls and fixed effects), Section 3.1
         # adjusted R^2; 'r2_lm' uses the LM words not in the ML lists, 'r2_ml' the ML words not in LM; corpus 13.10.2005-
    # 07.10.2020 (Table 1), dictionaries for Table 2 trained on the calls before 2016
    'r2_controls': 1.7, 'r2_lm': 2.1, 'r2_ml': 4.6, 'r2_overlap': 5.4, 'r2_bigrams': 4.5, 'r2_joint': 6.5,
         'b_lm': (0.41, -0.50), 'b_ml': (0.98, -1.37), 'b_overlap': (1.25, -1.56),
         # Section 3.2, dictionaries learned on the full sample (2006-2020), not the pre-2016 lists of Table 2
         'n_overlap': (18, 30), 'n_ml_only': (57, 64), 'n_lm_only': (329, 2315)}

K, Q, P_VOCAB, CUT, SEED = 500, 5000, 2 ** 14, 80.0, 0
BLOCK, B_BOOT = 10, 1999          # moving-block bootstrap of the R^2 differences: block length (trading days), draws
TRAIN_END = '2019-12-31'
CUTS = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

# Snowball English stop-word list (snowballstem.org/algorithms/english/stop.txt)
SNOWBALL = """i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers
herself it its itself they them their theirs themselves what which who whom this that these those am is are was were
be been being have has had having do does did doing would should could ought i'm you're he's she's it's we're they're
i've you've we've they've i'd you'd he'd she'd we'd they'd i'll you'll he'll she'll we'll they'll isn't aren't wasn't
weren't hasn't haven't hadn't doesn't don't didn't won't wouldn't shan't shouldn't can't cannot couldn't mustn't let's
that's who's what's here's there's when's where's why's how's a an the and but if or because as until while of at by
for with about against between into through during before after above below to from up down in out on off over under
again further then once here there when where why how all any both each few more most other some such no nor not only
own same so than too very""".split()
# the paper (Appendix, note 47) keeps these stop words (and adds can, will, must, let; not added here)
KEEP = {'against', 'above', 'below', 'up', 'down', 'over', 'under', 'again', 'further', 'few', 'more', 'most',
        'no', 'not'}
STOP = set(SNOWBALL) - KEEP
# proxy for the proper-noun filter: names and symbols of the 16 firms of the panel
FIRMS = set("""apple aapl microsoft msft amazon amzn nvidia nvda tesla tsla alphabet google googl goog meta facebook fb
jpmorgan jpm chase bac citigroup citi goldman sachs morgan stanley wells fargo wfc cisco csco gamestop gme
microstrategy mstr coinbase coin""".split())
CONTR = [(r"n't\b", ' not'), (r"'ll\b", ' will'), (r"'re\b", ' are'), (r"'d\b", ' would'), (r"'m\b", ' am'),
         (r"'ve\b", ' have'), (r"\bcannot\b", 'can not'), (r"'s\b", '')]
WORD = re.compile(r"[a-z]+")


def clean(text):
    t = str(text).lower().replace('’', "'")
    t = re.sub(r"[^\x00-\x7f]", ' ', t)
    for a, b in CONTR:
        t = re.sub(a, b, t)
    return [w for w in WORD.findall(t)
            if w not in STOP and w not in FIRMS and (len(w) > 2 or w in ('no', 'up', 'go'))]


def winsor(x, lo=0.01, hi=0.99, ref=None):
    """Clip at the lo/hi quantiles of `ref` (default: of x itself)."""
    a, b = np.nanquantile(x if ref is None else ref, [lo, hi])
    return np.clip(x, a, b)


def nw_lags(T):
    return int(np.floor(4 * (T / 100) ** (2 / 9)))


def cluster_ols_multi(y, X, groups, calendar):
    """OLS y = a + X b with Driscoll-Kraay standard errors: the score contributions x_i e_i are summed by day over
    the full trading calendar (days without texts contribute 0) and the Newey-West (Bartlett) long-run variance of
    that daily series is used, so that both the cross-firm dependence within a day and the serial dependence created
    by the overlapping 4-day returns are allowed for."""
    ok = X.std(0) > 0                      # a list without any word in the test texts has no coefficient
    if not ok.all():
        r = cluster_ols_multi(y, X[:, ok], groups, calendar) if ok.any() else {'b': [], 'se': [], 't': [], 'r2': 0.0,
                                                                      'r2_adj': 0.0, 'n': len(y), 'G': 0}
        full = {k: [float('nan')] * len(ok) for k in ('b', 'se', 't')}
        for k in full:
            vals = iter(r[k])
            full[k] = [next(vals) if o else None for o in ok]
        return {**r, **full}
    X = np.column_stack([np.ones(len(y)), X])
    XtX = np.linalg.inv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    n, k = X.shape
    pos = pd.Index(calendar).get_indexer(pd.DatetimeIndex(groups))
    if (pos < 0).any():
        raise ValueError('a text day is not in the trading calendar')
    T = len(calendar)
    S = np.zeros((T, k))
    np.add.at(S, pos, X * e[:, None])
    L = nw_lags(T)
    meat = S.T @ S
    for l in range(1, L + 1):
        G_l = S[l:].T @ S[:-l]
        meat += (1 - l / (L + 1)) * (G_l + G_l.T)
    G_ = int(len(np.unique(pos)))
    V = XtX @ meat @ XtX * (n - 1) / (n - k)
    se = np.sqrt(np.diag(V))
    r2 = 1 - (e @ e) / np.sum((y - y.mean()) ** 2)
    r2a = 1 - (1 - r2) * (n - 1) / (n - k)
    return {'b': b[1:].tolist(), 'se': se[1:].tolist(), 't': (b[1:] / se[1:]).tolist(), 'r2': float(r2),
            'r2_adj': float(r2a), 'n': int(n), 'G': int(G_), 'T': int(T), 'L': int(L)}


def build_docs():
    h = pd.read_csv(os.path.join(HERE, 'ch15_c3_headlines.csv.gz'), dtype=str, keep_default_na=False)
    rets = M.stock_returns(sorted(set(M.TICKERS.values())) + ['SPY.US'], start='2009-01-01')
    rets.columns = [c.replace('.US', '') for c in rets.columns]
    h['day'] = M.assign_trading_day(pd.to_datetime(h['date'], utc=True), rets.index)
    h = h.dropna(subset=['day'])
    h = h[h['day'] >= '2009-06-01']
    docs = h.groupby(['day', 'ticker'])['headline'].apply(lambda s: ' '.join(s))
    n_hl = h.groupby(['day', 'ticker']).size()
    # 4-day buy-and-hold excess return: close d-1 to close d+2
    g = np.log1p(rets.loc[:'2023-12-31'] / 100)
    w = sum(g.shift(-k) for k in range(3))
    bh = np.expm1(w)
    ex = 100 * bh.drop(columns='SPY').sub(bh['SPY'], axis=0)
    R = ex.stack()
    R.index.names = ['day', 'ticker']
    D = pd.DataFrame({'text': docs, 'n': n_hl}).join(R.rename('R'), how='inner').dropna(subset=['R'])
    daily = pd.read_csv(os.path.join(HERE, 'ch15_news_daily.csv'), parse_dates=['day']).set_index(['day', 'ticker'])
    D = D.join(daily[['finbert', 'qwen', 'lm']], how='left')
    cal = rets.loc[:'2023-12-31'].index
    # last return day of each text's window (close of d+2)
    i = cal.get_indexer(D.index.get_level_values('day'))
    D['end'] = cal[np.minimum(i + 2, len(cal) - 1)]
    return D, cal


def dtm(tok_lists, vocab):
    ix = {w: i for i, w in enumerate(vocab)}
    rows, cols = [], []
    for r, ws in enumerate(tok_lists):
        for w in ws:
            j = ix.get(w)
            if j is not None:
                rows.append(r)
                cols.append(j)
    C = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(tok_lists), len(vocab)))
    C.sum_duplicates()
    return C


def mnir_signs(C, v):
    """Sign of each word's loading in the Poisson inverse regression c_ij ~ Poisson(m_i exp(a_j + phi_j v_i)):
    score statistic at phi_j = 0 (a_j at its MLE), sign kept when z^2 > 2 (AIC), else 0."""
    m = np.asarray(C.sum(1)).ravel()
    keep = m > 0
    C, v, m = C[keep], v[keep], m[keep]
    v = (v - v.mean()) / v.std()
    Mtot = m.sum()
    p = np.asarray(C.sum(0)).ravel() / Mtot
    vbar = (m * v).sum() / Mtot
    score = C.T @ v - p * (m * v).sum()
    info = p * (m * (v - vbar) ** 2).sum()
    z = np.where(info > 0, score / np.sqrt(np.where(info > 0, info, 1)), 0.0)
    return np.where(z ** 2 > 2, np.sign(z), 0.0)


def robust_mnir(C, v, k=K, q=Q, seed=SEED):
    rng = np.random.default_rng(seed)
    n = C.shape[0]
    pos = np.zeros(C.shape[1])
    neg = np.zeros(C.shape[1])
    for _ in range(k):
        idx = rng.choice(n, size=q, replace=False)
        s = mnir_signs(C[idx], v[idx])
        pos += s > 0
        neg += s < 0
    return 100 * (pos - neg) / k


def scores(tok_lists, words):
    words = set(words)
    return np.array([sum(w in words for w in ws) / max(len(ws), 1) for ws in tok_lists])


def zscore(x):
    """Unit variance. Word shares are not winsorized: they lie in [0, 1] and are 0 for most firm-days, so the 1/99%
    winsorization of the paper would set the sparse lists to a constant."""
    s = x.std()
    return (x - x.mean()) / s if s > 0 else x * 0


def _r2(y, X):
    X = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    return 1 - (e @ e) / np.sum((y - y.mean()) ** 2)


def boot_r2(y, groups, Xs, calendar, B=B_BOOT, block=BLOCK, seed=SEED):
    """Moving-block bootstrap of the R^2 differences between specifications: blocks of `block` consecutive trading
    days of the test calendar (days without texts included), drawn with replacement; all firms of a day and all
    specifications stay together. Conditional on the learned dictionaries."""
    rng = np.random.default_rng(seed)
    pos = pd.Index(calendar).get_indexer(pd.DatetimeIndex(groups))
    T = len(calendar)
    order = np.argsort(pos, kind='stable')
    bounds = np.searchsorted(pos[order], np.arange(T + 1))
    rows = [order[bounds[t]:bounds[t + 1]] for t in range(T)]
    nb = int(np.ceil(T / block))
    pairs = [('ml_only', 'lm_all'), ('qwen', 'ml_only'), ('finbert', 'ml_only')]
    D = {f'{a}-{b}': [] for a, b in pairs}
    for _ in range(B):
        starts = rng.integers(0, T - block + 1, nb)
        days = (starts[:, None] + np.arange(block)[None, :]).ravel()[:T]
        idx = np.concatenate([rows[t] for t in days])
        r = {k: _r2(y[idx], X[idx]) for k, X in Xs.items() if X[idx].std(0).min() > 0}
        for a, b in pairs:
            if a in r and b in r:
                D[f'{a}-{b}'].append(r[a] - r[b])
    out = {}
    for k, v in D.items():
        v = 100 * np.array(v)
        a, b = k.split('-')
        out[k] = {'diff': 100 * float(_r2(y, Xs[a]) - _r2(y, Xs[b])), 'lo': float(np.quantile(v, 0.025)),
                  'hi': float(np.quantile(v, 0.975)), 'p_le0': float((v <= 0).mean()), 'B': len(v),
                  'block': block}
    return out


def horse_race(Dt, toks, lists, cal, boot=True):
    """Regressions on the test period (Table 2 of the paper, without controls); coefficients estimated on the test
    texts."""
    y = winsor(Dt['R'].values)
    grp = Dt.index.get_level_values('day')
    S = {k: zscore(scores(toks, w)) for k, w in lists.items()}
    out = {}
    specs = {'lm_all': ['lm_all_pos', 'lm_all_neg'], 'lm_only': ['lm_only_pos', 'lm_only_neg'],
             'ml_only': ['ml_only_pos', 'ml_only_neg'], 'overlap': ['ov_pos', 'ov_neg'],
             'joint': ['lm_only_pos', 'lm_only_neg', 'ml_only_pos', 'ml_only_neg', 'ov_pos', 'ov_neg']}
    for name, cols in specs.items():
        out[name] = cluster_ols_multi(y, np.column_stack([S[c] for c in cols]), grp, cal)
        out[name]['vars'] = cols
    for c in ('finbert', 'qwen'):
        out[c] = cluster_ols_multi(y, zscore(winsor(Dt[c].values))[:, None], grp, cal)
        out[c]['vars'] = [c]
    if not boot:
        out['share_hit'] = {k: float((scores(toks, w) > 0).mean()) for k, w in lists.items()}
        return out
    out['boot'] = boot_r2(y, grp, {'lm_all': np.column_stack([S['lm_all_pos'], S['lm_all_neg']]),
                                   'ml_only': np.column_stack([S['ml_only_pos'], S['ml_only_neg']]),
                                   'qwen': zscore(winsor(Dt['qwen'].values))[:, None],
                                   'finbert': zscore(winsor(Dt['finbert'].values))[:, None]}, cal)
    out['share_hit'] = {k: float((scores(toks, w) > 0).mean()) for k, w in lists.items()}
    return out


def run():
    D, cal = build_docs()
    toks = [clean(t) for t in D['text']]
    day = D.index.get_level_values('day')
    te = np.asarray(day > TRAIN_END)
    # training texts: return window (to the close of d+2) ends by the last training day
    tr = np.asarray((day <= TRAIN_END) & (D['end'] <= TRAIN_END))
    n_dropped = int(((day <= TRAIN_END) & ~tr).sum())
    toks_tr = [t for t, b in zip(toks, tr) if b]
    freq = pd.Series([w for ws in toks_tr for w in ws]).value_counts()     # training texts only
    vocab = freq.index[:P_VOCAB].tolist()
    C = dtm(toks_tr, vocab)
    R_tr = D['R'].values[tr]
    v = winsor(R_tr)                                                      # training quantiles
    Dplus = robust_mnir(C, v)
    lm = M.load_dictionaries()
    LMp = {w.lower() for w in lm['LM_pos']}
    LMn = {w.lower() for w in lm['LM_neg']}
    toks_te = [t for t, b in zip(toks, te) if b]
    Dt = D[te]
    cal_te = cal[(cal > TRAIN_END) & (cal <= day[te].max())]
    res = {'n_docs': int(len(D)), 'n_train': int(tr.sum()), 'n_test': int(te.sum()), 'n_dropped': n_dropped,
           'winsor_train': [float(x) for x in np.nanquantile(R_tr, [0.01, 0.99])],
           'n_cal_test': int(len(cal_te)), 'block': BLOCK,
           'n_headlines': int(D['n'].sum()), 'n_vocab': len(vocab), 'n_types': int(len(freq)),
           'train': [str(day[tr].min().date()), str(day[tr].max().date())],
           'test': [str(day[te].min().date()), str(day[te].max().date())],
           'k': K, 'q': Q, 'cut': CUT, 'paper': PAPER, 'by_cut': {}}

    def lists_at(cut):
        MLp = {w for w, d in zip(vocab, Dplus) if d >= cut}
        MLn = {w for w, d in zip(vocab, Dplus) if d <= -cut}
        return MLp, MLn, {'lm_all_pos': LMp, 'lm_all_neg': LMn, 'lm_only_pos': LMp - MLp, 'lm_only_neg': LMn - MLn,
                          'ml_only_pos': MLp - LMp, 'ml_only_neg': MLn - LMn, 'ov_pos': LMp & MLp,
                          'ov_neg': LMn & MLn}

    for cut in CUTS:
        MLp, MLn, L = lists_at(cut)
        hr = horse_race(Dt, toks_te, L, cal_te)
        res['by_cut'][str(cut)] = {'n_ml_pos': len(MLp), 'n_ml_neg': len(MLn),
                                   'n_ov_pos': len(L['ov_pos']), 'n_ov_neg': len(L['ov_neg']),
                                   'n_ml_only_pos': len(L['ml_only_pos']), 'n_ml_only_neg': len(L['ml_only_neg']),
                                   'reg': hr}
    MLp, MLn, L = lists_at(CUT)
    vs = pd.Series(Dplus, index=vocab)
    fr = freq.reindex(vocab)
    res['top_pos'] = [[w, float(vs[w]), int(fr[w])] for w in vs[vs >= CUT].sort_values(ascending=False).index[:40]]
    res['top_neg'] = [[w, float(vs[w]), int(fr[w])] for w in vs[vs <= -CUT].sort_values().index[:40]]
    res['dplus50'] = [[w, float(vs[w]), int(fr[w])] for w in vs[vs.abs() >= 50].sort_values(ascending=False).index]
    res['ml_pos'] = sorted(MLp)
    res['ml_neg'] = sorted(MLn)
    res['ov_pos'] = sorted(L['ov_pos'])
    res['ov_neg'] = sorted(L['ov_neg'])
    # LM words in the vocabulary that the algorithm colours the other way, and LM words it leaves neutral
    lm_in = [w for w in vocab if w in LMp | LMn]
    res['lm_in_vocab'] = len(lm_in)
    res['lm_flip'] = sorted([w for w in lm_in if (w in LMp and vs[w] <= -CUT) or (w in LMn and vs[w] >= CUT)])
    with open(os.path.join(HERE, 'ch15_colour_results.json'), 'w') as f:
        json.dump(res, f, indent=1)
    return res


def fig_colour_words(res):
    """Left: out-of-sample R^2 of each specification (2020-2023). Right: return per 1 s.d. of each word list."""
    from matplotlib.patches import Patch
    R = res['by_cut'][str(int(CUT))]['reg']
    names = [('lm_all', 'LM, all words'), ('lm_only', 'LM words not in ML'), ('ml_only', 'ML words not in LM'),
             ('overlap', 'Words in LM and ML'), ('joint', 'All three lists'), ('finbert', 'FinBERT'),
             ('qwen', 'Qwen2.5-7B')]
    col = {'lm_all': G.Orange, 'lm_only': G.Orange, 'ml_only': G.Teal, 'overlap': G.Teal, 'joint': G.Teal,
           'finbert': G.MainBlue, 'qwen': G.MainBlue}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={'width_ratios': [1.1, 1]})
    y = np.arange(len(names))[::-1]
    v = [100 * R[k]['r2'] for k, _ in names]
    a1.barh(y, v, 0.62, color=[col[k] for k, _ in names])
    for yi, vi in zip(y, v):
        a1.text(vi + 0.03, yi, f'{vi:.2f}', va='center', fontsize=7.5, color='black')
    a1.set_yticks(y)
    a1.set_yticklabels([lab for _, lab in names])
    a1.set_xlim(0, max(v) * 1.25)
    a1.set_xlabel('$R^2$ on the 2020–2023 test texts (%)')
    a1.set_title('How much of the 4-day return is explained?')
    grp = [('lm_only', 'LM not in ML'), ('ml_only', 'ML not in LM'), ('overlap', 'LM and ML')]
    x = np.arange(len(grp))
    for j, (sgn, c) in enumerate(((0, G.Forest), (1, G.IDAred))):
        b = [R[k]['b'][sgn] for k, _ in grp]
        e = [1.96 * R[k]['se'][sgn] for k, _ in grp]
        a2.bar(x + (j - 0.5) * 0.36, b, 0.36, color=c, yerr=e, capsize=3, ecolor=G.Navy)
    a2.axhline(0, color=G.Navy, lw=0.6)
    a2.set_xticks(x)
    a2.set_xticklabels([lab for _, lab in grp])
    a2.set_ylabel('Excess return per 1 s.d.\nof the word share (%)')
    a2.set_title('Positive and negative lists')
    fig.tight_layout()
    h = [Patch(color=G.Orange), Patch(color=G.Teal), Patch(color=G.MainBlue), Patch(color=G.Forest),
         Patch(color=G.IDAred)]
    G.fig_legend_bottom(fig, h, ['Loughran-McDonald (LM) lists', 'Lists learned from returns (ML)',
                                 'Language models (daily mean score)', 'Positive words (95% CI, Driscoll-Kraay)',
                                 'Negative words (95% CI, Driscoll-Kraay)'], ncol=3, y=0.0)
    G.save_fig('ch15_colour_words')


if __name__ == '__main__':
    r = run()
    fig_colour_words(r)
    b = r['by_cut'][str(int(CUT))]
    print({k: r[k] for k in ('n_docs', 'n_train', 'n_test', 'n_dropped', 'winsor_train', 'n_cal_test', 'n_vocab',
                             'n_types', 'train', 'test')})
    print({k: v for k, v in b.items() if k != 'reg'})
    for k, x in b['reg'].items():
        if k == 'boot':
            print(x)
        elif k != 'share_hit':
            print(k, round(100 * x['r2'], 3), [round(t, 3) for t in x['b']], [round(t, 2) for t in x['t']])
    print('top pos', [w for w, *_ in r['top_pos'][:25]])
    print('top neg', [w for w, *_ in r['top_neg'][:25]])
    print('overlap', r['ov_pos'], r['ov_neg'])
    print('flip', r['lm_flip'])

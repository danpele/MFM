"""
Seminarul 15: LLM-uri si analiza sentimentului -- calculele pentru Partile A, B si C
===================================================================================
Foloseste tabelele de scoruri produse de run_scores.py (ch15_*.csv) si functiile din generate_all_charts.py.
Rezultat: sem15_results.json si graficele ch15_sem_*.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_text as M            # noqa: E402
import generate_all_charts as g  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
S = {}


# =============================================================================
# PARTEA A
# =============================================================================
def dict_example(text, D):
    w = M.tokens(text)
    out = {}
    for k in ('LM', 'GI'):
        pos = [x for x in w if x in D[k + '_pos']]
        neg = [x for x in w if x in D[k + '_neg']]
        P, N = len(pos), len(neg)
        out[k] = {'pos': pos, 'neg': neg, 'P': P, 'N': N, 'tone': (P - N) / (P + N) if P + N else 0.0}
    out['n_words'] = len(w)
    return out


def part_a():
    """A1-A2: tonul dupa doua dictionare; A3-A4: metrici din matricea de confuzie; A5-A6: probabilitati si
    clasa majoritara; A7-A8: costul la care strategia nu mai castiga nimic."""
    pb = M.load_phrasebank()
    D = M.load_dictionaries()
    # propozitii reale din PhraseBank (acord 100%) in care cele doua dictionare dau semne diferite
    allag = pb[pb['agree'] == 'AllAgree'].copy()
    allag['len'] = allag['text'].str.len()
    lm = M.dict_tone(allag['text'], D['LM_pos'], D['LM_neg'])
    gi = M.dict_tone(allag['text'], D['GI_pos'], D['GI_neg'])
    c1 = allag[(allag['label'] == 'positive') & (lm > 0) & (gi < 0)].sort_values('len')
    c2 = allag[(allag['label'] == 'neutral') & (lm == 0) & (gi < 0)].sort_values('len')
    for key, text in (('A1', c1['text'].iloc[0]), ('A2', c2['text'].iloc[0])):
        r = dict_example(text, D)
        r['label'] = pb.loc[pb['text'] == text, 'label'].iloc[0]
        r['text'] = text
        S[key] = r
    tw = g.load_csv('ch15_twitter_scores.csv')
    pr = g.predictions(tw)
    for key, m in (('A3', 'FinBERT'), ('A4', 'LM')):
        cm = M.confusion(tw['label'], pr[m])
        cmx = M.class_metrics(tw['label'], pr[m])
        S[key] = {'cm': cm.values.tolist(), 'acc': M.acc(tw['label'], pr[m]), 'f1': M.macro_f1(tw['label'], pr[m]),
                  'metrics': cmx.to_dict('index')}
    # A5: probabilitatile Qwen2.5-7B pentru un titlu; temperatura
    i = int(np.argmin(np.abs(tw['qwen7B_negative'] - 0.62)))
    p = tw.loc[i, ['qwen7B_negative', 'qwen7B_neutral', 'qwen7B_positive']].values.astype(float)
    logit = np.log(np.maximum(p, 1e-12))
    logit = logit - logit.max()
    T = 2.0
    pT = np.exp(logit / T) / np.exp(logit / T).sum()
    S['A5'] = {'id': i, 'label': tw.loc[i, 'label'], 'p': p.tolist(), 'logit': logit.tolist(), 'T': T,
               'pT': pT.tolist(), 'net': float(p[2] - p[0])}
    n = tw['label'].value_counts()
    S['A6'] = {'n': n.to_dict(), 'N': int(n.sum()), 'acc_neutral': float(n['neutral'] / n.sum()),
               'f1_neutral_class': float(2 * (n['neutral'] / n.sum()) / (1 + n['neutral'] / n.sum())),
               'macro_f1': M.macro_f1(tw['label'], np.full(len(tw), 'neutral'))}


def part_a_costs(R):
    """A7-A8: pragul de cost (puncte de baza pe tranzactie) sub care strategia ramane profitabila."""
    st = R['news']['strat']['finbert']
    S['A7'] = {'mean_active_bp': st['mean_active_bp'], 'breakeven_bp': st['mean_active_bp'] / 4,
               'active': st['active']}
    S['A8'] = {'mean_active_bp': st['mean_active_bp'], 'hold': 5}


def part_a_inference(R):
    """A1-A8 (derivari): atenuarea prin clasificare gresita (Aigner, 1973), varianta si puterea testului McNemar,
    kappa Fleiss si un pas E Dawid-Skene pe un tabel mic, conditia de ordinul intai pentru temperatura,
    eroarea standard a costului de echilibru (metoda delta)."""
    from scipy import stats as st
    out = {}
    # A1-A2: variabila "stire negativa" (rand/coloana 0 din matricea de confuzie Twitter)
    for key in ('A3', 'A4'):
        cm = np.array(S[key]['cm'], float)
        n = cm.sum()
        pi = cm[0].sum() / n
        p = cm[:, 0].sum() / n
        a1 = (cm[0, 1] + cm[0, 2]) / cm[0].sum()
        a0 = (cm[1, 0] + cm[2, 0]) / (cm[1].sum() + cm[2].sum())
        lam = pi * (1 - pi) * (1 - a0 - a1) / (p * (1 - p))
        out['att_' + key] = {'n': n, 'pi': pi, 'p': p, 'a0': a0, 'a1': a1, 'lam': lam, 'inv': 1 / lam,
                             'n_tp': cm[0, 0], 'n_neg': cm[0].sum(), 'n_predneg': cm[:, 0].sum(),
                             'n_fp': cm[1, 0] + cm[2, 0], 'n_nonneg': cm[1].sum() + cm[2].sum()}
    # A3-A4: diferenta de acuratete pe perechi, varianta multinomiala, McNemar exact, puterea
    for key in ('B1', 'B2'):
        b = S[key]
        n = int(np.array(S['A3']['cm']).sum())       # titlurile din setul de validare Twitter
        n01, n10 = b['n01'], b['n10']
        d = (n01 - n10) / n
        q = (n01 + n10) / n
        se = np.sqrt((q - d ** 2) / n)
        pz = 2 * st.norm.sf(abs(d) / se)
        pex = 2 * st.binom.cdf(min(n01, n10), n01 + n10, 0.5)
        zc = st.norm.ppf(0.975)
        power = st.norm.cdf(abs(d) * np.sqrt(n) / np.sqrt(q - d ** 2) - zc)
        n80 = (zc + st.norm.ppf(0.8)) ** 2 * (q - d ** 2) / d ** 2
        out['mc_' + key] = {'n': n, 'n01': n01, 'n10': n10, 'd': d, 'q': q, 'se': se, 'lo': d - zc * se, 'hi': d + zc * se,
                            'p_z': pz, 'p_exact': min(1.0, pex), 'power': power, 'n80': n80}
    # A6: kappa Fleiss si un pas E Dawid-Skene pe un tabel ilustrativ (6 propozitii x 5 evaluatori)
    V = np.array([[5, 0, 0], [0, 5, 0], [0, 1, 4], [1, 3, 1], [2, 3, 0], [0, 2, 3]], float)
    m = V.sum(1)[0]
    Pi = (V * (V - 1)).sum(1) / (m * (m - 1))
    pj = V.sum(0) / V.sum()
    Pbar, Pe = Pi.mean(), (pj ** 2).sum()
    kappa = (Pbar - Pe) / (1 - Pe)
    acc_r = 0.8
    Pi_mat = np.full((3, 3), (1 - acc_r) / 2) + np.eye(3) * (acc_r - (1 - acc_r) / 2)
    like = np.array([[np.prod(Pi_mat[j] ** v) for j in range(3)] for v in V])
    post = like / like.sum(1, keepdims=True)
    maj = V / V.sum(1, keepdims=True)
    out['fleiss'] = {'votes': V.tolist(), 'Pi': Pi.tolist(), 'pj': pj.tolist(), 'Pbar': Pbar, 'Pe': Pe, 'kappa': kappa,
                     'acc_r': acc_r, 'post': post.tolist(), 'share': maj.tolist()}
    # A5(d): temperatura optima pentru Qwen2.5-7B (conditia de ordinul intai), pe jumatatea de validare
    tw = g.load_csv('ch15_twitter_scores.csv')
    y = tw['label'].map({'negative': 0, 'neutral': 1, 'positive': 2}).values
    P = tw[['qwen7B_negative', 'qwen7B_neutral', 'qwen7B_positive']].values.astype(float)
    Z = np.log(np.clip(P / P.sum(1, keepdims=True), 1e-12, 1))
    idx = np.random.default_rng(15).permutation(len(y))[:len(y) // 2]
    Zv, yv = Z[idx], y[idx]

    def foc(T):
        L = Zv / T
        L = L - L.max(1, keepdims=True)
        E = np.exp(L)
        Pt = E / E.sum(1, keepdims=True)
        return float(np.mean(Zv[np.arange(len(yv)), yv]) - np.mean((Pt * Zv).sum(1)))
    from scipy.optimize import brentq
    T_star = brentq(foc, 0.5, 50)
    out['temp'] = {'T': T_star, 'foc_1': foc(1.0), 'foc_T': foc(T_star)}
    # A7-A8: costul de echilibru si eroarea lui standard (metoda delta, varianta Newey-West a mediei)
    for c in ('finbert', 'qwen'):
        x = R['news']['strat'][c]
        mu, t, a = x['mean_bp'], x['t'], x['active']
        se_mu = mu / t
        cstar = mu / (4 * a)
        se_c = se_mu / (4 * a)
        sigma = np.sqrt(252) * mu / x['sr']
        out['cost_' + c] = {'mu': mu, 't': t, 'a': a, 'se_mu': se_mu, 'c': cstar, 'se_c': se_c,
                            'lo': cstar - 1.96 * se_c, 'hi': cstar + 1.96 * se_c, 'sigma': sigma,
                            'sr': x['sr'], 'sr_net5': np.sqrt(252) * (mu - 4 * a * 5) / sigma, 'sr_net': x['sr_net']}
    S['AI'] = out
    return out


# =============================================================================
# PARTEA B
# =============================================================================
def b_pairs(a, b, data='tw'):
    d = g.load_csv('ch15_twitter_scores.csv' if data == 'tw' else 'ch15_phrasebank_scores.csv')
    y = d['label'].values
    pr = g.predictions(d)
    n01, n10, p = M.mcnemar(y, pr[a], pr[b])
    lo, hi = M.diff_ci(y, pr[a], pr[b])
    return {'acc_a': M.acc(y, pr[a]), 'acc_b': M.acc(y, pr[b]), 'diff': M.acc(y, pr[b]) - M.acc(y, pr[a]),
            'lo': lo, 'hi': hi, 'n01': n01, 'n10': n10, 'p': p,
            'ci_a': M.boot_ci(y, pr[a], M.acc), 'ci_b': M.boot_ci(y, pr[b], M.acc)}


def b_leakage():
    """B3: acuratetea pe datele de antrenare ale FinBERT (PhraseBank) si pe date noi (Twitter)."""
    pb = g.load_csv('ch15_phrasebank_scores.csv')
    tw = g.load_csv('ch15_twitter_scores.csv')
    out = {}
    for m in ('FinBERT', 'Qwen 7B', 'LM', 'MiniLM + LR'):
        r = {}
        for name, d in (('pb_all', pb[pb['agree'] == 'AllAgree']), ('pb', pb), ('tw', tw)):
            yh = g.predictions(d)[m]
            r[name] = {'acc': M.acc(d['label'], yh), 'ci': M.boot_ci(d['label'].values, yh, M.acc),
                       'f1': M.macro_f1(d['label'], yh)}
        out[m] = r
    return out


def b_learning():
    lc = g.load_csv('ch15_learning_curve.csv')
    tw = g.load_csv('ch15_twitter_scores.csv')
    fb = M.acc(tw['label'], g.predictions(tw)['FinBERT'])
    q7 = M.acc(tw['label'], g.predictions(tw)['Qwen 7B'])
    m = lc.groupby('n')[['emb_acc', 'tfidf_acc']].agg(['mean', 'std'])
    first_emb = next((int(n) for n in m.index if m.loc[n, ('emb_acc', 'mean')] > fb), None)
    first_tf = next((int(n) for n in m.index if m.loc[n, ('tfidf_acc', 'mean')] > fb), None)
    return {'fb': fb, 'q7': q7, 'first_emb': first_emb, 'first_tfidf': first_tf,
            'table': {int(n): {'emb': float(r[('emb_acc', 'mean')]), 'emb_sd': float(r[('emb_acc', 'std')]),
                               'tfidf': float(r[('tfidf_acc', 'mean')])} for n, r in m.iterrows()}}


def b_cluster(P):
    """B5: aceeasi regresie, erori standard OLS vs grupate pe zile vs grupate pe actiuni."""
    out = {}
    for c in ('finbert', 'lm', 'qwen'):
        for y in ('r0', 'r1', 'r2'):
            a = M.cluster_ols(P[y].values, P[f'z_{c}'].values, P.index.get_level_values('day'))
            b = M.cluster_ols(P[y].values, P[f'z_{c}'].values, P.index.get_level_values('ticker'))
            out[f'{c}|{y}'] = {'b_bp': 100 * a['b'], 'se_ols': 100 * a['se_ols'], 'se_day': 100 * a['se_cl'],
                               'se_tic': 100 * b['se_cl'], 't_ols': a['t_ols'], 't_day': a['t_cl'],
                               't_tic': b['t_cl'], 'n': a['n'], 'G_day': a['G'], 'G_tic': b['G'], 'r2': a['r2']}
    return out


def b_event(P, col):
    cols = g.EVENT_COLS
    neg, pos = g.event_groups(P[col])
    out = {'zero_share': float((P[col] == 0).mean())}
    for grp, sel in (('neg', neg), ('pos', pos)):
        X = P.loc[sel, cols].groupby(level='day').mean().fillna(0)
        car = X.cumsum(axis=1)
        pre = X[['rm5', 'rm4', 'rm3', 'rm2', 'rm1']].sum(1)
        post = X[['r2', 'rp3', 'rp4', 'rp5']].sum(1)
        out[grp] = {'car_m1': float(car['rm1'].mean()), 'car_0': float(car['r0'].mean()),
                    'day0': float(X['r0'].mean()), 'day0_t': M.nw_t(X['r0'])[1],
                    'day1': float(X['r1'].mean()), 'day1_t': M.nw_t(X['r1'])[1],
                    'pre': float(pre.mean()), 'pre_t': M.nw_t(pre)[1],
                    'post': float(post.mean()), 'post_t': M.nw_t(post)[1], 'n_days': len(X), 'n_obs': int(sel.sum())}
    return out


def b_memory():
    """B7: AUC pentru directia lunara a S&P 500, inainte si dupa publicarea ponderilor Qwen2.5."""
    mm = g.load_csv('ch15_memory_monthly.csv', index_col=0, parse_dates=True)
    out = {}
    for s in ('1.5B', '7B', '14B'):
        r = {}
        for per, sel in (('pre', mm.index <= '2024-08-31'), ('post', mm.index >= '2024-10-01')):
            p, u = mm.loc[sel, f'qwen{s}'].values, (mm.loc[sel, 'ret'] > 0).values
            lo, hi = g.boot_auc(p, u)
            r[per] = {'auc': g.auc(p, u), 'lo': lo, 'hi': hi, 'n': int(sel.sum()), 'n_up': int(u.sum()),
                      'mean_up': float(p[u].mean()), 'mean_down': float(p[~u].mean())}
        out[s] = r
    # permutare: AUC sub ipoteza nula, perioada de dinainte (14B)
    rng = np.random.default_rng(1)
    pre = mm.loc[:'2024-08-31']
    p, u = pre['qwen14B'].values, (pre['ret'] > 0).values
    null = [g.auc(p, rng.permutation(u)) for _ in range(2000)]
    out['perm_p'] = float(np.mean(np.array(null) >= g.auc(p, u)))
    return out


def b_prompts():
    tw = g.load_csv('ch15_twitter_scores.csv')
    y = tw['label'].values
    out = {}
    for s in ('7B', '14B'):
        labs = {p: M.probs_label(tw[[f'qwen{s}{"" if p == "P1" else "_" + p}_{l}' for l in M.LABELS]].values)
                for p in ('P1', 'P2', 'P3')}
        r = {p: {'acc': M.acc(y, v), 'ci': M.boot_ci(y, v, M.acc), 'neutral': float(np.mean(v == 'neutral'))}
             for p, v in labs.items()}
        n01, n10, pv = M.mcnemar(y, labs['P1'], labs['P3'])
        r['p13'] = {'n01': n01, 'n10': n10, 'p': pv, 'agree': float(np.mean(labs['P1'] == labs['P3']))}
        r['agree_all'] = float(np.mean((labs['P1'] == labs['P2']) & (labs['P1'] == labs['P3'])))
        out[s] = r
    return out


# =============================================================================
# PARTEA C
# =============================================================================
def part_c(P, rets):
    """Prezice sentimentul FinBERT al titlurilor randamentul din d+2 (pozitie de la inchiderea din d+1 la inchiderea din d+2), dupa costuri?"""
    days = rets.index[rets.index >= P.index.get_level_values('day').min()]
    out = {}
    for c in ('finbert', 'qwen', 'lm'):
        r = {}
        for band_name, band in (('all', 0.0), ('strong', 0.5)):
            St = M.signal_portfolio(P, c, days, cost_bp=5, band=band, ret='r2')
            mu, t = M.nw_t(St['gross'])
            lo, hi = M.block_boot_mean(St['gross'].values)
            act = St['k'] > 0
            r[band_name] = {'mean_bp': 100 * mu, 't': t, 'lo_bp': 100 * lo, 'hi_bp': 100 * hi,
                            'sr': M.sharpe(St['gross']), 'sr_net': M.sharpe(St['net']),
                            'net_bp': 100 * St['net'].mean(), 'active': float(act.mean()),
                            'be_bp': 100 * St.loc[act, 'gross'].mean() / 4 if act.any() else np.nan,
                            'n_active': int(act.sum())}
        out[c] = r
    # doar dupa titlurile publicate in afara sesiunii? nu: sensibilitate la costuri
    St = M.signal_portfolio(P, 'finbert', days, ret='r2')
    act = St['k'] > 0
    out['cost_grid'] = {int(c): float(M.sharpe(St['gross'] - np.where(act, 4 * c / 100, 0))) for c in (0, 1, 2, 5, 10)}
    out['cum'] = St
    # graficul: randamentul cumulat net pentru trei niveluri de cost
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    for cbp, col in ((0, g.MainBlue), (2, g.Teal), (5, g.IDAred)):
        net = St['gross'] - np.where(act, 4 * cbp / 100, 0)
        ax.plot(St.index, net.cumsum(), color=col, lw=1.0, label=f'FinBERT signal, {cbp} bp per trade')
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_ylabel('Cumulative d+2 return (%, sum)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.14)
    g.save_fig('ch15_sem_partc')
    return out


def fig_cluster(B5):
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    x = np.arange(3)
    for k, (se, c, lab) in enumerate((('se_ols', g.Amber, 'OLS standard errors'),
                                      ('se_day', g.MainBlue, 'Clustered by day'),
                                      ('se_tic', g.Purple, 'Clustered by stock'))):
        b = [B5[f'{s}|r0']['b_bp'] for s in ('finbert', 'qwen', 'lm')]
        e = [1.96 * B5[f'{s}|r0'][se] for s in ('finbert', 'qwen', 'lm')]
        ax.errorbar(x + (k - 1) * 0.2, b, yerr=e, fmt='o', color=c, capsize=3, ms=4, label=lab)
    ax.axhline(0, color=g.Gray, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(['FinBERT', 'Qwen2.5-7B', 'Loughran-McDonald'])
    ax.set_ylabel('Same-day excess return per 1 s.d. (bp)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.16)
    g.save_fig('ch15_sem_cluster')


# =============================================================================
# GRAFICELE SEMINARULUI (cate unul pentru fiecare rezolvare din Partea B si pentru A1, A3, A7)
# =============================================================================
def fig_a1_attenuation(key='A3', name='ch15_sem_a1_attenuation', label='FinBERT', col=None, reps=2000, seed=15):
    """A1/A2: distributia pantei OLS pe variabila adevarata s* si pe variabila prezisa s_hat, simulata cu ratele de
    clasificare gresita din matricea de confuzie Twitter; beta = 1, zgomot N(0, 1), n = numarul de titluri."""
    x = S['AI']['att_' + key]
    n, pi, a0, a1, lam = int(x['n']), x['pi'], x['a0'], x['a1'], x['lam']
    rng = np.random.default_rng(seed)
    bt, bh = np.empty(reps), np.empty(reps)
    for k in range(reps):
        s = rng.random(n) < pi
        u = rng.random(n)
        sh = np.where(s, u >= a1, u < a0)
        r = s + rng.standard_normal(n)
        bt[k] = np.cov(r, s)[0, 1] / np.var(s, ddof=1)
        bh[k] = np.cov(r, sh)[0, 1] / np.var(sh, ddof=1)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    bins = np.linspace(min(bh.min(), bt.min()), max(bh.max(), bt.max()), 60)
    ax.hist(bt, bins=bins, color=g.MainBlue, alpha=0.75, label='Slope on the true dummy $s^*$')
    ax.hist(bh, bins=bins, color=col or g.Forest, alpha=0.75, label=f'Slope on the {label} dummy $\\hat s$')
    ax.axvline(1.0, color=g.MainBlue, lw=1.2, ls='--', label=r'True $\beta = 1$')
    ax.axvline(lam, color=g.IDAred, lw=1.2, ls='--', label=rf'$\beta\lambda = {lam:.3f}$')
    ax.set_xlabel(f'OLS slope, {reps:,} simulated samples of {n:,} headlines')
    ax.set_ylabel('Number of samples')
    g.legend_outside_bottom(ax, ncol=2, y=-0.24)
    g.save_fig(name)
    return {'mean_true': float(bt.mean()), 'mean_hat': float(bh.mean()), 'sd_hat': float(bh.std(ddof=1))}


def fig_power(keys=('mc_B1',), labels=('LM vs FinBERT',), name='ch15_sem_a3_power'):
    """A3/A4: puterea testului pe perechi in functie de numarul de titluri, cu d si q estimate pe Twitter."""
    from scipy import stats as st
    zc = st.norm.ppf(0.975)
    nn = np.logspace(2, 4.6, 200)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    for key, lab, col in zip(keys, labels, (g.MainBlue, g.IDAred)):
        x = S['AI'][key]
        d, q, n0 = abs(x['d']), x['q'], x['n']
        pw = st.norm.cdf(d * np.sqrt(nn) / np.sqrt(q - d ** 2) - zc)
        ax.plot(nn, pw, color=col, lw=1.6, label=f'{lab}: $d$ = {100 * x["d"]:+.1f} pp')
        ax.plot([n0], [x['power']], 'o', color=col, ms=5)
        ax.axvline(x['n80'], color=col, lw=0.9, ls=':', label=f'{lab}: $n_{{80}}$ = {x["n80"]:,.0f}')
    ax.axhline(0.8, color=g.Gray, lw=0.7, ls='--')
    ax.axvline(S['AI'][keys[0]]['n'], color=g.Gray, lw=0.7)
    ax.set_xscale('log')
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('Number of headlines $n$ (log scale); solid grey line: the validation set, dots: its power')
    ax.set_ylabel('Power at 5%')
    g.legend_outside_bottom(ax, ncol=2, y=-0.26)
    g.save_fig(name)


def fig_cost(key='cost_finbert', label='FinBERT', name='ch15_sem_a7_cost'):
    """A7/A8: randamentul net zilnic mediu in functie de costul pe tranzactie, cu banda +-1.96 SE (a fix)."""
    x = S['AI'][key]
    c = np.linspace(0, 6, 121)
    net = x['mu'] - 4 * x['a'] * c
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.fill_between(c, net - 1.96 * x['se_mu'], net + 1.96 * x['se_mu'], color=g.LightGray, alpha=0.7,
                    label=r'$\pm 1.96$ SE of the mean')
    ax.plot(c, net, color=g.MainBlue, lw=1.6, label=f'{label} strategy: mean net return per day')
    ax.axhline(0, color=g.Gray, lw=0.7)
    ax.axvline(x['c'], color=g.IDAred, lw=1.2, ls='--', label=f'Break-even cost $c^*$ = {x["c"]:.2f} bp')
    ax.axvspan(max(x['lo'], 0), x['hi'], color=g.IDAred, alpha=0.12, label='95% CI of $c^*$')
    ax.axvline(5, color=g.Amber, lw=1.2, label='Realistic cost, 5 bp per trade')
    ax.set_xlabel('Cost per trade $c$ (bp); four trades on each day with positions')
    ax.set_ylabel('Mean net return (bp per day)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.26)
    g.save_fig(name)


def fig_pairs(key='B1', names=('LM', 'FinBERT'), name='ch15_sem_b1_pairs'):
    """B1/B2: acuratetea celor doi clasificatori cu CI bootstrap, diferenta pe perechi cu CI si cazurile discordante."""
    b = S[key]
    fig, (ax, cx, bx) = plt.subplots(1, 3, figsize=(7.0, 2.4), gridspec_kw={'width_ratios': [1.3, 1.1, 1.0]})
    for yy, v, ci, col in ((1, b['acc_a'], b['ci_a'], g.Orange), (0, b['acc_b'], b['ci_b'], g.MainBlue)):
        ax.errorbar(100 * v, yy, xerr=[[100 * (v - ci[0])], [100 * (ci[1] - v)]], fmt='o', color=col, capsize=3, ms=5)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(list(names))
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel('Accuracy (%), 95% bootstrap CI')
    d = 100 * b['diff']
    cx.errorbar(d, 0, xerr=[[d - 100 * b['lo']], [100 * b['hi'] - d]], fmt='s', color=g.IDAred, capsize=3, ms=5)
    cx.axvline(0, color=g.Gray, lw=0.8, ls='--')
    cx.set_yticks([0])
    cx.set_yticklabels([f'{names[1]} $-$\n{names[0]}'], fontsize=7)
    cx.set_ylim(-1, 1)
    cx.set_xlabel('Paired difference (pp), 95% CI')
    n01, n10 = b['n01'], b['n10']
    bx.bar([0, 1], [n01, n10], color=[g.MainBlue, g.Orange], width=0.6)
    bx.axhline((n01 + n10) / 2, color=g.Gray, lw=0.8, ls='--')
    bx.set_xticks([0, 1])
    bx.set_xticklabels([f'$n_{{01}}$ = {n01}', f'$n_{{10}}$ = {n10}'])
    bx.set_ylim(0, 1.18 * max(n01, n10))
    bx.set_ylabel('Discordant headlines')
    bx.set_xlabel('Dashed line: $H_0$')
    fig.tight_layout()
    g.save_fig(name)


def fig_leakage():
    """B3: acuratetea pe tot Financial PhraseBank si pe Twitter, pentru patru clasificatori."""
    B3 = S['B3']
    ms = ['FinBERT', 'Qwen 7B', 'LM', 'MiniLM + LR']
    labs = ['FinBERT', 'Qwen2.5-7B', 'LM', 'MiniLM + LR']
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    for k, m in enumerate(ms):
        a, b = 100 * B3[m]['pb']['acc'], 100 * B3[m]['tw']['acc']
        ax.plot([a, b], [k, k], color=g.Amber, lw=1.4)
        ax.plot(a, k, 'o', color=g.MainBlue, ms=6, label='Financial PhraseBank (all)' if k == 0 else None)
        ax.plot(b, k, 's', color=g.IDAred, ms=6, label='Twitter validation set' if k == 0 else None)
        ax.text(max(a, b) + 0.8, k, f'{a - b:+.1f} pp', va='center', fontsize=8, color='black')
    ax.set_yticks(range(len(ms)))
    ax.set_yticklabels(labs)
    ax.invert_yaxis()
    ax.set_xlabel('Accuracy (%); label: PhraseBank minus Twitter')
    g.legend_outside_bottom(ax, ncol=2, y=-0.26)
    g.save_fig('ch15_sem_b3_leakage')


def fig_event_paths(P):
    """B6: randamentul in exces cumulat mediu, zilele -5..+5, grupurile LM (semn) si FinBERT (tercile)."""
    cols = g.EVENT_COLS
    days = np.arange(-5, 6)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    style = {('lm', 'neg'): (g.Orange, '--', 'LM tone < 0'), ('lm', 'pos'): (g.Teal, '--', 'LM tone > 0'),
             ('finbert', 'neg'): (g.IDAred, '-', 'FinBERT bottom tercile'),
             ('finbert', 'pos'): (g.Forest, '-', 'FinBERT top tercile')}
    for c in ('lm', 'finbert'):
        neg, pos = g.event_groups(P[c])
        for grp, sel in (('neg', neg), ('pos', pos)):
            X = P.loc[sel, cols].groupby(level='day').mean().fillna(0)
            col, ls, lab = style[(c, grp)]
            ax.plot(days, X.cumsum(axis=1).mean().values, color=col, ls=ls, marker='o', ms=3, lw=1.3, label=lab)
    ax.axvline(0, color=g.Gray, lw=0.7, ls=':')
    ax.axhline(0, color=g.Gray, lw=0.7)
    ax.axvspan(1.5, 5.5, color=g.LightGray, alpha=0.4)
    ax.set_xticks(days)
    ax.set_xlabel('Trading days relative to the news day $d$ (shaded: tradable days $d+2$ to $d+5$)')
    ax.set_ylabel('Cumulative excess return (%)')
    g.legend_outside_bottom(ax, ncol=4, y=-0.26)
    g.save_fig('ch15_sem_b6_event')


def fig_perm():
    """B7: distributia AUC sub ipoteza nula (etichete amestecate), Qwen2.5-14B, lunile dinainte de publicare."""
    mm = g.load_csv('ch15_memory_monthly.csv', index_col=0, parse_dates=True)
    rng = np.random.default_rng(1)
    pre = mm.loc[:'2024-08-31']
    p, u = pre['qwen14B'].values, (pre['ret'] > 0).values
    null = np.array([g.auc(p, rng.permutation(u)) for _ in range(2000)])
    obs = g.auc(p, u)
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    ax.hist(null, bins=40, color=g.MainBlue, alpha=0.8, label='AUC with shuffled up/down labels (2,000 permutations)')
    ax.axvline(obs, color=g.IDAred, lw=1.6, label=f'Observed AUC = {obs:.2f}')
    ax.axvline(0.5, color=g.Gray, lw=0.7, ls='--')
    ax.set_xlabel('AUC of Qwen2.5-14B, monthly S&P 500 direction, months before the release')
    ax.set_ylabel('Permutations')
    g.legend_outside_bottom(ax, ncol=2, y=-0.26)
    g.save_fig('ch15_sem_b7_perm')
    return float(np.mean(null >= obs))


def fig_prompts_ci():
    """B8: acuratetea cu CI bootstrap si ponderea raspunsurilor 'neutral' pentru trei prompturi."""
    B8 = S['B8']
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.8, 2.6))
    for k, (s, col) in enumerate((('7B', g.MainBlue), ('14B', g.Purple))):
        x = np.arange(3) + (k - 0.5) * 0.25
        acc = [100 * B8[s][q]['acc'] for q in ('P1', 'P2', 'P3')]
        lo = [a - 100 * B8[s][q]['ci'][0] for a, q in zip(acc, ('P1', 'P2', 'P3'))]
        hi = [100 * B8[s][q]['ci'][1] - a for a, q in zip(acc, ('P1', 'P2', 'P3'))]
        ax.errorbar(x, acc, yerr=[lo, hi], fmt='o', color=col, capsize=3, ms=5, label=f'Qwen2.5-{s}')
        bx.bar(x, [100 * B8[s][q]['neutral'] for q in ('P1', 'P2', 'P3')], width=0.25, color=col)
    for a in (ax, bx):
        a.set_xticks(range(3))
        a.set_xticklabels(['P1', 'P2', 'P3'])
    ax.set_ylabel('Accuracy (%), 95% bootstrap CI')
    bx.set_ylabel('"neutral" answers (%)')
    tw = g.load_csv('ch15_twitter_scores.csv')
    bx.axhline(100 * (tw['label'] == 'neutral').mean(), color=g.Gray, lw=0.8, ls='--')
    bx.set_title('Dashed: share of neutral headlines', fontsize=8, color='black')
    g.legend_outside_bottom(ax, ncol=2, y=-0.18)
    fig.tight_layout()
    g.save_fig('ch15_sem_b8_prompts')


def fig_pvalues(PN):
    """B10: valorile p ale celor noua pante, trei metode (t15, wild cluster bootstrap, Holm), scala logaritmica;
    PN = ch15_inference.json['panel']['reg'] (valid_inference.py)."""
    rows = [(c, h) for c in ('finbert', 'qwen', 'lm') for h in ('r0', 'r1', 'r2')]
    names = {'finbert': 'FinBERT', 'qwen': 'Qwen2.5-7B', 'lm': 'LM'}
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    y = np.arange(len(rows))
    floor = 1e-4
    for key, col, mk, lab in (('p_t15', g.MainBlue, 'o', '$t_{15}$ critical values'),
                              ('p_wcr', g.Orange, 's', 'Wild cluster bootstrap (9,999 draws)'),
                              ('p_wcr_holm', g.IDAred, 'D', 'Wild bootstrap, Holm over 9 slopes')):
        ax.plot([max(PN[f'{c}|{h}'][key], floor) for c, h in rows], y, mk, color=col, ms=5, label=lab)
    ax.axvline(0.05, color=g.Gray, lw=0.8, ls='--')
    ax.set_xscale('log')
    ax.set_xlim(5e-5, 1.5)
    ax.set_yticks(y)
    ax.set_yticklabels([f'{names[c]}, $h$ = {h[1]}' for c, h in rows], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel('$p$-value (log scale; values below $10^{-4}$ drawn at $10^{-4}$; dashed: 5%)')
    g.legend_outside_bottom(ax, ncol=3, y=-0.24)
    g.save_fig('ch15_sem_b10_pvalues')


def seminar_charts(P):
    out = {'a1_sim': fig_a1_attenuation(), 'a2_sim': fig_a1_attenuation('A4', 'ch15_sem_a2_attenuation', 'LM', g.Orange)}
    fig_power()
    fig_power(('mc_B1', 'mc_B2'), ('LM vs FinBERT', 'FinBERT vs Qwen2.5-7B'), 'ch15_sem_a4_power')
    fig_cost()
    fig_cost('cost_qwen', 'Qwen2.5-7B', 'ch15_sem_a8_cost')
    fig_pairs()
    fig_pairs('B2', ('FinBERT', 'Qwen2.5-7B'), 'ch15_sem_b2_pairs')
    fig_leakage()
    fig_event_paths(P)
    out['perm_check'] = fig_perm()
    fig_prompts_ci()
    with open(os.path.join(HERE, 'ch15_inference.json')) as f:
        fig_pvalues(json.load(f)['panel']['reg'])
    S['charts'] = out


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items() if not isinstance(v, pd.DataFrame)}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return o


if __name__ == '__main__':
    with open(os.path.join(HERE, 'ch15_results.json')) as f:
        R = json.load(f)
    part_a()
    part_a_costs(R)
    S['B1'] = b_pairs('LM', 'FinBERT')
    S['B2'] = b_pairs('FinBERT', 'Qwen 7B')
    S['B3'] = b_leakage()
    S['B4'] = b_learning()
    P, rets = g.news_panel()
    S['B5'] = b_cluster(P)
    fig_cluster(S['B5'])
    S['B6'] = {'lm': b_event(P, 'lm'), 'finbert': b_event(P, 'finbert')}
    S['B7'] = b_memory()
    S['B8'] = b_prompts()
    S['C'] = part_c(P, rets)
    part_a_inference(R)
    seminar_charts(P)
    old = os.path.join(HERE, 'sem15_results.json')
    if os.path.exists(old):                     # C3 (c3_reference.py) se pastreaza
        with open(old) as f:
            c3 = json.load(f).get('c3')
        if c3 is not None:
            S['c3'] = c3
    with open(os.path.join(HERE, 'sem15_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1, default=float)
    print('saved sem15_results.json')

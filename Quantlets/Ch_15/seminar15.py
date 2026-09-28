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
    q1, q2 = P[col].quantile([1 / 3, 2 / 3])
    out = {}
    for grp, sel in (('neg', P[col] <= q1), ('pos', P[col] >= q2)):
        X = P.loc[sel, cols].groupby(level='day').mean().fillna(0)
        car = X.cumsum(axis=1)
        pre = X[['rm5', 'rm4', 'rm3', 'rm2', 'rm1']].sum(1)
        post = X[['r2', 'rp3', 'rp4', 'rp5']].sum(1)
        out[grp] = {'car_m1': float(car['rm1'].mean()), 'car_0': float(car['r0'].mean()),
                    'day0': float(X['r0'].mean()), 'day0_t': M.nw_t(X['r0'])[1],
                    'day1': float(X['r1'].mean()), 'day1_t': M.nw_t(X['r1'])[1],
                    'pre': float(pre.mean()), 'pre_t': M.nw_t(pre)[1],
                    'post': float(post.mean()), 'post_t': M.nw_t(post)[1], 'n_days': len(X)}
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
    """Prezice sentimentul FinBERT al titlurilor randamentul din ziua urmatoare, dupa costuri?"""
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
    ax.set_ylabel('Cumulative next-day return (%, sum)')
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
    with open(os.path.join(HERE, 'sem15_results.json'), 'w') as f:
        json.dump(jsonable(S), f, indent=1, default=float)
    print('saved sem15_results.json')

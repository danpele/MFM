"""
Generator pentru graficele din Capitolul 15: LLM-uri si analiza sentimentului
============================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Texte etichetate: Financial PhraseBank, Twitter Financial News; titluri datate: FNSPID; preturi: data/market.
Scorurile modelelor de limbaj sunt produse de run_scores.py (ch15_*.csv); aici se evalueaza si se deseneaza.
Rezultat numeric: ch15_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_text as M   # noqa: E402

# Stil standard MFM: transparent + ENG + legenda jos
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.1
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

# Culori brand
MainBlue = '#1A3A6E'
IDAred = '#CD0000'
Forest = '#2E7D32'
Amber = '#B5853F'
Orange = '#E67E22'
Purple = '#8E44AD'
Crimson = '#DC3545'
Teal = '#17A2B8'
Magenta = '#D63384'
Brown = '#795548'
Gray = '#7F7F7F'          # doar linii de referinta
LightGray = '#DADADA'     # doar benzi

LAB_COL = {'negative': IDAred, 'neutral': Amber, 'positive': Forest}
METHODS = ['GI', 'VADER', 'LM', 'TF-IDF + LR', 'MiniLM + LR', 'FinBERT', 'Qwen 0.5B', 'Qwen 1.5B', 'Qwen 3B',
           'Qwen 7B', 'Qwen 14B']
M_COL = {'GI': Brown, 'VADER': Amber, 'LM': Orange, 'TF-IDF + LR': Teal, 'MiniLM + LR': Magenta,
         'FinBERT': MainBlue, 'Qwen 0.5B': '#F4A6A6', 'Qwen 1.5B': '#E86A6A', 'Qwen 3B': Crimson,
         'Qwen 7B': IDAred, 'Qwen 14B': '#7A0000'}
SIZES_B = {'0.5B': 0.5, '1.5B': 1.5, '3B': 3.0, '7B': 7.0, '14B': 14.0}
SCORE_LBL = {'lm': 'Loughran-McDonald tone', 'finbert': 'FinBERT', 'qwen': 'Qwen2.5-7B'}
SCORE_COL = {'lm': Orange, 'finbert': MainBlue, 'qwen': IDAred}
EVENT_COLS = ['rm5', 'rm4', 'rm3', 'rm2', 'rm1', 'r0', 'r1', 'r2', 'rp3', 'rp4', 'rp5']
PERIODS = (('2010', '2015'), ('2016', '2019'), ('2020', '2021'), ('2022', '2023'))

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
RES = {}


def save_fig(name):
    """Salveaza figura ca PDF si PNG transparent."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f'   saved {name}')


def legend_outside_bottom(ax, ncol=2, y=-0.22, **kw):
    """Plaseaza legenda in afara graficului, jos-centru."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False, **kw)


def fig_legend_bottom(fig, handles, labels, ncol=3, y=0.0):
    """O singura legenda pentru toata figura, sub panouri."""
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def load_csv(name, **kw):
    return pd.read_csv(os.path.join(HERE, name), **kw)


# =============================================================================
# CLASIFICAREA TEXTELOR
# =============================================================================
def predictions(d):
    """Eticheta prezisa de fiecare metoda (coloanele ch15_*_scores.csv)."""
    v = d['vader'].values
    out = {'GI': M.tone_label(d['GI_tone'].values), 'LM': M.tone_label(d['LM_tone'].values),
           'VADER': np.where(v >= 0.05, 'positive', np.where(v <= -0.05, 'negative', 'neutral')),
           'TF-IDF + LR': M.probs_label(d[[f'tfidf_{l}' for l in M.LABELS]].values),
           'MiniLM + LR': M.probs_label(d[[f'emb_{l}' for l in M.LABELS]].values),
           'FinBERT': M.probs_label(d[[f'finbert_{l}' for l in M.LABELS]].values)}
    for s in SIZES_B:
        out[f'Qwen {s}'] = M.probs_label(d[[f'qwen{s}_{l}' for l in M.LABELS]].values)
    return out


def eval_texts():
    pb, tw = load_csv('ch15_phrasebank_scores.csv'), load_csv('ch15_twitter_scores.csv')
    R = {'n_pb': len(pb), 'n_tw': len(tw), 'n_pb_all': int((pb['agree'] == 'AllAgree').sum())}
    for name, d in (('pb', pb), ('tw', tw)):
        y = d['label'].values
        pr = predictions(d)
        R[name] = {}
        for m, yh in pr.items():
            lo, hi = M.boot_ci(y, yh, M.acc, B=1000)
            R[name][m] = {'acc': M.acc(y, yh), 'lo': lo, 'hi': hi, 'f1': M.macro_f1(y, yh)}
        R[name]['share'] = d['label'].value_counts(normalize=True).to_dict()
        R[name]['always_neutral_f1'] = M.macro_f1(y, np.full(len(y), 'neutral'))
    # acordul adnotatorilor (PhraseBank)
    pr = predictions(pb)
    R['agree'] = {lvl: {m: M.acc(pb['label'][pb['agree'] == lvl], pr[m][pb['agree'] == lvl])
                        for m in ('LM', 'FinBERT', 'Qwen 7B', 'Qwen 14B')} for lvl in M.AGREE}
    R['agree_n'] = pb['agree'].value_counts().to_dict()
    # teste pe perechi (Twitter)
    y = tw['label'].values
    pt = predictions(tw)
    R['pairs'] = {}
    for a, b in (('LM', 'FinBERT'), ('FinBERT', 'Qwen 7B'), ('FinBERT', 'Qwen 14B'), ('Qwen 1.5B', 'Qwen 7B'),
                 ('FinBERT', 'MiniLM + LR')):
        n01, n10, p = M.mcnemar(y, pt[a], pt[b])
        lo, hi = M.diff_ci(y, pt[a], pt[b], B=1000)
        R['pairs'][f'{a}|{b}'] = {'n01': n01, 'n10': n10, 'p': p, 'diff': M.acc(y, pt[b]) - M.acc(y, pt[a]),
                                  'lo': lo, 'hi': hi}
    # formularea cerintei
    R['prompts'] = {}
    for s in ('1.5B', '7B', '14B'):
        labs = {p: M.probs_label(tw[[f'qwen{s}{"" if p == "P1" else "_" + p}_{l}' for l in M.LABELS]].values)
                for p in ('P1', 'P2', 'P3')}
        R['prompts'][s] = {p: {'acc': M.acc(y, v), 'f1': M.macro_f1(y, v)} for p, v in labs.items()}
        R['prompts'][s]['agree_all'] = float(np.mean((labs['P1'] == labs['P2']) & (labs['P1'] == labs['P3'])))
        R['prompts'][s]['share_neutral'] = {p: float(np.mean(v == 'neutral')) for p, v in labs.items()}
    t = load_csv('ch15_llm_time.csv', index_col=0)['sec_per_text']
    R['time'] = {k.replace('time_qwen', ''): float(v) for k, v in t.items() if '_' not in k.replace('time_qwen', '')}
    lc = load_csv('ch15_learning_curve.csv')
    R['lc'] = lc.groupby('n')[['emb_acc', 'tfidf_acc', 'emb_f1', 'tfidf_f1']].mean().to_dict('index')
    for name, d in (('pb', pb), ('tw', tw)):
        for m in ('LM', 'FinBERT', 'Qwen 7B'):
            R[name][m]['cm'] = M.confusion(d['label'], predictions(d)[m]).values.tolist()
    RES['texts'] = R
    return pb, tw


def fig_dict_words(top=14):
    """Cuvintele negative in Harvard IV-4, dar nu in Loughran-McDonald, cele mai frecvente in PhraseBank."""
    pb = M.load_phrasebank()
    D = M.load_dictionaries()
    only = D['GI_neg'] - D['LM_neg']
    rows = {}
    for t, l in zip(pb['text'], pb['label']):
        for w in set(M.tokens(t)):
            if w in only:
                r = rows.setdefault(w, {'negative': 0, 'neutral': 0, 'positive': 0})
                r[l] += 1
    f = pd.DataFrame(rows).T
    f['n'] = f.sum(1)
    f = f.sort_values('n', ascending=False).head(top)[::-1]
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    left = np.zeros(len(f))
    for l in ('positive', 'neutral', 'negative'):
        ax.barh(f.index.str.lower(), f[l], left=left, color=LAB_COL[l], label=f'Sentences labelled {l}', height=0.7)
        left += f[l].values
    ax.set_xlabel('Number of PhraseBank sentences containing the word')
    legend_outside_bottom(ax, ncol=3, y=-0.16)
    save_fig('ch15_dict_words')
    n_gi = sum(1 for t in pb['text'] if any(w in D['GI_neg'] for w in M.tokens(t)))
    n_only = sum(1 for t in pb['text'] if any(w in only for w in M.tokens(t)) and
                 not any(w in D['LM_neg'] for w in M.tokens(t)))
    lab_only = pb['label'][[any(w in only for w in M.tokens(t)) and not any(w in D['LM_neg'] for w in M.tokens(t))
                            for t in pb['text']]]
    RES['dict'] = {'n_lm_neg': len(D['LM_neg']), 'n_lm_pos': len(D['LM_pos']), 'n_gi_neg': len(D['GI_neg']),
                   'n_gi_pos': len(D['GI_pos']), 'n_only': len(only),
                   'share_gi_neg_not_lm': len(only) / len(D['GI_neg']),
                   'sent_gi_neg': n_gi, 'sent_only': n_only,
                   'sent_only_nonneg': float((lab_only != 'negative').mean()),
                   'top': {w: int(r['n']) for w, r in f[::-1].iterrows()},
                   'top_nonneg': {w: float(1 - r['negative'] / r['n']) for w, r in f[::-1].iterrows()},
                   'hit_lm_pb': float(np.mean([any(w in D['LM_neg'] | D['LM_pos'] for w in M.tokens(t))
                                               for t in pb['text']]))}


def fig_accuracy():
    R = RES['texts']
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.9), sharey=True)
    y = np.arange(len(METHODS))[::-1]
    for ax, key, title in zip(axes, ('pb', 'tw'), ('Financial PhraseBank (news sentences)',
                                                     'Twitter Financial News (2022)')):
        for yi, m in zip(y, METHODS):
            r = R[key][m]
            ax.errorbar(100 * r['acc'], yi, xerr=[[100 * (r['acc'] - r['lo'])], [100 * (r['hi'] - r['acc'])]],
                        fmt='o', color=M_COL[m], ms=5, capsize=2, lw=1)
        base = 100 * R[key]['share']['neutral']
        ax.axvline(base, color=Gray, ls='--', lw=0.8)
        ax.set_title(title, fontsize=8.5, loc='left')
        ax.set_xlabel('Accuracy (%) with 95% CI')
        ax.set_xlim(30, 100)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(METHODS)
    h = [plt.Line2D([], [], color=Gray, ls='--', lw=0.8)]
    fig_legend_bottom(fig, h, ['Always "neutral" (majority class)'], ncol=1, y=0.0)
    fig.tight_layout()
    save_fig('ch15_accuracy')


def fig_agreement():
    R = RES['texts']['agree']
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    x = np.arange(len(M.AGREE))
    for k, (m, c) in enumerate((('LM', Orange), ('FinBERT', MainBlue), ('Qwen 7B', IDAred), ('Qwen 14B', '#7A0000'))):
        ax.bar(x + (k - 1.5) * 0.2, [100 * R[l][m] for l in M.AGREE], 0.2, color=c, label=m)
    n = RES['texts']['agree_n']
    ax.set_xticks(x)
    rng = {'50Agree': '50% to <66%', '66Agree': '66% to <75%', '75Agree': '75% to <100%', 'AllAgree': '100%'}
    ax.set_xticklabels([f'{rng[l]}\n(n = {n[l]:,})' for l in M.AGREE], fontsize=8)
    ax.set_xlabel("Share of each sentence's annotators (5-8 per sentence) who agree on the label")
    ax.set_ylabel('Accuracy (%)')
    ax.set_ylim(0, 100)
    legend_outside_bottom(ax, ncol=4, y=-0.32)
    save_fig('ch15_agreement')


def fig_confusion(tw):
    fig, axes = plt.subplots(1, 3, figsize=(7.8, 2.8))
    pr = predictions(tw)
    for ax, m in zip(axes, ('LM', 'FinBERT', 'Qwen 7B')):
        cm = M.confusion(tw['label'], pr[m]).values
        share = cm / cm.sum(1, keepdims=True)
        ax.imshow(share, cmap='Blues', vmin=0, vmax=1)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f'{cm[i, j]}', ha='center', va='center', fontsize=8,
                        color='white' if share[i, j] > 0.55 else 'black')
        ax.set_xticks(range(3))
        ax.set_xticklabels(['neg', 'neu', 'pos'])
        ax.set_yticks(range(3))
        ax.set_yticklabels(['neg', 'neu', 'pos'])
        ax.set_title(f'{m}: acc. {100 * M.acc(tw["label"], pr[m]):.1f}%', fontsize=8.5)
        ax.set_xlabel('Predicted')
    axes[0].set_ylabel('True label')
    fig.tight_layout()
    save_fig('ch15_confusion')


def fig_llm_size():
    R = RES['texts']
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    xs = list(SIZES_B.values())
    for key, c, lab in (('pb', MainBlue, 'Financial PhraseBank'), ('tw', IDAred, 'Twitter Financial News')):
        ax.plot(xs, [100 * R[key][f'Qwen {s}']['f1'] for s in SIZES_B], 'o-', color=c, label=f'Qwen2.5, {lab}')
        ax.axhline(100 * R[key]['FinBERT']['f1'], color=c, ls=':', lw=1, label=f'FinBERT, {lab}')
    ax.set_xscale('log')
    ax.set_xticks(xs)
    ax.set_xticklabels([f'{s}' for s in SIZES_B])
    ax.set_xlabel('Parameters (billions, log scale)')
    ax.set_ylabel('Macro-F1 (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch15_llm_size')


def fig_prompts():
    R = RES['texts']['prompts']
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    x = np.arange(3)
    for k, (p, c) in enumerate((('P1', MainBlue), ('P2', Teal), ('P3', Purple))):
        ax.bar(x + (k - 1) * 0.26, [100 * R[s][p]['acc'] for s in ('1.5B', '7B', '14B')], 0.26, color=c,
               label={'P1': 'P1: "classify the sentiment ... for investors"',
                      'P2': 'P2: "good, bad or neutral for the stock price"',
                      'P3': 'P3: "what is the sentiment of this text"'}[p])
    ax.set_xticks(x)
    ax.set_xticklabels(['Qwen2.5-1.5B', 'Qwen2.5-7B', 'Qwen2.5-14B'])
    ax.set_ylabel('Accuracy on Twitter Financial News (%)')
    ax.set_ylim(0, 100)
    legend_outside_bottom(ax, ncol=1, y=-0.14)
    save_fig('ch15_prompts')


def fig_embeddings(tw):
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    for l in ('neutral', 'positive', 'negative'):
        q = tw[tw['label'] == l]
        ax.scatter(q['pc1'], q['pc2'], s=5, alpha=0.55, color=LAB_COL[l], label=f'{l} ({len(q):,})', lw=0)
    ax.set_xlabel('First principal component')
    ax.set_ylabel('Second principal component')
    legend_outside_bottom(ax, ncol=3, y=-0.18, markerscale=3)
    save_fig('ch15_embeddings')


def fig_learning_curve():
    lc = load_csv('ch15_learning_curve.csv')
    grp = lc.groupby('n')
    m, s = grp.mean(), grp.std().fillna(0)
    R = RES['texts']['tw']
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    for k, c, lab in (('emb', Magenta, 'MiniLM embeddings + logistic regression'),
                      ('tfidf', Teal, 'TF-IDF (words and word pairs) + logistic regression')):
        ax.plot(m.index, 100 * m[f'{k}_acc'], 'o-', color=c, label=lab, ms=4)
        ax.fill_between(m.index, 100 * (m[f'{k}_acc'] - 2 * s[f'{k}_acc']), 100 * (m[f'{k}_acc'] + 2 * s[f'{k}_acc']),
                        color=c, alpha=0.15, lw=0)
    for mm, c, ls in (('FinBERT', MainBlue, '--'), ('Qwen 7B', IDAred, ':')):
        ax.axhline(100 * R[mm]['acc'], color=c, ls=ls, lw=1.1, label=f'{mm}, no Twitter labels used')
    ax.set_xscale('log')
    ax.set_xlabel('Labelled training examples (log scale)')
    ax.set_ylabel('Accuracy on the validation set (%)')
    legend_outside_bottom(ax, ncol=2, y=-0.22)
    save_fig('ch15_learning_curve')


# =============================================================================
# MEMORAREA TRECUTULUI (LOOK-AHEAD)
# =============================================================================
def auc(p, up):
    p, up = np.asarray(p), np.asarray(up, bool)
    return float(stats_auc(p[up], p[~up]))


def stats_auc(a, b):
    from scipy.stats import mannwhitneyu
    if len(a) == 0 or len(b) == 0:
        return np.nan
    return mannwhitneyu(a, b).statistic / (len(a) * len(b))


def boot_auc(p, up, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    p, up = np.asarray(p), np.asarray(up, bool)
    v = []
    for _ in range(B):
        i = rng.integers(0, len(p), len(p))
        if up[i].all() or (~up[i]).all():
            continue
        v.append(stats_auc(p[i][up[i]], p[i][~up[i]]))
    return tuple(np.quantile(v, [0.025, 0.975]))


def eval_memory():
    mm = load_csv('ch15_memory_monthly.csv', index_col=0, parse_dates=True)
    md = load_csv('ch15_memory_daily.csv', index_col=0, parse_dates=True)
    R = {}
    for name, d, cut_pre, cut_post in (('monthly', mm, '2024-08-31', '2024-10-01'),
                                       ('daily', md, '2023-12-31', '2024-10-01')):
        up = d['ret'] > 0
        R[name] = {}
        for s in ('1.5B', '7B', '14B'):
            col = f'qwen{s}'
            r = {}
            for per, sel in (('pre', d.index <= cut_pre), ('post', d.index >= cut_post)):
                p, u = d.loc[sel, col].values, up[sel].values
                lo, hi = boot_auc(p, u)
                ba = 0.5 * (np.mean(p[u] > 0.5) + np.mean(p[~u] <= 0.5))
                r[per] = {'auc': auc(p, u), 'lo': lo, 'hi': hi, 'ba': float(ba), 'n': int(sel.sum()),
                          'n_up': int(u.sum()), 'p_rise': float(np.mean(p > 0.5))}
            R[name][s] = r
    # lunile cele mai cunoscute
    pre = mm.loc[:'2024-08-31']
    worst = pre.nsmallest(8, 'ret')
    R['worst'] = {d.strftime('%Y-%m'): {'ret': float(r['ret']), 'p14': float(r['qwen14B'])} for d, r in worst.iterrows()}
    R['range'] = {'m_start': mm.index[0].strftime('%Y-%m'), 'm_end': mm.index[-1].strftime('%Y-%m'),
                  'd_pre_start': md.index[0].strftime('%Y-%m-%d')}
    RES['memory'] = R
    return mm, md


def fig_memory_timeline(mm):
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    up = mm['ret'] > 0
    ax.scatter(mm.index[up], mm.loc[up, 'qwen14B'], s=10, color=Forest, label='S&P 500 rose that month', lw=0)
    ax.scatter(mm.index[~up], mm.loc[~up, 'qwen14B'], s=10, color=IDAred, label='S&P 500 fell that month', lw=0)
    ax.axvline(pd.Timestamp(M.QWEN_RELEASE), color=Gray, ls='--', lw=0.9)
    ax.text(pd.Timestamp(M.QWEN_RELEASE), 1.04, ' weights released', fontsize=7.5, color='black', va='bottom')
    ax.set_ylabel('Qwen2.5-14B: P("rise")')
    ax.set_ylim(-0.04, 1.12)
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    legend_outside_bottom(ax, ncol=2, y=-0.16, markerscale=2)
    save_fig('ch15_memory_timeline')


def fig_memory_auc():
    R = RES['memory']
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
    for ax, name, title in zip(axes, ('monthly', 'daily'), ('S&P 500, direction of each month',
                                                             'Apple, direction of single days')):
        x = np.arange(3)
        for k, (per, c, lab) in enumerate((('pre', MainBlue, 'Before the weights were released'),
                                          ('post', Orange, 'After the release (the model cannot know)'))):
            vals = [R[name][s][per] for s in ('1.5B', '7B', '14B')]
            ax.errorbar(x + (k - 0.5) * 0.22, [v['auc'] for v in vals],
                        yerr=[[v['auc'] - v['lo'] for v in vals], [v['hi'] - v['auc'] for v in vals]],
                        fmt='o', color=c, capsize=2, ms=5, label=lab)
        ax.axhline(0.5, color=Gray, ls='--', lw=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(['1.5B', '7B', '14B'])
        ax.set_title(title, fontsize=8.5, loc='left')
        ax.set_xlabel('Qwen2.5 model size')
    axes[0].set_ylabel('AUC: rises vs falls (95% CI)')
    h, l = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    fig_legend_bottom(fig, h, l, ncol=2, y=0.0)
    save_fig('ch15_memory_auc')


# =============================================================================
# DE LA SENTIMENT LA SEMNAL (FNSPID)
# =============================================================================
def news_panel():
    daily = load_csv('ch15_news_daily.csv', parse_dates=['day']).set_index(['day', 'ticker'])
    syms = sorted(set(M.TICKERS.values()))
    rets = M.stock_returns(syms + ['SPY.US'], start='2009-01-01')
    rets.columns = [c.replace('.US', '') for c in rets.columns]
    rets = rets.loc[:'2023-12-31']
    P = M.daily_panel(daily, rets)
    for c in SCORE_LBL:
        P[f'z_{c}'] = (P[c] - P[c].mean()) / P[c].std()
    return P, rets


def event_groups(x):
    """Grupurile studiului de eveniment: tercila cea mai negativa si cea mai pozitiva a scorului zilnic. Daca cele
    doua praguri coincid (tonul LM este exact 0 in aproape jumatate din zilele-actiune), grupurile disjuncte sunt
    scor < prag si scor > prag, iar zilele egale cu pragul sunt excluse."""
    q1, q2 = x.quantile([1 / 3, 2 / 3])
    if q1 >= q2:
        return x < q1, x > q2
    return x <= q1, x >= q2


def eval_news(P, rets):
    cnt = load_csv('ch15_news_counts.csv', index_col=0)
    hl = load_csv('ch15_news_headlines.csv.gz', usecols=['finbert', 'lm', 'lm_hit', 'qwen', 'finbert_lab'])
    R = {'n_headlines': int(cnt.values.sum()), 'n_tickers': int((cnt.sum() > 0).sum()),
         'n_obs': len(P), 'n_days': int(P.index.get_level_values('day').nunique()),
         'first': str(P.index.get_level_values('day').min().date()),
         'last': str(P.index.get_level_values('day').max().date()),
         'per_year': cnt.sum(1).to_dict(), 'per_ticker': cnt.sum().sort_values(ascending=False).to_dict(),
         'mean_n': float(P['n'].mean()), 'lm_hit': float(hl['lm_hit'].mean()),
         'fb_share': (hl['finbert_lab'].value_counts(normalize=True).sort_index()).tolist(),
         'corr': hl[['lm', 'finbert', 'qwen']].corr().round(3).to_dict(),
         'corr_daily': P[['lm', 'finbert', 'qwen']].corr().round(3).to_dict()}
    R['reg'] = {}
    groups = P.index.get_level_values('day')
    for c in SCORE_LBL:
        for y in ('r0', 'r1', 'r2'):
            R['reg'][f'{c}|{y}'] = {k: float(v) for k, v in M.cluster_ols(P[y].values, P[f'z_{c}'].values,
                                                                           groups).items()}
    # studiul de eveniment: tercilele scorului FinBERT
    cols = EVENT_COLS
    R['event'] = {}
    for c in ('finbert', 'qwen', 'lm'):
        neg, pos = event_groups(P[c])
        ev = {}
        for grp, sel in (('neg', neg), ('pos', pos)):
            X = P.loc[sel, cols].groupby(level='day').mean()
            car = X.fillna(0).cumsum(axis=1)
            ev[grp] = {'car': car.mean().tolist(), 'se': (car.std() / np.sqrt(len(car))).tolist(), 'n_days': len(X),
                       'n': int(sel.sum())}
        R['event'][c] = ev
    # strategia
    days = rets.index[(rets.index >= P.index.get_level_values('day').min())]
    R['strat'] = {}
    for c in SCORE_LBL:
        St = M.signal_portfolio(P, c, days, cost_bp=5, ret='r2')
        S1 = M.signal_portfolio(P, c, days, ret='r1')
        m1, t1 = M.nw_t(S1['gross'])
        mu, t = M.nw_t(St['gross'])
        lo, hi = M.block_boot_mean(St['gross'].values)
        mun, tn = M.nw_t(St['net'])
        active = St['k'] > 0
        R['strat'][c] = {'mean_bp': 1e2 * mu, 't': t, 'lo_bp': 1e2 * lo, 'hi_bp': 1e2 * hi,
                         'sr': M.sharpe(St['gross']), 'sr_net': M.sharpe(St['net']), 't_net': tn,
                         'mean_net_bp': 1e2 * mun, 'active': float(active.mean()),
                         'mean_active_bp': 1e2 * St.loc[active, 'gross'].mean(),
                         'breakeven_bp': 1e2 * St.loc[active, 'gross'].mean() / 4,
                         'r1_mean_bp': 1e2 * m1, 'r1_t': t1, 'r1_sr': M.sharpe(S1['gross']),
                         'years': {}}
        for a, b in PERIODS:
            x = St.loc[a:b, 'gross']
            m_, t_ = M.nw_t(x)
            R['strat'][c]['years'][f'{a}-{b}'] = {'mean_bp': 1e2 * m_, 't': t_}
        R['strat'][c]['cum'] = St[['gross', 'net']]
    RES['news'] = R
    return P


def fig_news_coverage():
    cnt = load_csv('ch15_news_counts.csv', index_col=0)
    tot = cnt.sum(1)
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.bar(tot.index.astype(int), tot.values / 1e3, color=MainBlue, width=0.75, label='Headlines about the stocks studied')
    ax.set_ylabel('Headlines (thousands)')
    ax.set_xlabel('Year (trading day the headline is assigned to)')
    legend_outside_bottom(ax, ncol=1, y=-0.28)
    save_fig('ch15_news_coverage')


def fig_news_hours():
    h = load_csv('ch15_news_hours.csv', index_col=0)
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    ax.bar(h.index, h['n'], color=[IDAred if x == 0 else MainBlue for x in h.index], width=0.8)
    ax.set_yscale('log')
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel('Hour of the timestamp (UTC)')
    ax.set_ylabel('Headlines (log scale)')
    h1 = [plt.Rectangle((0, 0), 1, 1, color=IDAred), plt.Rectangle((0, 0), 1, 1, color=MainBlue)]
    ax.legend(h1, [f'00:00 UTC: {100 * h["share_midnight"].iloc[0]:.1f}% of headlines stamped exactly at midnight',
                   'Other hours'], loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=1, frameon=False)
    RES.setdefault('news', {})['midnight'] = float(h['share_midnight'].iloc[0])
    save_fig('ch15_news_hours')


def fig_contemp_next():
    R = RES['news']['reg']
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    x = np.arange(len(SCORE_LBL))
    for k, (y, c, lab) in enumerate((('r0', MainBlue, 'Day of the news (d)'),
                                     ('r1', Amber, 'Day d+1 (news may still be arriving)'),
                                     ('r2', IDAred, 'Day d+2 (tradable forecast)'))):
        b = [100 * R[f'{s}|{y}']['b'] for s in SCORE_LBL]
        e = [1.96 * 100 * R[f'{s}|{y}']['se_cl'] for s in SCORE_LBL]
        ax.errorbar(x + (k - 1) * 0.22, b, yerr=e, fmt='o', color=c, capsize=3, ms=5, label=lab)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([SCORE_LBL[s] for s in SCORE_LBL])
    ax.set_ylabel('Excess return per 1 s.d. of score (bp)')
    legend_outside_bottom(ax, ncol=2, y=-0.16)
    save_fig('ch15_contemp_next')


def fig_event_study():
    R = RES['news']['event']['finbert']
    k = np.arange(-5, 6)
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    for grp, c, lab in (('pos', Forest, 'Most positive third of news days (FinBERT)'),
                        ('neg', IDAred, 'Most negative third of news days (FinBERT)')):
        car, se = np.array(R[grp]['car']), np.array(R[grp]['se'])
        ax.plot(k, car, 'o-', color=c, label=lab, ms=4)
        ax.fill_between(k, car - 1.96 * se, car + 1.96 * se, color=c, alpha=0.15, lw=0)
    ax.axvline(0, color=Gray, ls='--', lw=0.8)
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(k)
    ax.axvspan(1.5, 5.4, color=LightGray, alpha=0.4, lw=0)
    ax.set_xlabel('Trading days relative to the date of the headline (0)')
    ax.set_ylabel('Cumulative excess return vs SPY (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch15_event_study')


def fig_strategy():
    R = RES['news']['strat']
    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    for c in SCORE_LBL:
        St = R[c]['cum']
        ax.plot(St.index, St['gross'].cumsum(), color=SCORE_COL[c], lw=1.1, label=f'{SCORE_LBL[c]}, before costs')
        ax.plot(St.index, St['net'].cumsum(), color=SCORE_COL[c], lw=0.9, ls='--', label=f'{SCORE_LBL[c]}, 5 bp per trade')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_ylabel('Cumulative d+2 return (%, sum)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch15_strategy')


def fig_subperiods():
    R = RES['news']['strat']
    per = list(R['finbert']['years'])
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    x = np.arange(len(per))
    for k, c in enumerate(SCORE_LBL):
        ax.bar(x + (k - 1) * 0.26, [R[c]['years'][p]['mean_bp'] for p in per], 0.26, color=SCORE_COL[c],
               label=SCORE_LBL[c])
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(per)
    ax.set_ylabel('Mean daily return, before costs (bp)')
    legend_outside_bottom(ax, ncol=3, y=-0.16)
    save_fig('ch15_subperiods')


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items() if not isinstance(v, pd.DataFrame)}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


if __name__ == '__main__':
    print('Chapter 15 charts')
    fig_dict_words()
    pb, tw = eval_texts()
    fig_accuracy()
    fig_agreement()
    fig_confusion(tw)
    fig_llm_size()
    fig_prompts()
    fig_embeddings(tw)
    fig_learning_curve()
    mm, md = eval_memory()
    fig_memory_timeline(mm)
    fig_memory_auc()
    P, rets = news_panel()
    eval_news(P, rets)
    fig_news_coverage()
    fig_news_hours()
    fig_contemp_next()
    fig_event_study()
    fig_strategy()
    fig_subperiods()
    with open(os.path.join(HERE, 'ch15_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1, default=float)
    print('saved ch15_results.json')

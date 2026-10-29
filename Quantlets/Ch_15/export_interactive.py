"""Export the inputs of the Chapter 15 interactive page (MFM/interactive/ch15_data.js).

Uses the functions and the saved outputs of generate_all_charts.py, mfm_text.py, valid_inference.py and
ai_discovery_case.py, so the page starts from the same numbers as the slides. No language model is run: the scores
of the dictionaries, FinBERT, the Qwen2.5 models, MiniLM and TF-IDF are the chapter's saved tables (ch15_*.csv),
and the evaluation results come from ch15_results.json and ch15_inference.json. save_fig is replaced by a no-op,
so no chart or results file of the chapter is rewritten. Market data: the local files in data/market (EODHD).
The PhraseBank sentences (only for the word counts of the dictionary slide) are read with the chapter's own loader
(mfm_text.load_phrasebank, public Hugging Face file, no key).

The panel of the 18,282 stock-days (scores, number of headlines, excess returns on days d ... d+5) is stored as
base64-encoded little-endian integer arrays: the scores x 10^6 as 24-bit integers (exact: ch15_news_daily.csv has six
decimals), the returns of days d, d+1 and d+2 in units of 0.01 basis point (24-bit), those of days d+3 ... d+5 in
units of 0.1 basis point (16-bit; the few returns beyond that range are listed separately, unrounded).
"""
import base64
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_all_charts as g      # noqa: E402
import mfm_text as M                 # noqa: E402
import ai_discovery_case as A        # noqa: E402

g.save_fig = lambda name: g.plt.close()

OUT = os.path.join(HERE, '..', '..', 'interactive', 'ch15_data.js')
LAB = {'negative': '0', 'neutral': '1', 'positive': '2'}


def r(x, d=6):
    return [None if not np.isfinite(v) else float(v) for v in np.round(np.asarray(x, float), d)]


def b64(a, dtype):
    a = np.asarray(a)
    info = np.iinfo(dtype)
    assert a.min() >= info.min and a.max() <= info.max, (dtype, a.min(), a.max())
    return base64.b64encode(a.astype(np.dtype(dtype).newbyteorder('<')).tobytes()).decode('ascii')


def b64_24(a):
    """Signed 24-bit little-endian integers, base64."""
    a = np.asarray(a, np.int64)
    assert np.abs(a).max() < 2 ** 23
    return base64.b64encode(a.astype('<i4').view(np.uint8).reshape(-1, 4)[:, :3].tobytes()).decode('ascii')


def enc_score(x):
    """Scores x 10^6 as integers (exact for the six-decimal scores of ch15_news_daily.csv)."""
    x = np.asarray(x, float)
    q = np.round(x * 1e6)
    assert np.abs(q / 1e6 - x).max() < 1e-12
    return q.astype(np.int64)


def labels(a):
    return ''.join(LAB[v] for v in a)


def word_counts(pb, D, only, top=30):
    """Sentences of PhraseBank that contain each word of a list, by human label (as in fig_dict_words)."""
    rows = {}
    for t, l in zip(pb['text'], pb['label']):
        for w in set(M.tokens(t)):
            if w in only:
                rows.setdefault(w, {'negative': 0, 'neutral': 0, 'positive': 0})[l] += 1
    f = pd.DataFrame(rows).T
    f['n'] = f.sum(1)
    f = f.sort_values('n', ascending=False).head(top)
    # sentences whose only words of the first list are missing from the second (the 964 of the slide)
    sel = [any(w in only for w in M.tokens(t)) for t in pb['text']]
    return f, sel


def main():
    res = json.load(open(os.path.join(HERE, 'ch15_results.json')))
    inf = json.load(open(os.path.join(HERE, 'ch15_inference.json')))
    case = json.load(open(os.path.join(HERE, 'ai_discovery_case.json')))
    d = {}

    # 1. dictionaries: words negative in one list and not in the other, counted in PhraseBank sentences
    pb_txt = M.load_phrasebank()
    D = M.load_dictionaries()
    gi_only, lm_only = D['GI_neg'] - D['LM_neg'], D['LM_neg'] - D['GI_neg']
    f, _ = word_counts(pb_txt, D, gi_only)
    top = res['dict']['top']
    assert {w: int(n) for w, n in f['n'].head(14).items()} == top, 'word counts differ from the slide'
    for w, v in res['dict']['top_nonneg'].items():
        assert abs(1 - f.loc[w, 'negative'] / f.loc[w, 'n'] - v) < 1e-12
    f2, _ = word_counts(pb_txt, D, lm_only)
    tok = [set(M.tokens(t)) for t in pb_txt['text']]
    only_gi = [bool(s & gi_only) and not (s & D['LM_neg']) for s in tok]
    only_lm = [bool(s & lm_only) and not (s & D['GI_neg']) for s in tok]
    assert sum(only_gi) == res['dict']['sent_only']
    lab = pb_txt['label'].values
    d['dict'] = {k: dict(words=[w.lower() for w in ff.index], pos=ff['positive'].astype(int).tolist(),
                         neu=ff['neutral'].astype(int).tolist(), neg=ff['negative'].astype(int).tolist(),
                         n_list=len(s), n_sent=int(sum(o)), nonneg=float(np.mean(lab[np.array(o)] != 'negative')))
                 for k, ff, s, o in (('gi', f, gi_only, only_gi), ('lm', f2, lm_only, only_lm))}
    d['dict']['res'] = {k: res['dict'][k] for k in ('n_lm_neg', 'n_lm_pos', 'n_gi_neg', 'n_gi_pos', 'n_only', 'sent_only',
                                                     'sent_only_nonneg')}

    # 2. labelled texts: true labels and the label predicted by each method (generate_all_charts.predictions)
    pb, tw = g.load_csv('ch15_phrasebank_scores.csv'), g.load_csv('ch15_twitter_scores.csv')
    T = {}
    for name, df in (('pb', pb), ('tw', tw)):
        pr = g.predictions(df)
        T[name] = dict(y=labels(df['label']), pred={m: labels(pr[m]) for m in g.METHODS})
    T['pb']['agree'] = ''.join(str(M.AGREE.index(a)) for a in pb['agree'])
    for s in ('1.5B', '7B', '14B'):
        for p in ('P2', 'P3'):
            T['tw']['pred'][f'Qwen {s} {p}'] = labels(M.probs_label(tw[[f'qwen{s}_{p}_{l}' for l in M.LABELS]].values))
    T['methods'] = g.METHODS
    T['colors'] = g.M_COL
    T['res'] = {k: {m: {q: v for q, v in res['texts'][k][m].items() if q != 'cm'} for m in g.METHODS} for k in ('pb', 'tw')}
    T['share'] = {k: res['texts'][k]['share'] for k in ('pb', 'tw')}
    T['pairs'] = res['texts']['pairs']
    T['prompts'] = res['texts']['prompts']
    d['texts'] = T

    # 3. embeddings: first two principal components of the MiniLM vectors (Twitter validation set)
    d['emb'] = dict(pc1=b64(np.round(tw['pc1'].values * 1e4), 'int16'), pc2=b64(np.round(tw['pc2'].values * 1e4), 'int16'),
                    acc_lr=res['texts']['tw']['MiniLM + LR']['acc'])

    # 4. learning curve
    lc = g.load_csv('ch15_learning_curve.csv')
    ns = sorted(lc['n'].unique())
    d['lc'] = dict(n=[int(n) for n in ns], emb=[r(lc.loc[lc.n == n, 'emb_acc']) for n in ns],
                   tfidf=[r(lc.loc[lc.n == n, 'tfidf_acc']) for n in ns],
                   finbert=res['texts']['tw']['FinBERT']['acc'], qwen7=res['texts']['tw']['Qwen 7B']['acc'])

    # 5. memory: P(rise) of the three Qwen2.5 models for the S&P 500 months and the Apple days
    mm = g.load_csv('ch15_memory_monthly.csv', index_col=0, parse_dates=True)
    md = g.load_csv('ch15_memory_daily.csv', index_col=0, parse_dates=True)
    d['mem'] = {name: dict(dates=[f'{t:%Y-%m-%d}' for t in df.index], up=''.join('1' if v > 0 else '0' for v in df['ret']),
                           p={s: df[f'qwen{s}'].tolist() for s in ('1.5B', '7B', '14B')}, cut_pre=cp, cut_post=cq)
                for name, df, cp, cq in (('monthly', mm, '2024-08-31', '2024-10-01'), ('daily', md, '2023-12-31', '2024-10-01'))}
    d['mem']['res'] = {k: res['memory'][k] for k in ('monthly', 'daily')}
    d['mem']['release'] = M.QWEN_RELEASE
    d['mem']['test'] = inf['auc']

    # 6. hours of the FNSPID timestamps
    h = g.load_csv('ch15_news_hours.csv', index_col=0)
    d['hours'] = dict(n=h['n'].astype(int).tolist(), midnight=float(h['share_midnight'].iloc[0]))

    # 7. the panel of stock-days (generate_all_charts.news_panel) and the trading days of the strategy
    P, rets = g.news_panel()
    days = rets.index[rets.index >= P.index.get_level_values('day').min()]
    tickers = sorted(P.index.get_level_values('ticker').unique())
    di = days.get_indexer(P.index.get_level_values('day'))
    assert (di >= 0).all()
    RCOL = ['r0', 'r1', 'r2', 'rp3', 'rp4', 'rp5']
    assert not P[RCOL].isna().any().any()
    pan = dict(n_obs=len(P), day=b64(di, 'int16'), tic=b64(pd.Index(tickers).get_indexer(P.index.get_level_values('ticker')), 'uint8'),
               n=b64(P['n'].values, 'uint8'), tickers=tickers)
    for c in ('lm', 'finbert', 'qwen'):
        pan[c] = b64_24(enc_score(P[c].values))
    pan['big'] = {}
    for c in RCOL[:3]:                 # returns of d, d+1, d+2 in units of 0.01 bp
        pan[c] = b64_24(np.round(P[c].values * 1e4))
    for c in RCOL[3:]:                 # returns of d+3 ... d+5 in units of 0.1 bp; the few beyond the int16 range apart
        q = np.round(P[c].values * 1000)
        big = np.abs(q) > 32767
        pan['big'][c] = [[int(i), float(P[c].values[i])] for i in np.where(big)[0]]
        q[big] = 0
        pan[c] = b64(q, 'int16')
    off = (days - days[0]).days
    pan['days'] = dict(start=f'{days[0]:%Y-%m-%d}', off=b64(off.values, 'int16'))
    d['panel'] = pan
    N = res['news']
    d['news'] = {k: N[k] for k in ('n_headlines', 'n_tickers', 'n_obs', 'n_days', 'first', 'last', 'mean_n', 'midnight')}
    d['news']['reg'] = N['reg']
    d['news']['strat'] = {c: {k: v for k, v in s.items() if k != 'years'} for c, s in N['strat'].items()}
    d['news']['panel'] = inf['panel']

    # 8. PPI: human labels and the net scores of FinBERT and Qwen2.5-7B on the Twitter validation headlines
    d['ppi'] = dict(res=inf['ppi'], f_finbert=b64(np.round((tw['finbert_positive'] - tw['finbert_negative']).values * 1e4), 'int16'),
                    f_qwen=b64(np.round((tw['qwen7B_positive'] - tw['qwen7B_negative']).values * 1e4), 'int16'))

    # 9. Lopez-Lira and Tang (2026), Table 5, as drawn in the lecture
    d['llt'] = dict(models=list(g.LLT_TABLE5), hit_r=[v[0] for v in g.LLT_TABLE5.values()], hit_d=[v[1] for v in g.LLT_TABLE5.values()],
                    sr=[v[2] for v in g.LLT_TABLE5.values()], mu=[v[3] for v in g.LLT_TABLE5.values()])

    # 10. specification curve: the 36 strategies of the mini-case and the sign-flip test of valid_inference.py
    d['spec'] = {k: inf['spec'][k] for k in ('t', 'meta', 'n_pos_sig', 'median_t', 'p_count', 'p_median', 'n_neg_sig', 'B', 'block')}
    d['spec']['bands'] = list(A.BANDS)
    d['spec']['hold'] = A.HOLD
    d['spec']['case'] = {k: case[k] for k in ('n_variants', 'base_mean_bp', 'base_t', 'n_sig', 'n_sig_pos', 'expected_false', 'n_holm',
                                              'n_bh', 'n_t3', 'bonf_crit')}

    with open(OUT, 'w') as fo:
        fo.write('// Inputs of the Chapter 15 interactive page, exported by Quantlets/Ch_15/export_interactive.py.\n')
        fo.write('window.CH15_DATA = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

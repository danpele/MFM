"""
c3_score.py -- Seminarul 15, C3: titlurile FNSPID evaluate cu prompt-ul Lopez-Lira & Tang (2026, sectiunea 5)
============================================================================================================
Pasul 1 (headlines): titlurile FNSPID (Dong, Fan & Peng, 2024) pentru actiunile din mfm_text.TICKERS, aceleasi
  reguli ca run_scores.news_block (titlu identic, aceeasi actiune, aceeasi zi calendaristica -> o singura data;
  zile de tranzactionare de la 2009-06-01) -> ch15_c3_headlines.csv.gz (date, ticker, headline).
  Fisierele FNSPID (Stock_news/All_external.csv si nasdaq_exteral_data.csv de pe Hugging Face, Zihan1004/FNSPID)
  se dau prin FNSPID_FILES=cale1,cale2 (altfel se citesc direct de la URL-urile din mfm_text.FNSPID_URLS).
Pasul 2 (score): Qwen2.5-7B-Instruct, decodare greedy (temperatura 0), prompt-ul publicat cuvant cu cuvant;
  se pastreaza doar prima linie a raspunsului. Rezultatele se adauga incremental in ch15_c3_llt_raw.csv
  (reluarea continua de unde a ramas).

Rulare:  FNSPID_FILES=... python3 c3_score.py headlines
         python3 c3_score.py score [batch]
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import csv
import hashlib
import os
import re
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_text as M  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HEADLINES = os.path.join(HERE, 'ch15_c3_headlines.csv.gz')
RAW = os.path.join(HERE, 'ch15_c3_llt_raw.csv')
MODEL = 'Qwen/Qwen2.5-7B-Instruct'

# Lopez-Lira & Tang (2026), sectiunea 5: prompt-ul, cuvant cu cuvant
PROMPT = ('Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert '
          'with stock recommendation experience. Answer "YES" if good news, "NO" if bad news, or "UNKNOWN" if '
          'uncertain in the first line. Then elaborate with one short and concise sentence on the next line. Is '
          'this headline good or bad for the stock price of {company} in the short term?\nHeadline: {headline}')

NAMES = {'AAPL': 'Apple', 'MSFT': 'Microsoft', 'AMZN': 'Amazon', 'NVDA': 'NVIDIA', 'TSLA': 'Tesla',
         'JPM': 'JPMorgan Chase', 'BAC': 'Bank of America', 'C': 'Citigroup', 'GS': 'Goldman Sachs',
         'MS': 'Morgan Stanley', 'WFC': 'Wells Fargo', 'CSCO': 'Cisco', 'GME': 'GameStop',
         'MSTR': 'MicroStrategy', 'COIN': 'Coinbase'}


def company(ticker, date):
    """Numele firmei la data titlului (Google -> Alphabet la 2 octombrie 2015; Facebook -> Meta la 28 octombrie 2021)."""
    if ticker == 'GOOGL':
        return 'Alphabet' if date >= '2015-10-02' else 'Google'
    if ticker == 'META':
        return 'Meta Platforms' if date >= '2021-10-28' else 'Facebook'
    return NAMES[ticker]


def build_headlines():
    t0 = time.time()
    f = os.environ.get('FNSPID_FILES')
    news = M.load_fnspid(f.split(',') if f else None)
    rets = M.stock_returns(sorted(set(M.TICKERS.values())) + ['SPY.US'], start='2009-01-01')
    news['day'] = M.assign_trading_day(news['ts'], rets.index)
    news = news.dropna(subset=['day'])
    news = news[news['day'] >= '2009-06-01']
    out = pd.DataFrame({'date': news['ts'].dt.tz_convert('UTC').dt.strftime('%Y-%m-%d'),
                        'ticker': news['ticker'], 'headline': news['title']})
    out = out.sort_values(['date', 'ticker', 'headline']).reset_index(drop=True)
    out.to_csv(HEADLINES, index=False, compression='gzip')
    print(f'{len(out)} headlines, {out["ticker"].nunique()} stocks, {out["date"].min()} -- {out["date"].max()}, '
          f'{time.time() - t0:.0f}s')


def key(prompt):
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()


def prompts():
    h = pd.read_csv(HEADLINES, dtype=str, keep_default_na=False)
    h['company'] = [company(t, d) for t, d in zip(h['ticker'], h['date'])]
    h['prompt'] = [PROMPT.format(company=c, headline=x) for c, x in zip(h['company'], h['headline'])]
    h['key'] = h['prompt'].map(key)
    return h


LABEL_RE = re.compile(r'^\W*(YES|NO|UNKNOWN)\W*$')


def parse(first_line):
    """Eticheta din prima linie: YES -> 1, UNKNOWN -> 0, NO -> -1; orice alt format -> NaN (nevalid)."""
    m = LABEL_RE.match(str(first_line).strip())
    return {'YES': 1.0, 'UNKNOWN': 0.0, 'NO': -1.0}[m.group(1)] if m else np.nan


def score(batch=32, max_new=6, limit=None):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.manual_seed(0)
    h = prompts()
    todo = h.drop_duplicates('key')
    done = set(pd.read_csv(RAW, usecols=['key'])['key']) if os.path.exists(RAW) else set()
    todo = todo[~todo['key'].isin(done)]
    if limit:
        todo = todo.iloc[:int(limit)]
    print(f'{h["key"].nunique()} distinct prompts, {len(done)} cached, {len(todo)} to score', flush=True)
    if todo.empty:
        return
    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = 'left'
    dev = M.device()
    m = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16 if dev != 'cpu' else torch.float32)
    m = m.to(dev).eval()
    chat = [tok.apply_chat_template([{'role': 'user', 'content': p}], tokenize=False, add_generation_prompt=True)
            for p in todo['prompt']]
    lens = np.array([len(c) for c in chat])
    order = np.argsort(lens, kind='stable')            # lungimi apropiate in acelasi lot: mai putina completare
    keys = todo['key'].values
    new = not os.path.exists(RAW)
    t0, n = time.time(), 0
    with open(RAW, 'a', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['key', 'first_line', 'complete'])
        for i in range(0, len(order), batch):
            idx = order[i:i + batch]
            b = tok([chat[j] for j in idx], return_tensors='pt', padding=True).to(dev)
            with torch.no_grad():
                g = m.generate(**b, max_new_tokens=max_new, do_sample=False, temperature=None, top_p=None,
                               top_k=None, pad_token_id=tok.eos_token_id)
            txt = tok.batch_decode(g[:, b['input_ids'].shape[1]:], skip_special_tokens=True)
            ended = (g[:, b['input_ids'].shape[1]:] == tok.eos_token_id).any(1).cpu().numpy()
            for j, t, e in zip(idx, txt, ended):
                complete = int('\n' in t or bool(e))
                w.writerow([keys[j], t.split('\n')[0].strip(), complete])
            f.flush()
            n += len(idx)
            if (i // batch) % 50 == 0:
                el = time.time() - t0
                print(f'{n}/{len(order)} scored, {n / el:.1f} per s, ETA {(len(order) - n) / (n / el) / 60:.0f} min',
                      flush=True)
    print(f'done: {n} in {(time.time() - t0) / 60:.1f} min', flush=True)


def rescore_incomplete(max_new=48, batch=16):
    """Raspunsurile a caror prima linie nu s-a incheiat in max_new jetoane si nu se pot citi: generare mai lunga."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    raw = pd.read_csv(RAW, dtype={'first_line': str}, keep_default_na=False)
    bad = raw[(raw['complete'] == 0) & raw['first_line'].map(parse).isna()]
    print(f'{len(bad)} incomplete first lines', flush=True)
    if bad.empty:
        return
    h = prompts().drop_duplicates('key').set_index('key')
    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = 'left'
    dev = M.device()
    m = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16).to(dev).eval()
    upd = {}
    ks = bad['key'].tolist()
    for i in range(0, len(ks), batch):
        kk = ks[i:i + batch]
        chat = [tok.apply_chat_template([{'role': 'user', 'content': h.loc[k, 'prompt']}], tokenize=False,
                                        add_generation_prompt=True) for k in kk]
        b = tok(chat, return_tensors='pt', padding=True).to(dev)
        with torch.no_grad():
            g = m.generate(**b, max_new_tokens=max_new, do_sample=False, temperature=None, top_p=None, top_k=None,
                           pad_token_id=tok.eos_token_id)
        for k, t in zip(kk, tok.batch_decode(g[:, b['input_ids'].shape[1]:], skip_special_tokens=True)):
            upd[k] = t.split('\n')[0].strip()
    raw.loc[raw['key'].isin(upd), 'first_line'] = raw['key'].map(upd)
    raw.loc[raw['key'].isin(upd), 'complete'] = 1
    raw.to_csv(RAW, index=False)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'score'
    if cmd == 'headlines':
        build_headlines()
    elif cmd == 'score':
        score(batch=int(sys.argv[2]) if len(sys.argv) > 2 else 32,
              limit=sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == 'rescore':
        rescore_incomplete()

"""
c3_reference.py -- Seminarul 15, C3: analiza de referinta pentru replicarea Lopez-Lira & Tang (2026) pe FNSPID
============================================================================================================
Intrari: ch15_c3_headlines.csv.gz (date, ticker, headline) si ch15_c3_llt_raw.csv (prima linie a raspunsului
Qwen2.5-7B-Instruct la prompt-ul publicat), ambele produse de c3_score.py; preturile ajustate din data/market.
Conventiile (slide-ul C3 2/3):
  * scor YES = 1, UNKNOWN = 0, NO = -1 (prima linie); scorul zilei-actiune = media scorurilor titlurilor
  * ziua d = prima zi de tranzactionare la data titlului sau dupa; castigul = randamentul brut din d + 2
  * long = media cu ponderi egale a actiunilor cu s > 0, short = la fel pentru s < 0, fiecare cu cel putin doua
    actiuni; long-short = long - short; o singura componenta calificata -> doar aceasta; altfel 0
  * toate zilele de tranzactionare ale esantionului (ca in C1); media, t Newey-West, Sharpe pe toate zilele;
    rata de succes pe zilele cu pozitii
  * cost c bp pe tranzactie dus-intors pe unitatea de valoare nominala: c x expunerea bruta (2 sau 1), plus c pe
    valoarea nominala neta SPY in varianta acoperita
  * ec. (1) la nivel de titlu: r_{i,d+h} (%, brut) pe scor, efecte fixe de actiune si de data, h = 0, 2; SE grupate
    pe date si pe actiuni (Cameron, Gelbach & Miller, 2011) si wild cluster bootstrap pe actiuni cu modelul nul
    cu ambele efecte fixe (ponderi Rademacher, 9 999 extrageri)
Rezultat: cheia 'c3' din sem15_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_text as M          # noqa: E402
import c3_score as C3         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
COSTS = (5, 10, 20)
PPY = 252


# =============================================================================
# DATE
# =============================================================================
def load():
    h = C3.prompts()
    raw = pd.read_csv(C3.RAW, dtype={'first_line': str}, keep_default_na=False).drop_duplicates('key', keep='last')
    h = h.merge(raw[['key', 'first_line']], on='key', how='left')
    h['s'] = h['first_line'].map(C3.parse)
    h['lab'] = h['first_line'].str.strip().str.extract(r'^\W*(YES|NO|UNKNOWN)\W*$')[0].fillna('invalid')
    syms = sorted(set(M.TICKERS.values()))
    rets = M.stock_returns(syms + ['SPY.US'], start='2009-01-01')
    rets.columns = [c.replace('.US', '') for c in rets.columns]
    rets = rets.loc[:'2023-12-31']                 # acelasi calendar ca in C1 (generate_all_charts.news_panel)
    h['day'] = M.assign_trading_day(pd.to_datetime(h['date'], utc=True), rets.index)
    return h, rets


# =============================================================================
# PORTOFOLIUL ZILNIC (tabelul 1 din lucrare)
# =============================================================================
def portfolio(daily, rets, days, lag=2):
    """daily: scorul mediu pe (day, ticker). Castigul se inregistreaza in ziua d + lag."""
    pos = pd.DatetimeIndex(days)
    idx = pos.get_indexer(daily.index.get_level_values('day'))
    ok = (idx >= 0) & (idx + lag < len(pos))
    d = daily[ok].copy()
    d['earn'] = pos[idx[ok] + lag]
    d['r'] = [rets.at[e, t] for e, t in zip(d['earn'], d.index.get_level_values('ticker'))]
    d = d.dropna(subset=['r'])
    L = d[d['s'] > 0].groupby('earn')['r'].agg(['mean', 'size'])
    S = d[d['s'] < 0].groupby('earn')['r'].agg(['mean', 'size'])
    L = L[L['size'] >= 2]['mean'].reindex(pos)
    S = S[S['size'] >= 2]['mean'].reindex(pos)
    spy = rets['SPY'].reindex(pos)
    hasL, hasS = L.notna(), S.notna()
    out = pd.DataFrame(index=pos)
    out['L'], out['S'] = L, S
    out['legs'] = hasL.astype(int) + hasS.astype(int)
    out['raw'] = np.where(hasL & hasS, L - S, np.where(hasL, L, np.where(hasS, -S, 0.0)))
    out['hedged'] = np.where(hasL & hasS, L - S, np.where(hasL, L - spy, np.where(hasS, spy - S, 0.0)))
    out['gross_exp'] = out['legs'].astype(float)
    out['spy_exp'] = (out['legs'] == 1).astype(float)
    return out


def stats(x, active):
    mu, t = M.nw_t(x)
    return {'mean_bp': 100 * mu, 't_nw': t, 'sr': M.sharpe(x, PPY),
            'hit': float((x[active] > 0).mean()), 'n_days': int(len(x)), 'n_active': int(active.sum())}


def c1_same_days(c1daily, keep, rets, days):
    """C1: sign(scorul net Qwen, prompt P1) in fiecare actiune cu stiri, acoperita cu SPY, ponderi egale, castigul din
    d + 2 -- pe zilele-actiune ale lui C3. Expunerea: 1 pe actiuni plus |media semnelor| pe SPY (valoarea neta)."""
    P = c1daily.loc[c1daily.index.intersection(keep)]
    P = P[P['qwen'].abs() > 0]
    pos = pd.DatetimeIndex(days)
    idx = pos.get_indexer(P.index.get_level_values('day'))
    ok = (idx >= 0) & (idx + 2 < len(pos))
    P = P[ok]
    earn = pos[idx[ok] + 2]
    tk = P.index.get_level_values('ticker')
    ex = np.array([rets.at[e, t] - rets.at[e, 'SPY'] for e, t in zip(earn, tk)])
    sg = np.sign(P['qwen'].values)
    df = pd.DataFrame({'x': sg * ex, 'sg': sg}, index=earn).dropna()
    g = df.groupby(level=0)
    R = pd.DataFrame({'gross': g['x'].mean(), 'spy': g['sg'].mean().abs(), 'k': g.size()}).reindex(pos)
    R['k'] = R['k'].fillna(0)
    R['gross'] = R['gross'].fillna(0.0)
    R['exp'] = np.where(R['k'] > 0, 1 + R['spy'].fillna(0), 0.0)
    act = R['k'] > 0
    out = stats(R['gross'], act)
    out['sr_net'] = {c: M.sharpe(R['gross'] - c / 100 * R['exp'], PPY) for c in COSTS}
    out['mean_net_bp'] = {c: 100 * (R['gross'] - c / 100 * R['exp']).mean() for c in COSTS}
    out['exp'] = float(R.loc[act, 'exp'].mean())
    return out, R


# =============================================================================
# EC. (1): EFECTE FIXE DE ACTIUNE SI DE DATA, SE PE DOUA DIMENSIUNI, WILD CLUSTER BOOTSTRAP
# =============================================================================
def fe_resid(v, g1, g2, tol=1e-12, it=1000):
    """Reziduurile dupa efectele fixe g1 si g2 (proiectii alternante)."""
    v = np.asarray(v, float).copy()
    n1, n2 = g1.max() + 1, g2.max() + 1
    c1, c2 = np.bincount(g1, minlength=n1), np.bincount(g2, minlength=n2)
    for _ in range(it):
        old = v.copy()
        v -= (np.bincount(g1, weights=v, minlength=n1) / c1)[g1]
        v -= (np.bincount(g2, weights=v, minlength=n2) / c2)[g2]
        if np.max(np.abs(v - old)) < tol:
            break
    return v


def eq1(y, x, stock, date, B=9999, seed=15):
    gs, us = pd.factorize(stock)
    gd, ud = pd.factorize(date)
    xt = fe_resid(x, gs, gd)
    yt = fe_resid(y, gs, gd)
    Sxx = xt @ xt
    b = xt @ yt / Sxx
    e = yt - b * xt
    u = xt * e

    def V(codes):
        s = np.bincount(codes, weights=u)
        G = len(s)
        return G / (G - 1) * (s @ s) / Sxx ** 2
    inter = pd.factorize(pd.Series(gs).astype(str) + '_' + pd.Series(gd).astype(str))[0]
    v_d, v_s, v_i = V(gd), V(gs), V(inter)
    se2 = np.sqrt(max(v_d + v_s - v_i, 0))
    # wild cluster bootstrap pe actiuni, modelul nul (b = 0) cu ambele efecte fixe
    G = len(us)
    e0 = yt                                    # reziduurile modelului nul = y fara efectele fixe
    U = np.column_stack([fe_resid(np.where(gs == g, e0, 0.0), gs, gd) for g in range(G)])   # M(e0 * 1_g)
    A = np.bincount(gs, weights=xt * e0, minlength=G)
    Bg = np.bincount(gs, weights=xt * xt, minlength=G)
    K = np.column_stack([np.bincount(gs, weights=xt * U[:, h], minlength=G) for h in range(G)])  # K[g, h]
    cr = G / (G - 1)

    def tstat_s(bb, s):
        return bb / np.sqrt(cr * np.sum(s ** 2, -1) / Sxx ** 2)
    t_s = b / np.sqrt(v_s)
    rng = np.random.default_rng(seed)
    W = rng.choice([-1.0, 1.0], size=(B, G))
    bs = W @ A / Sxx
    Sg = W @ K.T - bs[:, None] * Bg[None, :]
    ts = tstat_s(bs, Sg)
    p_wcr = float(np.mean(np.abs(ts) >= abs(t_s)))
    return {'b': float(b), 'se_2way': float(se2), 't_2way': float(b / se2), 'se_date': float(np.sqrt(v_d)),
            'se_stock': float(np.sqrt(v_s)), 't_stock': float(t_s), 'p_wcr': p_wcr, 'n': int(len(y)),
            'G_date': int(len(ud)), 'G_stock': int(G), 'B': B}


# =============================================================================
def main():
    h, rets = load()
    out = {}
    # (a) raspunsurile
    N = len(h)
    sh = h['lab'].value_counts(normalize=True)
    out['a'] = {'n_headlines': N, 'n_prompts': int(h['key'].nunique()),
                'n_stocks': int(h['ticker'].nunique()), 'first': h['date'].min(), 'last': h['date'].max(),
                'share': {k: float(sh.get(k, 0.0)) for k in ('YES', 'NO', 'UNKNOWN', 'invalid')}}
    v = h.dropna(subset=['s', 'day'])
    # (b)-(c) portofoliul
    daily = v.groupby(['day', 'ticker'])['s'].mean().to_frame()
    first = daily.index.get_level_values('day').min()
    days = rets.index[rets.index >= first]
    Pf = portfolio(daily, rets, days, lag=2)
    act = Pf['legs'] > 0
    res = {}
    for col, spy in (('raw', 0.0), ('hedged', 1.0)):
        x = Pf[col]
        r = stats(x, act)
        r['sr_net'] = {c: M.sharpe(x - c / 100 * (Pf['gross_exp'] + spy * Pf['spy_exp']), PPY) for c in COSTS}
        r['mean_net_bp'] = {c: 100 * (x - c / 100 * (Pf['gross_exp'] + spy * Pf['spy_exp'])).mean() for c in COSTS}
        res[col] = r
    out['port'] = res
    out['days'] = {'n': int(len(Pf)), 'both': float((Pf['legs'] == 2).mean()), 'one': float((Pf['legs'] == 1).mean()),
                   'long_only': float(((Pf['legs'] == 1) & Pf['L'].notna()).mean()),
                   'short_only': float(((Pf['legs'] == 1) & Pf['S'].notna()).mean()),
                   'none': float((Pf['legs'] == 0).mean()), 'first': str(days[0].date()), 'last': str(days[-1].date()),
                   'n_stockdays': int(len(daily))}
    out['legs'] = {'long_bp': 100 * float(Pf['L'].mean()), 'short_bp': -100 * float(Pf['S'].mean()),
                   'long_t': M.nw_t(Pf['L'].dropna())[1], 'short_t': M.nw_t(-Pf['S'].dropna())[1]}
    # reactia (aceeasi zi d), ca reper pentru rata de succes a reactiei din tabelul 1
    P0 = portfolio(daily, rets, days, lag=0)
    out['reaction'] = stats(P0['raw'], P0['legs'] > 0)
    # (d) ec. (1) la nivel de titlu
    ix = pd.DatetimeIndex(rets.index)
    reg = {}
    for hh in (0, 2):
        pos = ix.get_indexer(v['day'])
        ok = (pos >= 0) & (pos + hh < len(ix))
        w = v[ok].copy()
        w['ret'] = [rets.iat[p + hh, rets.columns.get_loc(t)] for p, t in zip(pos[ok], w['ticker'])]
        w = w.dropna(subset=['ret'])
        reg[f'h{hh}'] = eq1(w['ret'].values, w['s'].values, w['ticker'].values, w['day'].values)
    out['eq1'] = reg
    # (e) C1 pe aceleasi zile-actiune, acelasi cost pe unitatea de valoare nominala
    c1daily = pd.read_csv(os.path.join(HERE, 'ch15_news_daily.csv'), parse_dates=['day']).set_index(['day', 'ticker'])
    c1, _ = c1_same_days(c1daily, daily.index, rets, days)
    out['c1'] = c1
    path = os.path.join(HERE, 'sem15_results.json')
    with open(path) as f:
        S = json.load(f)
    S['c3'] = json.loads(json.dumps(out, default=float))
    with open(path, 'w') as f:
        json.dump(S, f, indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()

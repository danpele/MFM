"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 9 (MFM): volatilitate realizata
===================================================================================
  * read_market(symbol)     -- seria zilnica din data/market/
  * daily_returns(name)     -- randamente log zilnice (in %), pe calendarul propriu al seriei
  * spy_intraday()          -- SPY, bare de 5 minute, doar sesiunea regulata din SUA (09:30-16:00, ora New York)
  * btc_intraday()          -- Bitcoin, bare de 5 minute, zile UTC complete (24 de ore)
  * intraday_returns(P)     -- randamentele log de 5 minute ale fiecarei zile (in %)

Conventii:
  * barele sunt etichetate cu ora de inceput; pretul unei bare = pretul de inchidere;
  * SPY: prima bara 09:30, ultima 15:55 (78 de randamente pe zi; 42 in zilele cu program redus);
    randamentul zilei incepe de la deschiderea barei de 09:30; bara-ciot de 16:00 si barele din afara
    grilei de 5 minute sunt eliminate;
  * Bitcoin: grila UTC regulata de 5 minute; fiecare interval pastreaza ultimul pret; se pastreaza doar
    zilele cu cel putin 95% din cele 288 de bare (golurile scurte se completeaza cu pretul anterior);
  * seriile zilnice: ETF-uri -> pretul ajustat; indici, cripto -> pretul de inchidere.

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'

# nume -> (simbol, coloana, eticheta, 7 zile din 7?)
DAILY = {
    'spy': ('SPY.US', 'adjusted_close', 'SPY (S&P 500 ETF)', False),
    'sp500': ('GSPC.INDX', 'close', 'S&P 500', False),
    'btc': ('BTC-USD.CC', 'close', 'Bitcoin', True),
    'vix': ('VIX.INDX', 'close', 'VIX', False),
}


def read_market(symbol):
    """Citeste data/market/<SIMBOL>.csv local sau din repo-ul GitHub."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def read_intraday(symbol):
    """Citeste data/market/intraday/<SIMBOL>_5m.csv (ora UTC)."""
    fname = f'intraday/{symbol}_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    d = pd.read_csv(src, index_col='datetime_utc', parse_dates=True).sort_index()
    return d[~d.index.duplicated(keep='last')]


def daily_close(name, start=None, end=END):
    """Pretul zilnic: fara cotatii de weekend (in afara de cripto) si fara zile cu pret neschimbat (indici)."""
    symbol, col, _, all_week = DAILY[name]
    s = read_market(symbol)[col].loc[start:end]
    s = s[s > 0].dropna()
    if not all_week:
        s = s[s.index.dayofweek < 5]
    if name in ('sp500', 'vix'):
        s = s[s.diff() != 0]
    return s.rename(name)


def daily_returns(name, start=None, end=END):
    """Randamente log zilnice, in %, pe calendarul propriu al seriei."""
    return (100 * np.log(daily_close(name, start, end)).diff().dropna()).rename(name)


def spy_intraday(end=END):
    """Preturile SPY din sesiunea regulata: matrice zi x 79 de puncte (deschiderea de 09:30 + 78 de inchideri)."""
    d = read_intraday('SPY.US')
    d.index = d.index.tz_localize('UTC').tz_convert('America/New_York')
    d = d[(d.index.second == 0) & (d.index.minute % 5 == 0)]            # fara bare din afara grilei
    mins = d.index.hour * 60 + d.index.minute
    d = d[(mins >= 9 * 60 + 30) & (mins <= 15 * 60 + 55)]               # 09:30-15:55 (fara bara-ciot de 16:00)
    d = d.loc[:end + ' 23:59']
    slot = ((d.index.hour * 60 + d.index.minute) - (9 * 60 + 30)) // 5  # 0..77
    day = pd.to_datetime(d.index.date)
    close = pd.DataFrame({'day': day, 'slot': slot, 'p': d['close'].values}).pivot(index='day', columns='slot', values='p')
    first = pd.Series(d['open'].values, index=day)[slot == 0]
    first = first[~first.index.duplicated()]
    P = pd.concat([first.rename(-1), close], axis=1).sort_index(axis=1)
    P = P[P[0].notna() & P[-1].notna()]
    P.columns = range(P.shape[1])                                        # 0 = deschiderea, 1..78 = inchiderile barelor
    last = P.notna().values.cumsum(axis=1).argmax(axis=1)                # ultima bara disponibila a zilei
    F = P.ffill(axis=1)                                                  # bare lipsa in interiorul zilei: pretul anterior
    F = F.where(np.arange(P.shape[1])[None, :] <= last[:, None])         # dupa inchiderea zilelor scurte: NaN
    return F


def btc_intraday(end=END, min_share=0.95):
    """Preturile Bitcoin pe zile UTC: matrice zi x 289 de puncte (deschiderea de 00:00 + 288 de inchideri)."""
    d = read_intraday('BTC-USD.CC')
    d = d[d['close'].notna() & (d['close'] > 0)].loc[:end + ' 23:59']
    g = d.resample('5min', label='left', closed='left').agg({'open': 'first', 'close': 'last'})
    have = g['close'].notna()
    day = pd.to_datetime(g.index.date)
    n = have.groupby(day).sum()
    keep = n[n >= min_share * 288].index
    g = g[day.isin(keep)]
    day = pd.to_datetime(g.index.date)
    slot = (g.index.hour * 60 + g.index.minute) // 5
    close = pd.DataFrame({'day': day, 'slot': slot, 'p': g['close'].values}).pivot(index='day', columns='slot', values='p')
    close = close.ffill(axis=1)                                          # goluri scurte: ultimul pret cunoscut
    op = pd.DataFrame({'day': day, 'slot': slot, 'p': g['open'].values}).pivot(index='day', columns='slot', values='p')
    first = op.bfill(axis=1)[0].fillna(close[0])
    close = close.bfill(axis=1)                                          # zi care incepe cu un gol
    P = pd.concat([first.rename(-1), close], axis=1).sort_index(axis=1)
    P.columns = range(P.shape[1])
    return P


def intraday_returns(P):
    """Randamentele log intr-o zi, in %: coloana j = intervalul (j-1, j]; NaN dupa inchiderea zilelor scurte."""
    return 100 * np.log(P).diff(axis=1).iloc[:, 1:]


def spy_overnight(P):
    """Randamentul peste noapte (%): randamentul zilnic ajustat minus randamentul deschidere-inchidere al zilei."""
    oc = 100 * np.log(P.ffill(axis=1).iloc[:, -1] / P[0])
    cc = daily_returns('spy').reindex(P.index)
    return (cc - oc).rename('overnight'), oc.rename('open_close'), cc.rename('close_close')

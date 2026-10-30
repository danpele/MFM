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
  * SPY: prima bara 09:30, ultima 15:55 (78 de randamente pe zi); randamentul zilei incepe de la deschiderea
    barei de 09:30; bara-ciot de 16:00 si barele din afara grilei de 5 minute sunt eliminate;
  * SPY, zilele cu program redus (inchidere la 13:00): 42 de intervale, 09:30-13:00; bara etichetata 13:00
    (13:00-13:05) este dupa inchidere si nu devine un interval; deschiderea ei (printul de la 13:00) este folosita
    doar ca pret la 13:00 cind bara de 12:55 lipseste;
  * Bitcoin: grila UTC regulata de 5 minute; fiecare interval pastreaza ultimul pret; se pastreaza doar
    zilele cu cel putin 95% din cele 288 de bare (golurile se completeaza cu pretul anterior, deci intervalul lipsa
    se contopeste cu urmatorul); pretul de la 00:00 = deschiderea primei bare sau, daca bara de 00:00 lipseste,
    inchiderea barei de 23:55 din ziua precedenta; fara aceste observatii ziua este eliminata (fara bfill);
    ziua masurata se termina la ultimul pret observat;
  * masca barelor completate: IMPUTED['spy'], IMPUTED['btc'] (True = bara lipsa, completata cu pretul anterior);
  * seriile zilnice: ETF-uri -> pretul ajustat; indici, cripto -> pretul de inchidere.
  * seriile zilnice (fara cripto): o zi care repeta inchiderea anterioara este eliminata doar daca nu arata
    tranzactii (volum zero, cand fisierul raporteaza volum, open = high = low = close sau o copie a
    randului precedent); o inchidere
    neschimbata intr-o zi cu tranzactii este un randament zero real si se pastreaza;
  * barele de 5 minute nu se filtreaza dupa pretul neschimbat (o bara cu aceeasi inchidere este reala).

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'
IMPUTED = {}       # name -> mask of the 5-minute bars filled with the previous price (set by spy_intraday, btc_intraday)

# name -> (symbol, price field, label, traded 7 days a week?)
DAILY = {
    'spy': ('SPY.US', 'adjusted_close', 'SPY (S&P 500 ETF)', False),
    'sp500': ('GSPC.INDX', 'close', 'S&P 500', False),
    'btc': ('BTC-USD.CC', 'close', 'Bitcoin', True),
    'vix': ('VIX.INDX', 'close', 'VIX', False),
}


def read_market(symbol):
    """Daily prices of one course series (local copy if present, otherwise the online copy)."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def read_intraday(symbol):
    """5-minute bars of one course series (UTC time)."""
    fname = f'intraday/{symbol}_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    d = pd.read_csv(src, index_col='datetime_utc', parse_dates=True).sort_index()
    return d[~d.index.duplicated(keep='last')]


def daily_close(name, start=None, end=END):
    """Daily price: no weekend quotes (except crypto) and no artificial non-trading-day fills."""
    symbol, col, _, all_week = DAILY[name]
    d = read_market(symbol).loc[start:end]
    d = d[d[col] > 0].dropna(subset=[col])
    if not all_week:
        d = d[d.index.dayofweek < 5]          # no weekend quotes
        d = d[~artificial_fill(d)]            # non-trading days filled with the previous price
    return d[col].rename(name)


def artificial_fill(d):
    """Rows that repeat the previous close and show no trading: an artificial non-trading-day fill.

    A repeated close is a fill only if the row itself shows no trading: zero volume (for files that report
    volume), no intraday range (open = high = low = close) or a copy of the previous row in every field. A
    repeated close on a day with volume and an intraday range is a genuine unchanged close (a zero return)
    and is kept. Files with closes only give no such evidence, so every row is kept.
    """
    repeat = d['close'].diff() == 0
    no_trade = pd.Series(False, index=d.index)
    if 'volume' in d and (d['volume'] > 0).mean() > 0.5:
        no_trade |= d['volume'].fillna(0) <= 0
    if {'open', 'high', 'low'} <= set(d.columns):
        no_trade |= (d['open'] == d['high']) & (d['high'] == d['low']) & (d['low'] == d['close'])
        fields = [c for c in ['open', 'high', 'low', 'close', 'volume'] if c in d]
        no_trade |= (d[fields] == d[fields].shift()).all(axis=1)
    return repeat & no_trade


def daily_returns(name, start=None, end=END):
    """Daily log returns in %, on the series' own calendar."""
    return (100 * np.log(daily_close(name, start, end)).diff().dropna()).rename(name)


def spy_intraday(end=END):
    """SPY prices in the regular session: day x 79 matrix (09:30 open + 78 bar closes).

    Early-close days (no bar after 13:00): the session ends at 13:00, 42 intervals; the 13:00 bar is after the close
    and is not an interval (its open, the print at 13:00, is used only as the 13:00 price when the 12:55 bar is
    missing). IMPUTED[name]: mask of the bars filled with the previous price."""
    d = read_intraday('SPY.US')
    d.index = d.index.tz_localize('UTC').tz_convert('America/New_York')
    d = d[(d.index.second == 0) & (d.index.minute % 5 == 0)]            # drop bars off the 5-minute grid
    mins = d.index.hour * 60 + d.index.minute
    d = d[(mins >= 9 * 60 + 30) & (mins <= 15 * 60 + 55)]               # 09:30-15:55 (drop the stub 16:00 bar)
    d = d.loc[:end + ' 23:59']
    slot = ((d.index.hour * 60 + d.index.minute) - (9 * 60 + 30)) // 5  # 0..77
    day = pd.to_datetime(d.index.date)
    close = pd.DataFrame({'day': day, 'slot': slot, 'p': d['close'].values}).pivot(index='day', columns='slot', values='p')
    opn = pd.DataFrame({'day': day, 'slot': slot, 'p': d['open'].values}).pivot(index='day', columns='slot', values='p')
    close = close.reindex(columns=range(78))
    opn = opn.reindex(columns=range(78))
    early = ~close.loc[:, 43:].notna().any(axis=1) & close.loc[:, :42].notna().any(axis=1)   # session closes at 13:00
    fill41 = early & close[41].isna() & opn[42].notna()
    close.loc[fill41, 41] = opn.loc[fill41, 42]                          # price at 13:00 = first print of the 13:00 bar
    close.loc[early, 42:] = np.nan                                       # nothing after the 13:00 close
    first = pd.Series(d['open'].values, index=day)[slot == 0]
    first = first[~first.index.duplicated()]
    P = pd.concat([first.rename(-1), close], axis=1).sort_index(axis=1)
    P = P[P[0].notna() & P[-1].notna()]
    early = early.reindex(P.index)
    P.columns = range(P.shape[1])                                        # 0 = open, 1..78 = bar closes
    n_int = np.where(early.values, 42, 78)                              # intervals in the session
    inside = np.arange(P.shape[1])[None, :] <= n_int[:, None]
    imputed = P.isna() & inside
    F = P.ffill(axis=1)                                                  # missing bars inside the day: previous price
    F = F.where(inside)                                                  # after the close of short days: NaN
    IMPUTED['spy'] = imputed
    return F


def btc_intraday(end=END, min_share=0.95):
    """Bitcoin prices on UTC days: day x 289 matrix (price at 00:00 + 288 bar closes).

    Price at 00:00: open of the 00:00 bar or, if that bar is missing, the close of the previous day's 23:55 bar;
    days with neither are dropped (no backward fill). Gaps inside the day keep the previous price (the missing
    interval merges with the next one); the measured day ends at the last observed price.
    IMPUTED[name]: mask of the bars filled with the previous price."""
    d = read_intraday('BTC-USD.CC')
    d = d[d['close'].notna() & (d['close'] > 0)].loc[:end + ' 23:59']
    g = d.resample('5min', label='left', closed='left').agg({'open': 'first', 'close': 'last'})
    have = g['close'].notna()
    day = pd.to_datetime(g.index.date)
    n = have.groupby(day).sum()
    slot = (g.index.hour * 60 + g.index.minute) // 5
    close_all = pd.DataFrame({'day': day, 'slot': slot, 'p': g['close'].values}).pivot(index='day', columns='slot', values='p')
    op_all = pd.DataFrame({'day': day, 'slot': slot, 'p': g['open'].values}).pivot(index='day', columns='slot', values='p')
    prev_last = close_all[287].shift(1, freq='D').reindex(close_all.index)   # previous day's 23:55 bar close
    first = op_all[0].where(op_all[0].notna(), prev_last)
    keep = n[(n >= min_share * 288)].index
    keep = keep[first.reindex(keep).notna().values]
    close = close_all.loc[keep]
    imputed = close.isna()
    close = close.ffill(axis=1)                                          # gaps: last known price
    close = close.where(close.notna(), first.loc[keep], axis=0) if close.isna().any().any() else close
    P = pd.concat([first.loc[keep].rename(-1), close], axis=1).sort_index(axis=1)
    P.columns = range(P.shape[1])
    imputed = pd.concat([pd.Series(False, index=keep, name=-1), imputed], axis=1)
    imputed.columns = range(imputed.shape[1])
    IMPUTED['btc'] = imputed
    return P


def intraday_returns(P):
    """Intraday log returns in %: column j = interval (j-1, j]; NaN after the close of short days."""
    return 100 * np.log(P).diff(axis=1).iloc[:, 1:]


def spy_overnight(P):
    """Overnight return (%): adjusted daily return minus the open-to-close return of the day."""
    oc = 100 * np.log(P.ffill(axis=1).iloc[:, -1] / P[0])
    cc = daily_returns('spy').reindex(P.index)
    return (cc - oc).rename('overnight'), oc.rename('open_close'), cc.rename('close_close')

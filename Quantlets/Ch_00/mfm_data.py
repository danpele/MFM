"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 0 (MFM): Pietele financiare in 2026
======================================================================================
TOATE descarcarile trec printr-o singura functie, fetch_daily(symbol, source, field).

Surse:
  * 'market'    -- date zilnice de piata din data/market/<SYMBOL>.csv
                   (coloane: date, open, high, low, close, adjusted_close, volume),
                   citite local, altfel din repo-ul GitHub MFM.
  * 'fred'      -- FRED (CSV public: randamente Treasury SUA, rata Fed Funds
  * 'defillama' -- DefiLlama (JSON public: oferta de stablecoins legate de USD
  * 'bnr'       -- BNR (arhive XML anuale publice:
                   cursul oficial de referinta EUR/RON

Conventie: adjusted_close pentru ETF-uri si actiuni; close pentru indici, FX, cripto, randamente.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import io
import json
import urllib.request
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
START, END = '2000-01-01', '2026-09-18'

# nume -> (sursa, simbol, camp)
SERIES = {
    # indici (close)
    'S&P 500':            ('market', 'GSPC.INDX', 'close'),
    'Euro Stoxx 50':      ('market', 'STOXX50E.INDX', 'close'),
    'Nikkei 225':         ('market', 'N225.INDX', 'close'),
    'VIX':                ('market', 'VIX.INDX', 'close'),
    'BET-TR':             ('market', 'BETTR.INDX', 'close'),
    'BET':                ('market', 'BET', 'close'),             # indicele BET, valori oficiale 19.09.1997 - 18.09.2026
    'BET-XT':             ('market', 'BETXT.INDX', 'close'),
    # ETF-uri (adjusted_close; volume)
    'US Treasuries 20y+ (TLT)': ('market', 'TLT.US', 'adjusted_close'),
    'SPY':                ('market', 'SPY.US', 'adjusted_close'),
    'RSP':                ('market', 'RSP.US', 'adjusted_close'),
    'IBIT':               ('market', 'IBIT.US', 'close'),
    'IBIT volume':        ('market', 'IBIT.US', 'volume'),
    # marfuri, FX, cripto (close)
    'Gold':               ('market', 'XAUUSD.FOREX', 'close'),
    'EUR/USD':            ('market', 'EURUSD.FOREX', 'close'),
    'EUR/RON (market file)':    ('market', 'EURRON.FOREX', 'close'),
    'Bitcoin':            ('market', 'BTC-USD.CC', 'close'),
    'Ethereum':           ('market', 'ETH-USD.CC', 'close'),
    # randamente titluri de stat (close, %)
    'Romania 10y':        ('market', 'RO10Y.GBOND', 'close'),
    'Germany 10y':        ('market', 'DE10Y.GBOND', 'close'),
    # actiuni BVB (adjusted_close)
    'Banca Transilvania': ('market', 'TLV.RO', 'adjusted_close'),
    'OMV Petrom':         ('market', 'SNP.RO', 'adjusted_close'),
    'BRD':                ('market', 'BRD.RO', 'adjusted_close'),
    'Transgaz':           ('market', 'TGN.RO', 'adjusted_close'),
    'Romgaz':             ('market', 'SNG.RO', 'adjusted_close'),
    'Hidroelectrica':     ('market', 'H2O.RO', 'adjusted_close'),
    # surse publice
    'EUR/RON':            ('bnr', 'EUR', None),
    'DGS10':              ('fred', 'DGS10', None),
    'DGS2':               ('fred', 'DGS2', None),
    'FEDFUNDS':           ('fred', 'FEDFUNDS', None),
    'USD per EUR':        ('fred', 'DEXUSEU', None),   # cursuri FRED (H.10), pentru conversia in USD
    'JPY per USD':        ('fred', 'DEXJPUS', None),
    'T10Y2Y':             ('fred', 'T10Y2Y', None),
    'Stablecoins':        ('defillama', 'stablecoincharts/all', None),
}


def read_market(symbol):
    """Fisierul de date de piata: local (data/market), altfel din repo-ul GitHub."""
    path = os.path.join(MARKET_DIR, f'{symbol}.csv')
    src = path if os.path.exists(path) else REPO_RAW + f'{symbol}.csv'
    return pd.read_csv(src, index_col='date', parse_dates=True)


def fetch_daily(symbol, source='market', field='close', start=START, end=END):
    """Punctul unic de acces la date: intoarce o pd.Series zilnica (fara NaN)."""
    if source == 'market':
        s = read_market(symbol)[field]
    elif source == 'fred':
        raw = urllib.request.urlopen(
            f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={symbol}', timeout=90).read().decode()
        s = pd.read_csv(io.StringIO(raw), index_col=0, parse_dates=True, na_values='.').iloc[:, 0]
    elif source == 'defillama':
        req = urllib.request.Request(f'https://stablecoins.llama.fi/{symbol}',
                                     headers={'User-Agent': 'Mozilla/5.0'})
        d = json.load(urllib.request.urlopen(req, timeout=90))
        s = pd.Series({pd.to_datetime(int(x['date']), unit='s'): x['totalCirculatingUSD'].get('peggedUSD', 0)
                       for x in d}) / 1e9                                   # miliarde USD
    elif source == 'bnr':
        # cursul oficial BNR (RON pentru o unitate de valuta), arhive XML anuale
        import re
        rows = []
        for y in range(max(int(start[:4]), 2005), int(end[:4]) + 1):
            url = f'https://curs.bnr.ro/files/xml/years/nbrfxrates{y}.xml'
            xml = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla'}),
                                         timeout=90).read().decode()
            for d, body in re.findall(r'<Cube date="([\d-]+)">(.*?)</Cube>', xml, re.S):
                m = re.search(rf'<Rate currency="{symbol}">([\d.]+)</Rate>', body)
                if m:
                    rows.append((d, float(m.group(1))))
        s = pd.Series(dict(rows))
    else:
        raise ValueError(f'unknown source: {source}')
    s = pd.to_numeric(s, errors='coerce')
    s.index = pd.to_datetime(s.index)
    s.index.name = 'Date'
    return s.sort_index().loc[start:end].dropna()


WEEKDAYS_ONLY = {'Gold', 'EUR/USD'}   # cotatii FX/OTC: sesiunile partiale de weekend rup randamentul vineri-luni


def load(name, start=START, end=END):
    """Seria cu numele din SERIES (pentru aur si EUR/USD: doar zilele lucratoare)."""
    source, symbol, field = SERIES[name]
    s = fetch_daily(symbol, source, field, start, end).rename(name)
    if name in WEEKDAYS_ONLY:
        s = s[s.index.dayofweek < 5]
    return s


def load_panel(names, start=START, end=END):
    """Mai multe serii aliniate pe data (NaN acolo unde o piata nu tranzactioneaza)."""
    return pd.concat([load(n, start, end) for n in names], axis=1)

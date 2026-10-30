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
  * 'french'    -- Kenneth French Data Library (zip public: factori Fama-French lunari)
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
    'EUR/RON (EODHD)':    ('market', 'EURRON.FOREX', 'close'),
    'EUR/RON (market)':   ('market', 'EURRON.FOREX', 'close'),   # aceeasi serie (nume folosit in Seminarul 0)
    'Bitcoin':            ('market', 'BTC-USD.CC', 'close'),
    'Ethereum':           ('market', 'ETH-USD.CC', 'close'),
    'Tether (USDT)':      ('market', 'USDT-USD.CC', 'close'),
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
    'ETF equities':       ('fred', 'BOGZ1LM563064100Q', None),   # Financial Accounts of the US, trimestrial, mil. USD
    'All equities':       ('fred', 'BOGZ1LM893064105Q', None),
    'Stablecoins':        ('defillama', 'stablecoincharts/all', None),
    # Kenneth French Data Library (lunar, zecimal): piata SUA ponderata dupa capitalizare (CRSP) si T-bill 1 luna
    'US market excess (FF)': ('french', 'F-F_Research_Data_Factors', 'Mkt-RF'),
    'T-bill 1m (FF)':        ('french', 'F-F_Research_Data_Factors', 'RF'),
    'DFII10':             ('fred', 'DFII10', None),     # randamentul TIPS la 10 ani (indexat la inflatie)
    'DTB3':               ('fred', 'DTB3', None),       # T-bill la 3 luni (piata secundara)
}


def read_market(symbol):
    """Fisierul de date de piata: local (data/market), altfel din repo-ul GitHub."""
    path = os.path.join(MARKET_DIR, f'{symbol}.csv')
    src = path if os.path.exists(path) else REPO_RAW + f'{symbol}.csv'
    return pd.read_csv(src, index_col='date', parse_dates=True)


def fetch_daily(symbol, source='market', field='close', start=START, end=END):
    """Single access point to the data: returns a daily pd.Series (no NaN)."""
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
                       for x in d}) / 1e9                                   # billion USD
    elif source == 'bnr':
        # official BNR rate (RON per unit of currency), yearly XML archives
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
    elif source == 'french':
        # Kenneth French Data Library (public zip): monthly Fama-French factors, in percent
        import zipfile
        url = f'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{symbol}_CSV.zip'
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}),
                                     timeout=120).read()
        z = zipfile.ZipFile(io.BytesIO(raw))
        lines = z.read(z.namelist()[0]).decode('latin-1').splitlines()
        i = next(k for k, l in enumerate(lines) if l.startswith(',') and len(l.split(',')) > 1)
        cols = [c.strip() for c in lines[i].split(',')[1:]]
        rows = {}
        for l in lines[i + 1:]:
            parts = [x.strip() for x in l.split(',')]
            if len(parts[0]) != 6 or not parts[0].isdigit():
                break                                                     # end of the monthly table
            rows[pd.Timestamp(parts[0] + '01') + pd.offsets.MonthEnd(0)] = float(parts[1 + cols.index(field)])
        s = pd.Series(rows) / 100.0                                       # percent -> decimal
    else:
        raise ValueError(f'unknown source: {source}')
    s = pd.to_numeric(s, errors='coerce')
    s.index = pd.to_datetime(s.index)
    s.index.name = 'Date'
    return s.sort_index().loc[start:end].dropna()


WEEKDAYS_ONLY = {'Gold', 'EUR/USD'}   # cotatii FX/OTC: sesiunile partiale de weekend rup randamentul vineri-luni


def load(name, start=START, end=END):
    """The series named in SERIES (gold and EUR/USD: weekdays only)."""
    source, symbol, field = SERIES[name]
    s = fetch_daily(symbol, source, field, start, end).rename(name)
    if name in WEEKDAYS_ONLY:
        s = s[s.index.dayofweek < 5]
    return s


def load_panel(names, start=START, end=END):
    """Several series aligned on date (NaN where a market does not trade)."""
    return pd.concat([load(n, start, end) for n in names], axis=1)

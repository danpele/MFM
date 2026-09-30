"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 17 (MFM): bule si crahuri
===========================================================================
  * price(name, freq)      -- pretul (nivelul) unei serii din data/market/, zilnic, saptamanal sau lunar
  * shiller()              -- S&P Composite lunar din 1871: pret real, dividend real, raportul pret/dividend
                              (datele publice ale lui Robert J. Shiller)
  * industries()           -- cele 49 de portofolii pe industrii (ponderate cu valoarea) si piata,
                              randamente lunare din Kenneth French Data Library

Conventii (ca in capitolele 0-8):
  * indicii bursieri: doar zilele lucratoare; zilele cu inchidere identica cu ziua precedenta sunt eliminate;
  * cripto: 7 zile din 7;
  * actiuni: pretul ajustat (dividende, split-uri); indici si cripto: pretul de inchidere;
  * saptamanal / lunar: ultimul pret al saptamanii (vineri) / al lunii.

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import io
import os
import re
import zipfile
import urllib.request
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'

# name -> (symbol, label, type, price field, start date)
MARKETS = {
    'sp500': ('GSPC.INDX',   'S&P 500',        'index',  'close',          '1990-01-01'),
    'ndx':   ('NDX.INDX',    'Nasdaq 100',     'index',  'close',          '1990-01-01'),
    'bet':   ('BET',         'BET',            'index',  'close',          '1997-09-19'),
    'betfi': ('BETFI.INDX',  'BET-FI',         'index',  'close',          '2012-01-25'),
    'btc':   ('BTC-USD.CC',  'Bitcoin',        'crypto', 'close',          '2014-09-17'),
    'eth':   ('ETH-USD.CC',  'Ethereum',       'crypto', 'close',          '2016-01-01'),
    'doge':  ('DOGE-USD.CC', 'Dogecoin',       'crypto', 'close',          '2017-01-01'),
    'nvda':  ('NVDA.US',     'NVIDIA',         'stock',  'adjusted_close', '1999-01-22'),
    'csco':  ('CSCO.US',     'Cisco Systems',  'stock',  'adjusted_close', '1990-02-16'),
    'tsla':  ('TSLA.US',     'Tesla',          'stock',  'adjusted_close', '2010-06-29'),
    'gme':   ('GME.US',      'GameStop',       'stock',  'adjusted_close', '2002-02-13'),
    'mstr':  ('MSTR.US',     'Strategy (MicroStrategy)', 'stock', 'adjusted_close', '1998-06-11'),
}
LABELS = {k: v[1] for k, v in MARKETS.items()}

SHILLER_URLS = ['https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/ie_data.xls',
                'http://www.econ.yale.edu/~shiller/data/ie_data.xls']
FRENCH = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'

_CACHE = {}


def read_market(symbol):
    """Read the daily prices of one asset from the course data."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def price(name, freq='D', start=None, end=END):
    """Price level: 'D' daily (cleaned), 'W' last price of the week, 'M' last price of the month."""
    symbol, _, kind, col, start0 = MARKETS[name]
    s = read_market(symbol)[col].loc[start or start0:end]
    s = s[s > 0].dropna()
    if kind != 'crypto':
        s = s[s.index.dayofweek < 5]          # no weekend quotes
    if kind == 'index':
        s = s[s.diff() != 0]                  # drop holidays filled with the previous price
    last = s.index[-1]
    if freq == 'W':
        s = s.resample('W-FRI').last().dropna()
    elif freq == 'M':
        s = s.resample('ME').last().dropna()
    if freq in ('W', 'M') and s.index[-1] > last:
        s.index = s.index[:-1].append(pd.DatetimeIndex([last]))   # last incomplete period: dated at its last observation
    return s.rename(name)


def shiller_urls():
    """Addresses of Shiller's ie_data.xls: the current shillerdata.com link, then known copies."""
    urls = []
    try:
        html = urllib.request.urlopen(urllib.request.Request('https://shillerdata.com/', headers={'User-Agent': 'Mozilla/5.0'}),
                                      timeout=60).read().decode('utf-8', 'ignore')
        urls += ['https:' + u if u.startswith('//') else u
                 for u in re.findall(r'href="([^"]*ie_data\.xls[^"]*)"', html)]
    except Exception:
        pass
    return urls + SHILLER_URLS


def shiller():
    """Monthly S&P Composite (Shiller): real price, real dividend and the price-dividend ratio (P/D)."""
    if 'shiller' in _CACHE:
        return _CACHE['shiller']
    raw = None
    for url in shiller_urls():
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}),
                                         timeout=120).read()
            break
        except Exception:
            continue
    d = pd.read_excel(io.BytesIO(raw), sheet_name='Data', header=None, skiprows=8)
    d = d.iloc[:, [0, 1, 2, 7, 8]]
    d.columns = ['date', 'P', 'D', 'real_P', 'real_D']
    d = d[pd.to_numeric(d['date'], errors='coerce').notna()].copy()
    yr = d['date'].astype(float)
    year = np.floor(yr + 1e-9).astype(int)
    month = np.round((yr - year) * 100).astype(int)
    d.index = pd.to_datetime(dict(year=year, month=month, day=1)) + pd.offsets.MonthEnd(0)
    d = d[['P', 'D', 'real_P', 'real_D']].apply(pd.to_numeric, errors='coerce').dropna()
    d['PD'] = d['real_P'] / d['real_D']
    _CACHE['shiller'] = d
    return d


def _french_table(fname, section=None, scale=100.0):
    """One monthly table (YYYYMM) from a Kenneth French file: the first (default) or the one titled `section`;
    returns are divided by `scale` (100: decimal), firm counts are read with scale=1."""
    raw = urllib.request.urlopen(urllib.request.Request(FRENCH + fname, headers={'User-Agent': 'Mozilla/5.0'}),
                                 timeout=120).read()
    text = zipfile.ZipFile(io.BytesIO(raw)).read(zipfile.ZipFile(io.BytesIO(raw)).namelist()[0]).decode('latin-1')
    lines = text.splitlines()
    k0 = 0 if section is None else next(k for k, l in enumerate(lines) if l.strip() == section)
    i = next(k for k, l in enumerate(lines) if k >= k0 and l.startswith(',') and len(l.split(',')) > 1)
    cols = [c.strip() for c in lines[i].split(',')[1:]]
    rows = []
    for l in lines[i + 1:]:
        parts = [x.strip() for x in l.split(',')]
        if not parts or len(parts[0]) != 6 or not parts[0].isdigit():
            break
        rows.append([parts[0]] + [float(x) for x in parts[1:]])
    df = pd.DataFrame(rows, columns=['date'] + cols)
    df['date'] = pd.to_datetime(df['date'], format='%Y%m') + pd.offsets.MonthEnd(0)
    return df.set_index('date').replace([-99.99, -999.0], np.nan) / scale


def industries():
    """49 industries (value-weighted monthly returns) and the market return (Mkt-RF + RF)."""
    if 'ind' in _CACHE:
        return _CACHE['ind']
    ind = _french_table('49_Industry_Portfolios_CSV.zip')
    ff = _french_table('F-F_Research_Data_Factors_CSV.zip')
    mkt = (ff['Mkt-RF'] + ff['RF']).rename('MKT')
    _CACHE['ind'] = (ind, mkt)
    return ind, mkt


def industry_firms():
    """Monthly number of firms in each of the 49 industry portfolios (Kenneth French)."""
    if 'firms' not in _CACHE:
        _CACHE['firms'] = _french_table('49_Industry_Portfolios_CSV.zip', 'Number of Firms in Portfolios', 1.0)
    return _CACHE['firms']

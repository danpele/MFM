"""
mfm_data.py -- Data loading for Chapter 19 (MFM): review and integrated case study
===============================================================================================
  * load_close(name)    -- daily price of a course series (or the BNR reference rate)
  * log_returns(name)   -- log returns on the own calendar of each series
  * joint_returns(...)  -- returns for a portfolio: prices aligned on common days first
  * MARKETS             -- S&P 500, BET, Bitcoin, EUR/RON, gold; ETFs and BVB stocks for portfolios

Conventions (as in Chapters 0-8):
  * stock indices: weekdays only; days whose close repeats the previous day
    (holidays filled with the last price) are removed;
  * gold (XAU/USD): weekend quotes removed; annualised with the real frequency;
  * crypto: 7 days a week;
  * ETFs and stocks: adjusted price (dividends, splits); indices, FX, crypto: closing price;
  * EUR/RON: official BNR reference rate.

Modelling Financial Markets - Daniel Traian PELE
"""

import os
import re
import urllib.request
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'

# name -> (symbol, label, type, start date)
MARKETS = {
    'sp500':  ('GSPC.INDX',    'S&P 500',                  'index',  '2000-01-01'),
    'bet':    ('BET',          'BET',                      'index',  '2000-01-01'),
    'btc':    ('BTC-USD.CC',   'Bitcoin',                  'crypto', '2014-09-17'),
    'eurron': ('REF:EUR',      'EUR/RON (reference rate)', 'fx',     '2005-07-01'),
    'gold':   ('XAUUSD.FOREX', 'Gold (XAU/USD)',           'fx',     '2000-01-01'),
}
# assets for portfolios (prices aligned on common days)
ASSETS = {
    'SPY': ('SPY.US', 'adjusted_close'), 'TLT': ('TLT.US', 'adjusted_close'), 'GLD': ('GLD.US', 'adjusted_close'),
    'BTC': ('BTC-USD.CC', 'close'),
    'TLV': ('TLV.RO', 'adjusted_close'), 'SNP': ('SNP.RO', 'adjusted_close'), 'BRD': ('BRD.RO', 'adjusted_close'),
    'TGN': ('TGN.RO', 'adjusted_close'), 'SNG': ('SNG.RO', 'adjusted_close'), 'SNN': ('SNN.RO', 'adjusted_close'),
    'EL': ('EL.RO', 'adjusted_close'), 'FP': ('FP.RO', 'adjusted_close'), 'TEL': ('TEL.RO', 'adjusted_close'),
    'WIG20': ('WIG20.INDX', 'close'),
}
LABELS = {k: v[1] for k, v in MARKETS.items()}

_CACHE = {}


def read_market(symbol):
    """Read one daily price series of the course data (local copy or the course GitHub repository)."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def read_reference_rate(currency='EUR', start='2005-07-01', end=END):
    """Official RON reference rate (annual BNR XML archives)."""
    key = (currency, start, end)
    if key in _CACHE:
        return _CACHE[key]
    rows = []
    for y in range(int(start[:4]), int(end[:4]) + 1):
        url = f'https://curs.bnr.ro/files/xml/years/nbrfxrates{y}.xml'
        xml = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla'}),
                                     timeout=60).read().decode()
        for d, body in re.findall(r'<Cube date="([\d-]+)">(.*?)</Cube>', xml, re.S):
            m = re.search(rf'<Rate currency="{currency}">([\d.]+)</Rate>', body)
            if m:
                rows.append((d, float(m.group(1))))
    s = pd.DataFrame(rows, columns=['date', 'close']).drop_duplicates('date').set_index('date')['close']
    s.index = pd.to_datetime(s.index)
    _CACHE[key] = s.sort_index().loc[start:end]
    return _CACHE[key]


def drop_duplicate_records(df):
    """Remove duplicate records: rows identical (open, high, low, close, volume) to the previous row."""
    cols = [c for c in ('open', 'high', 'low', 'close', 'volume') if c in df.columns]
    return df[~(df[cols] == df[cols].shift()).all(axis=1)]


def load_close(name, start=None, end=END):
    """Daily price, cleaned with the conventions of the chapter."""
    symbol, _, kind, start0 = MARKETS[name]
    start = start or start0
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start, end=end).rename(name)
    df = read_market(symbol).loc[start:end]
    if kind != 'crypto':
        df = df[df.index.dayofweek < 5]       # no weekend quotes
    if kind == 'index':
        df = drop_duplicate_records(df)       # no duplicate records
    s = df['close']
    s = s[s > 0].dropna()
    return s.rename(name)


def log_returns(name, start=None, end=END):
    """Log returns on the own calendar of the series."""
    return np.log(load_close(name, start, end)).diff().dropna().rename(name)


def periods_per_year(r):
    """Real frequency: average number of observations per calendar year."""
    return len(r) / ((r.index[-1] - r.index[0]).days / 365.25)


def asset_price(key, end=END):
    symbol, col = ASSETS[key]
    df = read_market(symbol).loc[:end]
    if key != 'BTC':
        df = df[df.index.dayofweek < 5]       # no weekend quotes
    if symbol.endswith('.INDX'):
        df = drop_duplicate_records(df)       # no duplicate records
    s = df[col]
    s = s[s > 0].dropna()
    return s.rename(key)


def joint_returns(keys, start=None, end=END):
    """Log returns for several assets: PRICES aligned on common days first, then returns."""
    p = pd.concat([asset_price(k, end) for k in keys], axis=1, join='inner').dropna()
    if start:
        p = p.loc[start:]
    return np.log(p).diff().dropna()

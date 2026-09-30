"""
mfm_data.py -- data for Chapter 5 (MFM): conditional volatility, GARCH models
=============================================================================
  * load_close(name)   -- daily closing price of the course data (or the BNR reference rate)
  * pct_returns(name)  -- daily log returns in percent, each series on its own calendar
  * periods_per_year() -- actual observation frequency (for annualisation)
  * MARKETS            -- S&P 500, BET, BET-TR, Bitcoin, EUR/RON, gold

Conventions (as in Chapters 1 and 2):
  * equity indices: weekdays only; days whose close equals the previous close
    (holidays filled with the last price) are dropped;
  * gold (XAU/USD): no weekend quotes; annualised with the actual frequency (about 260 days a year);
  * crypto: 7 days a week;
  * EUR/RON: the official BNR reference rate (the EUR/RON series from EODHD has erroneous quotes).

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

# name -> (symbol, label, group, start date)
MARKETS = {
    'sp500':  ('GSPC.INDX',      'S&P 500',                 'Equity', '2000-01-01'),
    'bet':    ('BET',            'BET',                     'Equity', '2000-01-01'),
    'bettr':  ('BETTR.INDX',     'BET-TR',                  'Equity', '2014-09-23'),
    'btc':    ('BTC-USD.CC',     'Bitcoin',                 'Crypto', '2014-09-17'),
    'eurron': ('REF:EUR',        'EUR/RON (BNR reference)', 'FX',     '2005-07-01'),
    'gold':   ('XAUUSD.FOREX',   'Gold (XAU/USD)',          'Commodity', '2000-01-01'),
}
LABELS = {k: v[1] for k, v in MARKETS.items()}

_CACHE = {}


def read_market(symbol):
    """Daily price table of one symbol (local copy of the course data, or GitHub)."""
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


def load_close(name, start=None, end=END):
    """Daily closing price, cleaned with the chapter conventions."""
    symbol, _, group, start0 = MARKETS[name]
    start = start or start0
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start, end=end).rename(name)
    s = read_market(symbol)['close'].loc[start:end]
    s = s[s > 0].dropna()
    if group != 'Crypto':
        s = s[s.index.dayofweek < 5]          # no weekend quotes
        s = s[s.diff() != 0]                  # no holidays filled with the previous price
    return s.rename(name)


def pct_returns(name, start=None, end=END):
    """Daily log returns in percent, on the series' own calendar."""
    return (100 * np.log(load_close(name, start, end)).diff().dropna()).rename(name)


def periods_per_year(r):
    """Average number of observations per calendar year (actual frequency of the series)."""
    years = (r.index[-1] - r.index[0]).days / 365.25
    return len(r) / years


def load_vix(start='2000-01-01', end=END):
    """The VIX index (30-day implied volatility of the S&P 500, annualised percent)."""
    s = read_market('VIX.INDX')['close'].loc[start:end]
    return s[s.index.dayofweek < 5].rename('vix')

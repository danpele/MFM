"""
mfm_data.py -- data for Chapter 5 (MFM): conditional volatility, GARCH models
=============================================================================
  * load_close(name)   -- daily closing price of the course data (or the BNR reference rate)
  * pct_returns(name)  -- daily log returns in percent, each series on its own calendar
  * periods_per_year() -- actual observation frequency (for annualisation)
  * MARKETS            -- S&P 500, BET, BET-TR, Bitcoin, EUR/RON, gold

Conventions (as in Chapters 1 and 2):
  * equity indices and gold: weekdays only; a row that repeats the previous close is dropped only if it
    shows no trading (zero volume, open = high = low = close, or a copy of the previous row): an artificial
    non-trading-day fill; a genuine unchanged close (zero return) is kept;
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
    d = read_market(symbol).loc[start:end]
    d = d[d['close'] > 0].dropna(subset=['close'])
    if group != 'Crypto':
        d = d[d.index.dayofweek < 5]          # no weekend quotes
        d = d[~artificial_fill(d)]            # non-trading days filled with the previous price
    return d['close'].rename(name)


def artificial_fill_reasons(d):
    """Heuristic flags for rows that repeat the previous close and show no sign of trading.

    The flags identify suspect rows; they do not prove that the market was closed: an unchanged close, a flat
    intraday range or a repeated row can also occur in a genuine session. Each excluded row keeps its reason
    (columns 'zero_volume', 'flat_range', 'copy_of_previous') so that it can be checked against the exchange
    calendar or the provider's metadata. A missing volume is unknown, not zero: only a reported volume <= 0 counts.
    Files with closes only (the BET) give no such evidence, so every row is kept.
    """
    repeat = d['close'].diff() == 0
    out = pd.DataFrame(False, index=d.index, columns=['zero_volume', 'flat_range', 'copy_of_previous'])
    if 'volume' in d and (d['volume'] > 0).mean() > 0.5:
        out['zero_volume'] = d['volume'].notna() & (d['volume'] <= 0)
    if {'open', 'high', 'low'} <= set(d.columns):
        out['flat_range'] = (d['open'] == d['high']) & (d['high'] == d['low']) & (d['low'] == d['close'])
        fields = [c for c in ['open', 'high', 'low', 'close', 'volume'] if c in d]
        out['copy_of_previous'] = (d[fields] == d[fields].shift()).all(axis=1)
    out = out & repeat.values[:, None]
    return out[out.any(axis=1)]


def artificial_fill(d):
    """Rows flagged by artificial_fill_reasons (a heuristic for non-trading days filled with the previous price)."""
    return pd.Series(d.index.isin(artificial_fill_reasons(d).index), index=d.index)


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

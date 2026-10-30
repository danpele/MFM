"""
mfm_data.py -- Data loading for Chapter 10 (MFM): market microstructure
=======================================================================
  * read_market(symbol)     -- daily price file of one symbol (local copy or repository)
  * ohlc(key, start, end)   -- ADJUSTED open, high, low, close (dividends, splits)
  * dollar_volume(key, ...) -- daily traded value in USD (unadjusted close x volume, on one share-count basis)
  * returns(key, ...)       -- daily log returns from the adjusted price
  * intraday_spy()          -- SPY 5-minute bars, regular session 09:30-16:00 (New York time)
  * intraday_btc()          -- Bitcoin 5-minute bars, 24/7 (UTC)
  * read_reference_rate()   -- BNR (National Bank of Romania) reference rate (USD/RON), to convert BVB values

Conventions:
  * stocks and ETFs: weekdays only; days without trading are dropped (high = low or zero volume);
  * crypto: 7 days a week; the daily volume of crypto-assets is already in USD;
  * stock volume is in number of shares adjusted by the provider for splits and bonus shares up to the end of the
    snapshot; the traded value divides the unadjusted close by the product of the documented share-count events
    after each day (SPLITS), computed over the whole snapshot before any window is selected, so that the value of a
    past trading day does not depend on the end of the window.

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

# key -> (symbol, label, group)
ASSETS = {
    'SPY': ('SPY.US', 'SPY', 'US'), 'AAPL': ('AAPL.US', 'Apple', 'US'), 'MSFT': ('MSFT.US', 'Microsoft', 'US'),
    'NVDA': ('NVDA.US', 'NVIDIA', 'US'), 'JPM': ('JPM.US', 'JPMorgan', 'US'), 'GME': ('GME.US', 'GameStop', 'US'),
    'MSTR': ('MSTR.US', 'Strategy', 'US'),
    'TLV': ('TLV.RO', 'Banca Transilvania', 'BVB'), 'SNP': ('SNP.RO', 'OMV Petrom', 'BVB'),
    'H2O': ('H2O.RO', 'Hidroelectrica', 'BVB'), 'BRD': ('BRD.RO', 'BRD', 'BVB'), 'SNG': ('SNG.RO', 'Romgaz', 'BVB'),
    'SNN': ('SNN.RO', 'Nuclearelectrica', 'BVB'), 'TGN': ('TGN.RO', 'Transgaz', 'BVB'),
    'EL': ('EL.RO', 'Electrica', 'BVB'), 'DIGI': ('DIGI.RO', 'Digi', 'BVB'), 'TEL': ('TEL.RO', 'Transelectrica', 'BVB'),
    'TVBETETF': ('TVBETETF.RO', 'BET ETF', 'BVB'),
    'BTC': ('BTC-USD.CC', 'Bitcoin', 'Crypto'), 'ETH': ('ETH-USD.CC', 'Ethereum', 'Crypto'),
    'SOL': ('SOL-USD.CC', 'Solana', 'Crypto'), 'XRP': ('XRP-USD.CC', 'XRP', 'Crypto'),
    'DOGE': ('DOGE-USD.CC', 'Dogecoin', 'Crypto'), 'ADA': ('ADA-USD.CC', 'Cardano', 'Crypto'),
    'LTC': ('LTC-USD.CC', 'Litecoin', 'Crypto'),
}
GROUPS = {g: [k for k, v in ASSETS.items() if v[2] == g] for g in ('US', 'BVB', 'Crypto')}
LABELS = {k: v[1] for k, v in ASSETS.items()}
# Share-count events (splits, consolidations, bonus shares) from the snapshot start (19 Sep 2016) onwards:
# (provider ex-date, shares after / shares before). The ratio is the provider's adjustment factor on that date;
# split_adjusted_close checks it against the data, so a wrong date or ratio stops the run.
#   AAPL 4-for-1 (31 Aug 2020); NVDA 4-for-1 (20 Jul 2021) and 10-for-1 (10 Jun 2024); GME 4-for-1 (22 Jul 2022);
#   MSTR 10-for-1 (8 Aug 2024): issuer announcements.
#   TLV.RO, Banca Transilvania: bonus shares every year (AGM resolutions, bancatransilvania.ro, investor relations),
#     e.g. 2023: 91,000,000 new shares on 707,658,233 (ratio 1.1286); 2026: 157,264,425 new shares (ratio 1.1442);
#     consolidation of the nominal value 10 to 1 on 16 Aug 2022 (ratio 0.1).
#   TGN.RO, Transgaz: bonus shares, 15 new for each share (2 May 2023, ratio 16).
#   SNG.RO, Romgaz: split 1 to 10 (28 May 2024).
#   DIGI.RO, Digi Communications: bonus shares raising the share count to 300 million (7 Apr 2026, ratio 3).
# All other adjustment days of the provider (cash dividends) leave the share count unchanged.
SPLITS = {
    'AAPL.US': [('2020-08-31', 4.0)],
    'NVDA.US': [('2021-07-20', 4.0), ('2024-06-10', 10.0)],
    'GME.US': [('2022-07-22', 4.0)],
    'MSTR.US': [('2024-08-08', 10.0)],
    'TLV.RO': [('2017-08-03', 1.2157), ('2018-08-02', 1.1085), ('2019-08-01', 1.0833), ('2020-10-14', 1.0999),
               ('2021-09-09', 1.1000), ('2022-07-12', 1.1211), ('2022-08-16', 0.1), ('2023-07-20', 1.1286),
               ('2024-07-18', 1.1480), ('2025-07-17', 1.1892), ('2026-07-13', 1.1442)],
    'TGN.RO': [('2023-05-02', 16.0)],
    'SNG.RO': [('2024-05-28', 10.0)],
    'DIGI.RO': [('2026-04-07', 3.0)],
}

_CACHE = {}


def read_market(symbol):
    """Read the daily price file of one symbol, from a local copy or from the GitHub repository."""
    if symbol in _CACHE:
        return _CACHE[symbol]
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    _CACHE[symbol] = pd.read_csv(src, index_col='date', parse_dates=True).sort_index()
    return _CACHE[symbol]


def read_reference_rate(currency='USD', start='2014-01-01', end=END):
    """Official RON reference rate (BNR yearly XML archives)."""
    key = ('REF', currency, start, end)
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
    s = pd.DataFrame(rows, columns=['date', 'rate']).drop_duplicates('date').set_index('date')['rate']
    s.index = pd.to_datetime(s.index)
    _CACHE[key] = s.sort_index().loc[start:end]
    return _CACHE[key]


def _clean(key, d):
    d = d[(d['high'] > d['low']) & (d['volume'].fillna(0) > 0)]
    if ASSETS[key][2] != 'Crypto':
        d = d[d.index.dayofweek < 5]
        # isolated bad ticks: adjusted price more than twice / less than half the local median (21 days)
        med = d['adjusted_close'].rolling(21, center=True, min_periods=5).median()
        d = d[np.abs(np.log(d['adjusted_close'] / med)) < np.log(2)]
    return d


def ohlc(key, start='2016-09-19', end=END):
    """Open, high, low, close scaled by the adjustment factor of the adjusted price (dividends and splits)."""
    d = read_market(ASSETS[key][0]).loc[start:end].copy()
    f = d['adjusted_close'] / d['close']
    for c in ['open', 'high', 'low', 'close']:
        d[c] = d[c] * f
    return _clean(key, d)[['open', 'high', 'low', 'close', 'volume']]


def split_adjusted_close(d, symbol=None):
    """Close price on the share-count basis of the end of the snapshot (the basis of the volume): the unadjusted close
    divided by the product of the documented events in SPLITS after each day. d must be the whole snapshot."""
    k = pd.Series(1.0, index=d.index)
    f = (d['close'].shift(1) / d['close']) / (d['adjusted_close'].shift(1) / d['adjusted_close'])
    for day, ratio in SPLITS.get(symbol, []):
        t = pd.Timestamp(day)
        if t < d.index[0] or t > d.index[-1]:
            continue
        assert t in d.index and abs(np.log(f.loc[t] / ratio)) < 0.005, (symbol, day, ratio)
        k.loc[t] = ratio
    back = k[::-1].cumprod()[::-1].shift(-1).fillna(1.0)          # product of the events after each day
    return d['close'] / back


def returns(key, start='2016-09-19', end=END):
    """Daily log returns from the adjusted price (days without trading dropped)."""
    d = read_market(ASSETS[key][0]).loc[start:end]
    d = _clean(key, d)
    return np.log(d['adjusted_close']).diff().dropna().rename(key)


def dollar_volume(key, start='2016-09-19', end=END):
    """Daily traded value, in USD; the price-volume basis is fixed on the whole snapshot, then the window is selected."""
    d = read_market(ASSETS[key][0])
    grp = ASSETS[key][2]
    if grp == 'Crypto':
        dv = d['volume']                                          # already in USD
    else:
        dv = split_adjusted_close(d, ASSETS[key][0]) * d['volume']
        if grp == 'BVB':                                          # RON -> USD at the BNR reference rate
            fx = read_reference_rate('USD', start='2014-01-01', end=END)
            dv = dv / fx.reindex(dv.index).ffill()
    d = _clean(key, d.assign(dv=dv))
    return d['dv'].loc[start:end].dropna().rename(key)


def intraday_spy():
    """SPY 5-minute bars, regular session (09:30-15:55 = bar start), complete days only (78 bars)."""
    fname = 'intraday/SPY.US_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    d = pd.read_csv(path if os.path.exists(path) else REPO_RAW + fname, parse_dates=['datetime_utc'])
    t = d['datetime_utc'].dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)
    d = d.assign(t=t, date=t.dt.normalize(), tod=t.dt.strftime('%H:%M')).drop(columns='datetime_utc')
    d = d[(d['tod'] >= '09:30') & (d['tod'] <= '15:55')]
    n = d.groupby('date').size()
    d = d[d['date'].isin(n[n == 78].index)].set_index('t').sort_index()
    d['r'] = np.log(d['close']).groupby(d['date']).diff()
    first = d['tod'] == '09:30'
    d.loc[first, 'r'] = np.log(d.loc[first, 'close'] / d.loc[first, 'open'])   # first bar: from the open
    d['dv'] = d['close'] * d['volume']
    return d


def intraday_btc():
    """Bitcoin 5-minute bars (UTC), 24 hours a day; volume is not used (missing on many bars)."""
    fname = 'intraday/BTC-USD.CC_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    d = pd.read_csv(path if os.path.exists(path) else REPO_RAW + fname, parse_dates=['datetime_utc'])
    d = d.set_index('datetime_utc').sort_index()
    d = d[~d.index.duplicated()]
    d['date'] = d.index.normalize()
    d['r'] = np.log(d['close']).diff()
    gap = d.index.to_series().diff() != pd.Timedelta('5min')
    d.loc[gap, 'r'] = np.nan                                       # no returns across missing bars
    return d

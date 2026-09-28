"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 19 (MFM): recapitulare si studiu de caz integrat
===============================================================================================
  * load_close(name)    -- pretul zilnic din data/market/ (sau cursul de referinta BNR)
  * log_returns(name)   -- randamente log pe calendarul propriu al fiecarei serii
  * joint_returns(...)  -- randamente pentru un portofoliu: intai join pe PRETURI in zilele comune
  * MARKETS             -- S&P 500, BET, Bitcoin, EUR/RON, aur; ETF-uri si actiuni BVB pentru portofolii

Conventii (ca in capitolele 0-8):
  * indicii bursieri: doar zilele lucratoare; zilele cu inchidere identica cu ziua precedenta
    (sarbatori completate cu ultimul pret) sunt eliminate;
  * aurul (XAU/USD): fara cotatiile de weekend; anualizare cu frecventa reala;
  * cripto: 7 zile din 7;
  * ETF-uri si actiuni: pretul ajustat (dividende, split-uri); indici, FX, cripto: pretul de inchidere;
  * EUR/RON: cursul oficial de referinta BNR.

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import re
import urllib.request
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'

# nume -> (simbol, eticheta, tip, data de start)
MARKETS = {
    'sp500':  ('GSPC.INDX',    'S&P 500',                  'index',  '2000-01-01'),
    'bet':    ('BET',          'BET',                      'index',  '2000-01-01'),
    'btc':    ('BTC-USD.CC',   'Bitcoin',                  'crypto', '2014-09-17'),
    'eurron': ('REF:EUR',      'EUR/RON (reference rate)', 'fx',     '2005-07-01'),
    'gold':   ('XAUUSD.FOREX', 'Gold (XAU/USD)',           'fx',     '2000-01-01'),
}
# active pentru portofolii (join pe preturi in zilele comune)
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
    """Citeste data/market/<SIMBOL>.csv local sau din repo-ul GitHub."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def read_reference_rate(currency='EUR', start='2005-07-01', end=END):
    """Cursul oficial de referinta RON (arhive XML anuale BNR)."""
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
    """Elimina inregistrarile duplicate: randuri identice (open, high, low, close, volume) cu randul anterior."""
    cols = [c for c in ('open', 'high', 'low', 'close', 'volume') if c in df.columns]
    return df[~(df[cols] == df[cols].shift()).all(axis=1)]


def load_close(name, start=None, end=END):
    """Pretul zilnic, curatat dupa conventiile capitolului."""
    symbol, _, kind, start0 = MARKETS[name]
    start = start or start0
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start, end=end).rename(name)
    df = read_market(symbol).loc[start:end]
    if kind != 'crypto':
        df = df[df.index.dayofweek < 5]       # fara cotatii de weekend
    if kind == 'index':
        df = drop_duplicate_records(df)       # fara inregistrari duplicate
    s = df['close']
    s = s[s > 0].dropna()
    return s.rename(name)


def log_returns(name, start=None, end=END):
    """Randamente log pe calendarul propriu al seriei."""
    return np.log(load_close(name, start, end)).diff().dropna().rename(name)


def periods_per_year(r):
    """Frecventa reala: numarul mediu de observatii pe an calendaristic."""
    return len(r) / ((r.index[-1] - r.index[0]).days / 365.25)


def asset_price(key, end=END):
    symbol, col = ASSETS[key]
    df = read_market(symbol).loc[:end]
    if key != 'BTC':
        df = df[df.index.dayofweek < 5]       # fara cotatii de weekend
    if symbol.endswith('.INDX'):
        df = drop_duplicate_records(df)       # fara inregistrari duplicate
    s = df[col]
    s = s[s > 0].dropna()
    return s.rename(key)


def joint_returns(keys, start=None, end=END):
    """Randamente log simple pentru mai multe active: join pe PRETURI in zilele comune, apoi randamente."""
    p = pd.concat([asset_price(k, end) for k in keys], axis=1, join='inner').dropna()
    if start:
        p = p.loc[start:]
    return np.log(p).diff().dropna()

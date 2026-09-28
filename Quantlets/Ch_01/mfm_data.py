"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 1 (MFM): fapte stilizate
==========================================================================
  * load_data(name)  -- OHLCV zilnic din data/market/ sau cursul oficial de referinta EUR/RON
  * log_returns      -- randamente logaritmice curatate
  * vol estimators   -- close-to-close, Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')

# nume -> (simbol, coloana de pret, data de start)
# Date zilnice de piata din data/market/<SIMBOL>.csv; EUR/RON: cursul oficial de referinta.
SOURCES = {
    'sp500':  ('GSPC.INDX',    'close', '1990-01-01'),
    'bettr':  ('BETTR.INDX',   'close', '2014-09-01'),
    'btc':    ('BTC-USD.CC',   'close', '2014-09-17'),
    'eurron': ('REF:EUR',      'close', '2005-07-01'),   # de la introducerea leului nou (RON), 1 iulie 2005
    'gold':   ('XAUUSD.FOREX', 'close', '1990-01-01'),
}

LABELS = {'sp500': 'S&P 500', 'bettr': 'BET-TR (Romania)', 'btc': 'Bitcoin',
          'eurron': 'EUR/RON', 'gold': 'Gold'}

# cotatii OTC (aur): sesiunile partiale de sambata/duminica rup randamentul vineri -> luni,
# deci pastram doar zilele lucratoare (aceeasi conventie ca in Capitolul 0)
WEEKDAYS_ONLY = {'gold'}

_CACHE = {}


def read_market(symbol):
    """Citeste data/market/<SIMBOL>.csv local sau din repo-ul GitHub."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    df = pd.read_csv(src, parse_dates=['date']).set_index('date').sort_index()
    df.index.name = 'Date'
    return df


def read_reference_rate(currency='EUR', start='2005-07-01', end='2026-09-18'):
    """Cursul oficial de referinta RON (arhive XML anuale BNR)."""
    key = (currency, start, end)
    if key in _CACHE:
        return _CACHE[key]
    import re
    import urllib.request
    rows = []
    for y in range(int(start[:4]), int(end[:4]) + 1):
        url = f'https://curs.bnr.ro/files/xml/years/nbrfxrates{y}.xml'
        xml = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla'}),
                                     timeout=60).read().decode()
        for d, body in re.findall(r'<Cube date="([\d-]+)">(.*?)</Cube>', xml, re.S):
            m = re.search(rf'<Rate currency="{currency}">([\d.]+)</Rate>', body)
            if m:
                rows.append((d, float(m.group(1))))
    df = pd.DataFrame(rows, columns=['Date', 'Close']).drop_duplicates('Date').set_index('Date')
    df.index = pd.to_datetime(df.index)
    _CACHE[key] = df.sort_index().loc[start:end]
    return _CACHE[key]


def load_data(name='sp500'):
    """OHLCV zilnic cu coloane Open/High/Low/Close/Volume (Close = pretul folosit)."""
    symbol, col, start = SOURCES[name]
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start)
    d = read_market(symbol).loc[start:]
    if name in WEEKDAYS_ONLY:
        d = d[d.index.dayofweek < 5]
    out = pd.DataFrame({'Open': d['open'], 'High': d['high'], 'Low': d['low'],
                        'Close': d[col], 'Volume': d['volume']})
    return out[out['Close'] > 0].dropna(subset=['Close'])


def log_returns(close, max_abs=None):
    """Randamente log; optional elimina erori de date (|r| > max_abs, ex. cotatii FX gresite)."""
    r = np.log(close).diff().dropna()
    if max_abs is not None:
        r = r[r.abs() < max_abs]
    return r


# =============================================================================
# ESTIMATORI DE VOLATILITATE (anualizati, fereastra rulanta n zile)
# =============================================================================
def vol_close_to_close(df, n=21, periods=252):
    r = np.log(df['Close']).diff()
    return r.rolling(n).std() * np.sqrt(periods)


def vol_parkinson(df, n=21, periods=252):
    hl = np.log(df['High'] / df['Low']) ** 2
    return np.sqrt(hl.rolling(n).mean() / (4 * np.log(2)) * periods)


def vol_garman_klass(df, n=21, periods=252):
    hl = np.log(df['High'] / df['Low']) ** 2
    co = np.log(df['Close'] / df['Open']) ** 2
    v = 0.5 * hl - (2 * np.log(2) - 1) * co
    return np.sqrt(v.rolling(n).mean() * periods)


def vol_rogers_satchell(df, n=21, periods=252):
    ho, hc = np.log(df['High'] / df['Open']), np.log(df['High'] / df['Close'])
    lo, lc = np.log(df['Low'] / df['Open']), np.log(df['Low'] / df['Close'])
    return np.sqrt((ho * hc + lo * lc).rolling(n).mean() * periods)


def vol_yang_zhang(df, n=21, periods=252):
    o = np.log(df['Open'] / df['Close'].shift(1))          # overnight
    c = np.log(df['Close'] / df['Open'])                   # open-to-close
    ho, hc = np.log(df['High'] / df['Open']), np.log(df['High'] / df['Close'])
    lo, lc = np.log(df['Low'] / df['Open']), np.log(df['Low'] / df['Close'])
    rs = (ho * hc + lo * lc).rolling(n).mean()
    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    v = o.rolling(n).var() + k * c.rolling(n).var() + (1 - k) * rs
    return np.sqrt(v * periods)


def drawdown(close):
    """Drawdown procentual fata de maximul anterior."""
    return close / close.cummax() - 1



def load_close(name):
    """Pretul de inchidere, folosit in toate graficele."""
    return load_data(name)['Close'].dropna()

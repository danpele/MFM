"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 5 (MFM): volatilitate conditionata, modele GARCH
===================================================================================================
  * load_close(name)   -- pretul de inchidere zilnic din data/market/ (sau cursul de referinta BNR)
  * pct_returns(name)  -- randamente log zilnice in procente, pe calendarul propriu al fiecarei serii
  * periods_per_year() -- frecventa reala a observatiilor (pentru anualizare)
  * MARKETS            -- S&P 500, BET, BET-TR, Bitcoin, EUR/RON, aur

Conventii (ca in capitolele 1 si 2):
  * indicii bursieri: doar zilele lucratoare; zilele cu inchidere identica cu ziua precedenta
    (sarbatori completate cu ultimul pret) sunt eliminate;
  * aur (XAU/USD): fara cotatiile de weekend; anualizare cu frecventa reala (aprox. 260 de zile pe an);
  * cripto: 7 zile din 7;
  * EUR/RON: cursul oficial de referinta BNR (seria EODHD are cotatii eronate).

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

# nume -> (simbol, eticheta, grup, data de start)
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


def load_close(name, start=None, end=END):
    """Pretul de inchidere zilnic, curatat dupa conventiile capitolului."""
    symbol, _, group, start0 = MARKETS[name]
    start = start or start0
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start, end=end).rename(name)
    s = read_market(symbol)['close'].loc[start:end]
    s = s[s > 0].dropna()
    if group != 'Crypto':
        s = s[s.index.dayofweek < 5]          # fara cotatii de weekend
        s = s[s.diff() != 0]                  # fara sarbatori completate cu pretul anterior
    return s.rename(name)


def pct_returns(name, start=None, end=END):
    """Randamente log zilnice, in procente, pe calendarul propriu al seriei."""
    return (100 * np.log(load_close(name, start, end)).diff().dropna()).rename(name)


def periods_per_year(r):
    """Numarul mediu de observatii pe an calendaristic (frecventa reala a seriei)."""
    years = (r.index[-1] - r.index[0]).days / 365.25
    return len(r) / years


def load_vix(start='2000-01-01', end=END):
    """Indicele VIX (volatilitatea implicita pe 30 de zile a S&P 500, in procente anualizate)."""
    s = read_market('VIX.INDX')['close'].loc[start:end]
    return s[s.index.dayofweek < 5].rename('vix')

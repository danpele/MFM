"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 11 (MFM): modele in timp continuu
===================================================================================
  * load_close(name)   -- pretul zilnic din data/market/ (sau cursul de referinta BNR)
  * log_returns(name)  -- randamente log pe calendarul propriu al fiecarei serii
  * load_vix()         -- indicele VIX (CBOE), nivel zilnic
  * read_fred(series)  -- serii publice FRED (de ex. DTB3, randamentul titlurilor de stat pe 3 luni)

Conventii (ca in capitolele 0-8):
  * indicii bursieri: doar zilele lucratoare; cotatiile inerte (inchidere identica cu ziua precedenta si
    fara amplitudine intraday, high = low, sau fara high/low) sunt eliminate; o inchidere neschimbata intr-o zi
    cu tranzactii reale (high > low) este pastrata ca randament zero;
  * cripto: 7 zile din 7; ETF-uri si actiuni: pretul ajustat; indici, FX, cripto: pretul de inchidere;
  * EUR/RON: cursul oficial de referinta BNR.

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import re
import io
import urllib.request
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'

# nume -> (simbol, eticheta, tip, data de start)
MARKETS = {
    'sp500':  ('GSPC.INDX',  'S&P 500',                  'index',  '1990-01-01'),
    'bet':    ('BET',        'BET',                      'index',  '2000-01-01'),
    'btc':    ('BTC-USD.CC', 'Bitcoin',                  'crypto', '2014-09-17'),
    'eurron': ('REF:EUR',    'EUR/RON (reference rate)', 'fx',     '2005-07-01'),
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
    key = ('bnr', currency, start, end)
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


def read_fred(series, start='1954-01-01', end=END):
    """Serie zilnica FRED (Federal Reserve Bank of St. Louis), in unitatile originale."""
    key = ('fred', series, start, end)
    if key in _CACHE:
        return _CACHE[key]
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}'
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(url, timeout=120).read().decode()
            break
        except OSError:
            if attempt == 3:
                raise
    df = pd.read_csv(io.StringIO(raw), index_col=0, parse_dates=True, na_values='.')
    s = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().loc[start:end].rename(series)
    _CACHE[key] = s
    return s


def load_close(name, start=None, end=END):
    """Pretul zilnic, curatat dupa conventiile capitolului."""
    symbol, _, kind, start0 = MARKETS[name]
    start = start or start0
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start, end=end).rename(name)
    d = read_market(symbol).loc[start:end]
    d = d[d['close'] > 0].dropna(subset=['close'])
    if kind != 'crypto':
        d = d[d.index.dayofweek < 5]          # fara cotatii de weekend
    s = d['close']
    if kind == 'index':
        # cotatie inerta: inchidere neschimbata si nicio amplitudine intraday (sau high/low indisponibile)
        no_range = (d['high'] <= d['low']) if {'high', 'low'} <= set(d.columns) else pd.Series(True, index=d.index)
        s = s[~((s.diff() == 0) & no_range)]
    return s.rename(name)


def log_returns(name, start=None, end=END):
    """Randamente log pe calendarul propriu al seriei."""
    return np.log(load_close(name, start, end)).diff().dropna().rename(name)


def periods_per_year(r):
    """Frecventa reala: numarul mediu de observatii pe an calendaristic."""
    return len(r) / ((r.index[-1] - r.index[0]).days / 365.25)


def load_vix(start='1990-01-01', end=END):
    """Indicele VIX (CBOE), nivelul zilnic de inchidere, in puncte de volatilitate anualizata (%)."""
    s = read_market('VIX.INDX')['close'].loc[start:end]
    s = s[(s > 0) & (s.index.dayofweek < 5)].dropna()
    return s.rename('vix')


def load_spy_5m(end=END):
    """Bare de 5 minute SPY (data/market/intraday), sesiunea 09:30-16:00 ora New York, doar zilele complete
    (78 de bare). Randamente log: primul randament al zilei = close/open al primei bare, apoi close/close."""
    fname = 'intraday/SPY.US_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    d = pd.read_csv(src, index_col='datetime_utc', parse_dates=True).sort_index()
    d = d.dropna(subset=['open', 'close'])
    d = d[~d.index.duplicated()]
    d.index = d.index.tz_localize('UTC').tz_convert('America/New_York')
    mins = d.index.hour * 60 + d.index.minute
    d = d[(mins >= 570) & (mins < 960)]
    day = pd.Index(d.index.date)
    full = day.value_counts()
    d = d[day.isin(full[full == 78].index)]
    d = d[d.index.date <= pd.Timestamp(end).date()]
    day = d.index.date
    lc, lo = np.log(d['close'].values), np.log(d['open'].values)
    r = np.r_[np.nan, np.diff(lc)]
    first = np.r_[True, day[1:] != day[:-1]]
    r[first] = lc[first] - lo[first]
    return pd.Series(r, index=d.index, name='spy_5m')

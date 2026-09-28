"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 10 (MFM): microstructura pietei
==================================================================================
  * read_market(symbol)     -- fisierul zilnic data/market/<SIMBOL>.csv (local sau din repo)
  * ohlc(key, start, end)   -- deschidere, maxim, minim, inchidere AJUSTATE (dividende, split-uri)
  * dollar_volume(key, ...) -- valoarea tranzactionata zilnic in USD (pret ajustat doar pentru split-uri x volum)
  * returns(key, ...)       -- randamente log zilnice din pretul ajustat
  * intraday_spy()          -- bare de 5 minute SPY, sesiunea regulata 09:30-16:00 (ora New York)
  * intraday_btc()          -- bare de 5 minute Bitcoin, 24/7 (UTC)
  * read_reference_rate()   -- cursul de referinta BNR (USD/RON), pentru conversia valorilor BVB

Conventii:
  * actiuni si ETF-uri: doar zilele lucratoare; se elimina zilele fara tranzactii (maxim = minim sau volum zero);
  * cripto: 7 zile din 7; volumul zilnic al cripto-activelor este deja exprimat in USD;
  * volumul actiunilor este in numar de actiuni, pe aceeasi baza ca pretul ajustat pentru split-uri.

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

# cheie -> (simbol, eticheta, grup)
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
# evenimente de ajustare mari care sunt dividende in numerar, nu split-uri (verificate la emitent):
#   SNN.RO 2018-12-21: dividend brut de 1,61 lei pe actiune, data ex 21.12.2018
#   (https://www.nuclearelectrica.ro/wp-content/uploads/2018/12/SNN_Comunicat-plata-dividende-suplimentare_EN.pdf)
CASH_DIVIDENDS = {'SNN.RO': ['2018-12-21']}

_CACHE = {}


def read_market(symbol):
    """Citeste data/market/<SIMBOL>.csv local sau din repo-ul GitHub."""
    if symbol in _CACHE:
        return _CACHE[symbol]
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    _CACHE[symbol] = pd.read_csv(src, index_col='date', parse_dates=True).sort_index()
    return _CACHE[symbol]


def read_reference_rate(currency='USD', start='2014-01-01', end=END):
    """Cursul oficial de referinta RON (arhive XML anuale BNR)."""
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
        # cotatii eronate izolate: pretul ajustat de peste doua ori mai mare / mai mic decat mediana locala (21 de zile)
        med = d['adjusted_close'].rolling(21, center=True, min_periods=5).median()
        d = d[np.abs(np.log(d['adjusted_close'] / med)) < np.log(2)]
    return d


def ohlc(key, start='2016-09-19', end=END):
    """Deschidere, maxim, minim, inchidere ajustate cu factorul pretului ajustat (dividende si split-uri)."""
    d = read_market(ASSETS[key][0]).loc[start:end].copy()
    f = d['adjusted_close'] / d['close']
    for c in ['open', 'high', 'low', 'close']:
        d[c] = d[c] * f
    return _clean(key, d)[['open', 'high', 'low', 'close', 'volume']]


def split_adjusted_close(d, symbol=None):
    """Pretul de inchidere ajustat DOAR pentru split-uri si actiuni gratuite (aceeasi baza ca volumul in numar de
    actiuni); dividendele in numerar mari din CASH_DIVIDENDS nu sunt tratate ca split-uri."""
    k = (d['close'].shift(1) / d['close']) / (d['adjusted_close'].shift(1) / d['adjusted_close'])
    k = k.where(np.abs(np.log(k)) > 0.15, 1.0).fillna(1.0)      # zilele de split: raportul de divizare
    for day in CASH_DIVIDENDS.get(symbol, []):
        k.loc[k.index == pd.Timestamp(day)] = 1.0
    back = k[::-1].cumprod()[::-1].shift(-1).fillna(1.0)          # produsul split-urilor ulterioare fiecarei zile
    return d['close'] / back


def returns(key, start='2016-09-19', end=END):
    """Randamente log zilnice din pretul ajustat (zilele fara tranzactii eliminate)."""
    d = read_market(ASSETS[key][0]).loc[start:end]
    d = _clean(key, d)
    return np.log(d['adjusted_close']).diff().dropna().rename(key)


def dollar_volume(key, start='2016-09-19', end=END):
    """Valoarea tranzactionata zilnic, in USD."""
    d = read_market(ASSETS[key][0]).loc[:end]
    grp = ASSETS[key][2]
    if grp == 'Crypto':
        dv = d['volume']                                          # deja in USD
    else:
        dv = split_adjusted_close(d, ASSETS[key][0]) * d['volume']
        if grp == 'BVB':                                          # RON -> USD la cursul de referinta BNR
            fx = read_reference_rate('USD', start='2014-01-01', end=end)
            dv = dv / fx.reindex(dv.index).ffill()
    d = _clean(key, d.assign(dv=dv))
    return d['dv'].loc[start:end].dropna().rename(key)


def intraday_spy():
    """Bare de 5 minute SPY, sesiunea regulata (09:30-15:55 = inceputul barei), doar zilele complete (78 de bare)."""
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
    d.loc[first, 'r'] = np.log(d.loc[first, 'close'] / d.loc[first, 'open'])   # prima bara: de la deschidere
    d['dv'] = d['close'] * d['volume']
    return d


def intraday_btc():
    """Bare de 5 minute Bitcoin (UTC), 24 de ore din 24; volumul nu este folosit (lipseste pe multe bare)."""
    fname = 'intraday/BTC-USD.CC_5m.csv'
    path = os.path.join(MARKET_DIR, fname)
    d = pd.read_csv(path if os.path.exists(path) else REPO_RAW + fname, parse_dates=['datetime_utc'])
    d = d.set_index('datetime_utc').sort_index()
    d = d[~d.index.duplicated()]
    d['date'] = d.index.normalize()
    d['r'] = np.log(d['close']).diff()
    gap = d.index.to_series().diff() != pd.Timedelta('5min')
    d.loc[gap, 'r'] = np.nan                                       # fara randamente peste goluri
    return d

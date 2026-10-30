"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 18 (MFM): risc sistemic si retele
=====================================================================================
  * bank_price(key)      -- pretul ajustat zilnic al unei banci din data/market/
  * index_close(key)     -- indicii S&P 500, Euro Stoxx 50, BET si VIX (pret de inchidere)
  * joint_returns(keys)  -- randamente log (%) intre date comune: intai join pe PRETURI in zilele comune, apoi
                           randamente; un randament acopera mai multe sedinte cand o piata a fost deschisa intr-o zi
                           eliminata din intersectie (orizont variabil, nu exclusiv o zi)
  * bank_range_vol(keys) -- volatilitatea zilnica Parkinson din maximul si minimul zilei

Conventii:
  * actiuni: pretul ajustat (dividende, split-uri); indici: pretul de inchidere; doar zilele lucratoare;
  * actiunile BVB (TLV, BRD): fara zilele fara tranzactii (volum zero); analiza incepe in 2010;
  * Parkinson: zilele cu maxim = minim (interval nul, de regula cu volum pozitiv: o zi cu tranzactii, nu o zi
    fara tranzactii) dau log 0; varianta lor este regularizata cu minimul pozitiv observat pana la acea zi (fara
    informatie ulterioara), deci acele valori sunt imputate, nu estimari Parkinson observate. Alternativa
    zero_range='drop' elimina acele zile (analiza de sensibilitate in inference18.py, etapa 'diag');
  * Banca Transilvania: ajustarea pentru actiunile gratuite din 2016 este aplicata de la data ex (30 mai 2016).

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
START = '2010-01-01'
END = '2026-09-18'

# bank -> (symbol, name, region)
BANKS = {
    'JPM':  ('JPM.US',    'JPMorgan Chase',       'US'),
    'BAC':  ('BAC.US',    'Bank of America',      'US'),
    'C':    ('C.US',      'Citigroup',            'US'),
    'GS':   ('GS.US',     'Goldman Sachs',        'US'),
    'MS':   ('MS.US',     'Morgan Stanley',       'US'),
    'WFC':  ('WFC.US',    'Wells Fargo',          'US'),
    'DBK':  ('DBK.XETRA', 'Deutsche Bank',        'EU'),
    'BNP':  ('BNP.PA',    'BNP Paribas',          'EU'),
    'SAN':  ('SAN.MC',    'Santander',            'EU'),
    'INGA': ('INGA.AS',   'ING',                  'EU'),
    'HSBA': ('HSBA.LSE',  'HSBC',                 'EU'),
    'TLV':  ('TLV.RO',    'Banca Transilvania',   'RO'),
    'BRD':  ('BRD.RO',    'BRD-Groupe SG',        'RO'),
}
US = [k for k, v in BANKS.items() if v[2] == 'US']
EU = [k for k, v in BANKS.items() if v[2] == 'EU']
RO = [k for k, v in BANKS.items() if v[2] == 'RO']
ALL = US + EU + RO
NAMES = {k: v[1] for k, v in BANKS.items()}
INDICES = {'SPX': ('GSPC.INDX', 'S&P 500'), 'SX5E': ('STOXX50E.INDX', 'Euro Stoxx 50'),
           'BET': ('BET', 'BET'), 'VIX': ('VIX.INDX', 'VIX')}
REGION_INDEX = {'US': 'SPX', 'EU': 'SX5E', 'RO': 'BET'}


def read_market(symbol):
    """Read the daily price series of one symbol from the course data."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def bank_frame(key, start=START, end=END):
    """Daily prices and volume of one bank, with the adjusted price and the corrections above."""
    symbol, _, region = BANKS[key]
    d = read_market(symbol).loc[start:end].copy()
    d = d[(d.index.dayofweek < 5) & (d['adjusted_close'] > 0)]
    if region == 'RO':
        d = d[d['volume'] > 0]                                   # days without trades
    if key == 'TLV' and pd.Timestamp('2016-05-30') in d.index:
        # bonus-share adjustment: the post-ex-date factor also applies on 30 May 2016
        f = d.loc['2016-05-31', 'adjusted_close'] / d.loc['2016-05-31', 'close']
        d.loc['2016-05-30', 'adjusted_close'] = d.loc['2016-05-30', 'close'] * f
    return d


def bank_price(key, start=START, end=END):
    return bank_frame(key, start, end)['adjusted_close'].rename(key)


def index_close(key, start=START, end=END):
    d = read_market(INDICES[key][0]).loc[start:end]
    d = d[(d.index.dayofweek < 5) & (d['close'] > 0)].dropna(subset=['close'])
    if key != 'VIX':
        d = d[~artificial_fill(d)]                               # non-trading days filled with the previous price
    return d['close'].rename(key)


def artificial_fill(d):
    """Rows that repeat the previous close and show no trading: an artificial non-trading-day fill.

    A repeated close is a fill only if the row itself shows no trading: zero volume (for files that report
    volume), no intraday range (open = high = low = close) or a copy of the previous row in every field. A
    repeated close on a day with volume and an intraday range is a genuine unchanged close (a zero return)
    and is kept. Files with closes only (the BET) give no such evidence, so every row is kept.
    """
    repeat = d['close'].diff() == 0
    no_trade = pd.Series(False, index=d.index)
    if 'volume' in d and (d['volume'] > 0).mean() > 0.5:
        no_trade |= d['volume'].fillna(0) <= 0
    if {'open', 'high', 'low'} <= set(d.columns):
        no_trade |= (d['open'] == d['high']) & (d['high'] == d['low']) & (d['low'] == d['close'])
        fields = [c for c in ['open', 'high', 'low', 'close', 'volume'] if c in d]
        no_trade |= (d[fields] == d[fields].shift()).all(axis=1)
    return repeat & no_trade


def prices(keys, start=START, end=END):
    """Daily prices of banks and/or indices, on common trading days only."""
    cols = [bank_price(k, start, end) if k in BANKS else index_close(k, start, end) for k in keys]
    return pd.concat(cols, axis=1, join='inner').dropna()


def joint_returns(keys, start=START, end=END):
    """Log returns in % between common dates: prices are aligned on common trading days first, then returns are
    computed. A return spans several sessions of a market that traded on dates dropped from the intersection."""
    return 100 * np.log(prices(keys, start, end)).diff().dropna()


def bank_range_vol(keys, start=START, end=END, zero_range='floor'):
    """Daily Parkinson volatility (in %, annualised), on the days common to all banks.

    Days with high = low (zero range) or a missing range: zero_range='floor' replaces the variance by the smallest
    positive value observed up to that day (a regularisation before taking logs, no look-ahead; imputed values, not
    observed Parkinson estimates); zero_range='drop' removes those days."""
    out = []
    for k in keys:
        d = bank_frame(k, start, end)
        rng = np.log(d['high'] / d['low']).where(d['high'] > d['low'])
        s2 = rng ** 2 / (4 * np.log(2))
        if zero_range == 'floor':
            floor = s2.where(s2 > 0).cummin().ffill()              # smallest positive value observed UP TO day t
            s2 = s2.fillna(floor)
        out.append((100 * np.sqrt(252 * s2)).rename(k))
    return pd.concat(out, axis=1, join='inner').dropna()


def system_return(R, members):
    """System return: equal-weighted portfolio of the banks (log returns in %, daily approximation)."""
    return R[members].mean(axis=1)

"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 4 (MFM): optimizarea portofoliului
====================================================================================
  * read_market(symbol)     -- data/market/<SIMBOL>.csv
  * prices(symbols)         -- preturi ajustate (ETF/actiuni) sau de inchidere (indici), join pe zilele comune
  * french_rf()             -- rata fara risc lunara (Kenneth French Data Library)
  * bnr_rate(currency)      -- cursul oficial de referinta BNR (RON pentru o unitate de valuta)

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import io
import os
import re
import zipfile
import urllib.request

import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
FRENCH = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'
BNR_XML = 'https://curs.bnr.ro/files/xml/years/nbrfxrates{}.xml'

SECTORS = ['XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY']        # din dec. 1998
SECTOR_NAMES = {'XLB': 'Materials', 'XLE': 'Energy', 'XLF': 'Financials', 'XLI': 'Industrials',
                'XLK': 'Technology', 'XLP': 'Cons. staples', 'XLU': 'Utilities', 'XLV': 'Health care',
                'XLY': 'Cons. discretionary'}
MULTI = ['SPY', 'EFA', 'EEM', 'TLT', 'IEF', 'LQD', 'HYG', 'GLD']                  # HYG din apr. 2007
MULTI_NAMES = {'SPY': 'US equities', 'EFA': 'Developed ex-US', 'EEM': 'Emerging markets',
               'TLT': 'US Treasuries 20y+', 'IEF': 'US Treasuries 7-10y', 'LQD': 'Investment-grade credit',
               'HYG': 'High-yield credit', 'GLD': 'Gold'}
BVB = ['TLV', 'SNP', 'BRD', 'TGN', 'SNG', 'SNN', 'EL', 'TEL']                      # listate inainte de 2014-09
BVB_NAMES = {'TLV': 'Banca Transilvania', 'SNP': 'OMV Petrom', 'BRD': 'BRD-GSG', 'TGN': 'Transgaz',
             'SNG': 'Romgaz', 'SNN': 'Nuclearelectrica', 'EL': 'Electrica', 'TEL': 'Transelectrica'}

_CACHE = {}


def read_market(symbol):
    """Seria data/market/<SIMBOL>.csv."""
    fname = f'{symbol}.csv'
    path = os.path.join(MARKET_DIR, fname)
    src = path if os.path.exists(path) else REPO_RAW + fname
    return pd.read_csv(src, index_col='date', parse_dates=True).sort_index()


def price(symbol):
    """Pretul folosit: adjusted_close pentru ETF/actiuni (.US, .RO), close pentru indici si cripto."""
    d = read_market(symbol)
    col = 'close' if symbol.endswith('.INDX') or symbol.endswith('.CC') or symbol == 'BET' else 'adjusted_close'
    s = d[col].astype(float)
    return s[s > 0].rename(symbol)


def prices(symbols, start=None, end=None):
    """Preturi aliniate: join pe zilele comune (analiza comuna -> intai join pe preturi)."""
    p = pd.concat([price(s) for s in symbols], axis=1).dropna()
    return p.loc[start:end]


def log_returns(p):
    """Randamente log pe un tabel deja aliniat (zile comune)."""
    return np.log(p).diff().dropna()


def french_rf():
    """Rata fara risc lunara (T-bill la o luna) din fisierul Fama-French cu 3 factori, in zecimal."""
    if 'rf' in _CACHE:
        return _CACHE['rf']
    url = FRENCH + 'F-F_Research_Data_Factors_CSV.zip'
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}),
                                 timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    text = z.read(z.namelist()[0]).decode('latin-1')
    rows = []
    for line in text.splitlines():
        parts = [x.strip() for x in line.split(',')]
        if len(parts) == 5 and len(parts[0]) == 6 and parts[0].isdigit():
            rows.append((parts[0], float(parts[4]) / 100.0))
        elif rows and not (len(parts[0]) == 6 and parts[0].isdigit()):
            break
    rf = pd.Series(dict(rows))
    rf.index = pd.to_datetime(rf.index, format='%Y%m') + pd.offsets.MonthEnd(0)
    _CACHE['rf'] = rf.rename('RF')
    return _CACHE['rf']


def monthly_returns(symbols, start=None):
    """Randamente lunare simple din preturile de sfarsit de luna (zile comune)."""
    p = prices(symbols).resample('ME').last()
    return p.pct_change().dropna().loc[start:]


def bnr_rate(currency='USD', start=2014, end=2026):
    """Cursul de referinta BNR: lei pentru o unitate de valuta (arhivele XML anuale)."""
    key = ('bnr', currency, start, end)
    if key in _CACHE:
        return _CACHE[key]
    rows = []
    for y in range(start, end + 1):
        xml = urllib.request.urlopen(urllib.request.Request(BNR_XML.format(y), headers={'User-Agent': 'Mozilla'}),
                                     timeout=60).read().decode()
        for d, body in re.findall(r'<Cube date="([\d-]+)">(.*?)</Cube>', xml, re.S):
            m = re.search(rf'<Rate currency="{currency}"( multiplier="\d+")?>([\d.]+)</Rate>', body)
            if m:
                rows.append((d, float(m.group(2))))
    s = pd.Series(dict(rows)).sort_index()
    s.index = pd.to_datetime(s.index)
    _CACHE[key] = s.rename(f'{currency}RON')
    return _CACHE[key]

"""
mfm_data.py -- Incarcarea datelor pentru Capitolul 2 (MFM): eficienta pietei
==========================================================================
  * load_close(name)   -- pretul de inchidere zilnic din data/market/ (sau cursul de referinta BNR)
  * log_returns(name)  -- randamente log pe calendarul propriu al fiecarei serii
  * MARKETS            -- piete dezvoltate, emergente/de frontiera, cripto si EUR/RON

Conventii (ca in capitolele 0 si 1):
  * indicii bursieri: doar zilele lucratoare; zilele cu inchidere identica cu ziua precedenta
    (sarbatori completate cu ultimul pret) sunt eliminate;
  * cripto: 7 zile din 7;
  * EUR/RON: cursul oficial de referinta BNR (fisierul de piata are cotatii eronate).

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import io
import os
import re
import urllib.request
import numpy as np
import pandas as pd

REPO_RAW = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
MARKET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'market')
END = '2026-09-18'

# nume -> (simbol, eticheta, grup, data de start, zile pe an)
MARKETS = {
    'sp500':  ('GSPC.INDX',     'S&P 500 (US)',          'Developed', '2000-01-01', 252),
    'stoxx':  ('STOXX50E.INDX', 'Euro Stoxx 50',         'Developed', '2000-01-01', 252),
    'nikkei': ('N225.INDX',     'Nikkei 225 (Japan)',    'Developed', '2000-01-01', 252),
    'hsi':    ('HSI.INDX',      'Hang Seng (HK)',        'Developed', '2000-01-01', 252),
    'bet':    ('BET',           'BET (Romania)',         'Emerging/frontier', '2000-01-01', 252),
    'wig20':  ('WIG20.INDX',    'WIG20 (Poland)',        'Emerging/frontier', '2000-01-01', 252),
    'bux':    ('BUX.INDX',      'BUX (Hungary)',         'Emerging/frontier', '2000-01-01', 252),
    'px':     ('PX.INDX',       'PX (Czechia)',          'Emerging/frontier', '2000-01-01', 252),
    'xu100':  ('XU100.INDX',    'BIST 100 (Turkey)',     'Emerging/frontier', '2000-01-01', 252),
    'bvsp':   ('BVSP.INDX',     'Bovespa (Brazil)',      'Emerging/frontier', '2000-01-01', 252),
    'mxx':    ('MXX.INDX',      'IPC (Mexico)',          'Emerging/frontier', '2000-01-01', 252),
    'nsei':   ('NSEI.INDX',     'Nifty 50 (India)',      'Emerging/frontier', '2000-01-01', 252),
    'ssec':   ('SSEC.INDX',     'Shanghai (China)',      'Emerging/frontier', '2000-01-01', 252),
    'btc':    ('BTC-USD.CC',    'Bitcoin',               'Crypto', '2014-09-17', 365),
    'eth':    ('ETH-USD.CC',    'Ethereum',              'Crypto', '2016-01-01', 365),
    'eurron': ('REF:EUR',       'EUR/RON (reference rate)', 'FX', '2005-07-01', 252),
}

LABELS = {k: v[1] for k, v in MARKETS.items()}
GROUPS = {k: v[2] for k, v in MARKETS.items()}
PERIODS = {k: v[4] for k, v in MARKETS.items()}

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
    symbol, _, group, start0, _ = MARKETS[name]
    start = start or start0
    if symbol.startswith('REF:'):
        return read_reference_rate(symbol.split(':')[1], start=start, end=end).rename(name)
    s = read_market(symbol)['close'].loc[start:end]
    s = s[s > 0].dropna()
    if group != 'Crypto':
        s = s[s.index.dayofweek < 5]          # fara cotatii de weekend
        s = s[s.diff() != 0]                  # fara sarbatori completate cu pretul anterior
    return s.rename(name)


def complete_months(x):
    """Elimina luna finala incompleta (ultima observatie inainte de ultima zi lucratoare a lunii):
    analizele lunare si efectul schimbarii lunii folosesc doar luni complete."""
    last = x.index[-1]
    if last + pd.offsets.BMonthEnd(0) != last:
        x = x[x.index < last.to_period('M').start_time]
    return x


def log_returns(name, start=None, end=END):
    """Randamente log pe calendarul propriu al seriei."""
    return np.log(load_close(name, start, end)).diff().dropna().rename(name)


# =============================================================================
# SERII LUNARE PENTRU REGRESIILE PREDICTIVE (surse publice)
# =============================================================================
SHILLER_URLS = ['http://www.econ.yale.edu/~shiller/data/ie_data.xls']
FRED = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id='


def _get(url, timeout=120, agent='Mozilla/5.0'):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': agent}),
                                  timeout=timeout).read()


def shiller():
    """S&P Composite lunar (datele publice ale lui Robert J. Shiller): P = media lunara a preturilor,
    D = dividendele pe 12 luni (nominale)."""
    if 'shiller' in _CACHE:
        return _CACHE['shiller']
    urls = []
    try:
        html = _get('https://shillerdata.com/', 60).decode('utf-8', 'ignore')
        urls = ['https:' + u if u.startswith('//') else u for u in re.findall(r'href="([^"]*ie_data\.xls[^"]*)"', html)]
    except Exception:
        pass
    raw = None
    for url in urls + SHILLER_URLS:
        try:
            raw = _get(url)
            break
        except Exception:
            continue
    d = pd.read_excel(io.BytesIO(raw), sheet_name='Data', header=None, skiprows=8).iloc[:, [0, 1, 2]]
    d.columns = ['date', 'P', 'D']
    d = d[pd.to_numeric(d['date'], errors='coerce').notna()].copy()
    yr = d['date'].astype(float)
    year = np.floor(yr + 1e-9).astype(int)
    month = np.round((yr - year) * 100).astype(int)
    d.index = pd.to_datetime(dict(year=year, month=month, day=1)) + pd.offsets.MonthEnd(0)
    d = d[['P', 'D']].apply(pd.to_numeric, errors='coerce').dropna()
    _CACHE['shiller'] = d
    return d


def fred(series):
    """Serie FRED (fara cheie), ca pd.Series cu indice la sfarsit de luna."""
    d = pd.read_csv(io.BytesIO(_get(FRED + series, agent='Python-urllib')), index_col=0, parse_dates=True)
    s = pd.to_numeric(d.iloc[:, 0], errors='coerce').dropna()
    s.index = s.index + pd.offsets.MonthEnd(0)
    return s.rename(series)


def sp500_monthly(end='2026-08-31'):
    """S&P 500 lunar, P (media lunara) si D (dividende pe 12 luni), prelungit pana la `end`.
    Prelungire (splicing): P = media lunara a inchiderilor zilnice GSPC.INDX; D = dividendele pe 12 luni
    ale SPY.US (din adjusted_close si close), scalate cu raportul mediu D_Shiller / D_SPY pe ultimele 12 luni comune."""
    sh = shiller()
    spx = read_market('GSPC.INDX')['close']
    P_ext = spx.resample('ME').mean()
    spy = read_market('SPY.US')
    tr = spy['adjusted_close'] / spy['adjusted_close'].shift(1)
    div = (tr * spy['close'].shift(1) - spy['close']).clip(lower=0)
    div[div < 1e-3 * spy['close']] = 0.0                       # doar zilele ex-dividend
    D_spy = div.resample('ME').sum().rolling(12).sum()
    common = sh.index.intersection(D_spy.dropna().index)[-12:]
    kP = float((sh.loc[common, 'P'] / P_ext.loc[common]).mean())
    kD = float((sh.loc[common, 'D'] / D_spy.loc[common]).mean())
    last = sh.index[-1]
    ext = pd.DataFrame({'P': kP * P_ext, 'D': kD * D_spy}).loc[last + pd.offsets.MonthEnd(1):end]
    out = pd.concat([sh, ext]).loc[:end]
    out.attrs.update(shiller_last=str(last.date()), kP=kP, kD=kD)
    return out

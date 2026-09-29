"""
mfm_ml.py -- Instrumente de Financial Machine Learning pentru Capitolul 13 (MFM)
==============================================================================
Functii autonome (numpy / pandas / scipy / scikit-learn), folosite de
generatorul de grafice, de Quantlet-uri si de notebook-uri:

  * load_data            -- date zilnice de piata din data/market (local sau din repo)
  * frac_diff_ffd        -- diferentiere fractionara cu fereastra fixa (FFD)
  * local_whittle, exact_local_whittle -- estimarea parametrului de memorie d
    (Robinson 1995; Shimotsu & Phillips 2005; Shimotsu 2010), SE = 1/(2 sqrt(m))
  * get_daily_vol        -- volatilitate EWMA a randamentelor zilnice
  * triple_barrier       -- etichetare prin metoda celor trei bariere
  * PurgedKFold          -- validare incrucisata cu purjare + embargo
  * build_features       -- set de caracteristici tehnice fara look-ahead
  * sharpe_ratio, probabilistic_sharpe_ratio, expected_max_sharpe,
    deflated_sharpe_ratio -- statistici pentru overfitting-ul de backtest

Referinte: Lopez de Prado (2018) Advances in Financial Machine Learning;
Bailey & Lopez de Prado (2014) The Deflated Sharpe Ratio.

Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
DATA_URL = 'https://raw.githubusercontent.com/danpele/MFM/main/data/market/'
SERIES = {'sp500': 'GSPC.INDX', 'vix': 'VIX.INDX', 'btc': 'BTC-USD.CC'}
START = {'sp500': '2000-01-01', 'vix': '2000-01-01', 'btc': '2014-09-17'}


def load_data(name='sp500', start=None, end='2026-09-18'):
    """OHLCV zilnic din data/market: copia locala, altfel fisierul din repo-ul GitHub MFM."""
    fname = SERIES[name] + '.csv'
    local = [os.path.join(DATA_DIR, 'market', fname)]
    path = next((p for p in local if os.path.exists(p)), DATA_URL + fname)
    df = pd.read_csv(path, parse_dates=['date']).set_index('date')
    df = df.rename(columns=str.capitalize)[['Open', 'High', 'Low', 'Close', 'Volume']]
    return df.loc[start or START[name]:end]


# =============================================================================
# DIFERENTIERE FRACTIONARA (FFD)
# =============================================================================
def ffd_weights(d, threshold=1e-4, max_size=10_000):
    """Ponderile w_k = -w_{k-1} (d - k + 1) / k, trunchiate cand |w_k| < threshold."""
    w = [1.0]
    for k in range(1, max_size):
        w_k = -w[-1] * (d - k + 1) / k
        if abs(w_k) < threshold:
            break
        w.append(w_k)
    return np.array(w)


def frac_diff_ffd(series, d, threshold=1e-4):
    """Seria diferentiata fractionar cu fereastra fixa: X~_t = sum_k w_k X_{t-k}."""
    w = ffd_weights(d, threshold)
    width = len(w)
    x = series.dropna().values
    out = np.convolve(x, w, mode='valid')          # out[j] = sum_k w_k x[j+width-1-k]
    return pd.Series(out, index=series.dropna().index[width - 1:])


# =============================================================================
# ESTIMAREA PARAMETRULUI DE MEMORIE d (LOCAL WHITTLE)
# =============================================================================
def _periodogram(x, m):
    n = len(x)
    w = np.fft.fft(x)[1:m + 1]
    lam = 2 * np.pi * np.arange(1, m + 1) / n
    return lam, np.abs(w) ** 2 / (2 * np.pi * n)


def local_whittle(x, m=None, alpha=0.65):
    """Estimatorul local Whittle al lui d (Robinson, 1995), cu m = n^alpha frecvente Fourier.
    Intoarce (d_hat, se), se = 1/(2 sqrt(m))."""
    from scipy.optimize import minimize_scalar
    x = np.asarray(x, float)
    m = m or int(len(x) ** alpha)
    lam, I = _periodogram(x - x.mean(), m)
    R = lambda d: np.log(np.mean(lam ** (2 * d) * I)) - 2 * d * np.mean(np.log(lam))
    return minimize_scalar(R, bounds=(-0.49, 1.99), method='bounded').x, 1 / (2 * np.sqrt(m))


def _frac_diff_full(x, d):
    """(1-L)^d x_t cu x_t = 0 pentru t <= 0 (fara trunchiere), prin FFT."""
    n = len(x)
    k = np.arange(1, n)
    pi = np.concatenate([[1.0], np.cumprod((k - 1 - d) / k)])
    L = 2 ** int(np.ceil(np.log2(2 * n)))
    return np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(pi, L), L)[:n]


def exact_local_whittle(x, m=None, alpha=0.65):
    """Exact local Whittle (Shimotsu & Phillips, 2005), valid si pentru serii nestationare (d >= 0.5);
    media necunoscuta tratata prin scaderea valorii initiale (Shimotsu, 2010). Intoarce (d_hat, se)."""
    from scipy.optimize import minimize_scalar
    x = np.asarray(x, float)
    x = x - x[0]
    m = m or int(len(x) ** alpha)
    lam = 2 * np.pi * np.arange(1, m + 1) / len(x)
    def R(d):
        _, I = _periodogram(_frac_diff_full(x, d), m)
        return np.log(np.mean(I)) - 2 * d * np.mean(np.log(lam))
    return minimize_scalar(R, bounds=(-0.49, 1.99), method='bounded').x, 1 / (2 * np.sqrt(m))


# =============================================================================
# ETICHETARE: METODA CELOR TREI BARIERE
# =============================================================================
def get_daily_vol(close, span=50):
    """Volatilitatea EWMA: radacina patrata a mediei EWMA a abaterilor patratice ale randamentelor log zilnice."""
    return np.log(close).diff().ewm(span=span).std()


def triple_barrier(close, events_idx, vol, pt=1.0, sl=1.0, horizon=10):
    """
    Pentru fiecare moment t0 din events_idx:
      bariera superioara = P_t0 * exp(+pt * vol_t0 * sqrt(horizon))
      bariera inferioara = P_t0 * exp(-sl * vol_t0 * sqrt(horizon))
      bariera verticala  = t0 + horizon zile de tranzactionare
    Evenimentele fara o fereastra completa de horizon zile (sfarsitul esantionului) sunt omise.
    Eticheta: +1 (atinge sus), -1 (atinge jos), sign(randament) la bariera verticala.
    Intoarce DataFrame cu t1 (momentul atingerii), ret, label, barrier.
    """
    logp = np.log(close)
    pos = {t: i for i, t in enumerate(close.index)}
    rows = []
    for t0 in events_idx:
        i0 = pos[t0]
        if i0 + horizon >= len(close) or np.isnan(vol.iloc[i0]):
            continue                                   # fereastra completa de h zile, altfel evenimentul e cenzurat
        i1 = i0 + horizon
        width = vol.iloc[i0] * np.sqrt(horizon)
        path = logp.iloc[i0 + 1:i1 + 1] - logp.iloc[i0]
        up = path[path >= pt * width].index.min() if pt > 0 else pd.NaT
        dn = path[path <= -sl * width].index.min() if sl > 0 else pd.NaT
        first = min([t for t in (up, dn) if pd.notna(t)], default=pd.NaT)
        if pd.isna(first):
            t1, barrier = close.index[i1], 'vertical'
            label = int(np.sign(path.iloc[-1])) if len(path) else 0
        else:
            t1 = first
            barrier = 'upper' if first == up else 'lower'
            label = 1 if barrier == 'upper' else -1
        rows.append((t0, t1, logp.loc[t1] - logp.iloc[i0], label, barrier, width))
    return pd.DataFrame(rows, columns=['t0', 't1', 'ret', 'label', 'barrier', 'width']).set_index('t0')


# =============================================================================
# VALIDARE INCRUCISATA CU PURJARE SI EMBARGO
# =============================================================================
class PurgedKFold:
    """
    K-Fold fara amestecare pentru etichete care se suprapun in timp.

    t1 : pd.Series indexata dupa momentul observatiei t0, cu valoarea = momentul
         in care se cunoaste eticheta (sfarsitul ferestrei etichetei).
    Purjare: se elimina din antrenare observatiile al caror interval [t0, t1]
             se suprapune cu intervalul setului de test.
    Embargo: se elimina si o fractiune pct_embargo de observatii imediat dupa test.
    """

    def __init__(self, n_splits=5, t1=None, pct_embargo=0.01):
        self.n_splits = n_splits
        self.t1 = t1
        self.pct_embargo = pct_embargo

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits

    def split(self, X, y=None, groups=None):
        idx = np.arange(len(X))
        t0 = self.t1.index.values
        t1 = self.t1.values
        embargo = int(len(X) * self.pct_embargo)
        for test in np.array_split(idx, self.n_splits):
            start, stop = test[0], test[-1]
            test_t0, test_t1 = t0[start], t1[test].max()
            # purjare: antrenare doar pe observatii care nu se suprapun cu testul
            before = idx[(t1 < test_t0)]
            after_start = min(stop + 1 + embargo, len(X))
            after = idx[after_start:][t0[after_start:] > test_t1]
            yield np.concatenate([before, after]), test


# =============================================================================
# CARACTERISTICI (FARA LOOK-AHEAD)
# =============================================================================
def rsi(close, n=14):
    delta = close.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / n).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / n).mean()
    return 100 - 100 / (1 + up / dn)


def build_features(close, vix=None, d_ffd=None):
    """Caracteristici calculate doar cu informatie disponibila la momentul t."""
    lp = np.log(close)
    r = lp.diff()
    f = pd.DataFrame(index=close.index)
    for h in (1, 5, 20, 60, 120):
        f[f'mom_{h}'] = lp.diff(h)
    f['vol_20'] = r.rolling(20).std() * np.sqrt(252)
    f['vol_60'] = r.rolling(60).std() * np.sqrt(252)
    f['vol_ratio'] = f['vol_20'] / f['vol_60']
    f['dist_ma50'] = lp - lp.rolling(50).mean()
    f['dist_ma200'] = lp - lp.rolling(200).mean()
    f['rsi_14'] = rsi(close) / 100
    if vix is not None:
        v = np.log(vix.reindex(close.index).ffill())
        f['vix_level'] = v
        f['vix_chg_5'] = v.diff(5)
    if d_ffd is not None:
        f['ffd_price'] = frac_diff_ffd(lp, d_ffd)
    return f


# =============================================================================
# SHARPE, PSR, DSR
# =============================================================================
EULER_GAMMA = 0.5772156649015329


def sharpe_ratio(returns, periods=252):
    """Sharpe anualizat (fara rata fara risc)."""
    r = np.asarray(returns)
    return np.sqrt(periods) * r.mean() / r.std(ddof=1)


def probabilistic_sharpe_ratio(sr, sr_benchmark, T, skew=0.0, kurt=3.0):
    """
    PSR(SR*) = Phi( (SR - SR*) sqrt(T-1) / sqrt(1 - g3 SR + (g4 - 1)/4 SR^2) )
    SR si SR* sunt NEanualizate (pe perioada de observatie); kurt = kurtosis (distributia Normala = 3).
    """
    denom = np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    return stats.norm.cdf((sr - sr_benchmark) * np.sqrt(T - 1) / denom)


def expected_max_sharpe(n_trials, sr_std=1.0):
    """
    Teorema strategiei false (Bailey & Lopez de Prado, 2014):
    E[max SR_n] ~ sqrt(V[SR]) * ((1-g) Phi^{-1}(1 - 1/N) + g Phi^{-1}(1 - 1/(N e)))
    """
    n = np.asarray(n_trials, dtype=float)
    return sr_std * ((1 - EULER_GAMMA) * stats.norm.ppf(1 - 1 / n)
                     + EULER_GAMMA * stats.norm.ppf(1 - 1 / (n * np.e)))


def deflated_sharpe_ratio(sr, T, n_trials, sr_std, skew=0.0, kurt=3.0):
    """DSR = PSR(SR_0), cu SR_0 = E[max SR] sub ipoteza nula de lipsa a abilitatii."""
    sr0 = expected_max_sharpe(n_trials, sr_std)
    return probabilistic_sharpe_ratio(sr, sr0, T, skew, kurt)


# =============================================================================
# FACTORI FAMA-FRENCH (KENNETH FRENCH DATA LIBRARY) -- studiul de caz
# =============================================================================
FRENCH_URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'
FF_FILES = {'ff3': 'F-F_Research_Data_Factors_CSV.zip',
            'ff5': 'F-F_Research_Data_5_Factors_2x3_CSV.zip'}


def french_factors(name='ff5'):
    """Factorii lunari FF3 / FF5 (in zecimal, index = sfarsitul lunii) din Kenneth French Data Library."""
    import io
    import zipfile
    import urllib.request
    req = urllib.request.Request(FRENCH_URL + FF_FILES[name], headers={'User-Agent': 'Mozilla/5.0'})
    zf = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=120).read()))
    lines = zf.read(zf.namelist()[0]).decode('latin-1').splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(',') and len(l.split(',')) > 1)
    cols = [c.strip() for c in lines[i].split(',')[1:]]
    rows = []
    for l in lines[i + 1:]:
        parts = [x.strip() for x in l.split(',')]
        if len(parts[0]) != 6 or not parts[0].isdigit():      # sfarsitul tabelului lunar
            break
        rows.append([parts[0]] + [float(x) for x in parts[1:]])
    df = pd.DataFrame(rows, columns=['date'] + cols)
    df['date'] = pd.to_datetime(df['date'], format='%Y%m') + pd.offsets.MonthEnd(0)
    return df.set_index('date') / 100


def tangency_portfolio(factors, train=('1967-01', '1986-12')):
    """Portofoliul tangent cu ponderi fixe w = Sigma^{-1} mu estimate pe perioada de antrenare
    (normalizate la sum|w| = 1); intoarce ponderile si randamentul lunar pe tot esantionul."""
    X = factors.loc[train[0]:train[1]]
    w = np.linalg.solve(X.cov().values, X.mean().values)
    w = pd.Series(w / np.abs(w).sum(), index=factors.columns)
    return w, factors @ w

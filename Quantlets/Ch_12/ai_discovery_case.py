"""
ai_discovery_case.py -- Capitolul 12, secțiunea "AI for Scientific Discovery": mini-studiul de caz
==================================================================================================
Ipoteza: prima de risc a varianței (VRP = IV - RV) prognozează randamentul în exces al S&P 500 pe 3 luni
(Bollerslev, Tauchen & Zhou, 2009, Tabelul 2). Pași:
  1. replicare pe eșantionul publicat (ian. 1990 -- dec. 2007), erori standard Hodrick (1992) ca în lucrare;
  2. același test pe eșantionul extins până la zi;
  3. test în afara eșantionului din ian. 2008: R^2_OS (Campbell & Thompson, 2008) și testul Clark--West.
Definiții (BTZ, 2009): IV_t = VIX_t^2 / 12 la sfârșitul lunii; RV_t = suma randamentelor log (%) la pătrat din luna t;
randamentul în exces = randamentul log lunar al S&P 500 minus TB3MS/12 (FRED), anualizat: (12/h) * suma pe h luni.
Limitare de date: RV din randamente zilnice, nu din randamente la 5 minute (indisponibile pentru 1990--2007).
Ieșire: ai_discovery_case.json
"""

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
MARKET = os.path.join(HERE, '..', '..', 'data', 'market')
H = 3


def read(sym):
    return pd.read_csv(os.path.join(MARKET, f'{sym}.csv'), index_col='date', parse_dates=True)['close']


def hodrick_t(y, X, e1, h):
    """Erori standard Hodrick (1992) 1B pentru regresia cu randamente suprapuse (sumă de regresori trecuți)."""
    T = len(y)
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    Z = X.T @ X / T
    S = np.zeros((X.shape[1], X.shape[1]))
    for t in range(h - 1, T):
        w = e1[t] * X[t - h + 1:t + 1].sum(axis=0)
        S += np.outer(w, w)
    S /= T
    Zi = np.linalg.inv(Z)
    V = Zi @ S @ Zi / T
    return b, b / np.sqrt(np.diag(V))


def nw_t(x, lags):
    x = np.asarray(x) - np.mean(x)
    T = len(x)
    s = x @ x / T
    for L in range(1, lags + 1):
        s += 2 * (1 - L / (lags + 1)) * (x[L:] @ x[:-L]) / T
    return np.sqrt(s / T)


def monthly_data():
    """Date lunare BTZ (2009): IV = VIX^2/12, RV = suma randamentelor zilnice (%) la patrat, VRP = IV - RV (ex ante),
    randamentul in exces = randamentul log lunar S&P 500 minus TB3MS/12 (FRED)."""
    spx, vix = read('GSPC.INDX'), read('VIX.INDX')
    px = pd.concat([spx, vix], axis=1, keys=['spx', 'vix']).dropna()
    r = 100 * np.log(px['spx']).diff().dropna()
    rv = (r ** 2).resample('ME').sum()
    iv = (px['vix'] ** 2 / 12).resample('ME').last()
    rm = 100 * np.log(px['spx'].resample('ME').last()).diff()
    tb = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS', index_col=0, parse_dates=True).iloc[:, 0]
    tb.index = tb.index + pd.offsets.MonthEnd(0)
    df = pd.DataFrame({'iv': iv, 'rv': rv, 'rm': rm, 'rf': tb / 12}).dropna()
    df = df[df.index >= '1990-01-31']
    df['vrp'] = df['iv'] - df['rv']
    df['ex'] = df['rm'] - df['rf']
    return df


def main():
    df = monthly_data()
    ex = df['ex'].values
    # y_t = (12/h) * sum_{j=1..h} ex_{t+j}
    y = pd.Series([(12 / H) * ex[t + 1:t + 1 + H].sum() if t + H < len(ex) else np.nan for t in range(len(ex))],
                  index=df.index)
    df['y'] = y
    out = {}

    def insample(d, tag):
        d = d.dropna()
        X = np.column_stack([np.ones(len(d)), d['vrp'].values])
        yv = d['y'].values
        # reziduurile pe o perioadă sub H0 (fără predictibilitate): ex_{t+1} - media, scalate cu 12/h
        e1 = (12 / H) * (d['ex'].shift(-1).reindex(d.index).values - np.nanmean(d['ex'].shift(-1).values))
        e1 = np.nan_to_num(e1)
        b, t = hodrick_t(yv, X, e1, H)
        res = yv - X @ b
        r2 = 1 - res.var() / yv.var()
        n = len(yv)
        adj = 1 - (1 - r2) * (n - 1) / (n - 2)
        out[tag] = {'b': float(b[1]), 't': float(t[1]), 'adjr2': float(100 * adj), 'n': int(n),
                    'start': d.index[0].strftime('%Y-%m'), 'end': d.index[-1].strftime('%Y-%m'),
                    'mean_iv': float(d['iv'].mean()), 'mean_rv': float(d['rv'].mean())}

    insample(df[(df.index <= '2007-09-30')], 'pub')   # ultimul randament folosit: dec. 2007
    insample(df, 'full')

    # în afara eșantionului: fereastră extinsă; la data t folosim doar perechi (vrp_s, y_s) cu s + H <= t
    d = df.dropna(subset=['y'])
    idx = list(df.index)
    fc, bm, act = [], [], []
    for t0 in d.index[d.index >= '2008-01-31']:
        k = idx.index(t0)
        train = df.iloc[:k - H + 1].dropna(subset=['y'])
        X = np.column_stack([np.ones(len(train)), train['vrp'].values])
        b = np.linalg.lstsq(X, train['y'].values, rcond=None)[0]
        fc.append(b[0] + b[1] * df['vrp'].iloc[k])
        bm.append(train['y'].mean())
        act.append(d.loc[t0, 'y'])
    fc, bm, act = map(np.array, (fc, bm, act))
    r2os = 1 - np.sum((act - fc) ** 2) / np.sum((act - bm) ** 2)
    f = (act - bm) ** 2 - ((act - fc) ** 2 - (bm - fc) ** 2)   # Clark--West (2007)
    cw = f.mean() / nw_t(f, H)
    from scipy.stats import norm
    out['oos'] = {'r2os': float(100 * r2os), 'cw': float(cw), 'p': float(1 - norm.cdf(cw)), 'n': int(len(act)),
                  'start': d.index[d.index >= '2008-01-31'][0].strftime('%Y-%m'),
                  'end': d.index[-1].strftime('%Y-%m')}
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()

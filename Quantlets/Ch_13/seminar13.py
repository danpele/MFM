"""
seminar13.py -- Calculele si graficele Seminarului 13 (MFM): Machine Learning in finante
========================================================================================
Fiecare functie calculeaza rezultatele unui exercitiu (cifrele din slide-uri) si deseneaza graficul
rezolvarii in charts/ch13_sem_*.pdf|png (fundal transparent, etichete ENG, legenda jos, paleta MFM).
Codul reproduce notebook-ul seminarului (aceleasi functii, aceiasi generatori aleatori, seed 42):
fiecare exercitiu porneste propriul numpy.random.default_rng(42), ca in notebook.

Date: data/market/BTC-USD.CC.csv (2014-09-17 -- 2026-09-18), ETH-USD.CC.csv (2015-08-07 -- 2026-09-18),
VIX.INDX.csv (B14); pret de inchidere (close).

Rulare:  python seminar13.py            (scrie seminar13_results.json; aproximativ 10 minute)
         python seminar13.py a1 b3      (doar exercitiile numite)
Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import os
import sys
import json
import itertools
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats
from scipy.special import gamma as G, gammaln
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LogisticRegression, Lasso
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import KFold, TimeSeriesSplit, cross_val_score
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, roc_auc_score, precision_score, recall_score, f1_score,
                             log_loss, roc_curve)
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from generate_all_charts import MainBlue, IDAred, Forest, Amber, Orange, Purple, Gray, save_fig  # noqa: E402
from mfm_ml import PurgedKFold, local_whittle, exact_local_whittle  # noqa: E402

Teal = '#17A2B8'
SEED = 42
DATA = os.path.join(HERE, '..', '..', 'data', 'market')
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 9.5
plt.rcParams['legend.fontsize'] = 8
OUT = {}


def bottom_legend(fig, ncol=3, handles=None, labels=None, fontsize=7.5, y=0.0):
    """Legenda sub figura (in afara axelor), dupa tight_layout."""
    plt.tight_layout()
    if handles is None:
        handles, labels, seen = [], [], set()
        for ax in fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in seen and not l.startswith('_'):
                    handles.append(h); labels.append(l); seen.add(l)
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False,
               fontsize=fontsize)


# =============================================================================
# DATE SI FUNCTII (identice cu notebook-ul seminarului)
# =============================================================================
def load_close(symbol, start, end='2026-09-18'):
    df = pd.read_csv(os.path.join(DATA, symbol + '.csv'), parse_dates=['date']).set_index('date')
    return df['close'].loc[start:end]


btc = load_close('BTC-USD.CC', '2014-09-17')
eth = load_close('ETH-USD.CC', '2015-08-07')
log_btc, log_eth = np.log(btc), np.log(eth)


def ffd_weights(d, threshold=1e-4, max_size=10_000):
    w = [1.0]
    for k in range(1, max_size):
        w_k = -w[-1] * (d - k + 1) / k
        if abs(w_k) < threshold:
            break
        w.append(w_k)
    return np.array(w)


def frac_diff_ffd(series, d, threshold=1e-4):
    w = ffd_weights(d, threshold)
    x = series.dropna().values
    out = np.convolve(x, w, mode='valid')
    return pd.Series(out, index=series.dropna().index[len(w) - 1:])


def get_daily_vol(close, span=50):
    return np.log(close).diff().ewm(span=span).std()


def triple_barrier(close, events_idx, vol, pt=1.0, sl=1.0, horizon=10):
    logp = np.log(close)
    pos = {t: i for i, t in enumerate(close.index)}
    rows = []
    for t0 in events_idx:
        i0 = pos[t0]
        if i0 + horizon >= len(close) or np.isnan(vol.iloc[i0]):
            continue
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


def rsi(close, n=14):
    delta = close.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / n).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / n).mean()
    return 100 - 100 / (1 + up / dn)


def build_features(close, periods=365):
    lp = np.log(close)
    r = lp.diff()
    f = pd.DataFrame(index=close.index)
    for h in (1, 5, 20, 60, 120):
        f[f'mom_{h}'] = lp.diff(h)
    f['vol_20'] = r.rolling(20).std() * np.sqrt(periods)
    f['vol_60'] = r.rolling(60).std() * np.sqrt(periods)
    f['vol_ratio'] = f['vol_20'] / f['vol_60']
    f['dist_ma50'] = lp - lp.rolling(50).mean()
    f['dist_ma200'] = lp - lp.rolling(200).mean()
    f['rsi_14'] = rsi(close) / 100
    return f


EULER_GAMMA = 0.5772156649015329


def psr(sr, sr_b, T, skew=0.0, kurt=3.0):
    return stats.norm.cdf((sr - sr_b) * np.sqrt(T - 1) / np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2))


def expected_max_sharpe(n_trials, sr_std=1.0):
    n = np.asarray(n_trials, dtype=float)
    return sr_std * ((1 - EULER_GAMMA) * stats.norm.ppf(1 - 1 / n) + EULER_GAMMA * stats.norm.ppf(1 - 1 / (n * np.e)))


def dsr(sr, T, n_trials, sr_std, skew=0.0, kurt=3.0):
    return psr(sr, expected_max_sharpe(n_trials, sr_std), T, skew, kurt)


def hac_mean(x, lags):
    r = sm.OLS(np.asarray(x, float), np.ones(len(x))).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    return r.params[0], r.bse[0], r.tvalues[0], r.pvalues[0]


# =============================================================================
# SETUP: datele
# =============================================================================
def setup():
    rb, re_ = log_btc.diff().dropna(), log_eth.diff().dropna()
    OUT['setup'] = dict(btc_n=len(btc), btc_start=str(btc.index[0].date()), btc_end=str(btc.index[-1].date()),
                        eth_n=len(eth), eth_start=str(eth.index[0].date()), eth_end=str(eth.index[-1].date()),
                        btc_first=round(float(btc.iloc[0]), 2), btc_last=round(float(btc.iloc[-1]), 2),
                        eth_first=round(float(eth.iloc[0]), 4), eth_last=round(float(eth.iloc[-1]), 2),
                        btc_ret_n=len(rb), eth_ret_n=len(re_),
                        btc_vol_ann=float(rb.std() * np.sqrt(365)), eth_vol_ann=float(re_.std() * np.sqrt(365)))
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 3.9), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    axes[0].plot(log_btc.index, log_btc, color=MainBlue, lw=0.8, label='BTC-USD, log close')
    axes[0].plot(log_eth.index, log_eth, color=Amber, lw=0.8, label='ETH-USD, log close')
    axes[0].set_ylabel('log price (USD)')
    axes[1].plot(rb.index, rb, color=MainBlue, lw=0.4)
    axes[1].plot(re_.index, re_, color=Amber, lw=0.4, alpha=0.8)
    axes[1].set_ylabel('daily log return')
    for ax in axes:
        for d0, lab in ((btc.index[0], 'BTC sample start 2014-09-17'), (eth.index[0], 'ETH sample start 2015-08-07')):
            ax.axvline(d0, color=IDAred if 'BTC' in lab else Forest, ls='--', lw=0.8, label=lab if ax is axes[0] else None)
        ax.axvline(pd.Timestamp('2026-09-18'), color='black', ls=':', lw=0.8, label='end 2026-09-18' if ax is axes[0] else None)
    axes[0].set_title('Frozen seminar sample: prices and daily log returns', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_data')


# =============================================================================
# A1, A2: ponderile FFD, suma lor si Monte Carlo ADF
# =============================================================================
def a1():
    res = {}
    for d in (0.25, 0.3, 0.5):
        w = ffd_weights(d)
        K = len(w) - 1
        res[str(d)] = dict(K=K, n_weights=len(w), sum=float(w.sum()),
                          closed=float(np.exp(gammaln(K + 1 - d) - gammaln(1 - d) - gammaln(K + 1))),
                          asympt=float(K ** (-d) / G(1 - d)),
                          K_approx=float((1e-4 * abs(G(-d))) ** (-1 / (1 + d))))
    res['w_first5_d025'] = [float(x) for x in ffd_weights(0.25, threshold=0, max_size=5)]
    # descompunerea unui mers aleator filtrat (seed 42)
    rng = np.random.default_rng(SEED)
    w = ffd_weights(0.25)
    K = len(w) - 1
    X = np.cumsum(rng.normal(size=3000 + K))
    ffd = np.convolve(X, w, mode='valid')
    lev = w.sum() * X[K:]
    stat = ffd - lev
    res['decomp_corr_ffd_level'] = float(np.corrcoef(ffd, lev)[0, 1])
    res['decomp_sd_level'] = float(lev.std()); res['decomp_sd_stat'] = float(stat.std())
    OUT['A1'] = res
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    cols = {0.25: MainBlue, 0.3: Amber, 0.5: Teal}
    for d, c in cols.items():
        wd = ffd_weights(d)
        k = np.arange(1, len(wd))
        axes[0].loglog(k, np.abs(wd[1:]), color=c, lw=1.1, label=f'd = {d}: K = {len(wd) - 1}')
        axes[1].plot(np.arange(len(wd)), np.cumsum(wd), color=c, lw=1.1)
        axes[1].plot(len(wd) - 1, wd.sum(), 'o', color=c, ms=4)
        axes[1].annotate(f'{wd.sum():.3f}', (len(wd) - 1, wd.sum()), textcoords='offset points', xytext=(3, -11 if d == 0.3 else 4),
                         fontsize=7.5, color=c)
    axes[0].axhline(1e-4, color='black', ls='--', lw=0.8, label=r'threshold $\tau = 10^{-4}$')
    axes[0].set_xlabel('lag k'); axes[0].set_ylabel('$|w_k|$'); axes[0].set_title('Weights, log-log scale', loc='left')
    axes[1].set_xlabel('lag k'); axes[1].set_ylabel('partial sum of weights')
    axes[1].set_title('Partial sums stop above 0', loc='left'); axes[1].set_ylim(0, 1.02)
    t = np.arange(len(ffd))
    axes[2].plot(t, ffd, color=Purple, lw=0.8, label='FFD series, d = 0.25')
    axes[2].plot(t, lev, color=IDAred, lw=1.0, label=f'{w.sum():.3f} x level (unit root)')
    axes[2].plot(t, stat, color=Forest, lw=0.6, label='stationary remainder')
    axes[2].set_xlabel('day'); axes[2].set_title('One simulated random walk', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_a1_weights')


def a2():
    """Monte Carlo ca in notebook (rng 42, d = 0.3 apoi 0.5); pe aceleasi traiectorii si ADF cu lag ales prin AIC."""
    rng = np.random.default_rng(SEED)
    rows = {}
    for d in (0.3, 0.5):
        w = ffd_weights(d)
        rej1, rejA = [], []
        for _ in range(500):
            f = np.convolve(np.cumsum(rng.normal(size=2500 + len(w) - 1)), w, mode='valid')
            a = adfuller(f, maxlag=1, regression='c', autolag=None)
            rej1.append(a[0] < a[4]['5%'])
            b = adfuller(f, regression='c', autolag='AIC')
            rejA.append(b[0] < b[4]['5%'])
        rows[str(d)] = dict(K=len(w) - 1, wsum=float(w.sum()), rej_1lag=float(np.mean(rej1)), rej_aic=float(np.mean(rejA)))
    # d = 0.25 (curs) si controlul nefiltrat (d = 0), aceeasi continuare a generatorului
    for d in (0.25, 0.0):
        w = ffd_weights(d) if d > 0 else np.array([1.0])
        rej1, rejA = [], []
        for _ in range(500):
            f = np.convolve(np.cumsum(rng.normal(size=2500 + len(w) - 1)), w, mode='valid')
            a = adfuller(f, maxlag=1, regression='c', autolag=None)
            rej1.append(a[0] < a[4]['5%'])
            b = adfuller(f, regression='c', autolag='AIC')
            rejA.append(b[0] < b[4]['5%'])
        rows[str(d)] = dict(K=len(w) - 1, wsum=float(w.sum()), rej_1lag=float(np.mean(rej1)), rej_aic=float(np.mean(rejA)))
    OUT['A2'] = rows
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    ds = ['0.0', '0.25', '0.3', '0.5']
    x = np.arange(len(ds))
    for j, (key, c, lab) in enumerate((('rej_1lag', MainBlue, 'ADF, constant, 1 lag'), ('rej_aic', Amber, 'ADF, lags chosen by AIC'))):
        v = np.array([rows[d][key] for d in ds])
        se = np.sqrt(v * (1 - v) / 500)
        ax.bar(x + (j - 0.5) * 0.36, v, 0.36, color=c, label=lab, yerr=1.96 * se, capsize=2, ecolor='black')
        for xi, vi in zip(x, v):
            ax.text(xi + (j - 0.5) * 0.36, vi + 0.03, f'{vi:.1%}', ha='center', fontsize=7)
    ax.axhline(0.05, color=IDAred, ls='--', lw=0.9, label='nominal 5%')
    ax.set_xticks(x, ['no filter (d = 0)', 'FFD d = 0.25', 'FFD d = 0.3', 'FFD d = 0.5'])
    ax.set_ylabel('rejection frequency'); ax.set_ylim(0, 1.15)
    ax.set_title('Every path is a random walk: every rejection is a type I error', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_a2_adf')


# =============================================================================
# A3, A4: trei bariere pe traiectorii scurte
# =============================================================================
def label_path(path, sigma, h, pt, sl):
    width = sigma * np.sqrt(h)
    up, dn = path[0] * np.exp(pt * width), path[0] * np.exp(-sl * width)
    for day, p_ in enumerate(path[1:], start=1):
        if p_ >= up:
            return +1, day, up, dn, 'upper'
        if p_ <= dn:
            return -1, day, up, dn, 'lower'
    return int(np.sign(np.log(path[-1] / path[0]))), len(path) - 1, up, dn, 'vertical'


def p_no_touch(c, terms=50):
    n = np.arange(terms)
    return 4 / np.pi * np.sum((-1) ** n / (2 * n + 1) * np.exp(-(2 * n + 1) ** 2 * np.pi ** 2 / (8 * c ** 2)))


def a3_a4():
    cases = [('A3 path 1', [100, 101.0, 100.4, 102.5, 101.2, 99.8], 0.01, 5, 1, 1),
             ('A3 path 2', [100, 99.2, 98.6, 99.5, 98.9, 99.1], 0.01, 5, 1, 1),
             ('A4 path (i)', [50, 51.5, 53.0, 49.5, 47.9], 0.02, 4, 2, 1),
             ('A4 path (ii)', [50, 52.0, 54.5, 53.0, 51.0], 0.02, 4, 2, 1)]
    res = {}
    for tag, group, answers in (('a3_task', cases[:2], False), ('a3_paths', cases[:2], True), ('a4_paths', cases[2:], True)):
        fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
        for ax, (name, path, s, h, pt, sl) in zip(axes, group):
            lab, day, up, dn, bar = label_path(path, s, h, pt, sl)
            res[name] = dict(label=lab, day=day, upper=round(up, 2), lower=round(dn, 2), exit=bar)
            t = np.arange(len(path))
            ax.plot(t, path, 'o-', color=MainBlue, ms=3, lw=1.0, label='close')
            if answers:
                ax.axhline(up, color=Forest, ls='--', lw=0.9, label='upper barrier')
                ax.axhline(dn, color=IDAred, ls='--', lw=0.9, label='lower barrier')
                ax.plot(day, path[day], 'o', ms=8, mfc='none', mec='black', mew=1.2, label='first touch / exit')
                ax.set_title(f'{name}: label {lab:+d} ({bar}, day {day})', loc='left', fontsize=8.5)
                ax.text(0.1, up, f'{up:.2f}', va='bottom', fontsize=7, color=Forest)
                ax.text(0.1, dn, f'{dn:.2f}', va='top', fontsize=7, color=IDAred)
                ax.set_ylim(dn - 0.08 * (up - dn), up + 0.12 * (up - dn))
            else:
                ax.set_title(f'{name}: where are the barriers?', loc='left', fontsize=8.5)
                for i_, v in enumerate(path):
                    ax.text(i_, v, f' {v}', fontsize=7, va='bottom')
            ax.axvline(h, color=Amber, ls='-', lw=1.0, label='vertical barrier')
            ax.set_xlabel('day')
        bottom_legend(fig, ncol=4)
        save_fig('ch13_sem_' + tag)
    OUT['A3A4'] = res
    # repere browniene pentru h = 10 (A3 extins): continuu, aproximare discreta, simulare discreta
    rng = np.random.default_rng(SEED)
    x = np.cumsum(rng.normal(size=(400_000, 10)), 1) / np.sqrt(10)
    sim = float(np.mean(np.all(np.abs(x) < 1, axis=1)))
    OUT['A3_time_out'] = dict(continuous=float(p_no_touch(1.0)), daily_approx=float(p_no_touch(1 + 0.5826 / np.sqrt(10))),
                              daily_sim=sim, daily_sim_se=float(np.sqrt(sim * (1 - sim) / 400_000)))
    # A4 (c): probabilitatea de atingere cu tendinta
    sig, mu, h, pt_, sl_ = 0.03, 0.001, 10, 2, 1
    a, b = pt_ * sig * np.sqrt(h), sl_ * sig * np.sqrt(h)
    k = 2 * mu / sig ** 2
    OUT['A4_drift'] = dict(a=a, b=b, k=k, p=float((np.exp(k * b) - 1) / (np.exp(k * b) - np.exp(-k * a))), p0=b / (a + b))


# =============================================================================
# A5, A6: PSR, DSR si constanta Gumbel
# =============================================================================
def a5_a6():
    res = {}
    for key, sra, T, g3, g4, N in (('A5', 1.2, 756, -0.4, 5, 100), ('A6', 1.5, 504, -0.2, 6, 20)):
        sr = sra / np.sqrt(252)
        den = np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)
        se = den / np.sqrt(T - 1)
        sr0 = float(expected_max_sharpe(N, np.sqrt(1 / T)))
        res[key] = dict(sr_daily=sr, den=den, se=se, z0=sr / se, psr0=float(psr(sr, 0, T, g3, g4)), sr0=sr0,
                        sr0_ann=sr0 * np.sqrt(252), zdsr=(sr - sr0) / se, dsr=float(dsr(sr, T, N, np.sqrt(1 / T), g3, g4)),
                        q1=float(stats.norm.ppf(1 - 1 / N)), q2=float(stats.norm.ppf(1 - 1 / (N * np.e))))
    rng = np.random.default_rng(SEED)
    mx = rng.standard_normal((20_000, 100)).max(1)
    bN = stats.norm.ppf(1 - 1 / 100); aN = stats.norm.ppf(1 - 1 / (100 * np.e)) - bN
    res['gumbel'] = dict(mc_mean=float(mx.mean()), mc_se=float(mx.std() / np.sqrt(len(mx))), formula=float(bN + EULER_GAMMA * aN),
                         bN=float(bN), aN=float(aN))
    OUT['A5A6'] = res
    for key, lab in (('A5', 'A5: SR 1.2, T = 756, N = 100'), ('A6', 'A6: SR 1.5, T = 504, N = 20')):
        r = res[key]; q = np.sqrt(252)
        fig, ax = plt.subplots(figsize=(6.2, 2.3))
        ax.errorbar(r['sr_daily'] * q, 0, xerr=1.96 * r['se'] * q, fmt='o', color=MainBlue, capsize=3, label='estimate, 95% interval')
        ax.plot(r['sr0_ann'], 0, 'D', color=IDAred, ms=7, label='$SR_0$: expected best of N trials without skill')
        ax.axvline(0, color='black', lw=0.8, ls='--', label='zero benchmark')
        ax.text(r['sr_daily'] * q, 0.25, f"PSR(0) = {r['psr0']:.3f}: benchmark 0;   DSR = {r['dsr']:.3f}: benchmark $SR_0$", ha='center', fontsize=7.5)
        ax.set_yticks([0], [lab]); ax.set_ylim(-0.6, 0.7)
        ax.set_xlabel('annualised Sharpe ratio (daily value x sqrt(252))')
        ax.set_title('Deflation moves the benchmark from 0 to $SR_0$', loc='left')
        bottom_legend(fig, ncol=2)
        save_fig('ch13_sem_' + key.lower() + '_dsr')
    fig, ax = plt.subplots(figsize=(6.2, 2.8))
    ax.hist(mx, bins=60, density=True, color=MainBlue, alpha=0.75, label='max of 100 N(0,1), 20,000 draws')
    xs = np.linspace(mx.min(), mx.max(), 300)
    z = (xs - bN) / aN
    ax.plot(xs, np.exp(-z - np.exp(-z)) / aN, color=IDAred, lw=1.3, label='Gumbel approximation')
    ax.axvline(mx.mean(), color=Forest, lw=1.1, label=f'simulated mean {mx.mean():.2f}')
    ax.axvline(bN + EULER_GAMMA * aN, color=Amber, lw=1.1, ls='--', label=f'formula {bN + EULER_GAMMA * aN:.2f}')
    ax.set_xlabel('maximum of 100 standard Normal draws'); ax.set_title('The Gumbel constant', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_a6_gumbel')


# =============================================================================
# A7, A8: purjare si embargo pe 20 de observatii
# =============================================================================
def purge_sets(h, test_start):
    n = 20
    t1 = pd.Series(np.minimum(np.arange(n) + h, n - 1), index=np.arange(n))
    for tr, te in PurgedKFold(5, t1=t1, pct_embargo=0.05).split(np.zeros(n)):
        if te[0] == test_start:
            removed = sorted(set(range(n)) - set(tr) - set(te))
            before = [i for i in removed if i < te[0]]
            after = [i for i in removed if i > te[-1]]
            emb = [te[-1] + 1] if te[-1] + 1 < n else []
            return dict(test=[int(i) for i in te], train=[int(i) for i in tr], before=before, after=after,
                        embargo=emb, lost_share=len(removed) / (n - len(te)), t1=t1)


def a7_a8():
    res = {'A7': purge_sets(3, 8), 'A8': purge_sets(2, 12)}
    for key, h, tag, answers in (('A7', 3, 'a7_task', False), ('A7', 3, 'a7_purge', True), ('A8', 2, 'a8_purge', True)):
        r = res[key]
        fig, ax = plt.subplots(figsize=(6.0, 3.3))
        for i in range(20):
            if i in r['test']:
                c, lab = MainBlue, 'test'
            elif not answers:
                c, lab = Amber, 'not yet classified'
            elif i in r['embargo']:
                c, lab = Orange, 'embargo (its label also overlaps)'
            elif i in r['before'] or i in r['after']:
                c, lab = IDAred, 'purged: span overlaps the test labels'
            else:
                c, lab = Forest, 'train'
            ax.plot([i, r['t1'][i]], [i, i], color=c, lw=3, solid_capstyle='butt', label=lab)
            ax.plot(i, i, 'o', color=c, ms=3)
        lo, hi = r['test'][0], max(r['t1'][j] for j in r['test'])
        ax.axvspan(lo, hi, color=MainBlue, alpha=0.08)
        extra = f"; removed {len(r['before']) + len(r['after'])} of 16" if answers else ''
        ax.set_title(f"{key}: label of i ends at i + {h}; test {{{lo},...,{r['test'][-1]}}}{extra}", loc='left', fontsize=8.5)
        ax.set_xlabel('day (label span [i, i + h])'); ax.set_xticks(range(0, 20, 2))
        ax.set_ylabel('observation i'); ax.set_yticks(range(0, 20, 2)); ax.invert_yaxis()
        h_, l_, seen = [], [], set()
        for a_, b_ in zip(*ax.get_legend_handles_labels()):
            if b_ not in seen:
                h_.append(a_); l_.append(b_); seen.add(b_)
        bottom_legend(fig, ncol=2, handles=h_, labels=l_)
        save_fig('ch13_sem_' + tag)
    for r in res.values():
        r.pop('t1')
    OUT['A7A8'] = res


# =============================================================================
# A9, A10: AUC pas cu pas
# =============================================================================
def auc_by_hand(pos, neg):
    U = sum((p_ > q_) + 0.5 * (p_ == q_) for p_ in pos for q_ in neg)
    A = U / (len(pos) * len(neg))
    Q1, Q2 = A / (2 - A), 2 * A ** 2 / (1 + A)
    se = np.sqrt((A * (1 - A) + (len(pos) - 1) * (Q1 - A ** 2) + (len(neg) - 1) * (Q2 - A ** 2)) / (len(pos) * len(neg)))
    return U, A, se, (A - 0.5) / se


def a9_a10():
    pos, neg = [0.80, 0.55, 0.40], [0.60, 0.35, 0.20]
    U, A, se, z = auc_by_hand(pos, neg)
    scores = np.array(pos + neg)
    Us = []
    for comb in itertools.combinations(range(6), 3):
        p_ = scores[list(comb)]; n_ = np.delete(scores, list(comb))
        Us.append(sum((a > b) for a in p_ for b in n_))
    Us = np.array(Us)
    OUT['A9'] = dict(U=U, A=A, se=se, z=z, p_wald=float(2 * (1 - stats.norm.cdf(abs(z)))),
                     p_perm_one=float(np.mean(Us >= U)), p_perm_two=float(np.mean(np.abs(Us - 4.5) >= abs(U - 4.5))),
                     perm_dist={int(k): int(v) for k, v in zip(*np.unique(Us, return_counts=True))})
    pos4, neg4 = [0.70, 0.62, 0.48, 0.45], [0.66, 0.50, 0.40, 0.30]
    U4, A4, se4, z4 = auc_by_hand(pos4, neg4)
    M = np.array([[1.0 * (a > b) + 0.5 * (a == b) for b in neg4] for a in pos4])
    v10, v01 = M.mean(1), M.mean(0)
    se_dl = np.sqrt(np.var(v10, ddof=1) / 4 + np.var(v01, ddof=1) / 4)
    OUT['A10'] = dict(U=U4, A=A4, se_hm=se4, z=z4, V10=v10.tolist(), V01=v01.tolist(), S10=float(np.var(v10, ddof=1)),
                      S01=float(np.var(v01, ddof=1)), se_delong=float(se_dl))
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.0))
    M3 = np.array([[1.0 * (a > b) for b in neg] for a in pos])
    from matplotlib.colors import ListedColormap
    yn = ListedColormap(['#F4C7C7', '#CFE3D0'])
    axes[0].imshow(M3, cmap=yn, vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            axes[0].text(j, i, 'yes' if M3[i, j] else 'no', ha='center', va='center', color='black', fontsize=8)
    axes[0].set_xticks(range(3), [f'neg {s}' for s in neg]); axes[0].set_yticks(range(3), [f'pos {s}' for s in pos])
    axes[0].set_title(f'Is pos > neg? U = {U:.0f} of 9', loc='left')
    y = np.r_[np.ones(3), np.zeros(3)]
    fpr, tpr, _ = roc_curve(y, scores)
    axes[1].step(fpr, tpr, where='post', color=MainBlue, lw=1.5, label=f'ROC, AUC = {A:.3f}')
    axes[1].fill_between(fpr, tpr, step='post', color=MainBlue, alpha=0.12)
    axes[1].plot([0, 1], [0, 1], color='black', ls='--', lw=0.8, label='no skill')
    axes[1].set_xlabel('false positive rate'); axes[1].set_ylabel('true positive rate')
    axes[1].set_title('ROC staircase', loc='left')
    vals, cnt = np.unique(Us, return_counts=True)
    axes[2].bar(vals, cnt, color=[IDAred if v >= U else MainBlue for v in vals], width=0.7)
    axes[2].set_xlabel('U under random labels (20 allocations)'); axes[2].set_ylabel('count')
    axes[2].set_title(f'Exact null: P(U >= {U:.0f}) = {np.mean(Us >= U):.2f}', loc='left')
    axes[2].set_yticks(range(0, 4))
    from matplotlib.patches import Patch
    h_, l_ = axes[1].get_legend_handles_labels()
    h_.append(Patch(color=IDAred)); l_.append('U at least as large as observed')
    bottom_legend(fig, ncol=3, handles=h_, labels=l_)
    save_fig('ch13_sem_a9_auc')
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    from matplotlib.colors import ListedColormap
    ax.imshow(M, cmap=ListedColormap(['#F4C7C7', '#CFE3D0']), vmin=0, vmax=1)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f'{M[i, j]:.0f}', ha='center', va='center', color='black', fontsize=8)
        ax.text(4.1, i, f'{v10[i]:.2f}', ha='left', va='center', color=IDAred, fontsize=8)
    for j in range(4):
        ax.text(j, 4.0, f'{v01[j]:.2f}', ha='center', va='center', color=IDAred, fontsize=8)
    ax.set_xticks(range(4), [f'{s}' for s in neg4]); ax.set_yticks(range(4), [f'{s}' for s in pos4])
    ax.set_xlabel('negatives (column means = $V_{01}$)'); ax.set_ylabel('positives (row means = $V_{10}$)')
    ax.set_xlim(-0.5, 4.6); ax.set_ylim(4.5, -0.5)
    ax.set_title(f'A10: U = {U4:.0f} of 16, AUC = {A4:.4f}, DeLong SE = {se_dl:.3f}', loc='left', fontsize=8.5)
    plt.tight_layout()
    save_fig('ch13_sem_a10_delong')


# =============================================================================
# B1, B2: memoria BTC si ETH
# =============================================================================
def min_d_table(logp, regression='c'):
    rows = []
    for d in np.round(np.arange(0, 1.01, 0.05), 2):
        x = frac_diff_ffd(logp, d).dropna()
        res = adfuller(x, maxlag=1, regression=regression, autolag=None)
        rows.append((d, res[0], res[4]['5%'], res[1], np.corrcoef(logp.loc[x.index], x)[0, 1], len(x)))
    t = pd.DataFrame(rows, columns=['d', 'adf', 'crit_5%', 'p_value', 'corr', 'n_obs']).set_index('d')
    return t, t.index[t['adf'] < t['crit_5%']].min()


def mem(v, est):
    dh, se = est(v)
    return dict(d=float(dh), lo=float(dh - 1.96 * se), hi=float(dh + 1.96 * se), se=float(se), m=int(len(v) ** 0.65), n=len(v))


def b1():
    t, dstar = min_d_table(log_btc)
    r = log_btc.diff().dropna()
    ffd = frac_diff_ffd(log_btc, dstar)
    m = {'log price (ELW)': mem(log_btc.values, exact_local_whittle),
         f'FFD, d* = {dstar} (ELW)': mem(ffd.values, exact_local_whittle),
         'returns (LW)': mem(r.values, local_whittle), '|returns| (LW)': mem(r.abs().values, local_whittle)}
    lp = m['log price (ELW)']
    OUT['B1'] = dict(table=t.round(4).reset_index().to_dict('records'), d_star=float(dstar), wsum=float(ffd_weights(dstar).sum()),
                     K=len(ffd_weights(dstar)) - 1, ffd_n=len(ffd), ffd_start=str(ffd.index[0].date()), memory=m,
                     z_d1=(lp['d'] - 1) / lp['se'], p_d1=float(2 * (1 - stats.norm.cdf(abs((lp['d'] - 1) / lp['se'])))))
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.0), gridspec_kw={'width_ratios': [1, 0.8, 1.1]})
    ax = axes[0]
    ax.plot(t.index, t['adf'], 'o-', ms=3, color=MainBlue, label='ADF statistic (constant, 1 lag)')
    ax.axhline(t['crit_5%'].iloc[0], color=IDAred, ls='--', lw=0.9, label='5% critical value')
    ax.axvline(dstar, color='black', ls=':', lw=0.9, label=f'd* = {dstar}')
    ax.set_xlabel('FFD order d'); ax.set_ylabel('ADF statistic'); ax.set_xlim(-0.02, 0.62); ax.set_ylim(-18, 1)
    ax.set_title('ADF along d: rule picks d* = %.2f' % dstar, loc='left')
    ax = axes[1]
    ax.plot(t.index, t['corr'], 's-', ms=3, color=Forest, label='corr(FFD series, log price)')
    ax.axvline(dstar, color='black', ls=':', lw=0.9)
    ax.set_xlabel('FFD order d'); ax.set_ylim(-0.05, 1.05)
    ax.set_title('Correlation with the log price', loc='left')
    ax = axes[2]
    labs = list(m)
    for i, k in enumerate(labs):
        v = m[k]
        ax.errorbar(v['d'], i, xerr=[[v['d'] - v['lo']], [v['hi'] - v['d']]], fmt='o', color=[MainBlue, Amber, Forest, Purple][i], capsize=3)
        ax.text(v['hi'] + 0.03, i, f"{v['d']:.3f}", va='center', fontsize=7.5)
    ax.axvline(0.5, color=IDAred, ls='-.', lw=0.9, label='stationarity boundary 0.5')
    ax.axvline(1.0, color=Purple, ls=':', lw=0.9, label='unit root 1')
    ax.set_yticks(range(len(labs)), labs); ax.set_xlim(-0.15, 1.35); ax.invert_yaxis(); ax.tick_params(axis='y', labelsize=7.5)
    ax.set_xlabel(r'memory $\hat\delta$, 95% CI ($m = n^{0.65}$)')
    ax.set_title('Memory estimated directly', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b1_memory')


def b2():
    specs = {}
    for key, s, reg in (('full, constant', log_eth, 'c'), ('full, constant + trend', log_eth, 'ct'),
                        ('from 2018, constant', log_eth.loc['2018-01-01':], 'c')):
        t, ds = min_d_table(s, reg)
        specs[key] = dict(table=t, d_star=None if pd.isna(ds) else float(ds), n=len(s), start=str(s.index[0].date()),
                          end=str(s.index[-1].date()), crit=float(t['crit_5%'].iloc[0]))
    r = log_eth.diff().dropna()
    m = {'log price, full (ELW)': mem(log_eth.values, exact_local_whittle),
         'log price, from 2018 (ELW)': mem(log_eth.loc['2018-01-01':].values, exact_local_whittle),
         '|returns|, full (LW)': mem(r.abs().values, local_whittle)}
    out = {k: {kk: vv for kk, vv in v.items() if kk != 'table'} for k, v in specs.items()}
    for k, v in specs.items():
        out[k]['adf'] = {str(d): float(a) for d, a in v['table']['adf'].items()}
        out[k]['corr'] = {str(d): float(a) for d, a in v['table']['corr'].items()}
    OUT['B2'] = dict(specs=out, memory=m, dec2017=float(eth.loc['2017-12'].max()), first=float(eth.iloc[0]))
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 2.9), gridspec_kw={'width_ratios': [1.05, 1.1, 1]})
    axes[0].plot(log_eth.index, log_eth, color=Amber, lw=0.8, label='ETH-USD log close')
    axes[0].axvline(pd.Timestamp('2018-01-01'), color=IDAred, ls='--', lw=0.9, label='2018 sample start')
    axes[0].set_title('ETH log price', loc='left')
    for (k, v), c in zip(specs.items(), (MainBlue, Purple, Forest)):
        axes[1].plot(v['table'].index, v['table']['adf'], 'o-', ms=2.5, color=c, label=f"{k}: d* = {v['d_star']}")
        axes[1].axhline(v['crit'], color=c, ls=':', lw=0.8)
    axes[1].set_xlabel('FFD order d'); axes[1].set_ylabel('ADF statistic')
    axes[1].set_title('ADF rule by specification (dotted: 5% values)', loc='left')
    labs = list(m)
    for i, k in enumerate(labs):
        v = m[k]
        axes[2].errorbar(v['d'], i, xerr=[[v['d'] - v['lo']], [v['hi'] - v['d']]], fmt='o', color=[Amber, Forest, Purple][i], capsize=3)
        axes[2].text(v['hi'] + 0.03, i, f"{v['d']:.3f}", va='center', fontsize=7.5)
    axes[2].axvline(0.5, color=IDAred, ls='--', lw=0.9); axes[2].axvline(1.0, color='black', ls=':', lw=0.9)
    axes[2].set_yticks(range(len(labs)), labs); axes[2].invert_yaxis(); axes[2].set_xlim(0, 1.45)
    axes[2].set_title(r'Memory estimates, 95% CI', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b2_eth')


# =============================================================================
# B3, B4: trei bariere pe BTC
# =============================================================================
def barrier_table(settings, vol_b):
    rows, tbs = [], {}
    for pt_, sl_ in settings:
        tb = triple_barrier(btc, btc.index, vol_b, pt=pt_, sl=sl_, horizon=10)
        tbs[(pt_, sl_)] = tb
        share = tb['barrier'].value_counts(normalize=True).reindex(['upper', 'lower', 'vertical']).fillna(0)
        rows.append((f'{pt_},{sl_}', share['upper'], share['lower'], share['vertical'],
                     (tb['t1'] - tb.index).dt.days.mean(), (tb['label'] > 0).mean(), len(tb)))
    return pd.DataFrame(rows, columns=['setting', 'upper', 'lower', 'vertical', 'avg_days', 'share_+1', 'n']).set_index('setting'), tbs


def b3_b4():
    vol_b = get_daily_vol(btc)
    t3, tbs = barrier_table([(1, 1), (2, 2)], vol_b)
    fixed = np.sign(log_btc.shift(-10) - log_btc).reindex(tbs[(1, 1)].index).dropna()
    tb = tbs[(1, 1)]
    ex = tb.loc['2024-03-11'] if pd.Timestamp('2024-03-11') in tb.index else tb.iloc[len(tb) // 2]
    t0 = pd.Timestamp('2024-03-11') if pd.Timestamp('2024-03-11') in tb.index else tb.index[len(tb) // 2]
    ct = pd.crosstab(tb['barrier'], tb['label'])
    OUT['B3'] = dict(table=t3.round(4).reset_index().to_dict('records'), fixed_share_up=float((fixed > 0).mean()),
                     n_events=len(tb), first_event=str(tb.index[0].date()), last_event=str(tb.index[-1].date()),
                     vol_first_valid=str(vol_b.dropna().index[0].date()),
                     example=dict(t0=str(t0.date()), p0=float(btc.loc[t0]), sigma=float(vol_b.loc[t0]),
                                  upper=float(btc.loc[t0] * np.exp(ex['width'])), lower=float(btc.loc[t0] * np.exp(-ex['width'])),
                                  t1=str(pd.Timestamp(ex['t1']).date()), exit=ex['barrier'], ret=float(ex['ret']), label=int(ex['label'])),
                     crosstab={f'{i}|{j}': int(ct.loc[i, j]) for i in ct.index for j in ct.columns},
                     zero_ret=int((tb['ret'] == 0).sum()))
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 2.9), gridspec_kw={'width_ratios': [1.3, 0.9, 1.1]})
    seg = btc.loc[t0 - pd.Timedelta(days=5): t0 + pd.Timedelta(days=15)]
    axes[0].plot(seg.index, seg, 'o-', ms=2.5, color=MainBlue, lw=1, label='BTC close')
    up, dn = btc.loc[t0] * np.exp(ex['width']), btc.loc[t0] * np.exp(-ex['width'])
    t_end = btc.index[btc.index.get_loc(t0) + 10]
    axes[0].hlines([up, dn], t0, t_end, colors=[Forest, IDAred], linestyles='--', lw=1)
    axes[0].axvline(t_end, color=Amber, lw=1, label='vertical barrier (h = 10)')
    axes[0].plot([], [], color=Forest, ls='--', label='upper barrier'); axes[0].plot([], [], color=IDAred, ls='--', label='lower barrier')
    t1 = pd.Timestamp(ex['t1'])
    axes[0].plot(t1, btc.loc[t1], 'o', ms=8, mfc='none', mec='black', mew=1.2, label='exit')
    axes[0].axvline(t0, color='black', ls=':', lw=0.8)
    axes[0].set_title(f'One event: t0 = {t0.date()}, {ex["barrier"]} exit, label {int(ex["label"]):+d}', loc='left', fontsize=8.5)
    axes[0].tick_params(axis='x', labelsize=7, rotation=30)
    x = np.arange(2)
    for j, (col, c) in enumerate((('upper', Forest), ('lower', IDAred), ('vertical', Amber))):
        axes[1].bar(x + (j - 1) * 0.26, t3[col].values, 0.26, color=c, label=f'{col} exit')
    axes[1].set_xticks(x, ['pt = sl = 1', 'pt = sl = 2']); axes[1].set_ylabel('share of events')
    axes[1].set_title('Exit shares', loc='left')
    for j, (k, c) in enumerate(zip(tbs, (MainBlue, Amber))):
        hd = (tbs[k]['t1'] - tbs[k].index).dt.days
        cnt = np.bincount(hd, minlength=11)[1:11] / len(hd)
        axes[2].bar(np.arange(1, 11) + (j - 0.5) * 0.4, cnt, 0.4, color=c, label=f'holding days, pt = sl = {k[0]}')
    axes[2].set_ylabel('share of events')
    axes[2].set_xlabel('calendar days until exit'); axes[2].set_title('Holding periods', loc='left')
    bottom_legend(fig, ncol=4)
    save_fig('ch13_sem_b3_barriers')
    # ---------------- B4
    t4, _ = barrier_table([(2, 1), (1, 2)], vol_b)
    t4['upper_share_horizontal'] = t4['upper'] / (t4['upper'] + t4['lower'])
    rng = np.random.default_rng(SEED)
    r_btc = log_btc.diff().dropna()
    mu_b = r_btc.mean() / r_btc.std()
    sim = {}
    for pt_, sl_ in ((2, 1), (1, 2)):
        for mu_ in (0.0, mu_b):
            xx = np.cumsum(rng.normal(mu_, 1, (400_000, 10)), 1)
            hit_u, hit_d = xx >= pt_ * np.sqrt(10), xx <= -sl_ * np.sqrt(10)
            fu = np.where(hit_u.any(1), hit_u.argmax(1), 99); fd = np.where(hit_d.any(1), hit_d.argmax(1), 99)
            U, D = ((fu < fd) & (fu < 99)).mean(), ((fd < fu) & (fd < 99)).mean()
            sh = U / (U + D)
            sim[f'{pt_},{sl_}|{mu_:.3f}'] = dict(U=float(U), D=float(D), share=float(sh),
                                                 se=float(np.sqrt(sh * (1 - sh) / (400_000 * (U + D)))))
    OUT['B4'] = dict(table=t4.round(4).reset_index().to_dict('records'), sim=sim, mu_over_sigma=float(mu_b))
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    groups = ['2,1', '1,2']
    x = np.arange(2)
    inf = [1 / 3, 2 / 3]
    s0 = [sim[f'{g}|0.000']['share'] for g in groups]
    s1 = [sim[f'{g}|{mu_b:.3f}']['share'] for g in groups]
    bt = [t4.loc[g, 'upper_share_horizontal'] for g in groups]
    for j, (v, c, lab) in enumerate(((inf, Purple, 'infinite horizon, no drift: sl/(pt+sl)'),
                                     (s0, MainBlue, 'Gaussian daily steps, h = 10, no drift'),
                                     (s1, Teal, f'Gaussian, h = 10, BTC drift ({mu_b:.3f} sigma/day)'),
                                     (bt, Amber, 'BTC 2014-2026'))):
        ax.bar(x + (j - 1.5) * 0.2, v, 0.2, color=c, label=lab)
        for xi, vi in zip(x, v):
            ax.text(xi + (j - 1.5) * 0.2, vi + 0.02, f'{vi:.2f}', ha='center', fontsize=7)
    ax.set_xticks(x, ['(pt, sl) = (2, 1)', '(pt, sl) = (1, 2)']); ax.set_ylim(0, 1.05)
    ax.set_ylabel('upper / (upper + lower)')
    ax.set_title('Upper exits among horizontal exits', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_b4_asym')


# =============================================================================
# B5: PurgedKFold vs K-fold cu amestecare
# =============================================================================
def b5():
    rng = np.random.default_rng(SEED)
    n, h = 3000, 20
    p = pd.Series(np.cumsum(rng.normal(0, 0.01, n + h)))
    y_leak = (p.shift(-h) - p > 0).astype(int).iloc[:n].values
    X_leak = np.column_stack([pd.Series(rng.normal(size=n + h)).rolling(h).mean().bfill().iloc[:n] for _ in range(5)])
    t1_leak = pd.Series(np.arange(n) + h, index=np.arange(n))
    schemes = {'K-fold, shuffled': KFold(5, shuffle=True, random_state=SEED),
               'K-fold, contiguous': KFold(5, shuffle=False),
               'purged K-fold, 1% embargo': PurgedKFold(5, t1=t1_leak, pct_embargo=0.01)}
    model = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1, random_state=SEED)
    ex5, ntrain = {}, {}
    for name, cv_ in schemes.items():
        ex5[name], ntrain[name] = [], []
        for tr, te in cv_.split(X_leak):
            ex5[name].append(accuracy_score(y_leak[te], model.fit(X_leak[tr], y_leak[tr]).predict(X_leak[te])))
            ntrain[name].append(len(tr))
    OUT['B5'] = dict(folds={k: [float(x) for x in v] for k, v in ex5.items()}, mean={k: float(np.mean(v)) for k, v in ex5.items()},
                     ntrain=ntrain, share_up=float(y_leak.mean()), embargo=int(n * 0.01))
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    cols = [IDAred, Amber, Forest]
    for i, (k, v) in enumerate(ex5.items()):
        ax.bar(i, np.mean(v), 0.6, color=cols[i], alpha=0.85, label=f'{k}: mean {np.mean(v):.1%}')
        ax.scatter(np.full(5, i) + np.linspace(-0.15, 0.15, 5), v, color='black', s=12, zorder=3,
                   label='single folds' if i == 0 else None)
    ax.axhline(0.5, color='black', ls='--', lw=0.9, label='truth: 50%')
    ax.set_xticks(range(3), list(ex5)); ax.set_ylim(0.35, 0.8); ax.set_ylabel('out-of-fold accuracy')
    ax.set_title('Random forest on pure noise (3,000 days, 20-day labels)', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_b5_cv')


# =============================================================================
# CADRUL DE MODELARE B6-B8, B12, B14
# =============================================================================
H = 5


def frame_b():
    feats_b = build_features(btc)
    FB = list(feats_b.columns)
    dfb = feats_b.assign(fwd=log_btc.shift(-H) - log_btc).dropna()
    dfb['y'] = (dfb['fwd'] > 0).astype(int)
    pos = np.searchsorted(btc.index, dfb.index)
    dfb['t1'] = btc.index[np.minimum(pos + H, len(btc) - 1)]
    return dfb, FB


def b6():
    dfb, FB = frame_b()
    r1 = log_btc.diff()
    df6 = dfb.copy()
    df6['ma11'] = r1.rolling(11, center=True).mean().reindex(df6.index)
    df6 = df6.dropna()
    rf6 = RandomForestClassifier(n_estimators=300, min_samples_leaf=50, max_features='sqrt', n_jobs=-1, random_state=SEED)
    cv6 = PurgedKFold(5, t1=df6['t1'], pct_embargo=0.01)

    def purged_oos(cols):
        Xs, ys = df6[cols].values, df6['y'].values
        pr = np.full(len(ys), np.nan)
        for tr, te in cv6.split(Xs):
            pr[te] = rf6.fit(Xs[tr], ys[tr]).predict_proba(Xs[te])[:, 1]
        return accuracy_score(ys, pr > 0.5), roc_auc_score(ys, pr)

    res = {'leaky': purged_oos(FB + ['ma11'])}
    rf6.fit(df6[FB + ['ma11']].values, df6['y'].values)
    mdi = pd.Series(rf6.feature_importances_, index=FB + ['ma11']).sort_values(ascending=False)
    df6['ma11_trailing'] = r1.rolling(11).mean().reindex(df6.index)
    res['base'] = purged_oos(FB)
    res['trailing'] = purged_oos(FB + ['ma11_trailing'])
    OUT['B6'] = dict(n=len(df6), start=str(df6.index[0].date()), end=str(df6.index[-1].date()),
                     res={k: [float(a) for a in v] for k, v in res.items()},
                     mdi_top={k: float(v) for k, v in mdi.head(3).items()},
                     corr_centred=float(df6['ma11'].corr(df6['fwd'])), corr_trailing=float(df6['ma11_trailing'].corr(df6['fwd'])))
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 2.8), gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axes[0]
    days = np.arange(-6, 7)
    for dd in days:
        if -5 <= dd <= 5:
            ax.add_patch(Rectangle((dd - 0.45, 1.6), 0.9, 0.7, color=IDAred if dd >= 1 else MainBlue, alpha=0.8))
        if -10 <= dd <= 0 and dd >= -6:
            ax.add_patch(Rectangle((dd - 0.45, 0.6), 0.9, 0.7, color=MainBlue, alpha=0.8))
        if 1 <= dd <= 5:
            ax.add_patch(Rectangle((dd - 0.45, -0.4), 0.9, 0.7, color=Amber, alpha=0.9))
    ax.text(-6.6, 1.95, 'ma11 (centred)', ha='right', va='center', fontsize=8)
    ax.text(-6.6, 0.95, 'ma11 (trailing)', ha='right', va='center', fontsize=8)
    ax.text(-6.6, -0.05, 'target: r(t+1..t+5)', ha='right', va='center', fontsize=8)
    ax.axvline(0.5, color='black', ls='--', lw=1)
    ax.text(0.6, 2.55, 'decision time t', fontsize=8)
    ax.set_xlim(-11.5, 6.8); ax.set_ylim(-0.7, 2.8); ax.set_yticks([])
    ax.set_xticks(range(-6, 7)); ax.set_xticklabels([f'{d:+d}' if d else 't' for d in range(-6, 7)], fontsize=7)
    ax.add_patch(Rectangle((0, 0), 0, 0, color=MainBlue, label='return known at t'))
    ax.add_patch(Rectangle((0, 0), 0, 0, color=IDAred, label='future return inside the feature'))
    ax.add_patch(Rectangle((0, 0), 0, 0, color=Amber, label='returns of the target'))
    ax.set_title('Which daily returns enter each feature on day t (trailing window shown from t-6)', loc='left', fontsize=8)
    ax = axes[1]
    labs = ['11 base + ma11 (centred)', '11 base + ma11 (trailing)', '11 base features']
    keys = ['leaky', 'trailing', 'base']
    x = np.arange(3)
    ax.bar(x - 0.18, [res[k][0] for k in keys], 0.36, color=MainBlue, label='accuracy')
    ax.bar(x + 0.18, [res[k][1] for k in keys], 0.36, color=Forest, label='AUC')
    for xi, k in zip(x, keys):
        ax.text(xi - 0.18, res[k][0] + 0.01, f'{res[k][0]:.3f}', ha='center', fontsize=7)
        ax.text(xi + 0.18, res[k][1] + 0.01, f'{res[k][1]:.3f}', ha='center', fontsize=7)
    ax.axhline(0.5, color='black', ls='--', lw=0.8, label='coin flip / no ranking')
    ax.set_xticks(x, labs, fontsize=7); ax.set_ylim(0.4, 0.95)
    ax.set_title('Purged 5-fold CV, BTC 5-day direction', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b6_leak')


def b7_b8_b12():
    dfb, FB = frame_b()
    Xb, yb = dfb[FB].values, dfb['y'].values
    models = {
        'Logit-L1': make_pipeline(StandardScaler(), LogisticRegression(penalty='l1', C=0.05, solver='liblinear', random_state=SEED)),
        'Random Forest': RandomForestClassifier(n_estimators=400, min_samples_leaf=50, max_features='sqrt', n_jobs=-1, random_state=SEED),
        'Gradient Boosting': HistGradientBoostingClassifier(max_depth=3, learning_rate=0.03, max_iter=200, min_samples_leaf=50, random_state=SEED),
    }
    cv = PurgedKFold(5, t1=dfb['t1'], pct_embargo=0.01)
    oos = {k: np.full(len(yb), np.nan) for k in models}
    const = np.full(len(yb), np.nan)
    fold = np.full(len(yb), -1)
    rows, folds = [], {}
    for name, m in models.items():
        acc, auc, base, upsh = [], [], [], []
        for f_, (tr, te) in enumerate(cv.split(Xb)):
            prob = m.fit(Xb[tr], yb[tr]).predict_proba(Xb[te])[:, 1]
            oos[name][te] = prob; const[te] = yb[tr].mean(); fold[te] = f_
            acc.append(accuracy_score(yb[te], prob > 0.5)); auc.append(roc_auc_score(yb[te], prob))
            base.append(max(yb[te].mean(), 1 - yb[te].mean())); upsh.append(yb[te].mean())
        folds[name] = dict(acc=acc, auc=auc)
        rows.append(dict(model=name, acc=float(np.mean(acc)), acc_sd=float(np.std(acc)), auc=float(np.mean(auc)),
                         auc_sd=float(np.std(auc)), majority_oracle=float(np.mean(base)), always_up=float(np.mean(upsh)),
                         pooled_auc=float(roc_auc_score(yb, oos[name])), pooled_acc=float(accuracy_score(yb, oos[name] > 0.5)),
                         share_pred_up=float(np.mean(oos[name] > 0.5))))
    fold_up = [float(yb[fold == f_].mean()) for f_ in range(5)]
    fold_dates = [(str(dfb.index[fold == f_][0].date()), str(dfb.index[fold == f_][-1].date()), int((fold == f_).sum())) for f_ in range(5)]
    OUT['B7'] = dict(n=len(yb), share_up=float(yb.mean()), start=str(dfb.index[0].date()), end=str(dfb.index[-1].date()),
                     rows=rows, folds=folds, fold_up=fold_up, fold_dates=fold_dates, embargo=int(len(yb) * 0.01))
    # --- importanta (impartire separata 70/30, ca in notebook)
    split = int(len(dfb) * 0.7)
    gap = split + H + int(0.01 * len(dfb))
    Xbdf = dfb[FB]
    rf = RandomForestClassifier(n_estimators=400, min_samples_leaf=50, max_features='sqrt', n_jobs=-1,
                                random_state=SEED).fit(Xbdf.iloc[:split], yb[:split])
    mdi = pd.Series(rf.feature_importances_, index=FB)
    mda = pd.Series(permutation_importance(rf, Xbdf.iloc[gap:], yb[gap:], scoring='roc_auc', n_repeats=10,
                                           random_state=SEED, n_jobs=-1).importances_mean, index=FB)
    try:
        import shap
        sv = shap.TreeExplainer(rf).shap_values(Xbdf.iloc[gap:].sample(300, random_state=SEED))
        sv = sv[1] if isinstance(sv, list) else (sv[..., 1] if np.ndim(sv) == 3 else sv)
        shp = pd.Series(np.abs(sv).mean(0), index=FB)
    except Exception as e:  # pragma: no cover
        print('SHAP skipped:', e); shp = pd.Series(np.nan, index=FB)
    imp = pd.DataFrame({'MDI': mdi, 'MDA': mda, 'SHAP': shp}).sort_values('MDI')
    sp = imp.corr(method='spearman')
    OUT['B7imp'] = dict(split_date=str(dfb.index[split].date()), test_start=str(dfb.index[gap].date()),
                        imp=imp.round(5).to_dict(), spearman=dict(MDI_SHAP=float(sp.loc['MDI', 'SHAP']),
                        MDI_MDA=float(sp.loc['MDI', 'MDA']), MDA_SHAP=float(sp.loc['MDA', 'SHAP'])))
    fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.1), sharey=True)
    axes[0].barh(imp.index, imp['MDI'], color=MainBlue); axes[0].set_title('MDI (in sample)', loc='left')
    axes[1].barh(imp.index, imp['MDA'], color=np.where(imp['MDA'] > 0, Forest, IDAred))
    axes[1].axvline(0, color='black', lw=0.7); axes[1].set_title('MDA: AUC drop (out of sample)', loc='left')
    axes[2].barh(imp.index, imp['SHAP'], color=Amber); axes[2].set_title('mean |SHAP| (out of sample)', loc='left')
    axes[1].barh([], [], color=Forest, label='MDA > 0: helps'); axes[1].barh([], [], color=IDAred, label='MDA < 0: hurts')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_b7_importance')
    # --- grafic modele
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 2.8))
    names = list(models)
    x = np.arange(3)
    for ax, key, lab in ((axes[0], 'acc', 'accuracy'), (axes[1], 'auc', 'ROC AUC')):
        v = [np.mean(folds[k][key]) for k in names]
        ax.bar(x, v, 0.55, color=[MainBlue, Forest, Amber])
        for i, k in enumerate(names):
            ax.scatter(np.full(5, i) + np.linspace(-0.15, 0.15, 5), folds[k][key], color='black', s=10, zorder=3,
                       label='single folds' if i == 0 else None)
            ax.text(i, v[i] + 0.012, f'{v[i]:.3f}', ha='center', fontsize=7.5)
        ax.set_xticks(x, names); ax.set_title(f'{lab}, mean of 5 purged folds', loc='left')
    axes[0].axhline(yb.mean(), color=IDAred, ls='--', lw=0.9, label=f'always up: {yb.mean():.1%} (share of up labels)')
    axes[0].set_ylim(0.4, 0.66)
    axes[1].axhline(0.5, color='black', ls='--', lw=0.9, label='AUC 0.5: no ranking')
    axes[1].set_ylim(0.4, 0.62)
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b7_models')
    # --- CI pentru AUC
    s_rf = oos['Random Forest']
    pos, neg = s_rf[yb == 1], s_rf[yb == 0]
    m1, n0 = len(pos), len(neg)
    rk = stats.rankdata(np.concatenate([pos, neg]))
    auc_rf = (rk[:m1].sum() - m1 * (m1 + 1) / 2) / (m1 * n0)
    v10 = (rk[:m1] - stats.rankdata(pos)) / n0
    v01 = 1 - (rk[m1:] - stats.rankdata(neg)) / m1
    se_d = np.sqrt(np.var(v10, ddof=1) / m1 + np.var(v01, ddof=1) / n0)
    rng = np.random.default_rng(SEED)
    boot = {}
    for L in (1, 20, 60):
        bs = []
        for _ in range(1000):
            starts = rng.integers(0, len(yb), int(np.ceil(len(yb) / L)))
            i = ((starts[:, None] + np.arange(L)[None, :]).ravel() % len(yb))[:len(yb)]
            if yb[i].min() == yb[i].max():
                continue
            bs.append(roc_auc_score(yb[i], s_rf[i]))
        boot[L] = np.array(bs)
    OUT['B7auc'] = dict(auc=float(auc_rf), se_delong=float(se_d), z=float((auc_rf - 0.5) / se_d),
                        p=float(2 * (1 - stats.norm.cdf(abs(auc_rf - 0.5) / se_d))),
                        boot={str(L): dict(se=float(b.std()), lo=float(np.quantile(b, .025)), hi=float(np.quantile(b, .975)),
                                           share_le_half=float(np.mean(b <= 0.5)), n=len(b)) for L, b in boot.items()})
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 2.8), gridspec_kw={'width_ratios': [1, 1.2]})
    ivs = [('DeLong (independent)', auc_rf - 1.96 * se_d, auc_rf + 1.96 * se_d, MainBlue)]
    for L, c in ((1, Teal), (20, Amber), (60, Purple)):
        ivs.append((f'block bootstrap, L = {L}', np.quantile(boot[L], .025), np.quantile(boot[L], .975), c))
    for i, (lab, lo, hi, c) in enumerate(ivs):
        axes[0].errorbar(auc_rf, i, xerr=[[auc_rf - lo], [hi - auc_rf]], fmt='o', color=c, capsize=3)
        axes[0].text(hi + 0.002, i, f'[{lo:.3f}; {hi:.3f}]', va='center', fontsize=7)
    axes[0].axvline(0.5, color=IDAred, ls='--', lw=0.9, label='AUC 0.5')
    axes[0].set_yticks(range(len(ivs)), [v[0] for v in ivs]); axes[0].invert_yaxis(); axes[0].set_xlim(0.47, 0.57)
    axes[0].set_title(f'RF pooled AUC = {auc_rf:.3f}: 95% intervals', loc='left')
    axes[1].hist(boot[1], bins=40, alpha=0.55, color=Teal, label='bootstrap AUC, L = 1')
    axes[1].hist(boot[20], bins=40, alpha=0.55, color=Amber, label='bootstrap AUC, L = 20')
    axes[1].axvline(0.5, color=IDAred, ls='--', lw=0.9)
    axes[1].axvline(auc_rf, color='black', lw=0.9, label='observed pooled AUC')
    axes[1].set_xlabel('estimator distribution (not a null distribution)')
    axes[1].set_title('Serial dependence widens the distribution', loc='left')
    bottom_legend(fig, ncol=4)
    save_fig('ch13_sem_b7_auc')

    # --- B8: Diebold--Mariano pe log loss
    def ll(p_, y):
        p_ = np.clip(p_, 1e-6, 1 - 1e-6)
        return -(y * np.log(p_) + (1 - y) * np.log(1 - p_))
    losses = {k: float(log_loss(yb, v)) for k, v in {**oos, 'constant': const}.items()}
    order = np.argsort(dfb.index.values)
    dm, dser = {}, {}
    ex_i = 100
    example = dict(date=str(dfb.index[ex_i].date()), y=int(yb[ex_i]), p={k: float(v[ex_i]) for k, v in {**oos, 'constant': const}.items()},
                   loss={k: float(ll(np.array([v[ex_i]]), np.array([yb[ex_i]]))[0]) for k, v in {**oos, 'constant': const}.items()})
    for a_, b_ in (('Random Forest', 'Logit-L1'), ('Random Forest', 'constant'), ('Gradient Boosting', 'constant')):
        d = ll(oos[a_], yb) - ll(const if b_ == 'constant' else oos[b_], yb)
        dser[f'{a_} - {b_}'] = d
        row = dict(mean=float(d.mean()), naive_t=float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))))
        for L in (4, 20):
            mu_, se_, t_, p_ = hac_mean(d, L)
            row[f'lag{L}'] = dict(se=float(se_), t=float(t_), p=float(p_))
        dm[f'{a_} - {b_}'] = row
    OUT['B8'] = dict(logloss=losses, dm=dm, example=example)
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 2.8), gridspec_kw={'width_ratios': [1.35, 1]})
    cols = [MainBlue, Forest, IDAred]
    for (k, d), c in zip(dser.items(), cols):
        axes[0].plot(dfb.index, np.cumsum(d), color=c, lw=0.9, label=k)
    axes[0].axhline(0, color='black', lw=0.7)
    axes[0].set_ylabel('cumulative loss difference')
    axes[0].set_title('Cumulative log-loss differential (> 0: first model worse)', loc='left', fontsize=8.5)
    for i, ((k, r), c) in enumerate(zip(dm.items(), cols)):
        for j, L in enumerate((4, 20)):
            se_ = r[f'lag{L}']['se']
            axes[1].errorbar(r['mean'], i + (j - 0.5) * 0.25, xerr=1.96 * se_, fmt='o' if L == 4 else 's', color=c, capsize=3)
    axes[1].errorbar([], [], xerr=[], fmt='o', color='black', label='HAC 95% CI, 4 lags')
    axes[1].errorbar([], [], xerr=[], fmt='s', color='black', label='HAC 95% CI, 20 lags')
    axes[1].axvline(0, color='black', ls='--', lw=0.8)
    axes[1].set_yticks(range(3), list(dm)); axes[1].invert_yaxis(); axes[1].tick_params(axis='y', labelsize=7)
    axes[1].set_xlabel('mean loss differential')
    axes[1].set_title('Diebold-Mariano intervals', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b8_dm')

    # --- B12: Pesaran--Timmermann si Clark--West
    def pesaran_timmermann(y, x):
        n = len(y); P = np.mean(y == x); py, px = y.mean(), x.mean()
        Ps = py * px + (1 - py) * (1 - px)
        VP = Ps * (1 - Ps) / n
        VPs = (2 * py - 1) ** 2 * px * (1 - px) / n + (2 * px - 1) ** 2 * py * (1 - py) / n + 4 * py * px * (1 - py) * (1 - px) / n ** 2
        return P, Ps, (P - Ps) / np.sqrt(VP - VPs)
    pt = {}
    for name, pr in oos.items():
        xx = (pr > 0.5).astype(int)
        P, Ps, s = pesaran_timmermann(yb, xx)
        t_hac = sm.OLS(yb, sm.add_constant(xx)).fit(cov_type='HAC', cov_kwds={'maxlags': 4}).tvalues[1]
        pt[name] = dict(pred_up=float(xx.mean()), P=float(P), Ps=float(Ps), PT=float(s), t_hac=float(t_hac),
                        p_hac=float(2 * (1 - stats.norm.cdf(abs(t_hac)))))
    p1, p0 = oos['Logit-L1'], const
    f = (yb - p0) ** 2 - ((yb - p1) ** 2 - (p0 - p1) ** 2)
    _, _, cw_t, _ = hac_mean(f, 4)
    _, _, dm_t, dm_p = hac_mean((yb - p1) ** 2 - (yb - p0) ** 2, 4)
    OUT['B12'] = dict(pt=pt, cw_t=float(cw_t), cw_p=float(1 - stats.norm.cdf(cw_t)), dm_brier_t=float(dm_t), dm_brier_p=float(dm_p))
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    x = np.arange(3)
    ax.bar(x - 0.18, [pt[k]['P'] for k in names], 0.36, color=MainBlue, label='observed accuracy $\\hat P$')
    ax.bar(x + 0.18, [pt[k]['Ps'] for k in names], 0.36, color=Amber, label='expected under independence $\\hat P^*$')
    for i, k in enumerate(names):
        ax.text(i, max(pt[k]['P'], pt[k]['Ps']) + 0.006, f"PT = {pt[k]['PT']:.2f}, HAC t = {pt[k]['t_hac']:.2f}", ha='center', fontsize=7)
    ax.axhline(yb.mean(), color=IDAred, ls='--', lw=0.9, label=f'always up {yb.mean():.3f}')
    ax.set_xticks(x, names); ax.set_ylim(0.48, 0.58)
    ax.set_title('Sign accuracy: observed vs. independence benchmark', loc='left')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b12_pt')
    return dfb, FB


# =============================================================================
# B9: meta-etichetare
# =============================================================================
def b9():
    side = np.sign(btc.rolling(20).mean() - btc.rolling(50).mean())
    feats_m = build_features(btc)
    valid = feats_m.dropna().index.intersection(side[side != 0].dropna().index)
    events_m = valid[valid <= btc.index[-13]]
    tb_m = triple_barrier(btc, events_m, get_daily_vol(btc), pt=1.0, sl=1.0, horizon=10)
    meta = pd.DataFrame({'side': side.reindex(tb_m.index), 't1': tb_m['t1']})
    meta['ret_side'] = tb_m['ret'] * meta['side']
    meta['y'] = (meta['ret_side'] > 0).astype(int)
    Xm = feats_m.reindex(meta.index).assign(side=meta['side'])
    split = int(0.6 * len(meta)); test0 = split + 10
    rf_meta = RandomForestClassifier(n_estimators=400, min_samples_leaf=50, max_features='sqrt', class_weight='balanced',
                                     n_jobs=-1, random_state=SEED)
    rf_meta.fit(Xm.iloc[:split], meta['y'].iloc[:split])
    test = meta.iloc[test0:]
    prob = rf_meta.predict_proba(Xm.iloc[test0:])[:, 1]
    take = prob > 0.5
    ym = test['y'].values
    p0 = ym.mean()
    tp, fp = int(((take == 1) & (ym == 1)).sum()), int(((take == 1) & (ym == 0)).sum())
    fn, tn = int(((take == 0) & (ym == 1)).sum()), int(((take == 0) & (ym == 0)).sum())
    OUT['B9'] = dict(n_events=len(meta), train_end=str(meta.index[split - 1].date()), test_start=str(test.index[0].date()),
                     test_end=str(test.index[-1].date()), n_test=len(test), take_share=float(take.mean()),
                     before=dict(prec=float(p0), rec=1.0, f1=float(2 * p0 / (1 + p0)), n=len(ym), ret=float(test['ret_side'].mean())),
                     after=dict(prec=float(precision_score(ym, take)), rec=float(recall_score(ym, take)), f1=float(f1_score(ym, take)),
                                n=int(take.sum()), ret=float(test['ret_side'][take].mean())),
                     skipped_ret=float(test['ret_side'][~take].mean()), confusion=dict(tp=tp, fp=fp, fn=fn, tn=tn),
                     long_share=float((test['side'] > 0).mean()))
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 2.8))
    b, a = OUT['B9']['before'], OUT['B9']['after']
    x = np.arange(3)
    axes[0].bar(x - 0.18, [b['prec'], b['rec'], b['f1']], 0.36, color=MainBlue, label=f"primary only: all {b['n']} trades")
    axes[0].bar(x + 0.18, [a['prec'], a['rec'], a['f1']], 0.36, color=Forest, label=f"+ meta-model: {a['n']} trades kept")
    for xi, v1, v2 in zip(x, [b['prec'], b['rec'], b['f1']], [a['prec'], a['rec'], a['f1']]):
        axes[0].text(xi - 0.18, v1 + 0.02, f'{v1:.3f}', ha='center', fontsize=7); axes[0].text(xi + 0.18, v2 + 0.02, f'{v2:.3f}', ha='center', fontsize=7)
    axes[0].set_xticks(x, ['precision', 'recall', 'F1']); axes[0].set_ylim(0, 1.12)
    axes[0].set_title('Test period %s to %s' % (test.index[0].strftime('%Y-%m'), test.index[-1].strftime('%Y-%m')), loc='left')
    bins = np.linspace(-0.3, 0.3, 41)
    axes[1].hist(test['ret_side'][take], bins=bins, alpha=0.6, color=Forest, label=f"kept: mean {a['ret']:+.2%}")
    axes[1].hist(test['ret_side'][~take], bins=bins, alpha=0.6, color=IDAred, label=f"skipped: mean {OUT['B9']['skipped_ret']:+.2%}")
    axes[1].axvline(0, color='black', lw=0.7)
    axes[1].set_xlabel('gross log return per trade, before costs (overlapping trades)')
    axes[1].set_title('Returns of kept and skipped trades', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_b9_meta')


# =============================================================================
# B10, B11, B13: grila de 120 de reguli
# =============================================================================
def grid_returns():
    r_b = log_btc.diff()
    rets = {}
    for fast in range(5, 60, 5):
        for slow in range(20, 260, 20):
            if slow <= fast:
                continue
            ma_f, ma_s = log_btc.rolling(fast).mean(), log_btc.rolling(slow).mean()
            sig = (ma_f > ma_s).astype(float).where(ma_s.notna()).shift(1)
            rets[(fast, slow)] = sig * r_b
    return pd.DataFrame(rets).dropna(), r_b


def b10_b11_b13():
    R, r_b = grid_returns()
    N, T10 = R.shape[1], len(R)
    srs = R.mean() / R.std()
    best = srs.idxmax(); s_best = R[best]
    sk, ku = stats.skew(s_best), stats.kurtosis(s_best, fisher=False)
    bh = r_b.loc[R.index]
    C = np.corrcoef(R.values.T)
    lam = np.linalg.eigvalsh(C)[::-1]
    n_pr = lam.sum() ** 2 / (lam ** 2).sum()
    n95 = int(np.searchsorted(np.cumsum(lam) / lam.sum(), 0.95) + 1)
    rho_bar = (C.sum() - N) / (N * (N - 1)); n_rho = rho_bar + (1 - rho_bar) * N
    tab = []
    for label, Nx in (('N = 120', N), ('N_hat', n_rho), ('95% eigen', n95)):
        for vlab, sd in (('1/T', np.sqrt(1 / T10)), ('trials', srs.std())):
            tab.append(dict(case=label, N=float(Nx), V=vlab, SR0_ann=float(expected_max_sharpe(max(Nx, 1.0001), sd) * np.sqrt(365)),
                            DSR=float(dsr(srs[best], T10, max(Nx, 1.0001), sd, sk, ku))))
    OUT['B10'] = dict(N=N, T=T10, start=str(R.index[0].date()), end=str(R.index[-1].date()), best=list(best),
                      sr_best_ann=float(srs[best] * np.sqrt(365)), sr_best_daily=float(srs[best]),
                      sr_bh_ann=float(bh.mean() / bh.std() * np.sqrt(365)), skew=float(sk), kurt=float(ku),
                      psr0=float(psr(srs[best], 0, T10, sk, ku)), lam1=float(lam[0]), lam1_share=float(lam[0] / lam.sum()),
                      pr=float(n_pr), n95=n95, rho_bar=float(rho_bar), n_hat=float(n_rho), table=tab,
                      sr_trials_sd_ann=float(srs.std() * np.sqrt(365)), exposure_best=float((R[best] != 0).mean()))
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.1), gridspec_kw={'width_ratios': [1.25, 0.9, 1.1]})
    fasts, slows = sorted({k[0] for k in srs.index}), sorted({k[1] for k in srs.index})
    Mh = np.full((len(fasts), len(slows)), np.nan)
    for (f_, s_), v in srs.items():
        Mh[fasts.index(f_), slows.index(s_)] = v * np.sqrt(365)
    im = axes[0].imshow(Mh, cmap='viridis', aspect='auto', origin='lower')
    axes[0].set_xticks(range(len(slows)), slows, fontsize=6.5); axes[0].set_yticks(range(len(fasts)), fasts, fontsize=7)
    axes[0].set_xlabel('slow window (days)'); axes[0].set_ylabel('fast window (days)')
    axes[0].plot(slows.index(best[1]), fasts.index(best[0]), '*', color=IDAred, ms=12, label=f'selected rule ({int(best[0])}, {int(best[1])}): SR {srs[best] * np.sqrt(365):.2f}')
    plt.colorbar(im, ax=axes[0], fraction=0.046, pad=0.02).set_label('annualised SR', fontsize=7)
    axes[0].set_title('Sharpe ratio of the 120 rules', loc='left')
    axes[1].bar(np.arange(1, 11), lam[:10] / lam.sum(), color=MainBlue, label='share of variance')
    axes[1].plot(np.arange(1, 11), np.cumsum(lam[:10]) / lam.sum(), 'o-', ms=3, color=Amber, label='cumulative share')
    axes[1].axhline(0.95, color=IDAred, ls='--', lw=0.8, label='95%')
    axes[1].set_xlabel('eigenvalue rank'); axes[1].set_title('Scree of the trial correlations', loc='left')
    Ns = np.unique(np.round(np.logspace(0.05, np.log10(120), 60), 2))
    for sd, c, lab in ((np.sqrt(1 / T10), MainBlue, 'V = 1/T (independent trials)'), (srs.std(), Forest, 'V = dispersion of the 120 SRs')):
        axes[2].plot(Ns, [dsr(srs[best], T10, n_, sd, sk, ku) for n_ in Ns], color=c, lw=1.2, label=lab)
    for n_, lab in ((N, 'N = 120'), (n_rho, 'N_hat = %.1f' % n_rho), (n95, '95%% eigen: %d' % n95)):
        axes[2].axvline(n_, color='black', ls=':', lw=0.7)
        axes[2].text(n_, 0.905, lab, rotation=90, fontsize=6.5, va='bottom', ha='right')
    axes[2].axhline(0.95, color=IDAred, ls='--', lw=0.8, label='0.95 threshold')
    axes[2].set_xscale('log'); axes[2].set_ylim(0.9, 1.002); axes[2].set_xlabel('number of trials N')
    axes[2].set_title('DSR of the selected rule', loc='left')
    bottom_legend(fig, ncol=4)
    save_fig('ch13_sem_b10_grid')
    # ---------------- B11 CSCV
    from itertools import combinations
    S = 16
    blocks = np.array_split(np.arange(len(R)), S)
    Rv = R.values
    logits, sr_is, sr_oos = [], [], []
    for comb in combinations(range(S), S // 2):
        ins = np.concatenate([blocks[i] for i in comb])
        outs = np.concatenate([blocks[i] for i in range(S) if i not in comb])
        a_, b_ = Rv[ins], Rv[outs]
        s_in, s_out = a_.mean(0) / a_.std(0), b_.mean(0) / b_.std(0)
        k = np.argmax(s_in)
        w = stats.rankdata(s_out)[k] / (N + 1)
        logits.append(np.log(w / (1 - w))); sr_is.append(s_in[k]); sr_oos.append(s_out[k])
    logits, sr_is, sr_oos = map(np.array, (logits, sr_is, sr_oos))
    OUT['B11'] = dict(splits=len(logits), pbo=float(np.mean(logits <= 0)), median_logit=float(np.median(logits)),
                      med_is=float(np.median(sr_is) * np.sqrt(365)), med_oos=float(np.median(sr_oos) * np.sqrt(365)),
                      p_neg=float(np.mean(sr_oos < 0)), block_sizes=sorted({len(b) for b in blocks}))
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 2.8))
    bins = np.linspace(logits.min(), logits.max(), 45)
    axes[0].hist(logits[logits <= 0], bins=bins, color=IDAred, alpha=0.8, label=f'winner at or below the OOS median: PBO = {np.mean(logits <= 0):.3f}')
    axes[0].hist(logits[logits > 0], bins=bins, color=MainBlue, alpha=0.8, label='winner above the OOS median')
    axes[0].axvline(0, color='black', ls='--', lw=0.8)
    axes[0].set_xlabel(r'$\lambda = \ln[\omega/(1-\omega)]$, $\omega$ = OOS rank/(N+1)')
    axes[0].set_title('12,870 CSCV splits', loc='left')
    axes[1].scatter(sr_is * np.sqrt(365), sr_oos * np.sqrt(365), s=3, alpha=0.25, color=MainBlue, label='in-sample winner of one split')
    lim = [min(sr_oos.min(), 0) * np.sqrt(365), sr_is.max() * np.sqrt(365)]
    axes[1].plot(lim, lim, color='black', ls=':', lw=0.8, label='45 degree line')
    axes[1].axhline(0, color='black', lw=0.6)
    axes[1].set_xlabel('SR in sample (annualised)'); axes[1].set_ylabel('SR out of sample')
    axes[1].set_title('Selected winners lose Sharpe out of sample', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_b11_pbo')
    # ---------------- B13 RC / SPA / StepM
    def sb_index(n, q, rng):
        idx = np.empty(n, int); idx[0] = rng.integers(n)
        new = rng.random(n) < q; starts = rng.integers(0, n, n)
        for t in range(1, n):
            idx[t] = starts[t] if new[t] else (idx[t - 1] + 1) % n
        return idx

    def snooping(Dm, B=2000, q=1 / 20, seed=SEED, alpha=0.05):
        rng = np.random.default_rng(seed); n, K = Dm.shape
        dbar = Dm.mean(0)
        boots = np.array([Dm[sb_index(n, q, rng)].mean(0) for _ in range(B)])
        omega = np.sqrt(n) * boots.std(0); tstat = np.sqrt(n) * dbar / omega
        rc_null = np.max(np.sqrt(n) * (boots - dbar), 1)
        p_rc = np.mean(rc_null >= np.max(np.sqrt(n) * dbar))
        mu_c = dbar * (tstat >= -np.sqrt(2 * np.log(np.log(n))))
        spa_null = np.maximum((np.sqrt(n) * (boots - mu_c) / omega).max(1), 0)
        p_spa = np.mean(spa_null >= max(tstat.max(), 0))
        Z = np.sqrt(n) * (boots - dbar) / omega
        active, rej = np.ones(K, bool), np.zeros(K, bool)
        while active.any():
            c = np.quantile(Z[:, active].max(1), 1 - alpha)
            new = active & (tstat > c)
            if not new.any():
                break
            rej |= new; active &= ~new
        return dict(max_t=float(tstat.max()), p_RC=float(p_rc), p_SPA=float(p_spa), StepM=int(rej.sum()),
                    crit_spa=float(np.quantile(spa_null, 0.95))), spa_null
    bh10 = r_b.loc[R.index].values
    res13, nulls = {}, {}
    for lab, Dm in (('cash', R.values), ('buy-and-hold', R.values - bh10[:, None])):
        res13[lab], nulls[lab] = snooping(Dm)
    OUT['B13'] = res13
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 2.7))
    for ax, lab, c in ((axes[0], 'cash', MainBlue), (axes[1], 'buy-and-hold', Amber)):
        ax.hist(nulls[lab], bins=40, color=c, alpha=0.8, label='SPA bootstrap null of the max statistic')
        ax.axvline(res13[lab]['max_t'], color=IDAred, lw=1.3, label='observed largest studentised mean')
        ax.axvline(res13[lab]['crit_spa'], color='black', ls='--', lw=0.8, label='95% quantile')
        ax.set_title(f"Benchmark {lab}: SPA p = {res13[lab]['p_SPA']:.3f}, StepM keeps {res13[lab]['StepM']}", loc='left', fontsize=8.5)
        ax.set_xlabel('max over 120 rules of sqrt(n) mean / omega')
    bottom_legend(fig, ncol=3)
    save_fig('ch13_sem_b13_spa')


# =============================================================================
# B14: selectie dubla
# =============================================================================
def rlasso(y, X, c=1.1, iters=15):
    n, p = X.shape; gam = 0.1 / np.log(n)
    lam = 2 * c * np.sqrt(n) * stats.norm.ppf(1 - gam / (2 * p))
    yc = y - y.mean(); Xc = X - X.mean(0)
    psi = np.sqrt(np.mean((Xc ** 2) * (yc ** 2)[:, None], 0)); sel = np.array([], int)
    for _ in range(iters):
        sel = np.flatnonzero(Lasso(alpha=lam / (2 * n), max_iter=50000).fit(Xc / psi, yc).coef_)
        e = yc - sm.OLS(yc, sm.add_constant(Xc[:, sel])).fit().fittedvalues if len(sel) else yc
        psi_new = np.sqrt(np.mean((Xc ** 2) * (e ** 2)[:, None], 0))
        if np.allclose(psi_new, psi, rtol=1e-4):
            break
        psi = psi_new
    return sel, lam


def b14():
    dfb, FB = frame_b()
    vix = load_close('VIX.INDX', '2000-01-01')
    vix_b = np.log(vix).reindex(btc.index).ffill().reindex(dfb.index)
    d14 = ((vix_b - vix_b.mean()) / vix_b.std()).values
    Zb = (dfb[FB] - dfb[FB].mean()) / dfb[FB].std()
    cols = {c: Zb[c] for c in FB}
    cols.update({c + '^2': Zb[c] ** 2 for c in FB})
    cols.update({a + '*' + b: Zb[a] * Zb[b] for a, b in itertools.combinations(FB, 2)})
    X14 = pd.DataFrame(cols); names = list(X14.columns); X14 = ((X14 - X14.mean()) / X14.std()).values
    y14 = dfb['fwd'].values * 1e4
    sel, lam = rlasso(y14, np.column_stack([d14, X14]))
    Sy, _ = rlasso(y14, X14); Sd, _ = rlasso(d14, X14); U = sorted(set(Sy) | set(Sd))
    ols = lambda Xv: sm.OLS(y14, sm.add_constant(Xv)).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
    r_uni, r_all, r_pds = ols(d14), ols(np.column_stack([d14, X14])), ols(np.column_stack([d14, X14[:, U]]))
    est = {k: dict(theta=float(r.params[1]), se=float(r.bse[1])) for k, r in
           (('OLS, VIX only', r_uni), ('OLS, all 77 controls', r_all), ('post-double selection', r_pds))}
    OUT['B14'] = dict(n=len(y14), p=X14.shape[1], lam=float(lam), single_kept=len(sel), vix_kept=bool(0 in sel),
                      single_names=[(['VIX'] + names)[i] for i in sel], Sy=[names[i] for i in Sy], Sd=[names[i] for i in Sd],
                      est=est, vix_sd=float(vix_b.std()))
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    for i, (k, v) in enumerate(est.items()):
        ax.errorbar(v['theta'], i, xerr=1.96 * v['se'], fmt='o', color=[MainBlue, Amber, Forest][i], capsize=3)
        ax.text(v['theta'] + 1.96 * v['se'] + 3, i, f"{v['theta']:.1f} [{v['theta'] - 1.96 * v['se']:.1f}; {v['theta'] + 1.96 * v['se']:.1f}]",
                va='center', fontsize=7)
    ax.plot([], [], 'x', color=IDAred, label=f'single LASSO: VIX dropped ({len(sel)} regressor kept), no SE')
    ax.axvline(0, color='black', ls='--', lw=0.8, label='no effect')
    ax.set_yticks(range(3), list(est)); ax.invert_yaxis()
    ax.set_xlabel('bp of 5-day BTC log return per SD of log VIX (HAC 95% CI, illustrative)')
    ax.set_title(f"$|\\hat S_y| = {len(Sy)}$, $|\\hat S_d| = {len(Sd)}$: union of {len(U)} controls", loc='left')
    ax.set_xlim(-160, 160)
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_b14_ds')


# =============================================================================
# C2: critica unui raspuns AI
# =============================================================================
def c2():
    r = np.log(btc).diff()
    res = {}

    def run(trend, pipeline, cvname):
        X = pd.DataFrame({'r1': r, 'r5': r.rolling(5).sum(), 'vol20': r.rolling(20).std(), 'trend10': trend})
        data = pd.concat([X, r.shift(-1).rename('fwd')], axis=1).dropna()
        y = (data['fwd'] > 0).astype(int)
        model = LogisticRegression(penalty='l1', C=0.1, solver='liblinear')
        if cvname == 'shuffled':
            cv = KFold(n_splits=5, shuffle=True, random_state=0)
        else:
            cv = TimeSeriesSplit(n_splits=5, gap=20)
        if pipeline:
            est, Xs = make_pipeline(StandardScaler(), model), data[X.columns].values
        else:
            est, Xs = model, StandardScaler().fit_transform(data[X.columns])
        auc = cross_val_score(est, Xs, y, cv=cv, scoring='roc_auc')
        return float(auc.mean()), [float(a) for a in auc], len(data), str(data.index[0].date()), str(data.index[-1].date())
    centred, trailing = r.rolling(10, center=True).mean(), r.rolling(10).mean()
    res['AI answer'] = run(centred, False, 'shuffled')
    res['trailing trend10'] = run(trailing, False, 'shuffled')
    res['+ scaler in pipeline'] = run(trailing, True, 'shuffled')
    res['+ walk-forward split'] = run(trailing, True, 'walk')
    res['centred, walk-forward'] = run(centred, True, 'walk')
    tr = centred.shift(0)
    X = pd.concat([centred.rename('c'), r.shift(-1).rename('fwd')], axis=1).dropna()
    OUT['C2'] = dict(res={k: dict(auc=v[0], folds=v[1], n=v[2], start=v[3], end=v[4]) for k, v in res.items()},
                     corr_centred=float(X['c'].corr(X['fwd'])),
                     corr_trailing=float(pd.concat([trailing.rename('t'), r.shift(-1).rename('fwd')], axis=1).dropna().corr().iloc[0, 1]))
    fig, ax = plt.subplots(figsize=(6.6, 2.7))
    keys = ['AI answer', 'trailing trend10', '+ scaler in pipeline', '+ walk-forward split']
    x = np.arange(len(keys))
    ax.bar(x, [res[k][0] for k in keys], 0.55, color=[IDAred, Amber, Amber, Forest])
    for i, k in enumerate(keys):
        ax.scatter(np.full(5, i) + np.linspace(-0.15, 0.15, 5), res[k][1], color='black', s=10, zorder=3,
                   label='single folds' if i == 0 else None)
        ax.text(i, res[k][0] + 0.015, f'{res[k][0]:.3f}', ha='center', fontsize=7.5)
    ax.axhline(0.5, color='black', ls='--', lw=0.8, label='AUC 0.5')
    ax.set_xticks(x, ['AI code\n(centred, shuffled)', 'fix 1: trailing\nwindow', 'fix 2: scaler\ninside folds',
                      'fix 3: walk-forward\n(corrected pipeline)'], fontsize=7)
    ax.set_ylim(0.4, 0.8); ax.set_ylabel('mean ROC AUC over 5 folds')
    ax.set_title('C2: the AI answer, corrected one error at a time', loc='left')
    bottom_legend(fig, ncol=2)
    save_fig('ch13_sem_c2_fix')


# =============================================================================
def to_json(o):
    if isinstance(o, dict):
        return {str(k): to_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_json(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


TASKS = {'setup': setup, 'a1': a1, 'a2': a2, 'a3': a3_a4, 'a5': a5_a6, 'a7': a7_a8, 'a9': a9_a10, 'b1': b1, 'b2': b2,
         'b3': b3_b4, 'b5': b5, 'b6': b6, 'b7': b7_b8_b12, 'b9': b9, 'b10': b10_b11_b13, 'b14': b14, 'c2': c2}

if __name__ == '__main__':
    path = os.path.join(HERE, 'seminar13_results.json')
    if os.path.exists(path):
        OUT.update(json.load(open(path)))
    todo = sys.argv[1:] or list(TASKS)
    for k in todo:
        print('==', k); TASKS[k]()
        json.dump(to_json(OUT), open(path, 'w'), indent=1)
    print('written', path)

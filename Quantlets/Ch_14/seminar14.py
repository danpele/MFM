"""
seminar14.py -- cifrele si graficele Seminarului 14 (deep learning si modele fundationale)
=========================================================================================
Partea A: numararea parametrilor LSTM, gradientul care dispare, tokenizarea Chronos, VaR/ES din grila de cuantile.
Partea B: R^2 in afara esantionului, QLIKE si MCS, backtesting VaR 1%, variabilitatea semintelor, scurgerea
          de informatie (validare amestecata vs validare in ordinea timpului).
Partea C: poate un model fundational zero-shot inlocui GARCH pentru VaR 1% / ES 2.5% al indicelui BET?
Rezultat: sem14_results.json si graficele ch14_sem_*.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_tsfm as M   # noqa: E402
from generate_all_charts import (plt, mdates, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray,  # noqa: E402
                                 LightGray, save_fig, legend_outside_bottom, load_csv, RISK_COL, RISK_LBL)

HERE = os.path.dirname(os.path.abspath(__file__))
S = {}


# =============================================================================
# PARTEA A
# =============================================================================
def part_a():
    # A1/A2: parametrii LSTM
    S['A1'] = dict(d=1, h=16, lstm=M.lstm_param_count(1, 16), lstm_text=M.lstm_param_count(1, 16, False),
                   head=17, total=M.lstm_param_count(1, 16) + 17)
    S['A2'] = dict(d=5, h=32, l1=M.lstm_param_count(5, 32), l2=M.lstm_param_count(32, 32), head=33,
                   total=M.lstm_param_count(5, 32) + M.lstm_param_count(32, 32) + 33)
    # A3/A4: memoria unei celule LSTM cu poarta de uitare constanta
    sig = lambda b: 1 / (1 + np.exp(-b))
    S['A3'] = dict(w=0.9, w20=0.9 ** 20, w50=0.9 ** 50, f0=sig(0), f3=sig(3), f0_50=sig(0) ** 50, f3_50=sig(3) ** 50,
                   half3=np.log(0.5) / np.log(sig(3)))
    S['A4'] = dict(f1=sig(1), half1=np.log(0.5) / np.log(sig(1)), half99=np.log(0.5) / np.log(0.99),
                   b99=np.log(0.99 / 0.01), f5=sig(5), f5_250=sig(5) ** 250)
    # A5/A6: tokenizarea Chronos (scalare prin media valorilor absolute, 4093 de centre in [-15, 15])
    x = np.array([0.8, -1.2, 0.4, 2.0])
    s = np.mean(np.abs(x))
    delta = 30 / 4092
    z = x / s
    j = np.round((z + 15) / delta).astype(int)
    S['A5'] = dict(x=x.tolist(), s=s, z=z.tolist(), delta=delta, j=j.tolist())
    x6 = np.array([0.8, -1.2, 0.4, -9.0])
    s6 = np.mean(np.abs(x6))
    z6 = x6 / s6
    S['A6'] = dict(x=x6.tolist(), s=s6, z=z6.tolist(), j=np.round((z6 + 15) / delta).astype(int).tolist(),
                   z_small=float(0.4 / s6), z_small0=float(0.4 / s))
    # A7/A8: VaR si ES din grila de cuantile a ultimei prognoze Chronos-2 pentru S&P 500
    d = load_csv('ch14_returns_sp500.csv')
    last = d.iloc[-1]
    q = {u: float(last[f'chronos2_q{u:.2f}']) for u in M.C2_LEVELS}
    q025 = q[0.01] + (0.025 - 0.01) / (0.05 - 0.01) * (q[0.05] - q[0.01])
    es = -(0.01 * q[0.01] + 0.015 * (q[0.01] + q025) / 2) / 0.025
    S['A7'] = dict(date=str(d.index[-1].date()), q01=q[0.01], q05=q[0.05], q10=q[0.1], q50=q[0.5], q025=q025,
                   var1=-q[0.01], var25=-q025, es=es, es_ratio=es / (-q025))
    b = {u: float(last[f'bolt_q{u:.2f}']) for u in M.DEC_LEVELS}
    sd = (b[0.5] - b[0.1]) / stats.norm.ppf(0.9)
    S['A8'] = dict(q10=b[0.1], q50=b[0.5], sd=sd, var1=-(b[0.5] + sd * stats.norm.ppf(0.01)),
                   es25=-(b[0.5] - sd * stats.norm.pdf(stats.norm.ppf(0.025)) / 0.025), clamp=-b[0.1])


# =============================================================================
# PARTEA B
# =============================================================================
def b_returns(asset):
    """R^2 in afara esantionului fata de prognoza zero (interval bootstrap pe blocuri de 20 de zile), testul DM pe
    erorile patratice (varianta Newey-West) si rata semnelor corecte, pentru fiecare model."""
    d = load_csv(f'ch14_returns_{asset}.csv')
    y = d['y'].values
    rows = {}
    for k, lab in (('hist', 'Historical mean'), ('ar1', 'AR(1)'), ('lstm', 'LSTM'), ('chronos2_point', 'Chronos-2'),
                   ('bolt_point', 'Chronos-Bolt'), ('timesfm_point', 'TimesFM-2.5')):
        f = d[k].values
        lo, hi = M.block_bootstrap_ci(lambda yy, ff: M.r2_oos(yy, ff), [y, f], B=1000)
        dm = M.diebold_mariano((y - f) ** 2, y ** 2)
        st = M.sign_test(y, f)
        rows[lab] = {'R2 (%)': 100 * M.r2_oos(y, f), 'CI low': 100 * lo, 'CI high': 100 * hi, 'DM': dm['DM'],
                     'p (DM)': dm['p'], 'correct sign (%)': 100 * st['rate'],
                     'always up (%)': 100 * np.mean(y[y != 0] > 0)}
    return pd.DataFrame(rows).T


def b_rv(post=False):
    """QLIKE medie, testul DM fata de log-HAR si valorile p ale MCS pentru prognozele varianței realizate SPY."""
    d = load_csv('ch14_rv.csv')
    if post:
        d = d[d.index >= M.POST_FROM]
    models = ['RW', 'HAR', 'logHAR', 'GARCH-t', 'LSTM', 'Chronos-2', 'Chronos-Bolt', 'TimesFM-2.5']
    L = pd.DataFrame({m: M.qlike(d['RV'], d[m]) for m in models})
    p = M.mcs(L)
    rows = {}
    for m in models:
        dm = M.diebold_mariano(L[m], L['logHAR']) if m != 'logHAR' else dict(DM=np.nan, p=np.nan)
        rows[m] = {'QLIKE': L[m].mean(), 'DM vs log-HAR': dm['DM'], 'p (DM)': dm['p'], 'MCS p': p[m],
                   'mean forecast / mean RV': d[m].mean() / d['RV'].mean()}
    return pd.DataFrame(rows).T


def b_median():
    """Media din grila de cuantile vs exp(mediana) si efectul lungimii contextului (Chronos-2)."""
    d = load_csv('ch14_rv.csv')
    rows = {}
    for m in ('Chronos-2', 'TimesFM-2.5'):
        for kind, col in (('grid mean', m), ('exp(median)', m + '|median')):
            rows[f'{m}, {kind}'] = {'QLIKE': M.qlike(d['RV'], d[col]).mean(),
                                    'mean forecast / mean RV': d[col].mean() / d['RV'].mean()}
    c = load_csv('ch14_ctx.csv')
    ctx = pd.Series({int(k): M.qlike(c['RV'], c[k]).mean() for k in c.columns[1:]}, name='QLIKE (Chronos-2)')
    return pd.DataFrame(rows).T, ctx


def b_risk(asset, post=False):
    """VaR 1%: depasiri, testele Kupiec si Christoffersen; (VaR 2.5%, ES 2.5%): FZ0, DM fata de FHS, MCS."""
    d = load_csv(f'ch14_risk_{asset}.csv')
    if post:
        d = d[d.index >= M.POST_FROM]
    L = -d['y'].values
    models = ['HS', 'GARCH-t', 'FHS', 'C2-raw', 'C2-FHS', 'TFM-FHS']
    F = pd.DataFrame({m: M.fz0(L, d[f'{m}|VaR2.5'].values, np.maximum(d[f'{m}|ES2.5'].values, 1e-6)) for m in models})
    p = M.mcs(F)
    rows = {}
    for m in models:
        h = (L > d[f'{m}|VaR1'].values).astype(int)
        k, c = M.kupiec(h, 0.01), M.christoffersen(h, 0.01)
        dm = M.diebold_mariano(F[m], F['FHS']) if m != 'FHS' else dict(DM=np.nan)
        rows[m] = {'breaches': k['x'], 'rate (%)': 100 * k['rate'], 'p Kupiec': k['p'], 'p independence': c['p_ind'],
                   'FZ0': F[m].mean(), 'DM vs FHS': dm['DM'], 'MCS p': p[m]}
    return pd.DataFrame(rows).T


def b_var10(asset):
    """VaR 10%: cuantilele directe ale celor trei modele fundationale fata de HS si FHS."""
    d = load_csv(f'ch14_risk_{asset}.csv')
    L = -d['y'].values
    rows = {}
    for m, col in (('HS', 'HS|VaR10'), ('FHS', 'FHS|VaR10'), ('Chronos-2', 'C2-raw|VaR10'),
                   ('Chronos-Bolt', 'bolt-raw|VaR10'), ('TimesFM-2.5', 'timesfm-raw|VaR10')):
        h = (L > d[col].values).astype(int)
        k = M.kupiec(h, 0.10)
        rows[m] = {'rate (%)': 100 * k['rate'], 'p Kupiec': k['p'],
                   'pinball': np.mean(M.pinball(-L, -d[col].values, 0.10))}
    return pd.DataFrame(rows).T


def b_seeds():
    """R^2 in afara esantionului pentru fiecare dintre cele 5 seminte LSTM si pentru media lor."""
    rows = {}
    for a in M.ASSETS:
        d = load_csv(f'ch14_returns_{a}.csv')
        y = d['y'].values
        r = {f'seed {s}': 100 * M.r2_oos(y, d[f'lstm_s{s}'].values) for s in range(5)}
        r['average of 5 seeds'] = 100 * M.r2_oos(y, d['lstm'].values)
        rows[M.LABELS[a]] = r
    return pd.DataFrame(rows).T


def b8_leakage():
    """Scurgerea de informatie prin privirea in viitor: log-HAR cu mediile pe 5 si 22 de zile care includ si ziua
    prognozata (gresit) fata de log-HAR corect (medii pana la ziua precedenta). SPY, aceleasi zile de test."""
    d = load_csv('ch14_rv.csv')
    rv = M.load_rv()
    y = np.log(rv.values)
    s = pd.Series(y)
    X_leak = np.column_stack([np.ones(len(s)), s.shift(1), s.rolling(5).mean(), s.rolling(22).mean()])
    org = rv.index.get_indexer(d.index)
    f = []
    for t in org:
        idx = np.arange(max(22, t - 500), t)
        b, *_ = np.linalg.lstsq(X_leak[idx], y[idx], rcond=None)
        s2 = np.var(y[idx] - X_leak[idx] @ b, ddof=4)
        f.append(np.exp(X_leak[t] @ b + s2 / 2))
    f = np.array(f)
    L_ok = M.qlike(d['RV'], d['logHAR'])
    L_leak = M.qlike(d['RV'], f)
    L_c2 = M.qlike(d['RV'], d['Chronos-2'])
    dm = M.diebold_mariano(L_leak, L_ok)
    res = dict(qlike_ok=float(L_ok.mean()), qlike_leak=float(L_leak.mean()), qlike_c2=float(L_c2.mean()),
               dm=dm['DM'], p=dm['p'], gain=float(1 - L_leak.mean() / L_ok.mean()), n=int(len(d)))
    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    lab = ['log-HAR, correct\n(averages up to $t-1$)', 'log-HAR with look-ahead\n(averages include day $t$)',
           'Chronos-2\n(zero-shot)']
    v = [res['qlike_ok'], res['qlike_leak'], res['qlike_c2']]
    ax.barh(range(3), v, color=[Purple, IDAred, Orange])
    for i in range(3):
        ax.text(v[i] + 0.003, i, f'{v[i]:.3f}', va='center', fontsize=8, color='black')
    ax.set_yticks(range(3), lab, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Mean QLIKE loss (lower is better)')
    ax.set_xlim(0, max(v) * 1.2)
    save_fig('ch14_sem_leakage')
    return res


def part_b():
    S['B1'] = b_returns('sp500').to_dict('index')
    S['B2'] = {a: b_returns(a).to_dict('index') for a in ('btc', 'bet')}
    S['B3'] = b_rv().to_dict('index')
    S['B3_post'] = b_rv(post=True).to_dict('index')
    med, ctx = b_median()
    S['B4'] = dict(median=med.to_dict('index'), ctx={str(k): v for k, v in ctx.items()})
    S['B5'] = b_risk('sp500').to_dict('index')
    S['B5_post'] = b_risk('sp500', post=True).to_dict('index')
    S['B6'] = b_risk('btc').to_dict('index')
    S['B6_v10'] = {a: b_var10(a).to_dict('index') for a in M.ASSETS}
    S['B7'] = b_seeds().to_dict('index')
    S['B8'] = b8_leakage()


# =============================================================================
# PARTEA C: BET
# =============================================================================
def part_c():
    S['C'] = b_risk('bet').to_dict('index')
    S['C_post'] = b_risk('bet', post=True).to_dict('index')
    S['C_ret'] = b_returns('bet').to_dict('index')
    d = load_csv('ch14_risk_bet.csv')
    L = -d['y']
    # zonele semaforului Basel pe ferestre de 250 de zile (fara suprapunere)
    tl = {}
    for m in ('HS', 'GARCH-t', 'FHS', 'C2-raw', 'C2-FHS', 'TFM-FHS'):
        h = (L > d[f'{m}|VaR1']).astype(int).values
        zones = []
        for i in range(0, len(h) - 249, 250):
            x = h[i:i + 250].sum()
            zones.append('green' if x <= 4 else ('yellow' if x <= 9 else 'red'))
        tl[m] = dict(green=zones.count('green'), yellow=zones.count('yellow'), red=zones.count('red'), n=len(zones))
    S['C_tl'] = tl
    s = d.loc['2022-01-01':'2022-12-31']
    Ls = -s['y']
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.bar(s.index, Ls.clip(lower=0), width=1.0, color=Teal, alpha=0.7, label='BET daily loss (gains set to 0)')
    for m in ('FHS', 'C2-raw', 'C2-FHS'):
        ax.plot(s.index, s[f'{m}|VaR1'], color=RISK_COL[m], lw=1.0, label=f'VaR 1%: {RISK_LBL[m]}')
    ax.set_ylabel('Loss (%)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch14_sem_bet')
    S['C_2022'] = {m: int(np.sum(Ls > s[f'{m}|VaR1'])) for m in ('HS', 'GARCH-t', 'FHS', 'C2-raw', 'C2-FHS', 'TFM-FHS')}
    S['C_2022']['T'] = int(len(s))


if __name__ == '__main__':
    part_a()
    part_b()
    part_c()
    with open(os.path.join(HERE, 'sem14_results.json'), 'w') as f:
        json.dump(S, f, indent=1, default=float)
    print('wrote sem14_results.json')

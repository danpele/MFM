"""
ai_discovery_case.py -- Capitolul 19, mini-caz „AI pentru descoperire stiintifica” (replicare, apoi extindere)
==========================================================================================================
Pornim de la rezultatele deja calculate in capitolele anterioare:
  * Capitolul 8 (Quantlets/Ch_08/ch8_results.json, cheia var99): VaR 1% pentru 4 active x 6 modele,
    cu testele Kupiec (acoperire neconditionata) si Christoffersen (acoperire conditionata);
  * Capitolul 19 (ch19_results.json): acelasi model FHS pe BET, dar pe alt esantion de evaluare.
Pasul 1 (replicare): FHS pe BET in cele doua capitole -- aceeasi metoda, ferestre diferite.
Pasul 2 (extindere): 24 de teste de acoperire conditionata (4 active x 6 modele) tratate ca o familie:
  respingeri la 5% fara corectie, cu corectia Holm (FWER) si cu Benjamini-Hochberg (FDR 5%).
Iesire: ai_discovery_case.json
"""

import os
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CH8 = os.path.join(HERE, '..', 'Ch_08', 'ch8_results.json')
ALPHA = 0.05


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run, m = 0.0, len(p)
    for i, j in enumerate(order):
        run = max(run, (m - i) * p[j])
        adj[j] = min(1.0, run)
    return adj


def bh(p):
    p = np.asarray(p, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 1.0
    for i in range(m - 1, -1, -1):
        j = order[i]
        run = min(run, p[j] * m / (i + 1))
        adj[j] = run
    return adj


def main():
    v8 = json.load(open(CH8))['var99']
    c19 = json.load(open(os.path.join(HERE, 'ch19_results.json')))
    keys = list(v8.keys())
    pcc = np.array([v8[k]['p_cc'] for k in keys])
    h, b = holm(pcc), bh(pcc)
    models = sorted({k.split('|')[1] for k in keys})
    survive = {m: all(h[i] >= ALPHA for i, k in enumerate(keys) if k.endswith('|' + m)) for m in models}
    survive_raw = {m: all(pcc[i] >= ALPHA for i, k in enumerate(keys) if k.endswith('|' + m)) for m in models}
    res = dict(
        rep8=dict(T=v8['bet|FHS']['T'], x=v8['bet|FHS']['x'], rate=100 * v8['bet|FHS']['rate'],
                  p_uc=v8['bet|FHS']['p_uc'], p_cc=v8['bet|FHS']['p_cc']),
        rep19=dict(T=c19['backtest']['FHS']['T'], x=c19['backtest']['FHS']['x'],
                   rate=100 * c19['backtest']['FHS']['rate'], p_uc=c19['backtest']['FHS']['p_uc'],
                   p_cc=c19['backtest']['FHS']['p_cc'], start=c19['eval']['start']),
        n_tests=len(keys), rej_raw=int((pcc < ALPHA).sum()), rej_holm=int((h < ALPHA).sum()),
        rej_bh=int((b < ALPHA).sum()),
        pass_all_raw=[m for m in models if survive_raw[m]], pass_all_holm=[m for m in models if survive[m]],
        table={k: dict(p_cc=float(pcc[i]), holm=float(h[i]), bh=float(b[i])) for i, k in enumerate(keys)})
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(res, f, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != 'table'}, indent=2))


if __name__ == '__main__':
    main()

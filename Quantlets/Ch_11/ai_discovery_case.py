"""
ai_discovery_case.py -- Capitolul 11, secțiunea „AI pentru descoperire științifică”: mini-caz
=============================================================================================
Întrebare: ce parte din varianța S&P 500 provine din salturi? Salturile Merton estimate pe randamente zilnice
sunt salturi reale sau volatilitate stochastică deghizată?

  * Pasul 0 (replicare): estimarea Merton prin verosimilitate maximă pe randamentele zilnice S&P 500 și
    ponderea salturilor în varianță, lam (mu_j^2 + s_j^2) / (sigma^2 + lam (mu_j^2 + s_j^2)) (cifra din curs)
  * Implicație testabilă: dacă „salturile” sunt volatilitate variabilă în timp, ele dispar după standardizarea
    randamentelor cu o volatilitate cunoscută ex ante; salturile reale rămân
  * Standardizare: EWMA (RiskMetrics), sigma^2_t = 0.94 sigma^2_{t-1} + 0.06 r^2_{t-1} (Capitolul 5),
    apoi scalare la abaterea standard a eșantionului; aceeași estimare Merton pe seria standardizată
  * Test: raportul de verosimilitate Merton vs distribuția Normală (GBM) pe ambele serii
Iesire: ai_discovery_case.json
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import log_returns            # noqa: E402
from ct_models import merton_mle            # noqa: E402

DT = 1 / 252
LAM = 0.94
BURN = 250


def ewma_var(x, lam=LAM, burn=BURN):
    s = np.empty(len(x))
    s[0] = np.var(x[:burn])
    for t in range(1, len(x)):
        s[t] = lam * s[t - 1] + (1 - lam) * x[t - 1] ** 2
    return s


def summary(x):
    mf = merton_mle(x, DT)
    jv = mf['lam'] * (mf['mu_j'] ** 2 + mf['s_j'] ** 2)
    ll0 = float(stats.norm.logpdf(x, x.mean(), x.std()).sum())
    return dict(lam=float(mf['lam']), lam_se=float(mf['se']['lam']), s_j=float(mf['s_j']), sigma=float(mf['sigma']),
                jump_share=float(jv / (mf['sigma'] ** 2 + jv)), lr=float(2 * (mf['loglik'] - ll0)),
                exkurt=float(stats.kurtosis(x)), n=int(len(x)))


def main():
    R = json.load(open(os.path.join(HERE, 'ch11_results.json')))
    r = log_returns('sp500').values
    raw = summary(r)
    raw['course_jump_share'] = R['merton']['sp500']['jump_share']
    s2 = ewma_var(r)
    z = (r / np.sqrt(s2))[BURN:]
    z = z * r[BURN:].std() / z.std()
    std = summary(z)
    out = dict(raw=raw, ewma=std, start=str(log_returns('sp500').index[0].date()))
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()

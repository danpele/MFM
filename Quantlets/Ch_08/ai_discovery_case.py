"""
ai_discovery_case.py -- Capitolul 8, secțiunea „AI pentru descoperire științifică”: mini-caz
============================================================================================
Întrebare: restabilește VaR conformal calculat pe scoruri standardizate cu volatilitatea GARCH-t
acoperirea condiționată în perioadele de criză, acolo unde conformal split (scoruri standardizate
cu abaterea standard pe 250 de zile) eșuează?

Două experimente, fiecare cu calendarul și familia Holm proprii:
  * Experimentul 1 (conformal split, patru piețe): calendarul complet al secțiunii conformale (aceleași zile ca
    prognozele capitolului); nu depinde de prognozele GARCH.
  * Experimentul 2 (scala GARCH față de conformal split, doar piețele cu prognoze GARCH-t complete pe calendarul
    canonic: S&P 500 și BET): calendarul comun al zilelor cu VaR conformal GARCH (după 250 de zile de scoruri).
    Scor conformal GARCH: s_t = (L_t + mu_t) / sigma_t, cu mu_t, sigma_t prognozele GARCH-t din t-1;
    VaR_t = -mu_t + sigma_t * s_(k), k = ceil((n+1)(1-alpha)), ultimele n = 250 de scoruri.
Test: momentul E[C_t (I_t - alpha)] = 0 (C_t: indicatorul de criză cunoscut ex ante, I_t: depășirea), statistică t cu
varianță HAC Newey--West (nucleu Bartlett), p bilateral asimptotic; corecția Holm în interiorul fiecărei familii.
Rata de depășire din criză se raportează descriptiv; nu se folosește aproximarea Binomială (depășirile din criză nu sînt
independente, iar zilele de criză sînt selectate dinamic).
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
import mfm_data as M   # noqa: E402

N_CAL = 250
COL = {0.05: 'VaR5', 0.01: 'VaR1'}


def canonical_calendar(r):
    """Evaluation days of the chapter (same rule as the forecasts): from EVAL_FROM, after W observations."""
    r = r.dropna()
    start = max(M.W, int(np.searchsorted(r.index, pd.Timestamp(M.EVAL_FROM))))
    return r.index[start:]


def garch_eligible(g, cal, a):
    """GARCH-t forecasts complete (finite mean, scale and VaR) on every day of the canonical calendar."""
    if not g.index.equals(cal):
        return False
    x = g[['mu', 'scale', COL[a]]].to_numpy(dtype=float)
    return bool(np.isfinite(x).all())


def conformal_garch(g, a, n_cal=N_CAL):
    """VaR conformal split pe scorurile GARCH-t standardizate (doar informație pînă la t-1)."""
    s = ((g['L'] + g['mu']) / g['scale']).values
    k = int(np.ceil((n_cal + 1) * (1 - a)))
    v = np.full(len(g), np.nan)
    for t in range(n_cal, len(g)):
        cal = np.sort(s[t - n_cal:t])
        v[t] = np.inf if k > n_cal else -g['mu'].values[t] + g['scale'].values[t] * cal[k - 1]
    return pd.Series(v, index=g.index)


def crisis_moment_test(hit, crisis, a):
    """t test of E[C_t (I_t - a)] = 0 with a Newey--West long-run variance; two-sided asymptotic p."""
    m = crisis.astype(float).values * (hit.astype(float).values - a)
    T = len(m)
    lrv = M.nw_var(m)
    t = m.mean() / np.sqrt(lrv / T)
    return dict(t_hac=float(t), p_hac=float(2 * stats.norm.sf(abs(t))))


def rates(hit, crisis, a):
    nc = int(crisis.sum())
    d = dict(T=int(len(hit)), n_crisis=nc, x_crisis=int(hit[crisis].sum()),
             all=float(hit.mean()), calm=float(hit[~crisis].mean()), crisis=float(hit[crisis].mean()))
    d.update(crisis_moment_test(hit, crisis, a))
    return d


def holm(p):
    """Valori p ajustate Holm (control FWER), pe familia dată."""
    keys = sorted(p, key=p.get)
    m, out, run = len(keys), {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (m - i) * p[k]))
        out[k] = run
    return out


def main():
    out = dict(protocol=dict(
        test='t test of E[C_t(I_t - alpha)] = 0, Newey-West (Bartlett) long-run variance, two-sided asymptotic p',
        holm='within each experiment: split conformal across all four markets; GARCH scale across the eligible markets',
        eligibility='GARCH-t mean, scale and VaR finite on every day of the canonical calendar',
        n_cal=N_CAL))
    for a, tag in ((0.05, 'a5'), (0.01, 'a1')):
        split, garch = {}, {}
        for n in M.ASSETS:
            r = M.load_returns(n)
            cal = canonical_calendar(r)
            c = M.conformal_var(r, a=a).reindex(cal)
            assert np.isfinite(c['L']).all() and not c['VaR_split'].isna().any()
            reg = M.regimes(r, cal)
            split[n] = rates(c['L'] > c['VaR_split'], reg, a)
            g = M.get_forecasts(n)[0]['GARCH-t']
            if not garch_eligible(g, cal, a):
                garch[n] = dict(status='withheld', reason='incomplete GARCH-t forecasts on the canonical calendar')
                continue
            vg = conformal_garch(g, a).dropna()
            idx = vg.index
            regc = M.regimes(r, idx)
            L = c.loc[idx, 'L']
            garch[n] = dict(status='computed',
                            cgarch=rates(L > vg, regc, a),
                            split_common=rates(L > c.loc[idx, 'VaR_split'], regc, a),
                            garch_t=rates(L > g.loc[idx, COL[a]], regc, a))
        ps = holm({n: split[n]['p_hac'] for n in split})
        for n in split:
            split[n]['p_hac_holm'] = ps[n]
        elig = [n for n in garch if garch[n]['status'] == 'computed']
        pg = holm({n: garch[n]['cgarch']['p_hac'] for n in elig})
        for n in elig:
            garch[n]['cgarch']['p_hac_holm'] = pg[n]
        out[tag] = dict(split=split, garch=garch, garch_family=elig)
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()

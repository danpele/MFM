"""
ai_discovery_case.py -- Capitolul 8, secțiunea „AI pentru descoperire științifică”: mini-caz
============================================================================================
Întrebare: restabilește VaR conformal calculat pe scoruri standardizate cu volatilitatea GARCH-t
acoperirea condiționată în perioadele de criză, acolo unde conformal split (scoruri standardizate
cu abaterea standard pe 250 de zile) eșuează?

  * Pasul 0 (replicare): rata de depășire a VaR 5% conformal split în zilele de criză (cifra din curs)
  * Scor conformal GARCH: s_t = (L_t + mu_t) / sigma_t, cu mu_t, sigma_t prognozele GARCH-t din t-1
    VaR_t = -mu_t + sigma_t * s_(k), k = ceil((n+1)(1-alpha)), ultimele n = 250 de scoruri
  * Evaluare pe aceleași zile: rate de depășire (toate / calm / criză), test Binomial exact bilateral
    pentru rata din criză, corecție Holm pe cele patru piețe
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


def conformal_garch(g, a, n_cal=N_CAL):
    """VaR conformal split pe scorurile GARCH-t standardizate (doar informație până la t-1)."""
    s = ((g['L'] + g['mu']) / g['scale']).values
    k = int(np.ceil((n_cal + 1) * (1 - a)))
    v = np.full(len(g), np.nan)
    for t in range(n_cal, len(g)):
        cal = np.sort(s[t - n_cal:t])
        v[t] = -g['mu'].values[t] + g['scale'].values[t] * cal[min(k, n_cal) - 1]
    return pd.Series(v, index=g.index)


def binom_p(x, n, a):
    return float(stats.binomtest(int(x), int(n), a).pvalue)


def holm(p):
    """Valori p ajustate Holm (control FWER)."""
    keys = sorted(p, key=p.get)
    m, out, run = len(keys), {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (m - i) * p[k]))
        out[k] = run
    return out


def main():
    R = json.load(open(os.path.join(HERE, 'ch8_results.json')))
    out = {}
    for a, tag in ((0.05, 'a5'), (0.01, 'a1')):
        res, pc = {}, {}
        for n in M.ASSETS:
            r = M.load_returns(n)
            fc = M.get_forecasts(n)[0]
            c = M.conformal_var(r, a=a).loc[fc['HS'].index[0]:]
            # pasul 0: replicarea cifrei din curs (conformal split, zile de criză)
            reg_full = M.regimes(r, c.index)
            rep = float((c['L'] > c['VaR_split'])[reg_full].mean())
            g = fc['GARCH-t']
            vg = conformal_garch(g, a).dropna()
            idx = vg.index.intersection(c.index)
            reg = M.regimes(r, idx)
            L = c.loc[idx, 'L']
            h_split = L > c.loc[idx, 'VaR_split']
            h_cg = L > vg.loc[idx]
            h_gt = L > g.loc[idx, {0.05: 'VaR5', 0.01: 'VaR1'}[a]]
            nc = int(reg.sum())
            d = dict(T=int(len(idx)), n_crisis=nc, replicated_split_crisis=rep,
                     course_split_crisis=R['conformal5' if a == 0.05 else 'conformal'][n]['split'][2])
            for lab, h in (('split', h_split), ('cgarch', h_cg), ('garch_t', h_gt)):
                d[lab] = dict(all=float(h.mean()), calm=float(h[~reg].mean()), crisis=float(h[reg].mean()),
                              x_crisis=int(h[reg].sum()), p_crisis=binom_p(h[reg].sum(), nc, a),
                              p_all=binom_p(h.sum(), len(h), a))
            res[n] = d
            pc[n] = d['cgarch']['p_crisis']
        ph = holm(pc)
        ps = holm({n: res[n]['split']['p_crisis'] for n in M.ASSETS})
        for n in M.ASSETS:
            res[n]['cgarch']['p_crisis_holm'] = ph[n]
            res[n]['split']['p_crisis_holm'] = ps[n]
        out[tag] = res
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()

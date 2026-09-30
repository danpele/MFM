"""
ai_discovery_case.py -- Capitolul 18, mini-caz „AI pentru descoperire stiintifica”
==================================================================================
Ipoteza testata: indicele total de conectivitate (TCI, Diebold-Yilmaz, ferestre de 250 de zile) anunta
stresul viitor al bancilor dincolo de nivelul curent al volatilitatii.
  y_t   = log din volatilitatea medie (Parkinson) a celor 13 banci in urmatoarele 63 de zile comune
  TCI_t = indicele total de conectivitate la data t (ch18_spill_rolling.csv, doar informatie pana la t)
  RV_t  = log din volatilitatea medie a bancilor in ultimele 20 de zile (control)
  H0: beta_TCI = 0 in y_t = a + beta_TCI * TCI_t (+ gamma * RV_t) + e_t
  * observatii saptamanale cu orizonturi suprapuse: erori standard Newey-West cu 13 decalaje
  * a doua variabila-tinta: cea mai mare scadere cumulata a portofoliului cu ponderi egale in urmatoarele 63 de zile
Iesire: ai_discovery_case.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mfm_data import ALL, bank_range_vol, joint_returns  # noqa: E402

H, SHORT, LAGS = 63, 20, 13


def ols(y, X, names):
    m = sm.OLS(y, sm.add_constant(X)).fit(cov_type='HAC', cov_kwds={'maxlags': LAGS})
    return {n: dict(b=float(m.params[n]), t=float(m.tvalues[n])) for n in names} | dict(r2=float(m.rsquared), n=int(m.nobs))


def main():
    tci = pd.read_csv(os.path.join(HERE, 'ch18_spill_rolling.csv'), index_col=0, parse_dates=True).iloc[:, 0]
    vol = bank_range_vol(ALL).mean(axis=1)
    ret = joint_returns(ALL).mean(axis=1) / 100
    rows = []
    for d, v in tci.items():
        i = vol.index.searchsorted(d, side='right')          # first day after t
        if i + H > len(vol):
            break
        fut = vol.iloc[i:i + H]
        past = vol.iloc[i - SHORT:i]
        j = ret.index.searchsorted(d, side='right')
        cum = np.exp(ret.iloc[j:j + H].cumsum())
        rows.append(dict(date=d, tci=v, y=np.log(fut.mean()), rv=np.log(past.mean()),
                         mdd=float((cum / np.maximum.accumulate(np.r_[1.0, cum.values])[1:] - 1).min())))
    df = pd.DataFrame(rows).set_index('date')
    z = (df - df.mean()) / df.std()
    res = dict(
        n=len(df), start=str(df.index[0].date()), end=str(df.index[-1].date()), horizon=H, lags=LAGS,
        corr_tci_rv=float(df.tci.corr(df.rv)),
        vol_tci=ols(z.y, z[['tci']], ['tci']),
        vol_both=ols(z.y, z[['tci', 'rv']], ['tci', 'rv']),
        vol_rv=ols(z.y, z[['rv']], ['rv']),
        mdd_tci=ols(z.mdd, z[['tci']], ['tci']),
        mdd_both=ols(z.mdd, z[['tci', 'rv']], ['tci', 'rv']),
    )
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()

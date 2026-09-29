"""
case_study17.py -- graficele studiului de caz din Capitolul 17 (MFM)
===================================================================
DeFusco, Nathanson & Zwick (2022), "Speculative dynamics of prices and volume", Journal of Financial Economics
146(1), 205-229, replicat la nivel national cu seriile publice FRED:
  CSUSHPINSA -- S&P CoreLogic Case-Shiller U.S. National Home Price Index (lunar, neajustat sezonier)
  HSN1FNSA   -- New One Family Houses Sold, United States (mii, lunar, neajustat sezonier)
  1. fig_dnz_cycle()   -- analogul Figurii 1, Panelul A: preturi si volum (ajustat pe luna calendaristica),
                          2000 = 100, cu acalmia (de la varful volumului la ultimul varf al preturilor).
  2. fig_dnz_leadlag() -- analogul Figurii 2: corelatia implicita dintre logaritmul centrat al pretului si volumul
                          centrat pe luna calendaristica, intarziat cu k = -12, ..., 48 luni (ec. 1, fara termen
                          liber, centrare pe intregul esantion), 2000-2011 si
                          1990-2011, cu interval bootstrap circular pe blocuri de 24 de luni (95%).
Rezultate: case17.json; grafice: ch17_dnz_cycle, ch17_dnz_leadlag.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import io
import os
import sys
import json
import urllib.request
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Teal, Gray, save_fig,  # noqa: E402
                                 legend_outside_bottom, jsonable, HERE)

LAGS = np.arange(-12, 49)      # k = -12, ..., 48 luni (Figura 2)
BLOCK = 24                     # lungimea blocului pentru bootstrap-ul circular (luni)
B_BOOT = 2000                  # replici bootstrap
BOOT_SEED = 17

_FRED = {}


def fred(series):
    """Serie lunara FRED (fara cheie), ca pd.Series float."""
    if series not in _FRED:
        url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}'
        for attempt in range(4):
            try:
                raw = urllib.request.urlopen(url, timeout=120).read().decode()
                break
            except OSError:
                if attempt == 3:
                    raise
        df = pd.read_csv(io.StringIO(raw), index_col=0, parse_dates=True, na_values='.')
        _FRED[series] = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().rename(series)
    return _FRED[series]


def dnz_series(start='2000', end='2011'):
    """p: logaritmul pretului minus media pe esantion; v: vanzarile minus media lunii lor calendaristice (ec. 1)."""
    price, sales = fred('CSUSHPINSA').loc[start:end], fred('HSN1FNSA').loc[start:end]
    p = np.log(price)
    p = p - p.mean()
    v = sales - sales.groupby(sales.index.month).transform('mean')
    return p, v


def eq1_corr(d):
    """Ec. (1) fara termen liber: beta_k = sum(p v) / sum(v^2); corelatia implicita beta_k sd(v_{t-k}) / sd(p_t)."""
    p, v = d[:, 0], d[:, 1]
    return float((p @ v) / (v @ v) * v.std(ddof=1) / p.std(ddof=1))


def implied_corr(p, v, k):
    """Corelatia implicita pentru decalajul k; p si v raman centrate pe intregul esantion (ec. 1 din articol)."""
    d = pd.concat([p, v.shift(k)], axis=1).dropna().values
    return eq1_corr(d), d


def cbb_corr(d, B=B_BOOT, L=BLOCK, seed=BOOT_SEED):
    """Interval bootstrap circular pe blocuri (95%) pentru corelatia implicita din ec. (1)."""
    rng = np.random.default_rng(seed)
    n = len(d)
    out = np.empty(B)
    for b in range(B):
        idx = np.concatenate([np.arange(s, s + L) % n for s in rng.integers(0, n, int(np.ceil(n / L)))])[:n]
        out[b] = eq1_corr(d[idx])
    return np.percentile(out, [2.5, 97.5])


def fig_dnz_cycle(start='2000', end='2011'):
    """Figura 1, Panelul A, la nivel national: preturi si vanzari de case noi (ajustate pe luna calendaristica), 2000 = 100."""
    price, sales = fred('CSUSHPINSA').loc[start:end], fred('HSN1FNSA').loc[start:end]
    sales_sa = sales - sales.groupby(sales.index.month).transform('mean') + sales.mean()
    pi = 100 * price / price.loc[start].mean()
    vi = 100 * sales_sa / sales_sa.loc[start].mean()
    v_peak, p_peak = vi.idxmax(), pi.idxmax()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.axvspan(v_peak, p_peak, color=Amber, alpha=0.25, lw=0,
               label=f'Quiet: peak of volume ({v_peak:%b %Y}) to peak of prices ({p_peak:%b %Y})')
    ax.axhline(100, color=Gray, lw=0.6, ls=':')
    ax.plot(pi.index, pi, color=MainBlue, lw=1.8, label='Case-Shiller U.S. National Home Price Index')
    ax.plot(vi.index, vi, color=IDAred, lw=1.3, label='New one-family houses sold, calendar-month adjusted')
    ax.set_ylabel('Index, 2000 average = 100')
    ax.set_title(f'U.S. housing cycle, monthly {start}-{end}: prices and volume', color='black')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    save_fig('ch17_dnz_cycle')
    return {'vol_peak': f'{v_peak:%Y-%m}', 'price_peak': f'{p_peak:%Y-%m}',
            'quiet_months': (p_peak.year - v_peak.year) * 12 + p_peak.month - v_peak.month,
            'vol_peak_idx': float(vi.max()), 'price_peak_idx': float(pi.max()),
            'raw_vol_peak': f'{sales.idxmax():%Y-%m}',
            'vol_2011_idx': float(vi.loc['2011'].mean()), 'price_2011_idx': float(pi.loc['2011'].mean()),
            'vol_at_price_peak_idx': float(vi.loc[p_peak])}


def leadlag(start, end, boot=True):
    p, v = dnz_series(start, end)
    rows = []
    for k in LAGS:
        r, d = implied_corr(p, v, int(k))
        lo, hi = cbb_corr(d) if boot else (np.nan, np.nan)
        rows.append((int(k), r, lo, hi))
    return pd.DataFrame(rows, columns=['k', 'corr', 'lo', 'hi']).set_index('k')


def fig_dnz_leadlag():
    """Figura 2 la nivel national: corelatia implicita pe decalaje, 2000-2011 (cu CI 95%) si 1990-2011."""
    a = leadlag('2000', '2011')
    b = leadlag('1990', '2011', boot=False)
    ka, kb = int(a['corr'].idxmax()), int(b['corr'].idxmax())
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.fill_between(a.index, a['lo'], a['hi'], color=Teal, alpha=0.22, lw=0,
                    label='Pointwise 95% circular block bootstrap interval (24-month blocks), 2000-2011')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.axvline(0, color=Gray, lw=0.6, ls=':')
    ax.axvline(24, color=Forest, lw=1.2, ls='--', label='Peak lag in DeFusco et al. (2022), Fig. 2: k = 24')
    ax.plot(a.index, a['corr'], color=MainBlue, lw=1.8, label='National, 2000-2011')
    ax.plot(b.index, b['corr'], color=IDAred, lw=1.3, ls='-.', label='National, 1990-2011')
    ax.plot([ka], [a['corr'].max()], 'o', color=MainBlue, ms=5)
    ax.annotate(f'max at k = {ka}: {a["corr"].max():.2f}', (ka, a['corr'].max()), xytext=(ka + 4, a['corr'].max() + 0.45),
                color='black', fontsize=8, arrowprops=dict(arrowstyle='->', color='black', lw=0.6))
    ax.set_xlim(-12, 48)
    ax.axhline(1, color=Gray, lw=0.6, ls=':')
    ax.set_ylim(-1, 1.4)
    ax.set_xticks(np.arange(-12, 49, 6))
    ax.set_xlabel('Lag k of volume (months; k > 0: volume precedes prices)')
    ax.set_ylabel('Implied correlation')
    ax.set_title('Correlation of log house prices with lagged new-home sales, Eq. (1)', color='black')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch17_dnz_leadlag')
    return {'peak_k': ka, 'peak_corr': float(a['corr'].max()), 'peak_lo': float(a.loc[ka, 'lo']),
            'peak_hi': float(a.loc[ka, 'hi']), 'corr24': float(a.loc[24, 'corr']), 'lo24': float(a.loc[24, 'lo']),
            'hi24': float(a.loc[24, 'hi']), 'corr0': float(a.loc[0, 'corr']), 'corr_m12': float(a.loc[-12, 'corr']),
            'n_pos_ci': int((a['lo'] > 0).sum()), 'ks_pos_ci': [int(k) for k in a.index[a['lo'] > 0]],
            'peak_k_1990': kb, 'peak_corr_1990': float(b['corr'].max()), 'corr24_1990': float(b.loc[24, 'corr'])}


def main():
    out = {'cycle': fig_dnz_cycle(), 'leadlag': fig_dnz_leadlag()}
    with open(os.path.join(HERE, 'case17.json'), 'w') as f:
        json.dump(jsonable(out), f, indent=1)
    print(json.dumps(jsonable(out), indent=1))


if __name__ == '__main__':
    main()

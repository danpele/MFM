"""
case_study17_crises.py -- al doilea studiu de caz din Capitolul 17 (MFM)
=======================================================================
Greenwood, Hanson, Shleifer & Sorensen (2022), "Predictable Financial Crises", Journal of Finance 77(2), 863-921,
https://doi.org/10.1111/jofi.13105, replicat in logica sa pe baza de date publica Jorda-Schularick-Taylor
Macrohistory Database (JST, versiunea R6, 18 economii avansate, 1870-2020; citita online, fara cheie):
  tbus, thh   -- creditul bancar catre firmele nefinanciare / catre gospodarii (moneda nationala)
  gdp, cpi    -- PIB nominal, indicele preturilor de consum
  eq_capgain  -- castigul de capital anual al indicelui bursier (randamentul de pret)
  hpnom       -- indicele nominal al preturilor locuintelor
  crisisJST   -- 1 in anul in care incepe o criza financiara sistemica (cronologia JST)
Definitiile din articol (ec. 2a-2c):
  Delta_3(D/Y)  = variatia pe 3 ani a creditului raportat la PIB (puncte procentuale);
  Delta_3 log P = variatia pe 3 ani a logaritmului pretului real (actiuni pentru firme, locuinte pentru gospodarii);
  High-Debt-Growth  = Delta_3(D/Y) peste percentila 80 a panelului;  High-Price-Growth = peste percentila 66,7;
  R-zone = High-Debt-Growth x High-Price-Growth;  Crisis_{t+1..t+h} = 1 daca o criza incepe in t+1, ..., t+h.
Esantionul: anii de prognoza t = 1950-2016 (deci h = 1, ..., 4 au aceleasi observatii; datele se opresc in 2020).
Interval de 95%: bootstrap pe blocuri de ani calendaristici (5 ani; toate tarile dintr-un an raman impreuna),
pentru dependenta dintre tari in acelasi an si pentru orizonturile suprapuse; pragurile (percentilele) se reestimeaza
in fiecare replica; sensibilitate la blocuri de 3 si 8 ani. Intervalele sint punctuale, nu simultane.
Pragul pretului este in puncte logaritmice (100 x Delta_3 log P). Articolul opreste originile prognozelor in 2012;
aici originile merg pina in 2016 (datele JST R6 se opresc in 2020).
Rezultate: case17_crises.json; grafic: ch17_ghss_rzone.
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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from generate_all_charts import (plt, MainBlue, IDAred, Forest, save_fig,  # noqa: E402
                                 jsonable, HERE)

JST_URL = 'https://www.macrohistory.net/app/download/9834512569/JSTdatasetR6.xlsx'
T0, T1 = 1950, 2016          # anii de prognoza t (h <= 4 ani, datele JST R6 se opresc in 2020)
HMAX = 4
Q_DEBT, Q_PRICE = 0.80, 2 / 3
BLOCK, B_BOOT, BOOT_SEED = 5, 2000, 17
Q_GRID = [round(0.50 + 0.05 * i, 2) for i in range(10)]     # pragul creditului (percentila) pentru pagina interactiva
PAPER = {'rzone_3y': 0.40, 'normal_3y': 0.07}               # rezumatul articolului (JF 2022): ~40% si ~7% la 3 ani
SECTORS = {'bus': ('tbus', 'equity'), 'hh': ('thh', 'house')}

_CACHE = {}


def jst():
    """Baza JST Macrohistory R6 (online, fara cheie), ca DataFrame tara-an."""
    if 'jst' not in _CACHE:
        for attempt in range(4):
            try:
                req = urllib.request.Request(JST_URL, headers={'User-Agent': 'Mozilla/5.0'})
                raw = urllib.request.urlopen(req, timeout=180).read()
                break
            except OSError:
                if attempt == 3:
                    raise
        _CACHE['jst'] = pd.read_excel(io.BytesIO(raw), engine='openpyxl')
    return _CACHE['jst']


def panel():
    """Predictorii din ec. (2a)-(2b) si indicatorii Crisis_{t+1..t+h}, pe tari si ani."""
    d = jst().sort_values(['country', 'year']).copy()
    out = []
    for c, g in d.groupby('country'):
        g = g.set_index('year').reindex(range(g.year.min(), g.year.max() + 1))
        lcpi = np.log(g['cpi'])
        row = pd.DataFrame(index=g.index)
        row['country'] = c
        for s, (credit, _) in SECTORS.items():
            ratio = 100 * g[credit] / g['gdp']
            row[f'd_{s}'] = ratio - ratio.shift(3)
        leq = np.log1p(g['eq_capgain'])
        row['p_bus'] = 100 * (leq + leq.shift(1) + leq.shift(2) - (lcpi - lcpi.shift(3)))
        lhp = np.log(g['hpnom']) - lcpi
        row['p_hh'] = 100 * (lhp - lhp.shift(3))
        cr = g['crisisJST']
        row['onset'] = cr
        for h in range(1, HMAX + 1):
            fut = pd.concat([cr.shift(-j) for j in range(1, h + 1)], axis=1)
            row[f'c{h}'] = fut.max(axis=1).where(fut.notna().all(axis=1))
        out.append(row)
    p = pd.concat(out).rename_axis('year').reset_index()
    return p[(p.year >= T0) & (p.year <= T1)]


def sector_sample(p, s):
    cols = [f'd_{s}', f'p_{s}'] + [f'c{h}' for h in range(1, HMAX + 1)]
    return p.dropna(subset=cols)[['country', 'year'] + cols].rename(columns={f'd_{s}': 'debt', f'p_{s}': 'price'})


def flags(x, qd=Q_DEBT, qp=Q_PRICE):
    """High-Debt-Growth, High-Price-Growth, R-zone (praguri din distributia panelului, ca in articol)."""
    td, tp = float(np.quantile(x['debt'], qd)), float(np.quantile(x['price'], qp))
    hd, hp = (x['debt'] > td).values, (x['price'] > tp).values
    return hd, hp, hd & hp, td, tp


def block_index(years, rng, block=BLOCK):
    """Indicii unei replici bootstrap pe blocuri de ani calendaristici (circular)."""
    yrs = np.arange(T0, T1 + 1)
    n = len(yrs)
    starts = rng.integers(0, n, int(np.ceil(n / block)))
    pick = np.concatenate([yrs[(s + np.arange(block)) % n] for s in starts])[:n]
    by = {y: np.flatnonzero(years == y) for y in yrs}
    return np.concatenate([by[y] for y in pick])


def masks_of(x, qd=Q_DEBT):
    """R-zone, perioade normale si toate observatiile, cu pragurile (percentilele) estimate pe esantionul x."""
    hd, hp, rz, _, _ = flags(x, qd)
    return {'rzone': rz, 'normal': ~hd & ~hp, 'all': np.ones(len(x), bool)}


def boot_probs(x, keys, qd=Q_DEBT, B=B_BOOT, seed=BOOT_SEED, block=BLOCK):
    """CI 95% pentru P(Crisis_{t+1..t+h} = 1 | masca), h = 1..HMAX. In fiecare replica pragurile (percentilele
    panelului) se reestimeaza pe esantionul reesantionat, deci intervalul include incertitudinea regulii estimate.
    Intervalele sint punctuale (pentru fiecare orizont si sector separat), nu simultane."""
    rng = np.random.default_rng(seed)
    C = x[[f'c{h}' for h in range(1, HMAX + 1)]].values
    yrs = x['year'].values
    res = {k: np.full((B, HMAX), np.nan) for k in keys}
    for b in range(B):
        idx = block_index(yrs, rng, block)
        mk = masks_of(x.iloc[idx], qd)
        for k in keys:
            mm = mk[k]
            if mm.sum():
                res[k][b] = C[idx][mm].mean(axis=0)
    return {k: [[float(np.nanquantile(v[:, j], 0.025)), float(np.nanquantile(v[:, j], 0.975))] for j in range(HMAX)]
            for k, v in res.items()}


def boot_diff(x, qd=Q_DEBT, B=B_BOOT, seed=BOOT_SEED, block=BLOCK):
    """CI 95% pentru diferenta P(. | R-zone) - P(. | normal), h = 1..HMAX, cu pragurile reestimate in fiecare replica
    (aceleasi replici ca boot_probs)."""
    rng = np.random.default_rng(seed)
    C = x[[f'c{h}' for h in range(1, HMAX + 1)]].values
    yrs = x['year'].values
    d = np.full((B, HMAX), np.nan)
    for b in range(B):
        idx = block_index(yrs, rng, block)
        mk = masks_of(x.iloc[idx], qd)
        a, z = mk['rzone'], mk['normal']
        if a.sum() and z.sum():
            d[b] = C[idx][a].mean(axis=0) - C[idx][z].mean(axis=0)
    return [[float(np.nanquantile(d[:, j], 0.025)), float(np.nanquantile(d[:, j], 0.975))] for j in range(HMAX)]


def probs(x, m):
    C = x[[f'c{h}' for h in range(1, HMAX + 1)]].values
    return [float(v) for v in C[m].mean(axis=0)]


def preceded(p, x, rz, s):
    """Crizele (anul de inceput in T0+1..T1+1) precedate de R-zone in cel putin unul din cei 3 ani anteriori."""
    on = set(map(tuple, x.loc[rz, ['country', 'year']].values))
    cr = p[(p['onset'] == 1)][['country', 'year']]
    cr = cr[(cr.year > T0) & (cr.year <= T1 + 1)]
    have = set(map(tuple, x[['country', 'year']].values))
    rows = []
    for c, y in cr.values:
        obs = [(c, y - j) in have for j in (1, 2, 3)]
        if not any(obs):
            continue                       # nicio observatie a sectorului in cei 3 ani: criza nu intra in numarator
        rows.append(dict(country=c, year=int(y), hit=any((c, y - j) in on for j in (1, 2, 3))))
    return rows


def sector_stats(p, s, qd=Q_DEBT, boot=True):
    x = sector_sample(p, s).reset_index(drop=True)
    hd, hp, rz, td, tp = flags(x, qd)
    normal = ~hd & ~hp
    allm = np.ones(len(x), bool)
    o = dict(n=int(len(x)), n_countries=int(x['country'].nunique()), first=int(x.year.min()), last=int(x.year.max()),
             thr_debt=td, thr_price=tp, n_rzone=int(rz.sum()), n_normal=int(normal.sum()),
             p_rzone=probs(x, rz), p_normal=probs(x, normal), p_all=probs(x, allm),
             )
    pre = preceded(p, x, rz, s)
    o['crises'] = pre
    o['n_crises'] = len(pre)
    o['n_preceded'] = int(sum(r['hit'] for r in pre))
    o['rzone_years'] = [dict(country=c, year=int(y)) for c, y in x.loc[rz, ['country', 'year']].values]
    if boot:
        ci = boot_probs(x, ['rzone', 'normal', 'all'], qd)
        o['ci_rzone'], o['ci_normal'], o['ci_all'] = ci['rzone'], ci['normal'], ci['all']
        o['ci_diff'] = boot_diff(x, qd)
        # sensitivity to the block length (3, 5, 8 calendar years), horizon h = 3
        o['block_sens'] = {}
        for bl in (3, 5, 8):
            cb = boot_probs(x, ['rzone'], qd, block=bl)['rzone'][2] if bl != BLOCK else o['ci_rzone'][2]
            db = boot_diff(x, qd, block=bl)[2] if bl != BLOCK else o['ci_diff'][2]
            o['block_sens'][str(bl)] = dict(ci_rzone_3=cb, ci_diff_3=db)
        # thresholds in log points (100 x Delta_3 log P) and as simple growth
        o['thr_price_simple'] = float(np.expm1(tp / 100))
    return o, x


def fig_ghss(res):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
    h = np.arange(1, HMAX + 1)
    names = {'bus': 'Business credit/GDP, real stock prices', 'hh': 'Household credit/GDP, real house prices'}
    for ax, s in zip(axes, ['bus', 'hh']):
        o = res[s]
        for key, col, lab, off, ls in [('rzone', IDAred, 'R-zone', -0.08, '-'),
                                       ('normal', MainBlue, 'Normal times (neither growth high)', 0.08, '-'),
                                       ('all', Forest, 'All country-years', 0.0, '--')]:
            y = 100 * np.array(o[f'p_{key}'])
            lo = 100 * np.array([c[0] for c in o[f'ci_{key}']])
            hi = 100 * np.array([c[1] for c in o[f'ci_{key}']])
            ax.errorbar(h + off, y, yerr=[y - lo, hi - y], fmt='o', ls=ls, color=col, capsize=3, ms=4, lw=1.3,
                        label=lab + ' (95% CI, year-block bootstrap)' if key == 'rzone' else lab)
        ax.plot([3.18], [100 * PAPER['rzone_3y']], 'D', mfc='none', mec=IDAred, ms=6, mew=1.2,
                label='Greenwood et al. (2022), 42 countries: R-zone, h = 3')
        ax.plot([3.18], [100 * PAPER['normal_3y']], 'D', mfc='none', mec=MainBlue, ms=6, mew=1.2,
                label='Greenwood et al. (2022): normal times, h = 3')
        ax.set_xticks(h)
        ax.set_xlabel('Horizon h (years after t)')
        ax.set_title(names[s] + f'\n{o["n_countries"]} economies, {o["n_rzone"]} R-zone years of {o["n"]}', fontsize=8.5, color='black')
    axes[0].set_ylabel('P(crisis begins in t+1 ... t+h), %')
    fig.suptitle(f'Crisis probability after credit and asset price booms, JST Macrohistory data, forecasts made in {T0}-{T1}',
                 fontsize=8.5, x=0.02, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    hs, ls = axes[0].get_legend_handles_labels()
    order = [ls.index(l) for l in ls if l.startswith('R-zone')] + [ls.index(l) for l in ls if l.startswith('Normal')] + \
        [ls.index(l) for l in ls if l.startswith('All')] + [ls.index(l) for l in ls if l.startswith('Greenwood')]
    fig.legend([hs[i] for i in order], [ls[i] for i in order], loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2,
               frameon=False)
    save_fig('ch17_ghss_rzone')


def grid(p):
    """Pentru pagina interactiva: pragul creditului (percentila) variaza, pragul pretului ramane la 66,7."""
    out = {}
    for s in SECTORS:
        rows = []
        for q in Q_GRID:
            o, x = sector_stats(p, s, qd=q, boot=False)
            ci = boot_probs(x, ['rzone', 'normal'], q)
            rows.append(dict(q=q, thr_debt=o['thr_debt'], n_rzone=o['n_rzone'], p_rzone=o['p_rzone'], ci_rzone=ci['rzone'],
                             n_normal=o['n_normal'], p_normal=o['p_normal'], ci_normal=ci['normal'],
                             n_crises=o['n_crises'], n_preceded=o['n_preceded']))
        out[s] = rows
    return out


def main(with_grid=False):
    p = panel()
    res = {}
    for s in SECTORS:
        res[s], _ = sector_stats(p, s)
    on = {s: set((r['country'], r['year']) for r in res[s]['rzone_years']) for s in SECTORS}
    both = {}
    for s in SECTORS:
        for r in res[s]['crises']:
            both[(r['country'], r['year'])] = any((r['country'], r['year'] - j) in on[k] for k in SECTORS for j in (1, 2, 3))
    res['either'] = dict(n_crises=len(both), n_preceded=int(sum(both.values())))
    res['paper'] = PAPER
    res['sample'] = dict(t0=T0, t1=T1, block=BLOCK, B=B_BOOT, countries=int(p['country'].nunique()),
                         onsets=int(((p['onset'] == 1) & (p.year > T0) & (p.year <= T1 + 1)).sum()))
    fig_ghss(res)
    if with_grid:
        res['grid'] = grid(p)
    with open(os.path.join(HERE, 'case17_crises.json'), 'w') as f:
        json.dump(jsonable(res), f, indent=1)
    return res, p


if __name__ == '__main__':
    r, _ = main(with_grid=True)
    for s in SECTORS:
        o = r[s]
        print(s, {k: o[k] for k in ['n', 'n_countries', 'first', 'last', 'thr_debt', 'thr_price', 'n_rzone', 'n_normal',
                                    'n_crises', 'n_preceded']})
        for k in ['rzone', 'normal', 'all']:
            print('  ', k, [round(100 * v, 1) for v in o[f'p_{k}']], [[round(100 * a, 1), round(100 * b, 1)] for a, b in o[f'ci_{k}']])
        print('  diff', [[round(100 * a, 1), round(100 * b, 1)] for a, b in o['ci_diff']])
        print('  crises', [(c['country'], c['year'], c['hit']) for c in o['crises']])
    print('either', r['either'], r['sample'])
    for s in SECTORS:
        print(s, [(g['q'], g['n_rzone'], round(100 * g['p_rzone'][2], 1), g['n_preceded'], g['n_crises']) for g in r['grid'][s]])

"""
case_vast_dcc.py -- Capitolul 6, al doilea studiu de caz: DCC in dimensiuni mari
=================================================================================
Pakel, Shephard, Sheppard & Engle (2021), Fitting vast dimensional time-varying covariance models,
Journal of Business & Economic Statistics 39(3), 652-668, doi:10.1080/07350015.2020.1713795.

Afirmatia articolului: cu correlation targeting, verosimilitatea completa a DCC da parametri dinamici (a, b)
deplasati cind numarul de active K creste (problema parametrilor incidentali: cele K(K-1)/2 elemente ale lui Qbar
sint estimate); verosimilitatea compusa (suma verosimilitatilor bivariate pe perechi) nu are aceasta deplasare
si costa O(K^2) (toate perechile) sau O(K) (perechile contigue).

Replicarea pe datele cursului:
  * universul: toate actiunile si ETF-urile listate in SUA din data/market cu istoric complet din 18 iulie 2013
    (48 de serii), randamente zilnice log pe zilele comune (mfm_data.joint_returns), pina la 18 septembrie 2026;
  * pasul 1: GARCH(1,1) Normal pe fiecare serie (dep_tools.garch_all, ca in capitol);
  * pasul 2, pentru o sectiune transversala care creste (ordinea alfabetica a tickerelor, ca in articol):
      - verosimilitatea completa (dep_tools.dcc_fit, DCC-ul capitolului, correlation targeting);
      - verosimilitatea compusa pe toate perechile si pe perechile contigue, cu aceeasi tinta Qbar;
  * robustete: 10 ordini aleatoare ale activelor (seed 42), K in {5, 10, 20, 30, 40}, verosimilitatea completa
    si cea compusa pe perechile contigue;
  * consecinta: abaterea standard in timp a corelatiei medii conditionate dintre cele 48 de active, cu fiecare
    pereche (a, b).
Iesire: ch6_vast_dcc.json si graficul ch6_vast_dcc.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mfm_data as md   # noqa: E402
from dep_tools import garch_all, dcc_fit, dcc2_corr_loglik, dcc_path   # noqa: E402

START = '2013-07-18'           # first day of QUAL, the youngest series of the universe
K_GRID = [2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 48]
K_RAND = [5, 10, 20, 30, 40]
N_RAND = 10
SEED = 42


# every US-listed stock and ETF of data/market whose history starts on or before START (alphabetical order)
UNIVERSE = ['AAPL', 'AGG', 'AMZN', 'BAC', 'C', 'CSCO', 'DBC', 'EEM', 'EFA', 'GLD', 'GME', 'GOOGL', 'GS', 'HYG', 'IEF',
            'IWD', 'IWF', 'IWM', 'JPM', 'LQD', 'META', 'MS', 'MSFT', 'MSTR', 'MTUM', 'NVDA', 'QQQ', 'QUAL', 'RSP', 'SHY',
            'SPY', 'TIP', 'TLT', 'TSLA', 'UNG', 'USMV', 'USO', 'VLUE', 'WFC', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP',
            'XLU', 'XLV', 'XLY']


def universe():
    """UNIVERSE, checked against the local data/market folder when it is there."""
    files = sorted(glob.glob(os.path.join(md.MARKET_DIR, '*.US.csv')))
    if files:
        found = [os.path.basename(f)[:-len('.US.csv')] for f in files
                 if pd.read_csv(f, nrows=1)['date'].iloc[0] <= START]
        assert found == UNIVERSE, (found, UNIVERSE)
    return list(UNIVERSE)


def residuals(tickers):
    for s in tickers:
        md.ASSETS['us_' + s.lower()] = (s + '.US', 'adjusted_close', s, START)
    R = md.joint_returns(['us_' + s.lower() for s in tickers], start=START)
    R.columns = tickers
    P, V, Z, _ = garch_all(R)
    return R, P, Z


def cl_fit(Z, pairs, start=(0.03, 0.95)):
    """Composite likelihood of DCC: sum of the bivariate correlation log-likelihoods over the pairs,
    each pair with its own block of the targeted Qbar (the sample covariance of the standardised residuals);
    same starts and optimiser as dep_tools.dcc_fit."""
    X = np.asarray(Z, dtype=float)
    Qbar = np.cov(X.T, bias=True)
    cols = [np.ascontiguousarray(X[:, i]) for i in range(X.shape[1])]

    def nll(p):
        a, b = p
        if a < 0 or b < 0 or a + b >= 0.9999:
            return 1e10
        return -sum(dcc2_corr_loglik(cols[i], cols[j], float(a), float(b), Qbar[i, i], Qbar[j, j], Qbar[i, j])
                    for i, j in pairs)

    best = None
    for s in (start, (0.01, 0.98), (0.05, 0.90), (0.10, 0.80)):
        r = optimize.minimize(nll, s, method='Nelder-Mead', options=dict(xatol=1e-7, fatol=1e-7, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
    return dict(a=float(best.x[0]), b=float(best.x[1]), loglik=float(-best.fun))


def all_pairs(k):
    return [(i, j) for i in range(k) for j in range(i + 1, k)]


def contiguous(k):
    return [(i, i + 1) for i in range(k - 1)]


def ml(Z):
    f = dcc_fit(Z)
    return dict(a=float(f['a']), b=float(f['b']), se_a=float(f['se_a']), se_b=float(f['se_b']))


def avg_corr_path(Z, a, b):
    R = dcc_path(Z, a, b)
    k = R.shape[1]
    iu = np.triu_indices(k, 1)
    return R[:, iu[0], iu[1]].mean(axis=1)


def run():
    t0 = time.time()
    tickers = universe()
    R, P, Z = residuals(tickers)
    print(f'universe: {len(tickers)} series, {len(Z)} days, {Z.index[0].date()} - {Z.index[-1].date()}')

    expand = []
    for k in K_GRID:
        Zk = Z.iloc[:, :k]
        row = dict(K=k, ml=ml(Zk), cl_all=cl_fit(Zk, all_pairs(k)), cl_contig=cl_fit(Zk, contiguous(k)))
        expand.append(row)
        print(f"K={k:2d}  ML a={row['ml']['a']:.4f} b={row['ml']['b']:.4f}   CL-all a={row['cl_all']['a']:.4f} "
              f"b={row['cl_all']['b']:.4f}   CL-contig a={row['cl_contig']['a']:.4f} b={row['cl_contig']['b']:.4f}"
              f"   ({time.time() - t0:.0f}s)", flush=True)

    rng = np.random.default_rng(SEED)
    rand = []
    for d in range(N_RAND):
        perm = rng.permutation(len(tickers))
        for k in K_RAND:
            Zk = Z.iloc[:, perm[:k]]
            rand.append(dict(draw=d, K=k, ml=ml(Zk), cl_contig=cl_fit(Zk, contiguous(k))))
        print(f'random order {d + 1}/{N_RAND} done ({time.time() - t0:.0f}s)', flush=True)

    full = expand[-1]
    paths = {}
    for key in ('ml', 'cl_all'):
        p = avg_corr_path(Z, full[key]['a'], full[key]['b'])
        paths[key] = p
    out = dict(
        paper=dict(ref='Pakel, Shephard, Sheppard & Engle (2021), JBES 39(3), 652-668',
                   doi='10.1080/07350015.2020.1713795'),
        start=str(Z.index[0].date()), end=str(Z.index[-1].date()), T=int(len(Z)), tickers=tickers,
        garch_persistence_median=float((P.loc['alpha[1]'] + P.loc['beta[1]']).median()),
        expand=expand, random=rand,
        avg_corr=dict(mean=float(paths['ml'].mean()),
                      sd_ml=float(paths['ml'].std()), sd_cl=float(paths['cl_all'].std()),
                      min_ml=float(paths['ml'].min()), max_ml=float(paths['ml'].max()),
                      min_cl=float(paths['cl_all'].min()), max_cl=float(paths['cl_all'].max())),
        half_life=dict(ml=float(np.log(0.5) / np.log(full['ml']['a'] + full['ml']['b'])),
                       cl_all=float(np.log(0.5) / np.log(full['cl_all']['a'] + full['cl_all']['b']))),
    )
    with open(os.path.join(HERE, 'ch6_vast_dcc.json'), 'w') as f:
        json.dump(out, f, indent=1)
    pd.DataFrame({'date': Z.index.strftime('%Y-%m-%d'), 'avg_corr_ml': paths['ml'],
                  'avg_corr_cl': paths['cl_all']}).to_csv(os.path.join(HERE, 'ch6_vast_dcc_avgcorr.csv'),
                                                          index=False, float_format='%.5f')
    print(f'saved ch6_vast_dcc.json ({time.time() - t0:.0f}s)')
    return out


def chart(out=None):
    import matplotlib.pyplot as plt
    from generate_all_charts import save_fig, MainBlue, IDAred, Forest
    if out is None:
        with open(os.path.join(HERE, 'ch6_vast_dcc.json')) as f:
            out = json.load(f)
    E = out['expand']
    K = [r['K'] for r in E]
    rnd = pd.DataFrame([dict(K=r['K'], ml_a=r['ml']['a'], ml_b=r['ml']['b'], cl_a=r['cl_contig']['a'],
                             cl_b=r['cl_contig']['b']) for r in out['random']])
    band = rnd.groupby('K').agg(['min', 'max'])
    RedTint, BlueTint = '#F2B8B8', '#C5D2E8'

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, par, lab in ((axes[0], 'a', r'$\hat a$ (news coefficient)'), (axes[1], 'b', r'$\hat b$ (persistence)')):
        ax.fill_between(band.index, band[('ml_' + par, 'min')], band[('ml_' + par, 'max')], color=RedTint,
                        alpha=0.7, lw=0, label='Full likelihood, 10 random orders (range)')
        ax.fill_between(band.index, band[('cl_' + par, 'min')], band[('cl_' + par, 'max')], color=BlueTint,
                        alpha=0.7, lw=0, label='Composite, contiguous pairs, 10 random orders (range)')
        ax.plot(K, [r['ml'][par] for r in E], 'o-', color=IDAred, ms=3.5, label='Full likelihood')
        ax.plot(K, [r['cl_all'][par] for r in E], 's-', color=MainBlue, ms=3.5, label='Composite, all pairs')
        ax.plot(K, [r['cl_contig'][par] for r in E], '^--', color=Forest, ms=3.5,
                label='Composite, contiguous pairs')
        ax.set_xlabel('Number of assets K (alphabetical order)')
        ax.set_ylabel(lab)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    save_fig('ch6_vast_dcc')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'chart':
        chart()
    else:
        chart(run())

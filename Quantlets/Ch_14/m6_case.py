"""
m6_case.py -- Capitolul 14, al doilea studiu de caz: Makridakis, Spiliotis, Hollyman, Petropoulos, Swanson & Gaba
              (2025), The M6 forecasting competition, International Journal of Forecasting 41(4), 1315-1354
=====================================================================================================================
Replicare pe datele cursului a sarcinii de prognoza din M6 (Sectiunea 2.5 din lucrare): pentru fiecare activ,
probabilitatile ca randamentul total pe 4 saptamini sa cada in fiecare chintila a universului; evaluare cu Ranked
Probability Score (RPS, ec. 1-3) fata de reperul cu probabilitati egale (0,2).
  * universul: cele 19 active M6 care exista in data/market (AMZN, JPM, META, HYG, IEF, IWM, LQD, SHY, TLT si cele
    10 ETF-uri sectoriale XL*; Tabelul A3 din lucrare), preturi ajustate (adjusted_close, EODHD)
  * perioadele M6: cele 12 perioade de 4 saptamini dintre 4.03.2022 si 3.02.2023 (Tabelul 1); perioade extinse:
    acelasi calendar de 4 saptamini (4.03.2022 + 28k zile), din iulie 2019 pina la ultima zi din date
  * cu 19 active (nu 100), chintilele realizate sint fractionare: activul de pe pozitia r ocupa intervalul
    [(r-1)/N, r/N], iar q_k este partea lui din chintila k (generalizarea regulii M6 pentru egalitati)
  * prognoze: (U) reperul 0,2; (HM) media istorica: randamente normale cu media si covarianta din ultimele 250 de
    zile; (VOL) doar volatilitatea: media 0 si covarianta EWMA (lambda = 0,94); (NN) o retea mica (4 -> 8 -> 5),
    antrenata pe toate perioadele anterioare (din 2004) cu RPS ca pierdere, reestimata la inceputul fiecarui an;
    intrari: volatilitatile pe 20 si 250 de zile si randamentele pe 20 si 250 de zile, standardizate in sectiune
  * HM si VOL: 20 000 de simulari ale vectorului de randamente pe 20 de zile, chintile din ranguri (fara antrenare)
  * test: Diebold-Mariano (HAC) pe diferentele de RPS pe perioade, fata de U
Iesire: m6_case.json, m6_case_probs.json (probabilitatile, pentru pagina interactiva), charts/ch14_m6_rps.pdf/.png
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
import mfm_tsfm as M               # noqa: E402
import generate_all_charts as g    # noqa: E402  (stil MFM, culori, save_fig)

ASSETS = ['AMZN', 'JPM', 'META', 'HYG', 'IEF', 'IWM', 'LQD', 'SHY', 'TLT',
          'XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY']
M6_BASE = ['2022-03-04', '2022-04-01', '2022-04-29', '2022-05-27', '2022-06-24', '2022-07-22', '2022-08-19',
           '2022-09-16', '2022-10-14', '2022-11-11', '2022-12-09', '2023-01-06', '2023-02-03']
EXT_FROM = '2019-07-01'
TRAIN_FROM = '2004-01-01'
NSIM = 20000
LAM = 0.94
MODELS = ['HM', 'VOL', 'NN']
LBL = {'U': 'Equal probabilities (benchmark)', 'HM': 'Historical mean and covariance',
       'VOL': 'Volatility only (EWMA, zero mean)', 'NN': 'Small network (4, 8, 5)'}
COL = {'HM': g.Amber, 'VOL': g.MainBlue, 'NN': g.Forest}
# published statistics, each with its own sample (Makridakis et al., 2025): 163 teams in the global leaderboard,
# 38 of them (23.3%) below the benchmark RPS 0.16; median 0.162 and mean 0.179 over 162 teams; RPS-IR correlation
# 0.04 (p = 0.601) over the 138 teams whose forecasts differ from the benchmark; at most 2.2% RPS reduction among the
# 11 teams that beat the benchmark in both tasks. The benchmark 0.16 is for 100 assets and 0/1 quintile indicators.
PAPER = dict(bench=0.16, median=0.162, mean=0.179, n_teams=163, beat=38, beat_share=23.3, n_median=162,
             corr=0.04, corr_p=0.601, n_corr=138, both_max=2.2, n_both=11)


def prices():
    P = pd.concat({a: M.read_market(f'{a}.US')['adjusted_close'] for a in ASSETS}, axis=1).sort_index()
    return P[P.index >= '2002-01-01']


def realised_q(R):
    """Fractional quintile membership (N x 5) of the realised returns R (N,): position r covers [(r-1)/N, r/N]."""
    N = len(R)
    pos = np.empty(N)
    pos[np.argsort(R, kind='mergesort')] = np.arange(N)
    lo, hi = pos / N, (pos + 1) / N
    k0, k1 = np.arange(5) / 5, np.arange(1, 6) / 5
    q = np.clip(np.minimum(hi[:, None], k1) - np.maximum(lo[:, None], k0), 0, None) * N
    return q


def rps(q, f):
    """Ranked probability score of each asset (eq. 1): mean over j of (cumsum q - cumsum f)^2."""
    return ((np.cumsum(q, 1) - np.cumsum(f, 1)) ** 2).mean(1)


def sim_probs(mu, S, rng):
    """Quintile probabilities from NSIM Normal draws of the h-day return vector (rank-based, fractional)."""
    N = len(mu)
    Z = rng.multivariate_normal(mu, S, size=NSIM, method='cholesky')
    pos = np.argsort(np.argsort(Z, 1), 1)
    lo, hi = pos / N, (pos + 1) / N
    k0, k1 = np.arange(5) / 5, np.arange(1, 6) / 5
    q = np.clip(np.minimum(hi[..., None], k1) - np.maximum(lo[..., None], k0), 0, None) * N
    return q.mean(0)


def ewma_cov(X, lam=LAM):
    S = np.cov(X[:60].T)
    for x in X[60:]:
        S = lam * S + (1 - lam) * np.outer(x, x)
    return S


def periods(idx):
    """Four-week periods on the M6 calendar: base dates 4 March 2022 + 28k days (last trading day on or before),
    consecutive pairs. Returns the 12 M6 periods, the evaluation periods from EXT_FROM (the M6 periods among them)
    and the training periods of the network from TRAIN_FROM, as (i0, i1) positions."""
    d0 = pd.Timestamp(M6_BASE[0])
    ks = range(-int((d0 - pd.Timestamp(TRAIN_FROM)).days // 28), int((idx[-1] - d0).days // 28) + 1)
    pos = sorted({int(np.searchsorted(idx, d0 + pd.Timedelta(days=28 * k), side='right') - 1) for k in ks})
    pairs = list(zip(pos[:-1], pos[1:]))
    m6b = [int(idx.get_indexer([pd.Timestamp(d)])[0]) for d in M6_BASE]
    assert min(m6b) >= 0
    m6 = list(zip(m6b[:-1], m6b[1:]))
    assert all(p in pairs for p in m6)
    ext = [p for p in pairs if idx[p[0]] >= pd.Timestamp(EXT_FROM)]
    return m6, ext, pairs


def features(L, i0, ok):
    """Cross-sectionally standardised features at base position i0 for the available assets ok."""
    x = L[i0 - 249:i0 + 1][:, ok]
    f = np.column_stack([np.log(x[-20:].std(0)), np.log(x.std(0)), x[-20:].sum(0), x.sum(0)])
    return (f - f.mean(0)) / f.std(0)


def nn_fit(Xs, Qs, seed):
    """4 -> 8 -> 5 network (tanh, softmax), mean RPS as loss, Adam, 300 epochs, 10 initialisations averaged
    (d -> 8 -> 5 when the features have d columns)."""
    import torch
    torch.manual_seed(seed)
    X = torch.tensor(np.vstack(Xs), dtype=torch.float32)
    Q = torch.tensor(np.vstack(Qs), dtype=torch.float32)
    nets = []
    for s in range(10):
        net = torch.nn.Sequential(torch.nn.Linear(X.shape[1], 8), torch.nn.Tanh(), torch.nn.Linear(8, 5))
        opt = torch.optim.Adam(net.parameters(), lr=1e-2, weight_decay=1e-3)
        for _ in range(300):
            opt.zero_grad()
            p = torch.softmax(net(X), 1)
            loss = ((torch.cumsum(Q, 1) - torch.cumsum(p, 1)) ** 2).mean()
            loss.backward()
            opt.step()
        nets.append(net)

    def predict(Xn):
        with torch.no_grad():
            Z = torch.tensor(Xn, dtype=torch.float32)
            return np.mean([torch.softmax(n(Z), 1).numpy() for n in nets], 0)
    return predict


def run():
    P = prices()
    idx = P.index
    L = np.log(P).diff().values
    m6, ext, allp = periods(idx)
    rng = np.random.default_rng(14)
    eval_p = sorted(set(m6) | set(ext))
    out = {}
    # training sample of the network: every four-week period from 2004 (assets present over the whole window)
    train = []
    for i0, i1 in allp:
        ok = np.isfinite(L[i0 - 249:i1 + 1]).all(0) & np.isfinite(P.values[i0]) & np.isfinite(P.values[i1])
        if ok.sum() < 10:
            continue
        R = P.values[i1, ok] / P.values[i0, ok] - 1
        train.append((i0, i1, features(L, i0, ok), realised_q(R)))
    year_fit = {}
    for i0, i1 in eval_p:
        ok = np.isfinite(L[i0 - 249:i1 + 1]).all(0)
        assert ok.all(), idx[i0]
        R = P.values[i1] / P.values[i0] - 1
        q = realised_q(R)
        X = L[i0 - 249:i0 + 1]
        h = i1 - i0                                    # trading days in the period
        mu = h * X.mean(0)
        S250 = h * np.cov(X.T)
        Sew = h * ewma_cov(X)
        fU = np.full((len(ASSETS), 5), 0.2)
        fHM = sim_probs(mu, S250, rng)
        fVOL = sim_probs(np.zeros(len(ASSETS)), Sew, rng)
        y = idx[i0].year
        if y not in year_fit:     # re-estimated at the start of each year, on the blocks that ended before
            past = [t for t in train if t[1] <= i0]
            year_fit[y] = nn_fit([t[2] for t in past], [t[3] for t in past], seed=y)
            print(f'   NN {y}: {len(past)} training blocks')
        fNN = year_fit[y](features(L, i0, np.ones(len(ASSETS), bool)))
        f = dict(U=fU, HM=fHM, VOL=fVOL, NN=fNN)
        out[(i0, i1)] = dict(start=str(idx[i0].date()), end=str(idx[i1].date()), R=R, q=q,
                             f=f, rps={m: float(rps(q, v).mean()) for m, v in f.items()},
                             vol=np.sqrt(np.diag(Sew) / h * 252))
    return idx, m6, ext, out


def summarise(m6, ext, out):
    res = {'assets': ASSETS, 'paper': PAPER, 'n_assets': len(ASSETS)}
    for name, per in (('m6', m6), ('ext', ext)):
        D = pd.DataFrame([out[p]['rps'] for p in per])
        r = {'n': len(per), 'start': out[per[0]]['start'], 'end': out[per[-1]]['end'],
             'U': float(D['U'].mean())}
        for m in MODELS:
            dm = M.diebold_mariano(D[m], D['U'])
            r[m] = dict(rps=float(D[m].mean()), gain=float(100 * (1 - D[m].mean() / D['U'].mean())),
                        dm=dm['DM'], p=dm['p'], share_better=float(100 * (D[m] < D['U'] - 1e-12).mean()))
        res[name] = r
    # where the volatility model gains: RPS by realised quintile of the asset and the dispersion of its forecasts
    per = ext
    q_all = np.vstack([out[p]['q'] for p in per])
    for m in ('VOL', 'NN', 'HM'):
        f_all = np.vstack([out[p]['f'][m] for p in per])
        e = rps(q_all, f_all) - rps(q_all, np.full_like(f_all, 0.2))
        res['ext'][m]['by_quintile'] = [float(e[q_all[:, k] > 0.5].mean()) for k in range(5)]
        res['ext'][m]['p_extreme_mean'] = float((f_all[:, 0] + f_all[:, 4]).mean())
    # the volatility of each asset and its probability of an extreme quintile (VOL, last M6 period)
    p = m6[0]
    res['m6_first'] = dict(start=out[p]['start'], vol=dict(zip(ASSETS, map(float, out[p]['vol']))),
                           p_ext=dict(zip(ASSETS, map(float, out[p]['f']['VOL'][:, [0, 4]].sum(1)))))
    return res


def fig_rps(idx, m6, ext, out, res):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1, 1.35]))
    ax = axes[0]
    xs = np.arange(2)
    w = 0.26
    for j, m in enumerate(MODELS):
        v = [res['m6'][m]['gain'], res['ext'][m]['gain']]
        ax.bar(xs + (j - 1) * w, v, width=w, color=COL[m], label=LBL[m])
        for xi, vi in zip(xs + (j - 1) * w, v):
            ax.text(xi, vi + (0.08 if vi >= 0 else -0.08), f'{vi:.1f}', ha='center', va='bottom' if vi >= 0 else 'top',
                    fontsize=7, color='black')
    med = 100 * (1 - PAPER['median'] / PAPER['bench'])
    ax.axhline(med, color=g.IDAred, ls=':', lw=1.0, label='Paper: median M6 team (100 assets)')
    ax.axhline(0, color=g.Navy, lw=0.8)
    ax.set_xticks(xs, [f'M6 year ({res["m6"]["n"]} periods)', f'2019–2026 ({res["ext"]["n"]} periods)'])
    lo = min(min(res[k][m]['gain'] for k in ('m6', 'ext') for m in MODELS), 100 * (1 - PAPER['median'] / PAPER['bench']))
    hi = max(res[k][m]['gain'] for k in ('m6', 'ext') for m in MODELS)
    ax.set_ylim(lo - 0.7, hi + 0.6)
    ax.set_ylabel('RPS gain over equal\nprobabilities (%)')
    ax = axes[1]
    D = pd.DataFrame([out[p]['rps'] for p in ext], index=pd.to_datetime([out[p]['end'] for p in ext]))
    for m in MODELS:
        ax.plot(D.index, (D['U'] - D[m]).cumsum(), color=COL[m], lw=1.2)
    ax.axvspan(pd.Timestamp(M6_BASE[0]), pd.Timestamp(M6_BASE[-1]), color=g.BandBlue, alpha=0.7, lw=0,
               label='M6 competition year')
    ax.axhline(0, color=g.Navy, lw=0.8)
    ax.set_ylabel('Cumulative RPS gain over\nequal probabilities')
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    h0, l0 = axes[0].get_legend_handles_labels()
    h1, l1 = axes[1].get_legend_handles_labels()
    g.fig_legend_bottom(fig, h0 + h1, l0 + l1, ncol=3, y=0.0)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    g.save_fig('ch14_m6_rps')


def export_probs(m6, ext, out):
    """Per-period realised quintiles and forecasts (3 decimals) for the interactive page."""
    per = sorted(set(m6) | set(ext))
    rows = []
    for p in per:
        o = out[p]
        rows.append(dict(start=o['start'], end=o['end'], m6=p in m6, ext=p in ext,
                         q=np.round(o['q'], 4).tolist(), R=np.round(100 * o['R'], 3).tolist(),
                         f={m: np.round(o['f'][m], 4).tolist() for m in MODELS}, rps=o['rps']))
    with open(os.path.join(HERE, 'm6_case_probs.json'), 'w') as fh:
        json.dump(dict(assets=ASSETS, periods=rows), fh, separators=(',', ':'))


def ablation():
    """Mechanism checks on the same periods (written to m6_case.json under 'ablation'; the main results unchanged):
    (i) direction: zero mean versus the 250-day mean, both with the same 250-day sample covariance (ZM250 vs HM);
    (ii) network: the same network without the two return inputs (volatilities only, NN-vol) against NN;
    (iii) NN against VOL. DM (HAC) on the per-period RPS differences."""
    P = prices()
    idx = P.index
    L = np.log(P).diff().values
    m6, ext, allp = periods(idx)
    rng = np.random.default_rng(15)
    with open(os.path.join(HERE, 'm6_case_probs.json')) as fh:
        saved = {(r['start'], r['end']): r['rps'] for r in json.load(fh)['periods']}
    train = []
    for i0, i1 in allp:
        ok = np.isfinite(L[i0 - 249:i1 + 1]).all(0) & np.isfinite(P.values[i0]) & np.isfinite(P.values[i1])
        if ok.sum() < 10:
            continue
        R = P.values[i1, ok] / P.values[i0, ok] - 1
        train.append((i0, i1, features(L, i0, ok)[:, :2], realised_q(R)))
    year_fit, rows = {}, {}
    for i0, i1 in sorted(set(m6) | set(ext)):
        R = P.values[i1] / P.values[i0] - 1
        q = realised_q(R)
        X = L[i0 - 249:i0 + 1]
        h = i1 - i0
        fZM = sim_probs(np.zeros(len(ASSETS)), h * np.cov(X.T), rng)
        y = idx[i0].year
        if y not in year_fit:
            past = [t for t in train if t[1] <= i0]
            year_fit[y] = nn_fit([t[2] for t in past], [t[3] for t in past], seed=y)
        fNV = year_fit[y](features(L, i0, np.ones(len(ASSETS), bool))[:, :2])
        r = dict(saved[(str(idx[i0].date()), str(idx[i1].date()))])
        r.update(ZM250=float(rps(q, fZM).mean()), NNvol=float(rps(q, fNV).mean()))
        rows[(i0, i1)] = r
    res = {}
    for name, per in (('m6', m6), ('ext', ext)):
        D = pd.DataFrame([rows[p] for p in per])
        r = {'n': len(per)}
        for a_, b_ in (('ZM250', 'HM'), ('NNvol', 'NN'), ('NN', 'VOL'), ('ZM250', 'U'), ('NNvol', 'U')):
            dm = M.diebold_mariano(D[a_], D[b_])
            r[f'{a_}_vs_{b_}'] = dict(dm=dm['DM'], p=dm['p'], diff=float(100 * (D[a_].mean() / D[b_].mean() - 1)))
        r['gain'] = {m: float(100 * (1 - D[m].mean() / D['U'].mean())) for m in ('ZM250', 'NNvol')}
        res[name] = r
    path = os.path.join(HERE, 'm6_case.json')
    with open(path) as fh:
        full = json.load(fh)
    full['ablation'] = res
    full['paper'] = PAPER
    with open(path, 'w') as fh:
        json.dump(full, fh, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


def main():
    if sys.argv[1:] == ['ablation']:
        ablation()
        return
    idx, m6, ext, out = run()
    res = summarise(m6, ext, out)
    fig_rps(idx, m6, ext, out, res)
    export_probs(m6, ext, out)
    with open(os.path.join(HERE, 'm6_case.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=float)
    for k in ('m6', 'ext'):
        r = res[k]
        print(k, r['n'], r['start'], r['end'], 'U', round(r['U'], 4),
              {m: (round(r[m]['rps'], 4), round(r[m]['gain'], 2), round(r[m]['p'], 3), round(r[m]['share_better'], 0))
               for m in MODELS})
    print({m: [round(x, 4) for x in res['ext'][m]['by_quintile']] for m in ('VOL', 'NN', 'HM')})


if __name__ == '__main__':
    main()

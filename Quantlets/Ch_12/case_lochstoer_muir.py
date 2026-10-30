"""
Studiul de caz 2 al Capitolului 12: Lochstoer & Muir (2022), Volatility expectations and returns,
Journal of Finance 77(2), 1055-1096, doi:10.1111/jofi.13120.
================================================================================================
Replicare pe datele cursului (data/market: S&P 500 si VIX, zilnic, 1990-2026; rata fara risc zilnica din
Kenneth French Data Library, prin ff_rf_daily din generate_all_charts.py):
  1. ecuatia (4) / Tabelul 1: VIX^2 la sfirsitul lunii t si varianta realizata in luna t+1, fiecare pe
     a + b * sum_{j=0}^{11} phi^j rv_{t-j}; phi estimat prin NLS (grila + OLS), erori standard prin
     moving block bootstrap (blocuri de 18 luni, ca cele 6 trimestre din lucrare);
  2. Tabelul 3, coloanele 5-7: VRP realizat, varianta viitoare si VIX^2 pe varianta asteptata obiectiv
     sigma2hat_t (HAR in timp real pe randamentele zilnice) si media ponderata a ultimelor 6 valori
     (phi = 0.5), erori standard Newey-West cu 12 laguri;
  3. Figura 2: VAR(1) lunar [sigma2hat, VRP = VIX^2 - sigma2hat, randamentul in exces], ordonare Cholesky cu
     sigma2hat primul; raspunsul la un soc de o abatere standard, benzi de 95% prin bootstrap pe reziduuri.
Graficul: charts/ch12_lm_vrp_irf.pdf/png; cifrele: ch12_lm_case.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_all_charts as G  # noqa: E402  stilul, culorile si incarcatoarele capitolului
from mfm_data import load_close  # noqa: E402

J_LAGS = 12           # rv_t ... rv_{t-11}
BLOCK = 18            # luni (6 trimestre)
B_BOOT = 1000
PHI_WA = 0.5          # ponderile mediei expected variance (Tabelul 3)
H_IRF = 12
PAPER_END = '2020-04-30'
PAPER = dict(phi_vix=0.42, phi_vix_se=0.12,
             t3_rv=(1.53, 0.54, -0.58, 0.46, 0.469), t3_vix=(0.30, 0.12, 0.64, 0.07, 0.790),
             t3_vrp=(-1.26, 0.49, 1.23, 0.46, 0.172))
SEED = 12


def monthly():
    """Month-end VIX^2, monthly realised variance (sum of squared daily log returns, x12, in %^2 a year), the HAR
    regressors at the month end and the monthly excess return of the S&P 500 price index (in %)."""
    px = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    r = np.log(px['sp500']).diff().dropna()
    r2 = r ** 2 * 1e4
    rf = G.ff_rf_daily().reindex(r.index).ffill().fillna(0.0)
    g = pd.DataFrame({'r2': r2, 'ex': np.expm1(r) - rf})
    m = pd.DataFrame({
        'rv': 12 * r2.resample('ME').sum(),
        'n': r2.resample('ME').count(),
        'vix2': px['vix'].resample('ME').last() ** 2,
        'ex': 100 * ((1 + g['ex']).resample('ME').prod() - 1),
    })
    # HAR regressors at the month end, annualised: last day, last 5 days, last 21 days
    d1 = 252 * r2.rolling(1).sum()
    d5 = 252 / 5 * r2.rolling(5).sum()
    d21 = 252 / 21 * r2.rolling(21).sum()
    for k, s in (('har_d', d1), ('har_w', d5), ('har_m', d21)):
        m[k] = s.resample('ME').last()
    m = m[m['n'] >= 15]                       # drop the incomplete last month (September 2026 ends on the 18th)
    return m.drop(columns='n')


def lag_sum(rv, phi):
    return sum(phi ** j * rv.shift(j) for j in range(J_LAGS))


def fit_phi(y, rv, grid=np.linspace(-0.6, 0.98, 317)):
    """NLS of y_t = a + b sum_j phi^j rv_{t-j}: grid over phi, OLS for (a, b)."""
    best = None
    for p in grid:
        x = lag_sum(rv, p)
        d = pd.concat([y, x], axis=1).dropna()
        X = np.column_stack([np.ones(len(d)), d.iloc[:, 1].values])
        beta, res, *_ = np.linalg.lstsq(X, d.iloc[:, 0].values, rcond=None)
        e = d.iloc[:, 0].values - X @ beta
        ssr = float(e @ e)
        if best is None or ssr < best[0]:
            yy = d.iloc[:, 0].values
            best = (ssr, float(p), beta, 1 - ssr / float(((yy - yy.mean()) ** 2).sum()), len(d))
    return dict(phi=best[1], a=float(best[2][0]), b=float(best[2][1]), r2=best[3], n=best[4])


def block_boot_phi(df, ycol, rng, B=B_BOOT):
    """Moving block bootstrap of the rows (y_t, rv_t, ..., rv_{t-11}); phi re-estimated on each sample."""
    rows = pd.concat([df[ycol]] + [df['rv'].shift(j) for j in range(J_LAGS)], axis=1).dropna().values
    n = len(rows)
    grid = np.linspace(-0.6, 0.98, 159)
    W = np.array([[p ** j for j in range(J_LAGS)] for p in grid])          # grid x lags
    out = []
    for _ in range(B):
        starts = rng.integers(0, n - BLOCK + 1, size=int(np.ceil(n / BLOCK)))
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in starts])[:n]
        y, L = rows[idx, 0], rows[idx, 1:]
        X = L @ W.T                                                          # n x grid
        xc = X - X.mean(0); yc = y - y.mean()
        b = (xc * yc[:, None]).sum(0) / (xc ** 2).sum(0)
        ssr = ((yc[:, None] - xc * b) ** 2).sum(0)
        out.append(grid[int(np.argmin(ssr))])
    return float(np.std(out, ddof=1))


def har_realtime(m, burn=24):
    """Objective expected variance sigma2hat_t of next month's rv, from an expanding-window HAR regression
    estimated only on months up to t (real time); the first `burn` months are the burn-in."""
    X = sm.add_constant(m[['har_d', 'har_w', 'har_m']])
    y = m['rv'].shift(-1)
    f = pd.Series(np.nan, index=m.index)
    for i in range(burn, len(m)):
        Xi, yi = X.iloc[:i], y.iloc[:i]          # pairs (s, s+1) with s+1 <= i, i.e. known at month i
        ok = yi.notna()
        b = np.linalg.lstsq(Xi[ok].values, yi[ok].values, rcond=None)[0]
        f.iloc[i] = max(float(X.iloc[i].values @ b), 1.0)
    return f.rename('s2hat')


def wavg(s, phi=PHI_WA, k=6):
    w = np.array([phi ** (j - 1) for j in range(1, k + 1)])
    return sum(w[j - 1] * s.shift(j) for j in range(1, k + 1)) / w.sum()


def table3(m, end=None):
    d = pd.DataFrame({'s2hat': m['s2hat'], 'wa': wavg(m['s2hat']), 'rv_next': m['rv'].shift(-1),
                      'vix2': m['vix2']})
    d['vrp_real'] = d['vix2'] - d['rv_next']
    d = d.loc[:end] if end else d
    out = {}
    for y in ('vrp_real', 'rv_next', 'vix2'):
        z = d[[y, 's2hat', 'wa']].dropna()
        r = sm.OLS(z[y], sm.add_constant(z[['s2hat', 'wa']])).fit(cov_type='HAC', cov_kwds={'maxlags': 12})
        out[y] = dict(b=float(r.params['s2hat']), b_se=float(r.bse['s2hat']), c=float(r.params['wa']),
                      c_se=float(r.bse['wa']), r2=float(r.rsquared), n=int(r.nobs),
                      start=str(z.index[0].date()), end=str(z.index[-1].date()))
    return out


def var_irf(Y, H=H_IRF):
    """VAR(1) with intercept; orthogonalised (Cholesky) responses to a 1-s.d. shock to the first variable."""
    Yv = Y.values
    X = np.column_stack([np.ones(len(Yv) - 1), Yv[:-1]])
    B = np.linalg.lstsq(X, Yv[1:], rcond=None)[0]
    E = Yv[1:] - X @ B
    S = E.T @ E / (len(E) - X.shape[1])
    P = np.linalg.cholesky(S)
    A = B[1:].T
    resp = [P[:, 0]]
    for _ in range(H):
        resp.append(A @ resp[-1])
    return np.array(resp), B, E


def irf_boot(Y, rng, B_=B_BOOT, H=H_IRF):
    base, Bc, E = var_irf(Y, H)
    Yv = Y.values
    k = Yv.shape[1]
    draws = []
    for _ in range(B_):
        e = E[rng.integers(0, len(E), size=len(E))]
        sim = np.zeros_like(Yv); sim[0] = Yv[0]
        for t in range(1, len(Yv)):
            sim[t] = Bc[0] + Bc[1:].T @ sim[t - 1] + e[t - 1]
        draws.append(var_irf(pd.DataFrame(sim, columns=Y.columns), H)[0])
    draws = np.array(draws)
    return base, np.percentile(draws, 2.5, axis=0), np.percentile(draws, 97.5, axis=0)


def fig(irf, lo, hi, cols, phis, span):
    """Left: responses to a 1-s.d. shock to expected variance (VAR on the course data);
    right: the fitted lag weights phi^j of VIX^2 and of next month's realised variance."""
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.3), gridspec_kw={'width_ratios': [1.45, 1]})
    ax = axes[0]
    h = np.arange(irf.shape[0])
    iv, ivrp = cols.index('s2hat'), cols.index('vrp')
    ax.axhline(0, color=G.Navy, lw=0.6)
    ax.fill_between(h, lo[:, ivrp], hi[:, ivrp], color=G.IDAred, alpha=0.15, lw=0)
    ax.plot(h, irf[:, iv], color=G.MainBlue, lw=1.3, marker='o', ms=2.5)
    ax.plot(h, irf[:, iv] + irf[:, ivrp], color=G.Teal, lw=1.1, ls='--')
    ax.plot(h, irf[:, ivrp], color=G.IDAred, lw=1.3, marker='o', ms=2.5)
    ax.set_xlabel('Months after the shock'); ax.set_ylabel('Response (annualised %$^2$)')
    ax.set_xticks(range(0, H_IRF + 1, 2))
    ax.set_title(f'Response to a 1-s.d. shock to expected variance, VAR(1), {span[0]}-{span[1]}', fontsize=9.5, loc='left')
    ax = axes[1]
    j = np.arange(J_LAGS)
    w = 0.38
    ax.bar(j - w / 2, phis['vix'] ** j, w * 0.95, color=G.Purple)
    ax.bar(j + w / 2, np.where(j == 0, 1.0, phis['rv'] ** j), w * 0.95, color=G.Forest)
    ax.axhline(0, color=G.Navy, lw=0.6)
    ax.set_xlabel('Lag $j$ of monthly realised variance'); ax.set_ylabel('Weight $\\phi^j$')
    ax.set_xticks(j[::2])
    ax.set_title(f'Weight on past realised variance, {span[2]}-{span[1]}', fontsize=9.5, loc='left')
    handles = [Line2D([], [], color=G.MainBlue, lw=1.3, marker='o', ms=2.5, label='Expected variance (real-time HAR)'),
               Line2D([], [], color=G.Teal, lw=1.1, ls='--', label='VIX$^2$ = expected variance + VRP'),
               Line2D([], [], color=G.IDAred, lw=1.3, marker='o', ms=2.5, label='VRP = VIX$^2$ $-$ expected variance'),
               Patch(color=G.IDAred, alpha=0.15, label='VRP: 95% bootstrap band'),
               Patch(color=G.Purple, label=f'VIX$^2$: $\\hat\\phi$ = {phis["vix"]:.2f}'),
               Patch(color=G.Forest, label=f'Next month realised variance: $\\hat\\phi$ = {phis["rv"]:.2f}')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=7.6)
    plt.tight_layout()
    G.save_fig('ch12_lm_vrp_irf')


def main():
    rng = np.random.default_rng(SEED)
    m = monthly()
    m['s2hat'] = har_realtime(m)
    m['vrp'] = m['vix2'] - m['s2hat']
    res = dict(start=str(m.index[0].date()), end=str(m.index[-1].date()), n=int(len(m)), paper=PAPER)
    # 1. phi (eq. 4), paper sample and full sample
    for tag, end in (('paper', PAPER_END), ('full', None)):
        mm = m.loc[:end]
        fv = fit_phi(mm['vix2'], mm['rv'])
        fr = fit_phi(mm['rv'].shift(-1), mm['rv'])
        fv['se'] = block_boot_phi(mm.assign(y=mm['vix2']), 'y', rng)
        fr['se'] = block_boot_phi(mm.assign(y=mm['rv'].shift(-1)), 'y', rng)
        res['phi_' + tag] = dict(vix=fv, rv=fr)
    # 2. Table 3 analogue
    res['t3_paper'] = table3(m, PAPER_END)
    res['t3_full'] = table3(m)
    # 3. VAR impulse responses, full sample from the first month with sigma2hat
    Y = m[['s2hat', 'vrp', 'ex']].dropna()
    irf, lo, hi = irf_boot(Y, rng)
    cols = list(Y.columns)
    iv, ivrp, ie = (cols.index(c) for c in ('s2hat', 'vrp', 'ex'))
    neg = [int(k) for k in range(H_IRF + 1) if hi[k, ivrp] < 0]
    res['irf'] = dict(start=str(Y.index[0].date()), end=str(Y.index[-1].date()), n=int(len(Y)),
                      s2hat=irf[:, iv].tolist(), vrp=irf[:, ivrp].tolist(), vrp_lo=lo[:, ivrp].tolist(),
                      vrp_hi=hi[:, ivrp].tolist(), ex=irf[:, ie].tolist(), ex_lo=lo[:, ie].tolist(),
                      ex_hi=hi[:, ie].tolist(), vrp_sig_neg=neg,
                      vrp_first_pos=next((int(k) for k in range(H_IRF + 1) if irf[k, ivrp] > 0), None),
                      vrp_min=float(irf[:, ivrp].min()), vrp_min_h=int(np.argmin(irf[:, ivrp])),
                      shock=float(irf[0, iv]))
    irf_p, lo_p, hi_p = irf_boot(m.loc[:PAPER_END, ['s2hat', 'vrp', 'ex']].dropna(), rng)
    res['irf_paper'] = dict(vrp=irf_p[:, 1].tolist(), vrp_lo=lo_p[:, 1].tolist(), vrp_hi=hi_p[:, 1].tolist(),
                            s2hat=irf_p[:, 0].tolist())
    # descriptive: mean VRP, share of negative months
    v = m['vrp'].dropna()
    res['vrp_desc'] = dict(mean=float(v.mean()), share_neg=float((v < 0).mean()), n=int(len(v)),
                           corr_s2_vix2=float(m[['s2hat', 'vix2']].dropna().corr().iloc[0, 1]))
    fig(irf, lo, hi, cols, dict(vix=res['phi_full']['vix']['phi'], rv=res['phi_full']['rv']['phi']),
        (res['irf']['start'][:4], res['end'][:4], res['start'][:4]))
    # series for the interactive page
    res['series'] = dict(dates=[str(d.date()) for d in m.index], rv=m['rv'].round(3).tolist(),
                         vix2=m['vix2'].round(3).tolist(),
                         s2hat=[None if np.isnan(x) else round(float(x), 3) for x in m['s2hat']],
                         ex=m['ex'].round(4).tolist())
    with open(os.path.join(HERE, 'ch12_lm_case.json'), 'w') as f:
        json.dump(G.jsonable(res), f, indent=1)
    print(json.dumps({k: v for k, v in G.jsonable(res).items() if k != 'series'}, indent=1)[:6000])


def paired_phi_diff(mm, rng, B=B_BOOT):
    """Paired moving block bootstrap (blocks of 18 months) of phi_VIX - phi_RV: the same resampled months enter both
    regressions (VIX^2_t and rv_{t+1} on the lagged realised variances), so the difference has a joint distribution."""
    rows = pd.concat([mm['vix2'], mm['rv'].shift(-1)] + [mm['rv'].shift(j) for j in range(J_LAGS)], axis=1).dropna().values
    n = len(rows)
    grid = np.linspace(-0.6, 0.98, 317)     # the grid of fit_phi
    W = np.array([[p ** j for j in range(J_LAGS)] for p in grid])

    def phi_of(y, L):
        X = L @ W.T
        xc = X - X.mean(0); yc = y - y.mean()
        b = (xc * yc[:, None]).sum(0) / (xc ** 2).sum(0)
        return grid[int(np.argmin(((yc[:, None] - xc * b) ** 2).sum(0)))]
    est = phi_of(rows[:, 0], rows[:, 2:]) - phi_of(rows[:, 1], rows[:, 2:])
    out = []
    for _ in range(B):
        starts = rng.integers(0, n - BLOCK + 1, size=int(np.ceil(n / BLOCK)))
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in starts])[:n]
        L = rows[idx, 2:]
        out.append(phi_of(rows[idx, 0], L) - phi_of(rows[idx, 1], L))
    out = np.array(out)
    return dict(n=int(n), diff=float(est), se=float(out.std(ddof=1)), lo=float(np.quantile(out, 0.025)),
                hi=float(np.quantile(out, 0.975)), share_le0=float((out <= 0).mean()))


def var_diagnostics(Y, rng):
    """VAR(1) checks: largest eigenvalue modulus of the slope matrix, ARCH-LM test (12 lags) on each residual,
    and the VRP response to the expected-variance shock when expected variance is ordered last instead of first."""
    from statsmodels.stats.diagnostic import het_arch
    irf, Bc, E = var_irf(Y)
    A = Bc[1:].T
    eig = float(np.max(np.abs(np.linalg.eigvals(A))))
    arch = {c: float(het_arch(E[:, i], nlags=12)[1]) for i, c in enumerate(Y.columns)}
    # alternative ordering: [vrp, ex, s2hat]; response to the s2hat shock (last Cholesky column)
    Yv = Y.values
    X = np.column_stack([np.ones(len(Yv) - 1), Yv[:-1]])
    S = E.T @ E / (len(E) - X.shape[1])
    order = [1, 2, 0]
    P = np.linalg.cholesky(S[np.ix_(order, order)])
    shock = np.zeros(3); shock[order] = P[:, 2]
    resp = [shock]
    for _ in range(H_IRF):
        resp.append(A @ resp[-1])
    resp = np.array(resp)
    return dict(max_eig=eig, arch_p=arch, alt_vrp=resp[:, 1].tolist(), alt_s2hat=resp[:, 0].tolist())


def diag():
    """Inference checks for the case study: paired bootstrap of the phi difference (paper sample and full sample)
    and VAR diagnostics; saved under 'diag' in ch12_lm_case.json, other numbers unchanged."""
    rng = np.random.default_rng(SEED + 1)
    m = monthly()
    m['s2hat'] = har_realtime(m)
    m['vrp'] = m['vix2'] - m['s2hat']
    with open(os.path.join(HERE, 'ch12_lm_case.json')) as f:
        res = json.load(f)
    Y = m[['s2hat', 'vrp', 'ex']].dropna()
    res['diag'] = dict(phi_diff_paper=paired_phi_diff(m.loc[:PAPER_END], rng), phi_diff_full=paired_phi_diff(m, rng),
                       var=var_diagnostics(Y, rng), irf_n=int(len(Y)))
    with open(os.path.join(HERE, 'ch12_lm_case.json'), 'w') as f:
        json.dump(G.jsonable(res), f, indent=1)
    print(json.dumps(G.jsonable(res['diag']), indent=1))


if __name__ == '__main__':
    if 'diag' in sys.argv[1:]:
        diag()
    else:
        main()

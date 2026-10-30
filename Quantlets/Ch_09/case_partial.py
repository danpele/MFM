"""
case_partial.py -- Capitolul 9 (MFM), al doilea studiu de caz: varianțe realizate parțiale
=========================================================================================
Bollerslev, Medeiros, Patton & Quaedvlieg (2022), "From zero to hero: Realized partial (co)variances",
Journal of Econometrics 231(2), 348-360, doi:10.1016/j.jeconom.2021.04.013.

Varianța parțială a zilei t pentru intervalul (c_{g-1}, c_g] al randamentelor standardizate z = r / sqrt(RV_t):
    PV_t^(g) = sum_k r_{t,k}^2 1{c_{g-1} < z_{t,k} <= c_g},   sum_g PV_t^(g) = RV_t.
Pragurile c_g sînt cuantile q_g ale lui z din fereastra de estimare (fără informație din ziua prognozată).
Modele (MCO pe niveluri, ca în lucrare; doar lagul zilnic este descompus):
    RV-HAR   RV_{t+1} = b0 + b_d RV_t + b_w RV_t^(w) + b_m RV_t^(m)
    SV-HAR   lagul zilnic -> semivarianțele RS^-_t, RS^+_t (prag 0)
    PV(2)    lagul zilnic -> două varianțe parțiale, prag la cuantila q (q = 0.05, 0.10, ..., 0.95)
    PV(3)    lagul zilnic -> trei varianțe parțiale, cuantilele (q1, q2) alese prin validare încrucișată în 5 blocuri
             (MSE), pe fereastra de estimare, la fiecare 21 de zile de prognoză
Prognoze pentru ziua următoare, fereastră extinsă, reestimare zilnică (ca prognozele HAR din capitol):
SPY de la 2022-01-03 (ținta: RV intraday 09:30-16:00, ca în lucrare), Bitcoin de la 2025-03-01 (RV pe 24 de ore UTC,
laguri pe zile calendaristice). Filtru: o prognoză sub cea mai mică RV din fereastra de estimare este înlocuită cu acea
valoare (insanity filter). Pierderi: MSE și QLIKE; teste Diebold-Mariano cu erori Newey-West (rv_tools.dm_test).

Rezultate: ch9_partial.json, prognozele zilnice în ch9_partial_forecasts_{spy,btc}.csv; grafic: charts/ch9_partial_q.pdf/png.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import mfm_data as M      # noqa: E402
import rv_tools as T      # noqa: E402

try:
    import slide_fit      # noqa: F401  charts drawn at the size they have on the slides
except Exception:         # stand-alone use (Colab): default size
    pass

plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.facecolor': 'none',
                     'savefig.transparent': True, 'axes.grid': False, 'font.family': 'sans-serif',
                     'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'], 'font.size': 9,
                     'axes.labelsize': 10, 'axes.titlesize': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.6, 'lines.linewidth': 1.1,
                     'legend.facecolor': 'none', 'legend.framealpha': 0, 'legend.fontsize': 8})
MainBlue, Amber, Black, IDAred = '#1A3A6E', '#B5853F', '#000000', '#CD0000'

CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
QS = np.round(np.arange(0.05, 0.951, 0.05), 2)
OOS = {'spy': '2022-01-03', 'btc': '2025-03-01'}
REFIT_CV = 21
MIN_OBS = 100


def load():
    """Intraday returns (%) and realised variance of SPY (regular session) and Bitcoin (24 h UTC)."""
    out = {}
    for k, P in (('spy', M.spy_intraday()), ('btc', M.btc_intraday())):
        R = M.intraday_returns(P)
        v = T.rv(R)
        Z = R.div(np.sqrt(v), axis=0)
        out[k] = {'R2': (R ** 2).values, 'Z': Z.values, 'v': v, 'cal': k == 'btc'}
    return out


def daily_lag(x, index, cal):
    """Value of the previous trading day (SPY) or of the previous calendar day (Bitcoin)."""
    s = pd.Series(x, index=index)
    return (s.asfreq('D').shift(1).reindex(index) if cal else s.shift(1)).values


def partials(d, cuts):
    """Partial variances for the standardised thresholds `cuts` (sorted): G = len(cuts) + 1 columns."""
    R2, Z = d['R2'], d['Z']
    edges = [-np.inf] + list(cuts) + [np.inf]
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (Z > lo) & (Z <= hi)
        out.append(np.where(m, R2, 0.0).sum(axis=1))
    return np.column_stack(out)


def semis(d):
    R2, Z = d['R2'], d['Z']
    return np.column_stack([np.where(Z < 0, R2, 0.0).sum(axis=1), np.where(Z > 0, R2, 0.0).sum(axis=1)])


def design(d, daily):
    """Regressors: intercept, the daily components (lagged one day), weekly and monthly RV."""
    v = d['v']
    if 'H' not in d:
        d['H'] = T.har_design(v, calendar=d['cal'])
    H = d['H']
    lag = np.column_stack([daily_lag(daily[:, j], v.index, d['cal']) for j in range(daily.shape[1])])
    return np.column_stack([np.ones(len(v)), lag, H['w'].values, H['m'].values])


def fit_predict(X, y, tr, t):
    b, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
    return float(X[t] @ b)


def cv_mse(X, y, tr, k=5):
    """5-fold cross-validation on contiguous blocks of the estimation window (MSE)."""
    folds = np.array_split(tr, k)
    e = []
    for f in folds:
        rest = np.setdiff1d(tr, f)
        b, *_ = np.linalg.lstsq(X[rest], y[rest], rcond=None)
        e.append(np.mean((y[f] - X[f] @ b) ** 2))
    return float(np.mean(e))


def quantiles(d, tr_days, qs):
    z = d['Z'][tr_days].ravel()
    return np.quantile(z[~np.isnan(z)], qs)


def forecasts(d, start, window=None):
    """Expanding window (window=None) or a rolling window of fixed length `window` (Giacomini-White setting: the
    estimation error does not vanish, so the DM statistic on these losses keeps its N(0,1) reference also for the
    nested comparisons RV-HAR inside SV-HAR and PV(3)-HAR); thresholds and the CV selection use the same window."""
    v = d['v']
    y = v.values
    idx = v.index
    X_rv = design(d, y[:, None])
    X_sv = design(d, semis(d))
    ok_base = ~np.isnan(X_rv).any(axis=1) & ~np.isnan(y)
    days = np.where((idx >= pd.Timestamp(start)) & ok_base)[0]
    pairs = [(a, b) for a, b in itertools.combinations(range(len(QS)), 2)]
    F = {'RV-HAR': {}, 'SV-HAR': {}, 'PV(3)': {}}
    F2 = {q: {} for q in QS}
    sel = []
    best = None
    for i, t in enumerate(days):
        tr = np.where(ok_base[:t])[0]
        if window is not None:
            tr = tr[-window:]
        if len(tr) < MIN_OBS:
            continue
        floor = float(np.min(y[tr]))
        F['RV-HAR'][idx[t]] = max(fit_predict(X_rv, y, tr, t), floor)
        F['SV-HAR'][idx[t]] = max(fit_predict(X_sv, y, tr, t), floor)
        # thresholds from the standardised returns of the estimation window (days up to t-1)
        cq = quantiles(d, np.arange(t) if window is None else np.arange(tr[0], t), QS)
        for j, q in enumerate(QS):
            X = design(d, partials(d, [cq[j]]))
            F2[q][idx[t]] = max(fit_predict(X, y, tr, t), floor)
        if best is None or i % REFIT_CV == 0:
            scores = []
            for a, b in pairs:
                X = design(d, partials(d, [cq[a], cq[b]]))
                scores.append(cv_mse(X, y, tr))
            best = pairs[int(np.argmin(scores))]
            sel.append({'date': str(idx[t].date()), 'q1': float(QS[best[0]]), 'q2': float(QS[best[1]])})
        X3 = design(d, partials(d, [cq[best[0]], cq[best[1]]]))
        F['PV(3)'][idx[t]] = max(fit_predict(X3, y, tr, t), floor)
    F = pd.DataFrame(F)
    F2 = pd.DataFrame({f'{q:.2f}': pd.Series(F2[q]) for q in QS})
    return F, F2, v.reindex(F.index), sel


def full_sample_semis(d):
    """SV-HAR on the full sample: coefficients of RS^- and RS^+ with Newey-West standard errors."""
    X = design(d, semis(d))
    y = d['v'].values
    ok = ~np.isnan(X).any(axis=1)
    res = T.ols_nw(y[ok], X[ok][:, 1:])
    return {'b_neg': float(res['b'][1]), 'se_neg': float(res['se'][1]), 'b_pos': float(res['b'][2]),
            'se_pos': float(res['se'][2]), 'T': int(res['T'])}


def evaluate(F, F2, y):
    out = {'T': int(len(F)), 'start': str(F.index[0].date()), 'end': str(F.index[-1].date())}
    L = {m: {'mse': T.mse(y, F[m]), 'qlike': T.qlike(y, F[m])} for m in F}
    for m in F:
        out[m] = {'mse': float(L[m]['mse'].mean()), 'qlike': float(L[m]['qlike'].mean())}
        for loss in ('mse', 'qlike'):
            out[m][f'{loss}_ratio'] = out[m][loss] / float(L['RV-HAR'][loss].mean())
        if m != 'RV-HAR':
            for loss in ('mse', 'qlike'):
                dm = T.dm_test(L[m][loss], L['RV-HAR'][loss])
                out[m][f'dm_rv_{loss}_t'], out[m][f'dm_rv_{loss}_p'] = dm['t'], dm['p']
        if m == 'PV(3)':
            for loss in ('mse', 'qlike'):
                dm = T.dm_test(L[m][loss], L['SV-HAR'][loss])
                out[m][f'dm_sv_{loss}_t'], out[m][f'dm_sv_{loss}_p'] = dm['t'], dm['p']
    curve = {'q': [float(q) for q in QS], 'mse_ratio': [], 'qlike_ratio': []}
    for c in F2:
        f = F2[c].reindex(F.index)
        curve['mse_ratio'].append(float(T.mse(y, f).mean() / L['RV-HAR']['mse'].mean()))
        curve['qlike_ratio'].append(float(T.qlike(y, f).mean() / L['RV-HAR']['qlike'].mean()))
    out['curve'] = curve
    j = int(np.argmin(curve['mse_ratio']))
    out['best_q_mse'], out['best_mse_ratio'] = curve['q'][j], curve['mse_ratio'][j]
    j = int(np.argmin(curve['qlike_ratio']))
    out['best_q_qlike'], out['best_qlike_ratio'] = curve['q'][j], curve['qlike_ratio'][j]
    return out


def fig_partial(res, name='ch9_partial_q'):
    """Out-of-sample loss of PV(2)-HAR relative to RV-HAR, as a function of the threshold quantile q."""
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.2), sharex=True)
    for ax, loss, title in ((axes[0], 'mse', 'MSE relative to RV-HAR'), (axes[1], 'qlike', 'QLIKE relative to RV-HAR')):
        top = 1.15
        for k, col, lab in (('spy', MainBlue, 'SPY'), ('btc', Amber, 'Bitcoin')):
            r = res[k]
            q, y = np.array(r['curve']['q']), np.array(r['curve'][f'{loss}_ratio'])
            ax.plot(q, np.minimum(y, top), 'o-', ms=3, color=col,
                    label=f'{lab}: PV(2)-HAR, one threshold at quantile q')
            for qq, yy in zip(q[y > top], y[y > top]):      # off-scale point: drawn at the top edge, value written
                ax.annotate(f'{lab}, q = {qq:.2f}: {yy:.2f}', (qq, top), xytext=(-4, -2), textcoords='offset points',
                            ha='right', va='top', fontsize=7.5, color=col)
            ax.axhline(r['SV-HAR'][f'{loss}_ratio'], color=col, ls='--', lw=0.9,
                       label=f'{lab}: SV-HAR (threshold at zero)')
        ax.axhline(1.0, color=Black, lw=0.7, ls=':', label='RV-HAR = 1')
        ax.set_ylim(top=top + 0.01)
        ax.set_xlabel('Threshold: quantile q of standardised returns')
        ax.set_title(title, loc='left')
    axes[0].set_ylabel('Loss ratio')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False)
    plt.tight_layout(rect=(0, 0.1, 1, 1))
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print('   saved', name)


def run():
    D = load()
    res = {}
    for k in ('spy', 'btc'):
        F, F2, y, sel = forecasts(D[k], OOS[k])
        r = evaluate(F, F2, y)
        # sensitivity: the 10 days with the largest realised variance removed from the evaluation sample
        keep = y.rank(ascending=False, method='first') > 10
        sub = evaluate(F[keep], F2[keep], y[keep])
        r['drop10'] = {m: {'mse_ratio': sub[m]['mse_ratio'], 'qlike_ratio': sub[m]['qlike_ratio']}
                       for m in ('SV-HAR', 'PV(3)')}
        r['drop10']['best_q_mse'], r['drop10']['best_mse_ratio'] = sub['best_q_mse'], sub['best_mse_ratio']
        e = T.mse(y, F['RV-HAR'])
        r['mse_top10_share'] = float(e[~keep].sum() / e.sum())     # share of the squared error of RV-HAR on those 10 days
        F2.columns = [f'PV2_{c}' for c in F2.columns]
        pd.concat([y.rename('rv'), F, F2.reindex(F.index)], axis=1).to_csv(
            os.path.join(HERE, f'ch9_partial_forecasts_{k}.csv'), float_format='%.6g')
        r['selected'] = sel
        r['q1_mean'] = float(np.mean([s['q1'] for s in sel]))
        r['q2_mean'] = float(np.mean([s['q2'] for s in sel]))
        # Giacomini-White: the same forecasts from a rolling window of fixed length (the estimation sample available
        # at the first forecast origin); unconditional test = DM on these losses, valid for nested models
        v = D[k]['v']
        X0 = design(D[k], v.values[:, None])
        okb = ~np.isnan(X0).any(axis=1) & ~np.isnan(v.values)
        W = int(okb[:np.searchsorted(v.index, pd.Timestamp(OOS[k]))].sum())
        Fr, _, yr, _ = forecasts(D[k], OOS[k], window=W)
        Lr = {m: {'mse': T.mse(yr, Fr[m]), 'qlike': T.qlike(yr, Fr[m])} for m in Fr}
        gw = {'window': W, 'T': int(len(Fr))}
        for m, base in (('SV-HAR', 'RV-HAR'), ('PV(3)', 'RV-HAR'), ('PV(3)', 'SV-HAR')):
            for loss in ('mse', 'qlike'):
                dm = T.dm_test(Lr[m][loss], Lr[base][loss])
                key = f'{m}_vs_{base}_{loss}'
                gw[key] = {'t': dm['t'], 'p': dm['p'], 'ratio': float(Lr[m][loss].mean() / Lr[base][loss].mean())}
        r['gw'] = gw
        r['semis_full'] = full_sample_semis(D[k])
        z = D[k]['Z'].ravel()
        z = z[~np.isnan(z)]
        r['zero_share'] = float(np.mean(z == 0))
        r['days'] = int(D[k]['v'].notna().sum())
        r['first_day'] = str(D[k]['v'].index[0].date())
        r['last_day'] = str(D[k]['v'].index[-1].date())
        res[k] = r
        print(k, {m: (round(r[m]['mse_ratio'], 4), round(r[m]['qlike_ratio'], 4)) for m in ('SV-HAR', 'PV(3)')},
              'best q mse', r['best_q_mse'], round(r['best_mse_ratio'], 4), 'q1/q2', r['q1_mean'], r['q2_mean'])
    with open(os.path.join(HERE, 'ch9_partial.json'), 'w') as f:
        json.dump(res, f, indent=1)
    fig_partial(res)
    return res


if __name__ == '__main__':
    run()

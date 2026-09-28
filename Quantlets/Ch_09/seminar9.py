"""
seminar9.py -- calculele Seminarului 9 (MFM): volatilitate realizata
====================================================================
Partea A: exercitii pas cu pas (RV, BV, zgomot, TSRV, HAR, QLIKE/MSE, DM).
Partea B: SPY si Bitcoin, bare de 5 minute: salturi, frecventa de esantionare, randamente standardizate,
HAR in esantion, prognoze pe 5 zile, HAR-CJ, asprimea volatilitatii.
Partea C: este volatilitatea Bitcoin mai previzibila decat a SPY? (analiza de referinta pentru profesor)
Cifrele sunt salvate in sem9_results.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_data as M                                                           # noqa: E402
import rv_tools as T                                                           # noqa: E402
from generate_all_charts import (plt, MainBlue, IDAred, Forest, Amber, Orange, Purple, Teal, Gray, LightGray,  # noqa: E402
                                 save_fig, legend_outside_bottom, fig_legend_bottom, jsonable, ann, rough_H,
                                 P_SPY, R_SPY, ON, OC, RV_SPY, RVT_SPY, P_BTC, R_BTC, RV_BTC, D_SPY, D_BTC, SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
B_BOOT = 2000
C_START = '2025-03-01'


# =============================================================================
# PARTEA A
# =============================================================================
A1_R = np.array([0.08, -0.15, 0.03, 0.10, -0.04, 0.12])


def a1_rv_bv(r=A1_R):
    """RV, BV si ponderea variatiei nediscutate de BV pentru sase randamente de 5 minute (%)."""
    M_ = len(r)
    v = np.sum(r ** 2)
    s = np.sum(np.abs(r[1:]) * np.abs(r[:-1]))
    b = (np.pi / 2) * M_ / (M_ - 1) * s
    sparse = np.sum(np.array([r[:3].sum(), r[3:].sum()]) ** 2)
    return {'rv': v, 's': s, 'bv': b, 'ratio': (v - b) / v, 'sparse15': sparse,
            'vol_ann': np.sqrt(252 * v * 78 / M_), 'sq': list(r ** 2), 'prod': list(np.abs(r[1:]) * np.abs(r[:-1]))}


def a2_jump(r=A1_R):
    """Aceleasi randamente, dar ultimul este un salt de -0,90%: RV, BV, statistica raportului."""
    x = r.copy()
    x[-1] = -0.90
    out = a1_rv_bv(x)
    M_ = len(x)
    a43 = np.abs(x) ** (4 / 3)
    tq = M_ * T.MU43 ** -3 * M_ / (M_ - 2) * np.sum(a43[2:] * a43[1:-1] * a43[:-2])
    theta = T.MU1 ** -4 + 2 * T.MU1 ** -2 - 5
    z = out['ratio'] / np.sqrt(theta / M_ * max(1, tq / out['bv'] ** 2))
    out.update({'tq': tq, 'theta': theta, 'z': z, 'crit': stats.norm.ppf(0.999), 'jump_part': out['rv'] - out['bv']})
    return out


def a3_noise(iv=1.0, omega=0.01):
    """Bias-ul zgomotului: E[RV] = IV + 2 n omega^2; frecventa optima n* = (IQ / (4 omega^4))^(1/3) cu IQ = IV^2."""
    rows = {n: {'bias': 2 * n * omega ** 2, 'erv': iv + 2 * n * omega ** 2} for n in (78, 390, 23400)}
    nstar = (iv ** 2 / (4 * omega ** 4)) ** (1 / 3)
    return {'rows': rows, 'nstar': nstar, 'secs': 23400 / nstar, 'omega2': omega ** 2}


def a4_tsrv(rv_all=1.70, rv_avg=1.10, n=390, K=5, iv=1.0):
    """Actiune BVB mai putin lichida: omega = 0,03%; TSRV din RV pe 1 minut si media pe 5 grile de 5 minute."""
    om = 0.03
    nbar = (n - K + 1) / K
    ts = rv_avg - nbar / n * rv_all
    return {'bias5': 2 * 78 * om ** 2, 'bias1': 2 * n * om ** 2, 'nstar': (iv ** 2 / (4 * om ** 4)) ** (1 / 3),
            'secs': 23400 / (iv ** 2 / (4 * om ** 4)) ** (1 / 3), 'nbar': nbar, 'ratio': nbar / n, 'tsrv': ts,
            'tsrv_adj': ts / (1 - nbar / n), 'omega2_hat': (rv_all - iv) / (2 * n)}


def a5_har(b=(-0.08, 0.36, 0.34, 0.17), d=np.log(2.0), w=np.log(1.2), m=np.log(0.9)):
    """Prognoza log-HAR pentru maine; ponderi implicite pe intarzieri; persistenta."""
    lf = b[0] + b[1] * d + b[2] * w + b[3] * m
    return {'lf': lf, 'f': np.exp(lf), 'w1': b[1] + b[2] / 5 + b[3] / 22, 'w2': b[2] / 5 + b[3] / 22, 'w6': b[3] / 22,
            'pers': b[1] + b[2] + b[3], 'mean': np.exp(b[0] / (1 - sum(b[1:]))), 'd': d, 'w': w, 'm': m}


def a6_losses():
    """QLIKE si MSE pentru doua prognoze pe trei zile."""
    v = np.array([0.8, 1.5, 0.6])
    fa = np.array([1.0, 1.0, 1.0])
    fb = np.array([0.6, 1.6, 0.4])
    out = {}
    for k, f in [('A', fa), ('B', fb)]:
        q = v / f - np.log(v / f) - 1
        e = (v - f) ** 2
        out[k] = {'q': list(q), 'qm': q.mean(), 'e': list(e), 'em': e.mean()}
    # prognoza de 2 ori prea mica vs de 2 ori prea mare (v = 1)
    out['under'] = 1 / 0.5 - np.log(1 / 0.5) - 1
    out['over'] = 1 / 2.0 - np.log(1 / 2.0) - 1
    out['under_mse'] = (1 - 0.5) ** 2
    out['over_mse'] = (1 - 2.0) ** 2
    return out


def a7_har2(b=(-0.08, 0.36, 0.34, 0.17), days=(2.0, 1.6, 1.3, 1.1, 1.0), m=0.9):
    """Prognoza log-HAR pe doua zile, iterativ: prognoza de maine devine valoare 'observata' pentru poimaine."""
    L = np.log(np.array(days))           # log RV pe ultimele 5 zile (azi primul)
    lm = np.log(m)
    f1 = b[0] + b[1] * L[0] + b[2] * L.mean() + b[3] * lm
    L2 = np.r_[f1, L[:4]]
    lm2 = (21 * lm + f1) / 22            # aproximatie: media lunara actualizata cu noua valoare
    f2 = b[0] + b[1] * f1 + b[2] * L2.mean() + b[3] * lm2
    return {'lw': L.mean(), 'f1': f1, 'F1': np.exp(f1), 'lw2': L2.mean(), 'lm2': lm2, 'f2': f2, 'F2': np.exp(f2), 'lm': lm}


def a8_dm(mean_d=-0.0327, se=0.0142, b=0.70, se_b=0.24, a=0.24, se_a=0.23):
    """Statistica DM din media diferentelor de pierdere si eroarea ei HAC; testele MZ separate pentru a si b."""
    t = mean_d / se
    return {'t': t, 'p': 2 * stats.norm.sf(abs(t)), 'tb': (b - 1) / se_b, 'ta': a / se_a,
            'pb': 2 * stats.norm.sf(abs((b - 1) / se_b)), 'pa': 2 * stats.norm.sf(abs(a / se_a))}


# =============================================================================
# PARTEA B
# =============================================================================
def b1_spy_jumps():
    """Testul de salturi pe SPY la trei niveluri; ora celui mai mare randament in zilele cu salt."""
    j = T.jump_test(R_SPY)
    out = {'N': int(len(j))}
    for a, tag in [(0.05, '5'), (0.01, '1'), (0.001, '0_1')]:
        k = int((j['z'] > stats.norm.ppf(1 - a)).sum())
        out[f'n{tag}'] = k
        out[f'share{tag}'] = k / len(j)
        out[f'exp{tag}'] = a * len(j)
    jd = j[j['jump']].index
    slot = R_SPY.loc[jd].abs().idxmax(axis=1).astype(int)          # coloana 1..78 = intervalul care se termina la 09:30 + 5*col
    end = pd.Timestamp('2000-01-01 09:30') + pd.to_timedelta(5 * slot.values, unit='min')
    hours = pd.Series([t.strftime('%H:%M') for t in end], index=jd)
    at10 = float(np.mean([(t.hour == 10 and t.minute <= 5) for t in end]))
    at14 = float(np.mean([(t.hour == 14 and t.minute <= 5) or (t.hour == 14 and t.minute == 0) for t in end]))
    fig, ax = plt.subplots(figsize=(8.2, 3.0))
    mins = np.array([(t.hour - 9) * 60 + t.minute - 30 for t in end])
    ax.hist(mins, bins=np.arange(0, 391, 15), color=MainBlue, label='Days with a significant jump: time of the largest 5-minute return')
    ax.set_xticks([0, 30, 90, 150, 210, 270, 330, 390])
    ax.set_xticklabels(['09:30', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'])
    ax.set_ylabel('Number of days')
    legend_outside_bottom(ax, ncol=1, y=-0.15)
    save_fig('ch9_sem_jump_times')
    top = j.sort_values('z', ascending=False).head(3)
    out.update({'at10': at10, 'at14': at14, 'n_jump': int(len(jd)),
                'top': [{'date': str(d.date()), 'z': float(r['z']), 'jshare': float(r['J'] / r['rv']),
                         'time': hours[d]} for d, r in top.iterrows()],
                'jshare': float(j['J'].sum() / j['rv'].sum()), 'z_mean': float(j['z'].mean()), 'z_sd': float(j['z'].std())})
    return out


def b2_btc_jumps():
    """Testul de salturi pe Bitcoin; zilele de weekend vs zilele lucratoare."""
    j = T.jump_test(R_BTC)
    wk = j.index.dayofweek >= 5
    return {'N': int(len(j)), 'n': int(j['jump'].sum()), 'share': float(j['jump'].mean()),
            'share_we': float(j.loc[wk, 'jump'].mean()), 'share_wd': float(j.loc[~wk, 'jump'].mean()),
            'jshare': float(j['J'].sum() / j['rv'].sum()), 'exp': 0.001 * len(j),
            'p_binom': float(stats.binomtest(int(j['jump'].sum()), len(j), 0.001, alternative='greater').pvalue),
            'bv_rv_we': float((j.loc[wk, 'bv'] / j.loc[wk, 'rv']).mean()),
            'bv_rv_wd': float((j.loc[~wk, 'bv'] / j.loc[~wk, 'rv']).mean()),
            'z_zero_share': float((R_BTC == 0).mean().mean())}


def b3_frequency():
    """SPY: RV la 5, 15, 30 si 65 de minute; bootstrap pe blocuri pentru raportul mediilor; putere predictiva."""
    base = RV_SPY
    out = {}
    fig, ax = plt.subplots(figsize=(8.2, 3.0))
    for k, col in [(1, MainBlue), (3, Forest), (6, Amber), (13, IDAred)]:
        v = T.sparse_rv(P_SPY, k)
        vs = T.subsampled_rv(P_SPY, k)
        ratio = v.mean() / base.mean()
        boot = T.block_bootstrap(np.c_[v.values, base.values], lambda x: x[:, 0].mean() / x[:, 1].mean(), 20, B_BOOT, SEED)
        lv = np.log(v)
        nxt = np.log(base).shift(-1)
        c = pd.concat([lv, nxt], axis=1).dropna().corr().iloc[0, 1]
        rel = np.log(v / base)
        out[str(5 * k)] = {'vol': float(ann(v.mean(), 252)), 'vol_sub': float(ann(vs.mean(), 252)), 'ratio': float(ratio),
                           'lo': float(np.percentile(boot, 2.5)), 'hi': float(np.percentile(boot, 97.5)),
                           'corr_next': float(c), 'sd_rel': float(rel.std()),
                           'corr_next_sub': float(pd.concat([np.log(vs), nxt], axis=1).dropna().corr().iloc[0, 1])}
        if k > 1:
            ax.hist(rel.clip(-2, 2), bins=np.linspace(-2, 2, 61), histtype='step', color=col, lw=1.3,
                    label=f'log(RV at {5 * k} min / RV at 5 min)')
    ax.set_xlabel('Log ratio to the 5-minute RV, same day')
    ax.set_ylabel('Number of days')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch9_sem_frequency')
    return out


def b4_standardised():
    """Randamente standardizate cu RV (Andersen, Bollerslev, Diebold si Labys): aplatizare cu interval bootstrap."""
    out = {}
    btc_oc = 100 * np.log(P_BTC.iloc[:, -1] / P_BTC[0])
    for k, r, v in [('spy', OC, RV_SPY), ('btc', btc_oc, RV_BTC)]:
        z = (r / np.sqrt(v)).values
        u = (r / r.std()).values
        kz = T.block_bootstrap(z, lambda x: stats.kurtosis(x) + 3, 20, B_BOOT, SEED)
        ku = T.block_bootstrap(u, lambda x: stats.kurtosis(x) + 3, 20, B_BOOT, SEED)
        out[k] = {'kz': float(stats.kurtosis(z) + 3), 'kz_lo': float(np.percentile(kz, 2.5)), 'kz_hi': float(np.percentile(kz, 97.5)),
                  'ku': float(stats.kurtosis(u) + 3), 'ku_lo': float(np.percentile(ku, 2.5)), 'ku_hi': float(np.percentile(ku, 97.5)),
                  'sdz': float(z.std()), 'jbz': float(stats.jarque_bera(z).statistic), 'jbz_p': float(stats.jarque_bera(z).pvalue),
                  'skz': float(stats.skew(z)), 'N': int(len(z)),
                  'tail3': float(np.mean(np.abs(z) > 3)), 'tail3u': float(np.mean(np.abs(u) > 3))}
    out['normal_tail3'] = float(2 * stats.norm.sf(3))
    return out


def b5_har_insample():
    """log-HAR pe SPY (varianta totala), MCO cu erori obisnuite si Newey-West; Wald: beta_w = beta_m; Ljung-Box pe reziduuri."""
    res, X, ok = T.har_fit(RVT_SPY, log=True)
    y = np.log(RVT_SPY)[ok]
    Xc = np.column_stack([np.ones(ok.sum()), X[ok].values])
    e = res['resid']
    s2 = e @ e / (len(e) - 4)
    se_ols = np.sqrt(np.diag(s2 * np.linalg.inv(Xc.T @ Xc)))
    R = np.array([0, 0, 1, -1.0])
    wald = float((R @ res['b']) ** 2 / (R @ res['V'] @ R))
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb = acorr_ljungbox(e, lags=[10, 22])
    lb2 = acorr_ljungbox(y.values - y.mean(), lags=[10, 22])
    ar1 = T.ols_nw(y.values[1:], y.values[:-1, None])
    return {'b': res['b'], 'se_nw': res['se'], 'se_ols': se_ols, 'r2': res['r2'], 'T': res['T'], 'lags': res['lags'],
            'wald_wm': wald, 'p_wm': float(stats.chi2.sf(wald, 1)), 'lb10': float(lb['lb_stat'].iloc[0]), 'lb10_p': float(lb['lb_pvalue'].iloc[0]),
            'lb22': float(lb['lb_stat'].iloc[1]), 'lb22_p': float(lb['lb_pvalue'].iloc[1]), 'lby22': float(lb2['lb_stat'].iloc[1]),
            'pers': float(sum(res['b'][1:])), 'ar1_b': float(ar1['b'][1]), 'ar1_r2': float(ar1['r2']),
            't_nw': list(res['b'] / res['se']), 'ratio_se': list(res['se'] / se_ols)}


def garch_params_blocks(r, dates, refit=21):
    """Parametrii GARCH(1,1)-t reestimati la fiecare `refit` zile si varianta conditionata pentru fiecare zi."""
    from arch import arch_model
    dates = pd.DatetimeIndex(dates)
    pos = r.index.get_indexer(dates)
    rows = []
    for i0 in range(0, len(dates), refit):
        blk = dates[i0:i0 + refit]
        fit = arch_model(r.iloc[:pos[i0]], mean='Constant', vol='GARCH', p=1, q=1, dist='t').fit(disp='off')
        fixed = arch_model(r.iloc[:pos[min(i0 + refit, len(dates)) - 1] + 1], mean='Constant', vol='GARCH', p=1, q=1,
                           dist='t').fix(fit.params)
        s2 = (fixed.conditional_volatility ** 2).reindex(blk)
        for d in blk:
            rows.append((d, s2[d], fit.params['omega'], fit.params['alpha[1]'], fit.params['beta[1]']))
    return pd.DataFrame(rows, columns=['date', 's2', 'omega', 'alpha', 'beta']).set_index('date')


def b6_week():
    """Prognoza variantei pe urmatoarele 5 zile (SPY): HAR direct pe log vs GARCH(1,1)-t cu formula pe h pasi."""
    v = RVT_SPY
    y5 = v[::-1].rolling(5).sum()[::-1]                     # suma RV pe zilele t..t+4 (tinta pentru prognoza facuta la t-1)
    X = T.har_design(np.log(v))
    ok = X.notna().all(axis=1) & y5.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    ly = np.log(y5).values
    idx = np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]
    fh = {}
    for t in idx:
        tr = np.where(ok.values[:t - 4])[0]                 # doar tinte complet observate inainte de t
        b, *_ = np.linalg.lstsq(Xc[tr], ly[tr], rcond=None)
        s2 = np.var(ly[tr] - Xc[tr] @ b)
        fh[v.index[t]] = np.exp(Xc[t] @ b + s2 / 2)
    fh = pd.Series(fh)
    G = garch_params_blocks(D_SPY, fh.index)
    pers = G['alpha'] + G['beta']
    lr = G['omega'] / (1 - pers)
    fg = sum(lr + pers ** h * (G['s2'] - lr) for h in range(5))
    yy = y5.reindex(fh.index)
    out = {'T': int(len(fh))}
    for k, f in [('har', fh), ('garch', fg)]:
        mz = T.mz_test(yy, f)
        out[k] = {'qlike': float(T.qlike(yy, f).mean()), 'mse': float(T.mse(yy, f).mean()), 'mz_b': mz['b'], 'mz_a': mz['a'],
                  'mz_r2': mz['r2'], 'mz_p': mz['p'], 'mz_se_b': mz['se_b']}
    dq = T.dm_test(T.qlike(yy, fh), T.qlike(yy, fg))
    out.update({'dm_t': dq['t'], 'dm_p': dq['p'], 'pers_med': float(pers.median()),
                'note_overlap': 'overlapping 5-day targets: HAC lags set by the rule of thumb'})
    return out


def b7_harcj():
    """HAR-CJ pe log (Andersen, Bollerslev si Diebold): componenta continua si de salt; in esantion si out-of-sample."""
    j = T.jump_test(R_SPY)
    C = j['C'] + ON ** 2                                    # partea continua a variantei totale (noaptea inclusa)
    Jc = j['J']
    v = RVT_SPY
    X = pd.DataFrame({'cd': np.log(C).shift(1), 'cw': np.log(C).rolling(5).mean().shift(1),
                      'cm': np.log(C).rolling(22).mean().shift(1), 'j': np.log1p(Jc).shift(1)})
    y = np.log(v)
    ok = X.notna().all(axis=1)
    res = T.ols_nw(y[ok], X[ok])
    base, *_ = T.har_fit(v, log=True)
    # out-of-sample de la 2022, fereastra extinsa
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        f[v.index[t]] = np.exp(Xc[t] @ b + np.var(y.values[tr] - Xc[tr] @ b) / 2)
    f = pd.Series(f)
    fl = T.har_expanding(v, '2022-01-03', log=True).reindex(f.index)
    yy = v.reindex(f.index)
    dq = T.dm_test(T.qlike(yy, f), T.qlike(yy, fl))
    return {'b': res['b'], 'se': res['se'], 'r2': res['r2'], 'r2_base': base['r2'], 'T': res['T'],
            'q_cj': float(T.qlike(yy, f).mean()), 'q_har': float(T.qlike(yy, fl).mean()), 'dm_t': dq['t'], 'dm_p': dq['p']}


def b8_rough():
    """Exponentul H al log-volatilitatii (SPY): RV totala, RV intraday, BV, RV subesantionata la 30 de minute; bootstrap pe blocuri."""
    series = {'rv_total': RVT_SPY, 'rv_intraday': RV_SPY, 'bv': T.bv(R_SPY), 'rv30_sub': T.subsampled_rv(P_SPY, 6)}
    out = {}
    for k, s in series.items():
        x = 0.5 * np.log(s.values)
        H = rough_H(x)['H']
        boot = T.block_bootstrap(x, lambda z: rough_H(z)['H'], 60, 300, SEED)
        out[k] = {'H': H, 'lo': float(np.percentile(boot, 2.5)), 'hi': float(np.percentile(boot, 97.5))}
    # H pentru un proces cu H = 0.5 masurat cu zgomot (simulare): cat de mult coboara estimarea?
    rng = np.random.default_rng(SEED)
    n = len(RVT_SPY)
    x = np.cumsum(0.1 * rng.standard_normal(n))
    x = x - np.linspace(0, x[-1], n)
    out['sim_bm'] = rough_H(x)['H']
    out['sim_bm_noise'] = rough_H(x + 0.25 * rng.standard_normal(n))['H']
    return out


# =============================================================================
# PARTEA C: ESTE VOLATILITATEA BITCOIN MAI PREVIZIBILA DECAT A SPY?
# =============================================================================
def c1_predictability():
    """Aceeasi perioada out-of-sample (martie 2025 - septembrie 2026): log-HAR, GARCH-t, RV de ieri; R^2 MZ,
    castigul QLIKE fata de RV de ieri, bootstrap pe blocuri pentru diferenta de R^2; log-HAR cu efect de weekend pentru Bitcoin."""
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True).loc[C_START:]
    Fb = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_btc.csv'), index_col=0, parse_dates=True).loc[C_START:]
    out = {}
    for k, D in [('spy', F), ('btc', Fb)]:
        y = D['proxy']
        o = {'T': int(len(D))}
        for m in ['logHAR', 'GARCH-t', 'RW']:
            o[m] = {'r2': T.mz_test(y, D[m])['r2'], 'qlike': float(T.qlike(y, D[m]).mean())}
            o[m]['r2log'] = float(np.corrcoef(np.log(y), np.log(D[m]))[0, 1] ** 2)
        o['gain_rw'] = 1 - o['logHAR']['qlike'] / o['RW']['qlike']
        o['gain_garch'] = 1 - o['logHAR']['qlike'] / o['GARCH-t']['qlike']
        out[k] = o
    # bootstrap pe blocuri pentru diferenta R^2 (pe log) intre Bitcoin si SPY
    a = np.c_[np.log(F['proxy']), np.log(F['logHAR'])]
    b = np.c_[np.log(Fb['proxy']), np.log(Fb['logHAR'])]
    rng = np.random.default_rng(SEED)

    def boot_r2(x, block=20):
        n = len(x)
        nb = int(np.ceil(n / block))
        st = rng.integers(0, n - block + 1, nb)
        idx = (st[:, None] + np.arange(block)[None, :]).ravel()[:n]
        return np.corrcoef(x[idx, 0], x[idx, 1])[0, 1] ** 2
    d = np.array([boot_r2(b) - boot_r2(a) for _ in range(B_BOOT)])
    out['r2diff'] = float(out['btc']['logHAR']['r2log'] - out['spy']['logHAR']['r2log'])
    out['r2diff_lo'] = float(np.percentile(d, 2.5))
    out['r2diff_hi'] = float(np.percentile(d, 97.5))
    # log-HAR cu indicator de weekend pentru Bitcoin (fereastra extinsa)
    v = RV_BTC
    X = T.har_design(np.log(v), calendar=True)
    X['we'] = (v.index.dayofweek >= 5).astype(float)
    ok = X.notna().all(axis=1)
    y = np.log(v)
    res = T.ols_nw(y[ok], X[ok])
    base, *_ = T.har_fit(v, calendar=True, log=True)
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((v.index >= pd.Timestamp(C_START)) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        bb, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        f[v.index[t]] = np.exp(Xc[t] @ bb + np.var(y.values[tr] - Xc[tr] @ bb) / 2)
    f = pd.Series(f).reindex(Fb.index)
    yb = Fb['proxy']
    dq = T.dm_test(T.qlike(yb, f), T.qlike(yb, Fb['logHAR']))
    out['we'] = {'b_we': float(res['b'][4]), 'se_we': float(res['se'][4]), 'r2': res['r2'], 'r2_base': base['r2'],
                 'qlike': float(T.qlike(yb, f).mean()), 'r2log': float(np.corrcoef(np.log(yb), np.log(f))[0, 1] ** 2),
                 'dm_t': dq['t'], 'dm_p': dq['p'], 'mult': float(np.exp(res['b'][4]))}
    # grafic: R^2 pe log si castigul QLIKE, SPY vs Bitcoin
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.1))
    labs = ['logHAR', 'GARCH-t', 'RW']
    x = np.arange(3)
    axes[0].bar(x - 0.2, [out['spy'][m]['r2log'] for m in labs], 0.4, color=MainBlue, label='SPY (with overnight)')
    axes[0].bar(x + 0.2, [out['btc'][m]['r2log'] for m in labs], 0.4, color=Amber, label='Bitcoin (24 hours)')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(['log-HAR', 'GARCH(1,1)-t', "Yesterday's RV"])
    axes[0].set_ylabel(r'$R^2$ of log RV on log forecast')
    axes[1].bar(x - 0.2, [out['spy'][m]['qlike'] for m in labs], 0.4, color=MainBlue)
    axes[1].bar(x + 0.2, [out['btc'][m]['qlike'] for m in labs], 0.4, color=Amber)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(['log-HAR', 'GARCH(1,1)-t', "Yesterday's RV"])
    axes[1].set_ylabel('Mean QLIKE loss')
    fig_legend_bottom(fig, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch9_sem_c1')
    return out


# =============================================================================
# EXTINDERI DE NIVEL MASTER: inferenta pe salturi, HAR ca AR(22) restrictionat, HARQ, SHAR, MCS
# =============================================================================
def bh_count(p, q=0.05):
    """Benjamini-Hochberg: numarul de ipoteze respinse cu rata falselor descoperiri controlata la q."""
    p = np.sort(np.asarray(p))
    n = len(p)
    ok = np.where(p <= q * np.arange(1, n + 1) / n)[0]
    return int(ok[-1] + 1) if len(ok) else 0


def periodicity_sd(R, bv_day):
    """Factorul de periodicitate intraday (estimatorul SD din Boudt, Croux si Laurent, 2011):
    randamente standardizate cu sqrt(BV_t / M_t), abaterea patratica pe interval, normalizata la media 1 a patratelor."""
    M_ = R.notna().sum(axis=1)
    rb = R.div(np.sqrt(bv_day / M_), axis=0)
    sd = np.sqrt((rb ** 2).mean(axis=0))
    return sd / np.sqrt((sd ** 2).mean())


def ex_jump_inference(K=270, alpha_lm=0.01, c_trunc=3.0, varpi=0.49):
    """Salturi SPY: FDR (Benjamini-Hochberg), Bonferroni, testul raportului pe randamente ajustate de periodicitate,
    testul intraday Lee-Mykland (K = 270 pentru 5 minute), RV trunchiata (Mancini) si MedRV (Andersen, Dobrev, Schaumburg)."""
    j = T.jump_test(R_SPY)
    N = len(j)
    p = stats.norm.sf(j['z'].values)
    out = {'N': N, 'n5': int((p < 0.05).sum()), 'bh5': bh_count(p, 0.05), 'bh1': bh_count(p, 0.01),
           'bonf5': int((p < 0.05 / N).sum()), 'n0_1': int(j['jump'].sum())}
    f = periodicity_sd(R_SPY, j['bv'])
    Rs = R_SPY / f.values[None, :]
    js = T.jump_test(Rs)
    ps = stats.norm.sf(js['z'].values)
    out.update({'per_n5': int((ps < 0.05).sum()), 'per_n0_1': int(js['jump'].sum()), 'per_bh5': bh_count(ps, 0.05),
                'f_first': float(f.iloc[0]), 'f_min': float(f.min()), 'f_last': float(f.iloc[-1])})
    # Lee-Mykland: L = r / sigma_hat, sigma_hat^2 = media produselor |r_j||r_{j-1}| pe K-1 randamente anterioare (serie concatenata)
    x = Rs.values.ravel()
    day = np.repeat(np.arange(N), Rs.shape[1])
    slot = np.tile(np.arange(Rs.shape[1]), N)
    ok = ~np.isnan(x)
    x, day, slot = x[ok], day[ok], slot[ok]
    prod = np.r_[np.nan, np.abs(x[1:]) * np.abs(x[:-1])]
    bvl = pd.Series(prod).rolling(K - 2).mean().shift(1).values
    L = x / np.sqrt(bvl * np.pi / 2)     # mu_1^{-2} = pi/2: BV local estimeaza varianta pe interval
    n = int(np.isfinite(L).sum())
    c = np.sqrt(2 / np.pi)
    Cn = np.sqrt(2 * np.log(n)) / c - (np.log(np.pi) + np.log(np.log(n))) / (2 * c * np.sqrt(2 * np.log(n)))
    Sn = 1 / (c * np.sqrt(2 * np.log(n)))
    beta = -np.log(-np.log(1 - alpha_lm))
    hit = np.isfinite(L) & ((np.abs(L) - Cn) / Sn > beta)
    jd = np.unique(day[hit])
    out.update({'lm_K': K, 'lm_n': n, 'lm_crit': float(Cn + Sn * beta), 'lm_hits': int(hit.sum()), 'lm_days': int(len(jd)),
                'lm_open': int((slot[hit] == 0).sum()), 'lm_10': int((slot[hit] == 6).sum()),
                'lm_slots': [int(x) for x in slot[hit]],
                'lm_wed14': int(np.sum(hit & (np.asarray(Rs.index.dayofweek)[day] == 2) & (slot >= 54) & (slot <= 65))),
                'lm_top': {'date': str(Rs.index[day[hit]][np.argmax(np.abs(L[hit]))].date()),
                           'L': float(L[hit][np.argmax(np.abs(L[hit]))])},
                'lm_in_ratio': float(np.mean(j['jump'].values[jd])) if len(jd) else float('nan'),
                'ratio_in_lm': float(np.mean(np.isin(np.where(j['jump'].values)[0], jd)))})
    # RV trunchiata si MedRV (pe randamentele brute, pragul tine cont de periodicitate)
    Mt = R_SPY.notna().sum(axis=1).values
    thr = c_trunc * np.sqrt(j['bv'].values)[:, None] * (1 / Mt[:, None]) ** varpi * f.values[None, :]
    A = R_SPY.values
    trv = np.nansum(np.where(np.abs(A) <= thr, A ** 2, 0.0), axis=1)
    a = np.abs(A)
    med = np.nanmedian(np.stack([a[:, :-2], a[:, 1:-1], a[:, 2:]]), axis=0)
    medrv = np.pi / (6 - 4 * np.sqrt(3) + np.pi) * Mt / (Mt - 2) * np.nansum(med ** 2, axis=1)
    rvs = j['rv'].values
    out.update({'trv_share': float(1 - trv.sum() / rvs.sum()), 'bv_share': float(1 - j['bv'].sum() / rvs.sum()),
                'medrv_share': float(1 - medrv.sum() / rvs.sum()), 'trunc_days': float(np.mean(trv < rvs)),
                'c_trunc': c_trunc, 'varpi': varpi})
    return out


def ex_har_ar22():
    """log-HAR ca AR(22) restrictionat: test Wald (Newey-West) al celor 19 restrictii liniare."""
    y = np.log(RVT_SPY)
    X = pd.concat({f'l{k}': y.shift(k) for k in range(1, 23)}, axis=1)
    ok = X.notna().all(axis=1)
    res = T.ols_nw(y[ok].values, X[ok].values)
    Rm = []
    for k in (2, 3, 4):                                   # phi_k = phi_{k+1}, k = 2..4
        r = np.zeros(23); r[k] = 1; r[k + 1] = -1; Rm.append(r)
    for k in range(6, 22):                                # phi_k = phi_{k+1}, k = 6..21
        r = np.zeros(23); r[k] = 1; r[k + 1] = -1; Rm.append(r)
    Rm = np.array(Rm)
    d = Rm @ res['b']
    W = float(d @ np.linalg.solve(Rm @ res['V'] @ Rm.T, d))
    har, Xh, okh = T.har_fit(RVT_SPY, log=True)
    # aceeasi selectie pentru comparatia R^2
    return {'q': int(Rm.shape[0]), 'wald': W, 'p': float(stats.chi2.sf(W, Rm.shape[0])), 'r2_ar22': float(res['r2']),
            'r2_har': float(har['r2']), 'T': int(res['T']), 'lags': int(res['lags'])}


def _expanding_ols(y, X, start, filt=True):
    """Prognoze OLS pe fereastra extinsa; filtrul de 'insanity' din Bollerslev, Patton si Quaedvlieg (2016):
    prognoza din afara intervalului observat in esantionul de estimare este inlocuita cu media esantionului."""
    ok = X.notna().all(axis=1) & y.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    f = {}
    for t in np.where((y.index >= pd.Timestamp(start)) & ok.values)[0]:
        tr = np.where(ok.values[:t])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], y.values[tr], rcond=None)
        v = Xc[t] @ b
        if filt and (v < y.values[tr].min() or v > y.values[tr].max()):
            v = y.values[tr].mean()
        f[y.index[t]] = v
    return pd.Series(f)


def ex_harq_shar(start='2022-01-03'):
    """HARQ (Bollerslev, Patton, Quaedvlieg 2016) si SHAR (Patton, Sheppard 2015) pe varianta totala SPY, in niveluri;
    in esantion cu erori Newey-West; prognoze out-of-sample; MCS (Hansen, Lunde, Nason 2011) pe QLIKE."""
    v = RVT_SPY
    rqd = T.rq(R_SPY)
    Xh = T.har_design(v)
    XQ = Xh.copy()
    XQ['dq'] = (np.sqrt(rqd) * v).shift(1)
    okq = XQ.notna().all(axis=1)
    rQ = T.ols_nw(v[okq].values, XQ[okq].values)
    rH = T.ols_nw(v[okq].values, Xh[okq].values)
    # semivariante: randamentele intraday plus randamentul peste noapte ca un randament suplimentar al zilei
    A = np.c_[ON.reindex(R_SPY.index).values, R_SPY.values]
    rsp = pd.Series(np.nansum(np.where(A > 0, A ** 2, 0), axis=1), index=R_SPY.index)
    rsn = pd.Series(np.nansum(np.where(A < 0, A ** 2, 0), axis=1), index=R_SPY.index)
    XS = pd.DataFrame({'rsp': rsp.shift(1), 'rsn': rsn.shift(1), 'w': Xh['w'], 'm': Xh['m']})
    oks = XS.notna().all(axis=1)
    rS = T.ols_nw(v[oks].values, XS[oks].values)
    Rr = np.array([0, 1, -1.0, 0, 0])
    w_pm = float((Rr @ rS['b']) ** 2 / (Rr @ rS['V'] @ Rr))
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True)
    fQ = _expanding_ols(v, XQ, start).reindex(F.index)
    fS = _expanding_ols(v, XS, start).reindex(F.index)
    fH = _expanding_ols(v, Xh, start).reindex(F.index)
    y = F['proxy']
    L = pd.DataFrame({m: T.qlike(y, F[m]) for m in ['logHAR', 'HAR', 'GARCH-t', 'EWMA', 'RW']})
    L['HARQ'] = T.qlike(y, fQ)
    L['SHAR'] = T.qlike(y, fS)
    L['HARf'] = T.qlike(y, fH)
    out = {'harq': {'b': list(rQ['b']), 'se': list(rQ['se']), 'r2': float(rQ['r2']), 'r2_har': float(rH['r2']),
                    'bd_at': {}},
           'shar': {'b': list(rS['b']), 'se': list(rS['se']), 'r2': float(rS['r2']), 'wald_pm': w_pm,
                    'p_pm': float(stats.chi2.sf(w_pm, 1))},
           'qlike': {m: float(L[m].mean()) for m in L}}
    # panta zilnica efectiva beta_d + beta_Q sqrt(RQ) la cuantilele lui sqrt(RQ)
    s = np.sqrt(rqd.reindex(v[okq].index).values)
    for qq in (0.5, 0.99):
        out['harq']['bd_at'][str(qq)] = float(rQ['b'][1] + rQ['b'][4] * np.quantile(s, qq))
    # HARQ pe RV intraday (cadrul din lucrarea originala: RQ si RV din aceleasi randamente)
    vi = RV_SPY
    Xi = T.har_design(vi)
    Xi['dq'] = (np.sqrt(rqd) * vi).shift(1)
    oki = Xi.notna().all(axis=1)
    rI = T.ols_nw(vi[oki].values, Xi[oki].values)
    si = np.sqrt(rqd.reindex(vi[oki].index).values)
    out['harq_intra'] = {'b': list(rI['b']), 'se': list(rI['se']), 'r2': float(rI['r2']),
                         'bd_at': {str(qq): float(rI['b'][1] + rI['b'][4] * np.quantile(si, qq)) for qq in (0.5, 0.99)},
                         'sq': {str(qq): float(np.quantile(si, qq)) for qq in (0.5, 0.99)}}
    for m in ['HARQ', 'SHAR']:
        for base in ['HARf', 'logHAR']:
            dq = T.dm_test(L[m], L[base])
            out[f'dm_{m}_{base}'] = {'t': dq['t'], 'p': dq['p']}
    from arch.bootstrap import MCS
    mods = ['logHAR', 'HAR', 'GARCH-t', 'EWMA', 'RW', 'HARQ', 'SHAR']
    mcs = MCS(L[mods].dropna(), size=0.10, reps=10000, block_size=20, method='R', seed=SEED)
    mcs.compute()
    pv = mcs.pvalues['Pvalue']
    out['mcs'] = {'included': [str(m) for m in mcs.included], 'pvalues': {str(k): float(x) for k, x in pv.items()},
                  'T': int(len(L[mods].dropna()))}
    return out


def ex_gw_week():
    """Testul conditional Giacomini-White pentru prognozele pe 5 zile (B6): instrumente (1, d_{t-5}), HAC cu 4 intarzieri."""
    v = RVT_SPY
    y5 = v[::-1].rolling(5).sum()[::-1]
    X = T.har_design(np.log(v))
    ok = X.notna().all(axis=1) & y5.notna()
    Xc = np.column_stack([np.ones(len(X)), X.values])
    ly = np.log(y5).values
    idx = np.where((v.index >= pd.Timestamp('2022-01-03')) & ok.values)[0]
    fh = {}
    for t in idx:
        tr = np.where(ok.values[:t - 4])[0]
        b, *_ = np.linalg.lstsq(Xc[tr], ly[tr], rcond=None)
        fh[v.index[t]] = np.exp(Xc[t] @ b + np.var(ly[tr] - Xc[tr] @ b) / 2)
    fh = pd.Series(fh)
    G = garch_params_blocks(D_SPY, fh.index)
    pers = G['alpha'] + G['beta']
    lr = G['omega'] / (1 - pers)
    fg = sum(lr + pers ** h * (G['s2'] - lr) for h in range(5))
    yy = y5.reindex(fh.index)
    d = (T.qlike(yy, fh) - T.qlike(yy, fg)).values
    tau = 5
    Z = np.column_stack([np.ones(len(d) - tau), d[:-tau]]) * d[tau:, None]
    n = len(Z)
    zbar = Z.mean(axis=0)
    U = Z - zbar
    S = U.T @ U / n
    for l in range(1, tau):
        w = 1 - l / tau
        g = U[l:].T @ U[:-l] / n
        S += w * (g + g.T)
    stat = float(n * zbar @ np.linalg.solve(S, zbar))
    u = d - d.mean()
    s0 = u @ u / len(d)
    for l in range(1, tau):
        s0 += 2 * (1 - l / tau) * (u[l:] @ u[:-l]) / len(d)
    t_unc = float(d.mean() / np.sqrt(s0 / len(d)))
    return {'gw': stat, 'p': float(stats.chi2.sf(stat, 2)), 'T': n, 't_unc': t_unc,
            'p_unc': float(2 * stats.norm.sf(abs(t_unc)))}


def ex_rk_ratio():
    """Nucleul realizat pe bare de 5 minute: raportul mediilor RK/RV cu CI bootstrap pe blocuri (20 de zile)."""
    rk, H = T.realized_kernel(R_SPY, P_SPY)
    rk = rk.reindex(RV_SPY.index)
    boot = T.block_bootstrap(np.c_[rk.values, RV_SPY.values], lambda x: x[:, 0].mean() / x[:, 1].mean(), 20, B_BOOT, SEED)
    return {'ratio': float(rk.mean() / RV_SPY.mean()), 'lo': float(np.percentile(boot, 2.5)),
            'hi': float(np.percentile(boot, 97.5)), 'H_med': float(H.median())}


def ex_a8_mz():
    """A8: MZ pentru GARCH(1,1)-t (SPY, 2022-2026): coeficienti, erori NW si covarianta pentru testul Wald comun."""
    F = pd.read_csv(os.path.join(HERE, 'ch9_forecasts_spy.csv'), index_col=0, parse_dates=True)
    res = T.ols_nw(F['proxy'].values, F['GARCH-t'].values[:, None])
    V = res['V']
    dl = res['b'] - np.array([0, 1.0])
    W = float(dl @ np.linalg.solve(V, dl))
    d = (T.qlike(F['proxy'], F['logHAR']) - T.qlike(F['proxy'], F['GARCH-t']))
    dm = T.dm_test(T.qlike(F['proxy'], F['logHAR']), T.qlike(F['proxy'], F['GARCH-t']))
    return {'a': float(res['b'][0]), 'b': float(res['b'][1]), 'se_a': float(res['se'][0]), 'se_b': float(res['se'][1]),
            'cov': float(V[0, 1]), 'corr': float(V[0, 1] / np.sqrt(V[0, 0] * V[1, 1])), 'wald': W,
            'p': float(stats.chi2.sf(W, 2)), 'ta': float(res['b'][0] / res['se'][0]), 'tb': float((res['b'][1] - 1) / res['se'][1]),
            'dbar': float(d.mean()), 'se_d': float(dm['mean_diff'] / dm['t']), 'dm_t': dm['t'], 'dm_p': dm['p']}


def ex_a6_jensen():
    """A6: minimizantul MSE pe volatilitate cu un proxy RV = IV chi2_M / M: F* = IV (E sqrt(chi2_M/M))^2."""
    from scipy.special import gammaln
    out = {}
    for m in (1, 6, 78):
        out[str(m)] = float(2 / m * np.exp(2 * (gammaln((m + 1) / 2) - gammaln(m / 2))))
    return out


if __name__ == '__main__':
    ONLY = sys.argv[1:]                              # optional: recalculeaza doar blocurile numite, restul raman din json
    S = {}
    if ONLY:
        with open(os.path.join(HERE, 'sem9_results.json')) as fh:
            S = json.load(fh)
    for name, f in [('A1', a1_rv_bv), ('A2', a2_jump), ('A3', a3_noise), ('A4', a4_tsrv), ('A5', a5_har), ('A6', a6_losses),
                    ('A7', a7_har2), ('A8', a8_dm), ('B1', b1_spy_jumps), ('B2', b2_btc_jumps), ('B3', b3_frequency),
                    ('B4', b4_standardised), ('B5', b5_har_insample), ('B6', b6_week), ('B7', b7_harcj), ('B8', b8_rough),
                    ('C1', c1_predictability), ('XJ', ex_jump_inference), ('XAR', ex_har_ar22),
                    ('XQS', ex_harq_shar), ('XGW', ex_gw_week), ('XRK', ex_rk_ratio), ('XA8', ex_a8_mz),
                    ('XA6', ex_a6_jensen)]:
        if ONLY and name not in ONLY:
            continue
        print(name)
        S[name] = f()
    with open(os.path.join(HERE, 'sem9_results.json'), 'w') as fh:
        json.dump(jsonable(S), fh, indent=1)
    print('saved sem9_results.json')

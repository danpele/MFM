"""
seminar2.py -- Calculele pentru Seminarul 2 (MFM): eficienta pietei
===================================================================
Partea A: exemple pe hartie (VR pas cu pas, testul secventelor, Hurst din VR).
Partea B: VR/Chow-Denning pe piete, DFA rulant, AMH pe Bitcoin cu benzi bootstrap,
          anomalii de calendar cu corectii Bonferroni/Holm, autocorelatia fara zilele de criza.
Partea C: a devenit BVB mai eficienta dupa reclasificarea FTSE din septembrie 2020?
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import MARKETS, LABELS, load_close, log_returns, read_market, complete_months   # noqa: E402
from eff_tests import variance_ratio, chow_denning, runs_test, dfa_hurst, rolling_stat   # noqa: E402

from generate_all_charts import (plt, MainBlue, IDAred, Amber, Gray, LightGray, save_fig,  # noqa: E402
                                 legend_outside_bottom, calendar_table)

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42

# -----------------------------------------------------------------------------
# PARTEA A
# -----------------------------------------------------------------------------
A_RETURNS = np.array([1.0, -0.5, 0.8, 0.3, -1.2, 0.6, 0.9, -0.4])          # %
A_SIGNS = '++-+++--+-++---+-+++'                                            # 20 de zile
A4_SIGNS = '+++++-----+++++-----'


def a_vr_by_hand(r=A_RETURNS, q=2):
    """VR(q) fara corectii de deplasare: var(sume pe q zile, suprapuse) / (q * var zilnica)."""
    mu = r.mean()
    var1 = ((r - mu) ** 2).mean()
    sums = np.convolve(r, np.ones(q), mode='valid')
    varq = ((sums - q * mu) ** 2).mean()
    e = r - mu
    rho = [(e[j:] * e[:-j]).sum() / (e ** 2).sum() for j in range(1, q)]
    approx = 1 + 2 * sum((1 - j / q) * rho[j - 1] for j in range(1, q))
    return dict(mean=mu, var1=var1, sums=sums, varq=varq, VR=varq / (q * var1), rho=rho, approx=approx)


def a_runs(signs=A_SIGNS):
    n1, n2 = signs.count('+'), signs.count('-')
    n = n1 + n2
    runs = 1 + sum(signs[i] != signs[i - 1] for i in range(1, n))
    mean = 2 * n1 * n2 / n + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n ** 2 * (n - 1))
    z = (runs - mean) / np.sqrt(var)
    return dict(n1=n1, n2=n2, runs=runs, mean=mean, var=var, z=z, p=2 * (1 - stats.norm.cdf(abs(z))))


def h_from_vr(vr, q):
    """Pentru cresteri autosimilare, VR(q) = q^(2H-1), deci H = 0,5 + ln VR(q) / (2 ln q)."""
    return 0.5 + np.log(vr) / (2 * np.log(q))


# -----------------------------------------------------------------------------
# PARTEA B
# -----------------------------------------------------------------------------
def b_vr_table(names):
    rows = []
    for k in names:
        r = log_returns(k) if k != 'bettr' else np.log(read_market('BETTR.INDX')['close']).diff().dropna()
        v2, v5, v10, v20 = (variance_ratio(r, q) for q in (2, 5, 10, 20))
        cd = chow_denning(r)
        rows.append(dict(market=LABELS.get(k, 'BET-TR (Romania)'), N=len(r),
                         VR2=v2[0], z2=v2[1], zstar2=v2[2], VR5=v5[0], z5=v5[1], zstar5=v5[2],
                         VR20=v20[0], zstar20=v20[2], CD=cd[0], CD_p=cd[1]))
    return pd.DataFrame(rows).set_index('market')


def b_rolling_dfa(k='sp500', window=500, step=21, n_boot=199, seed=SEED):
    """DFA pe ferestre mobile; banda nula wild bootstrap (semne Rademacher) calculata pentru FIECARE fereastra:
    pastreaza volatilitatea ferestrei (permisa sub RW3) si distruge autocorelatia randamentelor.
    Pentru comparatie: banda i.i.d. Student-t4 (aceeasi pentru toate ferestrele)."""
    rng = np.random.default_rng(seed)
    null = [dfa_hurst(rng.standard_t(4, window))[0] for _ in range(300)]
    lo_t, hi_t = np.percentile(null, [2.5, 97.5])
    r = log_returns(k)
    x = r.values
    rows = []
    for end in range(window, len(x) + 1, step):
        e = x[end - window:end] - x[end - window:end].mean()
        g = np.random.default_rng(seed + end)
        sims = [dfa_hurst(e * g.choice([-1.0, 1.0], window))[0] for _ in range(n_boot)]
        lo, hi = np.percentile(sims, [2.5, 97.5])
        rows.append((r.index[end - 1], dfa_hurst(e)[0], lo, hi))
    d = pd.DataFrame(rows, columns=['date', 'dfa', 'lo', 'hi']).set_index('date')
    h = d['dfa']
    return dict(lo_t=lo_t, hi_t=hi_t, share_t=float(((h < lo_t) | (h > hi_t)).mean()),
                share_out=float(((h < d['lo']) | (h > d['hi'])).mean()), n=len(d),
                band_lo_mean=float(d['lo'].mean()), band_hi_mean=float(d['hi'].mean()),
                width_min=float((d['hi'] - d['lo']).min()), width_max=float((d['hi'] - d['lo']).max()),
                argwide=(d['hi'] - d['lo']).idxmax().date(), min=h.min(), max=h.max(),
                argmin=h.idxmin().date(), argmax=h.idxmax().date(), mean=h.mean())


def wild_bootstrap_vr_band(x, q=5, n_boot=199, seed=SEED):
    """Banda 95% pentru z*(q) sub ipoteza de mers aleator cu heteroscedasticitate: semne Rademacher."""
    rng = np.random.default_rng(seed)
    e = x - x.mean()
    zs = [variance_ratio(e * rng.choice([-1, 1], len(e)), q)[2] for _ in range(n_boot)]
    return np.percentile(zs, [2.5, 97.5])


def b_amh_bitcoin(window=365, step=30, q=5, seed=SEED):
    r = log_returns('btc', start='2011-01-01')
    rows = []
    x = r.values
    for end in range(window, len(x) + 1, step):
        w = x[end - window:end]
        z = variance_ratio(w, q)[2]
        lo, hi = wild_bootstrap_vr_band(w, q, 99, seed + end)
        rows.append((r.index[end - 1], z, lo, hi))
    d = pd.DataFrame(rows, columns=['date', 'zstar', 'lo', 'hi']).set_index('date')
    d['reject'] = (d['zstar'] < d['lo']) | (d['zstar'] > d['hi'])
    return d


def b_tom_ols_hac(k='sp500'):
    """Efectul turn-of-month: aceeasi regresie cu erori OLS clasice si cu erori HAC (Newey-West, 5 decalaje)."""
    r = complete_months(log_returns(k)) * 1e4
    d = pd.DataFrame({'r': r})
    ym = d.index.to_period('M')
    rank = d.groupby(ym).cumcount()
    rank_end = d.groupby(ym).cumcount(ascending=False)
    d['tom'] = ((rank < 3) | (rank_end == 0)).astype(float)
    X = sm.add_constant(d['tom'])
    ols = sm.OLS(d['r'], X).fit()
    hac = sm.OLS(d['r'], X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    return dict(N=len(d), share_tom=float(d['tom'].mean()), const=float(ols.params['const']),
                beta=float(ols.params['tom']), se_ols=float(ols.bse['tom']), t_ols=float(ols.tvalues['tom']),
                se_hac=float(hac.bse['tom']), t_hac=float(hac.tvalues['tom']), p_hac=float(hac.pvalues['tom']),
                mean_tom=float(d.loc[d['tom'] == 1, 'r'].mean()), mean_other=float(d.loc[d['tom'] == 0, 'r'].mean()))


def b_calendar_multiple(t):
    """5 piete x 3 efecte (ziua saptamanii, ianuarie, turn-of-month) din calendar_table(); Bonferroni si Holm."""
    rows = []
    for m, row in t.iterrows():
        rows.append((m, 'day of week (equal means)', row['dow_equal_p']))
        rows.append((m, 'January', 2 * (1 - stats.norm.cdf(abs(row['jan_t'])))))
        rows.append((m, 'turn of month', row['tom_p']))
    d = pd.DataFrame(rows, columns=['market', 'effect', 'p'])
    m = len(d)
    d['bonferroni_reject'] = d['p'] < 0.05 / m
    order = d['p'].sort_values().index
    holm = pd.Series(False, index=d.index)
    for i, ix in enumerate(order):
        if d.loc[ix, 'p'] < 0.05 / (m - i):
            holm[ix] = True
        else:
            break
    d['holm_reject'] = holm
    d['raw_reject'] = d['p'] < 0.05
    return d


def _segment_stats(x, keep, q=5):
    """rho1, tau1 si z*(q) Lo-MacKinlay calculate DOAR in segmentele contigue pastrate:
    perechile (t, t-k) si sumele pe q zile care traverseaza o perioada eliminata nu sunt folosite.
    Cu keep = True peste tot, rezultatul coincide cu variance_ratio(x, q)."""
    x = np.asarray(x, dtype=float)
    keep = np.asarray(keep, dtype=bool)
    T = keep.sum()
    mu = x[keep].mean()
    e = np.where(keep, x - mu, 0.0)
    s2 = (e ** 2).sum()

    def pair(k):                          # ambele capete pastrate si toate zilele dintre ele pastrate
        ok = np.convolve(keep.astype(int), np.ones(k + 1, dtype=int), mode='valid') == k + 1
        return ok, e[k:] * ok, e[:-k] * ok
    ok1, a1, b1 = pair(1)
    rho1 = (a1 * b1).sum() / s2
    tau1 = (a1 ** 2 * b1 ** 2).sum() / s2 ** 2
    okq = np.convolve(keep.astype(int), np.ones(q, dtype=int), mode='valid') == q
    agg = (np.convolve(np.where(keep, x, 0.0), np.ones(q), mode='valid') - q * mu)[okq]
    m = q * len(agg) * (1 - q / T)
    vr = ((agg ** 2).sum() / m) / (s2 / (T - 1))
    theta = 0.0
    for j in range(1, q):
        _, a, b = pair(j)
        theta += (2 * (q - j) / q) ** 2 * T * (a ** 2 * b ** 2).sum() / s2 ** 2
    return dict(N=int(T), rho1=rho1, t_iid=rho1 * np.sqrt(T), t_robust=rho1 / np.sqrt(tau1),
                zstar5=np.sqrt(T) * (vr - 1) / np.sqrt(theta), n_pairs=int(ok1.sum()), n_windows=int(okq.sum()))


def b_crisis_robustness():
    """Autocorelatia S&P 500 cu si fara 2008-2009 si 2020; fara crize, statisticile se calculeaza doar in
    segmentele contigue ramase (nicio pereche de zile si nicio suma pe 5 zile nu traverseaza o criza eliminata)."""
    r = log_returns('sp500')
    mask = ~(((r.index >= '2008-09-01') & (r.index <= '2009-06-30')) |
             ((r.index >= '2020-02-15') & (r.index <= '2020-06-30')))
    out = {'all days': _segment_stats(r.values, np.ones(len(r), bool)),
           'without 2008-09 and 2020 crises': _segment_stats(r.values, mask)}
    return pd.DataFrame(out).T


def b_bet_common_period():
    """BET vs BET-TR pe perioada comuna (de la inceputul BET-TR): separa efectul selectiei de cel al dividendelor."""
    tr = np.log(read_market('BETTR.INDX')['close']).diff().dropna()
    b = log_returns('bet')
    out = {}
    for lab, r in [('BET, full sample', b), ('BET, BET-TR period', b.loc[tr.index[0]:tr.index[-1]]),
                   ('BET-TR', tr)]:
        v2 = variance_ratio(r, 2)
        cd = chow_denning(r)
        out[lab] = dict(start=str(r.index[0].date()), N=len(r), rho1=r.autocorr(1), VR2=v2[0], z2=v2[1],
                        zstar2=v2[2], zstar5=variance_ratio(r, 5)[2], CD=cd[0], CD_p=cd[1])
    return out


# -----------------------------------------------------------------------------
# PARTEA C
# -----------------------------------------------------------------------------
def c_bvb_before_after(split='2020-09-21', years=5, n_boot=999, block=20, seed=SEED):
    """rho1 si z*(5) pentru BET cu 5 ani inainte si dupa reclasificare; bootstrap pe blocuri pentru diferenta."""
    r = log_returns('bet')
    s = pd.Timestamp(split)
    before = r.loc[s - pd.DateOffset(years=years):s - pd.Timedelta(days=1)]
    after = r.loc[s:s + pd.DateOffset(years=years)]
    rng = np.random.default_rng(seed)

    def block_boot(x):
        n = len(x)
        starts = rng.integers(0, n - block + 1, int(np.ceil(n / block)))
        return np.concatenate([x[s0:s0 + block] for s0 in starts])[:n]

    def rho1(x):
        return np.corrcoef(x[1:], x[:-1])[0, 1]

    diffs = [rho1(block_boot(after.values)) - rho1(block_boot(before.values)) for _ in range(n_boot)]
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return dict(before=(before.index[0].date(), before.index[-1].date(), len(before), rho1(before.values),
                        variance_ratio(before, 5)[2]),
                after=(after.index[0].date(), after.index[-1].date(), len(after), rho1(after.values),
                       variance_ratio(after, 5)[2]),
                diff=rho1(after.values) - rho1(before.values), ci=(lo, hi))


# -----------------------------------------------------------------------------
# GRAFICE PENTRU SEMINAR
# -----------------------------------------------------------------------------
def fig_amh_btc(d):
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.fill_between(d.index, d['lo'], d['hi'], color=LightGray, alpha=0.8, lw=0,
                    label='Wild-bootstrap 95% band under RW3 (per window)')
    ax.plot(d.index, d['zstar'], color=Amber, lw=1.0, label=r'Bitcoin $z^*(5)$, 365-day windows')
    r = d[d['reject']]
    ax.scatter(r.index, r['zstar'], color=IDAred, zorder=3, s=18, label='Outside the band')
    for x in (-1.96, 1.96):
        ax.axhline(x, color=Gray, ls='--', lw=0.7)
    ax.set_ylabel(r'$z^*(5)$')
    ax.set_title('Adaptive efficiency of Bitcoin: variance-ratio test on rolling one-year windows',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    plt.tight_layout()
    save_fig('ch2_sem_amh_btc')


def fig_bvb_before_after(split='2020-09-21', window=250):
    r = log_returns('bet', start='2014-01-01')
    rho = r.rolling(window).apply(lambda x: np.corrcoef(x[1:], x[:-1])[0, 1], raw=True).dropna()
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(rho.index, rho.values, color=IDAred, lw=0.9, label=f'BET lag-1 autocorrelation, rolling {window} days')
    ax.axhspan(-1.96 / np.sqrt(window), 1.96 / np.sqrt(window), color=LightGray, alpha=0.7, lw=0,
               label=rf'i.i.d. 95% band $\pm 1.96/\sqrt{{{window}}}$')
    ax.axvline(pd.Timestamp(split), color=MainBlue, ls='--', lw=1,
               label='FTSE upgrade to Secondary Emerging (21 Sep 2020)')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel(r'$\hat\rho_1$')
    ax.set_title('Did the Bucharest Stock Exchange become more efficient after the FTSE upgrade?',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    plt.tight_layout()
    save_fig('ch2_sem_bvb_before_after')


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if hasattr(o, 'isoformat'):
        return o.isoformat()
    return o


if __name__ == '__main__':
    import json
    pd.set_option('display.width', 220)
    S = {}
    S['A1'] = a_vr_by_hand()
    S['A2'] = a_vr_by_hand(q=3)
    S['A3'] = a_runs()
    S['A4'] = a_runs(A4_SIGNS)
    t = b_vr_table(['sp500', 'bet'])
    S['A5'] = dict(vr=float(t.loc[LABELS['bet'], 'VR20']), H=float(h_from_vr(t.loc[LABELS['bet'], 'VR20'], 20)))
    S['A6'] = dict(vr=float(t.loc[LABELS['sp500'], 'VR20']), H=float(h_from_vr(t.loc[LABELS['sp500'], 'VR20'], 20)))
    S['B1'] = t.to_dict(orient='index')
    t2 = b_vr_table(['bettr', 'wig20', 'bux', 'px', 'xu100', 'bvsp', 'mxx', 'nsei', 'ssec'])
    t2.to_csv(os.path.join(HERE, 'ch2_sem_vr_emerging.csv'))
    S['B2'] = t2.to_dict(orient='index')
    S['B3'] = b_rolling_dfa()
    d = b_amh_bitcoin()
    d.to_csv(os.path.join(HERE, 'ch2_sem_amh_btc.csv'))
    fig_amh_btc(d)
    fig_bvb_before_after()
    rej = d[d['reject']]
    S['B4'] = dict(n=len(d), share=float(d['reject'].mean()), first=d.index[0].date(), last=d.index[-1].date(),
                   rejections=[dict(date=i.date(), z=float(r.zstar), lo=float(r.lo), hi=float(r.hi)) for i, r in rej.iterrows()],
                   band_lo_mean=float(d['lo'].mean()), band_hi_mean=float(d['hi'].mean()),
                   share_naive=float((d['zstar'].abs() > 1.96).mean()))
    S['B5'] = {k: b_tom_ols_hac(k) for k in ['sp500', 'bet']}
    cm = b_calendar_multiple(calendar_table())
    cm.to_csv(os.path.join(HERE, 'ch2_sem_calendar_multiple.csv'), index=False)
    S['B6'] = cm.to_dict(orient='records')
    S['B7'] = b_crisis_robustness().to_dict(orient='index')
    S['B2c'] = b_bet_common_period()
    S['C1'] = c_bvb_before_after()
    S = _clean(S)
    with open(os.path.join(HERE, 'ch2_seminar_numbers.json'), 'w') as f:
        json.dump(S, f, indent=1)
    print(json.dumps({k: S[k] for k in ['A1', 'A3', 'A5', 'B3', 'B4', 'B5', 'B7', 'C1']}, indent=1, default=str)[:6000])

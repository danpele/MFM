"""
seminar1.py -- Calculele Seminarului 1 (MFM): fapte stilizate, inferenta si verificarea modelelor
================================================================================================
Foloseste datele si stilul din generate_all_charts.py (closes, rets, spx_ohlc, culori, save_fig).
Fiecare functie intoarce rezultatele numerice folosite in versiunea profesorului a slide-urilor;
graficele noi se salveaza in charts/ (fundal transparent, legenda sub grafic).

Modelarea Pietelor Financiare - Daniel Traian PELE & Antoaneta Amza
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

from mfm_data import read_market
from generate_all_charts import (closes, rets, spx_ohlc, LABELS, COLORS, PERIODS, MainBlue, IDAred,
                                 Forest, Amber, Gray, LightGray, save_fig, legend_outside_bottom,
                                 hill_estimator, leverage_corr, cusum_squares_break, local_whittle)

SEED = 42


# =============================================================================
# A7: indicele de coada Hill, pas cu pas (cele mai mari 11 randamente absolute)
# =============================================================================
def hill_by_hand(asset='bettr', k=10):
    """Lista celor mai mari k+1 randamente absolute (in %, 3 zecimale) si alpha_hat din valorile rotunjite."""
    r = rets[asset]
    top = r.abs().sort_values(ascending=False).iloc[:k + 1]
    x = np.round(100 * top.values, 3)
    alpha = 1.0 / np.mean(np.log(x[:k] / x[k]))
    return dict(dates=[d.date() for d in top.index], signs=np.sign(r.loc[top.index].values),
                x_pct=x, alpha=alpha, se=alpha / np.sqrt(k), n=len(r),
                alpha_exact=hill_estimator(np.abs(r.values), k))


# =============================================================================
# A8: mixtura cu regimuri Markov -> autocorelatia lui r_t^2
# =============================================================================
def markov_mixture(p_high=0.9, s2=(1.0, 4.0), pi=(0.8, 0.2), n_sim=400_000):
    """r_t = sigma_{S_t} eps_t; S_t lant Markov cu 2 stari, distributie stationara pi.

    Probabilitatea de a ramane in starea de volatilitate mare este p_high; din echilibrul
    pi_1 p_12 = pi_2 p_21 rezulta p_12 = (1 - p_high) pi_2 / pi_1.
    corr(r_t^2, r_{t-k}^2) = lambda^k Var(sigma^2) / Var(r^2), lambda = p_11 + p_22 - 1.
    """
    s2 = np.asarray(s2)
    p21 = 1 - p_high
    p12 = p21 * pi[1] / pi[0]
    lam = (1 - p12) + p_high - 1
    e2 = pi[0] * s2[0] + pi[1] * s2[1]
    e4 = pi[0] * s2[0] ** 2 + pi[1] * s2[1] ** 2
    var_s2, var_r2 = e4 - e2 ** 2, 3 * e4 - e2 ** 2
    rho = lambda k: lam ** k * var_s2 / var_r2
    # verificare prin simulare
    rng = np.random.default_rng(SEED)
    S = np.empty(n_sim, dtype=int); S[0] = 0
    u = rng.random(n_sim)
    for t in range(1, n_sim):
        S[t] = (u[t] < p12) if S[t - 1] == 0 else (u[t] >= p21)
    r = np.sqrt(s2[S]) * rng.standard_normal(n_sim)
    r2 = pd.Series(r ** 2)
    return dict(p12=p12, p21=p21, lam=lam, var_s2=var_s2, var_r2=var_r2, bound=var_s2 / var_r2,
                rho1=rho(1), rho10=rho(10), sim_rho1=r2.autocorr(1), sim_rho10=r2.autocorr(10),
                kurt=3 * e4 / e2 ** 2)


# =============================================================================
# A9: kurtosisul unui GARCH(1,1) cu inovatii cu distributie Normala
# =============================================================================
def garch_kurtosis(alpha=0.10, beta=0.85):
    s = alpha + beta
    denom = 1 - s ** 2 - 2 * alpha ** 2
    return dict(persistence=s, fourth_moment_cond=s ** 2 + 2 * alpha ** 2,
                K=3 * (1 - s ** 2) / denom if denom > 0 else np.inf)


def garch_alpha_for_kurtosis(K_target, persistence):
    """alpha necesar pentru un kurtosis dat, la persistenta alpha + beta fixa."""
    s2 = persistence ** 2
    return np.sqrt((1 - s2) * (K_target - 3) / (2 * K_target))


# =============================================================================
# B3: Ljung-Box standard vs robust la heteroscedasticitate
# =============================================================================
def robust_ljung_box(r, m=10):
    """t_k = rho_k / sqrt(sum e_t^2 e_{t-k}^2 / (sum e_t^2)^2); Q* = sum t_k^2 ~ chi2_m."""
    e = (r - r.mean()).values
    s2 = np.sum(e ** 2)
    rows = []
    for k in range(1, m + 1):
        rho = np.sum(e[k:] * e[:-k]) / s2
        se_rob = np.sqrt(np.sum(e[k:] ** 2 * e[:-k] ** 2)) / s2
        rows.append((k, rho, rho * np.sqrt(len(e)), rho / se_rob))
    t = pd.DataFrame(rows, columns=['k', 'rho', 't_iid', 't_robust']).set_index('k')
    q_std = acorr_ljungbox(r, lags=[m], return_df=True)
    q_rob = float((t['t_robust'] ** 2).sum())
    return dict(table=t, Q=float(q_std['lb_stat'].iloc[0]), Q_p=float(q_std['lb_pvalue'].iloc[0]),
                Q_rob=q_rob, Q_rob_p=float(stats.chi2.sf(q_rob, m)),
                n_sig_iid=int((t['t_iid'].abs() > 1.96).sum()), n_sig_rob=int((t['t_robust'].abs() > 1.96).sum()))


def fig_robust_acf(asset='sp500', m=20):
    x = (rets[asset] - rets[asset].mean()).values
    T, s2 = len(x), np.sum(x ** 2)
    ks = np.arange(1, m + 1)
    rho = np.array([np.sum(x[k:] * x[:-k]) / s2 for k in ks])
    tau = np.array([np.sum(x[k:] ** 2 * x[:-k] ** 2) / s2 ** 2 for k in ks])
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    ax.bar(ks, rho, color=MainBlue, width=0.6, label='$\\hat\\rho_k$')
    ax.plot(ks, 1.96 * np.sqrt(tau), color=IDAred, lw=1.1, label='Robust band $\\pm1.96\\sqrt{\\hat\\tau_k}$')
    ax.plot(ks, -1.96 * np.sqrt(tau), color=IDAred, lw=1.1)
    ax.axhline(1.96 / np.sqrt(T), color=Gray, ls='--', lw=0.9, label='Classical band $\\pm1.96/\\sqrt{T}$')
    ax.axhline(-1.96 / np.sqrt(T), color=Gray, ls='--', lw=0.9)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xticks(ks[::2] if m > 10 else ks)
    ax.set_xlabel('Lag $k$')
    ax.set_ylabel('Autocorrelation of $r_t$')
    ax.set_title(f'{LABELS[asset]}: classical vs heteroskedasticity-robust bands', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_sem_robust_acf')


def dgp_q(r, m=10, lam=2.576):
    """Dalla, Giraitis & Phillips (2022): Q = t' R*^{-1} t, t_k = sum e_t e_{t-k} / sqrt(sum e_t^2 e_{t-k}^2);
    R* pastreaza doar termenii incrucisati semnificativi (|tau_jk| > 2.576). R* = I da Q-tilde diagonal."""
    e = (r - r.mean()).values
    P = np.array([np.r_[np.zeros(k), e[k:] * e[:-k]] for k in range(1, m + 1)])
    d = np.sqrt((P ** 2).sum(1))
    t = P.sum(1) / d
    R = (P @ P.T) / np.outer(d, d)
    for j in range(m):
        for k in range(m):
            if j != k:
                pp = P[j] * P[k]
                if abs(pp.sum() / np.sqrt((pp ** 2).sum())) < lam:
                    R[j, k] = 0.0
    q = float(t @ np.linalg.solve(R, t))
    return q, float(stats.chi2.sf(q, m)), int((R != 0).sum() - m)


def robust_lb_table(assets=('sp500', 'bettr', 'eurron'), m_q=10, m_band=20):
    rows = []
    for a in assets:
        x = (rets[a] - rets[a].mean()).values
        T, s2 = len(x), np.sum(x ** 2)
        ks = np.arange(1, m_band + 1)
        rho = np.array([np.sum(x[k:] * x[:-k]) / s2 for k in ks])
        tau = np.array([np.sum(x[k:] ** 2 * x[:-k] ** 2) / s2 ** 2 for k in ks])
        q = acorr_ljungbox(rets[a], lags=[m_q], return_df=True)
        qt = float(np.sum(rho[:m_q] ** 2 / tau[:m_q]))
        rows.append({'asset': LABELS[a], 'T': T, 'Q10': float(q['lb_stat'].iloc[0]), 'Q10_p': float(q['lb_pvalue'].iloc[0]),
                     'Qt10': qt, 'Qt10_p': float(stats.chi2.sf(qt, m_q)),
                     'sig_classic': int(np.sum(np.abs(rho) > 1.96 / np.sqrt(T))),
                     'sig_robust': int(np.sum(np.abs(rho) > 1.96 * np.sqrt(tau))),
                     'robust_lags': [int(k) for k in ks[np.abs(rho) > 1.96 * np.sqrt(tau)]], 'rho1': rho[0],
                     **dict(zip(['Q_DGP', 'Q_DGP_p', 'n_cross_terms'], dgp_q(rets[a], m_q)))})
    return pd.DataFrame(rows).set_index('asset')


# =============================================================================
# B5: kurtosisul care nu converge (fereastra extinsa)
# =============================================================================
def _kurt_path(x, ends):
    """Excesul de kurtosis pe ferestre extinse [0, e) calculat din sume cumulate (vectorizat pe coloane)."""
    c1, c2, c3, c4 = (np.cumsum(x ** p, axis=0) for p in (1, 2, 3, 4))
    n = ends[:, None].astype(float)
    m1, m2, m3, m4 = (c[ends - 1] / n for c in (c1, c2, c3, c4))
    var = m2 - m1 ** 2
    mu4 = m4 - 4 * m1 * m3 + 6 * m1 ** 2 * m2 - 3 * m1 ** 4
    return mu4 / var ** 2 - 3


def fig_kurtosis_expanding(n_paths=500, nus=(3, 6)):
    """Excesul de kurtosis al S&P 500 pe primii n ani (n = 1..36) vs benzi 5-95% din Student-t simulate."""
    r = rets['sp500']
    first = r.index[0]
    ends = np.array([np.searchsorted(r.index, first + pd.DateOffset(years=y)) for y in range(1, 37)])
    ends = ends[(ends > 0) & (ends <= len(r))]
    k_data = _kurt_path(r.values[:, None], ends)[:, 0]
    rng = np.random.default_rng(SEED)
    bands = {}
    for nu in nus:
        sims = stats.t.rvs(nu, size=(len(r), n_paths), random_state=rng)
        K = _kurt_path(sims, ends)
        bands[nu] = (np.quantile(K, 0.05, axis=1), np.quantile(K, 0.5, axis=1), np.quantile(K, 0.95, axis=1))
    years = np.arange(1, len(ends) + 1)
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    for nu, c in zip(nus, (IDAred, Forest)):
        lo, med, hi = bands[nu]
        ax.fill_between(years, lo, hi, color=c, alpha=0.15, lw=0, label=f'Student-t, $\\nu$={nu}: 5%-95% of {n_paths} paths')
        ax.plot(years, med, color=c, lw=0.8, ls='--', label=f'Student-t, $\\nu$={nu}: median')
    ax.plot(years, k_data, color=MainBlue, lw=1.4, marker='o', ms=2.5, label='S&P 500 (from January 1990)')
    ax.set_yscale('symlog', linthresh=10)
    ax.set_xlabel('Window length: first $n$ years of data')
    ax.set_ylabel('Excess kurtosis')
    ax.set_title('Expanding-window kurtosis: data vs simulated Student-t', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.3)
    plt.tight_layout()
    save_fig('ch1_sem_kurtosis_expanding')
    kd = pd.Series(k_data, index=years)
    jumps = kd.diff().sort_values(ascending=False).head(3)
    top_days = r.abs().sort_values(ascending=False).head(5)
    return dict(k_by_year=kd.round(2).to_dict(), jumps=jumps.round(2).to_dict(),
                top_days=[(d.date(), round(100 * r[d], 1)) for d in top_days.index],
                band3_end=(bands[3][0][-1], bands[3][1][-1], bands[3][2][-1]),
                band6_end=(bands[6][0][-1], bands[6][1][-1], bands[6][2][-1]),
                band6_width_y5=bands[6][2][4] - bands[6][0][4], band6_width_end=bands[6][2][-1] - bands[6][0][-1],
                band3_width_y5=bands[3][2][4] - bands[3][0][4], band3_width_end=bands[3][2][-1] - bands[3][0][-1],
                inside3=bool(bands[3][0][-1] <= kd.iloc[-1] <= bands[3][2][-1]),
                inside6=bool(bands[6][0][-1] <= kd.iloc[-1] <= bands[6][2][-1]))


# =============================================================================
# B6: Hill pe ambele cozi, cu intervale de incredere, vs nu_hat Student-t
# =============================================================================
HILL_FRACS_TAILS = np.round(np.arange(0.01, 0.1001, 0.0025), 4)


def hill_tails(assets=('bettr', 'btc'), frac=0.02):
    rows = []
    for a in assets:
        r = rets[a]
        k = int(frac * len(r))
        aL, aR = hill_estimator(-r.values, k), hill_estimator(r.values, k)
        z = (r - r.mean()) / r.std()
        nu = stats.t.fit(z)[0]
        zdiff = (aL - aR) / np.sqrt(aL ** 2 / k + aR ** 2 / k)
        rows.append({'asset': LABELS[a], 'n': len(r), 'k': k, 'alpha_left': aL,
                     'ci_left': (aL * (1 - 1.96 / np.sqrt(k)), aL * (1 + 1.96 / np.sqrt(k))),
                     'alpha_right': aR,
                     'ci_right': (aR * (1 - 1.96 / np.sqrt(k)), aR * (1 + 1.96 / np.sqrt(k))),
                     'z_diff': zdiff, 'p_diff': 2 * stats.norm.sf(abs(zdiff)), 'nu_mle': nu})
    return pd.DataFrame(rows).set_index('asset')


def fig_hill_tails(assets=('bettr', 'btc')):
    fig, axes = plt.subplots(1, len(assets), figsize=(7.2, 3.0), sharey=True)
    for ax, a in zip(axes, assets):
        r = rets[a].values
        for side, x, c, lab in [('left', -r, IDAred, 'Left tail (losses)'), ('right', r, Forest, 'Right tail (gains)')]:
            ks = np.array([max(int(f * len(r)), 5) for f in HILL_FRACS_TAILS])
            al = np.array([hill_estimator(x, k) for k in ks])
            ax.plot(100 * HILL_FRACS_TAILS, al, color=c, lw=1.1, label=lab)
            ax.fill_between(100 * HILL_FRACS_TAILS, al * (1 - 1.96 / np.sqrt(ks)), al * (1 + 1.96 / np.sqrt(ks)),
                            color=c, alpha=0.15, lw=0)
        z = (rets[a] - rets[a].mean()) / rets[a].std()
        ax.axhline(stats.t.fit(z)[0], color=Gray, ls='--', lw=0.9, label='Student-t $\\hat\\nu$ (MLE)')
        ax.axhline(4, color=LightGray, lw=0.8)
        ax.set_title(LABELS[a], fontsize=9, loc='left')
        ax.set_xlabel('Tail fraction $k/n$ (%)')
    axes[0].set_ylabel('Hill tail index $\\hat\\alpha$')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch1_sem_hill_tails')


# =============================================================================
# B7: efectul de levier -- Romania vs cripto (grafic + regresie HAC)
# =============================================================================
def fig_leverage_ro_crypto(K=20):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    out = {}
    for a in ('bettr', 'btc'):
        ks, vals = leverage_corr(rets[a], K)
        L = pd.Series(vals, index=ks)
        out[a] = L
        ax.plot(L.index, L.values, marker='o', ms=2.5, lw=1.0, color=COLORS[a], label=LABELS[a])
    ax.axhline(0, color=Gray, lw=0.5)
    ax.axvline(0, color=LightGray, lw=0.5)
    for a in ('bettr', 'btc'):                      # banda i.i.d. de referinta, cu T-ul fiecarei serii
        band = 1.96 / np.sqrt(len(rets[a]))
        ax.axhline(band, color=COLORS[a], ls=':', lw=0.9, label=f'{LABELS[a]}: i.i.d. reference band $\\pm${band:.3f}')
        ax.axhline(-band, color=COLORS[a], ls=':', lw=0.9)
    ax.set_xlabel('Lag $k$ (days); $k>0$: return today, volatility later')
    ax.set_ylabel('corr$(r_t, |r_{t+k}|)$')
    ax.set_title('Leverage effect: Romania (BET-TR) vs crypto (Bitcoin)', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_sem_leverage_ro_crypto')
    return pd.DataFrame(out)


def leverage_regression(asset, n_controls=5):
    """|r_{t+1}| = c + b_plus r_t^+ + b_minus r_t^- + sum_{j=1..5} d_j |r_{t-j}| + u, erori Newey-West (HAC).

    |r_t| nu intra printre controale: |r_t| = r_t^+ - r_t^- (coliniaritate perfecta)."""
    r = rets[asset]
    df = pd.DataFrame({'y': r.abs().shift(-1), 'pos': np.maximum(r, 0), 'neg': np.minimum(r, 0)})
    for j in range(1, n_controls + 1):
        df[f'abs_lag{j}'] = r.abs().shift(j)
    df = df.dropna()
    L = int(4 * (len(df) / 100) ** (2 / 9))
    fit = sm.OLS(df['y'], sm.add_constant(df.drop(columns='y'))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    w = fit.wald_test('pos + neg = 0', scalar=True)
    return dict(b_pos=fit.params['pos'], se_pos=fit.bse['pos'], b_neg=fit.params['neg'], se_neg=fit.bse['neg'],
                wald=float(w.statistic), wald_p=float(w.pvalue), lags=L, n=len(df))


# =============================================================================
# B9: BET-TR vs S&P 500 -- test pentru Sharpe si tranzactionare nesincrona
# =============================================================================
def bettr_vs_sp500(n_boot=2000, block=21):
    px = pd.concat([closes['bettr'], closes['sp500']], axis=1, keys=['bet', 'spx']).dropna()   # join pe PRETURI
    r = np.log(px).diff().dropna()                            # randamente log: corelatii
    R = px.pct_change().dropna()                              # randamente simple: Sharpe (definitia cursului)
    T = len(r)
    sr = R.mean() / R.std()                                   # Sharpe zilnic, r_f = 0
    rho = R['bet'].corr(R['spx'])
    theta = 2 - 2 * rho + 0.5 * (sr['bet'] ** 2 + sr['spx'] ** 2 - 2 * sr['bet'] * sr['spx'] * rho ** 2)
    z_jkm = (sr['bet'] - sr['spx']) / np.sqrt(theta / T)
    # bootstrap pe blocuri (blocuri circulare de 21 de zile) pentru diferenta Sharpe anualizata
    rng = np.random.default_rng(SEED)
    vals = R.values
    nb = int(np.ceil(T / block))
    diffs = []
    for _ in range(n_boot):
        starts = rng.integers(0, T, nb)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:T] % T
        s = vals[idx]
        m, sd = s.mean(0), s.std(0, ddof=1)
        diffs.append(np.sqrt(252) * (m[0] / sd[0] - m[1] / sd[1]))
    diffs = np.array(diffs)
    d_obs = np.sqrt(252) * (sr['bet'] - sr['spx'])
    # corelatii cu decalaj: BET ziua t vs S&P ziua t-1 (informatia americana ajunge a doua zi la BVB)
    lag1 = r['bet'].corr(r['spx'].shift(1))
    lead1 = r['bet'].corr(r['spx'].shift(-1))
    wk = np.log(px.resample('W-FRI').last()).diff().dropna()
    return dict(start=px.index[0].date(), end=px.index[-1].date(), T=T,
                sr_ann_bet=np.sqrt(252) * sr['bet'], sr_ann_spx=np.sqrt(252) * sr['spx'],
                diff_ann=d_obs, rho=rho, z_jkm=z_jkm, p_jkm=2 * stats.norm.sf(abs(z_jkm)),
                boot_ci=(np.quantile(diffs, 0.025), np.quantile(diffs, 0.975)),
                boot_p=2 * min((diffs <= 0).mean(), (diffs >= 0).mean()),
                corr_lag0=r['bet'].corr(r['spx']), corr_lag1=lag1, corr_lead1=lead1,
                corr_sum3=r['bet'].corr(r['spx']) + lag1 + lead1,   # ~ corelatia saptamanala; nu este o corelatie
                corr_weekly=wk['bet'].corr(wk['spx']))


# =============================================================================
# B11: verificarea unui model -- GARCH(1,1) cu inovatii t, estimat pe S&P 500
# =============================================================================
def garch_check(n_paths=200, lags=(1, 20, 100, 250), frac=0.02):
    """GARCH(1,1)-t pe S&P 500; 200 traiectorii simulate; benzi 5-95% pentru fapte stilizate."""
    from arch import arch_model
    r = 100 * rets['sp500']
    am = arch_model(r, mean='Constant', vol='GARCH', p=1, q=1, dist='t')
    res = am.fit(disp='off')
    from arch.univariate import StudentsT
    am.distribution = StudentsT(seed=np.random.default_rng(SEED))   # simulari reproductibile
    n = len(r)
    k = int(frac * n)

    def facts(x):
        x = pd.Series(np.asarray(x))
        a = x.abs()
        return dict(exkurt=stats.kurtosis(x), **{f'acf{j}': a.autocorr(j) for j in lags},
                    hill=hill_estimator(a.values, k), L1=x.corr(a.shift(-1)))

    data = facts(r.values)
    sims = [facts(am.simulate(res.params, nobs=n, burn=1000)['data'].values) for _ in range(n_paths)]
    sims = pd.DataFrame(sims)
    q05, q50, q95 = sims.quantile(0.05), sims.quantile(0.5), sims.quantile(0.95)
    table = pd.DataFrame({'data': pd.Series(data), 'q05': q05, 'median': q50, 'q95': q95})
    table['reproduced'] = (table['data'] >= table['q05']) & (table['data'] <= table['q95'])
    # grafic: ACF |r| date vs 20 de traiectorii
    K = np.arange(1, 251)
    data_curve = [r.abs().autocorr(j) for j in K]
    curves = []
    for _ in range(20):
        s_ = pd.Series(am.simulate(res.params, nobs=n, burn=1000)['data'].values).abs()
        curves.append([s_.autocorr(j) for j in K])
    curves = np.array(curves)
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.fill_between(K, np.quantile(curves, 0.05, axis=0), np.quantile(curves, 0.95, axis=0), color=IDAred,
                    alpha=0.15, lw=0, label='GARCH(1,1)-t simulations: 5%-95%')
    ax.plot(K, np.median(curves, axis=0), color=IDAred, lw=1.1, label='GARCH(1,1)-t simulations: median')
    ax.plot(K, data_curve, color=MainBlue, lw=1.1, label='S&P 500 data')
    ax.set_xscale('log')
    ax.set_xlabel('Lag $k$ (days, log scale)')
    ax.set_ylabel('ACF of $|r_t|$')
    ax.set_title('Does GARCH(1,1)-t reproduce the long memory of volatility?', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch1_sem_garch_check')
    a_, b_, nu_ = res.params['alpha[1]'], res.params['beta[1]'], res.params['nu']
    kappa = 3 * (nu_ - 2) / (nu_ - 4)                     # E z^4 pentru t standardizat
    return dict(params=res.params.round(4).to_dict(), persistence=a_ + b_,
                fourth_moment_cond=(a_ + b_) ** 2 + (kappa - 1) * a_ ** 2,
                table=table, n_paths=n_paths, k=k)


def garch_normal_sp500():
    """GARCH(1,1) cu inovatii cu distributie Normala pe S&P 500: kurtosisul implicat de parametrii estimati."""
    from arch import arch_model
    res = arch_model(100 * rets['sp500'], mean='Constant', vol='GARCH', p=1, q=1, dist='normal').fit(disp='off')
    a, b = res.params['alpha[1]'], res.params['beta[1]']
    return dict(alpha=a, beta=b, **garch_kurtosis(a, b))


# =============================================================================
# C1: autocorelatia BET-TR inainte si dupa reclasificarea FTSE (21.09.2020)
# =============================================================================
def rho_robust(r):
    """rho_1 si EE robusta sub H0: rho_1 = 0 (diferenta de martingala); pentru benzi in jurul lui 0."""
    e = (r - r.mean()).values
    s2 = np.sum(e ** 2)
    rho = np.sum(e[1:] * e[:-1]) / s2
    se = np.sqrt(np.sum(e[1:] ** 2 * e[:-1] ** 2)) / s2
    return rho, se


def rho_hac(r):
    """rho_1 ca panta regresiei r_t pe r_{t-1}, cu EE Newey-West (HAC): valida si cand rho_1 != 0."""
    df = pd.DataFrame({'y': r, 'x': r.shift(1)}).dropna()
    L = int(4 * (len(df) / 100) ** (2 / 9))
    fit = sm.OLS(df['y'], sm.add_constant(df['x'])).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    return fit.params['x'], fit.bse['x']


BLUE_CHIPS = ['TLV.RO', 'SNP.RO', 'BRD.RO', 'TGN.RO', 'FP.RO', 'SNG.RO', 'H2O.RO', 'SNN.RO', 'EL.RO', 'DIGI.RO', 'TEL.RO']


def traded_value_proxy():
    """Valoarea zilnica tranzactionata (lei) a acțiunilor blue-chip BVB din data/market: volum x pret de inchidere."""
    v = []
    for sym in BLUE_CHIPS:
        d = read_market(sym)
        v.append((d['volume'] * d['close']).rename(sym))
    return pd.concat(v, axis=1).sum(axis=1, min_count=1)


def fig_bettr_rolling_acf(window=250, split='2020-09-21'):
    r = rets['bettr']
    vals, lo, hi, idx = [], [], [], []
    for end in range(window, len(r) + 1, 5):
        w = r.iloc[end - window:end]
        rho, se = rho_robust(w)
        vals.append(rho); lo.append(rho - 1.96 * se); hi.append(rho + 1.96 * se); idx.append(w.index[-1])
    roll = pd.Series(vals, index=idx)
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.plot(idx, vals, color=IDAred, lw=1.0, label='Rolling lag-1 autocorrelation (250 days)')
    ax.fill_between(idx, lo, hi, color=IDAred, alpha=0.15, lw=0, label='$\\pm1.96$ robust SE under $\\rho_1 = 0$')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.axvline(pd.Timestamp(split), color=MainBlue, ls='--', lw=0.9, label='FTSE Russell reclassification (Sep 2020)')
    ax.set_ylabel('$\\hat\\rho_1$')
    ax.set_title('BET-TR: did the lag-1 autocorrelation fall after the upgrade?', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    plt.tight_layout()
    save_fig('ch1_sem_bettr_rolling_acf')
    pre, post = r.loc[:split].iloc[:-1], r.loc[split:]
    rp, sp = rho_hac(pre)
    rq, sq = rho_hac(post)
    z = (rp - rq) / np.sqrt(sp ** 2 + sq ** 2)
    df = pd.DataFrame({'y': r, 'x': r.shift(1)}).dropna()
    df['post'] = (df.index >= pd.Timestamp(split)).astype(float)
    df['x_post'] = df['x'] * df['post']
    fit = sm.OLS(df['y'], sm.add_constant(df[['x', 'post', 'x_post']])).fit(cov_type='HAC', cov_kwds={'maxlags': 10})
    # lichiditate: valoarea tranzactionata a blue-chip-urilor, medie mobila pe 250 de zile (log)
    tv = traded_value_proxy().reindex(r.index)
    liq = np.log(tv.rolling(window, min_periods=200).mean()).reindex(roll.index)
    ok = liq.notna()
    corr_liq = float(np.corrcoef(roll[ok], liq[ok])[0, 1])
    tv_pre, tv_post = tv.loc[pre.index].median(), tv.loc[post.index].median()
    return dict(pre=(rp, sp, len(pre), pre.index[0].date(), pre.index[-1].date()),
                post=(rq, sq, len(post), post.index[0].date(), post.index[-1].date()),
                z=z, p=2 * stats.norm.sf(abs(z)), hac_diff=fit.params['x_post'], hac_se=fit.bse['x_post'],
                hac_p=fit.pvalues['x_post'], share_sig=float(np.mean(np.array(lo) > 0)),
                corr_rho_liquidity=corr_liq, tv_median_pre_mn=tv_pre / 1e6, tv_median_post_mn=tv_post / 1e6)


# =============================================================================
# A4: drawdown-ul maxim asteptat al unei miscari browniene fara drift (Magdon-Ismail et al. 2004)
# =============================================================================
def mdd_brownian(assets=('gold', 'sp500', 'btc')):
    """E[MDD] = sqrt(pi/2) sigma sqrt(T) pentru log-pret, mu = 0; comparat cu MDD observat (log)."""
    rows = []
    for a in assets:
        c = closes[a]
        Y = (c.index[-1] - c.index[0]).days / 365.25
        sig = rets[a].std() * np.sqrt(PERIODS[a])
        e = np.sqrt(np.pi / 2) * sig * np.sqrt(Y)
        mdd = float(np.log(c / c.cummax()).min())
        rows.append({'asset': LABELS[a], 'years': Y, 'sigma': sig, 'mu_log': rets[a].mean() * PERIODS[a],
                     'E_mdd_log': e, 'pct_fall_at_mean_log_dd': 100 * (1 - np.exp(-e)), 'mdd_log': mdd,   # 1-exp(-E[D]) nu este E[MDD] procentual (Jensen)
                     'mdd_pct': 100 * (np.exp(mdd) - 1)})
    return pd.DataFrame(rows).set_index('asset')


# =============================================================================
# B6: EUR/RON pe regimuri -- ruptura de varianta si testul egalitatii lui rho_1 (EE robuste)
# =============================================================================
def eurron_regimes(periods=(('2005-07-01', '2011-12-31'), ('2012-01-01', '2019-12-31'), ('2020-01-01', '2026-12-31'))):
    r = rets['eurron']
    rows = []
    for a, b in periods:
        x = (r[a:b] - r[a:b].mean()).values
        rho, se = rho_hac(r[a:b])        # EE HAC: valida si pentru rho_1 != 0 (tau_1 e varianta sub rho_1 = 0)
        rows.append({'period': f'{a[:4]}-{b[:4]}', 'rho1': rho, 'se_hac': se,
                     'se_iid': 1 / np.sqrt(len(x)), 'vol_pct': 100 * x.std() * np.sqrt(252),
                     'exkurt': stats.kurtosis(x)})
    t = pd.DataFrame(rows).set_index('period')
    w = 1 / t['se_hac'] ** 2
    rbar = np.sum(w * t['rho1']) / np.sum(w)
    wald = float(np.sum(w * (t['rho1'] - rbar) ** 2))
    j, it = cusum_squares_break(r.values)
    return dict(table=t, wald=wald, wald_p=float(stats.chi2.sf(wald, len(t) - 1)),
                break_date=r.index[j].date(), it_stat=it)


# =============================================================================
# B15: parametrul de memorie d al lui |r_t| (Whittle local), inainte si dupa ruptura de varianta
# =============================================================================
def memory_before_after(assets=('sp500', 'bettr', 'btc'), power=0.65):
    rows = []
    for a in assets:
        r = rets[a]
        x = np.abs(r.values)
        d, se = local_whittle(x, int(len(x) ** power))
        j, _ = cusum_squares_break(r.values)
        d1, s1 = local_whittle(x[:j + 1], int((j + 1) ** power))
        d2, s2 = local_whittle(x[j + 1:], int((len(x) - j - 1) ** power))
        rows.append({'asset': LABELS[a], 'm': int(len(x) ** power), 'd': d, 'se': se,
                     'ci': (d - 1.96 * se, d + 1.96 * se), 'break': r.index[j].date(),
                     'd_before': d1, 'se_before': s1, 'd_after': d2, 'se_after': s2,
                     'z_change': (d2 - d1) / np.sqrt(s1 ** 2 + s2 ** 2)})
    return pd.DataFrame(rows).set_index('asset')


if __name__ == '__main__':
    import pprint
    pd.set_option('display.width', 200)
    np.set_printoptions(precision=4, suppress=True)
    print('A Hill real BET-TR k=10'); pprint.pprint(hill_by_hand())
    print('A Markov p=0.9'); pprint.pprint(markov_mixture(0.9))
    print('A GARCH'); pprint.pprint(garch_kurtosis(0.10, 0.85)); pprint.pprint(garch_kurtosis(0.10, 0.88)); pprint.pprint(garch_normal_sp500())
    print('B9 robust LB'); fig_robust_acf(); print(robust_lb_table())
    print('B10'); pprint.pprint(fig_kurtosis_expanding())
    print('B11'); print(hill_tails().T); fig_hill_tails()
    print('B5 chart'); print(fig_leverage_ro_crypto().loc[[1, 5]].round(3))
    print('B12'); [pprint.pprint((a, leverage_regression(a))) for a in ('sp500', 'bettr', 'btc', 'eurron')]
    print('B13'); pprint.pprint(bettr_vs_sp500())
    print('B14'); gc = garch_check(); print(gc['params'], gc['persistence']); print(gc['table'].round(3))
    print('C1'); pprint.pprint(fig_bettr_rolling_acf())
    print('A4 MDD'); print(mdd_brownian().round(3))
    print('B6'); pprint.pprint(eurron_regimes())
    print('B15'); print(memory_before_after().round(3).T)

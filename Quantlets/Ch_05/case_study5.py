"""
case_study5.py -- Capitolul 5, studiul de caz: modele bazate pe un cvasi-scor (Blasques, Francq & Laurent, 2023)
==============================================================================================================
Replicarea Sectiunii 5.1 din lucrare pe cele 11 actiuni din data/market care erau in S&P 500 in februarie 2019
si au cel putin 4000 de randamente zilnice in fereastra 3 ianuarie 1995 (sau mai tarziu) -- 28 februarie 2019.
  * randamente log zilnice in procente (adjusted_close), medie AR(1) (nota 6 din lucrare);
  * X_t = VIX_t^2 / 252 (patratul VIX convertit la orizont zilnic), preturile unite cu VIX pe zilele comune;
  * QSD GARCH(1,1)-t, ec. (31) cu Psi din ec. (32), c = 1000, zeta in (-1, 1/2), inovatii Student-t
    standardizate cu 1/xi grade de libertate; GARCH(1,1)-t (zeta = 0) si Beta-t-GARCH (zeta = xi);
  * verosimilitate maxima; testele LR pentru H0: zeta = 0 si H0: xi = zeta, chi2(1), 5%.
Grafice: ch5_qsd_gap (xi - zeta pe actiuni, ca Fig. 2), ch5_qsd_nic (curbe de impact al stirilor, ca Fig. 3).
Iesire: ch5_case_qsd.csv, ch5_case_qsd.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, optimize
from scipy.special import gammaln
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
from mfm_data import read_market                                                    # noqa: E402
from generate_all_charts import save_fig, MainBlue, IDAred, Forest, TABLE_DIR       # noqa: E402

QSD_STOCKS = {'AAPL': 'Apple', 'AMZN': 'Amazon', 'BAC': 'Bank of America', 'C': 'Citigroup', 'CSCO': 'Cisco',
              'GS': 'Goldman Sachs', 'JPM': 'JPMorgan', 'MSFT': 'Microsoft', 'MS': 'Morgan Stanley',
              'NVDA': 'Nvidia', 'WFC': 'Wells Fargo'}
QSD_START, QSD_END = '1995-01-03', '2019-02-28'
QSD_C = 1000.0
QSD = {}


def qsd_data(ticker):
    """Randamente log (%) ale actiunii si X_t = VIX_t^2/252, pe zilele comune (join pe preturi)."""
    p = read_market(f'{ticker}.US')['adjusted_close'].rename('p')
    v = read_market('VIX.INDX')['close'].rename('vix')
    df = pd.concat([p, v], axis=1, join='inner').loc[:QSD_END].dropna()
    df = df[(df.index.dayofweek < 5) & (df.p > 0)]
    before = df.index[df.index < QSD_START]
    if len(before):
        df = df.loc[before[-1]:]                                # ultimul pret inainte de 3 ianuarie 1995
    r = 100 * np.log(df.p).diff()
    x = df.vix ** 2 / 252
    out = pd.DataFrame({'r': r, 'x': x}).iloc[1:]
    return out


def psi(x, c=QSD_C):
    """Ec. (32): Psi(x) = x (1 - e^{-cx}) / (1 + e^{-cx}) = x tanh(cx/2), aproximare neteda a lui |x|."""
    return x * np.tanh(c * x / 2)


def qsd_filter(theta, r, x):
    """Medie AR(1) si recursia (31); intoarce reziduurile y_t, f_t si eps_t."""
    mu, phi, om, vp, al, be, xi, ze = theta
    y = r[1:] - mu - phi * r[:-1]
    xx = x[1:]                                                  # X_t aliniat cu y_t: f_{t+1} foloseste X_t
    n = len(y)
    f = np.empty(n)
    f[0] = np.var(y)
    for t in range(n - 1):
        e2 = y[t] * y[t] / f[t]
        w = psi((1 + ze) / (1 - 2 * ze + ze * e2))
        f[t + 1] = om + vp * xx[t] + al * w * e2 * f[t] + be * f[t]
    return y, f, y / np.sqrt(f)


def qsd_negll(theta, r, x):
    """Minus log-verosimilitatea: Student-t standardizat cu nu = 1/xi grade de libertate."""
    xi = theta[6]
    if not (0 < xi < 0.5) or not (-1 < theta[7] < 0.5) or theta[2] <= 0 or min(theta[3:6]) < 0:
        return 1e10
    y, f, e = qsd_filter(theta, r, x)
    if not np.all(np.isfinite(f)) or np.any(f <= 0):
        return 1e10
    nu = 1 / xi
    ll = (gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(np.pi * (nu - 2)) - 0.5 * np.log(f)
          - (nu + 1) / 2 * np.log1p(e ** 2 / (nu - 2)))
    return -ll.sum()


def fit_qsd(r, x, model, start=None):
    """model: 'GARCH-t' (zeta = 0), 'Beta-t-GARCH' (zeta = xi) sau 'QSD' (zeta liber)."""
    def full(p):
        if model == 'GARCH-t':
            return np.r_[p, 0.0]
        if model == 'Beta-t-GARCH':
            return np.r_[p, p[6]]
        return p
    bnd = [(-1, 1), (-0.5, 0.5), (1e-6, None), (0, None), (0, 1), (0, 1), (0.01, 0.49)]
    if model == 'QSD':
        bnd = bnd + [(-0.99, 0.49)]
    starts = start if start is not None else [np.array([0.05, 0.0, 0.05, 0.1, 0.06, 0.85, 0.15, 0.1])]
    best = None
    for s0 in starts:
        s0 = np.asarray(s0, float)[:len(bnd)]
        res = optimize.minimize(lambda p: qsd_negll(full(p), r, x), s0, method='L-BFGS-B', bounds=bnd)
        res = optimize.minimize(lambda p: qsd_negll(full(p), r, x), res.x, method='Nelder-Mead',
                                options={'maxiter': 4000, 'xatol': 1e-7, 'fatol': 1e-7})
        if best is None or res.fun < best.fun:
            best = res
    return full(best.x), -best.fun


def qsd_se(theta, r, x, h=1e-4):
    """Erori standard din inversa hessianei numerice (modelul QSD nerestrictionat)."""
    k = len(theta)
    H = np.zeros((k, k))
    step = h * np.maximum(np.abs(theta), 1e-2)
    for i in range(k):
        for j in range(i, k):
            ei, ej = np.eye(k)[i] * step[i], np.eye(k)[j] * step[j]
            H[i, j] = H[j, i] = (qsd_negll(theta + ei + ej, r, x) - qsd_negll(theta + ei - ej, r, x)
                                 - qsd_negll(theta - ei + ej, r, x) + qsd_negll(theta - ei - ej, r, x)) / (4 * step[i] * step[j])
    return np.sqrt(np.diag(np.linalg.inv(H)))


def qsd_estimates():
    """Cele trei modele pe fiecare actiune; testele LR ca in Tabelele 4--5 din lucrare."""
    rows = []
    for tk, name in QSD_STOCKS.items():
        d = qsd_data(tk)
        r, x = d.r.values, d.x.values
        g, llg = fit_qsd(r, x, 'GARCH-t')
        b, llb = fit_qsd(r, x, 'Beta-t-GARCH', start=[g[:7]])
        q, llq = fit_qsd(r, x, 'QSD', start=[np.r_[b[:7], b[6]]] + [np.r_[g[:7], z] for z in (0.01, 0.03, 0.06, 0.1)])
        # modelele restrictionate reestimate si din solutia QSD (maximul global al fiecarei verosimilitati)
        g2, llg2 = fit_qsd(r, x, 'GARCH-t', start=[q[:7]])
        b2, llb2 = fit_qsd(r, x, 'Beta-t-GARCH', start=[q[:7]])
        if llg2 > llg:
            g, llg = g2, llg2
        if llb2 > llb:
            b, llb = b2, llb2
        se = qsd_se(q, r, x)
        lr0, lrx = 2 * (llq - llg), 2 * (llq - llb)
        rows.append(dict(ticker=tk, name=name, first=str(d.index[0].date()), last=str(d.index[-1].date()),
                         T=len(d) - 1, xi_garch=g[6], xi_beta=b[6], xi=q[6], zeta=q[7], se_xi=se[6], se_zeta=se[7],
                         alpha=q[4], beta=q[5], varpi=q[3], ll_garch=llg, ll_beta=llb, ll_qsd=llq,
                         lr_zeta0=lr0, p_zeta0=stats.chi2.sf(max(lr0, 0), 1),
                         lr_xi_zeta=lrx, p_xi_zeta=stats.chi2.sf(max(lrx, 0), 1)))
        print(tk, round(q[6], 3), round(q[7], 3), round(lr0, 2), round(lrx, 2))
    t = pd.DataFrame(rows).set_index('ticker')
    t.to_csv(os.path.join(TABLE_DIR, 'ch5_case_qsd.csv'))
    QSD.update(dict(n=len(t), rej_zeta0=int((t.p_zeta0 < 0.05).sum()), rej_xi_zeta=int((t.p_xi_zeta < 0.05).sum()),
                    n_zeta_pos=int((t.zeta > 0).sum()), n_xi_gt_zeta=int((t.xi > t.zeta).sum()),
                    n_sig_xi_gt_zeta=int(((t.p_xi_zeta < 0.05) & (t.xi > t.zeta)).sum()),
                    med_inv_zeta=float(np.median(1 / t.zeta[t.zeta > 0])) if (t.zeta > 0).any() else float('nan'),
                    med_inv_xi_beta=float(np.median(1 / t.xi_beta)),
                    med_zeta=float(t.zeta.median()), med_xi=float(t.xi.median()), med_xi_beta=float(t.xi_beta.median()),
                    min_T=int(t['T'].min()), max_T=int(t['T'].max())))
    with open(os.path.join(TABLE_DIR, 'ch5_case_qsd.json'), 'w') as fh:
        json.dump(QSD, fh, indent=1)
    return t


def fig_qsd_gap(t):
    """xi - zeta pentru fiecare actiune (ca Fig. 2 din lucrare): plin = LR(xi = zeta) semnificativ la 5%."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    t = t.sort_index()
    pos = np.arange(len(t))
    gap = t.xi - t.zeta
    sig = t.p_xi_zeta < 0.05
    ax.axhline(0, color='#1F2A44', lw=0.6)
    ax.vlines(pos, 0, gap, color=MainBlue, lw=1.0)
    ax.scatter(pos[sig], gap[sig], s=46, color=MainBlue, zorder=3,
               label=r'$\hat\xi - \hat\zeta$, LR test of $\xi = \zeta$ significant at 5%')
    ax.scatter(pos[~sig], gap[~sig], s=46, facecolor='none', edgecolor=MainBlue, lw=1.2, zorder=3,
               label=r'$\hat\xi - \hat\zeta$, not significant')
    ax.scatter(pos + 0.2, t.zeta, s=30, marker='D', color=IDAred, zorder=3,
               label=r'$\hat\zeta$ (downweighting; 0 = GARCH-t)')
    ax.set_xticks(pos)
    ax.set_xticklabels([f'{n} ({k})' for k, n in zip(t.index, t.name)], fontsize=7.5, rotation=30, ha='right')
    ax.set_ylabel(r'QSD GARCH(1,1)-t estimate')
    ax.set_title(f'Quasi score-driven GARCH(1,1)-t, 11 S&P 500 stocks, {QSD_START[:4]}\u2013{QSD_END[:4]}: '
                 '\n' r'tail parameter $\hat\xi$ vs downweighting $\hat\zeta$', color='black')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.36), ncol=3, frameon=False)
    save_fig('ch5_qsd_gap')


def fig_qsd_nic(t):
    """Curbe de impact al stirilor eps -> Psi((1+z)/(1-2z+z eps^2)) eps^2 (ca Fig. 3 din lucrare),
    la cuantilele 5, 50 si 95% ale estimarilor pe cele 11 actiuni."""
    e = np.linspace(-10, 10, 801)
    nic = lambda z: psi((1 + z) / (1 - 2 * z + z * e ** 2)) * e ** 2   # noqa: E731
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.plot(e, e ** 2, color=Forest, lw=1.6, ls='--', label=r'GARCH(1,1)-t ($\zeta = 0$)')
    qs = [0.05, 0.5, 0.95]
    for m, col, c, ls, name in [('beta', 'xi_beta', IDAred, ':', r'Beta-t-GARCH, $\zeta = \hat\xi$'),
                                ('qsd', 'zeta', MainBlue, '-', r'QSD GARCH(1,1)-t, $\hat\zeta$')]:
        z5, z50, z95 = np.quantile(t[col], qs)
        ax.plot(e, nic(z50), color=c, ls=ls, lw=2.2, label=fr'{name}, median over stocks ({z50:.3f})')
        ax.plot(e, nic(z5), color=c, ls=ls, lw=0.9, label=fr'{name}, 5% and 95% quantiles ({z5:.3f}, {z95:.3f})')
        ax.plot(e, nic(z95), color=c, ls=ls, lw=0.9, label='_nolegend_')
    ax.set_ylim(0, 40)
    ax.set_xlabel(r'Standardised shock $\epsilon_t$')
    ax.set_ylabel(r'Impact on $f_{t+1}$ (units of $\alpha f_t$)')
    ax.set_title('News impact curves, 11 S&P 500 stocks (quantiles over the stocks)', color='black')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False)
    save_fig('ch5_qsd_nic')
    QSD['nic'] = {f'{m}_{int(qq * 100)}_{s}': float(nic(z)[np.argmin(np.abs(e - s))])
                  for m, col in [('beta', 'xi_beta'), ('qsd', 'zeta')] for qq in qs
                  for z in [np.quantile(t[col], qq)] for s in [3, 5, 10]}
    with open(os.path.join(TABLE_DIR, 'ch5_case_qsd.json'), 'w') as fh:
        json.dump(QSD, fh, indent=1)


if __name__ == '__main__':
    tab = qsd_estimates()
    print(tab.round(4).T)
    fig_qsd_gap(tab)
    fig_qsd_nic(tab)
    print(json.dumps(QSD, indent=1))

"""
ai_discovery_case.py -- Capitolul 14, secțiunea "AI for Scientific Discovery": mini-studiul de caz
==================================================================================================
Ipoteza (propusă tipic de un asistent AI): paritatea Chronos-2 cu log-HAR la prognoza varianței realizate
vine din memorarea datelor de pre-antrenare. Implicația testabilă: diferențialul de pierdere
d_t = QLIKE(Chronos-2) - QLIKE(log-HAR) ar trebui să crească (avantajul să dispară) după 3.11.2025.
  * H0: E[d | după] = E[d | înainte]; t Newey--West pentru diferența mediilor (regresia lui d pe o dummy)
  * puterea: efectul minim detectabil (MDE) al lui beta_1 la 5% bilateral și putere 80%,
    MDE = (z_0.975 + z_0.80) * se_HAC(beta_1); și numărul de zile de după publicare necesar pentru a detecta
    o schimbare egală cu diferența medie dinainte de publicare
Folosește prognozele salvate în ch14_rv.csv (nu rulează din nou modelele).
Ieșire: ai_discovery_case.json și graficul ch14_ai_prepost (charts/)
"""

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RELEASE = '2025-11-03'


def qlike(rv, h):
    x = rv / h
    return x - np.log(x) - 1


def lrv(x, lags):
    """Varianța pe termen lung (Newey--West) a unei serii."""
    x = np.asarray(x) - np.mean(x)
    T = len(x)
    s = x @ x / T
    for L in range(1, lags + 1):
        s += 2 * (1 - L / (lags + 1)) * (x[L:] @ x[:-L]) / T
    return s


def main():
    df = pd.read_csv(os.path.join(HERE, 'ch14_rv.csv'), index_col='day', parse_dates=True)
    d = qlike(df['RV'], df['Chronos-2']) - qlike(df['RV'], df['logHAR'])
    post = d.index >= RELEASE
    n = len(d)
    lags = int(np.floor(4 * (n / 100) ** (2 / 9)))
    dpre, dpost = d[~post], d[post]
    # regresia lui d pe [1, dummy_post] cu erori HAC
    X = np.column_stack([np.ones(n), post.astype(float)])
    b = np.linalg.lstsq(X, d.values, rcond=None)[0]
    u = d.values - X @ b
    g = X * u[:, None]
    S = g.T @ g / n
    for L in range(1, lags + 1):
        G = g[L:].T @ g[:-L] / n
        S += (1 - L / (lags + 1)) * (G + G.T)
    Zi = np.linalg.inv(X.T @ X / n)
    V = Zi @ S @ Zi / n
    t_diff = b[1] / np.sqrt(V[1, 1])
    s_post = np.sqrt(lrv(dpost.values, lags))
    s_pre = np.sqrt(lrv(dpre.values, lags))
    z = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)
    # MDE of the break coefficient beta_1 (the tested pre/post difference): z * HAC s.e. of beta_1
    mde = z * np.sqrt(V[1, 1])
    # MDE of the post-release mean alone (a different estimand, reported for comparison)
    mde_mean = z * s_post / np.sqrt(len(dpost))
    # post-release days needed to detect beta_1 = |pre-release mean| with n_pre fixed:
    # z^2 (s_pre^2 / n_pre + s_post^2 / n_post) = gap^2  (pre and post blocks treated as independent)
    gap = abs(dpre.mean())
    den = (gap / z) ** 2 - s_pre ** 2 / len(dpre)
    need = s_post ** 2 / den if den > 0 else np.inf
    floor = z * s_pre / np.sqrt(len(dpre))      # MDE with an infinitely long post-release window
    out = {
        'n': int(n), 'n_pre': int((~post).sum()), 'n_post': int(post.sum()), 'lags': lags,
        'qlike_c2': float(qlike(df['RV'], df['Chronos-2']).mean()),
        'qlike_lhar': float(qlike(df['RV'], df['logHAR']).mean()),
        'mean_pre': float(dpre.mean()), 'mean_post': float(dpost.mean()),
        'diff': float(b[1]), 't_diff': float(t_diff), 'p_diff': float(2 * (1 - stats.norm.cdf(abs(t_diff)))),
        'se_diff': float(np.sqrt(V[1, 1])), 'mde_post': float(mde), 'mde_mean_post': float(mde_mean),
        'mde_floor': float(floor), 'mde_ratio_qlike': float(mde / qlike(df['RV'], df['logHAR']).mean()),
        'days_needed': float(need), 'years_needed': float(need / 252),
    }
    with open(os.path.join(HERE, 'ai_discovery_case.json'), 'w') as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))
    fig_prepost(dpre, dpost, b[1], np.sqrt(V[1, 1]), mde, lags)


def fig_prepost(dpre, dpost, diff, se_diff, mde, lags):
    """Pre- and post-release means of d_t and their difference, with HAC 95% intervals and +/- MDE."""
    import sys
    sys.path.insert(0, HERE)
    from generate_all_charts import plt, MainBlue, IDAred, Orange, Forest, Gray, save_fig, legend_outside_bottom
    rows = [('Before 3 Nov 2025\n(%d days)' % len(dpre), dpre.mean(), np.sqrt(lrv(dpre.values, lags) / len(dpre)), Forest),
            ('After 3 Nov 2025\n(%d days)' % len(dpost), dpost.mean(), np.sqrt(lrv(dpost.values, lags) / len(dpost)), Orange),
            ('Change $\\hat\\beta_1$\n(after minus before)', diff, se_diff, MainBlue)]
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for i, (lab, m, se, c) in enumerate(rows):
        ax.plot([m - 1.96 * se, m + 1.96 * se], [i, i], color=c, lw=2.4, solid_capstyle='butt')
        ax.scatter(m, i, color=c, s=34, zorder=3)
    ax.scatter([-mde, mde], [2, 2], marker='|', s=260, color=IDAred, zorder=4, label='$\\pm$MDE of $\\beta_1$ (80% power)')
    ax.plot([], [], color='black', lw=2.4, label='HAC 95% interval')
    ax.axvline(0, color=Gray, lw=0.7, ls='--')
    ax.set_yticks(range(3), [r[0] for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Mean QLIKE differential $d_t$ (Chronos-2 minus log-HAR)')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch14_ai_prepost')


if __name__ == '__main__':
    main()

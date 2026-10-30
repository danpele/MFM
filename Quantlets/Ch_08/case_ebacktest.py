"""
Case study (Chapter 8): e-backtesting of ES 2.5% forecasts
==========================================================
Wang, Wang & Ziegel (2026), E-backtesting, Management Science 72(6), 4952-4973,
doi:10.1287/mnsc.2023.01659.

Course replication on the chapter's own one-day-ahead forecasts (rolling window of 1000 days,
models HS, Normal, Student-t, GARCH-t, FHS, GARCH-EVT; mfm_data.get_forecasts):
  e-statistic for (ES, VaR) at tail probability 2.5%:  e_t = (L_t - z_t)_+ / (0.025 (r_t - z_t)),
  z_t = VaR 2.5% forecast, r_t = ES 2.5% forecast, L_t = realised loss.
  e-process  M_t = prod_s (1 - lam_s + lam_s e_s),  lam_s in [0, 1/2] chosen from past data only:
    GREE: past e-values (forecasts and losses), GREL: past losses at today's forecast,
    GREM: average of the two e-processes (the paper's default).
  Betting window: past 500 days (the paper's choice); Taylor approximation of the optimal lambda
  (the paper's eq. 15 / Appendix A).  Evidence thresholds 2, 5, 10 (Ville: P(sup M >= 1/a) <= a).
  Null hypothesis (Wang, Wang & Ziegel, Sec. 4.2): for every t, z_t = VaR_t (correct VaR), r_t >= ES_t and r_t > z_t,
  with forecasts known at t-1. A wrong VaR can give E[e_t | F_{t-1}] > 1 even with the correct ES, so the test is an
  ES test conditional on the VaR hypothesis.
  Monotonicity: for a fixed loss and VaR, e_t decreases in r_t. The adaptive GREE/GREL/GREM processes are not monotone
  in the ES forecasts, because the bets lam_s are estimated from past e-values; lower maxima with the ES raised by 10%
  are an empirical result of this sample.
Writes ch8_ebacktest.json and charts/ch8_ebacktest.{pdf,png}.
Modelling Financial Markets - Daniel Traian PELE
"""
import os
import sys
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import mfm_data as M  # noqa: E402

P_TAIL = 0.025          # ES 2.5%
WIN = 500               # betting window (past days)
GAMMA = 0.5             # upper bound for lambda
THRESH = (2, 5, 10)
YMAX = 1e6              # upper limit of the chart's y axis; larger values are drawn at the top edge
ASSETS = ('sp500', 'bet')
MODELS = M.MODELS


def e_es(L, r, z, a=P_TAIL):
    """Backtest e-statistic for (ES, VaR) at tail probability a."""
    L, r, z = map(np.asarray, (L, r, z))
    d = a * (r - z)
    with np.errstate(divide='ignore', invalid='ignore'):
        e = np.maximum(L - z, 0.0) / d
    e = np.where(d > 0, e, np.where(np.maximum(L - z, 0) > 0, np.inf, 1.0))
    return e


def lam_taylor(e_past):
    """Taylor-approximated growth-optimal lambda from past e-values, truncated to [0, GAMMA]."""
    n = len(e_past)
    if n == 0:
        return 0.0
    den = np.sum((e_past - 1.0) ** 2)
    if den <= 0:
        return 0.0
    return float(np.clip((np.sum(e_past) - n) / den, 0.0, GAMMA))


def e_processes(L_hist, idx_eval, r, z, a=P_TAIL, win=WIN):
    """GREE, GREL and GREM e-processes on the evaluation days.

    L_hist: full loss series (Series, includes the days before the evaluation sample);
    idx_eval: evaluation dates; r, z: ES and VaR forecasts on idx_eval."""
    pos = L_hist.index.get_indexer(idx_eval)
    Lall = L_hist.values
    L = Lall[pos]
    e = e_es(L, r, z, a)
    T = len(e)
    lam_ee = np.zeros(T)
    lam_el = np.zeros(T)
    for t in range(T):
        lam_ee[t] = lam_taylor(e[max(0, t - win):t])
        past = Lall[max(0, pos[t] - win):pos[t]]
        lam_el[t] = lam_taylor(e_es(past, np.full(len(past), r[t]), np.full(len(past), z[t]), a))
    M_ee = np.cumprod(1 - lam_ee + lam_ee * e)
    M_el = np.cumprod(1 - lam_el + lam_el * e)
    return dict(e=e, gree=M_ee, grel=M_el, grem=0.5 * (M_ee + M_el), lam_ee=lam_ee, lam_el=lam_el)


def first_cross(Mt, idx, c):
    k = np.argmax(Mt >= c)
    if Mt[k] < c:
        return None
    return dict(day=int(k + 1), date=str(idx[k].date()))


def run_asset(name, scale_es=1.0):
    frames = M.get_forecasts(name)[0]
    r_all = M.load_returns(name).dropna()
    L_hist = -r_all
    out = {}
    for m in MODELS:
        df = frames[m]
        ok = df[['VaR2.5', 'ES2.5', 'L']].notna().all(axis=1)
        if not ok.all():
            out[m] = dict(status='withheld', reason='incomplete GARCH forecasts', n_missing=int((~ok).sum()))
            continue
        z = df['VaR2.5'].values
        r = scale_es * df['ES2.5'].values          # scale_es = 1.10: the paper's over-reported ES (+10%)
        ep = e_processes(L_hist, df.index, r, z)
        rec = dict(status='computed', T=len(df), start=str(df.index[0].date()), end=str(df.index[-1].date()),
                   mean_e=float(np.mean(ep['e'])), n_tail=int((df['L'].values > z).sum()),
                   avg_es_pct=float(100 * np.mean(r)))
        for k in ('gree', 'grel', 'grem'):
            Mt = ep[k]
            rec[k] = dict(final=float(Mt[-1]), max=float(Mt.max()), argmax=str(df.index[int(Mt.argmax())].date()),
                          cross={str(c): first_cross(Mt, df.index, c) for c in THRESH},
                          cross_ymax=first_cross(Mt, df.index, YMAX))
        rec['_paths'] = {k: ep[k] for k in ('gree', 'grel', 'grem')}
        rec['_idx'] = df.index
        out[m] = rec
    return out


def main():
    res = {a: run_asset(a) for a in ASSETS}
    res_up = {a: run_asset(a, scale_es=1.10) for a in ASSETS}
    return res, res_up


def fig_ebacktest(res):
    """GREM e-processes of the six models, S&P 500 and BET, ES 2.5%, log scale; thresholds 2, 5, 10."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import generate_all_charts as g
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, a in zip(axs, ASSETS):
        for m in MODELS:
            x = res[a][m]
            if x['status'] != 'computed':
                continue
            ax.plot(x['_idx'], np.minimum(x['_paths']['grem'], YMAX), color=g.MCOL[m], lw=0.9, label=m)
        ax.axhspan(THRESH[0], THRESH[-1], color=g.BandBlue, alpha=0.45, lw=0)
        for c in THRESH:
            ax.axhline(c, color=g.Navy, ls=':', lw=0.7)
        ax.set_yscale('log')
        ax.set_ylim(0.1, YMAX)
        ax.set_title(f'{M.LABELS[a]}: GREM e-process, ES 2.5%')
        ax.xaxis.set_major_locator(g.mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(g.mdates.DateFormatter('%Y'))
    axs[0].set_ylabel('e-process (log scale)')
    from matplotlib.patches import Patch
    h, l = axs[0].get_legend_handles_labels()
    h.append(Patch(facecolor=g.BandBlue, alpha=0.45, edgecolor=g.Navy, ls=':', lw=0.7))
    l.append('Evidence thresholds 2, 5, 10')
    fig.legend(h, l, loc='lower center', ncol=7, frameon=False, bbox_to_anchor=(0.5, -0.10))
    fig.tight_layout()
    g.save_fig('ch8_ebacktest')


def summary(res, res_up):
    out = dict(paper='Wang, Wang & Ziegel (2026), Management Science 72(6), 4952-4973, doi:10.1287/mnsc.2023.01659',
               p_tail=P_TAIL, window=WIN, gamma=GAMMA, thresholds=list(THRESH), ymax=YMAX, assets={})
    for a in ASSETS:
        out['assets'][a] = {}
        for m in MODELS:
            x = res[a][m]
            if x['status'] != 'computed':
                out['assets'][a][m] = x
                continue
            rec = {k: v for k, v in x.items() if not k.startswith('_')}
            y = res_up[a][m]
            rec['es_plus10'] = {k: y[k] for k in ('gree', 'grel', 'grem')}
            rec['es_plus10']['avg_es_pct'] = y['avg_es_pct']
            out['assets'][a][m] = rec
    return out


if __name__ == '__main__':
    res, res_up = main()
    fig_ebacktest(res)
    S = summary(res, res_up)
    with open(os.path.join(HERE, 'ch8_ebacktest.json'), 'w') as f:
        json.dump(S, f, indent=1)
    for a in ASSETS:
        for m in MODELS:
            x = S['assets'][a][m]
            gm = x['grem']
            print(a, m, 'mean e %.3f' % x['mean_e'], 'avgES %.2f' % x['avg_es_pct'],
                  'GREM final %.3g max %.3g (%s)' % (gm['final'], gm['max'], gm['argmax']),
                  {c: (v['day'], v['date']) if v else None for c, v in gm['cross'].items()},
                  '| +10%%: max %.3g' % x['es_plus10']['grem']['max'],
                  {c: (v['day'] if v else None) for c, v in x['es_plus10']['grem']['cross'].items()})

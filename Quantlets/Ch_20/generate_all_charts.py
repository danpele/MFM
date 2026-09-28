"""
Generator pentru graficele si cifrele Capitolului 20 (capitol special): signaturi si volatilitate realizata
=========================================================================================================
Studiu de caz: metoda lui Gu, Guo, Jacobs, Kaminsky & Li (2024) -- signatura caii augmentate cu timpul,
LASSO in doi pasi si ponderi date de nucleul signaturii -- transferata la prognoza variantei realizate
pe baza de date VOLARE (40 de actiuni americane, 5 futures, 5 perechi valutare).
Prognozele se calculeaza in forecast_panel.py (cache local in data/volare/ch20_cache, nepublicat);
aici: evaluarea (QLIKE, MSE, Diebold-Mariano, Giacomini-White, MCS, Holm/BH), graficele si ch20_results.json.
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sigvol as S   # noqa: E402

if not os.path.isdir(S.VOLARE_DIR):
    S.VOLARE_DIR = os.path.join(HERE, '..', '..', 'data', 'volare')
CACHE = os.path.join(S.VOLARE_DIR, 'ch20_cache')

# Stil standard MFM (identic cu SFM): transparent + ENG + legenda jos
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.6
plt.rcParams['lines.linewidth'] = 1.1
plt.rcParams['legend.facecolor'] = 'none'
plt.rcParams['legend.framealpha'] = 0
plt.rcParams['legend.fontsize'] = 8

# Culori brand
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Gray     = '#7F7F7F'   # doar linii de referinta, benzi, grila
Teal     = '#17A2B8'
COL = {'HAR': MainBlue, 'logHAR': Teal, 'HARQ': Purple, 'SHAR': Amber, 'logHAR-K': Orange,
       'Sig-L': Forest, 'Sig-LK': IDAred}
SHORT = {'HAR': 'HAR', 'logHAR': 'log-HAR', 'HARQ': 'HARQ', 'SHAR': 'SHAR', 'logHAR-K': 'log-HAR-K',
         'Sig-L': 'Sig-L', 'Sig-LK': 'Sig-LK'}
CLASS_LABEL = {'stocks': 'US stocks (40)', 'futures': 'Futures (5)', 'forex': 'FX (5)', 'all': 'All 50 assets'}
PERIODS = {'covid': ('2020-02-20', '2020-04-30'), 'apr2025': ('2025-04-02', '2025-04-30')}
H = S.CFG['HORIZONS']
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
RES = {}


def save_fig(name):
    """Salveaza figura ca PDF si PNG transparent."""
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Plaseaza legenda in afara graficului, jos-centru."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def fig_legend_bottom(fig, axes, ncol=4, y=0.0):
    """O singura legenda sub o figura cu mai multe panouri."""
    h, l = [], []
    for ax in axes:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh)
                l.append(ll)
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def assets():
    return [(k, s) for k in S.CLASSES for s in S.symbols(k)]


def read_fc(kind, sym, h, tag='main'):
    return pd.read_csv(os.path.join(CACHE, tag, f'fc_{kind}_{sym}_h{h}.csv'), index_col=0, parse_dates=True)


def read_info(kind, sym, h, tag='main'):
    return pd.read_csv(os.path.join(CACHE, tag, f'info_{kind}_{sym}_h{h}.csv'), parse_dates=['date'])


# -----------------------------------------------------------------------------
# EVALUARE PE ACTIV
# -----------------------------------------------------------------------------
def eval_asset(kind, sym, h):
    fc = read_fc(kind, sym, h)
    M = S.MODELS
    y = fc.y.values
    QL = pd.DataFrame({m: S.qlike(y, fc[m].values) for m in M}, index=fc.index)
    SE = pd.DataFrame({m: S.mse(y, fc[m].values) for m in M}, index=fc.index)
    out = {'kind': kind, 'sym': sym, 'h': h, 'T': len(fc), 'start': str(fc.index[0].date()), 'end': str(fc.index[-1].date()),
           'ql': QL.mean().to_dict(), 'se': SE.mean().to_dict(),
           'relerr': {m: float(np.mean(np.abs(y - fc[m]) / y)) for m in M}}
    dm = {}
    for b in ['HAR', 'logHAR']:
        for m in M:
            if m == b:
                continue
            tq, pq, _ = S.dm_test(QL[m], QL[b], h)
            tm, pm, _ = S.dm_test(SE[m], SE[b], h)
            dm[f'{m}|{b}'] = {'t_ql': tq, 'p_ql': pq, 't_se': tm, 'p_se': pm}
    out['dm'] = dm
    out['gw'] = {f'{m}|logHAR': S.gw_test(QL[m], QL['logHAR'], h)[1] for m in ['Sig-L', 'Sig-LK', 'logHAR-K']}
    inc_q, pv_q = S.mcs(QL, block=max(h, 10))
    inc_s, pv_s = S.mcs(SE / SE.values.mean(), block=max(h, 10))
    out['mcs_ql'], out['mcs_se'] = inc_q, inc_s
    sub = {}
    for p, (a, b) in PERIODS.items():
        sl = QL.loc[a:b]
        sub[p] = sl.mean().to_dict() if len(sl) else None
    rest = QL.drop(QL.loc[PERIODS['covid'][0]:PERIODS['covid'][1]].index)
    rest = rest.drop(rest.loc[PERIODS['apr2025'][0]:PERIODS['apr2025'][1]].index)
    sub['rest'] = rest.mean().to_dict()
    out['sub'] = sub
    # BPQ insanity filter (robustness)
    fi = S.insanity(fc, M)
    out['ql_filter'] = {m: float(S.qlike(y, fi[m].values).mean()) for m in M}
    out['n_filter'] = {m: int(((fc[m] < fc.lo) | (fc[m] > fc.hi)).sum()) for m in M}
    out['n_explode'] = {m: int((fc[m] > 10 * fc.hi).sum()) for m in M}
    out['max_ratio'] = {m: float((fc[m] / fc.hi).max()) for m in M}
    # variante de robustete (doar modelele cu signaturi)
    rob = {}
    for tag in ['N2', 'noret']:
        f = os.path.join(CACHE, tag, f'fc_{kind}_{sym}_h{h}.csv')
        if os.path.exists(f):
            r = read_fc(kind, sym, h, tag).reindex(fc.index)
            rob[tag] = {m: float(S.qlike(y, r[m].values).mean()) for m in ['Sig-L', 'Sig-LK']}
    out['rob'] = rob
    info = read_info(kind, sym, h)
    out['k'] = {m: float(info[f'k_{m}'].mean()) for m in ['Sig-L', 'Sig-LK']}
    out['ess'] = float(info['ess'].mean())
    out['hv_share'] = float(info['hv_share'].mean())
    sel = {}
    for m in ['Sig-L', 'Sig-LK']:
        cnt = np.zeros(3 + 39)
        for s in info[f'S_{m}'].fillna(''):
            for j in str(s).split():
                cnt[int(float(j))] += 1
        sel[m] = (cnt / len(info)).tolist()
    out['sel'] = sel
    return out


def evaluate_all():
    from joblib import Parallel, delayed
    f = os.path.join(CACHE, 'evaluation.json')
    if os.path.exists(f) and os.path.getmtime(f) > max(os.path.getmtime(os.path.join(CACHE, 'main', x))
                                                        for x in os.listdir(os.path.join(CACHE, 'main'))):
        return json.load(open(f))
    ev = Parallel(n_jobs=12, verbose=2)(delayed(eval_asset)(k, s, h) for k, s in assets() for h in H)
    json.dump(ev, open(f, 'w'), default=float)
    return ev


# -----------------------------------------------------------------------------
# AGREGARE
# -----------------------------------------------------------------------------
def holm_bh_counts(p):
    p = np.asarray(p)
    return {'raw': int((p < 0.05).sum()), 'holm': int((S.holm(p) < 0.05).sum()), 'bh': int((S.bh(p) < 0.05).sum()),
            'n': int(len(p))}


def panel_dm(h, kinds, m, b, loss='ql'):
    """DM on the cross-sectional average loss differential (one series per date, all assets of the group)."""
    ds = []
    for k, s in assets():
        if k not in kinds:
            continue
        fc = read_fc(k, s, h)
        f = S.qlike if loss == 'ql' else S.mse
        d = f(fc.y, fc[m]) - f(fc.y, fc[b])
        if loss == 'se':
            d = d / (f(fc.y, fc[b]).mean())
        ds.append(d.rename(s))
    D = pd.concat(ds, axis=1).mean(axis=1).dropna()
    t, p1, _ = S.dm_test(D.values, np.zeros(len(D)), h)
    return {'t': float(t), 'p': float(p1), 'T': int(len(D)), 'start': str(D.index[0].date())}


def aggregate(ev):
    E = pd.DataFrame(ev)
    M = S.MODELS
    groups = {'stocks': ['stocks'], 'futures': ['futures'], 'forex': ['forex'], 'all': list(S.CLASSES)}
    pooled, wins, mcs, sub, rel, rob, filt, gw, pdm = {}, {}, {}, {}, {}, {}, {}, {}, {}
    for h in H:
        Eh = E[E.h == h]
        pooled[h], sub[h], rel[h], rob[h], filt[h], pdm[h] = {}, {}, {}, {}, {}, {}
        for g, ks in groups.items():
            Eg = Eh[Eh.kind.isin(ks)]
            q = pd.DataFrame(list(Eg.ql))
            s = pd.DataFrame(list(Eg.se))
            rq = q.div(q['HAR'], axis=0)
            rs = s.div(s['HAR'], axis=0)
            pooled[h][g] = {m: {'rq_mean': rq[m].mean(), 'rq_median': rq[m].median(), 'rs_mean': rs[m].mean(),
                                'rq_vs_loghar': (q[m] / q['logHAR']).mean(), 'ql': q[m].mean()} for m in M}
            sub[h][g] = {}
            for p in ['covid', 'apr2025', 'rest']:
                qq = pd.DataFrame([x[p] for x in Eg['sub'] if x[p] is not None])
                sub[h][g][p] = {m: (qq[m] / qq['HAR']).mean() for m in M} if len(qq) else None
                if len(qq):
                    sub[h][g][p]['ql_logHAR'] = qq['logHAR'].mean()
            re = pd.DataFrame(list(Eg.relerr))
            rel[h][g] = {'mean': re.mean().to_dict(), 'median': re.median().to_dict(),
                         'n_explode': pd.DataFrame(list(Eg.n_explode)).sum().to_dict(),
                         'assets_explode': (pd.DataFrame(list(Eg.n_explode)) > 0).sum().to_dict()}
            qf = pd.DataFrame(list(Eg.ql_filter))
            filt[h][g] = {m: (qf[m] / qf['HAR']).mean() for m in M}
            filt[h][g]['n_filter'] = pd.DataFrame(list(Eg.n_filter)).sum().to_dict()
            filt[h][g]['rl'] = {m: (qf[m] / qf['logHAR']).mean() for m in M}     # filtered, relative to filtered log-HAR
            filt[h][g]['n_fc'] = int(Eg['T'].sum())
            rr = {}
            for tag in ['N2', 'noret']:
                vals = [x.get(tag) for x in Eg.rob]
                if all(v is not None for v in vals) and len(vals):
                    qq = pd.DataFrame(vals)
                    rr[tag] = {m: (qq[m].values / q['HAR'].values).mean() for m in ['Sig-L', 'Sig-LK']}
            rob[h][g] = rr
            pdm[h][g] = {f'{m}|{b}': panel_dm(h, ks, m, b) for m, b in
                         [('Sig-LK', 'logHAR'), ('Sig-LK', 'HAR'), ('Sig-L', 'logHAR'), ('logHAR-K', 'logHAR'),
                          ('Sig-LK', 'Sig-L'), ('logHAR', 'HAR')]}
        # victorii pe active, cu corectie pentru testare multipla (familia: cele 50 de active)
        wins[h] = {}
        for comp in ['Sig-LK|logHAR', 'Sig-LK|HAR', 'Sig-L|logHAR', 'logHAR-K|logHAR', 'logHAR|HAR', 'HARQ|HAR',
                     'SHAR|HAR', 'Sig-LK|Sig-L']:
            m, b = comp.split('|')
            if comp == 'Sig-LK|Sig-L':
                p_b = []
                p_w = []
                for _, r in Eh.iterrows():
                    fc = read_fc(r.kind, r.sym, h)
                    t, p1, _ = S.dm_test(S.qlike(fc.y, fc[m]), S.qlike(fc.y, fc[b]), h)
                    p_b.append(p1)
                    p_w.append(1 - p1)
            else:
                p_b = [d[comp]['p_ql'] for d in Eh.dm]
                p_w = [1 - d[comp]['p_ql'] for d in Eh.dm]
            wins[h][comp] = {'better': holm_bh_counts(p_b), 'worse': holm_bh_counts(p_w)}
        mcs[h] = {'ql': {m: float(np.mean([m in inc for inc in Eh.mcs_ql])) for m in M},
                  'se': {m: float(np.mean([m in inc for inc in Eh.mcs_se])) for m in M},
                  'ql_by_class': {k: {m: float(np.mean([m in inc for inc in Eh[Eh.kind == k].mcs_ql])) for m in M}
                                  for k in S.CLASSES}}
        gw[h] = {c: holm_bh_counts([g[c] for g in Eh.gw]) for c in ['Sig-LK|logHAR', 'Sig-L|logHAR', 'logHAR-K|logHAR']}
    return dict(pooled=pooled, wins=wins, mcs=mcs, sub=sub, relerr=rel, rob=rob, filter=filt, gw=gw, panel_dm=pdm)


# -----------------------------------------------------------------------------
# GRAFICE
# -----------------------------------------------------------------------------
def chart_volare():
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    picks = {'stocks': [('JPM', MainBlue), ('NVDA', IDAred)], 'futures': [('ES', Forest), ('CL', Orange)],
             'forex': [('EURUSD', Purple), ('USDJPY', Teal)]}
    stats_ = {}
    for ax, (k, pk) in zip(axes, picks.items()):
        for s, c in pk:
            a = S.load_asset(k, s)
            vol = np.sqrt(252 * a.rv).rolling(5).mean() * 100
            ax.plot(vol.index, vol, color=c, lw=0.7, label=s)
        ax.set_yscale('log')
        ax.set_title(CLASS_LABEL[k])
        ax.set_yticks([5, 10, 20, 50, 100, 200])
        ax.set_yticklabels(['5', '10', '20', '50', '100', '200'])
    for k in S.CLASSES:
        d = S.load_class(k)
        stats_[k] = {'n_assets': int(d.symbol.nunique()), 'start': str(d.date.min().date()), 'end': str(d.date.max().date()),
                     'n_obs': int(len(d)),
                     'med_vol': float(np.median(np.sqrt(252 * d.groupby('symbol').rv5.median())) * 100)}
    axes[0].set_ylabel('Annualised volatility, %\n(5-day mean, log scale)')
    axes[0].set_ylim(2, 400)
    fig_legend_bottom(fig, axes, ncol=6, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch20_volare_rv')
    RES['data'] = stats_


def chart_signature_demo():
    """Lead-lag of (log RV, cumulative return) for JPM in the 22 days before 16 March 2020 and in a calm window."""
    a = S.load_asset('stocks', 'JPM')
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    out = {}
    for ax, end, lab, c in [(axes[0], '2019-11-15', 'Calm window (22 days to 15 Nov 2019)', MainBlue),
                            (axes[1], '2020-03-16', 'Stress window (22 days to 16 Mar 2020)', IDAred)]:
        j = a.index.searchsorted(pd.Timestamp(end))
        w = a.iloc[j - 21:j + 1]
        x = np.cumsum(w.r.values) * 100
        x = x - x[0]
        yv = np.log(w.rv.values)
        ax.plot(x, yv, '-o', color=c, ms=2.5, lw=1.0, label=lab)
        ax.fill(np.r_[x, x[0]], np.r_[yv, yv[0]], color=c, alpha=0.12)
        ax.plot([x[0], x[-1]], [yv[0], yv[-1]], color=Gray, lw=0.8, ls='--')
        ax.scatter([x[0]], [yv[0]], color='black', zorder=5, s=14)
        ax.set_xlabel('Cumulative open-to-close return in the window, %')
        ax.set_ylabel('log RV (5-minute)')
        P = np.c_[np.linspace(0, 1, 22), yv, x / 100]
        sg = S.sig_path(P, 2)
        la = S.levy_area(np.c_[x / 100, yv])
        ax.set_title(f'Lévy area (return, log RV) = {la:+.3f}', fontsize=9)
        out[end] = {'levy': float(la), 'dlogrv': float(yv[-1] - yv[0]), 'dret': float(x[-1]),
                    'sig_lvl1': sg[:3].tolist()}
    fig_legend_bottom(fig, axes, ncol=2, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch20_signature_demo')
    RES['sig_demo'] = out


def chart_sig_dimension():
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    Ns = np.arange(1, 7)
    for d, c in [(2, MainBlue), (3, IDAred), (4, Forest), (5, Orange)]:
        M = [(d ** (n + 1) - 1) // (d - 1) - 1 for n in Ns]
        ax.plot(Ns, M, '-o', color=c, ms=3.5, label=f'd = {d} channels')
    ax.set_yscale('log')
    ax.axhline(1000, color=Gray, ls='--', lw=0.8)
    ax.text(1.05, 1150, 'rolling window of 1000 days', fontsize=8, color='black')
    ax.set_xlabel('Truncation depth N')
    ax.set_ylabel('Number of signature terms (levels 1..N)')
    legend_outside_bottom(ax, ncol=4, y=-0.2)
    save_fig('ch20_sig_dimension')


def weights_chart(date, name, h=1):
    ws = []
    for k, s in assets():
        if k != 'stocks':
            continue
        f = os.path.join(CACHE, 'main', f'w_{k}_{s}_h{h}.csv')
        if not os.path.exists(f):
            continue
        W = pd.read_csv(f, index_col=0, parse_dates=True)
        if date in W.columns:
            ws.append(W[date].rename(s))
    W = pd.concat(ws, axis=1).dropna(how='all')
    avg = W.mean(axis=1)
    jpm = W['JPM']
    a = S.load_asset('stocks', 'JPM')
    rvbar = pd.concat([np.sqrt(252 * S.load_asset('stocks', s).rv).rename(s) for s in W.columns], axis=1).mean(axis=1)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    n = len(avg)
    ax.plot(avg.index, avg * n, color=IDAred, lw=0.9, label='Kernel weight x window length, average of 40 stocks')
    ax.plot(jpm.index, jpm * n, color=MainBlue, lw=0.6, alpha=0.8, label='Kernel weight x window length, JPM')
    ax.axhline(1, color=Gray, ls='--', lw=0.8)
    ax.set_ylabel('Weight relative to equal weighting')
    ax2 = ax.twinx()
    rv = rvbar.reindex(avg.index)
    ax2.plot(rv.index, 100 * rv, color=Forest, lw=0.7, label='Annualised RV volatility, average of 40 stocks (right, %)')
    ax2.set_ylabel('Volatility, %')
    ax2.spines['right'].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    save_fig(name)
    top = (avg.groupby(avg.index.to_period('M')).sum().sort_values(ascending=False))
    corr = float(np.corrcoef(avg.values, np.log(rv.values))[0, 1])
    return {'ess_avg': float((1 / (W ** 2).sum()).mean()), 'top_months': {str(k): float(v) for k, v in top.head(5).items()},
            'corr_w_logvol': corr, 'max_ratio': float(avg.max() * n), 'min_ratio': float(avg.min() * n),
            'train_start': str(avg.index[0].date()), 'train_end': str(avg.index[-1].date()),
            'hv_share': float(avg[rv >= rv.quantile(0.9)].sum())}


def chart_hv_share():
    rows = []
    for k, s in assets():
        info = read_info(k, s, 1)
        rows.append(info.set_index('date')['hv_share'].rename(f'{k}|{s}'))
    D = pd.concat(rows, axis=1)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    for k, c, lw in [('futures', Forest, 0.9), ('forex', MainBlue, 0.9), ('stocks', IDAred, 1.4)]:
        cols = [x for x in D.columns if x.startswith(k)]
        ser = D[cols].mean(axis=1).dropna().rolling(12, min_periods=6).mean()   # 12 re-estimations ~ 3 months
        ax.plot(ser.index, ser * 100, color=c, lw=lw, label=CLASS_LABEL[k])
    ax.axhline(10, color=Gray, ls='--', lw=0.8)
    ax.set_ylabel('Weight on the 10% most volatile\ntraining days, % (3-month mean)')
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch20_hv_share')
    st = D[[x for x in D.columns if x.startswith('stocks')]].mean(axis=1)
    return {'stocks_mean': float(st.mean()), 'stocks_max': float(st.max()), 'stocks_max_date': str(st.idxmax().date()),
            'stocks_min': float(st.min())}


def chart_qlike_ratio(E):
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    M = [m for m in S.MODELS if m != 'HAR']
    for ax, h in zip(axes, H):
        Eh = E[E.h == h]
        q = pd.DataFrame(list(Eh.ql))
        r = q[M].div(q['HAR'], axis=0)
        bp = ax.boxplot([r[m] for m in M], widths=0.6, patch_artist=True, showfliers=False)
        for patch, m in zip(bp['boxes'], M):
            patch.set_facecolor(COL[m])
            patch.set_alpha(0.35)
            patch.set_edgecolor(COL[m])
        for med, m in zip(bp['medians'], M):
            med.set_color(COL[m])
        for i, m in enumerate(M):
            ax.scatter([i + 1], [r[m].mean()], marker='D', color=COL[m], s=14, zorder=5,
                       label=f'{SHORT[m]}' if h == H[0] else None)
        ax.axhline(1, color=Gray, ls='--', lw=0.8)
        ax.set_xticks(range(1, len(M) + 1))
        ax.set_xticklabels([SHORT[m] for m in M], rotation=40, fontsize=7.5)
        ax.set_title(f'h = {h} day' + ('s' if h > 1 else ''))
    axes[0].set_ylabel('QLIKE relative to HAR (50 assets)')
    fig_legend_bottom(fig, axes, ncol=6, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch20_qlike_ratio')


def chart_mcs(A):
    fig, ax = plt.subplots(figsize=(8.5, 3.3))
    M = S.MODELS
    w = 0.26
    for i, (h, c) in enumerate(zip(H, [MainBlue, Orange, IDAred])):
        v = [100 * A['mcs'][h]['ql'][m] for m in M]
        ax.bar(np.arange(len(M)) + (i - 1) * w, v, width=w, color=c, label=f'h = {h}')
    ax.set_xticks(range(len(M)))
    ax.set_xticklabels([SHORT[m] for m in M])
    ax.set_ylabel('Share of assets in the\n90% MCS (QLIKE), %')
    ax.set_ylim(0, 105)
    legend_outside_bottom(ax, ncol=3, y=-0.14)
    save_fig('ch20_mcs')


def chart_dm_heat(E):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.6), gridspec_kw={'width_ratios': [1, 1]})
    for ax, comp, ttl in [(axes[0], 'Sig-LK|logHAR', 'Sig-LK vs log-HAR'), (axes[1], 'Sig-LK|HAR', 'Sig-LK vs HAR')]:
        T = pd.DataFrame({h: {f'{r.sym}': r.dm[comp]['t_ql'] for _, r in E[E.h == h].iterrows()} for h in H})
        order = [s for k, s in assets()]
        T = T.loc[order]
        im = ax.imshow(T.values.T, aspect='auto', cmap='RdBu_r', vmin=-4, vmax=4)
        ax.set_yticks(range(len(H)))
        ax.set_yticklabels([f'h = {h}' for h in H])
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(order, rotation=90, fontsize=5.5)
        ax.set_title(ttl + ' (DM t-statistic, QLIKE)', fontsize=9)
    cb = fig.colorbar(im, ax=axes, orientation='horizontal', fraction=0.05, pad=0.18)
    cb.set_label('DM t-statistic: negative (blue) = signature model more accurate; |t| > 1.645 one-sided 5%')
    save_fig('ch20_dm_heat')


def chart_subperiod(A):
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.3), sharey=False)
    M = ['logHAR', 'HARQ', 'SHAR', 'logHAR-K', 'Sig-L', 'Sig-LK']
    labels = {'covid': 'COVID-19 crash\n(20 Feb-30 Apr 2020)', 'apr2025': 'Tariff shock\n(2-30 Apr 2025)', 'rest': 'All other days'}
    for ax, h in zip(axes, H):
        w = 0.13
        for i, m in enumerate(M):
            v = [A['sub'][h]['all'][p][m] if A['sub'][h]['all'][p] else np.nan for p in labels]
            ax.bar(np.arange(3) + (i - 2.5) * w, v, width=w, color=COL[m], label=SHORT[m])
        ax.axhline(1, color=Gray, ls='--', lw=0.8)
        ax.set_xticks(range(3))
        ax.set_xticklabels(list(labels.values()), fontsize=7.5)
        ax.set_title(f'h = {h}')
    axes[0].set_ylabel('QLIKE relative to HAR\n(mean over 50 assets)')
    fig_legend_bottom(fig, axes, ncol=6, y=0.02)
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    save_fig('ch20_subperiod')


def chart_ablation(A):
    fig, ax = plt.subplots(figsize=(8, 3.3))
    M = ['logHAR', 'logHAR-K', 'Sig-L', 'Sig-LK']
    w = 0.2
    for i, m in enumerate(M):
        v = [A['pooled'][h]['all'][m]['rq_vs_loghar'] for h in H]
        ax.bar(np.arange(3) + (i - 1.5) * w, v, width=w, color=COL[m], label=S.LABEL[m])
    ax.axhline(1, color=Gray, ls='--', lw=0.8)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f'h = {h}' for h in H])
    ax.set_ylabel('QLIKE relative to log-HAR\n(mean over 50 assets)')
    lo = min(A['pooled'][h]['all'][m]['rq_vs_loghar'] for h in H for m in M)
    hi = max(A['pooled'][h]['all'][m]['rq_vs_loghar'] for h in H for m in M)
    ax.set_ylim(min(0.95, lo - 0.02), hi + 0.03)
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch20_ablation')


def chart_covid_forecasts():
    fc = read_fc('stocks', 'JPM', 1).loc['2020-02-03':'2020-05-29']
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.plot(fc.index, np.sqrt(252 * fc.y) * 100, color='black', lw=1.1, label='Realised (5-minute RV), next day')
    for m in ['HAR', 'logHAR', 'Sig-LK']:
        ax.plot(fc.index, np.sqrt(252 * fc[m]) * 100, color=COL[m], lw=0.9, label=f'{S.LABEL[m]} forecast')
    ax.set_ylabel('Annualised volatility, %')
    legend_outside_bottom(ax, ncol=2, y=-0.12)
    save_fig('ch20_covid_forecasts')


def chart_robustness(A):
    fig, ax = plt.subplots(figsize=(8.5, 3.3))
    variants = [('main', 'Main: depth 3, path (t, log RV, return)', IDAred), ('N2', 'Depth 2', Orange),
                ('noret', 'Path without the return channel', MainBlue), ('filter', 'Insanity filter on all models', Forest)]
    w = 0.2
    for i, (tag, lab, c) in enumerate(variants):
        v = []
        for h in H:
            if tag == 'main':
                v.append(A['pooled'][h]['all']['Sig-LK']['rq_mean'])
            elif tag == 'filter':
                v.append(A['filter'][h]['all']['Sig-LK'])
            else:
                v.append(A['rob'][h]['all'].get(tag, {}).get('Sig-LK', np.nan))
        ax.bar(np.arange(3) + (i - 1.5) * w, v, width=w, color=c, label=lab)
    ax.plot([], [])
    for j, h in enumerate(H):
        ax.plot([j - 0.45, j + 0.45], [A['pooled'][h]['all']['logHAR']['rq_mean']] * 2, color=Teal, lw=1.4,
                label='log-HAR (main)' if j == 0 else None)
    ax.axhline(1, color=Gray, ls='--', lw=0.8)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f'h = {h}' for h in H])
    ax.set_ylabel('Sig-LK: QLIKE relative to HAR\n(mean over 50 assets)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch20_robustness')


def word_labels():
    ch = ['t', 'lrv', 'ret']
    labs = ['HAR day', 'HAR week', 'HAR month']
    for w in S.sig_words(3, 3):
        labs.append('(' + ','.join(ch[i] for i in w) + ')')
    return labs


def chart_selection(E):
    labs = word_labels()
    sel = np.mean([r['Sig-LK'] for r in E.sel], axis=0)
    o = np.argsort(sel)[::-1][:14]
    fig, ax = plt.subplots(figsize=(8.5, 3.4))
    cols = [MainBlue if j < 3 else (Forest if j < 6 else (Orange if j < 15 else Purple)) for j in o]
    ax.bar(range(len(o)), 100 * sel[o], color=cols)
    ax.set_xticks(range(len(o)))
    ax.set_xticklabels([labs[j] for j in o], rotation=45, fontsize=7.5, ha='right')
    ax.set_ylabel('Selected in % of re-estimations\n(Sig-LK, all assets and horizons)')
    from matplotlib.patches import Patch
    hd = [Patch(color=c, label=l) for c, l in [(MainBlue, 'log-HAR terms'), (Forest, 'Signature level 1'),
                                                (Orange, 'Signature level 2'), (Purple, 'Signature level 3')]]
    ax.legend(handles=hd, loc='upper center', bbox_to_anchor=(0.5, -0.32), ncol=4, frameon=False)
    save_fig('ch20_selection')
    return {labs[j]: float(sel[j]) for j in o}


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import time
    T0 = time.time()
    chart_volare()
    chart_signature_demo()
    chart_sig_dimension()
    ev = evaluate_all()
    E = pd.DataFrame(ev)
    A = aggregate(ev)
    RES.update(A)
    chart_qlike_ratio(E)
    chart_mcs(A)
    chart_dm_heat(E)
    chart_subperiod(A)
    chart_ablation(A)
    chart_covid_forecasts()
    chart_robustness(A)
    RES['selection'] = chart_selection(E)
    RES['weights'] = {'2020-03-16': weights_chart('2020-03-16', 'ch20_weights_2020'),
                      '2025-04-07': weights_chart('2025-04-07', 'ch20_weights_2025')}
    RES['hv'] = chart_hv_share()
    val = json.load(open(os.path.join(CACHE, 'validation.json')))
    RES['validation'] = val['choice']            # keys 'class|model|h': c chosen on the class validation block
    RES['val_cutoff'] = val['cutoff']            # keys 'class|h': date of the last validation target of the class
    RES['design'] = {k: (list(v) if isinstance(v, tuple) else v) for k, v in S.CFG.items()}
    per = E.groupby('kind').agg(start=('start', 'min'), end=('end', 'max'), T=('T', 'median'))
    RES['eval_period'] = per.astype(str).to_dict('index')
    RES['n_forecasts'] = int(E['T'].sum())
    RES['n_forecasts_h'] = {str(h): int(E[E.h == h]['T'].sum()) for h in H}
    RES['dm_p'] = {str(h): {comp: {f"{r.kind}|{r.sym}": r.dm[comp]['p_ql'] for _, r in E[E.h == h].iterrows()}
                            for comp in ['Sig-LK|logHAR', 'Sig-LK|HAR', 'Sig-L|logHAR']} for h in H}
    RES['per_asset'] = {f"{r.kind}|{r.sym}|{r.h}": {'rq_loghar': r.ql['Sig-LK'] / r.ql['logHAR'],
                                                   't_loghar': r.dm['Sig-LK|logHAR']['t_ql'],
                                                   'mcs_sig': 'Sig-LK' in r.mcs_ql, 'mcs_loghar': 'logHAR' in r.mcs_ql}
                        for _, r in E.iterrows()}
    RES['k'] = {m: float(np.mean([r[m] for r in E.k])) for m in ['Sig-L', 'Sig-LK']}
    RES['ess'] = float(E.ess.mean())
    rt = pd.read_csv(os.path.join(CACHE, 'runtime.csv'))
    RES['runtime'] = {'core_seconds': float(rt.seconds.sum()), 'jobs': int(len(rt))}
    if os.path.exists(os.path.join(CACHE, 'wall.json')):
        RES['runtime']['wall_seconds'] = json.load(open(os.path.join(CACHE, 'wall.json')))['wall_seconds_last_run']
    with open(os.path.join(HERE, 'ch20_results.json'), 'w') as f:
        json.dump(RES, f, indent=1, default=float)
    print('done', round(time.time() - T0), 's')

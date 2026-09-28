"""
Generator pentru toate graficele din Capitolul 13: Machine Learning in Finance
============================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date reale: S&P 500, VIX (2000-2026), Bitcoin (2014-2026) din data/market.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import KFold
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_ml import (load_data, ffd_weights, frac_diff_ffd, get_daily_vol, triple_barrier,
                    PurgedKFold, build_features, sharpe_ratio, expected_max_sharpe,
                    deflated_sharpe_ratio, local_whittle, exact_local_whittle)

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
Crimson  = '#DC3545'
Gray     = '#7F7F7F'
LightGray = '#DADADA'

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')
SEED = 42


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


# =============================================================================
# DATE
# =============================================================================
spx = load_data('sp500')['Close']
vix = load_data('vix')['Close']
btc = load_data('btc')['Close']
log_spx = np.log(spx)


def find_min_d(logp, grid=np.round(np.arange(0, 1.01, 0.05), 2), crit_level='5%'):
    """Cel mai mic d pentru care seria FFD este stationara (ADF la 5%)."""
    rows = []
    for d in grid:
        x = frac_diff_ffd(logp, d).dropna()
        adf = adfuller(x, maxlag=1, regression='c', autolag=None)
        corr = np.corrcoef(logp.loc[x.index], x)[0, 1]
        rows.append((d, adf[0], adf[4][crit_level], corr))
    out = pd.DataFrame(rows, columns=['d', 'adf', 'crit', 'corr']).set_index('d')
    d_star = out.index[out['adf'] < out['crit']].min()
    return out, d_star


# =============================================================================
# FIG 1: Ponderile diferentierii fractionare
# =============================================================================
def fig_ffd_weights():
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    for d, c in zip([0.2, 0.4, 0.6, 0.8, 1.0], [Forest, Amber, Orange, IDAred, MainBlue]):
        w = ffd_weights(d, threshold=0, max_size=11)
        ax.plot(range(len(w)), w, marker='o', ms=3.5, color=c, label=f'$d={d}$')
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag $k$')
    ax.set_ylabel('Weight $w_k$')
    ax.set_title('Fractional differentiation weights: memory decays slowly for $0<d<1$',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=5, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_ffd_weights')


# =============================================================================
# FIG 2: ADF si corelatie vs d (S&P 500)
# =============================================================================
def fig_ffd_adf():
    out, d_star = find_min_d(log_spx)
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.plot(out.index, out['adf'], color=MainBlue, marker='o', ms=3, label='ADF statistic')
    ax.axhline(out['crit'].iloc[0], color=IDAred, ls='--', lw=0.9, label='5% critical value')
    ax.axvline(d_star, color=Gray, ls=':', lw=0.9)
    ax.set_xlabel('Differentiation order $d$')
    ax.set_ylabel('ADF statistic')
    ax2 = ax.twinx()
    ax2.plot(out.index, out['corr'], color=Forest, marker='s', ms=3, label='Corr. with log price')
    ax2.set_ylabel('Correlation', color=Forest)
    ax2.spines['right'].set_visible(True)
    ax2.set_ylim(-0.05, 1.05)
    ax.annotate(f"$d^*={d_star:.2f}$\ncorr $={out.loc[d_star, 'corr']:.2f}$",
                xy=(d_star, out.loc[d_star, 'adf']), xytext=(d_star + 0.12, out['adf'].min() * 0.45),
                fontsize=8, arrowprops=dict(arrowstyle='->', color=Gray, lw=0.6))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False)
    ax.set_title('S&P 500 log price, 2000-2026: ADF (constant, 1 lag) on the FFD series', fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch13_ffd_adf')
    return d_star


# =============================================================================
# FIG 3: Log pret vs FFD(d*) vs prima diferenta
# =============================================================================
def fig_ffd_series(d_star):
    x_ffd = frac_diff_ffd(log_spx, d_star)
    x_d1 = log_spx.diff().dropna()
    fig, axes = plt.subplots(3, 1, figsize=(7.0, 4.2), sharex=True)
    panels = [(log_spx, MainBlue, '$d=0$: log price (memory, non-stationary)'),
              (x_ffd, Forest, f'$d={d_star:.2f}$: FFD series (ADF rejects, yet still I(1): weights sum to {ffd_weights(d_star).sum():.3f})'),
              (x_d1, IDAred, '$d=1$: log returns (stationary, memory erased)')]
    for ax, (s, c, t) in zip(axes, panels):
        ax.plot(s.index, s.values, color=c, lw=0.6)
        ax.set_title(t, fontsize=8.5, loc='left', color=c)
    axes[-1].set_xlabel('Date')
    plt.tight_layout()
    save_fig('ch13_ffd_series')


# =============================================================================
# FIG 3b: Estimarea memoriei d (local Whittle / exact local Whittle) in functie de latimea de banda
# =============================================================================
def fig_memory_estimation(d_ffd=0.25):
    r = log_spx.diff().dropna()
    x_ffd = frac_diff_ffd(log_spx, d_ffd)
    alphas = np.round(np.arange(0.45, 0.801, 0.025), 3)
    series = [('Log price (exact local Whittle)', log_spx.values, exact_local_whittle, MainBlue),
              (f'FFD series, $d={d_ffd}$ (exact local Whittle)', x_ffd.values, exact_local_whittle, Forest),
              ('Absolute returns $|r_t|$ (local Whittle)', r.abs().values, local_whittle, Amber),
              ('Returns $r_t$ (local Whittle)', r.values, local_whittle, IDAred)]
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    out = {}
    for lab, x, est, c in series:
        res = np.array([est(x, alpha=a) for a in alphas])
        ax.plot(alphas, res[:, 0], color=c, marker='o', ms=2.5, label=lab)
        ax.fill_between(alphas, res[:, 0] - 1.96 * res[:, 1], res[:, 0] + 1.96 * res[:, 1], color=c, alpha=0.15, lw=0)
        out[lab] = dict(zip(alphas, res[:, 0]))
    for v in (0, 0.5, 1):
        ax.axhline(v, color=Gray, ls=':', lw=0.7)
    ax.axvline(0.65, color=Gray, ls='--', lw=0.7)
    ax.set_xlabel('Bandwidth exponent $a$ (number of frequencies $m = n^{a}$)')
    ax.set_ylabel('Estimated memory $\\hat d$')
    ax.set_title('S&P 500, 2000-2026: memory parameter with 95% CI ($\\pm 1.96/(2\\sqrt{m})$)', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_memory_estimation')
    return out


# =============================================================================
# FIG 4: Metoda celor trei bariere (S&P 500, 2022)
# =============================================================================
def fig_triple_barrier():
    close = spx.loc['2021-10-01':'2023-03-31']
    vol = get_daily_vol(spx).reindex(close.index)
    events = [pd.Timestamp(t) for t in ['2022-01-18', '2022-03-15', '2022-05-19', '2022-08-01', '2022-11-01']]
    events = [close.index[close.index.searchsorted(t)] for t in events]
    tb = triple_barrier(close, events, vol, pt=1.0, sl=1.0, horizon=15)

    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(close.index, close.values, color=Purple, lw=0.8, label='S&P 500')
    colors = {'upper': Forest, 'lower': IDAred, 'vertical': Amber}
    for t0, row in tb.iterrows():
        p0 = close.loc[t0]
        i0 = close.index.get_loc(t0)
        tv = close.index[min(i0 + 15, len(close) - 1)]
        up, dn = p0 * np.exp(row['width']), p0 * np.exp(-row['width'])
        ax.add_patch(mpatches.Rectangle((t0, dn), tv - t0, up - dn, fill=True,
                                        fc=colors[row['barrier']], alpha=0.10, lw=0))
        ax.plot([t0, tv], [up, up], color=Forest, lw=0.9)
        ax.plot([t0, tv], [dn, dn], color=IDAred, lw=0.9)
        ax.plot([tv, tv], [dn, up], color=Amber, lw=0.9)
        ax.plot(t0, p0, 'o', color=MainBlue, ms=3.5)
        ax.plot(row['t1'], close.loc[row['t1']], marker='*', ms=9, color=colors[row['barrier']])
        ax.annotate(f"{'+1' if row['label'] > 0 else '-1'}", xy=(row['t1'], close.loc[row['t1']]),
                    xytext=(3, 6), textcoords='offset points', fontsize=8,
                    color=colors[row['barrier']], fontweight='bold')
    handles = [plt.Line2D([], [], color=Forest, label='Upper barrier (profit-taking)'),
               plt.Line2D([], [], color=IDAred, label='Lower barrier (stop-loss)'),
               plt.Line2D([], [], color=Amber, label='Vertical barrier (time limit)'),
               plt.Line2D([], [], color=MainBlue, marker='o', ls='', ms=4, label='Event $t_0$'),
               plt.Line2D([], [], color='black', marker='*', ls='', ms=8, label='First touch $t_1$')]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    ax.set_ylabel('Index level')
    ax.set_title('Triple-barrier labelling: barriers at $\\pm\\sigma_{t_0}\\sqrt{h}$, $h=15$ days',
                 fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch13_triple_barrier')


# =============================================================================
# FIG 5: Distributia etichetelor: orizont fix vs trei bariere
# =============================================================================
def fig_label_comparison():
    vol = get_daily_vol(spx)
    idx = spx.index[250:-20]
    tb = triple_barrier(spx, idx, vol, pt=1.0, sl=1.0, horizon=10)
    fixed = np.sign(np.log(spx).shift(-10) - np.log(spx)).reindex(tb.index)
    shares = pd.DataFrame({
        'Fixed horizon (10d)': [np.mean(fixed > 0), np.mean(fixed < 0), 0.0],
        'Triple barrier': [np.mean(tb['barrier'] == 'upper'), np.mean(tb['barrier'] == 'lower'),
                           np.mean(tb['barrier'] == 'vertical')]},
        index=['+1 (up)', '-1 (down)', 'time-out'])
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), gridspec_kw={'width_ratios': [1, 1.25]})
    x = np.arange(3)
    axes[0].bar(x - 0.18, shares.iloc[:, 0], 0.36, color=MainBlue, label=shares.columns[0])
    axes[0].bar(x + 0.18, shares.iloc[:, 1], 0.36, color=Amber, label=shares.columns[1])
    axes[0].set_xticks(x, shares.index)
    axes[0].set_ylabel('Share of labels')
    axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
    hold = (tb['t1'] - tb.index).dt.days
    axes[1].hist(hold[tb['barrier'] != 'vertical'], bins=np.arange(0, 17, 1), color=MainBlue, alpha=0.85)
    axes[1].set_xlabel('Calendar days until first touch')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Horizontal barrier hits', fontsize=8.5, loc='left')
    axes[0].set_title('S&P 500, 2001-2026', fontsize=8.5, loc='left')
    plt.tight_layout()
    save_fig('ch13_label_comparison')
    return shares


# =============================================================================
# FIG 6: Schema Purged K-Fold cu embargo
# =============================================================================
def fig_purged_cv_scheme():
    n, k, h, emb = 100, 5, 4, 3
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    for fold in range(k):
        y = k - fold
        t_start, t_end = fold * n // k, (fold + 1) * n // k
        for t in range(n):
            if t_start <= t < t_end:
                c = IDAred
            elif t_start - h <= t < t_start:
                c = LightGray
            elif t_end <= t < t_end + emb:
                c = Amber
            else:
                c = MainBlue
            ax.add_patch(mpatches.Rectangle((t, y - 0.35), 1, 0.7, fc=c, ec='none'))
        ax.text(-2, y, f'Fold {fold + 1}', ha='right', va='center', fontsize=8)
    ax.set_xlim(-12, n + 1)
    ax.set_ylim(0.3, k + 0.7)
    ax.set_yticks([])
    ax.set_xlabel('Time (observation index)')
    ax.spines['left'].set_visible(False)
    handles = [mpatches.Patch(color=MainBlue, label='Train'),
               mpatches.Patch(color=IDAred, label='Test'),
               mpatches.Patch(color=LightGray, label='Purged (label overlaps test)'),
               mpatches.Patch(color=Amber, label='Embargo (after test)')]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=4, frameon=False)
    plt.tight_layout()
    save_fig('ch13_purged_cv_scheme')


# =============================================================================
# FIG 7: Scurgerea de informatie (leakage) - experiment pe date fara semnal
# =============================================================================
def fig_leakage_experiment():
    rng = np.random.default_rng(SEED)
    n, h = 3000, 20
    # pret: mers aleator pur -> nu exista nimic de prezis
    p = pd.Series(np.cumsum(rng.normal(0, 0.01, n + h)))
    y = (p.shift(-h) - p > 0).astype(int).iloc[:n].values          # eticheta pe h zile (suprapusa)
    # caracteristici persistente, dar independente de viitor
    X = np.column_stack([pd.Series(rng.normal(size=n + h)).rolling(h).mean().bfill().iloc[:n]
                         for _ in range(5)])
    t1 = pd.Series(np.arange(n) + h, index=np.arange(n))
    model = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1, random_state=SEED)

    schemes = {
        'K-Fold\n(shuffled)': KFold(5, shuffle=True, random_state=SEED),
        'K-Fold\n(no shuffle)': KFold(5, shuffle=False),
        'Purged K-Fold\n+ embargo': PurgedKFold(5, t1=t1, pct_embargo=0.01),
    }
    res = {}
    for name, cv in schemes.items():
        accs = []
        for tr, te in cv.split(X):
            model.fit(X[tr], y[tr])
            accs.append(accuracy_score(y[te], model.predict(X[te])))
        res[name] = accs

    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    colors = [IDAred, Amber, Forest]
    for i, (name, accs) in enumerate(res.items()):
        ax.bar(i, np.mean(accs), 0.55, color=colors[i], alpha=0.85)
        ax.scatter(np.full(len(accs), i) + np.linspace(-0.12, 0.12, len(accs)), accs,
                   color='black', s=10, zorder=3)
        ax.text(i + 0.3, np.mean(accs) + 0.01, f'{np.mean(accs):.1%}', ha='left', fontsize=8.5,
                fontweight='bold', color=colors[i])
    ax.axhline(0.5, color=Gray, ls='--', lw=0.8)
    ax.text(2.45, 0.505, 'coin flip', fontsize=7.5, color='black', ha='right', va='bottom')
    ax.set_xticks(range(len(res)), list(res.keys()))
    ax.set_ylim(0.35, 1.0)
    ax.set_ylabel('Out-of-fold accuracy')
    ax.set_title('Random walk + persistent noise features: there is NOTHING to predict',
                 fontsize=9, loc='left')
    plt.tight_layout()
    save_fig('ch13_leakage_experiment')
    return {k: np.mean(v) for k, v in res.items()}


# =============================================================================
# DATE DE MODELARE (S&P 500): caracteristici + etichete pe 5 zile
# =============================================================================
H_LABEL = 5


def modelling_frame(d_star):
    feats = build_features(spx, vix=vix, d_ffd=d_star)
    fwd = np.log(spx).shift(-H_LABEL) - np.log(spx)
    df = feats.assign(fwd=fwd).dropna()
    df = df.loc['2001-01-01':]
    df['y'] = (df['fwd'] > 0).astype(int)
    pos = np.searchsorted(spx.index, df.index)
    df['t1'] = spx.index[np.minimum(pos + H_LABEL, len(spx) - 1)]
    return df


def get_models():
    return {
        'Logistic (L2)': make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000)),
        'Random Forest': RandomForestClassifier(n_estimators=400, min_samples_leaf=100,
                                                max_features='sqrt', n_jobs=-1, random_state=SEED),
        'Gradient Boosting': HistGradientBoostingClassifier(max_depth=3, learning_rate=0.03,
                                                            max_iter=200, min_samples_leaf=100,
                                                            random_state=SEED),
        'Neural net (MLP)': make_pipeline(StandardScaler(),
                                          MLPClassifier(hidden_layer_sizes=(32, 16), alpha=1e-2,
                                                        early_stopping=True, max_iter=500,
                                                        random_state=SEED)),
    }


# =============================================================================
# FIG 8: Comparatia modelelor (Purged K-Fold, S&P 500)
# =============================================================================
def fig_model_comparison(df):
    feat_cols = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    X, y = df[feat_cols].values, df['y'].values
    cv = PurgedKFold(5, t1=df['t1'], pct_embargo=0.01)
    rows = []
    for name, model in get_models().items():
        accs, aucs, base = [], [], []
        for tr, te in cv.split(X):
            model.fit(X[tr], y[tr])
            prob = model.predict_proba(X[te])[:, 1]
            accs.append(accuracy_score(y[te], prob > 0.5))
            aucs.append(roc_auc_score(y[te], prob))
            base.append(max(y[te].mean(), 1 - y[te].mean()))
        rows.append((name, np.mean(accs), np.std(accs), np.mean(aucs), np.std(aucs), np.mean(base)))
    res = pd.DataFrame(rows, columns=['model', 'acc', 'acc_sd', 'auc', 'auc_sd', 'base']).set_index('model')

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    x = np.arange(len(res))
    cols = [MainBlue, Forest, Amber, Purple]
    axes[0].bar(x, res['acc'], 0.6, yerr=res['acc_sd'], color=cols, alpha=0.85,
                error_kw=dict(lw=0.7, capsize=2))
    axes[0].axhline(res['base'].mean(), color=IDAred, ls='--', lw=0.9)
    axes[0].text(len(res) - 0.5, res['base'].mean() + 0.004, 'always "up"', color=IDAred,
                 fontsize=7.5, ha='right', va='bottom')
    axes[0].set_ylim(0.45, 0.65)
    axes[0].set_ylabel('Accuracy')
    axes[1].bar(x, res['auc'], 0.6, yerr=res['auc_sd'], color=cols, alpha=0.85,
                error_kw=dict(lw=0.7, capsize=2))
    axes[1].axhline(0.5, color=Gray, ls='--', lw=0.9)
    axes[1].set_ylim(0.45, 0.65)
    axes[1].set_ylabel('ROC AUC')
    for ax in axes:
        ax.set_xticks(x, [m.replace(' (', '\n(').replace('Random Forest', 'Random\nForest').replace('Gradient Boosting', 'Gradient\nBoosting') for m in res.index], fontsize=7.5)
    axes[0].set_title('S&P 500, 5-day direction, purged 5-fold CV', fontsize=8.5, loc='left')
    plt.tight_layout()
    save_fig('ch13_model_comparison')
    return res


# =============================================================================
# FIG 8b: Drumul de regularizare LASSO (logistic L1)
# =============================================================================
def fig_lasso_path(df):
    feat_cols = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    X = StandardScaler().fit_transform(df[feat_cols].values)
    y = df['y'].values
    Cs = np.logspace(-4, 0, 40)
    coefs = []
    for C in Cs:
        m = LogisticRegression(penalty='l1', C=C, solver='liblinear', max_iter=5000).fit(X, y)
        coefs.append(m.coef_.ravel())
    coefs = np.array(coefs)
    fig, ax = plt.subplots(figsize=(6.8, 3.1))
    cmap = plt.get_cmap('tab20')
    order = np.argsort(-np.abs(coefs[-1]))
    for j, i in enumerate(order):
        ax.plot(1 / Cs, coefs[:, i], color=cmap(j % 20), lw=1.0,
                label=feat_cols[i] if j < 6 else None)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xscale('log')
    ax.invert_xaxis()
    ax.set_xlabel('Penalty $\\lambda = 1/C$ (log scale, stronger to the left)')
    ax.set_ylabel('Standardised coefficient')
    ax.set_title('LASSO-logistic path, S&P 500 5-day direction: most features are shrunk to zero',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_lasso_path')


# =============================================================================
# FIG 8c: Complexitate vs eroare: arbori de decizie (bias-varianta)
# =============================================================================
def fig_tree_complexity(df):
    from sklearn.tree import DecisionTreeClassifier
    feat_cols = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    X, y = df[feat_cols].values, df['y'].values
    cv = PurgedKFold(5, t1=df['t1'], pct_embargo=0.01)
    depths = range(1, 16)
    tr_acc, te_acc, rf_te = [], [], []
    for d in depths:
        a_tr, a_te, a_rf = [], [], []
        for tr, te in cv.split(X):
            m = DecisionTreeClassifier(max_depth=d, random_state=SEED).fit(X[tr], y[tr])
            a_tr.append(accuracy_score(y[tr], m.predict(X[tr])))
            a_te.append(accuracy_score(y[te], m.predict(X[te])))
            rf = RandomForestClassifier(n_estimators=150, max_depth=d, max_features='sqrt',
                                        n_jobs=-1, random_state=SEED).fit(X[tr], y[tr])
            a_rf.append(accuracy_score(y[te], rf.predict(X[te])))
        tr_acc.append(np.mean(a_tr)); te_acc.append(np.mean(a_te)); rf_te.append(np.mean(a_rf))
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.plot(depths, tr_acc, color=IDAred, marker='o', ms=3, label='Single tree: training')
    ax.plot(depths, te_acc, color=MainBlue, marker='o', ms=3, label='Single tree: purged CV')
    ax.plot(depths, rf_te, color=Forest, marker='s', ms=3, label='Random forest: purged CV')
    ax.axhline(df['y'].mean(), color=Gray, ls='--', lw=0.8)
    ax.text(15, df['y'].mean() + 0.004, 'always "up"', color='black', fontsize=7.5, ha='right')
    ax.set_xlabel('Maximum tree depth')
    ax.set_ylabel('Accuracy')
    ax.set_title('Bias-variance trade-off: training accuracy explodes, out-of-sample does not',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_tree_complexity')


# =============================================================================
# FIG 9: Importanta caracteristicilor: MDI vs MDA vs SHAP
# =============================================================================
def fig_feature_importance(df):
    feat_cols = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    X, y = df[feat_cols], df['y'].values
    split = int(len(df) * 0.7)
    gap = split + H_LABEL + int(0.01 * len(df))
    rf = RandomForestClassifier(n_estimators=400, min_samples_leaf=100, max_features='sqrt',
                                n_jobs=-1, random_state=SEED).fit(X.iloc[:split], y[:split])
    mdi = pd.Series(rf.feature_importances_, index=feat_cols)
    mda = pd.Series(permutation_importance(rf, X.iloc[gap:], y[gap:], scoring='roc_auc',
                                           n_repeats=20, random_state=SEED, n_jobs=-1).importances_mean,
                    index=feat_cols)
    try:
        import shap
        gbm = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.03, max_iter=200,
                                             min_samples_leaf=100, random_state=SEED)
        gbm.fit(X.iloc[:split], y[:split])
        sample = X.iloc[gap:].sample(min(800, len(X) - gap), random_state=SEED)
        explainer = shap.Explainer(gbm.predict_proba, X.iloc[:split].sample(200, random_state=SEED))
        sv = explainer(sample).values[..., 1]
        shap_imp = pd.Series(np.abs(sv).mean(0), index=feat_cols)
    except Exception as e:
        print('   SHAP skipped:', e)
        shap_imp = None

    order = mdi.sort_values().index
    n_panels = 3 if shap_imp is not None else 2
    fig, axes = plt.subplots(1, n_panels, figsize=(7.4, 3.3), sharey=True)
    axes[0].barh(order, mdi[order], color=MainBlue, alpha=0.85)
    axes[0].set_title('MDI (in-sample)', fontsize=8.5, loc='left')
    axes[1].barh(order, mda[order], color=np.where(mda[order] > 0, Forest, IDAred), alpha=0.85)
    axes[1].axvline(0, color=Gray, lw=0.5)
    axes[1].set_title('MDA (OOS, $\\Delta$AUC)', fontsize=8.5, loc='left')
    if shap_imp is not None:
        axes[2].barh(order, shap_imp[order], color=Amber, alpha=0.85)
        axes[2].set_title('mean |SHAP| (OOS)', fontsize=8.5, loc='left')
    for ax in axes:
        ax.tick_params(axis='y', labelsize=7.5)
        ax.tick_params(axis='x', labelsize=7)
    plt.tight_layout()
    save_fig('ch13_feature_importance')
    return mdi, mda, shap_imp


# =============================================================================
# FIG 10: Backtest walk-forward al unui semnal ML (cu costuri)
# =============================================================================
def fig_walk_forward_backtest(df, cost_bp=5):
    feat_cols = [c for c in df.columns if c not in ('fwd', 'y', 't1')]
    ret1 = np.log(spx).diff().shift(-1).reindex(df.index)      # randamentul zilei urmatoare
    signal = pd.Series(np.nan, index=df.index)
    years = range(2010, df.index[-1].year + 1)
    for yr in years:
        test = df.index[df.index.year == yr]
        train = df.index[df['t1'] < test[0]]                    # purjare: etichete cunoscute inainte de test
        model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.03, max_iter=200,
                                               min_samples_leaf=100, random_state=SEED)
        model.fit(df.loc[train, feat_cols], df.loc[train, 'y'])
        prob = model.predict_proba(df.loc[test, feat_cols])[:, 1]
        signal.loc[test] = np.where(prob > 0.5, 1.0, 0.0)       # long / cash
    oos = signal.dropna().index
    pos = signal.loc[oos]
    turnover = pos.diff().abs().fillna(pos.iloc[0])
    strat = pos * ret1.loc[oos] - turnover * cost_bp / 1e4
    bh = ret1.loc[oos]
    strat, bh = strat.dropna(), bh.dropna()

    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.plot(bh.index, np.exp(bh.cumsum()), color=Amber, lw=0.9,
            label=f'Buy & hold (SR = {sharpe_ratio(bh):.2f})')
    ax.plot(strat.index, np.exp(strat.cumsum()), color=MainBlue, lw=0.9,
            label=f'GBM long/cash, {cost_bp} bp costs (SR = {sharpe_ratio(strat):.2f})')
    ax.set_yscale('log')
    ax.set_yticks([1, 2, 3, 4, 6])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:g}'))
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_ylabel('Growth of 1 USD (log scale)')
    ax.set_title('Walk-forward backtest 2010-2026: yearly refit, purged training window',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    plt.tight_layout()
    save_fig('ch13_walk_forward_backtest')
    return sharpe_ratio(strat), sharpe_ratio(bh), pos.mean()


# =============================================================================
# FIG 11: Sharpe maxim asteptat sub H0 (teorema strategiei false)
# =============================================================================
def fig_expected_max_sharpe():
    rng = np.random.default_rng(SEED)
    T = 252 * 5
    Ns = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000])
    sims = []
    for N in Ns:
        # N strategii fara abilitate: randamente iid N(0, 1%) pe 5 ani, 200 repetitii
        r = rng.normal(0, 0.01, size=(200, N, T))
        sr = np.sqrt(252) * r.mean(-1) / r.std(-1, ddof=1)
        sims.append(sr.max(1))
    sims = np.array(sims)
    grid = np.logspace(np.log10(2), 3, 200)
    theory = expected_max_sharpe(grid, sr_std=np.sqrt(252 / T))

    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.plot(grid, theory, color=IDAred, lw=1.2, label='$E[\\max SR]$ (False Strategy Theorem)')
    ax.errorbar(Ns, sims.mean(1), yerr=sims.std(1), fmt='o', ms=3.5, color=MainBlue,
                capsize=2, lw=0.8, label='Monte Carlo (mean $\\pm$ 1 sd)')
    ax.set_xscale('log')
    ax.set_xlabel('Number of independent strategies tried $N$')
    ax.set_ylabel('Best annualised Sharpe ratio')
    ax.set_title('Zero-skill strategies, 5 years of daily data: the best one always "works"',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_expected_max_sharpe')


# =============================================================================
# FIG 12: Backtest overfitting: Sharpe in-sample vs out-of-sample
# =============================================================================
def fig_is_vs_oos():
    """Cautare de parametri pentru o strategie de medii mobile pe BTC: IS 2015-2020, OOS 2021-2026."""
    r = np.log(btc).diff()
    lp = np.log(btc)
    is_mask = btc.index < '2021-01-01'
    rows = []
    for fast in range(2, 60, 3):
        for slow in range(10, 250, 10):
            if slow <= fast:
                continue
            for band in (0.0, 0.01, 0.03):
                sig = ((lp.rolling(fast).mean() - lp.rolling(slow).mean()) > band).astype(float).shift(1)
                sr_is = sharpe_ratio((sig * r)[is_mask].dropna(), 365)
                sr_oos = sharpe_ratio((sig * r)[~is_mask].dropna(), 365)
                rows.append((fast, slow, band, sr_is, sr_oos))
    res = pd.DataFrame(rows, columns=['fast', 'slow', 'band', 'sr_is', 'sr_oos']).dropna()
    best = res.loc[res['sr_is'].idxmax()]
    rank_corr = stats.spearmanr(res['sr_is'], res['sr_oos'])[0]
    top = res.nlargest(int(len(res) * 0.1), 'sr_is')

    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    ax.scatter(res['sr_is'], res['sr_oos'], s=6, color=MainBlue, alpha=0.35, label=f'{len(res)} configurations')
    ax.scatter(top['sr_is'], top['sr_oos'], s=8, color=Amber, alpha=0.8, label='Top 10% in-sample')
    ax.scatter(best['sr_is'], best['sr_oos'], s=70, marker='*', color=IDAred, zorder=3,
               label=f"Best IS: SR$_{{IS}}$={best['sr_is']:.2f}, SR$_{{OOS}}$={best['sr_oos']:.2f}")
    lims = [min(res['sr_is'].min(), res['sr_oos'].min()) - 0.1, max(res['sr_is'].max(), res['sr_oos'].max()) + 0.1]
    ax.plot(lims, lims, color=Gray, ls=':', lw=0.8)
    ax.set_xlabel('Sharpe in-sample (2015-2020)')
    ax.set_ylabel('Sharpe out-of-sample (2021-2026)')
    ax.set_title(f'BTC moving-average crossover grid search (Spearman $\\rho$ = {rank_corr:.2f})',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    plt.tight_layout()
    save_fig('ch13_is_vs_oos')
    return res, best, rank_corr, top['sr_oos'].median()


# =============================================================================
# FIG 13: Deflated Sharpe Ratio in functie de numarul de incercari
# =============================================================================
def fig_deflated_sharpe():
    T = 252 * 5
    N = np.unique(np.logspace(0, 3, 60).astype(int))
    sr_std = np.sqrt(1 / T)                       # dispersia SR (neanualizat) sub H0
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    for sr_ann, c in zip([1.0, 1.5, 2.0, 2.5], [IDAred, Amber, Forest, MainBlue]):
        sr = sr_ann / np.sqrt(252)
        dsr = deflated_sharpe_ratio(sr, T, np.maximum(N, 1.0001), sr_std, skew=-0.5, kurt=6.0)
        ax.plot(N, dsr, color=c, label=f'observed SR = {sr_ann}')
    ax.axhline(0.95, color=Gray, ls='--', lw=0.8)
    ax.text(1.05, 0.90, '95% confidence', fontsize=7.5, color='black')
    ax.set_xscale('log')
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('Number of trials $N$')
    ax.set_ylabel('Deflated Sharpe Ratio')
    ax.set_title('DSR: 5 years daily, skew = -0.5, kurtosis = 6', fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=4, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_deflated_sharpe')


# =============================================================================
# FIG 14: Raport semnal/zgomot: finante vs alte domenii (R^2 OOS)
# =============================================================================
def fig_signal_to_noise(df):
    """Autocorelatia randamentelor vs autocorelatia volatilitatii: ce se poate prezice."""
    r = np.log(spx).diff().dropna()
    lags = np.arange(1, 41)
    ac_r = [r.autocorr(l) for l in lags]
    ac_a = [r.abs().autocorr(l) for l in lags]
    band = 1.96 / np.sqrt(len(r))
    fig, ax = plt.subplots(figsize=(6.8, 2.8))
    ax.bar(lags - 0.2, ac_r, 0.4, color=MainBlue, label='Returns $r_t$')
    ax.bar(lags + 0.2, ac_a, 0.4, color=Amber, label='Absolute returns $|r_t|$')
    ax.axhspan(-band, band, color=LightGray, alpha=0.6, lw=0)
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_xlabel('Lag (days)')
    ax.set_ylabel('Autocorrelation')
    ax.set_title('S&P 500 2000-2026: direction is almost unpredictable, risk is predictable',
                 fontsize=9, loc='left')
    legend_outside_bottom(ax, ncol=2, y=-0.25)
    plt.tight_layout()
    save_fig('ch13_signal_to_noise')


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print('Chapter 13 charts')
    fig_ffd_weights()
    d_star = fig_ffd_adf()
    print('   d* =', d_star)
    fig_ffd_series(d_star)
    fig_memory_estimation(d_star)
    fig_triple_barrier()
    print(fig_label_comparison())
    fig_purged_cv_scheme()
    print('   leakage:', fig_leakage_experiment())
    fig_signal_to_noise(None)
    df = modelling_frame(d_star)
    print('   modelling frame', df.shape, df.index[0].date(), df.index[-1].date())
    fig_lasso_path(df)
    fig_tree_complexity(df)
    print(fig_model_comparison(df))
    mdi, mda, shp = fig_feature_importance(df)
    print(pd.DataFrame({'mdi': mdi, 'mda': mda, 'shap': shp}).round(4))
    print('   walk-forward SR strat / B&H / exposure:', fig_walk_forward_backtest(df))
    fig_expected_max_sharpe()
    res, best, rho, top_oos = fig_is_vs_oos()
    print('   IS/OOS best:', best.to_dict(), 'rho', round(rho, 3), 'top10 median OOS', round(top_oos, 3),
          'N', len(res))
    fig_deflated_sharpe()

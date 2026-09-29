"""
Generator pentru toate graficele si cifrele din Capitolul 12: Optiuni si suprafata de volatilitate
================================================================================================
Toate graficele: fundal transparent, etichete ENG, legenda in afara, jos.
Date zilnice de piata (data/market): S&P 500 (1990-2026), SPY, Bitcoin, VIX, VIX9D, VIX3M, VVIX.
Optiuni Bitcoin: instantaneu datat al lantului Deribit (ch12_deribit_snapshot.csv) si indicele DVOL (Deribit).
Cifrele sunt salvate in ch12_results.json (folosite de generatoarele de slide-uri).
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
from scipy import stats, integrate
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfm_data import load_close, log_returns, spy_open_close, deribit_chain, dvol_history, read_market, _get  # noqa: E402
from option_tools import (bs_price, bs_greeks, implied_vol, newton_iv, crr_price, merton_price,  # noqa: E402
                          heston_price, svi_w, svi_fit, variance_from_strip, delta_hedge)

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
Gray     = '#7F7F7F'   # doar linii de referinta, benzi, grila
LightGray = '#DADADA'
Teal     = '#17A2B8'

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


def fig_legend_bottom(fig, handles, ncol=3, y=0.0):
    """O singura legenda pentru o figura cu mai multe panouri, sub figura."""
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def nw_mean(x, lags):
    """Media si eroarea standard Newey-West (HAC) a unei serii."""
    x = np.asarray(x, float)
    m = sm.OLS(x, np.ones_like(x)).fit(cov_type='HAC', cov_kwds={'maxlags': lags})
    return float(m.params[0]), float(m.bse[0])


# =============================================================================
# 1. PLATI LA SCADENTA SI STRATEGII
# =============================================================================
BASE = dict(S=100.0, K=100.0, T=0.25, r=0.04, sigma=0.20)


def fig_payoffs():
    """Plata la scadenta si profitul unei optiuni call si put cumparate (K = 100, T = 3 luni, sigma = 20%)."""
    b = BASE
    C = float(bs_price(b['S'], b['K'], b['T'], b['r'], b['sigma'], 'call'))
    P = float(bs_price(b['S'], b['K'], b['T'], b['r'], b['sigma'], 'put'))
    ST = np.linspace(60, 140, 401)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
    for ax, pay, prem, col, name in [(axes[0], np.maximum(ST - 100, 0), C, MainBlue, 'Long call'),
                                     (axes[1], np.maximum(100 - ST, 0), P, IDAred, 'Long put')]:
        ax.plot(ST, pay, color=col, lw=1.6)
        ax.plot(ST, pay - prem * np.exp(b['r'] * b['T']), color=col, lw=1.1, ls='--')
        ax.axhline(0, color=Gray, lw=0.6)
        ax.axvline(100, color=Gray, lw=0.5, ls=':')
        ax.set_title(f'{name}: premium {prem:.2f}', fontsize=9.5, loc='left')
        ax.set_xlabel('Price of the underlying at expiry $S_T$')
    axes[0].set_ylabel('Pay-off / profit at expiry')
    axes[0].set_ylim(-12, 40)
    fig_legend_bottom(fig, [Line2D([], [], color='black', lw=1.6, label='Pay-off at expiry'),
                            Line2D([], [], color='black', lw=1.1, ls='--', label='Profit = pay-off minus premium (with interest)'),
                            Line2D([], [], color=Gray, lw=0.5, ls=':', label='Strike $K = 100$')], ncol=3, y=-0.02)
    plt.tight_layout()
    save_fig('ch12_payoffs')
    return dict(call=C, put=P)


def fig_strategies():
    """Patru strategii: straddle, put de protectie, call acoperit, spread de call-uri (profit la scadenta)."""
    b = BASE
    pr = lambda K, kind: float(bs_price(b['S'], K, b['T'], b['r'], b['sigma'], kind)) * np.exp(b['r'] * b['T'])
    ST = np.linspace(60, 140, 401)
    stock = ST - 100 * np.exp(b['r'] * b['T'])
    strat = {
        'Long straddle (call + put, K = 100)': (np.maximum(ST - 100, 0) + np.maximum(100 - ST, 0) - pr(100, 'call') - pr(100, 'put'), Purple),
        'Protective put (stock + put, K = 95)': (stock + np.maximum(95 - ST, 0) - pr(95, 'put'), Forest),
        'Covered call (stock - call, K = 105)': (stock - np.maximum(ST - 105, 0) + pr(105, 'call'), Orange),
        'Bull call spread (call 95 - call 105)': (np.maximum(ST - 95, 0) - np.maximum(ST - 105, 0) - pr(95, 'call') + pr(105, 'call'), Teal),
    }
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.0), sharey=True)
    for ax, (name, (pnl, col)) in zip(axes, strat.items()):
        ax.plot(ST, pnl, color=col, lw=1.6)
        if 'stock' in name:
            ax.plot(ST, stock, color=MainBlue, lw=0.9, ls='--')
        ax.axhline(0, color=Gray, lw=0.6)
        ax.set_title(name, fontsize=8.2, loc='left')
        ax.set_xlabel('$S_T$')
        ax.set_ylim(-25, 25)
    axes[0].set_ylabel('Profit at expiry')
    fig_legend_bottom(fig, [Line2D([], [], color='black', lw=1.6, label='Profit of the strategy'),
                            Line2D([], [], color=MainBlue, lw=0.9, ls='--', label='Profit of the stock alone')], ncol=2, y=-0.02)
    plt.tight_layout()
    save_fig('ch12_strategies')
    return {k.split(' (')[0]: dict(cost=float(-v[0][200])) for k, v in strat.items()}


def parity_example():
    """Paritatea put-call pentru S = K = 100, T = 6 luni, r = 4%, sigma = 20%."""
    S, K, T, r, s = 100.0, 100.0, 0.5, 0.04, 0.20
    C = float(bs_price(S, K, T, r, s, 'call')); P = float(bs_price(S, K, T, r, s, 'put'))
    return dict(C=C, P=P, pv_k=K * np.exp(-r * T), lhs=C - P, rhs=S - K * np.exp(-r * T))


# =============================================================================
# 2. ARBORELE BINOMIAL
# =============================================================================
def fig_binomial():
    """Convergenta arborelui CRR la Black-Scholes; put american vs european."""
    S, K, T, r, s = 100.0, 100.0, 1.0, 0.05, 0.20
    bs = float(bs_price(S, K, T, r, s, 'call'))
    Ns = np.arange(1, 201)
    crr = np.array([crr_price(S, K, T, r, s, k) for k in Ns])
    Sg = np.linspace(60, 140, 81)
    am = np.array([crr_price(x, K, T, r, s, 500, 'put', True) for x in Sg])
    eu = bs_price(Sg, K, T, r, s, 'put')
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.3))
    ax = axes[0]
    ax.plot(Ns, crr, color=MainBlue, lw=0.9, marker='o', ms=1.6, label='Binomial tree (CRR), $N$ steps')
    ax.axhline(bs, color=IDAred, lw=1.1, label=f'Black-Scholes ({bs:.3f})')
    ax.set_xlabel('Number of steps $N$'); ax.set_ylabel('Call price')
    ax.set_title('European call, $S = K = 100$, $T = 1$, $r = 5\\%$, $\\sigma = 20\\%$', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    ax = axes[1]
    ax.plot(Sg, am, color=Forest, lw=1.4, label='American put (CRR, 500 steps)')
    ax.plot(Sg, eu, color=Purple, lw=1.1, ls='--', label='European put (Black-Scholes)')
    ax.plot(Sg, np.maximum(K - Sg, 0), color=Gray, lw=0.8, ls=':', label='Exercise value $\\max(K - S, 0)$')
    ax.set_xlabel('Price of the underlying $S$'); ax.set_ylabel('Put price')
    ax.set_title('Early exercise has a value for puts', fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch12_binomial')
    am100 = crr_price(S, K, T, r, s, 2000, 'put', True)
    eu100 = float(bs_price(S, K, T, r, s, 'put'))
    return dict(bs=bs, crr10=crr_price(S, K, T, r, s, 10), crr11=crr_price(S, K, T, r, s, 11),
                crr50=crr_price(S, K, T, r, s, 50), crr200=crr_price(S, K, T, r, s, 200),
                crr1000=crr_price(S, K, T, r, s, 1000), am_put=am100, eu_put=eu100, eep=am100 - eu100)


# =============================================================================
# 3. BLACK-SCHOLES SI SENZITIVITATI
# =============================================================================
def bs_example():
    """Exemplu lucrat: S = 100, K = 105, T = 3 luni, r = 4%, sigma = 16%."""
    S, K, T, r, s = 100.0, 105.0, 0.25, 0.04, 0.16
    g = bs_greeks(S, K, T, r, s, 'call')
    gp = bs_greeks(S, K, T, r, s, 'put')
    return dict(d1=float(g['d1']), d2=float(g['d2']), Nd1=float(stats.norm.cdf(g['d1'])), Nd2=float(stats.norm.cdf(g['d2'])),
                call=float(bs_price(S, K, T, r, s, 'call')), put=float(bs_price(S, K, T, r, s, 'put')),
                pvk=K * np.exp(-r * T), delta=float(g['delta']), gamma=float(g['gamma']), vega=float(g['vega']),
                theta=float(g['theta']), rho=float(g['rho']), delta_put=float(gp['delta']), theta_put=float(gp['theta']))


def fig_greeks():
    """Delta, gamma, vega si theta ale unei optiuni call (K = 100, sigma = 20%, r = 4%) pentru trei scadente."""
    S = np.linspace(60, 140, 401)
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 2.9))
    cols = {1 / 12: IDAred, 0.25: MainBlue, 1.0: Forest}
    for T, c in cols.items():
        g = bs_greeks(S, 100, T, 0.04, 0.20, 'call')
        for ax, k in zip(axes, ['delta', 'gamma', 'vega', 'theta']):
            ax.plot(S, g[k], color=c, lw=1.3)
    for ax, t in zip(axes, ['Delta $\\partial C/\\partial S$', 'Gamma $\\partial^2 C/\\partial S^2$',
                            'Vega (per volatility point)', 'Theta (per calendar day)']):
        ax.set_title(t, fontsize=9, loc='left'); ax.set_xlabel('$S$')
        ax.axvline(100, color=Gray, lw=0.5, ls=':')
    fig_legend_bottom(fig, [Line2D([], [], color=c, lw=1.3, label=l) for c, l in
                            [(IDAred, 'One month to expiry'), (MainBlue, 'Three months'), (Forest, 'One year')]], ncol=3, y=-0.02)
    plt.tight_layout()
    save_fig('ch12_greeks')


# =============================================================================
# 4. ACOPERIREA DELTA
# =============================================================================
def gbm_paths(S0, mu, sigma, T, nstep, npath, seed=SEED):
    rng = np.random.default_rng(seed)
    dt = T / nstep
    z = rng.standard_normal((npath, nstep))
    x = np.cumsum((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z, axis=1)
    return S0 * np.exp(np.hstack([np.zeros((npath, 1)), x]))


HEDGE = dict(S0=100.0, K=100.0, T=0.25, r=0.04, sigma=0.20, mu=0.08, nstep=252, npath=20000)


def fig_hedge_path():
    """O traiectorie: valoarea optiunii vs valoarea portofoliului de replicare (acoperire zilnica)."""
    h = HEDGE
    p = gbm_paths(h['S0'], h['mu'], h['sigma'], h['T'], 63, 1, seed=7)[0]
    t = np.linspace(0, h['T'], 64)
    V = np.array([float(bs_price(p[i], h['K'], h['T'] - t[i], h['r'], h['sigma'])) if i < 63 else max(p[i] - h['K'], 0)
                  for i in range(64)])
    delta = float(bs_greeks(p[0], h['K'], h['T'], h['r'], h['sigma'])['delta'])
    cash = V[0] - delta * p[0]
    port = [V[0]]
    dt = h['T'] / 63
    for i in range(1, 64):
        cash *= np.exp(h['r'] * dt)
        port.append(cash + delta * p[i])
        if i < 63:
            d_new = float(bs_greeks(p[i], h['K'], h['T'] - t[i], h['r'], h['sigma'])['delta'])
            cash -= (d_new - delta) * p[i]
            delta = d_new
    days = np.arange(64)
    fig, axes = plt.subplots(2, 1, figsize=(8, 4.2), sharex=True, gridspec_kw={'height_ratios': [1, 1.2]})
    axes[0].plot(days, p, color=MainBlue, lw=1.2, label='Simulated price of the underlying $S_t$')
    axes[0].axhline(h['K'], color=Gray, lw=0.5, ls=':')
    axes[0].set_ylabel('$S_t$')
    axes[1].plot(days, V, color=IDAred, lw=1.4, label='Value of the call $C_t$ (Black-Scholes)')
    axes[1].plot(days, port, color=Forest, lw=1.2, ls='--', label='Replicating portfolio: $\\Delta_t$ shares + cash')
    axes[1].set_ylabel('Value'); axes[1].set_xlabel('Trading day')
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch12_hedge_path')
    return dict(err=float(port[-1] - V[-1]), premium=float(V[0]), ST=float(p[-1]))


def hedge_errors():
    """Eroarea de acoperire pentru mai multe frecvente de reechilibrare (20 000 de traiectorii GBM)."""
    h = HEDGE
    paths = gbm_paths(h['S0'], h['mu'], h['sigma'], h['T'], h['nstep'], h['npath'])
    prem = float(bs_price(h['S0'], h['K'], h['T'], h['r'], h['sigma']))
    out = {}
    for nr in [1, 3, 6, 12, 21, 63, 126, 252]:
        e = delta_hedge(paths, h['K'], h['T'], h['r'], h['sigma'], nr)
        out[nr] = e
    return out, prem


def fig_hedge_error(errs, prem):
    labels = {3: 'Monthly (3 rebalancings)', 12: 'Weekly (12)', 63: 'Daily (63)', 252: 'Four times a day (252)'}
    cols = {3: Orange, 12: Purple, 63: MainBlue, 252: Forest}
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.3), gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    bins = np.linspace(-4, 4, 121)
    for nr in [3, 12, 63, 252]:
        ax.hist(errs[nr], bins=bins, histtype='step', color=cols[nr], lw=1.3, density=True, label=labels[nr])
    ax.set_xlabel('Hedging error at expiry (per option, $S_0 = 100$)'); ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    ax = axes[1]
    ns = np.array(sorted(errs)); sd = np.array([errs[k].std() for k in ns])
    ax.loglog(ns, sd / prem * 100, 'o-', color=MainBlue, ms=4, label='Standard deviation of the error, % of premium')
    ref = sd[4] / prem * 100 * np.sqrt(ns[4] / ns)
    ax.loglog(ns, ref, color=Gray, lw=0.8, ls='--', label='Slope $-1/2$: error $\\propto 1/\\sqrt{N}$')
    ax.set_xlabel('Number of rebalancings $N$'); ax.set_ylabel('% of the premium')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch12_hedge_error')
    slope = np.polyfit(np.log(ns[1:]), np.log(sd[1:]), 1)[0]
    return dict(premium=prem, slope=float(slope),
                sd={str(k): float(errs[k].std()) for k in ns}, sdpct={str(k): float(errs[k].std() / prem * 100) for k in ns},
                mean={str(k): float(errs[k].mean()) for k in ns},
                q01_63=float(np.quantile(errs[63], 0.01)), q01_12=float(np.quantile(errs[12], 0.01)))


def fig_vol_mismatch():
    """Vanzatorul acoperit delta la sigma implicita 20%, cand volatilitatea realizata este 15%, 20% sau 25%."""
    h = HEDGE
    prem = float(bs_price(h['S0'], h['K'], h['T'], h['r'], 0.20))
    vega = float(bs_greeks(h['S0'], h['K'], h['T'], h['r'], 0.20)['vega'])
    res = {}
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    bins = np.linspace(-6, 6, 121)
    for sr, c in [(0.15, Forest), (0.20, MainBlue), (0.25, IDAred)]:
        paths = gbm_paths(h['S0'], h['mu'], sr, h['T'], 63, h['npath'], seed=11)
        e = delta_hedge(paths, h['K'], h['T'], h['r'], 0.20, 63)
        res[f'{int(sr * 100)}'] = dict(mean=float(e.mean()), sd=float(e.std()), win=float((e > 0).mean()))
        ax.hist(e, bins=bins, histtype='step', lw=1.4, density=True, color=c,
                label=f'Realised volatility {int(sr * 100)}%: mean P&L {e.mean():+.2f}')
    ax.axvline(0, color=Gray, lw=0.6)
    ax.set_xlabel('P&L of the seller of a 3-month call, hedged daily at 20% implied volatility')
    ax.set_ylabel('Density')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch12_vol_mismatch')
    return dict(premium=prem, vega=vega, **res)


def delta_hedged_history():
    """S&P 500: vinde lunar o optiune call ATM pe 21 de zile la volatilitatea VIX si o acopera zilnic (1990-2026)."""
    px = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    S, V = px['sp500'].values, px['vix'].values / 100
    dates = px.index
    H, T = 21, 21 / 252
    rows = []
    for i0 in range(0, len(px) - H, H):
        s0, sig = S[i0], V[i0]
        K = s0
        prem = float(bs_price(s0, K, T, 0.0, sig))
        delta = float(bs_greeks(s0, K, T, 0.0, sig)['delta'])
        cash = prem - delta * s0
        for i in range(1, H + 1):
            if i < H:
                d_new = float(bs_greeks(S[i0 + i], K, T * (H - i) / H, 0.0, sig)['delta'])
                cash -= (d_new - delta) * S[i0 + i]
                delta = d_new
        pnl = cash + delta * S[i0 + H] - max(S[i0 + H] - K, 0)
        rv = np.sqrt(252 / H * np.sum(np.diff(np.log(S[i0:i0 + H + 1])) ** 2))
        rows.append(dict(date=dates[i0], pnl=100 * pnl / s0, prem=100 * prem / s0, vix=sig * 100, rv=rv * 100))
    return pd.DataFrame(rows).set_index('date')


def fig_delta_hedged(d):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), gridspec_kw={'width_ratios': [1.8, 1]})
    ax = axes[0]
    ax.bar(d.index, d['pnl'], width=25, color=np.where(d['pnl'] >= 0, Forest, IDAred))
    ax.axhline(0, color=Gray, lw=0.5)
    ax.set_ylabel('P&L, % of the index level')
    ax.set_title('Seller of a one-month ATM call on the S&P 500, hedged daily at the VIX', fontsize=8.8, loc='left')
    ax = axes[1]
    ax.hist(d['pnl'], bins=60, color=MainBlue, alpha=0.85)
    ax.axvline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Monthly P&L (% of the index level)'); ax.set_ylabel('Number of months')
    fig_legend_bottom(fig, [Patch(color=Forest, label='Month with a gain'), Patch(color=IDAred, label='Month with a loss'),
                            Patch(color=MainBlue, label='All months (histogram)')], ncol=3, y=-0.02)
    plt.tight_layout()
    save_fig('ch12_delta_hedged_sp500')
    m, se = nw_mean(d['pnl'], 3)
    w = d['pnl'].idxmin()
    return dict(n=int(len(d)), mean=m, se=se, t=m / se, sd=float(d['pnl'].std()), win=float((d['pnl'] > 0).mean()),
                worst=float(d['pnl'].min()), worst_date=w.strftime('%Y-%m'), best=float(d['pnl'].max()),
                prem=float(d['prem'].mean()), skew=float(stats.skew(d['pnl'])),
                vix=float(d['vix'].mean()), rv=float(d['rv'].mean()), start=d.index[0].strftime('%Y-%m'),
                share_vix_gt_rv=float((d['vix'] > d['rv']).mean()))


# =============================================================================
# 5. ZAMBETUL DE VOLATILITATE: DE CE EXISTA
# =============================================================================
def smile_from_prices(S, Ks, T, price_fn):
    """Volatilitati implicite din preturi: put OTM sub S, call OTM peste S."""
    out = []
    for K in Ks:
        kind = 'put' if K < S else 'call'
        out.append(implied_vol(price_fn(K, kind), S, K, T, 0.0, kind))
    return np.array(out)


def fig_smile_models():
    """Zambete de volatilitate pe o luna: randamente empirice S&P 500, salturi Merton, volatilitate stocastica Heston."""
    S, T = 100.0, 21 / 252
    Ks = np.linspace(80, 120, 41)
    lr = np.log(load_close('sp500'))
    R = (lr.shift(-21) - lr).dropna().values
    ST = S * np.exp(R) / np.mean(np.exp(R))           # medie neutra la risc (r = 0)
    emp = lambda K, kind: np.mean(np.maximum(ST - K, 0)) if kind == 'call' else np.mean(np.maximum(K - ST, 0))
    mer = lambda K, kind: float(merton_price(S, K, T, 0.0, 0.14, 1.0, -0.08, 0.08, kind))
    hes = lambda K, kind: heston_price(S, K, T, 0.0, 0.03, 3.0, 0.04, 0.8, -0.7, kind)
    iv = {'emp': smile_from_prices(S, Ks, T, emp), 'mer': smile_from_prices(S, Ks, T, mer),
          'hes': smile_from_prices(S, Ks, T, hes)}
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(Ks / S, 100 * iv['emp'], color=MainBlue, lw=1.6, label='Historical one-month S&P 500 returns, 1990-2026 (fat tails)')
    ax.plot(Ks / S, 100 * iv['mer'], color=IDAred, lw=1.3, ls='--', label='Merton jump-diffusion: one crash a year of -8% on average')
    ax.plot(Ks / S, 100 * iv['hes'], color=Forest, lw=1.3, ls='-.', label='Heston stochastic volatility, $\\rho = -0.7$')
    ax.axhline(100 * iv['emp'][20], color=Gray, lw=0.7, ls=':', label='Black-Scholes: one volatility for all strikes')
    ax.set_xlabel('Moneyness $K/S$'); ax.set_ylabel('Implied volatility (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch12_smile_models')
    i90, i100, i110 = 10, 20, 30
    return {k: dict(k90=float(100 * v[i90]), k100=float(100 * v[i100]), k110=float(100 * v[i110]),
                    k80=float(100 * v[0]), k120=float(100 * v[-1])) for k, v in iv.items()} | dict(
        skew_R=float(stats.skew(R)), kurt_R=float(stats.kurtosis(R)), nR=int(len(R)))


def fig_leverage():
    """Efectul de levier: randamentul zilnic S&P 500 vs variatia VIX in aceeasi zi (1990-2026)."""
    px = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    r = 100 * np.log(px['sp500']).diff()
    dv = px['vix'].diff()
    d = pd.concat([r, dv], axis=1).dropna()
    d.columns = ['r', 'dv']
    b = np.polyfit(d['r'], d['dv'], 1)
    rho = float(d.corr().iloc[0, 1])
    up, dn = d[d['r'] > 0], d[d['r'] < 0]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.scatter(d['r'], d['dv'], s=3, color=MainBlue, alpha=0.35, label='Trading days, 1990-2026')
    xx = np.linspace(d['r'].min(), d['r'].max(), 10)
    ax.plot(xx, b[1] + b[0] * xx, color=IDAred, lw=1.4, label=f'Least-squares line: slope {b[0]:.2f}')
    ax.axhline(0, color=Gray, lw=0.5); ax.axvline(0, color=Gray, lw=0.5)
    ax.set_xlabel('S&P 500 daily log return (%)'); ax.set_ylabel('Daily change of the VIX (points)')
    ax.text(0.98, 0.95, f'correlation {rho:.2f}', transform=ax.transAxes, ha='right', va='top', fontsize=8, color='black')
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch12_leverage')
    return dict(rho=rho, slope=float(b[0]), n=int(len(d)), dv_down=float(dn['dv'].mean()), dv_up=float(up['dv'].mean()),
                slope_dn=float(np.polyfit(dn['r'], dn['dv'], 1)[0]), slope_up=float(np.polyfit(up['r'], up['dv'], 1)[0]))


# =============================================================================
# 6. OPTIUNI BITCOIN: SUPRAFATA DE VOLATILITATE (Deribit)
# =============================================================================
def btc_surface():
    """SVI pe fiecare scadenta a lantului BTC (optiuni OTM cotate, cel putin 2 zile pana la scadenta)."""
    c = deribit_chain()
    t0 = c['snapshot_utc'].iloc[0]
    c['T'] = (c['expiry'] - t0).dt.total_seconds() / (365 * 86400)
    c = c[(c['T'] >= 2 / 365) & (c['mark_iv'] > 0) & (c['bid'] > 0)]
    c = c[((c['type'] == 'put') & (c['strike'] < c['forward'])) | ((c['type'] == 'call') & (c['strike'] >= c['forward']))].copy()
    c['k'] = np.log(c['strike'] / c['forward'])
    c['w'] = (c['mark_iv'] / 100) ** 2 * c['T']
    c = c[c['k'].abs() < 1.2]
    fits = {}
    for e, g in c.groupby('expiry'):
        if len(g) < 7:
            continue
        f = svi_fit(g['k'].values, g['w'].values)
        T = g['T'].iloc[0]
        iv = lambda k: 100 * np.sqrt(svi_w(k, f['a'], f['b'], f['rho'], f['m'], f['s']) / T)
        fits[e] = dict(T=T, days=T * 365, F=float(g['forward'].iloc[0]), n=int(len(g)), atm=float(iv(0.0)),
                       rr=float(iv(0.15) - iv(-0.15)), wing_dn=float(iv(-0.3)), wing_up=float(iv(0.3)),
                       rmse_iv=float(np.sqrt(np.mean((iv(g['k'].values) - g['mark_iv'].values) ** 2))), **f)
    tab = pd.DataFrame(fits).T
    tab.index.name = 'expiry'
    tab.to_csv(os.path.join(HERE, 'ch12_btc_svi.csv'))
    return c, tab, t0


def pick(tab, days):
    """Scadenta cea mai apropiata de un numar dat de zile."""
    return (tab['days'] - days).abs().astype(float).idxmin()


def fig_btc_smile(c, tab, t0):
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    cols = [IDAred, Orange, MainBlue, Forest, Purple]
    chosen = []
    for dd in [7, 30, 90, 180, 280]:
        e = pick(tab, dd)
        if e not in chosen:
            chosen.append(e)
    for e, col in zip(chosen, cols):
        g = c[c['expiry'] == e]; f = tab.loc[e]
        kk = np.linspace(g['k'].min(), g['k'].max(), 200)
        ax.scatter(g['k'], g['mark_iv'], s=9, color=col)
        ax.plot(kk, 100 * np.sqrt(svi_w(kk, f['a'], f['b'], f['rho'], f['m'], f['s']) / f['T']), color=col, lw=1.2,
                label=f"{pd.Timestamp(e).strftime('%d %b %Y')} ({f['days']:.0f} days)")
    ax.axvline(0, color=Gray, lw=0.5, ls=':')
    ax.set_xlabel('Log-moneyness $k = \\ln(K/F)$'); ax.set_ylabel('Implied volatility (%)')
    ax.set_title(f"Bitcoin options, Deribit, {pd.Timestamp(t0).strftime('%d %B %Y %H:%M')} UTC: quotes (dots) and SVI fits (lines)",
                 fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch12_btc_smile')
    return [str(pd.Timestamp(e).date()) for e in chosen]


def fig_btc_term(tab, dvol_now):
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.1))
    ax = axes[0]
    ax.plot(tab['days'].astype(float), tab['atm'].astype(float), 'o-', color=MainBlue, ms=4, label='At-the-money implied volatility (SVI, $k = 0$)')
    ax.axhline(dvol_now, color=Amber, lw=1.1, ls='--', label=f'DVOL index at the snapshot: {dvol_now:.1f}')
    ax.set_xlabel('Days to expiry'); ax.set_ylabel('Implied volatility (%)')
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    ax = axes[1]
    ax.plot(tab['days'].astype(float), tab['rr'].astype(float), 's-', color=Purple, ms=4,
            label='Skew: IV($k = +0.15$) $-$ IV($k = -0.15$)')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_xlabel('Days to expiry'); ax.set_ylabel('Volatility points')
    legend_outside_bottom(ax, ncol=1, y=-0.22)
    plt.tight_layout()
    save_fig('ch12_btc_term')


def cboe_strip(g, F, S):
    """Banda de optiuni a formulei Cboe pentru o scadenta (Cboe, sectiunea 3(a)(iii)): K0 = primul pret de exercitare
    egal cu sau imediat sub F; put-uri sub K0 si call-uri peste K0, fara cele cu bid zero, oprire dupa doua preturi
    de exercitare consecutive cu bid zero; la K0 media put-ului si a call-ului. Q = pretul mid in USD
    (prima in BTC inmultita cu indicele S, conventia Deribit)."""
    g = g.assign(mid=0.5 * (g['bid'] + g['ask']) * S, bid0=g['bid'].fillna(0.0))
    Ks = np.sort(g['strike'].unique())
    K0 = Ks[Ks <= F].max()
    side = {t: g[g['type'] == t].set_index('strike').sort_index() for t in ('put', 'call')}
    rows = []
    for t, seq in (('put', Ks[Ks < K0][::-1]), ('call', Ks[Ks > K0])):
        zeros = 0
        for K in seq:
            if K not in side[t].index or side[t].loc[K, 'bid0'] <= 0:
                zeros += 1
                if zeros == 2:
                    break
                continue
            zeros = 0
            rows.append((K, float(side[t].loc[K, 'mid'])))
    rows.append((K0, 0.5 * float(side['put'].loc[K0, 'mid'] + side['call'].loc[K0, 'mid'])))
    rows.sort()
    return np.array([r[0] for r in rows]), np.array([r[1] for r in rows]), float(K0)


def btc_vix(c_all=None):
    """Indice de tip VIX pe 30 de zile din lantul BTC (formula Cboe): preturi mid in USD (prima in BTC x indicele S),
    rata R = ln(F/S)/T implicita in forward-ul Deribit, deci e^{RT} Q = prima in BTC x F."""
    c = deribit_chain() if c_all is None else c_all
    t0 = c['snapshot_utc'].iloc[0]
    c = c.copy()
    c['T'] = (c['expiry'] - t0).dt.total_seconds() / (365 * 86400)
    exps = sorted(c['expiry'].unique())
    Td = {e: c.loc[c['expiry'] == e, 'T'].iloc[0] * 365 for e in exps}
    near = max(e for e in exps if Td[e] < 30)
    nxt = min(e for e in exps if Td[e] >= 30)
    res = {}
    for tag, e in [('near', near), ('next', nxt)]:
        g = c[c['expiry'] == e]
        F = float(g['forward'].iloc[0]); S = float(g['index'].iloc[0]); T = float(g['T'].iloc[0])
        K, Q, K0 = cboe_strip(g, F, S)
        R = np.log(F / S) / T
        v = variance_from_strip(K, Q, F, T, R)
        res[tag] = dict(expiry=str(pd.Timestamp(e).date()), days=float(T * 365), F=F, S=S, R=float(R), K0=K0,
                        n=int(len(K)), var=float(v), vol=float(100 * np.sqrt(v)),
                        kf_min=float(K.min() / F), kf_max=float(K.max() / F))
    T1, T2 = res['near']['days'], res['next']['days']
    w1 = (T2 - 30) / (T2 - T1)
    v30 = (T1 * res['near']['var'] * w1 + T2 * res['next']['var'] * (1 - w1)) / 30
    res['index'] = float(100 * np.sqrt(v30))
    return res


def dvol_now():
    """Valoarea DVOL la momentul instantaneului: inchiderea ultimului minut complet inainte de ora instantaneului."""
    t0 = pd.Timestamp(deribit_chain()['snapshot_utc'].iloc[0]).tz_localize('UTC')
    t1 = int(t0.timestamp() * 1000)
    r = _get('get_volatility_index_data', currency='BTC', start_timestamp=t1 - 3_600_000, end_timestamp=t1, resolution='60')
    d = pd.DataFrame(r['data'], columns=['t', 'open', 'high', 'low', 'close'])
    d = d[d['t'] + 60_000 <= t1]
    last = d.iloc[-1]
    return float(last['close']), str(pd.to_datetime(last['t'] + 60_000, unit='ms'))


# =============================================================================
# 7. VIX: ISTORIE, STRUCTURA LA TERMEN, VVIX, PRIMA DE RISC A VARIANTEI
# =============================================================================
def fig_vix_history():
    v = load_close('vix')
    peaks = []
    s = v.copy()
    for _ in range(6):
        d = s.idxmax()
        peaks.append((d, float(v[d])))
        s = s[(s.index < d - pd.Timedelta(days=500)) | (s.index > d + pd.Timedelta(days=500))]
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(v.index, v.values, color=MainBlue, lw=0.7, label='VIX, daily close')
    ax.axhline(v.mean(), color=Gray, lw=0.7, ls='--', label=f'Mean 1990-2026: {v.mean():.1f}')
    for d, x in peaks:
        ax.annotate(f"{d.strftime('%b %Y')}\n{x:.1f}", (d, x), xytext=(0, 4), textcoords='offset points', ha='center',
                    va='bottom', fontsize=6.8, color='black')
    ax.set_ylim(0, 95); ax.set_ylabel('VIX (annualised %, 30 days)')
    legend_outside_bottom(ax, ncol=2, y=-0.14)
    save_fig('ch12_vix_history')
    return dict(mean=float(v.mean()), median=float(v.median()), min=float(v.min()), min_date=str(v.idxmin().date()),
                max=float(v.max()), max_date=str(v.idxmax().date()), share30=float((v > 30).mean()),
                share15=float((v < 15).mean()), last=float(v.iloc[-1]), n=int(len(v)),
                peaks=[(str(d.date()), x) for d, x in peaks])


def fig_vix_term():
    px = pd.concat([load_close('vix9d'), load_close('vix'), load_close('vix3m'), load_close('sp500')], axis=1, join='inner').dropna()
    ratio = px['vix'] / px['vix3m']
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.4), sharex=True, gridspec_kw={'height_ratios': [1.5, 1]})
    ax = axes[0]
    ax.plot(px.index, px['vix9d'], color=Teal, lw=0.6, label='VIX9D (9 days)')
    ax.plot(px.index, px['vix'], color=MainBlue, lw=0.7, label='VIX (30 days)')
    ax.plot(px.index, px['vix3m'], color=Purple, lw=0.7, label='VIX3M (3 months)')
    ax.set_ylabel('Implied volatility (%)')
    ax = axes[1]
    ax.plot(ratio.index, ratio.values, color=Forest, lw=0.6, label='Ratio VIX / VIX3M')
    ax.fill_between(ratio.index, 1, ratio.values, where=ratio.values > 1, color=IDAred, alpha=0.5, lw=0,
                    label='Backwardation: VIX above VIX3M')
    ax.axhline(1, color=Gray, lw=0.6)
    ax.set_ylabel('VIX / VIX3M')
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch12_vix_term')
    lr = np.log(px['sp500'])
    fwd = 100 * (lr.shift(-21) - lr)
    rv = 100 * np.sqrt(252 / 21 * (lr.diff() ** 2).rolling(21).sum().shift(-21))
    back = ratio > 1
    ok = fwd.notna()
    return dict(start=str(px.index[0].date()), n=int(len(px)), share_back=float(back.mean()),
                mean_ratio=float(ratio.mean()), share_9d_below=float((px['vix9d'] < px['vix']).mean()),
                fwd_back=float(fwd[back & ok].mean()), fwd_cont=float(fwd[~back & ok].mean()),
                rv_back=float(rv[back & rv.notna()].mean()), rv_cont=float(rv[~back & rv.notna()].mean()),
                last_ratio=float(ratio.iloc[-1]), last_vix9d=float(px['vix9d'].iloc[-1]), last_vix3m=float(px['vix3m'].iloc[-1]))


def fig_vvix():
    px = pd.concat([load_close('vix'), load_close('vvix')], axis=1, join='inner').dropna()
    fig, axes = plt.subplots(2, 1, figsize=(9, 3.9), sharex=True)
    axes[0].plot(px.index, px['vix'], color=MainBlue, lw=0.7, label='VIX: implied volatility of the S&P 500')
    axes[1].plot(px.index, px['vvix'], color=Purple, lw=0.7, label='VVIX: implied volatility of the VIX')
    axes[0].set_ylabel('VIX'); axes[1].set_ylabel('VVIX')
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch12_vvix')
    d = px.diff().dropna()
    return dict(start=str(px.index[0].date()), mean=float(px['vvix'].mean()), max=float(px['vvix'].max()),
                max_date=str(px['vvix'].idxmax().date()), corr_d=float(d.corr().iloc[0, 1]),
                corr_lvl=float(px.corr().iloc[0, 1]), ratio=float((px['vvix'] / px['vix']).mean()))


def vrp_sp500():
    """Prima de risc a variantei: VIX^2 minus varianta realizata in urmatoarele 21 de zile de tranzactionare."""
    px = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    r = np.log(px['sp500']).diff()
    rv = 252 / 21 * (r ** 2).rolling(21).sum().shift(-21) * 1e4       # (%)^2 anualizat
    d = pd.DataFrame({'vix': px['vix'], 'iv2': px['vix'] ** 2, 'rv': rv, 'rv_past': rv.shift(21)}).dropna()
    d['vrp'] = d['iv2'] - d['rv']
    d['vrp_vol'] = d['vix'] - np.sqrt(d['rv'])
    return d


def fig_vrp(d):
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.4), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    ax = axes[0]
    ax.plot(d.index, d['vix'], color=MainBlue, lw=0.6, label='VIX at day $t$ (implied, next 30 days)')
    ax.plot(d.index, np.sqrt(d['rv']), color=IDAred, lw=0.6, label='Realised volatility over the next 21 trading days')
    ax.set_ylabel('Annualised %')
    ax = axes[1]
    ax.plot(d.index, d['vrp_vol'], color=Forest, lw=0.5, label='Premium in volatility points: VIX $-\\sqrt{RV}$')
    ax.axhline(0, color=Gray, lw=0.6)
    ax.set_ylabel('Volatility points'); ax.set_ylim(-45, 30)
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch12_vrp')
    m, se = nw_mean(d['vrp'], 21)
    mv, sev = nw_mean(d['vrp_vol'], 21)
    w = d['vrp_vol'].idxmin()
    return dict(n=int(len(d)), start=str(d.index[0].date()), end=str(d.index[-1].date()), mean=m, se=se, t=m / se,
                mean_vol=mv, se_vol=sev, share_pos=float((d['vrp'] > 0).mean()), vix=float(d['vix'].mean()),
                rv=float(np.sqrt(d['rv']).mean()), worst=float(d['vrp_vol'].min()), worst_date=str(w.date()),
                median_vol=float(d['vrp_vol'].median()))


def fig_mz(d):
    """Regresia Mincer-Zarnowitz: varianta realizata viitoare pe VIX^2 (erori standard Newey-West, 21 de lag-uri)."""
    X = sm.add_constant(d[['iv2']])
    m1 = sm.OLS(d['rv'], X).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
    m2 = sm.OLS(d['rv'], sm.add_constant(d[['rv_past']])).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
    m3 = sm.OLS(d['rv'], sm.add_constant(d[['iv2', 'rv_past']])).fit(cov_type='HAC', cov_kwds={'maxlags': 21})
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    ax.scatter(d['vix'], np.sqrt(d['rv']), s=2, color=MainBlue, alpha=0.3, label='Trading days (VIX, realised volatility next 21 days)')
    xx = np.linspace(9, 85, 50)
    ax.plot(xx, xx, color=Gray, lw=0.8, ls='--', label='45-degree line: realised = implied')
    ax.plot(xx, np.sqrt(np.clip(m1.params['const'] + m1.params['iv2'] * xx ** 2, 0, None)), color=IDAred, lw=1.4,
            label='Mincer-Zarnowitz fit (in variance)')
    ax.set_xlabel('VIX at day $t$'); ax.set_ylabel('Realised volatility, next 21 days (%)')
    ax.set_xlim(8, 85); ax.set_ylim(0, 110)
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    save_fig('ch12_vix_rv_mz')
    wald = m1.t_test('iv2 = 1')
    return dict(a=float(m1.params['const']), a_se=float(m1.bse['const']), b=float(m1.params['iv2']), b_se=float(m1.bse['iv2']),
                r2=float(m1.rsquared), t_b1=float(wald.tvalue), r2_past=float(m2.rsquared), r2_both=float(m3.rsquared),
                b_both=float(m3.params['iv2']), c_both=float(m3.params['rv_past']),
                b_both_se=float(m3.bse['iv2']), c_both_se=float(m3.bse['rv_past']))


def vrp_btc():
    """Bitcoin: DVOL minus volatilitatea realizata in urmatoarele 30 de zile calendaristice."""
    dv = dvol_history()
    p = load_close('btc')
    r = np.log(p).diff()
    rv = 365 / 30 * (r ** 2).rolling(30).sum().shift(-30) * 1e4
    d = pd.concat([dv, rv.rename('rv')], axis=1, join='inner').dropna()
    d['vrp'] = d['dvol'] ** 2 - d['rv']
    d['vrp_vol'] = d['dvol'] - np.sqrt(d['rv'])
    return d


def fig_vrp_btc(d):
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.2), sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    axes[0].plot(d.index, d['dvol'], color=Amber, lw=0.8, label='DVOL at day $t$ (implied, next 30 days)')
    axes[0].plot(d.index, np.sqrt(d['rv']), color=IDAred, lw=0.7, label='Realised volatility over the next 30 days')
    axes[0].set_ylabel('Annualised %')
    axes[1].plot(d.index, d['vrp_vol'], color=Forest, lw=0.7, label='Premium in volatility points')
    axes[1].axhline(0, color=Gray, lw=0.6)
    axes[1].set_ylabel('Volatility points')
    h1, l1 = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch12_vrp_btc')
    m, se = nw_mean(d['vrp'], 30)
    mv, sev = nw_mean(d['vrp_vol'], 30)
    return dict(n=int(len(d)), start=str(d.index[0].date()), end=str(d.index[-1].date()), mean=m, se=se, t=m / se,
                mean_vol=mv, se_vol=sev, t_vol=mv / sev, share_pos=float((d['vrp'] > 0).mean()),
                dvol=float(d['dvol'].mean()), rv=float(np.sqrt(d['rv']).mean()),
                worst=float(d['vrp_vol'].min()), worst_date=str(d['vrp_vol'].idxmin().date()))


# =============================================================================
# 8. OPTIUNI CU ZERO ZILE PANA LA SCADENTA (0DTE)
# =============================================================================
def fig_0dte_gamma():
    S = np.linspace(95, 105, 401)
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.0))
    for T, c, lab in [(1 / 252, IDAred, 'One trading day'), (5 / 252, Orange, 'One week'), (21 / 252, MainBlue, 'One month')]:
        g = bs_greeks(S, 100, T, 0.0, 0.16, 'call')
        axes[0].plot(S, g['gamma'], color=c, lw=1.3, label=lab)
    axes[0].set_xlabel('$S$ (strike $K = 100$, volatility 16%)'); axes[0].set_ylabel('Gamma')
    legend_outside_bottom(axes[0], ncol=3, y=-0.22)
    days = np.linspace(0.25, 30, 300)
    th = -bs_greeks(100, 100, days / 365, 0.0, 0.16, 'call')['theta']
    axes[1].plot(days, th, color=Purple, lw=1.4, label='Time decay of an ATM call (price lost per calendar day)')
    axes[1].set_xlabel('Calendar days to expiry'); axes[1].set_ylabel('$-\\Theta$ per day')
    axes[1].invert_xaxis()
    legend_outside_bottom(axes[1], ncol=1, y=-0.22)
    plt.tight_layout()
    save_fig('ch12_0dte_gamma')
    g1 = float(bs_greeks(100, 100, 1 / 252, 0, 0.16)['gamma']); g21 = float(bs_greeks(100, 100, 21 / 252, 0, 0.16)['gamma'])
    return dict(g1=g1, g21=g21, ratio=g1 / g21, th1=float(-bs_greeks(100, 100, 1 / 365, 0, 0.16)['theta']),
                th30=float(-bs_greeks(100, 100, 30 / 365, 0, 0.16)['theta']))


def odte_straddle():
    """Vanzarea stilizata a unui straddle ATM cu scadenta in aceeasi zi pe SPY, de la deschidere la inchidere (2011-2026).
    Volatilitatea implicita a sesiunii: VIX9D din ziua precedenta, scalata cu ponderea variantei din timpul sesiunii
    (estimata pe 1993-2010, in afara perioadei de test). Prima = sqrt(2/pi) x sigma_sesiune x pretul de deschidere."""
    oc = spy_open_close()
    adj = load_close('spy')
    cc = np.log(adj).diff()
    oc_r = np.log(oc['close'] / oc['open'])
    both = pd.concat([oc_r.rename('oc'), cc.rename('cc')], axis=1).dropna()
    est = both.loc[:'2010-12-31']
    phi = float((est['oc'] ** 2).sum() / (est['cc'] ** 2).sum())
    v9 = load_close('vix9d').shift(1)
    d = pd.concat([oc, v9.rename('v9')], axis=1, join='inner').dropna().loc['2011-01-04':]
    sig = d['v9'] / 100 * np.sqrt(phi / 252)
    d['prem'] = 100 * np.sqrt(2 / np.pi) * sig
    d['pay'] = 100 * (d['close'] / d['open'] - 1).abs()
    d['pnl'] = d['prem'] - d['pay']
    return d, phi


def fig_0dte_straddle(d, phi):
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.2), gridspec_kw={'width_ratios': [1.7, 1]})
    cum = d['pnl'].cumsum()
    axes[0].plot(cum.index, cum.values, color=MainBlue, lw=1.0, label='Cumulative P&L of the seller (% of the price, summed)')
    axes[0].axhline(0, color=Gray, lw=0.5)
    axes[0].set_ylabel('Cumulative P&L (%)')
    legend_outside_bottom(axes[0], ncol=1, y=-0.14)
    axes[1].hist(d['pnl'], bins=np.linspace(-3, 0.6, 73), color=Purple, alpha=0.85, label='Daily P&L of the seller')
    axes[1].axvline(0, color=Gray, lw=0.6)
    axes[1].set_xlabel('Daily P&L (% of the price)'); axes[1].set_ylabel('Days')
    legend_outside_bottom(axes[1], ncol=1, y=-0.22)
    plt.tight_layout()
    save_fig('ch12_0dte_straddle')
    x = d['pnl']
    dd = (cum - cum.cummax()).min()
    w = x.idxmin()
    return dict(phi=phi, n=int(len(x)), start=str(d.index[0].date()), mean_bp=float(100 * x.mean()), sd=float(x.std()),
                sharpe=float(x.mean() / x.std() * np.sqrt(252)), win=float((x > 0).mean()), worst=float(x.min()),
                worst_date=str(w.date()), maxdd=float(dd), prem=float(d['prem'].mean()), pay=float(d['pay'].mean()),
                skew=float(stats.skew(x)), cum=float(cum.iloc[-1]),
                share_big=float((d['pay'] > 2 * d['prem']).mean()))


# =============================================================================
# 9. INFERENTA: CONSTRANGERI DE ARBITRAJ, BANDE PENTRU DENSITATE, VARIANTA FARA MODEL, PROGNOZA VIX, PREDICTIBILITATE
# =============================================================================
def svi_gk(k, a, b, rho, m, s):
    """Functia g(k) a lui Gatheral-Jacquier (2014): fara arbitraj de tip fluture daca g(k) >= 0 si w > 0."""
    W = svi_w(k, a, b, rho, m, s)
    W1 = b * (rho + (k - m) / np.sqrt((k - m) ** 2 + s ** 2))
    W2 = b * s ** 2 / ((k - m) ** 2 + s ** 2) ** 1.5
    return (1 - k * W1 / (2 * W)) ** 2 - W1 ** 2 / 4 * (1 / W + 0.25) + W2 / 2


def svi_no_arbitrage(tab):
    """Verificarile de absenta a arbitrajului pentru fiecare SVI: panta aripilor (Lee, 2004), g(k) >= 0 si w(k) > 0
    (Gatheral-Jacquier, 2014), si arbitrajul de calendar dw/dtau >= 0 intre scadente consecutive."""
    kg = np.linspace(-1.5, 1.5, 3001)
    rows = {}
    for e, f in tab.iterrows():
        p = [float(f[x]) for x in ['a', 'b', 'rho', 'm', 's']]
        rows[str(pd.Timestamp(e).date())] = dict(days=float(f['days']), slope_left=p[1] * (1 - p[2]),
                                                 slope_right=p[1] * (1 + p[2]), wmin=float(svi_w(kg, *p).min()),
                                                 gmin=float(svi_gk(kg, *p).min()))
    ex = list(tab.index)
    kc = np.linspace(-0.5, 0.5, 201)
    cal = []
    for e1, e2 in zip(ex[:-1], ex[1:]):
        p1 = [float(tab.loc[e1, x]) for x in ['a', 'b', 'rho', 'm', 's']]
        p2 = [float(tab.loc[e2, x]) for x in ['a', 'b', 'rho', 'm', 's']]
        dw = svi_w(kc, *p2) - svi_w(kc, *p1)
        cal.append(dict(e1=str(pd.Timestamp(e1).date()), e2=str(pd.Timestamp(e2).date()), min_dw=float(dw.min()),
                        share_viol=float((dw < 0).mean())))
    lee = max(max(r['slope_left'], r['slope_right']) for r in rows.values())
    return dict(per_expiry=rows, calendar=cal, max_slope=float(lee), n_exp=len(rows),
                n_g_neg=int(sum(r['gmin'] < 0 for r in rows.values())),
                n_w_neg=int(sum(r['wmin'] <= 0 for r in rows.values())),
                n_cal_viol=int(sum(c['min_dw'] < 0 for c in cal)), n_pairs=len(cal))


def rnd_from_svi(p, F, T, K):
    """Densitatea neutra la risc (Breeden-Litzenberger) din parametrii SVI, pe grila de preturi de exercitare K."""
    k = np.log(K / F)
    sig = np.sqrt(np.clip(svi_w(k, *p), 1e-10, None) / T)
    C = bs_price(F, K, T, 0.0, sig, 'call')
    return np.clip(np.gradient(np.gradient(C, K), K), 0, None)


def btc_rnd(tab, c=None, days=30, B=300):
    """Densitatea neutra la risc (Breeden-Litzenberger) din SVI pentru scadenta cea mai apropiata de 30 de zile;
    banda bootstrap pe perechi (reestimam SVI pe cotatii reesantionate) si intervalul cotatiilor observate."""
    e = pick(tab, days); f = tab.loc[e]
    F, T = f['F'], f['T']
    p0 = [float(f[x]) for x in ['a', 'b', 'rho', 'm', 's']]
    K = F * np.exp(np.linspace(-1.2, 1.0, 2201))
    q = rnd_from_svi(p0, F, T, K)
    atm = np.sqrt(svi_w(0.0, *p0) / T)
    ln = stats.lognorm.pdf(K, s=atm * np.sqrt(T), scale=F * np.exp(-0.5 * atm ** 2 * T))
    area = integrate.trapezoid(q, K)
    below_q = lambda qq, x: float(integrate.trapezoid(qq[K <= x * F], K[K <= x * F]) / integrate.trapezoid(qq, K))
    below = lambda x: below_q(q, x)
    lnb = lambda x: float(stats.lognorm.cdf(x * F, s=atm * np.sqrt(T), scale=F * np.exp(-0.5 * atm ** 2 * T)))
    out = dict(expiry=str(pd.Timestamp(e).date()), days=float(f['days']), F=float(F), atm=float(100 * atm), area=float(area),
               p80=below(0.8), p120=1 - below(1.2), ln80=lnb(0.8), ln120=1 - lnb(1.2), p70=below(0.7), ln70=lnb(0.7))
    band = None
    if c is not None:
        g = c[c['expiry'] == e]
        kq, wq = g['k'].values, g['w'].values
        rng = np.random.default_rng(SEED)
        Q, P70, P80 = [], [], []
        while len(Q) < B:
            i = rng.integers(0, len(kq), len(kq))
            if len(np.unique(kq[i])) < 6:
                continue
            pb = svi_fit(kq[i], wq[i])
            qb = rnd_from_svi([pb[x] for x in ['a', 'b', 'rho', 'm', 's']], F, T, K)
            Q.append(qb); P70.append(below_q(qb, 0.7)); P80.append(below_q(qb, 0.8))
        Q = np.array(Q)
        band = (np.quantile(Q, 0.025, axis=0), np.quantile(Q, 0.975, axis=0))
        kmin, kmax = float(np.exp(kq.min())), float(np.exp(kq.max()))
        out.update(ext70=below(kmin), ext70_share=below(kmin) / out['p70'])   # masa sub ultima cotatie (extrapolare SVI)
        out.update(B=int(B), p70_lo=float(np.quantile(P70, 0.025)), p70_hi=float(np.quantile(P70, 0.975)),
                   p80_lo=float(np.quantile(P80, 0.025)), p80_hi=float(np.quantile(P80, 0.975)),
                   kf_min=kmin, kf_max=kmax, n_quotes=int(len(kq)),
                   width_centre=float((band[1] - band[0])[np.argmin(np.abs(K / F - 1))] / q[np.argmin(np.abs(K / F - 1))]),
                   width_070=float((band[1] - band[0])[np.argmin(np.abs(K / F - 0.7))] / max(q[np.argmin(np.abs(K / F - 0.7))], 1e-30)))
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    if band is not None:
        ax.fill_between(K / F, band[0] * F, band[1] * F, color=Teal, alpha=0.35, lw=0,
                        label=f'95% pairs-bootstrap band ({B} SVI refits)')
        ax.axvspan(0.3, out['kf_min'], color='#F5E6CC', alpha=0.7, lw=0,
                   label=f"Outside the quoted strikes ({out['kf_min']:.2f}F to {out['kf_max']:.2f}F): SVI extrapolation")
        ax.axvspan(out['kf_max'], 1.6, color='#F5E6CC', alpha=0.7, lw=0)
    ax.plot(K / F, q * F, color=MainBlue, lw=1.6, label='Risk-neutral density implied by the SVI smile')
    ax.plot(K / F, ln * F, color=Orange, lw=1.2, ls='--', label=f'Log-normal density with the ATM volatility ({100 * atm:.1f}%)')
    ax.set_xlim(0.4 if band is not None else 0.5, 1.6)
    ax.set_xlabel('$S_T/F$ at expiry'); ax.set_ylabel('Density')
    ax.set_title(f"Bitcoin, expiry {pd.Timestamp(e).strftime('%d %b %Y')} ({f['days']:.0f} days), forward {F:,.0f} USD",
                 fontsize=8.5, loc='left')
    legend_outside_bottom(ax, ncol=2 if band is not None else 1, y=-0.2)
    save_fig('ch12_btc_rnd')
    return out


def strip_variance(K, Q, F, T):
    """Integrala 2/T * int Q(K)/K^2 dK (trapez) pe o grila densa de preturi forward OTM (put sub F, call peste F)."""
    return 2 / T * integrate.trapezoid(Q / K ** 2, K)


def btc_vix_bias(tab, c_all=None):
    """Indicele de tip VIX pentru Bitcoin: efectul discretizarii si al trunchierii benzii de preturi de exercitare
    (Jiang-Tian, 2005), cu preturi SVI in locul cotatiilor; plus diferenta salt vs variatia patratica intr-un model Merton."""
    c = deribit_chain() if c_all is None else c_all
    t0 = c['snapshot_utc'].iloc[0]
    c = c.copy()
    c['T'] = (c['expiry'] - t0).dt.total_seconds() / (365 * 86400)
    base = btc_vix(c_all)
    res = {}
    for tag in ['near', 'next']:
        e = pd.Timestamp(base[tag]['expiry'] + ' 08:00:00')
        g = c[c['expiry'] == e]
        F = float(g['forward'].iloc[0]); S = float(g['index'].iloc[0]); T = float(g['T'].iloc[0])
        Kq, _, K0 = cboe_strip(g, F, S)                                      # aceleasi preturi de exercitare ca indicele
        f = tab.loc[e]
        p = [float(f[x]) for x in ['a', 'b', 'rho', 'm', 's']]
        def svi_q(K, split=F):
            """Pretul forward (e^{RT} x pretul in USD) al optiunii OTM, din SVI: put sub split, call peste."""
            sig = np.sqrt(np.clip(svi_w(np.log(K / F), *p), 1e-10, None) / T)
            return np.where(K < split, bs_price(F, K, T, 0.0, sig, 'put'), bs_price(F, K, T, 0.0, sig, 'call'))
        Qq = np.where(Kq == K0, 0.5 * (svi_q(Kq, np.inf) + svi_q(Kq, -np.inf)), svi_q(Kq, K0))
        v_q = variance_from_strip(Kq, Qq, F, T)                              # SVI la preturile cotate, regula Cboe
        Kd = np.linspace(Kq.min(), Kq.max(), 20001)
        v_d = strip_variance(Kd, svi_q(Kd), F, T)                            # grila densa, acelasi interval
        Kw = F * np.exp(np.linspace(-4, 4, 40001))
        v_w = strip_variance(Kw, svi_q(Kw), F, T)                            # grila densa, interval extins
        res[tag] = dict(days=float(T * 365), quoted=base[tag]['var'], svi_quoted=float(v_q), svi_dense=float(v_d),
                        svi_wide=float(v_w), kf_min=float(Kq.min() / F), kf_max=float(Kq.max() / F))
    T1, T2 = res['near']['days'], res['next']['days']
    w1 = (T2 - 30) / (T2 - T1)
    idx = lambda key: float(100 * np.sqrt((T1 * res['near'][key] * w1 + T2 * res['next'][key] * (1 - w1)) / 30))
    out = dict(res, index_quoted=idx('quoted'), index_svi_quoted=idx('svi_quoted'), index_svi_dense=idx('svi_dense'),
               index_svi_wide=idx('svi_wide'))
    # salturi Merton (parametrii din graficul zambetelor): E^Q[-2 ln(S_T/F)] / T vs E^Q[QV] / T
    sigma, lam, mu_j, sig_j = 0.14, 1.0, -0.08, 0.08
    # sub masura de evaluare din merton_price: intensitate lam, salturi log ~ N(mu_j, sig_j^2)
    lq, mq = lam, mu_j
    EJ2 = mq ** 2 + sig_j ** 2
    EeJ = np.exp(mq + 0.5 * sig_j ** 2)
    qv = sigma ** 2 + lq * EJ2
    strip = sigma ** 2 + 2 * lq * (EeJ - 1 - mq)
    out['merton'] = dict(qv=float(qv), strip=float(strip), vol_qv=float(100 * np.sqrt(qv)), vol_strip=float(100 * np.sqrt(strip)),
                         rel=float(strip / qv - 1))
    return out


def qlike(rv, f):
    return rv / f - np.log(rv / f) - 1


def hac_se(u, lags):
    """Eroarea standard HAC (Newey-West, Bartlett) a mediei unei serii."""
    u = np.asarray(u, float)
    return nw_mean(u, lags)[1]


def iv_gmm(y, X, Z, lags):
    """Estimator IV exact identificat, b = (Z'X)^{-1} Z'y, cu varianta HAC (Newey-West) a momentelor Z u."""
    b = np.linalg.solve(Z.T @ X, Z.T @ y)
    u = y - X @ b
    g = Z * u[:, None]
    T = len(y)
    S = g.T @ g / T
    for L in range(1, lags + 1):
        G = g[L:].T @ g[:-L] / T
        S += (1 - L / (lags + 1)) * (G + G.T)
    A = np.linalg.inv(Z.T @ X / T)
    V = A @ S @ A.T / T
    return b, np.sqrt(np.diag(V))


def vix_forecast_inference():
    """VIX ca prognoza a variantei realizate pe 21 de zile: test comun Mincer-Zarnowitz, specificatia in logaritmi,
    erori in variabile (IV cu VIX^2 intarziat, Christensen-Prabhala), incluziune fata de HAR-RV (Corsi; Busch et al.)
    si comparatie in afara esantionului cu pierderea QLIKE si testul Diebold-Mariano (Patton, 2011)."""
    d = vrp_sp500().copy()
    out = {}
    L = 21
    m = sm.OLS(d['rv'], sm.add_constant(d[['iv2']])).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    w = m.wald_test('const = 0, iv2 = 1', scalar=True)
    cv = m.cov_params()
    out['lev'] = dict(a=float(m.params['const']), b=float(m.params['iv2']), a_se=float(m.bse['const']), b_se=float(m.bse['iv2']),
                      corr_ab=float(cv.loc['const', 'iv2'] / np.sqrt(cv.loc['const', 'const'] * cv.loc['iv2', 'iv2'])),
                      wald=float(w.statistic), wald_p=float(w.pvalue), n=int(len(d)), r2=float(m.rsquared))
    px = pd.concat([load_close('sp500'), load_close('vix')], axis=1, join='inner').dropna()
    rd = (np.log(px['sp500']).diff() ** 2 * 252 * 1e4)
    d['har_d'] = rd.reindex(d.index)
    d['har_w'] = rd.rolling(5).mean().reindex(d.index)
    d['har_m'] = rd.rolling(22).mean().reindex(d.index)
    d['iv2_lag'] = d['iv2'].shift(21)
    d = d.dropna()
    ly, lx = np.log(d['rv']), np.log(d['iv2'])
    ml = sm.OLS(ly, sm.add_constant(lx.rename('liv2'))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    wl = ml.wald_test('liv2 = 1', scalar=True)
    out['log'] = dict(a=float(ml.params['const']), b=float(ml.params['liv2']), a_se=float(ml.bse['const']),
                      b_se=float(ml.bse['liv2']), r2=float(ml.rsquared), t_b1=float((ml.params['liv2'] - 1) / ml.bse['liv2']),
                      wald_b1=float(wl.statistic), wald_b1_p=float(wl.pvalue))
    X = np.column_stack([np.ones(len(d)), lx.values])
    Z = np.column_stack([np.ones(len(d)), np.log(d['iv2_lag']).values])
    b, se = iv_gmm(ly.values, X, Z, L)
    fs = sm.OLS(lx, sm.add_constant(np.log(d['iv2_lag']).rename('z'))).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    out['iv'] = dict(a=float(b[0]), b=float(b[1]), a_se=float(se[0]), b_se=float(se[1]), t_b1=float((b[1] - 1) / se[1]),
                     first_stage_t=float(fs.tvalues['z']), first_stage_r2=float(fs.rsquared))
    # incluziune: log RV pe log VIX^2 si componentele HAR in logaritmi
    for c_ in ['har_d', 'har_w', 'har_m']:
        d['l' + c_] = np.log(d[c_].clip(lower=1e-2))
    me = sm.OLS(ly, sm.add_constant(pd.concat([lx.rename('liv2'), d[['lhar_d', 'lhar_w', 'lhar_m']]], axis=1))).fit(
        cov_type='HAC', cov_kwds={'maxlags': L})
    mh = sm.OLS(ly, sm.add_constant(d[['lhar_d', 'lhar_w', 'lhar_m']])).fit(cov_type='HAC', cov_kwds={'maxlags': L})
    wh = me.wald_test('lhar_d = 0, lhar_w = 0, lhar_m = 0', scalar=True)
    out['enc'] = dict(b_iv=float(me.params['liv2']), b_iv_se=float(me.bse['liv2']), r2=float(me.rsquared),
                      r2_har=float(mh.rsquared), r2_iv=float(ml.rsquared), wald_har=float(wh.statistic),
                      wald_har_p=float(wh.pvalue), b_m=float(me.params['lhar_m']), b_m_se=float(me.bse['lhar_m']))
    # in afara esantionului (din 2000): coeficienti reestimati la fiecare 21 de zile, doar cu tinte deja observate
    idx = d.index
    start = np.searchsorted(idx, pd.Timestamp('2000-01-03'))
    F_raw, F_mz, F_har, RV = [], [], [], []
    b_mz = b_har = None
    Xh_all = sm.add_constant(d[['lhar_d', 'lhar_w', 'lhar_m']]).values
    Xm_all = sm.add_constant(lx.rename('liv2')).values
    for i in range(start, len(d)):
        if (i - start) % 21 == 0:
            tr = slice(0, i - 21)                       # tintele RV_{s, s+21} cunoscute la data i: s <= i - 21
            b_har = np.linalg.lstsq(Xh_all[tr], ly.values[tr], rcond=None)[0]
            b_mz = np.linalg.lstsq(Xm_all[tr], ly.values[tr], rcond=None)[0]
            s2h = np.var(ly.values[tr] - Xh_all[tr] @ b_har)
            s2m = np.var(ly.values[tr] - Xm_all[tr] @ b_mz)
        F_raw.append(d['iv2'].values[i])
        F_mz.append(np.exp(Xm_all[i] @ b_mz + 0.5 * s2m))   # prognoza in nivel din regresia in logaritmi
        F_har.append(np.exp(Xh_all[i] @ b_har + 0.5 * s2h))
        RV.append(d['rv'].values[i])
    F_raw, F_mz, F_har, RV = map(np.array, (F_raw, F_mz, F_har, RV))
    oos = dict(start=str(idx[start].date()), n=int(len(RV)))
    for name, Fc in [('raw', F_raw), ('mz', F_mz)]:
        for lname, lf in [('qlike', qlike), ('mse', lambda y, f: (y - f) ** 2)]:
            dl = lf(RV, Fc) - lf(RV, F_har)          # < 0: VIX mai bun decat HAR
            se = hac_se(dl, L)
            oos[f'{name}_{lname}'] = dict(loss=float(lf(RV, Fc).mean()), loss_har=float(lf(RV, F_har).mean()),
                                          ratio=float(lf(RV, Fc).mean() / lf(RV, F_har).mean()), dm=float(dl.mean() / se),
                                          p=float(2 * (1 - stats.norm.cdf(abs(dl.mean() / se)))))
    out['oos'] = oos
    return out


def vrp_monthly():
    """Date lunare BTZ (2009): IV = VIX^2/12 la sfarsitul lunii, RV = suma randamentelor zilnice (%) la patrat din luna,
    VRP = IV - RV (ex ante), randamentul in exces = randamentul log lunar S&P 500 minus TB3MS/12 (FRED)."""
    spx, vix = read_market('GSPC.INDX')['close'], read_market('VIX.INDX')['close']
    px = pd.concat([spx, vix], axis=1, keys=['spx', 'vix']).dropna()
    r = 100 * np.log(px['spx']).diff().dropna()
    rv = (r ** 2).resample('ME').sum()
    iv = (px['vix'] ** 2 / 12).resample('ME').last()
    rm = 100 * np.log(px['spx'].resample('ME').last()).diff()
    tb = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS', index_col=0, parse_dates=True).iloc[:, 0]
    tb.index = tb.index + pd.offsets.MonthEnd(0)
    df = pd.DataFrame({'iv': iv, 'rv': rv, 'rm': rm, 'rf': tb / 12}).dropna()
    df = df[df.index >= '1990-01-31']
    df['vrp'] = df['iv'] - df['rv']
    df['ex'] = df['rm'] - df['rf']
    return df


def hodrick_t(y, X, e1, h):
    """Erori standard Hodrick (1992) 1B pentru regresia cu randamente suprapuse (suma regresorilor trecuti)."""
    T = len(y)
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    Z = X.T @ X / T
    S = np.zeros((X.shape[1], X.shape[1]))
    for t in range(h - 1, T):
        w = e1[t] * X[t - h + 1:t + 1].sum(axis=0)
        S += np.outer(w, w)
    S /= T
    Zi = np.linalg.inv(Z)
    V = Zi @ S @ Zi / T
    return b, b / np.sqrt(np.diag(V))


def vrp_predict(B=2000):
    """Predictibilitatea randamentelor prin VRP ex ante (BTZ, 2009): regresii lunare suprapuse pe h = 1, 3, 6, 12 luni,
    cu erori standard Newey-West (h lag-uri), Hansen-Hodrick (h - 1 lag-uri, nucleu uniform) si Hodrick (1992) 1B;
    p-valoare bootstrap sub H0 (VRP ca AR(1), reziduuri reesantionate impreuna; Stambaugh, 1999)."""
    df = vrp_monthly()
    ex, v = df['ex'].values, df['vrp'].values
    n = len(ex)

    def stats_h(ex, v, h):
        y = np.array([(12 / h) * ex[t + 1:t + 1 + h].sum() if t + h < n else np.nan for t in range(n)])
        ok = ~np.isnan(y)
        yy, vv = y[ok], v[ok]
        X = np.column_stack([np.ones(len(yy)), vv])
        e1 = (12 / h) * (np.append(ex[1:], np.nan)[ok] - np.nanmean(ex[1:]))
        b, th = hodrick_t(yy, X, np.nan_to_num(e1), h)
        u = yy - X @ b
        T = len(yy)
        g = X * u[:, None]
        def lrv(lags, kern):
            S = g.T @ g / T
            for L_ in range(1, lags + 1):
                G = g[L_:].T @ g[:-L_] / T
                S += kern(L_, lags) * (G + G.T)
            A = np.linalg.inv(X.T @ X / T)
            return A @ S @ A / T
        Vnw = lrv(h, lambda L_, m: 1 - L_ / (m + 1))
        Vhh = lrv(h - 1, lambda L_, m: 1.0)
        se_hh = np.sqrt(Vhh[1, 1]) if Vhh[1, 1] > 0 else np.nan
        r2 = 1 - u.var() / yy.var()
        return dict(b=float(b[1]), t_nw=float(b[1] / np.sqrt(Vnw[1, 1])), t_hh=float(b[1] / se_hh),
                    t_hod=float(th[1]), r2=float(100 * r2), n=int(T))
    out = {}
    # AR(1) pentru VRP si randamente sub H0
    phi = np.polyfit(v[:-1], v[1:], 1)
    ev = v[1:] - np.polyval(phi, v[:-1])
    er = ex[1:] - ex[1:].mean()
    rng = np.random.default_rng(SEED)
    for h in [1, 3, 6, 12]:
        out[str(h)] = stats_h(ex, v, h)
    tb = {h: [] for h in [1, 3, 6, 12]}
    for _ in range(B):
        j = rng.integers(0, len(ev), len(ev))
        vb = np.empty(n); vb[0] = v[rng.integers(0, n)]
        for t in range(1, n):
            vb[t] = phi[1] + phi[0] * vb[t - 1] + ev[j[t - 1]]
        xb = np.empty(n); xb[0] = ex.mean(); xb[1:] = ex[1:].mean() + er[j]
        for h in [1, 3, 6, 12]:
            tb[h].append(stats_h(xb, vb, h)['t_hod'])
    for h in [1, 3, 6, 12]:
        a = np.array(tb[h])
        out[str(h)]['p_boot'] = float(np.mean(a >= out[str(h)]['t_hod']))
        out[str(h)]['t_boot95'] = float(np.quantile(a, 0.95))
    out['phi'] = float(phi[0]); out['start'] = df.index[0].strftime('%Y-%m'); out['end'] = df.index[-1].strftime('%Y-%m')
    return out


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, pd.Timestamp):
        return str(o)
    return o


if __name__ == '__main__':
    RES = {}
    RES['payoffs'] = fig_payoffs()
    RES['strategies'] = fig_strategies()
    RES['parity'] = parity_example()
    RES['binomial'] = fig_binomial()
    RES['bs'] = bs_example()
    fig_greeks()
    RES['hedge_path'] = fig_hedge_path()
    errs, prem = hedge_errors()
    RES['hedge'] = fig_hedge_error(errs, prem)
    RES['mismatch'] = fig_vol_mismatch()
    dh = delta_hedged_history()
    dh.to_csv(os.path.join(HERE, 'ch12_delta_hedged_sp500.csv'))
    RES['dh'] = fig_delta_hedged(dh)
    RES['smile'] = fig_smile_models()
    RES['leverage'] = fig_leverage()
    c, tab, t0 = btc_surface()
    RES['snapshot'] = str(t0)
    RES['btc_expiries'] = fig_btc_smile(c, tab, t0)
    dv, dv_date = dvol_now()
    RES['dvol_now'] = dict(value=dv, date=dv_date)
    fig_btc_term(tab, dv)
    RES['btc_svi'] = {str(pd.Timestamp(e).date()): {k: (float(v) if not isinstance(v, str) else v) for k, v in row.items()}
                      for e, row in tab.iterrows()}
    RES['btc_rnd'] = btc_rnd(tab, c)
    RES['svi_arb'] = svi_no_arbitrage(tab)
    RES['btc_vix'] = btc_vix()
    RES['btc_vix_bias'] = btc_vix_bias(tab)
    RES['vix'] = fig_vix_history()
    RES['term'] = fig_vix_term()
    RES['vvix'] = fig_vvix()
    vd = vrp_sp500()
    RES['vrp'] = fig_vrp(vd)
    RES['mz'] = fig_mz(vd)
    RES['vix_inf'] = vix_forecast_inference()
    RES['vrp_pred'] = vrp_predict()
    vb = vrp_btc()
    RES['vrp_btc'] = fig_vrp_btc(vb)
    RES['gamma0'] = fig_0dte_gamma()
    od, phi = odte_straddle()
    RES['odte'] = fig_0dte_straddle(od, phi)
    with open(os.path.join(HERE, 'ch12_results.json'), 'w') as f:
        json.dump(jsonable(RES), f, indent=1)
    print('saved ch12_results.json')

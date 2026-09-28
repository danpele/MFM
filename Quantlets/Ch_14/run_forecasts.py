"""
run_forecasts.py -- prognozele la o zi pentru Capitolul 14 (rulare lunga, o singura data)
========================================================================================
Iesire (in acest folder):
  ch14_returns_<activ>.csv  -- randamente: medie istorica, AR(1), LSTM, Chronos-2, Chronos-Bolt, TimesFM-2.5
  ch14_risk_<activ>.csv     -- VaR 1%, VaR 2.5%, ES 2.5%: HS, GARCH-t, FHS, FHS cu volatilitate din modele
                               fundationale, cuantile directe ale modelelor fundationale; VaR 10% pentru toate
  ch14_rv.csv               -- varianta realizata SPY: RW, HAR, log-HAR, GARCH-t, LSTM, Chronos-2, Bolt, TimesFM
  ch14_ctx.csv              -- Chronos-2 pe log RV cu diverse lungimi de context
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import os
import sys
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfm_tsfm as M   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = [0, 1, 2, 3, 4]
L_RET = 20


def tick(msg, t0=[time.time()]):
    print(f'[{time.time() - t0[0]:7.0f}s] {msg}', flush=True)


def returns_block(name):
    r = M.load_returns(name)
    x = r.values
    t0 = r.index.searchsorted(pd.Timestamp(M.TEST_FROM[name]))
    org = np.arange(t0, len(r))
    out = pd.DataFrame({'y': x[org]}, index=r.index[org])
    out['hist'] = M.hist_mean(x, org)
    out['ar1'] = M.ar1(x, org)
    # LSTM: antrenat o singura data pe datele dinainte de perioada de test (standardizare cu statistici de antrenare)
    tr = x[max(0, t0 - 4000):t0]
    mu, sd = tr.mean(), tr.std()
    Xtr, ytr = M.make_windows((tr - mu) / sd, L_RET)
    Xte = np.stack([(x[t - L_RET:t] - mu) / sd for t in org])
    preds = []
    for s in SEEDS:
        f, hist = M.train_lstm(Xtr, ytr, hidden=16, seed=s)
        preds.append(mu + sd * f(Xte))
        pd.DataFrame(hist, columns=['train', 'val']).to_csv(os.path.join(HERE, f'ch14_lstm_hist_{name}_s{s}.csv'))
    for s, p in zip(SEEDS, preds):
        out[f'lstm_s{s}'] = p
    out['lstm'] = np.mean(preds, axis=0)
    tick(f'{name}: baselines + LSTM')
    ctx = M.contexts_at(x, org)
    for fm in ('chronos2', 'bolt', 'timesfm'):
        lv, Q, P = M.fm_forecast(fm, ctx)
        for j, u in enumerate(lv):
            out[f'{fm}_q{u:.2f}'] = Q[:, j]
        out[f'{fm}_point'] = P
        tick(f'{name}: {fm} on returns ({len(org)} origins)')
    return r, org, out


def risk_block(name, r, org, ret):
    x = r.values
    # volatilitatea prognozata de modelele fundationale pe |r| (context 512), pentru W zile inainte de test
    org_s = np.arange(org[0] - M.W, len(r))
    ctx = M.contexts_at(np.abs(x), org_s)
    sig = {}
    lv, Q, P = M.fm_forecast('chronos2', ctx)
    s = np.full(len(x), np.nan)
    s[org_s] = M.grid_mean(lv, Q)
    sig['C2-FHS'] = s
    tick(f'{name}: chronos2 on |r|')
    lv, Q, P = M.fm_forecast('timesfm', ctx)
    s = np.full(len(x), np.nan)
    s[org_s] = np.maximum(P, 1e-6)
    sig['TFM-FHS'] = s
    tick(f'{name}: timesfm on |r|')
    tabs = M.risk_table(x, org, fm_sigma=sig)
    out = pd.DataFrame(index=r.index[org])
    out['y'] = x[org]
    for k, t in tabs.items():
        for c in t.columns:
            out[f'{k}|{c}'] = t[c].values
    # cuantile directe (fara filtrare): Chronos-2 are nivelul 1%; Bolt si TimesFM au doar decile
    c2 = ret[[c for c in ret.columns if c.startswith('chronos2_q')]].values
    out['C2-raw|VaR1'] = -M.quantile_at(M.C2_LEVELS, c2, 0.01)
    out['C2-raw|VaR2.5'] = -M.quantile_at(M.C2_LEVELS, c2, 0.025)
    out['C2-raw|ES2.5'] = M.es_from_grid(M.C2_LEVELS, c2)
    for fm in ('bolt', 'timesfm'):
        Qd = ret[[c for c in ret.columns if c.startswith(fm + '_q')]].values
        out[f'{fm}-raw|VaR1'] = -M.quantile_at(M.DEC_LEVELS, Qd, 0.01)      # limitat la decila 10%
        out[f'{fm}-raw|VaR10'] = -Qd[:, 0]
    out['C2-raw|VaR10'] = -M.quantile_at(M.C2_LEVELS, c2, 0.10)
    # VaR 10% pentru HS si FHS (pentru comparatia cu decilele modelelor fundationale)
    gfit, Z = M.garch_t(x, org)
    out['HS|VaR10'] = [-np.quantile(x[t - M.W:t], 0.10) for t in org]
    out['FHS|VaR10'] = -(gfit.mu.values + gfit.sigma.values * np.array([np.quantile(z, 0.10) for z in Z]))
    for k, s in sig.items():
        out[f'{k}|sigma'] = s[org]
    tick(f'{name}: risk table')
    return out


def rv_block():
    rv = M.load_rv()
    spy = M.load_spy_daily()
    x = rv.values
    org = np.arange(500, len(rv))
    out = pd.DataFrame({'RV': x[org]}, index=rv.index[org])
    out['RW'] = x[org - 1]
    out['HAR'] = M.har(x, org)
    out['logHAR'] = M.har(x, org, log=True)
    # GARCH-t pe randamentele zilnice ale SPY, reexprimat in unitatile RV (raport pe ultimele 500 de zile)
    pos = spy.index.get_indexer(rv.index[org])
    gfit, _ = M.garch_t(spy.values, pos)
    r2 = pd.Series(spy.values ** 2, index=spy.index).reindex(rv.index).values
    c = np.array([np.nanmean(x[t - 500:t]) / np.nanmean(r2[t - 500:t]) for t in org])
    out['GARCH-t'] = c * gfit.sigma.values ** 2
    tick('rv: RW, HAR, GARCH-t')
    # LSTM pe log RV: fereastra mobila de 500 de zile, reantrenat la fiecare 125 de zile, 3 seminte
    lx = np.log(x)
    f_lstm = np.empty(len(org))
    for k0 in range(0, len(org), 125):
        t = org[k0]
        tr = lx[t - 500:t]
        mu, sd = tr.mean(), tr.std()
        Xtr, ytr = M.make_windows((tr - mu) / sd, 22)
        blk = org[k0:k0 + 125]
        Xte = np.stack([(lx[s - 22:s] - mu) / sd for s in blk])
        ps, s2 = [], []
        for sdd in (0, 1, 2):
            f, _ = M.train_lstm(Xtr, ytr, hidden=8, seed=sdd, epochs=200)
            ps.append(f(Xte))
            s2.append(np.var(ytr - f(Xtr)))
        f_lstm[k0:k0 + 125] = np.exp(mu + sd * np.mean(ps, axis=0) + sd ** 2 * np.mean(s2) / 2)
    out['LSTM'] = f_lstm
    tick('rv: LSTM')
    ctx = M.contexts_at(lx, org)
    for fm, col in (('chronos2', 'Chronos-2'), ('bolt', 'Chronos-Bolt'), ('timesfm', 'TimesFM-2.5')):
        lv, Q, P = M.fm_forecast(fm, ctx)
        out[col] = M.grid_mean(lv, Q, np.exp)
        out[col + '|median'] = np.exp(M.quantile_at(lv, Q, 0.5))
        tick(f'rv: {fm}')
    # sensibilitatea la lungimea contextului (Chronos-2)
    rows = {}
    for L in (32, 64, 128, 256, 512):
        lv, Q, P = M.fm_forecast('chronos2', M.contexts_at(lx, org, ctx=L))
        rows[L] = M.grid_mean(lv, Q, np.exp)
    ctxdf = pd.DataFrame(rows, index=rv.index[org])
    ctxdf.insert(0, 'RV', x[org])
    tick('rv: context lengths')
    return out, ctxdf


if __name__ == '__main__':
    only = sys.argv[1:]
    if not only or 'rv' in only:
        rvo, ctxo = rv_block()
        rvo.to_csv(os.path.join(HERE, 'ch14_rv.csv'), float_format='%.6g')
        ctxo.to_csv(os.path.join(HERE, 'ch14_ctx.csv'), float_format='%.6g')
    for a in M.ASSETS:
        if only and a not in only:
            continue
        r, org, ret = returns_block(a)
        ret.to_csv(os.path.join(HERE, f'ch14_returns_{a}.csv'), float_format='%.6g')
        rk = risk_block(a, r, org, ret)
        rk.to_csv(os.path.join(HERE, f'ch14_risk_{a}.csv'), float_format='%.6g')
    tick('done')

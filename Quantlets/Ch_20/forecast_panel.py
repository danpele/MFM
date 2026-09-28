"""
forecast_panel.py -- rolling out-of-sample forecasts of realised variance for the 50 VOLARE assets
==================================================================================================
Pre-registered design (sigvol.CFG): rolling window of 1000 days, re-estimation every 5 days, horizons 1, 5, 22,
signature of the time-augmented path (t, log RV, cumulative open-to-close return) over 22 days, depth 3.
Stage 1  validation block (first 250 forecast days of each asset): choose c in gamma = c / median(d) per horizon,
         pooled over all assets, separately for the two kernel-weighted models.
Stage 2  evaluation (from the end of the validation block + h days): all seven models.
Stage 3  pre-registered robustness: depth 2; path without the return channel (signature models only).
Forecast tables go to <VOLARE_DIR>/ch20_cache (they contain VOLARE values, so they stay local).
Run:  python3 forecast_panel.py      (parallel with joblib; single-threaded BLAS in each worker)
Modelarea Pietelor Financiare - Daniel Traian PELE
"""

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')
import sys
import json
import time
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sigvol as S   # noqa: E402

if not os.path.isdir(S.VOLARE_DIR):
    S.VOLARE_DIR = os.path.join(HERE, '..', '..', 'data', 'volare')
CACHE = os.path.join(S.VOLARE_DIR, 'ch20_cache')
STRESS = ['2020-03-16', '2022-03-07', '2025-04-07']     # COVID-19 crash, invasion of Ukraine, US tariff shock
N_JOBS = int(os.environ.get('CH20_JOBS', '14'))
ROBUST = {'N2': dict(DEPTH=2), 'noret': dict(CHANNELS=('t', 'logrv'))}


def assets():
    return [(k, s) for k in S.CLASSES for s in S.symbols(k)]


def cfg_of(tag):
    c = dict(S.CFG)
    c.update(ROBUST.get(tag, {}))
    return c


def _trading(dates, iso_list):
    out = []
    for iso in iso_list:
        j = dates.searchsorted(pd.Timestamp(iso))
        if j < len(dates):
            out.append(dates[j])
    return out


def val_job(kind, sym, h):
    cfg = S.CFG
    a = S.load_asset(kind, sym)
    D = S.build_design(a, h, cfg)
    st = S.first_origin(D, cfg)
    res = {}
    for c in cfg['C_GRID']:
        fc, _, _ = S.run_forecasts(D, cfg, c, c, st, st + cfg['VAL'], models=['logHAR-K', 'Sig-LK'])
        res[c] = {m: float(S.qlike(fc.y, fc[m]).mean()) for m in ['logHAR-K', 'Sig-LK']}
    return kind, sym, h, res


def eval_job(kind, sym, h, c_sig, c_har, tag='main'):
    cfg = cfg_of(tag)
    models = S.MODELS if tag == 'main' else ['Sig-L', 'Sig-LK']
    a = S.load_asset(kind, sym)
    D = S.build_design(a, h, cfg)
    st = S.first_origin(D, cfg) + cfg['VAL'] + h
    stop = len(a) - h
    t0 = time.time()
    fc, ks, ws = S.run_forecasts(D, cfg, c_sig, c_har, st, stop, models=models,
                                 weight_dates=_trading(D['dates'], STRESS) if tag == 'main' else ())
    d = os.path.join(CACHE, tag)
    os.makedirs(d, exist_ok=True)
    fc.to_csv(os.path.join(d, f'fc_{kind}_{sym}_h{h}.csv'))
    ks.to_csv(os.path.join(d, f'info_{kind}_{sym}_h{h}.csv'), index=False)
    if ws:
        pd.DataFrame({str(k.date()): v for k, v in ws.items() if v is not None}).to_csv(
            os.path.join(d, f'w_{kind}_{sym}_h{h}.csv'))
    return kind, sym, h, tag, time.time() - t0


def stage1():
    f = os.path.join(CACHE, 'validation.json')
    if os.path.exists(f):
        return json.load(open(f))
    jobs = [delayed(val_job)(k, s, h) for k, s in assets() for h in S.CFG['HORIZONS']]
    out = Parallel(n_jobs=N_JOBS, verbose=5)(jobs)
    raw = {f'{k}|{s}|{h}': {str(c): v for c, v in r.items()} for k, s, h, r in out}
    choice = {}
    for h in S.CFG['HORIZONS']:
        for m in ['Sig-LK', 'logHAR-K']:
            M = pd.DataFrame({key: {c: v[m] for c, v in r.items()} for key, r in raw.items()
                              if key.endswith(f'|{h}')}).T               # assets x c
            rel = M.div(M.mean(axis=1), axis=0).mean()                # each asset counts equally
            choice[f'{m}|{h}'] = {'c': float(rel.idxmin()), 'rel': rel.round(4).to_dict()}
    res = {'raw': raw, 'choice': choice}
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(f, 'w'), indent=1)
    return res


def stage2(val, tags=('main',)):
    todo = []
    for tag in tags:
        for k, s in assets():
            for h in S.CFG['HORIZONS']:
                if os.path.exists(os.path.join(CACHE, tag, f'fc_{k}_{s}_h{h}.csv')):
                    continue
                cs = val['choice'][f'Sig-LK|{h}']['c']
                ch = val['choice'][f'logHAR-K|{h}']['c']
                todo.append(delayed(eval_job)(k, s, h, cs, ch, tag))
    if todo:
        out = Parallel(n_jobs=N_JOBS, verbose=5)(todo)
        log = os.path.join(CACHE, 'runtime.csv')
        pd.DataFrame(out, columns=['kind', 'symbol', 'h', 'tag', 'seconds']).to_csv(
            log, mode='a', header=not os.path.exists(log), index=False)


if __name__ == '__main__':
    T0 = time.time()
    val = stage1()
    print('stage 1 done', round(time.time() - T0), 's', {k: v['c'] for k, v in val['choice'].items()})
    stage2(val, ('main',))
    print('stage 2 done', round(time.time() - T0), 's')
    stage2(val, tuple(ROBUST))
    print('stage 3 done', round(time.time() - T0), 's')
    json.dump({'wall_seconds_last_run': time.time() - T0}, open(os.path.join(CACHE, 'wall.json'), 'w'))

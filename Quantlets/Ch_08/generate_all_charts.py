"""
Chart generator for Chapter 8: Backtesting and Evaluating Risk Forecasts
========================================================================
All charts: transparent background, English labels, legend outside at the bottom.
Data: S&P 500, BET and Bitcoin daily closes (course data), EUR/RON (BNR reference rate).
One-day-ahead VaR/ES forecasts on a rolling window (1000 observations): HS, Normal, Student-t,
GARCH-t, FHS, GARCH-EVT; evaluation from 2007 (EUR/RON from 2009, Bitcoin from 2017).
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import sys
import json
import tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.dates as mdates
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import slide_fit  # noqa: E402,F401  charts drawn at the size they have on the slides
import mfm_data as M   # noqa: E402

# Chart style: transparent background, legend below the plot
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

# Brand colours
MainBlue = '#1A3A6E'
IDAred   = '#CD0000'
Forest   = '#2E7D32'
Amber    = '#B5853F'
Orange   = '#E67E22'
Purple   = '#8E44AD'
Crimson  = '#DC3545'
Navy     = '#1F2A44'   # reference lines (no grey in charts)
BandBlue = '#C5D2E8'   # light MainBlue tint for confidence / reference bands
Gray, LightGray = Navy, BandBlue   # legacy names kept for importing scripts
Teal = '#17A2B8'
MCOL = {'HS': Teal, 'Normal': Amber, 'Student-t': Purple, 'GARCH-t': MainBlue, 'FHS': Forest, 'GARCH-EVT': IDAred}
PV_CMAP = LinearSegmentedColormap.from_list('pv', [IDAred, '#F4B6B6', '#FFFFFF', '#BFD8BF', Forest])

HERE = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(HERE, '..', '..', 'charts')


def save_fig(name):
    """Save the figure as transparent PDF and PNG."""
    # Local geometry for the final full-width chart boxes; numerical code is unchanged.
    boxes = {'ch8_sem_c3_esr': (410, 94), 'ch8_sem_a8_mass': (410, 95), 'ch8_sem_b8_mcs': (410, 95), 'ch8_kupiec_curve': (240, 175), 'ch8_murphy': (240, 175),
             'ch8_elicitability': (410, 108), 'ch8_sem_a10_aci': (410, 103),
             'ch8_sem_b4_conformal': (410, 103), 'ch8_sem_b3_null': (410, 132)}
    if name in boxes:
        slide_fit.SIZES[name] = boxes[name]
    os.makedirs(CHART_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.pdf'), bbox_inches='tight', transparent=True)
    plt.savefig(os.path.join(CHART_DIR, f'{name}.png'), bbox_inches='tight', transparent=True, dpi=180)
    plt.close()
    print(f"   saved {name}")


def legend_outside_bottom(ax, ncol=2, y=-0.22):
    """Place the legend outside the plot, bottom centre."""
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol, frameon=False)


def pv_heatmap(ax, P, fmt='{:.2f}', title=None):
    """Heat map of p-values: red = rejection, green = no rejection (log scale)."""
    Z = np.log10(np.clip(P.values.astype(float), 1e-4, 1))
    ax.imshow(Z, cmap=PV_CMAP, vmin=-4, vmax=0, aspect='auto')
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            v = P.values[i, j]
            txt = '<.001' if v < 0.001 else (f'{v:.3f}' if v < 0.01 else fmt.format(v))
            ax.text(j, i, txt, ha='center', va='center', fontsize=7)
    ax.set_xticks(range(P.shape[1]), P.columns, fontsize=7.5)
    ax.set_yticks(range(P.shape[0]), P.index, fontsize=7.5)
    for s in ax.spines.values():
        s.set_visible(False)
    if title:
        ax.set_title(title, fontsize=9)


# =============================================================================
# DATA: forecasts of all models for the four assets
# =============================================================================
_FC = {}


def fc(name):
    if name not in _VALIDATED_FC:
        result=M.get_forecasts(name)
        _FC_REPORTS[name]=M.get_forecasts.last_diagnostics
        calendar,losses=canonical_sample(name)
        validate_forecast_contract(result[0],M.MODELS,calendar,losses,M.get_forecasts.last_diagnostics)
        _VALIDATED_FC[name]=result
    return _VALIDATED_FC[name]


def hits(name,model,col='VaR1'):
    df=fc(name)[0][model]
    values=df[['L',col]].to_numpy(dtype=float)
    if not np.isfinite(values).all():raise ValueError('Hit indicators require finite losses and forecasts')
    return (df['L']>df[col]).astype(int)


# --- Google-validated helpers (synchronised from the Chapter 8 lecture notebook) ---
"""Prototype only: metric eligibility on an externally supplied canonical calendar.
Caller must retain the original model universe; this function cannot establish it.
"""


import numpy as np


import pandas as pd


from pandas.api.types import is_numeric_dtype, is_bool_dtype, is_complex_dtype


def completeness(frame, calendar, columns, losses):
    if isinstance(columns, (str, bytes)):
        raise ValueError('Metric columns must be a sequence, not a bare string')
    columns = list(columns)
    if not columns or any(not isinstance(c, str) or c == 'L' for c in columns) or len(set(columns)) != len(columns):
        raise ValueError('Metric columns must be unique forecast names, excluding L')
    calendar = pd.Index(calendar)
    if len(calendar) == 0 or not calendar.is_unique or not calendar.is_monotonic_increasing:
        raise ValueError('Canonical calendar must be nonempty, unique, ordered')
    if not isinstance(losses, pd.Series) or not losses.index.equals(calendar):
        raise ValueError('Canonical losses must align exactly with the calendar')
    def real_values(series):
        if not is_numeric_dtype(series.dtype) or is_bool_dtype(series.dtype) or is_complex_dtype(series.dtype):
            return None
        return series.to_numpy(dtype=float, na_value=np.nan)
    expected = real_values(losses)
    if expected is None or not np.isfinite(expected).all():
        raise ValueError('Canonical losses must be finite real numbers')
    if not isinstance(frame, pd.DataFrame) or not frame.columns.is_unique or isinstance(frame.columns, pd.MultiIndex):
        return {'eligible': False, 'reason': 'invalid_frame'}
    if not frame.index.equals(calendar):
        return {'eligible': False, 'reason': 'calendar_mismatch'}
    for name in dict.fromkeys(['L'] + columns):
        if name not in frame:
            return {'eligible': False, 'reason': 'missing_column', 'column': name}
        values = real_values(frame[name])
        if values is None or not np.isfinite(values).all():
            return {'eligible': False, 'reason': 'nonfinite_or_nonreal', 'column': name}
        if name == 'L' and not np.array_equal(values, expected):
            return {'eligible': False, 'reason': 'loss_mismatch'}
    return {'eligible': True, 'reason': None}


"""Validate forecast absence against the producer's dated availability record."""


import numpy as np


import pandas as pd


from pandas.api.types import is_numeric_dtype,is_bool_dtype,is_complex_dtype


def validate_forecast_contract(frames,models,calendar,losses,report):
    calendar=pd.Index(calendar)
    if not calendar.is_unique or not calendar.is_monotonic_increasing or not len(calendar):
        raise ValueError('Invalid canonical calendar')
    if not isinstance(losses,pd.Series) or not losses.index.equals(calendar) or not np.isfinite(losses.to_numpy()).all():
        raise ValueError('Invalid canonical losses')
    if set(frames)!=set(models):raise ValueError('Forecast universe mismatch')
    daily=report['daily']
    if list(daily['forecast_date'])!=[str(d.date()) for d in calendar]:
        raise ValueError('Diagnostic calendar mismatch')
    available=daily['forecast_available']
    if len(available)!=len(calendar) or any(type(x) is not bool for x in available):
        raise ValueError('Invalid availability record')
    missing=~np.array(available,dtype=bool)
    for model in models:
        frame=frames[model]
        if not isinstance(frame,pd.DataFrame) or not frame.index.equals(calendar) or not frame.columns.is_unique:
            raise ValueError('Forecast structure mismatch: '+model)
        if 'L' not in frame or not np.array_equal(frame['L'].values,losses.values):
            raise ValueError('Forecast loss mismatch: '+model)
        expected=missing if model in ['GARCH-t','FHS','GARCH-EVT'] else np.zeros(len(calendar),dtype=bool)
        for column in ['VaR1','VaR2.5','VaR5','ES1','ES2.5']:
            if column not in frame:raise ValueError('Missing forecast column: '+column)
            series=frame[column]
            if not is_numeric_dtype(series.dtype) or is_bool_dtype(series.dtype) or is_complex_dtype(series.dtype):
                raise ValueError('Nonreal forecast: '+model+'/'+column)
            values=series.to_numpy(dtype=float,na_value=np.nan)
            if np.isinf(values).any() or not np.array_equal(np.isnan(values),expected):
                raise ValueError('Forecast missingness disagrees with producer: '+model+'/'+column)
    return frames


import numpy as np


from pandas.api.types import is_numeric_dtype,is_bool_dtype,is_complex_dtype


def validate_es_contract(frames,models,calendar,losses,report,tails,k_tail):
    if set(models)!={'HS','Normal','Student-t','GARCH-t','FHS','GARCH-EVT'} or len(models)!=6:raise ValueError('Unknown model universe')
    if type(k_tail) is not int or k_tail<1:raise ValueError('Invalid empirical tail width')
    validate_forecast_contract(frames,models,calendar,losses,report)
    available=np.asarray(report['daily']['forecast_available'],dtype=bool)
    if np.any(available[:-1] & ~available[1:]):raise ValueError('Availability must be an initial missing prefix')
    for model in models:
        missing=~available if model in ('GARCH-t','FHS','GARCH-EVT') else np.zeros(len(calendar),dtype=bool)
        columns=['pit','scale','mu']
        if model in ('Student-t','GARCH-t'):columns+=['nu']
        if model=='GARCH-EVT':columns+=['u','xi','beta','pu']
        for col in columns:
            if col not in frames[model]:raise ValueError('Missing ES field: '+col)
            series=frames[model][col]
            if not is_numeric_dtype(series.dtype) or is_bool_dtype(series.dtype) or is_complex_dtype(series.dtype):raise ValueError('Nonreal ES field')
            a=series.to_numpy(dtype=float,na_value=np.nan)
            if a.dtype.kind not in 'fi' or np.isinf(a).any() or not np.array_equal(np.isnan(a),missing):
                raise ValueError(f'Invalid ES field {model}/{col}')
            v=a[~missing]
            if col=='pit' and ((v<0)|(v>1)).any():raise ValueError('PIT outside [0,1]')
            if col in ('scale','beta') and (v<=0).any():raise ValueError('Nonpositive scale')
            if col=='nu' and (v<=2).any():raise ValueError('Invalid t degrees of freedom')
            if col=='xi' and ((v>=1)|(v==0)).any():raise ValueError('GPD ES domain or singular implemented formula')
            if col=='pu' and ((v<.05)|(v>1)).any():raise ValueError('Invalid tail probability')
        if model in ('HS','FHS'):
            if model not in tails or not isinstance(tails[model],np.ndarray):raise ValueError('Expected producer positional tail ndarray')
            a=tails[model]  # producer sorts standardised losses ascending, then applies positive scale
            if a.shape!=(len(calendar),k_tail) or a.dtype.kind not in 'fi' or np.isinf(a).any():raise ValueError('Invalid tail array')
            if not np.array_equal(np.isnan(a),np.broadcast_to(missing[:,None],a.shape)):raise ValueError('Tail availability mismatch')
            if (np.diff(a[~missing],axis=1)<0).any():raise ValueError('Unsorted empirical tails')
    return True


"""Individual-model coverage on the original full evaluation sample."""


def coverage_table(assets,models,frames_for,canonical_for,kupiec,christoffersen,duration_test,report_for,col='VaR1',p=.01):
    if not assets or not models or len(set(assets))!=len(assets) or len(set(models))!=len(models):
        raise ValueError('Assets and models must be nonempty and unique')
    if col not in {'VaR1':.01,'VaR2.5':.025,'VaR5':.05} or p!={'VaR1':.01,'VaR2.5':.025,'VaR5':.05}[col]:
        raise ValueError('VaR column and nominal probability must agree')
    rows={}
    for name in assets:
        frames=frames_for(name);calendar,losses=canonical_for(name)
        validate_forecast_contract(frames,models,calendar,losses,report_for(name))
        for model in models:
            check=completeness(frames[model],calendar,[col],losses)
            if not check['eligible']:
                if check['reason']!='nonfinite_or_nonreal' or check.get('column')!=col:
                    raise ValueError('Forecast contract violation: '+str(check))
                rows[(name,model)]=dict(status='withheld',reason=check,result=None)
                continue
            h=(frames[model]['L']>frames[model][col]).astype(int).values
            k=kupiec(h,p);c=christoffersen(h,p);d=duration_test(h)
            if k['T']!=len(calendar):raise ValueError('Coverage sample changed')
            result=dict(T=k['T'],x=k['x'],rate=k['rate'],LR_uc=k['LR'],p_uc=k['p'],LR_ind=c['LR_ind'],
                        p_ind=c['p_ind'],LR_cc=c['LR_cc'],p_cc=c['p_cc'],pi01=c['pi01'],pi11=c['pi11'],
                        b=d['b'],LR_dur=d['LR'],p_dur=d['p'])
            rows[(name,model)]=dict(status='computed',reason=None,result=result)
    return rows


"""Eligibility plan only. Never computes a metric or shrinks its model universe."""


from collections.abc import Mapping


def metric_plan(frames, original_models, calendar, losses, columns):
    if isinstance(original_models,(str,bytes)):
        raise ValueError('Original model universe must be a sequence')
    models=list(original_models)
    if not models or any(not isinstance(m,str) or not m for m in models) or len(set(models))!=len(models):
        raise ValueError('Original model universe must be nonempty and unique')
    if not isinstance(frames,Mapping) or set(frames)!=set(models):
        raise ValueError('Frames must retain exactly the original model universe')
    if isinstance(columns,(str,bytes)):
        raise ValueError('Metric columns must be a sequence')
    columns=list(columns)
    checks={m:completeness(frames[m],calendar,columns,losses) for m in models}
    withheld=[m for m in models if not checks[m]['eligible']]
    return {'original_models':models,'per_model':checks,
            'joint_eligible':not withheld,'withheld_models':withheld,
            'joint_reason':'incomplete_original_model_universe' if withheld else None}


"""Prototype gate; caller must supply the original universe and canonical sample."""


def execute_joint_metric(frames, original_models, calendar, losses, columns, evaluate):
    plan=metric_plan(frames,original_models,calendar,losses,columns)
    if not plan['joint_eligible']:
        return {'status':'withheld','plan':plan,'result':None}
    result=evaluate(frames)
    return {'status':'computed','plan':plan,'result':result}


"""Staged replacement contract; rendering must handle explicit withheld assets."""


import numpy as np


import pandas as pd


def comparative_table(assets, models, frames_for, canonical_for, fz0,
                      diebold_mariano, mcs, pinball):
    out={}
    for name in assets:
        frames=frames_for(name)
        calendar,losses=canonical_for(name)
        def evaluate(F):
            Lf=pd.DataFrame({m:fz0(F[m]['L'].values,F[m]['VaR2.5'].values,F[m]['ES2.5'].values)
                             for m in models},index=calendar)
            if not np.isfinite(Lf.to_numpy()).all():
                raise ValueError('FZ0 produced nonfinite scores on complete inputs')
            best=Lf.mean().idxmin()
            dm={m:diebold_mariano(Lf[m],Lf[best]) for m in models if m!=best}
            mc=mcs(Lf)
            return dict(mean={m:float(v) for m,v in Lf.mean().items()},best=best,
                        dm={m:dict(DM=d['DM'],p=d['p'],dbar=d['dbar']) for m,d in dm.items()},
                        mcs={m:float(v) for m,v in mc.items()},
                        pin={m:float(pinball(F[m]['L'].values,F[m]['VaR1'].values,.01).mean()) for m in models})
        out[name]=execute_joint_metric(frames,models,calendar,losses,
                                      ['VaR1','VaR2.5','ES2.5'],evaluate)
    return out


"""Render staged table contracts without treating missing comparisons as zeros."""


import numpy as np


import matplotlib.pyplot as plt


def comparative_figure(table, assets, models, labels, colors):
    fig,ax=plt.subplots(figsize=(6.8,3.4))
    width=.78/len(models)
    for i,model in enumerate(models):
        values=[]
        for asset in assets:
            row=table[asset]
            if row['status']=='withheld':values.append(np.nan)
            elif row['status']=='computed':
                result=row['result']
                values.append(result['mean'][model]-result['mean'][result['best']])
            else:raise ValueError('Unknown comparative table status')
        ax.bar(np.arange(len(assets))+(i-(len(models)-1)/2)*width,
               values,width,color=colors[model],label=model)
    for i,asset in enumerate(assets):
        if table[asset]['status']=='withheld':
            ax.text(i,.5,'Comparison\nunavailable',transform=ax.get_xaxis_transform(),
                    ha='center',va='center',fontsize=8,color='black')
    ax.set_xticks(range(len(assets)),[labels[a] for a in assets])
    ax.set_xlim(-.6,len(assets)-.4)
    ax.set_ylabel('Mean FZ0 loss minus\nthat of the best model')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.13),ncol=3,frameon=False)
    fig.subplots_adjust(left=.14,right=.98,top=.95,bottom=.27)
    return fig,ax


"""Render MCS contracts; unavailable assets have no fabricated p-values."""


import numpy as np


import pandas as pd


import matplotlib.pyplot as plt


def comparative_mcs_figure(table,assets,models,labels,cmap='viridis'):
    if not assets or not models or len(set(models))!=len(models) or len(set(assets))!=len(assets):
        raise ValueError('Assets and models must be nonempty and unique')
    values=np.full((len(models),len(assets)),np.nan)
    for j,asset in enumerate(assets):
        row=table[asset]
        if row['status']=='withheld':
            if row.get('result') is not None:raise ValueError('Withheld result must be None')
            continue
        if row['status']!='computed':raise ValueError('Unknown comparative table status')
        pvalues=row['result']['mcs']
        if set(pvalues)!=set(models):raise ValueError('MCS must retain the original model universe')
        column=np.array([pvalues[m] for m in models],dtype=float)
        if not np.isfinite(column).all() or ((column<0)|(column>1)).any():
            raise ValueError('MCS p-values must be finite and in [0,1]')
        values[:,j]=column
    fig,ax=plt.subplots(figsize=(6.4,3.6))
    im=ax.imshow(np.ma.masked_invalid(values),cmap=cmap,vmin=0,vmax=1,aspect='auto')
    for j,asset in enumerate(assets):
        if table[asset]['status']=='withheld':
            ax.text(j,(len(models)-1)/2,'Unavailable',rotation=90,ha='center',va='center',color='black')
        else:
            for i in range(len(models)):
                rgba=im.cmap(im.norm(values[i,j]))
                color='black' if np.dot(rgba[:3],[.299,.587,.114])>.5 else 'white'
                ax.text(j,i,f'{values[i,j]:.3f}'+ (' *' if values[i,j]>=.10 else ''),ha='center',va='center',color=color,fontsize=8)
    ax.set_xticks(range(len(assets)),[labels[a] for a in assets])
    ax.set_yticks(range(len(models)),models)
    ax.set_title('MCS p-values (FZ0 loss)\n* p ≥ 0.10: retained in the 90% MCS',fontsize=9)
    fig.colorbar(im,ax=ax,label='p-value',shrink=.8)
    fig.tight_layout()
    return fig,ax,pd.DataFrame(values,index=models,columns=assets)


"""Gate score consumers on the complete original forecast universe."""


import numpy as np


import pandas as pd


def guarded_fz_scores(frames,models,calendar,losses,fz0,evaluate):
    def scores(F):
        Lf=pd.DataFrame({m:fz0(F[m]['L'].values,F[m]['VaR2.5'].values,F[m]['ES2.5'].values)
                         for m in models},index=calendar)
        if not np.isfinite(Lf.to_numpy()).all():
            raise ValueError('FZ0 produced nonfinite scores on complete inputs')
        return evaluate(Lf)
    return execute_joint_metric(frames,models,calendar,losses,['VaR2.5','ES2.5'],scores)


def canonical_sample(name):
    if name in _CANONICAL:return _CANONICAL[name]
    r=M.load_returns(name).dropna()
    start=max(M.W,int(np.searchsorted(r.index,pd.Timestamp(M.EVAL_FROM))))
    _CANONICAL[name]=(r.index[start:],-r.iloc[start:])
    return _CANONICAL[name]


class ComparisonUnavailable(RuntimeError):
    def __init__(self,plan):
        self.plan=plan
        super().__init__('Comparison unavailable: incomplete original model universe')


def fc(name):
    if name not in _VALIDATED_FC:
        result=M.get_forecasts(name)
        _FC_REPORTS[name]=M.get_forecasts.last_diagnostics
        calendar,losses=canonical_sample(name)
        validate_forecast_contract(result[0],M.MODELS,calendar,losses,M.get_forecasts.last_diagnostics)
        _VALIDATED_FC[name]=result
    return _VALIDATED_FC[name]


def hits(name,model,col='VaR1'):
    df=fc(name)[0][model]
    values=df[['L',col]].to_numpy(dtype=float)
    if not np.isfinite(values).all():raise ValueError('Hit indicators require finite losses and forecasts')
    return (df['L']>df[col]).astype(int)


def es_inputs(name):
    frames,tails=fc(name);calendar,losses=canonical_sample(name)
    validate_es_contract(frames,M.MODELS,calendar,losses,_FC_REPORTS[name],tails,M.K_TAIL)
    return frames,tails,calendar,losses


def es_eligible(frame,calendar,losses):
    check=completeness(frame,calendar,['VaR2.5','ES2.5','pit','scale'],losses)
    if not check['eligible'] and check['reason']!='nonfinite_or_nonreal':raise ValueError(str(check))
    return check


def require_es_complete(name,model):
    frames,tails,calendar,losses=es_inputs(name)
    check=es_eligible(frames[model],calendar,losses)
    if not check['eligible']:raise ValueError('ES figure requires complete original sample: '+str(check))


def es_one(df,m,tails):
    mf = M.mcneil_frey(df['L'].values, df['VaR2.5'].values, df['ES2.5'].values, df['scale'].values)
    z = M.z_pvalues(df, m, tails, M=2000)
    de = M.du_escanciano(df['pit'].values)
    return dict(n_hit=mf['n'], MF_mean=mf['mean'], MF_t=mf['t'], MF_p=mf['p'], Z1=z['Z1'], p1=z['p1'], Z2=z['Z2'], p2=z['p2'], Z2_crit=z['crit2'], U_ES=de['U'], p_U=de['pU'], C_ES=de['C'], p_C=de['pC'], meanH=de['meanH'])


_CANONICAL={}


_VALIDATED_FC={}


_FC_REPORTS={}


def validate_conformal_frame(frame,calendar,losses):
    if not frame.index.equals(calendar) or not np.array_equal(frame['L'].values,losses.values):raise ValueError('Conformal canonical sample mismatch')
    for column in ['L','sd','alpha_t']:
        if not np.isfinite(frame[column].values).all():raise ValueError('Invalid conformal field: '+column)
    if (frame['sd']<=0).any():raise ValueError('Nonpositive conformal scale')
    for column in ['VaR_split','VaR_aci']:
        a=frame[column].values
        if np.isnan(a).any() or np.isneginf(a).any():raise ValueError('Invalid conformal quantile')
    return frame


def metric_display(records):
    rows={}
    for key,record in records.items():
        if record['status']=='computed':rows[key]=dict(status='computed',**record['result'])
        elif record['status']=='withheld' and record['result'] is None:rows[key]=dict(status='withheld: incomplete sample')
        else:raise ValueError('Invalid metric record')
    return pd.DataFrame.from_dict(rows, orient='index')


def mcs_display(records):
    rows={}
    for name,record in records.items():
        if record['status']=='computed':rows[name]=dict(status='computed',**record['result']['mcs'])
        elif record['status']=='withheld' and record['result'] is None:rows[name]=dict(status='withheld: incomplete sample')
        else:raise ValueError('Invalid MCS record')
    return pd.DataFrame.from_dict(rows, orient='index')


def show_conformal_rates(cf):
    import pandas as pd
    rows = []
    for market, data in cf.items():
        for method in ('split', 'aci', 'garch'):
            all_days, calm, crisis = data[method]
            rows.append({'Market': market, 'Method': {'split':'Split conformal','aci':'ACI','garch':'GARCH-t'}[method], 'Status': data['garch_status'] if method=='garch' else 'computed',
                         'All (%)':100*all_days, 'Calm (%)':100*calm, 'Crisis (%)':100*crisis})
    print('VaR 5% breach rates; percentages of the observations in each regime:')
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda x:f'{x:.2f}'))


# =============================================================================
# FIG 1: four assets, losses and GARCH-EVT VaR 1%
# =============================================================================
def fig_four_assets():
    fig,axs=plt.subplots(2,2,figsize=(7.0,4.2),sharex=False)
    out={}
    for ax,name in zip(axs.flat,M.ASSETS):
        df=fc(name)[0]['GARCH-EVT']
        available=df['VaR1'].notna()
        h=pd.Series(pd.NA,index=df.index,dtype='boolean')
        h.loc[available]=df.loc[available,'L']>df.loc[available,'VaR1']
        ax.plot(df.index,100*df['L'],color=Orange,lw=.5,alpha=.7,label='Daily loss')
        ax.plot(df.index,100*df['VaR1'],color=IDAred,lw=.7,label='VaR 1% (GARCH-EVT)')
        observed_breaches=h.fillna(False)
        ax.scatter(df.index[observed_breaches],100*df.loc[observed_breaches,'L'],s=4,color=MainBlue,zorder=3,label='Breach (available forecasts)')
        missing=int((~available).sum())
        if missing:
            ax.text(.02,.96,f'{missing} days without a forecast',transform=ax.transAxes,ha='left',va='top',fontsize=7,
                    bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
        ax.set_title(M.LABELS[name],fontsize=9)
        ax.set_ylabel('Loss (%)',fontsize=8);ax.tick_params(labelsize=7)
        ax.xaxis.set_major_locator(mdates.YearLocator(4 if name!='btc' else 2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        out[name]=dict(start=str(df.index[0].date()),end=str(df.index[-1].date()),T=len(df),
                       available_days=int(available.sum()),unavailable_days=missing)
    handles,labels=axs[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=8)
    fig.tight_layout(rect=(0,.08,1,1))
    save_fig('ch8_four_assets')
    return out


# =============================================================================
# FIG 2: S&P 500 -- losses, VaR 1% of HS and GARCH-t, breaches
# =============================================================================
def fig_sp500_var():
    F = fc('sp500')[0]
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    L = F['HS']['L']
    ax.plot(L.index, 100 * L, color=Orange, lw=0.5, alpha=0.6, label='Daily loss of the S&P 500')
    for m, ls in (('HS', '-'), ('GARCH-t', '-')):
        ax.plot(L.index, 100 * F[m]['VaR1'], color=MCOL[m], lw=0.8, ls=ls, label=f'VaR 1%, {m}')
    for m, mk in (('HS', 'o'), ('GARCH-t', 'x')):
        h = hits('sp500',m).astype(bool)
        ax.scatter(L.index[h], 100 * L[h] + (0.4 if m == 'GARCH-t' else 0), s=7, marker=mk, color=MCOL[m],
                   zorder=3, label=f'Breach, {m}' + (' (+0.4 pp)' if m == 'GARCH-t' else ''))
    ax.set_ylabel('Loss (%)')
    ax.autoscale(enable=True, axis='y')
    ax.margins(y=0.05)
    legend_outside_bottom(ax, ncol=3, y=-0.12)
    save_fig('ch8_sp500_var')
    return {m: int(hits('sp500', m).sum()) for m in ('HS', 'GARCH-t')}


# =============================================================================
# FIG 3: COVID-19 zoom (Feb.-June 2020), all models
# =============================================================================
def fig_covid_zoom():
    F = fc('sp500')[0]
    a, b = '2020-02-01', '2020-06-30'
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    L = F['HS']['L'].loc[a:b]
    ax.bar(L.index, 100 * L, color=Orange, alpha=0.5, width=1.0, label='Daily loss')
    out = {}
    for m in M.MODELS:
        v = F[m]['VaR1'].loc[a:b]
        ax.plot(v.index, 100 * v, color=MCOL[m], lw=1.0, label=m)
        out[m] = int(hits('sp500',m).loc[a:b].sum())
    ax.set_ylabel('Loss / VaR 1% (%)')
    legend_outside_bottom(ax, ncol=7, y=-0.12)
    save_fig('ch8_covid_zoom')
    out['max_loss'] = float(100 * L.max())
    out['max_loss_day'] = str(L.idxmax().date())
    out['T'] = len(L)
    return out


# =============================================================================
# FIG 4: VaR 1% breach rates by model and asset
# =============================================================================
def breach_table(col='VaR1',p=.01):
    return coverage_table(M.ASSETS,M.MODELS,lambda n:fc(n)[0],canonical_sample,M.kupiec,M.christoffersen,M.duration_test,_FC_REPORTS.__getitem__,col,p)


def fig_breach_rates(tab):
    fig,ax=plt.subplots(figsize=(7.0,3.6))
    w=.78/len(M.MODELS)
    for i,m in enumerate(M.MODELS):
        y=[100*tab[n,m]['result']['rate'] if tab[n,m]['status']=='computed' else np.nan for n in M.ASSETS]
        ax.bar(np.arange(len(M.ASSETS))+(i-(len(M.MODELS)-1)/2)*w,y,w,color=MCOL[m],label=m)
    for j,n in enumerate(M.ASSETS):
        missing=[m for m in M.MODELS if tab[n,m]['status']=='withheld']
        if missing:
            ax.text(j,.98,', '.join(missing)+'\nwithheld: incomplete sample',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=6)
    ax.axhline(1.0,color='black',lw=.8,ls='--',label='Nominal 1%')
    ax.set_xticks(range(len(M.ASSETS)),[M.LABELS[n] for n in M.ASSETS])
    ax.set_xlim(-.6,len(M.ASSETS)-.4)
    ax.set_ylabel('Breach rate of VaR 1% (%)')
    ax.margins(y=.35)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.13),ncol=4,frameon=False,fontsize=8)
    fig.subplots_adjust(left=.11,right=.98,top=.96,bottom=.27)
    save_fig('ch8_breach_rates')


# =============================================================================
# FIG 5: Kupiec statistic as a function of the number of breaches
# =============================================================================
def fig_kupiec_curve():
    fig, axs = plt.subplots(2, 1, figsize=(4.6, 4.2))
    out = {}
    for ax, T in zip(axs, (250, 1000)):
        xs = np.arange(0, int(0.03 * T) + 1)
        lr = np.array([M.kupiec(np.r_[np.ones(x), np.zeros(T - x)], 0.01)['LR'] for x in xs])
        acc = lr < stats.chi2.ppf(0.95, 1)
        ax.bar(xs[acc], lr[acc], color=Forest, width=0.8, label='Not rejected at 5%')
        ax.bar(xs[~acc], lr[~acc], color=IDAred, width=0.8, label='Rejected at 5%')
        ax.axhline(stats.chi2.ppf(0.95, 1), color='black', ls='--', lw=0.8, label=r'$\chi^2_1$ 5% critical value 3.84')
        ax.set_title(f'T = {T} days, α = 1%', fontsize=9)
        ax.set_xlabel('Number of breaches x')
        ax.set_ylim(0, max(25, 1.05 * float(lr.max())))
        out[T] = dict(lo=int(xs[acc].min()), hi=int(xs[acc].max()))
    axs[0].set_ylabel(r'LR$_{uc}$')
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=1, frameon=False)
    plt.tight_layout()
    save_fig('ch8_kupiec_curve')
    return out


# =============================================================================
# FIG 6: p-values of the VaR tests (Kupiec, Christoffersen, durations)
# =============================================================================
def fig_var_pvalues(tab):
    fig,axs=plt.subplots(1,3,figsize=(7.2,3.1),sharey=True)
    for ax,(key,title) in zip(axs,(('p_uc','Kupiec POF'),('p_cc','Christoffersen CC'),('p_dur','Duration (Weibull)'))):
        P=np.array([[tab[n,m]['result'][key] if tab[n,m]['status']=='computed' else np.nan for n in M.ASSETS] for m in M.MODELS])
        for i,m in enumerate(M.MODELS):
            for j,n in enumerate(M.ASSETS):
                if tab[n,m]['status']=='computed' and (not np.isfinite(P[i,j]) or not 0<=P[i,j]<=1):raise ValueError('Invalid computed coverage p-value')
        ax.imshow(np.ma.masked_invalid(np.log10(np.clip(P,1e-4,1))),cmap=PV_CMAP,vmin=-4,vmax=0,aspect='auto')
        for i in range(len(M.MODELS)):
            for j in range(len(M.ASSETS)):
                v=P[i,j];txt='—' if np.isnan(v) else ('<.001' if v<.001 else f'{v:.3f}')
                ax.text(j,i,txt,ha='center',va='center',fontsize=7,color='black')
        ax.set_xticks(range(len(M.ASSETS)),[M.LABELS[n] for n in M.ASSETS],rotation=30,fontsize=7.5)
        ax.set_yticks(range(len(M.MODELS)),M.MODELS,fontsize=7.5);ax.set_title(title,fontsize=9)
        for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.5,.015,'— withheld: incomplete sample',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1));save_fig('ch8_var_pvalues')


# =============================================================================
# FIG 7: breach timeline (S&P 500)
# =============================================================================
def fig_breach_timeline():
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    ms = ['HS', 'Normal', 'Student-t', 'GARCH-t', 'FHS', 'GARCH-EVT']
    for i, m in enumerate(ms):
        h = hits('sp500', m)
        d = h.index[h.values == 1]
        ax.vlines(d, i - 0.35, i + 0.35, color=MCOL[m], lw=0.8)
    ax.set_yticks(range(len(ms)), ms)
    ax.invert_yaxis()
    ax.set_xlabel('Breach days of VaR 1%, S&P 500')
    save_fig('ch8_breach_timeline')
    F = fc('sp500')[0]
    by_year = {m: {str(y): int(v) for y, v in hits('sp500', m).groupby(F[m].index.year).sum().items()} for m in ms}
    return by_year


# =============================================================================
# FIG 8: survival function of the durations between breaches
# =============================================================================
def fig_durations(tab):
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    out = {}
    for m in ('HS', 'Normal', 'GARCH-t', 'GARCH-EVT'):
        D, _, _ = M.durations(hits('sp500', m).values)
        Ds = np.sort(D)
        surv = 1 - np.arange(1, len(Ds) + 1) / (len(Ds) + 1)
        ax.step(Ds, surv, where='post', color=MCOL[m], label=f'{m} (b = {tab[("sp500", m)]["result"]["b"]:.2f})')
        out[m] = dict(n=len(D), median=float(np.median(D)), share_le5=float(np.mean(D <= 5)))
    d = np.linspace(1, 800, 200)
    ax.plot(d, (1 - 0.01) ** d, color='black', ls='--', lw=0.9, label='No memory, α = 1% (geometric)')
    ax.set_yscale('log')
    ax.set_xlabel('Days between consecutive breaches of VaR 1% (S&P 500)')
    ax.set_ylabel('Share of durations > d')
    legend_outside_bottom(ax, ncol=3, y=-0.2)
    save_fig('ch8_durations')
    return out


# =============================================================================
# FIG 9: Basel traffic light -- exceptions over 250 days (S&P 500)
# =============================================================================
def rolling_exceptions(name, model, col='VaR1', n=250):
    return hits(name, model, col).rolling(n).sum().dropna()


def fig_traffic_light():
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    ax.axhspan(-0.5, 4.5, color=Forest, alpha=0.10, lw=0)
    ax.axhspan(4.5, 9.5, color='#F1C40F', alpha=0.15, lw=0)
    out = {}
    for m in ('HS', 'Normal', 'GARCH-t', 'FHS'):
        x = rolling_exceptions('sp500', m)
        ax.plot(x.index, x, color=MCOL[m], lw=0.9, label=m)
        out[m] = dict(max=int(x.max()), max_day=str(x.idxmax().date()), share_red=float(np.mean(x >= 10)),
                      share_yellow=float(np.mean((x >= 5) & (x <= 9))), last=int(x.iloc[-1]))
    plot_top = max(40, 1.05 * max(v['max'] for v in out.values()))
    ax.axhspan(9.5, plot_top, color=IDAred, alpha=0.10, lw=0)
    ax.text(1.01, 2, 'green', color=Forest, fontsize=8, transform=ax.get_yaxis_transform())
    ax.text(1.01, 7.5, 'yellow', color=Amber, fontsize=8, transform=ax.get_yaxis_transform())
    ax.text(1.01, (9.5 + plot_top) / 2, 'red', color=IDAred, fontsize=8, transform=ax.get_yaxis_transform())
    ax.set_ylim(-0.5, plot_top)
    ax.set_ylabel('Exceptions of VaR 1%\nin the last 250 days')
    legend_outside_bottom(ax, ncol=4, y=-0.13)
    save_fig('ch8_traffic_light')
    return out


# =============================================================================
# ES TESTS: McNeil-Frey, Acerbi-Szekely, Du-Escanciano
# =============================================================================
def es_table():
    rows={}
    for name in M.ASSETS:
        frames,tails,calendar,losses=es_inputs(name)
        for model in M.MODELS:
            check=es_eligible(frames[model],calendar,losses)
            rows[name,model]=dict(status='computed' if check['eligible'] else 'withheld',reason=None if check['eligible'] else check,result=es_one(frames[model],model,tails) if check['eligible'] else None)
    return rows


def fig_es_pvalues(tab):
    fig,axs=plt.subplots(1,3,figsize=(7.2,3.1),sharey=True)
    for ax,(key,title) in zip(axs,(('MF_p','McNeil-Frey'),('p2','Acerbi-Szekely Z2'),('p_U','Du-Escanciano U'))):
        P=np.array([[tab[n,m]['result'][key] if tab[n,m]['status']=='computed' else np.nan for n in M.ASSETS] for m in M.MODELS])
        for i,m in enumerate(M.MODELS):
            for j,n in enumerate(M.ASSETS):
                if tab[n,m]['status']=='computed' and (not np.isfinite(P[i,j]) or not 0<=P[i,j]<=1):raise ValueError('Invalid computed ES p-value')
        ax.imshow(np.ma.masked_invalid(np.log10(np.clip(P,1e-4,1))),cmap=PV_CMAP,vmin=-4,vmax=0,aspect='auto')
        for i in range(len(M.MODELS)):
            for j in range(len(M.ASSETS)):
                v=P[i,j];txt='—' if np.isnan(v) else ('<.001' if v<.001 else f'{v:.3f}')
                ax.text(j,i,txt,ha='center',va='center',fontsize=7,color='black')
        ax.set_xticks(range(len(M.ASSETS)),[M.LABELS[n] for n in M.ASSETS],rotation=30,fontsize=7.5)
        ax.set_yticks(range(len(M.MODELS)),M.MODELS,fontsize=7.5);ax.set_title(title,fontsize=9)
        for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.5,.015,'— withheld: incomplete sample',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1));save_fig('ch8_es_pvalues')


def rolling_z2(name, model, n=250):
    require_es_complete(name,model)
    df = fc(name)[0][model]
    L, v, e = df['L'].values, df['VaR2.5'].values, df['ES2.5'].values
    term = np.where(L > v, L / e, 0.0)
    z2 = 1 - pd.Series(term, index=df.index).rolling(n).sum() / (n * M.A_ES)
    return z2.dropna()


def fig_z2_rolling():
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    out = {}
    for m in ('HS', 'Normal', 'GARCH-t', 'FHS'):
        z = rolling_z2('sp500', m)
        ax.plot(z.index, z, color=MCOL[m], lw=0.9, label=m)
        out[m] = dict(min=float(z.min()), min_day=str(z.idxmin().date()), share_below07=float(np.mean(z < -0.7)),
                      share_below18=float(np.mean(z < -1.8)), last=float(z.iloc[-1]))
    ax.axhline(-0.70, color=Amber, ls='--', lw=0.9, label='Threshold -0.70 (5%)')
    ax.axhline(-1.8, color=IDAred, ls='--', lw=0.9, label='Threshold -1.8 (0.01%)')
    ax.set_ylabel(r'$Z_2$ over the last 250 days')
    legend_outside_bottom(ax, ncol=3, y=-0.13)
    save_fig('ch8_z2_rolling')
    return out


def fig_mf_residuals():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    data, out = [], {}
    for m in M.MODELS:
        require_es_complete('sp500',m)
        df = fc('sp500')[0][m]
        h = df['L'] > df['VaR2.5']
        e = ((df['L'] - df['ES2.5']) / df['scale'])[h]
        data.append(e.values)
        out[m] = float(e.mean())
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=True,
                    flierprops=dict(marker='.', markersize=3, markeredgecolor=Gray))
    for b, m in zip(bp['boxes'], M.MODELS):
        b.set_facecolor(MCOL[m]); b.set_alpha(0.5)
    for i, m in enumerate(M.MODELS):
        ax.plot(i + 1, out[m], 'D', color='black', ms=4, label='Mean' if i == 0 else None)
    ax.axhline(0, color='black', lw=0.8, ls='--', label='Expected under a correct ES (mean 0)')
    ax.set_xticks(range(1, 7), M.MODELS)
    ax.set_ylabel('Exceedance residual (L - ES) / σ\n(σ: forecast volatility)')
    legend_outside_bottom(ax, ncol=2, y=-0.13)
    save_fig('ch8_mf_residuals')
    return out


# =============================================================================
# FIG: elicitability -- expected quantile (pinball) and FZ0 losses
# =============================================================================
def fig_elicitability(nu=4, a=0.025, n=2_000_000, seed=3):
    rng = np.random.default_rng(seed)
    L = rng.standard_t(nu, n) * np.sqrt((nu - 2) / nu)
    q_true, es_true = M.t_std_q(nu, a), M.t_std_es(nu, a)
    vs = np.linspace(1.2, 3.6, 121)
    m_plus = np.array([np.mean(np.maximum(L - v, 0)) for v in vs])      # E[(L - v)+]
    pin = m_plus - a * (np.mean(L) - vs)                                 # E[(1{L>v} - a)(L - v)]
    es_grid = np.linspace(1.6, 5.0, 121)
    V, E = np.meshgrid(vs, es_grid)
    FZ = np.interp(V, vs, m_plus) / (a * E) + V / E + np.log(E) - 1
    FZ = np.where(E >= V, FZ, np.nan)
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axs[0]
    ax.plot(vs, pin, color=MainBlue, label='Expected pinball loss')
    ax.axvline(q_true, color=IDAred, ls='--', lw=0.9, label=f'True VaR 2.5% = {q_true:.2f}')
    ax.set_xlabel('Reported VaR v')
    ax.set_ylabel('Expected loss')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    ax = axs[1]
    cs = ax.contour(V, E, FZ, levels=np.nanquantile(FZ, [0.01, 0.03, 0.08, 0.15, 0.3, 0.5]), colors=MainBlue,
                    linewidths=0.8)
    ax.clabel(cs, manual=[(2.1, 3.0), (2.5, 4.4)], fontsize=7, fmt='%.3f', inline_spacing=7)
    i = np.nanargmin(FZ)
    ax.plot(V.flat[i], E.flat[i], 'o', color=Forest, ms=5, label='Minimum of expected FZ0')
    ax.plot(q_true, es_true, 'x', color=IDAred, ms=8, label=f'True (VaR, ES) = ({q_true:.2f}, {es_true:.2f})')
    ax.set_xlabel('Reported VaR v')
    ax.set_ylabel('Reported ES e')
    legend_outside_bottom(ax, ncol=1, y=-0.2)
    plt.tight_layout()
    save_fig('ch8_elicitability')
    return dict(nu=nu, q=q_true, es=es_true, v_min=float(vs[np.argmin(pin)]), fz_v=float(V.flat[i]),
                fz_e=float(E.flat[i]))


# =============================================================================
# FZ0 LOSS, DIEBOLD-MARIANO, MCS
# =============================================================================
def fz_losses(name):
    calendar,losses=canonical_sample(name)
    result=guarded_fz_scores(fc(name)[0],M.MODELS,calendar,losses,M.fz0,lambda scores:scores)
    if result['status']=='withheld':raise ComparisonUnavailable(result['plan'])
    return result['result']


def fz_table():
    return comparative_table(M.ASSETS,M.MODELS,lambda n:fc(n)[0],canonical_sample,
                             M.fz0,M.diebold_mariano,M.mcs,M.pinball)


def fig_fz0(tab):
    comparative_figure(tab,M.ASSETS,M.MODELS,M.LABELS,MCOL)
    save_fig('ch8_fz0')


def fig_dm_matrix(name='sp500'):
    Lf = fz_losses(name)
    D = pd.DataFrame(index=M.MODELS, columns=M.MODELS, dtype=float)
    for a in M.MODELS:
        for b in M.MODELS:
            D.loc[a, b] = np.nan if a == b else M.diebold_mariano(Lf[a], Lf[b])['DM']
    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    im = ax.imshow(D.values.astype(float), cmap=LinearSegmentedColormap.from_list('dm', [Forest, '#FFFFFF', IDAred]),
                   vmin=-6, vmax=6)
    for i in range(6):
        for j in range(6):
            if i != j:
                ax.text(j, i, f'{D.values[i, j]:.1f}', ha='center', va='center', fontsize=7.5)
    ax.set_xticks(range(6), M.MODELS, rotation=30, fontsize=7.5)
    ax.set_yticks(range(6), M.MODELS, fontsize=7.5)
    ax.set_xlabel('Model B')
    ax.set_ylabel('Model A')
    cb = plt.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label('DM statistic (A minus B)', fontsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    save_fig('ch8_dm_matrix')
    return {f'{a}|{b}': float(D.loc[a, b]) for a in M.MODELS for b in M.MODELS if a != b}


def fig_mcs(tab):
    comparative_mcs_figure(tab,M.ASSETS,M.MODELS,M.LABELS,
                          cmap=LinearSegmentedColormap.from_list('mcs',[IDAred,'#FFFFFF',Forest]))
    save_fig('ch8_mcs')


# =============================================================================
# CONFORMAL PREDICTION
# =============================================================================
def conformal_table(a=0.01):
    out = {}
    for n in M.ASSETS:
        r = M.load_returns(n)
        c = M.conformal_var(r, a=a).loc[fc(n)[0]['HS'].index[0]:]
        reg = M.regimes(r, c.index)
        g = fc(n)[0]['GARCH-t']
        validate_conformal_frame(c,*canonical_sample(n))
        col = {0.01: 'VaR1', 0.05: 'VaR5', 0.025: 'VaR2.5'}[a]
        hs, ha = c['L'] > c['VaR_split'], c['L'] > c['VaR_aci']
        check=completeness(g,c.index,[col],c['L'])
        if not check['eligible'] and check['reason']!='nonfinite_or_nonreal':raise ValueError(str(check))
        hg=(g['L']>g[col]) if check['eligible'] else None
        out[n] = dict(T=len(c), n_crisis=int(reg.sum()),
                      split=[float(hs.mean()), float(hs[~reg].mean()), float(hs[reg].mean())],
                      aci=[float(ha.mean()), float(ha[~reg].mean()), float(ha[reg].mean())],
                      garch=[float(hg.mean()),float(hg[~reg].mean()),float(hg[reg].mean())] if hg is not None else [np.nan]*3,
                      garch_status='computed' if hg is not None else 'withheld', garch_reason=check,
                      inf_share=float(np.isinf(c['VaR_aci']).mean()),
                      kup_split=M.kupiec(hs.values, a)['p'], kup_aci=M.kupiec(ha.values, a)['p'])
    return out


def fig_conformal_path():
    r = M.load_returns('sp500')
    c = M.conformal_var(r, a=0.01).loc['2019-07-01':'2021-06-30']
    g = fc('sp500')[0]['GARCH-t']['VaR1'].loc[c.index]
    g_available=bool(np.isfinite(g).all())
    fig, axs = plt.subplots(2, 1, figsize=(6.8, 3.6), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1]))
    ax = axs[0]
    ax.bar(c.index, 100 * c['L'], color=Orange, alpha=0.5, width=1.0, label='Daily loss')
    ax.plot(c.index, 100 * c['VaR_split'], color=MainBlue, lw=1.0, label='Split conformal VaR 1%')
    va = np.where(np.isinf(c['VaR_aci']), np.nan, c['VaR_aci'])
    ax.plot(c.index, 100 * va, color=IDAred, lw=1.0, label='ACI VaR 1% (gaps: infinite)')
    if g_available:
        ax.plot(c.index,100*g,color=Forest,lw=.9,ls='--',label='GARCH-t VaR 1%')
    else:
        ax.plot([],[],color=Forest,ls='--',label='GARCH-t withheld: incomplete sample')
    ax.set_ylabel('Loss (%)')
    ax.autoscale(enable=True, axis="y")
    ax.margins(y=0.05)
    ax = axs[1]
    ax.plot(c.index, 100 * c['alpha_t'], color=IDAred, lw=1.0, label=r'ACI level $\alpha_t$')
    ax.axhline(1.0, color='black', ls='--', lw=0.8, label=r'Target $\alpha$ = 1%')
    ax.set_ylabel(r'$\alpha_t$ (%)')
    h1, l1 = axs[0].get_legend_handles_labels()
    h2, l2 = axs[1].get_legend_handles_labels()
    axs[1].legend(h1 + h2, l1 + l2, loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=3, frameon=False)
    save_fig('ch8_conformal_path')
    cc = c.loc['2020-02-20':'2020-04-30']
    return dict(covid_split=int((cc['L'] > cc['VaR_split']).sum()), covid_aci=int((cc['L'] > cc['VaR_aci']).sum()),
                covid_T=len(cc), covid_inf=int(np.isinf(cc['VaR_aci']).sum()), alpha_min=float(c['alpha_t'].min()))


def fig_conformal_regimes(tab):
    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    labels, x = [], 0
    for n in M.ASSETS:
        for j, (k, col) in enumerate((('split', MainBlue), ('aci', IDAred), ('garch', Forest))):
            ax.bar(x + j * 0.27 - 0.27, 100 * tab[n][k][1], 0.12, color=col, alpha=0.45,
                   label={'split': 'Split conformal', 'aci': 'ACI', 'garch': 'GARCH-t'}[k] + ', calm' if n == 'sp500' else None)
            ax.bar(x + j * 0.27 - 0.27 + 0.12, 100 * tab[n][k][2], 0.12, color=col,
                   label={'split': 'Split conformal', 'aci': 'ACI', 'garch': 'GARCH-t'}[k] + ', crisis' if n == 'sp500' else None)
        if tab[n]['garch_status']=='withheld':
            ax.text(x+.33,0,'GARCH withheld',rotation=90,ha='center',va='bottom',fontsize=7)
        labels.append(M.LABELS[n])
        x += 1
    ax.axhline(5.0, color='black', ls='--', lw=0.8, label='Nominal 5%')
    ax.set_xticks(np.arange(len(M.ASSETS)) + .06, labels)
    ax.set_ylabel('Breach rate of VaR 5% (%)')
    legend_outside_bottom(ax, ncol=4, y=-0.13)
    save_fig('ch8_conformal_regimes')


# =============================================================================
# WORKED EXAMPLES FOR THE LECTURE
# =============================================================================
def worked_examples():
    out = {}
    h = hits('sp500', 'GARCH-t').loc['2008']
    out['kupiec_2008'] = dict(M.kupiec(h.values, 0.01), zone=M.traffic_light(int(h.sum()), len(h))[0])
    h = hits('sp500', 'HS').loc['2007':'2010']
    out['chr_hs'] = dict(**M.transitions(h.values), **M.christoffersen(h.values, 0.01))
    h = hits('sp500', 'GARCH-t').loc['2007':'2010']
    out['chr_garch'] = dict(**M.transitions(h.values), **M.christoffersen(h.values, 0.01))
    # FRTB: desk-level exceptions in the last 250 days
    def window_hits(n, m, col, k=250):
        df = fc(n)[0][m].iloc[-k:]
        if not np.isfinite(df[['L', col]].to_numpy(dtype=float)).all():
            raise ValueError(f'{n} {m}: last {k} days need finite forecasts')
        return (df['L'] > df[col]).astype(int)
    out['desk'] = {n: {m: dict(x99=int(window_hits(n, m, 'VaR1').sum()),
                                x975=int(window_hits(n, m, 'VaR2.5').sum())) for m in M.MODELS}
                   for n in M.ASSETS}
    out['last_window'] = {n: [str(hits(n, 'HS').index[-250].date()), str(hits(n, 'HS').index[-1].date())]
                          for n in M.ASSETS}
    out['binom250'] = [float(stats.binom.cdf(k, 250, 0.01)) for k in range(0, 11)]
    # average model parameters
    out['params'] = {n: dict(nu_garch=float(fc(n)[0]['GARCH-t']['nu'].median()),
                             nu_t=float(fc(n)[0]['Student-t']['nu'].median()),
                             xi=float(fc(n)[0]['GARCH-EVT']['xi'].median())) for n in M.ASSETS}
    return out


# =============================================================================
# INFERENCE: DQ test, size and power (Monte Carlo), estimation risk,
# Giacomini-White, Nolde-Ziegel zones, Murphy diagram, multinomial test
# =============================================================================
def dq_test(hit, var, a, lags=4):
    """Dynamic Quantile test (Engle & Manganelli, 2004): Hit_t = I_t - a regressed on
    X_t = (1, Hit_{t-1..t-lags}, VaR_t); DQ = b'X'Xb / (a(1-a)) ~ chi2(k)."""
    h = np.asarray(hit, float) - a
    v = np.asarray(var, float)
    y = h[lags:]
    X = np.column_stack([np.ones(len(y))] + [h[lags - j:len(h) - j] for j in range(1, lags + 1)] + [v[lags:]])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    dq = float(b @ X.T @ X @ b / (a * (1 - a)))
    return dict(DQ=dq, df=X.shape[1], p=float(stats.chi2.sf(dq, X.shape[1])))


def dq_table(col='VaR1', a=.01):
    if col not in {'VaR1':.01,'VaR2.5':.025,'VaR5':.05} or a!={'VaR1':.01,'VaR2.5':.025,'VaR5':.05}[col]:
        raise ValueError('VaR column and probability must agree')
    out={}
    for name in M.ASSETS:
        frames=fc(name)[0]; calendar,losses=canonical_sample(name)
        validate_forecast_contract(frames,M.MODELS,calendar,losses,_FC_REPORTS[name])
        for model in M.MODELS:
            check=completeness(frames[model],calendar,[col],losses)
            if not check['eligible']:
                if check['reason']!='nonfinite_or_nonreal' or check.get('column')!=col:
                    raise ValueError('Forecast contract violation: '+str(check))
                out[f'{name}|{model}']=dict(status='withheld',reason=check,result=None)
                continue
            frame=frames[model]
            result=dq_test((frame['L']>frame[col]).astype(int).values,frame[col].values,a)
            out[f'{name}|{model}']=dict(status='computed',reason=None,result=result)
    return out


def fig_var_pvalues4(tab,dq):
    fig,axs=plt.subplots(2,2,figsize=(7.4,4.2),sharex=True,sharey=True)
    for ax,(key,title) in zip(axs.ravel(),(('p_uc','Kupiec POF'),('p_cc','Christoffersen CC'),('p_dur','Duration (Weibull)'),('dq','Dynamic Quantile'))):
        values=[]
        for model in M.MODELS:
            row=[]
            for name in M.ASSETS:
                record=dq[f'{name}|{model}'] if key=='dq' else tab[(name,model)]
                if record['status']=='withheld':
                    if record['result'] is not None: raise ValueError('Withheld result must be None')
                    value=np.nan
                elif record['status']=='computed':
                    value=record['result']['p' if key=='dq' else key]
                    if not np.isfinite(value) or not 0<=value<=1:raise ValueError('Invalid computed p-value')
                else:raise ValueError('Unknown metric status')
                row.append(value)
            values.append(row)
        P=np.asarray(values,dtype=float)
        ax.imshow(np.ma.masked_invalid(np.log10(np.clip(P,1e-4,1))),cmap=PV_CMAP,vmin=-4,vmax=0,aspect='auto')
        for i in range(len(M.MODELS)):
            for j in range(len(M.ASSETS)):
                v=P[i,j]
                txt='—' if np.isnan(v) else ('<.001' if v<.001 else f'{v:.3f}')
                ax.text(j,i,txt,ha='center',va='center',fontsize=7,color='black')
        ax.set_xticks(range(len(M.ASSETS)),[M.LABELS[n] for n in M.ASSETS],fontsize=7.5)
        ax.set_yticks(range(len(M.MODELS)),M.MODELS,fontsize=7.5)
        ax.set_title(title,fontsize=9)
        for spine in ax.spines.values():spine.set_visible(False)
        ax.label_outer()
    fig.text(.5,.015,'— withheld: incomplete sample',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1))
    save_fig('ch8_var_pvalues')


def pof_power(T, pis, a=0.01, level=0.05):
    """Exact power of the Kupiec test (LR, 5% level) under Binomial(T, pi) and the local
    noncentral chi2 approximation with parameter T (pi - a)^2 / (a(1-a))."""
    x = np.arange(T + 1)
    lr = np.array([M.kupiec(np.r_[np.ones(k), np.zeros(T - k)], a)['LR'] for k in x])
    rej = lr > stats.chi2.ppf(1 - level, 1)
    exact = np.array([stats.binom.pmf(x, T, p)[rej].sum() for p in pis])
    lam = T * (pis - a) ** 2 / (a * (1 - a))
    asym = stats.ncx2.sf(stats.chi2.ppf(1 - level, 1), 1, np.maximum(lam, 1e-12))
    return exact, asym, rej


def fig_pof_power():
    pis = np.linspace(0.0, 0.04, 401)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    out = {}
    for T, col in ((250, MainBlue), (1000, IDAred)):
        ex, asy, rej = pof_power(T, pis)
        ax.plot(100 * pis, ex, color=col, lw=1.4, label=f'Exact power, T = {T}')
        ax.plot(100 * pis, asy, color=col, lw=1.1, ls='--', label=f'Local asymptotic power, T = {T}')
        up = pis > 0.01
        half = float(pis[up][np.argmax(ex[up] >= 0.5)])
        eighty = float(pis[up][np.argmax(ex[up] >= 0.8)])
        i2 = int(np.argmin(abs(pis - 0.02)))
        out[str(T)] = dict(pi50=half, pi80=eighty, pow2=float(ex[i2]), asy2=float(asy[i2]),
                           size=float(ex[int(np.argmin(abs(pis - 0.01)))]))
    ax.axhline(0.05, color=Gray, lw=0.7, ls=':')
    ax.axvline(1.0, color=Gray, lw=0.7, ls=':')
    ax.set_xlabel('True breach probability (%) of a VaR 1% forecast')
    ax.set_ylabel('Rejection probability at 5%')
    ax.set_ylim(0, 1.02)
    legend_outside_bottom(ax, ncol=2, y=-0.2)
    save_fig('ch8_pof_power')
    return out


def sim_garch_t(par, n, reps, rng, burn=500):
    """GARCH(1,1)-t paths (standardised t innovations); returns the returns and sigma_t."""
    mu, om, a, b, nu = par
    z = rng.standard_t(nu, size=(reps, n + burn)) * np.sqrt((nu - 2) / nu)
    r = np.empty((reps, n + burn))
    s2 = np.full(reps, om / (1 - a - b))
    S = np.empty((reps, n + burn))
    for t in range(n + burn):
        S[:, t] = np.sqrt(s2)
        r[:, t] = mu + S[:, t] * z[:, t]
        s2 = om + a * (r[:, t] - mu) ** 2 + b * s2
    return r[:, burn:], S[:, burn:]


def mc_size_power(reps=1000, seed=8, Ts=(250, 1000, 5000), a=0.01, w=1000):
    """Monte Carlo: GARCH(1,1)-t DGP with the parameters estimated on the S&P 500, 1990-2026.
    VaR 1% forecasts: correct model (true parameters), Normal-GARCH (true sigma, Normal tail), HS (1000 days).
    Rejection rate at 5% for POF, CC, durations (Weibull) and DQ; undefined p (too few breaches) = no rejection."""
    r = M.load_returns('sp500').values
    par = M.garch_fit(r)
    mu, om, al, be, nu = par
    rng = np.random.default_rng(seed)
    Tmax = max(Ts)
    R, S = sim_garch_t(par, Tmax + w, reps, rng)
    L = -R[:, w:]
    q_t, q_n = M.t_std_q(nu, a), stats.norm.ppf(1 - a)
    out = {}
    for m in ('Correct', 'Normal-GARCH', 'HS'):
        rej = {T: {k: 0 for k in ('POF', 'CC', 'DUR', 'DQ')} for T in Ts}
        nan_dur = {T: 0 for T in Ts}
        for i in range(reps):
            if m == 'Correct':
                v = -mu + S[i, w:] * q_t
            elif m == 'Normal-GARCH':
                v = -mu + S[i, w:] * q_n
            else:
                v = pd.Series(-R[i]).rolling(w).quantile(1 - a).shift(1).values[w:]
            I = (L[i] > v).astype(int)
            for T in Ts:
                h, vv = I[:T], v[:T]
                rej[T]['POF'] += M.kupiec(h, a)['p'] < 0.05
                rej[T]['CC'] += M.christoffersen(h, a)['p_cc'] < 0.05 if h.sum() > 0 else 0
                d = M.duration_test(h)['p']
                nan_dur[T] += np.isnan(d)
                rej[T]['DUR'] += (d < 0.05) if not np.isnan(d) else 0
                rej[T]['DQ'] += dq_test(h, vv, a)['p'] < 0.05
        out[m] = {str(T): dict({k: v / reps for k, v in rej[T].items()}, dur_nan=nan_dur[T] / reps) for T in Ts}
    out['par'] = dict(mu=mu, omega=om, alpha=al, beta=be, nu=nu)
    out['reps'] = reps
    return out


def mc_estimation_risk(reps=400, seed=9, Rw=1000, Ps=(250, 1000, 5000), a=0.01):
    """Estimation risk: GARCH-t estimated once on R = 1000 days (fixed scheme), VaR 1% over P days.
    POF rejection rate at 5% with estimated versus true parameters, on the same paths.
    If any replication has no admissible estimate, withhold estimated aggregates over the original replication set."""
    r0 = M.load_returns('sp500').values
    par = M.garch_fit(r0)
    rng = np.random.default_rng(seed)
    Pm = max(Ps)
    R, S = sim_garch_t(par, Rw + Pm, reps, rng)
    mu0, _, _, _, nu0 = par
    rej_est = {P: 0 for P in Ps}
    rej_true = {P: 0 for P in Ps}
    rate_est = {P: [] for P in Ps}
    fit_records=[]
    unavailable=[]
    for i in range(reps):
        x = R[i, :Rw]
        v_true = -mu0 + S[i, Rw:] * M.t_std_q(nu0, a)
        L = -R[i, Rw:]
        for P in Ps:
            ht = (L[:P] > v_true[:P]).astype(int)
            rej_true[P] += M.kupiec(ht, a)['p'] < 0.05
        try:
            mu, om, al, be, nu = M.garch_fit(x)
        except M.NoAdmissibleInitialFit:
            unavailable.append(i)
            fit_records.append(dict(replication=i, **M.garch_fit.last_diagnostic))
            continue
        fit_records.append(dict(replication=i, **M.garch_fit.last_diagnostic))
        nu = max(nu, 2.2)
        s2 = M.garch_filter(R[i], mu, om, al, be, np.var(x[:50]))
        v_est = -mu + np.sqrt(s2[Rw:Rw + Pm]) * M.t_std_q(nu, a)
        v_true = -mu0 + S[i, Rw:] * M.t_std_q(nu0, a)
        L = -R[i, Rw:]
        for P in Ps:
            he = (L[:P] > v_est[:P]).astype(int)
            rej_est[P] += M.kupiec(he, a)['p'] < 0.05
            rate_est[P].append(he.mean())
    complete=not unavailable
    return {str(P): dict(est=rej_est[P]/reps if complete else None,
                         true=rej_true[P]/reps,
                         sd_rate=float(np.std(rate_est[P])) if complete else None,
                         sd_binom=float(np.sqrt(a*(1-a)/P)),
                         estimated_status='computed' if complete else 'withheld')
            for P in Ps} | dict(reps=reps, unavailable_replications=unavailable,
                               fit_diagnostics=fit_records,
                               estimated_reason=None if complete else 'incomplete original replication set')


def gw_test(la, lb):
    """Giacomini-White (2006) test of conditional predictive ability, horizon 1:
    Z_t = h_{t-1} d_t with h_{t-1} = (1, d_{t-1}); W = T Zbar' Omega^{-1} Zbar ~ chi2(2)."""
    d = np.asarray(la) - np.asarray(lb)
    Z = np.column_stack([d[1:], d[:-1] * d[1:]])
    T = len(Z)
    zb = Z.mean(0)
    Om = Z.T @ Z / T
    W = float(T * zb @ np.linalg.solve(Om, zb))
    u = d.mean() / np.sqrt(np.mean(d ** 2) / len(d))
    return dict(W=W, p=float(stats.chi2.sf(W, 2)), unc=float(u), p_unc=float(2 * stats.norm.sf(abs(u))))


def gw_table():
    Lf = fz_losses('sp500')
    return {f'{a}|FHS': gw_test(Lf[a], Lf['FHS']) for a in ('GARCH-t', 'HS', 'GARCH-EVT', 'Normal')}


def nz_zones(standard='HS',internals=('GARCH-t','FHS','GARCH-EVT'),level=.05):
    return comparative_zones(M.ASSETS,M.MODELS,lambda n:fc(n)[0],canonical_sample,
                             M.fz0,M.diebold_mariano,standard,internals,level)


def comparative_zones(assets, models, frames_for, canonical_for, fz0, diebold_mariano,
                      standard='HS', internals=('GARCH-t','FHS','GARCH-EVT'), level=.05):
    if standard not in models or any(m not in models for m in internals):
        raise ValueError('Zone models must belong to the original universe')
    if standard in internals:
        raise ValueError('The standard cannot also be an internal model')
    if not 0 < level < .5:
        raise ValueError('level must lie between 0 and .5')
    z=stats.norm.ppf(1-level)
    out={}
    for name in assets:
        calendar,losses=canonical_for(name)
        def evaluate(F):
            Lf=pd.DataFrame({m:fz0(F[m]['L'].values,F[m]['VaR2.5'].values,F[m]['ES2.5'].values)
                             for m in models},index=calendar)
            if not np.isfinite(Lf.to_numpy()).all():
                raise ValueError('FZ0 produced nonfinite scores on complete inputs')
            result={}
            for m in internals:
                dm=diebold_mariano(Lf[m],Lf[standard])['DM']
                if not np.isfinite(dm):
                    raise ValueError('DM statistic is nonfinite; no zone assigned')
                # Negative DM means lower FZ0 loss for the internal model.
                result[m]=dict(DM=float(dm),zone='green' if dm < -z else ('red' if dm > z else 'yellow'))
            return result
        out[name]=execute_joint_metric(frames_for(name),models,calendar,losses,
                                      ['VaR2.5','ES2.5'],evaluate)
    return out






def elementary_scores(L, v, thetas, tau):
    """Elementary scores for the quantile of order tau (Ehm et al., 2016):
    S_theta(v, y) = (1{y < v} - tau)(1{theta < v} - 1{theta < y}); matrix T x len(thetas)."""
    L = np.asarray(L)[:, None]
    v = np.asarray(v)[:, None]
    th = np.asarray(thetas)[None, :]
    return ((L < v) - tau) * ((th < v).astype(float) - (th < L).astype(float))


def murphy(name, mA, mB, col='VaR1', a=0.01, n=240):
    F = fc(name)[0]
    L = F[mA]['L'].values
    lo, hi = np.nanquantile(np.r_[F[mA][col], F[mB][col]], [0.01, 0.99])   # range covered by the forecasts
    th = np.linspace(0.8 * lo, hi, n)
    SA = elementary_scores(L, F[mA][col].values, th, 1 - a)
    SB = elementary_scores(L, F[mB][col].values, th, 1 - a)
    D = SA - SB
    se = np.array([np.sqrt(M.nw_var(D[:, j]) / len(D)) for j in range(n)])
    return th, SA.mean(0), SB.mean(0), D.mean(0), se


def fig_murphy(name='sp500', mA='GARCH-t', mB='FHS'):
    th, a_, b_, d, se = murphy(name, mA, mB)
    fig, axs = plt.subplots(2, 1, figsize=(4.6, 4.2))
    axs[0].plot(100 * th, 1e4 * a_, color=MCOL[mA], lw=1.3, label=mA)
    axs[0].plot(100 * th, 1e4 * b_, color=MCOL[mB], lw=1.3, label=mB)
    axs[0].set_xlabel('Threshold θ (daily loss, %)')
    axs[0].set_ylabel('Mean elementary\nscore (×10⁴)')
    axs[0].set_title('Murphy diagram, VaR 1%, S&P 500', fontsize=9)
    axs[1].fill_between(100 * th, 1e4 * (d - 1.96 * se), 1e4 * (d + 1.96 * se), color=LightGray, alpha=0.8,
                        label='95% pointwise band (HAC)')
    axs[1].plot(100 * th, 1e4 * d, color=Purple, lw=1.3, label=f'{mA} minus {mB}')
    axs[1].axhline(0, color=Gray, lw=0.7)
    axs[1].set_xlabel('Threshold θ (daily loss, %)')
    axs[1].set_ylabel('Score difference (×10⁴)')
    axs[1].set_title('Difference: above 0 means FHS better', fontsize=9)
    h0, l0 = axs[0].get_legend_handles_labels()
    h1, l1 = axs[1].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch8_murphy')
    sig_pos = (d - 1.96 * se) > 0
    sig_neg = (d + 1.96 * se) < 0
    lo5 = th < 0.05
    return dict(neg_ge5=float(np.mean(d[~lo5] < 0)), zero_lt5=float(np.mean(~sig_pos[lo5] & ~sig_neg[lo5])), share_pos_lt5=float(np.mean(d[lo5] > 0)),
                share_pos=float(np.mean(d > 0)), share_sig_pos=float(np.mean(sig_pos)),
                share_sig_neg=float(np.mean(sig_neg)), share_neg=float(np.mean(d < 0)),
                th_min=float(th[0]), th_max=float(th[-1]),
                th_sig_lo=float(th[sig_pos].min()) if sig_pos.any() else None,
                th_sig_hi=float(th[sig_pos].max()) if sig_pos.any() else None)


# Google-validated wrappers (synchronised from MFM_ch8_comparative)
_original_murphy=murphy


def murphy(name,mA,mB,col='VaR1',a=.01,n=240):
    calendar,losses=canonical_sample(name)
    result=execute_joint_metric(fc(name)[0],M.MODELS,calendar,losses,[col],
                               lambda F:_original_murphy(name,mA,mB,col,a,n))
    if result['status']=='withheld':raise ComparisonUnavailable(result['plan'])
    return result['result']


def unavailable_figure(name,asset):
    fig,ax=plt.subplots(figsize=(5.4,3.3))
    ax.text(.5,.5,'Comparison unavailable\n'+M.LABELS[asset],ha='center',va='center',transform=ax.transAxes)
    ax.set_axis_off()
    save_fig(name)


_original_dm_figure=fig_dm_matrix


def fig_dm_matrix(name='sp500'):
    try:return dict(status='computed',result=_original_dm_figure(name))
    except ComparisonUnavailable as e:
        unavailable_figure('ch8_dm_matrix',name)
        return dict(status='withheld',plan=e.plan,result=None)


_original_gw_table=gw_table


def gw_table():
    try:return dict(status='computed',result=_original_gw_table())
    except ComparisonUnavailable as e:return dict(status='withheld',plan=e.plan,result=None)


_original_murphy_figure=fig_murphy


def fig_murphy(name='sp500',mA='GARCH-t',mB='FHS'):
    try:return dict(status='computed',result=_original_murphy_figure(name,mA,mB))
    except ComparisonUnavailable as e:
        unavailable_figure('ch8_murphy',name)
        return dict(status='withheld',plan=e.plan,result=None)



def murphy_summary(name, mA, mB, col, a):
    th, a_, b_, d, se = murphy(name, mA, mB, col, a)
    return dict(share_pos=float(np.mean(d > 0)), share_neg=float(np.mean(d < 0)),
                share_sig_pos=float(np.mean((d - 1.96 * se) > 0)), share_sig_neg=float(np.mean((d + 1.96 * se) < 0)),
                crosses=bool((d > 0).any() and (d < 0).any()))


def multinomial_table(N=4,a=.025):
    lev=np.array([1-a*(1-j/N) for j in range(N)])
    probs=np.diff(np.r_[0.,lev,1.]);out={}
    for name in M.ASSETS:
        frames,tails,calendar,losses=es_inputs(name)
        for model in M.MODELS:
            check=es_eligible(frames[model],calendar,losses)
            if not check['eligible']:
                out[f'{name}|{model}']=dict(status='withheld',reason=check,result=None);continue
            u=frames[model]['pit'].values
            cell=np.sum(u[:,None]>lev[None,:],axis=1)
            O=np.bincount(cell,minlength=N+1);E=len(u)*probs
            S=float(((O-E)**2/E).sum())
            out[f'{name}|{model}']=dict(status='computed',reason=None,result=dict(S=S,p=float(stats.chi2.sf(S,N)),O=O.tolist()))
    out['probs']=probs.tolist();return out


def extras(R):
    """Inference blocks of the lecture (DQ, power, estimation risk, GW, Nolde-Ziegel, Murphy, multinomial)."""
    R['dq'] = dq_table()
    fig_var_pvalues4(R['var99'], R['dq'])
    R['pof_power'] = fig_pof_power()
    R['gw'] = gw_table()
    R['nz'] = nz_zones()
    R['murphy'] = fig_murphy()
    try:
        R['murphy_btc'] = murphy_summary('btc', 'HS', 'GARCH-EVT', 'VaR2.5', 0.025)
    except ComparisonUnavailable as e:
        R['murphy_btc'] = dict(status='withheld', plan=e.plan)
    R['multinomial'] = multinomial_table()
    R['mc'] = mc_size_power()
    R['estrisk'] = mc_estimation_risk()
    return R


# =============================================================================
# CASE STUDY: Bayer & Dimitriadis (2022), regression-based ES backtesting
# =============================================================================
# Table 3 of the published paper (Journal of Financial Econometrics 20(3), 2022): share of the 200 largest S&P 500
# stocks for which the one-sided Intercept ESR test rejects the ES 2.5% forecasts at 5%; out-of-sample Jan 2010 - Aug 2019.
# Rows: rolling window (days); columns: refit frequency (days).
BD_WINDOWS = (250, 500, 1000, 1500, 2000)
BD_REFITS = (5, 21, 62, 125, 250)
BD_TABLE3 = {
    'GARCH-N': [[0.96, 0.96, 0.95, 0.95, 0.92], [0.94, 0.94, 0.93, 0.91, 0.87], [0.86, 0.88, 0.87, 0.83, 0.83],
                [0.85, 0.88, 0.86, 0.87, 0.87], [0.81, 0.82, 0.83, 0.82, 0.80]],
    'GJR-GARCH-N': [[0.96, 0.96, 0.95, 0.92, 0.90], [0.93, 0.93, 0.94, 0.94, 0.91], [0.93, 0.93, 0.91, 0.89, 0.91],
                    [0.93, 0.93, 0.93, 0.93, 0.91], [0.92, 0.92, 0.91, 0.92, 0.91]],
    'GARCH-t': [[0.00, 0.01, 0.04, 0.06, 0.12], [0.00, 0.00, 0.01, 0.01, 0.02], [0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.01, 0.00, 0.01, 0.01], [0.00, 0.00, 0.00, 0.01, 0.01]],
    'GJR-GARCH-t': [[0.00, 0.00, 0.01, 0.02, 0.04], [0.00, 0.00, 0.01, 0.01, 0.01], [0.00, 0.00, 0.00, 0.00, 0.01],
                    [0.00, 0.01, 0.00, 0.00, 0.01], [0.00, 0.01, 0.00, 0.01, 0.01]],
}
# large S&P 500 stocks in the course data with daily prices from 2002 (2000-day window before January 2010)
BD_STOCKS = ['AAPL.US', 'MSFT.US', 'AMZN.US', 'NVDA.US', 'CSCO.US', 'JPM.US', 'BAC.US', 'C.US', 'WFC.US', 'GS.US',
             'MS.US']
BD_OOS = ('2010-01-01', '2019-08-31')
BD_TAU = 0.025


ESBACK_R = r"""
lib <- Sys.getenv('MFM_RLIB'); dir.create(lib, showWarnings = FALSE, recursive = TRUE); .libPaths(c(lib, .libPaths()))
if (!requireNamespace('esback', quietly = TRUE))
  install.packages('esback', lib = lib, repos = 'https://cloud.r-project.org', quiet = TRUE)
args <- commandArgs(trailingOnly = TRUE)
d <- read.csv(args[1]); tau <- as.numeric(args[3])
RNGkind("L'Ecuyer-CMRG"); set.seed(8)
p <- parallel::mclapply(split(d, d$id), function(s) {
  b <- tryCatch(suppressWarnings(esback::esr_backtest(r = s$r, e = s$e, alpha = tau, version = 3)), error=function(e) e)
  if(inherits(b, "error")) return(data.frame(id=s$id[1], p=NA_real_, p2=NA_real_, error=conditionMessage(b)))
  data.frame(id = s$id[1], p = b$pvalue_onesided_asymptotic, p2 = b$pvalue_twosided_asymptotic, error="")
}, mc.cores = max(1, parallel::detectCores() - 1))
write.csv(do.call(rbind, p), args[2], row.names = FALSE)
"""


def esr_intercept(series, tau=BD_TAU):
    """One-sided Intercept ESR test of Bayer-Dimitriadis (Eq. 1.14-1.15) with the authors' R package esback:
    joint regression of r_t - e_t on (1, e_t) for the quantile and on a constant for the ES, FZ0-type loss
    (esreg, G1 = 2, G2 = 1), misspecification-robust covariance (sparsity 'nid', 'scl_sp'); H0: gamma_1 >= 0.
    series: dict id -> DataFrame with columns r (return) and e (ES forecast, return units). Needs R (Rscript)."""
    import subprocess
    tmp = tempfile.mkdtemp()
    d = pd.concat([df.assign(id=k)[['id', 'r', 'e']] for k, df in series.items()])
    d.to_csv(os.path.join(tmp, 'in.csv'), index=False)
    with open(os.path.join(tmp, 'esback.R'), 'w') as f:
        f.write(ESBACK_R)
    env = dict(os.environ, MFM_RLIB=os.path.join(tempfile.gettempdir(), 'mfm_rlib'))
    subprocess.run(['Rscript', os.path.join(tmp, 'esback.R'), os.path.join(tmp, 'in.csv'),
                    os.path.join(tmp, 'out.csv'), str(tau)], check=True, env=env)
    return pd.read_csv(os.path.join(tmp, 'out.csv')).set_index('id')


def garch_es_forecasts(r, dist, w, refit, oos):
    """Rolling one-day-ahead ES_tau forecasts (return units, negative) of a constant-mean GARCH(1,1) with Normal
    or Student-t innovations: window of w days, parameters re-estimated every `refit` days, volatility updated
    daily with the last parameters. r: log returns in percent (Series); oos: (start, end)."""
    from arch import arch_model
    idx = np.where((r.index >= oos[0]) & (r.index <= oos[1]))[0]
    x = r.values
    e = np.full(len(idx), np.nan)
    for j0 in range(0, len(idx), refit):
        s = idx[j0]
        res = arch_model(x[s - w:s], mean='Constant', vol='GARCH', p=1, q=1,
                         dist='t' if dist == 't' else 'normal').fit(disp='off', show_warning=False)
        mu, om, al, be = (res.params[k] for k in ('mu', 'omega', 'alpha[1]', 'beta[1]'))
        esz = (M.t_std_es(res.params['nu'], BD_TAU) if dist == 't'
               else stats.norm.pdf(stats.norm.ppf(BD_TAU)) / BD_TAU)
        s2 = res.conditional_volatility[-1] ** 2
        eps = x[s - 1] - mu
        for j in range(j0, min(j0 + refit, len(idx))):
            s2 = om + al * eps ** 2 + be * s2
            e[j] = mu - np.sqrt(s2) * esz
            eps = x[idx[j]] - mu
    return pd.Series(e, index=r.index[idx])


def _bd_one(sym, dist, w, refit):
    r = 100 * np.log(M.read_market(sym)['adjusted_close']).diff().dropna()
    e = garch_es_forecasts(r, dist, w, refit, BD_OOS)
    return f'{sym}|{dist}|{w}|{refit}', pd.DataFrame({'r': r.loc[e.index].values, 'e': e.values})


def esr_preflight():
    """Check R before forecasts; install missing esback in the same temp library as ESBACK_R."""
    import shutil
    import subprocess
    rscript = shutil.which('Rscript')
    if rscript is None:
        raise RuntimeError('ESR requires Rscript. Install R in this environment before running the forecast grid; no forecasts were started.')
    code = """
lib <- Sys.getenv('MFM_RLIB'); dir.create(lib, showWarnings = FALSE, recursive = TRUE); .libPaths(c(lib, .libPaths()))
if (!requireNamespace('esback', quietly = TRUE))
  install.packages('esback', lib = lib, repos = 'https://cloud.r-project.org', quiet = TRUE)
if (!requireNamespace('esback', quietly = TRUE)) stop('esback is unavailable after installation; forecast grid was not started')
cat('ESR preflight: R ', as.character(getRversion()), ', esback ', as.character(utils::packageVersion('esback')), '\n', sep='')
"""
    print('Checking Rscript and esback before the forecast grid...', flush=True)
    env = dict(os.environ, MFM_RLIB=os.path.join(tempfile.gettempdir(), 'mfm_rlib'))
    subprocess.run([rscript, '-e', code], check=True, env=env)


def bd_replication(n_jobs=-1):
    """Table 3 design on the course data: GARCH(1,1)-N and GARCH(1,1)-t, five windows x five refit frequencies,
    one-sided Intercept ESR at 5%; share of the stocks rejected."""
    esr_preflight()
    from joblib import Parallel, delayed
    jobs = [(s, d, w, k) for s in BD_STOCKS for d in ('normal', 't') for w in BD_WINDOWS for k in BD_REFITS]
    print(f'Forecast grid: {len(jobs)} tasks; joblib reports completed batches.', flush=True)
    series = dict(Parallel(n_jobs=n_jobs, verbose=10)(delayed(_bd_one)(*j) for j in jobs))
    print(f'Forecast grid complete: {len(series)} series. Starting ESR regressions in R.', flush=True)
    pv = esr_intercept(series)
    print(f'R ESR stage complete: {len(pv)} regression results.', flush=True)
    rows = pd.DataFrame([dict(zip(('sym', 'dist', 'w', 'refit'), k.split('|')), T=len(series[k]),
                              p=pv.loc[k, 'p'], p2=pv.loc[k, 'p2'], error=pv.loc[k, 'error']) for k in series])
    rows[['w', 'refit']] = rows[['w', 'refit']].astype(int)
    valid = np.isfinite(rows['p'].to_numpy(dtype=float))
    rows['reject'] = np.where(valid, rows['p'] < 0.05, np.nan)
    print(f'ESR fits: {len(rows)} attempted, {valid.sum()} valid, {(~valid).sum()} failed; rejection shares use valid fits only.')
    print('Valid denominators by distribution, window and refit:')
    print(rows.assign(valid=valid).groupby(['dist', 'w', 'refit'])['valid'].sum().to_string())
    if not valid.all():
        print(rows.loc[~valid, ['sym', 'dist', 'w', 'refit', 'error']].to_string(index=False))
    share = {d: rows[rows.dist == d].pivot_table(index='w', columns='refit', values='reject', aggfunc='mean')
             for d in ('normal', 't')}
    return rows, share


def fig_bd_table3():
    """Table 3 of Bayer-Dimitriadis: rejection shares by estimation window, weekly and yearly refit."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    x = np.arange(len(BD_WINDOWS))
    for ax, fam in zip(axs, ('GARCH', 'GJR-GARCH')):
        for d, col in (('N', IDAred), ('t', MainBlue)):
            tab = np.array(BD_TABLE3[f'{fam}-{d}'])
            lab = 'Normal' if d == 'N' else 'Student-t'
            ax.plot(x, tab[:, 0], '-o', color=col, ms=4, label=f'{lab} innovations, weekly refit (5 days)')
            ax.plot(x, tab[:, 4], '--s', color=col, ms=4, label=f'{lab} innovations, yearly refit (250 days)')
        ax.axhline(0.05, color=Gray, lw=0.8, ls=':', label='Nominal size 5%')
        ax.set_xticks(x, [str(v) for v in BD_WINDOWS])
        ax.set_xlabel('Rolling estimation window (days)')
        ax.set_title(f'{fam}(1,1)', fontsize=10)
        ax.set_ylim(-0.03, 1.05)
    axs[0].set_ylabel('Share of stocks rejected')
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
    plt.tight_layout()
    save_fig('ch8_bd_table3')


def fig_bd_replication(rows, share):
    """Course-data replication of Table 3 (GARCH(1,1)): share of stocks rejected, Normal versus Student-t."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    x = np.arange(len(BD_WINDOWS))
    paperN, papert = np.array(BD_TABLE3['GARCH-N']), np.array(BD_TABLE3['GARCH-t'])
    for ax, k, ttl in zip(axs, (0, 4), ('Weekly refit (5 days)', 'Yearly refit (250 days)')):
        ref = BD_REFITS[k]
        ax.plot(x, share['normal'][ref].values, '-o', color=IDAred, ms=4,
                label='Normal innovations, valid fits (course data)')
        ax.plot(x, share['t'][ref].values, '-o', color=MainBlue, ms=4,
                label='Student-t innovations, valid fits (course data)')
        ax.plot(x, paperN[:, k], '--s', color=Orange, ms=3.5, label='Normal innovations, 200 stocks (Table 3)')
        ax.plot(x, papert[:, k], '--s', color=Teal, ms=3.5, label='Student-t innovations, 200 stocks (Table 3)')
        ax.axhline(0.05, color=Gray, lw=0.8, ls=':', label='Nominal size 5%')
        ax.set_xticks(x, [str(v) for v in BD_WINDOWS])
        ax.set_xlabel('Rolling estimation window (days)')
        ax.set_title(ttl, fontsize=10)
        ax.set_ylim(-0.03, 1.05)
    axs[0].set_ylabel('Share of stocks rejected')
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    plt.tight_layout()
    save_fig('ch8_bd_replication')
    t = rows[rows.dist == 't']
    n = rows[rows.dist == 'normal']
    return dict(T=int(rows['T'].iloc[0]), n_stocks=len(BD_STOCKS),
                n_attempted=len(rows), n_valid=int(rows['p'].notna().sum()),
                failed_fits=rows.loc[rows['p'].isna(), ['sym','dist','w','refit','error']].to_dict('records'),
                share_n={str(w): {str(k): float(share['normal'].loc[w, k]) for k in BD_REFITS} for w in BD_WINDOWS},
                share_t={str(w): {str(k): float(share['t'].loc[w, k]) for k in BD_REFITS} for w in BD_WINDOWS},
                n_min=float(share['normal'].values.min()), n_max=float(share['normal'].values.max()),
                t_min=float(share['t'].values.min()), t_max=float(share['t'].values.max()),
                p_n_median=float(n['p'].median()), p_t_median=float(t['p'].median()),
                t_250_250=float(share['t'].loc[250, 250]),
                t_long=float(share['t'].loc[[1500, 2000], [5, 21, 62]].values.mean()),
                t_long_max=float(share['t'].loc[[1500, 2000], [5, 21, 62]].values.max()))


def case_study(R):
    """Case study (Bayer-Dimitriadis, 2022): Table 3 chart and its replication on the course data."""
    fig_bd_table3()
    rows, share = bd_replication()
    R['bd'] = fig_bd_replication(rows, share)
    return R


def to_py(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, str) else '|'.join(map(str, k)) if isinstance(k, tuple) else str(k)): to_py(v)
                for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


if __name__ == '__main__' and '--case' in sys.argv:
    # only the case study block, added to the existing results
    R = json.load(open(os.path.join(HERE, 'ch8_results.json')))
    case_study(R)
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('case study done')
elif __name__ == '__main__' and '--extras' in sys.argv:
    # only the inference blocks, added to the existing results
    R = json.load(open(os.path.join(HERE, 'ch8_results.json')))
    extras(R)
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('extras done')
elif __name__ == '__main__':
    R = {}
    R['assets'] = fig_four_assets()
    R['sp500_var'] = fig_sp500_var()
    R['covid'] = fig_covid_zoom()
    tab = breach_table()
    tab975 = breach_table('VaR2.5', 0.025)
    R['var99'] = tab
    R['var975'] = tab975
    fig_breach_rates(tab)
    R['kupiec_curve'] = fig_kupiec_curve()
    fig_var_pvalues(tab)
    R['timeline'] = fig_breach_timeline()
    R['durations'] = fig_durations(tab)
    R['traffic'] = fig_traffic_light()
    est = es_table()
    R['es'] = est
    fig_es_pvalues(est)
    R['z2_rolling'] = fig_z2_rolling()
    R['mf_resid'] = fig_mf_residuals()
    R['elicit'] = fig_elicitability()
    fz = fz_table()
    R['fz'] = fz
    fig_fz0(fz)
    R['dm_sp500'] = fig_dm_matrix()
    fig_mcs(fz)
    R['conformal'] = conformal_table(0.01)
    R['conformal5'] = conformal_table(0.05)
    R['conf_path'] = fig_conformal_path()
    fig_conformal_regimes(R['conformal5'])
    R['worked'] = worked_examples()
    extras(R)
    case_study(R)
    with open(os.path.join(HERE, 'ch8_results.json'), 'w') as f:
        json.dump(to_py(R), f, indent=1, default=str)
    print('done')

"""
Black Thursday, 24 October 1929: the Dow Jones Industrial Average, daily closes 1921-1955
=========================================================================================
Data: Samuel H. Williamson, 'Daily Closing Value of the Dow Jones Average, 1885 to Present', MeasuringWorth
(data/market/DJIA_MeasuringWorth_daily.csv). Figures: the crash in context and the weekly BSADF date-stamping
(Phillips-Shi-Yu 2015) on the log Dow, 1921-1932, with Monte Carlo and wild bootstrap critical values.
Results saved in case1929.json.
Modelarea Pietelor Financiare - Daniel Traian PELE
"""
import os, sys, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_all_charts as g   # noqa: E402  course style, run_psy, save_fig

CSV = os.path.join(HERE, '..', '..', 'data', 'market', 'DJIA_MeasuringWorth_daily.csv')


def dow():
    d = pd.read_csv(CSV, skiprows=1)
    d['Date'] = pd.to_datetime(d['Date'], format='%m/%d/%Y')
    return d.set_index('Date')['DJIA'].astype(float).loc['1921':'1955']


def d2s(t):
    return None if t is None else pd.Timestamp(t).strftime('%Y-%m-%d')


def facts(s):
    r = 100 * s.pct_change()
    pk = s.loc[:'1930'].idxmax()
    lo = s.loc['1929':'1935'].idxmin()
    after = s.loc[lo:]
    rec = after[after >= s[pk]].index[0]
    two = s.loc[:pk - pd.DateOffset(years=2)].iloc[-1]
    days = {k: dict(close=float(s[k]), ret=float(r[k])) for k in
            ['1929-10-23', '1929-10-24', '1929-10-25', '1929-10-28', '1929-10-29', '1929-10-30', '1929-11-13']}
    nov = s.loc['1929-11'].idxmin()
    a30 = s.loc['1930-01':'1930-06'].idxmax()
    worst = r.loc['1921':'1955'].nsmallest(5)
    return dict(peak=d2s(pk), peak_close=float(s[pk]), runup_2y=float(s[pk] / two - 1),
                runup_1921=float(s[pk] / s.loc['1921-08'].min() - 1), low_1921=float(s.loc['1921-08'].min()),
                low=d2s(lo), low_close=float(s[lo]), fall_to_low=float(s[lo] / s[pk] - 1), recovered=d2s(rec),
                nov_low=d2s(nov), nov_close=float(s[nov]), fall_to_nov=float(s[nov] / s[pk] - 1),
                fall_peak_to_24oct=float(s['1929-10-24'] / s[pk] - 1),
                rally_1930=d2s(a30), rally_1930_close=float(s[a30]), rally_from_nov=float(s[a30] / s[nov] - 1),
                days=days, worst=[dict(date=d2s(k), ret=float(v)) for k, v in worst.items()])


def fig_context(s, f):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.3), gridspec_kw=dict(width_ratios=[1.35, 1]))
    w = s.loc['1927':'1934']
    a1.plot(w.index, w.values, color=g.MainBlue, lw=0.8)
    a1.set_yscale('log')
    a1.set_yticks([40, 60, 100, 150, 200, 300, 400]); a1.set_yticklabels(['40', '60', '100', '150', '200', '300', '400'])
    a1.minorticks_off()
    marks = [(f['peak'], 'Peak 3 Sep 1929\n381.17', (12, -2), 'left'), ('1929-11-13', '13 Nov 1929\n198.69', (-8, -26), 'right'),
             (f['low'], 'Low 8 Jul 1932\n41.22', (-10, 4), 'right')]
    for d, t, off, ha in marks:
        a1.plot(pd.Timestamp(d), s[d], 'o', ms=3.5, color=g.IDAred)
        a1.annotate(t, (pd.Timestamp(d), s[d]), xytext=off, textcoords='offset points', fontsize=7, ha=ha, color=g.Navy)
    a1.set_ylabel('Dow Jones Industrial Average (log scale)')
    a1.set_title('Daily closes, 1927-1934', fontsize=9, loc='left')
    a1.xaxis.set_major_locator(mdates.YearLocator(1)); a1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    r = 100 * s.pct_change().loc['1929-09-03':'1929-11-30']
    cols = [g.IDAred if d in (pd.Timestamp('1929-10-24'), pd.Timestamp('1929-10-28'), pd.Timestamp('1929-10-29'))
            else (g.Teal if v >= 0 else g.MainBlue) for d, v in r.items()]
    a2.bar(r.index, r.values, width=0.8, color=cols)
    a2.axhline(0, color=g.Navy, lw=0.5)
    a2.annotate('Thu 24 Oct: -2.1%', (pd.Timestamp('1929-10-24'), r['1929-10-24']), xytext=(-60, -38), textcoords='offset points',
                fontsize=7, color=g.Navy, arrowprops=dict(arrowstyle='-', color=g.Navy, lw=0.5))
    a2.annotate('28 Oct: -12.8%\n29 Oct: -11.7%', (pd.Timestamp('1929-10-29'), r['1929-10-29']), xytext=(8, -6),
                textcoords='offset points', fontsize=7, color=g.Navy)
    a2.annotate('30 Oct: +12.3%', (pd.Timestamp('1929-10-30'), r['1929-10-30']), xytext=(6, -2), textcoords='offset points',
                fontsize=7, color=g.Navy)
    a2.set_ylabel('Daily change of the close (%)')
    a2.set_title('Daily changes, Sep-Nov 1929', fontsize=9, loc='left')
    a2.xaxis.set_major_locator(mdates.MonthLocator()); a2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.text(0.01, -0.03, 'Source: S. H. Williamson, Daily Closing Value of the Dow Jones Average, MeasuringWorth (2026)',
             fontsize=6.5, color=g.Navy)
    fig.tight_layout()
    g.save_fig('ch17_1929')


def fig_bsadf(y, o):
    r, cv = o['res'], o['cv']
    idx = o['idx']
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.6), sharex=True, gridspec_kw=dict(height_ratios=[1, 1]))
    a1.plot(y.index, np.exp(y.values), color=g.MainBlue, lw=0.8, label='Dow Jones, weekly close (log scale)')
    a1.set_yscale('log'); a1.minorticks_off()
    a1.set_yticks([50, 100, 200, 400]); a1.set_yticklabels(['50', '100', '200', '400'])
    for s0, e0, _ in o['ep']:
        e0 = idx[-1] if e0 is None else e0
        for a in (a1, a2):
            a.axvspan(s0, e0, color=g.Amber if np.exp(y.loc[e0] - y.loc[s0]) > 1 else g.Teal, alpha=0.25, lw=0)
    a1.set_ylabel('Dow (log)')
    a2.plot(idx, r['bsadf'], color=g.MainBlue, lw=0.8, label='BSADF')
    a2.plot(idx, cv['bsadf95'], color=g.IDAred, lw=0.8, ls='--', label='95% critical value, Monte Carlo')
    a2.plot(idx, o['wild']['bsadf95'], color=g.Forest, lw=0.8, ls=':', label='95% critical value, wild bootstrap')
    a2.set_ylabel('Statistic')
    a2.xaxis.set_major_locator(mdates.YearLocator(1)); a2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    a1.set_title(f'Weekly log Dow, 1921-1932: BSADF date-stamping, T = {r["n"]}, minimum window {r["w0"]} weeks, '
                 f'run length {o["L"]} weeks', fontsize=8.5, loc='left')
    h = [plt.Line2D([], [], color=g.MainBlue, lw=0.8), plt.Line2D([], [], color=g.IDAred, lw=0.8, ls='--'),
         plt.Line2D([], [], color=g.Forest, lw=0.8, ls=':'), plt.Rectangle((0, 0), 1, 1, color=g.Amber, alpha=0.25),
         plt.Rectangle((0, 0), 1, 1, color=g.Teal, alpha=0.25)]
    a2.legend(h, ['BSADF (log Dow)', '95% critical value, Monte Carlo', '95% critical value, wild bootstrap',
                  'episode, price rising', 'episode, price falling'], loc='upper center', bbox_to_anchor=(0.5, -0.25),
              ncol=3, frameon=False, fontsize=7)
    g.save_fig('ch17_1929_bsadf')


if __name__ == '__main__':
    s = dow()
    f = facts(s)
    fig_context(s, f)
    wk = np.log(s.loc['1921':'1932'].resample('W-SAT').last().dropna())
    o = g.run_psy(wk, wild=True)
    summ = g.summarise(o, wk)
    fig_bsadf(wk, o)
    out = dict(facts=f, bsadf=summ, source='S. H. Williamson, Daily Closing Value of the Dow Jones Average, MeasuringWorth')
    json.dump(out, open(os.path.join(HERE, 'case1929.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))

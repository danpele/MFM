// Chapter 13 interactive page: one block per chart slide, computed in the browser from ch13_data.js.
(function () {
'use strict';
const D = window.CH13_DATA;
const { LANG, C, sum, solve, mean, sdev, median, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH13_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', navy: '#1F2A44', band: '#C5D2E8' };
const TAB = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2'];
const SEP = LANG === 'ro' ? '; ' : ', ';
const TH = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, LANG === 'ro' ? '\u00a0' : ',');
const ef = (x, d) => x.toFixed(d).replace('-', '−');                    // numbers inside charts: English format
const legendBelow = y => ({ orientation: 'h', x: 0, xanchor: 'left', y: y === undefined ? -0.2 : y, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } });

// ---------------------------------------------------------------- helpers
const DATES = D.spx.dates, CLOSE = D.spx.close, LOGP = CLOSE.map(Math.log);
const RET = LOGP.slice(1).map((v, i) => v - LOGP[i]);                  // daily log returns from the second day
function corr(a, b) {
  const ma = mean(a), mb = mean(b); let sab = 0, saa = 0, sbb = 0;
  for (let i = 0; i < a.length; i++) { const x = a[i] - ma, y = b[i] - mb; sab += x * y; saa += x * x; sbb += y * y; }
  return sab / Math.sqrt(saa * sbb);
}
const lagCorr = (x, l) => corr(x.slice(l), x.slice(0, x.length - l));   // pandas Series.autocorr
function nppf(p) {                                                       // Acklam's rational approximation
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239];
  const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
  const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  const pl = 0.02425;
  if (p < pl) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
  if (p > 1 - pl) return -nppf(1 - p);
  const q = p - 0.5, r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}
function ranks(a) {                                                      // average ranks of ties (scipy rankdata)
  const idx = a.map((_, i) => i).sort((i, j) => a[i] - a[j]), rk = new Array(a.length);
  for (let s = 0; s < idx.length;) { let e = s; while (e + 1 < idx.length && a[idx[e + 1]] === a[idx[s]]) e++; for (let k = s; k <= e; k++) rk[idx[k]] = (s + e) / 2 + 1; s = e + 1; }
  return rk;
}
const spearman = (a, b) => corr(ranks(a), ranks(b));
function auc(y, p) {                                                     // Mann-Whitney, ties counted one half
  const idx = p.map((_, i) => i).sort((i, j) => p[i] - p[j]); let rs = 0, npos = 0;
  for (let s = 0; s < idx.length;) { let e = s; while (e + 1 < idx.length && p[idx[e + 1]] === p[idx[s]]) e++; const r = (s + e) / 2 + 1; for (let k = s; k <= e; k++) if (y[idx[k]]) { rs += r; npos++; } s = e + 1; }
  const nneg = y.length - npos;
  return (rs - npos * (npos + 1) / 2) / (npos * nneg);
}
const sd0 = a => { const m = mean(a); return Math.sqrt(mean(a.map(x => (x - m) ** 2))); };   // numpy std, ddof = 0
const srAnn = (a, q) => Math.sqrt(q) * mean(a) / sdev(a);

// ================================================================= direction vs risk: ACF of r and |r|^p
const SN_PER = { all: ['2000', '2027'], a: ['2000', '2013'], b: ['2013', '2027'] };
function signalNoise() {
  const p = +$('sn-p').value, per = SN_PER[$('sn-per').value];
  $('sn-p-v').textContent = nf(p, 2);
  const pl = p === 1 ? '' : '^' + nf(p, 2);
  const i0 = DATES.findIndex(d => d >= per[0]), i1 = DATES.findIndex(d => d >= per[1]);
  const r = RET.slice(Math.max(i0 - 1, 0), (i1 < 0 ? DATES.length : i1) - 1), a = r.map(v => Math.pow(Math.abs(v), p));
  const lags = range(1, 40, 1), ar = lags.map(l => lagCorr(r, l)), aa = lags.map(l => lagCorr(a, l)), band = 1.96 / Math.sqrt(r.length);
  const lab = p === 1 ? 'Absolute returns |rₜ|' : `|rₜ|^${p}`;
  plot('sn-chart', [
    { x: lags.map(l => l - 0.2), y: ar, type: 'bar', width: 0.4, name: 'Returns rₜ', marker: { color: K.blue }, customdata: lags, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>' },
    { x: lags.map(l => l + 0.2), y: aa, type: 'bar', width: 0.4, name: lab, marker: { color: K.amber }, customdata: lags, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl(`S&P 500 ${DATES[Math.max(i0, 0)].slice(0, 4)}–${DATES[(i1 < 0 ? DATES.length : i1) - 1].slice(0, 4)}: autocorrelation, T = ${r.length}`), legend: legendBelow(-0.2),
    shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: -band, y1: band, fillcolor: K.band, opacity: 0.6, line: { width: 0 }, layer: 'below' }, hline(0, K.navy)],
    xaxis: AX('Lag (days)'), yaxis: AX('Autocorrelation', { range: [-0.15, 0.4] }) }));
  const outR = ar.filter(v => Math.abs(v) > band).length, outA = aa.filter(v => Math.abs(v) > band).length;
  out('sn-out', [T.sn(nf(ar[0], 3), outR, pl, nf(aa[0], 3), nf(aa[39], 3), outA, nf(band, 3))]);
}

// ================================================================= LASSO / ridge path
let laOrder = null;
function lassoPath() {
  const Lp = D.lasso, pen = $('la-pen').value, P = Lp.coef[pen], k = +$('la-k').value, F = Lp.features, lam = Lp.lam;
  if (!laOrder) { const last = Lp.coef.l1[Lp.coef.l1.length - 1]; laOrder = F.map((_, i) => i).sort((i, j) => Math.abs(last[j]) - Math.abs(last[i])); }
  $('la-k-v').textContent = 'λ = ' + (lam[k] >= 10 ? nf(lam[k], 0) : nf(lam[k], 2));
  const tr = laOrder.map((i, j) => ({ x: lam, y: P.map(c => c[i]), mode: 'lines', name: F[i], line: { color: TAB[j], width: 1.6 }, hovertemplate: F[i] + ', λ = %{x:.3g}: %{y:.4f}<extra></extra>' }));
  plot('la-path', tr, layout({ title: ttl((pen === 'l1' ? 'LASSO' : 'Ridge') + '-logistic path, S&P 500 5-day direction'), legend: legendBelow(-0.32),
    shapes: [vline(lam[k], K.red, 'dot'), hline(0, K.navy)],
    xaxis: AX('Penalty λ = 1/C (log scale, stronger to the left)', { type: 'log', autorange: 'reversed' }), yaxis: AX('Standardised coefficient') }));
  const ord = [...laOrder].reverse(), c = P[k];
  plot('la-bar', [{ y: ord.map(i => F[i]), x: ord.map(i => c[i]), type: 'bar', orientation: 'h', marker: { color: ord.map(i => TAB[laOrder.indexOf(i)]) }, hovertemplate: '%{y}: %{x:.4f}<extra></extra>' }],
    layout({ title: ttl('Coefficients at the chosen λ'), showlegend: false, margin: { l: 80, r: 12, t: 30, b: 40 }, xaxis: AX('Standardised coefficient', { range: pen === 'l1' ? [-0.25, 0.25] : null }), yaxis: AX('', { tickfont: { size: 10, color: K.navy } }) }));
  const nz = c.filter(v => Math.abs(v) > 1e-10).length;
  const first = (() => { for (const row of Lp.coef.l1) { const j = row.findIndex(v => Math.abs(v) > 1e-10); if (j >= 0) return F[j]; } return '—'; })();
  const au = Lp.cv_auc[pen], best = Math.max(...au.filter((_, j) => P[j].some(v => Math.abs(v) > 1e-10)));
  out('la-out', [pen === 'l1' ? T.la1(nz, F.length, first) : T.la2(F.length), T.la3(nf(au[k], 3), nf(best, 3))]);
}

// ================================================================= FFD: ADF statistic along d
const ffCache = {};
function ffdWeights(d) { const w = [1]; for (let k = 1; k < 10000; k++) { const v = -w[k - 1] * (d - k + 1) / k; if (Math.abs(v) < 1e-4) break; w.push(v); } return w; }
function ffdSeries(d) {
  if (ffCache[d]) return ffCache[d];
  const w = ffdWeights(d), K1 = w.length, x = LOGP, y = [];
  for (let t = K1 - 1; t < x.length; t++) { let s = 0; for (let k = 0; k < K1; k++) s += w[k] * x[t - k]; y.push(s); }
  return (ffCache[d] = { w, y, i0: K1 - 1 });
}
function ffd() {
  const F = D.ffd, k = +$('ff-k').value, d = F.d[k], aic = $('ff-lag').value === 'aic', S = ffdSeries(d);
  $('ff-k-v').textContent = nf(d, 2);
  const adf = aic ? F.adf_aic : F.adf;
  plot('ff-adf', [
    { x: F.d, y: adf, mode: 'lines+markers', name: aic ? 'ADF statistic, lags chosen by AIC' : 'ADF statistic, 1 lag', line: { color: K.blue, width: 2 }, marker: { size: 6 }, hovertemplate: 'd = %{x:.2f}: %{y:.2f}<extra></extra>' },
    { x: [0, 1], y: [F.crit, F.crit], mode: 'lines', name: '5% critical value', line: { color: K.red, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' },
    { x: F.d, y: F.corr, mode: 'lines+markers', name: 'Corr. with log price', yaxis: 'y2', line: { color: K.green, width: 2 }, marker: { size: 6, symbol: 'square' }, hovertemplate: 'd = %{x:.2f}: corr %{y:.3f}<extra></extra>' },
    { x: [d], y: [adf[k]], mode: 'markers', name: 'Chosen d', marker: { color: K.red, size: 12, line: { color: '#fff', width: 2 } }, hovertemplate: 'd = %{x:.2f}: ADF %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl('S&P 500 log price, 2000–2026: ADF (constant) on the FFD series'), legend: legendBelow(-0.22), margin: { l: 56, r: 56, t: 30, b: 40 },
    shapes: [vline(F.d_star, K.navy, 'dot')], annotations: [{ x: F.d_star, y: 0, yref: 'paper', text: ' d* = ' + ef(F.d_star, 2), showarrow: false, xanchor: 'left', yanchor: 'bottom', font: { size: 11 } }],
    xaxis: AX('Differentiation order d', { range: [-0.02, 1.02] }), yaxis: AX('ADF statistic'),
    yaxis2: AX('Correlation', { overlaying: 'y', side: 'right', range: [-0.05, 1.05], showgrid: false, color: K.green, tickfont: { size: 11, color: K.green } }) }));
  const st = 5, xs = [], ys = [], lp = [];
  for (let j = 0; j < S.y.length; j += st) { xs.push(DATES[S.i0 + j]); ys.push(S.y[j]); lp.push(LOGP[S.i0 + j]); }
  plot('ff-series', [
    { x: xs, y: lp, mode: 'lines', name: 'Log price (d = 0)', line: { color: K.blue, width: 1 }, yaxis: 'y2', hovertemplate: '%{x}: %{y:.3f}<extra></extra>' },
    { x: xs, y: ys, mode: 'lines', name: `FFD series, d = ${ef(d, 2)}`, line: { color: K.green, width: 1.2 }, hovertemplate: '%{x}: %{y:.4f}<extra></extra>' }
  ], layout({ title: ttl(`FFD series: ${S.w.length - 1} lags, sum of the weights ${ef(sum(S.w), 3)}`), legend: legendBelow(-0.15), margin: { l: 56, r: 56, t: 30, b: 40 },
    xaxis: AX('', { type: 'date' }), yaxis: AX('FFD series'), yaxis2: AX('Log price', { overlaying: 'y', side: 'right', showgrid: false }) }));
  out('ff-out', [T.ff(nf(d, 2), S.w.length - 1, nf(sum(S.w), 3), nf(F.corr[k], 2)), T.ff2(nf(F.adf[k], 2), F.adf[k] < F.crit, nf(F.adf_aic[k], 2), F.lags_aic[k], F.adf_aic[k] < F.crit, nf(F.crit, 2))]);
}

// ================================================================= triple barrier
function tripleBarrier() {
  const B = D.tb, pt = +$('tb-w').value, h = +$('tb-h').value, n = B.n, i0 = B.i0;
  $('tb-w-v').textContent = nf(pt, 2); $('tb-h-v').textContent = h;
  const dt = DATES.slice(i0, i0 + n), px = CLOSE.slice(i0, i0 + n), lp = px.map(Math.log), col = { upper: K.green, lower: K.red, vertical: K.amber };
  const shapes = [], tr = [{ x: dt, y: px, mode: 'lines', name: 'S&P 500', line: { color: K.purple, width: 1.2 }, hovertemplate: '%{x}: %{y:.0f}<extra></extra>' }];
  const ev = [], st = { x: [], y: [], c: [], t: [] }, en = { x: [], y: [] };
  for (const e of B.events) {
    if (e + h >= n) continue;
    const w = B.vol[e] * Math.sqrt(h), i1 = e + h; let first = -1, bar = 'vertical';
    for (let t = e + 1; t <= i1; t++) { const m = lp[t] - lp[e]; if (m >= pt * w) { first = t; bar = 'upper'; break; } if (m <= -pt * w) { first = t; bar = 'lower'; break; } }
    const t1 = first < 0 ? i1 : first, lab = bar === 'upper' ? 1 : bar === 'lower' ? -1 : Math.sign(lp[i1] - lp[e]);
    const tv = dt[Math.min(e + h, n - 1)];
    const upB = px[e] * Math.exp(pt * w), dnB = px[e] * Math.exp(-pt * w);
    shapes.push({ type: 'rect', x0: dt[e], x1: tv, y0: dnB, y1: upB, fillcolor: col[bar], opacity: 0.12, line: { width: 0 }, layer: 'below' },
      { type: 'line', x0: dt[e], x1: tv, y0: upB, y1: upB, line: { color: K.green, width: 1.5 } },
      { type: 'line', x0: dt[e], x1: tv, y0: dnB, y1: dnB, line: { color: K.red, width: 1.5 } },
      { type: 'line', x0: tv, x1: tv, y0: dnB, y1: upB, line: { color: K.amber, width: 1.5 } });
    en.x.push(dt[e]); en.y.push(px[e]);
    st.x.push(dt[t1]); st.y.push(px[t1]); st.c.push(col[bar]); st.t.push(lab > 0 ? '+1' : '−1');
    ev.push({ d: dt[e], lab, bar, days: t1 - e });
  }
  const lg = (name, color, dash) => ({ x: [null], y: [null], mode: 'lines', name, line: { color, width: 2, dash } });
  tr.push(lg('Upper barrier (profit-taking)', K.green), lg('Lower barrier (stop-loss)', K.red), lg('Vertical barrier (time limit)', K.amber),
    { x: en.x, y: en.y, mode: 'markers', name: 'Event t₀', marker: { color: K.blue, size: 8 }, hovertemplate: 'entry %{x}: %{y:.0f}<extra></extra>' },
    { x: st.x, y: st.y, mode: 'markers+text', name: 'First touch t₁', text: st.t, textposition: 'top right', textfont: { color: st.c, size: 12 }, marker: { color: st.c, size: 15, symbol: 'star' }, hovertemplate: 'exit %{x}: %{y:.0f}<extra></extra>' });
  plot('tb-chart', tr, layout({ title: ttl(`Triple-barrier labelling: barriers at ±${ef(pt, 2)}·σ√h, h = ${h} trading days`), legend: legendBelow(-0.12), shapes,
    xaxis: AX('', { type: 'date' }), yaxis: AX('Index level') }));
  const cnt = b => ev.filter(e => e.bar === b).length;
  out('tb-out', [T.tb(cnt('upper'), cnt('lower'), cnt('vertical'), ev.filter(e => e.lab > 0).length, ev.length), T.tb2(ev.map(e => T.tbe(e.d, e.lab > 0 ? '+1' : '−1', e.bar, e.days)).join('; '))]);
}

// ================================================================= purged K-fold with embargo (scheme, n = 100)
function purgedScheme() {
  const n = 100, k = +$('pc-k').value, h = +$('pc-h').value, e = +$('pc-e').value;
  $('pc-k-v').textContent = k; $('pc-h-v').textContent = h; $('pc-e-v').textContent = e;
  const t1 = range(0, n - 1, 1).map(i => Math.min(i + h, n - 1)), z = [], stat = [];
  // np.array_split(idx, k): the first n % k folds get one observation more
  const sizes = range(0, k - 1, 1).map(f => Math.floor(n / k) + (f < n % k ? 1 : 0));
  let a = 0;
  for (let f = 0; f < k; f++) {
    const b = a + sizes[f] - 1, Tk = Math.max(...t1.slice(a, b + 1)), row = [], c = [0, 0, 0, 0];
    for (let i = 0; i < n; i++) {
      let v;
      if (i >= a && i <= b) v = 1;
      else if (i < a) v = t1[i] < a ? 0 : 2;                          // purge: label ends inside the test labels
      else if (i <= Tk) v = 2;                                         // purge after the test: label start up to T_k
      else v = i <= Tk + e ? 3 : 0;                                    // embargo: the e observations after the last test label ends
      row.push(v); c[v]++;
    }
    z.push(row); stat.push(c); a = b + 1;
  }
  const cs = [[0, K.blue], [0.25, K.blue], [0.25, K.red], [0.5, K.red], [0.5, K.purple], [0.75, K.purple], [0.75, K.amber], [1, K.amber]];
  const names = ['Train', 'Test', 'Purged (label overlaps test)', 'Embargo (after the last test label)'];
  plot('pc-chart', [
    { z: z.map(r => r.map(v => v + 0.5)), x: range(0, n - 1, 1), y: range(1, k, 1).map(f => 'Fold ' + f), type: 'heatmap', zmin: 0, zmax: 4, colorscale: cs, showscale: false, xgap: 1, ygap: 6,
      customdata: z.map(r => r.map(v => names[v])), hovertemplate: '%{y}, observation %{x}: %{customdata}<extra></extra>' },
    ...names.map((nm, i) => ({ x: [null], y: [null], type: 'bar', name: nm, marker: { color: [K.blue, K.red, K.purple, K.amber][i] } }))
  ], layout({ title: ttl(`${k} contiguous folds, labels of ${h} observations, embargo of ${e}`), legend: legendBelow(-0.2),
    xaxis: AX('Time (observation index)', { range: [-0.5, n - 0.5] }), yaxis: AX('', { autorange: 'reversed' }) }));
  const mid = Math.floor(k / 2), s = stat[mid], tr = mean(stat.map(c => c[0]));
  out('pc-out', [T.pc(mid + 1, s[0], s[1], s[2], s[3]), T.pc2(nf(tr, 1), n)]);
}

// ================================================================= leakage experiment
function leakage() {
  const L = D.leak, k = +$('lk-h').value, h = L.h[k], A = L.acc[String(h)];
  $('lk-h-v').textContent = h;
  const sch = [['shuffled', 'K-Fold (shuffled)', K.red], ['contiguous', 'K-Fold (no shuffle)', K.amber], ['purged', 'Purged K-Fold + embargo', K.green]];
  const xl = ['K-Fold<br>(shuffled)', 'K-Fold<br>(no shuffle)', 'Purged K-Fold<br>+ embargo'], jit = [-0.12, -0.06, 0, 0.06, 0.12];
  plot('lk-bar', [
    { x: [0, 1, 2], y: sch.map(s => mean(A[s[0]])), type: 'bar', width: 0.55, marker: { color: sch.map(s => s[2]), opacity: 0.85 }, showlegend: false, name: 'Mean of 5 folds', customdata: sch.map(s => s[1]), hovertemplate: '%{customdata}: %{y:.1%}<extra></extra>' },
    { x: sch.flatMap((s, i) => A[s[0]].map((_, j) => i + jit[j])), y: sch.flatMap(s => A[s[0]]), mode: 'markers', name: 'Single fold', marker: { color: K.navy, size: 6 }, hovertemplate: 'fold: %{y:.1%}<extra></extra>' }
  ], layout({ title: ttl(`Random walk, ${h}-day labels, ${h}-day rolling-mean noise features`), legend: legendBelow(-0.2), shapes: [hline(0.5, K.navy, 'dash')],
    annotations: sch.map((sc, i) => ({ x: i, y: Math.max(...A[sc[0]]) + 0.035, text: '<b>' + (100 * mean(A[sc[0]])).toFixed(1) + '%</b>', showarrow: false, font: { color: sc[2], size: 12 } })),
    xaxis: AX('', { tickvals: [0, 1, 2], ticktext: xl, range: [-0.5, 2.5] }), yaxis: AX('Out-of-fold accuracy', { tickformat: '.0%', range: [0.35, 1] }) }));
  plot('lk-line', sch.map(s => ({ x: L.h, y: L.h.map(v => mean(L.acc[String(v)][s[0]])), mode: 'lines+markers', name: s[1], line: { color: s[2], width: 2 }, marker: { size: 7 }, hovertemplate: 'h = %{x}: %{y:.1%}<extra></extra>' })),
    layout({ title: ttl('Accuracy against the length h of labels and features'), legend: legendBelow(-0.2), shapes: [vline(h, K.navy, 'dot'), hline(0.5, K.navy, 'dash')],
      xaxis: AX('h (days, log scale)', { type: 'log', tickvals: L.h }), yaxis: AX('Out-of-fold accuracy', { tickformat: '.0%', range: [0.35, 1] }) }));
  out('lk-out', [T.lk(h, pct(mean(A.shuffled), 1), pct(mean(A.contiguous), 1), pct(mean(A.purged), 1))]);
}

// ================================================================= model comparison, purged 5-fold CV
let MC = null;
function mcPre() {
  const M = D.models, y = [...M.y].map(Number), f = [...M.fold].map(Number), P = {};
  M.names.forEach(nm => (P[nm] = M.p[nm].map(v => v / 1e4)));
  const folds = range(0, 4, 1).map(k => f.map((v, i) => (v === k ? i : -1)).filter(i => i >= 0));
  const aucs = {}; M.names.forEach(nm => (aucs[nm] = folds.map(ix => auc(ix.map(i => y[i]), ix.map(i => P[nm][i])))));
  const base = mean(folds.map(ix => { const m = mean(ix.map(i => y[i])); return Math.max(m, 1 - m); }));
  const cs = range(0.40, 0.65, 0.005), curve = M.names.map(s => cs.map(cc => mean(folds.map(ix => mean(ix.map(i => ((P[s][i] > cc ? 1 : 0) === y[i] ? 1 : 0)))))));
  return { y, folds, P, aucs, base, up: mean(y), cs, curve };
}
const MC_COL = [K.blue, K.green, K.amber, K.purple], MC_LAB = ['Logistic<br>(L2)', 'Random<br>Forest', 'Gradient<br>Boosting', 'Neural net<br>(MLP)'];
function modelComparison() {
  if (!MC) MC = mcPre();
  const { y, folds, P, aucs, base, up, cs, curve } = MC, c = +$('mc-c').value, nm = D.models.names;
  $('mc-c-v').textContent = nf(c, 3);
  const accF = s => folds.map(ix => mean(ix.map(i => ((P[s][i] > c ? 1 : 0) === y[i] ? 1 : 0))));
  const acc = nm.map(accF);
  plot('mc-acc', [{ x: MC_LAB, y: acc.map(mean), type: 'bar', width: 0.6, marker: { color: MC_COL, opacity: 0.85 }, error_y: { type: 'data', array: acc.map(sd0), color: K.navy, thickness: 1, width: 4 }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }],
    layout({ title: ttl(`S&P 500, 5-day direction, purged 5-fold CV, threshold ${ef(c, 3)}`), showlegend: false, shapes: [hline(base, K.red, 'dash')],
      annotations: [{ xref: 'paper', x: 0.02, y: 0.98, yref: 'paper', text: 'Dashed: always "up"', showarrow: false, xanchor: 'left', yanchor: 'top', font: { color: K.red, size: 11 } }],
      xaxis: AX('', { tickfont: { size: 10, color: K.navy } }), yaxis: AX('Accuracy', { tickformat: '.0%', range: [0.45, 0.65] }) }));
  plot('mc-auc', [{ x: MC_LAB, y: nm.map(s => mean(aucs[s])), type: 'bar', width: 0.6, marker: { color: MC_COL, opacity: 0.85 }, error_y: { type: 'data', array: nm.map(s => sd0(aucs[s])), color: K.navy, thickness: 1, width: 4 }, hovertemplate: '%{x}: %{y:.3f}<extra></extra>' }],
    layout({ title: ttl('ROC AUC (does not depend on the threshold)'), showlegend: false, shapes: [hline(0.5, K.navy, 'dash')], xaxis: AX('', { tickfont: { size: 10, color: K.navy } }), yaxis: AX('ROC AUC', { range: [0.45, 0.65] }) }));
  plot('mc-thr', [...nm.map((s, j) => ({ x: cs, y: curve[j], mode: 'lines', name: s, line: { color: MC_COL[j], width: 2 }, hovertemplate: s + ', threshold %{x:.3f}: %{y:.1%}<extra></extra>' })),
    { x: [cs[0], cs[cs.length - 1]], y: [base, base], mode: 'lines', name: 'Always "up"', line: { color: K.red, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' }],
    layout({ title: ttl('Fold-mean accuracy against the classification threshold'), legend: legendBelow(-0.2), shapes: [vline(c, K.navy, 'dot')],
      xaxis: AX('Threshold on the predicted probability of "up"'), yaxis: AX('Accuracy', { tickformat: '.0%' }) }));
  const pl = P[nm[0]], tp = y.filter((v, i) => v && pl[i] > c).length, fn = y.filter((v, i) => v && !(pl[i] > c)).length, fp = y.filter((v, i) => !v && pl[i] > c).length, tn = y.length - tp - fn - fp;
  out('mc-out', [T.mc(nm.map((s, j) => s + ' ' + pct(mean(acc[j]), 1)).join(', '), pct(base, 1)), T.mc2(TH(tp), TH(fn), TH(fp), TH(tn), pct((tp + fp) / y.length, 1), pct(up, 1))]);
}

// ================================================================= walk-forward backtest
function walkForward() {
  const W = D.wf, c = +$('wf-c').value, bp = +$('wf-b').value;
  $('wf-c-v').textContent = nf(c, 3); $('wf-b-v').textContent = bp + ' bp';
  const n = W.idx.length, pos = W.p.map(v => (v / 1e4 > c ? 1 : 0)), st = [], bh = [], x = [];
  for (let t = 0; t < n; t++) {
    if (W.ret[t] === null) continue;
    const to = t === 0 ? pos[0] : Math.abs(pos[t] - pos[t - 1]);
    st.push(pos[t] * W.ret[t] - to * bp / 1e4); bh.push(W.ret[t]); x.push(DATES[W.idx[t]]);
  }
  const cum = a => { let s = 0; return a.map(v => Math.exp((s += v))); };
  const sS = srAnn(st, 252), sB = srAnn(bh, 252), ex = mean(pos), sw = pos.slice(1).filter((v, i) => v !== pos[i]).length;
  plot('wf-chart', [
    { x, y: cum(bh), mode: 'lines', name: `Buy & hold (SR = ${sB.toFixed(2)})`, line: { color: K.amber, width: 1.4 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x, y: cum(st), mode: 'lines', name: `GBM long/cash, ${bp} bp costs (SR = ${sS.toFixed(2)})`, line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl(`Walk-forward backtest ${x[0].slice(0, 4)}–${x[x.length - 1].slice(0, 4)}: yearly refit, long if P(up) > ${ef(c, 3)}`), legend: legendBelow(-0.13),
    xaxis: AX('', { type: 'date' }), yaxis: AX('Growth of 1 USD (log scale)', { type: 'log', tickvals: [1, 2, 3, 4, 6, 8] }) }));
  out('wf-out', [T.wf(nf(sS, 2), nf(sB, 2), pct(ex, 0), sw, bp)]);
}

// ================================================================= anomalies and the market (Dong, Li, Rapach & Zhou 2022)
function ncdf(x) {                                                       // Abramowitz-Stegun 7.1.26
  const t = 1 / (1 + 0.3275911 * Math.abs(x) / Math.SQRT2), e = Math.exp(-x * x / 2);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * e;
  return x >= 0 ? 0.5 * (1 + y) : 0.5 * (1 - y);
}
function r2oos(y, f, hm) { let a = 0, b = 0; y.forEach((v, i) => { a += (v - f[i]) ** 2; b += (v - hm[i]) ** 2; }); return 100 * (1 - a / b); }
function clarkWest(y, f, hm) {                                         // HAC (Newey-West, Bartlett), floor(4 (T/100)^(2/9)) lags
  const d = y.map((v, i) => (v - hm[i]) ** 2 - ((v - f[i]) ** 2 - (hm[i] - f[i]) ** 2)), T = d.length, m = mean(d);
  const L = Math.floor(4 * Math.pow(T / 100, 2 / 9)), e = d.map(v => v - m);
  let om = e.reduce((a, v) => a + v * v, 0) / T;
  for (let j = 1; j <= L; j++) { let g = 0; for (let t = j; t < T; t++) g += e[t] * e[t - j]; om += 2 * (1 - j / (L + 1)) * g / T; }
  const t = m / Math.sqrt(om / T);
  return { t, p: 1 - ncdf(t), L };
}
const AN_SET = { all: [0, 15], ff: [0, 7], dec: [7, 15] };
function anomalies() {
  const A = D.dlrz, ye = +$('an-y').value, set = AN_SET[$('an-s').value];
  const n = A.dates.filter(d => d <= ye + '-12').length, sl = a => a.slice(0, n), x = sl(A.dates).map(d => d + '-15');
  $('an-y-v').textContent = `${A.dates[0].slice(0, 4)}–${ye}`;
  const y = sl(A.y), hm = sl(A.hm), cols = range(set[0], set[1] - 1, 1);
  const comb = sl(A.uni).map(r => mean(cols.map(j => r[j]))), cen = sl(A.cenet);
  const gain = f => { let s = 0; return y.map((v, i) => 1e4 * (s += (v - hm[i]) ** 2 - (v - f[i]) ** 2)); };
  const per = `${A.dates[0].slice(0, 4)}-${A.dates[n - 1].slice(0, 4)}`, k = cols.length;
  const rc = r2oos(y, comb, hm), re = r2oos(y, cen, hm), cw = clarkWest(y, comb, hm), cwe = clarkWest(y, cen, hm);
  const lab = { all: 'mean of 15 univariate forecasts', ff: 'mean of the 7 factor forecasts', dec: 'mean of the 8 decile-spread forecasts' }[$('an-s').value];
  const pe = A.dates.indexOf(A.paper_end);
  plot('an-gain', [
    { x, y: gain(comb), mode: 'lines', name: `Comb: ${lab} (R²OOS ${ef(rc, 2)}%, ${per})`, line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x|%b %Y}: %{y:.1f}<extra></extra>' },
    { x, y: gain(cen), mode: 'lines', name: `C-ENet: mean of the forecasts selected by elastic net (R²OOS ${ef(re, 2)}%, ${per})`, line: { color: K.red, width: 1.4 }, hovertemplate: '%{x|%b %Y}: %{y:.1f}<extra></extra>' }
  ], layout({ title: ttl(`Anomaly returns forecasting the market excess return: out-of-sample ${per.replace('-', '–')}`), legend: legendBelow(-0.13),
    shapes: [hline(0, K.navy)].concat(pe >= 0 && pe < n ? [vline(A.paper_end + '-31', K.navy, 'dash')] : []),
    xaxis: AX('', { type: 'date' }), yaxis: AX('Cumulative gain in squared errors (%²)') }));
  const ur = A.names.map((_, j) => r2oos(y, sl(A.uni).map(r => r[j]), hm));
  plot('an-uni', [
    { x: A.names, y: ur, type: 'bar', marker: { color: A.names.map((_, j) => (j >= set[0] && j < set[1] ? (ur[j] > 0 ? K.blue : K.red) : K.band)) }, showlegend: false, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ title: ttl(`Single-anomaly forecasts: R²OOS, ${per.replace('-', '–')}`), shapes: [hline(0, K.navy)],
    xaxis: AX('', { tickangle: -45 }), yaxis: AX('R²OOS (%)') }));
  const all = r2oos(y, sl(A.ols), hm), en = r2oos(y, sl(A.enet), hm), npos = cols.filter(j => ur[j] > 0).length;
  const ns = sl(A.nsel), none = ns.filter(v => v === 0).length / n;
  out('an-out', [T.an(per.replace('-', '–'), k, nf(rc, 2), nf(cw.p, 3), nf(re, 2), nf(cwe.p, 3), nf(en, 2), nf(all, 2)),
                 T.an2(npos, k, pct(none, 0), nf(A.paper['C-ENet'], 2), nf(A.paper.Comb, 2))]);
}

// ================================================================= best of N zero-skill strategies
function expectedMax() {
  const E = D.emax, k = +$('em-k').value, N = E.N[k], sd = Math.sqrt(252 / E.T), s = E.sims[k];
  $('em-k-v').textContent = TH(N);
  const th = n => sd * ((1 - 0.5772156649015329) * nppf(1 - 1 / n) + 0.5772156649015329 * nppf(1 - 1 / (n * Math.E)));
  const grid = range(0, 199, 1).map(i => Math.pow(10, Math.log10(2) + (3 - Math.log10(2)) * i / 199));
  const m = E.sims.map(mean), v = E.sims.map(sdev);
  plot('em-curve', [
    { x: grid, y: grid.map(th), mode: 'lines', name: 'Expected maximum (theory)', line: { color: K.red, width: 2 }, hovertemplate: 'N = %{x:.0f}: %{y:.2f}<extra></extra>' },
    { x: E.N, y: m, mode: 'markers', name: 'Monte Carlo: mean ± SD', marker: { color: K.blue, size: 8 }, error_y: { type: 'data', array: v.map(x => x), color: K.blue, thickness: 1.2, width: 4 }, hovertemplate: 'N = %{x}: %{y:.2f}<extra></extra>' },
    { x: [N], y: [m[k]], mode: 'markers', name: 'Chosen N', marker: { color: K.red, size: 13, symbol: 'diamond', line: { color: '#fff', width: 2 } }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Best Sharpe among zero-skill strategies, 5 years of daily data'), legend: legendBelow(-0.2),
    xaxis: AX('Independent strategies tried, N (log scale)', { type: 'log', tickvals: [1, 10, 100, 1000] }), yaxis: AX('Best annualised SR', { range: [-1.2, 2.2] }) }));
  plot('em-hist', [{ x: s, type: 'histogram', xbins: { start: -1.5, end: 2.5, size: 0.1 }, marker: { color: K.blue, line: { color: '#fff', width: 1 } }, hovertemplate: 'SR %{x}: %{y} samples<extra></extra>' }],
    layout({ title: ttl(`Best SR of ${N} strategies: 200 Monte Carlo samples`), showlegend: false, bargap: 0,
      shapes: N > 1 ? [vline(th(N), K.red), vline(1, K.navy, 'dot')] : [vline(1, K.navy, 'dot')],
      annotations: N > 1 ? [{ x: th(N), y: 1, yref: 'paper', text: 'theory', showarrow: false, xanchor: 'left', yanchor: 'top', font: { color: K.red, size: 11 } }] : [],
      xaxis: AX('Best annualised SR', { range: [-1.5, 2.5] }), yaxis: AX('Samples') }));
  out('em-out', [T.em(TH(N), N > 1 ? nf(th(N), 2) : '0', nf(m[k], 2), nf(v[k], 2), s.filter(x => x > 1).length)]);
}

// ================================================================= BTC grid: in-sample against out-of-sample
function isOos() {
  const G = D.grid, ys = $('io-y').value, q = +$('io-q').value / 100, S = G.splits[ys];
  $('io-q-v').textContent = Math.round(100 * q) + '%'; $('io-y-v').textContent = ys;
  // family fixed in sample: rules with a defined IS Sharpe; an undefined OOS Sharpe (always in cash) counts as 0
  const ix = S.is.map((v, i) => i).filter(i => S.is[i] !== null);
  const a = ix.map(i => S.is[i]), b = ix.map(i => (S.oos[i] === null ? 0 : S.oos[i])), lab = ix.map(i => `MA ${G.fast[i]}/${G.slow[i]}, band ${G.band[i] * 100}%`);
  const ord = a.map((_, j) => j).sort((i, j) => a[j] - a[i]), top = ord.slice(0, Math.floor(ix.length * q)), best = ord[0];
  const lo = Math.min(...a, ...b) - 0.1, hi = Math.max(...a, ...b) + 0.1, rho = spearman(a, b);
  const yEnd = G.end.slice(0, 4), isLab = `May 2015 – ${+ys - 1}`, oosLab = `${ys} – ${yEnd}`;
  plot('io-chart', [
    { x: a, y: b, text: lab, mode: 'markers', name: `${ix.length} configurations`, marker: { color: K.blue, size: 5, opacity: 0.35 }, hovertemplate: '%{text}<br>IS %{x:.2f}, OOS %{y:.2f}<extra></extra>' },
    { x: top.map(j => a[j]), y: top.map(j => b[j]), text: top.map(j => lab[j]), mode: 'markers', name: `Top ${Math.round(100 * q)}% in-sample`, marker: { color: K.amber, size: 6, opacity: 0.8 }, hovertemplate: '%{text}<br>IS %{x:.2f}, OOS %{y:.2f}<extra></extra>' },
    { x: [a[best]], y: [b[best]], text: [lab[best]], mode: 'markers', name: `Best IS: SR IS = ${a[best].toFixed(2)}, SR OOS = ${b[best].toFixed(2)}`, marker: { color: K.red, size: 16, symbol: 'star' }, hovertemplate: '%{text}<br>IS %{x:.2f}, OOS %{y:.2f}<extra></extra>' },
    { x: [lo, hi], y: [lo, hi], mode: 'lines', showlegend: false, line: { color: K.navy, width: 1, dash: 'dot' }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`BTC moving-average crossover grid search (Spearman ρ = ${rho.toFixed(2)})`), legend: legendBelow(-0.2),
    xaxis: AX(`Sharpe in-sample (${isLab})`), yaxis: AX(`Sharpe out-of-sample (${oosLab})`) }));
  const bi = ix[best];
  out('io-out', [T.io(G.fast[bi], G.slow[bi], nf(G.band[bi] * 100, 0), nf(a[best], 2), nf(b[best], 2), nf(rho, 2)), T.io2(Math.round(100 * q), nf(median(top.map(j => b[j])), 2), nf(median(b), 2), +ys, yEnd)]);
}

// ================================================================= VIX: double selection and DML
function vixInference() {
  const V = D.vix, k = +$('vx-l').value, L = V.lags[k], cols = [K.blue, K.amber, K.green, K.purple, K.orange];
  $('vx-l-v').textContent = L;
  const tr = V.names.map((nm, i) => {
    const th = V.theta[i], se = V.se[i][k];
    return { x: [th], y: [nm], mode: 'markers', name: nm, showlegend: false, marker: { color: cols[i], size: 10 }, error_x: { type: 'data', array: [1.96 * se], color: cols[i], thickness: 1.6, width: 6 }, hovertemplate: nm + ': %{x:.1f} bp<extra></extra>' };
  });
  tr.push({ x: V.names.map((_, i) => V.theta[i] + 1.96 * V.se[i][k] + 2), y: V.names, mode: 'text', showlegend: false, hoverinfo: 'skip', textposition: 'middle right', textfont: { size: 10, color: K.navy },
    text: V.names.map((_, i) => `${ef(V.theta[i], 1)} [${ef(V.theta[i] - 1.96 * V.se[i][k], 1)}; ${ef(V.theta[i] + 1.96 * V.se[i][k], 1)}]`) });
  tr.push({ x: [null], y: [null], mode: 'markers', name: 'single LASSO on (VIX, controls): VIX dropped, no standard error', marker: { color: K.red, symbol: 'x', size: 9 } });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'no predictive effect', line: { color: K.navy, dash: 'dash', width: 1.5 } });
  plot('vx-chart', tr, layout({ title: ttl(`Double selection keeps |Ŝ_y| = ${V.ny} and |Ŝ_d| = ${V.nd} controls; HAC with ${L} lags`), legend: legendBelow(-0.2), shapes: [vline(0, K.navy, 'dash')],
    margin: { l: 150, r: 12, t: 30, b: 40 }, xaxis: AX('bp of 5-day S&P 500 log return per SD of log VIX (95% CI)', { range: [-60, 75] }), yaxis: AX('', { autorange: 'reversed' }) }));
  const ci = i => nf(V.theta[i] - 1.96 * V.se[i][k], 1) + SEP + nf(V.theta[i] + 1.96 * V.se[i][k], 1);
  out('vx-out', [T.vx(L, ci(0), ci(2), nf(V.se[2][k] / V.se[0][k], 1)), T.vx2(nf(V.se[2][k], 1), nf(V.se[2][0], 1), V.names.filter((_, i) => V.theta[i] - 1.96 * V.se[i][k] > 0 || V.theta[i] + 1.96 * V.se[i][k] < 0).length)]);
}

// ================================================================= Chen, Pelger & Zhu: tangency benchmarks
const CP_TEST = { paper: ['1992-01', '2016-12'], after: ['2017-01', '9999'], all: ['1992-01', '9999'] };
function tangency(F, dates, y1) {
  const tr = F.filter((_, i) => dates[i] >= '1967-01' && dates[i] <= y1 + '-12'), n = tr.length, p = F[0].length;
  const mu = range(0, p - 1, 1).map(j => mean(tr.map(r => r[j])));
  const S = mu.map((mi, i) => mu.map((mj, j) => sum(tr.map(r => (r[i] - mi) * (r[j] - mj))) / (n - 1)));
  const w = solve(S, mu), s = sum(w.map(Math.abs));
  return w.map(v => v / s);
}
function msr(r) { const s = mean(r) / sdev(r); return { sr: s, se: Math.sqrt((1 + s * s / 2) / r.length), T: r.length }; }
function cpz() {
  const P = D.cpz, y1 = +$('cp-y').value, te = CP_TEST[$('cp-t').value], dt = P.dates;
  $('cp-y-v').textContent = '1967–' + y1;
  const w5 = tangency(P.ff5, dt, y1), w3 = tangency(P.ff3, dt, y1);
  const sel = dt.map((d, i) => i).filter(i => dt[i] >= te[0] && dt[i] <= te[1]);
  const r5 = msr(sel.map(i => P.ff5[i].reduce((s, v, j) => s + v * w5[j], 0))), r3 = msr(sel.map(i => P.ff3[i].reduce((s, v, j) => s + v * w3[j], 0))), rm = msr(sel.map(i => P.ff3[i][0]));
  const labs = ['GAN (deep SDF)', 'EN (linear SDF, elastic net)', 'FFN (return forecast)', 'LS (linear SDF)', 'FF5 tangency', 'FF3 tangency'], keys = ['GAN', 'EN', 'FFN', 'LS', 'FF5', 'FF3'];
  const per = `${dt[sel[0]].slice(0, 4)}–${dt[sel[sel.length - 1]].slice(0, 4)}`;
  plot('cp-sr', [
    { y: labs, x: keys.map(k => P.paper[k]), type: 'bar', orientation: 'h', name: 'Chen, Pelger & Zhu (2024), test 1992–2016', marker: { color: K.blue }, text: keys.map(k => P.paper[k].toFixed(2)), textposition: 'outside', textfont: { color: K.blue, size: 11 }, hovertemplate: '%{y}: %{x:.2f}<extra></extra>' },
    { y: labs.slice(4), x: [r5.sr, r3.sr], type: 'bar', orientation: 'h', name: `Replication: French factors, test ${per} (95% CI)`, marker: { color: K.red },
      error_x: { type: 'data', array: [1.96 * r5.se, 1.96 * r3.se], color: K.navy, thickness: 1, width: 4 }, hovertemplate: '%{y}: %{x:.2f}<extra></extra>' },
    { y: [4.2, 5.2], x: [r5, r3].map(r => r.sr + 1.96 * r.se + 0.015), text: [r5.sr, r3.sr].map(v => v.toFixed(2)), mode: 'text', textposition: 'middle right', textfont: { color: K.red, size: 11 }, showlegend: false, hoverinfo: 'skip', yaxis: 'y2' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Monthly out-of-sample Sharpe ratio of the SDF portfolio'), legend: legendBelow(-0.22), margin: { l: 180, r: 12, t: 30, b: 40 },
    xaxis: AX('Monthly Sharpe ratio', { range: [0, 0.9] }), yaxis: AX('', { autorange: 'reversed' }),
    yaxis2: { overlaying: 'y', type: 'linear', range: [5.5, -0.5], visible: false } }));
  const f5 = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'];
  plot('cp-w', [
    { x: f5, y: w5, type: 'bar', name: 'FF5 tangency', marker: { color: K.blue }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' },
    { x: f5.slice(0, 3), y: w3, type: 'bar', name: 'FF3 tangency', marker: { color: K.green }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl(`Weights estimated on 1967–${y1}, scaled to sum |w| = 1`), legend: legendBelow(-0.15), shapes: [hline(0, K.navy)],
    xaxis: AX(''), yaxis: AX('Weight', { tickformat: '.0%' }) }));
  out('cp-out', [T.cp(y1, per, nf(r5.sr, 2), nf(r5.sr - 1.96 * r5.se, 2), nf(r5.sr + 1.96 * r5.se, 2), nf(r3.sr, 2), nf(r3.sr - 1.96 * r3.se, 2), nf(r3.sr + 1.96 * r3.se, 2), nf(rm.sr, 2), nf(r5.se, 3))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['sn-p', 'sn-per'], signalNoise); P('sn-play', 'sn-p', range(0.25, 3, 0.25), 600);
  on(['la-pen', 'la-k'], lassoPath); P('la-play', 'la-k', range(0, 39, 1), 220);
  on(['ff-k', 'ff-lag'], ffd); P('ff-play', 'ff-k', range(0, 20, 1), 500);
  on(['tb-w', 'tb-h'], tripleBarrier); P('tb-play', 'tb-w', range(0.25, 3, 0.25), 600);
  on(['pc-k', 'pc-h', 'pc-e'], purgedScheme); P('pc-play', 'pc-h', range(0, 15, 1), 450);
  on(['lk-h'], leakage); P('lk-play', 'lk-h', range(0, D.leak.h.length - 1, 1), 900);
  on(['mc-c'], modelComparison); P('mc-play', 'mc-c', range(0.40, 0.65, 0.005), 150);
  on(['wf-c', 'wf-b'], walkForward); P('wf-play', 'wf-c', range(0.45, 0.6, 0.005), 300);
  on(['em-k'], expectedMax); P('em-play', 'em-k', range(0, D.emax.N.length - 1, 1), 700);
  on(['io-y', 'io-q'], isOos); P('io-play', 'io-y', range(2018, 2024, 1), 1000);
  on(['vx-l'], vixInference); P('vx-play', 'vx-l', range(0, D.vix.lags.length - 1, 1), 700);
  on(['an-y', 'an-s'], anomalies); P('an-play', 'an-y', range(1990, +D.dlrz.dates[D.dlrz.dates.length - 1].slice(0, 4), 1), 500);
  on(['cp-y', 'cp-t'], cpz); P('cp-play', 'cp-y', range(1976, 1991, 1), 600);
  const PFX = { 'predictability': 'sn', 'lasso-path': 'la', 'ffd-adf': 'ff', 'triple-barrier': 'tb', 'purged-cv': 'pc', 'leakage': 'lk',
    'model-comparison': 'mc', 'walk-forward': 'wf', 'anomalies': 'an', 'max-sharpe': 'em', 'is-oos': 'io', 'vix': 'vx', 'deep-sdf': 'cp' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  signalNoise(); lassoPath(); ffd(); tripleBarrier(); purgedScheme(); leakage(); modelComparison(); walkForward(); anomalies(); expectedMax(); isOos(); vixInference(); cpz();
}
window.CH13 = { r2oos, clarkWest, ncdf, lagCorr, auc, spearman, ffdWeights, ffdSeries, tangency, msr, nppf };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

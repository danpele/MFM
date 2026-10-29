// Chapter 14 interactive page: one block per chart slide, computed in the browser from ch14_data.js.
// No network is trained here: the forecasts of the LSTM and of the foundation models are the ones saved by the chapter.
(function () {
'use strict';
const D = window.CH14_DATA;
const { C, sum, mean, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH14_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  teal: '#17A2B8', magenta: '#D63384', brown: '#795548', navy: '#1F2A44', band: '#C5D2E8' };
const A = D.assets, LBL = D.labels;

// ---------------------------------------------------------------- statistics
function erfc(x) { const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r; }
const ncdf = x => 0.5 * erfc(-x / Math.SQRT2);
const chi2sf1 = x => (x <= 0 ? 1 : erfc(Math.sqrt(x / 2)));
const nwLags = n => Math.floor(4 * Math.pow(n / 100, 2 / 9));
function nwVar(d, L) {                       // mfm_tsfm.nw_var: Bartlett kernel, autocovariances divided by T
  const n = d.length, m = mean(d), x = d.map(v => v - m), lags = L === undefined ? nwLags(n) : L;
  let v = 0; for (let t = 0; t < n; t++) v += x[t] * x[t]; v /= n;
  for (let j = 1; j <= lags; j++) { let s = 0; for (let t = j; t < n; t++) s += x[t] * x[t - j]; v += 2 * (1 - j / (lags + 1)) * s / n; }
  return v;
}
function dm(la, lb) { const d = la.map((v, i) => v - lb[i]), s = mean(d) / Math.sqrt(nwVar(d) / d.length); return { DM: s, p: 2 * (1 - ncdf(Math.abs(s))) }; }
function kupiec(x, n, p) {
  const ph = x / n, ll0 = (n - x) * Math.log(1 - p) + x * Math.log(p), ll1 = x > 0 && x < n ? (n - x) * Math.log(1 - ph) + x * Math.log(ph) : 0;
  return chi2sf1(-2 * (ll0 - ll1));
}
function lgamma(x) {
  const g = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lgamma(1 - x);
  x -= 1; let a = g[0]; const t = x + 7.5; for (let i = 1; i < 9; i++) a += g[i] / (x + i);
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}
function binomPpf(q, n, p) {                 // scipy.stats.binom.ppf: smallest k with P(X <= k) >= q
  let c = 0; for (let k = 0; k <= n; k++) { c += Math.exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1) + k * Math.log(p) + (n - k) * Math.log(1 - p)); if (c >= q - 1e-12) return k; }
  return n;
}
const qlike = (y, f) => { const r = y / f; return r - Math.log(r) - 1; };
const cfmt = v => (Number.isInteger(v) ? int(v) : nf(v, v < 1 ? 2 : v < 10 ? 2 : 1));
const NM = s => (T.nm && T.nm[s]) || s;
const pv = p => (p < 0.001 ? '<' + nf(0.001, 3) : nf(p, 3));
const sgn = (x, d) => (x > 0 ? '+' : '') + nf(x, d);
const sup = e => '10' + String(e).replace(/-/g, '⁻').replace(/\d/g, c => '⁰¹²³⁴⁵⁶⁷⁸⁹'[c]);
const int = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, window.MFMI.LANG === 'ro' ? '\u202f' : ',');

// ---------------------------------------------------------------- dates
const DAY0 = Date.UTC(2000, 0, 1);
const iso = d => new Date(DAY0 + d * 864e5).toISOString().slice(0, 10);
const undelta = a => { const o = [a[0]]; for (let i = 1; i < a.length; i++) o.push(o[i - 1] + a[i]); return o.map(iso); };
const fd = s => `${s.slice(8, 10)}.${s.slice(5, 7)}.${s.slice(0, 4)}`;
const winLabel = k => (k < D.years.length ? String(D.years[k]) : fd(D.post));
const RV_DATES = undelta(D.rv.ddays);
const RISK_DATES = {}; A.forEach(a => { RISK_DATES[a] = undelta(D.risk[a].ddays); });
const sz = (id, h) => { $(id).style.height = h + 'px'; };
const legendPatch = (name, color, opacity) => ({ x: [null], y: [null], type: 'bar', name, marker: { color, opacity: opacity || 1 }, hoverinfo: 'skip' });

// ================================================================= 1. where the signal is: ACF of r and |r|
function acfOf(v, L) {
  const m = mean(v), x = v.map(a => a - m); let den = 0; for (const a of x) den += a * a;
  const o = []; for (let l = 1; l <= L; l++) { let s = 0; for (let t = l; t < x.length; t++) s += x[t] * x[t - l]; o.push(s / den); }
  return o;
}
function acfBlock() {
  const y0 = +$('ac-y').value, L = +$('ac-L').value, tr = $('ac-s').value;
  $('ac-y-v').textContent = y0; $('ac-L-v').textContent = L;
  const x = D.acf.r.slice(D.acf.ystart[y0]), n = x.length, band = 1.96 / Math.sqrt(n);
  const ar = acfOf(x, L), aa = acfOf(x.map(v => (tr === 'sq' ? v * v : Math.abs(v))), L), lags = range(1, L, 1);
  const nm = tr === 'sq' ? 'Squared returns r²' : 'Absolute returns |r|';
  plot('ac-chart', [
    { x: [0.5, L + 0.5, L + 0.5, 0.5], y: [-band, -band, band, band], fill: 'toself', mode: 'lines', line: { width: 0 }, fillcolor: K.band, name: '95% band under i.i.d.', hoverinfo: 'skip' },
    { x: lags.map(l => l - 0.2), y: ar, type: 'bar', width: 0.4, name: 'Returns r', marker: { color: K.blue }, hovertemplate: 'returns, lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags },
    { x: lags.map(l => l + 0.2), y: aa, type: 'bar', width: 0.4, name: nm, marker: { color: K.red }, hovertemplate: (tr === 'sq' ? 'r²' : '|r|') + ', lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags }
  ], layout({ barmode: 'overlay', title: ttl(`S&P 500 daily returns from ${y0} (${n} days)`), shapes: [hline(0, K.navy)],
    xaxis: AX('Lag (trading days)', { range: [0, L + 1] }), yaxis: AX('Autocorrelation') }));
  const kr = ar.filter(v => Math.abs(v) > band).length, ka = aa.filter(v => Math.abs(v) > band).length;
  out('ac-out', [T.ac1(y0, int(n), nf(band, 3), nf(ar[0], 3), kr, L), T.ac2(tr === 'sq', nf(aa[0], 2), L, nf(aa[L - 1], 2), ka)]);
}

// ================================================================= 2. patching a 512-day context
const PATCH = [2, 4, 8, 16, 32, 64];
function patchBlock() {
  const P = PATCH[+$('pa-p').value], n = +$('pa-n').value, x = D.patch.r.slice(-n), t = range(-n, -1, 1);
  $('pa-p-v').textContent = T.plen(P); $('pa-n-v').textContent = n;
  const shapes = [], ann = [];
  const panel = (Pp, yref, name) => {
    for (let j = 0; j * Pp < n; j++) shapes.push({ type: 'rect', xref: 'x', yref: yref + ' domain', x0: -n + j * Pp - 0.5, x1: Math.min(-n + (j + 1) * Pp, 0) - 0.5, y0: 0, y1: 1,
      fillcolor: j % 2 === 0 ? K.teal : K.amber, opacity: 0.18, line: { width: 0 }, layer: 'below' });
    ann.push({ text: name, xref: 'paper', yref: yref + ' domain', x: 0, y: 1.12, xanchor: 'left', showarrow: false, font: { size: 12, color: K.navy } });
  };
  const k1 = Math.ceil(n / P), k2 = Math.ceil(n / 32);
  panel(P, 'y', (P === 16 ? 'Chronos-2: ' : '') + `${k1} patches of ${P} days`);
  panel(32, 'y2', `TimesFM-2.5: ${k2} patches of 32 days`);
  const cd = (Pp) => t.map((_, i) => Math.floor(i / Pp) + 1);
  plot('pa-chart', [
    { x: t, y: x, mode: 'lines', line: { color: K.blue, width: 1 }, name: `S&P 500 daily return (context of ${n} days)`, customdata: cd(P), hovertemplate: 'day %{x}: %{y:.2f}%, patch %{customdata}<extra></extra>' },
    { x: t, y: x, mode: 'lines', line: { color: K.blue, width: 1 }, xaxis: 'x', yaxis: 'y2', showlegend: false, customdata: cd(32), hovertemplate: 'day %{x}: %{y:.2f}%, patch %{customdata}<extra></extra>' },
    legendPatch('Patch (even)', K.teal, 0.35), legendPatch('Patch (odd)', K.amber, 0.35)
  ], layout({ shapes, annotations: ann, margin: { l: 56, r: 12, t: 34, b: 40 }, legend: { orientation: 'h', x: 0, y: -0.14, yanchor: 'top' },
    xaxis: AX('Day relative to the forecast origin', { range: [-n - 1, 0], anchor: 'y2' }),
    yaxis: AX('Return (%)', { domain: [0.56, 0.94] }), yaxis2: AX('Return (%)', { domain: [0, 0.38] }) }));
  out('pa-out', [T.pa(n, P, k1, int(n * n), int(k1 * k1), int(Math.round(n * n / (k1 * k1)))), T.pa2(k2, int(k2 * k2))]);
}

// ================================================================= 3. Test 1: out-of-sample R^2
function r2Block() {
  const k = +$('r2-w').value, M = D.ret_models;
  $('r2-w-v').textContent = winLabel(k);
  const W = a => D.ret[a].win[k];
  plot('r2-chart', M.map(m => ({
    x: A.map(a => LBL[a]), y: A.map(a => W(a).m[m][0]), type: 'bar', name: D.ret_lbl[m], marker: { color: D.ret_col[m] },
    error_y: { type: 'data', symmetric: false, array: A.map(a => W(a).m[m][2] - W(a).m[m][0]), arrayminus: A.map(a => W(a).m[m][0] - W(a).m[m][1]), color: '#000', thickness: 1, width: 2 },
    customdata: A.map(a => [W(a).m[m][1], W(a).m[m][2], W(a).m[m][4]]),
    hovertemplate: D.ret_lbl[m] + ', %{x}: R² %{y:.2f}%<br>95% CI [%{customdata[0]:.2f}, %{customdata[1]:.2f}]<br>DM p = %{customdata[2]:.3f}<extra></extra>' })),
  layout({ barmode: 'group', bargap: 0.18, title: ttl('95% circular block-bootstrap intervals (20-observation blocks)'), shapes: [hline(0, K.navy)],
    xaxis: AX(''), yaxis: AX('Out-of-sample R² vs zero forecast (%)') }));
  out('r2-out', A.map(a => {
    const w = W(a), best = M.reduce((b, m) => (w.m[m][0] > w.m[b][0] ? m : b), M[0]), tf = w.m.timesfm_point;
    return T.r2(LBL[a], fd(w.start), int(w.n), NM(D.ret_lbl[best]), nf(w.m[best][0], 2), pv(w.m[best][4]), nf(tf[0], 2), pv(tf[4]));
  }));
}

// ================================================================= 4. Test 2: forecasts through the April 2025 shock
const RV_SLIDE = ['logHAR', 'GARCH-t', 'Chronos-2', 'TimesFM-2.5'];
const RV_MONTHS = [...new Set(RV_DATES.map(s => s.slice(0, 7)))];
function rvBlock() {
  const k = +$('rv-t').value, m0 = RV_MONTHS[k], m1 = RV_MONTHS[Math.min(k + 5, RV_MONTHS.length - 1)];
  $('rv-t-v').textContent = m0 + ' – ' + m1;
  const idx = RV_DATES.map((s, i) => i).filter(i => RV_DATES[i].slice(0, 7) >= m0 && RV_DATES[i].slice(0, 7) <= m1);
  const x = idx.map(i => RV_DATES[i]), vol = v => Math.sqrt(252 * v);
  const tr = [{ x, y: idx.map(i => vol(D.rv.RV[i])), mode: 'lines', name: 'Realised volatility (target)', line: { color: K.teal, width: 2.2 }, hovertemplate: 'RV %{x}: %{y:.1f}%<extra></extra>' }];
  D.rv.models.forEach(m => tr.push({ x, y: idx.map(i => vol(D.rv.f[m][i])), mode: 'lines', name: D.rv.lbl[m] + ' forecast', visible: RV_SLIDE.includes(m) ? true : 'legendonly',
    line: { color: D.rv.col[m], width: 1.4 }, hovertemplate: D.rv.lbl[m] + ' %{x}: %{y:.1f}%<extra></extra>' }));
  plot('rv-chart', tr, layout({ title: ttl('SPY realised volatility and one-day-ahead forecasts, annualised'), xaxis: AX('', { type: 'date' }), yaxis: AX('Volatility (% p.a.)'), hovermode: 'x unified' }));
  const pk = idx.reduce((b, i) => (D.rv.RV[i] > D.rv.RV[b] ? i : b), idx[0]);
  const q = m => mean(idx.map(i => qlike(D.rv.RV[i], D.rv.f[m][i])));
  const best = D.rv.models.reduce((b, m) => (q(m) < q(b) ? m : b), D.rv.models[0]);
  out('rv-out', [T.rv1(fd(RV_DATES[idx[0]]), fd(RV_DATES[idx[idx.length - 1]]), idx.length, nf(vol(D.rv.RV[pk]), 0), fd(RV_DATES[pk])),
    T.rv2(NM(D.rv.lbl[best]), nf(q(best), 3), nf(q('logHAR'), 3), nf(q('Chronos-2'), 3))]);
}

// ================================================================= 5. Test 2: QLIKE losses of eight models
function qlBlock() {
  const s = +$('ql-s').value, loss = $('ql-l').value, M = D.rv.models, n = D.rv.RV.length, i1 = RV_DATES.findIndex(d => d >= D.post);
  $('ql-s-v').textContent = fd(RV_DATES[s]);
  const L = m => D.rv.RV.map((y, i) => (loss === 'qlike' ? qlike(y, D.rv.f[m][i]) : (y - D.rv.f[m][i]) ** 2));
  const LL = {}; M.forEach(m => { LL[m] = L(m); });
  const bars = (id, a, b, title) => {
    const v = M.map(m => mean(LL[m].slice(a, b)));
    plot(id, [{ y: M.map(m => D.rv.lbl[m]), x: v, type: 'bar', orientation: 'h', marker: { color: M.map(m => D.rv.col[m]) }, text: v.map(z => z.toFixed(3)), textposition: 'outside', cliponaxis: false,
      textfont: { color: '#000', size: 10 }, hovertemplate: '%{y}: %{x:.4f}<extra></extra>' }],
    layout({ showlegend: false, title: ttl(title), margin: { l: 90, r: 40, t: 30, b: 44 }, xaxis: AX(loss === 'qlike' ? 'Mean QLIKE loss (lower is better)' : 'Mean squared error (%², lower is better)', { range: [0, Math.max(...v) * 1.22] }), yaxis: AX('') }));
    return v;
  };
  const v = bars('ql-full', s, n, s === 0 ? `Full test period (${n} days)` : `From ${RV_DATES[s]} (${n - s} days)`);
  bars('ql-post', i1, n, `After 3 Nov 2025 (${n - i1} days)`);
  const best = M[v.indexOf(Math.min(...v))], t = dm(LL['Chronos-2'].slice(s), LL.logHAR.slice(s));
  out('ql-out', [T.ql1(loss === 'qlike' ? 'QLIKE' : 'MSE', fd(RV_DATES[s]), n - s, NM(D.rv.lbl[best]), nf(Math.min(...v), 3), nf(v[M.indexOf('logHAR')], 3), nf(v[M.indexOf('Chronos-2')], 3)),
    T.ql2(sgn(t.DM, 2), pv(t.p))]);
}

// ================================================================= 6. Test 3: VaR 1% breach rates
const BR_MODELS = D.risk_models.concat(['bolt-raw']);
const brLbl = m => (m === 'bolt-raw' ? 'Chronos-Bolt: 10% endpoint' : D.risk_lbl[m]);
const countHits = (s, a, b) => { let c = 0; for (let i = a; i < b; i++) c += s.charCodeAt(i) === 49; return c; };
function brBlock() {
  const k = +$('br-w').value; $('br-w-v').textContent = winLabel(k);
  const R = a => { const e = D.risk[a], i0 = e.starts[k], n = e.n - i0; return { i0, n, x: m => countHits(e.hits[m], i0, e.n) }; };
  const shapes = [hline(1, K.navy, 'dash')], tr = [];
  A.forEach((a, i) => { const r = R(a), lo = binomPpf(0.025, r.n, 0.01) / r.n * 100, hi = binomPpf(0.975, r.n, 0.01) / r.n * 100;
    shapes.push({ type: 'rect', xref: 'x', yref: 'y', x0: i - 0.45, x1: i + 0.45, y0: Math.max(lo, 0.05), y1: hi, fillcolor: K.band, opacity: 0.8, line: { width: 0 }, layer: 'below' }); });
  tr.push(legendPatch('95% range of the breach rate under a correct model', K.band, 0.8));
  const w = 0.11, nm = BR_MODELS.length;
  BR_MODELS.forEach((m, j) => tr.push({ x: A.map((a, i) => i + (j - (nm - 1) / 2) * w), y: A.map(a => { const r = R(a); return 100 * r.x(m) / r.n; }), width: w, type: 'bar', name: brLbl(m), marker: { color: D.risk_col[m] },
    customdata: A.map(a => { const r = R(a); return [LBL[a], r.x(m), r.n]; }), hovertemplate: brLbl(m) + ', %{customdata[0]}: %{y:.2f}% (%{customdata[1]} of %{customdata[2]} days)<extra></extra>' }));
  plot('br-chart', tr, layout({ barmode: 'overlay', shapes, title: ttl('Evaluation from ' + (k < D.years.length ? D.years[k] : '3 Nov 2025')),
    xaxis: AX('', { tickvals: [0, 1, 2], ticktext: A.map(a => LBL[a]), range: [-0.55, 2.55] }),
    yaxis: AX('Breach rate of VaR 1% (%)', { type: 'log', tickvals: [0.5, 1, 2, 5, 10], ticktext: ['0.5', '1', '2', '5', '10'], range: [Math.log10(0.3), Math.log10(20)] }) }));
  out('br-out', A.map(a => { const r = R(a), lo = binomPpf(0.025, r.n, 0.01), hi = binomPpf(0.975, r.n, 0.01), c2 = r.x('C2-raw'), f = r.x('FHS'), h = r.x('C2-FHS');
    return T.br(LBL[a], int(r.n), pct(c2 / r.n, 2), pv(kupiec(c2, r.n, 0.01)), pct(f / r.n, 2), pct(h / r.n, 2), lo, hi); }));
}

// ================================================================= 7. the COVID-19 crash: VaR 1% of three models
const VP_SLIDE = ['FHS', 'C2-raw', 'C2-FHS'];
const SP = D.risk.sp500, SP_D = RISK_DATES.sp500, SP_MONTHS = [...new Set(SP_D.map(s => s.slice(0, 7)))];
const spVar = m => (m === 'C2-raw' ? SP.q1.map(v => -v) : SP.var[m]);
function vpBlock() {
  const k = +$('vp-t').value, m0 = SP_MONTHS[k], m1 = SP_MONTHS[Math.min(k + 4, SP_MONTHS.length - 1)];
  $('vp-t-v').textContent = m0 + ' – ' + m1;
  const idx = SP_D.map((s, i) => i).filter(i => SP_D[i].slice(0, 7) >= m0 && SP_D[i].slice(0, 7) <= m1), x = idx.map(i => SP_D[i]);
  const L = idx.map(i => -SP.y[i]);
  const tr = [{ x, y: L.map(v => Math.max(v, 0)), type: 'bar', name: 'Daily loss (gains set to 0)', marker: { color: K.teal, opacity: 0.7 }, hovertemplate: 'loss %{x}: %{y:.2f}%<extra></extra>' }];
  D.risk_models.forEach(m => {
    const v = spVar(m), vis = VP_SLIDE.includes(m) ? true : 'legendonly', hit = idx.filter(i => SP.hits[m][i] === '1');
    tr.push({ x, y: idx.map(i => v[i]), mode: 'lines', name: 'VaR 1%: ' + D.risk_lbl[m], legendgroup: m, visible: vis, line: { color: D.risk_col[m], width: 1.6 }, hovertemplate: D.risk_lbl[m] + ' %{x}: %{y:.2f}%<extra></extra>' });
    tr.push({ x: hit.map(i => SP_D[i]), y: hit.map(i => -SP.y[i]), mode: 'markers', legendgroup: m, showlegend: false, visible: vis, marker: { color: D.risk_col[m], size: 8 }, hovertemplate: 'breach of ' + D.risk_lbl[m] + ' %{x}: loss %{y:.2f}%<extra></extra>' });
  });
  plot('vp-chart', tr, layout({ title: ttl(`S&P 500, ${m0} to ${m1} (${idx.length} days)`), bargap: 0, xaxis: AX('', { type: 'date' }), yaxis: AX('Loss (%)') }));
  const cnt = m => idx.filter(i => SP.hits[m][i] === '1').length, h = spVar('C2-FHS'), f = spVar('FHS');
  const ih = idx.reduce((b, i) => (h[i] > h[b] ? i : b), idx[0]), mf = Math.max(...idx.map(i => f[i])), ml = Math.max(...L);
  out('vp-out', [T.vp1(idx.length, cnt('FHS'), cnt('C2-raw'), cnt('C2-FHS'), cnt('HS')), T.vp2(nf(h[ih], 1), fd(SP_D[ih]), nf(mf, 1), nf(ml, 1))]);
}

// ================================================================= 8. PIT and calibration
const PIT_MODELS = [['C2', 'Chronos-2 quantiles', K.red], ['FHS', 'FHS (GARCH-t filter)', K.green], ['GARCH-t', 'GARCH-t', K.blue]];
function pitBlock() {
  const k = +$('pi-w').value, LV = D.pit_lv, edges = [0, ...LV, 1], wd = edges.slice(1).map((e, i) => e - edges[i]);
  $('pi-w-v').textContent = winLabel(k);
  const lines = [];
  A.forEach((a, j) => {
    const P = D.pit[a], i0 = P.starts[k], n = P.C2.length - i0, res = {};
    const tr = PIT_MODELS.map(([nm, lab, col]) => {
      const c = new Array(LV.length + 1).fill(0); for (let i = i0; i < P[nm].length; i++) c[P[nm].charCodeAt(i) - 97]++;
      const dens = c.map((v, b) => v / (n * wd[b])); res[nm] = c[0] / n;
      return { x: edges, y: [...dens, dens[dens.length - 1]], mode: 'lines', line: { shape: 'hv', color: col, width: 1.8 }, name: lab, showlegend: j === 0,
        customdata: [...c, c[c.length - 1]], hovertemplate: lab + '<br>from u = %{x}: %{y:.2f} (%{customdata} days)<extra></extra>' };
    });
    plot('pi-' + a, tr, layout({ title: ttl(LBL[a] + ` (${n} days)`), shapes: [hline(1, K.navy, 'dash')], margin: { l: 56, r: 12, t: 30, b: 120, autoexpand: false }, legend: { orientation: 'h', x: 0, y: -0.2, yanchor: 'top' },
      xaxis: AX('PIT u = F̂(r)', { range: [-0.03, 1.03] }), yaxis: AX(j === 0 ? 'Observed / expected frequency' : '', { range: [0, 2] }) }));
    lines.push(T.pi(LBL[a], pct(res.C2, 2), pct(res.FHS, 2), pct(res['GARCH-t'], 2)));
  });
  out('pi-out', lines);
}

// ================================================================= 9. MCS of the (VaR 2.5%, ES 2.5%) forecasts
const PV_SCALE = [[0, K.red], [0.25, '#F4B6B6'], [0.5, '#FFFFFF'], [0.75, '#BFD8BF'], [1, K.green]];
function mcsBlock() {
  const k = +$('mc-w').value, lev = +$('mc-a').value, Mo = D.risk_models;
  $('mc-w-v').textContent = winLabel(k);
  const P = A.map(a => D.risk[a].mcs[k]);
  const z = Mo.map(m => P.map(w => Math.log10(Math.min(Math.max(w.p[m], 1e-4), 1))));
  const txt = Mo.map(m => P.map(w => (w.p[m] < 0.001 ? '<0.001' : w.p[m].toFixed(3)) + (w.p[m] < 1 - lev ? ' ×' : '')));
  plot('mc-chart', [{ type: 'heatmap', x: A.map(a => LBL[a]), y: Mo.map(m => D.risk_lbl[m]), z, zmin: -4, zmax: 0, colorscale: PV_SCALE, showscale: false, text: txt, texttemplate: '%{text}', textfont: { color: '#000', size: 12 },
    customdata: Mo.map(m => P.map(w => [w.fz0[m], w.n])), hovertemplate: '%{y}, %{x}: MCS p = %{text}<br>mean FZ0 %{customdata[0]:.4f} over %{customdata[1]} days<extra></extra>', xgap: 2, ygap: 2 }],
  layout({ title: ttl(`MCS p-values for FZ0, ${Math.round(100 * lev)}% set; × = eliminated`), margin: { l: 170, r: 12, t: 30, b: 30 }, xaxis: AX('', { side: 'bottom' }), yaxis: AX('', { autorange: 'reversed' }) }));
  const elim = []; Mo.forEach(m => A.forEach((a, j) => { if (P[j].p[m] < 1 - lev) elim.push(`${NM(D.risk_lbl[m])} (${LBL[a]}, p = ${pv(P[j].p[m])})`); }));
  const sp = P[0], low = Mo.reduce((b, m) => (sp.fz0[m] < sp.fz0[b] ? m : b), Mo[0]), h = sp.dm['C2-FHS'];
  out('mc-out', [T.mc1(Math.round(100 * lev), elim.length ? elim.join('; ') : T.none), T.mc2(NM(D.risk_lbl[low]), nf(sp.fz0[low], 3), sgn(h[0], 2), pv(h[1]))]);
}

// ================================================================= 10. adaptive conformal VaR 1%
const GAMMAS = [0, 0.0005, 0.001, 0.002, 0.003, 0.005];
function aci(y, q, alpha, gamma, nCal) {     // inference_tests.aci (Gibbs & Candes, 2021), published boundary rule
  const n = y.length, E = y.map((v, i) => q[i] - v), shift = new Array(n).fill(NaN), al = new Array(n).fill(NaN);
  let at = alpha;
  for (let t = nCal; t < n; t++) {
    const cal = E.slice(t - nCal, t).sort((a, b) => a - b), k = Math.ceil((1 - at) * (nCal + 1));
    const Qh = at <= 0 || k > nCal ? Infinity : at >= 1 || k < 1 ? -Infinity : cal[k - 1];
    shift[t] = Qh; al[t] = at;
    const err = y[t] < q[t] - Qh ? 1 : 0;
    at += gamma * (alpha - err);
  }
  return { shift, al };
}
function cfBlock() {
  const a = $('cf-a').value, g = GAMMAS[+$('cf-g').value], nCal = +$('cf-n').value, R = D.risk[a], dd = RISK_DATES[a];
  $('cf-g-v').textContent = g === 0 ? '0 (split conformal)' : String(g);
  const { shift, al } = aci(R.y, R.q1, 0.01, g, nCal), keep = range(nCal, R.y.length - 1, 1), x = keep.map(i => dd[i]);
  const vA = keep.map(i => -(R.q1[i] - shift[i])), vR = keep.map(i => -R.q1[i]), vF = keep.map(i => R.fhs[i]), L = keep.map(i => -R.y[i]);
  const fin = v => (Number.isFinite(v) ? v : null);
  plot('cf-chart', [
    { x, y: keep.map(i => 100 * al[i]), mode: 'lines', line: { color: K.purple, width: 1.2 }, name: 'Adaptive level α_t (target 1%)', hovertemplate: 'α_t %{x}: %{y:.3f}%<extra></extra>' },
    { x, y: vR, mode: 'lines', yaxis: 'y2', line: { color: K.red, width: 1 }, name: 'Chronos-2 direct quantile', hovertemplate: 'Chronos-2 %{x}: %{y:.2f}%<extra></extra>' },
    { x, y: vA.map(fin), mode: 'lines', yaxis: 'y2', line: { color: K.orange, width: 1 }, name: 'Chronos-2 + adaptive conformal', hovertemplate: 'ACI %{x}: %{y:.2f}%<extra></extra>' },
    { x, y: vF, mode: 'lines', yaxis: 'y2', line: { color: K.green, width: 1 }, name: 'FHS', hovertemplate: 'FHS %{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ title: ttl(`${LBL[a]}: γ = ${g}, ${nCal} calibration days`), shapes: [hline(1, K.navy, 'dash')], margin: { l: 56, r: 12, t: 30, b: 40 },
    legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top' },
    xaxis: AX('', { type: 'date', anchor: 'y2' }), yaxis: AX('α_t (%)', { domain: [0.64, 1] }),
    yaxis2: AX('VaR 1% (%)', { domain: [0, 0.56], type: 'log', tickvals: [0.5, 1, 2, 5, 10, 20, 50], ticktext: ['0.5', '1', '2', '5', '10', '20', '50'] }) }));
  const xA = keep.filter((i, j) => L[j] > vA[j]).length, xF = keep.filter((i, j) => L[j] > vF[j]).length, nInf = vA.filter(v => !Number.isFinite(v)).length;
  const mA = mean(vA.filter(Number.isFinite)), mF = mean(vF);
  out('cf-out', [T.cf1(int(keep.length), fd(dd[nCal]), xA, nf(0.01 * keep.length, 1), pct(xA / keep.length, 2), xF), T.cf2(nf(mA, 2), nf(mF, 2), nInf)]);
}

// ================================================================= 11. complexity on course data
const KZ_SLIDE = { '-3': K.red, '-1': K.orange, '1': K.green, '3': K.blue };
function kzBlock() {
  const Z = D.kmz, ze = String(+$('kz-z').value), ci = +$('kz-c').value, view = $('kz-v').value, c = Z.c;
  $('kz-z-v').textContent = sup(ze); $('kz-c-v').textContent = cfmt(c[ci]);
  const keys = ['-3', '-1', '1', '3'].concat(KZ_SLIDE[ze] ? [] : [ze]).sort((a, b) => +a - +b);
  const col = e => KZ_SLIDE[e] || K.teal, wd = e => (e === ze ? 2.6 : 1.4);
  const left = keys.map(e => ({ x: c, y: view === 'r2' ? Z.curve[e].r2 : Z.curve[e].bn, mode: 'lines+markers', marker: { size: 5 }, name: 'z = ' + sup(e), legendgroup: e, line: { color: col(e), width: wd(e) },
    hovertemplate: 'z = ' + sup(e) + ', c = %{x}: ' + (view === 'r2' ? 'R² %{y:.1f}%' : '‖β̂‖² %{y:.3g}') + '<extra></extra>' }));
  const right = keys.map(e => ({ x: c, y: Z.curve[e].sr, mode: 'lines+markers', marker: { size: 5 }, name: 'z = ' + sup(e), legendgroup: e, showlegend: false, line: { color: col(e), width: wd(e) },
    hovertemplate: 'z = ' + sup(e) + ', c = %{x}: Sharpe %{y:.3f}<extra></extra>' }));
  right.push({ x: [c[0], c[c.length - 1]], y: [Z.lin_sr, Z.lin_sr], mode: 'lines', line: { color: K.purple, dash: 'dot', width: 1.6 }, name: 'Linear, 7 predictors, z = 10³', hovertemplate: 'linear: %{y:.3f}<extra></extra>' });
  const cur = [{ x: [c[ci]], y: [view === 'r2' ? Z.curve[ze].r2[ci] : Z.curve[ze].bn[ci]], mode: 'markers', marker: { size: 11, color: col(ze), line: { color: K.navy, width: 1.5 } }, showlegend: false, hoverinfo: 'skip' }];
  const sh = [vline(1, K.navy, 'dash'), vline(c[ci], K.navy, 'dot')];
  const xa = AX('Complexity c = P/T (log scale)', { type: 'log' }), mg = { l: 60, r: 12, t: 30, b: 110, autoexpand: false }, lg = { orientation: 'h', x: 0, y: -0.2, yanchor: 'top' };
  plot('kz-r2', left.concat(cur), layout({ margin: mg, legend: lg, title: ttl(view === 'r2' ? 'Out-of-sample R² (clipped at −60%)' : 'Mean ‖β̂‖² of the ridge estimate'), shapes: sh.concat(view === 'r2' ? [hline(0, K.navy)] : []), xaxis: xa,
    yaxis: view === 'r2' ? AX('Out-of-sample R² (%)', { range: [-60, 5] }) : AX('‖β̂‖² (log scale)', { type: 'log' }) }));
  plot('kz-sr', right.concat([{ x: [c[ci]], y: [Z.curve[ze].sr[ci]], mode: 'markers', marker: { size: 11, color: col(ze), line: { color: K.navy, width: 1.5 } }, showlegend: false, hoverinfo: 'skip' }]),
    layout({ margin: mg, legend: lg, title: ttl('Sharpe ratio of the timing strategy'), shapes: sh.concat([hline(0, K.navy)]), xaxis: xa, yaxis: AX('Annualised Sharpe ratio') }));
  const sr = Z.curve[ze].sr, jb = sr.indexOf(Math.max(...sr));
  out('kz-out', [T.kz1(cfmt(c[ci]), sup(ze), nf(Z.curve[ze].r2[ci], 1), nf(sr[ci], 2), nf(Z.lin_sr, 2)), T.kz2(sup(ze), nf(sr[jb], 2), cfmt(c[jb]))]);
}

// ================================================================= 12. a test without power
function lrv(x, L) { const m = mean(x), d = x.map(v => v - m), n = d.length; let s = 0; for (const v of d) s += v * v; s /= n;
  for (let l = 1; l <= L; l++) { let g = 0; for (let t = l; t < n; t++) g += d[t] * d[t - l]; s += 2 * (1 - l / (L + 1)) * g / n; } return s; }
function prepost(d, b) {                     // ai_discovery_case.py: d on [1, post], HAC (Bartlett) covariance
  const n = d.length, lags = nwLags(n), pre = d.slice(0, b), post = d.slice(b), m0 = mean(pre), m1 = mean(post), beta = m1 - m0;
  const u = d.map((v, i) => v - (i < b ? m0 : m1)), g = d.map((_, i) => [u[i], i < b ? 0 : u[i]]);
  const S = [[0, 0], [0, 0]];
  for (let i = 0; i < n; i++) { S[0][0] += g[i][0] * g[i][0] / n; S[0][1] += g[i][0] * g[i][1] / n; S[1][1] += g[i][1] * g[i][1] / n; }
  for (let l = 1; l <= lags; l++) { const w = 1 - l / (lags + 1); let a00 = 0, a01 = 0, a10 = 0, a11 = 0;
    for (let t = l; t < n; t++) { a00 += g[t][0] * g[t - l][0]; a01 += g[t][0] * g[t - l][1]; a10 += g[t][1] * g[t - l][0]; a11 += g[t][1] * g[t - l][1]; }
    S[0][0] += w * 2 * a00 / n; S[0][1] += w * (a01 + a10) / n; S[1][1] += w * 2 * a11 / n; }
  S[1][0] = S[0][1];
  const np1 = (n - b) / n, XX = [[1, np1], [np1, np1]], det = XX[0][0] * XX[1][1] - XX[0][1] * XX[1][0], Zi = [[XX[1][1] / det, -XX[0][1] / det], [-XX[1][0] / det, XX[0][0] / det]];
  const ZS = [[Zi[1][0] * S[0][0] + Zi[1][1] * S[1][0], Zi[1][0] * S[0][1] + Zi[1][1] * S[1][1]]];
  const v11 = (ZS[0][0] * Zi[0][1] + ZS[0][1] * Zi[1][1]) / n, se = Math.sqrt(v11), t = beta / se;
  const zq = 1.959963984540054 + 0.8416212335729143;
  return { n, b, m0, m1, beta, se, t, p: 2 * (1 - ncdf(Math.abs(t))), mde: zq * se, s0: Math.sqrt(lrv(pre, lags) / pre.length), s1: Math.sqrt(lrv(post, lags) / post.length) };
}
function aiBlock() {
  const m = $('ai-m').value, b = +$('ai-b').value, rv = D.rv.RV;
  $('ai-b-v').textContent = fd(RV_DATES[b]);
  const d = rv.map((y, i) => qlike(y, D.rv.f[m][i]) - qlike(y, D.rv.f.logHAR[i])), R = prepost(d, b);
  const rows = [[`Before ${RV_DATES[b]} (${R.b} days)`, R.m0, R.s0, K.green], [`After ${RV_DATES[b]} (${R.n - R.b} days)`, R.m1, R.s1, K.orange], ['Change β̂₁ (after minus before)', R.beta, R.se, K.blue]];
  const tr = rows.map(([lab, mu, se, col]) => ({ x: [mu - 1.96 * se, mu + 1.96 * se], y: [lab, lab], mode: 'lines', line: { color: col, width: 7 }, showlegend: false, hoverinfo: 'skip' }));
  tr.push({ x: rows.map(r => r[1]), y: rows.map(r => r[0]), mode: 'markers', marker: { size: 13, color: rows.map(r => r[3]) }, showlegend: false, customdata: rows.map(r => [r[1] - 1.96 * r[2], r[1] + 1.96 * r[2]]),
    hovertemplate: '%{y}: %{x:.4f}<br>95% HAC interval [%{customdata[0]:.4f}, %{customdata[1]:.4f}]<extra></extra>' });
  tr.push({ x: [-R.mde, R.mde], y: [rows[2][0], rows[2][0]], mode: 'markers', marker: { symbol: 'line-ns', size: 30, line: { color: K.red, width: 3 }, color: K.red }, name: '±MDE of β₁ (80% power)', hovertemplate: 'MDE ±%{x:.4f}<extra></extra>' });
  tr.push({ x: [null], y: [null], mode: 'lines', line: { color: '#000', width: 7 }, name: 'HAC 95% interval' });
  const lim = Math.max(R.mde, ...rows.map(r => Math.abs(r[1]) + 1.96 * r[2])) * 1.12;
  plot('ai-chart', tr, layout({ title: ttl(`Mean QLIKE differential d_t (${D.rv.lbl[m]} minus log-HAR)`), shapes: [vline(0, K.navy, 'dash')], margin: { l: 230, r: 16, t: 30, b: 44 },
    xaxis: AX('Mean QLIKE differential d_t', { range: [-lim, lim], zeroline: false }), yaxis: AX('', { autorange: 'reversed' }) }));
  out('ai-out', [T.ai1(fd(RV_DATES[b]), R.b, R.n - R.b, sgn(R.m0, 4), sgn(R.m1, 4)), T.ai2(sgn(R.beta, 4), nf(R.t, 2), nf(R.p, 2), nf(R.mde, 4))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  on(['ac-y', 'ac-L', 'ac-s'], acfBlock); P('ac-play', 'ac-L', range(10, 250, 10), 350);
  sz('pa-chart', 440); on(['pa-p', 'pa-n'], patchBlock); P('pa-play', 'pa-p', range(0, PATCH.length - 1, 1), 1100);
  sz('r2-chart', 420); $('r2-w').max = D.years.length; on(['r2-w'], r2Block); P('r2-play', 'r2-w', range(0, D.years.length, 1), 900);
  $('rv-t').max = RV_MONTHS.length - 6; $('rv-t').value = RV_MONTHS.indexOf('2025-02'); on(['rv-t'], rvBlock); P('rv-play', 'rv-t', range(0, RV_MONTHS.length - 6, 1), 500);
  sz('ql-full', 380); sz('ql-post', 380);
  $('ql-s').max = D.rv.RV.length - 120; on(['ql-s', 'ql-l'], qlBlock); P('ql-play', 'ql-s', range(0, D.rv.RV.length - 120, 21), 350);
  sz('br-chart', 420); $('br-w').max = D.years.length; on(['br-w'], brBlock); P('br-play', 'br-w', range(0, D.years.length, 1), 900);
  $('vp-t').max = SP_MONTHS.length - 5; $('vp-t').value = SP_MONTHS.indexOf('2020-02'); on(['vp-t'], vpBlock); P('vp-play', 'vp-t', range(0, SP_MONTHS.length - 5, 1), 450);
  $('pi-w').max = D.years.length; on(['pi-w'], pitBlock); P('pi-play', 'pi-w', range(0, D.years.length, 1), 900);
  $('mc-w').max = D.years.length; on(['mc-w', 'mc-a'], mcsBlock); P('mc-play', 'mc-w', range(0, D.years.length, 1), 900);
  sz('cf-chart', 460); on(['cf-a', 'cf-g', 'cf-n'], cfBlock); P('cf-play', 'cf-g', range(0, GAMMAS.length - 1, 1), 1100);
  on(['kz-z', 'kz-c', 'kz-v'], kzBlock); P('kz-play', 'kz-c', range(0, D.kmz.c.length - 1, 1), 450);
  const b0 = RV_DATES.findIndex(s => s >= D.post), bmax = D.rv.RV.length - 60;
  $('ai-b').max = bmax; $('ai-b').value = b0; on(['ai-b', 'ai-m'], aiBlock); P('ai-play', 'ai-b', range(120, bmax, 21), 300);
  acfBlock(); patchBlock(); r2Block(); rvBlock(); qlBlock(); brBlock(); vpBlock(); pitBlock(); mcsBlock(); cfBlock(); kzBlock(); aiBlock();
}
window.CH14 = { acfOf, nwVar, dm, kupiec, binomPpf, aci, prepost, qlike };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

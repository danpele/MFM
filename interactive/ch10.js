// Chapter 10 interactive page: one block per chart slide, computed in the browser from ch10_data.js.
(function () {
'use strict';
const D = window.CH10_DATA;
const { LANG, sum, mean, median, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH10_TEXT;

// ---------------------------------------------------------------- colours of the chapter charts (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', teal: '#17A2B8', navy: '#1F2A44', band: '#C5D2E8' };
const GCOL = { US: K.blue, BVB: K.red, Crypto: K.amber };
const GROUPS = ['US', 'BVB', 'Crypto'];
const KEYS = D.assets, LAB = D.labels, GRP = D.group;

// ---------------------------------------------------------------- formatting
const MON = LANG === 'ro' ? ['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sep.', 'oct.', 'nov.', 'dec.'] : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const MONL = LANG === 'ro' ? ['ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 'iunie', 'iulie', 'august', 'septembrie', 'octombrie', 'noiembrie', 'decembrie'] : ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const fday = s => `${+s.slice(8, 10)} ${MONL[+s.slice(5, 7) - 1]} ${s.slice(0, 4)}`;
const fmonEN = s => `${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][+s.slice(5, 7) - 1]} ${s.slice(0, 4)}`;
const nfE = x => x.toFixed(2).replace('-', '−');
const fmon = s => `${MON[+s.slice(5, 7) - 1]} ${s.slice(0, 4)}`;
const nfi = (x, d = 0) => {          // thousands separator: 15 500 / 15,500
  const s = nf(x, d), [a, b] = s.split(LANG === 'ro' ? ',' : '.'), neg = a.startsWith('−'), m = neg ? a.slice(1) : a;
  const g = m.replace(/\B(?=(\d{3})+(?!\d))/g, LANG === 'ro' ? '\u202F' : ',');
  return (neg ? '−' : '') + g + (b !== undefined ? (LANG === 'ro' ? ',' : '.') + b : '');
};
const sig = x => (Math.abs(x) >= 100 ? nfi(x, 0) : Math.abs(x) >= 10 ? nf(x, 1) : Math.abs(x) >= 1 ? nf(x, 2) : Math.abs(x) >= 0.1 ? nf(x, 3) : nf(x, 4));
const sz = (id, h) => { $(id).style.height = h + 'px'; };

// ---------------------------------------------------------------- statistics (numpy / scipy definitions)
function pearson(x, y) {
  const mx = mean(x), my = mean(y); let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < x.length; i++) { const a = x[i] - mx, b = y[i] - my; sxy += a * b; sxx += a * a; syy += b * b; }
  return sxy / Math.sqrt(sxx * syy);
}
function ranks(x) {                       // average ranks for ties (scipy.stats.rankdata)
  const idx = x.map((_, i) => i).sort((i, j) => x[i] - x[j]), rk = new Array(x.length);
  for (let i = 0; i < idx.length;) { let j = i; while (j + 1 < idx.length && x[idx[j + 1]] === x[idx[i]]) j++; const v = (i + j) / 2 + 1; for (let k = i; k <= j; k++) rk[idx[k]] = v; i = j + 1; }
  return rk;
}
const spearman = (x, y) => pearson(ranks(x), ranks(y));
const ols = (x, y) => { const mx = mean(x), my = mean(y); let a = 0, b = 0; for (let i = 0; i < x.length; i++) { a += (x[i] - mx) * (y[i] - my); b += (x[i] - mx) ** 2; } return { b: a / b, a: my - a / b * mx }; };
const polyslope = (x, y) => ols(x.map(Math.log), y.map(Math.log)).b;

// ---------------------------------------------------------------- spread estimators (micro.py)
function rollCov(close) {                 // first-order autocovariance of the log changes, demeaned (np.mean)
  const dp = []; for (let i = 1; i < close.length; i++) dp.push(Math.log(close[i]) - Math.log(close[i - 1]));
  const m = mean(dp); let s = 0; for (let i = 1; i < dp.length; i++) s += (dp[i] - m) * (dp[i - 1] - m);
  return s / (dp.length - 1);
}
function csSpread(H, L, C) {              // Corwin-Schultz with the overnight adjustment (daily data)
  const k = 3 - 2 * Math.SQRT2, res = [];
  for (let t = 0; t + 1 < H.length; t++) {
    let h1 = H[t + 1], l1 = L[t + 1]; const h0 = H[t], l0 = L[t];
    if (C) { const c0 = C[t]; if (l1 > c0) { const d = l1 - c0; h1 -= d; l1 -= d; } if (h1 < c0) { const d = c0 - h1; h1 += d; l1 += d; } }
    const beta = Math.log(h0 / l0) ** 2 + Math.log(h1 / l1) ** 2, gamma = Math.log(Math.max(h0, h1) / Math.min(l0, l1)) ** 2;
    const al = (Math.sqrt(2 * beta) - Math.sqrt(beta)) / k - Math.sqrt(gamma / k);
    res.push(Math.max(2 * (Math.exp(al) - 1) / (1 + Math.exp(al)), 0));
  }
  return res;
}
function arTerms(C, H, L) {
  const res = []; for (let t = 0; t + 1 < C.length; t++) { const c = Math.log(C[t]), e0 = (Math.log(H[t]) + Math.log(L[t])) / 2, e1 = (Math.log(H[t + 1]) + Math.log(L[t + 1])) / 2; res.push(4 * (c - e0) * (c - e1)); }
  return res;
}
function edge(O, H, L, C) {               // EDGE (Ardia, Guidotti and Kroencke, 2024), signed; no missing values here
  const lg = a => a.map(Math.log), o0 = lg(O), h0 = lg(H), l0 = lg(L), c0 = lg(C), n = o0.length;
  if (n < 3) return NaN;
  const m0 = h0.map((v, i) => (v + l0[i]) / 2), r1 = [], r2 = [], r3 = [], r4 = [], r5 = [], tau = [], po1 = [], po2 = [], pc1 = [], pc2 = [];
  for (let t = 1; t < n; t++) {
    const o = o0[t], h = h0[t], l = l0[t], m = m0[t], h1 = h0[t - 1], l1 = l0[t - 1], c1 = c0[t - 1], m1 = m0[t - 1];
    r1.push(m - o); r2.push(o - m1); r3.push(m - c1); r4.push(c1 - m1); r5.push(o - c1);
    const ta = (h !== l || l !== c1) ? 1 : 0; tau.push(ta);
    po1.push(ta * (o !== h)); po2.push(ta * (o !== l)); pc1.push(ta * (c1 !== h1)); pc2.push(ta * (c1 !== l1));
  }
  const pt = mean(tau), po = mean(po1) + mean(po2), pc = mean(pc1) + mean(pc2);
  if (sum(tau) < 2 || po === 0 || pc === 0) return NaN;
  const a1 = mean(r1) / pt, a3 = mean(r3) / pt, a5 = mean(r5) / pt, x1 = [], x2 = [];
  for (let i = 0; i < tau.length; i++) {
    const d1 = r1[i] - a1 * tau[i], d3 = r3[i] - a3 * tau[i], d5 = r5[i] - a5 * tau[i];
    x1.push(-4 / po * d1 * r2[i] - 4 / pc * d3 * r4[i]); x2.push(-4 / po * d1 * r5[i] - 4 / pc * d5 * r4[i]);
  }
  const e1 = mean(x1), e2 = mean(x2), v1 = mean(x1.map(v => v * v)) - e1 * e1, v2 = mean(x2.map(v => v * v)) - e2 * e2, vt = v1 + v2;
  const s2 = vt > 0 ? (v2 * e1 + v1 * e2) / vt : (e1 + e2) / 2;
  return Math.sqrt(Math.abs(s2)) * Math.sign(s2);
}

// ================================================================= 1. simulated order book
const LB = D.lob, NS = LB.bid.length;
const lobRel = k => LB.bid[k].map((_, i) => LB.rel0[k] + i);
let lobPool = null;
function pooled(ks) {                    // pandas: mean by distance over the snapshots, then bids and asks pooled
  const acc = {};
  ks.forEach(k => lobRel(k).forEach((r, i) => { const a = acc[r] || (acc[r] = [0, 0, 0]); a[0] += LB.bid[k][i]; a[1] += LB.ask[k][i]; a[2]++; }));
  const xs = Object.keys(acc).map(Number).filter(r => r > 0 && acc[-r]).sort((a, b) => a - b);
  return { x: xs, y: xs.map(r => (acc[r][1] / acc[r][2] + acc[-r][0] / acc[-r][2]) / 2) };
}
const at = (P, lo, hi) => mean(P.x.map((x, i) => [x, P.y[i]]).filter(p => p[0] >= lo && p[0] <= hi).map(p => p[1]));
function lob() {
  const k = +$('lob-k').value, rel = lobRel(k), b = LB.bid[k], a = LB.ask[k];
  $('lob-k-v').textContent = (k + 1) + ' / ' + NS;
  if (!lobPool) lobPool = pooled(range(0, NS - 1, 1));
  const bb = Math.max(...rel.filter((_, i) => b[i] > 0)), ba = Math.min(...rel.filter((_, i) => a[i] > 0)), cur = pooled([k]);
  plot('lob-book', [
    { x: rel, y: b, type: 'bar', name: 'Buy limit orders (bids)', marker: { color: K.green }, width: 0.9, hovertemplate: '%{x} ticks: %{y} orders<extra>bid</extra>' },
    { x: rel, y: a, type: 'bar', name: 'Sell limit orders (asks)', marker: { color: K.red }, width: 0.9, hovertemplate: '%{x} ticks: %{y} orders<extra>ask</extra>' }
  ], layout({ barmode: 'overlay', title: ttl('Snapshot ' + (k + 1) + ' of the simulated order book'), shapes: [vline(0, K.navy, 'dash')],
    xaxis: AX('Distance from the mid-price (ticks)', { range: [-31, 31] }), yaxis: AX('Orders at the price level', { range: [0, 12] }) }));
  plot('lob-depth', [
    { x: lobPool.x, y: lobPool.y, mode: 'lines+markers', name: 'Average depth over ' + NS + ' snapshots', line: { color: K.purple, width: 2 }, marker: { size: 4 }, hovertemplate: '%{x} ticks: %{y:.2f}<extra></extra>' },
    { x: cur.x, y: cur.y, mode: 'lines', name: 'This snapshot, bids and asks pooled', line: { color: K.teal, width: 1.2, shape: 'hv' }, hovertemplate: '%{x} ticks: %{y:.1f}<extra></extra>' }
  ], layout({ title: ttl('Depth by distance from the mid, bids and asks pooled'), xaxis: AX('Distance from the mid-price (ticks)', { range: [0, 31] }), yaxis: AX('Depth (orders)', { range: [0, 10] }) }));
  plot('lob-path', [
    { x: LB.event.map(e => e / 1e3), y: LB.spread, mode: 'lines', name: 'Spread at each snapshot', line: { color: K.blue, width: 1.2, shape: 'hv' }, hovertemplate: 'event %{x:.0f}k: %{y} ticks<extra></extra>' },
    { x: [LB.event[k] / 1e3], y: [LB.spread[k]], mode: 'markers', name: 'This snapshot', marker: { color: K.red, size: 10 }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Bid-ask spread over the simulation'), xaxis: AX('Event (thousands)'), yaxis: AX('Spread (ticks)', { rangemode: 'tozero' }) }));
  const R = LB.res;
  out('lob-out', [T.lob(k + 1, NS, nfi(LB.event[k]), nf(-bb, 1), nf(ba, 1), nf(ba - bb, 0)),
    T.lob2(nf(R.spread_mean, 2), nf(R.spread_med, 0), nf(at(lobPool, 0.5, 1.5), 1), nf(at(lobPool, 9.5, 10.5), 1), nf(at(lobPool, 24.5, 25.5), 1))]);
}

// ================================================================= 2. walking the book
function walk(k, q) {                     // micro.walk_book on the asks of snapshot k: deepest level and VWAP
  const rel = lobRel(k), A = LB.ask[k], lv = [];
  rel.forEach((r, i) => { if (r > 0 && A[i] > 0) lv.push([r, A[i]]); });
  if (sum(lv.map(v => v[1])) < q) return null;
  let left = q, cost = 0, deep = 0; const fills = [];
  for (const [p, n] of lv) { if (left <= 0) break; const t = Math.min(n, left); fills.push([p, t]); cost += p * t; left -= t; deep = p; }
  return { deep, vwap: cost / q, fills, lv };
}
const wbCache = {};
function impactAt(q) {
  if (!wbCache[q]) { const dp = [], vw = []; for (let k = 0; k < NS; k++) { const w = walk(k, q); if (w) { dp.push(w.deep); vw.push(w.vwap); } } wbCache[q] = { deep: mean(dp), vwap: mean(vw), n: dp.length }; }
  return wbCache[q];
}
function walkBook() {
  const q = +$('wb-q').value, S = LB.sizes, k = NS >> 1;
  $('wb-q-v').textContent = q;
  const im = S.map(impactAt), cur = impactAt(q), c0 = im[0].deep;
  plot('wb-chart', [
    { x: S, y: im.map(v => v.deep), mode: 'lines+markers', name: 'Deepest price level reached (ticks from mid)', line: { color: K.red, width: 2 }, marker: { size: 8 }, hovertemplate: '%{x} units: %{y:.2f} ticks<extra></extra>' },
    { x: S, y: im.map(v => v.vwap), mode: 'lines+markers', name: 'Average execution price (ticks from mid)', line: { color: K.blue, width: 2 }, marker: { size: 8, symbol: 'square' }, hovertemplate: '%{x} units: %{y:.2f} ticks<extra></extra>' },
    { x: S, y: S.map(s => c0 * Math.sqrt(s)), mode: 'lines', name: 'Reference slope 1/2', line: { color: K.navy, width: 1, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [q, q], y: [cur.deep, cur.vwap], mode: 'markers', name: 'Order of ' + q + ' units', marker: { color: K.teal, size: 12, symbol: 'diamond', line: { color: '#fff', width: 1.5 } }, hovertemplate: '%{y:.2f} ticks<extra></extra>' }
  ], layout({ title: ttl('Mean over the simulated snapshots'), legend: { orientation: 'h', x: 0, y: -0.3, yanchor: 'top' }, xaxis: AX('Size of the market buy order (units, log scale)', { type: 'log' }), yaxis: AX('Ticks above the mid (log)', { type: 'log' }) }));
  const w = walk(k, q), lv = w.lv, filled = {}; w.fills.forEach(([p, t]) => (filled[p] = t));
  plot('wb-book', [
    { x: lv.map(v => v[0]), y: lv.map(v => filled[v[0]] || 0), type: 'bar', name: 'Taken by the order', marker: { color: K.teal }, hovertemplate: '%{x} ticks: %{y} taken<extra></extra>' },
    { x: lv.map(v => v[0]), y: lv.map(v => v[1] - (filled[v[0]] || 0)), type: 'bar', name: 'Left in the book', marker: { color: K.red }, hovertemplate: '%{x} ticks: %{y} left<extra></extra>' }
  ], layout({ barmode: 'stack', title: ttl('Asks of snapshot ' + (k + 1) + ', walked by an order of ' + q), shapes: [vline(w.vwap, K.blue, 'dash')],
    annotations: [{ x: w.vwap, y: 1, yref: 'paper', text: 'average price', showarrow: false, xanchor: 'left', font: { color: K.blue, size: 11 } }],
    xaxis: AX('Distance from the mid-price (ticks)', { range: [0, 31] }), yaxis: AX('Sell orders') }));
  out('wb-out', [T.wb(q, nf(cur.deep, 1), nf(cur.vwap, 1), cur.n, nf(polyslope(S, im.map(v => v.deep)), 2), nf(polyslope(S, im.map(v => v.vwap)), 2))]);
}

// ================================================================= 3. Roll model
const RZ = D.roll.z, RQ = [...D.roll.q].map(v => (v === '1' ? 1 : -1));
function roll() {
  const c = +$('ro-c').value, s = +$('ro-s').value, n = +$('ro-n').value;
  $('ro-c-v').textContent = nf(c, 3); $('ro-s-v').textContent = nf(s, 3);
  const m = [], p = []; let acc = 100;
  for (let t = 0; t < n; t++) { acc += s * RZ[t]; m.push(acc); p.push(acc + c * RQ[t]); }
  const dp = p.slice(1).map((v, i) => v - p[i]), dm = m.slice(1).map((v, i) => v - m[i]), mu = mean(dp);
  let cv = 0; for (let i = 1; i < dp.length; i++) cv += (dp[i] - mu) * (dp[i - 1] - mu); cv /= dp.length - 1;
  const lags = range(1, 8, 1), ap = lags.map(l => pearson(dp.slice(l), dp.slice(0, -l))), am = lags.map(l => pearson(dm.slice(l), dm.slice(0, -l)));
  const th = -c * c / (s * s + 2 * c * c), b = 1.96 / Math.sqrt(dp.length), k80 = range(0, 79, 1);
  plot('ro-path', [
    { x: k80, y: m.slice(0, 80), mode: 'lines', name: 'Efficient price m<sub>t</sub>', line: { color: K.blue, width: 2 }, hovertemplate: '%{x}: %{y:.3f}<extra></extra>' },
    { x: k80, y: p.slice(0, 80), mode: 'lines+markers', name: 'Trade price p<sub>t</sub> = m<sub>t</sub> + c q<sub>t</sub>', line: { color: K.red, width: 1 }, marker: { size: 4 }, hovertemplate: '%{x}: %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl(`Simulated bid-ask bounce (c = ${c.toFixed(3)}, σ = ${s.toFixed(3)})`), xaxis: AX('Trade number'), yaxis: AX('Price') }));
  plot('ro-acf', [
    { x: lags.map(l => l - 0.18), y: ap, type: 'bar', width: 0.36, name: 'Trade price changes', marker: { color: K.red }, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags },
    { x: lags.map(l => l + 0.18), y: am, type: 'bar', width: 0.36, name: 'Efficient price changes', marker: { color: K.blue }, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags }
  ], layout({ title: ttl('Autocorrelation of price changes, n = ' + n), shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: -b, y1: b, fillcolor: K.band, opacity: 0.6, line: { width: 0 }, layer: 'below' }, hline(th, K.navy, 'dash')],
    xaxis: AX('Lag', { dtick: 1 }), yaxis: AX('Autocorrelation', { range: [-0.55, 0.15] }) }));
  out('ro-out', [cv < 0 ? T.ro(nfi(n), nf(2 * c, 3), nf(2 * Math.sqrt(-cv), 4), nf(ap[0], 3), nf(th, 3)) : T.ro_pos(nfi(n), nf(2 * c, 3), nf(ap[0], 3), nf(th, 3))]);
}

// ================================================================= 4. spread estimators at two frequencies (SPY)
const F = D.freq, SF_P = ['slide', '2020', '2021', '2022', '2023', '2024', '2025', '2026'];
function sfWindow(p) {
  const inY = (d, y) => d.slice(0, 4) === y, last = F.d_days[F.d_days.length - 1];
  const dsel = F.d_days.map((d, i) => (p === 'slide' ? d >= F.start2 : inY(d, p)) ? i : -1).filter(i => i >= 0);
  const isel = F.days.map((d, i) => (p === 'slide' || inY(d, p)) ? i : -1).filter(i => i >= 0);
  const pick = (a, s) => s.map(i => a[i]);
  const O = pick(F.o, dsel), H = pick(F.h, dsel), L = pick(F.l, dsel), Cc = pick(F.c, dsel), rc = rollCov(Cc), ar2 = mean(arTerms(Cc, H, L));
  const daily = { Roll: rc < 0 ? 1e4 * 2 * Math.sqrt(-rc) : NaN, 'Corwin-Schultz': 1e4 * mean(csSpread(H, L, Cc)), 'Abdi-Ranaldo': 1e4 * Math.sqrt(Math.max(ar2, 0)), EDGE: 1e4 * edge(O, H, L, Cc) };
  const cv = mean(pick(F.cov, isel)) / 1e8, a5 = mean(pick(F.ar2, isel)) / 1e8;
  const intr = { Roll: 1e4 * 2 * Math.sqrt(Math.max(-cv, 0)), 'Corwin-Schultz': mean(pick(F.cs, isel)), 'Abdi-Ranaldo': 1e4 * Math.sqrt(Math.max(a5, 0)), EDGE: mean(pick(F.edge, isel).map(v => Math.max(v, 0))) };
  const tick = mean(pick(F.price, isel).map(v => 1e4 * 0.01 / v));
  return { daily, intr, tick, nd: dsel.length, n5: isel.length, d0: F.d_days[dsel[0]], d1: F.d_days[dsel[dsel.length - 1]] || last };
}
function spreadFreq() {
  const i = +$('sf-y').value, p = SF_P[i], W = sfWindow(p), E = Object.keys(W.daily);
  $('sf-y-v').textContent = p === 'slide' ? T.sf_slide : p;
  plot('sf-chart', [
    { x: E, y: E.map(e => W.daily[e]), type: 'bar', name: p === 'slide' ? 'From daily bars (last two years)' : 'From daily bars (' + p + ')', marker: { color: K.blue }, hovertemplate: '%{x}: %{y:.2f} bp<extra></extra>' },
    { x: E, y: E.map(e => W.intr[e]), type: 'bar', name: p === 'slide' ? 'From 5-minute bars (average over days)' : 'From 5-minute bars (' + p + ')', marker: { color: K.teal }, hovertemplate: '%{x}: %{y:.2f} bp<extra></extra>' },
    { x: [E[0]], y: [null], mode: 'lines', name: 'One tick (USD 0.01) relative to the price: ' + W.tick.toFixed(2) + ' bp', line: { color: K.red, dash: 'dash', width: 2 }, hoverinfo: 'skip' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('SPY: estimated relative spread'), shapes: [hline(W.tick, K.red, 'dash')],
    xaxis: AX(''), yaxis: AX('Estimated relative spread (bp, log scale)', { type: 'log', range: [-1, 2.3], tickvals: [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200] }) }));
  const f = v => (isFinite(v) ? nf(v, 2) : '—');
  out('sf-out', [T.sf(p === 'slide' ? T.sf_d2 : p, W.nd, f(W.daily.Roll), f(W.daily['Corwin-Schultz']), f(W.daily['Abdi-Ranaldo']), f(W.daily.EDGE)),
    T.sf5(nfi(W.n5), f(W.intr.Roll), f(W.intr['Corwin-Schultz']), f(W.intr['Abdi-Ranaldo']), f(W.intr.EDGE), nf(W.tick, 2))]);
}

// ================================================================= 5. spreads of 25 assets
const SC_E = [['cs', 'Corwin–Schultz'], ['ar', 'Abdi–Ranaldo'], ['roll', 'Roll'], ['edge', 'EDGE']];
const ORDER_G = GROUPS.flatMap(g => KEYS.filter(k => GRP[k] === g));
function spreadCross() {
  const i = +$('sc-e').value, [e, en] = SC_E[i], X = D.cross, srt = $('sc-s').value;
  const [e2, en2] = e === 'ar' ? ['cs', 'Corwin–Schultz'] : ['ar', 'Abdi–Ranaldo'];
  $('sc-e-v').textContent = en;
  const ks = srt === 'vol' ? [...KEYS].sort((a, b) => X[a].vol - X[b].vol) : ORDER_G, y = ks.map(k => LAB[k]);
  const v = k => (X[k][e] === null || !isFinite(X[k][e]) ? null : X[k][e]);
  sz('sc-bars', 560); sz('sc-scat', 560);
  plot('sc-bars', [
    { y, x: ks.map(v), type: 'bar', orientation: 'h', name: en + ' (solid)', marker: { color: ks.map(k => GCOL[GRP[k]]) }, hovertemplate: '%{y}: %{x:.1f} bp<extra>' + en + '</extra>' },
    { y, x: ks.map(k => X[k][e2]), type: 'bar', orientation: 'h', name: en2 + ' (hatched)', marker: { color: ks.map(k => GCOL[GRP[k]]), opacity: 0.6, pattern: { shape: '/', fgcolor: '#fff', size: 6 } }, hovertemplate: '%{y}: %{x:.1f} bp<extra>' + en2 + '</extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Estimated from daily bars, September 2024 – September 2026'), margin: { l: 120, r: 12, t: 30, b: 40 },
    legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top' }, xaxis: AX('Relative spread (bp)'), yaxis: AX('', { autorange: 'reversed', tickfont: { size: 10 } }) }));
  const ok = KEYS.filter(k => v(k) !== null);
  plot('sc-scat', GROUPS.map(g => {
    const kk = ok.filter(k => GRP[k] === g);
    return { x: kk.map(k => X[k].vol), y: kk.map(k => X[k][e]), text: kk.map(k => LAB[k]), mode: 'markers', name: g, marker: { color: GCOL[g], size: 10 }, hovertemplate: '%{text}<br>vol %{x:.1f}%<br>%{y:.1f} bp<extra></extra>' };
  }), layout({ title: ttl(en + ' against volatility'), legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top' }, xaxis: AX('Annualised volatility (%)'), yaxis: AX(en + ' spread (bp)') }));
  const med = g => median(ok.filter(k => GRP[k] === g).map(v));
  out('sc-out', [T.sc(en, nf(med('US'), 0), nf(med('BVB'), 0), nf(med('Crypto'), 0), nf(spearman(ok.map(v), ok.map(k => X[k].vol)), 2), ok.length,
    KEYS.filter(k => X[k][e] === 0).length)]);
}

// ================================================================= 6. Amihud, 25 assets
const AM = D.amihud;
function amihudCross() {
  const s0 = +$('am-s').value, M = AM.months;
  $('am-s-v').textContent = fmon(M[s0]);
  const il = {}; KEYS.forEach(k => { const S = sum(AM.s[k].slice(s0)), N = sum(AM.n[k].slice(s0)); il[k] = N ? S / N : NaN; });
  const ks = [...KEYS].sort((a, b) => il[a] - il[b]);
  sz('am-chart', 560);
  plot('am-chart', [{ y: ks.map(k => LAB[k]), x: ks.map(k => il[k]), type: 'bar', orientation: 'h', marker: { color: ks.map(k => GCOL[GRP[k]]) }, showlegend: false, hovertemplate: '%{y}: %{x:.4g} bp per USD 1m<extra></extra>' },
    ...GROUPS.map(g => ({ x: [null], y: [null], type: 'bar', name: g, marker: { color: GCOL[g] }, hoverinfo: 'skip' }))],
  layout({ title: ttl('Amihud illiquidity: mean |daily return| per USD 1 million traded, ' + fmonEN(M[s0]) + ' – Sep 2026'), margin: { l: 130, r: 12, t: 30, b: 40 }, legend: { orientation: 'h', x: 0, y: -0.1, yanchor: 'top' },
    xaxis: AX('bp per USD 1 million traded (log scale)', { type: 'log' }), yaxis: AX('', { tickfont: { size: 10 } }) }));
  const nd = sum(AM.n.SPY.slice(s0));
  out('am-out', [T.am(fmon(M[s0]), nfi(nd), sig(il.SPY), sig(il.BTC), sig(il.TLV), sig(il.TEL), nfi(il.TLV / il.SPY, 0))]);
}

// ================================================================= 7. Amihud over time
const AT = D.amihud_time;
const atMed = {};
GROUPS.forEach(g => { const S = AT.series[g], ks = Object.keys(S); atMed[g] = AT.months.map((_, t) => { const v = ks.map(k => S[k][t]).filter(x => x !== null); return v.length ? median(v) : null; }); });
function amihudTime() {
  const t = +$('at-t').value, M = AT.months;
  $('at-t-v').textContent = fmon(M[t]);
  plot('at-chart', GROUPS.map(g => ({ x: M.slice(0, t + 1), y: atMed[g].slice(0, t + 1), mode: 'lines', name: g + ': median across assets', line: { color: GCOL[g], width: 1.8 }, hovertemplate: g + ' %{x}: %{y:.3g}<extra></extra>' })),
    layout({ title: ttl('Monthly Amihud ratio, median by group (without SPY and the BET ETF)'), shapes: [vline('2020-09', K.navy, 'dot')],
      annotations: [{ x: '2020-09', y: 0.62, yref: 'paper', text: 'Romania becomes an emerging<br>market (FTSE Russell), Sep 2020', showarrow: false, xanchor: 'left', yanchor: 'middle', align: 'left', font: { size: 11 } }],
      xaxis: AX('', { type: 'category', nticks: 10, range: [-0.5, M.length - 0.5] }), yaxis: AX('Amihud (bp per USD 1m, log scale)', { type: 'log', range: [-2.2, 3.3] }) }));
  const yr = M[t].slice(0, 4), ym = g => mean(atMed[g].filter((_, i) => M[i].slice(0, 4) === yr && i <= t));
  out('at-out', [T.at(fmon(M[t]), sig(atMed.US[t]), sig(atMed.BVB[t]), sig(atMed.Crypto[t]), nfi(atMed.BVB[t] / atMed.US[t], 0)),
    T.at2(yr, sig(ym('US')), nfi(ym('BVB'), 0), sig(ym('Crypto')))]);
}

// ================================================================= 8. SPY intraday
const TD = D.tod;
function intraday() {
  const p = TD.periods[+$('id-p').value], t = +$('id-t').value, L = TD.labels, sh = TD.share[p], ab = TD.absr[p];
  $('id-p-v').textContent = p === 'all' ? T.id_all : p; $('id-t-v').textContent = L[t];
  sz('id-vol', 340); sz('id-abs', 340);
  plot('id-vol', [{ x: L, y: sh, type: 'bar', name: 'Share of daily volume (%)', marker: { color: L.map((_, i) => (i === t ? K.navy : K.teal)) }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }],
    layout({ title: ttl('Share of the day\'s volume, by 5-minute bar'), showlegend: false, xaxis: AX('Start of the 5-minute bar (New York time)', { type: 'category', tickvals: L.filter((_, i) => i % 12 === 0) }), yaxis: AX('Share of daily volume (%)', { range: [0, 8] }) }));
  plot('id-abs', [{ x: L, y: ab, mode: 'lines+markers', name: 'Mean absolute 5-minute return (bp)', line: { color: K.red, width: 1.5 }, marker: { size: 4 }, hovertemplate: '%{x}: %{y:.2f} bp<extra></extra>' },
    { x: [L[t]], y: [ab[t]], mode: 'markers', name: 'Selected bar', marker: { color: K.navy, size: 11, symbol: 'diamond' }, hoverinfo: 'skip' }],
    layout({ title: ttl('Mean |5-minute return|'), showlegend: false, xaxis: AX('Start of the 5-minute bar (New York time)', { type: 'category', tickvals: L.filter((_, i) => i % 12 === 0) }), yaxis: AX('Mean |return| (basis points)', { range: [0, 16] }) }));
  const mid = L.map((l, i) => (l >= '11:30' && l <= '14:00' ? i : -1)).filter(i => i >= 0);
  out('id-out', [T.id(p === 'all' ? T.id_all : p, nfi(TD.ndays[p]), L[t], nf(sh[t], 1), nf(ab[t], 1), nf(sum(sh.slice(0, t + 1)), 1)),
    T.id2(nf(sum(sh.slice(0, 6)), 1), nf(sum(sh.slice(-6)), 1), nf(ab[0] / mean(mid.map(i => ab[i])), 2))]);
}

// ================================================================= 9. illiquidity and the VIX
const IV = D.vix, IV_F = ['day', 'week', 'month', 'quarter'];
function weekKey(s) {                     // pandas resample('W'): weeks ending on Sunday
  const d = new Date(s + 'T00:00:00Z'), dow = d.getUTCDay(), e = new Date(d.getTime() + ((7 - dow) % 7) * 864e5);
  return e.toISOString().slice(0, 10);
}
function aggregate(f) {
  const key = f === 'day' ? s => s : f === 'week' ? weekKey : f === 'month' ? s => s.slice(0, 7) : s => s.slice(0, 4) + '-' + String(((+s.slice(5, 7) - 1) / 3 | 0) * 3 + 2).padStart(2, '0') + '-15';
  const g = new Map();
  IV.days.forEach((s, i) => { const k = key(s), a = g.get(k) || [0, 0, 0]; a[0] += IV.ill[i]; a[1] += IV.vix[i]; a[2]++; g.set(k, a); });
  const ks = [...g.keys()];
  return { x: ks, ill: ks.map(k => g.get(k)[0] / g.get(k)[2]), vix: ks.map(k => g.get(k)[1] / g.get(k)[2]) };
}
function illiqVix() {
  const f = IV_F[+$('iv-f').value], A = aggregate(f);
  $('iv-f-v').textContent = T.iv_f[f];
  plot('iv-chart', [
    { x: A.x, y: A.ill, mode: 'lines', name: 'SPY intraday illiquidity (bp per USD 100 million)', line: { color: K.blue, width: f === 'day' ? 0.8 : 1.6 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: A.x, y: A.vix, mode: 'lines', name: 'VIX (right axis)', yaxis: 'y2', line: { color: K.red, width: f === 'day' ? 0.8 : 1.3, dash: 'dash' }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }
  ], layout({ title: ttl('Means by ' + f), margin: { l: 56, r: 50, t: 30, b: 40 }, xaxis: AX('', { type: 'date' }), yaxis: AX('Illiquidity (bp per USD 100m)'),
    yaxis2: AX('VIX', { overlaying: 'y', side: 'right', showgrid: false }) }));
  const lx = A.vix.map(Math.log), ly = A.ill.map(Math.log), fit = ols(lx, ly), xs = [Math.min(...lx), Math.max(...lx)];
  plot('iv-scat', [
    { x: A.vix, y: A.ill, text: A.x, mode: 'markers', name: 'One ' + f, marker: { color: K.blue, size: f === 'day' ? 4 : 7, opacity: f === 'day' ? 0.5 : 0.85 }, hovertemplate: '%{text}<br>VIX %{x:.1f}<br>illiquidity %{y:.2f}<extra></extra>' },
    { x: xs.map(Math.exp), y: xs.map(v => Math.exp(fit.a + fit.b * v)), mode: 'lines', name: 'OLS of log illiquidity on log VIX', line: { color: K.red, width: 2 }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Log illiquidity against log VIX'), xaxis: AX('VIX (log scale)', { type: 'log' }), yaxis: AX('Illiquidity (log scale)', { type: 'log' }) }));
  out('iv-out', [T.iv(T.iv_f[f], nfi(A.x.length), nf(pearson(A.ill, A.vix), 2), nf(fit.b, 2)), ...(f === 'day' ? [T.iv2(nf(IV.res.elast_se, 2))] : [])]);
}

// ================================================================= 10. Kyle
function kyle() {
  const sv = +$('ky-v').value, su = +$('ky-u').value, us = range(2, 40, 0.5);
  $('ky-v-v').textContent = nf(sv, 1) + ' USD'; $('ky-u-v').textContent = su + (LANG === 'ro' ? ' mii' : ' thousand');
  const lam = u => sv / (2 * u), prof = u => sv * u / 2;
  plot('ky-lam', [{ x: us, y: us.map(lam), mode: 'lines', name: 'Price impact λ = σ<sub>v</sub> / (2σ<sub>u</sub>)', line: { color: K.blue, width: 2 }, hovertemplate: 'σ<sub>u</sub> %{x}: λ %{y:.3f}<extra></extra>' },
    { x: [su], y: [lam(su)], mode: 'markers', name: 'Selected σ<sub>u</sub>', marker: { color: K.red, size: 11 }, hoverinfo: 'skip' }],
  layout({ title: ttl('σ<sub>v</sub> = ' + sv.toFixed(1) + ' USD'), xaxis: AX('σ<sub>u</sub> (thousand shares)'), yaxis: AX('λ (USD per thousand shares)', { rangemode: 'tozero' }) }));
  plot('ky-prof', [{ x: us, y: us.map(prof), mode: 'lines', name: 'Expected profit of the insider σ<sub>v</sub>σ<sub>u</sub> / 2', line: { color: K.green, width: 2 }, hovertemplate: 'σ<sub>u</sub> %{x}: %{y:.1f}<extra></extra>' },
    { x: [su], y: [prof(su)], mode: 'markers', name: 'Selected σ<sub>u</sub>', marker: { color: K.red, size: 11 }, hoverinfo: 'skip', showlegend: false }],
  layout({ title: ttl('σ<sub>v</sub> = ' + sv.toFixed(1) + ' USD'), xaxis: AX('σ<sub>u</sub> (thousand shares)'), yaxis: AX('Expected profit (thousand USD)', { rangemode: 'tozero' }) }));
  const ys = range(-50, 50, 1);
  plot('ky-imp', [{ x: ys, y: ys.map(y => lam(su) * y), mode: 'lines', name: 'p − p₀ = λ y', line: { color: K.purple, width: 2 }, hovertemplate: 'y %{x}: %{y:.2f} USD<extra></extra>' },
    { x: [-2 * su, 2 * su], y: [-2 * su * lam(su), 2 * su * lam(su)], mode: 'markers', name: 'y = ±2σ<sub>u</sub>', marker: { color: K.red, size: 9 }, hovertemplate: '%{y:.2f} USD<extra></extra>' }],
  layout({ title: ttl('Price move against net order flow'), xaxis: AX('Net order flow y (thousand shares)'), yaxis: AX('Price move (USD)', { range: [-6, 6] }) }));
  out('ky-out', [T.ky(nf(sv, 1), su, nf(lam(su), 3), nf(1 / lam(su), 1), nf(su / sv, 1), nf(prof(su), 1), nf(10 * lam(su), 2))]);
}

// ================================================================= 11. Almgren-Chriss
const ACP = D.ac.par, AC_L = [0, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 3e-4];
function acTraj(lam, N) {                 // micro.ac_trajectory, exact discrete-time formulas
  const { X, T: TT, sigma, eta, gamma } = ACP, tau = TT / N, et = eta - gamma * tau / 2, t = range(0, N, 1).map(k => k * tau);
  let x;
  if (lam === 0) x = t.map(v => X * (1 - v / TT));
  else { const kt2 = lam * sigma ** 2 / et, kap = Math.acosh(kt2 * tau * tau / 2 + 1) / tau; x = t.map(v => X * Math.sinh(kap * (TT - v)) / Math.sinh(kap * TT)); }
  x[N] = 0;
  let s2 = 0, v = 0; for (let k = 1; k <= N; k++) { s2 += (x[k - 1] - x[k]) ** 2; v += x[k] ** 2; }
  return { t, x, E: 0.5 * gamma * X * X + et / tau * s2, sd: Math.sqrt(sigma ** 2 * tau * v) };
}
const lamTxt = l => (l === 0 ? '0' : l.toExponential(0).replace('e-', 'e-'));
const lamHtml = l => { if (l === 0) return '0'; const e = Math.floor(Math.log10(l) + 1e-9), m = Math.round(l / 10 ** e); return (m === 1 ? '' : m + '·') + '10<sup>' + String(e).replace('-', '−') + '</sup>'; };
let acFr = null;
function almgren() {
  const i = +$('ac-l').value, lam = AC_L[i], N = ACP.N;
  $('ac-l-v').textContent = lamTxt(lam);
  if (!acFr) { acFr = []; for (let k = 0; k < 60; k++) acFr.push(acTraj(Math.pow(10, -8 + 4.5 * k / 59), N)); }
  const ref = [[0, K.blue, 'Risk-neutral, λ = 0 (sell evenly)'], [2e-6, K.green, 'λ = 2e-6'], [2e-5, K.orange, 'λ = 2e-5'], [1e-4, K.red, 'λ = 1e-4 (very risk averse)']];
  const cur = acTraj(lam, 50), c5 = acTraj(lam, N);
  plot('ac-traj', [...ref.map(([l, c, n]) => { const a = acTraj(l, 50); return { x: a.t, y: a.x.map(v => v / 1e3), mode: 'lines', name: n, line: { color: c, width: 1.6 }, hovertemplate: 'day %{x:.1f}: %{y:.0f}k<extra></extra>' }; }),
    { x: cur.t, y: cur.x.map(v => v / 1e3), mode: 'lines', name: 'Selected λ = ' + lamTxt(lam), line: { color: K.purple, width: 3.5 }, hovertemplate: 'day %{x:.1f}: %{y:.0f}k<extra></extra>' }],
  layout({ title: ttl('Optimal trading trajectories'), legend: { orientation: 'h', x: 0, y: -0.25, yanchor: 'top' }, xaxis: AX('Time (days)'), yaxis: AX('Shares still to sell (thousands)', { range: [0, 1050] }) }));
  plot('ac-front', [{ x: acFr.map(a => a.sd / 1e6), y: acFr.map(a => a.E / 1e6), mode: 'lines', name: 'Efficient frontier (N = 5 days)', line: { color: K.purple, width: 2 }, hovertemplate: 'sd %{x:.3f}m<br>E %{y:.3f}m<extra></extra>' },
    ...ref.map(([l, c]) => { const a = acTraj(l, N); return { x: [a.sd / 1e6], y: [a.E / 1e6], mode: 'markers', marker: { color: c, size: 10 }, showlegend: false, hovertemplate: 'λ = ' + lamTxt(l) + '<br>sd %{x:.3f}m<br>E %{y:.3f}m<extra></extra>' }; }),
    { x: [c5.sd / 1e6], y: [c5.E / 1e6], mode: 'markers', name: 'Selected λ', marker: { color: K.purple, size: 15, symbol: 'diamond', line: { color: '#fff', width: 2 } }, hoverinfo: 'skip' }],
  layout({ title: ttl('Cost versus risk of the liquidation'), legend: { orientation: 'h', x: 0, y: -0.25, yanchor: 'top' }, xaxis: AX('Standard deviation of cost (USD million)', { range: [-0.03, 1.1] }), yaxis: AX('Expected cost (USD million)', { range: [0.4, 2.6] }) }));
  const tau = ACP.T / N, kap = lam === 0 ? 0 : Math.acosh(lam * ACP.sigma ** 2 / (ACP.eta - ACP.gamma * tau / 2) * tau * tau / 2 + 1) / tau;
  out('ac-out', [T.ac(lamHtml(lam), pct(1 - c5.x[1] / ACP.X, 0), nf(c5.E / 1e6, 2), nf(c5.sd / 1e6, 2), nf(kap, 2))]);
}

// ================================================================= 12. flash crash
const FL = D.flash;
function flash() {
  const k = +$('fc-t').value, n = FL.days.length, x = FL.days.map(fday), idx = range(0, n - 1, 1);
  $('fc-t-v').textContent = x[k];
  const pre = FL.days.map((d, i) => (d <= '2010-05-05' ? FL.v[i] : null)).filter(v => v !== null), vmed = median(pre);
  const show = idx.filter(i => i <= k), i6 = FL.days.indexOf('2010-05-06');
  plot('fc-chart', [
    { x: show, y: show.map(i => FL.h[i] - FL.l[i]), base: show.map(i => FL.l[i]), type: 'bar', width: 0.35, name: 'Daily range: low to high', marker: { color: show.map(i => (i === k ? K.purple : K.blue)) }, customdata: show.map(i => [x[i], FL.l[i], FL.h[i]]), hovertemplate: '%{customdata[0]}<br>low %{customdata[1]:.2f}<br>high %{customdata[2]:.2f}<extra></extra>' },
    { x: show, y: show.map(i => FL.c[i]), mode: 'markers', name: 'Close', marker: { color: K.red, size: 8 }, customdata: show.map(i => x[i]), hovertemplate: '%{customdata}: close %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl('SPY daily bars, 15 April – 28 May 2010 (unadjusted)'), annotations: k >= i6 ? [{ x: i6, y: FL.l[i6], text: '6 May 2010: low of USD ' + FL.l[i6].toFixed(2) + ',<br>' + (100 * (1 - FL.l[i6] / FL.prev[i6])).toFixed(1) + '% below the previous close', showarrow: true, arrowhead: 2, ax: 120, ay: -150, align: 'left', font: { size: 11, color: K.navy }, bgcolor: 'rgba(255,255,255,0.85)' }] : [], xaxis: AX('', { tickvals: idx.filter(i => i % 5 === 0), ticktext: idx.filter(i => i % 5 === 0).map(i => FL.days[i].slice(8) + ' ' + ['Apr', 'May'][+FL.days[i].slice(5, 7) - 4]), range: [-0.7, n - 0.3] }),
    yaxis: AX('SPY price (USD)', { range: [103, 123] }) }));
  const lo = FL.l[k] / FL.prev[k] - 1, cl = FL.c[k] / FL.prev[k] - 1;
  out('fc-out', [T.fc(x[k], nf(FL.l[k], 2), pct(lo, 1), nf(FL.c[k], 2), pct(cl, 1), nf(FL.v[k] / vmed, 1))]);
}

// ================================================================= 13. latency arbitrage tax
const RT = D.race, RC = RT.coef;
function raceTax() {
  const h = +$('rt-h').value, b = +$('rt-b').value;
  $('rt-h-v').textContent = nf(h, 4) + ' bp'; $('rt-b-v').textContent = nf(b, 4);
  const tax = RT.sigma.map(s => RC.col6_v + b * s), mx = Math.max(...tax), im = tax.indexOf(mx);
  plot('rt-chart', [{ x: RT.days, y: tax, mode: 'lines', name: `Implied daily tax: ${RC.col6_v} + ${b.toFixed(4)} × volatility (%)`, line: { color: K.blue, width: 0.9 }, hovertemplate: '%{x}: %{y:.3f} bp<extra></extra>' },
    { x: [RT.days[0]], y: [null], mode: 'lines', name: 'Value-only specification: 0.4213 bp', line: { color: K.red, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [RT.days[0]], y: [null], mode: 'lines', name: "The paper's lowest and highest scenarios: 0.20 and 0.74 bp", line: { color: K.green, dash: 'dot' }, hoverinfo: 'skip' },
    { x: [RT.days[0]], y: [null], mode: 'lines', name: 'Selected threshold', line: { color: K.purple, width: 2 }, hoverinfo: 'skip' }],
  layout({ title: ttl('Latency arbitrage tax implied for SPY, 2021–2025'), shapes: [hline(RC.col2, K.red, 'dash'), hline(RC.lo, K.green, 'dot'), hline(RC.hi, K.green, 'dot'), hline(h, K.purple)],
    xaxis: AX(''), yaxis: AX('Latency arbitrage tax (bp)', { range: [0.1, 1.45] }) }));
  plot('rt-hist', [{ x: tax, type: 'histogram', xbins: { start: 0.3, end: 1.5, size: 0.01 }, marker: { color: K.blue, line: { color: '#fff', width: 0.5 } }, name: 'Days', hovertemplate: '%{x} bp: %{y} days<extra></extra>' }],
    layout({ title: ttl('Distribution of the daily tax'), showlegend: false, shapes: [vline(h, K.purple), vline(RC.hi, K.green, 'dot')], xaxis: AX('Latency arbitrage tax (bp)', { range: [0.3, 1.2] }), yaxis: AX('Days') }));
  out('rt-out', [T.rt(nf(b, 4), nf(median(tax), 2), nf(h, 4), pct(tax.filter(v => v > h).length / tax.length, 0), tax.filter(v => v > RC.hi).length, nf(mx, 2), fday(RT.days[im]), nfi(tax.length))]);
}

// ================================================================= 14. AI mini-case
const MC_SET = ['all', 'US', 'BVB', 'Crypto'];
function miniCase() {
  const i = +$('mc-x').value, ex = MC_SET[i], X = D.cross, ks = KEYS.filter(k => GRP[k] !== ex);
  $('mc-x-v').textContent = T.mc_set[ex];
  const r1 = spearman(ks.map(k => X[k].cs), ks.map(k => X[k].vol)), r2 = spearman(ks.map(k => X[k].illiq), ks.map(k => X[k].dv)), r3 = spearman(ks.map(k => X[k].cs), ks.map(k => X[k].illiq));
  const sc = (id, a, b, tl, xl, yl, logx, logy) => plot(id, GROUPS.filter(g => g !== ex).map(g => {
    const kk = ks.filter(k => GRP[k] === g);
    return { x: kk.map(k => X[k][a]), y: kk.map(k => X[k][b]), text: kk.map(k => (['SPY', 'TLV', 'BTC'].includes(k) ? k : '')), customdata: kk.map(k => LAB[k]), mode: 'markers+text', textposition: 'top center', cliponaxis: false, textfont: { size: 10, color: K.navy }, name: g, marker: { color: GCOL[g], size: 9 }, hovertemplate: '%{customdata}<br>%{x:.3g}, %{y:.3g}<extra></extra>' };
  }), layout({ title: ttl(tl), xaxis: AX(xl, logx ? { type: 'log' } : {}), yaxis: AX(yl, logy ? { type: 'log' } : {}) }));
  sc('mc-1', 'vol', 'cs', `(1) Spearman ${nfE(r1)}: spread and volatility`, 'Annualised volatility (%)', 'Corwin-Schultz spread (bp)');
  sc('mc-2', 'dv', 'illiq', `(2) Spearman ${nfE(r2)}: value and illiquidity`, 'Daily traded value (USD m)', 'Amihud (bp / USD m)', true, true);
  sc('mc-3', 'illiq', 'cs', `(3) Spearman ${nfE(r3)}: spread and illiquidity`, 'Amihud (bp / USD m)', 'Corwin-Schultz spread (bp)', true);
  out('mc-out', [T.mc(T.mc_set[ex], ks.length, nf(r1, 2), nf(r2, 2), nf(r3, 2), nf(r1 - r3, 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  $('lob-k').max = NS - 1; $('lob-k').value = NS >> 1; on(['lob-k'], lob); P('lob-play', 'lob-k', range(0, NS - 1, 1), 140);
  on(['wb-q'], walkBook); P('wb-play', 'wb-q', range(1, 80, 1), 90);
  on(['ro-c', 'ro-s', 'ro-n'], roll); P('ro-play', 'ro-c', range(0, 0.15, 0.005), 220);
  on(['sf-y'], spreadFreq); P('sf-play', 'sf-y', range(0, 7, 1), 1100);
  on(['sc-e', 'sc-s'], spreadCross); P('sc-play', 'sc-e', range(0, 3, 1), 1500);
  $('am-s').max = AM.months.length - 2; on(['am-s'], amihudCross); P('am-play', 'am-s', range(0, AM.months.length - 2, 1), 400);
  $('at-t').max = AT.months.length - 1; $('at-t').value = AT.months.length - 1; on(['at-t'], amihudTime); P('at-play', 'at-t', range(0, AT.months.length - 1, 1), 70);
  $('id-p').max = TD.periods.length - 1; on(['id-p', 'id-t'], intraday); P('id-play', 'id-t', range(0, 77, 1), 120);
  on(['iv-f'], illiqVix); P('iv-play', 'iv-f', range(0, 3, 1), 1500);
  on(['ky-v', 'ky-u'], kyle); P('ky-play', 'ky-u', range(2, 40, 1), 150);
  on(['ac-l'], almgren); P('ac-play', 'ac-l', range(0, AC_L.length - 1, 1), 500);
  $('fc-t').max = FL.days.length - 1; $('fc-t').value = FL.days.length - 1; on(['fc-t'], flash); P('fc-play', 'fc-t', range(0, FL.days.length - 1, 1), 350);
  on(['rt-h', 'rt-b'], raceTax); P('rt-play', 'rt-h', range(0.2, 1.1, 0.02), 220);
  on(['mc-x'], miniCase); P('mc-play', 'mc-x', range(0, 3, 1), 1500);
  lob(); walkBook(); roll(); spreadFreq(); spreadCross(); amihudCross(); amihudTime(); intraday(); illiqVix(); kyle(); almgren(); flash(); raceTax(); miniCase();
}
window.CH10 = { pooled, impactAt, polyslope, sfWindow, rollCov, csSpread, arTerms, edge, spearman, aggregate, acTraj, AC_L, atMed, pearson, ols };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

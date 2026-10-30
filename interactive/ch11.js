// Chapter 11 interactive page: one block per chart slide, computed in the browser from ch11_data.js.
(function () {
'use strict';
const D = window.CH11_DATA;
const { sum, mean, median, nf, pct, $, AX, layout, ttl, plot, out, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH11_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', forest: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', teal: '#17A2B8', navy: '#1F2A44', band: '#C5D2E8' };
const MODEL_COL = { Data: K.blue, GBM: K.orange, Merton: K.purple, Heston: K.forest };
const DT = 1 / 252;

// ---------------------------------------------------------------- helpers
function decodeDates(start, gaps) {
  const t0 = Date.parse(start + 'T00:00:00Z'), res = [start]; let d = 0;
  for (const g of gaps) { d += g; res.push(new Date(t0 + d * 864e5).toISOString().slice(0, 10)); }
  return res;
}
function ncdf(x) {                                                   // Normal cdf through erfc (Numerical Recipes, relative error < 1.2e-7)
  const z = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.5 * z), y = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? 1 - y / 2 : y / 2;
}
function nppf(p) {                                                   // Acklam's rational approximation
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
function lgamma(x) {
  const g = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
  let y = x, tmp = x + 5.5; tmp -= (x + 0.5) * Math.log(tmp); let s = 1.000000000190015;
  for (const c of g) s += c / ++y;
  return -tmp + Math.log(2.5066282746310005 * s / x);
}
function acf(x, L) {                                                 // as ct_models.acf: demeaned, divided by the sum of squares
  const m = mean(x), y = x.map(v => v - m); let dd = 0; for (const v of y) dd += v * v;
  const res = [];
  for (let k = 1; k <= L; k++) { let s = 0; for (let i = k; i < y.length; i++) s += y[i] * y[i - k]; res.push(s / dd); }
  return res;
}
function quantile(a, p) {                                            // numpy default (linear interpolation)
  const s = [...a].sort((x, y) => x - y), h = (s.length - 1) * p, lo = Math.floor(h), hi = Math.min(lo + 1, s.length - 1);
  return s[lo] + (h - lo) * (s[hi] - s[lo]);
}
const sd0 = a => { const m = mean(a); return Math.sqrt(sum(a.map(v => (v - m) ** 2)) / a.length); };
function polyfit1(x, y) {
  const mx = mean(x), my = mean(y); let sxy = 0, sxx = 0;
  for (let i = 0; i < x.length; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; }
  const b = sxy / sxx; return [b, my - b * mx];
}
function golden(f, lo, hi) {                                         // grid search, then golden-section refinement
  let best = lo, fb = Infinity; const n = 400;
  for (let i = 0; i <= n; i++) { const x = lo + (hi - lo) * i / n, v = f(x); if (v < fb) { fb = v; best = x; } }
  let a = Math.max(lo, best - (hi - lo) / n), b = Math.min(hi, best + (hi - lo) / n); const gr = (Math.sqrt(5) - 1) / 2;
  for (let it = 0; it < 60; it++) { const c = b - gr * (b - a), d = a + gr * (b - a); if (f(c) < f(d)) b = d; else a = c; }
  return (a + b) / 2;
}
const nf0 = (x, d) => nf(Math.abs(x) < 0.5 * Math.pow(10, -d) ? 0 : x, d);
const fmtInt = x => { const t = Math.round(x).toLocaleString('en-US'); return window.MFM_LANG === 'ro' ? t.replace(/,/g, '\u00a0') : t; };
const hband = (x, lo, hi, name, show) => [
  { x, y: hi, mode: 'lines', line: { width: 0 }, hoverinfo: 'skip', showlegend: false },
  { x, y: lo, mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: 'rgba(197,210,232,0.75)', name, showlegend: show !== false, hoverinfo: 'skip' }];

const SPR = D.sp.r, SPD = decodeDates(D.sp.start, D.sp.gaps), N = SPR.length;

// ================================================================= Donsker
const DK = (() => {
  const w = {};
  for (const [n, bits] of Object.entries(D.donsker.walks)) {
    const S = [0]; for (const b of bits) S.push(S[S.length - 1] + (b === '1' ? 1 : -1));
    const nn = +n; w[n] = { t: S.map((_, k) => k / nn), W: S.map(s => s / Math.sqrt(nn)), max: Math.max(...S) / Math.sqrt(nn) };
  }
  return w;
})();
function donsker() {
  const a = +$('dk-a').value, P = D.donsker; $('dk-a-v').textContent = nf(a, 2);
  const col = { 5: K.red, 50: K.amber, 5000: K.blue };
  plot('dk-paths', [
    ...['5', '50', '5000'].map(n => ({ x: DK[n].t, y: DK[n].W, mode: 'lines', line: { shape: 'hv', color: col[n], width: n === '5000' ? 1 : 1.6 }, name: 'n = ' + n,
      hovertemplate: 'n = ' + n + '<br>t %{x:.3f}<br>%{y:.3f}<extra></extra>' })),
    { x: [0, 1], y: [a, a], mode: 'lines', line: { color: K.navy, width: 1.5, dash: 'dot' }, name: 'Level a = ' + a.toFixed(2), hoverinfo: 'skip' }
  ], layout({ title: ttl('Scaled random walks'), xaxis: AX('Time t'), yaxis: AX('S⌊nt⌋ / √n'), legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const p = P.ns.map(n => { const c = P.counts[n], r = Math.sqrt(n); let k = 0; c.forEach((v, j) => { if (j / r > a) k += v; }); return k / P.M; });
  const se = p.map(v => 1.96 * Math.sqrt(v * (1 - v) / P.M)), exact = 2 * (1 - ncdf(a));
  plot('dk-p', [
    { x: P.ns, y: p, mode: 'lines+markers', name: 'Random walk, 20,000 paths (95% CI)', line: { color: K.blue, width: 1.6 }, marker: { size: 6, color: K.blue },
      error_y: { type: 'data', array: se, color: K.blue, thickness: 1.2, width: 3 }, hovertemplate: 'n = %{x}<br>P = %{y:.4f}<extra></extra>' },
    { x: [4, 2500], y: [exact, exact], mode: 'lines', name: 'Brownian limit: ' + exact.toFixed(4), line: { color: K.red, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl('A path functional converges too'), xaxis: AX('Number of steps n', { type: 'log', dtick: 1 }), yaxis: AX('P(max W_n(t) > a)'),
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const crossed = ['5', '50', '5000'].filter(n => DK[n].max > a).map(n => 'n = ' + n);
  out('dk-out', [T.dk(nf(a, 2), nf(exact, 4), nf(p[0], 4), nf(p[p.length - 1], 4), nf(exact - p[p.length - 1], 4)), T.dk2(crossed.length ? crossed.join(', ') : null)]);
}

// ================================================================= quadratic variation
const CUM = (() => { const c = []; let s = 0; for (const r of SPR) { s += r * r; c.push(s); } return c; })();
const YRS = SPD.map(d => (Date.parse(d) - Date.parse(SPD[0])) / 864e5 / 365.25);
const CRISES = { '2008': ['2008-09-01', '2009-03-31'], '2020': ['2020-02-20', '2020-04-30'] };
function quadVar() {
  const p = +$('qv-p').value, cr = $('qv-c').value, Q = D.qv; $('qv-p-v').textContent = nf(p, 1);
  const key = p.toFixed(1), ns = Q.ns, ez = Math.exp(p / 2 * Math.log(2) + lgamma((p + 1) / 2)) / Math.sqrt(Math.PI);
  const tr = [
    { x: ns, y: Q.sums['2.0'], mode: 'lines+markers', name: 'Quadratic variation Σ(ΔW)²', line: { color: K.blue, width: 1.8 }, marker: { size: 6 }, hovertemplate: 'n = %{x}<br>%{y:.3f}<extra></extra>' },
    { x: ns, y: Q.sums['1.0'], mode: 'lines+markers', name: 'Total variation Σ|ΔW|', line: { color: K.red, width: 1.8 }, marker: { size: 6, symbol: 'square' }, hovertemplate: 'n = %{x}<br>%{y:.1f}<extra></extra>' },
    { x: ns, y: ns.map(n => Math.sqrt(2 * n / Math.PI)), mode: 'lines', name: '√(2n/π)', line: { color: K.navy, width: 1.2, dash: 'dot' }, hoverinfo: 'skip' },
    { x: [ns[0], ns[ns.length - 1]], y: [1, 1], mode: 'lines', name: 'T = 1', line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' }];
  if (key !== '1.0' && key !== '2.0') tr.push(
    { x: ns, y: Q.sums[key], mode: 'lines+markers', name: 'Σ|ΔW|^p, p = ' + p.toFixed(1), line: { color: K.amber, width: 1.8 }, marker: { size: 7, symbol: 'diamond' }, hovertemplate: 'n = %{x}<br>%{y:.4g}<extra></extra>' },
    { x: ns, y: ns.map(n => Math.pow(n, 1 - p / 2) * ez), mode: 'lines', name: 'Mean n^(1−p/2) E|Z|^p', line: { color: K.amber, width: 1.2, dash: 'dot' }, hoverinfo: 'skip' });
  plot('qv-grid', tr, layout({ title: ttl('One Brownian path, finer and finer grids'), xaxis: AX('Number of intervals n on [0, 1]', { type: 'log', dtick: 1 }), yaxis: AX('', { type: 'log', dtick: 1, exponentformat: 'power' }),
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const lin = YRS.map(y => CUM[N - 1] * y / YRS[N - 1]), shapes = [];
  let share = null;
  if (cr !== 'none') {
    const [a, b] = CRISES[cr]; shapes.push({ type: 'rect', xref: 'x', yref: 'paper', x0: a, x1: b, y0: 0, y1: 1, fillcolor: 'rgba(205,0,0,0.15)', line: { width: 0 }, layer: 'below' });
    let q = 0, k = 0; for (let i = 0; i < N; i++) if (SPD[i] >= a && SPD[i] <= b) { q += SPR[i] ** 2; k++; }
    share = [k / N, q / CUM[N - 1]];
  }
  plot('qv-sp', [
    { x: SPD, y: CUM, mode: 'lines', name: 'S&P 500: Σ r²', line: { color: K.blue, width: 1.6 }, hovertemplate: '%{x}<br>%{y:.3f}<extra></extra>' },
    { x: SPD, y: lin, mode: 'lines', name: 'GBM: σ²t (same end point)', line: { color: K.orange, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Realised quadratic variation, 1990-2026'), xaxis: AX(''), yaxis: AX('Cumulative squared returns'), shapes,
    legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top', font: { size: 11 } } }));
  const last = Q.sums[key][ns.length - 1], items = [T.qv(nf(p, 1), last < 100 ? nf(last, 3) : fmtInt(last), p < 2 - 1e-9 ? 'up' : p > 2 + 1e-9 ? 'down' : 'one')];
  items.push(share ? T.qv2(cr, pct(share[0], 1), pct(share[1], 1)) : T.qv3(nf(CUM[N - 1], 3), nf(YRS[N - 1], 1), pct(Math.sqrt(CUM[N - 1] / YRS[N - 1]), 1)));
  out('qv-out', items);
}

// ================================================================= drift precision
const C1 = [0], C2 = [0]; for (const r of SPR) { C1.push(C1[C1.length - 1] + r); C2.push(C2[C2.length - 1] + r * r); }
function drift() {
  const yrs = +$('dp-w').value, w = 252 * yrs, G = D.gbm; $('dp-w-v').textContent = yrs;
  const Ty = range(1, 100, 99 / 199), lab = { sp500: 'S&P 500', btc: 'Bitcoin' }, col = { sp500: K.blue, btc: K.amber };
  const tr = [];
  for (const k of ['sp500', 'btc']) {
    const s = G[k].sigma;
    tr.push({ x: Ty, y: Ty.map(t => 196 * s / Math.sqrt(t)), mode: 'lines', name: `${lab[k]} (σ = ${(100 * s).toFixed(0)}%)`, line: { color: col[k], width: 2 }, hovertemplate: 'T = %{x:.0f} years<br>±%{y:.1f} pp<extra></extra>' });
    tr.push({ x: [yrs], y: [196 * s / Math.sqrt(yrs)], mode: 'markers', showlegend: false, marker: { color: col[k], size: 10, line: { color: '#fff', width: 1.5 } }, hovertemplate: 'T = %{x} years<br>±%{y:.1f} pp<extra></extra>' });
  }
  tr.push({ x: [1, 100], y: [1, 1], mode: 'lines', name: '±1 percentage point', line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' });
  plot('dp-ci', tr, layout({ title: ttl('Drift precision depends only on T: 1.96 σ/√T'), xaxis: AX('Years of data T'), yaxis: AX('Half-width of 95% CI (pp)', { type: 'log', dtick: 1, exponentformat: 'power' }),
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const x = [], m = [], s = [], lo = [], hi = [];
  for (let e = w; e <= N; e++) {
    const s1 = C1[e] - C1[e - w], s2 = C2[e] - C2[e - w], mu = s1 / w, v = (s2 - s1 * s1 / w) / (w - 1);
    const mm = mu / DT, ss = Math.sqrt(v / DT), ci = 1.96 * ss / Math.sqrt(w * DT);
    x.push(SPD[e - 1]); m.push(100 * mm); s.push(100 * ss); lo.push(100 * (mm - ci)); hi.push(100 * (mm + ci));
  }
  plot('dp-roll', [
    ...hband(x, lo, hi, '95% CI for the log drift'),
    { x, y: m, mode: 'lines', name: 'Log drift m̂ (% p.a.)', line: { color: K.blue, width: 1.6 }, hovertemplate: '%{x}<br>m̂ %{y:.1f}%<extra></extra>' },
    { x, y: s, mode: 'lines', name: 'Volatility σ̂ (% p.a.)', line: { color: K.red, width: 1.6 }, hovertemplate: '%{x}<br>σ̂ %{y:.1f}%<extra></extra>' }
  ], layout({ title: ttl(`S&P 500, rolling ${yrs}-year windows`), xaxis: AX('', { range: ['1990-01-01', '2026-12-31'] }), yaxis: AX('% p.a.', { zeroline: true, zerolinecolor: K.navy }),
    legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top', font: { size: 11 } } }));
  let iMin = 0, iMax = 0; m.forEach((v, i) => { if (v < m[iMin]) iMin = i; if (v > m[iMax]) iMax = i; });
  const half = median(hi.map((h, i) => (h - lo[i]) / 2));
  out('dp-out', [T.dp(yrs, nf(1.96 * 100 * G.sp500.sigma / Math.sqrt(yrs), 1), nf(1.96 * 100 * G.btc.sigma / Math.sqrt(yrs), 1)),
    T.dp2(nf(m[iMin], 1), x[iMin].slice(0, 7), nf(m[iMax], 1), x[iMax].slice(0, 7), nf(half, 1), nf(Math.min(...s), 1), nf(Math.max(...s), 1))]);
}

// ================================================================= GBM against the data
const Z = (() => { const m = mean(SPR), s = sd0(SPR); return SPR.map(r => (r - m) / s); })();
const ZS = [...Z].sort((a, b) => a - b), QN = ZS.map((_, i) => nppf((i + 0.5) / N));
const ACF_DATA = { abs: acf(SPR.map(Math.abs), 50), sq: acf(SPR.map(r => r * r), 50), raw: acf(SPR, 50) };
function gbmData() {
  const k = +$('gd-k').value, ser = $('gd-s').value; $('gd-k-v').textContent = nf(k, 2);
  const inn = { x: [], y: [] }, ext = { x: [], y: [] };
  ZS.forEach((z, i) => { const o = Math.abs(z) > k ? ext : inn; o.x.push(QN[i]); o.y.push(z); });
  plot('gd-qq', [
    { x: inn.x, y: inn.y, type: 'scatter', mode: 'markers', name: 'S&P 500 daily log returns, standardised', marker: { color: K.blue, size: 4 }, hovertemplate: 'Normal %{x:.2f}<br>sample %{y:.2f}<extra></extra>' },
    { x: ext.x, y: ext.y, type: 'scatter', mode: 'markers', name: `Beyond ±${k.toFixed(2)} s.d.`, marker: { color: K.red, size: 5 }, hovertemplate: 'Normal %{x:.2f}<br>sample %{y:.2f}<extra></extra>' },
    { x: [-5, 5], y: [-5, 5], mode: 'lines', name: '45-degree line (Normal distribution)', line: { color: K.navy, width: 1.2 }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Tails: returns are not Normal'), xaxis: AX('Quantiles of the standard Normal distribution'), yaxis: AX('Sample quantiles'),
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const lags = range(1, 50, 1), B = D.band[ser], lab = { abs: '|r|', sq: 'r²', raw: 'r' }[ser];
  plot('gd-acf', [
    ...hband(lags, B.lo, B.hi, 'GBM: 95% range of 200 simulations'),
    { x: lags, y: ACF_DATA[ser], type: 'bar', name: 'S&P 500: ACF of ' + lab, marker: { color: K.blue }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl(`Clustering: ACF of ${lab}`), xaxis: AX('Lag (trading days)'), yaxis: AX(''), bargap: 0.3,
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const nExp = N * 2 * (1 - ncdf(k)), bandMax = Math.max(...B.hi.map(Math.abs), ...B.lo.map(Math.abs));
  out('gd-out', [T.gd(nf(k, 2), ext.x.length, nExp < 10 ? nf(nExp, 2) : nf(nExp, 0)), T.gd2(lab, nf(ACF_DATA[ser][0], 2), nf(ACF_DATA[ser][49], 2), nf(bandMax, 3))]);
}

// ================================================================= Vasicek on the 3-month bill rate
const TBD = decodeDates(D.tb.start, D.tb.gaps), TBY = D.tb.y, TBYR = TBD.map(d => +d.slice(0, 4));
function ouMle(x) {
  const n = x.length - 1; let sz = 0, sy = 0, szz = 0, szy = 0;
  for (let i = 0; i < n; i++) { const z = x[i], y = x[i + 1]; sz += z; sy += y; szz += z * z; szy += z * y; }
  const det = n * szz - sz * sz, b = (n * szy - sz * sy) / det, a = (sy - b * sz) / n;
  let sse = 0; for (let i = 0; i < n; i++) { const e = x[i + 1] - a - b * x[i]; sse += e * e; }
  const s2 = sse / n, varB = s2 * n / det, kappa = -Math.log(b) / DT, theta = a / (1 - b), sigma = Math.sqrt(s2 * 2 * kappa / (1 - b * b));
  return { n, a, b, kappa, theta, sigma, se_kappa: Math.sqrt(varB) / (b * DT), half_life: Math.log(2) / kappa, stat_sd: sigma / Math.sqrt(2 * kappa) };
}
function vasicek() {
  let a = +$('va-a').value, b = +$('va-b').value;
  if (b < a + 5) { if (this === $('va-a')) { b = Math.min(a + 5, 2026); $('va-b').value = b; } else { a = Math.max(b - 5, 1954); $('va-a').value = a; } }
  $('va-a-v').textContent = a; $('va-b-v').textContent = b;
  const idx = []; TBYR.forEach((y, i) => { if (y >= a && y <= b) idx.push(i); });
  const f = ouMle(idx.map(i => TBY[i] / 100)), d0 = TBD[idx[0]], d1 = TBD[idx[idx.length - 1]], ok = f.kappa > 0;
  const shapes = ok ? [{ type: 'rect', xref: 'x', yref: 'y', x0: d0, x1: d1, y0: 100 * (f.theta - 2 * f.stat_sd), y1: 100 * (f.theta + 2 * f.stat_sd), fillcolor: 'rgba(197,210,232,0.45)', line: { width: 0 }, layer: 'below' }] : [];
  const tr = [{ x: TBD, y: TBY, mode: 'lines', name: '3-month Treasury bill rate (% p.a.)', line: { color: K.blue, width: 1 }, hovertemplate: '%{x}<br>%{y:.2f}%<extra></extra>' }];
  if (ok) tr.push({ x: [d0, d1], y: [100 * f.theta, 100 * f.theta], mode: 'lines', name: `Vasicek θ̂ = ${(100 * f.theta).toFixed(2)}%`, line: { color: K.red, width: 1.6, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [null], y: [null], mode: 'markers', marker: { symbol: 'square', size: 12, color: 'rgba(197,210,232,0.8)' }, name: 'θ̂ ± 2 stationary s.d.', hoverinfo: 'skip' });
  plot('va-rate', tr, layout({ title: ttl('Short rate, 1954-2026'), xaxis: AX(''), yaxis: AX('% p.a.', { zeroline: true, zerolinecolor: K.navy }), shapes,
    legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top', font: { size: 11 } } }));
  const V = D.vasicek, labs = Object.keys(V), cols = [K.blue, K.amber, K.forest, K.purple];
  const mine = `${a}-${b}`, pts = labs.map((l, i) => ({ x: [l], y: [V[l].kappa], mode: 'markers', marker: { color: cols[i], size: 11 }, showlegend: false,
    error_y: { type: 'data', array: [1.96 * V[l].se_kappa], color: cols[i], thickness: 1.5, width: 6 }, hovertemplate: `${l}<br>κ̂ %{y:.3f}<extra></extra>` }));
  pts.push({ x: ['Selected ' + mine], y: [f.kappa], mode: 'markers', name: 'Selected sample', marker: { color: K.red, size: 12, symbol: 'diamond' }, showlegend: false,
    error_y: { type: 'data', array: [1.96 * f.se_kappa], color: K.red, thickness: 1.5, width: 6 }, hovertemplate: `${mine}<br>κ̂ %{y:.3f}<extra></extra>` });
  plot('va-k', pts, layout({ title: ttl('Speed of mean reversion'), xaxis: AX('', { type: 'category', tickfont: { size: 10, color: K.navy } }), yaxis: AX('κ̂ with 95% CI (per year)', { zeroline: true, zerolinecolor: K.navy }),
    margin: { l: 56, r: 12, t: 30, b: 60 } }));
  out('va-out', [T.va(a, b, nf(f.kappa, 3), nf(f.se_kappa, 3), ok ? nf(f.half_life, 1) : null, nf(f.b, 5)),
    ok ? T.va2(nf(100 * f.theta, 2), nf(100 * f.sigma, 2), nf(100 * f.stat_sd, 2), f.kappa - 1.96 * f.se_kappa <= 0) : T.va3(nf(100 * f.sigma, 2))]);
}

// ================================================================= Merton densities
const BTR = D.btc.r;
function poisW(lt, kmax) { const w = []; let p = Math.exp(-lt); for (let k = 0; k <= kmax; k++) { w.push(p); p *= lt / (k + 1); } return w; }
function mertonDens(x, dt, m, s, lam, mj, sj) {
  const w = poisW(lam * dt, 12); let d = 0;
  for (let k = 0; k <= 12; k++) { const mu = m * dt + k * mj, v = s * s * dt + k * sj * sj; d += w[k] * Math.exp(-0.5 * (x - mu) ** 2 / v) / Math.sqrt(2 * Math.PI * v); }
  return Math.max(d, 1e-300);
}
function hist(r, nb) {
  let lo = Infinity, hi = -Infinity; for (const v of r) { if (v < lo) lo = v; if (v > hi) hi = v; }
  const wd = (hi - lo) / nb, c = new Array(nb).fill(0);
  for (const v of r) c[Math.min(Math.floor((v - lo) / wd), nb - 1)]++;
  return { lo, hi, wd, h: c.map(k => k / (r.length * wd)), mid: c.map((_, i) => lo + (i + 0.5) * wd) };
}
const MJ = { sp500: { r: SPR, dt: 1 / 252, H: hist(SPR, 120), name: 'S&P 500' }, btc: { r: BTR, dt: 1 / 365, H: hist(BTR, 120), name: 'Bitcoin' } };
function mertonOne(key, mult, id) {
  const A = MJ[key], P = D.merton[key], dt = A.dt, J2 = P.mu_j ** 2 + P.s_j ** 2, tot = P.sigma ** 2 + P.lam * J2;
  const lam = mult * P.lam, sig = Math.sqrt(Math.max(tot - lam * J2, 1e-10)), m = P.m + (P.lam - lam) * P.mu_j;
  const H = A.H, ok = H.h.map(v => v > 0), xs = range(0, 799, 1).map(i => H.lo + (H.hi - H.lo) * i / 799);
  const mu0 = mean(A.r), s0 = sd0(A.r);
  const hpos = H.h.filter(v => v > 0), ymin = Math.min(...hpos) / 3, ymax = Math.max(...H.h) * 3;
  plot(id, [
    { x: H.mid.filter((_, i) => ok[i]), y: hpos, mode: 'markers', name: 'Data (histogram)', marker: { color: K.blue, size: 6 }, hovertemplate: 'r %{x:.3f}<br>density %{y:.3g}<extra></extra>' },
    { x: xs, y: xs.map(x => Math.exp(-0.5 * ((x - mu0) / s0) ** 2) / (s0 * Math.sqrt(2 * Math.PI))), mode: 'lines', name: 'Normal distribution (GBM)', line: { color: K.orange, width: 1.8 }, hoverinfo: 'skip' },
    { x: xs, y: xs.map(x => mertonDens(x, dt, m, sig, lam, P.mu_j, P.s_j)), mode: 'lines', name: 'Merton jump-diffusion', line: { color: K.red, width: 1.8 }, hovertemplate: 'r %{x:.3f}<br>Merton %{y:.3g}<extra></extra>' }
  ], layout({ title: ttl(A.name), xaxis: AX('Daily log return'), yaxis: AX('Density', { type: 'log', range: [Math.log10(ymin), Math.log10(ymax)], dtick: 1, exponentformat: 'power' }),
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  let ll = 0; for (const x of A.r) ll += Math.log(mertonDens(x, dt, m, sig, lam, P.mu_j, P.s_j));
  const k2 = sig * sig * dt + lam * dt * J2, k4 = lam * dt * (P.mu_j ** 4 + 6 * P.mu_j ** 2 * P.s_j ** 2 + 3 * P.s_j ** 4);
  return T.mj(A.name, nf(lam, 0), pct(sig, 1), pct(lam * J2 / tot, 0), nf(k4 / (k2 * k2), 1), nf(P.data_exkurt, 1), fmtInt(ll), fmtInt(P.loglik), fmtInt(P.ll_gbm));
}
function merton() {
  const mult = +$('mj-l').value; $('mj-l-v').textContent = nf(mult, 2) + ' × λ̂';
  out('mj-out', [mertonOne('sp500', mult, 'mj-sp'), mertonOne('btc', mult, 'mj-btc')]);
}

// ================================================================= models against the data
const ACF_ABS = ACF_DATA.abs;
function modelsData() {
  const k = +$('mv-k').value, show = $('mv-m').value, M = D.models, Cd = D.compare.Data, names = ['GBM', 'Merton', 'Heston'];
  $('mv-k-v').textContent = k;
  const lags = range(1, 50, 1), tr = [];
  if (show !== 'none') M[show].acf.slice(0, k).forEach((a, i) => tr.push({ x: lags, y: a, mode: 'lines', line: { color: MODEL_COL[show], width: 0.6 }, opacity: 0.25, showlegend: false, hoverinfo: 'skip' }));
  tr.push({ x: lags, y: ACF_ABS, mode: 'lines', name: 'S&P 500 data', line: { color: K.blue, width: 2.6 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' });
  for (const m of names) tr.push({ x: lags, y: lags.map((_, j) => median(M[m].acf.slice(0, k).map(a => a[j]))), mode: 'lines', name: m, line: { color: MODEL_COL[m], width: 1.8 }, hovertemplate: m + ', lag %{x}: %{y:.3f}<extra></extra>' });
  plot('mv-acf', tr, layout({ title: ttl(`ACF of |r| (median of ${k} simulations)`), xaxis: AX('Lag (trading days)'), yaxis: AX('', { zeroline: true, zerolinecolor: K.navy }),
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const bars = (id, key, title) => {
    const st = names.map(m => { const v = M[m][key].slice(0, k), md = median(v); return { md, lo: md - quantile(v, 0.05), hi: quantile(v, 0.95) - md }; });
    plot(id, [{ x: ['Data', ...names], y: [Cd[key], ...st.map(s => s.md)], type: 'bar', marker: { color: ['Data', ...names].map(n => MODEL_COL[n]) }, showlegend: false,
      error_y: { type: 'data', symmetric: false, array: [0, ...st.map(s => s.hi)], arrayminus: [0, ...st.map(s => s.lo)], color: K.navy, thickness: 1.5, width: 5 },
      hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }], layout({ title: ttl(title), xaxis: AX(''), yaxis: AX(''), bargap: 0.35 }));
    return st;
  };
  const ku = bars('mv-ku', 'exkurt', 'Excess kurtosis'), hi = bars('mv-hi', 'hill', 'Hill statistic, k = 5% of n');
  const geK = names.map(m => M[m].exkurt.slice(0, k).filter(v => v >= Cd.exkurt).length), a1 = names.map(m => median(M[m].acf.slice(0, k).map(a => a[0])));
  out('mv-out', [T.mv(k, nf(Cd.exkurt, 2), ku.map(s => nf0(s.md, 2)), geK),
    T.mv2(nf(Cd.hill, 2), hi.map(s => nf(s.md, 2))), T.mv3(nf(ACF_ABS[0], 2), a1.map(v => nf0(v, 2)))]);
}

// ================================================================= rough volatility, SPY
const RX = D.rough.x, RN = RX.length;
const VG = range(1, 30, 1).map(k => { let s = 0; for (let i = k; i < RN; i++) s += (RX[i] - RX[i - k]) ** 2; return s / (RN - k); });
const RHO = acf(RX, 100);
const cauchy = (h, a, b) => Math.pow(1 + Math.pow(Math.abs(h), 2 * a + 1), -b / (2 * a + 1));
function rough() {
  const m = +$('ro-m').value, H = +$('ro-H').value, R = D.rough; $('ro-m-v').textContent = m; $('ro-H-v').textContent = H;
  const ks = range(1, 30, 1), lk = ks.slice(0, m).map(Math.log), [a1] = polyfit1(lk, VG.slice(0, m).map(Math.log)), aOls = (a1 - 1) / 2;
  const c0 = Math.exp(mean(lk.map((l, i) => Math.log(VG[i]) - a1 * l))), [b0, b1, an] = R.nlls_m15;
  plot('ro-vg', [
    { x: ks, y: VG, mode: 'markers', name: 'Empirical variogram of log σ̂', marker: { color: K.blue, size: 7 }, hovertemplate: 'k = %{x}<br>%{y:.3f}<extra></extra>' },
    { x: ks, y: ks.map(k => c0 * Math.pow(k, a1)), mode: 'lines', name: `OLS, k = 1..${m}: α̂ = ${aOls.toFixed(2)}`, line: { color: K.red, width: 1.8 }, hoverinfo: 'skip' },
    { x: ks, y: ks.map(k => b0 + b1 * Math.pow(k, 2 * an + 1)), mode: 'lines', name: `NLLS, m = 15; α̂* = ${R.alpha_nlls.toFixed(2)}`, line: { color: K.forest, width: 1.8, dash: 'dash' }, hoverinfo: 'skip' },
    { x: ks.slice(0, 10), y: ks.slice(0, 10).map(k => VG[0] * k), mode: 'lines', name: 'Brownian roughness, α = 0', line: { color: K.orange, width: 1.5, dash: 'dot' }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Roughness: variogram of log-volatility'), xaxis: AX('Lag k (trading days)', { type: 'log', tickvals: [1, 2, 5, 10, 20, 30] }),
    yaxis: AX('γ̂₂(k)', { type: 'log', tickvals: [0.1, 0.2, 0.5, 1.0], range: [-1, 0.15] }), legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  const hh = range(1, H, 1), lr = RHO.slice(0, H).map(Math.log);
  const bPlain = golden(b => sum(hh.map((h, i) => (RHO[i] - cauchy(h, aOls, b)) ** 2)), 0, 5);
  const cOf = b => Math.min(0, mean(hh.map((h, i) => lr[i] - Math.log(cauchy(h, R.alpha_nlls, b)))));
  const bStar = golden(b => { const c = cOf(b); return sum(hh.map((h, i) => (lr[i] - c - Math.log(cauchy(h, R.alpha_nlls, b))) ** 2)); }, 0, 5), cStar = cOf(bStar);
  const [sl, ic] = polyfit1(hh, lr), lamOU = -sl, hl = Math.log(2) / lamOU, lags = range(1, 100, 1);
  plot('ro-acf', [
    { x: lags, y: RHO, mode: 'lines', name: 'Empirical ACF of log σ̂', line: { color: K.blue, width: 2 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lags, y: lags.map(h => Math.exp(cStar) * cauchy(h, R.alpha_nlls, bStar)), mode: 'lines', name: `Cauchy class, noise-robust: β̂* = ${bStar.toFixed(2)}`, line: { color: K.purple, width: 1.8 }, hoverinfo: 'skip' },
    { x: lags, y: lags.map(h => Math.exp(ic - lamOU * h)), mode: 'lines', name: `Exponential decay (OU): half-life ${hl.toFixed(0)} days`, line: { color: K.amber, width: 1.8, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Persistence: ACF of log-volatility'), xaxis: AX('Lag h (trading days)'), yaxis: AX('', { range: [-0.1, 1.0], zeroline: true, zerolinecolor: K.navy }),
    shapes: [{ type: 'line', xref: 'x', yref: 'paper', x0: H, x1: H, y0: 0, y1: 1, line: { color: K.navy, width: 1, dash: 'dot' } }],
    annotations: [{ x: H, y: 0.95, xref: 'x', yref: 'y', text: `fit on lags 1..${H}`, showarrow: false, xanchor: 'left', xshift: 4, font: { size: 11, color: K.navy } }],
    legend: { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } } }));
  out('ro-out', [T.ro(m, nf(aOls, 3), nf(R.alpha_nlls, 2)), T.ro2(H, nf(bPlain, 2), nf(bStar, 2), nf(hl, 1), nf(RHO[99], 2), nf(Math.exp(-lamOU * 100), 3))]);
}

// ================================================================= drift bursts, SPY (second case study)
const DBD = D.drift_burst, DB_DT = 5, DB_START = 6;
function dbT(r, h) {                                                 // as generate_all_charts.drift_burst_t, one day
  const hs = 5 * h, T = r.map(() => null);
  for (let j = DB_START - 1; j < r.length; j++) {
    let num = 0, sw2 = 0, s2n = 0, sws = 0;
    for (let k = 0; k <= j; k++) {
      const lag = (j - k + 1) * DB_DT, w = Math.exp(-lag / h), ws = Math.exp(-lag / hs);
      num += w * r[k]; sw2 += w * w; s2n += ws * r[k] * r[k]; sws += ws;
    }
    T[j] = num / Math.sqrt(s2n / (sws * DB_DT) * sw2 * DB_DT);
  }
  return T;
}
const hhmm = j => { const m = 570 + 5 * (j + 1); return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); };
function driftBurst() {
  const h = +$('db-h').value, day = $('db-d').value, B = DBD.by_h[String(h)], c = B.c95, dd = DBD.days[day];
  $('db-h-v').textContent = h;
  const tt = dd.r.map((_, j) => hhmm(j)), Tt = dbT(dd.r, h);
  let jm = DB_START - 1; for (let j = DB_START - 1; j < Tt.length; j++) if (Math.abs(Tt[j]) > Math.abs(Tt[jm])) jm = j;
  const leg = { orientation: 'h', x: 0, y: -0.22, yanchor: 'top', font: { size: 11 } };
  plot('db-day', [
    { x: tt, y: Tt, mode: 'lines', name: 'T_t (left axis)', line: { color: K.red, width: 1.8 }, hovertemplate: '%{x}: T = %{y:.2f}<extra></extra>' },
    { x: tt, y: dd.close, mode: 'lines', name: 'SPY close (right axis, USD)', yaxis: 'y2', line: { color: K.blue, width: 1.5 }, hovertemplate: '%{x}: %{y:.2f} USD<extra></extra>' },
    { x: [tt[0], tt[tt.length - 1]], y: [c, c], mode: 'lines', name: `±${c.toFixed(2)}: 5% per day under the null`, line: { color: K.navy, width: 1, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [tt[0], tt[tt.length - 1]], y: [-c, -c], mode: 'lines', showlegend: false, line: { color: K.navy, width: 1, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`SPY, ${day}`), xaxis: AX('', { tickvals: ['10:00', '12:00', '14:00', '16:00'], tickangle: 0 }), yaxis: AX('T_t', { range: [-4.6, 4.6] }),
    yaxis2: AX('', { overlaying: 'y', side: 'right', showgrid: false }), legend: leg }));
  const G = B.grid, cl = a => a.map(v => Math.max(v, 0.8));
  plot('db-cnt', [
    { x: G, y: cl(B.null_lo), mode: 'lines', line: { width: 0, color: K.band }, showlegend: false, hoverinfo: 'skip' },
    { x: G, y: cl(B.null_hi), mode: 'lines', fill: 'tonexty', fillcolor: K.band, line: { width: 0, color: K.band }, name: 'Sign-flip null, 1%-99%', hoverinfo: 'skip' },
    { x: G, y: cl(B.null_mean), mode: 'lines', name: 'Sign-flip null, mean', line: { color: K.orange, width: 1.8, dash: 'dash' }, hovertemplate: 'c = %{x:.2f}: %{y:.1f} days<extra></extra>' },
    { x: G, y: cl(B.data), mode: 'lines', name: `SPY, ${DBD.ref.n_days} days`, line: { color: K.blue, width: 2.2 }, hovertemplate: 'c = %{x:.2f}: %{y} days<extra></extra>' }
  ], layout({ title: ttl('Days with max |T_t| > c'), xaxis: AX('Critical value c'), yaxis: AX('', { type: 'log', range: [Math.log10(0.8), Math.log10(2000)], tickvals: [1, 10, 100, 1000] }),
    shapes: [{ type: 'line', xref: 'x', yref: 'paper', x0: c, x1: c, y0: 0, y1: 1, line: { color: K.navy, width: 1, dash: 'dot' } }], legend: leg }));
  const x = B.rm, y = B.rp, [b, a] = polyfit1(x, y), rev = x.filter((v, i) => Math.sign(v) !== Math.sign(y[i])).length / x.length;
  const xs = [Math.min(...x), Math.max(...x)];
  plot('db-rev', [
    { x, y, mode: 'markers', name: `${x.length} days, reversal in ${(100 * rev).toFixed(0)}%`, marker: { color: K.blue, size: 6, opacity: 0.8 }, hovertemplate: 'before: %{x:.1f} bp<br>after: %{y:.1f} bp<extra></extra>' },
    { x: xs, y: xs.map(v => a + b * v), mode: 'lines', name: `OLS slope ${b.toFixed(2)}`, line: { color: K.red, width: 1.8 }, hoverinfo: 'skip' }
  ], layout({ title: ttl('After the burst'), xaxis: AX(`${h} min to the peak (bp)`, { zeroline: true, zerolinecolor: K.navy }),
    yaxis: AX(`Next ${h} min (bp)`, { zeroline: true, zerolinecolor: K.navy }), legend: leg }));
  const t = B.tests.c95;
  out('db-out', [T.db(h, 5 * h, nf(c, 2), t.days, nf(t.null_mean, 1), t.null_max, nf(t.p, 3), nf(B.jump_bound, 2)),
    T.db2(day, nf(Tt[jm], 2), hhmm(jm)),
    T.db3(x.length, nf(100 * rev, 0), nf(b, 2), B.n_events_neg, B.n_events, B.n_close, h)]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['dk-a'], donsker); P('dk-play', 'dk-a', range(0.25, 2.5, 0.05), 160);
  on(['qv-p', 'qv-c'], quadVar); P('qv-play', 'qv-p', range(0.5, 3, 0.1), 350);
  on(['dp-w'], drift); P('dp-play', 'dp-w', range(1, 20, 1), 500);
  on(['gd-k', 'gd-s'], gbmData); P('gd-play', 'gd-k', range(2, 6, 0.25), 450);
  ['va-a', 'va-b'].forEach(id => $(id).addEventListener('input', vasicek)); P('va-play', 'va-b', range(1964, 2026, 1), 220);
  on(['mj-l'], merton); P('mj-play', 'mj-l', range(0, 1.15, 0.05), 300);
  on(['mv-k', 'mv-m'], modelsData); P('mv-play', 'mv-k', range(1, 100, 1), 90);
  on(['ro-m', 'ro-H'], rough); P('ro-play', 'ro-H', range(4, 60, 2), 300);
  on(['db-h', 'db-d'], driftBurst); P('db-play', 'db-h', range(5, 60, 5), 900);
  const PFX = { 'donsker': 'dk', 'quadratic-variation': 'qv', 'drift-precision': 'dp', 'gbm-vs-data': 'gd', 'vasicek': 'va',
    'merton-density': 'mj', 'models-vs-data': 'mv', 'rough-volatility': 'ro', 'drift-burst': 'db' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  donsker(); quadVar(); drift(); gbmData(); vasicek(); merton(); modelsData(); rough(); driftBurst();
}
window.CH11 = { ouMle, acf, mertonDens, ncdf, nppf, TBD, TBY, donsker, quadVar, drift, gbmData, vasicek, merton, modelsData, rough, dbT, driftBurst };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

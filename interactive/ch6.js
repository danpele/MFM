// Chapter 6 interactive page: one block per chart slide, computed in the browser from ch6_data.js.
(function () {
'use strict';
const D = window.CH6_DATA;
const { rng, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH6_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  navy: '#1F2A44', band: '#C5D2E8' };
const FAM = ['gaussian', 't', 'clayton', 'gumbel', 'frank'];
const FAM_LAB = { gaussian: 'Gaussian', t: 'Student t', clayton: 'Clayton', gumbel: 'Gumbel', frank: 'Frank' };
const FAM_COL = { gaussian: K.blue, t: K.red, clayton: K.green, gumbel: K.amber, frank: K.purple };
const CRISES = [['2008-09-15', '2009-03-31'], ['2020-02-20', '2020-04-30'], ['2022-01-03', '2022-10-31']];
const crisisShapes = () => CRISES.map(([a, b]) => ({ type: 'rect', xref: 'x', yref: 'paper', x0: a, x1: b, y0: 0, y1: 1, fillcolor: K.band, opacity: 0.5, line: { width: 0 }, layer: 'below' }));
const zero = () => hline(0, K.navy);
const Q975 = 1.959963984540054;
function LY(extra) {                 // shared layout; legend in plot order, lower when the x axis has a title
  const l = layout(extra), xt = l.xaxis && l.xaxis.title && l.xaxis.title.text;
  l.legend = Object.assign({}, layout().legend, { traceorder: 'normal' }, xt ? { y: -0.3 } : {}, (extra || {}).legend || {});
  return l;
}

// ---------------------------------------------------------------- dates (days since 1970-01-01, delta-encoded)
const DAY = 864e5;
const iso = d => new Date(d * DAY).toISOString().slice(0, 10);
const cum = a => { const r = new Array(a.length); let s = 0; for (let i = 0; i < a.length; i++) { s += a[i]; r[i] = s; } return r; };
const dates = o => (o._d || (o._d = cum(o.t).map(iso)));
const fd = s => T.date(new Date(s + 'T00:00:00Z'));
const addDays = (s, k) => iso(Math.round(Date.parse(s + 'T00:00:00Z') / DAY) + k);
function firstAt(d, s) { let lo = 0, hi = d.length; while (lo < hi) { const m = (lo + hi) >> 1; if (d[m] < s) lo = m + 1; else hi = m; } return lo; }
function cols(P, unit) {             // panel {t, cols, v} -> {d, x: {col: array}}
  if (!P._x) { P._x = {}; P.cols.forEach(c => (P._x[c] = P.v[c].map(v => v * unit))); }
  return { d: dates(P), x: P._x };
}

// ---------------------------------------------------------------- statistics
const meanA = (a, i0 = 0, i1 = a.length) => { let s = 0; for (let i = i0; i < i1; i++) s += a[i]; return s / (i1 - i0); };
function varA(a, i0 = 0, i1 = a.length) { const m = meanA(a, i0, i1); let s = 0; for (let i = i0; i < i1; i++) s += (a[i] - m) ** 2; return s / (i1 - i0 - 1); }
const sdA = (a, i0, i1) => Math.sqrt(varA(a, i0, i1));
function corr(x, y, i0 = 0, i1 = x.length) {
  const mx = meanA(x, i0, i1), my = meanA(y, i0, i1); let sxx = 0, syy = 0, sxy = 0;
  for (let i = i0; i < i1; i++) { const a = x[i] - mx, b = y[i] - my; sxx += a * a; syy += b * b; sxy += a * b; }
  return sxy / Math.sqrt(sxx * syy);
}
const corrIdx = (x, y, idx) => corr(idx.map(i => x[i]), idx.map(i => y[i]));
function rollCorr(x, y, m) {          // pandas Series.rolling(m).corr
  const n = x.length, r = new Array(n).fill(NaN); let sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0;
  for (let i = 0; i < n; i++) {
    sx += x[i]; sy += y[i]; sxx += x[i] * x[i]; syy += y[i] * y[i]; sxy += x[i] * y[i];
    if (i >= m) { const a = x[i - m], b = y[i - m]; sx -= a; sy -= b; sxx -= a * a; syy -= b * b; sxy -= a * b; }
    if (i >= m - 1) r[i] = (sxy - sx * sy / m) / Math.sqrt((sxx - sx * sx / m) * (syy - sy * sy / m));
  }
  return r;
}
const fisherCI = (r, n) => { const z = Math.atanh(r), s = Q975 / Math.sqrt(n - 3); return [Math.tanh(z - s), Math.tanh(z + s)]; };
function quantile(a, q) {            // numpy default (linear interpolation)
  const b = Float64Array.from(a).sort(), h = (b.length - 1) * q, lo = Math.floor(h);
  return lo + 1 < b.length ? b[lo] + (h - lo) * (b[lo + 1] - b[lo]) : b[lo];
}
const finite = a => a.filter(v => Number.isFinite(v));
const nanMean = a => { const f = finite(a); return f.reduce((s, v) => s + v, 0) / f.length; };
function erfc(x) {
  const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r;
}
const pnorm = x => 0.5 * erfc(-x / Math.SQRT2);
function qnorm(p) {                  // Acklam's rational approximation
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.3577518672690, -30.66479806614716, 2.506628277459239];
  const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
  const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  if (p < 0.02425) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
  if (p > 1 - 0.02425) return -qnorm(1 - p);
  const q = p - 0.5, r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}
function lgamma(x) {
  const g = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (x < 0.5) return Math.log(Math.PI / Math.abs(Math.sin(Math.PI * x))) - lgamma(1 - x);
  x -= 1; let a = g[0]; const t = x + 7.5; for (let i = 1; i < 9; i++) a += g[i] / (x + i);
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}
function betacf(a, b, x) {
  const F = 1e-300; let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap;
  if (Math.abs(d) < F) d = F; d = 1 / d; let h = d;
  for (let m = 1; m <= 300; m++) {
    const m2 = 2 * m; let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d; if (Math.abs(d) < F) d = F; c = 1 + aa / c; if (Math.abs(c) < F) c = F; d = 1 / d; h *= d * c;
    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d; if (Math.abs(d) < F) d = F; c = 1 + aa / c; if (Math.abs(c) < F) c = F; d = 1 / d;
    const del = d * c; h *= del; if (Math.abs(del - 1) < 3e-15) break;
  }
  return h;
}
function ibeta(a, b, x) {
  if (x <= 0) return 0; if (x >= 1) return 1;
  const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
}
function pt(x, nu) { const p = 0.5 * ibeta(nu / 2, 0.5, nu / (nu + x * x)); return x > 0 ? 1 - p : p; }
const dtC = nu => Math.exp(lgamma((nu + 1) / 2) - lgamma(nu / 2)) / Math.sqrt(nu * Math.PI);
function qt(p, nu) {                 // Student t quantile for p < 0.5: Newton steps inside a bracket
  let lo = -1e5, hi = 0, x = qnorm(p) * Math.sqrt(nu / Math.max(nu - 2, 0.5)) * 0.9;
  const c = dtC(nu);
  for (let it = 0; it < 100; it++) {
    const F = pt(x, nu) - p;
    if (F > 0) hi = x; else lo = x;
    let nx = x - F / (c * Math.pow(1 + x * x / nu, -(nu + 1) / 2));
    if (!(nx > lo && nx < hi)) nx = 0.5 * (lo + hi);
    if (Math.abs(nx - x) < 1e-11 * (1 + Math.abs(x))) return nx;
    x = nx;
  }
  return x;
}
function gamma(k, z) {               // Marsaglia-Tsang, z: seeded Normal generator with z.u uniform
  if (k < 1) return gamma(k + 1, z) * Math.pow(z.u(), 1 / k);
  const d = k - 1 / 3, c = 1 / Math.sqrt(9 * d);
  for (;;) { const x = z(), v = (1 + c * x) ** 3; if (v <= 0) continue; const u = z.u(); if (Math.log(u) < 0.5 * x * x + d - d * v + d * Math.log(v)) return d * v; }
}
const expo = z => -Math.log(1 - z.u());

// ---------------------------------------------------------------- SPY-TLT daily series
let ST = null;
function st() {
  if (!ST) {
    const S = D.st;
    ST = { d: dates(S), r1: S.r1.map(v => v * 1e-5), r2: S.r2.map(v => v * 1e-5), z1: S.z1.map(v => v * 1e-4), z2: S.z2.map(v => v * 1e-4),
      v1: S.v1.map(v => v * 1e-4), v2: S.v2.map(v => v * 1e-4) };
  }
  return ST;
}
const sharePos = (r, d, a, b) => { let k = 0, n = 0; for (let i = 0; i < r.length; i++) if (Number.isFinite(r[i]) && d[i] >= a && d[i] <= b) { n++; if (r[i] > 0) k++; } return k / n; };

// ================================================================= 1. SPY-TLT rolling correlation
function rolling() {
  const S = st(), m = +$('ro-m').value, n = S.d.length, rc = rollCorr(S.r1, S.r2, m);
  const k = Math.min(Math.max(+$('ro-t').value, m - 1), n - 1);
  $('ro-m-v').textContent = m; $('ro-t-v').textContent = fd(S.d[k]);
  const i0 = m - 1, d = S.d.slice(i0), r = rc.slice(i0), ci = r.map(v => fisherCI(v, m));
  plot('ro-chart', [
    { x: d, y: ci.map(c => c[0]), mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: d, y: ci.map(c => c[1]), mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: 'rgba(26,58,110,0.18)', name: '95% Fisher interval (i.i.d.)', hoverinfo: 'skip' },
    { x: d, y: r, mode: 'lines', name: m + '-day rolling correlation', line: { color: K.blue, width: 1.5 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: [null], y: [null], mode: 'markers', marker: { symbol: 'square', size: 12, color: K.band }, name: '2008-09, 2020 and 2022 stress windows' }
  ], LY({ shapes: [...crisisShapes(), zero(), vline(S.d[k], K.red, 'dot')], xaxis: AX('', { type: 'date' }), yaxis: AX('Correlation SPY-TLT', { range: [-0.9, 0.5] }) }));
  const a = k - m + 1, xs = S.r1.slice(a, k + 1).map(v => 100 * v), ys = S.r2.slice(a, k + 1).map(v => 100 * v);
  const mx = meanA(xs), my = meanA(ys); let sxy = 0, sxx = 0; xs.forEach((v, i) => { sxy += (v - mx) * (ys[i] - my); sxx += (v - mx) ** 2; });
  const bt = sxy / sxx, ext = [Math.min(...xs), Math.max(...xs)];
  plot('ro-sc', [
    { x: xs, y: ys, mode: 'markers', name: 'Daily returns in the window', marker: { color: K.blue, size: 4, opacity: 0.5 }, hovertemplate: 'SPY %{x:.2f}%<br>TLT %{y:.2f}%<extra></extra>' },
    { x: ext, y: ext.map(v => my + bt * (v - mx)), mode: 'lines', name: 'Least-squares line', line: { color: K.red, width: 2 }, hoverinfo: 'skip' }
  ], LY({ title: ttl(`${m} days to ${S.d[k]}: correlation ${rc[k].toFixed(2)}`), xaxis: AX('SPY daily return (%)'), yaxis: AX('TLT daily return (%)') }));
  let mn = 0, mxI = 0; r.forEach((v, i) => { if (v < r[mn]) mn = i; if (v > r[mxI]) mxI = i; });
  const c = fisherCI(rc[k], m);
  out('ro-out', [T.ro1(fd(S.d[k]), nf(rc[k], 2), nf(c[0], 2), nf(c[1], 2)),
    T.ro2(m, nf(r[mn], 2), fd(d[mn]), nf(r[mxI], 2), fd(d[mxI])),
    T.ro3(pct(sharePos(rc, S.d, '0000', '2021-12-31'), 0), pct(sharePos(rc, S.d, '2022-01-01', '9999'), 0))]);
}

// ================================================================= 2. asynchronous trading
const AS_PAIRS = [['spy', 'stoxx', 'SPY / Euro Stoxx 50'], ['spy', 'bet', 'SPY / BET'], ['stoxx', 'bet', 'Euro Stoxx 50 / BET']];
function kday(a, k) { const r = []; for (let i = 0; i + k <= a.length; i += k) { let s = 0; for (let j = i; j < i + k; j++) s += a[j]; r.push(s); } return r; }
const asCache = {};
function asK(k) {
  if (!asCache[k]) {
    const X = cols(D.as.daily, 1e-5).x, R = {}; ['spy', 'stoxx', 'bet'].forEach(c => (R[c] = kday(X[c], k)));
    asCache[k] = AS_PAIRS.map(([a, b]) => { const r = corr(R[a], R[b]), n = R[a].length, c = fisherCI(r, n); return { r, n, lo: c[0], hi: c[1] }; });
  }
  return asCache[k];
}
function asyncCorr() {
  const k = +$('as-k').value; $('as-k-v').textContent = k;
  const W = cols(D.as.weekly, 1e-5).x, nw = W.spy.length;
  const wk = AS_PAIRS.map(([a, b]) => { const r = corr(W[a], W[b]), c = fisherCI(r, nw); return { r, n: nw, lo: c[0], hi: c[1] }; });
  const d1 = asK(1), dk = asK(k), lab = AS_PAIRS.map(p => p[2]);
  const bar = (S, name, col) => ({ x: lab, y: S.map(s => s.r), type: 'bar', name, marker: { color: col },
    error_y: { type: 'data', symmetric: false, array: S.map(s => s.hi - s.r), arrayminus: S.map(s => s.r - s.lo), color: K.navy, thickness: 1, width: 3 },
    customdata: S.map(s => s.n), hovertemplate: '%{x}: %{y:.3f}<br>n = %{customdata}<extra></extra>' });
  plot('as-chart', [bar(d1, 'daily returns', K.green), bar(dk, k === 1 ? '1-day returns' : k + '-day returns', K.amber), bar(wk, 'weekly returns', K.blue)],
    LY({ barmode: 'group', bargap: 0.25, xaxis: AX(''), yaxis: AX('Correlation', { range: [0, 1] }) }));
  const ks = range(1, 20, 1), pc = [K.blue, K.red, K.amber];
  plot('as-k-chart', AS_PAIRS.map((p, j) => ({ x: ks, y: ks.map(h => asK(h)[j].r), mode: 'lines+markers', name: p[2], line: { color: pc[j], width: 2 }, marker: { size: 5 }, hovertemplate: p[2] + ', %{x} days: %{y:.3f}<extra></extra>' })),
    LY({ title: ttl('Non-overlapping k-day returns'), shapes: [vline(k, K.navy, 'dot')], xaxis: AX('Return horizon k (trading days)', { dtick: 2 }), yaxis: AX('Correlation', { range: [0, 1] }) }));
  const X = cols(D.as.daily, 1e-5).x, n = X.spy.length;
  const lead = (a, b) => corr(X[a].slice(0, n - 1), X[b].slice(1));
  out('as-out', [T.as1(k, nf(d1[0].r, 2), nf(dk[0].r, 2), nf(wk[0].r, 2), dk[0].n),
    T.as2(nf(d1[1].r, 2), nf(dk[1].r, 2), nf(wk[1].r, 2), nf(d1[2].r, 2), nf(dk[2].r, 2), nf(wk[2].r, 2)),
    T.as3(nf(lead('spy', 'stoxx'), 2), nf(lead('spy', 'bet'), 2), d1[0].n, nw)]);
}

// ================================================================= 3. Fisher against HAC intervals
const lRule = m => Math.floor(4 * Math.pow(m / 100, 2 / 9));
function hacPath(m, L) {
  const S = st(), x = S.r1, y = S.r2, n = x.length, res = { d: [], r: [], lf: [], hf: [], lh: [], hh: [] }, psi = new Float64Array(m);
  for (let e = m; e <= n; e += 5) {
    const a = e - m; let m1 = 0, m2 = 0, m3 = 0, m4 = 0, m5 = 0;
    for (let t = a; t < e; t++) { m1 += x[t]; m2 += y[t]; m3 += x[t] * x[t]; m4 += y[t] * y[t]; m5 += x[t] * y[t]; }
    m1 /= m; m2 /= m; m3 /= m; m4 /= m; m5 /= m;
    const vx = m3 - m1 * m1, vy = m4 - m2 * m2, c = m5 - m1 * m2, s = Math.sqrt(vx * vy), r = c / s;
    const g = [-m2 / s + r * m1 / vx, -m1 / s + r * m2 / vy, -r / (2 * vx), -r / (2 * vy), 1 / s];
    for (let t = a; t < e; t++) psi[t - a] = g[0] * (x[t] - m1) + g[1] * (y[t] - m2) + g[2] * (x[t] * x[t] - m3) + g[3] * (y[t] * y[t] - m4) + g[4] * (x[t] * y[t] - m5);
    let lrv = 0; for (let t = 0; t < m; t++) lrv += psi[t] * psi[t];
    for (let l = 1; l <= L; l++) { let gl = 0; for (let t = l; t < m; t++) gl += psi[t] * psi[t - l]; lrv += 2 * (1 - l / (L + 1)) * gl; }
    const se = Math.sqrt(lrv / m / m), z = Math.atanh(r), sz = se / (1 - r * r), f = fisherCI(r, m);
    res.d.push(S.d[e - 1]); res.r.push(r); res.lf.push(f[0]); res.hf.push(f[1]); res.lh.push(Math.tanh(z - Q975 * sz)); res.hh.push(Math.tanh(z + Q975 * sz));
  }
  return res;
}
function hac() {
  const m = +$('ha-m').value, L = +$('ha-L').value; $('ha-L-v').textContent = L + (L === lRule(m) ? ' (' + T.rule + ')' : '');
  const P = hacPath(m, L), n = P.r.length, ratio = P.r.map((_, i) => (P.hh[i] - P.lh[i]) / (P.hf[i] - P.lf[i]));
  const sf = P.r.map((_, i) => P.lf[i] > 0 || P.hf[i] < 0), sh = P.r.map((_, i) => P.lh[i] > 0 || P.hh[i] < 0);
  const band = (lo, hi, name, col) => [{ x: P.d, y: lo, mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: P.d, y: hi, mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: col, name, hoverinfo: 'skip' }];
  plot('ha-chart', [...band(P.lh, P.hh, '95% HAC delta-method interval', 'rgba(205,0,0,0.20)'), ...band(P.lf, P.hf, '95% Fisher interval (i.i.d. Normal)', 'rgba(26,58,110,0.35)'),
    { x: P.d, y: P.r, mode: 'lines', name: m + '-day rolling correlation SPY-TLT', line: { color: K.blue, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }],
  LY({ shapes: [...crisisShapes(), zero()], xaxis: AX('', { type: 'date' }), yaxis: AX('Correlation', { range: [-0.95, 0.6] }) }));
  const med = quantile(ratio, 0.5);
  plot('ha-ratio', [{ x: P.d, y: ratio, mode: 'lines', name: 'HAC width / Fisher width', line: { color: K.red, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }],
    LY({ title: ttl('Width of the HAC interval relative to the Fisher interval'), shapes: [hline(1, K.navy, 'dot'), hline(med, K.blue, 'dash')],
      annotations: [{ xref: 'paper', x: 0, y: med, text: 'median ' + med.toFixed(2), showarrow: false, yanchor: 'bottom', xanchor: 'left', bgcolor: 'rgba(255,255,255,0.85)', font: { color: K.blue } }],
      xaxis: AX('', { type: 'date' }), yaxis: AX('Ratio of widths', { range: [0.5, 2.6] }) }));
  const share = a => a.filter(Boolean).length / n;
  out('ha-out', [T.ha1(m, L, n, nf(med, 2), nf(quantile(ratio, 0.9), 2)),
    T.ha2(pct(share(sf), 0), pct(share(sh), 0), pct(sf.filter((v, i) => v && !sh[i]).length / n, 1))]);
}

// ================================================================= 4. EWMA against rolling windows
function ewmaCorr(lam) {
  const S = st(), x = S.r1.map(v => 100 * v), y = S.r2.map(v => 100 * v), n = x.length, init = 100, r = new Array(n).fill(NaN);
  const mx = meanA(x, 0, init), my = meanA(y, 0, init); let a = 0, b = 0, c = 0;
  for (let t = 0; t < init; t++) { a += (x[t] - mx) ** 2; b += (y[t] - my) ** 2; c += (x[t] - mx) * (y[t] - my); }
  a /= init - 1; b /= init - 1; c /= init - 1; r[init] = c / Math.sqrt(a * b);
  for (let t = init + 1; t < n; t++) { a = lam * a + (1 - lam) * x[t - 1] ** 2; b = lam * b + (1 - lam) * y[t - 1] ** 2; c = lam * c + (1 - lam) * x[t - 1] * y[t - 1]; r[t] = c / Math.sqrt(a * b); }
  return r;
}
function firstPositive(r, d, a, b, len = 20) {
  let run = 0;
  for (let i = firstAt(d, a); i < d.length && d[i] <= b; i++) { run = r[i] > 0 ? run + 1 : 0; if (run >= len) return d[i]; }
  return null;
}
function diffSd(r, i0) { const df = []; for (let i = i0 + 1; i < r.length; i++) if (Number.isFinite(r[i]) && Number.isFinite(r[i - 1])) df.push(r[i] - r[i - 1]); return sdA(df); }
let ewFixed = null;
function ewma() {
  const S = st(), lam = +$('ew-l').value, m = +$('ew-m').value, i0 = firstAt(S.d, '2019-01-01');
  $('ew-l-v').textContent = nf(lam, 3); $('ew-m-v').textContent = m;
  if (!ewFixed) ewFixed = { e97: ewmaCorr(0.97), r250: rollCorr(S.r1, S.r2, 250) };
  const e = ewmaCorr(lam), rm = rollCorr(S.r1, S.r2, m), d = S.d.slice(i0), sl = a => a.slice(i0), ht = '%{x}: %{y:.2f}<extra></extra>';
  plot('ew-chart', [
    { x: d, y: sl(e), mode: 'lines', name: 'EWMA, lambda = ' + lam.toFixed(3), line: { color: K.red, width: 1.1 }, hovertemplate: ht },
    { x: d, y: sl(ewFixed.e97), mode: 'lines', name: 'EWMA, lambda = 0.97', line: { color: K.amber, width: 1.2 }, hovertemplate: ht },
    { x: d, y: sl(rm), mode: 'lines', name: m + '-day rolling', line: { color: K.green, width: 1, dash: 'dash' }, hovertemplate: ht },
    { x: d, y: sl(ewFixed.r250), mode: 'lines', name: '250-day rolling', line: { color: K.blue, width: 2 }, hovertemplate: ht }
  ], LY({ shapes: [zero()], xaxis: AX('', { type: 'date' }), yaxis: AX('Correlation SPY-TLT', { range: [-0.9, 0.9] }) }));
  const A = '2021-06-01', B = '2023-06-30', f1 = firstPositive(e, S.d, A, B), f2 = firstPositive(rm, S.d, A, B), f3 = firstPositive(ewFixed.r250, S.d, A, B);
  out('ew-out', [T.ew1(nf(lam, 3), nf(Math.log(0.5) / Math.log(lam), 1), nf((1 + lam) / (1 - lam), 0), nf(diffSd(e, i0), 3), f1 ? fd(f1) : '—'),
    T.ew2(m, nf(diffSd(rm, i0), 4), f2 ? fd(f2) : '—', nf(diffSd(ewFixed.r250, i0), 4), f3 ? fd(f3) : '—')]);
}

// ================================================================= 5. DCC
function dccPath(a, b) {
  const S = st(), x = S.z1, y = S.z2, Q = D.st.Qbar, n = x.length, R = new Float64Array(n), c = 1 - a - b;
  let q11 = Q[0][0], q22 = Q[1][1], q12 = Q[0][1], ll = 0;
  for (let t = 0; t < n; t++) {
    const r = q12 / Math.sqrt(q11 * q22), dd = 1 - r * r; R[t] = r;
    ll += -0.5 * (Math.log(dd) + (x[t] * x[t] + y[t] * y[t] - 2 * r * x[t] * y[t]) / dd - x[t] * x[t] - y[t] * y[t]);
    q11 = c * Q[0][0] + a * x[t] * x[t] + b * q11; q22 = c * Q[1][1] + a * y[t] * y[t] + b * q22; q12 = c * Q[0][1] + a * x[t] * y[t] + b * q12;
  }
  return { R: Array.from(R), ll };
}
let dcRoll = null, dcCCC = null;
function dcc() {
  const S = st(); let a = +$('dc-a').value, b = +$('dc-b').value;
  if (a + b > 0.9999) { b = 0.9999 - a; $('dc-b').value = b; }
  $('dc-a-v').textContent = nf(a, 4); $('dc-b-v').textContent = nf(b, 4);
  if (!dcRoll) { dcRoll = rollCorr(S.r1, S.r2, 252); dcCCC = dccPath(0, 0).ll; }
  const P = dccPath(a, b), qb = D.st.Qbar[0][1];
  plot('dc-chart', [
    { x: S.d, y: P.R, mode: 'lines', name: 'DCC(1,1) conditional correlation', line: { color: K.red, width: 0.8 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: S.d, y: dcRoll, mode: 'lines', name: '252-day rolling correlation', line: { color: K.blue, width: 1.8 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', line: { color: K.navy, dash: 'dash', width: 2 }, name: 'DCC target Q̄₁₂ (sample covariance of standardised residuals)' }
  ], LY({ shapes: [...crisisShapes(), zero(), hline(qb, K.navy, 'dash')], xaxis: AX('', { type: 'date' }), yaxis: AX('Correlation SPY-TLT', { range: [-1, 1] }) }));
  let mn = 0, mx = 0; P.R.forEach((v, i) => { if (v < P.R[mn]) mn = i; if (v > P.R[mx]) mx = i; });
  const i22 = firstAt(S.d, '2022-01-01'), above = (i0, i1) => P.R.slice(i0, i1).filter(v => v > qb).length / (i1 - i0);
  const ab = a + b, hl = ab > 0 && ab < 1 ? nf(Math.log(0.5) / Math.log(ab), 0) : '—';
  out('dc-out', [T.dc1(nf(a, 4), nf(b, 4), nf(ab, 4), hl),
    T.dc2(nf(P.ll, 2), nf(dcCCC, 2), nf(2 * (P.ll - dcCCC), 1), nf(D.st.ll, 2)),
    T.dc3(nf(P.R[mn], 2), fd(S.d[mn]), nf(P.R[mx], 2), fd(S.d[mx]), nf(P.R[P.R.length - 1], 2), pct(above(i22, P.R.length), 0), pct(above(0, i22), 0))]);
}

// ================================================================= 6. minimum-variance weights with DCC
let mvPre = null;
function mvPrep() {
  if (!mvPre) {
    const S = st(), rc = dccPath(D.st.a, D.st.b).R, n = rc.length, s1 = S.v1, s2 = S.v2;
    const X1 = S.r1.map(v => 100 * Math.expm1(v)), X2 = S.r2.map(v => 100 * Math.expm1(v));
    const wf = rho => s1.map((a, i) => { const c = (rho === null ? rc[i] : rho) * a * s2[i]; return Math.min(Math.max((s2[i] ** 2 - c) / (a * a + s2[i] ** 2 - 2 * c), 0), 1); });
    const vol = w => { const p = w.map((v, i) => v * X1[i] + (1 - v) * X2[i]); return sdA(p) * Math.sqrt(252); };
    const wd = wf(null), rho0 = corr(S.r1, S.r2), grid = range(-0.9, 0.9, 0.05);
    mvPre = { wf, vol, wd, rho0, vd: vol(wd), v64: vol(s1.map(() => 0.6)), grid, vg: grid.map(r => vol(wf(r))) };
  }
  return mvPre;
}
function minvar() {
  const S = st(), M = mvPrep(), r0 = +$('mv-r').value; $('mv-r-v').textContent = nf(r0, 2);
  const wc = M.wf(r0), df = M.wd.map((v, i) => v - wc[i]), vc = M.vol(wc);
  plot('mv-w', [
    { x: S.d, y: wc, mode: 'lines', name: 'GARCH + constant correlation ' + r0.toFixed(2), line: { color: K.blue, width: 0.7 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: S.d, y: M.wd, mode: 'lines', name: 'GARCH + DCC', line: { color: K.red, width: 0.7 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: S.d, y: df, mode: 'lines', name: 'Difference: DCC minus constant correlation', xaxis: 'x2', yaxis: 'y2', line: { color: K.green, width: 0.7 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }
  ], LY({ grid: { rows: 2, columns: 1, pattern: 'independent', roworder: 'top to bottom' }, margin: { l: 56, r: 12, t: 20, b: 40 },
    xaxis: AX('', { type: 'date', matches: 'x2', showticklabels: false }), yaxis: AX('Weight in SPY', { range: [0, 1], domain: [0.42, 1] }),
    xaxis2: AX('', { type: 'date' }), yaxis2: AX('Difference', { domain: [0, 0.32] }), shapes: [{ type: 'line', xref: 'x2 domain', yref: 'y2', x0: 0, x1: 1, y0: 0, y1: 0, line: { color: K.navy, width: 1 } }] }));
  plot('mv-v', [
    { x: M.grid, y: M.vg, mode: 'lines', name: 'GARCH + constant correlation', line: { color: K.blue, width: 2 }, hovertemplate: 'correlation %{x:.2f}: %{y:.2f}%<extra></extra>' },
    { x: [r0], y: [vc], mode: 'markers', name: 'Chosen constant correlation', marker: { color: K.blue, size: 11, line: { color: '#fff', width: 2 } }, hovertemplate: '%{y:.2f}%<extra></extra>' },
    { x: [M.grid[0], M.grid[M.grid.length - 1]], y: [M.vd, M.vd], mode: 'lines', name: 'GARCH + DCC', line: { color: K.red, width: 2, dash: 'dash' }, hovertemplate: 'DCC: %{y:.2f}%<extra></extra>' },
    { x: [M.grid[0], M.grid[M.grid.length - 1]], y: [M.v64, M.v64], mode: 'lines', name: 'Fixed 60/40', line: { color: K.amber, width: 2, dash: 'dot' }, hovertemplate: '60/40: %{y:.2f}%<extra></extra>' }
  ], LY({ title: ttl('Annualised volatility of the daily portfolio (%)'), shapes: [vline(M.rho0, K.navy, 'dot')],
    annotations: [{ x: M.rho0, y: 1, yref: 'paper', text: 'full-sample correlation', showarrow: false, xanchor: 'left', font: { size: 11 } }],
    xaxis: AX('Constant correlation used for the weights'), yaxis: AX('Volatility (%)') }));
  let mx = 0; df.forEach((v, i) => { if (Math.abs(v) > Math.abs(df[mx])) mx = i; });
  out('mv-out', [T.mv1(nf(r0, 2), nf(M.v64, 2), nf(vc, 2), nf(M.vd, 2)), T.mv2(nf(meanA(df.map(Math.abs)), 3), nf(Math.abs(df[mx]), 2), fd(S.d[mx]))]);
}

// ================================================================= 7. the Forbes-Rigobon bias
const frInfl = (rho, d) => rho * Math.sqrt((1 + d) / (1 + d * rho * rho));
const frAdj = (rc, d) => rc / Math.sqrt(1 + d * (1 - rc * rc));
function frBias() {
  const dl = +$('fb-d').value, rho = +$('fb-r').value, dg = range(0, 10, 0.05), d0 = D.ref.num.fr_delta;
  $('fb-d-v').textContent = nf(dl, 2); $('fb-r-v').textContent = nf(rho, 2);
  const tr = [[0.2, K.green], [0.4, K.blue], [0.6, K.red]].map(([r, c]) => ({ x: dg, y: dg.map(v => frInfl(r, v)), mode: 'lines', name: 'true correlation ' + r, line: { color: c, width: 2 }, hovertemplate: 'delta %{x:.2f}: %{y:.3f}<extra></extra>' }));
  tr.push({ x: dg, y: dg.map(v => frInfl(rho, v)), mode: 'lines', name: 'chosen true correlation ' + rho.toFixed(2), line: { color: K.purple, width: 2, dash: 'dash' }, hovertemplate: 'delta %{x:.2f}: %{y:.3f}<extra></extra>' });
  tr.push({ x: [dl, dl, dl, dl], y: [0.2, 0.4, 0.6, rho].map(r => frInfl(r, dl)), mode: 'markers', marker: { color: [K.green, K.blue, K.red, K.purple], size: 9, line: { color: '#fff', width: 1.5 } }, showlegend: false, hovertemplate: '%{y:.3f}<extra></extra>' });
  tr.push({ x: [null], y: [null], mode: 'lines', line: { color: K.navy, dash: 'dash', width: 2 }, name: 'S&P 500 in 2008: delta = ' + d0.toFixed(1) });
  const sh = [0.2, 0.4, 0.6].map((r, j) => ({ ...hline(r, [K.green, K.blue, K.red][j], 'dot'), line: { color: [K.green, K.blue, K.red][j], width: 1, dash: 'dot' } }));
  plot('fb-chart', tr, LY({ shapes: [...sh, vline(d0, K.navy, 'dash'), vline(dl, K.purple, 'dot')], xaxis: AX('delta = Var(crisis) / Var(calm) − 1 for the source market'), yaxis: AX('Measured crisis correlation', { range: [0, 1] }) }));
  const rc = frInfl(rho, dl);
  out('fb-out', [T.fb1(nf(dl, 2), nf(1 + dl, 2), nf(rho, 2), nf(rc, 2), nf(rc - rho, 2)), T.fb2(nf(frInfl(0.4, dl), 2), nf(frInfl(0.2, dl), 2), nf(frAdj(rc, dl), 2))]);
}

// ================================================================= 8. Forbes-Rigobon in 2008
function frWindow(k) {
  const P = cols(D.fr.r2, 1e-5), d = P.d, X = P.x, s = 7 * k;
  const sel = (a, b) => { const A = addDays(a, s), B = addDays(b, s); const i0 = firstAt(d, A), i1 = firstAt(d, addDays(B, 1)); return [i0, i1]; };
  const [c0, c1] = sel(...D.fr.calm), [k0, k1] = sel(...D.fr.crisis);
  const delta = varA(X.sp500, k0, k1) / varA(X.sp500, c0, c1) - 1, n0 = Math.floor((c1 - c0) / 2), n1 = Math.floor((k1 - k0) / 2);
  const res = { delta, calm: [d[c0], d[c1 - 1]], crisis: [d[k0], d[k1 - 1]] };
  ['stoxx', 'bet'].forEach(m => {
    const r0 = corr(X.sp500, X[m], c0, c1), r1 = corr(X.sp500, X[m], k0, k1), adj = frAdj(r1, delta);
    const z = rr => (Math.atanh(rr) - Math.atanh(r0)) / Math.sqrt(1 / (n1 - 3) + 1 / (n0 - 3));
    res[m] = { r0, r1, adj, p_raw: 1 - pnorm(z(r1)), p_adj: 1 - pnorm(z(adj)) };
  });
  return res;
}
const frCache = {};
const frW = k => frCache[k] || (frCache[k] = frWindow(k));
function forbesRigobon() {
  const k = +$('fr-k').value, R = frW(k), M = ['stoxx', 'bet'], lab = ['S&P 500 / Euro Stoxx 50', 'S&P 500 / BET'];
  $('fr-k-v').textContent = (k > 0 ? '+' : '') + k;
  const bar = (key, name, col) => ({ x: lab, y: M.map(m => R[m][key]), type: 'bar', name, marker: { color: col }, hovertemplate: '%{x}: %{y:.3f}<extra></extra>' });
  plot('fr-chart', [bar('r0', `Calm year before (${R.calm[0]} – ${R.calm[1]})`, K.green), bar('r1', `Crisis (${R.crisis[0]} – ${R.crisis[1]}), raw`, K.red), bar('adj', 'Crisis, Forbes-Rigobon adjusted', K.blue)],
    LY({ barmode: 'group', bargap: 0.25, xaxis: AX(''), yaxis: AX('Correlation of 2-day returns', { range: [0, 1] }) }));
  const ks = range(-8, 8, 1), L = [['stoxx', 'p_raw', 'Euro Stoxx 50, raw', K.red, 'solid'], ['stoxx', 'p_adj', 'Euro Stoxx 50, adjusted', K.blue, 'solid'],
    ['bet', 'p_raw', 'BET, raw', K.red, 'dot'], ['bet', 'p_adj', 'BET, adjusted', K.blue, 'dot']];
  plot('fr-p', L.map(([m, key, name, col, dash]) => ({ x: ks, y: ks.map(h => frW(h)[m][key]), mode: 'lines+markers', name, line: { color: col, width: 2, dash }, marker: { size: 4 }, hovertemplate: name + ', %{x} weeks: p = %{y:.3f}<extra></extra>' })),
    LY({ title: ttl('One-sided Fisher z test of a rise in correlation'), shapes: [hline(0.05, K.navy, 'dash'), vline(k, K.navy, 'dot')],
      annotations: [{ xref: 'paper', x: 1, y: 0.05, text: '5%', showarrow: false, xanchor: 'right', yanchor: 'bottom' }],
      xaxis: AX('Shift of both windows (weeks)', { dtick: 2 }), yaxis: AX('p-value', { range: [0, 1] }) }));
  out('fr-out', [T.fr1(fd(R.calm[0]), fd(R.calm[1]), fd(R.crisis[0]), fd(R.crisis[1]), nf(R.delta, 2)),
    T.fr2('Euro Stoxx 50', nf(R.stoxx.r0, 2), nf(R.stoxx.r1, 2), nf(R.stoxx.adj, 2), nf(R.stoxx.p_raw, 3), nf(R.stoxx.p_adj, 2)),
    T.fr2('BET', nf(R.bet.r0, 2), nf(R.bet.r1, 2), nf(R.bet.adj, 2), nf(R.bet.p_raw, 3), nf(R.bet.p_adj, 2))]);
}

// ================================================================= 9. exceedance correlations
const EX_Q = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50];
function exceed(x, y, q) {
  const qx = quantile(x, q), qy = quantile(y, q), px = quantile(x, 1 - q), py = quantile(y, 1 - q), lo = [], hi = [];
  for (let i = 0; i < x.length; i++) { if (x[i] <= qx && y[i] <= qy) lo.push(i); if (x[i] >= px && y[i] >= py) hi.push(i); }
  return { lo: lo.length > 5 ? corrIdx(x, y, lo) : NaN, hi: hi.length > 5 ? corrIdx(x, y, hi) : NaN, ilo: lo, ihi: hi, qx, qy, px, py };
}
let exPre = null;
function exceedance() {
  const W = cols(D.ex.w, 1e-5).x, x = W.sp500, y = W.stoxx, q = +$('ex-q').value;
  $('ex-q-v').textContent = nf(q, 2);
  if (!exPre) exPre = EX_Q.map(v => exceed(x, y, v));
  const E = exceed(x, y, q), G = D.ex.q, j = G.findIndex(v => Math.abs(v - q) < 1e-9), nlo = D.ex.norm_low[j], nhi = D.ex.norm_high[j];
  const xt = [0.05, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.95];
  plot('ex-chart', [
    { x: EX_Q, y: exPre.map(e => e.lo), mode: 'lines+markers', name: 'Data: both below quantile q (joint losses)', line: { color: K.red, width: 2 }, marker: { size: 7 }, hovertemplate: 'q = %{x:.2f}: %{y:.3f}<extra></extra>' },
    { x: EX_Q.map(v => 1 - v), y: exPre.map(e => e.hi), mode: 'lines+markers', name: 'Data: both above quantile 1-q (joint gains)', line: { color: K.green, width: 2 }, marker: { size: 7, symbol: 'square' }, hovertemplate: '1 − q = %{x:.2f}: %{y:.3f}<extra></extra>' },
    { x: G, y: D.ex.norm_low, mode: 'lines', name: 'Bivariate Normal distribution with the same correlation', line: { color: K.blue, width: 2, dash: 'dash' }, hovertemplate: 'Normal, q = %{x:.2f}: %{y:.3f}<extra></extra>' },
    { x: G.map(v => 1 - v), y: D.ex.norm_high, mode: 'lines', showlegend: false, line: { color: K.blue, width: 2, dash: 'dash' }, hovertemplate: 'Normal, 1 − q = %{x:.2f}: %{y:.3f}<extra></extra>' },
    { x: [q, 1 - q], y: [E.lo, E.hi], mode: 'markers', name: 'Chosen q', marker: { color: K.navy, size: 12, symbol: 'diamond-open', line: { width: 2 } }, hovertemplate: '%{y:.3f}<extra></extra>' }
  ], LY({ xaxis: AX('Threshold quantile', { tickvals: xt, ticktext: xt.map(v => v.toFixed(2)), tickfont: { size: 10, color: K.navy } }), yaxis: AX('Exceedance correlation', { range: [0, 1] }) }));
  const inLo = new Set(E.ilo), inHi = new Set(E.ihi), idx = x.map((_, i) => i), pick = f => idx.filter(f);
  const sc = (I, name, col, sz) => ({ x: I.map(i => 100 * x[i]), y: I.map(i => 100 * y[i]), mode: 'markers', name, marker: { color: col, size: sz, opacity: 0.7 }, hovertemplate: 'S&P 500 %{x:.2f}%<br>Euro Stoxx 50 %{y:.2f}%<extra></extra>' });
  plot('ex-sc', [sc(pick(i => !inLo.has(i) && !inHi.has(i)), 'Other weeks', K.band, 4), sc(E.ilo, 'Joint losses', K.red, 6), sc(E.ihi, 'Joint gains', K.green, 6)],
    LY({ title: ttl(`Weekly returns, thresholds at quantiles ${q.toFixed(2)} and ${(1 - q).toFixed(2)}`),
      shapes: [vline(100 * E.qx, K.red, 'dot'), hline(100 * E.qy, K.red, 'dot'), vline(100 * E.px, K.green, 'dot'), hline(100 * E.py, K.green, 'dot')],
      xaxis: AX('S&P 500 weekly return (%)', { range: [-20, 15] }), yaxis: AX('Euro Stoxx 50 weekly return (%)', { range: [-25, 18] }) }));
  out('ex-out', [T.ex1(nf(q, 2), nf(E.lo, 2), E.ilo.length, nf(E.hi, 2), E.ihi.length), T.ex2(nf(nlo, 2), nf(corr(x, y), 2), x.length)]);
}

// ================================================================= 10. five copulas with the same Kendall tau
function debyeTau(th) {               // Kendall tau of the Frank copula, 1 - 4/theta (1 - D1(theta))
  const n = 400, h = th / n; let s = 1 + th / Math.expm1(th);
  for (let i = 1; i < n; i++) { const t = i * h; s += (i % 2 ? 4 : 2) * t / Math.expm1(t); }
  return 1 - 4 / th * (1 - s * h / 3 / th);
}
function thetaFromTau(fam, tau) {
  if (fam === 'gaussian' || fam === 't') return Math.sin(Math.PI * tau / 2);
  if (fam === 'clayton') return 2 * tau / (1 - tau);
  if (fam === 'gumbel') return 1 / (1 - tau);
  let lo = 1e-6, hi = 60; for (let i = 0; i < 80; i++) { const m = 0.5 * (lo + hi); if (debyeTau(m) < tau) lo = m; else hi = m; }
  return 0.5 * (lo + hi);
}
function tailDep(fam, th, nu) {
  if (fam === 't') { const l = 2 * pt(-Math.sqrt((nu + 1) * (1 - th) / (1 + th)), nu + 1); return [l, l]; }
  if (fam === 'clayton') return [Math.pow(2, -1 / th), 0];
  if (fam === 'gumbel') return [0, 2 - Math.pow(2, 1 / th)];
  return [0, 0];
}
function simCopula(fam, th, n, z) {   // pairs of Normal scores (Phi^-1(u), Phi^-1(v)), as in dep_tools.simulate
  const X = [], Y = [], nu = 4, cl = p => Math.min(Math.max(p, 1e-12), 1 - 1e-12);
  for (let i = 0; i < n; i++) {
    let u, v;
    if (fam === 'gaussian' || fam === 't') {
      const a = z(), b = th * a + Math.sqrt(1 - th * th) * z();
      if (fam === 'gaussian') { X.push(a); Y.push(b); continue; }
      const w = Math.sqrt(nu / (2 * gamma(nu / 2, z))); u = pt(a * w, nu); v = pt(b * w, nu);
    } else if (fam === 'clayton') {
      const V = gamma(1 / th, z); u = Math.pow(1 + expo(z) / V, -1 / th); v = Math.pow(1 + expo(z) / V, -1 / th);
    } else if (fam === 'gumbel') {
      const al = 1 / th, U = Math.PI * z.u(), W = expo(z);
      const S = Math.sin(al * U) / Math.pow(Math.sin(U), 1 / al) * Math.pow(Math.sin((1 - al) * U) / W, (1 - al) / al);
      u = Math.exp(-Math.pow(expo(z) / S, al)); v = Math.exp(-Math.pow(expo(z) / S, al));
    } else {
      u = z.u(); const w = z.u(); v = -Math.log1p(w * Math.expm1(-th) / (w + (1 - w) * Math.exp(-th * u))) / th;
    }
    X.push(qnorm(cl(u))); Y.push(qnorm(cl(v)));
  }
  return { x: X, y: Y };
}
const czCache = {};
function copulaZoo() {
  const tau = +$('cz-t').value; $('cz-t-v').textContent = nf(tau, 2);
  const key = tau.toFixed(2);
  if (!czCache[key]) {
    const z = rng(42 + Math.round(100 * tau));
    czCache[key] = FAM.map(f => { const th = thetaFromTau(f, tau); return { th, pts: Math.abs(tau - 0.5) < 1e-9 ? { x: D.zoo[f].x.map(v => v / 100), y: D.zoo[f].y.map(v => v / 100) } : simCopula(f, th, 1500, z) }; });
  }
  const C = czCache[key], tr = [], ann = [], lay = { grid: { rows: 1, columns: 5, pattern: 'independent', xgap: 0.12 }, showlegend: false, margin: { l: 36, r: 8, t: 50, b: 40 } };
  FAM.forEach((f, j) => {
    const s = j ? String(j + 1) : '', th = C[j].th;
    tr.push({ x: C[j].pts.x, y: C[j].pts.y, mode: 'markers', xaxis: 'x' + s, yaxis: 'y' + s, marker: { color: FAM_COL[f], size: 3, opacity: 0.5 }, hovertemplate: '%{x:.2f}, %{y:.2f}<extra>' + FAM_LAB[f] + '</extra>' });
    lay['xaxis' + s] = AX('', { range: [-3.8, 3.8], tickvals: [-3, 0, 3] }); lay['yaxis' + s] = AX('', { range: [-3.8, 3.8], tickvals: [-3, 0, 3] });
    const p = f === 't' ? `rho = ${th.toFixed(2)}, nu = 4` : f === 'gaussian' ? `rho = ${th.toFixed(2)}` : `theta = ${th.toFixed(2)}`;
    ann.push({ text: `${FAM_LAB[f]}<br>${p}`, xref: 'x' + s + ' domain', yref: 'paper', x: 0.5, y: 1.02, showarrow: false, yanchor: 'bottom', font: { size: 11, color: K.navy } });
  });
  ann.push({ text: `All with Kendall's tau = ${tau.toFixed(2)}, shown on Normal-score margins`, xref: 'paper', yref: 'paper', x: 0.5, y: -0.16, showarrow: false, yanchor: 'top', font: { size: 11, color: K.navy } });
  lay.annotations = ann;
  plot('cz-chart', tr, LY(lay));
  const lam = FAM.map((f, j) => tailDep(f, C[j].th, 4));
  out('cz-out', [T.cz1(nf(tau, 2), nf(C[0].th, 3), nf(C[2].th, 2), nf(C[3].th, 2), nf(C[4].th, 2)),
    T.cz2(nf(lam[1][0], 2), nf(lam[2][0], 2), nf(lam[3][1], 2))]);
}

// ================================================================= 11. pseudo-observations
const BK = () => { const B = D.bk; if (!B._d) { B._d = dates(B); B._z1 = B.z1.map(v => v / 100); B._z2 = B.z2.map(v => v / 100); } return B; };
function ranksOf(a) { const idx = a.map((_, i) => i).sort((i, j) => a[i] - a[j]), r = new Array(a.length); idx.forEach((i, k) => (r[i] = k + 1)); return r; }
function kendall(x, y) {
  const n = x.length; let s = 0;
  for (let i = 0; i < n; i++) { const xi = x[i], yi = y[i]; for (let j = i + 1; j < n; j++) { const p = (x[j] - xi) * (y[j] - yi); s += p > 0 ? 1 : p < 0 ? -1 : 0; } }
  return 2 * s / (n * (n - 1));
}
const poCache = {};
function pseudoObs() {
  const B = BK(), y0 = +$('po-y').value; $('po-y-v').textContent = y0;
  const i0 = firstAt(B._d, y0 + '-01-01');
  if (!poCache[y0]) {
    const a = ranksOf(B.r1.slice(i0)), b = ranksOf(B.r2.slice(i0)), n = a.length;
    poCache[y0] = { u: a.map(v => v / (n + 1)), v: b.map(v => v / (n + 1)), n, tau: kendall(a, b), rs: corr(a, b) };
  }
  const P = poCache[y0];
  plot('po-z', [{ x: B._z1.slice(i0), y: B._z2.slice(i0), mode: 'markers', name: 'GARCH standardised residuals', marker: { color: K.blue, size: 3, opacity: 0.35 }, hovertemplate: 'JPM %{x:.2f}<br>BAC %{y:.2f}<extra></extra>' }],
    LY({ xaxis: AX('JPM', { range: [-8, 9] }), yaxis: AX('BAC', { range: [-8, 6.5] }), showlegend: true }));
  plot('po-u', [{ x: P.u, y: P.v, mode: 'markers', name: 'Pseudo-observations (ranks / (n+1))', marker: { color: K.red, size: 3, opacity: 0.35 }, hovertemplate: 'JPM %{x:.3f}<br>BAC %{y:.3f}<extra></extra>' }],
    LY({ xaxis: AX('JPM (uniform scale)', { range: [-0.03, 1.03] }), yaxis: AX('BAC (uniform scale)', { range: [-0.03, 1.03] }), showlegend: true }));
  out('po-out', [T.po1(fd(B._d[i0]), fd(B._d[B._d.length - 1]), P.n, nf(P.tau, 3), nf(P.rs, 3)), T.po2(nf(Math.sin(Math.PI * P.tau / 2), 3), nf(2 * Math.sin(Math.PI * P.rs / 6), 3))]);
}

// ================================================================= 12. copula estimates (t copula profile in nu)
const tqCache = {};
function tTable(nu) {                 // x_k = T_nu^-1(k / (n + 1)), k = 1..n
  const key = nu.toFixed(4);
  if (!tqCache[key]) {
    const n = D.bk.r1.length, x = new Float64Array(n + 1);
    for (let k = 1; 2 * k <= n + 1; k++) { const v = qt(k / (n + 1), nu); x[k] = v; x[n + 1 - k] = -v; }
    if ((n + 1) % 2 === 0) x[(n + 1) / 2] = 0;
    tqCache[key] = x;
  }
  return tqCache[key];
}
function tLogLik(nu) {
  const B = D.bk, x = tTable(nu), n = B.r1.length, a = new Float64Array(n), b = new Float64Array(n);
  for (let i = 0; i < n; i++) { a[i] = x[B.r1[i]]; b[i] = x[B.r2[i]]; }
  const cst = lgamma((nu + 2) / 2) + lgamma(nu / 2) - 2 * lgamma((nu + 1) / 2);
  let marg = 0; for (let i = 0; i < n; i++) marg += (nu + 1) / 2 * (Math.log1p(a[i] * a[i] / nu) + Math.log1p(b[i] * b[i] / nu));
  const ll = rho => { let s = 0; const k = nu * (1 - rho * rho); for (let i = 0; i < n; i++) s += Math.log1p((a[i] * a[i] + b[i] * b[i] - 2 * rho * a[i] * b[i]) / k);
    return n * (cst - 0.5 * Math.log(1 - rho * rho)) - (nu + 2) / 2 * s + marg; };
  let lo = 0.3, hi = 0.99; const g = (Math.sqrt(5) - 1) / 2;
  let c = hi - g * (hi - lo), d = lo + g * (hi - lo), fc = ll(c), fd2 = ll(d);
  for (let it = 0; it < 70; it++) { if (fc > fd2) { hi = d; d = c; fd2 = fc; c = hi - g * (hi - lo); fc = ll(c); } else { lo = c; c = d; fc = fd2; d = lo + g * (hi - lo); fd2 = ll(d); } }
  const rho = 0.5 * (lo + hi);
  return { rho, ll: ll(rho) };
}
const CF_NU = [2.2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40];
let cfProfile = null;
function copulaFit() {
  const nu = +$('cf-n').value, Tb = D.bk.table, nuHat = D.bk.t_par[1]; $('cf-n-v').textContent = nf(nu, 2);
  const F = tLogLik(nu), aicT = 4 - 2 * F.ll;
  const aic = FAM.map(f => (f === 't' ? aicT : Tb[f].aic)), best = Math.min(...aic), dA = aic.map(v => v - best);
  const atHat = Math.abs(nu - nuHat) < 1e-3;
  const txt = FAM.map(f => (f === 't' && !atHat ? '' : 'p = ' + Tb[f].gof_p.toFixed(3)));
  plot('cf-chart', [{ x: FAM.map(f => FAM_LAB[f]), y: dA, type: 'bar', marker: { color: FAM.map(f => FAM_COL[f]) }, text: txt, textposition: 'outside', textfont: { size: 11, color: K.navy }, cliponaxis: false, hovertemplate: '%{x}: AIC − best AIC = %{y:.1f}<extra></extra>', showlegend: false }],
  LY({ margin: { l: 56, r: 12, t: 30, b: 80 }, annotations: [{ xref: 'paper', yref: 'paper', x: 0, y: -0.14, xanchor: 'left', yanchor: 'top', showarrow: false, align: 'left', font: { size: 11, color: K.navy },
      text: 'Numbers above bars: goodness-of-fit p-value<br>(Rosenblatt Cramér–von Mises, parametric bootstrap)' }], title: ttl('Student t at nu = ' + nu.toFixed(2) + (atHat ? ' (ML estimate)' : '')), xaxis: AX(''), yaxis: AX('AIC minus best AIC', { range: [0, 1.15 * Math.max(...dA, 100)] }) }));
  if (!cfProfile) cfProfile = CF_NU.map(v => tLogLik(v).ll);
  plot('cf-prof', [
    { x: CF_NU, y: cfProfile, mode: 'lines+markers', name: 't copula, profile log-likelihood', line: { color: K.red, width: 2 }, marker: { size: 5 }, hovertemplate: 'nu = %{x}: %{y:.1f}<extra></extra>' },
    { x: [nu], y: [F.ll], mode: 'markers', name: 'Chosen nu', marker: { color: K.red, size: 12, symbol: 'diamond', line: { color: '#fff', width: 2 } }, hovertemplate: 'nu = %{x:.2f}: %{y:.1f}<extra></extra>' },
    { x: [CF_NU[0], CF_NU[CF_NU.length - 1]], y: [Tb.gaussian.loglik, Tb.gaussian.loglik], mode: 'lines', name: 'Gaussian copula', line: { color: K.blue, width: 2, dash: 'dash' }, hovertemplate: 'Gaussian: %{y:.1f}<extra></extra>' }
  ], LY({ title: ttl('Log-likelihood, maximised over rho for each nu'), xaxis: AX('Degrees of freedom nu (log scale)', { type: 'log', tickvals: [2, 3, 4, 5, 7, 10, 15, 20, 30, 40] }), yaxis: AX('Log-likelihood') }));
  const lam = tailDep('t', F.rho, nu)[0];
  out('cf-out', [T.cf1(nf(nu, 2), nf(F.rho, 3), nf(F.ll, 1), nf(lam, 2)), T.cf2(nf(aicT - Tb.gaussian.aic, 1), FAM_LAB[FAM[dA.indexOf(0)]], nf(nuHat, 2), nf(D.bk.t_ll, 1))]);
}

// ================================================================= 13. empirical tail dependence
function tailDepBlock() {
  const B = D.bk, n = B.r1.length, qs = B.qs, j = +$('td-q').value, q = qs[j];
  $('td-q-v').textContent = nf(q, 2);
  const u = B.r1.map(v => v / (n + 1)), v = B.r2.map(x => x / (n + 1));
  const emp = qq => { let lo = 0, hi = 0; for (let i = 0; i < n; i++) { if (u[i] <= qq && v[i] <= qq) lo++; if (u[i] > 1 - qq && v[i] > 1 - qq) hi++; } return [lo / n / qq, hi / n / qq, lo, hi]; };
  const E = qs.map(emp), T6 = B.table;
  plot('td-chart', [
    { x: qs, y: B.band_lo, mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: qs, y: B.band_hi, mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: 'rgba(205,0,0,0.15)', name: '90% band under the fitted t copula', hoverinfo: 'skip' },
    { x: qs, y: E.map(e => e[0]), mode: 'lines+markers', name: 'Lower tail, P(U≤q, V≤q) / q', line: { color: K.red, width: 2 }, marker: { size: 5 }, hovertemplate: 'q = %{x:.2f}: %{y:.3f}<extra></extra>' },
    { x: qs, y: E.map(e => e[1]), mode: 'lines+markers', name: 'Upper tail, P(U>1−q, V>1−q) / q', line: { color: K.green, width: 2 }, marker: { size: 5, symbol: 'square' }, hovertemplate: 'q = %{x:.2f}: %{y:.3f}<extra></extra>' },
    ...[[T6.t.lamL, K.red, 'dash', 't copula limit '], [T6.clayton.lamL, K.green, 'dot', 'Clayton lower limit '], [T6.gumbel.lamU, K.amber, 'dot', 'Gumbel upper limit ']].map(([y, c, dash, name]) =>
      ({ x: [0, 0.21], y: [y, y], mode: 'lines', name: name + y.toFixed(2), line: { color: c, width: 1.5, dash }, hoverinfo: 'skip' }))
  ], LY({ shapes: [vline(q, K.navy, 'dot')], xaxis: AX('q', { range: [0, 0.21] }), yaxis: AX('Tail dependence estimate', { range: [0, 1] }) }));
  const inL = [], inU = [], rest = [];
  for (let i = 0; i < n; i++) (u[i] <= q && v[i] <= q ? inL : u[i] > 1 - q && v[i] > 1 - q ? inU : rest).push(i);
  const sc = (I, name, col, sz) => ({ x: I.map(i => u[i]), y: I.map(i => v[i]), mode: 'markers', name, marker: { color: col, size: sz, opacity: 0.6 }, hovertemplate: '%{x:.3f}, %{y:.3f}<extra></extra>' });
  const box = (a, b, c) => ({ type: 'rect', xref: 'x', yref: 'y', x0: a, x1: b, y0: a, y1: b, line: { color: c, width: 1.5 } });
  plot('td-sc', [sc(rest, 'Other days', K.band, 3), sc(inL, 'Both in the lower q-tail', K.red, 4), sc(inU, 'Both in the upper q-tail', K.green, 4)],
    LY({ title: ttl('Pseudo-observations JPM-BAC'), shapes: [box(0, q, K.red), box(1 - q, 1, K.green)], xaxis: AX('JPM (uniform scale)', { range: [0, 1] }), yaxis: AX('BAC (uniform scale)', { range: [0, 1] }) }));
  const e = E[j];
  out('td-out', [T.td1(nf(q, 2), nf(e[0], 2), nf(e[1], 2), nf(B.band_lo[j], 2), nf(B.band_hi[j], 2)), T.td2(Math.round(q * n), e[2], e[3])]);
}

// ================================================================= 14. integration of US, euro-area and Romanian equities
const IN_PAIRS = [['sp500', 'stoxx', 'S&P 500 / Euro Stoxx 50', K.blue], ['stoxx', 'bet', 'Euro Stoxx 50 / BET', K.red], ['sp500', 'bet', 'S&P 500 / BET', K.amber]];
function integration() {
  const P = cols(D.int, 1e-5), d = P.d, X = P.x, w = +$('in-w').value; $('in-w-v').textContent = w;
  const rc = IN_PAIRS.map(([a, b]) => rollCorr(X[a], X[b], w));
  plot('in-chart', IN_PAIRS.map(([, , lab, col], j) => ({ x: d.slice(w - 1), y: rc[j].slice(w - 1), mode: 'lines', name: lab, line: { color: col, width: 1.5 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' })),
    LY({ shapes: [zero()], xaxis: AX('', { type: 'date' }), yaxis: AX(w + '-week rolling correlation', { range: [-0.4, 1] }) }));
  const per = (a, b, lo, hi) => { const i0 = firstAt(d, lo), i1 = firstAt(d, hi); return corr(X[a], X[b], i0, i1); };
  const eb = rc[1], at = (e) => eb[firstAt(d, addDays(e, 1)) - 1];   // Euro Stoxx 50 / BET on the chart's calendar
  out('in-out', [T.in1(w, nf(at('2007-12-31'), 2), nf(at('2009-12-31'), 2), nf(at('2019-12-31'), 2), nf(at('2021-12-31'), 2), nf(eb[eb.length - 1], 2)),
    T.in2(nf(per('stoxx', 'bet', '0000', '2010-01-01'), 2), nf(per('stoxx', 'bet', '2010-01-01', '2020-01-01'), 2), nf(per('stoxx', 'bet', '2020-01-01', '9999'), 2),
      nf(per('sp500', 'stoxx', '0000', '2010-01-01'), 2), nf(per('sp500', 'stoxx', '2010-01-01', '2020-01-01'), 2), nf(per('sp500', 'stoxx', '2020-01-01', '9999'), 2))]);
}

// ================================================================= 15-17. banks
const BANKS = ['jpm', 'bac', 'dbk', 'bnp', 'tlv', 'brd'], BLAB = ['JPM', 'BAC', 'DBK', 'BNP', 'TLV', 'BRD'];
const REGION = { jpm: 'US', bac: 'US', dbk: 'EA', bnp: 'EA', tlv: 'RO', brd: 'RO' };
function bankCorr(i0, i1) { const X = cols(D.banks, 1e-5).x; return BANKS.map(a => BANKS.map(b => (a === b ? 1 : corr(X[a], X[b], i0, i1)))); }
function bankWindow(pfx) {
  const d = cols(D.banks, 1e-5).d, n = d.length, wv = $(pfx + '-w').value, k = Math.min(+$(pfx + '-t').value, n - 1), w = wv === 'all' ? n : +wv;
  const i1 = k + 1, i0 = wv === 'all' ? 0 : Math.max(0, i1 - w);
  $(pfx + '-t-v').textContent = fd(d[k]);
  return { i0, i1, d, n };
}
function banksHeat() {
  const { i0, i1, d } = bankWindow('bh'), Cm = bankCorr(i0, i1);
  const ann = []; Cm.forEach((r, i) => r.forEach((v, j) => ann.push({ x: BLAB[j], y: BLAB[i], text: v.toFixed(2), showarrow: false, font: { size: 12, color: v > 0.6 ? '#fff' : K.navy } })));
  plot('bh-chart', [{ z: Cm, x: BLAB, y: BLAB, type: 'heatmap', zmin: 0, zmax: 1, colorscale: [[0, '#F4F7FC'], [0.5, '#93AEDD'], [1, K.blue]], colorbar: { title: { text: 'Correlation of weekly returns', side: 'right' }, thickness: 12 },
    hovertemplate: '%{y} – %{x}: %{z:.3f}<extra></extra>' }],
  LY({ annotations: ann, title: ttl(`${i1 - i0} weeks, ${d[i0]} to ${d[i1 - 1]}`), xaxis: AX(''), yaxis: AX('', { autorange: 'reversed' }) }));
  const c = (a, b) => nf(Cm[BANKS.indexOf(a)][BANKS.indexOf(b)], 2);
  out('bh-out', [T.bh1(i1 - i0, fd(d[i0]), fd(d[i1 - 1])), T.bh2(c('jpm', 'bac'), c('dbk', 'bnp'), c('tlv', 'brd'), c('bnp', 'tlv'), c('jpm', 'brd'))]);
}
const BA_GROUPS = [['Within region (US-US, EA-EA, RO-RO)', K.blue, (a, b) => REGION[a] === REGION[b]],
  ['US - euro area', K.amber, (a, b) => [REGION[a], REGION[b]].sort().join() === 'EA,US'],
  ['Romania - US / euro area', K.red, (a, b) => (REGION[a] === 'RO') !== (REGION[b] === 'RO')]];
function banksAvg() {
  const P = cols(D.banks, 1e-5), d = P.d, X = P.x, w = +$('ba-w').value; $('ba-w-v').textContent = w;
  const pairs = []; BANKS.forEach((a, i) => BANKS.slice(i + 1).forEach(b => pairs.push([a, b])));
  const rc = {}; pairs.forEach(p => (rc[p] = rollCorr(X[p[0]], X[p[1]], w)));
  const M = BA_GROUPS.map(([, , f]) => { const ps = pairs.filter(p => f(...p)); return d.map((_, t) => (t < w - 1 ? NaN : ps.reduce((s, p) => s + rc[p][t], 0) / ps.length)); });
  plot('ba-chart', BA_GROUPS.map(([lab, col], j) => ({ x: d.slice(w - 1), y: M[j].slice(w - 1), mode: 'lines', name: lab, line: { color: col, width: 1.6 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' })),
    LY({ shapes: [zero()],
      xaxis: AX('', { type: 'date' }), yaxis: AX(`Average ${w}-week correlation`, { range: [-0.3, 1] }) }));
  const i0 = firstAt(d, '2020-03-01'), i1 = firstAt(d, '2020-07-01'), f = (v, k) => nf(v, 2);
  const m20 = M.map(m => nanMean(m.slice(i0, i1))), mm = M.map(nanMean), last = M.map(m => m[m.length - 1]);
  out('ba-out', [T.ba1(w, f(mm[0]), f(mm[1]), f(mm[2])), T.ba2(f(m20[0]), f(m20[1]), f(m20[2])), T.ba3(f(last[0]), f(last[1]), f(last[2]))]);
}
const MST_POS = { JPM: [-1.0, 0.6], BAC: [-1.0, -0.6], DBK: [0.3, 0.6], BNP: [0.3, -0.6], TLV: [1.6, 0.6], BRD: [1.6, -0.6] };
const MST_COL = { JPM: K.blue, BAC: K.blue, DBK: K.amber, BNP: K.amber, TLV: K.red, BRD: K.red };
function mst(Cm) {                    // Kruskal on d = sqrt(2 (1 - rho))
  const E = []; for (let i = 0; i < 6; i++) for (let j = i + 1; j < 6; j++) E.push([Math.sqrt(2 * (1 - Cm[i][j])), i, j]);
  E.sort((a, b) => a[0] - b[0]); const par = [0, 1, 2, 3, 4, 5], find = x => (par[x] === x ? x : (par[x] = find(par[x]))), T5 = [];
  for (const [, i, j] of E) { const a = find(i), b = find(j); if (a !== b) { par[a] = b; T5.push([i, j, Cm[i][j]]); } }
  return T5;
}
function banksMst() {
  const { i0, i1, d } = bankWindow('bm'), Cm = bankCorr(i0, i1), Tr = mst(Cm), tr = [], ann = [];
  Tr.forEach(([i, j, r]) => {
    const a = MST_POS[BLAB[i]], b = MST_POS[BLAB[j]], vert = a[0] === b[0];
    tr.push({ x: [a[0], b[0]], y: [a[1], b[1]], mode: 'lines', line: { color: 'rgba(26,58,110,0.45)', width: 2 + 10 * Math.max(r, 0) }, showlegend: false, hoverinfo: 'skip' });
    const diag = !vert && a[1] !== b[1];
    ann.push({ x: (a[0] + b[0]) / 2 + (vert ? 0.16 : diag ? 0.14 : 0), y: (a[1] + b[1]) / 2 + (vert ? 0 : diag ? 0.12 : 0.1), text: r.toFixed(2), showarrow: false, font: { size: 12, color: K.navy } });
  });
  [['US banks', K.blue, ['JPM', 'BAC']], ['Euro-area banks', K.amber, ['DBK', 'BNP']], ['Romanian banks', K.red, ['TLV', 'BRD']]].forEach(([name, col, ks]) =>
    tr.push({ x: ks.map(k => MST_POS[k][0]), y: ks.map(k => MST_POS[k][1]), mode: 'markers+text', text: ks, textfont: { color: '#fff', size: 12, family: 'Inter, sans-serif' }, name,
      marker: { color: col, size: 44 }, hovertemplate: '%{text}<extra></extra>' }));
  plot('bm-chart', tr, LY({ title: ttl(`${i1 - i0} weeks, ${d[i0]} to ${d[i1 - 1]}`), annotations: ann, xaxis: { visible: false, range: [-1.5, 2.1] }, yaxis: { visible: false, range: [-1.0, 1.0] }, legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.05, yanchor: 'top' } }));
  const edges = Tr.map(([i, j, r]) => `${BLAB[i]}–${BLAB[j]} (${nf(r, 2)})`).join('; ');
  const bridge = Tr.filter(([i, j]) => (REGION[BANKS[i]] === 'RO') !== (REGION[BANKS[j]] === 'RO')).map(([i, j]) => `${BLAB[i]}–${BLAB[j]}`).join(', ');
  out('bm-out', [T.bm1(i1 - i0, fd(d[i0]), fd(d[i1 - 1]), edges), T.bm2(bridge)]);
}

// ================================================================= 18. inflation and the stock-bond correlation
function nwOls(x, z, L) {              // OLS of z on (1, x) with Newey-West (Bartlett, L lags) standard errors, no small-sample correction
  const n = x.length, mx = meanA(x), mz = meanA(z); let sxx = 0, sxz = 0; for (let i = 0; i < n; i++) { sxx += (x[i] - mx) ** 2; sxz += (x[i] - mx) * (z[i] - mz); }
  const b = sxz / sxx, a = mz - b * mx, e = z.map((v, i) => v - a - b * x[i]);
  let sse = 0, sst = 0; e.forEach((v, i) => { sse += v * v; sst += (z[i] - mz) ** 2; });
  const S = [[0, 0], [0, 0]];
  for (let l = 0; l <= L; l++) {
    const w = l === 0 ? 1 : 1 - l / (L + 1); let g00 = 0, g01 = 0, g10 = 0, g11 = 0;
    for (let t = l; t < n; t++) { const u = e[t] * e[t - l]; g00 += u; g01 += u * x[t - l]; g10 += u * x[t]; g11 += u * x[t] * x[t - l]; }
    if (l === 0) { S[0][0] += g00; S[0][1] += g01; S[1][0] += g10; S[1][1] += g11; }
    else { S[0][0] += 2 * w * g00; S[0][1] += w * (g01 + g10); S[1][0] += w * (g10 + g01); S[1][1] += 2 * w * g11; }
  }
  let s0 = 0, s1 = 0, s2 = 0; x.forEach(v => { s0 += 1; s1 += v; s2 += v * v; });
  const det = s0 * s2 - s1 * s1, B = [[s2 / det, -s1 / det], [-s1 / det, s0 / det]];
  const BS = [[B[0][0] * S[0][0] + B[0][1] * S[1][0], B[0][0] * S[0][1] + B[0][1] * S[1][1]], [B[1][0] * S[0][0] + B[1][1] * S[1][0], B[1][0] * S[0][1] + B[1][1] * S[1][1]]];
  const v11 = BS[1][0] * B[0][1] + BS[1][1] * B[1][1], se = Math.sqrt(v11);
  return { a, b, se, t: b / se, r2: 1 - sse / sst, n };
}
function aiInflation() {
  const A = D.ai, k = +$('ai-t').value, m = A.m, n1 = k + 1;
  $('ai-t-v').textContent = T.month(m[k]);
  const x = A.infl.slice(0, n1), z = A.rho.slice(0, n1).map(Math.atanh), F = nwOls(x, z, 12);
  const ip = m.indexOf('2021-12') + 1, P = nwOls(A.infl.slice(0, ip), A.rho.slice(0, ip).map(Math.atanh), 12);
  const pre = [], post = []; for (let i = 0; i < n1; i++) (i < ip ? pre : post).push(i);
  const xg = range(Math.min(...A.infl), Math.max(...A.infl), 0.1);
  const pts = (I, name, col) => ({ x: I.map(i => A.infl[i]), y: I.map(i => A.rho[i]), customdata: I.map(i => m[i]), mode: 'markers', name, marker: { color: col, size: 6, opacity: 0.7 }, hovertemplate: '%{customdata}: inflation %{x:.1f}%, correlation %{y:.2f}<extra></extra>' });
  const lab = `Fitted, ${m[0]} to ${m[k]}`;
  plot('ai-chart', [pts(pre, 'Months 2002-2021', K.blue), pts(post, 'Months 2022-2026', K.red),
    { x: xg, y: xg.map(v => Math.tanh(F.a + F.b * v)), mode: 'lines', name: lab, line: { color: K.amber, width: 2.2 }, hoverinfo: 'skip' },
    { x: xg, y: xg.map(v => Math.tanh(P.a + P.b * v)), mode: 'lines', name: 'Fitted, 2002-2021 only', line: { color: K.green, width: 2.2, dash: 'dash' }, hoverinfo: 'skip' }],
  LY({ shapes: [zero()], xaxis: AX('US CPI inflation known at the start of the month (%)', { range: [-2.5, 9.5] }), yaxis: AX('Monthly SPY-TLT correlation', { range: [-1, 1] }) }));
  plot('ai-ci', [
    { x: [F.b], y: ['Chosen sample'], error_x: { type: 'data', array: [Q975 * F.se], color: K.amber, thickness: 2, width: 6 }, mode: 'markers', marker: { color: K.amber, size: 12 }, name: 'Slope γ1, chosen sample, 95% HAC interval', hovertemplate: 'γ1 = %{x:.3f}<extra></extra>' },
    { x: [P.b], y: ['2002-2021'], error_x: { type: 'data', array: [Q975 * P.se], color: K.green, thickness: 2, width: 6 }, mode: 'markers', marker: { color: K.green, size: 12 }, name: 'Slope γ1, 2002-2021, 95% HAC interval', hovertemplate: 'γ1 = %{x:.3f}<extra></extra>' }
  ], LY({ title: ttl('Slope of the Fisher-z correlation on inflation'), shapes: [vline(0, K.navy)], xaxis: AX('γ1 per percentage point of inflation', { range: [Math.min(-0.1, F.b - 2.2 * F.se), Math.max(0.15, F.b + 2.2 * F.se)], dtick: 0.05 }), yaxis: AX('', { type: 'category', range: [-0.7, 1.7] }) }));
  const hi = [], lo = []; for (let i = 0; i < n1; i++) (A.infl[i] > 3 ? hi : lo).push(A.rho[i]);
  out('ai-out', [T.ai1(T.month(m[0]), T.month(m[k]), F.n, nf(F.b, 3), nf(F.se, 3), nf(F.t, 2), nf(F.r2, 3)),
    T.ai2(nf(meanA(hi), 2), hi.length, nf(meanA(lo), 2), lo.length), T.ai3(nf(P.b, 3), nf(P.t, 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  const n = D.st.t.length, R = D.ref.num;
  $('ro-t').max = n - 1; $('ro-t').value = n - 1; on(['ro-m', 'ro-t'], rolling); P('ro-play', 'ro-t', range(251, n - 1, 25), 70);
  on(['as-k'], asyncCorr); P('as-play', 'as-k', range(1, 20, 1), 600);
  $('ha-m').addEventListener('input', () => { $('ha-L').value = lRule(+$('ha-m').value); hac(); }); on(['ha-L'], hac); P('ha-play', 'ha-L', range(0, 20, 1), 500);
  on(['ew-l', 'ew-m'], ewma); P('ew-play', 'ew-l', range(0.8, 0.995, 0.005), 160);
  $('dc-a').value = D.st.a; $('dc-b').value = D.st.b; on(['dc-a', 'dc-b'], dcc); P('dc-play', 'dc-a', range(0, 0.06, 0.0025), 300);
  $('mv-r').value = mvPrep().rho0; on(['mv-r'], minvar); P('mv-play', 'mv-r', range(-0.9, 0.9, 0.05), 250);
  $('fb-d').value = R.fr_delta; on(['fb-d', 'fb-r'], frBias); P('fb-play', 'fb-d', range(0, 10, 0.25), 150);
  on(['fr-k'], forbesRigobon); P('fr-play', 'fr-k', range(-8, 8, 1), 450);
  on(['ex-q'], exceedance); P('ex-play', 'ex-q', range(0.05, 0.5, 0.01), 200);
  on(['cz-t'], copulaZoo); P('cz-play', 'cz-t', range(0.05, 0.9, 0.05), 700);
  on(['po-y'], pseudoObs); P('po-play', 'po-y', range(2010, 2024, 1), 700);
  $('cf-n').value = D.bk.t_par[1]; on(['cf-n'], copulaFit); P('cf-play', 'cf-n', CF_NU, 600);
  on(['td-q'], tailDepBlock); P('td-play', 'td-q', range(0, 19, 1), 400);
  on(['in-w'], integration); P('in-play', 'in-w', range(26, 260, 6), 250);
  const nb = D.banks.t.length;
  ['bh', 'bm'].forEach(p => { $(p + '-t').max = nb - 1; $(p + '-t').value = nb - 1; $(p + '-t').min = 51; });
  on(['bh-w', 'bh-t'], banksHeat); on(['bm-w', 'bm-t'], banksMst);
  ['bh', 'bm'].forEach(p => $(p + '-play').addEventListener('click', () => { if ($(p + '-w').value === 'all') $(p + '-w').value = '104'; }, true));
  P('bh-play', 'bh-t', range(103, nb - 1, 4), 120); P('bm-play', 'bm-t', range(103, nb - 1, 4), 160);
  on(['ba-w'], banksAvg); P('ba-play', 'ba-w', range(26, 156, 4), 250);
  const na = D.ai.m.length; $('ai-t').max = na - 1; $('ai-t').min = 59; $('ai-t').value = na - 1; on(['ai-t'], aiInflation); P('ai-play', 'ai-t', range(59, na - 1, 3), 150);
  rolling(); asyncCorr(); hac(); ewma(); dcc(); minvar(); frBias(); forbesRigobon(); exceedance(); copulaZoo(); pseudoObs(); copulaFit(); tailDepBlock();
  integration(); banksHeat(); banksAvg(); banksMst(); aiInflation();
}
window.CH6 = { rollCorr, hacPath, ewmaCorr, dccPath, mvPrep, frW, exceed, thetaFromTau, tailDep, tLogLik, qt, pt, qnorm, pnorm, kendall, nwOls, mst, bankCorr, firstPositive, diffSd, simCopula, rng };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

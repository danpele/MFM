// Chapter 19 interactive page: one block per chart slide, computed in the browser from ch19_data.js.
(function () {
'use strict';
const D = window.CH19_DATA;
const { LANG, sum, mean, sdev, median, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH19_TEXT;

// ---------------------------------------------------------------- colours of the chapter charts (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  teal: '#17A2B8', navy: '#1F2A44', band: '#C5D2E8', black: '#000000' };
const MODELS = D.models, MC = D.mcol;
const legendBelow = y => ({ orientation: 'h', x: 0, xanchor: 'left', y: y === undefined ? -0.2 : y, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } });

// ---------------------------------------------------------------- formatting
const ni = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, LANG === 'ro' ? ' ' : ',').replace('-', '−');
const MON = LANG === 'ro' ? ['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sept.', 'oct.', 'nov.', 'dec.']
  : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const dfmt = s => `${+s.slice(8, 10)} ${MON[+s.slice(5, 7) - 1]} ${s.slice(0, 4)}`;
const pv = p => (p < 0.001 ? '< ' + nf(0.001, 3) : nf(p, 3));
const levTxt = a => nf(100 * a, Math.abs(a - 0.025) < 1e-9 ? 1 : 0) + '%';
const levChart = a => (100 * a).toFixed(Math.abs(a - 0.025) < 1e-9 ? 1 : 0) + '%';
const roundHalfEven = x => { const f = Math.floor(x), d = x - f; return d > 0.5 + 1e-12 ? f + 1 : d < 0.5 - 1e-12 ? f : (f % 2 === 0 ? f : f + 1); };

// ---------------------------------------------------------------- data: dates and BET daily log returns in %
function calendar(R) {
  const o = [R.d0]; let t = Date.parse(R.d0 + 'T00:00:00Z');
  for (const g of R.gaps) { t += g * 864e5; o.push(new Date(t).toISOString().slice(0, 10)); }
  return o;
}
const DATES = calendar(D.cal), R = D.r.map(v => v / 1e5), NR = R.length, YEAR = DATES.map(s => +s.slice(0, 4));
const I0 = D.i0, EDATES = DATES.slice(I0), NE = EDATES.length, LOSS = R.slice(I0).map(v => -v);
const VAR = {}; for (const l in D.var) { VAR[l] = {}; for (const m of MODELS) VAR[l][m] = D.var[l][m].map(v => v / 1e4); }
const firstYear = (dates, y) => { const i = dates.findIndex(d => +d.slice(0, 4) >= y); return i < 0 ? dates.length : i; };
const lastYear = (dates, y) => { const i = dates.findIndex(d => +d.slice(0, 4) > y); return (i < 0 ? dates.length : i) - 1; };
const countIn = (arr, a, b) => { let c = 0; for (const v of arr) if (v >= a && v <= b) c++; return c; };

// ---------------------------------------------------------------- distributions and tests (numpy / scipy definitions)
function ncdf(x) {                                                   // erfc approximation (Numerical Recipes), relative error < 1.2e-7
  const z = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.5 * z), y = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? 1 - y / 2 : y / 2;
}
const nsf = x => (x >= 0 ? 1 - ncdf(x) > 1e-6 ? 1 - ncdf(x) : ncdf(-x) : 1 - ncdf(x));   // upper tail without cancellation
function ninv(p) {                                                   // Acklam
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239],
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572],
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783],
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416], pl = 0.02425;
  if (p < pl) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
  if (p > 1 - pl) return -ninv(1 - p);
  const q = p - 0.5, r = q * q; return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}
const chi2sf1 = x => (x <= 0 ? 1 : 2 * nsf(Math.sqrt(x)));
const CRIT = { '0.01': 6.634896601021214, '0.05': 3.841458820694124, '0.1': 2.705543454095404 };   // chi2(1) quantiles
const SF4 = 3.167124183311998e-05;                                   // P(Z > 4), Z ~ N(0, 1)
function quantile(sorted, p) {                                       // numpy 'linear' rule
  const h = (sorted.length - 1) * p, lo = Math.floor(h), hi = Math.min(lo + 1, sorted.length - 1);
  return sorted[lo] + (h - lo) * (sorted[hi] - sorted[lo]);
}
const pctl = (a, q) => quantile([...a].sort((x, y) => x - y), q / 100);
function acf(x, K) {                                                 // demeaned, divided by the sum of squares
  const m = mean(x), y = x.map(v => v - m), d = sum(y.map(v => v * v)), o = [];
  for (let k = 1; k <= K; k++) { let s = 0; for (let t = k; t < y.length; t++) s += y[t] * y[t - k]; o.push(s / d); }
  return o;
}
function ljungBox(x, m) { const rho = acf(x, m), n = x.length; let q = 0; for (let k = 1; k <= m; k++) q += rho[k - 1] ** 2 / (n - k); return n * (n + 2) * q; }
function hillAlpha(r, share) {                                       // inference19.hill with k = round(share x loss days)
  const L = r.map(v => -v).filter(v => v > 0).sort((a, b) => b - a), k = roundHalfEven(share * L.length);
  if (k < 2 || k >= L.length) return { k, a: NaN };
  let s = 0; for (let i = 0; i < k; i++) s += Math.log(L[i]) - Math.log(L[k]);
  return { k, a: k / s };
}
function kupiecLR(x, n, a) {
  const ph = x / n, l0 = (n - x) * Math.log(1 - a) + x * Math.log(a), l1 = x > 0 && x < n ? (n - x) * Math.log(1 - ph) + x * Math.log(ph) : 0;
  return -2 * (l0 - l1);
}
function binomPmf(T, p) {                                            // P(X = x), x = 0..T, from log-space recursion
  const o = new Float64Array(T + 1), lp = Math.log(p), lq = Math.log1p(-p); let lc = 0;
  for (let x = 0; x <= T; x++) { if (x > 0) lc += Math.log((T - x + 1) / x); o[x] = Math.exp(lc + x * lp + (T - x) * lq); }
  return o;
}
function binomPpf(T, p, q) { const f = binomPmf(T, p); let c = 0; for (let x = 0; x <= T; x++) { c += f[x]; if (c >= q * (1 - 1e-12)) return x; } return T; }
function holm(p) {                                                   // Holm-adjusted p-values
  const m = p.length, o = p.map((_, i) => i).sort((a, b) => p[a] - p[b]), adj = new Array(m); let run = 0;
  o.forEach((i, j) => { run = Math.max(run, (m - j) * p[i]); adj[i] = Math.min(run, 1); });
  return adj;
}
function bhReject(p, q) {                                            // Benjamini-Hochberg rejections at FDR q
  const m = p.length, o = p.map((_, i) => i).sort((a, b) => p[a] - p[b]); let k = 0;
  o.forEach((i, j) => { if (p[i] <= q * (j + 1) / m) k = j + 1; });
  const rej = new Array(m).fill(false); o.slice(0, k).forEach(i => (rej[i] = true));
  return rej;
}

// ================================================================= Step 1: stylised facts of the BET
let bfKey = null, bfQQ = null;
function facts() {
  let y0 = +$('bf-y0').value, y1 = +$('bf-y1').value; const share = +$('bf-k').value / 100;
  if (y1 <= y0) { y1 = y0 + 1; $('bf-y1').value = y1; }
  $('bf-y0-v').textContent = y0; $('bf-y1-v').textContent = y1; $('bf-k-v').textContent = nf(100 * share, 1) + '%';
  const a = firstYear(DATES, y0), b = lastYear(DATES, y1), x = R.slice(a, b + 1), n = x.length;
  const m = mean(x), s = sdev(x), z = x.map(v => (v - m) / s), n4 = z.filter(v => Math.abs(v) > 4).length;
  if (bfKey !== a + ':' + b) {
    bfKey = a + ':' + b;
    const zs = [...z].sort((u, v) => u - v);
    bfQQ = { y: zs, x: zs.map((_, i) => ninv((i + 0.5) / n)), ar: acf(x, 50), aa: acf(x.map(Math.abs), 50), q: ljungBox(x.map(v => v * v), 10) };
  }
  const Q = bfQQ, lags = range(1, 50, 1), band = 1.96 / Math.sqrt(n), H = hillAlpha(x, share);
  plot('bf-qq', [
    { x: Q.x, y: Q.y, mode: 'markers', name: 'BET standardised daily log returns', marker: { color: K.blue, size: 4 }, hovertemplate: 'Normal %{x:.2f}<br>empirical %{y:.2f}<extra></extra>' },
    { x: [-5, 5], y: [-5, 5], mode: 'lines', name: 'Normal distribution (45-degree line)', line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`Quantile-quantile plot, ${y0}–${y1}`), legend: legendBelow(-0.22), xaxis: AX('Normal quantile', { range: [-5.2, 5.2] }), yaxis: AX('Empirical quantile') }));
  plot('bf-acf', [
    { x: lags.map(v => v - 0.2), y: Q.ar, type: 'bar', width: 0.4, name: 'ACF of returns r<sub>t</sub>', marker: { color: K.blue }, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags },
    { x: lags.map(v => v + 0.2), y: Q.aa, type: 'bar', width: 0.4, name: 'ACF of absolute returns |r<sub>t</sub>|', marker: { color: K.red }, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags },
    { x: [null], y: [null], type: 'bar', name: '95% band under i.i.d.', marker: { color: K.band }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Autocorrelation function'), barmode: 'overlay', bargap: 0, legend: legendBelow(-0.22),
    shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: -band, y1: band, fillcolor: K.band, opacity: 0.7, line: { width: 0 }, layer: 'below' }, hline(0, K.navy)],
    xaxis: AX('Lag (trading days)', { range: [0, 51] }), yaxis: AX('Autocorrelation', { range: [-0.08, 0.45] }) }));
  out('bf-out', [T.bf(y0, y1, ni(n), H.k, isFinite(H.a) ? nf(H.a, 2) : '—', n4, nf(2 * SF4 * n, 2)),
    T.bf2(nf(Q.aa[0], 2), nf(Q.ar[0], 2), ni(Q.q))]);
}

// ================================================================= Step 2: GARCH(1,1)-t volatility
function garch() {
  const G = D.garch, al = +$('bg-a').value, pp = +$('bg-p').value;
  const exact = Math.abs(al - G.alpha) < 5e-4 && Math.abs(pp - G.alpha - G.beta) < 5e-5;     // the estimates of the slide
  const a = exact ? G.alpha : al, b = exact ? G.beta : Math.max(pp - al, 0), p = a + b;
  $('bg-a-v').textContent = nf(a, 3); $('bg-p-v').textContent = nf(p, 4) + ' (β = ' + nf(b, 3) + ')';
  const sig = new Array(NR); let s2 = G.s2_0; sig[0] = Math.sqrt(s2);
  for (let t = 1; t < NR; t++) { s2 = G.omega + a * (R[t - 1] - G.mu) ** 2 + b * s2; sig[t] = Math.sqrt(s2); }
  let im = 0; for (let t = 1; t < NR; t++) if (sig[t] > sig[im]) im = t;
  let nOut = 0; for (let t = 0; t < NR; t++) if (Math.abs(R[t]) > 2 * sig[t]) nOut++;
  plot('bg-chart', [
    { x: DATES, y: R, mode: 'lines', name: 'BET daily log return (%)', line: { color: K.blue, width: 0.6 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: DATES, y: sig.map(v => 2 * v), mode: 'lines', name: '±2σ̂<sub>t</sub>, GARCH(1,1)-t', line: { color: K.red, width: 1 }, hovertemplate: '%{x}: σ̂ = %{customdata:.2f}%<extra></extra>', customdata: sig },
    { x: DATES, y: sig.map(v => -2 * v), mode: 'lines', showlegend: false, line: { color: K.red, width: 1 }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`α = ${a.toFixed(3)}, β = ${b.toFixed(3)}, α + β = ${p.toFixed(4)}`), legend: legendBelow(-0.12), shapes: [hline(0, K.navy)],
    xaxis: AX('', { range: [DATES[0], DATES[NR - 1]] }), yaxis: AX('%', { range: [-16, 16] }) }));
  const hl = p < 1 ? Math.log(0.5) / Math.log(p) : Infinity;
  const lines = [T.bg(nf(a, 3), nf(b, 3), nf(p, 4), T.hl(hl)), T.bg2(nf(sig[im], 2) + '%', dfmt(DATES[im]), nf(sig[NR - 1], 2) + '%', dfmt(DATES[NR - 1]))];
  if (p < 1) { const lv = Math.sqrt(G.omega / (1 - p)); lines.push(T.bg3(nf(lv, 2) + '%', nf(lv * Math.sqrt(G.ppy), 1) + '%')); } else lines.push(T.bg3n);
  lines.push(T.bg4(ni(nOut), pct(nOut / NR, 1)));
  out('bg-out', lines);
}

// ================================================================= Step 3: losses and VaR, 2020-2026
function varPath() {
  const m = $('bv-m').value, lev = $('bv-l').value, al = +lev / 100, y0 = +$('bv-y0').value, f = +$('bv-t').value / 1000;
  const a = firstYear(EDATES, y0), n = NE - a, b = a + Math.round(f * (n - 1)), V = VAR[lev], H = D.hits[lev];
  $('bv-y0-v').textContent = y0; $('bv-t-v').textContent = dfmt(EDATES[b]);
  const dd = EDATES.slice(a, b + 1), hf = H.FHS.filter(i => i >= a && i <= b);
  plot('bv-chart', [
    { x: dd, y: LOSS.slice(a, b + 1).map(v => Math.max(v, 0)), type: 'bar', name: 'Daily loss (gains set to 0)', marker: { color: K.teal, opacity: 0.7 }, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x: dd, y: V[m].slice(a, b + 1), mode: 'lines', name: m === 'Normal' ? `Normal VaR ${levChart(al)} (500 days)` : `${m} VaR ${levChart(al)}`, line: { color: m === 'Normal' ? K.orange : MC[m], width: 1.2 }, hovertemplate: '%{x}: ' + m + ' %{y:.2f}%<extra></extra>' },
    { x: dd, y: V.FHS.slice(a, b + 1), mode: 'lines', name: `FHS VaR ${levChart(al)} (GARCH-t filter)`, line: { color: K.red, width: 1.2 }, hovertemplate: '%{x}: FHS %{y:.2f}%<extra></extra>' },
    { x: hf.map(i => EDATES[i]), y: hf.map(i => LOSS[i]), mode: 'markers', name: `Loss above FHS VaR ${levChart(al)}`, marker: { color: K.black, size: 6 }, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' }
  ], layout({ bargap: 0, legend: legendBelow(-0.12), xaxis: AX('', { range: [EDATES[a], EDATES[NE - 1]] }), yaxis: AX('Loss = negative log return (%)', { rangemode: 'tozero' }) }));
  let jm = a; for (let i = a; i <= b; i++) if (V.FHS[i] > V.FHS[jm]) jm = i;
  const nb = b - a + 1;
  out('bv-out', [T.bv(dfmt(EDATES[a]), dfmt(EDATES[b]), ni(nb), nf(al * nb, 1), levTxt(al)),
    T.bv2(hf.length, m, countIn(H[m], a, b)),
    T.bv3(nf(V.FHS[jm], 1) + '%', dfmt(EDATES[jm]), dfmt(EDATES[b]), nf(V.FHS[b], 2) + '%', m, nf(V[m][b], 2) + '%')]);
}

// ================================================================= Step 4: breach rates
function breachRates() {
  const lev = $('br-l').value, al = +lev / 100, adj = $('br-adj').value;
  let y0 = +$('br-y0').value, y1 = +$('br-y1').value;
  if (y1 < y0) { y1 = y0; $('br-y1').value = y1; }
  $('br-y0-v').textContent = y0; $('br-y1-v').textContent = y1;
  const a = firstYear(EDATES, y0), b = lastYear(EDATES, y1), n = b - a + 1, H = D.hits[lev];
  const x = MODELS.map(m => countIn(H[m], a, b)), rate = x.map(v => v / n);
  const lo = binomPpf(n, al, 0.025) / n, hi = binomPpf(n, al, 0.975) / n;
  const p = x.map(v => chi2sf1(kupiecLR(v, n, al)));
  const rej = adj === 'none' ? p.map(v => v <= 0.05) : adj === 'holm' ? holm(p).map(v => v <= 0.05) : bhReject(p, 0.05);
  const top = Math.max(...rate, hi) * 100;
  plot('br-chart', [
    { x: MODELS, y: rate.map(v => 100 * v), type: 'bar', width: 0.55, showlegend: false, marker: { color: MODELS.map(m => MC[m]) }, text: rate.map(v => (100 * v).toFixed(2) + '%'), textposition: 'outside', cliponaxis: false, textfont: { color: K.black, size: 11 },
      hovertemplate: '%{x}: %{customdata[0]} breaches in ' + n + ' days (%{y:.2f}%)<br>Kupiec p = %{customdata[1]}<extra></extra>', customdata: x.map((v, i) => [v, p[i].toPrecision(3)]) },
    { x: [null], y: [null], type: 'bar', name: `95% binomial band if the rate is ${levChart(al)}`, marker: { color: K.band }, hoverinfo: 'skip' },
    { x: [null], y: [null], mode: 'lines', name: `Target: ${levChart(al)}`, line: { color: K.black, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`${EDATES[a]} to ${EDATES[b]}, T = ${n} days`), legend: legendBelow(-0.14),
    shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: 100 * lo, y1: 100 * hi, fillcolor: K.band, opacity: 0.7, line: { width: 0 }, layer: 'below' },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 100 * al, y1: 100 * al, line: { color: K.black, width: 1.5, dash: 'dash' } }],
    xaxis: AX(''), yaxis: AX(`Share of days with loss > VaR ${levChart(al)} (%)`, { range: [0, 1.15 * top + 0.1] }) }));
  const inn = MODELS.filter((_, i) => rate[i] >= lo - 1e-12 && rate[i] <= hi + 1e-12);
  out('br-out', [T.br(dfmt(EDATES[a]), dfmt(EDATES[b]), ni(n), levTxt(al), pct(lo, 2), pct(hi, 2), inn.length ? inn.join(', ') : T.none),
    T.br2(MODELS.map((m, i) => `${m} ${pct(rate[i], 2)}, p ${p[i] < 0.001 ? '' : '= '}${pv(p[i])}`).join('; ')),
    T.br3(T.adj[adj], MODELS.filter((_, i) => rej[i]).join(', ') || T.none)]);
}

// ================================================================= power of the Kupiec test
const KP_GRID = range(0.002, 0.0405, 0.0005);
const kpCache = {};
function kupiecRegion(Tn, crit, p0) {
  const rej = new Uint8Array(Tn + 1);
  for (let x = 0; x <= Tn; x++) if (kupiecLR(x, Tn, p0) > crit) rej[x] = 1;
  return rej;
}
function kupiecPower(Tn, p1, rej) { const f = binomPmf(Tn, p1); let s = 0; for (let x = 0; x <= Tn; x++) if (rej[x]) s += f[x]; return s; }
function powerCurve(Tn, lv) {
  const key = Tn + ':' + lv; if (kpCache[key]) return kpCache[key];
  const rej = kupiecRegion(Tn, CRIT[lv], 0.01), y = KP_GRID.map(p => kupiecPower(Tn, p, rej));
  let mde = NaN; for (let k = 1; 0.01 + 0.0005 * k < 0.2; k++) { const p1 = 0.01 + 0.0005 * k; if (kupiecPower(Tn, p1, rej) >= 0.8) { mde = p1; break; } }
  let hiR = -1; for (let x = 0; x <= Tn; x++) if (rej[x] && x > 0.01 * Tn) { hiR = x; break; }
  let loR = -1; for (let x = 0; x < 0.01 * Tn; x++) if (rej[x]) loR = x;
  kpCache[key] = { rej, y, mde, loR, hiR, size: kupiecPower(Tn, 0.01, rej) };
  return kpCache[key];
}
function kupiecPowerBlock() {
  const Tn = +$('kp-T').value, pi = +$('kp-pi').value / 100, lv = $('kp-a').value;
  $('kp-T-v').textContent = ni(Tn); $('kp-pi-v').textContent = pct(pi, 2);
  const base = [[250, K.orange], [1000, K.blue], [D.power.T, K.red]];
  const tr = base.map(([t, c]) => ({ x: KP_GRID.map(v => 100 * v), y: powerCurve(t, lv).y, mode: 'lines', name: `T = ${t} days`, line: { color: c, width: 2 }, hovertemplate: `T = ${t}, true rate %{x:.2f}%: %{y:.1%}<extra></extra>` }));
  if (!base.some(([t]) => t === Tn)) tr.push({ x: KP_GRID.map(v => 100 * v), y: powerCurve(Tn, lv).y, mode: 'lines', name: `T = ${Tn} days (chosen)`, line: { color: K.purple, width: 2, dash: 'dot' }, hovertemplate: `T = ${Tn}, true rate %{x:.2f}%: %{y:.1%}<extra></extra>` });
  const P = powerCurve(Tn, lv), pw = kupiecPower(Tn, pi, P.rej);
  tr.push({ x: [100 * pi], y: [pw], mode: 'markers', name: `T = ${Tn}, true rate ${(100 * pi).toFixed(2)}%`, marker: { color: K.purple, size: 11, symbol: 'diamond', line: { color: '#fff', width: 1.5 } }, hovertemplate: 'power %{y:.1%}<extra></extra>' });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Null: 1%', line: { color: K.black, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' });
  plot('kp-chart', tr, layout({ title: ttl(`Kupiec test at the ${(100 * +lv).toFixed(0)}% level`), legend: legendBelow(-0.16),
    shapes: [hline(0.8, K.navy, 'dash'), hline(+lv, K.navy, 'dot'), vline(1, K.black, 'dash')],
    xaxis: AX('True breach rate of the VaR 1% model (%)', { range: [0, 4.1] }), yaxis: AX('Rejection probability of the Kupiec test', { tickformat: '.0%', range: [0, 1.02] }) }));
  out('kp-out', [T.kp(ni(Tn), pct(pi, 2), (100 * +lv).toFixed(0) + '%', pct(pw, 0)), T.kp2(T.reg(P.loR, P.hiR)),
    T.kp3(isFinite(P.mde) ? pct(P.mde, 2) : '—', pct(P.size, 1))]);
}

// ================================================================= nonstandard errors: the mini-multiverse
const NF = D.nse_forks, IDX = Object.keys(D.nse);
const NX = {}; IDX.forEach(lab => {
  const S = D.nse[lab], x = S.x.map(v => v / 1e9), g = []; let i = 0;
  S.n.forEach(c => { g.push(x.slice(i, i + c)); i += c; });
  NX[lab] = g;
});
function varianceRatio(x, q) {                                       // Chapter 2, eff_tests.variance_ratio: Lo-MacKinlay corrections
  const T0 = x.length, mu = mean(x); let s2 = 0; for (const v of x) s2 += (v - mu) ** 2;
  let s = 0, vc = 0; for (let i = 0; i < T0; i++) { s += x[i]; if (i >= q) s -= x[i - q]; if (i >= q - 1) vc += (s - q * mu) ** 2; }
  return vc / (q * (T0 - q + 1) * (1 - q / T0)) / (s2 / (T0 - 1));
}
function corr(a, b) { const ma = mean(a), mb = mean(b); let sab = 0, saa = 0, sbb = 0; for (let i = 0; i < a.length; i++) { const u = a[i] - ma, v = b[i] - mb; sab += u * v; saa += u * u; sbb += v * v; } return sab / Math.sqrt(saa * sbb); }
const measureOf = { '|VR(5) - 1|': x => Math.abs(varianceRatio(x, 5) - 1), '|VR(21) - 1|': x => Math.abs(varianceRatio(x, 21) - 1), 'AR(1) R$^2$': x => corr(x.slice(1), x.slice(0, -1)) ** 2 };
function annualMeasure(groups, outlier, measure, q) {
  let m = groups.map(measureOf[measure]);
  const lo = pctl(m, q), hi = pctl(m, 100 - q);
  if (outlier === 'Winsorised') m = m.map(v => Math.min(Math.max(v, lo), hi));
  else if (outlier === 'Trimmed') m = m.map(v => (v >= lo && v <= hi ? v : NaN));
  return m;
}
function yearlyChange(m, model) {
  const t = m.map((_, i) => i), ok = m.map(v => !isNaN(v));
  if (model === 'Linear trend') {
    const xs = t.filter((_, i) => ok[i]), ys = m.filter((_, i) => ok[i]), n = xs.length, mx = mean(xs), my = mean(ys);
    let sxy = 0, sxx = 0, syy = 0; for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; syy += (ys[i] - my) ** 2; }
    const b = sxy / sxx, r2 = sxy * sxy / (sxx * syy), se = Math.sqrt((1 - r2) * syy / sxx / (n - 2));
    return [100 * b / my, 100 * se / my];
  }
  const d = [];
  for (let i = 1; i < m.length; i++) { const v = model === 'Log difference' ? 100 * (Math.log(m[i]) - Math.log(m[i - 1])) : 100 * (m[i] / m[i - 1] - 1); if (!isNaN(v)) d.push(v); }
  return [mean(d), sdev(d) / Math.sqrt(d.length)];
}
const nmCache = {};
function multiverse(lab, q) {
  const key = lab + ':' + q; if (nmCache[key]) return nmCache[key];
  const rows = [];
  for (const o of NF.outliers) for (const ms of NF.measures) { const m = annualMeasure(NX[lab], o, ms, q); for (const mo of NF.models) { const [est, se] = yearlyChange(m, mo); rows.push({ outlier: o, measure: ms, model: mo, est, se }); } }
  nmCache[key] = rows; return rows;
}
const symlog = y => (Math.abs(y) <= 10 ? y : Math.sign(y) * 10 * (1 + Math.log10(Math.abs(y) / 10)));
const MEAS_COL = { '|VR(5) - 1|': K.blue, '|VR(21) - 1|': K.green, 'AR(1) R$^2$': K.red };
const MEAS_LAB = { '|VR(5) - 1|': '|VR(5) − 1|', '|VR(21) - 1|': '|VR(21) − 1|', 'AR(1) R$^2$': 'AR(1) R²' };
const OUT_SYM = { None: 'circle', Winsorised: 'square', Trimmed: 'triangle-up' };
const OUT_OFF = { None: -0.22, Winsorised: 0, Trimmed: 0.22 }, MEAS_OFF = { '|VR(5) - 1|': -0.06, '|VR(21) - 1|': 0, 'AR(1) R$^2$': 0.06 };
function nseBlock() {
  const fm = $('nm-model').value, fs = $('nm-meas').value, fo = $('nm-ol').value, q = +$('nm-q').value;
  $('nm-q-v').textContent = nf(q, 1) + '%';
  const tr = [], shapes = [], ann = [], lines = []; let ymin = -10, ymax = 10;
  IDX.forEach((lab, k) => {
    const xa = k ? 'x2' : 'x', all = multiverse(lab, q), rows = all.filter(r => (fm === 'all' || r.model === fm) && (fs === 'all' || r.measure === fs) && (fo === 'all' || r.outlier === fo));
    const e = rows.map(r => r.est), q25 = pctl(e, 25), q50 = pctl(e, 50), q75 = pctl(e, 75), mse = median(rows.map(r => r.se));
    for (const ms of NF.measures) for (const o of NF.outliers) {
      const rr = rows.filter(r => r.measure === ms && r.outlier === o); if (!rr.length) continue;
      tr.push({ x: rr.map(r => NF.models.indexOf(r.model) + OUT_OFF[o] + MEAS_OFF[ms]), y: rr.map(r => symlog(r.est)), xaxis: xa, yaxis: 'y', mode: 'markers', showlegend: false,
        marker: { color: MEAS_COL[ms], symbol: OUT_SYM[o], size: 9, line: { color: K.black, width: 0.5 } }, customdata: rr.map(r => [r.est.toFixed(2), r.se.toFixed(2)]),
        hovertemplate: `${lab}<br>${MEAS_LAB[ms]}, outliers: ${o}<br>%{text}: %{customdata[0]}% a year (SE %{customdata[1]})<extra></extra>`, text: rr.map(r => r.model) });
    }
    all.forEach(r => { ymin = Math.min(ymin, symlog(r.est)); ymax = Math.max(ymax, symlog(r.est)); });
    const xr = k ? 'x2 domain' : 'x domain';
    shapes.push({ type: 'rect', xref: xr, yref: 'y', x0: 0, x1: 1, y0: symlog(q25), y1: symlog(q75), fillcolor: K.amber, opacity: 0.18, line: { width: 0 }, layer: 'below' },
      { type: 'line', xref: xr, yref: 'y', x0: 0, x1: 1, y0: symlog(q50), y1: symlog(q50), line: { color: K.amber, width: 2, dash: 'dash' } },
      { type: 'line', xref: xr, yref: 'y', x0: 0, x1: 1, y0: 0, y1: 0, line: { color: K.black, width: 1 } });
    ann.push({ xref: xr, yref: 'paper', x: 0.5, y: 1.0, yanchor: 'bottom', showarrow: false, text: `${lab}: IQR = ${(q75 - q25).toFixed(1)} pp, median = ${q50.toFixed(1)}%`, font: { size: 12, color: K.navy } });
    lines.push(T.nm(lab, rows.length, nf(q50, 1) + '%', nf(q75 - q25, 1), nf(1.35 * mse, 1)));
  });
  NF.measures.forEach(ms => tr.push({ x: [null], y: [null], mode: 'markers', name: 'Measure: ' + MEAS_LAB[ms], marker: { color: MEAS_COL[ms], size: 9, line: { color: K.black, width: 0.5 } }, hoverinfo: 'skip' }));
  NF.outliers.forEach(o => tr.push({ x: [null], y: [null], mode: 'markers', name: 'Outliers: ' + o, marker: { color: '#fff', symbol: OUT_SYM[o], size: 9, line: { color: K.black, width: 1 } }, hoverinfo: 'skip' }));
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Median of the paths shown', line: { color: K.amber, width: 2, dash: 'dash' }, hoverinfo: 'skip' });
  tr.push({ x: [null], y: [null], type: 'bar', name: 'Interquartile range (nonstandard error)', marker: { color: K.amber, opacity: 0.3 }, hoverinfo: 'skip' });
  const tv = [-1e3, -100, -10, 0, 10, 100, 1e3, 1e4, 1e5], tickvals = tv.map(symlog), ticktext = tv.map(v => (v < 0 ? '−' : '') + Math.abs(v).toLocaleString('en-US'));
  const xax = d => AX('', { domain: d, range: [-0.5, 2.5], tickvals: [0, 1, 2], ticktext: NF.models.map(m => m.replace(' ', '<br>')), zeroline: false });
  plot('nm-chart', tr, layout({ legend: legendBelow(-0.16), shapes, annotations: ann, margin: { l: 64, r: 12, t: 34, b: 40 },
    xaxis: xax([0, 0.47]), xaxis2: xax([0.53, 1]), yaxis: AX('Average yearly change (%), log scale beyond ±10%', { tickvals, ticktext, range: [ymin - 2, ymax + 3], zeroline: false }) }));
  out('nm-out', lines);
}

// ================================================================= integrated case studies (Quantlets/Ch_19/integrated_cases.py)
const Z99 = 2.3263478740408408;                                      // scipy.stats.norm.ppf(0.99)
const dec = (a, k) => a.map(v => (v === null ? NaN : v / 10 ** k));
function christoffersen(hit, dates) {                                // LR_ind (Chapter 8, mfm_data.christoffersen); with dates: consecutive calendar days only
  let n00 = 0, n01 = 0, n10 = 0, n11 = 0;
  for (let t = 1; t < hit.length; t++) { if (dates && Date.parse(dates[t]) - Date.parse(dates[t - 1]) !== 864e5) continue; const a = hit[t - 1], b = hit[t]; if (!a && !b) n00++; else if (!a && b) n01++; else if (a && !b) n10++; else n11++; }
  const xl = (n, q) => (n > 0 ? n * Math.log(q) : 0);
  const p01 = n01 / (n00 + n01), p11 = n10 + n11 > 0 ? n11 / (n10 + n11) : 0, pi = (n01 + n11) / (n00 + n01 + n10 + n11);
  const lind = -2 * (xl(n00 + n10, 1 - pi) + xl(n01 + n11, pi) - (xl(n00, 1 - p01) + xl(n01, p01) + xl(n10, 1 - p11) + xl(n11, p11)));
  return lind;
}
function backtest(loss, v, a, dates) {
  const hit = loss.map((l, i) => (l > v[i] ? 1 : 0)), x = sum(hit), n = hit.length;
  const luc = kupiecLR(x, n, a), lind = christoffersen(hit, dates);
  return { x, n, rate: x / n, p_uc: chi2sf1(luc), p_ind: chi2sf1(lind), p_cc: Math.exp(-(luc + lind) / 2), hit };
}
function hsVaR(L, a) { return quantile([...L].sort((x, y) => x - y), 1 - a); }          // numpy 'linear'
function hsES(L, a) {                                                // risk_measures.hs_es: fractional weight on the last loss
  const s = [...L].sort((x, y) => y - x), na = s.length * a, m = Math.floor(na + 1e-9), fr = Math.max(na - m, 0);
  let t = 0; for (let i = 0; i < m; i++) t += s[i];
  if (fr > 1e-12 && m < s.length) t += fr * s[m];
  return t / na;
}
const sharesCol = { Equities: K.purple, Treasuries: K.teal, Credit: K.amber, Gold: '#795548' };

// ---------------------------------------------------------------- 1. multi-asset portfolio
const IP = D.ip, IPD = calendar(IP.cal), IPR = dec(IP.ret, 5), IPS = dec(IP.sig, 6), IPL = IPR.map(v => -v);
const IPV = { n: IPS.map(s => Z99 * s), fhs: dec(IP.var_fhs, 5), hs: dec(IP.var_hs, 5) };
const IPVG = dec(IP.vol_gmv, 4), IPVL = dec(IP.vol_lw, 4);
const IPLAB = { n: 'VaR 1%, DCC-Normal', fhs: 'VaR 1%, DCC-FHS', hs: 'VaR 1%, HS 500 days' };
const IPCOL = { n: K.red, fhs: K.green, hs: K.orange };
function portfolioBlock() {
  const m = $('ip-m').value, y0 = +$('ip-y0').value, f = +$('ip-t').value / 1000;
  const a = firstYear(IPD, y0), b = a + Math.round(f * (IPD.length - 1 - a));
  $('ip-y0-v').textContent = y0; $('ip-t-v').textContent = dfmt(IPD[b]);
  const dd = IPD.slice(a, b + 1), L = IPL.slice(a, b + 1), V = IPV[m].slice(a, b + 1), bt = backtest(L, V, 0.01);
  const hd = dd.filter((_, i) => bt.hit[i]), hl = L.filter((_, i) => bt.hit[i]);
  plot('ip-c1', [
    { x: dd, y: IPVG.slice(a, b + 1), mode: 'lines', name: 'GMV, sample covariance', line: { color: K.orange, width: 1.3 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: dd, y: IPVL.slice(a, b + 1), mode: 'lines', name: 'GMV, Ledoit-Wolf shrinkage', line: { color: K.blue, width: 1.3 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ title: ttl('(a) Ch. 4: GMV risk'), legend: legendBelow(-0.18), xaxis: AX('', { range: [IPD[a], IPD[IPD.length - 1]] }), yaxis: AX('1-year volatility (%)') }));
  plot('ip-c2', [
    { x: dd, y: L.map(v => Math.max(v, 0)), type: 'bar', name: `Daily loss of ${IP.choice}`, marker: { color: K.band }, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x: dd, y: V, mode: 'lines', name: IPLAB[m], line: { color: IPCOL[m], width: 1.2 }, hovertemplate: '%{x}: VaR %{y:.2f}%<extra></extra>' },
    { x: hd, y: hl, mode: 'markers', name: `Loss above ${IPLAB[m].replace('VaR 1%, ', '')} VaR`, marker: { color: K.navy, size: 6 }, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' }
  ], layout({ title: ttl('(b) Ch. 6-8: VaR 1%'), bargap: 0, legend: legendBelow(-0.18), xaxis: AX('', { range: [IPD[a], IPD[IPD.length - 1]] }), yaxis: AX('Loss, VaR (%)', { rangemode: 'tozero' }) }));
  const m1 = IPD[b].slice(0, 7), mi = IP.months.filter(x => x >= IPD[a].slice(0, 7) && x <= m1);
  const j0 = IP.months.indexOf(mi[0]), j1 = IP.months.indexOf(m1);
  plot('ip-c3', Object.keys(IP.shares).map(c => ({ x: mi.map(s => s + '-15'), y: dec(IP.shares[c], 4).slice(j0, j1 + 1).map(v => 100 * v), mode: 'lines', name: c, line: { color: sharesCol[c], width: 1.4 }, hovertemplate: '%{x|%b %Y}: ' + c + ' %{y:.0f}%<extra></extra>' })),
    layout({ title: ttl('(c) Ch. 7: Euler shares'), legend: legendBelow(-0.18), shapes: [hline(0, K.navy)], xaxis: AX('', { range: [IPD[a], IPD[IPD.length - 1]] }), yaxis: AX('Share of risk (%)') }));
  const sh = Object.keys(IP.shares).map(c => `${T.cls[c]} ${pct(IP.shares[c][j1] / 1e4, 0)}`).join(', ');
  out('ip-out', [T.ip(dfmt(IPD[a]), dfmt(IPD[b]), ni(bt.n), nf(0.01 * bt.n, 1)),
    T.ip2(T.ipm[m], bt.x, pct(bt.rate, 2), pv(bt.p_uc), pv(bt.p_ind), pv(bt.p_cc)),
    T.ip3(MON[+m1.slice(5) - 1] + ' ' + m1.slice(0, 4), sh)]);
}

// ---------------------------------------------------------------- 2. Bitcoin
const IB = D.ib, IBD = calendar(IB.cal), IBL = dec(IB.loss, 5), IBF = dec(IB.fvar, 5);
const IBDD = calendar(IB.dcal), IBR = dec(IB.daily, 5), IBW = calendar(IB.wcal);
const IBpos = IBD.map(d => { let lo = 0, hi = IBDD.length; while (lo < hi) { const mid = (lo + hi) >> 1; if (IBDD[mid] < d) lo = mid + 1; else hi = mid; } return lo; });  // daily returns before day d
function bitcoinBlock() {
  const a = +$('ib-a').value / 100, w = +$('ib-w').value;
  $('ib-a-v').textContent = pct(a, 2); $('ib-w-v').textContent = ni(w);
  const z = Math.abs(ninv(a)), vh = IBF.map(v => (Math.abs(a - 0.01) < 1e-12 ? Z99 : z) * Math.sqrt(v));
  const vs = IBpos.map(p => hsVaR(IBR.slice(Math.max(0, p - w), p).map(v => -v), a));
  const bh = backtest(IBL, vh, a, IBD), bs = backtest(IBL, vs, a, IBD);
  const ep = IB.episodes.map(e => ({ type: 'rect', xref: 'x', yref: 'paper', x0: e.start, x1: e.end || IBW[IBW.length - 1], y0: 0, y1: 1, fillcolor: K.band, opacity: 0.8, line: { width: 0 }, layer: 'below' }));
  plot('ib-c1', [
    { x: IBW, y: dec(IB.bsadf, 4), mode: 'lines', name: 'BSADF statistic (weekly)', line: { color: K.blue, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: IBW, y: dec(IB.cv95, 4), mode: 'lines', name: '95% critical value, wild bootstrap', line: { color: K.red, width: 1.2, dash: 'dash' }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: [null], y: [null], type: 'bar', name: 'Explosive episode', marker: { color: K.band }, hoverinfo: 'skip' }
  ], layout({ title: ttl('(a) Ch. 17: BSADF'), shapes: ep, legend: legendBelow(-0.18), xaxis: AX(''), yaxis: AX('ADF statistic') }));
  const lab = levChart(a);
  plot('ib-c2', [
    { x: IBD, y: IBL.map(v => Math.max(v, 0)), type: 'bar', name: 'Daily loss (UTC day)', marker: { color: K.band }, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x: IBD, y: vh, mode: 'lines', name: `VaR ${lab}, log-HAR forecast`, line: { color: K.red, width: 1.2 }, connectgaps: false, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: IBD, y: vs, mode: 'lines', name: `VaR ${lab}, HS ${w} days`, line: { color: K.green, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: IBD.filter((_, i) => bh.hit[i]), y: IBL.filter((_, i) => bh.hit[i]), mode: 'markers', name: 'Loss above log-HAR VaR', marker: { color: K.navy, size: 7 }, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' }
  ], layout({ title: ttl(`(b) Ch. 8-9: VaR ${lab}`), bargap: 0, legend: legendBelow(-0.18), xaxis: AX(''), yaxis: AX('Loss, VaR (%)', { rangemode: 'tozero' }) }));
  plot('ib-c3', [
    { x: IB.months.map(s => s + '-15'), y: dec(IB.ill_btc, 7), mode: 'lines', name: 'Bitcoin', line: { color: K.orange, width: 1.4 }, hovertemplate: '%{x|%b %Y}: %{y:.4f}<extra></extra>' },
    { x: IB.months.map(s => s + '-15'), y: dec(IB.ill_spy, 7), mode: 'lines', name: 'SPY', line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x|%b %Y}: %{y:.4f}<extra></extra>' }
  ], layout({ title: ttl('(c) Ch. 10: Amihud'), legend: legendBelow(-0.18), xaxis: AX(''), yaxis: AX('bp per USD 1M (log)', { type: 'log', dtick: 1, exponentformat: 'power' }) }));
  out('ib-out', [T.ib(dfmt(IBD[0]), dfmt(IBD[IBD.length - 1]), ni(bh.n), levTxt(a), nf(a * bh.n, 1)),
    T.ib2(bh.x, pv(bh.p_uc), pv(bh.p_ind), nf(mean(vh), 2) + '%'),
    T.ib3(ni(w), bs.x, pv(bs.p_uc), pv(bs.p_ind), nf(mean(vs), 2) + '%'),
    T.ib4(nf(IB.gsadf, 2), nf(IB.cv_gsadf, 2), nf(IB.amihud, 4), nf(IB.amihud_spy, 4))]);
}

// ---------------------------------------------------------------- 3. a Romanian investor
const IR = D.ir, IRW = calendar(IR.wcal), IRS = dec(IR.stoxx, 8), IRB = dec(IR.bet, 8), IRF = dec(IR.fx, 8);
const IRDAILY = {}; for (const k in IR.daily) IRDAILY[k] = { d: calendar(IR.daily[k].cal), r: dec(IR.daily[k].r, 8) };
const QS = range(2, 20, 1);
function vrz(x, q) {                                                 // Chapter 2, eff_tests.variance_ratio: robust z*
  const T0 = x.length, mu = mean(x), e = x.map(v => v - mu), s2 = sum(e.map(v => v * v)), varA = s2 / (T0 - 1);
  let s = 0, vc = 0; for (let i = 0; i < T0; i++) { s += x[i]; if (i >= q) s -= x[i - q]; if (i >= q - 1) vc += (s - q * mu) ** 2; }
  const vr = vc / (q * (T0 - q + 1) * (1 - q / T0)) / varA;
  let th = 0; for (let j = 1; j < q; j++) { let c = 0; for (let t = j; t < T0; t++) c += e[t] ** 2 * e[t - j] ** 2; th += (2 * (q - j) / q) ** 2 * T0 * c / (s2 * s2); }
  return { vr, z: Math.sqrt(T0) * (vr - 1) / Math.sqrt(th) };
}
const vrCache = {};
function vrProfile(k, y0) {
  const key = k + y0; if (vrCache[key]) return vrCache[key];
  const S = IRDAILY[k], i = firstYear(S.d, y0), x = S.r.slice(i);
  vrCache[key] = { z: QS.map(q => vrz(x, q).z), vr2: vrz(x, 2).vr, n: x.length };
  return vrCache[key];
}
function hedgeRatio(W) {                                             // rolling Cov(s_ron, f) / Var(f), known at the start of the week
  const sr = IRS.map((v, i) => v + IRF[i]), h = new Array(IRW.length).fill(NaN);
  for (let t = W; t < IRW.length; t++) {
    const a = sr.slice(t - W, t), f = IRF.slice(t - W, t), ma = mean(a), mf = mean(f);
    let c = 0, v = 0; for (let i = 0; i < W; i++) { c += (a[i] - ma) * (f[i] - mf); v += (f[i] - mf) ** 2; }
    h[t] = c / v;
  }
  return h;
}
const IRCH = ['Unhedged', 'Min-variance hedge', 'Hedged'], IRCOL = { 'Unhedged': K.orange, 'Min-variance hedge': K.purple, 'Hedged': K.blue };
function romaniaBlock() {
  const W = +$('ir-w').value, y0 = +$('ir-y0').value;
  $('ir-w-v').textContent = ni(W); $('ir-y0-v').textContent = y0;
  const SER = [['eurron', K.red, 'EUR/RON (BNR)'], ['bet', K.blue, 'BET'], ['stoxx', K.green, 'Euro Stoxx 50']];
  const P = SER.map(([k]) => vrProfile(k, y0));
  plot('ir-c1', SER.map(([k, c, lab], j) => ({ x: QS, y: P[j].z, mode: 'lines+markers', name: lab, line: { color: c, width: 1.4 }, marker: { size: 5 }, hovertemplate: `${lab}, q = %{x}: z* = %{y:.2f}<extra></extra>` }))
    .concat([{ x: [null], y: [null], type: 'bar', name: '|z*| < 1.96', marker: { color: K.band }, hoverinfo: 'skip' }]),
    layout({ title: ttl('(a) Ch. 2: variance ratios'), legend: legendBelow(-0.24), shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: -1.96, y1: 1.96, fillcolor: K.band, opacity: 0.7, line: { width: 0 }, layer: 'below' }, hline(0, K.navy)],
      xaxis: AX('Horizon q (days)', { tickvals: [2, 5, 10, 15, 20] }), yaxis: AX('z*(q)') }));
  const h = hedgeRatio(W), sr = IRS.map((v, i) => v + IRF[i]);
  // exact simple return of the 50/50 portfolio with a forward on h times the euro leg (zero carry), then the log return
  const pr = (i, hh) => Math.log1p(0.5 * Math.expm1(IRB[i]) + 0.5 * (Math.expm1(sr[i]) - hh * Math.expm1(IRF[i])));
  const port = { 'Unhedged': IRB.map((_, i) => pr(i, 0)), 'Hedged': IRB.map((_, i) => pr(i, 1)), 'Min-variance hedge': IRB.map((_, i) => pr(i, h[i])) };
  const firstH = h.findIndex(v => isFinite(v)), start = IRW.findIndex(d => d >= IR.periods.full[0]), i0 = Math.max(firstH, start);
  plot('ir-c2', [
    { x: IRW, y: h, mode: 'lines', name: `h*: min-variance, ${W}-week rolling`, line: { color: K.purple, width: 1.4 }, hovertemplate: '%{x}: h* = %{y:.2f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: 'Full hedge (h = 1)', line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl('(b) Ch. 3, 6: hedge ratio'), legend: legendBelow(-0.18), shapes: [hline(1, K.navy, 'dash'), hline(0, K.navy)], xaxis: AX(''), yaxis: AX('Hedge ratio h') }));
  const PER = [['full', '2008-26'], ['2008', '2008-12'], ['2020', '2020-26']], es = {};
  for (const [p] of PER) {
    const [a, b] = IR.periods[p], idx = []; for (let i = i0; i < IRW.length; i++) if (IRW[i] >= a && IRW[i] <= b) idx.push(i);
    es[p] = {}; for (const c of IRCH) es[p][c] = hsES(idx.map(i => -100 * port[c][i]), 0.025);
  }
  plot('ir-c3', IRCH.map(c => ({ x: PER.map(([, l]) => l), y: PER.map(([p]) => es[p][c]), type: 'bar', name: T.irlab[c], marker: { color: IRCOL[c] }, hovertemplate: '%{x}: ES %{y:.2f}%<extra></extra>' })),
    layout({ title: ttl('(c) Ch. 7: ES in RON'), barmode: 'group', legend: legendBelow(-0.18), xaxis: AX('', { type: 'category' }), yaxis: AX('Weekly ES 2.5% (%)', { rangemode: 'tozero' }) }));
  const hv = h.filter(v => isFinite(v)), dmax = Math.max(...PER.map(([p]) => Math.max(...IRCH.map(c => es[p][c])) - Math.min(...IRCH.map(c => es[p][c]))));
  out('ir-out', [T.ir(y0, SER.map(([k, , lab], j) => `${lab} ${nf(P[j].z[0], 2)}`).join(', ')),
    T.ir2(ni(W), nf(Math.min(...hv), 2), nf(Math.max(...hv), 2), nf(hv[hv.length - 1], 2)),
    T.ir3(PER.map(([p, l]) => `${T.irper[p]}: ${IRCH.map(c => nf(es[p][c], 2) + '%').join(' / ')}`).join('; '), nf(dmax, 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['bf-y0', 'bf-y1', 'bf-k'], facts); P('bf-play', 'bf-y1', range(2001, 2026, 1), 700);
  $('bf-play').addEventListener('click', () => { if (+$('bf-y0').value >= 2001) { $('bf-y0').value = 2000; } }, true);
  on(['bg-a', 'bg-p'], garch); P('bg-play', 'bg-p', range(0.9, 1, 0.0025), 300);
  on(['bv-m', 'bv-l', 'bv-y0', 'bv-t'], varPath); P('bv-play', 'bv-t', range(0, 1000, 10), 90);
  on(['br-l', 'br-adj', 'br-y0', 'br-y1'], breachRates); P('br-play', 'br-y1', range(2005, 2026, 1), 600);
  on(['kp-T', 'kp-pi', 'kp-a'], kupiecPowerBlock); P('kp-play', 'kp-T', [100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 5432, 6000], 600);
  on(['nm-model', 'nm-meas', 'nm-ol', 'nm-q'], nseBlock); P('nm-play', 'nm-model', ['all', ...NF.models], 1500);
  $('nm-chart').style.height = '480px';
  on(['ip-m', 'ip-y0', 'ip-t'], portfolioBlock); P('ip-play', 'ip-t', range(0, 1000, 10), 90);
  on(['ib-a', 'ib-w'], bitcoinBlock); P('ib-play', 'ib-a', range(0.5, 5, 0.25), 600);
  on(['ir-w', 'ir-y0'], romaniaBlock); P('ir-play', 'ir-w', range(52, 260, 8), 500);
  const PFX = { 'bet-facts': 'bf', 'bet-garch': 'bg', 'bet-var': 'bv', 'breach-rates': 'br', 'kupiec-power': 'kp', 'nse-multiverse': 'nm',
    'int-portfolio': 'ip', 'int-bitcoin': 'ib', 'int-romania': 'ir' };
  // blocks whose initial live chart shows the answer: the charts are veiled with the slide and the readout
  const VEIL_CHART = new Set(['bet-var', 'breach-rates', 'nse-multiverse']);
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) =>
    predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true, charts: VEIL_CHART.has(b) } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  facts(); garch(); varPath(); breachRates(); kupiecPowerBlock(); nseBlock(); portfolioBlock(); bitcoinBlock(); romaniaBlock();
}
window.CH19 = { portfolioBlock, bitcoinBlock, romaniaBlock, backtest, hsES, hsVaR, vrz, hedgeRatio, IPV, IPL, IBF, IBL, IBR, IBpos, Z99, hillAlpha, acf, ljungBox, kupiecLR, chi2sf1, binomPpf, holm, bhReject, powerCurve, multiverse, DATES, R, EDATES, LOSS, VAR };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

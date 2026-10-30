// Chapter 2 interactive page: one block per chart slide, computed in the browser from ch2_data.js.
(function () {
'use strict';
const D = window.CH2_DATA;
const { C, sum, rng, mean, sdev, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH2_TEXT;

// ---------------------------------------------------------------- colours (same as the slides)
const MB = '#1A3A6E', RED = '#CD0000', FOREST = '#2E7D32', AMBER = '#B5853F', BAND = '#C5D2E8', NAVY = '#1F2A44';
const CBLUE = '#164b82', TEAL = '#168577';                  // ch2_concept_charts.py
const GROUP_COL = { 'Developed': MB, 'Emerging/frontier': RED, 'Crypto': AMBER, 'FX': FOREST };
const PANEL_COL = [MB, RED, AMBER, FOREST];
const short = k => D.labels[k].replace(/ \(.*\)$/, '');

// subplot grid: axis objects for rows x cols panels (axis 1 = top left)
function grid(rows, cols, gx, gy, ax) {
  const L = {}, w = (1 - gx * (cols - 1)) / cols, h = (1 - gy * (rows - 1)) / rows;
  for (let i = 0; i < rows; i++) for (let j = 0; j < cols; j++) {
    const n = i * cols + j + 1, s = n === 1 ? '' : n;
    const x0 = j * (w + gx), y1 = 1 - i * (h + gy);
    L['xaxis' + s] = Object.assign(AX(ax.x(i, j)), { domain: [x0, x0 + w], anchor: 'y' + s }, ax.xo ? ax.xo(i, j) : {});
    L['yaxis' + s] = Object.assign(AX(ax.y(i, j)), { domain: [y1 - h, y1], anchor: 'x' + s }, ax.yo ? ax.yo(i, j) : {});
  }
  return L;
}
const panelTitle = (n, cols, gx, gy, rows, text, color) => {
  const w = (1 - gx * (cols - 1)) / cols, h = (1 - gy * (rows - 1)) / rows, i = Math.floor((n - 1) / cols), j = (n - 1) % cols;
  return { xref: 'paper', yref: 'paper', x: j * (w + gx), y: 1 - i * (h + gy), xanchor: 'left', yanchor: 'bottom', showarrow: false, text, font: { size: 12, color: color || NAVY } };
};
const setH = (id, h) => { $(id).style.height = h + 'px'; };
const acf = (x, k) => { const m = mean(x), e = x.map(v => v - m), d = sum(e.map(v => v * v)); let s = 0; for (let t = k; t < e.length; t++) s += e[t] * e[t - k]; return s / d; };
const kurt = x => { const m = mean(x), e = x.map(v => v - m), v2 = mean(e.map(v => v * v)); return mean(e.map(v => v ** 4)) / (v2 * v2); };

// ================================================================= the random-walk game
let rgSeed = 0, rgPaths = null;
function rgMake() {
  const G = D.game;
  if (rgSeed === 0) { rgPaths = G.paths; return; }
  const z = rng(1000 + rgSeed);
  rgPaths = G.paths.map((p, i) => {
    if (i === G.real) return p;
    let s = 0; const a = [1];
    for (let t = 0; t < G.n; t++) { s += G.mu + G.sd * z(); a.push(Math.exp(s)); }
    return a;
  });
}
function game() {
  const G = D.game, k = +$('rg-t').value, show = $('rg-show').value === 'reveal', gx = 0.08, gy = 0.16;
  $('rg-t-v').textContent = k;
  const tr = rgPaths.map((p, i) => {
    const s = i === 0 ? '' : i + 1, real = show && i === G.real;
    return { x: range(0, k, 1), y: p.slice(0, k + 1), xaxis: 'x' + s, yaxis: 'y' + s, mode: 'lines', showlegend: false,
      line: { color: real ? RED : MB, width: real ? 1.4 : 1 }, hovertemplate: 'day %{x}<br>%{y:.2f}<extra>' + 'ABCD'[i] + '</extra>' };
  });
  const lay = grid(2, 2, gx, gy, { x: () => '', y: (i, j) => (j === 0 ? 'Value of 1 USD (start = 1)' : ''), xo: () => ({ range: [0, G.n], showticklabels: false }) });
  const ann = [0, 1, 2, 3].map(i => panelTitle(i + 1, 2, gx, gy, 2, 'Series ' + 'ABCD'[i] + (show && i === G.real ? ': S&P 500' : ''), show && i === G.real ? RED : NAVY));
  plot('rg-chart', tr, layout(Object.assign(lay, { annotations: ann, margin: { l: 56, r: 12, t: 30, b: 20 } })));
  const fin = rgPaths.map(p => nf(p[k], 2));
  out('rg-out', [T.rg(k, fin), show ? T.rgReveal('ABCD'[G.real], nf(G.paths[G.real][G.n], 2), pct(G.mu, 3), pct(G.sd, 2), G.start, G.end) : T.rgHide]);
}

// ================================================================= RW1, RW2, GARCH simulated with the same innovations
function garchPath(eps, a, b) {
  const om = 1 - a - b, n = eps.length, v = new Array(n).fill(1), r = new Array(n).fill(0);
  for (let t = 1; t < n; t++) { v[t] = om + a * r[t - 1] ** 2 + b * v[t - 1]; r[t] = Math.sqrt(v[t]) * eps[t]; }
  return { r, s: v.map(Math.sqrt) };
}
function abInputs(p) {
  const a = +$(p + '-a').value; let b = +$(p + '-b').value;
  if (a + b > 0.995) { b = +(0.995 - a).toFixed(3); $(p + '-b').value = b; }
  $(p + '-a-v').textContent = nf(a, 3); $(p + '-b-v').textContent = nf(b, 2);
  return [a, b];
}
function rwReturns() {
  const eps = D.eps, n = eps.length, [a, b] = abInputs('cr'), s2 = +$('cr-s').value, gx = 0.06, gy = 0.14;
  $('cr-s-v').textContent = nf(s2, 1) + '%';
  const g = garchPath(eps, a, b), vols = [eps.map(() => 1), eps.map((_, t) => (t < n / 2 ? 1 : s2)), g.s];
  const rr = [eps, eps.map((e, t) => vols[1][t] * e), g.r], days = range(0, n - 1, 1), tr = [];
  const ymax = Math.max(10, Math.ceil(Math.max(...rr.flat().map(Math.abs)) / 2) * 2);
  rr.forEach((y, j) => tr.push({ x: days, y, xaxis: 'x' + (j ? j + 1 : ''), yaxis: 'y' + (j ? j + 1 : ''), mode: 'lines', line: { color: CBLUE, width: 0.7 }, showlegend: false, hovertemplate: 'day %{x}: %{y:.2f}%<extra></extra>' }));
  vols.forEach((y, j) => tr.push({ x: days, y, xaxis: 'x' + (j + 4), yaxis: 'y' + (j + 4), mode: 'lines', line: { color: TEAL, width: 2 }, showlegend: false, hovertemplate: 'day %{x}: %{y:.2f}%<extra></extra>' }));
  const smax = Math.max(3.6, Math.max(...vols.flat()) + 0.6);
  const lay = grid(2, 3, gx, gy, { x: i => (i === 1 ? 'Day' : ''), y: (i, j) => (j ? '' : i ? 'Conditional SD (%)' : 'Log return (%)'),
    yo: i => ({ range: i ? [0, smax] : [-ymax, ymax] }), xo: i => (i ? {} : { showticklabels: false }) });
  const heads = ['RW1: independent,<br>same distribution', 'RW2: independent,<br>changing distribution', 'RW3 example (GARCH):<br>uncorrelated, dependent'];
  const ann = heads.map((h, j) => panelTitle(j + 1, 3, gx, gy, 2, h));
  ['Volatility fixed in advance', 'Volatility fixed in advance', 'Volatility responds to past shocks'].forEach((h, j) => ann.push(panelTitle(j + 4, 3, gx, gy, 2, h, TEAL)));
  plot('cr-chart', tr, layout(Object.assign(lay, { annotations: ann, margin: { l: 56, r: 12, t: 46, b: 40 } })));
  out('cr-out', [T.cr(rr.map(y => nf(sdev(y), 2) + '%'), rr.map(y => nf(kurt(y), 1))), T.crG(nf(acf(g.r, 1), 3), nf(acf(g.r.map(v => v * v), 1), 3), nf(1 - a - b, 3))]);
}

// ================================================================= ACF of GARCH returns and of squared returns
let csExtra = null;
function csEps(n) {
  if (n <= D.eps.length) return D.eps.slice(0, n);
  if (!csExtra || csExtra.length < n - D.eps.length) { const z = rng(203); csExtra = Array.from({ length: 20000 }, z); }
  return D.eps.concat(csExtra.slice(0, n - D.eps.length));
}
function rwSquared() {
  const [a, b] = abInputs('cs'), n = +$('cs-T').value, g = garchPath(csEps(n), a, b), lags = range(1, 20, 1);
  const r1 = lags.map(k => acf(g.r, k)), sq = g.r.map(v => v * v), r2 = lags.map(k => acf(sq, k)), bd = 1.96 / Math.sqrt(n);
  const fin = 3 * a * a + 2 * a * b + b * b < 1, th1 = a * (1 - a * b - b * b) / (1 - 2 * a * b - b * b), th = lags.map(k => th1 * (a + b) ** (k - 1));
  const band = [hline(bd, NAVY, 'dot'), hline(-bd, NAVY, 'dot')];
  const yax = () => AX('Sample autocorrelation', { range: [-0.12, 0.5], tickvals: [-0.1, 0, 0.1, 0.2, 0.3, 0.4] });
  const xax = () => AX('Lag (days)', { tickvals: [1, 5, 10, 15, 20] });
  plot('cs-r', [{ x: lags, y: r1, type: 'bar', name: 'Returns', marker: { color: CBLUE }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: '±1.96/√T', line: { color: NAVY, dash: 'dot', width: 2 } }],
  layout({ title: ttl('GARCH returns'), shapes: band, xaxis: xax(), yaxis: yax() }));
  const tr = [{ x: lags, y: r2, type: 'bar', name: 'Squared returns', marker: { color: TEAL }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' }];
  if (fin) tr.push({ x: lags, y: th, mode: 'lines+markers', name: 'Theoretical ACF of squares', line: { color: RED, width: 2 }, marker: { size: 5 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' });
  plot('cs-s', tr, layout({ title: ttl('Squared GARCH returns'), shapes: band, xaxis: xax(), yaxis: yax() }));
  out('cs-out', [T.cs(n, nf(Math.max(...r1.map(Math.abs)), 3), nf(r2[0], 3), nf(r2[19], 3), nf(bd, 3)), fin ? T.csTh(nf(th1, 3), nf(a + b, 3)) : T.csInf]);
}

// ================================================================= lag-k autocorrelation across markets
function acfMarkets() {
  const k = +$('ac-k').value, A = D.acf;
  $('ac-k-v').textContent = k;
  const ks = [...D.order].sort((p, q) => A[p].rho[k - 1] - A[q].rho[k - 1]), y = ks.map((_, i) => i), tr = [];
  // test bands centred at 0 use the SEs derived under H0; the bars are 95% CIs with the HAC SE of the estimator
  const bands = ks.map((m, i) => ({ type: 'rect', layer: 'below', xref: 'x', yref: 'y', x0: -1.96 * A[m].se[k - 1], x1: 1.96 * A[m].se[k - 1],
    y0: i - 0.32, y1: i + 0.32, fillcolor: BAND, opacity: 0.8, line: { width: 0 } }));
  for (const [gname, col] of Object.entries(GROUP_COL)) {
    const idx = ks.map((m, i) => [m, i]).filter(([m]) => D.groups[m] === gname);
    tr.push({ x: idx.map(([m]) => A[m].rho[k - 1]), y: idx.map(([, i]) => i), mode: 'markers', name: gname, marker: { color: col, size: 8 },
      error_x: { type: 'data', array: idx.map(([m]) => 1.96 * A[m].hac[k - 1]), color: col, thickness: 1.6, width: 3 },
      customdata: idx.map(([m]) => [short(m), 1.96 * A[m].hac[k - 1], 1.96 * A[m].se[k - 1], 1.96 / Math.sqrt(A[m].T)]),
      hovertemplate: '%{customdata[0]}<br>ρ̂ = %{x:.3f}<br>95% CI (HAC) ±%{customdata[1]:.3f}<br>robust test band at 0: ±%{customdata[2]:.3f}<br>i.i.d. test band at 0: ±%{customdata[3]:.3f}<extra></extra>' });
  }
  const ix = [], iy = [];
  ks.forEach((m, i) => { const h = 1.96 / Math.sqrt(A[m].T); ix.push(-h, h); iy.push(i, i); });
  tr.push({ x: ix, y: iy, mode: 'markers', name: 'Test band at 0, i.i.d. ±1.96/√T', marker: { symbol: 'line-ns-open', size: 12, color: NAVY, line: { color: NAVY, width: 1.5 } }, hoverinfo: 'skip' });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Test band at 0, robust SE under H₀', line: { color: BAND, width: 10 } });
  tr.push({ x: [null], y: [null], mode: 'lines', name: '95% CI, HAC SE (bars)', line: { color: NAVY, width: 1.6 } });
  plot('ac-chart', tr, layout({ title: ttl('Lag-' + k + ' autocorrelation of daily log returns (full samples)'), shapes: [...bands, vline(0, NAVY)],
    xaxis: AX('Lag-' + k + ' autocorrelation ρ̂' + k, { zeroline: false }), yaxis: AX('', { tickvals: y, ticktext: ks.map(m => D.labels[m]), range: [-0.6, ks.length - 0.4] }),
    legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top', font: { size: 11 } }, margin: { l: 150, r: 12, t: 30, b: 40 } }));
  const rej = ks.filter(m => Math.abs(A[m].rho[k - 1]) > 1.96 * A[m].se[k - 1]), rejI = ks.filter(m => Math.abs(A[m].rho[k - 1]) > 1.96 / Math.sqrt(A[m].T));
  out('ac-out', [T.ac(k, rej.length, rej.map(short).join(', ') || '—', rejI.length), T.ac2(k, nf(A.sp500.rho[k - 1], 3), nf(A.sp500.se[k - 1], 3), nf(1 / Math.sqrt(A.sp500.T), 3), nf(A.sp500.hac[k - 1], 3))]);
}

// ================================================================= variance-ratio profiles
const VR_SETS = { slide: ['sp500', 'bet', 'btc', 'eurron'], cee: ['bet', 'wig20', 'bux', 'px'], dev: ['sp500', 'stoxx', 'nikkei', 'hsi'], em: ['xu100', 'bvsp', 'mxx', 'eth'] };
function vrProfile() {
  const set = VR_SETS[$('vr-set').value], q = +$('vr-q').value, qs = range(2, 60, 1), gx = 0.09, gy = 0.2, tr = [];
  $('vr-q-v').textContent = q + (q > 20 ? ' (' + T.descr + ')' : '');
  set.forEach((m, j) => {
    const V = D.vr[m], s = j ? j + 1 : '', ax = { xaxis: 'x' + s, yaxis: 'y' + s }, col = PANEL_COL[j];
    tr.push(Object.assign({ x: qs, y: V.band.map(b => 1 + b), mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' }, ax));
    tr.push(Object.assign({ x: qs, y: V.band.map(b => 1 - b), mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: 'rgba(197,210,232,0.8)', name: 'Pointwise 95% null band (robust)', showlegend: j === 0, legendgroup: 'b', hoverinfo: 'skip' }, ax));
    tr.push(Object.assign({ x: qs, y: V.VR, mode: 'lines', line: { color: col, width: 2 }, name: 'VR(q)', showlegend: false, customdata: V.band, hovertemplate: short(m) + ', q = %{x}<br>VR %{y:.3f}<br>band ±%{customdata:.3f}<extra></extra>' }, ax));
    tr.push(Object.assign({ x: [2, 5, 10, 20], y: [2, 5, 10, 20].map(h => V.VR[h - 2]), mode: 'markers', marker: { color: col, size: 7, line: { color: '#fff', width: 1 } }, name: 'Test horizons: 2, 5, 10, 20 days', showlegend: j === 0, legendgroup: 't', hovertemplate: 'q = %{x}: %{y:.3f}<extra></extra>' }, ax));
    tr.push(Object.assign({ x: [q], y: [V.VR[q - 2]], mode: 'markers', marker: { color: NAVY, size: 10, symbol: 'diamond-open', line: { width: 2 } }, name: 'Chosen horizon q', showlegend: j === 0, legendgroup: 'q', hovertemplate: 'q = %{x}: %{y:.3f}<extra></extra>' }, ax));
  });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'VR(q)', line: { color: MB, width: 2 } });
  const all = set.flatMap(m => D.vr[m].VR.concat(D.vr[m].band.map(b => 1 + b), D.vr[m].band.map(b => 1 - b)));
  const yr = [Math.min(...all) - 0.03, Math.max(...all) + 0.03];
  const lay = grid(2, 2, gx, gy, { x: i => (i ? 'Horizon q (days)' : ''), y: (i, j) => (j ? '' : 'Variance ratio'), yo: () => ({ range: yr }), xo: () => ({ range: [1, 61] }) });
  const shapes = [];
  set.forEach((m, j) => { const s = j ? j + 1 : ''; shapes.push({ type: 'line', xref: 'x' + s, yref: 'y' + s, x0: 1, x1: 61, y0: 1, y1: 1, line: { color: NAVY, width: 1 } }); });
  plot('vr-chart', tr, layout(Object.assign(lay, { shapes, annotations: set.map((m, j) => panelTitle(j + 1, 2, gx, gy, 2, D.labels[m], PANEL_COL[j])),
    legend: { orientation: 'h', x: 0, y: -0.16, yanchor: 'top', font: { size: 11 } }, margin: { l: 56, r: 12, t: 24, b: 40 } })));
  out('vr-out', set.map(m => { const V = D.vr[m], v = V.VR[q - 2], b = V.band[q - 2]; return T.vr(short(m), q, nf(v, 3), nf(1 - b, 3), nf(1 + b, 3), Math.abs(v - 1) > b, V.CD_p < 0.001 ? '< ' + nf(0.001, 3) : '= ' + nf(V.CD_p, 3)); }));
}

// ================================================================= dividend-price ratio out of sample
function oosDp() {
  const O = D.oos, y0 = +$('od-y').value, ct = $('od-f').value === 'ct', f = ct ? O.ct : O.pred;
  $('od-y-v').textContent = y0;
  const i0 = O.dates.findIndex(d => +d.slice(0, 4) >= y0), x = [], cum = [];
  let c = 0, s0 = 0, s1 = 0;
  for (let i = i0; i < O.dates.length; i++) {
    const e0 = (O.y[i] - O.mean[i]) ** 2, e1 = (O.y[i] - f[i]) ** 2;
    c += e0 - e1; s0 += e0; s1 += e1; x.push(O.dates[i]); cum.push(c);
  }
  plot('od-chart', [{ x, y: cum, mode: 'lines', name: ct ? 'Predictive regression on log D/P with Campbell–Thompson restrictions, vs historical mean' : 'Predictive regression on log D/P vs historical mean',
    line: { color: RED, width: 1.6 }, hovertemplate: '%{x}: %{y:.4f}<extra></extra>' }],
  layout({ showlegend: true, title: ttl('S&P 500, monthly: cumulative squared-error difference, from January ' + y0), shapes: [hline(0, NAVY, 'dash')],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Cumulative reduction in squared errors', { tickformat: '.3f' }) }));
  out('od-out', [T.od(y0, x.length, pct(1 - s1 / s0, 2), nf(c, 4)), T.od2(pct(O.res.r2, 2), nf(O.res.cw_t, 2), nf(O.res.cw_p, 2))]);
}

// ================================================================= bank tax event study
function mm(y, x) {                 // OLS y = a + b x; residual variance with T - 2 degrees of freedom
  const n = y.length, mx = mean(x), my = mean(y);
  let sxx = 0, sxy = 0; for (let i = 0; i < n; i++) { sxx += (x[i] - mx) ** 2; sxy += (x[i] - mx) * (y[i] - my); }
  const b = sxy / sxx, a = my - b * mx; let ssr = 0; for (let i = 0; i < n; i++) ssr += (y[i] - a - b * x[i]) ** 2;
  return { a, b, s2: ssr / (n - 2), mx, vx: sxx / (n - 1), n, sxx };
}
function eventFit(L) {
  const E = D.event, day = E.day, iE = day.map((d, i) => [d, i]).filter(([d]) => d >= -10 - L && d <= -11).map(([, i]) => i);
  const xs = iE.map(i => E.BET[i]), res = {};
  const ser = { TLV: E.TLV, BRD: E.BRD, PORT: E.TLV.map((v, i) => (v + E.BRD[i]) / 2) };
  for (const [k, s] of Object.entries(ser)) {
    const f = mm(iE.map(i => s[i]), xs), w = day.map((d, i) => i).filter(i => day[i] >= -10);
    res[k] = { f, day: w.map(i => day[i]), rm: w.map(i => E.BET[i]),
      ar: w.map(i => s[i] - f.a - f.b * E.BET[i]),
      se: w.map(i => Math.sqrt(f.s2 * (1 + 1 / f.n + (E.BET[i] - f.mx) ** 2 / ((f.n - 1) * f.vx)))) };
  }
  return res;
}
function carStat(R, t1, t2) {       // CAR over [t1, t2]; variance s2 (L + v'(X'X)^-1 v), v = (L, sum r_m) (MacKinlay, 1997)
  const f = R.f, idx = R.day.map((d, i) => i).filter(i => R.day[i] >= t1 && R.day[i] <= t2), L = idx.length;
  const car = sum(idx.map(i => R.ar[i])), sm = sum(idx.map(i => R.rm[i]));
  const sx = f.n * f.mx, sxx = f.sxx + f.n * f.mx * f.mx, det = f.n * sxx - sx * sx;
  const quadv = (L * L * sxx - 2 * L * sm * sx + sm * sm * f.n) / det;
  return { car, t: car / Math.sqrt(f.s2 * (L + quadv)), tn: car / Math.sqrt(f.s2 * L) };
}
function eventStudy() {
  const L = +$('ev-L').value; let t1 = +$('ev-a').value, t2 = +$('ev-b').value;
  if (t1 > t2) { t1 = t2; $('ev-a').value = t1; }
  $('ev-L-v').textContent = L + ' [' + nf(-10 - L, 0) + ', −11]'; $('ev-a-v').textContent = nf(t1, 0); $('ev-b-v').textContent = nf(t2, 0);
  const R = eventFit(L), cols = { TLV: MB, BRD: FOREST, PORT: RED }, names = { TLV: 'Banca Transilvania', BRD: 'BRD', PORT: 'Equal-weighted portfolio' };
  const P = R.PORT, band = P.day.map((d, i) => ({ type: 'rect', layer: 'below', xref: 'x', yref: 'y', x0: d - 0.5, x1: d + 0.5, y0: -196 * P.se[i], y1: 196 * P.se[i], fillcolor: BAND, opacity: 0.8, line: { width: 0 } }));
  const tr = [{ x: [null], y: [null], mode: 'lines', name: 'Portfolio ±1.96 prediction-error SE', line: { color: BAND, width: 10 } }];
  ['TLV', 'BRD', 'PORT'].forEach(k => tr.push({ x: R[k].day, y: R[k].ar.map(v => 100 * v), type: 'bar', name: names[k], marker: { color: cols[k] }, hovertemplate: names[k] + ', day %{x}: %{y:.2f}%<extra></extra>' }));
  plot('ev-ar', tr, layout({ barmode: 'group', bargap: 0.15, title: ttl('Daily abnormal returns'), shapes: [...band, vline(0, NAVY, 'dash')], legend: { orientation: 'h', x: 0, y: -0.3, yanchor: 'top', traceorder: 'normal', font: { size: 11 } },
    xaxis: AX('Event day (0 = 19 Dec 2018)', { dtick: 5 }), yaxis: AX('Abnormal return (%)') }));
  const days = range(t1, 5, 1);
  plot('ev-car', ['TLV', 'BRD', 'PORT'].map(k => {
    const c = []; let s = 0; R[k].day.forEach((d, i) => { if (d >= t1) { s += R[k].ar[i]; c.push(100 * s); } });
    return { x: days, y: c, mode: 'lines+markers', name: names[k], line: { color: cols[k], width: 2 }, marker: { size: days.map(d => (d === t2 ? 11 : 6)) }, hovertemplate: names[k] + ', CAR[' + t1 + ', %{x}] = %{y:.2f}%<extra></extra>' };
  }), layout({ title: ttl('Cumulative abnormal return from day ' + t1), shapes: [hline(0, NAVY), vline(t2, NAVY, 'dot')], xaxis: AX('Event day', { dtick: 1 }), yaxis: AX('CAR from day ' + t1 + ' (%)') }));
  const f = R.TLV.f, i0 = R.TLV.day.indexOf(0), cs = ['TLV', 'BRD', 'PORT'].map(k => carStat(R[k], t1, t2));
  out('ev-out', [T.ev0(nf(f.b, 2), pct(Math.sqrt(f.s2), 2), pct(R.TLV.ar[i0], 1), nf(R.TLV.ar[i0] / Math.sqrt(f.s2), 1), nf(R.TLV.ar[i0] / R.TLV.se[i0], 2)),
    T.ev(nf(t1, 0), nf(t2, 0), cs.map(c => pct(c.car, 1)), cs.map(c => nf(c.t, 2)), nf(cs[0].tn, 2))]);
}

// ================================================================= multiple testing with random rules
let mtSeed = 0, mtCache = {};
function mtStats(p) {
  const key = p + ':' + mtSeed;
  if (mtCache[key]) return mtCache[key];
  if (p === 0.2 && mtSeed === 0) return (mtCache[key] = D.mt.t);
  const x = D.mt.r_bp, n = x.length, u = rng(77 + mtSeed * 13 + Math.round(p * 100)).u, ts = [];
  for (let r = 0; r < 2000; r++) {
    let n1 = 0, s1 = 0, q1 = 0, s0 = 0, q0 = 0;
    for (let i = 0; i < n; i++) { const v = x[i]; if (u() < p) { n1++; s1 += v; q1 += v * v; } else { s0 += v; q0 += v * v; } }
    const n0 = n - n1, m1 = s1 / n1, m0 = s0 / n0, v1 = (q1 - n1 * m1 * m1) / (n1 - 1), v0 = (q0 - n0 * m0 * m0) / (n0 - 1);
    ts.push((m1 - m0) / Math.sqrt(v1 / n1 + v0 / n0));
  }
  return (mtCache[key] = ts);
}
function multipleTesting() {
  const p = +$('mt-p').value, k = +$('mt-n').value, ts = mtStats(p).slice(0, k), xx = range(-4.5, 4.5, 0.05);
  $('mt-n-v').textContent = k;
  const sh = (c, col, dash) => [vline(c, col, dash), vline(-c, col, dash)];
  plot('mt-chart', [
    { x: ts, type: 'histogram', histnorm: 'probability density', xbins: { start: -4.5, end: 4.5, size: 0.15 }, name: k + ' random "anomalies" on the S&P 500', marker: { color: MB, opacity: 0.8, line: { color: '#fff', width: 0.5 } }, hovertemplate: 't %{x}<br>density %{y:.3f}<extra></extra>' },
    { x: xx, y: xx.map(v => Math.exp(-v * v / 2) / Math.sqrt(2 * Math.PI)), mode: 'lines', name: 'Standard Normal distribution', line: { color: NAVY, width: 1.5 }, hoverinfo: 'skip' },
    { x: [null], y: [null], mode: 'lines', name: '|t| > 1.96', line: { color: RED, dash: 'dash', width: 2 } },
    { x: [null], y: [null], mode: 'lines', name: '|t| > 3.0 (Harvey–Liu–Zhu)', line: { color: FOREST, dash: 'dash', width: 2 } }
  ], layout({ bargap: 0, title: ttl('Good days: ' + Math.round(100 * p) + '% of the days, drawn at random'), shapes: [...sh(1.96, RED, 'dash'), ...sh(3, FOREST, 'dash')],
    xaxis: AX('t-statistic of "good days minus other days"', { range: [-4.5, 4.5] }), yaxis: AX('Density') }));
  const a = ts.map(Math.abs), n196 = a.filter(v => v > 1.96).length, n3 = a.filter(v => v > 3).length;
  out('mt-out', [T.mt(k, pct(n196 / k, 1), n196, pct(n3 / k, 2), n3, nf(Math.max(...a), 2)), T.mt2(k, pct(1 - 0.95 ** k, 1))]);
}

// ================================================================= case study: weekly crypto momentum (Liu & Tsyvinski, 2021)
const nwLag = T => Math.floor(4 * Math.pow(T / 100, 2 / 9));
function olsHac(y, x, L) {           // OLS y = a + b x; Newey-West (Bartlett, no small-sample correction), as crypto_momentum_case.ols_hac
  const T = y.length; L = L === undefined ? nwLag(T) : L;
  let sx = 0, sxx = 0, sy = 0, sxy = 0;
  for (let i = 0; i < T; i++) { sx += x[i]; sxx += x[i] * x[i]; sy += y[i]; sxy += x[i] * y[i]; }
  const det = T * sxx - sx * sx, i00 = sxx / det, i01 = -sx / det, i11 = T / det;
  const b = (T * sxy - sx * sy) / det, a = (sy - b * sx) / T, e = y.map((v, i) => v - a - b * x[i]);
  const u0 = e, u1 = e.map((v, i) => v * x[i]);
  let s00 = 0, s01 = 0, s11 = 0;
  for (let i = 0; i < T; i++) { s00 += u0[i] * u0[i]; s01 += u0[i] * u1[i]; s11 += u1[i] * u1[i]; }
  for (let l = 1; l <= L; l++) {
    const w = 1 - l / (L + 1); let g00 = 0, g01 = 0, g10 = 0, g11 = 0;
    for (let i = l; i < T; i++) { g00 += u0[i] * u0[i - l]; g01 += u0[i] * u1[i - l]; g10 += u1[i] * u0[i - l]; g11 += u1[i] * u1[i - l]; }
    s00 += 2 * w * g00; s01 += w * (g01 + g10); s11 += 2 * w * g11;
  }
  const v11 = i01 * (i01 * s00 + i11 * s01) + i11 * (i01 * s01 + i11 * s11), ssr = sum(e.map(v => v * v));
  return { b, se: Math.sqrt(v11), t: b / Math.sqrt(v11), tOls: b / Math.sqrt(ssr / (T - 2) * i11), T, L };
}
function cmSeries(k) {
  const M = D.cmom, d = [], r = [];
  M.dates.forEach((x, i) => { if (M[k][i] !== null) { d.push(x); r.push(M[k][i]); } });
  return { d, r };
}
function cmPeriod(S, a, b) {         // weeks with a <= date <= b; regressions of R(t+h) on R(t) for h = 1..4
  const idx = S.d.map((x, i) => i).filter(i => S.d[i] >= a && S.d[i] <= b), r = idx.map(i => S.r[i]);
  const reg = [1, 2, 3, 4].map(h => olsHac(r.slice(h), r.slice(0, r.length - h)));
  return { r, reg, sd: sdev(r), weeks: r.length };
}
function cmRolling(S, W) {
  const x = S.r.slice(0, -1), y = S.r.slice(1), res = [];
  for (let i = W; i <= x.length; i++) res.push(Object.assign(olsHac(y.slice(i - W, i), x.slice(i - W, i)), { date: S.d[i] }));
  return res;
}
const cmCut = m => { const y = 2011 + Math.floor(m / 12), mo = m % 12, last = new Date(Date.UTC(y, mo + 1, 0)); return { s: last.toISOString().slice(0, 10), label: T.months[mo] + ' ' + y }; };
function cryptoMomentum() {
  const k = $('cm-asset').value, m = +$('cm-m').value, W = +$('cm-w').value, S = cmSeries(k), c = cmCut(m);
  $('cm-m-v').textContent = c.label; $('cm-w-v').textContent = W;
  const A = cmPeriod(S, S.d[0], c.s), F = cmPeriod(S, c.s + 'z', '9999'), H = [1, 2, 3, 4], name = k === 'btc' ? 'Bitcoin' : 'Ethereum';
  const fy = d => d.slice(0, 4) === S.d[0].slice(0, 4) ? 'Jan ' + S.d[0].slice(0, 4) : d;
  const mon = s => ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][+s.slice(5, 7) - 1] + ' ' + s.slice(0, 4);
  const nxt = cmCut(m + 1).s.slice(0, 8) + '01', last = S.d[S.d.length - 1];
  const tr = [
    { x: H.map(h => h - 0.13), y: A.reg.map(f => f.b), error_y: { type: 'data', array: A.reg.map(f => 1.96 * f.se), color: MB, thickness: 1.2, width: 4 }, mode: 'markers', marker: { color: MB, size: 8 },
      name: fy(S.d[0]) + ' – ' + mon(c.s), hovertemplate: 'h = %{customdata}: b = %{y:.3f}<extra></extra>', customdata: H },
    { x: H.map(h => h + 0.13), y: F.reg.map(f => f.b), error_y: { type: 'data', array: F.reg.map(f => 1.96 * f.se), color: RED, thickness: 1.2, width: 4 }, mode: 'markers', marker: { color: RED, size: 8 },
      name: mon(nxt) + ' – ' + mon(last), hovertemplate: 'h = %{customdata}: b = %{y:.3f}<extra></extra>', customdata: H }];
  if (k === 'btc') tr.push({ x: H, y: D.cmom.paper.beta, mode: 'markers', marker: { color: AMBER, size: 9, symbol: 'diamond' }, name: 'Liu & Tsyvinski (working paper)', hovertemplate: 'paper, h = %{x}: b = %{y:.2f}<extra></extra>' });
  plot('cm-b', tr, layout({ title: ttl(name + ', weekly: slope of R(t+h) on R(t), 95% NW intervals'), shapes: [hline(0, NAVY)],
    xaxis: AX('Horizon h (weeks)', { tickvals: H, range: [0.5, 4.5] }), yaxis: AX('Slope b_h') }));
  const Rl = cmRolling(S, W), dd = Rl.map(f => f.date);
  plot('cm-roll', [
    { x: dd, y: Rl.map(f => f.b + 1.96 * f.se), mode: 'lines', line: { width: 0 }, hoverinfo: 'skip', showlegend: false },
    { x: dd, y: Rl.map(f => f.b - 1.96 * f.se), mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: BAND, name: '95% NW band', hoverinfo: 'skip' },
    { x: dd, y: Rl.map(f => f.b), mode: 'lines', line: { color: MB, width: 1.6 }, name: 'Rolling b_1 (' + W + ' weeks)', hovertemplate: '%{x}: b_1 = %{y:.3f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', line: { color: RED, dash: 'dash', width: 2 }, name: 'End of the first period' }
  ], layout({ title: ttl(name + ': one-week slope b_1, rolling windows'), shapes: [hline(0, NAVY), vline(c.s, RED, 'dash')], xaxis: AX('', { type: 'date' }), yaxis: AX('Slope b_1') }));
  const sig = Rl.filter(f => Math.abs(f.t) > 1.96).length;
  out('cm-out', [T.cm(name, c.label, A.weeks, nf(A.reg[0].b, 3), nf(A.reg[0].t, 2), F.weeks, nf(F.reg[0].b, 3), nf(F.reg[0].t, 2)),
    T.cmE(pct(A.reg[0].b * A.sd, 2), pct(F.reg[0].b * F.sd, 2), pct(A.sd, 1), pct(F.sd, 1)), T.cm2(W, pct(sig / Rl.length, 0), Rl.length)]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  setH('rg-chart', 420); setH('cr-chart', 460); setH('ac-chart', 560); setH('vr-chart', 520);
  rgMake(); $('rg-t').max = D.game.n; $('rg-t').value = D.game.n; on(['rg-t', 'rg-show'], game); P('rg-play', 'rg-t', range(20, D.game.n, 40).concat([D.game.n]), 60);
  $('rg-new').addEventListener('click', () => { rgSeed++; rgMake(); $('rg-show').value = 'hidden'; game(); });
  on(['cr-a', 'cr-b', 'cr-s'], rwReturns); P('cr-play', 'cr-a', range(0, 0.095, 0.005), 350);
  on(['cs-a', 'cs-b', 'cs-T'], rwSquared); P('cs-play', 'cs-a', range(0, 0.095, 0.005), 350);
  on(['ac-k'], acfMarkets); P('ac-play', 'ac-k', range(1, 10, 1), 900);
  on(['vr-set', 'vr-q'], vrProfile); P('vr-play', 'vr-q', range(2, 60, 1), 140);
  on(['od-y', 'od-f'], oosDp); P('od-play', 'od-y', range(1970, 2015, 1), 220);
  on(['ev-L', 'ev-a', 'ev-b'], eventStudy); P('ev-play', 'ev-b', range(0, 5, 1), 800);
  on(['mt-n', 'mt-p'], multipleTesting); P('mt-play', 'mt-n', range(20, 2000, 20), 60);
  $('mt-new').addEventListener('click', () => { mtSeed++; multipleTesting(); });
  const cmMin = () => { const mn = $('cm-asset').value === 'eth' ? 72 : 24; $('cm-m').min = mn; if (+$('cm-m').value < mn) $('cm-m').value = mn; };
  $('cm-asset').addEventListener('input', cmMin); on(['cm-asset', 'cm-m', 'cm-w'], cryptoMomentum); P('cm-play', 'cm-m', range(24, 164, 2), 250);
  const PFX = { 'random-walk-game': 'rg', 'rw-models': 'cr', 'garch-acf': 'cs', 'acf-markets': 'ac', 'vr-profile': 'vr',
    'oos-dp': 'od', 'bank-tax': 'ev', 'multiple-testing': 'mt', 'crypto-momentum': 'cm' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  game(); rwReturns(); rwSquared(); acfMarkets(); vrProfile(); oosDp(); eventStudy(); multipleTesting(); cryptoMomentum();
}
window.CH2 = { garchPath, acf, kurt, eventFit, carStat, mtStats, olsHac, cmSeries, cmPeriod, cmRolling };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

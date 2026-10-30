// Chapter 5 interactive page: one block per chart slide, computed in the browser from ch5_data.js.
(function () {
'use strict';
const D = window.CH5_DATA;
const { C, sum, mean, sdev, median, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH5_TEXT;

// ---------------------------------------------------------------- colours (same as the slides)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  navy: '#1F2A44', band: '#C5D2E8', teal: '#17A2B8' };
const COL = D.col, LAB = D.labels;
const SHORT = { sp500: 'S&P 500', bet: 'BET', bettr: 'BET-TR', btc: 'Bitcoin', eurron: 'EUR/RON', gold: T.gold };

// ---------------------------------------------------------------- data helpers
function calendar(R) {
  const out = [R.d0]; let t = Date.parse(R.d0 + 'T00:00:00Z');
  for (const g of R.gaps) { t += g * 864e5; out.push(new Date(t).toISOString().slice(0, 10)); }
  return out;
}
const DATES = {}; for (const k in D.ret) DATES[k] = calendar(D.ret[k]);
const RET = k => D.ret[k].r;
function acf(x, L) {
  const m = mean(x), u = x.map(v => v - m), d = sum(u.map(v => v * v)), a = [];
  for (let k = 1; k <= L; k++) { let s = 0; for (let t = k; t < u.length; t++) s += u[t] * u[t - k]; a.push(s / d); }
  return a;
}
const exkurt = x => { const m = mean(x), n = x.length; let m2 = 0, m4 = 0; for (const v of x) { const d = (v - m) ** 2; m2 += d; m4 += d * d; } m2 /= n; m4 /= n; return m4 / (m2 * m2) - 3; };
const corr = (a, b) => { const ma = mean(a), mb = mean(b); let sab = 0, saa = 0, sbb = 0; for (let i = 0; i < a.length; i++) { const x = a[i] - ma, y = b[i] - mb; sab += x * y; saa += x * x; sbb += y * y; } return sab / Math.sqrt(saa * sbb); };
const halfLife = p => (p > 0 && p < 1 ? Math.log(0.5) / Math.log(p) : Infinity);
// E tau_{t+s} - E tau follows an AR(m) recursion, c_1 = l2 + l1/m, c_j = l1/m (j = 2..m): its dominant root
// (ratio of successive terms of the impulse response after many steps); lambda1 + lambda2 alone is not a half-life
function slowRoot(l1, l2, m) {
  const N = 6000, x = new Float64Array(N); x[0] = 1; let run = 1;
  for (let s = 1; s < N; s++) { x[s] = l2 * x[s - 1] + l1 / m * run; run += x[s]; if (s - m >= 0) run -= x[s - m]; }
  return x[N - 1] / x[N - 2];
}
const days = h => (isFinite(h) && h < 1e4 ? nf(h, 0) : '> 10000');

// special functions: log-gamma, regularised incomplete beta, Student-t and Normal distributions
function lgamma(x) {
  const g = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
  let y = x, tmp = x + 5.5; tmp -= (x + 0.5) * Math.log(tmp); let s = 1.000000000190015;
  for (const c of g) s += c / ++y;
  return -tmp + Math.log(2.5066282746310005 * s / x);
}
function betacf(a, b, x) {
  const qab = a + b, qap = a + 1, qam = a - 1; let c = 1, d = 1 - qab * x / qap; if (Math.abs(d) < 1e-300) d = 1e-300; d = 1 / d; let h = d;
  for (let m = 1; m <= 300; m++) {
    const m2 = 2 * m; let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d; if (Math.abs(d) < 1e-300) d = 1e-300; c = 1 + aa / c; if (Math.abs(c) < 1e-300) c = 1e-300; d = 1 / d; h *= d * c;
    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d; if (Math.abs(d) < 1e-300) d = 1e-300; c = 1 + aa / c; if (Math.abs(c) < 1e-300) c = 1e-300; d = 1 / d;
    const del = d * c; h *= del; if (Math.abs(del - 1) < 1e-13) break;
  }
  return h;
}
function ibeta(a, b, x) {
  if (x <= 0) return 0; if (x >= 1) return 1;
  const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
}
const tScale = nu => Math.sqrt((nu - 2) / nu);                     // unit-variance Student-t
function tcdf(x, nu) { const p = 0.5 * ibeta(nu / 2, 0.5, nu / (nu + x * x)); return x < 0 ? p : 1 - p; }
const tcdfU = (x, nu) => tcdf(x / tScale(nu), nu);
const tpdfU = (x, nu) => { const s = tScale(nu), y = x / s; return Math.exp(lgamma((nu + 1) / 2) - lgamma(nu / 2) - 0.5 * Math.log(nu * Math.PI) - (nu + 1) / 2 * Math.log1p(y * y / nu)) / s; };
function tppfU(p, nu) {
  let lo = -200, hi = 200;
  for (let i = 0; i < 90; i++) { const m = (lo + hi) / 2; if (tcdfU(m, nu) < p) lo = m; else hi = m; }
  return (lo + hi) / 2;
}
const npdf = x => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
function nppf(p) {                                                  // Acklam's rational approximation
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

// GARCH(1,1) filter of a return series, as in arch: sigma^2_0 from the backcast
function garchFilter(r, mu, om, al, be, bc) {
  const n = r.length, s2 = new Array(n);
  s2[0] = om + (al + be) * bc;
  for (let t = 1; t < n; t++) { const e = r[t - 1] - mu; s2[t] = om + al * e * e + be * s2[t - 1]; }
  return s2;
}
function ewma(r, lam) {                                             // forecast for day t from data up to t-1; start: mean of the first 250 r^2
  const n = r.length, h = new Array(n); let s = 0; for (let t = 0; t < 250; t++) s += r[t] * r[t]; s /= 250;
  for (let t = 0; t < n; t++) { h[t] = s; s = lam * s + (1 - lam) * r[t] * r[t]; }
  return h;
}
function hacT(d, L) {                                               // Diebold-Mariano: mean / Newey-West SE (Bartlett, L lags)
  const n = d.length, m = mean(d), u = d.map(v => v - m); let s = sum(u.map(v => v * v)) / n;
  for (let j = 1; j <= L; j++) { let c = 0; for (let t = j; t < n; t++) c += u[t] * u[t - j]; s += 2 * (1 - j / (L + 1)) * c / n; }
  return m / Math.sqrt(s / n);
}
const legendBelow = y => ({ orientation: 'h', x: 0, xanchor: 'left', y: y === undefined ? -0.2 : y, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } });

// ================================================================= volatility clustering
const CL = ['sp500', 'bet', 'btc'];
function clustering() {
  const k = +$('cl-k').value; $('cl-k-v').textContent = nf(k, 1) + ' s';
  const tr = [], lay = layout({ margin: { l: 56, r: 12, t: 16, b: 40 }, legend: legendBelow(-0.08), showlegend: true }), res = [];
  CL.forEach((m, i) => {
    const r = RET(m), dt = DATES[m], s = sdev(r), ax = i === 0 ? '' : String(i + 1), big = [];
    for (let t = 0; t < r.length; t++) if (Math.abs(r[t]) > k * s) big.push(t);
    tr.push({ x: dt, y: r, mode: 'lines', name: LAB[m] + ' daily log return (%)', line: { color: COL[m], width: 0.6 }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' });
    tr.push({ x: big.map(t => dt[t]), y: big.map(t => r[t]), mode: 'markers', name: '|r| > ' + nf(k, 1) + ' s', legendgroup: 'big', showlegend: i === 0, marker: { color: K.navy, size: 4 }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' });
    const top = 1 - i * 0.345;
    lay['xaxis' + ax] = AX('', { type: 'date', anchor: 'y' + ax, domain: [0, 1] });
    lay['yaxis' + ax] = AX('%', { domain: [top - 0.29, top], anchor: 'x' + ax });
    // clustering: probability of another large day within the next 5 days
    const q = big.length / r.length, set = new Set(big); let hit = 0, nb = 0;
    for (const t of big) { if (t + 5 >= r.length) continue; nb++; for (let j = 1; j <= 5; j++) if (set.has(t + j)) { hit++; break; } }
    res.push(T.cl(SHORT[m], big.length, pct(q, 1), pct(nb ? hit / nb : 0, 0), pct(1 - (1 - q) ** 5, 0)));
  });
  plot('cl-chart', tr, lay);
  out('cl-out', res);
}

// ================================================================= ACF of returns and of their magnitude
function acfBlock() {
  const m = $('ac-m').value, dl = +$('ac-d').value, r = RET(m), L = 50, n = r.length;
  $('ac-d-v').textContent = nf(dl, 2);
  const a1 = acf(r, L), a2 = acf(r.map(v => Math.abs(v) ** dl), L), b = 1.96 / Math.sqrt(n), lags = range(1, L, 1);
  const lab = Math.abs(dl - 2) < 1e-9 ? 'ACF of squared returns r²' : Math.abs(dl - 1) < 1e-9 ? 'ACF of absolute returns |r|' : 'ACF of |r|^' + dl.toFixed(2);
  plot('ac-chart', [
    { x: lags.map(v => v - 0.2), y: a1, type: 'bar', width: 0.4, name: 'ACF of returns r', marker: { color: K.blue }, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags },
    { x: lags.map(v => v + 0.2), y: a2, type: 'bar', width: 0.4, name: lab, marker: { color: K.red }, hovertemplate: 'lag %{customdata}: %{y:.3f}<extra></extra>', customdata: lags },
    { x: [null], y: [null], mode: 'markers', name: '95% band under i.i.d.', marker: { color: K.band, size: 12, symbol: 'square' }, hoverinfo: 'skip' }
  ], layout({ title: ttl(LAB[m] + ', ' + n + ' daily returns'), shapes: [{ type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: -b, y1: b, fillcolor: K.band, opacity: 0.6, line: { width: 0 }, layer: 'below' }],
    xaxis: AX('Lag (trading days)', { range: [0, L + 1] }), yaxis: AX('Autocorrelation', { range: [-0.15, 0.45] }), legend: legendBelow(-0.25) }));
  const out1 = a1.filter(v => Math.abs(v) > b).length, out2 = a2.filter(v => Math.abs(v) > b).length;
  out('ac-out', [T.ac(SHORT[m], nf(a1[0], 3), nf(dl, 2), nf(a2[0], 3), out1, out2, nf(b, 3)), T.ac2(nf(exkurt(r), 1))]);
}

// ================================================================= simulated GARCH path
function simulation() {
  const S = D.sim, p = +$('si-p').value; let a = +$('si-a').value;
  if (a > p) { a = p; $('si-a').value = a; }
  const be = p - a, om = 1 - p, z = S.z, n = z.length, x = new Array(n), s = new Array(n);
  $('si-a-v').textContent = nf(a, 2); $('si-p-v').textContent = nf(p, 3);
  let s2 = om / (1 - p);
  for (let t = 0; t < n; t++) { if (t > 0) s2 = om + a * x[t - 1] ** 2 + be * s2; s[t] = Math.sqrt(s2); x[t] = s[t] * z[t]; }
  const day = range(0, n - 1, 1), lim = Math.max(6, ...x.map(Math.abs), ...S.iid.map(Math.abs)) * 1.05;
  plot('si-chart', [
    { x: day, y: S.iid, mode: 'lines', name: 'i.i.d. Normal, same unconditional variance', line: { color: K.teal, width: 0.7 }, xaxis: 'x', yaxis: 'y', hoverinfo: 'skip' },
    { x: day, y: x, mode: 'lines', name: `GARCH(1,1): ω = ${om.toFixed(3)}, α = ${a.toFixed(2)}, β = ${be.toFixed(3)}`, line: { color: K.blue, width: 0.7 }, xaxis: 'x2', yaxis: 'y2', hoverinfo: 'skip' },
    { x: day, y: s.map(v => 2 * v), mode: 'lines', name: '±2σ<sub>t</sub>', legendgroup: 'b', line: { color: K.red, width: 1 }, xaxis: 'x2', yaxis: 'y2', hovertemplate: 'day %{x}: 2σ = %{y:.2f}<extra></extra>' },
    { x: day, y: s.map(v => -2 * v), mode: 'lines', showlegend: false, legendgroup: 'b', line: { color: K.red, width: 1 }, xaxis: 'x2', yaxis: 'y2', hoverinfo: 'skip' }
  ], layout({ margin: { l: 56, r: 12, t: 16, b: 40 },
    xaxis: AX('', { anchor: 'y', domain: [0, 1], showticklabels: false }), yaxis: AX('Return (%)', { domain: [0.55, 1], range: [-lim, lim] }),
    xaxis2: AX('Day', { anchor: 'y2', domain: [0, 1] }), yaxis2: AX('Return (%)', { domain: [0, 0.45], range: [-lim, lim] }), legend: legendBelow(-0.14) }));
  const den = 1 - p * p - 2 * a * a, kt = den > 0 ? 3 * (1 - p * p) / den - 3 : Infinity;
  out('si-out', [T.si(nf(be, 3), nf(om, 3), isFinite(kt) ? nf(kt, 2) : null, nf(exkurt(x), 2), nf(exkurt(S.iid), 2), days(halfLife(p)))]);
}

// ================================================================= delta method near p = 1
function deltaMethod() {
  const Dm = D.delta, pc = +$('dm-p').value, A = D.ppy.sp500;
  $('dm-p-v').textContent = nf(pc, 5);
  const ps = []; for (let i = 0; i < 800; i++) ps.push(0.975 + (0.99995 - 0.975) * i / 799);
  const h = ps.map(p => Math.log(0.5) / Math.log(p)), tang = ps.map(p => Dm.hl + Dm.dh * (p - Dm.pers)), lv = p => Math.sqrt(A * Dm.omega / (1 - p));
  const hc = halfLife(pc), tc = Dm.hl + Dm.dh * (pc - Dm.pers), vc = pc < 1 ? lv(pc) : Infinity;
  const band = { type: 'rect', xref: 'x', yref: 'paper', x0: Dm.p_lo, x1: 1, y0: 0, y1: 1, fillcolor: K.amber, opacity: 0.18, line: { width: 0 }, layer: 'below' };
  plot('dm-h', [
    { x: ps, y: h, mode: 'lines', name: 'Half-life h(p) = ln 0.5 / ln p', line: { color: K.blue, width: 2 }, hovertemplate: 'p %{x:.4f}: %{y:.0f} days<extra></extra>' },
    { x: ps, y: tang, mode: 'lines', name: 'Delta-method tangent at p̂', line: { color: K.red, width: 2, dash: 'dash' }, hovertemplate: 'p %{x:.4f}: %{y:.0f} days<extra></extra>' },
    { x: [Dm.pers], y: [Dm.hl], mode: 'markers', name: `p̂ = ${Dm.pers.toFixed(4)}, ĥ = ${Dm.hl.toFixed(0)} days`, marker: { color: K.navy, size: 9 }, hoverinfo: 'skip' },
    { x: [Dm.p_lo], y: [Dm.hl_lo], mode: 'markers', name: `h(lower end) = ${Dm.hl_lo.toFixed(0)} days`, marker: { color: K.green, size: 9, symbol: 'square' }, hoverinfo: 'skip' },
    { x: [pc], y: [Math.min(hc, 1500)], mode: 'markers', name: 'Chosen p', marker: { color: K.teal, size: 12, symbol: 'diamond', line: { color: '#fff', width: 1.5 } }, hovertemplate: 'p %{x:.5f}<extra></extra>' }
  ], layout({ title: ttl('Half-life: the delta-method line falls below zero'), shapes: [band, vline(1, K.navy, 'dot'), hline(0, K.navy)],
    annotations: [{ x: Dm.p_lo + 0.0004, y: 0.62, yref: 'paper', yanchor: 'bottom', xanchor: 'left', align: 'left', showarrow: false, text: `95% interval for p:<br>[${Dm.p_lo.toFixed(4)}; ${Dm.p_hi.toFixed(4)}]`, font: { size: 11, color: K.navy } }],
    xaxis: AX('Persistence p = α + β', { range: [0.974, 1.0012] }), yaxis: AX('Days', { range: [-300, 1500] }), legend: legendBelow(-0.24) }));
  plot('dm-v', [
    { x: ps, y: ps.map(lv), mode: 'lines', name: 'Long-run volatility √(A ω̂ / (1 − p)), ω̂ fixed', line: { color: K.purple, width: 2 }, hovertemplate: 'p %{x:.4f}: %{y:.1f}%<extra></extra>' },
    { x: [Dm.pers], y: [Dm.vol], mode: 'markers', name: `Estimate ${Dm.vol.toFixed(1)}% p.a. (s.e. ${Dm.se_vol.toFixed(1)})`, marker: { color: K.navy, size: 9 }, hoverinfo: 'skip' },
    { x: [pc], y: [Math.min(vc, 80)], mode: 'markers', name: 'Chosen p', marker: { color: K.teal, size: 12, symbol: 'diamond', line: { color: '#fff', width: 1.5 } }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Long-run volatility: division by 1 − p'), shapes: [band], xaxis: AX('Persistence p = α + β', { range: [0.974, 1.0012] }), yaxis: AX('% per year', { range: [0, 80] }), legend: legendBelow(-0.24) }));
  out('dm-out', [T.dm(nf(pc, 5), days(hc), nf(tc, 0), isFinite(vc) ? nf(vc, 1) + '%' : '∞'), T.dm2(nf(Dm.se_p, 4), nf(Dm.se_hl, 0), nf(Dm.p_lo, 4), nf(Dm.p_hi, 4))]);
}

// ================================================================= term structure of volatility
const TS_L = ['sp500', 'bet', 'gold'], TS_ALL = ['sp500', 'bet', 'gold', 'btc'];
const MONTHS = D.garch_t.sp500.origin_dates;
function tsCurve(m, ym) {
  const G = D.garch_t[m], k = G.origin_dates.findIndex(d => d.slice(0, 7) === ym);
  if (k < 0) return null;
  const p = G.alpha + G.beta, H = 250, A = D.ppy[m]; let v = G.next_var[k], cs = 0; const avg = [];
  for (let h = 1; h <= H; h++) { cs += v; avg.push(Math.sqrt(cs / h * A)); v = G.omega + p * v; }
  return { date: G.origin_dates[k], avg, unc: p < 0.999 ? Math.sqrt(A * G.omega / (1 - p)) : null };
}
function termStructure() {
  const k = +$('ts-t').value, ym = MONTHS[k].slice(0, 7), hh = range(1, 250, 1);
  $('ts-t-v').textContent = MONTHS[k];
  const cur = {}; TS_ALL.forEach(m => (cur[m] = tsCurve(m, ym)));
  const tr = [], shapes = [];
  TS_L.forEach(m => {
    const c = cur[m]; if (!c) return;
    tr.push({ x: hh, y: c.avg, mode: 'lines', name: LAB[m], line: { color: COL[m], width: 2 }, hovertemplate: LAB[m] + ', h = %{x}: %{y:.1f}%<extra></extra>' });
    if (c.unc) shapes.push(hline(c.unc, COL[m], 'dot'));
  });
  shapes.forEach(s => (s.line.width = 1.2));
  plot('ts-l', tr, layout({ title: ttl('Forecast from ' + cur.sp500.date + ' (dotted: long-run level)'), shapes, xaxis: AX('Horizon h (days)'), yaxis: AX('Average volatility over [T+1, T+h] (% p.a.)'), legend: legendBelow(-0.2) }));
  const b = cur.btc;
  plot('ts-r', b ? [{ x: hh, y: b.avg, mode: 'lines', name: 'Bitcoin', line: { color: COL.btc, width: 2 }, hovertemplate: 'Bitcoin, h = %{x}: %{y:.1f}%<extra></extra>' }] : [],
    layout({ title: ttl(b ? 'Bitcoin, from ' + b.date + ' (α + β = 1)' : 'Bitcoin: data start in September 2014'), showlegend: true, xaxis: AX('Horizon h (days)'), yaxis: AX('Average volatility over [T+1, T+h] (% p.a.)', { rangemode: 'tozero' }), legend: legendBelow(-0.2) }));
  out('ts-out', TS_ALL.filter(m => cur[m]).map(m => T.ts(SHORT[m], nf(cur[m].avg[0], 1), nf(cur[m].avg[249], 1), cur[m].unc ? nf(cur[m].unc, 1) : null)));
}

// ================================================================= persistence
const PE = ['sp500', 'bet', 'btc', 'eurron', 'gold', 'bettr'];
function persistence() {
  const hc = +$('pe-h').value, hh = range(0, 250, 1);
  $('pe-h-v').textContent = hc;
  const tr = PE.map(m => {
    const P = D.persistence[m];
    return { x: hh, y: hh.map(h => P.p ** h), mode: 'lines', name: `${LAB[m]}: α+β = ${P.p.toFixed(4)}, half-life ${days(P.hl)} days`, line: { color: COL[m], width: 2, dash: m === 'btc' ? 'dash' : 'solid' }, hovertemplate: SHORT[m] + ', h = %{x}: %{y:.2f}<extra></extra>' };
  });
  plot('pe-chart', tr, layout({ shapes: [hline(0.5, K.navy, 'dash'), vline(hc, K.navy, 'dot')], xaxis: AX('Horizon h (days)', { range: [-5, 255] }), yaxis: AX('Share of a variance shock left, (α+β)^h', { range: [0, 1.04] }), legend: legendBelow(-0.2) }));
  out('pe-out', [T.pe(hc, PE.map(m => SHORT[m] + ' ' + pct(D.persistence[m].p ** hc, 0)).join(', '))]);
}

// ================================================================= S&P 500: GARCH volatility and VIX
const VX_EVENTS = [['2008-10-15', 'Lehman'], ['2020-03-16', 'COVID-19'], ['2025-04-08', 'Tariffs']];
const VX_PER = { all: ['2000-01-01', '2026-12-31'], gfc: ['2008-01-01', '2009-12-31'], covid: ['2020-01-01', '2020-12-31'], tariffs: ['2025-01-01', '2025-12-31'] };
function vix() {
  const G = D.garch_t.sp500, a = +$('vx-a').value, per = VX_PER[$('vx-per').value], dt = DATES.sp500, A = D.ppy.sp500;
  $('vx-a-v').textContent = nf(a, 4);
  const v = garchFilter(RET('sp500'), G.mu, G.omega, a, G.beta, G.backcast).map(s => Math.sqrt(s * A)), V = D.vix.vix;
  const g = [], x = []; for (let i = 0; i < dt.length; i++) if (V[i] !== null && dt[i] >= per[0] && dt[i] <= per[1]) { g.push(v[i]); x.push(V[i]); }
  const idx = s => { let i = dt.findIndex(d => d > s); return (i < 0 ? dt.length : i) - 1; };
  plot('vx-chart', [
    { x: dt, y: V, mode: 'lines', name: 'VIX (30-day implied volatility, % p.a.)', line: { color: K.amber, width: 0.9 }, connectgaps: false, hovertemplate: 'VIX %{x}: %{y:.1f}<extra></extra>' },
    { x: dt, y: v, mode: 'lines', name: 'GARCH(1,1)-t conditional volatility (% p.a.)', line: { color: K.blue, width: 0.9 }, hovertemplate: 'GARCH %{x}: %{y:.1f}<extra></extra>' }
  ], layout({ annotations: VX_EVENTS.map(([d, l]) => ({ x: dt[idx(d)], y: v[idx(d)], text: l, showarrow: false, xanchor: 'left', xshift: 6, font: { size: 10, color: K.navy } })),
    xaxis: AX('', { type: 'date', range: [per[0], per[1] > dt[dt.length - 1] ? dt[dt.length - 1] : per[1]] }), yaxis: AX('Annualised volatility (%)', { rangemode: 'tozero' }), legend: legendBelow(-0.12) }));
  const p = a + G.beta;
  out('vx-out', [T.vx(nf(a, 4), nf(p, 4), days(halfLife(p)), nf(corr(g, x), 2), nf(mean(x), 1), nf(mean(g), 1), pct(x.filter((u, i) => u > g[i]).length / x.length, 0))]);
}

// ================================================================= news impact curve
function nicValue(M, kind, e, s2) {
  if (kind === 'EGARCH') { const z = e / Math.sqrt(s2); return Math.exp(M.omega + M['alpha[1]'] * (Math.abs(z) - Math.sqrt(2 / Math.PI)) + M['gamma[1]'] * z + M['beta[1]'] * Math.log(s2)); }
  return M.omega + (M['alpha[1]'] + (e < 0 ? M['gamma[1]'] : 0)) * e * e + M['beta[1]'] * s2;
}
function newsImpact() {
  const N = D.nic, e0 = +$('ni-e').value, s2 = +$('ni-s').value, E = range(-6, 6, 0.05);
  $('ni-e-v').textContent = nf(e0, 1) + '%'; $('ni-s-v').textContent = nf(s2, 2);
  const MODS = [['GARCH', K.blue, 'GARCH(1,1)-t'], ['GJR', K.red, 'GJR-GARCH(1,1)-t'], ['EGARCH', K.green, 'EGARCH(1,1)-t']];
  const tr = MODS.map(([m, c, l]) => ({ x: E, y: E.map(e => nicValue(N.models[m], m, e, s2)), mode: 'lines', name: l, line: { color: c, width: 2 }, hovertemplate: l + ': shock %{x:.1f}%, variance %{y:.2f}<extra></extra>' }));
  MODS.forEach(([m, c]) => tr.push({ x: [e0], y: [nicValue(N.models[m], m, e0, s2)], mode: 'markers', showlegend: false, marker: { color: c, size: 9, line: { color: '#fff', width: 1.5 } }, hoverinfo: 'skip' }));
  plot('ni-chart', tr, layout({ title: ttl('S&P 500, σ²(t−1) = ' + s2.toFixed(2) + ' (%²)'), shapes: [vline(0, K.navy), vline(e0, K.navy, 'dot')], xaxis: AX('Shock ε(t−1) (%)'), yaxis: AX('Next-day variance σ²(t) (%²)', { rangemode: 'tozero' }), legend: legendBelow(-0.2) }));
  const a = Math.abs(e0), v = (m, e) => nicValue(N.models[m], m, e, s2);
  out('ni-out', [T.ni(nf(-a, 1), nf(v('GJR', -a), 2), nf(v('EGARCH', -a), 2), nf(v('GARCH', -a), 2)),
    T.ni('+' + nf(a, 1), nf(v('GJR', a), 2), nf(v('EGARCH', a), 2), nf(v('GARCH', a), 2)),
    T.ni2(nf(v('GJR', -a) / v('GJR', a), 1), nf(v('EGARCH', -a) / v('EGARCH', a), 1))]);
}

// ================================================================= innovations: Normal and Student-t
let INN = null;
function innPrep() {
  if (INN) return INN;
  const z = D.innov.z, n = z.length, bw = 0.25 * sdev(z), grid = range(-7, 5, 12 / 399).slice(0, 400);
  const kde = grid.map(g => { let s = 0; for (const v of z) { const u = (g - v) / bw; s += Math.exp(-0.5 * u * u); } return s / (n * bw * Math.sqrt(2 * Math.PI)); });
  const q = [...z].sort((a, b) => a - b), pr = q.map((_, i) => (i + 0.5) / n), keep = [];
  q.forEach((v, i) => { if (Math.abs(v) > 2.5 || i % 6 === 0) keep.push(i); });            // all tail points, every 6th point in the centre
  INN = { z, n, grid, kde, q: keep.map(i => q[i]), pr: keep.map(i => pr[i]), nq: keep.map(i => nppf(pr[i])), below4: z.filter(v => v < -4).length };
  return INN;
}
function innovations() {
  const I = innPrep(), nu = +$('in-nu').value;
  $('in-nu-v').textContent = nf(nu, 2);
  // Student-t quantiles: exact at 161 nodes in the Normal quantile scale, interpolated in between
  const nodes = range(-4.5, 4.5, 9 / 160), tq = nodes.map(x => tppfU(Math.min(Math.max(ncdfApprox(x), 1e-12), 1 - 1e-12), nu));
  const tqAt = x => { const f = (x + 4.5) / (9 / 160), i = Math.min(Math.max(Math.floor(f), 0), nodes.length - 2), w = f - i; return tq[i] * (1 - w) + tq[i + 1] * w; };
  const lab = `Student-t, ν = ${nu.toFixed(1)} (unit variance)`;
  plot('in-d', [
    { x: I.grid, y: I.kde, mode: 'lines', name: 'Standardised residuals ẑ (kernel density)', line: { color: K.blue, width: 2 }, hovertemplate: 'z %{x:.2f}: %{y:.2e}<extra></extra>' },
    { x: I.grid, y: I.grid.map(npdf), mode: 'lines', name: 'Normal N(0,1)', line: { color: K.red, width: 2, dash: 'dash' }, hovertemplate: 'z %{x:.2f}: %{y:.2e}<extra></extra>' },
    { x: I.grid, y: I.grid.map(x => tpdfU(x, nu)), mode: 'lines', name: lab, line: { color: K.green, width: 2, dash: 'dashdot' }, hovertemplate: 'z %{x:.2f}: %{y:.2e}<extra></extra>' }
  ], layout({ xaxis: AX('z'), yaxis: AX('Density (log scale)', { type: 'log', range: [-5, 0], exponentformat: 'power' }), legend: legendBelow(-0.2) }));
  plot('in-q', [
    { x: I.nq, y: I.q, mode: 'markers', name: 'vs Normal quantiles', marker: { color: K.red, size: 3 }, hovertemplate: '%{x:.2f}, %{y:.2f}<extra></extra>' },
    { x: I.nq.map(tqAt), y: I.q, mode: 'markers', name: `vs Student-t (ν = ${nu.toFixed(1)}) quantiles`, marker: { color: K.green, size: 3 }, hovertemplate: '%{x:.2f}, %{y:.2f}<extra></extra>' },
    { x: [-8, 6], y: [-8, 6], mode: 'lines', showlegend: false, line: { color: K.navy, width: 1 }, hoverinfo: 'skip' }
  ], layout({ xaxis: AX('Theoretical quantile', { range: [-8, 6] }), yaxis: AX('Empirical quantile of ẑ', { range: [-8, 6] }), legend: legendBelow(-0.2) }));
  const et = I.n * tcdfU(-4, nu), en = I.n * ncdfApprox(-4);
  out('in-out', [T.inn(I.below4, nf(en, 2), nf(nu, 1), nf(et, 1)), T.inn2(nf(exkurt(I.z), 2), nu > 4 ? nf(6 / (nu - 4), 2) : null)]);
}
function ncdfApprox(x) {                                             // Normal cdf through erfc (Numerical Recipes, relative error < 1.2e-7)
  const z = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.5 * z), y = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? 1 - y / 2 : y / 2;
}

// ================================================================= out-of-sample forecasts
const OO_PER = { all: ['2016-01-01', '2026-12-31'], y2020: ['2020-01-01', '2020-12-31'], y2022: ['2022-01-01', '2022-12-31'], y2025: ['2025-01-01', '2025-12-31'] };
function oosPaths() {
  const O = D.oos, r = RET('sp500'), dt = DATES.sp500.slice(O.i0, O.i0 + O.n), px = r.slice(O.i0, O.i0 + O.n).map(v => v * v);
  return { O, r, dt, px };
}
let OOS = null;
function oos() {
  OOS = OOS || oosPaths();
  const { O, r, dt, px } = OOS, lam = +$('oo-l').value, per = OO_PER[$('oo-per').value], A = Math.sqrt(D.ppy.sp500);
  $('oo-l-v').textContent = nf(lam, 3);
  const ew = ewma(r, lam).slice(O.i0, O.i0 + O.n), gj = O.h['GJR-t'];
  plot('oo-chart', [
    { x: dt, y: px.map(v => Math.sqrt(v) * A), mode: 'markers', name: `Realised proxy |r|√A, A = ${D.ppy.sp500.toFixed(1)}`, marker: { color: K.teal, size: 3, opacity: 0.5 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' },
    { x: dt, y: gj.map(v => Math.sqrt(v) * A), mode: 'lines', name: 'GJR-GARCH-t one-day-ahead forecast', line: { color: K.red, width: 1 }, hovertemplate: 'GJR-t %{x}: %{y:.1f}%<extra></extra>' },
    { x: dt, y: ew.map(v => Math.sqrt(v) * A), mode: 'lines', name: `EWMA (λ = ${lam.toFixed(3)})`, line: { color: K.blue, width: 1 }, opacity: 0.85, hovertemplate: 'EWMA %{x}: %{y:.1f}%<extra></extra>' }
  ], layout({ xaxis: AX('', { type: 'date', range: [per[0], per[1] > dt[dt.length - 1] ? dt[dt.length - 1] : per[1]] }), yaxis: AX('Annualised volatility (%)', { range: [0, 110] }), legend: legendBelow(-0.12) }));
  const sel = []; dt.forEach((d, i) => { if (d >= per[0] && d <= per[1]) sel.push(i); });
  const ql = h => mean(sel.map(i => px[i] / h[i] + Math.log(h[i])));
  const lq = ql(ew), gq = ql(gj), e94 = ql(O.h.EWMA);
  out('oo-out', [T.oo(sel.length, dt[sel[0]], dt[sel[sel.length - 1]], nf(lam, 3), nf(lq, 3), nf(gq, 3), nf(e94, 3))]);
}

// ================================================================= relative QLIKE and Diebold-Mariano
function qlikeBlock() {
  OOS = OOS || oosPaths();
  const { O, dt, px } = OOS, loss = $('ql-loss').value, y0 = +$('ql-y').value;
  $('ql-y-v').textContent = y0;
  const sel = []; dt.forEach((d, i) => { if (+d.slice(0, 4) >= y0) sel.push(i); });
  const L = m => sel.map(i => (loss === 'qlike' ? px[i] / O.h[m][i] + Math.log(O.h[m][i]) : (px[i] - O.h[m][i]) ** 2));
  const base = L('GARCH-t'), res = O.models.map(m => { const l = L(m), d = l.map((v, i) => v - base[i]); return { m, loss: mean(l), diff: mean(d), t: m === 'GARCH-t' ? null : hacT(d, 5) }; });
  res.sort((a, b) => a.loss - b.loss);
  const col = res.map(o => (o.m === 'GARCH-t' ? K.blue : o.diff < 0 ? K.green : K.red));
  const LN = loss === 'qlike' ? 'QLIKE' : 'MSE', lo = Math.min(0, ...res.map(o => o.diff)), hi = Math.max(0, ...res.map(o => o.diff)), pad = 0.22 * (hi - lo);
  plot('ql-chart', [{ x: res.map(o => o.m), y: res.map(o => o.diff), type: 'bar', marker: { color: col }, text: res.map(o => (o.t === null ? '' : 'DM t = ' + o.t.toFixed(2))), textposition: 'outside', textfont: { size: 10, color: K.navy }, cliponaxis: false,
    hovertemplate: '%{x}: ' + LN + ' %{customdata:.4f}, difference %{y:.4f}<extra></extra>', customdata: res.map(o => o.loss) }],
    layout({ showlegend: false, title: ttl(`S&P 500, one-day forecasts from ${y0} (${sel.length} days)`), shapes: [hline(0, K.navy)], margin: { l: 70, r: 12, t: 40, b: 50 },
      xaxis: AX(''), yaxis: AX(LN + ' minus GARCH-t (lower = better)', { range: [lo - pad, hi + pad] }) }));
  const best = res[0], g = m => res.find(o => o.m === m);
  out('ql-out', [T.ql(y0, LN, best.m, nf(best.loss, loss === 'qlike' ? 3 : 2), nf(g('EWMA').t, 2), nf(g('Hist-20').t, 2))]);
}

// ================================================================= long memory
function longMemory() {
  const Lm = D.longmem, r1 = +$('lm-r').value, p = +$('lm-p').value, lags = range(1, 250, 1);
  $('lm-r-v').textContent = nf(r1, 3); $('lm-p-v').textContent = nf(p, 4);
  const geo = lags.map(k => r1 * p ** (k - 1));
  plot('lm-chart', [
    { x: lags, y: Lm.emp, mode: 'markers', name: 'S&P 500 data, ACF of |r|', marker: { color: K.blue, size: 4 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lags, y: Lm.garch, mode: 'lines', name: 'Simulated from fitted GARCH(1,1)-t', line: { color: K.red, width: 2 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lags, y: Lm.figarch, mode: 'lines', name: 'Simulated from fitted FIGARCH(1,d,1)-t', line: { color: K.green, width: 2, dash: 'dash' }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lags, y: geo, mode: 'lines', name: `Geometric decay ρ₁·p^(k−1), ρ₁ = ${r1.toFixed(3)}, p = ${p.toFixed(4)}`, line: { color: K.purple, width: 2, dash: 'dot' }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' }
  ], layout({ shapes: [hline(0, K.navy)], xaxis: AX('Lag (trading days, log scale)', { type: 'log', range: [-0.03, 2.42] }), yaxis: AX('Autocorrelation of |r|', { range: [-0.02, 0.45] }), legend: legendBelow(-0.2) }));
  // least-squares decay rate for this lag-1 level
  let bp = 0.9, bs = Infinity; for (let q = 0.9; q < 0.99995; q += 0.00005) { let s = 0; for (let k = 1; k <= 250; k++) s += (Lm.emp[k - 1] - r1 * q ** (k - 1)) ** 2; if (s < bs) { bs = s; bp = q; } }
  out('lm-out', [T.lm(nf(geo[0], 3), nf(geo[99], 3), nf(geo[249], 3), nf(Lm.emp[0], 3), nf(Lm.emp[99], 3), nf(Lm.emp[249], 3)), T.lm2(nf(r1, 3), nf(bp, 4), days(halfLife(bp)))]);
}

// ================================================================= quasi score-driven case study
const psi = x => x * Math.tanh(1000 * x / 2);
const qsdW = (z, e) => psi((1 + z) / (1 - 2 * z + z * e * e)) * e * e;
function qsd() {
  const Q = D.qsd, k = Q.tickers.indexOf($('qs-s').value), z = +$('qs-z').value, n = Q.tickers.length, pos = range(0, n - 1, 1);
  $('qs-z-v').textContent = nf(z, 3);
  const gap = Q.xi.map((x, i) => x - Q.zeta[i]), sig = Q.p_xi_zeta.map(p => p < 0.05);
  const ix = f => pos.filter(i => f(i)), lab = Q.tickers.map((t, i) => `${Q.names[i]} (${t})`);
  plot('qs-gap', [
    { x: ix(i => sig[i]), y: ix(i => sig[i]).map(i => gap[i]), mode: 'markers', name: 'ξ̂ − ζ̂, LR test of ξ = ζ significant at 5%', marker: { color: K.blue, size: 11 }, customdata: ix(i => sig[i]).map(i => lab[i]), hovertemplate: '%{customdata}: %{y:.3f}<extra></extra>' },
    { x: ix(i => !sig[i]), y: ix(i => !sig[i]).map(i => gap[i]), mode: 'markers', name: 'ξ̂ − ζ̂, not significant', marker: { color: 'rgba(0,0,0,0)', size: 11, line: { color: K.blue, width: 2 } }, customdata: ix(i => !sig[i]).map(i => lab[i]), hovertemplate: '%{customdata}: %{y:.3f}<extra></extra>' },
    { x: pos.map(i => i + 0.2), y: Q.zeta, mode: 'markers', name: 'ζ̂ (downweighting; 0 = GARCH-t)', marker: { color: K.red, size: 9, symbol: 'diamond' }, customdata: lab, hovertemplate: '%{customdata}: ζ̂ = %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl('QSD GARCH(1,1)-t, 11 S&P 500 stocks, 1995–2019'), margin: { l: 56, r: 12, t: 30, b: 90 },
    shapes: [hline(0, K.navy), ...pos.map(i => ({ type: 'line', x0: i, x1: i, y0: 0, y1: gap[i], line: { color: K.blue, width: 1.5 } })),
      { type: 'rect', x0: k - 0.45, x1: k + 0.45, yref: 'paper', y0: 0, y1: 1, fillcolor: K.band, opacity: 0.35, line: { width: 0 }, layer: 'below' }],
    xaxis: AX('', { tickvals: pos, ticktext: Q.tickers, range: [-0.6, n - 0.4] }), yaxis: AX('QSD GARCH(1,1)-t estimate', { range: [-0.02, 0.22] }), legend: legendBelow(-0.16) }));
  const E = range(-10, 10, 0.05);
  plot('qs-nic', [
    { x: E, y: E.map(e => e * e), mode: 'lines', name: 'GARCH(1,1)-t (ζ = 0)', line: { color: K.green, width: 1.8, dash: 'dash' }, hovertemplate: 'ε %{x:.1f}: %{y:.1f}<extra></extra>' },
    { x: E, y: E.map(e => qsdW(Q.xi_beta[k], e)), mode: 'lines', name: `Beta-t-GARCH, ζ = ξ̂ = ${Q.xi_beta[k].toFixed(3)}`, line: { color: K.red, width: 2, dash: 'dot' }, hovertemplate: 'ε %{x:.1f}: %{y:.1f}<extra></extra>' },
    { x: E, y: E.map(e => qsdW(z, e)), mode: 'lines', name: `QSD, ζ = ${z.toFixed(3)}`, line: { color: K.blue, width: 2.2 }, hovertemplate: 'ε %{x:.1f}: %{y:.1f}<extra></extra>' }
  ], layout({ title: ttl(lab[k] + ': news impact'), xaxis: AX('Standardised shock ε'), yaxis: AX('Impact on f(t+1) (units of α f(t))', { range: [0, 40] }), legend: legendBelow(-0.2) }));
  out('qs-out', [T.qs(lab[k], nf(Q.xi[k], 3), nf(Q.zeta[k], 3), nf(Q.p_xi_zeta[k], 3)), T.qs2(nf(z, 3), nf(qsdW(z, 5), 1), nf(qsdW(Q.xi_beta[k], 5), 1))]);
}

// ================================================================= MF2-GARCH case study (Conrad & Engle, 2025)
const MF = D.mf2;
const MF_DT = calendar(MF);
const MF_VAR = (() => { const m = mean(MF.r); return mean(MF.r.map(v => (v - m) ** 2)); })();
function mf2Filter(r, th, m) {                                       // case_mf2garch.mf2_filter: h_0 = 1, tau fixed at var(r) for the first m days
  const [mu, al, ga, be, l0, l1, l2] = th, phi = al + ga / 2 + be, n = r.length;
  const sig = new Array(n), tau = new Array(n), V = new Array(n);
  let h = 1, t = MF_VAR, run = 0;
  for (let i = 0; i < n; i++) {
    const e = r[i] - mu; sig[i] = Math.sqrt(h * t); tau[i] = Math.sqrt(t);
    V[i] = e * e / h; run += V[i]; if (i >= m) run -= V[i - m];
    const hn = (1 - phi) + (al + (e < 0 ? ga : 0)) * e * e / t + be * h;
    t = i + 1 >= m ? l0 + l1 * run / m + l2 * t : MF_VAR; h = hn;
  }
  return { sig, tau };
}
const MF_PER = { pre: '2010–2019', full: '2010–2026' };
function mf2Block() {
  const m = +$('mf-m').value, per = $('mf-per').value, th = MF.grid[String(m)], A = Math.sqrt(MF.ppy), B = MF.burn;
  $('mf-m-v').textContent = m;
  const F = mf2Filter(MF.r, th, m), sig = F.sig.map(v => v * A), tau = F.tau.map(v => v * A);
  let k = B; for (let i = B; i < tau.length; i++) if (tau[i] > tau[k]) k = i;
  let j = B; for (let i = B; i < tau.length; i++) if (tau[i] < tau[j]) j = i;
  plot('mf-vol', [
    { x: MF_DT, y: sig, mode: 'lines', name: 'Conditional volatility √(h·τ)', line: { color: K.blue, width: 0.6 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' },
    { x: MF_DT, y: tau, mode: 'lines', name: `Long-term volatility √τ, m = ${m}`, line: { color: K.red, width: 2 }, hovertemplate: '√τ %{x}: %{y:.1f}%<extra></extra>' },
    { x: [null], y: [null], mode: 'markers', name: 'NBER recessions', marker: { color: K.band, size: 12, symbol: 'square' }, hoverinfo: 'skip' }
  ], layout({ title: ttl('S&P 500, MF2-GARCH-rw-m, 1990–2026'), xaxis: AX('', { type: 'date' }), yaxis: AX('Annualised volatility (%)', { range: [0, 80] }), legend: legendBelow(-0.12),
    shapes: MF.nber.map(([a, b]) => ({ type: 'rect', xref: 'x', x0: a, x1: b, yref: 'paper', y0: 0, y1: 1, fillcolor: K.band, opacity: 0.7, line: { width: 0 }, layer: 'below' })) }));
  const H = MF.horizons, lab = ['1d', '1w', ...H.slice(2).map((h, i) => 'M' + (i + 1))], tr = [];
  for (const [mk, col, nm] of [['gjr', K.navy, 'GJR-GARCH'], ['mf2', K.red, 'MF2-GARCH']])
    for (const [pk, dash, sym] of [['full', 'solid', 'circle'], ['pre', 'dash', 'square']]) {
      const on = per === 'both' || per === pk;
      tr.push({ x: lab, y: H.map(h => MF.oos[pk][h][mk + '_ql']), mode: 'lines+markers', name: `${nm}, ${MF_PER[pk].replace('–', '-')}`, opacity: on ? 1 : 0.25,
        line: { color: col, width: on ? 1.8 : 1, dash }, marker: { color: col, size: 6, symbol: sym }, hovertemplate: `${nm} ${MF_PER[pk]}, %{x}: %{y:.3f}<extra></extra>` });
    }
  plot('mf-ql', tr, layout({ title: ttl('Out of sample, 20-year rolling window, m = 63'), margin: { l: 64, r: 12, t: 40, b: 60 }, shapes: [hline(1, K.navy)], legend: legendBelow(-0.3),
    xaxis: AX('Horizon: next day, next week, forward month M1-M8'), yaxis: AX('Relative QLIKE (historical = 1)') }));
  const [, al, ga, be, , l1, l2] = th, phi = al + ga / 2 + be, lam = l1 + l2, db = (MF.bic[String(m)] - MF.bic[String(MF.m)]) * MF.n_eff;
  const lines = [T.mf(m, m === MF.m ? null : nf(db, 1), nf(phi, 3), days(halfLife(phi)), nf(lam, 3), nf(slowRoot(l1, l2, m), 4), days(halfLife(slowRoot(l1, l2, m))), nf(tau[k], 1), MF_DT[k], nf(tau[j], 1), MF_DT[j])];
  for (const pk of (per === 'both' ? ['pre', 'full'] : [per])) {
    const o = MF.oos[pk];
    lines.push(T.mf2(MF_PER[pk], nf(o['1m'].mf2_ql, 3), nf(o['1m'].gjr_ql, 3), nf(o['1m'].dm_ql, 2), nf(o['8m'].mf2_ql, 3), nf(o['8m'].gjr_ql, 3), nf(o['8m'].dm_ql, 2)));
  }
  out('mf-out', lines);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  $('cl-chart').style.height = '560px'; $('si-chart').style.height = '470px';
  on(['cl-k'], clustering); P('cl-play', 'cl-k', range(1, 6, 0.5), 700);
  on(['ac-m', 'ac-d'], acfBlock); P('ac-play', 'ac-d', range(0.25, 4, 0.25), 450);
  on(['si-a', 'si-p'], simulation); P('si-play', 'si-p', range(0.5, 0.995, 0.005), 90);
  $('dm-p').value = D.delta.pers.toFixed(5); on(['dm-p'], deltaMethod); P('dm-play', 'dm-p', range(0.975, 0.99995, 0.00025), 70);
  $('ts-t').max = MONTHS.length - 1; $('ts-t').value = MONTHS.length - 1; on(['ts-t'], termStructure); P('ts-play', 'ts-t', range(0, MONTHS.length - 1, 2), 90);
  on(['pe-h'], persistence); P('pe-play', 'pe-h', range(0, 250, 5), 120);
  $('vx-a').value = D.garch_t.sp500.alpha.toFixed(4); on(['vx-a', 'vx-per'], vix); P('vx-play', 'vx-a', range(0.02, 0.125, 0.005), 350);
  $('ni-s').value = String(D.nic.s2bar); on(['ni-e', 'ni-s'], newsImpact); P('ni-play', 'ni-e', range(-6, 6, 0.2), 120);
  $('in-nu').value = String(D.innov.nu_t); on(['in-nu'], innovations); P('in-play', 'in-nu', range(3, 30, 0.5), 250);
  on(['oo-l', 'oo-per'], oos); P('oo-play', 'oo-l', range(0.8, 0.995, 0.005), 200);
  on(['ql-loss', 'ql-y'], qlikeBlock); P('ql-play', 'ql-y', range(2016, 2025, 1), 800);
  $('lm-p').value = D.longmem.pers.toFixed(4); on(['lm-r', 'lm-p'], longMemory); P('lm-play', 'lm-p', range(0.95, 0.999, 0.001), 150);
  $('qs-s').addEventListener('input', () => { $('qs-z').value = D.qsd.zeta[D.qsd.tickers.indexOf($('qs-s').value)].toFixed(3); qsd(); });
  $('qs-z').value = D.qsd.zeta[D.qsd.tickers.indexOf($('qs-s').value)].toFixed(3); on(['qs-z'], qsd); P('qs-play', 'qs-z', range(0, 0.3, 0.005), 150);
  on(['mf-m', 'mf-per'], mf2Block); P('mf-play', 'mf-m', range(5, 160, 1), 120);
  const PFX = { 'clustering': 'cl', 'acf': 'ac', 'simulation': 'si', 'delta-method': 'dm', 'term-structure': 'ts', 'persistence': 'pe', 'vix': 'vx',
    'news-impact': 'ni', 'innovations': 'in', 'oos': 'oo', 'qlike': 'ql', 'long-memory': 'lm', 'qsd': 'qs', 'volatility-cycles': 'mf' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  clustering(); acfBlock(); simulation(); deltaMethod(); termStructure(); persistence(); vix(); newsImpact(); innovations(); oos(); qlikeBlock(); longMemory(); qsd(); mf2Block();
}
window.CH5 = { acf, exkurt, corr, garchFilter, ewma, hacT, tcdfU, tppfU, nppf, ncdfApprox, tsCurve, nicValue, qsdW, halfLife, mf2Filter };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

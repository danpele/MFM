// Chapter 8 interactive page: one block per chart slide, computed in the browser from ch8_data.js.
(function () {
'use strict';
const D = window.CH8_DATA;
const { LANG, sum, mean, sdev, rng, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH8_TEXT;

// ---------------------------------------------------------------- colours (same as the slides)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  navy: '#1F2A44', band: '#C5D2E8', teal: '#17A2B8', yellow: '#F1C40F' };
const MC = D.mcol, MODELS = D.models, ASSETS = D.assets, LAB = D.labels, GARCH = ['GARCH-t', 'FHS', 'GARCH-EVT'];
const LEVELS = { 'VaR1': 0.01, 'VaR2.5': 0.025, 'VaR5': 0.05 };
const legendBelow = y => ({ orientation: 'h', x: 0, xanchor: 'left', y: y === undefined ? -0.2 : y, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } });
const PV_SCALE = [[0, '#CD0000'], [0.25, '#F4B6B6'], [0.5, '#FFFFFF'], [0.75, '#BFD8BF'], [1, '#2E7D32']];

// ---------------------------------------------------------------- formatting
const ni = n => { const s = String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, LANG === 'ro' ? ' ' : ','); return s.replace('-', '−'); };
const dmy = s => s.slice(8, 10) + '.' + s.slice(5, 7) + '.' + s.slice(0, 4);
const pv = p => (p === null || p === undefined || !isFinite(p) ? '—' : p < 0.001 ? '< ' + nf(0.001, 3) : '= ' + nf(p, 3));   // used as 'p ' + pv(p)
const levC = a => (100 * a).toFixed(Math.abs(a - 0.025) < 1e-9 ? 1 : 0);   // chart text (English)
const levR = a => nf(100 * a, Math.abs(a - 0.025) < 1e-9 ? 1 : 0);        // readouts
const rgba = (h, a) => `rgba(${parseInt(h.slice(1, 3), 16)},${parseInt(h.slice(3, 5), 16)},${parseInt(h.slice(5, 7), 16)},${a})`;
const pc1 = x => { const r = Math.round(10 * x) / 10; return nf(r, Number.isInteger(r) ? 0 : 1); };
const pvCell = p => (p === null || !isFinite(p) ? '—' : p < 0.001 ? '<.001' : p.toFixed(3));

// ---------------------------------------------------------------- data helpers
function calendar(R) {
  const o = [R.d0]; let t = Date.parse(R.d0 + 'T00:00:00Z');
  for (const g of R.gaps) { t += g * 864e5; o.push(new Date(t).toISOString().slice(0, 10)); }
  return o;
}
const DATES = {}; for (const n of ASSETS) DATES[n] = calendar(D.cal[n]);
const LOSS = {}; for (const n of ASSETS) LOSS[n] = D.L[n].map(v => v / 100);           // loss in %
const NT = n => DATES[n].length;
const yearIdx = (n, y) => { const dt = DATES[n]; let i = dt.findIndex(d => +d.slice(0, 4) >= y); return i < 0 ? dt.length : i; };
const yearEnd = (n, y) => { const dt = DATES[n]; let i = dt.findIndex(d => +d.slice(0, 4) > y); return (i < 0 ? dt.length : i) - 1; };
const hitsOf = (n, m, lev) => D.hits[n][m][lev];
const isG = m => GARCH.includes(m);
const avail = (n, m, i0) => !isG(m) || i0 >= D.first[n];                    // forecasts exist on the whole sample from i0
function countIn(arr, a, b) { let c = 0; for (const v of arr) if (v >= a && v <= b) c++; return c; }
function hitVec(n, m, lev, a, b) { const h = new Uint8Array(b - a + 1); for (const v of hitsOf(n, m, lev)) if (v >= a && v <= b) h[v - a] = 1; return h; }

// ---------------------------------------------------------------- distributions
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
function tcdf(x, nu) { const p = 0.5 * ibeta(nu / 2, 0.5, nu / (nu + x * x)); return x < 0 ? p : 1 - p; }
const tpdf = (x, nu) => Math.exp(lgamma((nu + 1) / 2) - lgamma(nu / 2) - 0.5 * Math.log(nu * Math.PI) - (nu + 1) / 2 * Math.log1p(x * x / nu));
function tppf(p, nu) { let lo = -500, hi = 500; for (let i = 0; i < 100; i++) { const m = (lo + hi) / 2; if (tcdf(m, nu) < p) lo = m; else hi = m; } return (lo + hi) / 2; }
function ncdf(x) {                                                   // erfc approximation (Numerical Recipes), relative error < 1.2e-7
  const z = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.5 * z), y = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? 1 - y / 2 : y / 2;
}
const chi2sf1 = x => (x <= 0 ? 1 : 2 * (1 - ncdf(Math.sqrt(x))));
const chi2sf2 = x => Math.exp(-Math.max(x, 0) / 2);
const CRIT = 3.841458820694124;                                      // 95% quantile of chi2(1)

// ---------------------------------------------------------------- VaR tests (as in mfm_data.py)
const xlogy = (n, q) => (n > 0 ? n * Math.log(q) : 0);
function kupiecLR(x, n, a) {
  const ph = x / n, l0 = (n - x) * Math.log(1 - a) + x * Math.log(a), l1 = x > 0 && x < n ? (n - x) * Math.log(1 - ph) + x * Math.log(ph) : 0;
  return -2 * (l0 - l1);
}
function christoffersen(h, a) {
  let n00 = 0, n01 = 0, n10 = 0, n11 = 0;
  for (let t = 1; t < h.length; t++) { if (h[t - 1]) { if (h[t]) n11++; else n10++; } else if (h[t]) n01++; else n00++; }
  const p01 = n01 / (n00 + n01), p11 = n10 + n11 > 0 ? n11 / (n10 + n11) : 0, p = (n01 + n11) / (n00 + n01 + n10 + n11);
  const lind = xlogy(n00, 1 - p01) + xlogy(n01, p01) + xlogy(n10, 1 - p11) + xlogy(n11, p11), l0 = xlogy(n00 + n10, 1 - p) + xlogy(n01 + n11, p);
  const LRind = -2 * (l0 - lind), TT = n00 + n01 + n10 + n11, x = n01 + n11;
  const LRuc = -2 * (xlogy(TT - x, 1 - a) + xlogy(x, a) - xlogy(TT - x, 1 - p) - xlogy(x, p));
  return { n00, n01, n10, n11, p01, p11, LRind, pind: chi2sf1(LRind), LRcc: LRuc + LRind, pcc: chi2sf2(LRuc + LRind) };
}
function durationTest(h) {                                           // Christoffersen-Pelletier, Weibull, censored first/last spell
  const n = h.length, pos = []; for (let t = 0; t < n; t++) if (h[t]) pos.push(t);
  if (!pos.length) return { b: NaN, LR: NaN, p: NaN };
  const ends = [-1, ...pos, h[n - 1] === 0 ? n - 1 : pos[pos.length - 1]], Dd = [];
  for (let i = 1; i < ends.length; i++) { const v = ends[i] - ends[i - 1]; if (v > 0) Dd.push(v); }
  if (Dd.length < 3) return { b: NaN, LR: NaN, p: NaN };
  const c1 = h[0] === 0, cn = h[n - 1] === 0, U = Dd.map((_, i) => !((i === 0 && c1) || (i === Dd.length - 1 && cn)));
  const nU = U.filter(Boolean).length, lnD = Dd.map(Math.log), sU = sum(lnD.filter((_, i) => U[i]));
  const prof = b => { let s = 0; for (const v of Dd) s += Math.pow(v, b); return nU * Math.log(b) + nU * Math.log(nU / s) + (b - 1) * sU - nU; };
  let lo = Math.log(0.05), hi = Math.log(5); const gr = (Math.sqrt(5) - 1) / 2;
  for (let i = 0; i < 120; i++) { const m1 = hi - gr * (hi - lo), m2 = lo + gr * (hi - lo); if (prof(Math.exp(m1)) < prof(Math.exp(m2))) lo = m1; else hi = m2; }
  const b = Math.exp((lo + hi) / 2), LR = Math.max(2 * (prof(b) - prof(1)), 0);
  return { b, LR, p: chi2sf1(LR) };
}
function binomLogPmf(T, p) {                                         // log P(X = x), x = 0..T
  const o = new Float64Array(T + 1), lp = Math.log(p), lq = Math.log1p(-p); let lc = 0;
  for (let x = 0; x <= T; x++) { if (x > 0) lc += Math.log((T - x + 1) / x); o[x] = lc + x * lp + (T - x) * lq; }
  return o;
}
function acceptRange(T, a) { let lo = -1, hi = -1; for (let x = 0; x <= T; x++) if (kupiecLR(x, T, a) <= CRIT) { if (lo < 0) lo = x; hi = x; } return [lo, hi]; }
function exactPower(T, p, lohi) { if (p <= 0) return lohi[0] > 0 ? 1 : 0; if (p >= 1) return 1; const lp = binomLogPmf(T, p); let acc = 0; for (let x = lohi[0]; x <= lohi[1]; x++) acc += Math.exp(lp[x]); return Math.max(0, 1 - acc); }
const localPower = (T, p, a) => { const lam = Math.max(T * (p - a) ** 2 / (a * (1 - a)), 1e-12), r = Math.sqrt(lam), c = Math.sqrt(CRIT); return ncdf(-c - r) + 1 - ncdf(c - r); };

// ---------------------------------------------------------------- DM with Newey-West long-run variance (divisor T)
function dmStat(d, q) {
  const n = d.length, m = mean(d), u = d.map(v => v - m); let v = sum(u.map(x => x * x)) / n;
  for (let j = 1; j <= q; j++) { let c = 0; for (let t = j; t < n; t++) c += u[t] * u[t - j]; v += 2 * (1 - j / (q + 1)) * c / n; }
  return m / Math.sqrt(v / n);
}

// ---------------------------------------------------------------- heat maps of p-values
function pvHeat(id, title, models, cols, P, txt, lev, colorbar) {
  const z = P.map(r => r.map(p => (p === null || !isFinite(p) ? null : Math.log10(Math.min(Math.max(p, 1e-4), 1)))));
  const ann = [], shapes = [];
  P.forEach((r, i) => r.forEach((p, j) => {
    const rej = p !== null && isFinite(p) && p < lev;
    ann.push({ x: j, y: i, text: rej ? '<b>' + txt[i][j] + '</b>' : txt[i][j], showarrow: false, font: { size: 10, color: p !== null && isFinite(p) && p < 0.001 ? '#FFFFFF' : K.navy } });
    if (rej) shapes.push({ type: 'rect', x0: j - 0.47, x1: j + 0.47, y0: i - 0.45, y1: i + 0.45, line: { color: K.navy, width: 1.6 } });
  }));
  plot(id, [{ type: 'heatmap', z, x: cols.map((_, j) => j), y: models.map((_, i) => i), zmin: -4, zmax: 0, colorscale: PV_SCALE, showscale: !!colorbar, xgap: 1, ygap: 1,
    colorbar: { title: { text: 'log10 p', font: { size: 10 } }, tickfont: { size: 10 }, len: 0.8, thickness: 10 },
    customdata: P.map(r => r.map(p => pvCell(p))), hovertemplate: '%{customdata}<extra></extra>' }],
    layout({ title: ttl(title), annotations: ann, shapes, margin: { l: 72, r: colorbar ? 40 : 8, t: 30, b: 60 },
      xaxis: AX('', { tickvals: cols.map((_, j) => j), ticktext: cols, tickangle: -30, showgrid: false, zeroline: false, ticks: '' }),
      yaxis: AX('', { tickvals: models.map((_, i) => i), ticktext: models, autorange: 'reversed', showgrid: false, zeroline: false, ticks: '' }) }));
}

// ================================================================= four markets: losses, VaR and breaches
function fourAssets() {
  const lev = $('fa-l').value, y = +$('fa-y').value;
  $('fa-y-v').textContent = y;
  const tr = [], lay = layout({ margin: { l: 50, r: 10, t: 24, b: 40 }, legend: legendBelow(-0.08), annotations: [] }), res = [];
  ASSETS.forEach((n, i) => {
    const ax = i === 0 ? '' : String(i + 1), dt = DATES[n], e = yearEnd(n, y), L = LOSS[n], V = D.evt[n][lev];
    const col = i % 2, row = i >> 1, x0 = col * 0.53, y1 = 1 - row * 0.55;
    const h = hitsOf(n, 'GARCH-EVT', lev).filter(t => t <= e);
    tr.push({ x: dt.slice(0, e + 1), y: L.slice(0, e + 1), mode: 'lines', name: 'Daily loss', legendgroup: 'l', showlegend: i === 0, line: { color: K.orange, width: 0.5 }, opacity: 0.75, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' });
    tr.push({ x: dt.slice(0, e + 1), y: V.slice(0, e + 1).map(v => (v === null ? null : v / 100)), mode: 'lines', name: `VaR ${lev.slice(3)}% (GARCH-EVT)`, legendgroup: 'v', showlegend: i === 0, line: { color: K.red, width: 0.8 }, connectgaps: false, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: 'VaR %{x}: %{y:.2f}%<extra></extra>' });
    tr.push({ x: h.map(t => dt[t]), y: h.map(t => L[t]), mode: 'markers', name: 'Breach (available forecasts)', legendgroup: 'b', showlegend: i === 0, marker: { color: K.blue, size: 4 }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' });
    lay['xaxis' + ax] = AX('', { type: 'date', anchor: 'y' + ax, domain: [x0, x0 + 0.47], range: [dt[0], dt[dt.length - 1]] });
    const lo = Math.min(...L), hi = Math.max(...L, ...V.filter(v => v !== null).map(v => v / 100));
    lay['yaxis' + ax] = AX('Loss (%)', { anchor: 'x' + ax, domain: [y1 - 0.4, y1], range: [lo * 1.08, hi * 1.06] });
    lay.annotations.push({ text: LAB[n], x: x0 + 0.235, xref: 'paper', y: y1 + 0.005, yref: 'paper', yanchor: 'bottom', showarrow: false, font: { size: 12, color: K.navy } });
    if (D.first[n] > 0) lay.annotations.push({ text: `${D.first[n]} days without a forecast`, x: x0 + 0.01, xref: 'paper', xanchor: 'left', y: y1 - 0.01, yref: 'paper', yanchor: 'top', showarrow: false, font: { size: 10, color: K.navy }, bgcolor: 'rgba(255,255,255,0.85)' });
    const nd = Math.max(0, e - D.first[n] + 1);
    res.push(T.fa(LAB[n], h.length, ni(nd), nd ? pct(h.length / nd, 2) : '—'));
  });
  plot('fa-chart', tr, lay);
  out('fa-out', [T.fa0(y, levR(LEVELS[lev])), ...res]);
}

// ================================================================= S&P 500: two VaR forecasts
function spVar() {
  const y = +$('sv-y').value, n = 'sp500', dt = DATES[n], L = LOSS[n], whole = y < 2007;
  const per = whole ? dt[0].slice(0, 4) + '–' + dt[dt.length - 1].slice(0, 4) : String(y);
  $('sv-y-v').textContent = per;
  const a = whole ? 0 : yearIdx(n, y), b = whole ? dt.length - 1 : yearEnd(n, y);
  const hs = hitsOf(n, 'HS', 'VaR1'), gt = hitsOf(n, 'GARCH-t', 'VaR1');
  const tr = [
    { x: dt, y: L, mode: 'lines', name: 'Daily loss of the S&P 500', line: { color: K.orange, width: 0.6 }, opacity: 0.7, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: dt, y: D.sp_var.HS.map(v => v / 100), mode: 'lines', name: 'VaR 1%, HS', line: { color: MC.HS, width: 1 }, hovertemplate: 'HS %{x}: %{y:.2f}%<extra></extra>' },
    { x: dt, y: D.sp_var['GARCH-t'].map(v => v / 100), mode: 'lines', name: 'VaR 1%, GARCH-t', line: { color: MC['GARCH-t'], width: 1 }, hovertemplate: 'GARCH-t %{x}: %{y:.2f}%<extra></extra>' },
    { x: hs.map(t => dt[t]), y: hs.map(t => L[t]), mode: 'markers', name: 'Breach, HS', marker: { color: MC.HS, size: 4, symbol: 'circle' }, hovertemplate: 'HS breach %{x}: %{y:.2f}%<extra></extra>' },
    { x: gt.map(t => dt[t]), y: gt.map(t => L[t] + 0.4), mode: 'markers', name: 'Breach, GARCH-t (+0.4 pp)', marker: { color: MC['GARCH-t'], size: 5, symbol: 'x-thin', line: { color: MC['GARCH-t'], width: 1.2 } }, hovertemplate: 'GARCH-t breach %{x}<extra></extra>' }
  ];
  let ymax = 0, ymin = 0; for (let t = a; t <= b; t++) { ymax = Math.max(ymax, L[t] + 0.4, D.sp_var.HS[t] / 100, D.sp_var['GARCH-t'][t] / 100); ymin = Math.min(ymin, L[t]); }
  plot('sv-chart', tr, layout({ xaxis: AX('', { type: 'date', range: [dt[a], dt[b]] }), yaxis: AX('Loss (%)', { range: [ymin * 1.05 - 0.2, ymax * 1.05 + 0.2] }), legend: legendBelow(-0.12) }));
  const nd = b - a + 1, xh = countIn(hs, a, b), xg = countIn(gt, a, b);
  out('sv-out', [T.sv(per, ni(nd), nf(0.01 * nd, 1), xh, xg),
    T.sv2(pv(chi2sf1(kupiecLR(xh, nd, 0.01))), pv(chi2sf1(kupiecLR(xg, nd, 0.01))))]);
}

// ================================================================= Kupiec statistic against the number of breaches
function kupBars(id, TT, a) {
  const xm = Math.max(7, Math.floor(0.03 * TT * a / 0.01 + 1e-9)), xs = range(0, xm, 1), lr = xs.map(x => kupiecLR(x, TT, a)), acc = lr.map(v => v <= CRIT);
  const ymax = Math.max(25, 1.05 * Math.max(...lr));
  plot(id, [
    { x: xs.filter((_, i) => acc[i]), y: lr.filter((_, i) => acc[i]), type: 'bar', name: 'Not rejected at 5%', marker: { color: K.green }, hovertemplate: 'x = %{x}: LR = %{y:.2f}<extra></extra>' },
    { x: xs.filter((_, i) => !acc[i]), y: lr.filter((_, i) => !acc[i]), type: 'bar', name: 'Rejected at 5%', marker: { color: K.red }, hovertemplate: 'x = %{x}: LR = %{y:.2f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: 'χ²₁ 5% critical value 3.84', line: { color: K.navy, dash: 'dash', width: 1.2 }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`T = ${TT} days, α = ${levC(a)}%`), barmode: 'overlay', bargap: 0.2, shapes: [hline(CRIT, K.navy, 'dash')],
    xaxis: AX('Number of breaches x', { range: [-0.7, xm + 0.7] }), yaxis: AX('LR_uc', { range: [0, ymax] }), legend: legendBelow(-0.24) }));
  const [lo, hi] = acceptRange(TT, a), lp = binomLogPmf(TT, a); let acc2 = 0; for (let x = lo; x <= hi; x++) acc2 += Math.exp(lp[x]);
  return { lo, hi, size: 1 - acc2, lr0: kupiecLR(0, TT, a), p0: Math.exp(lp[0]) };
}
function kupiec() {
  const a = +$('kp-a').value, TT = +$('kp-T').value;
  $('kp-T-v').textContent = ni(TT);
  const r1 = kupBars('kp-top', 250, a), r2 = kupBars('kp-bot', TT, a);
  out('kp-out', [T.kp(ni(250), r1.lo, r1.hi, nf(250 * a, 1), pct(r1.size, 1)), T.kp(ni(TT), r2.lo, r2.hi, nf(TT * a, 1), pct(r2.size, 1)), T.kp0(nf(r1.lr0, 2), pct(r1.p0, 1))]);
}

// ================================================================= power of the POF test
const PIS = range(0, 0.04, 0.0001);
const POW_CACHE = {};
function powerCurve(TT) {
  if (POW_CACHE[TT]) return POW_CACHE[TT];
  const lh = acceptRange(TT, 0.01), ex = PIS.map(p => exactPower(TT, p, lh)), as = PIS.map(p => localPower(TT, p, 0.01));
  const up = PIS.map((p, i) => i).filter(i => PIS[i] > 0.01), i2 = PIS.findIndex(p => Math.abs(p - 0.02) < 1e-9), i1 = PIS.findIndex(p => Math.abs(p - 0.01) < 1e-9);
  const first = th => { const i = up.find(k => ex[k] >= th); return i === undefined ? null : PIS[i]; };
  return (POW_CACHE[TT] = { ex, as, pi50: first(0.5), pi80: first(0.8), pow2: ex[i2], asy2: as[i2], size: ex[i1] });
}
function pofPower() {
  const TT = +$('pp-T').value; $('pp-T-v').textContent = ni(TT);
  const A = powerCurve(250), B = powerCurve(TT), x = PIS.map(p => 100 * p);
  plot('pp-chart', [
    { x, y: A.ex, mode: 'lines', name: 'Exact power, T = 250', line: { color: K.blue, width: 2 }, hovertemplate: 'π = %{x:.2f}%: %{y:.3f}<extra></extra>' },
    { x, y: A.as, mode: 'lines', name: 'Local asymptotic power, T = 250', line: { color: K.blue, width: 1.6, dash: 'dash' }, hovertemplate: 'π = %{x:.2f}%: %{y:.3f}<extra></extra>' },
    { x, y: B.ex, mode: 'lines', name: `Exact power, T = ${TT}`, line: { color: K.red, width: 2 }, hovertemplate: 'π = %{x:.2f}%: %{y:.3f}<extra></extra>' },
    { x, y: B.as, mode: 'lines', name: `Local asymptotic power, T = ${TT}`, line: { color: K.red, width: 1.6, dash: 'dash' }, hovertemplate: 'π = %{x:.2f}%: %{y:.3f}<extra></extra>' }
  ], layout({ shapes: [hline(0.05, K.navy, 'dot'), vline(1, K.navy, 'dot')], xaxis: AX('True breach probability (%) of a VaR 1% forecast'), yaxis: AX('Rejection probability at 5%', { range: [0, 1.02] }), legend: legendBelow(-0.2) }));
  const f = (t, R) => T.pp(ni(t), pct(R.size, 1), pct(R.pow2, 0), pct(R.asy2, 0), R.pi50 === null ? '> 4%' : nf(100 * R.pi50, 2) + '%', R.pi80 === null ? '> 4%' : nf(100 * R.pi80, 2) + '%');
  out('pp-out', TT === 250 ? [f(250, A)] : [f(250, A), f(TT, B)]);
}

// ================================================================= breach rates by model and market
function breachRates() {
  const lev = $('br-l').value, y0 = +$('br-y').value, a = LEVELS[lev];
  $('br-y-v').textContent = y0;
  const tr = [], ann = [], res = [], w = 0.78 / MODELS.length;
  const S = ASSETS.map(n => { const i0 = yearIdx(n, y0); return { i0, n1: NT(n) - i0 }; });
  MODELS.forEach((m, i) => {
    const yv = ASSETS.map((n, j) => (avail(n, m, S[j].i0) && S[j].n1 > 0 ? 100 * countIn(hitsOf(n, m, lev), S[j].i0, NT(n) - 1) / S[j].n1 : null));
    tr.push({ x: ASSETS.map((_, j) => j + (i - (MODELS.length - 1) / 2) * w), y: yv, type: 'bar', width: w, name: m, marker: { color: MC[m] }, hovertemplate: m + ': %{y:.2f}%<extra></extra>' });
  });
  ASSETS.forEach((n, j) => {
    const miss = MODELS.filter(m => !avail(n, m, S[j].i0));
    if (miss.length) ann.push({ x: j, y: 0.98, yref: 'paper', yanchor: 'top', text: miss.join(', ') + '<br>withheld: incomplete sample', showarrow: false, font: { size: 9, color: K.navy } });
    const rows = MODELS.filter(m => avail(n, m, S[j].i0)).map(m => { const x = countIn(hitsOf(n, m, lev), S[j].i0, NT(n) - 1); return { m, x, p: chi2sf1(kupiecLR(x, S[j].n1, a)) }; });
    const rej = rows.filter(r => r.p < 0.05).map(r => r.m);
    res.push(T.br(LAB[n], ni(S[j].n1), rows.map(r => r.m + ' ' + pct(r.x / S[j].n1, 2)).join(', '), rej.length ? rej.join(', ') : T.none));
  });
  tr.push({ x: [null], y: [null], mode: 'lines', name: `Nominal ${levC(a)}%`, line: { color: K.navy, dash: 'dash', width: 1.2 }, hoverinfo: 'skip' });
  plot('br-chart', tr, layout({ annotations: ann, shapes: [hline(100 * a, K.navy, 'dash')], bargap: 0,
    xaxis: AX('', { tickvals: [0, 1, 2, 3], ticktext: ASSETS.map(n => LAB[n]), range: [-0.6, 3.4] }), yaxis: AX(`Breach rate of VaR ${levC(a)}% (%)`, { rangemode: 'tozero' }), legend: legendBelow(-0.12) }));
  out('br-out', res);
}

// ================================================================= breach timeline and the independence test
function timeline() {
  const m = $('tl-m').value, s = +$('tl-s').value, k = +$('tl-n').value, n = 'sp500', dt = DATES[n];
  const e = Math.min(s + k - 1, +dt[dt.length - 1].slice(0, 4));
  $('tl-s-v').textContent = s; $('tl-n-v').textContent = k;
  const tr = MODELS.map((mm, i) => {
    const xs = [], ys = [];
    for (const t of hitsOf(n, mm, 'VaR1')) { xs.push(dt[t], dt[t], null); ys.push(i - 0.35, i + 0.35, null); }
    return { x: xs, y: ys, mode: 'lines', name: mm, showlegend: false, line: { color: MC[mm], width: mm === m ? 1.6 : 1 }, hoverinfo: 'skip' };
  });
  const a = yearIdx(n, s), b = yearEnd(n, e);
  plot('tl-chart', tr, layout({ margin: { l: 80, r: 12, t: 16, b: 50 }, shapes: [{ type: 'rect', xref: 'x', yref: 'paper', x0: dt[a], x1: dt[b], y0: 0, y1: 1, fillcolor: K.band, opacity: 0.45, line: { width: 0 }, layer: 'below' }],
    xaxis: AX('Breach days of VaR 1%, S&P 500', { type: 'date' }), yaxis: AX('', { tickvals: MODELS.map((_, i) => i), ticktext: MODELS, range: [5.6, -0.6], showgrid: false, zeroline: false, ticks: '' }) }));
  const h = hitVec(n, m, 'VaR1', a, b), c = christoffersen(h, 0.01);
  out('tl-out', [T.tl(m, s, e, c.n00, c.n01, c.n10, c.n11), T.tl2(nf(c.p01, 4), nf(c.p11, 4), nf(c.LRind, 2), pv(c.pind), nf(c.LRcc, 2), pv(c.pcc))]);
}

// ================================================================= p-values of the VaR tests
let VP = null;
function vpPrep() {
  if (VP) return VP;
  VP = { uc: [], cc: [], dur: [] };
  MODELS.forEach(m => {
    const ru = [], rc = [], rd = [];
    ASSETS.forEach(n => {
      if (!avail(n, m, 0)) { ru.push(null); rc.push(null); rd.push(null); return; }
      const h = hitVec(n, m, 'VaR1', 0, NT(n) - 1), x = hitsOf(n, m, 'VaR1').length;
      ru.push(chi2sf1(kupiecLR(x, NT(n), 0.01))); rc.push(christoffersen(h, 0.01).pcc); rd.push(durationTest(h).p);
    });
    VP.uc.push(ru); VP.cc.push(rc); VP.dur.push(rd);
  });
  return VP;
}
function varPvalues() {
  const lev = +$('vp-s').value, P = vpPrep(), cols = ASSETS.map(n => LAB[n]);
  $('vp-s-v').textContent = pc1(100 * lev) + '%';
  const tx = M => M.map(r => r.map(pvCell));
  pvHeat('vp-uc', 'Kupiec POF', MODELS, cols, P.uc, tx(P.uc), lev);
  pvHeat('vp-cc', 'Christoffersen CC', MODELS, cols, P.cc, tx(P.cc), lev);
  pvHeat('vp-dur', 'Duration (Weibull)', MODELS, cols, P.dur, tx(P.dur), lev);
  const cnt = M => { let r = 0, c = 0; M.forEach(row => row.forEach(p => { if (p !== null && isFinite(p)) { c++; if (p < lev) r++; } })); return [r, c]; };
  const [u1, u2] = cnt(P.uc), [c1, c2] = cnt(P.cc), [d1, d2] = cnt(P.dur);
  const dqp = MODELS.map(m => ASSETS.map(n => D.dq[n + '|' + m])), [q1, q2] = cnt(dqp);
  out('vp-out', [T.vp(pc1(100 * lev), u1, u2, c1, c2, d1, d2), T.vp2(q1, q2)]);
}

// ================================================================= Basel traffic light through time
const FRTB = x => (x <= 4 ? 1.5 : x >= 10 ? 2.0 : [1.70, 1.76, 1.83, 1.88, 1.92][x - 5]);
const zone = x => (x <= 4 ? 'green' : x <= 9 ? 'yellow' : 'red');
function rollCount(n, m, w) {                                         // exceptions in the last w days, defined once w forecasts exist
  const N = NT(n), h = hitVec(n, m, 'VaR1', 0, N - 1), o = new Array(N).fill(null), f = isG(m) ? D.first[n] : 0; let c = 0;
  for (let t = f; t < N; t++) { c += h[t]; if (t - w >= f) c -= h[t - w]; if (t - f >= w - 1) o[t] = c; }
  return o;
}
const TF_M = ['HS', 'Normal', 'GARCH-t', 'FHS'];
let TF = {};
function traffic() {
  const n = $('tf-a').value, dt = DATES[n], N = dt.length, el = $('tf-t');
  if (+el.max !== N - 1) { el.max = N - 1; el.value = N - 1; }
  const k = Math.min(+el.value, N - 1); $('tf-t-v').textContent = dmy(dt[k]);
  if (!TF[n]) TF[n] = Object.fromEntries(TF_M.map(m => [m, rollCount(n, m, 250)]));
  const R = TF[n], top = Math.max(40, 1.05 * Math.max(...TF_M.flatMap(m => R[m].filter(v => v !== null))));
  const tr = TF_M.map(m => ({ x: dt, y: R[m], mode: 'lines', name: m, line: { color: MC[m], width: 1.2, shape: 'hv' }, connectgaps: false, hovertemplate: m + ' %{x}: %{y}<extra></extra>' }));
  const band = (y0, y1, c, o) => ({ type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0, y1, fillcolor: c, opacity: o, line: { width: 0 }, layer: 'below' });
  plot('tf-chart', tr, layout({ shapes: [band(-0.5, 4.5, K.green, 0.10), band(4.5, 9.5, K.yellow, 0.15), band(9.5, top, K.red, 0.10), vline(dt[k], K.navy, 'dot')],
    annotations: [['green', 2, K.green], ['yellow', 7, K.amber], ['red', (9.5 + top) / 2, K.red]].map(([t, y, c]) => ({ x: 1.005, xref: 'paper', xanchor: 'left', y, text: t, showarrow: false, font: { size: 11, color: c } })),
    margin: { l: 60, r: 50, t: 16, b: 40 }, xaxis: AX('', { type: 'date' }), yaxis: AX('Exceptions of VaR 1% in the last 250 days', { range: [-0.5, top] }), legend: legendBelow(-0.12) }));
  const now = TF_M.map(m => (R[m][k] === null ? T.tfNA(m) : T.tfNow(m, R[m][k], T.zone[zone(R[m][k])], nf(FRTB(R[m][k]), 2))));
  const sh = TF_M.filter(m => R[m].some(v => v !== null)).map(m => { const v = R[m].filter(x => x !== null); return T.tfSh(m, pct(v.filter(x => x >= 10).length / v.length, 1), pct(v.filter(x => x >= 5 && x <= 9).length / v.length, 1), Math.max(...v)); });
  out('tf-out', [T.tf(dmy(dt[k]), now.join('; ')), T.tf2(LAB[n], sh.join('; '))]);
}

// ================================================================= exceedance residuals (McNeil-Frey)
function mfBoot(e, B, seed) {                                         // i.i.d. bootstrap of the centred residuals, one-sided p-value
  const n = e.length, m = mean(e), s = sdev(e), t0 = m / (s / Math.sqrt(n)), ec = e.map(v => v - m), u = rng(seed).u; let c = 0;
  for (let b = 0; b < B; b++) { let s1 = 0, s2 = 0; for (let i = 0; i < n; i++) { const v = ec[Math.floor(u() * n)]; s1 += v; s2 += v * v; } const mb = s1 / n, vb = (s2 - n * mb * mb) / (n - 1); if (mb / Math.sqrt(vb / n) >= t0) c++; }
  return { t: t0, p: c / B };
}
function mfRes() {
  const n = $('mf-a').value, y = +$('mf-y').value, e = yearEnd(n, y), full = e === NT(n) - 1;
  $('mf-y-v').textContent = y;
  if (e < 0) { plot('mf-chart', [], layout({ xaxis: AX(''), yaxis: AX('Exceedance residual (L − ES) / σ (σ: forecast volatility)') })); out('mf-out', [T.mf0(LAB[n], dmy(DATES[n][0]))]); return; }
  const tr = [], res = [], ms = [];
  MODELS.forEach((m, i) => {
    if (!avail(n, m, 0)) return;
    const pos = hitsOf(n, m, 'VaR2.5'), r = D.es[n][m].res.filter((_, k) => pos[k] <= e);
    if (r.length < 3) return;
    ms.push(m);
    tr.push({ type: 'box', y: r, x: r.map(() => m), name: m, marker: { color: MC[m], size: 3, outliercolor: K.navy }, line: { color: MC[m], width: 1.2 }, fillcolor: MC[m] + '80', boxpoints: 'outliers', showlegend: false, hovertemplate: m + ': %{y:.2f}<extra></extra>' });
    let t, p;
    if (full) { const J = D.esres[n + '|' + m]; t = J.MF_t; p = J.MF_p; } else ({ t, p } = mfBoot(r, 5000, 11 + i));
    res.push(T.mfRow(m, r.length, nf(mean(r), 3), nf(t, 2), pv(p)));
    tr.push({ x: [m], y: [mean(r)], mode: 'markers', name: 'Mean', legendgroup: 'mean', showlegend: tr.filter(o => o.legendgroup === 'mean').length === 0, marker: { color: '#000', symbol: 'diamond', size: 8 }, hovertemplate: 'mean %{y:.3f}<extra></extra>' });
  });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Expected under a correct ES (mean 0)', line: { color: K.navy, dash: 'dash', width: 1.2 }, hoverinfo: 'skip' });
  plot('mf-chart', tr, layout({ shapes: [hline(0, K.navy, 'dash')], xaxis: AX('', { categoryorder: 'array', categoryarray: MODELS.filter(m => ms.includes(m)) }),
    yaxis: AX('Exceedance residual (L − ES) / σ (σ: forecast volatility)'), legend: legendBelow(-0.12) }));
  out('mf-out', [T.mf(LAB[n], dmy(DATES[n][0]), dmy(DATES[n][e]), full), ...res]);
}

// ================================================================= Z2 on rolling windows
const Z2_M = ['HS', 'Normal', 'GARCH-t', 'FHS'];
function rollingZ2(n, m, w) {
  const N = NT(n), term = new Float64Array(N), pos = hitsOf(n, m, 'VaR2.5'), tv = D.es[n][m].term;
  pos.forEach((t, k) => (term[t] = tv[k]));
  const o = new Array(N).fill(null); let s = 0;
  for (let t = 0; t < N; t++) { s += term[t]; if (t >= w) s -= term[t - w]; if (t >= w - 1) o[t] = 1 - s / (w * 0.025); }
  return o;
}
function z2Roll() {
  const n = $('z2-a').value, w = +$('z2-n').value, dt = DATES[n];
  $('z2-n-v').textContent = w;
  const tr = [], res = [];
  Z2_M.forEach(m => {
    const z = rollingZ2(n, m, w), v = z.filter(x => x !== null);
    let k = z.indexOf(Math.min(...v));
    tr.push({ x: dt, y: z, mode: 'lines', name: m, line: { color: MC[m], width: 1.1 }, hovertemplate: m + ' %{x}: %{y:.2f}<extra></extra>' });
    res.push(T.z2Row(m, nf(z[k], 2), dmy(dt[k]), pct(v.filter(x => x < -0.7).length / v.length, 1), pct(v.filter(x => x < -1.8).length / v.length, 1)));
  });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Threshold −0.70 (5%)', line: { color: K.amber, dash: 'dash', width: 1.2 }, hoverinfo: 'skip' });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Threshold −1.8 (0.01%)', line: { color: K.red, dash: 'dash', width: 1.2 }, hoverinfo: 'skip' });
  plot('z2-chart', tr, layout({ shapes: [hline(-0.7, K.amber, 'dash'), hline(-1.8, K.red, 'dash')], xaxis: AX('', { type: 'date' }), yaxis: AX(`Z₂ over the last ${w} days`), legend: legendBelow(-0.12) }));
  out('z2-out', [T.z2(LAB[n], w), ...res]);
}

// ================================================================= p-values of the ES tests
function esPvalues() {
  const lev = +$('ep-s').value, kind = $('ep-k').value, cols = ASSETS.map(n => LAB[n]);
  $('ep-s-v').textContent = pc1(100 * lev) + '%';
  const get = (k) => MODELS.map(m => ASSETS.map(n => { const J = D.esres[n + '|' + m]; return J ? J[k] : null; }));
  const fmt = (M, d) => M.map(r => r.map(v => (v === null ? '—' : v.toFixed(d))));
  const P = { mf: get('MF_p'), z2: get('p2'), u: get('p_U') }, S = { mf: get('MF_t'), z2: get('Z2'), u: get('U_ES') };
  pvHeat('ep-mf', kind === 'stat' ? 'McNeil-Frey t' : 'McNeil-Frey', MODELS, cols, P.mf, kind === 'stat' ? fmt(S.mf, 2) : P.mf.map(r => r.map(pvCell)), lev);
  pvHeat('ep-z2', kind === 'stat' ? 'Acerbi-Szekely Z2' : 'Acerbi-Szekely Z2', MODELS, cols, P.z2, kind === 'stat' ? fmt(S.z2, 3) : P.z2.map(r => r.map(pvCell)), lev);
  pvHeat('ep-u', kind === 'stat' ? 'Du-Escanciano U' : 'Du-Escanciano U', MODELS, cols, P.u, kind === 'stat' ? fmt(S.u, 2) : P.u.map(r => r.map(pvCell)), lev);
  const rej = M => { const o = []; M.forEach((r, i) => r.forEach((p, j) => { if (p !== null && p < lev) o.push(MODELS[i] + ' (' + LAB[ASSETS[j]] + ')'); })); return o; };
  const notRej = ['sp500', 'bet'].map(n => MODELS.filter(m => ['MF_p', 'p2', 'p_U'].every(k => D.esres[n + '|' + m][k] >= lev)));
  out('ep-out', [T.ep(pc1(100 * lev), rej(P.mf).length, rej(P.z2).length, rej(P.u).length, P.mf.flat().filter(v => v !== null).length),
    T.ep2(notRej[0].join(', ') || T.none, notRej[1].join(', ') || T.none)]);
}

// ================================================================= elicitability: pinball and FZ0
function mPlus(v, nu) { const s = Math.sqrt((nu - 2) / nu), c = v / s; return s * ((nu + c * c) / (nu - 1) * tpdf(c, nu) - c * (1 - tcdf(c, nu))); }
function quantile(a, q) { const b = [...a].sort((x, y) => x - y), h = (b.length - 1) * q, i = Math.floor(h); return b[i] + (h - i) * ((b[Math.min(i + 1, b.length - 1)]) - b[i]); }
const Q0 = 1.963243161477561, E0 = 2.823871251815408;
function elicit() {
  const nu = +$('el-nu').value, a = +$('el-a').value;
  $('el-nu-v').textContent = nf(nu, 1);
  const s = Math.sqrt((nu - 2) / nu), q = tppf(1 - a, nu) * s, tq = q / s, es = tpdf(tq, nu) / a * (nu + tq * tq) / (nu - 1) * s;
  const vs = range(0, 120, 1).map(i => (1.2 + 2.4 * i / 120) * q / Q0), eg = range(0, 120, 1).map(i => (1.6 + 3.4 * i / 120) * es / E0);
  const mp = vs.map(v => mPlus(v, nu)), pin = mp.map((m, i) => m + a * vs[i]);
  const ip = pin.indexOf(Math.min(...pin));
  const Z = eg.map(e => vs.map((v, i) => (e >= v ? mp[i] / (a * e) + v / e + Math.log(e) - 1 : null)));
  const flat = Z.flat().filter(v => v !== null); let best = Infinity, bi = 0, bj = 0;
  Z.forEach((r, j) => r.forEach((v, i) => { if (v !== null && v < best) { best = v; bi = i; bj = j; } }));
  const lv = [0.01, 0.03, 0.08, 0.15, 0.3, 0.5].map(p => quantile(flat, p));
  plot('el-pin', [
    { x: vs, y: pin, mode: 'lines', name: 'Expected pinball loss', line: { color: K.blue, width: 2 }, hovertemplate: 'v = %{x:.3f}: %{y:.4f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: `True VaR ${levC(a)}% = ${q.toFixed(2)}`, line: { color: K.red, dash: 'dash', width: 1.4 }, hoverinfo: 'skip' }
  ], layout({ shapes: [vline(q, K.red, 'dash')], xaxis: AX('Reported VaR v'), yaxis: AX('Expected loss'), legend: legendBelow(-0.22) }));
  plot('el-fz', [
    ...lv.map((l, i) => ({ type: 'contour', x: vs, y: eg, z: Z, autocontour: false, contours: { coloring: 'lines', showlabels: i === 1 || i === 4, labelfont: { size: 9, color: K.blue }, labelformat: '.3f', start: l, end: l, size: 1 },
      line: { width: 1, color: K.blue }, colorscale: [[0, K.blue], [1, K.blue]], showscale: false, showlegend: false, name: 'Expected FZ0', hovertemplate: 'v %{x:.2f}, e %{y:.2f}: expected FZ0 %{z:.3f}<extra></extra>' })),
    { x: [vs[bi]], y: [eg[bj]], mode: 'markers', name: 'Minimum of expected FZ0', marker: { color: K.green, size: 9 }, hoverinfo: 'skip' },
    { x: [q], y: [es], mode: 'markers', name: `True (VaR, ES) = (${q.toFixed(2)}, ${es.toFixed(2)})`, marker: { color: K.red, size: 11, symbol: 'x' }, hoverinfo: 'skip' }
  ], layout({ xaxis: AX('Reported VaR v', { range: [vs[0], vs[120]] }), yaxis: AX('Reported ES e', { range: [eg[0], eg[120]] }), legend: legendBelow(-0.22) }));
  out('el-out', [T.el(nf(nu, 1), levR(a), nf(q, 3), nf(es, 3), nf(es / q, 3)), T.el2(nf(vs[ip], 3), nf(vs[bi], 3), nf(eg[bj], 3))]);
}

// ================================================================= mean FZ0 loss by model
const FZ_A = ['sp500', 'bet'];
function fzMeans(n, y0) { const F = D.fz[n], k = F.years.findIndex(y => y >= y0); const c = sum(F.cnt.slice(k)); return Object.fromEntries(MODELS.map(m => [m, sum(F.sum[m].slice(k)) / c])); }
function fz0() {
  const y0 = +$('fz-y').value; $('fz-y-v').textContent = y0;
  const M = Object.fromEntries(FZ_A.map(n => [n, fzMeans(n, y0)])), best = n => MODELS.reduce((b, m) => (M[n][m] < M[n][b] ? m : b), MODELS[0]);
  const w = 0.78 / MODELS.length;
  const tr = MODELS.map((m, i) => ({ x: ASSETS.map((_, j) => j + (i - 2.5) * w), y: ASSETS.map(n => (M[n] ? M[n][m] - M[n][best(n)] : null)), type: 'bar', width: w, name: m, marker: { color: MC[m] }, hovertemplate: m + ': %{y:.4f}<extra></extra>' }));
  plot('fz-chart', tr, layout({ annotations: ['btc', 'eurron'].map(n => ({ x: ASSETS.indexOf(n), y: 0.5, yref: 'paper', text: 'Comparison<br>unavailable', showarrow: false, font: { size: 11, color: K.navy } })),
    xaxis: AX('', { tickvals: [0, 1, 2, 3], ticktext: ASSETS.map(n => LAB[n]), range: [-0.6, 3.4] }), yaxis: AX('Mean FZ0 loss minus that of the best model', { rangemode: 'tozero' }), legend: legendBelow(-0.12) }));
  const n0 = D.fz.sp500.cnt.slice(D.fz.sp500.years.findIndex(y => y >= y0)).reduce((a, b) => a + b, 0);
  out('fz-out', [T.fz(y0, ni(n0)), ...FZ_A.map(n => { const b = best(n); return T.fzRow(LAB[n], b, nf(M[n][b], 3), nf(M[n]['GARCH-t'] - M[n].FHS, 3), nf(M[n]['GARCH-EVT'] - M[n].FHS, 4)); })]);
}

// ================================================================= Diebold-Mariano matrix, S&P 500
function fzDaily(m) { return m === 'FHS' ? null : D.fz_sp.diff[m]; }
function dmMatrix() {
  const q = +$('dm-q').value, y0 = +$('dm-y').value, i0 = yearIdx('sp500', y0), Tn = NT('sp500') - i0;
  $('dm-q-v').textContent = q; $('dm-y-v').textContent = y0;
  const diff = m => { const d = fzDaily(m); return d ? d.slice(i0) : new Array(Tn).fill(0); };
  const Dd = MODELS.map(diff), M = MODELS.map((a, i) => MODELS.map((b, j) => (i === j ? null : dmStat(Dd[i].map((v, t) => (v - Dd[j][t]) / 1e5), q))));
  const ann = []; M.forEach((r, i) => r.forEach((v, j) => { if (v !== null) ann.push({ x: j, y: i, text: v.toFixed(1), showarrow: false, font: { size: 11, color: K.navy } }); }));
  plot('dm-chart', [{ type: 'heatmap', z: M, x: MODELS.map((_, j) => j), y: MODELS.map((_, i) => i), zmin: -6, zmax: 6, colorscale: [[0, K.green], [0.5, '#FFFFFF'], [1, K.red]], xgap: 1, ygap: 1,
    colorbar: { title: { text: 'DM statistic (A minus B)', side: 'right', font: { size: 11 } }, tickfont: { size: 10 }, thickness: 12 }, hovertemplate: 'DM = %{z:.2f}<extra></extra>' }],
    layout({ annotations: ann, margin: { l: 90, r: 10, t: 16, b: 80 }, xaxis: AX('Model B', { tickvals: MODELS.map((_, j) => j), ticktext: MODELS, tickangle: -30, showgrid: false, zeroline: false, ticks: '' }),
      yaxis: AX('Model A', { tickvals: MODELS.map((_, i) => i), ticktext: MODELS, autorange: 'reversed', showgrid: false, zeroline: false, ticks: '' }) }));
  const g = (a, b) => M[MODELS.indexOf(a)][MODELS.indexOf(b)];
  let sig = 0; for (let i = 0; i < 6; i++) for (let j = i + 1; j < 6; j++) if (Math.abs(M[i][j]) > 1.96) sig++;
  const rule = Math.floor(4 * Math.pow(Tn / 100, 2 / 9));
  out('dm-out', [T.dm(y0, ni(Tn), q, rule), T.dm2(nf(g('HS', 'FHS'), 2), nf(g('GARCH-t', 'FHS'), 2), nf(g('GARCH-EVT', 'FHS'), 2), nf(g('Normal', 'HS'), 2), sig)]);
}

// ================================================================= model confidence set
function mcsBlock() {
  const a = +$('mc-a').value; $('mc-a-v').textContent = pct(a, 0);
  const z = MODELS.map(m => ASSETS.map(n => (D.mcs[n] ? D.mcs[n][m] : null)));
  const ann = [];
  z.forEach((r, i) => r.forEach((v, j) => { if (v !== null) ann.push({ x: j, y: i, text: v.toFixed(3) + (v >= a ? ' *' : ''), showarrow: false, font: { size: 11, color: v > 0.25 && v < 0.75 ? K.navy : '#FFFFFF' } }); }));
  ASSETS.forEach((n, j) => { if (!D.mcs[n]) ann.push({ x: j, y: 2.5, text: 'Unavailable', textangle: -90, showarrow: false, font: { size: 11, color: K.navy } }); });
  const shapes = []; z.forEach((r, i) => r.forEach((v, j) => { if (v !== null && v >= a) shapes.push({ type: 'rect', x0: j - 0.48, x1: j + 0.48, y0: i - 0.46, y1: i + 0.46, line: { color: K.navy, width: 2 } }); }));
  plot('mc-chart', [{ type: 'heatmap', z, x: ASSETS.map((_, j) => j), y: MODELS.map((_, i) => i), zmin: 0, zmax: 1, colorscale: [[0, K.red], [0.5, '#FFFFFF'], [1, K.green]], xgap: 1, ygap: 1,
    colorbar: { title: { text: 'p-value', side: 'right', font: { size: 11 } }, tickfont: { size: 10 }, thickness: 12 }, hovertemplate: 'MCS p = %{z:.3f}<extra></extra>' }],
    layout({ title: ttl(`MCS p-values (FZ0 loss); * p ≥ ${a.toFixed(2)}: retained in the ${Math.round(100 * (1 - a))}% MCS`), annotations: ann, shapes, margin: { l: 80, r: 10, t: 34, b: 40 },
      xaxis: AX('', { tickvals: [0, 1, 2, 3], ticktext: ASSETS.map(n => LAB[n]), showgrid: false, zeroline: false, ticks: '' }), yaxis: AX('', { tickvals: MODELS.map((_, i) => i), ticktext: MODELS, autorange: 'reversed', showgrid: false, zeroline: false, ticks: '' }) }));
  out('mc-out', ['sp500', 'bet'].map(n => T.mc(LAB[n], Math.round(100 * (1 - a)), MODELS.filter(m => D.mcs[n][m] >= a).join(', '))));
}

// ================================================================= conformal VaR, COVID-19
const CONF_DATES = calendar(D.conf.cal);
function conformalPath(a, gamma) {                                     // split conformal and ACI, as mfm_data.conformal_var
  const C = D.conf, s = C.s, sd = C.sd, n = 250, N = s.length, w0 = CONF_DATES.indexOf(C.w0);
  const vs = [], va = [], al = []; let at = a;
  const k = Math.ceil((n + 1) * (1 - a));
  for (let t = C.i0; t < N; t++) {
    const cal = s.slice(t - n, t).sort((x, y) => x - y);
    const ka = Math.ceil((n + 1) * (1 - at));
    const vS = k > n ? Infinity : sd[t] * cal[k - 1], vA = ka > n ? Infinity : sd[t] * cal[Math.max(ka, 1) - 1];
    if (t >= w0) { vs.push(vS); va.push(vA); al.push(at); }
    const err = s[t] * sd[t] > vA ? 1 : 0;
    at = at + gamma * (a - err);
  }
  return { vs, va, al, dt: CONF_DATES.slice(w0), L: s.slice(w0).map((v, i) => v * sd[w0 + i]) };
}
function conformal() {
  const g = +$('cp-g').value, lev = $('cp-a').value, a = LEVELS[lev];
  $('cp-g-v').textContent = nf(g, 3);
  const P = conformalPath(a, g), G = D.conf.garch[lev].map(v => v / 100), fin = v => (isFinite(v) ? v : null);
  const tr = [
    { x: P.dt, y: P.L, type: 'bar', name: 'Daily loss', marker: { color: K.orange }, opacity: 0.55, xaxis: 'x', yaxis: 'y', hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: P.dt, y: P.vs.map(fin), mode: 'lines', name: `Split conformal VaR ${levC(a)}%`, line: { color: K.blue, width: 1.4 }, xaxis: 'x', yaxis: 'y', hovertemplate: 'split %{x}: %{y:.2f}%<extra></extra>' },
    { x: P.dt, y: P.va.map(fin), mode: 'lines', name: `ACI VaR ${levC(a)}% (gaps: infinite)`, line: { color: K.red, width: 1.4 }, connectgaps: false, xaxis: 'x', yaxis: 'y', hovertemplate: 'ACI %{x}: %{y:.2f}%<extra></extra>' },
    { x: P.dt, y: G, mode: 'lines', name: `GARCH-t VaR ${levC(a)}%`, line: { color: K.green, width: 1.2, dash: 'dash' }, xaxis: 'x', yaxis: 'y', hovertemplate: 'GARCH-t %{x}: %{y:.2f}%<extra></extra>' },
    { x: P.dt, y: P.al.map(v => 100 * v), mode: 'lines', name: 'ACI level α_t', line: { color: K.red, width: 1.4 }, xaxis: 'x2', yaxis: 'y2', hovertemplate: 'α_t %{x}: %{y:.3f}%<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: `Target α = ${levC(a)}%`, line: { color: K.navy, dash: 'dash', width: 1.2 }, xaxis: 'x2', yaxis: 'y2', hoverinfo: 'skip' }
  ];
  const lim = Math.max(...P.L, ...P.vs.filter(isFinite), ...P.va.filter(isFinite), ...G) * 1.05;
  plot('cp-chart', tr, layout({ margin: { l: 56, r: 12, t: 16, b: 40 }, bargap: 0,
    shapes: [{ type: 'line', xref: 'paper', yref: 'y2', x0: 0, x1: 1, y0: 100 * a, y1: 100 * a, line: { color: K.navy, width: 1.2, dash: 'dash' } }],
    xaxis: AX('', { type: 'date', anchor: 'y', domain: [0, 1], showticklabels: false, matches: 'x2' }), yaxis: AX('Loss (%)', { domain: [0.36, 1], range: [Math.min(...P.L) * 1.05, lim] }),
    xaxis2: AX('', { type: 'date', anchor: 'y2', domain: [0, 1] }), yaxis2: AX('α_t (%)', { domain: [0, 0.28], rangemode: 'tozero' }), legend: legendBelow(-0.12) }));
  const c0 = P.dt.indexOf('2020-02-20'), c1 = P.dt.indexOf('2020-04-30'), nC = c1 - c0 + 1; let hs = 0, ha = 0, inf = 0;
  for (let i = c0; i <= c1; i++) { if (P.L[i] > P.vs[i]) hs++; if (P.L[i] > P.va[i]) ha++; if (!isFinite(P.va[i])) inf++; }
  const infAll = P.va.filter(v => !isFinite(v)).length;
  out('cp-out', [T.cp(levR(a), nC, nf(nC * a, 1), hs, ha, inf), T.cp2(nf(g, 3), nf(100 * Math.min(...P.al), 2), infAll, ni(P.dt.length))]);
}

// ================================================================= conformal coverage in calm and crisis periods
function conformalRegimes() {
  const q = (+$('cr-q').value).toFixed(2); $('cr-q-v').textContent = Math.round(100 * q);
  const rates = {}, res = [];
  ASSETS.forEach(n => {
    const N = NT(n), cr = new Uint8Array(N); for (const [a, b] of D.reg[n].crisis[q]) for (let t = a; t <= b; t++) cr[t] = 1;
    const nc = cr.reduce((s, v) => s + v, 0), rate = pos => { if (!pos) return [null, null]; let c0 = 0, c1 = 0; for (const t of pos) (cr[t] ? c1++ : c0++); return [100 * c0 / (N - nc), 100 * c1 / nc]; };
    const gAvail = D.first[n] === 0;
    rates[n] = { split: rate(D.reg[n].split), aci: rate(D.reg[n].aci), garch: gAvail ? rate(hitsOf(n, 'GARCH-t', 'VaR5')) : [null, null], nc, gAvail };
    res.push(T.cr(LAB[n], ni(nc), nf(rates[n].split[1], 2), nf(rates[n].aci[1], 2), gAvail ? nf(rates[n].garch[1], 2) : T.withheld));
  });
  const S = [['split', K.blue, 'Split conformal'], ['aci', K.red, 'ACI'], ['garch', K.green, 'GARCH-t']], tr = [];
  S.forEach(([k, c, l], j) => [0, 1].forEach(r => tr.push({ x: ASSETS.map((_, i) => i + j * 0.27 - 0.27 + r * 0.12), y: ASSETS.map(n => rates[n][k][r]), type: 'bar', width: 0.12, name: l + (r ? ', crisis' : ', calm'),
    marker: { color: r ? c : rgba(c, 0.45) }, hovertemplate: l + (r ? ', crisis' : ', calm') + ': %{y:.2f}%<extra></extra>' })));
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Nominal 5%', line: { color: K.navy, dash: 'dash', width: 1.2 }, hoverinfo: 'skip' });
  plot('cr-chart', tr, layout({ shapes: [hline(5, K.navy, 'dash')], annotations: ASSETS.filter(n => !rates[n].gAvail).map(n => ({ x: ASSETS.indexOf(n) + 0.33, y: 0, yanchor: 'bottom', text: 'GARCH withheld', textangle: -90, showarrow: false, font: { size: 10, color: K.navy } })),
    xaxis: AX('', { tickvals: [0.06, 1.06, 2.06, 3.06], ticktext: ASSETS.map(n => LAB[n]), range: [-0.5, 3.6] }), yaxis: AX('Breach rate of VaR 5% (%)', { rangemode: 'tozero' }), legend: legendBelow(-0.12) }));
  out('cr-out', [T.cr0(Math.round(100 * q)), ...res]);
}

// ================================================================= case study: Table 3 of Bayer and Dimitriadis (2022)
function bdTable() {
  const B = D.bd, k = +$('bd-r').value, ref = B.refits[k], x = B.windows.map(String);
  $('bd-r-v').textContent = ref;
  const tr = [], lay = layout({ margin: { l: 56, r: 12, t: 26, b: 40 }, legend: legendBelow(-0.2), annotations: [], shapes: [] });
  ['GARCH', 'GJR-GARCH'].forEach((fam, p) => {
    const ax = p ? '2' : '', x0 = p ? 0.53 : 0;
    [['N', K.red, 'Normal'], ['t', K.blue, 'Student-t']].forEach(([d, c, l]) => {
      const tab = B.table[`${fam}-${d}`];
      tr.push({ x, y: tab.map(r => r[0]), mode: 'lines+markers', name: `${l} innovations, weekly refit (5 days)`, legendgroup: d + 'w', showlegend: !p, line: { color: c, width: 1.6 }, marker: { size: 6 }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: fam + ', window %{x}: %{y:.2f}<extra></extra>' });
      tr.push({ x, y: tab.map(r => r[k]), mode: 'lines+markers', name: `${l} innovations, refit every ${ref} days`, legendgroup: d + 'r', showlegend: !p, line: { color: c, width: 1.6, dash: 'dash' }, marker: { size: 6, symbol: 'square' }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: fam + ', window %{x}: %{y:.2f}<extra></extra>' });
    });
    lay['xaxis' + ax] = AX('Rolling estimation window (days)', { type: 'category', anchor: 'y' + ax, domain: [x0, x0 + 0.47] });
    lay['yaxis' + ax] = AX(p ? '' : 'Share of stocks rejected', { anchor: 'x' + ax, range: [-0.03, 1.05] });
    lay.annotations.push({ text: fam + '(1,1)', x: x0 + 0.235, xref: 'paper', y: 1.0, yref: 'paper', yanchor: 'bottom', showarrow: false, font: { size: 12, color: K.navy } });
    lay.shapes.push({ type: 'line', xref: (p ? 'x2' : 'x') + ' domain', yref: 'y' + ax, x0: 0, x1: 1, y0: 0.05, y1: 0.05, line: { color: K.navy, width: 1.2, dash: 'dot' } });
  });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Nominal size 5%', line: { color: K.navy, dash: 'dot', width: 1.2 }, hoverinfo: 'skip' });
  plot('bd-chart', tr, lay);
  const col = key => B.table[key].map(r => r[k]);
  const mm = a => [nf(Math.min(...a), 2), nf(Math.max(...a), 2)];
  const n1 = mm([...col('GARCH-N'), ...col('GJR-GARCH-N')]), t1 = mm([...col('GARCH-t'), ...col('GJR-GARCH-t')]);
  out('bd-out', [T.bd(ref, n1[0], n1[1], t1[0], t1[1]), T.bd2(nf(B.table['GARCH-t'][0][k], 2), nf(Math.max(...B.table['GARCH-t'].slice(2).map(r => r[k]), ...B.table['GJR-GARCH-t'].slice(2).map(r => r[k])), 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  $('fa-chart').style.height = '560px'; $('cp-chart').style.height = '470px'; $('tl-chart').style.height = '300px'; $('br-chart').style.height = '400px';
  on(['fa-l', 'fa-y'], fourAssets); P('fa-play', 'fa-y', range(2007, 2026, 1), 700);
  on(['sv-y'], spVar); P('sv-play', 'sv-y', range(2007, 2026, 1), 900);
  on(['kp-a', 'kp-T'], kupiec); P('kp-play', 'kp-T', range(250, 5000, 250), 500);
  on(['pp-T'], pofPower); P('pp-play', 'pp-T', range(250, 5000, 250), 500);
  on(['br-l', 'br-y'], breachRates); P('br-play', 'br-y', range(2007, 2024, 1), 700);
  on(['tl-m', 'tl-s', 'tl-n'], timeline); P('tl-play', 'tl-s', range(2007, 2023, 1), 800);
  on(['vp-s'], varPvalues); P('vp-play', 'vp-s', range(0.01, 0.1, 0.005), 400);
  $('tf-a').addEventListener('input', () => { $('tf-t').max = NT($('tf-a').value) - 1; $('tf-t').value = $('tf-t').max; traffic(); });
  $('tf-t').max = NT('sp500') - 1; $('tf-t').value = NT('sp500') - 1; on(['tf-t'], traffic);
  const tfPlayer = P('tf-play', 'tf-t', range(249, NT('sp500') - 1, 20), 60);
  $('tf-a').addEventListener('input', () => { tfPlayer.values = range(249, NT($('tf-a').value) - 1, 20); });
  on(['mf-a', 'mf-y'], mfRes); P('mf-play', 'mf-y', range(2008, 2026, 1), 900);
  on(['z2-a', 'z2-n'], z2Roll); P('z2-play', 'z2-n', range(125, 1000, 25), 300);
  on(['ep-k', 'ep-s'], esPvalues); P('ep-play', 'ep-s', range(0.01, 0.1, 0.005), 400);
  on(['el-nu', 'el-a'], elicit); P('el-play', 'el-nu', range(2.5, 30, 0.5), 250);
  on(['fz-y'], fz0); P('fz-play', 'fz-y', range(2007, 2025, 1), 700);
  on(['dm-q', 'dm-y'], dmMatrix); P('dm-play', 'dm-q', range(0, 40, 1), 300);
  on(['mc-a'], mcsBlock); P('mc-play', 'mc-a', range(0.01, 0.3, 0.01), 250);
  on(['cp-g', 'cp-a'], conformal); P('cp-play', 'cp-g', range(0.001, 0.05, 0.001), 200);
  on(['cr-q'], conformalRegimes); P('cr-play', 'cr-q', range(0.75, 0.95, 0.05), 900);
  on(['bd-r'], bdTable); P('bd-play', 'bd-r', range(0, 4, 1), 1000);
  fourAssets(); spVar(); kupiec(); pofPower(); breachRates(); timeline(); varPvalues(); traffic(); mfRes(); z2Roll(); esPvalues(); elicit(); fz0(); dmMatrix(); mcsBlock(); conformal(); conformalRegimes(); bdTable();
}
window.CH8 = { kupiecLR, christoffersen, durationTest, acceptRange, exactPower, localPower, powerCurve, dmStat, rollCount, rollingZ2, fzMeans, conformalPath, mPlus, tppf, hitVec, DATES, mfBoot };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

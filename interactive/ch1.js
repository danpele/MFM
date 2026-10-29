// Chapter 1 interactive page: one block per chart slide, computed in the browser from ch1_data.js.
(function () {
'use strict';
const D = window.CH1_DATA;
const { C, sum, mean, sdev, median, rng, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH1_TEXT;
const A = D.assets, LBL = D.labels, COL = D.colors, PER = D.periods, N = a => T.lab[a];

// ---------------------------------------------------------------- colours of the chapter charts
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', teal: '#17A2B8', navy: '#1F2A44', band: '#C5D2E8' };

// ---------------------------------------------------------------- data: dates, log returns
const dstr = t => new Date(t * 864e5).toISOString().slice(0, 10);
const M = {};
A.forEach(a => {
  const c = D.mk[a].c, d = D.mk[a].t.map(dstr), r = [];
  for (let i = 1; i < c.length; i++) r.push(Math.log(c[i] / c[i - 1]));
  M[a] = { c, d, r, rd: d.slice(1) };
});

// ---------------------------------------------------------------- statistics (same definitions as numpy / scipy / pandas)
const sq = x => x * x;
function moments(x) {                     // biased skewness and excess kurtosis (scipy.stats defaults)
  const m = mean(x); let m2 = 0, m3 = 0, m4 = 0;
  for (const v of x) { const e = v - m, e2 = e * e; m2 += e2; m3 += e2 * e; m4 += e2 * e2; }
  const n = x.length; m2 /= n; m3 /= n; m4 /= n;
  return { skew: m3 / Math.pow(m2, 1.5), exk: m4 / (m2 * m2) - 3 };
}
function quantile(sorted, p) {            // numpy 'linear' rule
  const h = (sorted.length - 1) * p, lo = Math.floor(h), hi = Math.min(lo + 1, sorted.length - 1);
  return sorted[lo] + (h - lo) * (sorted[hi] - sorted[lo]);
}
const asc = x => Float64Array.from(x).sort();
function acf(x, K) {                      // statsmodels acf: demeaned, divided by the sum of squares
  const m = mean(x), e = x.map(v => v - m), s2 = sum(e.map(sq)), res = [];
  for (let k = 1; k <= K; k++) { let s = 0; for (let t = k; t < e.length; t++) s += e[t] * e[t - k]; res.push(s / s2); }
  return res;
}
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
function rollStd(x, n) {                  // pandas rolling(n).std(), ddof = 1; NaN until n values
  const o = new Array(x.length).fill(NaN); let s = 0, s2 = 0;
  for (let i = 0; i < x.length; i++) {
    s += x[i]; s2 += x[i] * x[i];
    if (i >= n) { s -= x[i - n]; s2 -= x[i - n] * x[i - n]; }
    if (i >= n - 1) o[i] = Math.sqrt(Math.max((s2 - s * s / n) / (n - 1), 0));
  }
  return o;
}
function rollMean(x, n) {                 // NaN when the window holds a missing value
  const o = new Array(x.length).fill(NaN);
  for (let i = n - 1; i < x.length; i++) { let s = 0, ok = true; for (let j = i - n + 1; j <= i; j++) { if (!Number.isFinite(x[j])) { ok = false; break; } s += x[j]; } if (ok) o[i] = s / n; }
  return o;
}

// ---------------------------------------------------------------- distributions
function lgamma(z) {
  const g = [676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61503916999185, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (z < 0.5) return Math.log(Math.PI / Math.abs(Math.sin(Math.PI * z))) - lgamma(1 - z);
  z -= 1; let x = 0.99999999999980993; for (let i = 0; i < 8; i++) x += g[i] / (z + i + 1);
  const t = z + 7.5; return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}
function betacf(a, b, x) {
  let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap; d = 1 / (Math.abs(d) < 1e-300 ? 1e-300 : d); let h = d;
  for (let m = 1; m <= 300; m++) {
    const m2 = 2 * m; let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d; d = 1 / (Math.abs(d) < 1e-300 ? 1e-300 : d); c = 1 + aa / c; if (Math.abs(c) < 1e-300) c = 1e-300; h *= d * c;
    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d; d = 1 / (Math.abs(d) < 1e-300 ? 1e-300 : d); c = 1 + aa / c; if (Math.abs(c) < 1e-300) c = 1e-300;
    const del = d * c; h *= del; if (Math.abs(del - 1) < 1e-14) break;
  }
  return h;
}
function betai(a, b, x) {
  if (x <= 0) return 0; if (x >= 1) return 1;
  const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
}
const tpdf = (x, nu) => Math.exp(lgamma((nu + 1) / 2) - lgamma(nu / 2) - 0.5 * Math.log(nu * Math.PI) - (nu + 1) / 2 * Math.log(1 + x * x / nu));
const tcdf = (x, nu) => { const ib = betai(nu / 2, 0.5, nu / (nu + x * x)); return x > 0 ? 1 - 0.5 * ib : 0.5 * ib; };
function tinv(p, nu) { let lo = -500, hi = 500; for (let i = 0; i < 90; i++) { const m = (lo + hi) / 2; if (tcdf(m, nu) < p) lo = m; else hi = m; } return (lo + hi) / 2; }
const npdf = x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
function erfc(x) { const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r; }
const ncdf = x => 0.5 * erfc(-x / Math.SQRT2);
function ninv(p) {                        // Acklam
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239],
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572],
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783],
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416], pl = 0.02425;
  if (p < pl) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
  if (p > 1 - pl) return -ninv(1 - p);
  const q = p - 0.5, r = q * q; return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}

// ---------------------------------------------------------------- helpers of the page
const listOut = items => items.join('; ');
const rect = (y0, y1, extra) => Object.assign({ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0, y1, fillcolor: K.band, opacity: 0.7, line: { width: 0 }, layer: 'below' }, extra || {});
const bandIid = n => rect(-1.96 / Math.sqrt(n), 1.96 / Math.sqrt(n));
const BOT = { legend: { orientation: 'h', x: 0, xanchor: 'left', y: -0.22, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } } };
const yearOf = s => +s.slice(0, 4);
const NICE = [0.0001, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 3.5, 4, 4.5, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 1e4, 2e4, 5e4, 1e5, 2e5];
function logTicks(lo, hi) {               // a few round values inside [lo, hi] for a log axis
  const dec = NICE.filter(v => v >= lo && v <= hi && Math.abs(Math.log10(v) - Math.round(Math.log10(v))) < 1e-9);
  if (dec.length >= 2) return dec;
  const all = NICE.filter(v => v >= lo && v <= hi); return all.length > 4 ? all.filter((_, i) => i % 2 === 0) : all;
}
function threeCols(id) {                  // three charts in one row on wide screens (the shared CSS gives two)
  const el = $(id).parentNode, mq = window.matchMedia('(min-width: 721px)'), f = () => { el.style.gridTemplateColumns = mq.matches ? '1fr 1fr 1fr' : ''; };
  f(); if (mq.addEventListener) mq.addEventListener('change', f);
}

// ================================================================= prices and returns
function pricesReturns() {
  const th = +$('pr-th').value / 100; $('pr-th-v').textContent = pct(th, 1);
  const tr = [], lay = layout({ showlegend: false, margin: { l: 70, r: 12, t: 30, b: 40 }, hovermode: 'closest' }), n = A.length, gap = 0.035;
  lay.xaxis = AX('', { domain: [0, 0.46], type: 'date', anchor: 'y' + (2 * n - 1) });
  lay.xaxis2 = AX('', { domain: [0.54, 1], type: 'date', anchor: 'y' + (2 * n) });
  const shares = [];
  A.forEach((a, i) => {
    const m = M[a], top = 1 - i / n, bot = 1 - (i + 1) / n + gap, yp = 2 * i + 1, yr = 2 * i + 2;
    lay['yaxis' + (yp === 1 ? '' : yp)] = AX('', { domain: [bot, top], type: 'log', anchor: 'x', tickvals: logTicks(Math.min(...m.c), Math.max(...m.c)), tickfont: { size: 10, color: K.navy } });
    lay['yaxis' + yr] = AX('', { domain: [bot, top], anchor: 'x2', tickfont: { size: 10, color: K.navy } });
    tr.push({ x: m.d, y: m.c, xaxis: 'x', yaxis: 'y' + (yp === 1 ? '' : yp), mode: 'lines', name: LBL[a], line: { color: COL[a], width: 1 }, hovertemplate: LBL[a] + ' %{x}: %{y:.4g}<extra></extra>' });
    tr.push({ x: m.rd, y: m.r.map(v => 100 * v), xaxis: 'x2', yaxis: 'y' + yr, mode: 'lines', name: LBL[a], line: { color: COL[a], width: 0.6 }, hovertemplate: LBL[a] + ' %{x}: %{y:.2f}%<extra></extra>' });
    const ex = m.r.map((v, k) => (Math.abs(v) > th ? k : -1)).filter(k => k >= 0);
    tr.push({ x: ex.map(k => m.rd[k]), y: ex.map(k => 100 * m.r[k]), xaxis: 'x2', yaxis: 'y' + yr, mode: 'markers', name: '|r<sub>t</sub>| > threshold', marker: { color: K.navy, size: 3 }, hovertemplate: LBL[a] + ' %{x}: %{y:.2f}%<extra></extra>' });
    shares.push(`${N(a)} ${pct(ex.length / m.r.length, 1)}`);
    lay.annotations = (lay.annotations || []).concat([{ xref: 'paper', yref: 'paper', x: 0.455, y: bot, xanchor: 'right', yanchor: 'bottom', text: LBL[a], showarrow: false, font: { size: 11, color: COL[a] } }]);
  });
  lay.annotations.push({ xref: 'paper', yref: 'paper', x: 0, y: 1.06, xanchor: 'left', text: 'Price (log scale)', showarrow: false, font: { size: 12, color: K.navy } },
    { xref: 'paper', yref: 'paper', x: 0.54, y: 1.06, xanchor: 'left', text: 'Daily log return (%); dots: |r<sub>t</sub>| above the threshold', showarrow: false, font: { size: 12, color: K.navy } });
  plot('pr-chart', tr, lay);
  const b = M.btc, kmin = b.r.indexOf(Math.min(...b.r));
  out('pr-out', [T.pr(pct(th, 1), listOut(shares)), T.pr2(b.rd[kmin], pct(b.r[kmin], 1), pct(1 - Math.exp(b.r[kmin]), 1))]);
}

// ================================================================= histograms and QQ plots
const hqCache = {};
function hqData(a) {
  if (hqCache[a]) return hqCache[a];
  const r = M[a].r, m = mean(r), s = sdev(r), z = r.map(v => (v - m) / s), zs = asc(z), n = z.length;
  const osm = new Array(n);
  for (let i = 0; i < n; i++) { const p = i === 0 ? 1 - Math.pow(0.5, 1 / n) : i === n - 1 ? Math.pow(0.5, 1 / n) : (i + 1 - 0.3175) / (n + 0.365); osm[i] = ninv(p); }
  return (hqCache[a] = { z, zs: Array.from(zs), osm, exk: moments(r).exk, out4: z.filter(v => Math.abs(v) > 4).length / n });
}
function histQQ() {
  const a = $('hq-a').value, H = hqData(a), F = D.tfit[a], nu = +$('hq-nu').value; $('hq-nu-v').textContent = nf(nu, 1);
  const x = range(-8, 8, 0.02), tp = v => tpdf((v - F.loc) / F.scale, nu) / F.scale;
  plot('hq-h', [
    { x: H.z, type: 'histogram', histnorm: 'probability density', xbins: { start: -8, end: 8, size: 0.08 }, name: 'Standardised returns', marker: { color: COL[a], opacity: 0.55 }, hovertemplate: 'z %{x}<br>density %{y:.3f}<extra></extra>' },
    { x, y: x.map(npdf), mode: 'lines', name: 'Normal distribution', line: { color: K.red, width: 1.6 }, hoverinfo: 'skip' },
    { x, y: x.map(tp), mode: 'lines', name: `Student-t (ν = ${nu.toFixed(1)})`, line: { color: K.green, width: 1.6 }, hoverinfo: 'skip' }
  ], layout(Object.assign({ bargap: 0, title: ttl(LBL[a] + ': standardised returns'), xaxis: AX('Standardised return z', { range: [-6, 6] }), yaxis: AX('Density') }, BOT)));
  const ps = range(0.0005, 0.9995, 0.0025).concat([0.00005, 0.0001, 0.0002, 0.9998, 0.9999, 0.99995]).sort((p, q) => p - q);
  const lim = [Math.min(H.osm[0], H.zs[0]), Math.max(H.osm[H.osm.length - 1], H.zs[H.zs.length - 1])];
  plot('hq-q', [
    { x: H.osm, y: H.zs, mode: 'markers', name: 'Empirical quantiles', marker: { color: COL[a], size: 3, opacity: 0.6 }, hovertemplate: 'Normal %{x:.2f}<br>empirical %{y:.2f}<extra></extra>' },
    { x: lim, y: lim, mode: 'lines', name: 'y = x (Normal distribution)', line: { color: K.red, width: 1.2 }, hoverinfo: 'skip' },
    { x: ps.map(ninv), y: ps.map(p => F.loc + F.scale * tinv(p, nu)), mode: 'lines', name: `Student-t (ν = ${nu.toFixed(1)}) quantiles`, line: { color: K.green, width: 1.6 }, hoverinfo: 'skip' }
  ], layout(Object.assign({ title: ttl('QQ plot against the Normal distribution'), xaxis: AX('Normal-distribution quantiles'), yaxis: AX('Empirical quantiles', { range: [Math.max(lim[0], -15) - 0.5, Math.min(lim[1], 15) + 0.5] }) }, BOT)));
  const tt = tcdf((-4 - F.loc) / F.scale, nu) + 1 - tcdf((4 - F.loc) / F.scale, nu);
  out('hq-out', [T.hq(N(a), nf(H.exk, 1), pct(H.out4, 2), pct(2 * ncdf(-4), 3), nf(nu, 1), pct(tt, 2), nf(F.nu, 1))]);
}

// ================================================================= Hill plots
const HILL_FRACS = range(0, 38, 1).map(i => +(0.005 + 0.0025 * i).toFixed(4));
const hillCache = {};
function hillCum(a) {                     // cumulative sums of ln X_(i), X = |r| sorted in decreasing order
  if (hillCache[a]) return hillCache[a];
  const x = Array.from(asc(M[a].r.map(Math.abs).filter(v => v > 0))).reverse(), lx = x.map(Math.log), cs = [0];
  lx.forEach(v => cs.push(cs[cs.length - 1] + v));
  return (hillCache[a] = { lx, cs, n: M[a].r.length });
}
const hillK = (H, k) => 1 / (H.cs[k] / k - H.lx[k]);
function hill() {
  const f = +$('hl-f').value / 100; $('hl-f-v').textContent = pct(f, 2);
  const est = A.map(a => { const H = hillCum(a), k = Math.floor(f * H.n), al = hillK(H, Math.max(k, 5)); return { a, k, al, se: al / Math.sqrt(k) }; });
  plot('hl-plot', A.map(a => { const H = hillCum(a); return { x: HILL_FRACS.map(v => 100 * v), y: HILL_FRACS.map(v => hillK(H, Math.max(Math.floor(v * H.n), 5))), mode: 'lines', name: LBL[a], line: { color: COL[a], width: 1.6 }, hovertemplate: LBL[a] + ': k/n %{x:.2f}%, α̂ %{y:.2f}<extra></extra>' }; }),
    layout(Object.assign({ title: ttl('Hill plots of |r<sub>t</sub>|'), shapes: [rect(2, 4, { opacity: 0.5 }), hline(4, K.navy, 'dash'), hline(2, K.navy, 'dot'), vline(100 * f, K.navy, 'dot')],
      annotations: [{ xref: 'paper', x: 1, y: 4, yanchor: 'bottom', xanchor: 'right', text: 'α = 4: kurtosis exists above', showarrow: false, font: { size: 10 } }, { xref: 'paper', x: 0, y: 2, yanchor: 'top', xanchor: 'left', text: 'α = 2: variance exists above', showarrow: false, font: { size: 10 } }],
      xaxis: AX('Tail fraction k/n used by the estimator (%)'), yaxis: AX('Hill estimate α̂', { range: [1, 6] }) }, BOT)));
  plot('hl-ci', [{ x: est.map(e => LBL[e.a]), y: est.map(e => e.al), mode: 'markers', type: 'scatter', name: 'α̂ with 95% CI (i.i.d.)',
    error_y: { type: 'data', array: est.map(e => 1.96 * e.se), color: K.navy, thickness: 1.5, width: 6 }, marker: { color: est.map(e => COL[e.a]), size: 11 },
    hovertemplate: '%{x}: α̂ %{y:.2f} ± %{error_y.array:.2f}<extra></extra>' }],
    layout(Object.assign({ title: ttl('α̂ at k/n = ' + (100 * f).toFixed(2) + '%, 95% CI α̂(1 ± 1.96/√k)'), shapes: [hline(4, K.navy, 'dash'), hline(2, K.navy, 'dot')], xaxis: AX(''), yaxis: AX('Hill estimate α̂', { range: [1, 6.5] }) }, BOT)));
  const n4 = est.filter(e => e.al - 1.96 * e.se > 4 || e.al + 1.96 * e.se < 4).length;
  out('hl-out', [T.hl(pct(f, 2), listOut(est.map(e => `${N(e.a)} ${nf(e.al, 2)} (k = ${e.k})`)), n4)]);
}

// ================================================================= gain/loss asymmetry
function gainLoss() {
  const a = $('gl-a').value, p = +$('gl-p').value / 100; $('gl-p-v').textContent = pct(p, 1);
  const r = M[a].r, n = r.length, surv = s => { const x = Array.from(asc(s)).reverse(); return { x: x.map(v => 100 * v), y: x.map((_, i) => (i + 1) / n) }; };
  const L = surv(r.filter(v => v < 0).map(v => -v)), G = surv(r.filter(v => v > 0));
  const q = A.map(b => { const s = asc(M[b].r); return { b, lo: -100 * quantile(s, p), hi: 100 * quantile(s, 1 - p) }; }), me = q[A.indexOf(a)];
  const med = 100 * median(r.map(Math.abs)), xr = a === 'sp500' ? [Math.log10(0.5), Math.log10(15)] : [Math.log10(med), Math.log10(1.3 * Math.max(L.x[0], G.x[0]))];
  plot('gl-s', [
    { x: L.x, y: L.y, mode: 'lines', name: 'Losses −r<sub>t</sub>', line: { color: K.red, width: 1.6 }, hovertemplate: 'loss > %{x:.2f}%: %{y:.4f}<extra></extra>' },
    { x: G.x, y: G.y, mode: 'lines', name: 'Gains r<sub>t</sub>', line: { color: K.green, width: 1.6 }, hovertemplate: 'gain > %{x:.2f}%: %{y:.4f}<extra></extra>' }
  ], layout(Object.assign({ title: ttl(LBL[a] + ': survival functions P(X > x)'), shapes: [vline(me.lo, K.red, 'dash'), vline(me.hi, K.green, 'dot')],
    xaxis: AX('Daily move x (%, log scale)', { type: 'log', range: xr, tickvals: [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50] }), yaxis: AX('P(X > x) (log scale)', { type: 'log', dtick: 1, exponentformat: 'power' }) }, BOT)));
  plot('gl-q', [
    { x: q.map(e => LBL[e.b]), y: q.map(e => e.lo), type: 'bar', name: `−q(${+p.toFixed(3)}), loss`, marker: { color: K.red, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: q.map(e => LBL[e.b]), y: q.map(e => e.hi), type: 'bar', name: `q(${+(1 - p).toFixed(3)}), gain`, marker: { color: K.green, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout(Object.assign({ barmode: 'group', bargap: 0.25, title: ttl(`Tails at ${(100 * p).toFixed(1)}% by market`), xaxis: AX(''), yaxis: AX('Daily move (%)') }, BOT)));
  const ci = Math.abs(p - 0.01) < 1e-9 ? D.res.gainloss_ci[a] : null;
  out('gl-out', [T.gl(N(a), pct(p, 1), nf(me.lo, 2), nf(me.hi, 2), nf(me.lo - me.hi, 2), ci ? [nf(ci[0], 2), nf(ci[1], 2)] : null),
    T.gl2(q.filter(e => e.lo > e.hi).length)]);
}

// ================================================================= ACF of r, |r|, r^2
const acCache = {};
function acfData(a, y0) {
  const key = a + y0; if (acCache[key]) return acCache[key];
  const m = M[a], i0 = Math.max(0, m.rd.findIndex(s => yearOf(s) >= y0)), r = m.r.slice(i0), mu = mean(r), x = r.map(v => v - mu), s2 = sum(x.map(sq)), Kl = 100;
  const rob = []; for (let k = 1; k <= Kl; k++) { let s = 0; for (let t = k; t < x.length; t++) s += x[t] * x[t] * x[t - k] * x[t - k]; rob.push(1.96 * Math.sqrt(s / (s2 * s2))); }
  return (acCache[key] = { n: r.length, start: m.rd[i0], r: acf(r, Kl), a: acf(r.map(Math.abs), Kl), s: acf(r.map(sq), Kl), rob });
}
function acfThree() {
  const a = $('ac-a').value, y0 = +$('ac-y').value, Q = acfData(a, y0), lags = range(1, 100, 1), b = 1.96 / Math.sqrt(Q.n);
  $('ac-y-v').textContent = Q.start.slice(0, 4);
  const one = (id, y, title, col, rob) => {
    const tr = [{ x: lags, y, type: 'bar', name: 'ACF', marker: { color: col }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
      { x: [null], y: [null], mode: 'lines', name: '95% band, i.i.d. ±1.96/√T', line: { color: K.band, width: 8 } }];
    if (rob) tr.push({ x: lags, y: Q.rob, mode: 'lines', line: { shape: 'hvh', color: K.navy, width: 1 }, name: '95% band, robust ±1.96√τ<sub>k</sub>', hoverinfo: 'skip' },
      { x: lags, y: Q.rob.map(v => -v), mode: 'lines', line: { shape: 'hvh', color: K.navy, width: 1 }, showlegend: false, hoverinfo: 'skip' });
    plot(id, tr, layout(Object.assign({ title: ttl(title), bargap: 0.2, shapes: [rect(-b, b)], xaxis: AX('Lag (days)'), yaxis: AX('Autocorrelation', { range: [-0.15, 0.4] }) }, { legend: Object.assign({}, BOT.legend, { y: -0.25 }) })));
  };
  one('ac-r', Q.r, 'Returns r<sub>t</sub>', K.blue, true); one('ac-b', Q.a, 'Absolute returns |r<sub>t</sub>|', K.amber); one('ac-s', Q.s, 'Squared returns r<sub>t</sub><sup>2</sup>', K.red);
  const oi = Q.r.filter(v => Math.abs(v) > b).length, orb = Q.r.filter((v, i) => Math.abs(v) > Q.rob[i]).length;
  out('ac-out', [T.ac(N(a), Q.start, nf(Q.r[0], 2), oi, orb), T.ac2(nf(Q.a[0], 2), Q.a.filter(v => v > 0).length, Q.s.filter(v => v > 0).length)]);
}

// ================================================================= rolling volatility
function rollingVol() {
  const n = +$('rv-n').value; $('rv-n-v').textContent = n;
  const tr = [], hi = [], eur = [];
  A.forEach(a => {
    const m = M[a], v = rollStd(m.r, n).map(x => 100 * x * Math.sqrt(PER[a]));
    tr.push({ x: m.rd, y: v, mode: 'lines', name: LBL[a], line: { color: COL[a], width: 1 }, hovertemplate: LBL[a] + ' %{x}: %{y:.1f}%<extra></extra>' });
    let k = n - 1; v.forEach((x, i) => { if (x > v[k]) k = i; }); hi.push(`${N(a)} ${nf(v[k], 0)}% (${m.rd[k]})`);
    if (a === 'eurron') { const pre = v.filter((x, i) => Number.isFinite(x) && m.rd[i] < '2013-07-01'), post = v.filter((x, i) => Number.isFinite(x) && m.rd[i] >= '2013-07-01'); eur.push(mean(pre), mean(post)); }
  });
  plot('rv-chart', tr, layout(Object.assign({ title: ttl(n + '-day rolling volatility, annualised'), xaxis: AX('', { type: 'date' }),
    yaxis: AX(n + '-day volatility (%, ann., log)', { type: 'log', tickvals: [0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200] }) }, BOT)));
  out('rv-out', [T.rv(n, listOut(hi)), T.rv2(nf(eur[0], 1), nf(eur[1], 1))]);
}

// ================================================================= aggregational Gaussianity
const HZ = [1, 2, 5, 10, 20, 40, 60, 120, 250];
const agCache = {};
function aggSums(a, h) {
  const key = a + ':' + h; if (agCache[key]) return agCache[key];
  const r = M[a].r, nb = Math.floor(r.length / h), s = [];
  for (let b = 0; b < nb; b++) { let x = 0; for (let j = 0; j < h; j++) x += r[b * h + j]; s.push(x); }
  return (agCache[key] = { s, exk: moments(s).exk, n: nb });
}
function aggregation() {
  const h = HZ[+$('ag-h').value], a = $('ag-a').value; $('ag-h-v').textContent = h;
  plot('ag-k', A.map(b => ({ x: HZ, y: HZ.map(v => aggSums(b, v).exk), mode: 'lines+markers', name: LBL[b], line: { color: COL[b], width: 1.6 }, marker: { size: 6 }, hovertemplate: LBL[b] + ', h = %{x}: %{y:.2f}<extra></extra>' })),
    layout(Object.assign({ title: ttl('Excess kurtosis of non-overlapping h-day returns'), shapes: [hline(0, K.navy, 'dash'), vline(h, K.navy, 'dot')],
      annotations: [{ xref: 'paper', x: 0.01, y: 0, yanchor: 'bottom', xanchor: 'left', text: 'Normal distribution', showarrow: false, font: { size: 10 } }],
      xaxis: AX('Aggregation horizon h (trading days, log scale)', { type: 'log', tickvals: HZ }), yaxis: AX('Excess kurtosis') }, BOT)));
  const S = aggSums(a, h), mu = mean(S.s), sd = sdev(S.s), z = S.s.map(v => (v - mu) / sd), x = range(-6, 6, 0.05);
  plot('ag-hist', [
    { x: z, type: 'histogram', histnorm: 'probability density', xbins: { start: -8, end: 8, size: h >= 60 ? 0.4 : h >= 10 ? 0.25 : 0.1 }, name: `${LBL[a]}, ${h}-day returns`, marker: { color: COL[a], opacity: 0.6 }, hovertemplate: 'z %{x}<br>density %{y:.3f}<extra></extra>' },
    { x, y: x.map(npdf), mode: 'lines', name: 'Normal distribution', line: { color: K.red, width: 1.6 }, hoverinfo: 'skip' }
  ], layout(Object.assign({ bargap: 0, title: ttl(`${LBL[a]}: standardised ${h}-day returns, n<sub>h</sub> = ${S.n}`), xaxis: AX('Standardised return', { range: [-6, 6] }), yaxis: AX('Density') }, BOT)));
  const zz = b => { const Q = aggSums(b, h); return Q.exk / Math.sqrt(24 / Q.n); };
  out('ag-out', [T.ag(N(a), h, nf(S.exk, 1), S.n, nf(zz(a), 1)), T.ag2(h, A.filter(b => Math.abs(zz(b)) > 1.96).map(b => N(b)).join(', ') || '—')]);
}

// ================================================================= leverage effect
function corrPairs(x, y) {                // pandas Series.corr on the overlapping (non-missing) pairs
  const xs = [], ys = []; for (let i = 0; i < x.length; i++) if (Number.isFinite(x[i]) && Number.isFinite(y[i])) { xs.push(x[i]); ys.push(y[i]); }
  return pearson(xs, ys);
}
const shiftBack = (x, k) => x.map((_, t) => (t + k >= 0 && t + k < x.length ? x[t + k] : NaN));     // x_{t+k}
const lvCache = {};
function levData(a) {
  if (lvCache[a]) return lvCache[a];
  const r = M[a].r, ab = r.map(Math.abs), mr = mean(r), ma = mean(ab), xc = r.map(v => v - mr), yc = ab.map(v => v - ma), ks = range(-20, 20, 1);
  const L = ks.map(k => corrPairs(r, shiftBack(ab, k)));
  const rob = ks.map(k => { let sxy = 0, sx = 0, sy = 0; for (let t = 0; t < r.length; t++) { const u = t + k; if (u < 0 || u >= r.length) continue; sxy += xc[t] * xc[t] * yc[u] * yc[u]; sx += xc[t] * xc[t]; sy += yc[u] * yc[u]; } return Math.sqrt(sxy / (sx * sy)); });
  return (lvCache[a] = { ks, L, rob, n: r.length });
}
function leverage() {
  const a = $('lv-a').value, k = +$('lv-k').value, Q = levData(a), r = M[a].r; $('lv-k-v').textContent = k;
  const b = 1.96 / Math.sqrt(Q.n), j = Q.ks.indexOf(k);
  plot('lv-bar', [
    { x: Q.ks, y: Q.L, type: 'bar', name: 'corr(r<sub>t</sub>, |r<sub>t+k</sub>|)', marker: { color: Q.L.map((v, i) => (v < 0 ? K.red : K.green)), line: { color: Q.ks.map(v => (v === k ? K.navy : 'rgba(0,0,0,0)')), width: 2 } }, hovertemplate: 'k = %{x}: %{y:.3f}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: '95% band, i.i.d. ±1.96/√T', line: { color: K.band, width: 8 } },
    { x: Q.ks, y: Q.rob.map(v => 1.96 * v), mode: 'lines', line: { shape: 'hvh', color: K.navy, width: 1 }, name: '95% band, robust', hoverinfo: 'skip' },
    { x: Q.ks, y: Q.rob.map(v => -1.96 * v), mode: 'lines', line: { shape: 'hvh', color: K.navy, width: 1 }, showlegend: false, hoverinfo: 'skip' }
  ], layout(Object.assign({ title: ttl(LBL[a] + ': corr(r<sub>t</sub>, |r<sub>t+k</sub>|)'), bargap: 0.2, shapes: [rect(-b, b)], xaxis: AX('Lag k (days)'), yaxis: AX('Correlation') }, BOT)));
  const idx = range(0, r.length - 1 - k, 1).sort((s, t) => r[s] - r[t]), G = 20, gx = [], gy = [];
  for (let g = 0; g < G; g++) { const part = idx.slice(Math.floor(g * idx.length / G), Math.floor((g + 1) * idx.length / G)); gx.push(100 * mean(part.map(t => r[t]))); gy.push(100 * mean(part.map(t => Math.abs(r[t + k])))); }
  plot('lv-bin', [{ x: gx, y: gy, mode: 'lines+markers', name: `Mean |r<sub>t+${k}</sub>| in each 5% group of r<sub>t</sub>`, line: { color: COL[a], width: 1.6 }, marker: { size: 7 }, hovertemplate: 'mean r_t %{x:.2f}%<br>mean |r_{t+k}| %{y:.2f}%<extra></extra>' }],
    layout(Object.assign({ title: ttl(`Size of the return ${k} day${k > 1 ? 's' : ''} later, by today's return`), xaxis: AX('Return on day t (%, mean of the group)'), yaxis: AX(`Mean |r<sub>t+${k}</sub>| (%)`, { rangemode: 'tozero' }) }, BOT)));
  out('lv-out', [T.lv(N(a), k, nf(Q.L[j], 2), nf(Q.L[j] / Q.rob[j], 1)), T.lv2(k, nf(gy[0], 2), nf(gy[G - 1], 2))]);
}

// ================================================================= volume and volatility
function volumeVol() {
  const a = $('vv-a').value, w = +$('vv-w').value; $('vv-w-v').textContent = w;
  const V = D.vol[a], lv = V.map(v => (v === null ? NaN : Math.log(v))), rm = rollMean(lv, w), m = M[a], xs = [], ys = [];
  for (let t = 1; t < m.c.length; t++) { const v = lv[t] - rm[t], ab = Math.abs(m.r[t - 1]); if (Number.isFinite(v) && ab > 0) { xs.push(v); ys.push(ab); } }
  const rho = spearman(xs, ys);
  plot('vv-chart', [{ x: xs, y: ys.map(v => 100 * v), mode: 'markers', name: 'One day', marker: { color: COL[a], size: 3, opacity: 0.3 }, hovertemplate: 'volume %{x:.2f}<br>|r| %{y:.2f}%<extra></extra>' }],
    layout(Object.assign({ showlegend: false, title: ttl(`${LBL[a]}: Spearman ρ = ${rho.toFixed(2)}, ${xs.length} days`), xaxis: AX(`Abnormal log volume (vs ${w}-day mean)`), yaxis: AX('|r<sub>t</sub>| (%, log scale)', { type: 'log', tickvals: [0.001, 0.01, 0.1, 1, 10], ticktext: ['0.001', '0.01', '0.1', '1', '10'] }) }, BOT)));
  const ci = w === 250 ? D.res.vol_ci[a] : null;
  out('vv-out', [T.vv(N(a), w, nf(rho, 2), xs.length, ci ? [nf(ci[0], 2), nf(ci[1], 2)] : null)]);
}

// ================================================================= ACF of |r| across markets
const aaCache = {};
const KS = [...new Set(range(0, 20, 1).map(i => Math.round(10 * Math.pow(25, i / 20))))];   // lags 10-250, evenly spaced on the log scale
const acfAbsOf = a => aaCache[a] || (aaCache[a] = acf(M[a].r.map(Math.abs), 250));
function fitLine(x, y) { const mx = mean(x), my = mean(y); let sxy = 0, sxx = 0; x.forEach((v, i) => { sxy += (v - mx) * (y[i] - my); sxx += (v - mx) ** 2; }); const b = sxy / sxx; return [my - b * mx, b]; }
function acfAbs() {
  const a = $('aa-a').value, d = +$('aa-d').value, lags = range(1, 250, 1); $('aa-d-v').textContent = nf(d, 2);
  const ac = acfAbsOf(a), ok = KS.filter(k => ac[k - 1] > 0), ly = ok.map(k => Math.log(ac[k - 1])), lk = ok.map(Math.log);
  const c = Math.exp(mean(ly.map((v, i) => v - (2 * d - 1) * lk[i]))), s20 = range(1, 20, 1), [ea, eb] = fitLine(s20, s20.map(k => Math.log(ac[k - 1])));
  const hyp = k => c * Math.pow(k, 2 * d - 1), ex = k => Math.exp(ea + eb * k);
  const tr = A.map(b => ({ x: lags, y: acfAbsOf(b), mode: 'lines', name: LBL[b], line: { color: COL[b], width: b === a ? 2 : 1.1 }, hovertemplate: LBL[b] + ', lag %{x}: %{y:.3f}<extra></extra>' }));
  tr.push({ x: lags.slice(9), y: lags.slice(9).map(hyp), mode: 'lines', name: `Hyperbolic c·k<sup>2d−1</sup>, d = ${d.toFixed(2)}, fitted on lags 10–250`, line: { color: K.navy, width: 1.6, dash: 'dash' }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lags, y: lags.map(ex), mode: 'lines', name: 'Exponential c·φ<sup>k</sup>, fitted on lags 1–20', line: { color: K.navy, width: 1.6, dash: 'dot' }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' });
  plot('aa-chart', tr, layout(Object.assign({ title: ttl('ACF of |r<sub>t</sub>|, lags 1–250; reference curves fitted to ' + LBL[a]), shapes: [hline(0, K.navy)], xaxis: AX('Lag (days, log scale)', { type: 'log', tickvals: [1, 2, 5, 10, 20, 50, 100, 250] }), yaxis: AX('ACF of |r<sub>t</sub>|', { range: [-0.05, 0.5] }) }, BOT)));
  const [, sl] = fitLine(lk, ly);
  out('aa-out', [T.aa(N(a), nf(ac[0], 2), nf(ac[19], 2), nf(ac[99], 2)), T.aa2(nf(d, 2), nf(hyp(250), 3), nf(ex(250), 3), nf(ac[249], 3), nf((sl + 1) / 2, 2), nf(D.res.d_lw[a], 2))]);
}

// ================================================================= Taylor effect
const DELTAS = range(1, 12, 1).map(i => 0.25 * i);
const tyCache = {};
function taylorData(a) {
  if (tyCache[a]) return tyCache[a];
  const ab = M[a].r.map(Math.abs);
  return (tyCache[a] = DELTAS.map(dl => acf(ab.map(v => Math.pow(v, dl)), 100)));
}
function taylor() {
  const a = $('ty-a').value, k = +$('ty-k').value, Q = taylorData(a); $('ty-k-v').textContent = k;
  const curve = lag => DELTAS.map((_, i) => Q[i][lag - 1]), am = lag => { const c = curve(lag); return DELTAS[c.indexOf(Math.max(...c))]; };
  const LC = { 1: K.blue, 5: K.amber, 20: K.red }, tr = [];
  [...new Set([1, 5, 20, k])].forEach(lag => {
    const c = curve(lag), col = LC[lag] || K.navy, mx = Math.max(...c);
    tr.push({ x: DELTAS, y: c, mode: 'lines+markers', name: 'lag ' + lag, line: { color: col, width: lag === k ? 2.6 : 1.4 }, marker: { size: 5 }, hovertemplate: `lag ${lag}, δ %{x}: %{y:.3f}<extra></extra>` },
      { x: [DELTAS[c.indexOf(mx)]], y: [mx], mode: 'markers', marker: { symbol: 'star', size: 14, color: col }, showlegend: false, hovertemplate: `lag ${lag}: maximum at δ = %{x}<extra></extra>` });
  });
  plot('ty-c', tr, layout(Object.assign({ title: ttl(LBL[a] + ': corr(|r<sub>t</sub>|<sup>δ</sup>, |r<sub>t−k</sub>|<sup>δ</sup>)'), shapes: [vline(1, K.navy, 'dot')], xaxis: AX('Power δ'), yaxis: AX('Autocorrelation') }, BOT)));
  const lags = range(1, 100, 1);
  plot('ty-m', [{ x: lags, y: lags.map(am), mode: 'lines+markers', name: 'δ with the highest autocorrelation', line: { color: COL[a], width: 1.4, shape: 'hv' }, marker: { size: 4 }, hovertemplate: 'lag %{x}: δ = %{y}<extra></extra>' }],
    layout(Object.assign({ title: ttl('Position of the maximum, by lag'), shapes: [hline(1, K.navy, 'dot'), vline(k, K.navy, 'dot')], xaxis: AX('Lag k (days, log scale)', { type: 'log', tickvals: [1, 2, 5, 10, 20, 50, 100] }), yaxis: AX('δ at the maximum', { range: [0, 3.1], dtick: 0.5 }) }, BOT)));
  const c = curve(k);
  out('ty-out', [T.ty(N(a), k, nf(am(k), 2), nf(Math.max(...c), 3), nf(c[3], 3), nf(c[7], 3))]);
}

// ================================================================= one simulated OHLC day
let ohSeed = 0, ohPath = D.ohlc_day;
function ohlcDay() {
  const x = ohPath, n = x.length, m = +$('oh-m').value; $('oh-m-v').textContent = m;
  const seg = x.slice(0, m + 1); let ih = 0, il = 0; seg.forEach((v, i) => { if (v > seg[ih]) ih = i; if (v < seg[il]) il = i; });
  const P = v => 100 * v;
  plot('oh-chart', [
    { x: [-60, -1], y: [0, 0], mode: 'lines', name: 'Previous close c<sub>t−1</sub> = 0', line: { color: K.purple, width: 2 }, hoverinfo: 'skip' },
    { x: range(0, m, 1), y: seg.map(P), mode: 'lines', name: 'Simulated intraday log price', line: { color: K.blue, width: 1.5 }, hovertemplate: 'minute %{x}: %{y:.2f}%<extra></extra>' },
    { x: [0], y: [P(x[0])], mode: 'markers+text', text: ['open o<sub>t</sub>'], textposition: 'top left', name: 'Open', marker: { color: K.orange, size: 9 }, showlegend: false, hovertemplate: 'open %{y:.2f}%<extra></extra>' },
    { x: [ih], y: [P(seg[ih])], mode: 'markers+text', text: ['high h<sub>t</sub>'], textposition: 'top center', name: 'High', marker: { color: K.green, size: 9 }, showlegend: false, hovertemplate: 'high %{y:.2f}%<extra></extra>' },
    { x: [il], y: [P(seg[il])], mode: 'markers+text', text: ['low l<sub>t</sub>'], textposition: 'bottom center', name: 'Low', marker: { color: K.red, size: 9 }, showlegend: false, hovertemplate: 'low %{y:.2f}%<extra></extra>' },
    { x: [m], y: [P(seg[m])], mode: 'markers+text', text: [m === n - 1 ? 'close c<sub>t</sub>' : 'now'], textposition: 'middle right', name: 'Close', marker: { color: K.blue, size: 9 }, showlegend: false, hovertemplate: '%{y:.2f}%<extra></extra>' }
  ], layout(Object.assign({ title: ttl('One simulated trading day: the four OHLC prices'), shapes: [hline(0, K.navy, 'dot'), { type: 'line', x0: 0, x1: 0, y0: 0, y1: P(x[0]), line: { color: K.orange, width: 2 } }],
    annotations: [{ x: -4, y: P(x[0]) / 2, xanchor: 'right', text: 'overnight gap', showarrow: false, font: { size: 10 } }],
    xaxis: AX('Minutes after the open (overnight shown to the left)', { range: [-65, n + 45] }), yaxis: AX('Log price relative to c<sub>t−1</sub> (%)', { range: [P(Math.min(0, ...x)) - 0.3, P(Math.max(0, ...x)) + 0.3] }) }, BOT)));
  const rg = seg[ih] - seg[il], pk = rg / Math.sqrt(4 * Math.log(2));
  out('oh-out', [T.oh(m, nf(P(x[0]), 2), nf(P(seg[ih]), 2), nf(P(seg[il]), 2), nf(P(seg[m]), 2)), T.oh2(nf(P(rg), 2), nf(P(pk), 2), nf(P(Math.abs(seg[m])), 2))]);
}
function newDay() {
  ohSeed++; const z = rng(1000 + ohSeed), n = 390, s = 0.012 / Math.sqrt(n), x = [0.006];
  for (let i = 1; i < n; i++) x.push(x[i - 1] + s * z());
  ohPath = x; ohlcDay();
}

// ================================================================= volatility estimators, S&P 500
const EST = ['Close-to-close', 'Parkinson', 'Garman-Klass', 'Rogers-Satchell', 'Yang-Zhang'], ECOL = [K.teal, K.blue, K.green, K.amber, K.red];
const veCache = {};
function estimators(n) {
  if (veCache[n]) return veCache[n];
  const { O, H, L, C: Cl } = D.ohlc, T0 = Cl.length, ln = Math.log, P = 252;
  const rm = x => { const o = new Array(T0).fill(NaN); let s = 0, c = 0; for (let i = 0; i < T0; i++) { s += x[i]; if (i >= n) s -= x[i - n]; if (i >= n - 1) o[i] = s / n; } return o; };
  const cc = new Array(T0).fill(0), on = new Array(T0).fill(0), oc = [], hl2 = [], co2 = [], rs = [];
  for (let i = 0; i < T0; i++) {
    if (i > 0) { cc[i] = ln(Cl[i] / Cl[i - 1]); on[i] = ln(O[i] / Cl[i - 1]); }
    oc.push(ln(Cl[i] / O[i])); hl2.push(ln(H[i] / L[i]) ** 2); co2.push(ln(Cl[i] / O[i]) ** 2);
    rs.push(ln(H[i] / O[i]) * ln(H[i] / Cl[i]) + ln(L[i] / O[i]) * ln(L[i] / Cl[i]));
  }
  const rv = x => { const o = new Array(T0).fill(NaN); for (let i = n; i < T0; i++) { let m = 0; for (let j = i - n + 1; j <= i; j++) m += x[j]; m /= n; let v = 0; for (let j = i - n + 1; j <= i; j++) v += (x[j] - m) ** 2; o[i] = v / (n - 1); } return o; };
  const vcc = rv(cc), von = rv(on), voc = rv(oc), mhl = rm(hl2), mgk = rm(hl2.map((v, i) => 0.5 * v - (2 * Math.log(2) - 1) * co2[i])), mrs = rm(rs);
  const kk = 0.34 / (1.34 + (n + 1) / (n - 1)), sq2 = v => (v >= 0 ? Math.sqrt(v * P) : NaN);
  const S = [vcc.map(sq2), mhl.map(v => sq2(v / (4 * Math.log(2)))), mgk.map(sq2), mrs.map(sq2), von.map((v, i) => sq2(v + kk * voc[i] + (1 - kk) * mrs[i]))];
  const rows = []; for (let i = 0; i < T0; i++) if (S.every(s => Number.isFinite(s[i]))) rows.push(i);
  const means = S.map(s => mean(rows.map(i => s[i]))), noise = S.map(s => sdev(rows.slice(1).map((i, j) => s[i] - s[rows[j]])));
  return (veCache[n] = { S, rows, means, sm: noise.map(v => (noise[0] / v) ** 2), d: D.ohlc.t.map(dstr) });
}
const VE_P = { covid: ['2019-07-01', '2021-06-30'], gfc: ['2008-01-01', '2009-12-31'], all: ['2008-01-01', '2026-12-31'] };
function volEst() {
  const n = +$('ve-n').value, pr = VE_P[$('ve-p').value], E = estimators(n); $('ve-n-v').textContent = n;
  const sel = E.rows.filter(i => E.d[i] >= pr[0] && E.d[i] <= pr[1]);
  plot('ve-ts', EST.map((nm, j) => ({ x: sel.map(i => E.d[i]), y: sel.map(i => 100 * E.S[j][i]), mode: 'lines', name: nm, line: { color: ECOL[j], width: 1.3 }, hovertemplate: nm + ' %{x}: %{y:.1f}%<extra></extra>' })),
    layout(Object.assign({ title: ttl(`S&P 500, ${n}-day window`), xaxis: AX('', { type: 'date' }), yaxis: AX(`Annualised volatility (%, ${n}-day)`) }, BOT)));
  plot('ve-sm', [{ y: EST, x: E.sm, type: 'bar', orientation: 'h', marker: { color: ECOL }, name: 'Relative smoothness', hovertemplate: '%{y}: %{x:.2f}<extra></extra>' }],
    layout({ showlegend: false, title: ttl('Relative smoothness vs close-to-close'), shapes: [vline(1, K.navy, 'dot')], margin: { l: 110, r: 12, t: 30, b: 40 }, xaxis: AX('(sd of daily changes, CC / estimator)²'), yaxis: AX('') }));
  out('ve-out', [T.ve(n, listOut(EST.map((nm, j) => `${nm} ${nf(100 * E.means[j], 1)}%`))), T.ve2(nf(Math.min(...E.sm.slice(1)), 1), nf(Math.max(...E.sm.slice(1)), 1))]);
}

// ================================================================= drawdowns
const MONTHS = (() => { const m = []; for (let y = 1990; y <= 2026; y++) for (let k = 1; k <= 12; k++) { if (y === 2026 && k > 9) break; m.push(`${y}-${String(k).padStart(2, '0')}`); } return m; })();
const ddOf = c => { let pk = -Infinity; return c.map(v => { pk = Math.max(pk, v); return v / pk - 1; }); };
const DD = {}; A.forEach(a => (DD[a] = ddOf(M[a].c)));
function drawdowns() {
  const k = +$('dd-t').value, end = MONTHS[k] + '-31'; $('dd-t-v').textContent = MONTHS[k];
  const tr = [], mdd = [];
  A.forEach(a => {
    const d = M[a].d, j = d.findIndex(s => s > end), last = j < 0 ? d.length : j;
    if (last === 0) return;
    const y = DD[a].slice(0, last), mn = Math.min(...y);
    tr.push({ x: d.slice(0, last), y: y.map(v => 100 * v), mode: 'lines', name: `${LBL[a]} (max ${(100 * mn).toFixed(0)}%)`, line: { color: COL[a], width: 1 }, hovertemplate: LBL[a] + ' %{x}: %{y:.1f}%<extra></extra>' });
    mdd.push(`${N(a)} ${nf(100 * mn, 0)}%`);
  });
  plot('dd-chart', tr, layout(Object.assign({ title: ttl('Underwater curves: drawdown from the running peak'), xaxis: AX('', { type: 'date', range: ['1990-01-01', '2026-10-01'] }), yaxis: AX('Drawdown from running peak (%)', { range: [-90, 2] }) }, BOT)));
  const d = M.sp500.d, c = M.sp500.c, j = d.findIndex(s => s > end), last = j < 0 ? d.length : j, y = DD.sp500.slice(0, last);
  const it = y.indexOf(Math.min(...y)); let ip = 0; for (let i = 0; i <= it; i++) if (c[i] > c[ip]) ip = i;
  out('dd-out', [T.dd(MONTHS[k], listOut(mdd)), T.dd2(d[ip], nf(c[ip], 2), d[it], nf(c[it], 2), nf(100 * y[it], 1), nf(100 * (1 / (1 + y[it]) - 1), 0))]);
}

// ================================================================= risk and return
function riskStats(a, y0) {
  const m = M[a], i0 = Math.max(0, m.d.findIndex(s => yearOf(s) >= y0)), c = m.c.slice(i0), d = m.d.slice(i0), P = PER[a];
  const R = []; for (let i = 1; i < c.length; i++) R.push(c[i] / c[i - 1] - 1);
  const years = (Date.parse(d[d.length - 1]) - Date.parse(d[0])) / 864e5 / 365.25, cagr = Math.pow(c[c.length - 1] / c[0], 1 / years) - 1;
  const mu = mean(R) * P, vol = sdev(R) * Math.sqrt(P), srd = mean(R) / sdev(R);
  return { start: d[0], cagr, vol, sr: mu / vol, se: Math.sqrt(P * (1 + srd * srd / 2) / R.length), mdd: Math.min(...ddOf(c)), years };
}
const RR_POS = { sp500: [95, 10], gold: [-80, 40], bettr: [-60, -40], btc: [-80, 30], eurron: [60, 35] };
function riskReturn() {
  const y0 = +$('rr-y').value, S = A.map(a => Object.assign({ a }, riskStats(a, y0))); $('rr-y-v').textContent = y0 === 1990 ? (window.MFM_LANG === 'ro' ? 'eșantionul întreg' : 'full sample') : y0;
  plot('rr-chart', [{ x: S.map(s => 100 * s.vol), y: S.map(s => 100 * s.cagr), text: S.map(s => LBL[s.a]), mode: 'markers', marker: { color: S.map(s => COL[s.a]), size: 14 }, name: 'Market',
    hovertemplate: '%{text}<br>volatility %{x:.1f}%<br>CAGR %{y:.1f}%<extra></extra>' }],
    layout({ showlegend: false, title: ttl(y0 === 1990 ? 'Risk and return, full samples' : `Risk and return, samples from ${y0}`), shapes: [hline(0, K.navy)],
      annotations: S.map(s => ({ x: Math.log10(100 * s.vol), y: 100 * s.cagr, ax: RR_POS[s.a][0], ay: RR_POS[s.a][1], text: `${LBL[s.a]}<br>Sharpe ${s.sr.toFixed(2)} (SE ${s.se.toFixed(2)}), MDD ${(100 * s.mdd).toFixed(0)}%`, showarrow: true, arrowhead: 0, arrowcolor: K.navy, arrowwidth: 0.8, font: { size: 10, color: K.navy }, align: 'left' })),
      xaxis: AX('Annualised volatility (%, log scale)', { type: 'log', range: [Math.log10(3), Math.log10(120)], tickvals: [5, 10, 20, 50, 100] }), yaxis: AX('CAGR (%)', { range: [-15, 65] }) }));
  out('rr-out', [T.rr(y0, listOut(S.map(s => `${N(s.a)} ${nf(s.sr, 2)} (SE ${nf(s.se, 2)}, ${nf(s.years, 1)} ${window.MFM_LANG === 'ro' ? 'ani' : 'years'})`)))]);
}

// ================================================================= case study: VIX from the S&P 500 path
const PL = [1, 2, 5, 10, 20, 50, 100, 250, 500, 1000];
let pvBase = null; const pvCache = {};
function pvInit() {
  const c = M.sp500.c, R = [NaN]; for (let i = 1; i < c.length; i++) R.push(c[i] / c[i - 1] - 1);
  const d = M.sp500.d, P = D.pdv, dates = P.pos.map(p => d[p]);
  const set = dt => (dt <= P.train[1] ? 0 : dt <= P.test[1] ? 1 : 2);
  pvBase = { R, dates, set: dates.map(set) };
}
const kern = (al, de, n) => { const w = range(0, n - 1, 1).map(i => Math.pow(i / 252 + de, -al)), s = sum(w) / 252; return w.map(v => v / s); };
function pvFit(L) {
  if (pvCache[L]) return pvCache[L];
  const P = D.pdv, p = P.params, { R, set } = pvBase, k1 = kern(p.alpha1, p.delta1, L), k2 = kern(p.alpha2, p.delta2, L);
  const X = P.pos.map(t => { let a = 0, b = 0; for (let i = 0; i < L; i++) { const r = R[t - i]; a += k1[i] * r; b += k2[i] * r * r; } return [1, a, Math.sqrt(b)]; });
  const XtX = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], Xty = [0, 0, 0];
  X.forEach((x, i) => { if (set[i] !== 0) return; for (let u = 0; u < 3; u++) { Xty[u] += x[u] * P.vix[i]; for (let v = 0; v < 3; v++) XtX[u][v] += x[u] * x[v]; } });
  const be = window.MFMI.solve(XtX, Xty), fit = X.map(x => be[0] * x[0] + be[1] * x[1] + be[2] * x[2]);
  const sc = [0, 1, 2].map(s => { const ix = set.map((v, i) => (v === s ? i : -1)).filter(i => i >= 0), y = ix.map(i => P.vix[i]), my = mean(y);
    const sse = sum(ix.map(i => (P.vix[i] - fit[i]) ** 2)), sst = sum(y.map(v => (v - my) ** 2)); return { r2: 1 - sse / sst, rmse: Math.sqrt(sse / ix.length) }; });
  const full = kern(p.alpha2, p.delta2, P.lags);
  return (pvCache[L] = { fit, be, sc, share: sum(full.slice(0, L)) / sum(full) });
}
function pathVol() {
  if (!pvBase) pvInit();
  const L = PL[+$('pv-L').value], F = pvFit(L), P = D.pdv, { dates } = pvBase; $('pv-L-v').textContent = L;
  const shade = { type: 'rect', xref: 'x', yref: 'paper', x0: P.test[0], x1: P.test[1], y0: 0, y1: 1, fillcolor: K.amber, opacity: 0.15, line: { width: 0 }, layer: 'below' };
  plot('pv-v', [
    { x: dates, y: P.vix.map(v => 100 * v), mode: 'lines', name: 'VIX (observed)', line: { color: K.blue, width: 1 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' },
    { x: dates, y: F.fit.map(v => 100 * v), mode: 'lines', name: `Fitted from the last ${L} S&P 500 returns`, line: { color: K.red, width: 1 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }
  ], layout(Object.assign({ title: ttl(`R² train ${F.sc[0].r2.toFixed(3)}, test ${F.sc[1].r2.toFixed(3)}, after test ${F.sc[2].r2.toFixed(3)} (test set shaded)`), shapes: [shade],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Volatility (%)', { range: [0, 100] }) }, BOT)));
  plot('pv-r', [{ x: dates, y: P.vix.map((v, i) => v / F.fit[i]), mode: 'lines', name: 'Ratio observed / fitted VIX', line: { color: K.green, width: 0.8 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }],
    layout(Object.assign({ title: ttl('Ratio observed / fitted VIX'), shapes: [shade, hline(1, K.navy, 'dash')], xaxis: AX('', { type: 'date' }), yaxis: AX('Ratio', { range: [0.4, 1.8] }) }, BOT)));
  out('pv-out', [T.pv(L, nf(F.sc[0].r2, 3), nf(F.sc[1].r2, 3), nf(F.sc[2].r2, 3), nf(F.sc[0].rmse, 3), nf(F.sc[1].rmse, 3)), T.pv2(L, pct(F.share, 0))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  $('pr-chart').style.height = '640px'; threeCols('ac-r');
  on(['pr-th'], pricesReturns); P('pr-play', 'pr-th', range(0.5, 10, 0.5), 450);
  $('hq-nu').value = D.tfit.sp500.nu.toFixed(1);
  $('hq-a').addEventListener('input', () => { $('hq-nu').value = D.tfit[$('hq-a').value].nu.toFixed(1); histQQ(); });
  on(['hq-nu'], histQQ); P('hq-play', 'hq-nu', range(2.5, 30, 0.5), 220);
  on(['hl-f'], hill); P('hl-play', 'hl-f', range(0.5, 10, 0.25), 220);
  on(['gl-a', 'gl-p'], gainLoss); P('gl-play', 'gl-p', range(0.1, 5, 0.1), 160);
  on(['ac-a', 'ac-y'], acfThree); P('ac-play', 'ac-y', range(1990, 2020, 1), 600);
  on(['rv-n'], rollingVol); P('rv-play', 'rv-n', range(10, 250, 5), 300);
  on(['ag-a', 'ag-h'], aggregation); P('ag-play', 'ag-h', range(0, HZ.length - 1, 1), 1000);
  on(['lv-a', 'lv-k'], leverage); P('lv-play', 'lv-k', range(1, 20, 1), 500);
  on(['vv-a', 'vv-w'], volumeVol); P('vv-play', 'vv-w', range(20, 500, 20), 500);
  
  const aaReset = () => { const a = $('aa-a').value, ac = acfAbsOf(a), lags = KS.filter(k => ac[k - 1] > 0); const [, sl] = fitLine(lags.map(Math.log), lags.map(k => Math.log(ac[k - 1]))); $('aa-d').value = Math.min(0.49, Math.max(0.01, (sl + 1) / 2)).toFixed(2); };
  aaReset(); $('aa-a').addEventListener('input', () => { aaReset(); acfAbs(); }); on(['aa-d'], acfAbs); P('aa-play', 'aa-d', range(0.01, 0.49, 0.02), 250);
  on(['ty-a', 'ty-k'], taylor); P('ty-play', 'ty-k', range(1, 100, 1), 150);
  on(['oh-m'], ohlcDay); P('oh-play', 'oh-m', range(0, 389, 3), 40); $('oh-new').addEventListener('click', newDay);
  on(['ve-n', 've-p'], volEst); P('ve-play', 've-n', range(5, 125, 4), 450);
  $('dd-t').max = MONTHS.length - 1; $('dd-t').value = MONTHS.length - 1; on(['dd-t'], drawdowns); P('dd-play', 'dd-t', range(0, MONTHS.length - 1, 2), 60);
  on(['rr-y'], riskReturn); P('rr-play', 'rr-y', range(1990, 2022, 1), 600);
  $('pv-L').value = PL.length - 1; on(['pv-L'], pathVol); P('pv-play', 'pv-L', range(0, PL.length - 1, 1), 1200);
  pricesReturns(); histQQ(); hill(); gainLoss(); acfThree(); rollingVol(); aggregation(); leverage(); volumeVol(); acfAbs(); taylor(); ohlcDay(); volEst(); drawdowns(); riskReturn(); pathVol();
}
window.CH1 = { render: { pricesReturns, histQQ, hill, gainLoss, acfThree, rollingVol, aggregation, leverage, volumeVol, acfAbs, taylor, ohlcDay, newDay, volEst, drawdowns, riskReturn, pathVol }, M, moments, quantile, asc, acf, acfData, hillCum, hillK, aggSums, levData, spearman, estimators, riskStats, pvInit: () => pvInit(), pvFit, taylorData, DELTAS, tfit: D.tfit, rollStd, ddOf, tcdf, tinv, ninv };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

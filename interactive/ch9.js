// Chapter 9 interactive page: one block per chart slide, computed in the browser from ch9_data.js.
(function () {
'use strict';
const D = window.CH9_DATA;
const { sum, mean, sdev, median, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, rng, predict, exitTicket } = window.MFMI;
const T = window.CH9_TEXT;
const K = D.col;
const ANN = { spy: 252, btc: 365 };

// ---------------------------------------------------------------- data helpers
function calendar(R) {
  const o = [R.d0]; let t = Date.parse(R.d0 + 'T00:00:00Z');
  for (const g of R.gaps) { t += g * 864e5; o.push(new Date(t).toISOString().slice(0, 10)); }
  return o;
}
const addDays = (d, k) => new Date(Date.parse(d + 'T00:00:00Z') + k * 864e5).toISOString().slice(0, 10);
const DT = { spy: calendar(D.spy), btc: calendar(D.btc) };
const RV = { spy: D.spy.rv, btc: D.btc.rv };
const ON = D.spy.on, OC = D.spy.oc;
const RVT = RV.spy.map((v, i) => v + ON[i] * ON[i]);          // total daily variance: intraday RV + squared overnight return
const CC = ON.map((v, i) => v + OC[i]);                        // close-to-close return
const annv = (v, a) => Math.sqrt(a * v);                       // annualised volatility (%) from a daily variance (%^2)
function daily(dates, y) {                                     // calendar-day version of a series: null on missing days
  const x = [], z = [];
  for (let i = 0; i < dates.length; i++) {
    if (i > 0) for (let d = addDays(dates[i - 1], 1); d < dates[i]; d = addDays(d, 1)) { x.push(d); z.push(null); }
    x.push(dates[i]); z.push(y[i]);
  }
  return { x, y: z };
}
function acf(x, L) {
  const m = mean(x), u = x.map(v => v - m), d = sum(u.map(v => v * v)), a = [];
  for (let k = 1; k <= L; k++) { let s = 0; for (let t = k; t < u.length; t++) s += u[t] * u[t - k]; a.push(s / d); }
  return a;
}
function moments(x) {                                          // population skewness and kurtosis (scipy.stats defaults)
  const n = x.length, m = mean(x); let m2 = 0, m3 = 0, m4 = 0;
  for (const v of x) { const e = v - m, e2 = e * e; m2 += e2; m3 += e2 * e; m4 += e2 * e2; }
  m2 /= n; m3 /= n; m4 /= n;
  return { skew: m3 / m2 ** 1.5, kurt: m4 / (m2 * m2) };
}
const corr = (a, b) => { const ma = mean(a), mb = mean(b); let sab = 0, saa = 0, sbb = 0; for (let i = 0; i < a.length; i++) { const x = a[i] - ma, y = b[i] - mb; sab += x * y; saa += x * x; sbb += y * y; } return sab / Math.sqrt(saa * sbb); };
function slope(x, y) { const mx = mean(x), my = mean(y); let a = 0, b = 0; for (let i = 0; i < x.length; i++) { a += (x[i] - mx) * (y[i] - my); b += (x[i] - mx) ** 2; } return { b: a / b, a: my - a / b * mx }; }
const npdf = x => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
function ncdf(x) {                                             // Normal cdf through erfc (Numerical Recipes, relative error < 1.2e-7)
  const z = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.5 * z), y = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? 1 - y / 2 : y / 2;
}
function nppf(p) {                                             // Acklam's rational approximation
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239];
  const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
  const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  if (p < 0.02425) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
  if (p > 1 - 0.02425) return -nppf(1 - p);
  const q = p - 0.5, r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}
function nwT(d) {                                              // Diebold-Mariano t: mean / Newey-West s.e., floor(4 (T/100)^(2/9)) lags (rv_tools.ols_nw)
  const n = d.length, m = mean(d), u = d.map(v => v - m), L = Math.floor(4 * (n / 100) ** (2 / 9));
  let s = sum(u.map(v => v * v));
  for (let l = 1; l <= L; l++) { let c = 0; for (let t = l; t < n; t++) c += u[t] * u[t - l]; s += 2 * (1 - l / (L + 1)) * c; }
  return m / (Math.sqrt(s) / n);
}
function hist(x, edges) {                                      // density histogram (numpy, density=True)
  const k = edges.length - 1, c = new Array(k).fill(0), lo = edges[0], w = edges[1] - edges[0];
  for (const v of x) { let j = Math.floor((v - lo) / w); if (j === k && v <= edges[k] + 1e-12) j = k - 1; if (j >= 0 && j < k) c[j]++; }
  const n = sum(c);
  return { mid: c.map((_, j) => lo + (j + 0.5) * w), dens: c.map(v => v / (n * w)), w };
}
const legendBelow = y => ({ orientation: 'h', x: 0, xanchor: 'left', y: y === undefined ? -0.2 : y, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } });
const fint = n => (n >= 1000 ? String(n).replace(/\B(?=(\d{3})+(?!\d))/g, window.MFMI.LANG === 'ro' ? '\u00a0' : ',') : String(n));
const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
const small = x => { if (x >= 0.001) return nf(x, 3); if (x >= 1e-5) return nf(x, 5); const e = Math.floor(Math.log10(x)); return nf(x / 10 ** e, 1) + ' × 10' + String(e).split('').map(c => SUP[c]).join(''); };
const sgn = (x, d) => (x >= 0 ? '+' : '') + nf(x, d);

// ================================================================= one trading day
const DAYS = Object.keys(D.days);
function dayPath(day) {
  const Dd = D.days[day], r = Dd.r, n = r.length, p = [Dd.p0], t = [];
  for (let i = 0; i < n; i++) p.push(p[i] * Math.exp(r[i] / 100));
  for (let i = 0; i <= n; i++) { const m = 570 + 5 * i; t.push(`${day} ${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`); }
  const cum = []; let s = 0; for (const v of r) { s += v * v; cum.push(s); }
  let big = 0; for (let i = 1; i < n; i++) if (Math.abs(r[i]) > Math.abs(r[big])) big = i;
  return { Dd, r, p, t, cum, big, rv: s };
}
function intraday() {
  const day = $('id-d').value, P = dayPath(day), k = +$('id-k').value, hm = P.t[k].slice(11);
  $('id-k-v').textContent = hm;
  const cur = vline(P.t[k], K.navy, 'dot');
  plot('id-p', [{ x: P.t, y: P.p, mode: 'lines', name: 'SPY price, 5-minute bars', line: { color: K.blue, width: 1.6 }, hovertemplate: '%{x|%H:%M}: %{y:.2f} USD<extra></extra>' }],
    layout({ title: ttl('SPY on ' + day), shapes: [cur], xaxis: AX('', { type: 'date', tickformat: '%H:%M' }), yaxis: AX('USD'), legend: legendBelow(-0.15), showlegend: true }));
  const xs = P.t.slice(1, k + 1), ys = P.cum.slice(0, k);
  plot('id-c', [
    { x: [P.t[0], ...xs], y: [0, ...ys], mode: 'lines', line: { color: K.red, width: 1.8, shape: 'hv' }, name: 'Cumulative Σ r²ᵢ (%²)', hovertemplate: '%{x|%H:%M}: %{y:.2f} %²<extra></extra>' },
    { x: [P.t[1 + P.big]], y: [P.cum[P.big]], mode: 'markers', name: `Largest 5-minute return (${sgn(P.r[P.big], 2)}%)`, marker: { color: K.amber, size: 10 }, hovertemplate: '%{x|%H:%M}: %{y:.2f} %²<extra></extra>' }
  ], layout({ title: ttl('Realised variance accumulates over the day'), shapes: [cur], xaxis: AX('', { type: 'date', tickformat: '%H:%M', range: [P.t[0], P.t[78]] }),
    yaxis: AX('%²', { range: [-0.03 * P.rv, P.rv * 1.06] }), legend: legendBelow(-0.15) }));
  const sk = k ? P.cum[k - 1] : 0;
  out('id-out', [T.id(hm, nf(sk, 2), pct(sk / P.rv, 0)),
    T.id2(day, nf(P.rv, P.rv < 10 ? 2 : 1), nf(annv(P.rv, 252), 0) + '%', sgn(P.r[P.big], 2) + '%', P.t[1 + P.big].slice(11), pct(P.r[P.big] ** 2 / P.rv, 0), sgn(P.Dd.on, 2) + '%', sgn(P.Dd.oc, 2) + '%')]);
}

// ================================================================= daily realised volatility
function rvSeries() {
  const k = +$('rs-k').value; $('rs-k-v').textContent = k;
  const tr = [], lay = layout({ margin: { l: 56, r: 12, t: 16, b: 40 }, legend: legendBelow(-0.1) }), res = [];
  [['spy', K.blue, 'SPY, daily realised volatility (09:30-16:00, % p.a.)'], ['btc', K.amber, 'Bitcoin, daily realised volatility (24 hours UTC, % p.a.)']].forEach(([m, c, lab], i) => {
    const v = RV[m], dt = DT[m], a = ANN[m], vol = v.map(x => annv(x, a)), ax = i ? '2' : '';
    const ord = v.map((_, j) => j).sort((p, q) => v[q] - v[p]), drop = new Set(ord.slice(0, k));
    const S = m === 'btc' ? daily(dt, vol) : { x: dt, y: vol };
    tr.push({ x: S.x, y: S.y, mode: 'lines', name: lab, line: { color: c, width: 0.9 }, connectgaps: false, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' });
    tr.push({ x: ord.slice(0, k).map(j => dt[j]), y: ord.slice(0, k).map(j => vol[j]), mode: 'markers', name: 'Days removed from the mean', legendgroup: 'rm', showlegend: i === 0, marker: { color: K.red, size: 6 }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' });
    lay['xaxis' + ax] = AX('', { type: 'date', anchor: 'y' + ax, domain: [0, 1] });
    lay['yaxis' + ax] = AX('% p.a.', { domain: i ? [0, 0.44] : [0.56, 1], anchor: 'x' + ax });
    const kept = v.filter((_, j) => !drop.has(j));
    res.push(T.rs(m === 'spy' ? 'SPY' : 'Bitcoin', fint(v.length), nf(annv(mean(v), a), 1) + '%', nf(median(vol), 1) + '%', nf(Math.max(...vol), 1) + '%', dt[ord[0]], k, nf(annv(mean(kept), a), 1) + '%'));
  });
  plot('rs-chart', tr, lay);
  out('rs-out', res);
}

// ================================================================= intraday and overnight variance
function overnight() {
  const g = $('on-g').value, c = +$('on-c').value; $('on-c-v').textContent = nf(c, 2);
  const key = d => (g === 'year' ? d.slice(0, 4) : g === 'quarter' ? d.slice(0, 4) + '-Q' + (Math.floor((+d.slice(5, 7) - 1) / 3) + 1) : d.slice(0, 7));
  const grp = new Map();
  DT.spy.forEach((d, i) => { const k = key(d); if (!grp.has(k)) grp.set(k, { a: 0, b: 0, n: 0 }); const o = grp.get(k); o.a += RV.spy[i]; o.b += ON[i] ** 2; o.n++; });
  const ks = [...grp.keys()], ia = ks.map(k => 252 * grp.get(k).a / grp.get(k).n), ib = ks.map(k => 252 * grp.get(k).b / grp.get(k).n);
  const lab = ks.map(k => (g === 'year' && (k === '2020' || k === '2026') ? k + '*' : k));
  const tr = [
    { x: lab, y: ia, type: 'bar', name: 'Intraday realised variance (09:30-16:00)', marker: { color: K.blue }, hovertemplate: '%{x}: %{y:.0f}<extra></extra>' },
    { x: lab, y: ib, type: 'bar', name: 'Squared overnight return (close to next open)', marker: { color: K.amber }, hovertemplate: '%{x}: %{y:.0f}<extra></extra>' }];
  if (Math.abs(c - 1) > 1e-9) tr.push({ x: lab, y: ia.map(v => c * v), mode: 'markers', name: `Scaled intraday RV, c × RV, c = ${c.toFixed(2)}`, marker: { color: K.navy, size: g === 'month' ? 6 : 10, symbol: 'diamond' }, hovertemplate: '%{x}: %{y:.0f}<extra></extra>' });
  plot('on-chart', tr, layout({ barmode: 'stack', bargap: 0.35, xaxis: AX('', { type: 'category', tickangle: g === 'year' ? 0 : -45 }), yaxis: AX('Annualised variance (%²)'), legend: Object.assign(legendBelow(g === 'year' ? -0.14 : -0.26), { traceorder: 'normal' }) }));
  const sA = sum(RV.spy), sB = sum(ON.map(v => v * v)), n = ON.length, sh = ks.map((k, i) => ib[i] / (ia[i] + ib[i]));
  out('on-out', [T.on(pct(sB / (sA + sB), 0), nf(sdev(CC) * Math.sqrt(252), 1) + '%', nf(sdev(OC) * Math.sqrt(252), 1) + '%', nf(sdev(ON) * Math.sqrt(252), 1) + '%', nf(annv((sA + sB) / n, 252), 1) + '%', pct(Math.min(...sh), 0), pct(Math.max(...sh), 0)),
    T.on2(nf(c, 2), nf(annv(c * sA / n, 252), 1) + '%', nf((sA + sB) / sA, 2))]);
}

// ================================================================= signature plot
function sigCurve(m, year) {
  const S = D.sig[m], j = year === 'all' ? null : S.years.indexOf(+year);
  if (j !== null && j < 0) return null;
  const n = j === null ? sum(S.n) : S.n[j], f = row => (j === null ? sum(row) : row[j]) / n;
  return { ks: S.ks, min: S.ks.map(k => 5 * k), sparse: S.sparse.map(f), sub: S.sub.map(f), ppy: S.ppy, ndays: n, per: m === 'spy' ? 78 : 288 };
}
function signature() {
  const year = $('sg-y').value, om = +$('sg-w').value; $('sg-w-v').textContent = nf(om, 3) + '%';
  const res = [];
  [['spy', 'sg-s', 'SPY'], ['btc', 'sg-b', 'Bitcoin']].forEach(([m, id, name]) => {
    const c = sigCurve(m, year);
    if (!c) { plot(id, [], layout({ title: ttl(`${name}: no data in ${year}`), xaxis: AX('Sampling interval (minutes)'), yaxis: AX('Volatility from mean RV (% p.a.)') })); return; }
    const vs = c.sparse.map(v => annv(v, c.ppy)), vb = c.sub.map(v => annv(v, c.ppy)), nret = c.ks.map(k => Math.ceil(c.per / k));
    const tr = [
      { x: c.min, y: vs, mode: 'lines+markers', name: 'One grid (sparse sampling)', line: { color: K.blue, width: 1.8 }, marker: { size: 7 }, hovertemplate: '%{x} min: %{y:.2f}%<extra></extra>' },
      { x: c.min, y: vb, mode: 'lines+markers', name: 'Average over shifted grids (subsampling)', line: { color: K.red, width: 1.8, dash: 'dash' }, marker: { size: 6, symbol: 'square' }, hovertemplate: '%{x} min: %{y:.2f}%<extra></extra>' }];
    let wn = null;
    if (om > 0) {
      wn = c.sparse.map((v, i) => annv(v + 2 * nret[i] * om * om, c.ppy));
      tr.push({ x: c.min, y: wn, mode: 'lines+markers', name: `One grid + i.i.d. noise ω = ${om.toFixed(3)}%: RV + 2nω²`, line: { color: K.purple, width: 1.8, dash: 'dot' }, marker: { size: 6, symbol: 'diamond' }, hovertemplate: '%{x} min: %{y:.2f}%<extra></extra>' });
    }
    const all = [...vs, ...vb, ...(wn || [])], lo = Math.min(...vs, ...vb), hi = Math.max(...all);
    plot(id, tr, layout({ title: ttl(`${name}, ${year === 'all' ? 'whole sample' : year} (${c.ndays} days)`), xaxis: AX('Sampling interval (minutes)'), yaxis: AX('Volatility from mean RV (% p.a.)', { range: [lo * 0.88, hi * 1.12] }), legend: legendBelow(-0.24) }));
    const last = c.ks.length - 1, lab = c.min[last] >= 60 ? (c.min[last] % 60 ? c.min[last] + ' min' : c.min[last] / 60 + ' h') : c.min[last] + ' min';
    res.push(T.sg(name, nf(vs[0], 1) + '%', nf(vb[m === 'spy' ? 4 : 5], 1) + '%', m === 'spy' ? '30 min' : '60 min', nf(vb[last], 1) + '%', lab, nf(D.sig.rho1[m], 3)));
    if (om > 0) res.push(T.sg2(name, nf(om, 3), nf(2 * c.per * om * om, 4), nf(wn[0], 1) + '%', nf(vs[0], 1) + '%'));
  });
  out('sg-out', res);
}

// ================================================================= jumps
const ALPHAS = [0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001];
const fmtA = a => nf(100 * a, a >= 0.01 ? 0 : a >= 0.001 ? 1 : 2) + '%';
function jumpDays(m, a, bh) {
  const J = D.jumps[m], z = J.z, n = z.length, p = z.map(v => 1 - ncdf(v));
  let thr;
  if (bh) { const s = [...p].sort((x, y) => x - y); let kk = -1; for (let i = 0; i < n; i++) if (s[i] <= (i + 1) * a / n) kk = i; thr = kk < 0 ? -1 : s[kk]; }
  const crit = nppf(1 - a), jump = z.map((v, i) => (bh ? p[i] <= thr : v > crit));
  const Jt = RV[m].map((v, i) => (jump[i] ? Math.max(v - J.bv[i], 0) : 0));
  return { jump, Jt, crit, n };
}
function jumps() {
  const a = ALPHAS[+$('jp-a').value], bh = $('jp-m').value === 'bh';
  $('jp-a-v').textContent = fmtA(a);
  const tr = [], lay = layout({ margin: { l: 56, r: 12, t: 16, b: 40 }, legend: legendBelow(-0.1) }), res = [];
  [['spy', K.blue, 'SPY'], ['btc', K.amber, 'Bitcoin']].forEach(([m, c, name], i) => {
    const R = jumpDays(m, a, bh), v = RV[m], dt = DT[m], A = ANN[m], vol = v.map(x => annv(x, A)), ax = i ? '2' : '', mx = Math.max(...v);
    const S = m === 'btc' ? daily(dt, vol) : { x: dt, y: vol }, idx = v.map((_, j) => j).filter(j => R.jump[j]);
    tr.push({ x: S.x, y: S.y, mode: 'lines', name: `${name}: realised volatility (% p.a.)`, line: { color: c, width: 0.9 }, connectgaps: false, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' });
    tr.push({ x: idx.map(j => dt[j]), y: idx.map(j => vol[j]), mode: 'markers', name: `Day with a significant jump (${bh ? 'FDR ' : ''}${fmtA(a)} level)`, legendgroup: 'j', showlegend: i === 0,
      marker: { color: K.red, size: idx.map(j => 1.3 * Math.sqrt(8 + 400 * R.Jt[j] / mx)), line: { width: 0 } }, xaxis: 'x' + ax, yaxis: 'y' + ax,
      customdata: idx.map(j => [D.jumps[m].z[j], 100 * R.Jt[j] / v[j]]), hovertemplate: '%{x}: z = %{customdata[0]:.2f}, jump %{customdata[1]:.0f}% of RV<extra></extra>' });
    lay['xaxis' + ax] = AX('', { type: 'date', anchor: 'y' + ax, domain: [0, 1] });
    lay['yaxis' + ax] = AX('% p.a.', { domain: i ? [0, 0.44] : [0.56, 1], anchor: 'x' + ax });
    const nj = idx.length, js = sum(R.Jt) / sum(v), mj = nj ? mean(idx.map(j => R.Jt[j] / v[j])) : 0;
    res.push(T.jp(name, nj, fint(R.n), pct(nj / R.n, 1), nf(R.n * a, 1), pct(js, 1), nj ? pct(mj, 0) : '–', bh));
  });
  plot('jp-chart', tr, lay);
  res.push(bh ? T.jp3(fmtA(a)) : T.jp2(fmtA(a), nf(nppf(1 - a), 2)));
  out('jp-out', res);
}

// ================================================================= distributions
const BTC_CC = D.btc.cc;
function distributions() {
  const m = $('ds-m').value, lam = +$('ds-lam').value; $('ds-lam-v').textContent = nf(lam, 2);
  const v = RV[m], ret = m === 'spy' ? OC : BTC_CC, name = m === 'spy' ? 'SPY' : 'Bitcoin';
  const x = v.map(r => (lam < 1e-9 ? Math.log(r) : (r ** lam - 1) / lam)), lo = Math.min(...x), hi = Math.max(...x);
  const H = hist(x, range(0, 50, 1).map(i => lo + (hi - lo) * i / 50)), mu = mean(x), sd = sdev(x), grid = range(0, 199, 1).map(i => lo + (hi - lo) * i / 199);
  const xl = lam < 1e-9 ? 'log RV' : `Box–Cox transform of RV, (RV^λ − 1)/λ, λ = ${lam.toFixed(2)}`;
  plot('ds-l', [
    { x: H.mid, y: H.dens, type: 'bar', width: H.w, name: (lam < 1e-9 ? 'log RV' : 'Box–Cox(RV)') + `, ${name} (daily)`, marker: { color: K.blue, opacity: 0.8 }, hovertemplate: '%{x:.2f}: %{y:.3f}<extra></extra>' },
    { x: grid, y: grid.map(g => npdf((g - mu) / sd) / sd), mode: 'lines', name: 'Normal distribution, same mean and s.d.', line: { color: K.red, width: 2 }, hoverinfo: 'skip' }
  ], layout({ bargap: 0, xaxis: AX(xl), yaxis: AX('Density'), legend: legendBelow(-0.24) }));
  const su = sdev(ret), u = ret.map(r => r / su), z = ret.map((r, i) => r / Math.sqrt(v[i])), cl = a => a.map(q => Math.min(6, Math.max(-6, q)));
  const ed = range(0, 60, 1).map(i => -6 + i * 0.2), Hu = hist(cl(u), ed), Hz = hist(cl(z), ed), xx = range(-6, 6, 0.04);
  const step = Hh => { const X = [], Y = []; Hh.mid.forEach((c, j) => { X.push(c - 0.1, c + 0.1); Y.push(Hh.dens[j], Hh.dens[j]); }); return { X, Y }; }, sz = step(Hz);
  const rl = m === 'spy' ? 'Open-to-close return' : 'Daily return (UTC)';
  plot('ds-r', [
    { x: Hu.mid, y: Hu.dens, type: 'bar', width: 0.2, name: rl + ' / its s.d.', marker: { color: K.amber, opacity: 0.55 }, hovertemplate: '%{x:.1f}: %{y:.3f}<extra></extra>' },
    { x: sz.X, y: sz.Y, mode: 'lines', name: rl + ' / √RV', line: { color: K.blue, width: 1.8 }, hovertemplate: '%{x:.1f}: %{y:.3f}<extra></extra>' },
    { x: xx, y: xx.map(npdf), mode: 'lines', name: 'Standard Normal distribution', line: { color: K.red, width: 1.6, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ bargap: 0, xaxis: AX('Standardised return', { range: [-6.2, 6.2] }), yaxis: AX('Density'), legend: legendBelow(-0.24) }));
  const Mx = moments(x), Mv = moments(v), Mu = moments(u), Mz = moments(z);
  out('ds-out', [T.ds(name, nf(lam, 2), nf(Mx.skew, 2), nf(Mx.kurt, 2), nf(Mv.skew, 1), nf(Mv.kurt, 0)), T.ds2(name, nf(Mu.kurt, 2), nf(Mz.kurt, 2), nf(sdev(z), 2))]);
}

// ================================================================= persistence: ACF of log RV
let AC = null;
function acPrep() {
  if (AC) return AC;
  const L = 100, a1 = acf(RVT.map(Math.log), L);
  const B = daily(DT.btc, RV.btc.map(Math.log)).y, b = [...B];       // calendar days; missing days interpolated linearly
  for (let i = 0; i < b.length; i++) if (b[i] === null) { let j = i; while (b[j] === null) j++; const l = b[i - 1], r = b[j]; for (let k = i; k < j; k++) b[k] = l + (r - l) * (k - i + 1) / (j - i + 1); i = j; }
  const a2 = acf(b, L), a3 = acf(CC.map(v => v * v), L);
  // log-HAR on SPY as an AR(22): implied autocorrelation, from a long simulated path
  const hb = D.har.spy_log, w = new Array(22).fill(0); w[0] += hb[1]; for (let j = 0; j < 5; j++) w[j] += hb[2] / 5; for (let j = 0; j < 22; j++) w[j] += hb[3] / 22;
  const z = rng(9), n = 300000, x = new Array(n).fill(0);
  for (let t = 22; t < n; t++) { let s = z(); for (let j = 0; j < 22; j++) s += w[j] * x[t - 1 - j]; x[t] = s; }
  AC = { L, a1, a2, a3, har: acf(x.slice(2000), L), band: 1.96 / Math.sqrt(RVT.length) };
  return AC;
}
function acfBlock() {
  const A = acPrep(), cmp = $('ac-c').value, rho = +$('ac-r').value, lg = range(1, A.L, 1);
  $('ac-r-v').textContent = nf(rho, 2);
  const tr = [
    { x: lg, y: A.a1, mode: 'lines', name: 'log RV, SPY (trading days)', line: { color: K.blue, width: 2 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lg, y: A.a2, mode: 'lines', name: 'log RV, Bitcoin (calendar days)', line: { color: K.amber, width: 2 }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: lg, y: A.a3, mode: 'lines', name: 'Squared daily return, SPY', line: { color: K.purple, width: 1.5, dash: 'dash' }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' },
    { x: [null], y: [null], mode: 'markers', name: '95% band under independence (SPY)', marker: { color: K.band, size: 12, symbol: 'square' }, hoverinfo: 'skip' }];
  if (cmp === 'ar1') tr.push({ x: lg, y: lg.map(k => rho ** k), mode: 'lines', name: `AR(1) with ρ = ${rho.toFixed(2)}: ρ^k`, line: { color: K.green, width: 2, dash: 'dot' }, hovertemplate: 'lag %{x}: %{y:.4f}<extra></extra>' });
  if (cmp === 'har') tr.push({ x: lg, y: A.har, mode: 'lines', name: 'Implied by the fitted log-HAR (SPY), an AR(22)', line: { color: K.red, width: 2, dash: 'dot' }, hovertemplate: 'lag %{x}: %{y:.3f}<extra></extra>' });
  plot('ac-chart', tr, layout({ shapes: [{ type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: -A.band, y1: A.band, fillcolor: K.band, opacity: 0.7, line: { width: 0 }, layer: 'below' }],
    xaxis: AX('Lag (days)', { range: [0, A.L + 1] }), yaxis: AX('Autocorrelation', { range: [-0.15, 1] }), legend: legendBelow(-0.2) }));
  const r = [T.ac(nf(A.a1[0], 2), nf(A.a1[21], 2), nf(A.a1[99], 2), nf(A.a3[0], 2), nf(A.a2[6], 2), nf(A.a2[29], 2))];
  if (cmp === 'ar1') r.push(T.ac2(nf(rho, 2), small(rho ** 22), small(rho ** 100)));
  if (cmp === 'har') r.push(T.ac3(nf(A.har[0], 2), nf(A.har[21], 2), nf(A.har[99], 2)));
  out('ac-out', r);
}

// ================================================================= VIX and future realised volatility
let VXD = null;
function vixPrep(h) {
  const n = RVT.length, V = D.vix, dt = [], vix = [], fv = [];
  for (let t = 0; t + h < n; t++) {
    if (V[t] === null) continue;
    let s = 0; for (let j = 1; j <= h; j++) s += RVT[t + j];
    dt.push(DT.spy[t]); vix.push(V[t]); fv.push(Math.sqrt(252 / h * s));
  }
  return { h, dt, vix, fv, gap: vix.map((v, i) => v - fv[i]) };
}
function vixBlock() {
  const h = +$('vx-h').value; $('vx-h-v').textContent = h;
  if (!VXD || VXD.h !== h) VXD = vixPrep(h);
  const X = VXD, k = Math.min(+$('vx-t').value, X.dt.length - 1); $('vx-t').max = X.dt.length - 1; $('vx-t-v').textContent = X.dt[k];
  plot('vx-l', [
    { x: X.dt, y: X.vix, mode: 'lines', name: 'VIX (implied volatility, next 30 calendar days)', line: { color: K.red, width: 1.1 }, hovertemplate: 'VIX %{x}: %{y:.1f}<extra></extra>' },
    { x: X.dt, y: X.fv, mode: 'lines', name: `Realised volatility over the next ${h} trading days`, line: { color: K.blue, width: 1.1 }, hovertemplate: 'Realised %{x}: %{y:.1f}<extra></extra>' }
  ], layout({ shapes: [vline(X.dt[k], K.navy, 'dot')], xaxis: AX('', { type: 'date' }), yaxis: AX('% p.a.'), legend: legendBelow(-0.14) }));
  const ed = range(-30, 31.5, 1.5), Hc = ed.slice(0, -1).map((e, j) => X.gap.filter(g => g >= e && (j === ed.length - 2 ? g <= ed[j + 1] : g < ed[j + 1])).length);
  plot('vx-r', [{ x: ed.slice(0, -1).map(e => e + 0.75), y: Hc, type: 'bar', width: 1.5, name: 'VIX minus future realised volatility (percentage points)', marker: { color: K.teal, opacity: 0.85 }, hovertemplate: '%{x:.2f} pp: %{y} days<extra></extra>' }],
    layout({ bargap: 0, showlegend: true, shapes: [vline(0, K.navy), vline(X.gap[k], K.red, 'dot')], xaxis: AX('Percentage points', { range: [-31, 31] }), yaxis: AX('Days'), legend: legendBelow(-0.24) }));
  out('vx-out', [T.vx(h, fint(X.dt.length), nf(mean(X.vix), 2) + '%', nf(mean(X.fv), 2) + '%', pct(X.vix.filter((v, i) => v ** 2 > X.fv[i] ** 2).length / X.dt.length, 0), nf(mean(X.gap), 2), nf(corr(X.vix, X.fv), 2)),
    T.vx2(X.dt[k], nf(X.vix[k], 1) + '%', nf(X.fv[k], 1) + '%', sgn(X.gap[k], 1))]);
}

// ================================================================= out-of-sample forecasts
const MODELS = ['logHAR', 'HAR', 'GARCH-t', 'EWMA', 'RW'];
const ML = { logHAR: 'log-HAR', HAR: 'HAR', 'GARCH-t': 'GARCH(1,1)-t', EWMA: 'EWMA', RW: T.rw };
function fcSet(m) {
  const F = D.fc[m], y = F.pos.map(i => (m === 'spy' ? RVT[i] : RV.btc[i])), dt = F.pos.map(i => DT[m][i]);
  return { F, y, dt };
}
const FC = { spy: fcSet('spy'), btc: fcSet('btc') };
const MONTH0 = []; FC.spy.dt.forEach((d, i) => { if (!i || d.slice(0, 7) !== FC.spy.dt[i - 1].slice(0, 7)) MONTH0.push(d); });
const lossF = (kind, y, f) => (kind === 'qlike' ? y / f - Math.log(y / f) - 1 : (y - f) ** 2);
function oos() {
  const kind = $('oo-l').value, d0 = MONTH0[+$('oo-t').value]; $('oo-t-v').textContent = d0.slice(0, 7);
  const S = FC.spy, sel = S.dt.map((d, i) => i).filter(i => S.dt[i] >= d0), LN = kind === 'qlike' ? 'QLIKE' : 'MSE';
  const loss = (Sx, mm, idx) => idx.map(i => lossF(kind, Sx.y[i], Sx.F[mm][i]));
  const x = sel.map(i => S.dt[i]);
  plot('oo-f', [
    { x, y: sel.map(i => annv(S.y[i], 252)), mode: 'lines', name: 'SPY realised (incl. overnight)', line: { color: K.teal, width: 0.8 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' },
    { x, y: sel.map(i => annv(S.F['GARCH-t'][i], 252)), mode: 'lines', name: 'GARCH(1,1)-t forecast', line: { color: K.blue, width: 1.3 }, hovertemplate: 'GARCH %{x}: %{y:.1f}%<extra></extra>' },
    { x, y: sel.map(i => annv(S.F.logHAR[i], 252)), mode: 'lines', name: 'log-HAR forecast', line: { color: K.red, width: 1.3 }, hovertemplate: 'log-HAR %{x}: %{y:.1f}%<extra></extra>' }
  ], layout({ title: ttl('Volatility forecasts'), xaxis: AX('', { type: 'date' }), yaxis: AX('% p.a.'), legend: legendBelow(-0.14) }));
  const base = loss(S, 'logHAR', sel), cum = mm => { let c = 0; return loss(S, mm, sel).map((v, j) => (c += v - base[j])); };
  const tr = [['GARCH-t', K.purple, 'dash'], ['EWMA', K.green, 'solid'], ['HAR', K.orange, 'solid']].map(([mm, c, ds]) => ({ x, y: cum(mm), mode: 'lines', name: `SPY: ${mm} minus log-HAR`, line: { color: c, width: 1.6, dash: ds }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }));
  const B = FC.btc, sb = B.dt.map((d, i) => i).filter(i => B.dt[i] >= d0), bb = loss(B, 'logHAR', sb);
  if (sb.length) { let c = 0; tr.push({ x: sb.map(i => B.dt[i]), y: loss(B, 'GARCH-t', sb).map((v, j) => (c += v - bb[j])), mode: 'lines', name: 'Bitcoin: GARCH-t minus log-HAR', line: { color: K.amber, width: 1.6, dash: 'dash' }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }); }
  plot('oo-c', tr, layout({ title: ttl('Loss relative to log-HAR'), shapes: [hline(0, K.navy)], xaxis: AX('', { type: 'date', range: [d0, S.dt[S.dt.length - 1]] }), yaxis: AX('Cum. ' + LN + ' diff.'), legend: legendBelow(-0.14) }));
  const ml = mm => mean(loss(S, mm, sel)), dmt = mm => nwT(base.map((v, j) => v - loss(S, mm, sel)[j])), dg = kind === 'qlike' ? 3 : 2;
  const r = [T.oo('SPY', S.dt[sel[0]], fint(sel.length), LN, MODELS.map(mm => `${ML[mm]} ${nf(ml(mm), dg)}`).join(', ')),
    T.oo2(nf(dmt('HAR'), 2), nf(dmt('GARCH-t'), 2), nf(dmt('EWMA'), 2), nf(dmt('RW'), 2))];
  if (sb.length > 30) {
    const mb = mm => mean(loss(B, mm, sb)), tb = nwT(bb.map((v, j) => v - loss(B, 'GARCH-t', sb)[j]));
    r.push(T.oo3(B.dt[sb[0]], sb.length, LN, nf(mb('logHAR'), dg), nf(mb('GARCH-t'), dg), nf(tb, 2)));
  }
  out('oo-out', r);
}

// ================================================================= rough volatility
const QS = [0.5, 1, 1.5, 2, 3], QC = [K.blue, K.green, K.amber, K.purple, K.red];
const LOGSIG = { spy: RVT.map(v => 0.5 * Math.log(v)), btc: daily(DT.btc, RV.btc.map(v => 0.5 * Math.log(v))).y };
const MQ = {};
for (const m of ['spy', 'btc']) {
  const x = LOGSIG[m]; MQ[m] = {};
  for (const q of QS) MQ[m][q] = range(1, 30, 1).map(l => { let s = 0, c = 0; for (let t = l; t < x.length; t++) if (x[t] !== null && x[t - l] !== null) { s += Math.abs(x[t] - x[t - l]) ** q; c++; } return s / c; });
}
function roughFit(m, lo, hi) {
  const lags = range(lo, hi, 1), lx = lags.map(Math.log), zeta = QS.map(q => slope(lx, lags.map(l => Math.log(MQ[m][q][l - 1]))));
  return { lags, zeta, H: sum(QS.map((q, i) => q * zeta[i].b)) / sum(QS.map(q => q * q)) };
}
function rough() {
  let lo = +$('ro-a').value; const hi = 30; $('ro-a-v').textContent = lo + '–' + hi;
  const S = roughFit('spy', lo, hi), Bf = roughFit('btc', lo, hi), all = range(1, 30, 1), lx = all.map(Math.log), tr = [];
  QS.forEach((q, i) => {
    const y = MQ.spy[q].map(Math.log);
    tr.push({ x: lx, y, mode: 'markers', name: `q = ${q}`, legendgroup: 'q' + q, marker: { color: QC[i], size: 6, opacity: all.map(l => (l >= lo ? 1 : 0.3)) }, customdata: all, hovertemplate: 'Δ = %{customdata}: %{y:.3f}<extra></extra>' });
    const f = S.zeta[i];
    tr.push({ x: [Math.log(lo), Math.log(hi)], y: [f.a + f.b * Math.log(lo), f.a + f.b * Math.log(hi)], mode: 'lines', showlegend: false, legendgroup: 'q' + q, line: { color: QC[i], width: 1.4 }, hoverinfo: 'skip' });
  });
  plot('ro-m', tr, layout({ shapes: lo > 1 ? [vline(Math.log(lo), K.navy, 'dot')] : [], xaxis: AX('log Δ (days)'), yaxis: AX('log m(q, Δ)'), legend: legendBelow(-0.2) }));
  plot('ro-z', [
    { x: QS, y: S.zeta.map(z => z.b), mode: 'lines+markers', name: `SPY: slopes, H = ${S.H.toFixed(2)}`, line: { color: K.blue, width: 2 }, marker: { size: 10 }, hovertemplate: 'q = %{x}: ζ = %{y:.3f}<extra></extra>' },
    { x: QS, y: Bf.zeta.map(z => z.b), mode: 'lines+markers', name: `Bitcoin: slopes, H = ${Bf.H.toFixed(2)}`, line: { color: K.amber, width: 2, dash: 'dash' }, marker: { size: 10, symbol: 'square' }, hovertemplate: 'q = %{x}: ζ = %{y:.3f}<extra></extra>' },
    { x: [0.5, 3], y: [0.25, 1.5], mode: 'lines', name: 'Brownian motion: H = 0.5', line: { color: K.navy, width: 1.4, dash: 'dot' }, hoverinfo: 'skip' }
  ], layout({ xaxis: AX('q'), yaxis: AX('Slope ζ<sub>q</sub>', { rangemode: 'tozero' }), legend: legendBelow(-0.2) }));
  out('ro-out', [T.ro(lo, hi, nf(S.H, 3), nf(Bf.H, 3), nf(S.zeta[3].b, 3), nf(Math.pow(2, S.zeta[3].b), 2))]);
}

// ================================================================= case study: ML against HAR
const SIX = [['HAR-X', K.amber, 'diamond'], ['LogHAR', K.red, 'circle'], ['HARQ', K.orange, 'triangle-down'], ['EN', K.purple, 'square'], ['RF', K.green, 'triangle-up'], ['NN10_2', K.blue, 'cross']];
const HZ = ['day', 'week', 'month'], HL = ['1 day', '1 week', '1 month'];
function csvBlock() {
  const C = D.csv, sel = $('cs-m').value, j = C.models.indexOf(sel), lab = C.labels[j];
  const rel = (info, m) => HZ.map(h => C.rel[h + '|' + info][C.models.indexOf(m)]);
  const lines = SIX.some(s => s[0] === sel) ? SIX : [...SIX, [sel, C.fcol[C.family[sel]], 'star']], tr = [];
  ['HAR', 'ALL'].forEach((info, p) => {
    const ax = p ? '2' : '';
    tr.push({ x: HL, y: [1, 1, 1], mode: 'lines', name: 'HAR = 1', legendgroup: 'har', showlegend: !p, line: { color: K.navy, width: 1.2, dash: 'dash' }, xaxis: 'x' + ax, yaxis: 'y' + ax, hoverinfo: 'skip' });
    lines.forEach(([m, c, mk]) => {
      const on = m === sel, l = C.labels[C.models.indexOf(m)];
      tr.push({ x: HL, y: rel(info, m), mode: on ? 'lines+markers+text' : 'lines+markers', name: l, legendgroup: m, showlegend: !p, xaxis: 'x' + ax, yaxis: 'y' + ax,
        line: { color: c, width: on ? 3.4 : 1.6, dash: SIX.some(s => s[0] === m) ? 'solid' : 'dot' }, marker: { symbol: mk, size: on ? 12 : 8, color: c },
        text: on ? rel(info, m).map(v => v.toFixed(3)) : undefined, textposition: 'top right', textfont: { size: 11, color: K.navy }, cliponaxis: false, opacity: on ? 1 : 0.75, hovertemplate: l + ', %{x}: %{y:.3f}<extra></extra>' });
    });
  });
  const ttl2 = (x, t) => ({ text: t, x, xref: 'paper', y: 1.02, yref: 'paper', xanchor: 'left', yanchor: 'bottom', showarrow: false, font: { size: 12, color: K.navy } });
  plot('cs-chart', tr, layout({ margin: { l: 60, r: 40, t: 34, b: 40 }, annotations: [ttl2(0, 'M<sub>HAR</sub>: daily, weekly, monthly RV'), ttl2(0.54, 'M<sub>ALL</sub>: RV lags + 9 predictors (12 in total)')],
    xaxis: AX('Forecast horizon', { type: 'category', range: [-0.25, 2.55], domain: [0, 0.46] }), yaxis: AX('Out-of-sample MSE relative to HAR', { range: [0.55, 1.65] }),
    xaxis2: AX('Forecast horizon', { type: 'category', range: [-0.25, 2.55], domain: [0.54, 1], anchor: 'y2' }), yaxis2: AX('', { range: [0.55, 1.65], anchor: 'x2' }),
    legend: legendBelow(-0.2) }));
  const a = rel('HAR', sel), b = rel('ALL', sel), month = C.rel['month|ALL'], rank = 1 + month.filter(v => v < month[j]).length;
  out('cs-out', [T.cs(lab, T.fam[C.family[sel]], nf(a[0], 3), nf(a[1], 3), nf(a[2], 3), nf(b[0], 3), nf(b[1], 3), nf(b[2], 3), rank)]);
}

// ================================================================= case study: partial variances (Bollerslev, Medeiros, Patton & Quaedvlieg, 2022)
const PV = D.partial, PVQ = PV.q, PVCOL = { spy: K.blue, btc: K.amber }, PVLAB = { spy: 'SPY', btc: 'Bitcoin' }, PVTOP = 1.15;
function pvSet(m) {                                            // forecasts of case_partial.py; target = RV (SPY intraday, Bitcoin 24 hours)
  const S = PV[m], y = S.pos.map(i => RV[m][i]), order = y.map((v, i) => i).sort((a, b) => y[b] - y[a]);
  return { S, y, order };
}
const PVS = { spy: pvSet('spy'), btc: pvSet('btc') };
function pvRatios(m, k) {                                      // loss ratios to RV-HAR without the k days with the largest RV
  const { S, y, order } = PVS[m], drop = new Set(order.slice(0, k)), idx = y.map((v, i) => i).filter(i => !drop.has(i));
  const L = (mm, kind) => mean(idx.map(i => lossF(kind, y[i], S[mm][i])));
  const base = { mse: L('RV-HAR', 'mse'), qlike: L('RV-HAR', 'qlike') }, rat = (mm, kind) => L(mm, kind) / base[kind];
  const se = y.map((v, i) => lossF('mse', v, S['RV-HAR'][i]));
  const dq = idx.map(i => lossF('qlike', y[i], S['SV-HAR'][i]) - lossF('qlike', y[i], S['RV-HAR'][i]));
  return { n: idx.length, sv: { mse: rat('SV-HAR', 'mse'), qlike: rat('SV-HAR', 'qlike') }, p3: { mse: rat('PV(3)', 'mse'), qlike: rat('PV(3)', 'qlike') },
    curve: { mse: PVQ.map(q => rat('PV2_' + q.toFixed(2), 'mse')), qlike: PVQ.map(q => rat('PV2_' + q.toFixed(2), 'qlike')) },
    share: sum(order.slice(0, k).map(i => se[i])) / sum(se), t: nwT(dq) };
}
function partialBlock() {
  const k = +$('pv-k').value; $('pv-k-v').textContent = k;
  const R = { spy: pvRatios('spy', k), btc: pvRatios('btc', k) };
  ['mse', 'qlike'].forEach(kind => {
    const vals = ['spy', 'btc'].flatMap(m => [...R[m].curve[kind], R[m].sv[kind]]);
    const top = Math.max(PVTOP, ...vals.filter(v => v <= 1.5)), tr = [], ann = [];
    for (const m of ['spy', 'btc']) {
      const c = R[m].curve[kind];
      tr.push({ x: PVQ, y: c.map(v => Math.min(v, top)), customdata: c, mode: 'lines+markers', name: `${PVLAB[m]}: PV(2)-HAR, one threshold at quantile q`, line: { color: PVCOL[m], width: 1.8 }, marker: { size: 6 }, hovertemplate: PVLAB[m] + ', q = %{x:.2f}: %{customdata:.3f}<extra></extra>' });
      tr.push({ x: [PVQ[0], PVQ[PVQ.length - 1]], y: [R[m].sv[kind], R[m].sv[kind]], mode: 'lines', name: `${PVLAB[m]}: SV-HAR (threshold at zero)`, line: { color: PVCOL[m], width: 1.4, dash: 'dash' }, hovertemplate: PVLAB[m] + ' SV-HAR: ' + R[m].sv[kind].toFixed(3) + '<extra></extra>' });
      c.forEach((v, j) => { if (v > top) ann.push({ x: PVQ[j], y: top, text: `${PVLAB[m]}, q = ${PVQ[j].toFixed(2)}: ${v.toFixed(2)}`, showarrow: false, xanchor: 'right', yanchor: 'top', xshift: -6, font: { size: 11, color: PVCOL[m] } }); });
    }
    tr.push({ x: [PVQ[0], PVQ[PVQ.length - 1]], y: [1, 1], mode: 'lines', name: 'RV-HAR = 1', line: { color: K.navy, width: 1.2, dash: 'dot' }, hoverinfo: 'skip' });
    plot(kind === 'mse' ? 'pv-m' : 'pv-q', tr, layout({ title: ttl(kind === 'mse' ? 'MSE relative to RV-HAR' : 'QLIKE relative to RV-HAR'), annotations: ann,
      xaxis: AX('Threshold: quantile q of standardised returns'), yaxis: AX('Loss ratio', { range: [Math.min(...vals) - 0.01, top + 0.01] }), legend: legendBelow(-0.3) }));
  });
  const best = (m, kind) => { const c = R[m].curve[kind], j = c.indexOf(Math.min(...c)); return [nf(PVQ[j], 2), nf(c[j], 3)]; };
  const line = m => T.pv(PVLAB[m], fint(R[m].n), k, nf(R[m].sv.mse, 3), nf(R[m].sv.qlike, 3), nf(R[m].p3.mse, 3), nf(R[m].p3.qlike, 3), ...best(m, 'mse'), ...best(m, 'qlike'));
  out('pv-out', [line('spy'), line('btc'), T.pv2(k, pct(R.spy.share, 0), nf(R.spy.t, 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  $('rs-chart').style.height = '480px'; $('jp-chart').style.height = '480px'; $('on-chart').style.height = '400px'; $('ac-chart').style.height = '420px'; $('cs-chart').style.height = '440px'; $('pv-m').style.height = '400px'; $('pv-q').style.height = '400px';
  on(['id-d', 'id-k'], intraday); P('id-play', 'id-k', range(1, 78, 1), 120);
  on(['rs-k'], rvSeries); P('rs-play', 'rs-k', range(0, 100, 5), 500);
  on(['on-g', 'on-c'], overnight); P('on-play', 'on-c', range(1, 2, 0.05), 300);
  on(['sg-y', 'sg-w'], signature); P('sg-play', 'sg-w', range(0, 0.05, 0.002), 350);
  on(['jp-a', 'jp-m'], jumps); P('jp-play', 'jp-a', range(0, ALPHAS.length - 1, 1), 900);
  on(['ds-m', 'ds-lam'], distributions); P('ds-play', 'ds-lam', range(0, 1, 0.05), 300);
  $('ac-r').addEventListener('input', () => { if ($('ac-c').value !== 'ar1') $('ac-c').value = 'ar1'; acfBlock(); });
  on(['ac-c'], acfBlock); P('ac-play', 'ac-r', range(0.3, 0.99, 0.01), 120);
  const n0 = vixPrep(21).dt.length; $('vx-t').max = n0 - 1; $('vx-t').value = n0 - 1;
  on(['vx-h', 'vx-t'], vixBlock); P('vx-play', 'vx-t', range(0, n0 - 1, 5), 60);
  $('oo-t').max = MONTH0.findIndex(d => d >= '2026-01-01'); on(['oo-l', 'oo-t'], oos); P('oo-play', 'oo-t', range(0, +$('oo-t').max, 1), 500);
  on(['ro-a'], rough); P('ro-play', 'ro-a', range(1, 20, 1), 500);
  on(['cs-m'], csvBlock); P('cs-play', 'cs-m', D.csv.models, 1200);
  on(['pv-k'], partialBlock); P('pv-play', 'pv-k', range(0, 30, 1), 450);
  const PFX = { 'one-day': 'id', 'rv-series': 'rs', 'overnight': 'on', 'signature': 'sg', 'jumps': 'jp', 'distributions': 'ds', 'persistence': 'ac', 'vix': 'vx', 'forecasts': 'oo', 'rough': 'ro', 'ml-vs-har': 'cs', 'partial': 'pv' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'] }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  intraday(); rvSeries(); overnight(); signature(); jumps(); distributions(); acfBlock(); vixBlock(); oos(); rough(); csvBlock(); partialBlock();
}
window.CH9 = { acf, moments, nwT, ncdf, nppf, jumpDays, sigCurve, vixPrep, roughFit, dayPath, RVT, CC, DT, RV, FC, lossF, acPrep, pvRatios };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

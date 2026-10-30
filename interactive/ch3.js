// Chapter 3 interactive page: one block per chart slide, computed in the browser from ch3_data.js.
(function () {
'use strict';
const D = window.CH3_DATA;
const { C, dot, mv, quad, solve, wTan, frontierUnc, rng, mean, sum, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH3_TEXT;
// layout with the legend further down when the x axis has a title (no overlap with the axis title)
const lay = extra => { const l = layout(extra); if (l.xaxis && l.xaxis.title && l.xaxis.title.text) l.legend = Object.assign({}, l.legend, { y: -0.3 }); return l; };
const thin = (sh, w) => Object.assign(sh, { line: Object.assign({}, sh.line, { width: w || 1 }) });

// ---------------------------------------------------------------- colours (same as generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', crimson: '#DC3545', teal: '#17A2B8' };

// ---------------------------------------------------------------- chapter helpers
const nwLags = n => Math.floor(4 * Math.pow(n / 100, 2 / 9));
function inv(A) { const n = A.length, cols = A.map((_, j) => solve(A, A.map((__, i) => (i === j ? 1 : 0)))); return A.map((_, i) => cols.map(c => c[i])); }
// OLS with a constant and Newey-West (Bartlett) covariance, as ols_hac in mfm_data.py; X: rows of regressors
function olsNW(y, X, lags) {
  const n = y.length, Z = X ? X.map(r => [1, ...r]) : y.map(() => [1]), k = Z[0].length;
  if (lags === undefined) lags = nwLags(n);
  const ZZ = Array.from({ length: k }, () => new Array(k).fill(0)), Zy = new Array(k).fill(0);
  for (let t = 0; t < n; t++) for (let i = 0; i < k; i++) { Zy[i] += Z[t][i] * y[t]; for (let j = 0; j < k; j++) ZZ[i][j] += Z[t][i] * Z[t][j]; }
  const Zi = inv(ZZ), b = mv(Zi, Zy), e = y.map((v, t) => v - dot(Z[t], b)), u = Z.map((r, t) => r.map(v => v * e[t]));
  const S = Array.from({ length: k }, () => new Array(k).fill(0));
  for (let t = 0; t < n; t++) for (let i = 0; i < k; i++) for (let j = 0; j < k; j++) S[i][j] += u[t][i] * u[t][j];
  for (let l = 1; l <= lags; l++) {
    const w = 1 - l / (lags + 1);
    for (let t = l; t < n; t++) for (let i = 0; i < k; i++) for (let j = 0; j < k; j++) S[i][j] += w * (u[t][i] * u[t - l][j] + u[t - l][i] * u[t][j]);
  }
  const mm = (A, B) => A.map(r => B[0].map((_, j) => r.reduce((s, v, m) => s + v * B[m][j], 0))), V = mm(Zi, mm(S, Zi));
  const se = V.map((r, i) => Math.sqrt(r[i]));
  return { b, se, t: b.map((v, i) => v / se[i]), e, V };
}
// regularized incomplete beta (Numerical Recipes) and the upper tail of the F distribution
function lgam(x) { const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]; let y = x, tmp = x + 5.5; tmp -= (x + 0.5) * Math.log(tmp); let s = 1.000000000190015; for (const v of c) s += v / ++y; return -tmp + Math.log(2.5066282746310005 * s / x); }
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
function ibeta(x, a, b) {
  if (x <= 0) return 0; if (x >= 1) return 1;
  const bt = Math.exp(lgam(a + b) - lgam(a) - lgam(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
}
const fUpper = (w, d1, d2) => ibeta(d2 / (d2 + d1 * w), d2 / 2, d1 / 2);
function eigSymV(A) {              // Jacobi rotations with eigenvectors; decreasing eigenvalues, vectors in columns
  const n = A.length, M = A.map(r => [...r]), V = A.map((_, i) => A.map((__, j) => (i === j ? 1 : 0)));
  for (let sweep = 0; sweep < 80; sweep++) {
    let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += M[i][j] * M[i][j];
    if (off < 1e-22) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      if (Math.abs(M[p][q]) < 1e-16) continue;
      const th = (M[q][q] - M[p][p]) / (2 * M[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < n; k++) { const a = M[k][p], b = M[k][q]; M[k][p] = c * a - s * b; M[k][q] = s * a + c * b; }
      for (let k = 0; k < n; k++) { const a = M[p][k], b = M[q][k]; M[p][k] = c * a - s * b; M[q][k] = s * a + c * b; }
      for (let k = 0; k < n; k++) { const a = V[k][p], b = V[k][q]; V[k][p] = c * a - s * b; V[k][q] = s * a + c * b; }
    }
  }
  const ord = M.map((r, i) => i).sort((i, j) => M[j][j] - M[i][i]);
  return { vals: ord.map(i => M[i][i]), vecs: V.map(r => ord.map(i => r[i])) };
}
const cov1 = (a, b) => { const ma = mean(a), mb = mean(b); let s = 0; for (let i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb); return s / (a.length - 1); };
const corr = (a, b) => cov1(a, b) / Math.sqrt(cov1(a, a) * cov1(b, b));
function pctile(a, p) { const s = [...a].sort((x, y) => x - y), h = (s.length - 1) * p, lo = Math.floor(h); return s[lo] + (h - lo) * ((s[Math.min(lo + 1, s.length - 1)]) - s[lo]); }
function fmtP(p) {
  if (p >= 0.001) return nf(p, 3);
  let e = Math.floor(Math.log10(p)), m = +(p / Math.pow(10, e)).toFixed(1);
  if (m >= 10) { m = 1; e += 1; }
  return `${nf(m, 1)} × 10<sup>−${-e}</sup>`;
}
const firstOfYear = (dates, y) => Math.max(0, dates.findIndex(d => d >= String(y)));
const per = (dates, i0, i1) => `${dates[i0]} – ${dates[i1]}`;

// ================================================================= efficient frontier of the US sectors
const FR_POS = { XLI: 'top left', XLU: 'bottom right', XLV: 'bottom center', XLP: 'middle left', XLE: 'bottom right', XLY: 'top right', XLB: 'middle right', XLF: 'middle right', XLK: 'top center' };
function frontier() {
  const F = D.fr, S = D.sectors, k = +$('fr-t').value, n = k + 1;
  $('fr-t-v').textContent = F.dates[k];
  const R = F.R.slice(0, n), mu = S.map((_, j) => 12 * mean(R.map(r => r[j]))), cov = S.map((_, i) => S.map((__, j) => 12 * cov1(R.map(r => r[i]), R.map(r => r[j]))));
  const sp = F.spy.slice(0, n), spm = 12 * mean(sp), sps = Math.sqrt(12 * cov1(sp, sp));
  const Si1 = solve(cov, S.map(() => 1)), Sim = solve(cov, mu), A = sum(Si1), B = sum(Sim);
  const sdi = S.map((_, i) => Math.sqrt(cov[i][i]));
  const ok = B > 0, w = ok ? wTan(mu, cov) : null, mt = ok ? dot(w, mu) : NaN, st = ok ? Math.sqrt(quad(w, cov)) : NaN;
  const ytop = Math.max(0.20, ...mu.map(v => v + 0.02), ok ? mt + 0.03 : 0), ybot = Math.min(-0.02, ...mu.map(v => v - 0.02)), xr = Math.max(0.32, ...sdi.map(v => v + 0.03), ok ? st + 0.03 : 0);
  const tg = range(ybot, ytop, (ytop - ybot) / 300), sf = frontierUnc(mu, cov, tg), eff = tg.map(t => t >= B / A);
  const ht = 'vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>';
  const tr = [
    { x: sf.filter((_, i) => eff[i]), y: tg.filter((_, i) => eff[i]), mode: 'lines', name: 'Efficient frontier (risky sectors)', line: { color: K.blue, width: 2 }, hovertemplate: ht },
    { x: sf.filter((_, i) => !eff[i]), y: tg.filter((_, i) => !eff[i]), mode: 'lines', name: 'Inefficient branch', line: { color: K.blue, width: 1.5, dash: 'dot' }, hovertemplate: ht }
  ];
  if (ok) tr.push({ x: [0, xr], y: [0, mt / st * xr], mode: 'lines', name: 'Capital market line (CML)', line: { color: K.red, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [st], y: [mt], mode: 'markers', name: 'Tangency portfolio', marker: { color: K.red, size: 15, symbol: 'star' }, hovertemplate: 'Tangency<br>vol %{x:.1%}<br>mean %{y:.1%}<br>Sharpe ' + (mt / st).toFixed(2) + '<extra></extra>' });
  tr.push({ x: sdi, y: mu, text: S, mode: 'markers+text', textposition: S.map(s => FR_POS[s] || 'top right'), textfont: { size: 10, color: C.navy }, name: 'Sector ETFs', marker: { color: K.purple, size: 8 }, hovertemplate: '%{text}<br>vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>' },
    { x: [sps], y: [spm], mode: 'markers', name: 'S&P 500 (SPY)', marker: { color: K.green, size: 10 }, hovertemplate: 'SPY<br>vol %{x:.1%}<br>mean %{y:.1%}<br>Sharpe ' + (spm / sps).toFixed(2) + '<extra></extra>' });
  plot('fr-chart', tr, lay({ title: ttl(`US sector ETFs, monthly ${per(F.dates, 0, k)}: in-sample frontier`), xaxis: AX('Volatility (annualised)', { tickformat: '.0%', range: [0, xr] }), yaxis: AX('Mean excess return (ann.)', { tickformat: '.0%', range: [ybot, ytop] }) }));
  plot('fr-w', [{ x: S, y: ok ? w : S.map(() => 0), type: 'bar', name: 'Tangency portfolio', marker: { color: ok ? w.map(v => (v < 0 ? K.red : K.blue)) : K.blue, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }],
    lay({ showlegend: false, title: ttl('Weights of the tangency portfolio (red: short)'), shapes: [hline(0, C.navy)], xaxis: AX(''), yaxis: AX('Weight', { tickformat: '.1f' }) }));
  out('fr-out', [ok ? T.fr(F.dates[k], pct(mt, 2), pct(st, 2), nf(mt / st, 2), nf(spm / sps, 2), S.filter((_, i) => w[i] < 0).map(s => `${s} ${nf(w[S.indexOf(s)], 2)}`).join(', ') || '—') : T.fr0(F.dates[k])]);
}

// ================================================================= XLK market model
function bootAlpha(y, x, block, B, seed) {
  const n = y.length, nb = Math.ceil(n / block), z = rng(seed), res = [];
  for (let b = 0; b < B; b++) {
    let sx = 0, sy = 0, sxx = 0, sxy = 0, m = 0;
    for (let k = 0; k < nb && m < n; k++) {
      const st = Math.floor(z.u() * (n - block + 1));
      for (let j = 0; j < block && m < n; j++, m++) { const xi = x[st + j], yi = y[st + j]; sx += xi; sy += yi; sxx += xi * xi; sxy += xi * yi; }
    }
    const be = (sxy - sx * sy / n) / (sxx - sx * sx / n); res.push(12 * (sy / n - be * sx / n));
  }
  return res;
}
const xkCache = {};
function xlk() {
  const X = D.xlk, bl = +$('xk-b').value, L = +$('xk-L').value, y = X.y, x = X.x, n = y.length;
  $('xk-b-v').textContent = bl; $('xk-L-v').textContent = L;
  const r = olsNW(y, x.map(v => [v]), L), r0 = olsNW(y, x.map(v => [v]), 0);
  const e = r.e, s2 = sum(e.map(v => v * v)) / (n - 2), mx = mean(x), sxx = sum(x.map(v => (v - mx) ** 2));
  const seCl = [Math.sqrt(s2 * (1 / n + mx * mx / sxx)), Math.sqrt(s2 / sxx)];
  if (!xkCache[bl]) xkCache[bl] = bl === 12 ? X.draws12 : bootAlpha(y, x, bl, 2000, 100 + bl);
  const dr = xkCache[bl], lo = pctile(dr, 0.025), hi = pctile(dr, 0.975), bse = Math.sqrt(sum(dr.map(v => (v - mean(dr)) ** 2)) / dr.length);
  const xs = [Math.min(...x), Math.max(...x)];
  plot('xk-sc', [
    { x: x.map(v => 100 * v), y: y.map(v => 100 * v), mode: 'markers', name: 'Monthly excess returns', marker: { color: K.blue, size: 4, opacity: 0.7 }, text: X.dates, hovertemplate: '%{text}<br>Mkt-RF %{x:.1f}%<br>XLK %{y:.1f}%<extra></extra>' },
    { x: xs.map(v => 100 * v), y: xs.map(v => 100 * (r.b[0] + r.b[1] * v)), mode: 'lines', name: 'OLS: beta = ' + r.b[1].toFixed(3), line: { color: K.red, width: 2 }, hoverinfo: 'skip' }
  ], lay({ title: ttl(`T = ${n} months`), xaxis: AX('Mkt-RF (%)'), yaxis: AX('XLK excess return (%)') }));
  plot('xk-res', [{ x: X.dates, y: e.map(v => 100 * v), mode: 'lines', name: 'OLS residual', line: { color: K.green, width: 1 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' }],
    lay({ title: ttl('Residuals: 2000-02, 2008, 2020'), shapes: [thin(hline(0, C.navy))], xaxis: AX(''), yaxis: AX('Residual (%)') }));
  plot('xk-boot', [
    { x: dr.map(v => 100 * v), type: 'histogram', nbinsx: 40, name: 'Bootstrap alpha (2000 draws)', marker: { color: K.amber, line: { color: '#fff', width: 0.5 } }, hovertemplate: '%{x}: %{y}<extra></extra>' },
    { x: [null], y: [null], mode: 'lines', name: '95% percentile interval', line: { color: K.red, dash: 'dash', width: 2 } }
  ], lay({ bargap: 0, title: ttl(`Moving-block bootstrap, blocks of ${bl} months`), shapes: [vline(100 * lo, K.red, 'dash'), vline(100 * hi, K.red, 'dash'), vline(0, C.navy, 'dot')], xaxis: AX('Annualised alpha (%)'), yaxis: AX('Draws') }));
  out('xk-out', [T.xk1(pct(12 * r.b[0], 2), nf(r.b[1], 3), nf(seCl[1], 3), nf(r0.se[1], 3), L, nf(r.se[1], 3), nf(r.b[0] / r.se[0], 2)),
    T.xk2(bl, pct(lo, 1), pct(hi, 1), pct(bse, 2), pct(12 * r.se[0], 2))]);
}

// ================================================================= Dimson beta (simulation)
function dimson() {
  const M = D.dim, p = +$('dm-p').value, be = +$('dm-b').value, n = M.rm.length;
  $('dm-p-v').textContent = pct(p, 0); $('dm-b-v').textContent = nf(be, 1);
  const obs = new Array(n).fill(0); let acc = 0;
  for (let t = 0; t < n; t++) { acc += be * M.rm[t] + M.eps[t]; if (M.u[t] < p) { obs[t] = acc; acc = 0; } }
  const y = obs.slice(1, -1), X = y.map((_, i) => [M.rm[i], M.rm[i + 1], M.rm[i + 2]]);
  const b = olsNW(y, X, 0).b, vals = [b[1], b[2], b[3], b[1] + b[2] + b[3]];
  plot('dm-chart', [
    { x: ['t−1', 't', 't+1', 'Dimson sum'], y: vals, type: 'bar', name: 'Slope', marker: { color: [K.amber, K.blue, K.amber, K.green], line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.3f}<extra></extra>', showlegend: false },
    { x: [null], y: [null], mode: 'lines', name: 'True beta = ' + be.toFixed(1), line: { color: K.red, dash: 'dash', width: 2 } }
  ], lay({ title: ttl(`Simulated stock that trades on ${Math.round(100 * p)}% of the days, 5000 days`), shapes: [hline(be, K.red, 'dash')], annotations: vals.map((v, i) => ({ x: i, y: v > 0.3 ? v / 2 : Math.max(v, 0) + 0.02, text: (Math.abs(v) < 0.005 ? Math.abs(v) : v).toFixed(2), showarrow: false, yanchor: v > 0.3 ? 'middle' : 'bottom', font: { color: v > 0.3 ? '#fff' : C.navy, size: 12 } })), xaxis: AX('Market return of day'), yaxis: AX('Slope', { range: [Math.min(0, ...vals) - 0.05, Math.max(1.25, 1.25 * be, ...vals.map(v => v + 0.15))] }) }));
  out('dm-out', [T.dm(pct(p, 0), nf(be, 1), nf(b[2], 2), nf(b[1], 2), nf(vals[3], 2))]);
}

// ================================================================= rolling betas
const RB_W = [63, 126, 252, 504, 756], RB_COL = [K.blue, K.green, K.red, K.amber], RB_NAME = { XLK: 'Technology', XLU: 'Utilities', XLF: 'Financials', XLE: 'Energy' };
const rbCache = {};
function rollBeta(x, m, w) {
  const n = x.length, b = new Array(n).fill(null); let sx = 0, sm = 0, sxm = 0, smm = 0;
  for (let t = 0; t < n; t++) {
    sx += x[t]; sm += m[t]; sxm += x[t] * m[t]; smm += m[t] * m[t];
    if (t >= w) { sx -= x[t - w]; sm -= m[t - w]; sxm -= x[t - w] * m[t - w]; smm -= m[t - w] * m[t - w]; }
    if (t >= w - 1) b[t] = (sxm - sx * sm / w) / (smm - sm * sm / w);
  }
  return b;
}
function rolling() {
  const R = D.rb, w = RB_W[+$('rb-w').value];
  $('rb-w-v').textContent = T.days(w);
  if (!rbCache[w]) rbCache[w] = R.R.map(x => rollBeta(x, R.m, w));
  const B = rbCache[w];
  plot('rb-chart', R.names.map((s, k) => ({ x: R.dates.slice(w - 1), y: B[k].slice(w - 1), mode: 'lines', name: `${s} (${RB_NAME[s]})`, line: { color: RB_COL[k], width: 1 }, hovertemplate: s + ' %{x}: %{y:.2f}<extra></extra>' })),
    lay({ title: ttl(`Rolling ${w}-day betas of sector ETFs against SPY`), shapes: [thin(hline(1, C.navy, 'dot'), 1.2)], xaxis: AX(''), yaxis: AX(`${w}-day rolling beta vs SPY`), hovermode: 'x unified' }));
  out('rb-out', [T.rb(w), ...R.names.map((s, k) => { const v = B[k].filter(z => z !== null); return T.rbRow(s, nf(Math.min(...v), 2), nf(Math.max(...v), 2), nf(v[v.length - 1], 2)); })]);
}

// ================================================================= 25 size x B/M portfolios
const p25Cache = {};
function p25Stats(i0) {
  if (p25Cache[i0]) return p25Cache[i0];
  const P = D.p25, mk = P.f['Mkt-RF'].slice(i0), Xm = mk.map(v => [v]), n = mk.length, lags = nwLags(n);
  const rows = P.R.map(r => { const y = r.slice(i0), o = olsNW(y, Xm, lags); return { avg: 12 * mean(y), alpha: 12 * o.b[0], t: o.t[0], beta: o.b[1], e: o.e, a: o.b[0] }; });
  // GRS (division by T, as grs_test in mfm_data.py)
  const N = rows.length, Sig = rows.map(ri => rows.map(rj => dot(ri.e, rj.e) / n)), al = rows.map(r => r.a);
  const mu = mean(mk), s2 = mk.reduce((s, v) => s + (v - mu) ** 2, 0) / n;
  const W = (n - N - 1) / N * dot(al, solve(Sig, al)) / (1 + mu * mu / s2);
  const res = { rows, n, prem: 12 * mu, grs: W, p: fUpper(W, N, n - N - 1) };
  p25Cache[i0] = res; return res;
}
const P25_STAT = ['avg', 'alpha', 't'];
function grid() {
  const P = D.p25, s = +$('pg-s').value, y0 = +$('pg-y').value, i0 = firstOfYear(P.dates, y0), G = p25Stats(i0), key = P25_STAT[s];
  $('pg-y-v').textContent = P.dates[i0];
  const z = [0, 1, 2, 3, 4].map(i => [0, 1, 2, 3, 4].map(j => G.rows[5 * i + j][key])), sc = s === 2 ? 1 : 100;
  const txt = z.map(r => r.map(v => (sc * v).toFixed(1)));
  const ylab = ['ME1 (small)', 'ME2', 'ME3', 'ME4', 'ME5 (big)'], xlab = ['BM1 (growth)', 'BM2', 'BM3', 'BM4', 'BM5 (value)'];
  const zmax = Math.max(...z.flat().map(Math.abs));
  const cs = s === 0 ? [[0, '#FFFFFF'], [1, '#7B9BD6']] : [[0, '#E68080'], [0.5, '#FFFFFF'], [1, '#7B9BD6']];
  const name = ['Mean excess return (% a year)', 'CAPM alpha (% a year)', 't-statistic of the CAPM alpha (Newey-West)'][s];
  plot('pg-heat', [{ z, x: xlab, y: ylab, type: 'heatmap', colorscale: cs, zmin: s === 0 ? 0 : -zmax, zmax, text: txt, texttemplate: '%{text}', textfont: { size: 13, color: C.navy }, showscale: false,
    hovertemplate: '%{y}, %{x}: %{text}<extra></extra>' }],
  lay({ title: ttl(name + ', ' + per(P.dates, i0, P.dates.length - 1)), xaxis: AX('', { side: 'bottom' }), yaxis: AX('', { autorange: 'reversed' }) }));
  const spread = [0, 1, 2, 3, 4].map(i => sc * (z[i][4] - z[i][0]));
  plot('pg-bar', [{ x: ylab, y: spread, type: 'bar', name: 'BM5 minus BM1', marker: { color: spread.map(v => (v >= 0 ? K.blue : K.red)), line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }],
    lay({ showlegend: false, title: ttl('Value minus growth (BM5 − BM1), by size quintile'), shapes: [hline(0, C.navy)], xaxis: AX(''), yaxis: AX(s === 2 ? 'Difference of t-statistics' : 'Percentage points a year') }));
  const sg = G.rows[0], sv = G.rows[4];
  out('pg-out', [T.pg(per(P.dates, i0, P.dates.length - 1), T.months(G.n), pct(sg.avg, 1), pct(sg.alpha, 1), pct(sv.avg, 1), pct(sv.alpha, 1), G.rows.filter(r => Math.abs(r.t) > 1.96).length)]);
}

// ================================================================= security market line
function sml() {
  const P = D.p25, y0 = +$('sm-y').value, i0 = firstOfYear(P.dates, y0), G = p25Stats(i0), R = G.rows;
  $('sm-y-v').textContent = P.dates[i0];
  const b = R.map(r => r.beta), a = R.map(r => r.avg), f = olsNW(a, b.map(v => [v]), 0).b, xs = [0.8, 1.5];
  const small = P.names.map(c => c.startsWith('SMALL') || c.startsWith('ME1'));
  plot('sm-sml', [
    { x: b, y: a, text: P.names, mode: 'markers', name: '25 size × B/M portfolios', marker: { color: K.blue, size: 8 }, hovertemplate: '%{text}<br>beta %{x:.2f}<br>mean %{y:.1%}<extra></extra>' },
    { x: xs, y: xs.map(v => G.prem * v), mode: 'lines', name: `CAPM SML (slope = ${(100 * G.prem).toFixed(1)}%)`, line: { color: K.red, dash: 'dash', width: 2 }, hoverinfo: 'skip' },
    { x: xs, y: xs.map(v => f[0] + f[1] * v), mode: 'lines', name: `Fitted line (slope = ${(100 * f[1]).toFixed(1)}%)`, line: { color: K.green, width: 2 }, hoverinfo: 'skip' }
  ], lay({ title: ttl('Security market line'), xaxis: AX('CAPM beta', { range: [0.75, 1.55] }), yaxis: AX('Mean excess return (ann.)', { tickformat: '.0%' }) }));
  plot('sm-alpha', [
    { x: b.filter((_, i) => small[i]), y: R.filter((_, i) => small[i]).map(r => r.alpha), text: P.names.filter((_, i) => small[i]), mode: 'markers', name: 'Smallest-size quintile', marker: { color: K.crimson, size: 8 }, hovertemplate: '%{text}<br>beta %{x:.2f}<br>alpha %{y:.1%}<extra></extra>' },
    { x: b.filter((_, i) => !small[i]), y: R.filter((_, i) => !small[i]).map(r => r.alpha), text: P.names.filter((_, i) => !small[i]), mode: 'markers', name: 'Other portfolios', marker: { color: K.blue, size: 8 }, hovertemplate: '%{text}<br>beta %{x:.2f}<br>alpha %{y:.1%}<extra></extra>' }
  ], lay({ title: ttl(`Alphas: GRS = ${G.grs.toFixed(2)}, p ${G.p < 0.001 ? '< 0.001' : '= ' + G.p.toFixed(3)}`), shapes: [hline(0, C.navy)], xaxis: AX('CAPM beta', { range: [0.75, 1.55] }), yaxis: AX('CAPM alpha (ann.)', { tickformat: '.0%' }) }));
  out('sm-out', [T.sm1(per(P.dates, i0, P.dates.length - 1), G.n, pct(G.prem, 1), pct(f[1], 1), nf(Math.min(...b), 2), nf(Math.max(...b), 2)),
    T.sm2(nf(G.grs, 2), fmtP(G.p), R.filter(r => Math.abs(r.t) > 1.96).length)]);
}

// ================================================================= cumulative factor returns
const FC = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM'], FC_COL = [K.blue, K.teal, K.red, K.green, K.purple, K.orange];
function factorCum() {
  const F = D.fc, y0 = +$('fc-y').value, i0 = firstOfYear(F.dates, y0), last = F.dates.length - 1;
  $('fc-y-v').textContent = F.dates[i0];
  const W = FC.map(c => { let w = 1; return F.f[c].slice(i0).map(r => (w *= 1 + r)); });
  plot('fc-chart', FC.map((c, k) => ({ x: F.dates.slice(i0), y: W[k], mode: 'lines', name: c, line: { color: FC_COL[k], width: 1.4 }, hovertemplate: c + ' %{x}: %{y:.2f}<extra></extra>' })),
    lay({ title: ttl(`Excess and long-short factor returns, ${per(F.dates, i0, last)} (Kenneth French data)`), xaxis: AX(''), yaxis: AX('Growth of 1 (log scale)', { type: 'log', tickvals: [0.2, 0.5, 1, 2, 5, 10, 20, 50, 100], ticktext: ['0.2', '0.5', '1', '2', '5', '10', '20', '50', '100'] }) }));
  const L = FC.map((c, k) => ({ c, v: W[k][W[k].length - 1], m: 12 * mean(F.f[c].slice(i0)) })).sort((a, b) => b.v - a.v);
  out('fc-out', [T.fc(per(F.dates, i0, last), L.map(o => T.fcItem(o.c, nf(o.v, 1), pct(o.m, 1))).join('; '))]);
}

// ================================================================= Fama-MacBeth
const FM_MODELS = { CAPM: ['Mkt-RF'], FF3: ['Mkt-RF', 'SMB_FF3', 'HML'], FF5: ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'] }, FM_COL = { CAPM: K.blue, FF3: K.amber, FF5: K.green };
const fmCache = {};
function famaMacBeth(i0, fac) {
  const P = D.p25, Rm = P.R.map(r => r.slice(i0)), n = Rm[0].length, N = Rm.length, Kf = fac.length;
  const Xf = Rm[0].map((_, t) => fac.map(c => P.f[c][i0 + t]));
  const Bt = Rm.map(y => olsNW(y, Xf, 0).b.slice(1));                 // pass 1: N x K betas
  const Z = Bt.map(b => [1, ...b]), ZZ = Z[0].map((_, i) => Z[0].map((__, j) => sum(Z.map(r => r[i] * r[j])))), Hm = inv(ZZ).map(r => Z.map(z => dot(r, z)));
  const lam = Rm[0].map((_, t) => Hm.map(h => { let s = 0; for (let i = 0; i < N; i++) s += h[i] * Rm[i][t]; return s; }));   // pass 2: T x (1+K)
  const m = lam[0].map((_, j) => mean(lam.map(l => l[j])));
  const seFM = m.map((mj, j) => Math.sqrt(lam.reduce((s, l) => s + (l[j] - mj) ** 2, 0) / (n - 1) / n));
  const seNW = m.map((_, j) => olsNW(lam.map(l => l[j]), null, 6).se[0]);
  const Sf = fac.map((_, a) => fac.map((__, b) => cov1(Xf.map(x => x[a]), Xf.map(x => x[b])))), lf = m.slice(1), c = dot(lf, solve(Sf, lf));
  const sfd = [0, ...fac.map((_, a) => Sf[a][a])].map(v => v / n);
  const seSh = seFM.map((s, j) => Math.sqrt((1 + c) * (s * s - sfd[j]) + sfd[j]));
  const fmean = fac.map((_, a) => 12 * mean(Xf.map(x => x[a])));
  return { lam: m.map(v => 12 * v), se: { fm: seFM.map(v => 12 * v), nw: seNW.map(v => 12 * v), sh: seSh.map(v => 12 * v) }, fmean, bmk: Bt.map(b => b[0]), names: ['const', ...fac.map(f => (f === 'SMB_FF3' ? 'SMB' : f))] };
}
function fm() {
  const P = D.p25, y0 = +$('fm-y').value, i0 = firstOfYear(P.dates, y0), se = $('fm-se').value;
  $('fm-y-v').textContent = P.dates[i0];
  if (!fmCache[i0]) fmCache[i0] = Object.fromEntries(Object.entries(FM_MODELS).map(([k, f]) => [k, famaMacBeth(i0, f)]));
  const Rz = fmCache[i0], tr = [], ticks = [], labs = [], fx = [], fy = [];
  let x0 = 0;
  for (const k of Object.keys(FM_MODELS)) {
    const r = Rz[k], xs = r.lam.map((_, j) => x0 + j);
    tr.push({ x: xs, y: r.lam, mode: 'markers', name: k, marker: { color: FM_COL[k], size: 8 }, error_y: { type: 'data', array: r.se[se].map(v => 1.96 * v), color: FM_COL[k], thickness: 1.5, width: 4 },
      text: r.names.map((nm, j) => `${k}: ${nm}<br>premium ${(100 * r.lam[j]).toFixed(1)}%<br>SE ${(100 * r.se[se][j]).toFixed(1)}%`), hovertemplate: '%{text}<extra></extra>' });
    ticks.push(...xs); labs.push(...r.names); r.fmean.forEach((v, j) => { fx.push(x0 + j + 1); fy.push(v); });
    x0 += r.lam.length + 1;
  }
  tr.push({ x: fx, y: fy, mode: 'markers', name: 'Time-series mean of the factor', marker: { color: K.purple, size: 9, symbol: 'x' }, hovertemplate: 'factor mean %{y:.1%}<extra></extra>' });
  const seName = { sh: 'Shanken', fm: 'Fama-MacBeth', nw: 'Newey-West' }[se];
  plot('fm-chart', tr, lay({ title: ttl(`Fama-MacBeth risk premia on 25 size × B/M portfolios, ${per(P.dates, i0, P.dates.length - 1)}`), shapes: [hline(0, C.navy)],
    xaxis: AX('', { tickvals: ticks, ticktext: labs, tickangle: -45, tickfont: { size: 10, color: C.navy }, zeroline: false }), yaxis: AX(`Premium (ann.), 95% CI (${seName})`, { tickformat: '.0%' }) }));
  const F3 = Rz.FF3, bm = Rz.FF3.bmk;
  out('fm-out', [T.fm(per(P.dates, i0, P.dates.length - 1), T.fmSE[se], pct(F3.lam[1], 1), pct(F3.fmean[0], 1), pct(F3.lam[3], 1), pct(F3.fmean[2], 1), nf(Math.min(...bm), 2), nf(Math.max(...bm), 2)),
    T.fmCapm(pct(Rz.CAPM.lam[0], 1), pct(Rz.CAPM.se[se][0], 2), pct(Rz.CAPM.lam[1], 1), pct(Rz.CAPM.se[se][1], 2))]);
}

// ================================================================= PCA of the sector ETFs
function pca() {
  const P = D.pca, S = D.sectors_all, wv = $('pc-w').value, n = P.dates.length;
  $('pc-t').disabled = wv === 'all';
  let i1 = +$('pc-t').value, i0;
  if (wv === 'all') { i0 = 0; i1 = n - 1; } else { const w = +wv; i1 = Math.max(i1, w - 1); i0 = i1 - w + 1; }
  $('pc-t-v').textContent = P.dates[i1];
  const X = P.R.map(r => r.slice(i0, i1 + 1)), m = X.length, T0 = X[0].length;
  const Zs = X.map(x => { const mu = mean(x), sd = Math.sqrt(cov1(x, x)); return x.map(v => (v - mu) / sd); });
  const Cm = Zs.map(a => Zs.map(b => dot(a, b) / (T0 - 1)));
  const { vals, vecs } = eigSymV(Cm);
  for (let k = 0; k < m; k++) { if (sum(vecs.map(r => r[k])) < 0) vecs.forEach(r => (r[k] *= -1)); }
  const share = vals.map(v => v / sum(vals)), cum = share.map((_, i) => sum(share.slice(0, i + 1))), kk = share.map((_, i) => i + 1);
  const pc1 = Zs[0].map((_, t) => Zs.reduce((s, z, i) => s + z[t] * vecs[i][0], 0)), rc = corr(pc1, P.spy.slice(i0, i1 + 1));
  plot('pc-scree', [
    { x: kk, y: share, type: 'bar', name: 'Share of variance', marker: { color: K.blue, line: { color: '#fff', width: 1.5 } }, hovertemplate: 'PC%{x}: %{y:.1%}<extra></extra>' },
    { x: kk, y: cum, mode: 'lines+markers', name: 'Cumulative', line: { color: K.red, width: 2 }, marker: { size: 6 }, hovertemplate: 'PC1–%{x}: %{y:.1%}<extra></extra>' }
  ], lay({ title: ttl(`Scree plot, ${per(P.dates, i0, i1)}`), xaxis: AX('Principal component', { dtick: 1 }), yaxis: AX('Share of total variance', { tickformat: '.0%', range: [0, 1.02] }) }));
  plot('pc-load', [0, 1, 2].map(j => ({ x: S, y: vecs.map(r => r[j]), type: 'bar', name: 'PC' + (j + 1), marker: { color: [K.blue, K.red, K.green][j], line: { color: '#fff', width: 1 } }, hovertemplate: 'PC' + (j + 1) + ', %{x}: %{y:.2f}<extra></extra>' })),
    lay({ barmode: 'group', bargap: 0.2, title: ttl('Loadings of the first three components'), shapes: [hline(0, C.navy)], xaxis: AX('', { tickangle: -45 }), yaxis: AX('Loading (eigenvector)', { range: [-0.8, 0.8] }) }));
  out('pc-out', [T.pc(per(P.dates, i0, i1), T.days(T0), pct(share[0], 1), pct(share[1], 1), pct(share[2], 1), pct(cum[2], 1), nf(rc, 3))]);
}

// ================================================================= factor ETFs
const FE_NAME = { MTUM: 'Momentum', VLUE: 'Value', QUAL: 'Quality', USMV: 'Min. volatility', IWM: 'Small caps', IWD: 'Large value', IWF: 'Large growth', SPY: 'S&P 500' };
const FE_COL = { MTUM: K.blue, VLUE: K.red, QUAL: K.green, USMV: K.teal, IWM: K.orange, IWD: K.purple, IWF: K.amber, SPY: C.navy };
function factorEtfs() {
  const E = D.etf, k = +$('fe-t').value, last = E.dates.length - 1;
  $('fe-t-v').textContent = E.dates[k];
  plot('fe-chart', E.names.map((s, j) => ({ x: E.dates.slice(k), y: E.W[j].slice(k).map(v => v / E.W[j][k]), mode: 'lines', name: `${s} (${FE_NAME[s]})`,
    line: { color: FE_COL[s], width: s === 'SPY' ? 2.2 : 1.2, dash: s === 'IWD' || s === 'IWF' ? 'dash' : 'solid' }, hovertemplate: s + ' %{x}: %{y:.2f}<extra></extra>' })),
  lay({ title: ttl(`Factor ETFs vs the S&P 500, ${per(E.dates, k, last)}`), xaxis: AX(''), yaxis: AX('Growth of 1 USD (total return)') }));
  const yrs = (new Date(E.dates[last]) - new Date(E.dates[k])) / 864e5 / 365.25;
  const L = E.names.map((s, j) => ({ s, g: Math.pow(E.W[j][last] / E.W[j][k], 1 / yrs) - 1 })).sort((a, b) => b.g - a.g);
  out('fe-out', [T.fe(E.dates[k], E.dates[last], L.map(o => `${o.s} ${pct(o.g, 1)}`).join(', '))]);
}

// ================================================================= case study: factor momentum (Ehsani & Linnainmaa, 2022)
// signal = compounded return over months t-L ... t-1; TSFM_t = mean_i sign(signal_i,t) r_i,t (sign 0 counts as negative)
function tfStats(L, i0) {
  const P = D.tf, N = P.names.length, n = P.dates.length, R = P.names.map(c => P.f[c]);
  const start = Math.max(i0, L), idx = range(start, n - 1, 1);
  const up = P.names.map(() => []), dn = P.names.map(() => []), ts = [], yv = [], dv = [], gv = [];
  idx.forEach((t, k) => {
    let s = 0;
    for (let i = 0; i < N; i++) {
      let w = 1;
      for (let l = 1; l <= L; l++) w *= 1 + R[i][t - l] / 100;
      const pos = w - 1 > 0, r = R[i][t];
      (pos ? up : dn)[i].push(r); s += (pos ? 1 : -1) * r;
      yv.push(r); dv.push(pos ? 1 : 0); gv.push(k);
    }
    ts.push(s / N);
  });
  // pooled difference, standard errors clustered by month
  const n1 = sum(dv), n0 = dv.length - n1, m0 = sum(yv.filter((_, j) => !dv[j])) / n0, m1 = sum(yv.filter((_, j) => dv[j])) / n1;
  const XtX = [[dv.length, n1], [n1, n1]], Xi = inv(XtX), Sg = [[0, 0], [0, 0]], sc = idx.map(() => [0, 0]);
  yv.forEach((y, j) => { const e = y - (dv[j] ? m1 : m0); sc[gv[j]][0] += e; sc[gv[j]][1] += dv[j] * e; });
  sc.forEach(v => { for (let a = 0; a < 2; a++) for (let b = 0; b < 2; b++) Sg[a][b] += v[a] * v[b]; });
  const mm = (A, B) => A.map(r => B[0].map((_, j) => r.reduce((s, v, m) => s + v * B[m][j], 0))), V = mm(Xi, mm(Sg, Xi));
  const mom = idx.map(t => P.f.MOM[t]), ff5 = idx.map(t => ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'].map(c => P.f[c][t]));
  const sd = a => { const m = mean(a); return Math.sqrt(sum(a.map(v => (v - m) * (v - m))) / (a.length - 1)); };
  const sr = a => mean(a) / sd(a) * Math.sqrt(12);
  return { idx, up: up.map(mean), dn: dn.map(mean), pdn: m0, pup: m1, diff: m1 - m0, tdiff: (m1 - m0) / Math.sqrt(V[1][1]),
    nf: up.filter((u, i) => mean(u) > mean(dn[i])).length, ts, mom, tsT: olsNW(ts).t[0], tsM: mean(ts), sr: sr(ts), srm: sr(mom),
    a0: olsNW(mom, ff5), a1: olsNW(mom, ff5.map((r, k) => [...r, ts[k]])) };
}
function factorMom() {
  const P = D.tf, L = +$('tf-L').value, y0 = +$('tf-y').value;
  $('tf-L-v').textContent = L; $('tf-y-v').textContent = y0;
  const i0 = P.dates.indexOf(y0 + '-07'), S = tfStats(L, i0), dts = S.idx.map(t => P.dates[t]);
  const names = [...P.names, 'Average factor'];
  plot('tf-bar', [
    { x: names, y: [...S.dn, S.pdn], type: 'bar', name: 'After a negative signal', marker: { color: K.red }, hovertemplate: '%{x}: %{y:.2f}% a month<extra></extra>' },
    { x: names, y: [...S.up, S.pup], type: 'bar', name: 'After a positive signal', marker: { color: K.green }, hovertemplate: '%{x}: %{y:.2f}% a month<extra></extra>' }
  ], lay({ barmode: 'group', bargap: 0.25, title: ttl(`Factor returns after a positive or negative prior ${L}-month return`), shapes: [hline(0, C.navy)],
    xaxis: AX('', { tickangle: -30 }), yaxis: AX('Mean return, % a month') }));
  const cum = a => { let w = 1; return a.map(v => (w *= 1 + v / 100)); };
  plot('tf-cum', [
    { x: dts, y: cum(S.ts), mode: 'lines', name: 'Factor momentum (TSFM)', line: { color: K.blue, width: 1.5 }, hovertemplate: 'TSFM %{x}: %{y:.2f}<extra></extra>' },
    { x: dts, y: cum(S.mom), mode: 'lines', name: 'Stock momentum (MOM)', line: { color: K.orange, width: 1.5 }, hovertemplate: 'MOM %{x}: %{y:.2f}<extra></extra>' }
  ], lay({ title: ttl(`Growth of 1, ${dts[0]} to ${dts[dts.length - 1]}`), xaxis: AX(''), yaxis: AX('Growth of 1 (log scale)', { type: 'log', tickvals: [0.5, 1, 2, 5, 10, 20, 50, 100], ticktext: ['0.5', '1', '2', '5', '10', '20', '50', '100'] }) }));
  const p2 = v => nf(v, 2) + '%';
  out('tf-out', [T.tf1(`${dts[0]} – ${dts[dts.length - 1]}, T = ${dts.length}`, L, dts.length, p2(S.pdn), p2(S.pup), nf(S.diff, 2), nf(S.tdiff, 2), S.nf),
    T.tf2(p2(S.tsM), nf(S.tsT, 2), nf(S.sr, 2), nf(S.srm, 2), p2(S.a0.b[0]), nf(S.a0.t[0], 2), p2(S.a1.b[0]), nf(S.a1.t[0], 2))]);
}

// ================================================================= AI mini-case: momentum after publication
function aiFit(y, ps0, pub) {
  const X = y.map((_, t) => [t >= ps0 && t < pub ? 1 : 0, t >= pub ? 1 : 0]), r = olsNW(y, X), V = r.V;
  const inc = r.b[2] - r.b[1], seI = Math.sqrt(V[2][2] + V[1][1] - 2 * V[1][2]);
  const pm = c => ({ m: dot(c, r.b), se: Math.sqrt(quad(c, V)) });
  return { r, inc, seI, per: [pm([1, 0, 0]), pm([1, 1, 0]), pm([1, 0, 1])] };
}
function ai() {
  const A = D.ai, pub = +$('ai-p').value, ps0 = pub - 39, dt = A.dates;
  $('ai-p-v').textContent = dt[pub];
  const M = aiFit(A.MOM, ps0, pub), P = aiFit(A.MKT, ps0, pub);
  const labs = [`In sample<br>${dt[0]} – ${dt[ps0 - 1]}`, `Post-sample<br>${dt[ps0]} – ${dt[pub - 1]}`, `Post-publication<br>${dt[pub]} – ${dt[dt.length - 1]}`], cols = [K.blue, K.amber, K.red];
  plot('ai-per', M.per.map((p, k) => ({ x: [k], y: [p.m], mode: 'markers+text', text: [p.m.toFixed(2) + '%'], textposition: 'middle right', textfont: { color: C.navy }, name: labs[k].split('<br>')[0], showlegend: false,
    marker: { color: cols[k], size: 10 }, error_y: { type: 'data', array: [1.96 * p.se], color: cols[k], thickness: 1.5, width: 6 }, hovertemplate: `%{y:.2f}% ± ${(1.96 * p.se).toFixed(2)}<extra></extra>` })),
  lay({ title: ttl('Momentum by period, 95% intervals (Newey-West)'), shapes: [hline(0, C.navy, 'dot')], xaxis: AX('', { tickvals: [0, 1, 2], ticktext: labs, range: [-0.4, 2.75], tickfont: { size: 10, color: C.navy }, zeroline: false }), yaxis: AX('MOM mean, % a month') }));
  const rows = ['Total decline b₂', 'Incremental b₂ − b₁'];
  const est = F => [{ e: F.r.b[2], s: F.r.se[2] }, { e: F.inc, s: F.seI }];
  plot('ai-dec', [['MOM', M, K.blue, 'circle', 0.12], ['Mkt-RF (placebo)', P, K.green, 'square', -0.12]].map(([nm, F, col, sym, off]) => {
    const v = est(F);
    return { x: v.map(o => o.e), y: [1 + off, off], mode: 'markers', name: nm, marker: { color: col, size: 9, symbol: sym }, error_x: { type: 'data', array: v.map(o => 1.96 * o.s), color: col, thickness: 1.5, width: 5 },
      text: rows, hovertemplate: nm + ', %{text}: %{x:.2f}%<extra></extra>' };
  }), lay({ title: ttl('Decline estimates, 95% intervals'), shapes: [vline(0, C.navy, 'dot')], xaxis: AX('% a month'), yaxis: AX('', { tickvals: [1, 0], ticktext: rows, range: [-0.6, 1.6] }) }));
  const a = M.r.b[0];
  out('ai-out', [T.ai1(dt[pub], nf(a, 2) + '%', nf(M.r.t[0], 2), nf(M.r.b[2], 2) + '%', nf(M.r.t[2], 2), pct(-M.r.b[2] / a, 0), nf(M.inc, 2) + '%', nf(M.inc / M.seI, 2)),
    T.ai2(nf(P.r.b[2], 2) + '%', nf(P.r.t[2], 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  const nfr = D.fr.dates.length - 1;
  $('fr-t').max = nfr; $('fr-t').value = nfr; on(['fr-t'], frontier); P('fr-play', 'fr-t', range(60, nfr, 6), 220);
  on(['xk-b', 'xk-L'], xlk); $('xk-res').style.gridColumn = '1 / -1'; $('xk-res').style.height = '280px'; P('xk-play', 'xk-b', range(1, 24, 1), 700);
  on(['dm-p', 'dm-b'], dimson); P('dm-play', 'dm-p', range(0.3, 1, 0.05), 400);
  on(['rb-w'], rolling); P('rb-play', 'rb-w', range(0, 4, 1), 1500);
  on(['pg-s', 'pg-y'], grid); P('pg-play', 'pg-s', [0, 1, 2], 1800);
  on(['sm-y'], sml); P('sm-play', 'sm-y', range(1963, 2006, 1), 450);
  on(['fc-y'], factorCum); P('fc-play', 'fc-y', range(1963, 2016, 1), 300);
  on(['fm-y', 'fm-se'], fm); P('fm-play', 'fm-y', range(1963, 2000, 1), 450);
  const npc = D.pca.dates.length - 1; $('pc-t').max = npc; $('pc-t').value = npc;
  on(['pc-w', 'pc-t'], pca); P('pc-play', 'pc-t', range(251, npc, 20), 160);
  $('pc-play').addEventListener('click', () => { if ($('pc-w').value === 'all') { $('pc-w').value = '252'; } }, true);
  $('fe-t').max = D.etf.dates.length - 253; on(['fe-t'], factorEtfs); P('fe-play', 'fe-t', range(0, D.etf.dates.length - 253, 21), 120);
  const ia = D.ai.dates.indexOf('1993-04'); $('ai-p').min = D.ai.dates.indexOf('1975-01'); $('ai-p').max = D.ai.dates.indexOf('2015-01'); $('ai-p').value = ia;
  on(['tf-L', 'tf-y'], factorMom); P('tf-play', 'tf-L', range(1, 36, 1), 600);
  on(['ai-p'], ai); P('ai-play', 'ai-p', range(D.ai.dates.indexOf('1975-01'), D.ai.dates.indexOf('2015-01'), 6), 250);
  const PFX = { 'frontier': 'fr', 'xlk-beta': 'xk', 'dimson': 'dm', 'rolling-beta': 'rb', 'test-assets': 'pg', 'sml': 'sm', 'factor-returns': 'fc',
    'fama-macbeth': 'fm', 'pca': 'pc', 'factor-etfs': 'fe', 'factor-momentum': 'tf', 'momentum-decay': 'ai' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  frontier(); xlk(); dimson(); rolling(); grid(); sml(); factorCum(); fm(); pca(); factorEtfs(); factorMom(); ai();
}
window.CH3 = { olsNW, fUpper, eigSymV, p25Stats, famaMacBeth, bootAlpha, rollBeta, aiFit, tfStats };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

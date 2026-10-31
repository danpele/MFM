// Chapter 7 interactive page: one block per chart slide, computed in the browser from ch7_data.js.
(function () {
'use strict';
const D = window.CH7_DATA;
const { C, sum, mean, nf, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH7_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', teal: '#17A2B8', navy: '#1F2A44' };
const MCOL = { 'HS': K.blue, 'Normal': K.orange, 'Student-t': K.green, 'Cornish-Fisher': K.purple, 'EVT (GPD)': K.red };
const ACOL = { sp500: K.blue, bet: K.red, btc: K.amber, eurron: K.green, gold: K.purple };
const FILL = 'rgba(23,162,184,0.45)', HISTC = 'rgba(26,58,110,0.55)';
const METHODS = ['HS', 'Normal', 'Student-t', 'Cornish-Fisher', 'EVT (GPD)'];

// ---------------------------------------------------------------- helpers
const p2 = (x, d = 2) => nf(x, d) + '%';                       // a number already in %
const ap = a => { const v = 100 * a, d = Math.abs(v - Math.round(v)) < 1e-9 ? 0 : Math.abs(10 * v - Math.round(10 * v)) < 1e-9 ? 1 : 2; return nf(v, d) + '%'; };
const ni = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, window.MFM_LANG === 'ro' ? '\u00a0' : ',');
const day = d => new Date(Date.UTC(2000, 0, 1) + d * 864e5).toISOString().slice(0, 10);
const sorted = a => Float64Array.from(a).sort();
function quant(s, p) { const pos = (s.length - 1) * p, lo = Math.floor(pos), hi = Math.min(lo + 1, s.length - 1); return s[lo] + (pos - lo) * (s[hi] - s[lo]); }
// historical ES = integral of the empirical quantile function: weight 1 on the floor(n a) largest losses, n a - floor(n a) on the next one
function hsVarEs(s, a) { const N = s.length, v = quant(s, 1 - a), na = N * a, m = Math.floor(na + 1e-9), fr = Math.max(na - m, 0);
  let t = 0, nb = 0; for (let i = 0; i < m; i++) t += s[N - 1 - i]; if (fr > 1e-12 && m < N) t += fr * s[N - 1 - m];
  for (let i = N - 1; i >= 0 && s[i] >= v; i--) nb++; return [v, t / na, nb, na]; }
const npdf = x => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
function nppf(p) {                                              // Acklam's rational approximation
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
const sdev1 = a => { const m = mean(a); let s = 0; for (const x of a) s += (x - m) ** 2; return Math.sqrt(s / (a.length - 1)); };
function gpdVarEs(f, a) { const v = f.u + f.beta / f.xi * (Math.pow(f.n / f.nu * a, -f.xi) - 1); return [v, v / (1 - f.xi) + (f.beta - f.xi * f.u) / (1 - f.xi)]; }
const ALOSS = {}; const lossSorted = k => ALOSS[k] || (ALOSS[k] = sorted(D.loss[k]));
const legendLow = (y) => ({ legend: { orientation: 'h', x: 0, xanchor: 'left', y: y || -0.22, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } } });
const ALPHA_LD = [0.05, 0.04, 0.03, 0.025, 0.02, 0.015, 0.01, 0.0075, 0.005, 0.0025, 0.001];

// ================================================================= loss distribution and VaR / ES
function lossDist() {
  const L = D.loss.sp500, s = lossSorted('sp500'), a = ALPHA_LD[+$('ld-a').value];
  $('ld-a-v').textContent = ap(a);
  const [v, e, nb] = hsVarEs(s, a), [, e25] = hsVarEs(s, 0.025);
  const m = mean(L), sd = sdev1(L), z = nppf(1 - a), vn = m + sd * z, en = m + sd * npdf(z) / a;
  const lo = Math.min(-8, Math.floor(s[0])), hi = Math.max(12, Math.ceil(s[s.length - 1])), w = (hi - lo) / 160;
  const xs = range(lo, hi, (hi - lo) / 600);
  const vl = (x, c, dash, name) => ({ x: [x, x], y: [0, 1], yaxis: 'y', xaxis: 'x', mode: 'lines', name, line: { color: c, width: 2, dash }, hoverinfo: 'skip' });
  plot('ld-dist', [
    { x: L, type: 'histogram', histnorm: 'probability density', xbins: { start: lo, end: hi, size: w }, name: 'S&P 500 daily losses, 2000-2026', marker: { color: HISTC }, hovertemplate: 'loss %{x}<br>density %{y:.3f}<extra></extra>' },
    { x: xs, y: xs.map(x => npdf((x - m) / sd) / sd), mode: 'lines', name: 'Normal distribution, same mean and s.d.', line: { color: K.orange, width: 2 }, hoverinfo: 'skip' }
  ], layout({ ...legendLow(), bargap: 0, title: ttl('Loss distribution'), shapes: [vline(v, K.red), vline(e, K.red, 'dash')],
    annotations: [{ x: v, y: 1, yref: 'paper', text: 'VaR ' + ap(a) + ' = ' + v.toFixed(2) + '%', showarrow: false, xanchor: 'left', xshift: 4, yanchor: 'top', font: { color: K.red, size: 11 } },
      { x: e, y: 0.88, yref: 'paper', text: 'ES ' + ap(a) + ' = ' + e.toFixed(2) + '%', showarrow: false, xanchor: 'left', xshift: 4, yanchor: 'top', font: { color: K.red, size: 11 } }],
    xaxis: AX('Daily loss L = -r (%)', { range: [lo, hi] }), yaxis: AX('Density') }));
  const tail = L.filter(x => x > 2), th = Math.max(12, Math.ceil(s[s.length - 1]));
  plot('ld-tail', [
    { x: tail, type: 'histogram', xbins: { start: 2, end: th, size: (th - 2) / 50 }, name: 'Losses above 2%', marker: { color: HISTC }, hovertemplate: '%{x}<br>%{y} days<extra></extra>' },
    vl(v, K.red, 'solid', 'VaR ' + ap(a)), vl(e, K.red, 'dash', 'ES ' + ap(a) + ' (average of the worst ' + ap(a) + ')'), vl(e25, K.amber, 'dashdot', 'ES 2.5% = ' + e25.toFixed(2) + '%')
  ].map((tr, i) => (i ? Object.assign(tr, { yaxis: 'y2' }) : tr)), layout({ ...legendLow(), bargap: 0, title: ttl('Right tail of the losses'),
    xaxis: AX('Daily loss (%)', { range: [2, th] }), yaxis: AX('Number of days'), yaxis2: { overlaying: 'y', range: [0, 1], visible: false } }));
  out('ld-out', [T.ld(ap(a), p2(v), nb, ni(L.length), p2(100 * nb / L.length), p2(e), p2(vn), p2(en))]);
}

// ================================================================= subadditivity: two bonds
function discreteVarEs(x, p, a) {
  const idx = x.map((_, i) => i).sort((i, j) => x[i] - x[j]), xs = idx.map(i => x[i]), ps = idx.map(i => p[i]);
  let c = 0, k = 0; const cdf = ps.map(q => (c += q));
  while (k < cdf.length - 1 && cdf[k] < 1 - a - 1e-12) k++;
  const v = xs[k]; let tl = 0, pt = 0;
  xs.forEach((y, i) => { if (y > v) { tl += y * ps[i]; pt += ps[i]; } });
  return [v, (tl + v * (a - pt)) / a];
}
function subadd() {
  const p = +$('sa-p').value / 100, a = 0.01, lgd = D.bonds.lgd;
  $('sa-p-v').textContent = p2(100 * p, 2);
  const [v1, e1] = discreteVarEs([0, lgd], [1 - p, p], a), [vp, ep] = discreteVarEs([0, lgd, 2 * lgd], [(1 - p) ** 2, 2 * p * (1 - p), p * p], a);
  const sums = [2 * v1, 2 * e1], port = [vp, ep], lab = ['VaR 1%', 'ES 1%'];
  plot('sa-chart', [
    { x: lab, y: sums, type: 'bar', name: 'Bond A + bond B, measured separately', marker: { color: K.blue }, text: sums.map(x => x.toFixed(1)), textposition: 'outside', hovertemplate: '%{x}: %{y:.1f}<extra></extra>' },
    { x: lab, y: port, type: 'bar', name: 'Portfolio A + B, measured jointly', marker: { color: K.red }, text: port.map(x => x.toFixed(1)), textposition: 'outside', hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }
  ], layout({ ...legendLow(-0.12), barmode: 'group', bargap: 0.3, title: ttl('Two independent bonds, default probability ' + (100 * p).toFixed(2) + '% each'),
    xaxis: AX(''), yaxis: AX('Risk (loss units)', { range: [0, 260] }) }));
  out('sa-out', [T.sa(p2(100 * p, 2), p2(100 * (1 - (1 - p) ** 2), 2), nf(2 * v1, 1), nf(vp, 1), nf(2 * e1, 1), nf(ep, 1), vp > 2 * v1 + 1e-9)]);
}

// ================================================================= five methods across levels
function varLevels() {
  const Lv = D.levels, A = Lv.alpha, k = +$('vl-a').value, a = A[k];
  $('vl-a-v').textContent = ap(a);
  const x = A.map(v => 100 * v), xa = AX('Tail probability alpha (%)', { type: 'log', autorange: 'reversed', tickvals: [5, 2.5, 1, 0.5, 0.1], ticktext: ['5', '2.5', '1', '0.5', '0.1'] });
  const tr = w => METHODS.map(m => ({ x, y: Lv[w][m], mode: 'lines', name: m, line: { color: MCOL[m], width: m === 'HS' ? 2.6 : 2 }, hovertemplate: m + ', α = %{x:.2f}%: %{y:.2f}%<extra></extra>' }))
    .concat([{ x: METHODS.map(() => 100 * a), y: METHODS.map(m => Lv[w][m][k]), mode: 'markers', showlegend: false, marker: { color: METHODS.map(m => MCOL[m]), size: 9, line: { color: '#fff', width: 1.5 } }, hoverinfo: 'skip' }]);
  const ym = Math.max(...METHODS.map(m => Math.max(...Lv.es[m]))) * 1.05;
  plot('vl-var', tr('var'), layout({ ...legendLow(), title: ttl('Value-at-Risk, S&P 500 2000-2026'), shapes: [vline(100 * a, K.navy, 'dot')], xaxis: xa, yaxis: AX('Daily loss (%)', { range: [0, ym] }) }));
  plot('vl-es', tr('es'), layout({ ...legendLow(), title: ttl('Expected Shortfall, S&P 500 2000-2026'), shapes: [vline(100 * a, K.navy, 'dot')], xaxis: xa, yaxis: AX('Daily loss (%)', { range: [0, ym] }) }));
  const li = w => METHODS.map(m => m + ' ' + p2(Lv[w][m][k])).join(', ');
  out('vl-out', [T.vl(ap(a), li('var'), li('es'))]);
}

// ================================================================= precision of VaR and ES
const PR_N = [250, 500, 750, 1000, 1500, 2000, 3000, 4000];
const PR_COL = { 'Asymptotic i.i.d.': K.teal, 'Asymptotic HAC': K.purple, 'i.i.d. bootstrap': K.blue, 'Block bootstrap (20 days)': K.red };
function precision() {
  const n = PR_N[+$('pr-n').value], F = D.prec[String(D.loss.sp500.length)], W = D.prec[String(n)];
  $('pr-n-v').textContent = n;
  const iv = (P, w) => (w === 'var' ? { 'Asymptotic i.i.d.': [P.var - 1.96 * P.se_var, P.var + 1.96 * P.se_var], 'Asymptotic HAC': [P.var - 1.96 * P.se_var_hac, P.var + 1.96 * P.se_var_hac] }
    : { 'Asymptotic i.i.d.': [P.es - 1.96 * P.se_es, P.es + 1.96 * P.se_es], 'Asymptotic HAC': [P.es - 1.96 * P.se_es_hac, P.es + 1.96 * P.se_es_hac], 'i.i.d. bootstrap': P.iid, 'Block bootstrap (20 days)': P.blk });
  const rows = [['VaR 1%<br>2000-2026', F.var, iv(F, 'var')], ['VaR 1%<br>last ' + n + ' days', W.var, iv(W, 'var')], ['ES 2.5%<br>2000-2026', F.es, iv(F, 'es')], ['ES 2.5%<br>last ' + n + ' days', W.es, iv(W, 'es')]];
  const off = { 'Asymptotic i.i.d.': 0.27, 'Asymptotic HAC': 0.09, 'i.i.d. bootstrap': -0.09, 'Block bootstrap (20 days)': -0.27 };
  const tr = Object.keys(PR_COL).map(m => {
    const x = [], y = [], cd = [];
    rows.forEach((rw, i) => { const q = rw[2][m]; if (!q) return; const yy = 3 - i + off[m]; x.push(q[0], q[1], null); y.push(yy, yy, null); cd.push(q[1] - q[0], q[1] - q[0], null); });
    return { x, y, customdata: cd, mode: 'lines', name: m, line: { color: PR_COL[m], width: 6 }, hovertemplate: m + '<br>%{x:.2f}%, width %{customdata:.2f} pp<extra></extra>' };
  });
  const ex = [], ey = []; rows.forEach((rw, i) => { ex.push(rw[1], rw[1], null); ey.push(3 - i - 0.38, 3 - i + 0.38, null); });
  tr.push({ x: ex, y: ey, mode: 'lines', name: 'Estimate', line: { color: K.navy, width: 2 }, hoverinfo: 'skip' });
  const xmax = Math.max(4.9, ...rows.map(rw => Math.max(...Object.values(rw[2]).map(q => q[1])) + 0.1)), xmin = Math.min(1.4, ...rows.map(rw => Math.min(...Object.values(rw[2]).map(q => q[0])) - 0.1));
  plot('pr-chart', tr, layout({ ...legendLow(-0.16), title: ttl('S&P 500: 95% confidence intervals'), margin: { l: 110, r: 12, t: 30, b: 40 },
    xaxis: AX('Daily loss (%); navy tick = estimate', { range: [xmin, xmax] }), yaxis: AX('', { tickvals: [3, 2, 1, 0], ticktext: rows.map(rw => rw[0]), range: [-0.6, 3.6], zeroline: false }) }));
  const na = hsVarEs(sorted(D.loss.sp500.slice(-n)), 0.025)[3], k = nf(na, Math.abs(na - Math.round(na)) < 1e-9 ? 0 : Math.abs(10 * na - Math.round(10 * na)) < 1e-9 ? 1 : 2);
  const wd = q => nf(q[1] - q[0], 2);
  out('pr-out', [T.pr(ni(n), k, wd(iv(W, 'var')['Asymptotic HAC']), wd(iv(W, 'es')['Asymptotic HAC']), wd(W.blk), wd(iv(F, 'es')['Asymptotic i.i.d.']), wd(iv(F, 'es')['Asymptotic HAC']), wd(F.iid), wd(F.blk))]);
}

// ================================================================= conditional VaR, S&P 500 2006-2026
const R = D.roll, RS = R.start, RN = R.mu.length, SPL = D.loss.sp500;
const RDATE = Array.from({ length: RN }, (_, j) => day(D.sp_days[RS + j]));
const RYEAR = []; R.years.forEach((y, i) => { for (let j = 0; j < y.n; j++) RYEAR.push(i); });
const ROLL_A = [0.05, 0.025, 0.01, 0.005, 0.0025, 0.001];
const condCache = {};
function cond(a) {                                     // FHS, conditional EVT and GARCH-Normal VaR / ES at level a
  if (condCache[a]) return condCache[a];
  const ka = R.alphas.findIndex(x => Math.abs(x - a) < 1e-12), z = nppf(1 - a), ez = npdf(z) / a;
  const Y = R.years.map(y => { const [gv, ge] = gpdVarEs(y.gpd, a); return { q: y.fhs_q[ka], e: y.fhs_e[ka], gv, ge }; });
  const o = { fv: [], fe: [], cv: [], ce: [], nv: [], ne: [] };
  for (let j = 0; j < RN; j++) {
    const m = -R.mu[j], s = R.sigma[j], y = Y[RYEAR[j]];
    o.fv.push(m + s * y.q); o.fe.push(m + s * y.e); o.cv.push(m + s * y.gv); o.ce.push(m + s * y.ge); o.nv.push(m + s * z); o.ne.push(m + s * ez);
  }
  return (condCache[a] = o);
}
const hsCache = {};
function rollHS(a, w) {                                // historical simulation on the w days before each day
  const key = a + ':' + w; if (hsCache[key]) return hsCache[key];
  const win = Array.from(SPL.slice(RS - w, RS)).sort((x, y) => x - y), res = new Float64Array(RN);
  const ins = x => { let lo = 0, hi = win.length; while (lo < hi) { const md = (lo + hi) >> 1; if (win[md] < x) lo = md + 1; else hi = md; } win.splice(lo, 0, x); };
  const del = x => { let lo = 0, hi = win.length; while (lo < hi) { const md = (lo + hi) >> 1; if (win[md] < x) lo = md + 1; else hi = md; } win.splice(lo, 1); };
  for (let j = 0; j < RN; j++) { res[j] = quant(win, 1 - a); ins(SPL[RS + j]); del(SPL[RS + j - w]); }
  return (hsCache[key] = res);
}
const lossPos = (i0, i1) => SPL.slice(RS + i0, RS + i1 + 1).map(x => Math.max(x, 0));
function hsFhs() {
  const a = +$('hf-a').value, w = +$('hf-w').value, k = +$('hf-t').value;
  $('hf-t-v').textContent = RDATE[k];
  const c = cond(a), hs = rollHS(a, w), x = RDATE.slice(0, k + 1), Lk = SPL.slice(RS, RS + k + 1);
  const eh = [], ef = []; let nh = 0, nfh = 0, ng = 0;
  for (let j = 0; j <= k; j++) { const l = Lk[j]; if (l > hs[j]) { eh.push(j); nh++; } if (l > c.fv[j]) { ef.push(j); nfh++; } if (l > c.nv[j]) ng++; }
  const ymax = 1.08 * Math.max(...SPL.slice(RS), ...c.fv);
  plot('hf-chart', [
    { x, y: lossPos(0, k), mode: 'lines', name: 'Daily loss (gains set to 0)', line: { color: FILL, width: 0.6 }, fill: 'tozeroy', fillcolor: FILL, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x, y: Array.from(hs.slice(0, k + 1)), mode: 'lines', name: 'HS VaR ' + ap(a) + ' (' + w + '-day window)', line: { color: K.blue, width: 1.6 }, hovertemplate: '%{x}: HS %{y:.2f}%<extra></extra>' },
    { x, y: c.fv.slice(0, k + 1), mode: 'lines', name: 'FHS VaR ' + ap(a) + ' (GARCH-filtered)', line: { color: K.red, width: 1 }, hovertemplate: '%{x}: FHS %{y:.2f}%<extra></extra>' },
    { x: eh.map(j => RDATE[j]), y: eh.map(j => Lk[j]), mode: 'markers', name: 'Loss above HS VaR', marker: { color: K.blue, size: 4 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: ef.map(j => RDATE[j]), y: ef.map(j => Lk[j]), mode: 'markers', name: 'Loss above FHS VaR', marker: { color: K.red, size: 6, symbol: 'x' }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ ...legendLow(-0.12), title: ttl('S&P 500, 2006-2026: historical vs filtered historical simulation'), xaxis: AX('', { type: 'date', range: [RDATE[0], RDATE[RN - 1]] }), yaxis: AX('Daily loss (%)', { range: [0, ymax] }) }));
  let fm = 0, fd = 0; for (let j = 0; j <= k; j++) if (c.fv[j] > fm) { fm = c.fv[j]; fd = j; }
  const n = k + 1;
  out('hf-out', [T.hf(RDATE[k], ni(n), ap(a), p2(100 * nh / n), nh, p2(100 * nfh / n), nfh, p2(100 * ng / n), w), T.hfm(p2(fm), RDATE[fd])]);
}

// ================================================================= CAViaR (SAV) against FHS
const CV = D.caviar, SPR = SPL.map(x => -x), CV_OOS = D.sp_days.findIndex(d => day(d) >= '2016-01-01');
const CV_M = mean(SPR.slice(0, CV.n_est).map(Math.abs)), CV_LEVEL = (CV.b[0] + CV.b[2] * CV_M) / (1 - CV.b[1]);
function caviarPath(b0, b1, b2) { const v = new Float64Array(SPR.length); v[0] = CV.v0; for (let t = 1; t < SPR.length; t++) v[t] = b0 + b1 * v[t - 1] + b2 * Math.abs(SPR[t - 1]); return v; }
function caviar() {
  const s1 = +$('cv-b1').value, s2 = +$('cv-b2').value;
  const b1 = Math.abs(s1 - +CV.b[1].toFixed(3)) < 1e-9 ? CV.b[1] : s1, b2 = Math.abs(s2 - +CV.b[2].toFixed(3)) < 1e-9 ? CV.b[2] : s2;
  const b0 = b1 === CV.b[1] && b2 === CV.b[2] ? CV.b[0] : CV_LEVEL * (1 - b1) - b2 * CV_M;
  $('cv-b1-v').textContent = nf(b1, 3); $('cv-b2-v').textContent = nf(b2, 3);
  const v = caviarPath(b0, b1, b2), c = cond(0.01), j0 = CV_OOS - RS, a = 0.01;
  const x = RDATE.slice(j0), vv = Array.from(v.slice(CV_OOS)), fv = c.fv.slice(j0), Lo = SPL.slice(CV_OOS);
  plot('cv-chart', [
    { x, y: Lo.map(l => Math.max(l, 0)), mode: 'lines', name: 'Daily loss (positive part)', line: { color: FILL, width: 0.6 }, fill: 'tozeroy', fillcolor: FILL, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x, y: fv, mode: 'lines', name: 'FHS: refit each January', line: { color: K.red, width: 1 }, opacity: 0.65, hovertemplate: '%{x}: FHS %{y:.2f}%<extra></extra>' },
    { x, y: vv, mode: 'lines', name: 'CAViaR: β₁ = ' + nf(b1, 3) + ', β₂ = ' + nf(b2, 3), line: { color: K.blue, width: 1.6, dash: 'dash' }, hovertemplate: '%{x}: CAViaR %{y:.2f}%<extra></extra>' }
  ], layout({ ...legendLow(-0.12), title: ttl('S&P 500: out-of-sample VaR 1%, 2016–2026'), xaxis: AX('', { type: 'date' }), yaxis: AX('Daily loss (%)', { range: [0, 20] }) }));
  let nh = 0, pc = 0, pf = 0, cm = 0;
  const pin = (r, q) => (a - (r < q ? 1 : 0)) * (r - q);
  Lo.forEach((l, i) => { if (l > vv[i]) nh++; pc += pin(-l, -vv[i]); pf += pin(-l, -fv[i]); if (x[i] >= '2020-02-20' && x[i] <= '2020-04-30') cm = Math.max(cm, vv[i]); });
  out('cv-out', [T.cv(nf(b1, 3), nf(Math.log(0.5) / Math.log(b1), 1), nh, ni(Lo.length), p2(100 * nh / Lo.length), nf(pc / Lo.length, 3), nf(pf / Lo.length, 3), p2(cm, 1), nf(b0, 3))]);
}

// ================================================================= GEV on block maxima
const GV_PER = { week: 52, month: 12, quarter: 4, half: 2, year: 1 };
function gev() {
  const b = $('gv-b').value, G = D.gev[b], yrs = +$('gv-y').value, c = G.c, xi = -c;
  $('gv-y-v').textContent = yrs;
  const kk = yrs * GV_PER[b], pp = 1 - 1 / kk, rl = G.mu + G.sigma * (1 - Math.pow(-Math.log(pp), c)) / c;
  const M = G.M, mn = Math.min(...M), mx = Math.max(...M), xs = range(mn, mx * 1.1, (mx * 1.1 - mn) / 400);
  const pdf = x => { const t = 1 - c * (x - G.mu) / G.sigma; return t > 0 ? Math.exp(-Math.pow(t, 1 / c)) * Math.pow(t, 1 / c - 1) / G.sigma : 0; };
  const name = { week: 'week', month: 'calendar month', quarter: 'quarter', half: 'half-year', year: 'year' }[b];
  plot('gv-chart', [
    { x: M, type: 'histogram', histnorm: 'probability density', xbins: { start: mn, end: mx, size: (mx - mn) / 50 }, name: 'Maximum daily loss per ' + name + ', S&P 500', marker: { color: 'rgba(26,58,110,0.5)' }, hovertemplate: '%{x}<br>density %{y:.3f}<extra></extra>' },
    { x: xs, y: xs.map(pdf), mode: 'lines', name: 'GEV fit, xi = ' + xi.toFixed(2), line: { color: K.red, width: 2 }, hoverinfo: 'skip' },
    { x: [rl, rl], y: [0, 1], yaxis: 'y2', mode: 'lines', name: yrs + '-year return level = ' + rl.toFixed(2) + '%', line: { color: K.amber, width: 2, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ ...legendLow(), bargap: 0, title: ttl('Block maxima: one maximum per ' + name + ', 2000-2026'), xaxis: AX('Largest daily loss in the block (%)', { range: [0, Math.max(mx * 1.1, rl * 1.05)] }), yaxis: AX('Density'), yaxis2: { overlaying: 'y', range: [0, 1], visible: false } }));
  out('gv-out', [T.gv(b, nf(xi, 2), nf(G.mu, 2), nf(G.sigma, 2), yrs, kk, p2(rl), M.filter(m => m > rl).length, M.length)]);
}

// ================================================================= mean excess and the threshold
function meanExcess() {
  const E = D.me, F = D.gpd.fits.sp500[+$('me-k').value], tail = F.tail;
  $('me-k-v').textContent = ap(tail);
  const uu = range(F.u, E.u[E.u.length - 1], (E.u[E.u.length - 1] - F.u) / 49 || 1);
  const near = E.u.reduce((b, u, i) => (Math.abs(u - F.u) < Math.abs(E.u[b] - F.u) ? i : b), 0);
  plot('me-chart', [
    { x: E.u, y: E.me, customdata: E.n, mode: 'markers', name: 'Empirical mean excess e(u)', marker: { color: K.blue, size: 6 }, hovertemplate: 'u = %{x:.2f}%<br>e(u) = %{y:.2f}%<br>%{customdata} losses above u<extra></extra>' },
    { x: uu, y: uu.map(u => (F.beta + F.xi * (u - F.u)) / (1 - F.xi)), mode: 'lines', name: 'GPD implied: (beta + xi (u - u0)) / (1 - xi)', line: { color: K.red, width: 2 }, hoverinfo: 'skip' },
    { x: [F.u, F.u], y: [0, 1], yaxis: 'y2', mode: 'lines', name: 'Threshold u0 = ' + F.u.toFixed(2) + '% (top ' + (100 * tail) + '% of losses above it)', line: { color: K.navy, width: 1.5, dash: 'dot' }, hoverinfo: 'skip' }
  ], layout({ ...legendLow(), title: ttl('S&P 500 losses: mean excess plot'), xaxis: AX('Threshold u (daily loss, %)'), yaxis: AX('Mean excess e(u) (%)', { range: [0.4, 2.6] }), yaxis2: { overlaying: 'y', range: [0, 1], visible: false } }));
  out('me-out', [T.me(ap(tail), p2(F.u), F.nu, nf(F.xi, 2), nf(F.beta, 2), nf(F.xi / (1 - F.xi), 2), p2(F.beta / (1 - F.xi)), p2(E.me[near]))]);
}

// ================================================================= GPD tails: S&P 500 and Bitcoin
function gpdTail() {
  const k = +$('gt-k').value, res = {};
  $('gt-k-v').textContent = ap(D.gpd.tails[k]);
  for (const a of ['sp500', 'btc']) {
    const F = D.gpd.fits[a][k], Cv = D.gpd.curves[a], top = Cv.top.filter(x => x > F.u), N = top.length;
    const emp = top.map((_, i) => (1 - i / N) * F.nu / F.n), sel = Cv.x.map((x, i) => i).filter(i => Cv.x[i] >= F.u);
    const xx = sel.map(i => Cv.x[i]), gp = xx.map(x => F.nu / F.n * Math.pow(1 + F.xi * (x - F.u) / F.beta, -1 / F.xi));
    plot('gt-' + a, [
      { x: top, y: emp, mode: 'markers', name: 'Empirical tail P(L >= x)', marker: { color: K.blue, size: 4 }, hovertemplate: 'x = %{x:.2f}%<br>%{y:.2e}<extra></extra>' },
      { x: xx, y: gp, mode: 'lines', name: 'GPD, xi = ' + F.xi.toFixed(2), line: { color: K.red, width: 2 }, hovertemplate: 'GPD %{y:.2e}<extra></extra>' },
      { x: xx, y: sel.map(i => Cv.norm[i]), mode: 'lines', name: 'Normal distribution', line: { color: K.orange, width: 2, dash: 'dash' }, hovertemplate: 'Normal %{y:.2e}<extra></extra>' },
      { x: xx, y: sel.map(i => Cv.t[i]), mode: 'lines', name: 'Student-t, nu = ' + Cv.nu.toFixed(1), line: { color: K.green, width: 2, dash: 'dashdot' }, hovertemplate: 'Student-t %{y:.2e}<extra></extra>' }
    ], layout({ ...legendLow(), title: ttl(D.labels[a] + ': largest ' + (100 * F.tail) + '% of daily losses'), xaxis: AX('Daily loss x (%)', { type: 'log' }), yaxis: AX('Exceedance probability', { type: 'log', range: [-6, Math.log10(0.25)], exponentformat: 'power' }) }));
    res[a] = F;
  }
  const S = res.sp500, B = res.btc;
  out('gt-out', [T.gt(ap(S.tail), nf(S.xi, 2), nf(S.se_xi, 3), nf(1 / S.xi, 1), p2(S.var1), nf(B.xi, 2), nf(B.se_xi, 3), nf(1 / B.xi, 1), p2(B.var1))]);
}

// ================================================================= conditional EVT, 2018-2026
const CE0 = RDATE.findIndex(d => d >= '2018-01-01');
function condEvt() {
  const a = ROLL_A[+$('ce-a').value], c = cond(a), hs = rollHS(a, 500);
  $('ce-a-v').textContent = ap(a);
  const x = RDATE.slice(CE0), sl = v => Array.from(v.slice(CE0)), Lo = SPL.slice(RS + CE0);
  const H = sl(hs), G = c.nv.slice(CE0), E = c.cv.slice(CE0);
  plot('ce-chart', [
    { x, y: Lo.map(l => Math.max(l, 0)), mode: 'lines', name: 'Daily loss (gains set to 0)', line: { color: FILL, width: 0.6 }, fill: 'tozeroy', fillcolor: FILL, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x, y: H, mode: 'lines', name: 'HS VaR ' + ap(a) + ' (500 days)', line: { color: K.blue, width: 1.6 }, hovertemplate: '%{x}: HS %{y:.2f}%<extra></extra>' },
    { x, y: G, mode: 'lines', name: 'GARCH with Normal shocks, VaR ' + ap(a), line: { color: K.orange, width: 1.2, dash: 'dash' }, hovertemplate: '%{x}: GARCH-N %{y:.2f}%<extra></extra>' },
    { x, y: E, mode: 'lines', name: 'Conditional EVT VaR ' + ap(a) + ' (McNeil-Frey)', line: { color: K.red, width: 1.2 }, hovertemplate: '%{x}: cEVT %{y:.2f}%<extra></extra>' }
  ], layout({ ...legendLow(-0.12), title: ttl('S&P 500, 2018-2026: unconditional vs conditional VaR'), xaxis: AX('', { type: 'date' }), yaxis: AX('Daily loss (%)', { range: [0, 1.08 * Math.max(...Lo, ...E, ...H)] }) }));
  const rate = v => { let n = 0; Lo.forEach((l, i) => { if (l > v[i]) n++; }); return [p2(100 * n / Lo.length), n]; };
  const [ce, nce] = rate(E), [cg, ncg] = rate(G), [ch, nch] = rate(H);
  out('ce-out', [T.ce(ap(a), ni(Lo.length), ce, nce, cg, ncg, ch, nch, nf(Lo.length * a, 1))]);
}

// ================================================================= horizon: square-root-of-time
function horizon() {
  const h = +$('hz-h').value, Hz = D.horizon, M = Hz.mc[h - 1], hs = range(1, 20, 1);
  $('hz-h-v').textContent = h;
  plot('hz-ratio', D.order.map(k => ({ x: hs, y: Hz.ratio[k], mode: 'lines+markers', name: D.labels[k], line: { color: ACOL[k], width: 2 }, marker: { size: 5 }, hovertemplate: D.labels[k] + ', h = %{x}: %{y:.3f}<extra></extra>' })),
    layout({ ...legendLow(), title: ttl('Empirical h-day VaR vs square-root-of-time rule'), shapes: [hline(1, K.navy, 'dot'), vline(h, K.navy, 'dot')], xaxis: AX('Horizon h (days)', { dtick: 2 }), yaxis: AX('VaR 1%(h) / (sqrt(h) VaR 1%(1))') }));
  const E = Hz.edges, mid = E.slice(0, -1).map((e, i) => (e + E[i + 1]) / 2), ym = Math.max(...M.dens) * 1.05;
  const vl = (x, c, dash, name) => ({ x: [x, x], y: [0, ym], mode: 'lines', name, line: { color: c, width: 2, dash }, hoverinfo: 'skip' });
  plot('hz-mc', [
    { x: mid, y: M.dens, type: 'bar', name: 'FHS Monte Carlo, ' + h + '-day loss', marker: { color: 'rgba(26,58,110,0.5)' }, width: E[1] - E[0], hovertemplate: '%{x:.1f}%: %{y:.3f}<extra></extra>' },
    vl(M.mc_var, K.red, 'solid', 'MC VaR 1% = ' + M.mc_var.toFixed(2) + '%'),
    vl(M.sqrt_var, K.amber, 'dash', 'sqrt(' + h + ') x 1-day FHS VaR = ' + M.sqrt_var.toFixed(2) + '%'),
    vl(M.uncond_var, K.purple, 'dot', 'sqrt(' + h + ') x 1-day HS VaR = ' + M.uncond_var.toFixed(2) + '%')
  ], layout({ ...legendLow(), bargap: 0, title: ttl('S&P 500: ' + h + '-day loss from 18 Sep 2026'), xaxis: AX(h + '-day loss (%)', { range: [-12, 16] }), yaxis: AX('Density', { range: [0, ym] }) }));
  const rt = D.order.map(k => T.names[k] + ' ' + nf(Hz.ratio[k][h - 1], 2)).join(', ');
  out('hz-out', [T.hz(h, rt, p2(M.mc_var), p2(M.sqrt_var), p2(M.uncond_var))]);
}

// ================================================================= portfolio risk contributions
const P = D.port, PN = P.names.length, PR = P.R;
const PCOV = (() => { const n = PR.length, m = P.names.map((_, i) => mean(PR.map(r => r[i]))), S = m.map(() => new Array(PN).fill(0));
  for (const r of PR) for (let i = 0; i < PN; i++) for (let j = 0; j < PN; j++) S[i][j] += (r[i] - m[i]) * (r[j] - m[j]) / (n - 1); return S; })();
function components() {
  const wb = +$('pc-w').value / 100, w = [0.4, 0.3, 0.2].map(x => x / 0.9 * (1 - wb)).concat([wb]);
  $('pc-w-v').textContent = Math.round(100 * wb) + '%';
  const z1 = -nppf(0.01), Sw = PCOV.map(r => sum(r.map((v, j) => v * w[j]))), sp = Math.sqrt(sum(w.map((x, i) => x * Sw[i])));
  const varp = z1 * sp, cshare = w.map((x, i) => x * z1 * Sw[i] / sp / varp), vund = sum(w.map((x, i) => z1 * Math.sqrt(PCOV[i][i]) * x));
  const Lp = PR.map(r => -sum(r.map((v, i) => v * w[i])));
  // historical component ES: the portfolio ES tail weights applied to -w_i R_i (the components add up to the portfolio ES)
  const na = Lp.length * 0.025, m = Math.floor(na + 1e-9), fr = Math.max(na - m, 0), ord = Lp.map((x, t) => t).sort((i, j) => Lp[j] - Lp[i]);
  const ces = new Array(PN).fill(0); let esp = 0;
  ord.slice(0, m + (fr > 1e-12 ? 1 : 0)).forEach((t, j) => { const wt = (j < m ? 1 : fr) / na; esp += wt * Lp[t]; PR[t].forEach((v, i) => (ces[i] -= wt * v * w[i])); });
  const eshare = ces.map(x => x / esp);
  const eund = sum(P.names.map((_, i) => hsVarEs(sorted(PR.map(r => -r[i] * w[i])), 0.025)[1]));
  const lab = ['SPY (US equity)', 'TLT (US Treasuries)', 'GLD (gold)', 'Bitcoin'];
  const bar = (y, name, col) => ({ x: lab, y: y.map(v => 100 * v), type: 'bar', name, marker: { color: col }, text: y.map(v => (100 * v).toFixed(0)), textposition: 'outside', textfont: { size: 10 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' });
  plot('pc-chart', [bar(w, 'Weight', K.teal), bar(cshare, 'Share of VaR 1% (Normal, Euler)', K.blue), bar(eshare, 'Share of ES 2.5% (historical, Euler)', K.red)],
    layout({ ...legendLow(-0.14), barmode: 'group', bargap: 0.25, title: ttl('Who contributes the risk? Portfolio ' + w.map(x => Math.round(100 * x)).join('/') + ', 2014-2026'), xaxis: AX(''), yaxis: AX('%', { range: [Math.min(0, ...eshare.map(v => 100 * v)) - 5, Math.max(...cshare, ...eshare, ...w) * 100 + 10] }) }));
  out('pc-out', [T.pc(w.map(x => Math.round(100 * x)).join('/'), p2(varp), p2(vund), p2(100 * (varp / vund - 1), 0), p2(esp), p2(eund), p2(100 * cshare[3], 1), p2(100 * eshare[3], 1), p2(100 * eshare[1], 1))]);
}

// ================================================================= VaR 1% against ES at level a (Basel 1996 vs FRTB)
function basel() {
  const a = +$('bs-a').value / 100, ks = D.order;
  $('bs-a-v').textContent = ap(a);
  const v = ks.map(k => hsVarEs(lossSorted(k), 0.01)[0]), e = ks.map(k => hsVarEs(lossSorted(k), a)[1]), lab = ks.map(k => D.labels[k]);
  plot('bs-chart', [
    { x: lab, y: v, type: 'bar', name: 'VaR 1% (Basel 1996)', marker: { color: K.blue }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: lab, y: e, type: 'bar', name: 'ES ' + ap(a) + (Math.abs(a - 0.025) < 1e-9 ? ' (FRTB, 2019)' : ''), marker: { color: K.red }, text: e.map((x, i) => 'x' + (x / v[i]).toFixed(2)), textposition: 'outside', hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ ...legendLow(-0.14), barmode: 'group', bargap: 0.3, title: ttl('Historical simulation: ES/VaR ratios above bars'), xaxis: AX(''), yaxis: AX('Daily loss (%)', { range: [0, 1.2 * Math.max(...v, ...e)] }) }));
  const za = nppf(a), nr = (npdf(za) / a) / -nppf(0.01);
  out('bs-out', [T.bs(ap(a), ks.map((k, i) => T.names[k] + ' ' + nf(e[i] / v[i], 2)).join(', '), nf(nr, 3))]);
}

// ================================================================= case study: Table 6 of Chronopoulos et al. (2024)
const CK_SETS = Object.keys(D.crk.table), CK_COL = [K.blue, K.red, K.green, K.orange];
function crk() {
  const s = +$('ck-s').value, sets = s === 0 ? CK_SETS : [CK_SETS[s - 1]];
  $('ck-s-v').textContent = s === 0 ? (window.MFM_LANG === 'ro' ? 'toate' : 'all') : CK_SETS[s - 1];
  const M = D.crk.methods.map(m => (m.startsWith('Deep ') || m.startsWith('Linear') ? m.replace(' ', '<br>') : m));
  const tr = sets.map(st => { const i = CK_SETS.indexOf(st), y = D.crk.table[st];
    return { x: M, y, type: 'bar', name: st, marker: { color: CK_COL[i] }, text: y.map(v => (v > 2 || v < 0.03 ? v.toFixed(3) : '')), textposition: 'outside', textfont: { size: 10 }, hovertemplate: st + ', %{x}: %{y:.3f}<extra></extra>' }; });
  plot('ck-chart', tr, layout({ ...legendLow(-0.22), barmode: 'group', bargap: 0.2, title: ttl('S&P 500 VaR 1%: relative forecast errors'),
    shapes: [hline(1, K.navy, 'dash'), { type: 'line', xref: 'x', yref: 'paper', x0: 2.5, x1: 2.5, y0: 0, y1: 1, line: { color: K.navy, width: 1, dash: 'dot' } }],
    annotations: [{ x: 1, y: 1, yref: 'paper', text: 'Flexible, not deep', showarrow: false, font: { color: K.orange, size: 11 } }, { x: 5, y: 1, yref: 'paper', text: 'Deep neural networks', showarrow: false, font: { color: K.blue, size: 11 } },
      { xref: 'paper', x: 1, y: Math.log10(1.15), text: 'Linear quantile regression = 1', showarrow: false, xanchor: 'right', yanchor: 'bottom', font: { size: 10 } }],
    xaxis: AX('', { tickfont: { size: 10, color: K.navy } }), yaxis: AX('Relative RMSFE (log scale)', { type: 'log', range: [Math.log10(0.007), Math.log10(16)], tickvals: [0.01, 0.1, 1, 10], ticktext: ['0.01', '0.1', '1', '10'] }) }));
  const flex = [], deep = [];
  sets.forEach(st => D.crk.table[st].forEach((v, j) => (j < 3 ? flex : deep).push(v)));
  out('ck-out', [T.ck(s === 0 ? null : CK_SETS[s - 1], flex.filter(v => v >= 1).length, flex.length, deep.filter(v => v < 1).length, deep.length, nf(Math.min(...deep), 3), nf(Math.max(...deep), 3))]);
}

// ================================================================= second case study: score-driven GPD tail (D'Innocenzo et al., 2024)
// f_t = (ln xi_t, ln delta_t); f_{t+1} = (1 - B) fbar + A s_t + B f_t, s_t = L_t' grad_t (0 without an exceedance); case_tailshape.py
function tailFilter(aXi) {
  const TS = D.tail, th = TS.theta, n = TS.tau.length, X = new Float64Array(n);
  TS.exc_i.forEach((i, j) => { X[i] = TS.exc_x[j]; });
  const xi = new Float64Array(n), de = new Float64Array(n), v1 = new Float64Array(n), e25 = new Float64Array(n);
  const ax = aXi, ad = th.a_delta, bx = th.b_xi, bd = th.b_delta, ox = (1 - bx) * th.fbar_xi, od = (1 - bd) * th.fbar_delta;
  let f1 = th.fbar_xi, f2 = th.fbar_delta, ll = 0, cnt = 0;
  const risk = (t, k, d, p, a) => { const v = TS.tau[t] + d / k * (Math.pow(a / p, -k) - 1); return [v, (v + d - k * TS.tau[t]) / (1 - k)]; };
  for (let t = 0; t < n; t++) {
    f1 = Math.min(Math.max(f1, -6), 1.5); f2 = Math.min(Math.max(f2, -6), 4);
    const k = Math.exp(f1), d = Math.exp(f2); xi[t] = k; de[t] = d;
    const p = cnt > 0 ? cnt / t : 0.1;
    v1[t] = risk(t, k, d, p, 0.01)[0]; e25[t] = risk(t, k, d, p, 0.025)[1];
    let s1 = 0, s2 = 0; const x = X[t];
    if (x > 0) {
      const z = 1 + k * x / d; ll += -Math.log(d) - (1 + 1 / k) * Math.log(z);
      const g1 = Math.log(z) / k - (1 + 1 / k) * k * x / (d + k * x), g2 = (x - d) / (d + k * x);
      s1 = (1 + 1 / k) * g1 - g2; s2 = Math.sqrt(1 + 2 * k) * g2; cnt++;
    }
    f1 = ox + ax * s1 + bx * f1; f2 = od + ad * s2 + bd * f2;
  }
  return { xi, de, v1, e25, ll };
}
const SPDATE = D.sp_days.map(day);
function tailShape() {
  const TS = D.tail, m = +$('ts-m').value, aXi = m * TS.theta.a_xi, F = tailFilter(aXi), L = D.loss.sp500, n = L.length;
  $('ts-m-v').innerHTML = nf(m, 2) + ' (a<sub>ξ</sub> = ' + nf(aXi, 3) + ')';
  const hit = []; let vmax = 0, vd = 0, xmin = Infinity, xmax = 0;
  for (let t = 0; t < n; t++) { if (L[t] > F.v1[t]) hit.push(t); if (F.v1[t] > vmax) { vmax = F.v1[t]; vd = t; } xmin = Math.min(xmin, F.xi[t]); xmax = Math.max(xmax, F.xi[t]); }
  plot('ts-risk', [
    { x: SPDATE, y: Array.from(L, v => Math.max(v, 0)), mode: 'lines', name: 'Daily loss (gains set to 0)', line: { color: FILL, width: 0.5 }, fill: 'tozeroy', fillcolor: FILL, hovertemplate: '%{x}: loss %{y:.2f}%<extra></extra>' },
    { x: SPDATE, y: TS.tau, mode: 'lines', name: 'Threshold τ<sub>t</sub> (90% quantile)', line: { color: K.green, width: 1 }, hovertemplate: '%{x}: τ %{y:.2f}%<extra></extra>' },
    { x: SPDATE, y: Array.from(F.v1), mode: 'lines', name: 'VaR 1%', line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x}: VaR 1% %{y:.2f}%<extra></extra>' },
    { x: SPDATE, y: Array.from(F.e25), mode: 'lines', name: 'ES 2.5%', line: { color: K.red, width: 1, dash: 'dot' }, hovertemplate: '%{x}: ES 2.5% %{y:.2f}%<extra></extra>' },
    { x: hit.map(t => SPDATE[t]), y: hit.map(t => L[t]), mode: 'markers', name: 'Loss above VaR 1%', marker: { color: K.orange, size: 5 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ ...legendLow(-0.12), title: ttl('S&P 500 losses, VaR and ES'), xaxis: AX('', { type: 'date' }), yaxis: AX('Daily loss (%)', { range: [0, 14] }) }));
  plot('ts-xi', [
    { x: [SPDATE[0], SPDATE[n - 1], SPDATE[n - 1], SPDATE[0]], y: [TS.paper_xi[0], TS.paper_xi[0], TS.paper_xi[1], TS.paper_xi[1]], fill: 'toself', fillcolor: 'rgba(197,210,232,0.6)', line: { width: 0 }, mode: 'lines', name: "Paper's range, 1962-2020", hoverinfo: 'skip' },
    { x: SPDATE, y: Array.from(F.xi), mode: 'lines', name: 'Score-driven ξ<sub>t</sub>', line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x}: ξ %{y:.3f}<extra></extra>' },
    { x: [SPDATE[0], SPDATE[n - 1]], y: [TS.static.xi, TS.static.xi], mode: 'lines', name: 'Static GPD, same thresholds', line: { color: K.navy, width: 1, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [SPDATE[0], SPDATE[n - 1]], y: [TS.xi_const, TS.xi_const], mode: 'lines', name: 'Constant ξ, score-driven δ<sub>t</sub>', line: { color: K.orange, width: 1.4, dash: 'dashdot' }, hoverinfo: 'skip' }
  ], layout({ ...legendLow(-0.12), title: ttl('Tail shape ξ<sub>t</sub>'), xaxis: AX('', { type: 'date' }), yaxis: AX('ξ<sub>t</sub>') }));
  out('ts-out', [T.ts(nf(aXi, 3), nf(F.ll, 2), nf(F.ll - TS.loglik_const, 2), nf(xmin, 3), nf(xmax, 3), hit.length, p2(100 * hit.length / n), p2(vmax), SPDATE[vd])]);
}

// ================================================================= AI mini case: FZ0 scores and Diebold-Mariano tests
let aiPre = null;
function aiPrep() {
  const a = 0.01, c = cond(a), Y = SPL.slice(RS).map(x => -x);
  const fz = (vr, es) => Y.map((y, j) => { const v = -vr[j], e = -es[j]; return -((y <= v ? 1 : 0) * (v - y)) / (a * e) + v / e + Math.log(-e) - 1; });
  const S = { FHS: fz(c.fv, c.fe), cEVT: fz(c.cv, c.ce), 'GARCH-N': fz(c.nv, c.ne) };
  return { S, d1: S.FHS.map((x, j) => x - S['GARCH-N'][j]), d2: S.cEVT.map((x, j) => x - S.FHS[j]), year: RDATE.map(d => +d.slice(0, 4)) };
}
function dm(x) {                                     // OLS on a constant, HAC (Bartlett, 5 lags), as statsmodels cov_type='HAC'
  const n = x.length, m = mean(x), e = x.map(v => v - m); let s = sum(e.map(v => v * v)) / n;
  for (let j = 1; j <= 5; j++) { let g = 0; for (let t = j; t < n; t++) g += e[t] * e[t - j]; s += 2 * (1 - j / 6) * g / n; }
  const se = Math.sqrt(s / n); return { m, se, t: m / se, n };
}
function aiCase() {
  if (!aiPre) aiPre = aiPrep();
  const Y = +$('ai-y').value, A = aiPre, early = A.year.map(y => y <= Y);
  $('ai-y-v').textContent = Y;
  const part = (d, f) => d.filter((_, j) => f(j)), r = [];
  for (const [d, lab, col] of [[A.d1, 'FHS - GARCH-N', K.blue], [A.d2, 'cEVT - FHS', K.red]]) {
    r.push([lab + ', 2006-2026', dm(d), col], [lab + ', 2006-' + Y, dm(part(d, j => early[j])), col], [lab + ', ' + (Y + 1) + '-2026', dm(part(d, j => !early[j])), col]);
  }
  const ys = r.map(x => x[0]);
  plot('ai-ci', [K.blue, K.red].map((col, ci) => { const rr = r.filter(x => x[2] === col);
    return { x: rr.map(x => x[1].m), y: rr.map(x => x[0]), mode: 'markers', name: ci ? 'Tail model: conditional EVT vs FHS' : 'Shape of the shocks: FHS vs GARCH with Normal shocks',
      marker: { color: col, size: 8 }, error_x: { type: 'data', array: rr.map(x => 1.96 * x[1].se), color: col, thickness: 4, width: 0 }, hovertemplate: '%{y}<br>mean %{x:.3f}<extra></extra>' }; }),
    layout({ ...legendLow(-0.2), title: ttl('Mean FZ0 score difference, 95% HAC interval'), margin: { l: 150, r: 12, t: 30, b: 40 }, shapes: [vline(0, K.navy, 'dash')],
      annotations: r.map(x => ({ x: 0.012, y: x[0], text: 't = ' + x[1].t.toFixed(2), showarrow: false, xanchor: 'left', font: { size: 10 } })),
      xaxis: AX('Negative favours the first model', { range: [-0.42, 0.11] }), yaxis: AX('', { categoryorder: 'array', categoryarray: [...ys].reverse(), tickfont: { size: 10, color: K.navy } }) }));
  const cum = d => { let s = 0; return d.map(v => (s += v)); };
  const sd = RDATE.find(dd => +dd.slice(0, 4) > Y);
  plot('ai-cum', [
    { x: RDATE, y: cum(A.d1), mode: 'lines', name: 'FHS - GARCH-N', line: { color: K.blue, width: 1.6 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' },
    { x: RDATE, y: cum(A.d2), mode: 'lines', name: 'cEVT - FHS', line: { color: K.red, width: 1.6 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }
  ], layout({ ...legendLow(-0.14), title: ttl('Cumulative FZ0 score difference'), shapes: [vline(sd, K.navy, 'dot')], xaxis: AX('', { type: 'date' }), yaxis: AX('Sum of daily differences') }));
  const sig = x => x[1].t < -1.96;
  out('ai-out', [T.ai(Y, nf(r[1][1].t, 2), nf(r[2][1].t, 2), nf(r[4][1].t, 2), nf(r[5][1].t, 2), sig(r[1]) && sig(r[2]), sig(r[4]) && sig(r[5]))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, PL = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['ld-a'], lossDist); PL('ld-play', 'ld-a', range(0, ALPHA_LD.length - 1, 1), 700);
  on(['sa-p'], subadd); PL('sa-play', 'sa-p', range(0.1, 2, 0.1), 450);
  $('vl-a').max = D.levels.alpha.length - 1; $('vl-a').value = D.levels.alpha.length - 1; on(['vl-a'], varLevels); PL('vl-play', 'vl-a', range(0, D.levels.alpha.length - 1, 1), 160);
  on(['pr-n'], precision); PL('pr-play', 'pr-n', range(0, PR_N.length - 1, 1), 900);
  $('hf-t').max = RN - 1; $('hf-t').value = RN - 1; on(['hf-a', 'hf-w', 'hf-t'], hsFhs); PL('hf-play', 'hf-t', range(0, RN - 1, 25).concat([RN - 1]), 90);
  $('cv-b1').value = CV.b[1].toFixed(3); $('cv-b2').value = CV.b[2].toFixed(3); on(['cv-b1', 'cv-b2'], caviar); PL('cv-play', 'cv-b1', range(0.7, 0.98, 0.01), 400);
  on(['gv-b', 'gv-y'], gev); PL('gv-play', 'gv-y', range(2, 50, 1), 200);
  on(['me-k'], meanExcess); PL('me-play', 'me-k', range(0, D.gpd.tails.length - 1, 1), 700);
  on(['gt-k'], gpdTail); PL('gt-play', 'gt-k', range(0, D.gpd.tails.length - 1, 1), 700);
  on(['ce-a'], condEvt); PL('ce-play', 'ce-a', range(0, ROLL_A.length - 1, 1), 1100);
  on(['hz-h'], horizon); PL('hz-play', 'hz-h', range(1, 20, 1), 500);
  on(['pc-w'], components); PL('pc-play', 'pc-w', range(0, 30, 1), 250);
  on(['bs-a'], basel); PL('bs-play', 'bs-a', range(1, 5, 0.25), 400);
  on(['ck-s'], crk); PL('ck-play', 'ck-s', range(0, CK_SETS.length, 1), 1200);
  on(['ts-m'], tailShape); PL('ts-play', 'ts-m', range(0, 2, 0.1), 700);
  on(['ai-y'], aiCase); PL('ai-play', 'ai-y', range(2008, 2024, 1), 600);
  const PFX = { 'loss-distribution': 'ld', 'subadditivity': 'sa', 'var-levels': 'vl', 'precision': 'pr', 'hs-fhs': 'hf', 'caviar': 'cv', 'gev': 'gv', 'mean-excess': 'me', 'gpd-tail': 'gt', 'cond-evt': 'ce', 'horizon': 'hz', 'components': 'pc', 'basel': 'bs', 'deep-quantile': 'ck', 'tail-shape': 'ts', 'fz0-ranking': 'ai' };
  // var-levels: both live charts show the VaR/ES curves of the five methods at every α, i.e. the answer; they are veiled until
  // „Verifică”, „Arată slide-ul”, the end of ▶ or a change of α
  const VEIL_CHART = new Set(['var-levels']);
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) =>
    predict(b, Object.assign({ player: players[PFX[b] + '-play'] }, sp, VEIL_CHART.has(b) ? { veil: Object.assign({ out: true }, sp.veil, { charts: true }) } : {})));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  lossDist(); subadd(); varLevels(); precision(); hsFhs(); caviar(); gev(); meanExcess(); gpdTail(); condEvt(); horizon(); components(); basel(); crk(); tailShape(); aiCase();
}
window.CH7 = { hsVarEs, sorted, nppf, cond, rollHS, caviarPath, dm, aiPrep, discreteVarEs, gpdVarEs, tailFilter };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

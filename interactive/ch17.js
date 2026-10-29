// Chapter 17 interactive page: one block per chart slide, computed in the browser from ch17_data.js.
(function () {
'use strict';
const D = window.CH17_DATA;
const { LANG, C, sum, mean, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH17_TEXT;

// ---------------------------------------------------------------- colours of the chapter (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  teal: '#17A2B8', magenta: '#D63384', brown: '#795548', navy: '#1F2A44', band: '#C5D2E8' };
const AMBER_BAND = 'rgba(181,133,63,0.25)', TEAL_BAND = 'rgba(23,162,184,0.25)';

// ---------------------------------------------------------------- helpers
const MON = T.months;
const th = v => String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, LANG === 'ro' ? ' ' : ',');   // thousands separator
const fmtM = s => MON[+s.slice(5, 7) - 1] + ' ' + s.slice(0, 4);                       // 'YYYY-MM[-DD]' -> 'Aug 1917'
const fmtD = s => (+s.slice(8, 10)) + ' ' + MON[+s.slice(5, 7) - 1] + ' ' + s.slice(0, 4);
const ms = s => Date.parse(s.length === 7 ? s + '-01' : s);
const DAY = 86400000;
const yrs = s => { const y = +s.slice(0, 4), d0 = Date.UTC(y, 0, 1); return y + (ms(s) - d0) / DAY / 365.25; };   // decimal years, as yrs() of the chapter
function quantile(a, q) {           // numpy's default (linear interpolation)
  const b = [...a].sort((x, y) => x - y), h = (b.length - 1) * q, l = Math.floor(h);
  return b[l] + (h - l) * ((b[Math.min(l + 1, b.length - 1)]) - b[l]);
}
function episodes(stat, cv, L, upto) {   // runs of stat > cv of at least L periods (bubbles.episodes); end = null if still open
  const n = upto === undefined ? stat.length : upto + 1, res = [];
  const ab = i => stat[i] !== null && cv[i] !== null && stat[i] > cv[i];
  let i = 0;
  while (i < n) {
    if (ab(i)) { let j = i; while (j + 1 < n && ab(j + 1)) j++; if (j - i + 1 >= L) res.push({ s: i, e: j + 1 < n ? j : null, n: j - i + 1 }); i = j + 1; } else i++;
  }
  return res;
}
const runAbove = (stat, cv, k) => { let m = 0; while (k - m >= 0 && stat[k - m] !== null && cv[k - m] !== null && stat[k - m] > cv[k - m]) m++; return m; };
const band = (x0, x1, col) => ({ type: 'rect', xref: 'x', yref: 'paper', x0, x1, y0: 0, y1: 1, fillcolor: col, line: { width: 0 }, layer: 'below' });
const sline = (x, col, dash, w) => ({ type: 'line', xref: 'x', yref: 'paper', x0: x, x1: x, y0: 0, y1: 1, line: { color: col, width: w || 1.5, dash: dash || 'solid' } });
const legendBox = (name, col) => ({ x: [null], y: [null], type: 'bar', name, marker: { color: col }, hoverinfo: 'skip' });
const epList = (E, dates) => E.length ? E.map(e => fmtM(dates[e.s]) + '–' + (e.e === null ? T.open : fmtM(dates[e.e]))).join(', ') : T.none;
const two = (h1) => ({ yaxis: AX('', { domain: [0.47, 1] }), yaxis2: AX('', { domain: [0, 0.4], anchor: 'x' }), xaxis: AX('', { anchor: 'y2' }), height: h1 });
// two side-by-side panels in one figure (one legend below both): panel titles as annotations
function sub2(t1, t2, lay) {
  const L = Object.assign({}, lay);
  L.xaxis = Object.assign(L.xaxis || AX(''), { domain: [0, 0.45], anchor: 'y' });
  L.xaxis2 = Object.assign(L.xaxis2 || AX(''), { domain: [0.55, 1], anchor: 'y2' });
  L.yaxis = Object.assign(L.yaxis || AX(''), { anchor: 'x' });
  L.yaxis2 = Object.assign(L.yaxis2 || AX(''), { anchor: 'x2' });
  L.annotations = (L.annotations || []).concat([[t1, 0], [t2, 0.55]].map(([t, x]) => ({ text: t, x, xref: 'paper', xanchor: 'left', y: 1.02, yref: 'paper', yanchor: 'bottom', showarrow: false, font: { size: 12, color: K.navy } })));
  L.margin = { l: 56, r: 12, t: 34, b: 40 };
  return L;
}
const hl = (y, panel, col, dash) => ({ type: 'line', xref: (panel === 2 ? 'x2' : 'x') + ' domain', x0: 0, x1: 1, yref: panel === 2 ? 'y2' : 'y', y0: y, y1: y, line: { color: col, width: 1.5, dash: dash || 'solid' } });
const vl = (x, xr, col, dash) => ({ type: 'line', xref: xr, x0: x, x1: x, yref: (xr === 'x2' ? 'y2' : 'y') + ' domain', y0: 0, y1: 1, line: { color: col, width: 2, dash: dash || 'solid' } });

// ================================================================= 1. simulated rational bubble
function rational() {
  const R = D.rational, pi = +$('rb-pi').value, b0 = +$('rb-b').value, r = R.r, n = R.F.length;
  $('rb-pi-v').textContent = nf(pi, 3); $('rb-b-v').textContent = nf(b0, 0);
  const B = new Array(n); B[0] = b0; let col = 0;
  for (let t = 1; t < n; t++) {
    const alive = R.U[t] < pi;
    B[t] = alive ? (b0 + (1 + r) / pi * (B[t - 1] - b0 / (1 + r))) * R.u[t] : b0 * R.u[t];
    if (!alive && B[t - 1] > 25) col++;
  }
  const P = R.F.map((f, t) => f + B[t]), x = range(0, n - 1, 1), mult = Math.max(...P.map((p, t) => p / R.F[t]));
  plot('rb-chart', [
    { x, y: P, mode: 'lines', name: 'Price = fundamental value + bubble', line: { color: K.blue, width: 1.3 }, hovertemplate: 'period %{x}<br>price %{y:.1f}<extra></extra>' },
    { x, y: R.F, mode: 'lines', name: 'Fundamental value D<sub>t</sub> / r', line: { color: K.green, width: 1.6 }, hovertemplate: 'period %{x}<br>F %{y:.1f}<extra></extra>' }
  ], layout({ title: ttl(`Simulated rational bubble (Evans form): survives with probability ${pi.toFixed(3)}, restarts at δ = ${b0}`),
    xaxis: AX('Period'), yaxis: AX('Price') }));
  out('rb-out', [T.rb(pct((1 + r) / pi - 1, 1), nf(1 / (1 - pi), 1), col, nf(mult, 2))]);
}

// ================================================================= 2. nine episodes aligned at the peak
const EP_COL = [K.blue, K.teal, K.red, K.amber, K.purple, K.orange, K.green, K.magenta, K.brown];
function episodesBlk() {
  const E = D.episodes, h = +$('ep-h').value, sel = $('ep-sel').value;
  const hs = nf(h, h % 0.5 ? 2 : (h % 1 ? 1 : 0));
  $('ep-h-v').textContent = hs;
  const tr = E.map((e, i) => ({ x: e.d.map(v => v / 365.25), y: e.y, mode: 'lines', name: e.label, opacity: sel === 'all' || +sel === i ? 1 : 0.25,
    line: { color: EP_COL[i], width: +sel === i ? 2.4 : 1.2 }, hovertemplate: e.label + '<br>%{x:.2f} years: %{y:.1f}<extra></extra>' }));
  plot('ep-chart', tr, layout({ title: ttl('Nine run-ups and crashes aligned at the peak'), shapes: [sline(0, K.navy, 'dot', 1), hline(100, K.navy), sline(h, K.red, 'dash', 1.5)],
    xaxis: AX('Years from the peak', { range: [-2.05, 2.05] }), yaxis: AX('Price, peak = 100 (log scale)', { type: 'log', dtick: 1 }) }));
  const dd = E.map(e => { let m = 100; e.d.forEach((d, k) => { if (d > 0 && d <= h * 365.25 + 1e-9) m = Math.min(m, e.y[k]); }); return m / 100 - 1; });
  const o = dd.map((v, i) => [v, E[i].label]).sort((a, b) => a[0] - b[0]), md = [...dd].sort((a, b) => a - b)[4];
  out('ep-out', [T.ep(hs, pct(o[o.length - 1][0], 0), o[o.length - 1][1], pct(o[0][0], 0), o[0][1], pct(md, 0))].concat(sel === 'all' ? [] :
    [T.ep1(E[+sel].label, fmtD(E[+sel].peak), pct(E[+sel].runup, 0), pct(dd[+sel], 0), hs, pct(E[+sel].maxdd4, 0))]));
}

// ================================================================= 3. Bubbles for Fama
function gsy() {
  const G = D.gsy, k = +$('gs-c').value, c = G.falls[k], key = c.toFixed(2), x = G.thr.map(v => 100 * v);
  $('gs-c-v').textContent = pct(c, 0);
  const p = G.crash[key], ci = G.crash_ci[key];
  const eb = (y, lo, hi) => ({ type: 'data', symmetric: false, array: hi.map((v, i) => v - y[i]), arrayminus: lo.map((v, i) => y[i] - v), color: K.red, thickness: 1.2, width: 4 });
  const ht = G.thr.map((_, i) => `n = ${G.n[i]} episodes in ${G.n_ind[i]} industries`), r2 = G.ret2.map(v => 100 * v), pc = p.map(v => 100 * v);
  plot('gs-chart', [
    { x, y: pc, error_y: eb(pc, ci.map(v => 100 * v[0]), ci.map(v => 100 * v[1])), mode: 'lines+markers', name: 'After a run-up (95% CI, bootstrap by year)',
      line: { color: K.red, width: 1.6 }, marker: { size: 7 }, text: ht, hovertemplate: 'threshold %{x}%<br>P(crash) %{y:.0f}%<br>%{text}<extra></extra>' },
    { x: [40, 160], y: [100 * G.uncond[key], 100 * G.uncond[key]], mode: 'lines', name: 'All industry-months (unconditional)', line: { color: K.blue, width: 1.5, dash: 'dash' }, hovertemplate: 'unconditional %{y:.1f}%<extra></extra>' },
    { x, y: r2, xaxis: 'x2', yaxis: 'y2', error_y: eb(r2, G.ret2_ci.map(v => 100 * v[0]), G.ret2_ci.map(v => 100 * v[1])), mode: 'lines+markers', showlegend: false,
      line: { color: K.red, width: 1.6 }, marker: { size: 7 }, text: ht, hovertemplate: 'threshold %{x}%<br>mean return %{y:.1f}%<br>%{text}<extra></extra>' },
    { x: [40, 160], y: [100 * G.uncond_ret2, 100 * G.uncond_ret2], xaxis: 'x2', yaxis: 'y2', mode: 'lines', showlegend: false, line: { color: K.blue, width: 1.5, dash: 'dash' }, hovertemplate: 'unconditional %{y:.1f}%<extra></extra>' }
  ], layout(sub2(`P(${Math.round(100 * c)}% drawdown in the next 2 years), %`, 'Mean return over the next 2 years, %', {
    xaxis: AX('Run-up threshold (%)', { range: [40, 160] }), yaxis: AX('Probability, %', { range: [0, 100] }),
    xaxis2: AX('Run-up threshold (%)', { range: [40, 160] }), yaxis2: AX('Return, %'), shapes: [hl(0, 2, K.navy)] })));
  out('gs-out', [T.gs(pct(c, 0), pct(p[2], 0), pct(ci[2][0], 0), pct(ci[2][1], 0), G.n[2], pct(G.uncond[key], 1), pct(p[4], 0), G.n[4])]);
}

// ================================================================= 4. three ways of choosing the windows
function windows() {
  const r0 = +$('wi-r').value, Tn = +$('wi-T').value;
  $('wi-r-v').textContent = nf(r0, 2);
  const lin = (a, b, k) => Array.from({ length: k }, (_, i) => a + (b - a) * i / (k - 1));
  const specs = [['wi-a', 'ADF: one window', [[0, 1]], K.blue], ['wi-s', 'SADF: start fixed, end grows', lin(r0, 1, 7).map(e => [0, e]), K.green],
    ['wi-g', 'GSADF: start and end both move', lin(r0, 1, 4).flatMap(e => lin(0, e - r0, 3).map(s => [s, e])), K.red]];
  for (const [id, title, wins, col] of specs) {
    plot(id, wins.map(([s, e], i) => ({ x: [s, e], y: [i, i], mode: 'lines', showlegend: false, line: { color: col, width: 6 }, hovertemplate: `window [${s.toFixed(2)}, ${e.toFixed(2)}]<extra></extra>` })),
      layout({ title: ttl(title), shapes: [sline(r0, K.navy, 'dot', 1)], margin: { l: 16, r: 8, t: 30, b: 40 },
        xaxis: AX('Fraction of the sample', { range: [-0.02, 1.02], tickvals: [0, r0, 1], ticktext: ['0', 'r₀', '1'] }), yaxis: AX('', { showticklabels: false, showgrid: false, zeroline: false, range: [-1, 12.5] }) }));
  }
  const w0 = Math.floor(r0 * Tn), rr = 0.01 + 1.8 / Math.sqrt(Tn), wr = Math.floor(rr * Tn);
  const cnt = w => (Tn - w + 1) * (Tn - w + 2) / 2;
  out('wi-out', [T.wi(th(Tn), nf(r0, 2), w0, th(Tn - w0 + 1), th(cnt(w0))), T.wi2(nf(rr, 3), wr, th(cnt(wr)))]);
}

// ================================================================= 5. null distributions
function nullDist() {
  const N = D.null, k = +$('nu-k').value, row = N.rows[k], b = N.bins, w = b[1] - b[0], mid = b.slice(0, -1).map(v => v + w / 2);
  $('nu-k-v').textContent = row.w0 + (row.w0 === N.w0_rule ? ' ' + T.rule(nf(N.r0_rule, 3)) : '');
  const S = [['adf', K.blue, 'ADF'], ['sadf', K.green, 'SADF'], ['gsadf', K.red, 'GSADF']], R = sum(row.hist.adf);
  plot('nu-chart', S.map(([key, col, lab]) => ({ x: mid, y: row.hist[key].map(c => c / (R * w)), mode: 'lines', line: { color: col, width: 1.6, shape: 'hvh' },
      name: `${lab} (95% critical value ${row.cv[key]['95'].toFixed(2)})`, hovertemplate: lab + ' %{x:.2f}: density %{y:.2f}<extra></extra>' })),
    layout({ title: ttl(`Null distributions, T = ${N.T}, minimum window ${row.w0}, ${R} Monte Carlo paths`), shapes: S.map(([key, col]) => sline(row.cv[key]['95'], col, 'dash', 1.2)),
      xaxis: AX('Test statistic under a random walk', { range: [-4, 5] }), yaxis: AX('Density') }));
  const cntw = (N.T - row.w0 + 1) * (N.T - row.w0 + 2) / 2;
  out('nu-out', [T.nu(row.w0, nf(row.cv.adf['95'], 2), nf(row.cv.sadf['95'], 2), nf(row.cv.gsadf['95'], 2), th(cntw)), T.nu2(N.w0_rule, nf(N.r0_rule, 3))]);
}

// ================================================================= 6-8. BSADF date-stamping (S&P P/D, Bitcoin, family-wise values)
function psyPanels(id, S, lvl, lvlName, ylab, cvs, k, L, title, shadeCv) {
  const d = S.dates, x = d.slice(1), stat = S.bsadf, E = episodes(stat, shadeCv, L, k), y = lvl.map(Math.log);
  const up = e => y[(e.e === null ? k : e.e) + 1] - y[e.s + 1] > 0;
  const shapes = E.map(e => band(x[e.s], x[e.e === null ? k : e.e], up(e) ? AMBER_BAND : TEAL_BAND)).concat([sline(x[k], K.navy, 'dot', 1.2)]);
  const tr = [{ x: d.slice(0, k + 2), y: lvl.slice(0, k + 2), mode: 'lines', name: lvlName, line: { color: K.blue, width: 1.1 }, hovertemplate: '%{x}: %{y:,.2f}<extra></extra>' },
    { x: x.slice(0, k + 1), y: stat.slice(0, k + 1), yaxis: 'y2', mode: 'lines', name: 'BSADF statistic', line: { color: K.red, width: 1.1 }, hovertemplate: '%{x}: BSADF %{y:.2f}<extra></extra>' }];
  cvs.forEach(c => tr.push({ x, y: c.y, yaxis: 'y2', mode: 'lines', name: c.name, line: { color: c.col, width: 1.3, dash: c.dash }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }));
  if (E.some(up)) tr.push(legendBox('Explosive episode, price rising', AMBER_BAND));
  if (E.some(e => !up(e))) tr.push(legendBox('Explosive episode, price falling', TEAL_BAND));
  const L2 = two(); L2.yaxis.title = { text: ylab, font: { size: 12, color: K.navy } }; L2.yaxis.type = 'log'; L2.yaxis.dtick = 1; L2.yaxis2.title = { text: 'Statistic', font: { size: 12, color: K.navy } };
  L2.xaxis.range = [d[0], d[d.length - 1]]; L2.yaxis.range = [Math.log10(Math.min(...lvl)) - 0.05, Math.log10(Math.max(...lvl)) + 0.05];
  const st = stat.filter(v => v !== null); L2.yaxis2.range = [Math.min(...st) - 0.3, Math.max(...st) + 0.3];
  plot(id, tr, layout(Object.assign(L2, { title: ttl(title), shapes, legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top', font: { size: 11 } } })));
  return { E, up };
}
function cursorText(S, cv, k, L) {
  const m = runAbove(S.bsadf, cv, k), v = S.bsadf[k], c = cv[k], dt = fmtM(S.dates[k + 1]);
  if (v === null) return T.before(dt);
  return m === 0 ? T.below(dt, nf(v, 2), nf(c, 2)) : T.above(dt, nf(v, 2), nf(c, 2), m, m >= L);
}
function spPd() {
  const S = D.sp_pd, k = +$('pd-t').value, L = +$('pd-L').value;
  $('pd-t-v').textContent = fmtM(S.dates[k + 1]); $('pd-L-v').textContent = L;
  const { E, up } = psyPanels('pd-chart', S, S.pd, 'Real price-dividend ratio', 'Price / dividend (log scale)', [{ y: S.cv, name: '95% critical value (Monte Carlo)', col: K.green, dash: 'dash' }],
    k, L, `S&P Composite real price-dividend ratio, monthly ${S.dates[0].slice(0, 4)}-${S.dates[S.dates.length - 1].slice(0, 4)}`, S.cv);
  out('pd-out', [cursorText(S, S.cv, k, L), T.eps(L, E.length, epList(E, S.dates.slice(1)), E.filter(e => !up(e)).length, true), T.pd(nf(S.gsadf, 2), nf(S.cv_gsadf['95'], 2), nf(S.cv_gsadf['99'], 2))]);
}
function btc() {
  const S = D.btc, k = +$('bt-t').value, L = +$('bt-L').value, wild = $('bt-cv').value === 'wild';
  $('bt-t-v').textContent = fmtD(S.dates[k + 1]); $('bt-L-v').textContent = L;
  const cv = wild ? S.cv_wild : S.cv_mc;
  const { E } = psyPanels('bt-chart', S, S.p, 'Bitcoin', 'USD (log scale)', [wild ? { y: S.cv_wild, name: '95% critical value (wild bootstrap)', col: K.purple, dash: 'dashdot' }
    : { y: S.cv_mc, name: '95% critical value (Monte Carlo)', col: K.green, dash: 'dash' }], k, L, 'Bitcoin, weekly 2014-2026', cv);
  out('bt-out', [cursorText(S, cv, k, L), T.eps(L, E.length, epList(E, S.dates.slice(1)), 0),
    T.bt(nf(S.gsadf, 2), nf(wild ? S.cv_gsadf_wild : S.cv_gsadf, 2), wild ? T.wildName : T.mcName)]);
}
function fwer() {
  const S = D.btc, F = D.fwer, tau = F.tau[+$('fw-k').value], lev = $('fw-l').value, q = F.q[String(tau)][lev], x = S.dates.slice(1), n = x.length;
  $('fw-k-v').textContent = tau;
  const cvc = new Array(n).fill(q), E = episodes(S.bsadf, cvc, S.L);
  const tr = [{ x, y: S.bsadf, mode: 'lines', name: 'BSADF statistic, Bitcoin weekly', line: { color: K.red, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x, y: S.cv_mc, mode: 'lines', name: '95% pointwise critical value, Monte Carlo', line: { color: K.green, width: 1.3, dash: 'dash' }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x, y: S.cv_wild, mode: 'lines', name: '95% pointwise critical value, wild bootstrap', line: { color: K.purple, width: 1.3, dash: 'dashdot' }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: [x[0], x[n - 1]], y: [q, q], mode: 'lines', name: `Family-wise ${lev.slice(1)}% critical value over ${tau} weeks (Phillips-Shi)`, line: { color: K.orange, width: 2 }, hovertemplate: '%{y:.2f}<extra></extra>' },
    legendBox('Episodes with the family-wise critical value', AMBER_BAND)];
  plot('fw-chart', tr, layout({ title: ttl('Bitcoin, weekly 2014-2026: pointwise vs family-wise critical values for date-stamping'),
    shapes: E.map(e => band(x[e.s], x[e.e === null ? n - 1 : e.e], AMBER_BAND)), xaxis: AX('', { type: 'date' }), yaxis: AX('Statistic') }));
  const qq = F.tau.map(t => F.q[String(t)][lev]);
  out('fw-out', [T.fw(tau, lev.slice(1), nf(q, 2), E.length, epList(E, x)), T.fw2(nf(F.fwer.cv_mc_max, 2), pct(F.fwer.fwer_any, 0), pct(F.fwer.fwer_ep, 0), nf(Math.min(...qq), 2), nf(Math.max(...qq), 2))]);
}

// ================================================================= 9. LPPLS on Bitcoin 2017
function lpplsPath(f, t) {
  const dt = Math.max(f.tc - t, 1e-9), fm = Math.pow(dt, f.m), lg = Math.log(dt);
  return f.A + f.B * fm + fm * (f.C1 * Math.cos(f.w * lg) + f.C2 * Math.sin(f.w * lg));
}
function lppls() {
  const P = D.btcd, Lp = D.lppls, f = Lp.fits[+$('lp-k').value];
  $('lp-k-v').textContent = fmtD(f.t2);
  const i0 = P.dates.indexOf('2017-01-01'), i1 = P.dates.indexOf('2018-03-31'), d = P.dates.slice(i0, i1 + 1), p = P.p.slice(i0, i1 + 1);
  const fd = d.filter(s => yrs(s) < f.tc), fy = fd.map(s => Math.exp(lpplsPath(f, yrs(s))));
  const tcd = f.tc_date, q = f.q ? 'qualified' : 'unqualified';
  plot('lp-chart', [
    { x: d, y: p, mode: 'lines', name: 'Bitcoin (USD, log scale)', line: { color: K.blue, width: 1.2 }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' },
    { x: fd, y: fy, mode: 'lines', name: `LPPLS fit to ${fmtDen(f.t2)} (${q})`, line: { color: K.red, width: 1.8 }, hovertemplate: '%{x}: fit %{y:,.0f}<extra></extra>' },
    { x: [tcd, tcd], y: [null, null], mode: 'lines', name: 'Estimated critical time t<sub>c</sub> = ' + tcd, line: { color: K.orange, width: 1.5, dash: 'dash' } },
    { x: [Lp.peak, Lp.peak], y: [null, null], mode: 'lines', name: 'Actual peak ' + Lp.peak, line: { color: K.green, width: 1.5, dash: 'dashdot' } }
  ], layout({ title: ttl('LPPLS on the 2017 Bitcoin bubble (search space of Shu and Zhu 2020, eq. 11)'),
    shapes: [sline(f.t2, K.navy, 'dot', 1.2), sline(tcd, K.orange, 'dash', 1.5), sline(Lp.peak, K.green, 'dashdot', 1.5)],
    xaxis: AX('', { range: [d[0], d[d.length - 1]] }), yaxis: AX('USD', { type: 'log', tickvals: [500, 1000, 2000, 5000, 10000, 20000], tickformat: ',.0f' }) }));
  const fail = Object.keys(f.cond).filter(c => f.cond[c] === false).map(c => T.cond[c]);
  const err = Math.round((ms(tcd) - ms(Lp.peak)) / DAY);
  out('lp-out', [T.lp(fmtD(f.t2), fmtD(tcd), err, nf(f.m, 2), nf(f.w, 2), nf(f.B, 2)), T.lp2(f.q, fail.join('; '), nf(f.rel_err, 2), nf(f.osc, 1))]);
}
const MON_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const fmtDen = s => (+s.slice(8, 10)) + ' ' + MON_EN[+s.slice(5, 7) - 1] + ' ' + s.slice(0, 4);   // chart text stays English

// ================================================================= 10. stability of the critical time
function tcBlk() {
  const opt = +$('tc-s').value, k = +$('tc-k').value, rows = [], tr = [], lay = {}, titles = [];
  $('tc-k-v').textContent = k;
  [['btc', 'Bitcoin'], ['ndx', 'Nasdaq 100']].forEach(([key, name], j) => {
    const Q = D.tc[key], t1 = Q.starts[opt], P = Q.paths[t1], m = Math.min(k, P.t2.length), ax = j ? { xaxis: 'x2', yaxis: 'y2' } : {}, ends = [P.t2[0], P.t2[P.t2.length - 1]];
    tr.push(Object.assign({ x: P.t2.slice(0, m), y: P.tc.slice(0, m), mode: 'lines+markers', name: 'Estimated critical time t<sub>c</sub>', showlegend: !j, legendgroup: 'a',
        line: { color: K.red, width: 1.2 }, marker: { size: 5, color: K.red }, hovertemplate: 't₂ %{x}<br>t<sub>c</sub> %{y}<extra></extra>' }, ax),
      Object.assign({ x: ends, y: ends, mode: 'lines', name: 'Date of the estimate (t<sub>c</sub> = t<sub>2</sub>)', showlegend: !j, legendgroup: 'b', line: { color: K.navy, width: 1, dash: 'dot' }, hoverinfo: 'skip' }, ax),
      Object.assign({ x: ends, y: [Q.peak, Q.peak], mode: 'lines', name: 'Actual peak', showlegend: !j, legendgroup: 'c', line: { color: K.green, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' }, ax));
    lay['xaxis' + (j ? '2' : '')] = AX('End of the estimation window t<sub>2</sub>', { type: 'date', range: ends });
    lay['yaxis' + (j ? '2' : '')] = AX(j ? '' : 'Estimated t<sub>c</sub>', { type: 'date' });
    titles.push(`${name}: window from ${fmtDen(t1)}`);
    const pk = ms(Q.peak), bef = P.t2.map((t, i) => i).filter(i => ms(P.t2[i]) < pk);
    const mae = mean(bef.map(i => Math.abs(P.err[i]))), w30 = bef.filter(i => Math.abs(P.err[i]) <= 30).length / bef.length, ql = bef.filter(i => P.q[i]).length / bef.length;
    rows.push(T.tc(name, fmtD(t1), fmtD(P.t2[m - 1]), fmtD(P.tc[m - 1]), P.err[m - 1], bef.length, nf(mae, 0), pct(w30, 0), pct(ql, 0)));
  });
  plot('tc-chart', tr, layout(sub2(titles[0], titles[1], lay)));
  out('tc-out', rows);
}

// ================================================================= 11. LPPLS confidence indicator and the evaluation
function ciPrice() {
  const P = D.btcd, CI = D.ci, fall = +$('ci-f').value / 100, H = +$('ci-h').value;
  $('ci-f-v').textContent = pct(fall, 0);
  const pm = P.dates.map(ms), last = pm[pm.length - 1];
  let n = 0, non = 0, hon = 0, hoff = 0; const hx = [], hy = [];
  let j0 = 0;
  CI.dates.forEach((d, i) => {
    const t0 = ms(d); if (t0 + H * DAY > last) return;
    while (pm[j0] < t0) j0++;
    let mn = Infinity; for (let j = j0; j < pm.length && pm[j] <= t0 + H * DAY; j++) mn = Math.min(mn, P.p[j]);
    const hit = mn / P.p[j0] - 1 <= -fall + 1e-12, on = CI.ci[i] > 0;
    n++; if (on) { non++; hon += hit; if (hit) { hx.push(d); hy.push(P.p[j0]); } } else hoff += hit;
  });
  plot('ci-chart', [
    { x: P.dates, y: P.p, mode: 'lines', name: 'Bitcoin (USD, log scale)', line: { color: K.blue, width: 1 }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' },
    { x: CI.dates, y: CI.ci, yaxis: 'y2', type: 'bar', name: 'LPPLS confidence indicator (right axis)', marker: { color: K.red }, width: 6 * DAY, hovertemplate: '%{x}: %{y:.3f}<extra></extra>' },
    { x: hx, y: hy, mode: 'markers', name: `Signal followed by a fall of ${Math.round(100 * fall)}% within ${H} days`, marker: { color: K.orange, size: 6, symbol: 'triangle-down' }, hovertemplate: '%{x}<extra></extra>' }
  ], layout({ title: ttl('Bitcoin: 141 windows of 50-750 observations, every 5 observations'), bargap: 0,
    xaxis: AX('', { type: 'date' }), yaxis: AX('USD', { type: 'log', dtick: 1 }), yaxis2: AX('Indicator', { overlaying: 'y', side: 'right', range: [0, 0.2], showgrid: false }) }));
  out('ci-out', [T.ci(H, pct(fall, 0), n, non, pct(hon / non, 0), pct(hoff / (n - non), 0), pct((hon + hoff) / n, 0)), T.ci2(pct(CI.eval.on_2017, 0), pct(CI.eval.on_2021, 0), nf(CI.eval.max, 2), fmtM(CI.eval.max_date))]);
}

// ================================================================= 12. qualification filters
const FL_YEARS = range(1997, 2026, 1);
function filters() {
  const F = D.filters, k = +$('fl-y').value, yr = k === 0 ? null : FL_YEARS[k - 1];
  $('fl-y-v').textContent = yr === null ? T.allYears : yr;
  const share = tag => {
    const Y = F.years[tag], ys = Object.keys(Y).filter(y => yr === null || +y === yr);
    if (!ys.length) return null;
    const n = sum(ys.map(y => Y[y].n)); return F.keys.map(c => sum(ys.map(y => Y[y][c])) / n);
  };
  const sb = share('btc'), sn = share('ndx'), lab = F.keys.map(c => F.labels[c]);
  const tr = [];
  if (sb) tr.push({ y: lab, x: sb.map(v => 100 * v), type: 'bar', orientation: 'h', name: 'Bitcoin, all windows', marker: { color: K.amber }, hovertemplate: '%{y}: %{x:.1f}%<extra></extra>' });
  if (sn) tr.push({ y: lab, x: sn.map(v => 100 * v), type: 'bar', orientation: 'h', name: 'Nasdaq 100, all windows', marker: { color: K.teal }, hovertemplate: '%{y}: %{x:.1f}%<extra></extra>' });
  plot('fl-chart', tr, layout({ barmode: 'group', title: ttl('Filters of the confidence indicator' + (yr === null ? '' : `, t₂ in ${yr}`)), hovermode: 'closest',
    xaxis: AX('% of windows passing', { range: [0, 100] }), yaxis: AX('', { autorange: 'reversed', categoryorder: 'array', categoryarray: lab }), margin: { l: 210, r: 12, t: 30, b: 40 } }));
  const f = (s, i) => (s ? pct(s[i], 1) : '—');
  out('fl-out', [T.fl(yr === null ? T.allYears : yr, f(sb, 6), f(sn, 6), f(sb, 7), f(sn, 7), f(sb, 8), f(sn, 8))]);
}

// ================================================================= 13. Markov switching, Nasdaq 100
function hamilton(r, mu, sd, p11, p22) {
  const n = r.length, P = [[p11, 1 - p11], [1 - p22, p22]], filt = [], pred = [];
  let pr = [(1 - p22) / (2 - p11 - p22), (1 - p11) / (2 - p11 - p22)];
  const dn = (x, m, s) => Math.exp(-0.5 * ((x - m) / s) ** 2) / s;
  for (let t = 0; t < n; t++) {
    if (t > 0) { const f = filt[t - 1]; pr = [f[0] * P[0][0] + f[1] * P[1][0], f[0] * P[0][1] + f[1] * P[1][1]]; }
    const a = pr[0] * dn(r[t], mu[0], sd[0]), b = pr[1] * dn(r[t], mu[1], sd[1]);
    pred.push(pr); filt.push([a / (a + b), b / (a + b)]);
  }
  const sm = new Array(n); sm[n - 1] = filt[n - 1];
  for (let t = n - 2; t >= 0; t--) {
    const q = [sm[t + 1][0] / pred[t + 1][0], sm[t + 1][1] / pred[t + 1][1]];
    const s0 = filt[t][0] * (P[0][0] * q[0] + P[0][1] * q[1]), s1 = filt[t][1] * (P[1][0] * q[0] + P[1][1] * q[1]);
    sm[t] = [s0 / (s0 + s1), s1 / (s0 + s1)];
  }
  return { fp: filt.map(v => v[1]), sp: sm.map(v => v[1]) };
}
function msBlk() {
  const M = D.ms, p22 = +$('ms-p').value, s2 = +$('ms-s').value;
  $('ms-p-v').textContent = nf(p22, 3); $('ms-s-v').textContent = nf(s2, 2);
  const H = hamilton(M.r, M.mu, [M.sd[0], s2], M.p11, p22), x = M.dates;
  const L2 = two(); L2.yaxis.type = 'log'; L2.yaxis.dtick = 1; L2.yaxis.title = { text: '', font: { size: 12 } }; L2.yaxis2.title = { text: 'P(turbulent regime)', font: { size: 12, color: K.navy } }; L2.yaxis2.range = [-0.02, 1.02];
  plot('ms-chart', [
    { x, y: M.p, mode: 'lines', name: 'Nasdaq 100 (log scale)', line: { color: K.blue, width: 1 }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' },
    { x, y: H.fp, yaxis: 'y2', mode: 'lines', name: 'Filtered probability (full-sample parameters)', line: { color: K.red, width: 0.9 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x, y: H.sp, yaxis: 'y2', mode: 'lines', name: 'Smoothed probability (full sample)', line: { color: K.green, width: 1.3 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }
  ], layout(Object.assign(L2, { title: ttl('Nasdaq 100, weekly log returns 1990-2026: two-regime Markov-switching model'), legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top', font: { size: 11 } } })));
  let kpk = 0; while (kpk + 1 < x.length && x[kpk + 1] <= '2000-03-31') kpk++;
  const share = H.sp.filter(v => v > 0.5).length / H.sp.length;
  out('ms-out', [T.ms(nf(p22, 3), nf(1 / (1 - p22), 1), nf(s2, 2), nf(M.sd[0], 2)), T.ms2(pct(share, 0), fmtD(x[kpk]), nf(H.fp[kpk], 2)),
    T.ms3(nf(M.summary.turb.stay, 3), nf(M.summary.turb.dur, 1), nf(M.summary.turb.sd, 2))]);
}

// ================================================================= 14. LR bootstrap for the number of regimes
const LR_TITLE = { btc_1v2: 'Bitcoin: one vs two regimes', ndx_1v2: 'Nasdaq 100: one vs two regimes', btc_2v3: 'Bitcoin: two vs three regimes' };
function lrBlk() {
  const B = +$('lr-B').value, rows = [], tr = [], sh = [], titles = [], lay = {};
  $('lr-B-v').textContent = B;
  [$('lr-s').value, 'btc_2v3'].forEach((key, j) => {
    const o = D.lr[key], v = o.lrs.slice(0, B), q95 = quantile(v, 0.95), mx = Math.max(...v), p = (1 + v.filter(z => z >= o.lr).length) / (B + 1);
    const far = o.lr > 3 * Math.max(mx, o.chi2_95), ax = j ? { xaxis: 'x2', yaxis: 'y2' } : {}, xr = j ? 'x2' : 'x';
    tr.push(Object.assign({ x: v, type: 'histogram', nbinsx: 30, name: 'Parametric-bootstrap LR under the null', showlegend: !j, marker: { color: K.blue, opacity: 0.7, line: { color: '#fff', width: 0.5 } }, hovertemplate: 'LR %{x}: %{y}<extra></extra>' }, ax));
    sh.push(vl(q95, xr, K.green, 'dash'), vl(o.chi2_95, xr, K.purple, 'dot'));
    if (!far) sh.push(vl(o.lr, xr, K.red, 'solid'));
    titles.push(LR_TITLE[key] + (far ? ` (observed LR = ${o.lr.toFixed(0)})` : ''));
    lay['xaxis' + (j ? '2' : '')] = AX('LR statistic', { range: [0, 1.08 * Math.max(mx, o.chi2_95, far ? 0 : o.lr)] }); lay['yaxis' + (j ? '2' : '')] = AX(j ? '' : 'Count');
    rows.push(T.lr(T.lrName[key], nf(o.lr, 1), B, nf(q95, 1), nf(mx, 1), nf(p, 3), nf(o.chi2_95, 1), o.df));
  });
  tr.push({ x: [null], y: [null], mode: 'lines', name: 'Bootstrap 95% critical value', line: { color: K.green, dash: 'dash', width: 2 } },
    { x: [null], y: [null], mode: 'lines', name: 'Naive chi-square 95% value', line: { color: K.purple, dash: 'dot', width: 2 } },
    { x: [null], y: [null], mode: 'lines', name: 'Observed LR', line: { color: K.red, width: 2 } });
  lay.shapes = sh; lay.bargap = 0.05;
  plot('lr-chart', tr, layout(sub2(titles[0], titles[1], lay)));
  out('lr-out', rows.concat([T.lr2(B, nf(1 / (B + 1), 3))]));
}

// ================================================================= 15. dot-com and AI
function aiBlk() {
  const A = D.ai, m = +$('ai-m').value, rows = [], tr = [];
  $('ai-m-v').textContent = m;
  const S = [[['csco', 'Cisco from ', K.teal], ['nvda', 'NVIDIA from ', K.green]], [['ndx95', 'Nasdaq 100 from ', K.blue], ['ndx23', 'Nasdaq 100 from ', K.red]]];
  S.forEach((ser, j) => {
    for (const [k, lab, col] of ser) {
      tr.push(Object.assign({ x: A[k].y.map((_, i) => i), y: A[k].y, mode: 'lines', name: lab + fmtMen(A[k].start), line: { color: col, width: 1.6 },
        hovertemplate: lab + fmtMen(A[k].start) + '<br>month %{x}: %{y:.0f}<extra></extra>' }, j ? { xaxis: 'x2', yaxis: 'y2' } : {}));
      const y = A[k].y, mm = Math.min(m, y.length - 1), seg = y.slice(0, mm + 1), pk = seg.indexOf(Math.max(...seg));
      rows.push(T.ai(T.aiName[k], fmtM(A[k].start), mm, A[k].dates[mm] ? fmtM(A[k].dates[mm]) : '', nf(y[mm] / 100, 1), pk, nf(seg[pk] / 100, 1), m > y.length - 1));
    }
  });
  const ya = { type: 'log', tickvals: [50, 100, 200, 500, 1000], range: [Math.log10(40), Math.log10(1200)] };
  plot('ai-chart', tr, layout(sub2('Stocks: dot-com vs AI', 'Nasdaq 100: 1990s vs 2020s', {
    xaxis: AX('Months since the first explosive signal', { range: [0, 96] }), yaxis: AX('Price, first signal = 100 (log scale)', ya),
    xaxis2: AX('Months since the first explosive signal', { range: [0, 96] }), yaxis2: AX('', ya),
    shapes: [hl(100, 1, K.navy), hl(100, 2, K.navy), vl(m, 'x', K.navy, 'dot'), vl(m, 'x2', K.navy, 'dot')] })));
  out('ai-out', rows);
}

const fmtMen = s => MON_EN[+s.slice(5, 7) - 1] + ' ' + s.slice(0, 4);

// ================================================================= 16. U.S. housing cycle
function dnz() {
  const Z = D.dnz, k = +$('dz-t').value, raw = $('dz-v').value === 'raw', v = raw ? Z.vol_raw : Z.vol, x = Z.dates;
  $('dz-t-v').textContent = fmtM(x[k]);
  const am = a => { let j = 0; for (let i = 1; i <= k; i++) if (a[i] > a[j]) j = i; return j; };
  const jv = am(v), jp = am(Z.price), quiet = jp > jv ? (+x[jp].slice(0, 4) - +x[jv].slice(0, 4)) * 12 + (+x[jp].slice(5) - +x[jv].slice(5)) : 0;
  const tr = [{ x: x.slice(0, k + 1), y: Z.price.slice(0, k + 1), mode: 'lines', name: 'Case-Shiller U.S. National Home Price Index', line: { color: K.blue, width: 2 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' },
    { x: x.slice(0, k + 1), y: v.slice(0, k + 1), mode: 'lines', name: raw ? 'New one-family houses sold, not adjusted' : 'New one-family houses sold, calendar-month adjusted', line: { color: K.red, width: 1.5 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }];
  const sh = [hline(100, K.navy, 'dot')];
  if (quiet > 0) { sh.push(band(x[jv], x[jp], AMBER_BAND)); tr.unshift(legendBox(`Quiet: peak of volume (${fmtMen(x[jv])}) to peak of prices (${fmtMen(x[jp])})`, AMBER_BAND)); }
  plot('dz-chart', tr, layout({ title: ttl(`U.S. housing cycle, monthly 2000-2011: prices and volume`), shapes: sh, xaxis: AX('', { type: 'date', range: [x[0], x[x.length - 1]] }), yaxis: AX('Index, 2000 average = 100', { range: [20, 190] }) }));
  out('dz-out', [T.dz(fmtM(x[k]), nf(Z.price[k], 0), nf(v[k], 0), fmtM(x[jv]), nf(v[jv], 0), fmtM(x[jp]), nf(Z.price[jp], 0), quiet, raw)]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms_) => new Player(btn, $(id), vals, ms_);
  on(['rb-pi', 'rb-b'], rational); P('rb-play', 'rb-pi', range(0.9, 0.995, 0.005), 260);
  on(['ep-h', 'ep-sel'], episodesBlk); P('ep-play', 'ep-h', range(0.25, 2, 0.25), 700);
  $('gs-c').value = D.gsy.falls.indexOf(0.4); on(['gs-c'], gsy); P('gs-play', 'gs-c', range(0, D.gsy.falls.length - 1, 1), 800);
  on(['wi-r', 'wi-T'], windows); P('wi-play', 'wi-r', range(0.05, 0.5, 0.05), 600);
  $('nu-k').max = D.null.rows.length - 1; $('nu-k').value = D.null.rows.findIndex(r => r.w0 === D.null.w0_rule); on(['nu-k'], nullDist); P('nu-play', 'nu-k', range(0, D.null.rows.length - 1, 1), 1000);
  const nP = D.sp_pd.bsadf.length - 1, w0P = D.sp_pd.w0 - 1;
  $('pd-t').min = w0P; $('pd-t').max = nP; $('pd-t').value = nP; $('pd-L').value = D.sp_pd.L; on(['pd-t', 'pd-L'], spPd); P('pd-play', 'pd-t', range(w0P, nP, 6).concat([nP]), 60);
  const nB = D.btc.bsadf.length - 1, w0B = D.btc.w0 - 1;
  $('bt-t').min = w0B; $('bt-t').max = nB; $('bt-t').value = nB; $('bt-L').value = D.btc.L; on(['bt-t', 'bt-L', 'bt-cv'], btc); P('bt-play', 'bt-t', range(w0B, nB, 2).concat(nB % 2 === w0B % 2 ? [] : [nB]), 60);
  $('fw-k').max = D.fwer.tau.length - 1; $('fw-k').value = D.fwer.tau.indexOf(104); on(['fw-k', 'fw-l'], fwer); P('fw-play', 'fw-k', range(0, D.fwer.tau.length - 1, 1), 900);
  $('lp-k').max = D.lppls.fits.length - 1; $('lp-k').value = D.lppls.fits.findIndex(f => f.t2 === '2017-11-15'); on(['lp-k'], lppls); P('lp-play', 'lp-k', range(0, D.lppls.fits.length - 1, 1), 500);
  const nT = Math.max(...['btc', 'ndx'].map(k => D.tc[k].paths[D.tc[k].starts[1]].t2.length));
  $('tc-k').max = nT; $('tc-k').value = nT; on(['tc-k', 'tc-s'], tcBlk); P('tc-play', 'tc-k', range(1, nT, 1), 250);
  on(['ci-f', 'ci-h'], ciPrice); P('ci-play', 'ci-f', range(10, 50, 5), 700);
  $('fl-y').max = FL_YEARS.length; on(['fl-y'], filters); P('fl-play', 'fl-y', range(1, FL_YEARS.length, 1), 500);
  $('ms-p').value = D.ms.p22; $('ms-s').value = D.ms.sd[1]; on(['ms-p', 'ms-s'], msBlk); P('ms-play', 'ms-p', range(0.8, 0.995, 0.005), 200);
  on(['lr-B', 'lr-s'], lrBlk); P('lr-play', 'lr-B', range(19, 199, 10), 300);
  on(['ai-m'], aiBlk); P('ai-play', 'ai-m', range(0, 96, 1), 120);
  $('dz-t').max = D.dnz.dates.length - 1; $('dz-t').value = D.dnz.dates.length - 1; on(['dz-t', 'dz-v'], dnz); P('dz-play', 'dz-t', range(0, D.dnz.dates.length - 1, 1), 70);
  rational(); episodesBlk(); gsy(); windows(); nullDist(); spPd(); btc(); fwer(); lppls(); tcBlk(); ciPrice(); filters(); msBlk(); lrBlk(); aiBlk(); dnz();
}
window.CH17 = { episodes, hamilton, quantile, lpplsPath, yrs };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

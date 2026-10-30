// Chapter 18 interactive page: one block per chart slide, computed in the browser from ch18_data.js.
(function () {
'use strict';
const D = window.CH18_DATA;
const { mean, sdev, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, solve, predict, exitTicket } = window.MFMI;
const T = window.CH18_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  teal: '#17A2B8', navy: '#1F2A44', band: '#C5D2E8' };
const RCOL = { US: K.blue, EU: K.red, RO: K.green };
const RLAB = { US: 'US banks', EU: 'European banks', RO: 'Romanian banks (BVB)' };
const B = D.banks, NAME = Object.fromEntries(B.map((k, i) => [k, D.names[i]])), REG = Object.fromEntries(B.map((k, i) => [k, D.region[i]]));
function LY(extra) {                 // shared layout; legend lower when the x axis has a title
  const l = layout(extra), xt = l.xaxis && l.xaxis.title && l.xaxis.title.text;
  l.legend = Object.assign({}, layout().legend, { traceorder: 'normal' }, xt ? { y: -0.3 } : {}, (extra || {}).legend || {});
  return l;
}
const eventMarks = (x0, x1) => {     // vertical event lines with their labels (mark_events)
  const ev = D.events.filter(([d]) => d >= x0 && d <= x1);
  return { shapes: ev.map(([d]) => ({ type: 'line', xref: 'x', yref: 'paper', x0: d, x1: d, y0: 0, y1: 1, line: { color: K.navy, width: 1, dash: 'dot' } })),
    annotations: ev.map(([d, l]) => ({ x: d, xref: 'x', yref: 'paper', y: 1, text: l, textangle: -90, showarrow: false, xanchor: 'right', yanchor: 'top', font: { size: 10, color: K.navy } })) };
};
const ranks = a => { const o = a.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]), r = new Array(a.length); o.forEach(([, i], k) => (r[i] = k + 1)); return r; };
function pearson(x, y) {             // correlation on the pairs where both values exist (pandas Series.corr)
  const p = x.map((v, i) => [v, y[i]]).filter(([a, b]) => a !== null && b !== null && isFinite(a) && isFinite(b));
  const mx = mean(p.map(q => q[0])), my = mean(p.map(q => q[1]));
  let sxy = 0, sxx = 0, syy = 0; for (const [a, b] of p) { sxy += (a - mx) * (b - my); sxx += (a - mx) ** 2; syy += (b - my) ** 2; }
  return sxy / Math.sqrt(sxx * syy);
}
const spearman = (x, y) => pearson(ranks(x), ranks(y));
const argmax = a => a.reduce((b, v, i) => (v > a[b] ? i : b), 0), argmin = a => a.reduce((b, v, i) => (v < a[b] ? i : b), 0);
const mplScale = c => c.map((v, i) => [i / (c.length - 1), v]);   // matplotlib Blues and RdBu
const BLUES = mplScale(['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']);
const RDBU = mplScale(['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061']);
const pp = (x, d = 1) => (x > 0 ? '+' : '') + nf(x, d);

// ================================================================= regional bank portfolios
let biMonths = null;
function bankIndices() {
  const dt = D.dates;
  if (!biMonths) { biMonths = dt.map((s, i) => (i === 0 || s.slice(0, 7) !== dt[i - 1].slice(0, 7) ? i : -1)).filter(i => i >= 0); $('bi-s').max = biMonths.length - 13; }
  const i0 = biMonths[+$('bi-s').value], x = dt.slice(i0);
  $('bi-s-v').textContent = dt[i0];
  const st = {}, tr = [];
  for (const rg of ['US', 'EU', 'RO']) {
    const r = D.idx[rg].simple, y = []; let v = 100, pk = 100, dd = 0, ddi = i0;
    for (let t = i0; t < dt.length; t++) { v *= 1 + r[t] / 1e5; y.push(v); if (v > pk) pk = v; if (v / pk - 1 < dd) { dd = v / pk - 1; ddi = t; } }
    st[rg] = { last: v, dd, ddd: dt[ddi], vol: sdev(D.idx[rg].logm.slice(i0).map(z => z / 1000)) * Math.sqrt(252) };
    tr.push({ x, y, mode: 'lines', name: RLAB[rg] + ' (equal weights)', line: { color: RCOL[rg], width: 1.3 }, hovertemplate: rg + ' %{x}: %{y:.0f}<extra></extra>' });
  }
  const em = eventMarks(x[0], x[x.length - 1]);
  plot('bi-chart', tr, LY({ title: ttl('Synthetic index of local-currency returns, ' + dt[i0] + ' = 100 (daily rebalancing)'), shapes: [hline(100, K.navy), ...em.shapes], annotations: em.annotations,
    xaxis: AX('', { type: 'date' }), yaxis: AX('Index (start = 100)') }));
  out('bi-out', ['US', 'EU', 'RO'].map(rg => T.bi(T.reg[rg], nf(st[rg].last, 0), pct(-st[rg].dd, 0), st[rg].ddd, nf(st[rg].vol, 0))));
}

// ================================================================= MES
function mesBars() {
  const M = D.mes, j = +$('me-a').value - 1, a = M.alphas[j], v = B.map(k => M.bank[k][j]), five = Math.abs(a - 0.05) < 1e-9;
  $('me-a-v').textContent = pct(a, 0);
  const lab = B.map(k => NAME[k]), mk = B.map(k => M.market[REG[k]][j]);
  plot('me-chart', [
    ...['US', 'EU', 'RO'].map(rg => ({ x: lab.filter((_, i) => REG[B[i]] === rg), y: v.filter((_, i) => REG[B[i]] === rg), type: 'bar', name: { US: 'US banks (market: S&P 500)', EU: 'European banks (market: Euro Stoxx 50)', RO: 'Romanian banks (market: BET)' }[rg],
      marker: { color: RCOL[rg], line: { color: '#fff', width: 1.5 } }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>',
      error_y: five ? { type: 'data', symmetric: false, array: B.map((k, i) => [k, M.hi[i] - v[i]]).filter(([k]) => REG[k] === rg).map(q => q[1]), arrayminus: B.map((k, i) => [k, v[i] - M.lo[i]]).filter(([k]) => REG[k] === rg).map(q => q[1]), color: K.navy, thickness: 1.2, width: 3 } : { visible: false } })),
    { x: lab, y: mk, mode: 'markers', name: 'Market index on the same days', marker: { symbol: 'line-ew-open', size: 22, color: K.navy, line: { width: 2.5, color: K.navy } }, hovertemplate: '%{x}, market: %{y:.2f}%<extra></extra>' }
  ], LY({ barmode: 'overlay', bargap: 0.3, legend: { y: -0.42 }, title: ttl(`MES ${pct(a, 0)}: mean loss on the worst ${pct(a, 0)} of market days` + (five ? '; 95% block-bootstrap intervals' : '')),
    xaxis: AX('', { tickangle: -35, categoryorder: 'array', categoryarray: lab }), yaxis: AX(`MES ${pct(a, 0)} (daily loss, %)`, { rangemode: 'tozero' }) }));
  const us = B.filter(k => REG[k] === 'US'), eu = B.filter(k => REG[k] === 'EU'), V = k => M.bank[k][j];
  const umin = us.reduce((p, k) => (V(k) < V(p) ? k : p)), umax = us.reduce((p, k) => (V(k) > V(p) ? k : p)), emax = eu.reduce((p, k) => (V(k) > V(p) ? k : p));
  out('me-out', [T.me1(pct(a, 0), NAME[umin], nf(V(umin), 2), NAME[umax], nf(V(umax), 2), NAME[emax], nf(V(emax), 2)),
    T.me2(nf(M.market.US[j], 2), nf(M.market.EU[j], 2), nf(V('HSBA'), 2), nf(V('TLV'), 2), nf(V('BRD'), 2), nf(M.market.RO[j], 2))]);
}

// ================================================================= SRISK
const sriskRatio = (lr, L, k) => k * (L - 1) - (1 - k) * (1 - lr);
const breakEven = (lr, k) => 1 + (1 - k) * (1 - lr) / k;
function srisk() {
  const S = D.srisk, k = +$('sr-k').value / 100, Lv = +$('sr-l').value, LR = Object.fromEntries(B.map((b, i) => [b, S.lrmes[i]]));
  $('sr-k-v').textContent = pct(k, 1); $('sr-l-v').textContent = nf(Lv, 1);
  const Ls = range(2, 20, 0.1), cols = [K.red, K.amber, K.blue];
  plot('sr-chart', [
    ...S.pick.map((b, i) => ({ x: Ls, y: Ls.map(L => 100 * sriskRatio(LR[b], L, k)), mode: 'lines', name: `${NAME[b]}: LRMES ${(100 * LR[b]).toFixed(0)}%, break-even leverage ${breakEven(LR[b], k).toFixed(1)}`,
      line: { color: cols[i], width: 2 }, hovertemplate: NAME[b] + ', L = %{x:.1f}: %{y:.1f}%<extra></extra>' })),
    { x: S.pick.map(b => breakEven(LR[b], k)), y: S.pick.map(() => 0), mode: 'markers', marker: { color: cols, size: 9 }, showlegend: false, hovertemplate: 'L* = %{x:.1f}<extra></extra>' }
  ], LY({ title: ttl(`SRISK / market equity with k = ${(100 * k).toFixed(1)}%`), shapes: [hline(0, K.navy), vline(Lv, K.navy, 'dot')],
    xaxis: AX('Quasi-market leverage (assumed)<br>L = (debt + market equity) / market equity', { range: [2, 20] }), yaxis: AX('SRISK / market equity (%)'), legend: { y: -0.36 } }));
  const Lst = B.map(b => breakEven(LR[b], k));
  plot('sr-bar', [{ x: B.map(b => NAME[b]), y: Lst, type: 'bar', marker: { color: B.map(b => RCOL[REG[b]]), line: { color: '#fff', width: 1.5 } }, hovertemplate: '%{x}: L* = %{y:.1f}<extra></extra>', showlegend: false }],
    LY({ title: ttl(`Break-even leverage L* of the 13 banks, k = ${(100 * k).toFixed(1)}%`), shapes: [hline(Lv, K.navy, 'dot')], xaxis: AX('', { tickangle: -35 }), yaxis: AX('L* (above it, SRISK > 0)', { range: [0, Math.max(...Lst, Lv) + 1] }) }));
  const lo = Math.min(...Lst), hi = Math.max(...Lst), short = B.filter((b, i) => Lv > Lst[i]).length;
  out('sr-out', [T.sr1(pct(k, 1), ...S.pick.flatMap(b => [NAME[b], nf(breakEven(LR[b], k), 1)]), nf(lo - 1, 1), nf(hi - 1, 1)),
    T.sr2(nf(Lv, 1), short, ...S.pick.flatMap(b => [NAME[b], nf(100 * sriskRatio(LR[b], Lv, k), 1)]))]);
}

// ================================================================= CoVaR: quantile regression for JPMorgan
const CV = (k, j) => Object.fromEntries(D.covar.fields.map((f, i) => [f, D.covar.v[k][j][i]]));
function covarQR() {
  const j = +$('qr-a').value - 1, a = D.covar.alphas[j], c = CV('JPM', j), n = +$('qr-t').value, Q = D.qr, [am, bm] = Q.med;
  $('qr-a-v').textContent = pct(a, 0); $('qr-t-v').textContent = D.dates[n - 1];
  const x = Q.x.slice(0, n).map(v => v / 1000), y = Q.y.slice(0, n).map(v => v / 1000), g = [-15, 15];
  const below = x.filter((v, i) => y[i] < c.a + c.b * v).length;
  plot('qr-chart', [
    { x, y, mode: 'markers', name: `Daily returns, ${D.dates[0].slice(0, 4)} to ${D.dates[n - 1]}`, marker: { color: K.teal, size: 4, opacity: 0.45 }, hovertemplate: 'JPM %{x:.2f}%, others %{y:.2f}%<extra></extra>' },
    { x: g, y: g.map(v => c.a + c.b * v), mode: 'lines', name: `${pct(a, 0)} quantile regression: ${c.a.toFixed(2)} + ${c.b.toFixed(2)} x`, line: { color: K.red, width: 2 }, hoverinfo: 'skip' },
    { x: g, y: g.map(v => am + bm * v), mode: 'lines', name: `50% quantile regression: ${am.toFixed(2)} + ${bm.toFixed(2)} x`, line: { color: K.blue, width: 2, dash: 'dash' }, hoverinfo: 'skip' }
  ], LY({ title: ttl('Other US banks (equal weights) against JPMorgan'), shapes: [vline(-c.var_i, K.navy, 'dot')],
    annotations: [{ x: -c.var_i, y: 1, yref: 'paper', text: ` JPMorgan at its VaR ${pct(a, 0)}`, showarrow: false, xanchor: 'left', yanchor: 'top', font: { size: 11, color: K.navy } }],
    xaxis: AX('JPMorgan daily return (%)', { range: [-15, 15] }), yaxis: AX('Other US banks (equal weights, %)', { range: [-17, 17] }), legend: { y: -0.22 } }));
  out('qr-out', [T.qr1(pct(a, 0), nf(c.a, 2), nf(c.b, 2), nf(am, 2), nf(bm, 2)),
    T.qr2(pct(a, 0), nf(c.var_i, 2), nf(c.covar, 2), nf(c.var_sys, 2), nf(c.covar_med, 2), nf(c.dcovar, 2)),
    T.qr3(n, below, pct(below / n, 1), pct(a, 0))]);
}

// ================================================================= ΔCoVaR of eleven banks
function dcovar() {
  const j = +$('dc-a').value - 1, a = D.covar.alphas[j], ks = D.covar.banks, v = ks.map(k => CV(k, j).dcovar), ci = D.covar.ci[String(a)];
  $('dc-a-v').textContent = pct(a, 0);
  const lab = ks.map(k => NAME[k]);
  plot('dc-chart', ['US', 'EU'].map(rg => {
    const I = ks.map((k, i) => i).filter(i => REG[ks[i]] === rg);
    return { x: I.map(i => lab[i]), y: I.map(i => v[i]), type: 'bar', name: rg === 'US' ? 'US banks (system: other US banks)' : 'European banks (system: other European banks)',
      marker: { color: RCOL[rg], line: { color: '#fff', width: 1.5 } }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>',
      error_y: ci ? { type: 'data', symmetric: false, array: I.map(i => ci[ks[i]][1] - v[i]), arrayminus: I.map(i => v[i] - ci[ks[i]][0]), color: K.navy, thickness: 1.2, width: 3 } : { visible: false } };
  }), LY({ barmode: 'overlay', bargap: 0.3, legend: { y: -0.4 }, title: ttl(`ΔCoVaR ${pct(a, 0)}` + (ci ? ' with 95% block-bootstrap intervals' : ' (intervals computed at 1% and 5% only)')),
    xaxis: AX('', { tickangle: -35, categoryorder: 'array', categoryarray: lab }), yaxis: AX(`ΔCoVaR ${pct(a, 0)} (additional system loss, %)`, { rangemode: 'tozero' }) }));
  const lo = argmin(v), hi = argmax(v), v1 = ks.map(k => CV(k, 0).dcovar);
  out('dc-out', [T.dc(pct(a, 0), lab[lo], nf(v[lo], 2), lab[hi], nf(v[hi], 2), nf(spearman(v1, v), 2), nf(CV('JPM', j).dcovar, 2))]);
}

// ================================================================= VaR against ΔCoVaR
const VD_POS = { 'Deutsche Bank': 'bottom center', ING: 'top center', 'Goldman Sachs': 'top right', HSBC: 'bottom center', 'Morgan Stanley': 'top right' };
function varDcovar() {
  const j = +$('vd-a').value - 1, a = D.covar.alphas[j], ks = D.covar.banks, P = ks.map(k => CV(k, j));
  $('vd-a-v').textContent = pct(a, 0);
  plot('vd-chart', ['US', 'EU'].map(rg => {
    const I = ks.map((k, i) => i).filter(i => REG[ks[i]] === rg);
    return { x: I.map(i => P[i].var_i), y: I.map(i => P[i].dcovar), text: I.map(i => NAME[ks[i]]), mode: 'markers+text', textposition: I.map(i => VD_POS[NAME[ks[i]]] || 'middle right'),
      textfont: { size: 10, color: K.navy }, name: RLAB[rg], marker: { color: RCOL[rg], size: 10 }, hovertemplate: '%{text}: VaR %{x:.2f}%, ΔCoVaR %{y:.2f}%<extra></extra>' };
  }), LY({ title: ttl(`VaR ${pct(a, 0)} of the bank and its ΔCoVaR ${pct(a, 0)}`), xaxis: AX(`VaR ${pct(a, 0)} of the bank (daily loss, %)`), yaxis: AX(`ΔCoVaR ${pct(a, 0)} (additional system loss, %)`) }));
  const vr = P.map(p => p.var_i), top = ranks(vr).map((r, i) => [r, i]).sort((x, y) => y[0] - x[0]).slice(0, 2).map(q => q[1]);
  out('vd-out', [T.vd(pct(a, 0), nf(spearman(vr, P.map(p => p.dcovar)), 2), NAME[ks[top[0]]], nf(vr[top[0]], 2), NAME[ks[top[1]]], nf(vr[top[1]], 2), nf(P[0].var_i, 2), nf(P[0].dcovar, 2))]);
}

// ================================================================= contribution against exposure
function exposure() {
  const j = +$('ex-a').value - 1, a = D.covar.alphas[j], ks = D.covar.banks, P = ks.map(k => CV(k, j)), lab = ks.map(k => NAME[k]);
  $('ex-a-v').textContent = pct(a, 0);
  plot('ex-chart', [
    { x: lab, y: P.map(p => p.dcovar), type: 'bar', name: `System ΔCoVaR ${pct(a, 0)}: bank distress minus median state`, marker: { color: K.blue, line: { color: '#fff', width: 1.5 } }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: lab, y: P.map(p => p.exp_dcovar), type: 'bar', name: `Bank exposure ΔCoVaR ${pct(a, 0)}: system distress minus median state`, marker: { color: K.orange, line: { color: '#fff', width: 1.5 } }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], LY({ barmode: 'group', bargap: 0.25, title: ttl('Contribution and exposure'), xaxis: AX('', { tickangle: -35 }), yaxis: AX('Additional loss relative to median state (%)', { rangemode: 'tozero' }), legend: { y: -0.4 } }));
  const C = k => P[ks.indexOf(k)], eu = ks.filter(k => REG[k] === 'EU'), more = eu.filter(k => C(k).exp_dcovar > C(k).dcovar).length;
  out('ex-out', [T.ex(pct(a, 0), nf(C('INGA').dcovar, 2), nf(C('INGA').exp_dcovar, 2), nf(C('BNP').dcovar, 2), nf(C('BNP').exp_dcovar, 2), nf(C('HSBA').dcovar, 2), nf(C('HSBA').exp_dcovar, 2), more, eu.length)]);
}

// ================================================================= connectedness table
function spillStats(th) {          // systemic.spillover_table
  const n = th.length, off = th.map((r, i) => r.map((v, j) => (i === j ? 0 : v)));
  const frm = off.map(r => r.reduce((s, v) => s + v, 0)), to = B.map((_, j) => off.reduce((s, r) => s + r[j], 0));
  return { frm, to, net: to.map((v, i) => v - frm[i]), total: frm.reduce((s, v) => s + v, 0) / n, pn: off.map((r, i) => r.map((_, j) => off[j][i] - off[i][j])) };
}
const block = (th, a, b) => {      // average share of a bank of region b due to shocks of region a
  const rb = B.map((k, i) => i).filter(i => REG[B[i]] === b), ca = B.map((k, i) => i).filter(i => REG[B[i]] === a);
  return rb.reduce((s, i) => s + ca.reduce((t, j) => t + th[i][j], 0), 0) / rb.length;
};
function spillTable() {
  const h = +$('st-h').value, th = D.spill.theta[h - 1], S = spillStats(th);
  $('st-h-v').textContent = h;
  plot('st-chart', [{ z: th, x: B, y: B.map(k => NAME[k]), type: 'heatmap', zmin: 0, zmax: 40, colorscale: BLUES, texttemplate: '%{z:.0f}', textfont: { size: 10 },
    colorbar: { title: { text: `Share of the ${h}-day<br>forecast error variance (%)`, side: 'right', font: { size: 11 } }, thickness: 12 }, hovertemplate: '%{y} from %{x}: %{z:.1f}%<extra></extra>' }],
    LY({ title: ttl(`VAR(${D.spill.p}) on log range volatility, ${D.spill.start} to ${D.spill.end}, H = ${h}`), margin: { l: 130, r: 10, t: 30, b: 50 },
      xaxis: AX('Shock from (column, ticker)', { side: 'bottom', tickfont: { size: 10 } }), yaxis: AX('', { autorange: 'reversed', tickfont: { size: 10 } }) }));
  out('st-out', [T.st1(h, nf(S.total, 1), nf(D.spill.total_ret, 1)),
    T.st2(nf(block(th, 'US', 'US'), 1), nf(block(th, 'EU', 'EU'), 1), nf(block(th, 'US', 'EU'), 1), nf(block(th, 'EU', 'US'), 1)),
    T.st3(nf(th[11][11], 1), nf(th[12][12], 1), nf(block(th, 'US', 'RO'), 1), nf(block(th, 'EU', 'RO'), 1))]);
}

// ================================================================= net spillover network
function quantile(a, q) {          // numpy.quantile, linear interpolation
  const s = [...a].sort((x, y) => x - y), h = (s.length - 1) * q, l = Math.floor(h);
  return l + 1 < s.length ? s[l] + (h - l) * (s[l + 1] - s[l]) : s[l];
}
function spillNetwork() {
  const q = +$('sn-q').value, h = +$('sn-h').value, S = spillStats(D.spill.theta[h - 1]), n = B.length;
  $('sn-q-v').textContent = pct(1 - q, 0); $('sn-h-v').textContent = h;
  const ang = B.map((_, i) => Math.PI / 2 - 2 * Math.PI * i / n), P = ang.map(a => [Math.cos(a), Math.sin(a)]);
  const pos = S.pn.flat().filter(v => v > 0), thr = quantile(pos, q), ann = [];
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    const v = S.pn[i][j]; if (!(v > thr)) continue;
    const [x0, y0] = P[i], [x1, y1] = P[j], f = 0.84, g = 0.06;
    ann.push({ x: x1 * f + (x0 - x1) * g, y: y1 * f + (y0 - y1) * g, ax: x0 * f + (x1 - x0) * g, ay: y0 * f + (y1 - y0) * g, xref: 'x', yref: 'y', axref: 'x', ayref: 'y', text: '', showarrow: true,
      arrowhead: 2, arrowsize: 1, arrowwidth: Math.min(0.6 + 0.6 * v, 6), arrowcolor: 'rgba(142,68,173,0.7)' });
  }
  B.forEach((k, i) => { const [x, y] = P[i]; ann.push({ x: 1.2 * x, y: 1.14 * y, text: NAME[k], showarrow: false, xanchor: x > 0.2 ? 'left' : x < -0.2 ? 'right' : 'center', font: { size: 11, color: K.navy } }); });
  plot('sn-chart', [
    ...['US', 'EU', 'RO'].map(rg => { const I = B.map((_, i) => i).filter(i => REG[B[i]] === rg);
      return { x: I.map(i => P[i][0]), y: I.map(i => P[i][1]), text: I.map(i => NAME[B[i]]), customdata: I.map(i => [S.to[i], S.net[i]]), mode: 'markers', name: RLAB[rg],
        marker: { color: RCOL[rg], opacity: 1, size: I.map(i => 1.25 * Math.sqrt(60 + 6 * S.to[i])) }, hovertemplate: '%{text}<br>to others %{customdata[0]:.1f}, net %{customdata[1]:.1f}<extra></extra>' }; }),
    { x: [null], y: [null], mode: 'lines', name: `Net pairwise spillover (top ${pct(1 - q, 0)} of links)`, line: { color: K.purple, width: 2 } }
  ], LY({ title: ttl(`Arrow i → j when i transmits net to j; H = ${h}`), annotations: ann, margin: { l: 10, r: 10, t: 30, b: 10 },
    xaxis: AX('', { range: [-1.75, 1.75], visible: false }), yaxis: AX('', { range: [-1.35, 1.35], visible: false, scaleanchor: 'x' }), legend: { y: -0.02 } }));
  const ord = S.net.map((v, i) => [v, i]).sort((x, y) => y[0] - x[0]), f4 = a => a.map(([v, i]) => `${NAME[B[i]]} (${pp(v)})`).join(', ');
  out('sn-out', [T.sn1(ann.length - n, pct(1 - q, 0), nf(thr, 2)), T.sn2(f4(ord.slice(0, 4))), T.sn3(f4(ord.slice(-4).reverse()))]);
}

// ================================================================= rolling connectedness
function spillRolling() {
  const w = $('sp-w').value, h = $('sp-h').value, R = D.roll[w + '_' + h], dt = D.roll['dates_' + w], last = dt.length - 1;
  $('sp-t').max = last; if (+$('sp-t').value > last) $('sp-t').value = last;
  const k = +$('sp-t').value, x = dt.slice(0, k + 1), tot = R.total.slice(0, k + 1);
  $('sp-t-v').textContent = dt[k];
  const em = eventMarks(dt[0], dt[k]), xr = [dt[0], dt[last]];
  plot('sp-tot', [{ x, y: tot, mode: 'lines', name: `Total connectedness index (${w}-day window)`, line: { color: K.purple, width: 1.6 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' }],
    LY({ title: ttl(`VAR(2), H = ${h}, every 5 days`), shapes: em.shapes, annotations: em.annotations, xaxis: AX('', { type: 'date', range: xr }), yaxis: AX('Total index (%)', { range: [30, 95] }) }));
  plot('sp-net', ['US', 'EU', 'RO'].map(rg => ({ x, y: R[rg].slice(0, k + 1), mode: 'lines', name: 'Net spillover of ' + RLAB[rg], line: { color: RCOL[rg], width: 1.3 }, hovertemplate: rg + ' %{x}: %{y:.1f}<extra></extra>' })),
    LY({ title: ttl('Sum of bank net spillovers by region'), shapes: [hline(0, K.navy)], xaxis: AX('', { type: 'date', range: xr }), yaxis: AX('Sum of net spillovers (pp)') }));
  const i0 = argmin(tot), i1 = argmax(tot), us = R.US.slice(0, k + 1);
  out('sp-out', [T.sp1(dt[k], nf(tot[k], 1), nf(tot[i0], 1), x[i0], nf(tot[i1], 1), x[i1], nf(mean(tot), 1)),
    T.sp2(pct(us.filter(v => v > 0).length / us.length, 0), pp(mean(us), 1), pp(mean(R.EU.slice(0, k + 1)), 1), pp(mean(R.RO.slice(0, k + 1)), 1))]);
}

// ================================================================= Financial Risk Meter
function frm() {
  const F = D.frm, n = F.dates.length;
  let a = +$('fr-a').value, b = +$('fr-b').value; if (b < a + 10) { b = Math.min(n - 1, a + 10); $('fr-b').value = b; a = Math.min(a, b - 10); $('fr-a').value = a; }
  $('fr-a-v').textContent = F.dates[a]; $('fr-b-v').textContent = F.dates[b];
  const x = F.dates, sel = a === 0 && b === n - 1 ? [] : [{ type: 'rect', xref: 'x', yref: 'paper', x0: x[a], x1: x[b], y0: 0, y1: 1, fillcolor: K.band, opacity: 0.35, line: { width: 0 }, layer: 'below' }];
  const em = eventMarks(x[0], x[n - 1]);
  plot('fr-frm', [{ x, y: F.frm, mode: 'lines', name: 'FRM: average GACV penalty λ × 10,000 (13 banks)', line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }],
    LY({ title: ttl('Financial Risk Meter, 63-day windows every 10 days'), shapes: [...sel, ...em.shapes], annotations: em.annotations, xaxis: AX('', { type: 'date' }), yaxis: AX('λ × 10,000') }));
  plot('fr-dens', [
    { x, y: F.dens.map(v => 100 * v), mode: 'lines', name: `Share of active predictors at a fixed penalty λ = ${F.lam_fix.toExponential(1)}`, line: { color: K.purple, width: 1.4 }, hovertemplate: '%{x}: %{y:.0f}%<extra></extra>' },
    { x, y: F.vix, mode: 'lines', name: 'VIX (right axis)', yaxis: 'y2', line: { color: K.orange, width: 1.1 }, hovertemplate: 'VIX %{x}: %{y:.1f}<extra></extra>' }
  ], LY({ title: ttl('Active predictors (12 banks + 3 lagged macro variables) and the VIX'), shapes: sel, xaxis: AX('', { type: 'date' }), yaxis: AX('Active predictors (%)'),
    yaxis2: AX('VIX', { overlaying: 'y', side: 'right', showgrid: false }) }));
  const s = (arr) => arr.slice(a, b + 1), dn = s(F.dens), i0 = argmin(dn), i1 = argmax(dn);
  out('fr-out', [T.fr1(F.dates[a], F.dates[b], b - a + 1, nf(pearson(s(F.frm), s(F.vix)), 2), nf(pearson(dn, s(F.vix)), 2)),
    T.fr2(pct(dn[i0], 0), F.dates[a + i0], pct(dn[i1], 0), F.dates[a + i1], pct(mean(dn), 0))]);
}

// ================================================================= historical stress scenarios
function stressWindow(E, L) {      // generate_all_charts.stress_historical with a window of L days
  const cols = E.X.map((c, j) => (c ? j : -1)).filter(j => j >= 0), n = E.dates.length;
  const lp = E.dates.map((_, t) => 100 * Math.log(mean(cols.map(j => Math.exp(E.X[j][t] / 1e5)))));
  let best = Infinity, end = -1;
  for (let t = L - 1; t < n; t++) { let s = 0; for (let u = t - L + 1; u <= t; u++) s += lp[u]; if (s < best) { best = s; end = t; } }
  const cum = E.X.map(c => (c ? 100 * (Math.exp(c.slice(end - L + 1, end + 1).reduce((s, v) => s + v, 0) / 1e5) - 1) : null));
  return { cum, loss: -100 * (Math.exp(best / 100) - 1), start: E.dates[end - L + 1], end: E.dates[end] };
}
function stress() {
  const L = +$('ss-l').value, W = D.stress.map(E => stressWindow(E, L)), lab = B.map(k => NAME[k]);
  $('ss-l-v').textContent = L;
  const z = W.map(w => w.cum);
  plot('ss-chart', [{ z, x: lab, y: D.stress.map(E => E.name), type: 'heatmap', zmin: -60, zmax: 60, colorscale: RDBU, texttemplate: '%{z:.0f}', textfont: { size: 10 },
    colorbar: { orientation: 'h', y: -0.42, yanchor: 'top', thickness: 10, len: 0.8, title: { text: `Return over the worst ${L} days of the equal-weighted bank portfolio (%)`, side: 'top', font: { size: 11 } } },
    hovertemplate: '%{y}, %{x}: %{z:.1f}%<extra></extra>', hoverongaps: false }],
    LY({ title: ttl(`Worst ${L} consecutive trading days of each episode`), margin: { l: 130, r: 10, t: 30, b: 60 }, xaxis: AX('', { tickangle: -40, tickfont: { size: 10 } }), yaxis: AX('', { autorange: 'reversed', tickfont: { size: 10 } }) }));
  let wc = [0, 0, Infinity]; z.forEach((r, i) => r.forEach((v, j) => { if (v !== null && v < wc[2]) wc = [i, j, v]; }));
  out('ss-out', [...W.map((w, i) => T.ss1(T.ep[D.stress[i].name] || D.stress[i].name, pct(w.loss / 100, 1), w.start, w.end)), T.ss2(lab[wc[1]], T.ep[D.stress[wc[0]].name] || D.stress[wc[0]].name, nf(wc[2], 0))]);
}

// ================================================================= quantile connectedness (case study)
const PAIRS = ['0.01', '0.05', '0.1'];
function quantileCase() {
  const A = D.ags, F = A.fig4, lo = $('qc-p').value, hi = { '0.01': '0.99', '0.05': '0.95', '0.1': '0.9' }[lo], [ca, cb, cc] = A.centre;
  const key = t => (+t).toString(), L = Object.keys(F).filter(t => +t < 0.5).sort((x, y) => x - y), Rt = Object.keys(F).filter(t => +t > 0.5).sort((x, y) => x - y);
  plot('qc-chart', [
    { x: L.map(Number), y: L.map(t => F[t]), mode: 'lines+markers', name: 'Left tail: large beneficial shocks (CDS spreads fall)', line: { color: K.green, width: 2 }, marker: { size: 8 }, hovertemplate: 'τ = %{x:.2f}: %{y:.2f}%<extra></extra>' },
    { x: Rt.map(Number), y: Rt.map(t => F[t]), mode: 'lines+markers', name: 'Right tail: large adverse shocks (CDS spreads rise)', line: { color: K.red, width: 2 }, marker: { size: 8 }, hovertemplate: 'τ = %{x:.2f}: %{y:.2f}%<extra></extra>' },
    { x: [ca, cb], y: [cc, cc], mode: 'lines', name: `Centre, quantiles ${ca.toFixed(2)} to ${cb.toFixed(2)}: about ${cc.toFixed(0)}%`, line: { color: K.amber, width: 6 }, hoverinfo: 'skip' },
    { x: [0, 1], y: [A.mean, A.mean], mode: 'lines', name: `Conditional mean (VAR): ${A.mean.toFixed(2)}%`, line: { color: K.blue, width: 2, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [+lo, +hi], y: [F[key(lo)], F[key(hi)]], mode: 'markers', name: `Pair compared: τ = ${(+lo).toFixed(2)} and ${(+hi).toFixed(2)}`, marker: { size: 16, color: 'rgba(0,0,0,0)', line: { color: K.navy, width: 2 } }, hoverinfo: 'skip' }
  ], LY({ title: ttl('17 sovereigns and 17 financial sectors, daily CDS changes, 2006-2017'),
    annotations: Object.keys(F).map(t => ({ x: +t, y: F[t], text: `τ = ${(+t).toFixed(2)}: ${F[t].toFixed(2)}%`, showarrow: false, xanchor: +t < 0.5 ? 'left' : 'right', xshift: +t < 0.5 ? 10 : -10, font: { size: 10, color: K.navy } })),
    xaxis: AX('Quantile τ of the QFVAR', { range: [0, 1], tickvals: [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1] }), yaxis: AX('Spillover index S<sub>τ</sub><sup>(5)</sup> (%)', { range: [30, 100] }) }));
  const vl = F[key(lo)], vh = F[key(hi)];
  out('qc-out', [T.qc(nf(+lo, 2), nf(vl, 2), nf(+hi, 2), nf(vh, 2), nf(vh - vl, 2), nf(vl - A.mean, 2), nf(vh - A.mean, 2))]);
}

// ================================================================= bank rate risk (second case study, case_rate_risk.py)
const rrCache = {};
function olsNW(rows, y, lags) {     // OLS with Newey-West (Bartlett) standard errors, as case_rate_risk.ols_nw
  const n = y.length, k = rows[0].length, XtX = Array.from({ length: k }, () => new Array(k).fill(0)), Xty = new Array(k).fill(0);
  for (let t = 0; t < n; t++) for (let a = 0; a < k; a++) { Xty[a] += rows[t][a] * y[t]; for (let c = 0; c < k; c++) XtX[a][c] += rows[t][a] * rows[t][c]; }
  const inv = XtX.map((_, j) => solve(XtX, XtX.map((__, i) => (i === j ? 1 : 0))));   // columns of the inverse (symmetric)
  const b = inv.map(r => r.reduce((s, v, i) => s + v * Xty[i], 0));
  const g = rows.map((r, t) => { const u = y[t] - r.reduce((s, v, i) => s + v * b[i], 0); return r.map(v => v * u); });
  const S = Array.from({ length: k }, () => new Array(k).fill(0));
  for (let L = 0; L <= lags; L++) {
    const w = L === 0 ? 1 : 1 - L / (lags + 1);
    for (let t = L; t < n; t++) for (let a = 0; a < k; a++) for (let c = 0; c < k; c++) {
      const v = g[t][a] * g[t - L][c]; S[a][c] += w * v; if (L > 0) S[c][a] += w * v;
    }
  }
  const j = k - 1; let V = 0;
  for (let a = 0; a < k; a++) for (let c = 0; c < k; c++) V += inv[j][a] * S[a][c] * inv[c][j];
  return [100 * b[j], 100 * Math.sqrt(V)];
}
function rateRolling(w) {
  if (rrCache[w]) return rrCache[w];
  const R = D.rate, n = R.dates.length, f = a => a.map(v => v / 1e4);
  const bank = f(R.bank), spx = f(R.spx), ief = f(R.ief), d10 = f(R.d10);
  const o = { dates: [], b: [], se: [], bi: [] };
  for (let t = w; t <= n; t++) {
    const rowsB = [], rowsI = [], yb = [], yi = [];
    for (let u = t - w; u < t; u++) { rowsB.push([1, spx[u], d10[u]]); rowsI.push([1, d10[u]]); yb.push(bank[u]); yi.push(ief[u]); }
    const [b, se] = olsNW(rowsB, yb, R.lags), [bi] = olsNW(rowsI, yi, R.lags);
    o.dates.push(R.dates[t - 1]); o.b.push(b); o.se.push(se); o.bi.push(bi);
  }
  return (rrCache[w] = o);
}
const lastUpTo = (o, d) => { let i = -1; o.dates.forEach((x, j) => { if (x <= d) i = j; }); return i; };
function rateRisk() {
  const R = D.rate, w = +$('rr-w').value, o = rateRolling(w);
  $('rr-w-v').textContent = w;
  // left: value of 100 on the base date, to the end of 2023
  const i0 = R.dates.indexOf(R.base), i1 = lastUpTo({ dates: R.dates }, '2023-12-31'), x = R.dates.slice(i0, i1 + 1);
  const cum = a => { let v = 100; return x.map((_, j) => (j === 0 ? 100 : (v *= 1 + a[i0 + j] / 1e6))); };
  const svbLine = { type: 'line', xref: 'x', yref: 'paper', x0: R.svb, x1: R.svb, y0: 0, y1: 1, line: { color: K.navy, width: 1, dash: 'dot' } };
  const svbLab = { x: R.svb, xref: 'x', yref: 'paper', y: 1, text: 'SVB', textangle: -90, showarrow: false, xanchor: 'right', yanchor: 'top', font: { size: 10, color: K.navy } };
  plot('rr-mtm', [
    { x: [R.base, R.mtm_end, R.mtm_end, R.base], y: [55, 55, 115, 115], fill: 'toself', mode: 'none', fillcolor: 'rgba(197,210,232,0.45)', name: 'Q1 2022 to Q1 2023', hoverinfo: 'skip' },
    ...[['ief', K.amber, 'IEF: Treasuries 7-10y, total return'], ['tlt', K.purple, 'TLT: Treasuries 20y+, total return'], ['bank', K.blue, 'Six US banks, total return'], ['spx', K.green, 'S&P 500 price index']].map(([k, c, nm]) =>
      ({ x, y: cum(R[k]), mode: 'lines', name: nm, line: { color: c, width: 1.4 }, hovertemplate: nm + ' %{x}: %{y:.1f}<extra></extra>' }))
  ], LY({ title: ttl('Treasury ETFs and bank equity'), shapes: [hline(100, K.navy), svbLine], annotations: [svbLab],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Value of 100 on 31 Dec 2021', { range: [55, 115] }) }));
  // right: rolling rate beta
  const lo = o.b.map((v, i) => v - 1.96 * o.se[i]), hi = o.b.map((v, i) => v + 1.96 * o.se[i]);
  plot('rr-beta', [
    { x: o.dates, y: hi, mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: o.dates, y: lo, mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: K.band, name: 'Bank beta: 95% Newey-West interval', hoverinfo: 'skip' },
    { x: o.dates, y: o.b, mode: 'lines', name: 'Bank beta, given the S&P 500', line: { color: K.blue, width: 1.4 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: o.dates, y: o.bi, mode: 'lines', name: 'IEF beta', line: { color: K.amber, width: 1.2 }, hovertemplate: 'IEF %{x}: %{y:.2f}%<extra></extra>' },
    { x: ['2022-03-16', '2022-03-16'], y: [Math.min(...lo, ...o.bi), Math.max(...hi)], mode: 'lines', name: 'First Fed hike', line: { color: K.red, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' }
  ], LY({ title: ttl(`Rolling ${w}-day rate beta, per +100 bp in the US 10Y yield`), shapes: [hline(0, K.navy), svbLine], annotations: [svbLab],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Return (%)') }));
  const e = lastUpTo(o, '2021-12-31'), s = lastUpTo(o, R.svb), M = R.mtm, P = R.periods;
  out('rr-out', [T.rr1(w, e >= 0 ? pp(o.b[e], 1) : '–', pp(o.b[s], 2), nf(lo[s], 2), nf(hi[s], 2)),
    T.rr2(nf(-M.ief, 1), nf(-M.tlt, 1), nf(-M.bank, 1), nf(-M.spx, 1)),
    T.rr3(pp(P['2012-2019'].b, 1), nf(P['2012-2019'].t, 1), pp(P.Tightening.b, 1), nf(P.Tightening.t, 1), nf(P.Tightening.b_ief, 1))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['bi-s'], bankIndices); bankIndices(); P('bi-play', 'bi-s', range(0, +$('bi-s').max, 3), 160);
  on(['me-a'], mesBars); P('me-play', 'me-a', range(1, 20, 1), 450);
  on(['sr-k', 'sr-l'], srisk); P('sr-play', 'sr-k', range(3, 12, 0.5), 300);
  $('qr-t').max = D.qr.x.length; $('qr-t').value = D.qr.x.length; on(['qr-a', 'qr-t'], covarQR); P('qr-play', 'qr-t', range(250, D.qr.x.length, 60).concat([D.qr.x.length]), 60);
  on(['dc-a'], dcovar); P('dc-play', 'dc-a', range(1, 10, 1), 600);
  on(['vd-a'], varDcovar); P('vd-play', 'vd-a', range(1, 10, 1), 600);
  on(['ex-a'], exposure); P('ex-play', 'ex-a', range(1, 10, 1), 600);
  on(['st-h'], spillTable); P('st-play', 'st-h', range(1, 30, 1), 300);
  on(['sn-q', 'sn-h'], spillNetwork); P('sn-play', 'sn-q', range(0.5, 0.95, 0.05), 600);
  $('sp-t').max = 9999; $('sp-t').value = 9999; on(['sp-w', 'sp-h', 'sp-t'], spillRolling); P('sp-play', 'sp-t', range(0, D.roll.dates_250.length - 1, 6), 60);
  $('fr-a').max = D.frm.dates.length - 1; $('fr-b').max = D.frm.dates.length - 1; $('fr-a').value = 0; $('fr-b').value = D.frm.dates.length - 1;
  on(['fr-a', 'fr-b'], frm); P('fr-play', 'fr-b', range(10, D.frm.dates.length - 1, 4), 80);
  on(['ss-l'], stress); P('ss-play', 'ss-l', range(3, 18, 1), 450);   // the shortest episode (Brexit vote) has 18 days
  on(['qc-p'], quantileCase); P('qc-play', 'qc-p', PAIRS.map(Number), 1100);
  on(['rr-w'], rateRisk); P('rr-play', 'rr-w', range(63, 504, 21), 700);
  const PFX = { 'bank-indices': 'bi', 'mes': 'me', 'srisk': 'sr', 'covar-qr': 'qr', 'dcovar': 'dc', 'var-dcovar': 'vd', 'exposure': 'ex',
    'spill-table': 'st', 'spill-network': 'sn', 'spill-rolling': 'sp', 'frm': 'fr', 'stress': 'ss', 'quantile': 'qc', 'rate-risk': 'rr' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  mesBars(); srisk(); covarQR(); dcovar(); varDcovar(); exposure(); spillTable(); spillNetwork(); spillRolling(); frm(); stress(); quantileCase(); rateRisk();
}
window.CH18 = { rateRolling, olsNW, spillStats, block, quantile, stressWindow, spearman, pearson, sriskRatio, breakEven, CV };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

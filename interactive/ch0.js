// Chapter 0 interactive page: one block per chart slide, computed in the browser from ch0_data.js.
(function () {
'use strict';
const D = window.CH0_DATA;
const { sdev, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH0_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD',
  crimson: '#DC3545', navy: '#1F2A44', band: '#C5D2E8', teal: '#17A2B8' };
const RED_FILL = 'rgba(205,0,0,0.35)';

// ---------------------------------------------------------------- dates: day numbers since 1970-01-01
const DAY = 864e5;
const MEN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const iso = d => new Date(d * DAY).toISOString().slice(0, 10);
const dayOf = s => Math.round(Date.parse(s + 'T00:00:00Z') / DAY);
const fd = d => T.date(new Date(d * DAY));                                  // readouts (page language)
const fdEN = d => { const x = new Date(d * DAY); return `${x.getUTCDate()} ${MEN[x.getUTCMonth()]} ${x.getUTCFullYear()}`; };
const monEN = d => { const x = new Date(d * DAY); return `${MEN[x.getUTCMonth()]} ${x.getUTCFullYear()}`; };
const cum = a => { const r = new Array(a.length); let s = 0; for (let i = 0; i < a.length; i++) { s += a[i]; r[i] = s; } return r; };
function decode(o) {                // delta-encoded day numbers -> o._t (days) and o._x (ISO dates for Plotly)
  if (!o._t) { o._t = cum(o.t); o._x = o._t.map(iso); }
  return o;
}
function firstAt(t, d) {            // first index with t[i] >= d
  let lo = 0, hi = t.length;
  while (lo < hi) { const m = (lo + hi) >> 1; if (t[m] < d) lo = m + 1; else hi = m; }
  return lo;
}
const yearsBetween = (a, b) => (b - a) / 365.25;
const sgn = (x, d) => (x > 0 ? '+' : '') + nf(x, d);

// ================================================================= history of exchanges and crashes
const HI_LV = [-30, 30, -62, 62];   // label offsets in pixels for the four levels of the slide
function history() {
  const y = +$('hi-y').value, L = D.history.lanes, tr = [], ann = [], cnt = [];
  $('hi-y-v').textContent = y;
  L.forEach((ln, r) => {
    const ev = ln.events.filter(e => e.a <= y);
    cnt.push(ev.length);
    tr.push({ x: [1250, 2035], y: [-r, -r], mode: 'lines', line: { color: ln.color, width: 1 }, opacity: 0.5, hoverinfo: 'skip', showlegend: false });
    ev.filter(e => e.b > e.a).forEach(e => tr.push({ x: [e.a, Math.min(e.b, y)], y: [-r, -r], mode: 'lines', line: { color: ln.color, width: 9 }, showlegend: false,
      hovertemplate: e.text.replace(/\n/g, ' ') + '<extra></extra>' }));
    const pts = ev.filter(e => e.b === e.a);
    tr.push({ x: pts.map(e => e.a), y: pts.map(() => -r), mode: 'markers', name: ln.label, legendgroup: 'l' + r, marker: { color: ln.color, size: 10 },
      text: pts.map(e => e.text.replace(/\n/g, ' ')), hovertemplate: '%{text}<extra></extra>' });
    ev.forEach(e => {
      const xm = (e.a + Math.min(e.b, y)) / 2;
      ann.push({ x: xm, y: -r, ax: xm + e.dx, ay: HI_LV[e.lv], axref: 'x', text: e.text.replace(/\n/g, '<br>'), showarrow: true, arrowhead: 0, arrowwidth: 0.8,
        arrowcolor: ln.color, font: { size: 10, color: K.navy }, bgcolor: 'rgba(255,255,255,0.85)', borderpad: 1 });
    });
  });
  plot('hi-chart', tr, layout({ annotations: ann, margin: { l: 20, r: 20, t: 20, b: 40 },
    xaxis: AX('', { range: [1250, 2035], dtick: 100, zeroline: false }), yaxis: AX('', { range: [-1.75, 0.95], showticklabels: false, showgrid: false, zeroline: false }),
    legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: -0.12, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } } }));
  out('hi-out', [T.hi(y, cnt[0], cnt[1])]);
}

// ================================================================= risk and return
const RR_POS = { 'Gold': 'bottom left', 'S&P 500 TR (SPY)': 'top center', 'Nikkei 225 (USD)': 'top right', 'Euro Stoxx 50 (USD)': 'bottom right',
  'US Treasuries 20y+ (TLT)': 'bottom left', 'EUR/USD': 'top center', 'EUR/RON': 'top right', 'Bitcoin': 'top left', 'Ethereum': 'top left' };
function annStats(o, d0) {          // ann_stats(p, 'obs') of generate_all_charts.py on the dates >= d0
  decode(o);
  const t = o._t, v = o.v, n = t.length - 1, i0 = firstAt(t, d0);
  if (n - i0 < 30) return null;
  const yrs = yearsBetween(t[i0], t[n]), r = [];
  for (let i = i0 + 1; i <= n; i++) r.push(Math.log(v[i] / v[i - 1]));
  return { cagr: Math.pow(v[n] / v[i0], 1 / yrs) - 1, vol: sdev(r) * Math.sqrt(r.length / yrs), yrs, from: t[i0], to: t[n] };
}
function riskReturn() {
  const R = D.risk_return, y = +$('rr-y').value, sel = $('rr-a').value, d0 = dayOf(`${y}-01-02`);
  $('rr-y-v').textContent = y;
  const st = R.names.map(n => annStats(R.series[n], d0));
  const tr = R.names.map((n, k) => {
    const s = st[k], late = s.from > d0 + 30, lab = late ? `${n} (from ${monEN(s.from)})` : n;
    return { x: [s.vol], y: [s.cagr], mode: 'markers+text', text: [lab], textposition: RR_POS[n] || 'top right', textfont: { size: 10, color: K.navy }, showlegend: false,
      marker: { color: R.colors[k], size: n === sel ? 17 : 12, line: { color: n === sel ? K.navy : '#fff', width: n === sel ? 2.5 : 1 } },
      hovertemplate: `${n}<br>CAGR %{y:.1%}<br>volatility %{x:.1%}<extra></extra>` };
  });
  const ys = st.map(s => s.cagr);
  plot('rr-chart', tr, layout({ title: ttl(`Risk and return, ${y}-2026`), shapes: [hline(0, K.navy)],
    xaxis: AX('Annualised volatility (log scale)', { type: 'log', tickvals: [0.02, 0.05, 0.1, 0.2, 0.4, 0.8], tickformat: '.0%', range: [Math.log10(0.014), Math.log10(1.6)] }),
    yaxis: AX('Annualised return (CAGR)', { tickformat: '.0%', range: [Math.min(-0.17, Math.min(...ys) - 0.05), Math.max(...ys) + 0.1], zeroline: false }) }));
  const s = st[R.names.indexOf(sel)];
  out('rr-out', [T.rr(fd(s.from), fd(s.to), nf(s.yrs, 1)), T.rr2(sel, pct(s.cagr, 1), pct(s.vol, 1), nf(100 * s.vol / Math.sqrt(s.yrs), 1))]);
}

// ================================================================= S&P 500 drawdowns
let DD = null;
function ddPrep() {
  const o = decode(D.drawdowns.sp), v = o.v, n = v.length, peak = new Array(n), dd = new Array(n);
  let m = -Infinity;
  for (let i = 0; i < n; i++) { m = Math.max(m, v[i]); peak[i] = m; dd[i] = v[i] / m - 1; }
  const pk = firstAt(o._t, dayOf('2007-10-09')), i9 = firstAt(o._t, dayOf('2009-03-10'));
  let rc = i9; while (rc < n && v[rc] < v[pk]) rc++;
  DD = { o, v, dd, pk, rc, minAll: Math.min(...dd) };
}
function drawdowns() {
  if (!DD) ddPrep();
  const { o, v, dd, pk, rc } = DD, k = +$('dd-t').value, x = o._x.slice(0, k + 1);
  $('dd-t-v').textContent = fd(o._t[k]);
  let mi = 0; for (let i = 1; i <= k; i++) if (dd[i] < dd[mi]) mi = i;
  const shapes = [], ann = [];
  if (k > pk) shapes.push({ type: 'line', xref: 'x', yref: 'y', x0: o._x[pk], x1: o._x[Math.min(k, rc)], y0: v[pk], y1: v[pk], line: { color: K.amber, width: 4 } });
  if (k >= rc) ann.push({ x: o._x[rc], y: Math.log10(v[pk]), xref: 'x', yref: 'y', text: `${yearsBetween(o._t[pk], o._t[rc]).toFixed(1)} years to regain<br>the Oct 2007 peak`,
    showarrow: false, xanchor: 'left', yanchor: 'top', font: { size: 10, color: K.navy } });
  for (const [name, a, b] of D.drawdowns.episodes) {
    const i0 = firstAt(o._t, dayOf(a)), i1 = Math.min(firstAt(o._t, dayOf(b) + 1) - 1, k);
    if (i1 < i0) continue;
    let j = i0; for (let i = i0; i <= i1; i++) if (dd[i] < dd[j]) j = i;
    ann.push({ x: o._x[j], y: dd[j], xref: 'x', yref: 'y2', text: `${name}<br>${(100 * dd[j]).toFixed(0)}%`, showarrow: false, yanchor: 'top', yshift: -8,
      xanchor: name === 'COVID-19' ? 'right' : name.startsWith('2022') ? 'left' : 'center', font: { size: 10, color: K.navy } });
  }
  plot('dd-chart', [
    { x, y: v.slice(0, k + 1), mode: 'lines', name: 'S&P 500 (price index, log scale)', line: { color: K.blue, width: 1.1 }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' },
    { x, y: dd.slice(0, k + 1), mode: 'lines', name: 'Drawdown', yaxis: 'y2', fill: 'tozeroy', fillcolor: RED_FILL, line: { color: K.red, width: 0.7 }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' },
    { x: [o._x[mi]], y: [dd[mi]], yaxis: 'y2', mode: 'markers', name: 'Maximum drawdown so far', marker: { color: K.navy, size: 9, symbol: 'diamond' }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }
  ], layout({ title: ttl('S&P 500, 2000-2026: level (log) and drawdown'), shapes, annotations: ann, margin: { l: 60, r: 12, t: 30, b: 40 },
    xaxis: AX('', { type: 'date', range: [o._x[0], o._x[o._x.length - 1]], anchor: 'y2' }),
    yaxis: AX('S&P 500 (log)', { type: 'log', domain: [0.56, 1], tickvals: [1000, 2000, 4000, 8000], range: [Math.log10(600), Math.log10(8000)] }),
    yaxis2: AX('Drawdown', { domain: [0, 0.48], tickformat: '.0%', range: [DD.minAll * 1.45, 0.02], anchor: 'x' }),
    legend: { orientation: 'h', x: 0, xanchor: 'left', y: -0.12, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } } }));
  const res = [T.dd(fd(o._t[k]), pct(dd[k], 1), pct(dd[mi], 1), fd(o._t[mi]))];
  if (k >= rc) res.push(T.ddr(fd(o._t[pk]), fd(o._t[rc]), nf(yearsBetween(o._t[pk], o._t[rc]), 1)));
  else if (k > pk) res.push(T.ddn(fd(o._t[pk]), pct(v[k] / v[pk] - 1, 1)));
  out('dd-out', res);
}

// ================================================================= VIX regimes
function vixPeaks(o) {
  const idx = o.v.map((_, i) => i).sort((a, b) => o.v[b] - o.v[a]), pk = [];
  for (const i of idx) { if (pk.every(p => Math.abs(o._t[i] - o._t[p]) > 730)) pk.push(i); if (pk.length === 5) break; }
  return pk;
}
let VXP = null;
function vix() {
  const o = decode(D.vix.vix), v = o.v;
  let lo = +$('vx-lo').value, hi = +$('vx-hi').value;
  if (hi < lo) { hi = lo; $('vx-hi').value = hi; }
  $('vx-lo-v').textContent = lo; $('vx-hi-v').textContent = hi;
  if (!VXP) VXP = vixPeaks(o);
  let a = 0, c = 0; for (const x of v) { if (x < lo) a++; else if (x >= hi) c++; }
  const n = v.length, vmax = Math.max(...v);
  plot('vx-chart', [
    { x: o._x, y: v, mode: 'lines', name: 'VIX', line: { color: K.blue, width: 0.8 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' },
    { x: [o._x[0], o._x[n - 1]], y: [lo, lo], mode: 'lines', name: 'VIX = ' + lo, line: { color: K.amber, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [o._x[0], o._x[n - 1]], y: [hi, hi], mode: 'lines', name: 'VIX = ' + hi, line: { color: K.red, width: 1.5, dash: 'dash' }, hoverinfo: 'skip' }
  ], layout({ title: ttl(`VIX 2000-2026: below ${lo} on ${Math.round(100 * a / n)}% of days, at least ${hi} on ${Math.round(100 * c / n)}%`),
    annotations: VXP.map(i => ({ x: o._x[i], y: v[i], text: `${monEN(o._t[i])}<br>${v[i].toFixed(0)}`, showarrow: false, yanchor: 'bottom', font: { size: 10, color: K.navy } })),
    xaxis: AX('', { type: 'date' }), yaxis: AX('VIX (implied volatility, %)', { range: [0, vmax * 1.2] }) }));
  out('vx-out', [T.vx(lo, hi, pct(a / n, 0), pct((n - a - c) / n, 0), pct(c / n, 0), n)]);
}

// ================================================================= rolling correlations
function rollCorr(x, y, w) {        // pandas rolling(w).corr on complete windows
  const n = x.length, r = new Array(n).fill(null);
  let sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0;
  for (let i = 0; i < n; i++) {
    sx += x[i]; sy += y[i]; sxx += x[i] * x[i]; syy += y[i] * y[i]; sxy += x[i] * y[i];
    if (i >= w) { const a = x[i - w], b = y[i - w]; sx -= a; sy -= b; sxx -= a * a; syy -= b * b; sxy -= a * b; }
    if (i >= w - 1) { const c = sxy - sx * sy / w, vx = sxx - sx * sx / w, vy = syy - sy * sy / w; r[i] = c / Math.sqrt(vx * vy); }
  }
  return r;
}
function meanOn(t, c, a, b) {       // mean of the non-missing values with a <= date <= b
  let s = 0, k = 0; for (let i = 0; i < t.length; i++) if (t[i] >= a && t[i] <= b && c[i] !== null) { s += c[i]; k++; }
  return s / k;
}
function correlations() {
  const w = +$('co-w').value, A = decode(D.corr.sb), B = decode(D.corr.be);
  $('co-w-v').textContent = w;
  const ca = rollCorr(A.x, A.y, w), cb = rollCorr(B.x, B.y, w), END = dayOf('2100-01-01');
  plot('co-chart', [
    { x: A._x, y: ca, mode: 'lines', name: 'S&P 500 vs long Treasuries (TLT)', line: { color: K.blue, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: B._x, y: cb, mode: 'lines', name: 'S&P 500 vs Bitcoin', line: { color: K.orange, width: 1.2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl(`Rolling correlations of daily log returns, window of ${w} trading days`), shapes: [hline(0, K.navy)],
    xaxis: AX('', { type: 'date', range: [A._x[0], A._x[A._x.length - 1]] }), yaxis: AX(`Rolling correlation (${w} days)`, { range: [-0.85, 0.85], zeroline: false }) }));
  out('co-out', [T.co(w, nf(meanOn(A._t, ca, dayOf('2010-01-01'), dayOf('2020-12-31')), 2), nf(meanOn(A._t, ca, dayOf('2022-01-01'), END), 2),
    nf(meanOn(B._t, cb, dayOf('2016-01-01'), dayOf('2019-12-31')), 2), nf(meanOn(B._t, cb, dayOf('2022-01-01'), END), 2))]);
}

// ================================================================= BET 1997-2026
const BT_OFF = [[0, -45], [0, -35], [0, 50], [-55, 45], [15, 55], [-10, -45]];
function bet() {
  const o = decode(D.bet.bet), v = o.v, n = v.length - 1, y = +$('bt-y').value;
  $('bt-y-v').textContent = y;
  const i0 = y === 1997 ? 0 : firstAt(o._t, dayOf(`${y}-01-01`)), yrs = yearsBetween(o._t[i0], o._t[n]);
  let m = i0, pk = i0, tr = i0, mdd = 0;
  for (let i = i0; i <= n; i++) { if (v[i] > v[m]) m = i; const d = v[i] / v[m] - 1; if (d < mdd) { mdd = d; pk = m; tr = i; } }
  let rc = tr; while (rc <= n && v[rc] < v[pk]) rc++;
  const shapes = mdd < 0 ? [{ type: 'line', xref: 'x', yref: 'y', x0: o._x[pk], x1: o._x[Math.min(rc, n)], y0: v[pk], y1: v[pk], line: { color: K.amber, width: 4 } }] : [];
  const ev = D.bet.events;
  plot('bt-chart', [
    ...(i0 > 0 ? [{ x: o._x.slice(0, i0 + 1), y: v.slice(0, i0 + 1), mode: 'lines', name: 'Before the start date', line: { color: K.band, width: 1.2 }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' }] : []),
    { x: o._x.slice(i0), y: v.slice(i0), mode: 'lines', name: 'BET, official closing values (base 1,000 on 19 Sep 1997)', line: { color: K.blue, width: 1.2 }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' },
    { x: [o._x[pk], o._x[tr]], y: [v[pk], v[tr]], mode: 'markers', name: 'Largest drawdown from the start date: peak and trough', marker: { color: K.amber, size: 10, symbol: 'diamond', line: { color: '#fff', width: 1 } }, hovertemplate: '%{x}: %{y:,.0f}<extra></extra>' },
    { x: ev.map(e => iso(e.t)), y: ev.map(e => v[firstAt(o._t, e.t)]), text: ev.map(e => e.text), mode: 'markers', name: 'Events', marker: { color: K.red, size: 8 }, hovertemplate: '%{text}<br>%{x}: %{y:,.0f}<extra></extra>' }
  ], layout({ title: ttl(`The BET index, 1997-2026; start date ${fdEN(o._t[i0])}`), shapes,
    annotations: ev.map((e, j) => ({ x: iso(e.t), y: Math.log10(v[firstAt(o._t, e.t)]), text: e.text.replace(/ (low|peak|trough|announcement|COVID-19|IPO)/, '<br>$1').replace('Hidroelectrica', '<br>Hidroelectrica'),
      ax: BT_OFF[j][0], ay: BT_OFF[j][1], arrowhead: 0, arrowwidth: 0.6, arrowcolor: K.band, font: { size: 10, color: K.navy } })),
    xaxis: AX('', { type: 'date' }), yaxis: AX('Index level (log scale)', { type: 'log', range: [Math.log10(150), Math.log10(5e4)], tickvals: [200, 500, 1000, 2000, 5000, 10000, 20000, 50000], tickformat: ',d' }) }));
  const rec = rc <= n ? T.btr(fd(o._t[rc]), nf(yearsBetween(o._t[pk], o._t[rc]), 1)) : T.btn;
  out('bt-out', [T.bt(fd(o._t[i0]), fd(o._t[n]), nf(v[n] / v[i0], 1), pct(Math.pow(v[n] / v[i0], 1 / yrs) - 1, 1), nf(yrs, 1)),
    mdd < 0 ? T.bt2(pct(mdd, 1), fd(o._t[pk]), fd(o._t[tr]), rec) : T.bt0]);
}

// ================================================================= Tether (USDT)
function usdt() {
  const o = decode(D.usdt.u), b = +$('us-b').value, p = $('us-p').value;
  $('us-b-v').textContent = nf(b, 1) + '%';
  let a = 0, z = o._t.length - 1;
  if (p === 'm20') { a = firstAt(o._t, dayOf('2020-02-24')); z = firstAt(o._t, dayOf('2020-04-11')) - 1; }
  else if (p !== 'all') { a = firstAt(o._t, dayOf(p + '-01-01')); z = firstAt(o._t, dayOf((+p + 1) + '-01-01')) - 1; }
  const x = o._x.slice(a, z + 1), dev = o.v.slice(a, z + 1).map(u => 100 * (u - 1)), n = dev.length;
  const inB = dev.filter(d => Math.abs(d) <= b + 1e-12).length, in1 = dev.filter(d => Math.abs(d) <= 1 + 1e-12).length;
  let lo = 0, hi = 0; dev.forEach((d, i) => { if (d < dev[lo]) lo = i; if (d > dev[hi]) hi = i; });
  const band = (y, c, name, show) => ({ x: [x[0], x[n - 1]], y: [y, y], mode: 'lines', name, legendgroup: name, showlegend: show, line: { color: c, width: 1.3, dash: 'dash' }, hoverinfo: 'skip' });
  const lbl = b.toFixed(1), pEN = p === 'all' ? '2019-2026' : p === 'm20' ? 'March 2020' : p;
  plot('us-chart', [
    { x, y: dev, mode: 'lines', name: 'USDT price minus 1 USD (%)', line: { color: K.green, width: p === 'all' ? 0.8 : 1.5 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    band(b, K.amber, `Band of ${lbl}%`, true), band(-b, K.amber, `Band of ${lbl}%`, false), band(1, K.red, 'Band of 1%', true), band(-1, K.red, 'Band of 1%', false)
  ], layout({ title: ttl(`Tether (USDT), ${pEN}: distance from the 1 USD peg`),
    annotations: [lo, hi].map(i => ({ x: x[i], y: dev[i], text: `${(1 + dev[i] / 100).toFixed(3)} USD<br>${fdEN(o._t[a + i])}`, showarrow: false, xanchor: 'left', xshift: 8, font: { size: 10, color: K.navy } })),
    xaxis: AX('', { type: 'date' }), yaxis: AX('Deviation (%)', p === 'all' ? { range: [-3.2, 6] } : {}) }));
  out('us-out', [T.us($('us-p').selectedOptions[0].textContent, nf(b, 1) + '%', pct(inB / n, 0), pct(in1 / n, 0), n)]);
}

// ================================================================= SPY and RSP
function concentration() {
  const C0 = decode(D.conc), t = C0._t, y = +$('cc-y').value, n = t.length - 1;
  $('cc-y-v').textContent = y;
  const i0 = y === 2003 ? 0 : firstAt(t, dayOf(`${y}-01-01`)), x = C0._x.slice(i0);
  const gs = C0.spy.slice(i0).map(v => v / C0.spy[i0]), gr = C0.rsp.slice(i0).map(v => v / C0.rsp[i0]), q = gs.map((v, i) => v / gr[i]);
  const j23 = firstAt(t, dayOf('2023-01-03')), ch23 = (C0.spy[n] / C0.rsp[n]) / (C0.spy[j23] / C0.rsp[j23]) - 1;
  const from = monEN(t[i0]);
  plot('cc-g', [
    { x, y: gs, mode: 'lines', name: `SPY (cap-weighted): x${gs[gs.length - 1].toFixed(1)}`, line: { color: K.blue, width: 1.1 }, hovertemplate: 'SPY %{x}: %{y:.2f}<extra></extra>' },
    { x, y: gr, mode: 'lines', name: `RSP (equal-weighted): x${gr[gr.length - 1].toFixed(1)}`, line: { color: K.amber, width: 1.1 }, hovertemplate: 'RSP %{x}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl(`S&P 500 ETFs, ${from}-2026 (total return)`), xaxis: AX('', { type: 'date' }),
    yaxis: AX('Growth of 1 USD (log)', { type: 'log', tickvals: [0.5, 1, 2, 4, 8, 16] }) }));
  plot('cc-r', [
    { x, y: q, mode: 'lines', name: `SPY / RSP (both rebased to 1 in ${from})`, line: { color: K.red, width: 1.1 }, hovertemplate: '%{x}: %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl('SPY / RSP relative performance'), shapes: [hline(1, K.navy, 'dot')], xaxis: AX('', { type: 'date' }), yaxis: AX('SPY / RSP') }));
  out('cc-out', [T.cc(fd(t[i0]), nf(gs[gs.length - 1], 1), nf(gr[gr.length - 1], 1), nf(q[q.length - 1], 2)), T.cc2(pct(ch23, 0))]);
}

// ================================================================= passive investing: eq. (5)
const relE = (chi, al) => al * (1 + chi) / (1 + chi * al);
function elasticity() {
  const chi = +$('hh-chi').value, p = +$('hh-p').value, al = 1 - p / 100, xs = range(0, 100, 0.5);
  $('hh-chi-v').textContent = nf(chi, 2); $('hh-p-v').textContent = p + '%';
  const curves = [[0, K.red, 'χ = 0: no strategic response (Koijen and Yogo)'], [chi, K.blue, `χ = ${chi.toFixed(2)}: chosen value (estimate 2.97, Table 2, row 1)`], [10, K.green, 'χ = 10: strong response']];
  plot('hh-chart', [
    ...curves.map(([c, col, name]) => ({ x: xs, y: xs.map(s => relE(c, 1 - s / 100)), mode: 'lines', name, line: { color: col, width: 2 }, hovertemplate: `χ = ${c.toFixed(2)}<br>passive %{x:.0f}%<br>relative E<sub>agg</sub> %{y:.3f}<extra></extra>` })),
    { x: curves.map(() => p), y: curves.map(([c]) => relE(c, al)), mode: 'markers+text', text: curves.map(([c]) => relE(c, al).toFixed(2)), textposition: ['bottom left', 'bottom right', 'top left'],
      textfont: { size: 11, color: K.navy }, marker: { color: curves.map(c => c[1]), size: 9 }, showlegend: false, hoverinfo: 'skip' }
  ], layout({ title: ttl('Aggregate elasticity when investors turn passive, eq. (5)'), shapes: [vline(p, K.navy, 'dot')],
    xaxis: AX('Share of investors turned passive, 1 − α (%)', { range: [0, 100] }), yaxis: AX('E<sub>agg</sub> relative to all active', { range: [0, 1.1] }),
    legend: { orientation: 'h', x: 0, xanchor: 'left', y: -0.2, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 }, traceorder: 'normal' } }));
  out('hh-out', [T.hh(p + '%', nf(relE(0, al), 2), nf(relE(chi, al), 2), nf(chi, 2), nf(relE(10, al), 2)), T.hh2(nf(chi, 2), nf(al, 2), nf(1 / (1 + chi * al), 2))]);
}

// ================================================================= Pflueger (2025): Treasury bond-stock betas
function rollBeta(y, x, w) {        // pandas y.rolling(w).cov(x) / x.rolling(w).var() on complete windows
  const n = x.length, b = new Array(n).fill(null);
  let sx = 0, sy = 0, sxx = 0, sxy = 0;
  for (let i = 0; i < n; i++) {
    sx += x[i]; sy += y[i]; sxx += x[i] * x[i]; sxy += x[i] * y[i];
    if (i >= w) { const a = x[i - w], c = y[i - w]; sx -= a; sy -= c; sxx -= a * a; sxy -= a * c; }
    if (i >= w - 1) b[i] = (sxy - sx * sy / w) / (sxx - sx * sx / w);
  }
  return b;
}
function bondBeta() {
  const qw = +$('bb-q').value, dw = +$('bb-d').value, Q = decode(D.pflueger.q), Dd = decode(D.pflueger.d), R = D.pflueger.ref;
  $('bb-q-v').textContent = qw; $('bb-d-v').textContent = dw;
  const bq = rollBeta(Q.bond, Q.eq, qw), bn = rollBeta(Dd.nom, Dd.eq, dw), bt = rollBeta(Dd.tips, Dd.eq, dw);
  const iq = bq.findIndex(v => v !== null), brk = Q.lab.indexOf('2001Q2');
  let mx = iq, mn = brk;
  for (let i = iq; i < brk; i++) if (bq[i] > bq[mx]) mx = i;
  for (let i = brk; i < bq.length; i++) if (bq[i] < bq[mn]) mn = i;
  const nq = bq.length - 1;
  plot('bb-a', [
    { x: Q._x.slice(iq), y: bq.slice(iq), mode: 'lines', name: 'Nominal 10y Treasury beta', showlegend: true, line: { color: K.blue, width: 1.4 },
      text: Q.lab.slice(iq), hovertemplate: '%{text}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl(`A: quarterly, ${qw}-quarter windows, ${Q.lab[iq].slice(0, 4)}-${Q.lab[nq].slice(0, 4)}`),
    shapes: [hline(0, K.navy), vline('2001-04-01', K.navy, 'dot'), vline('2020-01-01', K.navy, 'dot')],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Bond-stock beta', { zeroline: false }) }));
  const i18 = firstAt(Dd._t, dayOf('2018-01-01')), ic = firstAt(Dd._t, dayOf('2020-03-11')), nd = Dd._t.length - 1;
  let below = 0, k = 0;
  for (let i = ic; i <= nd; i++) if (bn[i] !== null && bt[i] !== null) { k++; if (bn[i] < bt[i]) below++; }
  plot('bb-b', [
    { x: Dd._x.slice(i18), y: bn.slice(i18), mode: 'lines', name: 'Nominal 10y Treasury beta', line: { color: K.blue, width: 1.1 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: Dd._x.slice(i18), y: bt.slice(i18), mode: 'lines', name: 'Inflation-indexed 10y (TIPS) beta', line: { color: K.amber, width: 1.1 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl(`B: daily, ${dw}-day windows, 2018-2026`), shapes: [hline(0, K.navy), vline('2020-03-11', K.navy, 'dot')],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Bond-stock beta', { zeroline: false }) }));
  const sp = R.subperiods, keys = Object.keys(sp).filter(s => !s.startsWith('TIPS'));
  out('bb-out', [T.bb(qw, nf(bq[mx], 2), Q.lab[mx], nf(bq[mn], 2), Q.lab[mn], nf(bq[nq], 2), Q.lab[nq]),
    T.bb2(dw, pct(below / k, 0), fd(Dd._t[nd]), nf(bn[nd], 2), nf(bt[nd], 2)),
    T.bb3(...keys.map(s => nf(Math.abs(sp[s].beta) < 0.005 ? 0 : sp[s].beta, 2) + ' (SE ' + nf(sp[s].se, 2) + ')'))]);
}

// ================================================================= concentration premium: d_t = r_SPY - r_RSP
function nwMean(x) {                // ai_discovery_case.nw_mean: Newey-West t, Bartlett, L = floor(4 (T/100)^(2/9))
  const n = x.length, L = Math.floor(4 * Math.pow(n / 100, 2 / 9));
  let m = 0; for (const v of x) m += v; m /= n;
  const e = x.map(v => v - m);
  let s = 0; for (const v of e) s += v * v; s /= n;
  for (let l = 1; l <= L; l++) { let c = 0; for (let i = l; i < n; i++) c += e[i] * e[i - l]; s += 2 * (1 - l / (L + 1)) * c / n; }
  const t = m / Math.sqrt(s / n), ma = 100 * 252 * m;
  return { m: ma, t, se: Math.abs(ma / t), mde: 2.8 * Math.abs(ma / t), n };
}
function premium() {
  const A = decode(D.ai), y = +$('ai-y').value, s = firstAt(A._t, dayOf(`${y}-01-01`)), n = A._t.length - 1;
  $('ai-y-v').textContent = y;
  const full = nwMean(A.d), a = nwMean(A.d.slice(0, s)), b = nwMean(A.d.slice(s));
  const rows = [[full, `${monEN(A._t[0])} - ${monEN(A._t[n])}`, K.blue, true], [a, `${new Date(A._t[0] * DAY).getUTCFullYear()} - ${y - 1}`, K.green, false], [b, `${y} - 2026`, K.green, true]];
  const labs = rows.map(r => r[1]);
  plot('ai-ci', [
    { x: rows.map(r => r[0].m), y: labs, mode: 'markers', name: 'Estimate with HAC 95% interval', marker: { color: rows.map(r => r[2]), size: 10 },
      error_x: { type: 'data', array: rows.map(r => 1.96 * r[0].se), color: K.blue, thickness: 1.6, width: 5 }, hovertemplate: '%{y}: %{x:.2f}% per year<extra></extra>' },
    { x: rows.filter(r => r[3]).flatMap(r => [r[0].mde, -r[0].mde]), y: rows.filter(r => r[3]).flatMap(r => [r[1], r[1]]), mode: 'markers', name: 'Minimum detectable effect, ±2.8 SE',
      marker: { color: K.red, symbol: 'line-ns-open', size: 18, line: { width: 2.5, color: K.red } }, hovertemplate: 'MDE %{x:.2f}%<extra></extra>' }
  ], layout({ title: ttl('Is there a concentration premium?'), shapes: [vline(0, K.navy, 'dot')],
    annotations: rows.map(r => ({ x: r[0].m, y: r[1], text: `${r[0].m > 0 ? '+' : ''}${r[0].m.toFixed(2)}% (t = ${r[0].t.toFixed(2)})`, showarrow: false, yshift: 16, bgcolor: 'rgba(255,255,255,0.85)', font: { size: 10, color: K.navy } })),
    xaxis: AX('Mean of r<sub>SPY</sub> − r<sub>RSP</sub> (% per year)', { range: [-9, 9], zeroline: false }), yaxis: AX('', { type: 'category', autorange: 'reversed' }) }));
  const cs = cum(A.d).map(v => 100 * v);
  plot('ai-cum', [
    { x: A._x, y: cs, mode: 'lines', name: 'Cumulative sum of r<sub>SPY</sub> − r<sub>RSP</sub>', line: { color: K.blue, width: 1.1 }, hovertemplate: '%{x}: %{y:.1f}%<extra></extra>' }
  ], layout({ title: ttl(`Split of the sample on 1 Jan ${y}`), shapes: [vline(iso(dayOf(`${y}-01-01`)), K.red, 'dash'), hline(0, K.navy, 'dot')],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Cumulative log-return difference (%)') }));
  out('ai-out', [T.ai(sgn(full.m, 2) + '%', nf(full.t, 2), nf(full.mde, 1) + '%', full.n),
    T.ai2(y - 1, sgn(a.m, 2) + '%', nf(a.t, 2), y, sgn(b.m, 2) + '%', nf(b.t, 2), nf(b.mde, 1) + '%')]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['hi-y'], history); P('hi-play', 'hi-y', [...range(1300, 2020, 10), 2026], 140);
  on(['rr-y', 'rr-a'], riskReturn); P('rr-play', 'rr-y', range(2015, 2024, 1), 900);
  $('dd-chart').style.height = '470px';
  const nd = D.drawdowns.sp.t.length - 1;
  $('dd-t').max = nd; $('dd-t').value = nd; on(['dd-t'], drawdowns); P('dd-play', 'dd-t', range(60, nd, 20), 45);
  on(['vx-lo', 'vx-hi'], vix); P('vx-play', 'vx-lo', range(10, 30, 1), 350);
  on(['co-w'], correlations); P('co-play', 'co-w', range(63, 756, 21), 300);
  on(['bt-y'], bet); P('bt-play', 'bt-y', range(1997, 2025, 1), 700);
  on(['us-b', 'us-p'], usdt); P('us-play', 'us-b', range(0.1, 2, 0.1), 300);
  on(['cc-y'], concentration); P('cc-play', 'cc-y', range(2003, 2025, 1), 700);
  on(['hh-chi', 'hh-p'], elasticity); P('hh-play', 'hh-chi', range(0, 10, 0.25), 180);
  on(['bb-q', 'bb-d'], bondBeta); P('bb-play', 'bb-d', range(20, 250, 10), 500);
  on(['ai-y'], premium); P('ai-play', 'ai-y', range(2005, 2024, 1), 800);
  const PFX = { 'history': 'hi', 'risk-return': 'rr', 'drawdowns': 'dd', 'vix': 'vx', 'correlations': 'co', 'bet': 'bt', 'usdt': 'us',
    'concentration': 'cc', 'elasticity': 'hh', 'bond-beta': 'bb', 'premium': 'ai' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  history(); riskReturn(); drawdowns(); vix(); correlations(); bet(); usdt(); concentration(); elasticity(); bondBeta(); premium();
}
window.CH0 = { annStats, rollCorr, rollBeta, meanOn, nwMean, relE, decode, firstAt, dayOf };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

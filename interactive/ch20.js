// Chapter 20 interactive page: one block per chart slide, computed in the browser from ch20_data.js.
(function () {
'use strict';
const D = window.CH20_DATA;
const { mean, median, nf, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH20_TEXT;
const K = D.col, M = D.models, H = D.horizons;
const SHORT = { HAR: 'HAR', logHAR: 'log-HAR', HARQ: 'HARQ', SHAR: 'SHAR', 'logHAR-K': 'log-HAR-K', 'Sig-L': 'Sig-L', 'Sig-LK': 'Sig-LK' };
const LABEL = { HAR: 'HAR', logHAR: 'log-HAR', HARQ: 'HARQ', SHAR: 'SHAR', 'logHAR-K': 'log-HAR + kernel weights',
  'Sig-L': 'Signature LASSO', 'Sig-LK': 'Signature LASSO + kernel weights' };
const CLASS_LABEL = { stocks: 'US stocks (40)', futures: 'Futures (5)', forex: 'FX (5)', all: 'All 50 assets' };
const GROUPS = ['all', 'stocks', 'futures', 'forex'];
const HCOL = [K.blue, K.orange, K.red];
const mi = m => M.indexOf(m);
const inGroup = g => D.kinds.map(k => g === 'all' || k === g);
const hTitle = h => `h = ${h} day${h > 1 ? 's' : ''}`;
const fmtDate = s => {                                        // 2020-03-16 -> 16 Mar 2020 / 16 mar. 2020
  const [y, m, d] = s.split('-').map(Number);
  return `${d} ${T.months[m - 1]} ${y}`;
};
const pad = v => { const a = Math.min(...v), b = Math.max(...v), d = 0.06 * (b - a); return [a - d, b + d]; };
const rgba = (hex, a) => `rgba(${parseInt(hex.slice(1, 3), 16)},${parseInt(hex.slice(3, 5), 16)},${parseInt(hex.slice(5, 7), 16)},${a})`;

// ================================================================= 1. realised volatility across asset classes
const VR_COL = { JPM: K.blue, NVDA: K.red, ES: K.green, CL: K.orange, EURUSD: K.purple, USDJPY: K.teal };
function smooth(v, k) {                                        // trailing mean of k weekly values = mean over 5k days
  const o = [];
  for (let i = 0; i < v.length; i++) {
    if (i < k - 1) { o.push(null); continue; }
    let s = 0; for (let j = i - k + 1; j <= i; j++) s += v[j];
    o.push(s / k);
  }
  return o;
}
function volare() {
  const k = +$('vr-k').value, lin = $('vr-s').value === 'lin';
  $('vr-k-v').textContent = k === 1 ? T.week1 : T.weeks(k);
  const items = [];
  for (const cls of D.classes) {
    const syms = D.volare.picks[cls], peaks = [];
    const tr = syms.map(s => {
      const S = D.volare.series[s], v = smooth(S.v, k);
      let best = -1, bd = '';
      S.dates.forEach((d, i) => { if (d >= '2020-01-01' && d <= '2020-06-30' && v[i] !== null && v[i] > best) { best = v[i]; bd = d; } });
      peaks.push([s, best, bd]);
      return { x: S.dates, y: v, mode: 'lines', name: s, line: { color: VR_COL[s], width: 1.1 }, hovertemplate: s + ' %{x}: %{y:.1f}%<extra></extra>' };
    });
    plot('vr-' + cls, tr, layout({ title: ttl(CLASS_LABEL[cls]), margin: { l: 50, r: 8, t: 30, b: 40 },
      xaxis: AX('', { type: 'date' }),
      yaxis: AX(cls === 'stocks' ? 'Annualised volatility, % (' + (k === 1 ? '5-day' : 5 * k + '-day') + ' mean)' : '',
        lin ? { range: [0, 480] } : { type: 'log', range: [Math.log10(2), Math.log10(600)], tickvals: [5, 10, 20, 50, 100, 200, 500] }) }));
    items.push(T.vr(T.cls[cls], 5 * k, ...peaks.flatMap(([s, v, d]) => [s, nf(v, 0), fmtDate(d)])));
  }
  out('vr-out', items);
}

// ================================================================= 2. QLIKE relative to HAR, asset by asset
function ratios(h, b, g) {                                     // per-asset ratio model / benchmark, assets of group g
  const keep = inGroup(g), Q = D.ql[h], ib = mi(b);
  return M.map((_, j) => Q.filter((_, a) => keep[a]).map(r => r[j] / r[ib]));
}
function quantile(s, p) { const h = (s.length - 1) * p, i = Math.floor(h); return s[i] + (h - i) * ((s[i + 1] ?? s[i]) - s[i]); }
function boxStats(v) {                                         // matplotlib boxplot: linear quartiles, whiskers at the last point within 1.5 IQR
  const s = [...v].sort((a, b) => a - b), q1 = quantile(s, 0.25), q3 = quantile(s, 0.75), iqr = q3 - q1;
  return { q1, q3, med: quantile(s, 0.5), lo: s.find(x => x >= q1 - 1.5 * iqr), hi: [...s].reverse().find(x => x <= q3 + 1.5 * iqr) };
}
const dropTop = (v, k) => [...v].sort((a, b) => a - b).slice(0, Math.max(v.length - k, 1));
function qlikeRatio() {
  const b = $('qr-b').value, g = $('qr-g').value, k = +$('qr-k').value, mods = M.filter(m => m !== b);
  $('qr-k-v').textContent = k;
  const items = [], rep = b === 'HAR' ? ['logHAR', 'Sig-LK'] : ['Sig-L', 'Sig-LK'];
  H.forEach((h, i) => {
    const R = ratios(h, b, g).map(v => dropTop(v, k)), tr = [];
    mods.forEach(m => {
      const v = R[mi(m)];
      const b5 = boxStats(v);
      tr.push({ x: [SHORT[m]], q1: [b5.q1], median: [b5.med], q3: [b5.q3], lowerfence: [b5.lo], upperfence: [b5.hi], type: 'box', name: SHORT[m],
        fillcolor: rgba(K[m], 0.35), line: { color: K[m], width: 1.3 }, showlegend: false, hoverinfo: 'y' });
    });
    tr.push({ x: mods.map(m => SHORT[m]), y: mods.map(m => mean(R[mi(m)])), mode: 'markers', name: 'Mean', marker: { symbol: 'diamond', size: 8, color: mods.map(m => K[m]) },
      showlegend: false, hovertemplate: '%{x}: mean %{y:.3f}<extra></extra>' });
    plot('qr-' + h, tr, layout({ title: ttl(hTitle(h)), margin: { l: 50, r: 8, t: 30, b: 40 }, shapes: [hline(1, K.navy, 'dash')],
      xaxis: AX('', { tickangle: -40, tickfont: { size: 10, color: K.navy } }),
      yaxis: AX(i === 0 ? 'QLIKE relative to ' + SHORT[b] : '') }));
    items.push(T.qr(h, ...rep.flatMap(m => [SHORT[m], nf(mean(R[mi(m)]), 3), nf(median(R[mi(m)]), 3)])));
  });
  out('qr-out', [T.qr0(T.cls[g], k, SHORT[b]), ...items]);
}

// ================================================================= 3. model confidence sets
function mcs() {
  const l = $('mc-l').value, g = $('mc-g').value, lev = +$('mc-a').value, a = 1 - lev / 100, keep = inGroup(g);
  $('mc-a-v').textContent = lev + '%';
  const share = (h, m) => { const P = D.mcs[l][h].filter((_, i) => keep[i]); return P.filter(p => p[mi(m)] > a + 1e-12).length / P.length; };
  plot('mc-chart', H.map((h, i) => ({ x: M.map(m => SHORT[m]), y: M.map(m => 100 * share(h, m)), type: 'bar', name: 'h = ' + h, marker: { color: HCOL[i], line: { color: '#fff', width: 1 } },
    hovertemplate: `h = ${h}, %{x}: %{y:.0f}%<extra></extra>` })),
    layout({ barmode: 'group', bargap: 0.22, title: ttl(`${CLASS_LABEL[g]}: share of assets in the ${lev}% MCS (${l === 'ql' ? 'QLIKE' : 'MSE'})`),
      xaxis: AX(''), yaxis: AX('Share of assets, %', { range: [0, 105] }) }));
  const f = m => H.map(h => nf(100 * share(h, m), 0) + '%').join(', ');
  out('mc-out', [T.mc(lev, l === 'ql' ? 'QLIKE' : 'MSE', T.cls[g], f('logHAR'), f('Sig-LK'), f('HAR'))]);
}

// ================================================================= 4. JPM in the COVID-19 crash
const CV_SHOW = ['HAR', 'logHAR', 'Sig-LK'];
function covid() {
  const h = +$('cv-h').value, C = D.covid[h], n = C.dates.length;
  $('cv-t').max = n - 1; if (+$('cv-t').value > n - 1) $('cv-t').value = n - 1;
  const t = +$('cv-t').value, x = C.dates.slice(0, t + 1);
  $('cv-t-v').textContent = fmtDate(C.dates[t]);
  const tr = [{ x, y: C.y.slice(0, t + 1), mode: 'lines', name: h === 1 ? 'Realised (5-minute RV), next day' : `Realised (5-minute RV), mean of the next ${h} days`,
    line: { color: '#000000', width: 1.6 }, hovertemplate: 'Realised %{x}: %{y:.1f}%<extra></extra>' }];
  M.forEach(m => tr.push({ x, y: C.f[m].slice(0, t + 1), mode: 'lines', name: LABEL[m] + ' forecast', visible: CV_SHOW.includes(m) ? true : 'legendonly',
    line: { color: K[m], width: 1.3 }, hovertemplate: SHORT[m] + ' %{x}: %{y:.1f}%<extra></extra>' }));
  plot('cv-chart', tr, layout({ title: ttl(`JPM, ${hTitle(h)} ahead: forecasts made at each origin`), legend: { orientation: 'h', x: 0, y: -0.14, yanchor: 'top', font: { size: 11 } },
    xaxis: AX('', { type: 'date', range: [C.dates[0], C.dates[n - 1]] }), yaxis: AX('Annualised volatility, %', { range: [0, 1.08 * Math.max(...C.y, ...CV_SHOW.flatMap(m => C.f[m]))] }) }));
  const q = m => nf(mean(C.ql[m].slice(0, t + 1)), 3);
  out('cv-out', [T.cv1(fmtDate(C.dates[t]), nf(C.y[t], 0), nf(C.f.HAR[t], 0), nf(C.f.logHAR[t], 0), nf(C.f['Sig-LK'][t], 0)),
    T.cv2(fmtDate(C.dates[0]), fmtDate(C.dates[t]), t + 1, q('HAR'), q('logHAR'), q('Sig-LK'))]);
}

// ================================================================= 5. stress periods vs normal times
const SP_MODELS = ['logHAR', 'HARQ', 'SHAR', 'logHAR-K', 'Sig-L', 'Sig-LK'];
const PERIODS = ['covid', 'apr2025', 'rest'];
const P_LABEL = { covid: 'COVID-19<br>crash', apr2025: 'Apr 2025<br>tariffs', rest: 'Other<br>days' };
const P_HOVER = { covid: 'COVID-19 crash (20 Feb–30 Apr 2020)', apr2025: '2–30 Apr 2025 (US tariff shock)', rest: 'All other days' };
function subRatio(h, p, m, g, stat) {
  const keep = inGroup(g), v = D.sub[h][p].filter((r, i) => keep[i] && r !== null).map(r => r[mi(m)] / r[0]);
  return v.length ? (stat === 'median' ? median(v) : mean(v)) : null;
}
function subperiod() {
  const g = GROUPS[+$('sp-g').value], st = $('sp-st').value;
  $('sp-g-v').textContent = T.cls[g];
  const tr = [], lay = { barmode: 'group', bargap: 0.18, grid: { rows: 1, columns: 3, pattern: 'independent' }, shapes: [], annotations: [] };
  H.forEach((h, i) => {
    const ax = i === 0 ? '' : String(i + 1);
    SP_MODELS.forEach(m => tr.push({ x: PERIODS.map(p => P_LABEL[p]), y: PERIODS.map(p => subRatio(h, p, m, g, st)), customdata: PERIODS.map(p => P_HOVER[p]), type: 'bar',
      name: SHORT[m], legendgroup: m, showlegend: i === 0, marker: { color: K[m] }, xaxis: 'x' + ax, yaxis: 'y' + ax, hovertemplate: SHORT[m] + ', %{customdata}: %{y:.2f}<extra></extra>' }));
    lay['xaxis' + ax] = AX('', { tickfont: { size: 10, color: K.navy } });
    lay['yaxis' + ax] = AX(i === 0 ? 'QLIKE relative to HAR' : '', { rangemode: 'tozero' });
    lay.shapes.push({ type: 'line', xref: 'x' + ax + ' domain', yref: 'y' + ax, x0: 0, x1: 1, y0: 1, y1: 1, line: { color: K.navy, width: 1.5, dash: 'dash' } });
    lay.annotations.push({ text: 'h = ' + h, xref: 'x' + ax + ' domain', yref: 'paper', x: 0, y: 1.08, showarrow: false, xanchor: 'left', font: { size: 12, color: K.navy } });
  });
  plot('sp-chart', tr, layout(lay));
  const v = (h, p, m) => { const x = subRatio(h, p, m, g, st); return x === null ? '—' : nf(x, 2); };
  out('sp-out', [T.sp1(T.cls[g], T.stat[st], v(1, 'covid', 'logHAR'), v(1, 'covid', 'Sig-LK'), v(1, 'covid', 'HARQ'), v(1, 'apr2025', 'logHAR'), v(1, 'apr2025', 'Sig-LK'),
    v(1, 'rest', 'logHAR'), v(1, 'rest', 'Sig-LK')), T.sp22(v(22, 'covid', 'Sig-LK'), v(22, 'covid', 'Sig-L'))]);
}

// ================================================================= 6. kernel weights at the origin 16 March 2020
function levyArea(P, k) {                                      // (S^12 - S^21)/2 of the piecewise-linear path through the first k points
  let A = 0; const x0 = P[0][0], y0 = P[0][1];
  for (let i = 1; i < k; i++) A += 0.5 * ((P[i - 1][0] - x0) * (P[i][1] - P[i - 1][1]) - (P[i - 1][1] - y0) * (P[i][0] - P[i - 1][0]));
  return A;
}
function weights() {
  const W = D.weights, ic = +$('kw-c').value, c = W.grid[ic], N = +$('kw-N').value, k = +$('kw-k').value, n = W.n;
  $('kw-c-v').textContent = nf(c, c < 1 ? 2 : c < 2 ? 2 : 1); $('kw-N-v').textContent = N; $('kw-k-v').textContent = k + ' / 22';
  const dj = W.dist_jpm[N], z = dj.map(v => -c * v), zm = Math.max(...z), e = z.map(v => Math.exp(v - zm)), s = e.reduce((a, b) => a + b, 0), wj = e.map(v => v / s);
  const avg = W.avg[N][ic], essJ = 1 / wj.reduce((a, b) => a + b * b, 0);
  plot('kw-chart', [
    { x: W.dates, y: avg, mode: 'lines', name: 'Kernel weight × window length, average of 40 stocks', line: { color: K.red, width: 1.3 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: W.dates, y: wj.map(v => v * n), mode: 'lines', name: 'Kernel weight × window length, JPM', line: { color: K.blue, width: 0.9 }, opacity: 0.85, hovertemplate: 'JPM %{x}: %{y:.2f}<extra></extra>' },
    { x: W.dates, y: W.vol40, mode: 'lines', name: 'Annualised RV volatility, average of 40 stocks (right, %)', yaxis: 'y2', line: { color: K.green, width: 0.9 }, hovertemplate: '%{x}: %{y:.0f}%<extra></extra>' }
  ], layout({ title: ttl(`Sig-LK, h = 1, origin 16 Mar 2020: c = ${c.toFixed(2)}, depth N = ${N}`), shapes: [hline(1, K.navy, 'dash')],
    legend: { orientation: 'h', x: 0, y: -0.14, yanchor: 'top', font: { size: 11 } },
    xaxis: AX('', { type: 'date' }), yaxis: AX('Weight relative to equal weighting'),
    yaxis2: AX('Volatility, %', { overlaying: 'y', side: 'right', showgrid: false, rangemode: 'tozero', color: K.green, tickfont: { size: 11, color: K.green } }) }));
  // paths in the (return, log RV) plane, each translated to start at the origin of the plane
  const O = W.paths.origin, Pn = W.paths[N], pc = P => P.map(p => [100 * p[0], p[1] - P[0][1]]);
  const o = pc(O), on = pc(Pn.p_near), of = pc(Pn.p_far), ok = o.slice(0, k);
  plot('kw-path', [
    { x: [...ok.map(p => p[0]), ok[0][0]], y: [...ok.map(p => p[1]), ok[0][1]], fill: 'toself', fillcolor: rgba(K.red, 0.12), mode: 'none', showlegend: false, hoverinfo: 'skip' },
    { x: [ok[0][0], ok[k - 1][0]], y: [ok[0][1], ok[k - 1][1]], mode: 'lines', name: 'Chord', line: { color: K.navy, width: 1, dash: 'dash' }, hoverinfo: 'skip' },
    { x: on.map(p => p[0]), y: on.map(p => p[1]), mode: 'lines+markers', name: 'Closest training window (ends ' + Pn.near + ')', line: { color: K.blue, width: 1 }, marker: { size: 3 }, hovertemplate: '%{x:.1f}%, %{y:.2f}<extra></extra>' },
    { x: of.map(p => p[0]), y: of.map(p => p[1]), mode: 'lines+markers', name: 'Farthest training window (ends ' + Pn.far + ')', line: { color: K.amber, width: 1 }, marker: { size: 3 }, hovertemplate: '%{x:.1f}%, %{y:.2f}<extra></extra>' },
    { x: ok.map(p => p[0]), y: ok.map(p => p[1]), mode: 'lines+markers', name: 'Origin window, 22 days to 16 Mar 2020', line: { color: K.red, width: 1.8 }, marker: { size: 5 }, hovertemplate: '%{x:.1f}%, %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl('JPM: 22-day paths (cumulative return, log RV), shifted to start at 0'), legend: { orientation: 'h', x: 0, y: -0.2, yanchor: 'top', font: { size: 11 } },
    xaxis: AX('Cumulative open-to-close return in the window, %', { range: pad([...o, ...on, ...of].map(p => p[0])) }),
    yaxis: AX('log RV minus its first value', { range: pad([...o, ...on, ...of].map(p => p[1])) }) }));
  out('kw-out', [T.kw1(nf(c, 2), N, nf(Math.min(...avg), 2), nf(Math.max(...avg), 2), nf(W.ess_avg[N][ic], 0), n),
    T.kw2(nf(Math.min(...wj) * n, 2), nf(Math.max(...wj) * n, 2), nf(essJ, 0)),
    T.kw3(k, nf(levyArea(O, k), 3), fmtDate(Pn.near), fmtDate(Pn.far))]);
}

// ================================================================= 7. the 2 x 2 ablation
const AB_MODELS = ['logHAR', 'logHAR-K', 'Sig-L', 'Sig-LK'];
function ablation() {
  const g = $('ab-g').value, x = +$('ab-x').value, hs = +$('ab-h').value, keep = inGroup(g);
  const left = x > 0 ? D.assets[x - 1] : null;
  $('ab-x-v').textContent = left || T.none;
  const val = (h, m) => mean(D.ql[h].filter((_, a) => keep[a] && D.assets[a] !== left).map(r => r[mi(m)] / r[1]));
  const V = AB_MODELS.map(m => H.map(h => val(h, m))), lo = Math.min(...V.flat()), hi = Math.max(...V.flat());
  plot('ab-chart', AB_MODELS.map((m, j) => ({ x: H.map(h => 'h = ' + h), y: V[j], type: 'bar', name: LABEL[m], marker: { color: K[m] },
    hovertemplate: SHORT[m] + ', %{x}: %{y:.3f}<extra></extra>' })),
    layout({ barmode: 'group', bargap: 0.2, title: ttl(CLASS_LABEL[g] + (left ? ', without ' + left : '')), shapes: [hline(1, K.navy, 'dash')],
      xaxis: AX(''), yaxis: AX('QLIKE relative to log-HAR', { range: [Math.min(0.95, lo - 0.02), hi + 0.03] }) }));
  const idx = D.assets.map((_, a) => a).filter(a => keep[a]), rr = idx.map(a => D.ql[hs][a][mi('Sig-LK')] / D.ql[hs][a][1]);
  plot('ab-assets', [{ x: idx.map(a => D.assets[a]), y: rr.map(v => v - 1), base: 1, customdata: rr, type: 'bar', name: 'Sig-LK / log-HAR',
    marker: { color: idx.map((a, j) => (D.assets[a] === left ? K.navy : rr[j] > 1 ? K['Sig-LK'] : K.logHAR)) },
    hovertemplate: '%{x}: %{customdata:.3f}<extra></extra>' }],
  layout({ title: ttl(`Sig-LK relative to log-HAR by asset, h = ${hs}`), showlegend: false, shapes: [hline(1, K.navy, 'dash')],
    xaxis: AX('', { tickangle: -90, nticks: 60, tickfont: { size: 8, color: K.navy } }), yaxis: AX('QLIKE ratio') }));
  const f = m => H.map(h => nf(val(h, m), 3)).join(', ');
  const top = rr.indexOf(Math.max(...rr));
  out('ab-out', [T.ab1(left || T.none, T.cls[g], f('logHAR-K'), f('Sig-L'), f('Sig-LK')), T.ab2(hs, D.assets[idx[top]], nf(rr[top], 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  on(['vr-k', 'vr-s'], volare); P('vr-play', 'vr-k', range(1, 13, 1), 600);
  on(['qr-b', 'qr-g', 'qr-k'], qlikeRatio); P('qr-play', 'qr-k', range(0, 10, 1), 600);
  on(['mc-l', 'mc-g', 'mc-a'], mcs); P('mc-play', 'mc-a', range(75, 99, 1), 300);
  $('cv-t').value = 999; on(['cv-h', 'cv-t'], covid); P('cv-play', 'cv-t', range(0, D.covid[1].dates.length - 1, 1), 120);
  on(['sp-g', 'sp-st'], subperiod); P('sp-play', 'sp-g', range(0, 3, 1), 1200);
  $('kw-c').max = D.weights.grid.length - 1; $('kw-c').value = D.weights.grid.indexOf(D.weights.c_lect);
  on(['kw-c', 'kw-N', 'kw-k'], weights); P('kw-play', 'kw-c', range(0, D.weights.grid.length - 1, 1), 700); P('kw-play2', 'kw-k', range(2, 22, 1), 300);
  $('ab-x').max = D.assets.length; on(['ab-g', 'ab-x', 'ab-h'], ablation); P('ab-play', 'ab-x', range(0, D.assets.length, 1), 400);
  volare(); qlikeRatio(); mcs(); covid(); subperiod(); weights(); ablation();
}
window.CH20 = { smooth, ratios, levyArea, subRatio };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

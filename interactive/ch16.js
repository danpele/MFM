// Chapter 16 interactive page: one block per chart slide, computed in the browser from ch16_data.js.
(function () {
'use strict';
const D = window.CH16_DATA;
const { C, sum, mean, sdev, median, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH16_TEXT;

// ---------------------------------------------------------------- colours (same as the slides, generate_all_charts.py)
const K = { MainBlue: '#1A3A6E', IDAred: '#CD0000', Forest: '#2E7D32', Amber: '#B5853F', Orange: '#E67E22', Purple: '#8E44AD',
  Teal: '#17A2B8', Magenta: '#D63384', Navy: '#1F2A44', Band: '#C5D2E8' };
const COL = { BTC: K.Orange, ETH: K.Purple, XRP: K.MainBlue, ADA: K.Forest, DOGE: K.Amber, LTC: K.Teal, SPX: K.MainBlue, QQQ: K.IDAred,
  GOLD: K.Forest, USDT: K.Forest, USDC: K.MainBlue, DAI: K.Orange, IBIT: K.MainBlue, ETHA: K.Purple };
const CLASS_COL = { Crypto: K.Orange, Equity: K.MainBlue, FX: K.Forest, Commodity: K.Amber, Bond: K.Purple };
const NAME = { BTC: 'Bitcoin', ETH: 'Ethereum', DOGE: 'Dogecoin', ADA: 'Cardano', LTC: 'Litecoin', XRP: 'XRP', SPX: 'S&P 500',
  QQQ: 'Nasdaq 100 (QQQ)', GOLD: 'Gold (XAU/USD)', USDT: 'Tether', USDC: 'USD Coin', DAI: 'Dai', IBIT: 'IBIT', ETHA: 'ETHA' };
const rgba = (h, a) => `rgba(${parseInt(h.slice(1, 3), 16)},${parseInt(h.slice(3, 5), 16)},${parseInt(h.slice(5, 7), 16)},${a})`;

// ---------------------------------------------------------------- helpers
const DAY = 864e5;
function expand(o) {                    // {d0, gap} -> ISO dates and day numbers
  let t = Date.parse(o.d0 + 'T00:00:00Z');
  const s = [o.d0], n = [t / DAY];
  for (const g of o.gap) { t += g * DAY; s.push(new Date(t).toISOString().slice(0, 10)); n.push(t / DAY); }
  return { s, n };
}
const dnum = s => Date.parse(s.slice(0, 10) + 'T00:00:00Z') / DAY;
const fd = s => { const [y, m, d] = s.split('-'); return T.date(+d, T.mon[+m - 1], y); };          // 5 Feb 2020
const fm = s => { const [y, m] = s.split('-'); return T.month(T.mon[+m - 1], y); };                // Feb 2020
const monthEnd = ym => { const [y, m] = ym.split('-').map(Number); return new Date(Date.UTC(y, m, 0)).toISOString().slice(0, 10); };
const fint = x => { const s = Math.round(x).toString(); return s.replace(/\B(?=(\d{3})+(?!\d))/g, T.th); };
const sgn = (x, d) => (x > 0 ? '+' : '') + nf(x, d);
const corr = (x, y) => { const mx = mean(x), my = mean(y); let a = 0, b = 0, c = 0; for (let i = 0; i < x.length; i++) { const u = x[i] - mx, v = y[i] - my; a += u * v; b += u * u; c += v * v; } return a / Math.sqrt(b * c); };
const cums = a => { const c = [0]; for (const v of a) c.push(c[c.length - 1] + v); return c; };
function ols(y, x) {                    // y = a + b x; slope, R^2, Newey-West (Bartlett) SE of the slope without small-sample correction
  const n = y.length, mx = mean(x), my = mean(y);
  let sxx = 0, sxy = 0, syy = 0;
  for (let i = 0; i < n; i++) { sxx += (x[i] - mx) ** 2; sxy += (x[i] - mx) * (y[i] - my); syy += (y[i] - my) ** 2; }
  const b = sxy / sxx, a = my - b * mx, e = y.map((v, i) => v - a - b * x[i]);
  return { a, b, r2: (b * sxy) / syy, e, nw: L => {
    const u = e.map((v, i) => v * (x[i] - mx));             // slope score (constant partialled out)
    let s = sum(u.map(v => v * v));
    for (let l = 1; l <= L; l++) { let g = 0; for (let i = l; i < n; i++) g += u[i] * u[i - l]; s += 2 * (1 - l / (L + 1)) * g; }
    return Math.sqrt(s) / sxx;
  } };
}
const steps = (a, b, st) => { const v = range(a, b, st); if (v[v.length - 1] !== b) v.push(b); return v; };
const LOGT = { type: 'log', tickvals: [10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000], ticktext: ['10', '30', '100', '300', '1,000', '3,000', '10,000', '30,000', '100,000'] };
const sliderV = (id, txt) => { $(id + '-v').textContent = txt; };
function setMax(id, mx, val) { const el = $(id); el.max = mx; if (val !== undefined) el.value = val; }

// ================================================================= 1. market value
const MV = (() => { const M = D.mv; return { x: M.months.map(monthEnd), sh: expand(M.share) }; })();
function marketValue() {
  const M = D.mv, k = +$('mv-t').value, x = MV.x, ks = M.keys;
  const totM = x.map((_, i) => sum(ks.map(c => M.mv[c][i])));
  const day = k === x.length - 1 ? D.end : x[k];
  sliderV('mv-t', fm(M.months[k]));
  const tr = ks.map(c => ({ x, y: M.mv[c], type: 'scatter', mode: 'lines', stackgroup: 'one', name: NAME[c], line: { width: 0, color: COL[c] },
    fillcolor: rgba(COL[c], 0.85), hovertemplate: NAME[c] + ' %{x|%b %Y}: %{y:,.0f} bn<extra></extra>' }));
  tr.push({ x: MV.sh.s, y: M.share.v, xaxis: 'x', yaxis: 'y2', mode: 'lines', name: 'Bitcoin share of the 5 assets (%)', line: { color: K.Orange, width: 1.2 },
    hovertemplate: '%{x|%d %b %Y}: %{y:.1f}%<extra></extra>' });
  plot('mv-chart', tr, layout({ margin: { l: 60, r: 12, t: 20, b: 30 }, legend: Object.assign(layout().legend, { y: -0.1, traceorder: 'normal' }),
    shapes: [{ type: 'line', xref: 'x', yref: 'paper', x0: day, x1: day, y0: 0, y1: 1, line: { color: K.Navy, width: 1.5, dash: 'dot' } }],
    xaxis: AX('', { type: 'date', anchor: 'y2' }), yaxis: AX('Market value (USD bn)', { domain: [0.36, 1], rangemode: 'tozero' }),
    yaxis2: AX('%', { domain: [0, 0.27], range: [40, 100], tickvals: [50, 75, 100], anchor: 'x' }) }));
  const vals = ks.map(c => M.mv[c][k]);
  const R = M.ref;
  out('mv-out', [T.mv(fm(M.months[k]), fint(totM[k]), pct(vals[0] / totM[k]), pct(vals[1] / totM[k])),
    T.mv2(fint(R.total_peak), fd(R.total_peak_date), nf(R.btc_share_min, 1), fd(R.btc_share_min_date), nf(R.btc_share_max, 1), fd(R.btc_share_max_date))]);
}

// ================================================================= 2. rolling volatility
const VOLK = ['BTC', 'ETH', 'SPX', 'GOLD'], VOL_COL = { BTC: K.Orange, ETH: K.Purple, SPX: K.MainBlue, GOLD: K.Forest };
const VD = Object.fromEntries(VOLK.map(k => [k, expand(D.vol[k])]));
function rollVolSeries(k, w) {          // pandas rolling('wD', min_periods = int(0.9 ppy w/365)).std() x sqrt(ppy), shown from 2019
  const V = D.vol[k], r = V.r, n = VD[k].n, mp = Math.floor(0.9 * V.ppy * w / 365), c1 = cums(r), c2 = cums(r.map(v => v * v));
  const t0 = dnum('2019-01-01'), xs = [], ys = [];
  let j = 0;
  for (let i = 0; i < r.length; i++) {
    while (n[j] <= n[i] - w) j++;
    if (n[i] < t0) continue;
    const m = i - j + 1;
    if (m < Math.max(mp, 2)) continue;
    const s1 = c1[i + 1] - c1[j], s2 = c2[i + 1] - c2[j], v = (s2 - s1 * s1 / m) / (m - 1);
    xs.push(VD[k].s[i]); ys.push(100 * Math.sqrt(Math.max(v, 0) * V.ppy));
  }
  return { xs, ys };
}
function rollVol() {
  const w = +$('rv-w').value; sliderV('rv-w', T.ndays(w));
  const S = Object.fromEntries(VOLK.map(k => [k, rollVolSeries(k, w)]));
  plot('rv-chart', VOLK.map(k => ({ x: S[k].xs, y: S[k].ys, mode: 'lines', name: NAME[k] === 'Gold (XAU/USD)' ? 'Gold (XAU/USD)' : NAME[k],
    line: { color: VOL_COL[k], width: 1.3, dash: k === 'GOLD' ? 'dash' : 'solid' }, hovertemplate: NAME[k] + ' %{x|%d %b %Y}: %{y:.1f}%<extra></extra>' })),
  layout({ xaxis: AX('', { type: 'date' }), yaxis: AX('Annualised volatility (%), ' + w + '-day window', { rangemode: 'tozero' }) }));
  const last = k => S[k].ys[S[k].ys.length - 1], mx = k => Math.max(...S[k].ys);
  out('rv-out', [T.rv(w, nf(last('BTC'), 1), nf(last('ETH'), 1), nf(last('SPX'), 1), nf(last('GOLD'), 1), nf(last('BTC') / last('SPX'), 1)),
    T.rv2(nf(mx('BTC'), 1), nf(mx('ETH'), 1))]);
}

// ================================================================= 3. weekday
const WD_SPLITS = (() => { const a = []; for (let y = 2019; y <= 2026; y++) for (let m = 1; m <= 12; m++) { if (y === 2026 && m > 3) break; a.push(y === 2024 && m === 1 ? D.etf_start : `${y}-${String(m).padStart(2, '0')}-01`); } return a; })();
const WD_DOW = VD.BTC.n.map(t => (new Date(t * DAY).getUTCDay() + 6) % 7);          // Monday = 0
function weekday() {
  const k = +$('wd-s').value, split = WD_SPLITS[k], ts = dnum(split), r = D.vol.BTC.r.map(v => 100 * v), n = VD.BTC.n;
  sliderV('wd-s', fd(split));
  const pre = [[], [], [], [], [], [], []], post = [[], [], [], [], [], [], []];
  r.forEach((v, i) => (n[i] < ts ? pre : post)[WD_DOW[i]].push(v));
  const rms = a => Math.sqrt(mean(a.map(v => v * v))), varc = a => sdev(a) ** 2;
  const ratio = g => varc([...g[5], ...g[6]]) / varc([...g[0], ...g[1], ...g[2], ...g[3], ...g[4]]);
  const rmsWd = g => rms([].concat(...g.slice(0, 5)));
  const isEtf = split === D.etf_start, days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const prevDay = new Date((ts - 1) * DAY).toISOString().slice(0, 10);
  plot('wd-chart', [
    { x: days, y: pre.map(rms), type: 'bar', name: isEtf ? '2018 - 10 Jan 2024' : '2018 - ' + prevDay, marker: { color: K.MainBlue }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: days, y: post.map(rms), type: 'bar', name: isEtf ? '11 Jan 2024 - Sep 2026 (spot ETF era)' : split + ' - Sep 2026', marker: { color: K.Orange }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, xaxis: AX(''), yaxis: AX('Root mean squared return (%)', { rangemode: 'tozero' }) }));
  out('wd-out', [T.wd(fd(split), nf(ratio(pre), 2), nf(ratio(post), 2)), T.wd2(nf(rmsWd(pre), 2), nf(rmsWd(post), 2))]);
}

// ================================================================= 4. rolling correlation
const CORR = Object.fromEntries(['SPX', 'QQQ', 'GOLD'].map(k => [k, expand(D.corr[k])]));
function rollCorr(x, y, w) {
  const n = x.length, a = cums(x), b = cums(y), aa = cums(x.map(v => v * v)), bb = cums(y.map(v => v * v)), ab = cums(x.map((v, i) => v * y[i]));
  const res = new Array(n).fill(null);
  for (let i = w - 1; i < n; i++) {
    const s = i + 1 - w, sx = a[i + 1] - a[s], sy = b[i + 1] - b[s], sxx = aa[i + 1] - aa[s], syy = bb[i + 1] - bb[s], sxy = ab[i + 1] - ab[s];
    res[i] = (w * sxy - sx * sy) / Math.sqrt((w * sxx - sx * sx) * (w * syy - sy * sy));
  }
  return res;
}
function periodCorr(k, a, b) {
  const d = CORR[k].s, P = D.corr[k], x = [], y = [];
  d.forEach((s, i) => { if (s >= a && s <= b) { x.push(P.btc[i]); y.push(P.other[i]); } });
  return { r: corr(x, y), n: x.length };
}
function rollingCorr() {
  const w = +$('rc-w').value; sliderV('rc-w', T.ncdays(w));
  const st = { SPX: ['x', 'y', K.MainBlue, 'solid', 1.6, null], QQQ: ['x', 'y', K.IDAred, 'dash', 1.1, 'circle'], GOLD: ['x2', 'y2', K.Forest, 'solid', 1.3, null] };
  const tr = [], last = {};
  for (const k of ['SPX', 'QQQ', 'GOLD']) {
    const rc = rollCorr(D.corr[k].btc, D.corr[k].other, w), d = CORR[k].s, xs = [], ys = [];
    d.forEach((s, i) => { if (s >= '2018-01-01' && rc[i] !== null) { xs.push(s); ys.push(rc[i]); } });
    last[k] = ys[ys.length - 1];
    const [xa, ya, c, dash, lw, mk] = st[k];
    const t = { x: xs, y: ys, xaxis: xa, yaxis: ya, mode: mk ? 'lines+markers' : 'lines', name: 'Bitcoin vs ' + NAME[k], line: { color: c, width: lw, dash },
      hovertemplate: '%{x|%d %b %Y}: %{y:.2f}<extra>' + k + '</extra>' };
    if (mk) t.marker = { symbol: mk, size: 4, color: c, maxdisplayed: 40 };
    tr.push(t);
  }
  const e = D.etf_start, sh = [];
  for (const [xa, ya] of [['x', 'y'], ['x2', 'y2']]) {
    sh.push({ type: 'line', xref: xa, yref: ya + ' domain', x0: e, x1: e, y0: 0, y1: 1, line: { color: K.Navy, width: 1, dash: 'dash' } });
    sh.push({ type: 'line', xref: xa + ' domain', yref: ya, x0: 0, x1: 1, y0: 0, y1: 0, line: { color: K.Navy, width: 1 } });
  }
  plot('rc-chart', tr, layout({ shapes: sh, margin: { l: 56, r: 12, t: 44, b: 40 },
    annotations: [['x', 'y'], ['x2', 'y2']].map(([xa, ya]) => ({ x: e, y: 0.72, xref: xa, yref: ya, text: ' spot ETFs', showarrow: false, xanchor: 'left', font: { size: 11, color: K.Navy } }))
      .concat([{ text: 'Bitcoin vs equity indices', x: 0, xref: 'x domain', y: 1.1, yref: 'paper', showarrow: false, xanchor: 'left', yanchor: 'bottom', font: { size: 12, color: K.Navy } },
               { text: 'Bitcoin vs gold', x: 0, xref: 'x2 domain', y: 1.1, yanchor: 'bottom', yref: 'paper', showarrow: false, xanchor: 'left', font: { size: 12, color: K.Navy } }]),
    xaxis: AX('', { type: 'date', domain: [0, 0.48] }), xaxis2: AX('', { type: 'date', domain: [0.52, 1], anchor: 'y2' }),
    yaxis: AX('Correlation of daily returns', { range: [-0.4, 0.8] }), yaxis2: AX('', { range: [-0.4, 0.8], anchor: 'x2', matches: 'y', showticklabels: false }) }));
  const p = k => [periodCorr(k, '2017-01-01', '2019-12-31'), periodCorr(k, '2020-01-01', '2023-12-31'), periodCorr(k, D.etf_start, D.end)];
  const ps = p('SPX'), pg = p('GOLD');
  out('rc-out', [T.rc(w, nf(last.SPX, 2), nf(last.QQQ, 2), nf(last.GOLD, 2)),
    T.rc2(nf(ps[0].r, 2), fint(ps[0].n), nf(ps[1].r, 2), fint(ps[1].n), nf(ps[2].r, 2), fint(ps[2].n)), T.rc3(nf(pg[0].r, 2), nf(pg[1].r, 2), nf(pg[2].r, 2))]);
}

// ================================================================= 5. crypto indices
const CX = expand(D.crix), CX_M = (() => { const m = []; CX.s.forEach((s, i) => { if (i === 0 || s.slice(0, 7) !== CX.s[i - 1].slice(0, 7)) m.push(i); }); return m; })();
const CX_L = [['tot', 'Cap-weighted, all 5 assets (total market)', K.Orange, 2], ['k2', 'Cap-weighted, top 2', K.Purple, 1.3],
  ['k1', 'Top 1 (Bitcoin)', K.MainBlue, 1.3], ['ew', 'Equally weighted, 5 assets', K.Forest, 1.3]];
function crixStats(lev, i0) {
  const a = lev.slice(i0), yrs = (CX.n[CX.n.length - 1] - CX.n[i0]) / 365.25, lr = a.slice(1).map((v, i) => Math.log(v / a[i]));
  return { cagr: 100 * (Math.pow(a[a.length - 1] / a[0], 1 / yrs) - 1), vol: 100 * sdev(lr) * Math.sqrt(365), yrs };
}
function crix() {
  const k = +$('cx-s').value, i0 = CX_M[k], L = D.crix.lev;
  sliderV('cx-s', fd(CX.s[i0]));
  plot('cx-chart', CX_L.map(([c, name, col, lw]) => ({ x: CX.s.slice(i0), y: L[c].slice(i0).map(v => 1000 * v / L[c][i0]), mode: 'lines', name, line: { color: col, width: lw },
    hovertemplate: '%{x|%d %b %Y}: %{y:,.0f}<extra>' + c + '</extra>' })),
  layout({ xaxis: AX('', { type: 'date' }), yaxis: AX('Index level (1000 at start, log scale)', LOGT) }));
  const st = Object.fromEntries(CX_L.map(([c]) => [c, crixStats(L[c], i0)]));
  out('cx-out', [T.cx(fd(CX.s[i0]), nf(st.tot.yrs, 1), nf(st.tot.cagr, 1), nf(st.tot.vol, 1), nf(st.ew.cagr, 1), nf(st.ew.vol, 1), nf(st.k1.cagr, 1))]);
}

// ================================================================= 6. peg deviations
const STABLE = ['USDT', 'USDC', 'DAI'], PEG = Object.fromEntries(STABLE.map(k => [k, expand(D.peg[k])]));
function peg() {
  const c = +$('pg-c').value; sliderV('pg-c', c + ' bp');
  const tr = [], sh = [], n = STABLE.length, dom = i => [1 - (i + 1) / n + 0.07, 1 - i / n];
  STABLE.forEach((k, i) => {
    const ya = i ? 'y' + (i + 1) : 'y', P = D.peg[k], x = PEG[k].s;
    tr.push({ x, y: P.low, xaxis: 'x', yaxis: ya, mode: 'lines', name: 'Daily low (below −400 bp outside the panels)', legendgroup: 'low', showlegend: i === 0,
      line: { color: rgba(K.IDAred, 0.7), width: 0.7 }, hovertemplate: k + ' low %{x|%d %b %Y}: %{y:.0f} bp<extra></extra>' });
    tr.push({ x, y: P.close, xaxis: 'x', yaxis: ya, mode: 'lines', name: NAME[k] + ' daily close', line: { color: COL[k], width: 1 },
      hovertemplate: k + ' close %{x|%d %b %Y}: %{y:.1f} bp<extra></extra>' });
    for (const v of [c, -c]) sh.push({ type: 'line', xref: 'x domain', yref: ya, x0: 0, x1: 1, y0: v, y1: v, line: { color: K.Navy, width: 1, dash: 'dash' } });
  });
  const L = layout({ shapes: sh, margin: { l: 70, r: 12, t: 10, b: 30 }, legend: Object.assign(layout().legend, { y: -0.08 }), xaxis: AX('', { type: 'date', anchor: 'y3' }) });
  STABLE.forEach((k, i) => { L[i ? 'yaxis' + (i + 1) : 'yaxis'] = AX(NAME[k] + ', bp', { domain: dom(i), range: [-400, 100], tickvals: [-300, -150, 0], anchor: 'x' }); });
  plot('pg-chart', tr, L);
  out('pg-out', STABLE.map(k => { const a = D.peg[k].close, sh = a.filter(v => Math.abs(v) > c).length / a.length;
    return T.pg(NAME[k], nf(sdev(a), 1), c, pct(sh, 2), fint(a.filter(v => Math.abs(v) > c).length)); }));
}

// ================================================================= 7. March 2023
function svb() {
  const k = +$('dp-t').value, dates = D.svb.USDC.dates, day = dates[k];
  sliderV('dp-t', fd(day));
  const tr = [];
  for (const c of STABLE) {
    const S = D.svb[c];
    tr.push({ x: S.dates, y: S.close, mode: 'lines+markers', name: c + ' close', line: { color: COL[c], width: 1.3 }, marker: { size: 5, color: COL[c] }, hovertemplate: c + ' close %{x|%d %b}: %{y:.4f}<extra></extra>' });
    tr.push({ x: S.dates, y: S.low, mode: 'markers', name: c + ' daily low', marker: { symbol: 'triangle-down', size: 8, color: rgba(COL[c], 0.8) }, hovertemplate: c + ' low %{x|%d %b}: %{y:.4f}<extra></extra>' });
  }
  plot('dp-chart', tr, layout({ shapes: [hline(1, K.Navy, 'dash'), vline(day, K.Navy, 'dot')], xaxis: AX('', { type: 'date', tickformat: '%d %b' }), yaxis: AX('Price (USD)') }));
  const g = (c, f) => nf(D.svb[c][f][k], 4);
  out('dp-out', [T.dp(fd(day), g('USDC', 'close'), g('USDC', 'low'), g('DAI', 'close'), g('DAI', 'low'), g('USDT', 'close'), g('USDT', 'high'))]);
}

// ================================================================= 8. DeFi TVL
function tvl() {
  const V = D.tvl, k = +$('tv-s').value, x = V.months.map(monthEnd);
  const dl = V.tvl.slice(1).map((v, i) => Math.log(v / V.tvl[i])), de = V.eth.slice(1).map((v, i) => Math.log(v / V.eth[i]));
  sliderV('tv-s', fm(V.months[k + 1]));
  const y = dl.slice(k), xx = de.slice(k), R = ols(y, xx), se = R.nw(3);
  const band = k > 0 ? [{ type: 'rect', xref: 'x', yref: 'paper', x0: x[0], x1: x[k], y0: 0, y1: 1, fillcolor: rgba(K.Band, 0.45), line: { width: 0 }, layer: 'below' }] : [];
  plot('tv-chart', [
    { x, y: V.tvl.map(v => 100 * v / V.tvl[0]), mode: 'lines', name: 'DeFi total value locked', line: { color: K.Forest, width: 2 }, hovertemplate: '%{x|%b %Y}: %{y:,.0f}<extra>TVL</extra>' },
    { x, y: V.eth.map(v => 100 * v / V.eth[0]), mode: 'lines', name: 'Ethereum price', line: { color: K.Purple, width: 1.6 }, hovertemplate: '%{x|%b %Y}: %{y:,.0f}<extra>ETH</extra>' }
  ], layout({ shapes: band,
    xaxis: AX('', { type: 'date' }), yaxis: AX('Index (100 in Jan 2020, log scale)', LOGT) }));
  const lo = Math.min(...de), hi = Math.max(...de);
  plot('tv-sc', [
    { x: de.slice(0, k), y: dl.slice(0, k), mode: 'markers', name: 'Months left out', marker: { color: '#fff', line: { color: K.MainBlue, width: 1 }, size: 6 }, hovertemplate: 'ETH %{x:.1%}<br>TVL %{y:.1%}<extra></extra>' },
    { x: xx, y, mode: 'markers', name: 'Months in the regression', marker: { color: K.MainBlue, size: 6 }, text: V.months.slice(k + 1), hovertemplate: '%{text}<br>ETH %{x:.1%}<br>TVL %{y:.1%}<extra></extra>' },
    { x: [lo, hi], y: [R.a + R.b * lo, R.a + R.b * hi], mode: 'lines', name: 'OLS fit', line: { color: K.IDAred, width: 2 }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Monthly log changes'), xaxis: AX('Ethereum', { tickformat: '.0%' }), yaxis: AX('DeFi TVL', { tickformat: '.0%' }) }));
  const F = V.ref;
  out('tv-out', [T.tv(fm(V.months[k + 1]), y.length, nf(R.b, 2), nf(se, 3), nf(R.r2, 2)), T.tv2(nf(F.start, 1), fint(F.peak), fd(F.peak_date), fint(F.last), pct(1 - F.last / F.peak, 0))]);
}

// ================================================================= 9. liquidity provider vs holding
const LPD = expand(D.lp);
function lpPaths(f) {
  const p = D.lp.p, p0 = p[0], n = p.length, hodl = [], lp = [], reb = [], mm = [], lpf = [];
  let rb = 100, R = 100;
  for (let i = 0; i < n; i++) {
    const rel = p[i] / p0;
    hodl.push(100 * (1 + rel) / 2); lp.push(100 * Math.sqrt(rel));
    if (i > 0) { rb *= 1 + 0.5 * (p[i] / p[i - 1] - 1); R += lp[i - 1] / (2 * p[i - 1]) * (p[i] - p[i - 1]); }
    reb.push(rb); mm.push(R); lpf.push(lp[i] * Math.exp(f / 100 * (LPD.n[i] - LPD.n[0]) / 365.25));
  }
  return { hodl, lp, reb, mm, lpf };
}
function lp() {
  const k = +$('lp-t').value, f = +$('lp-f').value, P = lpPaths(f), x = LPD.s, p = D.lp.p;
  sliderV('lp-t', fd(x[k])); sliderV('lp-f', nf(f, 1) + '%');
  const cut = a => a.slice(0, k + 1), xs = cut(x);
  const tr = [
    { x: xs, y: cut(P.hodl), mode: 'lines', name: 'Hold 50% ETH + 50% USD', line: { color: K.MainBlue, width: 1.4 } },
    { x: xs, y: cut(P.reb), mode: 'lines', name: 'Constant 50/50 mix, rebalanced daily', line: { color: K.Forest, width: 1.4 } },
    { x: xs, y: cut(P.mm), mode: 'lines', name: "Rebalancing benchmark: the pool's ETH, daily", line: { color: K.Orange, width: 1.4, dash: 'dash' } },
    { x: xs, y: cut(P.lp), mode: 'lines', name: 'Liquidity provider, x*y = k, no fees', line: { color: K.IDAred, width: 1.8 } }];
  if (f > 0) tr.push({ x: xs, y: cut(P.lpf), mode: 'lines', name: `Liquidity provider with fees of ${f}% a year`, line: { color: K.IDAred, width: 1.4, dash: 'dot' } });
  tr.forEach(t => (t.hovertemplate = '%{x|%d %b %Y}: %{y:.1f}<extra></extra>'));
  plot('lp-chart', tr, layout({ xaxis: AX('', { type: 'date', range: [x[0], x[x.length - 1]] }), yaxis: AX('Value (100 at start)', { range: [Math.min(...P.lp, ...P.hodl) - 5, Math.max(...P.mm, ...P.reb, ...P.lpf) + 5] }) }));
  const rel = p[k] / p[0], il = 2 * Math.sqrt(rel) / (1 + rel) - 1, rr = range(0.05, 5, 0.025);
  plot('lp-il', [
    { x: rr, y: rr.map(r => 100 * (2 * Math.sqrt(r) / (1 + r) - 1)), mode: 'lines', name: 'Impermanent loss (%)', line: { color: K.Purple, width: 2 }, hovertemplate: 'r = %{x:.2f}: %{y:.2f}%<extra></extra>' },
    { x: [rel], y: [100 * il], mode: 'markers', name: 'Ether price ratio on ' + x[k], marker: { color: K.IDAred, size: 11, line: { color: '#fff', width: 2 } }, hovertemplate: 'r = %{x:.3f}: %{y:.2f}%<extra></extra>' }
  ], layout({ shapes: [vline(1, K.Navy, 'dash')], xaxis: AX('Price ratio r = P1 / P0', { range: [0, 5] }), yaxis: AX('LP value vs holding (%)', { range: [-58, 3], dtick: 10 }) }));
  // realised LVR up to day k, annualised, and sigma^2 / 8 on the same days
  let lvr = 0; const lr = [];
  for (let i = 1; i <= k; i++) { lvr += ((P.mm[i] - P.mm[i - 1]) - (P.lp[i] - P.lp[i - 1])) / P.lp[i - 1]; lr.push(Math.log(p[i] / p[i - 1])); }
  const yrs = (LPD.n[k] - LPD.n[0]) / 365.25, s2 = lr.length > 2 ? sdev(lr) ** 2 * 365 : NaN;
  out('lp-out', [T.lp(fd(x[k]), fint(p[k]), nf(rel, 2), nf(100 * il, 2), nf(P.hodl[k], 1), nf(P.lp[k], 1), nf(P.mm[k], 1), nf(P.reb[k], 1)),
    k > 30 ? T.lp2(nf(100 * lvr / yrs, 2), nf(100 * s2 / 8, 2), nf(100 * Math.sqrt(s2), 1)) : T.lp0,
    ...(f > 0 ? [T.lp3(nf(f, 1), nf(P.lpf[k], 1), nf(P.mm[k], 1))] : [])]);
}

// ================================================================= 10. ETF tracking
function etfTrack() {
  const e = $('et-p').value, E = D.etf[e], c = E.coin, n = E.dates.length;
  setMax('et-t', n - 1); if (+$('et-t').value > n - 1) $('et-t').value = n - 1;
  const k = +$('et-t').value; sliderV('et-t', fd(E.dates[k]));
  const xs = E.dates.slice(0, k + 1), a = E.coin_p.slice(0, k + 1).map(v => 100 * v / E.coin_p[0]), b = E.etf_p.slice(0, k + 1).map(v => 100 * v / E.etf_p[0]);
  plot('et-chart', [
    { x: xs, y: a, mode: 'lines', name: NAME[c] + ' (on ETF trading days)', line: { color: K.Orange, width: 1.6 }, hovertemplate: '%{x|%d %b %Y}: %{y:.1f}<extra>' + c + '</extra>' },
    { x: xs, y: b, mode: 'lines', name: e + (e === 'IBIT' ? ' (spot Bitcoin ETF)' : ' (spot Ether ETF)'), line: { color: COL[e], width: 1.4, dash: 'dash' }, hovertemplate: '%{x|%d %b %Y}: %{y:.1f}<extra>' + e + '</extra>' }
  ], layout({ xaxis: AX('', { type: 'date', range: [E.dates[0], E.dates[n - 1]] }), yaxis: AX('Level (100 on ' + fdEN(E.dates[0]) + ')') }));
  // drift of log(ETF / coin) against time in years, fitted on the days shown
  const t = xs.map(s => (dnum(s) - dnum(E.dates[0])) / 365.25), lr = xs.map((_, i) => Math.log(E.etf_p[i] / E.coin_p[i]));
  const dr = k > 20 ? ols(lr, t).b : NaN;
  out('et-out', [T.et(fd(E.dates[k]), e, nf(b[k], 1), NAME[c], nf(a[k], 1), nf(100 * (Math.log(b[k] / a[k])), 2)),
    k > 20 ? T.et2(nf(100 * dr, 2), nf(E.ref.drift, 2)) : T.et0]);
}
const fdEN = s => { const [y, m, d] = s.split('-'); return `${+d} ${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][+m - 1]} ${y}`; };

// ================================================================= 11. daily vs weekly returns
function etfTiming() {
  const e = $('tm-p').value, E = D.etf[e], h = +$('tm-h').value, c = E.coin;
  sliderV('tm-h', h === 1 ? T.h1 : h + ' ' + T.tdays);
  const re = E.etf_p.slice(1).map((v, i) => Math.log(v / E.etf_p[i])), rc = E.coin_p.slice(1).map((v, i) => Math.log(v / E.coin_p[i]));
  const ae = [], ac = [];
  for (let i = 0; i + h <= re.length; i += h) { ae.push(100 * sum(re.slice(i, i + h))); ac.push(100 * sum(rc.slice(i, i + h))); }
  const we = E.w_etf.map(v => 100 * v), wc = E.w_coin.map(v => 100 * v);
  const panel = (id, x, y, title) => {
    const R = ols(y, x), lim = [Math.min(...x, ...y), Math.max(...x, ...y)];
    plot(id, [
      { x, y, mode: 'markers', name: 'Observations', marker: { color: rgba(K.MainBlue, 0.55), size: 5 }, hovertemplate: NAME[c] + ' %{x:.2f}%<br>' + e + ' %{y:.2f}%<extra></extra>' },
      { x: lim, y: lim, mode: 'lines', name: '45-degree line', line: { color: K.Navy, width: 1, dash: 'dash' }, hoverinfo: 'skip' },
      { x: lim, y: lim.map(v => R.a + R.b * v), mode: 'lines', name: 'OLS fit', line: { color: K.IDAred, width: 2 }, hoverinfo: 'skip' }
    ], layout({ title: ttl(title), xaxis: AX(NAME[c]), yaxis: AX(e) }));
    return R;
  };
  const Rd = panel('tm-d', ac, ae, h === 1 ? 'Daily returns (%)' : `${h}-day returns, non-overlapping (%)`), Rw = panel('tm-w', wc, we, 'Weekly returns, Friday to Friday (%)');
  out('tm-out', [T.tm(e, h, ae.length, nf(Rd.b, 2), nf(Rd.r2, 2), we.length, nf(Rw.b, 2), nf(Rw.r2, 2))]);
}

// ================================================================= 12. asset-class map
function jacobi(A) {                    // eigenvalues and eigenvectors (columns of V) of a symmetric matrix, decreasing order
  const n = A.length, M = A.map(r => [...r]), V = A.map((_, i) => A.map((_, j) => (i === j ? 1 : 0)));
  for (let sweep = 0; sweep < 100; sweep++) {
    let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += M[i][j] ** 2;
    if (off < 1e-22) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      if (Math.abs(M[p][q]) < 1e-15) continue;
      const th = (M[q][q] - M[p][p]) / (2 * M[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < n; k++) { const a = M[k][p], b = M[k][q]; M[k][p] = c * a - s * b; M[k][q] = s * a + c * b; }
      for (let k = 0; k < n; k++) { const a = M[p][k], b = M[q][k]; M[p][k] = c * a - s * b; M[q][k] = s * a + c * b; }
      for (let k = 0; k < n; k++) { const a = V[k][p], b = V[k][q]; V[k][p] = c * a - s * b; V[k][q] = s * a + c * b; }
    }
  }
  const idx = M.map((_, i) => i).sort((a, b) => M[b][b] - M[a][a]);
  return { val: idx.map(i => M[i][i]), vec: idx.map(i => V.map(r => r[i])) };
}
function altPCA(drop) {
  const A = D.alt, F = A.features.map((_, j) => j).filter(j => j !== drop - 1), N = A.X.length;
  const X = A.X.map(r => F.map(j => r[j])), m = F.map((_, j) => mean(X.map(r => r[j]))), s = F.map((_, j) => Math.sqrt(mean(X.map(r => (r[j] - m[j]) ** 2))));
  const Z = X.map(r => r.map((v, j) => (v - m[j]) / s[j])), p = F.length;
  const S = F.map((_, a) => F.map((_, b) => sum(Z.map(r => r[a] * r[b]))));
  const E = jacobi(S), tot = sum(E.val), v = [E.vec[0], E.vec[1]];
  for (let c = 0; c < 2; c++) { const ref = F.map(j => A.V[c][j]); if (sum(ref.map((x, i) => x * v[c][i])) < 0) v[c] = v[c].map(x => -x); }
  const pc = Z.map(r => [sum(r.map((x, i) => x * v[0][i])), sum(r.map((x, i) => x * v[1][i]))]);
  const ia = F.indexOf(0);
  if (ia >= 0 && corr(pc.map(q => q[0]), A.X.map(r => r[0])) < 0) pc.forEach(q => (q[0] = -q[0]));     // PC1 increases with volatility, as on the slide
  const dist = w => {
    const g = A.cls.map((c, i) => i).filter(i => A.window[i] === w), cen = c => { const ii = g.filter(i => A.cls[i] === c); return F.map((_, j) => mean(ii.map(i => Z[i][j]))); };
    const d = (a, b) => Math.sqrt(sum(a.map((x, i) => (x - b[i]) ** 2))), cc = cen('Crypto'), cr = g.filter(i => A.cls[i] === 'Crypto');
    return { eq: d(cc, cen('Equity')), com: d(cc, cen('Commodity')), spread: mean(cr.map(i => d(Z[i], cc))) };
  };
  return { pc, ev: [E.val[0] / tot, E.val[1] / tot], d1: dist('W1'), d2: dist('W2') };
}
function altAssets() {
  const k = +$('aa-k').value, A = D.alt, P = altPCA(k);
  sliderV('aa-k', k === 0 ? T.feat0 : T.feat[k - 1]);
  const tr = [];
  for (const [cls, c] of Object.entries(CLASS_COL)) for (const w of ['W1', 'W2']) {
    const ii = A.cls.map((_, i) => i).filter(i => A.cls[i] === cls && A.window[i] === w);
    tr.push({ x: ii.map(i => P.pc[i][0]), y: ii.map(i => P.pc[i][1]), text: ii.map(i => A.label[i]), mode: 'markers', name: `${cls}, ` + (w === 'W1' ? '2019 - Jun 2021' : 'Jan 2024 - Sep 2026'),
      marker: { size: 9, color: w === 'W1' ? 'rgba(0,0,0,0)' : c, line: { color: c, width: 1.6 } }, hovertemplate: '%{text}<br>PC1 %{x:.2f}, PC2 %{y:.2f}<extra>' + w + '</extra>' });
  }
  const at = (s, w) => A.symbol.findIndex((x, i) => x === s && A.window[i] === w), ann = [];
  for (const s of [...new Set(A.symbol.filter((_, i) => A.cls[i] === 'Crypto'))]) {
    const a = P.pc[at(s, 'W1')], b = P.pc[at(s, 'W2')];
    ann.push({ x: b[0], y: b[1], ax: a[0], ay: a[1], xref: 'x', yref: 'y', axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowsize: 1, arrowwidth: 1, arrowcolor: rgba(K.Orange, 0.8), text: '' });
  }
  for (const [s, w, lab, xs, ys] of [['BTC-USD.CC', 'W1', 'Bitcoin (2019-21)', 'left', 'top'], ['BTC-USD.CC', 'W2', 'Bitcoin', 'right', 'top'], ['GSPC.INDX', 'W2', 'S&P 500', 'left', 'bottom'], ['XAUUSD.FOREX', 'W2', 'Gold', 'left', 'bottom']]) {
    const q = P.pc[at(s, w)];
    ann.push({ x: q[0], y: q[1], text: lab, showarrow: false, xanchor: xs, yanchor: ys, xshift: xs === 'left' ? 6 : -6, font: { size: 11, color: K.Navy } });
  }
  plot('aa-chart', tr, layout({ annotations: ann, legend: Object.assign(layout().legend, { y: -0.17 }), margin: { l: 56, r: 12, t: 20, b: 40 },
    xaxis: AX(`PC1 (${nf(100 * P.ev[0], 0)}% of variance)`, { zerolinecolor: K.Navy }), yaxis: AX(`PC2 (${nf(100 * P.ev[1], 0)}% of variance)`, { zerolinecolor: K.Navy }) }));
  out('aa-out', [T.aa(nf(100 * P.ev[0], 0), nf(100 * P.ev[1], 0)), T.aa2(nf(P.d1.eq, 2), nf(P.d2.eq, 2), nf(P.d1.com, 2), nf(P.d2.com, 2), nf(P.d1.spread, 2), nf(P.d2.spread, 2))]);
}

// ================================================================= 13. Liu, Tsyvinski & Wu (2022), Table 1
const LTW = ['BTC', 'XRP', 'ETH'], LTW_NAME = { BTC: 'Bitcoin', XRP: 'XRP', ETH: 'Ether' };
const LT_M = (() => { const a = []; for (let y = 2018; y <= 2025; y++) for (let m = 1; m <= 12; m++) a.push(`${y}-${String(m).padStart(2, '0')}`); return a; })();
function ltw() {
  const k = +$('lt-e').value, ym = LT_M[k], cut = monthEnd(ym);
  sliderV('lt-e', fm(ym));
  const st = Object.fromEntries(LTW.map(c => { const L = D.ltw[c], a = L.r.filter((_, i) => L.dates[i] <= cut), b = L.r.filter((_, i) => L.dates[i] > cut);
    return [c, { ins: [100 * mean(a), 100 * sdev(a), a.length], oos: [100 * mean(b), 100 * sdev(b), b.length], first: L.dates[0] }]; }));
  const nx = new Date(Date.UTC(+ym.slice(0, 4), +ym.slice(5), 1)).toISOString().slice(0, 7);
  const isPaper = ym === D.ltw_end.slice(0, 7);
  const insLab = `Our sample (daily closes), ${isPaper ? 'same weeks' : 'weeks'} (2014 - ${fdEN(ym + '-01').slice(2)})`, oosLab = `Our sample (daily closes), out of sample (${fdEN(nx + '-01').slice(2)} - Sep 2026)`;
  const tr = [];
  [['mean', 0, 'x', 'y'], ['sd', 1, 'x2', 'y2']].forEach(([s, j, xa, ya], pi) => {
    const bars = [[LTW.map(c => D.ltw[c].paper[j]), K.MainBlue, 'Liu, Tsyvinski & Wu (2022), Table 1, Panel B'], [LTW.map(c => st[c].ins[j]), K.Orange, insLab], [LTW.map(c => st[c].oos[j]), K.Forest, oosLab]];
    bars.forEach(([v, col, lab]) => tr.push({ x: LTW.map(c => LTW_NAME[c]), y: v, type: 'bar', xaxis: xa, yaxis: ya, name: lab, showlegend: pi === 0, legendgroup: lab, marker: { color: col },
      text: v.map(z => z.toFixed(1)), textposition: 'outside', textfont: { size: 10, color: K.Navy }, cliponaxis: false, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' }));
  });
  plot('lt-chart', tr, layout({ barmode: 'group', bargap: 0.2, margin: { l: 40, r: 12, t: 34, b: 30 },
    annotations: [{ text: 'Mean weekly return (%)', x: 0.5, xref: 'x domain', y: 1.08, yref: 'paper', showarrow: false, font: { size: 12, color: K.Navy } },
      { text: 'Standard deviation of weekly returns (%)', x: 0.5, xref: 'x2 domain', y: 1.08, yref: 'paper', showarrow: false, font: { size: 12, color: K.Navy } }],
    xaxis: AX('', { domain: [0, 0.46] }), xaxis2: AX('', { domain: [0.54, 1], anchor: 'y2' }), yaxis: AX('', { range: [0, 1.2 * Math.max(...tr.filter(t => t.yaxis === 'y').flatMap(t => t.y))] }), yaxis2: AX('', { anchor: 'x2', range: [0, 1.2 * Math.max(...tr.filter(t => t.yaxis === 'y2').flatMap(t => t.y))] }) }));
  const E = st.ETH, tE = (E.ins[0] - D.ltw.ETH.paper[0]) / (E.ins[1] / Math.sqrt(E.ins[2]));
  out('lt-out', [T.lt(fm(ym), ...LTW.flatMap(c => [nf(st[c].ins[0], 2), nf(st[c].ins[1], 1)]), nf(tE, 2)),
    T.lt2(st.BTC.oos[2], ...LTW.flatMap(c => [nf(st[c].oos[0], 2), nf(st[c].oos[1], 1)]))]);
}

// ================================================================= 14. z scan of the Bitcoin - S&P 500 correlation
function zScan(W) {
  const P = D.corr.SPX, x = P.btc, y = P.other, n = x.length, a = cums(x), b = cums(y), aa = cums(x.map(v => v * v)), bb = cums(y.map(v => v * v)), ab = cums(x.map((v, i) => v * y[i]));
  const cr = (s, e) => { const m = e - s, sx = a[e] - a[s], sy = b[e] - b[s]; return (m * (ab[e] - ab[s]) - sx * sy) / Math.sqrt((m * (aa[e] - aa[s]) - sx * sx) * (m * (bb[e] - bb[s]) - sy * sy)); };
  const xs = [], zs = [], d = CORR.SPX.s;
  for (let i = W; i <= n - W; i++) { xs.push(d[i]); zs.push((Math.atanh(cr(i, i + W)) - Math.atanh(cr(i - W, i))) / Math.sqrt(2 / (W - 3))); }
  return { xs, zs };
}
function zscan() {
  const W = +$('az-w').value; sliderV('az-w', T.ncdays(W));
  const { xs, zs } = zScan(W), iE = xs.findIndex(s => s >= D.etf_start);
  let im = 0; zs.forEach((z, i) => { if (Math.abs(z) > Math.abs(zs[im])) im = i; });
  const zE = iE >= 0 ? zs[iE] : null, share = zE === null ? null : zs.filter(z => Math.abs(z) >= Math.abs(zE)).length / zs.length;
  plot('az-chart', [
    { x: [xs[0], xs[xs.length - 1], xs[xs.length - 1], xs[0], xs[0]], y: [-1.96, -1.96, 1.96, 1.96, -1.96], fill: 'toself', fillcolor: rgba(K.Band, 0.5), line: { width: 0 }, mode: 'lines', name: '|z| < 1.96', hoverinfo: 'skip' },
    { x: xs, y: zs, mode: 'lines', name: `z of the correlation change (${W} common days each side)`, line: { color: K.MainBlue, width: 1.4 }, hovertemplate: '%{x|%d %b %Y}: z = %{y:.2f}<extra></extra>' },
    { x: [xs[im]], y: [zs[im]], mode: 'markers', name: `Largest break: ${fdEN(xs[im])}, z = ${zs[im].toFixed(2)}`, marker: { color: K.Forest, size: 10 }, hovertemplate: '%{x|%d %b %Y}: z = %{y:.2f}<extra></extra>' }
  ], layout({ shapes: [{ type: 'line', xref: 'x', yref: 'paper', x0: D.etf_start, x1: D.etf_start, y0: 0, y1: 1, line: { color: K.IDAred, width: 2, dash: 'dash' } }, hline(0, K.Navy)],
    annotations: [{ x: D.etf_start, y: 1, yref: 'paper', text: 'Spot ETF launch, 11 Jan 2024', showarrow: false, xanchor: 'right', yanchor: 'top', font: { size: 11, color: K.IDAred } }],
    xaxis: AX('Candidate break date', { type: 'date', range: ['2016-01-01', '2026-09-30'] }), yaxis: AX('z statistic') }));
  out('az-out', [T.az(W, fd(xs[0]), fd(xs[xs.length - 1]), nf(zs[im], 2), fd(xs[im])),
    zE === null ? T.az0 : T.az2(nf(zE, 2), pct(share, 0))]);
}

// ================================================================= Pagnotta (2022): price, hashrate, halvings
const HR = D.hr, HR_COL = { '2012-11-28': K.Teal, '2016-07-09': K.Forest, '2020-05-11': K.Purple, '2024-04-20': K.IDAred };
const HR_S = (() => { const a = []; HR.months.forEach((m, i) => { if (m >= '2013-12' && m <= '2024-12') a.push(i); }); return a; })();
function olsTrend(y, x) {               // y = a + b x + c t, t in years from the first month; returns b and R^2
  const n = y.length, X = y.map((_, i) => [1, x[i], i / 12]);
  const A = [0, 1, 2].map(r => [0, 1, 2].map(c => sum(X.map(row => row[r] * row[c]))));
  const v = [0, 1, 2].map(r => sum(X.map((row, i) => row[r] * y[i])));
  const beta = window.MFMI.solve(A, v), my = mean(y);
  const e = y.map((yi, i) => yi - beta[0] - beta[1] * x[i] - beta[2] * i / 12);
  return { b: beta[1], r2: 1 - sum(e.map(u => u * u)) / sum(y.map(u => (u - my) ** 2)) };
}
function hrLevels(a, b) {               // monthly log H on log B, months a..b (YYYY-MM, inclusive)
  const y = [], x = [];
  HR.months.forEach((m, i) => { if (m >= a && m <= b) { y.push(Math.log(HR.H[i])); x.push(Math.log(HR.B[i])); } });
  const t = olsTrend(y, x), o = ols(y, x);
  return { b: t.b, b0: o.b, r20: o.r2, n: y.length };
}
function hashrate() {
  const j = HR_S[+$('hr-e').value], m = HR.months[j], nx = HR.months[j + 1], k = +$('hr-k').value;
  sliderV('hr-e', fm(m)); sliderV('hr-k', String(k));
  const x = HR.months.map(monthEnd).map(s => s.slice(0, 8) + '15');
  const shapes = HR.halvings.map(h => ({ type: 'line', xref: 'x', yref: 'paper', x0: h, x1: h, y0: 0, y1: 1, line: { color: K.Navy, width: 1, dash: 'dot' } }));
  shapes.push({ type: 'line', xref: 'x', yref: 'paper', x0: monthEnd(m), x1: monthEnd(m), y0: 0, y1: 1, line: { color: K.Navy, width: 1.6, dash: 'dash' } });
  plot('hr-lv', [
    { x, y: HR.P, mode: 'lines', name: 'Bitcoin price (USD, left axis, monthly mean)', line: { color: K.Orange, width: 1.4 }, hovertemplate: '%{x|%b %Y}: %{y:,.2f} USD<extra></extra>' },
    { x, y: HR.H.map(v => v / 1e6), mode: 'lines', yaxis: 'y2', name: 'Hashrate (EH/s, right axis, monthly mean)', line: { color: K.MainBlue, width: 1.4 }, hovertemplate: '%{x|%b %Y}: %{y:.3g} EH/s<extra></extra>' }
  ], layout({ shapes, margin: { l: 60, r: 60, t: 20, b: 30 },
    annotations: [{ x: monthEnd(m), y: 0.02, yref: 'paper', text: ' end of the first window', showarrow: false, xanchor: 'left', font: { size: 11, color: K.Navy } }],
    xaxis: AX('', { type: 'date' }), yaxis: AX('Price (USD)', { type: 'log', exponentformat: 'power' }),
    yaxis2: AX('Hashrate (EH/s)', { type: 'log', overlaying: 'y', side: 'right', exponentformat: 'power', showgrid: false }) }));
  const tr = HR.halvings.map(h => ({ x: HR.k, y: HR.H_ev[h], mode: 'lines', name: 'Hashrate, halving of ' + h.slice(0, 4), line: { color: HR_COL[h], width: 1.4 },
    hovertemplate: h.slice(0, 4) + ', day %{x}: %{y:.1f}%<extra></extra>' }));
  tr.push({ x: [HR.k[0], HR.k[HR.k.length - 1]], y: [-50, -50], mode: 'lines', name: 'Lemma 1, static benchmark: -50%', line: { color: K.Navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' });
  plot('hr-ev', tr, layout({ legend: Object.assign(layout().legend, { y: -0.3 }), margin: { l: 60, r: 12, t: 20, b: 40 }, shapes: [{ type: 'line', xref: 'x', yref: 'paper', x0: k, x1: k, y0: 0, y1: 1, line: { color: K.Navy, width: 1.4, dash: 'dot' } }, hline(0, K.Navy)],
    xaxis: AX('Days from the halving', { range: [HR.k[0], HR.k[HR.k.length - 1]] }), yaxis: AX('Change from the week before (%)') }));
  const A = hrLevels(HR.paper[0], m), B = hrLevels(nx, HR.oos[1]), i = HR.k.indexOf(k), R = HR.ref.levels;
  const hs = HR.halvings.map(h => `${h.slice(0, 4)}: ${sgn(HR.H_ev[h][i], 1)}%`).join('; '), bs = HR.halvings.map(h => `${h.slice(0, 4)}: ${sgn(HR.B_ev[h][i], 1)}%`).join('; ');
  out('hr-out', [T.hr(fm(HR.paper[0]), fm(m), A.n, nf(A.b, 2), nf(A.b0, 2), nf(A.r20, 2)),
    T.hr2(fm(nx), fm(HR.oos[1]), B.n, nf(B.b, 2), nf(B.b0, 2), nf(B.r20, 2)),
    T.hr3(nf(R.paper.eg_p, 2), nf(R.oos.eg_p, 2)),
    T.hr4(k, hs, bs)]);
}

// ================================================================= wiring
function init() {
  $('aa-chart').style.height = '470px'; $('pg-chart').style.height = '460px'; $('mv-chart').style.height = '420px';
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  const nM = D.mv.months.length;
  setMax('mv-t', nM - 1, nM - 1); on(['mv-t'], marketValue); P('mv-play', 'mv-t', range(0, nM - 1, 1), 110);
  on(['rv-w'], rollVol); P('rv-play', 'rv-w', range(30, 730, 20), 220);
  setMax('wd-s', WD_SPLITS.length - 1, WD_SPLITS.indexOf(D.etf_start)); on(['wd-s'], weekday); P('wd-play', 'wd-s', range(0, WD_SPLITS.length - 1, 1), 160);
  on(['rc-w'], rollingCorr); P('rc-play', 'rc-w', range(20, 500, 20), 260);
  setMax('cx-s', CX_M.length - 13, 0); on(['cx-s'], crix); P('cx-play', 'cx-s', range(0, CX_M.length - 13, 1), 120);
  on(['pg-c'], peg); P('pg-play', 'pg-c', range(10, 200, 5), 200);
  setMax('dp-t', D.svb.USDC.dates.length - 1, D.svb.USDC.dates.indexOf('2023-03-11')); on(['dp-t'], svb); P('dp-play', 'dp-t', range(0, D.svb.USDC.dates.length - 1, 1), 600);
  setMax('tv-s', D.tvl.months.length - 25, 0); on(['tv-s'], tvl); P('tv-play', 'tv-s', range(0, D.tvl.months.length - 25, 1), 200);
  setMax('lp-t', D.lp.p.length - 1, D.lp.p.length - 1); on(['lp-t', 'lp-f'], lp); P('lp-play', 'lp-t', steps(0, D.lp.p.length - 1, 7), 70);
  setMax('et-t', D.etf.IBIT.dates.length - 1, D.etf.IBIT.dates.length - 1); on(['et-t'], etfTrack);
  const etP = P('et-play', 'et-t', steps(0, D.etf.IBIT.dates.length - 1, 3), 50);
  $('et-p').addEventListener('input', () => { const n = D.etf[$('et-p').value].dates.length; etP.stop(); etP.values = steps(0, n - 1, 3); setMax('et-t', n - 1, n - 1); etfTrack(); });
  on(['tm-p', 'tm-h'], etfTiming); P('tm-play', 'tm-h', range(1, 10, 1), 700);
  on(['aa-k'], altAssets); P('aa-play', 'aa-k', range(0, 8, 1), 1100);
  setMax('lt-e', LT_M.length - 1, LT_M.indexOf(D.ltw_end.slice(0, 7))); on(['lt-e'], ltw); P('lt-play', 'lt-e', range(0, LT_M.length - 1, 1), 160);
  on(['az-w'], zscan); P('az-play', 'az-w', range(100, 800, 50), 500);
  setMax('hr-e', HR_S.length - 1, HR_S.indexOf(HR.months.indexOf(HR.paper[1]))); setMax('hr-k', 90, 30); on(['hr-e', 'hr-k'], hashrate); P('hr-play', 'hr-k', range(0, 90, 1), 90);
  const PFX = { 'market-value': 'mv', 'rolling-vol': 'rv', 'weekday': 'wd', 'rolling-corr': 'rc', 'crix': 'cx', 'peg': 'pg', 'svb': 'dp',
    'tvl': 'tv', 'lp': 'lp', 'etf-tracking': 'et', 'etf-timing': 'tm', 'alt-assets': 'aa', 'ltw': 'lt', 'hashrate': 'hr', 'zscan': 'az' };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) => predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  marketValue(); rollVol(); weekday(); rollingCorr(); crix(); peg(); svb(); tvl(); lp(); etfTrack(); etfTiming(); altAssets(); ltw(); hashrate(); zscan();
}
window.CH16 = { rollVolSeries, rollCorr, periodCorr, crixStats, lpPaths, altPCA, zScan, ols, jacobi, olsTrend, hrLevels };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

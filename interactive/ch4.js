// Chapter 4 interactive page: one block per chart slide, computed in the browser from ch4_data.js.
(function () {
'use strict';
const D = window.CH4_DATA;
const { C, dot, mv, quad, scale, sum, sub, solve, chol, eigSym, cov2corr, wEW, wTan, wGMV, wLOmv, wGMVLO, wTanLO, ercStep, wERC, riskContrib, frontierUnc,
  leaves, hrpLevels, rng, sampleMoments, median, mean, sharpe, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range } = window.MFMI;
const T = window.CH4_TEXT;

// ---------------------------------------------------------------- colours (same as the slides)
const SCOL = { '1/N': '#D63384', 'MV': '#CD0000', 'MV-LO': '#E67E22', 'GMV': '#B5853F', 'GMV-LO': '#8E44AD', 'GMV-LW': '#1A3A6E', 'ERC': '#2E7D32', 'HRP': '#17A2B8' };
const ASSET_COL = ['#2D5BA8', '#5B84C8', '#93AEDD', '#CD0000', '#E46A5C', '#B5853F', '#D8B27A', '#2E7D32'];

// ================================================================= two assets
function twoAsset() {
  const P = D.two, [m1, m2] = P.mu, [s1, s2] = P.sd, rho = +$('ta-rho').value, w = +$('ta-w').value;
  $('ta-rho-v').textContent = nf(rho, 2); $('ta-w-v').textContent = pct(w, 0);
  const vol = (a, r) => Math.sqrt(a * a * s1 * s1 + (1 - a) ** 2 * s2 * s2 + 2 * a * (1 - a) * r * s1 * s2);
  const curve = r => { const a = range(0, 1, 0.01); return { x: a.map(v => vol(v, r)), y: a.map(v => v * m1 + (1 - v) * m2), w: a }; };
  const c = curve(rho), c1 = curve(1);
  let g = (s2 * s2 - rho * s1 * s2) / (s1 * s1 + s2 * s2 - 2 * rho * s1 * s2); g = Math.min(Math.max(g, 0), 1);
  const ht = 'SPY %{customdata:.0%}<br>vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>';
  plot('ta-chart', [
    { x: c1.x, y: c1.y, customdata: c1.w, mode: 'lines', name: 'Correlation 1', line: { color: C.amber, width: 2, dash: 'dash' }, hovertemplate: ht },
    { x: c.x, y: c.y, customdata: c.w, mode: 'lines', name: 'Correlation ' + rho.toFixed(2), line: { color: C.blue, width: 2 }, hovertemplate: ht },
    { x: [s1, s2], y: [m1, m2], mode: 'markers+text', text: ['SPY', 'TLT'], textposition: 'top right', marker: { color: C.navy, size: 9 }, showlegend: false, hovertemplate: '%{text}<extra></extra>' },
    { x: [vol(g, rho)], y: [g * m1 + (1 - g) * m2], mode: 'markers', name: 'Minimum variance', marker: { color: C.green, size: 11, symbol: 'diamond', line: { color: '#fff', width: 2 } }, hovertemplate: 'SPY ' + (100 * g).toFixed(0) + '%<br>vol %{x:.1%}<extra></extra>' },
    { x: [vol(w, rho)], y: [w * m1 + (1 - w) * m2], mode: 'markers', name: 'Chosen weight', marker: { color: C.red, size: 12, line: { color: '#fff', width: 2 } }, hovertemplate: 'vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>' }
  ], layout({ xaxis: AX('Volatility (annualised)', { tickformat: '.0%', range: [0, 0.16] }), yaxis: AX('Mean return (annualised)', { tickformat: '.0%' }) }));
  out('ta-out', [T.ta(pct(vol(w, rho)), pct(w * m1 + (1 - w) * m2), pct(g, 0), pct(vol(g, rho)))]);
}

// ================================================================= frontier of US sectors
const FR_ORDER = ['XLK', 'XLP', 'XLE', 'XLV', 'XLF', 'XLU', 'XLI', 'XLB', 'XLY'];
const LABEL_POS = { XLF: 'bottom center', XLI: 'top left', XLY: 'top right', XLP: 'bottom center', XLU: 'bottom right', XLV: 'middle left' };
function frontier() {
  const all = D.sectors, mu12 = D.full.mu.map(x => 12 * x), S12 = scale(D.full.cov, 12), n = +$('fr-n').value;
  const names = FR_ORDER.slice(0, n), idx = names.map(s => all.indexOf(s)), mu = idx.map(i => mu12[i]), S = sub(S12, idx);
  $('fr-n-v').textContent = names.join(', ');
  const tg = range(-0.02, 0.18, 0.002), fu = frontierUnc(mu, S, tg), fAll = frontierUnc(mu12, S12, tg);
  const lo = []; let w = null;
  for (let k = 0; k <= 60; k++) { w = wLOmv(mu, S, Math.pow(10, -0.5 + 3.5 * k / 60), w); lo.push([Math.sqrt(quad(w, S)), dot(w, mu)]); }
  const gl = wGMVLO(S); lo.push([Math.sqrt(quad(gl, S)), dot(gl, mu)]); lo.sort((a, b) => a[1] - b[1]);
  const wt = wTan(mu, S), wl = wTanLO(mu, S), pt = v => [Math.sqrt(quad(v, S)), dot(v, mu)], Pt = pt(wt), Pl = pt(wl);
  const full = wv => all.map(s => { const k = names.indexOf(s); return k < 0 ? null : wv[k]; });
  plot('fr-chart', [
    { x: fAll, y: tg, mode: 'lines', name: 'Frontier, all 9 sectors', line: { color: C.band, width: 3 }, hoverinfo: 'skip' },
    { x: fu, y: tg, mode: 'lines', name: 'Frontier, short sales allowed', line: { color: C.blue, width: 2 }, hovertemplate: 'vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>' },
    { x: lo.map(p => p[0]), y: lo.map(p => p[1]), mode: 'lines', name: 'Frontier, long-only', line: { color: C.amber, width: 2 }, hovertemplate: 'vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>' },
    { x: all.map((_, i) => Math.sqrt(S12[i][i])), y: mu12, text: all, mode: 'markers+text', textposition: all.map(s => LABEL_POS[s] || 'top center'), textfont: { size: 10, color: C.navy },
      marker: { color: all.map(s => (names.includes(s) ? C.navy : '#fff')), line: { color: C.navy, width: 1.5 }, size: 8 }, showlegend: false, hovertemplate: '%{text}<br>vol %{x:.1%}<br>mean %{y:.1%}<extra></extra>' },
    { x: [Pt[0]], y: [Pt[1]], mode: 'markers', name: 'Tangency, short sales', marker: { color: C.blue, size: 13, symbol: 'star', line: { color: '#fff', width: 1.5 } }, hovertemplate: 'Sharpe ' + nf(Pt[1] / Pt[0], 2) + '<extra></extra>' },
    { x: [Pl[0]], y: [Pl[1]], mode: 'markers', name: 'Tangency, long-only', marker: { color: C.amber, size: 13, symbol: 'star', line: { color: '#fff', width: 1.5 } }, hovertemplate: 'Sharpe ' + nf(Pl[1] / Pl[0], 2) + '<extra></extra>' }
  ], layout({ xaxis: AX('Volatility (annualised)', { tickformat: '.0%', range: [0, 0.30] }), yaxis: AX('Mean excess return (annualised)', { tickformat: '.0%', range: [-0.02, 0.16] }) }));
  plot('fr-w', [
    { x: all, y: full(wt), type: 'bar', name: 'Tangency, short sales', marker: { color: C.blue, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' },
    { x: all, y: full(wl), type: 'bar', name: 'Tangency, long-only', marker: { color: C.amber, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Weights of the tangency portfolios'), xaxis: AX(''), yaxis: AX('Weight', { tickformat: '.0%', range: [-0.6, 1.05] }) }));
  out('fr-out', [T.fr(n, nf(Pt[1] / Pt[0], 2), nf(Pl[1] / Pl[0], 2), names.filter((_, k) => wt[k] < -1e-6).join(', ') || '—')]);
}

// ================================================================= estimation error
let eeSeed = 42, eeCache = null;
function eeSamples() {
  const Tm = +$('ee-T').value, key = Tm + ':' + eeSeed;
  if (eeCache && eeCache.key === key) return eeCache;
  const mu = D.full.mu, S = D.full.cov, L = chol(S), z = rng(eeSeed), n = mu.length, tg = range(-0.01, 0.06, 0.0007);
  const one = new Array(n).fill(1), fr = [], sr = [], est = [];
  const srT = w => dot(w, mu) / Math.sqrt(quad(w, S)) * Math.sqrt(12);
  for (let k = 0; k < 500; k++) {
    const { m, S: Sh } = sampleMoments(mu, L, Tm, z), w = wTan(m, Sh);
    sr.push(srT(w)); est.push(dot(w, m) / Math.sqrt(quad(w, Sh)) * Math.sqrt(12));
    if (k < 25) {
      const Si1 = solve(Sh, one), Sim = solve(Sh, m), A = sum(Si1), B = sum(Sim), Cc = dot(m, Sim), Dd = A * Cc - B * B;
      const e = frontierUnc(m, Sh, tg), rx = [], ry = [];
      for (const t of tg) { const l = (Cc - t * B) / Dd, g = (t * A - B) / Dd, wt = Si1.map((v, i) => l * v + g * Sim[i]); ry.push(12 * dot(wt, mu)); rx.push(Math.sqrt(12 * quad(wt, S))); }
      fr.push({ ex: e.map(v => v * Math.sqrt(12)), ey: tg.map(v => 12 * v), rx, ry });
    }
  }
  const tf = frontierUnc(mu, S, tg).map(v => v * Math.sqrt(12));
  eeCache = { key, fr, sr, est, tf, tg: tg.map(v => 12 * v), sr_ew: srT(wEW(n)), sr_opt: srT(wTan(mu, S)) };
  return eeCache;
}
function estimationError() {
  const E = eeSamples(), k = +$('ee-k').value;
  $('ee-k-v').textContent = k;
  const tr = [{ x: E.tf, y: E.tg, mode: 'lines', name: 'True frontier', line: { color: C.blue, width: 3 }, hoverinfo: 'skip' }];
  E.fr.slice(0, k).forEach((f, i) => {
    const last = i === k - 1;
    tr.push({ x: f.ex, y: f.ey, mode: 'lines', name: 'Estimated frontier', legendgroup: 'e', showlegend: i === 0, line: { color: C.red, width: last ? 2 : 0.8 }, opacity: last ? 1 : 0.45, hoverinfo: 'skip' });
    tr.push({ x: f.rx, y: f.ry, mode: 'lines', name: 'Realised frontier (same weights, true parameters)', legendgroup: 'r', showlegend: i === 0, line: { color: C.green, width: last ? 2 : 0.8 }, opacity: last ? 1 : 0.45, hoverinfo: 'skip' });
  });
  plot('ee-chart', tr, layout({ title: ttl($('ee-T').value + '-month samples, Normal returns'), xaxis: AX('Volatility (annualised)', { tickformat: '.0%', range: [0, 0.35] }), yaxis: AX('Mean excess return (annualised)', { tickformat: '.0%', range: [-0.12, 0.72] }) }));
  plot('ee-hist', [
    { x: E.sr, type: 'histogram', xbins: { start: -1, end: 1, size: 0.04 }, name: 'Out-of-sample Sharpe ratio, 500 samples', marker: { color: C.blue, line: { color: '#fff', width: 1 } }, hovertemplate: 'Sharpe %{x}<br>%{y} samples<extra></extra>' }
  ], layout({ bargap: 0, showlegend: false, title: ttl('Tangency portfolio: Sharpe ratio with the true parameters'), shapes: [vline(E.sr_ew, SCOL['1/N']), vline(E.sr_opt, C.green, 'dash')],
    annotations: [{ x: E.sr_ew, y: 1, yref: 'paper', text: '1/N', showarrow: false, xanchor: 'right', font: { color: SCOL['1/N'] } }, { x: E.sr_opt, y: 1, yref: 'paper', text: 'optimum', showarrow: false, xanchor: 'left', font: { color: C.green } }],
    xaxis: AX('Annualised Sharpe ratio', { range: [-0.6, 0.8] }), yaxis: AX('Number of samples') }));
  out('ee-out', [T.ee(nf(median(E.est), 2), nf(median(E.sr), 2), pct(E.sr.filter(x => x < E.sr_ew).length / 500, 0), nf(E.sr_ew, 2))]);
}

// ================================================================= unstable weights
function rolling() {
  const R = D.rolling, k = +$('rw-t').value, S = D.sectors;
  $('rw-t-v').textContent = R.dates[k];
  const gross = A => A.map(w => sum(w.map(Math.abs)));
  plot('rw-w', [
    { x: S, y: R.MV[k], type: 'bar', name: 'MV', marker: { color: SCOL.MV, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.0%}<extra></extra>' },
    { x: S, y: R.GMV_LW[k], type: 'bar', name: 'GMV-LW', marker: { color: SCOL['GMV-LW'], line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.0%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Weights estimated on the 60 months before ' + R.dates[k]), xaxis: AX(''), yaxis: AX('Weight', { tickformat: '.0%', range: [-3, 3] }) }));
  plot('rw-g', [
    { x: R.dates, y: gross(R.MV), mode: 'lines', name: 'MV', line: { color: SCOL.MV, width: 1.5 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' },
    { x: R.dates, y: gross(R.GMV_LW), mode: 'lines', name: 'GMV-LW', line: { color: SCOL['GMV-LW'], width: 2 }, hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }
  ], layout({ title: ttl('Gross exposure: sum of |weights|'), shapes: [vline(R.dates[k], C.navy, 'dot')], xaxis: AX('', { type: 'category', nticks: 8 }), yaxis: AX('Sum of |w| (log scale)', { type: 'log' }) }));
  out('rw-out', [T.rw(R.dates[k], nf(sum(R.MV[k].map(Math.abs)), 1), nf(sum(R.GMV_LW[k].map(Math.abs)), 1))]);
}

// ================================================================= window length
const wlCache = {};
function windowLength() {
  const W = D.window, Ts = W.Ts, k = +$('wl-t').value, Tm = Ts[k];
  $('wl-t-v').textContent = Tm;
  if (!wlCache[Tm]) {
    const mu = D.full.mu, S = D.full.cov, L = chol(S), z = rng(7 + Tm), srT = w => dot(w, mu) / Math.sqrt(quad(w, S)) * Math.sqrt(12), a = [];
    for (let s = 0; s < 150; s++) { const { m, S: Sh } = sampleMoments(mu, L, Tm, z); a.push(srT(wTan(m, Sh))); }
    wlCache[Tm] = a;
  }
  const rules = ['MV', 'MV-LO', 'GMV', 'GMV-LW', 'ERC'];
  plot('wl-chart', rules.map(r => ({ x: Ts, y: Ts.map(t => W.median_true_sr[r][t]), mode: 'lines+markers', name: r, line: { color: SCOL[r], width: 2 }, marker: { size: 6 }, hovertemplate: r + ', T = %{x}: %{y:.2f}<extra></extra>' })),
    layout({ title: ttl('Median out-of-sample Sharpe ratio, 300 samples per T'), shapes: [vline(Tm, C.navy, 'dot'), hline(W.sr_ew, SCOL['1/N'], 'dash')],
      annotations: [{ xref: 'paper', x: 0, y: W.sr_ew, text: '1/N', showarrow: false, yanchor: 'bottom', xanchor: 'left', font: { color: SCOL['1/N'] } }],
      xaxis: AX('Estimation window T (months, log scale)', { type: 'log', tickvals: Ts }), yaxis: AX('Sharpe ratio', { range: [0.2, 0.7] }) }));
  plot('wl-hist', [{ x: wlCache[Tm], type: 'histogram', xbins: { start: -1, end: 1, size: 0.03 }, name: 'MV', marker: { color: SCOL.MV, line: { color: '#fff', width: 1 } }, hovertemplate: '%{x}: %{y}<extra></extra>' }],
    layout({ bargap: 0, showlegend: false, title: ttl('MV, T = ' + Tm + ': Sharpe ratio of 150 simulated samples'), shapes: [vline(W.sr_ew, SCOL['1/N']), vline(W.sr_opt, C.green, 'dash')], xaxis: AX('Sharpe ratio', { range: [-0.4, 0.8] }), yaxis: AX('Samples') }));
  out('wl-out', [T.wl(Tm, nf(W.median_true_sr.MV[Tm], 2), nf(W.sr_ew, 2), W.mv_beats_ew_at)]);
}

// ================================================================= eigenvalues and the noise band
function mpBand() {
  const src = $('mp-src').value, Tm = +$('mp-T').value;
  $('mp-T-v').textContent = Tm; $('mp-T').disabled = src !== 'noise';
  let ev, N, Tt;
  if (src === 'noise') {
    N = 16; Tt = Tm; const z = rng(11 + Tm), X = [];
    for (let t = 0; t < Tt; t++) X.push(Array.from({ length: N }, z));
    const m = new Array(N).fill(0); X.forEach(x => x.forEach((v, i) => (m[i] += v / Tt)));
    const S = m.map(() => new Array(N).fill(0)); X.forEach(x => { for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) S[i][j] += (x[i] - m[i]) * (x[j] - m[j]); });
    ev = eigSym(cov2corr(S));
  } else { const M = D.mp[src]; ev = M.ev; N = M.N; Tt = M.T; }
  const c = N / Tt, lo = (1 - Math.sqrt(c)) ** 2, hi = (1 + Math.sqrt(c)) ** 2, k = ev.map((_, i) => i + 1), inn = ev.map(v => v >= lo && v <= hi);
  plot('mp-chart', [
    { x: k.filter((_, i) => inn[i]), y: ev.filter((_, i) => inn[i]), mode: 'markers', name: 'Inside the band', marker: { color: C.blue, size: 9 }, hovertemplate: 'rank %{x}: %{y:.2f}<extra></extra>' },
    { x: k.filter((_, i) => !inn[i]), y: ev.filter((_, i) => !inn[i]), mode: 'markers', name: 'Outside the band', marker: { color: C.red, size: 10, symbol: 'diamond' }, hovertemplate: 'rank %{x}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl(`N = ${N}, T = ${Tt}, c = N/T = ${c.toFixed(2)}`),
    shapes: [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: lo, y1: hi, fillcolor: C.band, opacity: 0.5, line: { width: 0 }, layer: 'below' }],
    annotations: [{ xref: 'paper', x: 1, y: Math.log10(hi), text: 'Marchenko–Pastur band', showarrow: false, xanchor: 'right', yanchor: 'bottom', font: { size: 11 } }],
    xaxis: AX('Eigenvalue rank', { dtick: N > 9 ? 3 : 1 }), yaxis: AX('Eigenvalue of the correlation matrix (log)', { type: 'log', range: [-1.6, 1.1] }) }));
  out('mp-out', [T.mp(ev.filter(v => v > hi).length, N, nf(lo, 2), nf(hi, 2))]);
}

// ================================================================= shrinkage
function shrinkage() {
  const H = D.shrink, d = +$('sh-d').value, S = H.S60.map((r, i) => r.map((v, j) => (1 - d) * v + d * H.F60[i][j]));
  $('sh-d-v').textContent = nf(d, 2);
  const ev = eigSym(S), k = ev.map((_, i) => i + 1), w = wGMV(S), cond = ev[0] / ev[ev.length - 1];
  plot('sh-ev', [
    { x: k, y: H.ev_sample, mode: 'lines+markers', name: 'Sample, last 60 months', line: { color: C.red, width: 1.5, dash: 'dot' }, marker: { size: 6 }, hovertemplate: '%{y:.4f}<extra></extra>' },
    { x: k, y: H.ev_full, mode: 'lines+markers', name: 'Sample, all months', line: { color: C.green, width: 1.5, dash: 'dash' }, marker: { size: 6, symbol: 'triangle-up' }, hovertemplate: '%{y:.4f}<extra></extra>' },
    { x: k, y: ev, mode: 'lines+markers', name: 'Shrunk, δ = ' + d.toFixed(2), line: { color: C.blue, width: 2.5 }, marker: { size: 8, symbol: 'square' }, hovertemplate: '%{y:.4f}<extra></extra>' }
  ], layout({ title: ttl('Eigenvalues'), xaxis: AX('Eigenvalue rank', { dtick: 1 }), yaxis: AX('Eigenvalue (annualised, log)', { type: 'log' }) }));
  plot('sh-w', [{ x: D.sectors, y: w, type: 'bar', name: 'GMV', marker: { color: C.blue, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }],
    layout({ title: ttl('GMV weights with the shrunk covariance'), showlegend: false, xaxis: AX(''), yaxis: AX('Weight', { tickformat: '.0%', range: [-0.6, 1.0] }) }));
  plot('sh-roll', [{ x: H.dates, y: H.delta, mode: 'lines', name: 'δ', line: { color: C.blue, width: 2 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' }],
    layout({ title: ttl('Ledoit–Wolf δ, rolling 60-month window'), showlegend: false, shapes: [hline(d, C.red, 'dot')], xaxis: AX('', { type: 'category', nticks: 8 }), yaxis: AX('δ', { range: [0, 1] }) }));
  out('sh-out', [T.sh(nf(d, 2), nf(cond, 0), pct(Math.max(...w.map(Math.abs)), 0), nf(H.delta_lw, 2))]);
}

// ================================================================= Black-Litterman
function blackLitterman() {
  const B = D.bl, S = B.cov_ann, n = S.length, names = D.sectors, tau = B.tau, del = B.delta;
  const q = +$('bl-q').value / 100, c = Math.pow(10, +$('bl-c').value);
  $('bl-q-v').textContent = pct(q, 1); $('bl-c-v').textContent = '× ' + nf(c, c < 1 ? 2 : c < 10 ? 1 : 0);
  const wb = wEW(n), pi = mv(scale(S, del), wb), P = new Array(n).fill(0); P[names.indexOf('XLK')] = 1; P[names.indexOf('XLU')] = -1;
  const tS = scale(S, tau), om = c * quad(P, tS), kk = (q - dot(P, pi)) / (quad(P, tS) + om), tSP = mv(tS, P);
  const mu = pi.map((v, i) => v + tSP[i] * kk), w = solve(scale(S, del), mu);
  plot('bl-mu', [
    { x: names, y: pi, type: 'bar', name: 'Prior (implied by 1/N)', marker: { color: C.amber, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.2%}<extra></extra>' },
    { x: names, y: mu, type: 'bar', name: 'Posterior', marker: { color: C.blue, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.2%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Expected excess returns'), xaxis: AX(''), yaxis: AX('Annualised', { tickformat: '.0%', range: [0, 0.10] }) }));
  plot('bl-w', [
    { x: names, y: wb, type: 'bar', name: 'Benchmark 1/N', marker: { color: C.amber, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' },
    { x: names, y: w, type: 'bar', name: 'Black–Litterman', marker: { color: C.blue, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Portfolio weights'), xaxis: AX(''), yaxis: AX('Weight', { tickformat: '.0%', range: [-0.1, 0.4] }) }));
  const iK = names.indexOf('XLK'), iU = names.indexOf('XLU');
  out('bl-out', [T.bl(pct(dot(P, pi)), pct(q), pct(dot(P, mu)), pct(w[iK] - wb[iK]), pct(w[iU] - wb[iU]))]);
}

// ================================================================= risk contributions
let rcW = null;
function riskContribs() {
  const M = D.multi, S = M.cov_ann, A = D.multi_assets, k = +$('rc-k').value;
  $('rc-k-v').textContent = k;
  if (!rcW) { rcW = [wEW(A.length)]; for (let i = 0; i < 30; i++) rcW.push(ercStep(rcW[rcW.length - 1], S)); }
  const w = rcW[k], rc = riskContrib(w, S), iH = A.indexOf('HYG');
  plot('rc-it', [
    { x: A, y: w, type: 'bar', name: 'Weight', marker: { color: C.amber, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' },
    { x: A, y: rc, type: 'bar', name: 'Risk contribution', marker: { color: C.blue, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl(k === 0 ? '1/N (iteration 0)' : 'Iteration ' + k + ' of the ERC algorithm'),
    shapes: [hline(1 / A.length, C.navy, 'dot')], xaxis: AX(''), yaxis: AX('Share', { tickformat: '.0%', range: [0, 0.3] }) }));
  const W = { '1/N': wEW(A.length), 'GMV-LO': wGMVLO(S), 'ERC': wERC(S), 'HRP': M.hrp }, keys = Object.keys(W);
  const tr = (what, show, ax) => A.map((a, i) => ({ x: keys, y: keys.map(s => (what === 'w' ? W[s][i] : riskContrib(W[s], S)[i])), type: 'bar', name: a, legendgroup: a, showlegend: show, xaxis: ax[0], yaxis: ax[1],
    marker: { color: ASSET_COL[i], line: { color: '#fff', width: 1.5 } }, hovertemplate: a + ', %{x}: %{y:.1%}<extra></extra>' }));
  plot('rc-st', [...tr('w', false, ['x', 'y']), ...tr('rc', true, ['x2', 'y2'])],
    layout({ barmode: 'stack', bargap: 0.35, grid: { rows: 1, columns: 2, pattern: 'independent' },
      annotations: [{ text: 'Weights', xref: 'x domain', yref: 'paper', x: 0, y: 1.1, showarrow: false, xanchor: 'left' }, { text: 'Risk contributions', xref: 'x2 domain', yref: 'paper', x: 0, y: 1.1, showarrow: false, xanchor: 'left' }],
      xaxis: AX(''), yaxis: AX('Share', { tickformat: '.0%', range: [0, 1] }), xaxis2: AX(''), yaxis2: AX('', { tickformat: '.0%', range: [0, 1] }) }));
  out('rc-out', [T.rc(k, pct(w[0] + w[1] + w[2] + w[iH], 0), pct(rc[0] + rc[1] + rc[2] + rc[iH], 0))]);
}

// ================================================================= HRP
let hrpPre = null;
function hrp() {
  const H = D.hrp, A = D.combined, n = A.length;
  if (!hrpPre) { const order = leaves(H.Z, n); hrpPre = { order, levels: hrpLevels(H.cov_ann, order), R: cov2corr(H.cov_ann) }; $('hrp-s').max = 2 + hrpPre.levels.length; }
  const { order, levels, R } = hrpPre, steps = 2 + levels.length, st = Math.min(+$('hrp-s').value, steps);
  $('hrp-s-v').textContent = st + ' / ' + steps;
  const ord = st === 1 ? A.map((_, i) => i) : order, lab = ord.map(i => A[i]);
  plot('hrp-heat', [{ z: ord.map(i => ord.map(j => R[i][j])), x: lab, y: lab, type: 'heatmap', zmin: -0.6, zmax: 1, colorscale: [[0, '#B03A2E'], [0.375, '#F4F4F2'], [1, '#1A3A6E']], colorbar: { title: { text: 'ρ' }, thickness: 12 }, hovertemplate: '%{y} – %{x}: %{z:.2f}<extra></extra>' }],
    layout({ title: ttl(st === 1 ? 'Correlations, original order' : 'Correlations, order of the tree leaves'), xaxis: AX('', { tickangle: -60, tickfont: { size: 9 } }), yaxis: AX('', { autorange: 'reversed', tickfont: { size: 9 } }) }));
  const L = st >= 3 ? levels[st - 3] : null, wv = L ? order.map(i => L.w[i]) : order.map(() => 1 / n);
  plot('hrp-w', [
    { x: order.map(i => A[i]), y: wv, type: 'bar', name: L ? 'HRP after ' + (st - 2) + ' bisection level(s)' : 'Before the bisection', marker: { color: SCOL.HRP, line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' },
    { x: order.map(i => A[i]), y: order.map(i => H.w_gmv_lo[i]), type: 'bar', name: 'GMV long-only', visible: st === steps ? true : 'legendonly', marker: { color: SCOL['GMV-LO'], line: { color: '#fff', width: 2 } }, hovertemplate: '%{x}: %{y:.1%}<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.25, title: ttl('Weights, in the order of the tree leaves'), xaxis: AX('', { tickangle: -60, tickfont: { size: 9 } }), yaxis: AX('Weight', { tickformat: '.0%', range: [0, 0.75] }) }));
  out('hrp-out', [st === 1 ? T.hrp1 : st === 2 ? T.hrp2 : T.hrp3(st - 2, L.clusters.length, pct(Math.max(...L.w), 0))]);
}

// ================================================================= out-of-sample growth
function wealthPath(ret, rf, to, cbp, upto) {
  let w = 1, alive = true; const y = [];
  for (let t = 0; t <= upto; t++) {
    const tot = ret[t] - cbp / 1e4 * to[t] + rf[t];
    if (alive && tot <= -1) alive = false;
    w = alive ? w * (1 + tot) / (1 + rf[t]) : NaN; y.push(w);
  }
  return y;
}
function oosCum() {
  const u = $('ow-u').value, O = D.oos[u], c = +$('ow-c').value, last = O.dates.length - 1;
  $('ow-t').max = last; if (+$('ow-t').value > last) $('ow-t').value = last;
  const k = +$('ow-t').value; $('ow-c-v').textContent = c + ' bp'; $('ow-t-v').textContent = O.dates[k];
  plot('ow-chart', D.strategies.map(s => ({ x: O.dates.slice(0, k + 1), y: wealthPath(O.ret[s], O.rf, O.turnover[s], c, k), mode: 'lines', name: s,
    line: { color: SCOL[s], width: ['1/N', 'GMV-LW', 'ERC', 'HRP'].includes(s) ? 2.2 : 1.2 }, hovertemplate: s + ' %{x}: %{y:.2f}<extra></extra>' })),
    layout({ title: ttl(u + ': wealth relative to T-bills, 60-month window, monthly rebalancing'), xaxis: AX('', { type: 'category', nticks: 8, range: [-0.5, last + 0.5] }), yaxis: AX('Wealth (log scale)', { type: 'log' }) }));
  const sr = D.strategies.map(s => sharpe(O.ret[s].slice(0, k + 1).map((r, t) => r - c / 1e4 * O.turnover[s][t]))), best = D.strategies[sr.indexOf(Math.max(...sr))];
  out('ow-out', [T.ow(O.dates[k], c, best, nf(Math.max(...sr), 2), nf(sr[0], 2))]);
}

// ================================================================= Sharpe ratios across universes
function oosSharpe() {
  const k = +$('os-y').value, U = Object.keys(D.oos), cols = [C.blue, C.green, C.amber];
  const y0 = String(+D.oos.Sectors.dates[0].slice(0, 4) + k);
  $('os-y-v').textContent = y0;
  const first = O => Math.max(0, O.dates.findIndex(d => d >= y0));
  plot('os-chart', U.map((u, j) => {
    const O = D.oos[u], i0 = first(O);
    return { x: D.strategies, y: D.strategies.map(s => sharpe(O.ret[s].slice(i0))), type: 'bar', name: `${u} (${O.dates[i0]} – ${O.dates[O.dates.length - 1]})`, marker: { color: cols[j], line: { color: '#fff', width: 2 } }, hovertemplate: u + ', %{x}: %{y:.2f}<extra></extra>' };
  }), layout({ barmode: 'group', bargap: 0.2, title: ttl('Out-of-sample Sharpe ratios before costs, evaluation from ' + y0), xaxis: AX(''), yaxis: AX('Sharpe ratio (annualised)', { range: [-0.6, 1.2] }) }));
  const O = D.oos.Sectors, i0 = first(O);
  out('os-out', [T.os(y0, nf(sharpe(O.ret['1/N'].slice(i0)), 2), nf(sharpe(O.ret.MV.slice(i0)), 2))]);
}

// ================================================================= Sharpe ratios after costs
function costs() {
  const u = $('co-u').value, O = D.oos[u], c = +$('co-c').value, cs = range(0, 100, 5);
  $('co-c-v').textContent = c + ' bp';
  const net = (s, cc) => sharpe(O.ret[s].map((r, t) => r - cc / 1e4 * O.turnover[s][t]));
  plot('co-chart', D.strategies.map(s => ({ x: cs, y: cs.map(cc => net(s, cc)), mode: 'lines', name: s, line: { color: SCOL[s], width: 2 }, hovertemplate: s + ', %{x} bp: %{y:.2f}<extra></extra>' })),
    layout({ title: ttl(u + ': Sharpe ratio after costs'), shapes: [vline(c, C.navy, 'dot')], xaxis: AX('Cost per unit of turnover (basis points)'), yaxis: AX('Net Sharpe ratio (annualised)') }));
  const tv = D.strategies.map(s => mean(O.turnover[s].slice(1)));
  plot('co-to', [{ y: D.strategies, x: tv, type: 'bar', orientation: 'h', marker: { color: D.strategies.map(s => SCOL[s]), line: { color: '#fff', width: 2 } }, hovertemplate: '%{y}: %{x:.3f}<extra></extra>' }],
    layout({ title: ttl('Mean monthly turnover'), showlegend: false, xaxis: AX('Turnover (log scale)', { type: 'log' }), yaxis: AX('', { autorange: 'reversed' }) }));
  const v = D.strategies.map(s => net(s, c)), best = D.strategies[v.indexOf(Math.max(...v))];
  out('co-out', [T.co(c, best, nf(Math.max(...v), 2), nf(net('MV', c), 2), nf(v[0], 2))]);
}

// ================================================================= Sharpe difference test (block bootstrap)
let stDraws = [], stKey = '';
function sharpeTest() {
  const [u, s] = $('st-p').value.split('|'), O = D.oos[u], R = D.tests[u][s], b = R.block, M = +$('st-m').value;
  $('st-m-v').textContent = M;
  const r1 = O.ret[s], r2 = O.ret['1/N'], n = r1.length, obs = sharpe(r1) - sharpe(r2);
  if (stKey !== u + s) {
    stKey = u + s; stDraws = []; const z = rng(5);
    for (let m = 0; m < 2000; m++) {
      const a = [], c = [];
      while (a.length < n) { const st = Math.floor(z.u() * n); for (let j = 0; j < b && a.length < n; j++) { a.push(r1[(st + j) % n]); c.push(r2[(st + j) % n]); } }
      stDraws.push(sharpe(a) - sharpe(c) - obs);
    }
  }
  const d = stDraws.slice(0, M), q = [...d].sort((x, y) => x - y), lo = q[Math.floor(0.025 * (M - 1))], hi = q[Math.ceil(0.975 * (M - 1))];
  plot('st-chart', [{ x: d, type: 'histogram', xbins: { start: -1.5, end: 1.5, size: 0.04 }, name: 'Bootstrap draws', marker: { color: SCOL[s], line: { color: '#fff', width: 1 } }, hovertemplate: '%{x}: %{y}<extra></extra>' }],
    layout({ bargap: 0, showlegend: false, title: ttl(`${u}: ${s} minus 1/N, circular blocks of ${b} months, ${M} draws`), shapes: [vline(obs, C.red), vline(lo, C.navy, 'dash'), vline(hi, C.navy, 'dash')],
      annotations: [{ x: obs, y: 1, yref: 'paper', text: 'observed ' + nf(obs, 2), showarrow: false, xanchor: 'left', font: { color: C.red } }],
      xaxis: AX('Δ* − Δ (difference of annualised Sharpe ratios)', { range: [-1.2, 1.2] }), yaxis: AX('Draws') }));
  out('st-out', [T.st(nf(obs, 2), nf(lo, 2), nf(hi, 2), nf(R.p_hac, 2), nf(R.p_boot, 2))]);
}

// ================================================================= BVB
function bvb() {
  const B = D.bvb, S = B.strategies, last = B.dates.length - 1;
  $('bv-t').max = last; if (+$('bv-t').value > last) $('bv-t').value = last;
  const k = +$('bv-t').value; $('bv-t-v').textContent = B.dates[k];
  const grow = a => { let w = 1; return a.slice(0, k + 1).map(r => (w *= 1 + r)); };
  plot('bv-chart', [
    ...S.map(s => ({ x: B.dates.slice(0, k + 1), y: grow(B.ret[s]), mode: 'lines', name: s, line: { color: SCOL[s], width: 1.6 }, hovertemplate: s + ' %{x}: %{y:.2f}<extra></extra>' })),
    { x: B.dates.slice(0, k + 1), y: grow(B.bench['BET-TR']), mode: 'lines', name: 'BET-TR', line: { color: C.navy, width: 2.5 }, hovertemplate: 'BET-TR %{x}: %{y:.2f}<extra></extra>' },
    { x: B.dates.slice(0, k + 1), y: grow(B.bench.BET), mode: 'lines', name: 'BET', line: { color: C.navy, width: 1.5, dash: 'dot' }, hovertemplate: 'BET %{x}: %{y:.2f}<extra></extra>' }
  ], layout({ title: ttl('Eight BVB blue chips, 36-month window: growth of 1 RON'), xaxis: AX('', { type: 'category', nticks: 8, range: [-0.5, last + 0.5] }), yaxis: AX('Growth of 1 RON') }));
  const sr = S.map(s => sharpe(B.ret[s].slice(0, k + 1))), bt = sharpe(B.bench['BET-TR'].slice(0, k + 1)), best = S[sr.indexOf(Math.max(...sr))];
  out('bv-out', [T.bv(B.dates[k], best, nf(Math.max(...sr), 2), nf(bt, 2))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const P = (btn, id, vals, ms) => new Player(btn, $(id), vals, ms);
  $('ta-rho').value = D.two.rho.toFixed(2); on(['ta-rho', 'ta-w'], twoAsset); P('ta-play', 'ta-rho', range(1, -1, -0.05), 160);
  on(['fr-n'], frontier); P('fr-play', 'fr-n', range(2, 9, 1), 900);
  on(['ee-k'], estimationError); $('ee-T').addEventListener('input', () => { eeCache = null; estimationError(); }); P('ee-play', 'ee-k', range(1, 25, 1), 350);
  $('ee-new').addEventListener('click', () => { eeSeed++; estimationError(); });
  $('rw-t').max = D.rolling.dates.length - 1; $('rw-t').value = D.rolling.dates.length - 1; on(['rw-t'], rolling); P('rw-play', 'rw-t', range(0, D.rolling.dates.length - 1, 2), 90);
  $('wl-t').max = D.window.Ts.length - 1; on(['wl-t'], windowLength); P('wl-play', 'wl-t', range(0, D.window.Ts.length - 1, 1), 1200);
  on(['mp-T', 'mp-src'], mpBand); P('mp-play', 'mp-T', range(20, 400, 10), 250);
  $('mp-play').addEventListener('click', () => { if ($('mp-src').value !== 'noise') $('mp-src').value = 'noise'; }, true);
  on(['sh-d'], shrinkage); P('sh-play', 'sh-d', range(0, 1, 0.05), 250);
  on(['bl-q', 'bl-c'], blackLitterman); P('bl-play', 'bl-c', range(2, -2, -0.1), 200);
  on(['rc-k'], riskContribs); P('rc-play', 'rc-k', range(0, 30, 1), 250);
  on(['hrp-s'], hrp); P('hrp-play', 'hrp-s', range(1, 7, 1), 1300);
  on(['ow-u', 'ow-c', 'ow-t'], oosCum); $('ow-t').max = 999; $('ow-t').value = 999; P('ow-play', 'ow-t', range(0, D.oos['Multi-asset'].dates.length - 1, 2), 70);
  on(['os-y'], oosSharpe); P('os-play', 'os-y', range(0, 15, 1), 700);
  on(['co-u', 'co-c'], costs); P('co-play', 'co-c', range(0, 100, 5), 300);
  on(['st-p', 'st-m'], sharpeTest); P('st-play', 'st-m', range(50, 2000, 50), 120);
  $('bv-t').max = 999; $('bv-t').value = 999; on(['bv-t'], bvb); P('bv-play', 'bv-t', range(0, D.bvb.dates.length - 1, 1), 110);
  twoAsset(); frontier(); estimationError(); rolling(); windowLength(); mpBand(); shrinkage(); blackLitterman(); riskContribs(); hrp(); oosCum(); oosSharpe(); costs(); sharpeTest(); bvb();
}
window.CH4 = { wTan, wTanLO, wGMVLO, wERC, riskContrib, leaves, hrpLevels, eigSym, solve };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

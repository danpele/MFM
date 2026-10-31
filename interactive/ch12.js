// Chapter 12 interactive page: one block per chart slide, computed in the browser from ch12_data.js.
(function () {
'use strict';
const D = window.CH12_DATA;
const { C, sum, mean, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, LANG, predict, exitTicket } = window.MFMI;
const T = window.CH12_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', teal: '#17A2B8', navy: '#1F2A44', band: '#C5D2E8' };
const sz = (id, h) => { $(id).style.height = h + 'px'; };
const fmtInt = n => { const s = Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, LANG === 'ro' ? '.' : ','); return s; };
const sgn = (x, d) => (x >= 0 ? '+' : '') + nf(x, d);
function sci(p) {                          // 8.9·10⁻¹⁰
  if (p >= 0.001) return nf(p, 3);
  const e = Math.floor(Math.log10(p)), m = p / Math.pow(10, e), sup = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
  return nf(m, 1) + '·10' + String(e).split('').map(c => sup[c]).join('');
}

// ---------------------------------------------------------------- Normal distribution and Black–Scholes
const npdf = x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
function erfc(x) { const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r; }
const ncdf = x => 0.5 * erfc(-x / Math.SQRT2);
function bs(S, Kk, t, r, s, put) {
  const d1 = (Math.log(S / Kk) + (r + 0.5 * s * s) * t) / (s * Math.sqrt(t)), d2 = d1 - s * Math.sqrt(t);
  return put ? Kk * Math.exp(-r * t) * ncdf(-d2) - S * ncdf(-d1) : S * ncdf(d1) - Kk * Math.exp(-r * t) * ncdf(d2);
}
function greeks(S, Kk, t, r, s) {          // call; vega per volatility point, theta per calendar day (as option_tools.bs_greeks)
  const d1 = (Math.log(S / Kk) + (r + 0.5 * s * s) * t) / (s * Math.sqrt(t)), d2 = d1 - s * Math.sqrt(t), f = npdf(d1);
  return { d1, delta: ncdf(d1), gamma: f / (S * s * Math.sqrt(t)), vega: S * f * Math.sqrt(t) / 100,
    theta: (-S * f * s / (2 * Math.sqrt(t)) - r * Kk * Math.exp(-r * t) * ncdf(d2)) / 365 };
}
function impliedVol(price, S, Kk, t, put) {  // bisection: the price increases in sigma
  let lo = 1e-4, hi = 5;
  if (bs(S, Kk, t, 0, lo, put) > price || bs(S, Kk, t, 0, hi, put) < price) return NaN;
  for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; if (bs(S, Kk, t, 0, m, put) < price) lo = m; else hi = m; }
  return (lo + hi) / 2;
}
function quantile(sorted, p) {            // numpy 'linear' rule
  const h = (sorted.length - 1) * p, lo = Math.floor(h), hi = Math.min(lo + 1, sorted.length - 1);
  return sorted[lo] + (h - lo) * (sorted[hi] - sorted[lo]);
}
const decodeDates = o => { let n = Math.round(Date.parse(o.start) / 864e5); const a = [n]; for (const d of o.diff) a.push(n += d); return a; };
const iso = n => new Date(n * 864e5).toISOString().slice(0, 10);
const MON = { en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] };
const dmy = s => { const [y, m, d] = s.split('-'); return `${d} ${MON.en[+m - 1]} ${y}`; };
const MON_RO = ['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sep.', 'oct.', 'nov.', 'dec.'];
const dmyL = s => { if (LANG !== 'ro') return dmy(s); const [y, m, d] = s.split('-'); return `${+d} ${MON_RO[+m - 1]} ${y}`; };
const daysL = n => (LANG === 'ro' ? `${n} de zile` : `${n} days`);
const LEG = { orientation: 'h', x: 0, xanchor: 'left', y: -0.3, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } };
const stepXY = (b, dens) => { const [a, z, n] = b, w = (z - a) / n, x = [], y = []; for (let i = 0; i <= n; i++) { x.push(a + i * w); y.push(dens[Math.min(i, n - 1)]); } return { x, y }; };
// Newey-West (Bartlett) covariance of OLS coefficients, no small-sample correction (statsmodels HAC)
function olsHAC(y, X, L) {
  const n = y.length, k = X[0].length, XtX = Array.from({ length: k }, () => new Array(k).fill(0)), Xty = new Array(k).fill(0);
  for (let t = 0; t < n; t++) for (let i = 0; i < k; i++) { Xty[i] += X[t][i] * y[t]; for (let j = 0; j < k; j++) XtX[i][j] += X[t][i] * X[t][j]; }
  const inv = M => { const [[a, b], [c, d]] = M, det = a * d - b * c; return [[d / det, -b / det], [-c / det, a / det]]; };
  const B = inv(XtX), beta = B.map(r => r[0] * Xty[0] + r[1] * Xty[1]);
  const u = y.map((v, t) => v - beta[0] * X[t][0] - beta[1] * X[t][1]), g = X.map((x, t) => [x[0] * u[t], x[1] * u[t]]);
  const S = [[0, 0], [0, 0]];
  for (let j = 0; j <= L; j++) {
    const w = j === 0 ? 1 : 1 - j / (L + 1), G = [[0, 0], [0, 0]];
    for (let t = j; t < n; t++) for (let a = 0; a < 2; a++) for (let b = 0; b < 2; b++) G[a][b] += g[t][a] * g[t - j][b];
    for (let a = 0; a < 2; a++) for (let b = 0; b < 2; b++) S[a][b] += j === 0 ? G[a][b] : w * (G[a][b] + G[b][a]);
  }
  const mm = (P, Q) => P.map(r => [r[0] * Q[0][0] + r[1] * Q[1][0], r[0] * Q[0][1] + r[1] * Q[1][1]]), V = mm(mm(B, S), B);
  const my = mean(y), ssr = sum(u.map(e => e * e)), sst = sum(y.map(v => (v - my) ** 2));
  return { beta, V, r2: 1 - ssr / sst };
}
function nwMean(x, L) {                    // mean and Newey-West standard error (Bartlett, L lags)
  const n = x.length, m = mean(x), e = x.map(v => v - m);
  let s = sum(e.map(v => v * v));
  for (let j = 1; j <= L; j++) { let c = 0; for (let t = j; t < n; t++) c += e[t] * e[t - j]; s += 2 * (1 - j / (L + 1)) * c; }
  return { m, se: Math.sqrt(s) / n };
}

// ================================================================= the Greeks
const GK_T = [[1 / 12, K.red, 'One month to expiry'], [0.25, K.blue, 'Three months'], [1, K.green, 'One year']];
function greeksBlock() {
  const s = +$('gk-sig').value / 100, S0 = +$('gk-S').value;
  $('gk-sig-v').textContent = pct(s, 0); $('gk-S-v').textContent = S0;
  const Sg = range(60, 140, 0.4);
  const P = [['gk-d', 'delta', 'Delta ∂C/∂S', '.2f'], ['gk-g', 'gamma', 'Gamma ∂²C/∂S²', '.3f'], ['gk-v', 'vega', 'Vega (per volatility point)', '.3f'], ['gk-t', 'theta', 'Theta (per calendar day)', '.3f']];
  P.forEach(([id, key, title, f], j) => {
    const tr = GK_T.map(([t, col, lab]) => ({ x: Sg, y: Sg.map(S => greeks(S, 100, t, 0.04, s)[key]), mode: 'lines', name: lab, line: { color: col, width: 2 },
      hovertemplate: lab + '<br>S %{x:.1f}: %{y:' + f + '}<extra></extra>' }));
    tr.push({ x: GK_T.map(() => S0), y: GK_T.map(([t]) => greeks(S0, 100, t, 0.04, s)[key]), mode: 'markers', showlegend: false, marker: { color: GK_T.map(g => g[1]), size: 8, line: { color: '#fff', width: 1.5 } }, hoverinfo: 'skip' });
    plot(id, tr, layout({ title: ttl(title), showlegend: j === 0, legend: { orientation: 'h', x: 0, y: -0.2, yanchor: 'top' }, shapes: [vline(100, K.navy, 'dot'), vline(S0, K.navy, 'dash')],
      xaxis: AX('S', { range: [60, 140] }), yaxis: AX('') }));
  });
  const g = greeks(S0, 100, 0.25, 0.04, s);
  out('gk-out', [T.gk(S0, pct(s, 0), nf(g.delta, 2), nf(g.gamma, 4), nf(g.vega, 3), nf(g.theta, 4), nf(g.gamma * S0 * S0 * s * 0.25 / 100, 3))]);
}

// ================================================================= discrete delta hedging
const HE_COL = { 3: K.orange, 12: K.purple, 63: K.blue, 252: K.green };
const HE_LAB = { 3: 'Monthly (3 rebalancings)', 12: 'Weekly (12)', 63: 'Daily (63)', 252: 'Four times a day (252)' };
function hedgeBlock() {
  const H = D.hedge, n = H.N[+$('he-n').value];
  $('he-n-v').textContent = n;
  const tr = [3, 12, 63, 252].map(k => { const p = stepXY(H.bins, H.dens[k]); return { x: p.x, y: p.y, mode: 'lines', line: { shape: 'hv', color: HE_COL[k], width: k === n ? 3 : 1.4 }, name: HE_LAB[k], hovertemplate: HE_LAB[k] + '<br>error %{x:.2f}: density %{y:.3f}<extra></extra>' }; });
  if (!HE_COL[n]) { const p = stepXY(H.bins, H.dens[n]); tr.push({ x: p.x, y: p.y, mode: 'lines', line: { shape: 'hv', color: K.navy, width: 2.5 }, name: `N = ${n}`, hovertemplate: `N = ${n}<br>error %{x:.2f}: density %{y:.3f}<extra></extra>` }); }
  plot('he-hist', tr, layout({ legend: LEG, xaxis: AX('Hedging error at expiry (per option, S₀ = 100)', { range: [-4, 4] }), yaxis: AX('Density') }));
  const Ns = H.N, sdp = Ns.map(k => 100 * H.sd[k] / H.premium), ref = Ns.map(k => sdp[4] * Math.sqrt(21 / k));
  plot('he-sd', [
    { x: Ns, y: sdp, mode: 'lines+markers', name: 'Standard deviation of the error, % of premium', line: { color: K.blue, width: 2 }, marker: { size: 6 }, hovertemplate: 'N = %{x}: %{y:.1f}%<extra></extra>' },
    { x: Ns, y: ref, mode: 'lines', name: 'Slope −1/2: error ∝ 1/√N', line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [n], y: [100 * H.sd[n] / H.premium], mode: 'markers', showlegend: false, marker: { color: K.red, size: 12, line: { color: '#fff', width: 2 } }, hoverinfo: 'skip' }
  ], layout({ legend: LEG, xaxis: AX('Number of rebalancings N', { type: 'log', tickvals: Ns }), yaxis: AX('% of the premium', { type: 'log', tickvals: [5, 10, 20, 40, 70] }) }));
  const vega = 100 * greeks(H.S0, H.K, H.T, H.r, H.sigma).vega, theory = Math.sqrt(Math.PI / 4) * vega * H.sigma / Math.sqrt(n);
  out('he-out', [T.he(n, nf(H.sd[n], 2), pct(H.sd[n] / H.premium), nf(H.premium, 2), nf(H.mean[n], 3), nf(H.q01[n], 2), nf(theory, 2))]);
}

// ================================================================= selling volatility at 20%
const VM_COL = { 15: K.green, 20: K.blue, 25: K.red };
function mismatchBlock() {
  const M = D.mismatch, sr = +$('vm-s').value, R = M.runs;
  $('vm-s-v').textContent = sr + '%';
  const lab = k => `Realised volatility ${k}%: mean P&L ${(R[k].mean >= 0 ? '+' : '−') + Math.abs(R[k].mean).toFixed(2)}`;
  const tr = [15, 20, 25].map(k => { const p = stepXY(M.bins, R[k].dens); return { x: p.x, y: p.y, mode: 'lines', line: { shape: 'hv', color: VM_COL[k], width: k === sr ? 3 : 1.4 }, name: lab(k), hovertemplate: 'P&L %{x:.2f}: density %{y:.3f}<extra></extra>' }; });
  if (!VM_COL[sr]) { const p = stepXY(M.bins, R[sr].dens); tr.push({ x: p.x, y: p.y, mode: 'lines', line: { shape: 'hv', color: K.navy, width: 2.5 }, name: lab(sr), hovertemplate: 'P&L %{x:.2f}: density %{y:.3f}<extra></extra>' }); }
  plot('vm-chart', tr, layout({ shapes: [vline(0, K.navy)], xaxis: AX('P&L of the seller of a 3-month call, hedged daily at 20% implied volatility', { range: [-6, 6] }), yaxis: AX('Density') }));
  const x = R[sr];
  out('vm-out', [T.vm(sr, sgn(x.mean, 2), nf(x.sd, 2), pct(x.win), nf(M.vega, 3), sgn(M.vega * (20 - sr), 2))]);
}

// ================================================================= three sources of a smile
function mertonPrice(S, Kk, t, s, lam, muj, sj, put) {        // Poisson series, r = 0 (option_tools.merton_price)
  const kap = Math.exp(muj + 0.5 * sj * sj) - 1, l2 = lam * (1 + kap) * t; let tot = 0, lf = 0;
  for (let k = 0; k < 60; k++) {
    if (k > 0) lf += Math.log(k);
    const w = Math.exp(-l2 + k * Math.log(l2) - lf), sk = Math.sqrt(s * s + k * sj * sj / t), rk = -lam * kap + k * Math.log(1 + kap) / t;
    tot += w * bs(S, Kk, t, rk, sk, put);
  }
  return tot;
}
function smileBlock() {
  const M = D.smile, rho = +$('sm-rho').value, mj = +$('sm-j').value / 100, t = M.T, S = 100, Ks = M.K.map(k => 100 * k);
  $('sm-rho-v').textContent = nf(rho, 1); $('sm-j-v').textContent = pct(mj, 0);
  // Heston smiles precomputed in Python (export_interactive.heston_smiles): deep OTM puts at ρ near +0.9 cost ~1e-13
  const hes = M.hes[(Math.round(rho * 10) / 10 + 0).toFixed(1)], mer = Ks.map(Kk => impliedVol(mertonPrice(S, Kk, t, 0.14, 1.0, mj, 0.08, Kk < S), S, Kk, t, Kk < S) * 100), emp = M.emp;
  plot('sm-chart', [
    { x: M.K, y: emp, mode: 'lines', name: 'Historical S&P 500 returns (1990-2026)', line: { color: K.blue, width: 2.5 }, hovertemplate: 'K/S %{x:.2f}: %{y:.1f}%<extra></extra>' },
    { x: M.K, y: mer, mode: 'lines', name: `Merton: one ${(mj * 100).toFixed(0)}% mean jump per year`, line: { color: K.red, width: 2, dash: 'dash' }, hovertemplate: 'K/S %{x:.2f}: %{y:.1f}%<extra></extra>' },
    { x: M.K, y: hes, mode: 'lines', name: `Heston stochastic volatility, ρ = ${rho.toFixed(1)}`, line: { color: K.green, width: 2, dash: 'dashdot' }, hovertemplate: 'K/S %{x:.2f}: %{y:.1f}%<extra></extra>' },
    { x: [0.8, 1.2], y: [emp[20], emp[20]], mode: 'lines', name: 'Black-Scholes: constant volatility', line: { color: K.navy, width: 1.2, dash: 'dot' }, hoverinfo: 'skip' }
  ], layout({ xaxis: AX('Moneyness K/S'), yaxis: AX('Implied volatility (%)') }));
  const tri = a => [a[0], a[20], a[40]].map(v => (Number.isFinite(v) ? nf(v, 1) : '—'));
  out('sm-out', [T.sm(...tri(emp), ...tri(mer), ...tri(hes))]);
}

// ================================================================= the Bitcoin smile
const svi = (k, p) => p[0] + p[1] * (p[2] * (k - p[3]) + Math.sqrt((k - p[3]) ** 2 + p[4] ** 2));
function sviG(k, p) {                      // Gatheral-Jacquier g(k)
  const [a, b, rho, m, s] = p, W = svi(k, p), q = Math.sqrt((k - m) ** 2 + s * s), W1 = b * (rho + (k - m) / q), W2 = b * s * s / (q * q * q);
  return (1 - k * W1 / (2 * W)) ** 2 - W1 * W1 / 4 * (1 / W + 0.25) + W2 / 2;
}
const BS_COL = [K.red, K.orange, K.blue, K.green, K.purple];
let bsLast = -1;
function btcSmile(e) {
  const B = D.btc, i = +$('bs-e').value, E = B.exps[i];
  if (i !== bsLast) { bsLast = i; $('bs-rho').value = E.p[2].toFixed(2); $('bs-b').value = 1; }
  const rs = +$('bs-rho').value, rho = Math.abs(rs - +E.p[2].toFixed(2)) < 1e-9 ? E.p[2] : rs, bm = +$('bs-b').value, p = [E.p[0], E.p[1] * bm, rho, E.p[3], E.p[4]];   // slider at the fit: exact fitted rho
  $('bs-e-v').textContent = `${dmyL(E.date)} (${daysL(E.days.toFixed(0))})`; $('bs-rho-v').textContent = nf(rho, 2); $('bs-b-v').textContent = '× ' + nf(bm, 2);
  const tr = [];
  const curve = (X, pp) => { const k0 = X.k[0], k1 = X.k[X.k.length - 1], kk = range(0, 199, 1).map(j => k0 + (k1 - k0) * j / 199); return { kk, iv: kk.map(k => 100 * Math.sqrt(Math.max(svi(k, pp), 0) / X.T)) }; };
  B.chosen.forEach((date, j) => {
    const X = B.exps.find(x => x.date === date), c = curve(X, X.p), sel = X === E, lab = `${dmy(X.date)} (${X.days.toFixed(0)} days)`;
    tr.push({ x: X.k, y: X.iv, mode: 'markers', marker: { color: BS_COL[j], size: sel ? 7 : 5 }, legendgroup: date, showlegend: false, hovertemplate: lab + '<br>k %{x:.3f}: %{y:.1f}%<extra></extra>' });
    tr.push({ x: c.kk, y: c.iv, mode: 'lines', line: { color: BS_COL[j], width: sel ? 3 : 1.6 }, name: lab, legendgroup: date, hoverinfo: 'skip' });
  });
  if (!B.chosen.includes(E.date)) {
    const c = curve(E, E.p), lab = `${dmy(E.date)} (${E.days.toFixed(0)} days)`;
    tr.push({ x: E.k, y: E.iv, mode: 'markers', marker: { color: K.navy, size: 7 }, showlegend: false, hovertemplate: lab + '<br>k %{x:.3f}: %{y:.1f}%<extra></extra>' });
    tr.push({ x: c.kk, y: c.iv, mode: 'lines', line: { color: K.navy, width: 3 }, name: lab, hoverinfo: 'skip' });
  }
  plot('bs-chart', tr, layout({ legend: Object.assign({}, LEG, { y: -0.22, entrywidth: 0.5, entrywidthmode: 'fraction' }), title: ttl('Deribit, 22 Sep 2026 07:51 UTC: quotes (dots), SVI fits (lines)'), shapes: [vline(0, K.navy, 'dot')],
    xaxis: AX('Log-moneyness k = ln(K/F)'), yaxis: AX('Implied volatility (%)') }));
  const c0 = curve(E, E.p), c1 = curve(E, p);
  plot('bs-w', [
    { x: E.k, y: E.iv.map(v => (v / 100) ** 2 * E.T), mode: 'markers', name: 'Quotes: σ²τ', marker: { color: K.navy, size: 6 }, hovertemplate: 'k %{x:.3f}: w %{y:.4f}<extra></extra>' },
    { x: c0.kk, y: c0.kk.map(k => svi(k, E.p)), mode: 'lines', name: 'Fitted SVI', line: { color: K.blue, width: 2.5 }, hoverinfo: 'skip' },
    { x: c1.kk, y: c1.kk.map(k => svi(k, p)), mode: 'lines', name: 'SVI with the chosen ρ and b', line: { color: K.red, width: 2, dash: 'dash' }, hovertemplate: 'k %{x:.3f}: w %{y:.4f}<extra></extra>' }
  ], layout({ legend: LEG, title: ttl(`Total implied variance w(k), ${dmy(E.date)}`), xaxis: AX('Log-moneyness k'), yaxis: AX('w(k) = σ²τ') }));
  const rm = Math.sqrt(mean(E.k.map((k, j) => (100 * Math.sqrt(Math.max(svi(k, p), 0) / E.T) - E.iv[j]) ** 2)));
  let gmin = Infinity, wmin = Infinity; for (let j = 0; j <= 3000; j++) { const k = -1.5 + j * 0.001; gmin = Math.min(gmin, sviG(k, p)); wmin = Math.min(wmin, svi(k, p)); }
  out('bs-out', [T.bs1(dmyL(E.date), E.days.toFixed(0), fmtInt(E.F), nf(E.atm, 1), nf(E.rmse, 2)),
    T.bs2(nf(rho, 2), nf(p[1], 3), nf(p[1] * (1 - rho), 3), nf(p[1] * (1 + rho), 3), nf(rm, 2), nf(gmin, 3), gmin >= 0 && wmin > 0)]);
}

// ================================================================= risk-neutral density
let RN = null;
function rnPrep() {
  const R = D.rnd, F = R.F, t = R.T, n = 2201, k = range(0, n - 1, 1).map(j => -1.2 + 2.2 * j / (n - 1)), Kg = k.map(v => F * Math.exp(v));
  const dens = p => k.map((kk, j) => { const w = Math.max(svi(kk, p), 1e-10), dm = -kk / Math.sqrt(w) - Math.sqrt(w) / 2; return sviG(kk, p) * Math.exp(-dm * dm / 2) / (Kg[j] * Math.sqrt(2 * Math.PI * w)); });   // analytic, no clipping
  const q0 = dens(R.p), atm = Math.sqrt(svi(0, R.p) / t), sl = atm * Math.sqrt(t), mu = Math.log(F) - 0.5 * atm * atm * t;
  const ln = Kg.map(x => Math.exp(-((Math.log(x) - mu) ** 2) / (2 * sl * sl)) / (x * sl * Math.sqrt(2 * Math.PI)));
  const boots = R.boot.map(p => ({ q: dens(p), c: p }));
  const lo = [], hi = [];
  for (let j = 0; j < n; j++) { const v = Float64Array.from(boots.map(b => b.q[j])).sort(); lo.push(quantile(v, 0.025)); hi.push(quantile(v, 0.975)); }
  RN = { F, t, k, Kg, q0, c0: R.p, ln, atm, sl, mu, boots, lo, hi };
}
function rnBelow(p, x) {                   // risk-neutral CDF at K = x F: 1 + dC/dK, analytic in SVI (as in btc_rnd)
  const k = Math.log(x), w = svi(k, p), sw = Math.sqrt(w), d2 = -k / sw - sw / 2;
  const w1 = p[1] * (p[2] + (k - p[3]) / Math.sqrt((k - p[3]) ** 2 + p[4] ** 2));
  return ncdf(-d2) + Math.exp(-d2 * d2 / 2) / Math.sqrt(2 * Math.PI) * w1 / (2 * sw);
}
function rndBlock() {
  if (!RN) rnPrep();
  const R = RN, D0 = D.rnd, x = +$('rn-x').value;
  $('rn-x-v').textContent = nf(x, 2) + 'F';
  const sel = R.Kg.map((v, j) => j).filter(j => R.Kg[j] / R.F >= 0.4 && R.Kg[j] / R.F <= 1.6 && j % 3 === 0);
  const X = sel.map(j => R.Kg[j] / R.F), Y = a => sel.map(j => a[j] * R.F);
  const below = sel.filter(j => R.Kg[j] <= x * R.F);
  plot('rn-chart', [
    { x: X, y: Y(R.lo), mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: X, y: Y(R.hi), mode: 'lines', fill: 'tonexty', fillcolor: 'rgba(23,162,184,0.35)', line: { width: 0 }, name: `95% pairs-bootstrap band (${D0.boot.length} SVI refits)`, hoverinfo: 'skip' },
    { x: below.map(j => R.Kg[j] / R.F), y: below.map(j => R.q0[j] * R.F), mode: 'lines', fill: 'tozeroy', fillcolor: 'rgba(205,0,0,0.25)', line: { width: 0 }, name: `Mass below ${x.toFixed(2)}F`, hoverinfo: 'skip' },
    { x: X, y: Y(R.q0), mode: 'lines', name: 'Risk-neutral density implied by the SVI smile', line: { color: K.blue, width: 2.5 }, hovertemplate: 'S<sub>T</sub>/F %{x:.3f}: %{y:.3f}<extra></extra>' },
    { x: X, y: Y(R.ln), mode: 'lines', name: `Log-normal density with the ATM volatility (${(100 * R.atm).toFixed(1)}%)`, line: { color: K.orange, width: 2, dash: 'dash' }, hovertemplate: 'S_T/F %{x:.3f}: %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl(`Bitcoin, expiry ${dmy(D0.expiry)} (${D0.days.toFixed(0)} days), forward ${fmtInt(D0.F)} USD`),
    shapes: [{ type: 'rect', xref: 'x', yref: 'paper', x0: 0.4, x1: D0.kf_min, y0: 0, y1: 1, fillcolor: '#F5E6CC', opacity: 0.7, line: { width: 0 }, layer: 'below' },
             { type: 'rect', xref: 'x', yref: 'paper', x0: D0.kf_max, x1: 1.6, y0: 0, y1: 1, fillcolor: '#F5E6CC', opacity: 0.7, line: { width: 0 }, layer: 'below' }, vline(x, K.navy, 'dash')],
    annotations: [{ x: 0.42, y: 0.95, xref: 'x', yref: 'paper', xanchor: 'left', showarrow: false, text: `outside the ${D0.n_quotes} quotes`, font: { size: 10, color: K.navy } }],
    xaxis: AX('S<sub>T</sub>/F at expiry', { range: [0.4, 1.6] }), yaxis: AX('Density') }));
  const pq = rnBelow(R.c0, x), lnc = ncdf((Math.log(x * R.F) - R.mu) / R.sl), bq = Float64Array.from(R.boots.map(b => rnBelow(b.c, x))).sort();
  const up = 2 - x, pu = 1 - rnBelow(R.c0, up), lnu = 1 - ncdf((Math.log(up * R.F) - R.mu) / R.sl), ext = rnBelow(R.c0, D0.kf_min);
  out('rn-out', [T.rn1(pct(1 - x, 0), pct(pq, 2), pct(quantile(bq, 0.025), 2), pct(quantile(bq, 0.975), 2), pct(lnc, 2), nf(pq / lnc, 1)),
    T.rn2(pct(1 - x, 0), pct(pu, 1), pct(lnu, 1)), T.rn3(nf(D0.kf_min, 2), nf(100 * ext, 2))]);
}

// ================================================================= the VIX, 1990-2026
let VX = null;
function vixPrep() { const d = decodeDates(D.vix.dates); VX = { n: d, dates: d.map(iso), v: D.vix.v.map(x => x / 100) }; VX.map = new Map(d.map((n, i) => [n, VX.v[i]])); }
function vixBlock() {
  if (!VX) vixPrep();
  const L = +$('vh-l').value, v = VX.v, m = mean(v);
  $('vh-l-v').textContent = L;
  let above = 0, ep = 0, run = 0, longest = 0, prev = false;
  v.forEach(x => { const a = x > L; if (a) { above++; run++; if (!prev) ep++; longest = Math.max(longest, run); } else run = 0; prev = a; });
  plot('vh-chart', [
    { x: VX.dates, y: v, mode: 'lines', name: 'VIX, daily close', line: { color: K.blue, width: 1 }, hovertemplate: '%{x}: %{y:.2f}<extra></extra>' },
    { x: [VX.dates[0], VX.dates[VX.dates.length - 1]], y: [m, m], mode: 'lines', name: 'Mean 1990-2026: ' + m.toFixed(1), line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' },
    { x: [VX.dates[0], VX.dates[VX.dates.length - 1]], y: [L, L], mode: 'lines', name: 'Level ' + L, line: { color: K.red, width: 1.5, dash: 'dot' }, hoverinfo: 'skip' }
  ], layout({ annotations: D.vix.peaks.map(([d, x]) => ({ x: d, y: x, text: `${MON.en[+d.slice(5, 7) - 1]} ${d.slice(0, 4)}<br>${x.toFixed(1)}`, showarrow: false, yanchor: 'bottom', font: { size: 10, color: K.navy } })),
    xaxis: AX('', { type: 'date' }), yaxis: AX('VIX (annualised %, 30 days)', { range: [0, 95] }) }));
  out('vh-out', [T.vh(L, pct(above / v.length), fmtInt(v.length), ep, longest), T.vh2(nf(m, 1), nf(Math.min(...v), 1), nf(Math.max(...v), 1))]);
}

// ================================================================= implied vs realised volatility
let VR = null;
function vrPrep() {
  if (!VX) vixPrep();
  const n = decodeDates(D.vrp.dates), rvAll = D.vrp.rv.map(x => x / 1000);
  VR = { n, dates: n.map(iso), vix: n.map(d => VX.map.get(d)), rv: rvAll.slice(21), rvPast: rvAll.slice(0, n.length) };
  VR.year = VR.dates.map(s => +s.slice(0, 4));
}
function vrpBlock() {
  if (!VR) vrPrep();
  const y0 = +$('vr-y').value, i0 = VR.year.findIndex(y => y >= y0);
  $('vr-y-v').textContent = y0;
  const dt = VR.dates.slice(i0), vx = VR.vix.slice(i0), rv = VR.rv.slice(i0), pv = vx.map((v, i) => v - rv[i]), pvar = vx.map((v, i) => v * v - rv[i] * rv[i]);
  plot('vr-chart', [
    { x: dt, y: vx, mode: 'lines', name: 'VIX at day t (implied, next 30 days)', line: { color: K.blue, width: 0.8 }, hovertemplate: '%{x}: VIX %{y:.1f}<extra></extra>' },
    { x: dt, y: rv, mode: 'lines', name: 'Realised volatility over the next 21 trading days', line: { color: K.red, width: 0.8 }, hovertemplate: '%{x}: RV %{y:.1f}<extra></extra>' },
    { x: dt, y: pv, mode: 'lines', name: 'Premium in volatility points: VIX − √RV', line: { color: K.green, width: 0.7 }, xaxis: 'x', yaxis: 'y2', hovertemplate: '%{x}: %{y:.1f}<extra></extra>' }
  ], layout({ xaxis: AX('', { type: 'date', anchor: 'y2' }), yaxis: AX('Annualised %', { domain: [0.46, 1] }), yaxis2: AX('Volatility points', { domain: [0, 0.38], range: [-75, 35], anchor: 'x' }),
    shapes: [{ type: 'line', xref: 'paper', yref: 'y2', x0: 0, x1: 1, y0: 0, y1: 0, line: { color: K.navy, width: 1.2 } }], legend: { orientation: 'h', x: 0, y: -0.12, yanchor: 'top' } }));
  const a = nwMean(pv, 21), b = nwMean(pvar, 21), w = pv.indexOf(Math.min(...pv));
  out('vr-out', [T.vr1(y0, fmtInt(pv.length), nf(mean(vx), 1), nf(mean(rv), 1)), T.vr2(nf(a.m, 2), nf(a.se, 2), nf(b.m, 0), nf(b.m / b.se, 1)),
    T.vr3(pct(pvar.filter(x => x > 0).length / pvar.length, 0), nf(pv[w], 1), dt[w])]);
}

// ================================================================= Mincer-Zarnowitz
function mzBlock() {
  if (!VR) vrPrep();
  const cap = +$('mz-c').value, idx = VR.vix.map((v, i) => i).filter(i => VR.vix[i] <= cap);
  $('mz-c-v').textContent = cap >= 90 ? (LANG === 'ro' ? 'toate zilele' : 'all days') : cap;
  const y = idx.map(i => VR.rv[i] ** 2), X = idx.map(i => [1, VR.vix[i] ** 2]), Xp = idx.map(i => [1, VR.rvPast[i] ** 2]);
  const m = olsHAC(y, X, 21), mp = olsHAC(y, Xp, 21), [a, b] = m.beta, V = m.V;
  const da = a, db = b - 1, det = V[0][0] * V[1][1] - V[0][1] * V[1][0], wald = (da * da * V[1][1] - 2 * da * db * V[0][1] + db * db * V[0][0]) / det;
  const xx = range(9, 85, 1);
  plot('mz-chart', [
    { x: idx.map(i => VR.vix[i]), y: idx.map(i => VR.rv[i]), mode: 'markers', name: 'Trading days (VIX, realised volatility next 21 days)', marker: { color: K.blue, size: 3, opacity: 0.3 }, hoverinfo: 'skip' },
    { x: xx, y: xx, mode: 'lines', name: '45-degree line: realised = implied', line: { color: K.navy, width: 1.2, dash: 'dash' }, hoverinfo: 'skip' },
    { x: xx, y: xx.map(v => Math.sqrt(Math.max(a + b * v * v, 0))), mode: 'lines', name: 'Mincer-Zarnowitz fit (in variance)', line: { color: K.red, width: 2.5 }, hovertemplate: 'VIX %{x}: fitted %{y:.1f}<extra></extra>' }
  ], layout({ shapes: cap < 90 ? [vline(cap, K.navy, 'dot')] : [], xaxis: AX('VIX at day t', { range: [8, 85] }), yaxis: AX('Realised volatility, next 21 days (%)', { range: [0, 110] }) }));
  out('mz-out', [T.mz1(fmtInt(idx.length), nf(a, 1), nf(Math.sqrt(V[0][0]), 1), nf(b, 2), nf(Math.sqrt(V[1][1]), 2), nf(m.r2, 2)),
    T.mz2(nf(wald, 1), sci(Math.exp(-wald / 2)), nf(V[0][1] / Math.sqrt(V[0][0] * V[1][1]), 2), nf(mp.r2, 2))]);
}

// ================================================================= 0DTE: gamma and time decay
function odteBlock() {
  const s = +$('od-sig').value / 100, d = +$('od-d').value;
  $('od-sig-v').textContent = pct(s, 0); $('od-d-v').textContent = d;
  const Sg = range(95, 105, 0.025);
  const tr = [[1, K.red, 'One trading day'], [5, K.orange, 'One week'], [21, K.blue, 'One month']].map(([n, col, lab]) =>
    ({ x: Sg, y: Sg.map(S => greeks(S, 100, n / 252, 0, s).gamma), mode: 'lines', name: lab, line: { color: col, width: 2 }, hovertemplate: lab + '<br>S %{x:.2f}: %{y:.3f}<extra></extra>' }));
  tr.push({ x: Sg, y: Sg.map(S => greeks(S, 100, d / 252, 0, s).gamma), mode: 'lines', name: `${d} trading day${d > 1 ? 's' : ''}`, line: { color: K.navy, width: 1.6, dash: 'dash' }, hovertemplate: 'S %{x:.2f}: %{y:.3f}<extra></extra>' });
  plot('od-g', tr, layout({ xaxis: AX(`S (strike K = 100, volatility ${(100 * s).toFixed(0)}%)`), yaxis: AX('Gamma') }));
  const days = range(0.25, 30, 0.1), th = t => -greeks(100, 100, t, 0, s).theta, dc = d * 365 / 252;
  plot('od-t', [
    { x: days, y: days.map(x => th(x / 365)), mode: 'lines', name: 'Time decay of an ATM call (price lost per calendar day)', line: { color: K.purple, width: 2 }, hovertemplate: '%{x:.1f} days: %{y:.3f}<extra></extra>' },
    { x: [dc], y: [th(dc / 365)], mode: 'markers', name: `${d} trading day${d > 1 ? 's' : ''} = ${dc.toFixed(1)} calendar days`, marker: { color: K.navy, size: 10, line: { color: '#fff', width: 1.5 } }, hoverinfo: 'skip' }
  ], layout({ xaxis: AX('Calendar days to expiry', { autorange: 'reversed' }), yaxis: AX('−Θ per day') }));
  const g1 = greeks(100, 100, 1 / 252, 0, s).gamma, g21 = greeks(100, 100, 21 / 252, 0, s).gamma, gd = greeks(100, 100, d / 252, 0, s).gamma;
  out('od-out', [T.od1(pct(s, 0), nf(g1, 3), nf(g21, 3), nf(g1 / g21, 1)), T.od2(d, nf(gd, 3), nf(gd, 2)), T.od3(nf(th(1 / 365), 3), nf(th(30 / 365), 3), nf(th(1 / 365) / th(30 / 365), 1))]);
}

// ================================================================= case study: bounds and realised premium
let BK = null;
const BK_H = [1, 3, 6, 12];
function bckBlock() {
  const B = D.bck;
  if (!BK) { const n = decodeDates(B.dates); BK = { dates: n.map(iso), m1: B.m1.map(v => (v === null ? null : v / 100)), cyl1: B.cyl1.map(v => (v === null ? null : v / 100)) }; }
  const h = BK_H[+$('bk-h').value], f = B.f[h].map(v => (v === null ? null : v / 100)), m = B.m[h].map(v => (v === null ? null : v / 100)), dx = BK.dates.slice(B.i0);
  $('bk-h-v').textContent = h + (LANG === 'ro' ? (h > 1 ? ' luni' : ' lună') : (h > 1 ? ' months' : ' month'));
  const ok = f.map((v, i) => i).filter(i => f[i] !== null && m[i] !== null), X = ok.map(i => dx[i]), F = ok.map(i => f[i]), M = ok.map(i => m[i]);
  plot('bk-chart', [
    { x: BK.dates, y: BK.cyl1, mode: 'lines', name: 'Chabi-Yo–Loudis bound', line: { color: K.orange, width: 0.8 }, connectgaps: false, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: BK.dates, y: BK.m1, mode: 'lines', name: 'Martin bound (SVIX)', line: { color: K.red, width: 0.8 }, hovertemplate: '%{x}: %{y:.2f}%<extra></extra>' },
    { x: X, y: M, mode: 'lines', showlegend: false, line: { color: K.red, width: 1.2 }, xaxis: 'x', yaxis: 'y2', hovertemplate: '%{x}: bound %{y:.2f}%<extra></extra>' },
    { x: X, y: F.map((v, i) => Math.min(v, M[i])), mode: 'lines', fill: 'tonexty', fillcolor: 'rgba(205,0,0,0.15)', line: { width: 0 }, name: 'Realised below the bound', xaxis: 'x', yaxis: 'y2', hoverinfo: 'skip' },
    { x: X, y: F, mode: 'lines', name: 'Realised excess return (price index)', line: { color: K.blue, width: 0.8 }, xaxis: 'x', yaxis: 'y2', hovertemplate: '%{x}: realised %{y:.1f}%<extra></extra>' }
  ], layout({ xaxis: AX('', { type: 'date', anchor: 'y2' }), yaxis: AX('Bound, 1 month (annualised %)', { domain: [0.58, 1], rangemode: 'tozero' }),
    yaxis2: AX(`${h} month${h > 1 ? 's' : ''} (annualised %)`, { domain: [0, 0.48], anchor: 'x' }),
    shapes: [{ type: 'line', xref: 'paper', yref: 'y2', x0: 0, x1: 1, y0: 0, y1: 0, line: { color: K.navy, width: 1 } }],
    annotations: [{ text: 'Option-implied lower bounds on the equity premium, 1-month horizon', xref: 'paper', yref: 'paper', x: 0, y: 1.04, showarrow: false, xanchor: 'left', font: { size: 12, color: K.navy } },
                  { text: `Realised ${h}-month S&P 500 excess return vs the ${h}-month Martin bound, by formation date`, xref: 'paper', yref: 'paper', x: 0, y: 0.5, showarrow: false, xanchor: 'left', font: { size: 12, color: K.navy } }],
    legend: { orientation: 'h', x: 0, y: -0.1, yanchor: 'top' } }));
  const below = F.filter((v, i) => v < M[i]).length / F.length, mf = mean(F), mm = mean(M);
  const cf = F.map(v => v - mf), cm = M.map(v => v - mm), corr = sum(cf.map((v, i) => v * cm[i])) / Math.sqrt(sum(cf.map(v => v * v)) * sum(cm.map(v => v * v)));
  out('bk-out', [T.bk1(h, X[0], X[X.length - 1], fmtInt(X.length), pct(below, 0), nf(corr, 2)), T.bk2(nf(mf, 2), nf(B.paper[h], 2), nf(mm, 2), nf(mf - mm, 2))]);
}
function bckStatic() {                      // statistics of the top panel (they do not depend on the horizon)
  const m1 = BK.m1.filter(v => v !== null), s = Float64Array.from(m1).sort(), med = quantile(s, 0.5), mx = Math.max(...m1), i = BK.m1.indexOf(mx);
  const both = BK.m1.map((v, j) => j).filter(j => BK.m1[j] !== null && BK.cyl1[j] !== null), ab = both.filter(j => BK.cyl1[j] >= BK.m1[j]).length / both.length;
  return T.bk3(nf(med, 1), nf(mx, 1), BK.dates[i], pct(ab, 2));
}

// ================================================================= case study 2: volatility expectations (Lochstoer & Muir)
let LM = null;
const LM_H = 12;
function lmPrep() {
  const L = D.lm; LM = { dates: L.dates, year: L.dates.map(x => +x.slice(0, 4)), rv: L.rv, vix2: L.vix2, s2: L.s2hat, ex: L.ex };
}
function lmFitPhi(y, rv, last) {            // NLS of y_t = a + b sum_{j<12} phi^j rv_{t-j}: grid over phi, OLS for (a, b)
  let best = null;
  for (let k = 0; k <= 316; k++) {
    const p = -0.6 + k * (1.58 / 316), xs = [], ys = [];
    for (let t = D.lm.J - 1; t <= last; t++) {
      if (y[t] === null || y[t] === undefined) continue;
      let x = 0; for (let j = 0; j < D.lm.J; j++) x += p ** j * rv[t - j];
      xs.push(x); ys.push(y[t]);
    }
    const mx = mean(xs), my = mean(ys);
    let sxy = 0, sxx = 0; for (let i = 0; i < xs.length; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; }
    const b = sxy / sxx, a = my - b * mx;
    let ssr = 0; for (let i = 0; i < xs.length; i++) ssr += (ys[i] - a - b * xs[i]) ** 2;
    if (!best || ssr < best.ssr) best = { ssr, phi: p };
  }
  return best.phi;
}
function lmIrf(rows) {                      // VAR(1) with intercept, Cholesky; responses to a 1-s.d. shock to the first variable
  const n = rows.length, k = 3, m = k + 1;
  const XtX = Array.from({ length: m }, () => new Array(m).fill(0)), XtY = Array.from({ length: m }, () => new Array(k).fill(0));
  for (let t = 1; t < n; t++) {
    const x = [1, ...rows[t - 1]];
    for (let i = 0; i < m; i++) { for (let j = 0; j < m; j++) XtX[i][j] += x[i] * x[j]; for (let j = 0; j < k; j++) XtY[i][j] += x[i] * rows[t][j]; }
  }
  const inv = matInv(XtX), B = inv.map(r => [0, 1, 2].map(j => r.reduce((s, v, i) => s + v * XtY[i][j], 0)));
  const S = Array.from({ length: k }, () => new Array(k).fill(0));
  for (let t = 1; t < n; t++) {
    const x = [1, ...rows[t - 1]], e = [0, 1, 2].map(j => rows[t][j] - x.reduce((s, v, i) => s + v * B[i][j], 0));
    for (let i = 0; i < k; i++) for (let j = 0; j < k; j++) S[i][j] += e[i] * e[j];
  }
  const dof = (n - 1) - m; for (let i = 0; i < k; i++) for (let j = 0; j < k; j++) S[i][j] /= dof;
  const p0 = Math.sqrt(S[0][0]), c = [p0, S[1][0] / p0, S[2][0] / p0];   // first column of the Cholesky factor
  const A = [0, 1, 2].map(i => [0, 1, 2].map(j => B[j + 1][i]));
  const out = [c];
  for (let h = 0; h < LM_H; h++) { const v = out[out.length - 1]; out.push(A.map(r => r[0] * v[0] + r[1] * v[1] + r[2] * v[2])); }
  return out;
}
function matInv(M) {                        // Gauss-Jordan
  const n = M.length, a = M.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => +(i === j))]);
  for (let c = 0; c < n; c++) {
    let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(a[r][c]) > Math.abs(a[p][c])) p = r;
    [a[c], a[p]] = [a[p], a[c]];
    const d = a[c][c]; for (let j = 0; j < 2 * n; j++) a[c][j] /= d;
    for (let r = 0; r < n; r++) if (r !== c) { const f = a[r][c]; for (let j = 0; j < 2 * n; j++) a[r][j] -= f * a[c][j]; }
  }
  return a.map(r => r.slice(n));
}
function lmCompute(y0) {
  if (!LM) lmPrep();
  let last = LM.year.lastIndexOf(y0);
  const rows = [];
  let first = null;
  for (let t = 0; t <= last; t++) if (LM.s2[t] !== null) { if (first === null) first = t; rows.push([LM.s2[t], LM.vix2[t] - LM.s2[t], LM.ex[t]]); }
  const next = LM.rv.map((v, t) => (t + 1 <= last ? LM.rv[t + 1] : null));
  return { irf: lmIrf(rows), phiV: lmFitPhi(LM.vix2, LM.rv, last), phiR: lmFitPhi(next, LM.rv, last), n: rows.length, first, last };
}
function lmBlock() {
  const y0 = +$('lm-y').value, R = lmCompute(y0), b = D.lm.bands[y0], h = range(0, LM_H, 1);
  $('lm-y-v').textContent = y0 === 2026 ? (LANG === 'ro' ? 'aug. 2026' : 'Aug 2026') : (LANG === 'ro' ? 'dec. ' : 'Dec ') + y0;
  const s2 = R.irf.map(v => v[0]), vrp = R.irf.map(v => v[1]), vx = R.irf.map(v => v[0] + v[1]), j = range(0, D.lm.J - 1, 1);
  const span = `${LM.year[R.first]}-${y0}`;
  plot('lm-irf', [
    { x: h, y: b.hi, mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: h, y: b.lo, mode: 'lines', fill: 'tonexty', fillcolor: 'rgba(205,0,0,0.15)', line: { width: 0 }, name: 'VRP: 95% bootstrap band', hoverinfo: 'skip' },
    { x: h, y: s2, mode: 'lines+markers', name: 'Expected variance (real-time HAR)', line: { color: K.blue, width: 2 }, marker: { size: 5 }, hovertemplate: 'month %{x}: %{y:.0f}<extra></extra>' },
    { x: h, y: vx, mode: 'lines', name: 'VIX² = expected variance + VRP', line: { color: K.teal, width: 1.8, dash: 'dash' }, hovertemplate: 'month %{x}: %{y:.0f}<extra></extra>' },
    { x: h, y: vrp, mode: 'lines+markers', name: 'VRP = VIX² − expected variance', line: { color: K.red, width: 2 }, marker: { size: 5 }, hovertemplate: 'month %{x}: %{y:.0f}<extra></extra>' }
  ], layout({ title: ttl(`Response to a 1-s.d. shock to expected variance, VAR(1), ${span}`), xaxis: AX('Months after the shock', { dtick: 2 }), yaxis: AX('Response (annualised %²)'),
    shapes: [hline(0, K.navy)], legend: LEG }));
  plot('lm-w', [
    { x: j.map(v => v - 0.19), y: j.map(v => R.phiV ** v), type: 'bar', width: 0.36, name: `VIX²: φ̂ = ${R.phiV.toFixed(2)}`, marker: { color: K.purple }, hovertemplate: 'lag %{x:.0f}: %{y:.3f}<extra></extra>' },
    { x: j.map(v => v + 0.19), y: j.map(v => (v === 0 ? 1 : R.phiR ** v)), type: 'bar', width: 0.36, name: `Next month realised variance: φ̂ = ${R.phiR.toFixed(2)}`, marker: { color: K.green }, hovertemplate: 'lag %{x:.0f}: %{y:.3f}<extra></extra>' }
  ], layout({ title: ttl(`Weight on past realised variance, ${LM.year[0]}-${y0}`), xaxis: AX('Lag j of monthly realised variance', { dtick: 2 }), yaxis: AX('Weight φ^j'), legend: LEG, barmode: 'overlay' }));
  const pos = vrp.findIndex(v => v > 0), mx = Math.max(...vrp);
  out('lm-out', [T.lm1(y0 === 2026 ? (LANG === 'ro' ? 'august 2026' : 'August 2026') : y0, fmtInt(R.n), nf(R.phiV, 2), nf(R.phiR, 2)),
    T.lm2(nf(s2[0], 0), nf(vx[0], 0), pct(vx[0] / s2[0], 0), nf(vrp[0], 0), nf(b.lo[0], 0), nf(b.hi[0], 0)),
    T.lm3(pos, nf(mx, 0), vrp.indexOf(mx))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['gk-sig', 'gk-S'], greeksBlock); P('gk-play', 'gk-sig', range(10, 50, 2), 250);
  on(['he-n'], hedgeBlock); P('he-play', 'he-n', range(0, 7, 1), 900);
  on(['vm-s'], mismatchBlock); P('vm-play', 'vm-s', range(10, 30, 1), 450);
  on(['sm-rho', 'sm-j'], smileBlock); P('sm-play', 'sm-rho', range(-0.9, 0.9, 0.1), 500);
  sz('bs-chart', 430); sz('bs-w', 430); on(['bs-e', 'bs-rho', 'bs-b'], btcSmile); P('bs-play', 'bs-e', range(0, 8, 1), 1100);
  on(['rn-x'], rndBlock); P('rn-play', 'rn-x', range(0.5, 0.95, 0.01), 200);
  on(['vh-l'], vixBlock); P('vh-play', 'vh-l', range(10, 80, 2), 300);
  sz('vr-chart', 470); on(['vr-y'], vrpBlock); P('vr-play', 'vr-y', range(1990, 2020, 1), 500);
  on(['mz-c'], mzBlock); P('mz-play', 'mz-c', range(20, 90, 2), 400);
  on(['od-sig', 'od-d'], odteBlock); P('od-play', 'od-d', range(21, 1, -1), 400);
  sz('bk-chart', 500); on(['bk-h'], () => { bckBlock(); }); P('bk-play', 'bk-h', range(0, 3, 1), 1300);
  on(['lm-y'], lmBlock); P('lm-play', 'lm-y', range(2005, 2026, 1), 700);
  const PFX = { 'greeks': 'gk', 'hedge-error': 'he', 'vol-mismatch': 'vm', 'smile-models': 'sm', 'btc-smile': 'bs', 'btc-rnd': 'rn',
    'vix-history': 'vh', 'vrp': 'vr', 'mincer-zarnowitz': 'mz', 'odte': 'od', 'bounds': 'bk', 'vol-expectations': 'lm' };
  // charts that show the answer of the question are blurred too (common veil), until „Verifică”, „Arată slide-ul”, the end of ▶
  // or a change of the parameters
  const HIDE = { 'hedge-error': ['he-hist', 'he-sd'], 'vol-mismatch': ['vm-chart'], 'odte': ['od-g'] };
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) =>
    predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: HIDE[b] ? { out: true, charts: HIDE[b] } : { out: true } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  greeksBlock(); hedgeBlock(); mismatchBlock(); smileBlock(); btcSmile(); rndBlock(); vixBlock(); vrpBlock(); mzBlock(); odteBlock(); bckBlock(); lmBlock();
  const o = $('bk-out'), st = bckStatic(), redraw = () => { if (!o.querySelector('.bk3')) o.insertAdjacentHTML('beforeend', `<li class="bk3">${st}</li>`); };
  redraw(); $('bk-h').addEventListener('input', redraw);
}
window.CH12 = { lmCompute, bs, greeks, impliedVol, mertonPrice, svi, sviG, olsHAC, nwMean, rnPrep, rnBelow, get RN() { return RN; } };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

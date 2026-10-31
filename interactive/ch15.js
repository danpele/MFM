// Chapter 15 interactive page: one block per chart slide, computed in the browser from ch15_data.js.
(function () {
'use strict';
const D = window.CH15_DATA;
const { LANG, sum, mean, median, rng, nf, pct, $, AX, layout, ttl, plot, out, vline, hline, Player, range, predict, exitTicket } = window.MFMI;
const T = window.CH15_TEXT;

// ---------------------------------------------------------------- colours (generate_all_charts.py)
const K = { blue: '#1A3A6E', red: '#CD0000', green: '#2E7D32', amber: '#B5853F', orange: '#E67E22', purple: '#8E44AD', teal: '#17A2B8',
  magenta: '#D63384', brown: '#795548', navy: '#1F2A44', band: '#C5D2E8' };
const LAB_COL = [K.red, K.amber, K.green];                   // negative, neutral, positive
const SCORES = ['lm', 'finbert', 'qwen'];
const SCORE_LBL = { lm: 'Loughran-McDonald tone', finbert: 'FinBERT', qwen: 'Qwen2.5-7B' };
const SCORE_COL = { lm: K.orange, finbert: K.blue, qwen: K.red };

// ---------------------------------------------------------------- helpers
function dec(s, Arr) { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new Arr(u.buffer); }
function dec24(s) { const b = atob(s), n = b.length / 3, o = new Int32Array(n); for (let i = 0; i < n; i++) { const v = b.charCodeAt(3 * i) | (b.charCodeAt(3 * i + 1) << 8) | (b.charCodeAt(3 * i + 2) << 16); o[i] = v & 0x800000 ? v - 0x1000000 : v; } return o; }
const codes = s => Uint8Array.from(s, ch => ch.charCodeAt(0) - 48);
function erfc(x) { const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r; }
const ncdf = x => 0.5 * erfc(-x / Math.SQRT2);
function lgamma(z) {
  const g = [676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61503916999185, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (z < 0.5) return Math.log(Math.PI / Math.abs(Math.sin(Math.PI * z))) - lgamma(1 - z);
  z -= 1; let x = 0.99999999999980993; for (let i = 0; i < 8; i++) x += g[i] / (z + i + 1);
  const t = z + 7.5; return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}
function mcnemarP(n01, n10) {            // exact two-sided binomial test, p = 0.5 (scipy binomtest)
  const n = n01 + n10, k = Math.min(n01, n10); if (n === 0) return 1;
  let s = 0; for (let i = 0; i <= k; i++) s += Math.exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) - n * Math.LN2);
  return Math.min(1, 2 * s);
}
const pv = p => (p < 0.001 ? '< ' + nf(0.001, 3) : '= ' + nf(p, 3));
function sd1(a) { const m = mean(a); return Math.sqrt(sum(a.map(x => (x - m) ** 2)) / (a.length - 1)); }
function quant(a, p) { const b = [...a].sort((x, y) => x - y), h = (b.length - 1) * p, lo = Math.floor(h), hi = Math.min(lo + 1, b.length - 1); return b[lo] + (h - lo) * (b[hi] - b[lo]); }
function aucOf(score, pos) {             // Mann-Whitney U / (n1 n0), ties counted 1/2
  const idx = Array.from(score, (_, i) => i).sort((a, b) => score[a] - score[b]);
  let rs = 0, n1 = 0, i = 0;
  while (i < idx.length) { let j = i; while (j + 1 < idx.length && score[idx[j + 1]] === score[idx[i]]) j++; const rk = (i + j) / 2 + 1; for (let k = i; k <= j; k++) if (pos[idx[k]]) { rs += rk; n1++; } i = j + 1; }
  const n0 = idx.length - n1; return (rs - n1 * (n1 + 1) / 2) / (n1 * n0);
}
function nwT(x, n) {                     // mean and Newey-West t (mfm_text.nw_t), on the first n values
  n = n || x.length; let m = 0; for (let i = 0; i < n; i++) m += x[i]; m /= n;
  const L = Math.floor(4 * Math.pow(n / 100, 2 / 9)); let v = 0;
  for (let i = 0; i < n; i++) v += (x[i] - m) ** 2; v /= n;
  for (let l = 1; l <= L; l++) { let c = 0; for (let i = l; i < n; i++) c += (x[i] - m) * (x[i - l] - m); v += 2 * (1 - l / (L + 1)) * c / n; }
  return [m, m / Math.sqrt(v / n)];
}
function sharpeD(x, n) { n = n || x.length; let m = 0; for (let i = 0; i < n; i++) m += x[i]; m /= n; let v = 0; for (let i = 0; i < n; i++) v += (x[i] - m) ** 2; return Math.sqrt(252) * m / Math.sqrt(v / (n - 1)); }
const ints = n => (LANG === 'ro' ? n.toLocaleString('en-US').replace(/,/g, '\u202f') : n.toLocaleString('en-US'));
const sgn = x => (x > 0 ? 1 : x < 0 ? -1 : 0);
const BOT = y => ({ orientation: 'h', x: 0, xanchor: 'left', y, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } });

// ---------------------------------------------------------------- decoded data
const TX = {};
for (const k of ['pb', 'tw']) { const t = D.texts[k]; TX[k] = { y: codes(t.y), pred: {} }; for (const m in t.pred) TX[k].pred[m] = codes(t.pred[m]); }
TX.pb.agree = codes(D.texts.pb.agree);
const PN = (() => {
  const P = D.panel, o = { n: P.n_obs, day: dec(P.day, Int16Array), tic: dec(P.tic, Uint8Array), cnt: dec(P.n, Uint8Array) };
  for (const c of SCORES) o[c] = Float64Array.from(dec24(P[c]), v => v / 1e6);
  o.r = ['r0', 'r1', 'r2'].map(c => Float64Array.from(dec24(P[c]), v => v / 1e4))
    .concat(['rp3', 'rp4', 'rp5'].map(c => { const r = Float64Array.from(dec(P[c], Int16Array), v => v / 1000); for (const [i, v] of P.big[c]) r[i] = v; return r; }));
  const off = dec(P.days.off, Int16Array), t0 = Date.parse(P.days.start + 'T00:00:00Z');
  o.dates = Array.from(off, v => new Date(t0 + v * 864e5).toISOString().slice(0, 10)); o.nd = off.length;
  o.z = {};
  for (const c of SCORES) { const x = o[c], m = mean(x); let v = 0; for (let i = 0; i < x.length; i++) v += (x[i] - m) ** 2; const s = Math.sqrt(v / (x.length - 1)); o.z[c] = Float64Array.from(x, u => (u - m) / s); }
  return o;
})();

// ================================================================= 1. dictionary words
function dictWords() {
  const L = $('dw-l').value, W = D.dict[L], k = +$('dw-k').value;
  $('dw-k-v').textContent = k;
  const w = W.words.slice(0, k), sl = a => a.slice(0, k);
  const tr = [['pos', 2, 'positive'], ['neu', 1, 'neutral'], ['neg', 0, 'negative']].map(([f, c, l]) => ({ y: w, x: sl(W[f]), type: 'bar', orientation: 'h', name: 'Sentences labelled ' + l,
    marker: { color: LAB_COL[c], line: { color: '#fff', width: 1 } }, hovertemplate: '%{y}: %{x} sentences labelled ' + l + '<extra></extra>' }));
  plot('dw-chart', tr, layout({ barmode: 'stack', bargap: 0.25, legend: Object.assign(BOT(-0.2), { traceorder: 'normal' }), margin: { l: 90, r: 12, t: 30, b: 40 },
    title: ttl(L === 'gi' ? 'Negative in Harvard IV-4, not in Loughran-McDonald' : 'Negative in Loughran-McDonald, not in Harvard IV-4'),
    xaxis: AX('Number of PhraseBank sentences containing the word'), yaxis: AX('', { autorange: 'reversed', tickfont: { size: 10, color: K.navy } }) }));
  const tot = sum(sl(W.pos)) + sum(sl(W.neu)) + sum(sl(W.neg));
  out('dw-out', [T.dw1(k, tot, pct(1 - sum(sl(W.neg)) / tot, 0)), T.dw2(L, W.n_list, W.n_sent, pct(W.nonneg, 0))]);
}

// ================================================================= 2. accuracy of the eleven classifiers
function f1Macro(y, p, idx) {
  const tp = [0, 0, 0], np_ = [0, 0, 0], ny = [0, 0, 0];
  for (const i of idx) { ny[y[i]]++; np_[p[i]]++; if (y[i] === p[i]) tp[y[i]]++; }
  let s = 0; for (let k = 0; k < 3; k++) { const pr = tp[k] / Math.max(np_[k], 1), rc = tp[k] / Math.max(ny[k], 1); s += pr + rc > 0 ? 2 * pr * rc / (pr + rc) : 0; }
  return s / 3;
}
const accOf = (y, p, idx) => { let c = 0; for (const i of idx) if (y[i] === p[i]) c++; return c / idx.length; };
const acCache = {};
function evalSet(set, metric, idx, methods, B) {
  const key = [set, metric, idx.length, B].join('|');
  if (acCache[key]) return acCache[key];
  const S = TX[set], f = metric === 'acc' ? accOf : f1Macro, res = {}, n = idx.length;
  for (const m of methods) {
    const p = S.pred[m], z = rng(15), draws = [], b = new Array(n);
    for (let r = 0; r < B; r++) { for (let i = 0; i < n; i++) b[i] = idx[Math.floor(z.u() * n)]; draws.push(f(S.y, p, b)); }
    res[m] = { v: f(S.y, p, idx), lo: B ? quant(draws, 0.025) : NaN, hi: B ? quant(draws, 0.975) : NaN };
  }
  const neu = new Uint8Array(S.y.length).fill(1);
  res.base = f(S.y, neu, idx);
  return (acCache[key] = res);
}
const AGREE_EN = ['all sentences', '≥ 66% agreement', '≥ 75% agreement', '100% agreement'];
function accuracy() {
  const metric = $('ac-m').value, a = +$('ac-a').value, M = D.texts.methods, col = D.texts.colors;
  $('ac-a-v').textContent = T.agree[a];
  const ipb = []; TX.pb.agree.forEach((v, i) => { if (v >= a) ipb.push(i); });
  const itw = Array.from(TX.tw.y, (_, i) => i);
  const saved = k => metric === 'acc' && (k === 'tw' || a === 0);     // the slide's bootstrap intervals (1,000 draws)
  const R = { pb: Object.assign({}, evalSet('pb', metric, ipb, M, saved('pb') ? 0 : 1000)), tw: Object.assign({}, evalSet('tw', metric, itw, M, saved('tw') ? 0 : 1000)) };
  for (const k of ['pb', 'tw']) if (saved(k)) for (const m of M) R[k][m] = { v: R[k][m].v, lo: D.texts.res[k][m].lo, hi: D.texts.res[k][m].hi };
  const lab = metric === 'acc' ? 'Accuracy (%) with 95% CI' : 'Macro-F1 (%) with 95% CI';
  const one = (id, k, title) => plot(id, [
    ...M.map(m => ({ x: [100 * R[k][m].v], y: [m], mode: 'markers', type: 'scatter', showlegend: false, marker: { color: col[m], size: 10 },
      error_x: { type: 'data', symmetric: false, array: [100 * (R[k][m].hi - R[k][m].v)], arrayminus: [100 * (R[k][m].v - R[k][m].lo)], color: col[m], thickness: 1.5, width: 3 },
      hovertemplate: m + ': %{x:.1f}%<br>95% CI ' + (100 * R[k][m].lo).toFixed(1) + '–' + (100 * R[k][m].hi).toFixed(1) + '<extra></extra>' })),
    { x: [100 * R[k].base, 100 * R[k].base], y: [M[0], M[M.length - 1]], mode: 'lines', name: 'Always "neutral" (majority class)', showlegend: k === 'pb', line: { color: K.navy, dash: 'dash', width: 1.5 }, hoverinfo: 'skip' }
  ], layout({ title: ttl(title), legend: BOT(-0.2), margin: { l: 90, r: 12, t: 30, b: 40 }, xaxis: AX(lab, { range: metric === 'acc' ? [30, 100] : [15, 100] }), yaxis: AX('', { autorange: 'reversed', type: 'category' }) }));
  one('ac-pb', 'pb', 'Financial PhraseBank, ' + AGREE_EN[a] + ', n = ' + ipb.length.toLocaleString('en-US'));
  one('ac-tw', 'tw', 'Twitter Financial News (2022), n = ' + itw.length.toLocaleString('en-US'));
  const best = M.reduce((b, m) => (R.tw[m].v > R.tw[b].v ? m : b), M[0]);
  out('ac-out', [T.ac1(T.agree[a], ints(ipb.length), T.metric[metric], pct(R.pb.FinBERT.v), pct(R.pb['Qwen 7B'].v), pct(R.pb.base)),
    T.ac2(T.best[metric], best, pct(R.tw[best].v), pct(R.tw.GI.v), pct(R.tw.VADER.v), pct(R.tw.LM.v), pct(R.tw.base))]);
}

// ================================================================= 3. model size
const SIZES = ['0.5B', '1.5B', '3B', '7B', '14B'], SZ = [0.5, 1.5, 3, 7, 14];
function llmSize() {
  const metric = $('ls-m').value, p = +$('ls-p').value, f = metric === 'acc' ? accOf : f1Macro;
  $('ls-p-v').textContent = 'P' + p;
  const all = k => Array.from(TX[k].y, (_, i) => i), ip = all('pb'), it = all('tw');
  const v = (k, m, idx) => 100 * f(TX[k].y, TX[k].pred[m], idx);
  const twS = p === 1 ? SIZES : ['1.5B', '7B', '14B'], twM = s => 'Qwen ' + s + (p === 1 ? '' : ' P' + p);
  const fb = { pb: v('pb', 'FinBERT', ip), tw: v('tw', 'FinBERT', it) };
  const ylab = metric === 'acc' ? 'Accuracy (%)' : 'Macro-F1 (%)';
  plot('ls-chart', [
    { x: SZ, y: SIZES.map(s => v('pb', 'Qwen ' + s, ip)), mode: 'lines+markers', name: 'Qwen2.5, Financial PhraseBank (prompt P1)', line: { color: K.blue, width: 2 }, marker: { size: 10 }, hovertemplate: '%{x}B: %{y:.1f}%<extra></extra>' },
    { x: [0.4, 18], y: [fb.pb, fb.pb], mode: 'lines', name: 'FinBERT, Financial PhraseBank', line: { color: K.blue, dash: 'dot', width: 1.5 }, hovertemplate: 'FinBERT: %{y:.1f}%<extra></extra>' },
    { x: twS.map(s => SZ[SIZES.indexOf(s)]), y: twS.map(s => v('tw', twM(s), it)), mode: 'lines+markers', name: 'Qwen2.5, Twitter Financial News (prompt P' + p + ')', line: { color: K.red, width: 2 }, marker: { size: 10 }, hovertemplate: '%{x}B: %{y:.1f}%<extra></extra>' },
    { x: [0.4, 18], y: [fb.tw, fb.tw], mode: 'lines', name: 'FinBERT, Twitter Financial News', line: { color: K.red, dash: 'dot', width: 1.5 }, hovertemplate: 'FinBERT: %{y:.1f}%<extra></extra>' }
  ], layout({ legend: BOT(-0.22), xaxis: AX('Parameters (billions, log scale)', { type: 'log', tickvals: SZ, ticktext: SIZES, range: [Math.log10(0.4), Math.log10(18)] }), yaxis: AX(ylab) }));
  const y = TX.tw.y, a = TX.tw.pred[twM('1.5B')], b = TX.tw.pred[twM('7B')];
  let n01 = 0, n10 = 0; for (let i = 0; i < y.length; i++) { const ca = a[i] === y[i], cb = b[i] === y[i]; if (!ca && cb) n01++; if (ca && !cb) n10++; }
  const neu = a.reduce((s, c) => s + (c === 1), 0) / a.length;
  out('ls-out', [T.ls1(p, T.metric[metric], ...['1.5B', '7B', '14B'].map(s => pct(v('tw', twM(s), it) / 100)), pct(fb.tw / 100)),
    T.ls2(pct(neu, 0), nf(100 * (n01 - n10) / y.length, 1), n01, n10, pv(mcnemarP(n01, n10)))]);
}

// ================================================================= 4. embeddings
const EMB = { x: Float64Array.from(dec(D.emb.pc1, Int16Array), v => v / 1e4), y: Float64Array.from(dec(D.emb.pc2, Int16Array), v => v / 1e4) };
let embBest = null;
function projAuc(th) {
  const c = Math.cos(th * Math.PI / 180), s = Math.sin(th * Math.PI / 180), y = TX.tw.y, sc = [], pos = [];
  for (let i = 0; i < y.length; i++) if (y[i] !== 1) { sc.push(c * EMB.x[i] + s * EMB.y[i]); pos.push(y[i] === 2); }
  return aucOf(sc, pos);
}
function embeddings() {
  const th = +$('em-t').value, c = Math.cos(th * Math.PI / 180), s = Math.sin(th * Math.PI / 180), y = TX.tw.y;
  $('em-t-v').textContent = th + '°';
  if (!embBest) { embBest = { a: 0, th: 0 }; for (let t = 0; t < 180; t++) { const a = projAuc(t), d = Math.max(a, 1 - a); if (d > embBest.a) embBest = { a: d, th: t }; } }
  const names = ['negative', 'neutral', 'positive'], cnt = [0, 1, 2].map(k => y.reduce((q, v) => q + (v === k), 0));
  const tr = [1, 2, 0].map(k => { const ix = []; y.forEach((v, i) => { if (v === k) ix.push(i); });
    return { x: ix.map(i => EMB.x[i]), y: ix.map(i => EMB.y[i]), mode: 'markers', type: 'scatter', name: `${names[k]} (${cnt[k].toLocaleString('en-US')})`, marker: { color: LAB_COL[k], size: 4, opacity: 0.6 }, hovertemplate: names[k] + '<br>PC1 %{x:.2f}, PC2 %{y:.2f}<extra></extra>' }; });
  tr.push({ x: [-0.5 * c, 0.5 * c], y: [-0.5 * s, 0.5 * s], mode: 'lines', name: 'Projection direction', line: { color: K.navy, width: 2.5 }, hoverinfo: 'skip' });
  plot('em-sc', tr, layout({ legend: BOT(-0.2), xaxis: AX('First principal component', { range: [-0.5, 0.5], zeroline: false }), yaxis: AX('Second principal component', { range: [-0.5, 0.5], zeroline: false }) }));
  plot('em-h', [1, 2, 0].map(k => { const v = []; y.forEach((u, i) => { if (u === k) v.push(c * EMB.x[i] + s * EMB.y[i]); });
    return { x: v, type: 'histogram', histnorm: 'probability density', xbins: { start: -0.6, end: 0.6, size: 0.03 }, name: names[k], opacity: 0.55, marker: { color: LAB_COL[k] }, hovertemplate: names[k] + ' %{x}: %{y:.2f}<extra></extra>' }; }),
    layout({ barmode: 'overlay', bargap: 0, legend: BOT(-0.2), title: ttl(`Projection on the direction at ${th}°`), xaxis: AX('Projection', { range: [-0.55, 0.55] }), yaxis: AX('Density') }));
  const a0 = projAuc(th), a = Math.max(a0, 1 - a0);
  out('em-out', [T.em(th, nf(a, 3), nf(embBest.a, 3), embBest.th, pct(D.emb.acc_lr))]);
}

// ================================================================= 5. learning curve
function learningCurve() {
  const L = D.lc, k = +$('lc-k').value, n = L.n[k];
  $('lc-k-v').textContent = ints(n);
  const ms = a => a.map(v => 100 * mean(v)), ss = a => a.map(v => (v.length > 1 ? 100 * sd1(v) : 0));
  const band = (a, c, name) => { const m = ms(a), s = ss(a); return [
    { x: L.n, y: m.map((v, i) => v + 2 * s[i]), mode: 'lines', line: { width: 0 }, showlegend: false, hoverinfo: 'skip' },
    { x: L.n, y: m.map((v, i) => v - 2 * s[i]), mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: c + '26', showlegend: false, hoverinfo: 'skip' },
    { x: L.n, y: m, mode: 'lines+markers', name, line: { color: c, width: 2 }, marker: { size: 6 }, hovertemplate: '%{x} labels: %{y:.1f}%<extra></extra>' }]; };
  const pts = (a, c, name) => ({ x: a[k].map(() => n), y: a[k].map(v => 100 * v), mode: 'markers', name, marker: { color: c, size: 8, symbol: 'circle-open', line: { width: 1.5 } }, hovertemplate: '%{y:.1f}%<extra></extra>' });
  plot('lc-chart', [...band(L.emb, K.magenta, 'MiniLM embeddings + logistic regression'), ...band(L.tfidf, K.teal, 'TF-IDF (min_df=1) + logistic regression'),
    pts(L.emb, K.magenta, 'Embeddings, each training resample'), pts(L.tfidf, K.teal, 'TF-IDF, each training resample'),
    { x: [80, 12000], y: [100 * L.finbert, 100 * L.finbert], mode: 'lines', name: 'FinBERT, no Twitter labels used', line: { color: K.blue, dash: 'dash', width: 1.5 }, hoverinfo: 'skip' },
    { x: [80, 12000], y: [100 * L.qwen7, 100 * L.qwen7], mode: 'lines', name: 'Qwen 7B, no Twitter labels used', line: { color: K.red, dash: 'dot', width: 1.5 }, hoverinfo: 'skip' }
  ], layout({ title: ttl('Bands: mean accuracy plus/minus 2 SD across training resamples'), legend: Object.assign(BOT(-0.2), { traceorder: 'normal' }), shapes: [vline(n, K.navy, 'dot')],
    xaxis: AX('Labelled training examples (log scale)', { type: 'log', range: [Math.log10(80), Math.log10(12000)], tickvals: L.n, ticktext: L.n.map(v => v.toLocaleString('en-US')) }), yaxis: AX('Validation accuracy (%)') }));
  const e = L.emb[k], t = L.tfidf[k], first = L.n.find((_, i) => mean(L.emb[i]) > L.finbert);
  out('lc-out', [T.lc(n, e.length, pct(mean(e)), pct(Math.min(...e)), pct(Math.max(...e)), pct(mean(t)), pct(L.finbert), pct(L.qwen7), first)]);
}

// ================================================================= 6. memory of past market moves
const MEM = {};
for (const s of ['monthly', 'daily']) { const m = D.mem[s]; MEM[s] = { up: codes(m.up).map(v => v === 1), pre: m.dates.map(d => d <= m.cut_pre), post: m.dates.map(d => d >= m.cut_post) }; }
function roc(p, up) {
  const th = [...new Set(p)].sort((a, b) => b - a), n1 = up.filter(Boolean).length, n0 = up.length - n1, x = [0], y = [0];
  for (const t of th) { let tp = 0, fp = 0; for (let i = 0; i < p.length; i++) if (p[i] >= t) { if (up[i]) tp++; else fp++; } x.push(fp / n0); y.push(tp / n1); }
  x.push(1); y.push(1); return { x, y };
}
function memory() {
  const s = $('ma-s').value, m = $('ma-m').value, c = +$('ma-c').value, M = D.mem, R = M.res, Ms = ['1.5B', '7B', '14B'];
  $('ma-c-v').textContent = nf(c, 2);
  const per = [['pre', K.blue, 'Before the weights were released'], ['post', K.orange, 'After the release (the model cannot know)']];
  const tr = [];
  ['monthly', 'daily'].forEach((name, j) => per.forEach(([q, col, lab], k) => tr.push({
    x: Ms.map((_, i) => i + (k - 0.5) * 0.22), y: Ms.map(z => R[name][z][q].auc), mode: 'markers', name: lab, showlegend: j === 0, legendgroup: q, xaxis: j ? 'x2' : 'x', yaxis: j ? 'y2' : 'y',
    marker: { color: col, size: Ms.map(z => (name === s && z === m ? 13 : 9)), line: { color: '#fff', width: 1 } },
    error_y: { type: 'data', symmetric: false, array: Ms.map(z => R[name][z][q].hi - R[name][z][q].auc), arrayminus: Ms.map(z => R[name][z][q].auc - R[name][z][q].lo), color: col, thickness: 1.5, width: 3 },
    customdata: Ms.map(z => [z, R[name][z][q].lo, R[name][z][q].hi]), hovertemplate: 'Qwen2.5-%{customdata[0]}: AUC %{y:.2f}<br>95% CI %{customdata[1]:.2f}–%{customdata[2]:.2f}<extra></extra>' })));
  const tk = { tickvals: [0, 1, 2], ticktext: Ms, range: [-0.5, 2.5] };
  plot('ma-auc', tr, layout({ grid: { rows: 1, columns: 2, pattern: 'independent' }, legend: BOT(-0.22),
    shapes: [{ type: 'line', xref: 'x domain', yref: 'y', x0: 0, x1: 1, y0: 0.5, y1: 0.5, line: { color: K.navy, dash: 'dash', width: 1.2 } }, { type: 'line', xref: 'x2 domain', yref: 'y2', x0: 0, x1: 1, y0: 0.5, y1: 0.5, line: { color: K.navy, dash: 'dash', width: 1.2 } }],
    annotations: [{ text: 'S&P 500, months', xref: 'x domain', yref: 'paper', x: 0, y: 1.08, showarrow: false, xanchor: 'left', font: { size: 11 } }, { text: 'Apple, single days', xref: 'x2 domain', yref: 'paper', x: 0, y: 1.08, showarrow: false, xanchor: 'left', font: { size: 11 } }],
    xaxis: AX('Qwen2.5 model size', tk), xaxis2: AX('Qwen2.5 model size', tk), yaxis: AX('AUC: rises vs falls (95% CI)', { range: [0.25, 0.95] }), yaxis2: AX('', { range: [0.25, 0.95], matches: 'y' }) }));
  const E = MEM[s], P = M[s].p[m], sel = q => { const p = [], u = []; E[q].forEach((b, i) => { if (b) { p.push(P[i]); u.push(E.up[i]); } }); return { p, u }; };
  const res = {}, rtr = [];
  per.forEach(([q, col, lab]) => {
    const { p, u } = sel(q), r = roc(p, u), n1 = u.filter(Boolean).length, n0 = u.length - n1;
    let tp = 0, tn = 0; p.forEach((v, i) => { if (u[i] && v > c) tp++; if (!u[i] && v <= c) tn++; });
    res[q] = { auc: aucOf(p, u), tpr: tp / n1, fpr: 1 - tn / n0, ba: 0.5 * (tp / n1 + tn / n0), n: u.length };
    rtr.push({ x: r.x, y: r.y, mode: 'lines', name: lab, line: { color: col, width: 2, shape: 'hv' }, hovertemplate: 'FPR %{x:.2f}, TPR %{y:.2f}<extra></extra>' });
    rtr.push({ x: [res[q].fpr], y: [res[q].tpr], mode: 'markers', showlegend: false, marker: { color: col, size: 11, line: { color: '#fff', width: 1.5 } }, hovertemplate: 'P("rise") > ' + c.toFixed(2) + '<br>FPR %{x:.2f}, TPR %{y:.2f}<extra></extra>' });
  });
  rtr.push({ x: [0, 1], y: [0, 1], mode: 'lines', name: 'AUC = 0.5', line: { color: K.navy, dash: 'dash', width: 1 }, hoverinfo: 'skip' });
  plot('ma-roc', rtr, layout({ title: ttl(`ROC curve, Qwen2.5-${m}, ${s === 'monthly' ? 'S&P 500 months' : 'Apple days'}`), legend: BOT(-0.22),
    xaxis: AX('False positive rate (falls called "rise")', { range: [0, 1] }), yaxis: AX('True positive rate (rises called "rise")', { range: [0, 1] }) }));
  out('ma-out', [T.ma1(s, m, nf(res.pre.auc, 2), res.pre.n, nf(res.post.auc, 2), res.post.n), T.ma2(nf(c, 2), pct(res.pre.tpr, 0), pct(res.pre.fpr, 0), pct(res.pre.ba, 1), pct(res.post.ba, 1))]);
}

// ================================================================= 7. hours of the timestamps
function newsHours() {
  const o = +$('nh-o').value, H = D.hours.n, lab = 'UTC' + (o === 0 ? '' : (o > 0 ? '+' : '−') + Math.abs(o));
  $('nh-o-v').textContent = lab;
  const loc = h => ((h + o) % 24 + 24) % 24, x = H.map((_, h) => loc(h)), mid = loc(0);
  const s0 = 14.5 + o, s1 = 21 + o, segs = [[s0, s1]].flatMap(([a, b]) => { const a2 = ((a % 24) + 24) % 24, b2 = a2 + (b - a); return b2 <= 24 ? [[a2, b2]] : [[a2, 24], [0, b2 - 24]]; });
  plot('nh-chart', [
    { x: [mid], y: [H[0]], type: 'bar', width: 0.8, name: `00:00 UTC: ${(100 * D.hours.midnight).toFixed(1)}% of headlines stamped exactly at midnight`, marker: { color: K.red }, hovertemplate: '%{x}:00 ' + lab + ': %{y:,} headlines<extra></extra>' },
    { x: x.slice(1), y: H.slice(1), type: 'bar', width: 0.8, name: 'Other hours', marker: { color: K.blue }, hovertemplate: '%{x}:00 ' + lab + ': %{y} headlines<extra></extra>' }
  ], layout({ legend: BOT(-0.24), bargap: 0.2,
    shapes: segs.map(([a, b]) => ({ type: 'rect', xref: 'x', yref: 'paper', x0: a - 0.5, x1: b - 0.5, y0: 0, y1: 1, fillcolor: K.band, opacity: 0.45, line: { width: 0 }, layer: 'below' })),
    annotations: [{ x: segs[0][0] - 0.5, y: 1, yref: 'paper', text: 'NYSE session, winter (14:30–21:00 UTC)', showarrow: false, xanchor: 'left', yanchor: 'bottom', font: { size: 10 } }],
    xaxis: AX(`Hour of the timestamp (${lab})`, { dtick: 2, range: [-0.6, 23.6] }), yaxis: AX('Headlines (log scale)', { type: 'log' }) }));
  const other = sum(H.slice(1)), prev = o < 0;
  out('nh-out', [T.nh(pct(D.hours.midnight, 1), lab, String(mid).padStart(2, '0'), prev, other)]);
}

// ================================================================= 8. reaction and prediction: panel slopes
function clusterOLS(y, x, day, idx) {    // y = a + b x, standard error clustered by day (mfm_text.cluster_ols)
  const n = idx.length; let mx = 0, my = 0; for (const i of idx) { mx += x[i]; my += y[i]; } mx /= n; my /= n;
  let sxx = 0, sxy = 0; for (const i of idx) { const d = x[i] - mx; sxx += d * d; sxy += d * (y[i] - my); }
  const b = sxy / sxx, a = my - b * mx, g = new Map();
  for (const i of idx) { const e = y[i] - a - b * x[i], u = (x[i] - mx) * e; g.set(day[i], (g.get(day[i]) || 0) + u); }
  let m = 0; for (const v of g.values()) m += v * v; const G = g.size;
  const se = Math.sqrt(m / (sxx * sxx) * G / (G - 1) * (n - 1) / (n - 2));
  return { b, se, t: b / se, n };
}
const HCOL = [K.blue, K.amber, K.red, K.green, K.purple, K.teal];
const HLAB = ['Day of the news (d)', 'Day d+1 (news may still be arriving)', 'Day d+2 (tradable forecast)', 'Day d+3', 'Day d+4', 'Day d+5'];
const cnCache = {};
function contempNext() {
  const m = +$('cn-n').value, H = +$('cn-h').value;
  $('cn-n-v').textContent = m;
  const idx = []; for (let i = 0; i < PN.n; i++) if (PN.cnt[i] >= m) idx.push(i);
  const R = {};
  for (const c of SCORES) for (let h = 0; h < 6; h++) { const k = m + c + h; R[c + h] = cnCache[k] || (cnCache[k] = clusterOLS(PN.r[h], PN.z[c], PN.day, idx)); }
  const w = H === 3 ? 0.22 : 0.13;
  plot('cn-chart', Array.from({ length: H }, (_, h) => ({ x: SCORES.map((_, j) => j + (h - (H - 1) / 2) * w), y: SCORES.map(c => 100 * R[c + h].b), mode: 'markers', name: HLAB[h],
    marker: { color: HCOL[h], size: 9 }, error_y: { type: 'data', array: SCORES.map(c => 196 * R[c + h].se), color: HCOL[h], thickness: 1.5, width: 4 },
    customdata: SCORES.map(c => [SCORE_LBL[c], R[c + h].t]), hovertemplate: '%{customdata[0]}, ' + HLAB[h].split(' (')[0] + ': %{y:.1f} bp (t = %{customdata[1]:.2f})<extra></extra>' })),
    layout({ legend: BOT(-0.16), shapes: [hline(0, K.navy)], title: ttl(`${idx.length.toLocaleString('en-US')} stock-days with at least ${m} headline${m > 1 ? 's' : ''}; bars: 95% CI clustered by day`),
      xaxis: AX('', { tickvals: [0, 1, 2], ticktext: SCORES.map(c => SCORE_LBL[c]), range: [-0.5, 2.5], zeroline: false }), yaxis: AX('Excess return per 1 s.d. of score (bp)') }));
  const f = (c, h) => [nf(100 * R[c + h].b, 1), nf(R[c + h].t, 2)];
  out('cn-out', [T.cn1(m, idx.length, ...f('finbert', 0), ...f('qwen', 0), ...f('lm', 0)), T.cn2(...f('finbert', 2), ...f('qwen', 2), ...f('lm', 2))]);
}

// ================================================================= 9. the long-short strategy
const sgCache = {};
function stratGross(c, lag, band) {      // mfm_text.signal_portfolio: return on day d+lag, positions sign(score) where |score| > band
  const k = c + lag + ':' + band; if (sgCache[k]) return sgCache[k];
  const nd = PN.nd, s = new Float64Array(nd), cnt = new Uint16Array(nd), x = PN[c], r = PN.r[lag];
  for (let i = 0; i < PN.n; i++) { if (!(Math.abs(x[i]) > band)) continue; const e = PN.day[i] + lag; if (e >= nd) continue; s[e] += sgn(x[i]) * r[i]; cnt[e]++; }
  for (let e = 0; e < nd; e++) if (cnt[e]) s[e] /= cnt[e];
  return (sgCache[k] = { g: s, k: cnt });
}
function strategy() {
  const lag = +$('sg-l').value, c = +$('sg-c').value, nd = PN.nd; let t = +$('sg-t').value;
  $('sg-t').max = nd - 1; if (t > nd - 1) { t = nd - 1; $('sg-t').value = t; }
  $('sg-l-v').textContent = 'd+' + lag; $('sg-c-v').textContent = nf(c, 1) + ' bp'; $('sg-t-v').textContent = PN.dates[t];
  const tr = [], st = {}, X = PN.dates.slice(0, t + 1);
  for (const sc of SCORES) {
    const { g, k } = stratGross(sc, lag, 0), net = Float64Array.from(g, (v, i) => v - (k[i] > 0 ? 4 * c / 100 : 0));
    let a = 0, b = 0; const cg = [], cn = [];
    for (let i = 0; i <= t; i++) { a += g[i]; b += net[i]; cg.push(a); cn.push(b); }
    const short = sc === 'lm' ? 'LM' : SCORE_LBL[sc];
    tr.push({ x: X, y: cg, mode: 'lines', name: short + ', gross', line: { color: SCORE_COL[sc], width: 1.6 }, hovertemplate: short + ' gross %{x}: %{y:.0f}%<extra></extra>' });
    tr.push({ x: X, y: cn, mode: 'lines', name: `${short}, net of ${c.toFixed(1)} bp`, line: { color: SCORE_COL[sc], width: 1.2, dash: 'dash' }, hovertemplate: short + ' net %{x}: %{y:.0f}%<extra></extra>' });
    const [mu, tt] = nwT(g, t + 1); let act = 0, sa = 0; for (let i = 0; i <= t; i++) if (k[i]) { act++; sa += g[i]; }
    st[sc] = { mu: 100 * mu, t: tt, sr: sharpeD(g, t + 1), srn: sharpeD(net, t + 1), be: 100 * sa / act / 4 };
  }
  plot('sg-chart', tr, layout({ legend: BOT(-0.14), shapes: [hline(0, K.navy)], xaxis: AX('', { type: 'date', range: [PN.dates[0], PN.dates[nd - 1]] }), yaxis: AX(`Cumulative d+${lag} return (%, sum)`) }));
  const q = st.qwen, f = st.finbert, l = st.lm;
  out('sg-out', [T.sg1(lag, PN.dates[t], nf(q.mu, 2), nf(q.t, 2), nf(q.sr, 2), nf(c, 1), nf(q.srn, 2), nf(q.be, 1)),
    T.sg2(nf(f.mu, 2), nf(f.t, 2), nf(f.srn, 2), nf(l.mu, 2), nf(l.t, 2), nf(l.srn, 2))]);
}

// ================================================================= 10. prediction-powered inference
const PPI_N = [50, 100, 200, 400, 800, 1200, 1600];
const PP = { y: Float64Array.from(TX.tw.y, v => v - 1), f: { finbert: Float64Array.from(dec(D.ppi.f_finbert, Int16Array), v => v / 1e4), qwen: Float64Array.from(dec(D.ppi.f_qwen, Int16Array), v => v / 1e4) } };
const ppCache = {};
function ppiSim(n, R) {
  if (ppCache[n]) return ppCache[n];
  const y = PP.y, N = y.length, z = rng(15 + n), th = mean(Array.from(y)), zq = 1.959963984540054;
  const S = { classical: [], ppi_finbert: [], ppi_qwen: [], naive_finbert: [] }, L = new Int32Array(n);
  for (let r = 0; r < R; r++) {
    let m = 0, v = 0; for (let i = 0; i < n; i++) { L[i] = Math.floor(z.u() * N); m += y[L[i]]; } m /= n; for (let i = 0; i < n; i++) v += (y[L[i]] - m) ** 2; v /= n - 1;
    S.classical.push([m, Math.sqrt(v / n)]);
    const fu = { finbert: [0, 0], qwen: [0, 0] }, nu = N - n;
    for (let i = 0; i < nu; i++) { const j = Math.floor(z.u() * N); for (const c in fu) { const f = PP.f[c][j]; fu[c][0] += f; fu[c][1] += f * f; } }
    for (const c in fu) {
      const mu = fu[c][0] / nu, vu = (fu[c][1] - nu * mu * mu) / (nu - 1); let rm = 0, rv = 0;
      for (let i = 0; i < n; i++) rm += PP.f[c][L[i]] - y[L[i]]; rm /= n; for (let i = 0; i < n; i++) rv += (PP.f[c][L[i]] - y[L[i]] - rm) ** 2; rv /= n - 1;
      S['ppi_' + c].push([mu - rm, Math.sqrt(vu / nu + rv / n)]);
      if (c === 'finbert') S.naive_finbert.push([mu, 0]);
    }
  }
  const res = { th, S };
  for (const k of ['classical', 'ppi_finbert', 'ppi_qwen']) res[k] = { cover: mean(S[k].map(([e, s]) => (Math.abs(e - th) <= zq * s ? 1 : 0))), width: mean(S[k].map(([, s]) => 2 * zq * s)) };
  return (ppCache[n] = res);
}
function ppi() {
  const n = PPI_N[+$('pp-n').value], R = D.ppi.res, ns = Object.keys(R.by_n).map(Number), S = ppiSim(n, 2000);
  $('pp-n-v').textContent = ints(n);
  const lab = { classical: 'Human labels only', ppi_finbert: 'PPI, FinBERT', ppi_qwen: 'PPI, Qwen2.5-7B' }, col = { classical: K.blue, ppi_finbert: K.green, ppi_qwen: K.red };
  const ks = Object.keys(lab), xax = AX('Human-labelled headlines n (log scale)', { type: 'log', tickvals: [50, 100, 200, 400, 800, 1600], tickangle: 0, range: [Math.log10(40), Math.log10(2000)] });
  const lines = (f, mult) => ks.map(k => ({ x: ns, y: ns.map(v => mult * R.by_n[v][k][f]), mode: 'lines+markers', name: lab[k], legendgroup: k, line: { color: col[k], width: 2 }, marker: { size: 7 }, hovertemplate: lab[k] + ', n = %{x}: %{y:.3f}<extra></extra>' }));
  const here = (f, mult) => ks.map(k => ({ x: [n], y: [mult * S[k][f]], mode: 'markers', name: 'Browser, n = ' + n, legendgroup: 'sim', showlegend: k === 'classical', marker: { color: col[k], size: 12, symbol: 'diamond-open', line: { width: 2 } }, hovertemplate: lab[k] + ', simulated: %{y:.3f}<extra></extra>' }));
  plot('pp-w', [...lines('width', 1), ...here('width', 1)], layout({ title: ttl('Mean width of the 95% CI'), legend: BOT(-0.22), xaxis: xax, yaxis: AX('Width') }));
  plot('pp-c', [...lines('cover', 100), ...here('cover', 100)], layout({ title: ttl('Coverage of the 95% CI (%)'), legend: BOT(-0.22), shapes: [hline(95, K.navy, 'dash')], xaxis: xax, yaxis: AX('Coverage (%)', { range: [85, 100] }) }));
  const hist = (k, name, c) => ({ x: S.S[k].map(v => v[0]), type: 'histogram', histnorm: 'probability density', xbins: { start: -0.4, end: 0.4, size: 0.005 }, name, opacity: 0.55, marker: { color: c }, hovertemplate: name + ' %{x}: %{y:.1f}<extra></extra>' });
  plot('pp-h', [hist('classical', 'Human labels only', K.blue), hist('ppi_finbert', 'PPI with FinBERT', K.green), hist('naive_finbert', 'Mean of the FinBERT scores', K.amber)],
    layout({ barmode: 'overlay', bargap: 0, legend: BOT(-0.2), margin: { l: 56, r: 12, t: 50, b: 40 }, title: ttl(`Estimates of θ, n = ${n}, 2,000 replications`), shapes: [vline(S.th, K.navy, 'dash')],
      annotations: [{ x: S.th, y: 0.97, yref: 'paper', text: ' θ = ' + S.th.toFixed(3), showarrow: false, xanchor: 'left', yanchor: 'top', font: { size: 11 } }], xaxis: AX('Estimate of the mean human tone', { range: [-0.15, 0.25] }), yaxis: AX('Density') }));
  const lec = R.by_n[n];
  out('pp-out', [T.pp1(n, nf(S.classical.width, 3), nf(S.ppi_finbert.width, 3), nf(S.ppi_qwen.width, 3), pct(S.classical.cover, 1), pct(S.ppi_finbert.cover, 1), pct(S.ppi_qwen.cover, 1)),
    lec ? T.pp2(n, nf(lec.classical.width, 3), nf(lec.ppi_finbert.width, 3), pct(lec.ppi_finbert.cover, 1)) : T.pp3(nf(R.naive.finbert, 3), nf(R.naive.qwen, 3), nf(R.theta, 3))]);
}

// ================================================================= 11. models in Lopez-Lira and Tang (2026)
function lltModels() {
  const h = +$('lt-h').value, L = D.llt, ord = L.models.map((_, i) => i).reverse(), names = ord.map(i => L.models[i]), on = ord.map(i => 100 * L.hit_r[i] > h);
  $('lt-h-v').textContent = h + '%';
  const op = on.map(b => (b ? 1 : 0.25));
  plot('lt-hit', [
    { y: names, x: ord.map(i => 100 * L.hit_d[i]), type: 'bar', orientation: 'h', name: 'Hit rate, drift', marker: { color: K.orange, opacity: op }, hovertemplate: '%{y}: %{x:.0f}%<extra></extra>' },
    { y: names, x: ord.map(i => 100 * L.hit_r[i]), type: 'bar', orientation: 'h', name: 'Hit rate, initial reaction', marker: { color: K.blue, opacity: op }, hovertemplate: '%{y}: %{x:.0f}%<extra></extra>' }
  ], layout({ barmode: 'group', bargap: 0.2, legend: Object.assign(BOT(-0.2), { traceorder: 'reversed' }), title: ttl('Does the long-short portfolio point the right way?'), margin: { l: 82, r: 12, t: 30, b: 40 },
    shapes: [vline(50, K.navy, 'dash'), vline(h, K.purple, 'dot')], xaxis: AX('Hit rate: share of days with a positive return (%)', { range: [40, 100] }), yaxis: AX('', { type: 'category' }) }));
  const sr = ord.map(i => L.sr[i]);
  plot('lt-sr', [{ y: names, x: sr, type: 'bar', orientation: 'h', marker: { color: sr.map(v => (v > 0 ? K.green : K.red)), opacity: op }, text: sr.map(v => v.toFixed(2)), textposition: 'outside', cliponaxis: false,
    showlegend: false, hovertemplate: '%{y}: Sharpe %{x:.2f}<extra></extra>' }],
  layout({ title: ttl('Is the drift profitable?'), margin: { l: 82, r: 12, t: 30, b: 40 }, shapes: [vline(0, K.navy)], xaxis: AX('Annualised Sharpe ratio of the drift', { range: [-1.4, 3.6] }), yaxis: AX('', { type: 'category' }) }));
  const a = ord.filter((_, j) => on[j]).map(i => L.sr[i]), b = ord.filter((_, j) => !on[j]).map(i => L.sr[i]);
  out('lt-out', [T.lt(a.length, h, a.length ? nf(median(a), 2) : '—', b.length ? nf(median(b), 2) : '—', b.length)]);
}

// ================================================================= 11b. Garcia, Hu and Rohrer (2023) on the FNSPID headlines
function colourWords() {
  const c = +$('cw-c').value, C = D.colour, R = C.by_cut[String(c)];
  $('cw-c-v').textContent = c + '%';
  const sp = [['lm_all', 'LM, all words', K.orange], ['lm_only', 'LM words not in ML', K.orange], ['ml_only', 'ML words not in LM', K.teal],
    ['overlap', 'Words in LM and ML', K.teal], ['joint', 'All three lists', K.teal], ['finbert', 'FinBERT', K.blue], ['qwen', 'Qwen2.5-7B', K.blue]].reverse();
  const v = sp.map(([k]) => 100 * R.r2[k]);
  plot('cw-r2', [{ y: sp.map(x => x[1]), x: v, type: 'bar', orientation: 'h', marker: { color: sp.map(x => x[2]) }, text: v.map(x => x.toFixed(2)), textposition: 'outside',
    cliponaxis: false, showlegend: false, hovertemplate: '%{y}: R² = %{x:.2f}%<extra></extra>' }],
  layout({ title: ttl('How much of the 4-day return is explained?'), margin: { l: 130, r: 20, t: 30, b: 40 }, xaxis: AX('R² on the 2020–2023 test texts (%)', { range: [0, 2.2] }),
    yaxis: AX('', { type: 'category' }) }));
  const g = [['lm_only', 'LM not in ML'], ['ml_only', 'ML not in LM'], ['overlap', 'LM and ML']];
  const tr = [[0, 'Positive words (95% CI, Driscoll-Kraay)', K.green], [1, 'Negative words (95% CI, Driscoll-Kraay)', K.red]].map(([j, name, col]) => ({
    x: g.map(x => x[1]), y: g.map(([k]) => R.b[k][j]), type: 'bar', name, marker: { color: col },
    error_y: { type: 'data', array: g.map(([k]) => (R.se[k][j] == null ? 0 : 1.96 * R.se[k][j])), color: K.navy, thickness: 1.2, width: 4 },
    hovertemplate: '%{x}: %{y:.3f}%<extra></extra>' }));
  plot('cw-b', tr, layout({ barmode: 'group', legend: BOT(-0.15), title: ttl('Positive and negative lists'), shapes: [hline(0, K.navy)],
    xaxis: AX(''), yaxis: AX('Excess return per 1 s.d. of the word share (%)', { range: [-0.45, 0.5] }) }));
  const bt = R.boot['ml_only-lm_all'];
  const top = c >= 95 ? 101 : c + 5, adm = C.dplus.filter(([, d]) => Math.abs(d) >= c && Math.abs(d) < top);
  const ap = adm.filter(([, d]) => d > 0).slice(-6).map(x => x[0]), an = adm.filter(([, d]) => d < 0).slice(0, 6).map(x => x[0]);
  out('cw-out', [T.cw1(c, R.n_ml_pos, R.n_ml_neg, R.n_ov_pos, R.n_ov_neg),
    T.cw2(nf(100 * R.r2.lm_all, 2), nf(100 * R.r2.ml_only, 2), nf(bt.diff, 2), nf(bt.lo, 2), nf(bt.hi, 2), nf(100 * R.r2.qwen, 2)),
    T.cw3(c, Math.min(top, 100), ap.join(', ') || '—', an.join(', ') || '—')]);
}

// ================================================================= 12. specification curve
let SPEC = null;
function specSeries() {                  // valid_inference.spec_curve: the 36 daily series, indexed by the signal day
  const S = D.spec, nd = PN.nd, X = [], lags = Object.values(S.hold);
  for (const m of S.meta) {
    const lag = m.day, x = PN[m.score], r = PN.r[lag], s = new Float64Array(nd), cnt = new Uint16Array(nd);
    for (let i = 0; i < PN.n; i++) { if (!(Math.abs(x[i]) > m.band)) continue; const d = PN.day[i]; if (d + lag >= nd) continue; s[d] += sgn(x[i]) * r[i]; cnt[d]++; }
    for (let d = 0; d < nd; d++) if (cnt[d]) s[d] /= cnt[d];
    X.push(s);
  }
  return { X, t: X.map(s => nwT(s)[1]), null: [], lags };
}
function specNull(B) {
  const nd = PN.nd, X = SPEC.X, blk = D.spec.block, z = SPEC.z || (SPEC.z = rng(15)), w = new Float64Array(nd), y = new Float64Array(nd);
  while (SPEC.null.length < B) {
    for (let b = 0; b < Math.ceil(nd / blk); b++) { const v = z.u() < 0.5 ? -1 : 1; for (let j = b * blk; j < Math.min(nd, (b + 1) * blk); j++) w[j] = v; }
    const tb = X.map(x => { for (let i = 0; i < nd; i++) y[i] = x[i] * w[i]; return nwT(y, nd)[1]; });
    SPEC.null.push(tb);
  }
}
function specCurve() {
  if (!SPEC) SPEC = specSeries();
  const c = +$('sc-c').value, B = +$('sc-b').value, S = D.spec, t = SPEC.t, o = t.map((_, i) => i).sort((a, b) => t[a] - t[b]);
  $('sc-c-v').textContent = nf(c, 2); $('sc-b-v').textContent = ints(B);
  specNull(B);
  const lab = { lm: 'Loughran-McDonald', finbert: 'FinBERT', qwen: 'Qwen2.5-7B' };
  plot('sc-curve', SCORES.map(sc => { const k = o.map((i, j) => [i, j]).filter(([i]) => S.meta[i].score === sc);
    return { x: k.map(([, j]) => j), y: k.map(([i]) => t[i]), mode: 'markers', name: lab[sc], marker: { color: SCORE_COL[sc], size: 9 },
      customdata: k.map(([i]) => [S.meta[i].band, S.meta[i].day]), hovertemplate: lab[sc] + ', |score| > %{customdata[0]}, day d+%{customdata[1]}: t = %{y:.2f}<extra></extra>' }; }),
  layout({ legend: BOT(-0.2), shapes: [hline(c, K.navy, 'dash'), hline(-c, K.navy, 'dash'), hline(0, K.navy)], xaxis: AX('36 specifications, sorted by t (score x threshold x holding day)'), yaxis: AX('Newey-West t, mean daily return') }));
  const nb = SPEC.null.slice(0, B), kObs = t.filter(v => v > c).length, mObs = median(t);
  const cnt = nb.map(v => v.filter(x => x > c).length), med = nb.map(v => median(v));
  plot('sc-null', [{ x: cnt, type: 'histogram', xbins: { start: -0.5, end: 36.5, size: 1 }, name: 'Sign-flip draws', marker: { color: K.band, line: { color: K.blue, width: 1 } }, hovertemplate: '%{x} specifications: %{y} draws<extra></extra>' }],
    layout({ showlegend: false, bargap: 0.05, title: ttl(`Joint null, ${B.toLocaleString('en-US')} sign-flip draws in blocks of ${S.block} days`), shapes: [vline(kObs, K.red)],
      annotations: [{ x: kObs, y: 0.97, yref: 'paper', text: ' observed: ' + kObs, showarrow: false, xanchor: 'left', yanchor: 'top', font: { color: K.red, size: 11 } }],
      xaxis: AX(`Number of specifications with t > ${c.toFixed(2)}`, { range: [-0.5, 12.5] }), yaxis: AX('Draws') }));
  const two = t.filter(v => Math.abs(v) > c).length;
  out('sc-out', [T.sc1(nf(c, 2), two, kObs, nf(36 * 2 * (1 - ncdf(c)), 1), nf(S.case.bonf_crit, 2)),
    T.sc2(B, kObs, nf(mean(cnt.map(v => (v >= kObs ? 1 : 0))), 3), nf(mObs, 2), nf(mean(med.map(v => (v >= mObs ? 1 : 0))), 3), nf(S.p_count, 3), nf(S.p_median, 3))]);
}

// ================================================================= wiring
function init() {
  const on = (ids, f) => ids.forEach(id => $(id).addEventListener('input', f));
  const players = {}, P = (btn, id, vals, ms) => (players[btn] = new Player(btn, $(id), vals, ms));
  on(['dw-l', 'dw-k'], dictWords); P('dw-play', 'dw-k', range(5, 30, 1), 300);
  on(['ac-m', 'ac-a'], accuracy); P('ac-play', 'ac-a', [0, 1, 2, 3], 1300);
  on(['ls-m', 'ls-p'], llmSize); P('ls-play', 'ls-p', [1, 2, 3], 1300);
  on(['em-t'], embeddings); P('em-play', 'em-t', range(0, 180, 5), 250);
  $('lc-k').max = D.lc.n.length - 1; on(['lc-k'], learningCurve); P('lc-play', 'lc-k', range(0, D.lc.n.length - 1, 1), 900);
  on(['ma-s', 'ma-m', 'ma-c'], memory); P('ma-play', 'ma-c', range(0, 1, 0.02), 160);
  on(['nh-o'], newsHours); P('nh-play', 'nh-o', range(-12, 12, 1), 350);
  on(['cn-n', 'cn-h'], contempNext); P('cn-play', 'cn-n', range(1, 20, 1), 600);
  $('sg-t').max = PN.nd - 1; $('sg-t').value = PN.nd - 1; on(['sg-l', 'sg-c', 'sg-t'], strategy); P('sg-play', 'sg-c', range(0, 10, 0.5), 300);
  on(['pp-n'], ppi); P('pp-play', 'pp-n', range(0, PPI_N.length - 1, 1), 1200);
  on(['lt-h'], lltModels); P('lt-play', 'lt-h', range(50, 95, 1), 200);
  on(['cw-c'], colourWords); P('cw-play', 'cw-c', range(50, 95, 5), 900);
  on(['sc-c', 'sc-b'], specCurve); P('sc-play', 'sc-b', range(100, 2000, 100), 500);
  const PFX = { 'dict-words': 'dw', 'accuracy': 'ac', 'llm-size': 'ls', 'embeddings': 'em', 'learning-curve': 'lc', 'memory': 'ma',
    'news-hours': 'nh', 'reaction': 'cn', 'strategy': 'sg', 'ppi': 'pp', 'llt-models': 'lt', 'colour-words': 'cw', 'spec-curve': 'sc' };
  // blocks whose initial live chart shows the answer: the charts are veiled with the slide and the readout
  const VEIL_CHART = new Set(['dict-words', 'accuracy', 'learning-curve', 'reaction', 'strategy', 'spec-curve']);
  if (T.predict && predict) Object.entries(T.predict).forEach(([b, sp]) =>
    predict(b, Object.assign({ player: players[PFX[b] + '-play'], veil: { out: true, charts: VEIL_CHART.has(b) } }, sp)));
  if (T.ticket && exitTicket) exitTicket(T.ticket);
  dictWords(); accuracy(); llmSize(); embeddings(); learningCurve(); memory(); newsHours(); contempNext(); strategy(); ppi(); lltModels(); colourWords(); specCurve();
}
window.CH15 = { PN, TX, clusterOLS, stratGross, nwT, sharpeD, aucOf, specSeries, ppiSim, evalSet, f1Macro, accOf, mcnemarP };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

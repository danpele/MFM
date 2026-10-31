// Shared helpers of the interactive chapter pages (MFM). Exposed as window.MFMI.
(function () {
'use strict';
const LANG = window.MFM_LANG === 'ro' ? 'ro' : 'en';
const C = { blue: '#2D5BA8', red: '#CD0000', amber: '#B5853F', green: '#2E7D32', navy: '#1F2A44', band: '#C5D2E8', grid: '#E3E9F4' };
const PLAY = LANG === 'ro' ? ['Pornește', 'Pauză'] : ['Play', 'Pause'];
// ---------------------------------------------------------------- linear algebra
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const mv = (M, v) => M.map(r => dot(r, v));
const quad = (w, S) => dot(w, mv(S, w));
const scale = (M, k) => M.map(r => r.map(x => x * k));
const sum = a => a.reduce((s, x) => s + x, 0);
const sub = (S, idx) => idx.map(i => idx.map(j => S[i][j]));
function solve(A, b) {
  const n = b.length, M = A.map((r, i) => [...r, b[i]]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    for (let r = c + 1; r < n; r++) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
  }
  const x = new Array(n).fill(0);
  for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / M[r][r]; }
  return x;
}
function chol(A) {
  const n = A.length, L = A.map(() => new Array(n).fill(0));
  for (let i = 0; i < n; i++) for (let j = 0; j <= i; j++) {
    let s = A[i][j]; for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k];
    L[i][j] = i === j ? Math.sqrt(Math.max(s, 1e-14)) : s / L[j][j];
  }
  return L;
}
function eigSym(A) {                // Jacobi rotations; eigenvalues in decreasing order
  const n = A.length, M = A.map(r => [...r]);
  for (let sweep = 0; sweep < 60; sweep++) {
    let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += M[i][j] * M[i][j];
    if (off < 1e-20) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      if (Math.abs(M[p][q]) < 1e-15) continue;
      const th = (M[q][q] - M[p][p]) / (2 * M[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1));
      const c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < n; k++) { const a = M[k][p], b = M[k][q]; M[k][p] = c * a - s * b; M[k][q] = s * a + c * b; }
      for (let k = 0; k < n; k++) { const a = M[p][k], b = M[q][k]; M[p][k] = c * a - s * b; M[q][k] = s * a + c * b; }
    }
  }
  return M.map((r, i) => r[i]).sort((a, b) => b - a);
}
const cov2corr = S => S.map((r, i) => r.map((v, j) => v / Math.sqrt(S[i][i] * S[j][j])));

// ---------------------------------------------------------------- portfolio rules
const wEW = n => new Array(n).fill(1 / n);
function wTan(mu, S) { const x = solve(S, mu), s = sum(x); return x.map(v => v / s); }
function wGMV(S) { const x = solve(S, S.map(() => 1)), s = sum(x); return x.map(v => v / s); }
function projSimplex(v) {
  const u = [...v].sort((a, b) => b - a); let css = 0, theta = 0;
  for (let i = 0; i < u.length; i++) { css += u[i]; const t = (css - 1) / (i + 1); if (u[i] - t > 0) theta = t; }
  return v.map(x => Math.max(x - theta, 0));
}
const trace = S => S.reduce((s, r, i) => s + r[i], 0);
function wLOmv(mu, S, lam, w0) {    // max mu'w - lam/2 w'Sw with w >= 0, sum w = 1 (projected gradient)
  let w = w0 ? [...w0] : wEW(mu.length);
  const eta = 1 / (lam * trace(S) + 1e-12);
  for (let it = 0; it < 3000; it++) {
    const g = mv(S, w), w1 = projSimplex(w.map((x, i) => x + eta * (mu[i] - lam * g[i])));
    let d = 0; for (let i = 0; i < w.length; i++) d += Math.abs(w1[i] - w[i]);
    w = w1; if (d < 1e-11) break;
  }
  return w;
}
const wGMVLO = S => wLOmv(S.map(() => 0), S, 1);
function wTanLO(mu, S) {
  let best = null, w = null;
  for (let k = 0; k <= 160; k++) {
    w = wLOmv(mu, S, Math.pow(10, -1 + 4 * k / 160), w);
    const sr = dot(w, mu) / Math.sqrt(quad(w, S));
    if (!best || sr > best.sr) best = { sr, w: [...w] };
  }
  return best.w;
}
function ercStep(w, S) { const m = mv(S, w), x = w.map((wi, i) => Math.sqrt(wi / m[i])), s = sum(x); return w.map((wi, i) => 0.5 * wi + 0.5 * x[i] / s); }
function wERC(S) { let w = wEW(S.length); for (let it = 0; it < 2000; it++) w = ercStep(w, S); return w; }
function riskContrib(w, S) { const m = mv(S, w), v = dot(w, m); return w.map((wi, i) => wi * m[i] / v); }
function frontierUnc(mu, S, targets) {
  const Si1 = solve(S, S.map(() => 1)), Sim = solve(S, mu);
  const A = sum(Si1), B = sum(Sim), Cc = dot(mu, Sim), Dd = A * Cc - B * B;
  return targets.map(m => Math.sqrt(Math.max((A * m * m - 2 * B * m + Cc) / Dd, 0)));
}
function leaves(Z, n) {             // left-to-right leaf order of a scipy linkage matrix
  const walk = k => (k < n ? [k] : [...walk(Z[k - n][0]), ...walk(Z[k - n][1])]);
  return walk(n + Z.length - 1);
}
function hrpLevels(S, order) {      // weights after each level of the recursive bisection
  const n = S.length, w = new Array(n).fill(1), res = [];
  const cvar = idx => { const s = sub(S, idx), iv = s.map((r, i) => 1 / r[i]), t = sum(iv); return quad(iv.map(x => x / t), s); };
  let clusters = [order];
  while (clusters.some(c => c.length > 1)) {
    const nxt = [];
    for (const c of clusters) {
      if (c.length < 2) { nxt.push(c); continue; }
      const h = c.length >> 1, a = c.slice(0, h), b = c.slice(h), va = cvar(a), vb = cvar(b), al = 1 - va / (va + vb);
      a.forEach(i => (w[i] *= al)); b.forEach(i => (w[i] *= 1 - al)); nxt.push(a, b);
    }
    clusters = nxt;
    const s = sum(w); res.push({ w: w.map(x => x / s), clusters: clusters.map(c => [...c]) });
  }
  return res;
}

// ---------------------------------------------------------------- random numbers (seeded)
function rng(seed) {
  let a = seed >>> 0;
  const u = () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  let spare = null;
  const z = () => {
    if (spare !== null) { const s = spare; spare = null; return s; }
    let x, y, r; do { x = 2 * u() - 1; y = 2 * u() - 1; r = x * x + y * y; } while (r >= 1 || r === 0);
    const f = Math.sqrt(-2 * Math.log(r) / r); spare = y * f; return x * f;
  };
  z.u = u;
  return z;
}
function sampleMoments(mu, L, T, z) {   // T Normal draws with mean mu and Cholesky factor L
  const n = mu.length, m = new Array(n).fill(0), X = [];
  for (let t = 0; t < T; t++) { const e = Array.from({ length: n }, z), x = mu.map((v, i) => v + dot(L[i], e)); X.push(x); for (let i = 0; i < n; i++) m[i] += x[i] / T; }
  const S = m.map(() => new Array(n).fill(0));
  for (const x of X) for (let i = 0; i < n; i++) { const di = x[i] - m[i]; for (let j = 0; j <= i; j++) S[i][j] += di * (x[j] - m[j]) / (T - 1); }
  for (let i = 0; i < n; i++) for (let j = 0; j < i; j++) S[j][i] = S[i][j];
  return { m, S };
}
const median = a => { const b = [...a].sort((x, y) => x - y); return (b[(b.length - 1) >> 1] + b[b.length >> 1]) / 2; };
const mean = a => sum(a) / a.length;
const sdev = a => { const m = mean(a); return Math.sqrt(sum(a.map(x => (x - m) ** 2)) / (a.length - 1)); };
const sharpe = a => mean(a) / sdev(a) * Math.sqrt(12);

// ---------------------------------------------------------------- formatting and charts
const nf = (x, d = 1) => { const s = x.toFixed(d).replace('-', '−'); return LANG === 'ro' ? s.replace('.', ',') : s; };
const pct = (x, d = 1) => nf(100 * x, d) + '%';
const $ = id => document.getElementById(id);
const AX = (title, extra) => Object.assign({ title: { text: title, font: { size: 12, color: C.navy } }, gridcolor: C.grid, zerolinecolor: C.band, color: C.navy, tickfont: { size: 11, color: C.navy }, automargin: true }, extra || {});
function layout(extra) {
  return Object.assign({
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, system-ui, sans-serif', color: C.navy, size: 12 },
    margin: { l: 56, r: 12, t: 30, b: 40 },
    legend: { orientation: 'h', x: 0, xanchor: 'left', y: -0.2, yanchor: 'top', bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } },
    hoverlabel: { bgcolor: '#fff', bordercolor: C.navy, font: { color: C.navy, family: 'Inter, sans-serif' } },
    hovermode: 'closest'
  }, extra || {});
}
const ttl = s => ({ text: s, x: 0, xanchor: 'left', font: { size: 12, color: C.navy } });
const CFG = { displayModeBar: false, responsive: true };
const plot = (id, tr, lay) => Plotly.react(id, tr, lay, CFG);
const out = (id, items) => { $(id).innerHTML = items.map(s => `<li>${s}</li>`).join(''); };
const vline = (x, color, dash) => ({ type: 'line', xref: 'x', yref: 'paper', x0: x, x1: x, y0: 0, y1: 1, line: { color, width: 2, dash: dash || 'solid' } });
const hline = (y, color, dash) => ({ type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: y, y1: y, line: { color, width: 2, dash: dash || 'solid' } });

// ---------------------------------------------------------------- play buttons
class Player {
  constructor(id, input, values, ms) { this.b = $(id); this.input = input; this.values = values; this.ms = ms; this.timer = null; this.b.addEventListener('click', () => this.toggle()); this.label(); }
  label() { this.b.textContent = this.timer ? '⏸ ' + PLAY[1] : '▶ ' + PLAY[0]; }
  toggle() { this.timer ? this.stop() : this.start(); }
  start() {
    const el = this.input, cur = this.values.findIndex(v => +v >= +el.value - 1e-9);
    let i = cur >= 0 && cur < this.values.length - 1 ? cur + 1 : 0;
    this.timer = setInterval(() => {
      el.value = this.values[i]; el.dispatchEvent(new Event('input'));
      if (++i >= this.values.length) { this.stop(); if (typeof this.onEnd === 'function') this.onEnd(); }
    }, this.ms);
    this.label();
  }
  stop() { clearInterval(this.timer); this.timer = null; this.label(); }
}
const range = (a, b, st) => { const r = []; for (let x = a; st > 0 ? x <= b + 1e-9 : x >= b - 1e-9; x += st) r.push(+x.toFixed(6)); return r; };

// ---------------------------------------------------------------- opt-in: predict, then check (per block) and exit ticket
// Pages that do not call predict() or exitTicket() are unchanged.
const UI = LANG === 'ro'
  ? { pick: 'Ce credeți? Alegeți o variantă:', check: 'Verifică', right: 'Corect.', wrong: 'Nu: varianta corectă este marcată.', checkAll: 'Verifică răspunsurile',
      score: (k, n) => `${k} din ${n} răspunsuri corecte.`, none: 'Fără răspuns.', ok: 'Corect', bad: 'Greșit', title: 'Verifică-te',
      show: 'Arată slide-ul', hidden: 'Rezultatul apare după „Verifică”, după ▶ sau cînd modificați parametrii.' }
  : { pick: 'What do you think? Pick an option:', check: 'Check', right: 'Correct.', wrong: 'No: the correct option is marked.', checkAll: 'Check answers',
      score: (k, n) => `${k} of ${n} answers correct.`, none: 'No answer.', ok: 'Correct', bad: 'Wrong', title: 'Check Yourself',
      show: 'Show slide', hidden: 'The result appears after “Check”, after ▶, or when you change the parameters.' };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
// Opt-in veil of a block: the slide image is blurred under a „Arată slide-ul” / "Show slide" button and, with { out: true },
// the readout of the live figure is blurred too; with { charts: true } (all .chart divs of the block) or { charts: [ids] } the
// live charts are blurred and made inert (no hover), for questions whose answer the initial chart shows. Returns reveal(),
// which removes all of it. A trusted (user) input in the block's controls reveals the readout and the charts only, since they
// then describe the reader's own choice.
function veil(blk, opt) {
  const fig = blk.querySelector('figure.slide'), outs = opt && opt.out ? [...blk.querySelectorAll('.out')] : [];
  const cs = !opt || !opt.charts ? [] : Array.isArray(opt.charts) ? opt.charts.map(id => $(id)).filter(e => e && blk.contains(e))
    : [...blk.querySelectorAll('.chart')];
  if (!fig && !outs.length && !cs.length) return () => {};
  const a = fig && fig.querySelector('a'), b = document.createElement('button');
  if (fig) {
    fig.classList.add('veiled');
    b.type = 'button'; b.className = 'btn play veil-btn'; b.textContent = UI.show;
    fig.appendChild(b);
    if (a) { a.setAttribute('tabindex', '-1'); a.setAttribute('aria-hidden', 'true'); }
  }
  const showOut = () => {
    outs.forEach(o => { o.classList.remove('veiled-out'); o.removeAttribute('title'); });
    cs.forEach(c => { c.classList.remove('veiled-chart'); c.removeAttribute('aria-hidden'); c.removeAttribute('title'); });
  };
  outs.forEach(o => { o.classList.add('veiled-out'); o.title = UI.hidden; });
  cs.forEach(c => { c.classList.add('veiled-chart'); c.setAttribute('aria-hidden', 'true'); c.title = UI.hidden; });
  let on = true;
  const reveal = () => {
    showOut(); if (!on) return; on = false;
    if (fig) { fig.classList.remove('veiled'); b.remove(); if (a) { a.removeAttribute('tabindex'); a.removeAttribute('aria-hidden'); } }
  };
  b.addEventListener('click', () => { reveal(); if (a) a.focus(); });
  const ctls = blk.querySelector('.ctls');
  if (ctls && (outs.length || cs.length)) ['input', 'change'].forEach(ev => ctls.addEventListener(ev, e => { if (e.isTrusted) showOut(); }));
  return reveal;
}
// Deterministic shuffle of the options, seeded by a string, so the correct option does not sit at a predictable position;
// returns the options in display order and the display index of the key.
function shuffleOpts(seed, opts, key) {
  let h = 2166136261;
  for (const ch of String(seed)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
  const idx = opts.map((_, i) => i);
  for (let i = idx.length - 1; i > 0; i--) { h = Math.imul(h ^ (h >>> 15), 2246822519) >>> 0; const j = h % (i + 1); [idx[i], idx[j]] = [idx[j], idx[i]]; }
  return { opts: idx.map(i => opts[i]), key: idx.indexOf(key) };
}
// spec: { opts: [text, ...], key: index of the correct option, player: Player (optional),
//         veil: true | { out: true, charts: true | [chart ids] } (optional: blur the slide, the readout with out: true and the
//         live charts with charts, until the reader presses „Arată slide-ul”, presses „Verifică” or runs ▶ to the end) };
//         options are shown in a fixed shuffled order
function predict(blockId, spec) {
  const blk = $(blockId), ask = blk && blk.querySelector('.ask'), det = blk && blk.querySelector('details');
  if (!ask || !spec || !spec.opts) return null;
  spec = Object.assign({}, spec, shuffleOpts('p:' + blockId, spec.opts, spec.key));
  const reveal = spec.veil ? veil(blk, spec.veil) : () => {};
  const nm = 'pred-' + blockId;
  const fs = document.createElement('fieldset'); fs.className = 'pred';
  fs.innerHTML = `<legend>${UI.pick}</legend>` + spec.opts.map((t, i) =>
    `<label class="pick"><input type="radio" name="${nm}" value="${i}"><span>${esc(t)}</span></label>`).join('') +
    `<div class="pred-act"><button class="btn" type="button">${UI.check}</button><span class="pred-res" role="status" aria-live="polite"></span></div>`;
  ask.appendChild(fs);
  const labels = [...fs.querySelectorAll('label.pick')], res = fs.querySelector('.pred-res');
  const chosen = () => { const r = fs.querySelector('input:checked'); return r ? +r.value : null; };
  const clear = () => { labels.forEach(l => l.classList.remove('ok', 'bad')); res.textContent = ''; res.className = 'pred-res'; };
  const check = () => {
    const c = chosen(); clear(); reveal();
    if (c !== null) {
      labels[spec.key].classList.add('ok');
      if (c !== spec.key) labels[c].classList.add('bad');
      res.textContent = c === spec.key ? UI.right : UI.wrong; res.classList.add(c === spec.key ? 'is-ok' : 'is-bad');
    }
    if (det) det.open = true;
  };
  fs.querySelector('button').addEventListener('click', check);
  fs.addEventListener('change', clear);
  if (spec.player) spec.player.onEnd = () => { reveal(); if (chosen() !== null) check(); };
  return { check, chosen, reveal };
}
// spec: { title (optional), id (default 'check'), store (localStorage key, optional),
//         qs: [{ q, key, opts: [{ t, why }, ...] }, ...] }; inserted before the page footnote (or at the end of <main>)
function exitTicket(spec) {
  const main = document.querySelector('main'); if (!main || !spec || !spec.qs) return null;
  const id = spec.id || 'check', title = spec.title || UI.title;
  spec = Object.assign({}, spec, { qs: spec.qs.map((q, k) => Object.assign({}, q, shuffleOpts(`t:${id}:${k}`, q.opts, q.key))) });
  const sec = document.createElement('section'); sec.className = 'ticket'; sec.id = id;
  sec.innerHTML = `<h2 class="sec">${esc(title)}</h2><ol class="tq">` + spec.qs.map((q, k) =>
    `<li><fieldset><legend>${esc(q.q)}</legend>` + q.opts.map((o, i) =>
      `<label class="pick"><input type="radio" name="${id}-q${k}" value="${i}"><span>${esc(o.t)}<span class="why" hidden></span></span></label>`).join('') +
    `</fieldset></li>`).join('') + `</ol><div class="pred-act"><button class="btn play" type="button">${UI.checkAll}</button><span class="pred-res" role="status" aria-live="polite"></span></div>`;
  const foot = main.querySelector('.src.foot');
  foot ? main.insertBefore(sec, foot) : main.appendChild(sec);
  const toc = main.querySelector('.toc');
  if (toc && !toc.querySelector(`a[href="#${id}"]`)) toc.insertAdjacentHTML('beforeend', `${toc.children.length ? ' · ' : ''}<a href="#${id}">${esc(title)}</a>`);
  const items = [...sec.querySelectorAll('ol.tq > li')], res = sec.querySelector('.pred-res');
  const save = () => { if (!spec.store) return; try { localStorage.setItem(spec.store, JSON.stringify(items.map(li => { const r = li.querySelector('input:checked'); return r ? +r.value : null; }))); } catch (e) { /* storage unavailable */ } };
  const clear = li => { li.querySelectorAll('label.pick').forEach(l => l.classList.remove('ok', 'bad', 'no', 'mine')); li.querySelectorAll('.why').forEach(w => { w.hidden = true; w.textContent = ''; }); };
  const check = () => {
    let n = 0;
    items.forEach((li, k) => {
      const q = spec.qs[k], r = li.querySelector('input:checked'), c = r ? +r.value : null;
      clear(li);
      li.querySelectorAll('label.pick').forEach((l, i) => {
        l.classList.add(i === q.key ? 'ok' : i === c ? 'bad' : 'no'); if (i === c) l.classList.add('mine');
        const w = l.querySelector('.why'); w.textContent = `${i === q.key ? UI.ok : UI.bad}. ${q.opts[i].why}`; w.hidden = false;
      });
      if (c === q.key) n++;
    });
    res.textContent = UI.score(n, items.length); res.className = 'pred-res';
  };
  sec.querySelector('button').addEventListener('click', check);
  items.forEach(li => li.addEventListener('change', () => { clear(li); res.textContent = ''; save(); }));
  if (spec.store) {
    try { const v = JSON.parse(localStorage.getItem(spec.store) || 'null'); if (Array.isArray(v)) v.forEach((c, k) => { const r = c !== null && items[k] && items[k].querySelectorAll('input')[c]; if (r) r.checked = true; }); } catch (e) { /* storage unavailable */ }
  }
  if (location.hash === '#' + id) sec.scrollIntoView();
  return { check };
}

window.MFMI = { LANG, C, dot, mv, quad, scale, sum, sub, solve, chol, eigSym, cov2corr, wEW, wTan, wGMV, projSimplex, trace, wLOmv, wGMVLO, wTanLO,
  ercStep, wERC, riskContrib, frontierUnc, leaves, hrpLevels, rng, sampleMoments, median, mean, sdev, sharpe, nf, pct, $, AX, layout, ttl, CFG, plot, out,
  vline, hline, Player, range, predict, exitTicket };
})();

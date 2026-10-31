// Web version of a lecture (web/chN.html): table of contents state, wide inline formulas, veil of the course text on prediction frames.
(function () {
'use strict';
const toc = document.getElementById('wtoc');
if (toc && window.innerWidth < 1000) toc.open = false;
// inline formulas wider than their line get their own horizontal scroll instead of widening the page
function fitMath() {
  document.querySelectorAll('.fbody mjx-container:not([display]), .ctext mjx-container:not([display])').forEach(m => {
    m.classList.remove('wide');
    const box = m.closest('li, p, td, th, .col, .col1, .bk-b, .fbody, .ctext');
    if (box && m.getBoundingClientRect().width > box.clientWidth - 4) m.classList.add('wide');
  });
}
window.addEventListener('mfm-mathjax', fitMath);
let rt = null;
window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(fitMath, 200); });
// highlight the current section in the table of contents
const links = [...document.querySelectorAll('.wtoc a')], heads = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
if ('IntersectionObserver' in window && heads.length) {
  const io = new IntersectionObserver(() => {
    let cur = null;
    for (const h of heads) if (h.getBoundingClientRect().top < 140) cur = h;
    links.forEach(a => a.classList.toggle('on', !!cur && a.getAttribute('href') === '#' + cur.id));
  }, { rootMargin: '0px 0px -60% 0px' });
  heads.forEach(h => io.observe(h));
}

// Course text that gives the answer to a block's prediction (article[data-pred] > .vgroup): blurred until the reader presses
// „Verifică”, runs ▶ to the end or presses „Arată textul”. interactive/common.js is not modified: the hooks are a document-level
// click listener on the Verifică button and a wrapper around Player.prototype.stop that detects the end of a run.
const SHOW = document.documentElement.lang === 'ro' ? 'Arată textul' : 'Show text';
function unveil(art) {
  const g = art && art.querySelector('.vgroup.veiled-t');
  if (!g) return;
  g.classList.remove('veiled-t');
  g.querySelectorAll('.ctext, .brief').forEach(e => e.removeAttribute('aria-hidden'));
  const b = g.querySelector('.veil-btn-t'); if (b) b.remove();
}
document.querySelectorAll('article.frame[data-pred] .vgroup').forEach(g => {
  if (!window.MFMI) return;                                   // without the interactive scripts the text stays visible
  g.classList.add('veiled-t');
  g.querySelectorAll('.ctext, .brief').forEach(e => e.setAttribute('aria-hidden', 'true'));
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'btn play veil-btn-t'; b.textContent = SHOW;
  b.addEventListener('click', () => unveil(g.closest('article')));
  g.prepend(b);
});
document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('fieldset.pred .pred-act button'); if (b) unveil(b.closest('article.frame')); });
const PL = window.MFMI && window.MFMI.Player;
if (PL && !PL.prototype.__webWrapped) {
  const stop = PL.prototype.stop;
  PL.prototype.stop = function () {
    const v = this.values, end = !!this.timer && v && v.length && Math.abs(+this.input.value - +v[v.length - 1]) < 1e-9;
    stop.call(this);
    if (end && this.b) unveil(this.b.closest('article.frame'));
  };
  PL.prototype.__webWrapped = true;
}
})();

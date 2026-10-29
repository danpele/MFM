// Readouts of the Chapter 17 interactive page, written by latex/build_interactive_ch17.py.
(function () {
const de = n => { const d = String(n).replace(/\D/g, ''), k = +d.slice(-2); return d !== '' && +d !== 0 && (k === 0 || k >= 20) ? ' de' : ''; };
const rel = (e, a, b) => `${Math.abs(e)}${de(e)} zile ${e < 0 ? a : b}`;
window.CH17_TEXT = {
 months: ['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sept.', 'oct.', 'nov.', 'dec.'],
 open: 'în curs', none: 'niciunul', rule: r => `(regula PSY, r₀ = ${r})`, allYears: 'toți anii', wildName: 'wild bootstrap', mcName: 'Monte Carlo',
 rb: (g, l, c, m) => `Cît supraviețuiește, bula crește cu ${g} pe perioadă; durata de viață așteptată: ${l} perioade. În cele 400 de perioade: ${c} colapsuri vizibile (bula peste 25 înainte de colaps); prețul a ajuns la cel mult ${m} ori valoarea fundamentală.`,
 ep: (h, a, la, b, lb, md) => `În primii ${h} ani după vîrf, cea mai mare scădere față de vîrf merge de la ${a} (${la}) la ${b} (${lb}); mediana celor nouă episoade este ${md}.`,
 ep1: (l, pk, ru, dh, h, d4) => `${l}: vîrf pe ${pk}, creștere de ${ru} în cei doi ani dinainte; scăderea maximă este ${dh} în ${h} ani și ${d4} în patru ani.`,
 gs: (c, p, lo, hi, n, u, p150, n150) => `Crah = o scădere de ${c} față de un maxim anterior în următorii 2 ani. După o creștere de peste 100%: ${p} (CI de 95% [${lo}, ${hi}], n = ${n}), față de ${u} pentru toate lunile-industrie. După o creștere de peste 150%: ${p150} (n = ${n150}).`,
 wi: (t, r, w, s, g) => `T = ${t}, r₀ = ${r}: fereastra minimă are ${w} observații; SADF parcurge ${s}${de(s)} ferestre, GSADF ${g}${de(g)} ferestre.`,
 wi2: (r, w, g) => `Regula PSY pentru acest T: r₀ = 0,01 + 1,8/√T = ${r}, adică w₀ = ${w} și ${g}${de(g)} ferestre GSADF.`,
 nu: (w, a, s, g, n) => `w₀ = ${w}: valorile critice de 95% sînt ${a} (ADF), ${s} (SADF) și ${g} (GSADF); GSADF parcurge ${n}${de(n)} ferestre.`,
 nu2: (w, r) => `Regula PSY pentru T = 440: w₀ = ${w} (r₀ = ${r}), valoarea din curs.`,
 before: d => `${d}: înainte de prima fereastră completă, BSADF nu este încă definit.`,
 below: (d, v, c) => `${d}: BSADF = ${v}, sub valoarea critică ${c}.`,
 above: (d, v, c, m, ok) => `${d}: BSADF = ${v}, peste valoarea critică ${c}, a ${m}-a dată consecutiv; ${ok ? 'episod confirmat în timp real' : 'episodul nu este încă confirmat'}.`,
 eps: (L, k, l, f, ratio) => `Episoade cu cel puțin ${L} depășiri consecutive, cu datele disponibile pînă la cursor: ${k} (${l})${f ? `; ${f} cu ${ratio ? 'raportul' : 'prețul'} în scădere` : ''}.`,
 cond: { B: 'B < 0', m: 'm în [0,01; 0,99]', w: 'ω în [2, 25]', tc: 't<sub>c</sub> în [t₂, t₂ + (t₂ − t₁)/5]', osc: 'cel puțin 2,5 oscilații', damping: 'amortizarea ≥ 1', rel_err: 'eroarea relativă maximă ≤ 0,15', lomb: 'testul Lomb la 10%', ar1: 'rădăcina unitară a reziduului respinsă la 10%' },
 pd: (g, c, c99) => `Întregul eșantion: GSADF = ${g}, față de valorile critice ${c} (95%) și ${c99} (99%).`,
 bt: (g, c, n) => `Întregul eșantion: GSADF = ${g}, față de valoarea critică de 95% ${c} (${n}).`,
 fw: (t, l, q, k, ls) => `Valoarea critică pe familie la ${l}% pentru ${t}${de(t)} săptămîni: ${q}. Episoade peste ea: ${k} (${ls}).`,
 fw2: (m, a, e, lo, hi) => `Valorile critice punctuale Monte Carlo ajung la cel mult ${m}. Sub ipoteza nulă, ${a} dintre traiectorii au o depășire punctuală și ${e} un „episod”. Pe grila τ<sub>b</sub>, valoarea pe familie variază între ${lo} și ${hi}.`,
 lp: (t2, tc, e, m, w, b) => `Fereastra 1 ian. 2017–${t2}: t<sub>c</sub> estimat ${tc}, cu ${rel(e, 'înainte de', 'după')} vîrf; m = ${m}, ω = ${w}, B = ${b}.`,
 lp2: (q, f, r, o) => q ? `Ajustare calificată: trece toate condițiile.` : `Ajustare necalificată. Condiții încălcate: ${f || 'testul Lomb sau testul reziduului'}. Eroarea relativă maximă: ${r}; numărul de oscilații: ${o}.`,
 tc: (n, t1, t2, tc, e, k, mae, w, q) => `${n}, fereastra de la ${t1}: la t₂ = ${t2}, t<sub>c</sub> = ${tc}, cu ${rel(e, 'înainte de', 'după')} vîrf. Înainte de vîrf (${k}${de(k)} ajustări): eroarea absolută medie ${mae}${de(mae)} zile, ${w} la cel mult 30 de zile, ${q} calificate.`,
 ci: (h, f, n, k, a, b, c) => `Scădere de cel puțin ${f} în ${h} de zile: după ${a} din cele ${k}${de(k)} semnale și după ${b} din datele fără semnal; ${n}${de(n)} date evaluate, frecvența medie ${c}.`,
 ci2: (a, b, m, d) => `Indicatorul este pozitiv în ${a} din datele din 2017 și în ${b} din cele din 2021; maximul este ${m}, în ${d}.`,
 fl: (p, ra, rb, la, lb, qa, qb) => `${String(p).charAt(0).toUpperCase() + String(p).slice(1)}: eroarea relativă maximă ≤ 0,15 trece în ${ra} dintre ferestrele Bitcoin și ${rb} dintre cele Nasdaq 100; după testul Lomb rămîn ${la} și ${lb}; calificate (toate condițiile): ${qa} și ${qb}.`,
 ms: (p, d, s, s1) => `p₂₂ = ${p}: durata așteptată a regimului turbulent este ${d} săptămîni; volatilitatea lui este ${s}%, față de ${s1}% în regimul calm.`,
 ms2: (s, d, f) => `Probabilitatea netezită depășește 0,5 în ${s} dintre săptămîni; probabilitatea filtrată la ${d}: ${f}.`,
 ms3: (p, d, s) => `Estimările modelului: p₂₂ = ${p}, durata ${d} săptămîni, σ₂ = ${s}%.`,
 lrName: { btc_1v2: 'Bitcoin, un regim față de două', ndx_1v2: 'Nasdaq 100, un regim față de două', btc_2v3: 'Bitcoin, două regimuri față de trei' },
 lr: (n, l, b, q, m, p, c, df) => `${n}: LR = ${l}; cu primele ${b}${de(b)} replici, valoarea critică de 95% este ${q}, cea mai mare replică ${m}, p = ${p} (χ²${df === 4 ? '₄' : '₆'} naiv: ${c}).`,
 lr2: (b, p) => `Cu B = ${b}${de(b)} replici, cel mai mic p-value posibil este 1/(B + 1) = ${p}.`,
 aiName: { csco: 'Cisco', nvda: 'NVIDIA', ndx95: 'Nasdaq 100 (anii 1990)', ndx23: 'Nasdaq 100 (era AI)' },
 ai: (n, s, m, d, x, k, xk, past) => `${n}, semnal în ${s}: ${past ? `datele se opresc după ${m}${de(m)} luni (${d}), la` : `după ${m}${de(m)} luni (${d}),`} ${x} ori nivelul de la semnal; maximul pînă atunci, ${xk} ori, după ${k}${de(k)} luni.`,
 dz: (d, p, v, dv, pv, dp, pp, q, raw) => `Pînă în ${d}: vîrful volumului ${pv} în ${dv}, vîrful prețurilor ${pp} în ${dp}${q > 0 ? `; acalmie de ${q} luni` : ''}. În ${d}: prețuri ${p}, volum ${v}${raw ? ' (neajustat)' : ''}.`
};
})();

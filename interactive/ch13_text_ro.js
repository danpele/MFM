// Readouts of the Chapter 13 interactive page, written by latex/build_interactive_ch13.py.
const deRO = n => { const k = Math.round(Math.abs(+String(n).replace(/\D/g, ''))) % 100; return (k >= 20 || (k === 0 && +String(n).replace(/\D/g, '') > 0)) ? n + ' de' : String(n); };
window.CH13_TEXT = {
 play: 'Pornește', pause: 'Pauză',
 sn: (r1, nr, p, a1, a40, na, b) => `Randamente: ρ₁ = ${r1}; ${nr} din 40 de autocorelații ies din banda ±${b}. |r|${p}: ρ₁ = ${a1}, ρ₄₀ = ${a40}; ${na} din 40 ies din bandă.`,
 la1: (nz, p, f) => `${nz} din ${p} coeficienți sînt nenuli. Prima caracteristică care intră în model: ${f}.`,
 la2: p => `Ridge: toți cei ${p} coeficienți sînt nenuli și scad spre zero împreună.`,
 la3: (a, b) => `AUC în CV cu purjare (5 pliuri) la acest λ: ${a}; cel mai mare cu cel puțin o caracteristică în model: ${b}.`,
 ff: (d, k, s, c) => `d = ${d}: fereastră de ${k === 1 ? '1 lag' : deRO(k) + ' laguri'}, suma ponderilor ${s}, corelația cu log-prețul ${c}.`,
 ff2: (a1, r1, aa, l, ra, cr) => `ADF cu 1 lag: ${a1}, ${r1 ? 'respinge' : 'nu respinge'} la 5% (valoarea critică ${cr}). Cu ${deRO(l)} laguri alese prin AIC: ${aa}, ${ra ? 'respinge' : 'nu respinge'}.`,
 tb: (u, l, v, p, n) => `Prima barieră atinsă: superioară ${u}, inferioară ${l}, verticală ${v}. ${p} din ${n} etichete sînt +1.`,
 tbe: (d, lab, b, k) => `${d}: ${lab} (${({ upper: 'bariera superioară', lower: 'bariera inferioară', vertical: 'bariera verticală' })[b]}, după ${k === 1 ? '1 zi' : deRO(k) + ' zile'})`,
 tb2: s => s + '.',
 pc: (f, a, t, p, e) => `Pliul ${f}: ${deRO(a)} observații de antrenare, ${t} de test, ${p} purjate, ${e} sub embargo.`,
 pc2: (m, n) => `În medie, ${m} din ${deRO(n)} observații rămîn pentru antrenare.`,
 lk: (h, a, b, c) => `h = ${h === 1 ? '1 zi' : deRO(h) + ' zile'}: K-fold amestecat ${a}, K-fold contiguu ${b}, K-fold cu purjare și embargo ${c}. Acuratețea reală este 50%.`,
 mc: (s, b) => `Acuratețea medie pe pliuri: ${s}. Reperul „mereu în sus”: ${b}.`,
 mc2: (tp, fn, fp, tn, u, y) => `Logit, predicții agregate: TP = ${tp}, FN = ${fn}, FP = ${fp}, TN = ${tn}; „sus” este prezis în ${u} din zile și realizat în ${y}.`,
 wf: (s, b, e, k, c) => `Raportul Sharpe anualizat: strategia ${s}, buy-and-hold ${b}. Expunerea medie ${e}; ${deRO(k)} schimbări de poziție, fiecare cu un cost de ${c} bp.`,
 em: (n, t, m, s, k) => `N = ${n}: teorema dă ${t}, media simulărilor ${m}, abaterea standard ${s}. În ${k} din 200 de eșantioane cea mai bună strategie are SR peste 1.`,
 io: (f, s, b, a, o, r) => `Regula selectată: MA ${f}/${s}, banda ${b}%; SR ${a} in-sample și ${o} out-of-sample. Spearman ρ = ${r}.`,
 io2: (q, t, a, y, e) => `In-sample 15 mai 2015 – decembrie ${y - 1}, out-of-sample ${y}–${e}. SR median out-of-sample: ${t} pentru cele mai bune ${q}% in-sample, ${a} pentru toate regulile.`,
 vx: (l, a, b, r) => `HAC cu ${l} laguri: OLS doar cu VIX [${a}] bp, selecția dublă [${b}] bp; intervalul selecției duble este de ${r} ori mai larg.`,
 vx2: (a, b, k) => `Eroarea standard a selecției duble: ${a} bp cu aceste laguri, ${b} bp fără corecție HAC (zile tratate ca independente). ${k} din 5 intervale exclud zero.`,
 cp: (y, p, a, al, ah, b, bl, bh, m, se) => `Ponderi 1967–${y}, test ${p}, SR lunar: FF5 ${a} [${al}; ${ah}], FF3 ${b} [${bl}; ${bh}], piața ${m}. Eroarea standard a SR FF5: ${se}.`
};

// Readouts of the Chapter 9 interactive page, written by latex/build_interactive_ch9.py.
const CH9_ZILE = s => { const n = parseInt(String(s).replace(/\D/g, ''), 10), r = n % 100; return s + (n === 1 ? ' zi' : n > 0 && (r === 0 || r >= 20) ? ' de zile' : ' zile'); };
window.CH9_TEXT = {
 play: 'Pornește', pause: 'Pauză', rw: 'RV de ieri',
 fam: { 'HAR family (OLS)': 'familia HAR (OLS)', 'Penalised regression': 'regresie penalizată', 'Regression trees': 'arbori de regresie', 'Neural networks': 'rețele neuronale' },
 id: (t, rv, sh) => `Pînă la ${t}: RV cumulată ${rv} %², adică ${sh} din RV a zilei.`,
 id2: (d, rv, vol, mx, tm, sh, on, oc) => `${d}: RV = ${rv} %², volatilitatea anualizată √(252 × RV) = ${vol}. Cel mai mare randament de 5 minute, ${mx}, în intervalul care se încheie la ${tm}, aduce ${sh} din RV. Randamentul peste noapte: ${on}; de la deschidere la închidere: ${oc}.`,
 rs: (s, n, m, md, mx, dmx, k, mk) => `${s}, ${CH9_ZILE(n)}: volatilitatea din RV medie ${m} pe an, mediana zilnică ${md}, maximul ${mx} (${dmx}).` + (k ? ` Fără cele mai volatile ${CH9_ZILE(k)}: ${mk}.` : ''),
 on: (sh, cc, oc, onv, tot, lo, hi) => `Randamentele peste noapte aduc ${sh} din varianța zilnică SPY (între ${lo} și ${hi} pe perioadele din grafic). Volatilitatea anualizată: ${cc} de la închidere la închidere, ${oc} de la deschidere la închidere, ${onv} peste noapte; din varianța totală medie: ${tot}.`,
 on2: (c, v, cs) => `RV intraday înmulțită cu c = ${c}: volatilitatea anualizată ${v}. Factorul care egalează media varianței totale este c = ${cs}.`,
 sg: (s, v5, vm, lm, vl, ll, r1) => `${s}: ${v5} la 5 minute, ${vm} la ${lm} și ${vl} la ${ll} (media grilelor decalate). Autocorelația de ordinul 1 a randamentelor de 5 minute: ${r1}.`,
 sg2: (s, om, b, w, v) => `${s} cu zgomot ω = ${om}%: deplasarea la 5 minute este 2nω² = ${b} %² pe zi, iar volatilitatea crește de la ${v} la ${w}.`,
 jp: (s, n, N, sh, ex, js, mj) => `${s}: ${CH9_ZILE(n)} cu salt din ${N} (${sh}); fără salturi ar fi de așteptat ${ex} respingeri. Salturile reprezintă ${js} din varianța realizată totală; într-o zi cu salt, în medie ${mj} din RV a zilei.`,
 jp2: (a, c) => `Test unilateral la α = ${a}: valoarea critică pentru z este ${c}.`,
 jp3: a => `Benjamini–Hochberg: p-value-urile zilnice, 1 − Φ(z), se ordonează și se resping cele mai mici k, cu proporția așteptată de respingeri false cel mult ${a}.`,
 ds: (s, l, sk, ku, vs, vk) => `${s}, λ = ${l}: asimetria ${sk} și kurtosis-ul ${ku} (distribuția Normală: 0 și 3). Pentru RV pe niveluri: ${vs} și ${vk}.`,
 ds2: (s, uk, zk, sd) => `${s}: kurtosis-ul randamentelor scade de la ${uk} (împărțite la abaterea lor standard) la ${zk} (împărțite la √RV); abaterea standard după împărțirea la √RV: ${sd}.`,
 ac: (a1, a22, a100, s1, b7, b30) => `log RV, SPY: ${a1} la lagul 1, ${a22} la lagul 22, ${a100} la lagul 100. Randamentul zilnic la pătrat: ${s1} la lagul 1. Bitcoin: ${b7} la lagul 7, ${b30} la lagul 30 (ciclul săptămînal).`,
 ac2: (r, a22, a100) => `AR(1) cu ρ = ${r}: ${a22} la lagul 22 și ${a100} la lagul 100.`,
 ac3: (a1, a22, a100) => `log-HAR estimat pentru SPY, ca AR(22): ${a1} la lagul 1, ${a22} la lagul 22, ${a100} la lagul 100.`,
 vx: (h, n, mv, mf, sh, g, c) => `Orizontul de ${CH9_ZILE(h)} de tranzacționare, ${CH9_ZILE(n)} în eșantion: media VIX ${mv}, media volatilității realizate ulterior ${mf}. VIX este mai mare în ${sh} din zile, în medie cu ${g} puncte procentuale; corelația este ${c}.`,
 vx2: (d, v, f, g) => `${d}: VIX ${v}, volatilitatea realizată ulterior ${f}, diferența ${g} puncte procentuale.`,
 oo: (s, d0, n, L, list) => `${s}, din ${d0} (${CH9_ZILE(n)}), ${L} mediu: ${list}.`,
 oo2: (h, g, e, w) => `Testul DM față de log-HAR (t < 0 favorizează log-HAR): t = ${h} pentru HAR, ${g} pentru GARCH(1,1)-t, ${e} pentru EWMA, ${w} pentru RV de ieri.`,
 oo3: (d0, n, L, a, b, t) => `Bitcoin, din ${d0} (${CH9_ZILE(n)}): ${L} mediu ${a} pentru log-HAR și ${b} pentru GARCH(1,1)-t; t DM = ${t}.`,
 ro: (lo, hi, hs, hb, z2, f) => `Lagurile ${lo}–${hi}: Ĥ = ${hs} pentru SPY și ${hb} pentru Bitcoin (mișcarea browniană: 0,5). Pentru SPY ζ₂ = ${z2}, deci dublarea lui Δ înmulțește m(2, Δ) cu ${f}.`,
 cs: (m, f, a1, a2, a3, b1, b2, b3, r) => `${m} (${f}). MSE relativ la HAR, doar lagurile RV: ${a1} la o zi, ${a2} la o săptămînă, ${a3} la o lună. Cu toți cei 12 predictori: ${b1}, ${b2} și ${b3}; locul ${r} din 21 la o lună.`
};

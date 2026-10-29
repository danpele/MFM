// Readouts of the Chapter 15 interactive page, written by latex/build_interactive_ch15.py.
(function () {
const F = n => n.toLocaleString('en-US').replace(/,/g, ' ');
const de = n => (n % 100 >= 20 || (n >= 100 && n % 100 === 0) ? 'de ' : '');
const N = (n, w) => `${F(n)} ${de(n)}${w}`;
window.CH15_TEXT = {
 play: 'Pornește', pause: 'Pauză',
 agree: ['toate propozițiile', 'acord de cel puțin 66%', 'acord de cel puțin 75%', 'acord de 100%'],
 metric: { acc: 'acuratețea', f1: 'F1 macro' },
 best: { acc: 'cea mai mare acuratețe', f1: 'cel mai mare F1 macro' },
 dw1: (k, tot, s) => `Cele ${N(k, 'cuvinte')} apar în ${N(tot, 'propoziții')} (o propoziție este numărată pentru fiecare cuvînt al ei); ${s} dintre ele nu sînt etichetate negativ.`,
 dw2: (l, nl, ns, s) => `Lista are ${N(nl, 'cuvinte')}. ${F(ns)} ${de(ns)}propoziții conțin un cuvînt din listă și niciun cuvînt negativ ${l === 'gi' ? 'LM' : 'GI'}; ${s} dintre ele nu sînt etichetate negativ.`,
 ac1: (a, n, m, fb, q, b) => `PhraseBank, ${a} (n = ${n}): ${m} este ${fb} pentru FinBERT și ${q} pentru Qwen2.5-7B; reperul „mereu neutru” are ${b}.`,
 ac2: (m, best, v, gi, va, lm, b) => `Twitter: ${m} o are ${best}, ${v}. Dicționarele: GI ${gi}, VADER ${va}, LM ${lm}; reperul „mereu neutru”: ${b}.`,
 ls1: (p, m, a, b, c, fb) => `Twitter, prompt-ul P${p}: ${m} este ${a} pentru 1.5B, ${b} pentru 7B și ${c} pentru 14B; FinBERT are ${fb}.`,
 ls2: (neu, d, n01, n10, p) => `Modelul 1.5B răspunde „neutral” pentru ${neu} dintre titluri (66% sînt etichetate neutre). Acuratețea 7B minus acuratețea 1.5B: ${d} puncte procentuale; testul McNemar (${F(n01)} față de ${N(n10, 'titluri')}): p ${p}.`,
 em: (th, a, best, tb, lr) => `Direcția la ${th}° (0° este prima componentă principală): AUC pentru titlurile pozitive față de cele negative este ${a}. Cea mai bună direcție din acest plan, la ${tb}°, dă ${best}. Regresia logistică pe toate cele 384 de dimensiuni are acuratețea ${lr}.`,
 lc: (n, r, e, lo, hi, t, fb, q, first) => `${N(n, 'etichete')}: embeddings + LR ${e}${r > 1 ? ` (între ${lo} și ${hi} în cele ${r} eșantioane)` : ' (tot setul de antrenare)'}, TF-IDF + LR ${t}. FinBERT (${fb}) și Qwen2.5-7B (${q}) nu folosesc etichete Twitter; embeddings depășesc FinBERT de la ${N(first, 'etichete')}.`,
 ma1: (s, m, a, n1, b, n2) => `${s === 'monthly' ? 'S&P 500, lunile' : 'Apple, zilele'}, Qwen2.5-${m}: AUC ${a} înainte de publicarea ponderilor (${N(n1, s === 'monthly' ? 'luni' : 'zile')}) și ${b} după (${N(n2, s === 'monthly' ? 'luni' : 'zile')}).`,
 ma2: (c, tpr, fpr, b1, b2) => `Regula „creștere dacă P(creștere) > ${c}”, înainte de publicare: ${tpr} dintre creșteri și ${fpr} dintre scăderi sînt numite creșteri. Acuratețea echilibrată: ${b1} înainte și ${b2} după publicare.`,
 nh: (s, lab, hh, prev, other) => `${s} dintre titluri au marcajul 00:00 UTC, adică doar data publicării. Pe ceasul ${lab}, acest marcaj apare ca ${hh}:00${prev ? ' din ziua calendaristică anterioară' : ''}, care nu este ora la care a apărut știrea. Doar ${N(other, 'titluri')} au un alt marcaj.`,
 cn1: (m, n, fb, tf, q, tq, l, tl) => `Zile-acțiune cu cel puțin ${m === 1 ? 'un titlu' : N(m, 'titluri')}: ${F(n)}. Ziua d: FinBERT ${fb} bp (t = ${tf}), Qwen ${q} bp (t = ${tq}), LM ${l} bp (t = ${tl}).`,
 cn2: (fb, tf, q, tq, l, tl) => `Ziua d+2: FinBERT ${fb} bp (t = ${tf}), Qwen ${q} bp (t = ${tq}), LM ${l} bp (t = ${tl}).`,
 sg1: (lag, d, mu, t, sr, c, srn, be) => `Qwen2.5-7B, randamentul din ziua d+${lag}, pînă la ${d}: ${mu} bp pe zi înainte de costuri (t Newey–West = ${t}). Raportul Sharpe este ${sr} înainte de costuri și ${srn} cu ${c} bp pe tranzacție; costul de echilibru este ${be} bp.`,
 sg2: (fm, ft, fs, lm, lt, ls) => `FinBERT: ${fm} bp pe zi (t = ${ft}), raportul Sharpe după costuri ${fs}. LM: ${lm} bp pe zi (t = ${lt}), raportul Sharpe după costuri ${ls}.`,
 pp1: (n, wc, wf, wq, cc, cf, cq) => `Simulare în browser, n = ${F(n)}, 2 000 de replicări: lățimea medie a intervalului este ${wc} doar cu etichete umane, ${wf} cu PPI și FinBERT, ${wq} cu PPI și Qwen; acoperirea este ${cc}, ${cf}, respectiv ${cq}.`,
 pp2: (n, wc, wf, cf) => `În curs, la n = ${F(n)}: lățimea este ${wc} doar cu etichete umane și ${wf} cu PPI și FinBERT; acoperirea PPI cu FinBERT este ${cf}.`,
 pp3: (f, q, th) => `Mediile simple ale scorurilor: FinBERT ${f}, Qwen ${q}, față de θ = ${th}; distorsiunea nu scade cu n.`,
 lt: (k, h, a, b, nb) => `${k} din 12 modele ghicesc reacția inițială în peste ${h}% din zile; mediana raportului Sharpe al drift-ului lor este ${a}${nb ? `, iar a celorlalte ${nb} modele ${b}` : ''}.`,
 sc1: (c, two, k, e, bf) => `Pragul ${c}: ${two} din 36 de specificații au |t| > ${c}, dintre care ${k} cu t > ${c}. Sub ipoteza nulă comună, numărul așteptat cu |t| > ${c} este ${e}. Pragul Bonferroni pentru 36 de teste: ${bf}.`,
 sc2: (B, k, p, med, pm, pl, pml) => `Cu ${N(B, 'extrageri')} cu semn schimbat: P(cel puțin ${k} specificații cu t peste prag) = ${p}; P(mediana lui t ≥ ${med}) = ${pm}. În curs, cu 2 000 de extrageri și pragul 1,96: ${pl} și ${pml}.`
};
})();

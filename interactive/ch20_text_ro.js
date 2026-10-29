// Readouts of the Chapter 20 interactive page, written by latex/build_interactive_ch20.py.
window.CH20_TEXT = {
 play: 'Pornește', pause: 'Pauză',
 months: ['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sep.', 'oct.', 'nov.', 'dec.'],
 cls: { all: 'toate cele 50 de active', stocks: 'acțiunile americane (40)', futures: 'futures (5)', forex: 'FX (5)' },
 stat: { mean: 'media', median: 'mediana' },
 none: 'niciunul',
 week1: '1 săptămînă (5 zile, ca în slide)', weeks: k => `${k} săptămîni (${5 * k} zile)`,
 vr: (c, n, a, va, da, b, vb, db) => `${c[0].toUpperCase() + c.slice(1)}, maximul din prima jumătate a lui 2020 al mediei pe ${n} zile: ${a} ${va}% (în zilele încheiate pe ${da}), ${b} ${vb}% (${db}).`,
 qr0: (g, k, b) => `${g[0].toUpperCase() + g.slice(1)}${k === 0 ? '' : ', fără cele ' + k + ' active cu cele mai mari rapoarte ale fiecărui model'}; reperul este ${b}.`,
 qr: (h, a, ma, da, b, mb, db) => `h = ${h}: ${a} are media ${ma} și mediana ${da}; ${b} are media ${mb} și mediana ${db}.`,
 mc: (lev, l, g, lh, sk, har) => `MCS de ${lev}%, ${l}, ${g}. Proporția activelor în care modelul rămîne în mulțime la h = 1, 5 și 22: log-HAR ${lh}; Sig-LK ${sk}; HAR ${har}.`,
 cv1: (d, y, a, b, c) => `Originea ${d}: ținta este ${y}%; prognozele sînt ${a}% (HAR), ${b}% (log-HAR) și ${c}% (Sig-LK).`,
 cv2: (d0, d, n, a, b, c) => `QLIKE medie de la ${d0} pînă la ${d} (${n} ${n % 100 >= 20 || n % 100 === 0 ? 'de ' : ''}zile): HAR ${a}, log-HAR ${b}, Sig-LK ${c}.`,
 sp1: (g, st, c1, c2, c3, a1, a2, r1, r2) => `${g[0].toUpperCase() + g.slice(1)}, ${st} pe active, h = 1. Crahul COVID-19: log-HAR ${c1}, Sig-LK ${c2}, HARQ ${c3}. 2–30 aprilie 2025: log-HAR ${a1}, Sig-LK ${a2}. Celelalte zile: log-HAR ${r1}, Sig-LK ${r2}.`,
 sp22: (a, b) => `h = 22, crahul COVID-19: Sig-LK ${a}, Sig-L ${b} ori pierderea HAR.`,
 kw1: (c, N, lo, hi, e, n) => `c = ${c}, N = ${N}: ponderea medie pe cele 40 de acțiuni este între ${lo} și ${hi} ori 1/n; mărimea efectivă medie a eșantionului este ${e} din ${n}.`,
 kw2: (lo, hi, e) => `JPM: ponderile sînt între ${lo} și ${hi} ori 1/n; mărimea efectivă a eșantionului este ${e}.`,
 kw3: (k, a, dn, df) => `Fereastra originii, primele ${k} ${k >= 20 ? 'de ' : ''}puncte: aria Lévy (randament, log RV) este ${a}. Cea mai apropiată fereastră de antrenare se încheie pe ${dn}, cea mai depărtată pe ${df}.`,
 ab1: (x, g, k, l, lk) => `Activ exclus: ${x}; ${g}. QLIKE relativ la log-HAR la h = 1, 5 și 22: log-HAR-K ${k}; Sig-L ${l}; Sig-LK ${lk}.`,
 ab2: (h, s, v) => `La h = ${h}, cel mai mare raport Sig-LK / log-HAR îl are ${s} (${v}).`
};

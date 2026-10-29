// Readouts of the Chapter 19 interactive page, written by latex/build_interactive_ch19.py.
(function () {
const de = s => { const n = +String(s).replace(/[^0-9]/g, ''), m = n % 100; return (m === 0 && n > 0) || m >= 20 ? 'de ' : ''; };
window.CH19_TEXT = {
 play: 'Pornește', pause: 'Pauză', none: 'niciunul',
 bf: (y0, y1, n, k, a, n4, e4) => `${y0}–${y1}: ${n} ${de(n)}randamente zilnice. Tail index-ul Hill al pierderilor (k = ${k}): ${a}. Zile dincolo de ±4 abateri standard: ${n4}, față de ${e4} așteptate sub distribuția Normală.`,
 bf2: (a1, r1, q) => `ACF a lui |r<sub>t</sub>| la lagul 1: ${a1}; ACF a lui r<sub>t</sub>: ${r1}. Ljung–Box Q(10) pe r<sub>t</sub><sup>2</sup>: ${q}, față de valoarea critică de 18,3.`,
 hl: h => { if (!isFinite(h)) return 'nu este finit, pentru că α + β ≥ 1'; const n = Math.round(h), m = n % 100; return n === 1 ? 'aproximativ o zi de tranzacționare' : `aproximativ ${n} ${m === 0 || m >= 20 ? 'de ' : ''}zile de tranzacționare`; },
 bg: (a, b, p, hl) => `α = ${a}, β = ${b}, persistența α + β = ${p}. Timpul de înjumătățire: ${hl}.`,
 bg2: (mx, dm, s, d) => `Volatilitatea condiționată zilnică maximă: ${mx}, pe ${dm}; la finalul eșantionului (${d}): ${s}.`,
 bg3: (d, a) => `Volatilitatea de termen lung √(ω/(1 − α − β)): ${d} pe zi, ${a} pe an.`,
 bg3n: 'Cu α + β ≥ 1, varianța necondiționată nu este finită.',
 bg4: (n, s) => `Randamente în afara benzii ±2σ̂<sub>t</sub>: ${n} ${de(n)}zile (${s}).`,
 bv: (d0, d1, n, e, l) => `${d0} – ${d1}: ${n} ${de(n)}zile, ${e} depășiri așteptate pentru VaR ${l}.`,
 bv2: (xf, m, xm) => `Depășiri efective: FHS ${xf}, ${m} ${xm}.`,
 bv3: (v, dv, d, f, m, fm) => `VaR-ul FHS maxim: ${v}, pe ${dv}. Prognoza pentru ${d}: FHS ${f}, ${m} ${fm}.`,
 br: (d0, d1, n, l, lo, hi, inn) => `${d0} – ${d1}, T = ${n} ${de(n)}zile. Intervalul binomial de 95% dacă rata adevărată este ${l}: [${lo}; ${hi}]. În interval: ${inn}.`,
 br2: s => `Rata depășirilor și p-value-ul testului Kupiec: ${s}.`,
 br3: (a, s) => `Respinse la 5% (${a}): ${s}.`,
 adj: { none: 'fiecare test separat', holm: 'Holm, FWER', bh: 'Benjamini–Hochberg, FDR 5%' },
 kp: (n, pi, a, pw) => `T = ${n} ${de(n)}zile, rata reală ${pi}: testul Kupiec de ${a} respinge modelul cu probabilitatea ${pw}.`,
 reg: (lo, hi) => (lo < 0 ? `cel puțin ${hi} depășiri` : lo === 0 ? `0 depășiri sau cel puțin ${hi}` : `cel mult ${lo} depășiri sau cel puțin ${hi}`),
 kp2: s => `Regiunea de respingere: ${s}.`,
 kp3: (m, s) => `MDE (putere de cel puțin 80%, grilă cu pasul de 0,05 puncte procentuale): ${m}. Mărimea efectivă a testului, la o rată reală de 1%: ${s}.`,
 nm: (lab, n, med, iqr, b) => `${lab}: ${n} ${de(n)}specificații, mediana ${med} pe an, IQR ${iqr} pp. Reperul datorat eșantionării, 1,35 × SE-ul median: ${b} pp.`
};
})();

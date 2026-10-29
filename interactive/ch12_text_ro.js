// Readouts of the Chapter 12 interactive page, written by latex/build_interactive_ch12.py.
const zile = n => { const v = +String(n).replace(/\./g, ''), r = v % 100; return `${n} ${r >= 1 && r <= 19 ? 'zile' : 'de zile'}`; };
window.CH12_TEXT = {
 play: 'Pornește', pause: 'Pauză',
 gk: (S, s, d, g, v, t, vg) => `Call pe trei luni, S = ${S}, σ = ${s}: delta ${d}, gamma ${g}, vega ${v} pe punct de volatilitate, theta ${t} pe zi. ΓS²στ = ${vg}, egal cu vega.`,
 he: (n, sd, sp, p, m, q, th) => `N = ${n}: abaterea standard a erorii este ${sd} (${sp} din prima de ${p}), media ${m}, cuantila de 1% ${q}. Aproximarea √(π/4)·vega·σ/√N dă ${th}.`,
 vm: (s, m, sd, w, v, a) => `Volatilitatea realizată ${s}%: rezultatul mediu este ${m}, abaterea standard ${sd}, pozitiv pe ${w} dintre traiectorii. Aproximarea vega × (20 − ${s}) = ${v} × (20 − ${s}) dă ${a}.`,
 sm: (e1, e2, e3, m1, m2, m3, h1, h2, h3) => `Volatilitatea implicită la K/S = 0,8, ATM și 1,2: istoric ${e1}%, ${e2}%, ${e3}%; Merton ${m1}%, ${m2}%, ${m3}%; Heston ${h1}%, ${h2}%, ${h3}%.`,
 bs1: (d, n, F, a, r) => `Scadența ${d}, ${n} de zile, forward ${F} USD: volatilitatea ATM este ${a}%, iar eroarea pătratică medie a ajustării SVI ${r} puncte de volatilitate.`,
 bs2: (rho, b, l, r, e, g, ok) => `SVI cu ρ = ${rho} și b = ${b}: pantele aripilor sînt b(1 − ρ) = ${l} în stînga și b(1 + ρ) = ${r} în dreapta (limita Lee: 2); eroarea pătratică medie este ${e} puncte; min g(k) = ${g}, ${ok ? 'deci fără arbitraj de tip butterfly' : 'deci densitatea devine negativă: arbitraj de tip butterfly'}.`,
 rn1: (x, p, lo, hi, ln, k) => `O scădere de peste ${x}: ${p} după zîmbetul SVI (intervalul bootstrap de 95%: ${lo}–${hi}), față de ${ln} sub distribuția log-normală (raportul ${k}).`,
 rn2: (x, p, ln) => `O creștere de peste ${x}: ${p} după zîmbetul SVI și ${ln} sub distribuția log-normală.`,
 rn3: (k, e) => `Sub cel mai mic preț de exercitare cotat (${k}F) se află ${e} puncte procentuale din densitate: aceasta este extrapolare SVI.`,
 vh: (L, s, n, e, l) => e === 0 ? `VIX nu a depășit ${L} în cele ${n} de zile.` : `VIX a fost peste ${L} în ${s} din cele ${n} de zile, în ${e === 1 ? 'un singur episod' : zile(e).replace(/zile$/, 'episoade separate')}; ${e === 1 ? 'acesta' : 'cel mai lung'} a durat ${l === 1 ? 'o zi' : zile(l)} de tranzacționare.`,
 vh2: (m, lo, hi) => `Media este ${m}, minimul ${lo}, maximul ${hi}.`,
 vr1: (y, n, v, r) => `Din ${y}: ${zile(n)}; VIX mediu ${v}, volatilitatea realizată medie ${r}.`,
 vr2: (m, se, mv, t) => `Prima medie este ${m} puncte de volatilitate (eroarea standard Newey–West, 21 de lag-uri: ${se}); în varianță, ${mv} %², cu t = ${t}.`,
 vr3: (s, w, d) => `Prima este pozitivă în ${s} dintre zile; cea mai slabă valoare este ${w} puncte, pentru fereastra începută pe ${d}.`,
 mz1: (n, a, as, b, bs, r) => `${zile(n)}: α̂ = ${a} (${as}), β̂ = ${b} (${bs}), R² = ${r}; erori standard Newey–West, 21 de lag-uri.`,
 mz2: (w, p, c, rp) => `Testul Wald comun pentru α = 0, β = 1: χ²₂ = ${w}, p = ${p}; corelația estimărilor este ${c}. Doar cu varianța realizată trecută: R² = ${rp}.`,
 od1: (s, g1, g21, k) => `σ = ${s}: gamma ATM este ${g1} cu o zi de tranzacționare înainte de scadență și ${g21} cu o lună înainte, de ${k} ori mai mare.`,
 od2: (d, g, g2) => `Cu ${d > 1 ? zile(d) + ' de tranzacționare rămase' : 'o zi de tranzacționare rămasă'}: gamma ATM este ${g}, deci o mișcare de 1% schimbă delta cu aproximativ ${g2}.`,
 od3: (t1, t30, k) => `Time decay-ul ATM este ${t1} în ultima zi calendaristică și ${t30} cu 30 de zile rămase, de ${k} ori mai mic.`,
 bk1: (h, a, b, n, s, c) => `Orizontul de ${h} ${h > 1 ? 'luni' : 'lună'}, date de formare ${a} – ${b} (${n}): randamentul în exces realizat este sub limita Martin la ${s} dintre date; corelația este ${c}.`,
 bk2: (f, p, m, s) => `Randamentul mediu în exces este ${f}% pe an (indicele de preț; cu dividende, în lucrare: ${p}%), limita medie ${m}%, diferența medie ${s} puncte.`,
 bk3: (md, mx, d, s) => `Limita Martin pe o lună: mediana ${md}%, maximul ${mx}% (${d}); limita Chabi-Yo–Loudis este cel puțin egală cu limita Martin în ${s} dintre zile.`
};

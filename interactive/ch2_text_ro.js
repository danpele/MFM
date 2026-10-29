// Readouts of the Chapter 2 interactive page, written by latex/build_interactive_ch2.py.
const de = n => (n >= 20 && (n % 100 === 0 || n % 100 >= 20) ? n + ' de' : '' + n);
window.CH2_TEXT = {
 play: 'Pornește', pause: 'Pauză', descr: 'doar descriptiv',
 rg: (k, f) => `Ziua ${k}: valoarea a 1 USD investit la început este A ${f[0]}, B ${f[1]}, C ${f[2]}, D ${f[3]}.`,
 rgHide: 'Alegeți seria reală, apoi arătați-o din lista de mai sus.',
 rgReveal: (s, v, m, sd, a, b) => `Seria ${s} este S&P 500 (${a} – ${b}): 1 USD a devenit ${v} USD. Random walk-urile au drift-ul zilnic ${m} și volatilitatea zilnică ${sd}, estimate pe S&P 500.`,
 cr: (s, k) => `Abaterea standard a randamentelor: RW1 ${s[0]}, RW2 ${s[1]}, GARCH ${s[2]}. Kurtosis: ${k[0]}, ${k[1]}, ${k[2]} (3 la distribuția Normală).`,
 crG: (a, b, o) => `GARCH: autocorelația de lag 1 este ${a} pentru randamente și ${b} pentru pătratele lor; ω = 1 − α − β = ${o}, deci dispersia pe termen lung este 1.`,
 cs: (n, m, a, b, bd) => `T = ${n} zile: cea mai mare autocorelație a randamentelor, în valoare absolută, este ${m}. Autocorelația pătratelor este ${a} la lagul 1 și ${b} la lagul 20; banda ±1,96/√T este ±${bd}.`,
 csTh: (a, p) => `Teoretic, autocorelația pătratelor este ${a} la lagul 1 și scade cu factorul α + β = ${p} la fiecare lag.`,
 csInf: 'Cu 3α² + 2αβ + β² ≥ 1 momentul de ordinul 4 nu există, iar autocorelația teoretică a pătratelor nu este definită.',
 ac: (k, n, l, ni) => `Lagul ${k}: intervalul robust exclude zero la ${n} din 16 serii (${l}); intervalul i.i.d. l-ar exclude la ${ni}.`,
 ac2: (k, r, s, si) => `S&P 500: ρ̂${k} = ${r}, eroarea standard robustă ${s}, cea i.i.d. ${si}.`,
 vr: (m, q, v, lo, hi, o, p) => `${m}: VR(${q}) = ${v}, null band-ul [${lo}; ${hi}]; ${o ? 'în afara lui, respingem la 5%' : 'în interior, nu respingem'}. Chow–Denning pe q = 2, 5, 10, 20: p ${p}.`,
 od: (y, n, r, c) => `Evaluare din ianuarie ${y}: ${de(n)} prognoze lunare, R²<sub>OS</sub> = ${r}; valoarea finală a curbei este ${c}.`,
 od2: (r, t, p) => `În curs (din 1970): R²<sub>OS</sub> = ${r}, testul Clark–West t = ${t}, p unilateral = ${p}.`,
 ev0: (b, s, a, tn, t) => `TLV: beta ${b}, abaterea standard a reziduurilor ${s} pe zi; AR₀ = ${a}, t = ${tn} cu σ̂ și t = ${t} cu eroarea de predicție.`,
 ev: (a, b, c, t, tn) => `CAR[${a}, ${b}]: TLV ${c[0]} (t = ${t[0]}), BRD ${c[1]} (t = ${t[1]}), portofoliul ${c[2]} (t = ${t[2]}). Pentru TLV, cu σ̂√L: t = ${tn}.`,
 mt: (k, s, n, s3, n3, m) => `${de(k)} reguli: ${s} au |t| > 1,96 (${de(n)} ${n === 1 ? 'regulă' : 'reguli'}), ${s3} au |t| > 3,0 (${n3}); cel mai mare |t| este ${m}.`,
 mt2: (k, f) => `Dacă cele ${de(k)} teste ar fi independente, probabilitatea a cel puțin unei respingeri false la 5% ar fi ${f}.`
};

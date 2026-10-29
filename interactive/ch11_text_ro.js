// Readouts of the Chapter 11 interactive page, written by latex/build_interactive_ch11.py.
window.CH11_TEXT = (() => {
const de = n => (n >= 20 && (n % 100 === 0 || n % 100 >= 20) ? ' de' : '');
return {
 play: 'Pornește', pause: 'Pauză',
 dk: (a, ex, p5, p2, g) => `Nivelul a = ${a}: limita browniană 2(1 − Φ(a)) este ${ex}. Random walk: ${p5} cu n = 5 și ${p2} cu n = 2 000 (diferență față de limită: ${g}).`,
 dk2: c => c ? `Traiectoriile din stînga care depășesc nivelul a: ${c}.` : 'Niciuna dintre cele trei traiectorii din stînga nu depășește nivelul a.',
 qv: (p, s, m) => `p = ${p}: pe grila cu 65 536 de intervale, Σ|ΔW|^p = ${s}. ` + (m === 'up' ? 'Pentru p < 2 suma crește odată cu n.' : m === 'down' ? 'Pentru p > 2 suma tinde la zero.' : 'Pentru p = 2 suma se stabilizează la T = 1.'),
 qv2: (c, d, q) => `${c === '2008' ? 'Septembrie 2008 – martie 2009' : '20 februarie – 30 aprilie 2020'}: ${d} din zile și ${q} din variația pătratică a S&P 500.`,
 qv3: (s, y, v) => `S&P 500: Σ r² = ${s} în ${y} ani, adică o volatilitate medie de ${v} pe an.`,
 dp: (y, a, b) => `Cu T = ${y}${de(y)} ${y === 1 ? 'an' : 'ani'} de date, semilățimea intervalului de 95% pentru drift este ±${a} puncte procentuale pentru S&P 500 și ±${b} pentru Bitcoin.`,
 dp2: (lo, dl, hi, dh, h, s0, s1) => `Ferestre rolling: driftul logaritmic variază între ${lo}% (fereastra încheiată în ${dl}) și ${hi}% (${dh}); semilățimea mediană a intervalului este ±${h} puncte. Volatilitatea rămîne între ${s0}% și ${s1}%.`,
 gd: (k, n, e) => `Dincolo de ±${k} abateri standard: ${n}${de(n)} ${n === 1 ? 'zi' : 'zile'} în date, față de ${e} așteptate sub distribuția Normală.`,
 gd2: (s, a1, a50, b) => `ACF a lui ${s}: ${a1} la lagul 1 și ${a50} la lagul 50. Banda GBM rămîne sub ${b} în valoare absolută.`,
 va: (a, b, k, se, hl, bb) => `${a}–${b}: κ̂ = ${k} (SE ${se}) pe an, ` + (hl ? `adică un timp de înjumătățire de ${hl} ani` : 'fără revenire la medie (κ̂ < 0)') + `; coeficientul AR(1) zilnic b̂ = ${bb}.`,
 va2: (t, s, sd, z) => `θ̂ = ${t}%, σ̂ = ${s}%, abaterea standard staționară ${sd}%. ` + (z ? 'Intervalul de 95% pentru κ include zero.' : 'Intervalul de 95% pentru κ nu include zero.'),
 va3: s => `σ̂ = ${s}%. Cu κ̂ < 0 procesul estimat este exploziv: media pe termen lung și banda staționară nu există.`,
 mj: (n, l, s, j, k, kd, ll, lm, lg) => `${n}: λ = ${l} salturi pe an, σ = ${s}, salturile explică ${j} din dispersie. Excesul de kurtosis implicat: ${k} (în date: ${kd}). Log-verosimilitatea: ${ll} (la estimarea MLE: ${lm}; GBM: ${lg}).`,
 mv: (k, d, m, g) => `${k} simulări. Excesul de kurtosis: ${d} în date; mediane GBM ${m[0]}, Merton ${m[1]}, Heston ${m[2]}. Simulări cu kurtosis cel puțin egal cu cel din date: ${g[0]}, ${g[1]}, ${g[2]}.`,
 mv2: (d, m) => `Statistica Hill: ${d} în date; mediane GBM ${m[0]}, Merton ${m[1]}, Heston ${m[2]}.`,
 mv3: (d, a) => `ACF a lui |r| la lagul 1: ${d} în date; mediane GBM ${a[0]}, Merton ${a[1]}, Heston ${a[2]}.`,
 ro: (m, a, s) => `Panta variogramei pe k = 1..${m} dă α̂ (OLS) = ${a}; estimatorul NLLS robust la zgomot dă α̂* = ${s}. α = 0 corespunde mișcării browniene.`,
 ro2: (H, b, bs, hl, r, o) => `Ajustare pe h = 1..${H}: β̂ = ${b}, β̂* = ${bs}. OU: timp de înjumătățire ${hl} zile, autocorelație implicată la lagul 100 ${o}, față de ${r} în date.`
};
})();

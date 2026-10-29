// Readouts of the Chapter 14 interactive page, written by latex/build_interactive_ch14.py.
// numerals from 20 upwards (last two digits 00 or 20-99) take "de" before the noun
const de = s => { const n = +String(s).replace(/[^0-9]/g, ''), r = n % 100; return n >= 20 && (r === 0 || r >= 20) ? s + ' de' : s; };
window.CH14_TEXT = {
 play: 'Pornește', pause: 'Pauză', none: 'niciunul', plen: P => `${de(P)} zile`,
 nm: { 'Historical mean': 'media istorică', 'LSTM (5 seeds)': 'LSTM (5 inițializări)', 'Random walk': 'mersul aleator', 'Chronos-2 quantiles': 'cuantilele Chronos-2',
       'FHS + Chronos-2 volatility': 'FHS cu volatilitatea Chronos-2', 'FHS + TimesFM volatility': 'FHS cu volatilitatea TimesFM' },
 ac1: (y, n, b, r1, k, L) => `S&P 500 din ${y}: ${de(n)} zile, banda ±${b}. Randamentele: autocorelația de ordinul 1 este ${r1}; ${k} din ${de(L)} lag-uri sînt în afara benzii.`,
 ac2: (sq, a1, L, aL, k) => `${sq ? 'Pătratele randamentelor' : 'Randamentele absolute'}: ${a1} la lag-ul 1, ${aL} la lag-ul ${L}; ${k} din ${de(L)} lag-uri sînt în afara benzii.`,
 pa: (n, P, k, full, sc, ratio) => `Context de ${de(n)} zile în patch-uri de ${de(P)} zile: ${de(k)} tokeni și ${de(sc)} scoruri de atenție pe strat, față de ${full} cu un token pe zi (de ${de(ratio)} ori mai puține).`,
 pa2: (k, s) => `TimesFM-2.5 (patch-uri de 32 de zile): ${k} tokeni, ${de(s)} scoruri.`,
 r2: (a, s, n, b, v, p, tf, tp) => `${a}, din ${s} (${de(n)} zile): cel mai mare R² îl are ${b}, ${v}% (p DM = ${p}); TimesFM-2.5 are ${tf}% (p = ${tp}).`,
 rv1: (a, b, n, pk, d) => `${a} – ${b} (${de(n)} zile): volatilitatea realizată maximă este ${pk}% pe an, la ${d}.`,
 rv2: (m, q, lh, c2) => `Pierderea QLIKE medie în această fereastră: cea mai mică la ${m} (${q}); log-HAR ${lh}, Chronos-2 ${c2}.`,
 ql1: (l, s, n, m, v, lh, c2) => `${l} din ${s} (${de(n)} zile): cea mai mică la ${m} (${v}); log-HAR ${lh}, Chronos-2 ${c2}.`,
 ql2: (d, p) => `Testul DM, Chronos-2 față de log-HAR: ${d}, p = ${p}.`,
 br: (a, n, c2, p, f, h, lo, hi) => `${a} (${de(n)} zile): Chronos-2 direct ${c2} (p Kupiec = ${p}), FHS ${f}, FHS cu volatilitatea Chronos-2 ${h}; un model corect dă între ${lo} și ${de(hi)} depășiri cu probabilitatea de 95%.`,
 vp1: (n, f, c, h, hs) => `${de(n)} zile. Depășiri: FHS ${f}, Chronos-2 direct ${c}, FHS cu volatilitatea Chronos-2 ${h}, HS ${hs}.`,
 vp2: (h, d, f, l) => `VaR 1% maxim al hibridului: ${h}% la ${d}; FHS cel mult ${f}%; pierderea zilnică maximă ${l}%.`,
 pi: (a, c2, f, g) => `${a}: randamentul cade sub cuantila de 1% în ${c2} dintre zile cu Chronos-2, ${f} cu FHS și ${g} cu GARCH-t (așteptat: 1%).`,
 mc1: (lev, s) => `Eliminate din mulțimea de ${lev}%: ${s}.`,
 mc2: (m, fz, d, p) => `S&P 500: cea mai mică FZ0 medie o are ${m} (${fz}); DM pentru FHS cu volatilitatea Chronos-2 față de FHS: ${d}, p = ${p}.`,
 cf1: (n, s, x, e, r, xf) => `${de(n)} zile din ${s}: ${de(x)} depășiri cu corecția conformală (${e} așteptate, rata ${r}); FHS are ${xf}.`,
 cf2: (a, f, k) => `VaR 1% mediu: ${a}% cu corecția, ${f}% pentru FHS.` + (k ? ` În ${de(k)} zile nivelul α_t a scăzut sub cel mai mic rang posibil, iar VaR este infinit.` : ''),
 kz1: (c, z, r2, sr, lin) => `c = ${c}, z = ${z}: R² ${r2}%, raportul Sharpe ${sr}; modelul liniar cu z = 10³: ${lin}.`,
 kz2: (z, sr, c) => `Cel mai mare raport Sharpe pentru z = ${z}: ${sr}, la c = ${c}.`,
 ai1: (d, n0, n1, m0, m1) => `Ruptura la ${d}: media lui d_t este ${m0} în cele ${de(n0)} zile dinainte și ${m1} în cele ${de(n1)} zile de după.`,
 ai2: (b, t, p, m) => `Schimbarea: ${b}, t HAC = ${t}, p = ${p}; MDE la o putere de 80%: ${m}.`
};

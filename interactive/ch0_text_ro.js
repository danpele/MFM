// Readouts of the Chapter 0 interactive page, written by latex/build_interactive_ch0.py.
window.CH0_TEXT = {
 date: d => `${d.getUTCDate()} ${['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sep.', 'oct.', 'nov.', 'dec.'][d.getUTCMonth()]} ${d.getUTCFullYear()}`,
 hi: (y, a, b) => `Pînă în ${y}: ${a} repere pe axa burselor și ${b} pe axa bulelor, panicilor și crahurilor.`,
 rr: (a, b, y) => `Fereastra: ${a} – ${b}, ${y} ani.`,
 rr2: (n, c, v, se) => `${n}: CAGR ${c}, volatilitate anualizată ${v}; eroarea standard a randamentului mediu anualizat, σ/√Y, este ${se} pp.`,
 dd: (d, c, m, md) => `Pe ${d}: drawdown ${c}. Drawdown-ul maxim pînă la această dată: ${m}, pe ${md}.`,
 ddr: (p, r, y) => `Maximul din ${p} a fost depășit din nou pe ${r}, după ${y} ani.`,
 ddn: (p, x) => `Indicele este încă sub maximul din ${p}, cu ${x}.`,
 vx: (lo, hi, a, b, c, n) => `Din ${n} de zile: VIX sub ${lo} în ${a}, între ${lo} și ${hi} în ${b}, cel puțin ${hi} în ${c}.`,
 co: (w, a, b, c, e) => `Fereastra de ${w} de zile. S&P 500–TLT: media corelației rolling ${a} în 2010–2020 și ${b} în 2022–2026. S&P 500–Bitcoin: ${c} în 2016–2019 și ${e} în 2022–2026.`,
 bt: (a, b, m, c, y) => `De la ${a} la ${b}: indicele crește de ${m} ori, un CAGR de ${c} pe ${y} ani.`,
 bt2: (d, p, t, r) => `Cel mai mare drawdown din fereastră: ${d}, de la maximul din ${p} la minimul din ${t}; ${r}.`,
 btr: (d, y) => `maximul a fost atins din nou pe ${d}, după ${y} ani`,
 btn: 'maximul nu a mai fost atins pînă în sep. 2026',
 bt0: 'Indicele nu a coborît sub nivelul de la data de început.',
 us: (p, b, a, c, n) => `${p}, ${n} de zile: USDT la cel mult ±${b} de 1 USD în ${a} din zile, la cel mult ±1% în ${c}.`,
 cc: (d, s, r, q) => `De la ${d}: SPY crește de ${s} ori, RSP de ${r} ori; raportul final SPY/RSP este ${q}.`,
 cc2: c => `Din 3 ian. 2023 raportul SPY/RSP a crescut cu ${c}, indiferent de data de început.`,
 hh: (p, a, b, chi, c) => `Cu ${p} dintre investitori trecuți la administrare pasivă, elasticitatea agregată relativă este ${a} pentru χ = 0, ${b} pentru χ = ${chi} și ${c} pentru χ = 10.`,
 hh2: (chi, al, r) => `Rata de transmitere 1/(1 + χα) pentru χ = ${chi} și α = ${al}: ${r}.`,
 ai: (m, t, mde, n) => `Întregul eșantion (${n} de zile): diferența medie ${m} pe an, t = ${t} (Newey–West), MDE ${mde} pe an.`,
 ai2: (y1, m1, t1, y2, m2, t2, mde) => `Pînă în ${y1}: ${m1} (t = ${t1}). Din ${y2}: ${m2} (t = ${t2}), MDE ${mde}.`
};

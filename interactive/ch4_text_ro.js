// Readouts of the Chapter 4 interactive page, written by latex/build_interactive_ch4.py.
window.CH4_TEXT = {
 play: 'Pornește', pause: 'Pauză',
 ta: (v, m, g, gv) => `Portofoliul ales: volatilitate ${v}, randament mediu ${m} pe an. Varianță minimă: ${g} în SPY, volatilitate ${gv}.`,
 fr: (n, a, b, s) => `${n} sectoare. Raportul Sharpe: ${a} cu vînzări în lipsă, ${b} long-only. Poziții short: ${s}.`,
 ee: (e, r, b, ew) => `Mediana raportului Sharpe estimat: ${e}; realizat: ${r}. ${b} dintre eșantioane rămîn sub 1/N (${ew}).`,
 rw: (d, a, b) => `${d}: expunerea brută este ${a} pentru MV și ${b} pentru GMV-LW.`,
 wl: (t, m, ew, at) => `T = ${t} luni: mediana raportului Sharpe MV este ${m}, față de ${ew} pentru 1/N. MV depășește 1/N de la T = ${at}.`,
 mp: (k, n, lo, hi) => `${k} din ${n} valori proprii sînt deasupra benzii [${lo}; ${hi}].`,
 sh: (d, c, w, lw) => `δ = ${d}: număr de condiționare ${c}, cea mai mare pondere GMV în valoare absolută ${w}. Valoarea Ledoit–Wolf pe ultimele 60 de luni: δ = ${lw}.`,
 bl: (p, q, m, k, u) => `XLK − XLU: a priori ${p}, opinia ${q}, a posteriori ${m} pe an. Ponderi față de 1/N: XLK ${k}, XLU ${u}; celelalte neschimbate.`,
 rc: (k, w, r) => `Iterația ${k}: acțiunile și high yield au ${w} din capital și ${r} din risc.`,
 hrp1: 'Pasul 1: matricea de corelație în ordinea inițială a celor 16 ETF-uri.',
 hrp2: 'Pasul 2: aceeași matrice în ordinea frunzelor arborelui; activele corelate ajung alături.',
 hrp3: (l, c, m) => `Bisecția, nivelul ${l}: ${c} grupuri; cea mai mare pondere este ${m}.`,
 ow: (d, c, s, v, e) => `Pînă în ${d}, cu ${c} bp: cel mai mare raport Sharpe îl are ${s} (${v}); 1/N are ${e}.`,
 os: (y, e, m) => `Sectoare, evaluare din ${y}: raportul Sharpe 1/N este ${e}, iar MV ${m}.`,
 co: (c, s, v, m, e) => `La ${c} bp: cel mai mare raport Sharpe net îl are ${s} (${v}); MV are ${m}, 1/N ${e}.`,
 st: (o, lo, hi, ph, pb) => `Diferența observată: ${o}. Intervalul de 95% al extragerilor centrate: [${lo}; ${hi}]. În curs: p = ${ph} (HAC), p = ${pb} (bootstrap studentizat).`,
 bv: (d, s, v, b) => `Pînă în ${d}: cel mai mare raport Sharpe îl are ${s} (${v}); BET-TR are ${b}.`
};

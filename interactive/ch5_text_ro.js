// Readouts of the Chapter 5 interactive page, written by latex/build_interactive_ch5.py.
const CH5_ZILE = s => { const n = parseFloat(String(s).replace(/[^0-9,.]/g, '').replace(',', '.')), r = n % 100; return s + (Number.isInteger(n) && n >= 20 && (r === 0 || r >= 20) ? ' de zile' : ' zile'); };
window.CH5_TEXT = {
 play: 'Pornește', pause: 'Pauză', gold: 'Aur',
 cl: (s, n, q, hit, base) => `${s}: ${CH5_ZILE(n)} cu |r| peste prag (${q} din zile). După o astfel de zi, încă una urmează în următoarele 5 zile în ${hit} din cazuri; la zile independente ar fi ${base}.`,
 ac: (s, a1, d, a2, o1, o2, b) => `${s}, lagul 1: ${a1} pentru r, ${a2} pentru |r|^${d}. În afara benzii ±${b}: ${o1} din 50 de autocorelații ale lui r, ${o2} din 50 ale lui |r|^${d}.`,
 ac2: k => `Excesul de kurtosis al randamentelor: ${k}.`,
 si: (be, om, kt, ks, ki, hl) => `β = ${be}, ω = ${om}. Excesul de kurtosis: teoretic ${kt === null ? 'infinit, deoarece (α + β)² + 2α² ≥ 1' : kt}; pe cele 2 000 de zile simulate, ${ks} pentru GARCH și ${ki} pentru seria i.i.d. Timpul de înjumătățire: ${CH5_ZILE(hl)}.`,
 dm: (p, h, t, v) => `p = ${p}: timpul de înjumătățire este ${CH5_ZILE(h)}, tangenta metodei delta dă ${CH5_ZILE(t)}, iar volatilitatea de termen lung este ${v} pe an.`,
 dm2: (se, seh, lo, hi) => `SE(p̂) = ${se}, deci SE(ĥ) ≈ ${CH5_ZILE(seh)} prin metoda delta. Intervalul de 95% pentru p, [${lo}; ${hi}], conține p = 1.`,
 ts: (s, a, b, u) => `${s}: ${a}% pentru ziua următoare, ${b}% în medie pe 250 de zile; nivelul de termen lung: ${u === null ? 'nu există (α̂ + β̂ ≥ 0,999)' : u + '%'}.`,
 pe: (h, list) => `Partea din șoc rămasă după ${CH5_ZILE(h)}: ${list}.`,
 vx: (a, p, hl, c, mv, mg, sh) => `α = ${a}, α + β = ${p}, timpul de înjumătățire ${CH5_ZILE(hl)}. Pe perioada aleasă: corelația cu VIX ${c}; media VIX ${mv}%, media GARCH ${mg}%; VIX este peste volatilitatea GARCH în ${sh} din zile.`,
 ni: (e, g, eg, ga) => `După un șoc de ${e}%: GJR ${g}, EGARCH ${eg}, GARCH ${ga}.`,
 ni2: (rg, re) => `Dispersia după un șoc negativ împărțită la cea după un șoc pozitiv de aceeași mărime: ${rg} (GJR), ${re} (EGARCH).`,
 inn: (o, en, nu, et) => `Reziduuri sub −4: ${o} observate; așteptate ${en} sub distribuția Normală și ${et} sub Student-t cu ν = ${nu}.`,
 inn2: (k, kt) => `Excesul de kurtosis: ${k} pentru ẑ, ${kt === null ? 'infinit' : kt} pentru Student-t cu acest ν.`,
 oo: (n, d0, d1, l, lq, gq, e94) => `${n} zile, ${d0} – ${d1}. QLIKE mediu: ${lq} pentru EWMA cu λ = ${l}, ${e94} pentru EWMA cu λ = 0,94, ${gq} pentru GJR-GARCH-t.`,
 ql: (y, L, m, v, te, th) => `Evaluare din ${y}, ${L}: cea mai mică pierdere o are ${m} (${v}). t DM față de GARCH-t: ${te} pentru EWMA, ${th} pentru Hist-20.`,
 lm: (g1, g100, g250, e1, e100, e250) => `Curba geometrică: ${g1} la lagul 1, ${g100} la lagul 100, ${g250} la lagul 250. Datele: ${e1}, ${e100} și ${e250}.`,
 lm2: (r, p, hl) => `Cu ρ₁ = ${r}, rata care aproximează cel mai bine datele (cele mai mici pătrate pe 250 de laguri) este p = ${p}, cu un timp de înjumătățire de ${CH5_ZILE(hl)}.`,
 qs: (s, x, z, p) => `${s}: ξ̂ = ${x}, ζ̂ = ${z}; testul LR pentru ξ = ζ are p = ${p}.`,
 qs2: (z, q, b) => `Impactul unui șoc ε = 5: 25 în GARCH-t, ${b} în Beta-t-GARCH și ${q} în QSD cu ζ = ${z}.`
};

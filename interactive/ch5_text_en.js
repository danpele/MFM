// Readouts of the Chapter 5 interactive page, written by latex/build_interactive_ch5.py.
window.CH5_TEXT = {
 play: 'Play', pause: 'Pause', gold: 'Gold',
 cl: (s, n, q, hit, base) => `${s}: ${n} days with |r| above the threshold (${q} of the days). After such a day, another follows within the next 5 days in ${hit} of the cases; with independent days it would be ${base}.`,
 ac: (s, a1, d, a2, o1, o2, b) => `${s}, lag 1: ${a1} for r, ${a2} for |r|^${d}. Outside the ±${b} band: ${o1} of 50 autocorrelations of r, ${o2} of 50 of |r|^${d}.`,
 ac2: k => `Excess kurtosis of the returns: ${k}.`,
 si: (be, om, kt, ks, ki, hl) => `β = ${be}, ω = ${om}. Excess kurtosis: ${kt === null ? 'infinite in theory, because (α + β)² + 2α² ≥ 1' : kt + ' in theory'}; on the 2,000 simulated days, ${ks} for GARCH and ${ki} for the i.i.d. series. Half-life: ${hl} days.`,
 dm: (p, h, t, v) => `p = ${p}: the half-life is ${h} days, the delta-method tangent gives ${t} days, and the long-run volatility is ${v} a year.`,
 dm2: (se, seh, lo, hi) => `SE(p̂) = ${se}, so SE(ĥ) ≈ ${seh} days by the delta method. The 95% interval for p, [${lo}, ${hi}], contains p = 1.`,
 ts: (s, a, b, u) => `${s}: ${a}% for the next day, ${b}% on average over 250 days; long-run level: ${u === null ? 'none (α̂ + β̂ ≥ 0.999)' : u + '%'}.`,
 pe: (h, list) => `Share of the shock left after ${h} days: ${list}.`,
 vx: (a, p, hl, c, mv, mg, sh) => `α = ${a}, α + β = ${p}, half-life ${hl} days. Over the chosen period: correlation with the VIX ${c}; mean VIX ${mv}%, mean GARCH ${mg}%; the VIX is above the GARCH volatility on ${sh} of the days.`,
 ni: (e, g, eg, ga) => `After a shock of ${e}%: GJR ${g}, EGARCH ${eg}, GARCH ${ga}.`,
 ni2: (rg, re) => `Variance after a negative shock divided by the variance after a positive shock of the same size: ${rg} (GJR), ${re} (EGARCH).`,
 inn: (o, en, nu, et) => `Residuals below −4: ${o} observed; ${en} expected under the Normal distribution and ${et} under a Student-t with ν = ${nu}.`,
 inn2: (k, kt) => `Excess kurtosis: ${k} for ẑ, ${kt === null ? 'infinite' : kt} for a Student-t with this ν.`,
 oo: (n, d0, d1, l, lq, gq, e94) => `${n} days, ${d0} – ${d1}. Mean QLIKE: ${lq} for EWMA with λ = ${l}, ${e94} for EWMA with λ = 0.94, ${gq} for GJR-GARCH-t.`,
 ql: (y, L, m, v, te, th) => `Evaluation from ${y}, ${L}: the lowest loss is ${m} (${v}). DM t against GARCH-t: ${te} for EWMA, ${th} for Hist-20.`,
 lm: (g1, g100, g250, e1, e100, e250) => `Geometric curve: ${g1} at lag 1, ${g100} at lag 100, ${g250} at lag 250. Data: ${e1}, ${e100} and ${e250}.`,
 lm2: (r, p, hl) => `With ρ₁ = ${r}, the rate that fits the data best (least squares over 250 lags) is p = ${p}, with a half-life of ${hl} days.`,
 qs: (s, x, z, p) => `${s}: ξ̂ = ${x}, ζ̂ = ${z}; the LR test of ξ = ζ has p = ${p}.`,
 qs2: (z, q, b) => `Impact of a shock ε = 5: 25 in GARCH-t, ${b} in Beta-t-GARCH and ${q} in QSD with ζ = ${z}.`
};

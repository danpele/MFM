// Readouts of the Chapter 7 interactive page, written by latex/build_interactive_ch7.py.
window.CH7_TEXT = {
 names: { sp500: 'S&P 500', bet: 'BET', btc: 'Bitcoin', eurron: 'EUR/RON', gold: 'gold' },
 ld: (a, v, nb, N, sh, e, vn, en) => `α = ${a}: historical VaR ${v}, exceeded on ${nb} of ${N} days (${sh}); ES ${e}. Normal distribution with the same mean and standard deviation: VaR ${vn}, ES ${en}.`,
 sa: (p, pa, vs, vp, es, ep, viol) => `Default probability of each bond: ${p}; probability that at least one defaults: ${pa}. VaR 1%: ${vs} for the sum of the two, ${vp} for the portfolio (${viol ? 'subadditivity is violated' : 'subadditivity holds'}). ES 1%: ${es} for the sum, ${ep} for the portfolio.`,
 vl: (a, v, e) => `α = ${a}. VaR: ${v}. ES: ${e}.`,
 pr: (n, k, wv, we, wb, fi, fh, bi, bb) => `Last ${n} days: ES 2.5% is the mean of ${k} losses. Width of the 95% interval: VaR 1% ${wv} pp (HAC); ES 2.5% ${we} pp (HAC) and ${wb} pp (block bootstrap). ES 2.5% on 2000–2026: ${fi} pp (i.i.d.), ${fh} pp (HAC), ${bi} pp (i.i.d. bootstrap), ${bb} pp (block bootstrap).`,
 hf: (d, n, a, h, nh, f, nfh, g, w) => `From 2006-01-03 to ${d} (${n} days), target ${a}: historical VaR on ${w} days exceeded on ${h} of the days (${nh}), FHS on ${f} (${nfh}), GARCH with Normal shocks on ${g}.`,
 hfm: (m, d) => `Largest FHS VaR in the period: ${m}, on ${d}.`,
 cv: (b1, hl, nh, N, rate, pc, pf, cm, b0) => `β₁ = ${b1}, β₀ = ${b0} (set so that the long-run VaR level stays at the estimated one): the half-life of a shock is ${hl} days. 2016–2026: ${nh} exceedances in ${N} days (${rate}); the mean pinball loss is ${pc} for CAViaR and ${pf} for FHS. Largest CAViaR VaR in the COVID-19 crash: ${cm}.`,
 gv: (b, xi, mu, s, y, k, rl, na, nb) => `Block: ${({ week: 'week', month: 'calendar month', quarter: 'quarter', half: 'half-year', year: 'year' })[b]}. GEV: ξ = ${xi}, μ = ${mu}, σ = ${s}. The ${y}-year return level (${k} blocks) is ${rl}; ${na} of ${nb} maxima exceed it.`,
 me: (t, u, nu, xi, b, sl, gm, em) => `The threshold u₀ = ${u} leaves the largest ${t} of the losses above it (${nu} exceedances). GPD: ξ = ${xi}, β = ${b}, slope ξ/(1 − ξ) = ${sl}. Mean excess at u₀: ${gm} from the GPD, ${em} empirical.`,
 gt: (t, sx, sse, sti, sv, bx, bse, bti, bv) => `GPD on the largest ${t} of the losses. S&P 500: ξ = ${sx} (SE ${sse}), tail index ${sti}, VaR 1% ${sv}. Bitcoin: ξ = ${bx} (SE ${bse}), tail index ${bti}, VaR 1% ${bv}.`,
 ce: (a, N, ce, nce, cg, ncg, ch, nch, ex) => `VaR ${a}, 2018–2026 (${N} days, ${ex} exceedances expected): conditional EVT ${ce} (${nce} days), GARCH with Normal shocks ${cg} (${ncg}), historical simulation on 500 days ${ch} (${nch}).`,
 hz: (h, rt, mc, sq, sh) => `h = ${h}: the ratio empirical VaR 1% / (√h × one-day VaR) is ${rt}. S&P 500, ${h}-day VaR 1%: ${mc} by filtered Monte Carlo, ${sq} as √${h} × one-day filtered VaR, ${sh} as √${h} × one-day historical VaR.`,
 pc: (w, vp, vu, red, ep, eu, bv, be, te) => `Weights SPY/TLT/GLD/Bitcoin: ${w}. VaR 1%: ${vp}, against ${vu} undiversified (${red}). ES 2.5%: ${ep}, against ${eu} undiversified. Bitcoin accounts for ${bv} of VaR and ${be} of ES; TLT for ${te} of ES.`,
 bs: (a, rt, nr) => `Ratio ES ${a} / VaR 1%: ${rt}. Under the Normal distribution: ${nr}.`,
 ck: (set, nf, tf, nd, td, lo, hi) => `${set ? 'Predictors: ' + set : 'All four predictor sets'}. Flexible models without networks: ${nf} of ${tf} bars at 1 or above. Deep networks (deep MIDAS included): ${nd} of ${td} bars below 1, between ${lo} and ${hi}.`,
 ai: (y, t1, t2, t3, t4, ok1, ok2) => `Subperiods 2006–${y} and ${y + 1}–2026. FHS against GARCH–Normal: t = ${t1} and ${t2}, so the gain ${ok1 ? 'is' : 'is not'} demonstrated. Conditional EVT against FHS: t = ${t3} and ${t4}, so the gain ${ok2 ? 'is' : 'is not'} demonstrated. The rule: t < −1.96 in both subperiods.`
};

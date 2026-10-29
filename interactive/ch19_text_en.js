// Readouts of the Chapter 19 interactive page, written by latex/build_interactive_ch19.py.
window.CH19_TEXT = {
 play: 'Play', pause: 'Pause', none: 'none',
 bf: (y0, y1, n, k, a, n4, e4) => `${y0}–${y1}: ${n} daily returns. Hill tail index of losses (k = ${k}): ${a}. Days beyond ±4 standard deviations: ${n4}, against ${e4} expected under the Normal distribution.`,
 bf2: (a1, r1, q) => `ACF of |r<sub>t</sub>| at lag 1: ${a1}; ACF of r<sub>t</sub>: ${r1}. Ljung–Box Q(10) on r<sub>t</sub><sup>2</sup>: ${q}, against the critical value 18.3.`,
 hl: h => (isFinite(h) ? `about ${Math.round(h)} trading day${Math.round(h) === 1 ? '' : 's'}` : 'not finite, because α + β ≥ 1'),
 bg: (a, b, p, hl) => `α = ${a}, β = ${b}, persistence α + β = ${p}. Half-life: ${hl}.`,
 bg2: (mx, dm, s, d) => `Peak daily conditional volatility: ${mx}, on ${dm}; at the end of the sample (${d}): ${s}.`,
 bg3: (d, a) => `Long-run volatility √(ω/(1 − α − β)): ${d} a day, ${a} a year.`,
 bg3n: 'With α + β ≥ 1 the unconditional variance is not finite.',
 bg4: (n, s) => `Returns outside the ±2σ̂<sub>t</sub> band: ${n} days (${s}).`,
 bv: (d0, d1, n, e, l) => `${d0} – ${d1}: ${n} days, ${e} breaches expected for the VaR ${l}.`,
 bv2: (xf, m, xm) => `Actual breaches: FHS ${xf}, ${m} ${xm}.`,
 bv3: (v, dv, d, f, m, fm) => `Highest FHS VaR: ${v}, on ${dv}. Forecast for ${d}: FHS ${f}, ${m} ${fm}.`,
 br: (d0, d1, n, l, lo, hi, inn) => `${d0} – ${d1}, T = ${n} days. 95% binomial band if the true rate is ${l}: [${lo}, ${hi}]. Inside the band: ${inn}.`,
 br2: s => `Breach rate and Kupiec p-value: ${s}.`,
 br3: (a, s) => `Rejected at 5% (${a}): ${s}.`,
 adj: { none: 'each test on its own', holm: 'Holm, FWER', bh: 'Benjamini–Hochberg, FDR 5%' },
 kp: (n, pi, a, pw) => `T = ${n} days, true rate ${pi}: the ${a} Kupiec test rejects the model with probability ${pw}.`,
 reg: (lo, hi) => (lo < 0 ? `${hi} breaches or more` : lo === 0 ? `0 breaches, or ${hi} or more` : `at most ${lo} breaches, or ${hi} or more`),
 kp2: s => `Rejection region: ${s}.`,
 kp3: (m, s) => `MDE (power of at least 80%, grid step 0.05 percentage points): ${m}. Actual size of the test at a true rate of 1%: ${s}.`,
 nm: (lab, n, med, iqr, b) => `${lab}: ${n} paths, median ${med} a year, IQR ${iqr} pp. Sampling benchmark, 1.35 × the median SE: ${b} pp.`
};

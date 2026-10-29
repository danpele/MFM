// Readouts of the Chapter 2 interactive page, written by latex/build_interactive_ch2.py.
window.CH2_TEXT = {
 play: 'Play', pause: 'Pause', descr: 'descriptive only',
 rg: (k, f) => `Day ${k}: the value of 1 USD invested at the start is A ${f[0]}, B ${f[1]}, C ${f[2]}, D ${f[3]}.`,
 rgHide: 'Choose the real series, then reveal it with the list above.',
 rgReveal: (s, v, m, sd, a, b) => `Series ${s} is the S&P 500 (${a} – ${b}): 1 USD became ${v} USD. The random walks have the daily drift ${m} and the daily volatility ${sd}, estimated on the S&P 500.`,
 cr: (s, k) => `Standard deviation of the returns: RW1 ${s[0]}, RW2 ${s[1]}, GARCH ${s[2]}. Kurtosis: ${k[0]}, ${k[1]}, ${k[2]} (3 for the Normal distribution).`,
 crG: (a, b, o) => `GARCH: the lag-1 autocorrelation is ${a} for the returns and ${b} for their squares; ω = 1 − α − β = ${o}, so the long-run variance is 1.`,
 cs: (n, m, a, b, bd) => `T = ${n} days: the largest absolute autocorrelation of the returns is ${m}. The autocorrelation of the squares is ${a} at lag 1 and ${b} at lag 20; the ±1.96/√T band is ±${bd}.`,
 csTh: (a, p) => `In theory, the autocorrelation of the squares is ${a} at lag 1 and falls by the factor α + β = ${p} at each lag.`,
 csInf: 'With 3α² + 2αβ + β² ≥ 1 the fourth moment does not exist and the theoretical autocorrelation of the squares is not defined.',
 ac: (k, n, l, ni) => `Lag ${k}: the robust interval excludes zero for ${n} of the 16 series (${l}); the i.i.d. interval would exclude it for ${ni}.`,
 ac2: (k, r, s, si) => `S&P 500: ρ̂${k} = ${r}, robust standard error ${s}, i.i.d. standard error ${si}.`,
 vr: (m, q, v, lo, hi, o, p) => `${m}: VR(${q}) = ${v}, null band [${lo}, ${hi}]; ${o ? 'outside, rejected at 5%' : 'inside, not rejected'}. Chow–Denning over q = 2, 5, 10, 20: p ${p}.`,
 od: (y, n, r, c) => `Evaluation from January ${y}: ${n} monthly forecasts, R²<sub>OS</sub> = ${r}; the final value of the curve is ${c}.`,
 od2: (r, t, p) => `In the lecture (from 1970): R²<sub>OS</sub> = ${r}, Clark–West t = ${t}, one-sided p = ${p}.`,
 ev0: (b, s, a, tn, t) => `TLV: beta ${b}, residual standard deviation ${s} a day; AR₀ = ${a}, t = ${tn} with σ̂ and t = ${t} with the prediction error.`,
 ev: (a, b, c, t, tn) => `CAR[${a}, ${b}]: TLV ${c[0]} (t = ${t[0]}), BRD ${c[1]} (t = ${t[1]}), portfolio ${c[2]} (t = ${t[2]}). For TLV, with σ̂√L: t = ${tn}.`,
 mt: (k, s, n, s3, n3, m) => `${k} rules: ${s} have |t| > 1.96 (${n} rules), ${s3} have |t| > 3.0 (${n3}); the largest |t| is ${m}.`,
 mt2: (k, f) => `If the ${k} tests were independent, the probability of at least one false rejection at 5% would be ${f}.`
};

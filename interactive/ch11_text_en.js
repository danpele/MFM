// Readouts of the Chapter 11 interactive page, written by latex/build_interactive_ch11.py.
window.CH11_TEXT = {
 play: 'Play', pause: 'Pause',
 dk: (a, ex, p5, p2, g) => `Level a = ${a}: the Brownian limit 2(1 − Φ(a)) is ${ex}. Random walk: ${p5} with n = 5 and ${p2} with n = 2,000 (gap to the limit: ${g}).`,
 dk2: c => c ? `Paths on the left that exceed the level a: ${c}.` : 'None of the three paths on the left exceeds the level a.',
 qv: (p, s, m) => `p = ${p}: on the grid with 65,536 intervals, Σ|ΔW|^p = ${s}. ` + (m === 'up' ? 'For p < 2 the sum grows with n.' : m === 'down' ? 'For p > 2 the sum tends to zero.' : 'For p = 2 the sum settles at T = 1.'),
 qv2: (c, d, q) => `${c === '2008' ? 'September 2008 – March 2009' : '20 February – 30 April 2020'}: ${d} of the days and ${q} of the quadratic variation of the S&P 500.`,
 qv3: (s, y, v) => `S&P 500: Σ r² = ${s} over ${y} years, an average volatility of ${v} a year.`,
 dp: (y, a, b) => `With T = ${y} year${y === 1 ? '' : 's'} of data, the half-width of the 95% interval for the drift is ±${a} percentage points for the S&P 500 and ±${b} for Bitcoin.`,
 dp2: (lo, dl, hi, dh, h, s0, s1) => `Rolling windows: the log drift ranges from ${lo}% (window ending ${dl}) to ${hi}% (${dh}); the median half-width of the interval is ±${h} points. Volatility stays between ${s0}% and ${s1}%.`,
 gd: (k, n, e) => `Beyond ±${k} standard deviations: ${n} day${n === 1 ? '' : 's'} in the data, against ${e} expected under the Normal distribution.`,
 gd2: (s, a1, a50, b) => `ACF of ${s}: ${a1} at lag 1 and ${a50} at lag 50. The GBM band stays below ${b} in absolute value.`,
 va: (a, b, k, se, hl, bb) => `${a}–${b}: κ̂ = ${k} (SE ${se}) a year, ` + (hl ? `a half-life of ${hl} years` : 'no mean reversion (κ̂ < 0)') + `; daily AR(1) coefficient b̂ = ${bb}.`,
 va2: (t, s, sd, z) => `θ̂ = ${t}%, σ̂ = ${s}%, stationary standard deviation ${sd}%. ` + (z ? 'The 95% interval for κ includes zero.' : 'The 95% interval for κ excludes zero.'),
 va3: s => `σ̂ = ${s}%. With κ̂ < 0 the fitted process is explosive: there is no long-run mean and no stationary band.`,
 mj: (n, l, s, j, k, kd, ll, lm, lg) => `${n}: λ = ${l} jumps a year, σ = ${s}, jumps account for ${j} of the variance. Implied excess kurtosis: ${k} (data: ${kd}). Log-likelihood: ${ll} (at the MLE: ${lm}; GBM: ${lg}).`,
 mv: (k, d, m, g) => `${k} simulations. Excess kurtosis: ${d} in the data; medians GBM ${m[0]}, Merton ${m[1]}, Heston ${m[2]}. Simulations with kurtosis at least as high as the data: ${g[0]}, ${g[1]}, ${g[2]}.`,
 mv2: (d, m) => `Hill statistic: ${d} in the data; medians GBM ${m[0]}, Merton ${m[1]}, Heston ${m[2]}.`,
 mv3: (d, a) => `ACF of |r| at lag 1: ${d} in the data; medians GBM ${a[0]}, Merton ${a[1]}, Heston ${a[2]}.`,
 ro: (m, a, s) => `The slope of the variogram on k = 1..${m} gives α̂ (OLS) = ${a}; the noise-robust NLLS estimator gives α̂* = ${s}. α = 0 corresponds to Brownian motion.`,
 ro2: (H, b, bs, hl, r, o) => `Fit on h = 1..${H}: β̂ = ${b}, β̂* = ${bs}. OU: half-life ${hl} days, implied autocorrelation at lag 100 ${o}, against ${r} in the data.`
};

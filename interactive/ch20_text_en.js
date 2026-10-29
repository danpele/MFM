// Readouts of the Chapter 20 interactive page, written by latex/build_interactive_ch20.py.
window.CH20_TEXT = {
 play: 'Play', pause: 'Pause',
 months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
 cls: { all: 'all 50 assets', stocks: 'US stocks (40)', futures: 'futures (5)', forex: 'FX (5)' },
 stat: { mean: 'mean', median: 'median' },
 none: 'none',
 week1: '1 week (5 days, as on the slide)', weeks: k => `${k} weeks (${5 * k} days)`,
 vr: (c, n, a, va, da, b, vb, db) => `${c[0].toUpperCase() + c.slice(1)}, highest ${n}-day mean in the first half of 2020: ${a} ${va}% (days ending ${da}), ${b} ${vb}% (${db}).`,
 qr0: (g, k, b) => `${g[0].toUpperCase() + g.slice(1)}${k === 0 ? '' : ', without the ' + k + ' assets with the highest ratios of each model'}; the benchmark is ${b}.`,
 qr: (h, a, ma, da, b, mb, db) => `h = ${h}: ${a} has mean ${ma} and median ${da}; ${b} has mean ${mb} and median ${db}.`,
 mc: (lev, l, g, lh, sk, har) => `${lev}% MCS, ${l}, ${g}. Share of the assets in which the model stays in the set at h = 1, 5 and 22: log-HAR ${lh}; Sig-LK ${sk}; HAR ${har}.`,
 cv1: (d, y, a, b, c) => `Origin ${d}: the target is ${y}%; the forecasts are ${a}% (HAR), ${b}% (log-HAR) and ${c}% (Sig-LK).`,
 cv2: (d0, d, n, a, b, c) => `Mean QLIKE from ${d0} to ${d} (${n} days): HAR ${a}, log-HAR ${b}, Sig-LK ${c}.`,
 sp1: (g, st, c1, c2, c3, a1, a2, r1, r2) => `${g[0].toUpperCase() + g.slice(1)}, ${st} over assets, h = 1. COVID-19 crash: log-HAR ${c1}, Sig-LK ${c2}, HARQ ${c3}. 2–30 April 2025: log-HAR ${a1}, Sig-LK ${a2}. Other days: log-HAR ${r1}, Sig-LK ${r2}.`,
 sp22: (a, b) => `h = 22, COVID-19 crash: Sig-LK ${a}, Sig-L ${b} times the HAR loss.`,
 kw1: (c, N, lo, hi, e, n) => `c = ${c}, N = ${N}: the average weight over the 40 stocks lies between ${lo} and ${hi} times 1/n; the mean effective sample size is ${e} of ${n}.`,
 kw2: (lo, hi, e) => `JPM: the weights lie between ${lo} and ${hi} times 1/n; the effective sample size is ${e}.`,
 kw3: (k, a, dn, df) => `Origin window, first ${k} points: the Lévy area (return, log RV) is ${a}. The closest training window ends on ${dn}, the farthest on ${df}.`,
 ab1: (x, g, k, l, lk) => `Asset left out: ${x}; ${g}. QLIKE relative to log-HAR at h = 1, 5 and 22: log-HAR-K ${k}; Sig-L ${l}; Sig-LK ${lk}.`,
 ab2: (h, s, v) => `At h = ${h}, the highest Sig-LK / log-HAR ratio is that of ${s} (${v}).`
};

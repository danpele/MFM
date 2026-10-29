// Readouts of the Chapter 4 interactive page, written by latex/build_interactive_ch4.py.
window.CH4_TEXT = {
 play: 'Play', pause: 'Pause',
 ta: (v, m, g, gv) => `Chosen portfolio: volatility ${v}, mean return ${m} a year. Minimum variance: ${g} in SPY, volatility ${gv}.`,
 fr: (n, a, b, s) => `${n} sectors. Sharpe ratio: ${a} with short sales, ${b} long-only. Short positions: ${s}.`,
 ee: (e, r, b, ew) => `Median estimated Sharpe ratio: ${e}; realised: ${r}. ${b} of the samples stay below 1/N (${ew}).`,
 rw: (d, a, b) => `${d}: gross exposure is ${a} for MV and ${b} for GMV-LW.`,
 wl: (t, m, ew, at) => `T = ${t} months: the median MV Sharpe ratio is ${m}, against ${ew} for 1/N. MV beats 1/N from T = ${at}.`,
 mp: (k, n, lo, hi) => `${k} of ${n} eigenvalues lie above the band [${lo}, ${hi}].`,
 sh: (d, c, w, lw) => `δ = ${d}: condition number ${c}, largest absolute GMV weight ${w}. Ledoit–Wolf value on the last 60 months: δ = ${lw}.`,
 bl: (p, q, m, k, u) => `XLK − XLU: prior ${p}, view ${q}, posterior ${m} a year. Weights against 1/N: XLK ${k}, XLU ${u}; the others unchanged.`,
 rc: (k, w, r) => `Iteration ${k}: equities and high yield hold ${w} of the capital and ${r} of the risk.`,
 hrp1: 'Step 1: the correlation matrix in the original order of the 16 ETFs.',
 hrp2: 'Step 2: the same matrix in the order of the tree leaves; correlated assets end up next to each other.',
 hrp3: (l, c, m) => `Bisection, level ${l}: ${c} groups; the largest weight is ${m}.`,
 ow: (d, c, s, v, e) => `Up to ${d}, with ${c} bp: the highest Sharpe ratio is ${s} (${v}); 1/N has ${e}.`,
 os: (y, e, m) => `Sectors, evaluation from ${y}: the Sharpe ratio is ${e} for 1/N and ${m} for MV.`,
 co: (c, s, v, m, e) => `At ${c} bp: the highest net Sharpe ratio is ${s} (${v}); MV has ${m}, 1/N ${e}.`,
 st: (o, lo, hi, ph, pb) => `Observed difference: ${o}. 95% interval of the centred draws: [${lo}, ${hi}]. In the lecture: p = ${ph} (HAC), p = ${pb} (studentized bootstrap).`,
 bv: (d, s, v, b) => `Up to ${d}: the highest Sharpe ratio is ${s} (${v}); BET-TR has ${b}.`
};

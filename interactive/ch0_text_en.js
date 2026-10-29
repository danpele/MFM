// Readouts of the Chapter 0 interactive page, written by latex/build_interactive_ch0.py.
window.CH0_TEXT = {
 date: d => `${d.getUTCDate()} ${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getUTCMonth()]} ${d.getUTCFullYear()}`,
 hi: (y, a, b) => `Up to ${y}: ${a} milestones on the exchanges lane and ${b} on the lane of bubbles, panics and crashes.`,
 rr: (a, b, y) => `Window: ${a} – ${b}, ${y} years.`,
 rr2: (n, c, v, se) => `${n}: CAGR ${c}, annualised volatility ${v}; the standard error of the annualised mean return, σ/√Y, is ${se} pp.`,
 dd: (d, c, m, md) => `On ${d}: drawdown ${c}. Maximum drawdown up to this date: ${m}, on ${md}.`,
 ddr: (p, r, y) => `The peak of ${p} was passed again on ${r}, after ${y} years.`,
 ddn: (p, x) => `The index is still ${x} below the peak of ${p}.`,
 vx: (lo, hi, a, b, c, n) => `Of ${n} days: VIX below ${lo} on ${a}, between ${lo} and ${hi} on ${b}, at least ${hi} on ${c}.`,
 co: (w, a, b, c, e) => `Window of ${w} days. S&P 500–TLT: mean rolling correlation ${a} in 2010–2020 and ${b} in 2022–2026. S&P 500–Bitcoin: ${c} in 2016–2019 and ${e} in 2022–2026.`,
 bt: (a, b, m, c, y) => `From ${a} to ${b}: the index grows ${m} times, a CAGR of ${c} over ${y} years.`,
 bt2: (d, p, t, r) => `Largest drawdown in the window: ${d}, from the peak of ${p} to the trough of ${t}; ${r}.`,
 btr: (d, y) => `the peak was reached again on ${d}, after ${y} years`,
 btn: 'the peak was not reached again by Sep 2026',
 bt0: 'The index never fell below its level at the start date.',
 us: (p, b, a, c, n) => `${p}, ${n} days: USDT within ±${b} of 1 USD on ${a} of the days, within ±1% on ${c}.`,
 cc: (d, s, r, q) => `From ${d}: SPY grows ${s} times, RSP ${r} times; the SPY/RSP ratio ends at ${q}.`,
 cc2: c => `Since 3 Jan 2023 the SPY/RSP ratio has risen by ${c}, whatever the start date.`,
 hh: (p, a, b, chi, c) => `With ${p} of investors turned passive, the relative aggregate elasticity is ${a} for χ = 0, ${b} for χ = ${chi} and ${c} for χ = 10.`,
 hh2: (chi, al, r) => `Pass-through rate 1/(1 + χα) for χ = ${chi} and α = ${al}: ${r}.`,
 ai: (m, t, mde, n) => `Full sample (${n} days): mean difference ${m} a year, t = ${t} (Newey–West), MDE ${mde} a year.`,
 ai2: (y1, m1, t1, y2, m2, t2, mde) => `Up to ${y1}: ${m1} (t = ${t1}). From ${y2}: ${m2} (t = ${t2}), MDE ${mde}.`
};

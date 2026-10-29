// Readouts of the Chapter 15 interactive page, written by latex/build_interactive_ch15.py.
(function () {
const F = n => n.toLocaleString('en-US');
const pl = (n, w, ws) => `${F(n)} ${n === 1 ? w : ws}`;
window.CH15_TEXT = {
 play: 'Play', pause: 'Pause',
 agree: ['all sentences', 'agreement of at least 66%', 'agreement of at least 75%', 'agreement of 100%'],
 metric: { acc: 'accuracy', f1: 'macro-F1' },
 best: { acc: 'the highest accuracy', f1: 'the highest macro-F1' },
 dw1: (k, tot, s) => `The ${k} words occur in ${F(tot)} sentences (a sentence is counted once for each of its words); ${s} of them are not labelled negative.`,
 dw2: (l, nl, ns, s) => `The list has ${F(nl)} words. ${F(ns)} sentences contain a word of the list and no ${l === 'gi' ? 'LM' : 'GI'} negative word; ${s} of them are not labelled negative.`,
 ac1: (a, n, m, fb, q, b) => `PhraseBank, ${a} (n = ${n}): ${m} is ${fb} for FinBERT and ${q} for Qwen2.5-7B; "always neutral" gives ${b}.`,
 ac2: (m, best, v, gi, va, lm, b) => `Twitter: ${m} is that of ${best}, ${v}. Dictionaries: GI ${gi}, VADER ${va}, LM ${lm}; "always neutral": ${b}.`,
 ls1: (p, m, a, b, c, fb) => `Twitter, prompt P${p}: ${m} is ${a} for 1.5B, ${b} for 7B and ${c} for 14B; FinBERT has ${fb}.`,
 ls2: (neu, d, n01, n10, p) => `The 1.5B model answers "neutral" for ${neu} of the headlines (66% are labelled neutral). Accuracy of 7B minus accuracy of 1.5B: ${d} percentage points; McNemar test (${F(n01)} against ${F(n10)} headlines): p ${p}.`,
 em: (th, a, best, tb, lr) => `Direction at ${th}° (0° is the first principal component): the AUC of positive against negative headlines is ${a}. The best direction in this plane, at ${tb}°, gives ${best}. Logistic regression on all 384 dimensions has an accuracy of ${lr}.`,
 lc: (n, r, e, lo, hi, t, fb, q, first) => `${F(n)} labels: embeddings + LR ${e}${r > 1 ? ` (from ${lo} to ${hi} across the ${r} resamples)` : ' (the whole training set)'}, TF-IDF + LR ${t}. FinBERT (${fb}) and Qwen2.5-7B (${q}) use no Twitter labels; embeddings beat FinBERT from ${F(first)} labels.`,
 ma1: (s, m, a, n1, b, n2) => `${s === 'monthly' ? 'S&P 500 months' : 'Apple days'}, Qwen2.5-${m}: AUC ${a} before the weights were released (${pl(n1, '', s === 'monthly' ? 'months' : 'days')}) and ${b} after (${pl(n2, '', s === 'monthly' ? 'months' : 'days')}).`,
 ma2: (c, tpr, fpr, b1, b2) => `The rule "rise if P(rise) > ${c}", before the release: ${tpr} of the rises and ${fpr} of the falls are called rises. Balanced accuracy: ${b1} before and ${b2} after the release.`,
 nh: (s, lab, hh, prev, other) => `${s} of the headlines are stamped 00:00 UTC, that is, with the publication date only. On a ${lab} clock this stamp reads ${hh}:00${prev ? ' of the previous calendar day' : ''}, which is not the time the news appeared. Only ${F(other)} headlines carry another stamp.`,
 cn1: (m, n, fb, tf, q, tq, l, tl) => `Stock-days with at least ${pl(m, 'headline', 'headlines')}: ${F(n)}. Day d: FinBERT ${fb} bp (t = ${tf}), Qwen ${q} bp (t = ${tq}), LM ${l} bp (t = ${tl}).`,
 cn2: (fb, tf, q, tq, l, tl) => `Day d+2: FinBERT ${fb} bp (t = ${tf}), Qwen ${q} bp (t = ${tq}), LM ${l} bp (t = ${tl}).`,
 sg1: (lag, d, mu, t, sr, c, srn, be) => `Qwen2.5-7B, return of day d+${lag}, up to ${d}: ${mu} bp a day before costs (Newey–West t = ${t}). The Sharpe ratio is ${sr} before costs and ${srn} at ${c} bp per trade; the break-even cost is ${be} bp.`,
 sg2: (fm, ft, fs, lm, lt, ls) => `FinBERT: ${fm} bp a day (t = ${ft}), Sharpe ratio after costs ${fs}. LM: ${lm} bp a day (t = ${lt}), Sharpe ratio after costs ${ls}.`,
 pp1: (n, wc, wf, wq, cc, cf, cq) => `Browser simulation, n = ${F(n)}, 2,000 replications: the mean width of the interval is ${wc} with human labels only, ${wf} with PPI and FinBERT, ${wq} with PPI and Qwen; coverage is ${cc}, ${cf} and ${cq}.`,
 pp2: (n, wc, wf, cf) => `In the lecture, at n = ${F(n)}: the width is ${wc} with human labels only and ${wf} with PPI and FinBERT; the coverage of PPI with FinBERT is ${cf}.`,
 pp3: (f, q, th) => `Plain means of the scores: FinBERT ${f}, Qwen ${q}, against θ = ${th}; the bias does not shrink with n.`,
 lt: (k, h, a, b, nb) => `${k} of the 12 models get the initial reaction right on more than ${h}% of the days; the median Sharpe ratio of their drift is ${a}${nb ? `, and ${b} for the other ${nb}` : ''}.`,
 sc1: (c, two, k, e, bf) => `Cut-off ${c}: ${two} of the 36 specifications have |t| > ${c}, of which ${k} with t > ${c}. Under the joint null, the expected number with |t| > ${c} is ${e}. Bonferroni cut-off for 36 tests: ${bf}.`,
 sc2: (B, k, p, med, pm, pl, pml) => `With ${F(B)} sign-flip draws: P(at least ${k} specifications with t above the cut-off) = ${p}; P(median t ≥ ${med}) = ${pm}. In the lecture, with 2,000 draws and the cut-off 1.96: ${pl} and ${pml}.`
};
})();

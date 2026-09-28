// ============================================================
// Quiz bank for chapter id 'stylized': Stylized Facts and Returns (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['stylized'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "Validity of the Jarque-Bera p-value",
                "text": "The Hill estimate of the tail index of daily S&P 500 returns is about 3, and the Jarque-Bera statistic is about 45,800. Is its chi-square(2) p-value reliable?",
                "options": [
                    "Yes, because the sample has more than 9,000 observations",
                    "Yes, provided the returns are serially uncorrelated",
                    "No: the chi-square(2) limit of JB requires finite moments up to order 8, which a tail index near 3 rules out",
                    "No, because Jarque-Bera can only be used with fewer than 1,000 observations"
                ],
                "correctExplanation": "The asymptotic variance of the sample kurtosis involves the eighth moment. With a tail index near 3 that moment is infinite, so JB grows with T without a limit and its p-value has no meaning; report quantile-based measures and the tail index instead.",
                "incorrectExplanation": "A large sample does not help when the limit distribution does not exist: the chi-square(2) limit needs finite moments up to order 8."
            },
            "ro": {
                "title": "Validitatea p-valorii Jarque-Bera",
                "text": "Estimarea Hill a indicelui de coadă pentru randamentele zilnice S&P 500 este aproximativ 3, iar statistica Jarque-Bera este aproximativ 45.800. Este fiabilă p-valoarea ei chi-pătrat(2)?",
                "options": [
                    "Da, pentru că eșantionul are peste 9.000 de observații",
                    "Da, cu condiția ca randamentele să fie necorelate serial",
                    "Nu: limita chi-pătrat(2) a JB cere momente finite până la ordinul 8, excluse de un indice de coadă în jur de 3",
                    "Nu, pentru că Jarque-Bera se poate folosi doar sub 1.000 de observații"
                ],
                "correctExplanation": "Varianța asimptotică a kurtosisului de selecție depinde de momentul de ordin opt. Cu un indice de coadă în jur de 3 acest moment este infinit, deci JB crește cu T fără limită și p-valoarea nu are sens; raportați măsuri bazate pe cuantile și indicele de coadă.",
                "incorrectExplanation": "Un eșantion mare nu ajută când distribuția limită nu există: limita chi-pătrat(2) cere momente finite până la ordinul 8."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Autocorrelation band under clustering",
                "text": "Returns are uncorrelated but show volatility clustering. How does the asymptotic variance of the square root of T times the lag-1 sample autocorrelation compare with 1?",
                "options": [
                    "It is larger than 1: it equals E[x_t^2 x_(t-1)^2]/sigma^4, which exceeds 1 under clustering",
                    "It equals 1, because the returns are uncorrelated",
                    "It is smaller than 1, because the sample mean is removed",
                    "It is not defined for uncorrelated returns"
                ],
                "correctExplanation": "For a martingale difference the variance is tau_1 = E[x_t^2 x_(t-1)^2]/sigma^4. Clustering makes large squares follow large squares, so tau_1 > 1 and the i.i.d. band of 1.96/sqrt(T) is too narrow (S&P 500: T tau_1 = 5).",
                "incorrectExplanation": "Zero correlation fixes the mean of the autocorrelation, not its variance: clustering inflates the variance above the i.i.d. value 1."
            },
            "ro": {
                "title": "Banda autocorelației în prezența grupării",
                "text": "Randamentele sunt necorelate, dar volatilitatea se grupează. Cum se compară varianța asimptotică a rădăcinii lui T înmulțite cu autocorelația de selecție de ordin 1 cu 1?",
                "options": [
                    "Este mai mare decât 1: este egală cu E[x_t^2 x_(t-1)^2]/sigma^4, care depășește 1 în prezența grupării",
                    "Este egală cu 1, pentru că randamentele sunt necorelate",
                    "Este mai mică decât 1, pentru că media de selecție este eliminată",
                    "Nu este definită pentru randamente necorelate"
                ],
                "correctExplanation": "Pentru o diferență de martingală varianța este tau_1 = E[x_t^2 x_(t-1)^2]/sigma^4. Gruparea face ca pătratele mari să urmeze pătratelor mari, deci tau_1 > 1 și banda i.i.d. 1,96/sqrt(T) este prea îngustă (S&P 500: T tau_1 = 5).",
                "incorrectExplanation": "Corelația zero fixează media autocorelației, nu varianța ei: gruparea crește varianța peste valoarea i.i.d. 1."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Volatility drag",
                "text": "For Bitcoin 2014-2026 the mean daily simple return times 365 is 65.2% per year, while the realised CAGR is 53.9%. What explains the gap?",
                "options": [
                    "A data error",
                    "Transaction costs",
                    "Volatility drag: the geometric mean is approximately the arithmetic mean minus half the variance",
                    "Bitcoin pays no dividends"
                ],
                "correctExplanation": "mu_geo is approximately mu_arith - sigma^2/2; with volatility of about 67% per year the drag is large.",
                "incorrectExplanation": "The gap is the volatility drag between arithmetic and geometric means."
            },
            "ro": {
                "title": "Frâna volatilității",
                "text": "Pentru Bitcoin 2014-2026, media randamentelor simple zilnice înmulțită cu 365 este 65,2% pe an, iar CAGR realizat este 53,9%. Ce explică diferența?",
                "options": [
                    "O eroare de date",
                    "Costurile de tranzacționare",
                    "Frâna volatilității: media geometrică este aproximativ media aritmetică minus jumătate din varianță",
                    "Bitcoin nu plătește dividende"
                ],
                "correctExplanation": "mu_geo este aproximativ mu_arit - sigma^2/2; la o volatilitate de circa 67% pe an, frâna este mare.",
                "incorrectExplanation": "Diferența este frâna volatilității dintre media aritmetică și cea geometrică."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Standard error of the Hill estimator",
                "text": "The Hill estimator gives a tail index of 3.0 from the k = 225 largest absolute returns. What is the approximate 95% confidence interval under i.i.d. data?",
                "options": [
                    "[2.96, 3.04], using a standard error of 3/sqrt(n) with the full sample",
                    "[2.6, 3.4], using a standard error of alpha/sqrt(k) = 0.2",
                    "[1.0, 5.0], using a standard error of 1",
                    "[2.87, 3.13], using a standard error of 1/sqrt(k)"
                ],
                "correctExplanation": "Asymptotically sqrt(k)(alpha_hat - alpha) is Normal with variance alpha^2, so the standard error is 3/15 = 0.2 and the interval is 3.0 plus or minus 0.39. With volatility clustering a block bootstrap gives a wider interval.",
                "incorrectExplanation": "Only the k tail observations carry information about the tail, and the Fisher information of the Pareto likelihood is k/alpha^2."
            },
            "ro": {
                "title": "Eroarea standard a estimatorului Hill",
                "text": "Estimatorul Hill dă un indice de coadă de 3,0 din cele mai mari k = 225 randamente absolute. Care este aproximativ intervalul de încredere de 95% pentru date i.i.d.?",
                "options": [
                    "[2,96; 3,04], cu o eroare standard de 3/sqrt(n) pe tot eșantionul",
                    "[2,6; 3,4], cu o eroare standard de alpha/sqrt(k) = 0,2",
                    "[1,0; 5,0], cu o eroare standard de 1",
                    "[2,87; 3,13], cu o eroare standard de 1/sqrt(k)"
                ],
                "correctExplanation": "Asimptotic, sqrt(k)(alpha_hat - alpha) urmează distribuția Normală cu varianța alpha^2, deci eroarea standard este 3/15 = 0,2, iar intervalul este 3,0 plus/minus 0,39. Cu grupare, un bootstrap pe blocuri dă un interval mai larg.",
                "incorrectExplanation": "Doar cele k observații din coadă aduc informație despre coadă, iar informația Fisher a verosimilității Pareto este k/alpha^2."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Tail of absolute returns",
                "text": "At a common threshold, the loss tail has index 2.7 and the gain tail has index 3.6. Asymptotically, what is the tail index of |r_t|?",
                "options": [
                    "3.15, the average of the two",
                    "3.6, the lighter tail",
                    "6.3, the sum of the two",
                    "2.7, the heavier tail"
                ],
                "correctExplanation": "P(|X| > x) = P(X > x) + P(X < -x): for large x the term with the smaller index dominates, so the tail index of |X| is min(2.7, 3.6) = 2.7.",
                "incorrectExplanation": "The probability of a large |r| is the sum of the two tail probabilities, and the slower-decaying term dominates far in the tail."
            },
            "ro": {
                "title": "Coada randamentelor absolute",
                "text": "La un prag comun, coada pierderilor are indicele 2,7, iar coada câștigurilor 3,6. Asimptotic, care este indicele de coadă al lui |r_t|?",
                "options": [
                    "3,15, media celor doi",
                    "3,6, coada mai subțire",
                    "6,3, suma celor doi",
                    "2,7, coada mai groasă"
                ],
                "correctExplanation": "P(|X| > x) = P(X > x) + P(X < -x): pentru x mare domină termenul cu indicele mai mic, deci indicele de coadă al lui |X| este min(2,7; 3,6) = 2,7.",
                "incorrectExplanation": "Probabilitatea unui |r| mare este suma celor două probabilități de coadă, iar termenul care scade mai lent domină departe în coadă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Long memory or breaks?",
                "text": "The ACF of absolute returns decays slowly and the local Whittle estimate of d is 0.35-0.48. Which alternative can produce the same picture without long memory?",
                "options": [
                    "A stationary GARCH(1,1) with alpha + beta = 0.9",
                    "I.i.d. Student-t returns with 3 degrees of freedom",
                    "Occasional shifts in the level of the unconditional variance",
                    "Bid-ask bounce in daily closing prices"
                ],
                "correctExplanation": "Rare regime shifts in volatility create a slowly decaying ACF of |r_t| and a positive estimated d (Diebold and Inoue, 2001); re-estimating d on each side of a variance break is a first check.",
                "incorrectExplanation": "A GARCH(1,1) with persistence 0.9 has exponential decay, i.i.d. returns have no autocorrelation in |r_t|, and bid-ask bounce affects the sign of returns, not their size."
            },
            "ro": {
                "title": "Memorie lungă sau rupturi?",
                "text": "ACF a randamentelor absolute scade lent, iar estimarea Whittle locală a lui d este 0,35-0,48. Ce alternativă poate produce aceeași imagine fără memorie lungă?",
                "options": [
                    "Un GARCH(1,1) staționar cu alpha + beta = 0,9",
                    "Randamente i.i.d. Student-t cu 3 grade de libertate",
                    "Schimbări ocazionale ale nivelului varianței necondiționate",
                    "Efectul bid-ask în prețurile de închidere zilnice"
                ],
                "correctExplanation": "Schimbările rare de regim ale volatilității creează o ACF a lui |r_t| care scade lent și un d estimat pozitiv (Diebold și Inoue, 2001); reestimarea lui d de o parte și de alta a unei rupturi de varianță este o primă verificare.",
                "incorrectExplanation": "Un GARCH(1,1) cu persistența 0,9 are scădere exponențială, randamentele i.i.d. nu au autocorelație în |r_t|, iar efectul bid-ask afectează semnul randamentelor, nu mărimea lor."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Ljung-Box on returns vs squared returns",
                "text": "For the S&P 500, Ljung-Box Q(10) is 91.6 on returns and 8,018 on squared returns. What is the main message?",
                "options": [
                    "Returns are strongly predictable in direction",
                    "The test is unreliable because the values differ",
                    "The size of returns (volatility) is far more predictable than their direction",
                    "Squared returns are normally distributed"
                ],
                "correctExplanation": "Autocorrelation of squared returns reflects volatility clustering; the linear autocorrelation of returns is small, even if significant in a large sample.",
                "incorrectExplanation": "The huge Q on squared returns signals volatility clustering, not predictable direction."
            },
            "ro": {
                "title": "Ljung-Box pe randamente vs pătrate",
                "text": "Pentru S&P 500, Ljung-Box Q(10) este 91,6 pe randamente și 8.018 pe randamentele pătratice. Care este mesajul principal?",
                "options": [
                    "Randamentele sunt puternic predictibile ca direcție",
                    "Testul nu este fiabil, pentru că valorile diferă",
                    "Mărimea randamentelor (volatilitatea) este mult mai predictibilă decât direcția lor",
                    "Randamentele pătratice urmează distribuția Normală"
                ],
                "correctExplanation": "Autocorelația randamentelor pătratice reflectă gruparea volatilității; autocorelația liniară a randamentelor este mică, chiar dacă e semnificativă într-un eșantion mare.",
                "incorrectExplanation": "Valoarea uriașă a lui Q pe pătrate semnalează gruparea volatilității, nu o direcție predictibilă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Mixture of normals",
                "text": "Daily volatility is 1% on 90% of days and 3% on 10% of days; conditional on volatility, returns follow the Normal distribution. What is the kurtosis?",
                "options": [
                    "3, because each regime follows the Normal distribution",
                    "1.8",
                    "30",
                    "8.33 = 3 x E[sigma^4] / E[sigma^2]^2"
                ],
                "correctExplanation": "K = 3 x (0.9 x 1 + 0.1 x 81) / (0.9 + 0.1 x 9)^2 = 3 x 9 / 3.24 = 8.33. Random volatility creates heavy tails.",
                "incorrectExplanation": "A mixture of normals with different variances is leptokurtic: K = 3 E[sigma^4]/E[sigma^2]^2 = 8.33."
            },
            "ro": {
                "title": "Mixtură de distribuții Normale",
                "text": "Volatilitatea zilnică este 1% în 90% din zile și 3% în 10% din zile; condiționat de volatilitate, randamentele urmează distribuția Normală. Cât este kurtosisul?",
                "options": [
                    "3, pentru că fiecare regim urmează distribuția Normală",
                    "1,8",
                    "30",
                    "8,33 = 3 x E[sigma^4] / E[sigma^2]^2"
                ],
                "correctExplanation": "K = 3 x (0,9 x 1 + 0,1 x 81) / (0,9 + 0,1 x 9)^2 = 3 x 9 / 3,24 = 8,33. Volatilitatea aleatoare creează cozi groase.",
                "incorrectExplanation": "O mixtură de distribuții Normale cu varianțe diferite este leptokurtică: K = 3 E[sigma^4]/E[sigma^2]^2 = 8,33."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Sharpe ratio on simple returns",
                "text": "S&P 500, 1990-2026: mean log return 8.3% a year, volatility 18.0%. Approximately what is the Sharpe ratio (r_f = 0) on simple returns, the course definition?",
                "options": [
                    "0.55, since the mean simple return is about 8.3% + sigma^2/2 = 9.9%",
                    "0.46, the mean log return divided by the volatility",
                    "0.37, after subtracting the volatility drag once more",
                    "0.18, the volatility itself"
                ],
                "correctExplanation": "The Sharpe ratio uses the arithmetic mean of simple returns: about 8.3% + 0.18^2/2 = 9.9%, and 9.9/18.0 = 0.55. Using the mean log return (0.46) understates it, by a lot for volatile assets such as Bitcoin (0.65 instead of 0.98).",
                "incorrectExplanation": "The mean log return is the arithmetic mean of simple returns minus about sigma^2/2; the Sharpe ratio is defined on the arithmetic mean."
            },
            "ro": {
                "title": "Raportul Sharpe pe randamente simple",
                "text": "S&P 500, 1990-2026: randament log mediu 8,3% pe an, volatilitate 18,0%. Cât este aproximativ raportul Sharpe (r_f = 0) pe randamente simple, definiția din curs?",
                "options": [
                    "0,55, pentru că randamentul simplu mediu este aproximativ 8,3% + sigma^2/2 = 9,9%",
                    "0,46, randamentul log mediu împărțit la volatilitate",
                    "0,37, după ce se scade încă o dată frâna volatilității",
                    "0,18, chiar volatilitatea"
                ],
                "correctExplanation": "Raportul Sharpe folosește media aritmetică a randamentelor simple: aproximativ 8,3% + 0,18^2/2 = 9,9%, iar 9,9/18,0 = 0,55. Media randamentelor log (0,46) îl subestimează, mult pentru active volatile precum Bitcoin (0,65 în loc de 0,98).",
                "incorrectExplanation": "Randamentul log mediu este media aritmetică a randamentelor simple minus aproximativ sigma^2/2; raportul Sharpe se definește pe media aritmetică."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Tail index (Hill estimator)",
                "text": "Hill estimates of the tail index of absolute daily returns lie mostly between 2 and 4 for the five markets. What does this imply?",
                "options": [
                    "Returns follow the Normal distribution",
                    "The variance exists but the population kurtosis very likely does not (it requires alpha > 4), so sample kurtosis is unstable",
                    "Returns have no variance at all",
                    "The tails are thinner than those of the Normal distribution"
                ],
                "correctExplanation": "With power-law tails, moments exist only up to order below alpha: variance needs alpha > 2, kurtosis alpha > 4. Sample kurtosis then depends heavily on a few extreme days. (A Student-t fit is not a tail-index estimator: it is dominated by the centre.)",
                "incorrectExplanation": "A tail index between 2 and 4 means finite variance but a fourth moment that very likely does not exist."
            },
            "ro": {
                "title": "Indicele de coadă (estimatorul Hill)",
                "text": "Estimările Hill ale indicelui de coadă pentru randamentele zilnice absolute sunt în mare parte între 2 și 4 pe cele cinci piețe. Ce implică acest lucru?",
                "options": [
                    "Randamentele urmează distribuția Normală",
                    "Varianța există, dar kurtosisul populației foarte probabil nu (cere alpha > 4), deci kurtosisul de selecție este instabil",
                    "Randamentele nu au deloc varianță",
                    "Cozile sunt mai subțiri decât cele ale distribuției Normale"
                ],
                "correctExplanation": "Cu cozi de tip lege de putere, momentele există doar până la un ordin mai mic decât alpha: varianța cere alpha > 2, kurtosisul alpha > 4. Kurtosisul de selecție depinde atunci mult de câteva zile extreme. (O distribuție Student-t estimată nu este un estimator al indicelui de coadă: este dominată de centru.)",
                "incorrectExplanation": "Un indice de coadă între 2 și 4 înseamnă varianță finită, dar un moment de ordin patru foarte probabil inexistent."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Gain/loss asymmetry",
                "text": "For the S&P 500 the 1% loss quantile is 3.15% and the 99% gain quantile is 2.97%. For EUR/RON the values are 0.76% and 0.94%. What is the correct reading?",
                "options": [
                    "Both markets show larger losses than gains",
                    "EUR/RON is a data error",
                    "Equities show larger losses than gains; for EUR/RON the larger moves are up-moves, i.e. depreciations of the leu",
                    "Quantiles cannot measure asymmetry"
                ],
                "correctExplanation": "Gain/loss asymmetry is typical of equities; for an exchange rate the \"loss\" direction depends on the viewpoint, and here leu depreciations are the larger moves.",
                "incorrectExplanation": "The asymmetry is market-specific: equities crash, the leu depreciates in jumps."
            },
            "ro": {
                "title": "Asimetria câștig/pierdere",
                "text": "Pentru S&P 500, cuantila de pierdere de 1% este 3,15%, iar cuantila de câștig de 99% este 2,97%. Pentru EUR/RON valorile sunt 0,76% și 0,94%. Care este interpretarea corectă?",
                "options": [
                    "Ambele piețe au pierderi mai mari decât câștigurile",
                    "EUR/RON este o eroare de date",
                    "Acțiunile au pierderi mai mari decât câștigurile; la EUR/RON variațiile mai mari sunt creșterile cursului, adică deprecierile leului",
                    "Cuantilele nu pot măsura asimetria"
                ],
                "correctExplanation": "Asimetria câștig/pierdere este tipică acțiunilor; la un curs valutar direcția „pierderii” depinde de punctul de vedere, iar aici deprecierile leului sunt variațiile mai mari.",
                "incorrectExplanation": "Asimetria este specifică pieței: acțiunile se prăbușesc, leul se depreciază în salturi."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Precision of a Sharpe ratio",
                "text": "An annual Sharpe ratio of 0.55 is estimated from 36.7 years of daily returns, assumed i.i.d. What is its approximate standard error?",
                "options": [
                    "0.01, i.e. 1/sqrt(T) with T = 9,245 daily observations, not annualised",
                    "0.17, i.e. about 1/sqrt(Y) with Y = 36.7 years",
                    "0.09, i.e. SR/sqrt(Y)",
                    "0.55, the Sharpe ratio itself"
                ],
                "correctExplanation": "By the delta method Var(SR_daily) is about (1 + SR_daily^2/2)/T; annualising multiplies the standard error by sqrt(P), giving about sqrt(P/T) = 1/sqrt(Y) = 0.17. The span of the sample matters, not the sampling frequency.",
                "incorrectExplanation": "The daily standard error must be annualised with sqrt(P); the result depends on the number of years, not on the number of days."
            },
            "ro": {
                "title": "Precizia unui raport Sharpe",
                "text": "Un raport Sharpe anual de 0,55 este estimat din 36,7 ani de randamente zilnice, presupuse i.i.d. Care este aproximativ eroarea sa standard?",
                "options": [
                    "0,01, adică 1/sqrt(T) cu T = 9.245 de observații zilnice, neanualizat",
                    "0,17, adică aproximativ 1/sqrt(Y) cu Y = 36,7 ani",
                    "0,09, adică SR/sqrt(Y)",
                    "0,55, chiar raportul Sharpe"
                ],
                "correctExplanation": "Prin metoda delta, Var(SR_zilnic) este aproximativ (1 + SR_zilnic^2/2)/T; anualizarea înmulțește eroarea standard cu sqrt(P), deci aproximativ sqrt(P/T) = 1/sqrt(Y) = 0,17. Contează durata eșantionului, nu frecvența.",
                "incorrectExplanation": "Eroarea standard zilnică trebuie anualizată cu sqrt(P); rezultatul depinde de numărul de ani, nu de numărul de zile."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Non-overlapping windows",
                "text": "Why should h-day returns be built from non-overlapping windows when estimating their kurtosis?",
                "options": [
                    "Overlapping windows share observations, create artificial dependence and bias moment estimates",
                    "Overlapping windows produce negative returns",
                    "Non-overlapping windows always give more observations",
                    "Kurtosis is only defined for weekly data"
                ],
                "correctExplanation": "Overlapping h-day sums reuse the same daily returns, so consecutive observations are strongly dependent.",
                "incorrectExplanation": "The problem with overlapping windows is induced dependence between observations."
            },
            "ro": {
                "title": "Ferestre nesuprapuse",
                "text": "De ce trebuie construite randamentele pe h zile din ferestre nesuprapuse atunci când le estimăm kurtosisul?",
                "options": [
                    "Ferestrele suprapuse au observații comune, creează dependență artificială și deplasează estimările momentelor",
                    "Ferestrele suprapuse produc randamente negative",
                    "Ferestrele nesuprapuse dau întotdeauna mai multe observații",
                    "Kurtosisul este definit doar pentru date săptămânale"
                ],
                "correctExplanation": "Sumele suprapuse pe h zile refolosesc aceleași randamente zilnice, deci observațiile consecutive sunt puternic dependente.",
                "incorrectExplanation": "Problema ferestrelor suprapuse este dependența indusă între observații."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Long memory",
                "text": "The ACF of absolute S&P 500 returns is 0.27 at lag 1 and still 0.09 at lag 100. Why is this important?",
                "options": [
                    "It proves returns are predictable in direction",
                    "The decay is much slower than the exponential decay of a short-memory model such as GARCH(1,1)",
                    "It shows that volatility is constant",
                    "It is an artefact of using log returns"
                ],
                "correctExplanation": "Slow, hyperbolic-like decay of the ACF of absolute returns indicates long memory in volatility, which GARCH(1,1) cannot fully reproduce.",
                "incorrectExplanation": "The key point is the slow decay of volatility autocorrelation (long memory)."
            },
            "ro": {
                "title": "Memorie lungă",
                "text": "ACF a randamentelor absolute S&P 500 este 0,27 la lagul 1 și încă 0,09 la lagul 100. De ce este important acest lucru?",
                "options": [
                    "Demonstrează că direcția randamentelor este predictibilă",
                    "Descreșterea este mult mai lentă decât descreșterea exponențială a unui model cu memorie scurtă precum GARCH(1,1)",
                    "Arată că volatilitatea este constantă",
                    "Este un artefact al folosirii randamentelor log"
                ],
                "correctExplanation": "Descreșterea lentă, aproape hiperbolică, a ACF a randamentelor absolute indică memorie lungă în volatilitate, pe care GARCH(1,1) nu o poate reproduce complet.",
                "incorrectExplanation": "Ideea cheie este descreșterea lentă a autocorelației volatilității (memorie lungă)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Taylor effect",
                "text": "For the S&P 500, the autocorrelation of |r_t|^delta peaks at delta = 1.75 (lag 1), 1.5 (lag 5) and 1.25 (lag 20). What does this suggest?",
                "options": [
                    "Squared returns are always the best volatility proxy",
                    "Returns follow the Normal distribution",
                    "At longer lags, absolute-type powers are more persistent than squared returns; motivates robust volatility measures and power-GARCH",
                    "The Taylor effect implies no volatility clustering"
                ],
                "correctExplanation": "The optimum power shifts towards delta = 1 as the lag grows; squared returns (delta = 2) are clearly less persistent at longer lags.",
                "incorrectExplanation": "The Taylor effect favours powers near 1 over squares for measuring persistent volatility."
            },
            "ro": {
                "title": "Efectul Taylor",
                "text": "Pentru S&P 500, autocorelația lui |r_t|^delta este maximă la delta = 1,75 (lagul 1), 1,5 (lagul 5) și 1,25 (lagul 20). Ce sugerează acest lucru?",
                "options": [
                    "Randamentele pătratice sunt mereu cea mai bună aproximare a volatilității",
                    "Randamentele urmează distribuția Normală",
                    "La laguri mari, puterile apropiate de 1 sunt mai persistente decât pătratele; motivează măsuri robuste ale volatilității și modele power-GARCH",
                    "Efectul Taylor implică absența grupării volatilității"
                ],
                "correctExplanation": "Puterea optimă se deplasează spre delta = 1 când lagul crește; randamentele pătratice (delta = 2) sunt clar mai puțin persistente la laguri mari.",
                "incorrectExplanation": "Efectul Taylor favorizează puterile apropiate de 1 în locul pătratelor pentru măsurarea volatilității persistente."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Leverage effect",
                "text": "For the S&P 500, corr(r_t, |r_{t+k}|) is -0.12 at k = 1 and about zero for negative k. What does this mean?",
                "options": [
                    "High volatility today predicts falling prices tomorrow",
                    "Returns are autocorrelated",
                    "Volume predicts returns",
                    "Falling prices today are followed by higher volatility in the following days"
                ],
                "correctExplanation": "A negative correlation between today's return and future absolute returns is the leverage effect; it is specific to equity markets.",
                "incorrectExplanation": "The sign and the timing (k > 0) indicate that losses raise future volatility."
            },
            "ro": {
                "title": "Efectul de levier",
                "text": "Pentru S&P 500, corr(r_t, |r_{t+k}|) este -0,12 la k = 1 și aproape zero pentru k negativ. Ce înseamnă acest lucru?",
                "options": [
                    "Volatilitatea mare de azi prezice scăderi de preț mâine",
                    "Randamentele sunt autocorelate",
                    "Volumul prezice randamentele",
                    "Scăderile de preț de azi sunt urmate de volatilitate mai mare în zilele următoare"
                ],
                "correctExplanation": "O corelație negativă între randamentul de azi și randamentele absolute viitoare este efectul de levier; este specific piețelor de acțiuni.",
                "incorrectExplanation": "Semnul și momentul (k > 0) arată că pierderile cresc volatilitatea viitoare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Leverage across markets",
                "text": "At k = 1 the leverage correlation is -0.12 for BET-TR, -0.07 for Bitcoin, -0.02 for gold and +0.10 for EUR/RON. Which reading is correct?",
                "options": [
                    "The effect is equity-specific; for EUR/RON it is reversed, since up-moves (leu depreciations) raise volatility",
                    "All markets show the same leverage effect",
                    "The effect is strongest for gold",
                    "Bitcoin has the strongest leverage effect"
                ],
                "correctExplanation": "Romanian and US equities share the effect, crypto shows a weak version, gold none, and the leu shows the opposite sign.",
                "incorrectExplanation": "Stylised facts such as leverage depend on the market: equity-like for BET-TR, reversed for EUR/RON."
            },
            "ro": {
                "title": "Levierul pe piețe",
                "text": "La k = 1, corelația de levier este -0,12 pentru BET-TR, -0,07 pentru Bitcoin, -0,02 pentru aur și +0,10 pentru EUR/RON. Care interpretare este corectă?",
                "options": [
                    "Efectul este specific acțiunilor; la EUR/RON este inversat, deoarece creșterile cursului (deprecierile leului) cresc volatilitatea",
                    "Toate piețele au același efect de levier",
                    "Efectul este cel mai puternic la aur",
                    "Bitcoin are cel mai puternic efect de levier"
                ],
                "correctExplanation": "Acțiunile românești și americane au efectul, cripto o versiune slabă, aurul deloc, iar leul semnul opus.",
                "incorrectExplanation": "Fapte stilizate precum levierul depind de piață: de tip acțiuni la BET-TR, inversat la EUR/RON."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Volume and volatility",
                "text": "Abnormal trading volume and absolute returns have a Spearman correlation of 0.25 (S&P 500) and 0.39 (Bitcoin). Which theory explains this?",
                "options": [
                    "The efficient market hypothesis in its strong form",
                    "The mixture-of-distributions hypothesis: information flow drives both volume and volatility (Clark, 1973)",
                    "The leverage effect",
                    "Aggregational Gaussianity"
                ],
                "correctExplanation": "In a subordinated process, returns evolve in random business time driven by information arrival, which also raises trading volume.",
                "incorrectExplanation": "Volume proxies the information flow that drives volatility."
            },
            "ro": {
                "title": "Volum și volatilitate",
                "text": "Volumul anormal și randamentele absolute au corelația Spearman 0,25 (S&P 500) și 0,39 (Bitcoin). Ce teorie explică acest lucru?",
                "options": [
                    "Ipoteza pieței eficiente în forma tare",
                    "Ipoteza mixturii de distribuții: fluxul de informație determină atât volumul, cât și volatilitatea (Clark, 1973)",
                    "Efectul de levier",
                    "Gaussianitatea prin agregare"
                ],
                "correctExplanation": "Într-un proces subordonat, randamentele evoluează într-un timp de afaceri aleator, determinat de sosirea informației, care crește și volumul tranzacționat.",
                "incorrectExplanation": "Volumul aproximează fluxul de informație care determină volatilitatea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "EUR/RON autocorrelation",
                "text": "The official EUR/RON reference rate has a positive lag-1 autocorrelation of 0.17, unlike equities. What is the most plausible explanation?",
                "options": [
                    "Investors can easily earn arbitrage profits",
                    "A mistake in computing log returns",
                    "A managed float: a daily fixing where adjustments are smoothed over several days",
                    "The leu is a crypto-asset"
                ],
                "correctExplanation": "Central-bank management and the fixing procedure smooth exchange-rate adjustments, which creates positive autocorrelation.",
                "incorrectExplanation": "Institutional setting (managed float, fixing) explains the positive autocorrelation."
            },
            "ro": {
                "title": "Autocorelația EUR/RON",
                "text": "Cursul oficial de referință EUR/RON are o autocorelație de ordin 1 pozitivă, de 0,17, spre deosebire de acțiuni. Care este explicația cea mai plauzibilă?",
                "options": [
                    "Investitorii pot obține ușor profituri din arbitraj",
                    "O greșeală în calculul randamentelor log",
                    "O flotare controlată: un fixing zilnic, cu ajustări netezite pe mai multe zile",
                    "Leul este un criptoactiv"
                ],
                "correctExplanation": "Administrarea de către banca centrală și procedura de fixing netezesc ajustările cursului, ceea ce creează autocorelație pozitivă.",
                "incorrectExplanation": "Cadrul instituțional (flotare controlată, fixing) explică autocorelația pozitivă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Data quality",
                "text": "A free exchange-quote series for EUR/RON shows lag-1 autocorrelation around -0.5 in several years and isolated moves of +/-15% reversed the next day. What should you do?",
                "options": [
                    "Report it as a new stylised fact of the leu",
                    "Delete all returns larger than 1%",
                    "Use a longer sample of the same series",
                    "Treat it as quote errors and use the official reference rate (or clean the ticks explicitly)"
                ],
                "correctExplanation": "Isolated spikes that reverse the next day create spurious negative autocorrelation and inflate kurtosis; official reference rates avoid the problem.",
                "incorrectExplanation": "Spikes that immediately reverse are data errors, not market behaviour."
            },
            "ro": {
                "title": "Calitatea datelor",
                "text": "O serie gratuită de cotații EUR/RON are autocorelație de ordin 1 în jur de -0,5 în mai mulți ani și variații izolate de +/-15% inversate a doua zi. Ce trebuie făcut?",
                "options": [
                    "Raportarea unui nou fapt stilizat al leului",
                    "Ștergerea tuturor randamentelor mai mari de 1%",
                    "Folosirea unui eșantion mai lung din aceeași serie",
                    "Tratarea lor ca erori de cotare și folosirea cursului oficial de referință (sau curățarea explicită a cotațiilor)"
                ],
                "correctExplanation": "Salturile izolate care se inversează a doua zi creează autocorelație negativă falsă și umflă kurtosisul; cursurile oficiale de referință evită problema.",
                "incorrectExplanation": "Salturile care se inversează imediat sunt erori de date, nu comportament al pieței."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Illiquid markets",
                "text": "BET-TR has a positive lag-1 autocorrelation (0.06), while the S&P 500 has -0.08. What is a standard explanation?",
                "options": [
                    "Non-synchronous trading of less liquid index constituents, so prices incorporate news over several days",
                    "The BET-TR index is computed with errors",
                    "Romanian investors are irrational",
                    "Dividends are reinvested"
                ],
                "correctExplanation": "When some constituents trade infrequently, index returns adjust with a lag, which induces positive autocorrelation (Campbell, Lo and MacKinlay, 1997, ch. 3).",
                "incorrectExplanation": "Thin trading and non-synchronous prices explain positive index autocorrelation."
            },
            "ro": {
                "title": "Piețe nelichide",
                "text": "BET-TR are o autocorelație de ordin 1 pozitivă (0,06), iar S&P 500 are -0,08. Care este o explicație standard?",
                "options": [
                    "Tranzacționarea nesincronă a componentelor mai puțin lichide ale indicelui, astfel încât prețurile încorporează știrile în mai multe zile",
                    "Indicele BET-TR este calculat cu erori",
                    "Investitorii români sunt iraționali",
                    "Dividendele sunt reinvestite"
                ],
                "correctExplanation": "Când unele componente se tranzacționează rar, randamentele indicelui se ajustează cu întârziere, ceea ce induce autocorelație pozitivă (Campbell, Lo și MacKinlay, 1997, cap. 3).",
                "incorrectExplanation": "Tranzacționarea rară și prețurile nesincrone explică autocorelația pozitivă a indicelui."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Range-based estimators",
                "text": "On the S&P 500 (2008-2026) close-to-close volatility averages 16.4%, while Parkinson gives 13.0%. Why is Parkinson lower?",
                "options": [
                    "Parkinson is biased upwards",
                    "It uses only the intraday high-low range and misses overnight gaps (close-to-open jumps)",
                    "The S&P 500 has no intraday volatility",
                    "Close-to-close uses a longer window"
                ],
                "correctExplanation": "The daily range captures intraday variation only; overnight jumps are part of close-to-close returns but not of the range. Yang-Zhang adds them back, but on the index it reaches only 13.9% because the index open is partly stale (16.8% on the SPY ETF).",
                "incorrectExplanation": "Pure range estimators ignore the overnight component of volatility."
            },
            "ro": {
                "title": "Estimatori bazați pe amplitudine",
                "text": "Pe S&P 500 (2008-2026), volatilitatea închidere-închidere are media 16,4%, iar Parkinson dă 13,0%. De ce este Parkinson mai mic?",
                "options": [
                    "Parkinson este deplasat în sus",
                    "Folosește doar amplitudinea maxim-minim din timpul zilei și ratează salturile de peste noapte (închidere-deschidere)",
                    "S&P 500 nu are volatilitate intraday",
                    "Estimatorul închidere-închidere folosește o fereastră mai lungă"
                ],
                "correctExplanation": "Amplitudinea zilnică surprinde doar variația din timpul zilei; salturile de peste noapte fac parte din randamentele închidere-închidere, dar nu din amplitudine. Yang-Zhang le readaugă, dar pe indice ajunge doar la 13,9%, pentru că deschiderea indicelui este parțial veche (16,8% pe ETF-ul SPY).",
                "incorrectExplanation": "Estimatorii bazați doar pe amplitudine ignoră componenta de peste noapte a volatilității."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Non-synchronous trading",
                "text": "BET-TR and S&P 500 daily returns have correlation 0.31 on the same day and 0.12 with the S&P 500 lagged one day (Bucharest closes before New York). Which is the best estimate of their co-movement?",
                "options": [
                    "0.31, the same-day correlation",
                    "0.12, the lagged correlation",
                    "0.19, the difference of the two",
                    "About 0.43, the Dimson / Scholes-Williams sum, close to the weekly correlation of 0.46"
                ],
                "correctExplanation": "US news after the Bucharest close reaches BET-TR only on the next day, so part of the co-movement appears at lag 1. Summing the lead-lag correlations recovers about 0.43, in line with the weekly 0.46.",
                "incorrectExplanation": "Asynchronous closes split the common reaction across two days; the same-day correlation alone understates the link."
            },
            "ro": {
                "title": "Tranzacționare nesincronă",
                "text": "Randamentele zilnice BET-TR și S&P 500 au corelația 0,31 în aceeași zi și 0,12 cu S&P 500 din ziua precedentă (Bucureștiul închide înaintea New York-ului). Care este cea mai bună estimare a mișcării lor comune?",
                "options": [
                    "0,31, corelația din aceeași zi",
                    "0,12, corelația cu decalaj",
                    "0,19, diferența celor două",
                    "Aproximativ 0,43, suma Dimson / Scholes-Williams, apropiată de corelația săptămânală de 0,46"
                ],
                "correctExplanation": "Știrile americane de după închiderea bursei din București ajung în BET-TR abia a doua zi, deci o parte din mișcarea comună apare la decalajul 1. Suma corelațiilor cu decalaj recuperează aproximativ 0,43, în acord cu valoarea săptămânală de 0,46.",
                "incorrectExplanation": "Închiderile nesincrone împart reacția comună pe două zile; corelația din aceeași zi, singură, subestimează legătura."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Fair comparisons",
                "text": "On common dates 2014-2026 BET-TR has a Sharpe ratio of 1.36 and the S&P 500 of 0.75. Why is this comparison not fully fair?",
                "options": [
                    "Sharpe ratios cannot be computed for indices",
                    "The S&P 500 has more observations",
                    "BET-TR is more volatile",
                    "BET-TR includes reinvested dividends while the S&P 500 price index does not, and the currencies differ (RON vs USD)"
                ],
                "correctExplanation": "Comparisons require the same return definition (price vs total return), the same currency and the same period.",
                "incorrectExplanation": "Price versus total-return indices and different currencies bias the comparison."
            },
            "ro": {
                "title": "Comparații corecte",
                "text": "Pe datele comune 2014-2026, BET-TR are raportul Sharpe 1,36, iar S&P 500 are 0,75. De ce nu este comparația pe deplin corectă?",
                "options": [
                    "Raportul Sharpe nu poate fi calculat pentru indici",
                    "S&P 500 are mai multe observații",
                    "BET-TR este mai volatil",
                    "BET-TR include dividendele reinvestite, iar indicele de preț S&P 500 nu, iar monedele diferă (RON vs USD)"
                ],
                "correctExplanation": "Comparațiile cer aceeași definiție a randamentului (preț vs randament total), aceeași monedă și aceeași perioadă.",
                "incorrectExplanation": "Indicii de preț vs de randament total și monedele diferite deplasează comparația."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: excess kurtosis in SciPy",
                "text": "An AI assistant writes: \"scipy.stats.kurtosis(r) returns 5.2 for these daily returns, so the excess kurtosis is 5.2 − 3 = 2.2.\" What is wrong?",
                "options": [
                    "Kurtosis must be computed on prices, not on returns",
                    "By default (fisher=True) SciPy already returns the excess kurtosis: it is 5.2, and the kurtosis is 8.2",
                    "The distribution of daily returns has kurtosis 0, so nothing should be subtracted or added",
                    "Excess kurtosis is the kurtosis divided by 3, so it is 1.73"
                ],
                "correctExplanation": "scipy.stats.kurtosis uses fisher=True by default and returns kurtosis − 3; subtracting 3 again understates the tails. Check the documentation or a simulated sample from the Normal distribution, which gives about 0.",
                "incorrectExplanation": "SciPy's default already subtracts 3 (fisher=True): the excess kurtosis is 5.2; a simulated sample from the Normal distribution returns about 0, not 3."
            },
            "ro": {
                "title": "Găsiți eroarea AI: excesul de kurtosis în SciPy",
                "text": "Un asistent AI scrie: „scipy.stats.kurtosis(r) întoarce 5,2 pentru aceste randamente zilnice, deci excesul de kurtosis este 5,2 − 3 = 2,2.” Ce este greșit?",
                "options": [
                    "Kurtosisul se calculează pe prețuri, nu pe randamente",
                    "Implicit (fisher=True) SciPy întoarce deja excesul de kurtosis: acesta este 5,2, iar kurtosisul este 8,2",
                    "Distribuția randamentelor zilnice are kurtosis 0, deci nu se scade și nu se adună nimic",
                    "Excesul de kurtosis este kurtosisul împărțit la 3, deci 1,73"
                ],
                "correctExplanation": "scipy.stats.kurtosis folosește implicit fisher=True și întoarce kurtosis − 3; scăderea încă o dată a lui 3 subestimează cozile. Verificați documentația sau o selecție simulată din distribuția Normală, care dă aproximativ 0.",
                "incorrectExplanation": "Setarea implicită din SciPy scade deja 3 (fisher=True): excesul de kurtosis este 5,2; o selecție simulată din distribuția Normală dă aproximativ 0, nu 3."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the AI error: Ljung–Box on squared returns",
                "text": "An AI assistant writes: \"The Ljung–Box test on squared daily returns gives Q(10) = 714, p < 0.001: the returns are autocorrelated, so the index is predictable.\" What is wrong?",
                "options": [
                    "Ljung–Box needs at least 50 lags to be valid",
                    "A p-value below 0.001 means the null hypothesis is true",
                    "Squared returns cannot be used in any test, because they are always positive",
                    "The test on r² detects volatility clustering; autocorrelation of returns must be tested on r itself, with a robust version"
                ],
                "correctExplanation": "Dependence in r² is volatility clustering: returns can be uncorrelated while their squares are not. Predictability of returns is tested with Ljung–Box on r, using the heteroskedasticity-robust version.",
                "incorrectExplanation": "A significant Ljung–Box on squared returns shows volatility clustering, not predictable returns; test r itself, with the robust statistic."
            },
            "ro": {
                "title": "Găsiți eroarea AI: Ljung–Box pe randamentele la pătrat",
                "text": "Un asistent AI scrie: „Testul Ljung–Box pe randamentele zilnice la pătrat dă Q(10) = 714, p < 0,001: randamentele sunt autocorelate, deci indicele este predictibil.” Ce este greșit?",
                "options": [
                    "Ljung–Box are nevoie de cel puțin 50 de laguri ca să fie valid",
                    "Un p-value sub 0,001 înseamnă că ipoteza nulă este adevărată",
                    "Randamentele la pătrat nu pot fi folosite în niciun test, pentru că sunt mereu pozitive",
                    "Testul pe r² detectează gruparea volatilității; autocorelația randamentelor se testează pe r, cu versiunea robustă"
                ],
                "correctExplanation": "Dependența în r² înseamnă volatilitate grupată: randamentele pot fi necorelate, iar pătratele lor nu. Predictibilitatea randamentelor se testează cu Ljung–Box pe r, în versiunea robustă la heteroscedasticitate.",
                "incorrectExplanation": "Un Ljung–Box semnificativ pe randamentele la pătrat arată gruparea volatilității, nu randamente predictibile; testați chiar r, cu statistica robustă."
            }
        }
    ]
};

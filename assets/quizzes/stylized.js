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
            "correct": 0,
            "en": {
                "title": "Time aggregation",
                "text": "A price goes from 100 to 150 and then back to 75. Which statement is correct?",
                "options": [
                    "The sum of the two log returns, ln 1.5 + ln 0.5 = -0.288, gives exactly the total log return ln 0.75",
                    "The sum of the two simple returns (+50% and -50%) gives exactly the total return",
                    "Simple and log returns always coincide over two periods",
                    "Log returns cannot be computed when the price falls"
                ],
                "correctExplanation": "Log returns are additive over time: the multi-period log return is the sum of one-period log returns.",
                "incorrectExplanation": "Simple returns multiply over time; only log returns add up over time."
            },
            "ro": {
                "title": "Agregarea în timp",
                "text": "Un preț crește de la 100 la 150 și apoi scade la 75. Care afirmație este corectă?",
                "options": [
                    "Suma celor două randamente log, ln 1,5 + ln 0,5 = -0,288, dă exact randamentul log total ln 0,75",
                    "Suma celor două randamente simple (+50% și -50%) dă exact randamentul total",
                    "Randamentele simple și log coincid întotdeauna pe două perioade",
                    "Randamentele log nu pot fi calculate când prețul scade"
                ],
                "correctExplanation": "Randamentele log sunt aditive în timp: randamentul log pe mai multe perioade este suma randamentelor log pe o perioadă.",
                "incorrectExplanation": "Randamentele simple se înmulțesc în timp; doar randamentele log se adună în timp."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Portfolio aggregation",
                "text": "A 50/50 portfolio holds asset A (R = +10%) and asset B (R = -10%). Which return aggregates exactly across assets?",
                "options": [
                    "The weighted average of log returns",
                    "The weighted average of simple returns, which gives exactly 0%",
                    "Neither: portfolio returns cannot be computed from asset returns",
                    "Both give exactly the same result"
                ],
                "correctExplanation": "Simple returns aggregate linearly across assets: R_p = sum of w_i R_i. The weighted log return (-0.005) differs from the true portfolio log return (0).",
                "incorrectExplanation": "Across assets, simple returns aggregate exactly; log returns only approximately."
            },
            "ro": {
                "title": "Agregarea în portofoliu",
                "text": "Un portofoliu 50/50 conține activul A (R = +10%) și activul B (R = -10%). Ce randament se agregă exact între active?",
                "options": [
                    "Media ponderată a randamentelor log",
                    "Media ponderată a randamentelor simple, care dă exact 0%",
                    "Niciunul: randamentul portofoliului nu poate fi calculat din randamentele activelor",
                    "Ambele dau exact același rezultat"
                ],
                "correctExplanation": "Randamentele simple se agregă liniar între active: R_p = suma w_i R_i. Randamentul log ponderat (-0,005) diferă de randamentul log real al portofoliului (0).",
                "incorrectExplanation": "Între active, randamentele simple se agregă exact; cele log doar aproximativ."
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
            "correct": 3,
            "en": {
                "title": "Annualisation",
                "text": "Bitcoin has a daily volatility of 3.5%. Which annualised volatility is appropriate?",
                "options": [
                    "3.5% x 252 = 882%",
                    "3.5% x sqrt(252) = 55.6%",
                    "3.5% x 12 = 42%",
                    "3.5% x sqrt(365) = 66.9%, because crypto trades every calendar day"
                ],
                "correctExplanation": "Crypto-assets trade 365 days per year, so P = 365 in the square-root-of-time rule.",
                "incorrectExplanation": "Use P = 365 for crypto and the square-root rule, not a linear multiplication."
            },
            "ro": {
                "title": "Anualizare",
                "text": "Bitcoin are volatilitatea zilnică de 3,5%. Ce volatilitate anualizată este potrivită?",
                "options": [
                    "3,5% x 252 = 882%",
                    "3,5% x rad(252) = 55,6%",
                    "3,5% x 12 = 42%",
                    "3,5% x rad(365) = 66,9%, pentru că cripto se tranzacționează în fiecare zi calendaristică"
                ],
                "correctExplanation": "Criptoactivele se tranzacționează 365 de zile pe an, deci P = 365 în regula rădăcinii pătrate a timpului.",
                "incorrectExplanation": "Folosiți P = 365 pentru cripto și regula rădăcinii pătrate, nu o înmulțire liniară."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Square-root-of-time rule",
                "text": "Under which assumption is sigma_ann = sqrt(P) x sigma_daily exact?",
                "options": [
                    "Returns are serially uncorrelated with constant variance",
                    "Returns are normally distributed, whatever their dependence",
                    "The asset pays no dividends",
                    "The sample is longer than one year"
                ],
                "correctExplanation": "The variance of a sum equals the sum of variances only without autocorrelation and with a constant variance; volatility clustering and autocorrelation break the rule.",
                "incorrectExplanation": "The rule requires uncorrelated returns with constant variance; normality alone is not enough."
            },
            "ro": {
                "title": "Regula rădăcinii pătrate a timpului",
                "text": "În ce ipoteză este exactă formula sigma_an = rad(P) x sigma_zilnic?",
                "options": [
                    "Randamentele sunt necorelate serial și au varianță constantă",
                    "Randamentele urmează distribuția Normală, indiferent de dependență",
                    "Activul nu plătește dividende",
                    "Eșantionul este mai lung de un an"
                ],
                "correctExplanation": "Varianța unei sume este suma varianțelor doar fără autocorelație și cu varianță constantă; gruparea volatilității și autocorelația invalidează regula.",
                "incorrectExplanation": "Regula cere randamente necorelate cu varianță constantă; normalitatea singură nu este suficientă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Jarque-Bera",
                "text": "The Jarque-Bera statistic for S&P 500 daily log returns (1990-2026) is about 45,800. What do you conclude?",
                "options": [
                    "Returns follow the Normal distribution because the p-value is large",
                    "Normality is strongly rejected: the 5% critical value of the chi-square with 2 degrees of freedom is 5.99",
                    "The test is invalid for financial data",
                    "Returns have zero kurtosis"
                ],
                "correctExplanation": "JB is asymptotically chi-square with 2 degrees of freedom; 45,800 is far beyond 5.99, driven by excess kurtosis of about 10.9.",
                "incorrectExplanation": "A JB value in the tens of thousands means a decisive rejection of normality."
            },
            "ro": {
                "title": "Jarque-Bera",
                "text": "Statistica Jarque-Bera pentru randamentele log zilnice S&P 500 (1990-2026) este circa 45.800. Ce concluzionați?",
                "options": [
                    "Randamentele urmează distribuția Normală, pentru că valoarea p este mare",
                    "Normalitatea este respinsă categoric: valoarea critică la 5% a lui chi-pătrat cu 2 grade de libertate este 5,99",
                    "Testul nu este valid pentru date financiare",
                    "Randamentele au kurtosis zero"
                ],
                "correctExplanation": "JB este asimptotic chi-pătrat cu 2 grade de libertate; 45.800 depășește cu mult 5,99, din cauza excesului de kurtosis de circa 10,9.",
                "incorrectExplanation": "O valoare JB de ordinul zecilor de mii înseamnă respingerea categorică a normalității."
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
                "title": "Five-sigma days",
                "text": "Under the Normal distribution about 0.005 daily moves beyond 5 standard deviations are expected in the S&P 500 sample 1990-2026. How many were observed?",
                "options": [
                    "30",
                    "0",
                    "1",
                    "About 2,500"
                ],
                "correctExplanation": "Thirty 5-sigma days versus 0.005 expected: extreme moves are thousands of times more frequent than the Normal distribution predicts.",
                "incorrectExplanation": "The observed count (30) exceeds the expectation under the Normal distribution by several thousand times."
            },
            "ro": {
                "title": "Zile de cinci sigma",
                "text": "Sub distribuția Normală, în eșantionul S&P 500 1990-2026 ar fi de așteptat circa 0,005 variații zilnice dincolo de 5 abateri standard. Câte au fost observate?",
                "options": [
                    "30",
                    "0",
                    "1",
                    "Circa 2.500"
                ],
                "correctExplanation": "Treizeci de zile de 5 sigma față de 0,005 așteptate: variațiile extreme sunt de mii de ori mai frecvente decât prezice distribuția Normală.",
                "incorrectExplanation": "Numărul observat (30) depășește de câteva mii de ori așteptarea sub normalitate."
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
            "correct": 3,
            "en": {
                "title": "Aggregational Gaussianity",
                "text": "Excess kurtosis of S&P 500 log returns is 10.9 at the daily horizon and 1.6 at 60 days. Which stylised fact is this?",
                "options": [
                    "Leverage effect",
                    "Volatility clustering",
                    "Absence of autocorrelation",
                    "Aggregational Gaussianity: the distribution approaches the Normal distribution as the horizon increases"
                ],
                "correctExplanation": "Summing returns over longer horizons makes the distribution closer to the Normal distribution (a central limit effect), though volatility clustering slows the convergence.",
                "incorrectExplanation": "Thinner tails at longer horizons is aggregational Gaussianity."
            },
            "ro": {
                "title": "Gaussianitate prin agregare",
                "text": "Excesul de kurtosis al randamentelor log S&P 500 este 10,9 la orizont zilnic și 1,6 la 60 de zile. Ce fapt stilizat este acesta?",
                "options": [
                    "Efectul de levier",
                    "Gruparea volatilității",
                    "Absența autocorelației",
                    "Gaussianitatea prin agregare: distribuția se apropie de distribuția Normală când orizontul crește"
                ],
                "correctExplanation": "Însumarea randamentelor pe orizonturi mai lungi apropie distribuția de distribuția Normală (un efect de tip limită centrală), deși gruparea volatilității încetinește convergența.",
                "incorrectExplanation": "Cozile mai subțiri la orizonturi mai lungi reprezintă gaussianitatea prin agregare."
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
            "correct": 2,
            "en": {
                "title": "Sortino ratio",
                "text": "How does the Sortino ratio differ from the Sharpe ratio?",
                "options": [
                    "It uses the maximum drawdown in the denominator",
                    "It uses log returns instead of simple returns",
                    "It divides excess return by the downside deviation, penalising only negative returns",
                    "It is always smaller than the Sharpe ratio"
                ],
                "correctExplanation": "Sortino and van der Meer (1991) replace the standard deviation with the downside deviation sqrt(E[min(r,0)^2]).",
                "incorrectExplanation": "The Sortino ratio penalises only downside variability."
            },
            "ro": {
                "title": "Raportul Sortino",
                "text": "Prin ce diferă raportul Sortino de raportul Sharpe?",
                "options": [
                    "Folosește drawdown-ul maxim la numitor",
                    "Folosește randamente log în loc de randamente simple",
                    "Împarte randamentul în exces la abaterea negativă, penalizând doar randamentele negative",
                    "Este întotdeauna mai mic decât raportul Sharpe"
                ],
                "correctExplanation": "Sortino și van der Meer (1991) înlocuiesc abaterea standard cu abaterea negativă rad(E[min(r,0)^2]).",
                "incorrectExplanation": "Raportul Sortino penalizează doar variabilitatea negativă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Fair comparisons",
                "text": "On common dates 2014-2026 BET-TR has a Sharpe ratio of 1.27 and the S&P 500 of 0.65. Why is this comparison not fully fair?",
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
                "text": "Pe datele comune 2014-2026, BET-TR are raportul Sharpe 1,27, iar S&P 500 are 0,65. De ce nu este comparația pe deplin corectă?",
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

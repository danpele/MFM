// ============================================================
// Quiz bank for chapter id 'realized-vol': Realized Volatility (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['realized-vol'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Stable convergence and the feasible CLT",
                "text": "Integrated quarticity IQ_t is random. Why may we still divide RV_t − IV_t by sqrt(2 RQ_t / M) and use N(0,1) quantiles?",
                "options": [
                    "Because the limit is mixed normal and the convergence is stable, so studentising by a consistent estimate of the random variance gives N(0,1)",
                    "Because integrated quarticity is constant within the day",
                    "Because intraday returns are Normal and independent of volatility",
                    "Because RQ_t is an unbiased estimator of IQ_t"
                ],
                "correctExplanation": "Barndorff-Nielsen and Shephard: sqrt(M)(RV − IV) converges stably to MN(0, 2 IQ); stable convergence allows studentising by sqrt(2 RQ/M), because RQ consistently estimates the random IQ.",
                "incorrectExplanation": "The argument needs neither constant volatility nor Normal returns nor unbiasedness of RQ: it rests on a mixed-normal limit that holds stably, jointly with the path of volatility."
            },
            "ro": {
                "title": "Convergența stabilă și CLT fezabilă",
                "text": "Cvarticitatea integrată IQ_t este aleatoare. De ce putem totuși împărți RV_t − IV_t la sqrt(2 RQ_t / M) și folosi cuantilele N(0,1)?",
                "options": [
                    "Deoarece limita este Normală mixtă, iar convergența este stabilă, deci studentizarea cu o estimare consistentă a varianței aleatoare dă N(0,1)",
                    "Deoarece cvarticitatea integrată este constantă în cursul zilei",
                    "Deoarece randamentele intraday sînt Normale și independente de volatilitate",
                    "Deoarece RQ_t este un estimator nedeplasat al lui IQ_t"
                ],
                "correctExplanation": "Barndorff-Nielsen și Shephard: sqrt(M)(RV − IV) converge stabil la MN(0, 2 IQ); convergența stabilă permite studentizarea cu sqrt(2 RQ/M), deoarece RQ estimează consistent IQ aleator.",
                "incorrectExplanation": "Argumentul nu cere volatilitate constantă, randamente Normale sau un RQ nedeplasat: se bazează pe o limită Normală mixtă valabilă stabil, împreună cu traiectoria volatilității."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "What RV converges to",
                "text": "Without noise and jumps, as the number of intraday returns grows, RV_t converges to:",
                "options": [
                    "Zero, because each return becomes very small",
                    "The integrated variance, the integral of the spot variance over the day",
                    "The squared daily return",
                    "The unconditional variance of the return series"
                ],
                "correctExplanation": "Barndorff-Nielsen and Shephard: RV_t converges to the quadratic variation, which equals integrated variance when there are no jumps.",
                "incorrectExplanation": "The returns shrink but their number grows; the sum of squares converges to integrated variance, a quantity specific to day t."
            },
            "ro": {
                "title": "Limita RV",
                "text": "Fără zgomot și fără salturi, cînd numărul de randamente intraday crește, RV_t converge la:",
                "options": [
                    "Zero, deoarece fiecare randament devine foarte mic",
                    "Varianța integrată, integrala varianței instantanee pe durata zilei",
                    "Randamentul zilnic la pătrat",
                    "Varianța necondiționată a seriei de randamente"
                ],
                "correctExplanation": "Barndorff-Nielsen și Shephard: RV_t converge la variația pătratică, egală cu varianța integrată cînd nu există salturi.",
                "incorrectExplanation": "Randamentele scad, dar numărul lor crește; suma pătratelor converge la varianța integrată, o mărime specifică zilei t."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Precision of RV",
                "text": "With 78 five-minute returns and roughly constant volatility, the relative standard error of RV is about:",
                "options": [
                    "0.1%, since RV is exact",
                    "141%, as for the squared daily return",
                    "16%, since it is close to the square root of 2/M",
                    "50%, whatever M is"
                ],
                "correctExplanation": "se(RV)/RV is approximately the square root of 2/M = 2/78, about 0.16.",
                "incorrectExplanation": "RV is a measurement with error; with M returns its relative error is about the square root of 2/M, which gives 16% for M = 78."
            },
            "ro": {
                "title": "Precizia RV",
                "text": "Cu 78 de randamente de 5 minute și volatilitate aproximativ constantă, eroarea standard relativă a RV este de aproximativ:",
                "options": [
                    "0,1%, deoarece RV este exactă",
                    "141%, ca pentru randamentul zilnic la pătrat",
                    "16%, deoarece este apropiată de rădăcina pătrată din 2/M",
                    "50%, oricare ar fi M"
                ],
                "correctExplanation": "se(RV)/RV este aproximativ rădăcina pătrată din 2/M = 2/78, circa 0,16.",
                "incorrectExplanation": "RV este o măsurare cu eroare; cu M randamente eroarea ei relativă este aproximativ rădăcina pătrată din 2/M, adică 16% pentru M = 78."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Roughness: how to read the estimate",
                "text": "The scaling estimator applied to daily realised volatility gives Ĥ = 0.11 for SPY. Which statement is most defensible?",
                "options": [
                    "H = 0.11 is proved for SPY volatility",
                    "Measurement noise in RV biases Ĥ upwards, so volatility is even rougher than 0.11",
                    "The Hurst exponent is irrelevant for volatility forecasting",
                    "Measurement error in RV pushes Ĥ down and the estimator is inconsistent on noisy proxies, so 0.11 may overstate the roughness"
                ],
                "correctExplanation": "Noise adds a constant to the increment moments and flattens the scaling slope; Fukasawa, Takabatake and Westphal show that consistency requires high-frequency asymptotics.",
                "incorrectExplanation": "An estimate from a noisy proxy is not a proof, the bias from measurement error goes towards smaller H, and H drives both option skews and forecast weights."
            },
            "ro": {
                "title": "Asprimea: interpretarea estimării",
                "text": "Estimatorul de scalare aplicat volatilității realizate zilnice dă Ĥ = 0,11 pentru SPY. Ce afirmație este cea mai ușor de susținut?",
                "options": [
                    "H = 0,11 este demonstrat pentru volatilitatea SPY",
                    "Zgomotul de măsurare din RV deplasează Ĥ în sus, deci volatilitatea este și mai aspră decît 0,11",
                    "Exponentul Hurst este irelevant pentru prognoza volatilității",
                    "Eroarea de măsurare din RV coboară Ĥ, iar estimatorul este inconsistent pe indicatori zgomotoși, deci 0,11 poate exagera asprimea"
                ],
                "correctExplanation": "Zgomotul adaugă o constantă la momentele incrementelor și aplatizează panta de scalare; Fukasawa, Takabatake și Westphal arată că pentru consistență este necesară asimptotica de înaltă frecvență.",
                "incorrectExplanation": "O estimare dintr-un indicator zgomotos nu este o demonstrație, deplasarea din eroarea de măsurare merge spre un H mai mic, iar H influențează atît panta zîmbetului, cît și ponderile prognozei."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Rates of convergence under noise",
                "text": "With i.i.d. microstructure noise and n observations per day, which estimator attains the optimal rate n^(-1/4)?",
                "options": [
                    "Pre-averaging (as do multi-scale RV and flat-top realised kernels)",
                    "Two-scale RV",
                    "RV computed from all ticks",
                    "RV on a fixed 5-minute grid"
                ],
                "correctExplanation": "Jacod et al. (2009): pre-averaging over windows of order sqrt(n) returns converges at n^(-1/4), the optimal rate with noise.",
                "incorrectExplanation": "Two-scale RV converges only at n^(-1/6), all-tick RV is inconsistent because its bias 2nω² grows, and a fixed 5-minute grid does not use the extra observations at all."
            },
            "ro": {
                "title": "Rate de convergență în prezența zgomotului",
                "text": "Cu zgomot de microstructură i.i.d. și n observații pe zi, ce estimator atinge rata optimă n^(-1/4)?",
                "options": [
                    "Pre-medierea (la fel RV pe mai multe scări și nucleele realizate flat-top)",
                    "RV pe două scări",
                    "RV calculată din toate tranzacțiile",
                    "RV pe o grilă fixă de 5 minute"
                ],
                "correctExplanation": "Jacod et al. (2009): pre-medierea pe ferestre de ordinul sqrt(n) randamente converge cu rata n^(-1/4), optimă în prezența zgomotului.",
                "incorrectExplanation": "RV pe două scări converge doar cu rata n^(-1/6), RV din toate tranzacțiile este inconsistentă deoarece deplasarea 2nω² crește, iar o grilă fixă de 5 minute nu folosește deloc observațiile suplimentare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Noise bias",
                "text": "With i.i.d. microstructure noise of variance omega^2 and n returns per day, the expected RV is:",
                "options": [
                    "IV - 2 n omega^2",
                    "IV + 2 n omega^2",
                    "IV / n",
                    "IV, the noise cancels out"
                ],
                "correctExplanation": "Each observed return contains two noise terms, so noise adds 2 omega^2 per return, 2 n omega^2 in total.",
                "incorrectExplanation": "The noise bias grows with the number of returns: E[RV] = IV + 2 n omega^2, which is why sampling every tick overstates volatility."
            },
            "ro": {
                "title": "Deplasarea din zgomot",
                "text": "Cu zgomot de microstructură i.i.d. de varianță omega^2 și n randamente pe zi, valoarea așteptată a RV este:",
                "options": [
                    "IV - 2 n omega^2",
                    "IV + 2 n omega^2",
                    "IV / n",
                    "IV, zgomotul se anulează"
                ],
                "correctExplanation": "Fiecare randament observat conține doi termeni de zgomot, deci zgomotul adaugă 2 omega^2 pe randament, 2 n omega^2 în total.",
                "incorrectExplanation": "Deplasarea din zgomot crește cu numărul de randamente: E[RV] = IV + 2 n omega^2, de aceea eșantionarea fiecărei tranzacții supraestimează volatilitatea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Signature plot",
                "text": "What does a volatility signature plot show?",
                "options": [
                    "RV as a function of the time of day",
                    "The autocorrelation of RV by lag",
                    "Mean RV as a function of the sampling interval; a rise at high frequency signals noise",
                    "Implied volatility as a function of the strike price"
                ],
                "correctExplanation": "Without noise RV does not depend on the sampling interval; an increase at short intervals is the fingerprint of noise.",
                "incorrectExplanation": "The signature plot puts the sampling interval on the horizontal axis and mean RV on the vertical axis."
            },
            "ro": {
                "title": "Signature plot-ul",
                "text": "Ce arată signature plot-ul volatilității?",
                "options": [
                    "RV în funcție de ora din zi",
                    "Autocorelația RV pe întîrzieri",
                    "RV medie în funcție de intervalul de eșantionare; o creștere la frecvențe mari semnalează zgomot",
                    "Volatilitatea implicită în funcție de prețul de exercitare"
                ],
                "correctExplanation": "Fără zgomot RV nu depinde de intervalul de eșantionare; o creștere la intervale scurte este amprenta zgomotului.",
                "incorrectExplanation": "Signature plot-ul are intervalul de eșantionare pe axa orizontală și RV medie pe axa verticală."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "SPY at 5 minutes",
                "text": "What did the signature plot and the autocorrelation of 5-minute SPY returns show?",
                "options": [
                    "RV at 5 minutes is twice the RV at 30 minutes",
                    "Returns have autocorrelation -0.5, so noise dominates",
                    "RV falls sharply from 5 to 130 minutes",
                    "The plot is flat and the first-order autocorrelation is about -0.01: noise is negligible at 5 minutes"
                ],
                "correctExplanation": "Annualised volatility from mean RV stays between 12.6% and 13.1% from 5 to 130 minutes; noise corrections change little at this frequency.",
                "incorrectExplanation": "For a liquid ETF at 5 minutes the noise is invisible: the signature plot is flat and the autocorrelation of returns is almost zero."
            },
            "ro": {
                "title": "SPY la 5 minute",
                "text": "Ce au arătat signature plot-ul și autocorelația randamentelor SPY de 5 minute?",
                "options": [
                    "RV la 5 minute este dublul RV la 30 de minute",
                    "Randamentele au autocorelație -0,5, deci zgomotul domină",
                    "RV scade puternic de la 5 la 130 de minute",
                    "Graficul este plat, iar autocorelația de ordinul 1 este aproximativ -0,01: zgomotul este neglijabil la 5 minute"
                ],
                "correctExplanation": "Volatilitatea anualizată din RV medie rămîne între 12,6% și 13,1% de la 5 la 130 de minute; corecțiile de zgomot schimbă puțin la această frecvență.",
                "incorrectExplanation": "Pentru un ETF lichid la 5 minute zgomotul nu este detectabil: signature plot-ul este plat, iar autocorelația randamentelor este aproape zero."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Two-scale RV",
                "text": "How does two-scale realised variance correct for noise?",
                "options": [
                    "It averages RV over shifted sparse grids and subtracts a multiple of the all-data RV, which estimates the noise",
                    "It uses only the first and last price of the day",
                    "It multiplies RV by 2",
                    "It drops the largest returns of the day"
                ],
                "correctExplanation": "TSRV = RV_avg - (n_bar/n) RV_all: the all-data RV is dominated by noise and removes the bias of the average.",
                "incorrectExplanation": "Zhang, Mykland and Ait-Sahalia combine a slow scale (average over sparse grids) with a fast scale (all data) to cancel the noise bias."
            },
            "ro": {
                "title": "RV pe două scări",
                "text": "Cum corectează varianța realizată pe două scări zgomotul?",
                "options": [
                    "Face media RV pe grile rare decalate și scade un multiplu al RV din toate datele, care estimează zgomotul",
                    "Folosește doar primul și ultimul preț al zilei",
                    "Înmulțește RV cu 2",
                    "Elimină cele mai mari randamente ale zilei"
                ],
                "correctExplanation": "TSRV = RV_avg - (n_bar/n) RV_all: RV din toate datele este dominată de zgomot și elimină deplasarea mediei.",
                "incorrectExplanation": "Zhang, Mykland și Ait-Sahalia combină o scară lentă (media pe grile rare) cu una rapidă (toate datele) pentru a anula deplasarea din zgomot."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Bipower variation",
                "text": "Why is bipower variation robust to jumps?",
                "options": [
                    "It discards all returns larger than 1%",
                    "A jump enters one return and is multiplied by a small neighbouring return, so its effect vanishes as M grows",
                    "It uses squared returns only",
                    "It is computed from daily returns"
                ],
                "correctExplanation": "BV sums products |r_i||r_{i-1}|; a single large return is multiplied by an ordinary neighbour.",
                "incorrectExplanation": "Products of adjacent absolute returns keep the diffusive variance but not the squared jumps: BV converges to integrated variance."
            },
            "ro": {
                "title": "Variația bipower",
                "text": "De ce este variația bipower robustă la salturi?",
                "options": [
                    "Elimină toate randamentele mai mari de 1%",
                    "Un salt intră într-un singur randament și este înmulțit cu un randament vecin mic, deci efectul lui dispare cînd M crește",
                    "Folosește doar randamentele la pătrat",
                    "Se calculează din randamente zilnice"
                ],
                "correctExplanation": "BV adună produse |r_i||r_{i-1}|; un singur randament mare este înmulțit cu un vecin obișnuit.",
                "incorrectExplanation": "Produsele randamentelor absolute alăturate păstrează varianța difuzivă, dar nu și salturile la pătrat: BV converge la varianța integrată."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "False discovery rate for jump days",
                "text": "The daily jump test on 1,489 SPY days at 5% gives 235 rejections. Which procedure sorts the N daily p-values and rejects the k smallest, with k the largest index such that p_(k) ≤ k × 0.05/N, so that the expected share of false jump days among the rejected days stays at most 5%?",
                "options": [
                    "Bonferroni at 5%",
                    "Raising the number of intraday returns M",
                    "Benjamini–Hochberg at a 5% false discovery rate",
                    "Replacing RV by BV in the numerator of the statistic"
                ],
                "correctExplanation": "Benjamini–Hochberg controls the FDR, the expected proportion of false rejections; in the chapter it leaves 42 SPY jump days (17 after the periodicity correction).",
                "incorrectExplanation": "Bonferroni compares every p-value with the single threshold 0.05/N: it controls the probability of any false rejection (FWER), hence also the FDR, but rejects far fewer days; a larger M changes power but not multiplicity, and the numerator must contrast RV with BV."
            },
            "ro": {
                "title": "Rata descoperirilor false pentru zilele cu salt",
                "text": "Testul zilnic de salturi pe 1.489 de zile SPY la 5% dă 235 de respingeri. Ce procedură ordonează cele N p-value-uri zilnice și respinge cele mai mici k, cu k cel mai mare indice pentru care p_(k) ≤ k × 0,05/N, astfel încît ponderea așteptată a zilelor cu salt false printre zilele respinse să rămînă cel mult 5%?",
                "options": [
                    "Bonferroni la 5%",
                    "Creșterea numărului de randamente intraday M",
                    "Benjamini–Hochberg la o rată a descoperirilor false de 5%",
                    "Înlocuirea lui RV cu BV la numărătorul statisticii"
                ],
                "correctExplanation": "Benjamini–Hochberg controlează FDR, proporția așteptată a respingerilor false; în capitol lasă 42 de zile SPY cu salt (17 după corecția de periodicitate).",
                "incorrectExplanation": "Bonferroni compară fiecare p-value cu pragul unic 0,05/N: controlează probabilitatea oricărei respingeri false (FWER), deci și FDR, dar respinge mult mai puține zile; un M mai mare schimbă puterea, dar nu multiplicitatea, iar numărătorul trebuie să compare RV cu BV."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Multiple testing",
                "text": "The jump test is applied to 1,489 days at the 5% level and rejects on 235 days. What is the main caution?",
                "options": [
                    "235 rejections prove that every such day had a jump",
                    "The test is invalid for daily data",
                    "The 5% level makes false alarms impossible",
                    "About 74 rejections are expected even without any jump, so not every rejection is a news jump"
                ],
                "correctExplanation": "With one test per day, alpha times the number of days are false alarms; a stricter level such as 0.1% keeps them few.",
                "incorrectExplanation": "Testing many days produces false alarms; at 5% about 74 of 1,489 days would reject without jumps."
            },
            "ro": {
                "title": "Testarea multiplă",
                "text": "Testul de salturi se aplică la 1.489 de zile la nivelul de 5% și respinge în 235 de zile. Care este principala precauție?",
                "options": [
                    "235 de respingeri dovedesc că fiecare astfel de zi a avut un salt",
                    "Testul nu este valid pentru date zilnice",
                    "Nivelul de 5% face imposibile alarmele false",
                    "Aproximativ 74 de respingeri sînt așteptate chiar fără salturi, deci nu orice respingere este un salt produs de știri"
                ],
                "correctExplanation": "Cu un test pe zi, alfa înmulțit cu numărul de zile reprezintă alarme false; un nivel mai strict, ca 0,1%, le menține puține.",
                "incorrectExplanation": "Testarea multor zile produce alarme false; la 5% aproximativ 74 din 1.489 de zile ar respinge fără salturi."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "HAR as a restricted AR(22)",
                "text": "Viewed as an AR(22) for log RV, how many linear restrictions does the HAR model impose on the lag coefficients?",
                "options": [
                    "19: equal coefficients on lags 2–5 (3 restrictions) and on lags 6–22 (16 restrictions)",
                    "3, one for each component",
                    "21, all lags beyond the first",
                    "None: HAR is an unrestricted AR(22)"
                ],
                "correctExplanation": "The staircase fixes φ2 = … = φ5 and φ6 = … = φ22; for SPY the Wald test of the 19 restrictions gives p = 0.51.",
                "incorrectExplanation": "HAR has 3 free slopes out of 22 lag coefficients, so 22 − 3 = 19 restrictions: equalities inside the weekly and monthly blocks, not zero lags."
            },
            "ro": {
                "title": "HAR ca AR(22) restricționat",
                "text": "Privit ca un AR(22) pentru log RV, cîte restricții liniare impune modelul HAR asupra coeficienților întîrzierilor?",
                "options": [
                    "19: coeficienți egali pe întîrzierile 2–5 (3 restricții) și pe întîrzierile 6–22 (16 restricții)",
                    "3, cîte una pentru fiecare componentă",
                    "21, toate întîrzierile după prima",
                    "Niciuna: HAR este un AR(22) nerestricționat"
                ],
                "correctExplanation": "Structura în trepte impune φ2 = … = φ5 și φ6 = … = φ22; pentru SPY testul Wald al celor 19 restricții dă p = 0,51.",
                "incorrectExplanation": "HAR are 3 pante libere din 22 de coeficienți ai întîrzierilor, deci 22 − 3 = 19 restricții: egalități în blocurile săptămînal și lunar, nu întîrzieri nule."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Estimating the noise variance",
                "text": "Under i.i.d. microstructure noise, observed returns at the highest frequency have first-order autocovariance −0.0004 (%²). What is the implied noise variance ω²?",
                "options": [
                    "0.0002",
                    "0.0004",
                    "0.0008",
                    "It cannot be identified from returns"
                ],
                "correctExplanation": "r_i = r*_i + ε_i − ε_{i−1}, so cov(r_i, r_{i−1}) = −Var(ε) = −ω²: ω² = 0.0004.",
                "incorrectExplanation": "Only ε_{i−1} is shared by adjacent returns, so the autocovariance equals −ω² exactly; 2ω² is the bias added per return to RV, not the autocovariance."
            },
            "ro": {
                "title": "Estimarea varianței zgomotului",
                "text": "Cu zgomot de microstructură i.i.d., randamentele observate la frecvența cea mai mare au autocovarianța de ordinul 1 egală cu −0,0004 (%²). Care este varianța zgomotului ω² implicată?",
                "options": [
                    "0,0002",
                    "0,0004",
                    "0,0008",
                    "Nu poate fi identificată din randamente"
                ],
                "correctExplanation": "r_i = r*_i + ε_i − ε_{i−1}, deci cov(r_i, r_{i−1}) = −Var(ε) = −ω²: ω² = 0,0004.",
                "incorrectExplanation": "Doar ε_{i−1} este comun randamentelor alăturate, deci autocovarianța este exact −ω²; 2ω² este deplasarea adăugată la RV de fiecare randament, nu autocovarianța."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Long memory",
                "text": "The autocorrelation of SPY log RV is 0.64 at lag 1 and 0.24 at 22 days. What does this indicate?",
                "options": [
                    "No memory: RV is i.i.d.",
                    "Short memory: an AR(1) fits perfectly",
                    "Long memory: autocorrelations decay much more slowly than in an AR(1)",
                    "A negative trend in volatility"
                ],
                "correctExplanation": "An AR(1) with 0.64 would give about 0.00005 at lag 22; the observed 0.24 shows slow, hyperbolic-like decay.",
                "incorrectExplanation": "Volatility shocks persist for months; the autocorrelation at one month is still far from zero."
            },
            "ro": {
                "title": "Memoria lungă",
                "text": "Autocorelația log RV pentru SPY este 0,64 la întîrzierea 1 și 0,24 la 22 de zile. Ce indică acest lucru?",
                "options": [
                    "Lipsa memoriei: RV este i.i.d.",
                    "Memorie scurtă: un AR(1) descrie perfect datele",
                    "Memorie lungă: autocorelațiile scad mult mai lent decît la un AR(1)",
                    "O tendință negativă a volatilității"
                ],
                "correctExplanation": "Un AR(1) cu 0,64 ar da aproximativ 0,00005 la întîrzierea 22; valoarea observată 0,24 arată o scădere lentă.",
                "incorrectExplanation": "Șocurile de volatilitate persistă luni de zile; autocorelația la o lună este încă departe de zero."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Truncated realised variance",
                "text": "Why is truncated RV, the sum of r² over returns with |r| ≤ c·Δ^ϖ and 0 < ϖ < 1/2, robust to jumps?",
                "options": [
                    "Because an exponent ϖ above 1/2 keeps all diffusive returns",
                    "Because the threshold stays fixed as Δ shrinks",
                    "Because it multiplies adjacent absolute returns",
                    "Because diffusive increments are of order Δ^(1/2) and end up below the threshold, while jumps are of order 1 and are cut off"
                ],
                "correctExplanation": "Mancini (2009): with ϖ < 1/2 the threshold shrinks more slowly than the diffusive increments but still goes to zero, so jumps are removed asymptotically.",
                "incorrectExplanation": "The threshold must shrink with Δ, but more slowly than Δ^(1/2); multiplying adjacent returns is bipower variation, a different estimator."
            },
            "ro": {
                "title": "Varianța realizată trunchiată",
                "text": "De ce este RV trunchiată, suma lui r² pe randamentele cu |r| ≤ c·Δ^ϖ și 0 < ϖ < 1/2, robustă la salturi?",
                "options": [
                    "Deoarece un exponent ϖ peste 1/2 păstrează toate randamentele difuzive",
                    "Deoarece pragul rămîne fix cînd Δ scade",
                    "Deoarece înmulțește randamentele absolute alăturate",
                    "Deoarece incrementele difuzive sînt de ordinul Δ^(1/2) și ajung sub prag, în timp ce salturile sînt de ordinul 1 și sînt eliminate"
                ],
                "correctExplanation": "Mancini (2009): cu ϖ < 1/2 pragul scade mai lent decît incrementele difuzive, dar tot tinde la zero, deci salturile sînt eliminate asimptotic.",
                "incorrectExplanation": "Pragul trebuie să scadă odată cu Δ, dar mai lent decît Δ^(1/2); înmulțirea randamentelor alăturate este variația bipower, un alt estimator."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Variance risk premium",
                "text": "On average, how does VIX compare with the SPY volatility realised over the following month?",
                "options": [
                    "VIX is higher: investors pay a premium to insure against volatility",
                    "VIX is lower, by about 4 points",
                    "They are exactly equal on average",
                    "VIX is unrelated to future volatility"
                ],
                "correctExplanation": "Mean VIX 19.5 vs 15.2 realised; VIX was above realised volatility on about 88% of days.",
                "incorrectExplanation": "Implied volatility contains the variance risk premium, so it is an upward-biased forecast of realised volatility."
            },
            "ro": {
                "title": "Prima de risc a varianței",
                "text": "În medie, cum se compară VIX cu volatilitatea SPY realizată în luna următoare?",
                "options": [
                    "VIX este mai mare: investitorii plătesc o primă pentru a se asigura împotriva volatilității",
                    "VIX este mai mic, cu aproximativ 4 puncte",
                    "Sînt exact egale în medie",
                    "VIX nu are legătură cu volatilitatea viitoare"
                ],
                "correctExplanation": "VIX mediu 19,5 față de 15,2 realizată; VIX a depășit volatilitatea realizată în aproximativ 88% din zile.",
                "incorrectExplanation": "Volatilitatea implicită conține prima de risc a varianței, deci este o prognoză deplasată în sus a volatilității realizate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Attenuation in HAR and HARQ",
                "text": "Why should the weight on yesterday's RV in a HAR forecast be smaller on days with high realised quarticity?",
                "options": [
                    "Leverage: negative returns raise future RV",
                    "RV_t measures IV_t with an error whose variance is proportional to IQ_t, and error in a regressor attenuates its slope",
                    "Jumps are more frequent on those days",
                    "The weekly component absorbs the daily effect"
                ],
                "correctExplanation": "Bollerslev, Patton and Quaedvlieg (2016): the signal-to-noise ratio of RV_t falls when IQ_t is high, so HARQ uses β_d + β_Q sqrt(RQ_t) with β_Q < 0.",
                "incorrectExplanation": "The mechanism is errors in variables: the CLT gives Var(RV − IV) = 2 IQ/M, so a noisier regressor deserves less weight; leverage and jumps are separate extensions."
            },
            "ro": {
                "title": "Atenuarea în HAR și HARQ",
                "text": "De ce ar trebui ca ponderea RV de ieri într-o prognoză HAR să fie mai mică în zilele cu cvarticitate realizată mare?",
                "options": [
                    "Efectul de pîrghie: randamentele negative cresc RV viitoare",
                    "RV_t măsoară IV_t cu o eroare a cărei varianță este proporțională cu IQ_t, iar eroarea dintr-un regresor îi atenuează panta",
                    "Salturile sînt mai frecvente în acele zile",
                    "Componenta săptămînală preia efectul zilnic"
                ],
                "correctExplanation": "Bollerslev, Patton și Quaedvlieg (2016): raportul semnal/zgomot al lui RV_t scade cînd IQ_t este mare, deci HARQ folosește β_d + β_Q sqrt(RQ_t) cu β_Q < 0.",
                "incorrectExplanation": "Mecanismul este cel al erorilor în variabile: CLT dă Var(RV − IV) = 2 IQ/M, deci un regresor mai zgomotos merită o pondere mai mică; efectul de pîrghie și salturile sînt extensii separate."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "HAR lag weights",
                "text": "In HAR with coefficients beta_d, beta_w, beta_m, what weight does lag 10 receive?",
                "options": [
                    "beta_d + beta_w/5 + beta_m/22",
                    "beta_w/5 + beta_m/22",
                    "beta_m / 22",
                    "Zero"
                ],
                "correctExplanation": "Lag 10 is outside the week but inside the month, so only the monthly average contributes: beta_m/22.",
                "incorrectExplanation": "Lag 1 gets all three terms, lags 2-5 get the weekly and monthly terms, lags 6-22 only the monthly term."
            },
            "ro": {
                "title": "Ponderile HAR pe întîrzieri",
                "text": "Într-un HAR cu coeficienții beta_d, beta_w, beta_m, ce pondere primește întîrzierea 10?",
                "options": [
                    "beta_d + beta_w/5 + beta_m/22",
                    "beta_w/5 + beta_m/22",
                    "beta_m / 22",
                    "Zero"
                ],
                "correctExplanation": "Întîrzierea 10 este în afara săptămînii, dar în interiorul lunii, deci contribuie doar media lunară: beta_m/22.",
                "incorrectExplanation": "Întîrzierea 1 primește toți cei trei termeni, întîrzierile 2-5 termenii săptămînal și lunar, întîrzierile 6-22 doar termenul lunar."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Which loss survives a noisy proxy",
                "text": "Forecasts are evaluated against RV, a noisy proxy of the true variance that is conditionally unbiased: E[RV_t | past] = E[IV_t | past]. Which loss ranks the forecasts as the true variance would?",
                "options": [
                    "MSE on volatility, (sqrt(RV) − sqrt(F))²",
                    "Mean absolute error on variance",
                    "Mean absolute percentage error",
                    "QLIKE on variance, RV/F − ln(RV/F) − 1"
                ],
                "correctExplanation": "Patton (2011): the QLIKE difference of two forecasts is linear in RV, so its conditional expectation depends on RV only through E[RV | past] = E[IV | past]; the expected ranking is the one under the true variance.",
                "incorrectExplanation": "Losses on volatility or absolute errors are minimised by a forecast other than the conditional variance (by Jensen, (E sqrt(RV))² is below E RV), so proxy noise distorts the ranking."
            },
            "ro": {
                "title": "Funcții de pierdere robuste la un proxy zgomotos",
                "text": "Prognozele sînt evaluate față de RV, un proxy zgomotos al varianței adevărate, nedeplasat condiționat: E[RV_t | trecut] = E[IV_t | trecut]. Ce funcție de pierdere ordonează prognozele la fel ca varianța adevărată?",
                "options": [
                    "MSE pe volatilitate, (sqrt(RV) − sqrt(F))²",
                    "Eroarea absolută medie pe varianță",
                    "Eroarea procentuală absolută medie",
                    "QLIKE pe varianță, RV/F − ln(RV/F) − 1"
                ],
                "correctExplanation": "Patton (2011): diferența QLIKE dintre două prognoze este liniară în RV, deci speranța ei condiționată depinde de RV doar prin E[RV | trecut] = E[IV | trecut]; ordonarea așteptată este cea dată de varianța adevărată.",
                "incorrectExplanation": "Funcțiile de pierdere pe volatilitate sau cu erori absolute sînt minimizate de altă prognoză decît varianța condiționată (din Jensen, (E sqrt(RV))² este sub E RV), deci zgomotul proxy-ului distorsionează ordonarea."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "QLIKE asymmetry",
                "text": "With true variance 1, which forecast has the larger QLIKE loss?",
                "options": [
                    "0.5, because QLIKE punishes under-prediction more",
                    "2.0, because QLIKE punishes over-prediction more",
                    "Both have the same loss",
                    "Neither, since QLIKE is zero for all forecasts"
                ],
                "correctExplanation": "QLIKE is 0.307 for 0.5 and 0.193 for 2.0: under-predicting risk costs more.",
                "incorrectExplanation": "QLIKE = RV/F - log(RV/F) - 1 grows quickly when F is too small; MSE would rank the two the other way."
            },
            "ro": {
                "title": "Asimetria QLIKE",
                "text": "Cu varianța adevărată 1, ce prognoză are pierderea QLIKE mai mare?",
                "options": [
                    "0,5, deoarece QLIKE penalizează mai mult subestimarea",
                    "2,0, deoarece QLIKE penalizează mai mult supraestimarea",
                    "Ambele au aceeași pierdere",
                    "Niciuna, deoarece QLIKE este zero pentru toate prognozele"
                ],
                "correctExplanation": "QLIKE este 0,307 pentru 0,5 și 0,193 pentru 2,0: subestimarea riscului costă mai mult.",
                "incorrectExplanation": "QLIKE = RV/F - log(RV/F) - 1 crește rapid cînd F este prea mic; MSE ar ordona cele două invers."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Model confidence set",
                "text": "For SPY one-day forecasts from 2022, the 90% model confidence set contains log-HAR and SHAR. What does this mean?",
                "options": [
                    "SHAR is significantly better than log-HAR",
                    "The data cannot separate the two, and the set contains the best model with probability at least 90%",
                    "Every other model has a QLIKE above 0.5",
                    "Each surviving model passed 21 separate Diebold–Mariano tests at 5%"
                ],
                "correctExplanation": "Hansen, Lunde and Nason (2011): models are eliminated sequentially until equal predictive ability is not rejected; the survivors form a confidence set for the best model.",
                "incorrectExplanation": "The MCS is a set-valued statement with multiplicity control, not a ranking between the survivors and not a sequence of unadjusted pairwise tests."
            },
            "ro": {
                "title": "Mulțimea de încredere a modelelor",
                "text": "Pentru prognozele SPY pe o zi din 2022, mulțimea de încredere a modelelor la 90% conține log-HAR și SHAR. Ce înseamnă aceasta?",
                "options": [
                    "SHAR este semnificativ mai bun decît log-HAR",
                    "Datele nu le pot separa, iar mulțimea conține cel mai bun model cu probabilitate de cel puțin 90%",
                    "Toate celelalte modele au QLIKE peste 0,5",
                    "Fiecare model rămas a trecut 21 de teste Diebold–Mariano separate la 5%"
                ],
                "correctExplanation": "Hansen, Lunde și Nason (2011): modelele sînt eliminate succesiv pînă cînd egalitatea capacității predictive nu mai este respinsă; cele rămase formează o mulțime de încredere pentru cel mai bun model.",
                "incorrectExplanation": "MCS este o afirmație despre o mulțime, cu corecție pentru testarea multiplă, nu un clasament între modelele rămase și nici un șir de teste pe perechi neajustate."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Joint test in Mincer–Zarnowitz",
                "text": "In the MZ regression for GARCH, î = 0.2418 (SE 0.2310), b̂ = 0.7046 (SE 0.2382) and corr(î, b̂) = −0.9750. How should unbiasedness, (a, b) = (0, 1), be tested?",
                "options": [
                    "Two separate t-tests, rejecting if either rejects",
                    "Test b = 1 only, because the intercept is irrelevant",
                    "A joint Wald test using the full HAC covariance matrix of (î, b̂)",
                    "Compare the R² of the regression with 1"
                ],
                "correctExplanation": "With strongly correlated estimates only the joint Wald statistic has the right size; here W = 2.07, p = 0.35.",
                "incorrectExplanation": "Separate t-tests ignore the correlation and have the wrong joint size, the intercept is part of the hypothesis, and R² is capped below 1 by the noise in RV."
            },
            "ro": {
                "title": "Testul comun în Mincer–Zarnowitz",
                "text": "În regresia MZ pentru GARCH, â = 0,2418 (SE 0,2310), b̂ = 0,7046 (SE 0,2382) și corr(â, b̂) = −0,9750. Cum trebuie testată nedeplasarea, (a, b) = (0, 1)?",
                "options": [
                    "Două teste t separate, respingînd dacă oricare respinge",
                    "Doar testul b = 1, deoarece termenul liber este irelevant",
                    "Un test Wald comun, cu matricea de covarianță HAC completă a lui (â, b̂)",
                    "Comparînd R² al regresiei cu 1"
                ],
                "correctExplanation": "Cu estimări puternic corelate doar statistica Wald comună are mărimea corectă; aici W = 2,07, p = 0,35.",
                "incorrectExplanation": "Testele t separate ignoră corelația și au mărimea comună greșită, termenul liber face parte din ipoteză, iar R² este limitat sub 1 de zgomotul din RV."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Rough volatility",
                "text": "The chapter estimates the Hurst exponent H of log volatility at about 0.1. What does H < 0.5 mean?",
                "options": [
                    "Volatility is smoother than a Brownian motion and trends",
                    "Volatility is constant",
                    "Volatility is a random walk with H exactly 0.5",
                    "Log volatility is rougher than a Brownian motion: its increments are negatively correlated"
                ],
                "correctExplanation": "H = 0.5 is Brownian motion; H about 0.1 means very rough paths (Gatheral, Jaisson and Rosenbaum); measurement error in RV can push H down.",
                "incorrectExplanation": "Roughness means H well below 0.5; the chapter finds 0.11 for SPY and 0.08 for Bitcoin, with a caution about measurement error."
            },
            "ro": {
                "title": "Rough volatility",
                "text": "Capitolul estimează exponentul Hurst H al log-volatilității la aproximativ 0,1. Ce înseamnă H < 0,5?",
                "options": [
                    "Volatilitatea este mai netedă decît o mișcare browniană și are tendință",
                    "Volatilitatea este constantă",
                    "Volatilitatea este un mers aleator cu H exact 0,5",
                    "Log-volatilitatea este mai aspră decît o mișcare browniană: incrementele ei sînt corelate negativ"
                ],
                "correctExplanation": "H = 0,5 este mișcarea browniană; H aproximativ 0,1 înseamnă traiectorii foarte aspre (Gatheral, Jaisson și Rosenbaum); eroarea de măsurare din RV poate coborî H.",
                "incorrectExplanation": "Asprimea înseamnă H mult sub 0,5; capitolul găsește 0,11 pentru SPY și 0,08 pentru Bitcoin, cu precauția privind eroarea de măsurare."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the AI error: annualising RV",
                "text": "An AI assistant writes: \"A daily realised variance of 1.0e-4 corresponds to an annualised volatility of sqrt(1.0e-4) x 252 = 2.52, i.e. 252%.\" What is wrong?",
                "options": [
                    "SPY must be annualised with 365 days, not 252",
                    "Realised variance cannot be annualised at all",
                    "The daily RV must first be divided by 252",
                    "Volatility scales with the square root of time: sqrt(252 x 1.0e-4) = 15.9%"
                ],
                "correctExplanation": "Variance grows in proportion to time and volatility with its square root, so the annual volatility is sqrt(252 x RV) = 15.9%. The 252% figure should also fail a plausibility check: the VIX is usually between 12 and 30.",
                "incorrectExplanation": "Multiplying a daily volatility by 252 treats volatility as if it grew linearly with time; only the variance does."
            },
            "ro": {
                "title": "Găsiți eroarea AI: anualizarea RV",
                "text": "Un asistent AI scrie: „O varianță realizată zilnică de 1,0e-4 corespunde unei volatilități anualizate de sqrt(1,0e-4) x 252 = 2,52, adică 252%.” Ce este greșit?",
                "options": [
                    "SPY trebuie anualizat cu 365 de zile, nu cu 252",
                    "Varianța realizată nu poate fi anualizată deloc",
                    "RV zilnică trebuie mai întîi împărțită la 252",
                    "Volatilitatea crește cu rădăcina pătrată a timpului: sqrt(252 x 1,0e-4) = 15,9%"
                ],
                "correctExplanation": "Varianța crește proporțional cu timpul, iar volatilitatea cu rădăcina lui pătrată, deci volatilitatea anuală este sqrt(252 x RV) = 15,9%. Cifra de 252% nu trece nici testul de plauzibilitate: VIX este de obicei între 12 și 30.",
                "incorrectExplanation": "Înmulțirea unei volatilități zilnice cu 252 tratează volatilitatea ca și cum ar crește liniar cu timpul; doar varianța crește astfel."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: sampling every tick",
                "text": "An AI assistant writes: \"For SPY, sum the squared returns at every tick: the more intraday returns, the smaller the error of the realised variance, so tick-by-tick sampling is always best.\" What is wrong?",
                "options": [
                    "Microstructure noise: with noise variance omega^2, E[RV] = IV + 2n omega^2, so the bias grows with the number of returns n; sample every 1-5 minutes or use a noise-robust estimator",
                    "Realised variance should use absolute returns, not squared returns",
                    "Tick data are too few to estimate a daily variance",
                    "Squared returns must be computed from simple returns, never from log returns"
                ],
                "correctExplanation": "Bid-ask bounce and price discreteness add noise to every observed price. Its contribution 2n omega^2 grows with the sampling frequency, which is why the signature plot rises at short intervals (Bandi and Russell, 2008; Zhang, Mykland and Ait-Sahalia, 2005).",
                "incorrectExplanation": "More returns reduce the error only for a noise-free price; with microstructure noise the bias of RV grows with the number of returns."
            },
            "ro": {
                "title": "Găsiți eroarea AI: eșantionarea fiecărei tranzacții",
                "text": "Un asistent AI scrie: „Pentru SPY, adunați pătratele randamentelor la fiecare tranzacție: cu cît sînt mai multe randamente intraday, cu atît eroarea varianței realizate este mai mică, deci eșantionarea tranzacție cu tranzacție este întotdeauna cea mai bună.” Ce este greșit?",
                "options": [
                    "Zgomotul de microstructură: cu un zgomot de varianță omega^2, E[RV] = IV + 2n omega^2, deci deplasarea crește cu numărul de randamente n; eșantionați la 1-5 minute sau folosiți un estimator robust la zgomot",
                    "Varianța realizată ar trebui să folosească randamente absolute, nu pătratele lor",
                    "Datele pe tranzacții sînt prea puține pentru a estima o varianță zilnică",
                    "Pătratele randamentelor trebuie calculate din randamente simple, niciodată din randamente log"
                ],
                "correctExplanation": "Oscilația bid-ask și discretizarea prețului adaugă zgomot fiecărui preț observat. Contribuția lui, 2n omega^2, crește cu frecvența de eșantionare, de aceea signature plot-ul urcă la intervale scurte (Bandi și Russell, 2008; Zhang, Mykland și Ait-Sahalia, 2005).",
                "incorrectExplanation": "Mai multe randamente reduc eroarea doar pentru un preț fără zgomot; cu zgomot de microstructură, deplasarea RV crește cu numărul de randamente."
            }
        }
    ]
};

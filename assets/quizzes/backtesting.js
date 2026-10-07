// ============================================================
// Quiz bank for chapter id 'backtesting': Backtesting and Evaluating Risk Forecasts (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['backtesting'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "Local power of the POF test",
                "text": "At T = 250 and alpha = 1%, roughly which true breach probability gives the Kupiec test (5% level) about 50% power?",
                "options": [
                    "About 1.1%: any excess over 1% is detected quickly",
                    "About 1.5%",
                    "About 2.5-3%",
                    "Any rate above 1%, because the LR test is consistent"
                ],
                "correctExplanation": "The exact Binomial power first reaches 50% near a true rate of 2.7%; the local approximation uses lambda = T(pi - alpha)^2/(alpha(1 - alpha)), and with alpha T = 2.5 the discreteness of x keeps power low.",
                "incorrectExplanation": "Consistency is an asymptotic property; with only 2.5 expected breaches in a year, the true rate must be close to three times the target before the test rejects half of the time."
            },
            "ro": {
                "title": "Puterea locală a testului POF",
                "text": "La T = 250 și alpha = 1%, aproximativ ce probabilitate reală de depășire dă testului Kupiec (nivel 5%) o putere de circa 50%?",
                "options": [
                    "Circa 1,1%: orice exces peste 1% este detectat repede",
                    "Circa 1,5%",
                    "Circa 2,5-3%",
                    "Orice rată peste 1%, pentru că testul LR este consistent"
                ],
                "correctExplanation": "Puterea Binomială exactă atinge prima dată 50% în jurul unei rate reale de 2,7%; aproximarea locală folosește lambda = T(pi - alpha)^2/(alpha(1 - alpha)), iar cu alpha T = 2,5 caracterul discret al lui x menține puterea scăzută.",
                "incorrectExplanation": "Consistența este o proprietate asimptotică; cu doar 2,5 depășiri așteptate într-un an, rata reală trebuie să fie aproape de trei ori ținta pentru ca testul să respingă în jumătate din cazuri."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Kupiec test",
                "text": "The Kupiec POF test compares",
                "options": [
                    "the observed breach rate x/T with the nominal probability alpha, via a likelihood ratio",
                    "the average loss on breach days with the ES forecast",
                    "the durations between breaches with a Weibull distribution",
                    "the FZ0 losses of two competing models"
                ],
                "correctExplanation": "LR_uc compares the Bernoulli likelihood at alpha with that at the estimated rate x/T; it is asymptotically chi-square with one degree of freedom.",
                "incorrectExplanation": "Kupiec tests only the number of breaches: the observed rate x/T against alpha."
            },
            "ro": {
                "title": "Testul Kupiec",
                "text": "Testul POF al lui Kupiec compară",
                "options": [
                    "rata observată de depășire x/T cu probabilitatea nominală alpha, printr-un raport de verosimilitate",
                    "pierderea medie din zilele cu depășire cu prognoza ES",
                    "duratele dintre depășiri cu o distribuție Weibull",
                    "pierderile FZ0 a două modele concurente"
                ],
                "correctExplanation": "LR_uc compară verosimilitatea Bernoulli la alpha cu cea la rata estimată x/T; asimptotic urmează o distribuție hi-pătrat cu un grad de libertate.",
                "incorrectExplanation": "Kupiec testează doar numărul depășirilor: rata observată x/T față de alpha."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Zero breaches",
                "text": "A VaR 1% was never breached in 250 days. What does the Kupiec test conclude at 5%?",
                "options": [
                    "The model is perfect",
                    "The test cannot be computed with zero breaches",
                    "Nothing: the test is one-sided",
                    "Coverage is rejected, because LR_uc = -500 ln(0.99), about 5.03, exceeds 3.84"
                ],
                "correctExplanation": "With x = 0 the statistic is -2 x 250 ln(0.99), about 5.03 > 3.84: a VaR that is never breached is too conservative and wastes capital.",
                "incorrectExplanation": "The test is two-sided: too few breaches also reject; here LR_uc is about 5.03."
            },
            "ro": {
                "title": "Nicio depășire",
                "text": "Un VaR 1% nu a fost depășit niciodată în 250 de zile. Ce concluzionează testul Kupiec la 5%?",
                "options": [
                    "Modelul este perfect",
                    "Testul nu poate fi calculat fără depășiri",
                    "Nimic: testul este unilateral",
                    "Acoperirea este respinsă, pentru că LR_uc = -500 ln(0,99), aproximativ 5,03, depășește 3,84"
                ],
                "correctExplanation": "Cu x = 0 statistica este -2 x 250 ln(0,99), aproximativ 5,03 > 3,84: un VaR niciodată depășit este prea conservator și irosește capital.",
                "incorrectExplanation": "Testul este bilateral: și prea puține depășiri duc la respingere; aici LR_uc este aproximativ 5,03."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Power of coverage tests",
                "text": "Why do coverage tests have low power over one year of VaR 1%?",
                "options": [
                    "Because daily returns are Normal",
                    "Because only about 2.5 breaches are expected, so wrong models often produce acceptable counts",
                    "Because the chi-square approximation is exact",
                    "Because breaches are always independent"
                ],
                "correctExplanation": "With T = 250 and alpha = 1%, the expected count is 2.5; a model with a true 2% rate still falls in the acceptance region (1 to 6 breaches) about three times out of four.",
                "incorrectExplanation": "Tail events are rare: one year contains too few breaches to separate good from mediocre models."
            },
            "ro": {
                "title": "Puterea testelor de acoperire",
                "text": "De ce testele de acoperire au putere redusă pe un an de VaR 1%?",
                "options": [
                    "Pentru că randamentele zilnice sînt Normale",
                    "Pentru că se așteaptă doar circa 2,5 depășiri, deci modelele greșite produc des un număr acceptabil de depășiri",
                    "Pentru că aproximarea hi-pătrat este exactă",
                    "Pentru că depășirile sînt mereu independente"
                ],
                "correctExplanation": "Cu T = 250 și alpha = 1%, numărul așteptat este 2,5; un model cu rata reală de 2% cade totuși în regiunea de acceptare (1--6 depășiri) aproximativ de trei ori din patru.",
                "incorrectExplanation": "Evenimentele din coadă sînt rare: un an conține prea puține depășiri pentru a separa modelele bune de cele mediocre."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Estimation risk in backtests",
                "text": "The lecture's Kupiec p-values use chi-square(1) limits with an estimation window R = 1000 and P of about 5000 out-of-sample days. Which statement is correct?",
                "options": [
                    "The chi-square limit ignores parameter uncertainty, which does not vanish because P/R does not go to 0; the size can be badly distorted",
                    "The chi-square limit is exact for Bernoulli data, so estimation plays no role",
                    "Estimation risk matters only for ES backtests, not for VaR",
                    "A larger P always removes estimation risk"
                ],
                "correctExplanation": "Out-of-sample hits depend on the estimated parameters; the extra term is of order sqrt(P/R). In the lecture's fixed-scheme Monte Carlo a correct GARCH-t is rejected in about 27% of samples at P = 5000 with estimated parameters; the rolling scheme has a different correction term of the same order.",
                "incorrectExplanation": "Estimation error enters the hits through VaR_t(theta-hat); its effect grows with P/R, so a larger evaluation sample makes it worse, not better."
            },
            "ro": {
                "title": "Riscul de estimare în backtesting",
                "text": "p-value-urile Kupiec din curs folosesc limite hi-pătrat(1), cu fereastra de estimare R = 1000 și aproximativ P = 5000 de zile în afara eșantionului. Care afirmație este corectă?",
                "options": [
                    "Limita hi-pătrat ignoră incertitudinea parametrilor, care nu dispare pentru că P/R nu tinde la 0; mărimea poate fi puternic distorsionată",
                    "Limita hi-pătrat este exactă pentru date Bernoulli, deci estimarea nu contează",
                    "Riscul de estimare contează doar pentru testele ES, nu pentru VaR",
                    "Un P mai mare elimină întotdeauna riscul de estimare"
                ],
                "correctExplanation": "Depășirile din afara eșantionului depind de parametrii estimați; termenul suplimentar este de ordinul sqrt(P/R). În simularea Monte Carlo din curs, cu schemă fixă, un GARCH-t corect este respins în circa 27% din eșantioane la P = 5000 cu parametri estimați; schema mobilă are un alt termen de corecție, de același ordin.",
                "incorrectExplanation": "Eroarea de estimare intră în depășiri prin VaR_t(theta estimat); efectul ei crește cu P/R, deci un eșantion de evaluare mai mare o agravează, nu o elimină."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Conditional coverage",
                "text": "How is the conditional coverage statistic LR_cc formed, and what is its null distribution?",
                "options": [
                    "LR_cc = LR_uc + LR_ind, chi-square with 2 degrees of freedom",
                    "LR_cc = LR_uc x LR_ind, Normal",
                    "LR_cc = LR_uc - LR_ind, chi-square with 1 degree of freedom",
                    "LR_cc = max(LR_uc, LR_ind), Student-t"
                ],
                "correctExplanation": "Conditional coverage tests both properties at once: the sum of the two likelihood ratios is asymptotically chi-square(2).",
                "incorrectExplanation": "The two statistics add up: LR_cc = LR_uc + LR_ind, asymptotically chi-square(2)."
            },
            "ro": {
                "title": "Acoperirea condiționată",
                "text": "Cum se formează statistica de acoperire condiționată LR_cc și ce distribuție are sub H0?",
                "options": [
                    "LR_cc = LR_uc + LR_ind, hi-pătrat cu 2 grade de libertate",
                    "LR_cc = LR_uc x LR_ind, Normală",
                    "LR_cc = LR_uc - LR_ind, hi-pătrat cu 1 grad de libertate",
                    "LR_cc = max(LR_uc, LR_ind), Student-t"
                ],
                "correctExplanation": "Acoperirea condiționată testează ambele proprietăți simultan: suma celor două rapoarte de verosimilitate este asimptotic hi-pătrat(2).",
                "incorrectExplanation": "Cele două statistici se adună: LR_cc = LR_uc + LR_ind, asimptotic hi-pătrat(2)."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Duration test",
                "text": "In the Christoffersen-Pelletier duration test, what does an estimated Weibull shape b well below 1 indicate?",
                "options": [
                    "Too few breaches",
                    "Perfectly independent breaches",
                    "A Normal distribution of losses",
                    "Too many short durations: breaches come in clusters"
                ],
                "correctExplanation": "b = 1 is the memoryless (exponential) case; b < 1 means short gaps between breaches are too frequent, the signature of clustering. On the S&P 500, HS gives b = 0.52.",
                "incorrectExplanation": "A shape below one means clustered breaches: short durations are over-represented."
            },
            "ro": {
                "title": "Testul de durată",
                "text": "În testul de durată Christoffersen-Pelletier, ce indică o formă Weibull estimată b mult sub 1?",
                "options": [
                    "Prea puține depășiri",
                    "Depășiri perfect independente",
                    "O distribuție Normală a pierderilor",
                    "Prea multe durate scurte: depășirile apar grupat"
                ],
                "correctExplanation": "b = 1 este cazul fără memorie (exponențial); b < 1 înseamnă că intervalele scurte dintre depășiri sînt prea frecvente, semnul grupării. Pe S&P 500, HS are b = 0,52.",
                "incorrectExplanation": "O formă sub unu înseamnă depășiri grupate: duratele scurte sînt suprareprezentate."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "DQ versus Christoffersen",
                "text": "A model's breaches tend to occur five days after a previous breach, while the breach probability the day after a breach is normal. Which test is designed to detect this?",
                "options": [
                    "Christoffersen's first-order Markov independence test",
                    "The Kupiec POF test",
                    "The Basel traffic light",
                    "The DQ test with lagged hits up to lag 5 (or the duration test)"
                ],
                "correctExplanation": "The DQ regression of Hit_t on lagged hits and the VaR level detects predictability at any included lag; the duration test also sees the unusual spacing. A first-order chain only compares yesterday with today.",
                "incorrectExplanation": "Coverage counts and the traffic light ignore timing, and the Markov test looks only one day back, so a pattern at lag 5 escapes all three."
            },
            "ro": {
                "title": "DQ față de Christoffersen",
                "text": "Depășirile unui model tind să apară la cinci zile după o depășire anterioară, iar probabilitatea de depășire în ziua de după o depășire este normală. Ce test este construit să detecteze aceasta?",
                "options": [
                    "Testul de independență Christoffersen, cu lanț Markov de ordinul întîi",
                    "Testul POF Kupiec",
                    "Semaforul Basel",
                    "Testul DQ cu depășiri întîrziate pînă la lagul 5 (sau testul de durată)"
                ],
                "correctExplanation": "Regresia DQ a lui Hit_t pe depășirile întîrziate și pe nivelul VaR detectează previzibilitatea la orice lag inclus; testul de durată vede și el distanțele neobișnuite. Un lanț de ordinul întîi compară doar ziua de ieri cu cea de azi.",
                "incorrectExplanation": "Testele de numărare și semaforul ignoră momentul depășirilor, iar testul Markov privește doar o zi înapoi, deci un tipar la lagul 5 le scapă tuturor."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Size of backtests in one year",
                "text": "In the lecture's Monte Carlo (correct GARCH-t VaR 1%, T = 250), which statement about the 5% tests is correct?",
                "options": [
                    "All four tests reject in about 5% of samples",
                    "The Kupiec test rejects in about 10% of samples, mostly because zero breaches already falls in its rejection region",
                    "The duration test is always computable and exactly sized",
                    "The Christoffersen conditional coverage test is oversized"
                ],
                "correctExplanation": "At T = 250, P(x = 0) = 0.99^250 = 8.1% already lies in the Kupiec rejection region, so the exact size is about 9.5%; the duration test is undefined in 28% of samples and oversized, CC is undersized.",
                "incorrectExplanation": "With only 2.5 expected breaches, the asymptotic chi-square levels are not attained: size must be simulated at the sample length used."
            },
            "ro": {
                "title": "Mărimea testelor pe un an",
                "text": "În simularea Monte Carlo din curs (VaR 1% GARCH-t corect, T = 250), care afirmație despre testele la 5% este corectă?",
                "options": [
                    "Toate cele patru teste resping în circa 5% din eșantioane",
                    "Testul Kupiec respinge în circa 10% din eșantioane, mai ales pentru că zero depășiri cade deja în regiunea lui de respingere",
                    "Testul de durată este mereu calculabil și are exact mărimea nominală",
                    "Testul de acoperire condiționată Christoffersen este supradimensionat"
                ],
                "correctExplanation": "La T = 250, P(x = 0) = 0,99^250 = 8,1% se află deja în regiunea de respingere Kupiec, deci mărimea exactă este de circa 9,5%; testul de durată nu este definit în 28% din eșantioane și este supradimensionat, iar CC este subdimensionat.",
                "incorrectExplanation": "Cu doar 2,5 depășiri așteptate, nivelurile asimptotice hi-pătrat nu sînt atinse: mărimea trebuie simulată la lungimea eșantionului folosit."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Why ES is hard",
                "text": "Why is ES harder to backtest than VaR?",
                "options": [
                    "It depends on the size of losses beyond VaR, and only about alpha T tail days carry information",
                    "It is always smaller than VaR",
                    "It cannot be computed for fat-tailed distributions",
                    "Regulators do not allow ES backtests"
                ],
                "correctExplanation": "ES is an average over the tail; the tail sample has about alpha T observations (6.25 in one year for alpha = 2.5%), so its precision is low.",
                "incorrectExplanation": "The difficulty is information: ES is a tail average estimated from very few observations."
            },
            "ro": {
                "title": "Dificultatea testării ES",
                "text": "De ce ES este mai greu de testat decît VaR?",
                "options": [
                    "Depinde de mărimea pierderilor de dincolo de VaR, iar doar circa alpha T zile din coadă aduc informație",
                    "Este întotdeauna mai mic decît VaR",
                    "Nu poate fi calculat pentru distribuții cu cozi groase",
                    "Reglementatorii nu permit teste pentru ES"
                ],
                "correctExplanation": "ES este o medie peste coadă; eșantionul din coadă are circa alpha T observații (6,25 într-un an pentru alpha = 2,5%), deci precizia este redusă.",
                "incorrectExplanation": "Dificultatea ține de informație: ES este o medie din coadă estimată din foarte puține observații."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Why E[Z2] = 0",
                "text": "Under a correct forecast distribution, which identity gives E[Z2] = 0 for the Acerbi-Szekely statistic Z2 = 1 - (1/(T alpha)) sum L_t I_t / ES_t?",
                "options": [
                    "E[I_t] = alpha, on its own",
                    "E[L_t] = 0",
                    "E[L_t 1{L_t > VaR_t} | F_{t-1}] = alpha ES_t",
                    "ES_t = VaR_t"
                ],
                "correctExplanation": "E[L_t I_t | F_{t-1}] = P(breach) E[L_t | breach] = alpha ES_t; since ES_t is known at t-1, each ratio has mean alpha and the known denominator T alpha makes the mean exactly zero.",
                "incorrectExplanation": "The coverage identity alone says nothing about the size of tail losses; the proof needs E[L_t I_t | F_{t-1}] = alpha ES_t, i.e. the mean loss on breach days equal to ES_t, multiplied by the breach probability alpha."
            },
            "ro": {
                "title": "Justificarea relației E[Z2] = 0",
                "text": "Pentru o distribuție prognozată corectă, ce identitate dă E[Z2] = 0 pentru statistica Acerbi-Szekely Z2 = 1 - (1/(T alpha)) sum L_t I_t / ES_t?",
                "options": [
                    "E[I_t] = alpha, singură",
                    "E[L_t] = 0",
                    "E[L_t 1{L_t > VaR_t} | F_{t-1}] = alpha ES_t",
                    "ES_t = VaR_t"
                ],
                "correctExplanation": "E[L_t I_t | F_{t-1}] = P(depășire) E[L_t | depășire] = alpha ES_t; cum ES_t este cunoscut la t-1, fiecare raport are media alpha, iar numitorul cunoscut T alpha face media exact zero.",
                "incorrectExplanation": "Identitatea de acoperire singură nu spune nimic despre mărimea pierderilor din coadă; demonstrația cere E[L_t I_t | F_{t-1}] = alpha ES_t, adică media pierderilor din zilele cu depășire egală cu ES_t, înmulțită cu probabilitatea de depășire alpha."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Ranking ES by squared error",
                "text": "Ranking ES forecasts by the mean of (L_t - ES_t)^2 over each model's own breach days (L_t > its VaR_t)",
                "options": [
                    "can favour a wrong forecast, because this score is not consistent for ES",
                    "is consistent, because ES is a conditional mean",
                    "is consistent if T is large enough",
                    "is equivalent to ranking by Z1"
                ],
                "correctExplanation": "ES alone is not elicitable: its level sets are not convex, so no score of ES alone rewards the true value; the breach days also depend on the VaR forecast. Consistent ranking needs a joint (VaR, ES) score such as FZ0.",
                "incorrectExplanation": "A larger sample does not repair an inconsistent score; ES is a conditional mean only given the VaR, which the squared error does not score."
            },
            "ro": {
                "title": "Clasificarea ES după eroarea pătratică",
                "text": "Clasificarea prognozelor ES după media lui (L_t - ES_t)^2 în zilele cu depășire ale fiecărui model (L_t > VaR_t al lui)",
                "options": [
                    "poate favoriza o prognoză greșită, pentru că acest scor nu este consistent pentru ES",
                    "este consistentă, pentru că ES este o medie condiționată",
                    "este consistentă dacă T este suficient de mare",
                    "este echivalentă cu clasificarea după Z1"
                ],
                "correctExplanation": "ES singur nu este elicitabil: mulțimile lui de nivel nu sînt convexe, deci niciun scor care depinde doar de ES nu recompensează valoarea adevărată; în plus, zilele cu depășire depind de prognoza VaR. Clasificarea consistentă cere un scor comun (VaR, ES), precum FZ0.",
                "incorrectExplanation": "Un eșantion mai mare nu corectează un scor inconsistent; ES este o medie condiționată doar dat fiind VaR, pe care eroarea pătratică nu îl evaluează."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Why the pinball loss is consistent",
                "text": "Let L have a density f > 0 around its unique (1 - alpha)-quantile. Differentiating E[(1{L > v} - alpha)(L - v)] with respect to v gives F(v) - (1 - alpha). What follows?",
                "options": [
                    "The minimiser is the mean of L",
                    "The minimiser satisfies F(v) = 1 - alpha, i.e. v = VaR_alpha, and the second derivative f(v) > 0 makes it a minimum",
                    "The minimiser is ES_alpha",
                    "The pinball loss has no unique minimiser under this assumption"
                ],
                "correctExplanation": "The first-order condition identifies the (1 - alpha)-quantile of the loss, which is VaR_alpha; the identification function 1{L <= v} - (1 - alpha) has mean zero only there.",
                "incorrectExplanation": "Set the derivative to zero: P(L > v) = alpha, which is the definition of the VaR, not of the mean or of ES."
            },
            "ro": {
                "title": "Consistența pierderii pinball",
                "text": "Fie L cu densitatea f > 0 în jurul cuantilei sale unice de ordin 1 - alpha. Derivînd E[(1{L > v} - alpha)(L - v)] în raport cu v obținem F(v) - (1 - alpha). Ce rezultă?",
                "options": [
                    "Punctul de minim este media lui L",
                    "Punctul de minim satisface F(v) = 1 - alpha, adică v = VaR_alpha, iar derivata a doua f(v) > 0 îl face minim",
                    "Punctul de minim este ES_alpha",
                    "Pierderea pinball nu are un minim unic sub această ipoteză"
                ],
                "correctExplanation": "Condiția de ordinul întîi identifică cuantila de ordin 1 - alpha a pierderii, adică VaR_alpha; funcția de identificare 1{L <= v} - (1 - alpha) are media zero doar acolo.",
                "incorrectExplanation": "Egalați derivata cu zero: P(L > v) = alpha, care este chiar definiția VaR, nu a mediei sau a ES."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "ES and elicitability",
                "text": "Which statement about ES and elicitability is correct?",
                "options": [
                    "ES is elicitable on its own with the squared error",
                    "ES is not elicitable alone, but the pair (VaR, ES) is jointly elicitable",
                    "Neither VaR nor ES is elicitable",
                    "ES is elicitable only for Normal distributions"
                ],
                "correctExplanation": "Gneiting (2011) showed that ES alone is not elicitable; Fissler and Ziegel (2016) characterised the scoring functions that make (VaR, ES) jointly elicitable, such as FZ0.",
                "incorrectExplanation": "ES alone fails, but together with VaR it becomes elicitable (Fissler-Ziegel family)."
            },
            "ro": {
                "title": "ES și elicitabilitatea",
                "text": "Care afirmație despre ES și elicitabilitate este corectă?",
                "options": [
                    "ES este elicitabil singur, cu eroarea pătratică",
                    "ES nu este elicitabil singur, dar perechea (VaR, ES) este elicitabilă împreună",
                    "Nici VaR, nici ES nu sînt elicitabile",
                    "ES este elicitabil doar pentru distribuții Normale"
                ],
                "correctExplanation": "Gneiting (2011) a arătat că ES singur nu este elicitabil; Fissler și Ziegel (2016) au caracterizat funcțiile de scor care fac perechea (VaR, ES) elicitabilă, de exemplu FZ0.",
                "incorrectExplanation": "ES singur nu este elicitabil, dar împreună cu VaR devine (familia Fissler-Ziegel)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "FZ0 loss",
                "text": "In the FZ0 loss (1{L>v}(L-v))/(alpha e) + v/e + ln e - 1, what does the first term do?",
                "options": [
                    "It increases when the reported ES increases, holding the loss and VaR fixed",
                    "It penalises forecasts on quiet days",
                    "It penalises breaches, in proportion to the excess loss and inversely to the reported ES",
                    "It measures the variance of losses"
                ],
                "correctExplanation": "Only breach days contribute to the first term; the other terms penalise reporting a large ES, so the optimum balances the two.",
                "incorrectExplanation": "The first term is the breach penalty: excess loss divided by alpha times ES."
            },
            "ro": {
                "title": "Pierderea FZ0",
                "text": "În pierderea FZ0 (1{L>v}(L-v))/(alpha e) + v/e + ln e - 1, ce face primul termen?",
                "options": [
                    "Crește cînd ES raportat crește, la pierdere și VaR fixe",
                    "Penalizează prognozele în zilele liniștite",
                    "Penalizează depășirile, proporțional cu pierderea în exces și invers proporțional cu ES raportat",
                    "Măsoară dispersia pierderilor"
                ],
                "correctExplanation": "Doar zilele cu depășire contribuie la primul termen; ceilalți termeni penalizează raportarea unui ES mare, deci optimul le echilibrează.",
                "incorrectExplanation": "Primul termen este penalizarea depășirilor: pierderea în exces împărțită la alpha ori ES."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Diebold-Mariano",
                "text": "Why is a Newey-West (HAC) variance used in the Diebold-Mariano test on FZ0 losses?",
                "options": [
                    "Because tail losses cluster, so the loss differential is autocorrelated",
                    "Because FZ0 losses are always Normal",
                    "To make the test one-sided",
                    "Because the test needs at least two assets"
                ],
                "correctExplanation": "The long-run variance accounts for autocorrelation; for HS versus FHS on the S&P 500 it is about 2.3 times the ordinary variance, and the naive t-statistic overstates significance.",
                "incorrectExplanation": "Loss differentials are autocorrelated in crises; a HAC long-run variance corrects the standard error."
            },
            "ro": {
                "title": "Diebold-Mariano",
                "text": "De ce se folosește o dispersie Newey-West (HAC) în testul Diebold-Mariano pe pierderile FZ0?",
                "options": [
                    "Pentru că pierderile din coadă se grupează, deci diferența de pierdere este autocorelată",
                    "Pentru că pierderile FZ0 sînt mereu Normale",
                    "Pentru a face testul unilateral",
                    "Pentru că testul are nevoie de cel puțin două active"
                ],
                "correctExplanation": "Dispersia pe termen lung ține cont de autocorelație; pentru HS față de FHS pe S&P 500 este de circa 2,3 ori dispersia obișnuită, iar statistica t naivă supraestimează semnificația.",
                "incorrectExplanation": "Diferențele de pierdere sînt autocorelate în crize; o dispersie HAC pe termen lung corectează eroarea standard."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Model confidence set",
                "text": "What does a model confidence set (Hansen, Lunde and Nason, 2011) contain?",
                "options": [
                    "Only the single best model",
                    "All models that pass the Kupiec test",
                    "The models with positive DM statistics",
                    "A set built by sequential elimination to contain the best models with a given asymptotic probability"
                ],
                "correctExplanation": "Models are eliminated one by one while equal predictive ability is rejected; the survivors form the MCS. On Bitcoin all six models survive: the data cannot separate them.",
                "incorrectExplanation": "The MCS is a set of models that the data cannot separate from the best, not a single winner; non-rejection is not proof of equal performance."
            },
            "ro": {
                "title": "Mulțimea de modele de încredere",
                "text": "Ce conține o mulțime de modele de încredere (Hansen, Lunde și Nason, 2011)?",
                "options": [
                    "Doar cel mai bun model",
                    "Toate modelele care trec testul Kupiec",
                    "Modelele cu statistici DM pozitive",
                    "O mulțime construită prin eliminări succesive astfel încît să conțină modelele cele mai bune cu o probabilitate asimptotică dată"
                ],
                "correctExplanation": "Modelele sînt eliminate unul cîte unul cît timp egalitatea abilității predictive este respinsă; cele rămase formează MCS. Pe Bitcoin rămîn toate cele șase modele: datele nu le pot separa.",
                "incorrectExplanation": "MCS este o mulțime de modele pe care datele nu le pot separa de cel mai bun, nu un singur cîștigător; nerespingerea nu dovedește că modelele sînt la fel de bune."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Conformal coverage beyond exchangeability",
                "text": "Split conformal VaR 5% breaches on about 7% of S&P 500 crisis days. Without exchangeability, the coverage gap of split conformal is bounded by",
                "options": [
                    "1/(n + 1)",
                    "the ACI step size gamma",
                    "zero, by the finite-sample guarantee",
                    "weighted total-variation distances between the joint score vector and the vectors obtained by swapping the test score with each calibration score (Barber et al., 2023)"
                ],
                "correctExplanation": "Barber, Candès, Ramdas and Tibshirani (2023) bound the loss of marginal coverage by weighted total-variation distances between the joint score vector and its swapped versions; the bound concerns marginal coverage, not coverage on crisis days.",
                "incorrectExplanation": "The finite-sample guarantee requires exchangeability; 1/(n + 1) is only the upper slack of coverage under exchangeability, and gamma belongs to ACI."
            },
            "ro": {
                "title": "Acoperirea conformală fără schimbabilitate",
                "text": "VaR 5% conformal split este depășit în circa 7% dintre zilele de criză S&P 500. Fără schimbabilitate, abaterea acoperirii conformale split este mărginită de",
                "options": [
                    "1/(n + 1)",
                    "pasul ACI gamma",
                    "zero, datorită garanției în eșantion finit",
                    "distanțe ponderate în variație totală între vectorul comun al scorurilor și vectorii obținuți schimbînd scorul de test cu fiecare scor de calibrare (Barber et al., 2023)"
                ],
                "correctExplanation": "Barber, Candès, Ramdas și Tibshirani (2023) mărginesc pierderea de acoperire marginală prin distanțe ponderate în variație totală între vectorul comun al scorurilor și versiunile lui cu scoruri schimbate; marginea privește acoperirea marginală, nu acoperirea în zilele de criză.",
                "incorrectExplanation": "Garanția în eșantion finit cere schimbabilitate; 1/(n + 1) este doar marja superioară a acoperirii sub schimbabilitate, iar gamma ține de ACI."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Exchangeability",
                "text": "Why can the split conformal guarantee not simply be invoked for VaR on financial returns, and why does it say nothing about crisis days?",
                "options": [
                    "Because returns have a mean of zero",
                    "Because the method needs Normal data",
                    "Because volatility clustering makes the scores non-exchangeable, and even under exchangeability the guarantee is only marginal",
                    "Because the calibration set is too large"
                ],
                "correctExplanation": "The finite-sample guarantee needs exchangeable scores, which volatility clustering breaks; even with exchangeable scores it is marginal, not conditional on crisis days. After turbulent periods the S&P 500 split conformal VaR 5% is breached on about 7% of days, and breaches cluster.",
                "incorrectExplanation": "The assumption that breaks is exchangeability, and conditional coverage was never guaranteed: split conformal controls only average coverage."
            },
            "ro": {
                "title": "Schimbabilitate",
                "text": "De ce garanția conformală split nu poate fi invocată direct pentru VaR pe randamente financiare și de ce nu spune nimic despre zilele de criză?",
                "options": [
                    "Pentru că randamentele au media zero",
                    "Pentru că metoda cere date Normale",
                    "Pentru că volatility clustering face scorurile neschimbabile, iar chiar sub schimbabilitate garanția este doar marginală",
                    "Pentru că mulțimea de calibrare este prea mare"
                ],
                "correctExplanation": "Garanția în eșantion finit cere scoruri schimbabile, iar volatility clustering distruge această proprietate; chiar cu scoruri schimbabile, garanția este marginală, nu condiționată de zilele de criză. După perioade agitate, VaR conformal split 5% pe S&P 500 este depășit în circa 7% dintre zile, iar depășirile se grupează.",
                "incorrectExplanation": "Ipoteza care cade este schimbabilitatea, iar acoperirea condiționată nu a fost niciodată garantată: conformal split controlează doar acoperirea medie."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Giacomini-White versus Diebold-Mariano",
                "text": "Forecasts come from rolling 1000-day windows with re-estimated GARCH parameters. Which test of equal predictive accuracy has a valid asymptotic justification for comparing them?",
                "options": [
                    "The Giacomini-White test of (conditional) predictive ability of the forecasting methods",
                    "The Diebold-Mariano test with an i.i.d. variance",
                    "A Kupiec test on the loss differential",
                    "A Mincer-Zarnowitz regression of losses on forecasts"
                ],
                "correctExplanation": "Giacomini and White (2006) test the forecasting method, including its estimation, and allow a finite rolling window where estimation error never vanishes; with a constant test function the statistic has the DM form.",
                "incorrectExplanation": "The DM justification targets population model accuracy; with finite rolling windows the object compared is the method, and the i.i.d. variance also ignores autocorrelated losses."
            },
            "ro": {
                "title": "Giacomini-White față de Diebold-Mariano",
                "text": "Prognozele provin din ferestre mobile de 1000 de zile, cu parametri GARCH reestimați. Ce test de acuratețe predictivă egală are o justificare asimptotică validă pentru compararea lor?",
                "options": [
                    "Testul Giacomini-White al abilității predictive (condiționate) a metodelor de prognoză",
                    "Testul Diebold-Mariano cu dispersie i.i.d.",
                    "Un test Kupiec pe diferența de pierdere",
                    "O regresie Mincer-Zarnowitz a pierderilor pe prognoze"
                ],
                "correctExplanation": "Giacomini și White (2006) testează metoda de prognoză, inclusiv estimarea ei, și permit o fereastră mobilă finită, în care eroarea de estimare nu dispare; cu o funcție test constantă, statistica are forma DM.",
                "incorrectExplanation": "Justificarea DM vizează acuratețea populațională a modelelor; cu ferestre mobile finite, obiectul comparat este metoda, iar dispersia i.i.d. ignoră și autocorelația pierderilor."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "The price of ACI",
                "text": "For VaR 1% on the S&P 500, how did ACI keep its long-run breach rate near 1%?",
                "options": [
                    "By using a GARCH model",
                    "By shrinking the calibration set to 20 days",
                    "By ignoring crisis days",
                    "By returning an infinite VaR on a sizeable share of days (about 13%)"
                ],
                "correctExplanation": "When alpha_t falls below 1/(n+1) the required quantile does not exist and the VaR becomes infinite; this happened on about 13% of S&P 500 days: coverage without information.",
                "incorrectExplanation": "The guarantee was bought with infinite VaR forecasts on many days."
            },
            "ro": {
                "title": "Costul garanției ACI",
                "text": "Pentru VaR 1% pe S&P 500, cum și-a menținut ACI rata de depășire pe termen lung aproape de 1%?",
                "options": [
                    "Folosind un model GARCH",
                    "Reducînd mulțimea de calibrare la 20 de zile",
                    "Ignorînd zilele de criză",
                    "Dînd un VaR infinit într-o parte importantă a zilelor (circa 13%)"
                ],
                "correctExplanation": "Cînd alpha_t scade sub 1/(n+1), cuantila cerută nu există și VaR devine infinit; aceasta s-a întîmplat în circa 13% dintre zilele S&P 500: acoperire fără informație.",
                "incorrectExplanation": "Garanția a fost obținută prin prognoze VaR infinite în multe zile."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Reading a Murphy diagram",
                "text": "For VaR 1% on the S&P 500 the mean elementary-score curves of GARCH-t and FHS cross several times. What follows?",
                "options": [
                    "FHS dominates GARCH-t under every consistent score",
                    "Both forecasts are miscalibrated",
                    "Some consistent scoring functions rank GARCH-t first and others FHS: the pinball ranking is score-specific",
                    "The Diebold-Mariano test is invalid for these forecasts"
                ],
                "correctExplanation": "Every consistent quantile score is a mixture of elementary scores; one forecast dominates only if its curve is lower at every threshold. Crossing curves mean the ranking depends on the weights, for example on how much crisis thresholds matter.",
                "incorrectExplanation": "Dominance needs one curve below the other everywhere; crossing curves say nothing about calibration or about the validity of a test on a chosen score."
            },
            "ro": {
                "title": "Interpretarea unei diagrame Murphy",
                "text": "Pentru VaR 1% pe S&P 500, curbele scorurilor elementare medii ale GARCH-t și FHS se intersectează de mai multe ori. Ce rezultă?",
                "options": [
                    "FHS domină GARCH-t sub orice scor consistent",
                    "Ambele prognoze sînt decalibrate",
                    "Unele funcții de scor consistente pun GARCH-t pe primul loc, altele FHS: clasamentul după pierderea pinball depinde de scor",
                    "Testul Diebold-Mariano nu este valid pentru aceste prognoze"
                ],
                "correctExplanation": "Orice scor consistent pentru cuantile este o mixtură de scoruri elementare; o prognoză domină doar dacă curba ei este mai jos la fiecare prag. Curbele care se intersectează arată că clasamentul depinde de ponderi, de exemplu de cît contează pragurile de criză.",
                "incorrectExplanation": "Dominanța cere ca o curbă să fie sub cealaltă peste tot; intersecția curbelor nu spune nimic despre calibrare sau despre validitatea unui test pe un scor ales."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "March 2020",
                "text": "In February-June 2020 (104 days) the VaR 1% of the S&P 500 was breached 12 times by HS and 2 times by FHS. What explains the difference?",
                "options": [
                    "FHS uses a longer window",
                    "FHS scales its quantiles by the current GARCH volatility, which rose within days",
                    "HS assumes the Normal distribution",
                    "FHS ignores the largest losses"
                ],
                "correctExplanation": "HS updates as days enter and leave its 1000-day window but has no current-volatility scaling, so it adapts slowly; FHS multiplies empirical standardised quantiles by today's volatility forecast, so it adapts to the crash almost immediately.",
                "incorrectExplanation": "Conditioning on current volatility, not the tail shape, made the difference."
            },
            "ro": {
                "title": "Martie 2020",
                "text": "În februarie-iunie 2020 (104 zile), VaR 1% pentru S&P 500 a fost depășit de 12 ori de HS și de 2 ori de FHS. Ce explică diferența?",
                "options": [
                    "FHS folosește o fereastră mai lungă",
                    "FHS scalează cuantilele cu volatilitatea GARCH curentă, care a crescut în cîteva zile",
                    "HS presupune distribuția Normală",
                    "FHS ignoră cele mai mari pierderi"
                ],
                "correctExplanation": "HS se actualizează pe măsură ce zilele intră și ies din fereastra de 1000 de zile, dar nu are scalare cu volatilitatea curentă, deci se adaptează lent; FHS înmulțește cuantilele empirice standardizate cu volatilitatea prognozată azi, deci se adaptează aproape imediat la crah.",
                "incorrectExplanation": "Condiționarea pe volatilitatea curentă, nu forma cozii, a făcut diferența."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Testing versus ranking",
                "text": "What is the difference between a backtest and comparative backtesting?",
                "options": [
                    "There is none",
                    "A backtest ranks models, comparative backtesting tests one model",
                    "Backtests use ES only, comparative backtesting uses VaR only",
                    "A backtest asks whether one model is acceptable; comparative backtesting asks which of several models is better, using a consistent score"
                ],
                "correctExplanation": "Several models can pass (or all can fail) a backtest; ranking requires a consistent scoring function such as FZ0 and tests such as Diebold-Mariano (Nolde and Ziegel, 2017).",
                "incorrectExplanation": "Testing checks acceptability of one model; comparative backtesting ranks models with a scoring function."
            },
            "ro": {
                "title": "Testare și clasificare",
                "text": "Care este diferența dintre un backtest și backtesting-ul comparativ?",
                "options": [
                    "Nu există nicio diferență",
                    "Un backtest clasifică modelele, backtesting-ul comparativ testează un singur model",
                    "Backtest-urile folosesc doar ES, cel comparativ doar VaR",
                    "Un backtest întreabă dacă un model este acceptabil; backtesting-ul comparativ întreabă care dintre mai multe modele este mai bun, cu un scor consistent"
                ],
                "correctExplanation": "Un backtest poate accepta mai multe modele (sau le poate respinge pe toate); clasificarea cere o funcție de scor consistentă, cum este FZ0, și teste precum Diebold-Mariano (Nolde și Ziegel, 2017).",
                "incorrectExplanation": "Testarea verifică acceptabilitatea unui model; backtesting-ul comparativ clasifică modelele cu o funcție de scor."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the AI error: Christoffersen test",
                "text": "An AI assistant writes: \"The conditional coverage statistic LR_cc = LR_uc + LR_ind is compared with the chi-square distribution with 1 degree of freedom, so we reject at 5% when LR_cc > 3.84.\" What is wrong?",
                "options": [
                    "LR_cc should be the product of LR_uc and LR_ind, not their sum",
                    "The Christoffersen test uses the Normal distribution, not the chi-square",
                    "The degrees of freedom: LR_cc tests two restrictions and is chi-square with 2 degrees of freedom, 5% critical value 5.99",
                    "LR_ind already contains LR_uc, so LR_cc = LR_ind"
                ],
                "correctExplanation": "LR_cc jointly tests the correct breach rate (pi = p) and independence (pi_01 = pi_11): two restrictions, so chi-square(2) with 5% critical value 5.99 (Christoffersen, 1998). With 1 degree of freedom the test rejects correct models too often.",
                "incorrectExplanation": "The sum LR_uc + LR_ind is right; the mistake is the reference distribution, which must have 2 degrees of freedom."
            },
            "ro": {
                "title": "Găsiți eroarea AI: testul Christoffersen",
                "text": "Un asistent AI scrie: „Statistica de acoperire condiționată LR_cc = LR_uc + LR_ind se compară cu distribuția hi-pătrat cu 1 grad de libertate, deci respingem la 5% cînd LR_cc > 3,84.” Ce este greșit?",
                "options": [
                    "LR_cc ar trebui să fie produsul lui LR_uc și LR_ind, nu suma lor",
                    "Testul Christoffersen folosește distribuția Normală, nu hi-pătrat",
                    "Gradele de libertate: LR_cc testează două restricții și urmează hi-pătrat cu 2 grade de libertate, valoarea critică de 5% fiind 5,99",
                    "LR_ind îl conține deja pe LR_uc, deci LR_cc = LR_ind"
                ],
                "correctExplanation": "LR_cc testează împreună rata corectă a depășirilor (pi = p) și independența (pi_01 = pi_11): două restricții, deci hi-pătrat(2), cu valoarea critică de 5% egală cu 5,99 (Christoffersen, 1998). Cu 1 grad de libertate testul respinge prea des modelele corecte.",
                "incorrectExplanation": "Suma LR_uc + LR_ind este corectă; greșeala este distribuția de referință, care trebuie să aibă 2 grade de libertate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: rolling VaR window",
                "text": "An AI assistant writes: \"For the historical-simulation VaR 1% of day t, take minus the 1% quantile of the 250 returns r_{t-249}, ..., r_t, then flag an exception when -r_t exceeds it.\" What is wrong?",
                "options": [
                    "VaR should be plus the 1% quantile, not minus",
                    "The window contains r_t itself: VaR_t must use only returns known at t-1, i.e. r_{t-250}, ..., r_{t-1}",
                    "An exception is flagged when r_t exceeds VaR, not -r_t",
                    "Historical simulation needs at least 1,000 days, so 250 is not allowed"
                ],
                "correctExplanation": "This is look-ahead bias: a large loss on day t enters its own quantile and hides the exception, so the backtest looks better than it is. The sign convention (VaR = minus the quantile, exception when the loss -r_t exceeds VaR) is correct.",
                "incorrectExplanation": "The sign convention and the exception rule are right; the error is that the forecast for day t uses the return of day t."
            },
            "ro": {
                "title": "Găsiți eroarea AI: fereastra VaR mobilă",
                "text": "Un asistent AI scrie: „Pentru VaR 1% prin simulare istorică în ziua t, luați minus cuantila de 1% a celor 250 de randamente r_{t-249}, ..., r_t, apoi marcați o excepție cînd -r_t îl depășește.” Ce este greșit?",
                "options": [
                    "VaR ar trebui să fie plus cuantila de 1%, nu minus",
                    "Fereastra îl conține chiar pe r_t: VaR_t trebuie să folosească doar randamentele cunoscute în t-1, adică r_{t-250}, ..., r_{t-1}",
                    "O excepție apare cînd r_t depășește VaR, nu -r_t",
                    "Simularea istorică cere cel puțin 1.000 de zile, deci 250 nu este permis"
                ],
                "correctExplanation": "Acesta este look-ahead bias: o pierdere mare în ziua t intră în propria cuantilă și ascunde excepția, astfel că backtest-ul pare mai bun decît este. Convenția de semn (VaR = minus cuantila, excepție cînd pierderea -r_t depășește VaR) este corectă.",
                "incorrectExplanation": "Convenția de semn și regula de excepție sînt corecte; greșeala este că prognoza pentru ziua t folosește randamentul din ziua t."
            }
        }
    ]
};

// ============================================================
// Quiz bank for chapter id 'options': Options and the Volatility Surface (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['options'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 1,
            "en": {
                "title": "Jump bias of the VIX",
                "text": "If S&P 500 prices can jump, what does the annualised strip variance (VIX/100)^2 measure in the ideal limit of a continuum of strikes (a strip of OTM options weighted by 1/K^2, horizon T)?",
                "options": [
                    "Annualised expected quadratic variation E^Q[QV]/T, exactly, in any model",
                    "E^Q[-2 ln(S_T/F)]/T, which differs from annualised expected quadratic variation by a jump term",
                    "The squared at-the-money implied volatility",
                    "E^P[RV]/T, the annualised expected realised variance under the real-world probability"
                ],
                "correctExplanation": "(VIX/100)^2 = E^Q[-2 ln(S_T/F)]/T with a continuum of strikes (the VIX index is 100 times its square root). Itô's lemma makes the log contract equal to integrated variance only for continuous paths; with jumps J the gap is 2E^Q[sum(e^J - 1 - J - J^2/2)], about E^Q[sum J^3]/3, negative for crashes (-2.0% of variance in the lecture's Merton example).",
                "incorrectExplanation": "The strip prices the log contract. It equals expected quadratic variation only without jumps, and it is an expectation under the pricing measure Q, not under the real-world measure."
            },
            "ro": {
                "title": "Deplasarea VIX din salturi",
                "text": "Dacă prețurile S&P 500 pot avea salturi, ce măsoară varianța anualizată a benzii, (VIX/100)^2, în limita ideală a unui continuum de prețuri de exercitare (o bandă de opțiuni OTM ponderate cu 1/K^2, orizontul T)?",
                "options": [
                    "Variația pătratică așteptată anualizată E^Q[QV]/T, exact, în orice model",
                    "E^Q[-2 ln(S_T/F)]/T, care diferă de variația pătratică așteptată anualizată printr-un termen de salt",
                    "Pătratul volatilității implicite la bani",
                    "E^P[RV]/T, varianța realizată așteptată anualizată sub probabilitatea reală"
                ],
                "correctExplanation": "(VIX/100)^2 = E^Q[-2 ln(S_T/F)]/T pentru un continuum de prețuri de exercitare (indicele VIX este de 100 de ori rădăcina ei pătrată). Lema lui Itô face contractul logaritmic egal cu varianța integrată doar pentru traiectorii continue; cu salturi J diferența este 2E^Q[sum(e^J - 1 - J - J^2/2)], aproximativ E^Q[sum J^3]/3, negativă pentru crahuri (-2,0% din varianță în exemplul Merton din curs).",
                "incorrectExplanation": "Banda evaluează contractul logaritmic. Acesta este egal cu variația pătratică așteptată doar fără salturi și este o speranță sub măsura de evaluare Q, nu sub măsura reală."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Lee's moment formula",
                "text": "An SVI fit of the total implied variance w(k) has a right-wing slope b(1 + rho) = 2.4. What is wrong?",
                "options": [
                    "Nothing: SVI wings must be linear in k",
                    "The wing slope must be exactly 2",
                    "It violates Lee's bound: w(k)/|k| cannot exceed 2 asymptotically, as |k| grows, so the fitted smile admits arbitrage in the wing",
                    "Nothing: only the left wing is constrained by no arbitrage"
                ],
                "correctExplanation": "Lee (2004): limsup w(k)/|k| lies in [0, 2] in both wings, and the slope fixes the number of finite moments of S_T; the fits in the lecture have slopes of at most 0.39.",
                "incorrectExplanation": "No arbitrage allows at most linear growth of total variance, with slope no larger than 2, in both wings; linear is allowed, steeper than 2 is not."
            },
            "ro": {
                "title": "Formula momentelor a lui Lee",
                "text": "O estimare SVI a varianței implicite totale w(k) are panta aripii drepte b(1 + rho) = 2,4. Ce este greșit?",
                "options": [
                    "Nimic: aripile SVI trebuie să fie liniare în k",
                    "Panta aripii trebuie să fie exact 2",
                    "Încalcă limita lui Lee: w(k)/|k| nu poate depăși 2 asimptotic, cînd |k| crește, deci zîmbetul estimat admite arbitraj în aripă",
                    "Nimic: doar aripa stîngă este constrînsă de absența arbitrajului"
                ],
                "correctExplanation": "Lee (2004): limsup w(k)/|k| este în [0, 2] în ambele aripi, iar panta fixează numărul de momente finite ale lui S_T; estimările din curs au pante de cel mult 0,39.",
                "incorrectExplanation": "Absența arbitrajului permite cel mult o creștere liniară a varianței totale, cu panta cel mult 2, în ambele aripi; liniar este permis, mai abrupt decît 2 nu."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Early exercise",
                "text": "Assuming a strictly positive risk-free rate, which American option may be optimally exercised before expiry, even without dividends?",
                "options": [
                    "A call on a stock without dividends",
                    "Any option that is out of the money",
                    "None: early exercise is never optimal",
                    "A put that is deep in the money"
                ],
                "correctExplanation": "Deep in the money, receiving K now and earning interest on it can be worth more than keeping the put alive.",
                "incorrectExplanation": "With r > 0, a call on a stock without dividends is worth more alive than exercised (at least S - K e^{-r tau} > S - K); for puts the interest on K makes early exercise valuable."
            },
            "ro": {
                "title": "Exercitarea anticipată",
                "text": "Presupunînd o rată fără risc strict pozitivă, ce opțiune americană poate fi exercitată optim înainte de scadență, chiar fără dividende?",
                "options": [
                    "Un call pe o acțiune fără dividende",
                    "Orice opțiune în afara banilor",
                    "Niciuna: exercitarea anticipată nu este niciodată optimă",
                    "Un put adînc în bani"
                ],
                "correctExplanation": "Adînc în bani, a încasa K acum și a cîștiga dobînda poate valora mai mult decît a păstra put-ul.",
                "incorrectExplanation": "Cu r > 0, un call pe o acțiune fără dividende valorează mai mult neexercitat decît exercitat (cel puțin S - K e^{-r tau} > S - K); la put-uri dobînda la K face valoroasă exercitarea anticipată."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Joint versus individual tests",
                "text": "Mincer-Zarnowitz regression of 21-day realised variance on VIX^2: intercept -51.9 (s.e. 34.4), slope 0.86 (s.e. 0.10), joint Wald statistic 41.7 with 2 degrees of freedom. What do you conclude?",
                "options": [
                    "Unbiasedness is not rejected, because both t-statistics are below 2",
                    "Unbiasedness is rejected jointly, although neither coefficient alone differs significantly from (0, 1): the two estimates are strongly negatively correlated",
                    "Unbiasedness is rejected because R^2 is below 1",
                    "The VIX is unbiased because the slope is close to 1"
                ],
                "correctExplanation": "The t-statistics are -1.50 and -1.34, but the estimates are correlated -0.90, so the confidence ellipse is thin and tilted and (0, 1) lies far outside it (p below 10^-9).",
                "incorrectExplanation": "A hypothesis on two parameters needs the joint test, which uses their covariance; two individual t-tests ignore it, and R^2 says nothing about bias."
            },
            "ro": {
                "title": "Teste comune și teste individuale",
                "text": "Regresia Mincer-Zarnowitz a varianței realizate pe 21 de zile pe VIX^2: termenul liber -51,9 (e.s. 34,4), panta 0,86 (e.s. 0,10), statistica Wald comună 41,7 cu 2 grade de libertate. Ce concluzionați?",
                "options": [
                    "Prognoza nedeplasată nu este respinsă, pentru că ambele statistici t sînt sub 2",
                    "Prognoza nedeplasată este respinsă împreună, deși niciun coeficient luat separat nu diferă semnificativ de (0, 1): cele două estimări sînt puternic corelate negativ",
                    "Prognoza nedeplasată este respinsă pentru că R^2 este sub 1",
                    "VIX este nedeplasat pentru că panta este aproape de 1"
                ],
                "correctExplanation": "Statisticile t sînt -1,50 și -1,34, dar estimările sînt corelate -0,90, deci elipsa de încredere este îngustă și înclinată, iar (0, 1) este mult în afara ei (p sub 10^-9).",
                "incorrectExplanation": "O ipoteză asupra a doi parametri cere testul comun, care folosește covarianța lor; două teste t separate o ignoră, iar R^2 nu spune nimic despre deplasare."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Gamma near expiry",
                "text": "How does the gamma of an at-the-money option change as expiry approaches?",
                "options": [
                    "It falls to zero",
                    "It stays constant",
                    "It explodes: one day before expiry it is about sqrt(21) times its value one month before",
                    "It becomes negative"
                ],
                "correctExplanation": "ATM gamma is proportional to 1/(sigma sqrt(tau)): with 1 day instead of 21 trading days it is about 4.6 times larger.",
                "incorrectExplanation": "Gamma of an at-the-money option grows like 1/sqrt(tau), which is why hedging options close to expiry is so demanding."
            },
            "ro": {
                "title": "Gamma aproape de scadență",
                "text": "Cum se schimbă gamma unei opțiuni la bani cînd se apropie scadența?",
                "options": [
                    "Scade la zero",
                    "Rămîne constantă",
                    "Explodează: cu o zi înainte de scadență este de aproximativ sqrt(21) ori valoarea de cu o lună înainte",
                    "Devine negativă"
                ],
                "correctExplanation": "Gamma ATM este proporțională cu 1/(sigma sqrt(tau)): cu o zi în loc de 21 de zile de tranzacționare este de aproximativ 4,6 ori mai mare.",
                "incorrectExplanation": "Gamma unei opțiuni la bani crește ca 1/sqrt(tau), motiv pentru care hedging-ul opțiunilor aproape de scadență este atît de solicitant."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Theta and gamma",
                "text": "For a delta-hedged option position under Black-Scholes, what is the link between theta and gamma?",
                "options": [
                    "They are unrelated",
                    "Theta equals gamma",
                    "Both are always positive for a long option",
                    "Theta + 0.5 sigma^2 S^2 Gamma + r S Delta - r C = 0: long gamma is paid for by time decay"
                ],
                "correctExplanation": "This is the Black-Scholes partial differential equation: after financing the delta hedge, Theta + r S Delta - r C = -0.5 sigma^2 S^2 Gamma < 0, so a delta-hedged long-gamma position loses value over time and a short-gamma one earns it. Raw theta alone can be positive, e.g. for a deep in-the-money put.",
                "incorrectExplanation": "The Black-Scholes equation ties theta to gamma: net of financing, the holder of convexity pays for it through time decay."
            },
            "ro": {
                "title": "Theta și gamma",
                "text": "Pentru o poziție în opțiuni cu delta hedging, în modelul Black-Scholes, care este legătura dintre theta și gamma?",
                "options": [
                    "Nu sînt legate",
                    "Theta este egală cu gamma",
                    "Ambele sînt mereu pozitive pentru o opțiune cumpărată",
                    "Theta + 0,5 sigma^2 S^2 Gamma + r S Delta - r C = 0: gamma pozitivă se plătește prin erodarea în timp"
                ],
                "correctExplanation": "Aceasta este ecuația cu derivate parțiale Black-Scholes: după finanțarea delta hedging-ului, Theta + r S Delta - r C = -0,5 sigma^2 S^2 Gamma < 0, deci o poziție cu delta hedging și gamma pozitivă pierde valoare în timp, iar una cu gamma negativă o cîștigă. Theta singură poate fi pozitivă, de exemplu pentru un put adînc în bani.",
                "incorrectExplanation": "Ecuația Black-Scholes leagă theta de gamma: după costul finanțării, deținătorul convexității o plătește prin erodarea în timp."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Hedging frequency",
                "text": "In the lecture simulation the standard deviation of the hedging error falls with the number of rebalancings N with a log-log slope of -0.48. What does this imply?",
                "options": [
                    "The error shrinks like 1/sqrt(N): four times more rebalancings roughly halve it",
                    "The error shrinks like 1/N",
                    "Rebalancing more often does not help",
                    "The error grows with N because of rounding"
                ],
                "correctExplanation": "A slope close to -1/2 means error proportional to 1/sqrt(N): daily hedging left about 9.5% of the premium, four times a day about 4.8%.",
                "incorrectExplanation": "The slope of about -1/2 on a log-log scale means the error is proportional to 1/sqrt(N), not to 1/N."
            },
            "ro": {
                "title": "Frecvența hedging-ului",
                "text": "În simularea din curs, abaterea standard a erorii de hedging scade cu numărul de reechilibrări N cu o pantă log-log de -0,48. Ce implică acest lucru?",
                "options": [
                    "Eroarea scade ca 1/sqrt(N): de patru ori mai multe reechilibrări o înjumătățesc aproximativ",
                    "Eroarea scade ca 1/N",
                    "Reechilibrarea mai deasă nu ajută",
                    "Eroarea crește cu N din cauza rotunjirilor"
                ],
                "correctExplanation": "O pantă apropiată de -1/2 înseamnă o eroare proporțională cu 1/sqrt(N): hedging-ul zilnic a lăsat aproximativ 9,5% din primă, de patru ori pe zi aproximativ 4,8%.",
                "incorrectExplanation": "Panta de aproximativ -1/2 pe scară log-log înseamnă o eroare proporțională cu 1/sqrt(N), nu cu 1/N."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Selling volatility",
                "text": "A dealer sells a call at 20% implied volatility and hedges it daily. Realised volatility turns out to be 25%. What is the expected result?",
                "options": [
                    "A profit, because the premium was collected",
                    "A loss of roughly vega times 5 volatility points",
                    "Zero, because the position is delta-hedged",
                    "A profit equal to theta times the number of days"
                ],
                "correctExplanation": "A delta-hedged option earns implied minus realised variance weighted by gamma: with realised above implied the seller loses about vega x 5 points.",
                "incorrectExplanation": "Delta hedging removes the directional exposure, not the volatility exposure: the seller loses when realised volatility exceeds the implied one."
            },
            "ro": {
                "title": "Vînzarea volatilității",
                "text": "Un dealer vinde un call la volatilitatea implicită de 20% și îi face zilnic delta hedging. Volatilitatea realizată se dovedește a fi 25%. Care este rezultatul așteptat?",
                "options": [
                    "Un profit, pentru că prima a fost încasată",
                    "O pierdere de aproximativ vega înmulțită cu 5 puncte de volatilitate",
                    "Zero, pentru că poziția are delta hedging",
                    "Un profit egal cu theta înmulțită cu numărul de zile"
                ],
                "correctExplanation": "O opțiune cu delta hedging cîștigă varianța implicită minus cea realizată, ponderată cu gamma: cu realizata peste implicită, vînzătorul pierde aproximativ vega x 5 puncte.",
                "incorrectExplanation": "Delta hedging-ul elimină expunerea la direcție, nu expunerea la volatilitate: vînzătorul pierde cînd volatilitatea realizată o depășește pe cea implicită."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Delta-hedged S&P 500 options",
                "text": "Selling one-month at-the-money S&P 500 calls at the VIX and hedging them daily, 1990-2026, gave a mean monthly P&L of 0.48% of the index. Why?",
                "options": [
                    "Because the S&P 500 rose on average",
                    "Because of interest earned on the cash account",
                    "Because the VIX was above the volatility realised afterwards in most months: a volatility risk premium",
                    "Because of a coding convention that ignores losses"
                ],
                "correctExplanation": "The VIX exceeded the realised volatility of the month in 85% of months: option sellers earn a premium for insuring against turbulence.",
                "incorrectExplanation": "A delta-hedged option does not bet on direction; its average gain is the gap between implied and realised volatility, the volatility risk premium."
            },
            "ro": {
                "title": "Opțiuni S&P 500 cu delta hedging",
                "text": "Vînzarea de call-uri S&P 500 la bani pe o lună la VIX, cu delta hedging zilnic, 1990-2026, a dat un rezultat lunar mediu de 0,48% din indice. De ce?",
                "options": [
                    "Pentru că S&P 500 a crescut în medie",
                    "Din cauza dobînzii la contul de numerar",
                    "Pentru că VIX a fost peste volatilitatea realizată ulterior în majoritatea lunilor: o primă de risc a volatilității",
                    "Din cauza unei convenții de calcul care ignoră pierderile"
                ],
                "correctExplanation": "VIX a depășit volatilitatea realizată a lunii în 85% din luni: vînzătorii de opțiuni încasează o primă pentru asigurarea împotriva turbulențelor.",
                "incorrectExplanation": "O opțiune cu delta hedging nu pariază pe direcție; cîștigul ei mediu este diferența dintre volatilitatea implicită și cea realizată, prima de risc a volatilității."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Errors in variables",
                "text": "Why can OLS in RV = alpha + beta VIX^2 + e understate beta?",
                "options": [
                    "Heteroskedastic errors bias the OLS slope towards 0",
                    "Overlapping 21-day windows bias the OLS slope",
                    "VIX^2 measures the true expected variance with error, which attenuates the slope; instrumenting it with the lagged VIX^2 corrects this",
                    "Non-normal residuals bias the OLS slope"
                ],
                "correctExplanation": "Classical measurement error in a regressor biases OLS towards 0 (Christensen and Prabhala, 1998); a lagged value is a valid instrument if its error is uncorrelated with today's. In the lecture data the correction is small: 1.06 (OLS) and 1.02 (instruments) in logs.",
                "incorrectExplanation": "Heteroskedasticity, overlap and non-normality affect the standard errors, not the consistency of OLS; attenuation comes from error in the regressor."
            },
            "ro": {
                "title": "Erori în variabile",
                "text": "De ce poate OLS în RV = alpha + beta VIX^2 + e să subestimeze beta?",
                "options": [
                    "Erorile heteroscedastice deplasează panta OLS spre 0",
                    "Ferestrele suprapuse de 21 de zile deplasează panta OLS",
                    "VIX^2 măsoară cu eroare varianța așteptată adevărată, ceea ce atenuează panta; instrumentarea cu VIX^2 întîrziat corectează acest lucru",
                    "Reziduurile care nu urmează distribuția Normală deplasează panta OLS"
                ],
                "correctExplanation": "Eroarea clasică de măsurare într-un regresor deplasează OLS spre 0 (Christensen și Prabhala, 1998); o valoare întîrziată este un instrument valid dacă eroarea ei este necorelată cu cea de azi. În datele cursului corecția este mică: 1,06 (OLS) și 1,02 (instrumente), în logaritmi.",
                "incorrectExplanation": "Heteroscedasticitatea, suprapunerea și abaterile de la distribuția Normală afectează erorile standard, nu consistența OLS; atenuarea vine din eroarea din regresor."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Equity skew",
                "text": "Why are low-strike puts on stock indices more expensive in implied-volatility terms than at-the-money options?",
                "options": [
                    "Fat left tails, volatility rising when prices fall, and demand for crash insurance",
                    "Because puts always cost more than calls",
                    "Because of the interest rate",
                    "Because Black-Scholes assumes negative skewness"
                ],
                "correctExplanation": "Heavy left tails, the leverage effect and the premium for crash risk all raise the price of low-strike puts.",
                "incorrectExplanation": "The skew is not a feature of Black-Scholes, which implies a flat smile; it comes from the return distribution and from risk premia."
            },
            "ro": {
                "title": "Asimetria acțiunilor",
                "text": "De ce put-urile cu preț de exercitare mic pe indici bursieri sînt mai scumpe, în volatilitate implicită, decît opțiunile la bani?",
                "options": [
                    "Cozi stîngi groase, volatilitate care crește cînd prețurile scad și cererea de asigurare împotriva crahurilor",
                    "Pentru că put-urile costă întotdeauna mai mult decît call-urile",
                    "Din cauza ratei dobînzii",
                    "Pentru că Black-Scholes presupune asimetrie negativă"
                ],
                "correctExplanation": "Cozile stîngi grele, efectul de levier și prima pentru riscul de crah ridică toate prețul put-urilor cu preț de exercitare mic.",
                "incorrectExplanation": "Asimetria nu este o proprietate a modelului Black-Scholes, care implică un zîmbet plat; ea vine din distribuția randamentelor și din primele de risc."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Where the hedging P&L comes from",
                "text": "A delta-hedged long option earns (1/2) Gamma S^2 (sigma_real^2 - sigma_imp^2) dt. Where is its P&L concentrated?",
                "options": [
                    "Near the strike and near expiry, where gamma is large, so the price path matters and not only total realised variance",
                    "It depends only on total realised variance over the life, like a variance swap",
                    "It depends only on the drift mu of the underlying",
                    "Only on the expiry date"
                ],
                "correctExplanation": "The variance difference is weighted by Gamma S^2, which peaks at the money and near expiry; a variance swap has constant weights, a delta-hedged option random ones.",
                "incorrectExplanation": "The drift drops out of the hedged P&L; what remains is the variance gap weighted by gamma along the path."
            },
            "ro": {
                "title": "De unde vine rezultatul hedging-ului",
                "text": "O opțiune cumpărată, cu delta hedging, cîștigă (1/2) Gamma S^2 (sigma_real^2 - sigma_imp^2) dt. Unde se concentrează rezultatul?",
                "options": [
                    "Aproape de prețul de exercitare și de scadență, unde gamma este mare, deci contează traiectoria prețului, nu doar varianța realizată totală",
                    "Depinde doar de varianța realizată totală pe durata opțiunii, ca un swap de varianță",
                    "Depinde doar de drift-ul mu al activului suport",
                    "Doar de data scadenței"
                ],
                "correctExplanation": "Diferența de varianță este ponderată cu Gamma S^2, maximă la bani și aproape de scadență; un swap de varianță are ponderi constante, o opțiune cu delta hedging are ponderi aleatoare.",
                "incorrectExplanation": "Drift-ul dispare din rezultatul cu hedging; rămîne diferența de varianță ponderată cu gamma de-a lungul traiectoriei."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Estimating the risk-neutral density",
                "text": "Why do risk-neutral densities obtained with Breeden-Litzenberger need smoothing and shape constraints?",
                "options": [
                    "Because index calls are American",
                    "Because the interest rate is not zero",
                    "Because the log-normal distribution is the true density",
                    "Because differentiating quotes twice amplifies their noise, and without convexity in K the estimated density can be negative"
                ],
                "correctExplanation": "q = e^{r tau} d^2C/dK^2 is an ill-posed inverse problem; in the lecture's Deribit chain 7 of 732 mark butterflies are negative, all within the bid-ask spread.",
                "incorrectExplanation": "The issue is statistical: a second derivative of noisy, discrete prices, which must be convex in the strike to give a non-negative density."
            },
            "ro": {
                "title": "Estimarea densității neutre la risc",
                "text": "De ce au nevoie densitățile neutre la risc obținute cu Breeden-Litzenberger de netezire și de constrîngeri de formă?",
                "options": [
                    "Pentru că opțiunile call pe indici sînt americane",
                    "Pentru că rata dobînzii nu este zero",
                    "Pentru că distribuția log-normală este densitatea adevărată",
                    "Pentru că derivarea de două ori a cotațiilor le amplifică zgomotul, iar fără convexitate în K densitatea estimată poate fi negativă"
                ],
                "correctExplanation": "q = e^{r tau} d^2C/dK^2 este o problemă inversă prost condiționată; în lanțul Deribit din curs 7 din 732 de fluturi de marcare sînt negativi, toți în interiorul spread-ului bid-ask.",
                "incorrectExplanation": "Problema este statistică: o derivată a doua a unor prețuri discrete și zgomotoase, care trebuie să fie convexe în prețul de exercitare pentru a da o densitate nenegativă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Overlapping predictive regressions",
                "text": "You regress 12-month excess returns on the monthly variance risk premium, sampled monthly, so the return windows overlap. Which standard errors?",
                "options": [
                    "White heteroskedasticity-robust (HC0) standard errors",
                    "Hodrick (1992) or Hansen-Hodrick standard errors, or Newey-West with at least h - 1 lags, plus a bootstrap for the bias of a persistent regressor",
                    "Standard errors clustered by calendar year",
                    "None needed: OLS is unbiased, so the usual standard errors are fine"
                ],
                "correctExplanation": "Overlap makes the errors MA(11); HC0 ignores it and overstates t. In the lecture no horizon of 1-12 months is significant on 1990-2026 with any of these corrections.",
                "incorrectExplanation": "Consecutive 12-month windows share 11 months, so the errors are autocorrelated; the correction must span the overlap, and a persistent predictor adds small-sample bias."
            },
            "ro": {
                "title": "Regresii predictive suprapuse",
                "text": "Regresați randamentele în exces pe 12 luni pe prima de risc a varianței lunară, eșantionate lunar, deci ferestrele de randament se suprapun. Ce erori standard folosiți?",
                "options": [
                    "Erori standard White robuste la heteroscedasticitate (HC0)",
                    "Erori standard Hodrick (1992) sau Hansen-Hodrick, ori Newey-West cu cel puțin h - 1 lag-uri, plus un bootstrap pentru deplasarea dată de un regresor persistent",
                    "Erori standard grupate pe ani calendaristici",
                    "Niciuna: OLS este nedeplasat, deci erorile standard obișnuite sînt suficiente"
                ],
                "correctExplanation": "Suprapunerea face erorile MA(11); HC0 o ignoră și supraestimează t. În curs niciun orizont de 1-12 luni nu este semnificativ pe 1990-2026, cu oricare dintre aceste corecții.",
                "incorrectExplanation": "Ferestrele consecutive de 12 luni au 11 luni în comun, deci erorile sînt autocorelate; corecția trebuie să acopere suprapunerea, iar un predictor persistent adaugă deplasare în eșantion mic."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Risk-neutral density",
                "text": "How is the risk-neutral density of S_T obtained from option prices (Breeden-Litzenberger)?",
                "options": [
                    "As e^{r tau} times the second derivative of call prices with respect to the strike",
                    "As the first derivative of the put price with respect to time",
                    "From the historical distribution of returns",
                    "As the ratio of call and put prices"
                ],
                "correctExplanation": "q(K) = e^{r tau} d2C/dK2: a narrow butterfly spread pays like a bet on S_T close to K.",
                "incorrectExplanation": "The density comes from the curvature of call prices in the strike; the historical distribution is the physical, not the risk-neutral one."
            },
            "ro": {
                "title": "Densitatea neutră la risc",
                "text": "Cum se obține densitatea neutră la risc a lui S_T din prețurile opțiunilor (Breeden-Litzenberger)?",
                "options": [
                    "Ca e^{r tau} înmulțit cu derivata a doua a prețurilor call în raport cu prețul de exercitare",
                    "Ca derivata întîi a prețului put în raport cu timpul",
                    "Din distribuția istorică a randamentelor",
                    "Ca raportul dintre prețurile call și put"
                ],
                "correctExplanation": "q(K) = e^{r tau} d2C/dK2: un spread fluture îngust plătește ca un pariu pe S_T aproape de K.",
                "incorrectExplanation": "Densitatea vine din curbura prețurilor call în prețul de exercitare; distribuția istorică este cea fizică, nu cea neutră la risc."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Bitcoin crash tail",
                "text": "For the Bitcoin expiry closest to 30 days, the SVI risk-neutral probability of a fall of more than 30% was 1.2% against 0.1% under the log-normal density. What does this show?",
                "options": [
                    "That the log-normal density overstates crash risk",
                    "That the market prices crash insurance far above what Black-Scholes with one volatility implies",
                    "That a crash will happen with probability 1.2%",
                    "That the SVI fit is wrong"
                ],
                "correctExplanation": "The tail of the risk-neutral density is several times heavier than the log-normal one: the crash tail is where Black-Scholes fails most.",
                "incorrectExplanation": "Risk-neutral probabilities are prices of insurance, not forecasts; the comparison shows how much heavier the priced tail is than the log-normal one."
            },
            "ro": {
                "title": "Coada de crah Bitcoin",
                "text": "Pentru scadența Bitcoin cea mai apropiată de 30 de zile, probabilitatea neutră la risc SVI a unei scăderi de peste 30% a fost 1,2% față de 0,1% sub densitatea log-normală. Ce arată acest lucru?",
                "options": [
                    "Că densitatea log-normală supraestimează riscul de crah",
                    "Că piața evaluează asigurarea împotriva crahului mult peste ce implică Black-Scholes cu o singură volatilitate",
                    "Că un crah va avea loc cu probabilitatea 1,2%",
                    "Că estimarea SVI este greșită"
                ],
                "correctExplanation": "Coada densității neutre la risc este de cîteva ori mai grea decît cea log-normală: coada crahurilor este locul unde Black-Scholes greșește cel mai mult.",
                "incorrectExplanation": "Probabilitățile neutre la risc sînt prețuri ale asigurării, nu prognoze; comparația arată cît de grea este coada evaluată față de cea log-normală."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The VIX formula",
                "text": "Since 2003, how is the VIX computed?",
                "options": [
                    "From the at-the-money implied volatility of S&P 100 options",
                    "From a GARCH model fitted to S&P 500 returns",
                    "From a strip of out-of-the-money S&P 500 options weighted by 1/K^2, interpolated to 30 days (an estimate of the variance-swap strike)",
                    "From VIX futures prices"
                ],
                "correctExplanation": "For each of two expiries around 30 days, sigma^2 = 2/T sum dK/K^2 e^{RT} Q(K) - (F/K0 - 1)^2/T; the total variances are interpolated to 30 days and VIX = 100 times the square root of the annualised result. The strip prices the log contract, so it equals the fair variance-swap strike only for continuous paths and a continuum of strikes.",
                "incorrectExplanation": "The original 1993 VIX used at-the-money S&P 100 options; the current VIX is a model-free variance measure from a strip of S&P 500 options."
            },
            "ro": {
                "title": "Formula VIX",
                "text": "Din 2003, cum se calculează VIX?",
                "options": [
                    "Din volatilitatea implicită la bani a opțiunilor pe S&P 100",
                    "Dintr-un model GARCH estimat pe randamentele S&P 500",
                    "Dintr-o bandă de opțiuni S&P 500 în afara banilor, ponderate cu 1/K^2, interpolată la 30 de zile (o estimare a prețului de exercitare al unui swap de varianță)",
                    "Din prețurile contractelor futures pe VIX"
                ],
                "correctExplanation": "Pentru fiecare dintre două scadențe din jurul a 30 de zile, sigma^2 = 2/T sum dK/K^2 e^{RT} Q(K) - (F/K0 - 1)^2/T; varianțele totale se interpolează la 30 de zile, iar VIX = de 100 de ori rădăcina pătrată a rezultatului anualizat. Banda evaluează contractul logaritmic, deci este egală cu prețul corect al swap-ului de varianță doar pentru traiectorii continue și un continuum de prețuri de exercitare.",
                "incorrectExplanation": "VIX-ul original din 1993 folosea opțiuni la bani pe S&P 100; VIX-ul actual este o măsură a varianței fără model, dintr-o bandă de opțiuni pe S&P 500."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "VIX term structure",
                "text": "The VIX was above the VIX3M (backwardation) on 7.6% of days since 2011. When does this happen?",
                "options": [
                    "In calm bull markets",
                    "At random, with no link to market conditions",
                    "Only on option expiry days",
                    "In crises, when fear is concentrated in the near term"
                ],
                "correctExplanation": "Backwardation marks stress; in the following 21 days realised volatility averaged 26.7% against 13.6% in contango.",
                "incorrectExplanation": "Normally the term structure slopes upwards (contango); it inverts in crises, when short-term uncertainty dominates."
            },
            "ro": {
                "title": "Structura la termen a VIX",
                "text": "VIX a fost peste VIX3M (backwardation) în 7,6% din zile, din 2011. Cînd se întîmplă acest lucru?",
                "options": [
                    "În piețe calme, în creștere",
                    "Aleatoriu, fără legătură cu condițiile de piață",
                    "Doar în zilele de scadență a opțiunilor",
                    "În crize, cînd frica se concentrează pe termen scurt"
                ],
                "correctExplanation": "Backwardation semnalează stresul; în următoarele 21 de zile volatilitatea realizată a fost în medie 26,7% față de 13,6% în contango.",
                "incorrectExplanation": "De obicei structura la termen este crescătoare (contango); se inversează în crize, cînd domină incertitudinea pe termen scurt."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Variance risk premium",
                "text": "Over 1990-2026 the mean VIX was 19.4 and the mean realised volatility over the following 21 days 15.3. What is the variance risk premium?",
                "options": [
                    "Implied variance minus the variance realised afterwards; positive on average, negative in crashes",
                    "Realised variance minus implied variance; always positive",
                    "The difference between the VIX and VVIX",
                    "The premium of an at-the-money call"
                ],
                "correctExplanation": "VRP = VIX^2 - RV: positive on 86% of days, about 4.1 volatility points on average, with large negative values in crashes.",
                "incorrectExplanation": "The premium is implied minus realised variance: buyers of variance pay it as insurance against turbulence."
            },
            "ro": {
                "title": "Prima de risc a varianței",
                "text": "În 1990-2026 media VIX a fost 19,4, iar media volatilității realizate în următoarele 21 de zile 15,3. Ce este prima de risc a varianței?",
                "options": [
                    "Varianța implicită minus varianța realizată ulterior; pozitivă în medie, negativă în crahuri",
                    "Varianța realizată minus varianța implicită; mereu pozitivă",
                    "Diferența dintre VIX și VVIX",
                    "Prima unui call la bani"
                ],
                "correctExplanation": "VRP = VIX^2 - RV: pozitivă în 86% din zile, în medie aproximativ 4,1 puncte de volatilitate, cu valori negative mari în crahuri.",
                "incorrectExplanation": "Prima este varianța implicită minus cea realizată: cumpărătorii de varianță o plătesc ca asigurare împotriva turbulențelor."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Overlapping windows",
                "text": "Why are Newey-West standard errors needed when averaging the daily variance risk premium?",
                "options": [
                    "Because the premium follows the Normal distribution",
                    "Because consecutive 21-day windows share 20 days, so the daily values are strongly autocorrelated",
                    "Because the VIX is measured with rounding error",
                    "Because the sample is too small"
                ],
                "correctExplanation": "Overlapping windows make the naive standard error several times too small; Newey-West with 21 lags corrects it.",
                "incorrectExplanation": "The issue is autocorrelation from overlapping windows, which the naive formula ignores."
            },
            "ro": {
                "title": "Ferestre suprapuse",
                "text": "De ce sînt necesare erori standard Newey-West cînd mediem prima zilnică de risc a varianței?",
                "options": [
                    "Pentru că prima urmează distribuția Normală",
                    "Pentru că ferestrele consecutive de 21 de zile au în comun 20 de zile, deci valorile zilnice sînt puternic autocorelate",
                    "Pentru că VIX este măsurat cu erori de rotunjire",
                    "Pentru că eșantionul este prea mic"
                ],
                "correctExplanation": "Ferestrele suprapuse fac eroarea standard naivă de cîteva ori prea mică; Newey-West cu 21 de lag-uri o corectează.",
                "incorrectExplanation": "Problema este autocorelația dată de ferestrele suprapuse, pe care formula naivă o ignoră."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Is the VIX unbiased?",
                "text": "Regressing 21-day realised variance on VIX^2 gave a slope of 0.86 and a negative intercept. What does this say?",
                "options": [
                    "The VIX is an unbiased forecast",
                    "The VIX underestimates future volatility",
                    "The VIX is too high on average, most of all when it is high: it contains a risk premium",
                    "The VIX has no information about future volatility"
                ],
                "correctExplanation": "An unbiased forecast needs intercept 0 and slope 1; neither t-statistic alone rejects, but the joint Wald test does (41.7, p below 10^-9): the VIX overstates realised variance, yet explains more (R^2 0.37) than past variance (0.29).",
                "incorrectExplanation": "The regression shows an upward bias from the risk premium, but the VIX remains informative about future volatility."
            },
            "ro": {
                "title": "Este VIX nedeplasat?",
                "text": "Regresia varianței realizate pe 21 de zile pe VIX^2 a dat o pantă de 0,86 și un termen liber negativ. Ce spune acest lucru?",
                "options": [
                    "VIX este o prognoză nedeplasată",
                    "VIX subestimează volatilitatea viitoare",
                    "VIX este prea mare în medie, cel mai mult cînd este mare: conține o primă de risc",
                    "VIX nu conține informație despre volatilitatea viitoare"
                ],
                "correctExplanation": "O prognoză nedeplasată cere termen liber 0 și pantă 1; nicio statistică t separată nu respinge, dar testul Wald comun respinge (41,7, p sub 10^-9): VIX supraestimează varianța realizată, dar explică mai mult (R^2 0,37) decît varianța trecută (0,29).",
                "incorrectExplanation": "Regresia arată o deplasare în sus dată de prima de risc, dar VIX rămîne informativ pentru volatilitatea viitoare."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Ex-ante and ex-post variance premium",
                "text": "What distinguishes the ex-ante from the ex-post variance risk premium?",
                "options": [
                    "They are the same quantity measured in different units",
                    "The ex-post premium uses past realised variance, the ex-ante premium future realised variance",
                    "The ex-ante premium E^Q_t[RV] - E^P_t[RV], proxied by VIX^2 minus past realised variance, is known at t and can serve as a predictor; the ex-post premium uses future realised variance and is the realised P&L of a variance swap",
                    "Only the ex-post premium can be tested with Newey-West errors"
                ],
                "correctExplanation": "A predictor must be known at the forecast date; VIX_t^2 - RV_{t,t+21} is known only at t+21 and measures what a variance-swap seller earned, not what an investor could see. Past realised variance is only a forecast of E^P_t[RV], so VIX_t^2 - RV_{t-21,t} is a proxy for the ex-ante premium.",
                "incorrectExplanation": "The two differ in timing: the ex-post version subtracts variance realised after t, so it cannot be used as a predictor at t."
            },
            "ro": {
                "title": "Prima de varianță ex ante și ex post",
                "text": "Ce deosebește prima de risc a varianței ex ante de cea ex post?",
                "options": [
                    "Sînt aceeași mărime, măsurată în unități diferite",
                    "Prima ex post folosește varianța realizată trecută, cea ex ante varianța realizată viitoare",
                    "Prima ex ante E^Q_t[RV] - E^P_t[RV], aproximată prin VIX^2 minus varianța realizată trecută, este cunoscută la t și poate fi folosită ca predictor; prima ex post folosește varianța realizată viitoare și este rezultatul realizat al unui swap de varianță",
                    "Doar prima ex post poate fi testată cu erori Newey-West"
                ],
                "correctExplanation": "Un predictor trebuie să fie cunoscut la data prognozei; VIX_t^2 - RV_{t,t+21} este cunoscută abia la t+21 și măsoară ce a cîștigat vînzătorul unui swap de varianță, nu ce putea vedea un investitor. Varianța realizată trecută este doar o prognoză pentru E^P_t[RV], deci VIX_t^2 - RV_{t-21,t} este o aproximare a primei ex ante.",
                "incorrectExplanation": "Cele două diferă prin moment: versiunea ex post scade varianța realizată după t, deci nu poate fi folosită ca predictor la t."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Bitcoin variance premium",
                "text": "For Bitcoin (2021-2026) the mean DVOL was 60.3 and the mean realised volatility over the next 30 days 51.7. Which statement is right?",
                "options": [
                    "Bitcoin option sellers also earned a premium on average, but with long episodes of negative premium",
                    "Bitcoin options are always cheap relative to realised volatility",
                    "The premium is exactly the same as for the S&P 500 in volatility points",
                    "DVOL is not related to option prices"
                ],
                "correctExplanation": "The premium was about 8.5 volatility points, positive on 71% of days: larger in points than for the S&P 500, but less regular.",
                "incorrectExplanation": "DVOL is built from Bitcoin option prices; it exceeded realised volatility on average, though less consistently than the VIX."
            },
            "ro": {
                "title": "Prima de varianță Bitcoin",
                "text": "Pentru Bitcoin (2021-2026) media DVOL a fost 60,3, iar media volatilității realizate în următoarele 30 de zile 51,7. Ce afirmație este corectă?",
                "options": [
                    "Și vînzătorii de opțiuni Bitcoin au cîștigat în medie o primă, dar cu episoade lungi de primă negativă",
                    "Opțiunile Bitcoin sînt mereu ieftine față de volatilitatea realizată",
                    "Prima este exact aceeași ca pentru S&P 500 în puncte de volatilitate",
                    "DVOL nu are legătură cu prețurile opțiunilor"
                ],
                "correctExplanation": "Prima a fost de aproximativ 8,5 puncte de volatilitate, pozitivă în 71% din zile: mai mare în puncte decît pentru S&P 500, dar mai puțin regulată.",
                "incorrectExplanation": "DVOL este construit din prețurile opțiunilor Bitcoin; a depășit în medie volatilitatea realizată, deși mai puțin constant decît VIX."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Variance swap",
                "text": "What does the seller of a variance swap receive and pay?",
                "options": [
                    "Receives the realised variance, pays a fixed strike",
                    "Receives a fixed strike (implied variance), pays the realised variance: small gains most months, large losses in crashes",
                    "Receives the VIX level in points, pays nothing",
                    "Receives dividends of the index"
                ],
                "correctExplanation": "The pay-off is notional times (strike minus realised variance) for the seller; realised variance explodes in crashes, so losses are convex.",
                "incorrectExplanation": "The seller of variance is short volatility insurance: the strike is fixed at the start, the realised variance is paid at the end."
            },
            "ro": {
                "title": "Swap-ul de varianță",
                "text": "Ce încasează și ce plătește vînzătorul unui swap de varianță?",
                "options": [
                    "Încasează varianța realizată, plătește un preț de exercitare fix",
                    "Încasează un preț de exercitare fix (varianța implicită), plătește varianța realizată: cîștiguri mici în majoritatea lunilor, pierderi mari în crahuri",
                    "Încasează nivelul VIX în puncte, nu plătește nimic",
                    "Încasează dividendele indicelui"
                ],
                "correctExplanation": "Plata pentru vînzător este notional înmulțit cu (prețul de exercitare minus varianța realizată); varianța realizată explodează în crahuri, deci pierderile sînt convexe.",
                "incorrectExplanation": "Vînzătorul de varianță a vîndut o asigurare împotriva volatilității: prețul de exercitare se fixează la început, varianța realizată se plătește la final."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: time to maturity",
                "text": "An AI assistant writes: \"For a 30-day at-the-money call, plug T = 30 into the Black-Scholes formula, with sigma = 0.20 and r = 0.04 per year.\" What is wrong?",
                "options": [
                    "T must be in years, T = 30/365 = 0.082, because sigma and r are annual",
                    "sigma must be entered as 20, not 0.20",
                    "r must be converted to a daily rate, not T",
                    "Black-Scholes cannot price at-the-money options"
                ],
                "correctExplanation": "sigma and r are per year, so time must be in years too; with T = 30 the call is priced as if it had 30 years to run.",
                "incorrectExplanation": "Check the units: every input to Black-Scholes must use the same time unit, and volatility enters as a decimal."
            },
            "ro": {
                "title": "Găsiți eroarea AI: scadența",
                "text": "Un asistent AI scrie: „Pentru un call la bani pe 30 de zile, puneți T = 30 în formula Black-Scholes, cu sigma = 0,20 și r = 0,04 pe an.” Ce este greșit?",
                "options": [
                    "T trebuie exprimat în ani, T = 30/365 = 0,082, pentru că sigma și r sînt anuale",
                    "sigma trebuie introdus ca 20, nu 0,20",
                    "r trebuie transformat într-o rată zilnică, nu T",
                    "Black-Scholes nu poate evalua opțiuni la bani"
                ],
                "correctExplanation": "sigma și r sînt pe an, deci și timpul trebuie exprimat în ani; cu T = 30, call-ul este evaluat ca și cum ar avea 30 de ani pînă la scadență.",
                "incorrectExplanation": "Verificați unitățile: toate datele de intrare Black-Scholes trebuie să folosească aceeași unitate de timp, iar volatilitatea intră ca număr zecimal."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: put-call parity",
                "text": "An AI assistant writes: \"By put-call parity, P = C + S - K e^{-r tau}. With C = 4, S = 100, K = 105 and r = 0, the put is worth -1: buy it and get paid.\" What is wrong?",
                "options": [
                    "Nothing: negative put prices are possible when rates are zero",
                    "The sign is wrong: P = C - S + K e^{-r tau} = 4 - 100 + 105 = 9",
                    "Parity holds only for American options",
                    "With r = 0 calls and puts have the same price, so the put is worth 4"
                ],
                "correctExplanation": "From C - P = S - K e^{-r tau}, the put is C - S + K e^{-r tau}; a negative option price is impossible, which flags the error at once.",
                "incorrectExplanation": "Rewrite C - P = S - K e^{-r tau} for P and check the no-arbitrage bound: a put can never have a negative price."
            },
            "ro": {
                "title": "Găsiți eroarea AI: paritatea put-call",
                "text": "Un asistent AI scrie: „Din paritatea put-call, P = C + S - K e^{-r tau}. Cu C = 4, S = 100, K = 105 și r = 0, put-ul valorează -1: îl cumpărați și sînteți plătiți.” Ce este greșit?",
                "options": [
                    "Nimic: prețurile negative ale put-urilor sînt posibile cînd ratele sînt zero",
                    "Semnul este greșit: P = C - S + K e^{-r tau} = 4 - 100 + 105 = 9",
                    "Paritatea este valabilă doar pentru opțiuni americane",
                    "Cu r = 0, call-urile și put-urile au același preț, deci put-ul valorează 4"
                ],
                "correctExplanation": "Din C - P = S - K e^{-r tau}, put-ul este C - S + K e^{-r tau}; un preț negativ al unei opțiuni este imposibil, ceea ce semnalează imediat eroarea.",
                "incorrectExplanation": "Scrieți C - P = S - K e^{-r tau} în funcție de P și verificați limita de non-arbitraj: un put nu poate avea niciodată preț negativ."
            }
        }
    ]
};

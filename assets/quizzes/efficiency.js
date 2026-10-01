// ============================================================
// Quiz bank for chapter id 'efficiency': Market Efficiency, from EMH to Adaptive Markets (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['efficiency'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "BDS and weak-form efficiency",
                "text": "The BDS test rejects i.i.d. for daily S&P 500 returns. Does this reject weak-form efficiency, as tested through RW3 or the martingale difference hypothesis?",
                "options": [
                    "Yes, because BDS tests the martingale property",
                    "Yes, as long as the p-value is below 0.01",
                    "No: volatility clustering alone (e.g. GARCH) makes BDS reject, and RW3 allows it",
                    "No, because BDS can only be applied to prices"
                ],
                "correctExplanation": "BDS tests independence and identical distribution. A GARCH process with unpredictable mean rejects BDS but satisfies RW3 and the martingale difference hypothesis.",
                "incorrectExplanation": "BDS is a test of i.i.d. (RW1). The martingale difference hypothesis restricts only the conditional mean and RW3 only the autocorrelations, so predictable volatility is enough for a BDS rejection without any inefficiency."
            },
            "ro": {
                "title": "BDS și eficiența slabă",
                "text": "Testul BDS respinge ipoteza i.i.d. pentru randamentele zilnice S&P 500. Respinge aceasta eficiența slabă, testată prin RW3 sau prin ipoteza diferenței de martingală?",
                "options": [
                    "Da, pentru că BDS testează proprietatea de martingală",
                    "Da, dacă valoarea p este sub 0,01",
                    "Nu: gruparea volatilității singură (de ex. GARCH) face BDS să respingă, iar RW3 o permite",
                    "Nu, pentru că BDS se aplică doar prețurilor"
                ],
                "correctExplanation": "BDS testează independența și distribuția identică. Un proces GARCH cu medie imprevizibilă respinge BDS, dar satisface RW3 și ipoteza diferenței de martingală.",
                "incorrectExplanation": "BDS este un test al ipotezei i.i.d. (RW1). Ipoteza diferenței de martingală restricționează doar media condiționată, iar RW3 doar autocorelațiile, deci volatilitatea predictibilă este suficientă pentru o respingere BDS fără nicio ineficiență."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Joint-hypothesis problem",
                "text": "Why can a test of market efficiency never reject efficiency alone?",
                "options": [
                    "Because returns are always normally distributed",
                    "Because efficiency is defined only for developed markets",
                    "Because it also needs a model of expected (fair) returns, so a rejection may reflect a wrong risk model",
                    "Because statistical tests have no power"
                ],
                "correctExplanation": "Fama (1991): abnormal returns are measured against a model of expected returns, so every efficiency test is a joint test of efficiency and of that model.",
                "incorrectExplanation": "A rejection can mean an inefficient market or a wrong asset-pricing model: this is the joint-hypothesis problem."
            },
            "ro": {
                "title": "Problema ipotezei comune",
                "text": "De ce un test al eficienței pieței nu poate respinge niciodată doar eficiența?",
                "options": [
                    "Pentru că randamentele urmează mereu distribuția Normală",
                    "Pentru că eficiența este definită doar pentru piețele dezvoltate",
                    "Pentru că are nevoie și de un model al randamentelor așteptate, deci o respingere poate proveni dintr-un model de risc greșit",
                    "Pentru că testele statistice nu au putere"
                ],
                "correctExplanation": "Fama (1991): randamentele anormale se măsoară față de un model al randamentelor așteptate, deci orice test de eficiență este un test comun al eficienței și al modelului.",
                "incorrectExplanation": "O respingere poate însemna o piață ineficientă sau un model de evaluare greșit: aceasta este problema ipotezei comune."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Martingale and volatility",
                "text": "If excess returns form a fair game (martingale difference), which statement is true?",
                "options": [
                    "Returns are uncorrelated with the past, but their volatility may still be predictable",
                    "Returns must be independent and identically distributed",
                    "Squared returns must be uncorrelated",
                    "Volatility must be constant over time"
                ],
                "correctExplanation": "A martingale restricts only the conditional mean; volatility clustering (predictable variance) is compatible with efficiency.",
                "incorrectExplanation": "The fair-game property restricts only the conditional mean; with finite variance it implies zero autocorrelations (RW3), but RW3 does not imply it. Volatility may still be predictable."
            },
            "ro": {
                "title": "Martingala și volatilitatea",
                "text": "Dacă randamentele în exces formează un joc echitabil (diferență de martingală), ce afirmație este adevărată?",
                "options": [
                    "Randamentele sînt necorelate cu trecutul, dar volatilitatea lor poate fi totuși predictibilă",
                    "Randamentele trebuie să fie independente și identic distribuite",
                    "Pătratele randamentelor trebuie să fie necorelate",
                    "Volatilitatea trebuie să fie constantă în timp"
                ],
                "correctExplanation": "Martingala restricționează doar media condiționată; gruparea volatilității (dispersie predictibilă) este compatibilă cu eficiența.",
                "incorrectExplanation": "Proprietatea de joc echitabil restricționează doar media condiționată; cu dispersie finită implică autocorelații nule (RW3), dar RW3 nu o implică. Volatilitatea poate fi totuși predictibilă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Grossman–Stiglitz",
                "text": "What does the Grossman–Stiglitz paradox imply?",
                "options": [
                    "Markets are always perfectly efficient",
                    "Some inefficiency must remain, just enough to pay informed traders for costly information",
                    "Prices never reflect private information",
                    "Arbitrage is free and riskless"
                ],
                "correctExplanation": "If prices reflected all information, nobody would pay to collect it; an equilibrium degree of inefficiency rewards information gathering.",
                "incorrectExplanation": "Costly information implies an equilibrium degree of inefficiency, not perfect efficiency."
            },
            "ro": {
                "title": "Grossman–Stiglitz",
                "text": "Ce implică paradoxul Grossman–Stiglitz?",
                "options": [
                    "Piețele sînt întotdeauna perfect eficiente",
                    "Trebuie să rămînă o anumită ineficiență, suficientă cît să plătească traderii informați pentru informația costisitoare",
                    "Prețurile nu reflectă niciodată informația privată",
                    "Arbitrajul este gratuit și fără risc"
                ],
                "correctExplanation": "Dacă prețurile ar reflecta toată informația, nimeni nu ar plăti pentru a o colecta; un grad de ineficiență de echilibru răsplătește colectarea informației.",
                "incorrectExplanation": "Informația costisitoare implică un grad de ineficiență de echilibru, nu eficiență perfectă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Robust standard error of autocorrelation",
                "text": "For the S&P 500 (2000–2026), the i.i.d. standard error of the lag-1 autocorrelation is 0.012 and the robust one is 0.027. Why is the robust one larger?",
                "options": [
                    "Because the sample is too short",
                    "Because the mean return is positive",
                    "Because large moves cluster in time, which inflates the sampling variance of the autocorrelation",
                    "Because the S&P 500 is a price index"
                ],
                "correctExplanation": "With volatility clustering, the variance of the sample autocorrelation is the sum of e_t² e_{t-1}² over the squared sum of squares, which exceeds 1/T.",
                "incorrectExplanation": "Volatility clustering, not the sample length or the mean, makes the robust standard error larger than 1/√T."
            },
            "ro": {
                "title": "Eroarea standard robustă a autocorelației",
                "text": "Pentru S&P 500 (2000–2026), eroarea standard i.i.d. a autocorelației de ordinul 1 este 0,012, iar cea robustă 0,027. De ce este cea robustă mai mare?",
                "options": [
                    "Pentru că selecția este prea scurtă",
                    "Pentru că randamentul mediu este pozitiv",
                    "Pentru că mișcările mari se grupează în timp, ceea ce mărește dispersia de selecție a autocorelației",
                    "Pentru că S&P 500 este un indice de preț"
                ],
                "correctExplanation": "Cu grupare a volatilității, dispersia autocorelației de selecție este suma lui e_t² e_{t-1}² împărțită la pătratul sumei pătratelor, care depășește 1/T.",
                "incorrectExplanation": "Gruparea volatilității, nu lungimea selecției sau media, face ca eroarea standard robustă să fie mai mare decît 1/√T."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Null distribution of the variance ratio",
                "text": "Under RW1, T = 6 714 daily returns and the estimated VR(2) = 0.901. What is the homoskedastic z statistic, approximately?",
                "options": [
                    "−8.1, because the asymptotic variance of √T(VR(2) − 1) equals 1",
                    "−0.099, the distance of VR(2) from one",
                    "−2.8, the robust z*(5) of the lecture",
                    "−0.012, the distance divided by √T"
                ],
                "correctExplanation": "For q = 2 the variance 2(2q − 1)(q − 1)/(3q) equals 1, so z(2) = √6714 × (0.901 − 1) ≈ 81.9 × (−0.099) ≈ −8.1.",
                "incorrectExplanation": "By the delta method √T(VR(q) − 1) → N(0, 2(2q − 1)(q − 1)/(3q)) under RW1; for q = 2 this variance is 1, so z(2) = √T(VR(2) − 1)."
            },
            "ro": {
                "title": "Distribuția nulă a raportului dispersiilor",
                "text": "Sub RW1, T = 6 714 randamente zilnice și VR(2) estimat = 0,901. Cît este aproximativ statistica z omoscedastică?",
                "options": [
                    "−8,1, pentru că dispersia asimptotică a lui √T(VR(2) − 1) este 1",
                    "−0,099, distanța lui VR(2) față de unu",
                    "−2,8, z*(5) robust din curs",
                    "−0,012, distanța împărțită la √T"
                ],
                "correctExplanation": "Pentru q = 2 dispersia 2(2q − 1)(q − 1)/(3q) este 1, deci z(2) = √6714 × (0,901 − 1) ≈ 81,9 × (−0,099) ≈ −8,1.",
                "incorrectExplanation": "Prin metoda delta √T(VR(q) − 1) → N(0, 2(2q − 1)(q − 1)/(3q)) sub RW1; pentru q = 2 această dispersie este 1, deci z(2) = √T(VR(2) − 1)."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Hurst exponent of a short-memory process",
                "text": "For an AR(1) with ρ = −0.1, what does the implied Hurst exponent H(q) = 0.5 + ln VR(q)/(2 ln q) tend to as q → ∞?",
                "options": [
                    "0.45, the value at q = 20",
                    "0, because the process is anti-persistent",
                    "It diverges to minus infinity",
                    "0.5, because VR(q) tends to the constant (1 + ρ)/(1 − ρ)"
                ],
                "correctExplanation": "For short memory with positive long-run variance VR(q) → 1 + 2Σρ_k = (1 + ρ)/(1 − ρ) ≈ 0.818, a positive constant, so ln VR(q)/(2 ln q) → 0 and H(q) → 0.5.",
                "incorrectExplanation": "VR(q) of a short-memory process with positive long-run variance, like this AR(1), converges to a positive constant, so the logarithm stays bounded while ln q grows: H(q) → 0.5. Values below 0.5 at finite q reflect short-run reversal, not long memory."
            },
            "ro": {
                "title": "Exponentul Hurst al unui proces cu memorie scurtă",
                "text": "Pentru un AR(1) cu ρ = −0,1, către ce tinde exponentul Hurst implicat H(q) = 0,5 + ln VR(q)/(2 ln q) cînd q → ∞?",
                "options": [
                    "0,45, valoarea la q = 20",
                    "0, pentru că procesul este anti-persistent",
                    "Diverge spre minus infinit",
                    "0,5, pentru că VR(q) tinde la constanta (1 + ρ)/(1 − ρ)"
                ],
                "correctExplanation": "Pentru memorie scurtă cu dispersie pe termen lung pozitivă VR(q) → 1 + 2Σρ_k = (1 + ρ)/(1 − ρ) ≈ 0,818, o constantă pozitivă, deci ln VR(q)/(2 ln q) → 0 și H(q) → 0,5.",
                "incorrectExplanation": "VR(q) al unui proces cu memorie scurtă și dispersie pe termen lung pozitivă, precum acest AR(1), converge la o constantă pozitivă, deci logaritmul rămîne mărginit în timp ce ln q crește: H(q) → 0,5. Valorile sub 0,5 la q finit reflectă inversarea pe termen scurt, nu memoria lungă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "z versus z*",
                "text": "For the S&P 500, VR(2) gives z = −8.12 under homoskedasticity but z* = −3.64 with the robust statistic. What explains the gap?",
                "options": [
                    "A coding error",
                    "The homoskedastic statistic ignores volatility clustering and overstates the evidence",
                    "The robust statistic uses fewer observations",
                    "The robust statistic assumes normality"
                ],
                "correctExplanation": "Lo and MacKinlay’s z* uses the heteroskedasticity-consistent variance of the autocorrelations; with clustering the homoskedastic z is too large.",
                "incorrectExplanation": "The difference comes from volatility clustering: only z* is valid under RW3."
            },
            "ro": {
                "title": "z versus z*",
                "text": "Pentru S&P 500, VR(2) dă z = −8,12 sub omoscedasticitate, dar z* = −3,64 cu statistica robustă. Ce explică diferența?",
                "options": [
                    "O eroare de programare",
                    "Statistica omoscedastică ignoră gruparea volatilității și exagerează dovezile",
                    "Statistica robustă folosește mai puține observații",
                    "Statistica robustă presupune normalitate"
                ],
                "correctExplanation": "Statistica z* a lui Lo și MacKinlay folosește dispersia autocorelațiilor consistentă la heteroscedasticitate; cu grupare, z omoscedastic este prea mare.",
                "incorrectExplanation": "Diferența vine din gruparea volatilității: doar z* este valid sub RW3."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Chow–Denning",
                "text": "Why use the Chow–Denning test instead of four separate variance-ratio tests at q = 2, 5, 10, 20?",
                "options": [
                    "It is more powerful against every alternative",
                    "It does not need returns",
                    "It controls the overall size when several horizons are tested; the 5% critical value becomes 2.49",
                    "It removes volatility clustering"
                ],
                "correctExplanation": "Testing several horizons inflates the chance of a false rejection; the maximum |z*| is compared with the studentised maximum modulus critical value.",
                "incorrectExplanation": "The point is size control over multiple horizons, which raises the critical value from 1.96 to about 2.49 for four horizons."
            },
            "ro": {
                "title": "Chow–Denning",
                "text": "De ce folosim testul Chow–Denning în locul a patru teste separate ale raportului dispersiilor la q = 2, 5, 10, 20?",
                "options": [
                    "Este mai puternic împotriva oricărei alternative",
                    "Nu are nevoie de randamente",
                    "Controlează pragul global cînd se testează mai multe orizonturi; valoarea critică de 5% devine 2,49",
                    "Elimină gruparea volatilității"
                ],
                "correctExplanation": "Testarea mai multor orizonturi mărește șansa unei respingeri false; maximul |z*| se compară cu valoarea critică a modulului maxim studentizat.",
                "incorrectExplanation": "Scopul este controlul pragului pe mai multe orizonturi, care crește valoarea critică de la 1,96 la circa 2,49 pentru patru orizonturi."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Runs test",
                "text": "The BET index has a runs-test statistic z = −6.05. What does it mean?",
                "options": [
                    "Fewer runs than expected: signs persist (positive dependence of signs)",
                    "More runs than expected: frequent reversals",
                    "Returns are normally distributed",
                    "The test cannot be applied to indices"
                ],
                "correctExplanation": "Too few runs means long sequences of equal signs, i.e. persistence of signs, in line with BET’s positive lag-1 autocorrelation; the runs test concerns signs, not the size of returns.",
                "incorrectExplanation": "A negative z means too few runs, hence persistence of signs."
            },
            "ro": {
                "title": "Testul secvențelor",
                "text": "Indicele BET are statistica testului secvențelor z = −6,05. Ce înseamnă?",
                "options": [
                    "Mai puține secvențe decît ne-am aștepta: semnele persistă (dependență pozitivă a semnelor)",
                    "Mai multe secvențe decît ne-am aștepta: inversări frecvente",
                    "Randamentele urmează distribuția Normală",
                    "Testul nu se poate aplica indicilor"
                ],
                "correctExplanation": "Prea puține secvențe înseamnă șiruri lungi de semne egale, adică persistența semnelor, în acord cu autocorelația pozitivă de ordinul 1 a BET; testul privește semnele, nu mărimea randamentelor.",
                "incorrectExplanation": "Un z negativ înseamnă prea puține secvențe, deci persistența semnelor."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Precision of the local Whittle estimator",
                "text": "The local Whittle estimator of d = H − 0.5 uses m = 400 Fourier frequencies. What is its asymptotic standard error?",
                "options": [
                    "0.05 = 1/√m",
                    "0.025 = 1/(2√m)",
                    "0.0025 = 1/m",
                    "1/√T, as for an autocorrelation"
                ],
                "correctExplanation": "Robinson (1995): √m(d̂ − d) → N(0, 1/4), so SE = 1/(2√m) = 1/40 = 0.025, under Robinson’s regularity conditions (|d| < 1/2, m → ∞, m/T → 0); Gaussianity is not needed.",
                "incorrectExplanation": "The asymptotic variance of √m(d̂ − d) is 1/4, so the standard error is 1/(2√m); precision is driven by the number of frequencies m, not by T."
            },
            "ro": {
                "title": "Precizia estimatorului Whittle local",
                "text": "Estimatorul Whittle local al lui d = H − 0,5 folosește m = 400 de frecvențe Fourier. Care este eroarea lui standard asimptotică?",
                "options": [
                    "0,05 = 1/√m",
                    "0,025 = 1/(2√m)",
                    "0,0025 = 1/m",
                    "1/√T, ca pentru o autocorelație"
                ],
                "correctExplanation": "Robinson (1995): √m(d̂ − d) → N(0, 1/4), deci SE = 1/(2√m) = 1/40 = 0,025, în condițiile de regularitate ale lui Robinson (|d| < 1/2, m → ∞, m/T → 0); nu este necesară distribuția Normală.",
                "incorrectExplanation": "Dispersia asimptotică a lui √m(d̂ − d) este 1/4, deci eroarea standard este 1/(2√m); precizia depinde de numărul de frecvențe m, nu de T."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Anis–Lloyd correction",
                "text": "Why is the classical R/S Hurst estimate corrected with the Anis–Lloyd expectation?",
                "options": [
                    "To remove the mean return",
                    "Because the R/S-based slope (Hurst estimate) is biased upward over small windows, even for i.i.d. returns",
                    "To make the estimate robust to heavy tails",
                    "To annualise the estimate"
                ],
                "correctExplanation": "For the S&P 500 the raw estimate is 0.530 but the corrected one 0.486: the uncorrected slope overstates memory.",
                "incorrectExplanation": "The correction removes the small-sample upward bias of the R/S-based Hurst slope under i.i.d. returns."
            },
            "ro": {
                "title": "Corecția Anis–Lloyd",
                "text": "De ce estimarea Hurst R/S clasică se corectează cu așteptarea Anis–Lloyd?",
                "options": [
                    "Pentru a elimina randamentul mediu",
                    "Pentru că panta bazată pe R/S (estimarea Hurst) este deplasată în sus pe ferestre mici, chiar pentru randamente i.i.d.",
                    "Pentru a face estimarea robustă la cozi groase",
                    "Pentru a anualiza estimarea"
                ],
                "correctExplanation": "Pentru S&P 500 estimarea brută este 0,530, iar cea corectată 0,486: panta necorectată supraestimează memoria.",
                "incorrectExplanation": "Corecția elimină deplasarea în sus a pantei Hurst bazate pe R/S în selecții mici, sub randamente i.i.d."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Lo’s modified R/S",
                "text": "What problem does Lo’s (1991) modified R/S statistic solve?",
                "options": [
                    "Classical R/S confuses short-run autocorrelation with long memory",
                    "R/S cannot be computed for crypto-assets",
                    "R/S requires normally distributed returns",
                    "R/S ignores the sign of returns"
                ],
                "correctExplanation": "Lo replaces the standard deviation by a long-run (HAC) standard deviation, so short memory no longer mimics long memory; under short memory V lies in [0.809, 1.862] with 95% probability.",
                "incorrectExplanation": "The modified statistic makes the test robust to short-run dependence."
            },
            "ro": {
                "title": "R/S modificat al lui Lo",
                "text": "Ce problemă rezolvă statistica R/S modificată a lui Lo (1991)?",
                "options": [
                    "R/S clasic confundă autocorelația pe termen scurt cu memoria lungă",
                    "R/S nu poate fi calculat pentru cripto-active",
                    "R/S cere randamente cu distribuția Normală",
                    "R/S ignoră semnul randamentelor"
                ],
                "correctExplanation": "Lo înlocuiește abaterea standard cu o abatere standard de termen lung (HAC), astfel încît memoria scurtă nu mai imită memoria lungă; sub memorie scurtă V se află în [0,809; 1,862] cu probabilitate 95%.",
                "incorrectExplanation": "Statistica modificată face testul robust la dependența pe termen scurt."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "DFA and shuffling",
                "text": "The DFA exponent of BET (0.58) lies above the band of shuffled series. Why is this not yet proof of long memory in returns?",
                "options": [
                    "Because DFA only works for prices",
                    "Because the band is always too wide",
                    "Because shuffling destroys all dependence, including volatility clustering, which also raises the exponent",
                    "Because BET is not traded daily"
                ],
                "correctExplanation": "The shuffled band represents i.i.d. returns; any dependence, including in volatility, can push the exponent above it. Lo’s V is a complementary check.",
                "incorrectExplanation": "Shuffling removes every kind of dependence, so a value above the band may reflect volatility clustering rather than long memory in returns."
            },
            "ro": {
                "title": "DFA și amestecarea",
                "text": "Exponentul DFA al BET (0,58) se află peste banda seriilor amestecate. De ce nu este aceasta încă o dovadă de memorie lungă în randamente?",
                "options": [
                    "Pentru că DFA funcționează doar pentru prețuri",
                    "Pentru că banda este mereu prea largă",
                    "Pentru că amestecarea distruge toată dependența, inclusiv gruparea volatilității, care crește și ea exponentul",
                    "Pentru că BET nu se tranzacționează zilnic"
                ],
                "correctExplanation": "Banda obținută prin amestecare reprezintă randamente i.i.d.; orice dependență, inclusiv în volatilitate, poate împinge exponentul peste ea. V al lui Lo este o verificare complementară.",
                "incorrectExplanation": "Amestecarea elimină orice tip de dependență, deci o valoare peste bandă poate reflecta gruparea volatilității, nu memoria lungă în randamente."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Out-of-sample R²",
                "text": "A predictor has an in-sample R² of 2% but an out-of-sample R²_OS of −1.5% against the historical mean. What does this mean?",
                "options": [
                    "Its recursive forecasts have a larger mean squared error than the recursive historical mean",
                    "The in-sample R² was computed incorrectly",
                    "Returns are unpredictable even in sample",
                    "A negative R² can only come from a coding error"
                ],
                "correctExplanation": "R²_OS = 1 − Σ(r − r̂)²/Σ(r − r̄)² is negative when the model's forecasts lose to the historical mean out of sample, as for most predictors in Welch and Goyal (2008).",
                "incorrectExplanation": "R²_OS compares forecast errors with those of the historical mean; it can be negative, and it often is when estimation error and instability outweigh the in-sample fit."
            },
            "ro": {
                "title": "R² în afara selecției",
                "text": "Un predictor are R² în selecție de 2%, dar R²_OS în afara selecției de −1,5% față de media istorică. Ce înseamnă?",
                "options": [
                    "Prognozele lui recursive au o eroare pătratică medie mai mare decît media istorică recursivă",
                    "R² din selecție a fost calculat greșit",
                    "Randamentele sînt imprevizibile chiar și în selecție",
                    "Un R² negativ poate proveni doar dintr-o eroare de cod"
                ],
                "correctExplanation": "R²_OS = 1 − Σ(r − r̂)²/Σ(r − r̄)² este negativ cînd prognozele modelului pierd în fața mediei istorice în afara selecției, ca la majoritatea predictorilor din Welch și Goyal (2008).",
                "incorrectExplanation": "R²_OS compară erorile de prognoză cu cele ale mediei istorice; poate fi negativ și adesea este, cînd eroarea de estimare și instabilitatea depășesc potrivirea din selecție."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Reading rolling tests",
                "text": "On rolling windows, the S&P 500 rejects the random walk (|z*(5)| > 1.96) in 6.4% of windows. How should this be read?",
                "options": [
                    "As strong evidence of inefficiency in 6.4% of the years",
                    "As close to the 5% expected by chance, keeping in mind that overlapping windows are correlated",
                    "As proof that the S&P 500 is perfectly efficient",
                    "As a sign that the test has no power"
                ],
                "correctExplanation": "Under the null about 5% of windows reject by chance, and overlapping windows are not independent pieces of evidence.",
                "incorrectExplanation": "The share must be compared with the 5% chance level, and runs of rejections in overlapping windows are correlated."
            },
            "ro": {
                "title": "Citirea testelor pe ferestre mobile",
                "text": "Pe ferestre mobile, S&P 500 respinge mersul aleator (|z*(5)| > 1,96) în 6,4% din ferestre. Cum trebuie citit acest rezultat?",
                "options": [
                    "Ca dovadă puternică de ineficiență în 6,4% din ani",
                    "Ca fiind aproape de cei 5% așteptați din întîmplare, ținînd cont că ferestrele suprapuse sînt corelate",
                    "Ca dovadă că S&P 500 este perfect eficient",
                    "Ca semn că testul nu are putere"
                ],
                "correctExplanation": "Sub ipoteza nulă circa 5% din ferestre resping din întîmplare, iar ferestrele suprapuse nu sînt dovezi independente.",
                "incorrectExplanation": "Proporția trebuie comparată cu nivelul întîmplător de 5%, iar respingerile consecutive pe ferestre suprapuse sînt corelate."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Bitcoin efficiency",
                "text": "In the lecture, yearly robust tests on Bitcoin and Ethereum find only 1 of 27 lag-1 autocorrelations with |t| > 1.96, while Urquhart (2016) found Bitcoin inefficient in its early years. What is the lesson?",
                "options": [
                    "Conclusions about crypto efficiency depend on the test, the sample and the inference used",
                    "Urquhart made a computational mistake",
                    "Bitcoin was always perfectly efficient",
                    "Yearly tests are more powerful than full-sample tests"
                ],
                "correctExplanation": "Different test batteries, price sources and classical versus robust errors lead to different conclusions; one year of data also has low power.",
                "incorrectExplanation": "The contrast shows that efficiency results are test- and inference-dependent, not that one study is wrong."
            },
            "ro": {
                "title": "Eficiența Bitcoin",
                "text": "În curs, testele robuste anuale pe Bitcoin și Ethereum găsesc doar 1 din 27 autocorelații de ordinul 1 cu |t| > 1,96, în timp ce Urquhart (2016) a găsit Bitcoin ineficient în primii ani. Care este lecția?",
                "options": [
                    "Concluziile despre eficiența cripto depind de test, de selecție și de inferența folosită",
                    "Urquhart a făcut o greșeală de calcul",
                    "Bitcoin a fost întotdeauna perfect eficient",
                    "Testele anuale sînt mai puternice decît cele pe întreaga selecție"
                ],
                "correctExplanation": "Seturi de teste diferite, surse de prețuri diferite și erori clasice versus robuste duc la concluzii diferite; un singur an de date are și putere mică.",
                "incorrectExplanation": "Contrastul arată că rezultatele privind eficiența depind de test și de inferență, nu că un studiu este greșit."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Clustered event days",
                "text": "Two banks are hit by the same announcement on the same day. Why can a cross-sectional test that treats their abnormal returns as independent over-reject?",
                "options": [
                    "Because such tests need at least 30 firms",
                    "Because they ignore the estimation window",
                    "Because the abnormal returns are cross-correlated, so the variance of their average is understated",
                    "Because banks have betas above one"
                ],
                "correctExplanation": "With a common event date the residuals are correlated (r̄ > 0); the variance of the mean abnormal return is larger than σ²/N. Kolari and Pynnönen (2010) adjust for this; a portfolio test does it automatically.",
                "incorrectExplanation": "Cross-correlation of abnormal returns on a common event day inflates the variance of their average by (1 + (N − 1)r̄); ignoring it makes t too large."
            },
            "ro": {
                "title": "Zile de eveniment comune",
                "text": "Două bănci sînt afectate de același anunț, în aceeași zi. De ce poate un test transversal care tratează randamentele lor anormale ca independente să respingă prea des?",
                "options": [
                    "Pentru că astfel de teste cer cel puțin 30 de firme",
                    "Pentru că ignoră fereastra de estimare",
                    "Pentru că randamentele anormale sînt corelate transversal, deci dispersia mediei lor este subestimată",
                    "Pentru că băncile au beta peste unu"
                ],
                "correctExplanation": "Cu o dată comună a evenimentului reziduurile sînt corelate (r̄ > 0); dispersia randamentului anormal mediu este mai mare decît σ²/N. Kolari și Pynnönen (2010) corectează pentru aceasta; un test pe portofoliu o face automat.",
                "incorrectExplanation": "Corelația transversală a randamentelor anormale într-o zi comună umflă dispersia mediei lor cu (1 + (N − 1)r̄); ignorată, face t prea mare."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "HAC standard errors",
                "text": "Why are calendar-effect regressions estimated with Newey–West (HAC) standard errors?",
                "options": [
                    "To increase the R²",
                    "To remove outliers",
                    "To make the coefficients unbiased",
                    "Because residuals are heteroskedastic and autocorrelated, so OLS standard errors are invalid"
                ],
                "correctExplanation": "HAC standard errors remain valid under heteroskedasticity and autocorrelation; the coefficients themselves are unchanged.",
                "incorrectExplanation": "HAC changes only the standard errors, making inference valid when residuals are heteroskedastic and autocorrelated."
            },
            "ro": {
                "title": "Erori standard HAC",
                "text": "De ce regresiile pentru efectele de calendar se estimează cu erori standard Newey–West (HAC)?",
                "options": [
                    "Pentru a crește R²",
                    "Pentru a elimina valorile extreme",
                    "Pentru ca estimatorii coeficienților să fie nedeplasați",
                    "Pentru că reziduurile sînt heteroscedastice și autocorelate, deci erorile standard OLS nu sînt valide"
                ],
                "correctExplanation": "Erorile standard HAC rămîn valide sub heteroscedasticitate și autocorelație; coeficienții nu se schimbă.",
                "incorrectExplanation": "HAC schimbă doar erorile standard, făcînd inferența validă cînd reziduurile sînt heteroscedastice și autocorelate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Clark–West test",
                "text": "Why is the Diebold–Mariano test inappropriate for comparing a predictive regression with the historical mean (nested models)?",
                "options": [
                    "Because it requires Normal forecast errors",
                    "Because under the null the larger model estimates a zero slope, which inflates its MSPE, so the test is undersized; Clark–West corrects this",
                    "Because it needs non-overlapping samples",
                    "Because nested models always give identical forecasts"
                ],
                "correctExplanation": "Under H0 the extra parameter is pure estimation noise, adding (r̄ − r̂)² to the MSPE of the larger model; Clark and West (2007) add this term back and obtain an approximately Normal statistic.",
                "incorrectExplanation": "With nested models the larger model's MSPE is inflated by estimation noise under the null, so Diebold–Mariano rejects too rarely; the Clark–West adjustment removes this bias."
            },
            "ro": {
                "title": "Testul Clark–West",
                "text": "De ce testul Diebold–Mariano nu este potrivit pentru a compara o regresie predictivă cu media istorică (modele imbricate)?",
                "options": [
                    "Pentru că cere erori de prognoză din distribuția Normală",
                    "Pentru că sub ipoteza nulă modelul mai mare estimează o pantă nulă, ceea ce îi umflă MSPE, deci testul respinge prea rar; Clark–West corectează acest lucru",
                    "Pentru că cere selecții care nu se suprapun",
                    "Pentru că modelele imbricate dau mereu prognoze identice"
                ],
                "correctExplanation": "Sub H0 parametrul suplimentar este doar zgomot de estimare, care adaugă (r̄ − r̂)² la MSPE a modelului mai mare; Clark și West (2007) adaugă înapoi acest termen și obțin o statistică aproximativ Normală.",
                "incorrectExplanation": "La modelele imbricate MSPE a modelului mai mare este umflată de zgomotul de estimare sub ipoteza nulă, deci Diebold–Mariano respinge prea rar; ajustarea Clark–West elimină această deplasare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Anomalies by chance",
                "text": "In the lecture, 2000 meaningless random rules on the S&P 500 were tested. About how many were “significant” at 5%?",
                "options": [
                    "About 5%, as the test promises under the null",
                    "None, because the rules are random",
                    "About 50%",
                    "All of them, because the S&P 500 is inefficient"
                ],
                "correctExplanation": "About 4.9% had |t| > 1.96: trying many rules and reporting the best one always produces an apparent anomaly (data snooping).",
                "incorrectExplanation": "Under the null, roughly 5% of tests reject by chance; this is why multiple testing must be corrected."
            },
            "ro": {
                "title": "Anomalii din întîmplare",
                "text": "În curs au fost testate 2000 de reguli aleatoare fără sens pe S&P 500. Aproximativ cîte au fost „semnificative” la 5%?",
                "options": [
                    "Aproximativ 5%, cît promite testul sub ipoteza nulă",
                    "Niciuna, pentru că regulile sînt aleatoare",
                    "Aproximativ 50%",
                    "Toate, pentru că S&P 500 este ineficient"
                ],
                "correctExplanation": "Aproximativ 4,9% au avut |t| > 1,96: încercarea multor reguli și raportarea celei mai bune produce mereu o anomalie aparentă (data snooping).",
                "incorrectExplanation": "Sub ipoteza nulă, aproximativ 5% din teste resping din întîmplare; de aceea testarea multiplă trebuie corectată."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Stambaugh bias",
                "text": "A predictor is very persistent (ρ = 0.99) and its innovations are strongly negatively correlated with return innovations. In small samples the OLS slope of returns on the lagged predictor is…",
                "options": [
                    "Unbiased, because OLS is BLUE",
                    "Biased toward zero",
                    "Inconsistent",
                    "Biased upward"
                ],
                "correctExplanation": "E[β̂ − β] ≈ −(σ_uv/σ_v²)(1 + 3ρ)/T; with σ_uv < 0 the bias is positive, so predictability looks stronger than it is (Stambaugh, 1999).",
                "incorrectExplanation": "The regressor is predetermined, not strictly exogenous, so OLS is biased: the downward bias of ρ̂ passes to β̂ through the negative correlation of the innovations and pushes it upward."
            },
            "ro": {
                "title": "Deplasarea Stambaugh",
                "text": "Un predictor este foarte persistent (ρ = 0,99), iar inovațiile lui sînt puternic negativ corelate cu inovațiile randamentelor. În selecții mici, panta OLS a randamentelor pe predictorul decalat este…",
                "options": [
                    "Nedeplasată, pentru că OLS este BLUE",
                    "Deplasată spre zero",
                    "Inconsistentă",
                    "Deplasată în sus"
                ],
                "correctExplanation": "E[β̂ − β] ≈ −(σ_uv/σ_v²)(1 + 3ρ)/T; cu σ_uv < 0 deplasarea este pozitivă, deci predictibilitatea pare mai puternică decît este (Stambaugh, 1999).",
                "incorrectExplanation": "Regresorul este predeterminat, nu strict exogen, deci OLS este deplasat: deplasarea în jos a lui ρ̂ trece în β̂ prin corelația negativă a inovațiilor și îl împinge în sus."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Statistical versus economic significance",
                "text": "Time-series momentum on BET has a HAC t-statistic of 2.68, but its Sharpe ratio is 0.65 against 0.75 for buy-and-hold. What does this show?",
                "options": [
                    "BET is extremely inefficient",
                    "The t-statistic is wrong",
                    "Momentum always beats buy-and-hold",
                    "A statistically significant pattern need not add economic value over a simple benchmark"
                ],
                "correctExplanation": "Much of the momentum return is the equity premium earned while long; significance against zero is not significance against buy-and-hold.",
                "incorrectExplanation": "Statistical rejection is not the same as an exploitable improvement: compare with the relevant benchmark and costs."
            },
            "ro": {
                "title": "Semnificație statistică versus economică",
                "text": "Momentum-ul pe serii de timp pe BET are statistica t HAC egală cu 2,68, dar raportul Sharpe este 0,65 față de 0,75 pentru cumpără-și-păstrează. Ce arată acest lucru?",
                "options": [
                    "BET este extrem de ineficient",
                    "Statistica t este greșită",
                    "Momentum-ul bate întotdeauna strategia cumpără-și-păstrează",
                    "Un tipar semnificativ statistic nu adaugă neapărat valoare economică față de un reper simplu"
                ],
                "correctExplanation": "O mare parte din randamentul momentum este prima de risc a acțiunilor cîștigată pe pozițiile lungi; semnificația față de zero nu este semnificație față de cumpără-și-păstrează.",
                "incorrectExplanation": "Respingerea statistică nu este același lucru cu o îmbunătățire exploatabilă: comparați cu reperul potrivit și cu costurile."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: variance ratio and ρ₁",
                "text": "An AI assistant writes: \"VR(2) = 0.90. Since VR(2) = 1 + 2ρ₁, the first-order autocorrelation is ρ₁ = −0.05.\" What is wrong?",
                "options": [
                    "VR(q) = 1 + 2 Σ (1 − k/q) ρ_k, so VR(2) = 1 + ρ₁ and ρ₁ ≈ −0.10",
                    "VR(2) = 0.90 implies ρ₁ = +0.10",
                    "The variance ratio does not depend on autocorrelations",
                    "VR(2) = 1 + 4ρ₁, so ρ₁ = −0.025"
                ],
                "correctExplanation": "With q = 2 the only weight is 1 − 1/2, so VR(2) = 1 + 2 · ½ · ρ₁ = 1 + ρ₁ and ρ₁ ≈ 0.90 − 1 = −0.10.",
                "incorrectExplanation": "The weights (1 − k/q) are missing: with q = 2, VR(2) = 1 + ρ₁, so ρ₁ ≈ −0.10, twice the AI's value."
            },
            "ro": {
                "title": "Găsiți eroarea AI: raportul dispersiilor și ρ₁",
                "text": "Un asistent AI scrie: „VR(2) = 0,90. Deoarece VR(2) = 1 + 2ρ₁, autocorelația de ordinul întîi este ρ₁ = −0,05.” Ce este greșit?",
                "options": [
                    "VR(q) = 1 + 2 Σ (1 − k/q) ρ_k, deci VR(2) = 1 + ρ₁ și ρ₁ ≈ −0,10",
                    "VR(2) = 0,90 implică ρ₁ = +0,10",
                    "Raportul dispersiilor nu depinde de autocorelații",
                    "VR(2) = 1 + 4ρ₁, deci ρ₁ = −0,025"
                ],
                "correctExplanation": "Pentru q = 2 singura pondere este 1 − 1/2, deci VR(2) = 1 + 2 · ½ · ρ₁ = 1 + ρ₁ și ρ₁ ≈ 0,90 − 1 = −0,10.",
                "incorrectExplanation": "Lipsesc ponderile (1 − k/q): pentru q = 2, VR(2) = 1 + ρ₁, deci ρ₁ ≈ −0,10, dublul valorii date de AI."
            }
        }
    ]
};

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
            "correct": 1,
            "en": {
                "title": "Weak-form efficiency",
                "text": "Which information set defines weak-form market efficiency?",
                "options": [
                    "All public information, including company reports",
                    "Past prices and returns of the asset",
                    "Private information held by insiders",
                    "Forecasts published by central banks"
                ],
                "correctExplanation": "In the weak form, prices fully reflect the history of prices and returns, so past returns cannot predict future excess returns.",
                "incorrectExplanation": "Weak-form efficiency concerns only past prices and returns; public news defines the semi-strong form and insider information the strong form."
            },
            "ro": {
                "title": "Eficiența în formă slabă",
                "text": "Ce mulțime de informații definește eficiența pieței în formă slabă?",
                "options": [
                    "Toată informația publică, inclusiv raportările companiilor",
                    "Prețurile și randamentele trecute ale activului",
                    "Informația privată deținută de cei din interior",
                    "Prognozele publicate de băncile centrale"
                ],
                "correctExplanation": "În forma slabă, prețurile reflectă complet istoria prețurilor și a randamentelor, deci randamentele trecute nu pot prezice randamentele în exces viitoare.",
                "incorrectExplanation": "Eficiența slabă privește doar prețurile și randamentele trecute; știrile publice definesc forma semi-tare, iar informația din interior forma tare."
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
                "incorrectExplanation": "The fair-game property says nothing about the variance: RW3 allows volatility clustering, only the conditional mean is unpredictable."
            },
            "ro": {
                "title": "Martingala și volatilitatea",
                "text": "Dacă randamentele în exces formează un joc echitabil (diferență de martingală), ce afirmație este adevărată?",
                "options": [
                    "Randamentele sunt necorelate cu trecutul, dar volatilitatea lor poate fi totuși predictibilă",
                    "Randamentele trebuie să fie independente și identic distribuite",
                    "Pătratele randamentelor trebuie să fie necorelate",
                    "Volatilitatea trebuie să fie constantă în timp"
                ],
                "correctExplanation": "Martingala restricționează doar media condiționată; gruparea volatilității (dispersie predictibilă) este compatibilă cu eficiența.",
                "incorrectExplanation": "Proprietatea de joc echitabil nu spune nimic despre dispersie: RW3 permite gruparea volatilității, doar media condiționată este imprevizibilă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "RW1, RW2, RW3",
                "text": "Which random walk hypothesis is the relevant one to test on real daily returns?",
                "options": [
                    "RW1, because returns are i.i.d.",
                    "RW2, because returns are identically distributed",
                    "None, because prices are not random",
                    "RW3, uncorrelated increments with time-varying volatility allowed"
                ],
                "correctExplanation": "Volatility clustering already rejects RW1; RW3 (uncorrelated increments) is the hypothesis compatible with the stylised facts, tested with heteroskedasticity-robust statistics.",
                "incorrectExplanation": "RW1 is rejected by volatility clustering; the hypothesis worth testing is RW3, with robust inference."
            },
            "ro": {
                "title": "RW1, RW2, RW3",
                "text": "Care ipoteză de mers aleator este relevantă pentru testare pe randamente zilnice reale?",
                "options": [
                    "RW1, pentru că randamentele sunt i.i.d.",
                    "RW2, pentru că randamentele sunt identic distribuite",
                    "Niciuna, pentru că prețurile nu sunt aleatoare",
                    "RW3, creșteri necorelate, cu volatilitate variabilă în timp permisă"
                ],
                "correctExplanation": "Gruparea volatilității respinge deja RW1; RW3 (creșteri necorelate) este ipoteza compatibilă cu faptele stilizate, testată cu statistici robuste la heteroscedasticitate.",
                "incorrectExplanation": "RW1 este respinsă de gruparea volatilității; ipoteza care merită testată este RW3, cu inferență robustă."
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
                    "Piețele sunt întotdeauna perfect eficiente",
                    "Trebuie să rămână o anumită ineficiență, suficientă cât să plătească traderii informați pentru informația costisitoare",
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
                "incorrectExplanation": "Gruparea volatilității, nu lungimea selecției sau media, face ca eroarea standard robustă să fie mai mare decât 1/√T."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Variance ratio above one",
                "text": "A variance ratio VR(20) = 1.38, as for the BET index, indicates:",
                "options": [
                    "Positive autocorrelation: returns persist (momentum)",
                    "Mean reversion",
                    "A pure random walk",
                    "Negative volatility"
                ],
                "correctExplanation": "VR(q) = 1 + 2Σ(1 − k/q)ρ_k; a value above one means the weighted sum of autocorrelations is positive, i.e. persistence.",
                "incorrectExplanation": "VR(q) above one means positive autocorrelations (persistence); below one means mean reversion."
            },
            "ro": {
                "title": "Raport al dispersiilor peste unu",
                "text": "Un raport al dispersiilor VR(20) = 1,38, ca pentru indicele BET, indică:",
                "options": [
                    "Autocorelație pozitivă: randamentele persistă (momentum)",
                    "Revenire la medie",
                    "Un mers aleator pur",
                    "Volatilitate negativă"
                ],
                "correctExplanation": "VR(q) = 1 + 2Σ(1 − k/q)ρ_k; o valoare peste unu înseamnă că suma ponderată a autocorelațiilor este pozitivă, adică persistență.",
                "incorrectExplanation": "VR(q) peste unu înseamnă autocorelații pozitive (persistență); sub unu înseamnă revenire la medie."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "VR(2) and autocorrelation",
                "text": "The S&P 500 has a lag-1 autocorrelation of −0.099. What is the approximate VR(2)?",
                "options": [
                    "1.099",
                    "0.802",
                    "1.000",
                    "0.901"
                ],
                "correctExplanation": "VR(2) = 1 + ρ_1 = 1 − 0.099 = 0.901, which matches the estimated value.",
                "incorrectExplanation": "For q = 2 the formula reduces to VR(2) = 1 + ρ_1."
            },
            "ro": {
                "title": "VR(2) și autocorelația",
                "text": "S&P 500 are autocorelația de ordinul 1 egală cu −0,099. Care este aproximativ VR(2)?",
                "options": [
                    "1,099",
                    "0,802",
                    "1,000",
                    "0,901"
                ],
                "correctExplanation": "VR(2) = 1 + ρ_1 = 1 − 0,099 = 0,901, valoare egală cu cea estimată.",
                "incorrectExplanation": "Pentru q = 2 formula se reduce la VR(2) = 1 + ρ_1."
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
                    "Controlează pragul global când se testează mai multe orizonturi; valoarea critică de 5% devine 2,49",
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
                    "Fewer runs than expected: signs persist, consistent with positive autocorrelation",
                    "More runs than expected: frequent reversals",
                    "Returns are normally distributed",
                    "The test cannot be applied to indices"
                ],
                "correctExplanation": "Too few runs means long sequences of equal signs, i.e. persistence, in line with BET’s positive lag-1 autocorrelation.",
                "incorrectExplanation": "A negative z means too few runs, hence persistence of signs."
            },
            "ro": {
                "title": "Testul secvențelor",
                "text": "Indicele BET are statistica testului secvențelor z = −6,05. Ce înseamnă?",
                "options": [
                    "Mai puține secvențe decât ne-am aștepta: semnele persistă, în acord cu o autocorelație pozitivă",
                    "Mai multe secvențe decât ne-am aștepta: inversări frecvente",
                    "Randamentele urmează distribuția Normală",
                    "Testul nu se poate aplica indicilor"
                ],
                "correctExplanation": "Prea puține secvențe înseamnă șiruri lungi de semne egale, adică persistență, în acord cu autocorelația pozitivă de ordinul 1 a BET.",
                "incorrectExplanation": "Un z negativ înseamnă prea puține secvențe, deci persistența semnelor."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Hurst exponent",
                "text": "What does a Hurst exponent H > 0.5 indicate for returns?",
                "options": [
                    "Anti-persistence",
                    "Heavy tails",
                    "No memory",
                    "Persistence (long memory)"
                ],
                "correctExplanation": "H = 0.5 means no memory; H > 0.5 persistence, with autocorrelations decaying like k^(2H−2); H < 0.5 anti-persistence.",
                "incorrectExplanation": "H above 0.5 means persistence; heavy tails are a different property."
            },
            "ro": {
                "title": "Exponentul Hurst",
                "text": "Ce indică un exponent Hurst H > 0,5 pentru randamente?",
                "options": [
                    "Anti-persistență",
                    "Cozi grele",
                    "Lipsa memoriei",
                    "Persistență (memorie lungă)"
                ],
                "correctExplanation": "H = 0,5 înseamnă lipsa memoriei; H > 0,5 persistență, cu autocorelații care scad ca k^(2H−2); H < 0,5 anti-persistență.",
                "incorrectExplanation": "H peste 0,5 înseamnă persistență; cozile grele sunt o altă proprietate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Anis–Lloyd correction",
                "text": "Why is the classical R/S Hurst estimate corrected with the Anis–Lloyd expectation?",
                "options": [
                    "To remove the mean return",
                    "Because R/S is biased upward in small windows, even for i.i.d. returns",
                    "To make the estimate robust to heavy tails",
                    "To annualise the estimate"
                ],
                "correctExplanation": "For the S&P 500 the raw estimate is 0.530 but the corrected one 0.486: the uncorrected slope overstates memory.",
                "incorrectExplanation": "The correction removes the small-sample upward bias of R/S under i.i.d. returns."
            },
            "ro": {
                "title": "Corecția Anis–Lloyd",
                "text": "De ce estimarea Hurst R/S clasică se corectează cu așteptarea Anis–Lloyd?",
                "options": [
                    "Pentru a elimina randamentul mediu",
                    "Pentru că R/S este deplasat în sus pe ferestre mici, chiar pentru randamente i.i.d.",
                    "Pentru a face estimarea robustă la cozi grele",
                    "Pentru a anualiza estimarea"
                ],
                "correctExplanation": "Pentru S&P 500 estimarea brută este 0,530, iar cea corectată 0,486: panta necorectată supraestimează memoria.",
                "incorrectExplanation": "Corecția elimină deplasarea în sus a R/S în selecții mici sub randamente i.i.d."
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
                "correctExplanation": "Lo înlocuiește abaterea standard cu o abatere standard de termen lung (HAC), astfel încât memoria scurtă nu mai imită memoria lungă; sub memorie scurtă V se află în [0,809; 1,862] cu probabilitate 95%.",
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
                "correctExplanation": "Banda din amestecare reprezintă randamente i.i.d.; orice dependență, inclusiv în volatilitate, poate împinge exponentul peste ea. V al lui Lo este o verificare complementară.",
                "incorrectExplanation": "Amestecarea elimină orice tip de dependență, deci o valoare peste bandă poate reflecta gruparea volatilității, nu memoria lungă în randamente."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Adaptive Market Hypothesis",
                "text": "What is the central prediction of Lo’s Adaptive Market Hypothesis?",
                "options": [
                    "Markets are never efficient",
                    "Investors are fully rational",
                    "Prices follow a random walk at all times",
                    "The degree of efficiency changes over time with competition and market conditions"
                ],
                "correctExplanation": "Under the AMH, markets are an ecology of adapting participants; profit opportunities appear and disappear, so efficiency is time-varying.",
                "incorrectExplanation": "The AMH replaces “efficient or not” with a degree of efficiency that varies over time."
            },
            "ro": {
                "title": "Ipoteza pieței adaptive",
                "text": "Care este predicția centrală a ipotezei pieței adaptive a lui Lo?",
                "options": [
                    "Piețele nu sunt niciodată eficiente",
                    "Investitorii sunt complet raționali",
                    "Prețurile urmează în orice moment un mers aleator",
                    "Gradul de eficiență se schimbă în timp, odată cu competiția și condițiile de piață"
                ],
                "correctExplanation": "În AMH, piețele sunt o ecologie de participanți care se adaptează; oportunitățile de profit apar și dispar, deci eficiența variază în timp.",
                "incorrectExplanation": "AMH înlocuiește „eficient sau nu” cu un grad de eficiență care variază în timp."
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
                    "Ca fiind aproape de cei 5% așteptați din întâmplare, ținând cont că ferestrele suprapuse sunt corelate",
                    "Ca dovadă că S&P 500 este perfect eficient",
                    "Ca semn că testul nu are putere"
                ],
                "correctExplanation": "Sub ipoteza nulă circa 5% din ferestre resping din întâmplare, iar ferestrele suprapuse nu sunt dovezi independente.",
                "incorrectExplanation": "Proporția trebuie comparată cu nivelul întâmplător de 5%, iar respingerile consecutive pe ferestre suprapuse sunt corelate."
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
                    "Testele anuale sunt mai puternice decât cele pe întreaga selecție"
                ],
                "correctExplanation": "Baterii de teste diferite, surse de prețuri diferite și erori clasice versus robuste duc la concluzii diferite; un singur an de date are și putere mică.",
                "incorrectExplanation": "Contrastul arată că rezultatele privind eficiența depind de test și de inferență, nu că un studiu este greșit."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Event study",
                "text": "Under semi-strong efficiency, what pattern of abnormal returns should follow a public announcement?",
                "options": [
                    "A slow drift over several weeks",
                    "A reversal of the day-0 move in the next days",
                    "A jump on the announcement day and no predictable drift or reversal afterwards",
                    "No reaction at all"
                ],
                "correctExplanation": "Prices should absorb the news immediately; a drift or reversal after day 0 (as for the 2018 bank tax) points to under- or overreaction.",
                "incorrectExplanation": "Efficiency predicts an immediate jump and no predictable movement afterwards."
            },
            "ro": {
                "title": "Studiul de eveniment",
                "text": "Sub eficiența semi-tare, ce tipar al randamentelor anormale ar trebui să urmeze unui anunț public?",
                "options": [
                    "O derivă lentă pe parcursul mai multor săptămâni",
                    "O inversare a mișcării din ziua 0 în zilele următoare",
                    "Un salt în ziua anunțului și nicio derivă sau inversare predictibilă după aceea",
                    "Nicio reacție"
                ],
                "correctExplanation": "Prețurile ar trebui să absoarbă știrea imediat; o derivă sau o inversare după ziua 0 (ca la taxa bancară din 2018) indică sub- sau supra-reacție.",
                "incorrectExplanation": "Eficiența prezice un salt imediat și nicio mișcare predictibilă după aceea."
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
                    "Pentru că reziduurile sunt heteroscedastice și autocorelate, deci erorile standard OLS nu sunt valide"
                ],
                "correctExplanation": "Erorile standard HAC rămân valide sub heteroscedasticitate și autocorelație; coeficienții nu se schimbă.",
                "incorrectExplanation": "HAC schimbă doar erorile standard, făcând inferența validă când reziduurile sunt heteroscedastice și autocorelate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Bonferroni",
                "text": "Fifteen calendar tests are run at the 5% level. What is the Bonferroni threshold for each p-value?",
                "options": [
                    "0.05",
                    "0.0033",
                    "0.0005",
                    "0.75"
                ],
                "correctExplanation": "Bonferroni divides the level by the number of tests: 0.05 / 15 = 0.0033; this keeps the family-wise error rate below 5%.",
                "incorrectExplanation": "The Bonferroni threshold is α/M = 0.05/15."
            },
            "ro": {
                "title": "Bonferroni",
                "text": "Se rulează cincisprezece teste de calendar la nivelul de 5%. Care este pragul Bonferroni pentru fiecare valoare p?",
                "options": [
                    "0,05",
                    "0,0033",
                    "0,0005",
                    "0,75"
                ],
                "correctExplanation": "Bonferroni împarte nivelul la numărul de teste: 0,05 / 15 = 0,0033; astfel rata erorii pe familia de teste rămâne sub 5%.",
                "incorrectExplanation": "Pragul Bonferroni este α/M = 0,05/15."
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
                "title": "Anomalii din întâmplare",
                "text": "În curs au fost testate 2000 de reguli aleatoare fără sens pe S&P 500. Aproximativ câte au fost „semnificative” la 5%?",
                "options": [
                    "Aproximativ 5%, cât promite testul sub ipoteza nulă",
                    "Niciuna, pentru că regulile sunt aleatoare",
                    "Aproximativ 50%",
                    "Toate, pentru că S&P 500 este ineficient"
                ],
                "correctExplanation": "Aproximativ 4,9% au avut |t| > 1,96: încercarea multor reguli și raportarea celei mai bune produce mereu o anomalie aparentă (data snooping).",
                "incorrectExplanation": "Sub ipoteza nulă, aproximativ 5% din teste resping din întâmplare; de aceea testarea multiplă trebuie corectată."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Limits to arbitrage",
                "text": "According to Shleifer and Vishny (1997), why can mispricing persist?",
                "options": [
                    "Because arbitrage is riskless",
                    "Because investors are always rational",
                    "Because arbitrage needs capital and bears noise-trader risk: mispricing can worsen before it corrects",
                    "Because prices are set by regulators"
                ],
                "correctExplanation": "Professional arbitrageurs face capital constraints and client withdrawals after losses, so they cannot always trade against mispricing.",
                "incorrectExplanation": "Real arbitrage is risky and capital-constrained; this is the essence of the limits to arbitrage."
            },
            "ro": {
                "title": "Limitele arbitrajului",
                "text": "Conform lui Shleifer și Vishny (1997), de ce poate persista prețul greșit?",
                "options": [
                    "Pentru că arbitrajul este fără risc",
                    "Pentru că investitorii sunt întotdeauna raționali",
                    "Pentru că arbitrajul cere capital și suportă riscul traderilor de zgomot: prețul greșit se poate înrăutăți înainte să se corecteze",
                    "Pentru că prețurile sunt stabilite de autorități"
                ],
                "correctExplanation": "Arbitrajorii profesioniști au constrângeri de capital și pierd clienți după pierderi, deci nu pot tranzacționa mereu împotriva prețului greșit.",
                "incorrectExplanation": "Arbitrajul real este riscant și limitat de capital; aceasta este esența limitelor arbitrajului."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Statistical versus economic significance",
                "text": "Time-series momentum on BET has a HAC t-statistic of 2.56, but its Sharpe ratio is 0.62 against 0.61 for buy-and-hold. What does this show?",
                "options": [
                    "BET is extremely inefficient",
                    "The t-statistic is wrong",
                    "Momentum always beats buy-and-hold",
                    "A statistically significant pattern can add little economic value over a simple benchmark"
                ],
                "correctExplanation": "Much of the momentum return is the equity premium earned while long; significance against zero is not significance against buy-and-hold.",
                "incorrectExplanation": "Statistical rejection is not the same as an exploitable improvement: compare with the relevant benchmark and costs."
            },
            "ro": {
                "title": "Semnificație statistică versus economică",
                "text": "Momentum-ul pe serii de timp pe BET are statistica t HAC egală cu 2,56, dar raportul Sharpe este 0,62 față de 0,61 pentru cumpără-și-păstrează. Ce arată acest lucru?",
                "options": [
                    "BET este extrem de ineficient",
                    "Statistica t este greșită",
                    "Momentum-ul bate întotdeauna strategia cumpără-și-păstrează",
                    "Un tipar semnificativ statistic poate adăuga puțină valoare economică față de un reper simplu"
                ],
                "correctExplanation": "O mare parte din randamentul momentum este prima de risc a acțiunilor câștigată pe pozițiile lungi; semnificația față de zero nu este semnificație față de cumpără-și-păstrează.",
                "incorrectExplanation": "Respingerea statistică nu este același lucru cu o îmbunătățire exploatabilă: comparați cu reperul relevant și cu costurile."
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
                "text": "Un asistent AI scrie: „VR(2) = 0,90. Deoarece VR(2) = 1 + 2ρ₁, autocorelația de ordinul întâi este ρ₁ = −0,05.” Ce este greșit?",
                "options": [
                    "VR(q) = 1 + 2 Σ (1 − k/q) ρ_k, deci VR(2) = 1 + ρ₁ și ρ₁ ≈ −0,10",
                    "VR(2) = 0,90 implică ρ₁ = +0,10",
                    "Raportul dispersiilor nu depinde de autocorelații",
                    "VR(2) = 1 + 4ρ₁, deci ρ₁ = −0,025"
                ],
                "correctExplanation": "Pentru q = 2 singura pondere este 1 − 1/2, deci VR(2) = 1 + 2 · ½ · ρ₁ = 1 + ρ₁ și ρ₁ ≈ 0,90 − 1 = −0,10.",
                "incorrectExplanation": "Lipsesc ponderile (1 − k/q): pentru q = 2, VR(2) = 1 + ρ₁, deci ρ₁ ≈ −0,10, dublul valorii date de AI."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the AI error: reading a variance ratio",
                "text": "An AI assistant writes: \"The 5-day variance ratio of the index is 0.83, significantly below 1. This means positive autocorrelation: momentum, so buy after up days.\" What is wrong?",
                "options": [
                    "A variance ratio below 1 proves that the market is efficient",
                    "Variance ratios are always below 1 for daily data, so nothing can be concluded",
                    "VR < 1 means negative autocorrelation (reversal), not momentum; and a rejection is not yet a profitable trading rule",
                    "The variance ratio measures volatility clustering, not autocorrelation"
                ],
                "correctExplanation": "VR(q) − 1 = 2 Σ (1 − k/q) ρ_k: a value below 1 needs negative autocorrelations, i.e. short-run reversal. Even then, transaction costs and risk decide whether a strategy pays.",
                "incorrectExplanation": "Below 1 the weighted autocorrelations are negative, which is reversal, not momentum; a statistical rejection says nothing yet about profits after costs."
            },
            "ro": {
                "title": "Găsiți eroarea AI: interpretarea raportului dispersiilor",
                "text": "Un asistent AI scrie: „Raportul dispersiilor pe 5 zile al indicelui este 0,83, semnificativ sub 1. Asta înseamnă autocorelație pozitivă: momentum, deci cumpărați după zilele de creștere.” Ce este greșit?",
                "options": [
                    "Un raport al dispersiilor sub 1 dovedește că piața este eficientă",
                    "Rapoartele dispersiilor sunt mereu sub 1 pentru date zilnice, deci nu se poate trage nicio concluzie",
                    "VR < 1 înseamnă autocorelație negativă (inversare), nu momentum; iar o respingere nu este încă o regulă de tranzacționare profitabilă",
                    "Raportul dispersiilor măsoară gruparea volatilității, nu autocorelația"
                ],
                "correctExplanation": "VR(q) − 1 = 2 Σ (1 − k/q) ρ_k: o valoare sub 1 cere autocorelații negative, adică inversare pe termen scurt. Chiar și atunci, costurile de tranzacționare și riscul decid dacă o strategie aduce profit.",
                "incorrectExplanation": "Sub 1 autocorelațiile ponderate sunt negative, adică inversare, nu momentum; o respingere statistică nu spune încă nimic despre profitul după costuri."
            }
        }
    ]
};

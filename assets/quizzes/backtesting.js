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
            "correct": 1,
            "en": {
                "title": "The hit sequence",
                "text": "What does the hit sequence I_t of a VaR backtest record?",
                "options": [
                    "The daily return of the portfolio",
                    "Whether the loss on day t exceeded the VaR forecast for day t",
                    "The number of models that passed the test",
                    "The volatility forecast of a GARCH model"
                ],
                "correctExplanation": "I_t = 1 when the realised loss exceeds the VaR forecast and 0 otherwise; all coverage tests are built on this 0/1 sequence.",
                "incorrectExplanation": "The hit sequence is the 0/1 indicator of a breach, L_t > VaR_t, on each day."
            },
            "ro": {
                "title": "Șirul depășirilor",
                "text": "Ce înregistrează șirul depășirilor I_t într-un backtest VaR?",
                "options": [
                    "Randamentul zilnic al portofoliului",
                    "Dacă pierderea din ziua t a depășit prognoza VaR pentru ziua t",
                    "Numărul de modele care au trecut testul",
                    "Prognoza de volatilitate a unui model GARCH"
                ],
                "correctExplanation": "I_t = 1 când pierderea realizată depășește prognoza VaR și 0 altfel; toate testele de acoperire se construiesc pe acest șir 0/1.",
                "incorrectExplanation": "Șirul depășirilor este indicatorul 0/1 al unei depășiri, L_t > VaR_t, în fiecare zi."
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
                    "Pentru că randamentele zilnice sunt Normale",
                    "Pentru că se așteaptă doar circa 2,5 depășiri, deci modelele greșite produc des numărări acceptabile",
                    "Pentru că aproximarea hi-pătrat este exactă",
                    "Pentru că depășirile sunt mereu independente"
                ],
                "correctExplanation": "Cu T = 250 și alpha = 1%, numărul așteptat este 2,5; un model cu rata reală de 2% cade totuși în regiunea de acceptare (1--6 depășiri) aproximativ de trei ori din patru.",
                "incorrectExplanation": "Evenimentele din coadă sunt rare: un an conține prea puține depășiri pentru a separa modelele bune de cele mediocre."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Christoffersen independence",
                "text": "In the Christoffersen independence test, what is compared?",
                "options": [
                    "The mean and variance of the losses",
                    "The ES forecasts of two models",
                    "The probability of a breach after a breach (pi_11) with that after no breach (pi_01)",
                    "The breach rates of VaR 1% and VaR 2.5%"
                ],
                "correctExplanation": "The hits are modelled as a first-order Markov chain; H0 states pi_01 = pi_11, i.e. yesterday's breach does not change today's breach probability.",
                "incorrectExplanation": "The test compares the transition probabilities pi_01 and pi_11 of the breach Markov chain."
            },
            "ro": {
                "title": "Independența Christoffersen",
                "text": "Ce se compară în testul de independență Christoffersen?",
                "options": [
                    "Media și dispersia pierderilor",
                    "Prognozele ES a două modele",
                    "Probabilitatea unei depășiri după o depășire (pi_11) cu cea după o zi fără depășire (pi_01)",
                    "Ratele de depășire ale VaR 1% și VaR 2,5%"
                ],
                "correctExplanation": "Depășirile sunt modelate ca lanț Markov de ordinul întâi; H0 afirmă pi_01 = pi_11, adică depășirea de ieri nu schimbă probabilitatea de azi.",
                "incorrectExplanation": "Testul compară probabilitățile de tranziție pi_01 și pi_11 ale lanțului Markov al depășirilor."
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
                    "Prea multe durate scurte: depășirile vin grupate"
                ],
                "correctExplanation": "b = 1 este cazul fără memorie (exponențial); b < 1 înseamnă că intervalele scurte dintre depășiri sunt prea frecvente, semnul grupării. Pe S&P 500, HS are b = 0,52.",
                "incorrectExplanation": "O formă sub unu înseamnă depășiri grupate: duratele scurte sunt suprareprezentate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Traffic light zones",
                "text": "Where does the Basel traffic light for 250 days of VaR 1% place a bank with 6 exceptions?",
                "options": [
                    "Green zone",
                    "Yellow (amber) zone",
                    "Red zone",
                    "The rule only applies to ES"
                ],
                "correctExplanation": "Green is 0-4, yellow 5-9, red 10 or more exceptions; the boundaries come from the Binomial(250, 0.01) cumulative probabilities 95% and 99.99%.",
                "incorrectExplanation": "Six exceptions fall in the yellow zone (5 to 9 exceptions)."
            },
            "ro": {
                "title": "Zonele semaforului",
                "text": "Unde plasează semaforul Basel, pentru 250 de zile de VaR 1%, o bancă cu 6 excepții?",
                "options": [
                    "Zona verde",
                    "Zona galbenă",
                    "Zona roșie",
                    "Regula se aplică doar pentru ES"
                ],
                "correctExplanation": "Verde înseamnă 0-4, galben 5-9, roșu 10 sau mai multe excepții; pragurile provin din probabilitățile cumulate Binomiale(250; 0,01) de 95% și 99,99%.",
                "incorrectExplanation": "Șase excepții cad în zona galbenă (5-9 excepții)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "FRTB",
                "text": "Under the FRTB (BCBS 2019), which statement is correct?",
                "options": [
                    "Capital is based on VaR 1% and backtesting on ES",
                    "Backtesting has been abolished",
                    "Capital is based on ES 2.5%, while backtesting still uses VaR 1% and VaR 2.5%",
                    "Capital and backtesting both use VaR 5%"
                ],
                "correctExplanation": "The FRTB computes capital from ES 2.5% but backtests VaR: bank-wide VaR 1%, and per desk VaR 1% (12 exceptions) and VaR 2.5% (30 exceptions).",
                "incorrectExplanation": "FRTB separates the two: ES 2.5% for capital, VaR 1% and VaR 2.5% for backtesting."
            },
            "ro": {
                "title": "FRTB",
                "text": "Conform FRTB (BCBS 2019), care afirmație este corectă?",
                "options": [
                    "Capitalul se bazează pe VaR 1%, iar backtesting-ul pe ES",
                    "Backtesting-ul a fost eliminat",
                    "Capitalul se bazează pe ES 2,5%, iar backtesting-ul folosește în continuare VaR 1% și VaR 2,5%",
                    "Capitalul și backtesting-ul folosesc ambele VaR 5%"
                ],
                "correctExplanation": "FRTB calculează capitalul din ES 2,5%, dar testează VaR: la nivelul băncii VaR 1%, pe mese VaR 1% (12 excepții) și VaR 2,5% (30 de excepții).",
                "incorrectExplanation": "FRTB le separă: ES 2,5% pentru capital, VaR 1% și VaR 2,5% pentru backtesting."
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
                "title": "De ce ES este dificil",
                "text": "De ce ES este mai greu de testat decât VaR?",
                "options": [
                    "Depinde de mărimea pierderilor de dincolo de VaR, iar doar circa alpha T zile din coadă aduc informație",
                    "Este întotdeauna mai mic decât VaR",
                    "Nu poate fi calculat pentru distribuții cu cozi groase",
                    "Reglementatorii nu permit teste pentru ES"
                ],
                "correctExplanation": "ES este o medie peste coadă; eșantionul din coadă are circa alpha T observații (6,25 într-un an pentru alpha = 2,5%), deci precizia este redusă.",
                "incorrectExplanation": "Dificultatea ține de informație: ES este o medie din coadă estimată din foarte puține observații."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "McNeil-Frey residuals",
                "text": "The McNeil-Frey test uses the exceedance residuals (L_t - ES_t)/sigma_t on breach days. Under a correct ES they have",
                "options": [
                    "variance zero",
                    "a Normal distribution",
                    "a positive mean",
                    "mean zero"
                ],
                "correctExplanation": "If ES is correct, E[L_t - ES_t | L_t > VaR_t] = 0; a positive mean signals underestimated ES. The p-value is usually obtained by bootstrap.",
                "incorrectExplanation": "The null hypothesis is a zero mean of the exceedance residuals; a positive mean means ES is too low."
            },
            "ro": {
                "title": "Reziduurile McNeil-Frey",
                "text": "Testul McNeil-Frey folosește reziduurile de depășire (L_t - ES_t)/sigma_t în zilele cu depășire. Pentru un ES corect, acestea au",
                "options": [
                    "dispersia zero",
                    "o distribuție Normală",
                    "o medie pozitivă",
                    "media zero"
                ],
                "correctExplanation": "Dacă ES este corect, E[L_t - ES_t | L_t > VaR_t] = 0; o medie pozitivă semnalează un ES subestimat. Valoarea p se obține de obicei prin bootstrap.",
                "incorrectExplanation": "Ipoteza nulă este media zero a reziduurilor de depășire; o medie pozitivă înseamnă că ES este prea mic."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Acerbi-Szekely Z2",
                "text": "For T = 250 and alpha = 2.5%, Acerbi and Szekely report 5% and 0.01% thresholds for Z2 close to",
                "options": [
                    "+0.70 and +1.8",
                    "-0.70 and -1.8",
                    "-1.96 and -3.09",
                    "0 and -1"
                ],
                "correctExplanation": "Z2 has expectation zero under H0 and becomes negative when risk is underestimated; its critical values are stable across distributions, near -0.70 (5%) and -1.8 (0.01%).",
                "incorrectExplanation": "Underestimated risk pushes Z2 below zero; the fixed thresholds are about -0.70 and -1.8."
            },
            "ro": {
                "title": "Z2 Acerbi-Szekely",
                "text": "Pentru T = 250 și alpha = 2,5%, Acerbi și Szekely raportează praguri de 5% și 0,01% pentru Z2 apropiate de",
                "options": [
                    "+0,70 și +1,8",
                    "-0,70 și -1,8",
                    "-1,96 și -3,09",
                    "0 și -1"
                ],
                "correctExplanation": "Z2 are media zero sub H0 și devine negativ când riscul este subestimat; valorile critice sunt stabile între distribuții, în jur de -0,70 (5%) și -1,8 (0,01%).",
                "incorrectExplanation": "Riscul subestimat împinge Z2 sub zero; pragurile fixe sunt aproximativ -0,70 și -1,8."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Elicitability",
                "text": "A statistic is elicitable when",
                "options": [
                    "it can be estimated by maximum likelihood",
                    "it is always positive",
                    "it has a closed-form formula",
                    "some scoring function is minimised in expectation exactly by its true value"
                ],
                "correctExplanation": "Elicitability (Gneiting, 2011) means a consistent scoring function exists: the mean with squared error, a quantile (VaR) with the pinball loss.",
                "incorrectExplanation": "Elicitable means there is a scoring function whose expected value is minimised by the true value of the statistic."
            },
            "ro": {
                "title": "Elicitabilitate",
                "text": "O statistică este elicitabilă atunci când",
                "options": [
                    "poate fi estimată prin verosimilitate maximă",
                    "este întotdeauna pozitivă",
                    "are o formulă explicită",
                    "o funcție de scor este minimizată în medie exact de valoarea ei adevărată"
                ],
                "correctExplanation": "Elicitabilitatea (Gneiting, 2011) înseamnă că există o funcție de scor consistentă: media cu eroarea pătratică, o cuantilă (VaR) cu pierderea pinball.",
                "incorrectExplanation": "Elicitabil înseamnă că există o funcție de scor a cărei valoare așteptată este minimizată de valoarea adevărată a statisticii."
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
                    "Nici VaR, nici ES nu sunt elicitabile",
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
                    "It rewards large ES forecasts",
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
                    "Recompensează prognozele ES mari",
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
                    "Pentru că pierderile FZ0 sunt mereu Normale",
                    "Pentru a face testul unilateral",
                    "Pentru că testul are nevoie de cel puțin două active"
                ],
                "correctExplanation": "Dispersia pe termen lung ține cont de autocorelație; pentru HS față de FHS pe S&P 500 este de circa 2,3 ori dispersia obișnuită, iar statistica t naivă supraestimează semnificația.",
                "incorrectExplanation": "Diferențele de pierdere sunt autocorelate în crize; o dispersie HAC pe termen lung corectează eroarea standard."
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
                    "The set of models that contains the best one with a given probability, after sequential elimination"
                ],
                "correctExplanation": "Models are eliminated one by one while equal predictive ability is rejected; the survivors form the MCS. On Bitcoin all six models survive: the data cannot separate them.",
                "incorrectExplanation": "The MCS is a set of statistically equivalent best models, not a single winner."
            },
            "ro": {
                "title": "Mulțimea de modele de încredere",
                "text": "Ce conține o mulțime de modele de încredere (Hansen, Lunde și Nason, 2011)?",
                "options": [
                    "Doar cel mai bun model",
                    "Toate modelele care trec testul Kupiec",
                    "Modelele cu statistici DM pozitive",
                    "Mulțimea de modele care conține modelul cel mai bun cu o probabilitate dată, după eliminări succesive"
                ],
                "correctExplanation": "Modelele sunt eliminate unul câte unul cât timp egalitatea abilității predictive este respinsă; cele rămase formează MCS. Pe Bitcoin rămân toate cele șase modele: datele nu le pot separa.",
                "incorrectExplanation": "MCS este o mulțime de modele cele mai bune, echivalente statistic, nu un singur câștigător."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Split conformal",
                "text": "With n = 250 calibration scores and alpha = 1%, which order statistic gives the split conformal VaR quantile?",
                "options": [
                    "The 248th",
                    "The 249th, since k = ceil(251 x 0.99)",
                    "The 250th",
                    "The median"
                ],
                "correctExplanation": "k = ceil((n+1)(1-alpha)) = ceil(248.49) = 249, the second largest score; under exchangeability the breach probability is then between about 0.60% and 1%.",
                "incorrectExplanation": "The index is k = ceil((n+1)(1-alpha)) = 249."
            },
            "ro": {
                "title": "Conformal split",
                "text": "Cu n = 250 de scoruri de calibrare și alpha = 1%, ce statistică de ordine dă cuantila VaR conformală split?",
                "options": [
                    "A 248-a",
                    "A 249-a, deoarece k = ceil(251 x 0,99)",
                    "A 250-a",
                    "Mediana"
                ],
                "correctExplanation": "k = ceil((n+1)(1-alpha)) = ceil(248,49) = 249, al doilea cel mai mare scor; sub schimbabilitate, probabilitatea de depășire este apoi între circa 0,60% și 1%.",
                "incorrectExplanation": "Indicele este k = ceil((n+1)(1-alpha)) = 249."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Exchangeability",
                "text": "Why does the split conformal guarantee fail conditionally on financial returns?",
                "options": [
                    "Because returns have a mean of zero",
                    "Because the method needs Normal data",
                    "Because volatility clustering makes the scores non-exchangeable, so breaches concentrate after turbulent periods",
                    "Because the calibration set is too large"
                ],
                "correctExplanation": "The guarantee holds only on average over exchangeable data; after turbulent periods the S&P 500 split conformal VaR 5% is breached on about 7% of days, and breaches cluster.",
                "incorrectExplanation": "The assumption that breaks is exchangeability: volatility clusters, so coverage is only marginal."
            },
            "ro": {
                "title": "Schimbabilitate",
                "text": "De ce garanția conformală split eșuează condiționat pe randamentele financiare?",
                "options": [
                    "Pentru că randamentele au media zero",
                    "Pentru că metoda cere date Normale",
                    "Pentru că gruparea volatilității face scorurile neschimbabile, deci depășirile se concentrează după perioade agitate",
                    "Pentru că mulțimea de calibrare este prea mare"
                ],
                "correctExplanation": "Garanția este valabilă doar în medie, pentru date schimbabile; după perioade agitate, VaR conformal split 5% pe S&P 500 este depășit în circa 7% dintre zile, iar depășirile se grupează.",
                "incorrectExplanation": "Ipoteza care cade este schimbabilitatea: volatilitatea se grupează, deci acoperirea este doar marginală."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Adaptive conformal inference",
                "text": "What is the update rule of adaptive conformal inference (Gibbs and Candès, 2021)?",
                "options": [
                    "alpha_{t+1} = alpha_t + gamma (alpha - err_t)",
                    "alpha_{t+1} = alpha_t x err_t",
                    "alpha_{t+1} = alpha (constant)",
                    "alpha_{t+1} = 1 - alpha_t"
                ],
                "correctExplanation": "After a breach (err_t = 1) the working level falls and the VaR rises; after quiet days it drifts back. The long-run breach rate converges to alpha for any sequence.",
                "incorrectExplanation": "ACI moves the working level by gamma times the gap between the target and the latest error."
            },
            "ro": {
                "title": "Inferența conformală adaptivă",
                "text": "Care este regula de actualizare a inferenței conformale adaptive (Gibbs și Candès, 2021)?",
                "options": [
                    "alpha_{t+1} = alpha_t + gamma (alpha - err_t)",
                    "alpha_{t+1} = alpha_t x err_t",
                    "alpha_{t+1} = alpha (constant)",
                    "alpha_{t+1} = 1 - alpha_t"
                ],
                "correctExplanation": "După o depășire (err_t = 1) nivelul de lucru scade și VaR crește; după zile liniștite revine treptat. Rata de depășire pe termen lung converge la alpha pentru orice șir.",
                "incorrectExplanation": "ACI mută nivelul de lucru cu gamma ori diferența dintre țintă și ultima eroare."
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
                "title": "Prețul ACI",
                "text": "Pentru VaR 1% pe S&P 500, cum și-a menținut ACI rata de depășire pe termen lung aproape de 1%?",
                "options": [
                    "Folosind un model GARCH",
                    "Reducând mulțimea de calibrare la 20 de zile",
                    "Ignorând zilele de criză",
                    "Dând un VaR infinit într-o parte importantă a zilelor (circa 13%)"
                ],
                "correctExplanation": "Când alpha_t scade sub 1/(n+1), cuantila cerută nu există și VaR devine infinit; aceasta s-a întâmplat în circa 13% dintre zilele S&P 500: acoperire fără informație.",
                "incorrectExplanation": "Garanția a fost obținută prin prognoze VaR infinite în multe zile."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Which model wins?",
                "text": "Across the S&P 500, BET, Bitcoin and EUR/RON, which models pass the Z2 test and stay in the 90% model confidence set everywhere?",
                "options": [
                    "HS and the Normal distribution",
                    "Student-t and GARCH-t",
                    "FHS and GARCH-EVT",
                    "Only the Normal distribution"
                ],
                "correctExplanation": "A GARCH volatility filter plus a flexible tail (empirical or generalised Pareto) passes all ES tests and stays in the MCS in all four markets.",
                "incorrectExplanation": "The winners combine a GARCH filter with a flexible tail: FHS and GARCH-EVT."
            },
            "ro": {
                "title": "Ce model câștigă?",
                "text": "Pe S&P 500, BET, Bitcoin și EUR/RON, ce modele trec testul Z2 și rămân peste tot în mulțimea de modele de încredere de 90%?",
                "options": [
                    "HS și distribuția Normală",
                    "Student-t și GARCH-t",
                    "FHS și GARCH-EVT",
                    "Doar distribuția Normală"
                ],
                "correctExplanation": "Un filtru de volatilitate GARCH plus o coadă flexibilă (empirică sau Pareto generalizată) trece toate testele ES și rămâne în MCS pe toate cele patru piețe.",
                "incorrectExplanation": "Câștigătorii combină un filtru GARCH cu o coadă flexibilă: FHS și GARCH-EVT."
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
                "correctExplanation": "HS updates only when extreme days enter the 1000-day window; FHS multiplies empirical standardised quantiles by today's volatility forecast, so it adapts to the crash almost immediately.",
                "incorrectExplanation": "Conditioning on current volatility, not the tail shape, made the difference."
            },
            "ro": {
                "title": "Martie 2020",
                "text": "În februarie-iunie 2020 (104 zile), VaR 1% pentru S&P 500 a fost depășit de 12 ori de HS și de 2 ori de FHS. Ce explică diferența?",
                "options": [
                    "FHS folosește o fereastră mai lungă",
                    "FHS scalează cuantilele cu volatilitatea GARCH curentă, care a crescut în câteva zile",
                    "HS presupune distribuția Normală",
                    "FHS ignoră cele mai mari pierderi"
                ],
                "correctExplanation": "HS se actualizează doar când zile extreme intră în fereastra de 1000 de zile; FHS înmulțește cuantilele empirice standardizate cu volatilitatea prognozată azi, deci se adaptează aproape imediat la prăbușire.",
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
                "title": "A testa versus a clasifica",
                "text": "Care este diferența dintre un backtest și backtesting-ul comparativ?",
                "options": [
                    "Nu există nicio diferență",
                    "Un backtest clasifică modelele, backtesting-ul comparativ testează un singur model",
                    "Backtest-urile folosesc doar ES, cel comparativ doar VaR",
                    "Un backtest întreabă dacă un model este acceptabil; backtesting-ul comparativ întreabă care dintre mai multe modele este mai bun, cu un scor consistent"
                ],
                "correctExplanation": "Mai multe modele pot trece (sau toate pot eșua) un backtest; clasificarea cere o funcție de scor consistentă, cum este FZ0, și teste precum Diebold-Mariano (Nolde și Ziegel, 2017).",
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
                "text": "Un asistent AI scrie: „Statistica de acoperire condiționată LR_cc = LR_uc + LR_ind se compară cu distribuția hi-pătrat cu 1 grad de libertate, deci respingem la 5% când LR_cc > 3,84.” Ce este greșit?",
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
                "text": "Un asistent AI scrie: „Pentru VaR 1% prin simulare istorică în ziua t, luați minus cuantila de 1% a celor 250 de randamente r_{t-249}, ..., r_t, apoi marcați o excepție când -r_t îl depășește.” Ce este greșit?",
                "options": [
                    "VaR ar trebui să fie plus cuantila de 1%, nu minus",
                    "Fereastra îl conține chiar pe r_t: VaR_t trebuie să folosească doar randamentele cunoscute în t-1, adică r_{t-250}, ..., r_{t-1}",
                    "O excepție apare când r_t depășește VaR, nu -r_t",
                    "Simularea istorică cere cel puțin 1.000 de zile, deci 250 nu este permis"
                ],
                "correctExplanation": "Aceasta este privirea în viitor: o pierdere mare în ziua t intră în propria cuantilă și ascunde excepția, astfel că backtest-ul pare mai bun decât este. Convenția de semn (VaR = minus cuantila, excepție când pierderea -r_t depășește VaR) este corectă.",
                "incorrectExplanation": "Convenția de semn și regula de excepție sunt corecte; greșeala este că prognoza pentru ziua t folosește randamentul din ziua t."
            }
        }
    ]
};

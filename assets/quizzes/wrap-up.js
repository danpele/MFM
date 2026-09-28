// ============================================================
// Quiz bank for chapter id 'wrap-up': Review and Project Presentations (EN + RO)
// Cumulative review of Chapters 0-18 and the project.
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['wrap-up'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "Log returns over time",
                "text": "Why are log returns convenient for multi-period analysis?",
                "options": [
                    "They are always normally distributed",
                    "They add up across assets in a portfolio",
                    "They add up over time: the log return of a period is the sum of the daily log returns",
                    "They are always smaller than simple returns in absolute value"
                ],
                "correctExplanation": "ln(P_T/P_0) is the sum of the daily log returns, so aggregation over time is exact.",
                "incorrectExplanation": "Only aggregation over time is exact for log returns; across assets the simple returns add up with the weights, and log returns are not Normal in general."
            },
            "ro": {
                "title": "Randamente log în timp",
                "text": "De ce sunt randamentele logaritmice comode pentru analiza pe mai multe perioade?",
                "options": [
                    "Sunt întotdeauna distribuite Normal",
                    "Se adună între active într-un portofoliu",
                    "Se adună în timp: randamentul log al unei perioade este suma randamentelor log zilnice",
                    "Sunt întotdeauna mai mici în valoare absolută decât randamentele simple"
                ],
                "correctExplanation": "ln(P_T/P_0) este suma randamentelor log zilnice, deci agregarea în timp este exactă.",
                "incorrectExplanation": "Doar agregarea în timp este exactă pentru randamentele log; între active se adună randamentele simple, ponderate, iar randamentele log nu sunt Normale în general."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Stylised facts",
                "text": "Which combination describes daily equity returns best?",
                "options": [
                    "Almost no autocorrelation in returns, strong autocorrelation in absolute returns, heavy tails",
                    "Strong autocorrelation in returns, none in absolute returns",
                    "Normal distribution with constant variance",
                    "Heavy tails but no volatility clustering"
                ],
                "correctExplanation": "Returns are nearly uncorrelated, but their size (|r_t|, r_t^2) is strongly autocorrelated, and tails are heavy.",
                "incorrectExplanation": "The sign of returns is almost unpredictable, their size is not; a constant-variance model with the Normal distribution fails on both tails and clustering."
            },
            "ro": {
                "title": "Fapte stilizate",
                "text": "Ce combinație descrie cel mai bine randamentele zilnice ale acțiunilor?",
                "options": [
                    "Aproape nicio autocorelație a randamentelor, autocorelație puternică a randamentelor absolute, cozi groase",
                    "Autocorelație puternică a randamentelor, niciuna a randamentelor absolute",
                    "Distribuția Normală cu varianță constantă",
                    "Cozi groase, dar fără grupări de volatilitate"
                ],
                "correctExplanation": "Randamentele sunt aproape necorelate, dar mărimea lor (|r_t|, r_t^2) este puternic autocorelată, iar cozile sunt groase.",
                "incorrectExplanation": "Semnul randamentelor este aproape imprevizibil, mărimea lor nu; modelul Normal cu varianță constantă greșește atât la cozi, cât și la grupări."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Joining two assets",
                "text": "Bitcoin trades every day, SPY only on weekdays. How should you build a joint return series?",
                "options": [
                    "Compute returns on each calendar, then keep the common days",
                    "Fill SPY weekends with zero returns",
                    "Drop Bitcoin's Monday returns",
                    "Keep the common days of the prices, then compute returns"
                ],
                "correctExplanation": "Aligning prices first makes Monday's return span Friday to Monday for both assets.",
                "incorrectExplanation": "Computing returns first and then joining deletes Bitcoin's weekend moves, which understates its variance and cumulative return."
            },
            "ro": {
                "title": "Unirea a două active",
                "text": "Bitcoin se tranzacționează zilnic, SPY doar în zilele lucrătoare. Cum construiți o serie comună de randamente?",
                "options": [
                    "Calculăm randamentele pe fiecare calendar, apoi păstrăm zilele comune",
                    "Completăm weekendurile SPY cu randamente zero",
                    "Eliminăm randamentele Bitcoin din zilele de luni",
                    "Păstrăm zilele comune ale prețurilor, apoi calculăm randamentele"
                ],
                "correctExplanation": "Alinierea întâi a prețurilor face ca randamentul de luni să acopere intervalul vineri--luni pentru ambele active.",
                "incorrectExplanation": "Calculul randamentelor înainte de join șterge mișcările Bitcoin din weekend, ceea ce subestimează varianța și randamentul cumulat."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Variance ratio",
                "text": "Under a random walk, what is the variance ratio VR(q)?",
                "options": [
                    "q",
                    "1",
                    "0",
                    "1/q"
                ],
                "correctExplanation": "The variance of a q-period return equals q times the one-period variance, so VR(q) = 1.",
                "incorrectExplanation": "Under a random walk variances add up with the horizon; positive autocorrelation pushes VR above 1, negative below 1."
            },
            "ro": {
                "title": "Raportul varianțelor",
                "text": "Pentru un mers aleator, cât este raportul varianțelor VR(q)?",
                "options": [
                    "q",
                    "1",
                    "0",
                    "1/q"
                ],
                "correctExplanation": "Varianța randamentului pe q perioade este de q ori varianța pe o perioadă, deci VR(q) = 1.",
                "incorrectExplanation": "Pentru un mers aleator varianțele se adună cu orizontul; autocorelația pozitivă duce VR peste 1, cea negativă sub 1."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Multiple testing",
                "text": "300 useless factors are each tested at |t| > 1.96. What happens?",
                "options": [
                    "About 15 look significant by chance, and the best one reaches |t| near 3",
                    "None looks significant",
                    "All of them look significant",
                    "Exactly one looks significant"
                ],
                "correctExplanation": "At 5% each, 300 tests give about 15 false discoveries, and the maximum |t| is around 3.",
                "incorrectExplanation": "Each test has a 5% false-positive rate, so many tests produce false discoveries; this is why the factor literature asks for |t| > 3."
            },
            "ro": {
                "title": "Testare multiplă",
                "text": "300 de factori fără valoare sunt testați fiecare la |t| > 1,96. Ce se întâmplă?",
                "options": [
                    "Circa 15 par semnificativi din întâmplare, iar cel mai bun ajunge la |t| aproape de 3",
                    "Niciunul nu pare semnificativ",
                    "Toți par semnificativi",
                    "Exact unul pare semnificativ"
                ],
                "correctExplanation": "La 5% fiecare, 300 de teste dau circa 15 descoperiri false, iar |t| maxim este în jur de 3.",
                "incorrectExplanation": "Fiecare test are o rată de 5% de fals pozitive, deci multe teste produc descoperiri false; de aceea literatura despre factori cere |t| > 3."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "CAPM on the data",
                "text": "What did the 25 size and book-to-market portfolios show about the CAPM?",
                "options": [
                    "A flat or negative security market line and a GRS test that rejects the CAPM",
                    "A steep security market line that confirms the CAPM",
                    "Betas equal to 1 for all portfolios",
                    "No difference in average returns across portfolios"
                ],
                "correctExplanation": "The fitted SML had slope -4.4% and GRS = 4.18: higher beta did not bring higher average return.",
                "incorrectExplanation": "The cross-section contradicts the CAPM prediction that average excess returns rise linearly with beta."
            },
            "ro": {
                "title": "CAPM pe date",
                "text": "Ce au arătat cele 25 de portofolii după mărime și raportul valoare contabilă/de piață despre CAPM?",
                "options": [
                    "O dreaptă a pieței titlurilor plată sau descrescătoare și un test GRS care respinge CAPM",
                    "O dreaptă a pieței titlurilor abruptă, care confirmă CAPM",
                    "Beta egal cu 1 pentru toate portofoliile",
                    "Nicio diferență între randamentele medii ale portofoliilor"
                ],
                "correctExplanation": "SML estimată a avut panta -4,4%, iar GRS = 4,18: un beta mai mare nu a adus un randament mediu mai mare.",
                "incorrectExplanation": "Secțiunea transversală contrazice predicția CAPM că randamentele medii în exces cresc liniar cu beta."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Estimation error",
                "text": "Why does the sample mean-variance portfolio often lose to 1/N out of sample?",
                "options": [
                    "1/N always has the highest Sharpe ratio in theory",
                    "Estimation error in expected returns dominates, and optimisation amplifies it",
                    "Mean-variance ignores variances",
                    "Out-of-sample data are always calmer"
                ],
                "correctExplanation": "The optimiser loads on assets whose mean was overestimated; with 60 months, in-sample Sharpe 1.57 became a true Sharpe of 0.30.",
                "incorrectExplanation": "The theory is right, but the inputs are noisy: errors in expected returns are magnified by the inverse covariance matrix."
            },
            "ro": {
                "title": "Eroarea de estimare",
                "text": "De ce pierde adesea portofoliul medie-varianță estimat în fața 1/N în afara eșantionului?",
                "options": [
                    "1/N are mereu cel mai mare raport Sharpe în teorie",
                    "Eroarea de estimare a randamentelor așteptate domină, iar optimizarea o amplifică",
                    "Medie-varianță ignoră varianțele",
                    "Datele din afara eșantionului sunt mereu mai calme"
                ],
                "correctExplanation": "Optimizatorul se încarcă pe activele cu media supraestimată; cu 60 de luni, un Sharpe de 1,57 în eșantion a devenit un Sharpe adevărat de 0,30.",
                "incorrectExplanation": "Teoria este corectă, dar intrările sunt zgomotoase: erorile randamentelor așteptate sunt amplificate de inversa matricei de covarianță."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "GARCH persistence",
                "text": "A GARCH(1,1) has alpha + beta = 0.99. What is the half-life of a volatility shock?",
                "options": [
                    "About 1 day",
                    "About 69 days",
                    "About 10 days",
                    "Infinite"
                ],
                "correctExplanation": "Half-life = ln 0.5 / ln 0.99 = 69 days.",
                "incorrectExplanation": "Shocks decay geometrically at rate alpha + beta; the half-life is ln 0.5 / ln(alpha + beta)."
            },
            "ro": {
                "title": "Persistența GARCH",
                "text": "Un GARCH(1,1) are alpha + beta = 0,99. Care este timpul de înjumătățire al unui șoc de volatilitate?",
                "options": [
                    "Aproximativ o zi",
                    "Aproximativ 69 de zile",
                    "Aproximativ 10 zile",
                    "Infinit"
                ],
                "correctExplanation": "Timpul de înjumătățire = ln 0,5 / ln 0,99 = 69 de zile.",
                "incorrectExplanation": "Șocurile scad geometric cu rata alpha + beta; timpul de înjumătățire este ln 0,5 / ln(alpha + beta)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Uncertainty of persistence",
                "text": "For the BET, the 95% CI of alpha + beta includes 1. What does that imply?",
                "options": [
                    "Volatility shocks disappear in one day",
                    "The GARCH model is misspecified and must be dropped",
                    "The half-life is very uncertain: from about a month to unbounded",
                    "The point estimate of the half-life is exact"
                ],
                "correctExplanation": "A persistence CI of [0.974, 1.007] maps to a half-life from 26 days to infinity.",
                "incorrectExplanation": "The half-life is a nonlinear function of alpha + beta; near 1, small changes in persistence mean huge changes in the half-life."
            },
            "ro": {
                "title": "Incertitudinea persistenței",
                "text": "Pentru BET, CI 95% al lui alpha + beta include valoarea 1. Ce implică asta?",
                "options": [
                    "Șocurile de volatilitate dispar într-o zi",
                    "Modelul GARCH este greșit specificat și trebuie abandonat",
                    "Timpul de înjumătățire este foarte incert: de la aproximativ o lună la nemărginit",
                    "Estimarea punctuală a timpului de înjumătățire este exactă"
                ],
                "correctExplanation": "Un CI al persistenței de [0,974; 1,007] corespunde unui timp de înjumătățire de la 26 de zile la infinit.",
                "incorrectExplanation": "Timpul de înjumătățire este o funcție neliniară de alpha + beta; aproape de 1, mici schimbări ale persistenței înseamnă schimbări uriașe ale timpului de înjumătățire."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Crisis correlations",
                "text": "Correlations rise in a crisis. Why is that not yet evidence of contagion?",
                "options": [
                    "Correlations cannot change over time",
                    "Crises reduce volatility",
                    "Contagion is defined as a fall in correlation",
                    "Correlation rises mechanically when the volatility of the source market rises; it must be adjusted"
                ],
                "correctExplanation": "The Forbes--Rigobon adjustment removes the volatility effect; in 2008 the adjusted increases were not significant.",
                "incorrectExplanation": "Higher volatility in the conditioning market inflates the measured correlation even when the dependence is unchanged."
            },
            "ro": {
                "title": "Corelații în criză",
                "text": "Corelațiile cresc în criză. De ce nu este aceasta încă o dovadă de contagiune?",
                "options": [
                    "Corelațiile nu se pot schimba în timp",
                    "Crizele reduc volatilitatea",
                    "Contagiunea se definește ca o scădere a corelației",
                    "Corelația crește mecanic când crește volatilitatea pieței-sursă; trebuie ajustată"
                ],
                "correctExplanation": "Ajustarea Forbes--Rigobon elimină efectul volatilității; în 2008 creșterile ajustate nu au fost semnificative.",
                "incorrectExplanation": "Volatilitatea mai mare a pieței de condiționare umflă corelația măsurată chiar dacă dependența nu s-a schimbat."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "VaR and ES",
                "text": "Which statement about VaR 1% and ES 2.5% is correct?",
                "options": [
                    "VaR is always larger than ES at the same level",
                    "ES ignores the tail beyond the quantile",
                    "ES is the average loss beyond the quantile and is subadditive; VaR is only the quantile",
                    "VaR is subadditive for every distribution"
                ],
                "correctExplanation": "ES averages the tail, so it sees how bad the bad days are, and it is coherent.",
                "incorrectExplanation": "VaR can fail subadditivity (two-bond example); ES at the same level is always at least as large as VaR."
            },
            "ro": {
                "title": "VaR și ES",
                "text": "Care afirmație despre VaR 1% și ES 2,5% este corectă?",
                "options": [
                    "VaR este mereu mai mare decât ES la același nivel",
                    "ES ignoră coada de dincolo de cuantilă",
                    "ES este pierderea medie dincolo de cuantilă și este subaditiv; VaR este doar cuantila",
                    "VaR este subaditiv pentru orice distribuție"
                ],
                "correctExplanation": "ES face media cozii, deci vede cât de rele sunt zilele rele, și este coerent.",
                "incorrectExplanation": "VaR poate încălca subaditivitatea (exemplul cu două obligațiuni); ES la același nivel este mereu cel puțin cât VaR."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Filtered historical simulation",
                "text": "What does filtered historical simulation (FHS) combine?",
                "options": [
                    "A GARCH volatility forecast with the empirical quantile of standardised residuals",
                    "A Normal distribution with a constant volatility",
                    "The largest loss in the sample with a safety factor",
                    "Implied volatility with the Student-t distribution"
                ],
                "correctExplanation": "VaR_t = -(mu + sigma_t * q_1%(z)): the filter adapts to volatility, the residual quantile keeps the heavy tail.",
                "incorrectExplanation": "FHS uses the conditional volatility from GARCH and the empirical distribution of the standardised residuals, not a parametric tail."
            },
            "ro": {
                "title": "Simularea istorică filtrată",
                "text": "Ce combină simularea istorică filtrată (FHS)?",
                "options": [
                    "O prognoză GARCH a volatilității cu cuantila empirică a reziduurilor standardizate",
                    "O distribuție Normală cu volatilitate constantă",
                    "Cea mai mare pierdere din eșantion cu un factor de siguranță",
                    "Volatilitatea implicită cu distribuția Student-t"
                ],
                "correctExplanation": "VaR_t = -(mu + sigma_t * q_1%(z)): filtrul se adaptează la volatilitate, cuantila reziduurilor păstrează coada groasă.",
                "incorrectExplanation": "FHS folosește volatilitatea condiționată din GARCH și distribuția empirică a reziduurilor standardizate, nu o coadă parametrică."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Kupiec test",
                "text": "A VaR 1% model has 6 breaches in 250 days. What does the Kupiec test say at 5%?",
                "options": [
                    "Coverage is rejected with p below 0.001",
                    "The model is in the red zone",
                    "Coverage is not rejected (p about 0.06), although the Basel zone is yellow",
                    "The test cannot be computed with 250 days"
                ],
                "correctExplanation": "LR_uc = 3.56, p = 0.059; 6 breaches fall in the Basel yellow zone (5-9).",
                "incorrectExplanation": "With 250 days the test has little power; Basel adds a capital multiplier in the yellow zone as a precaution."
            },
            "ro": {
                "title": "Testul Kupiec",
                "text": "Un model VaR 1% are 6 depășiri în 250 de zile. Ce spune testul Kupiec la 5%?",
                "options": [
                    "Acoperirea este respinsă cu p sub 0,001",
                    "Modelul este în zona roșie",
                    "Acoperirea nu este respinsă (p aproximativ 0,06), deși zona Basel este galbenă",
                    "Testul nu se poate calcula cu 250 de zile"
                ],
                "correctExplanation": "LR_uc = 3,56, p = 0,059; 6 depășiri cad în zona galbenă Basel (5-9).",
                "incorrectExplanation": "Cu 250 de zile testul are putere mică; Basel adaugă prudent un multiplicator de capital în zona galbenă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Independence of breaches",
                "text": "Why test the independence of VaR breaches, not only their number?",
                "options": [
                    "Breaches are always independent",
                    "The number of breaches is irrelevant for regulators",
                    "Clustered breaches mean the model reacts too slowly to volatility, even if the total is right",
                    "Independence tests replace coverage tests"
                ],
                "correctExplanation": "In the BET case study, HS had a nearly right count but failed independence: its breaches clustered in crises.",
                "incorrectExplanation": "Coverage and independence test different failures; the Christoffersen test adds the second."
            },
            "ro": {
                "title": "Independența depășirilor",
                "text": "De ce testăm independența depășirilor VaR, nu doar numărul lor?",
                "options": [
                    "Depășirile sunt mereu independente",
                    "Numărul depășirilor este irelevant pentru autorități",
                    "Depășirile grupate arată că modelul reacționează prea lent la volatilitate, chiar dacă totalul este corect",
                    "Testele de independență înlocuiesc testele de acoperire"
                ],
                "correctExplanation": "În studiul de caz BET, HS a avut un număr apropiat de cel corect, dar a picat testul de independență: depășirile s-au grupat în crize.",
                "incorrectExplanation": "Acoperirea și independența testează eșecuri diferite; testul Christoffersen îl adaugă pe al doilea."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Ranking ES forecasts",
                "text": "How can Expected Shortfall forecasts be ranked?",
                "options": [
                    "Alone, with the mean squared error",
                    "Alone, with any loss function",
                    "They cannot be compared at all",
                    "Jointly with VaR, using a consistent scoring function such as FZ0"
                ],
                "correctExplanation": "ES alone is not elicitable, but the pair (VaR, ES) is; FZ0 ranks it consistently.",
                "incorrectExplanation": "No scoring function ranks ES alone consistently; compare (VaR, ES) pairs with FZ0 and Diebold--Mariano tests."
            },
            "ro": {
                "title": "Clasificarea prognozelor ES",
                "text": "Cum pot fi clasificate prognozele de Expected Shortfall?",
                "options": [
                    "Singure, cu eroarea medie pătratică",
                    "Singure, cu orice funcție de pierdere",
                    "Nu pot fi comparate deloc",
                    "Împreună cu VaR, cu o funcție de scor consistentă precum FZ0"
                ],
                "correctExplanation": "ES singur nu este elicitabil, dar perechea (VaR, ES) este; FZ0 o clasifică în mod consistent.",
                "incorrectExplanation": "Nicio funcție de scor nu clasifică singur ES în mod consistent; comparați perechi (VaR, ES) cu FZ0 și teste Diebold--Mariano."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Look-ahead bias",
                "text": "A VaR model with parameters estimated on 2000-2026 is backtested on 2005-2026. What is wrong?",
                "options": [
                    "Nothing: more data always improves the backtest",
                    "It uses information that was not available at the forecast date, so its backtest looks better than reality",
                    "The backtest period is too long",
                    "GARCH cannot be estimated on 26 years"
                ],
                "correctExplanation": "In the BET case, full-sample parameters gave 1.31% breaches against 1.47% for the real-time version.",
                "incorrectExplanation": "Every forecast for day t must use only data up to t-1; full-sample estimates have already seen the crashes."
            },
            "ro": {
                "title": "Informația din viitor",
                "text": "Un model VaR cu parametri estimați pe 2000-2026 este testat pe 2005-2026. Ce este greșit?",
                "options": [
                    "Nimic: mai multe date îmbunătățesc mereu backtest-ul",
                    "Folosește informație care nu era disponibilă la data prognozei, deci backtest-ul arată mai bine decât realitatea",
                    "Perioada de backtest este prea lungă",
                    "GARCH nu poate fi estimat pe 26 de ani"
                ],
                "correctExplanation": "În cazul BET, parametrii din tot eșantionul au dat 1,31% depășiri, față de 1,47% pentru varianta în timp real.",
                "incorrectExplanation": "Orice prognoză pentru ziua t trebuie să folosească doar datele până la t-1; estimările pe tot eșantionul au văzut deja prăbușirile."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Realised variance",
                "text": "What is realised variance?",
                "options": [
                    "The variance of daily returns over a year",
                    "The square of the VIX",
                    "The GARCH forecast of tomorrow's variance",
                    "The sum of squared intraday returns over a day"
                ],
                "correctExplanation": "RV_t = sum of r_{t,i}^2 over the intraday intervals of day t; it measures that day's variance.",
                "incorrectExplanation": "RV is a measurement from high-frequency data, not a model forecast or an implied quantity."
            },
            "ro": {
                "title": "Varianța realizată",
                "text": "Ce este varianța realizată?",
                "options": [
                    "Varianța randamentelor zilnice pe un an",
                    "Pătratul VIX",
                    "Prognoza GARCH a varianței de mâine",
                    "Suma pătratelor randamentelor intraday dintr-o zi"
                ],
                "correctExplanation": "RV_t = suma r_{t,i}^2 pe intervalele intraday ale zilei t; măsoară varianța acelei zile.",
                "incorrectExplanation": "RV este o măsurătoare din date de frecvență înaltă, nu o prognoză de model sau o mărime implicită."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "QLIKE",
                "text": "Why is QLIKE preferred to MSE for comparing variance forecasts?",
                "options": [
                    "It ranks forecasts consistently with a noisy proxy and is less dominated by extreme days",
                    "It ignores the size of errors",
                    "It always gives smaller numbers",
                    "It does not need a proxy of the true variance"
                ],
                "correctExplanation": "Both are robust to proxy noise, but MSE is dominated by a few extreme days; QLIKE depends on the ratio RV/h.",
                "incorrectExplanation": "QLIKE = RV/h - ln(RV/h) - 1 penalises relative errors, so crisis days do not swamp the comparison."
            },
            "ro": {
                "title": "QLIKE",
                "text": "De ce este preferat QLIKE în locul MSE pentru compararea prognozelor de varianță?",
                "options": [
                    "Clasifică prognozele în mod consistent cu o aproximare zgomotoasă și este mai puțin dominat de zilele extreme",
                    "Ignoră mărimea erorilor",
                    "Dă mereu numere mai mici",
                    "Nu are nevoie de o aproximare a varianței adevărate"
                ],
                "correctExplanation": "Ambele sunt robuste la zgomotul aproximării, dar MSE este dominat de câteva zile extreme; QLIKE depinde de raportul RV/h.",
                "incorrectExplanation": "QLIKE = RV/h - ln(RV/h) - 1 penalizează erorile relative, deci zilele de criză nu domină comparația."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Amihud illiquidity",
                "text": "What does the Amihud ratio measure?",
                "options": [
                    "The bid-ask spread in basis points",
                    "The number of trades per day",
                    "The absolute return per unit of traded value: price impact of trading",
                    "The correlation of volume with volatility"
                ],
                "correctExplanation": "ILLIQ = average of |r_d| / traded value_d; Banca Transilvania was about 15,500 times less liquid than SPY by this measure.",
                "incorrectExplanation": "Amihud is a daily proxy for price impact, not a direct spread measure."
            },
            "ro": {
                "title": "Iliciditatea Amihud",
                "text": "Ce măsoară raportul Amihud?",
                "options": [
                    "Spread-ul bid-ask în puncte de bază",
                    "Numărul de tranzacții pe zi",
                    "Randamentul absolut pe unitatea de valoare tranzacționată: impactul tranzacțiilor asupra prețului",
                    "Corelația volumului cu volatilitatea"
                ],
                "correctExplanation": "ILLIQ = media lui |r_d| / valoarea tranzacționată_d; după această măsură, Banca Transilvania a fost de circa 15.500 de ori mai puțin lichidă decât SPY.",
                "incorrectExplanation": "Amihud este o aproximare zilnică a impactului asupra prețului, nu o măsură directă a spread-ului."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Geometric Brownian motion",
                "text": "Which stylised fact does geometric Brownian motion fail to reproduce?",
                "options": [
                    "Positive prices",
                    "Log returns that add up over time",
                    "A constant expected log return",
                    "Heavy tails and volatility clustering"
                ],
                "correctExplanation": "GBM implies Normal i.i.d. log returns; the S&P 500 has excess kurtosis 10.9 and clustered volatility.",
                "incorrectExplanation": "GBM keeps prices positive and log returns additive, but its constant volatility cannot create heavy tails or clustering."
            },
            "ro": {
                "title": "Mișcarea browniană geometrică",
                "text": "Ce fapt stilizat nu poate reproduce mișcarea browniană geometrică?",
                "options": [
                    "Prețurile pozitive",
                    "Randamentele log care se adună în timp",
                    "Un randament log așteptat constant",
                    "Cozile groase și grupările de volatilitate"
                ],
                "correctExplanation": "GBM implică randamente log Normale i.i.d.; S&P 500 are exces de kurtosis 10,9 și volatilitate grupată.",
                "incorrectExplanation": "GBM păstrează prețurile pozitive și randamentele log aditive, dar volatilitatea constantă nu poate crea cozi groase sau grupări."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Variance risk premium",
                "text": "What is the variance risk premium?",
                "options": [
                    "Realised variance minus the GARCH forecast",
                    "The difference between two stock indices",
                    "The premium of a call over a put",
                    "Implied variance minus the variance realised afterwards; positive on most days"
                ],
                "correctExplanation": "VRP_t = VIX_t^2 - RV_{t,t+21}; on the S&P 500 it was positive on 86% of days.",
                "incorrectExplanation": "Option buyers pay for protection, so implied variance usually exceeds the variance that follows, except in crashes."
            },
            "ro": {
                "title": "Prima de risc a varianței",
                "text": "Ce este prima de risc a varianței?",
                "options": [
                    "Varianța realizată minus prognoza GARCH",
                    "Diferența dintre doi indici bursieri",
                    "Prima unei opțiuni call față de un put",
                    "Varianța implicită minus varianța realizată ulterior; pozitivă în cele mai multe zile"
                ],
                "correctExplanation": "VRP_t = VIX_t^2 - RV_{t,t+21}; pentru S&P 500 a fost pozitivă în 86% din zile.",
                "incorrectExplanation": "Cumpărătorii de opțiuni plătesc pentru protecție, deci varianța implicită depășește de obicei varianța care urmează, cu excepția prăbușirilor."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Cross-validation in finance",
                "text": "Why can shuffled K-fold cross-validation mislead on financial time series?",
                "options": [
                    "Overlapping labels and serial dependence leak test information into training",
                    "It uses too little data",
                    "It always underestimates accuracy",
                    "It cannot be used with neural networks"
                ],
                "correctExplanation": "On pure noise, shuffled K-fold reported 69.4% accuracy; purging and an embargo remove the leak.",
                "incorrectExplanation": "Neighbouring observations share information; mixing them across folds lets the model see the test period."
            },
            "ro": {
                "title": "Validarea încrucișată în finanțe",
                "text": "De ce poate induce în eroare validarea încrucișată K-fold amestecată pe serii financiare?",
                "options": [
                    "Etichetele suprapuse și dependența serială aduc informație din setul de test în antrenare",
                    "Folosește prea puține date",
                    "Subestimează mereu acuratețea",
                    "Nu poate fi folosită cu rețele neuronale"
                ],
                "correctExplanation": "Pe zgomot pur, K-fold amestecat a raportat o acuratețe de 69,4%; purjarea și embargoul elimină scurgerea.",
                "incorrectExplanation": "Observațiile vecine au informație comună; amestecarea lor între fold-uri îi arată modelului perioada de test."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Foundation models",
                "text": "What did Chapter 14 find for zero-shot foundation models on SPY realised volatility?",
                "options": [
                    "They beat every benchmark by a wide margin",
                    "They tied with log-HAR: the QLIKE differences were not significant",
                    "They were worse than a random walk",
                    "They could not produce volatility forecasts"
                ],
                "correctExplanation": "Chronos-2 had QLIKE 0.231 against 0.234 for log-HAR; the Diebold--Mariano test did not separate them.",
                "incorrectExplanation": "New models must be judged against strong benchmarks with the tests of Chapter 8; here they matched but did not beat log-HAR."
            },
            "ro": {
                "title": "Modele fundaționale",
                "text": "Ce a arătat Capitolul 14 pentru modelele fundaționale zero-shot pe volatilitatea realizată SPY?",
                "options": [
                    "Au bătut toate reperele cu mult",
                    "Au egalat log-HAR: diferențele QLIKE nu au fost semnificative",
                    "Au fost mai slabe decât un mers aleator",
                    "Nu au putut produce prognoze de volatilitate"
                ],
                "correctExplanation": "Chronos-2 a avut QLIKE 0,231 față de 0,234 pentru log-HAR; testul Diebold--Mariano nu le-a separat.",
                "incorrectExplanation": "Modelele noi trebuie judecate față de repere puternice, cu testele din Capitolul 8; aici au egalat log-HAR, fără să-l bată."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "A good project question",
                "text": "Which is the best project question?",
                "options": [
                    "Is Bitcoin risky?",
                    "Does a boosting model beat log-HAR for next-day BET volatility in QLIKE, 2018-2026?",
                    "Can machine learning predict the market?",
                    "What is the best investment?"
                ],
                "correctExplanation": "It names one market, one target, one benchmark, one loss and one period: it is specific and testable.",
                "incorrectExplanation": "Vague or broad questions have no benchmark and no test; a good question can be answered with a hypothesis test."
            },
            "ro": {
                "title": "O întrebare bună de proiect",
                "text": "Care este cea mai bună întrebare de proiect?",
                "options": [
                    "Este Bitcoin riscant?",
                    "Bate un model de boosting modelul log-HAR pentru volatilitatea BET de a doua zi, în QLIKE, 2018-2026?",
                    "Poate machine learning să prezică piața?",
                    "Care este cea mai bună investiție?"
                ],
                "correctExplanation": "Numește o piață, o țintă, un reper, o funcție de pierdere și o perioadă: este specifică și testabilă.",
                "incorrectExplanation": "Întrebările vagi sau prea largi nu au reper și nici test; o întrebare bună poate primi răspuns printr-un test de ipoteză."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the error: an AI-written backtest",
                "text": "An AI assistant writes a VaR 1% backtest: var = -r.rolling(500).quantile(0.01); hit = (-r > var). It reports a breach rate below 1% and says the model is conservative. What is wrong?",
                "options": [
                    "The VaR for day t is computed from a window that already contains the return of day t (look-ahead); it must be shifted by one day, var.shift(1)",
                    "VaR 1% must be the 99% quantile of returns",
                    "A 500-day window is too long for historical simulation",
                    "The breaches should be counted on returns, not on losses"
                ],
                "correctExplanation": "The rolling quantile at t includes r_t, so a loss can breach only if it lies beyond the 1% quantile of a sample that includes it: breaches are under-counted. The forecast for day t must use data up to t - 1.",
                "incorrectExplanation": "The window length and the sign convention (loss = -r, VaR positive) are fine; the error is timing: the VaR used on day t already knows day t's return."
            },
            "ro": {
                "title": "Găsiți eroarea: un backtest scris de AI",
                "text": "Un asistent AI scrie un backtest pentru VaR 1%: var = -r.rolling(500).quantile(0.01); hit = (-r > var). Raportează o rată a depășirilor sub 1% și spune că modelul este prudent. Ce este greșit?",
                "options": [
                    "VaR-ul pentru ziua t este calculat pe o fereastră care conține deja randamentul zilei t (informație din viitor); trebuie decalat cu o zi, var.shift(1)",
                    "VaR 1% trebuie să fie cuantila 99% a randamentelor",
                    "O fereastră de 500 de zile este prea lungă pentru simularea istorică",
                    "Depășirile trebuie numărate pe randamente, nu pe pierderi"
                ],
                "correctExplanation": "Cuantila pe fereastra mobilă de la momentul t include r_t, deci o pierdere poate depăși doar dacă este dincolo de cuantila 1% a unui eșantion care o conține: depășirile sunt subnumărate. Prognoza pentru ziua t trebuie să folosească datele până la t - 1.",
                "incorrectExplanation": "Lungimea ferestrei și convenția de semn (pierderea = -r, VaR pozitiv) sunt corecte; eroarea este de moment: VaR-ul folosit în ziua t cunoaște deja randamentul zilei t."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "AI policy of the team project",
                "text": "Which practice follows the AI policy of the team project?",
                "options": [
                    "Using an AI assistant for code without declaring it, as long as the code runs",
                    "Keeping a reference suggested by an AI if the title and journal look plausible",
                    "Declaring every AI tool in AI_USE.md, logging at least three caught AI errors in AI_ERRORS.md and checking that every reference has a working DOI or link",
                    "Asking an AI assistant for help during the oral defence when a question is hard"
                ],
                "correctExplanation": "AI is allowed but must be declared in AI_USE.md; at least three caught errors go into AI_ERRORS.md; every reference must exist and have a working DOI or link; the oral defence is answered without AI.",
                "incorrectExplanation": "Undeclared AI use counts as plagiarism, an unchecked reference may not exist and counts as fabricated data, and no AI is allowed during the oral defence."
            },
            "ro": {
                "title": "Politica AI a proiectului de echipă",
                "text": "Ce practică respectă politica AI a proiectului de echipă?",
                "options": [
                    "Folosirea unui asistent AI pentru cod fără a o declara, atâta timp cât codul rulează",
                    "Păstrarea unei referințe sugerate de AI dacă titlul și revista par plauzibile",
                    "Declararea fiecărui instrument AI în AI_USE.md, notarea a cel puțin trei erori AI prinse în AI_ERRORS.md și verificarea că fiecare referință are un DOI sau link funcțional",
                    "Cererea de ajutor unui asistent AI în timpul susținerii orale, când o întrebare este grea"
                ],
                "correctExplanation": "AI-ul este permis, dar se declară în AI_USE.md; cel puțin trei erori prinse se notează în AI_ERRORS.md; fiecare referință trebuie să existe și să aibă un DOI sau link funcțional; la susținerea orală se răspunde fără AI.",
                "incorrectExplanation": "Utilizarea nedeclarată a AI este tratată ca plagiat, o referință neverificată poate să nu existe și este tratată ca date fabricate, iar la susținerea orală AI-ul nu este permis."
            }
        }
    ]
};

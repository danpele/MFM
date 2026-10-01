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
                "title": "The GRS null distribution",
                "text": "Under which assumptions is the GRS statistic of a factor model exactly F(N, T - N - K) distributed?",
                "options": [
                    "For any stationary return distribution",
                    "Whenever T is larger than N",
                    "With i.i.d. multivariate Normal errors, conditional on the factors",
                    "With HAC-robust errors"
                ],
                "correctExplanation": "The exact F distribution of Gibbons, Ross and Shanken needs i.i.d. multivariate Normal errors; with heavy tails or heteroskedasticity a GMM/HAC Wald or bootstrap version is needed.",
                "incorrectExplanation": "T > N alone does not even make the statistic computable: it needs T - N - K >= 1 and invertible covariance matrices; stationarity or HAC errors do not deliver the exact F distribution, which rests on i.i.d. Normal errors."
            },
            "ro": {
                "title": "Distribuția nulă GRS",
                "text": "În ce ipoteze are statistica GRS a unui model factorial exact distribuția F(N, T - N - K)?",
                "options": [
                    "Pentru orice distribuție staționară a randamentelor",
                    "Ori de câte ori T este mai mare decât N",
                    "Cu erori i.i.d. Normale multivariate, condiționat de factori",
                    "Cu erori robuste HAC"
                ],
                "correctExplanation": "Distribuția F exactă a lui Gibbons, Ross și Shanken cere erori i.i.d. Normale multivariate; cu cozi groase sau heteroscedasticitate este nevoie de o versiune Wald GMM/HAC sau bootstrap.",
                "incorrectExplanation": "T > N nu este suficient nici măcar pentru a calcula statistica: sunt necesare T - N - K >= 1 și matrici de covarianță inversabile; staționaritatea sau erorile HAC nu dau distribuția F exactă, care se bazează pe erori i.i.d. Normale."
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
                "incorrectExplanation": "Computing returns first and then joining gives the two assets different holding periods on Mondays and drops Bitcoin's weekend moves, which distorts variances, correlations and cumulative returns; the direction of the error depends on the sample (in the course's 2015-2026 data the cumulative return was understated)."
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
                "incorrectExplanation": "Calculul randamentelor înainte de join dă celor două active perioade de deținere diferite lunea și elimină mișcările Bitcoin din weekend, ceea ce distorsionează dispersiile, corelațiile și randamentele cumulate; direcția erorii depinde de eșantion (în datele cursului, 2015-2026, randamentul cumulat a fost subestimat)."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "An interval at the boundary",
                "text": "A Wald 95% interval for the GARCH persistence alpha + beta of the BET is [0.974, 1.007]. What is the main problem?",
                "options": [
                    "The parameter is near the boundary of the stationary region, so the symmetric Normal interval is unreliable; use a profile-likelihood or bootstrap interval restricted to the parameter space",
                    "The model must be an IGARCH",
                    "The standard errors are too large because of Student-t innovations",
                    "Nothing: the interval is exact"
                ],
                "correctExplanation": "Near alpha + beta = 1 the Normal approximation fails (Andrews, 1999); the profile-likelihood interval for the BET is [0.975, 1), a half-life of at least 27 days with no finite upper bound.",
                "incorrectExplanation": "An interval that leaves the parameter space signals that the Normal approximation does not hold there; it neither proves IGARCH nor is exact."
            },
            "ro": {
                "title": "Un interval la frontieră",
                "text": "Un interval Wald de 95% pentru persistența GARCH alpha + beta a BET este [0,974; 1,007]. Care este problema principală?",
                "options": [
                    "Parametrul este lângă frontiera regiunii staționare, deci intervalul Normal simetric nu este fiabil; folosiți un interval din verosimilitatea profil sau bootstrap, restrâns la spațiul parametrilor",
                    "Modelul trebuie să fie IGARCH",
                    "Erorile standard sunt prea mari din cauza inovațiilor Student-t",
                    "Nimic: intervalul este exact"
                ],
                "correctExplanation": "Lângă alpha + beta = 1 aproximarea Normală nu funcționează (Andrews, 1999); intervalul profil pentru BET este [0,975; 1), un timp de înjumătățire de cel puțin 27 de zile, fără limită superioară finită.",
                "incorrectExplanation": "Un interval care iese din spațiul parametrilor arată că aproximarea Normală nu este valabilă acolo; nu dovedește IGARCH și nici nu este exact."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Multiple testing",
                "text": "300 useless factors, with approximately independent and standard Normal t-statistics under the null, are each tested at |t| > 1.96. What happens?",
                "options": [
                    "About 15 are expected to look significant by chance, and the best one typically reaches |t| near 3",
                    "None looks significant",
                    "All of them look significant",
                    "Exactly one looks significant"
                ],
                "correctExplanation": "At 5% each, 300 independent tests give about 15 false discoveries in expectation, and the median of the maximum |t| is about 3.05; with strongly correlated tests the maximum would be much smaller.",
                "incorrectExplanation": "Each test has a 5% false-positive rate, so many tests produce false discoveries; this is why the factor literature asks for |t| > 3."
            },
            "ro": {
                "title": "Testare multiplă",
                "text": "300 de factori fără valoare, cu statistici t aproximativ independente și Normale standard sub ipoteza nulă, sunt testați fiecare la |t| > 1,96. Ce se întâmplă?",
                "options": [
                    "Circa 15 sunt de așteptat să pară semnificativi din întâmplare, iar cel mai bun ajunge de regulă la |t| aproape de 3",
                    "Niciunul nu pare semnificativ",
                    "Toți par semnificativi",
                    "Exact unul pare semnificativ"
                ],
                "correctExplanation": "La 5% fiecare, 300 de teste independente dau în medie circa 15 descoperiri false, iar mediana lui |t| maxim este în jur de 3,05; cu teste puternic corelate, maximul ar fi mult mai mic.",
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
                "text": "For the BET, the 95% interval for alpha + beta reaches the stationarity boundary. What does that imply for the half-life?",
                "options": [
                    "Volatility shocks disappear in one day",
                    "The GARCH model is misspecified and must be dropped",
                    "The half-life is very uncertain: from about a month to unbounded",
                    "The point estimate of the half-life is exact"
                ],
                "correctExplanation": "The profile-likelihood interval for alpha + beta is [0.975, 1): the half-life is at least about 27 days and has no finite upper bound.",
                "incorrectExplanation": "The half-life is a nonlinear function of alpha + beta; near 1, small changes in persistence mean huge changes in the half-life."
            },
            "ro": {
                "title": "Incertitudinea persistenței",
                "text": "Pentru BET, intervalul de 95% pentru alpha + beta ajunge la frontiera staționarității. Ce implică acest lucru pentru timpul de înjumătățire?",
                "options": [
                    "Șocurile de volatilitate dispar într-o zi",
                    "Modelul GARCH este greșit specificat și trebuie abandonat",
                    "Timpul de înjumătățire este foarte incert: de la aproximativ o lună la nemărginit",
                    "Estimarea punctuală a timpului de înjumătățire este exactă"
                ],
                "correctExplanation": "Intervalul din verosimilitatea profil pentru alpha + beta este [0,975; 1): timpul de înjumătățire este de cel puțin aproximativ 27 de zile și nu are o limită superioară finită.",
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
                "correctExplanation": "A model can have the right number of breaches and still cluster them in crises, which only an independence test detects. In the BET case study HS failed both: 79 breaches against about 54 expected (Kupiec p = 0.002) and clustered breaches (Christoffersen p < 0.001).",
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
                "correctExplanation": "Un model poate avea numărul corect de depășiri și totuși să le grupeze în crize, lucru pe care doar un test de independență îl detectează. În studiul de caz BET, HS a picat ambele teste: 79 de depășiri față de aproximativ 54 așteptate (Kupiec p = 0,002) și depășiri grupate (Christoffersen p < 0,001).",
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
                "title": "Look-ahead bias",
                "text": "Un model VaR cu parametri estimați pe 2000-2026 este supus backtesting-ului pe 2005-2026. Ce este greșit?",
                "options": [
                    "Nimic: mai multe date îmbunătățesc mereu backtest-ul",
                    "Folosește informație care nu era disponibilă la data prognozei, deci backtest-ul arată mai bine decât realitatea",
                    "Perioada de backtest este prea lungă",
                    "GARCH nu poate fi estimat pe 26 de ani"
                ],
                "correctExplanation": "În cazul BET, parametrii din tot eșantionul au dat 1,31% depășiri, față de 1,47% pentru varianta în timp real.",
                "incorrectExplanation": "Orice prognoză pentru ziua t trebuie să folosească doar datele până la t-1; estimările pe tot eșantionul au văzut deja crahurile."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "The power of Kupiec",
                "text": "With 250 days and a true breach rate of 2% for a VaR 1% model, how often does the 5% Kupiec test reject?",
                "options": [
                    "About 95% of the time",
                    "About one time in four",
                    "Exactly 5% of the time",
                    "About half of the time"
                ],
                "correctExplanation": "The rejection region is x = 0 or x >= 7; under Bin(250, 0.02) its probability is about 0.24: one year of data rarely detects a doubled breach rate.",
                "incorrectExplanation": "Power is not the confidence level and not the size of the test; doubling the breach rate still leaves only about five expected breaches, too few to reject reliably."
            },
            "ro": {
                "title": "Puterea testului Kupiec",
                "text": "Cu 250 de zile și o rată reală a depășirilor de 2% pentru un model VaR 1%, cât de des respinge testul Kupiec de 5%?",
                "options": [
                    "Aproximativ 95% din cazuri",
                    "Aproximativ o dată din patru",
                    "Exact 5% din cazuri",
                    "Aproximativ jumătate din cazuri"
                ],
                "correctExplanation": "Regiunea de respingere este x = 0 sau x >= 7; pentru Bin(250; 0,02) probabilitatea ei este aproximativ 0,24: un an de date detectează rar o rată a depășirilor dublată.",
                "incorrectExplanation": "Puterea nu este nivelul de încredere și nici nivelul testului; dublarea ratei lasă doar aproximativ cinci depășiri așteptate, prea puține pentru o respingere sigură."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "QLIKE",
                "text": "Why is QLIKE preferred to MSE for comparing variance forecasts?",
                "options": [
                    "With a conditionally unbiased proxy it ranks forecasts as the true variance would, and it is less dominated by extreme days",
                    "It ignores the size of errors",
                    "It always gives smaller numbers",
                    "It does not need a proxy of the true variance"
                ],
                "correctExplanation": "If the proxy (e.g. RV) is conditionally unbiased for the true variance, both MSE and QLIKE rank forecasts by expected loss as the true variance would (Patton, 2011); MSE is dominated by a few extreme days, while QLIKE depends only on the ratio RV/h. A biased proxy breaks the ranking for both.",
                "incorrectExplanation": "QLIKE = RV/h - ln(RV/h) - 1 penalises relative errors, so crisis days do not swamp the comparison; its robustness to proxy noise still requires a conditionally unbiased proxy."
            },
            "ro": {
                "title": "QLIKE",
                "text": "De ce este preferat QLIKE în locul MSE pentru compararea prognozelor de varianță?",
                "options": [
                    "Cu o aproximare condiționat nedeplasată ierarhizează prognozele la fel ca varianța adevărată și este mai puțin dominat de zilele extreme",
                    "Ignoră mărimea erorilor",
                    "Dă mereu numere mai mici",
                    "Nu are nevoie de o aproximare a varianței adevărate"
                ],
                "correctExplanation": "Dacă aproximarea (de exemplu RV) este condiționat nedeplasată pentru varianța adevărată, atât MSE, cât și QLIKE ierarhizează prognozele după pierderea așteptată la fel ca varianța adevărată (Patton, 2011); MSE este dominat de câteva zile extreme, iar QLIKE depinde doar de raportul RV/h. O aproximare deplasată strică ierarhia pentru ambele.",
                "incorrectExplanation": "QLIKE = RV/h - ln(RV/h) - 1 penalizează erorile relative, deci zilele de criză nu domină comparația; robustețea lui la zgomotul aproximării cere totuși o aproximare condiționat nedeplasată."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Comparing many risk models",
                "text": "Six VaR and ES models are compared on the same period. Which approach controls the risk of wrongly declaring one model best?",
                "options": [
                    "Pick the lowest average loss",
                    "Run a Kupiec test on each model",
                    "Compare the R-squared of the forecasts",
                    "A model confidence set on a consistent loss for (VaR, ES), such as FZ0"
                ],
                "correctExplanation": "The model confidence set (Hansen, Lunde and Nason, 2011) keeps all models not significantly worse than the best, controlling the family-wise error; FZ0 is consistent for the pair (VaR, ES).",
                "incorrectExplanation": "The lowest average loss ignores sampling error, Kupiec only checks coverage of one model, and R-squared is not a consistent score for tail risk."
            },
            "ro": {
                "title": "Compararea mai multor modele de risc",
                "text": "Șase modele VaR și ES sunt comparate pe aceeași perioadă. Ce abordare controlează riscul de a declara greșit un model drept cel mai bun?",
                "options": [
                    "Alegem cea mai mică pierdere medie",
                    "Rulăm un test Kupiec pentru fiecare model",
                    "Comparăm R-pătrat al prognozelor",
                    "Un set de modele de încredere pe o funcție de pierdere consistentă pentru (VaR, ES), de exemplu FZ0"
                ],
                "correctExplanation": "Setul de modele de încredere (Hansen, Lunde și Nason, 2011) păstrează toate modelele care nu sunt semnificativ mai slabe decât cel mai bun, controlând eroarea la nivel de familie; FZ0 este consistent pentru perechea (VaR, ES).",
                "incorrectExplanation": "Cea mai mică pierdere medie ignoră eroarea de eșantionare, Kupiec verifică doar acoperirea unui model, iar R-pătrat nu este un scor consistent pentru tail risk."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Identification of an event",
                "text": "Tail risk of the BET seems to fall after the 2020 FTSE upgrade. What would make this a credible effect of the upgrade?",
                "options": [
                    "A pre-specified comparison with a control market (difference-in-differences or synthetic control), placebo dates and a break test that locates the change near the event",
                    "A significant before/after t-test",
                    "A longer sample before 2020",
                    "A GARCH model estimated in each period"
                ],
                "correctExplanation": "One event needs a counterfactual: in the course data the difference-in-differences with WIG20 is not significant, placebo dates give similar changes and the sup-Wald break falls in November 2024.",
                "incorrectExplanation": "A before/after comparison, a longer sample or separate models cannot separate the event from everything else that changed at the same time."
            },
            "ro": {
                "title": "Identificarea unui eveniment",
                "text": "Tail risk-ul indicelui BET pare să scadă după reclasificarea FTSE din 2020. Ce ar face credibil un efect al reclasificării?",
                "options": [
                    "O comparație stabilită dinainte cu o piață de control (diferența în diferențe sau control sintetic), date placebo și un test de ruptură care plasează schimbarea lângă eveniment",
                    "Un test t semnificativ înainte/după",
                    "Un eșantion mai lung înainte de 2020",
                    "Un model GARCH estimat în fiecare perioadă"
                ],
                "correctExplanation": "Un singur eveniment cere un contrafactual: pe datele cursului, diferența în diferențe cu WIG20 nu este semnificativă, datele placebo dau schimbări similare, iar ruptura sup-Wald cade în noiembrie 2024.",
                "incorrectExplanation": "O comparație înainte/după, un eșantion mai lung sau modele separate nu pot separa evenimentul de tot ce s-a mai schimbat în același timp."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Variance risk premium",
                "text": "How is the variance risk premium measured ex post in the course?",
                "options": [
                    "Realised variance minus the GARCH forecast",
                    "The difference between two stock indices",
                    "The premium of a call over a put",
                    "Implied variance minus the variance realised afterwards; positive on most days"
                ],
                "correctExplanation": "The premium itself is E_Q[RV_{t,t+21}] - E_P[RV_{t,t+21}]; its ex-post measure is VRP_t = VIX_t^2 - RV_{t,t+21}, with both variances over the same 21-day horizon and in the same units (annualised, in %^2). It adds the forecast error of RV; on the S&P 500 it was positive on 86% of days.",
                "incorrectExplanation": "Option buyers pay for protection, so implied variance usually exceeds the variance that follows, except in crashes."
            },
            "ro": {
                "title": "Prima de risc a varianței",
                "text": "Cum se măsoară ex post prima de risc a varianței în curs?",
                "options": [
                    "Varianța realizată minus prognoza GARCH",
                    "Diferența dintre doi indici bursieri",
                    "Prima unei opțiuni call față de un put",
                    "Varianța implicită minus varianța realizată ulterior; pozitivă în cele mai multe zile"
                ],
                "correctExplanation": "Prima propriu-zisă este E_Q[RV_{t,t+21}] - E_P[RV_{t,t+21}]; măsura ei ex post este VRP_t = VIX_t^2 - RV_{t,t+21}, cu ambele varianțe pe același orizont de 21 de zile și în aceleași unități (anualizate, în %^2). Ea include și eroarea de prognoză a RV; pentru S&P 500 a fost pozitivă în 86% din zile.",
                "incorrectExplanation": "Cumpărătorii de opțiuni plătesc pentru protecție, deci varianța implicită depășește de obicei varianța care urmează, cu excepția crahurilor."
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
                    "Etichetele suprapuse și dependența serială produc leakage din setul de test în antrenare",
                    "Folosește prea puține date",
                    "Subestimează mereu acuratețea",
                    "Nu poate fi folosită cu rețele neuronale"
                ],
                "correctExplanation": "Pe zgomot pur, K-fold amestecat a raportat o acuratețe de 69,4%; purjarea și embargoul elimină leakage-ul.",
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
                    "No statistically significant QLIKE difference from log-HAR was detected",
                    "They were worse than a random walk",
                    "They could not produce volatility forecasts"
                ],
                "correctExplanation": "Chronos-2 had QLIKE 0.231 against 0.234 for log-HAR; the Diebold--Mariano test did not reject equal accuracy. This is not proof of equivalence, which would need a stated tolerance.",
                "incorrectExplanation": "New models must be judged against strong benchmarks with the tests of Chapter 8; here no significant difference from log-HAR was detected, so they did not beat it."
            },
            "ro": {
                "title": "Modele fundaționale",
                "text": "Ce a arătat Capitolul 14 pentru modelele fundaționale zero-shot pe volatilitatea realizată SPY?",
                "options": [
                    "Au bătut toate reperele cu mult",
                    "Nu s-a detectat o diferență QLIKE semnificativă statistic față de log-HAR",
                    "Au fost mai slabe decât un mers aleator",
                    "Nu au putut produce prognoze de volatilitate"
                ],
                "correctExplanation": "Chronos-2 a avut QLIKE 0,231 față de 0,234 pentru log-HAR; testul Diebold--Mariano nu a respins acuratețea egală. Aceasta nu dovedește echivalența, care ar cere o toleranță stabilită dinainte.",
                "incorrectExplanation": "Modelele noi trebuie judecate față de repere puternice, cu testele din Capitolul 8; aici nu s-a detectat o diferență semnificativă față de log-HAR, deci nu l-au bătut."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "A specification search",
                "text": "A team tries 48 combinations of window, lag and level and reports the best p = 0.01. What should they report instead?",
                "options": [
                    "Only the best specification",
                    "The median p-value without adjustment",
                    "The full specification curve and a multiplicity-adjusted p-value (Holm, Benjamini-Hochberg or a bootstrap reality check)",
                    "Only the specifications with p < 0.05, the others being misspecified"
                ],
                "correctExplanation": "With 48 tries a p-value of 0.01 is expected by chance; the specification curve shows the whole distribution and the correction accounts for the search.",
                "incorrectExplanation": "Reporting the best cell, an unadjusted summary or only the significant cells hides the search and inflates the evidence."
            },
            "ro": {
                "title": "O căutare printre specificații",
                "text": "O echipă încearcă 48 de combinații de fereastră, întârziere și nivel și raportează cea mai bună valoare p = 0,01. Ce ar trebui să raporteze în schimb?",
                "options": [
                    "Doar cea mai bună specificație",
                    "Valoarea p mediană, fără ajustare",
                    "Întreaga curbă a specificațiilor și o valoare p ajustată pentru testele multiple (Holm, Benjamini-Hochberg sau un bootstrap de tip reality check)",
                    "Doar specificațiile cu p < 0,05, celelalte fiind greșit specificate"
                ],
                "correctExplanation": "Din 48 de încercări, o valoare p de 0,01 apare din întâmplare; curba specificațiilor arată întreaga distribuție, iar corecția ține cont de căutare.",
                "incorrectExplanation": "Raportarea celei mai bune celule, a unui rezumat neajustat sau doar a celulelor semnificative ascunde căutarea și umflă dovezile."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the error: an AI-written backtest",
                "text": "An AI assistant writes a VaR 1% backtest: var = -r.rolling(500).quantile(0.01); hit = (-r > var). It reports a breach rate below 1% and says the model is conservative. What is wrong?",
                "options": [
                    "The VaR for day t is computed from a window that already contains the return of day t (look-ahead); it must be shifted by one day, var.shift(1), and the breach rate computed only on days that have a forecast",
                    "VaR 1% must be the 99% quantile of returns",
                    "A 500-day window is too long for historical simulation",
                    "The breaches should be counted on returns, not on losses"
                ],
                "correctExplanation": "The rolling quantile at t includes r_t, so a loss can breach only if it lies beyond the 1% quantile of a sample that includes it: breaches are under-counted. The forecast for day t must use data up to t - 1. Also, comparisons with the missing VaR of the first 500 days return False, so hit.mean() over all days understates the rate: keep only rows where var.shift(1) is not missing.",
                "incorrectExplanation": "The window length and the sign convention (loss = -r, VaR positive) are fine; the error is timing: the VaR used on day t already knows day t's return."
            },
            "ro": {
                "title": "Găsiți eroarea: un backtest scris de AI",
                "text": "Un asistent AI scrie un backtest pentru VaR 1%: var = -r.rolling(500).quantile(0.01); hit = (-r > var). Raportează o rată a depășirilor sub 1% și spune că modelul este prudent. Ce este greșit?",
                "options": [
                    "VaR-ul pentru ziua t este calculat pe o fereastră care conține deja randamentul zilei t (look-ahead bias); trebuie decalat cu o zi, var.shift(1), iar rata depășirilor calculată doar în zilele care au o prognoză",
                    "VaR 1% trebuie să fie cuantila 99% a randamentelor",
                    "O fereastră de 500 de zile este prea lungă pentru simularea istorică",
                    "Depășirile trebuie numărate pe randamente, nu pe pierderi"
                ],
                "correctExplanation": "Cuantila pe fereastra mobilă de la momentul t include r_t, deci o pierdere poate depăși doar dacă este dincolo de cuantila 1% a unui eșantion care o conține: depășirile sunt subnumărate. Prognoza pentru ziua t trebuie să folosească datele până la t - 1. În plus, comparațiile cu VaR-ul lipsă din primele 500 de zile dau False, deci hit.mean() pe toate zilele subestimează rata: păstrați doar rândurile în care var.shift(1) nu lipsește.",
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
                "incorrectExplanation": "Undeclared AI use counts as plagiarism; every reference must be checked, and a reference that does not exist counts as fabricated data; no AI is allowed during the oral defence."
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
                "incorrectExplanation": "Utilizarea nedeclarată a AI este tratată ca plagiat; fiecare referință trebuie verificată, iar o referință inexistentă este tratată ca date fabricate; la susținerea orală AI-ul nu este permis."
            }
        }
    ]
};

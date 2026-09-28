// ============================================================
// Quiz bank for chapter id 'bubbles': Bubbles and Crashes (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['bubbles'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "Rational bubble growth",
                "text": "In a rational bubble with required return r, how must the bubble component B_t grow in expectation?",
                "options": [
                    "At the dividend growth rate g",
                    "It must shrink over time",
                    "At the required return r: E_t[B_{t+1}] = (1 + r) B_t",
                    "It must stay constant"
                ],
                "correctExplanation": "No-arbitrage in the present-value model forces E_t[B_{t+1}] = (1 + r) B_t: investors hold the bubble only if it earns the required return.",
                "incorrectExplanation": "The bubble earns no dividend, so its expected growth must equal the required return r; any slower growth would make holders sell."
            },
            "ro": {
                "title": "Creșterea unei bule raționale",
                "text": "Într-o bulă rațională cu randamentul cerut r, cum trebuie să crească în medie componenta de bulă B_t?",
                "options": [
                    "Cu rata de creștere a dividendelor g",
                    "Trebuie să scadă în timp",
                    "Cu randamentul cerut r: E_t[B_{t+1}] = (1 + r) B_t",
                    "Trebuie să rămână constantă"
                ],
                "correctExplanation": "Condiția de nearbitraj din modelul valorii prezente impune E_t[B_{t+1}] = (1 + r) B_t: investitorii păstrează bula doar dacă aduce randamentul cerut.",
                "incorrectExplanation": "Bula nu plătește dividende, deci creșterea ei așteptată trebuie să fie egală cu randamentul cerut r; o creștere mai lentă i-ar face pe deținători să vândă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Blanchard-Watson bubble",
                "text": "A Blanchard-Watson bubble survives each period with probability 0.9. What is its expected lifetime?",
                "options": [
                    "10 periods",
                    "0.9 periods",
                    "1.1 periods",
                    "9 periods"
                ],
                "correctExplanation": "The number of periods until the collapse is geometric with success probability 1 - 0.9 = 0.1, so the expected lifetime is 1/0.1 = 10.",
                "incorrectExplanation": "The collapse probability per period is 0.1; the expected waiting time for the first collapse is its inverse, 10 periods."
            },
            "ro": {
                "title": "Bula Blanchard-Watson",
                "text": "O bulă Blanchard-Watson supraviețuiește în fiecare perioadă cu probabilitatea 0,9. Care este durata ei de viață așteptată?",
                "options": [
                    "10 perioade",
                    "0,9 perioade",
                    "1,1 perioade",
                    "9 perioade"
                ],
                "correctExplanation": "Numărul de perioade până la prăbușire urmează o distribuție geometrică cu probabilitatea 1 - 0,9 = 0,1, deci durata așteptată este 1/0,1 = 10.",
                "incorrectExplanation": "Probabilitatea de prăbușire pe perioadă este 0,1; timpul mediu până la prima prăbușire este inversul ei, 10 perioade."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Growth while the bubble survives",
                "text": "In the same bubble (survival probability 0.9, required return 6%), how fast does it grow in the periods it survives?",
                "options": [
                    "(1.06/0.9) - 1, about 17.8% per period",
                    "6% per period",
                    "0.9 x 6% = 5.4% per period",
                    "It does not grow"
                ],
                "correctExplanation": "The expected growth must be 6%: 0.9 x (1 + g) = 1.06, so the bubble grows by 1.06/0.9 - 1, about 17.8%, whenever it survives.",
                "incorrectExplanation": "The crash risk has to be compensated: conditional on survival the bubble must grow faster than r, by the factor (1 + r)/0.9."
            },
            "ro": {
                "title": "Creșterea cât timp bula supraviețuiește",
                "text": "În aceeași bulă (probabilitatea de supraviețuire 0,9, randamentul cerut 6%), cât de repede crește în perioadele în care supraviețuiește?",
                "options": [
                    "(1,06/0,9) - 1, aproximativ 17,8% pe perioadă",
                    "6% pe perioadă",
                    "0,9 x 6% = 5,4% pe perioadă",
                    "Nu crește"
                ],
                "correctExplanation": "Creșterea așteptată trebuie să fie 6%: 0,9 x (1 + g) = 1,06, deci bula crește cu 1,06/0,9 - 1, aproximativ 17,8%, de fiecare dată când supraviețuiește.",
                "incorrectExplanation": "Riscul de prăbușire trebuie compensat: condiționat de supraviețuire, bula trebuie să crească mai repede decât r, cu factorul (1 + r)/0,9."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Diba-Grossman argument",
                "text": "Why can a rational bubble not be negative (Diba and Grossman)?",
                "options": [
                    "Because dividends are always positive",
                    "Because regulators forbid it",
                    "Because volatility is always positive",
                    "Because a negative bubble growing at rate r would eventually push the price below zero, which free disposal rules out"
                ],
                "correctExplanation": "A negative bubble would grow in absolute value at rate r and drive the expected price below zero; limited liability and free disposal make that impossible.",
                "incorrectExplanation": "The argument uses the explosive growth of the bubble: a negative bubble would eventually imply a negative price, which cannot be an equilibrium."
            },
            "ro": {
                "title": "Argumentul Diba-Grossman",
                "text": "De ce nu poate fi negativă o bulă rațională (Diba și Grossman)?",
                "options": [
                    "Pentru că dividendele sunt mereu pozitive",
                    "Pentru că autoritățile o interzic",
                    "Pentru că volatilitatea este mereu pozitivă",
                    "Pentru că o bulă negativă care crește cu rata r ar împinge în cele din urmă prețul sub zero, ceea ce libera renunțare exclude"
                ],
                "correctExplanation": "O bulă negativă ar crește în valoare absolută cu rata r și ar duce prețul așteptat sub zero; răspunderea limitată și libera renunțare fac acest lucru imposibil.",
                "incorrectExplanation": "Argumentul folosește creșterea explozivă a bulei: o bulă negativă ar implica în cele din urmă un preț negativ, care nu poate fi un echilibru."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Right-tailed ADF",
                "text": "In the regression Delta y_t = a + b y_{t-1} + e_t on log prices, which alternative does a bubble test use?",
                "options": [
                    "b < 0 (stationarity)",
                    "b > 0 (explosive root)",
                    "b = 0 (unit root)",
                    "a > 0 (positive drift)"
                ],
                "correctExplanation": "Bubble tests reverse the usual unit-root test: the null is b = 0 and the alternative is b > 0, an explosive autoregressive root, so large positive t-statistics reject.",
                "incorrectExplanation": "The standard ADF test looks for stationarity (b < 0); bubble tests are right-tailed and look for explosive behaviour, b > 0."
            },
            "ro": {
                "title": "ADF la dreapta",
                "text": "În regresia Delta y_t = a + b y_{t-1} + e_t pe logaritmul prețului, ce ipoteză alternativă folosește un test de bulă?",
                "options": [
                    "b < 0 (staționaritate)",
                    "b > 0 (rădăcină explozivă)",
                    "b = 0 (rădăcină unitară)",
                    "a > 0 (derivă pozitivă)"
                ],
                "correctExplanation": "Testele de bulă inversează testul obișnuit de rădăcină unitară: ipoteza nulă este b = 0, iar alternativa b > 0, o rădăcină autoregresivă explozivă; respingem pentru valori t mari și pozitive.",
                "incorrectExplanation": "Testul ADF obișnuit caută staționaritate (b < 0); testele de bulă sunt la dreapta și caută un comportament exploziv, b > 0."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Evans critique",
                "text": "What did Evans (1991) show about periodically collapsing bubbles?",
                "options": [
                    "A full-sample unit-root test often fails to detect them, because the collapses make the series look mean-reverting",
                    "They make prices stationary in levels",
                    "They can only occur in cryptocurrencies",
                    "They are always detected by the Jarque-Bera test"
                ],
                "correctExplanation": "Collapses pull the price back repeatedly, so a single test on the whole sample looks for one explosive root and misses several short ones.",
                "incorrectExplanation": "The problem is power: one regression over the full sample averages explosive and collapsing phases, which motivates recursive and rolling windows."
            },
            "ro": {
                "title": "Critica lui Evans",
                "text": "Ce a arătat Evans (1991) despre bulele care se prăbușesc periodic?",
                "options": [
                    "Un test de rădăcină unitară pe toată selecția adesea nu le detectează, pentru că prăbușirile fac seria să pară că revine la medie",
                    "Fac prețurile staționare în nivel",
                    "Pot apărea doar la criptomonede",
                    "Sunt mereu detectate de testul Jarque-Bera"
                ],
                "correctExplanation": "Prăbușirile readuc prețul în jos de mai multe ori, așa că un singur test pe toată selecția caută o singură rădăcină explozivă și le ratează pe cele scurte.",
                "incorrectExplanation": "Problema este puterea testului: o regresie pe toată selecția amestecă fazele explozive cu prăbușirile, ceea ce motivează ferestrele recursive și mobile."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "SADF vs GSADF",
                "text": "What is the main difference between SADF (Phillips-Wu-Yu) and GSADF (Phillips-Shi-Yu)?",
                "options": [
                    "SADF uses weekly data, GSADF daily data",
                    "GSADF uses no critical values",
                    "SADF fixes the start of the window at the first observation; GSADF lets both start and end move",
                    "SADF allows lags, GSADF does not"
                ],
                "correctExplanation": "SADF takes the supremum over expanding windows starting at observation 1; GSADF also moves the start, which gives power against a second bubble after a collapse.",
                "incorrectExplanation": "Both are suprema of right-tailed ADF statistics; they differ in the set of windows: expanding only (SADF) versus all windows longer than the minimum (GSADF)."
            },
            "ro": {
                "title": "SADF vs GSADF",
                "text": "Care este diferența principală dintre SADF (Phillips-Wu-Yu) și GSADF (Phillips-Shi-Yu)?",
                "options": [
                    "SADF folosește date săptămânale, GSADF date zilnice",
                    "GSADF nu folosește valori critice",
                    "SADF fixează începutul ferestrei la prima observație; GSADF mută și începutul, și sfârșitul",
                    "SADF permite lag-uri, GSADF nu"
                ],
                "correctExplanation": "SADF ia supremul pe ferestre care cresc de la observația 1; GSADF mută și începutul, ceea ce îi dă putere împotriva unei a doua bule după o prăbușire.",
                "incorrectExplanation": "Ambele sunt supremuri ale statisticii ADF la dreapta; diferă prin mulțimea ferestrelor: doar ferestre care cresc (SADF) sau toate ferestrele mai lungi decât minimul (GSADF)."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Date-stamping in real time",
                "text": "The BSADF statistic at date t uses which observations?",
                "options": [
                    "Only observations up to t, over windows that end at t",
                    "All observations of the full sample",
                    "Only observations after t",
                    "One fixed window of 36 months"
                ],
                "correctExplanation": "BSADF at t is the supremum of ADF statistics over windows ending at t, so it uses information available at t and can be monitored in real time.",
                "incorrectExplanation": "Date-stamping compares BSADF at each t with its critical value; because the windows end at t, no future data are used."
            },
            "ro": {
                "title": "Datarea în timp real",
                "text": "Statistica BSADF la data t folosește ce observații?",
                "options": [
                    "Doar observațiile până la t, pe ferestre care se termină la t",
                    "Toate observațiile din selecție",
                    "Doar observațiile de după t",
                    "O singură fereastră fixă de 36 de luni"
                ],
                "correctExplanation": "BSADF la t este supremul statisticilor ADF pe ferestre care se termină la t, deci folosește informația disponibilă la t și poate fi urmărit în timp real.",
                "incorrectExplanation": "Datarea compară BSADF la fiecare t cu valoarea critică; fiindcă ferestrele se termină la t, nu se folosesc date din viitor."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Minimum window",
                "text": "With the Phillips-Shi-Yu rule r0 = 0.01 + 1.8/sqrt(T), what is the minimum window for T = 400 observations?",
                "options": [
                    "4 observations",
                    "94 observations",
                    "40 observations",
                    "200 observations"
                ],
                "correctExplanation": "r0 = 0.01 + 1.8/20 = 0.10, so the smallest window has 0.10 x 400 = 40 observations.",
                "incorrectExplanation": "Plug T = 400 into the rule: sqrt(400) = 20, 1.8/20 = 0.09, plus 0.01 gives 0.10 of the sample."
            },
            "ro": {
                "title": "Fereastra minimă",
                "text": "Cu regula Phillips-Shi-Yu r0 = 0,01 + 1,8/sqrt(T), care este fereastra minimă pentru T = 400 de observații?",
                "options": [
                    "4 observații",
                    "94 de observații",
                    "40 de observații",
                    "200 de observații"
                ],
                "correctExplanation": "r0 = 0,01 + 1,8/20 = 0,10, deci cea mai mică fereastră are 0,10 x 400 = 40 de observații.",
                "incorrectExplanation": "Înlocuim T = 400 în regulă: sqrt(400) = 20, 1,8/20 = 0,09, plus 0,01 dă 0,10 din selecție."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Critical values",
                "text": "Why are GSADF critical values obtained by simulation rather than from the standard Dickey-Fuller table?",
                "options": [
                    "Because GSADF is normally distributed",
                    "Because the statistic is a supremum over many overlapping windows, whose distribution depends on the sample size and the minimum window",
                    "Because the data are daily",
                    "Because the Dickey-Fuller table is only for bonds"
                ],
                "correctExplanation": "Taking the maximum over thousands of correlated ADF statistics shifts the distribution to the right; Monte Carlo under a random walk gives the finite-sample quantiles.",
                "incorrectExplanation": "A single ADF has the Dickey-Fuller distribution; the supremum over windows does not, so critical values are simulated for the given T and minimum window."
            },
            "ro": {
                "title": "Valorile critice",
                "text": "De ce valorile critice ale GSADF se obțin prin simulare și nu din tabelul Dickey-Fuller obișnuit?",
                "options": [
                    "Pentru că GSADF urmează distribuția Normală",
                    "Pentru că statistica este un suprem pe multe ferestre suprapuse, a cărui distribuție depinde de mărimea selecției și de fereastra minimă",
                    "Pentru că datele sunt zilnice",
                    "Pentru că tabelul Dickey-Fuller este doar pentru obligațiuni"
                ],
                "correctExplanation": "Maximul peste mii de statistici ADF corelate mută distribuția spre dreapta; simularea Monte Carlo sub un mers aleator dă cuantilele pentru selecția finită.",
                "incorrectExplanation": "Un singur ADF are distribuția Dickey-Fuller; supremul pe ferestre nu o are, așa că valorile critice se simulează pentru T și fereastra minimă date."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Changing volatility",
                "text": "Why do Harvey, Leybourne, Sollis and Taylor recommend a wild bootstrap for bubble tests?",
                "options": [
                    "Because it removes the need for data",
                    "Because shifts in volatility distort the size of the tests, and the wild bootstrap keeps the heteroskedasticity of the data",
                    "Because it makes the test two-sided",
                    "Because it estimates the critical time of the crash"
                ],
                "correctExplanation": "Monte Carlo critical values assume homoskedastic shocks; a wild bootstrap multiplies the observed changes by random signs, so the null keeps the data's volatility pattern.",
                "incorrectExplanation": "Volatility shifts, frequent in crypto and crisis periods, can create spurious rejections; resampling with random signs preserves them under the null."
            },
            "ro": {
                "title": "Volatilitatea variabilă",
                "text": "De ce recomandă Harvey, Leybourne, Sollis și Taylor un wild bootstrap pentru testele de bulă?",
                "options": [
                    "Pentru că elimină nevoia de date",
                    "Pentru că schimbările de volatilitate distorsionează pragul de semnificație al testelor, iar wild bootstrap păstrează heteroscedasticitatea datelor",
                    "Pentru că face testul bilateral",
                    "Pentru că estimează momentul critic al prăbușirii"
                ],
                "correctExplanation": "Valorile critice Monte Carlo presupun șocuri homoscedastice; wild bootstrap înmulțește variațiile observate cu semne aleatoare, deci ipoteza nulă păstrează tiparul de volatilitate al datelor.",
                "incorrectExplanation": "Schimbările de volatilitate, frecvente la cripto și în crize, pot produce respingeri false; reeșantionarea cu semne aleatoare le păstrează sub ipoteza nulă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Price-dividend ratio",
                "text": "Why test the price-dividend ratio instead of the price level for the S&P 500?",
                "options": [
                    "Because if dividends are I(1) and there is no bubble, the price-dividend ratio should not be explosive; explosiveness then points to the non-fundamental part",
                    "Because dividends are explosive",
                    "Because the price level is not observed",
                    "Because the ratio has no seasonality"
                ],
                "correctExplanation": "Fundamentals can grow fast; scaling by dividends removes that growth, so an explosive ratio is evidence against the fundamental value alone.",
                "incorrectExplanation": "An explosive price may reflect explosive fundamentals; the ratio controls for the dividend path, which is the point of using it."
            },
            "ro": {
                "title": "Raportul preț/dividend",
                "text": "De ce testăm raportul preț/dividend și nu nivelul prețului pentru S&P 500?",
                "options": [
                    "Pentru că, dacă dividendele sunt I(1) și nu există bulă, raportul preț/dividend nu ar trebui să fie exploziv; explozivitatea indică atunci partea nefundamentală",
                    "Pentru că dividendele sunt explozive",
                    "Pentru că nivelul prețului nu se observă",
                    "Pentru că raportul nu are sezonalitate"
                ],
                "correctExplanation": "Fundamentele pot crește rapid; împărțirea la dividende elimină această creștere, deci un raport exploziv este o dovadă împotriva explicației doar prin valoarea fundamentală.",
                "incorrectExplanation": "Un preț exploziv poate reflecta fundamente explozive; raportul controlează evoluția dividendelor, acesta este motivul pentru care îl folosim."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "LPPLS critical time",
                "text": "In the LPPLS model ln p(t) = A + B(tc - t)^m + C(tc - t)^m cos(omega ln(tc - t) - phi), what is tc?",
                "options": [
                    "The time of the last observation",
                    "The trading cost",
                    "The most probable time of the end of the bubble (the critical time)",
                    "The time constant of volatility"
                ],
                "correctExplanation": "tc is the finite-time singularity where the hazard rate of a crash peaks; the bubble ends at or near tc, by a crash or a slower transition.",
                "incorrectExplanation": "The model describes faster-than-exponential growth that ends at a critical time; tc is a parameter to estimate, not a data point."
            },
            "ro": {
                "title": "Momentul critic LPPLS",
                "text": "În modelul LPPLS ln p(t) = A + B(tc - t)^m + C(tc - t)^m cos(omega ln(tc - t) - phi), ce este tc?",
                "options": [
                    "Momentul ultimei observații",
                    "Costul de tranzacționare",
                    "Momentul cel mai probabil al sfârșitului bulei (momentul critic)",
                    "Constanta de timp a volatilității"
                ],
                "correctExplanation": "tc este singularitatea în timp finit la care rata de hazard a unei prăbușiri este maximă; bula se termină la sau aproape de tc, printr-o prăbușire sau o tranziție mai lentă.",
                "incorrectExplanation": "Modelul descrie o creștere mai rapidă decât exponențiala care se termină la un moment critic; tc este un parametru de estimat, nu o observație."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Filimonov-Sornette calibration",
                "text": "What does the Filimonov-Sornette reformulation of LPPLS achieve?",
                "options": [
                    "It removes the oscillations",
                    "It makes four parameters linear, so only tc, m and omega are searched nonlinearly",
                    "It guarantees the crash date",
                    "It turns the model into a GARCH"
                ],
                "correctExplanation": "Writing C cos(...) as C1 cos(omega ln(tc - t)) + C2 sin(omega ln(tc - t)) makes A, B, C1, C2 linear; given (tc, m, omega) they come from OLS.",
                "incorrectExplanation": "The reformulation reduces the nonlinear search from seven to three parameters, which makes the fit far more stable, but it does not fix the uncertainty about tc."
            },
            "ro": {
                "title": "Calibrarea Filimonov-Sornette",
                "text": "Ce aduce reformularea Filimonov-Sornette a modelului LPPLS?",
                "options": [
                    "Elimină oscilațiile",
                    "Face patru parametri liniari, astfel încât doar tc, m și omega se caută neliniar",
                    "Garantează data prăbușirii",
                    "Transformă modelul într-un GARCH"
                ],
                "correctExplanation": "Scriind C cos(...) ca C1 cos(omega ln(tc - t)) + C2 sin(omega ln(tc - t)), A, B, C1, C2 devin liniari; pentru (tc, m, omega) dați se obțin prin metoda celor mai mici pătrate.",
                "incorrectExplanation": "Reformularea reduce căutarea neliniară de la șapte la trei parametri, ceea ce face ajustarea mult mai stabilă, dar nu elimină incertitudinea despre tc."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Sign of B",
                "text": "For a positive (upward) bubble in the LPPLS model with 0 < m < 1, what sign must B have?",
                "options": [
                    "B < 0",
                    "B > 0",
                    "B = 0",
                    "Any sign"
                ],
                "correctExplanation": "With 0 < m < 1, (tc - t)^m falls as t approaches tc; the log price rises towards tc only if B < 0.",
                "incorrectExplanation": "The term B (tc - t)^m must increase over time for prices to accelerate upwards, which requires a negative B."
            },
            "ro": {
                "title": "Semnul lui B",
                "text": "Pentru o bulă pozitivă (în creștere) în modelul LPPLS cu 0 < m < 1, ce semn trebuie să aibă B?",
                "options": [
                    "B < 0",
                    "B > 0",
                    "B = 0",
                    "Orice semn"
                ],
                "correctExplanation": "Cu 0 < m < 1, (tc - t)^m scade când t se apropie de tc; logaritmul prețului crește spre tc doar dacă B < 0.",
                "incorrectExplanation": "Termenul B (tc - t)^m trebuie să crească în timp pentru ca prețul să accelereze în sus, ceea ce cere un B negativ."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Stability of tc",
                "text": "What did the rolling LPPLS fits in this chapter show about the estimated critical time?",
                "options": [
                    "It is stable across estimation dates",
                    "It always coincides with the actual peak",
                    "It moves as the estimation window ends later and often stays ahead of the current date until after the peak",
                    "It is always in the past"
                ],
                "correctExplanation": "For Bitcoin 2017 and the Nasdaq 100 in 2000, tc drifted with the end of the window; it locked onto the peak mostly after the peak had happened.",
                "incorrectExplanation": "A single fit can look impressive, but the estimate depends on the window; honest evaluation looks at the whole sequence of real-time fits."
            },
            "ro": {
                "title": "Stabilitatea lui tc",
                "text": "Ce au arătat ajustările LPPLS pe ferestre mobile din acest capitol despre momentul critic estimat?",
                "options": [
                    "Este stabil de la o dată de estimare la alta",
                    "Coincide mereu cu vârful real",
                    "Se mută pe măsură ce fereastra se termină mai târziu și rămâne adesea înaintea datei curente până după vârf",
                    "Este mereu în trecut"
                ],
                "correctExplanation": "Pentru Bitcoin în 2017 și Nasdaq 100 în 2000, tc s-a deplasat odată cu sfârșitul ferestrei; s-a fixat pe vârf mai ales după ce vârful avusese loc.",
                "incorrectExplanation": "O singură ajustare poate impresiona, dar estimarea depinde de fereastră; o evaluare onestă privește întreaga succesiune de ajustări în timp real."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "LPPLS confidence indicator",
                "text": "What is the LPPLS confidence indicator at date t2?",
                "options": [
                    "The R-squared of one LPPLS fit",
                    "The share of estimation windows ending at t2 whose fit passes the qualification filter",
                    "The probability of a crash tomorrow",
                    "The p-value of the GSADF test"
                ],
                "correctExplanation": "Many windows [t2 - L, t2] are fitted; the indicator is the fraction whose parameters are in the admissible ranges, a measure of how robust the bubble signal is.",
                "incorrectExplanation": "It aggregates many fits instead of trusting one, and it is computed with data up to t2 only."
            },
            "ro": {
                "title": "Indicatorul de încredere LPPLS",
                "text": "Ce este indicatorul de încredere LPPLS la data t2?",
                "options": [
                    "R-pătrat-ul unei ajustări LPPLS",
                    "Ponderea ferestrelor de estimare care se termină la t2 a căror ajustare trece filtrul de calificare",
                    "Probabilitatea unei prăbușiri mâine",
                    "Valoarea p a testului GSADF"
                ],
                "correctExplanation": "Se ajustează multe ferestre [t2 - L, t2]; indicatorul este fracția celor ai căror parametri sunt în intervalele admise, o măsură a robusteții semnalului de bulă.",
                "incorrectExplanation": "Agregă multe ajustări în loc să se bazeze pe una singură și se calculează doar cu datele până la t2."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Markov-switching durations",
                "text": "In a two-regime Markov-switching model the turbulent regime persists with probability 0.9 per week. What is its expected duration?",
                "options": [
                    "0.9 weeks",
                    "1.9 weeks",
                    "9 weeks",
                    "10 weeks"
                ],
                "correctExplanation": "The expected duration of a regime is 1/(1 - p_ii) = 1/0.1 = 10 weeks.",
                "incorrectExplanation": "Each week the regime ends with probability 0.1; the expected number of weeks until it ends is the inverse, 10."
            },
            "ro": {
                "title": "Duratele în modelul Markov-switching",
                "text": "Într-un model Markov-switching cu două regimuri, regimul turbulent persistă cu probabilitatea 0,9 pe săptămână. Care este durata lui așteptată?",
                "options": [
                    "0,9 săptămâni",
                    "1,9 săptămâni",
                    "9 săptămâni",
                    "10 săptămâni"
                ],
                "correctExplanation": "Durata așteptată a unui regim este 1/(1 - p_ii) = 1/0,1 = 10 săptămâni.",
                "incorrectExplanation": "În fiecare săptămână regimul se termină cu probabilitatea 0,1; numărul mediu de săptămâni până la sfârșit este inversul, 10."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Filtered vs smoothed",
                "text": "Which regime probability could an investor have used in real time?",
                "options": [
                    "The smoothed probability",
                    "Both equally",
                    "Neither",
                    "The filtered probability, which uses data up to t"
                ],
                "correctExplanation": "The filtered probability P(s_t | data up to t) is available at t; the smoothed one conditions on the whole sample, including the future.",
                "incorrectExplanation": "Smoothed probabilities look sharper because they use future data; for real-time decisions only the filtered probability is legitimate."
            },
            "ro": {
                "title": "Probabilitate filtrată vs netezită",
                "text": "Ce probabilitate de regim ar fi putut folosi un investitor în timp real?",
                "options": [
                    "Probabilitatea netezită",
                    "Ambele la fel",
                    "Niciuna",
                    "Probabilitatea filtrată, care folosește datele până la t"
                ],
                "correctExplanation": "Probabilitatea filtrată P(s_t | datele până la t) este disponibilă la t; cea netezită condiționează pe toată selecția, inclusiv pe viitor.",
                "incorrectExplanation": "Probabilitățile netezite par mai clare fiindcă folosesc date din viitor; pentru decizii în timp real doar probabilitatea filtrată este legitimă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Regimes in Bitcoin",
                "text": "In this chapter's two-regime model for weekly Bitcoin returns, how did the turbulent regime differ from the one for the Nasdaq 100?",
                "options": [
                    "It had a lower mean and was very persistent",
                    "It had zero volatility",
                    "It never occurred",
                    "It had a higher mean return as well as a higher volatility"
                ],
                "correctExplanation": "For the Nasdaq 100 the high-volatility regime has a negative mean; for Bitcoin the high-volatility regime also has the higher mean return: booms are turbulent too.",
                "incorrectExplanation": "In equities turbulence usually means falling prices; in Bitcoin the volatile regime contains both the booms and the crashes."
            },
            "ro": {
                "title": "Regimurile Bitcoin",
                "text": "În modelul cu două regimuri pentru randamentele săptămânale Bitcoin din acest capitol, prin ce s-a deosebit regimul turbulent de cel pentru Nasdaq 100?",
                "options": [
                    "Avea o medie mai mică și era foarte persistent",
                    "Avea volatilitate zero",
                    "Nu a apărut niciodată",
                    "Avea un randament mediu mai mare, pe lângă o volatilitate mai mare"
                ],
                "correctExplanation": "Pentru Nasdaq 100, regimul cu volatilitate mare are o medie negativă; pentru Bitcoin, regimul cu volatilitate mare are și randamentul mediu mai mare: și perioadele de creștere sunt turbulente.",
                "incorrectExplanation": "La acțiuni, turbulența înseamnă de obicei prețuri în scădere; la Bitcoin, regimul volatil conține atât creșterile rapide, cât și prăbușirile."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Bubbles for Fama",
                "text": "What do sharp industry run-ups predict, according to Greenwood, Shleifer and You and to this chapter's replication on 49 industries?",
                "options": [
                    "A certain crash within two years",
                    "Lower volatility",
                    "A higher probability of a 40% crash, but not a significantly negative average return",
                    "Nothing at all"
                ],
                "correctExplanation": "Run-ups of more than 100% raise the crash probability well above the unconditional rate, while the average subsequent return stays positive: run-ups are not a sell signal on their own.",
                "incorrectExplanation": "The evidence is about crash probability, not about predictable losses on average; many run-ups keep going."
            },
            "ro": {
                "title": "Bubbles for Fama",
                "text": "Ce prezic creșterile bruște ale unei industrii, după Greenwood, Shleifer și You și după replicarea din acest capitol pe 49 de industrii?",
                "options": [
                    "O prăbușire sigură în doi ani",
                    "O volatilitate mai mică",
                    "O probabilitate mai mare a unei scăderi de 40%, dar nu un randament mediu semnificativ negativ",
                    "Nimic"
                ],
                "correctExplanation": "Creșterile de peste 100% ridică probabilitatea unei prăbușiri mult peste rata necondiționată, în timp ce randamentul mediu ulterior rămâne pozitiv: creșterile nu sunt singure un semnal de vânzare.",
                "incorrectExplanation": "Dovezile privesc probabilitatea de prăbușire, nu pierderi previzibile în medie; multe creșteri continuă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Explosive price vs bubble",
                "text": "The GSADF test flags NVIDIA's price as explosive. What is the main caveat before calling it a bubble?",
                "options": [
                    "The test cannot be applied to stocks",
                    "NVIDIA has no volatility",
                    "The test only works on indices",
                    "Explosive prices can also come from explosive fundamentals, such as fast-growing earnings, so the test on prices alone does not separate the two"
                ],
                "correctExplanation": "The test detects explosive dynamics; whether they are fundamental or speculative needs a fundamentals-adjusted series such as a price-earnings or price-dividend ratio.",
                "incorrectExplanation": "Explosiveness is necessary for a rational bubble but not sufficient evidence of one; fundamentals can also accelerate."
            },
            "ro": {
                "title": "Preț exploziv vs bulă",
                "text": "Testul GSADF semnalează prețul NVIDIA ca exploziv. Care este principala rezervă înainte de a-l numi bulă?",
                "options": [
                    "Testul nu se poate aplica acțiunilor",
                    "NVIDIA nu are volatilitate",
                    "Testul funcționează doar pe indici",
                    "Prețurile explozive pot veni și din fundamente explozive, de exemplu profituri în creștere rapidă, deci testul pe preț singur nu le separă"
                ],
                "correctExplanation": "Testul detectează o dinamică explozivă; dacă este fundamentală sau speculativă cere o serie ajustată pentru fundamente, de exemplu un raport preț/profit sau preț/dividend.",
                "incorrectExplanation": "Explozivitatea este necesară pentru o bulă rațională, dar nu este o dovadă suficientă; și fundamentele pot accelera."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Speculative disagreement",
                "text": "In Scheinkman and Xiong's model, where does the bubble come from?",
                "options": [
                    "From rational growth at rate r",
                    "From central bank policy",
                    "From dividend taxes",
                    "From overconfident investors who disagree and cannot short, so the price includes the option to resell to a more optimistic buyer"
                ],
                "correctExplanation": "With short-sale constraints and heterogeneous beliefs, owners value the option to sell to someone more optimistic; this resale option is the bubble, and it comes with high trading volume.",
                "incorrectExplanation": "The mechanism is disagreement plus short-sale constraints, which also explains why bubbles come with heavy trading."
            },
            "ro": {
                "title": "Dezacordul speculativ",
                "text": "În modelul lui Scheinkman și Xiong, de unde vine bula?",
                "options": [
                    "Din creșterea rațională cu rata r",
                    "Din politica băncii centrale",
                    "Din impozitarea dividendelor",
                    "De la investitori prea încrezători care nu sunt de acord între ei și nu pot vinde în lipsă, deci prețul include opțiunea de a revinde unui cumpărător mai optimist"
                ],
                "correctExplanation": "Cu restricții la vânzarea în lipsă și convingeri diferite, deținătorii prețuiesc opțiunea de a vinde cuiva mai optimist; această opțiune de revânzare este bula și vine cu volume mari de tranzacționare.",
                "incorrectExplanation": "Mecanismul este dezacordul plus restricțiile la vânzarea în lipsă, ceea ce explică și de ce bulele vin cu tranzacționare intensă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Real-time lesson",
                "text": "Across the Nasdaq 100 (2000), Bitcoin (2017) and GameStop (2021), what did real-time BSADF date-stamping deliver?",
                "options": [
                    "An exact prediction of the crash date",
                    "An early warning that prices were explosive, often months before the peak, but no timing of the collapse",
                    "No signal before the crash",
                    "A signal only after the crash"
                ],
                "correctExplanation": "The signal typically started well before the peak and ended after it; the tests say that the market is in an explosive phase, not when it will end.",
                "incorrectExplanation": "Explosiveness tests are monitoring tools: useful for risk management, not a timing device for the crash."
            },
            "ro": {
                "title": "Lecția timpului real",
                "text": "Pentru Nasdaq 100 (2000), Bitcoin (2017) și GameStop (2021), ce a oferit datarea BSADF în timp real?",
                "options": [
                    "O predicție exactă a datei prăbușirii",
                    "Un avertisment timpuriu că prețurile erau explozive, adesea cu luni înainte de vârf, dar nu momentul prăbușirii",
                    "Niciun semnal înainte de prăbușire",
                    "Un semnal doar după prăbușire"
                ],
                "correctExplanation": "Semnalul a început de obicei mult înaintea vârfului și s-a încheiat după el; testele spun că piața este într-o fază explozivă, nu când se va termina.",
                "incorrectExplanation": "Testele de explozivitate sunt instrumente de monitorizare: utile pentru gestiunea riscului, nu un mijloc de a anticipa momentul prăbușirii."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the error: SADF critical value",
                "text": "An AI assistant computes SADF on a log price series, gets SADF = 0.40, compares it with the 5% critical value returned by statsmodels' adfuller (-2.86) and concludes: 'SADF > -2.86, so there is a bubble'. What is wrong?",
                "options": [
                    "Nothing: any SADF above -2.86 indicates explosive behaviour",
                    "It uses a left-tailed Dickey-Fuller critical value for a right-tailed test; the SADF critical value is positive and must be simulated (or bootstrapped) for the same sample size and minimum window",
                    "SADF should be compared with the Normal quantile 1.645",
                    "SADF must be run on returns, not on log prices"
                ],
                "correctExplanation": "Explosiveness is the right tail. The Dickey-Fuller value -2.86 belongs to the left-tailed test of stationarity, so with it almost every random walk is declared a bubble; the right-tailed SADF critical value is positive (about 1.4 for 300 observations) and comes from simulation.",
                "incorrectExplanation": "The test is right-tailed and the SADF statistic has a non-standard distribution: its critical value must be simulated under a random walk with the same sample size and minimum window, and it is positive, not -2.86."
            },
            "ro": {
                "title": "Găsiți eroarea: valoarea critică SADF",
                "text": "Un asistent AI calculează SADF pe o serie de log-prețuri, obține SADF = 0,40, o compară cu valoarea critică de 5% întoarsă de adfuller din statsmodels (-2,86) și conchide: „SADF > -2,86, deci există o bulă”. Ce este greșit?",
                "options": [
                    "Nimic: orice SADF peste -2,86 indică un comportament exploziv",
                    "Folosește o valoare critică Dickey-Fuller pentru coada stângă la un test la dreapta; valoarea critică SADF este pozitivă și trebuie simulată (sau obținută prin bootstrap) pentru aceeași dimensiune a eșantionului și aceeași fereastră minimă",
                    "SADF trebuie comparat cu cuantila 1,645 a distribuției Normale",
                    "SADF trebuie aplicat pe randamente, nu pe log-prețuri"
                ],
                "correctExplanation": "Explozivitatea este coada dreaptă. Valoarea Dickey-Fuller -2,86 aparține testului pe coada stângă pentru staționaritate, deci cu ea aproape orice mers aleator este declarat bulă; valoarea critică SADF la dreapta este pozitivă (circa 1,4 pentru 300 de observații) și se obține prin simulare.",
                "incorrectExplanation": "Testul este la dreapta, iar statistica SADF are o distribuție nestandard: valoarea ei critică se simulează sub un mers aleator cu aceeași dimensiune a eșantionului și aceeași fereastră minimă și este pozitivă, nu -2,86."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the error: one LPPLS critical time",
                "text": "An AI assistant fits an LPPLS model on the last 36 months of an index and answers: 'The critical time is t_c = March 2027, so the bubble will burst in March 2027.' What is the main problem with this answer?",
                "options": [
                    "LPPLS cannot be fitted on monthly data",
                    "The critical time should be reported in days, not months",
                    "The fit should use prices, not log prices",
                    "One window gives one fragile estimate: t_c must be reported with its dispersion across windows and the confidence indicator, and it marks the likely end of the regime, not a certain crash date"
                ],
                "correctExplanation": "The LPPLS critical time is very sensitive to the window and to the filter. A credible answer refits over many windows, reports the dispersion of t_c and the share of qualifying fits (the confidence indicator), and treats t_c as a probabilistic end of the regime.",
                "incorrectExplanation": "The problem is not the data frequency or the units: a single-window t_c is not robust, and LPPLS does not promise a crash at t_c; report its dispersion across windows and the confidence indicator."
            },
            "ro": {
                "title": "Găsiți eroarea: un singur moment critic LPPLS",
                "text": "Un asistent AI ajustează un model LPPLS pe ultimele 36 de luni ale unui indice și răspunde: „Momentul critic este t_c = martie 2027, deci bula se va sparge în martie 2027.” Care este principala problemă a acestui răspuns?",
                "options": [
                    "LPPLS nu poate fi ajustat pe date lunare",
                    "Momentul critic trebuie raportat în zile, nu în luni",
                    "Ajustarea trebuie făcută pe prețuri, nu pe log-prețuri",
                    "O singură fereastră dă o estimare fragilă: t_c trebuie raportat cu dispersia lui pe ferestre și cu indicatorul de încredere și marchează sfârșitul probabil al regimului, nu o dată sigură a crahului"
                ],
                "correctExplanation": "Momentul critic LPPLS este foarte sensibil la fereastră și la filtru. Un răspuns credibil reajustează modelul pe multe ferestre, raportează dispersia lui t_c și ponderea ajustărilor valide (indicatorul de încredere) și tratează t_c ca sfârșit probabil al regimului.",
                "incorrectExplanation": "Problema nu este frecvența datelor sau unitatea de măsură: un t_c dintr-o singură fereastră nu este robust, iar LPPLS nu promite un crah la t_c; raportați dispersia lui pe ferestre și indicatorul de încredere."
            }
        }
    ]
};

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
                "correctExplanation": "In the present-value model with a constant required return r (a model assumption, not implied by no-arbitrage alone), the pricing equation forces E_t[B_{t+1}] = (1 + r) B_t: investors hold the bubble only if it earns the required return.",
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
                "correctExplanation": "În modelul valorii prezente cu randament cerut constant r (o ipoteză a modelului, nu o consecință doar a nearbitrajului), ecuația de preț impune E_t[B_{t+1}] = (1 + r) B_t: investitorii păstrează bula doar dacă aduce randamentul cerut.",
                "incorrectExplanation": "Bula nu plătește dividende, deci creșterea ei așteptată trebuie să fie egală cu randamentul cerut r; o creștere mai lentă i-ar face pe deținători să vândă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Null limit of SADF",
                "text": "Under the same homoskedastic random-walk null, lag specification and deterministic terms, why can SADF critical values simulated for one sample size T and minimum window r0 be reused for series with different innovation variances?",
                "options": [
                    "Because SADF is asymptotically Normal",
                    "Because the critical values depend on the variance of the data, which simulation matches",
                    "Because under the unit-root null the statistic converges to a functional of standard Brownian motion that depends only on r0 and the deterministic terms",
                    "Because the ADF lags remove all dependence in the data"
                ],
                "correctExplanation": "Under a random walk with an asymptotically negligible drift, each window ADF converges to a ratio of Brownian functionals in which sigma cancels; SADF and GSADF are suprema of that functional, so their quantiles depend only on r0 (and the constant/drift specification).",
                "incorrectExplanation": "The limit is pivotal but non-standard: sigma and the drift drop out, and the supremum over windows is not Normal. This is an asymptotic argument under constant variance; with volatility shifts the finite-sample size is distorted and the wild bootstrap is needed."
            },
            "ro": {
                "title": "Limita SADF sub ipoteza nulă",
                "text": "Sub aceeași ipoteză nulă de mers aleator homoscedastic, aceeași specificare a întârzierilor și aceiași termeni determiniști, de ce valorile critice SADF simulate pentru o mărime a eșantionului T și o fereastră minimă r0 pot fi refolosite pentru serii cu dispersii diferite ale șocurilor?",
                "options": [
                    "Pentru că SADF are asimptotic distribuția Normală",
                    "Pentru că valorile critice depind de dispersia datelor, pe care simularea o reproduce",
                    "Pentru că sub ipoteza nulă a rădăcinii unitare statistica tinde la o funcțională a mișcării browniene standard care depinde doar de r0 și de termenii determiniști",
                    "Pentru că întârzierile ADF elimină orice dependență din date"
                ],
                "correctExplanation": "Sub un mers aleator cu drift asimptotic neglijabilă, fiecare ADF pe fereastră tinde la un raport de funcționale browniene în care sigma se simplifică; SADF și GSADF sunt supremuri ale acestei funcționale, deci cuantilele lor depind doar de r0 (și de specificarea termenului liber/drift-ului).",
                "incorrectExplanation": "Limita este pivotală, dar nestandard: sigma și drift-ul dispar, iar supremul pe ferestre nu urmează distribuția Normală. Argumentul este asimptotic și presupune dispersie constantă; la schimbări de volatilitate nivelul în eșantioane finite este distorsionat și este nevoie de wild bootstrap."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Mildly explosive alternative",
                "text": "Under rho_T = 1 + c/k_T with c > 0, k_T -> infinity and k_T = o(T), what happens to the right-tailed ADF t-ratio as T grows?",
                "options": [
                    "It converges to the Dickey-Fuller distribution",
                    "It diverges to plus infinity, so the right-tailed test is consistent",
                    "It converges to N(0, 1)",
                    "It diverges to minus infinity"
                ],
                "correctExplanation": "Phillips and Magdalinos show that (rho_T^T/(rho_T^2 - 1))(rho_hat - rho_T) has a Cauchy limit; the estimator converges so fast that the t-ratio of rho - 1 grows like rho_T^T, so power tends to one.",
                "incorrectExplanation": "A mildly explosive root is not local to unity: the estimation error vanishes at rate k_T rho_T^T while the deviation c/k_T stays, so the t-ratio explodes upwards, not towards a fixed distribution."
            },
            "ro": {
                "title": "Alternativa ușor explozivă",
                "text": "Sub rho_T = 1 + c/k_T cu c > 0, k_T -> infinit și k_T = o(T), ce se întâmplă cu raportul t ADF la dreapta când T crește?",
                "options": [
                    "Tinde la distribuția Dickey-Fuller",
                    "Diverge la plus infinit, deci testul la dreapta este consistent",
                    "Tinde la N(0, 1)",
                    "Diverge la minus infinit"
                ],
                "correctExplanation": "Phillips și Magdalinos arată că (rho_T^T/(rho_T^2 - 1))(rho_hat - rho_T) are o limită Cauchy; estimatorul converge atât de repede încât raportul t al lui rho - 1 crește ca rho_T^T, deci puterea tinde la unu.",
                "incorrectExplanation": "O rădăcină ușor explozivă nu este local-unitară: eroarea de estimare dispare cu viteza k_T rho_T^T, iar abaterea c/k_T rămâne, deci raportul t explodează în sus, nu tinde la o distribuție fixă."
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
            "correct": 3,
            "en": {
                "title": "Date-stamping multiplicity",
                "text": "BSADF is compared with its pointwise 95% critical value at each of 400 dates of a series with no bubble. What is the risk?",
                "options": [
                    "None: each comparison has size 5%, so the whole procedure has size 5%",
                    "The minimum-duration rule makes the family-wise error exactly 5%",
                    "The risk exists only for weekly data",
                    "The probability of at least one false episode over the sample is far above 5%; use family-wise (bootstrap sup-over-window) critical values or a slowly increasing critical value"
                ],
                "correctExplanation": "Hundreds of dependent 5% tests almost surely produce some crossing; in this chapter's simulation about half of the random-walk paths contain a false date-stamped episode. Phillips and Shi bootstrap the maximum of BSADF over a window to control the family-wise error; PSY's consistency theory lets the critical value grow slowly.",
                "incorrectExplanation": "Pointwise control is not family-wise control: the chance of at least one false alarm grows with the monitoring length, and the minimum duration reduces it but does not bring it back to 5%."
            },
            "ro": {
                "title": "Multiplicitatea în datare",
                "text": "BSADF este comparat cu valoarea critică punctuală de 95% la fiecare dintre cele 400 de date ale unei serii fără bulă. Care este riscul?",
                "options": [
                    "Niciunul: fiecare comparație are nivelul 5%, deci întreaga procedură are nivelul 5%",
                    "Regula duratei minime face eroarea pe familie exact 5%",
                    "Riscul există doar pentru datele săptămânale",
                    "Probabilitatea a cel puțin unui episod fals pe selecție este mult peste 5%; folosiți valori critice pe familie (bootstrap pentru supremul pe fereastră) sau o valoare critică ce crește lent"
                ],
                "correctExplanation": "Sute de teste dependente la 5% produc aproape sigur o depășire; în simularea din acest capitol, aproximativ jumătate dintre mersurile aleatoare conțin un episod datat fals. Phillips și Shi fac bootstrap pentru maximul BSADF pe o fereastră ca să controleze eroarea pe familie; teoria de consistență PSY lasă valoarea critică să crească lent.",
                "incorrectExplanation": "Controlul punctual nu este control pe familie: șansa a cel puțin unei alarme false crește cu lungimea monitorizării, iar durata minimă o reduce, dar nu o readuce la 5%."
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
                    "Un test de rădăcină unitară pe toată selecția adesea nu le detectează, pentru că colapsurile fac seria să pară că revine la medie",
                    "Fac prețurile staționare în nivel",
                    "Pot apărea doar la criptomonede",
                    "Sunt mereu detectate de testul Jarque-Bera"
                ],
                "correctExplanation": "Colapsurile readuc prețul în jos de mai multe ori, așa că un singur test pe toată selecția caută o singură rădăcină explozivă și le ratează pe cele scurte.",
                "incorrectExplanation": "Problema este puterea testului: o regresie pe toată selecția amestecă fazele explozive cu colapsurile, ceea ce motivează ferestrele recursive și mobile."
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
                "correctExplanation": "SADF ia supremul pe ferestre care cresc de la observația 1; GSADF mută și începutul, ceea ce îi dă putere împotriva unei a doua bule după un colaps.",
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
            "correct": 0,
            "en": {
                "title": "Size under a volatility shift",
                "text": "A series has no explosive root, but its volatility triples in mid-sample. What does GSADF with Monte Carlo critical values simulated under constant variance do?",
                "options": [
                    "It over-rejects, flagging spurious explosiveness; a wild bootstrap that keeps the variance path restores roughly correct size",
                    "It always under-rejects",
                    "Its size stays exactly 5%",
                    "The shift only lowers power; size is unaffected"
                ],
                "correctExplanation": "High variance in the recent windows inflates the supremum of the window ADF statistics; in this chapter's Monte Carlo the rejection rate was about 32% instead of 5%, and about 4% with the wild bootstrap (Harvey, Leybourne, Sollis and Taylor).",
                "incorrectExplanation": "The null distribution under constant variance is the wrong reference when volatility rises late in the sample: large recent shocks look like acceleration, so false rejections multiply; bootstrapping the observed changes with random signs fixes this."
            },
            "ro": {
                "title": "Nivelul la o schimbare de volatilitate",
                "text": "O serie nu are rădăcină explozivă, dar volatilitatea ei se triplează la mijlocul eșantionului. Ce face GSADF cu valori critice Monte Carlo simulate sub dispersie constantă?",
                "options": [
                    "Respinge prea des, semnalând explozivitate falsă; un wild bootstrap care păstrează traiectoria dispersiei readuce un nivel aproximativ corect",
                    "Respinge mereu prea rar",
                    "Nivelul rămâne exact 5%",
                    "Schimbarea scade doar puterea; nivelul nu este afectat"
                ],
                "correctExplanation": "Dispersia mare din ferestrele recente umflă supremul statisticilor ADF pe ferestre; în simularea Monte Carlo din acest capitol rata de respingere a fost de aproximativ 32% în loc de 5% și de circa 4% cu wild bootstrap (Harvey, Leybourne, Sollis și Taylor).",
                "incorrectExplanation": "Distribuția nulă sub dispersie constantă este referința greșită când volatilitatea crește târziu în eșantion: șocurile recente mari par accelerare, deci respingerile false se înmulțesc; bootstrap-ul variațiilor observate cu semne aleatoare corectează asta."
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
                    "Pentru că schimbările de volatilitate distorsionează rata efectivă de respingere a ipotezei nule, iar wild bootstrap păstrează heteroscedasticitatea datelor",
                    "Pentru că face testul bilateral",
                    "Pentru că estimează momentul critic al crahului"
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
                "title": "Evaluating the LPPLS indicator",
                "text": "An LPPLS confidence indicator is computed every 5 days and the outcome is a fall of at least 20% within 90 days. Why is a two-sample z-test of the hit rates after signal vs no signal inappropriate?",
                "options": [
                    "Because proportions can never be compared",
                    "Because the sample is too large for a z-test",
                    "Because outcome windows overlap and signals come in runs, so observations are dependent; use a block bootstrap or a regression with HAC standard errors",
                    "Because price falls are Normally distributed"
                ],
                "correctExplanation": "Consecutive dates share up to 85 of their 90 outcome days and the indicator is persistent, so the effective number of independent observations is much smaller; a circular block bootstrap with 90-day blocks or Newey-West standard errors gives an honest interval.",
                "incorrectExplanation": "The z-test assumes independent dates. Overlapping outcomes and clustered signals make its standard error too small, which overstates significance."
            },
            "ro": {
                "title": "Evaluarea indicatorului LPPLS",
                "text": "Un indicator de încredere LPPLS este calculat la fiecare 5 zile, iar rezultatul este o scădere de cel puțin 20% în 90 de zile. De ce nu este potrivit un test z pentru două eșantioane al ratelor de reușită după semnal vs fără semnal?",
                "options": [
                    "Pentru că proporțiile nu pot fi comparate niciodată",
                    "Pentru că eșantionul este prea mare pentru un test z",
                    "Pentru că ferestrele rezultatului se suprapun și semnalele vin în serii, deci observațiile sunt dependente; folosiți un bootstrap pe blocuri sau o regresie cu erori standard HAC",
                    "Pentru că scăderile de preț urmează distribuția Normală"
                ],
                "correctExplanation": "Datele consecutive au în comun până la 85 din cele 90 de zile ale rezultatului, iar indicatorul este persistent, deci numărul efectiv de observații independente este mult mai mic; un bootstrap pe blocuri circulare de 90 de zile sau erorile standard Newey-West dau un interval onest.",
                "incorrectExplanation": "Testul z presupune date independente. Rezultatele suprapuse și semnalele grupate îi fac eroarea standard prea mică, ceea ce exagerează semnificația."
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
                "incorrectExplanation": "The reformulation reduces the nonlinear search from four parameters (tc, m, omega, phi) to three (tc, m, omega), out of seven in total, which makes the fit far more stable, but it does not fix the uncertainty about tc."
            },
            "ro": {
                "title": "Calibrarea Filimonov-Sornette",
                "text": "Ce aduce reformularea Filimonov-Sornette a modelului LPPLS?",
                "options": [
                    "Elimină oscilațiile",
                    "Face patru parametri liniari, astfel încât doar tc, m și omega se caută neliniar",
                    "Garantează data crahului",
                    "Transformă modelul într-un GARCH"
                ],
                "correctExplanation": "Scriind C cos(...) ca C1 cos(omega ln(tc - t)) + C2 sin(omega ln(tc - t)), A, B, C1, C2 devin liniari; pentru (tc, m, omega) dați se obțin prin metoda celor mai mici pătrate.",
                "incorrectExplanation": "Reformularea reduce căutarea neliniară de la patru parametri (tc, m, omega, phi) la trei (tc, m, omega), din șapte în total, ceea ce face ajustarea mult mai stabilă, dar nu elimină incertitudinea despre tc."
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
                    "It moves as the estimation window ends later, varies by months across windows and, being constrained to lie after the window end, keeps moving ahead of the current date",
                    "It is always in the past"
                ],
                "correctExplanation": "For Bitcoin 2017 and the Nasdaq 100 in 2000, tc drifted with the end of the window and ranged over several months before the peak; the search space imposes tc after t2, so staying ahead of the current date is a constraint, not evidence.",
                "incorrectExplanation": "A single fit can look impressive, but the estimate depends on the window; honest evaluation looks at the whole sequence of real-time fits."
            },
            "ro": {
                "title": "Stabilitatea lui tc",
                "text": "Ce au arătat ajustările LPPLS pe ferestre mobile din acest capitol despre momentul critic estimat?",
                "options": [
                    "Este stabil de la o dată de estimare la alta",
                    "Coincide mereu cu vârful real",
                    "Se mută pe măsură ce fereastra se termină mai târziu, variază cu luni de la o fereastră la alta și, fiind constrâns să fie ulterior sfârșitului ferestrei, se mută mereu înaintea datei curente",
                    "Este mereu în trecut"
                ],
                "correctExplanation": "Pentru Bitcoin în 2017 și Nasdaq 100 în 2000, tc s-a deplasat odată cu sfârșitul ferestrei și a variat pe mai multe luni înaintea vârfului; spațiul de căutare impune tc ulterior datei t2, deci faptul că rămâne înaintea datei curente este o constrângere, nu o dovadă.",
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
                    "Probabilitatea unui crah mâine",
                    "Valoarea p a testului GSADF"
                ],
                "correctExplanation": "Se ajustează multe ferestre [t2 - L, t2]; indicatorul este fracția celor ai căror parametri sunt în intervalele admise, o măsură a robusteții semnalului de bulă.",
                "incorrectExplanation": "Agregă multe ajustări în loc să se bazeze pe una singură și se calculează doar cu datele până la t2."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "How many Markov regimes?",
                "text": "For weekly Bitcoin returns the likelihood-ratio statistic of one vs two Markov regimes is about 123. Why is comparing it with the chi-square(4) critical value invalid?",
                "options": [
                    "Because the sample has too many observations",
                    "Because under one regime the regime means and variances coincide, so the transition probabilities are not identified and the information matrix is singular; use Hansen-type bounds, the Carrasco-Hu-Ploberger test or a parametric bootstrap",
                    "Because a likelihood ratio must be negative",
                    "Because chi-square tests require Normal returns and nothing else"
                ],
                "correctExplanation": "The regularity conditions behind Wilks' theorem fail: nuisance parameters (the transition probabilities) are present only under the alternative and some scores are identically zero. Simulating from the fitted one-regime model and refitting both models gives the correct null distribution.",
                "incorrectExplanation": "The problem is not the sample size or the sign of the statistic: the LR test of the number of regimes is non-standard, so its critical values must come from bounds, an optimal test or a bootstrap."
            },
            "ro": {
                "title": "Câte regimuri Markov?",
                "text": "Pentru randamentele săptămânale Bitcoin, statistica raportului de verosimilitate pentru un regim vs două regimuri Markov este aproximativ 123. De ce comparația cu valoarea critică chi-pătrat(4) nu este validă?",
                "options": [
                    "Pentru că eșantionul are prea multe observații",
                    "Pentru că sub un singur regim mediile și dispersiile regimurilor coincid, deci probabilitățile de tranziție nu sunt identificate, iar matricea informațională este singulară; folosiți marginile de tip Hansen, testul Carrasco-Hu-Ploberger sau un bootstrap parametric",
                    "Pentru că raportul de verosimilitate trebuie să fie negativ",
                    "Pentru că testele chi-pătrat cer doar randamente din distribuția Normală"
                ],
                "correctExplanation": "Condițiile de regularitate din teorema lui Wilks nu sunt îndeplinite: parametrii de perturbare (probabilitățile de tranziție) apar doar sub ipoteza alternativă, iar unele scoruri sunt identic nule. Simularea din modelul estimat cu un regim și reestimarea ambelor modele dau distribuția nulă corectă.",
                "incorrectExplanation": "Problema nu este mărimea eșantionului sau semnul statisticii: testul LR pentru numărul de regimuri este nestandard, deci valorile lui critice vin din margini, dintr-un test optim sau dintr-un bootstrap."
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
                    "The filtered probability, which uses data up to t, computed with parameters estimated on data up to t"
                ],
                "correctExplanation": "The filtered probability P(s_t | data up to t) is available at t if the parameters are also estimated with data up to t; with full-sample parameters it is only pseudo real time. The smoothed one conditions on the whole sample, including the future.",
                "incorrectExplanation": "Smoothed probabilities look sharper because they use future data; for real-time decisions only the filtered probability is legitimate."
            },
            "ro": {
                "title": "Probabilitate filtrată vs netezită",
                "text": "Ce probabilitate de regim ar fi putut folosi un investitor în timp real?",
                "options": [
                    "Probabilitatea netezită",
                    "Ambele la fel",
                    "Niciuna",
                    "Probabilitatea filtrată, care folosește datele până la t, calculată cu parametri estimați pe datele până la t"
                ],
                "correctExplanation": "Probabilitatea filtrată P(s_t | datele până la t) este disponibilă la t dacă și parametrii sunt estimați cu datele până la t; cu parametrii din toată selecția este doar pseudo-timp real. Cea netezită condiționează pe toată selecția, inclusiv pe viitor.",
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
                "incorrectExplanation": "La acțiuni, turbulența înseamnă de obicei prețuri în scădere; la Bitcoin, regimul volatil conține atât creșterile rapide, cât și crahurile."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Bubbles for Fama",
                "text": "What do sharp industry run-ups predict, according to Greenwood, Shleifer and You and to this chapter's replication on their 48 industries?",
                "options": [
                    "A certain crash within two years",
                    "Lower volatility",
                    "A higher probability of a 40% crash, but not a significantly negative average return",
                    "Nothing at all"
                ],
                "correctExplanation": "Run-ups of more than 100% raise the crash probability well above the unconditional rate, while the average subsequent return is not significantly negative: run-ups are not a sell signal on their own.",
                "incorrectExplanation": "The evidence is about crash probability, not about predictable losses on average; many run-ups keep going."
            },
            "ro": {
                "title": "Bubbles for Fama",
                "text": "Ce prezic creșterile bruște ale unei industrii, după Greenwood, Shleifer și You și după replicarea din acest capitol pe cele 48 de industrii ale lor?",
                "options": [
                    "Un crah sigur în doi ani",
                    "O volatilitate mai mică",
                    "O probabilitate mai mare a unei scăderi de 40%, dar nu un randament mediu semnificativ negativ",
                    "Nimic"
                ],
                "correctExplanation": "Creșterile de peste 100% ridică probabilitatea unui crah mult peste rata necondiționată, în timp ce randamentul mediu ulterior nu este semnificativ negativ: creșterile nu sunt singure un semnal de vânzare.",
                "incorrectExplanation": "Dovezile privesc probabilitatea de crah, nu pierderi previzibile în medie; multe creșteri continuă."
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
                "correctExplanation": "Even dated at confirmation (after L consecutive exceedances), the warning came before the peak, months ahead for the Nasdaq 100 and Bitcoin and days ahead for GameStop; the tests say that the market is in an explosive phase, not when it will end.",
                "incorrectExplanation": "Explosiveness tests are monitoring tools: useful for risk management, not a timing device for the crash."
            },
            "ro": {
                "title": "Lecția timpului real",
                "text": "Pentru Nasdaq 100 (2000), Bitcoin (2017) și GameStop (2021), ce a oferit datarea BSADF în timp real?",
                "options": [
                    "O predicție exactă a datei crahului",
                    "Un avertisment timpuriu că prețurile erau explozive, adesea cu luni înainte de vârf, dar nu momentul crahului",
                    "Niciun semnal înainte de crah",
                    "Un semnal doar după crah"
                ],
                "correctExplanation": "Chiar datat la confirmare (după L depășiri consecutive), avertismentul a venit înaintea vârfului, cu luni înainte pentru Nasdaq 100 și Bitcoin și cu zile înainte pentru GameStop; testele spun că piața este într-o fază explozivă, nu când se va termina.",
                "incorrectExplanation": "Testele de explozivitate sunt instrumente de monitorizare: utile pentru gestiunea riscului, nu un mijloc de a anticipa momentul crahului."
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

// ============================================================
// Quiz bank for chapter id 'garch': Conditional Volatility, GARCH Models (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['garch'] = {
    draw: 20,
    questions: [
        {
            correct: 2,
            en: {
                title: 'Volatility clustering',
                text: 'For the S&P 500 (2000-2026), the lag-1 autocorrelation of daily returns is about -0.10, while that of squared returns is about 0.31. What does this mean?',
                options: [
                    'Returns are strongly predictable in direction',
                    'The variance of returns is constant over time',
                    'The size of tomorrow\'s move is predictable even though its direction is almost not',
                    'The data contain a calculation error, since both must be equal'
                ],
                correctExplanation: 'Squared returns measure the size of moves. Their strong, persistent autocorrelation is volatility clustering: large moves follow large moves, of either sign.',
                incorrectExplanation: 'The direction is almost unpredictable; what persists is the size of the moves (volatility clustering).'
            },
            ro: {
                title: 'Gruparea volatilității',
                text: 'Pentru S&P 500 (2000-2026), autocorelația de ordin 1 a randamentelor zilnice este circa -0,10, iar cea a pătratelor randamentelor circa 0,31. Ce înseamnă acest lucru?',
                options: [
                    'Randamentele sînt puternic predictibile ca direcție',
                    'Dispersia randamentelor este constantă în timp',
                    'Mărimea mișcării de mîine este predictibilă, deși direcția ei aproape nu este',
                    'Datele conțin o eroare de calcul, deoarece cele două trebuie să fie egale'
                ],
                correctExplanation: 'Pătratele randamentelor măsoară mărimea mișcărilor. Autocorelația lor puternică și persistentă este gruparea volatilității: mișcările mari urmează mișcărilor mari, de orice semn.',
                incorrectExplanation: 'Direcția este aproape imprevizibilă; ceea ce persistă este mărimea mișcărilor (gruparea volatilității).'
            }
        },
        {
            correct: 1,
            en: {
                title: "QMLE: consistency versus normality",
                text: "For the Gaussian QMLE of a GARCH(1,1), which condition is needed for sqrt(n)-asymptotic normality but NOT for consistency?",
                options: [
                    "E eps_t^4 < infinity (a finite fourth moment of the returns)",
                    "E z_t^4 < infinity (a finite fourth moment of the innovations)",
                    "alpha + beta < 1 (covariance stationarity)",
                    "Normally distributed innovations z_t"
                ],
                correctExplanation: "Consistency needs strict stationarity, identifiability and a compact parameter space, but no moment of the returns (z_t keeps unit variance). Asymptotic normality adds an interior theta_0 and E z_t^4 < infinity, since the score variance is proportional to kappa_z - 1.",
                incorrectExplanation: "Under strict stationarity, E ln(alpha z_t^2 + beta) < 0, no moment of the returns eps_t is needed, so alpha + beta >= 1 (e.g. IGARCH) is covered; Normal z_t would make the estimator the MLE. The nonstationary case is a separate result (Jensen-Rahbek: alpha and beta, with omega fixed). The extra condition is a finite fourth moment of the innovations z_t."
            },
            ro: {
                title: "QMLE: consistență și normalitate",
                text: "Pentru QMLE Gaussian al unui GARCH(1,1), ce condiție este necesară pentru normalitatea asimptotică în sqrt(n), dar NU și pentru consistență?",
                options: [
                    "E eps_t^4 < infinit (moment de ordin patru finit al randamentelor)",
                    "E z_t^4 < infinit (moment de ordin patru finit al inovațiilor)",
                    "alpha + beta < 1 (staționaritate în covarianță)",
                    "Inovații z_t distribuite Normal"
                ],
                correctExplanation: "Consistența cere staționaritate strictă, identificabilitate și un spațiu compact al parametrilor, dar niciun moment al randamentelor (z_t păstrează dispersia unitară). Normalitatea asimptotică adaugă theta_0 interior și E z_t^4 < infinit, deoarece dispersia scorului este proporțională cu kappa_z - 1.",
                incorrectExplanation: "Sub staționaritate strictă, E ln(alpha z_t^2 + beta) < 0, nu este necesar niciun moment al randamentelor eps_t, deci alpha + beta >= 1 (de ex. IGARCH) este acoperit; z_t Normal ar face din estimator MLE. Cazul nestaționar este un rezultat separat (Jensen-Rahbek: alpha și beta, cu omega fixat). Condiția suplimentară este momentul de ordin patru finit al inovațiilor z_t."
            }
        },
        {
            correct: 1,
            en: {
                title: 'From ARCH to GARCH',
                text: 'Why did Bollerslev (1986) add the lagged variance beta * sigma_{t-1}^2 to the ARCH model of Engle (1982)?',
                options: [
                    'To make the variance negative after good news',
                    'To capture long-lasting clustering with few parameters: GARCH(1,1) is an ARCH of infinite order with geometric weights',
                    'To remove the need for maximum likelihood estimation',
                    'To model the mean of returns instead of the variance'
                ],
                correctExplanation: 'Substituting backwards, GARCH(1,1) equals an ARCH(infinity) with weights alpha * beta^(j-1): persistent short-memory variance dynamics with only three parameters.',
                incorrectExplanation: 'The lagged variance gives an ARCH of infinite order with geometrically declining weights, so persistent clustering needs only three parameters.'
            },
            ro: {
                title: 'De la ARCH la GARCH',
                text: 'De ce a adăugat Bollerslev (1986) dispersia decalată beta * sigma_{t-1}^2 la modelul ARCH al lui Engle (1982)?',
                options: [
                    'Pentru ca dispersia să devină negativă după știri bune',
                    'Pentru a surprinde o grupare de durată cu puțini parametri: GARCH(1,1) este un ARCH de ordin infinit cu ponderi geometrice',
                    'Pentru a elimina nevoia estimării prin verosimilitate maximă',
                    'Pentru a modela media randamentelor în locul dispersiei'
                ],
                correctExplanation: 'Prin substituții succesive, GARCH(1,1) este un ARCH(infinit) cu ponderi alpha * beta^(j-1): o dinamică persistentă a dispersiei, cu memorie scurtă, cu doar trei parametri.',
                incorrectExplanation: 'Dispersia decalată dă un ARCH de ordin infinit cu ponderi descrescătoare geometric, deci gruparea persistentă cere doar trei parametri.'
            }
        },
        {
            correct: 0,
            en: {
                title: "Boundary likelihood ratio",
                text: "You test Normal innovations (1/nu = 0) against Student-t innovations with a likelihood ratio test. What is the 5% critical value?",
                options: [
                    "2.71, from the mixture 0.5 chi2(0) + 0.5 chi2(1)",
                    "3.84, from chi2(1)",
                    "5.99, from chi2(2)",
                    "None: with nu = infinity only AIC or BIC can be used"
                ],
                correctExplanation: "Since 1/nu >= 0, the null lies on the boundary. Half of the time the unrestricted estimate sits at the bound and LR = 0, so the limit is 0.5 chi2(0) + 0.5 chi2(1), whose 5% critical value is the 10% value of chi2(1), 2.71.",
                incorrectExplanation: "The restriction 1/nu = 0 is on the boundary of 1/nu >= 0, so the LR statistic has the mixture limit 0.5 chi2(0) + 0.5 chi2(1) (Self and Liang), with critical value 2.71; a valid test exists."
            },
            ro: {
                title: "Raportul de verosimilitate la frontieră",
                text: "Testați inovații Normale (1/nu = 0) față de inovații Student-t cu un test al raportului de verosimilitate. Care este valoarea critică la 5%?",
                options: [
                    "2,71, din amestecul 0,5 chi2(0) + 0,5 chi2(1)",
                    "3,84, din chi2(1)",
                    "5,99, din chi2(2)",
                    "Niciuna: cu nu = infinit se pot folosi doar AIC sau BIC"
                ],
                correctExplanation: "Deoarece 1/nu >= 0, ipoteza nulă este pe frontieră. Jumătate din timp estimarea nerestricționată stă la limită și LR = 0, deci limita este 0,5 chi2(0) + 0,5 chi2(1), a cărei valoare critică la 5% este valoarea de 10% a lui chi2(1), 2,71.",
                incorrectExplanation: "Restricția 1/nu = 0 este pe frontiera lui 1/nu >= 0, deci statistica LR are limita de tip amestec 0,5 chi2(0) + 0,5 chi2(1) (Self și Liang), cu valoarea critică 2,71; un test valid există."
            }
        },
        {
            correct: 2,
            en: {
                title: "The sandwich factor",
                text: "In a Gaussian QMLE of an ARCH(1) with known omega, the innovations have kurtosis kappa_z = 5. The ratio of the robust (sandwich) to the classical standard error of alpha-hat is about:",
                options: [
                    "1, because QMLE is consistent",
                    "sqrt(5) = 2.24",
                    "sqrt((5 - 1)/2) = 1.41",
                    "5/3 = 1.67"
                ],
                correctExplanation: "With A = 0.5 E x_t^2 and B = 0.25 (kappa_z - 1) E x_t^2, the sandwich A^-1 B A^-1 equals (kappa_z - 1)/2 times the inverse Hessian A^-1, so the standard errors differ by sqrt((kappa_z - 1)/2) = 1.41.",
                incorrectExplanation: "Consistency does not make the classical formula right. The score variance is proportional to kappa_z - 1 and the Hessian to 2, so the variance ratio is (kappa_z - 1)/2 = 2 and the standard error ratio is 1.41."
            },
            ro: {
                title: "Factorul „sandviș”",
                text: "Într-un QMLE Gaussian al unui ARCH(1) cu omega cunoscut, inovațiile au aplatizarea kappa_z = 5. Raportul dintre eroarea standard robustă („sandviș”) și cea clasică a lui alpha-hat este circa:",
                options: [
                    "1, deoarece QMLE este consistent",
                    "sqrt(5) = 2,24",
                    "sqrt((5 - 1)/2) = 1,41",
                    "5/3 = 1,67"
                ],
                correctExplanation: "Cu A = 0,5 E x_t^2 și B = 0,25 (kappa_z - 1) E x_t^2, sandvișul A^-1 B A^-1 este de (kappa_z - 1)/2 ori inversa hessianei A^-1, deci erorile standard diferă prin factorul sqrt((kappa_z - 1)/2) = 1,41.",
                incorrectExplanation: "Consistența nu face corectă formula clasică. Dispersia scorului este proporțională cu kappa_z - 1, iar hessiana cu 2, deci raportul dispersiilor este (kappa_z - 1)/2 = 2, iar cel al erorilor standard 1,41."
            }
        },
        {
            correct: 3,
            en: {
                title: "Portmanteau with estimated parameters",
                text: "You apply Ljung-Box with 10 lags to the squared standardised residuals of an estimated GARCH(1,1) and use chi2(10) critical values. The test is:",
                options: [
                    "Exact, because the standardised residuals are i.i.d. under the model",
                    "Correct with chi2(10 - 3) critical values, as for ARMA residuals",
                    "Invalid for any GARCH model",
                    "Not exactly chi2(10): estimation of the variance parameters changes the limit (Li and Mak), mostly at small lags"
                ],
                correctExplanation: "The residuals depend on the estimated parameters; the limit covariance of the squared-residual autocorrelations is I - H'J^-1 H/(kappa_z - 1). For the S&P 500 GARCH-N the corrected Q(10) is 19.1 (p = 0.038) against 16.4 (p = 0.089) for the naive test.",
                incorrectExplanation: "Parameter estimation makes the naive chi2(10) test conservative; the ARMA rule of subtracting the number of parameters does not apply to squares, and Li and Mak give the correct limit, which remains usable."
            },
            ro: {
                title: "Test portmanteau cu parametri estimați",
                text: "Aplicați Ljung-Box cu 10 decalaje pe pătratele reziduurilor standardizate ale unui GARCH(1,1) estimat și folosiți valorile critice chi2(10). Testul este:",
                options: [
                    "Exact, deoarece reziduurile standardizate sînt i.i.d. sub model",
                    "Corect cu valorile critice chi2(10 - 3), ca la reziduurile ARMA",
                    "Invalid pentru orice model GARCH",
                    "Nu exact chi2(10): estimarea parametrilor dispersiei schimbă limita (Li și Mak), mai ales la decalaje mici"
                ],
                correctExplanation: "Reziduurile depind de parametrii estimați; covarianța limită a autocorelațiilor pătratelor reziduurilor este I - H'J^-1 H/(kappa_z - 1). Pentru GARCH-N pe S&P 500, Q(10) corectat este 19,1 (p = 0,038), față de 16,4 (p = 0,089) pentru testul naiv.",
                incorrectExplanation: "Estimarea parametrilor face testul naiv chi2(10) conservator; regula ARMA de scădere a numărului de parametri nu se aplică pătratelor, iar Li și Mak dau limita corectă, care rămîne utilizabilă."
            }
        },
        {
            correct: 0,
            en: {
                title: 'Multi-step forecasts',
                text: 'In a covariance-stationary GARCH(1,1) (alpha + beta < 1), how does the h-step variance forecast behave as h grows?',
                options: [
                    'It converges to the long-run variance, closing the gap by the factor alpha + beta each day',
                    'It stays equal to tomorrow\'s variance forever',
                    'It grows without bound',
                    'It oscillates between high and low values'
                ],
                correctExplanation: 'E_t sigma_{t+h}^2 = sigma^2 + (alpha + beta)^(h-1) (sigma_{t+1}^2 - sigma^2): mean reversion towards the long-run variance.',
                incorrectExplanation: 'With alpha + beta < 1 the forecast reverts geometrically to omega / (1 - alpha - beta); a flat forecast is the EWMA case (IGARCH with omega = 0); with omega > 0, IGARCH forecasts grow by omega per day.'
            },
            ro: {
                title: 'Prognoze pe mai mulți pași',
                text: 'Într-un GARCH(1,1) staționar în covarianță (alpha + beta < 1), cum se comportă prognoza dispersiei pe h pași cînd h crește?',
                options: [
                    'Converge spre dispersia de termen lung, reducînd distanța cu factorul alpha + beta în fiecare zi',
                    'Rămîne egală pentru totdeauna cu dispersia de mîine',
                    'Crește nelimitat',
                    'Oscilează între valori mari și mici'
                ],
                correctExplanation: 'E_t sigma_{t+h}^2 = sigma^2 + (alpha + beta)^(h-1) (sigma_{t+1}^2 - sigma^2): revenire la medie spre dispersia de termen lung.',
                incorrectExplanation: 'Cu alpha + beta < 1 prognoza revine geometric spre omega / (1 - alpha - beta); prognoza constantă este cazul EWMA (IGARCH cu omega = 0); cu omega > 0, prognozele IGARCH cresc cu omega pe zi.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'EWMA',
                text: 'Which statement about the RiskMetrics EWMA with lambda = 0.94 is correct?',
                options: [
                    'It is a stationary GARCH(1,1) with a finite long-run variance',
                    'Its parameters must be estimated by maximum likelihood',
                    'It gives more weight to old observations than to recent ones',
                    'It is an IGARCH(1,1) with omega = 0, alpha = 0.06, beta = 0.94, so its forecast is flat in the horizon'
                ],
                correctExplanation: 'sigma_t^2 = 0.94 sigma_{t-1}^2 + 0.06 r_{t-1}^2 is GARCH with alpha + beta = 1 and omega = 0: no mean reversion, the forecast for any horizon equals tomorrow\'s variance.',
                incorrectExplanation: 'EWMA is the IGARCH special case with omega = 0; it has no long-run variance and no mean reversion.'
            },
            ro: {
                title: 'EWMA',
                text: 'Care afirmație despre EWMA RiskMetrics cu lambda = 0,94 este corectă?',
                options: [
                    'Este un GARCH(1,1) staționar cu dispersie de termen lung finită',
                    'Parametrii săi trebuie estimați prin verosimilitate maximă',
                    'Dă mai multă pondere observațiilor vechi decît celor recente',
                    'Este un IGARCH(1,1) cu omega = 0, alpha = 0,06, beta = 0,94, deci prognoza sa este constantă în orizont'
                ],
                correctExplanation: 'sigma_t^2 = 0,94 sigma_{t-1}^2 + 0,06 r_{t-1}^2 este un GARCH cu alpha + beta = 1 și omega = 0: fără revenire la medie, prognoza pentru orice orizont este dispersia de mîine.',
                incorrectExplanation: 'EWMA este cazul particular IGARCH cu omega = 0; nu are dispersie de termen lung și nici revenire la medie.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Fat tails from clustering',
                text: 'A GARCH(1,1) with Normal innovations z_t, alpha > 0 and a finite fourth moment ((alpha + beta)^2 + 2 alpha^2 < 1) generates returns with kurtosis...',
                options: [
                    'exactly 3, because z_t is Normal',
                    'above 3, because mixing periods of low and high variance produces heavy tails',
                    'below 3, because the variance is bounded',
                    'that cannot be computed'
                ],
                correctExplanation: 'The kurtosis is 3[1 - (alpha+beta)^2] / [1 - (alpha+beta)^2 - 2 alpha^2] > 3 for alpha > 0: clustering alone creates fat tails.',
                incorrectExplanation: 'Even with Normal innovations, a time-varying variance makes the unconditional distribution leptokurtic.'
            },
            ro: {
                title: 'Cozi groase din grupare',
                text: 'Un GARCH(1,1) cu inovații z_t Normale, alpha > 0 și moment de ordin patru finit ((alpha + beta)^2 + 2 alpha^2 < 1) generează randamente cu aplatizarea...',
                options: [
                    'exact 3, deoarece z_t este Normal',
                    'peste 3, deoarece amestecul perioadelor cu dispersie mică și mare produce cozi groase',
                    'sub 3, deoarece dispersia este mărginită',
                    'care nu poate fi calculată'
                ],
                correctExplanation: 'Aplatizarea este 3[1 - (alpha+beta)^2] / [1 - (alpha+beta)^2 - 2 alpha^2] > 3 pentru alpha > 0: gruparea singură creează cozi groase.',
                incorrectExplanation: 'Chiar și cu inovații Normale, o dispersie variabilă în timp face distribuția necondiționată leptocurtică.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Quasi-maximum likelihood',
                text: 'You estimate a GARCH by maximising the Normal likelihood, but the innovations are heavy-tailed, with a finite fourth moment. What should you do?',
                options: [
                    'Nothing: the classical standard errors remain valid',
                    'Abandon GARCH, since the estimates are inconsistent',
                    'Keep the estimates (consistent under correct mean and variance equations) but use robust Bollerslev-Wooldridge standard errors',
                    'Multiply the standard errors by the kurtosis'
                ],
                correctExplanation: 'Quasi-maximum likelihood is consistent if the first two conditional moments are correct; with E z_t^4 < infinity, inference uses the sandwich covariance A^-1 B A^-1 (if E z_t^4 = infinity, sqrt(n) inference fails: Hall and Yao, 2003).',
                incorrectExplanation: 'The QML estimates stay consistent; only the standard errors must be replaced by the robust sandwich form.'
            },
            ro: {
                title: 'Cvasi-verosimilitate maximă',
                text: 'Estimați un GARCH maximizînd verosimilitatea Normală, dar inovațiile au cozi groase, cu moment de ordin patru finit. Ce trebuie să faceți?',
                options: [
                    'Nimic: erorile standard clasice rămîn valide',
                    'Renunțați la GARCH, deoarece estimările sînt inconsistente',
                    'Păstrați estimările (consistente dacă ecuațiile mediei și dispersiei sînt corecte), dar folosiți erorile standard robuste Bollerslev-Wooldridge',
                    'Înmulțiți erorile standard cu aplatizarea'
                ],
                correctExplanation: 'Cvasi-verosimilitatea maximă este consistentă dacă primele două momente condiționate sînt corecte; cu E z_t^4 < infinit, inferența folosește covarianța „sandviș” A^-1 B A^-1 (dacă E z_t^4 = infinit, inferența în sqrt(n) nu mai funcționează: Hall și Yao, 2003).',
                incorrectExplanation: 'Estimările QML rămîn consistente; doar erorile standard trebuie înlocuite cu forma robustă „sandviș”.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Student-t degrees of freedom',
                text: 'A GARCH(1,1)-t fitted to Bitcoin gives nu = 3.18. What does this imply?',
                options: [
                    'The innovations have extremely heavy tails and no finite fourth moment',
                    'The innovations are close to the Normal distribution',
                    'The model is misspecified because nu must be an integer',
                    'The variance of the innovations is infinite'
                ],
                correctExplanation: 'For a Student-t, the fourth moment exists only if nu > 4; with nu = 3.18 kurtosis is infinite, although the variance (nu > 2) is finite.',
                incorrectExplanation: 'Small nu means heavy tails; the fourth moment requires nu > 4, the variance only nu > 2.'
            },
            ro: {
                title: 'Gradele de libertate Student-t',
                text: 'Un GARCH(1,1)-t estimat pentru Bitcoin dă nu = 3,18. Ce implică acest lucru?',
                options: [
                    'Inovațiile au cozi extrem de groase și nu au moment de ordin patru finit',
                    'Inovațiile sînt apropiate de distribuția Normală',
                    'Modelul este greșit specificat, deoarece parametrul ν trebuie să fie un număr întreg',
                    'Dispersia inovațiilor este infinită'
                ],
                correctExplanation: 'La o Student-t, momentul de ordin patru există doar dacă nu > 4; cu nu = 3,18 aplatizarea este infinită, deși dispersia (nu > 2) este finită.',
                incorrectExplanation: 'Un nu mic înseamnă cozi groase; momentul de ordin patru cere nu > 4, dispersia doar nu > 2.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Skewed-t',
                text: 'In Hansen\'s (1994) skewed-t distribution, what does a negative asymmetry parameter lambda indicate?',
                options: [
                    'Thinner tails than the Normal distribution',
                    'A longer right tail: large gains more likely than large losses',
                    'That the model is not identified',
                    'A longer left tail: large losses more likely than large gains'
                ],
                correctExplanation: 'lambda < 0 tilts the density to the left; for the S&P 500 GJR-GARCH gives lambda of about -0.15.',
                incorrectExplanation: 'A negative lambda means left skewness: the loss tail is longer.'
            },
            ro: {
                title: 't asimetric',
                text: 'În distribuția t asimetrică a lui Hansen (1994), ce indică un parametru de asimetrie lambda negativ?',
                options: [
                    'Cozi mai subțiri decît distribuția Normală',
                    'O coadă dreaptă mai lungă: cîștigurile mari mai probabile decît pierderile mari',
                    'Că modelul nu este identificat',
                    'O coadă stîngă mai lungă: pierderile mari mai probabile decît cîștigurile mari'
                ],
                correctExplanation: 'lambda < 0 înclină densitatea spre stînga; pentru S&P 500, GJR-GARCH dă lambda de circa -0,15.',
                incorrectExplanation: 'Un lambda negativ înseamnă asimetrie la stînga: coada pierderilor este mai lungă.'
            }
        },
        {
            correct: 0,
            en: {
                title: "Autocorrelation of squared shocks",
                text: "For a GARCH(1,1) with a finite fourth moment, the first autocorrelation of eps_t^2 is:",
                options: [
                    "alpha (1 - beta^2 - alpha beta) / (1 - beta^2 - 2 alpha beta)",
                    "alpha + beta",
                    "alpha",
                    "beta"
                ],
                correctExplanation: "eps_t^2 is an ARMA(1,1) with phi = alpha + beta and theta = -beta; the ARMA(1,1) formula gives the expression, and later lags decay as rho_k = rho_1 (alpha + beta)^(k-1). For the S&P 500 GARCH-N it gives 0.356.",
                incorrectExplanation: "alpha + beta is the rate of decay of the autocorrelations, not their level at lag 1; plugging phi = alpha + beta and theta = -beta into the ARMA(1,1) autocorrelation gives alpha (1 - beta^2 - alpha beta) / (1 - beta^2 - 2 alpha beta)."
            },
            ro: {
                title: "Autocorelația pătratelor șocurilor",
                text: "Pentru un GARCH(1,1) cu moment de ordin patru finit, prima autocorelație a lui eps_t^2 este:",
                options: [
                    "alpha (1 - beta^2 - alpha beta) / (1 - beta^2 - 2 alpha beta)",
                    "alpha + beta",
                    "alpha",
                    "beta"
                ],
                correctExplanation: "eps_t^2 este un ARMA(1,1) cu phi = alpha + beta și theta = -beta; formula ARMA(1,1) dă expresia, iar decalajele următoare scad ca rho_k = rho_1 (alpha + beta)^(k-1). Pentru GARCH-N pe S&P 500 rezultă 0,356.",
                incorrectExplanation: "alpha + beta este rata de scădere a autocorelațiilor, nu nivelul lor la decalajul 1; înlocuind phi = alpha + beta și theta = -beta în autocorelația ARMA(1,1) obținem alpha (1 - beta^2 - alpha beta) / (1 - beta^2 - 2 alpha beta)."
            }
        },
        {
            correct: 2,
            en: {
                title: 'GJR persistence',
                text: 'With symmetric innovations, what is the persistence of a GJR-GARCH(1,1)?',
                options: [
                    'alpha + beta',
                    'alpha + gamma + beta',
                    'alpha + gamma/2 + beta',
                    'beta only'
                ],
                correctExplanation: 'Half of the shocks are negative, so on average the slope on eps^2 is alpha + gamma/2; the persistence is alpha + gamma/2 + beta.',
                incorrectExplanation: 'The gamma term is active only after negative shocks, i.e. half of the time with symmetric innovations: alpha + gamma/2 + beta.'
            },
            ro: {
                title: 'Persistența GJR',
                text: 'Cu inovații simetrice, care este persistența unui GJR-GARCH(1,1)?',
                options: [
                    'alpha + beta',
                    'alpha + gamma + beta',
                    'alpha + gamma/2 + beta',
                    'doar beta'
                ],
                correctExplanation: 'Jumătate din șocuri sînt negative, deci în medie panta pe eps^2 este alpha + gamma/2; persistența este alpha + gamma/2 + beta.',
                incorrectExplanation: 'Termenul gamma este activ doar după șocuri negative, adică jumătate din timp cu inovații simetrice: alpha + gamma/2 + beta.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'EGARCH',
                text: 'What is an advantage of EGARCH (Nelson, 1991) over GARCH?',
                options: [
                    'It models ln sigma_t^2, so the variance is positive without sign restrictions on the parameters, and it allows asymmetry',
                    'It needs no numerical optimisation',
                    'Its forecasts never revert to the mean',
                    'It removes the need for innovations'
                ],
                correctExplanation: 'The log form guarantees sigma_t^2 > 0; the term gamma z_{t-1} captures the sign effect (gamma < 0: bad news raises volatility).',
                incorrectExplanation: 'EGARCH works on the log-variance, which keeps the variance positive and lets the sign of news enter through gamma.'
            },
            ro: {
                title: 'EGARCH',
                text: 'Care este un avantaj al EGARCH (Nelson, 1991) față de GARCH?',
                options: [
                    'Modelează ln sigma_t^2, deci dispersia este pozitivă fără restricții de semn asupra parametrilor, și permite asimetria',
                    'Nu necesită optimizare numerică',
                    'Prognozele sale nu revin niciodată la medie',
                    'Elimină nevoia inovațiilor'
                ],
                correctExplanation: 'Forma logaritmică garantează sigma_t^2 > 0; termenul gamma z_{t-1} surprinde efectul de semn (gamma < 0: știrile proaste cresc volatilitatea).',
                incorrectExplanation: 'EGARCH lucrează cu logaritmul dispersiei, ceea ce păstrează dispersia pozitivă și permite ca semnul știrilor să intervină prin gamma.'
            }
        },
        {
            correct: 1,
            en: {
                title: "Comparing nested forecasting models",
                text: "You compare GARCH-t with GJR-t (which nests it) using Diebold-Mariano on expanding-window forecasts with estimated parameters. What is the main problem?",
                options: [
                    "Diebold-Mariano requires Normally distributed losses",
                    "Under the null the loss differential degenerates, so the N(0,1) limit is invalid; test the method with a rolling window (Giacomini-White)",
                    "QLIKE is not robust to a noisy volatility proxy",
                    "Diebold-Mariano cannot use HAC standard errors"
                ],
                correctExplanation: "With nested models and parameters estimated on an expanding window, both forecasts converge to the same one under the null, so the differential vanishes (West; Clark and McCracken). Giacomini and White test the forecasting method with a finite rolling window, where estimation noise persists.",
                incorrectExplanation: "Normal losses are not required, QLIKE is Patton-robust, and HAC errors are standard in Diebold-Mariano. The issue is the degenerate loss differential of nested models with estimated parameters, which Giacomini-White avoid with a rolling window."
            },
            ro: {
                title: "Compararea modelelor de prognoză imbricate",
                text: "Comparați GARCH-t cu GJR-t (care îl include) cu testul Diebold-Mariano pe prognoze cu fereastră în expansiune și parametri estimați. Care este problema principală?",
                options: [
                    "Diebold-Mariano cere pierderi distribuite Normal",
                    "Sub ipoteza nulă diferența de pierderi degenerează, deci limita N(0,1) nu este validă; testați metoda cu o fereastră mobilă (Giacomini-White)",
                    "QLIKE nu este robustă la o aproximare zgomotoasă a volatilității",
                    "Diebold-Mariano nu poate folosi erori standard HAC"
                ],
                correctExplanation: "Cu modele imbricate și parametri estimați pe o fereastră în expansiune, sub ipoteza nulă cele două prognoze converg spre aceeași, deci diferența dispare (West; Clark și McCracken). Giacomini și White testează metoda de prognoză cu o fereastră mobilă finită, unde zgomotul estimării persistă.",
                incorrectExplanation: "Pierderile Normale nu sînt necesare, QLIKE este robustă în sensul lui Patton, iar erorile HAC sînt standard în Diebold-Mariano. Problema este diferența degenerată a modelelor imbricate cu parametri estimați, pe care Giacomini-White o evită cu o fereastră mobilă."
            }
        },
        {
            correct: 1,
            en: {
                title: 'Asymmetry across markets',
                text: 'In the chapter, GJR-GARCH-t gives a strongly positive gamma for the S&P 500, gamma close to 0 for Bitcoin and a negative gamma for gold. Which reading is right?',
                options: [
                    'All three markets show the classic leverage effect',
                    'The leverage effect is an equity phenomenon; for gold, price rises are the more volatile direction (safe-haven behaviour)',
                    'Bitcoin has the strongest leverage effect',
                    'Negative gamma means the model is wrong'
                ],
                correctExplanation: 'For gold, rallies in turbulent periods raise volatility more than falls: an inverted asymmetry, consistent with a safe-haven asset. Bitcoin shows no significant asymmetry.',
                incorrectExplanation: 'The classic leverage effect appears for equities; gold shows inverted asymmetry and Bitcoin none.'
            },
            ro: {
                title: 'Asimetria pe piețe',
                text: 'În capitol, GJR-GARCH-t dă un gamma puternic pozitiv pentru S&P 500, gamma aproape de 0 pentru Bitcoin și un gamma negativ pentru aur. Care interpretare este corectă?',
                options: [
                    'Toate cele trei piețe arată efectul de levier clasic',
                    'Efectul de levier este un fenomen al acțiunilor; la aur, creșterile de preț sînt direcția mai volatilă (comportament de activ de refugiu)',
                    'Bitcoin are cel mai puternic efect de levier',
                    'Un gamma negativ înseamnă că modelul este greșit'
                ],
                correctExplanation: 'La aur, creșterile din perioadele agitate cresc volatilitatea mai mult decît scăderile: o asimetrie inversă, compatibilă cu comportamentul unui activ de refugiu. Bitcoin nu are asimetrie semnificativă.',
                incorrectExplanation: 'Efectul de levier clasic apare la acțiuni; aurul are asimetrie inversă, iar Bitcoin deloc.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Diagnostics',
                text: 'After fitting a GARCH model, which check tests whether volatility clustering is left in the residuals?',
                options: [
                    'The Ljung-Box test on the raw returns',
                    'The R^2 of the mean equation',
                    'Ljung-Box on the squared standardised residuals z_t^2 and the ARCH-LM test on z_t',
                    'The number of parameters'
                ],
                correctExplanation: 'If the variance equation is adequate, z_t^2 is uncorrelated in the population: significant dependence in Q(10) on z_t^2 or the LM test is evidence against the model, while non-rejection only means insufficient evidence against it.',
                incorrectExplanation: 'Remaining clustering is tested on the squared standardised residuals, not on raw returns.'
            },
            ro: {
                title: 'Diagnostic',
                text: 'După estimarea unui model GARCH, ce verificare testează dacă a rămas grupare a volatilității în reziduuri?',
                options: [
                    'Testul Ljung-Box pe randamentele brute',
                    'R^2 al ecuației mediei',
                    'Ljung-Box pe pătratele reziduurilor standardizate z_t^2 și testul ARCH-LM pe z_t',
                    'Numărul de parametri'
                ],
                correctExplanation: 'Dacă ecuația dispersiei este adecvată, z_t^2 sînt necorelate în populație: o dependență semnificativă în Q(10) pe z_t^2 sau în testul LM este o dovadă împotriva modelului, iar nerespingerea înseamnă doar dovezi insuficiente împotriva lui.',
                incorrectExplanation: 'Gruparea rămasă se testează pe pătratele reziduurilor standardizate, nu pe randamentele brute.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Sign-bias test',
                text: 'The joint sign-bias test of Engle and Ng rejects for a symmetric GARCH on the S&P 500. What is the natural next step?',
                options: [
                    'Try an asymmetric variance equation such as GJR-GARCH or EGARCH',
                    'Increase the number of ARCH lags in a symmetric model',
                    'Switch to returns in decimals',
                    'Drop the constant from the mean equation'
                ],
                correctExplanation: 'Sign bias means the sign of past shocks still predicts squared residuals, which a symmetric model cannot capture.',
                incorrectExplanation: 'A rejected sign-bias test points to missing asymmetry; symmetric lags cannot fix it.'
            },
            ro: {
                title: 'Testul de asimetrie',
                text: 'Testul comun de asimetrie Engle-Ng respinge pentru un GARCH simetric pe S&P 500. Care este pasul următor firesc?',
                options: [
                    'Încercați o ecuație a dispersiei asimetrică, de exemplu GJR-GARCH sau EGARCH',
                    'Creșteți numărul de decalaje ARCH într-un model simetric',
                    'Treceți la randamente în zecimale',
                    'Eliminați constanta din ecuația mediei'
                ],
                correctExplanation: 'Asimetria de semn înseamnă că semnul șocurilor trecute încă prezice pătratele reziduurilor, ceea ce un model simetric nu poate surprinde.',
                incorrectExplanation: 'Un test de asimetrie respins indică lipsa asimetriei din model; decalajele simetrice nu o pot corecta.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'LR test versus BIC',
                text: 'For the BET, GJR vs GARCH gives LR = 4.93 (p = 0.026), yet BIC prefers GARCH. Why can both be true?',
                options: [
                    'The LR test is always wrong for GARCH models',
                    'BIC ignores the likelihood',
                    'The two models are not nested',
                    'BIC penalises each extra parameter by ln n (about 8.8 here), more than the likelihood gain, while the LR test uses the 3.84 critical value'
                ],
                correctExplanation: 'BIC = -2 log L + k ln n; with n of about 6,700 the penalty for one parameter exceeds the LR gain of 4.93, although the LR test rejects at 5%.',
                incorrectExplanation: 'The models are nested; the disagreement comes from BIC\'s larger penalty ln n compared with the chi-square critical value.'
            },
            ro: {
                title: 'Testul LR și BIC',
                text: 'Pentru BET, GJR față de GARCH dă LR = 4,93 (p = 0,026), dar BIC preferă GARCH. De ce pot fi ambele adevărate?',
                options: [
                    'Testul LR este mereu greșit pentru modelele GARCH',
                    'BIC ignoră verosimilitatea',
                    'Cele două modele nu sînt imbricate',
                    'BIC penalizează fiecare parametru suplimentar cu ln n (circa 8,8 aici), mai mult decît cîștigul de verosimilitate, iar testul LR folosește valoarea critică 3,84'
                ],
                correctExplanation: 'BIC = -2 log L + k ln n; cu n de circa 6.700, penalizarea pentru un parametru depășește cîștigul LR de 4,93, deși testul LR respinge la 5%.',
                incorrectExplanation: 'Modelele sînt imbricate; dezacordul vine din penalizarea mai mare ln n a BIC, comparată cu valoarea critică chi-pătrat.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'QLIKE',
                text: 'Why do Patton (2011) and this chapter use the QLIKE loss r_t^2 / h_t + ln h_t to compare volatility forecasts?',
                options: [
                    'Because it ignores large errors',
                    'Because it ranks forecasts correctly even when the proxy r_t^2 is noisy',
                    'Because it does not need a proxy for volatility',
                    'Because it rewards under-prediction of risk'
                ],
                correctExplanation: 'QLIKE and MSE are robust to proxy noise: if r_t^2 is conditionally unbiased for the variance, the ranking by expected loss with r_t^2 matches the ranking with the true variance (sample rankings can still differ). QLIKE also penalises under-prediction more.',
                incorrectExplanation: 'QLIKE is robust to a noisy proxy (Patton, 2011) and penalises under-prediction more heavily, not less.'
            },
            ro: {
                title: 'QLIKE',
                text: 'De ce folosesc Patton (2011) și acest capitol pierderea QLIKE r_t^2 / h_t + ln h_t pentru a compara prognozele de volatilitate?',
                options: [
                    'Pentru că ignoră erorile mari',
                    'Pentru că ordonează corect prognozele chiar și cînd aproximarea r_t^2 este zgomotoasă',
                    'Pentru că nu are nevoie de o aproximare a volatilității',
                    'Pentru că recompensează subestimarea riscului'
                ],
                correctExplanation: 'QLIKE și MSE sînt robuste la zgomotul aproximării: dacă r_t^2 este condiționat nedeplasat pentru dispersie, ordonarea după pierderea așteptată cu r_t^2 coincide cu cea după dispersia reală (ordonările din eșantion pot totuși diferi). QLIKE penalizează în plus mai mult subestimarea.',
                incorrectExplanation: 'QLIKE este robustă la o aproximare zgomotoasă (Patton, 2011) și penalizează mai mult subestimarea, nu mai puțin.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Mincer-Zarnowitz',
                text: 'A Mincer-Zarnowitz regression r_t^2 = a + b h_t for one-day GARCH forecasts gives a = 0.03, b = 0.97, a joint HAC Wald test of a = 0, b = 1 with p = 0.99, and R^2 of only about 0.25. What is the right conclusion?',
                options: [
                    'The forecasts are useless',
                    'The model is biased',
                    'Unbiasedness is not rejected; the low R^2 reflects the noise of r_t^2 as a proxy',
                    'The regression must be run without a constant'
                ],
                correctExplanation: 'Since r_t^2 = sigma_t^2 z_t^2, even a perfect forecast explains only part of the variation of r_t^2 (Andersen and Bollerslev, 1998).',
                incorrectExplanation: 'a = 0, b = 1 tests unbiasedness; a low R^2 is expected with a noisy daily proxy.'
            },
            ro: {
                title: 'Mincer-Zarnowitz',
                text: 'O regresie Mincer-Zarnowitz r_t^2 = a + b h_t pentru prognozele GARCH pe o zi dă a = 0,03, b = 0,97, un test Wald comun HAC pentru a = 0, b = 1 cu p = 0,99 și R^2 de doar circa 0,25. Care este concluzia corectă?',
                options: [
                    'Prognozele sînt inutile',
                    'Modelul este deplasat',
                    'Nedeplasarea nu este respinsă; R^2 mic reflectă zgomotul lui r_t^2 ca aproximare',
                    'Regresia trebuie estimată fără termen liber'
                ],
                correctExplanation: 'Deoarece r_t^2 = sigma_t^2 z_t^2, chiar și o prognoză perfectă explică doar o parte din variația lui r_t^2 (Andersen și Bollerslev, 1998).',
                incorrectExplanation: 'a = 0, b = 1 testează nedeplasarea; un R^2 mic este de așteptat cu o aproximare zilnică zgomotoasă.'
            }
        },
        {
            correct: 0,
            en: {
                title: "Uncertainty of the half-life",
                text: "For the S&P 500, alpha + beta = 0.9947 (half-life 131 days); a parametric bootstrap from the fitted model gives [0.983; 1.000], and a bootstrap test simulated under IGARCH gives p = 0.17. What follows?",
                options: [
                    "The half-life is very imprecise (about 41 days to infinity), and IGARCH is not rejected by the test under the null",
                    "IGARCH is rejected, because the point estimate is below 1",
                    "The interval reaching 1 is by itself a valid test that rejects IGARCH",
                    "The half-life interval is symmetric around 131 days"
                ],
                correctExplanation: "ln(0.5)/ln(x) explodes as x approaches 1, so the half-life interval is huge and skewed. The percentile interval is truncated by the constraint alpha + beta <= 1, so the IGARCH question needs a test simulated under the null, which gives p = 0.17.",
                incorrectExplanation: "A truncated percentile interval is not a test (Andrews, 2000), a point estimate below 1 proves nothing, and the half-life interval is very skewed; the test simulated under IGARCH does not reject."
            },
            ro: {
                title: "Incertitudinea timpului de înjumătățire",
                text: "Pentru S&P 500, alpha + beta = 0,9947 (timp de înjumătățire 131 de zile); un bootstrap parametric din modelul estimat dă [0,983; 1,000], iar un test bootstrap simulat sub IGARCH dă p = 0,17. Ce rezultă?",
                options: [
                    "Timpul de înjumătățire este foarte imprecis (de la circa 41 de zile la infinit), iar IGARCH nu este respins de testul sub ipoteza nulă",
                    "IGARCH este respins, deoarece estimarea punctuală este sub 1",
                    "Faptul că intervalul atinge 1 este în sine un test valid care respinge IGARCH",
                    "Intervalul pentru timpul de înjumătățire este simetric în jurul a 131 de zile"
                ],
                correctExplanation: "ln(0,5)/ln(x) explodează cînd x se apropie de 1, deci intervalul pentru timpul de înjumătățire este uriaș și asimetric. Intervalul percentil este trunchiat de restricția alpha + beta <= 1, deci întrebarea despre IGARCH cere un test simulat sub ipoteza nulă, care dă p = 0,17.",
                incorrectExplanation: "Un interval percentil trunchiat nu este un test (Andrews, 2000), o estimare punctuală sub 1 nu dovedește nimic, iar intervalul pentru timpul de înjumătățire este foarte asimetric; testul simulat sub IGARCH nu respinge."
            }
        },
        {
            correct: 3,
            en: {
                title: 'Limits of GARCH',
                text: 'Which of the following is a documented limitation of GARCH(1,1) discussed in the chapter?',
                options: [
                    'It cannot produce volatility clustering',
                    'It cannot be estimated on daily data',
                    'It always gives negative variances',
                    'Its autocorrelation of squared returns decays geometrically, while in the data the autocorrelation of absolute returns shows slow, long-memory decay'
                ],
                correctExplanation: 'GARCH(1,1) has a single time scale; FIGARCH (Baillie, Bollerslev and Mikkelsen, 1996) and realised-volatility models (Chapter 9) address long memory. Structural breaks can also inflate alpha + beta.',
                incorrectExplanation: 'GARCH does produce clustering; its main limits are geometric (short) memory, spurious persistence under breaks and the reaction lag.'
            },
            ro: {
                title: 'Limitele GARCH',
                text: 'Care dintre următoarele este o limită documentată a GARCH(1,1), discutată în capitol?',
                options: [
                    'Nu poate produce gruparea volatilității',
                    'Nu poate fi estimat pe date zilnice',
                    'Dă mereu dispersii negative',
                    'Autocorelația pătratelor randamentelor scade geometric, în timp ce în date autocorelația randamentelor absolute scade lent, cu memorie lungă'
                ],
                correctExplanation: 'GARCH(1,1) are o singură scară de timp; FIGARCH (Baillie, Bollerslev și Mikkelsen, 1996) și modelele de volatilitate realizată (Capitolul 9) tratează memoria lungă. Rupturile structurale pot și ele umfla alpha + beta.',
                incorrectExplanation: 'GARCH produce gruparea; limitele principale sînt memoria geometrică (scurtă), persistența falsă sub rupturi structurale și întîrzierea reacției.'
            }
        },
        {
            correct: 0,
            en: {
                title: "Spot the error: GARCH half-life",
                text: "An AI assistant writes: \"The GARCH(1,1) estimates are alpha = 0.10 and beta = 0.88, so the half-life of a volatility shock is ln(0.5)/ln(0.88), about 5.4 days.\" What is the error?",
                options: [
                    "The half-life depends on the persistence alpha + beta: ln(0.5)/ln(0.98), about 34 days",
                    "The half-life is ln(0.5)/ln(0.10), since alpha measures the reaction to news",
                    "The half-life of a GARCH(1,1) is always infinite",
                    "The half-life must be computed from omega/(1 - alpha - beta)"
                ],
                correctExplanation: "Variance forecasts revert to the long-run level at rate alpha + beta: E_t[sigma^2_{t+h}] - sigma^2 = (alpha + beta)^(h-1) (sigma^2_{t+1} - sigma^2). With alpha + beta = 0.98 the half-life is ln(0.5)/ln(0.98), about 34.3 days.",
                incorrectExplanation: "The speed of mean reversion of the variance forecast is alpha + beta, not beta alone; here ln(0.5)/ln(0.98) gives about 34 days."
            },
            ro: {
                title: "Găsiți eroarea: timpul de înjumătățire GARCH",
                text: "Un asistent AI scrie: „Estimările GARCH(1,1) sînt alpha = 0,10 și beta = 0,88, deci timpul de înjumătățire al unui șoc de volatilitate este ln(0,5)/ln(0,88), circa 5,4 zile.” Care este eroarea?",
                options: [
                    "Timpul de înjumătățire depinde de persistența alpha + beta: ln(0,5)/ln(0,98), circa 34 de zile",
                    "Timpul de înjumătățire este ln(0,5)/ln(0,10), deoarece alpha măsoară reacția la știri",
                    "Timpul de înjumătățire al unui GARCH(1,1) este întotdeauna infinit",
                    "Timpul de înjumătățire se calculează din omega/(1 - alpha - beta)"
                ],
                correctExplanation: "Prognozele dispersiei revin la nivelul de termen lung cu rata alpha + beta: E_t[sigma^2_{t+h}] - sigma^2 = (alpha + beta)^(h-1) (sigma^2_{t+1} - sigma^2). Cu alpha + beta = 0,98, timpul de înjumătățire este ln(0,5)/ln(0,98), circa 34,3 zile.",
                incorrectExplanation: "Viteza de revenire la medie a prognozei dispersiei este alpha + beta, nu doar beta; aici ln(0,5)/ln(0,98) dă circa 34 de zile."
            }
        },
        {
            correct: 2,
            en: {
                title: "Spot the error: reading a diagnostic test",
                text: "An AI assistant writes: \"The Ljung-Box test on the squared standardised residuals of the GARCH-t model gives Q(10) = 8.1 with p = 0.62. We reject the null of no remaining ARCH effects, so the model is inadequate.\" What is the error?",
                options: [
                    "The Ljung-Box test cannot be applied to standardised residuals",
                    "Q(10) = 8.1 is too large; with 10 lags it must be below 1",
                    "A p-value of 0.62 means the null is not rejected: there is no evidence of remaining ARCH effects",
                    "A p-value of 0.62 means the model explains 62% of the variance"
                ],
                correctExplanation: "The null of the test is no autocorrelation in the squared standardised residuals. A p-value of 0.62 is far above 5%, so the null is not rejected: the test finds no evidence of remaining volatility clustering.",
                incorrectExplanation: "The test and the statistic are fine; the p-value is misread: 0.62 is far above 5%, so there is no evidence of remaining ARCH effects."
            },
            ro: {
                title: "Găsiți eroarea: interpretarea unui test de diagnostic",
                text: "Un asistent AI scrie: „Testul Ljung-Box pe pătratele reziduurilor standardizate ale modelului GARCH-t dă Q(10) = 8,1 cu p = 0,62. Respingem ipoteza nulă de absență a efectelor ARCH rămase, deci modelul este inadecvat.” Care este eroarea?",
                options: [
                    "Testul Ljung-Box nu se poate aplica reziduurilor standardizate",
                    "Q(10) = 8,1 este prea mare; cu 10 decalaje trebuie să fie sub 1",
                    "O valoare p de 0,62 înseamnă că ipoteza nulă nu este respinsă: nu există dovezi de efecte ARCH rămase",
                    "O valoare p de 0,62 înseamnă că modelul explică 62% din dispersie"
                ],
                correctExplanation: "Ipoteza nulă a testului este absența autocorelației în pătratele reziduurilor standardizate. O valoare p de 0,62 este mult peste 5%, deci ipoteza nulă nu este respinsă: testul nu găsește dovezi de grupare a volatilității rămasă.",
                incorrectExplanation: "Testul și statistica sînt corecte; valoarea p este interpretată greșit: 0,62 este mult peste 5%, deci nu există dovezi de efecte ARCH rămase."
            }
        }
    ]
};

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
                    'Randamentele sunt puternic predictibile ca direcție',
                    'Dispersia randamentelor este constantă în timp',
                    'Mărimea mișcării de mâine este predictibilă, deși direcția ei aproape nu este',
                    'Datele conțin o eroare de calcul, deoarece cele două trebuie să fie egale'
                ],
                correctExplanation: 'Pătratele randamentelor măsoară mărimea mișcărilor. Autocorelația lor puternică și persistentă este gruparea volatilității: mișcările mari urmează mișcărilor mari, de orice semn.',
                incorrectExplanation: 'Direcția este aproape imprevizibilă; ceea ce persistă este mărimea mișcărilor (gruparea volatilității).'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Conditional variance',
                text: 'In the model r_t = mu + sigma_t z_t, what is sigma_t^2?',
                options: [
                    'The variance of r_t given the information available at the end of day t-1',
                    'The sample variance of all returns',
                    'The variance of the innovation z_t',
                    'The squared return of day t'
                ],
                correctExplanation: 'sigma_t^2 = Var(r_t | F_{t-1}) is the conditional variance; it changes every day as new information arrives. The unconditional variance is its long-run average.',
                incorrectExplanation: 'sigma_t^2 is the conditional variance, Var(r_t | F_{t-1}); z_t has unit variance and r_t^2 is only a noisy proxy.'
            },
            ro: {
                title: 'Dispersia condiționată',
                text: 'În modelul r_t = mu + sigma_t z_t, ce este sigma_t^2?',
                options: [
                    'Dispersia lui r_t dată fiind informația disponibilă la sfârșitul zilei t-1',
                    'Dispersia de selecție a tuturor randamentelor',
                    'Dispersia inovației z_t',
                    'Pătratul randamentului din ziua t'
                ],
                correctExplanation: 'sigma_t^2 = Var(r_t | F_{t-1}) este dispersia condiționată; se schimbă zilnic, pe măsură ce apare informație nouă. Dispersia necondiționată este media ei de termen lung.',
                incorrectExplanation: 'sigma_t^2 este dispersia condiționată, Var(r_t | F_{t-1}); z_t are dispersia 1, iar r_t^2 este doar o aproximare zgomotoasă.'
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
                correctExplanation: 'Substituting backwards, GARCH(1,1) equals an ARCH(infinity) with weights alpha * beta^(j-1): long memory in variance with only three parameters.',
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
                correctExplanation: 'Prin substituție înapoi, GARCH(1,1) este un ARCH(infinit) cu ponderi alpha * beta^(j-1): memorie în dispersie cu doar trei parametri.',
                incorrectExplanation: 'Dispersia decalată dă un ARCH de ordin infinit cu ponderi descrescătoare geometric, deci gruparea persistentă cere doar trei parametri.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Unconditional variance',
                text: 'A GARCH(1,1) has omega = 0.05, alpha = 0.10, beta = 0.85 (returns in %). What is its long-run (unconditional) daily variance?',
                options: [
                    '0.05',
                    '0.50',
                    '0.95',
                    '1.00'
                ],
                correctExplanation: 'sigma^2 = omega / (1 - alpha - beta) = 0.05 / 0.05 = 1.00 (%^2 per day), i.e. a daily volatility of 1%.',
                incorrectExplanation: 'Use sigma^2 = omega / (1 - alpha - beta) = 0.05 / 0.05 = 1.00.'
            },
            ro: {
                title: 'Dispersia necondiționată',
                text: 'Un GARCH(1,1) are omega = 0,05, alpha = 0,10, beta = 0,85 (randamente în %). Care este dispersia zilnică de termen lung (necondiționată)?',
                options: [
                    '0,05',
                    '0,50',
                    '0,95',
                    '1,00'
                ],
                correctExplanation: 'sigma^2 = omega / (1 - alpha - beta) = 0,05 / 0,05 = 1,00 (%^2 pe zi), adică o volatilitate zilnică de 1%.',
                incorrectExplanation: 'Folosiți sigma^2 = omega / (1 - alpha - beta) = 0,05 / 0,05 = 1,00.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Half-life',
                text: 'With alpha + beta = 0.95, after how many days has half of a variance shock disappeared?',
                options: [
                    'About 5 days',
                    'About 13.5 days',
                    'About 69 days',
                    'Never'
                ],
                correctExplanation: 'The half-life is ln(0.5) / ln(alpha + beta) = ln(0.5) / ln(0.95) = 13.5 days.',
                incorrectExplanation: 'Solve (alpha + beta)^h = 0.5: h = ln(0.5) / ln(0.95) = 13.5 days.'
            },
            ro: {
                title: 'Timpul de înjumătățire',
                text: 'Cu alpha + beta = 0,95, după câte zile a dispărut jumătate dintr-un șoc de dispersie?',
                options: [
                    'Circa 5 zile',
                    'Circa 13,5 zile',
                    'Circa 69 de zile',
                    'Niciodată'
                ],
                correctExplanation: 'Timpul de înjumătățire este ln(0,5) / ln(alpha + beta) = ln(0,5) / ln(0,95) = 13,5 zile.',
                incorrectExplanation: 'Rezolvați (alpha + beta)^h = 0,5: h = ln(0,5) / ln(0,95) = 13,5 zile.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'One-step recursion',
                text: 'omega = 0.05, alpha = 0.10, beta = 0.85, yesterday\'s variance 1.0 and yesterday\'s shock -2%. What is today\'s variance?',
                options: [
                    '0.90',
                    '1.00',
                    '1.30',
                    '1.50'
                ],
                correctExplanation: 'sigma_t^2 = 0.05 + 0.10 x 4 + 0.85 x 1.0 = 0.05 + 0.40 + 0.85 = 1.30.',
                incorrectExplanation: 'Apply the recursion step by step: 0.05 + 0.10 x (-2)^2 + 0.85 x 1.0 = 1.30.'
            },
            ro: {
                title: 'Recursia pe un pas',
                text: 'omega = 0,05, alpha = 0,10, beta = 0,85, dispersia de ieri 1,0 și șocul de ieri -2%. Care este dispersia de azi?',
                options: [
                    '0,90',
                    '1,00',
                    '1,30',
                    '1,50'
                ],
                correctExplanation: 'sigma_t^2 = 0,05 + 0,10 x 4 + 0,85 x 1,0 = 0,05 + 0,40 + 0,85 = 1,30.',
                incorrectExplanation: 'Aplicați recursia pas cu pas: 0,05 + 0,10 x (-2)^2 + 0,85 x 1,0 = 1,30.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Multi-step forecasts',
                text: 'In a stationary GARCH(1,1), how does the h-step variance forecast behave as h grows?',
                options: [
                    'It converges to the long-run variance, closing the gap by the factor alpha + beta each day',
                    'It stays equal to tomorrow\'s variance forever',
                    'It grows without bound',
                    'It oscillates between high and low values'
                ],
                correctExplanation: 'E_t sigma_{t+h}^2 = sigma^2 + (alpha + beta)^(h-1) (sigma_{t+1}^2 - sigma^2): mean reversion towards the long-run variance.',
                incorrectExplanation: 'With alpha + beta < 1 the forecast reverts geometrically to omega / (1 - alpha - beta); a flat forecast is the EWMA/IGARCH case.'
            },
            ro: {
                title: 'Prognoze pe mai mulți pași',
                text: 'Într-un GARCH(1,1) staționar, cum se comportă prognoza dispersiei pe h pași când h crește?',
                options: [
                    'Converge spre dispersia de termen lung, reducând distanța cu factorul alpha + beta în fiecare zi',
                    'Rămâne egală pentru totdeauna cu dispersia de mâine',
                    'Crește nelimitat',
                    'Oscilează între valori mari și mici'
                ],
                correctExplanation: 'E_t sigma_{t+h}^2 = sigma^2 + (alpha + beta)^(h-1) (sigma_{t+1}^2 - sigma^2): revenire la medie spre dispersia de termen lung.',
                incorrectExplanation: 'Cu alpha + beta < 1 prognoza revine geometric spre omega / (1 - alpha - beta); prognoza constantă este cazul EWMA/IGARCH.'
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
                    'Dă mai multă pondere observațiilor vechi decât celor recente',
                    'Este un IGARCH(1,1) cu omega = 0, alpha = 0,06, beta = 0,94, deci prognoza sa este constantă în orizont'
                ],
                correctExplanation: 'sigma_t^2 = 0,94 sigma_{t-1}^2 + 0,06 r_{t-1}^2 este un GARCH cu alpha + beta = 1 și omega = 0: fără revenire la medie, prognoza pentru orice orizont este dispersia de mâine.',
                incorrectExplanation: 'EWMA este cazul particular IGARCH cu omega = 0; nu are dispersie de termen lung și nici revenire la medie.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Fat tails from clustering',
                text: 'A GARCH(1,1) with Normal innovations z_t generates returns with kurtosis...',
                options: [
                    'exactly 3, because z_t is Normal',
                    'above 3, because mixing periods of low and high variance produces heavy tails',
                    'below 3, because the variance is bounded',
                    'that cannot be computed'
                ],
                correctExplanation: 'The kurtosis is 3[1 - (alpha+beta)^2] / [1 - (alpha+beta)^2 - 2 alpha^2] > 3 when finite: clustering alone creates fat tails.',
                incorrectExplanation: 'Even with Normal innovations, a time-varying variance makes the unconditional distribution leptokurtic.'
            },
            ro: {
                title: 'Cozi groase din grupare',
                text: 'Un GARCH(1,1) cu inovații z_t Normale generează randamente cu aplatizarea...',
                options: [
                    'exact 3, deoarece z_t este Normal',
                    'peste 3, deoarece amestecul perioadelor cu dispersie mică și mare produce cozi groase',
                    'sub 3, deoarece dispersia este mărginită',
                    'care nu poate fi calculată'
                ],
                correctExplanation: 'Aplatizarea este 3[1 - (alpha+beta)^2] / [1 - (alpha+beta)^2 - 2 alpha^2] > 3 când este finită: gruparea singură creează cozi groase.',
                incorrectExplanation: 'Chiar și cu inovații Normale, o dispersie variabilă în timp face distribuția necondiționată leptocurtică.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Quasi-maximum likelihood',
                text: 'You estimate a GARCH by maximising the Normal likelihood, but the innovations are heavy-tailed. What should you do?',
                options: [
                    'Nothing: the classical standard errors remain valid',
                    'Abandon GARCH, since the estimates are inconsistent',
                    'Keep the estimates (consistent under correct mean and variance equations) but use robust Bollerslev-Wooldridge standard errors',
                    'Multiply the standard errors by the kurtosis'
                ],
                correctExplanation: 'Quasi-maximum likelihood is consistent if the first two conditional moments are correct; inference needs the sandwich covariance A^-1 B A^-1.',
                incorrectExplanation: 'The QML estimates stay consistent; only the standard errors must be replaced by the robust sandwich form.'
            },
            ro: {
                title: 'Cvasi-verosimilitate maximă',
                text: 'Estimați un GARCH maximizând verosimilitatea Normală, dar inovațiile au cozi groase. Ce trebuie să faceți?',
                options: [
                    'Nimic: erorile standard clasice rămân valide',
                    'Renunțați la GARCH, deoarece estimările sunt inconsistente',
                    'Păstrați estimările (consistente dacă ecuațiile mediei și dispersiei sunt corecte), dar folosiți erorile standard robuste Bollerslev-Wooldridge',
                    'Înmulțiți erorile standard cu aplatizarea'
                ],
                correctExplanation: 'Cvasi-verosimilitatea maximă este consistentă dacă primele două momente condiționate sunt corecte; inferența cere covarianța „sandviș” A^-1 B A^-1.',
                incorrectExplanation: 'Estimările QML rămân consistente; doar erorile standard trebuie înlocuite cu forma robustă „sandviș”.'
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
                    'Inovațiile sunt apropiate de distribuția Normală',
                    'Modelul este greșit specificat, deoarece nu trebuie să fie întreg',
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
                    'Cozi mai subțiri decât distribuția Normală',
                    'O coadă dreaptă mai lungă: câștigurile mari mai probabile decât pierderile mari',
                    'Că modelul nu este identificat',
                    'O coadă stângă mai lungă: pierderile mari mai probabile decât câștigurile mari'
                ],
                correctExplanation: 'lambda < 0 înclină densitatea spre stânga; pentru S&P 500, GJR-GARCH dă lambda de circa -0,15.',
                incorrectExplanation: 'Un lambda negativ înseamnă asimetrie la stânga: coada pierderilor este mai lungă.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'GJR-GARCH',
                text: 'In GJR-GARCH, sigma_t^2 = omega + (alpha + gamma I_{t-1}) eps_{t-1}^2 + beta sigma_{t-1}^2 with I_{t-1} = 1 if eps_{t-1} < 0. What does gamma > 0 mean?',
                options: [
                    'Good news raises volatility more than bad news',
                    'Negative shocks raise next-day variance more than positive shocks of the same size',
                    'The variance is always constant',
                    'The model is not stationary'
                ],
                correctExplanation: 'After a negative shock the slope is alpha + gamma, after a positive one only alpha: the leverage effect.',
                incorrectExplanation: 'gamma is the extra slope for negative shocks, so gamma > 0 means bad news matters more (leverage effect).'
            },
            ro: {
                title: 'GJR-GARCH',
                text: 'În GJR-GARCH, sigma_t^2 = omega + (alpha + gamma I_{t-1}) eps_{t-1}^2 + beta sigma_{t-1}^2 cu I_{t-1} = 1 dacă eps_{t-1} < 0. Ce înseamnă gamma > 0?',
                options: [
                    'Știrile bune cresc volatilitatea mai mult decât știrile proaste',
                    'Șocurile negative cresc dispersia de a doua zi mai mult decât șocurile pozitive de aceeași mărime',
                    'Dispersia este mereu constantă',
                    'Modelul nu este staționar'
                ],
                correctExplanation: 'După un șoc negativ panta este alpha + gamma, după unul pozitiv doar alpha: efectul de levier.',
                incorrectExplanation: 'gamma este panta suplimentară pentru șocurile negative, deci gamma > 0 înseamnă că știrile proaste contează mai mult (efectul de levier).'
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
                correctExplanation: 'Jumătate din șocuri sunt negative, deci în medie panta pe eps^2 este alpha + gamma/2; persistența este alpha + gamma/2 + beta.',
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
                incorrectExplanation: 'EGARCH lucrează cu logaritmul dispersiei, ceea ce păstrează dispersia pozitivă și permite intrarea semnului știrilor prin gamma.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'News impact curve',
                text: 'The news impact curve of Engle and Ng (1993) plots...',
                options: [
                    'the price level against trading volume',
                    'the autocorrelation of returns against the lag',
                    'the implied volatility against the strike price',
                    'next-day variance against yesterday\'s shock, holding the lagged variance fixed'
                ],
                correctExplanation: 'It isolates how a model turns one day of news into tomorrow\'s variance: symmetric parabola for GARCH, tilted for GJR and EGARCH.',
                incorrectExplanation: 'The news impact curve is sigma_t^2 as a function of eps_{t-1} with sigma_{t-1}^2 held at a fixed level.'
            },
            ro: {
                title: 'Curba de impact a știrilor',
                text: 'Curba de impact a știrilor a lui Engle și Ng (1993) reprezintă...',
                options: [
                    'nivelul prețului în funcție de volumul tranzacționat',
                    'autocorelația randamentelor în funcție de decalaj',
                    'volatilitatea implicită în funcție de prețul de exercitare',
                    'dispersia de a doua zi în funcție de șocul de ieri, cu dispersia decalată ținută fixă'
                ],
                correctExplanation: 'Ea izolează modul în care un model transformă o zi de știri în dispersia de mâine: parabolă simetrică la GARCH, înclinată la GJR și EGARCH.',
                incorrectExplanation: 'Curba de impact a știrilor este sigma_t^2 în funcție de eps_{t-1}, cu sigma_{t-1}^2 ținut la un nivel fix.'
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
                    'Efectul de levier este un fenomen al acțiunilor; la aur, creșterile de preț sunt direcția mai volatilă (comportament de activ de refugiu)',
                    'Bitcoin are cel mai puternic efect de levier',
                    'Un gamma negativ înseamnă că modelul este greșit'
                ],
                correctExplanation: 'La aur, creșterile din perioadele agitate cresc volatilitatea mai mult decât scăderile: o asimetrie inversă, consistentă cu un activ de refugiu. Bitcoin nu are asimetrie semnificativă.',
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
                correctExplanation: 'If the variance equation is adequate, z_t^2 should be uncorrelated: Q(10) on z_t^2 and the LM test must not reject.',
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
                correctExplanation: 'Dacă ecuația dispersiei este adecvată, z_t^2 trebuie să fie necorelate: Q(10) pe z_t^2 și testul LM nu trebuie să respingă.',
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
                    'Cele două modele nu sunt imbricate',
                    'BIC penalizează fiecare parametru suplimentar cu ln n (circa 8,8 aici), mai mult decât câștigul de verosimilitate, iar testul LR folosește valoarea critică 3,84'
                ],
                correctExplanation: 'BIC = -2 log L + k ln n; cu n de circa 6.700, penalizarea pentru un parametru depășește câștigul LR de 4,93, deși testul LR respinge la 5%.',
                incorrectExplanation: 'Modelele sunt imbricate; dezacordul vine din penalizarea mai mare ln n a BIC, comparată cu valoarea critică chi-pătrat.'
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
                correctExplanation: 'QLIKE and MSE are robust to noise in the volatility proxy: the ranking with r_t^2 matches the ranking with the true variance. QLIKE also penalises under-prediction more.',
                incorrectExplanation: 'QLIKE is robust to a noisy proxy (Patton, 2011) and penalises under-prediction more heavily, not less.'
            },
            ro: {
                title: 'QLIKE',
                text: 'De ce folosesc Patton (2011) și acest capitol pierderea QLIKE r_t^2 / h_t + ln h_t pentru a compara prognozele de volatilitate?',
                options: [
                    'Pentru că ignoră erorile mari',
                    'Pentru că ordonează corect prognozele chiar și când aproximarea r_t^2 este zgomotoasă',
                    'Pentru că nu are nevoie de o aproximare a volatilității',
                    'Pentru că recompensează subestimarea riscului'
                ],
                correctExplanation: 'QLIKE și MSE sunt robuste la zgomotul aproximării: ordonarea cu r_t^2 coincide cu ordonarea cu dispersia reală. QLIKE penalizează în plus mai mult subestimarea.',
                incorrectExplanation: 'QLIKE este robustă la o aproximare zgomotoasă (Patton, 2011) și penalizează mai mult subestimarea, nu mai puțin.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Mincer-Zarnowitz',
                text: 'A Mincer-Zarnowitz regression r_t^2 = a + b h_t for one-day GARCH forecasts gives b close to 1 but R^2 of only about 0.25. What is the right conclusion?',
                options: [
                    'The forecasts are useless',
                    'The model is biased',
                    'The forecasts are unbiased; the low R^2 reflects the noise of r_t^2 as a proxy',
                    'The regression must be run without a constant'
                ],
                correctExplanation: 'Since r_t^2 = sigma_t^2 z_t^2, even a perfect forecast explains only part of the variation of r_t^2 (Andersen and Bollerslev, 1998).',
                incorrectExplanation: 'a = 0, b = 1 tests unbiasedness; a low R^2 is expected with a noisy daily proxy.'
            },
            ro: {
                title: 'Mincer-Zarnowitz',
                text: 'O regresie Mincer-Zarnowitz r_t^2 = a + b h_t pentru prognozele GARCH pe o zi dă b aproape de 1, dar R^2 de doar circa 0,25. Care este concluzia corectă?',
                options: [
                    'Prognozele sunt inutile',
                    'Modelul este deplasat',
                    'Prognozele sunt nedeplasate; R^2 mic reflectă zgomotul lui r_t^2 ca aproximare',
                    'Regresia trebuie estimată fără termen liber'
                ],
                correctExplanation: 'Deoarece r_t^2 = sigma_t^2 z_t^2, chiar și o prognoză perfectă explică doar o parte din variația lui r_t^2 (Andersen și Bollerslev, 1998).',
                incorrectExplanation: 'a = 0, b = 1 testează nedeplasarea; un R^2 mic este de așteptat cu o aproximare zilnică zgomotoasă.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Uncertainty of the half-life',
                text: 'For the S&P 500, alpha + beta = 0.9947 (half-life 131 days), and a parametric bootstrap gives a 95% interval of [0.984; 1.000]. What follows?',
                options: [
                    'The half-life is very imprecise: from about 43 days to infinity; IGARCH cannot be rejected',
                    'The half-life is known to within a few days',
                    'The bootstrap proves that volatility has no memory',
                    'The interval for the half-life is symmetric around 131 days'
                ],
                correctExplanation: 'ln(0.5)/ln(x) explodes as x approaches 1, so a narrow interval for alpha + beta becomes a huge, skewed interval for the half-life.',
                incorrectExplanation: 'Near 1, small changes in alpha + beta change the half-life enormously; the upper bound reaches 1, i.e. an infinite half-life.'
            },
            ro: {
                title: 'Incertitudinea timpului de înjumătățire',
                text: 'Pentru S&P 500, alpha + beta = 0,9947 (timp de înjumătățire 131 de zile), iar un bootstrap parametric dă intervalul de 95% [0,984; 1,000]. Ce rezultă?',
                options: [
                    'Timpul de înjumătățire este foarte imprecis: de la circa 43 de zile la infinit; IGARCH nu poate fi respins',
                    'Timpul de înjumătățire este cunoscut cu o precizie de câteva zile',
                    'Bootstrap-ul dovedește că volatilitatea nu are memorie',
                    'Intervalul pentru timpul de înjumătățire este simetric în jurul a 131 de zile'
                ],
                correctExplanation: 'ln(0,5)/ln(x) explodează când x se apropie de 1, deci un interval îngust pentru alpha + beta devine unul uriaș și asimetric pentru timpul de înjumătățire.',
                incorrectExplanation: 'Lângă 1, schimbări mici ale lui alpha + beta modifică enorm timpul de înjumătățire; limita superioară atinge 1, adică un timp de înjumătățire infinit.'
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
                    'Its autocorrelation of squared returns decays geometrically, while in the data absolute returns show slow, long-memory decay'
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
                    'Autocorelația pătratelor randamentelor scade geometric, în timp ce în date randamentele absolute scad lent, cu memorie lungă'
                ],
                correctExplanation: 'GARCH(1,1) are o singură scară de timp; FIGARCH (Baillie, Bollerslev și Mikkelsen, 1996) și modelele de volatilitate realizată (Capitolul 9) tratează memoria lungă. Rupturile structurale pot și ele umfla alpha + beta.',
                incorrectExplanation: 'GARCH produce gruparea; limitele principale sunt memoria geometrică (scurtă), persistența falsă sub rupturi structurale și întârzierea reacției.'
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
                text: "Un asistent AI scrie: „Estimările GARCH(1,1) sunt alpha = 0,10 și beta = 0,88, deci timpul de înjumătățire al unui șoc de volatilitate este ln(0,5)/ln(0,88), circa 5,4 zile.” Care este eroarea?",
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
                correctExplanation: "The null of the test is no autocorrelation in the squared standardised residuals. A p-value of 0.62 is far above 5%, so the null is not rejected: the GARCH model has absorbed the volatility clustering.",
                incorrectExplanation: "The test and the statistic are fine; the p-value is misread: 0.62 is far above 5%, so there is no evidence of remaining ARCH effects."
            },
            ro: {
                title: "Găsiți eroarea: citirea unui test de diagnostic",
                text: "Un asistent AI scrie: „Testul Ljung-Box pe pătratele reziduurilor standardizate ale modelului GARCH-t dă Q(10) = 8,1 cu p = 0,62. Respingem ipoteza nulă de absență a efectelor ARCH rămase, deci modelul este inadecvat.” Care este eroarea?",
                options: [
                    "Testul Ljung-Box nu se poate aplica reziduurilor standardizate",
                    "Q(10) = 8,1 este prea mare; cu 10 decalaje trebuie să fie sub 1",
                    "O valoare p de 0,62 înseamnă că ipoteza nulă nu este respinsă: nu există dovezi de efecte ARCH rămase",
                    "O valoare p de 0,62 înseamnă că modelul explică 62% din dispersie"
                ],
                correctExplanation: "Ipoteza nulă a testului este absența autocorelației în pătratele reziduurilor standardizate. O valoare p de 0,62 este mult peste 5%, deci ipoteza nulă nu este respinsă: modelul GARCH a absorbit gruparea volatilității.",
                incorrectExplanation: "Testul și statistica sunt corecte; valoarea p este citită greșit: 0,62 este mult peste 5%, deci nu există dovezi de efecte ARCH rămase."
            }
        }
    ]
};

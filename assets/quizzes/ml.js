// ============================================================
// Quiz bank for chapter id 'ml': Machine Learning in Finance (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['ml'] = {
    draw: 20,
    questions: [
        {
            correct: 1,
            en: {
                title: 'Signal-to-noise',
                text: 'Why is predicting asset returns harder than a typical machine learning task such as image recognition?',
                options: [
                    'Financial datasets are always too small to fit any model',
                    'The signal-to-noise ratio is very low and the data-generating process changes as markets adapt to exploited patterns',
                    'Returns are deterministic, so ML adds no value',
                    'Financial data cannot be stored in tabular form'
                ],
                correctExplanation: 'Predictable components of returns are tiny relative to noise, and once a pattern is exploited it tends to disappear (adaptive markets), so the relationship is non-stationary.',
                incorrectExplanation: 'The key problems are a low signal-to-noise ratio and non-stationarity, not data size or format.'
            },
            ro: {
                title: 'Raportul semnal-zgomot',
                text: 'De ce este prognoza randamentelor mai dificilă decît o sarcină tipică de machine learning, cum ar fi recunoașterea imaginilor?',
                options: [
                    'Seturile de date financiare sînt întotdeauna prea mici pentru orice model',
                    'Raportul semnal-zgomot este foarte mic, iar procesul generator al datelor se schimbă pe măsură ce piața se adaptează la tiparele exploatate',
                    'Randamentele sînt deterministe, deci ML nu aduce nimic',
                    'Datele financiare nu pot fi stocate în formă tabelară'
                ],
                correctExplanation: 'Componenta predictibilă a randamentelor este foarte mică față de zgomot, iar un tipar exploatat tinde să dispară (piețe adaptive), deci relația este nestaționară.',
                incorrectExplanation: 'Problemele esențiale sînt raportul semnal-zgomot scăzut și nestaționaritatea, nu volumul sau formatul datelor.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Forecast tests for nested models',
                text: 'You compare a logistic regression with 14 features against a constant forecast (the same logit with all slopes set to zero) using the Diebold-Mariano test on squared errors. What is the problem?',
                options: [
                    'The Diebold-Mariano test requires Normally distributed forecast errors',
                    'Squared errors cannot be used for probability forecasts',
                    'The models are nested: under the null the larger model estimates zeros with noise, so the DM statistic is not asymptotically N(0,1) and is undersized; use the Clark-West adjustment',
                    'Nothing: the Diebold-Mariano test is valid for any pair of models'
                ],
                correctExplanation: 'Clark and West (2007) add the term $(\\hat p_0 - \\hat p_1)^2$ back to the loss differential, which removes the noise a correctly nested model pays for estimating zero coefficients.',
                incorrectExplanation: 'Think about what the large model does under the null that it adds nothing: it still estimates 14 coefficients, and their noise inflates its loss.'
            },
            ro: {
                title: 'Teste de prognoză pentru modele imbricate',
                text: 'Comparați o regresie logistică cu 14 caracteristici cu o prognoză constantă (același logit cu toate pantele zero) prin testul Diebold-Mariano pe erori pătratice. Care este problema?',
                options: [
                    'Testul Diebold-Mariano cere erori de prognoză din distribuția Normală',
                    'Erorile pătratice nu pot fi folosite pentru prognoze de probabilitate',
                    'Modelele sînt imbricate: sub ipoteza nulă modelul mare estimează cu zgomot coeficienți nuli, deci statistica DM nu este asimptotic N(0,1), iar testul are un nivel efectiv prea mic; folosiți corecția Clark-West',
                    'Nimic: testul Diebold-Mariano este valid pentru orice pereche de modele'
                ],
                correctExplanation: 'Clark și West (2007) adaugă înapoi termenul $(\\hat p_0 - \\hat p_1)^2$ la diferența pierderilor, ceea ce elimină zgomotul de estimare care penalizează un model imbricat corect specificat cînd estimează coeficienți nuli.',
                incorrectExplanation: 'Gîndiți-vă ce face modelul mare sub ipoteza nulă că nu adaugă nimic: estimează totuși 14 coeficienți, iar zgomotul lor îi mărește pierderea.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Testing directional accuracy',
                text: 'Over 6,269 days, a model predicts "up" on 98.3% of days and is right 57.6% of the time, while 58.1% of the days are up. Which one-sided test answers whether its signs carry positive information?',
                options: [
                    'The Pesaran-Timmermann test, which compares the hit rate with the rate expected under independence given both marginal frequencies (here 57.8%, above the hit rate, so it cannot reject)',
                    'A binomial test of the hit rate against 50%',
                    'A t-test of the accuracy against 0.5 with i.i.d. standard errors',
                    'A McNemar test against a coin flip'
                ],
                correctExplanation: 'Under independence the expected hit rate is $\\hat p_y\\hat p_x + (1-\\hat p_y)(1-\\hat p_x) = 0.578$; the observed 0.576 is below it, so the statistic is negative for any $n$ (here $PT = -1.28$ over 6,269 days). With overlapping labels the variance must also be HAC-adjusted.',
                incorrectExplanation: 'A 50% benchmark ignores that the market goes up on 58% of days and that the model almost always says "up"; the right null conditions on both frequencies.'
            },
            ro: {
                title: 'Testarea acurateței direcționale',
                text: 'Pe 6.269 de zile, un model prezice „sus” în 98,3% din zile și are dreptate în 57,6% din cazuri, iar 58,1% dintre zile sînt „sus”. Ce test unilateral arată dacă semnele lui conțin informație pozitivă?',
                options: [
                    'Testul Pesaran-Timmermann, care compară rata de succes cu rata așteptată sub independență, date fiind ambele frecvențe marginale (aici 57,8%, peste rata de succes, deci nu poate respinge)',
                    'Un test binomial al ratei de succes față de 50%',
                    'Un test t al acurateței față de 0,5, cu erori standard i.i.d.',
                    'Un test McNemar față de aruncarea unei monede'
                ],
                correctExplanation: 'Sub independență rata așteptată este $\\hat p_y\\hat p_x + (1-\\hat p_y)(1-\\hat p_x) = 0,578$; valoarea observată 0,576 este sub ea, deci statistica este negativă pentru orice $n$ (aici $PT = -1,28$ pe 6.269 de zile). Cu etichete suprapuse, varianța trebuie ajustată și HAC.',
                incorrectExplanation: 'Un reper de 50% ignoră faptul că piața crește în 58% dintre zile și că modelul spune aproape mereu „sus”; ipoteza nulă corectă ține cont de ambele frecvențe.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Inference after selection',
                text: 'LASSO selects 3 of 14 features; you then run OLS on these 3 and report their t-statistics as evidence that they predict returns. What is wrong?',
                options: [
                    'Nothing, because OLS removes the shrinkage bias of LASSO',
                    'Only the standard errors are wrong; heteroskedasticity-robust errors fix the problem',
                    'LASSO coefficients are unbiased, so the OLS step is redundant',
                    'The t-statistics ignore the data-driven selection step and are over-optimistic; use post-double selection, double/debiased machine learning or sample splitting'
                ],
                correctExplanation: 'Selection and estimation on the same data make the reported t-statistics conditional on a selection event they ignore; Belloni, Chernozhukov and Hansen (2014) and Chernozhukov et al. (2018) give valid inference for a target coefficient.',
                incorrectExplanation: 'Robust standard errors do not repair a distribution that was distorted by choosing the regressors on the same sample.'
            },
            ro: {
                title: 'Inferența după selecție',
                text: 'LASSO selectează 3 din 14 caracteristici; apoi rulați OLS pe aceste 3 și raportați statisticile lor t drept dovadă că prezic randamentele. Ce este greșit?',
                options: [
                    'Nimic, pentru că OLS elimină biasul de shrinkage al LASSO',
                    'Doar erorile standard sînt greșite; erorile robuste la heteroscedasticitate rezolvă problema',
                    'Coeficienții LASSO sînt nedeplasați, deci pasul OLS este inutil',
                    'Statisticile t ignoră pasul de selecție bazat pe date și sînt prea optimiste; folosiți selecția dublă, machine learning dublu (DML) sau împărțirea eșantionului'
                ],
                correctExplanation: 'Selecția și estimarea pe aceleași date fac statisticile t raportate condiționate de un eveniment de selecție pe care îl ignoră; Belloni, Chernozhukov și Hansen (2014) și Chernozhukov et al. (2018) dau inferență validă pentru un coeficient-țintă.',
                incorrectExplanation: 'Erorile standard robuste nu repară o distribuție deformată de alegerea regresorilor pe același eșantion.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Fractional differentiation',
                text: 'For the S&P 500 log price (2000-2026), the ADF test (constant, 1 lag) first rejects on the FFD series at $d = 0.25$, where the truncated weights ($K = 444$ lags) sum to 0.178. What is the correct reading?',
                options: [
                    'The FFD series is stationary, because the ADF test rejected the unit root at 5%',
                    'The FFD series equals $0.178\\,\\log P_t$ plus a stationary part, so it is still I(1); the ADF rejection is a finite-sample artefact (with AIC-chosen lags it does not reject), and memory should be estimated directly, e.g. by local Whittle',
                    'The sum of the weights is irrelevant as long as the correlation with the price is high',
                    'Any fractional order $d > 0$ makes an I(1) series stationary'
                ],
                correctExplanation: 'Differencing an I(1) series by $d$ gives I($1-d$), stationary only for $d > 1/2$; truncation leaves a scaled random walk. The exact local Whittle estimate for the FFD series is 0.75, CI [0.69; 0.81].',
                incorrectExplanation: 'Write the FFD series as $(\\sum_k w_k)X_t - \\sum_k w_k (X_t - X_{t-k})$ and ask what happens to the first term when $X_t$ has a unit root.'
            },
            ro: {
                title: 'Diferențierea fracționară',
                text: 'Pentru logaritmul prețului S&P 500 (2000-2026), testul ADF (constantă, 1 lag) respinge pentru prima dată pe seria FFD la $d = 0,25$, unde ponderile trunchiate ($K = 444$ lag-uri) au suma 0,178. Care este interpretarea corectă?',
                options: [
                    'Seria FFD este staționară, pentru că testul ADF a respins rădăcina unitară la 5%',
                    'Seria FFD este egală cu $0,178\\,\\log P_t$ plus o parte staționară, deci rămîne I(1); respingerea ADF este un artefact de eșantion finit (cu lag-uri alese prin AIC nu respinge), iar memoria trebuie estimată direct, de exemplu prin local Whittle',
                    'Suma ponderilor nu contează, cît timp corelația cu prețul este mare',
                    'Orice ordin fracționar $d > 0$ face staționară o serie I(1)'
                ],
                correctExplanation: 'Diferențierea unei serii I(1) cu $d$ dă o serie I($1-d$), staționară doar pentru $d > 1/2$; trunchierea lasă un mers aleator scalat. Estimatorul local Whittle exact pentru seria FFD dă 0,75, CI [0,69; 0,81].',
                incorrectExplanation: 'Scrieți seria FFD ca $(\\sum_k w_k)X_t - \\sum_k w_k (X_t - X_{t-k})$ și întrebați-vă ce se întîmplă cu primul termen cînd $X_t$ are rădăcină unitară.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'How small is a small R²?',
                text: 'A predictor of monthly market returns has an out-of-sample $R^2$ of 0.5%. According to Campbell and Thompson (2008), what does this mean for a mean-variance investor?',
                options: [
                    'It is negligible, because any $R^2$ below 1% has no economic value',
                    'It is economically meaningful: the squared Sharpe ratio rises to $(SR_0^2 + R^2)/(1 - R^2)$; for the S&P 500 (annualised $SR_0 = 0.44$) the Sharpe ratio rises to about 0.51',
                    'The measure only applies to classification models',
                    'Such a small $R^2$ must be the result of leakage'
                ],
                correctExplanation: 'Because monthly Sharpe ratios are small, a small $R^2$ is a large relative gain: $SR^{*2} = (SR_0^2 + R^2)/(1 - R^2)$. Welch and Goyal (2008) show that most predictors fail this test against the historical mean.',
                incorrectExplanation: 'Compare the $R^2$ with the squared monthly Sharpe ratio of the market, not with 1.'
            },
            ro: {
                title: 'Cît de mic este un R² mic?',
                text: 'Un predictor al randamentelor lunare ale pieței are un $R^2$ în afara eșantionului de 0,5%. Potrivit lui Campbell și Thompson (2008), ce înseamnă asta pentru un investitor medie-varianță?',
                options: [
                    'Este neglijabil, pentru că orice $R^2$ sub 1% nu are valoare economică',
                    'Este relevant economic: pătratul raportului Sharpe crește la $(SR_0^2 + R^2)/(1 - R^2)$; pentru S&P 500 ($SR_0$ anualizat 0,44) raportul Sharpe crește la aproximativ 0,51',
                    'Măsura se aplică doar modelelor de clasificare',
                    'Un $R^2$ atît de mic trebuie să provină din leakage'
                ],
                correctExplanation: 'Pentru că rapoartele Sharpe lunare sînt mici, un $R^2$ mic înseamnă un cîștig relativ mare: $SR^{*2} = (SR_0^2 + R^2)/(1 - R^2)$. Welch și Goyal (2008) arată că majoritatea predictorilor pică acest test față de media istorică.',
                incorrectExplanation: 'Comparați $R^2$ cu pătratul raportului Sharpe lunar al pieței, nu cu 1.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Meta-labelling',
                text: 'What does meta-labelling do?',
                options: [
                    'It relabels the data with random noise to test robustness',
                    'It replaces the primary model with a larger neural network',
                    'A primary model (or rule) decides the side of the bet; a secondary ML model predicts whether to act on that signal and how much to bet',
                    'It labels observations by their calendar month'
                ],
                correctExplanation: 'Meta-labelling separates the side (primary model) from the size (secondary model), improving precision and enabling bet sizing from predicted probabilities.',
                incorrectExplanation: 'Meta-labelling = a secondary model that filters and sizes the signals of a primary model.'
            },
            ro: {
                title: 'Meta-etichetarea',
                text: 'Ce face meta-etichetarea?',
                options: [
                    'Reetichetează datele cu zgomot aleator pentru a testa robustețea',
                    'Înlocuiește modelul primar cu o rețea neuronală mai mare',
                    'Un model primar (sau o regulă) decide direcția pariului; un model ML secundar prezice dacă semnalul trebuie urmat și cît de mare să fie poziția',
                    'Etichetează observațiile după luna calendaristică'
                ],
                correctExplanation: 'Meta-etichetarea separă direcția (modelul primar) de mărimea poziției (modelul secundar), crește precizia și permite dimensionarea pozițiilor pe baza probabilităților estimate.',
                incorrectExplanation: 'Meta-etichetarea = un model secundar care filtrează și dimensionează semnalele unui model primar.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Overlapping labels',
                text: 'Labels are 5-day forward returns computed every day. Why does this break the usual IID assumption of cross-validation?',
                options: [
                    'Because 5-day returns are always positive',
                    'Because the features are standardised',
                    'Because daily data contain weekends',
                    'Because consecutive labels share 4 of their 5 daily returns, so neighbouring samples carry almost the same information'
                ],
                correctExplanation: 'Overlapping label windows create strong serial dependence between samples; a test sample and its training neighbours are near-duplicates.',
                incorrectExplanation: 'Overlapping windows make neighbouring labels highly dependent, which violates the IID assumption behind standard K-Fold.'
            },
            ro: {
                title: 'Etichete suprapuse',
                text: 'Etichetele sînt randamente viitoare pe 5 zile, calculate în fiecare zi. De ce încalcă acest lucru ipoteza IID a validării încrucișate obișnuite?',
                options: [
                    'Pentru că randamentele pe 5 zile sînt mereu pozitive',
                    'Pentru că variabilele sînt standardizate',
                    'Pentru că datele zilnice conțin weekenduri',
                    'Pentru că etichetele consecutive au în comun 4 din cele 5 randamente zilnice, deci observațiile vecine conțin aproape aceeași informație'
                ],
                correctExplanation: 'Ferestrele suprapuse creează o dependență serială puternică între observații; o observație de test și vecinii ei din antrenare sînt aproape duplicate.',
                incorrectExplanation: 'Ferestrele suprapuse fac etichetele vecine puternic dependente, ceea ce încalcă ipoteza IID din spatele K-Fold standard.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'When is K-fold valid?',
                text: 'Bergmeir, Hyndman and Koo (2018) study standard K-fold cross-validation for time series. When is it valid?',
                options: [
                    'Never: time series must always be validated walk-forward',
                    'Always, provided that the folds are shuffled',
                    'For purely autoregressive models with serially uncorrelated errors; it fails with overlapping labels, persistent features outside the lag set or under-specified dynamics',
                    'Only when the series is Normally distributed'
                ],
                correctExplanation: 'If the errors are uncorrelated, test-fold errors carry no information about training errors; overlapping $h$-day labels make the errors correlated, which is why the lecture needs purging.',
                incorrectExplanation: 'Ask whether the errors of neighbouring observations are correlated; that, not the time ordering itself, is what breaks K-fold.'
            },
            ro: {
                title: 'Cînd este valid K-fold?',
                text: 'Bergmeir, Hyndman și Koo (2018) studiază validarea încrucișată K-fold standard pentru serii de timp. Cînd este validă?',
                options: [
                    'Niciodată: seriile de timp se validează întotdeauna walk-forward',
                    'Întotdeauna, cu condiția ca pliurile să fie amestecate',
                    'Pentru modele pur autoregresive cu erori necorelate serial; eșuează la etichete suprapuse, caracteristici persistente din afara lag-urilor modelului sau dinamică subspecificată',
                    'Doar cînd seria urmează distribuția Normală'
                ],
                correctExplanation: 'Dacă erorile sînt necorelate, erorile din pliul de test nu conțin informație despre erorile de antrenare; etichetele suprapuse pe $h$ zile fac erorile corelate, de aceea cursul are nevoie de purjare.',
                incorrectExplanation: 'Întrebați-vă dacă erorile observațiilor vecine sînt corelate; asta, nu ordinea în timp în sine, strică K-fold.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Embargo',
                text: 'Why is an embargo applied after each test fold, in addition to purging?',
                options: [
                    'Because features built on rolling windows and serially correlated series can still carry information from the test period into the observations that immediately follow it',
                    'To make the training set larger',
                    'Because regulators require it',
                    'To remove weekends from the data'
                ],
                correctExplanation: 'The embargo drops a small fraction (e.g. 1%) of observations right after the test set, since their features overlap with test-period information.',
                incorrectExplanation: 'The embargo guards against leakage through serial correlation and rolling-window features right after the test set.'
            },
            ro: {
                title: 'Embargoul',
                text: 'De ce se aplică un embargo după fiecare fold de test, pe lîngă purjare?',
                options: [
                    'Pentru că variabilele construite pe ferestre mobile și seriile autocorelate pot transporta informație din perioada de test în observațiile imediat următoare',
                    'Pentru a mări setul de antrenare',
                    'Pentru că așa cer autoritățile de reglementare',
                    'Pentru a elimina weekendurile din date'
                ],
                correctExplanation: 'Embargoul elimină o mică fracțiune (de exemplu 1%) din observațiile imediat de după setul de test, deoarece variabilele lor se suprapun cu informația din perioada de test.',
                incorrectExplanation: 'Embargoul protejează împotriva leakage-ului prin autocorelare și prin ferestrele mobile imediat după setul de test.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Leakage experiment',
                text: 'On a pure random walk (nothing is predictable) with overlapping 20-day labels and persistent noise features, a random forest scores 69.4% accuracy under shuffled K-Fold but 49.7% under purged K-Fold with embargo. What explains the 69.4%?',
                options: [
                    'The random walk actually contains a predictable trend',
                    'Random forests are better than a coin flip on any data',
                    'Leakage: shuffling puts near-duplicate neighbours of each test sample into the training set, so the model "recognises" them',
                    'The purged K-Fold wastes too much data'
                ],
                correctExplanation: 'The 69.4% is pure leakage. With purging and an embargo the accuracy returns to the coin-flip level, as it must when there is no signal.',
                incorrectExplanation: 'There is no signal in a random walk; the inflated accuracy comes from information leakage through overlapping labels and shuffling.'
            },
            ro: {
                title: 'Experimentul de leakage',
                text: 'Pe un mers aleator pur (nimic nu este predictibil), cu etichete suprapuse pe 20 de zile și variabile de zgomot persistente, un random forest obține 69,4% acuratețe cu K-Fold amestecat, dar 49,7% cu Purged K-Fold și embargo. Ce explică valoarea de 69,4%?',
                options: [
                    'Mersul aleator conține de fapt un trend predictibil',
                    'Random forest este mai bun decît aruncarea monedei pe orice date',
                    'Leakage: amestecarea pune în antrenare vecini aproape identici ai fiecărei observații de test, pe care modelul îi „recunoaște”',
                    'Purged K-Fold irosește prea multe date'
                ],
                correctExplanation: 'Valoarea de 69,4% este leakage pur. Cu purjare și embargo, acuratețea revine la nivelul aruncării monedei, cum trebuie să fie cînd nu există semnal.',
                incorrectExplanation: 'Într-un mers aleator nu există semnal; acuratețea umflată vine din leakage prin etichete suprapuse și amestecare.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Walk-forward validation',
                text: 'Which is a known limitation of walk-forward (expanding window) backtesting?',
                options: [
                    'It uses future data to train the model',
                    'It cannot be applied to daily data',
                    'It always overstates performance because of shuffling',
                    'It tests a single historical path, so results depend heavily on that one sequence of events, and early periods are estimated on little data'
                ],
                correctExplanation: 'Walk-forward is honest about time ordering, but it yields only one scenario; combinatorial purged CV (CPCV) generates many backtest paths.',
                incorrectExplanation: 'Walk-forward respects time ordering, but it evaluates a strategy on only one historical path.'
            },
            ro: {
                title: 'Validarea walk-forward',
                text: 'Care este o limită cunoscută a backtesting-ului walk-forward (cu fereastră extinsă)?',
                options: [
                    'Folosește date din viitor pentru antrenarea modelului',
                    'Nu se poate aplica pe date zilnice',
                    'Supraestimează mereu performanța din cauza amestecării',
                    'Testează o singură traiectorie istorică, deci rezultatele depind mult de acea secvență de evenimente, iar primele perioade sînt estimate pe puține date'
                ],
                correctExplanation: 'Walk-forward respectă ordinea temporală, dar oferă un singur scenariu; validarea combinatorială cu purjare (CPCV) generează multe traiectorii de backtest.',
                incorrectExplanation: 'Walk-forward respectă ordinea temporală, dar evaluează strategia pe o singură traiectorie istorică.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Data-snooping tests',
                text: 'You backtest 1,279 highly correlated moving-average rules on Bitcoin. Which procedure tests whether the best rule beats buy-and-hold by estimating, from the data, the null distribution of the best rule\'s statistic, correlation between rules included?',
                options: [
                    'Hansen\'s SPA test (or White\'s Reality Check) with a stationary bootstrap of the whole matrix of rule returns',
                    'A Bonferroni correction with N = 1,279',
                    'The Deflated Sharpe Ratio with N = 1,279',
                    'A t-test of the best rule\'s mean return'
                ],
                correctExplanation: 'Resampling whole days keeps the correlation between rules, so the bootstrap estimates the null distribution of the maximum for this grid; here SPA gives $p = 0.70$ against buy-and-hold.',
                incorrectExplanation: 'Bonferroni with N = 1,279 remains valid under any dependence but ignores the correlation and is very conservative; the DSR needs a choice of N and of the variance of the Sharpe ratios; a bootstrap of the full return matrix takes the dependence from the data.'
            },
            ro: {
                title: 'Teste de data snooping',
                text: 'Faceți backtesting pentru 1.279 de reguli de medii mobile, puternic corelate, pe Bitcoin. Ce procedură testează dacă cea mai bună regulă bate buy-and-hold estimînd din date distribuția sub ipoteza nulă a statisticii celei mai bune reguli, inclusiv corelația dintre reguli?',
                options: [
                    'Testul SPA al lui Hansen (sau Reality Check al lui White) cu bootstrap staționar al întregii matrice a randamentelor regulilor',
                    'O corecție Bonferroni cu N = 1.279',
                    'Raportul Sharpe deflatat cu N = 1.279',
                    'Un test t al randamentului mediu al celei mai bune reguli'
                ],
                correctExplanation: 'Reeșantionarea unor zile întregi păstrează corelația dintre reguli, deci bootstrap-ul estimează distribuția maximului sub ipoteza nulă pentru această grilă; aici SPA dă $p = 0,70$ față de buy-and-hold.',
                incorrectExplanation: 'Bonferroni cu N = 1.279 rămîne valid la orice dependență, dar ignoră corelația și este foarte conservator; DSR cere alegerea lui N și a varianței rapoartelor Sharpe; un bootstrap al întregii matrice de randamente preia dependența din date.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'MDI importance',
                text: 'What is a known weakness of Mean Decrease Impurity (MDI) feature importance in random forests?',
                options: [
                    'It is computed in-sample, is biased towards continuous / high-cardinality features and can never be negative, so it cannot reveal features that hurt out-of-sample',
                    'It requires refitting the model thousands of times',
                    'It only works for linear models',
                    'It gives negative importance to every useful feature'
                ],
                correctExplanation: 'MDI is fast but in-sample; features with many split points look important even when pure noise.',
                incorrectExplanation: 'MDI is an in-sample, non-negative measure with a bias towards features offering many split points.'
            },
            ro: {
                title: 'Importanța MDI',
                text: 'Care este o slăbiciune cunoscută a importanței variabilelor de tip Mean Decrease Impurity (MDI) în random forest?',
                options: [
                    'Se calculează in-sample, favorizează variabilele continue / cu multe valori distincte și nu poate fi niciodată negativă, deci nu poate indica variabilele dăunătoare out-of-sample',
                    'Necesită reestimarea modelului de mii de ori',
                    'Funcționează doar pentru modele liniare',
                    'Atribuie importanță negativă fiecărei variabile utile'
                ],
                correctExplanation: 'MDI este rapidă, dar in-sample; variabilele cu multe puncte de separare par importante chiar dacă sînt zgomot pur.',
                incorrectExplanation: 'MDI este o măsură in-sample, nenegativă, care favorizează variabilele cu multe puncte posibile de separare.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'MDA and SHAP',
                text: 'In the S&P 500 example, the feature vol_20 has a high MDI but a negative MDA (permutation importance, out-of-sample $\\Delta$AUC). How should this be read?',
                options: [
                    'MDA is wrong whenever it disagrees with MDI',
                    'vol_20 is the most useful feature',
                    'Out-of-sample, permuting vol_20 slightly improves the score: the model relies on it in-sample, but it does not help (and may hurt) generalisation',
                    'Negative MDA means the feature is perfectly correlated with the label'
                ],
                correctExplanation: 'MDA measures the drop in out-of-sample performance when a feature is shuffled; a negative value is a warning sign. SHAP values give complementary local, additive attributions.',
                incorrectExplanation: 'A negative out-of-sample MDA means the feature does not generalise, despite looking important in-sample.'
            },
            ro: {
                title: 'MDA și SHAP',
                text: 'În exemplul S&P 500, variabila vol_20 are MDI mare, dar MDA negativ (importanță prin permutare, $\\Delta$AUC out-of-sample). Cum trebuie interpretat acest lucru?',
                options: [
                    'MDA este greșit ori de cîte ori contrazice MDI',
                    'vol_20 este cea mai utilă variabilă',
                    'Out-of-sample, permutarea lui vol_20 îmbunătățește ușor scorul: modelul se bazează pe ea in-sample, dar ea nu ajută (și poate chiar strica) generalizarea',
                    'Un MDA negativ înseamnă că variabila este perfect corelată cu eticheta'
                ],
                correctExplanation: 'MDA măsoară scăderea performanței out-of-sample atunci cînd o variabilă este permutată; o valoare negativă este un semnal de alarmă. Valorile SHAP oferă atribuiri locale, aditive, complementare.',
                incorrectExplanation: 'Un MDA negativ out-of-sample înseamnă că variabila nu generalizează, deși pare importantă in-sample.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Substitution effects',
                text: 'vol_20 and vol_60 are strongly correlated. What happens to their permutation (MDA) importance?',
                options: [
                    'Both importances are doubled',
                    'Each can look unimportant, because when one is permuted the model still gets the same information from the other; clustering correlated features (clustered MDA) fixes this',
                    'Correlation has no effect on importance measures',
                    'The model automatically deletes one of them'
                ],
                correctExplanation: 'This is the substitution effect: importance is shared or hidden among correlated features. Group them into clusters and permute whole clusters.',
                incorrectExplanation: 'Correlated features substitute for each other, so permuting one at a time underestimates their joint importance.'
            },
            ro: {
                title: 'Efecte de substituție',
                text: 'vol_20 și vol_60 sînt puternic corelate. Ce se întîmplă cu importanța lor prin permutare (MDA)?',
                options: [
                    'Ambele importanțe se dublează',
                    'Fiecare poate părea neimportantă, pentru că atunci cînd una este permutată modelul primește aceeași informație de la cealaltă; gruparea variabilelor corelate (clustered MDA) rezolvă problema',
                    'Corelația nu influențează măsurile de importanță',
                    'Modelul o elimină automat pe una dintre ele'
                ],
                correctExplanation: 'Acesta este efectul de substituție: importanța este împărțită sau ascunsă între variabilele corelate. Soluția este gruparea lor în clustere și permutarea întregului cluster.',
                incorrectExplanation: 'Variabilele corelate se substituie reciproc, deci permutarea lor pe rînd subestimează importanța lor comună.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'False Strategy Theorem',
                text: 'With 5 years of daily data, the best of $N = 1000$ independent strategies with zero true skill has an expected annualised Sharpe ratio of about 1.45. What does this imply?',
                options: [
                    'A Sharpe ratio of 1.45 always proves skill',
                    'Testing more strategies reduces the risk of false discoveries',
                    'The theorem only applies to cryptocurrencies',
                    'The best backtested Sharpe must be compared with the maximum expected under the null, which grows with the number of trials'
                ],
                correctExplanation: 'Under the null, $E[\\max SR]$ rises with the number of trials $N$ (roughly like $\\sqrt{2\\ln N}$). Reporting only the winner hides this selection bias.',
                incorrectExplanation: 'Selecting the best of many zero-skill strategies produces a high Sharpe by chance; the benchmark must account for the number of trials.'
            },
            ro: {
                title: 'Teorema strategiei false',
                text: 'Cu 5 ani de date zilnice, cea mai bună dintre $N = 1000$ de strategii independente, fără nicio abilitate reală, are un raport Sharpe anualizat așteptat de circa 1,45. Ce implică acest lucru?',
                options: [
                    'Un Sharpe de 1,45 dovedește întotdeauna abilitate',
                    'Testarea mai multor strategii reduce riscul descoperirilor false',
                    'Teorema se aplică doar criptomonedelor',
                    'Cel mai bun Sharpe din backtest trebuie comparat cu maximul așteptat sub ipoteza nulă, care crește odată cu numărul de încercări'
                ],
                correctExplanation: 'Sub ipoteza nulă, $E[\\max SR]$ crește cu numărul de încercări $N$ (aproximativ ca $\\sqrt{2\\ln N}$). Raportarea doar a cîștigătorului ascunde această eroare de selecție.',
                incorrectExplanation: 'Alegerea celei mai bune dintre multe strategii fără abilitate produce întîmplător un Sharpe mare; reperul trebuie să țină cont de numărul de încercări.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Grid search on Bitcoin',
                text: 'A grid search over 1,279 moving-average crossover configurations on BTC finds a best in-sample Sharpe of 1.89 (May 2015-2020). Its out-of-sample Sharpe (2021-2026) is 0.02. What is the main lesson?',
                options: [
                    'Selecting the in-sample winner among many trials picks up noise; the out-of-sample Sharpe collapses (backtest overfitting)',
                    'Moving averages never work, on any asset',
                    'The out-of-sample period must have been mis-measured',
                    'More configurations would have fixed the problem'
                ],
                correctExplanation: 'The in-sample and out-of-sample Sharpe ratios are only weakly related (Spearman correlation 0.18), so ranking by the backtest is largely ranking by luck.',
                incorrectExplanation: 'The collapse from 1.89 to 0.02 is the classic signature of backtest overfitting under multiple testing.'
            },
            ro: {
                title: 'Căutare exhaustivă pe Bitcoin',
                text: 'O căutare pe 1.279 de configurații de încrucișare a mediilor mobile pe BTC găsește un Sharpe in-sample maxim de 1,89 (mai 2015-2020). Sharpe-ul său out-of-sample (2021-2026) este 0,02. Care este lecția principală?',
                options: [
                    'Alegerea cîștigătorului in-sample dintre multe încercări captează zgomot; Sharpe-ul out-of-sample scade drastic (overfitting de backtest)',
                    'Mediile mobile nu funcționează niciodată, pe niciun activ',
                    'Perioada out-of-sample a fost probabil măsurată greșit',
                    'Mai multe configurații ar fi rezolvat problema'
                ],
                correctExplanation: 'Sharpe-urile in-sample și out-of-sample sînt slab legate (corelație Spearman 0,18), deci clasamentul după backtest este în mare parte un clasament după noroc.',
                incorrectExplanation: 'Scăderea bruscă de la 1,89 la 0,02 este simptomul clasic al overfitting-ului de backtest în condiții de testare multiplă.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Probabilistic Sharpe Ratio',
                text: 'Two strategies have the same positive observed Sharpe ratio, above the common benchmark $SR^* = 0$, and the same track-record length. Strategy A has negative skewness and fat tails; strategy B has returns that follow the Normal distribution. Which has the higher Probabilistic Sharpe Ratio $PSR(0)$?',
                options: [
                    'A, because fat tails increase expected returns',
                    'They always have the same PSR',
                    'B, because negative skewness and excess kurtosis inflate the standard error of the Sharpe ratio and lower the PSR',
                    'PSR does not depend on the return distribution'
                ],
                correctExplanation: 'For $SR > 0$ the denominator $\\sqrt{1 - \\gamma_3 SR + \\frac{\\gamma_4 - 1}{4}SR^2}$ grows when $\\gamma_3 < 0$ and $\\gamma_4 > 3$, so the same positive excess over $SR^*$ is less convincing.',
                incorrectExplanation: 'PSR penalises negative skewness and fat tails through the standard error of the estimated Sharpe ratio.'
            },
            ro: {
                title: 'Probabilistic Sharpe Ratio',
                text: 'Două strategii au același raport Sharpe observat, pozitiv, peste reperul comun $SR^* = 0$, și aceeași lungime a istoricului. Strategia A are asimetrie negativă și cozi groase; strategia B are randamente cu distribuție Normală. Care are un Probabilistic Sharpe Ratio $PSR(0)$ mai mare?',
                options: [
                    'A, pentru că cozile groase cresc randamentul așteptat',
                    'Au întotdeauna același PSR',
                    'B, pentru că asimetria negativă și excesul de aplatizare cresc eroarea standard a raportului Sharpe și scad PSR',
                    'PSR nu depinde de distribuția randamentelor'
                ],
                correctExplanation: 'Pentru $SR > 0$ numitorul $\\sqrt{1 - \\gamma_3 SR + \\frac{\\gamma_4 - 1}{4}SR^2}$ crește cînd $\\gamma_3 < 0$ și $\\gamma_4 > 3$, deci același avans pozitiv față de $SR^*$ este mai puțin convingător.',
                incorrectExplanation: 'PSR penalizează asimetria negativă și cozile groase prin eroarea standard a raportului Sharpe estimat.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Deflated Sharpe Ratio',
                text: 'What does the Deflated Sharpe Ratio (DSR) correct for, compared with a naive test of $SR > 0$?',
                options: [
                    'Only for transaction costs',
                    'For the number of trials (selection bias), returns that deviate from the Normal distribution (skewness, kurtosis) and the length of the track record',
                    'For the correlation of the strategy with the market index',
                    'For the currency in which returns are measured'
                ],
                correctExplanation: 'DSR is the PSR evaluated at the benchmark $SR_0 = E[\\max SR]$ implied by the number of trials; it answers "is this Sharpe significant, given how many strategies I tried?"',
                incorrectExplanation: 'DSR deflates the Sharpe ratio for multiple testing, non-normality and sample length.'
            },
            ro: {
                title: 'Deflated Sharpe Ratio',
                text: 'Pentru ce corectează Deflated Sharpe Ratio (DSR), față de un test naiv al ipotezei $SR > 0$?',
                options: [
                    'Doar pentru costurile de tranzacționare',
                    'Pentru numărul de încercări (eroarea de selecție), randamentele care se abat de la distribuția Normală (asimetrie, aplatizare) și lungimea istoricului',
                    'Pentru corelația strategiei cu indicele pieței',
                    'Pentru moneda în care sînt măsurate randamentele'
                ],
                correctExplanation: 'DSR este PSR evaluat în reperul $SR_0 = E[\\max SR]$ implicat de numărul de încercări; răspunde la întrebarea „este acest Sharpe semnificativ, dat fiind cîte strategii am încercat?”',
                incorrectExplanation: 'DSR ajustează raportul Sharpe pentru testarea multiplă, nenormalitate și lungimea eșantionului.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Probability of Backtest Overfitting',
                text: 'The Probability of Backtest Overfitting (PBO), estimated with combinatorially symmetric cross-validation (CSCV), is:',
                options: [
                    'The probability that a strategy loses money in the next year',
                    'The share of trades that are losers',
                    'The p-value of the Sharpe ratio of the best strategy',
                    'The probability that the configuration that is best in-sample ranks below the median of all configurations out-of-sample'
                ],
                correctExplanation: 'CSCV splits the data into many in-sample / out-of-sample combinations and counts how often the in-sample winner underperforms the median out-of-sample.',
                incorrectExplanation: 'PBO measures how often the in-sample winner falls below the out-of-sample median across many data splits.'
            },
            ro: {
                title: 'Probabilitatea de overfitting a backtest-ului',
                text: 'Probabilitatea de overfitting a backtest-ului (PBO), estimată prin validare încrucișată combinatorică simetrică (CSCV), este:',
                options: [
                    'Probabilitatea ca o strategie să piardă bani în anul următor',
                    'Ponderea tranzacțiilor cu pierdere',
                    'Valoarea p a raportului Sharpe al celei mai bune strategii',
                    'Probabilitatea ca în afara eșantionului configurația cea mai bună in-sample să se claseze sub mediana tuturor configurațiilor'
                ],
                correctExplanation: 'CSCV împarte datele în numeroase combinații in-sample / out-of-sample și numără cît de des cîștigătorul in-sample are rezultate sub mediana out-of-sample.',
                incorrectExplanation: 'PBO măsoară cît de des cîștigătorul in-sample ajunge sub mediana out-of-sample, pe multe împărțiri ale datelor.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Comparing two Sharpe ratios',
                text: 'A walk-forward strategy has an annualised Sharpe ratio of 0.49 and buy-and-hold 0.66 over the same 4,198 days (correlation of daily returns 0.93). How do you test whether the difference is significant?',
                options: [
                    'Check whether the two separate 95% confidence intervals overlap',
                    'Run a t-test on the difference in mean returns only',
                    'Run an F-test of equal variances',
                    'Test the difference of Sharpe ratios on the paired return series with the HAC delta method or a studentised block bootstrap (Ledoit and Wolf, 2008)'
                ],
                correctExplanation: 'The two Sharpe ratios are estimated on the same days and are strongly correlated; the paired test gives a difference of -0.17 with $p = 0.073$, while each Sharpe ratio alone has a standard error of about 0.25.',
                incorrectExplanation: 'Separate intervals ignore the correlation between the two estimates, and a mean or variance test answers a different question.'
            },
            ro: {
                title: 'Compararea a două rapoarte Sharpe',
                text: 'O strategie walk-forward are un raport Sharpe anualizat de 0,49, iar buy-and-hold 0,66, pe aceleași 4.198 de zile (corelația randamentelor zilnice 0,93). Cum testați dacă diferența este semnificativă?',
                options: [
                    'Verificați dacă cele două intervale de încredere de 95%, separate, se suprapun',
                    'Aplicați un test t doar pe diferența randamentelor medii',
                    'Aplicați un test F al egalității varianțelor',
                    'Testați diferența rapoartelor Sharpe pe perechile de randamente zilnice, cu metoda delta HAC sau cu un bootstrap pe blocuri studentizat (Ledoit și Wolf, 2008)'
                ],
                correctExplanation: 'Cele două rapoarte Sharpe sînt estimate pe aceleași zile și sînt puternic corelate; testul pe perechi dă o diferență de -0,17 cu $p = 0,073$, în timp ce fiecare raport Sharpe singur are o eroare standard de circa 0,25.',
                incorrectExplanation: 'Intervalele separate ignoră corelația dintre cele două estimări, iar un test al mediilor sau al varianțelor răspunde la o altă întrebare.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'The virtue of complexity',
                text: 'Kelly, Malamud and Zhou (2024) find that the out-of-sample Sharpe ratio of market timing rises with the number of random features, even when the model has more parameters than its 12-month training window. Which critique did Nagel (2025) raise?',
                options: [
                    'The result violates the bias-variance trade-off, so it must be a coding error',
                    'With a short window the forecast is a similarity-weighted average of recent returns, i.e. a volatility-timed momentum strategy, so the gains need no complexity',
                    'The result proves that deep networks always beat linear models',
                    'The result holds only for cryptocurrencies'
                ],
                correctExplanation: 'Nagel shows that for $P \\gg T$ the random-feature forecast weights past returns by similarity, which in short windows is mostly recency and falls with volatility; on data with reversals the same method loses.',
                incorrectExplanation: 'Ask what a ridge-less regression with thousands of features and 12 observations can do with its training data.'
            },
            ro: {
                title: 'Virtutea complexității',
                text: 'Kelly, Malamud și Zhou (2024) arată că raportul Sharpe în afara eșantionului al sincronizării pieței crește cu numărul de caracteristici aleatoare, chiar cînd modelul are mai mulți parametri decît fereastra lui de antrenare de 12 luni. Ce critică a formulat Nagel (2025)?',
                options: [
                    'Rezultatul încalcă compromisul bias-varianță, deci trebuie să fie o eroare de cod',
                    'Cu o fereastră scurtă, prognoza este o medie a randamentelor recente ponderată după similaritate, adică o strategie de momentum ajustat la volatilitate, deci cîștigul nu are nevoie de complexitate',
                    'Rezultatul dovedește că rețelele adînci bat întotdeauna modelele liniare',
                    'Rezultatul este valabil doar pentru criptomonede'
                ],
                correctExplanation: 'Nagel arată că pentru $P \\gg T$ prognoza cu caracteristici aleatoare ponderează randamentele trecute după similaritate, care în ferestre scurte înseamnă mai ales apropiere în timp și scade cu volatilitatea; pe date cu reveniri la medie aceeași metodă pierde.',
                incorrectExplanation: 'Întrebați-vă ce poate face o regresie ridge fără penalizare, cu mii de caracteristici și 12 observații, cu datele ei de antrenare.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Foundation models',
                text: 'Time-series foundation models (e.g. Chronos, TimesFM) forecast "zero-shot" after pre-training on huge collections of series. What is a specific risk when evaluating them on financial data?',
                options: [
                    'They cannot produce probabilistic forecasts',
                    'The pre-training corpus may already contain the evaluation period, which leaks future information into the "out-of-sample" test',
                    'They only work on monthly data',
                    'They always outperform GARCH models'
                ],
                correctExplanation: 'A model pre-trained on data that includes the test years has effectively seen the answers. The test period must be later than the pre-training cutoff.',
                incorrectExplanation: 'The main evaluation risk is look-ahead leakage through the pre-training data.'
            },
            ro: {
                title: 'Modele fundaționale (foundation models)',
                text: 'Modelele fundaționale pentru serii de timp (de exemplu Chronos, TimesFM) fac prognoze „zero-shot” după pre-antrenarea pe colecții uriașe de serii. Care este un risc specific la evaluarea lor pe date financiare?',
                options: [
                    'Nu pot produce prognoze probabilistice',
                    'Corpusul de pre-antrenare poate conține deja perioada de evaluare, ceea ce introduce look-ahead bias în testul „out-of-sample”',
                    'Funcționează doar pe date lunare',
                    'Depășesc întotdeauna modelele GARCH'
                ],
                correctExplanation: 'Un model pre-antrenat pe date care includ anii de test a „văzut” deja răspunsurile. Perioada de test trebuie să fie ulterioară datei-limită a pre-antrenării.',
                incorrectExplanation: 'Principalul risc de evaluare este leakage-ul (look-ahead bias) prin datele de pre-antrenare.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Spot the AI error: shuffled cross-validation',
                text: 'A classifier predicts, every day, the 5-day forward direction of Bitcoin from 20-day rolling features. An AI assistant writes: "Use KFold(n_splits=5, shuffle=True): shuffling removes ordering bias, so the AUC is a clean out-of-sample estimate." What is wrong?',
                options: [
                    'Five folds are too few; with 10 shuffled folds the estimate would be clean',
                    'AUC cannot be used for a binary classifier',
                    'Shuffling puts days next to each test day into training; overlapping features and labels then leak information, so use purged K-fold with an embargo or walk-forward validation',
                    'Shuffling is only a problem for regression, not for classification'
                ],
                correctExplanation: 'On a time series, neighbouring observations share information (rolling features, overlapping labels); a shuffled split lets the model see it, which inflates the score.',
                incorrectExplanation: 'Ask which days sit next to a test day in the training set, and what they share with it.'
            },
            ro: {
                title: 'Găsiți eroarea AI: validarea încrucișată cu amestecare',
                text: 'Un clasificator prezice, în fiecare zi, direcția Bitcoin pe următoarele 5 zile din caracteristici mobile pe 20 de zile. Un asistent AI scrie: „Folosiți KFold(n_splits=5, shuffle=True): amestecarea elimină efectul ordinii, deci AUC este o estimare curată în afara eșantionului.” Ce este greșit?',
                options: [
                    'Cinci blocuri sînt prea puține; cu 10 blocuri amestecate estimarea ar fi curată',
                    'AUC nu poate fi folosit pentru un clasificator binar',
                    'Amestecarea pune în antrenare zilele vecine fiecărei zile de test; caracteristicile și etichetele suprapuse produc atunci leakage, deci folosiți purged K-fold cu embargo sau validare walk-forward',
                    'Amestecarea este o problemă doar pentru regresie, nu pentru clasificare'
                ],
                correctExplanation: 'Într-o serie de timp, observațiile vecine au informație comună (caracteristici mobile, etichete suprapuse); o împărțire amestecată pune această informație la dispoziția modelului, ceea ce umflă scorul.',
                incorrectExplanation: 'Întrebați-vă ce zile vecine cu o zi de test se află în setul de antrenare și ce informație au în comun cu ea.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Spot the AI error: scaling',
                text: 'An AI assistant writes: "First standardise all features with StandardScaler().fit_transform(X) on the full 2014-2026 sample, then run walk-forward validation of the L1 logistic regression: walk-forward guarantees there is no look-ahead." What is wrong?',
                options: [
                    'The scaler is fitted on the whole sample, so means and standard deviations from the test periods enter the training data; fit it inside each training window (a pipeline)',
                    'An L1-penalised logistic regression does not need standardised features',
                    'Walk-forward validation is itself a form of look-ahead',
                    'StandardScaler must be replaced by min-max scaling to avoid look-ahead'
                ],
                correctExplanation: 'Every preprocessing step that is estimated from data is part of the model and must be fitted on the training window only; a pipeline does this automatically.',
                incorrectExplanation: 'Look at which data each estimated quantity uses: the mean and standard deviation of the scaler are estimates too.'
            },
            ro: {
                title: 'Găsiți eroarea AI: scalarea',
                text: 'Un asistent AI scrie: „Mai întîi standardizați toate caracteristicile cu StandardScaler().fit_transform(X) pe tot eșantionul 2014-2026, apoi rulați validarea walk-forward pentru regresia logistică L1: walk-forward garantează că nu există look-ahead bias.” Ce este greșit?',
                options: [
                    'Scalarea este estimată pe tot eșantionul, deci mediile și abaterile standard din perioadele de test intră în datele de antrenare; estimați-o în fiecare fereastră de antrenare (un pipeline)',
                    'O regresie logistică penalizată L1 nu are nevoie de caracteristici standardizate',
                    'Validarea walk-forward este ea însăși o formă de look-ahead bias',
                    'StandardScaler trebuie înlocuit cu scalarea min-max pentru a evita look-ahead bias'
                ],
                correctExplanation: 'Orice pas de pregătire a datelor care se estimează din date face parte din model și trebuie estimat doar pe fereastra de antrenare; un pipeline face asta automat.',
                incorrectExplanation: 'Verificați ce date folosește fiecare mărime estimată: media și abaterea standard ale scalării sînt și ele estimări.'
            }
        }
    ]
};

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
                text: 'De ce este prognoza randamentelor mai dificilă decât o sarcină tipică de machine learning, cum ar fi recunoașterea imaginilor?',
                options: [
                    'Seturile de date financiare sunt întotdeauna prea mici pentru orice model',
                    'Raportul semnal-zgomot este foarte mic, iar procesul generator al datelor se schimbă pe măsură ce piața se adaptează la tiparele exploatate',
                    'Randamentele sunt deterministe, deci ML nu aduce nimic',
                    'Datele financiare nu pot fi stocate în formă tabelară'
                ],
                correctExplanation: 'Componenta predictibilă a randamentelor este foarte mică față de zgomot, iar un tipar exploatat tinde să dispară (piețe adaptive), deci relația este nestaționară.',
                incorrectExplanation: 'Problemele esențiale sunt raportul semnal-zgomot scăzut și nestaționaritatea, nu volumul sau formatul datelor.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Bias-variance trade-off',
                text: 'On S&P 500 data, as the maximum depth of a single decision tree grows from 1 to 15, training accuracy rises to about 87% while purged cross-validated accuracy falls towards 50%. What does this show?',
                options: [
                    'Underfitting: the tree is too simple',
                    'The cross-validation is wrong because accuracy must rise with depth',
                    'Overfitting: deeper trees reduce bias but their variance explodes, so they memorise noise',
                    'Deeper trees are always better in finance'
                ],
                correctExplanation: 'Training accuracy measures memorisation; out-of-sample accuracy measures generalisation. Deep trees fit the noise (high variance).',
                incorrectExplanation: 'A widening gap between training and out-of-sample accuracy is the signature of overfitting (high variance).'
            },
            ro: {
                title: 'Compromisul bias-varianță',
                text: 'Pe datele S&P 500, când adâncimea maximă a unui singur arbore de decizie crește de la 1 la 15, acuratețea pe antrenare urcă la circa 87%, iar acuratețea din validarea încrucișată cu purjare scade spre 50%. Ce arată acest lucru?',
                options: [
                    'Subajustare: arborele este prea simplu',
                    'Validarea încrucișată este greșită, pentru că acuratețea trebuie să crească odată cu adâncimea',
                    'Supraajustare: arborii mai adânci reduc bias-ul, dar varianța lor explodează, deci memorează zgomotul',
                    'Arborii mai adânci sunt mereu mai buni în finanțe'
                ],
                correctExplanation: 'Acuratețea pe antrenare măsoară memorarea, iar cea out-of-sample măsoară generalizarea. Arborii adânci modelează zgomotul (varianță mare).',
                incorrectExplanation: 'Un decalaj tot mai mare între acuratețea pe antrenare și cea out-of-sample este semnul supraajustării (varianță mare).'
            }
        },
        {
            correct: 0,
            en: {
                title: 'LASSO vs Ridge',
                text: 'What is the main practical difference between the LASSO ($L_1$) and Ridge ($L_2$) penalties?',
                options: [
                    'LASSO can set coefficients exactly to zero (variable selection); Ridge only shrinks them towards zero',
                    'Ridge sets coefficients exactly to zero; LASSO never does',
                    'Both always give identical coefficients',
                    'LASSO can only be used for classification'
                ],
                correctExplanation: 'The $L_1$ penalty has a kink at zero, so the optimum often lies exactly at zero: LASSO performs automatic feature selection.',
                incorrectExplanation: 'Only the $L_1$ penalty produces exact zeros; the $L_2$ penalty shrinks all coefficients smoothly.'
            },
            ro: {
                title: 'LASSO vs Ridge',
                text: 'Care este principala diferență practică dintre penalizările LASSO ($L_1$) și Ridge ($L_2$)?',
                options: [
                    'LASSO poate anula exact coeficienții (selecție de variabile); Ridge doar îi micșorează spre zero',
                    'Ridge anulează exact coeficienții; LASSO niciodată',
                    'Ambele dau mereu coeficienți identici',
                    'LASSO se poate folosi doar pentru clasificare'
                ],
                correctExplanation: 'Penalizarea $L_1$ are un punct unghiular în zero, astfel că optimul se află adesea exact în zero: LASSO face selecție automată a variabilelor.',
                incorrectExplanation: 'Doar penalizarea $L_1$ produce zerouri exacte; penalizarea $L_2$ micșorează continuu toți coeficienții.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Random forest vs boosting',
                text: 'Which statement correctly contrasts random forests and gradient boosting?',
                options: [
                    'Both fit a single very deep tree',
                    'Random forests fit trees sequentially on residuals; boosting averages independent trees',
                    'Boosting cannot overfit, whatever the number of iterations',
                    'Random forests average many decorrelated trees fitted in parallel (variance reduction); boosting adds shallow trees sequentially, each fitting the errors of the previous ones (bias reduction)'
                ],
                correctExplanation: 'Bagging + feature subsampling reduces variance; boosting reduces bias step by step and needs a learning rate and early stopping to avoid overfitting.',
                incorrectExplanation: 'Random forests = parallel averaging (bagging); boosting = sequential fitting of residuals.'
            },
            ro: {
                title: 'Random forest vs boosting',
                text: 'Care afirmație compară corect random forest și gradient boosting?',
                options: [
                    'Ambele estimează un singur arbore foarte adânc',
                    'Random forest estimează arbori secvențial pe reziduuri; boosting mediază arbori independenți',
                    'Boosting nu poate supraajusta, indiferent de numărul de iterații',
                    'Random forest mediază mulți arbori decorelați, estimați în paralel (reduce varianța); boosting adaugă secvențial arbori mici, fiecare corectând erorile celor anteriori (reduce bias-ul)'
                ],
                correctExplanation: 'Bagging-ul plus eșantionarea variabilelor reduce varianța; boosting-ul reduce bias-ul pas cu pas și are nevoie de rată de învățare și early stopping pentru a evita supraajustarea.',
                incorrectExplanation: 'Random forest = mediere în paralel (bagging); boosting = estimare secvențială pe reziduuri.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Fractional differentiation',
                text: 'For the S&P 500 log price (2000-2026), the minimum differentiation order that passes the ADF test at 5% is $d^* = 0.25$, and the FFD series has a correlation of 0.98 with the log price. What is the point of using $d^*$ instead of $d = 1$ (returns)?',
                options: [
                    'Returns are non-stationary, so they cannot be used',
                    'The FFD series is stationary and still keeps most of the memory of the price level, which returns erase',
                    'FFD makes the series normally distributed',
                    'FFD removes all autocorrelation from the price'
                ],
                correctExplanation: 'Integer differencing ($d=1$) achieves stationarity by throwing away memory; the minimum $d^*$ gives stationarity while preserving predictive information.',
                incorrectExplanation: 'The trade-off is stationarity vs memory: $d^*$ is the smallest order that makes the series stationary, so it keeps as much memory as possible.'
            },
            ro: {
                title: 'Diferențierea fracționară',
                text: 'Pentru logaritmul prețului S&P 500 (2000-2026), ordinul minim de diferențiere care trece testul ADF la 5% este $d^* = 0,25$, iar seria FFD are o corelație de 0,98 cu logaritmul prețului. Care este avantajul folosirii lui $d^*$ în locul lui $d = 1$ (randamente)?',
                options: [
                    'Randamentele sunt nestaționare, deci nu pot fi folosite',
                    'Seria FFD este staționară și păstrează în mare parte memoria nivelului prețului, pe care randamentele o șterg',
                    'FFD face ca seria să urmeze distribuția Normală',
                    'FFD elimină toată autocorelația din preț'
                ],
                correctExplanation: 'Diferențierea întreagă ($d=1$) obține staționaritatea renunțând la memorie; $d^*$ minim asigură staționaritatea păstrând informația predictivă.',
                incorrectExplanation: 'Compromisul este staționaritate vs memorie: $d^*$ este cel mai mic ordin care face seria staționară, deci păstrează cât mai multă memorie.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Triple-barrier method',
                text: 'In the triple-barrier labelling method, how is the label of an observation determined?',
                options: [
                    'By the first barrier touched: upper (profit-taking, +1), lower (stop-loss, -1), or the vertical time barrier (sign of the return at expiry)',
                    'By the sign of the return over a fixed horizon, ignoring the path',
                    'By the analyst, manually',
                    'By the average of the three barrier levels'
                ],
                correctExplanation: 'The label is path-dependent: it reflects what a trader with a profit target, a stop-loss and a holding-period limit would actually experience. The horizontal barriers are scaled by volatility.',
                incorrectExplanation: 'The triple-barrier label is path-dependent and is set by whichever barrier is touched first.'
            },
            ro: {
                title: 'Metoda celor trei bariere',
                text: 'În metoda de etichetare cu trei bariere, cum se stabilește eticheta unei observații?',
                options: [
                    'După prima barieră atinsă: superioară (profit, +1), inferioară (stop-loss, -1) sau bariera verticală de timp (semnul randamentului la expirare)',
                    'După semnul randamentului pe un orizont fix, ignorând traiectoria',
                    'Manual, de către analist',
                    'După media celor trei niveluri ale barierelor'
                ],
                correctExplanation: 'Eticheta depinde de traiectorie: reflectă ce ar trăi efectiv un trader cu țintă de profit, stop-loss și limită de timp. Barierele orizontale sunt scalate cu volatilitatea.',
                incorrectExplanation: 'Eticheta cu trei bariere depinde de traiectorie și este dată de prima barieră atinsă.'
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
                title: 'Meta-labelling',
                text: 'Ce face meta-labelling-ul?',
                options: [
                    'Reetichetează datele cu zgomot aleator pentru a testa robustețea',
                    'Înlocuiește modelul primar cu o rețea neuronală mai mare',
                    'Un model primar (sau o regulă) decide direcția pariului; un model ML secundar prezice dacă semnalul trebuie urmat și cât de mare să fie poziția',
                    'Etichetează observațiile după luna calendaristică'
                ],
                correctExplanation: 'Meta-labelling-ul separă direcția (modelul primar) de mărimea poziției (modelul secundar), crește precizia și permite dimensionarea pozițiilor pe baza probabilităților estimate.',
                incorrectExplanation: 'Meta-labelling = un model secundar care filtrează și dimensionează semnalele unui model primar.'
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
                text: 'Etichetele sunt randamente viitoare pe 5 zile, calculate în fiecare zi. De ce încalcă acest lucru ipoteza IID a validării încrucișate obișnuite?',
                options: [
                    'Pentru că randamentele pe 5 zile sunt mereu pozitive',
                    'Pentru că variabilele sunt standardizate',
                    'Pentru că datele zilnice conțin weekenduri',
                    'Pentru că etichetele consecutive au în comun 4 din cele 5 randamente zilnice, deci observațiile vecine conțin aproape aceeași informație'
                ],
                correctExplanation: 'Ferestrele suprapuse creează o dependență serială puternică între observații; o observație de test și vecinii ei din antrenare sunt aproape duplicate.',
                incorrectExplanation: 'Ferestrele suprapuse fac etichetele vecine puternic dependente, ceea ce încalcă ipoteza IID din spatele K-Fold standard.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Purging',
                text: 'What does "purging" mean in purged K-Fold cross-validation?',
                options: [
                    'Deleting outliers from the test set',
                    'Removing from the training set every observation whose label interval $[t_0, t_1]$ overlaps the test period',
                    'Dropping features with low importance',
                    'Shuffling the observations before splitting'
                ],
                correctExplanation: 'If a training label is determined by prices that fall inside the test window, the model has seen test information. Purging removes those observations.',
                incorrectExplanation: 'Purging removes training observations whose labels overlap in time with the test set.'
            },
            ro: {
                title: 'Purjarea',
                text: 'Ce înseamnă „purjarea” în validarea încrucișată Purged K-Fold?',
                options: [
                    'Eliminarea valorilor extreme din setul de test',
                    'Eliminarea din setul de antrenare a tuturor observațiilor al căror interval al etichetei $[t_0, t_1]$ se suprapune cu perioada de test',
                    'Renunțarea la variabilele cu importanță mică',
                    'Amestecarea observațiilor înainte de împărțire'
                ],
                correctExplanation: 'Dacă o etichetă de antrenare depinde de prețuri din fereastra de test, modelul a „văzut” informație de test. Purjarea elimină aceste observații.',
                incorrectExplanation: 'Purjarea elimină observațiile de antrenare ale căror etichete se suprapun în timp cu setul de test.'
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
                text: 'De ce se aplică un embargo după fiecare fold de test, pe lângă purjare?',
                options: [
                    'Pentru că variabilele construite pe ferestre mobile și seriile autocorelate pot transporta informație din perioada de test în observațiile imediat următoare',
                    'Pentru a mări setul de antrenare',
                    'Pentru că așa cer autoritățile de reglementare',
                    'Pentru a elimina weekendurile din date'
                ],
                correctExplanation: 'Embargoul elimină o mică fracțiune (de exemplu 1%) din observațiile imediat de după setul de test, deoarece variabilele lor se suprapun cu informația din perioada de test.',
                incorrectExplanation: 'Embargoul protejează împotriva scurgerii de informație prin autocorelare și prin ferestrele mobile imediat după setul de test.'
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
                title: 'Experimentul de scurgere a informației',
                text: 'Pe un mers aleator pur (nimic nu este predictibil), cu etichete suprapuse pe 20 de zile și variabile de zgomot persistente, un random forest obține 69,4% acuratețe cu K-Fold amestecat, dar 49,7% cu Purged K-Fold și embargo. Ce explică valoarea de 69,4%?',
                options: [
                    'Mersul aleator conține de fapt un trend predictibil',
                    'Random forest este mai bun decât aruncarea monedei pe orice date',
                    'Scurgerea de informație: amestecarea pune în antrenare vecini aproape identici ai fiecărei observații de test, pe care modelul îi „recunoaște”',
                    'Purged K-Fold irosește prea multe date'
                ],
                correctExplanation: 'Valoarea de 69,4% este scurgere de informație pură. Cu purjare și embargo, acuratețea revine la nivelul aruncării monedei, cum trebuie să fie când nu există semnal.',
                incorrectExplanation: 'Într-un mers aleator nu există semnal; acuratețea umflată vine din scurgerea de informație prin etichete suprapuse și amestecare.'
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
                    'Testează o singură traiectorie istorică, deci rezultatele depind mult de acea secvență de evenimente, iar primele perioade sunt estimate pe puține date'
                ],
                correctExplanation: 'Walk-forward respectă ordinea temporală, dar oferă un singur scenariu; validarea combinatorială cu purjare (CPCV) generează multe traiectorii de backtest.',
                incorrectExplanation: 'Walk-forward respectă ordinea temporală, dar evaluează strategia pe o singură traiectorie istorică.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'The naive baseline',
                text: 'For the 5-day direction of the S&P 500 (purged 5-fold CV), the four ML models reach 55-58% accuracy with AUC close to 0.50, while always predicting "up" gives 58.1%. What is the correct conclusion?',
                options: [
                    'The models are excellent because accuracy is above 50%',
                    'None of the models beats the naive "always up" baseline; accuracy must always be compared with the class imbalance of the market drift',
                    'AUC is irrelevant for classification',
                    'The neural network is clearly the best model'
                ],
                correctExplanation: 'Because the market drifts upwards, "up" is the majority class. An AUC of about 0.5 confirms that the models have no ranking ability.',
                incorrectExplanation: 'Accuracy above 50% means nothing if a constant forecast does better; here no model beats the 58.1% baseline.'
            },
            ro: {
                title: 'Reperul naiv',
                text: 'Pentru direcția pe 5 zile a S&P 500 (Purged 5-fold CV), cele patru modele ML obțin 55-58% acuratețe și un AUC apropiat de 0,50, în timp ce prognoza „mereu în sus” dă 58,1%. Care este concluzia corectă?',
                options: [
                    'Modelele sunt excelente, pentru că acuratețea depășește 50%',
                    'Niciun model nu bate reperul naiv „mereu în sus”; acuratețea trebuie comparată întotdeauna cu dezechilibrul claselor dat de trendul pieței',
                    'AUC-ul este irelevant pentru clasificare',
                    'Rețeaua neuronală este clar cel mai bun model'
                ],
                correctExplanation: 'Deoarece piața are un trend ascendent, „sus” este clasa majoritară. Un AUC de aproximativ 0,5 confirmă că modelele nu au capacitate de ierarhizare.',
                incorrectExplanation: 'O acuratețe peste 50% nu înseamnă nimic dacă o prognoză constantă face mai bine; aici niciun model nu depășește reperul de 58,1%.'
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
                correctExplanation: 'MDI este rapidă, dar in-sample; variabilele cu multe puncte de separare par importante chiar dacă sunt zgomot pur.',
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
                    'MDA este greșit ori de câte ori contrazice MDI',
                    'vol_20 este cea mai utilă variabilă',
                    'Out-of-sample, permutarea lui vol_20 îmbunătățește ușor scorul: modelul se bazează pe ea in-sample, dar ea nu ajută (și poate chiar strica) generalizarea',
                    'Un MDA negativ înseamnă că variabila este perfect corelată cu eticheta'
                ],
                correctExplanation: 'MDA măsoară scăderea performanței out-of-sample atunci când o variabilă este permutată; o valoare negativă este un semnal de alarmă. Valorile SHAP oferă atribuiri locale, aditive, complementare.',
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
                text: 'vol_20 și vol_60 sunt puternic corelate. Ce se întâmplă cu importanța lor prin permutare (MDA)?',
                options: [
                    'Ambele importanțe se dublează',
                    'Fiecare poate părea neimportantă, pentru că atunci când una este permutată modelul primește aceeași informație de la cealaltă; gruparea variabilelor corelate (clustered MDA) rezolvă problema',
                    'Corelația nu influențează măsurile de importanță',
                    'Modelul o elimină automat pe una dintre ele'
                ],
                correctExplanation: 'Acesta este efectul de substituție: importanța este împărțită sau ascunsă între variabilele corelate. Soluția este gruparea lor în clustere și permutarea întregului cluster.',
                incorrectExplanation: 'Variabilele corelate se substituie reciproc, deci permutarea lor pe rând subestimează importanța lor comună.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'False Strategy Theorem',
                text: 'With 5 years of daily data, the best of $N = 1000$ strategies with zero true skill has an expected annualised Sharpe ratio of about 1.45. What does this imply?',
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
                text: 'Cu 5 ani de date zilnice, cea mai bună dintre $N = 1000$ de strategii fără nicio abilitate reală are un raport Sharpe anualizat așteptat de circa 1,45. Ce implică acest lucru?',
                options: [
                    'Un Sharpe de 1,45 dovedește întotdeauna abilitate',
                    'Testarea mai multor strategii reduce riscul descoperirilor false',
                    'Teorema se aplică doar criptomonedelor',
                    'Cel mai bun Sharpe din backtest trebuie comparat cu maximul așteptat sub ipoteza nulă, care crește odată cu numărul de încercări'
                ],
                correctExplanation: 'Sub ipoteza nulă, $E[\\max SR]$ crește cu numărul de încercări $N$ (aproximativ ca $\\sqrt{2\\ln N}$). Raportarea doar a câștigătorului ascunde această eroare de selecție.',
                incorrectExplanation: 'Alegerea celei mai bune dintre multe strategii fără abilitate produce întâmplător un Sharpe mare; reperul trebuie să țină cont de numărul de încercări.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Grid search on Bitcoin',
                text: 'A grid search over 1,279 moving-average crossover configurations on BTC finds a best in-sample Sharpe of 1.65 (2015-2020). Its out-of-sample Sharpe (2021-2026) is 0.02. What is the main lesson?',
                options: [
                    'Selecting the in-sample winner among many trials picks up noise; the out-of-sample Sharpe collapses (backtest overfitting)',
                    'Moving averages never work, on any asset',
                    'The out-of-sample period must have been mis-measured',
                    'More configurations would have fixed the problem'
                ],
                correctExplanation: 'The in-sample and out-of-sample Sharpe ratios are only weakly related (Spearman correlation 0.12), so ranking by the backtest is largely ranking by luck.',
                incorrectExplanation: 'The collapse from 1.65 to 0.02 is the classic signature of backtest overfitting under multiple testing.'
            },
            ro: {
                title: 'Căutare exhaustivă pe Bitcoin',
                text: 'O căutare pe 1.279 de configurații de încrucișare a mediilor mobile pe BTC găsește un Sharpe in-sample maxim de 1,65 (2015-2020). Sharpe-ul său out-of-sample (2021-2026) este 0,02. Care este lecția principală?',
                options: [
                    'Alegerea câștigătorului in-sample dintre multe încercări captează zgomot; Sharpe-ul out-of-sample se prăbușește (overfitting de backtest)',
                    'Mediile mobile nu funcționează niciodată, pe niciun activ',
                    'Perioada out-of-sample a fost probabil măsurată greșit',
                    'Mai multe configurații ar fi rezolvat problema'
                ],
                correctExplanation: 'Sharpe-urile in-sample și out-of-sample sunt slab legate (corelație Spearman 0,12), deci ierarhizarea după backtest este în mare parte ierarhizare după noroc.',
                incorrectExplanation: 'Prăbușirea de la 1,65 la 0,02 este semnătura clasică a overfitting-ului de backtest în condiții de testare multiplă.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Probabilistic Sharpe Ratio',
                text: 'Two strategies have the same observed Sharpe ratio and track-record length. Strategy A has negative skewness and fat tails; strategy B has returns that follow the Normal distribution. Which has the higher Probabilistic Sharpe Ratio (PSR)?',
                options: [
                    'A, because fat tails increase expected returns',
                    'They always have the same PSR',
                    'B, because negative skewness and excess kurtosis inflate the standard error of the Sharpe ratio and lower the PSR',
                    'PSR does not depend on the return distribution'
                ],
                correctExplanation: 'The denominator $\\sqrt{1 - \\gamma_3 SR + \\frac{\\gamma_4 - 1}{4}SR^2}$ grows when $\\gamma_3 < 0$ and $\\gamma_4 > 3$, so the same SR is less convincing.',
                incorrectExplanation: 'PSR penalises negative skewness and fat tails through the standard error of the estimated Sharpe ratio.'
            },
            ro: {
                title: 'Probabilistic Sharpe Ratio',
                text: 'Două strategii au același raport Sharpe observat și aceeași lungime a istoricului. Strategia A are asimetrie negativă și cozi groase; strategia B are randamente cu distribuție Normală. Care are un Probabilistic Sharpe Ratio (PSR) mai mare?',
                options: [
                    'A, pentru că cozile groase cresc randamentul așteptat',
                    'Au întotdeauna același PSR',
                    'B, pentru că asimetria negativă și excesul de aplatizare cresc eroarea standard a raportului Sharpe și scad PSR',
                    'PSR nu depinde de distribuția randamentelor'
                ],
                correctExplanation: 'Numitorul $\\sqrt{1 - \\gamma_3 SR + \\frac{\\gamma_4 - 1}{4}SR^2}$ crește când $\\gamma_3 < 0$ și $\\gamma_4 > 3$, deci același SR este mai puțin convingător.',
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
                    'Pentru moneda în care sunt măsurate randamentele'
                ],
                correctExplanation: 'DSR este PSR evaluat în reperul $SR_0 = E[\\max SR]$ implicat de numărul de încercări; răspunde la întrebarea „este acest Sharpe semnificativ, dat fiind câte strategii am încercat?”',
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
                text: 'Probabilitatea de overfitting a backtest-ului (PBO), estimată prin validare încrucișată combinatorial simetrică (CSCV), este:',
                options: [
                    'Probabilitatea ca o strategie să piardă bani în anul următor',
                    'Ponderea tranzacțiilor cu pierdere',
                    'Valoarea p a raportului Sharpe al celei mai bune strategii',
                    'Probabilitatea ca în afara eșantionului configurația cea mai bună in-sample să se claseze sub mediana tuturor configurațiilor'
                ],
                correctExplanation: 'CSCV împarte datele în numeroase combinații in-sample / out-of-sample și numără cât de des câștigătorul in-sample are rezultate sub mediana out-of-sample.',
                incorrectExplanation: 'PBO măsoară cât de des câștigătorul in-sample ajunge sub mediana out-of-sample, pe multe împărțiri ale datelor.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Transaction costs',
                text: 'In the S&P 500 walk-forward backtest (2010-2026, yearly refit), a gradient-boosting long/cash strategy with 5 bp costs has a Sharpe ratio of 0.49, against 0.66 for buy-and-hold. What is the lesson?',
                options: [
                    'A statistically "reasonable" classifier can still underperform a passive benchmark once trading costs and time out of the market are counted',
                    'Buy-and-hold is always optimal',
                    'Transaction costs never matter at daily frequency',
                    'Gradient boosting cannot be used for trading'
                ],
                correctExplanation: 'Every switch costs money, and being in cash during rebounds is expensive. Always report net-of-cost performance against a simple benchmark.',
                incorrectExplanation: 'The ML strategy loses to buy-and-hold after costs; performance must be judged net of costs and against a passive benchmark.'
            },
            ro: {
                title: 'Costuri de tranzacționare',
                text: 'În backtest-ul walk-forward pe S&P 500 (2010-2026, reestimare anuală), o strategie gradient boosting long/cash cu costuri de 5 bp are un Sharpe de 0,49, față de 0,66 pentru buy-and-hold. Care este lecția?',
                options: [
                    'Un clasificator „rezonabil” statistic poate avea totuși rezultate mai slabe decât un reper pasiv, odată ce se iau în calcul costurile și timpul petrecut în afara pieței',
                    'Buy-and-hold este întotdeauna optim',
                    'Costurile de tranzacționare nu contează niciodată la frecvență zilnică',
                    'Gradient boosting nu poate fi folosit în tranzacționare'
                ],
                correctExplanation: 'Fiecare schimbare de poziție costă, iar statul în cash în timpul revenirilor este scump. Performanța trebuie raportată mereu net de costuri, față de un reper simplu.',
                incorrectExplanation: 'Strategia ML pierde în fața buy-and-hold după costuri; performanța trebuie judecată net de costuri și față de un reper pasiv.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Backtesting is not research',
                text: 'According to <a href="https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086" target="_blank" rel="noopener">López de Prado (2018)</a>, why is "backtesting is not a research tool"?',
                options: [
                    'Because backtests are too slow to run',
                    'Because regulators forbid backtests',
                    'Because iterating on backtest results until they look good turns the backtest into an overfitting machine; research should rely on feature importance and theory, with the backtest as a final check',
                    'Because backtests cannot include transaction costs'
                ],
                correctExplanation: 'Each tweak made after looking at a backtest is another trial. Use feature importance (MDA, SHAP) to understand the model, then run the backtest once.',
                incorrectExplanation: 'Repeatedly adjusting a strategy to its backtest multiplies the number of trials and guarantees overfitting.'
            },
            ro: {
                title: 'Backtest-ul nu este cercetare',
                text: 'Potrivit lui <a href="https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086" target="_blank" rel="noopener">López de Prado (2018)</a>, de ce „backtest-ul nu este un instrument de cercetare”?',
                options: [
                    'Pentru că backtest-urile durează prea mult',
                    'Pentru că autoritățile de reglementare interzic backtest-urile',
                    'Pentru că iterarea pe rezultatele backtest-ului până când arată bine îl transformă într-o mașină de overfitting; cercetarea trebuie să se bazeze pe importanța variabilelor și pe teorie, iar backtest-ul să fie doar verificarea finală',
                    'Pentru că backtest-urile nu pot include costuri de tranzacționare'
                ],
                correctExplanation: 'Fiecare ajustare făcută după ce te uiți la un backtest este încă o încercare. Folosește importanța variabilelor (MDA, SHAP) pentru a înțelege modelul, apoi rulează backtest-ul o singură dată.',
                incorrectExplanation: 'Ajustarea repetată a unei strategii după backtest crește numărul de încercări și garantează overfitting-ul.'
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
                title: 'Modele fundamentale (foundation models)',
                text: 'Modelele fundamentale pentru serii de timp (de exemplu Chronos, TimesFM) fac prognoze „zero-shot” după pre-antrenarea pe colecții uriașe de serii. Care este un risc specific la evaluarea lor pe date financiare?',
                options: [
                    'Nu pot produce prognoze probabilistice',
                    'Corpusul de pre-antrenare poate conține deja perioada de evaluare, ceea ce introduce informație din viitor în testul „out-of-sample”',
                    'Funcționează doar pe date lunare',
                    'Depășesc întotdeauna modelele GARCH'
                ],
                correctExplanation: 'Un model pre-antrenat pe date care includ anii de test a „văzut” deja răspunsurile. Perioada de test trebuie să fie ulterioară datei limită a pre-antrenării.',
                incorrectExplanation: 'Principalul risc de evaluare este scurgerea de informație din viitor prin datele de pre-antrenare.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Spot the AI error: shuffled cross-validation',
                text: 'An AI assistant writes: "To evaluate a daily Bitcoin direction classifier, use KFold(n_splits=5, shuffle=True): shuffling removes ordering bias, so the AUC is a clean out-of-sample estimate." What is wrong?',
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
                text: 'Un asistent AI scrie: „Pentru a evalua un clasificator zilnic al direcției Bitcoin, folosiți KFold(n_splits=5, shuffle=True): amestecarea elimină efectul ordinii, deci AUC este o estimare curată în afara eșantionului.” Ce este greșit?',
                options: [
                    'Cinci blocuri sunt prea puține; cu 10 blocuri amestecate estimarea ar fi curată',
                    'AUC nu poate fi folosit pentru un clasificator binar',
                    'Amestecarea pune în antrenare zilele vecine fiecărei zile de test; caracteristicile și etichetele suprapuse transmit atunci informație, deci folosiți purged K-fold cu embargo sau validare walk-forward',
                    'Amestecarea este o problemă doar pentru regresie, nu pentru clasificare'
                ],
                correctExplanation: 'Într-o serie de timp, observațiile vecine au informație comună (caracteristici mobile, etichete suprapuse); o împărțire amestecată i-o arată modelului, ceea ce umflă scorul.',
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
                text: 'Un asistent AI scrie: „Mai întâi standardizați toate caracteristicile cu StandardScaler().fit_transform(X) pe tot eșantionul 2014-2026, apoi rulați validarea walk-forward pentru regresia logistică L1: walk-forward garantează că nu există informație din viitor.” Ce este greșit?',
                options: [
                    'Scalarea este estimată pe tot eșantionul, deci mediile și abaterile standard din perioadele de test intră în datele de antrenare; estimați-o în fiecare fereastră de antrenare (un pipeline)',
                    'O regresie logistică penalizată L1 nu are nevoie de caracteristici standardizate',
                    'Validarea walk-forward este ea însăși o formă de informație din viitor',
                    'StandardScaler trebuie înlocuit cu scalarea min-max pentru a evita informația din viitor'
                ],
                correctExplanation: 'Orice pas de pregătire a datelor care se estimează din date face parte din model și trebuie estimat doar pe fereastra de antrenare; un pipeline face asta automat.',
                incorrectExplanation: 'Verificați ce date folosește fiecare mărime estimată: media și abaterea standard ale scalării sunt și ele estimări.'
            }
        }
    ]
};

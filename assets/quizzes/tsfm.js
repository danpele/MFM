// ============================================================
// Quiz bank for chapter id 'tsfm': Deep Learning and Time-Series Foundation Models (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['tsfm'] = {
    draw: 20,
    questions: [
            {
                "correct": 0,
                "en": {
                    "title": "Vanishing gradient",
                    "text": "Why do gradients vanish when a simple recurrent network (RNN) is trained on long sequences?",
                    "options": [
                        "The gradient with respect to an input k steps back is a product of k Jacobians; when their norms are below 1 the product shrinks geometrically",
                        "Because the loss function of an RNN is always convex",
                        "Because the learning rate of Adam decreases to zero after a few epochs",
                        "Because recurrent networks cannot use the tanh activation"
                    ],
                    "correctExplanation": "Backpropagation through time multiplies one Jacobian per step; with norms below 1 (tanh saturates, small weights) the product decays like |w|^k.",
                    "incorrectExplanation": "The cause is the repeated product of Jacobians across time steps, not the optimiser or the shape of the loss."
                },
                "ro": {
                    "title": "Dispariția gradientului",
                    "text": "De ce dispar gradienții cînd o rețea recurentă simplă (RNN) este antrenată pe secvențe lungi?",
                    "options": [
                        "Gradientul față de o intrare aflată cu k pași în urmă este un produs de k matrice jacobiene; cînd normele lor sînt sub 1, produsul scade geometric",
                        "Pentru că funcția de pierdere a unei RNN este mereu convexă",
                        "Pentru că rata de învățare a lui Adam scade la zero după cîteva epoci",
                        "Pentru că rețelele recurente nu pot folosi funcția de activare tanh"
                    ],
                    "correctExplanation": "Propagarea înapoi în timp înmulțește cîte o matrice jacobiană pe pas; cu norme sub 1 (tanh saturat, ponderi mici), produsul scade ca |w|^k.",
                    "incorrectExplanation": "Cauza este produsul repetat de matrice jacobiene de-a lungul pașilor de timp, nu optimizatorul sau forma pierderii."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "The LSTM cell state",
                    "text": "In an LSTM, the cell state evolves as c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t. What does this imply for learning long memory?",
                    "options": [
                        "The output gate alone decides how far back the gradient can travel",
                        "Along the direct cell-state path (gates and candidate held fixed), the derivative of c_T with respect to c_{T-k} is the product of the forget gates, so memory survives when the forget gate stays close to 1",
                        "The candidate g_t must be zero for the network to remember",
                        "The cell state is reset to zero at every step, so there is no long memory"
                    ],
                    "correctExplanation": "Along the cell-state path the only multiplier is the forget gate: this path contributes ∏ f_t to the gradient, which decays slowly when f_t is near 1; the gates and the candidate add further paths through h_{t-1}.",
                    "incorrectExplanation": "The key path is the additive cell-state update; along it the gradient is the product of the forget gates."
                },
                "ro": {
                    "title": "Starea celulei LSTM",
                    "text": "Într-un LSTM, starea celulei evoluează după c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t. Ce implică acest lucru pentru învățarea memoriei lungi?",
                    "options": [
                        "Doar poarta de ieșire decide cît de departe în urmă poate ajunge gradientul",
                        "Pe drumul direct al stării celulei (cu porțile și candidatul fixate), derivata lui c_T în raport cu c_{T-k} este produsul porților de uitare, deci memoria se păstrează cînd poarta de uitare rămîne aproape de 1",
                        "Candidatul g_t trebuie să fie zero pentru ca rețeaua să-și amintească",
                        "Starea celulei este resetată la zero la fiecare pas, deci nu există memorie lungă"
                    ],
                    "correctExplanation": "Pe drumul stării celulei singurul multiplicator este poarta de uitare: acest drum contribuie la gradient cu ∏ f_t, care scade încet cînd f_t este aproape de 1; porțile și candidatul adaugă alte drumuri, prin h_{t-1}.",
                    "incorrectExplanation": "Drumul esențial este actualizarea aditivă a stării celulei; pe acest drum gradientul este produsul porților de uitare."
                }
            },
            {
                "correct": 2,
                "en": {
                    "title": "Forget-gate bias",
                    "text": "A constant forget gate f = σ(3) ≈ 0.953 is compared with f = σ(0) = 0.5. What is the fraction of the signal left after 50 steps in each case?",
                    "options": [
                        "About 50% in both cases",
                        "Exactly zero in both cases",
                        "About 9% with f ≈ 0.953 and about 10^-15 with f = 0.5",
                        "About 95% with f ≈ 0.953 and 50% with f = 0.5"
                    ],
                    "correctExplanation": "0.953^50 ≈ 0.09, while 0.5^50 ≈ 8.9 × 10^-16: opening the forget gate is what gives the LSTM its long memory.",
                    "incorrectExplanation": "Raise each forget-gate value to the power 50: 0.953^50 ≈ 0.09 and 0.5^50 ≈ 10^-15."
                },
                "ro": {
                    "title": "Termenul liber al porții de uitare",
                    "text": "O poartă de uitare constantă f = σ(3) ≈ 0,953 este comparată cu f = σ(0) = 0,5. Ce fracțiune din semnal rămîne după 50 de pași în fiecare caz?",
                    "options": [
                        "Circa 50% în ambele cazuri",
                        "Exact zero în ambele cazuri",
                        "Circa 9% cu f ≈ 0,953 și circa 10^-15 cu f = 0,5",
                        "Circa 95% cu f ≈ 0,953 și 50% cu f = 0,5"
                    ],
                    "correctExplanation": "0,953^50 ≈ 0,09, iar 0,5^50 ≈ 8,9 × 10^-16: deschiderea porții de uitare îi dă LSTM-ului memoria lungă.",
                    "incorrectExplanation": "Ridicați fiecare valoare a porții de uitare la puterea 50: 0,953^50 ≈ 0,09 și 0,5^50 ≈ 10^-15."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Nested forecasts",
                    "text": "You compare an AR(1) forecast of daily returns with the zero forecast using the Diebold–Mariano (DM) test on squared errors. Why is the plain DM test inappropriate here?",
                    "options": [
                        "Because DM requires the losses to be Normally distributed",
                        "Because DM requires the two forecasts to have the same number of parameters",
                        "Because an AR(1) model is non-stationary for daily returns",
                        "The zero forecast is nested in AR(1): under the null the larger model only adds estimation noise, the DM statistic is not N(0,1) and rejects too rarely; use Clark–West"
                    ],
                    "correctExplanation": "Setting both AR(1) coefficients to zero gives the zero forecast. Under H0 the population errors are equal, but the estimated AR(1) adds noise to its squared error; Clark and West (2007) add back (ŷ0 − ŷ1)² to correct this.",
                    "incorrectExplanation": "The problem is nesting: the benchmark is a special case of the model, so the DM statistic is undersized under the null. The Clark–West adjustment fixes it."
                },
                "ro": {
                    "title": "Prognoze imbricate",
                    "text": "Comparați o prognoză AR(1) a randamentelor zilnice cu prognoza zero prin testul Diebold–Mariano (DM) pe erorile pătratice. De ce nu este potrivit testul DM simplu aici?",
                    "options": [
                        "Pentru că DM cere ca pierderile să urmeze distribuția Normală",
                        "Pentru că DM cere ca cele două prognoze să aibă același număr de parametri",
                        "Pentru că un model AR(1) este nestaționar pentru randamentele zilnice",
                        "Prognoza zero este imbricată în AR(1): sub ipoteza nulă modelul mai mare doar adaugă zgomot de estimare, statistica DM nu este N(0,1) și respinge prea rar; folosiți Clark–West"
                    ],
                    "correctExplanation": "Coeficienții AR(1) egali cu zero dau prognoza zero. Sub H0 erorile din populație sînt egale, dar AR(1) estimat adaugă zgomot erorii pătratice; Clark și West (2007) adaugă înapoi (ŷ0 − ŷ1)² pentru corecție.",
                    "incorrectExplanation": "Problema este imbricarea: reperul este un caz particular al modelului, deci statistica DM respinge prea rar sub ipoteza nulă. Ajustarea Clark–West o corectează."
                }
            },
            {
                "correct": 0,
                "en": {
                    "title": "Scaled dot-product attention",
                    "text": "In attention, softmax(QK^T / √d_k) V, why are the scores divided by √d_k?",
                    "options": [
                        "To keep the dot products from growing with the dimension, so the softmax does not saturate and gradients stay usable",
                        "To turn the attention weights into probabilities that sum to d_k",
                        "To remove the need for positional information",
                        "To make the model invariant to the scale of the input series"
                    ],
                    "correctExplanation": "Dot products of d_k-dimensional vectors have variance proportional to d_k; dividing by √d_k keeps the softmax away from saturation.",
                    "incorrectExplanation": "The scaling controls the size of the scores; the softmax already produces weights that sum to one."
                },
                "ro": {
                    "title": "Atenția cu produs scalar scalat",
                    "text": "În mecanismul de atenție, softmax(QK^T / √d_k) V, de ce sînt scorurile împărțite la √d_k?",
                    "options": [
                        "Ca produsele scalare să nu crească odată cu dimensiunea, astfel încît softmax să nu se satureze și gradienții să rămînă utilizabili",
                        "Ca ponderile de atenție să devină probabilități cu suma d_k",
                        "Ca să nu mai fie nevoie de informația de poziție",
                        "Ca modelul să fie invariant la scala seriei de intrare"
                    ],
                    "correctExplanation": "Produsele scalare ale unor vectori de dimensiune d_k au varianța proporțională cu d_k; împărțirea la √d_k ține softmax departe de saturare.",
                    "incorrectExplanation": "Scalarea controlează mărimea scorurilor; softmax produce deja ponderi cu suma 1."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "Many models, one test period",
                    "text": "Six models are tested against the zero forecast in three markets (18 tests). The smallest one-sided DM p-value is 0.008, for the LSTM on the BET. What should you conclude?",
                    "options": [
                        "The LSTM signal on the BET is real, because 0.008 is below 0.05",
                        "For the family of 18 tests it is not significant (Bonferroni threshold 0.05/18 ≈ 0.0028; Holm-adjusted p ≈ 0.14); a family-wise method such as Romano–Wolf or SPA must be applied to the declared family",
                        "A p-value below 0.05 cannot be a false positive",
                        "Use a one-sided test to halve the p-value and the problem disappears"
                    ],
                    "correctExplanation": "The chance that the smallest of 18 p-values falls below 0.05 by luck is large. Within the BET family of six models, Romano–Wolf gives p ≈ 0.017 and SPA p ≈ 0.02; over all 18 tests, Holm gives about 0.14.",
                    "incorrectExplanation": "With many tests the smallest p-value is biased downwards; control the family-wise error rate (Holm, Romano–Wolf, SPA) for the family you declared before looking."
                },
                "ro": {
                    "title": "Multe modele, o singură perioadă de test",
                    "text": "Șase modele sînt testate față de prognoza zero pe trei piețe (18 teste). Cea mai mică valoare p DM unilaterală este 0,008, pentru LSTM pe BET. Ce concluzionați?",
                    "options": [
                        "Semnalul LSTM pe BET este real, pentru că 0,008 este sub 0,05",
                        "Pentru familia de 18 teste nu este semnificativ (pragul Bonferroni 0,05/18 ≈ 0,0028; p ajustat Holm ≈ 0,14); trebuie aplicată o metodă pentru familia de teste, precum Romano–Wolf sau SPA, familiei declarate",
                        "O valoare p sub 0,05 nu poate fi un fals pozitiv",
                        "Folosiți un test unilateral ca să înjumătățiți valoarea p și problema dispare"
                    ],
                    "correctExplanation": "Șansa ca cea mai mică dintre 18 valori p să cadă sub 0,05 din noroc este mare. În familia BET de șase modele, Romano–Wolf dă p ≈ 0,017 și SPA p ≈ 0,02; pe toate cele 18 teste, Holm dă circa 0,14.",
                    "incorrectExplanation": "Cu multe teste, cea mai mică valoare p este deplasată în jos; controlați eroarea pe familie (Holm, Romano–Wolf, SPA) pentru familia declarată înainte de a vedea rezultatele."
                }
            },
            {
                "correct": 2,
                "en": {
                    "title": "Patching",
                    "text": "Chronos-2 splits a 512-day context into patches of 16 days. What is the main gain?",
                    "options": [
                        "Patching removes the need to scale the series",
                        "Patching guarantees that the forecasts are unbiased",
                        "The Transformer sees 32 tokens instead of 512, which cuts the quadratic cost of attention and gives each token local context",
                        "Patching makes the model forecast only at a 16-day horizon"
                    ],
                    "correctExplanation": "Attention costs grow with the square of the number of tokens; 512/16 = 32 tokens is far cheaper, and each patch summarises local dynamics.",
                    "incorrectExplanation": "The gain is computational and representational: fewer, richer tokens."
                },
                "ro": {
                    "title": "Împărțirea în patch-uri",
                    "text": "Chronos-2 împarte un context de 512 zile în patch-uri de cîte 16 zile. Care este cîștigul principal?",
                    "options": [
                        "Împărțirea în patch-uri elimină nevoia de scalare a seriei",
                        "Împărțirea în patch-uri garantează prognoze nedeplasate",
                        "Transformerul vede 32 de tokeni în loc de 512, ceea ce reduce costul pătratic al atenției și dă fiecărui token context local",
                        "Împărțirea în patch-uri face ca modelul să prognozeze doar la orizontul de 16 zile"
                    ],
                    "correctExplanation": "Costul atenției crește cu pătratul numărului de tokeni; 512/16 = 32 de tokeni este mult mai ieftin, iar fiecare patch rezumă dinamica locală.",
                    "incorrectExplanation": "Cîștigul este de calcul și de reprezentare: tokeni mai puțini și mai bogați."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Reading a PIT histogram",
                    "text": "For a density forecast of daily returns, the probability integral transform u_t = F̂_t(r_t) falls below 0.01 on 1.67% of days and above 0.99 on 1.08% of days. What does this say?",
                    "options": [
                        "The predictive distribution is too wide: too few outcomes in the tails",
                        "The predictive mean is biased upwards, and the spread is correct",
                        "The forecast is perfectly calibrated, because the PIT values are between 0 and 1",
                        "The lower tail of the predictive distribution is too thin: too many outcomes fall below its 1% quantile; a Berkowitz test on Φ⁻¹(u_t) quantifies it"
                    ],
                    "correctExplanation": "Under correct calibration the PIT is i.i.d. uniform, so 1% of days should fall below 0.01. An excess in the lower tail means the forecast quantiles are too narrow there (raw Chronos-2 on the S&P 500).",
                    "incorrectExplanation": "Excess mass in a tail interval of the PIT means the predictive distribution is too narrow in that tail; a too-wide forecast gives too little mass in the tails."
                },
                "ro": {
                    "title": "Citirea histogramei PIT",
                    "text": "Pentru o prognoză de densitate a randamentelor zilnice, transformarea integrală a probabilității u_t = F̂_t(r_t) cade sub 0,01 în 1,67% din zile și peste 0,99 în 1,08% din zile. Ce arată acest lucru?",
                    "options": [
                        "Distribuția predictivă este prea largă: prea puține rezultate în cozi",
                        "Media predictivă este deplasată în sus, iar dispersia este corectă",
                        "Prognoza este perfect calibrată, pentru că valorile PIT sînt între 0 și 1",
                        "Coada stîngă a distribuției predictive este prea subțire: prea multe rezultate cad sub cuantila ei de 1%; testul Berkowitz pe Φ⁻¹(u_t) o cuantifică"
                    ],
                    "correctExplanation": "La o calibrare corectă PIT este i.i.d. uniformă, deci 1% din zile ar trebui să cadă sub 0,01. Un exces în coada stîngă înseamnă că acolo cuantilele prognozate sînt prea înguste (Chronos-2 direct pe S&P 500).",
                    "incorrectExplanation": "Excesul de masă într-un interval de coadă al PIT înseamnă o distribuție predictivă prea îngustă în acea coadă; o prognoză prea largă dă prea puțină masă în cozi."
                }
            },
            {
                "correct": 0,
                "en": {
                    "title": "Coverage versus independence",
                    "text": "A VaR 1% model has the right number of breaches (Kupiec p = 0.70) but a Christoffersen independence p-value of 0.02 and a DQ p-value of 0.001. What do you conclude?",
                    "options": [
                        "Coverage is right on average, but breaches cluster: the VaR reacts too slowly after volatility jumps, so conditional coverage is rejected",
                        "The model passes, because the Kupiec test is the regulatory test",
                        "Independence only matters for ES, not for VaR",
                        "Clustered breaches mean the VaR is too large on average"
                    ],
                    "correctExplanation": "This is the Chronos-2 hybrid on the S&P 500: breach rate 0.93%, but breaches follow breaches. The DQ test (Engle–Manganelli) regresses hits on lagged hits and on the VaR itself and also rejects.",
                    "incorrectExplanation": "A correct unconditional rate does not imply correct conditional coverage; independence and DQ tests detect breaches that arrive in clusters."
                },
                "ro": {
                    "title": "Acoperire versus independență",
                    "text": "Un model VaR 1% are numărul corect de depășiri (p Kupiec = 0,70), dar valoarea p a testului de independență Christoffersen este 0,02, iar a testului DQ 0,001. Ce concluzionați?",
                    "options": [
                        "Acoperirea este corectă în medie, dar depășirile se grupează: VaR reacționează prea încet după salturile volatilității, deci acoperirea condiționată este respinsă",
                        "Modelul trece, pentru că testul Kupiec este testul de reglementare",
                        "Independența contează doar pentru ES, nu și pentru VaR",
                        "Depășirile grupate înseamnă că VaR este prea mare în medie"
                    ],
                    "correctExplanation": "Este hibridul Chronos-2 pe S&P 500: rata de depășire 0,93%, dar depășirile urmează depășirilor. Testul DQ (Engle–Manganelli) regresează depășirile pe depășirile întîrziate și pe VaR și respinge și el.",
                    "incorrectExplanation": "O rată necondiționată corectă nu implică o acoperire condiționată corectă; testele de independență și DQ detectează depășirile care vin grupate."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "Quantile levels",
                    "text": "Chronos-Bolt outputs quantiles only between 10% and 90%. What happens if you ask it for VaR 1%?",
                    "options": [
                        "The model extrapolates the tail exactly with a generalised Pareto distribution",
                        "The requested 1% quantile is replaced by the 10% quantile, so the breach rate is around 10% or more instead of 1%",
                        "The model returns the 1% quantile of the Normal distribution with the same variance",
                        "The request fails and no forecast is produced"
                    ],
                    "correctExplanation": "Outside its training levels Chronos-Bolt clamps to the nearest available level, so a 'VaR 1%' is really a 10% quantile.",
                    "incorrectExplanation": "The library clamps the request to the lowest available level (10%); the tail is not extrapolated."
                },
                "ro": {
                    "title": "Nivelurile cuantilelor",
                    "text": "Chronos-Bolt produce cuantile doar între 10% și 90%. Ce se întîmplă dacă îi cereți VaR 1%?",
                    "options": [
                        "Modelul extrapolează exact coada cu o distribuție Pareto generalizată",
                        "Cuantila de 1% cerută este înlocuită cu cuantila de 10%, deci rata depășirilor este în jur de 10% sau mai mult, nu 1%",
                        "Modelul întoarce cuantila de 1% a distribuției Normale cu aceeași varianță",
                        "Cererea eșuează și nu se produce nicio prognoză"
                    ],
                    "correctExplanation": "În afara nivelurilor de antrenare, Chronos-Bolt se limitează la cel mai apropiat nivel disponibil, deci un „VaR 1%” este de fapt o cuantilă de 10%.",
                    "incorrectExplanation": "Biblioteca limitează cererea la cel mai mic nivel disponibil (10%); coada nu este extrapolată."
                }
            },
            {
                "correct": 2,
                "en": {
                    "title": "ES from a quantile grid",
                    "text": "A model gives quantiles at 1%, 5%, 10%, ... You compute ES 2.5% by integrating the quantile function from 0 to 2.5%, keeping it constant below 1%. Assuming the quantile function is exact between 1% and 2.5%, what is the direction of the error caused by this clamping?",
                    "options": [
                        "ES is overestimated, because the grid is too coarse",
                        "There is no error: ES depends only on the 2.5% quantile",
                        "ES is underestimated, because the true quantiles below 1% are more negative than the 1% quantile",
                        "ES becomes negative"
                    ],
                    "correctExplanation": "Holding the quantile at its 1% value below 1% cuts off the most extreme part of the tail, so the average tail loss is too small; interpolation between grid levels would add an error of either sign.",
                    "incorrectExplanation": "The cut-off tail below the lowest level makes the computed ES too small."
                },
                "ro": {
                    "title": "ES dintr-o grilă de cuantile",
                    "text": "Un model dă cuantile la 1%, 5%, 10%, ... Calculați ES 2,5% integrînd funcția cuantilă de la 0 la 2,5% și păstrînd-o constantă sub 1%. Presupunînd că funcția cuantilă este exactă între 1% și 2,5%, în ce sens este eroarea produsă de această limitare?",
                    "options": [
                        "ES este supraestimat, pentru că grila este prea rară",
                        "Nu există eroare: ES depinde doar de cuantila de 2,5%",
                        "ES este subestimat, pentru că adevăratele cuantile sub 1% sînt mai negative decît cuantila de 1%",
                        "ES devine negativ"
                    ],
                    "correctExplanation": "Păstrarea cuantilei la valoarea de 1% sub nivelul de 1% taie partea cea mai extremă a cozii, deci pierderea medie din coadă iese prea mică; interpolarea între nivelurile grilei ar adăuga o eroare de orice semn.",
                    "incorrectExplanation": "Coada trunchiată sub cel mai mic nivel face ca ES calculat să fie prea mic."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Pretraining leakage",
                    "text": "Why can a foundation model look better than it is when it is evaluated on public financial series?",
                    "options": [
                        "Because foundation models always use more parameters than GARCH",
                        "Because financial series are too short for any test",
                        "Because zero-shot models cannot be evaluated with scoring functions",
                        "Its pretraining corpus may contain the same or related series over the test period, so the test is not truly out of sample"
                    ],
                    "correctExplanation": "If the test period overlaps the pretraining data, the model may have seen the answers; a window after the release of the weights removes this risk.",
                    "incorrectExplanation": "The concern is information from the test period entering through the pretraining data."
                },
                "ro": {
                    "title": "Leakage prin pre-antrenare",
                    "text": "De ce poate un model fundațional să pară mai bun decît este cînd este evaluat pe serii financiare publice?",
                    "options": [
                        "Pentru că modelele fundaționale au mereu mai mulți parametri decît GARCH",
                        "Pentru că seriile financiare sînt prea scurte pentru orice test",
                        "Pentru că modelele zero-shot nu pot fi evaluate cu funcții de scor",
                        "Corpusul lui de pre-antrenare poate conține aceleași serii sau serii înrudite din perioada de test, deci testul nu este cu adevărat în afara eșantionului"
                    ],
                    "correctExplanation": "Dacă perioada de test se suprapune cu datele de pre-antrenare, modelul poate să fi văzut deja răspunsurile; o fereastră de după publicarea ponderilor elimină acest risc.",
                    "incorrectExplanation": "Problema este informația din perioada de test care intră prin datele de pre-antrenare."
                }
            },
            {
                "correct": 0,
                "en": {
                    "title": "Power of a short window",
                    "text": "After the release of the weights there are 220 trading days. A VaR 1% model has a true breach rate of 1.67%. What is the exact power of the two-sided Kupiec test at 5%?",
                    "options": [
                        "About 0.19: with 2.2 expected breaches the test almost never detects a 67% excess, so non-rejection is not evidence of correct coverage",
                        "About 0.95, because the breach rate is 67% too high",
                        "Exactly 0.05, the level of the test",
                        "It cannot be computed without knowing the distribution of returns"
                    ],
                    "correctExplanation": "The test rejects for x = 0 or x ≥ 6 breaches; under Bin(220, 0.0167) that has probability 0.025 + 0.165 ≈ 0.19. About 2,100–2,300 days are needed for 80% power.",
                    "incorrectExplanation": "Under the alternative the number of breaches is Binomial(T, 1.67%); summing its probabilities over the rejection region gives the power, which is low for T = 220."
                },
                "ro": {
                    "title": "Puterea unei ferestre scurte",
                    "text": "După publicarea ponderilor există 220 de zile de tranzacționare. Un model VaR 1% are o rată reală de depășire de 1,67%. Care este puterea exactă a testului Kupiec bilateral la 5%?",
                    "options": [
                        "Circa 0,19: cu 2,2 depășiri așteptate testul aproape niciodată nu detectează un exces de 67%, deci nerespingerea nu dovedește acoperirea corectă",
                        "Circa 0,95, pentru că rata de depășire este cu 67% prea mare",
                        "Exact 0,05, nivelul testului",
                        "Nu se poate calcula fără a cunoaște distribuția randamentelor"
                    ],
                    "correctExplanation": "Testul respinge pentru x = 0 sau x ≥ 6 depășiri; sub Bin(220; 0,0167) probabilitatea este 0,025 + 0,165 ≈ 0,19. Pentru o putere de 80% sînt necesare circa 2.100–2.300 de zile.",
                    "incorrectExplanation": "Sub alternativă numărul de depășiri este Binomial(T; 1,67%); suma probabilităților pe regiunea de respingere dă puterea, mică pentru T = 220."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "Adaptive conformal inference",
                    "text": "Adaptive conformal inference (Gibbs and Candès, 2021) is applied to the 1% quantile of Chronos-2. What does it guarantee?",
                    "options": [
                        "Correct coverage on every single day",
                        "A long-run breach rate close to 1% for any data sequence, without a correct model; it does not guarantee a sharp VaR or a low FZ0 loss",
                        "A VaR that is always smaller than the FHS VaR",
                        "Consistency of the ES estimate below the 1% quantile"
                    ],
                    "correctExplanation": "The level update α_{t+1} = α_t + γ(α − err_t) bounds the gap between the average breach rate and α by (max(α_1, 1 − α_1) + γ)/(γT). In the chapter it brings coverage near 1% in all three markets, but DQ still rejects on the S&P 500 and the BET and the wider VaR loses the FZ0 comparison with FHS.",
                    "incorrectExplanation": "The guarantee is about the long-run average breach rate only; sharpness, daily coverage and ES are not controlled."
                },
                "ro": {
                    "title": "Inferența conformală adaptivă",
                    "text": "Inferența conformală adaptivă (Gibbs și Candès, 2021) se aplică cuantilei de 1% a Chronos-2. Ce garantează?",
                    "options": [
                        "Acoperire corectă în fiecare zi",
                        "O rată de depășire pe termen lung apropiată de 1% pentru orice secvență de date, fără un model corect; nu garantează un VaR precis sau o pierdere FZ0 mică",
                        "Un VaR mereu mai mic decît VaR-ul FHS",
                        "Consistența estimării ES sub cuantila de 1%"
                    ],
                    "correctExplanation": "Actualizarea nivelului α_{t+1} = α_t + γ(α − err_t) limitează diferența dintre rata medie de depășire și α la (max(α_1, 1 − α_1) + γ)/(γT). În capitol aduce acoperirea aproape de 1% pe toate cele trei piețe, dar DQ încă respinge pe S&P 500 și BET, iar VaR-ul mai larg pierde comparația FZ0 cu FHS.",
                    "incorrectExplanation": "Garanția privește doar rata medie de depășire pe termen lung; precizia, acoperirea zilnică și ES nu sînt controlate."
                }
            },
            {
                "correct": 2,
                "en": {
                    "title": "QLIKE loss",
                    "text": "Why is the QLIKE loss preferred to the MSE for comparing volatility forecasts against realised variance?",
                    "options": [
                        "It is always smaller than the MSE",
                        "It does not require the forecasts to be positive",
                        "Like the MSE it ranks forecasts correctly when realised variance is a conditionally unbiased proxy, but it depends on the ratio of realisation to forecast and is less dominated by a few extreme days",
                        "It ignores under-prediction of volatility"
                    ],
                    "correctExplanation": "Patton (2011): both MSE and QLIKE keep the ranking of the true variance when E[RV | F] = σ²; QLIKE = y/f − log(y/f) − 1 penalises relative errors y/f, so a few high-variance days do not dominate the comparison.",
                    "incorrectExplanation": "Proxy robustness is shared with the MSE; the reason to prefer QLIKE is its relative-error scale; it requires positive forecasts and penalises under-prediction strongly."
                },
                "ro": {
                    "title": "Pierderea QLIKE",
                    "text": "De ce este preferată pierderea QLIKE în locul MSE pentru a compara prognozele de volatilitate cu varianța realizată?",
                    "options": [
                        "Este întotdeauna mai mică decît MSE",
                        "Nu cere ca prognozele să fie pozitive",
                        "La fel ca MSE, ordonează corect prognozele cînd varianța realizată este o aproximare condiționat nedeplasată, dar depinde de raportul dintre realizare și prognoză și este mai puțin dominată de cîteva zile extreme",
                        "Ignoră subestimarea volatilității"
                    ],
                    "correctExplanation": "Patton (2011): atît MSE, cît și QLIKE păstrează ordinea dată de varianța adevărată cînd E[RV | F] = σ²; QLIKE = y/f − log(y/f) − 1 penalizează erorile relative y/f, astfel încît cîteva zile cu varianță mare nu domină comparația.",
                    "incorrectExplanation": "Robustețea la aproximare este comună cu MSE; motivul pentru QLIKE este scala erorilor relative; QLIKE cere prognoze pozitive și penalizează puternic subestimarea."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Median versus mean",
                    "text": "A foundation model gives quantiles of log realised variance. Why is exp(median) a poor volatility forecast under QLIKE?",
                    "options": [
                        "Because the exponential of a quantile is not a quantile",
                        "Because the median is always above the mean",
                        "Because QLIKE is defined only for median forecasts",
                        "Realised variance is right-skewed, so the median is below the mean; the forecast is biased downwards and QLIKE punishes under-prediction"
                    ],
                    "correctExplanation": "Monotone transforms preserve quantiles, so exp(median) is the median of RV, which lies below its mean; averaging exp(q_u) over the grid approximates the mean.",
                    "incorrectExplanation": "The issue is skewness: the median of RV is below its mean, and QLIKE is minimised by the conditional mean."
                },
                "ro": {
                    "title": "Mediana versus media",
                    "text": "Un model fundațional dă cuantile ale logaritmului varianței realizate. De ce este exp(mediana) o prognoză slabă de volatilitate sub QLIKE?",
                    "options": [
                        "Pentru că exponențiala unei cuantile nu este o cuantilă",
                        "Pentru că mediana este mereu peste medie",
                        "Pentru că QLIKE este definită doar pentru prognoze mediane",
                        "Varianța realizată este asimetrică la dreapta, deci mediana este sub medie; prognoza este deplasată în jos, iar QLIKE penalizează subestimarea"
                    ],
                    "correctExplanation": "Transformările monotone păstrează cuantilele, deci exp(mediana) este mediana lui RV, aflată sub medie; media lui exp(q_u) pe grilă aproximează media.",
                    "incorrectExplanation": "Problema este asimetria: mediana lui RV este sub medie, iar QLIKE este minimizată de media condiționată."
                }
            },
            {
                "correct": 0,
                "en": {
                    "title": "Model confidence set",
                    "text": "What does it mean that several models are inside the 90% model confidence set (MCS) for the QLIKE loss?",
                    "options": [
                        "The data cannot distinguish them: none of them is significantly worse than the best at the 10% level",
                        "All of them have exactly the same average loss",
                        "Each of them beats the random walk with 90% probability",
                        "They are the three models with the smallest number of parameters"
                    ],
                    "correctExplanation": "The MCS keeps every model whose elimination is not supported by the data at the chosen level (Hansen, Lunde & Nason, 2011).",
                    "incorrectExplanation": "Membership means 'not rejected as worse', not equal losses or a probability of beating a benchmark."
                },
                "ro": {
                    "title": "Mulțimea de modele de încredere",
                    "text": "Ce înseamnă că mai multe modele sînt în mulțimea de modele de încredere (MCS) de 90% pentru pierderea QLIKE?",
                    "options": [
                        "Datele nu le pot distinge: niciunul nu este semnificativ mai slab decît cel mai bun la pragul de 10%",
                        "Toate au exact aceeași pierdere medie",
                        "Fiecare bate modelul random walk cu probabilitatea 90%",
                        "Sînt cele trei modele cu cei mai puțini parametri"
                    ],
                    "correctExplanation": "MCS păstrează orice model a cărui eliminare nu este susținută de date la pragul ales (Hansen, Lunde & Nason, 2011).",
                    "incorrectExplanation": "Apartenența înseamnă „nerespins ca fiind mai slab”, nu pierderi egale sau o probabilitate de a bate un reper."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "Hybrid tail model",
                    "text": "The hybrid model standardises returns by a foundation-model volatility forecast and takes empirical quantiles of the standardised returns (FHS). Why does the overall scale of that volatility forecast not matter?",
                    "options": [
                        "Because VaR is defined without reference to volatility",
                        "Multiplying the volatility by a constant rescales the standardised returns by the inverse constant, and the two effects cancel in the VaR",
                        "Because foundation models always output the exact standard deviation",
                        "Because the empirical quantile of standardised returns is always −2.33"
                    ],
                    "correctExplanation": "VaR = −σ̂_t × q_α(r/σ̂); replacing σ̂ by cσ̂ multiplies the first factor by c and divides the second by c.",
                    "incorrectExplanation": "In filtered historical simulation a constant factor in σ̂ cancels; only the relative dynamics of σ̂ matter."
                },
                "ro": {
                    "title": "Model hibrid pentru coadă",
                    "text": "Modelul hibrid standardizează randamentele cu prognoza de volatilitate a unui model fundațional și ia cuantilele empirice ale randamentelor standardizate (FHS). De ce nu contează scala generală a acestei prognoze de volatilitate?",
                    "options": [
                        "Pentru că VaR este definit fără legătură cu volatilitatea",
                        "Înmulțirea volatilității cu o constantă rescalează randamentele standardizate cu inversul constantei, iar cele două efecte se anulează în VaR",
                        "Pentru că modelele fundaționale dau mereu abaterea standard exactă",
                        "Pentru că cuantila empirică a randamentelor standardizate este mereu −2,33"
                    ],
                    "correctExplanation": "VaR = −σ̂_t × q_α(r/σ̂); înlocuirea lui σ̂ cu cσ̂ înmulțește primul factor cu c și îl împarte pe al doilea la c.",
                    "incorrectExplanation": "În simularea istorică filtrată, un factor constant din σ̂ se anulează; contează doar dinamica relativă a lui σ̂."
                }
            },
            {
                "correct": 2,
                "en": {
                    "title": "Early stopping",
                    "text": "Why must the validation set used for early stopping follow the training set in time, rather than being a random sample of windows?",
                    "options": [
                        "Because random sampling is slower on a CPU",
                        "Because early stopping only works with the MSE loss",
                        "Overlapping windows of neighbouring days are almost identical; a random split puts near-copies of validation windows in the training set and makes the validation loss too optimistic",
                        "Because a time-ordered split always gives a smaller validation loss"
                    ],
                    "correctExplanation": "With overlapping windows, a shuffled split leaks information between training and validation; the time-ordered split mimics real forecasting.",
                    "incorrectExplanation": "The issue is leakage between overlapping windows, which makes a shuffled validation loss too optimistic."
                },
                "ro": {
                    "title": "Oprirea timpurie",
                    "text": "De ce trebuie ca setul de validare folosit pentru oprirea timpurie să urmeze în timp setului de antrenare, și nu să fie un eșantion aleator de ferestre?",
                    "options": [
                        "Pentru că eșantionarea aleatoare este mai lentă pe procesor",
                        "Pentru că oprirea timpurie funcționează doar cu pierderea MSE",
                        "Ferestrele suprapuse din zile vecine sînt aproape identice; o împărțire aleatoare pune aproape-copii ale ferestrelor de validare în setul de antrenare și face pierderea de validare prea optimistă",
                        "Pentru că împărțirea în ordinea timpului dă mereu o pierdere de validare mai mică"
                    ],
                    "correctExplanation": "Cu ferestre suprapuse, o împărțire amestecată produce leakage între antrenare și validare; împărțirea în ordinea timpului imită prognoza reală.",
                    "incorrectExplanation": "Problema este leakage-ul între ferestrele suprapuse, care face pierderea de validare amestecată prea optimistă."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Random seeds",
                    "text": "Five LSTMs with identical data and architecture but different random seeds give different out-of-sample R². What is the right reporting practice?",
                    "options": [
                        "Report only the best seed, since it shows the potential of the method",
                        "Report only the first seed, since the choice is arbitrary",
                        "Increase the number of epochs until all seeds give the same R²",
                        "Report the whole distribution across seeds (or the ensemble average) and not the best single run"
                    ],
                    "correctExplanation": "When the signal is weak, seed-to-seed variation is of the same size as the effect; choosing the best seed is a form of backtest overfitting.",
                    "incorrectExplanation": "Selecting the best seed after seeing test results overstates performance; report all seeds or an ensemble."
                },
                "ro": {
                    "title": "Seed-urile aleatoare",
                    "text": "Cinci LSTM-uri cu aceleași date și aceeași arhitectură, dar cu seed-uri aleatoare diferite, dau valori diferite ale R² în afara eșantionului. Care este practica corectă de raportare?",
                    "options": [
                        "Raportați doar cel mai bun seed, pentru că arată potențialul metodei",
                        "Raportați doar primul seed, pentru că alegerea este arbitrară",
                        "Creșteți numărul de epoci pînă cînd toate seed-urile dau același R²",
                        "Raportați întreaga distribuție pe seed-uri (sau media ansamblului), nu cea mai bună rulare"
                    ],
                    "correctExplanation": "Cînd semnalul este slab, variația de la un seed la altul are aceeași mărime ca efectul; alegerea celui mai bun seed este o formă de overfitting al backtestului.",
                    "incorrectExplanation": "Alegerea celui mai bun seed după ce ați văzut rezultatele de test supraestimează rezultatele metodei; raportați toate seed-urile sau un ansamblu."
                }
            },
            {
                "correct": 0,
                "en": {
                    "title": "Joint scoring of VaR and ES",
                    "text": "Why is the FZ0 loss evaluated on the pair (VaR 2.5%, ES 2.5%) rather than on ES 2.5% alone?",
                    "options": [
                        "ES is not elicitable on its own, but the pair (VaR, ES) at the same level is jointly elicitable, so FZ0 ranks forecasts of the pair consistently",
                        "Because FZ0 is defined only for VaR",
                        "Because ES 2.5% is always smaller than VaR 2.5%",
                        "Because the Basel rules ban scoring functions for ES"
                    ],
                    "correctExplanation": "Fissler and Ziegel (2016) show that (VaR_α, ES_α) is jointly elicitable; FZ0 (Patton, Ziegel & Chen, 2019) is a member of that family.",
                    "incorrectExplanation": "ES alone has no strictly consistent scoring function; the pair with the VaR at the same level does."
                },
                "ro": {
                    "title": "Funcții de scor comune pentru VaR și ES",
                    "text": "De ce este pierderea FZ0 evaluată pe perechea (VaR 2,5%, ES 2,5%), și nu doar pe ES 2,5%?",
                    "options": [
                        "ES nu este elicitabil singur, dar perechea (VaR, ES) la același nivel este elicitabilă în comun, deci FZ0 ordonează consecvent prognozele perechii",
                        "Pentru că FZ0 este definită doar pentru VaR",
                        "Pentru că ES 2,5% este mereu mai mic decît VaR 2,5%",
                        "Pentru că regulile Basel interzic funcțiile de scor pentru ES"
                    ],
                    "correctExplanation": "Fissler și Ziegel (2016) arată că (VaR_α, ES_α) este elicitabilă în comun; FZ0 (Patton, Ziegel & Chen, 2019) face parte din această familie.",
                    "incorrectExplanation": "ES singur nu are o funcție de scor strict consecventă; perechea cu VaR la același nivel are."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "Context length",
                    "text": "For Chronos-2 on log realised variance, the QLIKE loss falls as the context grows from 32 to 512 days. What is the most plausible reason?",
                    "options": [
                        "Longer contexts always make any model more accurate",
                        "Volatility has long memory: a longer context gives the model more information about the slowly decaying level of volatility",
                        "The model was trained only on 512-day series",
                        "A longer context removes the need for scaling"
                    ],
                    "correctExplanation": "Long memory in volatility means that information from months back still helps; a 32-day context misses the slow component.",
                    "incorrectExplanation": "The gain reflects the long memory of volatility, not a general law that longer is always better."
                },
                "ro": {
                    "title": "Lungimea contextului",
                    "text": "Pentru Chronos-2 aplicat logaritmului varianței realizate, pierderea QLIKE scade cînd contextul crește de la 32 la 512 zile. Care este motivul cel mai plauzibil?",
                    "options": [
                        "Contextele mai lungi fac orice model mai precis",
                        "Volatilitatea are memorie lungă: un context mai lung îi dă modelului mai multă informație despre nivelul volatilității, care scade încet",
                        "Modelul a fost antrenat doar pe serii de 512 zile",
                        "Un context mai lung elimină nevoia de scalare"
                    ],
                    "correctExplanation": "Memoria lungă a volatilității înseamnă că informația de acum cîteva luni încă ajută; un context de 32 de zile ratează componenta lentă.",
                    "incorrectExplanation": "Cîștigul reflectă memoria lungă a volatilității, nu o regulă generală că mai lung înseamnă mereu mai bine."
                }
            },
            {
                "correct": 2,
                "en": {
                    "title": "Deciles and VaR 10%",
                    "text": "Chronos-Bolt and TimesFM-2.5 give deciles. On daily returns, their 10% quantiles are breached more often than 10% of the time. What does this indicate?",
                    "options": [
                        "Their predictive distributions are too wide",
                        "They forecast the mean return too pessimistically",
                        "Their predictive distributions for returns are too narrow in the lower tail",
                        "The test period contains no crises"
                    ],
                    "correctExplanation": "More breaches than nominal means the forecast quantile is not far enough in the tail: the predictive distribution is too narrow.",
                    "incorrectExplanation": "Too many breaches of a quantile forecast means the lower tail is underestimated, i.e. the distribution is too narrow."
                },
                "ro": {
                    "title": "Decile și VaR 10%",
                    "text": "Chronos-Bolt și TimesFM-2.5 dau decile. Pe randamente zilnice, cuantilele lor de 10% sînt depășite în mai mult de 10% din zile. Ce indică acest lucru?",
                    "options": [
                        "Distribuțiile lor predictive sînt prea largi",
                        "Prognozează media randamentului prea pesimist",
                        "Distribuțiile lor predictive pentru randamente sînt prea înguste în coada stîngă",
                        "Perioada de test nu conține crize"
                    ],
                    "correctExplanation": "Mai multe depășiri decît nivelul nominal înseamnă că cuantila prognozată nu este suficient de departe în coadă: distribuția predictivă este prea îngustă.",
                    "incorrectExplanation": "Prea multe depășiri ale unei prognoze de cuantilă înseamnă că coada stîngă este subestimată, adică distribuția este prea îngustă."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Why a post-release window",
                    "text": "In this chapter, the forecasts are also evaluated from 3 November 2025 onwards. Why?",
                    "options": [
                        "Because markets were calmer after that date",
                        "Because the foundation models do not work on older data",
                        "Because the Basel rules require one year of data",
                        "All model weights used were published before that date, so those observations cannot be in any pretraining corpus"
                    ],
                    "correctExplanation": "A window that starts after the weights were fixed is genuinely out of sample for the foundation models, although short and less powerful.",
                    "incorrectExplanation": "The purpose is to rule out pretraining leakage; the price is fewer observations and lower power."
                },
                "ro": {
                    "title": "De ce o fereastră de după publicare",
                    "text": "În acest capitol, prognozele sînt evaluate și de la 3 noiembrie 2025 încolo. De ce?",
                    "options": [
                        "Pentru că piețele au fost mai calme după această dată",
                        "Pentru că modelele fundaționale nu funcționează pe date mai vechi",
                        "Pentru că regulile Basel cer un an de date",
                        "Toate ponderile modelelor folosite au fost publicate înainte de această dată, deci aceste observații nu pot fi în niciun corpus de pre-antrenare"
                    ],
                    "correctExplanation": "O fereastră care începe după fixarea ponderilor este cu adevărat în afara eșantionului pentru modelele fundaționale, deși este scurtă și are putere mai mică.",
                    "incorrectExplanation": "Scopul este eliminarea leakage-ului prin pre-antrenare; prețul este un număr mai mic de observații și o putere mai mică."
                }
            },
            {
                "correct": 3,
                "en": {
                    "title": "Spot the AI error: the context window",
                    "text": "An AI assistant writes: \"For the one-day-ahead forecast of r_t, pass Chronos the 512 most recent returns, context = r[t-511 : t+1] in Python.\" What is wrong?",
                    "options": [
                        "512 days are too few for a foundation model",
                        "Chronos must receive prices, not returns",
                        "The context must first be standardised to unit variance",
                        "The slice ends with r_t, the value being forecast: the context must stop at r_{t-1}, i.e. r[t-512 : t]"
                    ],
                    "correctExplanation": "A Python slice a:b includes a and excludes b, so r[t-511 : t+1] ends at r_t; the forecast then uses the answer (look-ahead), and backtests look far too good.",
                    "incorrectExplanation": "Write out the first and last index of the slice and compare the last one with the day being forecast."
                },
                "ro": {
                    "title": "Găsiți eroarea AI: fereastra de context",
                    "text": "Un asistent AI scrie: „Pentru prognoza la o zi a lui r_t, dați lui Chronos cele mai recente 512 randamente, context = r[t-511 : t+1] în Python.” Ce este greșit?",
                    "options": [
                        "512 zile sînt prea puține pentru un model fundațional",
                        "Chronos trebuie să primească prețuri, nu randamente",
                        "Contextul trebuie mai întîi standardizat la varianță unitară",
                        "Fragmentul se termină cu r_t, valoarea prognozată: contextul trebuie să se oprească la r_{t-1}, adică r[t-512 : t]"
                    ],
                    "correctExplanation": "Un fragment Python a:b include a și exclude b, deci r[t-511 : t+1] se termină la r_t; prognoza folosește atunci răspunsul (look-ahead bias), iar rezultatele backtestului par mult prea bune.",
                    "incorrectExplanation": "Scrieți primul și ultimul indice al fragmentului și comparați-l pe ultimul cu ziua prognozată."
                }
            },
            {
                "correct": 1,
                "en": {
                    "title": "Spot the AI error: too few breaches",
                    "text": "An AI assistant writes: \"Over 1,500 days the Chronos VaR 1% had only 5 breaches against 15 expected: the model is conservative, so it passes the Kupiec test easily.\" What is wrong?",
                    "options": [
                        "The Kupiec test only checks whether breaches are independent",
                        "The Kupiec test is two-sided: 5 breaches in 1,500 days give LR = 9.1 and a p-value of about 0.003, so correct coverage is rejected",
                        "The expected number of breaches is 1.5, not 15",
                        "5 breaches are too many, so the VaR is too small"
                    ],
                    "correctExplanation": "The unconditional coverage test rejects both too many and too few breaches; too few means the VaR is too large, and in a backtest it is often the symptom of look-ahead.",
                    "incorrectExplanation": "Compute the likelihood-ratio statistic of the unconditional coverage test instead of comparing 5 with 15 by eye."
                },
                "ro": {
                    "title": "Găsiți eroarea AI: prea puține depășiri",
                    "text": "Un asistent AI scrie: „Pe 1.500 de zile, VaR 1% al Chronos a avut doar 5 depășiri față de 15 așteptate: modelul este prudent, deci trece ușor testul Kupiec.” Ce este greșit?",
                    "options": [
                        "Testul Kupiec verifică doar dacă depășirile sînt independente",
                        "Testul Kupiec este bilateral: 5 depășiri în 1.500 de zile dau LR = 9,1 și o valoare p de aproximativ 0,003, deci acoperirea corectă este respinsă",
                        "Numărul așteptat de depășiri este 1,5, nu 15",
                        "5 depășiri sînt prea multe, deci VaR este prea mic"
                    ],
                    "correctExplanation": "Testul de acoperire necondiționată respinge atît prea multe, cît și prea puține depășiri; prea puține înseamnă un VaR prea mare și, într-un backtest, sînt adesea simptomul unui look-ahead bias.",
                    "incorrectExplanation": "Calculați statistica raportului de verosimilitate a testului de acoperire necondiționată în loc să comparați 5 cu 15 din ochi."
                }
            }
        ]
};

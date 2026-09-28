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
                "title": "Gradientul care dispare",
                "text": "De ce dispar gradienții când o rețea recurentă simplă (RNN) este antrenată pe secvențe lungi?",
                "options": [
                    "Gradientul față de o intrare aflată cu k pași în urmă este un produs de k matrice jacobiene; când normele lor sunt sub 1, produsul scade geometric",
                    "Pentru că funcția de pierdere a unei RNN este mereu convexă",
                    "Pentru că rata de învățare a lui Adam scade la zero după câteva epoci",
                    "Pentru că rețelele recurente nu pot folosi funcția de activare tanh"
                ],
                "correctExplanation": "Propagarea înapoi în timp înmulțește câte o matrice jacobiană pe pas; cu norme sub 1 (tanh saturat, ponderi mici), produsul scade ca |w|^k.",
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
                    "The derivative of c_T with respect to c_{T-k} is the product of the forget gates, so memory survives when the forget gate stays close to 1",
                    "The candidate g_t must be zero for the network to remember",
                    "The cell state is reset to zero at every step, so there is no long memory"
                ],
                "correctExplanation": "Along the cell-state path the only multiplier is the forget gate: the gradient is ∏ f_t, which decays slowly when f_t is near 1.",
                "incorrectExplanation": "The key path is the additive cell-state update; its gradient is the product of the forget gates."
            },
            "ro": {
                "title": "Starea celulei LSTM",
                "text": "Într-un LSTM, starea celulei evoluează după c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t. Ce implică acest lucru pentru învățarea memoriei lungi?",
                "options": [
                    "Doar poarta de ieșire decide cât de departe în urmă poate ajunge gradientul",
                    "Derivata lui c_T în raport cu c_{T-k} este produsul porților de uitare, deci memoria supraviețuiește când poarta de uitare rămâne aproape de 1",
                    "Candidatul g_t trebuie să fie zero pentru ca rețeaua să-și amintească",
                    "Starea celulei este resetată la zero la fiecare pas, deci nu există memorie lungă"
                ],
                "correctExplanation": "Pe drumul stării celulei singurul multiplicator este poarta de uitare: gradientul este ∏ f_t, care scade încet când f_t este aproape de 1.",
                "incorrectExplanation": "Drumul esențial este actualizarea aditivă a stării celulei; gradientul ei este produsul porților de uitare."
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
                "title": "Deplasarea porții de uitare",
                "text": "O poartă de uitare constantă f = σ(3) ≈ 0,953 este comparată cu f = σ(0) = 0,5. Ce fracțiune din semnal rămâne după 50 de pași în fiecare caz?",
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
                "title": "Counting parameters",
                "text": "A one-layer LSTM in PyTorch has input dimension d = 1 and hidden size h = 16. How many parameters does the LSTM layer have (PyTorch uses two bias vectors)?",
                "options": [
                    "16 × 16 = 256",
                    "4 × 16 = 64",
                    "16 + 1 = 17",
                    "4 × (16·1 + 16·16 + 2·16) = 1,216"
                ],
                "correctExplanation": "Each of the four blocks (three gates and the candidate) has h·d input weights, h·h recurrent weights and 2h biases: 4 × (16 + 256 + 32) = 1,216.",
                "incorrectExplanation": "Count four blocks, each with input weights, recurrent weights and two bias vectors: 4 × (16 + 256 + 32)."
            },
            "ro": {
                "title": "Numărarea parametrilor",
                "text": "Un LSTM cu un strat în PyTorch are dimensiunea intrării d = 1 și dimensiunea stării ascunse h = 16. Câți parametri are stratul LSTM (PyTorch folosește doi vectori de deplasare)?",
                "options": [
                    "16 × 16 = 256",
                    "4 × 16 = 64",
                    "16 + 1 = 17",
                    "4 × (16·1 + 16·16 + 2·16) = 1.216"
                ],
                "correctExplanation": "Fiecare dintre cele patru blocuri (trei porți și candidatul) are h·d ponderi de intrare, h·h ponderi recurente și 2h deplasări: 4 × (16 + 256 + 32) = 1.216.",
                "incorrectExplanation": "Numărați patru blocuri, fiecare cu ponderi de intrare, ponderi recurente și doi vectori de deplasare: 4 × (16 + 256 + 32)."
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
                "text": "În mecanismul de atenție, softmax(QK^T / √d_k) V, de ce sunt scorurile împărțite la √d_k?",
                "options": [
                    "Ca produsele scalare să nu crească odată cu dimensiunea, astfel încât softmax să nu se satureze și gradienții să rămână utilizabili",
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
                "title": "Positional encoding",
                "text": "Why does a Transformer for time series need positional information (for example, sinusoidal encodings or rotary embeddings)?",
                "options": [
                    "Because the softmax function cannot handle negative numbers",
                    "Self-attention treats its inputs as a set: without positions, reordering the time steps would not change the output",
                    "Because positional encodings replace the need for training data",
                    "Because time series always have a fixed seasonality"
                ],
                "correctExplanation": "Attention is permutation-equivariant; positions must be injected so that the model knows the order of observations.",
                "incorrectExplanation": "Without positional information attention cannot tell the order of the inputs."
            },
            "ro": {
                "title": "Codificarea poziției",
                "text": "De ce are nevoie un Transformer pentru serii de timp de informație despre poziție (de exemplu, codificări sinusoidale sau rotative)?",
                "options": [
                    "Pentru că funcția softmax nu poate lucra cu numere negative",
                    "Auto-atenția tratează intrările ca pe o mulțime: fără poziții, reordonarea pașilor de timp nu ar schimba rezultatul",
                    "Pentru că codificările de poziție înlocuiesc nevoia de date de antrenare",
                    "Pentru că seriile de timp au mereu o sezonalitate fixă"
                ],
                "correctExplanation": "Atenția este echivariantă la permutări; pozițiile trebuie introduse explicit ca modelul să cunoască ordinea observațiilor.",
                "incorrectExplanation": "Fără informație de poziție, atenția nu poate distinge ordinea intrărilor."
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
                "text": "Chronos-2 împarte un context de 512 zile în patch-uri de câte 16 zile. Care este câștigul principal?",
                "options": [
                    "Împărțirea în patch-uri elimină nevoia de scalare a seriei",
                    "Împărțirea în patch-uri garantează prognoze nedeplasate",
                    "Transformerul vede 32 de tokeni în loc de 512, ceea ce reduce costul pătratic al atenției și dă fiecărui token context local",
                    "Împărțirea în patch-uri face ca modelul să prognozeze doar la orizontul de 16 zile"
                ],
                "correctExplanation": "Costul atenției crește cu pătratul numărului de tokeni; 512/16 = 32 de tokeni este mult mai ieftin, iar fiecare patch rezumă dinamica locală.",
                "incorrectExplanation": "Câștigul este de calcul și de reprezentare: tokeni mai puțini și mai bogați."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Chronos tokenisation",
                "text": "How does the original Chronos turn a real-valued series into tokens?",
                "options": [
                    "It rounds each value to the nearest integer and uses it as a word index",
                    "It uses a pretrained text tokeniser on the printed digits",
                    "It fits an ARIMA model and tokenises the residuals",
                    "It divides the context by its mean absolute value and quantises the result into a fixed set of uniform bins"
                ],
                "correctExplanation": "Chronos applies mean scaling and uniform quantisation (4,096 tokens in total), then trains a T5 language model with cross-entropy.",
                "incorrectExplanation": "Chronos uses mean scaling followed by uniform binning, not rounding, text tokenisers or model residuals."
            },
            "ro": {
                "title": "Tokenizarea în Chronos",
                "text": "Cum transformă Chronos (versiunea originală) o serie cu valori reale în tokeni?",
                "options": [
                    "Rotunjește fiecare valoare la cel mai apropiat întreg și o folosește ca indice de cuvânt",
                    "Folosește un tokenizator de text pre-antrenat pe cifrele tipărite",
                    "Estimează un model ARIMA și tokenizează reziduurile",
                    "Împarte contextul la media valorilor absolute și cuantizează rezultatul într-o mulțime fixă de intervale uniforme"
                ],
                "correctExplanation": "Chronos aplică scalarea prin medie și cuantizarea uniformă (4.096 de tokeni în total), apoi antrenează un model de limbaj T5 cu entropia încrucișată.",
                "incorrectExplanation": "Chronos folosește scalarea prin medie urmată de intervale uniforme, nu rotunjire, tokenizatori de text sau reziduuri de model."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Zero-shot",
                "text": "What does zero-shot forecasting mean for a time-series foundation model?",
                "options": [
                    "The model forecasts a series it was never trained or fine-tuned on, using only the context passed at prediction time",
                    "The model makes forecasts with zero error on the training data",
                    "The model is trained from scratch on each new series",
                    "The model forecasts only the value zero for returns"
                ],
                "correctExplanation": "Zero-shot means no parameter update on the target series: the context window is the only information used.",
                "incorrectExplanation": "Zero-shot refers to using the pretrained weights unchanged on a new series."
            },
            "ro": {
                "title": "Zero-shot",
                "text": "Ce înseamnă prognoza zero-shot pentru un model fundațional pentru serii de timp?",
                "options": [
                    "Modelul prognozează o serie pe care nu a fost antrenat sau ajustat, folosind doar contextul transmis la momentul prognozei",
                    "Modelul face prognoze cu eroare zero pe datele de antrenare",
                    "Modelul este antrenat de la zero pentru fiecare serie nouă",
                    "Modelul prognozează pentru randamente doar valoarea zero"
                ],
                "correctExplanation": "Zero-shot înseamnă că parametrii nu se actualizează pe seria-țintă: fereastra de context este singura informație folosită.",
                "incorrectExplanation": "Zero-shot se referă la folosirea neschimbată a ponderilor pre-antrenate pe o serie nouă."
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
                "text": "Chronos-Bolt produce cuantile doar între 10% și 90%. Ce se întâmplă dacă îi cereți VaR 1%?",
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
                "text": "A model gives quantiles at 1%, 5%, 10%, ... You compute ES 2.5% by integrating the quantile function from 0 to 2.5%, keeping it constant below 1%. What is the direction of the error?",
                "options": [
                    "ES is overestimated, because the grid is too coarse",
                    "There is no error: ES depends only on the 2.5% quantile",
                    "ES is underestimated, because the true quantiles below 1% are more negative than the 1% quantile",
                    "ES becomes negative"
                ],
                "correctExplanation": "Holding the quantile at its 1% value below 1% cuts off the most extreme part of the tail, so the average tail loss is too small.",
                "incorrectExplanation": "The cut-off tail below the lowest level makes the computed ES too small."
            },
            "ro": {
                "title": "ES dintr-o grilă de cuantile",
                "text": "Un model dă cuantile la 1%, 5%, 10%, ... Calculați ES 2,5% integrând funcția cuantilă de la 0 la 2,5% și păstrând-o constantă sub 1%. În ce sens este eroarea?",
                "options": [
                    "ES este supraestimat, pentru că grila este prea rară",
                    "Nu există eroare: ES depinde doar de cuantila de 2,5%",
                    "ES este subestimat, pentru că adevăratele cuantile sub 1% sunt mai negative decât cuantila de 1%",
                    "ES devine negativ"
                ],
                "correctExplanation": "Păstrarea cuantilei la valoarea de 1% sub nivelul de 1% taie partea cea mai extremă a cozii, deci pierderea medie din coadă iese prea mică.",
                "incorrectExplanation": "Coada tăiată sub cel mai mic nivel face ca ES calculat să fie prea mic."
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
                "title": "Scurgerea de informație prin pre-antrenare",
                "text": "De ce poate un model fundațional să pară mai bun decât este când este evaluat pe serii financiare publice?",
                "options": [
                    "Pentru că modelele fundaționale au mereu mai mulți parametri decât GARCH",
                    "Pentru că seriile financiare sunt prea scurte pentru orice test",
                    "Pentru că modelele zero-shot nu pot fi evaluate cu funcții de scor",
                    "Corpusul lui de pre-antrenare poate conține aceleași serii sau serii înrudite din perioada de test, deci testul nu este cu adevărat în afara eșantionului"
                ],
                "correctExplanation": "Dacă perioada de test se suprapune cu datele de pre-antrenare, modelul poate fi văzut deja răspunsurile; o fereastră de după publicarea ponderilor elimină acest risc.",
                "incorrectExplanation": "Problema este informația din perioada de test care intră prin datele de pre-antrenare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Out-of-sample R²",
                "text": "For daily returns, the out-of-sample R² is computed against the zero forecast. What does a negative value mean?",
                "options": [
                    "The model's squared forecast errors are larger than those of always forecasting a zero return",
                    "The model predicts the sign of returns worse than a coin flip",
                    "The model has more parameters than observations",
                    "The model's forecasts are negatively correlated with past returns"
                ],
                "correctExplanation": "R²_oos = 1 − Σ(r − f)² / Σr²; it is negative when the model's MSE exceeds that of the zero forecast.",
                "incorrectExplanation": "The benchmark is the zero forecast: a negative value means a larger mean squared error than that benchmark."
            },
            "ro": {
                "title": "R² în afara eșantionului",
                "text": "Pentru randamente zilnice, R² în afara eșantionului se calculează față de prognoza zero. Ce înseamnă o valoare negativă?",
                "options": [
                    "Erorile pătratice ale modelului sunt mai mari decât cele ale prognozei constante de randament zero",
                    "Modelul prezice semnul randamentelor mai prost decât aruncarea unei monede",
                    "Modelul are mai mulți parametri decât observații",
                    "Prognozele modelului sunt corelate negativ cu randamentele trecute"
                ],
                "correctExplanation": "R²_oos = 1 − Σ(r − f)² / Σr²; este negativ când MSE-ul modelului depășește MSE-ul prognozei zero.",
                "incorrectExplanation": "Reperul este prognoza zero: o valoare negativă înseamnă o eroare pătratică medie mai mare decât a acestui reper."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Why volatility is forecastable",
                "text": "Daily S&P 500 returns show almost no autocorrelation, but absolute returns do. What follows for deep-learning forecasts?",
                "options": [
                    "Returns are perfectly predictable, volatility is not",
                    "There is little to learn about the conditional mean, but the persistence in the size of moves gives any model a signal for volatility",
                    "Neither returns nor volatility can be forecast",
                    "Only foundation models can exploit the autocorrelation of absolute returns"
                ],
                "correctExplanation": "The autocorrelation of |r_t| is positive and slowly decaying (volatility clustering); the mean has almost no signal.",
                "incorrectExplanation": "The signal is in the size of the moves, not in their direction; simple models such as HAR already capture it."
            },
            "ro": {
                "title": "De ce volatilitatea este previzibilă",
                "text": "Randamentele zilnice ale S&P 500 nu au aproape deloc autocorelație, dar randamentele absolute au. Ce rezultă pentru prognozele cu deep learning?",
                "options": [
                    "Randamentele sunt perfect previzibile, volatilitatea nu",
                    "Despre media condiționată este puțin de învățat, dar persistența mărimii mișcărilor dă oricărui model un semnal pentru volatilitate",
                    "Nici randamentele, nici volatilitatea nu pot fi prognozate",
                    "Doar modelele fundaționale pot exploata autocorelația randamentelor absolute"
                ],
                "correctExplanation": "Autocorelația lui |r_t| este pozitivă și scade încet (gruparea volatilității); media nu are aproape niciun semnal.",
                "incorrectExplanation": "Semnalul este în mărimea mișcărilor, nu în direcția lor; modele simple precum HAR îl captează deja."
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
                    "It ranks forecasts consistently even when realised variance is a noisy proxy of the true variance, and it is less dominated by a few extreme days",
                    "It ignores under-prediction of volatility"
                ],
                "correctExplanation": "QLIKE = y/f − log(y/f) − 1 is robust to proxy noise (Patton, 2011) and depends on the ratio y/f rather than on squared levels.",
                "incorrectExplanation": "The reason is robustness to the noisy proxy and to extreme days; QLIKE requires positive forecasts and penalises under-prediction strongly."
            },
            "ro": {
                "title": "Pierderea QLIKE",
                "text": "De ce este preferată pierderea QLIKE în locul MSE pentru a compara prognozele de volatilitate cu varianța realizată?",
                "options": [
                    "Este întotdeauna mai mică decât MSE",
                    "Nu cere ca prognozele să fie pozitive",
                    "Clasifică prognozele consecvent chiar și când varianța realizată este o aproximare zgomotoasă a varianței adevărate și este mai puțin dominată de câteva zile extreme",
                    "Ignoră subestimarea volatilității"
                ],
                "correctExplanation": "QLIKE = y/f − log(y/f) − 1 este robustă la zgomotul aproximării (Patton, 2011) și depinde de raportul y/f, nu de nivelurile la pătrat.",
                "incorrectExplanation": "Motivul este robustețea la aproximarea zgomotoasă și la zilele extreme; QLIKE cere prognoze pozitive și penalizează puternic subestimarea."
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
                "text": "Ce înseamnă că mai multe modele sunt în mulțimea de modele de încredere (MCS) de 90% pentru pierderea QLIKE?",
                "options": [
                    "Datele nu le pot distinge: niciunul nu este semnificativ mai slab decât cel mai bun la pragul de 10%",
                    "Toate au exact aceeași pierdere medie",
                    "Fiecare bate modelul random walk cu probabilitatea 90%",
                    "Sunt cele trei modele cu cei mai puțini parametri"
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
                "correctExplanation": "VaR = σ̂_t × q_α(r/σ̂); replacing σ̂ by cσ̂ multiplies the first factor by c and divides the second by c.",
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
                "correctExplanation": "VaR = σ̂_t × q_α(r/σ̂); înlocuirea lui σ̂ cu cσ̂ înmulțește primul factor cu c și îl împarte pe al doilea la c.",
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
                    "Ferestrele suprapuse din zile vecine sunt aproape identice; o împărțire aleatoare pune aproape-copii ale ferestrelor de validare în setul de antrenare și face pierderea de validare prea optimistă",
                    "Pentru că împărțirea în ordinea timpului dă mereu o pierdere de validare mai mică"
                ],
                "correctExplanation": "Cu ferestre suprapuse, o împărțire amestecată scurge informație între antrenare și validare; împărțirea în ordinea timpului imită prognoza reală.",
                "incorrectExplanation": "Problema este scurgerea de informație între ferestrele suprapuse, care face pierderea de validare amestecată prea optimistă."
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
                "title": "Semințele aleatoare",
                "text": "Cinci LSTM-uri cu aceleași date și aceeași arhitectură, dar cu semințe aleatoare diferite, dau valori diferite ale R² în afara eșantionului. Care este practica corectă de raportare?",
                "options": [
                    "Raportați doar cea mai bună sămânță, pentru că arată potențialul metodei",
                    "Raportați doar prima sămânță, pentru că alegerea este arbitrară",
                    "Creșteți numărul de epoci până când toate semințele dau același R²",
                    "Raportați întreaga distribuție pe semințe (sau media ansamblului), nu cea mai bună rulare"
                ],
                "correctExplanation": "Când semnalul este slab, variația de la o sămânță la alta are aceeași mărime ca efectul; alegerea celei mai bune semințe este o formă de supraajustare a backtestului.",
                "incorrectExplanation": "Alegerea celei mai bune semințe după ce ați văzut rezultatele de test supraestimează performanța; raportați toate semințele sau un ansamblu."
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
                "title": "Scorarea comună a VaR și ES",
                "text": "De ce este pierderea FZ0 evaluată pe perechea (VaR 2,5%, ES 2,5%), și nu doar pe ES 2,5%?",
                "options": [
                    "ES nu este elicitabil singur, dar perechea (VaR, ES) la același nivel este elicitabilă în comun, deci FZ0 clasifică prognozele perechii consecvent",
                    "Pentru că FZ0 este definită doar pentru VaR",
                    "Pentru că ES 2,5% este mereu mai mic decât VaR 2,5%",
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
                "text": "Pentru Chronos-2 aplicat logaritmului varianței realizate, pierderea QLIKE scade când contextul crește de la 32 la 512 zile. Care este motivul cel mai plauzibil?",
                "options": [
                    "Contextele mai lungi fac orice model mai precis",
                    "Volatilitatea are memorie lungă: un context mai lung îi dă modelului mai multă informație despre nivelul volatilității, care scade încet",
                    "Modelul a fost antrenat doar pe serii de 512 zile",
                    "Un context mai lung elimină nevoia de scalare"
                ],
                "correctExplanation": "Memoria lungă a volatilității înseamnă că informația de acum câteva luni încă ajută; un context de 32 de zile ratează componenta lentă.",
                "incorrectExplanation": "Câștigul reflectă memoria lungă a volatilității, nu o regulă generală că mai lung înseamnă mereu mai bine."
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
                "text": "Chronos-Bolt și TimesFM-2.5 dau decile. Pe randamente zilnice, cuantilele lor de 10% sunt depășite în mai mult de 10% din zile. Ce indică acest lucru?",
                "options": [
                    "Distribuțiile lor predictive sunt prea largi",
                    "Prognozează media randamentului prea pesimist",
                    "Distribuțiile lor predictive pentru randamente sunt prea înguste în coada stângă",
                    "Perioada de test nu conține crize"
                ],
                "correctExplanation": "Mai multe depășiri decât nivelul nominal înseamnă că cuantila prognozată nu este suficient de departe în coadă: distribuția predictivă este prea îngustă.",
                "incorrectExplanation": "Prea multe depășiri ale unei prognoze de cuantilă înseamnă că coada stângă este subestimată, adică distribuția este prea îngustă."
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
                "text": "În acest capitol, prognozele sunt evaluate și de la 3 noiembrie 2025 încolo. De ce?",
                "options": [
                    "Pentru că piețele au fost mai calme după această dată",
                    "Pentru că modelele fundaționale nu funcționează pe date mai vechi",
                    "Pentru că regulile Basel cer un an de date",
                    "Toate ponderile modelelor folosite au fost publicate înainte de această dată, deci aceste observații nu pot fi în niciun corpus de pre-antrenare"
                ],
                "correctExplanation": "O fereastră care începe după fixarea ponderilor este cu adevărat în afara eșantionului pentru modelele fundaționale, deși este scurtă și are putere mai mică.",
                "incorrectExplanation": "Scopul este eliminarea scurgerii prin pre-antrenare; prețul este un număr mai mic de observații și o putere mai mică."
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
                    "512 zile sunt prea puține pentru un model fundațional",
                    "Chronos trebuie să primească prețuri, nu randamente",
                    "Contextul trebuie mai întâi standardizat la varianță unitară",
                    "Fragmentul se termină cu r_t, valoarea prognozată: contextul trebuie să se oprească la r_{t-1}, adică r[t-512 : t]"
                ],
                "correctExplanation": "Un fragment Python a:b include a și exclude b, deci r[t-511 : t+1] se termină la r_t; prognoza folosește atunci răspunsul (informație din viitor), iar backtestul arată mult prea bine.",
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
                    "Testul Kupiec verifică doar dacă depășirile sunt independente",
                    "Testul Kupiec este bilateral: 5 depășiri în 1.500 de zile dau LR = 9,1 și o valoare p de aproximativ 0,003, deci acoperirea corectă este respinsă",
                    "Numărul așteptat de depășiri este 1,5, nu 15",
                    "5 depășiri sunt prea multe, deci VaR este prea mic"
                ],
                "correctExplanation": "Testul de acoperire necondiționată respinge atât prea multe, cât și prea puține depășiri; prea puține înseamnă un VaR prea mare și, într-un backtest, sunt adesea simptomul informației din viitor.",
                "incorrectExplanation": "Calculați statistica raportului de verosimilitate a testului de acoperire necondiționată în loc să comparați 5 cu 15 din ochi."
            }
        }
    ]
};

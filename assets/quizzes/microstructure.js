// ============================================================
// Quiz bank for chapter id 'microstructure': Market Microstructure (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['microstructure'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "Roll with autocorrelated order flow",
                "text": "In the Roll model, trade signs form a symmetric stationary Markov chain with Corr(q_t, q_{t-k}) = 0.5^k (split orders), independent of efficient-price innovations and without information. Relative to the true half-spread c, the Roll estimator sqrt(-Cov(dp_t, dp_{t-1}))...",
                "options": [
                    "...overestimates c, because persistent flow adds negative autocorrelation",
                    "...is unbiased, because the efficient price is still a random walk",
                    "...underestimates c: it converges to c(1 - 0.5) = 0.5c",
                    "...is undefined, because the covariance becomes positive"
                ],
                "correctExplanation": "With Corr(q_t, q_{t-k}) = rho^k, Cov(dp_t, dp_{t-1}) = c^2 Cov(q_t - q_{t-1}, q_{t-1} - q_{t-2}) = -c^2 (1 - rho)^2, so the estimator returns c(1 - rho).",
                "incorrectExplanation": "Persistent signs make consecutive changes in q_t less likely to reverse, which shrinks the bounce: Cov = -c^2 (1 - rho)^2, still negative but smaller."
            },
            "ro": {
                "title": "Roll cu flux de ordine autocorelat",
                "text": "În modelul Roll, semnele tranzacțiilor formează un lanț Markov simetric și staționar cu Corr(q_t, q_{t-k}) = 0,5^k (ordine împărțite), independent de inovațiile prețului eficient și fără informație. Față de jumătatea adevărată de spread c, estimatorul Roll sqrt(-Cov(dp_t, dp_{t-1}))...",
                "options": [
                    "...supraestimează c, fiindcă fluxul persistent adaugă autocorelație negativă",
                    "...este nedeplasat, fiindcă prețul eficient rămâne un mers aleator",
                    "...subestimează c: converge la c(1 - 0,5) = 0,5c",
                    "...nu este definit, fiindcă covarianța devine pozitivă"
                ],
                "correctExplanation": "Cu Corr(q_t, q_{t-k}) = rho^k, Cov(dp_t, dp_{t-1}) = c^2 Cov(q_t - q_{t-1}, q_{t-1} - q_{t-2}) = -c^2 (1 - rho)^2, deci estimatorul dă c(1 - rho).",
                "incorrectExplanation": "Semnele persistente fac mai puțin probabilă inversarea lui q_t, ceea ce micșorează oscilația: Cov = -c^2 (1 - rho)^2, tot negativă, dar mai mică."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Kyle: the insider's intensity",
                "text": "In the Kyle model the market maker sets p = p_0 + lambda y. Maximising E[(v - p) x | v] over x gives the insider's intensity beta in x = beta (v - p_0) equal to...",
                "options": [
                    "1/(2 lambda)",
                    "1/lambda",
                    "lambda",
                    "sigma_v/sigma_u"
                ],
                "correctExplanation": "The objective is (v - p_0) x - lambda x^2; the first-order condition gives x = (v - p_0)/(2 lambda). In equilibrium this equals sigma_u/sigma_v.",
                "incorrectExplanation": "The insider's own order moves the price by lambda x, so the objective is quadratic, (v - p_0) x - lambda x^2; setting the derivative to zero halves the naive intensity."
            },
            "ro": {
                "title": "Kyle: intensitatea investitorului din interior",
                "text": "În modelul Kyle formatorul de piață stabilește p = p_0 + lambda y. Maximizând E[(v - p) x | v] după x, intensitatea beta din x = beta (v - p_0) este...",
                "options": [
                    "1/(2 lambda)",
                    "1/lambda",
                    "lambda",
                    "sigma_v/sigma_u"
                ],
                "correctExplanation": "Obiectivul este (v - p_0) x - lambda x^2; condiția de ordinul întâi dă x = (v - p_0)/(2 lambda). La echilibru aceasta este sigma_u/sigma_v.",
                "incorrectExplanation": "Propriul ordin mișcă prețul cu lambda x, deci obiectivul este pătratic, (v - p_0) x - lambda x^2; anularea derivatei înjumătățește intensitatea naivă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Lambda as a regression slope",
                "text": "In a Kyle economy with sigma_v = 2 and sigma_u = 10,000, you regress p - p_0 on the signed order flow y across many independent auctions. The population slope is...",
                "options": [
                    "beta = 5,000",
                    "sigma_v/sigma_u = 0.0002",
                    "1/lambda = 10,000",
                    "lambda = sigma_v/(2 sigma_u) = 0.0001"
                ],
                "correctExplanation": "p - p_0 = lambda y exactly, and lambda = Cov(v, y)/Var(y) is the market maker's own linear projection: sigma_v/(2 sigma_u) = 0.0001.",
                "incorrectExplanation": "The pricing rule is linear in y with coefficient lambda, which is the projection coefficient Cov(v, y)/Var(y) = sigma_v/(2 sigma_u)."
            },
            "ro": {
                "title": "Lambda ca pantă de regresie",
                "text": "Într-o economie Kyle cu sigma_v = 2 și sigma_u = 10.000, regresați p - p_0 pe fluxul de ordine cu semn y, pe multe licitații independente. Panta în populație este...",
                "options": [
                    "beta = 5.000",
                    "sigma_v/sigma_u = 0,0002",
                    "1/lambda = 10.000",
                    "lambda = sigma_v/(2 sigma_u) = 0,0001"
                ],
                "correctExplanation": "p - p_0 = lambda y exact, iar lambda = Cov(v, y)/Var(y) este chiar proiecția liniară a formatorului: sigma_v/(2 sigma_u) = 0,0001.",
                "incorrectExplanation": "Regula de preț este liniară în y cu coeficientul lambda, care este coeficientul de proiecție Cov(v, y)/Var(y) = sigma_v/(2 sigma_u)."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Information-share bounds",
                "text": "Two venues' prices of one asset are cointegrated. The Hasbrouck information share of venue 1 is reported as the interval [0.55, 0.80]. Why an interval and not a number?",
                "options": [
                    "It is a 95% confidence interval from the sampling error",
                    "The share depends on the Cholesky ordering when the VECM innovations are correlated",
                    "There are two cointegrating vectors",
                    "Prices are non-stationary, so the share is not identified"
                ],
                "correctExplanation": "The information share uses a Cholesky factor of the innovation covariance; with correlated innovations the two orderings give different shares, which are reported as bounds.",
                "incorrectExplanation": "The interval comes from identification, not sampling: the contemporaneous correlation of the innovations is attributed to one venue or the other depending on the ordering."
            },
            "ro": {
                "title": "Limitele ponderii informaționale",
                "text": "Prețurile aceluiași activ pe două platforme sunt cointegrate. Ponderea informațională Hasbrouck a platformei 1 este raportată ca intervalul [0,55; 0,80]. De ce un interval și nu un număr?",
                "options": [
                    "Este un interval de încredere de 95% din eroarea de selecție",
                    "Ponderea depinde de ordonarea Cholesky când inovațiile VECM sunt corelate",
                    "Există doi vectori de cointegrare",
                    "Prețurile sunt nestaționare, deci ponderea nu este identificată"
                ],
                "correctExplanation": "Ponderea informațională folosește un factor Cholesky al covarianței inovațiilor; cu inovații corelate, cele două ordonări dau ponderi diferite, raportate ca limite.",
                "incorrectExplanation": "Intervalul vine din identificare, nu din selecție: corelația contemporană a inovațiilor este atribuită uneia sau alteia dintre platforme, după ordonare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "MRR: adverse-selection share",
                "text": "In the Madhavan-Richardson-Roomans model the estimates are theta = 0.03 (permanent impact of the order-flow surprise) and phi = 0.01 (transitory cost). What share of the effective half-spread is adverse selection?",
                "options": [
                    "75%",
                    "25%",
                    "50%",
                    "3%"
                ],
                "correctExplanation": "The implied half-spread is phi + theta = 0.04; the adverse-selection share is theta/(phi + theta) = 0.03/0.04 = 75%.",
                "incorrectExplanation": "Adverse selection is the permanent part theta; divide it by the whole half-spread phi + theta."
            },
            "ro": {
                "title": "MRR: ponderea selecției adverse",
                "text": "În modelul Madhavan-Richardson-Roomans estimările sunt theta = 0,03 (impactul permanent al surprizei din fluxul de ordine) și phi = 0,01 (costul tranzitoriu). Ce parte din jumătatea de spread efectiv este selecție adversă?",
                "options": [
                    "75%",
                    "25%",
                    "50%",
                    "3%"
                ],
                "correctExplanation": "Jumătatea de spread implicată este phi + theta = 0,04; ponderea selecției adverse este theta/(phi + theta) = 0,03/0,04 = 75%.",
                "incorrectExplanation": "Selecția adversă este partea permanentă theta; împărțiți-o la întreaga jumătate de spread phi + theta."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Roll model",
                "text": "In the Roll model with half-spread c, what is the first-order autocovariance of trade price changes?",
                "options": [
                    "+c^2",
                    "0",
                    "-c^2",
                    "-2c^2"
                ],
                "correctExplanation": "The bid-ask bounce gives Cov(dp_t, dp_{t-1}) = -c^2, so the spread is 2 sqrt(-Cov).",
                "incorrectExplanation": "Trade prices alternate between bid and ask, which creates a negative autocovariance equal to minus the squared half-spread."
            },
            "ro": {
                "title": "Modelul Roll",
                "text": "În modelul Roll cu jumătatea de spread c, care este autocovarianța de ordinul 1 a variațiilor prețului tranzacțiilor?",
                "options": [
                    "+c^2",
                    "0",
                    "-c^2",
                    "-2c^2"
                ],
                "correctExplanation": "Oscilația bid-ask dă Cov(dp_t, dp_{t-1}) = -c^2, deci spread-ul este 2 sqrt(-Cov).",
                "incorrectExplanation": "Prețurile tranzacțiilor alternează între bid și ask, ceea ce creează o autocovarianță negativă egală cu minus pătratul jumătății de spread."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Roll estimate",
                "text": "The sample autocovariance of daily price changes is -0.0081 (lei squared). What is the Roll spread?",
                "options": [
                    "0.18 lei",
                    "0.09 lei",
                    "0.0081 lei",
                    "0.0162 lei"
                ],
                "correctExplanation": "c = sqrt(0.0081) = 0.09 and s = 2c = 0.18 lei.",
                "incorrectExplanation": "Take the square root of minus the covariance to get the half-spread, then double it."
            },
            "ro": {
                "title": "Estimarea Roll",
                "text": "Autocovarianța de selecție a variațiilor zilnice ale prețului este -0,0081 (lei la pătrat). Care este spread-ul Roll?",
                "options": [
                    "0,18 lei",
                    "0,09 lei",
                    "0,0081 lei",
                    "0,0162 lei"
                ],
                "correctExplanation": "c = sqrt(0,0081) = 0,09 și s = 2c = 0,18 lei.",
                "incorrectExplanation": "Extrageți rădăcina pătrată din minus covarianța pentru jumătatea de spread, apoi dublați-o."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "When Roll fails",
                "text": "What does the Roll estimator give when the sample autocovariance of price changes is positive?",
                "options": [
                    "A negative spread",
                    "A zero spread",
                    "Twice the volatility",
                    "No estimate: the square root of a negative number does not exist"
                ],
                "correctExplanation": "With positive autocovariance, -Cov is negative and the estimator is undefined.",
                "incorrectExplanation": "The formula 2 sqrt(-Cov) needs a non-positive sample covariance for a real-valued result. Positive sample values can arise from sampling error even when the Roll model holds, or from departures from its assumptions (trends, stale prices)."
            },
            "ro": {
                "title": "Când Roll eșuează",
                "text": "Ce dă estimatorul Roll când autocovarianța de selecție a variațiilor de preț este pozitivă?",
                "options": [
                    "Un spread negativ",
                    "Un spread zero",
                    "Dublul volatilității",
                    "Nicio estimare: rădăcina pătrată a unui număr negativ nu există"
                ],
                "correctExplanation": "Cu autocovarianță pozitivă, -Cov este negativă și estimatorul nu este definit.",
                "incorrectExplanation": "Formula 2 sqrt(-Cov) cere o covarianță de selecție nepozitivă pentru un rezultat real. Valorile de selecție pozitive pot apărea din eroarea de selecție chiar când modelul Roll este adevărat sau din abateri de la ipotezele lui (tendințe, prețuri vechi)."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "High-low estimators",
                "text": "Why does the Corwin-Schultz estimator compare the high-low range of one day with that of two days?",
                "options": [
                    "To remove weekends",
                    "Because volatility grows with the length of the interval and the spread does not",
                    "To estimate the tick size",
                    "Because closing prices are missing"
                ],
                "correctExplanation": "The two-day range contains twice the variance but the same spread, so the two can be separated.",
                "incorrectExplanation": "The method separates the part of the range that scales with time (volatility) from the part that does not (spread)."
            },
            "ro": {
                "title": "Estimatori maxim-minim",
                "text": "De ce compară estimatorul Corwin-Schultz intervalul maxim-minim al unei zile cu cel pe două zile?",
                "options": [
                    "Pentru a elimina weekendurile",
                    "Pentru că volatilitatea crește cu lungimea intervalului, iar spread-ul nu",
                    "Pentru a estima pasul de cotare",
                    "Pentru că lipsesc prețurile de închidere"
                ],
                "correctExplanation": "Intervalul pe două zile conține o dispersie dublă, dar același spread, deci cele două pot fi separate.",
                "incorrectExplanation": "Metoda separă partea intervalului care crește cu timpul (volatilitatea) de cea care nu crește (spread-ul)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Frequency matters",
                "text": "For SPY, daily Corwin-Schultz gives about 27 bp while one price step is about 0.2 bp. What explains the gap?",
                "options": [
                    "The SPY spread is really 27 bp",
                    "The data are wrong",
                    "On daily data the high-low range is dominated by volatility",
                    "The estimator only works for crypto-assets"
                ],
                "correctExplanation": "With a daily volatility near 1%, the range is almost all price movement; 5-minute bars bring the estimate down to about 3 bp.",
                "incorrectExplanation": "The estimator mistakes volatility for spread when the interval is long relative to the spread."
            },
            "ro": {
                "title": "Frecvența contează",
                "text": "Pentru SPY, Corwin-Schultz zilnic dă circa 27 pb, iar un pas de cotare este circa 0,2 pb. Ce explică diferența?",
                "options": [
                    "Spread-ul SPY este chiar de 27 pb",
                    "Datele sunt greșite",
                    "Pe date zilnice, intervalul maxim-minim este dominat de volatilitate",
                    "Estimatorul funcționează doar pentru cripto-active"
                ],
                "correctExplanation": "Cu o volatilitate zilnică de circa 1%, intervalul este aproape numai mișcare de preț; barele de 5 minute coboară estimarea la circa 3 pb.",
                "incorrectExplanation": "Estimatorul confundă volatilitatea cu spread-ul când intervalul este lung în raport cu spread-ul."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Amihud ratio",
                "text": "What does the Amihud illiquidity ratio measure?",
                "options": [
                    "The average absolute return per unit of money traded",
                    "The quoted spread divided by price",
                    "The number of trades per day",
                    "The volatility of volume"
                ],
                "correctExplanation": "ILLIQ is the average of the daily ratios |r_d| / traded value_d: an illiquidity proxy measuring absolute return per unit of money traded, not an identified causal impact.",
                "incorrectExplanation": "Amihud divides the absolute daily return by the traded value, giving price impact per unit of money."
            },
            "ro": {
                "title": "Raportul Amihud",
                "text": "Ce măsoară raportul de ilichiditate Amihud?",
                "options": [
                    "Randamentul absolut mediu per unitate de bani tranzacționați",
                    "Spread-ul cotat împărțit la preț",
                    "Numărul de tranzacții pe zi",
                    "Volatilitatea volumului"
                ],
                "correctExplanation": "ILLIQ este media rapoartelor zilnice |r_d| / valoarea tranzacționată_d: o aproximare a ilichidității, randamentul absolut per unitate de bani tranzacționați, nu un impact cauzal identificat.",
                "incorrectExplanation": "Amihud împarte randamentul zilnic absolut la valoarea tranzacționată, obținând impactul per unitate de bani."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "BVB liquidity",
                "text": "Compared with US large caps, what does the Amihud ratio say about BVB blue chips (2024-2026)?",
                "options": [
                    "They are about as liquid",
                    "They are twice as illiquid",
                    "They are more liquid",
                    "They need thousands of times more price move per dollar traded"
                ],
                "correctExplanation": "Banca Transilvania, the most liquid BVB stock, has an Amihud ratio about fifteen thousand times that of SPY.",
                "incorrectExplanation": "The Amihud ratio separates the BVB from US large caps by several orders of magnitude, unlike daily spread proxies."
            },
            "ro": {
                "title": "Lichiditatea BVB",
                "text": "Comparativ cu marile companii americane, ce spune raportul Amihud despre acțiunile blue-chip BVB (2024-2026)?",
                "options": [
                    "Sunt aproape la fel de lichide",
                    "Sunt de două ori mai nelichide",
                    "Sunt mai lichide",
                    "Cer de mii de ori mai multă mișcare de preț per dolar tranzacționat"
                ],
                "correctExplanation": "Banca Transilvania, cea mai lichidă acțiune BVB, are un raport Amihud de circa cincisprezece mii de ori mai mare decât SPY.",
                "incorrectExplanation": "Raportul Amihud separă BVB de marile companii americane prin mai multe ordine de mărime, spre deosebire de aproximările zilnice ale spread-ului."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Estimating PIN",
                "text": "Maximum-likelihood PIN estimates for very liquid stocks (thousands of trades a day) often pile up at boundary values. The main computational reason is...",
                "options": [
                    "PIN is not identified for any stock",
                    "Informed trading is absent in liquid stocks",
                    "Terms like exp(-eps) eps^B / B! under- or overflow for large B; the likelihood must be factorised and evaluated with log-sum-exp",
                    "Too few trading days in a year"
                ],
                "correctExplanation": "Lin and Ke (2011) show a computing bias: with large daily counts the Poisson terms leave floating-point range; factoring out common terms and working in logs removes it.",
                "incorrectExplanation": "The problem appears only with large counts and is numerical: exp(-1000) is 0 and 1000^1450 is infinite in double precision."
            },
            "ro": {
                "title": "Estimarea PIN",
                "text": "Estimările PIN prin verosimilitate maximă pentru acțiuni foarte lichide (mii de tranzacții pe zi) se adună adesea la valori de frontieră. Motivul numeric principal este...",
                "options": [
                    "PIN nu este identificată pentru nicio acțiune",
                    "Tranzacționarea informată lipsește la acțiunile lichide",
                    "Termeni precum exp(-eps) eps^B / B! depășesc domeniul numeric pentru B mare; verosimilitatea trebuie factorizată și evaluată cu log-sum-exp",
                    "Prea puține zile de tranzacționare într-un an"
                ],
                "correctExplanation": "Lin și Ke (2011) arată o deplasare de calcul: cu numere zilnice mari, termenii Poisson ies din domeniul virgulei mobile; scoaterea factorilor comuni și lucrul în logaritmi o elimină.",
                "incorrectExplanation": "Problema apare doar la numere mari și este numerică: exp(-1000) este 0, iar 1000^1450 este infinit în dublă precizie."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Simultaneity",
                "text": "Regressing log |r| on log relative volume across SPY 5-minute bars gives a slope of about 0.3. Why is this not the causal price-impact elasticity?",
                "options": [
                    "The residuals are heteroskedastic",
                    "The intraday U-shape biases the slope",
                    "Prices are rounded to one tick",
                    "News moves both volume and |r| (simultaneity), and opposite trades in a bar net out"
                ],
                "correctExplanation": "Volume is not exogenous: news raises both trading and price moves, and a bar mixes buyers and sellers, so the slope is not the effect of one trader's net order.",
                "incorrectExplanation": "Heteroskedasticity affects standard errors, not the meaning of the slope; the problem is endogeneity of volume and netting of opposite trades."
            },
            "ro": {
                "title": "Simultaneitatea",
                "text": "Regresia lui log |r| pe log volumul relativ, pe barele SPY de 5 minute, dă o pantă de circa 0,3. De ce nu este aceasta elasticitatea cauzală a impactului?",
                "options": [
                    "Reziduurile sunt heteroscedastice",
                    "Forma de U intrazilnică deplasează panta",
                    "Prețurile sunt rotunjite la un pas de cotare",
                    "Știrile mișcă și volumul, și |r| (simultaneitate), iar tranzacțiile opuse dintr-o bară se anulează"
                ],
                "correctExplanation": "Volumul nu este exogen: știrile cresc atât tranzacționarea, cât și mișcările de preț, iar o bară amestecă cumpărători și vânzători, deci panta nu este efectul ordinului net al unui investitor.",
                "incorrectExplanation": "Heteroscedasticitatea afectează erorile standard, nu sensul pantei; problema este endogenitatea volumului și anularea tranzacțiilor opuse."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Liquidity and the VIX",
                "text": "How does SPY intraday illiquidity relate to the VIX?",
                "options": [
                    "It rises when the VIX rises, almost proportionally",
                    "It falls when the VIX rises",
                    "It is unrelated to the VIX",
                    "It depends only on the day of the week"
                ],
                "correctExplanation": "The elasticity of log illiquidity on log VIX is about 0.95: liquidity disappears when volatility rises.",
                "incorrectExplanation": "Market makers widen quotes and reduce depth when risk rises, so illiquidity and the VIX move together."
            },
            "ro": {
                "title": "Lichiditatea și VIX",
                "text": "Cum este legată ilichiditatea intrazilnică a SPY de VIX?",
                "options": [
                    "Crește când crește VIX, aproape proporțional",
                    "Scade când crește VIX",
                    "Nu are legătură cu VIX",
                    "Depinde doar de ziua săptămânii"
                ],
                "correctExplanation": "Elasticitatea logaritmului ilichidității în raport cu logaritmul VIX este circa 0,95: lichiditatea dispare când volatilitatea crește.",
                "incorrectExplanation": "Formatorii de piață lărgesc cotațiile și reduc adâncimea când riscul crește, deci ilichiditatea și VIX evoluează împreună."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Glosten-Milgrom spread",
                "text": "In Glosten-Milgrom with V_L = 90, V_H = 110, prior 1/2 and share of informed traders mu, what is the spread?",
                "options": [
                    "20",
                    "10 mu",
                    "20 (1 - mu)",
                    "20 mu"
                ],
                "correctExplanation": "At a prior of 1/2 the spread equals mu (V_H - V_L) = 20 mu.",
                "incorrectExplanation": "The spread is proportional to the share of informed traders and to the value difference V_H - V_L."
            },
            "ro": {
                "title": "Spread-ul Glosten-Milgrom",
                "text": "În Glosten-Milgrom cu V_L = 90, V_H = 110, probabilitatea inițială 1/2 și ponderea investitorilor informați mu, care este spread-ul?",
                "options": [
                    "20",
                    "10 mu",
                    "20 (1 - mu)",
                    "20 mu"
                ],
                "correctExplanation": "La o probabilitate inițială de 1/2, spread-ul este mu (V_H - V_L) = 20 mu.",
                "incorrectExplanation": "Spread-ul este proporțional cu ponderea investitorilor informați și cu diferența de valoare V_H - V_L."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Kyle's lambda",
                "text": "In the Kyle model, what is the price impact coefficient lambda?",
                "options": [
                    "sigma_u / sigma_v",
                    "sigma_v sigma_u / 2",
                    "sigma_v / (2 sigma_u)",
                    "2 sigma_u / sigma_v"
                ],
                "correctExplanation": "lambda = sigma_v / (2 sigma_u): more noise trading makes the market deeper.",
                "incorrectExplanation": "sigma_u / sigma_v is the insider's intensity beta and sigma_v sigma_u / 2 is the insider's expected profit."
            },
            "ro": {
                "title": "Lambda lui Kyle",
                "text": "În modelul Kyle, care este coeficientul de impact lambda?",
                "options": [
                    "sigma_u / sigma_v",
                    "sigma_v sigma_u / 2",
                    "sigma_v / (2 sigma_u)",
                    "2 sigma_u / sigma_v"
                ],
                "correctExplanation": "lambda = sigma_v / (2 sigma_u): mai mult zgomot face piața mai adâncă.",
                "incorrectExplanation": "sigma_u / sigma_v este intensitatea beta a investitorului din interior, iar sigma_v sigma_u / 2 este profitul său așteptat."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Information in the Kyle price",
                "text": "In the one-period Kyle equilibrium, how much of the insider's information is revealed by the price?",
                "options": [
                    "Exactly half: Var(v | p) = sigma_v^2 / 2",
                    "All of it",
                    "None of it",
                    "A quarter"
                ],
                "correctExplanation": "The posterior variance is half of the prior variance: the price reveals half of the private information.",
                "incorrectExplanation": "The insider trades so that the market maker learns exactly half of the variance of the value."
            },
            "ro": {
                "title": "Informația din prețul Kyle",
                "text": "În echilibrul Kyle cu o singură perioadă, cât din informația investitorului din interior este dezvăluită de preț?",
                "options": [
                    "Exact jumătate: Var(v | p) = sigma_v^2 / 2",
                    "Toată",
                    "Nimic",
                    "Un sfert"
                ],
                "correctExplanation": "Dispersia a posteriori este jumătate din dispersia a priori: prețul dezvăluie jumătate din informația privată.",
                "incorrectExplanation": "Investitorul din interior tranzacționează astfel încât formatorul de piață află exact jumătate din dispersia valorii."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Square-root law",
                "text": "According to the square-root law, if a metaorder is four times larger, how does its price impact change?",
                "options": [
                    "It is four times larger",
                    "It is sixteen times larger",
                    "It does not change",
                    "It is about twice as large"
                ],
                "correctExplanation": "Impact grows with the square root of size: sqrt(4) = 2.",
                "incorrectExplanation": "The law is concave: Delta P is proportional to sqrt(Q / V), not to Q."
            },
            "ro": {
                "title": "Legea rădăcinii pătrate",
                "text": "Conform legii rădăcinii pătrate, dacă un metaordin este de patru ori mai mare, cum se schimbă impactul său?",
                "options": [
                    "Este de patru ori mai mare",
                    "Este de șaisprezece ori mai mare",
                    "Nu se schimbă",
                    "Este de circa două ori mai mare"
                ],
                "correctExplanation": "Impactul crește cu rădăcina pătrată a mărimii: sqrt(4) = 2.",
                "incorrectExplanation": "Legea este concavă: Delta P este proporțional cu sqrt(Q / V), nu cu Q."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Almgren-Chriss",
                "text": "In Almgren-Chriss, what does a risk-neutral trader (lambda = 0) do?",
                "options": [
                    "Sells everything at the start",
                    "Sells the same amount in each period",
                    "Sells everything at the end",
                    "Waits for a better price"
                ],
                "correctExplanation": "With lambda = 0, kappa = 0 and holdings fall linearly: the time-weighted schedule.",
                "incorrectExplanation": "Only price risk pushes trading forward; without risk aversion, spreading the order evenly minimises the temporary impact."
            },
            "ro": {
                "title": "Almgren-Chriss",
                "text": "În Almgren-Chriss, ce face un investitor neutru la risc (lambda = 0)?",
                "options": [
                    "Vinde totul la început",
                    "Vinde aceeași cantitate în fiecare perioadă",
                    "Vinde totul la sfârșit",
                    "Așteaptă un preț mai bun"
                ],
                "correctExplanation": "Cu lambda = 0, kappa = 0 și deținerea scade liniar: programul ponderat în timp.",
                "incorrectExplanation": "Doar riscul de preț împinge tranzacționarea spre început; fără aversiune la risc, împărțirea uniformă a ordinului minimizează impactul temporar."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Execution trade-off",
                "text": "Why does a more risk-averse trader front-load a liquidation?",
                "options": [
                    "To lower the expected impact cost",
                    "Because permanent impact disappears",
                    "To reduce the variance of the cost from future price moves",
                    "Because spreads are narrower early"
                ],
                "correctExplanation": "Selling early cuts exposure to price risk, at the cost of higher temporary impact.",
                "incorrectExplanation": "Front-loading raises the expected impact cost; it is chosen to reduce the variance of the implementation cost."
            },
            "ro": {
                "title": "Compromisul execuției",
                "text": "De ce un investitor cu aversiune mai mare la risc vinde mai mult la începutul lichidării?",
                "options": [
                    "Pentru a reduce costul așteptat al impactului",
                    "Pentru că impactul permanent dispare",
                    "Pentru a reduce dispersia costului provocată de mișcările viitoare ale prețului",
                    "Pentru că spread-urile sunt mai înguste la început"
                ],
                "correctExplanation": "Vânzarea timpurie reduce expunerea la riscul de preț, cu prețul unui impact temporar mai mare.",
                "incorrectExplanation": "Vânzarea timpurie crește costul așteptat al impactului; este aleasă pentru a reduce dispersia costului de implementare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Avellaneda-Stoikov inventory",
                "text": "An Avellaneda-Stoikov market maker is long inventory (q > 0). Her reservation price r = s - q gamma sigma^2 (T - t) is...",
                "options": [
                    "above the mid-price, so she raises both quotes",
                    "below the mid-price, so she skews both quotes down to sell",
                    "equal to the mid-price, since the spread is symmetric",
                    "independent of volatility sigma"
                ],
                "correctExplanation": "With q > 0, r < s: holding more of the risky asset lowers its value to her, so both quotes shift down to attract buyers and deter sellers.",
                "incorrectExplanation": "The inventory term q gamma sigma^2 (T - t) is subtracted from the mid-price and grows with volatility and the time left."
            },
            "ro": {
                "title": "Stocul în Avellaneda-Stoikov",
                "text": "Un formator de piață Avellaneda-Stoikov are stoc pozitiv (q > 0). Prețul său de rezervă r = s - q gamma sigma^2 (T - t) este...",
                "options": [
                    "peste prețul de mijloc, deci ridică ambele cotații",
                    "sub prețul de mijloc, deci coboară ambele cotații ca să vândă",
                    "egal cu prețul de mijloc, fiindcă spread-ul este simetric",
                    "independent de volatilitatea sigma"
                ],
                "correctExplanation": "Cu q > 0, r < s: deținerea a mai mult activ riscant îi scade valoarea pentru ea, deci ambele cotații coboară, ca să atragă cumpărători și să descurajeze vânzătorii.",
                "incorrectExplanation": "Termenul de stoc q gamma sigma^2 (T - t) se scade din prețul de mijloc și crește cu volatilitatea și cu timpul rămas."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Roll in small samples",
                "text": "For SPY 5-minute bars (77 returns a day) the within-day Roll covariance is positive on about 41% of days. Under the Roll model with a one-tick spread, a Monte Carlo gives about 45% (95% band 43% to 48%). What follows?",
                "options": [
                    "The Roll model is rejected, since a true bounce gives negative covariances",
                    "The market is inefficient on 41% of days",
                    "Positive days alone are not evidence against Roll: with c/sigma near 0.01 they occur almost half the time; the observed share is even below the band, i.e. more negative autocorrelation than a one-tick bounce",
                    "The spread of SPY is about 41% of a tick"
                ],
                "correctExplanation": "Harris (1990): when c^2 is small relative to sigma^2 / sqrt(T), P(Cov-hat > 0) is close to one half even if the model holds. The observed 41% lies below the one-tick band, so the data are more, not less, negatively autocorrelated than a one-tick bounce.",
                "incorrectExplanation": "Compare the observed share with the sampling distribution under the null: a tiny bounce relative to volatility gives little power in 77 observations."
            },
            "ro": {
                "title": "Roll în eșantioane mici",
                "text": "Pentru barele SPY de 5 minute (77 de randamente pe zi), covarianța Roll din cursul zilei este pozitivă în circa 41% din zile. Sub modelul Roll cu un spread de un pas, o simulare Monte Carlo dă circa 45% (banda 95%: între 43% și 48%). Ce rezultă?",
                "options": [
                    "Modelul Roll este respins, fiindcă o oscilație adevărată dă covarianțe negative",
                    "Piața este ineficientă în 41% din zile",
                    "Zilele pozitive nu sunt, singure, o dovadă împotriva Roll: cu c/sigma aproape de 0,01, apar în aproape jumătate din zile; ponderea observată este chiar sub bandă, adică o autocorelație mai negativă decât o oscilație de un pas",
                    "Spread-ul SPY este circa 41% dintr-un pas"
                ],
                "correctExplanation": "Harris (1990): când c^2 este mic față de sigma^2 / sqrt(T), P(Cov-estimat > 0) este aproape de o jumătate chiar dacă modelul este adevărat. Cei 41% observați sunt sub banda pentru un pas, deci datele sunt mai negativ autocorelate, nu mai puțin, decât o oscilație de un pas.",
                "incorrectExplanation": "Comparați ponderea observată cu distribuția de selecție sub ipoteza nulă: o oscilație minusculă față de volatilitate dă putere mică în 77 de observații."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Illiquidity shocks",
                "text": "In the seminar, how do monthly market returns react to an unexpected rise in market illiquidity?",
                "options": [
                    "They rise, on all three markets",
                    "They fall, on the BVB, in the US and in crypto",
                    "They fall only in the US",
                    "They do not react"
                ],
                "correctExplanation": "The coefficient of the illiquidity shock is negative with t-statistics near -4 on all three markets, as Amihud (2002) predicts.",
                "incorrectExplanation": "An unexpected rise in illiquidity raises required returns, so current prices fall on each of the three markets."
            },
            "ro": {
                "title": "Șocurile de ilichiditate",
                "text": "La seminar, cum reacționează randamentele lunare ale pieței la o creștere neașteptată a ilichidității?",
                "options": [
                    "Cresc, pe toate cele trei piețe",
                    "Scad, pe BVB, în SUA și pe piața cripto",
                    "Scad doar în SUA",
                    "Nu reacționează"
                ],
                "correctExplanation": "Coeficientul șocului de ilichiditate este negativ, cu statistici t apropiate de -4 pe toate cele trei piețe, cum prezice Amihud (2002).",
                "incorrectExplanation": "O creștere neașteptată a ilichidității crește randamentele cerute, deci prețurile curente scad pe fiecare dintre cele trei piețe."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the AI error: the Roll estimator",
                "text": "An AI assistant writes: \"The Roll spread is s = 2 sqrt(-Cov(dp_t, dp_{t-1})). For this stock the autocovariance of price changes is positive, so use s = 2 sqrt(|Cov|) instead.\" What is wrong?",
                "options": [
                    "The factor should be 1, not 2",
                    "The Roll estimator uses the variance of price changes, not their autocovariance",
                    "The autocovariance should be computed from prices, not price changes",
                    "A positive sample autocovariance makes the unmodified Roll estimator undefined over the real numbers, although it can arise through sampling error; report it as missing or use another estimator, such as a high-low one"
                ],
                "correctExplanation": "The Roll model implies a negative population autocovariance, -c^2. A sample value can still be positive, through sampling error or departures from the model (trends, stale prices); either way the square root is undefined, and taking the absolute value produces a spread with no basis in the model (Roll, 1984; Hasbrouck, 2007).",
                "incorrectExplanation": "The formula s = 2 sqrt(-Cov) is right; the error is forcing a positive autocovariance into it with an absolute value."
            },
            "ro": {
                "title": "Găsiți eroarea AI: estimatorul Roll",
                "text": "Un asistent AI scrie: „Spread-ul Roll este s = 2 sqrt(-Cov(dp_t, dp_{t-1})). Pentru această acțiune autocovarianța variațiilor de preț este pozitivă, deci folosiți în schimb s = 2 sqrt(|Cov|).” Ce este greșit?",
                "options": [
                    "Factorul ar trebui să fie 1, nu 2",
                    "Estimatorul Roll folosește varianța variațiilor de preț, nu autocovarianța lor",
                    "Autocovarianța ar trebui calculată din prețuri, nu din variațiile lor",
                    "O autocovarianță de selecție pozitivă face ca estimatorul Roll nemodificat să nu fie definit în numere reale, deși poate apărea din eroarea de selecție; raportați-l ca lipsă sau folosiți alt estimator, de exemplu unul maxim-minim"
                ],
                "correctExplanation": "Modelul Roll implică o autocovarianță negativă în populație, -c^2. O valoare de selecție poate fi totuși pozitivă, din eroarea de selecție sau din abateri de la model (tendințe, prețuri învechite); în ambele cazuri rădăcina nu este definită, iar valoarea absolută produce un spread fără nicio bază în model (Roll, 1984; Hasbrouck, 2007).",
                "incorrectExplanation": "Formula s = 2 sqrt(-Cov) este corectă; greșeala este forțarea unei autocovarianțe pozitive în formulă prin valoarea absolută."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: the Amihud ratio",
                "text": "An AI assistant writes: \"The Amihud illiquidity of a stock is the average over days of |r_d| divided by the number of shares traded on day d.\" What is wrong?",
                "options": [
                    "The numerator should be the squared return, not the absolute return",
                    "The denominator must be the traded value (price times shares, in money), not the number of shares",
                    "The ratio should be a median, not an average",
                    "Amihud uses intraday returns, not daily returns"
                ],
                "correctExplanation": "Amihud (2002) defines ILLIQ as the average of |r_d| / DVOL_d, with DVOL_d the traded value in currency. With the number of shares, the ratio depends on the price level, jumps at a stock split and cannot be compared across stocks.",
                "incorrectExplanation": "The absolute daily return and the average over days are right; the denominator must be measured in money, not in shares."
            },
            "ro": {
                "title": "Găsiți eroarea AI: raportul Amihud",
                "text": "Un asistent AI scrie: „Ilichiditatea Amihud a unei acțiuni este media pe zile a lui |r_d| împărțit la numărul de acțiuni tranzacționate în ziua d.” Ce este greșit?",
                "options": [
                    "Numărătorul ar trebui să fie pătratul randamentului, nu randamentul absolut",
                    "Numitorul trebuie să fie valoarea tranzacționată (preț ori număr de acțiuni, în bani), nu numărul de acțiuni",
                    "Raportul ar trebui să fie o mediană, nu o medie",
                    "Amihud folosește randamente intraday, nu randamente zilnice"
                ],
                "correctExplanation": "Amihud (2002) definește ILLIQ ca media lui |r_d| / DVOL_d, cu DVOL_d valoarea tranzacționată în monedă. Cu numărul de acțiuni, raportul depinde de nivelul prețului, face un salt la o divizare a acțiunilor și nu poate fi comparat între acțiuni.",
                "incorrectExplanation": "Randamentul zilnic absolut și media pe zile sunt corecte; numitorul trebuie măsurat în bani, nu în număr de acțiuni."
            }
        }
    ]
};

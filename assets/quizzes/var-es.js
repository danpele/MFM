// ============================================================
// Quiz bank for chapter id 'var-es': Value-at-Risk and Expected Shortfall (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['var-es'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "Sampling variance of historical VaR",
                "text": "For i.i.d. losses with density f, what is the asymptotic variance of the historical VaR_alpha estimator computed from n observations?",
                "options": [
                    "sigma^2 / n, the variance of the sample mean",
                    "alpha / n, from the binomial count of tail observations",
                    "alpha(1 - alpha) / (n f(VaR_alpha)^2)",
                    "alpha(1 - alpha) / n, the variance of the empirical hit rate"
                ],
                "correctExplanation": "The empirical quantile is asymptotically Normal with variance alpha(1 - alpha)/(n f(q)^2): the hit-rate variance alpha(1 - alpha)/n is converted into a quantile variance by the density at the quantile, which is small in the tail.",
                "incorrectExplanation": "The binomial variance alpha(1 - alpha)/n describes the share of days beyond VaR, not VaR itself; it must be divided by the squared density at the quantile, and the variance of the mean plays no role here."
            },
            "ro": {
                "title": "Dispersia de selecție a VaR istoric",
                "text": "Pentru pierderi i.i.d. cu densitatea f, care este dispersia asimptotică a estimatorului istoric al VaR_alpha calculat din n observații?",
                "options": [
                    "sigma^2 / n, dispersia mediei de selecție",
                    "alpha / n, din numărul binomial de observații din coadă",
                    "alpha(1 - alpha) / (n f(VaR_alpha)^2)",
                    "alpha(1 - alpha) / n, dispersia ratei empirice de depășire"
                ],
                "correctExplanation": "Cuantila empirică este asimptotic Normală cu dispersia alpha(1 - alpha)/(n f(q)^2): dispersia ratei de depășire alpha(1 - alpha)/n se transformă în dispersia cuantilei prin densitatea din cuantilă, mică în coadă.",
                "incorrectExplanation": "Dispersia binomială alpha(1 - alpha)/n descrie proporția zilelor de dincolo de VaR, nu VaR însuși; trebuie împărțită la pătratul densității din cuantilă, iar dispersia mediei nu joacă niciun rol aici."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Rockafellar-Uryasev representation",
                "text": "Which identity holds for any integrable loss L and tail probability alpha?",
                "options": [
                    "ES_alpha(L) = min over v of { v + E[(L - v)+] / alpha }, attained at v = VaR_alpha",
                    "ES_alpha(L) = VaR_alpha(L) + sd(L)",
                    "ES_alpha(L) = E[L | L > VaR_alpha(L)] for every discrete L",
                    "ES_alpha(L) = max over v of { v + E[(L - v)+] / alpha }"
                ],
                "correctExplanation": "The objective v + E[(L - v)+]/alpha is convex in v, with right derivative 1 - P(L > v)/alpha and left derivative 1 - P(L >= v)/alpha; v minimises it when P(L > v) <= alpha <= P(L >= v), which holds at VaR_alpha (an ordinary zero derivative only for continuous L). The minimum value is ES_alpha, also when L has atoms.",
                "incorrectExplanation": "The representation is a minimum, not a maximum (the objective is convex and unbounded above); the conditional mean beyond VaR fails when the distribution has atoms, and no volatility add-on is involved."
            },
            "ro": {
                "title": "Reprezentarea Rockafellar-Uryasev",
                "text": "Ce identitate este adevărată pentru orice pierdere integrabilă L și orice probabilitate a cozii alpha?",
                "options": [
                    "ES_alpha(L) = minimul după v al { v + E[(L - v)+] / alpha }, atins în v = VaR_alpha",
                    "ES_alpha(L) = VaR_alpha(L) + abaterea standard a lui L",
                    "ES_alpha(L) = E[L | L > VaR_alpha(L)] pentru orice L discret",
                    "ES_alpha(L) = maximul după v al { v + E[(L - v)+] / alpha }"
                ],
                "correctExplanation": "Funcția obiectiv v + E[(L - v)+]/alpha este convexă în v, cu derivata la dreapta 1 - P(L > v)/alpha și derivata la stînga 1 - P(L >= v)/alpha; v o minimizează cînd P(L > v) <= alpha <= P(L >= v), condiție îndeplinită în VaR_alpha (derivată obișnuită nulă doar pentru L continuă). Valoarea minimă este ES_alpha, inclusiv cînd L are atomi.",
                "incorrectExplanation": "Reprezentarea este un minim, nu un maxim (funcția obiectiv este convexă și nemărginită superior); media condiționată dincolo de VaR eșuează cînd distribuția are atomi, iar nu apare niciun adaos de volatilitate."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Precision of historical ES",
                "text": "At a fixed alpha = 2.5%, doubling the sample size n reduces the standard error of historical ES by about which factor?",
                "options": [
                    "2, because the variance falls with n^2",
                    "None, because ES depends only on the tail",
                    "The square root of 2.5",
                    "The square root of 2, because the number of tail observations n alpha doubles"
                ],
                "correctExplanation": "The asymptotic variance of historical ES is Var((L - VaR)+)/(n alpha^2), so the standard error falls like 1/sqrt(n alpha): doubling n doubles the tail count and divides the standard error by sqrt(2).",
                "incorrectExplanation": "Standard errors of smooth estimators fall with the square root of the sample size; for ES the relevant count is the n alpha tail observations, which grows linearly with n."
            },
            "ro": {
                "title": "Precizia ES istoric",
                "text": "La alpha = 2,5% fix, dublarea mărimii eșantionului n reduce eroarea standard a ES istoric cu aproximativ ce factor?",
                "options": [
                    "2, pentru că dispersia scade cu n^2",
                    "Deloc, pentru că ES depinde doar de coadă",
                    "Radical din 2,5",
                    "Radical din 2, pentru că numărul de observații din coadă n alpha se dublează"
                ],
                "correctExplanation": "Dispersia asimptotică a ES istoric este Var((L - VaR)+)/(n alpha^2), deci eroarea standard scade ca 1/sqrt(n alpha): dublarea lui n dublează numărul de observații din coadă și împarte eroarea standard la sqrt(2).",
                "incorrectExplanation": "Erorile standard ale estimatorilor netezi scad cu radicalul mărimii eșantionului; pentru ES numărul relevant este cel al celor n alpha observații din coadă, care crește liniar cu n."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Two bonds",
                "text": "Two independent bonds each lose 100 with probability 0.9%. What is the VaR 1% of each bond alone and of the portfolio of both?",
                "options": [
                    "100 and 100",
                    "0 and 0",
                    "100 and 200",
                    "0 and 100"
                ],
                "correctExplanation": "Alone, the default probability 0.9% is below 1%, so VaR is 0; together, the chance of at least one default is 1.79% above 1%, so VaR is 100.",
                "incorrectExplanation": "P(X <= -100) is 0.9% for one bond, not above 1%, but 1.79% for the pair, so the portfolio VaR jumps to 100 while each stand-alone VaR is 0."
            },
            "ro": {
                "title": "Două obligațiuni",
                "text": "Două obligațiuni independente pierd fiecare 100 cu probabilitatea 0,9%. Care este VaR 1% al fiecărei obligațiuni singure și al portofoliului ambelor?",
                "options": [
                    "100 și 100",
                    "0 și 0",
                    "100 și 200",
                    "0 și 100"
                ],
                "correctExplanation": "Singură, probabilitatea de neplată 0,9% este sub 1%, deci VaR este 0; împreună, șansa a cel puțin unei neplăți este 1,79%, peste 1%, deci VaR este 100.",
                "incorrectExplanation": "P(X <= -100) este 0,9% pentru o obligațiune, nu peste 1%, dar 1,79% pentru pereche, deci VaR al portofoliului sare la 100, iar fiecare VaR individual este 0."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Extremal index",
                "text": "Daily losses cluster, with extremal index theta = 0.5. How should the approximation P(monthly maximum <= x) ~ F(x)^n be corrected?",
                "options": [
                    "It is exact, because the monthly maximum does not depend on clustering",
                    "Replace F(x)^n by F(x)^(n theta); ignoring theta biases the implied daily VaR downward",
                    "Replace F(x)^n by F(x)^(n / theta)",
                    "Keep F(x)^n: theta changes only the shape parameter xi"
                ],
                "correctExplanation": "Under clustering P(M_n <= u_n) tends to exp(-theta tau): the n days behave like n theta independent days. Using F^n instead of F^(n theta) makes the implied daily quantile too low.",
                "incorrectExplanation": "Clustering reduces the effective number of independent days to n theta, which is smaller than n; the shape parameter is unchanged, but the mapping from block maxima to daily quantiles is not."
            },
            "ro": {
                "title": "Indicele extremal",
                "text": "Pierderile zilnice sînt grupate, cu indicele extremal theta = 0,5. Cum trebuie corectată aproximarea P(maximul lunar <= x) ~ F(x)^n?",
                "options": [
                    "Este exactă, pentru că maximul lunar nu depinde de grupare",
                    "Înlocuim F(x)^n cu F(x)^(n theta); ignorarea lui theta deplasează în jos VaR-ul zilnic implicat",
                    "Înlocuim F(x)^n cu F(x)^(n / theta)",
                    "Păstrăm F(x)^n: theta schimbă doar parametrul de formă xi"
                ],
                "correctExplanation": "Cu grupare, P(M_n <= u_n) tinde la exp(-theta tau): cele n zile se comportă ca n theta zile independente. Folosirea lui F^n în loc de F^(n theta) dă o cuantilă zilnică implicată prea mică.",
                "incorrectExplanation": "Gruparea reduce numărul efectiv de zile independente la n theta, mai mic decît n; parametrul de formă nu se schimbă, dar legătura dintre maximele pe blocuri și cuantilele zilnice da."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Heavy tails",
                "text": "For S&P 500 daily losses 2000-2026 the historical VaR 1% is 3.45% and the Normal VaR 1% is 2.80%. Why?",
                "options": [
                    "The sample mean is too large",
                    "The Normal distribution overestimates the tail",
                    "Daily losses have heavier tails than the Normal distribution",
                    "Historical simulation always overestimates VaR"
                ],
                "correctExplanation": "Excess kurtosis above 10 puts more probability far from the centre than the Normal distribution allows, so the empirical quantile is higher.",
                "incorrectExplanation": "The gap comes from heavy tails: the Normal distribution with the same standard deviation is too thin in the tail."
            },
            "ro": {
                "title": "Cozi grele",
                "text": "Pentru pierderile zilnice S&P 500 2000-2026, VaR 1% istoric este 3,45%, iar VaR 1% Normal este 2,80%. De ce?",
                "options": [
                    "Media de selecție este prea mare",
                    "Distribuția Normală supraestimează coada",
                    "Pierderile zilnice au cozi mai grele decît distribuția Normală",
                    "Simularea istorică supraestimează mereu VaR"
                ],
                "correctExplanation": "Un exces de aplatizare peste 10 pune mai multă probabilitate departe de centru decît permite distribuția Normală, deci cuantila empirică este mai mare.",
                "incorrectExplanation": "Diferența vine din cozile grele: distribuția Normală cu aceeași abatere standard este prea subțire în coadă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Cornish-Fisher",
                "text": "When does the Cornish-Fisher expansion give unreliable VaR estimates?",
                "options": [
                    "When skewness and excess kurtosis are large, as for daily returns with kurtosis near 10",
                    "When the distribution is exactly Normal",
                    "When the sample is very long",
                    "When the tail probability is 10%"
                ],
                "correctExplanation": "The expansion corrects the Normal quantile around small departures; with kurtosis near 10 the kurtosis term overshoots, e.g. 6.08% vs 3.45% for the S&P 500.",
                "incorrectExplanation": "Cornish-Fisher is exact for the Normal distribution and works for mild departures; large skewness and kurtosis break it."
            },
            "ro": {
                "title": "Cornish-Fisher",
                "text": "Cînd dă dezvoltarea Cornish-Fisher estimări VaR nesigure?",
                "options": [
                    "Cînd asimetria și excesul de aplatizare sînt mari, ca la randamentele zilnice cu aplatizare în jur de 10",
                    "Cînd distribuția este exact Normală",
                    "Cînd selecția este foarte lungă",
                    "Cînd probabilitatea cozii este 10%"
                ],
                "correctExplanation": "Dezvoltarea corectează cuantila Normală pentru abateri mici; cu o aplatizare în jur de 10, termenul de aplatizare depășește ținta, de ex. 6,08% față de 3,45% pentru S&P 500.",
                "incorrectExplanation": "Cornish-Fisher este exactă pentru distribuția Normală și funcționează pentru abateri mici; asimetria și aplatizarea mari o fac nesigură."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Robustness of risk estimators",
                "text": "In the sense of Cont, Deguest and Scandolo (2010), which historical risk estimator is qualitatively robust?",
                "options": [
                    "Historical VaR; historical ES is not",
                    "Historical ES only, because ES is coherent",
                    "Both, because both are computed from the empirical distribution",
                    "Neither, because both depend on the tail"
                ],
                "correctExplanation": "A small change in the data distribution changes historical VaR only a little, but a single extreme loss can move historical ES arbitrarily: coherence and robustness pull in opposite directions.",
                "incorrectExplanation": "Coherence and robustness are different properties: ES is coherent but reacts without bound to one extreme observation, whereas a quantile is insensitive to how far the extreme observations lie."
            },
            "ro": {
                "title": "Robustețea estimatorilor de risc",
                "text": "În sensul lui Cont, Deguest și Scandolo (2010), care estimator istoric al riscului este calitativ robust?",
                "options": [
                    "VaR istoric; ES istoric nu este",
                    "Doar ES istoric, pentru că ES este coerent",
                    "Amîndoi, pentru că ambii se calculează din distribuția empirică",
                    "Niciunul, pentru că ambii depind de coadă"
                ],
                "correctExplanation": "O mică schimbare a distribuției datelor schimbă puțin VaR istoric, dar o singură pierdere extremă poate muta arbitrar ES istoric: coerența și robustețea trag în direcții opuse.",
                "incorrectExplanation": "Coerența și robustețea sînt proprietăți diferite: ES este coerent, dar reacționează nemărginit la o singură observație extremă, în timp ce o cuantilă nu depinde de cît de departe se află observațiile extreme."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Estimation risk in FHS VaR",
                "text": "A 90% confidence interval for tomorrow's VaR 1% from filtered historical simulation must account for the sampling error of what?",
                "options": [
                    "Only the empirical quantile of the standardised residuals",
                    "Only the volatility forecast sigma_{t+1}",
                    "Both the GARCH parameter estimates (through sigma_{t+1}) and the empirical residual quantile",
                    "Nothing: a forecast is not an estimate"
                ],
                "correctExplanation": "The FHS VaR is -mu_{t+1} + sigma_{t+1} times a residual quantile; both factors are estimated, so a residual bootstrap that re-estimates the GARCH model on every path captures both sources.",
                "incorrectExplanation": "The volatility forecast depends on estimated GARCH parameters and the residual quantile on a finite sample of residuals; ignoring either source gives intervals that are too narrow."
            },
            "ro": {
                "title": "Riscul de estimare în VaR FHS",
                "text": "Un interval de încredere de 90% pentru VaR 1% de mîine din simularea istorică filtrată trebuie să includă eroarea de selecție a cui?",
                "options": [
                    "Doar a cuantilei empirice a reziduurilor standardizate",
                    "Doar a prognozei volatilității sigma_{t+1}",
                    "Atît a parametrilor GARCH estimați (prin sigma_{t+1}), cît și a cuantilei empirice a reziduurilor",
                    "Nicio eroare de selecție: o prognoză nu este o estimare"
                ],
                "correctExplanation": "VaR FHS este -mu_{t+1} + sigma_{t+1} înmulțit cu o cuantilă a reziduurilor; ambii factori sînt estimați, deci un bootstrap pe reziduuri care re-estimează modelul GARCH pe fiecare traiectorie surprinde ambele surse.",
                "incorrectExplanation": "Prognoza volatilității depinde de parametrii GARCH estimați, iar cuantila reziduurilor de un eșantion finit; ignorarea oricăreia dintre surse dă intervale prea înguste."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Exceedance clustering",
                "text": "Historical-simulation VaR exceedances for the S&P 500 come in clusters (2008, 2020). What does this reveal?",
                "options": [
                    "The tail probability is too high",
                    "The Normal distribution is correct",
                    "The risk measure does not adapt to volatility clustering",
                    "The data contain errors"
                ],
                "correctExplanation": "A good daily VaR forecast produces exceedances spread over time; clusters show that the window reacts too late to volatility shocks.",
                "incorrectExplanation": "Clustered exceedances are the signature of an unconditional measure in a market with volatility clustering."
            },
            "ro": {
                "title": "Gruparea depășirilor",
                "text": "Depășirile VaR istoric pentru S&P 500 vin în grupuri (2008, 2020). Ce arată acest lucru?",
                "options": [
                    "Probabilitatea cozii este prea mare",
                    "Distribuția Normală este corectă",
                    "Măsura de risc nu se adaptează la gruparea volatilității",
                    "Datele conțin erori"
                ],
                "correctExplanation": "O prognoză VaR zilnică bună produce depășiri împrăștiate în timp; grupurile arată că fereastra reacționează prea tîrziu la șocurile de volatilitate.",
                "incorrectExplanation": "Depășirile grupate sînt tipice pentru o măsură necondiționată pe o piață cu grupare a volatilității."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Estimating CAViaR",
                "text": "How are the parameters of a CAViaR model for the alpha-quantile q_t of returns r_t estimated?",
                "options": [
                    "By least squares on the returns",
                    "By Gaussian maximum likelihood",
                    "By minimising the number of exceedances",
                    "By minimising the pinball (tick) loss, the sum of (alpha - 1{r_t < q_t})(r_t - q_t)"
                ],
                "correctExplanation": "CAViaR is a quantile regression: the true conditional quantile minimises the expected pinball loss, so no distributional assumption is needed.",
                "incorrectExplanation": "Least squares and the Gaussian likelihood target the mean and the variance, not a quantile; the number of exceedances is a step function with many minimisers and ignores how far returns fall beyond the quantile."
            },
            "ro": {
                "title": "Estimarea CAViaR",
                "text": "Cum se estimează parametrii unui model CAViaR pentru cuantila alpha q_t a randamentelor r_t?",
                "options": [
                    "Prin cele mai mici pătrate pe randamente",
                    "Prin verosimilitate maximă Gaussiană",
                    "Prin minimizarea numărului de depășiri",
                    "Prin minimizarea pierderii pinball (tick), suma lui (alpha - 1{r_t < q_t})(r_t - q_t)"
                ],
                "correctExplanation": "CAViaR este o regresie cuantilă: adevărata cuantilă condiționată minimizează pierderea pinball așteptată, deci nu este nevoie de nicio ipoteză de distribuție.",
                "incorrectExplanation": "Cele mai mici pătrate și verosimilitatea Gaussiană vizează media și dispersia, nu o cuantilă; numărul de depășiri este o funcție în trepte cu multe puncte de minim și ignoră cît de departe cad randamentele dincolo de cuantilă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "BET horizon",
                "text": "For BET the empirical 10-day VaR 1% is 1.22 times sqrt(10) times the one-day VaR. What explains it?",
                "options": [
                    "Negative autocorrelation",
                    "The Normal distribution",
                    "A falling volatility trend",
                    "Positive autocorrelation of daily returns (lag-1 autocorrelation 0.109)"
                ],
                "correctExplanation": "Positive autocorrelation raises the variance of multi-day sums above h sigma^2 (variance ratio above 1), so sqrt(h) underestimates.",
                "incorrectExplanation": "The key is persistence: positively autocorrelated returns accumulate, making the multi-day tail wider than sqrt(h) suggests."
            },
            "ro": {
                "title": "Orizontul BET",
                "text": "Pentru BET, VaR 1% empiric pe 10 zile este de 1,22 ori radical(10) înmulțit cu VaR pe o zi. Ce explică acest lucru?",
                "options": [
                    "Autocorelația negativă",
                    "Distribuția Normală",
                    "O tendință descrescătoare a volatilității",
                    "Autocorelația pozitivă a randamentelor zilnice (autocorelația de ordin 1 egală cu 0,109)"
                ],
                "correctExplanation": "Autocorelația pozitivă ridică dispersia sumelor pe mai multe zile peste h sigma^2 (raportul dispersiilor peste 1), deci radical(h) subestimează.",
                "incorrectExplanation": "Cheia este persistența: randamentele autocorelate pozitiv se acumulează, iar coada pe mai multe zile devine mai largă decît sugerează radical(h)."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Euler allocation",
                "text": "Why do component VaRs C_i = w_i dVaR/dw_i add up exactly to the portfolio VaR?",
                "options": [
                    "Because correlations are zero",
                    "Because VaR is positively homogeneous of degree one in the weights (Euler's theorem)",
                    "Because returns are Normal",
                    "Because weights sum to one"
                ],
                "correctExplanation": "For a function homogeneous of degree one, sum_i w_i dRho/dw_i = Rho; this holds for VaR and ES.",
                "incorrectExplanation": "The additivity follows from homogeneity through Euler's theorem, not from zero correlations or weight normalisation."
            },
            "ro": {
                "title": "Alocarea Euler",
                "text": "De ce componentele VaR C_i = w_i dVaR/dw_i se adună exact la VaR-ul portofoliului?",
                "options": [
                    "Pentru că corelațiile sînt zero",
                    "Pentru că VaR este pozitiv omogen de grad unu în ponderi (teorema lui Euler)",
                    "Pentru că randamentele sînt Normale",
                    "Pentru că ponderile însumează unu"
                ],
                "correctExplanation": "Pentru o funcție omogenă de grad unu, suma_i w_i dRho/dw_i = Rho; acest lucru este valabil pentru VaR și ES.",
                "incorrectExplanation": "Aditivitatea decurge din omogenitate prin teorema lui Euler, nu din corelații nule sau din normarea ponderilor."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Risk contributions",
                "text": "In the 40/30/20/10 portfolio of SPY, TLT, GLD and Bitcoin, Bitcoin has a 10% weight. Its share of the Normal VaR 1% is closest to:",
                "options": [
                    "10%",
                    "20%",
                    "38%",
                    "60%"
                ],
                "correctExplanation": "Bitcoin's daily volatility is almost four times that of SPY and it is positively correlated with equities, so 10% of the money carries about 38% of VaR.",
                "incorrectExplanation": "Risk shares depend on volatility and correlation, not on money weights: the small crypto position contributes more than a third of the risk."
            },
            "ro": {
                "title": "Contribuții la risc",
                "text": "În portofoliul 40/30/20/10 din SPY, TLT, GLD și Bitcoin, Bitcoin are ponderea de 10%. Cota lui din VaR 1% Normal este cea mai apropiată de:",
                "options": [
                    "10%",
                    "20%",
                    "38%",
                    "60%"
                ],
                "correctExplanation": "Volatilitatea zilnică a Bitcoin este de aproape patru ori cea a SPY și este corelat pozitiv cu acțiunile, deci 10% din bani generează aproximativ 38% din VaR.",
                "incorrectExplanation": "Cotele de risc depind de volatilitate și corelație, nu de ponderile în bani: poziția cripto mică contribuie cu peste o treime din risc."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Fisher-Tippett-Gnedenko",
                "text": "What does the Fisher-Tippett-Gnedenko theorem state?",
                "options": [
                    "Excesses over a high threshold follow a GPD",
                    "Suitably normalised block maxima of i.i.d. variables can converge only to a GEV distribution",
                    "Sums of i.i.d. variables converge to the Normal distribution",
                    "VaR is always subadditive"
                ],
                "correctExplanation": "The non-degenerate limits of normalised maxima form the GEV family (Frechet, Gumbel, Weibull).",
                "incorrectExplanation": "The GPD result for threshold excesses is the Pickands-Balkema-de Haan theorem; the Normal limit of sums is the central limit theorem."
            },
            "ro": {
                "title": "Fisher-Tippett-Gnedenko",
                "text": "Ce afirmă teorema Fisher-Tippett-Gnedenko?",
                "options": [
                    "Excesele peste un prag ridicat urmează o GPD",
                    "Maximele pe blocuri ale unor variabile i.i.d., normalizate corespunzător, pot converge doar la o distribuție GEV",
                    "Sumele de variabile i.i.d. converg la distribuția Normală",
                    "VaR este întotdeauna subaditiv"
                ],
                "correctExplanation": "Limitele nedegenerate ale maximelor normalizate formează familia GEV (Frechet, Gumbel, Weibull).",
                "incorrectExplanation": "Rezultatul GPD pentru excesele peste prag este teorema Pickands-Balkema-de Haan; limita Normală a sumelor este teorema limită centrală."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Shape parameter",
                "text": "The GPD fitted to S&P 500 losses above the 95% quantile has xi = 0.19. What does this mean?",
                "options": [
                    "The tail is bounded",
                    "The tail is exponential, as for the Normal distribution",
                    "A power-law (Frechet-type) tail with tail index about 1/0.19 = 5.3",
                    "The variance is infinite"
                ],
                "correctExplanation": "xi > 0 means a heavy power-law tail; moments exist up to order below 1/xi, here about 5.",
                "incorrectExplanation": "A positive shape parameter implies a Frechet-type heavy tail; xi = 0 would be exponential and xi < 0 bounded."
            },
            "ro": {
                "title": "Parametrul de formă",
                "text": "GPD estimată pe pierderile S&P 500 peste cuantila de 95% are xi = 0,19. Ce înseamnă?",
                "options": [
                    "Coada este mărginită",
                    "Coada este exponențială, ca la distribuția Normală",
                    "O coadă de tip putere (Frechet) cu indicele de coadă aproximativ 1/0,19 = 5,3",
                    "Dispersia este infinită"
                ],
                "correctExplanation": "xi > 0 înseamnă o coadă grea de tip putere; momentele există pînă la un ordin sub 1/xi, aici aproximativ 5.",
                "incorrectExplanation": "Un parametru de formă pozitiv implică o coadă grea de tip Frechet; xi = 0 ar fi exponențială, iar xi < 0 mărginită."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Mean excess plot",
                "text": "What pattern in the mean excess plot supports a GPD tail with 0 < xi < 1?",
                "options": [
                    "A flat line",
                    "A decreasing line",
                    "Random scatter around zero",
                    "An approximately linear increase with the threshold"
                ],
                "correctExplanation": "For a GPD tail with xi < 1 (finite mean) e(u) is linear in u with slope xi/(1 - xi): upward sloping when 0 < xi < 1.",
                "incorrectExplanation": "A flat mean excess indicates an exponential tail, a decreasing one a bounded tail; heavy tails give an upward line."
            },
            "ro": {
                "title": "Graficul excesului mediu",
                "text": "Ce tipar în graficul excesului mediu susține o coadă GPD cu 0 < xi < 1?",
                "options": [
                    "O linie orizontală",
                    "O linie descrescătoare",
                    "O împrăștiere aleatoare în jurul lui zero",
                    "O creștere aproximativ liniară cu pragul"
                ],
                "correctExplanation": "Pentru o coadă GPD cu xi < 1 (medie finită), e(u) este liniară în u cu panta xi/(1 - xi): crescătoare cînd 0 < xi < 1.",
                "incorrectExplanation": "Un exces mediu constant indică o coadă exponențială, unul descrescător o coadă mărginită; cozile grele dau o linie crescătoare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Conditional EVT",
                "text": "What does the McNeil-Frey conditional EVT approach combine?",
                "options": [
                    "Historical simulation with a 250-day window and Cornish-Fisher",
                    "A GARCH filter for volatility and a GPD fitted to the tail of the standardised residuals",
                    "Block maxima and the Normal distribution",
                    "Monte Carlo from the Normal distribution"
                ],
                "correctExplanation": "The GARCH filter makes residuals approximately i.i.d.; the GPD then models their tail, and VaR = -mu + sigma times the GPD quantile.",
                "incorrectExplanation": "Conditional EVT is GARCH scale plus a GPD tail of standardised residuals."
            },
            "ro": {
                "title": "EVT condiționată",
                "text": "Ce combină abordarea EVT condiționată McNeil-Frey?",
                "options": [
                    "Simularea istorică pe 250 de zile și Cornish-Fisher",
                    "Un filtru GARCH pentru volatilitate și o GPD estimată pe coada reziduurilor standardizate",
                    "Maximele pe blocuri și distribuția Normală",
                    "Monte Carlo din distribuția Normală"
                ],
                "correctExplanation": "Filtrul GARCH face reziduurile aproximativ i.i.d.; GPD le modelează apoi coada, iar VaR = -mu + sigma înmulțit cu cuantila GPD.",
                "incorrectExplanation": "EVT condiționată înseamnă scală GARCH plus o coadă GPD a reziduurilor standardizate."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "GARCH with Normal shocks",
                "text": "For the S&P 500 in 2018-2026, VaR 1% from GARCH with Normal shocks was exceeded on 2.4% of days. Why?",
                "options": [
                    "Volatility forecasts were too slow",
                    "The window was too short",
                    "The Normal shocks are too thin-tailed even after filtering",
                    "The tail probability was 2.5%"
                ],
                "correctExplanation": "Standardised residuals remain heavy-tailed (minus their 1% quantile is about 2.8 vs 2.33), so the Normal quantile is too small.",
                "incorrectExplanation": "GARCH gets the timing right; the level is wrong because the shock distribution has heavier tails than the Normal distribution."
            },
            "ro": {
                "title": "GARCH cu șocuri Normale",
                "text": "Pentru S&P 500 în 2018-2026, VaR 1% din GARCH cu șocuri Normale a fost depășit în 2,4% din zile. De ce?",
                "options": [
                    "Prognozele de volatilitate au fost prea lente",
                    "Fereastra a fost prea scurtă",
                    "Șocurile Normale au cozi prea subțiri chiar și după filtrare",
                    "Probabilitatea cozii a fost 2,5%"
                ],
                "correctExplanation": "Reziduurile standardizate rămîn cu cozi grele (minus cuantila lor de 1% este aproximativ 2,8 față de 2,33), deci cuantila Normală este prea mică.",
                "incorrectExplanation": "GARCH prinde corect momentul; nivelul este greșit pentru că distribuția șocurilor are cozi mai grele decît distribuția Normală."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "VaR under dependence uncertainty",
                "text": "The margins of L1 and L2 are known but their copula is not. What can be said about the worst-case VaR 1% of L1 + L2?",
                "options": [
                    "It equals VaR(L1) + VaR(L2), the comonotone value",
                    "It can exceed VaR(L1) + VaR(L2)",
                    "It equals the VaR under independence",
                    "It is bounded by the VaR under a Gaussian copula"
                ],
                "correctExplanation": "VaR is not subadditive, so a dependence structure that concentrates the tail mass can push the VaR of the sum above the comonotone sum; the rearrangement algorithm computes this worst case.",
                "incorrectExplanation": "For VaR the comonotone sum need not be the worst case: the worst case is found by rearranging the tails and is often above it, far above independence or a Gaussian copula. The comonotone sum is the worst case for ES, which is subadditive and comonotone additive."
            },
            "ro": {
                "title": "VaR sub incertitudinea dependenței",
                "text": "Marginalele lui L1 și L2 sînt cunoscute, dar copula lor nu. Ce se poate spune despre VaR 1% maxim al lui L1 + L2?",
                "options": [
                    "Este egal cu VaR(L1) + VaR(L2), valoarea comonotonă",
                    "Poate depăși VaR(L1) + VaR(L2)",
                    "Este egal cu VaR sub independență",
                    "Este mărginit de VaR sub o copulă Gaussiană"
                ],
                "correctExplanation": "VaR nu este subaditiv, deci o structură de dependență care concentrează masa din coadă poate împinge VaR-ul sumei peste suma comonotonă; algoritmul de rearanjare calculează acest caz cel mai rău.",
                "incorrectExplanation": "Pentru VaR, suma comonotonă nu este neapărat cazul cel mai rău: acesta se găsește rearanjînd cozile și este adesea peste ea, mult peste independență sau o copulă Gaussiană. Suma comonotonă este cazul cel mai rău pentru ES, care este subaditiv și aditiv comonoton."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Why ES 2.5%",
                "text": "Why was ES set at 2.5% rather than at 1%, the old VaR level?",
                "options": [
                    "Under the Normal distribution ES 2.5% is almost equal to VaR 1%, so capital stays similar for thin tails but rises for heavy tails",
                    "Because ES 2.5% is easier to backtest than any VaR",
                    "Because ES 1% does not exist",
                    "Because it lowers capital for all portfolios"
                ],
                "correctExplanation": "2.338 sigma vs 2.326 sigma: the switch is neutral for thin tails and charges more where the tail is heavy.",
                "incorrectExplanation": "The choice keeps capital comparable in the Normal case while making it sensitive to the tail beyond the quantile."
            },
            "ro": {
                "title": "De ce ES 2,5%",
                "text": "De ce ES a fost stabilit la 2,5% și nu la 1%, vechiul nivel al VaR?",
                "options": [
                    "Sub distribuția Normală, ES 2,5% este aproape egal cu VaR 1%, deci capitalul rămîne similar pentru cozi subțiri, dar crește pentru cozi grele",
                    "Pentru că ES 2,5% este mai ușor de supus backtesting-ului decît orice VaR",
                    "Pentru că ES 1% nu există",
                    "Pentru că reduce capitalul pentru toate portofoliile"
                ],
                "correctExplanation": "2,338 sigma față de 2,326 sigma: trecerea este neutră pentru cozi subțiri și cere mai mult acolo unde coada este grea.",
                "incorrectExplanation": "Alegerea păstrează capitalul comparabil în cazul Normal, făcîndu-l în același timp sensibil la coada de dincolo de cuantilă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Elicitability",
                "text": "Which statement about elicitability is correct?",
                "options": [
                    "ES alone is elicitable, VaR is not",
                    "VaR is elicitable; ES alone is not, but the pair (VaR, ES) is jointly elicitable",
                    "Neither VaR nor ES can ever be backtested",
                    "Both are elicitable with the squared error"
                ],
                "correctExplanation": "The quantile minimises the pinball loss; Gneiting (2011) showed ES alone is not elicitable, and Fissler and Ziegel (2016) showed joint elicitability.",
                "incorrectExplanation": "VaR is elicitable, ES only jointly with VaR; this is why ES backtesting is harder (Chapter 8)."
            },
            "ro": {
                "title": "Elicitabilitatea",
                "text": "Care afirmație despre elicitabilitate este corectă?",
                "options": [
                    "ES singur este elicitabil, VaR nu",
                    "VaR este elicitabil; ES singur nu este, dar perechea (VaR, ES) este elicitabilă împreună",
                    "Nici VaR, nici ES nu pot fi supuse backtesting-ului",
                    "Ambele sînt elicitabile cu eroarea pătratică"
                ],
                "correctExplanation": "Cuantila minimizează funcția de pierdere pinball; Gneiting (2011) a arătat că ES singur nu este elicitabil, iar Fissler și Ziegel (2016) au arătat elicitabilitatea comună.",
                "incorrectExplanation": "VaR este elicitabil, ES doar împreună cu VaR; de aceea backtesting-ul ES este mai dificil (Capitolul 8)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Precision of ES",
                "text": "Historical ES 2.5% on a 500-day window averages how many observations?",
                "options": [
                    "500",
                    "50",
                    "About 12.5 (n alpha)",
                    "About 2"
                ],
                "correctExplanation": "n alpha = 500 x 0.025 = 12.5 (the course's tail mean averages the 13 losses at or above the interpolated VaR): the estimate is very noisy, as bootstrap intervals about 2 percentage points wide show.",
                "incorrectExplanation": "Only the worst 2.5% of days enter the average: 2.5% of 500 days."
            },
            "ro": {
                "title": "Precizia ES",
                "text": "ES 2,5% istoric pe o fereastră de 500 de zile face media a cîte observații?",
                "options": [
                    "500",
                    "50",
                    "Aproximativ 12,5 (n alfa)",
                    "Aproximativ 2"
                ],
                "correctExplanation": "n alfa = 500 x 0,025 = 12,5 (media din coadă folosită în curs mediază cele 13 pierderi mai mari sau egale cu VaR interpolat): estimarea este foarte zgomotoasă, așa cum arată intervalele bootstrap largi de aproximativ 2 puncte procentuale.",
                "incorrectExplanation": "În medie intră doar cele mai rele 2,5% dintre zile: 2,5% din 500 de zile."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Liquidity-adjusted VaR",
                "text": "In the Bangia et al. approach, what is added to market VaR?",
                "options": [
                    "The full bid-ask spread times 10",
                    "The expected return",
                    "The GARCH volatility",
                    "Half of the relative spread, using its mean plus a multiple of its standard deviation"
                ],
                "correctExplanation": "Exiting a position costs half the spread; LVaR = VaR + 0.5 (mu_S + a sigma_S) covers spread widening in stress.",
                "incorrectExplanation": "The liquidity add-on is the exogenous cost of crossing half the bid-ask spread in a stressed market."
            },
            "ro": {
                "title": "VaR ajustat la lichiditate",
                "text": "În abordarea Bangia et al., ce se adaugă la VaR de piață?",
                "options": [
                    "Întregul spread bid-ask înmulțit cu 10",
                    "Randamentul așteptat",
                    "Volatilitatea GARCH",
                    "Jumătate din spread-ul relativ, folosind media lui plus un multiplu al abaterii standard"
                ],
                "correctExplanation": "Ieșirea dintr-o poziție costă jumătate din spread; LVaR = VaR + 0,5 (mu_S + a sigma_S) acoperă lărgirea spread-ului în condiții de stres.",
                "incorrectExplanation": "Ajustarea de lichiditate este costul exogen al plății a jumătate din spread-ul bid-ask pe o piață aflată în stres."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the error: VaR sign convention",
                "text": "An AI assistant writes: \"The 1% quantile of the daily returns is -2.3%, so the one-day VaR 1% of the position is -2.3%.\" Using the course convention, what is the error?",
                "options": [
                    "The VaR 1% is the 99% quantile of the returns, +2.3%",
                    "VaR is reported as a positive loss: VaR 1% = -q_1% = 2.3% of the position",
                    "The VaR 1% needs the 0.1% quantile, not the 1% quantile",
                    "VaR cannot be computed from a quantile of returns"
                ],
                "correctExplanation": "With the loss L = -r, VaR_alpha = -q_alpha(r) = q_(1-alpha)(L), a positive number. A return quantile of -2.3% means a VaR 1% of 2.3% of the position.",
                "incorrectExplanation": "The quantile is the right one; only the sign is wrong: VaR_alpha = -q_alpha, so the VaR 1% is +2.3% of the position."
            },
            "ro": {
                "title": "Găsiți eroarea: convenția de semn pentru VaR",
                "text": "Un asistent AI scrie: „Cuantila de 1% a randamentelor zilnice este -2,3%, deci VaR 1% pe o zi al poziției este -2,3%.” Conform convenției cursului, care este eroarea?",
                "options": [
                    "VaR 1% este cuantila de 99% a randamentelor, +2,3%",
                    "VaR se raportează ca pierdere pozitivă: VaR 1% = -q_1% = 2,3% din poziție",
                    "VaR 1% cere cuantila de 0,1%, nu cuantila de 1%",
                    "VaR nu se poate calcula dintr-o cuantilă a randamentelor"
                ],
                "correctExplanation": "Cu pierderea L = -r, VaR_alpha = -q_alpha(r) = q_(1-alpha)(L), un număr pozitiv. O cuantilă a randamentelor de -2,3% înseamnă un VaR 1% de 2,3% din poziție.",
                "incorrectExplanation": "Cuantila este cea corectă; doar semnul este greșit: VaR_alpha = -q_alpha, deci VaR 1% este +2,3% din poziție."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the error: historical ES",
                "text": "An AI assistant writes: \"With 1,000 daily losses, the historical ES 2.5% is the average of the 10 largest losses.\" What is the error?",
                "options": [
                    "ES 2.5% is the median, not the average, of the largest losses",
                    "ES 2.5% is the single 25th largest loss",
                    "Historical ES cannot be computed from 1,000 observations",
                    "The 2.5% tail of 1,000 losses contains the 25 largest; the average of the 10 largest is ES 1%"
                ],
                "correctExplanation": "ES_alpha averages the losses beyond VaR_alpha, i.e. the worst alpha share of the sample: 2.5% of 1,000 = 25 losses. Averaging only the 10 largest gives ES 1%, a more extreme and noisier number.",
                "incorrectExplanation": "ES is a tail average, but of the worst 2.5% of the losses, i.e. 25 of 1,000; 10 losses correspond to the 1% tail."
            },
            "ro": {
                "title": "Găsiți eroarea: ES istoric",
                "text": "Un asistent AI scrie: „Cu 1.000 de pierderi zilnice, ES 2,5% istoric este media celor mai mari 10 pierderi.” Care este eroarea?",
                "options": [
                    "ES 2,5% este mediana, nu media, celor mai mari pierderi",
                    "ES 2,5% este doar a 25-a cea mai mare pierdere",
                    "ES istoric nu se poate calcula din 1.000 de observații",
                    "Coada de 2,5% a 1.000 de pierderi conține cele mai mari 25; media celor mai mari 10 este ES 1%"
                ],
                "correctExplanation": "ES_alpha mediază pierderile dincolo de VaR_alpha, adică cea mai rea parte alpha a eșantionului: 2,5% din 1.000 = 25 de pierderi. Media doar a celor mai mari 10 dă ES 1%, o cifră mai extremă și mai zgomotoasă.",
                "incorrectExplanation": "ES este o medie în coadă, dar a celor mai rele 2,5% dintre pierderi, adică 25 din 1.000; 10 pierderi corespund cozii de 1%."
            }
        }
    ]
};

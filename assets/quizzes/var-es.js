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
            "correct": 1,
            "en": {
                "title": "Definition of VaR",
                "text": "With losses counted as positive numbers, what is the one-day VaR 1%?",
                "options": [
                    "The average loss on the worst 1% of days",
                    "The loss exceeded with probability 1%, i.e. minus the 1% quantile of the one-day return",
                    "The largest loss ever observed",
                    "The standard deviation of losses times 2.33"
                ],
                "correctExplanation": "VaR 1% = -q_1%(X): the one-day loss exceeds it with probability 1%.",
                "incorrectExplanation": "VaR 1% is minus the 1% quantile of the return; the average beyond it is Expected Shortfall, and 2.33 standard deviations is only the Normal special case."
            },
            "ro": {
                "title": "Definiția VaR",
                "text": "Cu pierderile socotite ca numere pozitive, ce este VaR 1% pe o zi?",
                "options": [
                    "Pierderea medie în cele mai rele 1% dintre zile",
                    "Pierderea depășită cu probabilitatea 1%, adică minus cuantila de 1% a randamentului pe o zi",
                    "Cea mai mare pierdere observată vreodată",
                    "Abaterea standard a pierderilor înmulțită cu 2,33"
                ],
                "correctExplanation": "VaR 1% = -q_1%(X): pierderea pe o zi îl depășește cu probabilitatea 1%.",
                "incorrectExplanation": "VaR 1% este minus cuantila de 1% a randamentului; media de dincolo de ea este Expected Shortfall, iar 2,33 abateri standard este doar cazul particular al distribuției Normale."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Definition of ES",
                "text": "Which expression defines Expected Shortfall with tail probability alpha for a continuous loss L = -X?",
                "options": [
                    "P(L > VaR)",
                    "VaR divided by alpha",
                    "E[L | L >= VaR_alpha(L)]",
                    "The median of L"
                ],
                "correctExplanation": "For a continuous distribution ES is the expected loss given that the loss is at least VaR, equivalently the average of VaR_u over u below alpha.",
                "incorrectExplanation": "ES averages the losses beyond VaR; it is not a probability, a rescaled VaR or a median."
            },
            "ro": {
                "title": "Definiția ES",
                "text": "Ce expresie definește Expected Shortfall cu probabilitatea cozii alfa pentru o pierdere continuă L = -X?",
                "options": [
                    "P(L > VaR)",
                    "VaR împărțit la alfa",
                    "E[L | L >= VaR_alfa(L)]",
                    "Mediana lui L"
                ],
                "correctExplanation": "Pentru o distribuție continuă, ES este pierderea așteptată condiționat de faptul că pierderea este cel puțin VaR, echivalent media lui VaR_u pentru u sub alfa.",
                "incorrectExplanation": "ES face media pierderilor de dincolo de VaR; nu este o probabilitate, un VaR rescalat sau o mediană."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Coherence",
                "text": "Which axiom of a coherent risk measure can VaR violate?",
                "options": [
                    "Subadditivity",
                    "Monotonicity",
                    "Translation invariance",
                    "Positive homogeneity"
                ],
                "correctExplanation": "VaR satisfies monotonicity, translation invariance and positive homogeneity, but the risk of a combined position can exceed the sum of the stand-alone VaRs.",
                "incorrectExplanation": "The problematic axiom is subadditivity: VaR can penalise diversification, as in the two-bond example."
            },
            "ro": {
                "title": "Coerența",
                "text": "Ce axiomă a unei măsuri de risc coerente poate fi încălcată de VaR?",
                "options": [
                    "Subaditivitatea",
                    "Monotonia",
                    "Invarianța la translație",
                    "Omogenitatea pozitivă"
                ],
                "correctExplanation": "VaR satisface monotonia, invarianța la translație și omogenitatea pozitivă, dar riscul unei poziții combinate poate depăși suma VaR-urilor individuale.",
                "incorrectExplanation": "Axioma problematică este subaditivitatea: VaR poate penaliza diversificarea, ca în exemplul cu două obligațiuni."
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
                "title": "Normal ES constant",
                "text": "Under the Normal distribution with zero mean, ES 2.5% equals sigma times approximately which number?",
                "options": [
                    "1.960",
                    "2.338",
                    "2.326",
                    "2.665"
                ],
                "correctExplanation": "ES 2.5% = sigma phi(z_2.5%)/0.025 = 2.338 sigma, almost the same as VaR 1% = 2.326 sigma.",
                "incorrectExplanation": "1.960 and 2.326 are the Normal VaR constants at 2.5% and 1%; 2.665 is the ES 1% constant."
            },
            "ro": {
                "title": "Constanta ES Normală",
                "text": "Sub distribuția Normală cu medie zero, ES 2,5% este egal cu sigma înmulțit cu aproximativ ce număr?",
                "options": [
                    "1,960",
                    "2,338",
                    "2,326",
                    "2,665"
                ],
                "correctExplanation": "ES 2,5% = sigma phi(z_2,5%)/0,025 = 2,338 sigma, aproape la fel ca VaR 1% = 2,326 sigma.",
                "incorrectExplanation": "1,960 și 2,326 sunt constantele VaR Normale la 2,5% și 1%; 2,665 este constanta ES 1%."
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
                    "Pierderile zilnice au cozi mai grele decât distribuția Normală",
                    "Simularea istorică supraestimează mereu VaR"
                ],
                "correctExplanation": "Un exces de aplatizare peste 10 pune mai multă probabilitate departe de centru decât permite distribuția Normală, deci cuantila empirică este mai mare.",
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
                "text": "Când dă dezvoltarea Cornish-Fisher estimări VaR nesigure?",
                "options": [
                    "Când asimetria și excesul de aplatizare sunt mari, ca la randamentele zilnice cu aplatizare în jur de 10",
                    "Când distribuția este exact Normală",
                    "Când selecția este foarte lungă",
                    "Când probabilitatea cozii este 10%"
                ],
                "correctExplanation": "Dezvoltarea corectează cuantila Normală pentru abateri mici; cu o aplatizare în jur de 10, termenul de aplatizare depășește ținta, de ex. 6,08% față de 3,45% pentru S&P 500.",
                "incorrectExplanation": "Cornish-Fisher este exactă pentru distribuția Normală și funcționează pentru abateri mici; asimetria și aplatizarea mari o strică."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Historical simulation",
                "text": "What is a known weakness of historical simulation with a 500-day window?",
                "options": [
                    "It needs a GARCH model",
                    "It assumes the Normal distribution",
                    "It cannot be computed for ES",
                    "It reacts slowly to volatility changes and produces ghost effects when crisis days leave the window"
                ],
                "correctExplanation": "HS weights all 500 days equally: VaR stays low after a calm period and drops abruptly when a crash day leaves the window.",
                "incorrectExplanation": "HS makes no distributional assumption and gives ES directly; its problem is the equal weighting of an old window."
            },
            "ro": {
                "title": "Simularea istorică",
                "text": "Care este o slăbiciune cunoscută a simulării istorice cu o fereastră de 500 de zile?",
                "options": [
                    "Are nevoie de un model GARCH",
                    "Presupune distribuția Normală",
                    "Nu poate fi calculată pentru ES",
                    "Reacționează lent la schimbările de volatilitate și produce efecte fantomă când zilele de criză ies din fereastră"
                ],
                "correctExplanation": "HS ponderează egal toate cele 500 de zile: VaR rămâne mic după o perioadă calmă și scade brusc când o zi de criză iese din fereastră.",
                "incorrectExplanation": "HS nu face nicio ipoteză de distribuție și dă direct ES; problema ei este ponderarea egală a unei ferestre vechi."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Filtered historical simulation",
                "text": "In filtered historical simulation, how is tomorrow's VaR computed?",
                "options": [
                    "The empirical quantile of raw returns times the square root of 10",
                    "Tomorrow's GARCH volatility times the empirical quantile of the standardised residuals, adjusted for the conditional mean",
                    "The Normal quantile times the sample standard deviation",
                    "The largest loss of the last year"
                ],
                "correctExplanation": "FHS takes the shape of the shocks from history (standardised residuals) and the scale from the GARCH forecast.",
                "incorrectExplanation": "FHS rescales empirical standardised residuals by the GARCH volatility forecast; it is neither a Normal model nor a raw historical quantile."
            },
            "ro": {
                "title": "Simularea istorică filtrată",
                "text": "În simularea istorică filtrată, cum se calculează VaR de mâine?",
                "options": [
                    "Cuantila empirică a randamentelor brute înmulțită cu radical din 10",
                    "Volatilitatea GARCH de mâine înmulțită cu cuantila empirică a reziduurilor standardizate, ajustată pentru media condiționată",
                    "Cuantila Normală înmulțită cu abaterea standard de selecție",
                    "Cea mai mare pierdere din ultimul an"
                ],
                "correctExplanation": "FHS ia forma șocurilor din istorie (reziduurile standardizate) și scala din prognoza GARCH.",
                "incorrectExplanation": "FHS rescalează reziduurile standardizate empirice cu prognoza de volatilitate GARCH; nu este nici un model Normal, nici o cuantilă istorică brută."
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
                "correctExplanation": "O prognoză VaR zilnică bună produce depășiri împrăștiate în timp; grupurile arată că fereastra reacționează prea târziu la șocurile de volatilitate.",
                "incorrectExplanation": "Depășirile grupate sunt semnătura unei măsuri necondiționate pe o piață cu grupare a volatilității."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Square-root-of-time",
                "text": "Under which assumptions is the 10-day VaR exactly the square root of 10 times the one-day VaR?",
                "options": [
                    "i.i.d. Normal daily losses with zero mean",
                    "Any distribution with finite variance",
                    "GARCH volatility with Student-t shocks",
                    "Positively autocorrelated returns"
                ],
                "correctExplanation": "Only for i.i.d. Normal losses with zero mean is the 10-day loss Normal with standard deviation sqrt(10) sigma, so every quantile scales by sqrt(10).",
                "incorrectExplanation": "Autocorrelation, volatility clustering, heavy tails and a non-zero mean all break the exact scaling."
            },
            "ro": {
                "title": "Radical din timp",
                "text": "În ce ipoteze VaR pe 10 zile este exact radical din 10 înmulțit cu VaR pe o zi?",
                "options": [
                    "Pierderi zilnice i.i.d. Normale cu medie zero",
                    "Orice distribuție cu dispersie finită",
                    "Volatilitate GARCH cu șocuri Student-t",
                    "Randamente cu autocorelație pozitivă"
                ],
                "correctExplanation": "Doar pentru pierderi i.i.d. Normale cu medie zero pierderea pe 10 zile este Normală cu abaterea standard radical(10) sigma, deci orice cuantilă se scalează cu radical(10).",
                "incorrectExplanation": "Autocorelația, gruparea volatilității, cozile grele și media nenulă strică toate scalarea exactă."
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
                "incorrectExplanation": "Cheia este persistența: randamentele autocorelate pozitiv se acumulează, iar coada pe mai multe zile devine mai largă decât sugerează radical(h)."
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
                    "Pentru că corelațiile sunt zero",
                    "Pentru că VaR este pozitiv omogen de grad unu în ponderi (teorema lui Euler)",
                    "Pentru că randamentele sunt Normale",
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
                "correctExplanation": "Volatilitatea zilnică a Bitcoin este de aproape patru ori cea a SPY și este corelat pozitiv cu acțiunile, deci 10% din bani poartă aproximativ 38% din VaR.",
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
                "correctExplanation": "xi > 0 înseamnă o coadă grea de tip putere; momentele există până la un ordin sub 1/xi, aici aproximativ 5.",
                "incorrectExplanation": "Un parametru de formă pozitiv implică o coadă grea de tip Frechet; xi = 0 ar fi exponențială, iar xi < 0 mărginită."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Mean excess plot",
                "text": "What pattern in the mean excess plot supports a GPD tail with xi > 0?",
                "options": [
                    "A flat line",
                    "A decreasing line",
                    "Random scatter around zero",
                    "An approximately linear increase with the threshold"
                ],
                "correctExplanation": "For a GPD tail e(u) is linear in u with slope xi/(1 - xi): upward sloping when xi > 0.",
                "incorrectExplanation": "A flat mean excess indicates an exponential tail, a decreasing one a bounded tail; heavy tails give an upward line."
            },
            "ro": {
                "title": "Graficul excesului mediu",
                "text": "Ce tipar în graficul excesului mediu susține o coadă GPD cu xi > 0?",
                "options": [
                    "O linie orizontală",
                    "O linie descrescătoare",
                    "O împrăștiere aleatoare în jurul lui zero",
                    "O creștere aproximativ liniară cu pragul"
                ],
                "correctExplanation": "Pentru o coadă GPD, e(u) este liniară în u cu panta xi/(1 - xi): crescătoare când xi > 0.",
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
                "correctExplanation": "Reziduurile standardizate rămân cu cozi grele (minus cuantila lor de 1% este aproximativ 2,8 față de 2,33), deci cuantila Normală este prea mică.",
                "incorrectExplanation": "GARCH prinde corect momentul; nivelul este greșit pentru că distribuția șocurilor are cozi mai grele decât distribuția Normală."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "FRTB",
                "text": "What risk measure sets market-risk capital under the Basel FRTB standard (2019)?",
                "options": [
                    "VaR 1% over 10 days",
                    "VaR 0.1% over one year",
                    "Standard deviation over one day",
                    "ES 2.5% with a 10-day base horizon and liquidity horizons"
                ],
                "correctExplanation": "FRTB uses ES 2.5% (one-tailed), scaled from a 10-day base horizon by liquidity horizons and calibrated to a stressed period.",
                "incorrectExplanation": "The 1996 rules used VaR 1% over 10 days; FRTB replaced it by ES 2.5%."
            },
            "ro": {
                "title": "FRTB",
                "text": "Ce măsură de risc stabilește capitalul pentru riscul de piață conform standardului Basel FRTB (2019)?",
                "options": [
                    "VaR 1% pe 10 zile",
                    "VaR 0,1% pe un an",
                    "Abaterea standard pe o zi",
                    "ES 2,5% cu orizont de bază de 10 zile și orizonturi de lichiditate"
                ],
                "correctExplanation": "FRTB folosește ES 2,5% (unilateral), scalat de la un orizont de bază de 10 zile prin orizonturi de lichiditate și calibrat pe o perioadă de stres.",
                "incorrectExplanation": "Regulile din 1996 foloseau VaR 1% pe 10 zile; FRTB l-a înlocuit cu ES 2,5%."
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
                    "Sub distribuția Normală, ES 2,5% este aproape egal cu VaR 1%, deci capitalul rămâne similar pentru cozi subțiri, dar crește pentru cozi grele",
                    "Pentru că ES 2,5% este mai ușor de testat retrospectiv decât orice VaR",
                    "Pentru că ES 1% nu există",
                    "Pentru că reduce capitalul pentru toate portofoliile"
                ],
                "correctExplanation": "2,338 sigma față de 2,326 sigma: trecerea este neutră pentru cozi subțiri și cere mai mult acolo unde coada este grea.",
                "incorrectExplanation": "Alegerea păstrează capitalul comparabil în cazul Normal, făcându-l în același timp sensibil la coada de dincolo de cuantilă."
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
                    "Nici VaR, nici ES nu pot fi testate retrospectiv",
                    "Ambele sunt elicitabile cu eroarea pătratică"
                ],
                "correctExplanation": "Cuantila minimizează funcția de pierdere pinball; Gneiting (2011) a arătat că ES singur nu este elicitabil, iar Fissler și Ziegel (2016) au arătat elicitabilitatea comună.",
                "incorrectExplanation": "VaR este elicitabil, ES doar împreună cu VaR; de aceea testarea retrospectivă a ES este mai dificilă (Capitolul 8)."
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
                    "About 12",
                    "About 2"
                ],
                "correctExplanation": "n alpha = 500 x 0.025 = 12.5: the estimate is very noisy, as bootstrap intervals about 2 percentage points wide show.",
                "incorrectExplanation": "Only the worst 2.5% of days enter the average: 2.5% of 500 days."
            },
            "ro": {
                "title": "Precizia ES",
                "text": "ES 2,5% istoric pe o fereastră de 500 de zile face media a câte observații?",
                "options": [
                    "500",
                    "50",
                    "Aproximativ 12",
                    "Aproximativ 2"
                ],
                "correctExplanation": "n alfa = 500 x 0,025 = 12,5: estimarea este foarte zgomotoasă, așa cum arată intervalele bootstrap largi de aproximativ 2 puncte procentuale.",
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
                "incorrectExplanation": "Ajustarea de lichiditate este costul exogen al traversării a jumătate din spread-ul bid-ask pe o piață aflată în stres."
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

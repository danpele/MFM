// ============================================================
// Quiz bank for chapter id 'dependence': Multivariate Volatility and Dependence (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// Numbers come from Quantlets/Ch_06 (ch6_numbers.json, ch6_seminar_numbers.json).
// ============================================================
window.MFM_DATA.quizzes['dependence'] = {
    draw: 20,
    questions: [
        {
            correct: 1,
            en: {
                title: "CML on GARCH residuals",
                text: "A t copula is fitted by canonical maximum likelihood (CML) to the ranks of GARCH-standardised residuals. Compared with the same estimator on the ranks of the true innovations, its asymptotic variance is:",
                options: [
                    "Larger, because the GARCH parameters are estimated in a first step",
                    "Unchanged: the first-step GARCH estimation does not affect the limit distribution (Chen and Fan, 2006)",
                    "Smaller, because filtering removes volatility clustering",
                    "Undefined, because ranks of residuals are not independent"
                ],
                correctExplanation: "Chen and Fan (2006) show that CML on the ranks of estimated GARCH residuals has the same limit as on the true innovations; in the lecture Monte Carlo the standard deviations were 0.0081 and 0.0082.",
                incorrectExplanation: "Intuition suggests a first-step penalty, but for rank-based CML on GARCH residuals the limit distribution is unchanged; only the rank term of Genest, Ghoudi and Rivest is needed."
            },
            ro: {
                title: "CML pe reziduuri GARCH",
                text: "O copulă t este estimată prin verosimilitate maximă canonică (CML) pe rangurile reziduurilor standardizate GARCH. Față de același estimator pe rangurile inovațiilor adevărate, varianța sa asimptotică este:",
                options: [
                    "Mai mare, pentru că parametrii GARCH sînt estimați într-un prim pas",
                    "Neschimbată: estimarea GARCH din primul pas nu afectează distribuția limită (Chen și Fan, 2006)",
                    "Mai mică, pentru că filtrarea elimină volatility clustering",
                    "Nedefinită, pentru că rangurile reziduurilor nu sînt independente"
                ],
                correctExplanation: "Chen și Fan (2006) arată că CML pe rangurile reziduurilor GARCH estimate are aceeași limită ca pe inovațiile adevărate; în simularea Monte Carlo din curs abaterile standard au fost 0,0081 și 0,0082.",
                incorrectExplanation: "Intuiția sugerează o penalizare pentru primul pas, dar pentru CML pe ranguri ale reziduurilor GARCH distribuția limită nu se schimbă; este necesar doar termenul de rang Genest, Ghoudi și Rivest."
            }
        },
        {
            correct: 0,
            en: {
                title: 'Stock–bond correlation',
                text: 'The SPY–TLT daily correlation was -0.40 in 2002–2021 and 0.11 since 2022. What happened to a 60/40 portfolio?',
                options: [
                    'Its volatility rose from about 10.4% to 13.2% even with unchanged asset volatilities',
                    'Its volatility fell, because a positive correlation always reduces risk',
                    'Nothing: correlation does not enter portfolio volatility',
                    'It became riskless'
                ],
                correctExplanation: 'With the same asset volatilities, moving from a negative to a slightly positive correlation raises the 60/40 volatility: bonds stopped hedging equities.',
                incorrectExplanation: 'A higher correlation increases the cross term and therefore the portfolio volatility.'
            },
            ro: {
                title: 'Corelația acțiuni–obligațiuni',
                text: 'Corelația zilnică SPY–TLT a fost -0,40 în 2002–2021 și 0,11 din 2022. Ce s-a întîmplat cu un portofoliu 60/40?',
                options: [
                    'Volatilitatea lui a crescut de la circa 10,4% la 13,2%, chiar cu volatilitățile activelor neschimbate',
                    'Volatilitatea a scăzut, pentru că o corelație pozitivă reduce întotdeauna riscul',
                    'Nimic: corelația nu intră în volatilitatea portofoliului',
                    'A devenit fără risc'
                ],
                correctExplanation: 'Cu aceleași volatilități ale activelor, trecerea de la o corelație negativă la una ușor pozitivă crește volatilitatea portofoliului 60/40: obligațiunile nu mai oferă hedge pentru riscul acțiunilor.',
                incorrectExplanation: 'O corelație mai mare crește termenul încrucișat și deci volatilitatea portofoliului.'
            }
        },
        {
            correct: 3,
            en: {
                title: "CML standard errors",
                text: "Why is the inverse Hessian of the copula pseudo-likelihood not a valid covariance matrix for CML estimates?",
                options: [
                    "The copula log-likelihood is not concave",
                    "The fitted copula is always misspecified",
                    "Financial returns are serially dependent",
                    "The pseudo-observations are estimated ranks, which adds a variance term from the empirical margins (Genest, Ghoudi and Rivest, 1995)"
                ],
                correctExplanation: "The sandwich A⁻¹ΣA⁻¹ adds W1(U) + W2(V) to the score; for the weekly S&P 500–Euro Stoxx 50 Gaussian copula the standard error of ρ rises from 0.0085 to 0.0137.",
                incorrectExplanation: "The issue is neither concavity nor serial dependence: the margins are estimated through ranks, and that estimation error must enter the variance."
            },
            ro: {
                title: "Erorile standard CML",
                text: "De ce inversa hessienei pseudo-verosimilității copulei nu este o matrice de covarianță validă pentru estimările CML?",
                options: [
                    "Log-verosimilitatea copulei nu este concavă",
                    "Copula estimată este întotdeauna specificată greșit",
                    "Randamentele financiare sînt dependente serial",
                    "Pseudo-observațiile sînt ranguri estimate, ceea ce adaugă un termen de varianță din marginalele empirice (Genest, Ghoudi și Rivest, 1995)"
                ],
                correctExplanation: "Sandwich-ul A⁻¹ΣA⁻¹ adaugă W1(U) + W2(V) la scor; pentru copula Gaussiană S&P 500–Euro Stoxx 50 săptămînală, eroarea standard a lui ρ crește de la 0,0085 la 0,0137.",
                incorrectExplanation: "Problema nu este concavitatea sau dependența serială: marginalele sînt estimate prin ranguri, iar această eroare de estimare trebuie să intre în varianță."
            }
        },
        {
            correct: 0,
            en: {
                title: "Kendall's tau of the t copula",
                text: "For the Student t copula with correlation parameter rho and nu degrees of freedom, Kendall's tau depends on:",
                options: [
                    "rho only: tau = (2/pi) arcsin(rho) for every nu",
                    "nu only",
                    "Both rho and nu",
                    "Neither: tau is always 0.5"
                ],
                correctExplanation: "Kendall's tau is the same for all elliptical copulas with the same ρ, so τ identifies ρ but never ν; ν must come from the likelihood or from the tails.",
                incorrectExplanation: "For elliptical copulas τ = (2/π) arcsin ρ whatever ν is, so ν cannot be recovered from τ."
            },
            ro: {
                title: "Tau Kendall al copulei t",
                text: "Pentru copula Student t cu parametrul de corelație ρ și ν grade de libertate, tau Kendall depinde de:",
                options: [
                    "Doar ρ: τ = (2/π) arcsin ρ pentru orice ν",
                    "Doar ν",
                    "Atît ρ, cît și ν",
                    "De niciunul: τ este întotdeauna 0,5"
                ],
                correctExplanation: "Tau Kendall este același pentru toate copulele eliptice cu același ρ, deci τ identifică ρ, dar niciodată ν; ν vine din verosimilitate sau din cozi.",
                incorrectExplanation: "Pentru copulele eliptice τ = (2/π) arcsin ρ oricare ar fi ν, deci ν nu poate fi recuperat din τ."
            }
        },
        {
            correct: 2,
            en: {
                title: 'Asynchronous trading',
                text: 'The daily SPY–Euro Stoxx 50 correlation is 0.59, the weekly one 0.79. Why the difference?',
                options: [
                    'Weekly returns are always more correlated for any pair of assets',
                    'Daily data contain more crises',
                    'Europe closes before New York, so US news reaches European prices a day later, biasing daily correlation towards zero',
                    'Weekly returns remove the mean'
                ],
                correctExplanation: 'Non-synchronous closes split a common shock across two European days; the lagged daily correlation (0.20) shows the missing part.',
                incorrectExplanation: 'The cause is non-synchronous trading across time zones; lower frequencies or lead–lag terms recover the co-movement.'
            },
            ro: {
                title: 'Tranzacționarea asincronă',
                text: 'Corelația zilnică SPY–Euro Stoxx 50 este 0,59, cea săptămînală 0,79. De ce diferă?',
                options: [
                    'Randamentele săptămînale sînt întotdeauna mai corelate pentru orice pereche de active',
                    'Datele zilnice conțin mai multe crize',
                    'Europa se închide înaintea New York-ului, deci știrile americane ajung în prețurile europene cu o zi întîrziere, iar corelația zilnică este deplasată spre zero',
                    'Randamentele săptămînale elimină media'
                ],
                correctExplanation: 'Închiderile nesincrone împart un șoc comun pe două zile europene; corelația zilnică decalată (0,20) arată partea lipsă.',
                incorrectExplanation: 'Cauza este tranzacționarea nesincronă între fusuri orare; frecvențele mai mici sau termenii decalați recuperează mișcarea comună.'
            }
        },
        {
            correct: 2,
            en: {
                title: "Attainable correlation",
                text: "X = exp(Z) and Y = exp(3Z), with Z following the standard Normal distribution, so X and Y are comonotone lognormal variables. Their Pearson correlation is:",
                options: [
                    "1, because comonotone variables are perfectly correlated",
                    "0, because their variances differ",
                    "About 0.16: (e^3 - 1) / sqrt((e - 1)(e^9 - 1))",
                    "It cannot be computed without data"
                ],
                correctExplanation: "Comonotone variables reach the maximal attainable correlation for their margins, which for these lognormals is only about 0.16: a small ρ does not mean weak dependence (Fréchet–Hoeffding bounds).",
                incorrectExplanation: "Perfect dependence gives ρ = 1 only for linearly related variables; for these margins the maximum is (e³ − 1)/√((e − 1)(e⁹ − 1)) ≈ 0.16."
            },
            ro: {
                title: "Corelația posibilă",
                text: "X = exp(Z) și Y = exp(3Z), cu Z avînd distribuția Normală standard, deci X și Y sînt variabile lognormale comonotone. Corelația lor Pearson este:",
                options: [
                    "1, pentru că variabilele comonotone sînt perfect corelate",
                    "0, pentru că varianțele lor diferă",
                    "Aproximativ 0,16: (e^3 - 1) / sqrt((e - 1)(e^9 - 1))",
                    "Nu se poate calcula fără date"
                ],
                correctExplanation: "Variabilele comonotone ating corelația maximă posibilă pentru marginalele lor, care pentru aceste lognormale este doar circa 0,16: un ρ mic nu înseamnă dependență slabă (marginile Fréchet–Hoeffding).",
                incorrectExplanation: "Dependența perfectă dă ρ = 1 doar pentru variabile legate liniar; pentru aceste marginale maximul este (e³ − 1)/√((e − 1)(e⁹ − 1)) ≈ 0,16."
            }
        },
        {
            correct: 3,
            en: {
                title: 'Curse of dimensionality',
                text: 'Why is the full VEC multivariate GARCH model rarely used for many assets?',
                options: [
                    'It cannot capture volatility clustering',
                    'It assumes constant correlation',
                    'It needs Normal returns',
                    'The number of parameters grows with the fourth power of N and positive definiteness is not guaranteed'
                ],
                correctExplanation: 'With N(N+1)/2 distinct elements, VEC has N(N+1)/2 [1 + N(N+1)] parameters: 21 for N = 2 but over 3 million for N = 50.',
                incorrectExplanation: 'The problem is the explosion of parameters and the lack of guaranteed positive definiteness.'
            },
            ro: {
                title: 'Blestemul dimensionalității',
                text: 'De ce modelul GARCH multivariat VEC complet este rar folosit pentru multe active?',
                options: [
                    'Nu poate surprinde volatility clustering',
                    'Presupune corelație constantă',
                    'Cere randamente cu distribuția Normală',
                    'Numărul de parametri crește cu puterea a patra a lui N, iar caracterul pozitiv definit nu este garantat'
                ],
                correctExplanation: 'Cu N(N+1)/2 elemente distincte, VEC are N(N+1)/2 [1 + N(N+1)] parametri: 21 pentru N = 2, dar peste 3 milioane pentru N = 50.',
                incorrectExplanation: 'Problema este explozia numărului de parametri și lipsa garanției că matricea este pozitiv definită.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'DCC structure',
                text: 'In the DCC model of Engle (2002), H_t = D_t R_t D_t. What drives R_t?',
                options: [
                    'A GARCH-type recursion Q_t = (1-a-b)Qbar + a e e\' + b Q_{t-1} on standardised residuals, rescaled to a correlation matrix',
                    'A rolling window of fixed length',
                    'The VIX index',
                    'It is constant over time'
                ],
                correctExplanation: 'Q_t follows a scalar GARCH-type recursion in the standardised residuals and R_t = diag(Q_t)^{-1/2} Q_t diag(Q_t)^{-1/2}.',
                incorrectExplanation: 'The correlation dynamics come from the Q_t recursion with two parameters a and b.'
            },
            ro: {
                title: 'Structura DCC',
                text: 'În modelul DCC al lui Engle (2002), H_t = D_t R_t D_t. Ce determină R_t?',
                options: [
                    'O recursie de tip GARCH Q_t = (1-a-b)Qbar + a e e\' + b Q_{t-1} pe reziduurile standardizate, rescalată la o matrice de corelație',
                    'O fereastră mobilă de lungime fixă',
                    'Indicele VIX',
                    'Este constantă în timp'
                ],
                correctExplanation: 'Q_t urmează o recursie scalară de tip GARCH în reziduurile standardizate, iar R_t = diag(Q_t)^{-1/2} Q_t diag(Q_t)^{-1/2}.',
                incorrectExplanation: 'Dinamica corelațiilor vine din recursia lui Q_t, cu doi parametri a și b.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Two-step estimation',
                text: 'What is a known weakness of the standard errors from the second step of DCC estimation?',
                options: [
                    'They are too large because the first step is efficient',
                    'They are exact in finite samples',
                    'They ignore the estimation error of the first-step GARCH models, so they are too small',
                    'They require Normal residuals to be consistent'
                ],
                correctExplanation: 'Step 2 treats the GARCH volatilities as known; the extra uncertainty from step 1 is ignored.',
                incorrectExplanation: 'The second-step standard errors ignore first-step estimation error and are therefore too small.'
            },
            ro: {
                title: 'Estimarea în doi pași',
                text: 'Care este o slăbiciune cunoscută a erorilor standard din pasul al doilea al estimării DCC?',
                options: [
                    'Sînt prea mari, pentru că primul pas este eficient',
                    'Sînt exacte în eșantioane finite',
                    'Ignoră eroarea de estimare a modelelor GARCH din primul pas, deci sînt prea mici',
                    'Cer reziduuri cu distribuția Normală pentru a fi consistente'
                ],
                correctExplanation: 'Pasul 2 tratează volatilitățile GARCH ca fiind cunoscute; incertitudinea suplimentară din pasul 1 este ignorată.',
                incorrectExplanation: 'Erorile standard din pasul 2 ignoră eroarea din pasul 1 și sînt deci prea mici.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'DCC persistence',
                text: 'For SPY–TLT the DCC estimates are a = 0.052, b = 0.934. What is the approximate half-life of a shock to the DCC recursion Q_t?',
                options: [
                    'About 1 day',
                    'About 48 days',
                    'About 1 year',
                    'Infinite'
                ],
                correctExplanation: 'Half-life ≈ ln 0.5 / ln(a + b) = ln 0.5 / ln 0.986 ≈ 48 trading days; only approximate for the standard DCC, because E[ε_t ε_t′ | past] = R_t, not Q_t.',
                incorrectExplanation: 'Use ln 0.5 / ln(a + b) with a + b close to but below 1.'
            },
            ro: {
                title: 'Persistența DCC',
                text: 'Pentru SPY–TLT estimările DCC sînt a = 0,052, b = 0,934. Care este timpul de înjumătățire aproximativ al unui șoc asupra recursiei DCC Q_t?',
                options: [
                    'Aproximativ 1 zi',
                    'Aproximativ 48 de zile',
                    'Aproximativ 1 an',
                    'Infinit'
                ],
                correctExplanation: 'Timpul de înjumătățire ≈ ln 0,5 / ln(a + b) = ln 0,5 / ln 0,986 ≈ 48 de zile de tranzacționare; doar aproximativ pentru DCC-ul standard, deoarece E[ε_t ε_t′ | trecut] = R_t, nu Q_t.',
                incorrectExplanation: 'Folosiți ln 0,5 / ln(a + b), cu a + b aproape de 1, dar sub 1.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Testing CCC against DCC',
                text: 'Why is the chi-squared distribution only indicative for the likelihood ratio of CCC (a = 0) against DCC?',
                options: [
                    'Because the likelihood is not Gaussian',
                    'Because the sample is too large',
                    'Because the test has two parameters',
                    'Because under a = 0 the parameter b is not identified (a Davies-type problem)'
                ],
                correctExplanation: 'When a = 0, b drops out of the model; standard asymptotics fail and the chi-squared reference is only a rough guide.',
                incorrectExplanation: 'The nuisance parameter b is unidentified under the null, which breaks the standard chi-squared asymptotics.'
            },
            ro: {
                title: 'Testul CCC față de DCC',
                text: 'De ce distribuția hi-pătrat este doar orientativă pentru raportul de verosimilitate CCC (a = 0) față de DCC?',
                options: [
                    'Pentru că verosimilitatea nu este Gaussiană',
                    'Pentru că eșantionul este prea mare',
                    'Pentru că testul are doi parametri',
                    'Pentru că sub a = 0 parametrul b nu este identificat (o problemă de tip Davies)'
                ],
                correctExplanation: 'Cînd a = 0, b dispare din model; asimptotica standard nu mai funcționează, iar referința hi-pătrat este doar un ghid aproximativ.',
                incorrectExplanation: 'Parametrul perturbator b nu este identificat sub ipoteza nulă, ceea ce strică asimptotica hi-pătrat standard.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Bitcoin and equities',
                text: 'The average DCC correlation of Bitcoin and SPY was 0.04 before 2020 and 0.31 after. What does this imply?',
                options: [
                    'Bitcoin lost much of its diversification value for equity investors after 2020',
                    'Bitcoin became a hedge against equity crashes',
                    'The correlation is constant, so nothing changed',
                    'Bitcoin and equities became perfectly correlated'
                ],
                correctExplanation: 'A move from about zero to a clearly positive correlation means Bitcoin behaves more like a risk asset in equity portfolios.',
                incorrectExplanation: 'The correlation rose from about zero to clearly positive, which reduces diversification benefits.'
            },
            ro: {
                title: 'Bitcoin și acțiunile',
                text: 'Corelația DCC medie dintre Bitcoin și SPY a fost 0,04 înainte de 2020 și 0,31 după. Ce implică acest lucru?',
                options: [
                    'Bitcoin și-a pierdut mare parte din valoarea de diversificare pentru investitorii în acțiuni după 2020',
                    'Bitcoin a devenit un hedge împotriva crahurilor bursiere',
                    'Corelația este constantă, deci nu s-a schimbat nimic',
                    'Bitcoin și acțiunile au devenit perfect corelate'
                ],
                correctExplanation: 'Trecerea de la o corelație aproape nulă la una clar pozitivă înseamnă că Bitcoin se comportă mai mult ca un activ de risc în portofoliile de acțiuni.',
                incorrectExplanation: 'Corelația a crescut de la aproape zero la clar pozitivă, ceea ce reduce beneficiile diversificării.'
            }
        },
        {
            correct: 1,
            en: {
                title: "Forbes–Rigobon with a common shock",
                text: "In a crisis a global shock raises both the variance of the source market and the idiosyncratic variance of the target market. The Forbes–Rigobon adjusted correlation then:",
                options: [
                    "Is unbiased, because the adjustment uses the variance ratio",
                    "Over-corrects, biasing the test towards \"no contagion\" (Corsetti, Pericoli and Sbracia, 2005)",
                    "Under-corrects, biasing the test towards contagion",
                    "Becomes negative by construction"
                ],
                correctExplanation: "The adjustment assumes a constant idiosyncratic variance; a common shock inflates the variance ratio and removes too much of the rise in correlation, so true contagion can be hidden.",
                incorrectExplanation: "With a common shock the no-omitted-factor assumption fails and the adjustment removes too much of the rise in correlation."
            },
            ro: {
                title: "Forbes–Rigobon cu un șoc comun",
                text: "Într-o criză, un șoc global crește atît varianța pieței-sursă, cît și varianța idiosincratică a pieței-țintă. Corelația corectată Forbes–Rigobon atunci:",
                options: [
                    "Este nedeplasată, pentru că corecția folosește raportul varianțelor",
                    "Corectează excesiv, deplasînd testul spre „nicio contagiune” (Corsetti, Pericoli și Sbracia, 2005)",
                    "Corectează insuficient, deplasînd testul spre contagiune",
                    "Devine negativă prin construcție"
                ],
                correctExplanation: "Corecția presupune o varianță idiosincratică constantă; un șoc comun exagerează raportul varianțelor și elimină prea mult din creșterea corelației, deci contagiunea reală poate fi ascunsă.",
                incorrectExplanation: "Cu un șoc comun, ipoteza „niciun factor omis” cade, iar corecția elimină prea mult din creșterea corelației."
            }
        },
        {
            correct: 2,
            en: {
                title: 'Adjusted correlation',
                text: 'A crisis correlation is 0.60 and the source-market variance quadrupled (delta = 3). What is the Forbes–Rigobon adjusted correlation?',
                options: [
                    '0.60',
                    '0.80',
                    'About 0.35',
                    '0.15'
                ],
                correctExplanation: 'ρ* = 0.60 / sqrt(1 + 3 × (1 − 0.36)) = 0.60 / sqrt(2.92) ≈ 0.351.',
                incorrectExplanation: 'Apply ρ* = ρc / sqrt(1 + δ(1 − ρc²)) with δ = 3.'
            },
            ro: {
                title: 'Corelația corectată',
                text: 'O corelație de criză este 0,60, iar varianța pieței-sursă s-a multiplicat de 4 ori (δ = 3). Care este corelația corectată Forbes–Rigobon?',
                options: [
                    '0,60',
                    '0,80',
                    'Aproximativ 0,35',
                    '0,15'
                ],
                correctExplanation: 'ρ* = 0,60 / sqrt(1 + 3 × (1 − 0,36)) = 0,60 / sqrt(2,92) ≈ 0,351.',
                incorrectExplanation: 'Aplicați ρ* = ρc / sqrt(1 + δ(1 − ρc²)) cu δ = 3.'
            }
        },
        {
            correct: 0,
            en: {
                title: '2008 test',
                text: 'In 2008 the BET–S&P 500 correlation of 2-day returns rose from 0.22 to 0.48; the adjusted value is 0.20. The best reading is:',
                options: [
                    'The raw increase is explained by the volatility of the S&P 500; there is no evidence of contagion once adjusted, under strong assumptions',
                    'Strong contagion, significant after adjustment',
                    'The BET decoupled from the US in 2008',
                    'The adjustment proves that no common shock occurred'
                ],
                correctExplanation: 'The adjusted correlation is close to the calm-year value; the conclusion relies on assumptions such as no common shocks.',
                incorrectExplanation: 'After adjustment the increase disappears, but the test assumes no omitted common shock and has low power.'
            },
            ro: {
                title: 'Testul pentru 2008',
                text: 'În 2008 corelația randamentelor pe 2 zile BET–S&P 500 a crescut de la 0,22 la 0,48; valoarea corectată este 0,20. Cea mai bună interpretare este:',
                options: [
                    'Creșterea brută se explică prin volatilitatea S&P 500; după corecție nu există dovezi de contagiune, sub ipoteze puternice',
                    'Contagiune puternică, semnificativă după corecție',
                    'BET s-a decuplat de SUA în 2008',
                    'Corecția dovedește că nu a existat niciun șoc comun'
                ],
                correctExplanation: 'Corelația corectată este apropiată de valoarea din anul calm; concluzia se bazează pe ipoteze precum absența șocurilor comune.',
                incorrectExplanation: 'După corecție creșterea dispare, dar testul presupune că nu există un șoc comun omis și are putere mică.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Exceedance correlation',
                text: 'For a bivariate Normal distribution, what happens to the exceedance correlation as the threshold moves into the tails?',
                options: [
                    'It rises to 1',
                    'It stays equal to rho',
                    'It becomes negative',
                    'It falls towards 0'
                ],
                correctExplanation: 'Normal extremes are asymptotically independent; the data show far higher values (e.g. 0.80 for joint losses at q = 0.10 versus 0.41 under normality).',
                incorrectExplanation: 'Under normality, conditioning on extremes drives the correlation towards zero.'
            },
            ro: {
                title: 'Corelația de depășire',
                text: 'Pentru distribuția Normală bivariată, ce se întîmplă cu corelația de depășire cînd pragul se mută spre cozi?',
                options: [
                    'Crește spre 1',
                    'Rămîne egală cu ρ',
                    'Devine negativă',
                    'Scade spre 0'
                ],
                correctExplanation: 'Extremele Normale sînt asimptotic independente; datele arată valori mult mai mari (de exemplu 0,80 pentru pierderi comune la q = 0,10, față de 0,41 sub normalitate).',
                incorrectExplanation: 'Sub normalitate, condiționarea pe extreme duce corelația spre zero.'
            }
        },
        {
            correct: 3,
            en: {
                title: "Standard error of a correlation",
                text: "For daily returns with fat tails and volatility clustering, the Fisher interval tanh(z ± 1.96/sqrt(T − 3)) for a correlation is typically:",
                options: [
                    "Exact for any T",
                    "Too wide, hence conservative",
                    "Valid once T exceeds 250",
                    "Too narrow: the variance of the correlation depends on fourth moments and on the serial dependence of the cross-products"
                ],
                correctExplanation: "For SPY–TLT in 2002–2021 the delta-method HAC standard error was 0.0227 against 0.0120 from the Fisher formula, about 1.9 times larger.",
                incorrectExplanation: "The Fisher formula assumes i.i.d. pairs with the Normal distribution; fat tails and GARCH make the true variance larger, so the Fisher band is too narrow."
            },
            ro: {
                title: "Eroarea standard a unei corelații",
                text: "Pentru randamente zilnice cu cozi groase și volatility clustering, intervalul Fisher tanh(z ± 1,96/sqrt(T − 3)) pentru o corelație este de regulă:",
                options: [
                    "Exact pentru orice T",
                    "Prea larg, deci conservator",
                    "Valid cînd T depășește 250",
                    "Prea îngust: varianța corelației depinde de momentele de ordinul patru și de dependența serială a produselor încrucișate"
                ],
                correctExplanation: "Pentru SPY–TLT în 2002–2021, eroarea standard HAC prin metoda delta a fost 0,0227, față de 0,0120 din formula Fisher, de circa 1,9 ori mai mare.",
                incorrectExplanation: "Formula Fisher presupune perechi i.i.d. cu distribuția Normală; cozile groase și GARCH fac varianța reală mai mare, deci banda Fisher este prea îngustă."
            }
        },
        {
            correct: 0,
            en: {
                title: "A break date chosen by eye",
                text: "You pick January 2022 from a chart of the rolling correlation and then test for a change in correlation at that date with a Fisher z test. The test is:",
                options: [
                    "Oversized: the date was chosen from the data; use an unknown-date test such as Wied, Krämer and Dehling (2012)",
                    "Exactly sized, because the date is fixed before the statistic is computed",
                    "Undersized, because the chart smooths the data",
                    "Valid whenever the sample is large"
                ],
                correctExplanation: "A date chosen after looking at the data is itself random, so the null distribution of the statistic depends on the selection rule and Normal critical values reject too often; an unknown-date test such as Wied, Krämer and Dehling (2012) is defined with its own Brownian-bridge limit. On the SPY–TLT residuals it puts the break in August 2020, not January 2022.",
                incorrectExplanation: "A date selected from the data makes the null distribution depend on how the date was chosen, so Normal critical values reject too often."
            },
            ro: {
                title: "O dată de ruptură aleasă din ochi",
                text: "Alegeți ianuarie 2022 de pe graficul corelației mobile și apoi testați o schimbare a corelației la acea dată cu un test Fisher z. Testul este:",
                options: [
                    "Cu nivel real prea mare: data a fost aleasă din date; folosiți un test cu dată necunoscută, precum Wied, Krämer și Dehling (2012)",
                    "Cu nivel exact, pentru că data este fixată înainte de calculul statisticii",
                    "Cu nivel real prea mic, pentru că graficul netezește datele",
                    "Valid oricînd eșantionul este mare"
                ],
                correctExplanation: "O dată aleasă după ce am văzut datele este ea însăși aleatoare, deci distribuția statisticii sub ipoteza nulă depinde de regula de alegere, iar valorile critice Normale resping prea des; un test cu dată necunoscută, precum Wied, Krämer și Dehling (2012), este definit cu propria limită de tip punte browniană. Pe reziduurile SPY–TLT el plasează ruptura în august 2020, nu în ianuarie 2022.",
                incorrectExplanation: "O dată aleasă din date face ca distribuția sub ipoteza nulă să depindă de modul de alegere a datei, deci valorile critice Normale resping prea des."
            }
        },
        {
            correct: 3,
            en: {
                title: 'Gaussian vs t',
                text: 'Two copulas have the same rho = 0.5: Gaussian and Student t with nu = 4. Which statement is correct?',
                options: [
                    'Both have zero tail dependence',
                    'Both have the same tail dependence of 0.5',
                    'The Gaussian has more tail dependence',
                    'The t copula has tail dependence of about 0.25, the Gaussian has none'
                ],
                correctExplanation: 'λ = 2 t5(−sqrt(5 × 0.5/1.5)) ≈ 0.253 for the t copula; the Gaussian copula has λ = 0 for |ρ| < 1.',
                incorrectExplanation: 'The t copula has positive tail dependence; the Gaussian copula has none.'
            },
            ro: {
                title: 'Gaussiană vs t',
                text: 'Două copule au același ρ = 0,5: Gaussiana și Student t cu ν = 4. Care afirmație este corectă?',
                options: [
                    'Ambele au dependență zero în cozi',
                    'Ambele au aceeași dependență în cozi, 0,5',
                    'Gaussiana are mai multă dependență în cozi',
                    'Copula t are dependență în cozi de circa 0,25, Gaussiana nu are'
                ],
                correctExplanation: 'λ = 2 t5(−sqrt(5 × 0,5/1,5)) ≈ 0,253 pentru copula t; copula Gaussiană are λ = 0 pentru |ρ| < 1.',
                incorrectExplanation: 'Copula t are dependență pozitivă în cozi; copula Gaussiană nu are.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Goodness of fit',
                text: 'For JPM–BAC (T = 4202), all five static copulas are rejected by the Rosenblatt test, although the t copula has by far the best AIC. The most sensible conclusion is:',
                options: [
                    'The t copula is useless',
                    'The test is wrong',
                    'With thousands of observations even small misfits are detected; a static copula may also miss time-varying dependence',
                    'AIC and goodness-of-fit tests always agree'
                ],
                correctExplanation: 'Large samples give high power against small departures; time-varying dependence is one candidate (a dynamic t copula fits JPM–BAC far better). AIC ranks models, the test checks absolute fit.',
                incorrectExplanation: 'Rejection reflects high power against some misfit, not that the best model is useless.'
            },
            ro: {
                title: 'Adecvarea',
                text: 'Pentru JPM–BAC (T = 4202), toate cele cinci copule statice sînt respinse de testul Rosenblatt, deși copula t are de departe cel mai bun AIC. Concluzia cea mai rezonabilă este:',
                options: [
                    'Copula t este inutilă',
                    'Testul este greșit',
                    'Cu mii de observații sînt detectate și abateri mici; o copulă statică poate rata și dependența variabilă în timp',
                    'AIC și testele de adecvare coincid întotdeauna'
                ],
                correctExplanation: 'Eșantioanele mari dau putere mare împotriva abaterilor mici; dependența variabilă în timp este o explicație posibilă (o copulă t dinamică se potrivește mult mai bine pentru JPM–BAC). AIC ordonează modelele, testul verifică adecvarea absolută.',
                incorrectExplanation: 'Respingerea reflectă puterea mare împotriva unei abateri, nu faptul că cel mai bun model ar fi inutil.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Joint losses',
                text: 'For daily BET and Euro Stoxx 50 losses (L = −returns), Gumbel is not rejected (p = 0.23) while Clayton is (p = 0.005). Why?',
                options: [
                    'Joint crashes sit in the upper corner of the loss copula, where Gumbel has tail dependence and Clayton has none',
                    'Clayton cannot be estimated on losses',
                    'Gumbel is always better than Clayton',
                    'Losses are independent'
                ],
                correctExplanation: 'Gumbel on losses captures joint crashes (λU = 0.26); Clayton puts dependence in the joint-gain corner.',
                incorrectExplanation: 'The loss upper tail contains the joint crashes; only Gumbel puts dependence there.'
            },
            ro: {
                title: 'Pierderi comune',
                text: 'Pentru pierderile zilnice BET și Euro Stoxx 50 (L = −randamente), Gumbel nu este respinsă (p = 0,23), iar Clayton este (p = 0,005). De ce?',
                options: [
                    'Crahurile comune se află în upper tail-ul copulei pierderilor, unde Gumbel are dependență în cozi, iar Clayton nu',
                    'Clayton nu poate fi estimată pe pierderi',
                    'Gumbel este întotdeauna mai bună decît Clayton',
                    'Pierderile sînt independente'
                ],
                correctExplanation: 'Gumbel pe pierderi surprinde crahurile comune (λU = 0,26); Clayton plasează dependența în coada cîștigurilor comune.',
                incorrectExplanation: 'Coada superioară a pierderilor conține crahurile comune; doar Gumbel plasează dependența acolo.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Gaussian copula and 2008',
                text: 'Why is the Gaussian copula of Li (2000) often blamed in accounts of the 2008 credit crisis?',
                options: [
                    'It overstated tail dependence',
                    'It has zero asymptotic tail dependence and, calibrated with one static correlation, understated the probability of many extreme defaults at once',
                    'It could not be calibrated',
                    'It used Kendall\'s tau'
                ],
                correctExplanation: 'Joint defaults were not impossible in the model (at a finite default probability they still occur), but with λ = 0 and one static correlation calibrated in calm years it gave lower probabilities of many extreme defaults than tail-dependent models.',
                incorrectExplanation: 'The problem was zero asymptotic tail dependence combined with a static calibration, not an impossibility of joint defaults.'
            },
            ro: {
                title: 'Copula Gaussiană și 2008',
                text: 'De ce este adesea învinuită copula Gaussiană a lui Li (2000) în relatările despre criza creditelor din 2008?',
                options: [
                    'A supraestimat dependența în cozi',
                    'Are dependență asimptotică zero în cozi și, calibrată cu o singură corelație statică, subestima probabilitatea multor falimente extreme simultane',
                    'Nu putea fi calibrată',
                    'Folosea tau al lui Kendall'
                ],
                correctExplanation: 'Falimentele comune nu erau imposibile în model (la o probabilitate de faliment finită ele apar), dar cu λ = 0 și o singură corelație statică, calibrată în anii calmi, modelul dădea probabilități ale multor falimente extreme mai mici decît modelele cu dependență în cozi.',
                incorrectExplanation: 'Problema a fost dependența asimptotică zero în cozi combinată cu o calibrare statică, nu imposibilitatea falimentelor comune.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Bank network',
                text: 'In the minimum spanning tree of six banks (weekly returns 2010–2026), how are the Romanian banks attached to the rest?',
                options: [
                    'Through JPM',
                    'They are not attached',
                    'Through Deutsche Bank only, with the highest correlation of the tree',
                    'Through the BNP–BRD link, one of the weakest edges (0.35)'
                ],
                correctExplanation: 'The tree links TLV and BRD (0.65) and attaches them to the euro area through BNP–BRD (0.35): Romanian banks are the least connected.',
                incorrectExplanation: 'The Romanian block is attached through BNP–BRD, a weak link.'
            },
            ro: {
                title: 'Rețeaua băncilor',
                text: 'În arborele de acoperire minimă al celor șase bănci (randamente săptămînale 2010–2026), cum sînt legate băncile românești de celelalte?',
                options: [
                    'Prin JPM',
                    'Nu sînt legate',
                    'Doar prin Deutsche Bank, cu cea mai mare corelație din arbore',
                    'Prin legătura BNP–BRD, una dintre cele mai slabe muchii (0,35)'
                ],
                correctExplanation: 'Arborele leagă TLV și BRD (0,65) și le atașează zonei euro prin BNP–BRD (0,35): băncile românești sînt cele mai puțin conectate.',
                incorrectExplanation: 'Blocul românesc este legat prin BNP–BRD, o legătură slabă.'
            }
        },
        {
            correct: 2,
            en: {
                title: 'Integration after 2020',
                text: 'The weekly BET–Euro Stoxx 50 correlation rose from 0.45 (2010–2019) to 0.62 (2020–2026), with a 95% bootstrap interval for the change of [-0.05, 0.34]. What is the fairest conclusion?',
                options: [
                    'Strong, significant integration',
                    'Romania decoupled from the euro area',
                    'Modest, fragile evidence: the interval includes zero and the rise is concentrated in crisis years',
                    'The correlation did not change at all'
                ],
                correctExplanation: 'The point estimate rises, but the interval includes zero, excluding the 2020 crash weeks lowers it, and lower-tail dependence did not increase.',
                incorrectExplanation: 'The change is not significant at 5% and depends on crisis weeks.'
            },
            ro: {
                title: 'Integrarea după 2020',
                text: 'Corelația săptămînală BET–Euro Stoxx 50 a crescut de la 0,45 (2010–2019) la 0,62 (2020–2026), cu un interval bootstrap de 95% pentru schimbare de [-0,05; 0,34]. Care este concluzia cea mai corectă?',
                options: [
                    'Integrare puternică și semnificativă',
                    'România s-a decuplat de zona euro',
                    'Dovezi modeste și fragile: intervalul conține zero, iar creșterea este concentrată în anii de criză',
                    'Corelația nu s-a schimbat deloc'
                ],
                correctExplanation: 'Estimarea punctuală crește, dar intervalul conține zero, excluderea săptămînilor crahului din 2020 o reduce, iar dependența în coada inferioară nu a crescut.',
                incorrectExplanation: 'Schimbarea nu este semnificativă la 5% și depinde de săptămînile de criză.'
            }
        },
        {
            correct: 2,
            en: {
                title: "Spot the error: Gaussian copula tails",
                text: "An AI assistant writes: \"A Gaussian copula with correlation rho = 0.7 has lower tail dependence lambda_L = rho^2 = 0.49, so it captures joint crashes well.\" What is the error?",
                options: [
                    "The lower tail dependence of the Gaussian copula is rho, not rho^2",
                    "The Gaussian copula has upper but not lower tail dependence",
                    "For any rho < 1 the Gaussian copula has zero (asymptotic) tail dependence, so lambda_L = rho^2 is wrong",
                    "Tail dependence can only be computed for Archimedean copulas"
                ],
                correctExplanation: "The Gaussian copula is asymptotically independent in both tails: lambda_L = lambda_U = 0 for rho < 1. Joint extremes at a fixed threshold still occur (for rho = 0.7, P(V ≤ 0.01 | U ≤ 0.01) ≈ 0.27), but positive limiting tail dependence needs e.g. a t copula (symmetric) or a Clayton copula (lower tail).",
                incorrectExplanation: "No positive formula in rho is correct here: the Gaussian copula has lambda_L = lambda_U = 0 for every rho < 1, so joint crashes become asymptotically independent."
            },
            ro: {
                title: "Găsiți eroarea: cozile copulei Gaussiene",
                text: "Un asistent AI scrie: „O copulă Gaussiană cu corelația rho = 0,7 are dependența în coada inferioară lambda_L = rho^2 = 0,49, deci surprinde bine crahurile comune.” Care este eroarea?",
                options: [
                    "Dependența în coada inferioară a copulei Gaussiene este rho, nu rho^2",
                    "Copula Gaussiană are dependență în coada superioară, dar nu și în cea inferioară",
                    "Pentru orice rho < 1 copula Gaussiană are dependență (asimptotică) zero în cozi, deci lambda_L = rho^2 este greșit",
                    "Dependența în cozi se poate calcula doar pentru copulele arhimediene"
                ],
                correctExplanation: "Copula Gaussiană este asimptotic independentă în ambele cozi: lambda_L = lambda_U = 0 pentru rho < 1. Extremele comune la un prag fixat apar totuși (pentru rho = 0,7, P(V ≤ 0,01 | U ≤ 0,01) ≈ 0,27), dar o dependență în cozi pozitivă la limită cere de exemplu o copulă t (simetrică) sau o copulă Clayton (coada inferioară).",
                incorrectExplanation: "Nicio formulă pozitivă în rho nu este corectă aici: copula Gaussiană are lambda_L = lambda_U = 0 pentru orice rho < 1, deci crahurile comune devin asimptotic independente."
            }
        },
        {
            correct: 0,
            en: {
                title: "Spot the error: from Kendall's tau to rho",
                text: "An AI assistant writes: \"Kendall's tau between the two return series is 0.4, so the correlation parameter of the t copula is rho = 2 sin(pi tau / 6) = 0.416.\" What is the error?",
                options: [
                    "For elliptical copulas rho = sin(pi tau / 2) = 0.588; the formula used is the Gaussian link for Spearman's rho",
                    "For elliptical copulas rho = tau, so rho = 0.4",
                    "The t copula has no correlation parameter, only degrees of freedom",
                    "Kendall's tau must first be converted to Pearson correlation of the raw returns"
                ],
                correctExplanation: "For the Gaussian and t copulas, tau = (2/pi) arcsin(rho), so rho = sin(pi tau / 2) = sin(0.2 pi) = 0.588. The relation rho = 2 sin(pi rho_S / 6) links the Gaussian copula to Spearman's rho_S, not to Kendall's tau.",
                incorrectExplanation: "The inversion for Kendall's tau is rho = sin(pi tau / 2), which gives 0.588; 2 sin(pi x / 6) is the Spearman relation."
            },
            ro: {
                title: "Găsiți eroarea: de la tau Kendall la rho",
                text: "Un asistent AI scrie: „Tau Kendall între cele două serii de randamente este 0,4, deci parametrul de corelație al copulei t este rho = 2 sin(pi tau / 6) = 0,416.” Care este eroarea?",
                options: [
                    "Pentru copulele eliptice rho = sin(pi tau / 2) = 0,588; formula folosită este legătura Gaussiană pentru rho Spearman",
                    "Pentru copulele eliptice rho = tau, deci rho = 0,4",
                    "Copula t nu are parametru de corelație, doar grade de libertate",
                    "Tau Kendall trebuie întîi transformat în corelația Pearson a randamentelor brute"
                ],
                correctExplanation: "Pentru copulele Gaussiană și t, tau = (2/pi) arcsin(rho), deci rho = sin(pi tau / 2) = sin(0,2 pi) = 0,588. Relația rho = 2 sin(pi rho_S / 6) leagă copula Gaussiană de rho_S Spearman, nu de tau Kendall.",
                incorrectExplanation: "Inversarea pentru tau Kendall este rho = sin(pi tau / 2), care dă 0,588; 2 sin(pi x / 6) este relația pentru Spearman."
            }
        }
    ]
};

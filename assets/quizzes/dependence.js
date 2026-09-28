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
            correct: 2,
            en: {
                title: 'Portfolio variance',
                text: 'For two assets with weights w and 1-w, which term of the portfolio variance depends on the correlation?',
                options: [
                    'w squared times the variance of asset 1',
                    '(1-w) squared times the variance of asset 2',
                    '2w(1-w) rho sigma1 sigma2',
                    'None: correlation affects only expected returns'
                ],
                correctExplanation: 'The cross term 2w(1-w)ρσ1σ2 carries the correlation; it is what makes diversification work when ρ < 1.',
                incorrectExplanation: 'Only the cross term contains ρ; the two variance terms do not depend on it.'
            },
            ro: {
                title: 'Varianța portofoliului',
                text: 'Pentru două active cu ponderile w și 1-w, ce termen al varianței portofoliului depinde de corelație?',
                options: [
                    'w la pătrat înmulțit cu varianța activului 1',
                    '(1-w) la pătrat înmulțit cu varianța activului 2',
                    '2w(1-w) ρ σ1 σ2',
                    'Niciunul: corelația afectează doar randamentele așteptate'
                ],
                correctExplanation: 'Termenul încrucișat 2w(1-w)ρσ1σ2 conține corelația; el face ca diversificarea să funcționeze când ρ < 1.',
                incorrectExplanation: 'Doar termenul încrucișat conține ρ; termenii de varianță nu depind de el.'
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
                text: 'Corelația zilnică SPY–TLT a fost -0,40 în 2002–2021 și 0,11 din 2022. Ce s-a întâmplat cu un portofoliu 60/40?',
                options: [
                    'Volatilitatea lui a crescut de la circa 10,4% la 13,2%, chiar cu volatilitățile activelor neschimbate',
                    'Volatilitatea a scăzut, pentru că o corelație pozitivă reduce întotdeauna riscul',
                    'Nimic: corelația nu intră în volatilitatea portofoliului',
                    'A devenit fără risc'
                ],
                correctExplanation: 'Cu aceleași volatilități ale activelor, trecerea de la o corelație negativă la una ușor pozitivă crește volatilitatea portofoliului 60/40: obligațiunile nu mai acoperă riscul acțiunilor.',
                incorrectExplanation: 'O corelație mai mare crește termenul încrucișat și deci volatilitatea portofoliului.'
            }
        },
        {
            correct: 3,
            en: {
                title: 'Hedge ratio',
                text: 'What is the minimum-variance hedge ratio when hedging asset S with instrument F?',
                options: [
                    'sigma_S / sigma_F',
                    'rho squared',
                    '1, always',
                    'rho sigma_S / sigma_F, the slope of r_S on r_F'
                ],
                correctExplanation: 'Minimising Var(r_S - h r_F) gives h* = Cov(r_S, r_F)/Var(r_F) = ρσS/σF, the regression slope; ρ² is the share of variance removed.',
                incorrectExplanation: 'The optimal hedge ratio is the regression slope ρσS/σF; ρ² measures hedge effectiveness, not the ratio.'
            },
            ro: {
                title: 'Raportul de acoperire',
                text: 'Care este raportul de acoperire de varianță minimă când acoperim activul S cu instrumentul F?',
                options: [
                    'σS / σF',
                    'ρ la pătrat',
                    '1, întotdeauna',
                    'ρ σS / σF, panta regresiei lui r_S pe r_F'
                ],
                correctExplanation: 'Minimizarea lui Var(r_S - h r_F) dă h* = Cov(r_S, r_F)/Var(r_F) = ρσS/σF, panta regresiei; ρ² este proporția de varianță eliminată.',
                incorrectExplanation: 'Raportul optim este panta regresiei ρσS/σF; ρ² măsoară eficiența acoperirii, nu raportul.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'EWMA recursion',
                text: 'In the RiskMetrics EWMA covariance with lambda = 0.94, what is the half-life of a shock?',
                options: [
                    '0.94 days',
                    'About 11 days',
                    'About 250 days',
                    'Infinite, because EWMA never forgets'
                ],
                correctExplanation: 'Weights decay as λ^k, so the half-life is ln 0.5 / ln λ ≈ 11.2 days for λ = 0.94.',
                incorrectExplanation: 'The half-life is ln 0.5 / ln λ, about 11 days for λ = 0.94.'
            },
            ro: {
                title: 'Recursia EWMA',
                text: 'În covarianța EWMA RiskMetrics cu λ = 0,94, care este timpul de înjumătățire al unui șoc?',
                options: [
                    '0,94 zile',
                    'Aproximativ 11 zile',
                    'Aproximativ 250 de zile',
                    'Infinit, pentru că EWMA nu uită niciodată'
                ],
                correctExplanation: 'Ponderile scad ca λ^k, deci timpul de înjumătățire este ln 0,5 / ln λ ≈ 11,2 zile pentru λ = 0,94.',
                incorrectExplanation: 'Timpul de înjumătățire este ln 0,5 / ln λ, circa 11 zile pentru λ = 0,94.'
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
                text: 'Corelația zilnică SPY–Euro Stoxx 50 este 0,59, cea săptămânală 0,79. De ce diferă?',
                options: [
                    'Randamentele săptămânale sunt întotdeauna mai corelate pentru orice pereche de active',
                    'Datele zilnice conțin mai multe crize',
                    'Europa se închide înaintea New York-ului, deci știrile americane ajung în prețurile europene cu o zi întârziere, iar corelația zilnică este deplasată spre zero',
                    'Randamentele săptămânale elimină media'
                ],
                correctExplanation: 'Închiderile nesincrone împart un șoc comun pe două zile europene; corelația zilnică decalată (0,20) arată partea lipsă.',
                incorrectExplanation: 'Cauza este tranzacționarea nesincronă între fusuri orare; frecvențele mai mici sau termenii decalați recuperează mișcarea comună.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Joining series',
                text: 'When computing the correlation of Bitcoin (7 days a week) and SPY (weekdays), what is the correct order of operations?',
                options: [
                    'Compute returns on each calendar, then join the returns',
                    'Join the prices on common days, then compute returns',
                    'Fill SPY weekends with Friday prices and use all 7 days',
                    'Drop Mondays'
                ],
                correctExplanation: 'Joining prices first makes each Monday return include the Bitcoin weekend move, matching the SPY Friday-to-Monday return.',
                incorrectExplanation: 'Returns computed before joining would pair a Sunday-to-Monday Bitcoin return with a Friday-to-Monday SPY return.'
            },
            ro: {
                title: 'Unirea seriilor',
                text: 'Când calculăm corelația dintre Bitcoin (7 zile din 7) și SPY (zile lucrătoare), care este ordinea corectă a operațiilor?',
                options: [
                    'Calculăm randamentele pe fiecare calendar, apoi unim randamentele',
                    'Unim prețurile în zilele comune, apoi calculăm randamentele',
                    'Completăm weekendurile SPY cu prețul de vineri și folosim toate cele 7 zile',
                    'Eliminăm zilele de luni'
                ],
                correctExplanation: 'Unirea întâi a prețurilor face ca fiecare randament de luni să includă mișcarea Bitcoin din weekend, la fel ca randamentul SPY de vineri la luni.',
                incorrectExplanation: 'Randamentele calculate înainte de unire ar împerechea un randament Bitcoin duminică–luni cu un randament SPY vineri–luni.'
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
                    'Nu poate surprinde gruparea volatilității',
                    'Presupune corelație constantă',
                    'Cere randamente cu distribuția Normală',
                    'Numărul de parametri crește cu puterea a patra a lui N, iar pozitiv definirea nu este garantată'
                ],
                correctExplanation: 'Cu N(N+1)/2 elemente distincte, VEC are N(N+1)/2 [1 + N(N+1)] parametri: 21 pentru N = 2, dar peste 3 milioane pentru N = 50.',
                incorrectExplanation: 'Problema este explozia numărului de parametri și lipsa garanției de pozitiv definire.'
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
                    'Sunt prea mari, pentru că primul pas este eficient',
                    'Sunt exacte în eșantioane finite',
                    'Ignoră eroarea de estimare a modelelor GARCH din primul pas, deci sunt prea mici',
                    'Cer reziduuri cu distribuția Normală pentru a fi consistente'
                ],
                correctExplanation: 'Pasul 2 tratează volatilitățile GARCH ca fiind cunoscute; incertitudinea suplimentară din pasul 1 este ignorată.',
                incorrectExplanation: 'Erorile standard din pasul 2 ignoră eroarea din pasul 1 și sunt deci prea mici.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'DCC persistence',
                text: 'For SPY–TLT the DCC estimates are a = 0.053, b = 0.933. What is the half-life of a correlation shock?',
                options: [
                    'About 1 day',
                    'About 48 days',
                    'About 1 year',
                    'Infinite'
                ],
                correctExplanation: 'Half-life = ln 0.5 / ln(a + b) = ln 0.5 / ln 0.986 ≈ 48 trading days.',
                incorrectExplanation: 'Use ln 0.5 / ln(a + b) with a + b close to but below 1.'
            },
            ro: {
                title: 'Persistența DCC',
                text: 'Pentru SPY–TLT estimările DCC sunt a = 0,053, b = 0,933. Care este timpul de înjumătățire al unui șoc de corelație?',
                options: [
                    'Aproximativ 1 zi',
                    'Aproximativ 48 de zile',
                    'Aproximativ 1 an',
                    'Infinit'
                ],
                correctExplanation: 'Timpul de înjumătățire = ln 0,5 / ln(a + b) = ln 0,5 / ln 0,986 ≈ 48 de zile de tranzacționare.',
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
                title: 'Testul CCC contra DCC',
                text: 'De ce distribuția hi-pătrat este doar orientativă pentru raportul de verosimilitate CCC (a = 0) contra DCC?',
                options: [
                    'Pentru că verosimilitatea nu este Gaussiană',
                    'Pentru că eșantionul este prea mare',
                    'Pentru că testul are doi parametri',
                    'Pentru că sub a = 0 parametrul b nu este identificat (o problemă de tip Davies)'
                ],
                correctExplanation: 'Când a = 0, b dispare din model; asimptotica standard nu mai funcționează, iar referința hi-pătrat este doar un ghid aproximativ.',
                incorrectExplanation: 'Parametrul de perturbație b nu este identificat sub ipoteza nulă, ceea ce strică asimptotica hi-pătrat standard.'
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
                    'Bitcoin a devenit o acoperire împotriva prăbușirilor bursiere',
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
                title: 'Forbes–Rigobon bias',
                text: 'Why can correlations rise in a crisis even if the transmission mechanism does not change?',
                options: [
                    'Because returns become Normal in crises',
                    'Because a higher variance of the source market mechanically raises the measured correlation',
                    'Because trading volume falls',
                    'Because correlations are always higher in bull markets'
                ],
                correctExplanation: 'In y = α + βx + ε with constant β and σε, ρ² = β²σx²/(β²σx² + σε²) rises with σx²: the heteroskedasticity bias.',
                incorrectExplanation: 'The bias comes from the higher variance of the source market with unchanged β and σε.'
            },
            ro: {
                title: 'Distorsiunea Forbes–Rigobon',
                text: 'De ce pot crește corelațiile în criză chiar dacă mecanismul de transmitere nu se schimbă?',
                options: [
                    'Pentru că randamentele devin Normale în criză',
                    'Pentru că o varianță mai mare a pieței-sursă crește mecanic corelația măsurată',
                    'Pentru că volumul de tranzacționare scade',
                    'Pentru că în piețele în creștere corelațiile sunt întotdeauna mai mari'
                ],
                correctExplanation: 'În y = α + βx + ε cu β și σε constante, ρ² = β²σx²/(β²σx² + σε²) crește odată cu σx²: distorsiunea de heteroscedasticitate.',
                incorrectExplanation: 'Distorsiunea vine din varianța mai mare a pieței-sursă, cu β și σε neschimbate.'
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
                text: 'Pentru distribuția Normală bivariată, ce se întâmplă cu corelația de depășire când pragul se mută spre cozi?',
                options: [
                    'Crește spre 1',
                    'Rămâne egală cu ρ',
                    'Devine negativă',
                    'Scade spre 0'
                ],
                correctExplanation: 'Extremele Normale sunt asimptotic independente; datele arată valori mult mai mari (de exemplu 0,80 pentru pierderi comune la q = 0,10, față de 0,41 sub normalitate).',
                incorrectExplanation: 'Sub normalitate, condiționarea pe extreme duce corelația spre zero.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Sklar\'s theorem',
                text: 'What does Sklar\'s theorem state?',
                options: [
                    'Every joint distribution is Normal after a transformation',
                    'Every joint distribution can be written as a copula evaluated at the marginal distribution functions',
                    'Correlation determines the joint distribution',
                    'Copulas exist only for elliptical distributions'
                ],
                correctExplanation: 'F(x1, ..., xd) = C(F1(x1), ..., Fd(xd)); the copula is unique when the margins are continuous.',
                incorrectExplanation: 'Sklar separates any joint distribution into margins and a copula.'
            },
            ro: {
                title: 'Teorema lui Sklar',
                text: 'Ce afirmă teorema lui Sklar?',
                options: [
                    'Orice repartiție comună devine Normală după o transformare',
                    'Orice repartiție comună se poate scrie ca o copulă evaluată în funcțiile de repartiție marginale',
                    'Corelația determină repartiția comună',
                    'Copulele există doar pentru repartiții eliptice'
                ],
                correctExplanation: 'F(x1, ..., xd) = C(F1(x1), ..., Fd(xd)); copula este unică atunci când marginalele sunt continue.',
                incorrectExplanation: 'Sklar separă orice repartiție comună în marginale și o copulă.'
            }
        },
        {
            correct: 0,
            en: {
                title: 'Tail dependence by family',
                text: 'Which copula has upper-tail dependence but no lower-tail dependence?',
                options: [
                    'Gumbel',
                    'Clayton',
                    'Gaussian',
                    'Frank'
                ],
                correctExplanation: 'Gumbel: λU = 2 − 2^{1/θ}, λL = 0. Clayton is the mirror image; Gaussian and Frank have none; Student t has both.',
                incorrectExplanation: 'Only the Gumbel copula has upper-tail dependence alone.'
            },
            ro: {
                title: 'Dependența în cozi pe familii',
                text: 'Ce copulă are dependență în coada superioară, dar nu și în cea inferioară?',
                options: [
                    'Gumbel',
                    'Clayton',
                    'Gaussiană',
                    'Frank'
                ],
                correctExplanation: 'Gumbel: λU = 2 − 2^{1/θ}, λL = 0. Clayton este imaginea în oglindă; Gaussiana și Frank nu au; Student t le are pe amândouă.',
                incorrectExplanation: 'Doar copula Gumbel are exclusiv dependență în coada superioară.'
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
                text: 'For JPM–BAC (T = 4122), all five static copulas are rejected by the Rosenblatt test, although the t copula has by far the best AIC. The most sensible conclusion is:',
                options: [
                    'The t copula is useless',
                    'The test is wrong',
                    'With thousands of observations even small misfits are detected; a static copula also ignores time-varying dependence',
                    'AIC and goodness-of-fit tests always agree'
                ],
                correctExplanation: 'Large samples give high power; dependence moves over time, so a static model is an approximation. AIC ranks models, the test checks absolute fit.',
                incorrectExplanation: 'Rejection reflects high power and time variation, not that the best model is useless.'
            },
            ro: {
                title: 'Adecvarea',
                text: 'Pentru JPM–BAC (T = 4122), toate cele cinci copule statice sunt respinse de testul Rosenblatt, deși copula t are de departe cel mai bun AIC. Concluzia cea mai rezonabilă este:',
                options: [
                    'Copula t este inutilă',
                    'Testul este greșit',
                    'Cu mii de observații sunt detectate și abateri mici; o copulă statică ignoră și dependența variabilă în timp',
                    'AIC și testele de adecvare coincid întotdeauna'
                ],
                correctExplanation: 'Eșantioanele mari dau putere mare; dependența se mișcă în timp, deci un model static este o aproximare. AIC ordonează modelele, testul verifică adecvarea absolută.',
                incorrectExplanation: 'Respingerea reflectă puterea mare și variația în timp, nu faptul că cel mai bun model ar fi inutil.'
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
                    'Prăbușirile comune se află în colțul superior al copulei pierderilor, unde Gumbel are dependență în cozi, iar Clayton nu',
                    'Clayton nu poate fi estimată pe pierderi',
                    'Gumbel este întotdeauna mai bună decât Clayton',
                    'Pierderile sunt independente'
                ],
                correctExplanation: 'Gumbel pe pierderi surprinde prăbușirile comune (λU = 0,26); Clayton pune dependența în colțul câștigurilor comune.',
                incorrectExplanation: 'Coada superioară a pierderilor conține prăbușirile comune; doar Gumbel pune dependența acolo.'
            }
        },
        {
            correct: 1,
            en: {
                title: 'Gaussian copula and 2008',
                text: 'Why is the Gaussian copula of Li (2000) often blamed in accounts of the 2008 credit crisis?',
                options: [
                    'It overstated tail dependence',
                    'It has zero tail dependence, so joint defaults in a crisis were treated as almost impossible',
                    'It could not be calibrated',
                    'It used Kendall\'s tau'
                ],
                correctExplanation: 'With λ = 0 and one static correlation calibrated in calm years, the model understated the probability of many defaults at once.',
                incorrectExplanation: 'The problem was zero tail dependence combined with a static calibration.'
            },
            ro: {
                title: 'Copula Gaussiană și 2008',
                text: 'De ce este adesea învinuită copula Gaussiană a lui Li (2000) în relatările despre criza creditelor din 2008?',
                options: [
                    'A supraestimat dependența în cozi',
                    'Are dependență zero în cozi, deci falimentele comune din criză erau tratate ca aproape imposibile',
                    'Nu putea fi calibrată',
                    'Folosea tau al lui Kendall'
                ],
                correctExplanation: 'Cu λ = 0 și o singură corelație statică, calibrată în anii calmi, modelul subestima probabilitatea multor falimente simultane.',
                incorrectExplanation: 'Problema a fost dependența zero în cozi combinată cu o calibrare statică.'
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
                    'Through the BNP–TLV link, one of the weakest edges (0.35)'
                ],
                correctExplanation: 'The tree links TLV and BRD (0.65) and attaches them to the euro area through BNP–TLV (0.35): Romanian banks are the least connected.',
                incorrectExplanation: 'The Romanian block is attached through BNP–TLV, a weak link.'
            },
            ro: {
                title: 'Rețeaua băncilor',
                text: 'În arborele de acoperire minimă al celor șase bănci (randamente săptămânale 2010–2026), cum sunt legate băncile românești de celelalte?',
                options: [
                    'Prin JPM',
                    'Nu sunt legate',
                    'Doar prin Deutsche Bank, cu cea mai mare corelație din arbore',
                    'Prin legătura BNP–TLV, una dintre cele mai slabe muchii (0,35)'
                ],
                correctExplanation: 'Arborele leagă TLV și BRD (0,65) și le atașează zonei euro prin BNP–TLV (0,35): băncile românești sunt cele mai puțin conectate.',
                incorrectExplanation: 'Blocul românesc este legat prin BNP–TLV, o legătură slabă.'
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
                text: 'Corelația săptămânală BET–Euro Stoxx 50 a crescut de la 0,45 (2010–2019) la 0,62 (2020–2026), cu un interval bootstrap de 95% pentru schimbare de [-0,05; 0,34]. Care este concluzia cea mai corectă?',
                options: [
                    'Integrare puternică și semnificativă',
                    'România s-a decuplat de zona euro',
                    'Dovezi modeste și fragile: intervalul conține zero, iar creșterea este concentrată în anii de criză',
                    'Corelația nu s-a schimbat deloc'
                ],
                correctExplanation: 'Estimarea punctuală crește, dar intervalul conține zero, excluderea săptămânilor prăbușirii din 2020 o reduce, iar dependența în coada inferioară nu a crescut.',
                incorrectExplanation: 'Schimbarea nu este semnificativă la 5% și depinde de săptămânile de criză.'
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
                    "For any rho < 1 the Gaussian copula has zero tail dependence, so it does not capture joint crashes",
                    "Tail dependence can only be computed for Archimedean copulas"
                ],
                correctExplanation: "The Gaussian copula is asymptotically independent in both tails: lambda_L = lambda_U = 0 for rho < 1. Joint extremes need a t copula (symmetric tail dependence) or a Clayton copula (lower tail).",
                incorrectExplanation: "No positive formula in rho is correct here: the Gaussian copula has lambda_L = lambda_U = 0 for every rho < 1, so it understates joint crashes."
            },
            ro: {
                title: "Găsiți eroarea: cozile copulei Gaussiene",
                text: "Un asistent AI scrie: „O copulă Gaussiană cu corelația rho = 0,7 are dependența în coada inferioară lambda_L = rho^2 = 0,49, deci surprinde bine prăbușirile comune.” Care este eroarea?",
                options: [
                    "Dependența în coada inferioară a copulei Gaussiene este rho, nu rho^2",
                    "Copula Gaussiană are dependență în coada superioară, dar nu și în cea inferioară",
                    "Pentru orice rho < 1 copula Gaussiană are dependență zero în cozi, deci nu surprinde prăbușirile comune",
                    "Dependența în cozi se poate calcula doar pentru copulele arhimediene"
                ],
                correctExplanation: "Copula Gaussiană este asimptotic independentă în ambele cozi: lambda_L = lambda_U = 0 pentru rho < 1. Extremele comune cer o copulă t (dependență simetrică în cozi) sau o copulă Clayton (coada inferioară).",
                incorrectExplanation: "Nicio formulă pozitivă în rho nu este corectă aici: copula Gaussiană are lambda_L = lambda_U = 0 pentru orice rho < 1, deci subestimează prăbușirile comune."
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
                    "Tau Kendall trebuie întâi transformat în corelația Pearson a randamentelor brute"
                ],
                correctExplanation: "Pentru copulele Gaussiană și t, tau = (2/pi) arcsin(rho), deci rho = sin(pi tau / 2) = sin(0,2 pi) = 0,588. Relația rho = 2 sin(pi rho_S / 6) leagă copula Gaussiană de rho_S Spearman, nu de tau Kendall.",
                incorrectExplanation: "Inversarea pentru tau Kendall este rho = sin(pi tau / 2), care dă 0,588; 2 sin(pi x / 6) este relația pentru Spearman."
            }
        }
    ]
};

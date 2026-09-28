// ============================================================
// Quiz bank for chapter id 'factors': Factor Models and Asset Pricing (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['factors'] = {
    draw: 20,
    questions: [
        {
            correct: 1,
            en: {
                title: "GRS in Sharpe-ratio form",
                text: "With maximum-likelihood moments, the GRS quadratic form α̂′Σ̂⁻¹α̂ equals…",
                options: [
                    "The average squared alpha across the test assets",
                    "SR²(factors + test assets) − SR²(factors): the gain in the maximum squared Sharpe ratio from adding the test assets",
                    "The average R² of the time-series regressions",
                    "The squared Sharpe ratio of the factors, SR²(factors)"
                ],
                correctExplanation: "By the partitioned inverse of the covariance of (f, R), μ′V⁻¹μ = SR²(f) + α′Σ⁻¹α. On the 25 portfolios the monthly Sharpe ratio rises from 0.134 to 0.405, and GRS = 4.20.",
                incorrectExplanation: "The quadratic form weights the alphas by Σ̂⁻¹ and equals the increase in the tangency Sharpe ratio squared when the test assets are added to the factors."
            },
            ro: {
                title: "GRS în forma raportului Sharpe",
                text: "Cu momente de verosimilitate maximă, forma pătratică GRS α̂′Σ̂⁻¹α̂ este egală cu…",
                options: [
                    "Media pătratelor valorilor alfa ale activelor de test",
                    "SR²(factori + active de test) − SR²(factori): câștigul de raport Sharpe maxim la pătrat adus de activele de test",
                    "Media R² a regresiilor în serii de timp",
                    "Pătratul raportului Sharpe al factorilor, SR²(factori)"
                ],
                correctExplanation: "Din inversa partiționată a covarianței lui (f, R), μ′V⁻¹μ = SR²(f) + α′Σ⁻¹α. Pe cele 25 de portofolii, raportul Sharpe lunar crește de la 0,134 la 0,405, iar GRS = 4,20.",
                incorrectExplanation: "Forma pătratică ponderează valorile alfa cu Σ̂⁻¹ și este egală cu creșterea pătratului raportului Sharpe tangent când activele de test se adaugă la factori."
            }
        },
        {
            correct: 3,
            en: {
                title: "A skeptical appraisal of R²",
                text: "A new three-factor model reaches a cross-sectional R² of 80% on the 25 size × B/M portfolios. Why is this weak evidence (Lewellen, Nagel and Shanken, 2010)?",
                options: [
                    "Because 25 portfolios are too many test assets",
                    "Because a credible R² must exceed 95%",
                    "Because the OLS R² is always 80% on these portfolios",
                    "Because these portfolios have a strong factor structure, so any factors correlated with SMB and HML fit them; add other test assets and report the GLS R² with confidence intervals"
                ],
                correctExplanation: "In the lecture FF3 has an OLS R² of 0.66 on the 25 portfolios but 0.21 once 30 industries are added, and its GLS R² is at most 0.20.",
                incorrectExplanation: "A high OLS R² on the 25 size × B/M portfolios is a low hurdle: the assets are spanned by three factors, and many unrelated factor sets fit them."
            },
            ro: {
                title: "O evaluare sceptică a lui R²",
                text: "Un nou model cu trei factori atinge un R² transversal de 80% pe cele 25 de portofolii mărime × B/M. De ce este o dovadă slabă (Lewellen, Nagel și Shanken, 2010)?",
                options: [
                    "Pentru că 25 de portofolii sunt prea multe active de test",
                    "Pentru că un R² credibil trebuie să depășească 95%",
                    "Pentru că R² OLS este mereu 80% pe aceste portofolii",
                    "Pentru că aceste portofolii au o structură factorială puternică, deci orice factori corelați cu SMB și HML le potrivesc; adăugați alte active de test și raportați R² GLS cu intervale de încredere"
                ],
                correctExplanation: "În curs, FF3 are R² OLS 0,66 pe cele 25 de portofolii, dar 0,21 după adăugarea a 30 de industrii, iar R² GLS este cel mult 0,20.",
                incorrectExplanation: "Un R² OLS mare pe cele 25 de portofolii mărime × B/M este un prag jos: activele sunt acoperite de trei factori și multe seturi de factori fără legătură le potrivesc."
            }
        },
        {
            correct: 0,
            en: {
                title: "Useless factor",
                text: "A macroeconomic factor is statistically independent of all returns. In a two-pass regression with a misspecified model, its estimated premium λ̂…",
                options: [
                    "Can look significant: the Fama–MacBeth t-test over-rejects, because the betas on the factor are pure noise of order T^(−1/2)",
                    "Is exactly zero",
                    "Is always insignificant",
                    "Equals the time-series mean of the factor"
                ],
                correctExplanation: "Kan and Zhang (1999): pass 2 divides by noise, so λ̂ does not converge to zero. In the lecture simulation λ = 0 was rejected in 60% of the replications with Fama–MacBeth errors at the 5% level.",
                incorrectExplanation: "Independence from returns does not protect pass 2: the betas are estimated with noise and the premium estimate inherits a non-vanishing error; test the first-pass betas first."
            },
            ro: {
                title: "Factor inutil",
                text: "Un factor macroeconomic este statistic independent de toate randamentele. Într-o regresie în două etape cu un model greșit specificat, prima lui estimată λ̂…",
                options: [
                    "Poate părea semnificativă: testul t Fama–MacBeth respinge prea des, pentru că valorile beta pe acest factor sunt doar zgomot de ordinul T^(−1/2)",
                    "Este exact zero",
                    "Este mereu nesemnificativă",
                    "Este egală cu media factorului în timp"
                ],
                correctExplanation: "Kan și Zhang (1999): etapa 2 împarte la zgomot, deci λ̂ nu converge la zero. În simularea din curs, λ = 0 a fost respins în 60% din replicări cu erori Fama–MacBeth, la nivelul de 5%.",
                incorrectExplanation: "Independența față de randamente nu protejează etapa 2: valorile beta sunt estimate cu zgomot, iar prima estimată moștenește o eroare care nu dispare; testați întâi valorile beta din prima etapă."
            }
        },
        {
            correct: 3,
            en: {
                title: "Newey–West errors",
                text: "In the monthly regression of XLK on the market (1999–2026), the Newey–West standard error of beta is about twice the classical one. Why?",
                options: [
                    "Because OLS is biased",
                    "Because the sample is too short for OLS",
                    "Because Newey–West changes the estimate of beta",
                    "Because residual variance changes with market volatility (heteroskedasticity), which classical errors ignore"
                ],
                correctExplanation: "Newey–West keeps the OLS estimate and corrects its variance for heteroskedasticity and autocorrelation; volatility clustering makes classical errors too small.",
                incorrectExplanation: "The point estimate is the same; only the standard error changes, because residuals are heteroskedastic."
            },
            ro: {
                title: "Erori Newey–West",
                text: "În regresia lunară a XLK pe piață (1999–2026), eroarea standard Newey–West a lui beta este aproximativ dublă față de cea clasică. De ce?",
                options: [
                    "Pentru că OLS este deplasat",
                    "Pentru că eșantionul este prea scurt pentru OLS",
                    "Pentru că Newey–West schimbă estimația lui beta",
                    "Pentru că varianța reziduurilor se schimbă odată cu volatilitatea pieței (heteroscedasticitate), iar erorile clasice o ignoră"
                ],
                correctExplanation: "Newey–West păstrează estimația OLS și îi corectează varianța pentru heteroscedasticitate și autocorelare; gruparea volatilității face erorile clasice prea mici.",
                incorrectExplanation: "Estimația punctuală este aceeași; se schimbă doar eroarea standard, pentru că reziduurile sunt heteroscedastice."
            }
        },
        {
            correct: 2,
            en: {
                title: "Vasicek: empirical-Bayes prior",
                text: "The estimated betas of 9 sectors have a cross-sectional variance of 0.116, and their average squared standard error is 0.02. Which prior variance σ²_β should the Vasicek estimator use?",
                options: [
                    "0.116",
                    "0.136",
                    "0.096",
                    "0.02"
                ],
                correctExplanation: "Var_cs(β̂) = σ²_β + mean se², because estimation noise adds to the dispersion of the true betas; hence σ²_β = 0.116 − 0.02 = 0.096.",
                incorrectExplanation: "The variance of the estimated betas includes their sampling noise; the prior must describe the true betas, so subtract the average squared standard error."
            },
            ro: {
                title: "Vasicek: informația a priori Bayes empirică",
                text: "Valorile beta estimate pentru 9 sectoare au varianța transversală 0,116, iar media pătratelor erorilor lor standard este 0,02. Ce varianță a priori σ²_β trebuie să folosească estimatorul Vasicek?",
                options: [
                    "0,116",
                    "0,136",
                    "0,096",
                    "0,02"
                ],
                correctExplanation: "Var_cs(β̂) = σ²_β + media se², pentru că zgomotul de estimare se adaugă dispersiei valorilor beta adevărate; deci σ²_β = 0,116 − 0,02 = 0,096.",
                incorrectExplanation: "Varianța valorilor beta estimate include zgomotul de eșantionare; informația a priori trebuie să descrie valorile beta adevărate, deci se scade media pătratelor erorilor standard."
            }
        },
        {
            correct: 1,
            en: {
                title: "Nonsynchronous trading",
                text: "Daily OLS betas of thinly traded Bucharest Stock Exchange stocks on the BET index are…",
                options: [
                    "Biased upwards",
                    "Biased towards zero; the Dimson sum of slopes on lagged, current and leading BET returns corrects most of it",
                    "Unbiased, because OLS is unbiased",
                    "Undefined when a stock does not trade"
                ],
                correctExplanation: "Stale prices spread the reaction to market news over several days. In the seminar the Dimson beta of Nuclearelectrica rises from 0.80 to 0.94 and that of Digi from 0.67 to 0.75.",
                incorrectExplanation: "A stock that trades late reacts to today's market move tomorrow, so the contemporaneous covariance understates its beta; sum the lead and lag slopes."
            },
            ro: {
                title: "Tranzacționare asincronă",
                text: "Valorile beta OLS zilnice ale acțiunilor puțin lichide de la Bursa de Valori București față de indicele BET sunt…",
                options: [
                    "Deplasate în sus",
                    "Deplasate spre zero; suma Dimson a pantelor pe randamentele BET întârziate, curente și anticipate corectează cea mai mare parte",
                    "Nedeplasate, pentru că OLS este nedeplasat",
                    "Nedefinite când o acțiune nu se tranzacționează"
                ],
                correctExplanation: "Prețurile vechi împrăștie reacția la știrile pieței pe mai multe zile. În seminar, beta Dimson al Nuclearelectrica crește de la 0,80 la 0,94, iar al Digi de la 0,67 la 0,75.",
                incorrectExplanation: "O acțiune care se tranzacționează cu întârziere reacționează mâine la mișcarea de azi a pieței, deci covarianța contemporană subestimează beta; adunați pantele anticipate și întârziate."
            }
        },
        {
            correct: 3,
            en: {
                title: "Traded-factor premium",
                text: "For a traded factor, the two-pass premium λ̂ is far from the factor's time-series mean (market: −6.6% vs +7.2% a year on the 25 portfolios). What does this indicate?",
                options: [
                    "That the factor is not traded",
                    "That the time-series mean is biased",
                    "That the Shanken errors are too small",
                    "Misspecification of the model for these test assets, or weak identification of the premium when betas barely vary"
                ],
                correctExplanation: "A traded factor prices itself, so λ should equal E[f]. Market betas span only 0.86–1.42 on the 25 portfolios, so the intercept absorbs the level and λ_m is weakly identified.",
                incorrectExplanation: "The gap is a diagnostic about the model and the test assets, not about the factor mean or the standard errors."
            },
            ro: {
                title: "Prima unui factor tranzacționat",
                text: "Pentru un factor tranzacționat, prima λ̂ din cele două etape este departe de media factorului în timp (piața: −6,6% față de +7,2% pe an pe cele 25 de portofolii). Ce indică acest lucru?",
                options: [
                    "Că factorul nu este tranzacționat",
                    "Că media în timp este deplasată",
                    "Că erorile Shanken sunt prea mici",
                    "Specificarea greșită a modelului pentru aceste active de test sau identificarea slabă a primei când valorile beta variază foarte puțin"
                ],
                correctExplanation: "Un factor tranzacționat se evaluează pe sine, deci λ ar trebui să fie egal cu E[f]. Valorile beta de piață acoperă doar 0,86–1,42 pe cele 25 de portofolii, deci termenul liber absoarbe nivelul, iar λ_m este slab identificat.",
                incorrectExplanation: "Diferența este un diagnostic despre model și activele de test, nu despre media factorului sau erorile standard."
            }
        },
        {
            correct: 0,
            en: {
                title: "Large-N alpha test",
                text: "You want to test the alphas of N = 100 portfolios using T = 96 monthly returns. What happens to the GRS test?",
                options: [
                    "It cannot be computed: the residual covariance matrix has rank at most T − 2 < N, so it is singular; use a large-N test such as Pesaran–Yamagata",
                    "It is valid but has low power",
                    "It is valid if the residuals follow the Normal distribution",
                    "It is valid with Newey–West errors"
                ],
                correctExplanation: "Σ̂ is built from T residual vectors with two estimated parameters, so its rank is at most T − 2 = 94 < 100 and Σ̂⁻¹ does not exist.",
                incorrectExplanation: "The problem is not power or normality: Σ̂⁻¹ does not exist when N ≥ T − 1, and GRS needs it."
            },
            ro: {
                title: "Test de alfa pentru N mare",
                text: "Vreți să testați valorile alfa pentru N = 100 de portofolii cu T = 96 de randamente lunare. Ce se întâmplă cu testul GRS?",
                options: [
                    "Nu se poate calcula: matricea de covarianță a reziduurilor are rangul cel mult T − 2 < N, deci este singulară; folosiți un test pentru N mare, precum Pesaran–Yamagata",
                    "Este valid, dar are putere mică",
                    "Este valid dacă reziduurile urmează distribuția Normală",
                    "Este valid cu erori Newey–West"
                ],
                correctExplanation: "Σ̂ este construită din T vectori de reziduuri cu doi parametri estimați, deci rangul ei este cel mult T − 2 = 94 < 100, iar Σ̂⁻¹ nu există.",
                incorrectExplanation: "Problema nu este puterea sau normalitatea: Σ̂⁻¹ nu există când N ≥ T − 1, iar GRS are nevoie de ea."
            }
        },
        {
            correct: 2,
            en: {
                title: "Low power",
                text: "The GRS test does not reject the CAPM on 9 US sector ETFs (p = 0.85) but rejects it strongly on the 25 size × B/M portfolios. Why?",
                options: [
                    "Sector ETFs are more efficient than portfolios",
                    "The CAPM is true for sectors",
                    "Sectors do not spread size and value, so they have little dispersion in the alphas that matter: the test has low power",
                    "The sector sample is longer"
                ],
                correctExplanation: "Test assets must spread the characteristics that carry premia; sectors mix small and big, value and growth stocks. Not rejecting is weak evidence.",
                incorrectExplanation: "Failing to reject is not evidence that the CAPM holds; the sector test simply lacks power."
            },
            ro: {
                title: "Putere redusă",
                text: "Testul GRS nu respinge CAPM pe 9 ETF-uri sectoriale din SUA (p = 0,85), dar îl respinge categoric pe cele 25 de portofolii mărime × B/M. De ce?",
                options: [
                    "ETF-urile sectoriale sunt mai eficiente decât portofoliile",
                    "CAPM este adevărat pentru sectoare",
                    "Sectoarele nu împrăștie mărimea și valoarea, deci au puțină dispersie în valorile alfa care contează: testul are putere mică",
                    "Eșantionul sectorial este mai lung"
                ],
                correctExplanation: "Activele de test trebuie să împrăștie caracteristicile remunerate; sectoarele amestecă firme mici și mari, value și growth. Nerespingerea este o dovadă slabă.",
                incorrectExplanation: "Nerespingerea nu este o dovadă că CAPM este adevărat; testul pe sectoare nu are putere."
            }
        },
        {
            correct: 3,
            en: {
                title: "Flat SML",
                text: "On the 25 size × B/M portfolios (1963–2026), the fitted cross-sectional line of average excess returns on CAPM betas has slope −4.4% a year. What does this mean?",
                options: [
                    "The market premium was negative",
                    "Betas were estimated with the wrong sign",
                    "The CAPM holds exactly",
                    "Higher-beta portfolios did not earn higher average returns: the empirical SML is flat or negative"
                ],
                correctExplanation: "The CAPM predicts a slope equal to the premium (7.2%); a flat or negative SML is the classic empirical failure, explained for example by leverage constraints (Black; Frazzini–Pedersen).",
                incorrectExplanation: "The time-series market premium was positive (7.2%); the failure is that beta does not explain the cross section."
            },
            ro: {
                title: "SML plată",
                text: "Pe cele 25 de portofolii mărime × B/M (1963–2026), dreapta transversală a randamentelor medii în exces în funcție de beta CAPM are panta −4,4% pe an. Ce înseamnă?",
                options: [
                    "Prima pieței a fost negativă",
                    "Valorile beta au fost estimate cu semn greșit",
                    "CAPM este exact adevărat",
                    "Portofoliile cu beta mai mare nu au avut randamente medii mai mari: SML empirică este plată sau negativă"
                ],
                correctExplanation: "CAPM prezice o pantă egală cu prima (7,2%); o SML plată sau negativă este eșecul empiric clasic, explicat de exemplu prin constrângerile de levier (Black; Frazzini–Pedersen).",
                incorrectExplanation: "Prima pieței în timp a fost pozitivă (7,2%); eșecul constă în faptul că beta nu explică secțiunea transversală."
            }
        },
        {
            correct: 1,
            en: {
                title: "Betting against beta",
                text: "How is the BAB (Betting Against Beta) factor of Frazzini and Pedersen built?",
                options: [
                    "Long high-beta stocks, short low-beta stocks",
                    "Long leveraged low-beta stocks and short de-leveraged high-beta stocks, so that the portfolio has beta zero",
                    "Long the market, short the risk-free asset",
                    "Long small stocks, short big stocks"
                ],
                correctExplanation: "r_BAB = (R_L − R_f)/β_L − (R_H − R_f)/β_H: each leg is scaled to beta one, so the difference is market-neutral.",
                incorrectExplanation: "BAB buys low beta and sells high beta, scaled to a zero beta; it is not a size or market portfolio."
            },
            ro: {
                title: "Betting against beta",
                text: "Cum este construit factorul BAB (Betting Against Beta) al lui Frazzini și Pedersen?",
                options: [
                    "Long acțiuni cu beta mare, short acțiuni cu beta mic",
                    "Long acțiuni cu beta mic cu levier și short acțiuni cu beta mare cu levier redus, astfel încât portofoliul să aibă beta zero",
                    "Long piața, short activul fără risc",
                    "Long firme mici, short firme mari"
                ],
                correctExplanation: "r_BAB = (R_L − R_f)/β_L − (R_H − R_f)/β_H: fiecare parte este scalată la beta unu, deci diferența este neutră față de piață.",
                incorrectExplanation: "BAB cumpără beta mic și vinde beta mare, scalate la beta zero; nu este un portofoliu de mărime sau de piață."
            }
        },
        {
            correct: 0,
            en: {
                title: "Roll’s critique",
                text: "What is Roll’s (1977) critique of CAPM tests?",
                options: [
                    "The true market portfolio of all wealth is unobservable, so every test is also a test of whether the proxy is mean–variance efficient",
                    "Betas cannot be estimated by OLS",
                    "The risk-free rate is not constant",
                    "Monthly data are too noisy"
                ],
                correctExplanation: "Any mean–variance efficient portfolio prices all assets exactly by beta, so rejecting the CAPM with a stock index may only reject the efficiency of that index.",
                incorrectExplanation: "The critique is about the unobservable market portfolio, not about estimation methods or data frequency."
            },
            ro: {
                title: "Critica lui Roll",
                text: "În ce constă critica lui Roll (1977) la testele CAPM?",
                options: [
                    "Portofoliul adevărat al pieței, cu toată averea, nu este observabil, deci orice test verifică și dacă aproximarea lui este eficientă medie–varianță",
                    "Beta nu poate fi estimat prin OLS",
                    "Rata fără risc nu este constantă",
                    "Datele lunare sunt prea zgomotoase"
                ],
                correctExplanation: "Orice portofoliu eficient medie–varianță evaluează exact toate activele prin beta, deci respingerea CAPM cu un indice bursier poate respinge doar eficiența acelui indice.",
                incorrectExplanation: "Critica privește portofoliul pieței neobservabil, nu metodele de estimare sau frecvența datelor."
            }
        },
        {
            correct: 2,
            en: {
                title: "Fama–MacBeth",
                text: "In the second pass of a Fama–MacBeth regression, what is estimated?",
                options: [
                    "One time-series regression per asset",
                    "The covariance matrix of the factors",
                    "A cross-sectional regression of returns on estimated betas for each period; the premia are the averages of these slopes",
                    "The GRS statistic"
                ],
                correctExplanation: "Pass 1 estimates betas; pass 2 runs T cross-sectional regressions and averages the slopes λ̂_t, whose standard deviation gives the standard error.",
                incorrectExplanation: "The time-series betas come from the first pass; the second pass is cross-sectional, period by period."
            },
            ro: {
                title: "Fama–MacBeth",
                text: "Ce se estimează în a doua etapă a unei regresii Fama–MacBeth?",
                options: [
                    "O regresie în serii de timp pentru fiecare activ",
                    "Matricea de covarianță a factorilor",
                    "O regresie transversală a randamentelor pe valorile beta estimate, pentru fiecare perioadă; primele sunt mediile acestor pante",
                    "Statistica GRS"
                ],
                correctExplanation: "Etapa 1 estimează beta; etapa 2 face T regresii transversale și mediază pantele λ̂_t, a căror abatere standard dă eroarea standard.",
                incorrectExplanation: "Beta din serii de timp provine din prima etapă; a doua etapă este transversală, perioadă cu perioadă."
            }
        },
        {
            correct: 3,
            en: {
                title: "Shanken correction",
                text: "Why is the Shanken correction applied to Fama–MacBeth standard errors?",
                options: [
                    "To correct for autocorrelation of returns",
                    "To make premia positive",
                    "To correct for non-Normal distributions of returns",
                    "Because betas are estimated, not known (errors in variables), which makes the usual errors too small"
                ],
                correctExplanation: "Var_Sh = (1 + c)(Var_FM − Σ_f/T) + Σ_f/T with c = λ′Σ_f⁻¹λ: only the errors-in-variables part is scaled. With monthly traded factors c is small (0.03 for FF3), so HML keeps t ≈ 2.99.",
                incorrectExplanation: "The correction addresses the estimation error in the betas used in the second pass."
            },
            ro: {
                title: "Corecția Shanken",
                text: "De ce se aplică erorilor standard Fama–MacBeth corecția Shanken?",
                options: [
                    "Pentru a corecta autocorelarea randamentelor",
                    "Pentru a face primele pozitive",
                    "Pentru a corecta distribuțiile non-Normale ale randamentelor",
                    "Pentru că valorile beta sunt estimate, nu cunoscute (erori în variabile), ceea ce face erorile obișnuite prea mici"
                ],
                correctExplanation: "Var_Sh = (1 + c)(Var_FM − Σ_f/T) + Σ_f/T, cu c = λ′Σ_f⁻¹λ: doar partea datorată erorilor în variabile este scalată. Pentru factori tranzacționați lunari c este mic (0,03 pentru FF3), deci HML păstrează t ≈ 2,99.",
                incorrectExplanation: "Corecția tratează eroarea de estimare a valorilor beta folosite în a doua etapă."
            }
        },
        {
            correct: 2,
            en: {
                title: "Number of factors",
                text: "Which estimator chooses the number of factors k by maximising the ratio of consecutive eigenvalues μ_k/μ_(k+1) of the sample covariance matrix?",
                options: [
                    "Kaiser's rule",
                    "Bai and Ng's information criterion",
                    "Ahn and Horenstein's eigenvalue ratio",
                    "The elbow of the scree plot, judged by eye"
                ],
                correctExplanation: "Ahn and Horenstein (2013) maximise μ_k/μ_(k+1); Bai and Ng (2002) minimise a penalised residual variance; Kaiser keeps eigenvalues above 1 and is not consistent.",
                incorrectExplanation: "The eigenvalue-ratio estimator needs no penalty; the information criterion and Kaiser's rule use other principles."
            },
            ro: {
                title: "Numărul de factori",
                text: "Ce estimator alege numărul de factori k maximizând raportul valorilor proprii consecutive μ_k/μ_(k+1) ale matricei de covarianță de selecție?",
                options: [
                    "Regula Kaiser",
                    "Criteriul informațional Bai–Ng",
                    "Raportul valorilor proprii Ahn–Horenstein",
                    "Cotul graficului scree, judecat din ochi"
                ],
                correctExplanation: "Ahn și Horenstein (2013) maximizează μ_k/μ_(k+1); Bai și Ng (2002) minimizează o varianță reziduală penalizată; Kaiser păstrează valorile proprii peste 1 și nu este consistent.",
                incorrectExplanation: "Estimatorul prin raportul valorilor proprii nu are nevoie de penalizare; criteriul informațional și regula Kaiser folosesc alte principii."
            }
        },
        {
            correct: 1,
            en: {
                title: "Comparing models",
                text: "Barillas and Shanken (2018): which test assets are needed to compare two factor models?",
                options: [
                    "The 25 size × B/M portfolios",
                    "None beyond the factors themselves: compare the maximum squared Sharpe ratios of the two factor sets",
                    "Industry portfolios",
                    "All individual stocks"
                ],
                correctExplanation: "A model's ability to price any asset is summarised by SR²(f) of its factors. In the lecture FF5 and Carhart both reach an annual Sharpe ratio of 0.97 over 1963–2026.",
                incorrectExplanation: "The comparison is done on the factors: test assets add the same information to both models and cancel out."
            },
            ro: {
                title: "Compararea modelelor",
                text: "Barillas și Shanken (2018): ce active de test sunt necesare pentru a compara două modele factoriale?",
                options: [
                    "Cele 25 de portofolii mărime × B/M",
                    "Niciunul în afara factorilor înșiși: se compară rapoartele Sharpe maxime la pătrat ale celor două seturi de factori",
                    "Portofoliile pe industrii",
                    "Toate acțiunile individuale"
                ],
                correctExplanation: "Capacitatea unui model de a evalua orice activ este rezumată de SR²(f) al factorilor săi. În curs, FF5 și Carhart ating amândouă un raport Sharpe anual de 0,97 în 1963–2026.",
                incorrectExplanation: "Comparația se face pe factori: activele de test adaugă aceeași informație ambelor modele și se anulează."
            }
        },
        {
            correct: 3,
            en: {
                title: "Premium decay",
                text: "What happened to the momentum premium after 2000 in the Kenneth French data?",
                options: [
                    "It doubled",
                    "It stayed the same",
                    "It became the largest premium",
                    "It fell from about 10.7% to 2.5% a year and its t-statistic from 5.5 to 0.75"
                ],
                correctExplanation: "Momentum was strong in 1963–1999 but weak in 2000–2026, including the 2009 crash; McLean and Pontiff document such post-publication declines.",
                incorrectExplanation: "The data show a strong decline of the momentum premium after 2000."
            },
            ro: {
                title: "Scăderea primelor",
                text: "Ce s-a întâmplat cu prima de momentum după 2000, în datele Kenneth French?",
                options: [
                    "S-a dublat",
                    "A rămas la fel",
                    "A devenit cea mai mare primă",
                    "A scăzut de la aproximativ 10,7% la 2,5% pe an, iar statistica t de la 5,5 la 0,75"
                ],
                correctExplanation: "Momentum a fost puternic în 1963–1999, dar slab în 2000–2026, inclusiv crash-ul din 2009; McLean și Pontiff documentează astfel de scăderi după publicare.",
                incorrectExplanation: "Datele arată o scădere puternică a primei de momentum după 2000."
            }
        },
        {
            correct: 0,
            en: {
                title: "Factor zoo",
                text: "With 300 independent factors that have no true premium, how many would you expect to pass |t| > 1.96?",
                options: [
                    "About 15",
                    "About 0",
                    "About 3",
                    "About 150"
                ],
                correctExplanation: "300 × 0.05 = 15 false discoveries on average; the simulation in the lecture gives 15.0.",
                incorrectExplanation: "Each useless factor passes the 5% test with probability 0.05, so 300 tests give about 15 false discoveries."
            },
            ro: {
                title: "Grădina zoologică a factorilor",
                text: "Cu 300 de factori independenți fără primă reală, câți v-ați aștepta să treacă pragul |t| > 1,96?",
                options: [
                    "Aproximativ 15",
                    "Aproximativ 0",
                    "Aproximativ 3",
                    "Aproximativ 150"
                ],
                correctExplanation: "300 × 0,05 = 15 descoperiri false în medie; simularea din curs dă 15,0.",
                incorrectExplanation: "Fiecare factor inutil trece testul de 5% cu probabilitatea 0,05, deci 300 de teste dau aproximativ 15 descoperiri false."
            }
        },
        {
            correct: 1,
            en: {
                title: "Multiple testing",
                text: "Which procedure controls the false discovery rate (the expected share of false rejections among rejections)?",
                options: [
                    "Bonferroni",
                    "Benjamini–Hochberg",
                    "Holm",
                    "The naive 5% test"
                ],
                correctExplanation: "Benjamini–Hochberg rejects the hypotheses up to the largest j with p_(j) ≤ jα/M and controls the FDR; Bonferroni and Holm control the family-wise error rate.",
                incorrectExplanation: "Bonferroni and Holm control the probability of any false rejection (FWER), not the FDR."
            },
            ro: {
                title: "Testare multiplă",
                text: "Ce procedură controlează rata descoperirilor false (ponderea așteptată a respingerilor false în totalul respingerilor)?",
                options: [
                    "Bonferroni",
                    "Benjamini–Hochberg",
                    "Holm",
                    "Testul naiv de 5%"
                ],
                correctExplanation: "Benjamini–Hochberg respinge ipotezele până la cel mai mare j cu p_(j) ≤ jα/M și controlează FDR; Bonferroni și Holm controlează rata erorii pe familie.",
                incorrectExplanation: "Bonferroni și Holm controlează probabilitatea oricărei respingeri false (FWER), nu FDR."
            }
        },
        {
            correct: 2,
            en: {
                title: "The t > 3 hurdle",
                text: "Why do Harvey, Liu and Zhu (2016) propose a t-statistic above 3 for new factors?",
                options: [
                    "Because returns follow the Normal distribution",
                    "Because factor returns are always large",
                    "Because hundreds of factors have been tested, so the usual 1.96 threshold produces many false discoveries",
                    "Because Fama–MacBeth errors are too large"
                ],
                correctExplanation: "Multiple testing raises the bar: with 300 useless factors the best one has a median |t| of about 3.06.",
                incorrectExplanation: "The higher hurdle is a multiple-testing correction for the factor zoo."
            },
            ro: {
                title: "Pragul t > 3",
                text: "De ce propun Harvey, Liu și Zhu (2016) o statistică t peste 3 pentru factorii noi?",
                options: [
                    "Pentru că randamentele urmează distribuția Normală",
                    "Pentru că randamentele factorilor sunt mereu mari",
                    "Pentru că sute de factori au fost testați, deci pragul obișnuit de 1,96 produce multe descoperiri false",
                    "Pentru că erorile Fama–MacBeth sunt prea mari"
                ],
                correctExplanation: "Testarea multiplă ridică ștacheta: cu 300 de factori inutili, cel mai bun are un |t| median de aproximativ 3,06.",
                incorrectExplanation: "Pragul mai mare este o corecție pentru testarea multiplă în grădina zoologică a factorilor."
            }
        },
        {
            correct: 3,
            en: {
                title: "Size of the Shanken correction",
                text: "One traded factor with a monthly premium λ = 0.5% and monthly volatility σ_f = 4.5%. By how much does Shanken's factor (1 + c), c = λ²/σ_f², inflate the errors-in-variables part of the Fama–MacBeth variance?",
                options: [
                    "By about 11%",
                    "By about 0.5%",
                    "By about 50%",
                    "By about 1.2%"
                ],
                correctExplanation: "c = (0.005/0.045)² = 0.012: with monthly traded factors the correction is small; the lecture finds c = 0.03 for FF3, and HML's standard error barely changes.",
                incorrectExplanation: "c is the squared Sharpe ratio of the premium per period, not the Sharpe ratio itself; monthly Sharpe ratios are small, so c is small."
            },
            ro: {
                title: "Mărimea corecției Shanken",
                text: "Un factor tranzacționat are prima lunară λ = 0,5% și volatilitatea lunară σ_f = 4,5%. Cu cât mărește factorul Shanken (1 + c), c = λ²/σ_f², partea din varianța Fama–MacBeth datorată erorilor în variabile?",
                options: [
                    "Cu aproximativ 11%",
                    "Cu aproximativ 0,5%",
                    "Cu aproximativ 50%",
                    "Cu aproximativ 1,2%"
                ],
                correctExplanation: "c = (0,005/0,045)² = 0,012: pentru factori tranzacționați lunari corecția este mică; cursul găsește c = 0,03 pentru FF3, iar eroarea standard a HML abia se schimbă.",
                incorrectExplanation: "c este pătratul raportului Sharpe al primei pe perioadă, nu raportul Sharpe însuși; rapoartele Sharpe lunare sunt mici, deci c este mic."
            }
        },
        {
            correct: 0,
            en: {
                title: "First principal component",
                text: "In the PCA of 11 US sector ETFs (2018–2026), how should the first principal component be interpreted?",
                options: [
                    "As the market factor: all loadings are positive and its correlation with SPY is 0.95",
                    "As a value factor",
                    "As a defensive-versus-growth factor",
                    "As pure noise"
                ],
                correctExplanation: "PC1 explains 66% of the variance with loadings of the same sign; the defensive-versus-growth contrast appears in PC2.",
                incorrectExplanation: "The first latent factor is the market; the defensive-versus-growth factor is the second component."
            },
            ro: {
                title: "Prima componentă principală",
                text: "În PCA pe 11 ETF-uri sectoriale din SUA (2018–2026), cum trebuie interpretată prima componentă principală?",
                options: [
                    "Ca factor de piață: toate încărcările sunt pozitive, iar corelația cu SPY este 0,95",
                    "Ca factor de valoare",
                    "Ca factor defensiv versus creștere",
                    "Ca zgomot pur"
                ],
                correctExplanation: "PC1 explică 66% din varianță, cu încărcări de același semn; contrastul defensiv versus creștere apare în PC2.",
                incorrectExplanation: "Primul factor latent este piața; factorul defensiv versus creștere este a doua componentă."
            }
        },
        {
            correct: 1,
            en: {
                title: "IPCA",
                text: "What is the key idea of Instrumented PCA (Kelly, Pruitt and Su, 2019)?",
                options: [
                    "Factors are chosen by the investor",
                    "Factor loadings are linear functions of observed firm characteristics, estimated jointly with latent factors",
                    "Loadings are constant over time",
                    "Only the market factor is used"
                ],
                correctExplanation: "β_{i,t}′ = z_{i,t}′Γ_β lets betas change with characteristics; the paper finds that characteristics matter through covariances, not as alphas.",
                incorrectExplanation: "IPCA makes loadings time-varying through characteristics; standard PCA keeps them constant."
            },
            ro: {
                title: "IPCA",
                text: "Care este ideea de bază a PCA instrumentate (Kelly, Pruitt și Su, 2019)?",
                options: [
                    "Factorii sunt aleși de investitor",
                    "Încărcările factoriale sunt funcții liniare de caracteristici observate ale firmelor, estimate împreună cu factorii latenți",
                    "Încărcările sunt constante în timp",
                    "Se folosește doar factorul de piață"
                ],
                correctExplanation: "β_{i,t}′ = z_{i,t}′Γ_β permite ca beta să se schimbe cu caracteristicile; articolul arată că acestea contează prin covarianțe, nu ca alfa.",
                incorrectExplanation: "IPCA face încărcările variabile în timp prin caracteristici; PCA standard le păstrează constante."
            }
        },
        {
            correct: 2,
            en: {
                title: "Factor ETFs",
                text: "After regressing MTUM and QUAL on the FF5 + momentum factors, what did the lecture find?",
                options: [
                    "Large positive alphas of about 5% a year",
                    "Market betas close to zero",
                    "Alphas close to zero, with loadings that match the labels (MTUM on MOM, QUAL on RMW)",
                    "Negative loadings on their own factor"
                ],
                correctExplanation: "MTUM had alpha −0.2% (t = −0.11) and a MOM loading of 0.36; factor ETFs deliver exposure, not skill.",
                incorrectExplanation: "The alphas were statistically zero and the market betas close to one."
            },
            ro: {
                title: "ETF-uri factoriale",
                text: "După regresia MTUM și QUAL pe factorii FF5 + momentum, ce a arătat cursul?",
                options: [
                    "Valori alfa mari, pozitive, de aproximativ 5% pe an",
                    "Beta de piață aproape de zero",
                    "Valori alfa apropiate de zero, cu încărcări care corespund denumirilor (MTUM pe MOM, QUAL pe RMW)",
                    "Încărcări negative pe propriul factor"
                ],
                correctExplanation: "MTUM a avut alfa −0,2% (t = −0,11) și încărcarea pe MOM 0,36; ETF-urile factoriale oferă expunere, nu abilitate.",
                incorrectExplanation: "Valorile alfa au fost statistic zero, iar beta de piață apropiat de unu."
            }
        },
        {
            correct: 1,
            en: {
                title: "Spot the AI error: a momentum signal",
                text: "An AI assistant writes this momentum backtest: \"mom = P.pct_change(12); at each month-end t, rank the stocks on mom at t and record the return of the top minus bottom stocks over month t.\" The result is 49% a year. What is wrong?",
                options: [
                    "Momentum must be computed on 36 months, not 12",
                    "Look-ahead bias: the signal at t contains the return of month t, the month being held; the signal must be known before the month starts",
                    "Monthly returns cannot be annualised by multiplying by 12",
                    "A long–short portfolio always has a mean return of zero"
                ],
                correctExplanation: "Ranking on a 12-month return that ends at t and holding over month t uses the holding-period return to choose the stocks. Lag the signal, e.g. the 12–1 signal P.shift(2)/P.shift(13) − 1.",
                incorrectExplanation: "The signal includes the very return it is meant to predict: use only prices known at the start of the holding month, e.g. months t−12 to t−2."
            },
            ro: {
                title: "Găsiți eroarea AI: un semnal de momentum",
                text: "Un asistent AI scrie acest backtest de momentum: „mom = P.pct_change(12); la fiecare sfârșit de lună t, ordonați acțiunile după mom la t și înregistrați randamentul primelor minus ultimelor acțiuni în luna t.” Rezultatul este 49% pe an. Ce este greșit?",
                options: [
                    "Momentum-ul se calculează pe 36 de luni, nu pe 12",
                    "Informații din viitor (look-ahead bias): semnalul la t conține randamentul lunii t, luna în care portofoliul este deținut; semnalul trebuie să fie cunoscut înainte de începutul lunii",
                    "Randamentele lunare nu pot fi anualizate prin înmulțire cu 12",
                    "Un portofoliu long–short are mereu randamentul mediu zero"
                ],
                correctExplanation: "Ordonarea după un randament pe 12 luni care se termină la t, urmată de deținerea în luna t, folosește chiar randamentul perioadei de deținere pentru alegerea acțiunilor. Decalați semnalul, de exemplu semnalul 12–1 P.shift(2)/P.shift(13) − 1.",
                incorrectExplanation: "Semnalul conține chiar randamentul pe care ar trebui să-l prognozeze: folosiți doar prețuri cunoscute la începutul lunii de deținere, de exemplu lunile t−12 până la t−2."
            }
        },
        {
            correct: 3,
            en: {
                title: "Spot the AI error: Blume-adjusted beta",
                text: "An AI assistant writes: \"The Blume-adjusted beta is β_B = 0.67 + 0.33 β̂. For an estimated beta of 1.5, β_B = 1.165.\" What is wrong?",
                options: [
                    "Blume's adjustment moves betas away from 1, not towards it",
                    "The Blume beta applies only to portfolios, never to single stocks",
                    "Adjusted betas must equal the OLS beta when β̂ > 1",
                    "The weights are swapped: β_B = 0.33 + 0.67 β̂, so β_B = 1.335"
                ],
                correctExplanation: "Blume (1971): β_B = 0.33 + 0.67 β̂, which shrinks the estimate towards 1: 0.33 + 0.67 × 1.5 = 1.335. The swapped weights shrink far too much.",
                incorrectExplanation: "In Blume's rule the estimated beta gets the weight 0.67 and the constant is 0.33: for β̂ = 1.5 the adjusted beta is 1.335."
            },
            ro: {
                title: "Găsiți eroarea AI: beta ajustat Blume",
                text: "Un asistent AI scrie: „Beta ajustat Blume este β_B = 0,67 + 0,33 β̂. Pentru un beta estimat de 1,5, β_B = 1,165.” Ce este greșit?",
                options: [
                    "Ajustarea Blume îndepărtează beta de 1, nu îl apropie",
                    "Beta Blume se aplică doar portofoliilor, niciodată acțiunilor individuale",
                    "Beta ajustat trebuie să fie egal cu beta OLS când β̂ > 1",
                    "Ponderile sunt inversate: β_B = 0,33 + 0,67 β̂, deci β_B = 1,335"
                ],
                correctExplanation: "Blume (1971): β_B = 0,33 + 0,67 β̂, care apropie estimarea de 1: 0,33 + 0,67 × 1,5 = 1,335. Ponderile inversate micșorează mult prea mult.",
                incorrectExplanation: "În regula lui Blume beta estimat primește ponderea 0,67, iar constanta este 0,33: pentru β̂ = 1,5 beta ajustat este 1,335."
            }
        }
    ]
};

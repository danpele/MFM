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
            correct: 2,
            en: {
                title: "CAPM prediction",
                text: "What does the CAPM predict about expected excess returns?",
                options: [
                    "They depend on total volatility",
                    "They depend on firm size and book-to-market",
                    "They are proportional to the market beta",
                    "They are equal for all assets"
                ],
                correctExplanation: "Under the CAPM, E[R_i] − R_f = β_i (E[R_m] − R_f): only exposure to market risk is rewarded.",
                incorrectExplanation: "Only beta is priced in the CAPM; total volatility, size or value should not matter."
            },
            ro: {
                title: "Predicția CAPM",
                text: "Ce prezice CAPM despre randamentele în exces așteptate?",
                options: [
                    "Depind de volatilitatea totală",
                    "Depind de mărimea firmei și de raportul book-to-market",
                    "Sunt proporționale cu beta de piață",
                    "Sunt egale pentru toate activele"
                ],
                correctExplanation: "Conform CAPM, E[R_i] − R_f = β_i (E[R_m] − R_f): doar expunerea la riscul de piață este remunerată.",
                incorrectExplanation: "În CAPM doar beta este remunerat; volatilitatea totală, mărimea sau valoarea nu ar trebui să conteze."
            }
        },
        {
            correct: 0,
            en: {
                title: "CML versus SML",
                text: "Which statement correctly distinguishes the CML from the SML?",
                options: [
                    "The CML contains only efficient portfolios in (volatility, mean); the SML contains every asset in (beta, mean)",
                    "The CML uses beta on the horizontal axis; the SML uses volatility",
                    "Both lines contain every individual asset",
                    "The SML only exists when there is no risk-free asset"
                ],
                correctExplanation: "The CML plots efficient combinations of the risk-free asset and the tangency portfolio against volatility; the SML plots every asset against beta if the CAPM holds.",
                incorrectExplanation: "The CML is in (volatility, mean) and holds only for efficient portfolios; the SML is in (beta, mean) and holds for all assets."
            },
            ro: {
                title: "CML versus SML",
                text: "Care afirmație distinge corect CML de SML?",
                options: [
                    "CML conține doar portofolii eficiente în (volatilitate, medie); SML conține orice activ în (beta, medie)",
                    "CML are beta pe axa orizontală; SML are volatilitatea",
                    "Ambele drepte conțin orice activ individual",
                    "SML există doar când nu există activ fără risc"
                ],
                correctExplanation: "CML reprezintă combinațiile eficiente dintre activul fără risc și portofoliul tangent în funcție de volatilitate; SML reprezintă orice activ în funcție de beta, dacă CAPM este adevărat.",
                incorrectExplanation: "CML este în (volatilitate, medie) și este valabilă doar pentru portofolii eficiente; SML este în (beta, medie) și este valabilă pentru toate activele."
            }
        },
        {
            correct: 1,
            en: {
                title: "Tangency portfolio",
                text: "Which portfolio maximises the Sharpe ratio among risky portfolios?",
                options: [
                    "The minimum-variance portfolio",
                    "The tangency portfolio, with weights proportional to Σ⁻¹μ",
                    "The equally weighted portfolio",
                    "The portfolio with the highest expected return"
                ],
                correctExplanation: "The tangency portfolio w ∝ Σ⁻¹μ (normalised to sum to one) has the highest excess return per unit of volatility.",
                incorrectExplanation: "The maximum Sharpe ratio is reached by the tangency portfolio, not by minimum variance, equal weights or maximum return."
            },
            ro: {
                title: "Portofoliul tangent",
                text: "Ce portofoliu maximizează raportul Sharpe dintre portofoliile riscante?",
                options: [
                    "Portofoliul de varianță minimă",
                    "Portofoliul tangent, cu ponderi proporționale cu Σ⁻¹μ",
                    "Portofoliul cu ponderi egale",
                    "Portofoliul cu cel mai mare randament așteptat"
                ],
                correctExplanation: "Portofoliul tangent w ∝ Σ⁻¹μ (normalizat la suma unu) are cel mai mare randament în exces pe unitatea de volatilitate.",
                incorrectExplanation: "Raportul Sharpe maxim este atins de portofoliul tangent, nu de varianța minimă, de ponderile egale sau de randamentul maxim."
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
            correct: 1,
            en: {
                title: "Blume adjustment",
                text: "Why are adjusted betas such as Blume’s 0.33 + 0.67β̂ used in practice?",
                options: [
                    "Because betas are always equal to one",
                    "Because extreme estimated betas contain noise and tend to move towards one in later periods",
                    "Because OLS betas are always too small",
                    "Because regulators require it"
                ],
                correctExplanation: "Regression to the mean: part of an extreme estimate is estimation error, so shrinking towards one improves forecasts; in the sector ETFs the RMSE fell from 0.135 to 0.109.",
                incorrectExplanation: "The adjustment exploits regression to the mean of noisy estimates; betas are not all equal to one."
            },
            ro: {
                title: "Ajustarea Blume",
                text: "De ce se folosesc în practică beta ajustate, precum regula Blume 0,33 + 0,67β̂?",
                options: [
                    "Pentru că beta este întotdeauna egal cu unu",
                    "Pentru că valorile beta extreme estimate conțin zgomot și tind spre unu în perioadele următoare",
                    "Pentru că beta OLS este mereu prea mic",
                    "Pentru că autoritățile de reglementare o cer"
                ],
                correctExplanation: "Regresia spre medie: o parte dintr-o estimație extremă este eroare, deci ajustarea spre unu îmbunătățește prognozele; la ETF-urile sectoriale RMSE a scăzut de la 0,135 la 0,109.",
                incorrectExplanation: "Ajustarea exploatează regresia spre medie a estimațiilor zgomotoase; valorile beta nu sunt toate egale cu unu."
            }
        },
        {
            correct: 2,
            en: {
                title: "BVB betas",
                text: "Which Bucharest Stock Exchange blue chip had the highest CAPM beta against BET in 2015–2026?",
                options: [
                    "Digi",
                    "Transelectrica",
                    "Banca Transilvania",
                    "Hidroelectrica"
                ],
                correctExplanation: "Banca Transilvania had a beta of 1.25 (R² 0.59); banks were the most market-sensitive stocks, while Digi had 0.67.",
                incorrectExplanation: "The banks had the highest betas: Banca Transilvania 1.25 and BRD 1.13; utilities and telecom had the lowest."
            },
            ro: {
                title: "Beta la BVB",
                text: "Care blue chip de la Bursa de Valori București a avut cel mai mare beta CAPM față de BET în 2015–2026?",
                options: [
                    "Digi",
                    "Transelectrica",
                    "Banca Transilvania",
                    "Hidroelectrica"
                ],
                correctExplanation: "Banca Transilvania a avut beta 1,25 (R² 0,59); băncile au fost cele mai sensibile la piață, iar Digi a avut 0,67.",
                incorrectExplanation: "Băncile au avut cele mai mari valori beta: Banca Transilvania 1,25 și BRD 1,13; utilitățile și telecomul au avut cele mai mici."
            }
        },
        {
            correct: 1,
            en: {
                title: "Jensen’s alpha",
                text: "What is Jensen’s alpha?",
                options: [
                    "The slope of the market model",
                    "The intercept of the regression of excess returns on market excess returns",
                    "The Sharpe ratio of an asset",
                    "The difference between two betas"
                ],
                correctExplanation: "In R^e_i = α_i + β_i R^e_m + ε, α_i is the average return not explained by market risk; the CAPM implies α_i = 0.",
                incorrectExplanation: "Alpha is the intercept of the market model, not a slope or a Sharpe ratio."
            },
            ro: {
                title: "Alfa lui Jensen",
                text: "Ce este alfa lui Jensen?",
                options: [
                    "Panta modelului de piață",
                    "Termenul liber al regresiei randamentelor în exces pe randamentele în exces ale pieței",
                    "Raportul Sharpe al unui activ",
                    "Diferența dintre două valori beta"
                ],
                correctExplanation: "În R^e_i = α_i + β_i R^e_m + ε, α_i este randamentul mediu neexplicat de riscul de piață; CAPM implică α_i = 0.",
                incorrectExplanation: "Alfa este termenul liber al modelului de piață, nu o pantă sau un raport Sharpe."
            }
        },
        {
            correct: 0,
            en: {
                title: "GRS test",
                text: "What does the Gibbons–Ross–Shanken (GRS) test examine?",
                options: [
                    "Whether all N alphas are jointly zero",
                    "Whether each beta equals one",
                    "Whether returns follow the Normal distribution",
                    "Whether the market premium is positive"
                ],
                correctExplanation: "GRS is a joint F-test of H0: α_1 = … = α_N = 0 that accounts for the correlation of residuals across assets.",
                incorrectExplanation: "GRS tests the alphas jointly; it is not a test of betas, normality or the sign of the premium."
            },
            ro: {
                title: "Testul GRS",
                text: "Ce verifică testul Gibbons–Ross–Shanken (GRS)?",
                options: [
                    "Dacă toate cele N valori alfa sunt simultan zero",
                    "Dacă fiecare beta este egal cu unu",
                    "Dacă randamentele urmează distribuția Normală",
                    "Dacă prima pieței este pozitivă"
                ],
                correctExplanation: "GRS este un test F comun pentru H0: α_1 = … = α_N = 0, care ține cont de corelația reziduurilor între active.",
                incorrectExplanation: "GRS testează valorile alfa împreună; nu este un test pentru beta, normalitate sau semnul primei."
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
                correctExplanation: "The Shanken variance multiplies the Fama–MacBeth variance by (1 + λ′Σ_f⁻¹λ) and adds Σ_f/T; for HML in FF3 the t-statistic fell from 2.98 to 2.12.",
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
                correctExplanation: "Varianța Shanken înmulțește varianța Fama–MacBeth cu (1 + λ′Σ_f⁻¹λ) și adaugă Σ_f/T; pentru HML în FF3, statistica t a scăzut de la 2,98 la 2,12.",
                incorrectExplanation: "Corecția tratează eroarea de estimare a valorilor beta folosite în a doua etapă."
            }
        },
        {
            correct: 1,
            en: {
                title: "Fama–French factors",
                text: "What do RMW and CMA measure in the Fama–French five-factor model?",
                options: [
                    "Momentum and market beta",
                    "Profitability (robust minus weak) and investment (conservative minus aggressive)",
                    "Size and book-to-market",
                    "Liquidity and volatility"
                ],
                correctExplanation: "RMW is high minus low operating profitability; CMA is low minus high asset growth. FF5 adds them to market, SMB and HML.",
                incorrectExplanation: "Size and value are SMB and HML; RMW and CMA are profitability and investment."
            },
            ro: {
                title: "Factorii Fama–French",
                text: "Ce măsoară RMW și CMA în modelul Fama–French cu cinci factori?",
                options: [
                    "Momentum și beta de piață",
                    "Profitabilitatea (robust minus weak) și investițiile (conservative minus aggressive)",
                    "Mărimea și book-to-market",
                    "Lichiditatea și volatilitatea"
                ],
                correctExplanation: "RMW este profitabilitate operațională mare minus mică; CMA este creștere mică minus mare a activelor. FF5 îi adaugă la piață, SMB și HML.",
                incorrectExplanation: "Mărimea și valoarea sunt SMB și HML; RMW și CMA sunt profitabilitatea și investițiile."
            }
        },
        {
            correct: 2,
            en: {
                title: "Momentum",
                text: "How is the momentum factor (MOM) typically formed?",
                options: [
                    "Long stocks with the lowest past-month return",
                    "Long stocks with high book-to-market",
                    "Long past winners and short past losers, using returns from month t−12 to t−2",
                    "Long the stocks with the lowest beta"
                ],
                correctExplanation: "Momentum (Jegadeesh and Titman, 1993; Carhart, 1997) sorts on the past year’s return, skipping the most recent month.",
                incorrectExplanation: "Momentum sorts on past returns over roughly the previous year, not on value or beta."
            },
            ro: {
                title: "Momentum",
                text: "Cum se construiește de obicei factorul momentum (MOM)?",
                options: [
                    "Long acțiunile cu cel mai mic randament în luna trecută",
                    "Long acțiunile cu book-to-market mare",
                    "Long câștigătorii trecuți și short perdanții trecuți, după randamentele din luna t−12 până în t−2",
                    "Long acțiunile cu cel mai mic beta"
                ],
                correctExplanation: "Momentum (Jegadeesh și Titman, 1993; Carhart, 1997) sortează după randamentul ultimului an, sărind peste luna cea mai recentă.",
                incorrectExplanation: "Momentum sortează după randamentele din aproximativ ultimul an, nu după valoare sau beta."
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
                title: "PCA share",
                text: "Two standardised returns have correlation 0.6. What share of the total variance does the first principal component explain?",
                options: [
                    "60%",
                    "50%",
                    "40%",
                    "80%"
                ],
                correctExplanation: "The eigenvalues are 1 ± ρ = 1.6 and 0.4; the first explains 1.6/2 = 80%.",
                incorrectExplanation: "For two assets the first eigenvalue is 1 + ρ, and its share is (1 + ρ)/2."
            },
            ro: {
                title: "Ponderea PCA",
                text: "Două randamente standardizate au corelația 0,6. Ce pondere din varianța totală explică prima componentă principală?",
                options: [
                    "60%",
                    "50%",
                    "40%",
                    "80%"
                ],
                correctExplanation: "Valorile proprii sunt 1 ± ρ = 1,6 și 0,4; prima explică 1,6/2 = 80%.",
                incorrectExplanation: "Pentru două active prima valoare proprie este 1 + ρ, iar ponderea ei este (1 + ρ)/2."
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

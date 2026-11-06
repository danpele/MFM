// ============================================================
// Quiz bank for chapter id 'factors': Factor Models and Asset Pricing (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['factors'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 1,
            "en": {
                "title": "GRS in Sharpe-ratio form",
                "text": "With maximum-likelihood moments, the GRS quadratic form α̂′Σ̂⁻¹α̂ equals…",
                "options": [
                    "The average squared alpha across the test assets, with equal weights",
                    "The gain in the maximum squared Sharpe ratio from adding the test assets to the factors",
                    "The average R² of the time-series regressions of the test assets",
                    "The squared Sharpe ratio of the factors alone, SR²(factors)"
                ],
                "correctExplanation": "By the partitioned inverse of the covariance of (f, R), μ′V⁻¹μ = SR²(f) + α′Σ⁻¹α. On the 25 portfolios the monthly Sharpe ratio rises from 0.134 to 0.405, and GRS = 4.20.",
                "incorrectExplanation": "The quadratic form weights the alphas by Σ̂⁻¹ and equals the increase in the tangency Sharpe ratio squared when the test assets are added to the factors."
            },
            "ro": {
                "title": "GRS în forma raportului Sharpe",
                "text": "Cu momente de verosimilitate maximă, forma pătratică GRS α̂′Σ̂⁻¹α̂ este egală cu…",
                "options": [
                    "Media pătratelor valorilor alfa ale activelor de test, cu ponderi egale",
                    "Cîștigul de raport Sharpe maxim la pătrat cînd activele de test se adaugă la factori",
                    "Media R² a regresiilor în serii de timp ale activelor de test",
                    "Pătratul raportului Sharpe al factorilor singuri, SR²(factori)"
                ],
                "correctExplanation": "Din inversa partiționată a covarianței lui (f, R), μ′V⁻¹μ = SR²(f) + α′Σ⁻¹α. Pe cele 25 de portofolii, raportul Sharpe lunar crește de la 0,134 la 0,405, iar GRS = 4,20.",
                "incorrectExplanation": "Forma pătratică ponderează valorile alfa cu Σ̂⁻¹ și este egală cu creșterea pătratului raportului Sharpe tangent cînd activele de test se adaugă la factori."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "A skeptical appraisal of R²",
                "text": "A new three-factor model reaches a cross-sectional R² of 80% on the 25 size × B/M portfolios. Why is this weak evidence (Lewellen, Nagel and Shanken, 2010)?",
                "options": [
                    "Because 25 portfolios are too many test assets for a two-pass regression with three factors",
                    "Because a credible cross-sectional R² must exceed 95%",
                    "Because the OLS R² is always about 80% on these portfolios, whatever the factors",
                    "Because many models that capture size and value comovement fit these portfolios"
                ],
                "correctExplanation": "On portfolios sorted on the same characteristics, many models that capture the common size and value variation reach a high cross-sectional R². In the lecture FF3 goes from 0.66 to 0.22 (OLS) and from 0.21 to 0.08 (GLS) when 30 industries are added to the 25 portfolios.",
                "incorrectExplanation": "A high OLS R² on the 25 size × B/M portfolios is a low hurdle: three factors explain most of their variation, so many factor sets fit their means."
            },
            "ro": {
                "title": "O evaluare sceptică a lui R²",
                "text": "Un nou model cu trei factori atinge un R² transversal de 80% pe cele 25 de portofolii mărime × B/M. De ce este o dovadă slabă (Lewellen, Nagel și Shanken, 2010)?",
                "options": [
                    "Pentru că 25 de portofolii sînt prea multe active de test pentru o regresie în două etape",
                    "Pentru că un R² transversal credibil trebuie să depășească 95%",
                    "Pentru că R² OLS este mereu de circa 80% pe aceste portofolii, oricare ar fi factorii",
                    "Pentru că multe modele care surprind variația comună de mărime și valoare le explică"
                ],
                "correctExplanation": "Pe portofolii sortate după aceleași caracteristici, multe modele care surprind variația comună de mărime și valoare obțin un R² transversal ridicat. În curs, FF3 scade de la 0,66 la 0,22 (OLS) și de la 0,21 la 0,08 (GLS) cînd se adaugă 30 de portofolii pe industrii celor 25.",
                "incorrectExplanation": "Un R² OLS mare pe cele 25 de portofolii mărime × B/M este un criteriu puțin exigent: trei factori explică cea mai mare parte a variației lor, deci multe seturi de factori le reproduc mediile."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Useless factor",
                "text": "A macroeconomic factor is statistically independent of all returns. In a two-pass regression with a misspecified model, its estimated premium λ̂…",
                "options": [
                    "Can look significant, because the betas on a useless factor are pure estimation noise",
                    "Is exactly zero, because the factor is uncorrelated with returns",
                    "Is always insignificant, because its standard error grows with the noise",
                    "Equals the time-series mean of the factor, as for any factor"
                ],
                "correctExplanation": "Kan and Zhang (1999): pass 2 divides by noise, so λ̂ does not converge to zero. In the lecture simulation λ = 0 was rejected in 60% of the replications with Fama–MacBeth errors at the 5% level.",
                "incorrectExplanation": "Independence from returns does not protect pass 2: the betas are estimated with noise and the premium estimate inherits a non-vanishing error; test the first-pass betas first."
            },
            "ro": {
                "title": "Factor inutil",
                "text": "Un factor macroeconomic este statistic independent de toate randamentele. Într-o regresie în două etape cu un model greșit specificat, prima lui estimată λ̂…",
                "options": [
                    "Poate părea semnificativă, pentru că valorile beta pe un factor inutil sînt doar zgomot de estimare",
                    "Este exact zero, pentru că factorul nu este corelat cu randamentele",
                    "Este mereu nesemnificativă, pentru că eroarea ei standard crește odată cu zgomotul",
                    "Este egală cu media factorului în timp, ca pentru orice factor"
                ],
                "correctExplanation": "Kan și Zhang (1999): etapa 2 împarte la zgomot, deci λ̂ nu converge la zero. În simularea din curs, λ = 0 a fost respins în 60% din replicări cu erori Fama–MacBeth, la nivelul de 5%.",
                "incorrectExplanation": "Independența față de randamente nu protejează etapa 2: valorile beta sînt estimate cu zgomot, iar prima estimată moștenește o eroare care nu dispare; testați întîi valorile beta din prima etapă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Newey–West errors",
                "text": "In the monthly regression of XLK on the market (1999–2026), what changes when the classical standard errors are replaced by Newey–West errors?",
                "options": [
                    "The OLS estimate of beta, which becomes robust to fat tails",
                    "The estimated covariance matrix of the coefficients, not the OLS beta",
                    "Both beta and its standard error, by the same proportion",
                    "The sample, because the first lags are dropped"
                ],
                "correctExplanation": "Beta stays at 1.277; the standard error goes from 0.041 (classical) to 0.054 (White) and 0.082 (Newey–West, 5 lags). HAC errors allow for heteroskedasticity and autocorrelation; they need not be larger in every sample.",
                "incorrectExplanation": "Newey–West changes only the estimated variance of the coefficients; the OLS point estimate and the sample are the same."
            },
            "ro": {
                "title": "Erori Newey–West",
                "text": "În regresia lunară a XLK pe piață (1999–2026), ce se schimbă cînd erorile standard clasice sînt înlocuite cu erori Newey–West?",
                "options": [
                    "Estimația OLS a lui beta, care devine robustă la cozi groase",
                    "Matricea de covarianță estimată a coeficienților, nu beta OLS",
                    "Atît beta, cît și eroarea lui standard, în aceeași proporție",
                    "Eșantionul, pentru că primele laguri sînt eliminate"
                ],
                "correctExplanation": "Beta rămîne 1,277; eroarea standard trece de la 0,041 (clasică) la 0,054 (White) și 0,082 (Newey–West, 5 laguri). Erorile HAC țin cont de heteroscedasticitate și de autocorelație; ele nu sînt obligatoriu mai mari în orice eșantion.",
                "incorrectExplanation": "Newey–West schimbă doar varianța estimată a coeficienților; estimația punctuală OLS și eșantionul rămîn aceleași."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Vasicek: the prior variance estimated from the data",
                "text": "The estimated betas of the 9 sector ETFs have a cross-sectional variance of 0.1159, and their average squared standard error is 0.0077. Which prior variance σ²_β should the Vasicek estimator use?",
                "options": [
                    "0.1159",
                    "0.1236",
                    "0.1082",
                    "0.0077"
                ],
                "correctExplanation": "Var_cs(β̂) = σ²_β + mean se², because estimation noise adds to the dispersion of the true betas; hence σ²_β = 0.1159 − 0.0077 = 0.1082, as in the lecture.",
                "incorrectExplanation": "The variance of the estimated betas includes their sampling noise; the prior must describe the true betas, so subtract the average squared standard error."
            },
            "ro": {
                "title": "Vasicek: varianța a priori, estimată din date",
                "text": "Valorile beta estimate ale celor 9 ETF-uri sectoriale au varianța transversală 0,1159, iar media pătratelor erorilor lor standard este 0,0077. Ce varianță a priori σ²_β trebuie să folosească estimatorul Vasicek?",
                "options": [
                    "0,1159",
                    "0,1236",
                    "0,1082",
                    "0,0077"
                ],
                "correctExplanation": "Var_cs(β̂) = σ²_β + media se², pentru că zgomotul de estimare se adaugă dispersiei valorilor beta adevărate; deci σ²_β = 0,1159 − 0,0077 = 0,1082, ca în curs.",
                "incorrectExplanation": "Varianța valorilor beta estimate include zgomotul de eșantionare; informația a priori trebuie să descrie parametrii β_i, nu estimările, deci se scade media pătratelor erorilor standard."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Nonsynchronous trading",
                "text": "Daily OLS betas of thinly traded Bucharest Stock Exchange stocks on the BET index are…",
                "options": [
                    "Biased upwards, because illiquid stocks react with a lag",
                    "Biased towards zero; the Dimson sum b₋₁ + b₀ + b₊₁ recovers part of the lag",
                    "Unbiased, because OLS is unbiased whatever the trading frequency",
                    "Undefined on the days when a stock does not trade at all"
                ],
                "correctExplanation": "Stale prices spread the reaction to market news over several days. In the seminar the Dimson beta of Nuclearelectrica rises from 0.80 to 0.94 and that of Digi from 0.67 to 0.75.",
                "incorrectExplanation": "A stock that trades late reacts to today's market move tomorrow, so the contemporaneous covariance understates its beta; the Dimson beta adds the lagged, contemporaneous and leading slopes, b₋₁ + b₀ + b₊₁."
            },
            "ro": {
                "title": "Tranzacționare asincronă",
                "text": "Valorile beta OLS zilnice ale acțiunilor puțin lichide de la Bursa de Valori București față de indicele BET sînt…",
                "options": [
                    "Deplasate în sus, pentru că acțiunile puțin lichide reacționează cu întîrziere",
                    "Deplasate spre zero; suma Dimson b₋₁ + b₀ + b₊₁ recuperează o parte a întîrzierii",
                    "Nedeplasate, pentru că OLS este nedeplasat la orice frecvență de tranzacționare",
                    "Nedefinite în zilele în care acțiunea nu se tranzacționează deloc"
                ],
                "correctExplanation": "Prețurile stale (neactualizate) distribuie reacția la știrile pieței pe mai multe zile. În seminar, beta Dimson al Nuclearelectrica crește de la 0,80 la 0,94, iar al Digi de la 0,67 la 0,75.",
                "incorrectExplanation": "O acțiune care se tranzacționează cu întîrziere reacționează mîine la mișcarea de azi a pieței, deci covarianța contemporană subestimează beta; beta Dimson adună panta întîrziată, cea contemporană și cea anticipată, b₋₁ + b₀ + b₊₁."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Traded-factor premium",
                "text": "For a traded factor, the two-pass premium λ̂ is far from the factor's time-series mean (market: −6.5% vs +7.2% a year in FF3 on the 25 portfolios). What does this indicate?",
                "options": [
                    "That the factor is not really traded on an exchange",
                    "That the time-series mean of the factor is biased",
                    "That the Shanken standard errors are too small",
                    "A wrong model, or betas too close together to identify λ"
                ],
                "correctExplanation": "A traded factor prices itself, so in a correct model λ equals E[f]. In FF3 the market betas span only 0.89–1.14 on the 25 portfolios, so the slope on them is imprecise and the intercept absorbs the level of returns: λ_m is weakly identified.",
                "incorrectExplanation": "The gap is a diagnostic about the model and the test assets, not about the factor mean or the standard errors."
            },
            "ro": {
                "title": "Prima unui factor tranzacționat",
                "text": "Pentru un factor tranzacționat, prima λ̂ din cele două etape este departe de media factorului în timp (piața: −6,5% față de +7,2% pe an în FF3, pe cele 25 de portofolii). Ce indică acest lucru?",
                "options": [
                    "Că factorul nu este de fapt tranzacționat la bursă",
                    "Că media în timp a factorului este deplasată",
                    "Că erorile standard Shanken sînt prea mici pentru acest eșantion",
                    "Un model greșit sau valori beta prea apropiate pentru a identifica λ"
                ],
                "correctExplanation": "Un factor tranzacționat se evaluează pe sine, deci, într-un model corect, λ este egal cu E[f]. În FF3, valorile beta de piață acoperă doar 0,89–1,14 pe cele 25 de portofolii, deci panta pe ele este imprecisă, iar termenul liber preia nivelul randamentelor: λ_m este slab identificat.",
                "incorrectExplanation": "Diferența este un diagnostic despre model și activele de test, nu despre media factorului sau erorile standard."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Large-N alpha test",
                "text": "You want to test the alphas of N = 100 portfolios using T = 96 monthly returns. What happens to the GRS test?",
                "options": [
                    "It cannot be computed: the residual covariance matrix is singular",
                    "It is valid but has low power, because T is short",
                    "It is valid if the residuals follow the Normal distribution",
                    "It is valid once Newey–West errors replace the classical ones"
                ],
                "correctExplanation": "Σ̂ is built from T residual vectors with two estimated parameters, so its rank is at most T − 2 = 94 < 100 and Σ̂⁻¹ does not exist. Use a large-N test instead, such as Pesaran–Yamagata.",
                "incorrectExplanation": "The problem is not power or normality: Σ̂⁻¹ does not exist when N ≥ T − 1, and GRS needs it."
            },
            "ro": {
                "title": "Test de alfa pentru N mare",
                "text": "Vreți să testați valorile alfa pentru N = 100 de portofolii cu T = 96 de randamente lunare. Ce se întîmplă cu testul GRS?",
                "options": [
                    "Nu se poate calcula: matricea de covarianță a reziduurilor este singulară",
                    "Este valid, dar are putere mică, pentru că T este scurt",
                    "Este valid dacă reziduurile urmează distribuția Normală",
                    "Este valid dacă erorile Newey–West înlocuiesc erorile clasice"
                ],
                "correctExplanation": "Σ̂ este construită din T vectori de reziduuri cu doi parametri estimați, deci rangul ei este cel mult T − 2 = 94 < 100, iar Σ̂⁻¹ nu există. Se folosește atunci un test pentru N mare, precum Pesaran–Yamagata.",
                "incorrectExplanation": "Problema nu este puterea sau normalitatea: Σ̂⁻¹ nu există cînd N ≥ T − 1, iar GRS are nevoie de ea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Low power",
                "text": "Over the same 331 months, the GRS test does not reject the CAPM on 9 US sector ETFs (p = 0.85) but rejects it on the 25 size × B/M portfolios (GRS = 2.91). What is the most plausible explanation of the contrast?",
                "options": [
                    "Sector ETFs are priced more efficiently than size and value portfolios",
                    "The CAPM holds for sectors but not for small value stocks",
                    "Sectors barely spread size and value, so the test has little power",
                    "The sector test uses a longer sample, so its result is more reliable"
                ],
                "correctExplanation": "Test assets must spread the characteristics that carry premia; sectors mix small and big, value and growth stocks. Not rejecting is weak evidence.",
                "incorrectExplanation": "Both tests use the same months. Not rejecting does not confirm the CAPM; the sectors are not built to contrast the characteristics that the CAPM fails to price."
            },
            "ro": {
                "title": "Putere redusă",
                "text": "Pe aceleași 331 de luni, testul GRS nu respinge CAPM pe 9 ETF-uri sectoriale din SUA (p = 0,85), dar îl respinge pe cele 25 de portofolii mărime × B/M (GRS = 2,91). Care este explicația cea mai plauzibilă a contrastului?",
                "options": [
                    "ETF-urile sectoriale sînt evaluate mai eficient decît portofoliile pe mărime și valoare",
                    "CAPM este valabil pentru sectoare, dar nu și pentru firmele mici de valoare",
                    "Sectoarele aproape nu diferă după mărime și valoare, deci testul are putere mică",
                    "Testul pe sectoare folosește un eșantion mai lung, deci rezultatul lui este mai sigur"
                ],
                "correctExplanation": "Activele de test trebuie să aibă dispersie mare în caracteristicile care aduc o primă; sectoarele combină firme mici și mari, de valoare și de creștere. Nerespingerea este o dovadă slabă.",
                "incorrectExplanation": "Ambele teste folosesc aceleași luni. Nerespingerea nu confirmă CAPM; sectoarele nu sînt construite pentru a contrasta caracteristicile pe care CAPM nu le evaluează."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Flat SML",
                "text": "On the 25 size × B/M portfolios (1963–2026), the fitted cross-sectional line of average excess returns on CAPM betas has slope −4.4% a year. What does this mean?",
                "options": [
                    "The market risk premium was negative over the sample",
                    "The betas were estimated with the wrong sign",
                    "The CAPM holds exactly for these portfolios",
                    "Higher-beta portfolios did not earn higher average returns"
                ],
                "correctExplanation": "The CAPM predicts a slope equal to the premium (7.2%); a flat or negative SML is the classic empirical failure, explained for example by leverage constraints (Black; Frazzini–Pedersen).",
                "incorrectExplanation": "The time-series market premium was positive (7.2%); the failure is that beta does not explain the cross section."
            },
            "ro": {
                "title": "SML plată",
                "text": "Pe cele 25 de portofolii mărime × B/M (1963–2026), dreapta transversală a randamentelor medii în exces în funcție de beta CAPM are panta −4,4% pe an. Ce înseamnă?",
                "options": [
                    "Prima de risc a pieței a fost negativă în eșantion",
                    "Valorile beta au fost estimate cu semn greșit în prima etapă",
                    "CAPM este exact adevărat pentru aceste portofolii",
                    "Portofoliile cu beta mare nu au avut randamente medii mai mari"
                ],
                "correctExplanation": "CAPM prezice o pantă egală cu prima (7,2%); o SML plată sau negativă este eșecul empiric clasic, explicat de exemplu prin constrîngerile de levier (Black; Frazzini–Pedersen).",
                "incorrectExplanation": "Prima pieței în timp a fost pozitivă (7,2%); eșecul constă în faptul că beta nu explică secțiunea transversală."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Betting against beta",
                "text": "How is the BAB (Betting Against Beta) factor of Frazzini and Pedersen built?",
                "options": [
                    "Long high-beta stocks and short low-beta stocks, without leverage",
                    "Long levered low-beta stocks, short de-levered high-beta stocks: beta zero",
                    "Long the market portfolio and short the risk-free asset",
                    "Long small stocks and short big stocks, with equal weights"
                ],
                "correctExplanation": "r_BAB = (R_L − R_f)/β_L − (R_H − R_f)/β_H: each of the two portfolios is rescaled to beta one, so the long-minus-short difference has an estimated beta of zero.",
                "incorrectExplanation": "r_BAB = (R_L − R_f)/β_L − (R_H − R_f)/β_H: each of the two portfolios is rescaled to beta one, so the long-minus-short difference has an estimated beta of zero."
            },
            "ro": {
                "title": "Betting against beta",
                "text": "Cum este construit factorul BAB (Betting Against Beta) al lui Frazzini și Pedersen?",
                "options": [
                    "Long acțiuni cu beta mare și short acțiuni cu beta mic, fără levier",
                    "Long acțiuni cu beta mic, cu levier, și short acțiuni cu beta mare: beta zero",
                    "Long portofoliul pieței și short activul fără risc",
                    "Long firme mici și short firme mari, cu ponderi egale"
                ],
                "correctExplanation": "r_BAB = (R_L − R_f)/β_L − (R_H − R_f)/β_H: fiecare dintre cele două portofolii este redimensionat la beta unu, deci diferența long minus short are beta estimat zero.",
                "incorrectExplanation": "r_BAB = (R_L − R_f)/β_L − (R_H − R_f)/β_H: fiecare dintre cele două portofolii este redimensionat la beta unu, deci diferența long minus short are beta estimat zero."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Roll’s critique",
                "text": "What is Roll’s (1977) critique of CAPM tests?",
                "options": [
                    "The true market portfolio is unobservable, so the test also tests the proxy",
                    "Betas cannot be estimated by OLS when returns are autocorrelated",
                    "The risk-free rate is not constant over a long sample",
                    "Monthly data are too noisy to estimate any expected return"
                ],
                "correctExplanation": "Any mean–variance efficient portfolio prices all assets exactly by beta, so rejecting the CAPM with a stock index may only reject the efficiency of that index.",
                "incorrectExplanation": "The critique is about the unobservable market portfolio, not about estimation methods or data frequency."
            },
            "ro": {
                "title": "Critica lui Roll",
                "text": "În ce constă critica lui Roll (1977) la testele CAPM?",
                "options": [
                    "Adevăratul portofoliu al pieței nu se observă, deci testul verifică și aproximarea lui",
                    "Beta nu poate fi estimat prin OLS cînd randamentele sînt autocorelate",
                    "Rata fără risc nu este constantă pe un eșantion lung",
                    "Datele lunare sînt prea zgomotoase pentru a estima vreun randament așteptat"
                ],
                "correctExplanation": "Orice portofoliu eficient medie–varianță evaluează exact toate activele prin beta, deci respingerea CAPM cu un indice bursier poate respinge doar eficiența acelui indice.",
                "incorrectExplanation": "Critica privește portofoliul pieței neobservabil, nu metodele de estimare sau frecvența datelor."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Fama–MacBeth",
                "text": "In the second pass of a Fama–MacBeth regression, what is estimated?",
                "options": [
                    "One time-series regression of each asset on the factors",
                    "One cross-sectional regression per period; the premia average the slopes",
                    "The covariance matrix of the factors over the sample",
                    "The GRS statistic for all test assets jointly"
                ],
                "correctExplanation": "Pass 1 estimates betas; pass 2 runs T cross-sectional regressions and averages the slopes λ̂_t; the standard error is their standard deviation divided by √T (Newey–West if the slopes are autocorrelated).",
                "incorrectExplanation": "The time-series betas come from the first pass; the second pass is cross-sectional, period by period."
            },
            "ro": {
                "title": "Fama–MacBeth",
                "text": "Ce se estimează în a doua etapă a unei regresii Fama–MacBeth?",
                "options": [
                    "Cîte o regresie în serii de timp a fiecărui activ pe factori",
                    "Cîte o regresie transversală pe perioadă; primele sînt mediile pantelor",
                    "Matricea de covarianță a factorilor pe tot eșantionul",
                    "Statistica GRS pentru toate activele de test simultan"
                ],
                "correctExplanation": "Etapa 1 estimează beta; etapa 2 face T regresii transversale și calculează media pantelor λ̂_t; eroarea standard este abaterea lor standard împărțită la √T (Newey–West dacă pantele sînt autocorelate).",
                "incorrectExplanation": "Beta din serii de timp provine din prima etapă; a doua etapă este transversală, perioadă cu perioadă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Shanken correction",
                "text": "Why is the Shanken correction applied to Fama–MacBeth standard errors?",
                "options": [
                    "To correct for the autocorrelation of monthly returns",
                    "To make the estimated risk premia positive",
                    "To correct for the non-Normal distribution of returns",
                    "Because the betas are estimated, not known"
                ],
                "correctExplanation": "Var_Sh = (1 + c)(Var_FM − Σ_f/T) + Σ_f/T with c = λ′Σ_f⁻¹λ: only the errors-in-variables part is scaled. With monthly traded factors c is small (0.03 for FF3), so HML keeps t ≈ 2.99.",
                "incorrectExplanation": "The correction addresses the estimation error in the betas used in the second pass."
            },
            "ro": {
                "title": "Corecția Shanken",
                "text": "De ce se aplică erorilor standard Fama–MacBeth corecția Shanken?",
                "options": [
                    "Pentru a corecta autocorelația randamentelor lunare",
                    "Pentru a face pozitive primele de risc estimate",
                    "Pentru a corecta abaterile randamentelor de la distribuția Normală",
                    "Pentru că valorile beta sînt estimate, nu cunoscute"
                ],
                "correctExplanation": "Var_Sh = (1 + c)(Var_FM − Σ_f/T) + Σ_f/T, cu c = λ′Σ_f⁻¹λ: doar partea datorată erorilor în variabile este scalată. Pentru factori tranzacționați lunari c este mic (0,03 pentru FF3), deci HML păstrează t ≈ 2,99.",
                "incorrectExplanation": "Corecția tratează eroarea de estimare a valorilor beta folosite în a doua etapă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Comparing models",
                "text": "Barillas and Shanken (2018): which test assets are needed to compare two factor models whose factors are traded excess returns?",
                "options": [
                    "The 25 size × B/M portfolios, as in Fama and French",
                    "None: compare the maximum squared Sharpe ratios of the factors",
                    "The 30 industry portfolios, to avoid the size–value structure",
                    "All individual stocks, to avoid sorting on characteristics"
                ],
                "correctExplanation": "A model's ability to price any asset is summarised by SR²(f) of its factors. In the lecture FF5 and Carhart both reach an annual Sharpe ratio of 0.97 over 1963–2026.",
                "incorrectExplanation": "The comparison is done on the factors: test assets add the same information to both models and cancel out."
            },
            "ro": {
                "title": "Compararea modelelor",
                "text": "Barillas și Shanken (2018): ce active de test sînt necesare pentru a compara două modele factoriale ai căror factori sînt randamente în exces tranzacționate?",
                "options": [
                    "Cele 25 de portofolii mărime × B/M, ca la Fama și French",
                    "Niciunul: se compară rapoartele Sharpe maxime la pătrat ale factorilor",
                    "Cele 30 de portofolii pe industrii, pentru a evita structura mărime–valoare",
                    "Toate acțiunile individuale, pentru a evita sortarea după caracteristici"
                ],
                "correctExplanation": "Capacitatea unui model de a evalua orice activ este rezumată de SR²(f) al factorilor săi. În curs, FF5 și Carhart ating amîndouă un raport Sharpe anual de 0,97 în 1963–2026.",
                "incorrectExplanation": "Comparația se face pe factori: activele de test adaugă aceeași informație ambelor modele și se anulează."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Premium decay",
                "text": "What happened to the momentum premium after 2000 in the Kenneth French data?",
                "options": [
                    "It roughly doubled, to about 20% a year",
                    "It stayed close to 10% a year, as before 2000",
                    "It became the largest of the six factor premia",
                    "It fell from about 10.7% to 2.5% a year"
                ],
                "correctExplanation": "Its t-statistic fell from 5.5 to 0.75. Momentum was strong in 1963–1999 but weak in 2000–2026, including the 2009 crash; McLean and Pontiff document such post-publication declines.",
                "incorrectExplanation": "The data show a strong decline of the momentum premium after 2000."
            },
            "ro": {
                "title": "Scăderea primelor",
                "text": "Ce s-a întîmplat cu prima de momentum după 2000, în datele Kenneth French?",
                "options": [
                    "Aproape s-a dublat, la circa 20% pe an",
                    "A rămas aproape de 10% pe an, ca înainte de 2000",
                    "A devenit cea mai mare dintre primele celor șase factori",
                    "A scăzut de la aproximativ 10,7% la 2,5% pe an"
                ],
                "correctExplanation": "Statistica t a scăzut de la 5,5 la 0,75. Momentum a fost puternic în 1963–1999, dar slab în 2000–2026, inclusiv crahul din 2009; McLean și Pontiff documentează astfel de scăderi după publicare.",
                "incorrectExplanation": "Datele arată o scădere puternică a primei de momentum după 2000."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Factor zoo",
                "text": "With 300 independent factors that have no true premium, how many would you expect to pass |t| > 1.96?",
                "options": [
                    "About 15",
                    "About 0",
                    "About 3",
                    "About 150"
                ],
                "correctExplanation": "300 × 0.05 = 15 false discoveries on average; the simulation in the lecture gives 15.0.",
                "incorrectExplanation": "Each useless factor passes the 5% test with probability 0.05, so 300 tests give about 15 false discoveries."
            },
            "ro": {
                "title": "Factor zoo",
                "text": "Cu 300 de factori independenți fără primă reală, cîți v-ați aștepta să treacă pragul |t| > 1,96?",
                "options": [
                    "Aproximativ 15",
                    "Aproximativ 0",
                    "Aproximativ 3",
                    "Aproximativ 150"
                ],
                "correctExplanation": "300 × 0,05 = 15 descoperiri false în medie; simularea din curs dă 15,0.",
                "incorrectExplanation": "Fiecare factor inutil trece testul de 5% cu probabilitatea 0,05, deci 300 de teste dau aproximativ 15 descoperiri false."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Multiple testing",
                "text": "Which procedure targets the false discovery rate (the expected share of false rejections among rejections) directly, allowing more discoveries than family-wise error control?",
                "options": [
                    "Bonferroni",
                    "Benjamini–Hochberg",
                    "Holm",
                    "The naive 5% test"
                ],
                "correctExplanation": "Benjamini–Hochberg rejects the hypotheses up to the largest j with p_(j) ≤ jα/M and controls the FDR for independent tests or under positive regression dependence; Bonferroni and Holm control the stricter family-wise error rate.",
                "incorrectExplanation": "Bonferroni and Holm control the probability of any false rejection (FWER); since FDR ≤ FWER they also bound the FDR, but they are more conservative and do not target it."
            },
            "ro": {
                "title": "Testare multiplă",
                "text": "Ce procedură vizează direct rata descoperirilor false (ponderea așteptată a respingerilor false în totalul respingerilor), permițînd mai multe descoperiri decît controlul erorii pe familie?",
                "options": [
                    "Bonferroni",
                    "Benjamini–Hochberg",
                    "Holm",
                    "Testul naiv de 5%"
                ],
                "correctExplanation": "Benjamini–Hochberg respinge ipotezele pînă la cel mai mare j cu p_(j) ≤ jα/M și controlează FDR pentru teste independente sau sub dependență de regresie pozitivă; Bonferroni și Holm controlează rata erorii pe familie, mai strictă.",
                "incorrectExplanation": "Bonferroni și Holm controlează probabilitatea oricărei respingeri false (FWER); deoarece FDR ≤ FWER, ele limitează și FDR, dar sînt mai conservatoare și nu îl vizează."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The t > 3 hurdle",
                "text": "Why do Harvey, Liu and Zhu (2016) propose a t-statistic above 3 for new factors?",
                "options": [
                    "Because returns are assumed to follow the Normal distribution",
                    "Because factor returns are always large in absolute value",
                    "Because hundreds of factors have been tried on the same data",
                    "Because Fama–MacBeth standard errors are too large"
                ],
                "correctExplanation": "Multiple testing raises the bar: with 300 useless factors the best one has a median |t| of about 3.06.",
                "incorrectExplanation": "The higher hurdle is a multiple-testing correction for the factor zoo."
            },
            "ro": {
                "title": "Pragul t > 3",
                "text": "De ce propun Harvey, Liu și Zhu (2016) o statistică t peste 3 pentru factorii noi?",
                "options": [
                    "Pentru că se presupune că randamentele urmează distribuția Normală",
                    "Pentru că randamentele factorilor sînt mereu mari în valoare absolută",
                    "Pentru că sute de factori au fost încercați pe aceleași date",
                    "Pentru că erorile standard Fama–MacBeth sînt prea mari"
                ],
                "correctExplanation": "Testarea multiplă impune un prag mai ridicat: cu 300 de factori inutili, cel mai bun are un |t| median de aproximativ 3,06.",
                "incorrectExplanation": "Pragul mai mare este o corecție pentru testarea multiplă din factor zoo."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Size of the Shanken correction",
                "text": "One traded factor with a monthly premium λ = 0.5% and monthly volatility σ_f = 4.5%. By how much does Shanken's factor (1 + c), c = λ²/σ_f², inflate the errors-in-variables part of the Fama–MacBeth variance?",
                "options": [
                    "By about 11%",
                    "By about 0.5%",
                    "By about 50%",
                    "By about 1.2%"
                ],
                "correctExplanation": "c = (0.005/0.045)² = 0.012: with monthly traded factors the correction is small; the lecture finds c = 0.03 for FF3, and HML's standard error barely changes.",
                "incorrectExplanation": "c is the squared Sharpe ratio of the premium per period, not the Sharpe ratio itself; monthly Sharpe ratios are small, so c is small."
            },
            "ro": {
                "title": "Mărimea corecției Shanken",
                "text": "Un factor tranzacționat are prima lunară λ = 0,5% și volatilitatea lunară σ_f = 4,5%. Cu cît mărește factorul Shanken (1 + c), c = λ²/σ_f², partea din varianța Fama–MacBeth datorată erorilor în variabile?",
                "options": [
                    "Cu aproximativ 11%",
                    "Cu aproximativ 0,5%",
                    "Cu aproximativ 50%",
                    "Cu aproximativ 1,2%"
                ],
                "correctExplanation": "c = (0,005/0,045)² = 0,012: pentru factori tranzacționați lunari corecția este mică; cursul găsește c = 0,03 pentru FF3, iar eroarea standard a HML aproape nu se schimbă.",
                "incorrectExplanation": "c este pătratul raportului Sharpe al primei pe perioadă, nu raportul Sharpe însuși; rapoartele Sharpe lunare sînt mici, deci c este mic."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Factor ETFs",
                "text": "After regressing MTUM and VLUE on the FF5 + momentum factors, what did the lecture find?",
                "options": [
                    "Large positive alphas, of about 5% a year",
                    "Market betas close to zero for all the ETFs",
                    "Alphas near zero; loadings match the labels",
                    "Negative loadings on the factor in the ETF's name"
                ],
                "correctExplanation": "MTUM had alpha −0.2% (t = −0.11) and a MOM loading of 0.36; VLUE loads 0.34 on HML. No evidence of skill beyond factor exposure.",
                "incorrectExplanation": "For these two funds the alphas are not distinguishable from zero; their market betas are 1.034 (MTUM) and 0.983 (VLUE)."
            },
            "ro": {
                "title": "ETF-uri factoriale",
                "text": "După regresia MTUM și VLUE pe factorii FF5 + momentum, ce a arătat cursul?",
                "options": [
                    "Valori alfa mari și pozitive, de circa 5% pe an",
                    "Beta de piață aproape de zero pentru toate ETF-urile",
                    "Alfa aproape de zero; expunerile corespund denumirilor",
                    "Expuneri negative pe factorul din numele ETF-ului"
                ],
                "correctExplanation": "MTUM a avut alfa −0,2% (t = −0,11) și loading pe MOM 0,36; VLUE are loading 0,34 pe HML. Nicio dovadă de abilitate dincolo de expunerea factorială.",
                "incorrectExplanation": "Pentru aceste două fonduri, valorile alfa nu se disting de zero; beta lor de piață este 1,034 (MTUM) și 0,983 (VLUE)."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: a momentum signal",
                "text": "An AI assistant writes this momentum backtest: \"mom = P.pct_change(12); at each month-end t, rank the stocks on mom at t and record the return of the top minus bottom stocks over month t.\" The result is about 50% a year. What is wrong?",
                "options": [
                    "Momentum must be computed over 36 months, not over 12 months",
                    "Look-ahead bias: the signal at t already contains the return of month t",
                    "Monthly returns cannot be annualised by multiplying them by 12",
                    "A long–short portfolio always has a mean return of exactly zero"
                ],
                "correctExplanation": "Ranking on a 12-month return that ends at t and holding over month t uses the holding-period return to choose the stocks. Lag the signal, e.g. the 12–1 signal P.shift(2)/P.shift(13) − 1.",
                "incorrectExplanation": "The signal includes the very return it is meant to predict: use only prices known at the start of the holding month, e.g. months t−12 to t−2."
            },
            "ro": {
                "title": "Găsiți eroarea AI: un semnal de momentum",
                "text": "Un asistent AI scrie acest backtest de momentum: „mom = P.pct_change(12); la fiecare sfîrșit de lună t, ordonați acțiunile după mom la t și înregistrați randamentul primelor minus ultimelor acțiuni în luna t.” Rezultatul este circa 50% pe an. Ce este greșit?",
                "options": [
                    "Momentum-ul se calculează pe 36 de luni, nu pe 12 luni",
                    "Look-ahead bias: semnalul la t conține deja randamentul lunii t",
                    "Randamentele lunare nu pot fi anualizate prin înmulțirea cu 12",
                    "Un portofoliu long–short are mereu randamentul mediu exact zero"
                ],
                "correctExplanation": "Ordonarea după un randament pe 12 luni care se termină la t, urmată de deținerea în luna t, folosește chiar randamentul perioadei de deținere pentru alegerea acțiunilor. Decalați semnalul, de exemplu semnalul 12–1 P.shift(2)/P.shift(13) − 1.",
                "incorrectExplanation": "Semnalul conține chiar randamentul pe care ar trebui să-l prognozeze: folosiți doar prețuri cunoscute la începutul lunii de deținere, de exemplu lunile t−12 pînă la t−2."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the AI error: Blume-adjusted beta",
                "text": "An AI assistant writes: \"The Blume-adjusted beta is β_B = 0.67 + 0.33 β̂. For an estimated beta of 1.5, β_B = 1.165.\" What is wrong?",
                "options": [
                    "Blume's adjustment moves betas away from 1, not towards it",
                    "The Blume beta applies only to portfolios, never to single stocks",
                    "Adjusted betas must equal the OLS beta when β̂ > 1",
                    "The weights are swapped: β_B = 0.33 + 0.67 β̂, so β_B = 1.335"
                ],
                "correctExplanation": "Blume (1971): β_B = 0.33 + 0.67 β̂, which shrinks the estimate towards 1: 0.33 + 0.67 × 1.5 = 1.335. The swapped weights shrink far too much.",
                "incorrectExplanation": "In Blume's rule the estimated beta gets the weight 0.67 and the constant is 0.33: for β̂ = 1.5 the adjusted beta is 1.335."
            },
            "ro": {
                "title": "Găsiți eroarea AI: beta ajustat Blume",
                "text": "Un asistent AI scrie: „Beta ajustat Blume este β_B = 0,67 + 0,33 β̂. Pentru un beta estimat de 1,5, β_B = 1,165.” Ce este greșit?",
                "options": [
                    "Ajustarea Blume îndepărtează beta de 1, nu îl apropie",
                    "Beta Blume se aplică doar portofoliilor, niciodată acțiunilor individuale",
                    "Beta ajustat trebuie să fie egal cu beta OLS cînd β̂ > 1",
                    "Ponderile sînt inversate: β_B = 0,33 + 0,67 β̂, deci β_B = 1,335"
                ],
                "correctExplanation": "Blume (1971): β_B = 0,33 + 0,67 β̂, care apropie estimația de 1: 0,33 + 0,67 × 1,5 = 1,335. Ponderile inversate aplică un shrinkage mult prea puternic.",
                "incorrectExplanation": "În regula lui Blume beta estimat primește ponderea 0,67, iar constanta este 0,33: pentru β̂ = 1,5 beta ajustat este 1,335."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "What alpha measures",
                "text": "In the market model R_i,t − R_f,t = α_i + β_i (R_m,t − R_f,t) + ε_i,t, what is α_i?",
                "options": [
                    "The asset's sensitivity to movements of the market",
                    "The asset-specific shock in month t",
                    "The average excess return that beta does not explain",
                    "The market risk premium E[R_m] − R_f"
                ],
                "correctExplanation": "Taking means, α_i = E[R_i] − R_f − β_i (E[R_m] − R_f): the asset's vertical distance from the SML.",
                "incorrectExplanation": "Beta is the sensitivity and ε the asset-specific shock; alpha is the part of the average excess return left once beta is priced."
            },
            "ro": {
                "title": "Ce măsoară alfa",
                "text": "În modelul de piață R_i,t − R_f,t = α_i + β_i (R_m,t − R_f,t) + ε_i,t, ce este α_i?",
                "options": [
                    "Sensibilitatea activului la mișcările pieței",
                    "Șocul specific activului în luna t",
                    "Randamentul mediu în exces pe care beta nu îl explică",
                    "Prima de risc a pieței, E[R_m] − R_f"
                ],
                "correctExplanation": "În medie, α_i = E[R_i] − R_f − β_i (E[R_m] − R_f): distanța pe verticală a activului față de SML.",
                "incorrectExplanation": "Beta este sensibilitatea, iar ε este șocul specific activului; alfa este ce rămîne din randamentul mediu în exces după ce ținem cont de beta."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "What the CAPM says about alpha",
                "text": "If the CAPM holds, what must be true of the alphas of all assets in the market model?",
                "options": [
                    "They are all zero: beta explains the whole average excess return",
                    "They are all positive, equal to the market risk premium",
                    "They are equal to the risk-free rate",
                    "For an asset with beta one, alpha must be positive"
                ],
                "correctExplanation": "The CAPM, E[R_i] − R_f = β_i (E[R_m] − R_f), has no intercept; testing the CAPM is testing α_i = 0 for every asset, jointly with the GRS test.",
                "incorrectExplanation": "The CAPM equation has no intercept, so every asset lies on the SML and every alpha is zero."
            },
            "ro": {
                "title": "Ce spune CAPM despre alfa",
                "text": "Dacă CAPM este adevărat, ce trebuie să fie adevărat despre valorile alfa ale tuturor activelor în modelul de piață?",
                "options": [
                    "Sînt toate zero: beta explică tot randamentul mediu în exces",
                    "Sînt toate pozitive, egale cu prima de risc a pieței",
                    "Sînt egale cu rata fără risc",
                    "Pentru un activ cu beta unu, alfa este obligatoriu pozitiv"
                ],
                "correctExplanation": "Ecuația CAPM, E[R_i] − R_f = β_i (E[R_m] − R_f), nu are termen liber; a testa CAPM înseamnă a testa α_i = 0 pentru toate activele, simultan, cu testul GRS.",
                "incorrectExplanation": "Ecuația CAPM nu are termen liber, deci orice activ se află pe SML și orice alfa este zero."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Why everyone wants alpha",
                "text": "Over the same period, a fund earned on average 12% a year with beta 1.3, the market 10% and the risk-free rate 2% (arithmetic means). By how many percentage points did the fund beat its beta-adjusted benchmark?",
                "options": [
                    "+2 points: the fund beat the market",
                    "−0.4 points: its beta alone would have earned 12.4%",
                    "+10 points: it earned 10 points above the risk-free rate",
                    "0 points: alpha is always zero for a diversified fund"
                ],
                "correctExplanation": "α = 12 − 2 − 1.3 × (10 − 2) = −0.4 points. Market exposure can be obtained at low cost through an index fund (with leverage for β > 1), so an active fee has to be justified by alpha, not by beating the market.",
                "incorrectExplanation": "Beating the market is not alpha: subtract the return the fund's beta would have earned, 2 + 1.3 × 8 = 12.4%."
            },
            "ro": {
                "title": "De ce vrea toată lumea alfa",
                "text": "Pe aceeași perioadă, un fond a obținut în medie 12% pe an, cu beta 1,3, piața 10%, iar rata fără risc 2% (medii aritmetice). Cu cîte puncte procentuale a depășit fondul reperul ajustat la beta?",
                "options": [
                    "+2 puncte: fondul a depășit piața",
                    "−0,4 puncte: doar beta lui ar fi adus 12,4%",
                    "+10 puncte: a cîștigat 10 puncte peste rata fără risc",
                    "0 puncte: alfa este mereu zero pentru un fond diversificat"
                ],
                "correctExplanation": "α = 12 − 2 − 1,3 × (10 − 2) = −0,4 puncte. Expunerea la piață se poate obține cu costuri reduse printr-un fond indexat (cu levier pentru β > 1), deci un comision de administrare activă trebuie justificat prin alfa, nu prin depășirea pieței.",
                "incorrectExplanation": "Depășirea pieței nu înseamnă alfa: scădeți randamentul pe care l-ar fi adus beta fondului, 2 + 1,3 × 8 = 12,4%."
            }
        }
    ]
};

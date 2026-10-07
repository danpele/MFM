// ============================================================
// Quiz bank for chapter id 'continuous-time': Continuous-Time Models (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['continuous-time'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Girsanov: what changes",
                "text": "A diffusion dX = a dt + b dW is moved from the real-world measure P to an equivalent measure Q by Girsanov's theorem. What can change?",
                "options": [
                    "Only the drift; the diffusion coefficient, and hence the quadratic variation, is the same under P and Q",
                    "Only the volatility; the drift is fixed by the data",
                    "Both the drift and the volatility",
                    "Nothing, because equivalent measures give the same expectations"
                ],
                "correctExplanation": "Under Q, W becomes W~ + drift shift, so dX = (a - b theta) dt + b dW~: the drift moves, b and the quadratic variation do not. Under constant-volatility GBM, realised variance therefore measures the sigma that prices options; with stochastic volatility, P and Q can still weigh future variance paths differently.",
                "incorrectExplanation": "Quadratic variation is a path property, identical under equivalent measures, so the volatility cannot change; equivalent measures share null events, not expectations, so the drift does change."
            },
            "ro": {
                "title": "Girsanov: ce se schimbă",
                "text": "O difuzie dX = a dt + b dW este trecută de la măsura reală P la o măsură echivalentă Q prin teorema lui Girsanov. Ce se poate schimba?",
                "options": [
                    "Doar driftul; coeficientul de difuzie, deci și variația pătratică, este același sub P și Q",
                    "Doar volatilitatea; driftul este fixat de date",
                    "Atît driftul, cît și volatilitatea",
                    "Nimic, deoarece măsurile echivalente dau aceleași valori așteptate"
                ],
                "correctExplanation": "Sub Q, W devine W~ plus o deplasare de drift, deci dX = (a - b theta) dt + b dW~: driftul se schimbă, b și variația pătratică nu. Sub GBM cu volatilitate constantă, varianța realizată măsoară deci sigma care evaluează opțiunile; cu volatilitate stochastică, P și Q pot pondera totuși diferit traiectoriile viitoare ale varianței.",
                "incorrectExplanation": "Variația pătratică este o proprietate a traiectoriei, identică sub măsuri echivalente, deci volatilitatea nu se poate schimba; măsurile echivalente au aceleași evenimente de probabilitate zero, nu aceleași valori așteptate, deci driftul se schimbă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Donsker's theorem",
                "text": "What does Donsker's invariance principle add to the central limit theorem?",
                "options": [
                    "The random walk converges almost surely to a straight line",
                    "The steps must be Normal for the limit to exist",
                    "The limit depends on the distribution of the steps",
                    "The whole scaled path converges in distribution to Brownian motion, not only its value at one time"
                ],
                "correctExplanation": "Donsker's theorem is a functional central limit theorem: the scaled random walk converges as a random function, whatever the step distribution (mean 0, variance 1).",
                "incorrectExplanation": "The central limit theorem concerns a single time point; Donsker's result concerns the entire path and does not depend on the step distribution."
            },
            "ro": {
                "title": "Teorema lui Donsker",
                "text": "Ce adaugă principiul de invarianță al lui Donsker față de teorema limită centrală?",
                "options": [
                    "Mersul aleator converge aproape sigur la o dreaptă",
                    "Pașii trebuie să fie Normali pentru ca limita să existe",
                    "Limita depinde de distribuția pașilor",
                    "Întreaga traiectorie scalată converge în distribuție la mișcarea browniană, nu doar valoarea ei la un moment"
                ],
                "correctExplanation": "Teorema lui Donsker este o teoremă limită centrală funcțională: mersul aleator scalat converge ca funcție aleatoare, oricare ar fi distribuția pașilor (medie 0, dispersie 1).",
                "incorrectExplanation": "Teorema limită centrală privește un singur moment; rezultatul lui Donsker privește întreaga traiectorie și nu depinde de distribuția pașilor."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Infill versus long span",
                "text": "An OU process is observed at ever higher frequency over a fixed 5-year window: the sampling interval shrinks to zero, so n grows without bound while T = 5 stays fixed. Which parameter is estimated consistently?",
                "options": [
                    "The speed of mean reversion kappa",
                    "The long-run mean theta",
                    "The volatility sigma",
                    "All three, because n tends to infinity"
                ],
                "correctExplanation": "Infill asymptotics: the sum of squared increments converges to the integrated variance, so sigma is identified without error; kappa and theta are drift parameters whose information grows only with T.",
                "incorrectExplanation": "Drift parameters (kappa, theta) are identified by the calendar span T, not by the number of observations: Var(kappa-hat) is about (exp(2 kappa Delta) - 1) / (T Delta), which tends to 2 kappa / T, not to zero, as the step Delta shrinks with T fixed."
            },
            "ro": {
                "title": "Infill față de orizont lung",
                "text": "Un proces OU este observat din ce în ce mai des pe o fereastră fixă de 5 ani: intervalul de eșantionare tinde la zero, deci n crește nelimitat, iar T = 5 rămîne fix. Ce parametru se estimează consistent?",
                "options": [
                    "Viteza de revenire la medie kappa",
                    "Media pe termen lung theta",
                    "Volatilitatea sigma",
                    "Toți trei, deoarece n tinde la infinit"
                ],
                "correctExplanation": "Asimptotica infill: suma pătratelor creșterilor converge la varianța integrată, deci sigma este identificat fără eroare; kappa și theta sînt parametri de drift, a căror informație crește doar cu T.",
                "incorrectExplanation": "Parametrii de drift (kappa, theta) sînt identificați de durata calendaristică T, nu de numărul de observații: Var(kappa estimat) este circa (exp(2 kappa Delta) - 1) / (T Delta), care tinde la 2 kappa / T, nu la zero, cînd pasul Delta scade, iar T rămîne fix."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "The VIX in the Heston model",
                "text": "In the Heston model, what is (VIX_t / 100)^2, the 30-day risk-neutral expected variance?",
                "options": [
                    "Equal to the instantaneous variance v_t",
                    "An affine function a + b v_t of v_t, with risk-neutral parameters and b < 1",
                    "Equal to the long-run variance theta",
                    "Independent of v_t"
                ],
                "correctExplanation": "Integrating E^Q[v_s | v_t] = theta^Q + (v_t - theta^Q) exp(-kappa^Q (s - t)) over 30 days gives a + b v_t with b = (1 - exp(-kappa^Q tau)) / (kappa^Q tau) < 1: a CIR regression on VIX^2 attenuates the volatility of volatility, by the factor b at v_t = theta^Q (elsewhere the attenuation depends on the state).",
                "incorrectExplanation": "The VIX averages expected variance over the next 30 days under Q; mean reversion pulls this average towards theta^Q, so it depends on v_t, but with a slope below one."
            },
            "ro": {
                "title": "VIX în modelul Heston",
                "text": "În modelul Heston, ce este (VIX_t / 100)^2, varianța așteptată neutră la risc pe 30 de zile?",
                "options": [
                    "Egal cu varianța instantanee v_t",
                    "O funcție afină a + b v_t de v_t, cu parametri neutri la risc și b < 1",
                    "Egal cu varianța pe termen lung theta",
                    "Independent de v_t"
                ],
                "correctExplanation": "Integrînd E^Q[v_s | v_t] = theta^Q + (v_t - theta^Q) exp(-kappa^Q (s - t)) pe 30 de zile obținem a + b v_t, cu b = (1 - exp(-kappa^Q tau)) / (kappa^Q tau) < 1: o regresie CIR pe VIX^2 atenuează volatilitatea volatilității, cu factorul b la v_t = theta^Q (în rest, atenuarea depinde de stare).",
                "incorrectExplanation": "VIX mediază varianța așteptată în următoarele 30 de zile sub Q; revenirea la medie trage această medie spre theta^Q, deci depinde de v_t, dar cu o pantă sub unu."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The Itô integral",
                "text": "Why does finance use the Itô integral, evaluated at the left end point of each interval?",
                "options": [
                    "It is the only integral with a closed form",
                    "The mid-point rule does not converge",
                    "The position must be chosen before the next price move is known, so the integrand cannot look into the future",
                    "It makes Brownian motion differentiable"
                ],
                "correctExplanation": "Evaluating at the left end point keeps the integrand adapted: a trading strategy decided with today's information.",
                "incorrectExplanation": "Mid-point (Stratonovich) sums converge too, but they use information about the next increment, which a trader does not have."
            },
            "ro": {
                "title": "Integrala Itô",
                "text": "De ce finanțele folosesc integrala Itô, evaluată în capătul stîng al fiecărui interval?",
                "options": [
                    "Este singura integrală cu o formă închisă",
                    "Regula punctului de mijloc nu converge",
                    "Poziția trebuie aleasă înainte de a cunoaște următoarea mișcare a prețului, deci integrandul nu poate folosi informații din viitor",
                    "Face mișcarea browniană derivabilă"
                ],
                "correctExplanation": "Evaluarea în capătul stîng păstrează integrandul adaptat: o strategie de tranzacționare decisă cu informația de azi.",
                "incorrectExplanation": "Sumele la punctul de mijloc (Stratonovich) converg și ele, dar folosesc informație despre creșterea următoare, pe care un investitor nu o are."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Integral of W dW",
                "text": "What is the Itô integral of W with respect to W over [0, T]?",
                "options": [
                    "(W_T^2 - T)/2",
                    "W_T^2/2",
                    "W_T - T",
                    "0"
                ],
                "correctExplanation": "Summing the identity for each increment gives W_T^2/2 minus half the quadratic variation, T/2.",
                "incorrectExplanation": "Ordinary calculus would give W_T^2/2; the extra -T/2 comes from the quadratic variation, and the result is random, not 0."
            },
            "ro": {
                "title": "Integrala lui W dW",
                "text": "Care este integrala Itô a lui W în raport cu W pe [0, T]?",
                "options": [
                    "(W_T^2 - T)/2",
                    "W_T^2/2",
                    "W_T - T",
                    "0"
                ],
                "correctExplanation": "Sumînd identitatea pentru fiecare creștere se obține W_T^2/2 minus jumătate din variația pătratică, T/2.",
                "incorrectExplanation": "Calculul clasic ar da W_T^2/2; termenul suplimentar -T/2 provine din variația pătratică, iar rezultatul este aleator, nu 0."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Itô's lemma",
                "text": "For dX = a dt + b dW and a smooth function f(x), which term distinguishes Itô's lemma from the ordinary chain rule?",
                "options": [
                    "a f'(X) dt",
                    "b f'(X) dW",
                    "f(X) dt",
                    "(1/2) b^2 f''(X) dt"
                ],
                "correctExplanation": "Because (dW)^2 = dt, the second-order Taylor term (1/2) b^2 f'' dt survives.",
                "incorrectExplanation": "The terms a f' dt and b f' dW also appear in the ordinary chain rule; the novelty is the second-order term."
            },
            "ro": {
                "title": "Lema lui Itô",
                "text": "Pentru dX = a dt + b dW și o funcție netedă f(x), ce termen deosebește lema lui Itô de regula obișnuită de derivare a funcțiilor compuse?",
                "options": [
                    "a f'(X) dt",
                    "b f'(X) dW",
                    "f(X) dt",
                    "(1/2) b^2 f''(X) dt"
                ],
                "correctExplanation": "Deoarece (dW)^2 = dt, termenul Taylor de ordinul doi (1/2) b^2 f'' dt nu dispare.",
                "incorrectExplanation": "Termenii a f' dt și b f' dW apar și în regula obișnuită; diferența constă în termenul de ordinul doi."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Log price under GBM",
                "text": "If dS = mu S dt + sigma S dW, what is d ln S?",
                "options": [
                    "mu dt + sigma dW",
                    "(mu - sigma^2/2) dt + sigma dW",
                    "(mu + sigma^2/2) dt + sigma dW",
                    "mu dt"
                ],
                "correctExplanation": "Itô's lemma with f = ln x gives the drift mu - sigma^2/2 for the log price.",
                "incorrectExplanation": "The second-order term subtracts sigma^2/2 from the drift: volatility lowers the growth of the log price."
            },
            "ro": {
                "title": "Logaritmul prețului sub GBM",
                "text": "Dacă dS = mu S dt + sigma S dW, cît este d ln S?",
                "options": [
                    "mu dt + sigma dW",
                    "(mu - sigma^2/2) dt + sigma dW",
                    "(mu + sigma^2/2) dt + sigma dW",
                    "mu dt"
                ],
                "correctExplanation": "Lema lui Itô cu f = ln x dă driftul mu - sigma^2/2 pentru logaritmul prețului.",
                "incorrectExplanation": "Termenul de ordinul doi scade sigma^2/2 din drift: volatilitatea reduce creșterea logaritmului prețului."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Feynman-Kac",
                "text": "Let u(t, x) = E^Q[exp(-r (T - t)) g(X_T) | X_t = x] with dX = a(X) dt + b(X) dW~ under Q and a constant rate r. Which equation does u solve?",
                "options": [
                    "u_t + a u_x + b^2 u_xx - r u = 0",
                    "u_t + a u_x + (1/2) b^2 u_xx + r u = 0",
                    "u_t + (1/2) u_xx = 0, whatever the drift",
                    "u_t + a u_x + (1/2) b^2 u_xx - r u = 0, with u(T, x) = g(x)"
                ],
                "correctExplanation": "Discounted u(t, X_t) is a Q-martingale; Itô's lemma gives the drift u_t + a u_x + (1/2) b^2 u_xx - r u, which must vanish. The Vasicek bond and the Black-Scholes equation are special cases.",
                "incorrectExplanation": "The second-order Itô term carries the factor one half, discounting enters with a minus sign, and the drift a of X appears in the first-order term."
            },
            "ro": {
                "title": "Feynman-Kac",
                "text": "Fie u(t, x) = E^Q[exp(-r (T - t)) g(X_T) | X_t = x], cu dX = a(X) dt + b(X) dW~ sub Q și o rată constantă r. Ce ecuație satisface u?",
                "options": [
                    "u_t + a u_x + b^2 u_xx - r u = 0",
                    "u_t + a u_x + (1/2) b^2 u_xx + r u = 0",
                    "u_t + (1/2) u_xx = 0, oricare ar fi driftul",
                    "u_t + a u_x + (1/2) b^2 u_xx - r u = 0, cu u(T, x) = g(x)"
                ],
                "correctExplanation": "Valoarea actualizată u(t, X_t) este o Q-martingală; lema lui Itô dă driftul u_t + a u_x + (1/2) b^2 u_xx - r u, care trebuie să fie zero. Obligațiunea Vasicek și ecuația Black-Scholes sînt cazuri particulare.",
                "incorrectExplanation": "Termenul Itô de ordinul doi are factorul o jumătate, actualizarea intră cu semnul minus, iar driftul a al lui X apare în termenul de ordinul întîi."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Drift precision",
                "text": "How can the precision of the estimated log drift m = mu - sigma^2/2 of GBM be improved?",
                "options": [
                    "By sampling daily instead of monthly",
                    "By using intraday data",
                    "Only by a longer calendar span of data",
                    "By using log instead of simple returns"
                ],
                "correctExplanation": "The standard error of the estimated log drift is sigma/sqrt(T): it depends on the calendar length only, since the sum of log returns uses only the first and last prices.",
                "incorrectExplanation": "Sampling more often improves the volatility estimate, not the drift estimate."
            },
            "ro": {
                "title": "Precizia driftului",
                "text": "Cum poate fi îmbunătățită precizia driftului logaritmic estimat m = mu - sigma^2/2 al GBM?",
                "options": [
                    "Prin eșantionare zilnică în loc de lunară",
                    "Prin folosirea datelor intrazilnice",
                    "Doar printr-o durată calendaristică mai lungă a datelor",
                    "Prin randamente logaritmice în loc de randamente simple"
                ],
                "correctExplanation": "Eroarea standard a driftului logaritmic estimat este sigma/sqrt(T): depinde doar de durata calendaristică, deoarece suma randamentelor logaritmice folosește doar primul și ultimul preț.",
                "incorrectExplanation": "Eșantionarea mai deasă îmbunătățește estimarea volatilității, nu a driftului."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Euler-Maruyama",
                "text": "What is the strong order of convergence of the Euler-Maruyama scheme?",
                "options": [
                    "1",
                    "1/2",
                    "2",
                    "0"
                ],
                "correctExplanation": "The mean absolute path error of Euler-Maruyama falls like the square root of the step size; the lecture estimates 0.52.",
                "incorrectExplanation": "Order 1 is the strong order of Milstein and the weak order of Euler-Maruyama."
            },
            "ro": {
                "title": "Euler-Maruyama",
                "text": "Care este ordinul tare de convergență al schemei Euler-Maruyama?",
                "options": [
                    "1",
                    "1/2",
                    "2",
                    "0"
                ],
                "correctExplanation": "Eroarea absolută medie pe traiectorie a schemei Euler-Maruyama scade cu rădăcina pătrată a pasului; cursul estimează 0,52.",
                "incorrectExplanation": "Ordinul 1 este ordinul tare al schemei Milstein și ordinul slab al schemei Euler-Maruyama."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Milstein",
                "text": "What does the Milstein scheme add to Euler-Maruyama?",
                "options": [
                    "A second Brownian motion",
                    "An implicit drift step",
                    "A correction to the mean of the increments",
                    "The term (1/2) b b' [(dW)^2 - dt], raising the strong order to 1"
                ],
                "correctExplanation": "The next Itô-Taylor term (1/2) b b' [(dW)^2 - dt] has mean zero but corrects each path, giving strong order 1.",
                "incorrectExplanation": "Milstein keeps one Brownian motion and an explicit drift; its correction has mean zero, so it does not change the mean of the increments."
            },
            "ro": {
                "title": "Milstein",
                "text": "Ce adaugă schema Milstein față de Euler-Maruyama?",
                "options": [
                    "O a doua mișcare browniană",
                    "Un pas implicit pentru drift",
                    "O corecție a mediei creșterilor",
                    "Termenul (1/2) b b' [(dW)^2 - dt], care ridică ordinul tare la 1"
                ],
                "correctExplanation": "Următorul termen Itô-Taylor (1/2) b b' [(dW)^2 - dt] are media zero, dar corectează fiecare traiectorie, dînd ordinul tare 1.",
                "incorrectExplanation": "Milstein păstrează o singură mișcare browniană și un drift explicit; corecția are media zero, deci nu schimbă media creșterilor."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "The CIR transition law",
                "text": "For the CIR process dr = kappa (theta - r) dt + sigma sqrt(r) dW, what is the exact law of r_{t + Delta} given r_t?",
                "options": [
                    "A scaled noncentral chi-squared with 4 kappa theta / sigma^2 degrees of freedom",
                    "Normal, as for Vasicek",
                    "Lognormal",
                    "A Poisson mixture of Normal distributions"
                ],
                "correctExplanation": "2c r_{t + Delta} given r_t is noncentral chi-squared with 4 kappa theta / sigma^2 degrees of freedom and noncentrality 2c r_t exp(-kappa Delta), c = 2 kappa / (sigma^2 (1 - exp(-kappa Delta))): the exact likelihood is available, and Feller holds when the degrees of freedom are at least 2.",
                "incorrectExplanation": "The square-root diffusion keeps the rate non-negative and skews its law to the right; the Normal distribution belongs to Vasicek and the Poisson mixture belongs to the Merton jump model."
            },
            "ro": {
                "title": "Legea de tranziție CIR",
                "text": "Pentru procesul CIR dr = kappa (theta - r) dt + sigma sqrt(r) dW, care este legea exactă a lui r_{t + Delta} condiționat de r_t?",
                "options": [
                    "Un chi-pătrat necentral scalat, cu 4 kappa theta / sigma^2 grade de libertate",
                    "Distribuția Normală, ca în modelul Vasicek",
                    "Lognormală",
                    "O mixtură Poisson de distribuții Normale"
                ],
                "correctExplanation": "2c r_{t + Delta} condiționat de r_t este chi-pătrat necentral cu 4 kappa theta / sigma^2 grade de libertate și parametrul de necentralitate 2c r_t exp(-kappa Delta), c = 2 kappa / (sigma^2 (1 - exp(-kappa Delta))): verosimilitatea exactă este disponibilă, iar condiția Feller este îndeplinită cînd gradele de libertate sînt cel puțin 2.",
                "incorrectExplanation": "Volatilitatea sigma sqrt(r) scade spre zero cînd rata se apropie de zero, deci rata nu devine negativă, iar legea este asimetrică la dreapta; legea Normală este cea Vasicek, iar mixtura Poisson aparține modelului Merton cu salturi."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "LR test for jumps on the boundary",
                "text": "You test Merton (lambda > 0) against GBM (lambda = 0) with a likelihood-ratio statistic. What about the chi-squared(3) critical value?",
                "options": [
                    "It is valid, because Merton adds three parameters",
                    "It is valid with chi-squared(1), because only lambda is tested",
                    "It is invalid: lambda = 0 lies on the boundary and mu_J, sigma_J are unidentified under the null; use a parametric bootstrap",
                    "It is valid if the sample is longer than ten years"
                ],
                "correctExplanation": "Wilks' theorem needs an interior null and identified parameters; both fail here, so the null distribution is obtained by simulating GBM samples and refitting both models (Seminar B6).",
                "incorrectExplanation": "Neither counting parameters nor a longer sample repairs a boundary null with unidentified nuisance parameters: the chi-squared reference distribution does not apply."
            },
            "ro": {
                "title": "Testul LR pentru salturi pe frontieră",
                "text": "Testați Merton (lambda > 0) față de GBM (lambda = 0) cu statistica raportului de verosimilitate. Ce se întîmplă cu valoarea critică chi-pătrat(3)?",
                "options": [
                    "Este validă, deoarece Merton adaugă trei parametri",
                    "Este validă cu chi-pătrat(1), deoarece se testează doar lambda",
                    "Nu este validă: lambda = 0 se află pe frontieră, iar mu_J, sigma_J nu sînt identificați sub ipoteza nulă; folosiți un bootstrap parametric",
                    "Este validă dacă eșantionul depășește zece ani"
                ],
                "correctExplanation": "Teorema lui Wilks necesită o ipoteză nulă interioară și parametri identificați; ambele condiții lipsesc aici, deci distribuția sub ipoteza nulă se obține simulînd eșantioane GBM și reestimînd ambele modele (Seminarul B6).",
                "incorrectExplanation": "Nici numărarea parametrilor, nici un eșantion mai lung nu repară o ipoteză nulă pe frontieră cu parametri de perturbare neidentificați: distribuția chi-pătrat de referință nu se aplică."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Multivariate Itô formula",
                "text": "Under Heston, dS = mu S dt + sqrt(v) S dW1 and dv = kappa (theta - v) dt + xi sqrt(v) dW2 with Corr(dW1, dW2) = rho. Which cross term appears in d(S_t v_t)?",
                "options": [
                    "None, the product rule has no extra term",
                    "rho xi v_t S_t dt",
                    "rho dt",
                    "xi S_t dt"
                ],
                "correctExplanation": "d(Sv) = S dv + v dS + d[S, v], and d[S, v] = (sqrt(v) S)(xi sqrt(v)) rho dt = rho xi v S dt: the correlation enters the drift of the product.",
                "incorrectExplanation": "The quadratic covariation of the two diffusion terms is the product of their coefficients times rho dt; it does not vanish when the Brownian motions are correlated."
            },
            "ro": {
                "title": "Formula Itô multivariată",
                "text": "Sub Heston, dS = mu S dt + sqrt(v) S dW1 și dv = kappa (theta - v) dt + xi sqrt(v) dW2, cu Corr(dW1, dW2) = rho. Ce termen încrucișat apare în d(S_t v_t)?",
                "options": [
                    "Niciunul, regula produsului nu are termen suplimentar",
                    "rho xi v_t S_t dt",
                    "rho dt",
                    "xi S_t dt"
                ],
                "correctExplanation": "d(Sv) = S dv + v dS + d[S, v], iar d[S, v] = (sqrt(v) S)(xi sqrt(v)) rho dt = rho xi v S dt: corelația intră în driftul produsului.",
                "incorrectExplanation": "Covariația pătratică a celor doi termeni de difuzie este produsul coeficienților lor înmulțit cu rho dt; nu dispare cînd mișcările browniene sînt corelate."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Bias of kappa",
                "text": "In finite samples, the maximum likelihood estimate of the mean-reversion speed kappa is",
                "options": [
                    "Biased upwards, by roughly 4/T with T in years",
                    "Unbiased",
                    "Biased downwards",
                    "Biased only with daily data"
                ],
                "correctExplanation": "The lecture simulation gives a bias of 0.063 for the 72-year Treasury bill sample, close to 4/T = 0.055: mean reversion looks faster than it is.",
                "incorrectExplanation": "The bias depends on the calendar span, not on the sampling frequency, and it goes upwards."
            },
            "ro": {
                "title": "Deplasarea lui kappa",
                "text": "În eșantioane finite, estimatorul de verosimilitate maximă al vitezei de revenire la medie kappa este",
                "options": [
                    "Deplasat în sus, cu aproximativ 4/T, T în ani",
                    "Nedeplasat",
                    "Deplasat în jos",
                    "Deplasat doar cu date zilnice"
                ],
                "correctExplanation": "Simularea din curs dă o deplasare de 0,063 pentru cei 72 de ani de randamente ale titlurilor de stat, aproape de 4/T = 0,055: revenirea la medie pare mai rapidă decît este.",
                "incorrectExplanation": "Deplasarea depinde de durata calendaristică, nu de frecvența eșantionării, și este în sus."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Vasicek and CIR",
                "text": "What is the main difference between the Vasicek and the Cox-Ingersoll-Ross short-rate models?",
                "options": [
                    "Vasicek has no mean reversion",
                    "CIR scales the volatility by sqrt(r), which keeps the rate positive under the Feller condition",
                    "CIR has jumps",
                    "Vasicek has a closed form for bond prices and CIR does not"
                ],
                "correctExplanation": "In Vasicek the rate is Normal and can become negative; the sqrt(r) diffusion of CIR shrinks near zero.",
                "incorrectExplanation": "Both models mean-revert, have no jumps and give bond prices in closed form."
            },
            "ro": {
                "title": "Vasicek și CIR",
                "text": "Care este principala diferență dintre modelele Vasicek și Cox-Ingersoll-Ross pentru rata pe termen scurt?",
                "options": [
                    "Vasicek nu are revenire la medie",
                    "CIR scalează volatilitatea cu sqrt(r), ceea ce păstrează rata pozitivă sub condiția Feller",
                    "CIR are salturi",
                    "Vasicek are formă închisă pentru prețurile obligațiunilor, iar CIR nu"
                ],
                "correctExplanation": "În modelul Vasicek, rata urmează distribuția Normală și poate deveni negativă; difuzia sqrt(r) din CIR scade lîngă zero.",
                "incorrectExplanation": "Ambele modele revin la medie, nu au salturi și dau prețurile obligațiunilor în formă închisă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Merton fitted by MLE",
                "text": "Fitted by maximum likelihood to S&P 500 daily returns, the Merton model gives about 100 small jumps per year. How should this be read?",
                "options": [
                    "The i.i.d. model uses jumps to imitate changing volatility",
                    "The S&P 500 jumps every two or three days",
                    "The estimate is a numerical error",
                    "Jumps explain the volatility clustering"
                ],
                "correctExplanation": "An i.i.d. model cannot separate a jump from a volatile period, so it uses frequent small jumps to fatten the tails; the Lee-Mykland test flags under one candidate jump per year.",
                "incorrectExplanation": "Merton returns are still independent over time, so they cannot produce clustering; the jumps detected in daily data are rare."
            },
            "ro": {
                "title": "Merton estimat prin MLE",
                "text": "Estimat prin verosimilitate maximă pe randamentele zilnice ale S&P 500, modelul Merton dă circa 100 de salturi mici pe an. Cum trebuie interpretat acest rezultat?",
                "options": [
                    "Modelul i.i.d. folosește salturile pentru a imita volatilitatea variabilă",
                    "S&P 500 are un salt la fiecare două-trei zile",
                    "Estimarea este o eroare numerică",
                    "Salturile explică volatility clustering"
                ],
                "correctExplanation": "Un model i.i.d. nu poate separa un salt de o perioadă volatilă, așa că folosește salturi mici și frecvente pentru a îngroșa cozile; testul Lee-Mykland marchează mai puțin de un salt candidat pe an.",
                "incorrectExplanation": "Randamentele Merton rămîn independente în timp, deci nu pot produce volatility clustering; salturile detectate în datele zilnice sînt rare."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Lee-Mykland test",
                "text": "Why were none of the ten largest absolute S&P 500 returns flagged as jumps by the Lee-Mykland test?",
                "options": [
                    "The test only detects positive jumps",
                    "The test uses weekly data",
                    "Large returns are removed before testing",
                    "They occurred in turbulent periods, so they were not large relative to local volatility"
                ],
                "correctExplanation": "The statistic divides each return by a local bipower volatility; in 2008 and 2020 volatility was already high.",
                "incorrectExplanation": "The test is symmetric, uses the daily returns themselves and removes nothing; it measures size relative to local volatility."
            },
            "ro": {
                "title": "Testul Lee-Mykland",
                "text": "De ce niciunul dintre cele mai mari zece randamente S&P 500 în valoare absolută nu a fost marcat ca salt de testul Lee-Mykland?",
                "options": [
                    "Testul detectează doar salturile pozitive",
                    "Testul folosește date săptămînale",
                    "Randamentele mari sînt eliminate înainte de test",
                    "Au apărut în perioade de volatilitate ridicată, deci nu erau mari în raport cu volatilitatea locală"
                ],
                "correctExplanation": "Statistica împarte fiecare randament la o volatilitate locală bipower; în 2008 și 2020 volatilitatea era deja ridicată.",
                "incorrectExplanation": "Testul este simetric, folosește chiar randamentele zilnice și nu elimină nimic; măsoară mărimea în raport cu volatilitatea locală."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Jumps and horizon",
                "text": "How does the excess kurtosis of Merton returns change with the horizon Delta t?",
                "options": [
                    "It grows like Delta t",
                    "It stays constant",
                    "It falls like 1/Delta t",
                    "It falls like 1/sqrt(Delta t)"
                ],
                "correctExplanation": "The fourth cumulant grows like Delta t while the variance squared grows like Delta t^2, so excess kurtosis falls like 1/Delta t: jumps matter most at short horizons.",
                "incorrectExplanation": "Excess kurtosis is the fourth cumulant divided by the squared variance, and the two scale differently with Delta t."
            },
            "ro": {
                "title": "Salturile și orizontul",
                "text": "Cum se modifică excesul de kurtosis al randamentelor Merton cu orizontul Delta t?",
                "options": [
                    "Crește ca Delta t",
                    "Rămîne constant",
                    "Scade ca 1/Delta t",
                    "Scade ca 1/sqrt(Delta t)"
                ],
                "correctExplanation": "Cumulantul de ordinul patru crește ca Delta t, iar pătratul dispersiei ca Delta t^2, deci excesul de kurtosis scade ca 1/Delta t: salturile au cel mai mare efect pe orizonturi scurte.",
                "incorrectExplanation": "Excesul de kurtosis este cumulantul de ordinul patru împărțit la pătratul dispersiei, iar cele două se scalează diferit cu Delta t."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Leverage and the skew",
                "text": "In the Heston model with rho = -0.69, how do three-month implied volatilities vary with the strike?",
                "options": [
                    "They are flat",
                    "They rise with the strike",
                    "They fall with the strike: a downward skew, as for equity-index options",
                    "They form a symmetric smile around the money"
                ],
                "correctExplanation": "Negative correlation between returns and variance fattens the left tail, so low strikes get higher implied volatilities.",
                "incorrectExplanation": "A flat line is the Black-Scholes case; a symmetric smile appears with rho = 0 and a rising curve with rho > 0."
            },
            "ro": {
                "title": "Efectul de levier și skew-ul",
                "text": "În modelul Heston cu rho = -0,69, cum variază volatilitățile implicite pe trei luni cu prețul de exercitare?",
                "options": [
                    "Sînt constante",
                    "Cresc odată cu prețul de exercitare",
                    "Scad odată cu prețul de exercitare: un skew descendent, ca la opțiunile pe indici bursieri",
                    "Formează un smile simetric în jurul nivelului ATM"
                ],
                "correctExplanation": "Corelația negativă dintre randamente și varianță îngroașă coada stîngă, deci prețurile de exercitare mici au volatilități implicite mai mari.",
                "incorrectExplanation": "O linie orizontală este cazul Black-Scholes; un smile simetric apare cu rho = 0, iar o curbă crescătoare cu rho > 0."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "GARCH and its diffusion limit",
                "text": "GARCH(1,1) converges weakly to a stochastic-volatility diffusion as the time step shrinks (Nelson, 1990). Does it follow that statistical inference is the same in both models?",
                "options": [
                    "No: the two are not asymptotically equivalent experiments, because GARCH has one noise source and the diffusion has two",
                    "Yes, weak convergence implies equivalent inference",
                    "Yes, whenever alpha + beta < 1",
                    "Only for the drift parameters"
                ],
                "correctExplanation": "Wang (2002) shows that GARCH and its diffusion limit are asymptotically non-equivalent: likelihood-based inference can differ even as the step tends to zero.",
                "incorrectExplanation": "Weak convergence of the processes concerns their distributions, not the information in the observed data; stationarity conditions do not change this."
            },
            "ro": {
                "title": "GARCH și limita sa de difuzie",
                "text": "GARCH(1,1) converge slab la o difuzie cu volatilitate stochastică cînd pasul de timp scade (Nelson, 1990). Rezultă că inferența statistică este aceeași în cele două modele?",
                "options": [
                    "Nu: cele două nu sînt experimente asimptotic echivalente, deoarece GARCH are o singură sursă de zgomot, iar difuzia are două",
                    "Da, convergența slabă implică inferență echivalentă",
                    "Da, oricînd alpha + beta < 1",
                    "Doar pentru parametrii de drift"
                ],
                "correctExplanation": "Wang (2002) arată că GARCH și limita sa de difuzie nu sînt asimptotic echivalente: inferența bazată pe verosimilitate poate diferi chiar cînd pasul tinde la zero.",
                "incorrectExplanation": "Convergența slabă a proceselor privește distribuțiile lor, nu informația din datele observate; condițiile de staționaritate nu schimbă acest lucru."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "VIX and realised volatility",
                "text": "Heston parameters estimated from the VIX give a long-run volatility of 20.9%, while the realised S&P 500 volatility is 18.0%. Why?",
                "options": [
                    "The VIX is a risk-neutral expectation that contains a variance risk premium",
                    "The VIX is computed from Bitcoin options",
                    "Realised volatility is biased upwards",
                    "The CIR regression overestimates kappa"
                ],
                "correctExplanation": "Option buyers pay for protection against volatility, so implied variance exceeds realised variance on average.",
                "incorrectExplanation": "The VIX comes from S&P 500 options; the gap reflects a premium, not an estimation error."
            },
            "ro": {
                "title": "VIX și volatilitatea realizată",
                "text": "Parametrii Heston estimați din VIX dau o volatilitate pe termen lung de 20,9%, iar volatilitatea realizată a S&P 500 este 18,0%. De ce?",
                "options": [
                    "VIX este o așteptare neutră la risc care conține o primă de risc pentru varianță",
                    "VIX se calculează din opțiuni pe Bitcoin",
                    "Volatilitatea realizată este deplasată în sus",
                    "Regresia CIR supraestimează kappa"
                ],
                "correctExplanation": "Cumpărătorii de opțiuni plătesc pentru protecția împotriva volatilității, deci varianța implicită depășește în medie varianța realizată.",
                "incorrectExplanation": "VIX provine din opțiuni pe S&P 500; decalajul reflectă o primă, nu o eroare de estimare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Which model?",
                "text": "Simulated against the S&P 500, which statement matches the lecture results?",
                "options": [
                    "GBM reproduces all stylised facts",
                    "Merton reproduces the Hill statistic, Heston the volatility clustering, and neither the excess kurtosis",
                    "Merton reproduces volatility clustering",
                    "Heston reproduces the excess kurtosis of 10.9"
                ],
                "correctExplanation": "Merton's Hill statistic (2.70) is near the data (2.56) but its ACF of |r| is zero; Heston's ACF matches, but both give an excess kurtosis near 3.5 against 10.9.",
                "incorrectExplanation": "GBM fails on every statistic, i.i.d. jumps cannot create clustering, and no fitted model reaches the kurtosis: the evidence favours combining jumps and stochastic volatility."
            },
            "ro": {
                "title": "Comparația modelelor",
                "text": "Simulate și comparate cu S&P 500, ce afirmație corespunde rezultatelor din curs?",
                "options": [
                    "GBM reproduce toate faptele stilizate",
                    "Merton reproduce statistica Hill, Heston volatility clustering și niciunul excesul de kurtosis",
                    "Merton reproduce volatility clustering",
                    "Heston reproduce excesul de kurtosis de 10,9"
                ],
                "correctExplanation": "Statistica Hill Merton (2,70) este aproape de date (2,56), dar ACF a lui |r| este zero; ACF Heston este apropiată de cea din date, dar ambele dau un exces de kurtosis de circa 3,5 față de 10,9.",
                "incorrectExplanation": "GBM nu reproduce niciuna dintre statistici, salturile i.i.d. nu pot crea volatility clustering și niciun model estimat nu atinge excesul de kurtosis din date: rezultatele susțin combinarea salturilor cu volatilitatea stochastică."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the AI error: the log of a GBM",
                "text": "An AI assistant writes: \"For dS = mu S dt + sigma S dW, the chain rule gives d ln S = dS/S = mu dt + sigma dW, so the median of S_T is S_0 exp(mu T).\" What is wrong?",
                "options": [
                    "The GBM equation should have sigma dW without the factor S",
                    "The median of S_T equals its mean, S_0 exp(mu T / 2)",
                    "Ordinary calculus was used instead of Itô: d ln S = (mu - sigma^2/2) dt + sigma dW, so the median is S_0 exp((mu - sigma^2/2) T)",
                    "ln S_T has a Student-t distribution, so it has no median"
                ],
                "correctExplanation": "For f(S) = ln S, Itô's lemma adds (1/2) f''(S) sigma^2 S^2 = -sigma^2/2 because (dW)^2 = dt. The mean is still S_0 exp(mu T); the median is lower, S_0 exp((mu - sigma^2/2) T).",
                "incorrectExplanation": "The GBM equation is right; the error is applying the ordinary chain rule to a diffusion, which drops the -sigma^2/2 term."
            },
            "ro": {
                "title": "Găsiți eroarea AI: logaritmul unui GBM",
                "text": "Un asistent AI scrie: „Pentru dS = mu S dt + sigma S dW, regula de derivare a funcțiilor compuse dă d ln S = dS/S = mu dt + sigma dW, deci mediana lui S_T este S_0 exp(mu T).” Ce este greșit?",
                "options": [
                    "Ecuația GBM ar trebui să aibă sigma dW fără factorul S",
                    "Mediana lui S_T este egală cu media, S_0 exp(mu T / 2)",
                    "S-a folosit calculul diferențial clasic în loc de calculul Itô: d ln S = (mu - sigma^2/2) dt + sigma dW, deci mediana este S_0 exp((mu - sigma^2/2) T)",
                    "ln S_T are o distribuție Student-t, deci nu are mediană"
                ],
                "correctExplanation": "Pentru f(S) = ln S, lema lui Itô adaugă (1/2) f''(S) sigma^2 S^2 = -sigma^2/2, deoarece (dW)^2 = dt. Media rămîne S_0 exp(mu T); mediana este mai mică, S_0 exp((mu - sigma^2/2) T).",
                "incorrectExplanation": "Ecuația GBM este corectă; greșeala este aplicarea regulii obișnuite de derivare unei difuzii, care pierde termenul -sigma^2/2."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: the Itô integral",
                "text": "An AI assistant writes: \"As in ordinary calculus, the integral of W dW from 0 to T equals W_T^2/2, so its expected value is T/2.\" What is wrong?",
                "options": [
                    "The Itô integral equals (W_T^2 - T)/2, so its expected value is 0",
                    "The integral equals W_T, so its expected value is 0",
                    "The expected value of W_T^2 is T^2, so the mean is T^2/2",
                    "Stochastic integrals have no expected value"
                ],
                "correctExplanation": "Itô's lemma for f(x) = x^2 gives d(W^2) = 2W dW + dt, hence the integral of W dW is (W_T^2 - T)/2. It is a martingale with mean 0; W_T^2/2 is the Stratonovich integral, whose mean T/2 reflects that it anticipates the move.",
                "incorrectExplanation": "The ordinary-calculus answer W_T^2/2 misses the -T/2 term that comes from the quadratic variation of Brownian motion."
            },
            "ro": {
                "title": "Găsiți eroarea AI: integrala Itô",
                "text": "Un asistent AI scrie: „Ca în calculul obișnuit, integrala lui W dW de la 0 la T este W_T^2/2, deci valoarea ei așteptată este T/2.” Ce este greșit?",
                "options": [
                    "Integrala Itô este (W_T^2 - T)/2, deci valoarea ei așteptată este 0",
                    "Integrala este egală cu W_T, deci valoarea ei așteptată este 0",
                    "Valoarea așteptată a lui W_T^2 este T^2, deci media este T^2/2",
                    "Integralele stochastice nu au valoare așteptată"
                ],
                "correctExplanation": "Lema lui Itô pentru f(x) = x^2 dă d(W^2) = 2W dW + dt, deci integrala lui W dW este (W_T^2 - T)/2. Este o martingală cu media 0; W_T^2/2 este integrala Stratonovich, a cărei medie T/2 arată că anticipează mișcarea.",
                "incorrectExplanation": "Răspunsul din calculul obișnuit, W_T^2/2, omite termenul -T/2 care provine din variația pătratică a mișcării browniene."
            }
        }
    ]
};

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
            "correct": 1,
            "en": {
                "title": "Scaling a random walk",
                "text": "To obtain Brownian motion as the limit of a random walk with n steps on [0, 1], the time step is 1/n. What is the space step?",
                "options": [
                    "1/n",
                    "1/sqrt(n)",
                    "1",
                    "log(n)/n"
                ],
                "correctExplanation": "With steps of size 1/sqrt(n) the variance at time t stays equal to t for every n, the only scaling with a non-trivial limit.",
                "incorrectExplanation": "Steps of 1/n make the walk collapse to zero, steps of 1 make it explode; only 1/sqrt(n) keeps the variance at t."
            },
            "ro": {
                "title": "Scalarea unui mers aleator",
                "text": "Pentru a obține mișcarea browniană ca limită a unui mers aleator cu n pași pe [0, 1], pasul de timp este 1/n. Care este pasul de spațiu?",
                "options": [
                    "1/n",
                    "1/sqrt(n)",
                    "1",
                    "log(n)/n"
                ],
                "correctExplanation": "Cu pași de mărime 1/sqrt(n), dispersia la momentul t rămâne egală cu t pentru orice n: singura scalare cu o limită netrivială.",
                "incorrectExplanation": "Pașii de 1/n fac mersul să se reducă la zero, pașii de 1 îl fac să explodeze; doar 1/sqrt(n) păstrează dispersia egală cu t."
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
            "correct": 0,
            "en": {
                "title": "Brownian increments",
                "text": "For a standard Brownian motion and s < t, what is the distribution of W_t - W_s?",
                "options": [
                    "Normal with mean 0 and variance t - s, independent of the path up to s",
                    "Normal with mean 0 and variance t",
                    "Uniform on [-(t - s), t - s]",
                    "Normal with mean W_s and variance 1"
                ],
                "correctExplanation": "Brownian increments are independent of the past and Normal with variance equal to the elapsed time.",
                "incorrectExplanation": "The variance of an increment equals the length of the interval, not the total time, and the mean is zero."
            },
            "ro": {
                "title": "Creșterile browniene",
                "text": "Pentru o mișcare browniană standard și s < t, care este distribuția lui W_t - W_s?",
                "options": [
                    "Normală cu media 0 și dispersia t - s, independentă de traiectoria până la s",
                    "Normală cu media 0 și dispersia t",
                    "Uniformă pe [-(t - s), t - s]",
                    "Normală cu media W_s și dispersia 1"
                ],
                "correctExplanation": "Creșterile browniene sunt independente de trecut și Normale, cu dispersia egală cu timpul scurs.",
                "incorrectExplanation": "Dispersia unei creșteri este egală cu lungimea intervalului, nu cu timpul total, iar media este zero."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Quadratic variation",
                "text": "What is the limit of the sum of squared Brownian increments over [0, T] as the grid becomes finer?",
                "options": [
                    "0",
                    "Infinity",
                    "T",
                    "W_T squared"
                ],
                "correctExplanation": "The quadratic variation of Brownian motion is deterministic and equals T; this is the origin of (dW)^2 = dt.",
                "incorrectExplanation": "The total variation (sum of absolute increments) diverges, but the sum of squares converges to T, not to 0 or W_T squared."
            },
            "ro": {
                "title": "Variația pătratică",
                "text": "Care este limita sumei pătratelor creșterilor browniene pe [0, T] când grila devine tot mai fină?",
                "options": [
                    "0",
                    "Infinit",
                    "T",
                    "W_T la pătrat"
                ],
                "correctExplanation": "Variația pătratică a mișcării browniene este deterministă și egală cu T; de aici provine (dW)^2 = dt.",
                "incorrectExplanation": "Variația totală (suma creșterilor în valoare absolută) diverge, dar suma pătratelor converge la T, nu la 0 sau la W_T la pătrat."
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
                "text": "De ce finanțele folosesc integrala Itô, evaluată în capătul stâng al fiecărui interval?",
                "options": [
                    "Este singura integrală cu o formă închisă",
                    "Regula punctului de mijloc nu converge",
                    "Poziția trebuie aleasă înainte de a cunoaște următoarea mișcare a prețului, deci integrandul nu poate privi în viitor",
                    "Face mișcarea browniană derivabilă"
                ],
                "correctExplanation": "Evaluarea în capătul stâng păstrează integrandul adaptat: o strategie de tranzacționare decisă cu informația de azi.",
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
                "correctExplanation": "Sumând identitatea pentru fiecare creștere se obține W_T^2/2 minus jumătate din variația pătratică, T/2.",
                "incorrectExplanation": "Calculul obișnuit ar da W_T^2/2; termenul suplimentar -T/2 vine din variația pătratică, iar rezultatul este aleator, nu 0."
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
                "incorrectExplanation": "Termenii a f' dt și b f' dW apar și în regula obișnuită; noutatea este termenul de ordinul doi."
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
                "text": "Dacă dS = mu S dt + sigma S dW, cât este d ln S?",
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
            "correct": 0,
            "en": {
                "title": "Mean versus median",
                "text": "Under GBM with the S&P 500 parameters, the 10-year mean gross return is 2.71 and the median 2.30. What share of paths ends below the mean?",
                "options": [
                    "About 61%",
                    "Exactly 50%",
                    "About 7%",
                    "About 90%"
                ],
                "correctExplanation": "P(S_T < E[S_T]) = Phi(sigma sqrt(T)/2), about 61% here: the mean is pulled up by a few very large outcomes.",
                "incorrectExplanation": "Half of the paths end below the median, not the mean; the 7% figure is the probability of ending below today's level."
            },
            "ro": {
                "title": "Media și mediana",
                "text": "Sub GBM cu parametrii S&P 500, randamentul brut mediu pe 10 ani este 2,71, iar mediana 2,30. Ce proporție dintre traiectorii se încheie sub medie?",
                "options": [
                    "Circa 61%",
                    "Exact 50%",
                    "Circa 7%",
                    "Circa 90%"
                ],
                "correctExplanation": "P(S_T < E[S_T]) = Phi(sigma sqrt(T)/2), circa 61% aici: media este trasă în sus de câteva rezultate foarte mari.",
                "incorrectExplanation": "Jumătate dintre traiectorii se încheie sub mediană, nu sub medie; cifra de 7% este probabilitatea de a încheia sub nivelul de azi."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Drift precision",
                "text": "How can the precision of the estimated drift of GBM be improved?",
                "options": [
                    "By sampling daily instead of monthly",
                    "By using intraday data",
                    "Only by a longer calendar span of data",
                    "By using log instead of simple returns"
                ],
                "correctExplanation": "The standard error of the drift is sigma/sqrt(T): it depends on the calendar length only, since the sum of log returns uses only the first and last prices.",
                "incorrectExplanation": "Sampling more often improves the volatility estimate, not the drift estimate."
            },
            "ro": {
                "title": "Precizia driftului",
                "text": "Cum poate fi îmbunătățită precizia driftului estimat al GBM?",
                "options": [
                    "Prin eșantionare zilnică în loc de lunară",
                    "Prin folosirea datelor intraday",
                    "Doar printr-o durată calendaristică mai lungă a datelor",
                    "Prin randamente log în loc de randamente simple"
                ],
                "correctExplanation": "Eroarea standard a driftului este sigma/sqrt(T): depinde doar de durata calendaristică, deoarece suma randamentelor log folosește doar primul și ultimul preț.",
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
                "correctExplanation": "Următorul termen Itô-Taylor (1/2) b b' [(dW)^2 - dt] are media zero, dar corectează fiecare traiectorie, dând ordinul tare 1.",
                "incorrectExplanation": "Milstein păstrează o singură mișcare browniană și un drift explicit; corecția are media zero, deci nu schimbă media creșterilor."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Monte Carlo and weak error",
                "text": "With 20,000 paths the Monte Carlo estimate of the weak error stops decreasing at small step sizes. Why?",
                "options": [
                    "Euler-Maruyama has no weak convergence",
                    "The random numbers repeat",
                    "The exact mean of X_T is unknown",
                    "The Monte Carlo standard error, about 0.07, exceeds the true weak error"
                ],
                "correctExplanation": "The standard deviation of X_T is about 9.7, so 20,000 paths give a standard error near 0.07, ten times the weak error at the finest step.",
                "incorrectExplanation": "The weak order of Euler-Maruyama is 1 and the exact mean e^2 is known; the flattening is sampling noise."
            },
            "ro": {
                "title": "Monte Carlo și eroarea slabă",
                "text": "Cu 20.000 de traiectorii, estimarea Monte Carlo a erorii slabe nu mai scade la pași mici. De ce?",
                "options": [
                    "Euler-Maruyama nu are convergență slabă",
                    "Numerele aleatoare se repetă",
                    "Media exactă a lui X_T este necunoscută",
                    "Eroarea standard Monte Carlo, circa 0,07, depășește eroarea slabă reală"
                ],
                "correctExplanation": "Abaterea standard a lui X_T este circa 9,7, deci 20.000 de traiectorii dau o eroare standard de circa 0,07, de zece ori eroarea slabă la pasul cel mai fin.",
                "incorrectExplanation": "Ordinul slab al schemei Euler-Maruyama este 1, iar media exactă e^2 este cunoscută; aplatizarea este zgomot de selecție."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Half-life",
                "text": "For an Ornstein-Uhlenbeck process with speed kappa, what is the half-life of a deviation from the long-run mean?",
                "options": [
                    "1 / kappa",
                    "ln 2 / kappa",
                    "kappa / 2",
                    "ln 2 * kappa"
                ],
                "correctExplanation": "The expected deviation decays like exp(-kappa t), which halves after ln 2 / kappa.",
                "incorrectExplanation": "1/kappa is the mean lifetime (decay to 1/e), not the half-life."
            },
            "ro": {
                "title": "Timpul de înjumătățire",
                "text": "Pentru un proces Ornstein-Uhlenbeck cu viteza kappa, care este timpul de înjumătățire al unei abateri de la media pe termen lung?",
                "options": [
                    "1 / kappa",
                    "ln 2 / kappa",
                    "kappa / 2",
                    "ln 2 * kappa"
                ],
                "correctExplanation": "Abaterea așteptată scade ca exp(-kappa t), care se înjumătățește după ln 2 / kappa.",
                "incorrectExplanation": "1/kappa este durata medie (scădere la 1/e), nu timpul de înjumătățire."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "OU in discrete time",
                "text": "Sampled every Delta t, an Ornstein-Uhlenbeck process is exactly",
                "options": [
                    "A random walk",
                    "An AR(1) with coefficient kappa",
                    "An AR(1) with coefficient b = exp(-kappa Delta t)",
                    "A moving average of order 1"
                ],
                "correctExplanation": "The exact transition is Normal with mean theta + (x - theta) exp(-kappa Delta t): an AR(1), so maximum likelihood is OLS.",
                "incorrectExplanation": "The AR coefficient depends on the sampling step through exp(-kappa Delta t); kappa itself is a rate per year."
            },
            "ro": {
                "title": "OU în timp discret",
                "text": "Eșantionat la fiecare Delta t, un proces Ornstein-Uhlenbeck este exact",
                "options": [
                    "Un mers aleator",
                    "Un AR(1) cu coeficientul kappa",
                    "Un AR(1) cu coeficientul b = exp(-kappa Delta t)",
                    "O medie mobilă de ordinul 1"
                ],
                "correctExplanation": "Tranziția exactă este Normală cu media theta + (x - theta) exp(-kappa Delta t): un AR(1), deci verosimilitatea maximă este OLS.",
                "incorrectExplanation": "Coeficientul AR depinde de pasul de eșantionare prin exp(-kappa Delta t); kappa este o rată pe an."
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
                "correctExplanation": "Simularea din curs dă o deplasare de 0,063 pentru cei 72 de ani de randamente ale titlurilor de stat, aproape de 4/T = 0,055: revenirea la medie pare mai rapidă decât este.",
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
                "correctExplanation": "În Vasicek rata este Normală și poate deveni negativă; difuzia sqrt(r) din CIR scade lângă zero.",
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
                "correctExplanation": "An i.i.d. model cannot separate a jump from a volatile period, so it uses frequent small jumps to fatten the tails; the Lee-Mykland test finds under one jump per year.",
                "incorrectExplanation": "Merton returns are still independent over time, so they cannot produce clustering; true jumps are rare."
            },
            "ro": {
                "title": "Merton estimat prin MLE",
                "text": "Estimat prin verosimilitate maximă pe randamentele zilnice ale S&P 500, modelul Merton dă circa 100 de salturi mici pe an. Cum trebuie citit acest rezultat?",
                "options": [
                    "Modelul i.i.d. folosește salturile pentru a imita volatilitatea variabilă",
                    "S&P 500 sare la fiecare două-trei zile",
                    "Estimarea este o eroare numerică",
                    "Salturile explică gruparea volatilității"
                ],
                "correctExplanation": "Un model i.i.d. nu poate separa un salt de o perioadă volatilă, așa că folosește salturi mici și frecvente pentru a îngroșa cozile; testul Lee-Mykland găsește sub un salt pe an.",
                "incorrectExplanation": "Randamentele Merton rămân independente în timp, deci nu pot produce grupare; salturile reale sunt rare."
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
                    "Testul folosește date săptămânale",
                    "Randamentele mari sunt eliminate înainte de test",
                    "Au apărut în perioade agitate, deci nu erau mari în raport cu volatilitatea locală"
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
                "text": "Cum se modifică excesul de aplatizare al randamentelor Merton cu orizontul Delta t?",
                "options": [
                    "Crește ca Delta t",
                    "Rămâne constant",
                    "Scade ca 1/Delta t",
                    "Scade ca 1/sqrt(Delta t)"
                ],
                "correctExplanation": "Cumulantul de ordinul patru crește ca Delta t, iar pătratul dispersiei ca Delta t^2, deci excesul de aplatizare scade ca 1/Delta t: salturile contează cel mai mult pe orizonturi scurte.",
                "incorrectExplanation": "Excesul de aplatizare este cumulantul de ordinul patru împărțit la pătratul dispersiei, iar cele două se scalează diferit cu Delta t."
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
                "title": "Efectul de levier și panta",
                "text": "În modelul Heston cu rho = -0,69, cum variază volatilitățile implicite pe trei luni cu prețul de exercitare?",
                "options": [
                    "Sunt constante",
                    "Cresc odată cu prețul de exercitare",
                    "Scad odată cu prețul de exercitare: o pantă descendentă, ca la opțiunile pe indici bursieri",
                    "Formează un zâmbet simetric în jurul prețului la bani"
                ],
                "correctExplanation": "Corelația negativă dintre randamente și varianță îngroașă coada stângă, deci prețurile de exercitare mici au volatilități implicite mai mari.",
                "incorrectExplanation": "O linie orizontală este cazul Black-Scholes; un zâmbet simetric apare cu rho = 0, iar o curbă crescătoare cu rho > 0."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Feller condition",
                "text": "What does the Feller condition 2 kappa theta >= xi^2 guarantee in the Heston model?",
                "options": [
                    "Returns are Normal",
                    "The volatility smile is flat",
                    "The model has no leverage effect",
                    "The variance never reaches zero"
                ],
                "correctExplanation": "When the pull towards theta is strong enough relative to the volatility of variance, the CIR variance stays strictly positive.",
                "incorrectExplanation": "The condition concerns only the variance process; it says nothing about the return distribution, the smile or rho."
            },
            "ro": {
                "title": "Condiția Feller",
                "text": "Ce garantează condiția Feller 2 kappa theta >= xi^2 în modelul Heston?",
                "options": [
                    "Randamentele sunt Normale",
                    "Zâmbetul volatilității este plat",
                    "Modelul nu are efect de levier",
                    "Varianța nu atinge niciodată zero"
                ],
                "correctExplanation": "Când atracția spre theta este suficient de puternică în raport cu volatilitatea varianței, varianța CIR rămâne strict pozitivă.",
                "incorrectExplanation": "Condiția privește doar procesul varianței; nu spune nimic despre distribuția randamentelor, zâmbet sau rho."
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
                    "Merton reproduces the tail index, Heston the volatility clustering, and neither the excess kurtosis",
                    "Merton reproduces volatility clustering",
                    "Heston reproduces the excess kurtosis of 10.9"
                ],
                "correctExplanation": "Merton's Hill index (2.68) is near the data (2.56) but its ACF of |r| is zero; Heston's ACF matches, but both give an excess kurtosis near 3.5 against 10.9.",
                "incorrectExplanation": "GBM fails on every statistic, i.i.d. jumps cannot create clustering, and no single model reaches the kurtosis: jumps and stochastic volatility are needed together."
            },
            "ro": {
                "title": "Ce model?",
                "text": "Simulate și comparate cu S&P 500, ce afirmație corespunde rezultatelor din curs?",
                "options": [
                    "GBM reproduce toate faptele stilizate",
                    "Merton reproduce indicele de coadă, Heston gruparea volatilității și niciunul excesul de aplatizare",
                    "Merton reproduce gruparea volatilității",
                    "Heston reproduce excesul de aplatizare de 10,9"
                ],
                "correctExplanation": "Indicele Hill Merton (2,68) este aproape de date (2,56), dar ACF a lui |r| este zero; ACF Heston se potrivește, dar ambele dau un exces de aplatizare de circa 3,5 față de 10,9.",
                "incorrectExplanation": "GBM eșuează la toate statisticile, salturile i.i.d. nu pot crea grupare și niciun model singur nu atinge aplatizarea: este nevoie simultan de salturi și volatilitate stochastică."
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
                    "S-a folosit calculul obișnuit în loc de calculul Itô: d ln S = (mu - sigma^2/2) dt + sigma dW, deci mediana este S_0 exp((mu - sigma^2/2) T)",
                    "ln S_T are o distribuție Student-t, deci nu are mediană"
                ],
                "correctExplanation": "Pentru f(S) = ln S, lema lui Itô adaugă (1/2) f''(S) sigma^2 S^2 = -sigma^2/2, deoarece (dW)^2 = dt. Media rămâne S_0 exp(mu T); mediana este mai mică, S_0 exp((mu - sigma^2/2) T).",
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

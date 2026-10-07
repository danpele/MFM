// ============================================================
// Quiz bank for chapter id 'portfolio': Portfolio Optimization (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['portfolio'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 2,
            "en": {
                "title": "In-sample Sharpe bias",
                "text": "Returns are i.i.d. Normal with N = 10 assets and T = 60 months; θ² = μ'Σ⁻¹μ is the true squared maximum Sharpe ratio and θ̂² its plug-in estimate with the maximum-likelihood covariance. What holds?",
                "options": [
                    "θ̂² is unbiased because the sample mean and covariance are unbiased",
                    "θ̂² is biased downwards because Σ̂⁻¹ underestimates Σ⁻¹",
                    "E[θ̂²] = (Tθ² + N)/(T − N − 2), above θ²",
                    "The bias is proportional to 1/T and does not depend on N"
                ],
                "correctExplanation": "E[Σ̂⁻¹] = T/(T−N−2)·Σ⁻¹ and E[μ̂'Σ⁻¹μ̂] = θ² + N/T; with μ̂ and Σ̂ independent this gives (Tθ² + N)/(T − N − 2), which grows with N/T.",
                "incorrectExplanation": "Unbiased inputs do not give an unbiased nonlinear function; the inverse Wishart moment inflates Σ̂⁻¹ and the bias grows with the number of assets N."
            },
            "ro": {
                "title": "Deplasarea raportului Sharpe în eșantion",
                "text": "Randamentele sînt i.i.d. din distribuția Normală, cu N = 10 active și T = 60 de luni; θ² = μ'Σ⁻¹μ este pătratul raportului Sharpe maxim adevărat, iar θ̂² estimatorul său cu covarianța de verosimilitate maximă. Ce este adevărat?",
                "options": [
                    "θ̂² este nedeplasat, pentru că media și covarianța de selecție sînt nedeplasate",
                    "θ̂² este deplasat în jos, pentru că Σ̂⁻¹ subestimează Σ⁻¹",
                    "E[θ̂²] = (Tθ² + N)/(T − N − 2), peste θ²",
                    "Deplasarea este proporțională cu 1/T și nu depinde de N"
                ],
                "correctExplanation": "E[Σ̂⁻¹] = T/(T−N−2)·Σ⁻¹ și E[μ̂'Σ⁻¹μ̂] = θ² + N/T; cu μ̂ și Σ̂ independente rezultă (Tθ² + N)/(T − N − 2), care crește cu N/T.",
                "incorrectExplanation": "O funcție neliniară de estimatori nedeplasați nu este, în general, nedeplasată; momentul Wishart invers deplasează în sus pe Σ̂⁻¹, iar deplasarea crește cu numărul de active N."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Britten-Jones regression",
                "text": "You regress the constant 1 on the vector of excess returns r_t, without a constant term. The OLS coefficients are proportional to…",
                "options": [
                    "the sample tangency weights Σ̂⁻¹μ̂, so a zero tangency weight is tested with an OLS t-test",
                    "the sample GMV weights Σ̂⁻¹1",
                    "the CAPM betas of the assets",
                    "equal weights 1/N"
                ],
                "correctExplanation": "X'X/T = Σ̂ + μ̂μ̂', and Sherman–Morrison gives b̂ = Σ̂⁻¹μ̂/(1 + θ̂²): the tangency direction (Britten-Jones, 1999).",
                "incorrectExplanation": "The regressand is a constant and there is no constant term: the coefficients involve Σ̂⁻¹μ̂, not Σ̂⁻¹1, and the regression does not explain one asset by the market."
            },
            "ro": {
                "title": "Regresia Britten-Jones",
                "text": "Regresați constanta 1 pe vectorul randamentelor în exces r_t, fără termen liber. Coeficienții OLS sînt proporționali cu…",
                "options": [
                    "ponderile tangente de selecție Σ̂⁻¹μ̂, deci o pondere tangentă nulă se testează cu un test t OLS",
                    "ponderile GMV de selecție Σ̂⁻¹1",
                    "coeficienții beta CAPM ai activelor",
                    "ponderile egale 1/N"
                ],
                "correctExplanation": "X'X/T = Σ̂ + μ̂μ̂', iar Sherman–Morrison dă b̂ = Σ̂⁻¹μ̂/(1 + θ̂²): direcția tangentă (Britten-Jones, 1999).",
                "incorrectExplanation": "Variabila dependentă este o constantă și nu există termen liber: coeficienții conțin Σ̂⁻¹μ̂, nu Σ̂⁻¹1, iar regresia nu explică un activ prin piață."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Marchenko–Pastur",
                "text": "N = 16 assets, T = 64 months, i.i.d. returns with Σ = σ²I. For large N and T, where does the largest sample eigenvalue lie?",
                "options": [
                    "Close to σ², since all true eigenvalues equal σ²",
                    "Close to 16σ², the trace of Σ",
                    "Close to σ²(1 + 0.25) = 1.25σ²",
                    "Close to σ²(1 + √0.25)² = 2.25σ²"
                ],
                "correctExplanation": "With c = N/T = 0.25 the sample eigenvalues fill [σ²(1 − √c)², σ²(1 + √c)²] = [0.25σ², 2.25σ²]: noise alone spreads them nine-fold.",
                "incorrectExplanation": "Sampling noise spreads the eigenvalues around σ² even when all true ones are equal; the edge involves the square root of c = N/T, and the trace is the sum, not the largest eigenvalue."
            },
            "ro": {
                "title": "Marchenko–Pastur",
                "text": "N = 16 active, T = 64 de luni, randamente i.i.d. cu Σ = σ²I. Pentru N și T mari, unde se află cea mai mare valoare proprie de selecție?",
                "options": [
                    "Aproape de σ², pentru că toate valorile proprii adevărate sînt σ²",
                    "Aproape de 16σ², urma lui Σ",
                    "Aproape de σ²(1 + 0,25) = 1,25σ²",
                    "Aproape de σ²(1 + √0,25)² = 2,25σ²"
                ],
                "correctExplanation": "Cu c = N/T = 0,25, valorile proprii de selecție acoperă intervalul [σ²(1 − √c)², σ²(1 + √c)²] = [0,25σ², 2,25σ²]: numai zgomotul produce un raport de nouă între extreme.",
                "incorrectExplanation": "Zgomotul de eșantionare dispersează valorile proprii în jurul lui σ² chiar cînd cele adevărate sînt egale; limita superioară conține rădăcina pătrată a lui c = N/T, iar urma este suma, nu cea mai mare valoare proprie."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Error maximisation",
                "text": "Why did Michaud (1989) call mean–variance optimisers 'estimation-error maximisers'?",
                "options": [
                    "They minimise the variance of estimation errors",
                    "They ignore the covariance matrix",
                    "They always choose equal weights",
                    "They overweight assets whose means are overestimated and risks underestimated"
                ],
                "correctExplanation": "The optimiser treats noise in the inputs as information and loads on the largest errors.",
                "incorrectExplanation": "The point is that the optimiser chases the assets that look best because of estimation noise."
            },
            "ro": {
                "title": "Maximizarea erorilor",
                "text": "De ce a numit Michaud (1989) optimizatorii medie–varianță „maximizatori ai erorilor de estimare”?",
                "options": [
                    "Pentru că minimizează varianța erorilor de estimare",
                    "Pentru că ignoră matricea de covarianță",
                    "Pentru că aleg mereu ponderi egale",
                    "Pentru că supraponderează activele cu medii supraestimate și riscuri subestimate"
                ],
                "correctExplanation": "Optimizatorul tratează zgomotul din date drept informație și atribuie ponderi mari exact activelor cu cele mai mari erori.",
                "incorrectExplanation": "Ideea este că optimizatorul favorizează activele care par cele mai bune doar din cauza zgomotului de estimare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Precision of the mean",
                "text": "SPY has an annual volatility of about 15%. Roughly how many years of data give a standard error of 1% for its annual mean?",
                "options": [
                    "About 2 years of daily data",
                    "About 220 years",
                    "About 15 years",
                    "About 50 years of monthly data"
                ],
                "correctExplanation": "The standard error is σ/√Y, so Y = (0.15/0.01)² ≈ 220 years, whatever the sampling frequency.",
                "incorrectExplanation": "Sampling more often does not help: the precision of a mean depends on the length of the sample in years."
            },
            "ro": {
                "title": "Precizia mediei",
                "text": "SPY are o volatilitate anuală de circa 15%. Aproximativ cîți ani de date dau o eroare standard de 1% pentru media anuală?",
                "options": [
                    "Circa 2 ani de date zilnice",
                    "Circa 220 de ani",
                    "Circa 15 ani",
                    "Circa 50 de ani de date lunare"
                ],
                "correctExplanation": "Eroarea standard este σ/√Y, deci Y = (0,15/0,01)² ≈ 220 de ani, indiferent de frecvența eșantionării.",
                "incorrectExplanation": "Eșantionarea mai deasă nu ajută: precizia unei medii depinde de lungimea eșantionului în ani."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "The 1/N benchmark",
                "text": "What did DeMiguel, Garlappi and Uppal (2009) find?",
                "options": [
                    "None of 14 optimisation models beat 1/N consistently out of sample",
                    "Sample mean–variance beats 1/N with five years of data",
                    "1/N has the lowest variance of all rules",
                    "Only shrinkage beats 1/N"
                ],
                "correctExplanation": "Estimation error offsets the gains from optimisation; with 25 assets sample MV needs about 3000 months of data.",
                "incorrectExplanation": "Their result is that no model beat equal weights consistently in Sharpe ratio, certainty equivalent or turnover."
            },
            "ro": {
                "title": "Reperul 1/N",
                "text": "Ce au găsit DeMiguel, Garlappi și Uppal (2009)?",
                "options": [
                    "Niciunul dintre 14 modele de optimizare nu a depășit consecvent 1/N în afara eșantionului",
                    "Portofoliul medie–varianță de selecție depășește 1/N cu cinci ani de date",
                    "1/N are cea mai mică varianță dintre toate regulile",
                    "Doar shrinkage-ul depășește 1/N"
                ],
                "correctExplanation": "Eroarea de estimare anulează cîștigul optimizării; cu 25 de active, MV de selecție are nevoie de circa 3000 de luni de date.",
                "incorrectExplanation": "Rezultatul lor este că niciun model nu a depășit consecvent ponderile egale în raport Sharpe, echivalent cert sau turnover."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Ledoit–Wolf intensity",
                "text": "N is fixed, the sample length T grows, and the target converges to a matrix different from the true covariance matrix. What happens to the optimal Ledoit–Wolf shrinkage intensity δ* = κ/T?",
                "options": [
                    "It tends to 1: the target dominates",
                    "It tends to 0 at rate 1/T",
                    "It stays constant, because κ does not depend on T",
                    "It tends to 0 at rate 1/√T, the rate of the sample covariance"
                ],
                "correctExplanation": "With a misspecified target, κ converges to a constant, so δ* = κ/T falls like 1/T: with long samples the consistent sample matrix wins (if the target were correct, its bias would vanish too and δ* need not go to zero).",
                "incorrectExplanation": "The estimation error of S shrinks as T grows while the bias of the target does not, so the weight on the target must vanish; the rate is that of δ* = κ/T, not the √T rate of the estimator itself."
            },
            "ro": {
                "title": "Intensitatea Ledoit–Wolf",
                "text": "N este fix, lungimea eșantionului T crește, iar ținta converge la o matrice diferită de matricea de covarianță adevărată. Ce se întîmplă cu intensitatea optimă de shrinkage Ledoit–Wolf δ* = κ/T?",
                "options": [
                    "Tinde la 1: ținta domină",
                    "Tinde la 0 cu viteza 1/T",
                    "Rămîne constantă, pentru că κ nu depinde de T",
                    "Tinde la 0 cu viteza 1/√T, viteza covarianței de selecție"
                ],
                "correctExplanation": "Cu o țintă greșit specificată, κ converge la o constantă, deci δ* = κ/T scade ca 1/T: în eșantioane lungi devine preferabilă matricea de selecție, consistentă (dacă ținta ar fi corectă, deplasarea ei ar dispărea și δ* nu ar tinde neapărat la zero).",
                "incorrectExplanation": "Eroarea de estimare a lui S scade cu T, dar deplasarea țintei nu, deci ponderea țintei trebuie să dispară; viteza este cea a lui δ* = κ/T, nu viteza √T a estimatorului."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Black–Litterman with certain views",
                "text": "In Black–Litterman, the views are held with certainty (Ω → 0). What does the posterior mean μ_BL become?",
                "options": [
                    "The implied returns π: the views are ignored",
                    "q for every asset, even those not in the views",
                    "The GLS projection of π that satisfies Pμ_BL = q exactly",
                    "It is undefined, because Ω⁻¹ does not exist"
                ],
                "correctExplanation": "μ_BL = π + τΣP'(PτΣP' + Ω)⁻¹(q − Pπ); with Ω = 0 the views hold exactly and π is moved as little as possible in the τΣ metric (restricted least squares).",
                "incorrectExplanation": "The views pin Pμ_BL to q; means of assets outside the views can also move through their covariance with the viewed combinations, and the limit exists in the form π + τΣP'(PτΣP')⁻¹(q − Pπ)."
            },
            "ro": {
                "title": "Black–Litterman cu opinii certe",
                "text": "În Black–Litterman, opiniile sînt sigure (Ω → 0). Ce devine media a posteriori μ_BL?",
                "options": [
                    "Randamentele implicite π: opiniile sînt ignorate",
                    "q pentru fiecare activ, chiar și pentru cele din afara opiniilor",
                    "Proiecția GLS a lui π care satisface exact Pμ_BL = q",
                    "Nu este definită, pentru că Ω⁻¹ nu există"
                ],
                "correctExplanation": "μ_BL = π + τΣP'(PτΣP' + Ω)⁻¹(q − Pπ); cu Ω = 0 opiniile sînt satisfăcute exact, iar π se modifică cît mai puțin în metrica τΣ (cele mai mici pătrate cu restricții).",
                "incorrectExplanation": "Opiniile fixează Pμ_BL la q; mediile activelor din afara opiniilor se pot și ele modifica prin covarianța cu combinațiile din opinii, iar limita există sub forma π + τΣP'(PτΣP')⁻¹(q − Pπ)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Shrinkage estimator",
                "text": "What is the Ledoit–Wolf shrinkage estimator of the covariance matrix?",
                "options": [
                    "The sample matrix with negative eigenvalues set to zero",
                    "A matrix estimated from daily instead of monthly data",
                    "A weighted average δF + (1 − δ)S of a structured target and the sample matrix",
                    "The identity matrix"
                ],
                "correctExplanation": "δ is chosen from the data to minimise the expected squared distance to the true matrix.",
                "incorrectExplanation": "Shrinkage mixes the noisy sample matrix with a biased but stable target."
            },
            "ro": {
                "title": "Estimatorul de tip shrinkage",
                "text": "Ce este estimatorul de shrinkage Ledoit–Wolf al matricei de covarianță?",
                "options": [
                    "Matricea de selecție cu valorile proprii negative puse la zero",
                    "O matrice estimată din date zilnice în loc de lunare",
                    "O medie ponderată δF + (1 − δ)S între o țintă structurată și matricea de selecție",
                    "Matricea identitate"
                ],
                "correctExplanation": "δ este ales din date astfel încît să minimizeze distanța pătratică așteptată față de matricea adevărată.",
                "incorrectExplanation": "Shrinkage-ul combină matricea de selecție zgomotoasă cu o țintă deplasată, dar stabilă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Constraints as shrinkage",
                "text": "What did Jagannathan and Ma (2003) show about no-short-sale constraints?",
                "options": [
                    "They always lower the Sharpe ratio",
                    "They make the covariance matrix singular",
                    "They are equivalent to adding a risk-free asset",
                    "They act like shrinkage of the covariance matrix and can reduce out-of-sample risk"
                ],
                "correctExplanation": "The long-only GMV equals the unconstrained GMV of a modified covariance matrix: the 'wrong' constraint helps.",
                "incorrectExplanation": "Their point is that the constraint implicitly shrinks the covariances of the assets on which it binds."
            },
            "ro": {
                "title": "Restricțiile ca shrinkage",
                "text": "Ce au arătat Jagannathan și Ma (2003) despre restricțiile fără vînzări în lipsă?",
                "options": [
                    "Scad întotdeauna raportul Sharpe",
                    "Fac matricea de covarianță singulară",
                    "Sînt echivalente cu adăugarea unui activ fără risc",
                    "Acționează ca un shrinkage al matricei de covarianță și pot reduce riscul în afara eșantionului"
                ],
                "correctExplanation": "GMV long-only este GMV fără restricții al unei matrice de covarianță modificate: restricția „greșită” poate reduce riscul în afara eșantionului.",
                "incorrectExplanation": "Ideea lor este că restricția aplică implicit shrinkage covarianțelor activelor pe care este activă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Implied returns",
                "text": "In Black–Litterman, what are the implied (equilibrium) returns π?",
                "options": [
                    "The sample means of the last ten years",
                    "The returns that make the benchmark portfolio optimal: π = δΣw_b",
                    "The returns of the risk-free asset",
                    "The investor's views"
                ],
                "correctExplanation": "Reverse optimisation starts from a benchmark and asks which expected returns make it mean–variance optimal.",
                "incorrectExplanation": "π comes from reverse optimisation of a benchmark, not from sample means or views."
            },
            "ro": {
                "title": "Randamentele implicite",
                "text": "În Black–Litterman, ce sînt randamentele implicite (de echilibru) π?",
                "options": [
                    "Mediile de selecție din ultimii zece ani",
                    "Randamentele care fac optim portofoliul de referință: π = δΣw_b",
                    "Randamentele activului fără risc",
                    "Opiniile investitorului"
                ],
                "correctExplanation": "Optimizarea inversă pornește de la un portofoliu de referință și întreabă ce randamente așteptate îl fac optim medie–varianță.",
                "incorrectExplanation": "π provine din optimizarea inversă a unui portofoliu de referință, nu din medii de selecție sau opinii."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Posterior with one view",
                "text": "Prior π = 5% with variance 0.00128 and a view q = 8% with variance 0.0004. What is the Black–Litterman posterior mean?",
                "options": [
                    "5.0%",
                    "6.5%",
                    "About 7.3%",
                    "8.0%"
                ],
                "correctExplanation": "Precision weighting: (781 × 5% + 2500 × 8%)/(781 + 2500) = 7.29%; the view is more precise, so it gets weight 0.76.",
                "incorrectExplanation": "The posterior is a precision-weighted average, closer to the more precise of the two."
            },
            "ro": {
                "title": "Media a posteriori cu o opinie",
                "text": "A priori π = 5% cu varianța 0,00128 și o opinie q = 8% cu varianța 0,0004. Care este media a posteriori Black–Litterman?",
                "options": [
                    "5,0%",
                    "6,5%",
                    "Circa 7,3%",
                    "8,0%"
                ],
                "correctExplanation": "Ponderare cu precizia: (781 × 5% + 2500 × 8%)/(781 + 2500) = 7,29%; opinia este mai precisă, deci primește ponderea 0,76.",
                "incorrectExplanation": "Media a posteriori este o medie ponderată cu precizia, mai aproape de sursa mai precisă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Which weights move",
                "text": "With Ω = diag(PτΣP') and a single view on XLK minus XLU, which Black–Litterman weights change relative to the benchmark?",
                "options": [
                    "Only XLK and XLU",
                    "All nine sectors",
                    "None",
                    "Only the sectors most correlated with XLK"
                ],
                "correctExplanation": "In the He–Litterman form the weight change is P'λ: only the assets in the view move (XLK 11.1% → 14.4%, XLU 11.1% → 7.8%).",
                "incorrectExplanation": "The deviation from the benchmark lies in the span of the view portfolio."
            },
            "ro": {
                "title": "Ponderile modificate de o opinie",
                "text": "Cu Ω = diag(PτΣP') și o singură opinie asupra XLK minus XLU, ce ponderi Black–Litterman se modifică față de referință?",
                "options": [
                    "Doar XLK și XLU",
                    "Toate cele nouă sectoare",
                    "Niciuna",
                    "Doar sectoarele cele mai corelate cu XLK"
                ],
                "correctExplanation": "În forma He–Litterman modificarea ponderilor este P'λ: se modifică doar ponderile activelor din opinie (XLK 11,1% → 14,4%, XLU 11,1% → 7,8%).",
                "incorrectExplanation": "Abaterea de la referință se află în direcția portofoliului opiniei."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Studentized bootstrap",
                "text": "Why do Ledoit and Wolf (2008) bootstrap the studentized statistic |Δ̂* − Δ̂|/s(Δ̂*) rather than Δ̂* itself?",
                "options": [
                    "The studentized statistic is asymptotically pivotal, so the bootstrap test is more accurate than the Normal approximation",
                    "Studentizing removes the serial dependence of the returns",
                    "Studentizing makes the returns Normal",
                    "Studentizing reduces the computing time"
                ],
                "correctExplanation": "A pivotal statistic has a limit law free of unknown parameters; bootstrapping it gives a higher-order refinement, which a non-studentized bootstrap does not.",
                "incorrectExplanation": "Serial dependence is handled by resampling blocks, not by studentizing, and a studentized bootstrap costs more computing time, not less."
            },
            "ro": {
                "title": "Bootstrap studentizat",
                "text": "De ce aplică Ledoit și Wolf (2008) bootstrap statisticii studentizate |Δ̂* − Δ̂|/s(Δ̂*), și nu direct lui Δ̂*?",
                "options": [
                    "Statistica studentizată este asimptotic pivotală, deci testul bootstrap este mai precis decît aproximarea Normală",
                    "Studentizarea elimină dependența serială a randamentelor",
                    "Studentizarea face randamentele să urmeze distribuția Normală",
                    "Studentizarea reduce timpul de calcul"
                ],
                "correctExplanation": "O statistică pivotală are o lege limită fără parametri necunoscuți; bootstrap-ul ei dă o rafinare de ordin superior, pe care bootstrap-ul nestudentizat nu o dă.",
                "incorrectExplanation": "Dependența serială se tratează prin reeșantionarea blocurilor, nu prin studentizare, iar bootstrap-ul studentizat costă mai mult timp de calcul, nu mai puțin."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Multiple testing",
                "text": "You test 21 rules against 1/N; the smallest p-value is 0.03. What does Holm's procedure at a 5% family-wise level conclude?",
                "options": [
                    "Significant, because 0.03 < 0.05",
                    "Significant, because correlated tests need no adjustment",
                    "Holm cannot be used, because it requires independent tests",
                    "Not significant, because 21 × 0.03 = 0.63 > 0.05"
                ],
                "correctExplanation": "Holm compares the smallest p-value with 0.05/21 ≈ 0.0024; the adjusted value 0.63 is far above 5%, and Holm is valid under any dependence.",
                "incorrectExplanation": "A single p-value below 0.05 is expected by chance among 21 tests; Holm controls the family-wise error rate under arbitrary dependence, so correlation neither removes the need for it nor forbids it."
            },
            "ro": {
                "title": "Testarea multiplă",
                "text": "Testați 21 de reguli față de 1/N; cel mai mic p-value este 0,03. Ce conclude procedura Holm la un nivel de 5% pentru familie?",
                "options": [
                    "Semnificativ, pentru că 0,03 < 0,05",
                    "Semnificativ, pentru că testele corelate nu necesită ajustare",
                    "Holm nu se poate folosi, pentru că cere teste independente",
                    "Nesemnificativ, pentru că 21 × 0,03 = 0,63 > 0,05"
                ],
                "correctExplanation": "Holm compară cel mai mic p-value cu 0,05/21 ≈ 0,0024; valoarea ajustată 0,63 este mult peste 5%, iar Holm este valid sub orice dependență.",
                "incorrectExplanation": "Un p-value sub 0,05 este de așteptat din întîmplare printre 21 de teste; Holm controlează probabilitatea de cel puțin o eroare în familie sub orice dependență, deci corelația nici nu elimină ajustarea, nici nu o interzice."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Volatility ordering",
                "text": "Which ordering of volatilities holds for GMV, ERC and 1/N (Maillard, Roncalli and Teïletche, 2010)?",
                "options": [
                    "σ_ERC ≤ σ_GMV ≤ σ_1/N",
                    "σ_1/N ≤ σ_ERC ≤ σ_GMV",
                    "σ_GMV ≤ σ_ERC ≤ σ_1/N",
                    "They are always equal"
                ],
                "correctExplanation": "ERC lies between minimum variance and equal weights; on the multi-asset set: GMV-LO 5.8%, ERC 7.9%, 1/N 9.4%.",
                "incorrectExplanation": "GMV has by definition the lowest variance; ERC sits between it and 1/N."
            },
            "ro": {
                "title": "Ordinea volatilităților",
                "text": "Ce ordine a volatilităților este adevărată pentru GMV, ERC și 1/N (Maillard, Roncalli și Teïletche, 2010)?",
                "options": [
                    "σ_ERC ≤ σ_GMV ≤ σ_1/N",
                    "σ_1/N ≤ σ_ERC ≤ σ_GMV",
                    "σ_GMV ≤ σ_ERC ≤ σ_1/N",
                    "Sînt întotdeauna egale"
                ],
                "correctExplanation": "ERC se află între varianța minimă și ponderile egale; pe setul multi-active: GMV-LO 5,8%, ERC 7,9%, 1/N 9,4%.",
                "incorrectExplanation": "GMV are prin definiție cea mai mică varianță; ERC se află între ea și 1/N."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "60/40 risk",
                "text": "In a 60% SPY, 40% IEF portfolio (2002–2026), what share of the risk came from SPY?",
                "options": [
                    "About 94%",
                    "60%",
                    "About 50%",
                    "About 31%"
                ],
                "correctExplanation": "SPY's volatility (14.7%) is more than twice IEF's (6.6%) and the correlation is slightly negative, so SPY dominates the risk.",
                "incorrectExplanation": "Weights are not risk shares: the volatile asset carries most of the risk."
            },
            "ro": {
                "title": "Riscul în 60/40",
                "text": "Într-un portofoliu 60% SPY, 40% IEF (2002–2026), ce parte din risc a provenit de la SPY?",
                "options": [
                    "Circa 94%",
                    "60%",
                    "Circa 50%",
                    "Circa 31%"
                ],
                "correctExplanation": "Volatilitatea SPY (14,7%) este de peste două ori cea a IEF (6,6%), iar corelația ușor negativă, deci SPY domină riscul.",
                "incorrectExplanation": "Ponderile nu sînt cote de risc: activul volatil poartă cea mai mare parte a riscului."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "HRP",
                "text": "Which statement about Hierarchical Risk Parity (López de Prado, 2016) is correct?",
                "options": [
                    "It maximises the Sharpe ratio with sample means",
                    "It needs the inverse of the covariance matrix",
                    "It can produce negative weights",
                    "It clusters assets by correlation distance and splits weight by recursive bisection, without inverting Σ"
                ],
                "correctExplanation": "HRP works even when Σ is singular; all its weights are positive.",
                "incorrectExplanation": "HRP uses a tree and inverse-variance allocations, never a matrix inversion or expected returns."
            },
            "ro": {
                "title": "HRP",
                "text": "Ce afirmație despre Hierarchical Risk Parity (López de Prado, 2016) este corectă?",
                "options": [
                    "Maximizează raportul Sharpe cu mediile de selecție",
                    "Are nevoie de inversa matricei de covarianță",
                    "Poate produce ponderi negative",
                    "Grupează activele după distanța de corelație și împarte ponderea prin bisecție recursivă, fără a inversa Σ"
                ],
                "correctExplanation": "HRP funcționează chiar dacă Σ este singulară; toate ponderile sale sînt pozitive.",
                "incorrectExplanation": "HRP folosește un arbore și alocări invers proporționale cu varianța, niciodată o inversare de matrice sau randamente așteptate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Jagannathan–Ma mechanism",
                "text": "The long-only GMV equals the unconstrained GMV of a modified matrix S̃ = S − (λ1' + 1λ'), with λ ≥ 0 the multipliers of w ≥ 0. What does a binding constraint on asset i do?",
                "options": [
                    "It raises the variance of asset i",
                    "It lowers all covariances of asset i by λ_i, shrinking large estimates",
                    "It sets the correlations of asset i to zero",
                    "It leaves the covariance matrix unchanged"
                ],
                "correctExplanation": "s̃_ij = s_ij − λ_i − λ_j: the assets the GMV would short usually have overestimated covariances, and the constraint pulls them down, which acts as shrinkage.",
                "incorrectExplanation": "The modification subtracts nonnegative multipliers from every covariance of the constrained asset, so it lowers them rather than raising, zeroing or ignoring them."
            },
            "ro": {
                "title": "Mecanismul Jagannathan–Ma",
                "text": "GMV fără vînzări în lipsă este GMV nerestricționat al matricei modificate S̃ = S − (λ1' + 1λ'), cu λ ≥ 0 multiplicatorii restricțiilor w ≥ 0. Ce face o restricție activă pe activul i?",
                "options": [
                    "Crește varianța activului i",
                    "Scade toate covarianțele activului i cu λ_i, aplicînd shrinkage estimărilor mari",
                    "Anulează corelațiile activului i",
                    "Lasă matricea de covarianță neschimbată"
                ],
                "correctExplanation": "s̃_ij = s_ij − λ_i − λ_j: activele pe care GMV le-ar vinde în lipsă au de obicei covarianțe supraestimate, iar restricția le reduce, ceea ce acționează ca un shrinkage.",
                "incorrectExplanation": "Modificarea scade multiplicatori nenegativi din fiecare covarianță a activului restricționat, deci le micșorează, nu le crește, nu le anulează și nu le ignoră."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Out-of-sample verdict",
                "text": "What was the main out-of-sample finding of the chapter across three US universes?",
                "options": [
                    "Sample MV had the highest Sharpe ratio everywhere",
                    "GMV beat 1/N significantly everywhere",
                    "No rule beat 1/N significantly; sample MV failed in every universe",
                    "HRP beat all rules after costs"
                ],
                "correctExplanation": "The largest gain over 1/N (MV-LO on the multi-asset set, +0.29) had p = 0.12; significant differences were losses.",
                "incorrectExplanation": "Differences against 1/N were either not significant or negative."
            },
            "ro": {
                "title": "Verdictul în afara eșantionului",
                "text": "Care a fost principalul rezultat în afara eșantionului din capitol, pe cele trei universuri din SUA?",
                "options": [
                    "MV de selecție a avut cel mai mare Sharpe peste tot",
                    "GMV a depășit semnificativ 1/N peste tot",
                    "Nicio regulă nu a depășit semnificativ 1/N; MV de selecție a eșuat în toate universurile",
                    "HRP a depășit toate regulile după costuri"
                ],
                "correctExplanation": "Cel mai mare cîștig față de 1/N (MV-LO pe setul multi-active, +0,29) a avut p = 0,12; diferențele semnificative au fost negative.",
                "incorrectExplanation": "Diferențele față de 1/N au fost fie nesemnificative, fie negative."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Testing Sharpe differences",
                "text": "Why are HAC or block-bootstrap tests preferred to the i.i.d. formula for Sharpe ratio differences?",
                "options": [
                    "Returns show heavy tails and volatility clustering, which the i.i.d. Normal formula ignores",
                    "The i.i.d. formula cannot handle correlated strategies",
                    "HAC tests do not need a sample",
                    "The bootstrap always rejects the null"
                ],
                "correctExplanation": "Ledoit and Wolf (2008) use a HAC covariance of (r₁, r₂, r₁², r₂²) and a circular block bootstrap that keeps dependence.",
                "incorrectExplanation": "The i.i.d. formula does account for the correlation between strategies; its weakness is the i.i.d. Normal assumption."
            },
            "ro": {
                "title": "Testarea diferențelor de Sharpe",
                "text": "De ce sînt preferate testele HAC sau bootstrap pe blocuri formulei i.i.d. pentru diferențele de raport Sharpe?",
                "options": [
                    "Randamentele au cozi groase și volatility clustering, pe care formula i.i.d. Normală le ignoră",
                    "Formula i.i.d. nu poate trata strategii corelate",
                    "Testele HAC nu au nevoie de un eșantion",
                    "Bootstrap-ul respinge întotdeauna ipoteza nulă"
                ],
                "correctExplanation": "Ledoit și Wolf (2008) folosesc o covarianță HAC a lui (r₁, r₂, r₁², r₂²) și un bootstrap circular pe blocuri care păstrează dependența.",
                "incorrectExplanation": "Formula i.i.d. ține cont de corelația dintre strategii; slăbiciunea ei este ipoteza i.i.d. Normală."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Annualising a Sharpe ratio",
                "text": "The monthly Sharpe ratio is positive. Monthly returns have first-order autocorrelation ρ₁ = 0.2 and no higher autocorrelations. Compared with multiplying the monthly Sharpe ratio by √12, the correct annual Sharpe ratio (Lo, 2002) is…",
                "options": [
                    "identical, because √12 is exact for any return process",
                    "larger, because autocorrelation adds return",
                    "smaller, because positive autocorrelation raises the annual variance",
                    "undefined, because Sharpe ratios cannot be annualised"
                ],
                "correctExplanation": "SR(q) = η(q)·SR with η(q) = q/√(q + 2Σ(q−k)ρ_k); with ρ₁ = 0.2, η(12) = 12/√(12 + 4.4) = 2.96 < √12 = 3.46.",
                "incorrectExplanation": "The √12 rule assumes serially uncorrelated returns; positive autocorrelation makes annual variance grow faster than 12 times the monthly one, while the mean still scales by 12."
            },
            "ro": {
                "title": "Anualizarea raportului Sharpe",
                "text": "Raportul Sharpe lunar este pozitiv. Randamentele lunare au autocorelația de ordinul întîi ρ₁ = 0,2 și nicio altă autocorelație. Față de înmulțirea raportului Sharpe lunar cu √12, raportul Sharpe anual corect (Lo, 2002) este…",
                "options": [
                    "identic, pentru că √12 este exact pentru orice proces",
                    "mai mare, pentru că autocorelația adaugă randament",
                    "mai mic, pentru că autocorelația pozitivă mărește varianța anuală",
                    "nedefinit, pentru că rapoartele Sharpe nu se pot anualiza"
                ],
                "correctExplanation": "SR(q) = η(q)·SR, cu η(q) = q/√(q + 2Σ(q−k)ρ_k); cu ρ₁ = 0,2, η(12) = 12/√(12 + 4,4) = 2,96 < √12 = 3,46.",
                "incorrectExplanation": "Regula √12 presupune randamente necorelate serial; autocorelația pozitivă face varianța anuală să crească mai repede decît de 12 ori varianța lunară, în timp ce media crește tot de 12 ori."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Transaction costs",
                "text": "On the 16-ETF universe, below roughly which cost per unit of turnover did long-only MV keep its edge over 1/N?",
                "options": [
                    "2 bp",
                    "About 22 bp",
                    "About 100 bp",
                    "At any cost"
                ],
                "correctExplanation": "MV-LO trades about 0.20 of wealth a month against 0.025 for 1/N, so its small gross edge (0.81 vs 0.76) vanishes at about 22 bp.",
                "incorrectExplanation": "High turnover erodes a small gross advantage quickly."
            },
            "ro": {
                "title": "Costurile de tranzacționare",
                "text": "În universul cu 16 ETF-uri, sub ce cost aproximativ pe unitatea de turnover și-a păstrat MV long-only (MV-LO) avantajul față de 1/N?",
                "options": [
                    "2 bp",
                    "Circa 22 bp",
                    "Circa 100 bp",
                    "La orice cost"
                ],
                "correctExplanation": "MV-LO tranzacționează circa 0,20 din avere pe lună față de 0,025 pentru 1/N, deci micul avantaj brut (0,81 față de 0,76) dispare la circa 22 bp.",
                "incorrectExplanation": "Turnover-ul mare erodează rapid un avantaj brut mic."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Low risk, low Sharpe",
                "text": "On the multi-asset set (2012–2026), GMV rules had the lowest volatility but also low Sharpe ratios. Why?",
                "options": [
                    "They held mostly equities",
                    "Their turnover was zero",
                    "They loaded on Treasuries, whose excess returns were slightly negative after 2012",
                    "They used sample means"
                ],
                "correctExplanation": "GMV minimises risk, not risk per unit of return: IEF and TLT dominated the weights while their excess returns were −0.2% and −0.5% a year.",
                "incorrectExplanation": "GMV ignores expected returns by design, so it can end up in low-return assets."
            },
            "ro": {
                "title": "Risc mic, Sharpe mic",
                "text": "Pe setul multi-active (2012–2026), regulile GMV au avut cea mai mică volatilitate, dar și rapoarte Sharpe mici. De ce?",
                "options": [
                    "Au deținut mai ales acțiuni",
                    "Turnover-ul lor a fost zero",
                    "Au pus ponderi mari pe titlurile de stat, ale căror randamente în exces au fost ușor negative după 2012",
                    "Au folosit medii de selecție"
                ],
                "correctExplanation": "GMV minimizează riscul, nu riscul pe unitatea de randament: IEF și TLT au dominat ponderile, iar randamentele lor în exces au fost −0,2% și −0,5% pe an.",
                "incorrectExplanation": "GMV ignoră prin construcție randamentele așteptate, deci poate ajunge în active cu randament mic."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the error: an AI backtest",
                "text": "An AI assistant writes: \"I estimate the covariance matrix once on the full 2000-2026 sample, compute the GMV weights, rebalance monthly to them and report an out-of-sample Sharpe ratio of 0.9, annualised with sqrt(12).\" What is the error?",
                "options": [
                    "Monthly Sharpe ratios must be annualised with sqrt(252), not sqrt(12)",
                    "The weights use data from the months being evaluated (look-ahead bias), so the Sharpe ratio is in sample, not out of sample",
                    "GMV weights are proportional to the inverse covariance matrix times expected returns, not times a vector of ones",
                    "GMV weights cannot be rebalanced monthly because they do not sum to one"
                ],
                "correctExplanation": "Out of sample means that the weights of month t use only data up to month t-1, e.g. a rolling 60-month window. A covariance matrix from the full sample leaks future information; sqrt(12) is the right factor for serially uncorrelated monthly returns.",
                "incorrectExplanation": "The annualisation with sqrt(12) (serially uncorrelated monthly returns) and the GMV formula are correct; the problem is that the covariance matrix already contains the evaluation months (look-ahead bias)."
            },
            "ro": {
                "title": "Găsiți eroarea: un backtest scris de AI",
                "text": "Un asistent AI scrie: „Estimez matricea de covarianță o singură dată pe tot eșantionul 2000-2026, calculez ponderile GMV, reechilibrez lunar la ele și raportez un raport Sharpe în afara eșantionului de 0,9, anualizat cu sqrt(12).” Care este eroarea?",
                "options": [
                    "Rapoartele Sharpe lunare se anualizează cu sqrt(252), nu cu sqrt(12)",
                    "Ponderile folosesc date din lunile evaluate (look-ahead bias), deci raportul Sharpe este în eșantion, nu în afara eșantionului",
                    "Ponderile GMV sînt proporționale cu inversa matricei de covarianță înmulțită cu randamentele așteptate, nu cu un vector de unu",
                    "Ponderile GMV nu pot fi reechilibrate lunar, deoarece nu însumează unu"
                ],
                "correctExplanation": "În afara eșantionului înseamnă că ponderile lunii t folosesc doar date pînă în luna t-1, de exemplu o fereastră mobilă de 60 de luni. O matrice de covarianță din tot eșantionul introduce look-ahead bias; sqrt(12) este factorul corect pentru randamente lunare necorelate serial.",
                "incorrectExplanation": "Anualizarea cu sqrt(12) (randamente lunare necorelate serial) și formula GMV sînt corecte; problema este că matricea de covarianță conține deja lunile evaluate (look-ahead bias)."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the error: risk contributions",
                "text": "An AI assistant writes: \"The risk contribution of asset i is RC_i = w_i sigma_i / sigma_p, so in a 60/40 stock-bond portfolio the stocks carry about 60% of the risk.\" What is the error?",
                "options": [
                    "Risk contributions must be computed from expected returns, not volatilities",
                    "The risk contributions of a portfolio never sum to its volatility",
                    "In a 60/40 portfolio the bonds carry most of the risk",
                    "The formula ignores correlations: RC_i = w_i (Sigma w)_i / sigma_p, and with it the stocks carry far more than 60% of the risk"
                ],
                "correctExplanation": "Euler risk contributions use the marginal risk (Sigma w)_i / sigma_p, which includes covariances; they sum to sigma_p. Because stocks are much more volatile than bonds, they typically carry 90% or more of the risk of a 60/40 portfolio.",
                "incorrectExplanation": "The contributions do sum to the portfolio volatility, but only with RC_i = w_i (Sigma w)_i / sigma_p; with this formula the more volatile stocks carry far more than their 60% money weight."
            },
            "ro": {
                "title": "Găsiți eroarea: contribuțiile la risc",
                "text": "Un asistent AI scrie: „Contribuția la risc a activului i este RC_i = w_i sigma_i / sigma_p, deci într-un portofoliu 60/40 acțiuni-obligațiuni acțiunile poartă circa 60% din risc.” Care este eroarea?",
                "options": [
                    "Contribuțiile la risc se calculează din randamentele așteptate, nu din volatilități",
                    "Contribuțiile la risc ale unui portofoliu nu însumează niciodată volatilitatea lui",
                    "Într-un portofoliu 60/40 obligațiunile poartă cea mai mare parte a riscului",
                    "Formula ignoră corelațiile: RC_i = w_i (Sigma w)_i / sigma_p, iar cu ea acțiunile poartă mult mai mult de 60% din risc"
                ],
                "correctExplanation": "Contribuțiile Euler folosesc riscul marginal (Sigma w)_i / sigma_p, care include covarianțele; ele însumează sigma_p. Deoarece acțiunile sînt mult mai volatile decît obligațiunile, ele poartă de regulă 90% sau mai mult din riscul unui portofoliu 60/40.",
                "incorrectExplanation": "Contribuțiile însumează într-adevăr volatilitatea portofoliului, dar numai cu RC_i = w_i (Sigma w)_i / sigma_p; cu această formulă acțiunile, mai volatile, poartă mult mai mult decît ponderea lor de 60% în capital."
            }
        }
    ]
};

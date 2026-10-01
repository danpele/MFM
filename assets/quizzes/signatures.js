// ============================================================
// Quiz bank for chapter id 'signatures': Path Signatures and Realised Volatility (EN + RO)
// Chapter 20 (special chapter): the method of Gu et al. (KDD 2024) transferred to VOLARE realised variance.
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['signatures'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Level 1 of the signature",
                "text": "For a path X from time a to time b, what is level 1 of its signature?",
                "options": [
                    "The total increment X_b - X_a of each channel",
                    "The average value of each channel over the window",
                    "The variance of the increments of each channel",
                    "The maximum of each channel over the window"
                ],
                "correctExplanation": "S^i = integral of dX^i = X^i_b - X^i_a: level 1 keeps only the net change of each channel.",
                "incorrectExplanation": "Level 1 is the first iterated integral, which telescopes to the net change; averages, variances and extremes need higher levels or are not signature terms."
            },
            "ro": {
                "title": "Nivelul 1 al semnăturii",
                "text": "Pentru o traiectorie X de la momentul a la momentul b, ce este nivelul 1 al semnăturii ei (semnătura traiectoriei, engl. path signature)?",
                "options": [
                    "Incrementul total X_b - X_a al fiecărui canal",
                    "Valoarea medie a fiecărui canal pe fereastră",
                    "Varianța incrementelor fiecărui canal",
                    "Maximul fiecărui canal pe fereastră"
                ],
                "correctExplanation": "S^i = integrala lui dX^i = X^i_b - X^i_a: nivelul 1 păstrează doar schimbarea netă a fiecărui canal.",
                "incorrectExplanation": "Nivelul 1 este prima integrală iterată, care se reduce la schimbarea netă; mediile, varianțele și extremele cer niveluri superioare sau nu sînt termeni ai semnăturii."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Signature of a linear segment",
                "text": "What is the signature of a straight segment with increment D?",
                "options": [
                    "(1, D, 0, 0, ...), because a straight line has no curvature",
                    "(1, D, D, D, ...)",
                    "The tensor exponential (1, D, D⊗D/2!, D⊗D⊗D/3!, ...)",
                    "It is not defined for a straight line"
                ],
                "correctExplanation": "Along a straight line all iterated integrals factorise: level k equals D⊗...⊗D / k!, the tensor exponential of D.",
                "incorrectExplanation": "Higher levels of a straight segment are not zero: they are the symmetric tensor powers of the increment divided by k!."
            },
            "ro": {
                "title": "Semnătura unui segment liniar",
                "text": "Care este semnătura unui segment drept cu incrementul D?",
                "options": [
                    "(1, D, 0, 0, ...), pentru că o dreaptă nu are curbură",
                    "(1, D, D, D, ...)",
                    "Exponențiala tensorială (1, D, D⊗D/2!, D⊗D⊗D/3!, ...)",
                    "Nu este definită pentru o dreaptă"
                ],
                "correctExplanation": "Pe o dreaptă toate integralele iterate se factorizează: nivelul k este D⊗...⊗D / k!, exponențiala tensorială a lui D.",
                "incorrectExplanation": "Nivelurile superioare ale unui segment drept nu sînt zero: sînt puterile tensoriale simetrice ale incrementului împărțite la k!."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Chen's identity",
                "text": "What does Chen's identity state?",
                "options": [
                    "The signature of a path equals the signature of its time reversal",
                    "The signature of a concatenation X * Y is the tensor product Sig(X) ⊗ Sig(Y)",
                    "Level 2 of the signature is always symmetric",
                    "The signature is invariant to adding a time channel"
                ],
                "correctExplanation": "Chen (1957): Sig(X * Y) = Sig(X) ⊗ Sig(Y); for a piecewise-linear path it gives the whole algorithm: multiply the exponentials of the segments.",
                "incorrectExplanation": "The identity is about concatenation: the signature of a joined path is the tensor product of the two signatures; reversal gives the inverse, not the same signature."
            },
            "ro": {
                "title": "Identitatea lui Chen",
                "text": "Ce afirmă identitatea lui Chen?",
                "options": [
                    "Semnătura unei traiectorii este egală cu semnătura traiectoriei parcurse invers",
                    "Semnătura unei concatenări X * Y este produsul tensorial Sig(X) ⊗ Sig(Y)",
                    "Nivelul 2 al semnăturii este întotdeauna simetric",
                    "Semnătura este invariantă la adăugarea unui canal de timp"
                ],
                "correctExplanation": "Chen (1957): Sig(X * Y) = Sig(X) ⊗ Sig(Y); pentru o traiectorie liniară pe porțiuni dă tot algoritmul: se înmulțesc exponențialele segmentelor.",
                "incorrectExplanation": "Identitatea se referă la concatenare: semnătura traiectoriei concatenate este produsul tensorial al celor două semnături; inversarea dă inversa, nu aceeași semnătură."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "The Lévy area",
                "text": "For a two-channel path, what is the Lévy area A^{12} = (S^{12} - S^{21})/2?",
                "options": [
                    "The product of the two total increments",
                    "The quadratic variation of the first channel",
                    "The correlation of the two channels",
                    "The signed area enclosed between the path and the chord joining its end points"
                ],
                "correctExplanation": "The antisymmetric part of level 2 is the signed area between the path and its chord: it records which channel moved first.",
                "incorrectExplanation": "The symmetric part of level 2 is half the product of the increments; the antisymmetric part, the Lévy area, measures the order of the moves as a signed area."
            },
            "ro": {
                "title": "Aria Lévy",
                "text": "Pentru o traiectorie cu două canale, ce este aria Lévy A^{12} = (S^{12} - S^{21})/2?",
                "options": [
                    "Produsul celor două incremente totale",
                    "Variația pătratică a primului canal",
                    "Corelația celor două canale",
                    "Aria cu semn închisă între traiectorie și coarda care îi unește capetele"
                ],
                "correctExplanation": "Partea antisimetrică a nivelului 2 este aria cu semn dintre traiectorie și coarda ei: înregistrează care canal s-a mișcat primul.",
                "incorrectExplanation": "Partea simetrică a nivelului 2 este jumătate din produsul incrementelor; partea antisimetrică, aria Lévy, măsoară ordinea mișcărilor ca arie cu semn."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "The shuffle identity",
                "text": "Which relation between signature terms follows from the shuffle identity?",
                "options": [
                    "S^i S^j = S^{ij} + S^{ji}",
                    "S^i S^j = S^{ij} S^{ji}",
                    "S^{ij} = S^{ji} for every path",
                    "S^i S^j = 0 for i ≠ j"
                ],
                "correctExplanation": "Products of signature terms are linear combinations of higher terms; hence a linear model in the signature already contains polynomials of the increments.",
                "incorrectExplanation": "The shuffle product turns a product of two terms into a sum over interleavings of their words; S^{ij} and S^{ji} differ in general (their difference is twice the Lévy area)."
            },
            "ro": {
                "title": "Identitatea shuffle",
                "text": "Ce relație între termenii semnăturii rezultă din identitatea shuffle?",
                "options": [
                    "S^i S^j = S^{ij} + S^{ji}",
                    "S^i S^j = S^{ij} S^{ji}",
                    "S^{ij} = S^{ji} pentru orice traiectorie",
                    "S^i S^j = 0 pentru i ≠ j"
                ],
                "correctExplanation": "Produsele termenilor semnăturii sînt combinații liniare de termeni superiori; de aceea un model liniar în semnătură conține deja polinoame în incremente.",
                "incorrectExplanation": "Produsul shuffle transformă produsul a doi termeni într-o sumă pe intercalările cuvintelor lor; S^{ij} și S^{ji} diferă în general (diferența lor este de două ori aria Lévy)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Why time augmentation",
                "text": "Why is a strictly increasing time channel added to the path before computing signatures?",
                "options": [
                    "It makes the signature invariant to the speed of the path",
                    "It reduces the number of signature terms",
                    "It makes the full signature determine the path up to its starting point and lets it see when moves happened",
                    "It removes the need for a truncation depth"
                ],
                "correctExplanation": "Without time the signature is invariant to reparametrisation and to tree-like pieces; a strictly increasing channel removes both, so the full signature determines the path up to translation (Hambly and Lyons, 2010). The starting point must be fixed or supplied separately, and a finite truncation does not determine the path.",
                "incorrectExplanation": "Time augmentation adds terms rather than removing them, and it breaks, not creates, invariance to speed; truncation is still needed."
            },
            "ro": {
                "title": "De ce augmentăm cu timpul",
                "text": "De ce se adaugă traiectoriei un canal de timp strict crescător înainte de calculul semnăturilor?",
                "options": [
                    "Face semnătura invariantă la viteza de parcurgere a traiectoriei",
                    "Reduce numărul de termeni ai semnăturii",
                    "Face ca întreaga semnătură să determine traiectoria pînă la punctul de start și să vadă cînd au avut loc mișcările",
                    "Elimină nevoia unei adîncimi de trunchiere"
                ],
                "correctExplanation": "Fără timp, semnătura este invariantă la reparametrizare și la bucățile de tip arbore; un canal strict crescător le elimină pe amîndouă, deci întreaga semnătură determină traiectoria pînă la o translație (Hambly și Lyons, 2010). Punctul de start trebuie fixat sau furnizat separat, iar o trunchiere finită nu determină traiectoria.",
                "incorrectExplanation": "Augmentarea cu timpul adaugă termeni, nu îi reduce, și elimină, nu creează, invarianța la viteză; trunchierea rămîne necesară."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Truncation dimension",
                "text": "A path with d = 3 channels is truncated at depth N = 3. How many signature terms (levels 1 to 3) are there?",
                "options": [
                    "9",
                    "39",
                    "27",
                    "12"
                ],
                "correctExplanation": "d + d^2 + d^3 = 3 + 9 + 27 = 39; the number grows as d^N, which is why sparsity (LASSO) is needed.",
                "incorrectExplanation": "Count every word of length 1, 2 and 3 over 3 letters: 3 + 9 + 27."
            },
            "ro": {
                "title": "Dimensiunea trunchierii",
                "text": "O traiectorie cu d = 3 canale este trunchiată la adîncimea N = 3. Cîți termeni are semnătura (nivelurile 1-3)?",
                "options": [
                    "9",
                    "39",
                    "27",
                    "12"
                ],
                "correctExplanation": "d + d^2 + d^3 = 3 + 9 + 27 = 39; numărul crește ca d^N, de aceea este nevoie de o soluție cu puțini coeficienți nenuli (LASSO).",
                "incorrectExplanation": "Numărați toate cuvintele de lungime 1, 2 și 3 peste 3 litere: 3 + 9 + 27."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Universality of signatures",
                "text": "What does the universal approximation (linearisation) property of signatures say?",
                "options": [
                    "Every path has a finite signature",
                    "The signature of a path is always sparse",
                    "Signatures are independent of the path",
                    "On a compact set of time-augmented paths with a common starting point, any continuous function is approximated uniformly by a linear functional of the signature"
                ],
                "correctExplanation": "By Stone-Weierstrass and the shuffle identity, linear functionals of the signature are dense in the continuous functions on compact sets of time-augmented paths with a common starting point; without it, (t, 0) and (t, 10) have the same signature and their starting level cannot be approximated.",
                "incorrectExplanation": "The property concerns approximation of functions of the path by linear maps of its signature; it says nothing about sparsity or finiteness of the infinite signature."
            },
            "ro": {
                "title": "Universalitatea semnăturilor",
                "text": "Ce afirmă proprietatea de aproximare universală (liniarizare) a semnăturilor?",
                "options": [
                    "Orice traiectorie are o semnătură finită",
                    "Semnătura unei traiectorii are întotdeauna puțini termeni nenuli",
                    "Semnăturile nu depind de traiectorie",
                    "Pe o mulțime compactă de traiectorii augmentate cu timpul, cu un punct de start comun, orice funcție continuă este aproximată uniform de o funcțională liniară a semnăturii"
                ],
                "correctExplanation": "Prin Stone-Weierstrass și identitatea shuffle, funcționalele liniare ale semnăturii sînt dense în funcțiile continue pe mulțimi compacte de traiectorii augmentate cu timpul, cu un punct de start comun; fără el, (t, 0) și (t, 10) au aceeași semnătură, iar nivelul lor de start nu poate fi aproximat.",
                "incorrectExplanation": "Proprietatea se referă la aproximarea funcțiilor traiectoriei prin aplicații liniare ale semnăturii; nu spune nimic despre numărul termenilor nenuli sau despre finitudinea semnăturii infinite."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Translation invariance",
                "text": "The signature satisfies Sig(X + c) = Sig(X). What is the consequence for volatility forecasting?",
                "options": [
                    "The signature does not see the level of volatility, so the level must enter through other regressors such as the log-HAR terms",
                    "The signature over-weights high-volatility days",
                    "The signature must be computed on returns only",
                    "Log RV cannot be used as a channel"
                ],
                "correctExplanation": "Only increments enter the signature; the lecture adds log RV_t and its weekly and monthly averages, as Gu et al. add external factors x_tau.",
                "incorrectExplanation": "Translation invariance removes the level entirely; it does not favour high levels, and log RV can be a channel as long as its level is supplied separately."
            },
            "ro": {
                "title": "Invarianța la translație",
                "text": "Semnătura satisface Sig(X + c) = Sig(X). Care este consecința pentru prognoza volatilității?",
                "options": [
                    "Semnătura nu vede nivelul volatilității, deci nivelul trebuie să intre prin alți regresori, de exemplu termenii log-HAR",
                    "Semnătura supraponderează zilele cu volatilitate mare",
                    "Semnătura trebuie calculată doar pe randamente",
                    "Log RV nu poate fi folosit ca un canal"
                ],
                "correctExplanation": "Doar incrementele intră în semnătură; cursul adaugă log RV_t și mediile lui săptămînale și lunare, așa cum Gu et al. adaugă factorii externi x_tau.",
                "incorrectExplanation": "Invarianța la translație elimină complet nivelul; nu favorizează nivelurile mari, iar log RV poate fi un canal atît timp cît nivelul lui este furnizat separat."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The truncated signature kernel",
                "text": "Gu et al. define the signature kernel k(a, b) = <Sig^N(a), Sig^N(b)>. Which distance do they use for the weights?",
                "options": [
                    "The Euclidean distance between the two raw windows",
                    "The correlation between the two windows",
                    "d(a, b) = k(a, a) - 2k(a, b) + k(b, b) = ||Sig^N(a) - Sig^N(b)||^2",
                    "The dynamic time warping distance"
                ],
                "correctExplanation": "The kernel-induced squared distance equals the squared Euclidean distance between truncated signatures (Eq. 9 of the paper).",
                "incorrectExplanation": "The distance is built from the kernel itself: k(a,a) - 2k(a,b) + k(b,b), which is the squared norm of the difference of the feature maps."
            },
            "ro": {
                "title": "Nucleul de semnătură trunchiat",
                "text": "Gu et al. definesc nucleul de semnătură k(a, b) = <Sig^N(a), Sig^N(b)>. Ce distanță folosesc pentru ponderi?",
                "options": [
                    "Distanța euclidiană dintre cele două ferestre brute",
                    "Corelația dintre cele două ferestre",
                    "d(a, b) = k(a, a) - 2k(a, b) + k(b, b) = ||Sig^N(a) - Sig^N(b)||^2",
                    "Distanța dynamic time warping"
                ],
                "correctExplanation": "Distanța pătratică indusă de nucleu este distanța euclidiană pătratică dintre semnăturile trunchiate (ec. 9 din articol).",
                "incorrectExplanation": "Distanța se construiește din nucleu: k(a,a) - 2k(a,b) + k(b,b), adică norma pătratică a diferenței aplicațiilor de trăsături."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Kernel weights at zero temperature",
                "text": "With weights w_tau proportional to exp(-gamma d_tau), what happens as gamma goes to 0?",
                "options": [
                    "All weight goes to the most similar past window",
                    "The weights become equal and the regression is the ordinary one",
                    "The weights become proportional to d_tau",
                    "The regression is no longer identified"
                ],
                "correctExplanation": "exp(-gamma d) tends to 1 for every window, so w = 1/n: the kernel-weighted model collapses to its equal-weight version (Sig-L).",
                "incorrectExplanation": "The limit gamma to infinity concentrates the weight on the nearest window; gamma to 0 flattens the weights."
            },
            "ro": {
                "title": "Ponderile nucleului la temperatura zero",
                "text": "Cu ponderi w_tau proporționale cu exp(-gamma d_tau), ce se întîmplă cînd gamma tinde la 0?",
                "options": [
                    "Toată ponderea merge la fereastra trecută cea mai asemănătoare",
                    "Ponderile devin egale, iar regresia este cea obișnuită",
                    "Ponderile devin proporționale cu d_tau",
                    "Regresia nu mai este identificată"
                ],
                "correctExplanation": "exp(-gamma d) tinde la 1 pentru fiecare fereastră, deci w = 1/n: modelul cu ponderi de nucleu devine versiunea cu ponderi egale (Sig-L).",
                "incorrectExplanation": "Limita gamma la infinit concentrează ponderea pe fereastra cea mai apropiată; gamma la 0 face ponderile egale."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Effective sample size",
                "text": "Weights w_1, ..., w_n sum to one. What is the Kish effective sample size?",
                "options": [
                    "n times the largest weight",
                    "The number of non-zero weights",
                    "The sum of the weights squared",
                    "1 / sum of w_tau^2"
                ],
                "correctExplanation": "n_eff = 1 / sum w^2 equals n for equal weights and 1 when all weight sits on one observation.",
                "incorrectExplanation": "The Kish formula uses the sum of squared weights; with equal weights 1/n it returns n."
            },
            "ro": {
                "title": "Mărimea efectivă a eșantionului",
                "text": "Ponderile w_1, ..., w_n au suma unu. Care este mărimea efectivă Kish a eșantionului?",
                "options": [
                    "n înmulțit cu ponderea maximă",
                    "Numărul ponderilor nenule",
                    "Suma pătratelor ponderilor",
                    "1 / suma lui w_tau^2"
                ],
                "correctExplanation": "n_eff = 1 / suma w^2 este n pentru ponderi egale și 1 cînd toată ponderea stă pe o singură observație.",
                "incorrectExplanation": "Formula Kish folosește suma pătratelor ponderilor; cu ponderi egale 1/n dă n."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Two-step LASSO",
                "text": "Why do Gu et al. refit the model by OLS on the support selected by the LASSO?",
                "options": [
                    "The LASSO shrinks the kept coefficients towards zero; OLS on the support removes this bias",
                    "OLS selects more variables than the LASSO",
                    "The LASSO cannot use weights",
                    "OLS makes the model robust to heavy tails"
                ],
                "correctExplanation": "Least squares after selection (Belloni and Chernozhukov, 2013) keeps the sparsity of the LASSO but not its shrinkage bias.",
                "incorrectExplanation": "The refit is restricted to the selected support, so it adds no variables; weights can be used in both steps."
            },
            "ro": {
                "title": "LASSO în doi pași",
                "text": "De ce reestimează Gu et al. modelul prin OLS pe suportul selectat de LASSO?",
                "options": [
                    "LASSO aplică shrinkage spre zero coeficienților păstrați; OLS pe suport elimină această deplasare",
                    "OLS selectează mai multe variabile decît LASSO",
                    "LASSO nu poate folosi ponderi",
                    "OLS face modelul robust la cozi groase"
                ],
                "correctExplanation": "Cele mai mici pătrate după selecție (Belloni și Chernozhukov, 2013) păstrează selecția făcută de LASSO, dar nu și biasul lui de shrinkage.",
                "incorrectExplanation": "Reestimarea este restrînsă la suportul selectat, deci nu adaugă variabile; ponderile pot fi folosite în ambii pași."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Choosing lambda without look-ahead",
                "text": "In a rolling forecasting study, which choice of the LASSO penalty avoids look-ahead bias?",
                "options": [
                    "Cross-validation on the full sample, once, before the rolling loop",
                    "The lambda that minimises the out-of-sample QLIKE",
                    "A criterion such as BIC, or time-ordered validation, computed inside each training window",
                    "The largest lambda that keeps all HAR terms on a LASSO path fitted using the entire sample, including the evaluation period"
                ],
                "correctExplanation": "Any tuning must use only data available at the forecast origin; the lecture chooses lambda by BIC inside every 1000-day window.",
                "incorrectExplanation": "Tuning on the full sample or on the evaluation losses uses future information and flatters the model."
            },
            "ro": {
                "title": "Alegerea lui lambda fără look-ahead bias",
                "text": "Într-un studiu de prognoză pe fereastră mobilă, ce alegere a penalizării LASSO evită look-ahead bias?",
                "options": [
                    "Validare încrucișată pe tot eșantionul, o dată, înaintea buclei mobile",
                    "Lambda care minimizează QLIKE în afara eșantionului",
                    "Un criteriu precum BIC sau o validare ordonată în timp, calculate în fiecare fereastră de antrenare",
                    "Cel mai mare lambda care păstrează toți termenii HAR pe o traiectorie LASSO estimată folosind întregul eșantion, inclusiv perioada de evaluare"
                ],
                "correctExplanation": "Orice calibrare trebuie să folosească doar datele disponibile la originea prognozei; cursul alege lambda prin BIC în fiecare fereastră de 1000 de zile.",
                "incorrectExplanation": "Calibrarea pe tot eșantionul sau pe pierderile de evaluare introduce look-ahead bias și avantajează nejustificat modelul."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "HAR as a restricted AR(22)",
                "text": "How many linear restrictions does the HAR model impose on the 22 slope coefficients of an AR(22)?",
                "options": [
                    "3",
                    "19",
                    "22",
                    "5"
                ],
                "correctExplanation": "Three free slopes generate 22 lag coefficients: phi_2 = ... = phi_5 (3 restrictions) and phi_6 = ... = phi_22 (16 restrictions).",
                "incorrectExplanation": "Count the equalities: 22 coefficients, 3 free parameters, so 22 - 3 restrictions."
            },
            "ro": {
                "title": "HAR ca AR(22) restricționat",
                "text": "Cîte restricții liniare impune modelul HAR asupra celor 22 de coeficienți de pantă ai unui AR(22)?",
                "options": [
                    "3",
                    "19",
                    "22",
                    "5"
                ],
                "correctExplanation": "Trei pante libere generează 22 de coeficienți: phi_2 = ... = phi_5 (3 restricții) și phi_6 = ... = phi_22 (16 restricții).",
                "incorrectExplanation": "Numărați egalitățile: 22 de coeficienți, 3 parametri liberi, deci 22 - 3 restricții."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "The HARQ coefficient",
                "text": "In HARQ the daily coefficient is beta_d + beta_Q (RQ_t^{1/2} - mean). What does beta_Q < 0 mean?",
                "options": [
                    "Volatile days get more weight in the forecast",
                    "Quarticity is not informative",
                    "The model is misspecified",
                    "On days when RV is measured less precisely (high quarticity), the forecast relies less on that day's RV"
                ],
                "correctExplanation": "RV is a noisy estimate with error variance proportional to the quarticity; a negative beta_Q corrects the attenuation on noisy days (Bollerslev, Patton and Quaedvlieg, 2016).",
                "incorrectExplanation": "The interaction lowers the effective daily coefficient when measurement error is large; it is the expected sign, not a sign of misspecification."
            },
            "ro": {
                "title": "Coeficientul HARQ",
                "text": "În HARQ, coeficientul zilnic este beta_d + beta_Q (RQ_t^{1/2} - media). Ce înseamnă beta_Q < 0?",
                "options": [
                    "Zilele volatile primesc o pondere mai mare în prognoză",
                    "Cvarticitatea nu este informativă",
                    "Modelul este greșit specificat",
                    "În zilele în care RV este măsurată mai imprecis (cvarticitate mare), prognoza se bazează mai puțin pe RV din acea zi"
                ],
                "correctExplanation": "RV este o estimare zgomotoasă, cu varianța erorii proporțională cu cvarticitatea; un beta_Q negativ corectează atenuarea din zilele zgomotoase (Bollerslev, Patton și Quaedvlieg, 2016).",
                "incorrectExplanation": "Interacțiunea scade coeficientul zilnic efectiv cînd eroarea de măsurare este mare; este semnul așteptat, nu un semn de specificare greșită."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Semivariances in SHAR",
                "text": "Patton and Sheppard (2015) find beta^- > beta^+ in SHAR. What does it mean?",
                "options": [
                    "Variance from negative intraday returns is more persistent than variance from positive ones",
                    "Positive returns are more volatile",
                    "Semivariances do not add up to RV",
                    "The HAR model should use only positive returns"
                ],
                "correctExplanation": "Bad volatility predicts future volatility more strongly: an intraday version of the leverage effect.",
                "incorrectExplanation": "RV+ and RV- add up to RV; the finding is about their different persistence, with the negative part more persistent."
            },
            "ro": {
                "title": "Semivarianțele în SHAR",
                "text": "Patton și Sheppard (2015) găsesc beta^- > beta^+ în SHAR. Ce înseamnă?",
                "options": [
                    "Varianța din randamentele intraday negative este mai persistentă decît cea din randamentele pozitive",
                    "Randamentele pozitive sînt mai volatile",
                    "Semivarianțele nu se adună la RV",
                    "Modelul HAR ar trebui să folosească doar randamentele pozitive"
                ],
                "correctExplanation": "Volatilitatea rea prezice mai puternic volatilitatea viitoare: o versiune intraday a efectului de levier.",
                "incorrectExplanation": "RV+ și RV- se adună la RV; rezultatul se referă la persistența lor diferită, partea negativă fiind mai persistentă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The minimiser of QLIKE",
                "text": "QLIKE(RV, F) = RV/F - ln(RV/F) - 1. Which forecast minimises its conditional expectation?",
                "options": [
                    "The conditional median of RV",
                    "The harmonic mean 1/E[1/RV]",
                    "The conditional mean E[RV]",
                    "The conditional mode of RV"
                ],
                "correctExplanation": "Setting the derivative -E[RV]/F^2 + 1/F to zero gives F = E[RV]; with a proxy that is conditionally unbiased given the forecasters' information, the expected-loss ranking is the same as with the true variance (Patton, 2011).",
                "incorrectExplanation": "The harmonic mean minimises QLIKE with swapped arguments; the correct QLIKE is minimised by the conditional mean."
            },
            "ro": {
                "title": "Minimizantul QLIKE",
                "text": "QLIKE(RV, F) = RV/F - ln(RV/F) - 1. Ce prognoză minimizează speranța ei condiționată?",
                "options": [
                    "Mediana condiționată a RV",
                    "Media armonică 1/E[1/RV]",
                    "Media condiționată E[RV]",
                    "Modul condiționat al RV"
                ],
                "correctExplanation": "Anulînd derivata -E[RV]/F^2 + 1/F obținem F = E[RV]; cu o aproximare condiționat nedeplasată față de informația prognozelor, ordinea pierderilor așteptate este aceeași ca cu varianța adevărată (Patton, 2011).",
                "incorrectExplanation": "Media armonică minimizează QLIKE cu argumentele inversate; QLIKE corectă este minimizată de media condiționată."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Asymmetry of QLIKE",
                "text": "With RV = 1, compare QLIKE for the forecasts F = 0.5 and F = 1.5.",
                "options": [
                    "Both give the same loss, like MSE",
                    "F = 0.5 gives about 0.31, F = 1.5 about 0.07: under-prediction is penalised more",
                    "F = 1.5 gives the larger loss",
                    "Both losses are negative"
                ],
                "correctExplanation": "QLIKE(1, 0.5) = 2 - ln 2 - 1 = 0.307 and QLIKE(1, 1.5) = 0.667 + ln 1.5 - 1 = 0.072: under-predicting variance costs about four times more.",
                "incorrectExplanation": "QLIKE is non-negative and asymmetric; MSE would give 0.25 in both cases."
            },
            "ro": {
                "title": "Asimetria QLIKE",
                "text": "Cu RV = 1, comparați QLIKE pentru prognozele F = 0,5 și F = 1,5.",
                "options": [
                    "Ambele dau aceeași pierdere, ca MSE",
                    "F = 0,5 dă aproximativ 0,31, F = 1,5 aproximativ 0,07: subestimarea este penalizată mai mult",
                    "F = 1,5 dă pierderea mai mare",
                    "Ambele pierderi sînt negative"
                ],
                "correctExplanation": "QLIKE(1; 0,5) = 2 - ln 2 - 1 = 0,307 și QLIKE(1; 1,5) = 0,667 + ln 1,5 - 1 = 0,072: subestimarea varianței costă de aproximativ patru ori mai mult.",
                "incorrectExplanation": "QLIKE este nenegativă și asimetrică; MSE ar da 0,25 în ambele cazuri."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "DM test at longer horizons",
                "text": "Why does a Diebold-Mariano test for 22-day-ahead forecasts of average RV need a HAC variance?",
                "options": [
                    "Because QLIKE is not symmetric",
                    "Because the forecasts are in logs",
                    "Because the loss differential is always normally distributed",
                    "Because consecutive targets overlap, so loss differentials are autocorrelated even under the null"
                ],
                "correctExplanation": "Targets RV_{t+1:t+22} and RV_{t+2:t+23} share 21 days, which induces serial dependence through lag h - 1 = 21, and persistent RV can extend it further; a HAC (Newey-West) variance with a justified bandwidth, here at least h, and sensitivity checks are needed.",
                "incorrectExplanation": "The need for HAC comes from overlapping targets and serial correlation, not from the shape of the loss or the log transform."
            },
            "ro": {
                "title": "Testul DM la orizonturi lungi",
                "text": "De ce are nevoie un test Diebold-Mariano pentru prognoze pe 22 de zile ale RV medii de o varianță HAC?",
                "options": [
                    "Pentru că QLIKE nu este simetrică",
                    "Pentru că prognozele sînt în logaritmi",
                    "Pentru că diferența de pierdere are mereu distribuția Normală",
                    "Pentru că țintele consecutive se suprapun, deci diferențele de pierdere sînt autocorelate chiar sub ipoteza nulă"
                ],
                "correctExplanation": "Țintele RV_{t+1:t+22} și RV_{t+2:t+23} au 21 de zile în comun, ceea ce induce dependență serială pînă la lagul h - 1 = 21, iar RV persistentă o poate prelungi; este nevoie de o varianță HAC (Newey-West) cu o lățime de bandă justificată, aici cel puțin h, și de verificări de sensibilitate.",
                "incorrectExplanation": "Nevoia de HAC vine din țintele suprapuse și din autocorelație, nu din forma funcției de pierdere sau din transformarea logaritmică."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Holm versus BH",
                "text": "Over 50 assets, one DM test each, with valid p-values that are independent or positively dependent (PRDS): what do the Holm and Benjamini-Hochberg corrections control?",
                "options": [
                    "Holm: the probability of at least one false win (FWER); BH: the expected share of false wins among the declared wins (FDR)",
                    "Both control the FWER",
                    "Holm controls the FDR and BH the FWER",
                    "Both control the power of the tests"
                ],
                "correctExplanation": "Holm is a step-down FWER procedure valid under any dependence; BH is a step-up FDR procedure, valid under independence or PRDS (Benjamini and Yekutieli, 2001, give a version for arbitrary dependence), and it rejects at least as often as Holm.",
                "incorrectExplanation": "FWER and FDR are different error rates; neither correction controls power."
            },
            "ro": {
                "title": "Holm versus BH",
                "text": "Pe 50 de active, cîte un test DM pentru fiecare, cu valori p valide, independente sau pozitiv dependente (PRDS): ce controlează corecțiile Holm și Benjamini-Hochberg?",
                "options": [
                    "Holm: probabilitatea a cel puțin unei victorii false (FWER); BH: proporția așteptată de victorii false printre cele declarate (FDR)",
                    "Ambele controlează FWER",
                    "Holm controlează FDR, iar BH controlează FWER",
                    "Ambele controlează puterea testelor"
                ],
                "correctExplanation": "Holm este o procedură descendentă de control al FWER, validă sub orice dependență; BH este o procedură ascendentă de control al FDR, validă sub independență sau PRDS (Benjamini și Yekutieli, 2001, dau o variantă pentru dependență arbitrară), și respinge cel puțin la fel de des ca Holm.",
                "incorrectExplanation": "FWER și FDR sînt rate de eroare diferite; niciuna dintre corecții nu controlează puterea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Model confidence set",
                "text": "What is a 90% model confidence set (Hansen, Lunde and Nason, 2011)?",
                "options": [
                    "The set of models whose losses are below the median",
                    "The single best model with 90% probability",
                    "A set of models that contains the best model(s) with probability at least 90%",
                    "The 90% most accurate forecasts of each model"
                ],
                "correctExplanation": "The MCS eliminates models sequentially by equivalence tests; the surviving set contains the best models with the chosen confidence, and it is large when the data cannot separate them.",
                "incorrectExplanation": "The MCS is a set, not a single model; its size reflects how informative the data are about differences in loss."
            },
            "ro": {
                "title": "Mulțimea de încredere a modelelor",
                "text": "Ce este o mulțime de încredere a modelelor de 90% (Hansen, Lunde și Nason, 2011)?",
                "options": [
                    "Mulțimea modelelor cu pierderi sub mediană",
                    "Singurul cel mai bun model cu probabilitatea 90%",
                    "O mulțime de modele care conține cel(e) mai bun(e) model(e) cu probabilitatea de cel puțin 90%",
                    "Cele mai precise 90% dintre prognozele fiecărui model"
                ],
                "correctExplanation": "MCS elimină modelele secvențial prin teste de echivalență; mulțimea rămasă conține cele mai bune modele cu încrederea aleasă și este mare cînd datele nu le pot separa.",
                "incorrectExplanation": "MCS este o mulțime, nu un singur model; mărimea ei arată cît de informative sînt datele despre diferențele de pierdere."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "The main result of the case study",
                "text": "On 50 VOLARE assets, one day ahead, how did the signature LASSO with kernel weights (Sig-LK) compare with log-HAR?",
                "options": [
                    "It beat log-HAR on most assets after the Holm correction",
                    "It did not beat log-HAR: a slightly higher mean QLIKE and no significant win after correction",
                    "It lost to HAR in levels on every asset",
                    "It reproduced the fivefold gain reported by Gu et al."
                ],
                "correctExplanation": "Mean QLIKE relative to log-HAR was about 1.05 at h = 1, pushed up by crude oil, with two raw wins (ES, TSLA) and no Holm-significant win out of 50; at 5 and 22 days the signature models were worse.",
                "incorrectExplanation": "Beating HAR in levels came from the log target, not from signatures; against log-HAR there was no gain, and nothing close to a fivefold improvement."
            },
            "ro": {
                "title": "Rezultatul principal al studiului de caz",
                "text": "Pe 50 de active VOLARE, la o zi, cum s-a comparat LASSO-ul pe semnături cu ponderi de nucleu (Sig-LK) cu log-HAR?",
                "options": [
                    "A bătut log-HAR pe majoritatea activelor după corecția Holm",
                    "Nu a bătut log-HAR: o QLIKE medie puțin mai mare și nicio victorie semnificativă după corecție",
                    "A pierdut în fața HAR în nivel pe fiecare activ",
                    "A reprodus cîștigul de cinci ori raportat de Gu et al."
                ],
                "correctExplanation": "QLIKE medie relativ la log-HAR a fost aproximativ 1,05 la h = 1, împinsă în sus de petrol, cu două victorii necorectate (ES, TSLA) și nicio victorie semnificativă după Holm din 50; la 5 și 22 de zile modelele cu semnături au fost mai slabe.",
                "incorrectExplanation": "Victoria față de HAR în nivel a venit din ținta logaritmică, nu din semnături; față de log-HAR nu a existat niciun cîștig și nimic apropiat de o îmbunătățire de cinci ori."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Why the kernel weights did not help",
                "text": "In the COVID-19 crash the kernel weights stayed almost flat and even down-weighted past stress windows. What is the main reason?",
                "options": [
                    "The rolling window was too short to contain any stress period",
                    "The kernel was computed with the wrong sign",
                    "The LASSO removed the kernel",
                    "The signature kernel is translation-invariant: it compares the shape of windows, not the level of volatility"
                ],
                "correctExplanation": "A rising window in March 2020 has a different shape from past spike-and-decay windows, whatever their level; the kernel therefore did not single out past crises.",
                "incorrectExplanation": "The training window contained the late-2018 sell-off; the weights enter the LASSO objective and cannot be removed by it."
            },
            "ro": {
                "title": "De ce nu au ajutat ponderile nucleului",
                "text": "În crahul COVID-19, ponderile nucleului au rămas aproape plate și chiar au redus ponderea ferestrelor de stres trecute. Care este motivul principal?",
                "options": [
                    "Fereastra mobilă era prea scurtă pentru a conține vreo perioadă de stres",
                    "Nucleul a fost calculat cu semnul greșit",
                    "LASSO a eliminat nucleul",
                    "Nucleul de semnătură este invariant la translație: compară forma ferestrelor, nu nivelul volatilității"
                ],
                "correctExplanation": "O fereastră în creștere din martie 2020 are altă formă decît ferestrele trecute cu vîrf și scădere, indiferent de nivelul lor; de aceea nucleul nu a evidențiat crizele trecute.",
                "incorrectExplanation": "Fereastra de antrenare conținea scăderile de la sfîrșitul lui 2018; ponderile intră în funcția obiectiv a LASSO și nu pot fi eliminate de ea."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the error in this AI answer: signature features",
                "text": "An AI assistant writes: \"For each day, compute the depth-3 signature of the last 22 values of log RV (a one-dimensional path) and use its three terms as features; the signature captures the shape of the volatility path.\" What is wrong?",
                "options": [
                    "A one-dimensional path has signature (D, D^2/2, D^3/6): only the net change over the window, with no shape or order; the path needs a time channel (and more channels)",
                    "Depth 3 is too high for 22 observations",
                    "Signatures cannot be computed on logs",
                    "Log RV must first be differenced"
                ],
                "correctExplanation": "Without a second channel all iterated integrals are powers of the total increment; time augmentation (and a return channel) is what gives shape and lead-lag information.",
                "incorrectExplanation": "The depth is not the problem: in one dimension every level is a function of the net change, whatever the depth."
            },
            "ro": {
                "title": "Găsiți eroarea din acest răspuns AI: variabilele de semnătură",
                "text": "Un asistent AI scrie: „Pentru fiecare zi, calculați semnătura de adîncime 3 a ultimelor 22 de valori ale log RV (o traiectorie unidimensională) și folosiți cei trei termeni ca trăsături; semnătura surprinde forma traiectoriei volatilității.” Ce este greșit?",
                "options": [
                    "O traiectorie unidimensională are semnătura (D, D^2/2, D^3/6): doar schimbarea netă pe fereastră, fără formă și fără ordine; traiectoria are nevoie de un canal de timp (și de mai multe canale)",
                    "Adîncimea 3 este prea mare pentru 22 de observații",
                    "Semnăturile nu pot fi calculate pe logaritmi",
                    "Log RV trebuie întîi diferențiat"
                ],
                "correctExplanation": "Fără un al doilea canal, toate integralele iterate sînt puteri ale incrementului total; augmentarea cu timpul (și un canal al randamentelor) aduce informația despre formă și despre avans-întîrziere.",
                "incorrectExplanation": "Adîncimea nu este problema: într-o dimensiune, fiecare nivel este o funcție de schimbarea netă, indiferent de adîncime."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the error in this AI answer: evaluation",
                "text": "An AI assistant writes: \"I chose lambda with LassoCV on the whole sample, fitted on the first 70% and computed qlike(forecast, realised) on the last 30%; the signature LASSO has a lower QLIKE than HAR.\" Which pair of errors does the answer contain?",
                "options": [
                    "Using log RV and using 70% for training",
                    "Using the LASSO and using QLIKE instead of MSE",
                    "Lambda is tuned on data that include the test period (look-ahead), and QLIKE is computed with its arguments swapped, which rewards forecasts that are too low",
                    "Using a single split and reporting QLIKE with three decimals"
                ],
                "correctExplanation": "Tuning must use training data only; qlike(F, RV) = F/RV - ln(F/RV) - 1 is minimised by the harmonic mean, not by E[RV]. The claim also lacks a benchmark computation and a DM test.",
                "incorrectExplanation": "The log target, the LASSO and QLIKE are legitimate choices; the errors are the look-ahead in tuning and the swapped loss."
            },
            "ro": {
                "title": "Găsiți eroarea din acest răspuns AI: evaluarea",
                "text": "Un asistent AI scrie: „Am ales lambda cu LassoCV pe tot eșantionul, am estimat pe primele 70% și am calculat qlike(prognoza, realizat) pe ultimele 30%; LASSO-ul pe semnături are o valoare QLIKE mai mică decît HAR.” Ce pereche de erori conține răspunsul?",
                "options": [
                    "Folosirea log RV și folosirea a 70% pentru antrenare",
                    "Folosirea LASSO și a QLIKE în loc de MSE",
                    "Lambda este calibrat pe date care includ perioada de test (look-ahead bias), iar QLIKE este calculată cu argumentele inversate, ceea ce recompensează prognozele prea mici",
                    "Folosirea unei singure împărțiri și raportarea QLIKE cu trei zecimale"
                ],
                "correctExplanation": "Calibrarea trebuie să folosească doar datele de antrenare; qlike(F, RV) = F/RV - ln(F/RV) - 1 este minimizată de media armonică, nu de E[RV]. Afirmației îi lipsesc și calculul reperului și un test DM.",
                "incorrectExplanation": "Ținta logaritmică, LASSO și QLIKE sînt alegeri legitime; erorile sînt look-ahead bias la calibrare și pierderea inversată."
            }
        }
    ]
};

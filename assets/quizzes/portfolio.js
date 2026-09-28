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
            "correct": 1,
            "en": {
                "title": "Global minimum variance",
                "text": "Which inputs does the global minimum-variance (GMV) portfolio need?",
                "options": [
                    "Expected returns only",
                    "The covariance matrix only",
                    "Expected returns and the risk-free rate",
                    "Market capitalisations"
                ],
                "correctExplanation": "w_GMV = Σ⁻¹1 / 1'Σ⁻¹1 uses only the covariance matrix, which is why it is more robust than the tangency portfolio.",
                "incorrectExplanation": "The GMV formula contains no expected returns: only Σ is needed."
            },
            "ro": {
                "title": "Varianța minimă globală",
                "text": "De ce date de intrare are nevoie portofoliul de varianță minimă globală (GMV)?",
                "options": [
                    "Doar de randamentele așteptate",
                    "Doar de matricea de covarianță",
                    "De randamentele așteptate și rata fără risc",
                    "De capitalizările bursiere"
                ],
                "correctExplanation": "w_GMV = Σ⁻¹1 / 1'Σ⁻¹1 folosește doar matricea de covarianță; de aceea este mai robust decât portofoliul tangent.",
                "incorrectExplanation": "Formula GMV nu conține randamente așteptate: este nevoie doar de Σ."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Two-asset diversification",
                "text": "SPY and TLT had volatilities of 14.7% and 13.5% and a correlation of −0.10 (2002–2026). What was the volatility of their minimum-variance mix?",
                "options": [
                    "About 14%",
                    "About 13.5%",
                    "About 9.4%",
                    "Exactly zero"
                ],
                "correctExplanation": "With ρ = −0.10 the minimum-variance weight is 46% SPY and the volatility falls to 9.4%, below either asset.",
                "incorrectExplanation": "A negative correlation pushes the mix well below both volatilities, but not to zero (that needs ρ = −1)."
            },
            "ro": {
                "title": "Diversificarea cu două active",
                "text": "SPY și TLT au avut volatilități de 14,7% și 13,5% și o corelație de −0,10 (2002–2026). Care a fost volatilitatea combinației de varianță minimă?",
                "options": [
                    "Circa 14%",
                    "Circa 13,5%",
                    "Circa 9,4%",
                    "Exact zero"
                ],
                "correctExplanation": "Cu ρ = −0,10 ponderea de varianță minimă este 46% SPY, iar volatilitatea scade la 9,4%, sub a oricărui activ.",
                "incorrectExplanation": "O corelație negativă coboară combinația mult sub ambele volatilități, dar nu la zero (pentru asta ar trebui ρ = −1)."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Tobin separation",
                "text": "What does two-fund separation (Tobin, 1958) state?",
                "options": [
                    "With a riskless asset, all investors hold the same risky portfolio and differ only in how much they borrow or lend",
                    "Every investor should hold only two assets",
                    "Risky and riskless assets must have equal weights",
                    "The market portfolio has zero variance"
                ],
                "correctExplanation": "Risk aversion changes only the mix between the riskless asset and the tangency portfolio, not the risky portfolio itself.",
                "incorrectExplanation": "Separation concerns the split between cash and a single risky portfolio, the tangency portfolio."
            },
            "ro": {
                "title": "Separarea lui Tobin",
                "text": "Ce afirmă separarea în două fonduri (Tobin, 1958)?",
                "options": [
                    "Cu un activ fără risc, toți investitorii dețin același portofoliu riscant și diferă doar prin cât împrumută sau plasează",
                    "Fiecare investitor trebuie să dețină doar două active",
                    "Activele riscante și cel fără risc trebuie să aibă ponderi egale",
                    "Portofoliul pieței are varianță zero"
                ],
                "correctExplanation": "Aversiunea la risc schimbă doar combinația dintre activul fără risc și portofoliul tangent, nu portofoliul riscant.",
                "incorrectExplanation": "Separarea privește împărțirea între numerar și un singur portofoliu riscant, cel tangent."
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
                "correctExplanation": "Optimizatorul tratează zgomotul din date drept informație și se încarcă pe cele mai mari erori.",
                "incorrectExplanation": "Ideea este că optimizatorul urmărește activele care arată cel mai bine din cauza zgomotului de estimare."
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
                "text": "SPY are o volatilitate anuală de circa 15%. Aproximativ câți ani de date dau o eroare standard de 1% pentru media anuală?",
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
                    "Niciunul dintre 14 modele de optimizare nu a bătut consecvent 1/N în afara eșantionului",
                    "Medie–varianță de selecție bate 1/N cu cinci ani de date",
                    "1/N are cea mai mică varianță dintre toate regulile",
                    "Doar shrinkage-ul bate 1/N"
                ],
                "correctExplanation": "Eroarea de estimare anulează câștigul optimizării; cu 25 de active, MV de selecție are nevoie de circa 3000 de luni de date.",
                "incorrectExplanation": "Rezultatul lor este că niciun model nu a bătut consecvent ponderile egale în raport Sharpe, echivalent cert sau rulaj."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Window length",
                "text": "In the chapter's simulation with nine sectors, from which estimation window did sample MV beat 1/N (median true Sharpe)?",
                "options": [
                    "36 months",
                    "60 months",
                    "120 months",
                    "480 months"
                ],
                "correctExplanation": "Sample MV reached a median true Sharpe of 0.55 versus 0.54 for 1/N only with 480 months (40 years).",
                "incorrectExplanation": "With 60 months MV reached only 0.31; it needed decades of data."
            },
            "ro": {
                "title": "Lungimea ferestrei",
                "text": "În simularea din capitol cu nouă sectoare, de la ce fereastră de estimare a bătut MV de selecție 1/N (Sharpe adevărat median)?",
                "options": [
                    "36 de luni",
                    "60 de luni",
                    "120 de luni",
                    "480 de luni"
                ],
                "correctExplanation": "MV de selecție a atins un Sharpe adevărat median de 0,55 față de 0,54 pentru 1/N abia cu 480 de luni (40 de ani).",
                "incorrectExplanation": "Cu 60 de luni, MV a atins doar 0,31; a avut nevoie de decenii de date."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "In-sample optimism",
                "text": "In 2000 simulated 60-month samples, what was the median Sharpe of the estimated tangency portfolio in sample and with the true parameters?",
                "options": [
                    "0.66 and 0.66",
                    "1.57 and 0.30",
                    "0.30 and 1.57",
                    "0.54 and 0.54"
                ],
                "correctExplanation": "In-sample Sharpe ratios of optimised portfolios are biased upwards: 1.57 estimated against 0.30 true.",
                "incorrectExplanation": "The in-sample value is far too optimistic; evaluated with the true parameters the portfolio is much worse."
            },
            "ro": {
                "title": "Optimismul din eșantion",
                "text": "În 2000 de eșantioane simulate de 60 de luni, care a fost Sharpe-ul median al portofoliului tangent estimat în eșantion și cu parametrii adevărați?",
                "options": [
                    "0,66 și 0,66",
                    "1,57 și 0,30",
                    "0,30 și 1,57",
                    "0,54 și 0,54"
                ],
                "correctExplanation": "Rapoartele Sharpe în eșantion ale portofoliilor optimizate sunt deplasate în sus: 1,57 estimat față de 0,30 adevărat.",
                "incorrectExplanation": "Valoarea din eșantion este mult prea optimistă; evaluat cu parametrii adevărați, portofoliul este mult mai slab."
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
                "text": "Ce este estimatorul Ledoit–Wolf al matricei de covarianță?",
                "options": [
                    "Matricea de selecție cu valorile proprii negative puse la zero",
                    "O matrice estimată din date zilnice în loc de lunare",
                    "O medie ponderată δF + (1 − δ)S între o țintă structurată și matricea de selecție",
                    "Matricea identitate"
                ],
                "correctExplanation": "δ este ales din date astfel încât să minimizeze distanța pătratică așteptată față de matricea adevărată.",
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
                "text": "Ce au arătat Jagannathan și Ma (2003) despre restricțiile fără vânzări în lipsă?",
                "options": [
                    "Scad întotdeauna raportul Sharpe",
                    "Fac matricea de covarianță singulară",
                    "Sunt echivalente cu adăugarea unui activ fără risc",
                    "Acționează ca un shrinkage al matricei de covarianță și pot reduce riscul în afara eșantionului"
                ],
                "correctExplanation": "GMV doar long este GMV fără restricții al unei matrice de covarianță modificate: restricția „greșită” ajută.",
                "incorrectExplanation": "Ideea lor este că restricția contractă implicit covarianțele activelor pe care este activă."
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
                "text": "În Black–Litterman, ce sunt randamentele implicite (de echilibru) π?",
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
                "title": "Ce ponderi se mișcă",
                "text": "Cu Ω = diag(PτΣP') și o singură opinie asupra XLK minus XLU, ce ponderi Black–Litterman se schimbă față de referință?",
                "options": [
                    "Doar XLK și XLU",
                    "Toate cele nouă sectoare",
                    "Niciuna",
                    "Doar sectoarele cele mai corelate cu XLK"
                ],
                "correctExplanation": "În forma He–Litterman schimbarea ponderilor este P'λ: se mișcă doar activele din opinie (XLK 11,1% → 14,4%, XLU 11,1% → 7,8%).",
                "incorrectExplanation": "Abaterea de la referință se află în direcția portofoliului opiniei."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Risk contribution",
                "text": "How is the risk contribution of asset i defined?",
                "options": [
                    "w_i σ_i",
                    "w_i / σ_p",
                    "σ_i² / σ_p²",
                    "w_i (Σw)_i / σ_p, and the contributions sum to σ_p"
                ],
                "correctExplanation": "Volatility is homogeneous of degree one, so Euler's theorem splits it additively into w_i ∂σ_p/∂w_i.",
                "incorrectExplanation": "The definition uses the marginal contribution (Σw)_i/σ_p times the weight."
            },
            "ro": {
                "title": "Contribuția la risc",
                "text": "Cum se definește contribuția la risc a activului i?",
                "options": [
                    "w_i σ_i",
                    "w_i / σ_p",
                    "σ_i² / σ_p²",
                    "w_i (Σw)_i / σ_p, iar contribuțiile se adună la σ_p"
                ],
                "correctExplanation": "Volatilitatea este omogenă de gradul unu, deci teorema lui Euler o descompune aditiv în w_i ∂σ_p/∂w_i.",
                "incorrectExplanation": "Definiția folosește contribuția marginală (Σw)_i/σ_p înmulțită cu ponderea."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "ERC with two assets",
                "text": "For two assets, what are the equal-risk-contribution (ERC) weights?",
                "options": [
                    "Equal weights",
                    "Proportional to 1/σ_i, whatever the correlation",
                    "Proportional to σ_i",
                    "The GMV weights"
                ],
                "correctExplanation": "Both risk contributions share the same cross term, so they are equal when w₁σ₁ = w₂σ₂.",
                "incorrectExplanation": "With two assets the correlation drops out of the ERC condition."
            },
            "ro": {
                "title": "ERC cu două active",
                "text": "Pentru două active, care sunt ponderile cu contribuții egale la risc (ERC)?",
                "options": [
                    "Ponderi egale",
                    "Proporționale cu 1/σ_i, oricare ar fi corelația",
                    "Proporționale cu σ_i",
                    "Ponderile GMV"
                ],
                "correctExplanation": "Ambele contribuții la risc au același termen încrucișat, deci sunt egale când w₁σ₁ = w₂σ₂.",
                "incorrectExplanation": "Cu două active, corelația dispare din condiția ERC."
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
                    "Sunt întotdeauna egale"
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
                "text": "Într-un portofoliu 60% SPY, 40% IEF (2002–2026), ce parte din risc a venit de la SPY?",
                "options": [
                    "Circa 94%",
                    "60%",
                    "Circa 50%",
                    "Circa 31%"
                ],
                "correctExplanation": "Volatilitatea SPY (14,7%) este de peste două ori cea a IEF (6,6%), iar corelația ușor negativă, deci SPY domină riscul.",
                "incorrectExplanation": "Ponderile nu sunt cote de risc: activul volatil poartă cea mai mare parte a riscului."
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
                "correctExplanation": "HRP funcționează chiar dacă Σ este singulară; toate ponderile sale sunt pozitive.",
                "incorrectExplanation": "HRP folosește un arbore și alocări invers proporționale cu varianța, niciodată o inversare de matrice sau randamente așteptate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Turnover",
                "text": "How is monthly turnover measured in the chapter's backtests?",
                "options": [
                    "The number of assets with a non-zero weight",
                    "The sum of absolute differences between new weights and drifted old weights",
                    "The change in portfolio volatility",
                    "The share of months with a loss"
                ],
                "correctExplanation": "TO = Σ|w_new − w⁺|, where w⁺ are last month's weights after they drifted with returns; net return = gross − c × TO.",
                "incorrectExplanation": "Turnover is the fraction of wealth traded at rebalancing, computed from drifted weights."
            },
            "ro": {
                "title": "Rulajul",
                "text": "Cum se măsoară rulajul lunar în backtest-urile din capitol?",
                "options": [
                    "Numărul activelor cu pondere nenulă",
                    "Suma diferențelor absolute dintre ponderile noi și ponderile vechi după evoluția prețurilor",
                    "Schimbarea volatilității portofoliului",
                    "Ponderea lunilor cu pierderi"
                ],
                "correctExplanation": "TO = Σ|w_nou − w⁺|, unde w⁺ sunt ponderile lunii trecute după evoluția prețurilor; randament net = brut − c × TO.",
                "incorrectExplanation": "Rulajul este fracțiunea din avere tranzacționată la reechilibrare, calculată din ponderile după evoluția prețurilor."
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
                    "GMV a bătut semnificativ 1/N peste tot",
                    "Nicio regulă nu a bătut semnificativ 1/N; MV de selecție a eșuat în toate universurile",
                    "HRP a bătut toate regulile după costuri"
                ],
                "correctExplanation": "Cel mai mare câștig față de 1/N (MV-LO pe setul multi-active, +0,29) a avut p = 0,12; diferențele semnificative au fost pierderi.",
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
                "text": "De ce sunt preferate testele HAC sau bootstrap pe blocuri formulei i.i.d. pentru diferențele de raport Sharpe?",
                "options": [
                    "Randamentele au cozi groase și grupări de volatilitate, pe care formula i.i.d. Normală le ignoră",
                    "Formula i.i.d. nu poate trata strategii corelate",
                    "Testele HAC nu au nevoie de un eșantion",
                    "Bootstrap-ul respinge întotdeauna ipoteza nulă"
                ],
                "correctExplanation": "Ledoit și Wolf (2008) folosesc o covarianță HAC a lui (r₁, r₂, r₁², r₂²) și un bootstrap circular pe blocuri care păstrează dependența.",
                "incorrectExplanation": "Formula i.i.d. ține cont de corelația dintre strategii; slăbiciunea ei este ipoteza i.i.d. Normală."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "BVB benchmark",
                "text": "Why should optimised BVB portfolios be compared with BET-TR rather than BET?",
                "options": [
                    "BET-TR contains more stocks",
                    "BET is computed in euro",
                    "BET-TR has lower volatility by construction",
                    "BET is a price index; BET-TR reinvests dividends, worth about 7% a year in 2017–2026"
                ],
                "correctExplanation": "The stock returns include dividends, so the benchmark must too: BET-TR averaged 24.7% a year against 17.8% for BET.",
                "incorrectExplanation": "The difference between the two indices is the dividends, not the number of stocks or the currency."
            },
            "ro": {
                "title": "Reperul BVB",
                "text": "De ce trebuie comparate portofoliile BVB optimizate cu BET-TR și nu cu BET?",
                "options": [
                    "BET-TR conține mai multe acțiuni",
                    "BET se calculează în euro",
                    "BET-TR are prin construcție volatilitate mai mică",
                    "BET este un indice de preț; BET-TR reinvestește dividendele, de circa 7% pe an în 2017–2026"
                ],
                "correctExplanation": "Randamentele acțiunilor includ dividendele, deci și reperul trebuie să le includă: BET-TR a avut în medie 24,7% pe an față de 17,8% pentru BET.",
                "incorrectExplanation": "Diferența dintre cei doi indici o reprezintă dividendele, nu numărul de acțiuni sau moneda."
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
                "text": "În universul cu 16 ETF-uri, sub ce cost aproximativ pe unitatea de rulaj și-a păstrat MV doar long avantajul față de 1/N?",
                "options": [
                    "2 bp",
                    "Circa 22 bp",
                    "Circa 100 bp",
                    "La orice cost"
                ],
                "correctExplanation": "MV-LO tranzacționează circa 0,20 din avere pe lună față de 0,025 pentru 1/N, deci micul avantaj brut (0,81 față de 0,76) dispare la circa 22 bp.",
                "incorrectExplanation": "Rulajul mare erodează rapid un avantaj brut mic."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Low risk, low Sharpe",
                "text": "On the multi-asset set (2012–2026), GMV rules had the lowest volatility but also the lowest Sharpe ratios. Why?",
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
                "text": "Pe setul multi-active (2012–2026), regulile GMV au avut cea mai mică volatilitate, dar și cele mai mici rapoarte Sharpe. De ce?",
                "options": [
                    "Au deținut mai ales acțiuni",
                    "Rulajul lor a fost zero",
                    "S-au încărcat pe titluri de stat, ale căror randamente în exces au fost ușor negative după 2012",
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
                "correctExplanation": "Out of sample means that the weights of month t use only data up to month t-1, e.g. a rolling 60-month window. A covariance matrix from the full sample leaks future information; sqrt(12) is the right factor for monthly data.",
                "incorrectExplanation": "The annualisation with sqrt(12) and the GMV formula are correct; the problem is that the covariance matrix already contains the evaluation months (look-ahead bias)."
            },
            "ro": {
                "title": "Găsiți eroarea: un backtest scris de AI",
                "text": "Un asistent AI scrie: „Estimez matricea de covarianță o singură dată pe tot eșantionul 2000-2026, calculez ponderile GMV, reechilibrez lunar la ele și raportez un raport Sharpe în afara eșantionului de 0,9, anualizat cu sqrt(12).” Care este eroarea?",
                "options": [
                    "Rapoartele Sharpe lunare se anualizează cu sqrt(252), nu cu sqrt(12)",
                    "Ponderile folosesc date din lunile evaluate (informație din viitor), deci raportul Sharpe este în eșantion, nu în afara eșantionului",
                    "Ponderile GMV sunt proporționale cu inversa matricei de covarianță înmulțită cu randamentele așteptate, nu cu un vector de unu",
                    "Ponderile GMV nu pot fi reechilibrate lunar, deoarece nu însumează unu"
                ],
                "correctExplanation": "În afara eșantionului înseamnă că ponderile lunii t folosesc doar date până în luna t-1, de exemplu o fereastră rulantă de 60 de luni. O matrice de covarianță din tot eșantionul folosește informație din viitor; sqrt(12) este factorul corect pentru date lunare.",
                "incorrectExplanation": "Anualizarea cu sqrt(12) și formula GMV sunt corecte; problema este că matricea de covarianță conține deja lunile evaluate (informație din viitor)."
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
                "correctExplanation": "Contribuțiile Euler folosesc riscul marginal (Sigma w)_i / sigma_p, care include covarianțele; ele însumează sigma_p. Deoarece acțiunile sunt mult mai volatile decât obligațiunile, ele poartă de regulă 90% sau mai mult din riscul unui portofoliu 60/40.",
                "incorrectExplanation": "Contribuțiile însumează într-adevăr volatilitatea portofoliului, dar numai cu RC_i = w_i (Sigma w)_i / sigma_p; cu această formulă acțiunile, mai volatile, poartă mult mai mult decât ponderea lor de 60% în bani."
            }
        }
    ]
};

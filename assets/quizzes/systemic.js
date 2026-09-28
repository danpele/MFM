// ============================================================
// Quiz bank for chapter id 'systemic': Systemic Risk and Networks (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['systemic'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Systemic risk",
                "text": "What distinguishes systemic risk from the risk of a single bank?",
                "options": [
                    "It is the risk that distress of one or several institutions impairs the financial system as a whole",
                    "It is the VaR of the largest bank",
                    "It is the market risk of the stock index",
                    "It is the credit risk of households"
                ],
                "correctExplanation": "Systemic risk concerns the whole system: one failure can spread through runs, common exposures, fire sales and counterparty links.",
                "incorrectExplanation": "Systemic risk is not the risk of one institution or one asset class; it is the risk that distress spreads and impairs the system as a whole."
            },
            "ro": {
                "title": "Riscul sistemic",
                "text": "Ce deosebește riscul sistemic de riscul unei singure bănci?",
                "options": [
                    "Este riscul ca dificultățile uneia sau ale mai multor instituții să afecteze sistemul financiar în ansamblu",
                    "Este VaR al celei mai mari bănci",
                    "Este riscul de piață al indicelui bursier",
                    "Este riscul de credit al gospodăriilor"
                ],
                "correctExplanation": "Riscul sistemic privește întregul sistem: un faliment se poate propaga prin retrageri, expuneri comune, vânzări forțate și legături între contrapărți.",
                "incorrectExplanation": "Riscul sistemic nu este riscul unei instituții sau al unei clase de active; este riscul ca dificultățile să se propage și să afecteze sistemul în ansamblu."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Definition of MES",
                "text": "What is the MES 5% of bank i?",
                "options": [
                    "The VaR 5% of the bank",
                    "The average loss of the bank on the worst 5% of days for the market",
                    "The average loss of the market on the worst 5% of days for the bank",
                    "The capital the bank must raise in a crisis"
                ],
                "correctExplanation": "MES = -E[X_i | X_m <= q_5%(X_m)]: the bank's average loss on the market's worst days.",
                "incorrectExplanation": "MES conditions on the market being in its tail and averages the bank's loss; the reverse conditioning is exposure of the market, and the capital need is SRISK."
            },
            "ro": {
                "title": "Definiția MES",
                "text": "Ce este MES 5% al băncii i?",
                "options": [
                    "VaR 5% al băncii",
                    "Pierderea medie a băncii în cele mai rele 5% din zilele pieței",
                    "Pierderea medie a pieței în cele mai rele 5% din zilele băncii",
                    "Capitalul pe care banca trebuie să îl atragă într-o criză"
                ],
                "correctExplanation": "MES = -E[X_i | X_m <= q_5%(X_m)]: pierderea medie a băncii în cele mai rele zile ale pieței.",
                "incorrectExplanation": "MES condiționează pe piața aflată în coadă și face media pierderii băncii; condiționarea inversă privește piața, iar necesarul de capital este SRISK."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "MES under the Normal distribution",
                "text": "Bank and market are jointly Normal with zero means. The bank's beta is 1.2 and the market's ES 5% is 3%. What is the MES 5%?",
                "options": [
                    "1.2%",
                    "2.5%",
                    "3.6%",
                    "4.2%"
                ],
                "correctExplanation": "Under joint normality E[X_i | X_m] = beta X_m, so MES = beta x ES_5%(market) = 1.2 x 3% = 3.6%.",
                "incorrectExplanation": "With joint normality the conditional mean is beta times the market return, so MES is beta times the market's ES: 1.2 x 3% = 3.6%."
            },
            "ro": {
                "title": "MES sub distribuția Normală",
                "text": "Banca și piața au distribuție Normală bivariată cu medii zero. Beta băncii este 1,2, iar ES 5% al pieței este 3%. Cât este MES 5%?",
                "options": [
                    "1,2%",
                    "2,5%",
                    "3,6%",
                    "4,2%"
                ],
                "correctExplanation": "Sub normalitate bivariată E[X_i | X_m] = beta X_m, deci MES = beta x ES_5%(piață) = 1,2 x 3% = 3,6%.",
                "incorrectExplanation": "Cu normalitate bivariată media condiționată este beta înmulțit cu randamentul pieței, deci MES este beta înmulțit cu ES al pieței: 1,2 x 3% = 3,6%."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "LRMES",
                "text": "Which crisis does the LRMES approximation 1 - exp(-18 x MES) refer to?",
                "options": [
                    "A one-day fall of the market by 2%",
                    "A default of the bank itself",
                    "A 10-day loss at the 1% level",
                    "A fall of the market by 40% over six months"
                ],
                "correctExplanation": "LRMES is the expected fall of the bank's equity in a crisis defined as a 40% market decline over six months.",
                "incorrectExplanation": "The daily MES (market below -2%) is only the input; LRMES extrapolates it to a six-month crisis in which the market falls by 40%."
            },
            "ro": {
                "title": "LRMES",
                "text": "La ce criză se referă aproximarea LRMES 1 - exp(-18 x MES)?",
                "options": [
                    "O scădere a pieței cu 2% într-o zi",
                    "Falimentul băncii înseși",
                    "O pierdere pe 10 zile la nivelul de 1%",
                    "O scădere a pieței cu 40% în șase luni"
                ],
                "correctExplanation": "LRMES este scăderea așteptată a capitalului băncii într-o criză definită ca o scădere a pieței cu 40% în șase luni.",
                "incorrectExplanation": "MES zilnic (piața sub -2%) este doar intrarea; LRMES îl extrapolează la o criză de șase luni în care piața scade cu 40%."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "SRISK",
                "text": "A bank has debt D = 900, market equity W = 100, LRMES = 50% and k = 8%. What is its SRISK?",
                "options": [
                    "26",
                    "72",
                    "-18",
                    "46"
                ],
                "correctExplanation": "SRISK = kD - (1 - k)(1 - LRMES)W = 72 - 0.92 x 0.5 x 100 = 72 - 46 = 26.",
                "incorrectExplanation": "Apply SRISK = kD - (1 - k)(1 - LRMES)W: 0.08 x 900 = 72 minus 0.92 x 0.5 x 100 = 46 gives 26."
            },
            "ro": {
                "title": "SRISK",
                "text": "O bancă are datorii D = 900, capital de piață W = 100, LRMES = 50% și k = 8%. Cât este SRISK?",
                "options": [
                    "26",
                    "72",
                    "-18",
                    "46"
                ],
                "correctExplanation": "SRISK = kD - (1 - k)(1 - LRMES)W = 72 - 0,92 x 0,5 x 100 = 72 - 46 = 26.",
                "incorrectExplanation": "Aplicați SRISK = kD - (1 - k)(1 - LRMES)W: 0,08 x 900 = 72 minus 0,92 x 0,5 x 100 = 46 dă 26."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Break-even leverage",
                "text": "What happens to the break-even leverage L* = 1 + (1 - k)(1 - LRMES)/k when LRMES rises?",
                "options": [
                    "It rises",
                    "It falls: the bank can afford less debt before a crisis creates a shortfall",
                    "It does not change",
                    "It becomes negative"
                ],
                "correctExplanation": "A higher LRMES lowers (1 - LRMES), so L* falls.",
                "incorrectExplanation": "L* depends on 1 - LRMES, the equity left after the crisis; a larger crisis loss leaves less equity and lowers the leverage the bank can sustain."
            },
            "ro": {
                "title": "Levierul de echilibru",
                "text": "Ce se întâmplă cu levierul de echilibru L* = 1 + (1 - k)(1 - LRMES)/k când LRMES crește?",
                "options": [
                    "Crește",
                    "Scade: banca își permite mai puține datorii înainte ca o criză să creeze un deficit",
                    "Nu se schimbă",
                    "Devine negativ"
                ],
                "correctExplanation": "Un LRMES mai mare scade (1 - LRMES), deci L* scade.",
                "incorrectExplanation": "L* depinde de 1 - LRMES, capitalul rămas după criză; o pierdere mai mare în criză lasă mai puțin capital și scade levierul pe care banca îl poate susține."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Definition of CoVaR",
                "text": "What does the CoVaR 1% of the system given bank i measure?",
                "options": [
                    "The VaR 1% of bank i",
                    "The average loss of bank i when the system is in distress",
                    "The VaR 1% of the system on a day when bank i is at its own VaR 1%",
                    "The correlation between bank i and the system"
                ],
                "correctExplanation": "CoVaR is the VaR of the system conditional on the institution being at its VaR.",
                "incorrectExplanation": "CoVaR conditions the system's quantile on bank i being in distress; the loss of the bank given system distress is the exposure CoVaR."
            },
            "ro": {
                "title": "Definiția CoVaR",
                "text": "Ce măsoară CoVaR 1% al sistemului condiționat de banca i?",
                "options": [
                    "VaR 1% al băncii i",
                    "Pierderea medie a băncii i când sistemul este în dificultate",
                    "VaR 1% al sistemului într-o zi în care banca i se află la propriul VaR 1%",
                    "Corelația dintre banca i și sistem"
                ],
                "correctExplanation": "CoVaR este VaR al sistemului condiționat de instituția aflată la nivelul VaR-ului ei.",
                "incorrectExplanation": "CoVaR condiționează cuantila sistemului de dificultățile băncii i; pierderea băncii când sistemul este în dificultate este CoVaR de expunere."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Estimating Delta-CoVaR",
                "text": "With the quantile regression X_sys = a + b X_i at level alpha, how is Delta-CoVaR computed?",
                "options": [
                    "a + b",
                    "b x VaR of the system",
                    "a x (q_50%(X_i) - q_alpha(X_i))",
                    "b x (q_50%(X_i) - q_alpha(X_i))"
                ],
                "correctExplanation": "Delta-CoVaR is the change in the system quantile between the bank's median and distress states: b times the difference of the bank's quantiles.",
                "incorrectExplanation": "The intercept cancels when the two states are compared; only the tail slope b and the bank's own quantiles matter."
            },
            "ro": {
                "title": "Estimarea Delta-CoVaR",
                "text": "Cu regresia cuantilă X_sys = a + b X_i la nivelul alpha, cum se calculează Delta-CoVaR?",
                "options": [
                    "a + b",
                    "b x VaR al sistemului",
                    "a x (q_50%(X_i) - q_alpha(X_i))",
                    "b x (q_50%(X_i) - q_alpha(X_i))"
                ],
                "correctExplanation": "Delta-CoVaR este schimbarea cuantilei sistemului între starea mediană și starea de dificultate a băncii: b înmulțit cu diferența cuantilelor băncii.",
                "incorrectExplanation": "Termenul liber se simplifică la compararea celor două stări; contează doar panta din coadă b și cuantilele băncii."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Delta-CoVaR under the Normal distribution",
                "text": "Under joint normality with zero means, Delta-CoVaR at level alpha equals -rho x sigma_sys x z_alpha. What does it NOT depend on?",
                "options": [
                    "The standard deviation of the bank",
                    "The correlation between bank and system",
                    "The volatility of the system",
                    "The tail probability alpha"
                ],
                "correctExplanation": "sigma_i cancels: a bank with a large VaR but a low correlation contributes little to the system's tail.",
                "incorrectExplanation": "The formula contains rho, sigma_sys and z_alpha; the bank's own volatility drops out."
            },
            "ro": {
                "title": "Delta-CoVaR sub distribuția Normală",
                "text": "Sub normalitate bivariată cu medii zero, Delta-CoVaR la nivelul alpha este -rho x sigma_sys x z_alpha. De ce NU depinde?",
                "options": [
                    "De abaterea standard a băncii",
                    "De corelația dintre bancă și sistem",
                    "De volatilitatea sistemului",
                    "De probabilitatea cozii alpha"
                ],
                "correctExplanation": "sigma_i se simplifică: o bancă cu VaR mare, dar corelație mică, contribuie puțin la coada sistemului.",
                "incorrectExplanation": "Formula conține rho, sigma_sys și z_alpha; volatilitatea proprie a băncii dispare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "VaR and Delta-CoVaR",
                "text": "In the lecture, the Spearman rank correlation between VaR 1% and Delta-CoVaR 1% of eleven banks was about 0.16. What follows?",
                "options": [
                    "Banks with a large VaR are the most systemic",
                    "Ranking banks by their own VaR does not identify the banks that contribute most to system risk",
                    "Delta-CoVaR is useless",
                    "VaR and Delta-CoVaR are the same measure"
                ],
                "correctExplanation": "A weak rank correlation means the two measures order banks differently: the central message of Adrian and Brunnermeier.",
                "incorrectExplanation": "A correlation near zero means the rankings differ; it neither makes the banks with large VaR systemic nor makes Delta-CoVaR redundant."
            },
            "ro": {
                "title": "VaR și Delta-CoVaR",
                "text": "În curs, corelația de rang Spearman dintre VaR 1% și Delta-CoVaR 1% pentru unsprezece bănci a fost de aproximativ 0,16. Ce rezultă?",
                "options": [
                    "Băncile cu VaR mare sunt cele mai sistemice",
                    "Ordonarea băncilor după propriul VaR nu identifică băncile care contribuie cel mai mult la riscul sistemului",
                    "Delta-CoVaR este inutil",
                    "VaR și Delta-CoVaR sunt aceeași măsură"
                ],
                "correctExplanation": "O corelație de rang slabă înseamnă că cele două măsuri ordonează băncile diferit: mesajul central al lui Adrian și Brunnermeier.",
                "incorrectExplanation": "O corelație apropiată de zero înseamnă clasamente diferite; nu face sistemice băncile cu VaR mare și nici nu face Delta-CoVaR redundant."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Bootstrap intervals",
                "text": "Why does the lecture use a moving-block bootstrap with blocks of 20 days for Delta-CoVaR?",
                "options": [
                    "Because returns are Normal",
                    "Because it is faster than the i.i.d. bootstrap",
                    "Because tail days cluster in crises and blocks keep these clusters together",
                    "Because quantile regression needs exactly 20 observations"
                ],
                "correctExplanation": "Volatility clustering makes tail days dependent; blocks preserve the dependence and give wider, more honest intervals.",
                "incorrectExplanation": "The reason is dependence: the i.i.d. bootstrap breaks crisis clusters apart and understates uncertainty."
            },
            "ro": {
                "title": "Intervale bootstrap",
                "text": "De ce folosește cursul bootstrap pe blocuri mobile de 20 de zile pentru Delta-CoVaR?",
                "options": [
                    "Pentru că randamentele sunt Normale",
                    "Pentru că este mai rapid decât bootstrap-ul i.i.d.",
                    "Pentru că zilele din coadă se grupează în crize, iar blocurile păstrează aceste grupări",
                    "Pentru că regresia cuantilă are nevoie de exact 20 de observații"
                ],
                "correctExplanation": "Gruparea volatilității face zilele din coadă dependente; blocurile păstrează dependența și dau intervale mai largi și mai oneste.",
                "incorrectExplanation": "Motivul este dependența: bootstrap-ul i.i.d. desparte grupările din crize și subestimează incertitudinea."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "System portfolio",
                "text": "Why is bank i left out of its own system portfolio when estimating CoVaR?",
                "options": [
                    "To reduce computing time",
                    "Because the bank has no data",
                    "Because regulators require it",
                    "Because its own return would appear on both sides of the regression and inflate the slope mechanically"
                ],
                "correctExplanation": "With bank i inside the system, X_i enters both the dependent and the explanatory variable, which creates a spurious link.",
                "incorrectExplanation": "The reason is statistical: including the bank creates a mechanical correlation between the system and the bank."
            },
            "ro": {
                "title": "Portofoliul sistemului",
                "text": "De ce este banca i lăsată în afara propriului portofoliu al sistemului la estimarea CoVaR?",
                "options": [
                    "Pentru a reduce timpul de calcul",
                    "Pentru că banca nu are date",
                    "Pentru că o cer autoritățile",
                    "Pentru că propriul randament ar apărea de ambele părți ale regresiei și ar umfla panta în mod mecanic"
                ],
                "correctExplanation": "Cu banca i în sistem, X_i intră atât în variabila dependentă, cât și în cea explicativă, ceea ce creează o legătură falsă.",
                "incorrectExplanation": "Motivul este statistic: includerea băncii creează o corelație mecanică între sistem și bancă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Time-varying Delta-CoVaR",
                "text": "In the lecture, why did the Delta-CoVaR of six banks move almost together over time?",
                "options": [
                    "Because the six banks are the same company",
                    "Because the common lagged state variables drive the banks' conditional quantiles",
                    "Because the bootstrap was not used",
                    "Because the slope b changes every day"
                ],
                "correctExplanation": "With state variables such as the VIX, time variation comes from the state; the slope b is constant.",
                "incorrectExplanation": "The slope is estimated once; the common state variables move all conditional quantiles together."
            },
            "ro": {
                "title": "Delta-CoVaR variabil în timp",
                "text": "În curs, de ce s-a mișcat Delta-CoVaR al celor șase bănci aproape împreună în timp?",
                "options": [
                    "Pentru că cele șase bănci sunt aceeași companie",
                    "Pentru că variabilele de stare întârziate comune conduc cuantilele condiționate ale băncilor",
                    "Pentru că nu s-a folosit bootstrap-ul",
                    "Pentru că panta b se schimbă în fiecare zi"
                ],
                "correctExplanation": "Cu variabile de stare precum VIX, variația în timp vine din stare; panta b este constantă.",
                "incorrectExplanation": "Panta se estimează o singură dată; variabilele de stare comune mișcă împreună toate cuantilele condiționate."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Generalized variance decomposition",
                "text": "Why do Diebold and Yilmaz use the generalized forecast error variance decomposition?",
                "options": [
                    "Because it is always smaller than the Cholesky one",
                    "Because it removes the need for a VAR",
                    "Because its results do not depend on the ordering of the variables",
                    "Because it makes the rows sum to zero"
                ],
                "correctExplanation": "The Pesaran-Shin generalized decomposition is invariant to ordering; Cholesky results depend on which bank comes first.",
                "incorrectExplanation": "Orthogonal (Cholesky) shocks depend on the ordering; the generalized version does not, after row normalisation."
            },
            "ro": {
                "title": "Descompunerea generalizată a dispersiei",
                "text": "De ce folosesc Diebold și Yilmaz descompunerea generalizată a dispersiei erorii de prognoză?",
                "options": [
                    "Pentru că este întotdeauna mai mică decât cea Cholesky",
                    "Pentru că elimină nevoia unui VAR",
                    "Pentru că rezultatele ei nu depind de ordinea variabilelor",
                    "Pentru că face ca liniile să însumeze zero"
                ],
                "correctExplanation": "Descompunerea generalizată Pesaran-Shin nu depinde de ordine; rezultatele Cholesky depind de ce bancă apare prima.",
                "incorrectExplanation": "Șocurile ortogonale (Cholesky) depind de ordine; versiunea generalizată nu, după normalizarea pe linii."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Total connectedness",
                "text": "Three banks have normalized variance shares (%) with rows (70, 20, 10), (25, 60, 15), (5, 10, 85). What is total connectedness?",
                "options": [
                    "71.7%",
                    "85%",
                    "33.3%",
                    "28.3%"
                ],
                "correctExplanation": "Off-diagonal sum = 30 + 40 + 15 = 85; divided by N = 3 gives 28.3%.",
                "incorrectExplanation": "Add the off-diagonal elements (the 'from others' of each row) and divide by the number of banks: 85/3 = 28.3%."
            },
            "ro": {
                "title": "Conectivitatea totală",
                "text": "Trei bănci au proporțiile normalizate ale dispersiei (%) cu liniile (70, 20, 10), (25, 60, 15), (5, 10, 85). Cât este conectivitatea totală?",
                "options": [
                    "71,7%",
                    "85%",
                    "33,3%",
                    "28,3%"
                ],
                "correctExplanation": "Suma elementelor din afara diagonalei = 30 + 40 + 15 = 85; împărțită la N = 3 dă 28,3%.",
                "incorrectExplanation": "Adunați elementele din afara diagonalei („de la ceilalți” pe fiecare linie) și împărțiți la numărul de bănci: 85/3 = 28,3%."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Net transmitter",
                "text": "In the same three-bank table, which bank is a net transmitter?",
                "options": [
                    "Bank 3: it sends 25 to others and receives 15",
                    "Bank 1: its own share is the smallest",
                    "Bank 2: it receives the most",
                    "None: net spillovers are always zero"
                ],
                "correctExplanation": "Net = to - from: bank 3 has 25 - 15 = +10.",
                "incorrectExplanation": "Net spillover compares column sums (to others) with row sums (from others); only bank 3 sends more than it receives."
            },
            "ro": {
                "title": "Transmițător net",
                "text": "În același tabel cu trei bănci, ce bancă este transmițător net?",
                "options": [
                    "Banca 3: trimite 25 către ceilalți și primește 15",
                    "Banca 1: are cea mai mică pondere proprie",
                    "Banca 2: primește cel mai mult",
                    "Niciuna: transmiterile nete sunt întotdeauna zero"
                ],
                "correctExplanation": "Net = către - de la: banca 3 are 25 - 15 = +10.",
                "incorrectExplanation": "Transmiterea netă compară sumele pe coloane (către ceilalți) cu sumele pe linii (de la ceilalți); doar banca 3 trimite mai mult decât primește."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Connectedness in the data",
                "text": "What did the rolling Diebold-Yilmaz index of 13 banks show around March 2020?",
                "options": [
                    "A fall to its lowest value",
                    "No change",
                    "A jump to its highest values within days, followed by a slow decay",
                    "A permanent doubling"
                ],
                "correctExplanation": "Total connectedness rose from about 62% in 2019 to about 78% in spring 2020 and decayed over the following year.",
                "incorrectExplanation": "Connectedness jumps in crises and decays slowly; March 2020 was near the maximum of the index."
            },
            "ro": {
                "title": "Conectivitatea în date",
                "text": "Ce a arătat indicele Diebold-Yilmaz pe ferestre mobile pentru 13 bănci în jurul lui martie 2020?",
                "options": [
                    "O scădere la cea mai mică valoare",
                    "Nicio schimbare",
                    "Un salt la cele mai mari valori în câteva zile, urmat de o scădere lentă",
                    "O dublare permanentă"
                ],
                "correctExplanation": "Conectivitatea totală a crescut de la aproximativ 62% în 2019 la aproximativ 78% în primăvara lui 2020 și a scăzut în anul următor.",
                "incorrectExplanation": "Conectivitatea urcă brusc în crize și scade încet; martie 2020 a fost aproape de maximul indicelui."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Romanian banks in the network",
                "text": "How did Banca Transilvania and BRD appear in the 13-bank volatility network?",
                "options": [
                    "As the largest net transmitters",
                    "As isolated nodes with zero links",
                    "As transmitters to US banks",
                    "As net receivers with a large own share of their variance"
                ],
                "correctExplanation": "Their own shares were above 70% and their net spillovers negative: they are driven mainly by domestic shocks and receive more than they send.",
                "incorrectExplanation": "Romanian banks receive a little from US and European banks and send almost nothing back."
            },
            "ro": {
                "title": "Băncile românești în rețea",
                "text": "Cum au apărut Banca Transilvania și BRD în rețeaua de volatilitate a celor 13 bănci?",
                "options": [
                    "Ca cei mai mari transmițători neți",
                    "Ca noduri izolate, fără legături",
                    "Ca transmițători către băncile americane",
                    "Ca receptori neți, cu o pondere proprie mare a dispersiei"
                ],
                "correctExplanation": "Ponderile lor proprii au fost peste 70%, iar transmiterile nete negative: sunt conduse mai ales de șocuri interne și primesc mai mult decât trimit.",
                "incorrectExplanation": "Băncile românești primesc puțin de la băncile americane și europene și nu trimit aproape nimic înapoi."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Financial Risk Meter",
                "text": "How is the Financial Risk Meter (FRM) defined?",
                "options": [
                    "As the average over firms of the L1 penalty lambda selected in each firm's 5% quantile regression on the other firms",
                    "As the average VaR of all firms",
                    "As the VIX divided by 100",
                    "As the number of firms in distress"
                ],
                "correctExplanation": "Each firm's 5% quantile is regressed with an L1 penalty on all other firms and macro variables; FRM averages the selected penalties.",
                "incorrectExplanation": "FRM is built from penalized quantile regressions, not from VaR levels or volatility indices."
            },
            "ro": {
                "title": "Financial Risk Meter",
                "text": "Cum este definit Financial Risk Meter (FRM)?",
                "options": [
                    "Ca media pe firme a penalizării L1 lambda aleasă în regresia cuantilă de 5% a fiecărei firme pe celelalte firme",
                    "Ca VaR mediu al tuturor firmelor",
                    "Ca VIX împărțit la 100",
                    "Ca numărul firmelor în dificultate"
                ],
                "correctExplanation": "Cuantila de 5% a fiecărei firme este regresată cu penalizare L1 pe toate celelalte firme și pe variabile macro; FRM face media penalizărilor alese.",
                "incorrectExplanation": "FRM se construiește din regresii cuantile penalizate, nu din niveluri VaR sau indici de volatilitate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "FRM with a small panel",
                "text": "With 13 banks, 15 regressors and 63-day windows, why was the GACV-selected penalty small and noisy?",
                "options": [
                    "Because the data were wrong",
                    "Because the unpenalized fit is feasible when there are far fewer regressors than days",
                    "Because GACV always selects lambda = 0",
                    "Because returns were standardised"
                ],
                "correctExplanation": "The FRM is designed for large cross-sections (more regressors than days), where a penalty is needed; with few regressors GACV prefers little penalty.",
                "incorrectExplanation": "The issue is dimension: with p much smaller than n, the fit barely needs a penalty, so its selected value is noisy."
            },
            "ro": {
                "title": "FRM cu un panel mic",
                "text": "Cu 13 bănci, 15 regresori și ferestre de 63 de zile, de ce a fost penalizarea aleasă prin GACV mică și zgomotoasă?",
                "options": [
                    "Pentru că datele erau greșite",
                    "Pentru că estimarea fără penalizare este posibilă când sunt mult mai puțini regresori decât zile",
                    "Pentru că GACV alege întotdeauna lambda = 0",
                    "Pentru că randamentele au fost standardizate"
                ],
                "correctExplanation": "FRM este construit pentru secțiuni transversale mari (mai mulți regresori decât zile), unde penalizarea este necesară; cu puțini regresori GACV preferă o penalizare mică.",
                "incorrectExplanation": "Problema este dimensiunea: cu p mult mai mic decât n, estimarea aproape nu are nevoie de penalizare, deci valoarea aleasă este zgomotoasă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Reverse stress test",
                "text": "In a linear factor model with Normal factors, what is the most plausible scenario f* producing a loss l*?",
                "options": [
                    "All factors fall by l*",
                    "The factor with the largest variance falls by l*, the others stay unchanged",
                    "f* = -l* Sigma b / (b' Sigma b)",
                    "f* = -l* b"
                ],
                "correctExplanation": "Minimising the Mahalanobis distance subject to -b'f = l* gives f* = -l* Sigma b / (b' Sigma b).",
                "incorrectExplanation": "The most plausible scenario weights each factor by its covariance with the portfolio: Sigma b, scaled so that the loss equals l*."
            },
            "ro": {
                "title": "Test invers de stres",
                "text": "Într-un model factorial liniar cu factori Normali, care este cel mai plauzibil scenariu f* care produce pierderea l*?",
                "options": [
                    "Toți factorii scad cu l*",
                    "Factorul cu cea mai mare dispersie scade cu l*, ceilalți rămân neschimbați",
                    "f* = -l* Sigma b / (b' Sigma b)",
                    "f* = -l* b"
                ],
                "correctExplanation": "Minimizarea distanței Mahalanobis cu condiția -b'f = l* dă f* = -l* Sigma b / (b' Sigma b).",
                "incorrectExplanation": "Cel mai plauzibil scenariu ponderează fiecare factor după covarianța lui cu portofoliul: Sigma b, scalat astfel încât pierderea să fie l*."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Probabilities of reverse stress scenarios",
                "text": "The reverse stress test gave a Mahalanobis distance of about 4.3 for a 25% loss in four weeks, yet in 2020 the bank portfolio lost about 52% (log return) in four weeks. What is the lesson?",
                "options": [
                    "The data are wrong",
                    "The factor model is exact",
                    "Reverse stress tests are useless",
                    "The shape of the scenario is informative, but Normal-model probabilities are far too small because of heavy tails and rising correlations"
                ],
                "correctExplanation": "Heavy tails and crisis correlations make extreme losses much more likely than the Normal model implies.",
                "incorrectExplanation": "Use the direction of the scenario, not its Normal probability: the real tail is much heavier."
            },
            "ro": {
                "title": "Probabilitățile scenariilor inverse de stres",
                "text": "Testul invers de stres a dat o distanță Mahalanobis de aproximativ 4,3 pentru o pierdere de 25% în patru săptămâni, dar în 2020 portofoliul bancar a pierdut aproximativ 52% (randament log) în patru săptămâni. Care este lecția?",
                "options": [
                    "Datele sunt greșite",
                    "Modelul factorial este exact",
                    "Testele inverse de stres sunt inutile",
                    "Forma scenariului este informativă, dar probabilitățile modelului Normal sunt mult prea mici din cauza cozilor grele și a corelațiilor care cresc"
                ],
                "correctExplanation": "Cozile grele și corelațiile din crize fac pierderile extreme mult mai probabile decât implică modelul Normal.",
                "incorrectExplanation": "Folosiți direcția scenariului, nu probabilitatea lui Normală: coada reală este mult mai grea."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Climate risk",
                "text": "Which statement about the ECB climate risk stress test of 2022 is correct?",
                "options": [
                    "Around 60% of the banks had no climate risk stress-testing framework",
                    "All banks included climate risk in their credit models",
                    "Losses were zero in every scenario",
                    "It was a capital adequacy exercise that set capital requirements"
                ],
                "correctExplanation": "The ECB reported that around 60% of banks did not yet have a climate risk stress-testing framework; the test was a learning exercise.",
                "incorrectExplanation": "The exercise was not a capital adequacy test; it found data gaps and projected losses of around EUR 70 billion for 41 banks, which the ECB called an understatement."
            },
            "ro": {
                "title": "Riscul climatic",
                "text": "Ce afirmație despre testul de stres climatic al ECB din 2022 este corectă?",
                "options": [
                    "Aproximativ 60% dintre bănci nu aveau un cadru de testare la stres pentru riscul climatic",
                    "Toate băncile includeau riscul climatic în modelele de credit",
                    "Pierderile au fost zero în toate scenariile",
                    "A fost un exercițiu de adecvare a capitalului care a stabilit cerințe de capital"
                ],
                "correctExplanation": "ECB a raportat că aproximativ 60% dintre bănci nu aveau încă un cadru de testare la stres pentru riscul climatic; testul a fost un exercițiu de învățare.",
                "incorrectExplanation": "Exercițiul nu a fost un test de adecvare a capitalului; a găsit lipsuri de date și a proiectat pierderi de aproximativ 70 de miliarde EUR pentru 41 de bănci, pe care ECB le-a considerat subestimate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Historical stress scenarios",
                "text": "In the lecture's historical scenarios, what did the December 2018 Romanian bank-tax episode show?",
                "options": [
                    "It hit all banks equally",
                    "Romanian banks fell most (about 26% over 10 days): a domestic political shock that global scenarios would miss",
                    "Romanian banks rose",
                    "Only US banks were affected"
                ],
                "correctExplanation": "Banca Transilvania and BRD lost about 26% over the worst 10 days, more than any international bank in that window.",
                "incorrectExplanation": "The episode was mainly domestic: a stress test built only on global crises would miss it."
            },
            "ro": {
                "title": "Scenarii istorice de stres",
                "text": "În scenariile istorice din curs, ce a arătat episodul taxei bancare din România din decembrie 2018?",
                "options": [
                    "A lovit toate băncile la fel",
                    "Băncile românești au scăzut cel mai mult (aproximativ 26% în 10 zile): un șoc politic intern pe care scenariile globale l-ar rata",
                    "Băncile românești au crescut",
                    "Au fost afectate doar băncile americane"
                ],
                "correctExplanation": "Banca Transilvania și BRD au pierdut aproximativ 26% în cele mai rele 10 zile, mai mult decât orice bancă internațională în acea fereastră.",
                "incorrectExplanation": "Episodul a fost în principal intern: un test de stres construit doar pe crize globale l-ar rata."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the error: MES on the wrong tail",
                "text": "Bank and market are jointly Normal with zero means, bank volatility 2.5%, correlation 0.5. An AI assistant writes: 'MES 5% = -E[X_i | X_i <= q_5%(X_i)] = 2.5 x phi(1.645)/0.05 = 5.16%.' What is wrong?",
                "options": [
                    "Nothing: this is the definition of MES",
                    "MES must use the 1% level, not 5%",
                    "This is the bank's own ES 5%; MES conditions on the market's tail, -E[X_i | X_m <= q_5%(X_m)], which here equals 0.5 x 2.5 x phi(1.645)/0.05 = 2.58%",
                    "MES should be reported as a negative number"
                ],
                "correctExplanation": "Marginal expected shortfall measures the bank's expected loss on the market's worst days: MES = beta x ES_5%(X_m) = rho x sigma_i x phi(1.645)/0.05 = 2.58%. A quick check: with rho = 0 MES must be 0, but the AI's formula does not contain rho.",
                "incorrectExplanation": "The conditioning event is a market crash, not a bad day of the bank itself: MES = -E[X_i | X_m <= q_5%(X_m)], which depends on the correlation and here equals 2.58%."
            },
            "ro": {
                "title": "Găsiți eroarea: MES pe coada greșită",
                "text": "Banca și piața au distribuție Normală bivariată cu medii zero, volatilitatea băncii 2,5%, corelația 0,5. Un asistent AI scrie: „MES 5% = -E[X_i | X_i <= q_5%(X_i)] = 2,5 x phi(1,645)/0,05 = 5,16%.” Ce este greșit?",
                "options": [
                    "Nimic: aceasta este definiția MES",
                    "MES trebuie calculat la nivelul 1%, nu 5%",
                    "Acesta este ES 5% al băncii; MES condiționează pe coada pieței, -E[X_i | X_m <= q_5%(X_m)], care aici este 0,5 x 2,5 x phi(1,645)/0,05 = 2,58%",
                    "MES trebuie raportat ca număr negativ"
                ],
                "correctExplanation": "Deficitul marginal așteptat măsoară pierderea așteptată a băncii în cele mai proaste zile ale pieței: MES = beta x ES_5%(X_m) = rho x sigma_i x phi(1,645)/0,05 = 2,58%. O verificare rapidă: cu rho = 0 MES trebuie să fie 0, dar formula AI-ului nu îl conține pe rho.",
                "incorrectExplanation": "Evenimentul de condiționare este o prăbușire a pieței, nu o zi proastă a băncii: MES = -E[X_i | X_m <= q_5%(X_m)], care depinde de corelație și aici este 2,58%."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the error: Granger network on prices",
                "text": "An AI assistant builds a Granger-causality network of ten banks by fitting pairwise VARs to daily price levels, and reports that almost every pair is significant at 1%. What is the most likely problem?",
                "options": [
                    "The VARs need more lags",
                    "Prices are non-stationary: Granger tests on levels give spurious significance; use returns (or a method built for integrated series)",
                    "Ten banks are too few for a network",
                    "The network should be built with a Cholesky ordering of the banks"
                ],
                "correctExplanation": "With unit-root prices the usual Wald test does not have its standard distribution and spurious links appear. Networks of Granger causality are built on returns (stationary), or with procedures designed for integrated series.",
                "incorrectExplanation": "The issue is the input, not the number of lags or banks: bank prices have unit roots, so tests on levels over-reject; run the tests on returns."
            },
            "ro": {
                "title": "Găsiți eroarea: rețea Granger pe prețuri",
                "text": "Un asistent AI construiește o rețea de cauzalitate Granger pentru zece bănci, estimând VAR-uri pe perechi pe nivelurile zilnice ale prețurilor, și raportează că aproape toate perechile sunt semnificative la 1%. Care este cea mai probabilă problemă?",
                "options": [
                    "VAR-urile au nevoie de mai multe întârzieri",
                    "Prețurile sunt nestaționare: testele Granger pe niveluri dau o semnificație falsă; folosiți randamente (sau o metodă construită pentru serii integrate)",
                    "Zece bănci sunt prea puține pentru o rețea",
                    "Rețeaua trebuie construită cu o ordonare Cholesky a băncilor"
                ],
                "correctExplanation": "Cu prețuri cu rădăcină unitară, testul Wald obișnuit nu are distribuția standard și apar legături false. Rețelele de cauzalitate Granger se construiesc pe randamente (staționare) sau cu proceduri gândite pentru serii integrate.",
                "incorrectExplanation": "Problema este intrarea, nu numărul de întârzieri sau de bănci: prețurile băncilor au rădăcină unitară, deci testele pe niveluri resping prea des; aplicați testele pe randamente."
            }
        }
    ]
};

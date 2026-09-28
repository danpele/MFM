// ============================================================
// Quiz bank for chapter id 'realized-vol': Realized Volatility (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['realized-vol'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Definition of realised variance",
                "text": "What is the daily realised variance RV_t?",
                "options": [
                    "The sum of the squared intraday returns of day t",
                    "The squared daily close-to-close return",
                    "The variance forecast of a GARCH model for day t",
                    "The average of the absolute intraday returns"
                ],
                "correctExplanation": "RV_t = sum of r_{t,i}^2 over the M intraday intervals; it measures the day's variance without a model.",
                "incorrectExplanation": "Realised variance adds up the squares of all intraday returns of the day; the squared daily return is the special case with a single return, and a GARCH forecast is a model output."
            },
            "ro": {
                "title": "Definiția varianței realizate",
                "text": "Ce este varianța realizată zilnică RV_t?",
                "options": [
                    "Suma pătratelor randamentelor intraday din ziua t",
                    "Randamentul zilnic închidere-închidere la pătrat",
                    "Prognoza de varianță a unui model GARCH pentru ziua t",
                    "Media randamentelor intraday în valoare absolută"
                ],
                "correctExplanation": "RV_t = suma lui r_{t,i}^2 pe cele M intervale intraday; măsoară varianța zilei fără model.",
                "incorrectExplanation": "Varianța realizată adună pătratele tuturor randamentelor intraday ale zilei; randamentul zilnic la pătrat este cazul particular cu un singur randament, iar prognoza GARCH este rezultatul unui model."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "What RV converges to",
                "text": "Without noise and jumps, as the number of intraday returns grows, RV_t converges to:",
                "options": [
                    "Zero, because each return becomes very small",
                    "The integrated variance, the integral of the spot variance over the day",
                    "The squared daily return",
                    "The unconditional variance of the return series"
                ],
                "correctExplanation": "Barndorff-Nielsen and Shephard: RV_t converges to the quadratic variation, which equals integrated variance when there are no jumps.",
                "incorrectExplanation": "The returns shrink but their number grows; the sum of squares converges to integrated variance, a quantity specific to day t."
            },
            "ro": {
                "title": "Limita RV",
                "text": "Fără zgomot și fără salturi, când numărul de randamente intraday crește, RV_t converge la:",
                "options": [
                    "Zero, deoarece fiecare randament devine foarte mic",
                    "Varianța integrată, integrala varianței instantanee pe durata zilei",
                    "Randamentul zilnic la pătrat",
                    "Varianța necondiționată a seriei de randamente"
                ],
                "correctExplanation": "Barndorff-Nielsen și Shephard: RV_t converge la variația pătratică, egală cu varianța integrată când nu există salturi.",
                "incorrectExplanation": "Randamentele scad, dar numărul lor crește; suma pătratelor converge la varianța integrată, o mărime specifică zilei t."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Precision of RV",
                "text": "With 78 five-minute returns and roughly constant volatility, the relative standard error of RV is about:",
                "options": [
                    "0.1%, since RV is exact",
                    "141%, as for the squared daily return",
                    "16%, since it is close to the square root of 2/M",
                    "50%, whatever M is"
                ],
                "correctExplanation": "se(RV)/RV is approximately the square root of 2/M = 2/78, about 0.16.",
                "incorrectExplanation": "RV is a measurement with error; with M returns its relative error is about the square root of 2/M, which gives 16% for M = 78."
            },
            "ro": {
                "title": "Precizia RV",
                "text": "Cu 78 de randamente de 5 minute și volatilitate aproximativ constantă, eroarea standard relativă a RV este de aproximativ:",
                "options": [
                    "0,1%, deoarece RV este exactă",
                    "141%, ca pentru randamentul zilnic la pătrat",
                    "16%, deoarece este apropiată de rădăcina pătrată din 2/M",
                    "50%, oricare ar fi M"
                ],
                "correctExplanation": "se(RV)/RV este aproximativ rădăcina pătrată din 2/M = 2/78, circa 0,16.",
                "incorrectExplanation": "RV este o măsurare cu eroare; cu M randamente eroarea ei relativă este aproximativ rădăcina pătrată din 2/M, adică 16% pentru M = 78."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Overnight returns",
                "text": "In the chapter, what share of SPY's daily variance comes from the overnight return (close to next open)?",
                "options": [
                    "About 2%",
                    "About 80%",
                    "Exactly 0, since the market is closed",
                    "About 38%"
                ],
                "correctExplanation": "Overnight returns carry about 38% of the daily variance of SPY in 2020-2026, so daily risk uses RV plus the squared overnight return.",
                "incorrectExplanation": "News accumulates while the market is closed and is priced at the open; in the data this is about 38% of the daily variance."
            },
            "ro": {
                "title": "Randamentele peste noapte",
                "text": "În capitol, ce parte din varianța zilnică SPY provine din randamentul peste noapte (de la închidere la deschiderea următoare)?",
                "options": [
                    "Aproximativ 2%",
                    "Aproximativ 80%",
                    "Exact 0, deoarece piața este închisă",
                    "Aproximativ 38%"
                ],
                "correctExplanation": "Randamentele peste noapte aduc aproximativ 38% din varianța zilnică SPY în 2020-2026, deci riscul zilnic folosește RV plus randamentul peste noapte la pătrat.",
                "incorrectExplanation": "Știrile se acumulează cât piața este închisă și sunt încorporate în preț la deschidere; în date aceasta înseamnă aproximativ 38% din varianța zilnică."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Intraday pattern of SPY",
                "text": "How does the volatility of SPY 5-minute returns vary during the trading day?",
                "options": [
                    "U-shape: highest at the open and at the close, lowest around midday",
                    "It is constant during the day",
                    "It rises steadily from the open to the close",
                    "It is highest around midday"
                ],
                "correctExplanation": "The first 5 minutes are about twice as volatile as midday, with a second peak at the close.",
                "incorrectExplanation": "The open prices overnight news and the close concentrates rebalancing: the pattern is a U-shape."
            },
            "ro": {
                "title": "Tiparul intraday pentru SPY",
                "text": "Cum variază volatilitatea randamentelor SPY de 5 minute în cursul zilei?",
                "options": [
                    "Formă de U: cea mai mare la deschidere și la închidere, cea mai mică la prânz",
                    "Este constantă în cursul zilei",
                    "Crește constant de la deschidere la închidere",
                    "Este cea mai mare la prânz"
                ],
                "correctExplanation": "Primele 5 minute sunt de aproximativ două ori mai volatile decât prânzul, cu un al doilea vârf la închidere.",
                "incorrectExplanation": "Deschiderea încorporează știrile de peste noapte, iar închiderea concentrează reechilibrările: tiparul are formă de U."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Noise bias",
                "text": "With i.i.d. microstructure noise of variance omega^2 and n returns per day, the expected RV is:",
                "options": [
                    "IV - 2 n omega^2",
                    "IV + 2 n omega^2",
                    "IV / n",
                    "IV, the noise cancels out"
                ],
                "correctExplanation": "Each observed return contains two noise terms, so noise adds 2 omega^2 per return, 2 n omega^2 in total.",
                "incorrectExplanation": "The noise bias grows with the number of returns: E[RV] = IV + 2 n omega^2, which is why sampling every tick overstates volatility."
            },
            "ro": {
                "title": "Deplasarea din zgomot",
                "text": "Cu zgomot de microstructură i.i.d. de varianță omega^2 și n randamente pe zi, valoarea așteptată a RV este:",
                "options": [
                    "IV - 2 n omega^2",
                    "IV + 2 n omega^2",
                    "IV / n",
                    "IV, zgomotul se anulează"
                ],
                "correctExplanation": "Fiecare randament observat conține doi termeni de zgomot, deci zgomotul adaugă 2 omega^2 pe randament, 2 n omega^2 în total.",
                "incorrectExplanation": "Deplasarea din zgomot crește cu numărul de randamente: E[RV] = IV + 2 n omega^2, de aceea eșantionarea fiecărei tranzacții supraestimează volatilitatea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Signature plot",
                "text": "What does a volatility signature plot show?",
                "options": [
                    "RV as a function of the time of day",
                    "The autocorrelation of RV by lag",
                    "Mean RV as a function of the sampling interval; a rise at high frequency signals noise",
                    "Implied volatility as a function of the strike price"
                ],
                "correctExplanation": "Without noise RV does not depend on the sampling interval; an increase at short intervals is the fingerprint of noise.",
                "incorrectExplanation": "The signature plot puts the sampling interval on the horizontal axis and mean RV on the vertical axis."
            },
            "ro": {
                "title": "Graficul semnăturii",
                "text": "Ce arată graficul semnăturii volatilității?",
                "options": [
                    "RV în funcție de ora din zi",
                    "Autocorelația RV pe întârzieri",
                    "RV medie în funcție de intervalul de eșantionare; o creștere la frecvențe mari semnalează zgomot",
                    "Volatilitatea implicită în funcție de prețul de exercitare"
                ],
                "correctExplanation": "Fără zgomot RV nu depinde de intervalul de eșantionare; o creștere la intervale scurte este amprenta zgomotului.",
                "incorrectExplanation": "Graficul semnăturii pune intervalul de eșantionare pe axa orizontală și RV medie pe axa verticală."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "SPY at 5 minutes",
                "text": "What did the signature plot and the autocorrelation of 5-minute SPY returns show?",
                "options": [
                    "RV at 5 minutes is twice the RV at 30 minutes",
                    "Returns have autocorrelation -0.5, so noise dominates",
                    "RV falls sharply from 5 to 130 minutes",
                    "The plot is flat and the first-order autocorrelation is about -0.01: noise is negligible at 5 minutes"
                ],
                "correctExplanation": "Mean annualised volatility stays between 12.6% and 13.1% from 5 to 130 minutes; noise-robust estimators add nothing at this frequency.",
                "incorrectExplanation": "For a liquid ETF at 5 minutes the noise is invisible: the signature plot is flat and the autocorrelation of returns is almost zero."
            },
            "ro": {
                "title": "SPY la 5 minute",
                "text": "Ce au arătat graficul semnăturii și autocorelația randamentelor SPY de 5 minute?",
                "options": [
                    "RV la 5 minute este dublul RV la 30 de minute",
                    "Randamentele au autocorelație -0,5, deci zgomotul domină",
                    "RV scade puternic de la 5 la 130 de minute",
                    "Graficul este plat, iar autocorelația de ordinul 1 este aproximativ -0,01: zgomotul este neglijabil la 5 minute"
                ],
                "correctExplanation": "Volatilitatea anualizată medie rămâne între 12,6% și 13,1% de la 5 la 130 de minute; estimatorii robuști la zgomot nu aduc nimic la această frecvență.",
                "incorrectExplanation": "Pentru un ETF lichid la 5 minute zgomotul este invizibil: graficul semnăturii este plat, iar autocorelația randamentelor este aproape zero."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Two-scale RV",
                "text": "How does two-scale realised variance correct for noise?",
                "options": [
                    "It averages RV over shifted sparse grids and subtracts a multiple of the all-data RV, which estimates the noise",
                    "It uses only the first and last price of the day",
                    "It multiplies RV by 2",
                    "It drops the largest returns of the day"
                ],
                "correctExplanation": "TSRV = RV_avg - (n_bar/n) RV_all: the all-data RV is dominated by noise and removes the bias of the average.",
                "incorrectExplanation": "Zhang, Mykland and Ait-Sahalia combine a slow scale (average over sparse grids) with a fast scale (all data) to cancel the noise bias."
            },
            "ro": {
                "title": "RV pe două scări",
                "text": "Cum corectează varianța realizată pe două scări zgomotul?",
                "options": [
                    "Face media RV pe grile rare decalate și scade un multiplu al RV din toate datele, care estimează zgomotul",
                    "Folosește doar primul și ultimul preț al zilei",
                    "Înmulțește RV cu 2",
                    "Elimină cele mai mari randamente ale zilei"
                ],
                "correctExplanation": "TSRV = RV_avg - (n_bar/n) RV_all: RV din toate datele este dominată de zgomot și elimină deplasarea mediei.",
                "incorrectExplanation": "Zhang, Mykland și Ait-Sahalia combină o scară lentă (media pe grile rare) cu una rapidă (toate datele) pentru a anula deplasarea din zgomot."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Bipower variation",
                "text": "Why is bipower variation robust to jumps?",
                "options": [
                    "It discards all returns larger than 1%",
                    "A jump enters one return and is multiplied by a small neighbouring return, so its effect vanishes as M grows",
                    "It uses squared returns only",
                    "It is computed from daily returns"
                ],
                "correctExplanation": "BV sums products |r_i||r_{i-1}|; a single large return is multiplied by an ordinary neighbour.",
                "incorrectExplanation": "Products of adjacent absolute returns keep the diffusive variance but not the squared jumps: BV converges to integrated variance."
            },
            "ro": {
                "title": "Variația bipower",
                "text": "De ce este variația bipower robustă la salturi?",
                "options": [
                    "Elimină toate randamentele mai mari de 1%",
                    "Un salt intră într-un singur randament și este înmulțit cu un randament vecin mic, deci efectul lui dispare când M crește",
                    "Folosește doar randamentele la pătrat",
                    "Se calculează din randamente zilnice"
                ],
                "correctExplanation": "BV adună produse |r_i||r_{i-1}|; un singur randament mare este înmulțit cu un vecin obișnuit.",
                "incorrectExplanation": "Produsele randamentelor absolute alăturate păstrează varianța difuzivă, dar nu și salturile la pătrat: BV converge la varianța integrată."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Jumps in SPY",
                "text": "At the 0.1% level, what did the jump test find for SPY in 2020-2026?",
                "options": [
                    "Half of the days have a jump",
                    "No day has a significant jump",
                    "About 2% of days have a significant jump, and jumps are about 3% of total realised variance",
                    "Jumps are about 50% of total variance"
                ],
                "correctExplanation": "35 of 1,489 days are jump days; the jump part is 2.8% of the sum of RV.",
                "incorrectExplanation": "Jumps are rare and carry a small share of variance: 35 jump days, 2.8% of total realised variance."
            },
            "ro": {
                "title": "Salturi în SPY",
                "text": "La nivelul de 0,1%, ce a găsit testul de salturi pentru SPY în 2020-2026?",
                "options": [
                    "Jumătate dintre zile au un salt",
                    "Nicio zi nu are un salt semnificativ",
                    "Aproximativ 2% din zile au un salt semnificativ, iar salturile reprezintă aproximativ 3% din varianța realizată totală",
                    "Salturile reprezintă aproximativ 50% din varianța totală"
                ],
                "correctExplanation": "35 din 1.489 de zile sunt zile cu salt; partea de salt este 2,8% din suma RV.",
                "incorrectExplanation": "Salturile sunt rare și aduc o parte mică din varianță: 35 de zile cu salt, 2,8% din varianța realizată totală."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Multiple testing",
                "text": "The jump test is applied to 1,489 days at the 5% level and rejects on 235 days. What is the main caution?",
                "options": [
                    "235 rejections prove that every such day had a jump",
                    "The test is invalid for daily data",
                    "The 5% level makes false alarms impossible",
                    "About 74 rejections are expected even without any jump, so not every rejection is a news jump"
                ],
                "correctExplanation": "With one test per day, alpha times the number of days are false alarms; a stricter level such as 0.1% keeps them few.",
                "incorrectExplanation": "Testing many days produces false alarms; at 5% about 74 of 1,489 days would reject without jumps."
            },
            "ro": {
                "title": "Testarea multiplă",
                "text": "Testul de salturi se aplică la 1.489 de zile la nivelul de 5% și respinge în 235 de zile. Care este principala precauție?",
                "options": [
                    "235 de respingeri dovedesc că fiecare astfel de zi a avut un salt",
                    "Testul nu este valid pentru date zilnice",
                    "Nivelul de 5% face imposibile alarmele false",
                    "Aproximativ 74 de respingeri sunt așteptate chiar fără salturi, deci nu orice respingere este un salt produs de știri"
                ],
                "correctExplanation": "Cu un test pe zi, alfa înmulțit cu numărul de zile reprezintă alarme false; un nivel mai strict, ca 0,1%, le menține puține.",
                "incorrectExplanation": "Testarea multor zile produce alarme false; la 5% aproximativ 74 din 1.489 de zile ar respinge fără salturi."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Standardised returns",
                "text": "What happens to the kurtosis of SPY open-to-close returns when they are divided by the square root of RV?",
                "options": [
                    "It falls from about 16 to about 2.7, close to the Normal value",
                    "It rises from 3 to 16",
                    "It stays at about 16",
                    "It becomes negative"
                ],
                "correctExplanation": "Scaling by realised volatility removes almost all excess kurtosis: heavy tails come from changing volatility.",
                "incorrectExplanation": "Returns are close to a mixture of Normal distributions with daily variances IV_t; dividing by the square root of RV undoes the mixture."
            },
            "ro": {
                "title": "Randamente standardizate",
                "text": "Ce se întâmplă cu aplatizarea randamentelor SPY deschidere-închidere când sunt împărțite la rădăcina pătrată a RV?",
                "options": [
                    "Scade de la aproximativ 16 la aproximativ 2,7, aproape de valoarea Normală",
                    "Crește de la 3 la 16",
                    "Rămâne la aproximativ 16",
                    "Devine negativă"
                ],
                "correctExplanation": "Scalarea cu volatilitatea realizată elimină aproape toată aplatizarea în exces: cozile grele provin din volatilitatea variabilă.",
                "incorrectExplanation": "Randamentele sunt aproape un amestec de distribuții Normale cu varianțele zilnice IV_t; împărțirea la rădăcina pătrată a RV anulează amestecul."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Distribution of RV",
                "text": "Which transformation of realised variance is close to a Normal distribution?",
                "options": [
                    "RV itself",
                    "The logarithm of RV",
                    "The square of RV",
                    "The inverse of RV"
                ],
                "correctExplanation": "RV has skewness about 20 and kurtosis above 500; log RV has skewness 0.3 and kurtosis 3.2.",
                "incorrectExplanation": "RV is extremely right-skewed; its logarithm is nearly Normal, which is why the chapter models volatility in logs."
            },
            "ro": {
                "title": "Distribuția RV",
                "text": "Ce transformare a varianței realizate este aproape de o distribuție Normală?",
                "options": [
                    "RV însăși",
                    "Logaritmul RV",
                    "Pătratul RV",
                    "Inversul RV"
                ],
                "correctExplanation": "RV are asimetrie de aproximativ 20 și aplatizare peste 500; log RV are asimetrie 0,3 și aplatizare 3,2.",
                "incorrectExplanation": "RV este extrem de asimetrică la dreapta; logaritmul ei este aproape Normal, de aceea capitolul modelează volatilitatea pe log."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Long memory",
                "text": "The autocorrelation of SPY log RV is 0.64 at lag 1 and 0.24 at 22 days. What does this indicate?",
                "options": [
                    "No memory: RV is i.i.d.",
                    "Short memory: an AR(1) fits perfectly",
                    "Long memory: autocorrelations decay much more slowly than in an AR(1)",
                    "A negative trend in volatility"
                ],
                "correctExplanation": "An AR(1) with 0.64 would give about 0.00005 at lag 22; the observed 0.24 shows slow, hyperbolic-like decay.",
                "incorrectExplanation": "Volatility shocks persist for months; the autocorrelation at one month is still far from zero."
            },
            "ro": {
                "title": "Memoria lungă",
                "text": "Autocorelația log RV pentru SPY este 0,64 la întârzierea 1 și 0,24 la 22 de zile. Ce indică acest lucru?",
                "options": [
                    "Lipsa memoriei: RV este i.i.d.",
                    "Memorie scurtă: un AR(1) se potrivește perfect",
                    "Memorie lungă: autocorelațiile scad mult mai lent decât la un AR(1)",
                    "O tendință negativă a volatilității"
                ],
                "correctExplanation": "Un AR(1) cu 0,64 ar da aproximativ 0,00005 la întârzierea 22; valoarea observată 0,24 arată o scădere lentă.",
                "incorrectExplanation": "Șocurile de volatilitate persistă luni de zile; autocorelația la o lună este încă departe de zero."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Bitcoin weekly cycle",
                "text": "What pattern did the chapter find in Bitcoin realised volatility?",
                "options": [
                    "No calendar pattern, because Bitcoin trades every day",
                    "Weekends are twice as volatile as weekdays",
                    "Volatility is highest at midnight UTC every day",
                    "A weekly cycle: weekend RV is about 40% of weekday RV"
                ],
                "correctExplanation": "The autocorrelation of log RV peaks at 7, 14, 21 days; Saturday volatility is about 27% p.a. vs 48% on Wednesday.",
                "incorrectExplanation": "Bitcoin trades 24/7, but weekends lack equity and macro news and institutional traders: they are much calmer."
            },
            "ro": {
                "title": "Ciclul săptămânal Bitcoin",
                "text": "Ce tipar a găsit capitolul în volatilitatea realizată Bitcoin?",
                "options": [
                    "Niciun tipar de calendar, deoarece Bitcoin se tranzacționează zilnic",
                    "Weekendurile sunt de două ori mai volatile decât zilele lucrătoare",
                    "Volatilitatea este cea mai mare la miezul nopții UTC în fiecare zi",
                    "Un ciclu săptămânal: RV de weekend este aproximativ 40% din RV din zilele lucrătoare"
                ],
                "correctExplanation": "Autocorelația log RV are vârfuri la 7, 14, 21 de zile; volatilitatea de sâmbătă este aproximativ 27% pe an față de 48% miercurea.",
                "incorrectExplanation": "Bitcoin se tranzacționează non-stop, dar weekendurile nu au știri bursiere sau macro și investitori instituționali: sunt mult mai calme."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Variance risk premium",
                "text": "On average, how does VIX compare with the SPY volatility realised over the following month?",
                "options": [
                    "VIX is higher: investors pay a premium to insure against volatility",
                    "VIX is lower, by about 4 points",
                    "They are exactly equal on average",
                    "VIX is unrelated to future volatility"
                ],
                "correctExplanation": "Mean VIX 19.5 vs 15.2 realised; VIX was above realised volatility on about 88% of days.",
                "incorrectExplanation": "Implied volatility contains the variance risk premium, so it is an upward-biased forecast of realised volatility."
            },
            "ro": {
                "title": "Prima de risc a varianței",
                "text": "În medie, cum se compară VIX cu volatilitatea SPY realizată în luna următoare?",
                "options": [
                    "VIX este mai mare: investitorii plătesc o primă pentru a se asigura împotriva volatilității",
                    "VIX este mai mic, cu aproximativ 4 puncte",
                    "Sunt exact egale în medie",
                    "VIX nu are legătură cu volatilitatea viitoare"
                ],
                "correctExplanation": "VIX mediu 19,5 față de 15,2 realizată; VIX a depășit volatilitatea realizată în aproximativ 88% din zile.",
                "incorrectExplanation": "Volatilitatea implicită conține prima de risc a varianței, deci este o prognoză deplasată în sus a volatilității realizate."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "HAR-RV",
                "text": "In the HAR-RV model of Corsi, tomorrow's RV is regressed on:",
                "options": [
                    "Only today's squared return",
                    "Today's RV and the averages of RV over the last week and the last month",
                    "The last 22 daily RVs, each with its own free coefficient",
                    "The VIX index only"
                ],
                "correctExplanation": "HAR uses three regressors (day, week, month): a restricted AR(22) that mimics long memory.",
                "incorrectExplanation": "The heterogeneous market idea: traders at daily, weekly and monthly horizons; three averages of past RV."
            },
            "ro": {
                "title": "HAR-RV",
                "text": "În modelul HAR-RV al lui Corsi, RV de mâine este regresată pe:",
                "options": [
                    "Doar randamentul de azi la pătrat",
                    "RV de azi și mediile RV din ultima săptămână și din ultima lună",
                    "Ultimele 22 de valori RV zilnice, fiecare cu propriul coeficient liber",
                    "Doar indicele VIX"
                ],
                "correctExplanation": "HAR folosește trei regresori (zi, săptămână, lună): un AR(22) restricționat care imită memoria lungă.",
                "incorrectExplanation": "Ideea pieței eterogene: investitori pe orizonturi zilnice, săptămânale și lunare; trei medii ale RV trecute."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "HAR lag weights",
                "text": "In HAR with coefficients beta_d, beta_w, beta_m, what weight does lag 10 receive?",
                "options": [
                    "beta_d + beta_w/5 + beta_m/22",
                    "beta_w/5 + beta_m/22",
                    "beta_m / 22",
                    "Zero"
                ],
                "correctExplanation": "Lag 10 is outside the week but inside the month, so only the monthly average contributes: beta_m/22.",
                "incorrectExplanation": "Lag 1 gets all three terms, lags 2-5 get the weekly and monthly terms, lags 6-22 only the monthly term."
            },
            "ro": {
                "title": "Ponderile HAR pe întârzieri",
                "text": "Într-un HAR cu coeficienții beta_d, beta_w, beta_m, ce pondere primește întârzierea 10?",
                "options": [
                    "beta_d + beta_w/5 + beta_m/22",
                    "beta_w/5 + beta_m/22",
                    "beta_m / 22",
                    "Zero"
                ],
                "correctExplanation": "Întârzierea 10 este în afara săptămânii, dar în interiorul lunii, deci contribuie doar media lunară: beta_m/22.",
                "incorrectExplanation": "Întârzierea 1 primește toți cei trei termeni, întârzierile 2-5 termenii săptămânal și lunar, întârzierile 6-22 doar termenul lunar."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Robust loss functions",
                "text": "Why is QLIKE (or MSE on variance) used to compare volatility forecasts against RV?",
                "options": [
                    "They are the only losses that are always positive",
                    "They ignore the largest days",
                    "They do not require a proxy",
                    "They rank forecasts the same way with a noisy unbiased proxy as with the true variance"
                ],
                "correctExplanation": "Patton (2011): QLIKE and MSE on variance are robust to noise in the proxy; MAE or MSE on volatility are not.",
                "incorrectExplanation": "True variance is unobserved; only robust losses give a correct ranking when RV replaces it."
            },
            "ro": {
                "title": "Funcții de pierdere robuste",
                "text": "De ce se folosește QLIKE (sau MSE pe varianță) pentru a compara prognozele de volatilitate cu RV?",
                "options": [
                    "Sunt singurele funcții de pierdere întotdeauna pozitive",
                    "Ignoră zilele cele mai mari",
                    "Nu necesită un proxy",
                    "Ordonează prognozele la fel cu un proxy zgomotos nedeplasat ca și cu varianța adevărată"
                ],
                "correctExplanation": "Patton (2011): QLIKE și MSE pe varianță sunt robuste la zgomotul din proxy; MAE sau MSE pe volatilitate nu sunt.",
                "incorrectExplanation": "Varianța adevărată nu este observată; doar funcțiile de pierdere robuste dau o ordonare corectă când RV o înlocuiește."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "QLIKE asymmetry",
                "text": "With true variance 1, which forecast has the larger QLIKE loss?",
                "options": [
                    "0.5, because QLIKE punishes under-prediction more",
                    "2.0, because QLIKE punishes over-prediction more",
                    "Both have the same loss",
                    "Neither, since QLIKE is zero for all forecasts"
                ],
                "correctExplanation": "QLIKE is 0.307 for 0.5 and 0.193 for 2.0: under-predicting risk costs more.",
                "incorrectExplanation": "QLIKE = RV/F - log(RV/F) - 1 grows quickly when F is too small; MSE would rank the two the other way."
            },
            "ro": {
                "title": "Asimetria QLIKE",
                "text": "Cu varianța adevărată 1, ce prognoză are pierderea QLIKE mai mare?",
                "options": [
                    "0,5, deoarece QLIKE penalizează mai mult subestimarea",
                    "2,0, deoarece QLIKE penalizează mai mult supraestimarea",
                    "Ambele au aceeași pierdere",
                    "Niciuna, deoarece QLIKE este zero pentru toate prognozele"
                ],
                "correctExplanation": "QLIKE este 0,307 pentru 0,5 și 0,193 pentru 2,0: subestimarea riscului costă mai mult.",
                "incorrectExplanation": "QLIKE = RV/F - log(RV/F) - 1 crește rapid când F este prea mic; MSE ar ordona cele două invers."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "HAR vs GARCH for SPY",
                "text": "Out of sample for SPY in 2022-2026, how did log-HAR compare with GARCH(1,1)-t?",
                "options": [
                    "GARCH was significantly better on every loss",
                    "log-HAR had about 10% lower QLIKE, significant at 5% (DM t about -2.3)",
                    "They were identical",
                    "log-HAR was better only on MSE, significantly"
                ],
                "correctExplanation": "QLIKE 0.310 vs 0.343; the MSE difference was not significant.",
                "incorrectExplanation": "Intraday information helps: log-HAR beats GARCH under QLIKE; MSE rankings depend on a few crisis days."
            },
            "ro": {
                "title": "HAR vs GARCH pentru SPY",
                "text": "În afara eșantionului pentru SPY în 2022-2026, cum s-a comparat log-HAR cu GARCH(1,1)-t?",
                "options": [
                    "GARCH a fost semnificativ mai bun după fiecare funcție de pierdere",
                    "log-HAR a avut un QLIKE cu aproximativ 10% mai mic, semnificativ la 5% (DM t aproximativ -2,3)",
                    "Au fost identice",
                    "log-HAR a fost mai bun doar după MSE, semnificativ"
                ],
                "correctExplanation": "QLIKE 0,310 față de 0,343; diferența MSE nu a fost semnificativă.",
                "incorrectExplanation": "Informația intraday ajută: log-HAR întrece GARCH după QLIKE; clasamentele după MSE depind de câteva zile de criză."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Mincer-Zarnowitz regression",
                "text": "In the regression RV_t = a + b F_t + u_t, an unbiased forecast has:",
                "options": [
                    "a = 1 and b = 0",
                    "a = 0 and b = 0",
                    "a = 0 and b = 1",
                    "R^2 = 1"
                ],
                "correctExplanation": "Unbiasedness means the realised value equals the forecast on average for every level of the forecast.",
                "incorrectExplanation": "The joint Wald test of a = 0, b = 1 checks bias; R^2 measures informativeness and is capped by noise in RV."
            },
            "ro": {
                "title": "Regresia Mincer-Zarnowitz",
                "text": "În regresia RV_t = a + b F_t + u_t, o prognoză nedeplasată are:",
                "options": [
                    "a = 1 și b = 0",
                    "a = 0 și b = 0",
                    "a = 0 și b = 1",
                    "R^2 = 1"
                ],
                "correctExplanation": "Nedeplasarea înseamnă că valoarea realizată este în medie egală cu prognoza pentru orice nivel al prognozei.",
                "incorrectExplanation": "Testul Wald comun a = 0, b = 1 verifică deplasarea; R^2 măsoară conținutul informațional și este limitat de zgomotul din RV."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Rough volatility",
                "text": "The chapter estimates the Hurst exponent H of log volatility at about 0.1. What does H < 0.5 mean?",
                "options": [
                    "Volatility is smoother than a Brownian motion and trends",
                    "Volatility is constant",
                    "Volatility is a random walk with H exactly 0.5",
                    "Log volatility is rougher than a Brownian motion: its increments are negatively correlated"
                ],
                "correctExplanation": "H = 0.5 is Brownian motion; H about 0.1 means very rough paths (Gatheral, Jaisson and Rosenbaum); measurement error in RV can push H down.",
                "incorrectExplanation": "Roughness means H well below 0.5; the chapter finds 0.11 for SPY and 0.08 for Bitcoin, with a caution about measurement error."
            },
            "ro": {
                "title": "Volatilitatea aspră",
                "text": "Capitolul estimează exponentul Hurst H al log-volatilității la aproximativ 0,1. Ce înseamnă H < 0,5?",
                "options": [
                    "Volatilitatea este mai netedă decât o mișcare browniană și are tendință",
                    "Volatilitatea este constantă",
                    "Volatilitatea este un mers aleator cu H exact 0,5",
                    "Log-volatilitatea este mai aspră decât o mișcare browniană: incrementele ei sunt corelate negativ"
                ],
                "correctExplanation": "H = 0,5 este mișcarea browniană; H aproximativ 0,1 înseamnă traiectorii foarte aspre (Gatheral, Jaisson și Rosenbaum); eroarea de măsurare din RV poate coborî H.",
                "incorrectExplanation": "Asprimea înseamnă H mult sub 0,5; capitolul găsește 0,11 pentru SPY și 0,08 pentru Bitcoin, cu precauția privind eroarea de măsurare."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the AI error: annualising RV",
                "text": "An AI assistant writes: \"A daily realised variance of 1.0e-4 corresponds to an annualised volatility of sqrt(1.0e-4) x 252 = 2.52, i.e. 252%.\" What is wrong?",
                "options": [
                    "SPY must be annualised with 365 days, not 252",
                    "Realised variance cannot be annualised at all",
                    "The daily RV must first be divided by 252",
                    "Volatility scales with the square root of time: sqrt(252 x 1.0e-4) = 15.9%"
                ],
                "correctExplanation": "Variance grows in proportion to time and volatility with its square root, so the annual volatility is sqrt(252 x RV) = 15.9%. The 252% figure should also fail a plausibility check: the VIX is usually between 12 and 30.",
                "incorrectExplanation": "Multiplying a daily volatility by 252 treats volatility as if it grew linearly with time; only the variance does."
            },
            "ro": {
                "title": "Găsiți eroarea AI: anualizarea RV",
                "text": "Un asistent AI scrie: „O varianță realizată zilnică de 1,0e-4 corespunde unei volatilități anualizate de sqrt(1,0e-4) x 252 = 2,52, adică 252%.” Ce este greșit?",
                "options": [
                    "SPY trebuie anualizat cu 365 de zile, nu cu 252",
                    "Varianța realizată nu poate fi anualizată deloc",
                    "RV zilnică trebuie mai întâi împărțită la 252",
                    "Volatilitatea crește cu rădăcina pătrată a timpului: sqrt(252 x 1,0e-4) = 15,9%"
                ],
                "correctExplanation": "Varianța crește proporțional cu timpul, iar volatilitatea cu rădăcina lui pătrată, deci volatilitatea anuală este sqrt(252 x RV) = 15,9%. Cifra de 252% ar trebui să pice și testul de plauzibilitate: VIX este de obicei între 12 și 30.",
                "incorrectExplanation": "Înmulțirea unei volatilități zilnice cu 252 tratează volatilitatea ca și cum ar crește liniar cu timpul; doar varianța crește astfel."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: sampling every tick",
                "text": "An AI assistant writes: \"For SPY, sum the squared returns at every tick: the more intraday returns, the smaller the error of the realised variance, so tick-by-tick sampling is always best.\" What is wrong?",
                "options": [
                    "Microstructure noise: with noise variance omega^2, E[RV] = IV + 2n omega^2, so the bias grows with the number of returns n; sample every 1-5 minutes or use a noise-robust estimator",
                    "Realised variance should use absolute returns, not squared returns",
                    "Tick data are too few to estimate a daily variance",
                    "Squared returns must be computed from simple returns, never from log returns"
                ],
                "correctExplanation": "Bid-ask bounce and price discreteness add noise to every observed price. Its contribution 2n omega^2 grows with the sampling frequency, which is why the signature plot rises at short intervals (Bandi and Russell, 2008; Zhang, Mykland and Ait-Sahalia, 2005).",
                "incorrectExplanation": "More returns reduce the error only for a noise-free price; with microstructure noise the bias of RV grows with the number of returns."
            },
            "ro": {
                "title": "Găsiți eroarea AI: eșantionarea fiecărei tranzacții",
                "text": "Un asistent AI scrie: „Pentru SPY, adunați pătratele randamentelor la fiecare tranzacție: cu cât sunt mai multe randamente intraday, cu atât eroarea varianței realizate este mai mică, deci eșantionarea tranzacție cu tranzacție este întotdeauna cea mai bună.” Ce este greșit?",
                "options": [
                    "Zgomotul de microstructură: cu un zgomot de varianță omega^2, E[RV] = IV + 2n omega^2, deci deplasarea crește cu numărul de randamente n; eșantionați la 1-5 minute sau folosiți un estimator robust la zgomot",
                    "Varianța realizată ar trebui să folosească randamente absolute, nu pătratele lor",
                    "Datele pe tranzacții sunt prea puține pentru a estima o varianță zilnică",
                    "Pătratele randamentelor trebuie calculate din randamente simple, niciodată din randamente log"
                ],
                "correctExplanation": "Oscilația bid-ask și discretizarea prețului adaugă zgomot fiecărui preț observat. Contribuția lui, 2n omega^2, crește cu frecvența de eșantionare, de aceea graficul semnăturii urcă la intervale scurte (Bandi și Russell, 2008; Zhang, Mykland și Ait-Sahalia, 2005).",
                "incorrectExplanation": "Mai multe randamente reduc eroarea doar pentru un preț fără zgomot; cu zgomot de microstructură, deplasarea RV crește cu numărul de randamente."
            }
        }
    ]
};

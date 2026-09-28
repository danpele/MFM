// ============================================================
// Quiz bank for chapter id 'options': Options and the Volatility Surface (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['options'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Put-call parity",
                "text": "For European options on a stock without dividends, which relation always holds?",
                "options": [
                    "C - P = S - K e^{-r tau}",
                    "C + P = S + K",
                    "C = P for at-the-money options with any interest rate",
                    "C - P = K - S"
                ],
                "correctExplanation": "Call plus cash K e^{-r tau} and put plus one share pay max(S_T, K) in every state, so they cost the same today.",
                "incorrectExplanation": "Parity compares two portfolios with identical pay-offs: a call plus the present value of K, and a put plus the share."
            },
            "ro": {
                "title": "Paritatea put-call",
                "text": "Pentru opțiuni europene pe o acțiune fără dividende, ce relație este mereu adevărată?",
                "options": [
                    "C - P = S - K e^{-r tau}",
                    "C + P = S + K",
                    "C = P pentru opțiuni la bani, cu orice rată a dobânzii",
                    "C - P = K - S"
                ],
                "correctExplanation": "Call-ul plus numerarul K e^{-r tau} și put-ul plus o acțiune plătesc max(S_T, K) în orice stare, deci costă la fel azi.",
                "incorrectExplanation": "Paritatea compară două portofolii cu plăți identice: un call plus valoarea actualizată a lui K și un put plus acțiunea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Risk-neutral probability",
                "text": "In a one-period binomial tree with S = 100, uS = 120, dS = 90 and gross risk-free return R = 1.05, what is the risk-neutral probability of the up move?",
                "options": [
                    "0.60",
                    "0.35",
                    "0.50",
                    "It depends on the investors' expected return"
                ],
                "correctExplanation": "q = (R - d)/(u - d) = (1.05 - 0.9)/(1.2 - 0.9) = 0.5; under q the stock earns exactly the risk-free rate.",
                "incorrectExplanation": "The risk-neutral probability is fixed by no-arbitrage, q = (R - d)/(u - d); the real probability and expected return do not enter."
            },
            "ro": {
                "title": "Probabilitatea neutră la risc",
                "text": "Într-un arbore binomial cu o perioadă, cu S = 100, uS = 120, dS = 90 și randamentul brut fără risc R = 1,05, care este probabilitatea neutră la risc a creșterii?",
                "options": [
                    "0,60",
                    "0,35",
                    "0,50",
                    "Depinde de randamentul așteptat al investitorilor"
                ],
                "correctExplanation": "q = (R - d)/(u - d) = (1,05 - 0,9)/(1,2 - 0,9) = 0,5; sub q acțiunea câștigă exact rata fără risc.",
                "incorrectExplanation": "Probabilitatea neutră la risc este fixată de absența arbitrajului, q = (R - d)/(u - d); probabilitatea reală și randamentul așteptat nu intervin."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Early exercise",
                "text": "Which American option may be optimally exercised before expiry, even without dividends?",
                "options": [
                    "A call on a stock without dividends",
                    "Any option that is out of the money",
                    "None: early exercise is never optimal",
                    "A put that is deep in the money"
                ],
                "correctExplanation": "Deep in the money, receiving K now and earning interest on it can be worth more than keeping the put alive.",
                "incorrectExplanation": "A call on a stock without dividends is worth more alive than exercised (at least S - K e^{-r tau}); for puts the interest on K makes early exercise valuable."
            },
            "ro": {
                "title": "Exercitarea anticipată",
                "text": "Ce opțiune americană poate fi exercitată optim înainte de scadență, chiar fără dividende?",
                "options": [
                    "Un call pe o acțiune fără dividende",
                    "Orice opțiune în afara banilor",
                    "Niciuna: exercitarea anticipată nu este niciodată optimă",
                    "Un put adânc în bani"
                ],
                "correctExplanation": "Adânc în bani, a încasa K acum și a câștiga dobânda poate valora mai mult decât a păstra put-ul.",
                "incorrectExplanation": "Un call pe o acțiune fără dividende valorează mai mult nevândut decât exercitat (cel puțin S - K e^{-r tau}); la put-uri dobânda la K face valoroasă exercitarea anticipată."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Reading N(d2)",
                "text": "In the Black-Scholes call formula C = S N(d1) - K e^{-r tau} N(d2), what is N(d2)?",
                "options": [
                    "The real-world probability that the call ends in the money",
                    "The risk-neutral probability that the call ends in the money",
                    "The delta of the call",
                    "The probability that the stock price doubles"
                ],
                "correctExplanation": "N(d2) is the risk-neutral probability of exercise; N(d1) is the delta.",
                "incorrectExplanation": "Black-Scholes prices under the risk-neutral measure, so N(d2) is a risk-neutral probability, not a forecast; the delta is N(d1)."
            },
            "ro": {
                "title": "Citirea lui N(d2)",
                "text": "În formula call-ului Black-Scholes C = S N(d1) - K e^{-r tau} N(d2), ce este N(d2)?",
                "options": [
                    "Probabilitatea reală ca call-ul să se termine în bani",
                    "Probabilitatea neutră la risc ca call-ul să se termine în bani",
                    "Delta call-ului",
                    "Probabilitatea ca prețul acțiunii să se dubleze"
                ],
                "correctExplanation": "N(d2) este probabilitatea neutră la risc de exercitare; N(d1) este delta.",
                "incorrectExplanation": "Black-Scholes evaluează sub măsura neutră la risc, deci N(d2) este o probabilitate neutră la risc, nu o prognoză; delta este N(d1)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Gamma near expiry",
                "text": "How does the gamma of an at-the-money option change as expiry approaches?",
                "options": [
                    "It falls to zero",
                    "It stays constant",
                    "It explodes: one day before expiry it is about sqrt(21) times its value one month before",
                    "It becomes negative"
                ],
                "correctExplanation": "ATM gamma is proportional to 1/(sigma sqrt(tau)): with 1 day instead of 21 trading days it is about 4.6 times larger.",
                "incorrectExplanation": "Gamma of an at-the-money option grows like 1/sqrt(tau), which is why hedging options close to expiry is so demanding."
            },
            "ro": {
                "title": "Gamma aproape de scadență",
                "text": "Cum se schimbă gamma unei opțiuni la bani când se apropie scadența?",
                "options": [
                    "Scade la zero",
                    "Rămâne constantă",
                    "Explodează: cu o zi înainte de scadență este de aproximativ sqrt(21) ori valoarea de cu o lună înainte",
                    "Devine negativă"
                ],
                "correctExplanation": "Gamma ATM este proporțională cu 1/(sigma sqrt(tau)): cu o zi în loc de 21 de zile de tranzacționare este de aproximativ 4,6 ori mai mare.",
                "incorrectExplanation": "Gamma unei opțiuni la bani crește ca 1/sqrt(tau), motiv pentru care acoperirea opțiunilor aproape de scadență este atât de solicitantă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Theta and gamma",
                "text": "For a delta-hedged option position under Black-Scholes, what is the link between theta and gamma?",
                "options": [
                    "They are unrelated",
                    "Theta equals gamma",
                    "Both are always positive for a long option",
                    "Theta + 0.5 sigma^2 S^2 Gamma + r S Delta - r C = 0: long gamma is paid for by time decay"
                ],
                "correctExplanation": "This is the Black-Scholes partial differential equation; a long-gamma position loses time value, a short-gamma one earns it.",
                "incorrectExplanation": "The Black-Scholes equation ties theta to gamma: the holder of convexity pays for it through time decay."
            },
            "ro": {
                "title": "Theta și gamma",
                "text": "Pentru o poziție în opțiuni acoperită delta, în modelul Black-Scholes, care este legătura dintre theta și gamma?",
                "options": [
                    "Nu sunt legate",
                    "Theta este egală cu gamma",
                    "Ambele sunt mereu pozitive pentru o opțiune cumpărată",
                    "Theta + 0,5 sigma^2 S^2 Gamma + r S Delta - r C = 0: gamma pozitivă se plătește prin erodarea în timp"
                ],
                "correctExplanation": "Aceasta este ecuația cu derivate parțiale Black-Scholes; o poziție cu gamma pozitivă pierde valoare în timp, una cu gamma negativă o câștigă.",
                "incorrectExplanation": "Ecuația Black-Scholes leagă theta de gamma: deținătorul convexității o plătește prin erodarea în timp."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Hedging frequency",
                "text": "In the lecture simulation the standard deviation of the hedging error falls with the number of rebalancings N with a log-log slope of -0.48. What does this imply?",
                "options": [
                    "The error shrinks like 1/sqrt(N): four times more rebalancings roughly halve it",
                    "The error shrinks like 1/N",
                    "Rebalancing more often does not help",
                    "The error grows with N because of rounding"
                ],
                "correctExplanation": "A slope close to -1/2 means error proportional to 1/sqrt(N): daily hedging left about 9.5% of the premium, four times a day about 4.8%.",
                "incorrectExplanation": "The slope of about -1/2 on a log-log scale means the error is proportional to 1/sqrt(N), not to 1/N."
            },
            "ro": {
                "title": "Frecvența acoperirii",
                "text": "În simularea din curs, abaterea standard a erorii de acoperire scade cu numărul de reechilibrări N cu o pantă log-log de -0,48. Ce implică acest lucru?",
                "options": [
                    "Eroarea scade ca 1/sqrt(N): de patru ori mai multe reechilibrări o înjumătățesc aproximativ",
                    "Eroarea scade ca 1/N",
                    "Reechilibrarea mai deasă nu ajută",
                    "Eroarea crește cu N din cauza rotunjirilor"
                ],
                "correctExplanation": "O pantă apropiată de -1/2 înseamnă o eroare proporțională cu 1/sqrt(N): acoperirea zilnică a lăsat aproximativ 9,5% din primă, de patru ori pe zi aproximativ 4,8%.",
                "incorrectExplanation": "Panta de aproximativ -1/2 pe scară log-log înseamnă o eroare proporțională cu 1/sqrt(N), nu cu 1/N."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Selling volatility",
                "text": "A dealer sells a call at 20% implied volatility and hedges it daily. Realised volatility turns out to be 25%. What is the expected result?",
                "options": [
                    "A profit, because the premium was collected",
                    "A loss of roughly vega times 5 volatility points",
                    "Zero, because the position is delta-hedged",
                    "A profit equal to theta times the number of days"
                ],
                "correctExplanation": "A delta-hedged option earns implied minus realised variance weighted by gamma: with realised above implied the seller loses about vega x 5 points.",
                "incorrectExplanation": "Delta hedging removes the directional exposure, not the volatility exposure: the seller loses when realised volatility exceeds the implied one."
            },
            "ro": {
                "title": "Vânzarea volatilității",
                "text": "Un dealer vinde un call la volatilitatea implicită de 20% și îl acoperă zilnic. Volatilitatea realizată se dovedește a fi 25%. Care este rezultatul așteptat?",
                "options": [
                    "Un profit, pentru că prima a fost încasată",
                    "O pierdere de aproximativ vega înmulțită cu 5 puncte de volatilitate",
                    "Zero, pentru că poziția este acoperită delta",
                    "Un profit egal cu theta înmulțită cu numărul de zile"
                ],
                "correctExplanation": "O opțiune acoperită delta câștigă varianța implicită minus cea realizată, ponderată cu gamma: cu realizata peste implicită, vânzătorul pierde aproximativ vega x 5 puncte.",
                "incorrectExplanation": "Acoperirea delta elimină expunerea la direcție, nu expunerea la volatilitate: vânzătorul pierde când volatilitatea realizată o depășește pe cea implicită."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Delta-hedged S&P 500 options",
                "text": "Selling one-month at-the-money S&P 500 calls at the VIX and hedging them daily, 1990-2026, gave a mean monthly P&L of 0.48% of the index. Why?",
                "options": [
                    "Because the S&P 500 rose on average",
                    "Because of interest earned on the cash account",
                    "Because the VIX was above the volatility realised afterwards in most months: a volatility risk premium",
                    "Because of a coding convention that ignores losses"
                ],
                "correctExplanation": "The VIX exceeded the realised volatility of the month in 85% of months: option sellers earn a premium for insuring against turbulence.",
                "incorrectExplanation": "A delta-hedged option does not bet on direction; its average gain is the gap between implied and realised volatility, the volatility risk premium."
            },
            "ro": {
                "title": "Opțiuni S&P 500 acoperite delta",
                "text": "Vânzarea de call-uri S&P 500 la bani pe o lună la VIX, acoperite zilnic, 1990-2026, a dat un rezultat lunar mediu de 0,48% din indice. De ce?",
                "options": [
                    "Pentru că S&P 500 a crescut în medie",
                    "Din cauza dobânzii la contul de numerar",
                    "Pentru că VIX a fost peste volatilitatea realizată ulterior în majoritatea lunilor: o primă de risc a volatilității",
                    "Din cauza unei convenții de calcul care ignoră pierderile"
                ],
                "correctExplanation": "VIX a depășit volatilitatea realizată a lunii în 85% din luni: vânzătorii de opțiuni încasează o primă pentru asigurarea împotriva turbulențelor.",
                "incorrectExplanation": "O opțiune acoperită delta nu pariază pe direcție; câștigul ei mediu este diferența dintre volatilitatea implicită și cea realizată, prima de risc a volatilității."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Implied volatility",
                "text": "What is the implied volatility of an option?",
                "options": [
                    "The historical standard deviation of the underlying",
                    "The volatility forecast of a GARCH model",
                    "The average volatility of all options on the same asset",
                    "The sigma that makes the Black-Scholes price equal to the market price"
                ],
                "correctExplanation": "Implied volatility inverts the Black-Scholes formula; it is unique because the price increases in sigma (vega > 0).",
                "incorrectExplanation": "Implied volatility is read from the market price of the option, not estimated from past returns."
            },
            "ro": {
                "title": "Volatilitatea implicită",
                "text": "Ce este volatilitatea implicită a unei opțiuni?",
                "options": [
                    "Abaterea standard istorică a activului suport",
                    "Prognoza de volatilitate a unui model GARCH",
                    "Volatilitatea medie a tuturor opțiunilor pe același activ",
                    "Acel sigma pentru care prețul Black-Scholes este egal cu prețul de piață"
                ],
                "correctExplanation": "Volatilitatea implicită inversează formula Black-Scholes; este unică pentru că prețul crește în sigma (vega > 0).",
                "incorrectExplanation": "Volatilitatea implicită se citește din prețul de piață al opțiunii, nu se estimează din randamentele trecute."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Equity skew",
                "text": "Why are low-strike puts on stock indices more expensive in implied-volatility terms than at-the-money options?",
                "options": [
                    "Fat left tails, volatility rising when prices fall, and demand for crash insurance",
                    "Because puts always cost more than calls",
                    "Because of the interest rate",
                    "Because Black-Scholes assumes negative skewness"
                ],
                "correctExplanation": "Heavy left tails, the leverage effect and the premium for crash risk all raise the price of low-strike puts.",
                "incorrectExplanation": "The skew is not a feature of Black-Scholes, which implies a flat smile; it comes from the return distribution and from risk premia."
            },
            "ro": {
                "title": "Asimetria acțiunilor",
                "text": "De ce put-urile cu preț de exercitare mic pe indici bursieri sunt mai scumpe, în volatilitate implicită, decât opțiunile la bani?",
                "options": [
                    "Cozi stângi groase, volatilitate care crește când prețurile scad și cererea de asigurare împotriva prăbușirilor",
                    "Pentru că put-urile costă întotdeauna mai mult decât call-urile",
                    "Din cauza ratei dobânzii",
                    "Pentru că Black-Scholes presupune asimetrie negativă"
                ],
                "correctExplanation": "Cozile stângi grele, efectul de levier și prima pentru riscul de prăbușire ridică toate prețul put-urilor cu preț de exercitare mic.",
                "incorrectExplanation": "Asimetria nu este o proprietate a modelului Black-Scholes, care implică un zâmbet plat; ea vine din distribuția randamentelor și din primele de risc."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Leverage effect",
                "text": "The daily correlation between S&P 500 returns and VIX changes was -0.79 over 1990-2026. What does it mean?",
                "options": [
                    "Implied volatility is independent of prices",
                    "Implied volatility tends to rise when the market falls",
                    "The VIX predicts next month's return",
                    "The VIX rises when the market rises"
                ],
                "correctExplanation": "A strongly negative correlation: falling prices come with rising volatility, the negative rho of the Heston model.",
                "incorrectExplanation": "The sign is negative: the VIX goes up on down days, which is why puts hedge both the fall and the volatility spike."
            },
            "ro": {
                "title": "Efectul de levier",
                "text": "Corelația zilnică dintre randamentele S&P 500 și variațiile VIX a fost -0,79 în 1990-2026. Ce înseamnă?",
                "options": [
                    "Volatilitatea implicită este independentă de prețuri",
                    "Volatilitatea implicită tinde să crească atunci când piața scade",
                    "VIX prognozează randamentul lunii următoare",
                    "VIX crește când piața crește"
                ],
                "correctExplanation": "O corelație puternic negativă: prețurile în scădere vin cu volatilitate în creștere, rho negativ din modelul Heston.",
                "incorrectExplanation": "Semnul este negativ: VIX crește în zilele de scădere, motiv pentru care put-urile acoperă și scăderea, și saltul volatilității."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Bitcoin smile",
                "text": "In the Deribit snapshot of the lecture, how does the Bitcoin smile differ from the typical equity-index skew?",
                "options": [
                    "It is perfectly flat",
                    "Only calls have high implied volatility",
                    "Both wings rise: out-of-the-money calls and puts are both expensive",
                    "Implied volatility falls for all strikes away from the money"
                ],
                "correctExplanation": "Bitcoin can jump up as well as down, so the smile has two rising wings; the equity skew is mostly one-sided.",
                "incorrectExplanation": "The Bitcoin smile is a true smile, with both wings above the at-the-money level, unlike the one-sided equity skew."
            },
            "ro": {
                "title": "Zâmbetul Bitcoin",
                "text": "În instantaneul Deribit din curs, cum diferă zâmbetul Bitcoin de asimetria tipică a indicilor bursieri?",
                "options": [
                    "Este perfect plat",
                    "Doar call-urile au volatilitate implicită mare",
                    "Ambele aripi cresc: atât call-urile, cât și put-urile în afara banilor sunt scumpe",
                    "Volatilitatea implicită scade pentru toate prețurile de exercitare depărtate de bani"
                ],
                "correctExplanation": "Bitcoin poate sări atât în sus, cât și în jos, deci zâmbetul are două aripi crescătoare; asimetria acțiunilor este în mare parte unilaterală.",
                "incorrectExplanation": "Zâmbetul Bitcoin este un zâmbet adevărat, cu ambele aripi peste nivelul la bani, spre deosebire de asimetria unilaterală a acțiunilor."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "SVI",
                "text": "What does the SVI parameterisation model?",
                "options": [
                    "The price of the underlying",
                    "The risk-free rate curve",
                    "The volatility of the VIX",
                    "The total implied variance w(k) = sigma^2 tau as a function of log-moneyness"
                ],
                "correctExplanation": "SVI gives w(k) = a + b(rho(k - m) + sqrt((k - m)^2 + s^2)) for each expiry, with linear wings.",
                "incorrectExplanation": "SVI is a five-parameter description of one smile in total-variance form; it has no dynamics for the underlying."
            },
            "ro": {
                "title": "SVI",
                "text": "Ce modelează parametrizarea SVI?",
                "options": [
                    "Prețul activului suport",
                    "Curba ratei fără risc",
                    "Volatilitatea indicelui VIX",
                    "Varianța implicită totală w(k) = sigma^2 tau ca funcție de log-moneyness"
                ],
                "correctExplanation": "SVI dă w(k) = a + b(rho(k - m) + sqrt((k - m)^2 + s^2)) pentru fiecare scadență, cu aripi liniare.",
                "incorrectExplanation": "SVI este o descriere cu cinci parametri a unui zâmbet, în formă de varianță totală; nu are dinamică pentru activul suport."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Risk-neutral density",
                "text": "How is the risk-neutral density of S_T obtained from option prices (Breeden-Litzenberger)?",
                "options": [
                    "As e^{r tau} times the second derivative of call prices with respect to the strike",
                    "As the first derivative of the put price with respect to time",
                    "From the historical distribution of returns",
                    "As the ratio of call and put prices"
                ],
                "correctExplanation": "q(K) = e^{r tau} d2C/dK2: a narrow butterfly spread pays like a bet on S_T close to K.",
                "incorrectExplanation": "The density comes from the curvature of call prices in the strike; the historical distribution is the physical, not the risk-neutral one."
            },
            "ro": {
                "title": "Densitatea neutră la risc",
                "text": "Cum se obține densitatea neutră la risc a lui S_T din prețurile opțiunilor (Breeden-Litzenberger)?",
                "options": [
                    "Ca e^{r tau} înmulțit cu derivata a doua a prețurilor call în raport cu prețul de exercitare",
                    "Ca derivata întâi a prețului put în raport cu timpul",
                    "Din distribuția istorică a randamentelor",
                    "Ca raportul dintre prețurile call și put"
                ],
                "correctExplanation": "q(K) = e^{r tau} d2C/dK2: un spread fluture îngust plătește ca un pariu pe S_T aproape de K.",
                "incorrectExplanation": "Densitatea vine din curbura prețurilor call în prețul de exercitare; distribuția istorică este cea fizică, nu cea neutră la risc."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Bitcoin crash tail",
                "text": "For the Bitcoin expiry closest to 30 days, the SVI risk-neutral probability of a fall of more than 30% was 1.2% against 0.1% under the log-normal density. What does this show?",
                "options": [
                    "That the log-normal density overstates crash risk",
                    "That the market prices crash insurance far above what Black-Scholes with one volatility implies",
                    "That a crash will happen with probability 1.2%",
                    "That the SVI fit is wrong"
                ],
                "correctExplanation": "The tail of the risk-neutral density is several times heavier than the log-normal one: the crash tail is where Black-Scholes fails most.",
                "incorrectExplanation": "Risk-neutral probabilities are prices of insurance, not forecasts; the comparison shows how much heavier the priced tail is than the log-normal one."
            },
            "ro": {
                "title": "Coada de prăbușire Bitcoin",
                "text": "Pentru scadența Bitcoin cea mai apropiată de 30 de zile, probabilitatea neutră la risc SVI a unei scăderi de peste 30% a fost 1,2% față de 0,1% sub densitatea log-normală. Ce arată acest lucru?",
                "options": [
                    "Că densitatea log-normală supraestimează riscul de prăbușire",
                    "Că piața evaluează asigurarea împotriva prăbușirii mult peste ce implică Black-Scholes cu o singură volatilitate",
                    "Că o prăbușire va avea loc cu probabilitatea 1,2%",
                    "Că estimarea SVI este greșită"
                ],
                "correctExplanation": "Coada densității neutre la risc este de câteva ori mai grea decât cea log-normală: coada prăbușirilor este locul unde Black-Scholes greșește cel mai mult.",
                "incorrectExplanation": "Probabilitățile neutre la risc sunt prețuri ale asigurării, nu prognoze; comparația arată cât de grea este coada evaluată față de cea log-normală."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The VIX formula",
                "text": "Since 2003, how is the VIX computed?",
                "options": [
                    "From the at-the-money implied volatility of S&P 100 options",
                    "From a GARCH model fitted to S&P 500 returns",
                    "From a strip of out-of-the-money S&P 500 options weighted by 1/K^2, around 30 days (a variance-swap rate)",
                    "From VIX futures prices"
                ],
                "correctExplanation": "The Cboe formula sigma^2 = 2/T sum dK/K^2 e^{RT} Q(K) - (F/K0 - 1)^2/T replicates a 30-day variance swap.",
                "incorrectExplanation": "The original 1993 VIX used at-the-money S&P 100 options; the current VIX is a model-free variance measure from a strip of S&P 500 options."
            },
            "ro": {
                "title": "Formula VIX",
                "text": "Din 2003, cum se calculează VIX?",
                "options": [
                    "Din volatilitatea implicită la bani a opțiunilor pe S&P 100",
                    "Dintr-un model GARCH estimat pe randamentele S&P 500",
                    "Dintr-o bandă de opțiuni S&P 500 în afara banilor, ponderate cu 1/K^2, în jurul a 30 de zile (rata unui swap de varianță)",
                    "Din prețurile contractelor futures pe VIX"
                ],
                "correctExplanation": "Formula Cboe sigma^2 = 2/T sum dK/K^2 e^{RT} Q(K) - (F/K0 - 1)^2/T replică un swap de varianță pe 30 de zile.",
                "incorrectExplanation": "VIX-ul original din 1993 folosea opțiuni la bani pe S&P 100; VIX-ul actual este o măsură a varianței fără model, dintr-o bandă de opțiuni pe S&P 500."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "VIX term structure",
                "text": "The VIX was above the VIX3M (backwardation) on 7.6% of days since 2011. When does this happen?",
                "options": [
                    "In calm bull markets",
                    "At random, with no link to market conditions",
                    "Only on option expiry days",
                    "In crises, when fear is concentrated in the near term"
                ],
                "correctExplanation": "Backwardation marks stress; in the following 21 days realised volatility averaged 26.7% against 13.6% in contango.",
                "incorrectExplanation": "Normally the term structure slopes upwards (contango); it inverts in crises, when short-term uncertainty dominates."
            },
            "ro": {
                "title": "Structura la termen a VIX",
                "text": "VIX a fost peste VIX3M (backwardation) în 7,6% din zile, din 2011. Când se întâmplă acest lucru?",
                "options": [
                    "În piețe calme, în creștere",
                    "Aleatoriu, fără legătură cu condițiile de piață",
                    "Doar în zilele de scadență a opțiunilor",
                    "În crize, când frica se concentrează pe termen scurt"
                ],
                "correctExplanation": "Backwardation semnalează stresul; în următoarele 21 de zile volatilitatea realizată a fost în medie 26,7% față de 13,6% în contango.",
                "incorrectExplanation": "De obicei structura la termen este crescătoare (contango); se inversează în crize, când domină incertitudinea pe termen scurt."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Variance risk premium",
                "text": "Over 1990-2026 the mean VIX was 19.4 and the mean realised volatility over the following 21 days 15.3. What is the variance risk premium?",
                "options": [
                    "Implied variance minus the variance realised afterwards; positive on average, negative in crashes",
                    "Realised variance minus implied variance; always positive",
                    "The difference between the VIX and VVIX",
                    "The premium of an at-the-money call"
                ],
                "correctExplanation": "VRP = VIX^2 - RV: positive on 86% of days, about 4.1 volatility points on average, with large negative values in crashes.",
                "incorrectExplanation": "The premium is implied minus realised variance: buyers of variance pay it as insurance against turbulence."
            },
            "ro": {
                "title": "Prima de risc a varianței",
                "text": "În 1990-2026 media VIX a fost 19,4, iar media volatilității realizate în următoarele 21 de zile 15,3. Ce este prima de risc a varianței?",
                "options": [
                    "Varianța implicită minus varianța realizată ulterior; pozitivă în medie, negativă în prăbușiri",
                    "Varianța realizată minus varianța implicită; mereu pozitivă",
                    "Diferența dintre VIX și VVIX",
                    "Prima unui call la bani"
                ],
                "correctExplanation": "VRP = VIX^2 - RV: pozitivă în 86% din zile, în medie aproximativ 4,1 puncte de volatilitate, cu valori negative mari în prăbușiri.",
                "incorrectExplanation": "Prima este varianța implicită minus cea realizată: cumpărătorii de varianță o plătesc ca asigurare împotriva turbulențelor."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Overlapping windows",
                "text": "Why are Newey-West standard errors needed when averaging the daily variance risk premium?",
                "options": [
                    "Because the premium follows the Normal distribution",
                    "Because consecutive 21-day windows share 20 days, so the daily values are strongly autocorrelated",
                    "Because the VIX is measured with rounding error",
                    "Because the sample is too small"
                ],
                "correctExplanation": "Overlapping windows make the naive standard error several times too small; Newey-West with 21 lags corrects it.",
                "incorrectExplanation": "The issue is autocorrelation from overlapping windows, which the naive formula ignores."
            },
            "ro": {
                "title": "Ferestre suprapuse",
                "text": "De ce sunt necesare erori standard Newey-West când mediem prima zilnică de risc a varianței?",
                "options": [
                    "Pentru că prima urmează distribuția Normală",
                    "Pentru că ferestrele consecutive de 21 de zile au în comun 20 de zile, deci valorile zilnice sunt puternic autocorelate",
                    "Pentru că VIX este măsurat cu erori de rotunjire",
                    "Pentru că eșantionul este prea mic"
                ],
                "correctExplanation": "Ferestrele suprapuse fac eroarea standard naivă de câteva ori prea mică; Newey-West cu 21 de lag-uri o corectează.",
                "incorrectExplanation": "Problema este autocorelația dată de ferestrele suprapuse, pe care formula naivă o ignoră."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Is the VIX unbiased?",
                "text": "Regressing 21-day realised variance on VIX^2 gave a slope of 0.86 and a negative intercept. What does this say?",
                "options": [
                    "The VIX is an unbiased forecast",
                    "The VIX underestimates future volatility",
                    "The VIX is too high on average, most of all when it is high: it contains a risk premium",
                    "The VIX has no information about future volatility"
                ],
                "correctExplanation": "An unbiased forecast needs intercept 0 and slope 1; the VIX overstates realised variance, yet it explains more (R^2 0.37) than past variance (0.29).",
                "incorrectExplanation": "The regression shows an upward bias from the risk premium, but the VIX remains informative about future volatility."
            },
            "ro": {
                "title": "Este VIX nedeplasat?",
                "text": "Regresia varianței realizate pe 21 de zile pe VIX^2 a dat o pantă de 0,86 și un termen liber negativ. Ce spune acest lucru?",
                "options": [
                    "VIX este o prognoză nedeplasată",
                    "VIX subestimează volatilitatea viitoare",
                    "VIX este prea mare în medie, cel mai mult când este mare: conține o primă de risc",
                    "VIX nu conține informație despre volatilitatea viitoare"
                ],
                "correctExplanation": "O prognoză nedeplasată cere termen liber 0 și pantă 1; VIX supraestimează varianța realizată, dar explică mai mult (R^2 0,37) decât varianța trecută (0,29).",
                "incorrectExplanation": "Regresia arată o deplasare în sus dată de prima de risc, dar VIX rămâne informativ pentru volatilitatea viitoare."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "0DTE options",
                "text": "What characterises options with zero days to expiry (0DTE)?",
                "options": [
                    "Low gamma and slow time decay",
                    "They cannot be delta-hedged",
                    "They are only traded on Bitcoin",
                    "Very high gamma and time decay at the money: small premia and sudden large losses for sellers"
                ],
                "correctExplanation": "In the stylised same-day straddle test the seller won on 75% of days but lost 8.25% of the price on the worst day, about 11 premia.",
                "incorrectExplanation": "Near expiry gamma and theta explode at the money, so 0DTE positions change value very quickly."
            },
            "ro": {
                "title": "Opțiunile 0DTE",
                "text": "Ce caracterizează opțiunile cu zero zile până la scadență (0DTE)?",
                "options": [
                    "Gamma mică și erodare lentă în timp",
                    "Nu pot fi acoperite delta",
                    "Se tranzacționează doar pe Bitcoin",
                    "Gamma și erodarea în timp foarte mari la bani: prime mici și pierderi bruște și mari pentru vânzători"
                ],
                "correctExplanation": "În testul stilizat cu straddle în aceeași zi vânzătorul a câștigat în 75% din zile, dar a pierdut 8,25% din preț în cea mai rea zi, aproximativ 11 prime.",
                "incorrectExplanation": "Aproape de scadență gamma și theta explodează la bani, deci pozițiile 0DTE își schimbă valoarea foarte repede."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Bitcoin variance premium",
                "text": "For Bitcoin (2021-2026) the mean DVOL was 60.3 and the mean realised volatility over the next 30 days 51.7. Which statement is right?",
                "options": [
                    "Bitcoin option sellers also earned a premium on average, but with long episodes of negative premium",
                    "Bitcoin options are always cheap relative to realised volatility",
                    "The premium is exactly the same as for the S&P 500 in volatility points",
                    "DVOL is not related to option prices"
                ],
                "correctExplanation": "The premium was about 8.5 volatility points, positive on 71% of days: larger in points than for the S&P 500, but less regular.",
                "incorrectExplanation": "DVOL is built from Bitcoin option prices; it exceeded realised volatility on average, though less consistently than the VIX."
            },
            "ro": {
                "title": "Prima de varianță Bitcoin",
                "text": "Pentru Bitcoin (2021-2026) media DVOL a fost 60,3, iar media volatilității realizate în următoarele 30 de zile 51,7. Ce afirmație este corectă?",
                "options": [
                    "Și vânzătorii de opțiuni Bitcoin au câștigat în medie o primă, dar cu episoade lungi de primă negativă",
                    "Opțiunile Bitcoin sunt mereu ieftine față de volatilitatea realizată",
                    "Prima este exact aceeași ca pentru S&P 500 în puncte de volatilitate",
                    "DVOL nu are legătură cu prețurile opțiunilor"
                ],
                "correctExplanation": "Prima a fost de aproximativ 8,5 puncte de volatilitate, pozitivă în 71% din zile: mai mare în puncte decât pentru S&P 500, dar mai puțin regulată.",
                "incorrectExplanation": "DVOL este construit din prețurile opțiunilor Bitcoin; a depășit în medie volatilitatea realizată, deși mai puțin constant decât VIX."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Variance swap",
                "text": "What does the seller of a variance swap receive and pay?",
                "options": [
                    "Receives the realised variance, pays a fixed strike",
                    "Receives a fixed strike (implied variance), pays the realised variance: small gains most months, large losses in crashes",
                    "Receives the VIX level in points, pays nothing",
                    "Receives dividends of the index"
                ],
                "correctExplanation": "The pay-off is notional times (strike minus realised variance) for the seller; realised variance explodes in crashes, so losses are convex.",
                "incorrectExplanation": "The seller of variance is short volatility insurance: the strike is fixed at the start, the realised variance is paid at the end."
            },
            "ro": {
                "title": "Swap-ul de varianță",
                "text": "Ce încasează și ce plătește vânzătorul unui swap de varianță?",
                "options": [
                    "Încasează varianța realizată, plătește un preț de exercitare fix",
                    "Încasează un preț de exercitare fix (varianța implicită), plătește varianța realizată: câștiguri mici în majoritatea lunilor, pierderi mari în prăbușiri",
                    "Încasează nivelul VIX în puncte, nu plătește nimic",
                    "Încasează dividendele indicelui"
                ],
                "correctExplanation": "Plata pentru vânzător este notional înmulțit cu (prețul de exercitare minus varianța realizată); varianța realizată explodează în prăbușiri, deci pierderile sunt convexe.",
                "incorrectExplanation": "Vânzătorul de varianță a vândut o asigurare împotriva volatilității: prețul de exercitare se fixează la început, varianța realizată se plătește la final."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: time to maturity",
                "text": "An AI assistant writes: \"For a 30-day at-the-money call, plug T = 30 into the Black-Scholes formula, with sigma = 0.20 and r = 0.04 per year.\" What is wrong?",
                "options": [
                    "T must be in years, T = 30/365 = 0.082, because sigma and r are annual",
                    "sigma must be entered as 20, not 0.20",
                    "r must be converted to a daily rate, not T",
                    "Black-Scholes cannot price at-the-money options"
                ],
                "correctExplanation": "sigma and r are per year, so time must be in years too; with T = 30 the call is priced as if it had 30 years to run.",
                "incorrectExplanation": "Check the units: every input to Black-Scholes must use the same time unit, and volatility enters as a decimal."
            },
            "ro": {
                "title": "Găsiți eroarea AI: scadența",
                "text": "Un asistent AI scrie: „Pentru un call la bani pe 30 de zile, puneți T = 30 în formula Black-Scholes, cu sigma = 0,20 și r = 0,04 pe an.” Ce este greșit?",
                "options": [
                    "T trebuie exprimat în ani, T = 30/365 = 0,082, pentru că sigma și r sunt anuale",
                    "sigma trebuie introdus ca 20, nu 0,20",
                    "r trebuie transformat într-o rată zilnică, nu T",
                    "Black-Scholes nu poate evalua opțiuni la bani"
                ],
                "correctExplanation": "sigma și r sunt pe an, deci și timpul trebuie exprimat în ani; cu T = 30, call-ul este evaluat ca și cum ar avea 30 de ani până la scadență.",
                "incorrectExplanation": "Verificați unitățile: toate datele de intrare Black-Scholes trebuie să folosească aceeași unitate de timp, iar volatilitatea intră ca număr zecimal."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: put-call parity",
                "text": "An AI assistant writes: \"By put-call parity, P = C + S - K e^{-r tau}. With C = 4, S = 100, K = 105 and r = 0, the put is worth -1: buy it and get paid.\" What is wrong?",
                "options": [
                    "Nothing: negative put prices are possible when rates are zero",
                    "The sign is wrong: P = C - S + K e^{-r tau} = 4 - 100 + 105 = 9",
                    "Parity holds only for American options",
                    "With r = 0 calls and puts have the same price, so the put is worth 4"
                ],
                "correctExplanation": "From C - P = S - K e^{-r tau}, the put is C - S + K e^{-r tau}; a negative option price is impossible, which flags the error at once.",
                "incorrectExplanation": "Rewrite C - P = S - K e^{-r tau} for P and check the no-arbitrage bound: a put can never have a negative price."
            },
            "ro": {
                "title": "Găsiți eroarea AI: paritatea put-call",
                "text": "Un asistent AI scrie: „Din paritatea put-call, P = C + S - K e^{-r tau}. Cu C = 4, S = 100, K = 105 și r = 0, put-ul valorează -1: îl cumpărați și sunteți plătiți.” Ce este greșit?",
                "options": [
                    "Nimic: prețurile negative ale put-urilor sunt posibile când ratele sunt zero",
                    "Semnul este greșit: P = C - S + K e^{-r tau} = 4 - 100 + 105 = 9",
                    "Paritatea este valabilă doar pentru opțiuni americane",
                    "Cu r = 0, call-urile și put-urile au același preț, deci put-ul valorează 4"
                ],
                "correctExplanation": "Din C - P = S - K e^{-r tau}, put-ul este C - S + K e^{-r tau}; un preț negativ al unei opțiuni este imposibil, ceea ce semnalează imediat eroarea.",
                "incorrectExplanation": "Scrieți C - P = S - K e^{-r tau} în funcție de P și verificați limita de non-arbitraj: un put nu poate avea niciodată preț negativ."
            }
        }
    ]
};

// ============================================================
// Quiz bank for chapter id 'digital-assets': Digital Assets and DeFi (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['digital-assets'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 1,
            "en": {
                "title": "GRS under heavy tails",
                "text": "Weekly crypto test-asset returns have a Hill tail index of about 2.7. Which statement about the GRS F-test of zero alphas is correct?",
                "options": [
                    "It is exact for any error distribution, because it is an F statistic",
                    "Its exact F distribution relies on i.i.d. Normal errors; a HAC-Wald test or a bootstrap version is needed",
                    "It needs only T > N, whatever the tails",
                    "Heavy tails make it conservative, so its rejections are always reliable"
                ],
                "correctExplanation": "The F(N, T - N - K) distribution of GRS is derived under i.i.d. Normal errors; with heavy tails and volatility clustering use a GMM/HAC Wald test or a wild bootstrap under the null.",
                "incorrectExplanation": "GRS is exactly F only under i.i.d. Normal errors; heavy tails can bias its size in either direction, so a robust or bootstrap version is needed."
            },
            "ro": {
                "title": "GRS cu cozi grele",
                "text": "Randamentele săptămînale ale activelor cripto de test au un indice de coadă Hill de aproximativ 2,7. Ce afirmație despre testul F GRS pentru alfa nule este corectă?",
                "options": [
                    "Este exact pentru orice distribuție a erorilor, fiindcă este o statistică F",
                    "Distribuția F exactă cere erori i.i.d. cu distribuția Normală; este nevoie de un test Wald HAC sau de o versiune bootstrap",
                    "Cere doar T > N, oricare ar fi cozile",
                    "Cozile grele îl fac conservator, deci respingerile lui sînt mereu sigure"
                ],
                "correctExplanation": "Distribuția F(N, T - N - K) a statisticii GRS este derivată pentru erori i.i.d. cu distribuția Normală; cu cozi grele și volatility clustering folosim un test Wald GMM/HAC sau un bootstrap wild sub ipoteza nulă.",
                "incorrectExplanation": "GRS este exact F doar pentru erori i.i.d. cu distribuția Normală; cozile grele pot deplasa nivelul testului în orice direcție, deci este nevoie de o versiune robustă sau bootstrap."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Free float",
                "text": "Why were XRP and Chainlink left out of the index universe in this chapter?",
                "options": [
                    "Their prices are not available",
                    "They are stablecoins",
                    "Their reported supply includes tokens held by the issuer",
                    "They trade only on weekdays"
                ],
                "correctExplanation": "Their reported supply includes tokens held by the issuer, so price x supply would overstate the tradable market value.",
                "incorrectExplanation": "The issue is free float: the published supply is not the supply in circulation."
            },
            "ro": {
                "title": "Partea liberă la tranzacționare",
                "text": "De ce au fost lăsate XRP și Chainlink în afara universului indicelui în acest capitol?",
                "options": [
                    "Prețurile lor nu sînt disponibile",
                    "Sînt stablecoin-uri",
                    "Oferta lor raportată include tokenurile deținute de emitent",
                    "Se tranzacționează doar în zilele lucrătoare"
                ],
                "correctExplanation": "Oferta raportată include tokenurile deținute de emitent, deci prețul x oferta ar supraestima valoarea tranzacționabilă.",
                "incorrectExplanation": "Problema este partea liberă la tranzacționare: oferta publicată nu este oferta în circulație."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Concentration",
                "text": "The market-value shares of five coins give HHI = 0.71. What is the effective number of coins?",
                "options": [
                    "0.71",
                    "About 1.4",
                    "About 3.5",
                    "5"
                ],
                "correctExplanation": "1/HHI = 1/0.71, about 1.4: the market behaves like 1.4 equally sized coins.",
                "incorrectExplanation": "The effective number is the inverse of the Herfindahl-Hirschman index."
            },
            "ro": {
                "title": "Concentrarea",
                "text": "Ponderile valorii de piață pentru cinci monede dau HHI = 0,71. Care este numărul efectiv de monede?",
                "options": [
                    "0,71",
                    "Aproximativ 1,4",
                    "Aproximativ 3,5",
                    "5"
                ],
                "correctExplanation": "1/HHI = 1/0,71, aproximativ 1,4: piața se comportă ca 1,4 monede de mărime egală.",
                "incorrectExplanation": "Numărul efectiv este inversul indicelui Herfindahl-Hirschman."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Shanken correction",
                "text": "Which source of uncertainty does the Shanken correction add to the Fama-MacBeth standard errors of crypto factor premia?",
                "options": [
                    "The autocorrelation of the weekly premium estimates",
                    "The fact that the crypto market factor is not a traded portfolio",
                    "The number of coins in the cross-section",
                    "The estimation error in the first-pass betas (errors in variables)"
                ],
                "correctExplanation": "The second pass treats the estimated betas as known; Shanken (1992) multiplies the residual-driven part of the variance by (1 + lambda' Sigma_f^-1 lambda) and adds the factor-variation part Sigma_f / T once, without that multiplier.",
                "incorrectExplanation": "The Shanken correction addresses errors in variables: the betas in the second pass are estimates, which Fama-MacBeth standard errors ignore. Serial correlation of the premium estimates is a separate issue, handled by HAC standard errors."
            },
            "ro": {
                "title": "Corecția Shanken",
                "text": "Ce sursă de incertitudine adaugă corecția Shanken erorilor standard Fama-MacBeth ale primelor factorilor cripto?",
                "options": [
                    "Autocorelarea estimărilor săptămînale ale primei",
                    "Faptul că factorul pieței cripto nu este un portofoliu tranzacționat",
                    "Numărul de monede din secțiunea transversală",
                    "Eroarea de estimare a coeficienților beta din prima etapă (erori în variabile)"
                ],
                "correctExplanation": "A doua etapă tratează beta estimate ca și cum ar fi cunoscute; Shanken (1992) înmulțește partea varianței care provine din reziduuri cu (1 + lambda' Sigma_f^-1 lambda) și adaugă o singură dată, fără acest factor, partea provenită din variația factorilor, Sigma_f / T.",
                "incorrectExplanation": "Corecția Shanken tratează eroarea în variabile: beta din a doua etapă sînt estimări, lucru ignorat de erorile standard Fama-MacBeth. Autocorelarea estimărilor primei este o problemă separată, tratată cu erori standard HAC."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Weekend effect",
                "text": "What did the data show about Bitcoin returns at weekends?",
                "options": [
                    "Weekend variance is less than half of weekday variance, before and after the spot ETFs",
                    "Weekends are the most volatile days",
                    "The weekend effect appeared only after the spot ETFs",
                    "There is no trading at weekends"
                ],
                "correctExplanation": "The weekend / weekday variance ratio was about 0.45 before and 0.39 after January 2024; the change is not significant.",
                "incorrectExplanation": "Bitcoin trades at weekends, but weekend returns are much calmer, and this was already true before the ETFs."
            },
            "ro": {
                "title": "Efectul de weekend",
                "text": "Ce au arătat datele despre randamentele Bitcoin în weekend?",
                "options": [
                    "Dispersia de weekend este sub jumătate din cea din zilele lucrătoare, înainte și după ETF-urile spot",
                    "Weekendurile sînt zilele cele mai volatile",
                    "Efectul de weekend a apărut doar după ETF-urile spot",
                    "În weekend nu se tranzacționează"
                ],
                "correctExplanation": "Raportul dispersiilor weekend / zile lucrătoare a fost aproximativ 0,45 înainte și 0,39 după ianuarie 2024; modificarea nu este semnificativă.",
                "incorrectExplanation": "Bitcoin se tranzacționează în weekend, dar randamentele de weekend sînt mult mai calme, iar acest lucru era adevărat și înainte de ETF-uri."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Correlation with shares",
                "text": "When did Bitcoin become clearly positively correlated with the S&P 500?",
                "options": [
                    "In 2017",
                    "Only after the spot ETFs in 2024",
                    "Around March 2020",
                    "Never"
                ],
                "correctExplanation": "The rolling correlation jumped in March 2020 and stayed around 0.4 since then.",
                "incorrectExplanation": "The break came with the pandemic in 2020, not with the ETFs."
            },
            "ro": {
                "title": "Corelația cu acțiunile",
                "text": "Cînd a devenit Bitcoin clar corelat pozitiv cu S&P 500?",
                "options": [
                    "În 2017",
                    "Doar după ETF-urile spot din 2024",
                    "În jurul lui martie 2020",
                    "Niciodată"
                ],
                "correctExplanation": "Corelația mobilă a sărit în martie 2020 și a rămas în jur de 0,4 de atunci.",
                "incorrectExplanation": "Ruptura a venit odată cu pandemia din 2020, nu cu ETF-urile."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Kurtosis when the tail index is below 4",
                "text": "Bitcoin's Hill tail index is 2.7 and its sample excess kurtosis 14.8. What follows?",
                "options": [
                    "The population fourth moment is likely infinite, so the sample kurtosis is not a consistent estimate and its bootstrap CI is unreliable",
                    "The kurtosis is 14.8 plus or minus 1.96 standard errors",
                    "The Hill index and the kurtosis measure the same thing",
                    "Rescaling the returns to unit variance makes the kurtosis finite"
                ],
                "correctExplanation": "With alpha < 4 the fourth moment does not exist; the sample kurtosis grows with the sample and is driven by the largest days, and the bootstrap fails with infinite moments (Athreya, 1987): report the tail index with its CI.",
                "incorrectExplanation": "When alpha < 4 the population kurtosis is infinite, so no standard error or rescaling rescues the sample kurtosis; the Hill index is the right summary of the tail."
            },
            "ro": {
                "title": "Aplatizarea cînd indicele de coadă este sub 4",
                "text": "Indicele de coadă Hill al Bitcoin este 2,7, iar excesul de aplatizare de selecție 14,8. Ce rezultă?",
                "options": [
                    "Momentul de ordinul patru al populației este probabil infinit, deci aplatizarea de selecție nu este un estimator consistent, iar CI bootstrap pentru ea nu este de încredere",
                    "Aplatizarea este 14,8 plus sau minus 1,96 erori standard",
                    "Indicele Hill și aplatizarea măsoară același lucru",
                    "Rescalarea randamentelor la varianță unitară face aplatizarea finită"
                ],
                "correctExplanation": "Cu alpha < 4 momentul de ordinul patru nu există; aplatizarea de selecție crește odată cu eșantionul și este dominată de cele mai mari zile, iar bootstrap-ul eșuează la momente infinite (Athreya, 1987): raportăm indicele de coadă cu CI.",
                "incorrectExplanation": "Cînd alpha < 4, aplatizarea populației este infinită, deci nicio eroare standard și nicio rescalare nu salvează aplatizarea de selecție; indicele Hill este rezumatul potrivit al cozii."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "CRIX",
                "text": "How does CRIX choose its number of constituents?",
                "options": [
                    "By an information criterion (AIC) that trades tracking of the total market against the number of coins",
                    "It always holds 30 coins",
                    "It holds all coins with a price above 1 USD",
                    "It holds the coins with the highest returns last month"
                ],
                "correctExplanation": "Trimborn and Hardle (2018) choose the number of constituents with the Akaike information criterion.",
                "incorrectExplanation": "CRIX does not fix the number of members; model selection decides it."
            },
            "ro": {
                "title": "CRIX",
                "text": "Cum își alege CRIX numărul de constituenți?",
                "options": [
                    "Printr-un criteriu informațional (AIC) care echilibrează urmărirea întregii piețe cu numărul de monede",
                    "Are mereu 30 de monede",
                    "Conține toate monedele cu preț peste 1 USD",
                    "Conține monedele cu cele mai mari randamente în luna anterioară"
                ],
                "correctExplanation": "Trimborn și Härdle (2018) aleg numărul de constituenți cu criteriul informațional Akaike.",
                "incorrectExplanation": "CRIX nu fixează numărul de membri; selecția de model îl decide."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "AIC penalty",
                "text": "In the Gaussian form of the CRIX criterion, AIC = T ln(s_k^2) + 2s with s the number of added coins, when is one more constituent admitted?",
                "options": [
                    "When its price is rising",
                    "When it has the lowest volatility",
                    "Always",
                    "When it lowers T ln(s_k^2) by more than 2"
                ],
                "correctExplanation": "Each extra coin costs 2 in the penalty; it is admitted if the tracking improvement is larger.",
                "incorrectExplanation": "The rule compares the fall in T ln(s_k^2) with the penalty of 2 per added constituent."
            },
            "ro": {
                "title": "Penalizarea AIC",
                "text": "În forma gaussiană a criteriului CRIX, AIC = T ln(s_k^2) + 2s, cu s numărul de monede adăugate, cînd este admis încă un constituent?",
                "options": [
                    "Cînd prețul lui crește",
                    "Cînd are cea mai mică volatilitate",
                    "Întotdeauna",
                    "Cînd scade T ln(s_k^2) cu mai mult de 2"
                ],
                "correctExplanation": "Fiecare monedă în plus costă 2 în penalizare; este admisă dacă îmbunătățirea urmăririi este mai mare.",
                "incorrectExplanation": "Regula compară scăderea lui T ln(s_k^2) cu penalizarea de 2 pentru fiecare constituent adăugat."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Threshold AR identification",
                "text": "Testing a linear AR(1) against a threshold AR for stablecoin peg deviations, why are chi-square critical values invalid?",
                "options": [
                    "There are too few observations outside the band",
                    "The AR coefficient outside the band is negative",
                    "The threshold is not identified under the null (the Davies problem), so the sup-Wald statistic needs bootstrap p-values",
                    "The deviations are measured in basis points"
                ],
                "correctExplanation": "Under the linear null the threshold c does not enter the model, so the sup over c of W(c) is not chi-square; Hansen (1996) obtains p-values from a fixed-regressor bootstrap.",
                "incorrectExplanation": "The issue is a nuisance parameter that is not identified under the null: the supremum over thresholds has a non-standard distribution."
            },
            "ro": {
                "title": "Identificarea AR cu prag",
                "text": "Cînd testăm un AR(1) liniar împotriva unui AR cu prag pentru abaterile de la paritate ale unui stablecoin, de ce sînt invalide valorile critice chi-pătrat?",
                "options": [
                    "Sînt prea puține observații în afara benzii",
                    "Coeficientul AR din afara benzii este negativ",
                    "Pragul nu este identificat sub ipoteza nulă (problema Davies), deci statistica sup-Wald cere p-valori bootstrap",
                    "Abaterile sînt măsurate în puncte de bază"
                ],
                "correctExplanation": "Sub ipoteza nulă liniară, pragul c nu apare în model, deci supremul după c al lui W(c) nu are distribuția chi-pătrat; Hansen (1996) obține p-valorile dintr-un bootstrap cu regresori ficși.",
                "incorrectExplanation": "Problema este un parametru de perturbare neidentificat sub ipoteza nulă: supremul după praguri are o distribuție nestandard."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Arbitrage band",
                "text": "A stablecoin can be redeemed at 1 USD with a cost c_r. Where does arbitrage keep its market price from below?",
                "options": [
                    "At 0",
                    "Near 1 - c_r",
                    "At 1 + c_r",
                    "At the Bitcoin price"
                ],
                "correctExplanation": "Below 1 - c_r traders buy on the market and redeem at 1 USD, which pushes the price up.",
                "incorrectExplanation": "The lower edge of the band is set by the redemption cost."
            },
            "ro": {
                "title": "Banda de arbitraj",
                "text": "Un stablecoin poate fi răscumpărat la 1 USD cu un cost c_r. Unde menține arbitrajul prețul de piață dinspre jos?",
                "options": [
                    "La 0",
                    "Aproape de 1 - c_r",
                    "La 1 + c_r",
                    "La prețul Bitcoin"
                ],
                "correctExplanation": "Sub 1 - c_r, participanții cumpără pe piață și răscumpără la 1 USD, ceea ce împinge prețul în sus.",
                "incorrectExplanation": "Marginea de jos a benzii este stabilită de costul de răscumpărare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "March 2023",
                "text": "Why did USD Coin fall below par on 11 March 2023?",
                "options": [
                    "Part of its reserves was exposed to the failed Silicon Valley Bank and redemption could not settle over the weekend",
                    "Its smart contract was hacked",
                    "The Terra blockchain stopped",
                    "The Federal Reserve raised rates that day"
                ],
                "correctExplanation": "SVB was closed on 10 March; USD Coin relied on reserves held there and banks were shut until Monday.",
                "incorrectExplanation": "The trigger was a bank failure affecting the reserves, not a hack or a rate decision."
            },
            "ro": {
                "title": "Martie 2023",
                "text": "De ce a scăzut USD Coin sub paritate pe 11 martie 2023?",
                "options": [
                    "O parte din rezerve era expusă la Silicon Valley Bank, intrată în faliment, iar răscumpărarea nu se putea deconta în weekend",
                    "Contractul inteligent a fost atacat informatic (hack)",
                    "Blockchain-ul Terra s-a oprit",
                    "Rezerva Federală a crescut dobînda în acea zi"
                ],
                "correctExplanation": "SVB a fost închisă pe 10 martie; USD Coin depindea de rezerve deținute acolo, iar băncile au fost închise pînă luni.",
                "incorrectExplanation": "Declanșatorul a fost un faliment bancar care afecta rezervele, nu un atac informatic sau o decizie de dobîndă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Where LVR comes from",
                "text": "Which property of the constant-product pool value V(P) = 2 sqrt(kP) produces the loss versus rebalancing?",
                "options": [
                    "The trading fee charged on each swap",
                    "Its concavity in P (negative gamma): the LVR rate is -V''(P) sigma^2 P^2 / (2V) = sigma^2 / 8",
                    "The impermanent loss at the end of the holding period",
                    "Its linearity in P"
                ],
                "correctExplanation": "By Ito, the rebalancing portfolio minus the pool grows at -0.5 V'' sigma^2 P^2 dt; with V'' = -0.5 sqrt(k) P^(-3/2) this equals (sigma^2/8) V dt.",
                "incorrectExplanation": "LVR is a second-order (gamma) effect of a concave value function; fees reduce it and impermanent loss is a path-independent endpoint quantity."
            },
            "ro": {
                "title": "De unde vine LVR",
                "text": "Ce proprietate a valorii pool-ului cu produs constant V(P) = 2 sqrt(kP) produce pierderea față de reechilibrare?",
                "options": [
                    "Comisionul perceput la fiecare schimb",
                    "Concavitatea în P (gamma negativă): rata LVR este -V''(P) sigma^2 P^2 / (2V) = sigma^2 / 8",
                    "Pierderea impermanentă de la sfîrșitul perioadei de deținere",
                    "Liniaritatea în P"
                ],
                "correctExplanation": "Prin Itô, portofoliul de reechilibrare minus pool-ul crește cu -0,5 V'' sigma^2 P^2 dt; cu V'' = -0,5 sqrt(k) P^(-3/2) aceasta este (sigma^2/8) V dt.",
                "incorrectExplanation": "LVR este un efect de ordinul doi (gamma) al unei funcții de valoare concave; comisioanele îl reduc, iar pierderea impermanentă se calculează doar la sfîrșitul perioadei și nu depinde de traiectorie."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "TerraUSD",
                "text": "What made the TerraUSD run self-fulfilling?",
                "options": [
                    "High transaction fees",
                    "Its reserves in Treasury bills lost value",
                    "Regulators froze its accounts",
                    "Redemption created more of the second token (LUNA), pushing its price down, with no external collateral"
                ],
                "correctExplanation": "Without reserves, redemptions into LUNA diluted LUNA and weakened the peg further: a death spiral.",
                "incorrectExplanation": "TerraUSD had no external collateral; the peg rested on confidence and on the value of LUNA."
            },
            "ro": {
                "title": "TerraUSD",
                "text": "Ce a făcut ca panica din jurul TerraUSD să se autoîmplinească?",
                "options": [
                    "Comisioanele mari de tranzacționare",
                    "Rezervele în titluri de stat și-au pierdut valoarea",
                    "Autoritățile i-au înghețat conturile",
                    "Răscumpărarea a creat mai mult din al doilea token (LUNA), împingîndu-i prețul în jos, fără garanții externe"
                ],
                "correctExplanation": "Fără rezerve, răscumpărările în LUNA au diluat LUNA și au slăbit și mai mult paritatea: o spirală descendentă autoîntreținută (death spiral).",
                "incorrectExplanation": "TerraUSD nu avea garanții externe; paritatea se sprijinea pe încredere și pe valoarea LUNA."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Swap formula",
                "text": "With fee f and gamma = 1 - f, how much Y does a trader receive for Delta x?",
                "options": [
                    "y Delta x / x",
                    "y gamma Delta x / (x + gamma Delta x)",
                    "x gamma Delta x / (y + gamma Delta x)",
                    "gamma Delta x"
                ],
                "correctExplanation": "From (x + gamma Delta x)(y - Delta y) = xy.",
                "incorrectExplanation": "Solve the invariant after adding the fee-adjusted input to the X reserve."
            },
            "ro": {
                "title": "Formula schimbului",
                "text": "Cu comisionul f și gamma = 1 - f, cît Y primește un participant pentru Delta x?",
                "options": [
                    "y Delta x / x",
                    "y gamma Delta x / (x + gamma Delta x)",
                    "x gamma Delta x / (y + gamma Delta x)",
                    "gamma Delta x"
                ],
                "correctExplanation": "Din (x + gamma Delta x)(y - Delta y) = xy.",
                "incorrectExplanation": "Rezolvați invariantul după ce adăugați la rezerva X intrarea ajustată cu comisionul."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Impermanent loss",
                "text": "The price of Ether doubles (r = 2). What is the impermanent loss of a 50/50 constant-product position?",
                "options": [
                    "0%",
                    "About -2%",
                    "About -5.7%",
                    "-50%"
                ],
                "correctExplanation": "IL(2) = 2 sqrt(2) / 3 - 1, about -5.72%.",
                "incorrectExplanation": "Use IL(r) = 2 sqrt(r) / (1 + r) - 1."
            },
            "ro": {
                "title": "Pierderea impermanentă",
                "text": "Prețul Ether se dublează (r = 2). Care este pierderea impermanentă a unei poziții 50/50 cu produs constant?",
                "options": [
                    "0%",
                    "Aproximativ -2%",
                    "Aproximativ -5,7%",
                    "-50%"
                ],
                "correctExplanation": "IL(2) = 2 rad(2) / 3 - 1, aproximativ -5,72%.",
                "incorrectExplanation": "Folosiți IL(r) = 2 rad(r) / (1 + r) - 1."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Loss versus rebalancing",
                "text": "For a constant-product pool with price volatility sigma, at what rate does the loss versus rebalancing grow?",
                "options": [
                    "sigma",
                    "sigma / 2",
                    "sigma^2 / 2",
                    "sigma^2 / 8"
                ],
                "correctExplanation": "Milionis et al. (2022): LVR / V = sigma^2 / 8 per unit of time; with sigma = 68% this is about 5.8% a year.",
                "incorrectExplanation": "The rate is quadratic in volatility with factor one eighth."
            },
            "ro": {
                "title": "Pierderea față de reechilibrare",
                "text": "Pentru un pool cu produs constant și volatilitatea prețului sigma, cu ce rată crește pierderea față de reechilibrare?",
                "options": [
                    "sigma",
                    "sigma / 2",
                    "sigma^2 / 2",
                    "sigma^2 / 8"
                ],
                "correctExplanation": "Milionis et al. (2022): LVR / V = sigma^2 / 8 pe unitatea de timp; cu sigma = 68% înseamnă aproximativ 5,8% pe an.",
                "incorrectExplanation": "Rata este pătratică în volatilitate, cu factorul 1/8."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "TVL",
                "text": "Why is total value locked (TVL) in DeFi a weak measure of adoption?",
                "options": [
                    "It counts only Bitcoin",
                    "Deposits are valued at market prices, so TVL mixes price changes with deposits and co-moves strongly with Ether",
                    "It is published only once a year",
                    "It excludes stablecoins"
                ],
                "correctExplanation": "Monthly TVL changes load on Ether returns with a slope near 0.8 and R^2 about 0.6; the regression does not separate valuation from net deposits.",
                "incorrectExplanation": "TVL is a market value: a price fall lowers it even if nobody withdraws."
            },
            "ro": {
                "title": "TVL",
                "text": "De ce este valoarea totală blocată (TVL) în DeFi o măsură slabă a adoptării?",
                "options": [
                    "Numără doar Bitcoin",
                    "Depozitele sînt evaluate la prețul pieței, deci TVL amestecă schimbările de preț cu depunerile și se mișcă strîns cu Ether",
                    "Se publică doar o dată pe an",
                    "Exclude stablecoin-urile"
                ],
                "correctExplanation": "Variațiile lunare ale TVL depind de randamentele Ether cu o pantă de aproximativ 0,8 și R^2 de aproximativ 0,6; regresia nu separă evaluarea de depunerile nete.",
                "incorrectExplanation": "TVL este o valoare de piață: o scădere a prețului o reduce chiar dacă nimeni nu își retrage fondurile."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "ETF tracking",
                "text": "IBIT against Bitcoin has daily R^2 of about 0.82 but weekly R^2 of about 0.98. Why?",
                "options": [
                    "The two closing prices are recorded at different times of the day; the mismatch averages out over a week",
                    "IBIT holds futures, not Bitcoin",
                    "IBIT trades on weekends",
                    "Bitcoin is less volatile weekly"
                ],
                "correctExplanation": "Daily returns compare prices from different moments; weekly returns reduce the timing noise.",
                "incorrectExplanation": "The fund holds spot Bitcoin; the low daily R^2 is a measurement artefact."
            },
            "ro": {
                "title": "Urmărirea ETF",
                "text": "IBIT față de Bitcoin are R^2 zilnic de aproximativ 0,82, dar R^2 săptămînal de aproximativ 0,98. De ce?",
                "options": [
                    "Cele două prețuri de închidere sînt înregistrate la ore diferite; nepotrivirea se compensează într-o săptămînă",
                    "IBIT deține contracte futures, nu Bitcoin",
                    "IBIT se tranzacționează în weekend",
                    "Bitcoin este mai puțin volatil săptămînal"
                ],
                "correctExplanation": "Randamentele zilnice compară prețuri din momente diferite; randamentele săptămînale reduc zgomotul de sincronizare.",
                "incorrectExplanation": "Fondul deține Bitcoin spot; R^2 zilnic scăzut este un artefact de măsurare."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Fee drift",
                "text": "The log ratio of IBIT to Bitcoin falls by about 0.24% a year. What explains it?",
                "options": [
                    "A premium that grows over time",
                    "Weekend trading",
                    "The 0.25% annual sponsor fee paid out of the Bitcoin held",
                    "Rising Bitcoin supply"
                ],
                "correctExplanation": "The fund sells Bitcoin to pay its fee, so the Bitcoin per share shrinks at about the fee rate.",
                "incorrectExplanation": "The drift matches the fee, not a premium or a supply effect."
            },
            "ro": {
                "title": "Drift-ul din comision",
                "text": "Logaritmul raportului IBIT / Bitcoin scade cu aproximativ 0,24% pe an. Ce explică această scădere?",
                "options": [
                    "O primă care crește în timp",
                    "Tranzacționarea din weekend",
                    "Comisionul anual de 0,25% plătit din Bitcoin-ul deținut",
                    "Creșterea ofertei de Bitcoin"
                ],
                "correctExplanation": "Fondul vinde Bitcoin pentru a-și plăti comisionul, deci Bitcoin-ul pe unitate scade cu aproximativ rata comisionului.",
                "incorrectExplanation": "Drift-ul corespunde comisionului, nu unei prime sau unui efect de ofertă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Crypto equities",
                "text": "A weekly two-factor regression gives Strategy a Bitcoin beta of about 1.2 and an S&P 500 beta of about 1.0. What is the best description?",
                "options": [
                    "A pure Bitcoin tracker",
                    "A defensive stock",
                    "A stock uncorrelated with crypto",
                    "A leveraged Bitcoin position with extra equity-market risk"
                ],
                "correctExplanation": "A beta above 1 to Bitcoin plus an equity beta: more than Bitcoin exposure, plus stock-market risk.",
                "incorrectExplanation": "Both betas are sizeable, so the stock is neither a pure tracker nor defensive."
            },
            "ro": {
                "title": "Acțiunile „cripto”",
                "text": "O regresie săptămînală cu doi factori dă pentru Strategy un beta față de Bitcoin de aproximativ 1,2 și un beta față de S&P 500 de aproximativ 1,0. Care este cea mai bună descriere?",
                "options": [
                    "Un instrument care urmărește pur Bitcoin",
                    "O acțiune defensivă",
                    "O acțiune necorelată cu cripto",
                    "O poziție în Bitcoin cu efect de levier, plus riscul pieței de acțiuni"
                ],
                "correctExplanation": "Un beta peste 1 față de Bitcoin plus un beta de acțiune: mai mult decît expunerea la Bitcoin, plus riscul bursei.",
                "incorrectExplanation": "Ambii coeficienți beta sînt importanți, deci acțiunea nu este nici un instrument pur, nici defensivă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Safe haven",
                "text": "According to Baur and Lucey (2010), what makes an asset a safe haven?",
                "options": [
                    "A positive average return",
                    "Zero or negative correlation with the market on its worst days",
                    "Low volatility on all days",
                    "A fixed supply"
                ],
                "correctExplanation": "A safe haven is uncorrelated or negatively correlated with the market in extreme down markets.",
                "incorrectExplanation": "The definition is about behaviour on the worst market days, not about average returns or volatility."
            },
            "ro": {
                "title": "Refugiu",
                "text": "Conform Baur și Lucey (2010), ce face dintr-un activ un refugiu?",
                "options": [
                    "Un randament mediu pozitiv",
                    "Corelație zero sau negativă cu piața în cele mai rele zile ale ei",
                    "Volatilitate mică în toate zilele",
                    "O ofertă fixă"
                ],
                "correctExplanation": "Un refugiu este necorelat sau corelat negativ cu piața în scăderile extreme.",
                "incorrectExplanation": "Definiția se referă la comportamentul din cele mai rele zile ale pieței, nu la randamentele medii sau la volatilitate."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Alternative assets",
                "text": "Which factor mainly separates cryptos from other asset classes in Pele et al. (2023)?",
                "options": [
                    "The tail factor of log returns",
                    "The mean return",
                    "The trading volume",
                    "The number of exchanges"
                ],
                "correctExplanation": "Classification methods place cryptos in a separate class mainly because of the tail factor, a feature-space factor that loads on quantiles, tail expectations, variance and stable tail and scale parameters, not a gap in Hill indices.",
                "incorrectExplanation": "The study uses tail, memory and moment factors; the tail factor drives the separation."
            },
            "ro": {
                "title": "Active alternative",
                "text": "Ce factor separă în principal cripto-activele de celelalte clase de active în Pele et al. (2023)?",
                "options": [
                    "Factorul de coadă al randamentelor log",
                    "Randamentul mediu",
                    "Volumul tranzacționat",
                    "Numărul de burse"
                ],
                "correctExplanation": "Metodele de clasificare plasează cripto-activele într-o clasă separată în principal din cauza factorului de coadă, un factor al spațiului caracteristicilor cu încărcări pe cuantile, așteptări în coadă, varianță și parametrii de coadă și de scală ai distribuției stabile, nu o diferență între indici Hill.",
                "incorrectExplanation": "Studiul folosește factorii de coadă, memorie și momente; factorul de coadă determină separarea."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Nonsynchronous closes",
                "text": "IBIT's daily OLS beta on Bitcoin is 0.93 and its weekly beta 1.01. Which daily estimator corrects the bias?",
                "options": [
                    "OLS with Newey-West standard errors",
                    "Dropping the weekend returns of Bitcoin",
                    "Generalised least squares",
                    "A Dimson sum beta with lead and lag terms"
                ],
                "correctExplanation": "Summing the coefficients on the lagged, current and next-day Bitcoin returns (Dimson, 1979) captures the moves that reach the ETF a day later; here the sum is about 1.00.",
                "incorrectExplanation": "Newey-West changes only the standard error, not the downward bias from nonsynchronous closes; the Dimson sum beta removes it."
            },
            "ro": {
                "title": "Închideri nesincrone",
                "text": "Beta OLS zilnic al IBIT față de Bitcoin este 0,93, iar beta săptămînal 1,01. Ce estimator zilnic corectează deplasarea?",
                "options": [
                    "OLS cu erori standard Newey-West",
                    "Eliminarea randamentelor de weekend ale Bitcoin",
                    "Cele mai mici pătrate generalizate",
                    "Beta sumă Dimson, cu termeni decalați și avansați"
                ],
                "correctExplanation": "Suma coeficienților randamentelor Bitcoin din ziua anterioară, din ziua curentă și din ziua următoare (Dimson, 1979) captează mișcările care ajung în ETF cu o zi întîrziere; aici suma este aproximativ 1,00.",
                "incorrectExplanation": "Newey-West schimbă doar eroarea standard, nu și deplasarea în jos din închiderile nesincrone; beta sumă Dimson o elimină."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the AI error: annualising crypto volatility",
                "text": "An AI assistant writes: \"Bitcoin's daily volatility is 3%, so its annualised volatility is 3% x sqrt(252) = 47.6%.\" What is wrong?",
                "options": [
                    "Volatility must be multiplied by 252, not by sqrt(252)",
                    "Crypto volatility cannot be annualised",
                    "Bitcoin trades every day of the year: use sqrt(365), which gives 57.3%",
                    "Daily volatility must be multiplied by sqrt(12)"
                ],
                "correctExplanation": "The factor is the square root of the number of returns per year; with 7-day trading that is 365, and 252 understates the volatility by about 17%.",
                "incorrectExplanation": "Count how many daily returns a year of Bitcoin data contains."
            },
            "ro": {
                "title": "Găsiți eroarea AI: anualizarea volatilității cripto",
                "text": "Un asistent AI scrie: „Volatilitatea zilnică a Bitcoin este 3%, deci volatilitatea anualizată este 3% x sqrt(252) = 47,6%.” Ce este greșit?",
                "options": [
                    "Volatilitatea trebuie înmulțită cu 252, nu cu sqrt(252)",
                    "Volatilitatea cripto nu poate fi anualizată",
                    "Bitcoin se tranzacționează în fiecare zi a anului: folosiți sqrt(365), ceea ce dă 57,3%",
                    "Volatilitatea zilnică trebuie înmulțită cu sqrt(12)"
                ],
                "correctExplanation": "Factorul este rădăcina pătrată a numărului de randamente pe an; cu tranzacționare 7 zile din 7 acesta este 365, iar 252 subestimează volatilitatea cu aproximativ 17%.",
                "incorrectExplanation": "Numărați cîte randamente zilnice conține un an de date Bitcoin."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: a riskless stablecoin",
                "text": "An AI assistant writes: \"USD Coin (USDC) is backed 1:1 by dollars, so its price is always exactly 1; lending USDC at 5% is therefore the risk-free rate for your Sharpe ratio.\" What is wrong?",
                "options": [
                    "USDC lost its peg in March 2023 (low of about 0.88) and lending adds platform risk; the risk-free rate is a Treasury bill yield",
                    "USDC is backed by Bitcoin, not by dollars",
                    "The only error is that lending USDC pays no interest",
                    "A Sharpe ratio must not subtract any risk-free rate"
                ],
                "correctExplanation": "After Silicon Valley Bank failed, USDC traded as low as about 0.88 on 11 March 2023; a yield above Treasury bills is a premium for issuer, peg and smart-contract risk.",
                "incorrectExplanation": "Check the claim against the USDC price history and the definition of a risk-free asset: no default and no price risk."
            },
            "ro": {
                "title": "Găsiți eroarea AI: un stablecoin fără risc",
                "text": "Un asistent AI scrie: „USD Coin (USDC) este acoperit 1:1 cu dolari, deci prețul lui este mereu exact 1; împrumutul de USDC la 5% este deci rata fără risc pentru raportul Sharpe.” Ce este greșit?",
                "options": [
                    "USDC și-a pierdut paritatea în martie 2023 (minim de aproximativ 0,88), iar împrumutul adaugă riscul platformei; rata fără risc este randamentul bonurilor de trezorerie",
                    "USDC este acoperit cu Bitcoin, nu cu dolari",
                    "Singura eroare este că împrumutul de USDC nu plătește dobîndă",
                    "Raportul Sharpe nu trebuie să scadă nicio rată fără risc"
                ],
                "correctExplanation": "După falimentul Silicon Valley Bank, USDC a coborît pînă la aproximativ 0,88 pe 11 martie 2023; un randament peste bonurile de trezorerie este o primă pentru riscul emitentului, al parității și al contractului inteligent.",
                "incorrectExplanation": "Verificați afirmația cu istoricul prețului USDC și cu definiția unui activ fără risc: fără risc de neplată și fără risc de preț."
            }
        }
    ]
};

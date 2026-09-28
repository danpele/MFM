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
            "correct": 0,
            "en": {
                "title": "Market value",
                "text": "How is the market value (market capitalisation) of a coin computed?",
                "options": [
                    "Price times the number of coins in circulation",
                    "Price times daily trading volume",
                    "Total value locked in DeFi protocols",
                    "Price divided by the number of coins mined per day"
                ],
                "correctExplanation": "M = P x Q: the price times the coins in circulation.",
                "incorrectExplanation": "Market value multiplies the price by the supply in circulation; volume and value locked measure other things."
            },
            "ro": {
                "title": "Valoarea de piață",
                "text": "Cum se calculează valoarea de piață (capitalizarea) unei monede?",
                "options": [
                    "Prețul înmulțit cu numărul de monede în circulație",
                    "Prețul înmulțit cu volumul zilnic tranzacționat",
                    "Valoarea totală blocată în protocoalele DeFi",
                    "Prețul împărțit la numărul de monede minate pe zi"
                ],
                "correctExplanation": "M = P x Q: prețul înmulțit cu monedele în circulație.",
                "incorrectExplanation": "Valoarea de piață înmulțește prețul cu oferta în circulație; volumul și valoarea blocată măsoară alte lucruri."
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
                    "Prețurile lor nu sunt disponibile",
                    "Sunt stablecoin-uri",
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
                "title": "Annualisation",
                "text": "How should the daily volatility of Bitcoin be annualised?",
                "options": [
                    "Multiply by 252",
                    "Multiply by the square root of 252",
                    "Multiply by 365",
                    "Multiply by the square root of 365"
                ],
                "correctExplanation": "Crypto trades every day, so sigma_a = s x sqrt(365).",
                "incorrectExplanation": "Volatility scales with the square root of the number of observations per year, and crypto has about 365."
            },
            "ro": {
                "title": "Anualizarea",
                "text": "Cum se anualizează volatilitatea zilnică a Bitcoin?",
                "options": [
                    "Se înmulțește cu 252",
                    "Se înmulțește cu rădăcina pătrată din 252",
                    "Se înmulțește cu 365",
                    "Se înmulțește cu rădăcina pătrată din 365"
                ],
                "correctExplanation": "Cripto se tranzacționează în fiecare zi, deci sigma_a = s x rad(365).",
                "incorrectExplanation": "Volatilitatea se scalează cu rădăcina pătrată a numărului de observații pe an, iar cripto are aproximativ 365."
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
                    "Weekendurile sunt zilele cele mai volatile",
                    "Efectul de weekend a apărut doar după ETF-urile spot",
                    "În weekend nu se tranzacționează"
                ],
                "correctExplanation": "Raportul dispersiilor weekend / zile lucrătoare a fost aproximativ 0,45 înainte și 0,39 după ianuarie 2024; modificarea nu este semnificativă.",
                "incorrectExplanation": "Bitcoin se tranzacționează în weekend, dar randamentele de weekend sunt mult mai calme, iar acest lucru era adevărat și înainte de ETF-uri."
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
                "text": "Când a devenit Bitcoin clar corelat pozitiv cu S&P 500?",
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
            "correct": 1,
            "en": {
                "title": "Index divisor",
                "text": "Why does a market-value weighted index change its divisor at a reallocation?",
                "options": [
                    "To pay the index fee",
                    "So that the index level does not jump when quantities or members change",
                    "To make the weights equal",
                    "To remove the largest coin"
                ],
                "correctExplanation": "The new divisor makes the old and the new basket give the same level on the switch day.",
                "incorrectExplanation": "The divisor is a continuity device; it does not charge fees or change the weighting scheme."
            },
            "ro": {
                "title": "Divizorul indicelui",
                "text": "De ce își schimbă un indice ponderat cu valoarea de piață divizorul la o realocare?",
                "options": [
                    "Pentru a plăti comisionul indicelui",
                    "Pentru ca nivelul indicelui să nu sară când se schimbă cantitățile sau membrii",
                    "Pentru a egaliza ponderile",
                    "Pentru a elimina cea mai mare monedă"
                ],
                "correctExplanation": "Noul divizor face ca vechiul și noul coș să dea același nivel în ziua schimbării.",
                "incorrectExplanation": "Divizorul asigură continuitatea; nu percepe comisioane și nu schimbă modul de ponderare."
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
                "text": "In AIC(k) = n ln(s_k^2) + 2k, when is a new constituent admitted?",
                "options": [
                    "When its price is rising",
                    "When it has the lowest volatility",
                    "Always",
                    "When it lowers n ln(s_k^2) by more than 2"
                ],
                "correctExplanation": "Each extra coin costs 2 in the penalty; it is admitted if the tracking improvement is larger.",
                "incorrectExplanation": "The rule compares the fall in n ln(s_k^2) with the penalty per constituent."
            },
            "ro": {
                "title": "Penalizarea AIC",
                "text": "În AIC(k) = n ln(s_k^2) + 2k, când este admis un constituent nou?",
                "options": [
                    "Când prețul lui crește",
                    "Când are cea mai mică volatilitate",
                    "Întotdeauna",
                    "Când scade n ln(s_k^2) cu mai mult de 2"
                ],
                "correctExplanation": "Fiecare monedă în plus costă 2 în penalizare; este admisă dacă îmbunătățirea urmăririi este mai mare.",
                "incorrectExplanation": "Regula compară scăderea lui n ln(s_k^2) cu penalizarea pe constituent."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Stablecoin designs",
                "text": "Which stablecoin design has no external collateral?",
                "options": [
                    "Fiat-backed",
                    "Crypto-backed",
                    "Algorithmic",
                    "Tokenised Treasury fund"
                ],
                "correctExplanation": "Algorithmic stablecoins such as TerraUSD kept the peg through a second token, not reserves.",
                "incorrectExplanation": "Fiat-backed coins hold deposits and bills, crypto-backed coins hold crypto collateral; only algorithmic designs have neither."
            },
            "ro": {
                "title": "Tipuri de stablecoin",
                "text": "Ce tip de stablecoin nu are garanții externe?",
                "options": [
                    "Acoperit cu fiat",
                    "Acoperit cu cripto-active",
                    "Algoritmic",
                    "Fondul tokenizat de titluri de stat"
                ],
                "correctExplanation": "Stablecoin-urile algoritmice precum TerraUSD își mențineau paritatea printr-un al doilea token, nu prin rezerve.",
                "incorrectExplanation": "Cele acoperite cu fiat dețin depozite și titluri, cele acoperite cu cripto dețin garanții cripto; doar cele algoritmice nu au niciuna."
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
                    "O parte din rezerve era expusă la Silicon Valley Bank, falimentată, iar răscumpărarea nu se putea deconta în weekend",
                    "Contractul inteligent a fost spart",
                    "Blockchain-ul Terra s-a oprit",
                    "Rezerva Federală a crescut dobânda în acea zi"
                ],
                "correctExplanation": "SVB a fost închisă pe 10 martie; USD Coin depindea de rezerve deținute acolo, iar băncile au fost închise până luni.",
                "incorrectExplanation": "Declanșatorul a fost un faliment bancar care afecta rezervele, nu un atac informatic sau o decizie de dobândă."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Half-life",
                "text": "An AR(1) fit to daily peg deviations gives phi = 0.5. What is the half-life?",
                "options": [
                    "0.5 days",
                    "2 days",
                    "5 days",
                    "1 day"
                ],
                "correctExplanation": "h = ln 0.5 / ln 0.5 = 1 day.",
                "incorrectExplanation": "Use h = ln 0.5 / ln phi."
            },
            "ro": {
                "title": "Timpul de înjumătățire",
                "text": "Un model AR(1) pentru abaterile zilnice de la paritate dă phi = 0,5. Care este timpul de înjumătățire?",
                "options": [
                    "0,5 zile",
                    "2 zile",
                    "5 zile",
                    "1 zi"
                ],
                "correctExplanation": "h = ln 0,5 / ln 0,5 = 1 zi.",
                "incorrectExplanation": "Folosiți h = ln 0,5 / ln phi."
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
                    "Răscumpărarea a creat mai mult din al doilea token (LUNA), împingându-i prețul în jos, fără garanții externe"
                ],
                "correctExplanation": "Fără rezerve, răscumpărările în LUNA au diluat LUNA și au slăbit și mai mult paritatea: o spirală a morții.",
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
                "text": "Cu comisionul f și gamma = 1 - f, cât Y primește un participant pentru Delta x?",
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
                "text": "Pentru un fond cu produs constant și volatilitatea prețului sigma, cu ce rată crește pierderea față de reechilibrare?",
                "options": [
                    "sigma",
                    "sigma / 2",
                    "sigma^2 / 2",
                    "sigma^2 / 8"
                ],
                "correctExplanation": "Milionis et al. (2022): LVR / V = sigma^2 / 8 pe unitatea de timp; cu sigma = 68% înseamnă aproximativ 5,8% pe an.",
                "incorrectExplanation": "Rata este pătratică în volatilitate, cu factorul o optime."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "TVL",
                "text": "Why is total value locked (TVL) in DeFi a weak measure of adoption?",
                "options": [
                    "It counts only Bitcoin",
                    "Deposits are valued at market prices, so TVL moves mostly with the Ether price",
                    "It is published only once a year",
                    "It excludes stablecoins"
                ],
                "correctExplanation": "Monthly TVL changes load on Ether returns with a slope near 0.8 and R^2 about 0.6.",
                "incorrectExplanation": "TVL is a market value: a price fall lowers it even if nobody withdraws."
            },
            "ro": {
                "title": "TVL",
                "text": "De ce este valoarea totală blocată (TVL) în DeFi o măsură slabă a adoptării?",
                "options": [
                    "Numără doar Bitcoin",
                    "Depozitele sunt evaluate la prețul pieței, deci TVL se mișcă în principal cu prețul Ether",
                    "Se publică doar o dată pe an",
                    "Exclude stablecoin-urile"
                ],
                "correctExplanation": "Variațiile lunare ale TVL depind de randamentele Ether cu o pantă de aproximativ 0,8 și R^2 de aproximativ 0,6.",
                "incorrectExplanation": "TVL este o valoare de piață: o scădere a prețului o reduce chiar dacă nimeni nu retrage."
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
                "text": "IBIT față de Bitcoin are R^2 zilnic de aproximativ 0,82, dar R^2 săptămânal de aproximativ 0,98. De ce?",
                "options": [
                    "Cele două prețuri de închidere sunt înregistrate la ore diferite; nepotrivirea se compensează într-o săptămână",
                    "IBIT deține contracte futures, nu Bitcoin",
                    "IBIT se tranzacționează în weekend",
                    "Bitcoin este mai puțin volatil săptămânal"
                ],
                "correctExplanation": "Randamentele zilnice compară prețuri din momente diferite; randamentele săptămânale reduc zgomotul de moment.",
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
                "title": "Deriva din comision",
                "text": "Logaritmul raportului IBIT / Bitcoin scade cu aproximativ 0,24% pe an. Ce explică această scădere?",
                "options": [
                    "O primă care crește în timp",
                    "Tranzacționarea din weekend",
                    "Comisionul anual de 0,25% plătit din Bitcoin-ul deținut",
                    "Creșterea ofertei de Bitcoin"
                ],
                "correctExplanation": "Fondul vinde Bitcoin pentru a-și plăti comisionul, deci Bitcoin-ul pe unitate scade cu aproximativ rata comisionului.",
                "incorrectExplanation": "Deriva corespunde comisionului, nu unei prime sau unui efect de ofertă."
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
                "text": "O regresie săptămânală cu doi factori dă pentru Strategy un beta față de Bitcoin de aproximativ 1,2 și un beta față de S&P 500 de aproximativ 1,0. Care este cea mai bună descriere?",
                "options": [
                    "Un instrument care urmărește pur Bitcoin",
                    "O acțiune defensivă",
                    "O acțiune necorelată cu cripto",
                    "O poziție în Bitcoin cu efect de levier, plus riscul pieței de acțiuni"
                ],
                "correctExplanation": "Un beta peste 1 față de Bitcoin plus un beta de acțiune: mai mult decât expunerea la Bitcoin, plus riscul bursei.",
                "incorrectExplanation": "Ambii beta sunt importanți, deci acțiunea nu este nici un instrument pur, nici defensivă."
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
                "correctExplanation": "Classification methods place cryptos in a separate class mainly because of the tail factor.",
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
                "correctExplanation": "Metodele de clasificare plasează cripto-activele într-o clasă separată în principal din cauza factorului de coadă.",
                "incorrectExplanation": "Studiul folosește factorii de coadă, memorie și momente; factorul de coadă determină separarea."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Risk in numbers",
                "text": "Historical daily VaR 1% for Bitcoin (2018-2026) is about 10% and for the S&P 500 about 3.4%. What does VaR 1% mean here?",
                "options": [
                    "The average loss on the worst 1% of days",
                    "The largest loss ever observed",
                    "The loss exceeded on 1% of days",
                    "The loss with a 99% probability"
                ],
                "correctExplanation": "VaR 1% = -q_1%(r): a loss exceeded with probability 1%.",
                "incorrectExplanation": "VaR 1% is a quantile; the average beyond it is ES."
            },
            "ro": {
                "title": "Riscul în cifre",
                "text": "VaR 1% zilnic istoric pentru Bitcoin (2018-2026) este aproximativ 10%, iar pentru S&P 500 aproximativ 3,4%. Ce înseamnă aici VaR 1%?",
                "options": [
                    "Pierderea medie în cele mai rele 1% dintre zile",
                    "Cea mai mare pierdere observată vreodată",
                    "Pierderea depășită în 1% din zile",
                    "Pierderea cu probabilitatea de 99%"
                ],
                "correctExplanation": "VaR 1% = -q_1%(r): o pierdere depășită cu probabilitatea de 1%.",
                "incorrectExplanation": "VaR 1% este o cuantilă; media de dincolo de ea este ES."
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
                "incorrectExplanation": "Numărați câte randamente zilnice conține un an de date Bitcoin."
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
                    "Singura eroare este că împrumutul de USDC nu plătește dobândă",
                    "Raportul Sharpe nu trebuie să scadă nicio rată fără risc"
                ],
                "correctExplanation": "După falimentul Silicon Valley Bank, USDC a coborât până la aproximativ 0,88 pe 11 martie 2023; un randament peste bonurile de trezorerie este o primă pentru riscul emitentului, al parității și al contractului inteligent.",
                "incorrectExplanation": "Verificați afirmația cu istoricul prețului USDC și cu definiția unui activ fără risc: fără risc de neplată și fără risc de preț."
            }
        }
    ]
};

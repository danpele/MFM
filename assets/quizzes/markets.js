// ============================================================
// Chapter 0 quiz bank: Financial Markets in 2026 (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['markets'] = {
    draw: 20,
    questions: [
        {
            "correct": 2,
            "en": {
                "title": "Price discovery",
                "text": "Which function of financial markets is described as \"prices aggregate information that is dispersed among many participants\"?",
                "options": [
                    "Payments and settlement",
                    "Capital allocation",
                    "Price discovery",
                    "Monitoring of managers"
                ],
                "correctExplanation": "Price discovery: trading reveals and combines the private information of many participants into a single price.",
                "incorrectExplanation": "The phrase describes price discovery, the way trading combines dispersed information into prices."
            },
            "ro": {
                "title": "Descoperirea prețului",
                "text": "Care funcție a piețelor financiare este descrisă de afirmația „prețurile agregă informația dispersată între mulți participanți”?",
                "options": [
                    "Plăți și decontare",
                    "Alocarea capitalului",
                    "Descoperirea prețului",
                    "Monitorizarea managerilor"
                ],
                "correctExplanation": "Descoperirea prețului: tranzacționarea dezvăluie și combină informația privată a multor participanți într-un singur preț.",
                "incorrectExplanation": "Afirmația descrie descoperirea prețului, modul în care tranzacționarea combină informația dispersată în prețuri."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Exchanges vs OTC",
                "text": "Which asset classes trade mainly over the counter (OTC), through bilateral deals with dealers?",
                "options": [
                    "Bonds, FX and swaps",
                    "Large-cap stocks on NYSE",
                    "Equity ETFs",
                    "Bitcoin on centralised exchanges"
                ],
                "correctExplanation": "Most bond, FX and swap trading is bilateral with dealers, with less pre-trade transparency than an exchange order book.",
                "incorrectExplanation": "Bonds, FX and swaps are the classic OTC markets; stocks and ETFs trade mainly on exchanges."
            },
            "ro": {
                "title": "Burse vs OTC",
                "text": "Ce clase de active se tranzacționează în principal la ghișeu (OTC), prin tranzacții bilaterale cu dealeri?",
                "options": [
                    "Obligațiuni, valută și swap-uri",
                    "Acțiunile mari de pe NYSE",
                    "ETF-urile pe acțiuni",
                    "Bitcoin pe exchange-uri centralizate"
                ],
                "correctExplanation": "Cea mai mare parte a tranzacțiilor cu obligațiuni, valută și swap-uri este bilaterală, cu dealeri, cu mai puțină transparență decât un registru de ordine.",
                "incorrectExplanation": "Obligațiunile, valuta și swap-urile sunt piețele OTC clasice; acțiunile și ETF-urile se tranzacționează mai ales la bursă."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Limit and market orders",
                "text": "Which statement about order types is correct?",
                "options": [
                    "A market order waits in the book and provides liquidity",
                    "A limit order waits in the book and provides liquidity; a market order consumes it",
                    "A stop order always executes at the stop price",
                    "Limit orders always execute immediately"
                ],
                "correctExplanation": "Limit orders rest in the order book at a chosen price; market orders execute immediately against the best quotes and take that liquidity.",
                "incorrectExplanation": "Limit orders provide liquidity by waiting in the book; market orders consume it by executing immediately."
            },
            "ro": {
                "title": "Ordine limită și la piață",
                "text": "Care afirmație despre tipurile de ordine este corectă?",
                "options": [
                    "Un ordin la piață așteaptă în registru și oferă lichiditate",
                    "Un ordin limită așteaptă în registru și oferă lichiditate; un ordin la piață o consumă",
                    "Un ordin stop se execută întotdeauna la prețul stop",
                    "Ordinele limită se execută întotdeauna imediat"
                ],
                "correctExplanation": "Ordinele limită stau în registru la un preț ales; ordinele la piață se execută imediat la cele mai bune cotații și consumă acea lichiditate.",
                "incorrectExplanation": "Ordinele limită oferă lichiditate, așteptând în registru; ordinele la piață o consumă, executându-se imediat."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Bid-ask spread",
                "text": "What is the bid-ask spread?",
                "options": [
                    "The difference between the day's high and low",
                    "The commission paid to the broker",
                    "The difference between two exchanges' prices",
                    "Best ask minus best bid: the price paid for immediate execution"
                ],
                "correctExplanation": "The spread is the gap between the lowest price at which someone will sell and the highest price at which someone will buy: the cost of immediacy.",
                "incorrectExplanation": "The bid-ask spread is best ask minus best bid, the cost of trading immediately."
            },
            "ro": {
                "title": "Spread-ul bid-ask",
                "text": "Ce este spread-ul bid-ask?",
                "options": [
                    "Diferența dintre maximul și minimul zilei",
                    "Comisionul plătit brokerului",
                    "Diferența dintre prețurile a două burse",
                    "Cea mai bună ofertă de vânzare minus cea mai bună ofertă de cumpărare: prețul execuției imediate"
                ],
                "correctExplanation": "Spread-ul este diferența dintre cel mai mic preț la care cineva vinde și cel mai mare preț la care cineva cumpără: costul imediateței.",
                "incorrectExplanation": "Spread-ul bid-ask este cea mai bună ofertă de vânzare minus cea mai bună ofertă de cumpărare, costul tranzacționării imediate."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Closing auctions",
                "text": "Why do most daily return series in this course use the closing-auction price?",
                "options": [
                    "The closing auction concentrates liquidity and sets one reference price for the day",
                    "It is always the highest price of the day",
                    "It removes all volatility",
                    "Continuous trading stops working at the close"
                ],
                "correctExplanation": "A call auction collects orders and matches them at a single price, which makes the close a liquid and less noisy reference price.",
                "incorrectExplanation": "The close comes from a call auction that concentrates liquidity into one reference price."
            },
            "ro": {
                "title": "Licitația de închidere",
                "text": "De ce majoritatea seriilor de randamente zilnice din curs folosesc prețul din licitația de închidere?",
                "options": [
                    "Licitația de închidere concentrează lichiditatea și stabilește un singur preț de referință pentru zi",
                    "Este întotdeauna cel mai mare preț al zilei",
                    "Elimină toată volatilitatea",
                    "Tranzacționarea continuă nu mai funcționează la închidere"
                ],
                "correctExplanation": "O licitație colectează ordinele și le execută la un singur preț, deci prețul de închidere este o referință lichidă și mai puțin zgomotoasă.",
                "incorrectExplanation": "Prețul de închidere provine dintr-o licitație care concentrează lichiditatea într-un singur preț de referință."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Drawdown",
                "text": "The S&P 500 drawdown reached its deepest point of 2000–2026 on 9 March 2009. How large was it?",
                "options": [
                    "About -34%",
                    "About -25%",
                    "About -57%",
                    "About -91%"
                ],
                "correctExplanation": "Measured from the October 2007 peak, the S&P 500 lost about 57% by 9 March 2009 (Global Financial Crisis).",
                "incorrectExplanation": "The Global Financial Crisis drawdown was about -57%; -34% was COVID-19 (March 2020) and -25% the 2022 inflation shock."
            },
            "ro": {
                "title": "Drawdown",
                "text": "Drawdown-ul S&P 500 a atins cel mai adânc nivel din 2000–2026 pe 9 martie 2009. Cât a fost?",
                "options": [
                    "Circa -34%",
                    "Circa -25%",
                    "Circa -57%",
                    "Circa -91%"
                ],
                "correctExplanation": "Măsurat de la maximul din octombrie 2007, S&P 500 a pierdut circa 57% până pe 9 martie 2009 (criza financiară globală).",
                "incorrectExplanation": "Drawdown-ul crizei financiare globale a fost de circa -57%; -34% a fost COVID-19 (martie 2020), iar -25% șocul inflaționist din 2022."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "VIX regimes",
                "text": "Since 2000, on roughly what share of trading days was the VIX below 20?",
                "options": [
                    "About 9%",
                    "About 62%",
                    "About 29%",
                    "About 95%"
                ],
                "correctExplanation": "The VIX was below 20 on about 62% of days and above 30 on only about 9%: calm most of the time, with short violent spikes.",
                "incorrectExplanation": "In our data the VIX was below 20 on about 62% of days since 2000."
            },
            "ro": {
                "title": "Regimurile VIX",
                "text": "Din 2000, în aproximativ ce proporție din zilele de tranzacționare a fost VIX sub 20?",
                "options": [
                    "Circa 9%",
                    "Circa 62%",
                    "Circa 29%",
                    "Circa 95%"
                ],
                "correctExplanation": "VIX a fost sub 20 în circa 62% din zile și peste 30 doar în circa 9%: calm în cea mai mare parte a timpului, cu vârfuri scurte și violente.",
                "incorrectExplanation": "În datele noastre, VIX a fost sub 20 în circa 62% din zile din 2000."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Yield-curve inversion",
                "text": "What does a negative US 10-year minus 2-year Treasury spread (persistently from July 2022 to August 2024 in our data) mean?",
                "options": [
                    "Long-term rates were above short-term rates",
                    "The Fed had cut rates to zero",
                    "Bond prices could not fall",
                    "Short-term yields were above long-term yields: an inverted yield curve"
                ],
                "correctExplanation": "When the 2-year yield exceeds the 10-year yield the curve is inverted; in our data, after a brief dip on 1-4 April 2022, the persistent inversion ran from 6 July 2022 to 26 August 2024 (537 trading days), with a minimum of -1.08 pp on 3 July 2023.",
                "incorrectExplanation": "A negative 10y-2y spread means short-term yields exceed long-term yields, an inverted curve."
            },
            "ro": {
                "title": "Inversarea curbei randamentelor",
                "text": "Ce înseamnă un spread negativ între randamentul titlurilor de stat americane pe 10 ani și cel pe 2 ani (persistent din iulie 2022 până în august 2024 în datele noastre)?",
                "options": [
                    "Dobânzile pe termen lung erau peste cele pe termen scurt",
                    "Fed redusese dobânda la zero",
                    "Prețurile obligațiunilor nu puteau scădea",
                    "Randamentele pe termen scurt erau peste cele pe termen lung: o curbă inversată"
                ],
                "correctExplanation": "Când randamentul pe 2 ani depășește randamentul pe 10 ani, curba este inversată; în datele noastre, după o scurtă inversare pe 1-4 aprilie 2022, inversarea persistentă a durat de pe 6 iulie 2022 până pe 26 august 2024 (537 de zile de tranzacționare), cu un minim de -1,08 pp pe 3 iulie 2023.",
                "incorrectExplanation": "Un spread 10 ani -- 2 ani negativ înseamnă că randamentele pe termen scurt le depășesc pe cele pe termen lung, o curbă inversată."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Stock-bond correlation",
                "text": "The average 1-year rolling correlation between S&P 500 and long Treasury (TLT) returns was -0.43 in 2010–2020 and +0.08 in 2022–2026. What does this imply?",
                "options": [
                    "Long bonds hedged equity losses less well after the 2022 inflation shock",
                    "Bonds became riskier than Bitcoin",
                    "Correlations are constant over time",
                    "Equities and bonds now always move in opposite directions"
                ],
                "correctExplanation": "A negative stock-bond correlation makes bonds a hedge; when it turned positive, bonds and equities fell together, as in 2022.",
                "incorrectExplanation": "The move from -0.43 to +0.08 means bonds lost much of their hedging value after 2022."
            },
            "ro": {
                "title": "Corelația acțiuni-obligațiuni",
                "text": "Corelația mobilă pe 1 an dintre randamentele S&P 500 și ale obligațiunilor Trezoreriei pe termen lung (TLT) a fost în medie -0,43 în 2010–2020 și +0,08 în 2022–2026. Ce implică acest lucru?",
                "options": [
                    "Obligațiunile pe termen lung au protejat mai slab pierderile la acțiuni după șocul inflaționist din 2022",
                    "Obligațiunile au devenit mai riscante decât Bitcoin",
                    "Corelațiile sunt constante în timp",
                    "Acțiunile și obligațiunile se mișcă acum mereu în sens opus"
                ],
                "correctExplanation": "O corelație negativă acțiuni-obligațiuni face din obligațiuni o acoperire; când a devenit pozitivă, obligațiunile și acțiunile au scăzut împreună, ca în 2022.",
                "incorrectExplanation": "Trecerea de la -0,43 la +0,08 înseamnă că obligațiunile și-au pierdut mult din valoarea de acoperire după 2022."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Bitcoin and equities",
                "text": "In our data the average rolling correlation between Bitcoin and the S&P 500 rose from 0.01 (2016–2019) to 0.38 (2022–2026). What is the implication for a portfolio?",
                "options": [
                    "Bitcoin became a perfect hedge for equities",
                    "Bitcoin volatility fell to equity levels",
                    "Bitcoin offers less diversification against equity risk than it used to",
                    "The correlation proves that Bitcoin is a stock"
                ],
                "correctExplanation": "A higher correlation means Bitcoin tends to fall when equities fall, so its diversification benefit has shrunk.",
                "incorrectExplanation": "Rising correlation reduces the diversification benefit; it does not make Bitcoin a hedge or a stock."
            },
            "ro": {
                "title": "Bitcoin și acțiunile",
                "text": "În datele noastre, corelația mobilă medie dintre Bitcoin și S&P 500 a crescut de la 0,01 (2016–2019) la 0,38 (2022–2026). Ce implică acest lucru pentru un portofoliu?",
                "options": [
                    "Bitcoin a devenit o acoperire perfectă pentru acțiuni",
                    "Volatilitatea Bitcoin a scăzut la nivelul acțiunilor",
                    "Bitcoin oferă mai puțină diversificare față de riscul acțiunilor decât înainte",
                    "Corelația dovedește că Bitcoin este o acțiune"
                ],
                "correctExplanation": "O corelație mai mare înseamnă că Bitcoin tinde să scadă când scad acțiunile, deci beneficiul de diversificare s-a redus.",
                "incorrectExplanation": "Creșterea corelației reduce beneficiul de diversificare; nu face din Bitcoin o acoperire sau o acțiune."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Annualisation",
                "text": "A daily volatility of 1% is annualised. Which pair of results is correct for an equity index and for Bitcoin?",
                "options": [
                    "15.87% for both",
                    "15.87% for equities (252 days), 19.10% for Bitcoin (365 days)",
                    "19.10% for equities, 15.87% for Bitcoin",
                    "252% and 365%"
                ],
                "correctExplanation": "Volatility scales with the square root of time: 1% x sqrt(252) = 15.87% for equities and 1% x sqrt(365) = 19.10% for crypto, which trades every day.",
                "incorrectExplanation": "Use sqrt(252) for equities and sqrt(365) for crypto: 15.87% and 19.10%."
            },
            "ro": {
                "title": "Anualizare",
                "text": "O volatilitate zilnică de 1% este anualizată. Care pereche de rezultate este corectă pentru un indice de acțiuni și pentru Bitcoin?",
                "options": [
                    "15,87% pentru ambele",
                    "15,87% pentru acțiuni (252 de zile), 19,10% pentru Bitcoin (365 de zile)",
                    "19,10% pentru acțiuni, 15,87% pentru Bitcoin",
                    "252% și 365%"
                ],
                "correctExplanation": "Volatilitatea crește cu rădăcina pătrată a timpului: 1% x sqrt(252) = 15,87% pentru acțiuni și 1% x sqrt(365) = 19,10% pentru cripto, care se tranzacționează zilnic.",
                "incorrectExplanation": "Folosiți sqrt(252) pentru acțiuni și sqrt(365) pentru cripto: 15,87% și 19,10%."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Concentration",
                "text": "The ratio SPY / RSP (cap-weighted over equal-weighted S&P 500 ETF) rose by about 31% from January 2023 to September 2026. What does this indicate?",
                "options": [
                    "Small firms outperformed large firms",
                    "The S&P 500 fell in value",
                    "ETFs stopped tracking the index",
                    "The largest firms outperformed the average stock: the index became more concentrated"
                ],
                "correctExplanation": "The cap-weighted fund gives more weight to the largest companies; its outperformance means those companies drove index returns.",
                "incorrectExplanation": "A rising SPY/RSP ratio means the largest firms outperformed the typical stock."
            },
            "ro": {
                "title": "Concentrare",
                "text": "Raportul SPY / RSP (ETF pe S&P 500 ponderat după capitalizare față de cel cu ponderi egale) a crescut cu circa 31% din ianuarie 2023 până în septembrie 2026. Ce indică acest lucru?",
                "options": [
                    "Firmele mici au avut randamente mai bune decât cele mari",
                    "S&P 500 a scăzut",
                    "ETF-urile nu mai replică indicele",
                    "Firmele cele mai mari au depășit acțiunea medie: indicele a devenit mai concentrat"
                ],
                "correctExplanation": "Fondul ponderat după capitalizare dă o pondere mai mare celor mai mari companii; performanța sa superioară înseamnă că acestea au condus randamentul indicelui.",
                "incorrectExplanation": "Un raport SPY/RSP în creștere înseamnă că firmele cele mai mari au depășit acțiunea tipică."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "ETF creation and redemption",
                "text": "What keeps an ETF's market price close to its net asset value?",
                "options": [
                    "Authorised participants exchange baskets of the underlying assets for ETF shares (and back) when prices diverge",
                    "The exchange fixes the ETF price every day",
                    "The ETF issuer guarantees the price",
                    "ETFs cannot trade during the day"
                ],
                "correctExplanation": "Creation and redemption by authorised participants is an arbitrage mechanism: if the ETF trades above its NAV they create shares, if below they redeem.",
                "incorrectExplanation": "The creation/redemption mechanism run by authorised participants keeps the price close to NAV."
            },
            "ro": {
                "title": "Crearea și răscumpărarea unităților ETF",
                "text": "Ce menține prețul de piață al unui ETF aproape de valoarea activului net?",
                "options": [
                    "Participanții autorizați schimbă coșuri de active suport pe unități ETF (și invers) când prețurile se îndepărtează",
                    "Bursa fixează zilnic prețul ETF-ului",
                    "Emitentul ETF garantează prețul",
                    "ETF-urile nu se pot tranzacționa în timpul zilei"
                ],
                "correctExplanation": "Crearea și răscumpărarea de către participanții autorizați este un mecanism de arbitraj: dacă ETF-ul se tranzacționează peste NAV, ei creează unități; dacă este sub, le răscumpără.",
                "incorrectExplanation": "Mecanismul de creare/răscumpărare derulat de participanții autorizați ține prețul aproape de NAV."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "ETFs and volatility",
                "text": "What do Ben-David, Franzoni and Moussawi (2018) find about ETF ownership?",
                "options": [
                    "Stocks owned by ETFs are less volatile",
                    "ETF ownership has no effect on stocks",
                    "Stocks with higher ETF ownership are more volatile",
                    "ETFs eliminate the bid-ask spread"
                ],
                "correctExplanation": "Their evidence is that higher ETF ownership is associated with higher volatility of the underlying stocks, through arbitrage trades that propagate liquidity shocks.",
                "incorrectExplanation": "The paper finds that higher ETF ownership increases the volatility of the underlying stocks."
            },
            "ro": {
                "title": "ETF-uri și volatilitate",
                "text": "Ce arată Ben-David, Franzoni și Moussawi (2018) despre deținerile ETF?",
                "options": [
                    "Acțiunile deținute de ETF-uri sunt mai puțin volatile",
                    "Deținerile ETF nu au niciun efect asupra acțiunilor",
                    "Acțiunile cu deținere ETF mai mare sunt mai volatile",
                    "ETF-urile elimină spread-ul bid-ask"
                ],
                "correctExplanation": "Rezultatul lor este că o deținere ETF mai mare este asociată cu o volatilitate mai mare a acțiunilor suport, prin tranzacții de arbitraj care propagă șocurile de lichiditate.",
                "incorrectExplanation": "Articolul arată că o deținere ETF mai mare crește volatilitatea acțiunilor suport."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot Bitcoin ETFs",
                "text": "When did the US SEC approve spot Bitcoin exchange-traded products?",
                "options": [
                    "January 2009",
                    "November 2021",
                    "March 2020",
                    "January 2024"
                ],
                "correctExplanation": "The SEC approved spot Bitcoin ETPs on 10 January 2024; IBIT started trading on 11 January 2024.",
                "incorrectExplanation": "The approval came on 10 January 2024."
            },
            "ro": {
                "title": "ETF-uri pe Bitcoin spot",
                "text": "Când a aprobat SEC produsele tranzacționate la bursă pe Bitcoin spot?",
                "options": [
                    "Ianuarie 2009",
                    "Noiembrie 2021",
                    "Martie 2020",
                    "Ianuarie 2024"
                ],
                "correctExplanation": "SEC a aprobat ETP-urile pe Bitcoin spot pe 10 ianuarie 2024; IBIT a început tranzacționarea pe 11 ianuarie 2024.",
                "incorrectExplanation": "Aprobarea a venit pe 10 ianuarie 2024."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "IBIT",
                "text": "Since its launch, what has been the median daily traded value (price x volume) of the IBIT spot Bitcoin ETF in our data?",
                "options": [
                    "About 2 bn USD",
                    "About 20 million USD",
                    "About 200 bn USD",
                    "It is not traded on an exchange"
                ],
                "correctExplanation": "The median daily traded value was about 1.97 bn USD, with a peak of 10.3 bn USD on 5 February 2026.",
                "incorrectExplanation": "In our data the median daily traded value is about 2 bn USD."
            },
            "ro": {
                "title": "IBIT",
                "text": "De la lansare, care a fost valoarea tranzacționată zilnică mediană (preț x volum) a ETF-ului spot pe Bitcoin IBIT în datele noastre?",
                "options": [
                    "Circa 2 mld. USD",
                    "Circa 20 mil. USD",
                    "Circa 200 mld. USD",
                    "Nu se tranzacționează la bursă"
                ],
                "correctExplanation": "Valoarea tranzacționată zilnică mediană a fost de circa 1,97 mld. USD, cu un maxim de 10,3 mld. USD pe 5 februarie 2026.",
                "incorrectExplanation": "În datele noastre, valoarea tranzacționată zilnică mediană este de circa 2 mld. USD."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Stablecoins",
                "text": "Total USD-pegged stablecoin supply peaked at 187.4 bn USD on 2 April 2022 and fell to 122.7 bn USD on 19 August 2023. What happened in between?",
                "options": [
                    "Stablecoins were banned worldwide",
                    "The Fed issued a digital dollar",
                    "Supply contracted after the collapse of the algorithmic stablecoin TerraUSD and during the 2022 crypto downturn",
                    "Nothing: the numbers refer to different coins"
                ],
                "correctExplanation": "The 2022 decline followed the TerraUSD collapse and the wider crypto downturn; supply then recovered to about 310 bn USD by September 2026.",
                "incorrectExplanation": "Supply shrank after the TerraUSD collapse and the 2022 crypto downturn, then recovered."
            },
            "ro": {
                "title": "Stablecoins",
                "text": "Oferta totală de stablecoins legate de USD a atins maximul de 187,4 mld. USD pe 2 aprilie 2022 și a scăzut la 122,7 mld. USD pe 19 august 2023. Ce s-a întâmplat între timp?",
                "options": [
                    "Stablecoin-urile au fost interzise la nivel mondial",
                    "Fed a emis un dolar digital",
                    "Oferta s-a contractat după prăbușirea stablecoin-ului algoritmic TerraUSD și în timpul declinului cripto din 2022",
                    "Nimic: cifrele se referă la monede diferite"
                ],
                "correctExplanation": "Scăderea din 2022 a urmat prăbușirii TerraUSD și declinului general al pieței cripto; oferta a revenit apoi la circa 310 mld. USD în septembrie 2026.",
                "incorrectExplanation": "Oferta s-a redus după prăbușirea TerraUSD și declinul cripto din 2022, apoi și-a revenit."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "MiCA",
                "text": "What is MiCA?",
                "options": [
                    "A US law on spot Bitcoin ETFs",
                    "The EU Regulation (EU) 2023/1114 on markets in crypto-assets",
                    "A crypto exchange",
                    "A stablecoin issued by the ECB"
                ],
                "correctExplanation": "MiCA, Regulation (EU) 2023/1114, is the EU framework for crypto-asset issuers and service providers, including stablecoins.",
                "incorrectExplanation": "MiCA is the EU crypto-asset regulation, Regulation (EU) 2023/1114."
            },
            "ro": {
                "title": "MiCA",
                "text": "Ce este MiCA?",
                "options": [
                    "O lege americană privind ETF-urile pe Bitcoin spot",
                    "Regulamentul (UE) 2023/1114 privind piețele criptoactivelor",
                    "Un exchange cripto",
                    "Un stablecoin emis de BCE"
                ],
                "correctExplanation": "MiCA, Regulamentul (UE) 2023/1114, este cadrul UE pentru emitenții și furnizorii de servicii de criptoactive, inclusiv stablecoins.",
                "incorrectExplanation": "MiCA este regulamentul UE privind criptoactivele, Regulamentul (UE) 2023/1114."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Tokenisation",
                "text": "In the BIS view of a \"unified ledger\", what is tokenised?",
                "options": [
                    "Only cryptocurrencies such as Bitcoin",
                    "Only stock-exchange shares",
                    "Only central bank reserves",
                    "Central bank money, commercial bank deposits and other assets on a shared programmable platform"
                ],
                "correctExplanation": "The BIS blueprint combines tokenised central bank money, deposits and assets on one ledger, so transfers and settlement become programmable.",
                "incorrectExplanation": "The unified ledger brings central bank money, deposits and assets together on one programmable platform."
            },
            "ro": {
                "title": "Tokenizare",
                "text": "În viziunea BIS despre un „registru unificat”, ce este tokenizat?",
                "options": [
                    "Doar criptomonede precum Bitcoin",
                    "Doar acțiunile listate la bursă",
                    "Doar rezervele la banca centrală",
                    "Banii de bancă centrală, depozitele bancare și alte active, pe o platformă comună programabilă"
                ],
                "correctExplanation": "Proiectul BIS combină bani de bancă centrală, depozite și active tokenizate pe un singur registru, astfel încât transferurile și decontarea devin programabile.",
                "incorrectExplanation": "Registrul unificat reunește banii de bancă centrală, depozitele și activele pe o platformă programabilă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "BET-TR",
                "text": "Since January 2015, BET-TR multiplied by about 10.4 in our data. What is the difference between BET and BET-TR?",
                "options": [
                    "BET-TR reinvests dividends (total return); BET is a price index",
                    "BET-TR contains only banks",
                    "BET-TR is quoted in euro",
                    "There is no difference"
                ],
                "correctExplanation": "A total-return index assumes dividends are reinvested, so it grows faster than the price index when companies pay high dividends, as many Romanian blue chips do.",
                "incorrectExplanation": "BET-TR is the total-return version of BET: dividends are reinvested."
            },
            "ro": {
                "title": "BET-TR",
                "text": "Din ianuarie 2015, BET-TR s-a multiplicat de circa 10,4 ori în datele noastre. Care este diferența dintre BET și BET-TR?",
                "options": [
                    "BET-TR reinvestește dividendele (randament total); BET este un indice de preț",
                    "BET-TR conține doar bănci",
                    "BET-TR este cotat în euro",
                    "Nu există nicio diferență"
                ],
                "correctExplanation": "Un indice de randament total presupune reinvestirea dividendelor, deci crește mai repede decât indicele de preț când companiile plătesc dividende mari, cum fac multe blue chips românești.",
                "incorrectExplanation": "BET-TR este varianta de randament total a BET: dividendele sunt reinvestite."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Romania in index classifications",
                "text": "How does FTSE Russell classify the Romanian equity market (April 2026 announcement)?",
                "options": [
                    "Developed",
                    "Frontier",
                    "Secondary Emerging",
                    "Unclassified"
                ],
                "correctExplanation": "FTSE Russell lists Romania in the Secondary Emerging category of its equity country classification.",
                "incorrectExplanation": "Romania is classified as Secondary Emerging by FTSE Russell."
            },
            "ro": {
                "title": "România în clasificările de indici",
                "text": "Cum clasifică FTSE Russell piața de acțiuni din România (anunțul din aprilie 2026)?",
                "options": [
                    "Dezvoltată",
                    "De frontieră",
                    "Secondary Emerging",
                    "Neclasificată"
                ],
                "correctExplanation": "FTSE Russell include România în categoria Secondary Emerging a clasificării pe țări a piețelor de acțiuni.",
                "incorrectExplanation": "România este clasificată ca Secondary Emerging de FTSE Russell."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Bad ticks",
                "text": "The EUR/RON market file gives an annualised volatility of 12.1% for 2015–2026, while the BNR reference rate gives 2.1%. Why?",
                "options": [
                    "The reference rate is a 30-day moving average of market quotes",
                    "The market file contains isolated bad ticks (e.g. +/-15% on 13–14 August 2025) that reverse the next day",
                    "EUR/RON is more volatile in the morning",
                    "The two series use different currencies"
                ],
                "correctExplanation": "A few spikes that reverse the next day inflate the standard deviation more than five-fold; removing weekend rows and outliers gives about 2.5%.",
                "incorrectExplanation": "Isolated bad ticks that reverse the next day inflate the measured volatility."
            },
            "ro": {
                "title": "Cotații eronate",
                "text": "Fișierul de piață EUR/RON dă o volatilitate anualizată de 12,1% pentru 2015–2026, iar cursul de referință BNR dă 2,1%. De ce?",
                "options": [
                    "Cursul de referință este o medie mobilă pe 30 de zile a cotațiilor de piață",
                    "Fișierul de piață conține cotații eronate izolate (de exemplu +/-15% pe 13–14 august 2025), inversate a doua zi",
                    "EUR/RON este mai volatil dimineața",
                    "Cele două serii folosesc monede diferite"
                ],
                "correctExplanation": "Câteva vârfuri inversate a doua zi umflă abaterea standard de peste cinci ori; eliminând rândurile de weekend și valorile aberante se obține circa 2,5%.",
                "incorrectExplanation": "Cotațiile eronate izolate, inversate a doua zi, umflă volatilitatea măsurată."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Adjusted prices",
                "text": "Which price field should be used to compute returns of stocks and ETFs such as SPY or Banca Transilvania?",
                "options": [
                    "The opening price",
                    "The unadjusted close",
                    "The daily high",
                    "The adjusted close, which accounts for dividends and splits"
                ],
                "correctExplanation": "Adjusted prices include dividends and split corrections, so returns reflect what an investor actually earned.",
                "incorrectExplanation": "Use the adjusted close for stocks and ETFs; unadjusted prices show false drops on dividend and split dates."
            },
            "ro": {
                "title": "Prețuri ajustate",
                "text": "Ce câmp de preț trebuie folosit pentru randamentele acțiunilor și ale ETF-urilor, precum SPY sau Banca Transilvania?",
                "options": [
                    "Prețul de deschidere",
                    "Prețul de închidere neajustat",
                    "Maximul zilei",
                    "Prețul de închidere ajustat, care ține cont de dividende și split-uri"
                ],
                "correctExplanation": "Prețurile ajustate includ dividendele și corecțiile pentru split-uri, deci randamentele reflectă ce a câștigat efectiv investitorul.",
                "incorrectExplanation": "Folosiți prețul de închidere ajustat pentru acțiuni și ETF-uri; prețurile neajustate arată scăderi false la datele de dividend și split."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Calendars",
                "text": "You merge daily S&P 500 and Bitcoin prices on one calendar (including weekends) and then take log differences of the S&P 500 column. What goes wrong?",
                "options": [
                    "Every Monday return becomes missing, because the Sunday price is missing",
                    "Nothing: the result is identical",
                    "Bitcoin returns become zero on weekdays",
                    "The S&P 500 gains extra trading days"
                ],
                "correctExplanation": "Differencing across a missing value gives a missing return, so all Monday returns silently disappear. For one series, compute returns on its own calendar; for a joint analysis (correlation, portfolio), first join the prices on common days, then take returns, so both cover the same interval (Friday to Monday).",
                "incorrectExplanation": "On a union calendar the Sunday gap removes every Monday equity return. For a joint analysis, join the prices on common days first and then take returns."
            },
            "ro": {
                "title": "Calendare",
                "text": "Uniți prețurile zilnice S&P 500 și Bitcoin pe un singur calendar (inclusiv weekendul) și apoi calculați log-diferențele coloanei S&P 500. Ce nu funcționează?",
                "options": [
                    "Fiecare randament de luni devine lipsă, pentru că prețul de duminică lipsește",
                    "Nimic: rezultatul este identic",
                    "Randamentele Bitcoin devin zero în zilele lucrătoare",
                    "S&P 500 câștigă zile de tranzacționare în plus"
                ],
                "correctExplanation": "Diferențierea peste o valoare lipsă dă un randament lipsă, deci toate randamentele de luni dispar pe tăcute; pentru o singură serie, calculați randamentele pe calendarul ei; pentru o analiză comună (corelație, portofoliu), întâi join pe prețuri în zilele comune, apoi randamente, ca ambele să acopere același interval (vineri - luni).",
                "incorrectExplanation": "Pe un calendar reunit, golul de duminică elimină fiecare randament de luni al acțiunilor. Pentru o analiză comună, faceți întâi join pe prețuri în zilele comune, apoi calculați randamentele."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "History of the Bucharest Stock Exchange",
                "text": "When did the Bucharest Stock Exchange first open, and when did it re-open after the communist period?",
                "options": [
                    "1 December 1882; first session again on 20 November 1995",
                    "1 December 1918; re-opened in 1990",
                    "1929 (Madgearu law); re-opened in 1997 with BET",
                    "1948; re-opened in 2010 on its own regulated market"
                ],
                "correctExplanation": "The exchange opened on 1 December 1882 under a royal decree, was closed in 1948 and held the first session of the re-established exchange on 20 November 1995 (905 shares of 6 companies).",
                "incorrectExplanation": "1929 is the year of a new law on exchanges, 1997 the launch of BET and 2010 the listing of BVB itself; the opening was 1 December 1882 and the re-opening session 20 November 1995."
            },
            "ro": {
                "title": "Istoria Bursei de Valori București",
                "text": "Când s-a deschis pentru prima dată Bursa din București și când s-a redeschis după perioada comunistă?",
                "options": [
                    "1 decembrie 1882; prima ședință din nou pe 20 noiembrie 1995",
                    "1 decembrie 1918; redeschisă în 1990",
                    "1929 (legea Madgearu); redeschisă în 1997, odată cu BET",
                    "1948; redeschisă în 2010 pe propria piață reglementată"
                ],
                "correctExplanation": "Bursa s-a deschis pe 1 decembrie 1882, în baza unui decret regal, a fost închisă în 1948, iar prima ședință a bursei reînființate a avut loc pe 20 noiembrie 1995 (905 acțiuni ale celor 6 companii).",
                "incorrectExplanation": "1929 este anul unei noi legi a burselor, 1997 lansarea BET, iar 2010 listarea BVB; deschiderea a fost pe 1 decembrie 1882, iar ședința de redeschidere pe 20 noiembrie 1995."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Recovering from a crash",
                "text": "The BET index peaked at 10,813.59 on 24 July 2007 and fell to 1,887.14 on 25 February 2009 (a drawdown of -82.5%). When did it first close back above its 2007 peak?",
                "options": [
                    "In 2009, within a few months of the trough",
                    "In 2012, about five years after the peak",
                    "In March 2021, about 13.6 years after the peak",
                    "It has never regained the 2007 peak"
                ],
                "correctExplanation": "The BET closed above 10,813.59 again only on 16 March 2021: a fall of -82.5% needs a gain of about +473% to recover, which took 13.6 years.",
                "incorrectExplanation": "After a -82.5% fall the index needs about +473% just to get back to its peak; the BET first closed above the July 2007 level on 16 March 2021."
            },
            "ro": {
                "title": "Recuperarea după un crah",
                "text": "Indicele BET a atins maximul de 10.813,59 pe 24 iulie 2007 și a coborât la 1.887,14 pe 25 februarie 2009 (un drawdown de -82,5%). Când a închis pentru prima dată din nou peste maximul din 2007?",
                "options": [
                    "În 2009, la câteva luni după minim",
                    "În 2012, la aproximativ cinci ani după maxim",
                    "În martie 2021, la aproximativ 13,6 ani după maxim",
                    "Nu a mai recuperat niciodată maximul din 2007"
                ],
                "correctExplanation": "BET a închis din nou peste 10.813,59 abia pe 16 martie 2021: o scădere de -82,5% cere o creștere de aproximativ +473% pentru recuperare, ceea ce a durat 13,6 ani.",
                "incorrectExplanation": "După o scădere de -82,5%, indicele are nevoie de aproximativ +473% doar ca să revină la maxim; BET a închis prima dată peste nivelul din iulie 2007 pe 16 martie 2021."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the AI error: annualising volatility",
                "text": "An AI assistant writes: \"The daily volatility of the S&P 500 is 1.2%. To annualise it, multiply by 252 trading days: the annual volatility is 302%.\" What is wrong?",
                "options": [
                    "Volatility grows with the square root of time: 1.2% × √252 ≈ 19.0% a year",
                    "An equity index must be annualised with 365 days, not 252",
                    "Volatility is annualised as (1 + 1.2%)^252 − 1",
                    "Nothing: variance and volatility both grow linearly with time"
                ],
                "correctExplanation": "Variance grows linearly with the horizon, so volatility grows with its square root: 1.2% × √252 ≈ 19.0%. A value of 302% is a warning sign in itself.",
                "incorrectExplanation": "Only the variance scales with the number of days; the volatility scales with √252, giving about 19.0% a year, not 302%."
            },
            "ro": {
                "title": "Găsiți eroarea AI: anualizarea volatilității",
                "text": "Un asistent AI scrie: „Volatilitatea zilnică a S&P 500 este 1,2%. Pentru anualizare, înmulțim cu 252 de zile de tranzacționare: volatilitatea anuală este 302%.” Ce este greșit?",
                "options": [
                    "Volatilitatea crește cu rădăcina pătrată a timpului: 1,2% × √252 ≈ 19,0% pe an",
                    "Un indice bursier se anualizează cu 365 de zile, nu cu 252",
                    "Volatilitatea se anualizează ca (1 + 1,2%)^252 − 1",
                    "Nimic: dispersia și volatilitatea cresc ambele liniar în timp"
                ],
                "correctExplanation": "Dispersia crește liniar cu orizontul, deci volatilitatea crește cu rădăcina lui: 1,2% × √252 ≈ 19,0%. O valoare de 302% este deja un semnal de alarmă.",
                "incorrectExplanation": "Doar dispersia se scalează cu numărul de zile; volatilitatea se scalează cu √252, adică aproximativ 19,0% pe an, nu 302%."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Spot the AI error: close vs adjusted close",
                "text": "An AI assistant writes: \"For the Sharpe ratio of SPY, use the close column: it already includes the dividends paid by the ETF.\" What is wrong?",
                "options": [
                    "The Sharpe ratio must be computed from prices, not from returns",
                    "ETFs do not pay dividends, so the two columns are identical",
                    "The close is the traded price without dividends; for stocks and ETFs the adjusted close is the one corrected for dividends and splits",
                    "The adjusted close corrects only for splits, never for dividends"
                ],
                "correctExplanation": "The close is the raw traded price; the adjusted close adds back dividends and splits. Using the close for SPY understates its mean return by roughly the dividend yield.",
                "incorrectExplanation": "The close does not include dividends: for stocks and ETFs the course uses the adjusted close, which corrects for dividends and splits; SPY does pay dividends."
            },
            "ro": {
                "title": "Găsiți eroarea AI: close vs adjusted close",
                "text": "Un asistent AI scrie: „Pentru raportul Sharpe al SPY folosiți coloana close: ea include deja dividendele plătite de ETF.” Ce este greșit?",
                "options": [
                    "Raportul Sharpe se calculează din prețuri, nu din randamente",
                    "ETF-urile nu plătesc dividende, deci cele două coloane sunt identice",
                    "Close este prețul tranzacționat fără dividende; pentru acțiuni și ETF-uri, adjusted close este cel corectat pentru dividende și splituri",
                    "Adjusted close corectează doar pentru splituri, niciodată pentru dividende"
                ],
                "correctExplanation": "Close este prețul brut de tranzacționare; adjusted close adaugă înapoi dividendele și spliturile. Folosirea lui close pentru SPY subestimează randamentul mediu cu aproximativ randamentul dividendelor.",
                "incorrectExplanation": "Close nu include dividendele: pentru acțiuni și ETF-uri cursul folosește adjusted close, corectat pentru dividende și splituri; SPY plătește dividende."
            }
        }
    ]
};

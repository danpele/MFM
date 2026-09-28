// ============================================================
// Quiz bank for chapter id 'microstructure': Market Microstructure (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['microstructure'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 1,
            "en": {
                "title": "Limit and market orders",
                "text": "Which statement about limit and market orders is correct?",
                "options": [
                    "Market orders supply liquidity; limit orders consume it",
                    "Limit orders supply liquidity; market orders consume it",
                    "Both supply liquidity",
                    "Both consume liquidity"
                ],
                "correctExplanation": "A limit order waits in the book and offers liquidity to others; a market order executes immediately against standing limit orders.",
                "incorrectExplanation": "Standing limit orders are the liquidity in the book; a market order removes them."
            },
            "ro": {
                "title": "Ordine limită și ordine la piață",
                "text": "Care afirmație despre ordinele limită și ordinele la piață este corectă?",
                "options": [
                    "Ordinele la piață oferă lichiditate; ordinele limită o consumă",
                    "Ordinele limită oferă lichiditate; ordinele la piață o consumă",
                    "Ambele oferă lichiditate",
                    "Ambele consumă lichiditate"
                ],
                "correctExplanation": "Un ordin limită așteaptă în registru și oferă lichiditate altora; un ordin la piață se execută imediat pe ordinele limită existente.",
                "incorrectExplanation": "Ordinele limită în așteptare sunt lichiditatea din registru; un ordin la piață le consumă."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Walking the book",
                "text": "Asks: 300 at 100.02 and 500 at 100.03; mid-price 100.00. A market order buys 800 shares. What is its average price?",
                "options": [
                    "100.020",
                    "100.025",
                    "100.026 (rounded)",
                    "100.030"
                ],
                "correctExplanation": "(300 x 100.02 + 500 x 100.03) / 800 = 100.02625.",
                "incorrectExplanation": "Weight each price by the quantity executed there: 300 shares at 100.02 and 500 at 100.03."
            },
            "ro": {
                "title": "Parcurgerea registrului",
                "text": "Oferte de vânzare: 300 la 100,02 și 500 la 100,03; prețul de mijloc 100,00. Un ordin la piață cumpără 800 de acțiuni. Care este prețul mediu?",
                "options": [
                    "100,020",
                    "100,025",
                    "100,026 (rotunjit)",
                    "100,030"
                ],
                "correctExplanation": "(300 x 100,02 + 500 x 100,03) / 800 = 100,02625.",
                "incorrectExplanation": "Ponderați fiecare preț cu cantitatea executată la el: 300 de acțiuni la 100,02 și 500 la 100,03."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Relative spread",
                "text": "Best bid 99.98, best ask 100.02. What is the relative quoted spread?",
                "options": [
                    "4 basis points",
                    "2 basis points",
                    "0.4%",
                    "40 basis points"
                ],
                "correctExplanation": "Spread 0.04 divided by the mid-price 100.00 is 0.04%, i.e. 4 basis points.",
                "incorrectExplanation": "The relative spread is (ask - bid) / mid = 0.04 / 100 = 0.04% = 4 bp."
            },
            "ro": {
                "title": "Spread-ul relativ",
                "text": "Cel mai bun bid 99,98, cel mai bun ask 100,02. Care este spread-ul relativ cotat?",
                "options": [
                    "4 puncte de bază",
                    "2 puncte de bază",
                    "0,4%",
                    "40 de puncte de bază"
                ],
                "correctExplanation": "Spread-ul 0,04 împărțit la prețul de mijloc 100,00 este 0,04%, adică 4 puncte de bază.",
                "incorrectExplanation": "Spread-ul relativ este (ask - bid) / mijloc = 0,04 / 100 = 0,04% = 4 pb."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Time priority",
                "text": "Two limit buy orders sit at the same price. Which one is executed first by a price-time priority matching engine?",
                "options": [
                    "The larger one",
                    "The smaller one",
                    "A random one",
                    "The one that arrived first"
                ],
                "correctExplanation": "At equal prices the queue is served in order of arrival.",
                "incorrectExplanation": "Price priority decides between different prices; at the same price, time of arrival decides."
            },
            "ro": {
                "title": "Prioritatea de timp",
                "text": "Două ordine limită de cumpărare stau la același preț. Care se execută primul într-un motor cu prioritate preț-timp?",
                "options": [
                    "Cel mai mare",
                    "Cel mai mic",
                    "Unul ales aleator",
                    "Cel care a sosit primul"
                ],
                "correctExplanation": "La prețuri egale, coada este servită în ordinea sosirii.",
                "incorrectExplanation": "Prioritatea de preț decide între prețuri diferite; la același preț decide momentul sosirii."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Components of the spread",
                "text": "Which component of the bid-ask spread exists because some traders know more than the liquidity provider?",
                "options": [
                    "Order processing cost",
                    "Adverse selection",
                    "Inventory cost",
                    "Tick size"
                ],
                "correctExplanation": "The liquidity provider loses to informed traders and recovers it through the spread: adverse selection.",
                "incorrectExplanation": "Processing and inventory costs exist even without private information; the tick size is a market rule."
            },
            "ro": {
                "title": "Componentele spread-ului",
                "text": "Ce componentă a spread-ului bid-ask există pentru că unii investitori știu mai mult decât furnizorul de lichiditate?",
                "options": [
                    "Costul procesării ordinelor",
                    "Selecția adversă",
                    "Costul de stoc",
                    "Pasul de cotare"
                ],
                "correctExplanation": "Furnizorul de lichiditate pierde în fața investitorilor informați și recuperează prin spread: selecția adversă.",
                "incorrectExplanation": "Costurile de procesare și de stoc există și fără informație privată; pasul de cotare este o regulă a pieței."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Roll model",
                "text": "In the Roll model with half-spread c, what is the first-order autocovariance of trade price changes?",
                "options": [
                    "+c^2",
                    "0",
                    "-c^2",
                    "-2c^2"
                ],
                "correctExplanation": "The bid-ask bounce gives Cov(dp_t, dp_{t-1}) = -c^2, so the spread is 2 sqrt(-Cov).",
                "incorrectExplanation": "Trade prices alternate between bid and ask, which creates a negative autocovariance equal to minus the squared half-spread."
            },
            "ro": {
                "title": "Modelul Roll",
                "text": "În modelul Roll cu jumătatea de spread c, care este autocovarianța de ordinul 1 a variațiilor prețului tranzacțiilor?",
                "options": [
                    "+c^2",
                    "0",
                    "-c^2",
                    "-2c^2"
                ],
                "correctExplanation": "Oscilația bid-ask dă Cov(dp_t, dp_{t-1}) = -c^2, deci spread-ul este 2 sqrt(-Cov).",
                "incorrectExplanation": "Prețurile tranzacțiilor alternează între bid și ask, ceea ce creează o autocovarianță negativă egală cu minus pătratul jumătății de spread."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Roll estimate",
                "text": "The sample autocovariance of daily price changes is -0.0081 (lei squared). What is the Roll spread?",
                "options": [
                    "0.18 lei",
                    "0.09 lei",
                    "0.0081 lei",
                    "0.0162 lei"
                ],
                "correctExplanation": "c = sqrt(0.0081) = 0.09 and s = 2c = 0.18 lei.",
                "incorrectExplanation": "Take the square root of minus the covariance to get the half-spread, then double it."
            },
            "ro": {
                "title": "Estimarea Roll",
                "text": "Autocovarianța de selecție a variațiilor zilnice ale prețului este -0,0081 (lei la pătrat). Care este spread-ul Roll?",
                "options": [
                    "0,18 lei",
                    "0,09 lei",
                    "0,0081 lei",
                    "0,0162 lei"
                ],
                "correctExplanation": "c = sqrt(0,0081) = 0,09 și s = 2c = 0,18 lei.",
                "incorrectExplanation": "Extrageți rădăcina pătrată din minus covarianța pentru jumătatea de spread, apoi dublați-o."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "When Roll fails",
                "text": "What does the Roll estimator give when the sample autocovariance of price changes is positive?",
                "options": [
                    "A negative spread",
                    "A zero spread",
                    "Twice the volatility",
                    "No estimate: the square root of a negative number does not exist"
                ],
                "correctExplanation": "With positive autocovariance, -Cov is negative and the estimator is undefined.",
                "incorrectExplanation": "The formula 2 sqrt(-Cov) needs a negative covariance; positive values come from trends, stale prices or split orders."
            },
            "ro": {
                "title": "Când Roll eșuează",
                "text": "Ce dă estimatorul Roll când autocovarianța de selecție a variațiilor de preț este pozitivă?",
                "options": [
                    "Un spread negativ",
                    "Un spread zero",
                    "Dublul volatilității",
                    "Nicio estimare: rădăcina pătrată a unui număr negativ nu există"
                ],
                "correctExplanation": "Cu autocovarianță pozitivă, -Cov este negativă și estimatorul nu este definit.",
                "incorrectExplanation": "Formula 2 sqrt(-Cov) cere o covarianță negativă; valorile pozitive vin din tendințe, prețuri vechi sau ordine împărțite."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "High-low estimators",
                "text": "Why does the Corwin-Schultz estimator compare the high-low range of one day with that of two days?",
                "options": [
                    "To remove weekends",
                    "Because volatility grows with the length of the interval and the spread does not",
                    "To estimate the tick size",
                    "Because closing prices are missing"
                ],
                "correctExplanation": "The two-day range contains twice the variance but the same spread, so the two can be separated.",
                "incorrectExplanation": "The method separates the part of the range that scales with time (volatility) from the part that does not (spread)."
            },
            "ro": {
                "title": "Estimatori maxim-minim",
                "text": "De ce compară estimatorul Corwin-Schultz intervalul maxim-minim al unei zile cu cel pe două zile?",
                "options": [
                    "Pentru a elimina weekendurile",
                    "Pentru că volatilitatea crește cu lungimea intervalului, iar spread-ul nu",
                    "Pentru a estima pasul de cotare",
                    "Pentru că lipsesc prețurile de închidere"
                ],
                "correctExplanation": "Intervalul pe două zile conține o dispersie dublă, dar același spread, deci cele două pot fi separate.",
                "incorrectExplanation": "Metoda separă partea intervalului care crește cu timpul (volatilitatea) de cea care nu crește (spread-ul)."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Frequency matters",
                "text": "For SPY, daily Corwin-Schultz gives about 22 bp while one price step is about 0.2 bp. What explains the gap?",
                "options": [
                    "The SPY spread is really 22 bp",
                    "The data are wrong",
                    "On daily data the high-low range is dominated by volatility",
                    "The estimator only works for crypto-assets"
                ],
                "correctExplanation": "With a daily volatility near 1%, the range is almost all price movement; 5-minute bars bring the estimate down to about 3 bp.",
                "incorrectExplanation": "The estimator mistakes volatility for spread when the interval is long relative to the spread."
            },
            "ro": {
                "title": "Frecvența contează",
                "text": "Pentru SPY, Corwin-Schultz zilnic dă circa 22 pb, iar un pas de cotare este circa 0,2 pb. Ce explică diferența?",
                "options": [
                    "Spread-ul SPY este chiar de 22 pb",
                    "Datele sunt greșite",
                    "Pe date zilnice, intervalul maxim-minim este dominat de volatilitate",
                    "Estimatorul funcționează doar pentru cripto-active"
                ],
                "correctExplanation": "Cu o volatilitate zilnică de circa 1%, intervalul este aproape numai mișcare de preț; barele de 5 minute coboară estimarea la circa 3 pb.",
                "incorrectExplanation": "Estimatorul confundă volatilitatea cu spread-ul când intervalul este lung în raport cu spread-ul."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Amihud ratio",
                "text": "What does the Amihud illiquidity ratio measure?",
                "options": [
                    "The average absolute return per unit of money traded",
                    "The quoted spread divided by price",
                    "The number of trades per day",
                    "The volatility of volume"
                ],
                "correctExplanation": "ILLIQ = average of |r| / traded value: the price move caused by one unit of trading.",
                "incorrectExplanation": "Amihud divides the absolute daily return by the traded value, giving price impact per unit of money."
            },
            "ro": {
                "title": "Raportul Amihud",
                "text": "Ce măsoară raportul de iliciditate Amihud?",
                "options": [
                    "Randamentul absolut mediu per unitate de bani tranzacționați",
                    "Spread-ul cotat împărțit la preț",
                    "Numărul de tranzacții pe zi",
                    "Volatilitatea volumului"
                ],
                "correctExplanation": "ILLIQ = media |r| / valoarea tranzacționată: mișcarea de preț produsă de o unitate de tranzacționare.",
                "incorrectExplanation": "Amihud împarte randamentul zilnic absolut la valoarea tranzacționată, obținând impactul per unitate de bani."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "BVB liquidity",
                "text": "Compared with US large caps, what does the Amihud ratio say about BVB blue chips (2024-2026)?",
                "options": [
                    "They are about as liquid",
                    "They are twice as illiquid",
                    "They are more liquid",
                    "They need thousands of times more price move per dollar traded"
                ],
                "correctExplanation": "Banca Transilvania, the most liquid BVB stock, has an Amihud ratio about fifteen thousand times that of SPY.",
                "incorrectExplanation": "The Amihud ratio separates the BVB from US large caps by several orders of magnitude, unlike daily spread proxies."
            },
            "ro": {
                "title": "Lichiditatea BVB",
                "text": "Comparativ cu marile companii americane, ce spune raportul Amihud despre acțiunile blue-chip BVB (2024-2026)?",
                "options": [
                    "Sunt aproape la fel de lichide",
                    "Sunt de două ori mai nelichide",
                    "Sunt mai lichide",
                    "Cer de mii de ori mai multă mișcare de preț per dolar tranzacționat"
                ],
                "correctExplanation": "Banca Transilvania, cea mai lichidă acțiune BVB, are un raport Amihud de circa cincisprezece mii de ori mai mare decât SPY.",
                "incorrectExplanation": "Raportul Amihud separă BVB de marile companii americane prin mai multe ordine de mărime, spre deosebire de aproximările zilnice ale spread-ului."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Intraday U-shape",
                "text": "How are volume and volatility of SPY distributed over the trading day?",
                "options": [
                    "Highest at midday",
                    "Highest at the open and the close (U-shape)",
                    "Constant through the day",
                    "Highest in the last minute only"
                ],
                "correctExplanation": "Volume and mean absolute returns peak at the open and the close and are lowest at midday.",
                "incorrectExplanation": "Both follow a U-shape: overnight news at the open, index and ETF trading at the close."
            },
            "ro": {
                "title": "Forma de U intrazilnică",
                "text": "Cum sunt distribuite volumul și volatilitatea SPY în cursul zilei?",
                "options": [
                    "Maxime la prânz",
                    "Maxime la deschidere și la închidere (forma de U)",
                    "Constante în cursul zilei",
                    "Maxime doar în ultimul minut"
                ],
                "correctExplanation": "Volumul și randamentele absolute medii ating maximul la deschidere și la închidere și minimul la prânz.",
                "incorrectExplanation": "Ambele urmează o formă de U: știrile din timpul nopții la deschidere, tranzacționarea fondurilor pe indici și a ETF-urilor la închidere."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Bitcoin clock",
                "text": "When are Bitcoin 5-minute returns largest on average?",
                "options": [
                    "At weekends",
                    "During Asian night hours",
                    "During US trading hours on weekdays",
                    "At midnight UTC"
                ],
                "correctExplanation": "The weekday peak falls at 14:00 UTC, when US markets open; weekends are about 1.7 times calmer.",
                "incorrectExplanation": "Although Bitcoin trades 24/7, its activity follows the clock of US investors and news."
            },
            "ro": {
                "title": "Ceasul Bitcoin",
                "text": "Când sunt cele mai mari, în medie, randamentele Bitcoin pe 5 minute?",
                "options": [
                    "În weekend",
                    "În orele de noapte din Asia",
                    "În orele de tranzacționare americane din zilele lucrătoare",
                    "La miezul nopții UTC"
                ],
                "correctExplanation": "Maximul din zilele lucrătoare cade la 14:00 UTC, la deschiderea piețelor americane; weekendurile sunt de circa 1,7 ori mai calme.",
                "incorrectExplanation": "Deși Bitcoin se tranzacționează 24/7, activitatea sa urmează ceasul investitorilor și al știrilor americane."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Liquidity and the VIX",
                "text": "How does SPY intraday illiquidity relate to the VIX?",
                "options": [
                    "It rises when the VIX rises, almost proportionally",
                    "It falls when the VIX rises",
                    "It is unrelated to the VIX",
                    "It depends only on the day of the week"
                ],
                "correctExplanation": "The elasticity of log illiquidity on log VIX is about 0.95: liquidity disappears when volatility rises.",
                "incorrectExplanation": "Market makers widen quotes and reduce depth when risk rises, so illiquidity and the VIX move together."
            },
            "ro": {
                "title": "Lichiditatea și VIX",
                "text": "Cum este legată iliciditatea intrazilnică a SPY de VIX?",
                "options": [
                    "Crește când crește VIX, aproape proporțional",
                    "Scade când crește VIX",
                    "Nu are legătură cu VIX",
                    "Depinde doar de ziua săptămânii"
                ],
                "correctExplanation": "Elasticitatea logaritmului iliciditații în raport cu logaritmul VIX este circa 0,95: lichiditatea dispare când volatilitatea crește.",
                "incorrectExplanation": "Formatorii de piață lărgesc cotațiile și reduc adâncimea când riscul crește, deci iliciditatea și VIX evoluează împreună."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Glosten-Milgrom spread",
                "text": "In Glosten-Milgrom with V_L = 90, V_H = 110, prior 1/2 and share of informed traders mu, what is the spread?",
                "options": [
                    "20",
                    "10 mu",
                    "20 (1 - mu)",
                    "20 mu"
                ],
                "correctExplanation": "At a prior of 1/2 the spread equals mu (V_H - V_L) = 20 mu.",
                "incorrectExplanation": "The spread is proportional to the share of informed traders and to the value difference V_H - V_L."
            },
            "ro": {
                "title": "Spread-ul Glosten-Milgrom",
                "text": "În Glosten-Milgrom cu V_L = 90, V_H = 110, probabilitatea inițială 1/2 și ponderea investitorilor informați mu, care este spread-ul?",
                "options": [
                    "20",
                    "10 mu",
                    "20 (1 - mu)",
                    "20 mu"
                ],
                "correctExplanation": "La o probabilitate inițială de 1/2, spread-ul este mu (V_H - V_L) = 20 mu.",
                "incorrectExplanation": "Spread-ul este proporțional cu ponderea investitorilor informați și cu diferența de valoare V_H - V_L."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Kyle's lambda",
                "text": "In the Kyle model, what is the price impact coefficient lambda?",
                "options": [
                    "sigma_u / sigma_v",
                    "sigma_v sigma_u / 2",
                    "sigma_v / (2 sigma_u)",
                    "2 sigma_u / sigma_v"
                ],
                "correctExplanation": "lambda = sigma_v / (2 sigma_u): more noise trading makes the market deeper.",
                "incorrectExplanation": "sigma_u / sigma_v is the insider's intensity beta and sigma_v sigma_u / 2 is the insider's expected profit."
            },
            "ro": {
                "title": "Lambda lui Kyle",
                "text": "În modelul Kyle, care este coeficientul de impact lambda?",
                "options": [
                    "sigma_u / sigma_v",
                    "sigma_v sigma_u / 2",
                    "sigma_v / (2 sigma_u)",
                    "2 sigma_u / sigma_v"
                ],
                "correctExplanation": "lambda = sigma_v / (2 sigma_u): mai mult zgomot face piața mai adâncă.",
                "incorrectExplanation": "sigma_u / sigma_v este intensitatea beta a investitorului din interior, iar sigma_v sigma_u / 2 este profitul său așteptat."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Information in the Kyle price",
                "text": "In the one-period Kyle equilibrium, how much of the insider's information is revealed by the price?",
                "options": [
                    "Exactly half: Var(v | p) = sigma_v^2 / 2",
                    "All of it",
                    "None of it",
                    "A quarter"
                ],
                "correctExplanation": "The posterior variance is half of the prior variance: the price reveals half of the private information.",
                "incorrectExplanation": "The insider trades so that the market maker learns exactly half of the variance of the value."
            },
            "ro": {
                "title": "Informația din prețul Kyle",
                "text": "În echilibrul Kyle cu o singură perioadă, cât din informația investitorului din interior este dezvăluită de preț?",
                "options": [
                    "Exact jumătate: Var(v | p) = sigma_v^2 / 2",
                    "Toată",
                    "Nimic",
                    "Un sfert"
                ],
                "correctExplanation": "Dispersia a posteriori este jumătate din dispersia a priori: prețul dezvăluie jumătate din informația privată.",
                "incorrectExplanation": "Investitorul din interior tranzacționează astfel încât formatorul de piață află exact jumătate din dispersia valorii."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Square-root law",
                "text": "According to the square-root law, if a metaorder is four times larger, how does its price impact change?",
                "options": [
                    "It is four times larger",
                    "It is sixteen times larger",
                    "It does not change",
                    "It is about twice as large"
                ],
                "correctExplanation": "Impact grows with the square root of size: sqrt(4) = 2.",
                "incorrectExplanation": "The law is concave: Delta P is proportional to sqrt(Q / V), not to Q."
            },
            "ro": {
                "title": "Legea rădăcinii pătrate",
                "text": "Conform legii rădăcinii pătrate, dacă un metaordin este de patru ori mai mare, cum se schimbă impactul său?",
                "options": [
                    "Este de patru ori mai mare",
                    "Este de șaisprezece ori mai mare",
                    "Nu se schimbă",
                    "Este de circa două ori mai mare"
                ],
                "correctExplanation": "Impactul crește cu rădăcina pătrată a mărimii: sqrt(4) = 2.",
                "incorrectExplanation": "Legea este concavă: Delta P este proporțional cu sqrt(Q / V), nu cu Q."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Almgren-Chriss",
                "text": "In Almgren-Chriss, what does a risk-neutral trader (lambda = 0) do?",
                "options": [
                    "Sells everything at the start",
                    "Sells the same amount in each period",
                    "Sells everything at the end",
                    "Waits for a better price"
                ],
                "correctExplanation": "With lambda = 0, kappa = 0 and holdings fall linearly: the time-weighted schedule.",
                "incorrectExplanation": "Only price risk pushes trading forward; without risk aversion, spreading the order evenly minimises the temporary impact."
            },
            "ro": {
                "title": "Almgren-Chriss",
                "text": "În Almgren-Chriss, ce face un investitor neutru la risc (lambda = 0)?",
                "options": [
                    "Vinde totul la început",
                    "Vinde aceeași cantitate în fiecare perioadă",
                    "Vinde totul la sfârșit",
                    "Așteaptă un preț mai bun"
                ],
                "correctExplanation": "Cu lambda = 0, kappa = 0 și deținerea scade liniar: programul ponderat în timp.",
                "incorrectExplanation": "Doar riscul de preț împinge tranzacționarea spre început; fără aversiune la risc, împărțirea uniformă a ordinului minimizează impactul temporar."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Execution trade-off",
                "text": "Why does a more risk-averse trader front-load a liquidation?",
                "options": [
                    "To lower the expected impact cost",
                    "Because permanent impact disappears",
                    "To reduce the variance of the cost from future price moves",
                    "Because spreads are narrower early"
                ],
                "correctExplanation": "Selling early cuts exposure to price risk, at the cost of higher temporary impact.",
                "incorrectExplanation": "Front-loading raises the expected impact cost; it is chosen to reduce the variance of the implementation cost."
            },
            "ro": {
                "title": "Compromisul execuției",
                "text": "De ce un investitor cu aversiune mai mare la risc vinde mai mult la începutul lichidării?",
                "options": [
                    "Pentru a reduce costul așteptat al impactului",
                    "Pentru că impactul permanent dispare",
                    "Pentru a reduce dispersia costului provocată de mișcările viitoare ale prețului",
                    "Pentru că spread-urile sunt mai înguste la început"
                ],
                "correctExplanation": "Vânzarea timpurie reduce expunerea la riscul de preț, cu prețul unui impact temporar mai mare.",
                "incorrectExplanation": "Vânzarea timpurie crește costul așteptat al impactului; este aleasă pentru a reduce dispersia costului de implementare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Flash Crash",
                "text": "What started the selling pressure of 6 May 2010, according to the CFTC-SEC report?",
                "options": [
                    "An algorithm selling 75,000 E-Mini contracts at 9% of volume, regardless of price or time",
                    "A cyber attack on the NYSE",
                    "A central bank announcement",
                    "A crash of the Bitcoin market"
                ],
                "correctExplanation": "A mutual fund complex used a sell algorithm that targeted 9% of the previous minute's volume without regard to price or time.",
                "incorrectExplanation": "The report traces the start of the decline to a large, price-insensitive sell program in E-Mini futures."
            },
            "ro": {
                "title": "Prăbușirea fulger",
                "text": "Ce a declanșat presiunea vânzărilor din 6 mai 2010, conform raportului CFTC-SEC?",
                "options": [
                    "Un algoritm care vindea 75.000 de contracte E-Mini la 9% din volum, fără a ține cont de preț sau de timp",
                    "Un atac cibernetic asupra NYSE",
                    "Un anunț al unei bănci centrale",
                    "O prăbușire a pieței Bitcoin"
                ],
                "correctExplanation": "Un grup de fonduri mutuale a folosit un algoritm de vânzare care viza 9% din volumul minutului anterior, fără a ține cont de preț sau de timp.",
                "incorrectExplanation": "Raportul leagă începutul scăderii de un program mare de vânzare, insensibil la preț, pe contractele futures E-Mini."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Frequent batch auctions",
                "text": "What do Budish, Cramton and Shim propose against the high-frequency speed race?",
                "options": [
                    "Banning limit orders",
                    "A minimum holding period of one day",
                    "A tax on every trade",
                    "Frequent batch auctions at discrete intervals, e.g. every second"
                ],
                "correctExplanation": "Uniform-price batch auctions every second turn competition on speed into competition on price.",
                "incorrectExplanation": "Their proposal changes the market design from a continuous book to frequent discrete auctions."
            },
            "ro": {
                "title": "Licitații periodice frecvente",
                "text": "Ce propun Budish, Cramton și Shim împotriva cursei vitezei în tranzacționarea de înaltă frecvență?",
                "options": [
                    "Interzicerea ordinelor limită",
                    "O perioadă minimă de deținere de o zi",
                    "O taxă pe fiecare tranzacție",
                    "Licitații periodice frecvente la intervale discrete, de exemplu la fiecare secundă"
                ],
                "correctExplanation": "Licitațiile la preț unic la fiecare secundă transformă concurența pe viteză în concurență pe preț.",
                "incorrectExplanation": "Propunerea lor schimbă designul pieței de la un registru continuu la licitații discrete frecvente."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Illiquidity shocks",
                "text": "In the seminar, how do monthly market returns react to an unexpected rise in market illiquidity?",
                "options": [
                    "They rise, on all three markets",
                    "They fall, on the BVB, in the US and in crypto",
                    "They fall only in the US",
                    "They do not react"
                ],
                "correctExplanation": "The coefficient of the illiquidity shock is negative with t-statistics near -4 on all three markets, as Amihud (2002) predicts.",
                "incorrectExplanation": "An unexpected rise in illiquidity raises required returns, so current prices fall on each of the three markets."
            },
            "ro": {
                "title": "Șocurile de iliciditate",
                "text": "La seminar, cum reacționează randamentele lunare ale pieței la o creștere neașteptată a iliciditații?",
                "options": [
                    "Cresc, pe toate cele trei piețe",
                    "Scad, pe BVB, în SUA și pe piața cripto",
                    "Scad doar în SUA",
                    "Nu reacționează"
                ],
                "correctExplanation": "Coeficientul șocului de iliciditate este negativ, cu statistici t apropiate de -4 pe toate cele trei piețe, cum prezice Amihud (2002).",
                "incorrectExplanation": "O creștere neașteptată a iliciditații crește randamentele cerute, deci prețurile curente scad pe fiecare dintre cele trei piețe."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Spot the AI error: the Roll estimator",
                "text": "An AI assistant writes: \"The Roll spread is s = 2 sqrt(-Cov(dp_t, dp_{t-1})). For this stock the autocovariance of price changes is positive, so use s = 2 sqrt(|Cov|) instead.\" What is wrong?",
                "options": [
                    "The factor should be 1, not 2",
                    "The Roll estimator uses the variance of price changes, not their autocovariance",
                    "The autocovariance should be computed from prices, not price changes",
                    "A positive autocovariance contradicts the Roll model, so the estimator is undefined; report it as missing or use another estimator, such as a high-low one"
                ],
                "correctExplanation": "The Roll model implies Cov(dp_t, dp_{t-1}) = -c^2 < 0. A positive value means bid-ask bounce does not dominate the sample (trends, stale prices), and taking the absolute value produces a spread that has no basis in the model (Roll, 1984; Hasbrouck, 2007).",
                "incorrectExplanation": "The formula s = 2 sqrt(-Cov) is right; the error is forcing a positive autocovariance into it with an absolute value."
            },
            "ro": {
                "title": "Găsiți eroarea AI: estimatorul Roll",
                "text": "Un asistent AI scrie: „Spread-ul Roll este s = 2 sqrt(-Cov(dp_t, dp_{t-1})). Pentru această acțiune autocovarianța variațiilor de preț este pozitivă, deci folosiți în schimb s = 2 sqrt(|Cov|).” Ce este greșit?",
                "options": [
                    "Factorul ar trebui să fie 1, nu 2",
                    "Estimatorul Roll folosește varianța variațiilor de preț, nu autocovarianța lor",
                    "Autocovarianța ar trebui calculată din prețuri, nu din variațiile lor",
                    "O autocovarianță pozitivă contrazice modelul Roll, deci estimatorul nu este definit; raportați-l ca lipsă sau folosiți alt estimator, de exemplu unul maxim-minim"
                ],
                "correctExplanation": "Modelul Roll implică Cov(dp_t, dp_{t-1}) = -c^2 < 0. O valoare pozitivă arată că oscilația bid-ask nu domină eșantionul (tendințe, prețuri învechite), iar valoarea absolută produce un spread fără nicio bază în model (Roll, 1984; Hasbrouck, 2007).",
                "incorrectExplanation": "Formula s = 2 sqrt(-Cov) este corectă; greșeala este forțarea unei autocovarianțe pozitive în formulă prin valoarea absolută."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the AI error: the Amihud ratio",
                "text": "An AI assistant writes: \"The Amihud illiquidity of a stock is the average over days of |r_d| divided by the number of shares traded on day d.\" What is wrong?",
                "options": [
                    "The numerator should be the squared return, not the absolute return",
                    "The denominator must be the traded value (price times shares, in money), not the number of shares",
                    "The ratio should be a median, not an average",
                    "Amihud uses intraday returns, not daily returns"
                ],
                "correctExplanation": "Amihud (2002) defines ILLIQ as the average of |r_d| / DVOL_d, with DVOL_d the traded value in currency. With the number of shares, the ratio depends on the price level, jumps at a stock split and cannot be compared across stocks.",
                "incorrectExplanation": "The absolute daily return and the average over days are right; the denominator must be measured in money, not in shares."
            },
            "ro": {
                "title": "Găsiți eroarea AI: raportul Amihud",
                "text": "Un asistent AI scrie: „Iliciditatea Amihud a unei acțiuni este media pe zile a lui |r_d| împărțit la numărul de acțiuni tranzacționate în ziua d.” Ce este greșit?",
                "options": [
                    "Numărătorul ar trebui să fie pătratul randamentului, nu randamentul absolut",
                    "Numitorul trebuie să fie valoarea tranzacționată (preț ori număr de acțiuni, în bani), nu numărul de acțiuni",
                    "Raportul ar trebui să fie o mediană, nu o medie",
                    "Amihud folosește randamente intraday, nu randamente zilnice"
                ],
                "correctExplanation": "Amihud (2002) definește ILLIQ ca media lui |r_d| / DVOL_d, cu DVOL_d valoarea tranzacționată în monedă. Cu numărul de acțiuni, raportul depinde de nivelul prețului, face un salt la o divizare a acțiunilor și nu poate fi comparat între acțiuni.",
                "incorrectExplanation": "Randamentul zilnic absolut și media pe zile sunt corecte; numitorul trebuie măsurat în bani, nu în număr de acțiuni."
            }
        }
    ]
};

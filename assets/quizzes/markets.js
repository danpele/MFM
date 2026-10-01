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
                "title": "Precision of a mean return",
                "text": "S&P 500 with dividends, 2015-2026: annualised volatility 17.5%, 11.7 years of daily data (about 2,944 days), iid returns. What is the approximate standard error of the annualised mean return?",
                "options": [
                    "0.32 pp: daily data make the mean very precise",
                    "1.5 pp: sigma divided by the number of years",
                    "5.1 pp: sigma divided by the square root of the number of years",
                    "1.1 pp: sigma divided by sqrt(252)"
                ],
                "correctExplanation": "SE = q sigma_d / sqrt(T) = sigma_a / sqrt(Y) = 17.5% / sqrt(11.7) = 5.1 pp (Merton, 1980): only the span of the sample matters, not the sampling frequency.",
                "incorrectExplanation": "The standard error of an annualised mean is sigma_a / sqrt(Y) = 5.1 pp; sampling more often within the same 11.7 years does not help."
            },
            "ro": {
                "title": "Precizia unui randament mediu",
                "text": "S&P 500 cu dividende, 2015-2026: volatilitate anualizată 17,5%, 11,7 ani de date zilnice (circa 2.944 de zile), randamente iid. Care este aproximativ eroarea standard a randamentului mediu anualizat?",
                "options": [
                    "0,32 pp: datele zilnice fac media foarte precisă",
                    "1,5 pp: sigma împărțit la numărul de ani",
                    "5,1 pp: sigma împărțit la rădăcina pătrată a numărului de ani",
                    "1,1 pp: sigma împărțit la sqrt(252)"
                ],
                "correctExplanation": "SE = q sigma_d / sqrt(T) = sigma_a / sqrt(Y) = 17,5% / sqrt(11,7) = 5,1 pp (Merton, 1980): contează doar lungimea perioadei, nu frecvența eșantionării.",
                "incorrectExplanation": "Eroarea standard a unei medii anualizate este sigma_a / sqrt(Y) = 5,1 pp; observațiile mai dese în aceiași 11,7 ani nu ajută."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Annualising with the observed frequency",
                "text": "Bitcoin trades every day: 4,277 daily returns in 11.71 years (q = 365.25). Its daily log-return standard deviation is 3.49%. Which annualised volatility is right, and why?",
                "options": [
                    "55.4%: always use sqrt(252), the number of trading days of a year",
                    "66.7%: multiply by sqrt(q) with q = n/Y = 365.25, the observed returns per year",
                    "1,274%: multiply by 365.25",
                    "3.49%: volatility is not annualised"
                ],
                "correctExplanation": "Annualise with the observed number of return intervals per year: 3.49% x sqrt(365.25) = 66.7%. Using 252 understates Bitcoin's annual volatility by 11 pp; for gold (q = 260.5) the difference is only 0.3 pp.",
                "incorrectExplanation": "With iid daily returns the annual variance is q times the daily variance, with q the observed returns per year: 365.25 for Bitcoin, so 3.49% x sqrt(365.25) = 66.7%."
            },
            "ro": {
                "title": "Anualizarea cu frecvența observată",
                "text": "Bitcoin se tranzacționează în fiecare zi: 4.277 de randamente zilnice în 11,71 ani (q = 365,25). Abaterea standard a log-randamentelor zilnice este 3,49%. Care volatilitate anualizată este corectă și de ce?",
                "options": [
                    "55,4%: folosim întotdeauna sqrt(252), numărul zilelor de tranzacționare dintr-un an",
                    "66,7%: înmulțim cu sqrt(q), cu q = n/Y = 365,25, randamentele observate pe an",
                    "1.274%: înmulțim cu 365,25",
                    "3,49%: volatilitatea nu se anualizează"
                ],
                "correctExplanation": "Anualizăm cu numărul observat de intervale de randament pe an: 3,49% x sqrt(365,25) = 66,7%. Cu 252, volatilitatea anuală a Bitcoin ar fi subestimată cu 11 pp; la aur (q = 260,5) diferența este doar 0,3 pp.",
                "incorrectExplanation": "Cu randamente zilnice iid, varianța anuală este de q ori varianța zilnică, cu q numărul observat de randamente pe an: 365,25 la Bitcoin, deci 3,49% x sqrt(365,25) = 66,7%."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Standard error of a Sharpe ratio",
                "text": "An annualised Sharpe ratio of 0.82 is estimated from 11.7 years of daily returns, assumed iid Normal. What is its approximate standard error?",
                "options": [
                    "0.018: one over the square root of the number of days",
                    "0.24: the Sharpe ratio divided by sqrt(Y)",
                    "0.34: sqrt((1 + SR^2/2)/Y) with the annual SR",
                    "0.29: about 1/sqrt(Y) when the SR is estimated from daily data"
                ],
                "correctExplanation": "By the delta method Var(SR_a) = q(1 + SR_d^2/2)/T = (1 + SR_a^2/(2q))/Y, about 1/Y: SE = 0.29 (Lo, 2002, applied at the daily frequency).",
                "incorrectExplanation": "With daily data the annualised SR has variance q(1 + SR_d^2/2)/T, about 1/Y, so the SE is about 0.29; the formula with the annual SR treats the sample as 11.7 annual observations."
            },
            "ro": {
                "title": "Eroarea standard a unui raport Sharpe",
                "text": "Un raport Sharpe anualizat de 0,82 este estimat din 11,7 ani de randamente zilnice, presupuse iid cu distribuția Normală. Care este aproximativ eroarea lui standard?",
                "options": [
                    "0,018: unu supra rădăcina numărului de zile",
                    "0,24: raportul Sharpe împărțit la sqrt(Y)",
                    "0,34: sqrt((1 + SR^2/2)/Y) cu SR anual",
                    "0,29: circa 1/sqrt(Y) cînd SR este estimat din date zilnice"
                ],
                "correctExplanation": "Prin metoda delta Var(SR_a) = q(1 + SR_d^2/2)/T = (1 + SR_a^2/(2q))/Y, circa 1/Y: SE = 0,29 (Lo, 2002, aplicat la frecvența zilnică).",
                "incorrectExplanation": "Cu date zilnice SR anualizat are varianța q(1 + SR_d^2/2)/T, circa 1/Y, deci SE este circa 0,29; formula cu SR anual tratează eșantionul ca 11,7 observații anuale."
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
                    "Cea mai bună ofertă de vînzare minus cea mai bună ofertă de cumpărare: prețul execuției imediate"
                ],
                "correctExplanation": "Spread-ul este diferența dintre cel mai mic preț la care cineva vinde și cel mai mare preț la care cineva cumpără: costul imediateței.",
                "incorrectExplanation": "Spread-ul bid-ask este cea mai bună ofertă de vînzare minus cea mai bună ofertă de cumpărare, costul tranzacționării imediate."
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
            "correct": 3,
            "en": {
                "title": "Comparing maximum drawdowns",
                "text": "S&P 500: maximum drawdown -56.8% since 2000 and -33.9% since 17 Sep 2014. Bitcoin: -83.4% since 17 Sep 2014. Which comparison of the two assets is valid?",
                "options": [
                    "-56.8% vs -83.4%: each asset with its full history",
                    "-56.8% vs -33.9%: the S&P 500 with itself",
                    "No comparison is possible: drawdowns are not statistics",
                    "-33.9% vs -83.4%: both measured from 17 Sep 2014"
                ],
                "correctExplanation": "The magnitude of the maximum drawdown cannot decrease when the sample is extended, so MDDs are comparable only over the same horizon: since 17 Sep 2014, -33.9% for the S&P 500 against -83.4% for Bitcoin.",
                "incorrectExplanation": "A longer sample can only keep or deepen the maximum drawdown; comparing the S&P 500 since 2000 with Bitcoin since 2014 mixes horizons. The valid comparison uses the common horizon from 17 Sep 2014."
            },
            "ro": {
                "title": "Compararea drawdown-urilor maxime",
                "text": "S&P 500: drawdown maxim -56,8% din 2000 și -33,9% din 17 sep. 2014. Bitcoin: -83,4% din 17 sep. 2014. Care comparație între cele două active este validă?",
                "options": [
                    "-56,8% față de -83,4%: fiecare activ cu tot istoricul lui",
                    "-56,8% față de -33,9%: S&P 500 cu el însuși",
                    "Nicio comparație nu este posibilă: drawdown-urile nu sînt statistici",
                    "-33,9% față de -83,4%: ambele măsurate din 17 sep. 2014"
                ],
                "correctExplanation": "Mărimea drawdown-ului maxim nu poate scădea cînd eșantionul se extinde, deci MDD-urile se compară doar pe același orizont: din 17 sep. 2014, -33,9% la S&P 500 față de -83,4% la Bitcoin.",
                "incorrectExplanation": "Un eșantion mai lung poate doar să păstreze sau să adîncească drawdown-ul maxim; S&P 500 din 2000 comparat cu Bitcoin din 2014 amestecă orizonturile. Comparația validă folosește orizontul comun, din 17 sep. 2014."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "VIX and realised volatility",
                "text": "In 2000-2026 the VIX exceeded the S&P 500 volatility realised over the following 21 trading days on 83% of days. What is the main reason?",
                "options": [
                    "The VIX is annualised with 365 days, realised volatility with 252",
                    "The VIX data contain errors in stress periods",
                    "The VIX is a risk-neutral expectation that includes a variance risk premium",
                    "Realised volatility ignores weekends"
                ],
                "correctExplanation": "VIX^2 approximates the risk-neutral expectation of future variance; investors pay a premium for insurance against volatility, so implied variance exceeds realised variance on average (Carr and Wu, 2009).",
                "incorrectExplanation": "The gap is the variance risk premium: the VIX is computed from option prices under the risk-neutral measure, so it is a biased forecast of realised volatility."
            },
            "ro": {
                "title": "VIX și volatilitatea realizată",
                "text": "În 2000-2026, VIX a depășit volatilitatea S&P 500 realizată în următoarele 21 de zile de tranzacționare în 83% din zile. Care este motivul principal?",
                "options": [
                    "VIX este anualizat cu 365 de zile, volatilitatea realizată cu 252",
                    "Datele VIX conțin erori în perioadele de stres",
                    "VIX este o așteptare neutră la risc care include o primă de risc de varianță",
                    "Volatilitatea realizată ignoră weekendurile"
                ],
                "correctExplanation": "VIX^2 aproximează așteptarea neutră la risc a varianței viitoare; investitorii plătesc o primă pentru asigurarea împotriva volatilității, deci varianța implicită o depășește în medie pe cea realizată (Carr și Wu, 2009).",
                "incorrectExplanation": "Diferența este prima de risc de varianță: VIX se calculează din prețurile opțiunilor sub măsura neutră la risc, deci este o prognoză deplasată a volatilității realizate."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Reading a log-scale chart",
                "text": "A chart shows the growth of 1 USD invested on 2 Jan 2015 in six assets on a logarithmic vertical axis. What does an equal vertical distance mean anywhere on this axis?",
                "options": [
                    "The same percentage change",
                    "The same change in USD",
                    "The same volatility",
                    "The same Sharpe ratio"
                ],
                "correctExplanation": "On a log scale the vertical distance is ln(P2) - ln(P1) = ln(P2/P1): equal distances are equal growth multiples, so a move from 1 to 2 looks as large as one from 100 to 200. This is why assets that grew 0.9 times and 257 times fit on one readable chart.",
                "incorrectExplanation": "The log axis plots ln(P): an equal vertical distance is an equal ratio P2/P1, i.e. the same percentage change, not the same amount in USD."
            },
            "ro": {
                "title": "Citirea unui grafic pe scară logaritmică",
                "text": "Un grafic arată creșterea a 1 USD investit pe 2 ian. 2015 în șase active, cu axa verticală logaritmică. Ce înseamnă o distanță verticală egală oriunde pe această axă?",
                "options": [
                    "Aceeași variație procentuală",
                    "Aceeași variație în USD",
                    "Aceeași volatilitate",
                    "Același raport Sharpe"
                ],
                "correctExplanation": "Pe scară logaritmică distanța verticală este ln(P2) - ln(P1) = ln(P2/P1): distanțe egale înseamnă multipli de creștere egali, deci trecerea de la 1 la 2 arată la fel de mare ca trecerea de la 100 la 200. De aceea active care au crescut de 0,9 ori și de 257 de ori încap pe același grafic lizibil.",
                "incorrectExplanation": "Axa logaritmică reprezintă ln(P): o distanță verticală egală este un raport P2/P1 egal, adică aceeași variație procentuală, nu aceeași sumă în USD."
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
                    "Obligațiunile pe termen lung au oferit un hedge mai slab pentru pierderile la acțiuni după șocul inflaționist din 2022",
                    "Obligațiunile au devenit mai riscante decît Bitcoin",
                    "Corelațiile sînt constante în timp",
                    "Acțiunile și obligațiunile se mișcă acum mereu în sens opus"
                ],
                "correctExplanation": "O corelație negativă acțiuni-obligațiuni face din obligațiuni un hedge; cînd a devenit pozitivă, obligațiunile și acțiunile au scăzut împreună, ca în 2022.",
                "incorrectExplanation": "Trecerea de la -0,43 la +0,08 înseamnă că obligațiunile și-au pierdut mult din valoarea de hedge după 2022."
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
                    "Bitcoin a devenit un hedge perfect pentru acțiuni",
                    "Volatilitatea Bitcoin a scăzut la nivelul acțiunilor",
                    "Bitcoin oferă mai puțină diversificare față de riscul acțiunilor decît înainte",
                    "Corelația dovedește că Bitcoin este o acțiune"
                ],
                "correctExplanation": "O corelație mai mare înseamnă că Bitcoin tinde să scadă cînd scad acțiunile, deci beneficiul de diversificare s-a redus.",
                "incorrectExplanation": "Creșterea corelației reduce beneficiul de diversificare; nu face din Bitcoin un hedge sau o acțiune."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Rolling or whole-period correlation?",
                "text": "Bitcoin vs S&P 500, daily log returns on common days, 2022-2026: whole-period correlation 0.42; mean of the 252-day rolling correlations 0.38 (the first windows start in 2021). Which number answers \"what was the correlation in 2022-2026\"?",
                "options": [
                    "0.38: rolling correlations are always more accurate",
                    "Their average, 0.40",
                    "0.42: the mean of rolling correlations averages one-year windows, partly from 2021, a different estimand",
                    "Neither: correlations cannot be estimated over several years"
                ],
                "correctExplanation": "The whole-period correlation on common days estimates the 2022-2026 correlation; the mean of rolling correlations averages one-year windows, some starting in 2021, which is a different quantity.",
                "incorrectExplanation": "The question asks for one correlation over 2022-2026: the whole-period estimate on common days, 0.42. The mean of 252-day rolling correlations is the average of one-year correlations, partly measured in 2021."
            },
            "ro": {
                "title": "Corelație mobilă sau pe toată perioada?",
                "text": "Bitcoin vs S&P 500, log-randamente zilnice pe zilele comune, 2022-2026: corelația pe toată perioada 0,42; media corelațiilor mobile pe 252 de zile 0,38 (primele ferestre încep în 2021). Ce cifră răspunde la întrebarea „care a fost corelația în 2022-2026”?",
                "options": [
                    "0,38: corelațiile mobile sînt întotdeauna mai precise",
                    "Media lor, 0,40",
                    "0,42: media corelațiilor mobile face media unor ferestre de un an, parțial din 2021, adică altă mărime estimată",
                    "Niciuna: corelațiile nu se pot estima pe mai mulți ani"
                ],
                "correctExplanation": "Corelația pe toată perioada, pe zilele comune, estimează corelația din 2022-2026; media corelațiilor mobile face media unor ferestre de un an, unele începute în 2021, adică altă mărime.",
                "incorrectExplanation": "Întrebarea cere o singură corelație pentru 2022-2026: estimația pe toată perioada, pe zilele comune, 0,42. Media corelațiilor mobile pe 252 de zile este media unor corelații anuale, măsurate parțial în 2021."
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
                    "The cap-weighted fund beat the equal-weighted one: the most heavily weighted stocks did better than the average stock"
                ],
                "correctExplanation": "The cap-weighted fund gives more weight to the largest companies; its outperformance means that the heavily weighted stocks drove index returns. Whether concentration rose must be checked from the constituent weights (e.g. the effective number of stocks).",
                "incorrectExplanation": "A rising SPY/RSP ratio means that the heavily weighted stocks beat the typical stock; the constituent weights show whether concentration also rose."
            },
            "ro": {
                "title": "Concentrare",
                "text": "Raportul SPY / RSP (ETF pe S&P 500 ponderat după capitalizare față de cel cu ponderi egale) a crescut cu circa 31% din ianuarie 2023 pînă în septembrie 2026. Ce indică acest lucru?",
                "options": [
                    "Firmele mici au avut randamente mai bune decît cele mari",
                    "S&P 500 a scăzut",
                    "ETF-urile nu mai replică indicele",
                    "Fondul ponderat după capitalizare l-a depășit pe cel cu ponderi egale: acțiunile cu ponderile cele mai mari au avut randamente mai bune decît acțiunea medie"
                ],
                "correctExplanation": "Fondul ponderat după capitalizare dă o pondere mai mare celor mai mari companii; performanța sa superioară înseamnă că acțiunile cu ponderi mari au condus randamentul indicelui. Dacă a crescut concentrarea se verifică din ponderile componentelor (de exemplu numărul efectiv de acțiuni).",
                "incorrectExplanation": "Un raport SPY/RSP în creștere înseamnă că acțiunile cu ponderi mari au depășit acțiunea tipică; ponderile componentelor arată dacă a crescut și concentrarea."
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
                    "Participanții autorizați schimbă coșuri de active suport pe unități ETF (și invers) cînd prețurile se îndepărtează",
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
                    "Acțiunile deținute de ETF-uri sînt mai puțin volatile",
                    "Deținerile ETF nu au niciun efect asupra acțiunilor",
                    "Acțiunile cu deținere ETF mai mare sînt mai volatile",
                    "ETF-urile elimină spread-ul bid-ask"
                ],
                "correctExplanation": "Rezultatul lor este că o deținere ETF mai mare este asociată cu o volatilitate mai mare a acțiunilor suport, prin tranzacții de arbitraj care propagă șocurile de lichiditate.",
                "incorrectExplanation": "Articolul arată că o deținere ETF mai mare crește volatilitatea acțiunilor suport."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "An interval for a change in correlation",
                "text": "The S&P 500 - TLT correlation moved from -0.47 (2010-2020) to +0.11 (2022-2026). The iid 95% interval for the change is [0.52; 0.65] (Fisher, iid pairs from a bivariate Normal distribution). What can you conclude?",
                "options": [
                    "The 2022 inflation shock caused the change",
                    "The change is far larger than iid sampling error, but the interval does not identify its cause and assumes iid returns",
                    "The change is not significant because the 2022-2026 correlation is close to zero",
                    "The interval proves that the correlation will stay positive"
                ],
                "correctExplanation": "The interval excludes zero by a wide margin, so the sign change is not iid sampling noise; it is an association between two periods, not a cause, and the iid assumption ignores volatility clustering (a bootstrap interval is wider, but still excludes zero).",
                "incorrectExplanation": "A confidence interval for a change measures sampling uncertainty about the difference between the two population correlations; it says nothing about causes or the future, and its iid assumption must be checked."
            },
            "ro": {
                "title": "Un interval pentru o schimbare de corelație",
                "text": "Corelația S&P 500 - TLT a trecut de la -0,47 (2010-2020) la +0,11 (2022-2026). Intervalul iid de 95% pentru schimbare este [0,52; 0,65] (Fisher, perechi iid dintr-o distribuție Normală bivariată). Ce puteți conclude?",
                "options": [
                    "Șocul inflaționist din 2022 a cauzat schimbarea",
                    "Schimbarea depășește cu mult eroarea de eșantionare iid, dar intervalul nu îi identifică cauza și presupune randamente iid",
                    "Schimbarea nu este semnificativă, pentru că corelația din 2022-2026 este aproape de zero",
                    "Intervalul dovedește că corelația va rămîne pozitivă"
                ],
                "correctExplanation": "Intervalul exclude zero cu mult, deci schimbarea de semn nu este zgomot de eșantionare iid; este o asociere între două perioade, nu o cauză, iar ipoteza iid ignoră gruparea volatilității (un interval bootstrap este mai larg, dar exclude tot zero).",
                "incorrectExplanation": "Un interval de încredere pentru o schimbare măsoară incertitudinea de eșantionare a diferenței dintre cele două corelații din populație; nu spune nimic despre cauze sau despre viitor, iar ipoteza iid trebuie verificată."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Effective number of stocks",
                "text": "An index has five stocks with weights 0.40, 0.15, 0.15, 0.15 and 0.15. What is its effective number of stocks, N_eff = 1 / sum of squared weights?",
                "options": [
                    "5: the number of stocks",
                    "4.0",
                    "2.5: one over the largest weight",
                    "6.7: one over the smallest weight"
                ],
                "correctExplanation": "Sum of squared weights = 0.16 + 4 x 0.0225 = 0.25, so N_eff = 1/0.25 = 4.0: concentration makes the index behave like fewer equally weighted stocks.",
                "incorrectExplanation": "N_eff is the inverse Herfindahl index: 1/(0.40^2 + 4 x 0.15^2) = 1/0.25 = 4.0."
            },
            "ro": {
                "title": "Numărul efectiv de acțiuni",
                "text": "Un indice are cinci acțiuni cu ponderile 0,40, 0,15, 0,15, 0,15 și 0,15. Care este numărul efectiv de acțiuni, N_eff = 1 / suma pătratelor ponderilor?",
                "options": [
                    "5: numărul de acțiuni",
                    "4,0",
                    "2,5: unu supra ponderea maximă",
                    "6,7: unu supra ponderea minimă"
                ],
                "correctExplanation": "Suma pătratelor ponderilor = 0,16 + 4 x 0,0225 = 0,25, deci N_eff = 1/0,25 = 4,0: concentrarea face ca indicele să se comporte ca mai puține acțiuni cu ponderi egale.",
                "incorrectExplanation": "N_eff este inversul indicelui Herfindahl: 1/(0,40^2 + 4 x 0,15^2) = 1/0,25 = 4,0."
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
                "correctExplanation": "The 2022 decline followed the TerraUSD collapse and the wider crypto downturn; supply then recovered to about 308 bn USD by September 2026.",
                "incorrectExplanation": "Supply shrank after the TerraUSD collapse and the 2022 crypto downturn, then recovered."
            },
            "ro": {
                "title": "Stablecoins",
                "text": "Oferta totală de stablecoins legate de USD a atins maximul de 187,4 mld. USD pe 2 aprilie 2022 și a scăzut la 122,7 mld. USD pe 19 august 2023. Ce s-a întîmplat între timp?",
                "options": [
                    "Stablecoin-urile au fost interzise la nivel mondial",
                    "Fed a emis un dolar digital",
                    "Oferta s-a contractat după colapsul stablecoin-ului algoritmic TerraUSD și în timpul declinului cripto din 2022",
                    "Nimic: cifrele se referă la monede diferite"
                ],
                "correctExplanation": "Scăderea din 2022 a urmat colapsului TerraUSD și declinului general al pieței cripto; oferta a revenit apoi la circa 308 mld. USD în septembrie 2026.",
                "incorrectExplanation": "Oferta s-a redus după colapsul TerraUSD și declinul cripto din 2022, apoi și-a revenit."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Forward-filling weekends",
                "text": "To correlate the S&P 500 with Bitcoin you put both on Bitcoin's calendar (every day) and forward-fill the S&P 500 on weekends, then take log returns. What happens?",
                "options": [
                    "Nothing: forward-filling only fills missing values",
                    "The S&P 500 gains two extra genuine returns per week",
                    "Bitcoin's weekend returns disappear",
                    "Each weekend creates two zero S&P 500 returns paired with Bitcoin's weekend moves, which biases the correlation"
                ],
                "correctExplanation": "Forward-filled weekend prices give S&P 500 returns of exactly zero on Saturday and Sunday, paired with Bitcoin's real weekend moves; in 2022-2026 the correlation falls from 0.42 (common days) to 0.39. Join the prices on common days first, then take returns.",
                "incorrectExplanation": "The filled prices repeat Friday's close, so the S&P 500 return is zero on Saturday and Sunday while Bitcoin moves: artificial pairs that change the correlation. Join prices on common days first."
            },
            "ro": {
                "title": "Completarea weekendurilor",
                "text": "Pentru a corela S&P 500 cu Bitcoin, puneți ambele serii pe calendarul Bitcoin (în fiecare zi) și completați S&P 500 în weekend cu ultimul preț, apoi calculați log-randamentele. Ce se întîmplă?",
                "options": [
                    "Nimic: completarea doar umple valorile lipsă",
                    "S&P 500 primește două randamente reale în plus pe săptămînă",
                    "Randamentele Bitcoin din weekend dispar",
                    "Fiecare weekend creează două randamente nule ale S&P 500, puse lîngă mișcările Bitcoin din weekend, ceea ce deformează corelația"
                ],
                "correctExplanation": "Prețurile completate în weekend dau randamente S&P 500 exact nule sîmbăta și duminica, puse lîngă mișcările reale ale Bitcoin; în 2022-2026 corelația scade de la 0,42 (zile comune) la 0,39. Aliniați întîi prețurile pe zilele comune, apoi calculați randamentele.",
                "incorrectExplanation": "Prețurile completate repetă închiderea de vineri, deci randamentul S&P 500 este zero sîmbăta și duminica, în timp ce Bitcoin se mișcă: perechi artificiale care schimbă corelația. Aliniați întîi prețurile pe zilele comune."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Ranking two Sharpe ratios",
                "text": "2015-2026, 11.7 years: SPY Sharpe ratio 0.82, gold 0.77. A paired stationary-bootstrap 95% interval for the difference SPY minus gold is [-0.65; +0.88]. What follows?",
                "options": [
                    "The sample does not rank SPY above gold: the interval contains zero",
                    "SPY is significantly better because 0.82 > 0.77",
                    "Gold is significantly better because the interval reaches -0.65",
                    "The bootstrap is invalid because Sharpe ratios are not means"
                ],
                "correctExplanation": "With about 11.7 years each Sharpe ratio has a standard error near 1/sqrt(11.7) = 0.29, and the interval of the difference contains zero: the table describes the sample, it does not rank the assets.",
                "incorrectExplanation": "A difference of 0.05 is tiny relative to its sampling uncertainty; the interval [-0.65; +0.88] contains zero, so neither asset is shown to be better."
            },
            "ro": {
                "title": "Clasarea a două rapoarte Sharpe",
                "text": "2015-2026, 11,7 ani: raportul Sharpe al SPY 0,82, al aurului 0,77. Un interval bootstrap staționar de 95%, pe perechi, pentru diferența SPY minus aur este [-0,65; +0,88]. Ce rezultă?",
                "options": [
                    "Eșantionul nu plasează SPY deasupra aurului: intervalul îl conține pe zero",
                    "SPY este semnificativ mai bun, pentru că 0,82 > 0,77",
                    "Aurul este semnificativ mai bun, pentru că intervalul ajunge la -0,65",
                    "Bootstrap-ul nu este valid, pentru că rapoartele Sharpe nu sînt medii"
                ],
                "correctExplanation": "Cu circa 11,7 ani, fiecare raport Sharpe are o eroare standard de aproximativ 1/sqrt(11,7) = 0,29, iar intervalul diferenței îl conține pe zero: tabelul descrie eșantionul, nu clasează activele.",
                "incorrectExplanation": "O diferență de 0,05 este foarte mică față de incertitudinea ei de eșantionare; intervalul [-0,65; +0,88] îl conține pe zero, deci niciun activ nu se dovedește mai bun."
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
                "correctExplanation": "Un indice de randament total presupune reinvestirea dividendelor, deci crește mai repede decît indicele de preț cînd companiile plătesc dividende mari, cum fac multe blue chips românești.",
                "incorrectExplanation": "BET-TR este varianta de randament total a BET: dividendele sînt reinvestite."
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
                "text": "The EUR/RON market file gives an annualised volatility of 12.4% for 2015–2026, while the BNR reference rate gives 2.1%. Why?",
                "options": [
                    "The reference rate is a 30-day moving average of market quotes",
                    "The market file contains isolated bad ticks (e.g. +/-15% on 13–14 August 2025) that reverse the next day",
                    "EUR/RON is more volatile in the morning",
                    "The two series use different currencies"
                ],
                "correctExplanation": "A few spikes that reverse the next day inflate the standard deviation more than five-fold; removing weekend rows and outliers gives about 2.6%.",
                "incorrectExplanation": "Isolated bad ticks that reverse the next day inflate the measured volatility."
            },
            "ro": {
                "title": "Cotații eronate",
                "text": "Fișierul de piață EUR/RON dă o volatilitate anualizată de 12,4% pentru 2015–2026, iar cursul de referință BNR dă 2,1%. De ce?",
                "options": [
                    "Cursul de referință este o medie mobilă pe 30 de zile a cotațiilor de piață",
                    "Fișierul de piață conține cotații eronate izolate (de exemplu +/-15% pe 13–14 august 2025), inversate a doua zi",
                    "EUR/RON este mai volatil dimineața",
                    "Cele două serii folosesc monede diferite"
                ],
                "correctExplanation": "Cîteva vîrfuri inversate a doua zi umflă abaterea standard de peste cinci ori; eliminînd rîndurile de weekend și valorile aberante se obține circa 2,6%.",
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
                "text": "Ce cîmp de preț trebuie folosit pentru randamentele acțiunilor și ale ETF-urilor, precum SPY sau Banca Transilvania?",
                "options": [
                    "Prețul de deschidere",
                    "Prețul de închidere neajustat",
                    "Maximul zilei",
                    "Prețul de închidere ajustat, care ține cont de dividende și split-uri"
                ],
                "correctExplanation": "Prețurile ajustate includ dividendele și corecțiile pentru split-uri, deci randamentele reflectă ce a cîștigat efectiv investitorul.",
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
                    "S&P 500 cîștigă zile de tranzacționare în plus"
                ],
                "correctExplanation": "Diferențierea peste o valoare lipsă dă un randament lipsă, deci toate randamentele de luni dispar pe tăcute; pentru o singură serie, calculați randamentele pe calendarul ei; pentru o analiză comună (corelație, portofoliu), întîi join pe prețuri în zilele comune, apoi randamente, ca ambele să acopere același interval (vineri - luni).",
                "incorrectExplanation": "Pe un calendar reunit, golul de duminică elimină fiecare randament de luni al acțiunilor. Pentru o analiză comună, faceți întîi join pe prețuri în zilele comune, apoi calculați randamentele."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Survivorship and selection",
                "text": "An index of today's 100 largest coins, computed back to 2015, shows a CAGR of 70%. What is the main problem with this number?",
                "options": [
                    "Survivorship and look-ahead selection: coins that failed are missing",
                    "Volatility drag lowers the CAGR",
                    "The Epps effect",
                    "Non-synchronous trading across exchanges"
                ],
                "correctExplanation": "Choosing constituents with today's information keeps only the winners; failed coins are excluded, so the back-computed return is biased upward (Brown et al., 1992).",
                "incorrectExplanation": "The index is built from survivors known today, which biases past returns upward; the other effects do not explain a selection built with hindsight."
            },
            "ro": {
                "title": "Survivorship bias și selecție",
                "text": "Un indice al celor mai mari 100 de monede de azi, reconstruit ex post din 2015, arată un CAGR de 70%. Care este problema principală a acestei cifre?",
                "options": [
                    "Survivorship bias și selecția cu look-ahead bias: lipsesc monedele eșuate",
                    "Volatility drag scade CAGR",
                    "Efectul Epps",
                    "Tranzacționarea nesincronă între burse"
                ],
                "correctExplanation": "Alegerea componentelor cu informația de azi păstrează doar cîștigătorii; monedele eșuate sînt excluse, deci randamentul reconstruit ex post este deplasat în sus (Brown et al., 1992).",
                "incorrectExplanation": "Indicele este construit din supraviețuitorii cunoscuți azi, ceea ce deplasează în sus randamentele trecute; celelalte efecte nu explică o selecție făcută ex post."
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
                "text": "Indicele BET a atins maximul de 10.813,59 pe 24 iulie 2007 și a coborît la 1.887,14 pe 25 februarie 2009 (un drawdown de -82,5%). Cînd a închis pentru prima dată din nou peste maximul din 2007?",
                "options": [
                    "În 2009, la cîteva luni după minim",
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
                "text": "An AI assistant writes: \"The daily volatility of the S&P 500 is 1.2%. To annualise it, multiply by 252 trading days: the annual volatility is 302%.\" Assuming uncorrelated daily returns with constant variance, what is wrong?",
                "options": [
                    "Volatility grows with the square root of time: 1.2% × √252 ≈ 19.0% a year",
                    "An equity index must be annualised with 365 days, not 252",
                    "Volatility is annualised as (1 + 1.2%)^252 − 1",
                    "Nothing: variance and volatility both grow linearly with time"
                ],
                "correctExplanation": "For uncorrelated returns with constant variance, variance grows linearly with the horizon, so volatility grows with its square root: 1.2% × √252 ≈ 19.0%. A value of 302% is a warning sign in itself.",
                "incorrectExplanation": "Only the variance scales with the number of days; the volatility scales with √252, giving about 19.0% a year, not 302%."
            },
            "ro": {
                "title": "Găsiți eroarea AI: anualizarea volatilității",
                "text": "Un asistent AI scrie: „Volatilitatea zilnică a S&P 500 este 1,2%. Pentru anualizare, înmulțim cu 252 de zile de tranzacționare: volatilitatea anuală este 302%.” Presupunînd randamente zilnice necorelate, cu varianță constantă, ce este greșit?",
                "options": [
                    "Volatilitatea crește cu rădăcina pătrată a timpului: 1,2% × √252 ≈ 19,0% pe an",
                    "Un indice bursier se anualizează cu 365 de zile, nu cu 252",
                    "Volatilitatea se anualizează ca (1 + 1,2%)^252 − 1",
                    "Nimic: dispersia și volatilitatea cresc ambele liniar în timp"
                ],
                "correctExplanation": "Pentru randamente necorelate, cu varianță constantă, dispersia crește liniar cu orizontul, deci volatilitatea crește cu rădăcina lui: 1,2% × √252 ≈ 19,0%. O valoare de 302% este deja un semnal de alarmă.",
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
                    "ETF-urile nu plătesc dividende, deci cele două coloane sînt identice",
                    "Close este prețul tranzacționat fără dividende; pentru acțiuni și ETF-uri, adjusted close este cel corectat pentru dividende și splituri",
                    "Adjusted close corectează doar pentru splituri, niciodată pentru dividende"
                ],
                "correctExplanation": "Close este prețul brut de tranzacționare; adjusted close adaugă înapoi dividendele și spliturile. Folosirea lui close pentru SPY subestimează randamentul mediu cu aproximativ randamentul dividendelor.",
                "incorrectExplanation": "Close nu include dividendele: pentru acțiuni și ETF-uri cursul folosește adjusted close, corectat pentru dividende și splituri; SPY plătește dividende."
            }
        }
    ]
};

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
            "correct": 0,
            "en": {
                "title": "Square-root-of-time under AR(1)",
                "text": "EUR/RON (BNR fixing): daily lag-1 autocorrelation 0.17; the sqrt(252) rule gives an annual volatility of 4.4%. Assuming an AR(1), what is the corrected annual volatility?",
                "options": [
                    "About 5.3%: factor sqrt(1.17/0.83)",
                    "4.4%: autocorrelation does not affect annual volatility",
                    "About 3.7%: factor sqrt(0.83/1.17)",
                    "About 5.1%: factor 1.17"
                ],
                "correctExplanation": "For an AR(1) the variance ratio tends to (1 + rho)/(1 - rho), so volatility is multiplied by sqrt(1.17/0.83) = 1.19: 4.4% becomes 5.3%.",
                "incorrectExplanation": "Positive autocorrelation makes multi-day variance larger than h times the daily one: the factor is sqrt((1 + rho)/(1 - rho)) = 1.19, so about 5.3%."
            },
            "ro": {
                "title": "Regula rădăcinii pătrate a timpului pentru un AR(1)",
                "text": "EUR/RON (fixing BNR): autocorelația zilnică de ordinul 1 este 0,17; regula sqrt(252) dă o volatilitate anuală de 4,4%. Presupunând un AR(1), care este volatilitatea anuală corectată?",
                "options": [
                    "Circa 5,3%: factorul sqrt(1,17/0,83)",
                    "4,4%: autocorelația nu afectează volatilitatea anuală",
                    "Circa 3,7%: factorul sqrt(0,83/1,17)",
                    "Circa 5,1%: factorul 1,17"
                ],
                "correctExplanation": "Pentru un AR(1) raportul varianțelor tinde la (1 + rho)/(1 - rho), deci volatilitatea se înmulțește cu sqrt(1,17/0,83) = 1,19: 4,4% devine 5,3%.",
                "incorrectExplanation": "Autocorelația pozitivă face varianța pe mai multe zile mai mare decât de h ori cea zilnică: factorul este sqrt((1 + rho)/(1 - rho)) = 1,19, deci circa 5,3%."
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
                    "0,29: circa 1/sqrt(Y) când SR este estimat din date zilnice"
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
            "correct": 1,
            "en": {
                "title": "Maximum drawdown and the horizon",
                "text": "The same driftless process is observed over 10 years and over 40 years. How does the expected maximum drawdown (log scale) of the 40-year sample compare?",
                "options": [
                    "It is the same: drawdown does not depend on the horizon",
                    "About twice as large: it grows with sqrt(T)",
                    "About four times as large: it grows with T",
                    "Smaller: longer samples average out the losses"
                ],
                "correctExplanation": "For a driftless Brownian motion E[MDD] = sqrt(pi/2) sigma sqrt(T) (Magdon-Ismail et al., 2004): four times the horizon doubles the expected drawdown.",
                "incorrectExplanation": "The expected maximum drawdown of a driftless Brownian motion grows with sqrt(T), so 40 years give about twice the 10-year value; drawdowns from samples of different length are not comparable."
            },
            "ro": {
                "title": "Drawdown-ul maxim și orizontul",
                "text": "Același proces fără drift este observat pe 10 ani și pe 40 de ani. Cum se compară drawdown-ul maxim așteptat (pe scară logaritmică) al eșantionului de 40 de ani?",
                "options": [
                    "Este același: drawdown-ul nu depinde de orizont",
                    "Circa de două ori mai mare: crește cu sqrt(T)",
                    "Circa de patru ori mai mare: crește cu T",
                    "Mai mic: eșantioanele lungi compensează pierderile"
                ],
                "correctExplanation": "Pentru o mișcare browniană fără drift E[MDD] = sqrt(pi/2) sigma sqrt(T) (Magdon-Ismail et al., 2004): un orizont de patru ori mai lung dublează drawdown-ul așteptat.",
                "incorrectExplanation": "Drawdown-ul maxim așteptat al unei mișcări browniene fără drift crește cu sqrt(T), deci 40 de ani dau circa dublul valorii pe 10 ani; drawdown-urile din eșantioane de lungimi diferite nu sunt comparabile."
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
            "correct": 0,
            "en": {
                "title": "Correlation in turbulent periods",
                "text": "The true correlation between two markets is constant, but you estimate it only on days when the variance of the source market is several times higher. What happens to the estimate?",
                "options": [
                    "It is biased upward in absolute value (Forbes-Rigobon)",
                    "It is unbiased, only noisier",
                    "It is biased toward zero",
                    "It is undefined because the variance changes"
                ],
                "correctExplanation": "Conditioning on high variance gives rho* = rho sqrt((1 + delta)/(1 + delta rho^2)), larger than rho in absolute value: Bitcoin-S&P 500 is 0.52 on high-VIX days but 0.27 after the adjustment.",
                "incorrectExplanation": "Selecting high-variance days inflates the correlation even when the true one is constant: rho* = rho sqrt((1 + delta)/(1 + delta rho^2)) (Forbes and Rigobon, 2002)."
            },
            "ro": {
                "title": "Corelația în perioade turbulente",
                "text": "Corelația reală dintre două piețe este constantă, dar o estimați doar în zilele în care varianța pieței-sursă este de câteva ori mai mare. Ce se întâmplă cu estimația?",
                "options": [
                    "Este deplasată în sus în valoare absolută (Forbes-Rigobon)",
                    "Este nedeplasată, doar mai zgomotoasă",
                    "Este deplasată spre zero",
                    "Nu este definită, pentru că varianța se schimbă"
                ],
                "correctExplanation": "Condiționarea pe varianță mare dă rho* = rho sqrt((1 + delta)/(1 + delta rho^2)), mai mare decât rho în valoare absolută: Bitcoin-S&P 500 are 0,52 în zilele cu VIX ridicat, dar 0,27 după ajustare.",
                "incorrectExplanation": "Selectarea zilelor cu varianță mare umflă corelația chiar dacă cea reală este constantă: rho* = rho sqrt((1 + delta)/(1 + delta rho^2)) (Forbes și Rigobon, 2002)."
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
                "title": "Fisher z under volatility clustering",
                "text": "The stationary-bootstrap interval for the change in the stock-bond correlation is 1.54 times wider than the Fisher z interval. Why?",
                "options": [
                    "The bootstrap is biased and should not be used for correlations",
                    "The factor 1/(n - 3) is too large for long samples",
                    "Fisher z requires a positive correlation",
                    "Fisher's variance 1/(n - 3) assumes iid pairs; volatility clustering raises the variance of the estimated correlation"
                ],
                "correctExplanation": "atanh of the sample correlation has variance 1/(n - 3) only for iid Normal pairs; with dependent, heteroskedastic returns the sampling variance is larger, which the block bootstrap captures.",
                "incorrectExplanation": "The iid Fisher formula ignores the dependence created by volatility clustering; the stationary bootstrap resamples blocks of days and keeps it, so its interval is wider."
            },
            "ro": {
                "title": "Fisher z și gruparea volatilității",
                "text": "Intervalul bootstrap staționar pentru schimbarea corelației acțiuni-obligațiuni este de 1,54 ori mai larg decât intervalul Fisher z. De ce?",
                "options": [
                    "Bootstrap-ul este deplasat și nu trebuie folosit pentru corelații",
                    "Factorul 1/(n - 3) este prea mare pentru eșantioane lungi",
                    "Fisher z cere o corelație pozitivă",
                    "Varianța 1/(n - 3) a lui Fisher presupune perechi iid; gruparea volatilității crește varianța corelației estimate"
                ],
                "correctExplanation": "atanh din corelația de eșantion are varianța 1/(n - 3) doar pentru perechi iid cu distribuția Normală; cu randamente dependente și heteroscedastice varianța de eșantionare este mai mare, iar bootstrap-ul pe blocuri o surprinde.",
                "incorrectExplanation": "Formula iid a lui Fisher ignoră dependența creată de gruparea volatilității; bootstrap-ul staționar reeșantionează blocuri de zile și o păstrează, deci intervalul lui este mai larg."
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
            "correct": 2,
            "en": {
                "title": "Daily versus weekly correlation",
                "text": "Bitcoin vs S&P 500, 2022-2026: daily correlation 0.42, weekly 0.30. Which explanation is NOT consistent with the weekly value being lower?",
                "options": [
                    "Sampling noise of a 246-week estimate",
                    "Negative lagged cross-covariances between the two daily series",
                    "The Epps effect",
                    "The choice of the weekday used to anchor weekly returns"
                ],
                "correctExplanation": "The Epps effect says correlations measured over short intervals are biased toward zero, so it predicts a weekly correlation above the daily one; the observed gap has the opposite sign.",
                "incorrectExplanation": "Noise, negative lagged cross-covariances and the anchor day can all lower the weekly value; the Epps effect would raise it."
            },
            "ro": {
                "title": "Corelația zilnică versus cea săptămânală",
                "text": "Bitcoin vs S&P 500, 2022-2026: corelația zilnică 0,42, cea săptămânală 0,30. Care explicație NU este compatibilă cu valoarea săptămânală mai mică?",
                "options": [
                    "Zgomotul de eșantionare al unei estimații pe 246 de săptămâni",
                    "Covarianțe încrucișate decalate negative între cele două serii zilnice",
                    "Efectul Epps",
                    "Alegerea zilei din săptămână pentru ancorarea randamentelor săptămânale"
                ],
                "correctExplanation": "Efectul Epps spune că corelațiile măsurate pe intervale scurte sunt deplasate spre zero, deci prezice o corelație săptămânală peste cea zilnică; diferența observată are semnul opus.",
                "incorrectExplanation": "Zgomotul, covarianțele încrucișate decalate negative și ziua de ancorare pot toate coborî valoarea săptămânală; efectul Epps ar ridica-o."
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
                "title": "Supraviețuire și selecție",
                "text": "Un indice al celor mai mari 100 de monede de azi, calculat retroactiv din 2015, arată un CAGR de 70%. Care este problema principală a acestei cifre?",
                "options": [
                    "Supraviețuirea și selecția cu informație din viitor: lipsesc monedele eșuate",
                    "Frâna volatilității scade CAGR",
                    "Efectul Epps",
                    "Tranzacționarea nesincronă între burse"
                ],
                "correctExplanation": "Alegerea componentelor cu informația de azi păstrează doar câștigătorii; monedele eșuate sunt excluse, deci randamentul calculat retroactiv este deplasat în sus (Brown et al., 1992).",
                "incorrectExplanation": "Indicele este construit din supraviețuitorii cunoscuți azi, ceea ce deplasează în sus randamentele trecute; celelalte efecte nu explică o selecție făcută retroactiv."
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

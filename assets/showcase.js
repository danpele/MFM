// ============================================================
// MFM course website - showcase data: key formulas (grouped) and chart gallery
// Formulas link to the chapter that develops them (chapter `id`, see course-data.js).
// ============================================================
(function () {
    'use strict';
    const D = window.MFM_DATA;

    D.formulaGroups = [
        { id: 'returns', en: 'Returns and efficiency', ro: 'Randamente și eficiență' },
        { id: 'portfolio', en: 'Factors and portfolios', ro: 'Factori și portofolii' },
        { id: 'vol', en: 'Volatility and dependence', ro: 'Volatilitate și dependență' },
        { id: 'risk', en: 'Risk and backtesting', ro: 'Risc și backtesting' },
        { id: 'hf', en: 'High frequency and continuous time', ro: 'Frecvență înaltă și timp continuu' },
        { id: 'options', en: 'Options', ro: 'Opțiuni' },
        { id: 'ml', en: 'Machine learning and text', ro: 'Machine learning și text' },
        { id: 'crisis', en: 'Bubbles, systemic risk, crypto', ro: 'Bule, risc sistemic, cripto' }
    ];

    D.formulas = [
        // ---- course organisation / review
        { g: 'returns', ch: 'markets', en: 'Sharpe ratio and its standard error', ro: 'Raportul Sharpe și eroarea sa standard',
          tex: String.raw`$$\widehat{SR} = \frac{\bar r - r_f}{\hat\sigma}, \qquad \operatorname{se}(\widehat{SR}) \approx \sqrt{\frac{1 + \widehat{SR}^2/2}{T}} \;\;(\text{i.i.d.})$$` },
        { g: 'returns', ch: 'markets', en: 'Maximum drawdown', ro: 'Scăderea maximă (maximum drawdown)',
          tex: String.raw`$$\mathrm{MDD}_T = \max_{t \le T}\Big(1 - \frac{P_t}{\max_{s \le t} P_s}\Big)$$` },
        { g: 'ml', ch: 'wrap-up', en: 'Minimum detectable effect', ro: 'Efectul minim detectabil',
          tex: String.raw`$$\mathrm{MDE} = \big(z_{1-\alpha/2} + z_{1-\beta}\big)\,\operatorname{se}(\hat\theta) \approx 2.8\,\operatorname{se}(\hat\theta), \qquad (\alpha = 5\%,\ 1-\beta = 80\%)$$` },
        { g: 'ml', ch: 'wrap-up', en: 'Benjamini–Hochberg (false discovery rate)', ro: 'Benjamini–Hochberg (rata descoperirilor false)',
          tex: String.raw`$$\text{reject } H_{(1)},\dots,H_{(k)}, \qquad k = \max\Big\{i : p_{(i)} \le \frac{i}{m}\,q\Big\}$$` },
        // ---- returns and efficiency
        { g: 'returns', ch: 'stylized', en: 'Log returns and time aggregation', ro: 'Randamente logaritmice și agregarea în timp',
          tex: String.raw`$$r_t = \ln P_t - \ln P_{t-1}, \qquad r_t^{(k)} = \sum_{i=0}^{k-1} r_{t-i}$$` },
        { g: 'returns', ch: 'stylized', en: 'Ljung–Box test', ro: 'Testul Ljung–Box',
          tex: String.raw`$$Q(m) = T(T+2)\sum_{k=1}^{m}\frac{\hat\rho_k^2}{T-k} \;\xrightarrow{d}\; \chi^2_m$$` },
        { g: 'returns', ch: 'stylized', en: 'Hill estimator of the tail index', ro: 'Estimatorul Hill al indicelui de coadă',
          tex: String.raw`$$\hat\xi_k = \frac{1}{k}\sum_{i=1}^{k}\ln X_{(i)} - \ln X_{(k+1)}$$` },
        { g: 'returns', ch: 'efficiency', en: 'Variance ratio', ro: 'Raportul varianțelor',
          tex: String.raw`$$VR(q) = \frac{\operatorname{Var}\big(r_t^{(q)}\big)}{q\operatorname{Var}(r_t)} = 1 + 2\sum_{k=1}^{q-1}\Big(1-\frac{k}{q}\Big)\rho_k$$` },
        // ---- factors and portfolios
        { g: 'portfolio', ch: 'factors', en: 'CAPM', ro: 'CAPM',
          tex: String.raw`$$E[R_i] - R_f = \beta_i\,(E[R_m] - R_f), \qquad \beta_i = \frac{\operatorname{Cov}(R_i, R_m)}{\operatorname{Var}(R_m)}$$` },
        { g: 'portfolio', ch: 'factors', en: 'Fama–MacBeth second pass', ro: 'Al doilea pas Fama–MacBeth',
          tex: String.raw`$$r_{i,t} = \gamma_{0,t} + \boldsymbol\gamma_t^\top \hat{\boldsymbol\beta}_i + \eta_{i,t}, \qquad \hat{\boldsymbol\gamma} = \frac{1}{T}\sum_{t=1}^{T}\hat{\boldsymbol\gamma}_t$$` },
        { g: 'portfolio', ch: 'factors', en: 'GRS test of zero alphas', ro: 'Testul GRS pentru alfa nule',
          tex: String.raw`$$\mathrm{GRS} = \frac{T-N-L}{N}\,\frac{\hat{\boldsymbol\alpha}^\top\hat\Sigma^{-1}\hat{\boldsymbol\alpha}}{1+\bar{\boldsymbol\mu}^\top\hat\Omega^{-1}\bar{\boldsymbol\mu}} \sim F_{N,\,T-N-L}$$` },
        { g: 'portfolio', ch: 'portfolio', en: 'Global minimum-variance portfolio', ro: 'Portofoliul de varianță minimă globală',
          tex: String.raw`$$\mathbf w_{\mathrm{GMV}} = \frac{\Sigma^{-1}\mathbf 1}{\mathbf 1^\top\Sigma^{-1}\mathbf 1}, \qquad \sigma^2_{\mathrm{GMV}} = \frac{1}{\mathbf 1^\top\Sigma^{-1}\mathbf 1}$$` },
        { g: 'portfolio', ch: 'portfolio', en: 'Ledoit–Wolf shrinkage', ro: 'Contracția Ledoit–Wolf',
          tex: String.raw`$$\begin{gathered} \hat\Sigma_{\mathrm{LW}} = \delta^* F + (1-\delta^*)\,S \\ \delta^* = \arg\min_\delta E\big\|\delta F + (1-\delta)S - \Sigma\big\|_F^2 \end{gathered}$$` },
        { g: 'portfolio', ch: 'ml', en: 'Deflated Sharpe ratio', ro: 'Deflated Sharpe Ratio',
          tex: String.raw`$$\mathrm{DSR} = \Phi\!\left(\frac{(\widehat{SR} - SR_0)\sqrt{T-1}}{\sqrt{1 - \hat\gamma_3\widehat{SR} + \frac{\hat\gamma_4 - 1}{4}\widehat{SR}^2}}\right)$$` },
        // ---- volatility and dependence
        { g: 'vol', ch: 'garch', en: 'GJR-GARCH(1,1)', ro: 'GJR-GARCH(1,1)',
          tex: String.raw`$$\sigma_t^2 = \omega + \big(\alpha + \gamma\,\mathbf 1\{\varepsilon_{t-1} \lt 0\}\big)\varepsilon_{t-1}^2 + \beta\,\sigma_{t-1}^2$$` },
        { g: 'vol', ch: 'garch', en: 'Volatility forecast and half-life', ro: 'Prognoza volatilității și timpul de înjumătățire',
          tex: String.raw`$$E_t[\sigma^2_{t+h}] = \bar\sigma^2 + (\alpha+\beta)^{h-1}\big(\sigma^2_{t+1} - \bar\sigma^2\big), \quad h_{1/2} = \frac{\ln 0.5}{\ln(\alpha+\beta)}$$` },
        { g: 'vol', ch: 'dependence', en: 'DCC correlations', ro: 'Corelații DCC',
          tex: String.raw`$$\begin{gathered} Q_t = (1-a-b)\bar Q + a\,\mathbf z_{t-1}\mathbf z_{t-1}^\top + b\,Q_{t-1} \\ R_t = \operatorname{diag}(Q_t)^{-1/2}\, Q_t\, \operatorname{diag}(Q_t)^{-1/2} \end{gathered}$$` },
        { g: 'vol', ch: 'dependence', en: 'Sklar and t-copula tail dependence', ro: 'Sklar și dependența de coadă a copulei t',
          tex: String.raw`$$F(x,y) = C\big(F_X(x), F_Y(y)\big), \qquad \lambda = 2\,t_{\nu+1}\!\left(-\sqrt{\tfrac{(\nu+1)(1-\rho)}{1+\rho}}\right)$$` },
        // ---- risk and backtesting
        { g: 'risk', ch: 'var-es', en: 'VaR and Expected Shortfall', ro: 'VaR și Expected Shortfall',
          tex: String.raw`$$\mathrm{VaR}_\alpha = -q_\alpha(X), \qquad \mathrm{ES}_\alpha = -\frac{1}{\alpha}\int_0^\alpha q_u(X)\,du$$` },
        { g: 'risk', ch: 'var-es', en: 'Generalised Pareto tail', ro: 'Coada Pareto generalizată',
          tex: String.raw`$$\begin{gathered} P(L  \gt  u + y \mid L  \gt  u) = \Big(1 + \frac{\xi y}{\beta}\Big)^{-1/\xi} \\ \mathrm{VaR}_\alpha = u + \frac{\beta}{\xi}\Big[\Big(\frac{n\alpha}{N_u}\Big)^{-\xi} - 1\Big] \end{gathered}$$` },
        { g: 'risk', ch: 'backtesting', en: 'Kupiec unconditional coverage', ro: 'Acoperirea necondiționată Kupiec',
          tex: String.raw`$$LR_{uc} = -2\ln\frac{(1-\alpha)^{T-x}\alpha^{x}}{(1-\hat\pi)^{T-x}\hat\pi^{x}} \;\xrightarrow{d}\; \chi^2_1, \qquad \hat\pi = \frac{x}{T}$$` },
        { g: 'risk', ch: 'backtesting', en: 'FZ0 joint score for (VaR, ES)', ro: 'Scorul comun FZ0 pentru (VaR, ES)',
          tex: String.raw`$$S(v,e;y) = -\frac{1}{\alpha e}\,\mathbf 1\{y \le v\}(v - y) + \frac{v}{e} + \ln(-e) - 1, \quad v, e  \lt  0$$` },
        { g: 'risk', ch: 'tsfm', en: 'Diebold–Mariano test', ro: 'Testul Diebold–Mariano',
          tex: String.raw`$$d_t = L(e_{1,t}) - L(e_{2,t}), \qquad DM = \frac{\bar d}{\sqrt{\widehat{\mathrm{LRV}}(d_t)/T}} \;\xrightarrow{d}\; N(0,1)$$` },
        // ---- high frequency and continuous time
        { g: 'hf', ch: 'realized-vol', en: 'Realised and bipower variation', ro: 'Varianța realizată și variația bipower',
          tex: String.raw`$$\begin{gathered} RV_t = \sum_{i=1}^{n} r_{t,i}^2 \;\xrightarrow{p}\; \int_{t-1}^{t}\!\sigma_s^2\,ds + \sum J^2 \\ BV_t = \frac{\pi}{2}\sum_{i=2}^{n}|r_{t,i}||r_{t,i-1}| \;\xrightarrow{p}\; \int_{t-1}^{t}\!\sigma_s^2\,ds \end{gathered}$$` },
        { g: 'hf', ch: 'realized-vol', en: 'HAR model', ro: 'Modelul HAR',
          tex: String.raw`$$RV_{t+1} = \beta_0 + \beta_d RV_t + \beta_w RV_t^{(w)} + \beta_m RV_t^{(m)} + \varepsilon_{t+1}$$` },
        { g: 'hf', ch: 'microstructure', en: 'Roll spread and Kyle lambda', ro: 'Spread-ul Roll și lambda Kyle',
          tex: String.raw`$$s = 2\sqrt{-\operatorname{Cov}(\Delta p_t, \Delta p_{t-1})}, \qquad \Delta p = \lambda (x + u), \;\; \lambda = \frac{\sigma_v}{2\sigma_u}$$` },
        { g: 'hf', ch: 'continuous-time', en: 'Itô\'s lemma and GBM', ro: 'Lema lui Itô și GBM',
          tex: String.raw`$$\begin{gathered} df = \big(f_t + \mu f_x + \tfrac12\sigma^2 f_{xx}\big)dt + \sigma f_x\,dW_t \\ S_T = S_0 \exp\!\big((\mu - \sigma^2/2)T + \sigma W_T\big) \end{gathered}$$` },
        { g: 'hf', ch: 'continuous-time', en: 'Ornstein–Uhlenbeck (Vasicek)', ro: 'Ornstein–Uhlenbeck (Vasicek)',
          tex: String.raw`$$\begin{gathered} dX_t = \kappa(\theta - X_t)\,dt + \sigma\,dW_t \\ X_{t+\Delta} \mid X_t \sim N\!\Big(\theta + (X_t-\theta)e^{-\kappa\Delta},\; \tfrac{\sigma^2}{2\kappa}\big(1-e^{-2\kappa\Delta}\big)\Big) \end{gathered}$$` },
        { g: 'hf', ch: 'signatures', en: 'Path signature and Chen\'s identity', ro: 'Signatura unei căi și identitatea lui Chen',
          tex: String.raw`$$S(X)^{i_1\dots i_k}_{s,t} = \int_{s \lt u_1 \lt \dots \lt u_k \lt t} dX^{i_1}_{u_1}\cdots dX^{i_k}_{u_k}, \qquad S(X * Y) = S(X) \otimes S(Y)$$` },
        { g: 'hf', ch: 'signatures', en: 'Signature-kernel weights', ro: 'Ponderi din nucleul signaturii',
          tex: String.raw`$$w_\tau \propto \exp\!\Big(-\gamma\,\big\|\mathrm{Sig}^N(X_{\tau-l:\tau}) - \mathrm{Sig}^N(X_{t-l:t})\big\|^2\Big)$$` },
        // ---- options
        { g: 'options', ch: 'options', en: 'Black–Scholes call', ro: 'Call Black–Scholes',
          tex: String.raw`$$C = S\,\Phi(d_1) - K e^{-rT}\Phi(d_2), \qquad d_{1,2} = \frac{\ln(S/K) + (r \pm \sigma^2/2)T}{\sigma\sqrt{T}}$$` },
        { g: 'options', ch: 'options', en: 'Breeden–Litzenberger density', ro: 'Densitatea Breeden–Litzenberger',
          tex: String.raw`$$q_T(K) = e^{rT}\,\frac{\partial^2 C(K,T)}{\partial K^2}$$` },
        { g: 'options', ch: 'options', en: 'Model-free implied variance (VIX)', ro: 'Varianța implicită fără model (VIX)',
          tex: String.raw`$$\begin{gathered} \sigma^2_{\mathrm{MF}} = \frac{2e^{rT}}{T}\int_0^\infty \frac{O(K)}{K^2}\,dK \\ \mathrm{VRP}_t = \sigma^2_{\mathrm{MF},t} - E_t^{\mathbb P}[RV_{t,t+T}] \end{gathered}$$` },
        // ---- machine learning and text
        { g: 'ml', ch: 'ml', en: 'Lasso', ro: 'Lasso',
          tex: String.raw`$$\hat{\boldsymbol\beta} = \arg\min_{\boldsymbol\beta}\; \frac{1}{2T}\|\mathbf y - X\boldsymbol\beta\|_2^2 + \lambda\|\boldsymbol\beta\|_1$$` },
        { g: 'ml', ch: 'ml', en: 'Fractional differencing', ro: 'Diferențierea fracționară',
          tex: String.raw`$$\tilde X_t = \sum_{k=0}^{\infty} w_k X_{t-k}, \qquad w_0 = 1, \;\; w_k = -w_{k-1}\,\frac{d-k+1}{k}$$` },
        { g: 'ml', ch: 'tsfm', en: 'QLIKE loss for variance forecasts', ro: 'Funcția de pierdere QLIKE',
          tex: String.raw`$$L(\hat\sigma^2, RV) = \frac{RV}{\hat\sigma^2} - \ln\frac{RV}{\hat\sigma^2} - 1$$` },
        { g: 'ml', ch: 'llm', en: 'Sentiment scores', ro: 'Scoruri de sentiment',
          tex: String.raw`$$\tau = \frac{P - N}{P + N}, \qquad s = \hat p(\text{pos}) - \hat p(\text{neg}), \qquad \hat p = \operatorname{softmax}(\mathbf z / \vartheta)$$` },
        // ---- bubbles, systemic risk, crypto
        { g: 'crisis', ch: 'bubbles', en: 'GSADF test (Phillips–Shi–Yu)', ro: 'Testul GSADF (Phillips–Shi–Yu)',
          tex: String.raw`$$\mathrm{GSADF}(r_0) = \sup_{r_2 \in [r_0, 1]}\;\sup_{r_1 \in [0, r_2 - r_0]} \mathrm{ADF}_{r_1}^{r_2}$$` },
        { g: 'crisis', ch: 'bubbles', en: 'LPPLS', ro: 'LPPLS',
          tex: String.raw`$$\ln E[p(t)] = A + B(t_c - t)^m + C(t_c - t)^m\cos\!\big(\omega\ln(t_c - t) - \phi\big)$$` },
        { g: 'crisis', ch: 'systemic', en: 'ΔCoVaR', ro: 'ΔCoVaR',
          tex: String.raw`$$\begin{gathered} P\big(X^{s} \le \mathrm{CoVaR}_q^{s|i} \,\big|\, X^i = \mathrm{VaR}_q^i\big) = q \\ \Delta\mathrm{CoVaR}^{s|i} = \mathrm{CoVaR}_q^{s|\mathrm{VaR}^i_q} - \mathrm{CoVaR}_q^{s|\mathrm{med}^i} \end{gathered}$$` },
        { g: 'crisis', ch: 'systemic', en: 'SRISK', ro: 'SRISK',
          tex: String.raw`$$\mathrm{SRISK}_i = k\,D_i - (1-k)\,(1 - \mathrm{LRMES}_i)\,W_i$$` },
        { g: 'crisis', ch: 'digital-assets', en: 'Constant-product AMM', ro: 'AMM cu produs constant',
          tex: String.raw`$$x\,y = k, \qquad p = \frac{y}{x}, \qquad \mathrm{IL}(r) = \frac{2\sqrt r}{1 + r} - 1, \;\; r = \frac{p_1}{p_0}$$` }
    ];

    // One representative chart per chapter, shown on the chapter card (click to enlarge)
    D.chapterCharts = {
        'markets': { src: 'charts/ch0_cross_asset_growth.png', en: 'Growth of 1 USD across asset classes, 2015–2026', ro: 'Creșterea a 1 USD pe clase de active, 2015–2026' },
        'stylized': { src: 'charts/ch1_hist_qq.png', en: 'Fat tails: S&P 500 and Bitcoin against the Normal distribution', ro: 'Cozi groase: S&P 500 și Bitcoin față de distribuția Normală' },
        'efficiency': { src: 'charts/ch2_rolling_hurst.png', en: 'Time-varying memory: rolling DFA exponents', ro: 'Memorie variabilă în timp: exponenți DFA pe ferestre mobile' },
        'factors': { src: 'charts/ch3_factor_cum.png', en: 'Fama–French factors and momentum since 1963', ro: 'Factorii Fama–French și momentum din 1963' },
        'portfolio': { src: 'charts/ch4_frontier.png', en: 'Efficient frontier of sector ETFs', ro: 'Frontiera eficientă a ETF-urilor sectoriale' },
        'garch': { src: 'charts/ch5_sp500_vol.png', en: 'VIX against GARCH volatility, 2000–2026', ro: 'VIX față de volatilitatea GARCH, 2000–2026' },
        'dependence': { src: 'charts/ch6_copula_zoo.png', en: 'Five copulas with the same Kendall tau', ro: 'Cinci copule cu același tau Kendall' },
        'var-es': { src: 'charts/ch7_gpd_tail.png', en: 'Extreme value theory: GPD tails of daily losses', ro: 'Teoria valorilor extreme: cozi GPD ale pierderilor zilnice' },
        'backtesting': { src: 'charts/ch8_traffic_light.png', en: 'Basel traffic light for four VaR 1% models', ro: 'Semaforul Basel pentru patru modele VaR 1%' },
        'realized-vol': { src: 'charts/ch9_signature.png', en: 'Volatility signature plots: SPY and Bitcoin', ro: 'Grafice de semnătură a volatilității: SPY și Bitcoin' },
        'microstructure': { src: 'charts/ch10_lob_snapshot.png', en: 'A limit order book and its average depth', ro: 'Un registru de ordine limită și adâncimea sa medie' },
        'continuous-time': { src: 'charts/ch11_gbm_fan.png', en: 'Geometric Brownian motion: 20,000 paths of the S&P 500', ro: 'Mișcare browniană geometrică: 20.000 de traiectorii ale S&P 500' },
        'options': { src: 'charts/ch12_btc_smile.png', en: 'Bitcoin volatility smiles with SVI fits', ro: 'Zâmbetele de volatilitate Bitcoin, ajustate SVI' },
        'ml': { src: 'charts/ch13_deflated_sharpe.png', en: 'Deflated Sharpe ratio and the number of trials', ro: 'Deflated Sharpe Ratio și numărul de încercări' },
        'tsfm': { src: 'charts/ch14_fan_chart.png', en: 'Chronos-2 zero-shot volatility forecast', ro: 'Prognoza zero-shot a volatilității cu Chronos-2' },
        'llm': { src: 'charts/ch15_event_study.png', en: 'News sentiment: event study around headlines', ro: 'Sentimentul știrilor: studiu de eveniment în jurul titlurilor' },
        'digital-assets': { src: 'charts/ch16_ust_collapse.png', en: 'The collapse of TerraUSD, May 2022', ro: 'Prăbușirea TerraUSD, mai 2022' },
        'bubbles': { src: 'charts/ch17_lppls_btc2017.png', en: 'LPPLS on the 2017 Bitcoin bubble', ro: 'LPPLS pe bula Bitcoin din 2017' },
        'systemic': { src: 'charts/ch18_spill_network.png', en: 'Volatility spillover network of US, European and Romanian banks', ro: 'Rețeaua de contagiune a volatilității: bănci din SUA, Europa și România' },
        'signatures': { src: 'charts/ch20_qlike_ratio.png', en: 'Out-of-sample QLIKE relative to HAR across 50 VOLARE assets', ro: 'QLIKE în afara eșantionului față de HAR pe 50 de active VOLARE' },
        'wrap-up': { src: 'charts/ch19_bet_var.png', en: 'Case study: VaR 1% models on the BET index', ro: 'Studiu de caz: modele VaR 1% pe indicele BET' }
    };
})();

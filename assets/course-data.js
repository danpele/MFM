// ============================================================
// MFM course data (EN + RO). Rendered by assets/site.js.
// To publish a chapter: set available: true and fill in its links.
// ============================================================
(function () {
    const REPO = 'https://github.com/danpele/MFM';
    const COLAB = 'https://colab.research.google.com/github/danpele/MFM/blob/main/';

    // Quantinar courses (verified URLs), referenced by key from the chapters
    const Q = {
        digitalTransformation: ['Digital Transformation on Finance', 'https://quantinar.com/course/674/digital-transformation-on-finance'],
        cryptosNfts: ['Cryptos, NFTs, Digital Assets', 'https://quantinar.com/course/149/cryptos-nfts-digital-assets'],
        sfm: ['Statistics of Financial Markets', 'https://quantinar.com/course/103/statistics-of-financial-markets'],
        tukeyGH: ["Tukey's g- and h- transformations", 'https://quantinar.com/course/144/tukeys-g-and-h-transformations'],
        cryptoEfficiency: ['Efficiency of cryptocurrency markets - A GMM-based analysis', 'https://quantinar.com/course/184/efficiency-of-cryptocurrency-markets-a-gmm-based-analysis'],
        gmm: ['Generalized Method of Moments', 'https://quantinar.com/course/133/generalized-method-of-moments'],
        mva: ['MVA Multivariate Statistical Analysis', 'https://quantinar.com/course/540/multivariate-statistical-analysis'],
        hclust: ['Hierarchical Clustering', 'https://quantinar.com/course/101/hierarchical-clustering'],
        mst: ['Minimum Spanning Tree', 'https://quantinar.com/course/114/minimum-spanning-tree'],
        acf: ['Applied Computational Finance', 'https://quantinar.com/course/977/applied-computational-finance'],
        xfg: ['XFG Advanced Methods in Quantitative Finance', 'https://quantinar.com/course/100067/xfg-advanced-methods-in-quantitative-finance'],
        pricingKernels: ['Pricing Kernels and Risk Premia', 'https://quantinar.com/course/30/PricingKernels'],
        cryptoHedging: ['Hedging Cryptocurrency Options', 'https://quantinar.com/course/56/cryptohedging'],
        nonparametric: ['Nonparametric and Semiparametric Models', 'https://quantinar.com/course/750/nonparametric'],
        kalman: ['Kalman Filter', 'https://quantinar.com/course/42/methodology'],
        tsaPython: ['Applied Time Series Analysis with Python', 'https://quantinar.com/course/137/applied-time-series-analysis-with-python'],
        rf: ['Random Forests', 'https://quantinar.com/course/68/RF'],
        shapley: ['Shapley Values', 'https://quantinar.com/course/48/shapley'],
        mlRisk: ['Machine learning in Financial Risk', 'https://quantinar.com/course/934/machine-learning-in-financial-risk'],
        rl: ['Introduction to Reinforcement Learning', 'https://quantinar.com/course/36/ReinforcementLearning'],
        gans: ['Generative Adversarial Networks', 'https://quantinar.com/course/66/GANs'],
        xai: ['MSCA Digital: The Need for Explainable AI', 'https://quantinar.com/course/940/msca-digital-the-need-for-explainable-ai'],
        nlp: ['Natural Language Processing', 'https://quantinar.com/course/908/natural-language-processing'],
        delta: ['DELTA (Deep Learning for Text Analytics)', 'https://quantinar.com/course/963/delta'],
        lda: ['LDA Extensions', 'https://quantinar.com/course/41/LDA-extensions'],
        nextWord: ['The Next Word Problem', 'https://quantinar.com/course/100100/the-next-word-problem-full-course'],
        deda: ['DEDA Digital Economy & Decision Analytics', 'https://quantinar.com/course/23/Blockchain'],
        blockchainIntro: ['Introduction to Blockchain and Cryptocurrencies', 'https://quantinar.com/course/134/introduction-to-blockchain-and-cryptocurrencies'],
        ccIndices: ['Comparison of Cryptocurrency Indices', 'https://quantinar.com/course/65/___'],
        cryptoAsset: ['Cryptocurrency as an Asset Class', 'https://quantinar.com/course/55/cryptoasset'],
        smartContracts: ['Smart Contracts', 'https://quantinar.com/course/1037/smart-contracts'],
        cryptoLoans: ['On Crypto-backed Loans', 'https://quantinar.com/course/174/On-Crypto-backed-Loans'],
        stablecoinRisk: ['Stabilising Onchain Stablecoin Risks', 'https://quantinar.com/course/100110/stabilising-onchain-stablecoin-risks'],
        btcRiskPremia: ['Risk Premia in the Bitcoin Market', 'https://quantinar.com/course/100015/risk-premia-in-the-bitcoin-market'],
        cryptoSpeculative: ['Cryptocurrency: Speculative Asset and Medium of Exchange', 'https://quantinar.com/course/139/cryptocurrencies-from-an-economic-perspective'],
        statRisk: ['Measuring Statistical Risk', 'https://quantinar.com/course/100080/measuring-statistical-risk'],
        frm: ['Financial Risk Meter for Emerging Markets', 'https://quantinar.com/course/52/FRM'],
        cryptoNetworks: ['Dynamic Crypto Networks', 'https://quantinar.com/course/50/cryptonetworks'],
        centrality: ['Network Centrality', 'https://quantinar.com/course/84/lvu-network-centrality'],
        classifyCryptos: ['Are Cryptos becoming alternative Assets?', 'https://quantinar.com/course/87/classify_cryptos']
    };
    const q = (...keys) => keys.map(k => ({ title: Q[k][0], url: Q[k][1] }));

    // Links of the Financial Markets chapter (id 'markets')
    const marketsLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter0_financial_markets.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar0_financial_markets.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter0_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter0_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter0_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter0_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_00' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol0_piete_financiare.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar0_piete_financiare_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol0_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol0_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol0_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol0_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_00' }
        ]
    };

    // Links of the Stylized Facts chapter (id 'stylized')
    const stylizedLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter1_stylised_facts.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar1_stylised_facts.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter1_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter1_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter1_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter1_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_01' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol1_fapte_stilizate.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar1_fapte_stilizate_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol1_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol1_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol1_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol1_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_01' }
        ]
    };

    // Links of the chapter id 'efficiency'
    const efficiencyLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter2_market_efficiency.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar2_market_efficiency.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter2_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter2_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter2_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter2_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_02' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol2_eficienta_pietei.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar2_eficienta_pietei_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol2_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol2_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol2_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol2_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_02' }
        ]
    };

    // Links of the chapter id 'factors'
    const factorsLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter3_factor_models.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar3_factor_models.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter3_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter3_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter3_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter3_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_03' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol3_modele_factoriale.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar3_modele_factoriale_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol3_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol3_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol3_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol3_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_03' }
        ]
    };

    // Links of the chapter id 'var-es'
    const varEsLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter7_var_expected_shortfall.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar7_var_expected_shortfall.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter7_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter7_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter7_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter7_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_07' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol7_var_expected_shortfall.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar7_var_expected_shortfall_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol7_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol7_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol7_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol7_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_07' }
        ]
    };

    // Links of the chapter id 'garch'
    const garchLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter5_garch_models.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar5_garch_models.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter5_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter5_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter5_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter5_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_05' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol5_modele_garch.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar5_modele_garch_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol5_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol5_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol5_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol5_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_05' }
        ]
    };

    // Links of the chapter id 'portfolio'
    const portfolioLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter4_portfolio_optimization.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar4_portfolio_optimization.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter4_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter4_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter4_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter4_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_04' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol4_optimizarea_portofoliului.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar4_optimizarea_portofoliului_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol4_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol4_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol4_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol4_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_04' }
        ]
    };

    // Links of the chapter id 'backtesting'
    const backtestingLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter8_backtesting_risk.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar8_backtesting_risk.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter8_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter8_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter8_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter8_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_08' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol8_backtesting_risc.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar8_backtesting_risc_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol8_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol8_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol8_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol8_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_08' }
        ]
    };

    // Links of the chapter id 'dependence'
    const dependenceLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter6_multivariate_dependence.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar6_multivariate_dependence.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter6_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter6_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter6_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter6_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_06' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol6_dependenta_multivariata.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar6_dependenta_multivariata_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol6_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol6_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol6_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol6_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_06' }
        ]
    };

    // Links of the chapter id 'realized-vol'
    const realizedVolLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter9_realized_volatility.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar9_realized_volatility.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter9_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter9_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter9_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter9_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_09' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol9_volatilitate_realizata.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar9_volatilitate_realizata_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol9_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol9_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol9_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol9_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_09' }
        ]
    };

    // Links of the chapter id 'microstructure'
    const microstructureLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter10_market_microstructure.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar10_market_microstructure.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter10_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter10_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter10_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter10_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_10' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol10_microstructura_pietei.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar10_microstructura_pietei_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol10_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol10_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol10_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol10_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_10' }
        ]
    };

    // Links of the chapter id 'tsfm'
    const tsfmLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter14_deep_learning_foundation_models.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar14_deep_learning_foundation_models.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter14_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter14_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter14_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter14_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_14' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol14_deep_learning_modele_fundationale.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar14_deep_learning_modele_fundationale_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol14_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol14_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol14_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol14_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_14' }
        ]
    };

    // Links of the chapter id 'llm'
    const llmLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter15_llm_sentiment.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar15_llm_sentiment.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter15_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter15_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter15_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter15_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_15' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol15_llm_sentiment.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar15_llm_sentiment_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol15_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol15_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol15_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol15_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_15' }
        ]
    };

    // Links of the chapter id 'continuous-time'
    const continuousTimeLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter11_continuous_time.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar11_continuous_time.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter11_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter11_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter11_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter11_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_11' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol11_timp_continuu.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar11_timp_continuu_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol11_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol11_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol11_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol11_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_11' }
        ]
    };

    // Links of the chapter id 'options'
    const optionsLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter12_options_volatility_surface.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar12_options_volatility_surface.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter12_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter12_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter12_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter12_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_12' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol12_optiuni_suprafata_volatilitate.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar12_optiuni_suprafata_volatilitate_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol12_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol12_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol12_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol12_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_12' }
        ]
    };

    // Links of the chapter id 'wrap-up'
    const wrapUpLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter19_review_projects.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar19_review_projects.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter19_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter19_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter19_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter19_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_19' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol19_recapitulare_proiecte.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar19_recapitulare_proiecte_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol19_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol19_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol19_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol19_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_19' }
        ]
    };

    // Links of the chapter id 'digital-assets'
    const digitalAssetsLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter16_digital_assets_defi.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar16_digital_assets_defi.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter16_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter16_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter16_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter16_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_16' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol16_active_digitale_defi.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar16_active_digitale_defi_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol16_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol16_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol16_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol16_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_16' }
        ]
    };

    // Links of the chapter id 'systemic'
    const systemicLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter18_systemic_risk_networks.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar18_systemic_risk_networks.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter18_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter18_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter18_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter18_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_18' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol18_risc_sistemic_retele.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar18_risc_sistemic_retele_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol18_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol18_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol18_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol18_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_18' }
        ]
    };

    // Links of the chapter id 'bubbles'
    const bubblesLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter17_bubbles_crashes.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar17_bubbles_crashes.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter17_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter17_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter17_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter17_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_17' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol17_bule_crahuri.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar17_bule_crahuri_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol17_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol17_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol17_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol17_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_17' }
        ]
    };

    // Links of the Machine Learning chapter (id 'ml')
    const mlLinks = {
        en: [
            { type: 'slides', href: 'EN/Courses/chapter13_machine_learning.pdf' },
            { type: 'seminar', href: 'EN/Seminars/seminar13_machine_learning.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/EN/chapter13_lecture_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter13_lecture_notebook.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/EN/chapter13_seminar_notebook.ipynb', colab: COLAB + 'notebooks/EN/chapter13_seminar_notebook.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_13' }
        ],
        ro: [
            { type: 'slides', href: 'RO/Cursuri/capitol13_machine_learning.pdf' },
            { type: 'seminar', href: 'RO/Seminarii/seminar13_machine_learning_ro.pdf' },
            { type: 'lectureNb', href: REPO + '/blob/main/notebooks/RO/capitol13_notebook_curs.ipynb', colab: COLAB + 'notebooks/RO/capitol13_notebook_curs.ipynb' },
            { type: 'seminarNb', href: REPO + '/blob/main/notebooks/RO/capitol13_notebook_seminar.ipynb', colab: COLAB + 'notebooks/RO/capitol13_notebook_seminar.ipynb' },
            { type: 'quantlets', href: REPO + '/tree/main/Quantlets/Ch_13' }
        ]
    };

    window.MFM_DATA = {
        repo: REPO,

        // ---------------------------------------------------------------
        // UI strings
        // ---------------------------------------------------------------
        ui: {
            en: {
                pageTitle: 'Modelling Financial Markets - Course Website',
                courseTitle: 'Modelling Financial Markets',
                subtitle: "Master's programme Applied Statistics and Data Science | Faculty of Cybernetics, Statistics and Economic Informatics | Bucharest University of Economic Studies",
                nav: { home: 'Home', chapters: 'Chapters', project: 'Project &amp; AI', quizzes: 'Quizzes', resources: 'Resources', contact: 'Contact' },
                overview: 'Course Overview',
                objectives: 'Learning Objectives',
                heroTag: 'A research-grade course on financial markets: econometrics, risk, derivatives, machine learning and AI, on real data, with reproducible code.',
                heroCta1: 'Explore the chapters',
                heroCta2: 'Project and AI policy',
                stats: { chapters: 'chapters', slides: 'lecture slides', seminar: 'seminar pages', quantlets: 'Quantlets', quiz: 'quiz questions', charts: 'charts' },
                gallery: 'From the Lectures',
                galleryIntro: 'A selection of charts from the course, all built from real data with the code published as Quantlets. Click to enlarge.',
                formulasIntro: 'The core results of the course, grouped by theme. Each formula links to the chapter that derives it and tests it on data.',
                allFormulas: 'All',
                toChapter: 'Chapter',
                close: 'Close',
                formulas: 'Key Formulas',
                chapters: 'Course Chapters',
                chapter: 'Chapter',
                comingSoon: 'Coming soon',
                available: 'Available',
                selfStudy: 'Self-study',
                quantinar: 'Go deeper on Quantinar',
                links: {
                    slides: 'Lecture Slides', seminar: 'Seminar', lectureNb: 'Lecture Notebook',
                    seminarNb: 'Seminar Notebook', quantlets: 'Quantlets', colab: 'Open in Colab'
                },
                projectTitle: 'Team Project and the Use of AI',
                aiTitle: 'Using AI in this course',
                templates: 'Templates for your repository',
                attendanceForm: 'Attendance form (fill it in during each lecture and seminar, with the code on the board)',
                quizzes: 'Self-Assessment Quizzes',
                quizIntro: 'Each attempt draws 20 questions at random from the chapter bank and shuffles the answers. An answer is locked once selected.',
                loginPrompt: 'Log in with GitHub to record your quiz scores:',
                loginBtn: 'Login with GitHub',
                loggedAs: 'Logged in as',
                logout: 'Logout',
                quizSoon: 'The quiz for this chapter will be published together with its materials.',
                question: 'Question',
                correct: 'Correct!',
                incorrect: 'Incorrect.',
                correctIs: 'The correct answer is',
                calc: 'Calculate Score',
                reset: 'New attempt',
                score: 'Score',
                unanswered: 'questions unanswered',
                verdicts: ['Keep practicing!', 'Keep studying!', 'Good job!', 'Excellent!'],
                detailed: 'Detailed Results',
                colQ: 'Q', colQuestion: 'Question', colCorrect: 'Correct answer', colYours: 'Your answer', colResult: 'Result',
                resources: 'Resources',
                bibliography: 'Bibliography',
                dataSources: 'Data sources',
                contact: 'Contact',
                instructor: 'Lecturer',
                seminarCard: 'Seminar',
                seminarRole: 'Seminar instructor',
                office: 'Office Hours',
                officeText: 'By appointment',
                footer: 'Modelling Financial Markets | Faculty of Cybernetics, Statistics and Economic Informatics | Bucharest University of Economic Studies'
            },
            ro: {
                pageTitle: 'Modelarea piețelor financiare - Site-ul cursului',
                courseTitle: 'Modelarea piețelor financiare',
                subtitle: 'Masterul Statistică aplicată și Data Science | Facultatea de Cibernetică, Statistică și Informatică Economică | Academia de Studii Economice din București',
                nav: { home: 'Acasă', chapters: 'Capitole', project: 'Proiect și AI', quizzes: 'Quiz-uri', resources: 'Resurse', contact: 'Contact' },
                overview: 'Prezentarea cursului',
                objectives: 'Obiective de învățare',
                heroTag: 'Un curs de nivel de cercetare despre piețele financiare: econometrie, risc, derivate, machine learning și AI, pe date reale, cu cod reproductibil.',
                heroCta1: 'Explorați capitolele',
                heroCta2: 'Proiectul și politica AI',
                stats: { chapters: 'capitole', slides: 'slide-uri de curs', seminar: 'pagini de seminar', quantlets: 'Quantlets', quiz: 'întrebări de quiz', charts: 'grafice' },
                gallery: 'Din cursuri',
                galleryIntro: 'O selecție de grafice din curs, construite din date reale, cu codul publicat ca Quantlets. Click pentru mărire.',
                formulasIntro: 'Rezultatele centrale ale cursului, grupate pe teme. Fiecare formulă trimite la capitolul care o derivă și o testează pe date.',
                allFormulas: 'Toate',
                toChapter: 'Capitolul',
                close: 'Închide',
                formulas: 'Formule cheie',
                chapters: 'Capitolele cursului',
                chapter: 'Capitolul',
                comingSoon: 'În pregătire',
                available: 'Disponibil',
                selfStudy: 'Studiu individual',
                quantinar: 'Aprofundare pe Quantinar',
                links: {
                    slides: 'Slide-uri curs', seminar: 'Seminar', lectureNb: 'Notebook curs',
                    seminarNb: 'Notebook seminar', quantlets: 'Quantlets', colab: 'Deschide în Colab'
                },
                projectTitle: 'Proiectul de echipă și utilizarea AI',
                aiTitle: 'Utilizarea AI în acest curs',
                templates: 'Șabloane pentru repository-ul vostru',
                attendanceForm: 'Formularul de prezență (se completează la fiecare curs și seminar, cu codul de pe tablă)',
                quizzes: 'Quiz-uri de autoevaluare',
                quizIntro: 'La fiecare încercare se extrag aleator 20 de întrebări din banca de întrebări a capitolului, iar variantele de răspuns sunt amestecate. Răspunsul se blochează după selectare.',
                loginPrompt: 'Autentifică-te cu GitHub pentru a înregistra scorurile:',
                loginBtn: 'Autentificare cu GitHub',
                loggedAs: 'Autentificat ca',
                logout: 'Ieșire',
                quizSoon: 'Quiz-ul acestui capitol va fi publicat împreună cu materialele sale.',
                question: 'Întrebarea',
                correct: 'Corect!',
                incorrect: 'Greșit.',
                correctIs: 'Răspunsul corect este',
                calc: 'Calculează scorul',
                reset: 'Încercare nouă',
                score: 'Scor',
                unanswered: 'întrebări fără răspuns',
                verdicts: ['Mai exersează!', 'Mai studiază!', 'Bine!', 'Excelent!'],
                detailed: 'Rezultate detaliate',
                colQ: 'Nr.', colQuestion: 'Întrebare', colCorrect: 'Răspuns corect', colYours: 'Răspunsul tău', colResult: 'Rezultat',
                resources: 'Resurse',
                bibliography: 'Bibliografie',
                dataSources: 'Surse de date',
                contact: 'Contact',
                instructor: 'Titular curs',
                seminarCard: 'Seminar',
                seminarRole: 'Titular seminar',
                office: 'Program de consultații',
                officeText: 'Cu programare',
                footer: 'Modelarea piețelor financiare | Facultatea de Cibernetică, Statistică și Informatică Economică | Academia de Studii Economice din București'
            }
        },

        // ---------------------------------------------------------------
        // Overview cards, objectives, formulas
        // ---------------------------------------------------------------
        overview: {
            en: [
                { h: 'Course', p: ['Modelling Financial Markets', "Master's programme Applied Statistics and Data Science", 'Bucharest University of Economic Studies'] },
                { h: 'Schedule', p: ['<strong>Lectures:</strong> 2 hours/week', '<strong>Seminars:</strong> 2 hours/week', 'Academic year 2026/2027'] },
                { h: 'Prerequisites', p: ['Probability &amp; statistics', 'Econometrics / time series', 'Python programming'] },
                { h: 'Assessment', p: ['Team project (GitHub + presentation + oral defence): 70%', 'Quizzes &amp; activity: 20%', 'Attendance: 10% (at least 4 lectures and 4 seminars)'] },
                { h: 'Tools', p: ['Python, Jupyter / Google Colab', 'GitHub, Quantlet, Quantinar'] }
            ],
            ro: [
                { h: 'Curs', p: ['Modelarea piețelor financiare', 'Masterul Statistică aplicată și Data Science', 'Academia de Studii Economice din București'] },
                { h: 'Orar', p: ['<strong>Curs:</strong> 2 ore/săptămână', '<strong>Seminar:</strong> 2 ore/săptămână', 'Anul universitar 2026/2027'] },
                { h: 'Cunoștințe necesare', p: ['Probabilități și statistică', 'Econometrie / serii de timp', 'Programare în Python'] },
                { h: 'Evaluare', p: ['Proiect în echipă (GitHub + prezentare + susținere orală): 70%', 'Quiz-uri și activitate: 20%', 'Prezență: 10% (cel puțin 4 cursuri și 4 seminarii)'] },
                { h: 'Instrumente', p: ['Python, Jupyter / Google Colab', 'GitHub, Quantlet, Quantinar'] }
            ]
        },

        objectives: {
            en: [
                'Describe the structure of modern financial markets, from exchanges and ETFs to tokenised and crypto assets',
                'Document the stylised facts of returns and test market efficiency with modern tools',
                'Build and estimate factor, portfolio, continuous-time and option-pricing models on real data',
                'Model volatility, tail risk and systemic risk, backtest VaR / ES correctly and evaluate risk forecasts with consistent scoring functions and conformal prediction',
                'Apply machine learning, time-series foundation models and LLMs to financial data without leakage or backtest overfitting',
                'Deliver reproducible research in Python and GitHub, documented as Quantlets'
            ],
            ro: [
                'Descrierea structurii piețelor financiare moderne, de la burse și ETF-uri la active tokenizate și cripto',
                'Documentarea faptelor stilizate ale randamentelor și testarea eficienței pieței cu instrumente moderne',
                'Construirea și estimarea modelelor factoriale, de portofoliu, în timp continuu și de evaluare a opțiunilor pe date reale',
                'Modelarea volatilității, a riscului de coadă și a riscului sistemic, backtesting-ul corect al VaR / ES și evaluarea prognozelor de risc cu funcții de scor consistente și conformal prediction',
                'Aplicarea machine learning, a modelelor fundaționale pentru serii de timp și a LLM-urilor pe date financiare fără scurgeri de informație sau overfitting de backtest',
                'Realizarea de cercetare reproductibilă în Python și GitHub, documentată ca Quantlets'
            ]
        },


        // ---------------------------------------------------------------
        // Chapters 0-19. `id` is the stable key (quizzes, anchors, tabs);
        // `num` is only the display order. selfStudy: true shows a badge.
        // ---------------------------------------------------------------
        chapters: [
            {
                id: 'markets', num: 0, selfStudy: false, available: true,
                title: { en: 'Financial Markets in 2026', ro: 'Piețele financiare în 2026' },
                topics: {
                    en: ['Market structure: exchanges, OTC, dark pools', 'ETFs and passive investing', 'The Bucharest Stock Exchange (BVB)', 'Tokenisation and real-world assets (RWA), MiCA'],
                    ro: ['Structura pieței: burse, OTC, dark pools', 'ETF-uri și investiții pasive', 'Bursa de Valori București (BVB)', 'Tokenizare și active reale (RWA), MiCA']
                },
                links: marketsLinks,
                quantinar: q('digitalTransformation', 'cryptosNfts')
            },
            {
                id: 'stylized', num: 1, selfStudy: false, available: true,
                title: { en: 'Stylized Facts and Returns', ro: 'Fapte stilizate și randamente' },
                topics: {
                    en: ['Simple vs log returns, aggregation', 'Heavy tails and non-normality', 'Volatility clustering', 'Leverage effect', 'S&P 500, BET and Bitcoin compared'],
                    ro: ['Randamente simple vs logaritmice, agregare', 'Cozi groase și non-normalitate', 'Grupări de volatilitate', 'Efectul de levier', 'Comparație S&P 500, BET și Bitcoin']
                },
                links: stylizedLinks,
                quantinar: q('sfm', 'tukeyGH')
            },
            {
                id: 'efficiency', num: 2, selfStudy: false, available: true,
                title: { en: 'Market Efficiency: From EMH to Adaptive Markets', ro: 'Eficiența pieței: de la EMH la piețe adaptive' },
                topics: {
                    en: ['Efficient Market Hypothesis', 'Adaptive Market Hypothesis', 'Time-varying efficiency (rolling Hurst, variance ratio)', 'Anomalies'],
                    ro: ['Ipoteza pieței eficiente', 'Ipoteza pieței adaptive', 'Eficiență variabilă în timp (Hurst rulant, variance ratio)', 'Anomalii']
                },
                links: efficiencyLinks,
                quantinar: q('cryptoEfficiency', 'gmm')
            },
            {
                id: 'factors', num: 3, selfStudy: false, available: true,
                title: { en: 'Factor Models and Asset Pricing', ro: 'Modele factoriale și evaluarea activelor' },
                topics: {
                    en: ['CAPM and its tests', 'Fama-French 5 factors, momentum', 'The factor zoo', 'Fama-MacBeth regressions', 'Latent factors: PCA, IPCA'],
                    ro: ['CAPM și testarea sa', 'Modelul Fama-French cu 5 factori, momentum', '„Grădina zoologică” a factorilor', 'Regresii Fama-MacBeth', 'Factori latenți: PCA, IPCA']
                },
                links: factorsLinks,
                quantinar: q('gmm', 'mva')
            },
            {
                id: 'portfolio', num: 4, selfStudy: false, available: true,
                title: { en: 'Portfolio Optimization', ro: 'Optimizarea portofoliului' },
                topics: {
                    en: ['Markowitz and its limits', 'Black-Litterman', 'Risk parity', 'Hierarchical Risk Parity (HRP)', 'Covariance shrinkage, out-of-sample backtests'],
                    ro: ['Markowitz și limitele sale', 'Black-Litterman', 'Risk parity', 'Hierarchical Risk Parity (HRP)', 'Shrinkage al covarianței, backtest out-of-sample']
                },
                links: portfolioLinks,
                quantinar: q('hclust', 'mst')
            },
            {
                id: 'garch', num: 5, selfStudy: false, available: true,
                title: { en: 'Conditional Volatility: GARCH Models', ro: 'Volatilitate condiționată: modele GARCH' },
                topics: {
                    en: ['ARCH and GARCH', 'GJR-GARCH, EGARCH', 'Student-t and skew-t distributions', 'Estimation and volatility forecasting'],
                    ro: ['ARCH și GARCH', 'GJR-GARCH, EGARCH', 'Distribuții t și skew-t', 'Estimare și prognoza volatilității']
                },
                links: garchLinks,
                quantinar: q('sfm', 'tsaPython')
            },
            {
                id: 'dependence', num: 6, selfStudy: false, available: true,
                title: { en: 'Multivariate Volatility and Dependence', ro: 'Volatilitate multivariată și dependență' },
                topics: {
                    en: ['DCC-GARCH', 'Copulas', 'Tail dependence', 'Correlations in crisis periods'],
                    ro: ['DCC-GARCH', 'Copule', 'Dependență în cozi', 'Corelații în perioade de criză']
                },
                links: dependenceLinks,
                quantinar: q('statRisk', 'mva')
            },
            {
                id: 'var-es', num: 7, selfStudy: false, available: true,
                title: { en: 'Value-at-Risk and Expected Shortfall', ro: 'VaR și Expected Shortfall' },
                topics: {
                    en: ['Historical, filtered historical simulation, parametric and Monte Carlo VaR', 'Expected Shortfall', 'Extreme value theory: GPD / POT'],
                    ro: ['VaR istoric, filtered HS, parametric și Monte Carlo', 'Expected Shortfall', 'Teoria valorilor extreme: GPD / POT']
                },
                links: varEsLinks,
                quantinar: q('statRisk', 'xfg')
            },
            {
                id: 'backtesting', num: 8, selfStudy: false, available: true,
                title: { en: 'Backtesting and Evaluating Risk Forecasts', ro: 'Backtesting și evaluarea prognozelor de risc' },
                topics: {
                    en: ['Kupiec and Christoffersen tests', 'ES backtests', 'Fissler-Ziegel scoring functions', 'Diebold-Mariano test', 'Conformal prediction for tail risk', 'Basel FRTB'],
                    ro: ['Testele Kupiec și Christoffersen', 'Backtesting pentru ES', 'Funcții de scor Fissler-Ziegel', 'Testul Diebold-Mariano', 'Conformal prediction pentru riscul de coadă', 'Basel FRTB']
                },
                links: backtestingLinks,
                quantinar: q('mlRisk')
            },
            {
                id: 'realized-vol', num: 9, selfStudy: false, available: true,
                title: { en: 'Realized Volatility', ro: 'Volatilitate realizată' },
                topics: {
                    en: ['Realised variance from intraday data', 'Microstructure noise', 'HAR-RV model', 'HAR-RV vs GARCH forecasts', 'Rough volatility (optional)'],
                    ro: ['Varianța realizată din date intraday', 'Zgomotul de microstructură', 'Modelul HAR-RV', 'Prognoze HAR-RV vs GARCH', 'Rough volatility (opțional)']
                },
                links: realizedVolLinks,
                quantinar: q('nonparametric', 'kalman', 'tsaPython')
            },
            {
                id: 'microstructure', num: 10, selfStudy: false, available: true,
                title: { en: 'Market Microstructure', ro: 'Microstructura pieței' },
                topics: {
                    en: ['The limit order book', 'Bid-ask spread and liquidity', 'Market impact, Kyle and Almgren-Chriss', 'High-frequency trading', 'Crypto exchange order books'],
                    ro: ['Registrul de ordine limită', 'Spread-ul bid-ask și lichiditatea', 'Impactul de piață, Kyle și Almgren-Chriss', 'Tranzacționarea de înaltă frecvență', 'Order book-ul exchange-urilor cripto']
                },
                links: microstructureLinks,
                quantinar: q('acf')
            },
            {
                id: 'continuous-time', num: 11, selfStudy: false, available: true,
                title: { en: 'Continuous-Time Models', ro: 'Modele în timp continuu' },
                topics: {
                    en: ['Brownian motion and Itô calculus through simulation', 'Geometric Brownian motion', 'Merton jump-diffusion', 'Heston stochastic volatility (intuition)'],
                    ro: ['Mișcarea browniană și calculul Itô prin simulare', 'Mișcarea browniană geometrică', 'Modelul cu salturi Merton', 'Volatilitatea stochastică Heston (intuiție)']
                },
                links: continuousTimeLinks,
                quantinar: q('acf', 'xfg')
            },
            {
                id: 'options', num: 12, selfStudy: false, available: true,
                title: { en: 'Options and the Volatility Surface', ro: 'Opțiuni și suprafața de volatilitate' },
                topics: {
                    en: ['Black-Scholes and the Greeks', 'Implied volatility, smile and skew', 'VIX and 0DTE options', 'Bitcoin options (Deribit)'],
                    ro: ['Black-Scholes și indicatorii Greeks', 'Volatilitatea implicită, smile și skew', 'VIX și opțiunile 0DTE', 'Opțiuni pe Bitcoin (Deribit)']
                },
                links: optionsLinks,
                quantinar: q('xfg', 'pricingKernels', 'cryptoHedging')
            },
            {
                id: 'ml', num: 13, selfStudy: false, available: true,
                title: { en: 'Machine Learning in Finance', ro: 'Machine Learning în finanțe' },
                topics: {
                    en: ['ML foundations: LASSO / Ridge, trees, random forests, boosting', 'Fractional differentiation', 'Triple-barrier labelling and meta-labelling', 'Purged cross-validation with embargo', 'Feature importance: MDI, MDA, SHAP', 'Backtest overfitting and the Deflated Sharpe Ratio'],
                    ro: ['Fundamente ML: LASSO / Ridge, arbori, random forest, boosting', 'Diferențierea fracționară', 'Etichetarea cu trei bariere și meta-labelling', 'Validare încrucișată cu purjare și embargo', 'Importanța variabilelor: MDI, MDA, SHAP', 'Overfitting-ul de backtest și Deflated Sharpe Ratio']
                },
                links: mlLinks,
                quantinar: q('rf', 'shapley', 'mlRisk', 'rl', 'gans', 'xai')
            },
            {
                id: 'tsfm', num: 14, selfStudy: false, available: true,
                title: { en: 'Deep Learning and Time-Series Foundation Models', ro: 'Deep learning și modele fundaționale pentru serii de timp' },
                topics: {
                    en: ['LSTM and Transformers for financial time series', 'Chronos, TimesFM, Moirai', 'Zero-shot forecasting of quantiles and ES', 'Evaluation with the tools of chapter 8'],
                    ro: ['LSTM și Transformer pentru serii financiare', 'Chronos, TimesFM, Moirai', 'Prognoza zero-shot a cuantilelor și a ES', 'Evaluare cu instrumentele din capitolul 8']
                },
                links: tsfmLinks,
                quantinar: []
            },
            {
                id: 'llm', num: 15, selfStudy: false, available: true,
                title: { en: 'LLMs and Sentiment Analysis', ro: 'LLM-uri și analiza sentimentului' },
                topics: {
                    en: ['From dictionaries to FinBERT', 'LLMs on news and earnings calls', 'Text embeddings as features', 'AI agents in trading', 'From sentiment score to trading signal'],
                    ro: ['De la dicționare la FinBERT', 'LLM-uri pe știri și earnings calls', 'Embeddings de text ca variabile', 'Agenți AI în tranzacționare', 'De la scorul de sentiment la semnal de tranzacționare']
                },
                links: llmLinks,
                quantinar: q('nlp', 'delta', 'lda', 'nextWord', 'deda')
            },
            {
                id: 'digital-assets', num: 16, selfStudy: false, available: true,
                title: { en: 'Digital Assets and DeFi', ro: 'Active digitale și DeFi' },
                topics: {
                    en: ['CRIX and crypto indices', 'Stablecoins and depeg risk', 'Automated market makers (Uniswap)', 'Spot BTC / ETH ETFs', 'On-chain data and tokenisation'],
                    ro: ['CRIX și indicii cripto', 'Stablecoins și riscul de depeg', 'Automated market makers (Uniswap)', 'ETF-uri spot pe BTC / ETH', 'Date on-chain și tokenizare']
                },
                links: digitalAssetsLinks,
                quantinar: q('classifyCryptos', 'blockchainIntro', 'ccIndices', 'cryptoAsset', 'smartContracts', 'cryptoLoans', 'stablecoinRisk', 'btcRiskPremia')
            },
            {
                id: 'bubbles', num: 17, selfStudy: false, available: true,
                title: { en: 'Bubbles and Crashes', ro: 'Bule și crahuri' },
                topics: {
                    en: ['Log-periodic power law (LPPL)', 'Explosiveness tests: PSY / GSADF', 'Regime-switching models', 'Crypto and AI bubbles'],
                    ro: ['Modelul log-periodic power law (LPPL)', 'Teste de explozivitate: PSY / GSADF', 'Modele cu schimbare de regim', 'Bule cripto și AI']
                },
                links: bubblesLinks,
                quantinar: q('cryptoSpeculative')
            },
            {
                id: 'systemic', num: 18, selfStudy: false, available: true,
                title: { en: 'Systemic Risk and Networks', ro: 'Risc sistemic și rețele' },
                topics: {
                    en: ['CoVaR and SRISK', 'Diebold-Yilmaz spillover networks', 'Financial Risk Meter (FRM)', 'Climate risk', 'Stress testing'],
                    ro: ['CoVaR și SRISK', 'Rețele de contagiune Diebold-Yilmaz', 'Financial Risk Meter (FRM)', 'Riscul climatic', 'Teste de stres']
                },
                links: systemicLinks,
                quantinar: q('frm', 'cryptoNetworks', 'centrality')
            },
            {
                id: 'wrap-up', num: 19, selfStudy: false, available: true,
                title: { en: 'Review and Project Presentations', ro: 'Recapitulare și prezentarea proiectelor' },
                topics: {
                    en: ['Course review', 'Project preparation and feedback', 'Team project presentations'],
                    ro: ['Recapitularea cursului', 'Pregătirea proiectelor și feedback', 'Prezentarea proiectelor în echipă']
                },
                links: wrapUpLinks,
                quantinar: q('sfm')
            }
        ],

        // ---------------------------------------------------------------
        // Team project and AI policy (section #project)
        // ---------------------------------------------------------------
        project: {
            en: [
                { h: '1. Replicate', p: ['Start by reproducing one published number: a table, a coefficient or a backtest result from a paper or from the lecture.', 'An AI assistant cannot guess an exact published figure. Matching it shows that your data and code are right.'] },
                { h: '2. Extend', p: ['Apply the method to new data, a new market (for example BVB or crypto) or a more recent sample.', 'State one clear question and answer it with a test, not only with a chart.'] },
                { h: '3. Deliver on GitHub', p: ['A public repository with code, data description and a README that reproduces every result.', 'The files <code>AI_USE.md</code> and <code>AI_ERRORS.md</code> (templates below) are mandatory.'] },
                { h: '4. Present and defend', p: ['Team presentation, then a 10-minute oral defence.', 'Each member explains one result and answers a "what changes if..." question. Grades can differ between team members.'] }
            ],
            ro: [
                { h: '1. Replicați', p: ['Începeți prin a reproduce un rezultat publicat: un tabel, un coeficient sau un rezultat de backtest dintr-un articol sau din curs.', 'Un asistent AI nu poate ghici o cifră publicată exactă. Dacă o obțineți, datele și codul vostru sunt corecte.'] },
                { h: '2. Extindeți', p: ['Aplicați metoda pe date noi, pe altă piață (de exemplu BVB sau cripto) sau pe un eșantion mai recent.', 'Formulați o întrebare clară și răspundeți cu un test, nu doar cu un grafic.'] },
                { h: '3. Livrați pe GitHub', p: ['Un repository public cu cod, descrierea datelor și un README care reproduce fiecare rezultat.', 'Fișierele <code>AI_USE.md</code> și <code>AI_ERRORS.md</code> (șabloanele de mai jos) sunt obligatorii.'] },
                { h: '4. Prezentați și susțineți', p: ['Prezentarea echipei, apoi o susținere orală de 10 minute.', 'Fiecare membru explică un rezultat și răspunde la o întrebare de tipul „ce se schimbă dacă...”. Notele pot diferi între membrii echipei.'] }
            ]
        },

        aiPolicy: {
            en: [
                '<strong>AI is allowed</strong> for code, debugging, literature search and writing, in the project and in the seminars.',
                '<strong>AI use must be declared</strong> in <code>AI_USE.md</code>: which tool, for what, and what you checked yourself. Undeclared use of AI counts as plagiarism.',
                '<strong>You are responsible for every line.</strong> "The AI wrote it" is not an explanation at the oral defence.',
                '<strong>Log the errors you find</strong> in <code>AI_ERRORS.md</code>: at least three places where the assistant was wrong (a wrong formula, look-ahead bias, a sign error in VaR, invented data or a reference that does not exist) and how you found out.',
                '<strong>Check every reference.</strong> Each citation needs a working DOI or link. A reference that does not exist is treated as fabricated data.',
                '<strong>What we grade:</strong> the question, the checks, the interpretation and your answers at the defence, not the amount of code.',
                '<strong>No AI during the oral defence.</strong> You answer alone, from your own understanding of the project.'
            ],
            ro: [
                '<strong>AI-ul este permis</strong> pentru cod, depanare, căutarea literaturii și redactare, în proiect și la seminar.',
                '<strong>Utilizarea AI se declară</strong> în <code>AI_USE.md</code>: ce instrument, pentru ce și ce ați verificat voi. Utilizarea nedeclarată a AI este tratată ca plagiat.',
                '<strong>Răspundeți pentru fiecare rând.</strong> „L-a scris AI-ul” nu este o explicație la susținerea orală.',
                '<strong>Notați erorile găsite</strong> în <code>AI_ERRORS.md</code>: cel puțin trei locuri în care asistentul a greșit (o formulă greșită, privire în viitor, semnul VaR, date inventate sau o referință care nu există) și cum v-ați dat seama.',
                '<strong>Verificați fiecare referință.</strong> Fiecare citare are nevoie de un DOI sau link funcțional. O referință care nu există este tratată ca date fabricate.',
                '<strong>Ce notăm:</strong> întrebarea, verificările, interpretarea și răspunsurile de la susținere, nu cantitatea de cod.',
                '<strong>Fără AI la susținerea orală.</strong> Răspundeți singuri, pe baza propriei înțelegeri a proiectului.'
            ]
        },

        projectTemplates: [
            { href: REPO + '/blob/main/project/EN/AI_USE.md', en: 'AI_USE.md: AI use declaration (EN)', ro: 'AI_USE.md: declarația de utilizare AI (EN)', lang: 'en' },
            { href: REPO + '/blob/main/project/EN/AI_ERRORS.md', en: 'AI_ERRORS.md: log of AI errors (EN)', ro: 'AI_ERRORS.md: jurnalul erorilor AI (EN)', lang: 'en' },
            { href: REPO + '/blob/main/project/RO/AI_USE.md', en: 'AI_USE.md: AI use declaration (RO)', ro: 'AI_USE.md: declarația de utilizare AI (RO)', lang: 'ro' },
            { href: REPO + '/blob/main/project/RO/AI_ERRORS.md', en: 'AI_ERRORS.md: log of AI errors (RO)', ro: 'AI_ERRORS.md: jurnalul erorilor AI (RO)', lang: 'ro' }
        ],

        // ---------------------------------------------------------------
        // Resources
        // ---------------------------------------------------------------
        resources: [
            { icon: '&#128187;', href: REPO, en: ['GitHub Repository', 'Slides, notebooks, Quantlets and data'], ro: ['Repository GitHub', 'Slide-uri, notebook-uri, Quantlets și date'] },
            { icon: '&#127891;', img: 'logos/qr_logo.png', href: 'https://quantinar.com', en: ['Quantinar', 'P2P platform with advanced courses'], ro: ['Quantinar', 'Platformă P2P cu cursuri avansate'] },
            { icon: '&#128190;', img: 'logos/ql_logo.png', href: 'https://quantlet.com', en: ['Quantlet', 'Reproducible code for every chart'], ro: ['Quantlet', 'Cod reproductibil pentru fiecare grafic'] },
            { icon: '&#128200;', href: 'https://thecrix.de', en: ['CRIX', 'CRypto IndeX'], ro: ['CRIX', 'Indicele cripto CRIX'] },
            { icon: '&#127963;', img: 'logos/ida_square.png', href: 'https://theida.net', en: ['IDA', 'Institute for Digital Assets'], ro: ['IDA', 'Institute for Digital Assets'] }
        ],

        dataSources: [
            { name: 'yfinance', href: 'https://github.com/ranaroussi/yfinance', en: 'Yahoo Finance prices (Python)', ro: 'Prețuri Yahoo Finance (Python)' },
            { name: 'FRED', href: 'https://fred.stlouisfed.org', en: 'Macro and interest-rate data', ro: 'Date macroeconomice și de dobândă' },
            { name: 'CCXT', href: 'https://github.com/ccxt/ccxt', en: 'Crypto exchange data (order books, trades)', ro: 'Date de pe exchange-uri cripto (order book, tranzacții)' },
            { name: 'BVB', href: 'https://www.bvb.ro', en: 'Bucharest Stock Exchange', ro: 'Bursa de Valori București' }
        ],

        bibliography: [
            'López de Prado, M. (2018). <a href="https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086" target="_blank" rel="noopener"><em>Advances in Financial Machine Learning</em></a>. Wiley.',
            'López de Prado, M. (2020). <a href="https://doi.org/10.1017/9781108883658" target="_blank" rel="noopener"><em>Machine Learning for Asset Managers</em></a>. Cambridge University Press.',
            'Dixon, M. F., Halperin, I., &amp; Bilokon, P. (2020). <a href="https://doi.org/10.1007/978-3-030-41068-1" target="_blank" rel="noopener"><em>Machine Learning in Finance: From Theory to Practice</em></a>. Springer.',
            'Kelly, B., &amp; Xiu, D. (2023). <a href="https://doi.org/10.1561/0500000064" target="_blank" rel="noopener"><em>Financial Machine Learning</em></a>. Foundations and Trends in Finance, 13(3–4), 205–363.',
            'Campbell, J. Y., Lo, A. W., &amp; MacKinlay, A. C. (1997). <a href="https://doi.org/10.1515/9781400830213" target="_blank" rel="noopener"><em>The Econometrics of Financial Markets</em></a>. Princeton University Press.',
            'Brandimarte, P. (2018). <a href="https://doi.org/10.1002/9781119450290" target="_blank" rel="noopener"><em>An Introduction to Financial Markets: A Quantitative Approach</em></a>. Wiley.',
            'Franke, J., Härdle, W. K., &amp; Hafner, C. M. (2019). <a href="https://doi.org/10.1007/978-3-030-13751-9" target="_blank" rel="noopener"><em>Statistics of Financial Markets: An Introduction</em></a> (5th ed.). Springer.',
            'Härdle, W. K., &amp; Simar, L. (2019). <a href="https://doi.org/10.1007/978-3-030-26006-4" target="_blank" rel="noopener"><em>Applied Multivariate Statistical Analysis</em></a> (5th ed.). Springer.',
            'Härdle, W. K., Chen, C. Y.-H., &amp; Overbeck, L. (Eds.) (2017). <a href="https://doi.org/10.1007/978-3-662-54486-0" target="_blank" rel="noopener"><em>Applied Quantitative Finance</em></a> (3rd ed.). Springer.',
            'McNeil, A. J., Frey, R., &amp; Embrechts, P. (2015). <a href="https://press.princeton.edu/books/hardcover/9780691166278/quantitative-risk-management" target="_blank" rel="noopener"><em>Quantitative Risk Management</em></a> (revised ed.). Princeton University Press.',
            'Danielsson, J. (2011). <a href="https://doi.org/10.1002/9781119205869" target="_blank" rel="noopener"><em>Financial Risk Forecasting</em></a>. Wiley.',
            'Bouchaud, J.-P., Bonart, J., Donier, J., &amp; Gould, M. (2018). <a href="https://doi.org/10.1017/9781316659335" target="_blank" rel="noopener"><em>Trades, Quotes and Prices</em></a>. Cambridge University Press.',
            'Gatheral, J. (2006). <a href="https://doi.org/10.1002/9781119202073" target="_blank" rel="noopener"><em>The Volatility Surface: A Practitioner\'s Guide</em></a>. Wiley.',
            'Sornette, D. (2003). <a href="https://doi.org/10.23943/princeton/9780691175959.001.0001" target="_blank" rel="noopener"><em>Why Stock Markets Crash</em></a>. Princeton University Press.',
            'Francq, C., &amp; Zakoïan, J.-M. (2019). <a href="https://doi.org/10.1002/9781119313472" target="_blank" rel="noopener"><em>GARCH Models: Structure, Statistical Inference and Financial Applications</em></a> (2nd ed.). Wiley.',
            'Tsay, R. S. (2010). <a href="https://doi.org/10.1002/9780470644560" target="_blank" rel="noopener"><em>Analysis of Financial Time Series</em></a> (3rd ed.). Wiley.',
            'Fissler, T., &amp; Ziegel, J. F. (2016). <a href="https://doi.org/10.1214/16-AOS1439" target="_blank" rel="noopener">Higher order elicitability and Osband&#39;s principle</a>. <em>Annals of Statistics</em>, 44(4), 1680–1707.',
            'Ansari, A. F., et al. (2024). <a href="https://arxiv.org/abs/2403.07815" target="_blank" rel="noopener">Chronos: Learning the Language of Time Series</a>. <em>Transactions on Machine Learning Research</em>.',
            'Das, A., Kong, W., Sen, R., &amp; Zhou, Y. (2024). <a href="https://proceedings.mlr.press/v235/das24c.html" target="_blank" rel="noopener">A decoder-only foundation model for time-series forecasting</a>. <em>ICML</em>.',
            'Pele, D. T., Wesselhöfft, N., Härdle, W. K., Kolossiatis, M., &amp; Yatracos, Y. G. (2023). <a href="https://doi.org/10.1080/1351847X.2021.1960403" target="_blank" rel="noopener">Are cryptos becoming alternative assets?</a> <em>The European Journal of Finance</em>, 29(10), 1064–1105.',
            'Pele, D. T. (2013). <a href="https://www.researchgate.net/profile/Daniel-Traian-Pele/publication/338409433_Criza_pietelor_de_capital_-_dezastru_predictibil_sau_lebada_neagra/links/5e133c9c4585159aa4b4e155/Criza-pietelor-de-capital-dezastru-predictibil-sau-lebada-neagra.pdf" target="_blank" rel="noopener"><em>Criza piețelor de capital – dezastru predictibil sau lebădă neagră?</em></a> Editura ASE.'
        ],

        contact: {
            name: 'Prof. dr. Daniel Traian Pele',
            email: 'danpele@ase.ro',
            en: ['Bucharest University of Economic Studies', 'Department of Statistics and Econometrics', 'Faculty of Cybernetics, Statistics and Economic Informatics'],
            ro: ['Academia de Studii Economice din București', 'Departamentul de Statistică și Econometrie', 'Facultatea de Cibernetică, Statistică și Informatică Economică'],
            seminar: { name: 'Drd. Antoaneta Amza', email: 'antoaneta.amza@csie.ase.ro' }
        },

        footerLogos: [
            ['https://www.ase.ro', 'logos/ase_logo.png', 'ASE'],
            ['https://www.theida.net/', 'logos/ida_logo.png', 'IDA'],
            ['https://quantinar.com', 'logos/qr_logo.png', 'Quantinar'],
            ['https://quantlet.com', 'logos/ql_logo.png', 'Quantlet'],
            ['https://ai4efin.ase.ro', 'logos/ai4efin_logo.png', 'AI4EFin'],
            ['https://www.digital-finance-msca.com/', 'logos/msca_logo.png', 'MSCA Digital Finance'],
            ['https://blockchain-research-center.com/', 'logos/brc_logo.png', 'Blockchain Research Center'],
            ['https://ipe.ro/new/', 'logos/acad_logo.png', 'Romanian Academy']
        ],

        // Quiz banks register themselves here by chapter id (see assets/quizzes/<id>.js)
        quizzes: {}
    };
})();

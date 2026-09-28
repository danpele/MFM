// ============================================================
// Quiz bank for chapter id 'llm': LLMs and Sentiment Analysis (EN + RO)
// correct = index (0-3) of the right option in the original order.
// incorrectExplanation must not name a letter: the engine prepends
// "The correct answer is X) ..." after shuffling the options.
// ============================================================
window.MFM_DATA.quizzes['llm'] = {
    "draw": 20,
    "questions": [
        {
            "correct": 0,
            "en": {
                "title": "Attenuation from misclassification",
                "text": "You regress next-day returns on a dummy equal to 1 when FinBERT labels a headline negative. On Twitter, FinBERT misses 23.9% of the truly negative headlines and calls 13.3% of the others negative (14.5% of headlines are negative). What happens to the slope?",
                "options": [
                    "It is attenuated: its probability limit is about 0.45 times the true effect, so the true effect is about 2.2 times larger in absolute value",
                    "It is unbiased but less precise, because the classification errors average out",
                    "It is biased away from zero, because false negatives exaggerate the contrast",
                    "It is unaffected, because misclassification only changes the intercept"
                ],
                "correctExplanation": "With a misclassified binary regressor (Aigner, 1973), plim b = β·π(1 − π)(1 − α0 − α1)/[p(1 − p)] = β·0.449 here. The sign is kept as long as α0 + α1 < 1, but the magnitude shrinks.",
                "incorrectExplanation": "Measurement error in the regressor is a bias, not only a loss of precision: the covariance between the dummy and the true tone is π(1 − π)(1 − α0 − α1), smaller than the variance of the dummy, so the slope shrinks towards zero."
            },
            "ro": {
                "title": "Atenuarea prin clasificare greșită",
                "text": "Regresați randamentele zilei următoare pe o variabilă egală cu 1 când FinBERT etichetează un titlu drept negativ. Pe Twitter, FinBERT ratează 23,9% din titlurile cu adevărat negative și numește negative 13,3% dintre celelalte (14,5% dintre titluri sunt negative). Ce se întâmplă cu panta?",
                "options": [
                    "Este atenuată: limita ei în probabilitate este de circa 0,45 ori efectul adevărat, deci efectul adevărat este de circa 2,2 ori mai mare în valoare absolută",
                    "Este nedistorsionată, dar mai puțin precisă, pentru că erorile de clasificare se compensează",
                    "Este distorsionată departe de zero, pentru că falsele negative exagerează contrastul",
                    "Nu este afectată, pentru că clasificarea greșită schimbă doar termenul liber"
                ],
                "correctExplanation": "Cu un regresor binar clasificat greșit (Aigner, 1973), plim b = β·π(1 − π)(1 − α0 − α1)/[p(1 − p)] = β·0,449 aici. Semnul se păstrează cât timp α0 + α1 < 1, dar mărimea scade.",
                "incorrectExplanation": "Eroarea de măsurare din regresor este o distorsiune, nu doar o pierdere de precizie: covarianța dintre variabila binară și tonul adevărat este π(1 − π)(1 − α0 − α1), mai mică decât varianța variabilei, deci panta se apropie de zero."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Generic versus financial dictionary",
                "text": "In the lists used in the lecture, 1 552 of the 2 007 negative words of the Harvard General Inquirer (GI) are not negative in the Loughran-McDonald (LM) list. What does this imply?",
                "options": [
                    "GI is more accurate than LM on financial news because it has more negative words",
                    "Many GI negative words, such as \"service\", \"capital\" or \"board\", are ordinary business words, so GI misreads financial text",
                    "LM misses most negative financial words and should be replaced by GI",
                    "The two dictionaries give the same tone on financial text, since both are word lists"
                ],
                "correctExplanation": "About 77% of the GI negative words are not negative for LM. In Financial PhraseBank, sentences containing \"service\", \"capital\" or \"board\" are almost never labelled negative: finance has its own vocabulary.",
                "incorrectExplanation": "The overlap is small: GI, a psychology dictionary from the 1960s, flags business nouns as negative, which is why it loses even to the majority class on both labelled data sets."
            },
            "ro": {
                "title": "Dicționar generic versus financiar",
                "text": "În listele folosite în curs, 1 552 dintre cele 2 007 cuvinte negative din Harvard General Inquirer (GI) nu sunt negative în lista Loughran-McDonald (LM). Ce implică acest lucru?",
                "options": [
                    "GI este mai precis decât LM pe știri financiare, deoarece are mai multe cuvinte negative",
                    "Multe cuvinte negative din GI, precum „service”, „capital” sau „board”, sunt cuvinte obișnuite de afaceri, deci GI citește greșit textele financiare",
                    "LM ratează majoritatea cuvintelor financiare negative și ar trebui înlocuit cu GI",
                    "Cele două dicționare dau același ton pe texte financiare, fiind amândouă liste de cuvinte"
                ],
                "correctExplanation": "Circa 77% dintre cuvintele negative din GI nu sunt negative pentru LM. În Financial PhraseBank, propozițiile cu „service”, „capital” sau „board” nu sunt aproape niciodată etichetate negativ: finanțele au propriul vocabular.",
                "incorrectExplanation": "Suprapunerea este mică: GI, un dicționar de psihologie din anii 1960, marchează substantive de afaceri drept negative; de aceea pierde chiar și în fața clasei majoritare pe ambele seturi etichetate."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "The limit of any word list",
                "text": "Only 26% of the Financial PhraseBank sentences containing \"lower\" are labelled non-negative, yet \"lower costs\" is good news. What does this show about the Loughran-McDonald (LM) dictionary?",
                "options": [
                    "LM should drop \"lower\" from its negative list, which would solve the problem",
                    "The annotators of Financial PhraseBank made mistakes on sentences with \"lower\"",
                    "LM fixes the financial vocabulary but not the context: the sign of a word can depend on the next word",
                    "A longer list of positive words would allow LM to read negation and context"
                ],
                "correctExplanation": "A bag of words ignores word order. \"Lower sales\" is bad news and \"lower costs\" is good news: no fixed sign per word can capture both, which is why models that read words in context help.",
                "incorrectExplanation": "Changing the list does not help: the same word is negative in one phrase and positive in another. The problem is context, which a word count cannot see."
            },
            "ro": {
                "title": "Limita oricărei liste de cuvinte",
                "text": "Doar 26% dintre propozițiile din Financial PhraseBank care conțin „lower” nu sunt etichetate negativ, totuși „lower costs” este o veste bună. Ce arată acest lucru despre dicționarul Loughran-McDonald (LM)?",
                "options": [
                    "LM ar trebui să elimine „lower” din lista negativă, iar problema ar fi rezolvată",
                    "Adnotatorii din Financial PhraseBank au greșit la propozițiile cu „lower”",
                    "LM corectează vocabularul financiar, dar nu contextul: semnul unui cuvânt poate depinde de cuvântul următor",
                    "O listă mai lungă de cuvinte pozitive i-ar permite lui LM să citească negația și contextul"
                ],
                "correctExplanation": "Modelul bag of words ignoră ordinea cuvintelor. „Lower sales” este o veste proastă, iar „lower costs” una bună: niciun semn fix pe cuvânt nu le poate surprinde pe amândouă; de aceea ajută modelele care citesc cuvintele în context.",
                "incorrectExplanation": "Modificarea listei nu ajută: același cuvânt este negativ într-o expresie și pozitiv în alta. Problema este contextul, pe care o numărare de cuvinte nu îl vede."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Prediction-powered inference",
                "text": "You have 100 000 headlines scored by an LLM and a random subset of 500 also labelled by humans. Which estimator of the mean true sentiment gives valid confidence intervals whatever the accuracy of the LLM, and uses all the scores?",
                "options": [
                    "The mean of the LLM scores over the 100 000 headlines, with its usual standard error",
                    "The mean of the human labels on the 500 headlines only",
                    "The simple average of the LLM mean and the human-label mean",
                    "The LLM mean over all headlines minus the mean LLM error (score minus label) estimated on the 500 labelled headlines"
                ],
                "correctExplanation": "Prediction-powered inference (Angelopoulos et al., 2023) corrects the model mean with a rectifier estimated on the labelled subset; its variance is Var(f)/N + Var(f − Y)/n. On Twitter the plain FinBERT mean even has the wrong sign (−0.014 against a true 0.054).",
                "incorrectExplanation": "The plain LLM mean converges to the wrong number when the model is biased; the labels-only mean is valid but ignores the scores; an ad hoc average has no valid variance. The bias-corrected estimator combines both."
            },
            "ro": {
                "title": "Prediction-powered inference",
                "text": "Aveți 100 000 de titluri notate de un LLM și o submulțime aleatoare de 500 etichetate și de oameni. Ce estimator al sentimentului mediu adevărat dă intervale de încredere valide oricare ar fi acuratețea LLM-ului și folosește toate scorurile?",
                "options": [
                    "Media scorurilor LLM pe cele 100 000 de titluri, cu eroarea ei standard obișnuită",
                    "Media etichetelor umane doar pe cele 500 de titluri",
                    "Media simplă dintre media LLM și media etichetelor umane",
                    "Media LLM pe toate titlurile minus eroarea medie a LLM (scor minus etichetă) estimată pe cele 500 de titluri etichetate"
                ],
                "correctExplanation": "Prediction-powered inference (Angelopoulos et al., 2023) corectează media modelului cu o corecție estimată pe submulțimea etichetată; varianța este Var(f)/N + Var(f − Y)/n. Pe Twitter, media simplă FinBERT are chiar semnul greșit (−0,014 față de 0,054 adevărat).",
                "incorrectExplanation": "Media simplă a LLM converge la un număr greșit când modelul este distorsionat; media doar a etichetelor este validă, dar ignoră scorurile; o medie ad hoc nu are o varianță validă. Estimatorul corectat le combină pe amândouă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Two scores as instruments",
                "text": "The daily FinBERT and Qwen2.5-7B scores correlate 0.66. Instrumenting Qwen with FinBERT gives a same-day slope of 59 bp; instrumenting Qwen with the LM dictionary gives 37 bp (difference z = 5.4). What do you conclude?",
                "options": [
                    "At least one instrument is invalid: the two LLM scores share measurement errors, so FinBERT is not independent of Qwen's error",
                    "Instrumental variables always fail with correlations below 0.9",
                    "Both estimates are valid; the difference is sampling noise",
                    "The LM dictionary must be the better instrument because it is less correlated with Qwen"
                ],
                "correctExplanation": "IV with a second noisy measurement is consistent only if the two measurement errors are independent of each other and of the return shock. Two valid instruments would give the same estimate; a 22 bp gap with z = 5.4 rejects that, as expected for models trained on overlapping text.",
                "incorrectExplanation": "The strength of the correlation is not the issue; validity is. Two valid instruments must estimate the same coefficient, and the observed gap is far beyond sampling noise."
            },
            "ro": {
                "title": "Două scoruri ca instrumente",
                "text": "Scorurile zilnice FinBERT și Qwen2.5-7B au corelația 0,66. Instrumentând Qwen cu FinBERT se obține o pantă în aceeași zi de 59 bp; instrumentând Qwen cu dicționarul LM, 37 bp (diferența z = 5,4). Ce concluzionați?",
                "options": [
                    "Cel puțin un instrument nu este valid: cele două scoruri LLM au erori de măsurare comune, deci FinBERT nu este independent de eroarea lui Qwen",
                    "Variabilele instrumentale eșuează mereu la corelații sub 0,9",
                    "Ambele estimări sunt valide; diferența este zgomot de eșantionare",
                    "Dicționarul LM trebuie să fie instrumentul mai bun pentru că este mai puțin corelat cu Qwen"
                ],
                "correctExplanation": "IV cu o a doua măsurătoare zgomotoasă este consistentă doar dacă cele două erori de măsurare sunt independente între ele și de șocul randamentului. Două instrumente valide ar da aceeași estimare; o diferență de 22 bp cu z = 5,4 respinge acest lucru, cum era de așteptat pentru modele antrenate pe texte care se suprapun.",
                "incorrectExplanation": "Problema nu este mărimea corelației, ci validitatea. Două instrumente valide trebuie să estimeze același coeficient, iar diferența observată depășește cu mult zgomotul de eșantionare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Best classifier on Twitter",
                "text": "On Twitter Financial News, GI scores 43.6%, LM 60.5%, FinBERT 72.5%, Qwen2.5-7B zero-shot 74.2% and TF-IDF (Term Frequency - Inverse Document Frequency) + logistic regression trained on the Twitter training set 83.2%. What is the lesson?",
                "options": [
                    "Larger models are always more accurate than smaller ones",
                    "Labelled data from the target domain beat model size",
                    "Dictionaries are the most reliable method for short headlines",
                    "TF-IDF wins only because it memorised the validation headlines"
                ],
                "correctExplanation": "The simplest supervised model, trained on in-domain labels, beats both FinBERT and a 7-billion-parameter large language model (LLM) that saw no Twitter labels.",
                "incorrectExplanation": "The ranking is not by size: a word-count logistic regression trained on the target data leads. The validation headlines are separate from its training set."
            },
            "ro": {
                "title": "Cel mai bun clasificator pe Twitter",
                "text": "Pe Twitter Financial News, GI obține 43,6%, LM 60,5%, FinBERT 72,5%, Qwen2.5-7B zero-shot 74,2%, iar TF-IDF (Term Frequency - Inverse Document Frequency) + regresie logistică antrenată pe setul de antrenare Twitter 83,2%. Care este lecția?",
                "options": [
                    "Modelele mai mari sunt întotdeauna mai precise decât cele mici",
                    "Datele etichetate din domeniul-țintă contează mai mult decât mărimea modelului",
                    "Dicționarele sunt metoda cea mai sigură pentru titluri scurte",
                    "TF-IDF câștigă doar pentru că a memorat titlurile de validare"
                ],
                "correctExplanation": "Cel mai simplu model supervizat, antrenat pe etichete din domeniu, depășește atât FinBERT, cât și un model mare de limbaj (LLM) cu 7 miliarde de parametri care nu a văzut etichete Twitter.",
                "incorrectExplanation": "Clasamentul nu urmează mărimea: o regresie logistică pe frecvențe de cuvinte, antrenată pe datele-țintă, conduce. Titlurile de validare sunt separate de setul ei de antrenare."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Annotator agreement",
                "text": "On Financial PhraseBank, FinBERT reaches 97% accuracy on sentences where all 16 annotators agree, but 70% where only half agree (Qwen2.5-14B: 94% and 55%). How should this be read?",
                "options": [
                    "FinBERT is broken on long sentences",
                    "The annotators with finance background are less reliable than the models",
                    "Many sentences are genuinely ambiguous: when experts split, the label itself sets a ceiling on accuracy",
                    "The low-agreement sentences are all neutral, so accuracy there does not matter"
                ],
                "correctExplanation": "A model cannot be judged on a label humans do not agree on. For signals, a strong, unambiguous tone is more informative than a borderline one.",
                "incorrectExplanation": "The drop follows the annotators, not the model: where experts disagree, there is no clear correct answer, so every model falls."
            },
            "ro": {
                "title": "Acordul adnotatorilor",
                "text": "Pe Financial PhraseBank, FinBERT atinge 97% acuratețe pe propozițiile unde toți cei 16 adnotatori sunt de acord, dar 70% unde doar jumătate sunt de acord (Qwen2.5-14B: 94% și 55%). Cum trebuie interpretat acest lucru?",
                "options": [
                    "FinBERT nu funcționează pe propoziții lungi",
                    "Adnotatorii cu pregătire financiară sunt mai puțin fiabili decât modelele",
                    "Multe propoziții sunt cu adevărat ambigue: când experții se împart, eticheta însăși pune un plafon acurateței",
                    "Propozițiile cu acord scăzut sunt toate neutre, deci acuratețea acolo nu contează"
                ],
                "correctExplanation": "Un model nu poate fi judecat pe o etichetă asupra căreia oamenii nu cad de acord. Pentru semnale, un ton puternic și neambiguu este mai informativ decât unul la limită.",
                "incorrectExplanation": "Scăderea urmează adnotatorii, nu modelul: unde experții nu sunt de acord nu există un răspuns corect clar, deci toate modelele scad."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "The in-sample trap",
                "text": "The public FinBERT model scores 89.0% on Financial PhraseBank and 72.5% on Twitter Financial News; Qwen2.5-7B, never trained on these labels, scores 81.4% and 74.2%. What explains FinBERT's larger drop?",
                "options": [
                    "Twitter headlines are written in a language FinBERT does not know",
                    "Qwen2.5-7B was fine-tuned on Twitter Financial News",
                    "FinBERT has more parameters than Qwen2.5-7B and overfits short texts",
                    "FinBERT was fine-tuned on Financial PhraseBank, so part of its lead there is memory of its own training data"
                ],
                "correctExplanation": "Qwen2.5-7B also drops, by 7.2 points, because Twitter headlines are harder; the difference in differences, 9.2 points (bootstrap CI [6.7; 11.9]), measures FinBERT's memory of its own training data. Evaluate a language model only on texts it has never seen.",
                "incorrectExplanation": "The public FinBERT (ProsusAI/finbert) was fine-tuned on Financial PhraseBank itself; its score there is in-sample, not a fair comparison."
            },
            "ro": {
                "title": "Capcana evaluării în eșantion",
                "text": "Modelul public FinBERT obține 89,0% pe Financial PhraseBank și 72,5% pe Twitter Financial News; Qwen2.5-7B, neantrenat pe aceste etichete, obține 81,4% și 74,2%. Ce explică scăderea mai mare a lui FinBERT?",
                "options": [
                    "Titlurile de pe Twitter sunt scrise într-o limbă pe care FinBERT nu o cunoaște",
                    "Qwen2.5-7B a fost ajustat fin pe Twitter Financial News",
                    "FinBERT are mai mulți parametri decât Qwen2.5-7B și supraajustează textele scurte",
                    "FinBERT a fost ajustat fin pe Financial PhraseBank, deci o parte din avantajul său acolo este memoria propriilor date de antrenare"
                ],
                "correctExplanation": "Și Qwen2.5-7B scade, cu 7,2 puncte, pentru că titlurile Twitter sunt mai grele; diferența diferențelor, 9,2 puncte (CI bootstrap [6,7; 11,9]), măsoară memoria FinBERT a propriilor date de antrenare. Evaluați un model de limbaj doar pe texte pe care nu le-a văzut niciodată.",
                "incorrectExplanation": "FinBERT-ul public (ProsusAI/finbert) a fost ajustat fin chiar pe Financial PhraseBank; scorul lui acolo este în eșantion, deci comparația nu este corectă."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Reading the confusion matrix",
                "text": "On Twitter, Qwen2.5-7B classifies 414 of 475 positive headlines correctly, but also labels 325 of 1 566 neutral headlines as positive. What does this mean for a trading signal?",
                "options": [
                    "High recall but low precision on the extreme classes: many false signals, which cost money in trading",
                    "High precision and low recall: the model misses most positive news",
                    "The model is perfectly calibrated, since it finds almost all positive headlines",
                    "The errors are irrelevant, because only accuracy matters for trading"
                ],
                "correctExplanation": "The large language model \"sees\" sentiment where annotators saw plain facts. Precision on the positive class is 414/(414 + 325 + 12) ≈ 55%, so almost half of its buy signals are false.",
                "incorrectExplanation": "Finding almost all positive headlines is high recall; labelling many neutral headlines as positive lowers precision, and false positives trigger costly trades."
            },
            "ro": {
                "title": "Citirea matricei de confuzie",
                "text": "Pe Twitter, Qwen2.5-7B clasifică corect 414 din 475 de titluri pozitive, dar etichetează drept pozitive și 325 din 1 566 de titluri neutre. Ce înseamnă acest lucru pentru un semnal de tranzacționare?",
                "options": [
                    "Recall mare, dar precizie mică pe clasele extreme: multe semnale false, care costă bani în tranzacționare",
                    "Precizie mare și recall mic: modelul ratează majoritatea știrilor pozitive",
                    "Modelul este perfect calibrat, deoarece găsește aproape toate titlurile pozitive",
                    "Erorile nu contează, pentru că în tranzacționare contează doar acuratețea"
                ],
                "correctExplanation": "Modelul mare de limbaj „vede” sentiment acolo unde adnotatorii au văzut fapte simple. Precizia pe clasa pozitivă este 414/(414 + 325 + 12) ≈ 55%, deci aproape jumătate din semnalele de cumpărare sunt false.",
                "incorrectExplanation": "A găsi aproape toate titlurile pozitive înseamnă recall mare; a eticheta multe titluri neutre drept pozitive scade precizia, iar fals-pozitivele declanșează tranzacții costisitoare."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Few clusters",
                "text": "The FNSPID panel has 16 stocks. Clustering by stock, the Qwen2.5-7B slope at d + 2 has t = 2.41. What is the right reading?",
                "options": [
                    "It is significant at 1%, because t > 1.96 with 18 282 observations",
                    "With 16 clusters the clustered SE is biased down and t is not N(0, 1): the wild cluster bootstrap gives p = 0.061, and 0.37 after Holm over the nine regressions",
                    "Clustering by stock is always conservative, so the true p-value is even smaller",
                    "Clustering is only needed when the regressor is a dummy"
                ],
                "correctExplanation": "Inference rests on 16 cluster sums, not on 18 282 observations: use t15 critical values or a wild cluster bootstrap with the null imposed (Cameron, Gelbach & Miller, 2008), and count all the regressions tried.",
                "incorrectExplanation": "The number of independent units is the number of clusters. With 16 clusters the sandwich estimator underestimates the variance, and the normal approximation overstates significance."
            },
            "ro": {
                "title": "Puține grupuri",
                "text": "Panelul FNSPID are 16 acțiuni. Cu gruparea pe acțiuni, panta Qwen2.5-7B în d + 2 are t = 2,41. Care este interpretarea corectă?",
                "options": [
                    "Este semnificativă la 1%, pentru că t > 1,96 cu 18 282 de observații",
                    "Cu 16 grupuri SE grupată este subestimată și t nu este N(0, 1): wild cluster bootstrap dă p = 0,061, iar 0,37 după Holm pe cele nouă regresii",
                    "Gruparea pe acțiuni este mereu conservatoare, deci valoarea p adevărată este și mai mică",
                    "Gruparea este necesară doar când regresorul este o variabilă binară"
                ],
                "correctExplanation": "Inferența se sprijină pe 16 sume pe grupuri, nu pe 18 282 de observații: folosiți valori critice t15 sau un wild cluster bootstrap cu ipoteza nulă impusă (Cameron, Gelbach & Miller, 2008) și numărați toate regresiile încercate.",
                "incorrectExplanation": "Numărul unităților independente este numărul de grupuri. Cu 16 grupuri, estimatorul sandwich subestimează varianța, iar aproximarea normală exagerează semnificația."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Model size and accuracy",
                "text": "For zero-shot Qwen2.5 on Twitter Financial News, macro-F1 is 55.3% for 1.5B, 72.6% for 7B and lower again for 14B (B: billion parameters); FinBERT has 66.8%. What is the right conclusion?",
                "options": [
                    "Bigger models are always better, so the 14B model should be used",
                    "Size does not matter at all for zero-shot sentiment",
                    "Size helps on average but not monotonically; small models react strongly to the wording of the prompt",
                    "The 1.5B model is best, since it answers \"neutral\" least often"
                ],
                "correctExplanation": "On PhraseBank macro-F1 rises from 63.3% (0.5B) to 82.1% (14B), but on Twitter the curve is not monotone: the 1.5B model rarely answers \"neutral\" with this prompt and ends up worst.",
                "incorrectExplanation": "The results do not rise steadily with size: 7B beats 14B on Twitter, and the 1.5B model is the weakest because it rarely answers \"neutral\"."
            },
            "ro": {
                "title": "Mărimea modelului și acuratețea",
                "text": "Pentru Qwen2.5 zero-shot pe Twitter Financial News, F1 macro este 55,3% pentru 1.5B, 72,6% pentru 7B și din nou mai mic pentru 14B (B: miliarde de parametri); FinBERT are 66,8%. Care este concluzia corectă?",
                "options": [
                    "Modelele mai mari sunt întotdeauna mai bune, deci trebuie folosit modelul 14B",
                    "Mărimea nu contează deloc pentru sentimentul zero-shot",
                    "Mărimea ajută în medie, dar nu monoton; modelele mici reacționează puternic la formularea prompt-ului",
                    "Modelul 1.5B este cel mai bun, deoarece răspunde cel mai rar „neutral”"
                ],
                "correctExplanation": "Pe PhraseBank, F1 macro crește de la 63,3% (0.5B) la 82,1% (14B), dar pe Twitter curba nu este monotonă: modelul 1.5B răspunde rar „neutral” cu acest prompt și iese cel mai slab.",
                "incorrectExplanation": "Rezultatele nu cresc constant cu mărimea: 7B depășește 14B pe Twitter, iar modelul 1.5B este cel mai slab pentru că răspunde rar „neutral”."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "The prompt is a parameter",
                "text": "With three prompts that ask the same question, Qwen2.5-7B reaches between 73.7% and 77.8% accuracy on Twitter, and the three prompts give the same label on only 67% of headlines. A researcher reports the best prompt. What is wrong?",
                "options": [
                    "Nothing: the best prompt is the right one to report",
                    "The researcher should average the three accuracies and report that as a significance test",
                    "The prompt matters only for small models, so there is no issue with a 7B model",
                    "Choosing the prompt after seeing test results is data snooping; it must be fixed in advance or chosen on a separate validation set"
                ],
                "correctExplanation": "The prompt is a tuning parameter like any other. Picking it on the test set inflates the reported accuracy, the same data snooping discussed in Chapter 13.",
                "incorrectExplanation": "Reporting the best of several prompts on the test set overstates performance; the prompt must be fixed before the test or selected on validation data."
            },
            "ro": {
                "title": "Prompt-ul este un parametru",
                "text": "Cu trei prompt-uri care pun aceeași întrebare, Qwen2.5-7B obține între 73,7% și 77,8% acuratețe pe Twitter, iar cele trei prompt-uri dau aceeași etichetă doar pentru 67% dintre titluri. Un cercetător raportează cel mai bun prompt. Ce este greșit?",
                "options": [
                    "Nimic: cel mai bun prompt este cel corect de raportat",
                    "Cercetătorul ar trebui să facă media celor trei acurateți și să o raporteze drept test de semnificație",
                    "Prompt-ul contează doar la modelele mici, deci la un model 7B nu este nicio problemă",
                    "Alegerea prompt-ului după ce ați văzut rezultatele pe test este data snooping; prompt-ul trebuie fixat dinainte sau ales pe un set de validare separat"
                ],
                "correctExplanation": "Prompt-ul este un parametru de ajustare ca oricare altul. Alegerea lui pe setul de test umflă acuratețea raportată: același data snooping discutat în Capitolul 13.",
                "incorrectExplanation": "Raportarea celui mai bun dintre mai multe prompt-uri pe setul de test supraestimează performanța; prompt-ul trebuie fixat înainte de test sau selectat pe date de validare."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "LLM versus FinBERT",
                "text": "On Twitter, Qwen2.5-7B scores 74.2% and FinBERT 72.5%: n01 = 395, n10 = 355, McNemar p = 0.154, difference +1.7 points with 95% CI [−0.5; +3.8]. What do you conclude?",
                "options": [
                    "No significant difference: a model with 70 to 130 times more parameters is not more accurate on these headlines",
                    "Qwen2.5-7B is significantly better, since its accuracy is higher",
                    "FinBERT is significantly better, since the CI includes negative values",
                    "The test is invalid, because the two models use different architectures"
                ],
                "correctExplanation": "The paired test and the interval both include no difference. Where large language models help is elsewhere: no labels, other languages, longer documents.",
                "incorrectExplanation": "A p-value of 0.154 and a confidence interval that contains 0 mean the gap of 1.7 points could be noise; neither model is shown to be better."
            },
            "ro": {
                "title": "LLM versus FinBERT",
                "text": "Pe Twitter, Qwen2.5-7B obține 74,2%, iar FinBERT 72,5%: n01 = 395, n10 = 355, McNemar p = 0,154, diferența +1,7 puncte cu CI 95% [−0,5; +3,8]. Ce concluzionați?",
                "options": [
                    "Nicio diferență semnificativă: un model cu de 70 până la 130 de ori mai mulți parametri nu este mai precis pe aceste titluri",
                    "Qwen2.5-7B este semnificativ mai bun, deoarece are acuratețea mai mare",
                    "FinBERT este semnificativ mai bun, deoarece CI include valori negative",
                    "Testul nu este valid, deoarece cele două modele au arhitecturi diferite"
                ],
                "correctExplanation": "Atât testul pe perechi, cât și intervalul sunt compatibile cu diferența zero. Modelele mari de limbaj ajută în altă parte: fără etichete, alte limbi, documente mai lungi.",
                "incorrectExplanation": "O valoare p de 0,154 și un interval de încredere care conține 0 arată că diferența de 1,7 puncte poate fi zgomot; niciun model nu se dovedește mai bun."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Did the memory vanish?",
                "text": "For the monthly S&P 500 direction, Qwen2.5-14B has AUC 0.69 on 296 months before its release and 0.59 on 23 months after. A DeLong test of the difference gives z = 0.73. What can you conclude?",
                "options": [
                    "The memory has vanished after the release, since 0.59 < 0.69",
                    "Nothing about the memory: with 23 months the smallest drop detectable with 80% power is about 0.36, so a fall to 0.5 could not be detected",
                    "The model remembers the post-release months as well, since 0.59 > 0.5",
                    "AUC cannot be computed for months, so the test is invalid"
                ],
                "correctExplanation": "The post-release standard error of the AUC is about 0.12, so the test has little power; about 100 post-release months would be needed. Not rejecting equality is not evidence that the memory is gone.",
                "incorrectExplanation": "Point estimates cannot be compared without their sampling error. The formal test does not reject, and its power against a fall to 0.5 is low: absence of evidence is not evidence of absence."
            },
            "ro": {
                "title": "A dispărut memoria?",
                "text": "Pentru direcția lunară a S&P 500, Qwen2.5-14B are AUC 0,69 pe 296 de luni dinainte de publicare și 0,59 pe 23 de luni după. Testul DeLong al diferenței dă z = 0,73. Ce puteți concluziona?",
                "options": [
                    "Memoria a dispărut după publicare, pentru că 0,59 < 0,69",
                    "Nimic despre memorie: cu 23 de luni, cea mai mică scădere detectabilă cu puterea 80% este de circa 0,36, deci o cădere la 0,5 nu ar putea fi detectată",
                    "Modelul își amintește și lunile de după publicare, pentru că 0,59 > 0,5",
                    "AUC nu poate fi calculat pentru luni, deci testul nu este valid"
                ],
                "correctExplanation": "Eroarea standard a AUC după publicare este de circa 0,12, deci testul are putere mică; ar fi nevoie de circa 100 de luni după publicare. Nerespingerea egalității nu dovedește că memoria a dispărut.",
                "incorrectExplanation": "Estimările punctuale nu se pot compara fără eroarea lor de eșantionare. Testul formal nu respinge, iar puterea lui față de o cădere la 0,5 este mică: lipsa dovezilor nu este o dovadă a absenței."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "How many labels?",
                "text": "In the learning curve on Twitter Financial News, which statement matches the lecture?",
                "options": [
                    "FinBERT beats every supervised model at any number of labels",
                    "Embeddings need the full training set of 9 543 labels to beat FinBERT",
                    "Embeddings + logistic regression beat FinBERT from about 400 labels; with all 9 543 labels TF-IDF reaches 83.1%, above the embeddings (78.6%)",
                    "TF-IDF is best with 100 labels, but embeddings overtake it with many labels"
                ],
                "correctExplanation": "Pretrained vectors already contain most of what is needed, so a few hundred in-domain labels suffice; with many labels, exact words such as \"upgrade\", \"cuts\" or \"misses\" carry the signal and TF-IDF wins.",
                "incorrectExplanation": "Embeddings start high (69.0% with 100 labels) and pass FinBERT from about 400 labels; TF-IDF starts lower (66.9%) but keeps improving to 83.1%."
            },
            "ro": {
                "title": "Câte etichete sunt necesare?",
                "text": "În curba de învățare pe Twitter Financial News, care afirmație corespunde cursului?",
                "options": [
                    "FinBERT depășește orice model supervizat, oricâte etichete ar exista",
                    "Embedding-urile au nevoie de întregul set de 9 543 de etichete pentru a depăși FinBERT",
                    "Embedding-urile + regresia logistică depășesc FinBERT de la circa 400 de etichete; cu toate cele 9 543 de etichete, TF-IDF ajunge la 83,1%, peste embedding-uri (78,6%)",
                    "TF-IDF este cel mai bun cu 100 de etichete, dar embedding-urile îl depășesc când există multe etichete"
                ],
                "correctExplanation": "Vectorii preantrenați conțin deja aproape tot ce trebuie, deci câteva sute de etichete din domeniu sunt suficiente; cu multe etichete, cuvintele exacte precum „upgrade”, „cuts” sau „misses” poartă semnalul, iar TF-IDF câștigă.",
                "incorrectExplanation": "Embedding-urile pornesc sus (69,0% cu 100 de etichete) și trec de FinBERT de la circa 400 de etichete; TF-IDF pornește mai jos (66,9%), dar crește până la 83,1%."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "What the LLM remembers",
                "text": "Asked without context whether the S&P 500 rose or fell in a given month, Qwen2.5-14B reaches an AUC (Area Under the ROC Curve) of 0.69 on months before its release; asked about single days of Apple stock, its AUC is between 0.48 and 0.52. What is the conclusion?",
                "options": [
                    "The model predicts future months well, so it is a good forecaster",
                    "Both results are consistent with no knowledge at all",
                    "The model remembers single days better than months",
                    "It partly remembers the monthly direction (regimes, famous months) but not daily moves: look-ahead is a danger at the horizon of well-known events"
                ],
                "correctExplanation": "An AUC of 0.5 means no knowledge. Monthly AUC well above 0.5 before release is memory of market history (e.g. October 2008, March 2020); daily noise is not remembered.",
                "incorrectExplanation": "These are past months the model read about in training, not forecasts; 0.69 for months against about 0.5 for days means coarse memory of regimes and famous episodes only."
            },
            "ro": {
                "title": "Ce își amintește LLM-ul",
                "text": "Întrebat fără context dacă S&P 500 a crescut sau a scăzut într-o anumită lună, Qwen2.5-14B atinge un AUC (Area Under the ROC Curve) de 0,69 pe lunile dinaintea publicării sale; întrebat despre zile individuale ale acțiunii Apple, AUC-ul este între 0,48 și 0,52. Care este concluzia?",
                "options": [
                    "Modelul prognozează bine lunile viitoare, deci este un bun instrument de prognoză",
                    "Ambele rezultate sunt compatibile cu lipsa oricărei cunoașteri",
                    "Modelul își amintește zilele individuale mai bine decât lunile",
                    "Își amintește parțial direcția lunară (regimuri, luni celebre), dar nu mișcările zilnice: privirea în viitor este un pericol la orizontul evenimentelor cunoscute"
                ],
                "correctExplanation": "Un AUC de 0,5 înseamnă nicio cunoaștere. Un AUC lunar mult peste 0,5 înainte de publicare este memoria istoriei pieței (de exemplu octombrie 2008, martie 2020); zgomotul zilnic nu este memorat.",
                "incorrectExplanation": "Sunt luni trecute despre care modelul a citit la antrenare, nu prognoze; 0,69 pentru luni față de circa 0,5 pentru zile înseamnă doar o memorie grosieră a regimurilor și a episoadelor celebre."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Remedies for look-ahead bias",
                "text": "Which of the following is a remedy for look-ahead bias when backtesting a large language model (LLM) sentiment signal?",
                "options": [
                    "Test only on headlines published after the model's training cutoff, or remove company names and dates, or use point-in-time models",
                    "Use a larger model, which generalises better",
                    "Average the scores from several prompts",
                    "Extend the backtest further into the past to get more observations"
                ],
                "correctExplanation": "Lopez-Lira & Tang (2026) test GPT-4 on post-cutoff headlines; Glasserman & Lin (2023) anonymise the text; Sarkar & Vafa (2024) propose point-in-time models. Always report the model version and the release date of its weights.",
                "incorrectExplanation": "Larger models remember more, prompts do not remove memory, and older data are even more likely to be in the training text. Only post-cutoff data, anonymised text or point-in-time models remove the bias."
            },
            "ro": {
                "title": "Remedii pentru privirea în viitor",
                "text": "Care dintre următoarele este un remediu pentru privirea în viitor (look-ahead bias) la testarea istorică a unui semnal de sentiment dintr-un model mare de limbaj (LLM)?",
                "options": [
                    "Testarea doar pe titluri publicate după data-limită a datelor de antrenare, eliminarea numelor de companii și a datelor calendaristice sau folosirea unor modele point-in-time",
                    "Folosirea unui model mai mare, care generalizează mai bine",
                    "Media scorurilor obținute cu mai multe prompt-uri",
                    "Extinderea testului istoric mai departe în trecut, pentru mai multe observații"
                ],
                "correctExplanation": "Lopez-Lira & Tang (2026) testează GPT-4 pe titluri de după data-limită; Glasserman & Lin (2023) anonimizează textul; Sarkar & Vafa (2024) propun modele point-in-time. Raportați mereu versiunea modelului și data publicării ponderilor.",
                "incorrectExplanation": "Modelele mai mari memorează mai mult, prompt-urile nu șterg memoria, iar datele mai vechi sunt și mai probabil incluse în textele de antrenare. Doar datele de după data-limită, textul anonimizat sau modelele point-in-time elimină distorsiunea."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "FNSPID timestamps",
                "text": "In FNSPID (Financial News and Stock Price Integration Dataset), 99.8% of headlines are stamped exactly 00:00 UTC. Day d is the first trading day on or after the headline date. Which return is the first safe forecast?",
                "options": [
                    "The return on day d (close of d − 1 to close of d)",
                    "The return on day d + 2 (close of d + 1 to close of d + 2)",
                    "The return on day d + 1 (close of d to close of d + 1)",
                    "The return from the open to the close of day d"
                ],
                "correctExplanation": "The source gives the date, not the time: a headline dated d may appear before the open, during the session or after the close. Returns on d and d + 1 may still contain the reaction, so d + 2 is the first return one can trade on.",
                "incorrectExplanation": "Because only the date is known, the headline may be published after the close of d; the position can be opened safely only at the close of d + 1, which earns the return of d + 2."
            },
            "ro": {
                "title": "Marcajele de timp FNSPID",
                "text": "În FNSPID (Financial News and Stock Price Integration Dataset), 99,8% dintre titluri au marcajul exact 00:00 UTC. Ziua d este prima zi de tranzacționare egală cu data titlului sau ulterioară. Care randament este prima prognoză sigură?",
                "options": [
                    "Randamentul din ziua d (de la închiderea din d − 1 la închiderea din d)",
                    "Randamentul din ziua d + 2 (de la închiderea din d + 1 la închiderea din d + 2)",
                    "Randamentul din ziua d + 1 (de la închiderea din d la închiderea din d + 1)",
                    "Randamentul de la deschiderea la închiderea zilei d"
                ],
                "correctExplanation": "Sursa dă data, nu ora: un titlu datat d poate apărea înainte de deschidere, în timpul ședinței sau după închidere. Randamentele din d și d + 1 pot conține încă reacția, deci d + 2 este primul randament pe care se poate tranzacționa.",
                "incorrectExplanation": "Deoarece se cunoaște doar data, titlul poate fi publicat după închiderea din d; poziția poate fi deschisă sigur abia la închiderea din d + 1, câștigând randamentul din d + 2."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Clustered standard errors",
                "text": "The pooled regression of excess returns on the standardised daily sentiment score uses all stock-days with news. Why are standard errors clustered by trading day (Petersen, 2009)?",
                "options": [
                    "Because sentiment scores are not normally distributed",
                    "Because each stock has a different number of headlines",
                    "Because errors of different stocks on the same day are correlated through common shocks, and ordinary standard errors would be too small",
                    "Because clustering removes the look-ahead bias of the language model"
                ],
                "correctExplanation": "Common market shocks hit all 16 stocks on the same day. The clustered covariance sums X_gᵀ ε̂_g ε̂_gᵀ X_g over days g, so the t-statistics are not overstated.",
                "incorrectExplanation": "The issue is cross-sectional correlation within a day: treating same-day observations as independent overstates the information and inflates the t-statistics."
            },
            "ro": {
                "title": "Erori standard grupate",
                "text": "Regresia pe date cumulate a randamentelor în exces pe scorul zilnic standardizat de sentiment folosește toate zilele-acțiune cu știri. De ce sunt erorile standard grupate pe zile de tranzacționare (Petersen, 2009)?",
                "options": [
                    "Pentru că scorurile de sentiment nu urmează distribuția Normală",
                    "Pentru că fiecare acțiune are un număr diferit de titluri",
                    "Pentru că erorile acțiunilor diferite din aceeași zi sunt corelate prin șocuri comune, iar erorile standard obișnuite ar fi prea mici",
                    "Pentru că gruparea elimină privirea în viitor a modelului de limbaj"
                ],
                "correctExplanation": "Șocurile comune de piață lovesc toate cele 16 acțiuni în aceeași zi. Covarianța grupată însumează X_gᵀ ε̂_g ε̂_gᵀ X_g pe zilele g, deci statisticile t nu sunt supraestimate.",
                "incorrectExplanation": "Problema este corelația dintre acțiuni în aceeași zi: tratarea observațiilor din aceeași zi ca independente supraestimează informația și umflă statisticile t."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Reaction versus prediction",
                "text": "Per one standard deviation of the FinBERT score, the excess return is +39.2 bp on day d (t = +17.27), +3.2 bp on d + 1 (t = +1.60) and −0.5 bp on d + 2 (t = −0.25). What do these numbers show?",
                "options": [
                    "FinBERT is a strong predictor of future returns",
                    "The day-d slope proves that FinBERT sentiment causes returns",
                    "The signal is strongest on d + 2 once clustering is used",
                    "Headlines describe prices: a strong same-day reaction, and no predictability for the first tradable return"
                ],
                "correctExplanation": "Many headlines report the price move itself (\"shares jump\", \"stock falls\"), so causality runs both ways on day d. On d + 2, the return one can still trade, the slope is indistinguishable from zero.",
                "incorrectExplanation": "The large t-statistic belongs to day d, which is reaction, not forecast; for d + 2 the slope is −0.5 bp with t = −0.25."
            },
            "ro": {
                "title": "Reacție versus predicție",
                "text": "Pentru o abatere standard a scorului FinBERT, randamentul în exces este +39,2 bp în ziua d (t = +17,27), +3,2 bp în d + 1 (t = +1,60) și −0,5 bp în d + 2 (t = −0,25). Ce arată aceste cifre?",
                "options": [
                    "FinBERT este un predictor puternic al randamentelor viitoare",
                    "Panta din ziua d dovedește că sentimentul FinBERT cauzează randamentele",
                    "Semnalul este cel mai puternic în d + 2 după gruparea erorilor",
                    "Titlurile descriu prețurile: o reacție puternică în aceeași zi și nicio predictibilitate pentru primul randament tranzacționabil"
                ],
                "correctExplanation": "Multe titluri raportează chiar mișcarea prețului („shares jump”, „stock falls”), deci cauzalitatea merge în ambele sensuri în ziua d. În d + 2, randamentul care mai poate fi tranzacționat, panta nu diferă de zero.",
                "incorrectExplanation": "Statistica t mare aparține zilei d, adică reacției, nu prognozei; pentru d + 2 panta este −0,5 bp cu t = −0,25."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Event study around news days",
                "text": "For the most positive third of news days (FinBERT), the cumulative excess return is +0.63% over the 5 days before, +0.50% on day d and +0.11% on d + 1. How should this be read?",
                "options": [
                    "By the time a trader can act, the price has mostly adjusted; pre-event moves suggest leaks or headlines written after the move",
                    "The news causes a slow drift that is easy to trade on day d + 2",
                    "The pre-event move proves the data are wrong",
                    "Positive news days are always followed by reversals"
                ],
                "correctExplanation": "Most of the move happens before and on the news day, in line with efficient markets (Chapter 2). The tradable days d + 2 to d + 5 are small and similar for positive (+0.43%) and negative (+0.19%) news.",
                "incorrectExplanation": "The cumulative return is mostly earned before and on day d; what remains for the tradable window is small and not clearly separated between positive and negative news."
            },
            "ro": {
                "title": "Studiu de eveniment în jurul zilelor cu știri",
                "text": "Pentru treimea cea mai pozitivă a zilelor cu știri (FinBERT), randamentul în exces cumulat este +0,63% în cele 5 zile dinainte, +0,50% în ziua d și +0,11% în d + 1. Cum trebuie interpretat?",
                "options": [
                    "Până când un trader poate acționa, prețul s-a ajustat în mare parte; mișcările dinaintea evenimentului sugerează scurgeri de informație sau titluri scrise după mișcare",
                    "Știrea produce o derivă lentă, ușor de tranzacționat în ziua d + 2",
                    "Mișcarea dinaintea evenimentului dovedește că datele sunt greșite",
                    "Zilele cu știri pozitive sunt întotdeauna urmate de reveniri"
                ],
                "correctExplanation": "Cea mai mare parte a mișcării are loc înainte de știre și în ziua ei, în acord cu piețele eficiente (Capitolul 2). Zilele tranzacționabile d + 2 până la d + 5 aduc puțin și similar pentru știrile pozitive (+0,43%) și negative (+0,19%).",
                "incorrectExplanation": "Randamentul cumulat se obține mai ales înainte de ziua d și în ziua d; ce rămâne pentru fereastra tranzacționabilă este mic și nu separă clar știrile pozitive de cele negative."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Break-even cost",
                "text": "The daily Qwen2.5-7B strategy earns about 6 bp gross on days with positions; each such day needs four trades (stock and SPY, in and out) at 5 bp each. What are the break-even cost per trade and the net result?",
                "options": [
                    "About 6 bp per trade; the strategy is profitable after costs",
                    "About 1.5 bp per trade, well below 5 bp: the Sharpe ratio goes from +0.63 before costs to −1.48 after",
                    "About 1.2 bp per trade; costs do not matter for significance",
                    "About 24 bp per trade; the strategy easily covers 20 bp of daily costs"
                ],
                "correctExplanation": "Break-even cost = gross return on days with positions / 4 = 6/4 = 1.5 bp per trade. Actual costs are 4 × 5 = 20 bp per day, far above the gross edge.",
                "incorrectExplanation": "Divide the gross daily return by the four trades: about 1.5 bp per trade. With 5 bp per trade the 20 bp daily cost wipes out the edge."
            },
            "ro": {
                "title": "Costul de echilibru",
                "text": "Strategia zilnică Qwen2.5-7B câștigă brut circa 6 bp în zilele cu poziții; fiecare astfel de zi necesită patru tranzacții (acțiunea și SPY, la intrare și la ieșire) de câte 5 bp. Care sunt costul de echilibru pe tranzacție și rezultatul net?",
                "options": [
                    "Circa 6 bp pe tranzacție; strategia este profitabilă după costuri",
                    "Circa 1,5 bp pe tranzacție, mult sub 5 bp: raportul Sharpe trece de la +0,63 înainte de costuri la −1,48 după",
                    "Circa 1,2 bp pe tranzacție; costurile nu contează pentru semnificație",
                    "Circa 24 bp pe tranzacție; strategia acoperă ușor 20 bp de costuri zilnice"
                ],
                "correctExplanation": "Costul de echilibru = randamentul brut în zilele cu poziții / 4 = 6/4 = 1,5 bp pe tranzacție. Costurile reale sunt 4 × 5 = 20 bp pe zi, mult peste avantajul brut.",
                "incorrectExplanation": "Împărțiți randamentul brut zilnic la cele patru tranzacții: circa 1,5 bp pe tranzacție. La 5 bp pe tranzacție, costul zilnic de 20 bp anulează avantajul."
            }
        },
        {
            "correct": 2,
            "en": {
                "title": "Stability over subperiods",
                "text": "The FinBERT strategy earns before costs +1.4 bp per day in 2010–2015, −1.8 bp in 2016–2019, +24.3 bp in 2020–2021 (t = +1.89) and −1.8 bp in 2022–2023. What is the honest reading?",
                "options": [
                    "The strategy is robust, since the full-sample mean is positive",
                    "The 2020–2021 result is significant at 5% and proves the signal works",
                    "The evidence is weak: only two meme-stock years stand out, not significant at 5%, and 20 bp of daily costs would barely break even even there",
                    "The subperiods show a steady upward trend in profitability"
                ],
                "correctExplanation": "One short, special period drives the average. With 16 heavily followed stocks, date-only timestamps and daily frequency, little signal is expected; a negative result still tells you where the signal is not.",
                "incorrectExplanation": "Three of four subperiods are near zero, and t = +1.89 for 2020–2021 is below the 5% threshold; with four trades of 5 bp per day even that period barely breaks even."
            },
            "ro": {
                "title": "Stabilitatea pe subperioade",
                "text": "Strategia FinBERT câștigă înainte de costuri +1,4 bp pe zi în 2010–2015, −1,8 bp în 2016–2019, +24,3 bp în 2020–2021 (t = +1,89) și −1,8 bp în 2022–2023. Care este interpretarea onestă?",
                "options": [
                    "Strategia este robustă, deoarece media pe întregul eșantion este pozitivă",
                    "Rezultatul din 2020–2021 este semnificativ la 5% și dovedește că semnalul funcționează",
                    "Dovezile sunt slabe: doar doi ani de meme stocks ies în evidență, nesemnificativ la 5%, iar 20 bp de costuri zilnice abia ar fi acoperite chiar și acolo",
                    "Subperioadele arată o creștere constantă a profitabilității"
                ],
                "correctExplanation": "O singură perioadă scurtă și specială determină media. Cu 16 acțiuni foarte urmărite, marcaje doar la nivel de dată și frecvență zilnică, semnalul așteptat este mic; un rezultat negativ arată totuși unde semnalul nu există.",
                "incorrectExplanation": "Trei din patru subperioade sunt aproape de zero, iar t = +1,89 pentru 2020–2021 este sub pragul de 5%; cu patru tranzacții de 5 bp pe zi, chiar și acea perioadă abia ajunge la echilibru."
            }
        },
        {
            "correct": 3,
            "en": {
                "title": "Specification curve",
                "text": "Across 36 variants of the headline strategy (3 scores × 3 thresholds × 4 holding days), 3 have t > 1.96. Flipping the sign of each signal day's positions at random, the same flip for all variants, 3 or more such t occur with probability 0.095. What is the right report?",
                "options": [
                    "The best variant, since it has t > 1.96",
                    "The three significant variants, since they confirm each other",
                    "The average of the 36 t-statistics, since averaging removes noise",
                    "The whole curve with the joint test: the evidence is compatible with no predictability at 5%"
                ],
                "correctExplanation": "A specification curve (Simonsohn, Simmons & Nelson, 2020) reports all reasonable choices and tests them jointly under a null that keeps their dependence. Here the joint p-value is 0.095 and the median t is 0.50.",
                "incorrectExplanation": "The variants share days and stocks, so their t-statistics are dependent; selecting or averaging them ignores the search. A joint test under a common null is needed."
            },
            "ro": {
                "title": "Curba specificațiilor",
                "text": "Din 36 de variante ale strategiei pe titluri (3 scoruri × 3 praguri × 4 zile de deținere), 3 au t > 1,96. Schimbând aleator semnul pozițiilor fiecărei zile de semnal, aceeași schimbare pentru toate variantele, 3 sau mai multe astfel de valori t apar cu probabilitatea 0,095. Ce este corect să raportați?",
                "options": [
                    "Cea mai bună variantă, pentru că are t > 1,96",
                    "Cele trei variante semnificative, pentru că se confirmă reciproc",
                    "Media celor 36 de statistici t, pentru că media elimină zgomotul",
                    "Întreaga curbă, cu testul comun: dovezile sunt compatibile cu lipsa predictibilității la 5%"
                ],
                "correctExplanation": "O curbă a specificațiilor (Simonsohn, Simmons & Nelson, 2020) raportează toate alegerile rezonabile și le testează împreună sub un nul care păstrează dependența dintre ele. Aici valoarea p comună este 0,095, iar t median este 0,50.",
                "incorrectExplanation": "Variantele folosesc aceleași zile și acțiuni, deci statisticile lor t sunt dependente; selecția sau media lor ignoră căutarea. Este nevoie de un test comun sub un nul comun."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "Spot the error: same-day alignment",
                "text": "An AI assistant writes: \"Using FNSPID headlines, I aligned each headline to the close-to-close return of its date and regressed the return on FinBERT sentiment. The slope has t = 17, so headline sentiment is a strong forecast of stock returns.\" What is the error?",
                "options": [
                    "The headlines carry only a date, so they may appear during or after that day's session: the same-day slope measures reaction, not a forecast; the first safe return is d + 2",
                    "The t-statistic should use the Student t distribution instead of the Normal distribution",
                    "FinBERT should be replaced by a dictionary for such a regression",
                    "Nothing is wrong, since t = 17 is far above any critical value"
                ],
                "correctExplanation": "99.8% of FNSPID stamps are 00:00 UTC. A headline dated d may report the move itself (\"shares jump\"); at d + 2 the lecture finds −0.5 bp with t = −0.25 for FinBERT.",
                "incorrectExplanation": "A large t on the same-day return shows that headlines describe prices; a forecast must use a return that starts after the news is surely public, here d + 2."
            },
            "ro": {
                "title": "Găsiți eroarea: alinierea în aceeași zi",
                "text": "Un asistent AI scrie: „Folosind titlurile FNSPID, am aliniat fiecare titlu la randamentul de la închidere la închidere din data sa și am regresat randamentul pe sentimentul FinBERT. Panta are t = 17, deci sentimentul titlurilor este o prognoză puternică a randamentelor.” Care este eroarea?",
                "options": [
                    "Titlurile au doar data, deci pot apărea în timpul ședinței sau după ea: panta din aceeași zi măsoară reacția, nu o prognoză; primul randament sigur este cel din d + 2",
                    "Statistica t trebuia calculată cu distribuția t Student în locul distribuției Normale",
                    "FinBERT trebuia înlocuit cu un dicționar pentru o astfel de regresie",
                    "Nu este nicio eroare, deoarece t = 17 depășește cu mult orice valoare critică"
                ],
                "correctExplanation": "99,8% dintre marcajele FNSPID sunt 00:00 UTC. Un titlu datat d poate raporta chiar mișcarea („shares jump”); în d + 2 cursul găsește −0,5 bp cu t = −0,25 pentru FinBERT.",
                "incorrectExplanation": "Un t mare pe randamentul din aceeași zi arată că titlurile descriu prețurile; o prognoză trebuie să folosească un randament care începe după ce știrea este sigur publică, aici d + 2."
            }
        },
        {
            "correct": 1,
            "en": {
                "title": "Spot the error: out-of-sample LLM",
                "text": "An AI assistant writes: \"I scored 2010–2023 headlines with Qwen2.5-7B, whose weights were released in September 2024. The model was never fitted on our returns, so the backtest is fully out-of-sample, and the +5.64 bp per day (t = 2.26) is a genuine forecast.\" What is the error?",
                "options": [
                    "The daily t-statistic should be replaced by a monthly one",
                    "A model trained on text up to 2024 may remember what followed the 2010–2023 news, so the test is not out-of-sample; part of the edge may be memorised prices",
                    "The result is invalid only because the model has fewer parameters than GPT-4",
                    "Nothing is wrong: not fitting the model on returns is enough for out-of-sample"
                ],
                "correctExplanation": "Look-ahead bias: an LLM released in 2024 has read about the market after every earlier headline. Clean tests use post-cutoff headlines, anonymised text or point-in-time models; the 5.64 bp also vanishes after costs.",
                "incorrectExplanation": "Out-of-sample means the model had no access to the test period's information; a model trained on text through 2024 did, even if it never saw the return series directly."
            },
            "ro": {
                "title": "Găsiți eroarea: LLM în afara eșantionului",
                "text": "Un asistent AI scrie: „Am evaluat titlurile din 2010–2023 cu Qwen2.5-7B, ale cărui ponderi au fost publicate în septembrie 2024. Modelul nu a fost niciodată estimat pe randamentele noastre, deci testul istoric este complet în afara eșantionului, iar +5,64 bp pe zi (t = 2,26) este o prognoză autentică.” Care este eroarea?",
                "options": [
                    "Statistica t zilnică trebuia înlocuită cu una lunară",
                    "Un model antrenat pe texte până în 2024 își poate aminti ce a urmat știrilor din 2010–2023, deci testul nu este în afara eșantionului; o parte din avantaj poate fi memorarea prețurilor",
                    "Rezultatul este invalid doar pentru că modelul are mai puțini parametri decât GPT-4",
                    "Nu este nicio eroare: faptul că modelul nu a fost estimat pe randamente este suficient pentru a fi în afara eșantionului"
                ],
                "correctExplanation": "Privirea în viitor: un LLM publicat în 2024 a citit despre piață după fiecare titlu anterior. Testele curate folosesc titluri de după data-limită, text anonimizat sau modele point-in-time; în plus, cei 5,64 bp dispar după costuri.",
                "incorrectExplanation": "În afara eșantionului înseamnă că modelul nu a avut acces la informația din perioada de test; un model antrenat pe texte până în 2024 a avut, chiar dacă nu a văzut direct seria de randamente."
            }
        }
    ]
};

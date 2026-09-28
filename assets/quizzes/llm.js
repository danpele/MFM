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
                "title": "Dictionary tone",
                "text": "A headline contains 3 positive and 1 negative word from the Loughran-McDonald (LM) dictionary. What is its tone τ = (P − N)/(P + N) and its class?",
                "options": [
                    "τ = 0.50, positive",
                    "τ = 2, positive",
                    "τ = 0.25, neutral",
                    "τ = −0.50, negative"
                ],
                "correctExplanation": "τ = (3 − 1)/(3 + 1) = 2/4 = 0.50 > 0, so the headline is classified as positive. The tone is bounded in [−1, 1].",
                "incorrectExplanation": "The tone is the difference of the counts divided by their sum: (3 − 1)/(3 + 1) = 0.50, which lies in [−1, 1] and is positive."
            },
            "ro": {
                "title": "Tonul unui dicționar",
                "text": "Un titlu conține 3 cuvinte pozitive și 1 cuvânt negativ din dicționarul Loughran-McDonald (LM). Care este tonul τ = (P − N)/(P + N) și clasa lui?",
                "options": [
                    "τ = 0,50, pozitiv",
                    "τ = 2, pozitiv",
                    "τ = 0,25, neutru",
                    "τ = −0,50, negativ"
                ],
                "correctExplanation": "τ = (3 − 1)/(3 + 1) = 2/4 = 0,50 > 0, deci titlul este clasificat pozitiv. Tonul este mărginit în [−1, 1].",
                "incorrectExplanation": "Tonul este diferența numărătorilor împărțită la suma lor: (3 − 1)/(3 + 1) = 0,50, valoare din [−1, 1] și pozitivă."
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
                "title": "Accuracy versus macro-F1",
                "text": "On the Twitter Financial News validation set, always predicting \"neutral\" gives 66% accuracy. Why does the lecture also report macro-F1 (the average of the F1 scores of the three classes)?",
                "options": [
                    "Because macro-F1 is always higher than accuracy and makes the models look better",
                    "Because accuracy cannot be computed when there are three classes",
                    "Because macro-F1 does not depend on the number of texts in the test set",
                    "Because a model can reach high accuracy by ignoring the rare classes; macro-F1 counts each class equally"
                ],
                "correctExplanation": "\"Always neutral\" has 66% accuracy but a macro-F1 of only 26.4%: it gets F1 = 0 on the positive and negative classes. Macro-F1 exposes classifiers that never find the classes a trader cares about.",
                "incorrectExplanation": "The majority-class benchmark shows the problem: high accuracy, yet no positive or negative headline is found. Macro-F1 gives the rare classes the same weight as the neutral one."
            },
            "ro": {
                "title": "Acuratețe versus F1 macro",
                "text": "Pe setul de validare Twitter Financial News, prognoza „mereu neutru” dă 66% acuratețe. De ce raportează cursul și F1 macro (media scorurilor F1 ale celor trei clase)?",
                "options": [
                    "Pentru că F1 macro este mereu mai mare decât acuratețea și avantajează modelele",
                    "Pentru că acuratețea nu poate fi calculată când există trei clase",
                    "Pentru că F1 macro nu depinde de numărul de texte din setul de test",
                    "Pentru că un model poate avea acuratețe mare ignorând clasele rare; F1 macro tratează fiecare clasă la fel"
                ],
                "correctExplanation": "„Mereu neutru” are 66% acuratețe, dar un F1 macro de doar 26,4%: obține F1 = 0 pe clasele pozitivă și negativă. F1 macro scoate la iveală clasificatorii care nu găsesc niciodată clasele importante pentru un trader.",
                "incorrectExplanation": "Reperul clasei majoritare arată problema: acuratețe mare, dar niciun titlu pozitiv sau negativ găsit. F1 macro dă claselor rare aceeași pondere ca celei neutre."
            }
        },
        {
            "correct": 0,
            "en": {
                "title": "McNemar test",
                "text": "On 2 388 Twitter headlines, LM is wrong and FinBERT right in n01 = 539 cases, LM right and FinBERT wrong in n10 = 252 cases. Which texts does the exact McNemar test use?",
                "options": [
                    "Only the 791 discordant texts: under equal accuracy, n01 ∼ Binomial(791, 0.5)",
                    "All 2 388 texts, weighted by the confidence of each model",
                    "Only the texts on which both models are right",
                    "Only the texts that the annotators labelled positive or negative"
                ],
                "correctExplanation": "Texts where the two classifiers agree carry no information about which is better. Under H0, each discordant text favours either model with probability 0.5; 539 versus 252 gives p < 0.001.",
                "incorrectExplanation": "The paired test conditions on disagreements: n01 + n10 = 791 texts, with n01 ∼ Binomial(791, 0.5) under equal accuracy. Agreements do not enter the test."
            },
            "ro": {
                "title": "Testul McNemar",
                "text": "Pe 2 388 de titluri Twitter, LM greșește și FinBERT are dreptate în n01 = 539 de cazuri, iar LM are dreptate și FinBERT greșește în n10 = 252 de cazuri. Ce texte folosește testul McNemar exact?",
                "options": [
                    "Doar cele 791 de texte discordante: la acuratețe egală, n01 ∼ Binomial(791; 0,5)",
                    "Toate cele 2 388 de texte, ponderate cu încrederea fiecărui model",
                    "Doar textele pe care ambele modele le clasifică corect",
                    "Doar textele etichetate pozitiv sau negativ de adnotatori"
                ],
                "correctExplanation": "Textele pe care cei doi clasificatori le tratează la fel nu spun nimic despre care este mai bun. Sub H0, fiecare text discordant favorizează un model cu probabilitatea 0,5; 539 față de 252 dă p < 0,001.",
                "incorrectExplanation": "Testul pe perechi se bazează pe dezacorduri: n01 + n10 = 791 de texte, cu n01 ∼ Binomial(791; 0,5) la acuratețe egală. Acordurile nu intră în test."
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
                "correctExplanation": "The drop of about 16 percentage points is the in-sample trap: evaluate a language model only on texts it has never seen, as with out-of-sample testing in Chapters 8 and 13.",
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
                "correctExplanation": "Scăderea de circa 16 puncte procentuale este capcana evaluării în eșantion: evaluați un model de limbaj doar pe texte pe care nu le-a văzut niciodată, ca la testarea în afara eșantionului din capitolele 8 și 13.",
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
                "title": "Zero-shot scoring",
                "text": "In the lecture, how is the zero-shot sentiment of a headline obtained from an instruction-tuned large language model (LLM)?",
                "options": [
                    "By generating a paragraph of explanation and counting positive words in it",
                    "From the logits of the tokens \"positive\", \"negative\", \"neutral\" at the first generated position: a softmax gives p_k, the label is arg max p_k and the score p_pos − p_neg",
                    "By fine-tuning the LLM on Financial PhraseBank before scoring",
                    "By averaging the embeddings of the headline and comparing them with a threshold"
                ],
                "correctExplanation": "No text is generated, so nothing needs parsing: the probabilities of the three answer words give both a label and a continuous score in [−1, 1].",
                "incorrectExplanation": "Zero-shot means no labelled examples and no training: the prompt asks for one word, and the probabilities of the three answer tokens at the first position are read directly."
            },
            "ro": {
                "title": "Scorul zero-shot",
                "text": "În curs, cum se obține sentimentul zero-shot al unui titlu de la un model mare de limbaj (LLM) ajustat pe instrucțiuni?",
                "options": [
                    "Generând un paragraf de explicații și numărând cuvintele pozitive din el",
                    "Din logiții tokenilor „positive”, „negative”, „neutral” la prima poziție generată: un softmax dă p_k, eticheta este arg max p_k, iar scorul p_pos − p_neg",
                    "Ajustând fin LLM-ul pe Financial PhraseBank înainte de evaluare",
                    "Făcând media vectorilor de embedding ai titlului și comparând-o cu un prag"
                ],
                "correctExplanation": "Nu se generează text, deci nu trebuie interpretat nimic: probabilitățile celor trei cuvinte-răspuns dau atât o etichetă, cât și un scor continuu în [−1, 1].",
                "incorrectExplanation": "Zero-shot înseamnă fără exemple etichetate și fără antrenare: prompt-ul cere un singur cuvânt, iar probabilitățile celor trei tokeni-răspuns la prima poziție se citesc direct."
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
                "title": "Embeddings and principal components",
                "text": "The first two principal components of the 384-dimensional MiniLM embeddings of Twitter headlines separate topics (companies, macro news, crypto) rather than sentiment. Yet logistic regression on all 384 dimensions reaches 78.6% accuracy. Why?",
                "options": [
                    "The embeddings contain no sentiment information, and the 78.6% is luck",
                    "Principal component analysis (PCA) keeps the directions of largest variance, which need not be the sentiment direction; a supervised model finds that direction",
                    "Logistic regression uses only the first two components",
                    "Sentiment is always the first principal component of any text embedding"
                ],
                "correctExplanation": "PCA is unsupervised: it ranks directions by variance. Sentiment is one direction among many, and the labels let the logistic regression find it.",
                "incorrectExplanation": "Unsupervised PCA picks the largest-variance directions, here topic; the supervised classifier uses all 384 dimensions and the labels to find the sentiment direction."
            },
            "ro": {
                "title": "Embeddings și componente principale",
                "text": "Primele două componente principale ale embedding-urilor MiniLM cu 384 de dimensiuni ale titlurilor Twitter separă subiecte (companii, știri macro, cripto), nu sentiment. Totuși, regresia logistică pe toate cele 384 de dimensiuni atinge 78,6% acuratețe. De ce?",
                "options": [
                    "Embedding-urile nu conțin informație despre sentiment, iar 78,6% este noroc",
                    "Analiza componentelor principale (PCA) păstrează direcțiile de varianță maximă, care nu sunt neapărat direcția sentimentului; un model supervizat găsește acea direcție",
                    "Regresia logistică folosește doar primele două componente",
                    "Sentimentul este întotdeauna prima componentă principală a oricărui embedding de text"
                ],
                "correctExplanation": "PCA este nesupervizată: ordonează direcțiile după varianță. Sentimentul este o direcție printre multe, iar etichetele permit regresiei logistice să o găsească.",
                "incorrectExplanation": "PCA nesupervizată alege direcțiile cu varianță maximă, aici subiectul; clasificatorul supervizat folosește toate cele 384 de dimensiuni și etichetele pentru a găsi direcția sentimentului."
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
                "title": "Risks of AI agents",
                "text": "An AI agent, a large language model (LLM) in a loop that reads news, calls tools and can send orders through an API (Application Programming Interface), reads a fake press release that contains hidden instructions. What is this risk called, and which control fits?",
                "options": [
                    "Look-ahead bias; test the agent only after its release date",
                    "Survivorship bias; include delisted stocks",
                    "Distraction bias; remove company names from the text",
                    "Prompt injection; position limits, human approval for orders and logging of every step"
                ],
                "correctExplanation": "A text read by the agent can carry instructions that manipulate it. Controls include position limits, human approval for orders, logging and tests after each model update; the IMF (2024) also warns that similar agents may trade alike in stress.",
                "incorrectExplanation": "The hidden instructions in the text manipulate the agent itself: that is prompt injection, handled with limits, human approval and logging, not with backtest remedies."
            },
            "ro": {
                "title": "Riscurile agenților AI",
                "text": "Un agent AI, adică un model mare de limbaj (LLM) într-o buclă care citește știri, apelează instrumente și poate trimite ordine printr-un API (Application Programming Interface), citește un comunicat de presă fals care conține instrucțiuni ascunse. Cum se numește acest risc și ce control i se potrivește?",
                "options": [
                    "Privirea în viitor; testarea agentului doar după data publicării lui",
                    "Distorsiunea de supraviețuire; includerea acțiunilor delistate",
                    "Distorsiunea de distragere; eliminarea numelor de companii din text",
                    "Prompt injection; limite de poziție, aprobare umană pentru ordine și jurnalizarea fiecărui pas"
                ],
                "correctExplanation": "Un text citit de agent poate conține instrucțiuni care îl manipulează. Controalele includ limite de poziție, aprobare umană pentru ordine, jurnalizare și teste după fiecare actualizare a modelului; FMI (2024) avertizează și că agenți similari pot tranzacționa la fel în perioade de stres.",
                "incorrectExplanation": "Instrucțiunile ascunse din text manipulează chiar agentul: este prompt injection, tratat cu limite, aprobare umană și jurnalizare, nu cu remedii pentru testarea istorică."
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

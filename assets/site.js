// ============================================================
// MFM course website - rendering + quiz engine
// Reads window.MFM_DATA (course-data.js), window.MFM_CONFIG (config.js)
// and quiz banks registered in MFM_DATA.quizzes by chapter id (assets/quizzes/<id>.js).
// Chapters are referenced by their stable `id`; `num` is only the display order.
// Language is set by the page shell: window.MFM_LANG = 'en' | 'ro'.
// ============================================================
(function () {
    'use strict';

    const LANG = window.MFM_LANG === 'ro' ? 'ro' : 'en';
    const D = window.MFM_DATA;
    const T = D.ui[LANG];
    const CFG = window.MFM_CONFIG || {};
    const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

    const isConfigured = v => typeof v === 'string' && v.length > 0 && !v.startsWith('YOUR_');
    const $ = id => document.getElementById(id);

    // localStorage can throw (private mode, blocked storage) - never let it break the page
    const store = {
        get(k) { try { return localStorage.getItem('mfm-' + k); } catch (e) { return null; } },
        set(k, v) { try { localStorage.setItem('mfm-' + k, v); } catch (e) { /* ignore */ } },
        del(k) { try { localStorage.removeItem('mfm-' + k); } catch (e) { /* ignore */ } }
    };

    const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

    function typeset(el) {
        if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise(el ? [el] : undefined).catch(() => {});
        }
    }

    // ------------------------------------------------------------
    // STATIC TEXT (header, nav, section titles)
    // ------------------------------------------------------------
    function renderStatic() {
        document.title = T.pageTitle;
        document.documentElement.lang = LANG;
        document.querySelectorAll('[data-t]').forEach(el => {
            const path = el.getAttribute('data-t').split('.');
            let v = T;
            for (const p of path) v = v && v[p];
            if (typeof v === 'string') el.innerHTML = v;
        });
    }

    // ------------------------------------------------------------
    // OVERVIEW, OBJECTIVES, FORMULAS
    // ------------------------------------------------------------
    function renderOverview() {
        $('overview-cards').innerHTML = D.overview[LANG].map(c =>
            `<div class="info-card"><h3>${c.h}</h3>${c.p.map(p => `<p>${p}</p>`).join('')}</div>`
        ).join('');
        $('objectives-list').innerHTML = D.objectives[LANG].map(o => `<li>${o}</li>`).join('');
    }

    // ------------------------------------------------------------
    // HERO STATS
    // ------------------------------------------------------------
    function renderHero() {
        const S = window.MFM_STATS || {};
        const quiz = Object.values(D.quizzes).reduce((n, b) => n + b.questions.length, 0);
        const fmt = n => Number(n).toLocaleString(LANG === 'ro' ? 'ro-RO' : 'en-GB');
        const items = [
            ['chapters', S.chapters || D.chapters.length],
            ['slides', S.slides], ['seminar', S.seminar],
            ['quantlets', S.quantlets], ['quiz', quiz], ['charts', S.charts]
        ].filter(([, v]) => v);
        $('hero-stats').innerHTML = items.map(([k, v]) =>
            `<div class="stat"><span class="stat-num">${fmt(v)}</span><span class="stat-label">${T.stats[k]}</span></div>`
        ).join('');
    }

    // ------------------------------------------------------------
    // LIGHTBOX (chapter charts)
    // ------------------------------------------------------------
    function openLightbox(src, caption) {
        $('lightbox-img').src = src;
        $('lightbox-img').alt = caption;
        $('lightbox-cap').textContent = caption;
        $('lightbox').hidden = false;
        document.body.classList.add('no-scroll');
        $('lightbox-close').focus();
    }

    function initLightbox() {
        const box = $('lightbox');
        const close = () => { box.hidden = true; document.body.classList.remove('no-scroll'); };
        $('lightbox-close').setAttribute('aria-label', T.close);
        $('lightbox-close').onclick = close;
        box.onclick = e => { if (e.target === box) close(); };
        document.addEventListener('keydown', e => { if (e.key === 'Escape' && !box.hidden) close(); });
    }

    // ------------------------------------------------------------
    // CHAPTER CARDS
    // ------------------------------------------------------------
    const LINK_CLASS = { slides: 'btn-primary', seminar: 'btn-secondary', lectureNb: 'btn-outline', seminarNb: 'btn-outline', quantlets: 'btn-outline' };
    const PLACEHOLDER_LINKS = ['slides', 'seminar', 'lectureNb', 'seminarNb'];

    function linkButton(l) {
        const external = /^https?:/.test(l.href) ? ' target="_blank" rel="noopener"' : '';
        const main = `<a href="${l.href}" class="btn ${LINK_CLASS[l.type]}"${external}>${T.links[l.type]}</a>`;
        if (!l.colab) return main;
        return `<span class="link-group">${main}<a href="${l.colab}" class="btn btn-colab" target="_blank" rel="noopener" title="${T.links.colab}">Colab</a></span>`;
    }

    function renderChapters() {
        $('chapters-grid').innerHTML = D.chapters.map(ch => {
            const badge = (ch.available
                ? `<span class="badge badge-live">${T.available}</span>`
                : `<span class="badge badge-soon">${T.comingSoon}</span>`) +
                (ch.selfStudy ? `<span class="badge badge-self">${T.selfStudy}</span>` : '');
            const links = ch.available
                ? ch.links[LANG].map(linkButton).join('')
                : PLACEHOLDER_LINKS.map(t => `<span class="btn disabled" aria-disabled="true">${T.links[t]}</span>`).join('');
            const qn = (ch.quantinar || []).length
                ? `<div class="quantinar-box"><h4><img src="logos/qr_logo.png" alt="">${T.quantinar}</h4><ul>` +
                  ch.quantinar.map(c => `<li><a href="${c.url}" target="_blank" rel="noopener">${esc(c.title)}</a></li>`).join('') +
                  '</ul></div>'
                : '';
            const chart = (D.chapterCharts || {})[ch.id];
            const fig = chart
                ? `<button type="button" class="chapter-chart" data-src="${chart.src}" data-cap="${esc(chart[LANG])}" title="${esc(chart[LANG])}">
                       <img src="${chart.src}" alt="${esc(chart[LANG])}" loading="lazy"></button>`
                : '';
            const fs = (D.formulas || []).filter(f => f.ch === ch.id);
            const formulas = fs.length
                ? `<details class="chapter-formulas"><summary>${T.formulas} (${fs.length})</summary>` +
                  fs.map(f => `<div class="cf"><h5>${f[LANG]}</h5><div class="cf-tex">${f.tex}</div></div>`).join('') +
                  '</details>'
                : '';
            return `<div class="chapter-card${ch.available ? '' : ' soon'}${ch.selfStudy ? ' self-study' : ''}" id="chapter-${ch.id}">
                <div class="chapter-header"><h3>${T.chapter} ${ch.num}: ${ch.title[LANG]}</h3><div class="badges">${badge}</div></div>
                ${fig}
                <div class="chapter-body">
                    <ul>${ch.topics[LANG].map(t => `<li>${t}</li>`).join('')}</ul>
                    ${formulas}
                    <div class="chapter-links">${links}</div>
                    ${qn}
                </div>
            </div>`;
        }).join('');
        $('chapters-grid').querySelectorAll('.chapter-chart').forEach(b => {
            b.onclick = () => openLightbox(b.dataset.src, b.dataset.cap);
        });
    }

    // ------------------------------------------------------------
    // TEAM PROJECT AND AI POLICY
    // ------------------------------------------------------------
    function renderProject() {
        $('project-cards').innerHTML = D.project[LANG].map(c =>
            `<div class="info-card"><h3>${c.h}</h3>${c.p.map(p => `<p>${p}</p>`).join('')}</div>`
        ).join('');
        $('ai-policy').innerHTML = D.aiPolicy[LANG].map(o => `<li>${o}</li>`).join('');
    }

    // ------------------------------------------------------------
    // RESOURCES, CONTACT, FOOTER
    // ------------------------------------------------------------
    function renderResources() {
        $('resources-list').innerHTML = D.resources.map(r =>
            `<a href="${r.href}" class="resource-item" target="_blank" rel="noopener">
                ${r.img ? `<img class="resource-logo" src="${r.img}" alt="">` : `<div class="resource-icon">${r.icon}</div>`}
                <div><strong>${r[LANG][0]}</strong><p>${r[LANG][1]}</p></div>
            </a>`
        ).join('');
        $('data-sources').innerHTML = D.dataSources.map(s =>
            `<li><a href="${s.href}" target="_blank" rel="noopener"><strong>${s.name}</strong></a> - ${s[LANG]}</li>`
        ).join('');
        $('bibliography').innerHTML = D.bibliography.map(b => `<li>${b}</li>`).join('');
    }

    function renderContact() {
        const c = D.contact;
        $('contact-cards').innerHTML =
            `<div class="info-card"><h3>${T.instructor}</h3><p><strong>${c.name}</strong></p>` +
            c[LANG].map(p => `<p>${p}</p>`).join('') +
            `<p style="margin-top:0.6rem"><a href="mailto:${c.email}">${c.email}</a></p></div>` +
            (c.seminar ? `<div class="info-card"><h3>${T.seminarCard}</h3><p><strong>${c.seminar.name}</strong></p><p>${T.seminarRole}</p>` + (c.seminar.email ? `<p style="margin-top:0.6rem"><a href="mailto:${c.seminar.email}">${c.seminar.email}</a></p>` : '') + `</div>` : '') +
            `<div class="info-card"><h3>${T.office}</h3><p>${T.officeText}</p></div>`;
        $('footer-logos').innerHTML = D.footerLogos.map(([href, src, alt]) =>
            `<a href="${href}" target="_blank" rel="noopener"><img src="${src}" alt="${alt}"></a>`
        ).join('');
        $('footer-text').innerHTML = `&copy; 2026 ${T.footer}`;
    }

    // ------------------------------------------------------------
    // GITHUB LOGIN (optional)
    // ------------------------------------------------------------
    function getUser() {
        const raw = store.get('github-user');
        if (!raw) return null;
        try { return JSON.parse(raw); } catch (e) { return null; }
    }

    function renderLogin() {
        const box = $('github-login');
        if (!isConfigured(CFG.GITHUB_CLIENT_ID) || !isConfigured(CFG.APPS_SCRIPT_URL)) {
            box.style.display = 'none';
            return;
        }
        box.style.display = '';
        const user = getUser();
        if (user) {
            box.innerHTML = `<p>${T.loggedAs} <strong>${esc(user.name || user.login)}</strong>
                <button class="btn btn-outline" id="gh-logout" style="margin-left:0.5rem;padding:0.2rem 0.6rem">${T.logout}</button></p>`;
            $('gh-logout').onclick = () => { store.del('github-user'); renderLogin(); };
        } else {
            box.innerHTML = `<p>${T.loginPrompt}</p><button class="btn btn-primary" id="gh-login">${T.loginBtn}</button>`;
            $('gh-login').onclick = loginWithGitHub;
        }
    }

    function loginWithGitHub() {
        store.set('login-return', window.location.href);
        const redirectUri = window.location.origin + window.location.pathname.replace(/[^/]*$/, '') + 'callback.html';
        window.location.href = 'https://github.com/login/oauth/authorize?client_id=' + encodeURIComponent(CFG.GITHUB_CLIENT_ID) +
            '&redirect_uri=' + encodeURIComponent(redirectUri) + '&scope=read:user';
    }

    function sendResults(ch, score, total) {
        if (!isConfigured(CFG.APPS_SCRIPT_URL)) return;
        const user = getUser() || {};
        const payload = {
            nume: user.name || user.login || 'Anonymous',
            github_username: user.login || '',
            grupa: store.get('student-group') || '',
            capitol: 'Chapter ' + ch.num + ' (' + ch.id + ')',
            limba: LANG,
            scor: score + '/' + total,
            total: total,
            nota: Math.round((score / total) * 100) + '%'
        };
        fetch(CFG.APPS_SCRIPT_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(err => console.log('Score submission error:', err));
    }

    // ------------------------------------------------------------
    // QUIZ ENGINE
    // Bank format (assets/quizzes/<id>.js):
    //   MFM_DATA.quizzes['<id>'] = { draw: 20, questions: [
    //     { correct: <index 0-3>, en: {title, text, options:[4], correctExplanation, incorrectExplanation}, ro: {...} } ] }
    // ------------------------------------------------------------
    let quiz = null;   // { chapter: <chapter object>, items: [{ q, order, correctPos }], answers: {} }
    let activeChapter = null;

    function shuffle(arr) {
        const a = arr.slice();
        for (let i = a.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [a[i], a[j]] = [a[j], a[i]];
        }
        return a;
    }

    function renderQuizTabs() {
        $('quiz-tabs').innerHTML = D.chapters.map(ch => {
            const has = !!D.quizzes[ch.id];
            const self = ch.selfStudy ? ` <span class="tab-badge">${T.selfStudy}</span>` : '';
            return `<button class="btn btn-outline${has ? '' : ' unavailable'}${ch.selfStudy ? ' self-study' : ''}" data-ch="${ch.id}" title="${esc(ch.title[LANG])}">Ch ${ch.num}${self}</button>`;
        }).join('');
        $('quiz-tabs').querySelectorAll('button').forEach(b => {
            b.onclick = () => showQuiz(b.getAttribute('data-ch'));
        });
    }

    function showQuiz(id) {
        activeChapter = id;
        $('quiz-tabs').querySelectorAll('button').forEach(b =>
            b.classList.toggle('active', b.getAttribute('data-ch') === id));
        const ch = D.chapters.find(c => c.id === id);
        const bank = D.quizzes[id];
        const box = $('quiz-container');
        const heading = `<h3>${T.chapter} ${ch.num}: ${ch.title[LANG]}${ch.selfStudy ? ` <span class="badge badge-self">${T.selfStudy}</span>` : ''}</h3>`;
        if (!bank) {
            quiz = null;
            box.innerHTML = `${heading}<p class="quiz-intro">${T.quizSoon}</p>`;
            return;
        }
        box.innerHTML = `${heading}
            <p class="quiz-intro">${T.quizIntro}</p>
            <div id="quiz-questions"></div>
            <div class="quiz-actions">
                <button class="btn btn-primary" id="quiz-score">${T.calc}</button>
                <button class="btn btn-outline" id="quiz-reset">${T.reset}</button>
            </div>
            <p class="score-display" id="quiz-score-display" aria-live="polite"></p>
            <div id="quiz-answer-key"></div>`;
        $('quiz-score').onclick = calculateScore;
        $('quiz-reset').onclick = () => showQuiz(id);
        newAttempt(ch, bank);
    }

    function newAttempt(ch, bank) {
        const n = Math.min(bank.draw || 20, bank.questions.length);
        const items = shuffle(bank.questions).slice(0, n).map(q => {
            const order = shuffle(q[LANG].options.map((_, i) => i));   // order[pos] = original option index
            return { q, order, correctPos: order.indexOf(q.correct) };
        });
        quiz = { chapter: ch, items, answers: {} };

        $('quiz-questions').innerHTML = items.map((it, k) => {
            const L = it.q[LANG];
            return `<div class="quiz-question" id="qq${k}">
                <h4>${T.question} ${k + 1}: ${L.title}</h4>
                <p>${L.text}</p>
                <ul class="quiz-options" role="radiogroup">
                    ${it.order.map((orig, pos) =>
                        `<li tabindex="0" role="radio" aria-checked="false" data-k="${k}" data-pos="${pos}">
                            <input type="radio" name="qq${k}" tabindex="-1"> ${LETTERS[pos]}) ${L.options[orig]}</li>`).join('')}
                </ul>
                <div class="answer-reveal answer-correct" id="qq${k}-ok"><strong>${T.correct}</strong> ${L.correctExplanation}</div>
                <div class="answer-reveal answer-incorrect" id="qq${k}-ko"><strong>${T.incorrect}</strong>
                    ${T.correctIs} ${LETTERS[it.correctPos]}) ${L.options[it.q.correct]}. ${L.incorrectExplanation}</div>
            </div>`;
        }).join('');

        $('quiz-questions').querySelectorAll('.quiz-options li').forEach(li => {
            const pick = () => answer(parseInt(li.dataset.k, 10), parseInt(li.dataset.pos, 10));
            li.onclick = pick;
            li.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } };
        });
        typeset($('quiz-container'));
    }

    function answer(k, pos) {
        if (!quiz || quiz.answers[k] !== undefined) return;   // locked after the first answer
        quiz.answers[k] = pos;
        const qDiv = $('qq' + k);
        qDiv.querySelectorAll('.quiz-options li').forEach(li => {
            const mine = parseInt(li.dataset.pos, 10) === pos;
            li.classList.add('locked');
            li.classList.toggle('chosen', mine);
            li.setAttribute('aria-checked', mine ? 'true' : 'false');
            li.querySelector('input').checked = mine;
        });
        const ok = pos === quiz.items[k].correctPos;
        $('qq' + k + '-ok').style.display = ok ? 'block' : 'none';
        $('qq' + k + '-ko').style.display = ok ? 'none' : 'block';
    }

    function calculateScore() {
        if (!quiz) return;
        const total = quiz.items.length;
        let score = 0, answered = 0;
        quiz.items.forEach((it, k) => {
            if (quiz.answers[k] !== undefined) {
                answered++;
                if (quiz.answers[k] === it.correctPos) score++;
            }
        });
        const pct = Math.round((score / total) * 100);
        let msg = `${T.score}: ${score}/${total} (${pct}%)`;
        if (answered < total) msg += ` - ${total - answered} ${T.unanswered}`;
        msg += ' - ' + T.verdicts[pct >= 90 ? 3 : pct >= 70 ? 2 : pct >= 50 ? 1 : 0];
        $('quiz-score-display').textContent = msg;
        sendResults(quiz.chapter, score, total);

        const rows = quiz.items.map((it, k) => {
            const L = it.q[LANG];
            const a = quiz.answers[k];
            const cls = a === undefined ? '' : (a === it.correctPos ? 'ok' : 'ko');
            const res = a === undefined ? '-' : (a === it.correctPos ? '<span class="res-ok">OK</span>' : '<span class="res-ko">X</span>');
            const yours = a === undefined ? '-' : `${LETTERS[a]}) ${L.options[it.order[a]]}`;
            return `<tr class="${cls}"><td class="c"><strong>${k + 1}</strong></td><td>${L.text}</td>
                <td>${LETTERS[it.correctPos]}) ${L.options[it.q.correct]}</td><td>${yours}</td><td class="c">${res}</td></tr>`;
        }).join('');
        $('quiz-answer-key').innerHTML = `<div class="answer-key"><h4>${T.detailed}</h4><table>
            <tr><th class="c">${T.colQ}</th><th>${T.colQuestion}</th><th>${T.colCorrect}</th><th>${T.colYours}</th><th class="c">${T.colResult}</th></tr>
            ${rows}</table></div>`;
        typeset($('quiz-answer-key'));
    }

    // ------------------------------------------------------------
    // INIT
    // ------------------------------------------------------------
    function init() {
        renderStatic();
        renderOverview();
        renderHero();
        initLightbox();
        renderChapters();
        renderProject();
        renderResources();
        renderContact();
        renderLogin();
        renderQuizTabs();
        const first = D.chapters.find(c => D.quizzes[c.id]) || D.chapters[0];
        showQuiz(first.id);
        typeset();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

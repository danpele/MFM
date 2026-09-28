// ============================================================
// MFM site configuration (shared by index.html and index_ro.html)
// GOOGLE_CLIENT_ID: OAuth client (Web) of the Google Cloud project "MFM Quiz Login";
//   the quizzes require "Sign in with Google" with an ASE account.
// QUIZ_SCORES_URL: Google Apps Script web app (tools/quiz_scores.gs, not published)
//   that verifies the Google token and stores the score in a Google Sheet.
// ============================================================
window.MFM_CONFIG = {
    GOOGLE_CLIENT_ID: '1095360272769-rhjjncfor0gumhev6a0l6tnnrnmdrnna.apps.googleusercontent.com',
    QUIZ_SCORES_URL: 'https://script.google.com/macros/s/AKfycbzaF6BMoREZWPCV9hnh0WnabJz-AY2C7ivfcqFazpP6e29PcAC73LmQ2FogMenGrA4iMg/exec'
};

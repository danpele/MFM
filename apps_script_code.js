// ============================================================
// Google Apps Script - Quiz Score Backend (MFM: Modelling Financial Markets)
// Deploy as Web App in Google Apps Script
//
// This handles:
// 1. Receiving quiz scores via POST and storing them in a Google Sheet
// 2. GitHub OAuth token exchange (acting as a proxy to avoid exposing
//    client_secret in the browser)
//
// Setup:
// 1. Create a new Google Apps Script project
// 2. Paste this code
// 3. Set up a GitHub OAuth App (Settings > Developer settings > OAuth Apps)
// 4. Replace GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET below
// 5. Deploy as Web App (Execute as: Me, Who has access: Anyone)
// 6. Copy the deployment URL and the OAuth client ID into assets/config.js
// ============================================================

// appsscript.json manifest (set in Project Settings):
// {
//   "timeZone": "Europe/Bucharest",
//   "dependencies": {},
//   "exceptionLogging": "STACKDRIVER",
//   "oauthScopes": [
//     "https://www.googleapis.com/auth/spreadsheets",
//     "https://www.googleapis.com/auth/script.external_request"
//   ]
// }

// Configuration - Replace with your own values
var GITHUB_CLIENT_ID     = 'YOUR_GITHUB_CLIENT_ID';
var GITHUB_CLIENT_SECRET = 'YOUR_GITHUB_CLIENT_SECRET';

// POST handler - receives quiz results and appends them to the active spreadsheet
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // Create header row if the sheet is empty
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["Name", "GitHub Username", "Group", "Chapter", "Language", "Score", "Total", "Grade", "Date"]);
  }

  var data = JSON.parse(e.postData.contents);

  sheet.appendRow([
    data.nume,
    data.github_username || '',
    data.grupa,
    data.capitol,
    data.limba || '',
    data.scor,
    data.total,
    data.nota,
    new Date().toLocaleString("ro-RO", {timeZone: "Europe/Bucharest"})
  ]);

  return ContentService
    .createTextOutput(JSON.stringify({status: "ok"}))
    .setMimeType(ContentService.MimeType.JSON);
}

// GET handler - status check + GitHub OAuth token exchange
function doGet(e) {
  var params = e.parameter || {};

  // If this is a GitHub auth callback, exchange the code for a token
  if (params.action === 'github_auth' && params.code) {
    return handleGitHubAuth(params.code);
  }

  // Default: health check
  return ContentService
    .createTextOutput(JSON.stringify({status: "ok", message: "Quiz API active"}))
    .setMimeType(ContentService.MimeType.JSON);
}

// GitHub OAuth helper - exchanges authorization code for access token,
// then fetches user profile info
function handleGitHubAuth(code) {
  try {
    // Exchange code for access token
    var tokenResp = UrlFetchApp.fetch('https://github.com/login/oauth/access_token', {
      method: 'post',
      headers: { 'Accept': 'application/json' },
      payload: {
        client_id: GITHUB_CLIENT_ID,
        client_secret: GITHUB_CLIENT_SECRET,
        code: code
      }
    });

    var tokenData = JSON.parse(tokenResp.getContentText());

    if (tokenData.error) {
      return jsonResponse({ error: tokenData.error_description || tokenData.error });
    }

    // Use token to fetch user profile
    var userResp = UrlFetchApp.fetch('https://api.github.com/user', {
      headers: {
        'Authorization': 'Bearer ' + tokenData.access_token,
        'Accept': 'application/json',
        'User-Agent': 'MFM-Quiz-App'
      }
    });

    var user = JSON.parse(userResp.getContentText());

    return jsonResponse({
      login: user.login,
      name: user.name || user.login,
      avatar_url: user.avatar_url
    });

  } catch (err) {
    return jsonResponse({ error: 'Authentication failed: ' + err.message });
  }
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Customer testimonials -> Google Sheet -> website
 * Setup steps: _source/SETUP.md
 *
 * AUTO_APPROVE = false : new feedback is saved in the Sheet; tick the "Approved" box to show it on the website.
 * AUTO_APPROVE = true  : feedback appears on the website immediately (no review).
 */
var AUTO_APPROVE = false;
var NOTIFY_EMAIL = "";            // empty = email goes to the Sheet owner; write "none" to turn emails off
var SHEET_NAME = "Testimonials";
var HEADERS = ["Timestamp", "Name", "Designation", "Company", "Rating", "Message", "Approved"];

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
  }
  return sh;
}

function clean_(v, max) {
  v = String(v || "").replace(/[\u0000-\u001f]+/g, " ").trim().slice(0, max);
  if (/^[=+\-@]/.test(v)) v = "'" + v;   // block spreadsheet formula injection
  return v;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// The website reads approved testimonials from here
function doGet() {
  var sh = sheet_();
  var rows = sh.getLastRow() > 1 ? sh.getRange(2, 1, sh.getLastRow() - 1, HEADERS.length).getValues() : [];
  var out = [];
  for (var i = rows.length - 1; i >= 0; i--) {          // newest first
    var r = rows[i];
    if (r[6] === true && r[5]) {
      out.push({ name: r[1], role: r[2], company: r[3], rating: r[4], message: r[5] });
    }
  }
  return json_({ testimonials: out });
}

// The website feedback form posts here
function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.botcheck) return json_({ ok: false });           // spam bot
  var name = clean_(p.name, 80), msg = clean_(p.message, 1000);
  if (!name || !msg || p.consent !== "yes") return json_({ ok: false, error: "missing" });
  var rating = Math.max(1, Math.min(5, parseInt(p.rating, 10) || 5));

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sh = sheet_();
    sh.appendRow([new Date(), name, clean_(p.role, 80), clean_(p.company, 80), rating, msg, AUTO_APPROVE]);
    var last = sh.getLastRow();
    sh.getRange(last, 7).insertCheckboxes();
    sh.getRange(last, 7).setValue(AUTO_APPROVE);
  } finally {
    lock.releaseLock();
  }

  try {
    var to = NOTIFY_EMAIL || Session.getEffectiveUser().getEmail();
    if (to && to !== "none") {
      MailApp.sendEmail(to, "New testimonial from " + name,
        name + " (" + clean_(p.company, 80) + ") - " + rating + "/5\n\n" + msg + "\n\n" +
        (AUTO_APPROVE ? "Already published on the website." : "Tick 'Approved' in the Sheet to publish it."));
    }
  } catch (err) {}
  return json_({ ok: true });
}

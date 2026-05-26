// Google Apps Script for School Culture Typology App
// Deploy this as a Web App: Execute as "Me", Who has access "Anyone".
// Copy the Web App URL and add it to your Streamlit secrets as APPS_SCRIPT_URL.
// Optional: Set a secret API Key here and in Streamlit secrets as APPS_SCRIPT_API_KEY.

var API_KEY = ""; // Leave blank or set a password/token to restrict access

function checkAuth(e) {
  if (API_KEY === "") return true;
  var key = "";
  if (e.parameter && e.parameter.api_key) {
    key = e.parameter.api_key;
  } else if (e.postData && e.postData.contents) {
    try {
      var data = JSON.parse(e.postData.contents);
      key = data.api_key;
    } catch(err) {}
  }
  return key === API_KEY;
}

function getOrCreateSheets() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  var schoolsSheet = ss.getSheetByName("Schools");
  if (!schoolsSheet) {
    schoolsSheet = ss.insertSheet("Schools");
    schoolsSheet.appendRow(["school_code", "school_name", "password"]);
  }
  
  var resultsSheet = ss.getSheetByName("Results");
  if (!resultsSheet) {
    resultsSheet = ss.insertSheet("Results");
    resultsSheet.appendRow([
      "Timestamp", "School Code", "Toxic", "Fragmented", "Balkanized", 
      "Contrived Collegiality", "Comfortable Collaboration", "Collaborative"
    ]);
  }
  
  return { schools: schoolsSheet, results: resultsSheet };
}

function doGet(e) {
  if (!checkAuth(e)) {
    return ContentService.createTextOutput(JSON.stringify({error: "Unauthorized"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  var action = e.parameter.action;
  var sheets = getOrCreateSheets();
  
  if (action === "get_schools") {
    var data = sheets.schools.getDataRange().getValues();
    var headers = data[0];
    var schools = [];
    for (var i = 1; i < data.length; i++) {
      var row = {};
      for (var j = 0; j < headers.length; j++) {
        row[headers[j]] = String(data[i][j]); // Ensure everything is read as string
      }
      schools.push(row);
    }
    return ContentService.createTextOutput(JSON.stringify(schools)).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (action === "get_results") {
    var data = sheets.results.getDataRange().getValues();
    var headers = data[0];
    var results = [];
    for (var i = 1; i < data.length; i++) {
      var row = {};
      for (var j = 0; j < headers.length; j++) {
        var val = data[i][j];
        if (headers[j] === "Timestamp" || headers[j] === "School Code") {
          row[headers[j]] = String(val);
        } else {
          row[headers[j]] = Number(val);
        }
      }
      results.push(row);
    }
    return ContentService.createTextOutput(JSON.stringify(results)).setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput(JSON.stringify({error: "Invalid Action"})).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  if (!checkAuth(e)) {
    return ContentService.createTextOutput(JSON.stringify({error: "Unauthorized"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  var data = JSON.parse(e.postData.contents);
  var action = data.action;
  var sheets = getOrCreateSheets();
  
  if (action === "save_school") {
    // Check if school already exists to prevent duplicate rows
    var values = sheets.schools.getDataRange().getValues();
    var exists = false;
    for (var i = 1; i < values.length; i++) {
      if (String(values[i][0]) === String(data.school_code)) {
        exists = true;
        // Update password and name if duplicate is sent
        sheets.schools.getRange(i + 1, 2).setValue(data.school_name);
        sheets.schools.getRange(i + 1, 3).setValue(String(data.password));
        break;
      }
    }
    if (!exists) {
      sheets.schools.appendRow([String(data.school_code), data.school_name, String(data.password)]);
    }
    return ContentService.createTextOutput(JSON.stringify({success: true})).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (action === "save_result") {
    sheets.results.appendRow([
      data.Timestamp,
      String(data["School Code"]),
      Number(data.Toxic || 0),
      Number(data.Fragmented || 0),
      Number(data.Balkanized || 0),
      Number(data["Contrived Collegiality"] || 0),
      Number(data["Comfortable Collaboration"] || 0),
      Number(data.Collaborative || 0)
    ]);
    return ContentService.createTextOutput(JSON.stringify({success: true})).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (action === "clear_school_data") {
    var sheet = sheets.results;
    var values = sheet.getDataRange().getValues();
    var rowsDeleted = 0;
    // Iterate backwards when deleting rows to keep indices valid
    for (var i = values.length - 1; i >= 1; i--) {
      if (String(values[i][1]) === String(data.school_code)) {
        sheet.deleteRow(i + 1);
        rowsDeleted++;
      }
    }
    return ContentService.createTextOutput(JSON.stringify({success: true, deleted: rowsDeleted})).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (action === "delete_school_registration") {
    var sheet = sheets.schools;
    var values = sheet.getDataRange().getValues();
    var deleted = false;
    for (var i = values.length - 1; i >= 1; i--) {
      if (String(values[i][0]) === String(data.school_code)) {
        sheet.deleteRow(i + 1);
        deleted = true;
      }
    }
    return ContentService.createTextOutput(JSON.stringify({success: true, deleted: deleted})).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (action === "clear_all_data") {
    // Clear results except header
    var resultsSheet = sheets.results;
    var lastRowResults = resultsSheet.getLastRow();
    if (lastRowResults > 1) {
      resultsSheet.deleteRows(2, lastRowResults - 1);
    }
    // Clear schools except header
    var schoolsSheet = sheets.schools;
    var lastRowSchools = schoolsSheet.getLastRow();
    if (lastRowSchools > 1) {
      schoolsSheet.deleteRows(2, lastRowSchools - 1);
    }
    return ContentService.createTextOutput(JSON.stringify({success: true})).setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput(JSON.stringify({error: "Invalid Action"})).setMimeType(ContentService.MimeType.JSON);
}

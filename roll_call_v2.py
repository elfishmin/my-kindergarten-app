function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var action = e.parameter.action;

  if (action === "get_all_info") {
    var transSheet = ss.getSheetByName("transformat");
    var appSheet = ss.getSheetByName("app2google");
    
    // 一次抓取 A:D 欄 (星期, 班別, 姓名, 才藝班)
    var studentData = transSheet.getRange(2, 1, transSheet.getLastRow() - 1, 4).getValues();
    
    var today = e.parameter.date;
    var appData = appSheet.getRange("A:B").getValues();
    var submitted = [];
    for (var i = appData.length - 1; i > 0; i--) {
      if (appData[i][0] && Utilities.formatDate(new Date(appData[i][0]), "GMT+8", "yyyy-MM-dd") === today) {
        if (submitted.indexOf(appData[i][1]) === -1) submitted.push(appData[i][1]);
      }
    }
    return ContentService.createTextOutput(JSON.stringify({students: studentData, done: submitted})).setMimeType(ContentService.MimeType.JSON);
  }
}

// doPost 保持不變 (負責寫入資料)
function doPost(e) {
  // ... (維持之前的 doPost 代碼)
}

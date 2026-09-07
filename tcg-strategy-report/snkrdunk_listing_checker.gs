/**
 * Google Sheets (カード管理シート) 用 Apps Script
 * B列=カード名, C列=型番, D列=スニダン検索リンク(HYPERLINK数式) を前提に、
 * E列に現在の出品数、F列に「前回チェック時より増えていたら✓」を書き込む。
 *
 * 使い方:
 *   1. 対象のシートを開いた状態でこの関数 checkNewListings を実行する
 *   2. 初回実行時は E列に出品数が入るだけ（F列の✓判定は2回目以降から機能する）
 *   3. トリガー(時計アイコン)で時間主導型トリガーを設定すると自動実行できる
 *
 * 出品数の取得方法:
 *   snkrdunk.com の検索結果ページ(/search?keywords=...)は、Next.jsのSSR初期HTMLに
 *   検索結果そのもの(serverSearchData)がJSONとして埋め込まれている。
 *   これを正規表現で抽出し、タイトルにカード名を含む商品だけの出品数(stockFromGeneralUsers)を合計する。
 *   タイトル一致で絞り込むことで、無関係な商品(ランキング枠等)の数字を拾わないようにしている。
 */

function checkNewListings() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var lastRow = sheet.getLastRow();

  if (sheet.getRange(2, 5).getValue() !== "出品数") {
    sheet.getRange(2, 5).setValue("出品数");
    sheet.getRange(2, 6).setValue("出品増加");
  }

  for (var row = 3; row <= lastRow; row++) {
    var cardName = sheet.getRange(row, 2).getValue(); // B列
    var modelNumber = sheet.getRange(row, 3).getValue(); // C列
    if (!cardName) continue; // 空行はスキップ

    var keyword = cardName;
    if (modelNumber && modelNumber !== "型番無し" && modelNumber !== "(型番なし)") {
      keyword += " " + modelNumber;
    }

    try {
      var url = "https://snkrdunk.com/search?keywords=" + encodeURIComponent(keyword);
      var html = UrlFetchApp.fetch(url, { muteHttpExceptions: true }).getContentText();

      var products = extractProducts_(html);
      var currentStock = sumMatchingStock_(products, cardName);

      var prevStock = sheet.getRange(row, 5).getValue();

      if (currentStock === null) {
        sheet.getRange(row, 5).setValue("該当なし");
        sheet.getRange(row, 6).setValue("");
      } else {
        if (typeof prevStock === "number" && currentStock > prevStock) {
          sheet.getRange(row, 6).setValue("✓");
        } else {
          sheet.getRange(row, 6).setValue("");
        }
        sheet.getRange(row, 5).setValue(currentStock);
      }
    } catch (e) {
      sheet.getRange(row, 6).setValue("エラー");
    }

    Utilities.sleep(1500); // サーバーに負荷をかけすぎないよう待機
  }
}

/**
 * 検索結果ページのHTMLから、商品ごとの {title, stock} を抽出する。
 * フィールドの並び順や種類が商品によって異なっていても拾えるよう、
 * "title" の出現位置を基準に商品の区切りを推定し、その範囲内から
 * stockFromGeneralUsers を探す二段階方式にしている。
 */
function extractProducts_(html) {
  var products = [];
  var titleRegex = /\\"title\\":\\"((?:\\\\.|[^\\"])*?)\\",\\"link\\":\\"([^\\"]*)\\"/g;
  var matches = [];
  var m;
  while ((m = titleRegex.exec(html)) !== null) {
    matches.push({ title: m[1], index: m.index });
  }
  for (var i = 0; i < matches.length; i++) {
    var start = matches[i].index;
    var end = (i + 1 < matches.length) ? matches[i + 1].index : Math.min(html.length, start + 2000);
    var chunk = html.substring(start, end);
    var stockMatch = chunk.match(/\\"stockFromGeneralUsers\\":(\d+)/);
    products.push({
      title: matches[i].title,
      stock: stockMatch ? parseInt(stockMatch[1], 10) : null
    });
  }
  return products;
}

/**
 * カード名がタイトルに含まれる商品だけを対象に、出品数(stockFromGeneralUsers)を合計する。
 * stockFromGeneralUsers は「現在出品中(未売却)」の数なので、
 * 正しい商品にだけ絞り込めれば、売り切れ品の数字は自然と含まれない想定。
 */
function sumMatchingStock_(products, cardName) {
  var total = 0;
  var found = false;
  for (var i = 0; i < products.length; i++) {
    if (products[i].title && products[i].title.indexOf(cardName) !== -1 && products[i].stock !== null) {
      total += products[i].stock;
      found = true;
    }
  }
  return found ? total : null;
}

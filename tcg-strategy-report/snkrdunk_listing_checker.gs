/**
 * Google Sheets (カード管理シート) 用 Apps Script
 * B列=カード名, C列=型番, D列=メルカリ検索リンク, E列=スニダン検索リンク(HYPERLINK数式) を前提に、
 * F列に現在の出品数、G列に「前回チェック時より増えていたら✓」を書き込む。
 * (出品数・出品増加を書き込む列番号は COL_STOCK / COL_FLAG で変更できる)
 *
 * 手動で使う場合:
 *   1. 対象のシートを開いた状態で checkNewListings を実行する
 *   2. 初回実行時は E列に出品数が入るだけ（F列の✓判定は2回目以降から機能する）
 *   3. カードが多いシートは1回の実行(最大6分)では終わらないことがある。
 *      その場合は自動的に途中で止まり、続きの行を記憶しておくので、
 *      もう一度「実行」を押せばその続きから再開する。
 *      最後まで終わったシートは、次に実行するとまた最初の行から始まる。
 *   4. 進捗をリセットして最初からやり直したい場合は resetListingCheckProgress を実行する
 *   5. 複数のシート(ブランドごと)に手動で適用したい場合は、コードは変更せず、
 *      シートを切り替えてから同じ関数を実行し直すだけでよい
 *      (進捗はシートごとに個別に記録されるので、シート間で干渉しない)
 *
 * メルカリ検索列を追加する場合:
 *   addMercariLinkColumn をシートごとに手動実行するとC列とD列の間に列が挿入される
 *   (既存のD/E/F列はE/F/G列にずれる)。トリガーが有効なまま全シート分の作業を
 *   終える前に自動実行が走ると列がズレたままの状態で書き込まれてしまうので、
 *   作業前に一旦トリガーを削除し、全シートの列挿入とCOL_STOCK/COL_FLAGの更新を終えてから
 *   トリガーを設定し直すこと。
 *
 * 自動化する場合(トリガー):
 *   checkNewListingsAllSheets をトリガーに登録すると、
 *   ヘッダー行(2行目)のB列が「カード名」になっている全シートを自動でチェックする。
 *   カードが多いシート(例: ポケモン)だけで実行時間を使い切って他のシートに
 *   順番が回らなくなることがないよう、1シートにつき一度に最大
 *   LISTING_CHECK_ROWS_PER_TURN 件ずつ進める「ラウンドロビン」方式にしている。
 *   1回の実行(最大6分)で全カードを回りきれない場合は、途中で打ち切って
 *   次回の実行(次のトリガー発火時)で続きから再開する。
 *   1日1回だと全カード(900枚近く)を一周するのに数日かかるため、
 *   午前・午後で1日2回トリガーを設定する運用にしている。
 *   トリガーの設定方法:
 *     1. Apps Scriptエディタ左側の時計アイコン「トリガー」を開く
 *     2. 右下の「トリガーを追加」をクリック
 *     3. 実行する関数を選択: checkNewListingsAllSheets
 *     4. イベントのソース: 時間主導型 / 時間ベースのタイマー / 日付ベースのタイマー
 *     5. 時刻を選択(例: 午前8時〜9時)
 *     6. 保存
 *     7. もう一度「トリガーを追加」して、同じ関数で別の時間帯(例: 午後3時〜4時)を追加する
 *   これで1日2回、自動的にE列・F列が更新されるようになる。
 *
 * 対応済みの条件フィルタ調査:
 *   商品の状態(状態A/B/C等)で絞り込んだ在庫数を取ろうとしたが、
 *   状態別の一覧ページ(/apparels/{id}/used?conditionIds=...)はVue.jsで
 *   クライアント側からAPIを呼んで描画する方式のため、
 *   検索結果ページのように初期HTMLに埋め込まれておらず、単純な取得はできなかった。
 *   検索ページ側にconditionIdsを付けても絞り込みは効かないことを確認済み。
 *   そのため出品数は「全ての商品状態を合計した数」として扱う。
 *
 * 出品数の取得方法:
 *   snkrdunk.com の検索結果ページ(/search?keywords=...)は、Next.jsのSSR初期HTMLに
 *   検索結果そのもの(serverSearchData)がJSONとして埋め込まれている。
 *   これを正規表現で抽出し、タイトルにカード名を含む商品だけの出品数(stockFromGeneralUsers)を合計する。
 *   タイトル一致で絞り込むことで、無関係な商品(ランキング枠等)の数字を拾わないようにしている。
 */

var LISTING_CHECK_TIME_BUDGET_MS = 4 * 60 * 1000; // 手動実行1回あたりの打ち切り時間
var LISTING_CHECK_ALL_SHEETS_BUDGET_MS = 5 * 60 * 1000; // トリガー実行1回(全シート合計)の打ち切り時間
var COL_STOCK = 6; // 出品数を書き込む列(F列)
var COL_FLAG = 7; // 出品増加(✓)を書き込む列(G列)

/**
 * 手動実行用: 今開いているシートだけをチェックする。
 */
function checkNewListings() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var deadline = new Date().getTime() + LISTING_CHECK_TIME_BUDGET_MS;
  processSheetBatch_(sheet, deadline);
}

var LISTING_CHECK_ROWS_PER_TURN = 15; // ラウンドロビン1巡で1シートあたり何件進めるか

/**
 * 自動実行(トリガー)用: ヘッダーが「カード名」になっている全シートを、
 * 1シートずつ最後まで終わらせるのではなく、少しずつ・順番に(ラウンドロビン方式で)進める。
 * こうしないと、カード数が多いシート(例: ポケモン)だけで実行時間を使い切ってしまい、
 * 他のシートにいつまでも順番が回ってこなくなるため。
 * 1回の実行時間内に全部終わらなければ、途中で止めて次回のトリガー実行で続きから再開する。
 */
function checkNewListingsAllSheets() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets().filter(function (sheet) {
    return sheet.getRange(2, 2).getValue() === "カード名"; // カード一覧シートだけを対象にする
  });

  var deadline = new Date().getTime() + LISTING_CHECK_ALL_SHEETS_BUDGET_MS;
  var finishedThisRun = {}; // この実行中に最後まで終わったシート(同じ実行中に最初へ巻き戻さないため)

  while (new Date().getTime() < deadline) {
    var progressedAny = false;

    for (var i = 0; i < sheets.length; i++) {
      if (new Date().getTime() > deadline) break;

      var sheet = sheets[i];
      var key = sheet.getSheetId();
      if (finishedThisRun[key]) continue; // このシートはこの実行中にもう完了している

      var completed = processSheetBatch_(sheet, deadline, LISTING_CHECK_ROWS_PER_TURN);
      progressedAny = true;
      if (completed) finishedThisRun[key] = true;
    }

    if (!progressedAny) break; // 対象シートが全部この実行中に完了した
  }
}

/**
 * 指定シートの、前回の続きの行から処理する。
 * deadline(ミリ秒のタイムスタンプ)に達するか、maxRowsThisTurn件処理したら打ち切る。
 * 進捗(どこまで終わったか)はシートごとにドキュメントプロパティへ記録する。
 * 戻り値: シートの最後の行まで到達していれば true、途中で打ち切った場合は false。
 */
function processSheetBatch_(sheet, deadline, maxRowsThisTurn) {
  var lastRow = sheet.getLastRow();
  var props = PropertiesService.getDocumentProperties();
  var progressKey = "SNKR_ROW_" + sheet.getSheetId();
  var startRow = parseInt(props.getProperty(progressKey), 10) || 3;

  if (sheet.getRange(2, COL_STOCK).getValue() !== "出品数") {
    sheet.getRange(2, COL_STOCK).setValue("出品数");
    sheet.getRange(2, COL_FLAG).setValue("出品増加");
  }

  var processedCount = 0;
  var row;
  for (row = startRow; row <= lastRow; row++) {
    if (new Date().getTime() > deadline) break; // 時間切れ
    if (maxRowsThisTurn && processedCount >= maxRowsThisTurn) break; // この巡の件数上限に到達

    var cardName = sheet.getRange(row, 2).getValue(); // B列
    var modelNumber = sheet.getRange(row, 3).getValue(); // C列
    if (!cardName) continue; // 空行はスキップ(件数にはカウントしない)

    var keyword = cardName;
    if (modelNumber && modelNumber !== "型番無し" && modelNumber !== "(型番なし)") {
      keyword += " " + modelNumber;
    }

    try {
      var url = "https://snkrdunk.com/search?keywords=" + encodeURIComponent(keyword);
      var html = UrlFetchApp.fetch(url, { muteHttpExceptions: true }).getContentText();

      var products = extractProducts_(html);
      var currentStock = sumMatchingStock_(products, cardName);

      var prevStock = sheet.getRange(row, COL_STOCK).getValue();

      if (currentStock === null) {
        sheet.getRange(row, COL_STOCK).setValue("該当なし");
        sheet.getRange(row, COL_FLAG).setValue("");
      } else {
        if (typeof prevStock === "number" && currentStock > prevStock) {
          sheet.getRange(row, COL_FLAG).setValue("✓");
        } else {
          sheet.getRange(row, COL_FLAG).setValue("");
        }
        sheet.getRange(row, COL_STOCK).setValue(currentStock);
      }
    } catch (e) {
      sheet.getRange(row, COL_FLAG).setValue("エラー");
    }

    processedCount++;
    Utilities.sleep(1500); // サーバーに負荷をかけすぎないよう待機
  }

  if (row > lastRow) {
    props.deleteProperty(progressKey); // 最後の行まで終わったので、次回はまた最初から
    return true;
  } else {
    props.setProperty(progressKey, String(row)); // ここまで終わったので続きの行を記録
    return false;
  }
}

/**
 * 今開いているシートのC列とD列の間に「メルカリ検索」列を挿入する(1シートずつ手動実行する想定)。
 * 既に追加済みのシートで実行しても何もしない(二重挿入を防ぐ)。
 * 実行後は既存のD/E/F列がE/F/G列にずれるので、
 * COL_STOCK / COL_FLAG が新しい列番号(F=6, G=7)を指すようにしてから使うこと。
 */
function addMercariLinkColumn() {
  var sheet = SpreadsheetApp.getActiveSheet();
  if (sheet.getRange(2, 4).getValue() === "メルカリ検索") {
    return; // 既に追加済み
  }

  sheet.insertColumnBefore(4); // D列の前に挿入(既存のD/E/F列は右に1つずれる)
  sheet.getRange(2, 4).setValue("メルカリ検索");

  var formulaR1C1 =
    '=IF(R[0]C[-2]="","",HYPERLINK("https://jp.mercari.com/search?keyword="&R[0]C[-2]' +
    '&IF(R[0]C[-1]="","", " "&R[0]C[-1])&"&status=on_sale","🛒 検索"))';
  sheet.getRange(3, 4, 998, 1).setFormulaR1C1(formulaR1C1);
}

/**
 * 今開いているシートのD列(メルカリ検索列)の中身を、実際の最終行まで数式で上書きし直す。
 * 手動でのコピー&ペースト等によって、数式ではなく結果の文字列だけになってしまった
 * セルを直したいときに使う(D列の中身は全て上書きされる)。
 */
function refillMercariLinkFormulas() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var lastRow = Math.max(sheet.getLastRow(), 1000);
  var numRows = lastRow - 3 + 1;

  var formulaR1C1 =
    '=IF(R[0]C[-2]="","",HYPERLINK("https://jp.mercari.com/search?keyword="&R[0]C[-2]' +
    '&IF(R[0]C[-1]="","", " "&R[0]C[-1])&"&status=on_sale","🛒 検索"))';
  sheet.getRange(3, 4, numRows, 1).setFormulaR1C1(formulaR1C1);
}

/**
 * 今開いているシートの進捗記録を消して、次の実行を最初の行(3行目)からやり直せるようにする。
 */
function resetListingCheckProgress() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var props = PropertiesService.getDocumentProperties();
  props.deleteProperty("SNKR_ROW_" + sheet.getSheetId());
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

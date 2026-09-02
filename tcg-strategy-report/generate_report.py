import os
from weasyprint import HTML

html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>TCG事業戦略レポート</title>
    <style>
        @page {
            size: A4;
            margin: 20mm 15mm;
            background-color: #f8f9fb;
        }
        body {
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
            color: #2c3e50;
            line-height: 1.6;
            font-size: 11pt;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        *, *::before, *::after {
            box-sizing: border-box;
        }
        /* Header / Title */
        .title-section {
            text-align: center;
            margin-top: 40px;
            margin-bottom: 50px;
        }
        h1 {
            font-size: 24pt;
            color: #1a2b4c;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 12pt;
            color: #7f8c8d;
            border-bottom: 2px solid #d4af37;
            display: inline-block;
            padding-bottom: 10px;
        }
        h2 {
            font-size: 16pt;
            color: #1a2b4c;
            margin-top: 40px;
            border-left: 6px solid #d4af37;
            padding-left: 12px;
            page-break-after: avoid;
        }
        h3 {
            font-size: 13pt;
            color: #34495e;
            margin-top: 25px;
            page-break-after: avoid;
        }
        p {
            margin-bottom: 15px;
        }
        /* Callout boxes */
        .summary-box {
            background-color: #ffffff;
            border: 1px solid #e1e8ed;
            border-top: 4px solid #2980b9;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
            page-break-inside: avoid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .summary-box h3 {
            margin-top: 0;
            color: #2980b9;
        }
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            margin-bottom: 30px;
            background-color: #ffffff;
            font-size: 10pt;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ecf0f1;
            padding: 12px 10px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #1a2b4c;
            color: #ffffff;
            font-weight: bold;
            white-space: nowrap;
        }
        tr {
            page-break-inside: avoid;
        }
        tr:nth-child(even) {
            background-color: #f4f6f9;
        }
        /* Highlights */
        .highlight-red {
            color: #c0392b;
            font-weight: bold;
        }
        .highlight-blue {
            color: #2980b9;
            font-weight: bold;
        }
        .tag-s { background-color: #d4af37; color: #fff; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 9pt;}
        .tag-a { background-color: #7f8c8d; color: #fff; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 9pt;}
        .tag-b { background-color: #bdc3c7; color: #fff; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 9pt;}
        .tag-c { background-color: #ecf0f1; color: #333; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 9pt;}
    </style>
</head>
<body>

    <div class="title-section">
        <h1>TCG事業戦略レポート</h1>
        <div class="subtitle">銘柄別価値分析と鑑定スキームによるキャッシュフロー最適化</div>
    </div>

    <div class="summary-box">
        <h3>エグゼクティブ・サマリー（事業方針の結論）</h3>
        <p>トレーディングカード事業における収益最大化とリスクヘッジの鍵は、<b>「長期資産として価値が保全される銘柄」</b>と<b>「短期的なキャッシュフローを生む高回転銘柄」</b>を明確に切り分け、それぞれに最適な鑑定機関（PSA/ARS）を使い分けることにあります。</p>
        <p>本資料では、TCGプロフェッショナルの視点から、主要10銘柄の歴史的背景に基づく投資根拠と、事業目線での鑑定戦略を定義します。</p>
    </div>

    <h2>1. 主要10銘柄：事業ポートフォリオと投資根拠</h2>
    <p>各銘柄の「歴史と供給ルール」を読み解くことで、数年後の価値残存率を予測することが可能です。事業としての優先度と役割を以下の表に定義します。</p>

    <table>
        <thead>
            <tr>
                <th style="width: 18%;">銘柄</th>
                <th style="width: 10%;">優先度</th>
                <th style="width: 12%;">流動性 / 保全性</th>
                <th style="width: 60%;">価値担保の具体的根拠（なぜ価値が維持・変動するか）</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>マジック：ザ・<br>ギャザリング</b></td>
                <td><span class="tag-s">S (資産)</span></td>
                <td>中 / <b>最高</b></td>
                <td><b>【再録禁止カードによる絶対的供給制限】</b><br>1996年に制定された「Reserved List（再録禁止）」により、ヴィンテージカードは物理的に供給が増えない確約がある。ブラック・ロータス等は金や高級時計と同等の富裕層向け実物資産として機能しており、暴落リスクが極めて低い。</td>
            </tr>
            <tr>
                <td><b>ポケモンカード</b></td>
                <td><span class="tag-s">S (基軸)</span></td>
                <td><b>最高</b> / 高</td>
                <td><b>【世界最大のIP力と周年サイクルの定着】</b><br>世界総収益1位のIP力。「かいりきリザードン」等の旧裏面カードの歴史的価値に加え、25周年等の節目ごとに過去のプロモカードが再評価されるサイクルが市場に根付いている。言語を問わずグローバルな流動性を持つ事業の主軸。</td>
            </tr>
            <tr>
                <td><b>遊戯王OCG</b></td>
                <td><span class="tag-a">A (安定)</span></td>
                <td>高 / 高</td>
                <td><b>【コレクター層の成熟と美品の枯渇】</b><br>1999年の初期カードや「レリーフ（アルティメットレア）」。当時のプレイヤーが30〜40代の資金力ある層へ成長。20年以上前のカードゆえに状態の良い個体（PSA9〜10）が市場から枯渇しており、価格の底値が極めて固い。</td>
            </tr>
            <tr>
                <td><b>ワンピースカード</b></td>
                <td><span class="tag-a">A (高回転)</span></td>
                <td><b>最高</b> / 中</td>
                <td><b>【極端な低封入率による初動の高騰】</b><br>アジア圏での爆発的プレイヤー人口。「コミックパラレル」等の極端な低封入率により初動価格が高騰しやすい。ただし歴史が浅いため数十年単位での価値安定性は未検証であり、短期売買でのキャッシュ獲得銘柄として扱うべき。</td>
            </tr>
            <tr>
                <td><b>ディズニー ロルカナ</b></td>
                <td><span class="tag-b">B (投資)</span></td>
                <td>中 / 高</td>
                <td><b>【究極のコレクターIPによる将来性】</b><br>コレクターIPとして最強のディズニー。北米・欧州での需要が先行しており、将来的なヴィンテージ化（1st Chapter等）を見越した中長期の先行投資銘柄。海外バイヤー向けの有力商材。</td>
            </tr>
            <tr>
                <td><b>ドラゴンボール</b></td>
                <td><span class="tag-b">B (海外)</span></td>
                <td>中 / 中〜高</td>
                <td><b>【グローバル需要と円安の恩恵】</b><br>欧米・南米での絶大なキャラクター人気。特定キャラクターのパラレルレア等に対し、海外バイヤーによる円安を活かしたまとめ買いが起きやすく、越境EC（eBay等）と相性が良い。</td>
            </tr>
            <tr>
                <td><b>ヴァイスシュヴァルツ</b></td>
                <td><span class="tag-b">B (一撃性)</span></td>
                <td>高 / 低〜中</td>
                <td><b>【ファン層の熱狂と熱の冷却】</b><br>アニメ・VTuberの熱狂的ファン層が牽引。トップレアの箔押しサイン（SSP）は初動数十万をつけるが、再販やコンテンツの熱の冷却で下落しやすいため、長期保有は避け素早い売り抜けが必須。</td>
            </tr>
            <tr>
                <td><b>デュエル・マスターズ</b></td>
                <td><span class="tag-c">C (国内型)</span></td>
                <td>高 / 中</td>
                <td><b>【実用需要偏重の国内市場】</b><br>一部の初期プロモ（ボルメテウス等）を除き、対戦環境（Tier）による価格変動が主。鑑定を通さず、シングルカードとして素早く回転させるべき銘柄。</td>
            </tr>
            <tr>
                <td><b>ユニオンアリーナ</b></td>
                <td><span class="tag-c">C (短期型)</span></td>
                <td>中 / 低</td>
                <td><b>【新規参入IPの初動依存】</b><br>参戦IP（HUNTER×HUNTER等）のファンによる初動買いが中心。長期的ホールドは避け、発売直後のトレンドに乗った利確を徹底する。</td>
            </tr>
            <tr>
                <td><b>ヴァンガード</b></td>
                <td><span class="tag-c">C (実用型)</span></td>
                <td>中 / 低</td>
                <td><b>【プレイヤー需要特化】</b><br>コレクションよりもゲーム実用性が価格の源泉。高額な鑑定費用をかけると利益率を圧迫するため、鑑定事業としての優先度は低い。</td>
            </tr>
        </tbody>
    </table>


    <h2>2. 鑑定機関の戦略的使い分け（資金拘束リスクの管理）</h2>
    <p>カードを鑑定に出すという行為は、事業目線で見れば<b>「鑑定完了まで在庫（キャッシュ）が固定される期間」</b>を意味します。利ざやだけでなく「資金の回転率」から逆算した機関の選定が不可欠です。</p>

    <div class="summary-box">
        <h3>🔴 PSA (Professional Sports Authenticator)</h3>
        <p><b>【役割】価値の最大化とグローバル流動性の担保（長期ホールド向け）</b></p>
        <p>「PSA10」という状態そのものが世界共通の金融指標として機能します。eBay等を通じて海外富裕層へ高値で販売できる圧倒的なブランド力があります。</p>
        <p><span class="highlight-red">【事業的リスクと対策】</span><br>
        世界中から依頼が殺到するため、納期が数ヶ月遅れるリスクが常態化しています。つまり、<b>数ヶ月間キャッシュが寝る</b>ことになります。<br>
        そのためPSA鑑定は、相場が急落しにくい<b>「MTGの再録禁止カード」「ポケモンの旧裏・限定プロモ」「遊戯王の初期レリーフ」</b>など、数年単位で価値が落ちない確固たる根拠を持つ銘柄に絞って投入すべきです。</p>
    </div>

    <div class="summary-box">
        <h3>🔵 ARS (ARS 鑑定)</h3>
        <p><b>【役割】正確な納期による資金の高速回転（短期キャッシュフロー向け）</b></p>
        <p>ケースの圧倒的な審美性と厳格なグレーディングにより、国内コレクター間で「PSA10以上の付加価値」を持つケースが増加しています。</p>
        <p><span class="highlight-blue">【最大のビジネスメリット】</span><br>
        事業上最も優れた点は<b>「鑑定日数の正確さ」</b>です。予定通りに仕上がり手元に戻るため、キャッシュフローの計画が極めて立てやすくなります。<br>
        相場変動が激しい<b>「ワンピース」や「ヴァイスシュヴァルツ」の最新トップレア</b>などを最速でパッケージ化し、相場の熱が冷めて価格が下落する前に市場へ流して確実にキャッシュを回収する用途に最適です。</p>
    </div>

    <h2>3. 結論：推奨される事業ポートフォリオ</h2>
    <p>TCG市場における相場下落リスク（バブル崩壊リスク）を最小限に抑えるためには、以下のハイブリッド戦略を推奨します。</p>
    <ul>
        <li><b>ベース収益の確保（高回転・ARS活用）：</b> ワンピース等の最新弾を発売直後に仕入れ、ARSの正確な納期を活かして付加価値をつけて短期売却。日々の運転資金を稼ぐ。</li>
        <li><b>利益の資産化（長期保有・PSA活用）：</b> 短期で得た利益の一部を、歴史的背景に裏打ちされたMTG（再録禁止）やポケモン（旧プロモ）に再投資。PSAへ提出し、数ヶ月の鑑定待ちを許容しながらグローバル資産としての価値を確定させる。</li>
    </ul>

</body>
</html>
"""

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

html_path = os.path.join(OUTPUT_DIR, "TCG_Business_Strategy_Report.html")
pdf_path = os.path.join(OUTPUT_DIR, "TCG_Business_Strategy_Report.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

HTML(html_path).write_pdf(pdf_path)
print(f"[file-tag: {pdf_path}]")

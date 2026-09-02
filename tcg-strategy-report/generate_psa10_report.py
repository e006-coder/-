import os
from weasyprint import HTML

html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>PSA10鑑定品 相場調査資料</title>
    <style>
        @page {
            size: A4;
            margin: 20mm 15mm;
            background-color: #f8f9fb;
            @bottom-center {
                content: counter(page) " / " counter(pages);
                font-size: 9pt;
                color: #8b93a3;
            }
        }
        body {
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
            color: #2c3e50;
            line-height: 1.6;
            font-size: 10.5pt;
            margin: 0;
            padding: 0;
        }
        *, *::before, *::after { box-sizing: border-box; }

        .title-section {
            text-align: center;
            margin-top: 30px;
            margin-bottom: 40px;
        }
        h1 {
            font-size: 23pt;
            color: #1a2b4c;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 11.5pt;
            color: #7f8c8d;
            border-bottom: 2px solid #d4af37;
            display: inline-block;
            padding-bottom: 10px;
        }
        .meta-line {
            margin-top: 14px;
            font-size: 9.5pt;
            color: #8b93a3;
        }

        h2 {
            font-size: 15pt;
            color: #1a2b4c;
            margin-top: 34px;
            border-left: 6px solid #d4af37;
            padding-left: 12px;
            page-break-after: avoid;
        }
        h3 {
            font-size: 12pt;
            color: #34495e;
            margin-top: 20px;
            page-break-after: avoid;
        }
        p { margin-bottom: 12px; }

        .caveat-box {
            background-color: #fff8ec;
            border: 1px solid #eadfc4;
            border-left: 4px solid #d4af37;
            padding: 16px 18px;
            margin: 18px 0;
            border-radius: 4px;
            page-break-inside: avoid;
        }
        .caveat-box h3 { margin-top: 0; color: #a9781f; font-size: 11.5pt; }
        .caveat-box ul { margin: 8px 0 0; padding-left: 18px; }
        .caveat-box li { margin-bottom: 6px; }

        .summary-box {
            background-color: #ffffff;
            border: 1px solid #e1e8ed;
            border-top: 4px solid #2980b9;
            padding: 16px 18px;
            margin: 16px 0;
            border-radius: 4px;
            page-break-inside: avoid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .summary-box h3 { margin-top: 0; color: #2980b9; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 14px;
            margin-bottom: 22px;
            background-color: #ffffff;
            font-size: 9pt;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ecf0f1;
            padding: 8px 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #1a2b4c;
            color: #ffffff;
            font-weight: bold;
            white-space: nowrap;
        }
        tr { page-break-inside: avoid; }
        tr:nth-child(even) { background-color: #f4f6f9; }
        .num { text-align: right; white-space: nowrap; }

        .overview-table th, .overview-table td { font-size: 9.5pt; }
        .status-ok { color: #1e8449; font-weight: bold; }
        .status-zero { color: #c0392b; font-weight: bold; }

        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 8pt;
            font-weight: bold;
            white-space: nowrap;
        }
        .b-in { background-color: #eafaf1; color: #1e8449; border: 1px solid #a9dfbf; }
        .b-edge { background-color: #fef5e7; color: #b9770e; border: 1px solid #f5cba7; }
        .b-ref { background-color: #f4f6f7; color: #707b7c; border: 1px solid #d5dbdb; }

        .no-data {
            background-color: #fdf2f0;
            border: 1px solid #f0d4cf;
            border-left: 4px solid #c0392b;
            padding: 14px 16px;
            border-radius: 4px;
            margin: 14px 0;
        }
        .no-data h4 { margin: 0 0 8px; color: #a93226; font-size: 11pt; }
        .no-data p { margin: 0; font-size: 9.5pt; }

        .source-note { font-size: 8.5pt; color: #8b93a3; margin-top: -14px; margin-bottom: 18px; }

        footer.doc-footer {
            margin-top: 40px;
            font-size: 8.5pt;
            color: #95a5a6;
            border-top: 1px solid #ecf0f1;
            padding-top: 10px;
        }
    </style>
</head>
<body>

    <div class="title-section">
        <h1>PSA10鑑定品 相場調査資料</h1>
        <div class="subtitle">6大TCG・25万円〜40万円帯の該当銘柄リサーチ</div>
        <div class="meta-line">調査基準日：2026年9月2日　/　対象：ポケモンカード・ワンピースカード・遊戯王OCG・ドラゴンボール・デュエルマスターズ・ヴァイスシュヴァルツ</div>
    </div>

    <div class="caveat-box">
        <h3>本資料の前提と限界（必読）</h3>
        <ul>
            <li>本調査は、メルカリ・スニーカーダンク・ヤフオク!・カードラッシュへの<b>直接アクセスができない環境</b>で実施しました。これらのサイトの実売データを直接取得することはできず、Web検索経由でヒットした二次情報（各サイトの相場集計ページ・店舗の買取告知・オークション実績の要約等）を積み重ねて作成しています。</li>
            <li>相場は各出典に記載の時点（2026年4月〜9月頭）のものであり、「直近1〜2週間の平均」という厳密な定義には必ずしも一致しません。特に日付の古いデータは、上昇トレンドの銘柄ではすでに範囲を超えている可能性があります。</li>
            <li>「確定」は複数の手がかりから25万円〜40万円に該当すると判断したもの、「参考」はごく僅かに範囲外だが動向として注視価値があるものです。</li>
            <li>実際の仕入れ・鑑定判断の前には、必ず該当サイトで現物の出品状況をご自身でご確認ください。</li>
        </ul>
    </div>

    <h2>1. 調査結果サマリー</h2>
    <table class="overview-table">
        <thead>
            <tr>
                <th>TCG</th>
                <th class="num">確定件数</th>
                <th class="num">参考件数</th>
                <th>状況</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>ポケモンカード</td><td class="num">4</td><td class="num">4</td><td class="status-ok">調査完了</td></tr>
            <tr><td>ワンピースカード</td><td class="num">3</td><td class="num">0</td><td class="status-ok">調査完了</td></tr>
            <tr><td>遊戯王OCG（+ラッシュデュエル参考1件）</td><td class="num">2</td><td class="num">1</td><td class="status-ok">調査完了</td></tr>
            <tr><td>ドラゴンボール（フュージョンワールド）</td><td class="num">0</td><td class="num">0</td><td class="status-zero">該当なし</td></tr>
            <tr><td>デュエルマスターズ</td><td class="num">0</td><td class="num">1</td><td class="status-zero">該当なし</td></tr>
            <tr><td>ヴァイスシュヴァルツ</td><td class="num">1</td><td class="num">0</td><td class="status-ok">調査完了</td></tr>
        </tbody>
    </table>

    <div class="summary-box">
        <h3>分かったこと</h3>
        <p>ポケモンカード・ワンピースカード・遊戯王OCGでは、「有名な超高額プロモ（50万円〜数百万円）」と「量産チェイスカード（多くは15万円以下）」の谷間に、25万円〜40万円のカードが実在しました（2020年代前半のSA/SAR系イラストレア、初期の絶版アルティメットレア、コミックパラレルなど）。<br>
        一方、ドラゴンボール（フュージョンワールド）とデュエルマスターズは、この価格帯が構造的に薄いことが分かりました。ドラゴンボールは最高レアリティ（SCR★★）が一気に40万〜50万円超に跳ね上がり、その一段下（SCR★）は数万円台に落ちるため中間層がほぼ存在しません。デュエルマスターズは高額帯がトーナメント優勝プロモ（数十万〜数百万円、PSA鑑定に出す例が少ない）に偏っており、一般流通のPSA10鑑定品は数万円〜20万円程度に留まる傾向でした。</p>
    </div>

    <h2>2. ポケモンカード</h2>
    <p class="source-note">主な参照元：ポケカチ（altema.jp）、カードラッシュ、スニーカーダンク</p>
    <table>
        <thead>
            <tr>
                <th style="width:20%;">カード名</th>
                <th style="width:24%;">型番・収録パック</th>
                <th class="num" style="width:14%;">相場目安</th>
                <th style="width:10%;">判定</th>
                <th style="width:32%;">備考</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>ギラティナV(SA)</td><td>ロストアビス[S11] 111/100</td><td class="num">375,000円</td><td><span class="badge b-in">範囲内</span></td><td>1ヶ月前34万円から上昇傾向（2026/8/12時点）。</td></tr>
            <tr><td>ゲンガーVMAX(SA)</td><td>ハイクラスデッキ「ゲンガーVMAX」[SGG] 020/019</td><td class="num">390,000円</td><td><span class="badge b-in">範囲内</span></td><td>スニダンでは42万円台の出品例あり（2026/7/24時点）。</td></tr>
            <tr><td>Nのゾロアークex(UR・エラー版)</td><td>バトルパートナーズ[SV9] 131/100</td><td class="num">270,000円</td><td><span class="badge b-in">範囲内</span></td><td>通常版URは1万円前後だがエラー版のみ高額。</td></tr>
            <tr><td>ファイヤー(カードe)</td><td>{013/T}</td><td class="num">298,000円</td><td><span class="badge b-in">範囲内</span></td><td>カードラッシュ販売価格（1点在庫、状態難注記あり）。</td></tr>
            <tr><td>ニンフィアVMAX(SA)</td><td>イーブイヒーローズ[S6a] 093/069</td><td class="num">233,000〜244,000円</td><td><span class="badge b-edge">参考</span></td><td>僅かに下限未満。買取相場は128,000円。</td></tr>
            <tr><td>ピカチュウ(ソードシールドプロモ)</td><td>{001/S-P}</td><td class="num">210,000〜219,000円</td><td><span class="badge b-ref">参考</span></td><td>下限未満。緩やかに下落傾向。</td></tr>
            <tr><td>ライチュウ&アローラライチュウGX(SA)</td><td>ウルトラフォース[SM10a] 057/054</td><td class="num">約201,000円</td><td><span class="badge b-ref">参考</span></td><td>2026/4/19時点のデータ。上昇トレンドで現在はより高い可能性。</td></tr>
            <tr><td>ミュウVMAX(SA)</td><td>フュージョンアーツ[S8] 119/100</td><td class="num">248,000円</td><td><span class="badge b-edge">参考</span></td><td>僅かに下限未満。今後範囲入りの可能性。</td></tr>
        </tbody>
    </table>

    <h2>3. ワンピースカード</h2>
    <p class="source-note">主な参照元：ワンピカチ（altema.jp）</p>
    <table>
        <thead>
            <tr>
                <th style="width:20%;">カード名</th>
                <th style="width:24%;">型番・収録パック</th>
                <th class="num" style="width:14%;">相場目安</th>
                <th style="width:10%;">判定</th>
                <th style="width:32%;">備考</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>【金色】シャンクス 3周年SP</td><td>受け継がれる意志[OP09] OP09-004</td><td class="num">275,000円</td><td><span class="badge b-in">範囲内</span></td><td>発売から時間が経過し希少性が上昇。</td></tr>
            <tr><td>ナミ(パラレル)</td><td>神の島の冒険[OP15] OP15-086</td><td class="num">373,000円</td><td><span class="badge b-in">範囲内</span></td><td>初のウェディング衣装イラストで人気。</td></tr>
            <tr><td>ボア・ハンコック(コミパラ)</td><td>500年後の未来[OP07] OP07-051</td><td class="num">300,000〜310,000円</td><td><span class="badge b-in">範囲内</span></td><td>女性キャラ初のコミックパラレル。</td></tr>
        </tbody>
    </table>

    <h2>4. 遊戯王OCG</h2>
    <p class="source-note">主な参照元：複数店舗の買取告知、Yahoo!オークション落札実績</p>
    <table>
        <thead>
            <tr>
                <th style="width:20%;">カード名</th>
                <th style="width:24%;">型番・収録パック</th>
                <th class="num" style="width:14%;">相場目安</th>
                <th style="width:10%;">判定</th>
                <th style="width:32%;">備考</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>真紅眼の黒竜(レリーフ/アルティメットレア)</td><td>新たなる支配者 301-056</td><td class="num">310,000〜330,000円</td><td><span class="badge b-in">範囲内</span></td><td>2002年発売・絶版で希少性が高い。</td></tr>
            <tr><td>ブラック・マジシャン(レリーフ)</td><td>Labyrinth of Nightmare -悪夢の迷宮- LN-53</td><td class="num">270,000円</td><td><span class="badge b-in">範囲内</span></td><td>ヤフオク!落札実績（39件入札）。状態により変動大。</td></tr>
            <tr><td>ブラック・マジシャン・ガール(オーバーラッシュレア)<br><span style="color:#8b93a3;font-size:8pt;">※本家OCGではなくラッシュデュエル</span></td><td>オーバーラッシュパック2 RD/ORP2-JP001</td><td class="num">400,000円</td><td><span class="badge b-edge">範囲上限</span></td><td>1店舗のX告知ベース。範囲ぎりぎり上限。</td></tr>
        </tbody>
    </table>

    <h2>5. ドラゴンボール（フュージョンワールド）</h2>
    <div class="no-data">
        <h4>25万円〜40万円帯：該当カードなし</h4>
        <p>最高レアリティ「SCR★★（スーパーシークレットパラレル）」は人気キャラクターで軒並み40万〜50万円超（例：孫悟空 SCR★★ 約498,000円、孫悟飯:少年期 SCR★★ 約448,000円）。一方その一段下の「SCR★」は数千円〜数万円台に留まり、25万円〜40万円の中間帯が構造的に存在しませんでした。また、遊戯王・ポケカ・ワンピのような専門のPSA10相場集計サイトも見当たらず、素体の買取価格・ARS鑑定・PSA鑑定の情報が混在しており、精度の高い裏付けが取れませんでした。</p>
    </div>

    <h2>6. デュエルマスターズ</h2>
    <div class="no-data">
        <h4>25万円〜40万円帯：確定候補なし</h4>
        <p>高額帯はトーナメント優勝配布プロモ（例：勝利宣言 鬼丸覇 40万〜99万円、伝説の禁断 ドキンダムX 50万〜99万円）に集中していますが、これらは市場流通が極端に少なくPSA鑑定に出された実例も確認できませんでした。一般流通する初期の希少カードでは「無双竜機ボルバルザーク」がPSA10で約200,000円という事例が見つかりましたが、範囲のわずかに下でした。</p>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width:20%;">カード名</th>
                <th style="width:24%;">型番・収録パック</th>
                <th class="num" style="width:14%;">相場目安</th>
                <th style="width:10%;">判定</th>
                <th style="width:32%;">備考</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>無双竜機ボルバルザーク（参考）</td><td>DM10 9/110</td><td class="num">約200,000円</td><td><span class="badge b-ref">参考</span></td><td>範囲下限未満。単一事例ベース。</td></tr>
        </tbody>
    </table>

    <h2>7. ヴァイスシュヴァルツ</h2>
    <p class="source-note">主な参照元：カードショップの買取表告知（X/旧Twitter）</p>
    <table>
        <thead>
            <tr>
                <th style="width:20%;">カード名</th>
                <th style="width:24%;">型番・収録パック</th>
                <th class="num" style="width:14%;">相場目安</th>
                <th style="width:10%;">判定</th>
                <th style="width:32%;">備考</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>アニス：スパークリングサマー(サイン入り/SEC+)</td><td>勝利の女神：NIKKE NIK/S117-002EX</td><td class="num">250,000円</td><td><span class="badge b-edge">範囲内(下限)</span></td><td>同じ買取表内の他カードは19万〜23万円で僅かに範囲外。</td></tr>
        </tbody>
    </table>

    <footer class="doc-footer">
        本資料はWeb検索経由で取得した二次情報を基に作成した参考資料であり、PSA公式の母集団統計や各プラットフォームの公式APIデータではありません。投資・仕入れの判断材料とする場合は、必ず出典元での現物確認を行ってください。
    </footer>

</body>
</html>
"""

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(OUTPUT_DIR, "PSA10_Market_Research_Report.html")
pdf_path = os.path.join(OUTPUT_DIR, "PSA10_Market_Research_Report.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

HTML(html_path).write_pdf(pdf_path)
print(f"[file-tag: {pdf_path}]")

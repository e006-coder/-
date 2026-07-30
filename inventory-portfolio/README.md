# 在庫ポートフォリオ管理

スニダン等の転売在庫を4象限（流動性×収益性）で管理するためのExcel運用テンプレート。

## 使い方

`在庫ポートフォリオ管理.xlsx` を開き、まず「使い方」シートを読んでください。以下の7シートで構成されています。

1. **使い方** — シート構成、入力ルール（色分け）、使い始め方
2. **設定** — 4象限のしきい値、カテゴリ／レアリティ／ステータスのマスタ、集中リスク集計用のキャラ・イラストレーターリスト
3. **ウォッチリスト** — 未仕入れの銘柄を登録すると自動で4象限に振り分け
4. **仕入れ計画** — 象限別の上限単価・許容属性・月間予算配分
5. **在庫管理** — 実在庫を4分類＋タグで登録し、ポートフォリオ比率を自動計算
6. **ダッシュボード** — 資本効率（GMROI・回転率・ROI）、実行流動性、集中リスク（HHI）を自動集計・グラフ表示
7. **スケジュール** — 8月本格運用に向けたタスクとスケジュール

## サマリーPDF・Obsidianノート

`docs/` に、全体像をまとめたシンプルなサマリーPDFと、Obsidian用のMarkdownノートがあります。

- `docs/在庫ポートフォリオ管理_サマリー.pdf` — 4象限フレームワーク・仕入れ計画・在庫管理・ダッシュボードKPIの要点＋8/3〜9/2の詳細スケジュール
- `docs/obsidian/在庫ポートフォリオ管理.md` — 上記サマリーのObsidianノート版（Vaultにコピーして使用）
- `docs/obsidian/スケジュール_8月.md` — 8/3〜9/2の日次・時間帯別タスク（チェックボックス付き）

再生成: `python3 docs/build_schedule.py`（`docs/summary.html` を元に `docs/summary_full.html` を生成し、Chromiumヘッドレスで印刷）。

```bash
python3 docs/build_schedule.py
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf="docs/在庫ポートフォリオ管理_サマリー.pdf" "file://$(pwd)/docs/summary_full.html"
```

## 再生成

ワークブックは `scripts/build_workbook.py`（openpyxl）から生成しています。レイアウトやしきい値のロジックを変更する場合はこのスクリプトを編集し、再実行してください。

```bash
python3 scripts/build_workbook.py
# 数式の再計算（LibreOffice必須）
python3 <xlsxスキルのscripts>/recalc.py 在庫ポートフォリオ管理.xlsx
```

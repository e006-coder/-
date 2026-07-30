#!/usr/bin/env python3
"""Generate the resale inventory portfolio management workbook.

Builds 在庫ポートフォリオ管理.xlsx with 7 sheets:
使い方 / 設定 / ウォッチリスト / 仕入れ計画 / 在庫管理 / ダッシュボード / スケジュール

Run: python3 build_workbook.py
Then: python3 <xlsx-skill>/scripts/recalc.py ../在庫ポートフォリオ管理.xlsx
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, DataBarRule
from openpyxl.chart import PieChart, BarChart, Reference
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "在庫ポートフォリオ管理.xlsx")

FONT_NAME = "Yu Gothic"

BLUE = Font(name=FONT_NAME, size=10, color="0000FF")
BLACK = Font(name=FONT_NAME, size=10, color="000000")
GREEN = Font(name=FONT_NAME, size=10, color="008000")
BOLD = Font(name=FONT_NAME, size=10, bold=True)
BOLD_WHITE = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
TITLE = Font(name=FONT_NAME, size=16, bold=True, color="1F4E78")
SECTION = Font(name=FONT_NAME, size=11, bold=True, color="1F4E78")
NOTE = Font(name=FONT_NAME, size=9, italic=True, color="666666")

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
TODO_FILL = PatternFill("solid", fgColor="FCE4D6")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

CUR = '¥#,##0;[RED]-¥#,##0;"-"'
PCT = '0.0%;[RED]-0.0%;"-"'
INT = '#,##0;[RED]-#,##0;"-"'
DATE = "yyyy/mm/dd"

wb = openpyxl.Workbook()
wb.remove(wb.active)


def sheet(name):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    return ws


def title(ws, cell, text):
    ws[cell] = text
    ws[cell].font = TITLE


def note(ws, cell, text):
    ws[cell] = text
    ws[cell].font = NOTE


def section(ws, cell, text):
    ws[cell] = text
    ws[cell].font = SECTION
    ws[cell].fill = SECTION_FILL


def header_row(ws, row, col_start, labels):
    for i, label in enumerate(labels):
        c = ws.cell(row=row, column=col_start + i, value=label)
        c.font = BOLD_WHITE
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER


def set_col_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def style_row(ws, row, col_start, col_end, font=BLACK, fmt=None, fill=None, align=None):
    for col in range(col_start, col_end + 1):
        c = ws.cell(row=row, column=col)
        c.font = font
        c.border = BORDER
        if fmt:
            c.number_format = fmt
        if fill:
            c.fill = fill
        if align:
            c.alignment = align


# =====================================================================
# 1. 使い方
# =====================================================================
ws = sheet("使い方")
set_col_widths(ws, [4, 100])
title(ws, "B2", "在庫ポートフォリオ管理ブック")
note(ws, "B3", "スニダン等の転売在庫を4象限で管理するための運用テンプレートです。")

rows = [
    ("■ シート構成", None),
    ("設定", "4象限のしきい値、カテゴリ／レアリティ／ステータスのマスタ、集中リスク集計用のキャラ・イラストレーターリストを管理します。まずこのシートを事業実態に合わせて調整してください。"),
    ("ウォッチリスト", "スニダン等で気になっている未仕入れの銘柄を登録すると、想定売却日数と想定粗利率から自動で4象限に振り分けます（実務タスク1）。"),
    ("仕入れ計画", "象限ごとに「何を・いくらまで・どの属性なら仕入れてよいか」のルールと月間予算配分を定義します（実務タスク2）。"),
    ("在庫管理", "実在庫を4分類＋タグ（キャラ／イラストレーター／絶版／周年／レアリティ）で登録し、ポートフォリオ比率を自動計算します（実務タスク3）。"),
    ("ダッシュボード", "資本効率（在庫回転率・GMROI・ROI）と実行流動性（換金可能比率・滞留比率）、集中リスク（HHI）を自動集計します（実務タスク4）。"),
    ("スケジュール", "8月の本格運用に向けたタスクとスケジュールです（実務タスク5）。"),
    ("■ 入力ルール（色分け）", None),
    ("青字", "手入力セル。実データに置き換えてください。"),
    ("黄色背景", "しきい値・予算など、事業判断が必要な重要な前提値。"),
    ("オレンジ背景", "担当者未アサインなど、要記入の項目。"),
    ("黒字", "自動計算セル。数式が入っているため直接編集しないでください。"),
    ("緑字", "他シートを参照しているセル。"),
    ("■ 使い始め方", None),
    ("Step1", "「設定」シートでカテゴリ・レアリティ・4象限しきい値を確認・調整する。"),
    ("Step2", "「ウォッチリスト」にスニダンのウォッチリスト登録分を入力し、象限分布を確認する。"),
    ("Step3", "「仕入れ計画」で象限別の上限単価・許容属性・予算配分を確定する。"),
    ("Step4", "「在庫管理」に実在庫を棚卸し登録し、ポートフォリオ比率と集中リスクを確認する。"),
    ("Step5", "「ダッシュボード」を週次で確認し、「スケジュール」に沿って運用を回す。"),
    ("■ 注意事項", None),
    ("サンプル行", "各シートの数行はサンプル値です。実データ入力時は上書き、または不要なら内容を削除してください（数式は残しても構いません）。"),
    ("集中リスク(HHI)", "HHI = Σ(構成比^2)×10,000。目安：1,500未満＝分散、1,500〜2,500＝中程度、2,500以上＝集中リスク高（米国の産業集中度評価で一般的に使われる区分を援用）。"),
]

r = 5
for label, desc in rows:
    if desc is None:
        section(ws, f"B{r}", label)
        r += 1
        continue
    ws[f"B{r}"] = f"　{label}：{desc}" if not label.startswith("Step") else f"　{label}：{desc}"
    ws[f"B{r}"].font = BLACK
    ws[f"B{r}"].alignment = Alignment(wrap_text=True)
    r += 1
ws.row_dimensions[2].height = 24

# =====================================================================
# 2. 設定
# =====================================================================
ws = sheet("設定")
set_col_widths(ws, [3, 40, 16, 16, 40])
title(ws, "B2", "設定")
note(ws, "B3", "4象限のしきい値とマスタデータ。事業実態に合わせて調整してください。")

section(ws, "B5", "■ 4象限 判定しきい値")
ws["B6"] = "流動性しきい値（想定売却日数・この日数以下を高流動性とする）"
ws["C6"] = 30
ws["C6"].font, ws["C6"].fill, ws["C6"].number_format = BLUE, INPUT_FILL, '0"日"'
ws["B7"] = "収益性しきい値（想定粗利率・この率以上を高収益とする）"
ws["C7"] = 0.20
ws["C7"].font, ws["C7"].fill, ws["C7"].number_format = BLUE, INPUT_FILL, PCT
ws["B8"] = "滞留在庫リスクしきい値（想定売却日数がこの日数を超えたら滞留リスクとして警告）"
ws["C8"] = 90
ws["C8"].font, ws["C8"].fill, ws["C8"].number_format = BLUE, INPUT_FILL, '0"日"'
for r in (6, 7, 8):
    ws[f"B{r}"].font = BLACK
    ws[f"B{r}"].border = ws[f"C{r}"].border = BORDER

section(ws, "B9", "■ 4象限マスタ（分類ロジック・方針の目安）")
header_row(ws, 10, 2, ["象限コード", "流動性", "収益性", "方針の目安"])
quad_master = [
    ("I(コア)", "高（早く売れる）", "高（利益率が高い）", "積極的に仕入れる中心銘柄。予算配分と在庫上限を厚めに。"),
    ("II(回転)", "高（早く売れる）", "低（薄利）", "資金回転を稼ぐ数量枠。単価上限を抑えて回転数で稼ぐ。"),
    ("III(厳選)", "低（時間がかかる）", "高（利益率が高い）", "資金拘束を許容できる範囲で少数厳選。上限点数を絞る。"),
    ("IV(見送り)", "低（時間がかかる）", "低（薄利）", "原則仕入れ見送り。ウォッチのみ継続し再評価を待つ。"),
]
r = 11
for row in quad_master:
    for i, v in enumerate(row):
        c = ws.cell(row=r, column=2 + i, value=v)
        c.font = BLACK
        c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center")
    r += 1

section(ws, "B16", "■ カテゴリマスタ（在庫管理・ウォッチリストのプルダウンで使用）")
header_row(ws, 17, 2, ["カテゴリ名"])
categories = ["フィギュア", "トレーディングカード", "スニーカー", "アパレル", "アートトイ・グッズ", "その他"]
r = 18
for cat in categories:
    ws.cell(row=r, column=2, value=cat).font = BLUE
    ws.cell(row=r, column=2).fill = INPUT_FILL
    ws.cell(row=r, column=2).border = BORDER
    r += 1
CAT_RANGE = "設定!$B$18:$B$23"

section(ws, "B25", "■ レアリティマスタ")
header_row(ws, 26, 2, ["レアリティ"])
rarities = ["SS", "S", "A", "B", "C"]
r = 27
for rar in rarities:
    ws.cell(row=r, column=2, value=rar).font = BLUE
    ws.cell(row=r, column=2).fill = INPUT_FILL
    ws.cell(row=r, column=2).border = BORDER
    r += 1
RARITY_RANGE = "設定!$B$27:$B$31"

section(ws, "B33", "■ ステータスマスタ")
header_row(ws, 34, 2, ["ステータス"])
statuses = ["在庫中", "受注済", "売却済"]
r = 35
for st in statuses:
    ws.cell(row=r, column=2, value=st).font = BLUE
    ws.cell(row=r, column=2).fill = INPUT_FILL
    ws.cell(row=r, column=2).border = BORDER
    r += 1
STATUS_RANGE = "設定!$B$35:$B$37"

section(ws, "B39", "■ キャラクター集中リスク集計対象リスト（在庫管理シートで使うキャラ名を入力すると、ダッシュボードで自動集計されます。最大20件）")
header_row(ws, 40, 2, ["キャラ名"])
sample_chars = ["サンプルキャラA", "サンプルキャラB", "サンプルキャラC"]
CHAR_START = 41
for i in range(20):
    r = CHAR_START + i
    v = sample_chars[i] if i < len(sample_chars) else ""
    ws.cell(row=r, column=2, value=v).font = BLUE
    ws.cell(row=r, column=2).fill = INPUT_FILL
    ws.cell(row=r, column=2).border = BORDER
CHAR_RANGE = f"設定!$B${CHAR_START}:$B${CHAR_START+19}"

section(ws, "B62", "■ イラストレーター集中リスク集計対象リスト（最大20件）")
header_row(ws, 63, 2, ["イラストレーター名"])
sample_illust = ["サンプル絵師A", "サンプル絵師B"]
ILLUST_START = 64
for i in range(20):
    r = ILLUST_START + i
    v = sample_illust[i] if i < len(sample_illust) else ""
    ws.cell(row=r, column=2, value=v).font = BLUE
    ws.cell(row=r, column=2).fill = INPUT_FILL
    ws.cell(row=r, column=2).border = BORDER
ILLUST_RANGE = f"設定!$B${ILLUST_START}:$B${ILLUST_START+19}"

print("設定 sheet done:", CAT_RANGE, RARITY_RANGE, STATUS_RANGE, CHAR_RANGE, ILLUST_RANGE)

# =====================================================================
# 3. ウォッチリスト
# =====================================================================
ws = sheet("ウォッチリスト")
set_col_widths(ws, [5, 24, 16, 14, 14, 14, 12, 12, 12, 12, 16, 24])
title(ws, "B2", "ウォッチリスト（4象限分類）")
note(ws, "B3", "スニダン等のウォッチリスト登録分を入力すると、想定売却日数・想定粗利率から自動で4象限に振り分けます。青字セルのみ入力してください。")

section(ws, "B5", "■ 象限別 候補数サマリー")
labels = ["I(コア) 候補数", "II(回転) 候補数", "III(厳選) 候補数", "IV(見送り) 候補数"]
WL_HEADER_ROW = 12
WL_DATA_START = 13
WL_DATA_END = WL_DATA_START + 99  # 100 rows
for i, lab in enumerate(labels):
    r = 6 + i
    ws[f"B{r}"] = lab
    ws[f"B{r}"].font = BLACK
    ws[f"B{r}"].border = BORDER
    quad_code = ["I(コア)", "II(回転)", "III(厳選)", "IV(見送り)"][i]
    ws[f"C{r}"] = f'=COUNTIF(J{WL_DATA_START}:J{WL_DATA_END},"{quad_code}")'
    ws[f"C{r}"].font = BLACK
    ws[f"C{r}"].number_format = INT
    ws[f"C{r}"].border = BORDER

wl_cols = ["No", "銘柄名", "カテゴリ", "スニダン参考価格\n（現在相場）", "想定仕入値", "想定売却価格",
           "想定売却\n日数", "想定粗利額", "想定粗利率", "象限", "仕入れ判定", "メモ"]
header_row(ws, WL_HEADER_ROW, 1, wl_cols)
ws.freeze_panes = f"A{WL_DATA_START}"

wl_samples = [
    ("サンプル銘柄A（人気キャラ フィギュア）", "フィギュア", 28000, 22000, 30000, 20, ""),
    ("サンプル銘柄B（定番スニーカー）", "スニーカー", 32000, 28000, 33000, 10, ""),
    ("サンプル銘柄C（絶版トレカBOX）", "トレーディングカード", 45000, 38000, 52000, 60, "絶版・入手困難"),
    ("サンプル銘柄D（周年記念グッズ）", "アートトイ・グッズ", 9000, 7000, 8500, 45, "周年限定"),
    ("サンプル銘柄E（一般アパレル）", "アパレル", 6000, 5500, 5800, 90, ""),
]
for i, (name, cat, ref, buy, sell, days, memo) in enumerate(wl_samples):
    r = WL_DATA_START + i
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=cat)
    ws.cell(row=r, column=4, value=ref)
    ws.cell(row=r, column=5, value=buy)
    ws.cell(row=r, column=6, value=sell)
    ws.cell(row=r, column=7, value=days)
    ws.cell(row=r, column=12, value=memo)

for r in range(WL_DATA_START, WL_DATA_END + 1):
    ws.cell(row=r, column=1, value=f'=IF(B{r}="","",ROW()-{WL_DATA_START-1})')
    ws.cell(row=r, column=8, value=f'=IF(B{r}="","",F{r}-E{r})')
    ws.cell(row=r, column=9, value=f'=IF(B{r}="","",IF(E{r}=0,"",H{r}/E{r}))')
    ws.cell(row=r, column=10,
            value=(f'=IF(B{r}="","",IF(G{r}<=設定!$C$6,IF(I{r}>=設定!$C$7,"I(コア)","II(回転)"),'
                   f'IF(I{r}>=設定!$C$7,"III(厳選)","IV(見送り)")))'))
    ws.cell(row=r, column=11,
            value=(f'=IF(B{r}="","",IF(OR(J{r}="I(コア)",J{r}="II(回転)"),"仕入れ候補",'
                   f'IF(J{r}="III(厳選)","厳選検討（少数）","見送り")))'))
    for col, font, fmt in [(1, BLACK, INT), (2, BLUE, None), (3, BLUE, None), (4, BLUE, CUR),
                            (5, BLUE, CUR), (6, BLUE, CUR), (7, BLUE, '0"日"'), (8, BLACK, CUR),
                            (9, BLACK, PCT), (10, BLACK, None), (11, BLACK, None), (12, BLUE, None)]:
        c = ws.cell(row=r, column=col)
        c.font = font
        c.border = BORDER
        if fmt:
            c.number_format = fmt

dv_cat = DataValidation(type="list", formula1=CAT_RANGE, allow_blank=True)
ws.add_data_validation(dv_cat)
dv_cat.add(f"C{WL_DATA_START}:C{WL_DATA_END}")

print("ウォッチリスト sheet done")

# =====================================================================
# 4. 仕入れ計画
# =====================================================================
ws = sheet("仕入れ計画")
set_col_widths(ws, [5, 12, 26, 20, 14, 14, 30, 12, 14, 12, 12, 12])
title(ws, "B2", "仕入れ計画（象限別ルール）")
note(ws, "B3", "「何を・いくらまで・どの属性なら仕入れてよいか」を象限ごとに定義し、月間予算を配分します。黄色セルが判断の起点です。")

INV_HEADER_ROW = 10
INV_DATA_START = 11
INV_DATA_END = INV_DATA_START + 99  # 100 rows

ws["B5"] = "月間仕入れ総予算"
ws["B5"].font = BLACK
ws["C5"] = 500000
ws["C5"].font, ws["C5"].fill, ws["C5"].number_format = BLUE, INPUT_FILL, CUR
ws["B5"].border = ws["C5"].border = BORDER

PLAN_HEADER_ROW = 7
PLAN_START = 8
plan_cols = ["象限", "呼称", "方針", "対象カテゴリ例", "上限仕入単価", "許容レアリティ",
             "許容属性条件（絶版／周年／キャラ・イラストレーター等）", "予算配分比率", "予算配分金額",
             "在庫上限点数", "ウォッチ候補数", "現在庫点数"]
header_row(ws, PLAN_HEADER_ROW, 1, plan_cols)

plan_rows = [
    ("I(コア)", "I(コア)", "積極的に仕入れる中心銘柄。優先確保。", "フィギュア、スニーカー", 50000, "S以上",
     "絶版 または 周年記念 のいずれかに該当", 0.50, 15),
    ("II(回転)", "II(回転)", "資金回転重視。数量で稼ぐ。", "トレーディングカード、アパレル", 15000, "A以上",
     "特になし（回転優先）", 0.30, 40),
    ("III(厳選)", "III(厳選)", "少数厳選。資金拘束を許容できる範囲で。", "フィギュア、アートトイ・グッズ", 80000, "SS",
     "絶版 かつ 人気キャラ／人気イラストレーターに限定", 0.15, 5),
    ("IV(見送り)", "IV(見送り)", "原則仕入れ見送り。ウォッチのみ継続。", "-", 0, "-",
     "仕入れ対象外（再評価待ち）", 0.05, 0),
]
for i, (code, label, policy, cats, max_price, rarity, cond, ratio, cap) in enumerate(plan_rows):
    r = PLAN_START + i
    ws.cell(row=r, column=1, value=code)
    ws.cell(row=r, column=2, value=label)
    ws.cell(row=r, column=3, value=policy)
    ws.cell(row=r, column=4, value=cats)
    ws.cell(row=r, column=5, value=max_price)
    ws.cell(row=r, column=6, value=rarity)
    ws.cell(row=r, column=7, value=cond)
    ws.cell(row=r, column=8, value=ratio)
    ws.cell(row=r, column=9, value=f"=$C$5*H{r}")
    ws.cell(row=r, column=10, value=cap)
    ws.cell(row=r, column=11, value=f'=COUNTIF(ウォッチリスト!$J${WL_DATA_START}:$J${WL_DATA_END},"{code}")')
    ws.cell(row=r, column=12,
            value=f'=COUNTIF(在庫管理!$P${INV_DATA_START}:$P${INV_DATA_END},"{code}")')
    for col, font, fmt in [(1, BLACK, None), (2, BLACK, None), (3, BLUE, None), (4, BLUE, None),
                            (5, BLUE, CUR), (6, BLUE, None), (7, BLUE, None), (8, BLUE, PCT),
                            (9, BLACK, CUR), (10, BLUE, INT), (11, BLACK, INT), (12, BLACK, INT)]:
        c = ws.cell(row=r, column=col)
        c.font = font
        c.border = BORDER
        if fmt:
            c.number_format = fmt
        if col in (5, 8, 10):
            c.fill = INPUT_FILL
    ws.row_dimensions[r].height = 30

TOTAL_ROW = PLAN_START + len(plan_rows)
ws.cell(row=TOTAL_ROW, column=2, value="合計").font = BOLD
ws.cell(row=TOTAL_ROW, column=8, value=f"=SUM(H{PLAN_START}:H{TOTAL_ROW-1})")
ws.cell(row=TOTAL_ROW, column=9, value=f"=SUM(I{PLAN_START}:I{TOTAL_ROW-1})")
for col in (2, 8, 9):
    c = ws.cell(row=TOTAL_ROW, column=col)
    c.font = BOLD
    c.border = BORDER
    if col == 8:
        c.number_format = PCT
    if col == 9:
        c.number_format = CUR

ws.conditional_formatting.add(
    f"H{TOTAL_ROW}",
    CellIsRule(operator="notEqual", formula=["1"], fill=PatternFill("solid", fgColor="FFC7CE"),
               font=Font(color="9C0006")),
)
note(ws, f"B{TOTAL_ROW+2}", "※ 予算配分比率の合計は100%になるように調整してください（赤色表示は100%以外を意味します）。")

print("仕入れ計画 sheet done (in-stock placeholder pending)")

# =====================================================================
# 5. 在庫管理
# =====================================================================
ws = sheet("在庫管理")
set_col_widths(ws, [5, 26, 16, 14, 14, 8, 8, 10, 10, 12, 12, 14, 12, 12, 12, 12, 12, 22])
title(ws, "B2", "在庫管理シート（実在庫・ポートフォリオ管理）")
note(ws, "B3", "青字セルのみ入力してください。ステータスが「在庫中」の行のみ、集計・ポートフォリオ比率に反映されます。")

summary_labels = ["総仕入額（在庫中）", "総時価（在庫中）", "含み損益", "含み損益率", "在庫点数（在庫中）"]
for i, lab in enumerate(summary_labels):
    r = 5 + i
    ws.cell(row=r, column=2, value=lab).font = BLACK
    ws.cell(row=r, column=2).border = BORDER
ws["C5"] = f'=SUMIFS(K{INV_DATA_START}:K{INV_DATA_END},I{INV_DATA_START}:I{INV_DATA_END},"在庫中")'
ws["C6"] = f'=SUMIFS(L{INV_DATA_START}:L{INV_DATA_END},I{INV_DATA_START}:I{INV_DATA_END},"在庫中")'
ws["C7"] = "=C6-C5"
ws["C8"] = '=IFERROR(C7/C5,"")'
ws["C9"] = f'=COUNTIF(I{INV_DATA_START}:I{INV_DATA_END},"在庫中")'
for r, fmt in [(5, CUR), (6, CUR), (7, CUR), (8, PCT), (9, INT)]:
    ws.cell(row=r, column=3).font = BLACK
    ws.cell(row=r, column=3).border = BORDER
    ws.cell(row=r, column=3).number_format = fmt

inv_cols = ["No", "商品名", "カテゴリ", "キャラ", "イラストレーター", "絶版", "周年", "レアリティ",
            "ステータス", "仕入日", "仕入値", "現在時価\n（想定売却価格）", "想定売却\n日数",
            "想定粗利額", "想定粗利率", "象限", "ポートフォリオ\n比率", "メモ"]
header_row(ws, INV_HEADER_ROW, 1, inv_cols)
ws.freeze_panes = f"A{INV_DATA_START}"

inv_samples = [
    ("サンプル商品A（人気キャラ フィギュア）", "フィギュア", "サンプルキャラA", "サンプル絵師A", "○", "×", "SS",
     "在庫中", "2026-06-15", 24000, 31000, 18, ""),
    ("サンプル商品B（定番スニーカー）", "スニーカー", "", "", "×", "×", "A",
     "在庫中", "2026-07-01", 28000, 31500, 12, ""),
    ("サンプル商品C（絶版トレカBOX）", "トレーディングカード", "サンプルキャラB", "", "○", "×", "S",
     "在庫中", "2026-05-20", 38000, 49000, 55, "絶版・入手困難"),
    ("サンプル商品D（周年記念グッズ）", "アートトイ・グッズ", "サンプルキャラA", "サンプル絵師B", "×", "○", "A",
     "受注済", "2026-07-10", 7000, 8300, 40, "周年限定"),
    ("サンプル商品E（一般アパレル）", "アパレル", "", "", "×", "×", "B",
     "売却済", "2026-04-01", 5500, 5900, 88, ""),
]
for i, (name, cat, chara, illust, op, anniv, rarity, status, buydate, cost, mv, days, memo) in enumerate(inv_samples):
    r = INV_DATA_START + i
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=cat)
    ws.cell(row=r, column=4, value=chara)
    ws.cell(row=r, column=5, value=illust)
    ws.cell(row=r, column=6, value=op)
    ws.cell(row=r, column=7, value=anniv)
    ws.cell(row=r, column=8, value=rarity)
    ws.cell(row=r, column=9, value=status)
    ws.cell(row=r, column=10, value=buydate)
    ws.cell(row=r, column=11, value=cost)
    ws.cell(row=r, column=12, value=mv)
    ws.cell(row=r, column=13, value=days)
    ws.cell(row=r, column=18, value=memo)

for r in range(INV_DATA_START, INV_DATA_END + 1):
    ws.cell(row=r, column=1, value=f'=IF(B{r}="","",ROW()-{INV_DATA_START-1})')
    ws.cell(row=r, column=14, value=f'=IF(B{r}="","",L{r}-K{r})')
    ws.cell(row=r, column=15, value=f'=IF(B{r}="","",IF(K{r}=0,"",N{r}/K{r}))')
    ws.cell(row=r, column=16,
            value=(f'=IF(B{r}="","",IF(M{r}<=設定!$C$6,IF(O{r}>=設定!$C$7,"I(コア)","II(回転)"),'
                   f'IF(O{r}>=設定!$C$7,"III(厳選)","IV(見送り)")))'))
    ws.cell(row=r, column=17,
            value=f'=IF(B{r}="","",IF(I{r}="在庫中",IF($C$6=0,"",L{r}/$C$6),""))')
    col_font_fmt = {
        1: (BLACK, INT), 2: (BLUE, None), 3: (BLUE, None), 4: (BLUE, None), 5: (BLUE, None),
        6: (BLUE, None), 7: (BLUE, None), 8: (BLUE, None), 9: (BLUE, None), 10: (BLUE, DATE),
        11: (BLUE, CUR), 12: (BLUE, CUR), 13: (BLUE, '0"日"'), 14: (BLACK, CUR), 15: (BLACK, PCT),
        16: (BLACK, None), 17: (BLACK, PCT), 18: (BLUE, None),
    }
    for col, (font, fmt) in col_font_fmt.items():
        c = ws.cell(row=r, column=col)
        c.font = font
        c.border = BORDER
        if fmt:
            c.number_format = fmt

dv_cat2 = DataValidation(type="list", formula1=CAT_RANGE, allow_blank=True)
dv_rarity = DataValidation(type="list", formula1=RARITY_RANGE, allow_blank=True)
dv_status = DataValidation(type="list", formula1=STATUS_RANGE, allow_blank=True)
dv_yn = DataValidation(type="list", formula1='"○,×"', allow_blank=True)
for dv in (dv_cat2, dv_rarity, dv_status, dv_yn):
    ws.add_data_validation(dv)
dv_cat2.add(f"C{INV_DATA_START}:C{INV_DATA_END}")
dv_rarity.add(f"H{INV_DATA_START}:H{INV_DATA_END}")
dv_status.add(f"I{INV_DATA_START}:I{INV_DATA_END}")
dv_yn.add(f"F{INV_DATA_START}:G{INV_DATA_END}")

print("在庫管理 sheet done")

# =====================================================================
# 6. ダッシュボード
# =====================================================================
ws = sheet("ダッシュボード")
set_col_widths(ws, [3, 30, 16, 12, 12, 4, 20, 16, 12, 12, 12, 12])
title(ws, "B2", "ダッシュボード")
note(ws, "B3", "在庫管理シートを自動集計します。手入力は不要です（すべて数式）。")

INV_L = f"在庫管理!$L${INV_DATA_START}:$L${INV_DATA_END}"
INV_I = f"在庫管理!$I${INV_DATA_START}:$I${INV_DATA_END}"
INV_M = f"在庫管理!$M${INV_DATA_START}:$M${INV_DATA_END}"
INV_P = f"在庫管理!$P${INV_DATA_START}:$P${INV_DATA_END}"
INV_C = f"在庫管理!$C${INV_DATA_START}:$C${INV_DATA_END}"
INV_D = f"在庫管理!$D${INV_DATA_START}:$D${INV_DATA_END}"
INV_E = f"在庫管理!$E${INV_DATA_START}:$E${INV_DATA_END}"

def kpi(ws, row, label, formula, fmt, link=False):
    ws.cell(row=row, column=2, value=label).font = BLACK
    c = ws.cell(row=row, column=3, value=formula)
    c.font = GREEN if link else BLACK
    c.number_format = fmt
    for col in (2, 3):
        ws.cell(row=row, column=col).border = BORDER

section(ws, "B5", "■ 資本効率")
kpi(ws, 6, "総仕入額（在庫中）", "=在庫管理!$C$5", CUR, link=True)
kpi(ws, 7, "総時価（在庫中）", "=在庫管理!$C$6", CUR, link=True)
kpi(ws, 8, "含み損益", "=在庫管理!$C$7", CUR, link=True)
kpi(ws, 9, "含み損益率（簡易ROI）", "=在庫管理!$C$8", PCT, link=True)
kpi(ws, 10, "GMROI（簡易・総時価÷総仕入額）", '=IFERROR($C$7/$C$6,"")', "0.00x")
kpi(ws, 11, "加重平均想定売却日数", f'=IFERROR(SUMPRODUCT(({INV_I}="在庫中")*{INV_M}*{INV_L})/$C$7,"")', '0.0"日"')
kpi(ws, 12, "在庫回転率（年換算・365日÷平均売却日数）", '=IFERROR(365/$C$11,"")', "0.00")

section(ws, "B14", "■ 実行流動性")
kpi(ws, 15, f"高流動性しきい値（設定!C6）以内 換金可能比率", f'=IFERROR(SUMIFS({INV_L},{INV_I},"在庫中",{INV_M},"<="&設定!$C$6)/$C$7,"")', PCT)
kpi(ws, 16, "滞留リスクしきい値（設定!C8）超 滞留在庫比率", f'=IFERROR(SUMIFS({INV_L},{INV_I},"在庫中",{INV_M},">"&設定!$C$8)/$C$7,"")', PCT)
kpi(ws, 17, "高流動性象限（I+II）比率（時価ベース）",
    f'=IFERROR((SUMIFS({INV_L},{INV_I},"在庫中",{INV_P},"I(コア)")+SUMIFS({INV_L},{INV_I},"在庫中",{INV_P},"II(回転)"))/$C$7,"")', PCT)
kpi(ws, 18, "低流動性象限（III+IV）比率（時価ベース）",
    f'=IFERROR((SUMIFS({INV_L},{INV_I},"在庫中",{INV_P},"III(厳選)")+SUMIFS({INV_L},{INV_I},"在庫中",{INV_P},"IV(見送り)"))/$C$7,"")', PCT)

section(ws, "B20", "■ 集中リスク分析（HHI = Σ構成比^2×10,000。目安：1,500未満=分散／1,500〜2,500=中程度／2,500以上=集中リスク高）")


def conc_table_header(ws, row, col_start, name_label):
    header_row(ws, row, col_start, [name_label, "時価（在庫中）", "構成比", "HHI寄与"])


def conc_total_row(ws, row, col_start, data_start, data_end):
    L = get_column_letter(col_start + 1)
    S = get_column_letter(col_start + 2)
    H = get_column_letter(col_start + 3)
    ws.cell(row=row, column=col_start, value="合計 / HHI").font = BOLD
    ws.cell(row=row, column=col_start + 1, value=f"=SUM({L}{data_start}:{L}{data_end})")
    ws.cell(row=row, column=col_start + 2, value=f"=SUM({S}{data_start}:{S}{data_end})")
    ws.cell(row=row, column=col_start + 3, value=f"=SUM({H}{data_start}:{H}{data_end})")
    for c in range(col_start, col_start + 4):
        cc = ws.cell(row=row, column=c)
        cc.font = BOLD
        cc.border = BORDER
    ws.cell(row=row, column=col_start + 1).number_format = CUR
    ws.cell(row=row, column=col_start + 2).number_format = PCT
    ws.cell(row=row, column=col_start + 3).number_format = "0"
    risk_row = row + 1
    Hcell = f"{H}{row}"
    ws.cell(row=risk_row, column=col_start, value="集中リスク判定")
    ws.cell(row=risk_row, column=col_start).font = BOLD
    ws.cell(row=risk_row, column=col_start + 1,
            value=f'=IF({Hcell}>=2500,"集中リスク高",IF({Hcell}>=1500,"中程度","分散（健全）"))')
    ws.cell(row=risk_row, column=col_start + 1).font = BOLD
    ws.merge_cells(start_row=risk_row, start_column=col_start + 1, end_row=risk_row, end_column=col_start + 3)
    return risk_row


# --- カテゴリ別（B列） ---
CAT_TBL_HDR = 22
CAT_TBL_START = 23
conc_table_header(ws, CAT_TBL_HDR, 2, "カテゴリ")
for i in range(6):
    r = CAT_TBL_START + i
    setrow = 18 + i
    ws.cell(row=r, column=2, value=f"='設定'!B{setrow}")
    ws.cell(row=r, column=3, value=f'=SUMIFS({INV_L},{INV_I},"在庫中",{INV_C},$B{r})')
    ws.cell(row=r, column=4, value=f'=IFERROR($C{r}/$C$7,"")')
    ws.cell(row=r, column=5, value=f'=IFERROR($D{r}^2*10000,0)')
    for col, fmt in [(2, None), (3, CUR), (4, PCT), (5, "0")]:
        c = ws.cell(row=r, column=col)
        c.font = BLACK
        c.border = BORDER
        if fmt:
            c.number_format = fmt
CAT_TBL_END = CAT_TBL_START + 5
cat_risk_row = conc_total_row(ws, CAT_TBL_END + 1, 2, CAT_TBL_START, CAT_TBL_END)

# --- 象限別（G列） ---
QUAD_TBL_HDR = 22
QUAD_TBL_START = 23
conc_table_header(ws, QUAD_TBL_HDR, 7, "象限")
quad_labels = ["I(コア)", "II(回転)", "III(厳選)", "IV(見送り)"]
for i, q in enumerate(quad_labels):
    r = QUAD_TBL_START + i
    ws.cell(row=r, column=7, value=q)
    ws.cell(row=r, column=8, value=f'=SUMIFS({INV_L},{INV_I},"在庫中",{INV_P},$G{r})')
    ws.cell(row=r, column=9, value=f'=IFERROR($H{r}/$C$7,"")')
    ws.cell(row=r, column=10, value=f'=IFERROR($I{r}^2*10000,0)')
    for col, fmt in [(7, None), (8, CUR), (9, PCT), (10, "0")]:
        c = ws.cell(row=r, column=col)
        c.font = BLACK
        c.border = BORDER
        if fmt:
            c.number_format = fmt
QUAD_TBL_END = QUAD_TBL_START + 3
quad_risk_row = conc_total_row(ws, QUAD_TBL_END + 1, 7, QUAD_TBL_START, QUAD_TBL_END)

# --- キャラ別（B列、その他行含む） ---
CHAR_TBL_HDR = 32
CHAR_TBL_START = 33
conc_table_header(ws, CHAR_TBL_HDR, 2, "キャラ")
for i in range(20):
    r = CHAR_TBL_START + i
    setrow = CHAR_START + i
    ws.cell(row=r, column=2, value=f"='設定'!B{setrow}")
    ws.cell(row=r, column=3, value=f'=IF($B{r}="","",SUMIFS({INV_L},{INV_I},"在庫中",{INV_D},$B{r}))')
    ws.cell(row=r, column=4, value=f'=IFERROR($C{r}/$C$7,"")')
    ws.cell(row=r, column=5, value=f'=IFERROR($D{r}^2*10000,0)')
    for col, fmt in [(2, None), (3, CUR), (4, PCT), (5, "0")]:
        c = ws.cell(row=r, column=col)
        c.font = BLACK
        c.border = BORDER
        if fmt:
            c.number_format = fmt
OTHER_CHAR_ROW = CHAR_TBL_START + 20
ws.cell(row=OTHER_CHAR_ROW, column=2, value="その他（未登録キャラ／タグなし）")
ws.cell(row=OTHER_CHAR_ROW, column=3,
        value=f'=MAX(0,SUMIFS({INV_L},{INV_I},"在庫中")-SUM(C{CHAR_TBL_START}:C{CHAR_TBL_START+19}))')
ws.cell(row=OTHER_CHAR_ROW, column=4, value=f'=IFERROR($C{OTHER_CHAR_ROW}/$C$7,"")')
ws.cell(row=OTHER_CHAR_ROW, column=5, value=f'=IFERROR($D{OTHER_CHAR_ROW}^2*10000,0)')
for col, fmt in [(2, None), (3, CUR), (4, PCT), (5, "0")]:
    c = ws.cell(row=OTHER_CHAR_ROW, column=col)
    c.font = NOTE
    c.border = BORDER
    if fmt:
        c.number_format = fmt
char_risk_row = conc_total_row(ws, OTHER_CHAR_ROW + 1, 2, CHAR_TBL_START, OTHER_CHAR_ROW)

# --- イラストレーター別（G列、その他行含む） ---
ILL_TBL_HDR = 32
ILL_TBL_START = 33
conc_table_header(ws, ILL_TBL_HDR, 7, "イラストレーター")
for i in range(20):
    r = ILL_TBL_START + i
    setrow = ILLUST_START + i
    ws.cell(row=r, column=7, value=f"='設定'!B{setrow}")
    ws.cell(row=r, column=8, value=f'=IF($G{r}="","",SUMIFS({INV_L},{INV_I},"在庫中",{INV_E},$G{r}))')
    ws.cell(row=r, column=9, value=f'=IFERROR($H{r}/$C$7,"")')
    ws.cell(row=r, column=10, value=f'=IFERROR($I{r}^2*10000,0)')
    for col, fmt in [(7, None), (8, CUR), (9, PCT), (10, "0")]:
        c = ws.cell(row=r, column=col)
        c.font = BLACK
        c.border = BORDER
        if fmt:
            c.number_format = fmt
OTHER_ILL_ROW = ILL_TBL_START + 20
ws.cell(row=OTHER_ILL_ROW, column=7, value="その他（未登録／タグなし）")
ws.cell(row=OTHER_ILL_ROW, column=8,
        value=f'=MAX(0,SUMIFS({INV_L},{INV_I},"在庫中")-SUM(H{ILL_TBL_START}:H{ILL_TBL_START+19}))')
ws.cell(row=OTHER_ILL_ROW, column=9, value=f'=IFERROR($H{OTHER_ILL_ROW}/$C$7,"")')
ws.cell(row=OTHER_ILL_ROW, column=10, value=f'=IFERROR($I{OTHER_ILL_ROW}^2*10000,0)')
for col, fmt in [(7, None), (8, CUR), (9, PCT), (10, "0")]:
    c = ws.cell(row=OTHER_ILL_ROW, column=col)
    c.font = NOTE
    c.border = BORDER
    if fmt:
        c.number_format = fmt
ill_risk_row = conc_total_row(ws, OTHER_ILL_ROW + 1, 7, ILL_TBL_START, OTHER_ILL_ROW)

# 3-color scale conditional formatting on HHI columns
for col_letter, start, end in [("E", CAT_TBL_START, CAT_TBL_END), ("J", QUAD_TBL_START, QUAD_TBL_END),
                                ("E", CHAR_TBL_START, OTHER_CHAR_ROW), ("J", ILL_TBL_START, OTHER_ILL_ROW)]:
    rng = f"{col_letter}{start}:{col_letter}{end}"
    ws.conditional_formatting.add(
        rng,
        ColorScaleRule(start_type="num", start_value=0, start_color="C6EFCE",
                        mid_type="num", mid_value=2500, mid_color="FFEB9C",
                        end_type="num", end_value=10000, end_color="FFC7CE"),
    )

print("ダッシュボード 集中リスク table done, risk rows:", cat_risk_row, quad_risk_row, char_risk_row, ill_risk_row)

# --- charts ---
pie = PieChart()
pie.title = "ポートフォリオ構成（カテゴリ別・時価）"
pie_data = Reference(ws, min_col=3, min_row=CAT_TBL_HDR, max_row=CAT_TBL_END)
pie_cats = Reference(ws, min_col=2, min_row=CAT_TBL_START, max_row=CAT_TBL_END)
pie.add_data(pie_data, titles_from_data=True)
pie.set_categories(pie_cats)
pie.height, pie.width = 8, 14
ws.add_chart(pie, "M5")

bar = BarChart()
bar.type = "col"
bar.title = "象限別 時価（在庫中）"
bar.y_axis.title = "時価（円）"
bar_data = Reference(ws, min_col=8, min_row=QUAD_TBL_HDR, max_row=QUAD_TBL_END)
bar_cats = Reference(ws, min_col=7, min_row=QUAD_TBL_START, max_row=QUAD_TBL_END)
bar.add_data(bar_data, titles_from_data=True)
bar.set_categories(bar_cats)
bar.height, bar.width = 8, 14
bar.legend = None
ws.add_chart(bar, "M22")

print("ダッシュボード charts done")

# =====================================================================
# 7. スケジュール
# =====================================================================
ws = sheet("スケジュール")
set_col_widths(ws, [3, 16, 40, 14, 12, 12, 14, 10, 34])
title(ws, "B2", "スケジュール・タスク（8月本格運用に向けて）")
note(ws, "B3", "「やれることからやる」ではなく、データが取れる基盤（設定→ウォッチリスト→仕入れ計画→在庫管理→ダッシュボード）を先に作ることを優先する。")

SCH_HDR = 5
header_row(ws, SCH_HDR, 2, ["フェーズ", "タスク", "開始日", "期限", "担当", "ステータス", "進捗率", "備考"])

tasks = [
    ("0. 基盤準備", "設定シートでカテゴリ・レアリティ・4象限しきい値を事業実態に合わせて確定する", "2026-07-30", "2026-07-31", "未定", "未着手", "実務タスク5：基盤づくり"),
    ("0. 基盤準備", "在庫管理シートの入力ルール（誰が・いつ登録するか）を決める", "2026-07-30", "2026-08-01", "未定", "未着手", ""),
    ("1. ウォッチリスト分類", "スニダンのウォッチリスト登録分を全件エクスポートする", "2026-07-31", "2026-08-01", "未定", "未着手", "実務タスク1"),
    ("1. ウォッチリスト分類", "ウォッチリストシートへ登録し、自動分類（4象限）を確認する", "2026-08-01", "2026-08-03", "未定", "未着手", ""),
    ("1. ウォッチリスト分類", "象限別の候補数・偏りをレビューし、しきい値を再調整する", "2026-08-03", "2026-08-04", "未定", "未着手", ""),
    ("2. 仕入れ計画策定", "象限別「何を・いくらまで・どの属性なら仕入れるか」を確定する", "2026-08-01", "2026-08-05", "未定", "未着手", "実務タスク2"),
    ("2. 仕入れ計画策定", "月間仕入れ予算の象限別配分比率を決定する", "2026-08-03", "2026-08-05", "未定", "未着手", ""),
    ("2. 仕入れ計画策定", "仕入れ計画をチームに共有し、運用を開始する", "2026-08-05", "2026-08-07", "未定", "未着手", ""),
    ("3. 在庫管理運用開始", "既存在庫を4分類＋タグ（キャラ／イラストレーター／絶版／周年／レアリティ）で棚卸し登録する", "2026-08-01", "2026-08-10", "未定", "未着手", "実務タスク3"),
    ("3. 在庫管理運用開始", "ポートフォリオ比率・集中リスク（HHI）の初期値を確認する", "2026-08-10", "2026-08-12", "未定", "未着手", ""),
    ("3. 在庫管理運用開始", "在庫データの週次更新ルール（誰が・いつ更新するか）を決める", "2026-08-10", "2026-08-12", "未定", "未着手", ""),
    ("4. ダッシュボード運用", "資本効率（GMROI・回転率・ROI）と実行流動性指標の初期値を算出する", "2026-08-10", "2026-08-15", "未定", "未着手", "実務タスク4"),
    ("4. ダッシュボード運用", "週次レビューMTGにダッシュボードを組み込む", "2026-08-15", "2026-08-20", "未定", "未着手", ""),
    ("5. 継続運用", "週次でウォッチリスト→仕入れ計画→在庫管理→ダッシュボードのサイクルを回す", "2026-08-20", "継続", "未定", "未着手", "実務タスク5：本格運用"),
    ("5. 継続運用", "月次で4象限しきい値・カテゴリ／タグ体系を見直す", "2026-08-31", "継続", "未定", "未着手", ""),
]
SCH_START = SCH_HDR + 1
for i, (phase, task, start, due, owner, status, note_txt) in enumerate(tasks):
    r = SCH_START + i
    ws.cell(row=r, column=2, value=phase)
    ws.cell(row=r, column=3, value=task)
    import datetime as _dt
    start_v = _dt.datetime.strptime(start, "%Y-%m-%d") if "-" in start else start
    ws.cell(row=r, column=4, value=start_v)
    if "-" in due:
        ws.cell(row=r, column=5, value=_dt.datetime.strptime(due, "%Y-%m-%d"))
    else:
        ws.cell(row=r, column=5, value=due)
    ws.cell(row=r, column=6, value=owner)
    ws.cell(row=r, column=7, value=status)
    ws.cell(row=r, column=8, value=0)
    ws.cell(row=r, column=9, value=note_txt)
    for col, font, fmt, fill in [(2, BLACK, None, None), (3, BLACK, None, None), (4, BLUE, DATE, None),
                                  (5, BLUE, DATE, None), (6, BLUE, None, TODO_FILL), (7, BLUE, None, INPUT_FILL),
                                  (8, BLUE, PCT, INPUT_FILL), (9, BLACK, None, None)]:
        c = ws.cell(row=r, column=col)
        c.font = font
        c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center")
        if fmt:
            c.number_format = fmt
        if fill:
            c.fill = fill
    ws.row_dimensions[r].height = 28
SCH_END = SCH_START + len(tasks) - 1

dv_status2 = DataValidation(type="list", formula1='"未着手,進行中,完了,保留"', allow_blank=True)
ws.add_data_validation(dv_status2)
dv_status2.add(f"G{SCH_START}:G{SCH_END}")

ws.conditional_formatting.add(
    f"H{SCH_START}:H{SCH_END}",
    DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="638EC6"),
)
ws.conditional_formatting.add(
    f"G{SCH_START}:G{SCH_END}",
    CellIsRule(operator="equal", formula=['"完了"'], fill=PatternFill("solid", fgColor="C6EFCE")),
)
ws.freeze_panes = f"B{SCH_START}"
note(ws, f"B{SCH_END+2}", "担当（オレンジ）は要アサイン。ステータス・進捗率（黄）は運用しながら更新してください。")

print("スケジュール sheet done")

# =====================================================================
# final touches
# =====================================================================
tab_colors = {
    "使い方": "808080", "設定": "808080", "ウォッチリスト": "2E75B6", "仕入れ計画": "548235",
    "在庫管理": "BF8F00", "ダッシュボード": "C00000", "スケジュール": "7030A0",
}
for name, color in tab_colors.items():
    wb[name].sheet_properties.tabColor = color

for name in wb.sheetnames:
    s = wb[name]
    s.page_setup.orientation = "landscape"
    s.page_setup.fitToWidth = 1
    s.page_setup.fitToHeight = 0
    s.sheet_properties.pageSetUpPr.fitToPage = True
    s.page_margins.left = s.page_margins.right = 0.4
    s.page_margins.top = s.page_margins.bottom = 0.5

wb["ウォッチリスト"].print_title_rows = f"{WL_HEADER_ROW}:{WL_HEADER_ROW}"
wb["在庫管理"].print_title_rows = f"{INV_HEADER_ROW}:{INV_HEADER_ROW}"
wb["スケジュール"].print_title_rows = f"{SCH_HDR}:{SCH_HDR}"

wb.active = wb.sheetnames.index("使い方")
wb.save(OUT_PATH)
print("ALL SHEETS SAVED")

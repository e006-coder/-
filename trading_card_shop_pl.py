"""
トレーディングカードショップ 月次PLシミュレーション
2026年7月〜2027年7月（13ヶ月間）
"""

import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.views import SheetView

# ─────────────────────────────────────────────
# カラー定数
# ─────────────────────────────────────────────
COLOR = {
    "overview_header": "1F3864",   # ネイビー
    "overview_sub":    "2E75B6",
    "a_header":        "595959",   # グレー
    "a_sub":           "808080",
    "b_header":        "1E6B44",   # グリーン
    "b_sub":           "2E8B57",
    "c_header":        "1D6570",   # ティール
    "c_sub":           "2A9099",
    "section_bg":      "D9E1F2",   # 薄い青（セクション）
    "profit_bg":       "E2EFDA",   # 薄い緑（利益行）
    "loss_bg":         "FCE4D6",   # 薄い赤（損失行）
    "white":           "FFFFFF",
    "light_gray":      "F2F2F2",
    "total_bg":        "FFF2CC",   # 黄（合計行）
}

MONTHS = [
    "2026年7月", "2026年8月", "2026年9月", "2026年10月",
    "2026年11月", "2026年12月", "2027年1月", "2027年2月",
    "2027年3月", "2027年4月", "2027年5月", "2027年6月", "2027年7月",
]
NUM_MONTHS = len(MONTHS)  # 13

# ─────────────────────────────────────────────
# パターン別仮定値（千円）
# ─────────────────────────────────────────────
PATTERNS = {
    "A": {
        "name": "パターンA_EC特化",
        "label": "EC特化（無店舗）",
        "header_color": "595959",
        "sub_color":    "A6A6A6",
        # 売上
        "new_sales":    2_100_000,   # 新品売上
        "used_sales":     900_000,   # 中古売上
        # 原価率
        "new_cost_rate":  0.70,
        "used_cost_rate": 0.50,
        # 販管費（月次）
        "rent":               0,
        "salary_full":   350_000,
        "salary_part":        0,
        "ad":             50_000,
        "ec_fee_rate":     0.035,    # EC手数料：売上の3.5%
        "shipping":       80_000,
        "utilities":      50_000,
    },
    "B": {
        "name": "パターンB_大型実店舗",
        "label": "大型実店舗",
        "header_color": "1E6B44",
        "sub_color":    "70AD47",
        "new_sales":    5_600_000,
        "used_sales":   2_400_000,
        "new_cost_rate":  0.70,
        "used_cost_rate": 0.50,
        "rent":          300_000,
        "salary_full":   350_000,
        "salary_part":   250_000,
        "ad":            150_000,
        "ec_fee_rate":     0.015,
        "shipping":       80_000,
        "utilities":      120_000,
    },
    "C": {
        "name": "パターンC_ハイブリッド",
        "label": "ハイブリッド（実店舗＋EC）",
        "header_color": "1D6570",
        "sub_color":    "17A589",
        "new_sales":    3_500_000,
        "used_sales":   1_500_000,
        "new_cost_rate":  0.70,
        "used_cost_rate": 0.50,
        "rent":          150_000,
        "salary_full":   350_000,
        "salary_part":    80_000,
        "ad":             80_000,
        "ec_fee_rate":     0.025,
        "shipping":       80_000,
        "utilities":       80_000,
    },
}

# ─────────────────────────────────────────────
# スタイルヘルパー
# ─────────────────────────────────────────────
def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color="000000", size=11, italic=False):
    return Font(bold=bold, color=color, size=size, italic=italic, name="メイリオ")

def align(h="center", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def thin_border():
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def bottom_border(color="000000"):
    return Border(bottom=Side(style="medium", color=color))

def apply_style(cell, fill_color=None, bold=False, font_color="000000",
                h_align="right", v_align="center", size=11,
                border=True, italic=False):
    if fill_color:
        cell.fill = fill(fill_color)
    cell.font = font(bold=bold, color=font_color, size=size, italic=italic)
    cell.alignment = align(h_align, v_align)
    if border:
        cell.border = thin_border()

def num_format(cell, fmt="#,##0"):
    cell.number_format = fmt

# ─────────────────────────────────────────────
# 月次PLシートを生成
# ─────────────────────────────────────────────
def build_pl_sheet(ws, pattern_key):
    p = PATTERNS[pattern_key]
    hc = p["header_color"]
    sc = p["sub_color"]

    ws.sheet_view.showGridLines = True

    # ── 列構成 ──
    # A: 項目番号, B: 項目名, C〜O: 月次(13ヶ月), P: 年間合計
    COL_LABEL = 2   # B列
    COL_START = 3   # C列（1ヶ月目）
    COL_END   = COL_START + NUM_MONTHS - 1   # O列
    COL_TOTAL = COL_END + 1                  # P列

    # 列幅設定
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 28
    for col in range(COL_START, COL_TOTAL + 1):
        ws.column_dimensions[get_column_letter(col)].width = 14

    # ── ROW 1-4: タイトル・説明 ──
    ws.row_dimensions[1].height = 8
    ws.row_dimensions[2].height = 36
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 8
    ws.row_dimensions[5].height = 28

    # タイトル
    title_cell = ws.cell(row=2, column=COL_LABEL)
    title_cell.value = f"月次PLシミュレーション　{p['label']}"
    title_cell.font = Font(bold=True, size=16, color=hc, name="メイリオ")
    title_cell.alignment = align("left", "center")
    ws.merge_cells(start_row=2, start_column=COL_LABEL,
                   end_row=2, end_column=COL_TOTAL)

    subtitle = ws.cell(row=3, column=COL_LABEL)
    subtitle.value = "期間：2026年7月〜2027年7月（13ヶ月）　　単位：円"
    subtitle.font = Font(size=10, color="595959", italic=True, name="メイリオ")
    subtitle.alignment = align("left", "center")
    ws.merge_cells(start_row=3, start_column=COL_LABEL,
                   end_row=3, end_column=COL_TOTAL)

    # ── ROW 5: ヘッダー行 ──
    header_row = 5

    # 項目ラベル
    h = ws.cell(row=header_row, column=COL_LABEL, value="項　目")
    h.fill = fill(hc)
    h.font = font(bold=True, color="FFFFFF", size=11)
    h.alignment = align("center", "center")
    h.border = thin_border()

    for i, month in enumerate(MONTHS):
        col = COL_START + i
        c = ws.cell(row=header_row, column=col, value=month)
        c.fill = fill(hc)
        c.font = font(bold=True, color="FFFFFF", size=10)
        c.alignment = align("center", "center")
        c.border = thin_border()

    total_h = ws.cell(row=header_row, column=COL_TOTAL, value="年間合計")
    total_h.fill = fill(hc)
    total_h.font = font(bold=True, color="FFFFFF", size=11)
    total_h.alignment = align("center", "center")
    total_h.border = thin_border()

    # ウィンドウ枠固定（C6 = 6行目・3列目）
    ws.freeze_panes = ws.cell(row=header_row + 1, column=COL_START)

    # ─────────────────────────────────
    # PLの行定義
    # ─────────────────────────────────
    # (行ラベル, タイプ, 値or数式ヒント, 背景色, 太字, インデント)
    # タイプ: "input"=入力値, "formula"=他行参照数式, "section"=セクションヘッダー, "spacer"=空白行
    ROW_OFFSET = header_row + 1  # 実データ開始行

    rows_def = [
        # ラベル,                        type,      config_key / formula_keys,                 bg,               bold,   section_label
        ("▌ 売上高",                     "section", None,                                       hc,               True,   True),
        ("  新品売上",                   "input",   "new_sales",                                COLOR["light_gray"], False, False),
        ("  中古売上",                   "input",   "used_sales",                               COLOR["light_gray"], False, False),
        ("  売上合計",                   "sum2",    ("new_sales", "used_sales"),                 COLOR["total_bg"],  True,  False),
        ("",                             "spacer",  None,                                       None,             False,  False),
        ("▌ 売上原価",                   "section", None,                                       hc,               True,   True),
        ("  新品原価",                   "rate",    ("new_sales", "new_cost_rate"),              COLOR["light_gray"], False, False),
        ("  中古原価",                   "rate",    ("used_sales", "used_cost_rate"),            COLOR["light_gray"], False, False),
        ("  原価合計",                   "sum2",    ("new_cost", "used_cost"),                   COLOR["total_bg"],  True,  False),
        ("",                             "spacer",  None,                                       None,             False,  False),
        ("▌ 売上総利益（粗利）",          "gross",   ("sales_total", "cost_total"),               COLOR["profit_bg"], True,  False),
        ("",                             "spacer",  None,                                       None,             False,  False),
        ("▌ 販売管理費",                 "section", None,                                       hc,               True,   True),
        ("  地代家賃",                   "input",   "rent",                                     COLOR["light_gray"], False, False),
        ("  人件費（正社員）",            "input",   "salary_full",                              COLOR["light_gray"], False, False),
        ("  人件費（アルバイト）",        "input",   "salary_part",                              COLOR["light_gray"], False, False),
        ("  広告宣伝費・イベント費",      "input",   "ad",                                       COLOR["light_gray"], False, False),
        ("  EC決済手数料",               "rate",    ("sales_total", "ec_fee_rate"),              COLOR["light_gray"], False, False),
        ("  荷造運賃",                   "input",   "shipping",                                 COLOR["light_gray"], False, False),
        ("  水道光熱費・システム・その他", "input",   "utilities",                                COLOR["light_gray"], False, False),
        ("  販管費合計",                 "sga_sum",  None,                                       COLOR["total_bg"],  True,  False),
        ("",                             "spacer",  None,                                       None,             False,  False),
        ("▌ 営業利益",                   "op_inc",  None,                                       None,             True,   False),
    ]

    # 行番号マップ（ラベルキー → 実際の行番号）
    row_map = {}
    named_rows = [
        "new_sales", "used_sales", "sales_total",
        "new_cost", "used_cost", "cost_total",
        "gross_profit",
        "rent", "salary_full", "salary_part", "ad", "ec_fee", "shipping", "utilities",
        "sga_total", "op_income",
    ]
    row_idx = ROW_OFFSET
    for rd in rows_def:
        row_map[row_idx] = rd
        row_idx += 1

    # 論理行キーと実行番号のマッピング
    logic_keys = [
        "new_sales", "used_sales", "sales_total",
        None,  # spacer
        "new_cost", "used_cost", "cost_total",
        None,
        "gross_profit",
        None,
        "rent", "salary_full", "salary_part", "ad", "ec_fee", "shipping", "utilities",
        "sga_total",
        None,
        "op_income",
    ]

    # 実行行番号の割り当て
    key_to_row = {}
    data_rows = list(rows_def)
    actual_row = ROW_OFFSET
    key_idx = 0
    for rd in data_rows:
        if rd[1] != "section" and rd[1] != "spacer":
            if key_idx < len(logic_keys):
                while key_idx < len(logic_keys) and logic_keys[key_idx] is None:
                    key_idx += 1
                if key_idx < len(logic_keys) and logic_keys[key_idx]:
                    key_to_row[logic_keys[key_idx]] = actual_row
                    key_idx += 1
        actual_row += 1

    # 手動で正確なマッピングを構築
    key_to_row = {}
    r = ROW_OFFSET
    for rd in data_rows:
        lbl, typ, cfg, bg, bold, is_section = rd
        if typ == "section":
            r += 1
            continue
        if typ == "spacer":
            r += 1
            continue
        # 入力・計算行
        if lbl == "  新品売上":
            key_to_row["new_sales"] = r
        elif lbl == "  中古売上":
            key_to_row["used_sales"] = r
        elif "売上合計" in lbl:
            key_to_row["sales_total"] = r
        elif lbl == "  新品原価":
            key_to_row["new_cost"] = r
        elif lbl == "  中古原価":
            key_to_row["used_cost"] = r
        elif "原価合計" in lbl:
            key_to_row["cost_total"] = r
        elif "粗利" in lbl:
            key_to_row["gross_profit"] = r
        elif lbl == "  地代家賃":
            key_to_row["rent"] = r
        elif "正社員" in lbl:
            key_to_row["salary_full"] = r
        elif "アルバイト" in lbl:
            key_to_row["salary_part"] = r
        elif "広告" in lbl:
            key_to_row["ad"] = r
        elif "EC決済" in lbl:
            key_to_row["ec_fee"] = r
        elif "荷造" in lbl:
            key_to_row["shipping"] = r
        elif "水道光熱" in lbl:
            key_to_row["utilities"] = r
        elif "販管費合計" in lbl:
            key_to_row["sga_total"] = r
        elif "営業利益" in lbl:
            key_to_row["op_income"] = r
        r += 1

    # ── セルへの書き込み ──
    current_row = ROW_OFFSET
    for rd in data_rows:
        lbl, typ, cfg, bg, bold, is_section = rd

        ws.row_dimensions[current_row].height = 22 if typ != "spacer" else 8

        if typ == "spacer":
            current_row += 1
            continue

        # ラベルセル
        label_cell = ws.cell(row=current_row, column=COL_LABEL, value=lbl)
        if is_section:
            label_cell.fill = fill(hc)
            label_cell.font = font(bold=True, color="FFFFFF", size=11)
        else:
            label_cell.fill = fill(bg) if bg else fill(COLOR["white"])
            label_cell.font = font(bold=bold, color="1F1F1F", size=10)
        label_cell.alignment = align("left", "center")
        label_cell.border = thin_border()

        if is_section:
            ws.merge_cells(start_row=current_row, start_column=COL_LABEL,
                           end_row=current_row, end_column=COL_TOTAL)
            current_row += 1
            continue

        # データセル（月次）
        for m_idx in range(NUM_MONTHS):
            col = COL_START + m_idx
            cell = ws.cell(row=current_row, column=col)
            cell.border = thin_border()
            cell.fill = fill(bg) if bg else fill(COLOR["white"])

            # 営業利益は色分け（後で条件付きは難しいので固定で薄緑/薄赤はスキップ、シンプルに）
            def col_letter(c): return get_column_letter(c)

            if typ == "input":
                val = p[cfg]
                cell.value = val
                cell.number_format = "#,##0"
                cell.font = font(bold=bold, size=10)
                cell.alignment = align("right", "center")

            elif typ == "rate":
                # 売上×原価率 or 売上×手数料率
                sales_key, rate_key = cfg
                if sales_key == "new_sales":
                    ref_row = key_to_row["new_sales"]
                elif sales_key == "used_sales":
                    ref_row = key_to_row["used_sales"]
                elif sales_key == "sales_total":
                    ref_row = key_to_row["sales_total"]
                else:
                    ref_row = None

                rate_val = p[rate_key]
                if ref_row:
                    ref = f"{col_letter(col)}{ref_row}"
                    cell.value = f"=ROUND({ref}*{rate_val},0)"
                else:
                    cell.value = 0
                cell.number_format = "#,##0"
                cell.font = font(bold=bold, size=10, italic=True)
                cell.alignment = align("right", "center")

            elif typ == "sum2":
                k1, k2 = cfg
                if k1 == "new_sales":
                    r1 = key_to_row["new_sales"]
                    r2 = key_to_row["used_sales"]
                elif k1 == "new_cost":
                    r1 = key_to_row["new_cost"]
                    r2 = key_to_row["used_cost"]
                else:
                    r1 = r2 = current_row
                cl = col_letter(col)
                cell.value = f"={cl}{r1}+{cl}{r2}"
                cell.number_format = "#,##0"
                cell.font = font(bold=True, size=10)
                cell.alignment = align("right", "center")

            elif typ == "gross":
                k1, k2 = cfg
                r1 = key_to_row["sales_total"]
                r2 = key_to_row["cost_total"]
                cl = col_letter(col)
                cell.value = f"={cl}{r1}-{cl}{r2}"
                cell.number_format = "#,##0"
                cell.font = font(bold=True, size=10)
                cell.alignment = align("right", "center")
                cell.fill = fill(COLOR["profit_bg"])

            elif typ == "sga_sum":
                rows_to_sum = [
                    key_to_row["rent"], key_to_row["salary_full"],
                    key_to_row["salary_part"], key_to_row["ad"],
                    key_to_row["ec_fee"], key_to_row["shipping"],
                    key_to_row["utilities"],
                ]
                cl = col_letter(col)
                formula = "+".join([f"{cl}{r}" for r in rows_to_sum])
                cell.value = f"={formula}"
                cell.number_format = "#,##0"
                cell.font = font(bold=True, size=10)
                cell.alignment = align("right", "center")

            elif typ == "op_inc":
                r_gross = key_to_row["gross_profit"]
                r_sga   = key_to_row["sga_total"]
                cl = col_letter(col)
                cell.value = f"={cl}{r_gross}-{cl}{r_sga}"
                cell.number_format = "#,##0"
                cell.font = font(bold=True, size=10)
                cell.alignment = align("right", "center")
                # 動的な色分けは条件付き書式で（ここでは固定色なし）

        # 年間合計列（P列）
        total_cell = ws.cell(row=current_row, column=COL_TOTAL)
        total_cell.border = thin_border()
        total_cell.fill = fill(COLOR["total_bg"]) if bold else fill(bg) if bg else fill(COLOR["white"])
        total_cell.font = font(bold=True, size=10)
        total_cell.alignment = align("right", "center")

        start_cl = col_letter(COL_START)
        end_cl   = col_letter(COL_END)
        total_cell.value = f"=SUM({start_cl}{current_row}:{end_cl}{current_row})"
        total_cell.number_format = "#,##0"

        current_row += 1

    # ─────────────────────────────────
    # 仮定値メモエリア（右下）
    # ─────────────────────────────────
    note_row = current_row + 2
    ws.cell(row=note_row, column=COL_LABEL,
            value="【主要仮定値】").font = font(bold=True, color=hc, size=11)
    ws.cell(row=note_row, column=COL_LABEL).alignment = align("left")

    assumptions = [
        ("新品売上（月次）",  f"{p['new_sales']:,} 円"),
        ("中古売上（月次）",  f"{p['used_sales']:,} 円"),
        ("新品原価率",        f"{int(p['new_cost_rate']*100)}%"),
        ("中古原価率",        f"{int(p['used_cost_rate']*100)}%"),
        ("地代家賃",          f"{p['rent']:,} 円"),
        ("人件費（正社員）",  f"{p['salary_full']:,} 円"),
        ("人件費（アルバイト）", f"{p['salary_part']:,} 円"),
        ("広告・イベント費",  f"{p['ad']:,} 円"),
        ("EC手数料率",        f"{p['ec_fee_rate']*100:.1f}%"),
        ("荷造運賃",          f"{p['shipping']:,} 円"),
        ("水道光熱費等",      f"{p['utilities']:,} 円"),
    ]
    for i, (k, v) in enumerate(assumptions):
        r = note_row + 1 + i
        ws.row_dimensions[r].height = 18
        kc = ws.cell(row=r, column=COL_LABEL, value=f"  {k}")
        kc.font = font(size=10)
        kc.alignment = align("left", "center")
        vc = ws.cell(row=r, column=COL_LABEL + 1, value=v)
        vc.font = font(bold=True, size=10)
        vc.alignment = align("left", "center")

    return key_to_row, COL_START, COL_END, COL_TOTAL, header_row


# ─────────────────────────────────────────────
# 概要シート（3パターン比較ダッシュボード）
# ─────────────────────────────────────────────
def build_overview_sheet(ws, wb, sheet_refs):
    """
    sheet_refs: {
        "A": {"ws": ws_a, "key_to_row": {...}, "COL_START": 3, "COL_END": 15, "COL_TOTAL": 16, "header_row": 5},
        ...
    }
    """
    hc = COLOR["overview_header"]
    ws.sheet_view.showGridLines = True

    # 列幅
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 20
    ws.column_dimensions["F"].width = 3

    # ── タイトル ──
    ws.row_dimensions[1].height = 8
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 8

    title = ws.cell(row=2, column=2, value="トレーディングカードショップ　3パターン年間PLシミュレーション")
    title.font = Font(bold=True, size=18, color=hc, name="メイリオ")
    title.alignment = align("left", "center")
    ws.merge_cells("B2:E2")

    sub = ws.cell(row=3, column=2, value="期間：2026年7月〜2027年7月（13ヶ月）　　単位：円　　※数値を変更すると全シートが自動連動します")
    sub.font = Font(size=10, italic=True, color="595959", name="メイリオ")
    sub.alignment = align("left", "center")
    ws.merge_cells("B3:E3")

    # ── ヘッダー行（Row 5） ──
    headers = [
        ("項　目",          hc,               "FFFFFF"),
        ("パターンA\nEC特化（無店舗）",    PATTERNS["A"]["header_color"], "FFFFFF"),
        ("パターンB\n大型実店舗",           PATTERNS["B"]["header_color"], "FFFFFF"),
        ("パターンC\nハイブリッド",         PATTERNS["C"]["header_color"], "FFFFFF"),
    ]
    ws.row_dimensions[5].height = 36
    for col_idx, (hdr, bg, fg) in enumerate(headers, start=2):
        c = ws.cell(row=5, column=col_idx, value=hdr)
        c.fill = fill(bg)
        c.font = Font(bold=True, color=fg, size=11, name="メイリオ")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = thin_border()

    ws.freeze_panes = ws.cell(row=6, column=3)

    # ── 参照ヘルパー ──
    def ext_ref(pat_key, row_key):
        ref = sheet_refs[pat_key]
        sn  = PATTERNS[pat_key]["name"]
        r   = ref["key_to_row"][row_key]
        col = ref["COL_TOTAL"]
        cl  = get_column_letter(col)
        return f"='{sn}'!{cl}{r}"

    # ── PLデータ行定義 ──
    pl_items = [
        # (ラベル, row_key or None, タイプ)
        ("▌ 売上高",         None,            "section"),
        ("  新品売上",        "new_sales",     "data"),
        ("  中古売上",        "used_sales",    "data"),
        ("  売上合計",        "sales_total",   "total"),
        ("",                  None,            "spacer"),
        ("▌ 売上原価",        None,            "section"),
        ("  新品原価",        "new_cost",      "data"),
        ("  中古原価",        "used_cost",     "data"),
        ("  原価合計",        "cost_total",    "total"),
        ("",                  None,            "spacer"),
        ("▌ 売上総利益（粗利）", "gross_profit", "profit"),
        ("",                  None,            "spacer"),
        ("▌ 販売管理費",      None,            "section"),
        ("  地代家賃",        "rent",          "data"),
        ("  人件費（正社員）", "salary_full",  "data"),
        ("  人件費（アルバイト）", "salary_part", "data"),
        ("  広告・イベント費", "ad",           "data"),
        ("  EC決済手数料",    "ec_fee",        "data"),
        ("  荷造運賃",        "shipping",      "data"),
        ("  水道光熱費等",    "utilities",     "data"),
        ("  販管費合計",      "sga_total",     "total"),
        ("",                  None,            "spacer"),
        ("▌ 営業利益",        "op_income",     "op"),
    ]

    current_row = 6
    for lbl, row_key, typ in pl_items:
        ws.row_dimensions[current_row].height = 8 if typ == "spacer" else 22

        if typ == "spacer":
            current_row += 1
            continue

        # ラベル列
        lc = ws.cell(row=current_row, column=2, value=lbl)
        if typ == "section":
            lc.fill = fill(hc)
            lc.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
            lc.alignment = align("left", "center")
            lc.border = thin_border()
            ws.merge_cells(start_row=current_row, start_column=2,
                           end_row=current_row, end_column=5)
            current_row += 1
            continue

        is_bold = typ in ("total", "profit", "op")
        if typ == "profit":
            bg_c = COLOR["profit_bg"]
        elif typ == "total":
            bg_c = COLOR["total_bg"]
        elif typ == "op":
            bg_c = None
        else:
            bg_c = COLOR["light_gray"]

        lc.fill = fill(bg_c) if bg_c else fill(COLOR["white"])
        lc.font = Font(bold=is_bold, size=10, name="メイリオ")
        lc.alignment = align("left", "center")
        lc.border = thin_border()

        for col_idx, pat_key in enumerate(["A", "B", "C"], start=3):
            dc = ws.cell(row=current_row, column=col_idx)
            dc.value = ext_ref(pat_key, row_key)
            dc.number_format = "#,##0"
            dc.font = Font(bold=is_bold, size=10, name="メイリオ")
            dc.alignment = align("right", "center")
            dc.border = thin_border()
            if typ == "profit":
                dc.fill = fill(COLOR["profit_bg"])
            elif typ == "total":
                dc.fill = fill(COLOR["total_bg"])
            elif typ == "op":
                dc.fill = fill(COLOR["white"])
            else:
                dc.fill = fill(COLOR["light_gray"])

        current_row += 1

    # ── 比較サマリーテーブル ──
    sum_row = current_row + 3
    ws.row_dimensions[sum_row].height = 28
    sh = ws.cell(row=sum_row, column=2, value="★ 年間サマリー比較")
    sh.font = Font(bold=True, size=14, color=hc, name="メイリオ")
    sh.alignment = align("left", "center")
    ws.merge_cells(start_row=sum_row, start_column=2,
                   end_row=sum_row, end_column=5)

    sum_row += 1
    summary_items = [
        ("年間売上合計",     "sales_total"),
        ("年間粗利",         "gross_profit"),
        ("年間販管費合計",   "sga_total"),
        ("年間営業利益",     "op_income"),
    ]
    headers2 = ["指標", "パターンA", "パターンB", "パターンC"]
    header_colors = [hc, PATTERNS["A"]["header_color"],
                     PATTERNS["B"]["header_color"], PATTERNS["C"]["header_color"]]
    ws.row_dimensions[sum_row].height = 28
    for col_idx, (hdr, hclr) in enumerate(zip(headers2, header_colors), start=2):
        c = ws.cell(row=sum_row, column=col_idx, value=hdr)
        c.fill = fill(hclr)
        c.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
        c.alignment = align("center", "center")
        c.border = thin_border()

    for i, (label, row_key) in enumerate(summary_items):
        r = sum_row + 1 + i
        ws.row_dimensions[r].height = 24
        lc = ws.cell(row=r, column=2, value=label)
        lc.font = Font(bold=True, size=11, name="メイリオ")
        lc.alignment = align("left", "center")
        lc.border = thin_border()
        lc.fill = fill(COLOR["section_bg"])

        for col_idx, pat_key in enumerate(["A", "B", "C"], start=3):
            dc = ws.cell(row=r, column=col_idx)
            dc.value = ext_ref(pat_key, row_key)
            dc.number_format = "#,##0"
            dc.font = Font(bold=True, size=11, name="メイリオ")
            dc.alignment = align("right", "center")
            dc.border = thin_border()
            if row_key == "op_income":
                dc.fill = fill(COLOR["profit_bg"])
            else:
                dc.fill = fill(COLOR["section_bg"])

    # 粗利率・営業利益率
    rate_row = sum_row + len(summary_items) + 2
    ws.row_dimensions[rate_row].height = 28
    rh = ws.cell(row=rate_row, column=2, value="★ 収益性指標（年間）")
    rh.font = Font(bold=True, size=14, color=hc, name="メイリオ")
    rh.alignment = align("left", "center")
    ws.merge_cells(start_row=rate_row, start_column=2,
                   end_row=rate_row, end_column=5)

    rate_row += 1
    rate_headers = ["指標", "パターンA", "パターンB", "パターンC"]
    for col_idx, (hdr, hclr) in enumerate(zip(rate_headers, header_colors), start=2):
        c = ws.cell(row=rate_row, column=col_idx, value=hdr)
        c.fill = fill(hclr)
        c.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
        c.alignment = align("center", "center")
        c.border = thin_border()
    ws.row_dimensions[rate_row].height = 28

    rate_items = [
        ("粗利率（%）",   "gross_profit", "sales_total"),
        ("営業利益率（%）", "op_income",  "sales_total"),
    ]
    ref_cache = {}
    for pat_key in ["A", "B", "C"]:
        ref = sheet_refs[pat_key]
        sn  = PATTERNS[pat_key]["name"]
        col = ref["COL_TOTAL"]
        cl  = get_column_letter(col)
        ref_cache[pat_key] = {k: f"'{sn}'!{cl}{v}" for k, v in ref["key_to_row"].items()}

    for i, (label, num_key, den_key) in enumerate(rate_items):
        r = rate_row + 1 + i
        ws.row_dimensions[r].height = 24
        lc = ws.cell(row=r, column=2, value=label)
        lc.font = Font(bold=True, size=11, name="メイリオ")
        lc.alignment = align("left", "center")
        lc.border = thin_border()
        lc.fill = fill(COLOR["section_bg"])

        for col_idx, pat_key in enumerate(["A", "B", "C"], start=3):
            dc = ws.cell(row=r, column=col_idx)
            num_ref = ref_cache[pat_key][num_key]
            den_ref = ref_cache[pat_key][den_key]
            dc.value = f"=IFERROR({num_ref}/{den_ref}*100,0)"
            dc.number_format = "0.0\"%\""
            dc.font = Font(bold=True, size=11, name="メイリオ")
            dc.alignment = align("right", "center")
            dc.border = thin_border()
            dc.fill = fill(COLOR["profit_bg"])


# ─────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────
def main():
    wb = openpyxl.Workbook()

    # デフォルトシートを削除
    wb.remove(wb.active)

    # ── 各パターンシートを作成 ──
    sheet_refs = {}
    for pat_key in ["A", "B", "C"]:
        ws = wb.create_sheet(title=PATTERNS[pat_key]["name"])
        key_to_row, COL_START, COL_END, COL_TOTAL, header_row = build_pl_sheet(ws, pat_key)
        sheet_refs[pat_key] = {
            "ws":          ws,
            "key_to_row":  key_to_row,
            "COL_START":   COL_START,
            "COL_END":     COL_END,
            "COL_TOTAL":   COL_TOTAL,
            "header_row":  header_row,
        }

    # ── 概要シートを最初に挿入 ──
    ws_overview = wb.create_sheet(title="3パターン比較概要", index=0)
    build_overview_sheet(ws_overview, wb, sheet_refs)

    # ── 保存 ──
    filename = "trading_card_shop_PL_simulation.xlsx"
    wb.save(filename)
    print(f"✅ 保存完了: {filename}")
    print("📌 Googleスプレッドシートへのインポート手順:")
    print("   1. Google Drive を開く")
    print("   2. 「新規」→「ファイルのアップロード」でxlsxファイルを選択")
    print("   3. アップロード後、ファイルを右クリック → 「Googleスプレッドシートで開く」")
    print("   4. 数値を変更すると全シートの数式が自動連動します")


if __name__ == "__main__":
    main()

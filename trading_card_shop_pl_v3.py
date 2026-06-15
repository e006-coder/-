"""
トレーディングカードショップ 月次PLシミュレーション v2
「月次営業利益200万円達成」勝ちパターン
2026年7月〜2027年7月（13ヶ月）
"""

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ─────────────────────────────────────────────
# カラー定数
# ─────────────────────────────────────────────
C = {
    "navy":        "0D1F3C",
    "navy2":       "1F3864",
    "navy_light":  "2E4F8A",
    "gold":        "C9A84C",
    "gold_light":  "F0D080",
    "gold_bg":     "FFF8E1",
    "green":       "1A6B3A",
    "green_light":  "2E8B57",
    "green_bg":    "E8F5E9",
    "red":         "C0392B",
    "red_bg":      "FEECEC",
    "teal":        "0D5C63",
    "teal_light":  "17A589",
    "teal_bg":     "E0F4F4",
    "white":       "FFFFFF",
    "off_white":   "FAFAFA",
    "light_gray":  "F2F2F2",
    "mid_gray":    "D9D9D9",
    "dark_gray":   "595959",
    "total_bg":    "FFF3CD",
    "input_bg":    "EBF5FB",
    "section_bg":  "D6EAF8",
    "profit_bg":   "D5F5E3",
    "loss_bg":     "FADBD8",
    "vision_bg":   "0D1F3C",
}

MONTHS = [
    "2026年7月", "2026年8月", "2026年9月", "2026年10月",
    "2026年11月", "2026年12月", "2027年1月", "2027年2月",
    "2027年3月",  "2027年4月",  "2027年5月",  "2027年6月", "2027年7月",
]
N = len(MONTHS)  # 13

# ─────────────────────────────────────────────
# 目標数値（月次）：営業利益200万円
# ─────────────────────────────────────────────
# 売上: 1,000万 / 粗利: 360万 / 販管費: 160万 / 営業利益: 200万
TARGET = {
    "new_sales":        7_000_000,   # 新品売上
    "used_sales":       3_000_000,   # 中古売上
    "new_cost_rate":    0.70,        # 新品原価率
    "used_cost_rate":   0.50,        # 中古原価率
}

# ─────────────────────────────────────────────
# 販管費内訳（月次）
# ─────────────────────────────────────────────
SGA_DETAIL = {
    # 地代家賃
    "rent_shop":         200_000,    # 店舗賃料
    "rent_storage":       50_000,    # 倉庫賃料
    # 人件費（正社員 2名）
    "salary_base1":      400_000,    # 正社員①基本給
    "salary_base2":      250_000,    # 正社員②基本給
    "salary_social":     110_000,    # 社会保険料（会社負担 約20%）
    # 人件費（アルバイト）
    "part_wage":         130_000,    # アルバイト賃金
    "part_transport":     10_000,    # アルバイト交通費
    # 広告宣伝費・イベント費
    "ad_sns":             60_000,    # SNS広告（Instagram/X）
    "ad_event":           50_000,    # イベント出展費
    "ad_material":        20_000,    # 販促物・スリーブ等
    # EC決済手数料（売上1,000万×手数料率）
    "ec_mercari":         70_000,    # メルカリShops（約1%）
    "ec_card":            70_000,    # クレジットカード決済（約1%）
    # 荷造運賃
    "ship_material":      30_000,    # 発送資材（段ボール等）
    "ship_fee":           70_000,    # 配送費（ヤマト等）
    # 水道光熱費・システム・その他
    "util_electric":      30_000,    # 電気代
    "util_pos":           15_000,    # POSシステム（STORES等）
    "util_accounting":     5_000,    # 会計ソフト（freee等）
    "util_comm":          10_000,    # 通信費
    "util_misc":          20_000,    # 雑費・消耗品
}

# ─────────────────────────────────────────────
# スタイルヘルパー
# ─────────────────────────────────────────────
def F(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color="1A1A1A", size=10, italic=False, name="メイリオ"):
    return Font(bold=bold, color=color, size=size, italic=italic, name=name)

def A(h="right", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def border(style="thin", color="C8C8C8"):
    s = Side(style=style, color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def thick_bottom(color="808080"):
    return Border(bottom=Side(style="medium", color=color))

def set_cell(ws, row, col, value=None, fill_color=None, bold=False,
             font_color="1A1A1A", font_size=10, h_align="right",
             v_align="center", num_fmt=None, italic=False,
             wrap=False, border_on=True):
    c = ws.cell(row=row, column=col, value=value)
    if fill_color:
        c.fill = F(fill_color)
    c.font = font(bold=bold, color=font_color, size=font_size, italic=italic)
    c.alignment = A(h_align, v_align, wrap)
    if border_on:
        c.border = border()
    if num_fmt:
        c.number_format = num_fmt
    return c

def CL(col): return get_column_letter(col)


# ══════════════════════════════════════════════════════════
# Sheet 1: ビジョン・戦略シート
# ══════════════════════════════════════════════════════════
def build_vision_sheet(ws):
    ws.sheet_view.showGridLines = True
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 60
    ws.column_dimensions["D"].width = 4

    def section(row, title, height=32):
        ws.row_dimensions[row].height = height
        c = ws.cell(row=row, column=2, value=title)
        c.fill = F(C["navy"])
        c.font = Font(bold=True, color="FFFFFF", size=13, name="メイリオ")
        c.alignment = A("left", "center")
        c.border = border()
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)

    def row_item(row, label, text, height=20, label_color=C["navy2"], label_fc="FFFFFF",
                 text_bg=C["off_white"], text_fc="1A1A1A", bold_text=False):
        ws.row_dimensions[row].height = height
        lc = ws.cell(row=row, column=2, value=label)
        lc.fill = F(label_color)
        lc.font = Font(bold=True, color=label_fc, size=10, name="メイリオ")
        lc.alignment = A("left", "center")
        lc.border = border()
        tc = ws.cell(row=row, column=3, value=text)
        tc.fill = F(text_bg)
        tc.font = Font(bold=bold_text, color=text_fc, size=10, name="メイリオ")
        tc.alignment = A("left", "center", wrap=True)
        tc.border = border()

    # タイトル
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 50
    ws.merge_cells("B2:C2")
    t = ws.cell(row=2, column=2,
                value="本気でカードで儲ける　トレーディングカードショップ　事業ビジョン")
    t.fill = F(C["navy"])
    t.font = Font(bold=True, color=C["gold"], size=18, name="メイリオ")
    t.alignment = A("center", "center")

    ws.row_dimensions[3].height = 24
    ws.merge_cells("B3:C3")
    s = ws.cell(row=3, column=2,
                value="KGI：月次営業利益200万円　｜　ポケモン・ワンピース主軸　｜　2026年7月スタート")
    s.fill = F(C["navy2"])
    s.font = Font(bold=False, color=C["gold_light"], size=11, italic=True, name="メイリオ")
    s.alignment = A("center", "center")

    ws.row_dimensions[4].height = 10

    # ── ミッション・ビジョン ──
    r = 5
    section(r, "🎯  ミッション　／　ビジョン")
    r += 1
    row_item(r, "ミッション",
             "「カードに本気な人と、カードを楽しみたい人を、最高の体験でつなぐ」\n"
             "買取・販売・イベントを通じて、地域とオンラインの両方でカルチャーの拠点となる。",
             height=44, text_bg=C["gold_bg"], bold_text=True)
    r += 1
    row_item(r, "ビジョン",
             "3年以内に年商3億・月次利益500万円を達成し、直営2店舗＋EC年商1億の\n"
             "「ポケモン×ワンピース専門ショップ」としてブランド確立を目指す。",
             height=44, text_bg=C["gold_bg"])
    r += 1

    ws.row_dimensions[r].height = 10
    r += 1

    # ── 収益モデル ──
    section(r, "💴  収益モデル　「月次売上1,000万・営業利益200万」の構造")
    r += 1
    model_items = [
        ("新品販売（ECメイン）",
         "売上700万 / 原価率70% / 粗利210万　←　ボックス・パック・シングル。\n"
         "メルカリShops・自社EC・実店舗の3チャネル展開で在庫回転率を最大化。"),
        ("中古・シングル買取販売",
         "売上300万 / 原価率50% / 粗利150万　←　個人買取が最大の利益源。\n"
         "「その場で査定・即現金」を武器に買取量を積み上げ、粗利50%以上を死守する。"),
        ("販管費コントロール",
         "月次販管費160万以内に抑制。人件費・家賃・広告の3大費目を毎月モニタリング。\n"
         "EC手数料はチャネルミックスで実質2%未満に最適化する。"),
        ("スケール戦略",
         "達成後は中古買取強化（粗利率が高い）・イベント主催（原価ほぼゼロ）・\n"
         "サブスク封入パック等で高粗利の売上ミックスを改善し営業利益率を30%以上へ。"),
    ]
    for lbl, txt in model_items:
        row_item(r, lbl, txt, height=44)
        r += 1

    ws.row_dimensions[r].height = 10
    r += 1

    # ── KPI ──
    section(r, "📊  月次KPI　ターゲット（200万利益達成ライン）")
    r += 1
    kpi_items = [
        ("月次売上目標",       "1,000万円（新品700万＋中古300万）"),
        ("月次粗利目標",       "360万円（粗利率36%）"),
        ("月次販管費上限",     "160万円（粗利の44%以内）"),
        ("月次営業利益目標",   "200万円（利益率20%）　★KGI"),
        ("新品在庫回転率",     "月2.5回転以上（適正在庫: 280万円規模）"),
        ("中古買取件数",       "月80件以上（平均単価3.75万円/件）"),
        ("EC売上比率",         "新品の50%以上はEC経由（送料・手数料コスト最適化）"),
        ("SNSフォロワー",      "開店6ヶ月でInstagram/X 合計5,000人以上"),
    ]
    for lbl, txt in kpi_items:
        row_item(r, lbl, txt, height=22,
                 label_color=C["teal"], label_fc="FFFFFF",
                 text_bg=C["teal_bg"], text_fc="0D3B44")
        r += 1

    ws.row_dimensions[r].height = 10
    r += 1

    # ── ロードマップ ──
    section(r, "🗺️  成長ロードマップ")
    r += 1
    roadmap_items = [
        ("Phase 1　立上期\n（〜3ヶ月）",
         "【仕込み】在庫確保・EC出品体制構築・SNSアカウント開設。\n"
         "買取ルート開拓（個人・カードショップ・オークション）。売上500万→700万ランプアップ。"),
        ("Phase 2　安定期\n（4〜9ヶ月）",
         "【稼ぐ】月次売上1,000万・利益200万の安定達成。\n"
         "リピーター育成・メルマガ・LINE公式アカウントで顧客ロイヤルティ強化。"),
        ("Phase 3　拡張期\n（10〜13ヶ月）",
         "【攻める】大型イベント主催（トーナメント等）・限定BOX予約販売導入。\n"
         "利益の一部を2号店の保証金・初期在庫に積立開始。目標: 累計利益2,500万円突破。"),
        ("Phase 4　スケール\n（2年目〜）",
         "【広げる】直営2店舗目 or フランチャイズ展開・法人化・外部資本調達検討。\n"
         "年商3億・月次利益500万円達成で「業界標準の独立カードショップ」モデルを確立。"),
    ]
    for lbl, txt in roadmap_items:
        row_item(r, lbl, txt, height=50,
                 label_color=C["green"], label_fc="FFFFFF",
                 text_bg=C["green_bg"], text_fc="1A3A1A")
        r += 1

    ws.row_dimensions[r].height = 10
    r += 1

    # ── 勝ち筋 ──
    section(r, "⚡  絶対に外せない勝ち筋　3原則")
    r += 1
    win_items = [
        ("原則①  買取が命",
         "「売る前に買う」。高粗利の中古シングルを安定調達できれば利益は安定する。\n"
         "買取価格の査定精度を上げ、他店より1〜5%高く買って、2〜3倍で売る構造を作る。"),
        ("原則②  在庫を腐らせない",
         "新品は「封入期待値×市場相場」を毎日ウォッチし、需要ピーク前に仕入れ、ピークで売り切る。\n"
         "売れ残りは即EC値引き・抱き合わせ販売で現金化。在庫は「死に金」と心得る。"),
        ("原則③  数字で経営する",
         "このPLを毎月更新し、粗利率・営業利益・在庫回転率の3指標を週次でチェック。\n"
         "「なんとなく売れてる」ではなく「なぜ儲かったか/損したか」を数字で語れる経営者になる。"),
    ]
    for lbl, txt in win_items:
        row_item(r, lbl, txt, height=50,
                 label_color=C["navy"], label_fc=C["gold"],
                 text_bg=C["gold_bg"], text_fc="2C1A00", bold_text=False)
        r += 1


# ══════════════════════════════════════════════════════════
# Sheet 2: 月次PL
# ══════════════════════════════════════════════════════════
def build_pl_sheet(ws):
    ws.sheet_view.showGridLines = True

    COL_LABEL = 2
    COL_START = 3
    COL_END   = COL_START + N - 1
    COL_TOTAL = COL_END + 1

    # 列幅
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 30
    for col in range(COL_START, COL_TOTAL + 1):
        ws.column_dimensions[CL(col)].width = 14

    # ── タイトル ──
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 44
    ws.row_dimensions[3].height = 22
    ws.row_dimensions[4].height = 10

    ws.merge_cells(start_row=2, start_column=COL_LABEL, end_row=2, end_column=COL_TOTAL)
    t = ws.cell(row=2, column=COL_LABEL,
                value="月次PLシミュレーション　「月次営業利益200万円」達成プラン")
    t.fill = F(C["navy"])
    t.font = Font(bold=True, color=C["gold"], size=16, name="メイリオ")
    t.alignment = A("left", "center")

    ws.merge_cells(start_row=3, start_column=COL_LABEL, end_row=3, end_column=COL_TOTAL)
    s = ws.cell(row=3, column=COL_LABEL,
                value="期間：2026年7月〜2027年7月（13ヶ月）　｜　売上1,000万 / 粗利360万 / 販管費160万 / 営業利益200万　｜　単位：円")
    s.fill = F(C["navy2"])
    s.font = Font(italic=True, color="CCCCCC", size=10, name="メイリオ")
    s.alignment = A("left", "center")

    # ── ヘッダー行（Row 5）──
    HDR = 5
    ws.row_dimensions[HDR].height = 28
    set_cell(ws, HDR, COL_LABEL, "項　目", fill_color=C["navy"], bold=True,
             font_color="FFFFFF", font_size=11, h_align="center")
    for i, m in enumerate(MONTHS):
        set_cell(ws, HDR, COL_START + i, m, fill_color=C["navy"], bold=True,
                 font_color="FFFFFF", font_size=10, h_align="center")
    set_cell(ws, HDR, COL_TOTAL, "年間合計", fill_color=C["gold"], bold=True,
             font_color=C["navy"], font_size=11, h_align="center")

    ws.freeze_panes = ws.cell(row=HDR + 1, column=COL_START)

    # ── 行定義ヘルパー ──
    key_to_row = {}
    R = HDR + 1

    def section_row(label):
        nonlocal R
        ws.row_dimensions[R].height = 24
        ws.merge_cells(start_row=R, start_column=COL_LABEL, end_row=R, end_column=COL_TOTAL)
        c = ws.cell(row=R, column=COL_LABEL, value=label)
        c.fill = F(C["navy2"])
        c.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
        c.alignment = A("left", "center")
        c.border = border()
        R += 1

    def spacer():
        nonlocal R
        ws.row_dimensions[R].height = 6
        R += 1

    def input_row(key, label, monthly_val, bg=C["input_bg"], italic_val=False):
        nonlocal R
        ws.row_dimensions[R].height = 22
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=10, bold=False)
        for i in range(N):
            c = ws.cell(row=R, column=COL_START + i, value=monthly_val)
            c.fill = F(bg)
            c.font = Font(bold=False, color="1A1A1A", size=10,
                          italic=italic_val, name="メイリオ")
            c.alignment = A("right")
            c.border = border()
            c.number_format = "#,##0"
        # 年間合計
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["total_bg"])
        tc.font = Font(bold=True, size=10, name="メイリオ")
        tc.alignment = A("right")
        tc.border = border()
        tc.number_format = "#,##0"
        key_to_row[key] = R
        R += 1

    def formula_row(key, label, formula_fn, bg=C["input_bg"],
                    bold=False, italic=True):
        """formula_fn(col_letter, row_number) -> formula string"""
        nonlocal R
        ws.row_dimensions[R].height = 22
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=10, bold=bold)
        for i in range(N):
            col = COL_START + i
            c = ws.cell(row=R, column=col)
            c.value = formula_fn(CL(col), R)
            c.fill = F(bg)
            c.font = Font(bold=bold, color="1A1A1A", size=10,
                          italic=italic, name="メイリオ")
            c.alignment = A("right")
            c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["total_bg"])
        tc.font = Font(bold=True, size=10, name="メイリオ")
        tc.alignment = A("right")
        tc.border = border()
        tc.number_format = "#,##0"
        key_to_row[key] = R
        R += 1

    def total_row(key, label, formula_fn, bg=C["total_bg"], bold=True):
        nonlocal R
        ws.row_dimensions[R].height = 24
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=10, bold=bold)
        for i in range(N):
            col = COL_START + i
            c = ws.cell(row=R, column=col)
            c.value = formula_fn(CL(col), R)
            c.fill = F(bg)
            c.font = Font(bold=bold, size=10, name="メイリオ")
            c.alignment = A("right")
            c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["total_bg"])
        tc.font = Font(bold=True, size=10, name="メイリオ")
        tc.alignment = A("right")
        tc.border = border()
        tc.number_format = "#,##0"
        key_to_row[key] = R
        R += 1

    def profit_row(key, label, formula_fn, is_profit=True):
        nonlocal R
        bg = C["profit_bg"] if is_profit else C["loss_bg"]
        ws.row_dimensions[R].height = 28
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=11, bold=True)
        for i in range(N):
            col = COL_START + i
            c = ws.cell(row=R, column=col)
            c.value = formula_fn(CL(col), R)
            c.fill = F(bg)
            c.font = Font(bold=True, size=11, name="メイリオ")
            c.alignment = A("right")
            c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["gold_bg"])
        tc.font = Font(bold=True, size=11, color=C["navy"], name="メイリオ")
        tc.alignment = A("right")
        tc.border = border()
        tc.number_format = "#,##0"
        key_to_row[key] = R
        R += 1

    # ━━━━━━ 売上高 ━━━━━━
    section_row("▌ 売上高")
    input_row("new_sales",   "  新品売上",                TARGET["new_sales"])
    input_row("used_sales",  "  中古売上",                TARGET["used_sales"])
    total_row("sales_total", "  売上合計",
              lambda cl, r: f"={cl}{key_to_row['new_sales']}+{cl}{key_to_row['used_sales']}")
    spacer()

    # ━━━━━━ 売上原価 ━━━━━━
    section_row("▌ 売上原価")
    formula_row("new_cost",  "  新品原価（原価率70%）",
                lambda cl, r: f"=ROUND({cl}{key_to_row['new_sales']}*{TARGET['new_cost_rate']},0)")
    formula_row("used_cost", "  中古原価（原価率50%）",
                lambda cl, r: f"=ROUND({cl}{key_to_row['used_sales']}*{TARGET['used_cost_rate']},0)")
    total_row("cost_total",  "  原価合計",
              lambda cl, r: f"={cl}{key_to_row['new_cost']}+{cl}{key_to_row['used_cost']}")
    spacer()

    # ━━━━━━ 粗利 ━━━━━━
    profit_row("gross_profit", "▌ 売上総利益（粗利）　目標：360万円/月",
               lambda cl, r: f"={cl}{key_to_row['sales_total']}-{cl}{key_to_row['cost_total']}")
    spacer()

    # ━━━━━━ 販管費 ━━━━━━
    section_row("▌ 販売管理費　※詳細内訳は「販管費内訳」シート参照")

    sga_sheet_name = "販管費内訳"

    def sga_ref_fn(sga_key):
        """販管費内訳シートの年次合計列（P列=列16）の月次行を参照"""
        # 販管費内訳シートの構造は後で決まるので、まずは入力値で仮置きし、
        # 後でbuild_sga_sheet内でrow番号を返す設計にする
        return sga_key  # placeholder

    # 販管費は内訳シート参照の数式で埋める（後続でrow番号を割り当て）
    # ここでは先に入力値で仮建て、後続でsga_row_mapを使い数式置き換え
    sga_input_vals = {
        "rent":         SGA_DETAIL["rent_shop"] + SGA_DETAIL["rent_storage"],
        "salary_full":  SGA_DETAIL["salary_base1"] + SGA_DETAIL["salary_base2"] + SGA_DETAIL["salary_social"],
        "salary_part":  SGA_DETAIL["part_wage"] + SGA_DETAIL["part_transport"],
        "ad":           SGA_DETAIL["ad_sns"] + SGA_DETAIL["ad_event"] + SGA_DETAIL["ad_material"],
        "ec_fee":       SGA_DETAIL["ec_mercari"] + SGA_DETAIL["ec_card"],
        "shipping":     SGA_DETAIL["ship_material"] + SGA_DETAIL["ship_fee"],
        "utilities":    (SGA_DETAIL["util_electric"] + SGA_DETAIL["util_pos"] +
                         SGA_DETAIL["util_accounting"] + SGA_DETAIL["util_comm"] +
                         SGA_DETAIL["util_misc"]),
    }
    sga_labels = {
        "rent":        "  地代家賃",
        "salary_full": "  人件費（正社員）",
        "salary_part": "  人件費（アルバイト）",
        "ad":          "  広告宣伝費・イベント費",
        "ec_fee":      "  EC決済手数料",
        "shipping":    "  荷造運賃",
        "utilities":   "  水道光熱費・システム・その他",
    }
    sga_keys_order = ["rent", "salary_full", "salary_part", "ad", "ec_fee", "shipping", "utilities"]

    # 販管費行は一旦入力値で書き、後でsga_row_mapを受けて数式に差し替える
    sga_pl_rows = {}
    for k in sga_keys_order:
        input_row(k, sga_labels[k], sga_input_vals[k])
        sga_pl_rows[k] = key_to_row[k]

    # 販管費合計
    def sga_total_fn(cl, r):
        parts = "+".join([f"{cl}{sga_pl_rows[k]}" for k in sga_keys_order])
        return f"={parts}"
    total_row("sga_total", "  販管費合計",  sga_total_fn, bg=C["total_bg"])
    spacer()

    # ━━━━━━ 営業利益 ━━━━━━
    profit_row("op_income",
               "▌ 営業利益　★目標：200万円/月",
               lambda cl, r: f"={cl}{key_to_row['gross_profit']}-{cl}{key_to_row['sga_total']}")

    # ── 粗利率・営業利益率行 ──
    spacer()
    ws.row_dimensions[R].height = 20
    set_cell(ws, R, COL_LABEL, "  粗利率（%）",
             fill_color=C["section_bg"], h_align="left", font_size=10, bold=True)
    for i in range(N):
        col = COL_START + i
        cl  = CL(col)
        c   = ws.cell(row=R, column=col)
        c.value = (f"=IFERROR({cl}{key_to_row['gross_profit']}"
                   f"/{cl}{key_to_row['sales_total']}*100,0)")
        c.fill = F(C["section_bg"])
        c.font = Font(bold=True, size=10, color=C["navy"], name="メイリオ")
        c.alignment = A("right")
        c.border = border()
        c.number_format = '0.0"%"'
    tc = ws.cell(row=R, column=COL_TOTAL)
    tc.value = (f"=IFERROR({CL(COL_TOTAL)}{key_to_row['gross_profit']}"
                f"/{CL(COL_TOTAL)}{key_to_row['sales_total']}*100,0)")
    tc.fill = F(C["gold_bg"])
    tc.font = Font(bold=True, size=10, color=C["navy"], name="メイリオ")
    tc.alignment = A("right")
    tc.border = border()
    tc.number_format = '0.0"%"'
    R += 1

    ws.row_dimensions[R].height = 20
    set_cell(ws, R, COL_LABEL, "  営業利益率（%）",
             fill_color=C["profit_bg"], h_align="left", font_size=10, bold=True)
    for i in range(N):
        col = COL_START + i
        cl  = CL(col)
        c   = ws.cell(row=R, column=col)
        c.value = (f"=IFERROR({cl}{key_to_row['op_income']}"
                   f"/{cl}{key_to_row['sales_total']}*100,0)")
        c.fill = F(C["profit_bg"])
        c.font = Font(bold=True, size=10, color=C["green"], name="メイリオ")
        c.alignment = A("right")
        c.border = border()
        c.number_format = '0.0"%"'
    tc = ws.cell(row=R, column=COL_TOTAL)
    tc.value = (f"=IFERROR({CL(COL_TOTAL)}{key_to_row['op_income']}"
                f"/{CL(COL_TOTAL)}{key_to_row['sales_total']}*100,0)")
    tc.fill = F(C["gold_bg"])
    tc.font = Font(bold=True, size=10, color=C["green"], name="メイリオ")
    tc.alignment = A("right")
    tc.border = border()
    tc.number_format = '0.0"%"'

    return key_to_row, COL_START, COL_END, COL_TOTAL, sga_pl_rows


# ══════════════════════════════════════════════════════════
# Sheet 3: 販管費内訳シート
# ══════════════════════════════════════════════════════════
def build_sga_sheet(ws, pl_ws_name, pl_sga_rows, COL_START_PL, COL_END_PL, COL_TOTAL_PL):
    ws.sheet_view.showGridLines = True

    COL_LABEL = 2
    COL_CAT   = 3   # 大カテゴリ
    COL_START = 4
    COL_END   = COL_START + N - 1
    COL_TOTAL = COL_END + 1

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 14
    for col in range(COL_START, COL_TOTAL + 1):
        ws.column_dimensions[CL(col)].width = 13

    # タイトル
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 10

    ws.merge_cells(start_row=2, start_column=COL_LABEL, end_row=2, end_column=COL_TOTAL)
    t = ws.cell(row=2, column=COL_LABEL, value="販管費内訳　詳細シート")
    t.fill = F(C["navy"])
    t.font = Font(bold=True, color=C["gold"], size=16, name="メイリオ")
    t.alignment = A("left", "center")

    ws.merge_cells(start_row=3, start_column=COL_LABEL, end_row=3, end_column=COL_TOTAL)
    s = ws.cell(row=3, column=COL_LABEL,
                value="各費目の内訳を入力 → PLシートの合計行に自動反映　｜　単位：円")
    s.fill = F(C["navy2"])
    s.font = Font(italic=True, color="CCCCCC", size=10, name="メイリオ")
    s.alignment = A("left", "center")

    HDR = 5
    ws.row_dimensions[HDR].height = 28
    set_cell(ws, HDR, COL_LABEL, "費目（内訳）", fill_color=C["navy"], bold=True,
             font_color="FFFFFF", font_size=11, h_align="center")
    set_cell(ws, HDR, COL_CAT, "PL科目", fill_color=C["navy"], bold=True,
             font_color="FFFFFF", font_size=10, h_align="center")
    for i, m in enumerate(MONTHS):
        set_cell(ws, HDR, COL_START + i, m, fill_color=C["navy"], bold=True,
                 font_color="FFFFFF", font_size=10, h_align="center")
    set_cell(ws, HDR, COL_TOTAL, "年間合計", fill_color=C["gold"], bold=True,
             font_color=C["navy"], font_size=11, h_align="center")

    ws.freeze_panes = ws.cell(row=HDR + 1, column=COL_START)

    R = HDR + 1
    sga_category_rows = {}  # {pl_key: [row numbers of sub-items]}

    def sub_section(cat_label):
        nonlocal R
        ws.row_dimensions[R].height = 22
        ws.merge_cells(start_row=R, start_column=COL_LABEL, end_row=R, end_column=COL_TOTAL)
        c = ws.cell(row=R, column=COL_LABEL, value=cat_label)
        c.fill = F(C["teal"])
        c.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
        c.alignment = A("left", "center")
        c.border = border()
        R += 1

    def detail_row(label, pl_key, monthly_val):
        nonlocal R
        ws.row_dimensions[R].height = 20
        set_cell(ws, R, COL_LABEL, f"    {label}",
                 fill_color=C["input_bg"], h_align="left", font_size=10)
        # PL科目列
        cat_c = ws.cell(row=R, column=COL_CAT)
        cat_c.fill = F(C["section_bg"])
        cat_c.font = Font(size=9, color=C["navy2"], name="メイリオ")
        cat_c.alignment = A("center", "center")
        cat_c.border = border()
        # 入力欄
        for i in range(N):
            c = ws.cell(row=R, column=COL_START + i, value=monthly_val)
            c.fill = F(C["input_bg"])
            c.font = Font(size=10, name="メイリオ")
            c.alignment = A("right")
            c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["total_bg"])
        tc.font = Font(bold=True, size=10, name="メイリオ")
        tc.alignment = A("right")
        tc.border = border()
        tc.number_format = "#,##0"
        sga_category_rows.setdefault(pl_key, []).append(R)
        return R

    def sum_row(pl_key, label, pl_label):
        nonlocal R
        ws.row_dimensions[R].height = 24
        set_cell(ws, R, COL_LABEL, f"  {label}  ←  PLシートの「{pl_label}」に連動",
                 fill_color=C["total_bg"], h_align="left", font_size=10, bold=True)
        set_cell(ws, R, COL_CAT, pl_label,
                 fill_color=C["total_bg"], h_align="center", font_size=9, bold=True,
                 font_color=C["navy"])
        sub_rows = sga_category_rows.get(pl_key, [])
        for i in range(N):
            col = COL_START + i
            cl  = CL(col)
            parts = "+".join([f"{cl}{sr}" for sr in sub_rows])
            c = ws.cell(row=R, column=col)
            c.value = f"={parts}" if parts else "=0"
            c.fill = F(C["total_bg"])
            c.font = Font(bold=True, size=10, name="メイリオ")
            c.alignment = A("right")
            c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["gold_bg"])
        tc.font = Font(bold=True, size=10, color=C["navy"], name="メイリオ")
        tc.alignment = A("right")
        tc.border = border()
        tc.number_format = "#,##0"
        sga_category_rows[f"{pl_key}_total"] = R
        R += 1

    def spacer(h=6):
        nonlocal R
        ws.row_dimensions[R].height = h
        R += 1

    # ━━━━━━ 地代家賃 ━━━━━━
    sub_section("▌ 地代家賃")
    detail_row("店舗賃料",   "rent", SGA_DETAIL["rent_shop"])
    detail_row("倉庫賃料",   "rent", SGA_DETAIL["rent_storage"])
    R += 1  # catラベル用の行番号調整（detail_rowで+1してないので不要 → reset）
    R -= 1  # 戻す（detail_rowはR+=1している）
    # ↑ detail_row内でRをインクリメントしないので手動
    R += 1  # 最後のdetail_rowの後に+1
    sum_row("rent", "地代家賃　計", "地代家賃")
    spacer()

    # ━━━━━━ 人件費（正社員） ━━━━━━
    sub_section("▌ 人件費（正社員）")
    detail_row("正社員①　基本給",        "salary_full", SGA_DETAIL["salary_base1"])
    R += 1
    detail_row("正社員②　基本給",        "salary_full", SGA_DETAIL["salary_base2"])
    R += 1
    detail_row("社会保険料（会社負担）",  "salary_full", SGA_DETAIL["salary_social"])
    R += 1
    sum_row("salary_full", "人件費（正社員）　計", "人件費（正社員）")
    spacer()

    # ━━━━━━ 人件費（アルバイト） ━━━━━━
    sub_section("▌ 人件費（アルバイト）")
    detail_row("アルバイト賃金",  "salary_part", SGA_DETAIL["part_wage"])
    R += 1
    detail_row("交通費",          "salary_part", SGA_DETAIL["part_transport"])
    R += 1
    sum_row("salary_part", "人件費（アルバイト）　計", "人件費（アルバイト）")
    spacer()

    # ━━━━━━ 広告宣伝費・イベント費 ━━━━━━
    sub_section("▌ 広告宣伝費・イベント費")
    detail_row("SNS広告（Instagram/X）", "ad", SGA_DETAIL["ad_sns"])
    R += 1
    detail_row("イベント出展費",          "ad", SGA_DETAIL["ad_event"])
    R += 1
    detail_row("販促物・スリーブ等",      "ad", SGA_DETAIL["ad_material"])
    R += 1
    sum_row("ad", "広告宣伝費・イベント費　計", "広告宣伝費・イベント費")
    spacer()

    # ━━━━━━ EC決済手数料 ━━━━━━
    sub_section("▌ EC決済手数料")
    detail_row("メルカリShops手数料（約1%）",      "ec_fee", SGA_DETAIL["ec_mercari"])
    R += 1
    detail_row("クレジットカード決済手数料（約1%）", "ec_fee", SGA_DETAIL["ec_card"])
    R += 1
    sum_row("ec_fee", "EC決済手数料　計", "EC決済手数料")
    spacer()

    # ━━━━━━ 荷造運賃 ━━━━━━
    sub_section("▌ 荷造運賃")
    detail_row("発送資材（段ボール・プチプチ等）", "shipping", SGA_DETAIL["ship_material"])
    R += 1
    detail_row("配送費（ヤマト・佐川等）",          "shipping", SGA_DETAIL["ship_fee"])
    R += 1
    sum_row("shipping", "荷造運賃　計", "荷造運賃")
    spacer()

    # ━━━━━━ 水道光熱費・システム・その他 ━━━━━━
    sub_section("▌ 水道光熱費・システム・その他")
    detail_row("電気代",                            "utilities", SGA_DETAIL["util_electric"])
    R += 1
    detail_row("POSシステム（STORES・スマレジ等）", "utilities", SGA_DETAIL["util_pos"])
    R += 1
    detail_row("会計ソフト（freee等）",             "utilities", SGA_DETAIL["util_accounting"])
    R += 1
    detail_row("通信費",                            "utilities", SGA_DETAIL["util_comm"])
    R += 1
    detail_row("雑費・消耗品",                      "utilities", SGA_DETAIL["util_misc"])
    R += 1
    sum_row("utilities", "水道光熱費・システム・その他　計", "水道光熱費・システム・その他")
    spacer()
    spacer()

    # ━━━━━━ 販管費総合計 ━━━━━━
    ws.row_dimensions[R].height = 30
    set_cell(ws, R, COL_LABEL, "▌ 販管費　総合計",
             fill_color=C["navy"], bold=True, font_color=C["gold"],
             font_size=13, h_align="left")
    set_cell(ws, R, COL_CAT, "合　計",
             fill_color=C["navy"], bold=True, font_color=C["gold"],
             font_size=11, h_align="center")
    total_sub_rows = [
        sga_category_rows.get("rent_total"),
        sga_category_rows.get("salary_full_total"),
        sga_category_rows.get("salary_part_total"),
        sga_category_rows.get("ad_total"),
        sga_category_rows.get("ec_fee_total"),
        sga_category_rows.get("shipping_total"),
        sga_category_rows.get("utilities_total"),
    ]
    total_sub_rows = [r2 for r2 in total_sub_rows if r2]
    for i in range(N):
        col = COL_START + i
        cl  = CL(col)
        parts = "+".join([f"{cl}{sr}" for sr in total_sub_rows])
        c = ws.cell(row=R, column=col)
        c.value = f"={parts}"
        c.fill = F(C["gold_bg"])
        c.font = Font(bold=True, size=12, color=C["navy"], name="メイリオ")
        c.alignment = A("right")
        c.border = border()
        c.number_format = "#,##0"
    tc = ws.cell(row=R, column=COL_TOTAL)
    tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
    tc.fill = F(C["gold"])
    tc.font = Font(bold=True, size=12, color=C["navy"], name="メイリオ")
    tc.alignment = A("right")
    tc.border = border()
    tc.number_format = "#,##0"

    return sga_category_rows, COL_START, COL_END, COL_TOTAL


# ══════════════════════════════════════════════════════════
# Sheet 4: ダッシュボード（概要）
# ══════════════════════════════════════════════════════════
def build_dashboard_sheet(ws, pl_ws_name, pl_key_to_row,
                          PL_COL_START, PL_COL_END, PL_COL_TOTAL):
    ws.sheet_view.showGridLines = True

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 20
    ws.column_dimensions["F"].width = 20

    # タイトル
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 44
    ws.row_dimensions[3].height = 22
    ws.row_dimensions[4].height = 10

    ws.merge_cells("B2:F2")
    t = ws.cell(row=2, column=2,
                value="ダッシュボード　｜　月次営業利益200万円　達成モニタリング")
    t.fill = F(C["navy"])
    t.font = Font(bold=True, color=C["gold"], size=16, name="メイリオ")
    t.alignment = A("left", "center")

    ws.merge_cells("B3:F3")
    s = ws.cell(row=3, column=2,
                value="※ 各数値はPLシート・販管費内訳シートと連動しています。数値を変更するとこのシートも自動更新されます。")
    s.fill = F(C["navy2"])
    s.font = Font(italic=True, color="CCCCCC", size=10, name="メイリオ")
    s.alignment = A("left", "center")

    def ext(row_key, col=None):
        r = pl_key_to_row[row_key]
        c = CL(col or PL_COL_TOTAL)
        return f"='{pl_ws_name}'!{c}{r}"

    def ext_col(row_key, month_idx):
        r = pl_key_to_row[row_key]
        c = CL(PL_COL_START + month_idx)
        return f"='{pl_ws_name}'!{c}{r}"

    # ── 年間サマリーカード ──
    R = 5
    ws.row_dimensions[R].height = 28
    ws.merge_cells(f"B{R}:F{R}")
    sh = ws.cell(row=R, column=2, value="📊  年間サマリー（13ヶ月合計）")
    sh.fill = F(C["teal"])
    sh.font = Font(bold=True, color="FFFFFF", size=13, name="メイリオ")
    sh.alignment = A("left", "center")
    sh.border = border()
    R += 1

    cards = [
        ("年間売上合計",       "sales_total",  C["navy2"],    "FFFFFF", "#,##0"),
        ("年間粗利",           "gross_profit", C["green"],    "FFFFFF", "#,##0"),
        ("年間販管費",         "sga_total",    C["dark_gray"],"FFFFFF", "#,##0"),
        ("年間営業利益　★",   "op_income",    C["gold"],     C["navy"], "#,##0"),
    ]
    ws.row_dimensions[R].height = 20
    for ci, (lbl, key, bg, fg, fmt) in enumerate(cards):
        col = 2 + ci
        c = ws.cell(row=R, column=col, value=lbl)
        c.fill = F(bg)
        c.font = Font(bold=True, color=fg, size=10, name="メイリオ")
        c.alignment = A("center", "center")
        c.border = border()
    R += 1
    ws.row_dimensions[R].height = 30
    for ci, (lbl, key, bg, fg, fmt) in enumerate(cards):
        col = 2 + ci
        c = ws.cell(row=R, column=col)
        c.value = ext(key)
        c.fill = F(bg)
        c.font = Font(bold=True, color=fg, size=14, name="メイリオ")
        c.alignment = A("center", "center")
        c.border = border()
        c.number_format = fmt
    R += 1

    ws.row_dimensions[R].height = 22
    rate_items = [
        ("（月平均）",     "sales_total",  C["navy2"],    "FFFFFF", lambda v: f"=IFERROR({v}/{N},0)"),
        ("（月平均）",     "gross_profit", C["green"],    "FFFFFF", lambda v: f"=IFERROR({v}/{N},0)"),
        ("（月平均）",     "sga_total",    C["dark_gray"],"FFFFFF", lambda v: f"=IFERROR({v}/{N},0)"),
        ("（月平均）",     "op_income",    C["gold"],     C["navy"], lambda v: f"=IFERROR({v}/{N},0)"),
    ]
    for ci, (lbl, key, bg, fg, fn) in enumerate(rate_items):
        col = 2 + ci
        r = pl_key_to_row[key]
        ref = f"'{pl_ws_name}'!{CL(PL_COL_TOTAL)}{r}"
        c = ws.cell(row=R, column=col)
        c.value = fn(ref)
        c.fill = F(bg)
        c.font = Font(bold=False, color=fg, size=11, italic=True, name="メイリオ")
        c.alignment = A("center", "center")
        c.border = border()
        c.number_format = "#,##0"
    R += 1

    ws.row_dimensions[R].height = 6
    R += 1

    # ── 月次推移テーブル ──
    ws.row_dimensions[R].height = 28
    ws.merge_cells(f"B{R}:F{R}")
    mh = ws.cell(row=R, column=2, value="📅  月次推移　（粗利 / 販管費 / 営業利益）")
    mh.fill = F(C["navy2"])
    mh.font = Font(bold=True, color="FFFFFF", size=13, name="メイリオ")
    mh.alignment = A("left", "center")
    mh.border = border()
    R += 1

    # ヘッダー
    ws.row_dimensions[R].height = 22
    headers = ["月", "売上合計", "粗利", "販管費", "営業利益"]
    header_colors = [C["navy"], C["navy2"], C["green"], C["dark_gray"], C["gold"]]
    header_fc = ["FFFFFF", "FFFFFF", "FFFFFF", "FFFFFF", C["navy"]]
    for ci, (h, hc, fc) in enumerate(zip(headers, header_colors, header_fc)):
        c = ws.cell(row=R, column=2 + ci, value=h)
        c.fill = F(hc)
        c.font = Font(bold=True, color=fc, size=10, name="メイリオ")
        c.alignment = A("center", "center")
        c.border = border()
    R += 1

    for m_idx, month in enumerate(MONTHS):
        ws.row_dimensions[R].height = 20
        # 月ラベル
        c = ws.cell(row=R, column=2, value=month)
        c.fill = F(C["section_bg"])
        c.font = Font(bold=False, size=10, name="メイリオ")
        c.alignment = A("center", "center")
        c.border = border()
        # データ
        data_keys = ["sales_total", "gross_profit", "sga_total", "op_income"]
        data_colors = [C["navy2"], C["green"], C["dark_gray"], C["gold"]]
        data_fc = ["FFFFFF", "FFFFFF", "FFFFFF", C["navy"]]
        for ci, (dk, dc, dfc) in enumerate(zip(data_keys, data_colors, data_fc)):
            col = 3 + ci
            c2 = ws.cell(row=R, column=col)
            c2.value = ext_col(dk, m_idx)
            c2.fill = F(dc) if m_idx % 2 == 0 else F(dc)
            c2.font = Font(bold=False, color=dfc, size=10, name="メイリオ")
            c2.alignment = A("right", "center")
            c2.border = border()
            c2.number_format = "#,##0"
        R += 1

    # 合計行
    ws.row_dimensions[R].height = 24
    c = ws.cell(row=R, column=2, value="年間合計")
    c.fill = F(C["navy"])
    c.font = Font(bold=True, color=C["gold"], size=11, name="メイリオ")
    c.alignment = A("center", "center")
    c.border = border()
    data_keys = ["sales_total", "gross_profit", "sga_total", "op_income"]
    for ci, dk in enumerate(data_keys):
        col = 3 + ci
        c2 = ws.cell(row=R, column=col)
        c2.value = ext(dk)
        c2.fill = F(C["gold_bg"])
        c2.font = Font(bold=True, color=C["navy"], size=11, name="メイリオ")
        c2.alignment = A("right", "center")
        c2.border = border()
        c2.number_format = "#,##0"
    R += 1

    ws.row_dimensions[R].height = 6
    R += 1

    # ── 収益性指標 ──
    ws.row_dimensions[R].height = 28
    ws.merge_cells(f"B{R}:F{R}")
    ph = ws.cell(row=R, column=2, value="📈  収益性指標（年間ベース）")
    ph.fill = F(C["green"])
    ph.font = Font(bold=True, color="FFFFFF", size=13, name="メイリオ")
    ph.alignment = A("left", "center")
    ph.border = border()
    R += 1

    perf_items = [
        ("粗利率",       "gross_profit", "sales_total", '0.0"%"'),
        ("営業利益率",   "op_income",    "sales_total", '0.0"%"'),
        ("販管費比率",   "sga_total",    "sales_total", '0.0"%"'),
    ]
    ws.row_dimensions[R].height = 20
    for ci, (lbl, n_key, d_key, fmt) in enumerate(perf_items):
        col = 2 + ci
        lc = ws.cell(row=R, column=col, value=lbl)
        lc.fill = F(C["section_bg"])
        lc.font = Font(bold=True, size=10, color=C["navy"], name="メイリオ")
        lc.alignment = A("center")
        lc.border = border()
    R += 1
    ws.row_dimensions[R].height = 26
    for ci, (lbl, n_key, d_key, fmt) in enumerate(perf_items):
        col = 2 + ci
        n_r = pl_key_to_row[n_key]
        d_r = pl_key_to_row[d_key]
        n_ref = f"'{pl_ws_name}'!{CL(PL_COL_TOTAL)}{n_r}"
        d_ref = f"'{pl_ws_name}'!{CL(PL_COL_TOTAL)}{d_r}"
        c = ws.cell(row=R, column=col)
        c.value = f"=IFERROR({n_ref}/{d_ref}*100,0)"
        c.fill = F(C["profit_bg"])
        c.font = Font(bold=True, size=13, color=C["green"], name="メイリオ")
        c.alignment = A("center")
        c.border = border()
        c.number_format = fmt
    R += 1


# ══════════════════════════════════════════════════════════
# Sheet 5: 月次CF（キャッシュフロー計算書）
# ══════════════════════════════════════════════════════════
# 【財務モデルの前提】
# ・資本金          : 1,000万円（開業時払込）
# ・初期設備投資    : 200万円（什器・内装・POS）→ 60ヶ月定額償却 ≒ 33,333円/月
# ・敷金・保証金    : 60万円（開業時支払）
# ・初期在庫仕入    : 640万円（月次原価合計の1ヶ月分）
# ・売上は全額当月現金回収・仕入は当月現金払い（売掛・買掛ゼロ）
# ・税金・借入なし（簡略モデル）

INIT_CAPITAL     = 10_000_000
INIT_EQUIP       =  2_000_000
SECURITY_DEPOSIT =    600_000
INIT_INVENTORY   =  6_400_000   # 月次原価合計（新品4,900,000 + 中古1,500,000）
MONTHLY_DEPR     =     33_333   # 2,000,000 / 60ヶ月


def build_cf_sheet(ws, pl_ws_name, pl_key_to_row, PL_COL_START):
    """
    月次CF計算書。PLの営業利益を参照して組み立てる。
    Returns: cf_end_cash_row （BS側がここを参照して現金残高を引っ張る）
             CF_COL_START（月列の開始列番号）
    """
    ws.sheet_view.showGridLines = True

    COL_LABEL = 2
    COL_NOTE  = 3         # 補足注記列
    COL_START = 4         # 7月（月次データ開始）
    COL_END   = COL_START + N - 1
    COL_TOTAL = COL_END + 1

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 36
    ws.column_dimensions["C"].width = 20
    for col in range(COL_START, COL_TOTAL + 1):
        ws.column_dimensions[CL(col)].width = 13

    # ── タイトル ──
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 22
    ws.row_dimensions[4].height = 10

    ws.merge_cells(start_row=2, start_column=COL_LABEL, end_row=2, end_column=COL_TOTAL)
    t = ws.cell(row=2, column=COL_LABEL, value="月次キャッシュフロー計算書（間接法）")
    t.fill = F(C["navy"]); t.font = Font(bold=True, color=C["gold"], size=16, name="メイリオ")
    t.alignment = A("left", "center")

    ws.merge_cells(start_row=3, start_column=COL_LABEL, end_row=3, end_column=COL_TOTAL)
    s = ws.cell(row=3, column=COL_LABEL,
                value="期間：2026年7月〜2027年7月（13ヶ月）　｜　単位：円　　"
                      "※ 前提：売上全額当月現金回収・仕入当月現金払い・借入なし")
    s.fill = F(C["navy2"]); s.font = Font(italic=True, color="CCCCCC", size=10, name="メイリオ")
    s.alignment = A("left", "center")

    # ── ヘッダー行 ──
    HDR = 5
    ws.row_dimensions[HDR].height = 28
    set_cell(ws, HDR, COL_LABEL, "項　目", fill_color=C["navy"], bold=True,
             font_color="FFFFFF", font_size=11, h_align="center")
    set_cell(ws, HDR, COL_NOTE, "摘要・前提", fill_color=C["navy"], bold=True,
             font_color="FFFFFF", font_size=10, h_align="center")
    for i, m in enumerate(MONTHS):
        set_cell(ws, HDR, COL_START + i, m, fill_color=C["navy"], bold=True,
                 font_color="FFFFFF", font_size=10, h_align="center")
    set_cell(ws, HDR, COL_TOTAL, "13ヶ月累計", fill_color=C["gold"], bold=True,
             font_color=C["navy"], font_size=11, h_align="center")

    ws.freeze_panes = ws.cell(row=HDR + 1, column=COL_START)

    R = HDR + 1
    key_row = {}   # row name → row number

    def sec(label, color=C["teal"]):
        nonlocal R
        ws.row_dimensions[R].height = 24
        ws.merge_cells(start_row=R, start_column=COL_LABEL, end_row=R, end_column=COL_TOTAL)
        c = ws.cell(row=R, column=COL_LABEL, value=label)
        c.fill = F(color); c.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
        c.alignment = A("left", "center"); c.border = border()
        R += 1

    def cf_row(key, label, note, vals, bg=C["input_bg"], bold=False, italic=False):
        """
        vals: list of 13 values (can be int or str formula)
        """
        nonlocal R
        ws.row_dimensions[R].height = 20
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=10, bold=bold)
        nc = ws.cell(row=R, column=COL_NOTE, value=note)
        nc.fill = F(C["light_gray"]); nc.font = Font(size=9, italic=True,
                                                     color=C["dark_gray"], name="メイリオ")
        nc.alignment = A("left", "center", wrap=True); nc.border = border()
        for i, v in enumerate(vals):
            c = ws.cell(row=R, column=COL_START + i, value=v)
            c.fill = F(bg)
            c.font = Font(bold=bold, size=10, italic=italic, name="メイリオ")
            c.alignment = A("right"); c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["total_bg"] if bold else bg)
        tc.font = Font(bold=True, size=10, name="メイリオ")
        tc.alignment = A("right"); tc.border = border()
        tc.number_format = "#,##0"
        key_row[key] = R
        R += 1

    def cf_formula_row(key, label, note, formula_fn, bg=C["input_bg"],
                       bold=False, italic=False):
        nonlocal R
        ws.row_dimensions[R].height = 20
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=10, bold=bold)
        nc = ws.cell(row=R, column=COL_NOTE, value=note)
        nc.fill = F(C["light_gray"]); nc.font = Font(size=9, italic=True,
                                                     color=C["dark_gray"], name="メイリオ")
        nc.alignment = A("left", "center", wrap=True); nc.border = border()
        for i in range(N):
            col = COL_START + i
            c = ws.cell(row=R, column=col)
            c.value = formula_fn(CL(col), R, i)
            c.fill = F(bg)
            c.font = Font(bold=bold, size=10, italic=italic, name="メイリオ")
            c.alignment = A("right"); c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["total_bg"] if bold else bg)
        tc.font = Font(bold=True, size=10, name="メイリオ")
        tc.alignment = A("right"); tc.border = border()
        tc.number_format = "#,##0"
        key_row[key] = R
        R += 1

    def subtotal_row(key, label, components, bg=C["total_bg"], bold=True):
        nonlocal R
        ws.row_dimensions[R].height = 24
        set_cell(ws, R, COL_LABEL, label, fill_color=bg, h_align="left",
                 font_size=11, bold=bold)
        nc = ws.cell(row=R, column=COL_NOTE)
        nc.fill = F(bg); nc.border = border()
        for i in range(N):
            col = COL_START + i; cl = CL(col)
            parts = "+".join([f"{cl}{key_row[k]}" for k in components])
            c = ws.cell(row=R, column=col)
            c.value = f"={parts}"
            c.fill = F(bg); c.font = Font(bold=True, size=11, name="メイリオ")
            c.alignment = A("right"); c.border = border()
            c.number_format = "#,##0"
        tc = ws.cell(row=R, column=COL_TOTAL)
        tc.value = f"=SUM({CL(COL_START)}{R}:{CL(COL_END)}{R})"
        tc.fill = F(C["gold_bg"]); tc.font = Font(bold=True, size=11, color=C["navy"], name="メイリオ")
        tc.alignment = A("right"); tc.border = border()
        tc.number_format = "#,##0"
        key_row[key] = R
        R += 1

    def spacer(h=6):
        nonlocal R
        ws.row_dimensions[R].height = h; R += 1

    # ━━━━━━ 営業キャッシュフロー ━━━━━━
    sec("Ⅰ　営業キャッシュフロー", C["navy2"])

    # 税引前当期純利益 ← PLの営業利益を参照
    op_row = pl_key_to_row["op_income"]
    cf_formula_row(
        "op_income", "  税引前当期純利益（≒営業利益）",
        "PLシートの営業利益を参照",
        lambda cl, r, i: f"='月次PL'!{CL(PL_COL_START + i)}{op_row}",
        bg=C["section_bg"], bold=False
    )

    # 減価償却費
    cf_row("depr", "  減価償却費（加算）",
           f"設備{INIT_EQUIP:,}÷60ヶ月={MONTHLY_DEPR:,}円/月（非現金費用・加算）",
           [MONTHLY_DEPR] * N,
           bg=C["input_bg"])

    # 棚卸資産の増減
    inv_vals = [-INIT_INVENTORY] + [0] * (N - 1)
    cf_row("inv_change", "  棚卸資産の増減（△は増加）",
           f"初月のみ初期在庫{INIT_INVENTORY:,}円を仕入れ（以降は毎月同額仕入・同額出庫で変動ゼロ）",
           inv_vals, bg=C["input_bg"])

    # 売掛金・買掛金（ゼロ前提）
    cf_row("ar_change", "  売掛金の増減（△は増加）",
           "売上は全額当月現金回収前提 → 変動ゼロ",
           [0] * N, bg=C["light_gray"])
    cf_row("ap_change", "  買掛金の増減（△は減少）",
           "仕入は当月現金払い前提 → 変動ゼロ",
           [0] * N, bg=C["light_gray"])

    subtotal_row("op_cf", "  営業キャッシュフロー　合計",
                 ["op_income", "depr", "inv_change", "ar_change", "ap_change"],
                 bg=C["profit_bg"])
    spacer()

    # ━━━━━━ 投資キャッシュフロー ━━━━━━
    sec("Ⅱ　投資キャッシュフロー", C["teal"])

    equip_vals  = [-INIT_EQUIP]       + [0] * (N - 1)
    dep_vals    = [-SECURITY_DEPOSIT] + [0] * (N - 1)
    cf_row("equip_inv",   "  有形固定資産の取得（什器・内装・POS等）",
           f"開業時一括投資：{INIT_EQUIP:,}円",
           equip_vals, bg=C["input_bg"])
    cf_row("deposit_pay", "  敷金・保証金の支払",
           f"開業時支払：{SECURITY_DEPOSIT:,}円（退去時返還予定）",
           dep_vals, bg=C["input_bg"])
    subtotal_row("inv_cf", "  投資キャッシュフロー　合計",
                 ["equip_inv", "deposit_pay"],
                 bg=C["section_bg"])
    spacer()

    # ━━━━━━ 財務キャッシュフロー ━━━━━━
    sec("Ⅲ　財務キャッシュフロー", C["navy"])

    cap_vals = [INIT_CAPITAL] + [0] * (N - 1)
    cf_row("capital_in", "  資本金の払込",
           f"開業時払込：{INIT_CAPITAL:,}円（自己資金）",
           cap_vals, bg=C["input_bg"])
    subtotal_row("fin_cf", "  財務キャッシュフロー　合計",
                 ["capital_in"],
                 bg=C["section_bg"])
    spacer()

    # ━━━━━━ 期末現金残高 ━━━━━━
    sec("Ⅳ　現金残高", C["navy"])

    # 当月CF増減
    subtotal_row("net_cf", "  当月キャッシュフロー増減（Ⅰ+Ⅱ+Ⅲ）",
                 ["op_cf", "inv_cf", "fin_cf"],
                 bg=C["total_bg"])

    # 期首残高（前月末を参照）
    ws.row_dimensions[R].height = 22
    set_cell(ws, R, COL_LABEL, "  期首現金残高（前月末）",
             fill_color=C["light_gray"], h_align="left", font_size=10)
    nc = ws.cell(row=R, column=COL_NOTE, value="7月のみ0円（開業前）、8月以降は前月末残高")
    nc.fill = F(C["light_gray"]); nc.font = Font(size=9, italic=True, color=C["dark_gray"], name="メイリオ")
    nc.alignment = A("left", "center", wrap=True); nc.border = border()
    for i in range(N):
        col = COL_START + i; cl = CL(col)
        c = ws.cell(row=R, column=col)
        if i == 0:
            c.value = 0  # 7月開始時は0（資本金は財務CFに計上）
        else:
            # 前月の期末残高行を参照（後で確定、プレースホルダー）
            prev_col = CL(COL_START + i - 1)
            c.value = f"={prev_col}{R + 1}"  # 期末残高行のひとつ下を参照予定→後で修正
        c.fill = F(C["light_gray"]); c.font = Font(size=10, name="メイリオ")
        c.alignment = A("right"); c.border = border()
        c.number_format = "#,##0"
    tc = ws.cell(row=R, column=COL_TOTAL)
    tc.fill = F(C["light_gray"]); tc.font = Font(size=10, name="メイリオ")
    tc.alignment = A("right"); tc.border = border()
    tc.number_format = "#,##0"
    key_row["beg_cash"] = R
    beg_cash_row = R
    R += 1

    # 期末現金残高
    ws.row_dimensions[R].height = 28
    set_cell(ws, R, COL_LABEL, "  期末現金残高",
             fill_color=C["gold_bg"], h_align="left", font_size=12, bold=True)
    nc = ws.cell(row=R, column=COL_NOTE, value="当月CF増減 ＋ 期首現金残高")
    nc.fill = F(C["gold_bg"]); nc.font = Font(size=9, italic=True, name="メイリオ")
    nc.alignment = A("left", "center"); nc.border = border()
    end_cash_row = R
    for i in range(N):
        col = COL_START + i; cl = CL(col)
        net_cl = CL(col)
        c = ws.cell(row=R, column=col)
        c.value = f"={net_cl}{key_row['net_cf']}+{net_cl}{beg_cash_row}"
        c.fill = F(C["gold_bg"]); c.font = Font(bold=True, size=12, color=C["navy"], name="メイリオ")
        c.alignment = A("right"); c.border = border()
        c.number_format = "#,##0"
    tc = ws.cell(row=R, column=COL_TOTAL)
    tc.value = f"={CL(COL_START)}{R}"   # 最終月末残高を年度末とする
    tc.fill = F(C["gold"]); tc.font = Font(bold=True, size=12, color=C["navy"], name="メイリオ")
    tc.alignment = A("right"); tc.border = border()
    tc.number_format = "#,##0"
    key_row["end_cash"] = R
    R += 1

    # ── 期首現金参照を期末行で遡及修正 ──
    for i in range(1, N):
        col = COL_START + i
        prev_col = CL(COL_START + i - 1)
        cell = ws.cell(row=beg_cash_row, column=col)
        cell.value = f"={prev_col}{end_cash_row}"

    # 期首現金合計列（13ヶ月の合計は意味がないので最終月末残高）
    tc = ws.cell(row=beg_cash_row, column=COL_TOTAL)
    tc.value = ""

    # ── 注記 ──
    R += 1
    ws.row_dimensions[R].height = 20
    note = ws.cell(row=R, column=COL_LABEL,
                   value="※ 間接法：純利益に非現金項目（減価償却）・運転資本増減を加減して営業CFを算出")
    note.font = Font(size=9, italic=True, color=C["dark_gray"], name="メイリオ")
    note.alignment = A("left", "center")
    ws.merge_cells(start_row=R, start_column=COL_LABEL, end_row=R, end_column=COL_TOTAL)

    return end_cash_row, COL_START


# ══════════════════════════════════════════════════════════
# Sheet 6: 月次BS（貸借対照表）
# ══════════════════════════════════════════════════════════
def build_bs_sheet(ws, pl_ws_name, pl_key_to_row,
                   cf_ws_name, cf_end_cash_row, CF_COL_START,
                   PL_COL_START):
    """
    月次貸借対照表。
    ・現金   ← CFシートの期末現金残高
    ・利益剰余金 ← PLシートの営業利益の累計
    ・その他 ← 仮定値に基づく固定値 or 計算式
    """
    ws.sheet_view.showGridLines = True

    COL_LABEL  = 2
    COL_SOKO   = 3          # 期首（2026/7/1）
    COL_MON1   = 4          # 7月末
    COL_LAST   = COL_MON1 + N - 1   # 27年7月末

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 32
    for col in range(COL_SOKO, COL_LAST + 1):
        ws.column_dimensions[CL(col)].width = 14

    # ── タイトル ──
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 40
    ws.row_dimensions[3].height = 22
    ws.row_dimensions[4].height = 10

    ws.merge_cells(start_row=2, start_column=COL_LABEL, end_row=2, end_column=COL_LAST)
    t = ws.cell(row=2, column=COL_LABEL, value="月次貸借対照表（Balance Sheet）")
    t.fill = F(C["navy"]); t.font = Font(bold=True, color=C["gold"], size=16, name="メイリオ")
    t.alignment = A("left", "center")

    ws.merge_cells(start_row=3, start_column=COL_LABEL, end_row=3, end_column=COL_LAST)
    s = ws.cell(row=3, column=COL_LABEL,
                value="ある時点の「財政状態」を示す　｜　単位：円　"
                      "｜　左右一致（資産合計 ＝ 負債合計 ＋ 純資産合計）を常に確認")
    s.fill = F(C["navy2"]); s.font = Font(italic=True, color="CCCCCC", size=10, name="メイリオ")
    s.alignment = A("left", "center")

    # ── ヘッダー行 ──
    HDR = 5
    ws.row_dimensions[HDR].height = 28
    set_cell(ws, HDR, COL_LABEL, "勘　定　科　目", fill_color=C["navy"], bold=True,
             font_color="FFFFFF", font_size=11, h_align="center")
    set_cell(ws, HDR, COL_SOKO, "期首\n2026/7/1", fill_color=C["dark_gray"], bold=True,
             font_color="FFFFFF", font_size=10, h_align="center")
    month_labels = [m + "末" for m in MONTHS]
    for i, lbl in enumerate(month_labels):
        set_cell(ws, HDR, COL_MON1 + i, lbl, fill_color=C["navy"], bold=True,
                 font_color="FFFFFF", font_size=10, h_align="center")

    ws.freeze_panes = ws.cell(row=HDR + 1, column=COL_MON1)

    R = HDR + 1
    key_row = {}

    def sec(label, color=C["navy2"]):
        nonlocal R
        ws.row_dimensions[R].height = 22
        ws.merge_cells(start_row=R, start_column=COL_LABEL, end_row=R, end_column=COL_LAST)
        c = ws.cell(row=R, column=COL_LABEL, value=label)
        c.fill = F(color); c.font = Font(bold=True, color="FFFFFF", size=11, name="メイリオ")
        c.alignment = A("left", "center"); c.border = border()
        R += 1

    def bs_row(key, label, soko_val, monthly_fn, bg=C["input_bg"],
               bold=False, italic=False):
        """
        soko_val: 期首の値（int or formula str）
        monthly_fn(month_idx) -> value or formula for that month (0=July, ..., 12=Jul27)
        """
        nonlocal R
        ws.row_dimensions[R].height = 22

        lc = ws.cell(row=R, column=COL_LABEL, value=label)
        lc.fill = F(bg); lc.font = Font(bold=bold, size=10, italic=italic, name="メイリオ")
        lc.alignment = A("left", "center"); lc.border = border()

        # 期首列
        sc = ws.cell(row=R, column=COL_SOKO, value=soko_val)
        sc.fill = F(C["mid_gray"]); sc.font = Font(bold=False, size=10, color="333333", name="メイリオ")
        sc.alignment = A("right", "center"); sc.border = border()
        sc.number_format = "#,##0"

        # 月次列
        for i in range(N):
            col = COL_MON1 + i
            c = ws.cell(row=R, column=col, value=monthly_fn(i))
            c.fill = F(bg); c.font = Font(bold=bold, size=10, italic=italic, name="メイリオ")
            c.alignment = A("right", "center"); c.border = border()
            c.number_format = "#,##0"

        key_row[key] = R
        R += 1

    def total_row_bs(key, label, soko_formula_fn, monthly_formula_fn,
                     bg=C["total_bg"], bold=True, font_size=11):
        nonlocal R
        ws.row_dimensions[R].height = 24

        lc = ws.cell(row=R, column=COL_LABEL, value=label)
        lc.fill = F(bg); lc.font = Font(bold=bold, size=font_size, name="メイリオ")
        lc.alignment = A("left", "center"); lc.border = border()

        sc = ws.cell(row=R, column=COL_SOKO, value=soko_formula_fn(CL(COL_SOKO), R))
        sc.fill = F(C["mid_gray"]); sc.font = Font(bold=True, size=font_size, color="333333", name="メイリオ")
        sc.alignment = A("right", "center"); sc.border = border()
        sc.number_format = "#,##0"

        for i in range(N):
            col = COL_MON1 + i; cl = CL(col)
            c = ws.cell(row=R, column=col, value=monthly_formula_fn(cl, R, i))
            c.fill = F(bg); c.font = Font(bold=bold, size=font_size, name="メイリオ")
            c.alignment = A("right", "center"); c.border = border()
            c.number_format = "#,##0"

        key_row[key] = R
        R += 1

    def spacer(h=6):
        nonlocal R
        ws.row_dimensions[R].height = h; R += 1

    op_row = pl_key_to_row["op_income"]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 【資産の部】
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sec("【資産の部】", C["navy"])

    sec("  ▸ 流動資産", C["navy2"])

    # 現金・預金 ← CFシート参照
    def cash_monthly(i):
        cf_col = CL(CF_COL_START + i)
        return f"='{cf_ws_name}'!{cf_col}{cf_end_cash_row}"

    bs_row("cash", "    現金・預金", INIT_CAPITAL, cash_monthly,
           bg=C["section_bg"])

    # 売掛金（ゼロ前提）
    bs_row("ar", "    売掛金", 0, lambda i: 0, bg=C["light_gray"], italic=True)

    # 棚卸資産（月1以降は1ヶ月分固定）
    bs_row("inventory", "    棚卸資産（商品）",
           0,
           lambda i: INIT_INVENTORY,
           bg=C["input_bg"])

    # 流動資産合計
    total_row_bs(
        "cur_assets", "  流動資産　合計",
        lambda cl, r: f"={cl}{key_row['cash']}+{cl}{key_row['ar']}+{cl}{key_row['inventory']}",
        lambda cl, r, i: f"={cl}{key_row['cash']}+{cl}{key_row['ar']}+{cl}{key_row['inventory']}",
    )
    spacer()

    sec("  ▸ 固定資産", C["navy2"])

    # 什器備品（純額）= 取得原価 - 累計償却
    def equip_monthly(i):
        months_elapsed = i + 1  # July=1, Aug=2, ...
        val = max(0, INIT_EQUIP - MONTHLY_DEPR * months_elapsed)
        return val

    bs_row("equip", "    什器備品（純額）",
           0,
           equip_monthly,
           bg=C["input_bg"])

    # 敷金・保証金（固定）
    bs_row("deposit", "    敷金・保証金",
           0,
           lambda i: SECURITY_DEPOSIT,
           bg=C["input_bg"])

    # 固定資産合計
    total_row_bs(
        "fix_assets", "  固定資産　合計",
        lambda cl, r: f"={cl}{key_row['equip']}+{cl}{key_row['deposit']}",
        lambda cl, r, i: f"={cl}{key_row['equip']}+{cl}{key_row['deposit']}",
        bg=C["total_bg"]
    )
    spacer()

    # 資産合計
    total_row_bs(
        "total_assets", "資産　合計",
        lambda cl, r: f"={cl}{key_row['cur_assets']}+{cl}{key_row['fix_assets']}",
        lambda cl, r, i: f"={cl}{key_row['cur_assets']}+{cl}{key_row['fix_assets']}",
        bg=C["navy"], bold=True, font_size=12
    )
    # 資産合計行の文字色を白に
    for col in range(COL_SOKO, COL_LAST + 1):
        c = ws.cell(row=key_row["total_assets"], column=col)
        c.font = Font(bold=True, size=12, color="FFFFFF", name="メイリオ")
    ws.cell(row=key_row["total_assets"], column=COL_LABEL).font = \
        Font(bold=True, size=12, color="FFFFFF", name="メイリオ")

    spacer(10)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 【負債の部】
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sec("【負債の部】", C["red"])

    sec("  ▸ 流動負債", C["dark_gray"])
    bs_row("ap",       "    買掛金",         0, lambda i: 0, bg=C["light_gray"], italic=True)
    bs_row("accrued",  "    未払費用",        0, lambda i: 0, bg=C["light_gray"], italic=True)
    total_row_bs(
        "cur_liab", "  流動負債　合計",
        lambda cl, r: f"={cl}{key_row['ap']}+{cl}{key_row['accrued']}",
        lambda cl, r, i: f"={cl}{key_row['ap']}+{cl}{key_row['accrued']}",
    )
    spacer()

    sec("  ▸ 固定負債", C["dark_gray"])
    bs_row("lt_debt",  "    長期借入金",      0, lambda i: 0, bg=C["light_gray"], italic=True)
    total_row_bs(
        "fix_liab", "  固定負債　合計",
        lambda cl, r: f"={cl}{key_row['lt_debt']}",
        lambda cl, r, i: f"={cl}{key_row['lt_debt']}",
    )
    spacer()

    total_row_bs(
        "total_liab", "負債　合計",
        lambda cl, r: f"={cl}{key_row['cur_liab']}+{cl}{key_row['fix_liab']}",
        lambda cl, r, i: f"={cl}{key_row['cur_liab']}+{cl}{key_row['fix_liab']}",
        bg=C["red"], bold=True, font_size=12
    )
    for col in range(COL_SOKO, COL_LAST + 1):
        c = ws.cell(row=key_row["total_liab"], column=col)
        c.font = Font(bold=True, size=12, color="FFFFFF", name="メイリオ")
    ws.cell(row=key_row["total_liab"], column=COL_LABEL).font = \
        Font(bold=True, size=12, color="FFFFFF", name="メイリオ")

    spacer(10)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 【純資産の部】
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sec("【純資産の部】", C["green"])

    bs_row("capital", "    資本金",
           INIT_CAPITAL,
           lambda i: INIT_CAPITAL,
           bg=C["input_bg"], bold=True)

    # 利益剰余金 ← PLの営業利益の累計
    def retained_monthly(i):
        start_col = CL(PL_COL_START)
        end_col   = CL(PL_COL_START + i)
        return f"=SUM('{pl_ws_name}'!{start_col}{op_row}:{end_col}{op_row})"

    bs_row("retained", "    利益剰余金（累計営業利益）",
           0,
           retained_monthly,
           bg=C["profit_bg"])

    total_row_bs(
        "net_assets", "純資産　合計",
        lambda cl, r: f"={cl}{key_row['capital']}+{cl}{key_row['retained']}",
        lambda cl, r, i: f"={cl}{key_row['capital']}+{cl}{key_row['retained']}",
        bg=C["green"], bold=True, font_size=12
    )
    for col in range(COL_SOKO, COL_LAST + 1):
        c = ws.cell(row=key_row["net_assets"], column=col)
        c.font = Font(bold=True, size=12, color="FFFFFF", name="メイリオ")
    ws.cell(row=key_row["net_assets"], column=COL_LABEL).font = \
        Font(bold=True, size=12, color="FFFFFF", name="メイリオ")

    spacer(10)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 負債・純資産合計 ＆ 貸借チェック
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    total_row_bs(
        "total_lna", "負債・純資産　合計",
        lambda cl, r: f"={cl}{key_row['total_liab']}+{cl}{key_row['net_assets']}",
        lambda cl, r, i: f"={cl}{key_row['total_liab']}+{cl}{key_row['net_assets']}",
        bg=C["navy"], bold=True, font_size=12
    )
    for col in range(COL_SOKO, COL_LAST + 1):
        c = ws.cell(row=key_row["total_lna"], column=col)
        c.font = Font(bold=True, size=12, color="FFFFFF", name="メイリオ")
    ws.cell(row=key_row["total_lna"], column=COL_LABEL).font = \
        Font(bold=True, size=12, color="FFFFFF", name="メイリオ")

    spacer()

    # 貸借一致チェック行
    ws.row_dimensions[R].height = 20
    lc = ws.cell(row=R, column=COL_LABEL,
                 value="★ 貸借一致チェック（0 = 正常　/ 0以外 = 誤差あり）")
    lc.fill = F(C["gold_bg"]); lc.font = Font(bold=True, size=10, color=C["navy"], name="メイリオ")
    lc.alignment = A("left", "center"); lc.border = border()

    check_soko = ws.cell(row=R, column=COL_SOKO)
    cl_s = CL(COL_SOKO)
    check_soko.value = f"={cl_s}{key_row['total_assets']}-{cl_s}{key_row['total_lna']}"
    check_soko.fill = F(C["gold_bg"]); check_soko.font = Font(bold=True, size=10, name="メイリオ")
    check_soko.alignment = A("right"); check_soko.border = border()
    check_soko.number_format = "#,##0"

    for i in range(N):
        col = COL_MON1 + i; cl_c = CL(col)
        c = ws.cell(row=R, column=col)
        c.value = f"={cl_c}{key_row['total_assets']}-{cl_c}{key_row['total_lna']}"
        c.fill = F(C["gold_bg"]); c.font = Font(bold=True, size=10, name="メイリオ")
        c.alignment = A("right"); c.border = border()
        c.number_format = "#,##0"
    R += 1

    # ── 注記 ──
    spacer()
    note = ws.cell(row=R, column=COL_LABEL,
                   value=f"【BS前提メモ】　資本金{INIT_CAPITAL:,}円（自己資金）　"
                         f"/ 設備{INIT_EQUIP:,}円（60ヶ月定額償却）　"
                         f"/ 敷金{SECURITY_DEPOSIT:,}円　"
                         f"/ 初期在庫{INIT_INVENTORY:,}円（以降安定在庫）　"
                         f"/ 売掛・買掛・借入ゼロ（簡略モデル）")
    note.font = Font(size=9, italic=True, color=C["dark_gray"], name="メイリオ")
    note.alignment = A("left", "center", wrap=True)
    ws.merge_cells(start_row=R, start_column=COL_LABEL, end_row=R, end_column=COL_LAST)
    ws.row_dimensions[R].height = 28


# ══════════════════════════════════════════════════════════
# メイン
# ══════════════════════════════════════════════════════════
def main():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # シート作成順序
    ws_vision = wb.create_sheet("ビジョン・戦略")
    ws_pl     = wb.create_sheet("月次PL")
    ws_sga    = wb.create_sheet("販管費内訳")
    ws_cf     = wb.create_sheet("月次CF")
    ws_bs     = wb.create_sheet("月次BS")
    ws_dash   = wb.create_sheet("ダッシュボード")

    # ビジョンシート
    build_vision_sheet(ws_vision)

    # PLシート
    (pl_key_to_row, PL_COL_START, PL_COL_END,
     PL_COL_TOTAL, sga_pl_rows) = build_pl_sheet(ws_pl)

    # 販管費内訳シート
    (sga_cat_rows, SGA_COL_START, SGA_COL_END,
     SGA_COL_TOTAL) = build_sga_sheet(
        ws_sga, "月次PL", sga_pl_rows,
        PL_COL_START, PL_COL_END, PL_COL_TOTAL
    )

    # CFシート
    cf_end_cash_row, CF_COL_START = build_cf_sheet(
        ws_cf, "月次PL", pl_key_to_row, PL_COL_START
    )

    # BSシート
    build_bs_sheet(
        ws_bs, "月次PL", pl_key_to_row,
        "月次CF", cf_end_cash_row, CF_COL_START,
        PL_COL_START
    )

    # ダッシュボード
    build_dashboard_sheet(
        ws_dash, "月次PL", pl_key_to_row,
        PL_COL_START, PL_COL_END, PL_COL_TOTAL
    )

    # ── PLシートの販管費行を内訳シート参照数式に差し替え ──
    key_map = {
        "rent":        "rent_total",
        "salary_full": "salary_full_total",
        "salary_part": "salary_part_total",
        "ad":          "ad_total",
        "ec_fee":      "ec_fee_total",
        "shipping":    "shipping_total",
        "utilities":   "utilities_total",
    }
    for pl_key, sga_cat_key in key_map.items():
        sga_row = sga_cat_rows.get(sga_cat_key)
        if sga_row is None:
            continue
        pl_row = sga_pl_rows[pl_key]
        for m_idx in range(N):
            col = PL_COL_START + m_idx
            sga_col = SGA_COL_START + m_idx
            cell = ws_pl.cell(row=pl_row, column=col)
            cell.value = f"='販管費内訳'!{CL(sga_col)}{sga_row}"
            cell.number_format = "#,##0"
        tc = ws_pl.cell(row=pl_row, column=PL_COL_TOTAL)
        tc.value = f"=SUM({CL(PL_COL_START)}{pl_row}:{CL(PL_COL_END)}{pl_row})"

    fname = "trading_card_shop_PL_v3.xlsx"
    wb.save(fname)
    print(f"✅ 保存完了: {fname}")
    print()
    print("📋 シート構成:")
    print("  1. ビジョン・戦略  ← 事業コンセプト・KPI・ロードマップ・3原則")
    print("  2. 月次PL          ← 13ヶ月の損益計算書（数式連動）")
    print("  3. 販管費内訳      ← 費目ごとの詳細内訳（PLに自動反映）")
    print("  4. 月次CF          ← キャッシュフロー計算書（間接法、期末現金残高追跡）")
    print("  5. 月次BS          ← 貸借対照表（月末スナップショット、貸借一致チェック付）")
    print("  6. ダッシュボード  ← 月次推移テーブル・収益性指標")
    print()
    total_sales = TARGET["new_sales"] + TARGET["used_sales"]
    gross = (TARGET["new_sales"] * (1 - TARGET["new_cost_rate"]) +
             TARGET["used_sales"] * (1 - TARGET["used_cost_rate"]))
    sga_total = sum(SGA_DETAIL.values())
    op = gross - sga_total
    monthly_depr = MONTHLY_DEPR
    op_cf_m1 = op + monthly_depr - INIT_INVENTORY
    inv_cf_m1 = -(INIT_EQUIP + SECURITY_DEPOSIT)
    fin_cf_m1 = INIT_CAPITAL
    cash_end_m1 = op_cf_m1 + inv_cf_m1 + fin_cf_m1
    op_cf_steady = op + monthly_depr
    print("📌 月次目標数値:")
    print(f"  売上:       {total_sales:>12,} 円  |  粗利: {gross:,.0f} 円 ({gross/total_sales*100:.1f}%)")
    print(f"  販管費:     {sga_total:>12,} 円  |  営業利益: {op:,.0f} 円 ({op/total_sales*100:.1f}%)")
    print()
    print("📌 CFサマリー（初月/定常月）:")
    print(f"  営業CF:  初月 {op_cf_m1:>12,} 円  /  定常 {op_cf_steady:,} 円/月")
    print(f"  投資CF:  初月 {inv_cf_m1:>12,} 円")
    print(f"  財務CF:  初月 {fin_cf_m1:>12,} 円")
    print(f"  7月末現金残高: {cash_end_m1:,} 円")
    print(f"  13ヶ月後現金残高（概算）: {cash_end_m1 + op_cf_steady * 12:,} 円")


if __name__ == "__main__":
    main()

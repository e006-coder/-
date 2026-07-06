#!/usr/bin/env python3
"""カレントディレクトリのCSVファイルの文字コードを自動判定し、
1つのExcelスプレッドシート(各CSVを別シートに)にまとめて出力する。

使い方:
    python3 csv_to_spreadsheet.py [出力ファイル名]
"""
import glob
import sys

import pandas as pd

ENCODINGS = ("utf-8-sig", "cp932")  # cp932 = Windows版Shift-JIS


def read_csv_any_encoding(path):
    last_err = None
    for enc in ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc), enc
        except Exception as e:
            last_err = e
    raise last_err


def unique_sheet_name(name, used):
    base = name[:31]
    candidate = base
    n = 1
    while candidate in used:
        suffix = f"_{n}"
        candidate = base[: 31 - len(suffix)] + suffix
        n += 1
    used.add(candidate)
    return candidate


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "output.xlsx"
    files = sorted(glob.glob("*.csv"))
    if not files:
        print("CSVファイルが見つかりません")
        return

    used_names = set()
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for f in files:
            try:
                df, enc = read_csv_any_encoding(f)
            except Exception as e:
                print(f"読み込み失敗: {f} ({e})")
                continue
            sheet_name = unique_sheet_name(f.rsplit(".", 1)[0], used_names)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"{f}: encoding={enc}, rows={len(df)} -> シート「{sheet_name}」")

    print(f"\n作成しました: {out_path}")


if __name__ == "__main__":
    main()

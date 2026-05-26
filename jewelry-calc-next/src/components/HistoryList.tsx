'use client';

import type { HistoryEntry } from '@/lib/types';
import { parseNum } from '@/lib/calc';

interface Props {
  history: HistoryEntry[];
  onClear: () => void;
  onExportCsv: () => void;
}

const fmt = (n: number, d = 0) =>
  n.toLocaleString('ja-JP', { minimumFractionDigits: d, maximumFractionDigits: d });

export function HistoryList({ history, onClear, onExportCsv }: Props) {
  if (history.length === 0) {
    return (
      <div className="card text-center text-gray-400 text-sm py-8">
        履歴がありません
      </div>
    );
  }

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between border-b border-gold-100 pb-3">
        <h2 className="text-base font-semibold text-gold-700">
          履歴一覧
          <span className="ml-2 text-xs font-normal text-gray-400">({history.length}件)</span>
        </h2>
        <div className="flex gap-2">
          <button type="button" onClick={onExportCsv} className="btn-secondary text-xs px-3 py-1.5">
            CSV出力
          </button>
          <button type="button" onClick={onClear} className="btn-danger text-xs px-3 py-1.5">
            クリア
          </button>
        </div>
      </div>

      <div className="overflow-x-auto -mx-2 px-2">
        <table className="w-full text-xs min-w-[640px]">
          <thead>
            <tr className="text-gray-400 border-b border-gray-100">
              <th className="text-left pb-2 font-medium pr-2">#</th>
              <th className="text-left pb-2 font-medium pr-2">日時</th>
              <th className="text-left pb-2 font-medium pr-2">品位</th>
              <th className="text-left pb-2 font-medium pr-2">区分/No.</th>
              <th className="text-right pb-2 font-medium pr-2">製品代</th>
              <th className="text-right pb-2 font-medium pr-2">製品重量</th>
              <th className="text-right pb-2 font-medium pr-2">中石重量</th>
              <th className="text-right pb-2 font-medium pr-2 text-gold-600">中石代</th>
              <th className="text-right pb-2 font-medium text-gold-600">中石＠</th>
            </tr>
          </thead>
          <tbody>
            {[...history].reverse().map((entry, i) => {
              const { form, result } = entry;
              const idx = history.length - i;
              return (
                <tr key={entry.id} className="border-b border-gray-50 hover:bg-gold-50 transition">
                  <td className="py-2 pr-2 text-gray-300">{idx}</td>
                  <td className="py-2 pr-2 text-gray-500 whitespace-nowrap">{entry.timestamp}</td>
                  <td className="py-2 pr-2 font-medium text-gray-700">{form.metalGrade}</td>
                  <td className="py-2 pr-2 text-gray-600">
                    {[form.productCategory, form.productNo].filter(Boolean).join(' / ') || '—'}
                  </td>
                  <td className="py-2 pr-2 text-right tabular-nums text-gray-700">
                    ¥{fmt(parseNum(form.productPrice))}
                  </td>
                  <td className="py-2 pr-2 text-right tabular-nums text-gray-700">
                    {form.productWeight}g
                  </td>
                  <td className="py-2 pr-2 text-right tabular-nums text-gray-700">
                    {form.centerStoneWeight ? `${form.centerStoneWeight}ct` : '—'}
                  </td>
                  <td className={`py-2 pr-2 text-right tabular-nums font-semibold ${result.isNegative ? 'text-red-500' : 'text-gold-700'}`}>
                    ¥{fmt(result.centerStoneCost)}
                  </td>
                  <td className={`py-2 text-right tabular-nums font-semibold ${result.isNegative ? 'text-red-500' : 'text-gold-600'}`}>
                    {result.centerStonePricePerCt !== null
                      ? `¥${fmt(result.centerStonePricePerCt)}`
                      : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

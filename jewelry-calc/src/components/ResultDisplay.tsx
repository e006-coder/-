import type { CalculationResult } from '../types';

interface Props {
  result: CalculationResult | null;
  canCalculate: boolean;
  onAddToHistory: () => void;
}

function Row({ label, value, highlight, warn }: { label: string; value: string; highlight?: boolean; warn?: boolean }) {
  return (
    <div className={`flex justify-between items-center py-2 border-b border-gray-50 last:border-0 ${highlight ? 'mt-2 pt-3 border-t border-gold-100' : ''}`}>
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`text-sm font-semibold tabular-nums ${warn ? 'text-red-500' : highlight ? 'text-gold-700 text-base' : 'text-gray-800'}`}>
        {value}
      </span>
    </div>
  );
}

export function ResultDisplay({ result, canCalculate, onAddToHistory }: Props) {
  if (!canCalculate) {
    return (
      <div className="card flex items-center justify-center min-h-[160px] text-gray-400 text-sm">
        品位・製品代・製品重量を入力してください
      </div>
    );
  }

  if (!result) return null;

  const fmt = (n: number, decimals = 0) =>
    n.toLocaleString('ja-JP', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

  return (
    <div className="card space-y-1">
      <h2 className="text-base font-semibold text-gold-700 border-b border-gold-100 pb-3 mb-3">
        計算結果
      </h2>

      {result.stoneWeightExceedsProduct && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-xs text-amber-700 mb-3">
          ⚠ 石重量の合計が製品重量を超えています。入力値をご確認ください。
        </div>
      )}

      <Row label="地金重量" value={`${fmt(result.metalWeight, 3)} g`} />
      <Row label="地金代" value={`¥${fmt(result.metalCost)}`} />
      {result.sideStoneCost > 0 && (
        <Row label="脇石代" value={`¥${fmt(result.sideStoneCost)}`} />
      )}
      {result.mdCost > 0 && (
        <Row label="MD代" value={`¥${fmt(result.mdCost)}`} />
      )}
      <Row label="税抜製品代" value={`¥${fmt(result.taxExcludedPrice)}`} />

      <div className={`mt-3 rounded-xl px-4 py-4 ${result.isNegative ? 'bg-red-50 border border-red-100' : 'bg-gold-50 border border-gold-100'}`}>
        {result.isNegative && (
          <p className="text-xs text-red-500 mb-2 font-medium">⚠ 入力値を確認してください（中石代がマイナスです）</p>
        )}
        <div className="flex justify-between items-end">
          <div>
            <p className="text-xs text-gray-500 mb-0.5">中石代</p>
            <p className={`text-2xl font-bold tabular-nums ${result.isNegative ? 'text-red-500' : 'text-gold-700'}`}>
              ¥{fmt(result.centerStoneCost)}
            </p>
          </div>
          {result.centerStonePricePerCt !== null && (
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-0.5">中石＠（ct単価）</p>
              <p className={`text-lg font-bold tabular-nums ${result.isNegative ? 'text-red-500' : 'text-gold-600'}`}>
                ¥{fmt(result.centerStonePricePerCt)} /ct
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="pt-3">
        <button
          type="button"
          onClick={onAddToHistory}
          className="btn-primary w-full"
        >
          履歴に追加して次へ
        </button>
      </div>
    </div>
  );
}

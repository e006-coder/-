import { useState } from 'react';
import { METAL_PRICES, METAL_GRADE_OPTIONS } from '../constants';
import type { MarketRate } from '../types';

interface Props {
  marketRates: MarketRate[];
  activeDate: string;
  onSave: (rate: MarketRate) => void;
  onSelectDate: (date: string) => void;
  onDelete: (date: string) => void;
}

const fmt = (n: number) => n.toLocaleString('ja-JP', { maximumFractionDigits: 0 });

export function MarketRatePanel({ marketRates, activeDate, onSave, onSelectDate, onDelete }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(today);
  const [rate, setRate] = useState('');
  const [overrides, setOverrides] = useState<Record<string, string>>({});

  const rateNum = parseFloat(rate) || 1;

  const computedPrice = (grade: string): number => {
    const override = overrides[grade];
    if (override !== undefined && override !== '') return parseFloat(override) || 0;
    return Math.round(METAL_PRICES[grade] * rateNum);
  };

  const handleSave = () => {
    if (!date) return;
    const prices: Record<string, number> = {};
    for (const g of METAL_GRADE_OPTIONS) {
      prices[g] = computedPrice(g);
    }
    onSave({ date, rate: rateNum, prices });
    setOverrides({});
    setRate('');
  };

  const selectedRate = marketRates.find((r) => r.date === activeDate);

  return (
    <div className="space-y-5">
      {/* 入力フォーム */}
      <div className="card space-y-4">
        <h2 className="text-base font-semibold text-gold-700 border-b border-gold-100 pb-3">
          相場設定
        </h2>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">日付</label>
            <input
              type="date"
              className="input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div>
            <label className="label">掛け率</label>
            <input
              type="number"
              className="input text-right"
              min="0"
              step="0.001"
              placeholder="例: 0.950"
              value={rate}
              onChange={(e) => setRate(e.target.value)}
            />
          </div>
        </div>

        {rate && (
          <div className="rounded-xl border border-gold-100 overflow-hidden">
            <div className="bg-gold-50 px-3 py-2 text-xs font-semibold text-gold-700">
              実勢単価プレビュー（掛け率: {rateNum}）
            </div>
            <div className="divide-y divide-gray-50 max-h-64 overflow-y-auto">
              {METAL_GRADE_OPTIONS.map((g) => (
                <div key={g} className="flex items-center gap-2 px-3 py-1.5">
                  <span className="w-32 text-xs text-gray-600 font-medium shrink-0">{g}</span>
                  <span className="text-xs text-gray-400 w-24 text-right shrink-0">
                    基準: {fmt(METAL_PRICES[g])}
                  </span>
                  <span className="text-xs text-gray-400 shrink-0">→</span>
                  <input
                    type="number"
                    className="input text-right py-1 text-xs"
                    placeholder={String(Math.round(METAL_PRICES[g] * rateNum))}
                    value={overrides[g] ?? ''}
                    onChange={(e) =>
                      setOverrides((prev) => ({ ...prev, [g]: e.target.value }))
                    }
                  />
                  <span className="text-xs text-gray-400 shrink-0">円/g</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <button type="button" className="btn-primary w-full" onClick={handleSave}>
          相場を保存
        </button>
      </div>

      {/* 相場履歴 */}
      {marketRates.length > 0 && (
        <div className="card space-y-3">
          <h2 className="text-base font-semibold text-gold-700 border-b border-gold-100 pb-3">
            相場履歴
          </h2>
          <div className="space-y-2">
            {[...marketRates].reverse().map((mr) => {
              const isActive = mr.date === activeDate;
              return (
                <div
                  key={mr.date}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2.5 transition cursor-pointer ${
                    isActive
                      ? 'border-gold-400 bg-gold-50'
                      : 'border-gray-100 hover:border-gold-200 hover:bg-gold-50'
                  }`}
                  onClick={() => onSelectDate(isActive ? '' : mr.date)}
                >
                  <div>
                    <p className="text-sm font-medium text-gray-800">{mr.date}</p>
                    <p className="text-xs text-gray-400">掛け率: {mr.rate}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {isActive && (
                      <span className="text-xs bg-gold-500 text-white px-2 py-0.5 rounded-full">
                        適用中
                      </span>
                    )}
                    <button
                      type="button"
                      className="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(mr.date);
                      }}
                    >
                      削除
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {selectedRate && (
            <div className="rounded-xl border border-gold-100 overflow-hidden mt-2">
              <div className="bg-gold-50 px-3 py-2 text-xs font-semibold text-gold-700">
                {selectedRate.date} の実勢単価
              </div>
              <div className="divide-y divide-gray-50 max-h-48 overflow-y-auto">
                {METAL_GRADE_OPTIONS.map((g) => (
                  <div key={g} className="flex justify-between px-3 py-1.5">
                    <span className="text-xs text-gray-600">{g}</span>
                    <span className="text-xs font-medium text-gray-800">
                      {fmt(selectedRate.prices[g] ?? METAL_PRICES[g])} 円/g
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

'use client';

import { useState } from 'react';
import { METAL_MASTER, METAL_BASE_PRICE } from '@/lib/constants';
import type { MarketRate, MetalGroup } from '@/lib/types';

interface Props {
  marketRates: MarketRate[];
  onSave: (rate: MarketRate) => void;
  onDelete: (date: string) => void;
}

const fmt = (n: number) => n.toLocaleString('ja-JP', { maximumFractionDigits: 0 });

const GROUP_LABELS: Record<MetalGroup, string> = {
  Au: 'Au IG',
  Pt: 'Pt IG',
  SV: 'SV IG',
};

const GROUP_COLORS: Record<MetalGroup, string> = {
  Au: 'bg-yellow-50 text-yellow-700',
  Pt: 'bg-blue-50 text-blue-700',
  SV: 'bg-gray-100 text-gray-600',
};

export function MarketRatePanel({ marketRates, onSave, onDelete }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(today);
  const [rates, setRates] = useState<Record<MetalGroup, string>>({ Au: '', Pt: '', SV: '' });
  const [overrides, setOverrides] = useState<Record<string, string>>({});
  const [manualFlags, setManualFlags] = useState<Record<string, boolean>>({});
  const [expandedDate, setExpandedDate] = useState<string | null>(null);

  const getRateNum = (g: MetalGroup) => parseFloat(rates[g]) || 1;
  const hasRates = rates.Au !== '' || rates.Pt !== '' || rates.SV !== '';

  const computedPrice = (label: string, group: MetalGroup): number => {
    if (manualFlags[label] && overrides[label] !== undefined && overrides[label] !== '') {
      return parseFloat(overrides[label]) || 0;
    }
    return Math.round(METAL_BASE_PRICE[label] * getRateNum(group));
  };

  const handleOverride = (label: string, value: string) => {
    setOverrides((prev) => ({ ...prev, [label]: value }));
    setManualFlags((prev) => ({ ...prev, [label]: value !== '' }));
  };

  const handleResetOverride = (label: string) => {
    setOverrides((prev) => ({ ...prev, [label]: '' }));
    setManualFlags((prev) => ({ ...prev, [label]: false }));
  };

  const handleSave = () => {
    if (!date) return;
    const prices: Record<string, number> = {};
    const manualOverrides: Record<string, boolean> = {};
    for (const m of METAL_MASTER) {
      prices[m.label] = computedPrice(m.label, m.group);
      manualOverrides[m.label] = manualFlags[m.label] ?? false;
    }
    onSave({
      date,
      rates: { Au: getRateNum('Au'), Pt: getRateNum('Pt'), SV: getRateNum('SV') },
      prices,
      manualOverrides,
    });
    setOverrides({});
    setManualFlags({});
    setRates({ Au: '', Pt: '', SV: '' });
  };

  return (
    <div className="space-y-5">
      {/* 相場設定フォーム */}
      <div className="card space-y-4">
        <h2 className="text-base font-semibold text-gold-700 border-b border-gold-100 pb-3">
          相場設定
        </h2>

        {/* 日付 */}
        <div>
          <label className="label">日付</label>
          <input
            type="date"
            className="input"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>

        {/* 3系統の掛け率 */}
        <div className="grid grid-cols-3 gap-2">
          {(['Au', 'Pt', 'SV'] as MetalGroup[]).map((g) => (
            <div key={g}>
              <label className="label">{GROUP_LABELS[g]} 掛け率</label>
              <input
                type="number"
                className="input text-right"
                min="0"
                step="0.001"
                placeholder="例: 0.96"
                value={rates[g]}
                onChange={(e) => setRates((prev) => ({ ...prev, [g]: e.target.value }))}
              />
            </div>
          ))}
        </div>

        {/* 実勢単価プレビュー */}
        {hasRates && (
          <div className="rounded-xl border border-gold-100 overflow-hidden">
            <div className="bg-gold-50 px-3 py-2 text-xs font-semibold text-gold-700">
              実勢単価プレビュー
            </div>
            <div className="divide-y divide-gray-50 max-h-72 overflow-y-auto">
              {METAL_MASTER.map((m) => {
                const auto = Math.round(METAL_BASE_PRICE[m.label] * getRateNum(m.group));
                const isManual = manualFlags[m.label] ?? false;
                return (
                  <div key={m.label} className="flex items-center gap-2 px-3 py-1.5 flex-wrap">
                    <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${GROUP_COLORS[m.group]}`}>
                      {m.group}
                    </span>
                    <span className="w-28 text-xs text-gray-700 font-medium shrink-0">{m.label}</span>
                    <span className="text-xs text-gray-400 shrink-0">
                      {fmt(METAL_BASE_PRICE[m.label])}→
                    </span>
                    <input
                      type="number"
                      className="input text-right py-1 text-xs w-24 shrink-0"
                      placeholder={String(auto)}
                      value={isManual ? (overrides[m.label] ?? '') : ''}
                      onChange={(e) => handleOverride(m.label, e.target.value)}
                    />
                    <span className="text-xs text-gray-400 shrink-0">円/g</span>
                    {isManual ? (
                      <div className="flex items-center gap-1 shrink-0">
                        <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-medium">
                          手動設定済
                        </span>
                        <button
                          type="button"
                          className="text-xs text-gray-400 hover:text-gray-600 underline"
                          onClick={() => handleResetOverride(m.label)}
                        >
                          自動に戻す
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs font-medium text-gray-700 shrink-0">
                        {fmt(auto)}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <button
          type="button"
          className="btn-primary w-full"
          onClick={handleSave}
          disabled={!date}
        >
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
            {[...marketRates].reverse().map((mr) => (
              <div key={mr.date} className="rounded-lg border border-gray-100 overflow-hidden">
                <div
                  className="flex items-center justify-between px-3 py-2.5 cursor-pointer hover:bg-gold-50 transition"
                  onClick={() =>
                    setExpandedDate(expandedDate === mr.date ? null : mr.date)
                  }
                >
                  <div>
                    <p className="text-sm font-medium text-gray-800">{mr.date}</p>
                    <p className="text-xs text-gray-400">
                      Au×{mr.rates.Au} / Pt×{mr.rates.Pt} / SV×{mr.rates.SV}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">
                      {expandedDate === mr.date ? '▲' : '▼'}
                    </span>
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

                {expandedDate === mr.date && (
                  <div className="border-t border-gray-50 divide-y divide-gray-50 max-h-48 overflow-y-auto">
                    {METAL_MASTER.map((m) => (
                      <div key={m.label} className="flex justify-between items-center px-3 py-1.5">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-1 py-0.5 rounded ${GROUP_COLORS[m.group]}`}>
                            {m.group}
                          </span>
                          <span className="text-xs text-gray-600">{m.label}</span>
                          {mr.manualOverrides[m.label] && (
                            <span className="text-xs bg-amber-100 text-amber-700 px-1 rounded">
                              手動
                            </span>
                          )}
                        </div>
                        <span className="text-xs font-medium text-gray-800">
                          {fmt(mr.prices[m.label] ?? METAL_BASE_PRICE[m.label])} 円/g
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

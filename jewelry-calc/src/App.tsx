import { useState, useEffect, useMemo } from 'react';
import { METAL_PRICES } from './constants';
import { calculate, parseNum } from './calc';
import type { FormData, HistoryEntry, MarketRate, CalculationResult } from './types';
import { CalculatorForm } from './components/CalculatorForm';
import { ResultDisplay } from './components/ResultDisplay';
import { HistoryList } from './components/HistoryList';
import { MarketRatePanel } from './components/MarketRatePanel';

const STORAGE_HISTORY = 'jewelry-calc-history';
const STORAGE_MARKET = 'jewelry-calc-market';
const STORAGE_ACTIVE_DATE = 'jewelry-calc-active-date';

const EMPTY_FORM: FormData = {
  metalGrade: 'K18',
  productCategory: '',
  productNo: '',
  productPrice: '',
  productWeight: '',
  centerStoneWeight: '',
  sideStoneWeight: '',
  sideStonePricePerCt: '',
  mdWeight: '',
  mdPricePerCt: '',
  taxMode: 'none',
};

type Tab = 'calc' | 'market';

function loadStorage<T>(key: string, fallback: T): T {
  try {
    const s = localStorage.getItem(key);
    return s ? (JSON.parse(s) as T) : fallback;
  } catch {
    return fallback;
  }
}

function exportCsv(history: HistoryEntry[]) {
  const headers = [
    '番号', '日時', '品位', '製品区分', 'No.', 'TAX',
    '製品代(円)', '製品重量(g)', '中石重量(ct)', '脇石重量(ct)', '脇石単価(円/ct)',
    'MD重量(ct)', 'MD単価(円/ct)', '地金重量(g)', '地金単価(円/g)',
    '地金代(円)', '中石代(円)', '中石＠(円/ct)',
  ];
  const rows = history.map((e, i) => {
    const f = e.form;
    const r = e.result;
    return [
      i + 1, e.timestamp, f.metalGrade, f.productCategory, f.productNo,
      f.taxMode === 'none' ? 'なし' : `${f.taxMode}%`,
      parseNum(f.productPrice), parseNum(f.productWeight),
      parseNum(f.centerStoneWeight), parseNum(f.sideStoneWeight), parseNum(f.sideStonePricePerCt),
      parseNum(f.mdWeight), parseNum(f.mdPricePerCt),
      r.metalWeight.toFixed(3), r.metalPricePerG,
      Math.round(r.metalCost), Math.round(r.centerStoneCost),
      r.centerStonePricePerCt !== null ? Math.round(r.centerStonePricePerCt) : '',
    ];
  });

  const csv = [headers, ...rows]
    .map((row) => row.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(','))
    .join('\n');

  const bom = '﻿';
  const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `jewelry-calc-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function App() {
  const [tab, setTab] = useState<Tab>('calc');
  const [form, setForm] = useState<FormData>(EMPTY_FORM);
  const [history, setHistory] = useState<HistoryEntry[]>(() =>
    loadStorage<HistoryEntry[]>(STORAGE_HISTORY, [])
  );
  const [marketRates, setMarketRates] = useState<MarketRate[]>(() =>
    loadStorage<MarketRate[]>(STORAGE_MARKET, [])
  );
  const [activeDate, setActiveDate] = useState<string>(() =>
    loadStorage<string>(STORAGE_ACTIVE_DATE, '')
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_HISTORY, JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    localStorage.setItem(STORAGE_MARKET, JSON.stringify(marketRates));
  }, [marketRates]);

  useEffect(() => {
    localStorage.setItem(STORAGE_ACTIVE_DATE, activeDate);
  }, [activeDate]);

  const activeMarketRate = useMemo(
    () => marketRates.find((r) => r.date === activeDate) ?? null,
    [marketRates, activeDate]
  );

  const effectiveMetalPrice = useMemo((): number => {
    if (!form.metalGrade) return 0;
    if (activeMarketRate) {
      return activeMarketRate.prices[form.metalGrade] ?? METAL_PRICES[form.metalGrade] ?? 0;
    }
    return METAL_PRICES[form.metalGrade] ?? 0;
  }, [form.metalGrade, activeMarketRate]);

  const canCalculate =
    !!form.metalGrade &&
    parseNum(form.productPrice) > 0 &&
    parseNum(form.productWeight) > 0;

  const result: CalculationResult | null = useMemo(() => {
    if (!canCalculate) return null;
    return calculate(form, effectiveMetalPrice);
  }, [form, effectiveMetalPrice, canCalculate]);

  const handleAddToHistory = () => {
    if (!result) return;
    const entry: HistoryEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleString('ja-JP', {
        month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit',
      }),
      form: { ...form },
      result,
    };
    setHistory((prev) => [...prev, entry]);
    setForm({ ...EMPTY_FORM, metalGrade: form.metalGrade, taxMode: form.taxMode });
  };

  const handleSaveMarketRate = (mr: MarketRate) => {
    setMarketRates((prev) => {
      const filtered = prev.filter((r) => r.date !== mr.date);
      return [...filtered, mr].sort((a, b) => a.date.localeCompare(b.date));
    });
    setActiveDate(mr.date);
  };

  const handleDeleteMarketRate = (date: string) => {
    setMarketRates((prev) => prev.filter((r) => r.date !== date));
    if (activeDate === date) setActiveDate('');
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f8f5f0' }}>
      {/* Header */}
      <header className="bg-white border-b border-gold-100 shadow-sm sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl" role="img" aria-label="diamond">💎</span>
            <h1 className="text-base font-bold text-gold-700 tracking-tight">
              ジュエリー石代計算
            </h1>
          </div>
          {activeMarketRate && (
            <div className="text-xs text-gold-600 bg-gold-50 border border-gold-200 rounded-full px-3 py-1">
              相場: {activeMarketRate.date} (×{activeMarketRate.rate})
            </div>
          )}
        </div>

        {/* Tab nav */}
        <div className="max-w-2xl mx-auto px-4 flex gap-1 pb-2">
          {([
            { id: 'calc', label: '計算' },
            { id: 'market', label: '相場管理' },
          ] as const).map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${
                tab === t.id
                  ? 'bg-gold-500 text-white'
                  : 'text-gray-500 hover:bg-gold-50 hover:text-gold-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-2xl mx-auto px-4 py-5 space-y-4">
        {tab === 'calc' && (
          <>
            <CalculatorForm
              form={form}
              onChange={setForm}
              activeMarketRate={activeMarketRate}
              effectiveMetalPrice={effectiveMetalPrice}
            />
            <ResultDisplay
              result={result}
              canCalculate={canCalculate}
              onAddToHistory={handleAddToHistory}
            />
            {history.length > 0 && (
              <HistoryList
                history={history}
                onClear={() => setHistory([])}
                onExportCsv={() => exportCsv(history)}
              />
            )}
          </>
        )}

        {tab === 'market' && (
          <MarketRatePanel
            marketRates={marketRates}
            activeDate={activeDate}
            onSave={handleSaveMarketRate}
            onSelectDate={(d) => setActiveDate(d)}
            onDelete={handleDeleteMarketRate}
          />
        )}
      </main>

      <footer className="max-w-2xl mx-auto px-4 py-6 text-center text-xs text-gray-300">
        ジュエリー石代計算アプリ
      </footer>
    </div>
  );
}

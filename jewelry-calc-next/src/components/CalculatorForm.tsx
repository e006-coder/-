'use client';

import { METAL_GRADE_OPTIONS, METAL_BASE_PRICE } from '@/lib/constants';
import type { FormData, MarketRate } from '@/lib/types';
import { TaxTabs } from './TaxTabs';
import { parseNum, getTaxDivisor } from '@/lib/calc';

interface Props {
  form: FormData;
  onChange: (f: FormData) => void;
  activeMarketRate: MarketRate | null;
  effectiveMetalPrice: number;
}

function Field({ label, unit, children }: { label: string; unit?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="label">
        {label}
        {unit && <span className="ml-1 text-gray-400 font-normal">{unit}</span>}
      </label>
      {children}
    </div>
  );
}

export function CalculatorForm({ form, onChange, activeMarketRate, effectiveMetalPrice }: Props) {
  const set = (key: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    onChange({ ...form, [key]: e.target.value });
  };

  const rawPrice = parseNum(form.productPrice);
  const taxDivisor = getTaxDivisor(form.taxMode);
  const taxExcludedPrice = rawPrice > 0 ? rawPrice / taxDivisor : null;
  const showTaxInfo = form.taxMode !== 'none' && rawPrice > 0;
  const masterPrice = METAL_BASE_PRICE[form.metalGrade] ?? 0;

  return (
    <div className="card space-y-5">
      <h2 className="text-base font-semibold text-gold-700 border-b border-gold-100 pb-3">
        製品情報の入力
      </h2>

      {/* 日付 */}
      <Field label="日付">
        <input
          className="input"
          type="date"
          value={form.date}
          onChange={set('date')}
        />
        {form.date && !activeMarketRate && (
          <p className="mt-1 text-xs text-amber-600">
            ⚠ 選択日の相場データがありません。相場設定画面で登録してください。
          </p>
        )}
        {form.date && activeMarketRate && (
          <p className="mt-1 text-xs text-gold-600">
            ✓ {form.date} の相場を適用中
          </p>
        )}
      </Field>

      {/* 品位 + 地金単価 */}
      <div className="grid grid-cols-2 gap-3">
        <Field label="品位 ★">
          <select className="input" value={form.metalGrade} onChange={set('metalGrade')}>
            <option value="">選択してください</option>
            {METAL_GRADE_OPTIONS.map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </Field>
        <Field label="地金単価" unit="円/g">
          <div className="input-readonly text-right">
            {form.metalGrade ? (
              <span>
                <span className="text-gold-700 font-semibold">
                  {effectiveMetalPrice.toLocaleString()}
                </span>
                {activeMarketRate && (
                  <span className="ml-1 text-xs text-gray-400">
                    (基準: {masterPrice.toLocaleString()})
                  </span>
                )}
              </span>
            ) : '—'}
          </div>
        </Field>
      </div>

      {/* 製品区分 + No. */}
      <div className="grid grid-cols-2 gap-3">
        <Field label="製品区分">
          <input className="input" type="text" placeholder="例: リング" value={form.productCategory} onChange={set('productCategory')} />
        </Field>
        <Field label="No.">
          <input className="input" type="text" placeholder="例: A-001" value={form.productNo} onChange={set('productNo')} />
        </Field>
      </div>

      {/* 製品代 */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="label mb-0">
            製品代 ★<span className="ml-1 text-gray-400 font-normal">円</span>
          </label>
          <TaxTabs value={form.taxMode} onChange={(v) => onChange({ ...form, taxMode: v })} />
        </div>
        <input className="input text-right" type="number" min="0" placeholder="0" value={form.productPrice} onChange={set('productPrice')} />
        {showTaxInfo && taxExcludedPrice !== null && (
          <p className="mt-1 text-xs text-gold-600">
            税込 ¥{rawPrice.toLocaleString()} → 税抜 ¥{Math.round(taxExcludedPrice).toLocaleString()}（TAX{form.taxMode}%）
          </p>
        )}
      </div>

      {/* 製品重量 */}
      <Field label="製品重量 ★" unit="g">
        <input className="input text-right" type="number" min="0" step="0.01" placeholder="0.00" value={form.productWeight} onChange={set('productWeight')} />
      </Field>

      <hr className="border-gold-100" />
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">石情報</p>

      {/* 中石重量 */}
      <Field label="中石重量" unit="ct">
        <input className="input text-right" type="number" min="0" step="0.01" placeholder="0.00" value={form.centerStoneWeight} onChange={set('centerStoneWeight')} />
      </Field>

      {/* 脇石 */}
      <div className="grid grid-cols-2 gap-3">
        <Field label="脇石重量" unit="ct">
          <input className="input text-right" type="number" min="0" step="0.001" placeholder="0.000" value={form.sideStoneWeight} onChange={set('sideStoneWeight')} />
        </Field>
        <Field label="脇石単価" unit="円/ct">
          <input className="input text-right" type="number" min="0" placeholder="0" value={form.sideStonePricePerCt} onChange={set('sideStonePricePerCt')} />
        </Field>
      </div>

      {/* MD */}
      <div className="grid grid-cols-2 gap-3">
        <Field label="MD重量" unit="ct">
          <input className="input text-right" type="number" min="0" step="0.001" placeholder="0.000" value={form.mdWeight} onChange={set('mdWeight')} />
        </Field>
        <Field label="MD単価" unit="円/ct">
          <input className="input text-right" type="number" min="0" placeholder="0" value={form.mdPricePerCt} onChange={set('mdPricePerCt')} />
        </Field>
      </div>
    </div>
  );
}

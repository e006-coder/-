'use client';

import type { TaxMode } from '@/lib/types';

interface Props {
  value: TaxMode;
  onChange: (v: TaxMode) => void;
}

const TABS: { label: string; value: TaxMode }[] = [
  { label: 'TAXなし', value: 'none' },
  { label: 'TAX 4%', value: '4' },
  { label: 'TAX 10%', value: '10' },
];

export function TaxTabs({ value, onChange }: Props) {
  return (
    <div className="flex rounded-lg border border-gray-200 overflow-hidden text-xs font-medium w-fit">
      {TABS.map((tab) => (
        <button
          key={tab.value}
          type="button"
          onClick={() => onChange(tab.value)}
          className={`px-3 py-1.5 transition ${
            value === tab.value
              ? 'bg-gold-500 text-white'
              : 'bg-white text-gray-600 hover:bg-gold-50'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

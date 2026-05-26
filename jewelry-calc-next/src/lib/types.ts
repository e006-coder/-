export type TaxMode = 'none' | '4' | '10';
export type MetalGroup = "Au" | "Pt" | "SV";

export interface FormData {
  date: string;        // reference date for market rate lookup
  metalGrade: string;
  productCategory: string;
  productNo: string;
  productPrice: string;
  productWeight: string;
  centerStoneWeight: string;
  sideStoneWeight: string;
  sideStonePricePerCt: string;
  mdWeight: string;
  mdPricePerCt: string;
  taxMode: TaxMode;
}

export interface CalculationResult {
  metalPricePerG: number;
  metalWeight: number;
  metalCost: number;
  mdCost: number;
  sideStoneCost: number;
  centerStoneCost: number;
  centerStonePricePerCt: number | null;
  taxExcludedPrice: number;
  isNegative: boolean;
  stoneWeightExceedsProduct: boolean;
}

export interface HistoryEntry {
  id: string;
  timestamp: string;
  form: FormData;
  result: CalculationResult;
}

export interface MarketRate {
  date: string;
  rates: { Au: number; Pt: number; SV: number };
  prices: Record<string, number>;      // effective price per grade
  manualOverrides: Record<string, boolean>; // which grades were manually set
}

export type TaxMode = 'none' | '4' | '10';

export interface FormData {
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
  rate: number;
  prices: Record<string, number>;
}

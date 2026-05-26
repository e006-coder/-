import { CT_TO_G } from './constants';
import type { FormData, CalculationResult, TaxMode } from './types';

export function getTaxDivisor(mode: TaxMode): number {
  if (mode === '10') return 1.10;
  if (mode === '4') return 1.04;
  return 1;
}

export function parseNum(v: string): number {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

export function calculate(form: FormData, metalPricePerG: number): CalculationResult {
  const taxDivisor = getTaxDivisor(form.taxMode);
  const rawPrice = parseNum(form.productPrice);
  const taxExcludedPrice = rawPrice / taxDivisor;

  const productWeightG = parseNum(form.productWeight);
  const centerStoneWeightCt = parseNum(form.centerStoneWeight);
  const sideStoneWeightCt = parseNum(form.sideStoneWeight);
  const mdWeightCt = parseNum(form.mdWeight);

  const centerStoneWeightG = centerStoneWeightCt * CT_TO_G;
  const sideStoneWeightG = sideStoneWeightCt * CT_TO_G;
  const mdWeightG = mdWeightCt * CT_TO_G;

  const stoneWeightExceedsProduct =
    centerStoneWeightG + sideStoneWeightG + mdWeightG > productWeightG && productWeightG > 0;

  const metalWeight = productWeightG - centerStoneWeightG - sideStoneWeightG - mdWeightG;
  const metalCost = metalWeight * metalPricePerG;

  const sideStonePricePerCt = parseNum(form.sideStonePricePerCt);
  const mdPricePerCt = parseNum(form.mdPricePerCt);

  const sideStoneCost = sideStoneWeightCt * sideStonePricePerCt;
  const mdCost = mdWeightCt * mdPricePerCt;

  const centerStoneCost = taxExcludedPrice - metalCost - sideStoneCost - mdCost;
  const isNegative = centerStoneCost < 0;

  const centerStonePricePerCt =
    centerStoneWeightCt > 0 ? centerStoneCost / centerStoneWeightCt : null;

  return {
    metalPricePerG,
    metalWeight,
    metalCost,
    mdCost,
    sideStoneCost,
    centerStoneCost,
    centerStonePricePerCt,
    taxExcludedPrice,
    isNegative,
    stoneWeightExceedsProduct,
  };
}

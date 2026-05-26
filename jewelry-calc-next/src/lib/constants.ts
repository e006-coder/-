export type MetalGroup = "Au" | "Pt" | "SV";

export interface MetalMasterItem {
  label: string;
  basePrice: number;
  group: MetalGroup;
}

export const METAL_MASTER: MetalMasterItem[] = [
  // Gold系
  { label: "Au IG",              basePrice: 26310, group: "Au" },
  { label: "K24",                basePrice: 25791, group: "Au" },
  { label: "K22",                basePrice: 23371, group: "Au" },
  { label: "K21.6",              basePrice: 23029, group: "Au" },
  { label: "K20",                basePrice: 21316, group: "Au" },
  { label: "K18",                basePrice: 19732, group: "Au" },
  { label: "K14",                basePrice: 14478, group: "Au" },
  { label: "K10",                basePrice: 10264, group: "Au" },
  { label: "K9",                 basePrice:  9077, group: "Au" },
  { label: "K18WG",              basePrice: 19732, group: "Au" },
  { label: "K14WG",              basePrice: 14478, group: "Au" },
  // Platinum系
  { label: "Pt IG",              basePrice: 11641, group: "Pt" },
  { label: "Pt1000",             basePrice: 11415, group: "Pt" },
  { label: "Pt950",              basePrice: 10834, group: "Pt" },
  { label: "Pt900",              basePrice: 10476, group: "Pt" },
  { label: "Pt850",              basePrice:  9894, group: "Pt" },
  // Silver系
  { label: "SV IG",              basePrice:   426, group: "SV" },
  { label: "SV1000",             basePrice:   388, group: "SV" },
  { label: "SV950",              basePrice:   379, group: "SV" },
  { label: "SV925",              basePrice:   354, group: "SV" },
  // 複合系（Au基準）
  { label: "K18/Pt900(9:1)",     basePrice: 18771, group: "Au" },
  { label: "K18/Pt850(9:1)",     basePrice: 18754, group: "Au" },
  { label: "K18/Pt900(7:3)",     basePrice: 16905, group: "Au" },
  { label: "K18/Pt850(7:3)",     basePrice: 15992, group: "Au" },
  { label: "K18/Pt900(5:5)",     basePrice: 14324, group: "Au" },
  { label: "K18/Pt850(5:5)",     basePrice: 14054, group: "Au" },
  // 複合系（Pt基準）
  { label: "Pt900/K18(9:1)",     basePrice: 10634, group: "Pt" },
  { label: "Pt850/K18(9:1)",     basePrice: 10148, group: "Pt" },
  { label: "Pt900/K18(7:3)",     basePrice: 12454, group: "Pt" },
  { label: "Pt850/K18(7:3)",     basePrice: 12076, group: "Pt" },
];

export const METAL_GRADE_OPTIONS = METAL_MASTER.map((m) => m.label);
export const METAL_BASE_PRICE: Record<string, number> = Object.fromEntries(
  METAL_MASTER.map((m) => [m.label, m.basePrice])
);
export const METAL_GROUP: Record<string, MetalGroup> = Object.fromEntries(
  METAL_MASTER.map((m) => [m.label, m.group])
);

export const CT_TO_G = 0.2;

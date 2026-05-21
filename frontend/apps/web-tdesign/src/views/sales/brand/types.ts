export interface BrandSeriesPoint {
  sales: number;
  time: string;
  yoyGrowth: null | number;
}

export interface BrandSeriesRecord {
  brand_name: string;
  points: BrandSeriesPoint[];
}

export interface BrandSeriesPoint {
  sales: number;
  time: string;
}

export interface BrandSeriesRecord {
  brand_name: string;
  points: BrandSeriesPoint[];
}

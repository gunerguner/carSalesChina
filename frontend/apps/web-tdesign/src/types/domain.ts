export type DataType = 'production' | 'retail';
export type LevelType = 'all' | 'bev' | 'nev';
export type AnalysisGranularity = 'monthly' | 'yearly';

export interface YearMonthRecord {
  year: number;
  month: number;
}

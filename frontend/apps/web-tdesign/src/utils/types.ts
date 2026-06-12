export type DataType = 'production' | 'retail';
export type LevelType = 'all' | 'bev' | 'nev';
export type AnalysisGranularity = 'monthly' | 'yearly';

export interface YearMonthRecord {
  year: number;
  month: number;
}

/** i18n key lookup passed into chart/table builders (typically `$t`). */
export type Translate = (key: string) => string;

export const ORIGIN_DIMENSIONS = [
  {
    key: 'domestic',
    tableLabelKey: 'pages.analysis.origin.domestic',
    chartLabelKey: 'pages.analysis.origin.domesticLabel',
  },
  {
    key: 'german',
    tableLabelKey: 'pages.analysis.origin.german',
    chartLabelKey: 'pages.analysis.origin.germanLabel',
  },
  {
    key: 'japanese',
    tableLabelKey: 'pages.analysis.origin.japanese',
    chartLabelKey: 'pages.analysis.origin.japaneseLabel',
  },
  {
    key: 'american',
    tableLabelKey: 'pages.analysis.origin.american',
    chartLabelKey: 'pages.analysis.origin.americanLabel',
  },
  {
    key: 'european',
    tableLabelKey: 'pages.analysis.origin.european',
    chartLabelKey: 'pages.analysis.origin.europeanLabel',
  },
  {
    key: 'korean',
    tableLabelKey: 'pages.analysis.origin.korean',
    chartLabelKey: 'pages.analysis.origin.koreanLabel',
  },
  {
    key: 'french',
    tableLabelKey: 'pages.analysis.origin.french',
    chartLabelKey: 'pages.analysis.origin.frenchLabel',
  },
] as const;

export type OriginShareKey = (typeof ORIGIN_DIMENSIONS)[number]['key'];

export const ORIGIN_KEYS: readonly OriginShareKey[] = ORIGIN_DIMENSIONS.map(
  (d) => d.key,
);

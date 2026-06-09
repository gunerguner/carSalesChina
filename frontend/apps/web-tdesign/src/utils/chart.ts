import { formatNumberOrDash, formatSalesAxisLabel } from './format';

/** Default ECharts categorical colors (subset indices used e.g. for brand line charts). */
export const CHART_PALETTE = [
  '#5470c6',
  '#91cc75',
  '#fac858',
  '#ee6666',
  '#73c0de',
] as const;

/** Indices into `CHART_PALETTE` for brand multi-line (matches previous hard-coded order). */
export const BRAND_LINE_PALETTE_INDICES = [0, 3, 4, 1] as const;

export function getChartPaletteColor(index: number): string {
  return CHART_PALETTE[index % CHART_PALETTE.length]!;
}

export const ORIGIN_KEYS = [
  'domestic',
  'german',
  'japanese',
  'american',
  'european',
  'korean',
  'french',
] as const;

export type OriginShareKey = (typeof ORIGIN_KEYS)[number];

export const ORIGIN_COLORS: Record<OriginShareKey, string> = {
  domestic: '#5470c6',
  german: '#91cc75',
  japanese: '#fac858',
  american: '#ee6666',
  european: '#73c0de',
  korean: '#3ba272',
  french: '#9a6bef',
};

export function getEmptyChartOption(text: string) {
  return {
    animation: false,
    title: {
      text,
      left: 'center',
      top: 'center',
      textStyle: { color: '#999', fontSize: 14 },
    },
    xAxis: { type: 'category' as const, data: [] },
    yAxis: { type: 'value' as const },
    series: [],
  };
}

export { formatSalesAxisLabel };

export function lineSeriesTooltipFormatter(params: any): string {
  const arr = Array.isArray(params) ? params : [params];
  if (arr.length === 0) return '';
  const head = arr[0];
  const label = head.axisValueLabel ?? head.name ?? '';
  const body = arr
    .map((p: any) => {
      const v = formatNumberOrDash(Math.round(Number(p.value)));
      return `${p.marker}${p.seriesName}: ${v}`;
    })
    .join('<br/>');
  return `${label}<br/>${body}`;
}

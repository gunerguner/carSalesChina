import type { ECOption } from '@vben/plugins/echarts';

import { formatNumberOrDash, formatSalesAxisLabel } from './format';

export interface LineTooltipParams {
  axisValue?: string;
  axisValueLabel?: string;
  marker?: string;
  name?: string;
  seriesName?: string;
  value?: number | string;
}

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
  return CHART_PALETTE[index % CHART_PALETTE.length] ?? '#5470c6';
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

export function getEmptyChartOption(text: string): ECOption {
  return {
    animation: false,
    title: {
      text,
      left: 'center',
      top: 'center',
      textStyle: { color: '#999', fontSize: 14 },
    },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [],
  };
}

export { formatSalesAxisLabel };

export function lineSeriesTooltipFormatter(
  params: LineTooltipParams | LineTooltipParams[],
): string {
  const arr = Array.isArray(params) ? params : [params];
  if (arr.length === 0) return '';
  const head = arr[0];
  if (!head) return '';
  const label = String(head.axisValueLabel ?? head.name ?? '');
  const body = arr
    .map((p) => {
      const v = formatNumberOrDash(Math.round(Number(p.value)));
      return `${p.marker}${p.seriesName}: ${v}`;
    })
    .join('<br/>');
  return `${label}<br/>${body}`;
}

export function buildValueYAxis(locale: string): ECOption['yAxis'] {
  return {
    type: 'value',
    axisLabel: {
      formatter: (val: number) => formatSalesAxisLabel(val, locale),
    },
  };
}

export function buildPercentYAxis(maxCap = 100): ECOption['yAxis'] {
  return {
    type: 'value',
    axisLabel: { formatter: '{value}%' },
    max: maxCap,
  };
}

export interface LineChartSeriesItem {
  areaStyle?: { opacity: number };
  color?: string;
  data: number[];
  name: string;
}

export interface BuildLineChartOptionParams {
  grid?: ECOption['grid'];
  legend?: ECOption['legend'];
  locale?: string;
  percentMaxCap?: number;
  series: LineChartSeriesItem[];
  tooltipFormatter?: (
    params: LineTooltipParams | LineTooltipParams[],
  ) => string;
  xAxisExtra?: { interval: number; rotate: number };
  xData: string[];
  yAxisType?: 'percent' | 'value';
}

export function buildLineChartOption(
  params: BuildLineChartOptionParams,
): ECOption {
  const {
    grid = {
      bottom: '3%',
      containLabel: true,
      left: '3%',
      right: '4%',
      top: '8%',
    },
    legend,
    locale = 'zh-CN',
    percentMaxCap = 100,
    series,
    tooltipFormatter = lineSeriesTooltipFormatter,
    xAxisExtra,
    xData,
    yAxisType = 'value',
  } = params;

  const yAxis =
    yAxisType === 'percent'
      ? {
          ...buildPercentYAxis(percentMaxCap),
          max:
            percentMaxCap < 100
              ? (value: { max: number }) =>
                  Math.min(Math.ceil(value.max * 1.2), percentMaxCap)
              : percentMaxCap,
        }
      : buildValueYAxis(locale);

  return {
    animation: false,
    grid,
    legend,
    series: series.map((item) => ({
      areaStyle: item.areaStyle,
      data: item.data,
      itemStyle: item.color ? { color: item.color } : undefined,
      name: item.name,
      smooth: true,
      type: 'line',
    })),
    tooltip: {
      axisPointer: { type: 'line' },
      formatter: tooltipFormatter as (params: unknown) => string,
      trigger: 'axis',
    },
    xAxis: {
      boundaryGap: false,
      data: xData,
      type: 'category',
      ...(xAxisExtra && { axisLabel: xAxisExtra }),
    },
    yAxis,
  };
}

export interface StackedBarSeriesItem {
  color: string;
  data: number[];
  name: string;
}

export interface BuildStackedBarChartOptionParams {
  grid?: ECOption['grid'];
  legend: ECOption['legend'];
  series: StackedBarSeriesItem[];
  xData: string[];
  yMax?: number;
}

export function buildStackedBarChartOption(
  params: BuildStackedBarChartOptionParams,
): ECOption {
  const {
    grid = {
      bottom: '15%',
      containLabel: true,
      left: '3%',
      right: '4%',
      top: '8%',
    },
    legend,
    series,
    xData,
    yMax = 100,
  } = params;

  return {
    animation: false,
    grid,
    legend,
    series: series.map((item) => ({
      data: item.data,
      emphasis: { focus: 'series' },
      itemStyle: { color: item.color },
      name: item.name,
      stack: 'total',
      type: 'bar',
    })),
    tooltip: { axisPointer: { type: 'shadow' }, trigger: 'axis' },
    xAxis: { data: xData, type: 'category' },
    yAxis: buildPercentYAxis(yMax),
  };
}

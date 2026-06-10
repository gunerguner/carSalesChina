import type { ECOption } from '@vben/plugins/echarts';

import { formatOrDash } from './format';

export interface LineTooltipParams {
  axisValue?: string;
  axisValueLabel?: string;
  marker?: string;
  name?: string;
  seriesName?: string;
  value?: number | string;
}

const CHART_PALETTE = [
  '#5470c6',
  '#91cc75',
  '#fac858',
  '#ee6666',
  '#73c0de',
] as const;

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

function lineSeriesTooltipFormatter(
  params: LineTooltipParams | LineTooltipParams[],
): string {
  const arr = Array.isArray(params) ? params : [params];
  const head = arr[0];
  if (!head) return '';
  const label = head.axisValueLabel ?? head.name ?? '';
  const body = arr
    .map(
      (p) =>
        `${p.marker}${p.seriesName}: ${formatOrDash(Math.round(Number(p.value)))}`,
    )
    .join('<br/>');
  return `${label}<br/>${body}`;
}

function valueYAxis(locale: string): ECOption['yAxis'] {
  return {
    type: 'value',
    axisLabel: {
      formatter: (v: number) => {
        if (v >= 10_000) {
          return locale === 'zh-CN'
            ? `${(v / 10_000).toFixed(0)}万`
            : `${(v / 1000).toFixed(0)}k`;
        }
        return v.toLocaleString(locale);
      },
    },
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

const DEFAULT_LINE_GRID = {
  bottom: '3%',
  containLabel: true,
  left: '3%',
  right: '4%',
  top: '8%',
};

export function buildLineChartOption(
  params: BuildLineChartOptionParams,
): ECOption {
  const {
    grid = DEFAULT_LINE_GRID,
    legend,
    locale = 'zh-CN',
    percentMaxCap = 100,
    series,
    tooltipFormatter = lineSeriesTooltipFormatter,
    xAxisExtra,
    xData,
    yAxisType = 'value',
  } = params;

  const yAxis: ECOption['yAxis'] =
    yAxisType === 'percent'
      ? {
          type: 'value',
          axisLabel: { formatter: '{value}%' },
          max:
            percentMaxCap < 100
              ? (v: { max: number }) =>
                  Math.min(Math.ceil(v.max * 1.2), percentMaxCap)
              : percentMaxCap,
        }
      : valueYAxis(locale);

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

const DEFAULT_BAR_GRID = {
  bottom: '15%',
  containLabel: true,
  left: '3%',
  right: '4%',
  top: '8%',
};

export function buildStackedBarChartOption(
  params: BuildStackedBarChartOptionParams,
): ECOption {
  const { grid = DEFAULT_BAR_GRID, legend, series, xData, yMax = 100 } = params;
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
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' }, max: yMax },
  };
}

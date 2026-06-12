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

const CHART_VAR_KEYS = [
  '--chart-1',
  '--chart-2',
  '--chart-3',
  '--chart-4',
  '--chart-5',
] as const;

const CHART_FALLBACKS = [
  '#475569',
  '#64748b',
  '#94a3b8',
  '#cbd5e1',
  '#e2e8f0',
] as const;

function readCssVar(name: string, fallback: string): string {
  if (typeof document === 'undefined') return fallback;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

function chartTheme() {
  return {
    axis: readCssVar('--chart-axis', '#64748b'),
    grid: readCssVar('--chart-grid', '#e2e8f0'),
    pointer: readCssVar('--chart-pointer', '#475569'),
    tooltipBg: readCssVar('--chart-tooltip-bg', '#ffffff'),
    tooltipBorder: readCssVar('--chart-tooltip-border', '#e2e8f0'),
    tooltipText: readCssVar('--chart-tooltip-text', '#1e293b'),
  };
}

export const BRAND_LINE_PALETTE_INDICES = [0, 3, 4, 1] as const;

export function getChartPaletteColor(index: number): string {
  const key = CHART_VAR_KEYS[index % CHART_VAR_KEYS.length] ?? '--chart-1';
  return readCssVar(
    key,
    CHART_FALLBACKS[index % CHART_FALLBACKS.length] ?? '#475569',
  );
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

export function getOriginShareColor(key: OriginShareKey): string {
  const index = ORIGIN_KEYS.indexOf(key);
  return getChartPaletteColor(Math.max(index, 0));
}

export function getEmptyChartOption(text: string): ECOption {
  const theme = chartTheme();
  return {
    animation: false,
    title: {
      text,
      left: 'center',
      top: 'center',
      textStyle: { color: theme.axis, fontSize: 14, fontWeight: 400 },
    },
    xAxis: { show: false, type: 'category', data: [] },
    yAxis: { show: false, type: 'value' },
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

function themedCategoryAxis() {
  const theme = chartTheme();
  return {
    axisLabel: { color: theme.axis, fontSize: 11 },
    axisLine: { lineStyle: { color: theme.grid } },
  };
}

function valueAxisLabelFormatter(locale: string) {
  return (v: number) => {
    if (v >= 10_000) {
      return locale === 'zh-CN'
        ? `${(v / 10_000).toFixed(0)}万`
        : `${(v / 1000).toFixed(0)}k`;
    }
    return v.toLocaleString(locale);
  };
}

function themedValueAxis(locale?: string, percent = false) {
  const theme = chartTheme();
  const axisLabel: {
    color: string;
    fontSize: number;
    formatter?: ((v: number) => string) | string;
  } = {
    color: theme.axis,
    fontSize: 11,
  };
  if (percent) {
    axisLabel.formatter = '{value}%';
  } else if (locale) {
    axisLabel.formatter = valueAxisLabelFormatter(locale);
  }

  return {
    axisLabel,
    axisLine: { lineStyle: { color: theme.grid } },
    splitLine: {
      lineStyle: { color: theme.grid, opacity: 0.45, type: 'dashed' as const },
    },
  };
}

function themedTooltip(
  formatter?: (params: LineTooltipParams | LineTooltipParams[]) => string,
  axisPointerType: 'line' | 'shadow' = 'line',
) {
  const theme = chartTheme();
  return {
    axisPointer: {
      type: axisPointerType,
      lineStyle: { color: theme.pointer, width: 1 },
      shadowStyle: { color: theme.pointer, opacity: 0.08 },
    },
    backgroundColor: theme.tooltipBg,
    borderColor: theme.tooltipBorder,
    borderWidth: 1,
    confine: true,
    extraCssText:
      'border-radius: 6px; box-shadow: 0 4px 12px rgb(0 0 0 / 12%);',
    formatter: formatter as ((params: unknown) => string) | undefined,
    padding: [8, 12],
    textStyle: { color: theme.tooltipText, fontSize: 12 },
    trigger: 'axis' as const,
  };
}

const NO_FOCUS_EMPHASIS = {
  disabled: true,
  focus: 'none' as const,
};

function valueYAxis(locale: string): ECOption['yAxis'] {
  return {
    type: 'value',
    ...themedValueAxis(locale),
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
          ...themedValueAxis(undefined, true),
          max:
            percentMaxCap < 100
              ? (v: { max: number }) =>
                  Math.min(Math.ceil(v.max * 1.2), percentMaxCap)
              : percentMaxCap,
        }
      : valueYAxis(locale);

  const categoryAxis = themedCategoryAxis();

  return {
    animation: true,
    animationDuration: 400,
    animationEasing: 'cubicOut',
    grid,
    legend: legend
      ? {
          ...legend,
          textStyle: { color: chartTheme().axis, fontSize: 11 },
        }
      : undefined,
    series: series.map((item) => ({
      areaStyle: item.areaStyle,
      data: item.data,
      emphasis: NO_FOCUS_EMPHASIS,
      itemStyle: item.color ? { color: item.color } : undefined,
      lineStyle: { width: 2 },
      name: item.name,
      showSymbol: false,
      smooth: true,
      type: 'line',
    })),
    tooltip: themedTooltip(tooltipFormatter, 'line'),
    xAxis: {
      boundaryGap: false,
      data: xData,
      type: 'category',
      ...categoryAxis,
      ...(xAxisExtra && {
        axisLabel: { ...categoryAxis.axisLabel, ...xAxisExtra },
      }),
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
  const theme = chartTheme();

  return {
    animation: true,
    animationDuration: 400,
    animationEasing: 'cubicOut',
    grid,
    legend: {
      ...legend,
      textStyle: { color: theme.axis, fontSize: 11 },
    },
    series: series.map((item) => ({
      barMaxWidth: 28,
      data: item.data,
      emphasis: NO_FOCUS_EMPHASIS,
      itemStyle: { borderRadius: [2, 2, 0, 0], color: item.color },
      name: item.name,
      stack: 'total',
      type: 'bar',
    })),
    tooltip: themedTooltip(undefined, 'shadow'),
    xAxis: {
      data: xData,
      type: 'category',
      ...themedCategoryAxis(),
    },
    yAxis: {
      type: 'value',
      ...themedValueAxis(undefined, true),
      max: yMax,
    },
  };
}

import type { ECOption } from '@vben/plugins/echarts';

import { formatOrDash } from './format';
import { getChartTheme } from './style';

export interface LineTooltipParams {
  axisValue?: string;
  axisValueLabel?: string;
  marker?: string;
  name?: string;
  seriesName?: string;
  value?: number | string;
}

export function getEmptyChartOption(text: string): ECOption {
  const theme = getChartTheme();
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

/** Returns empty chart option when `data` has no rows; otherwise undefined. */
export function emptyChartIfNoData(
  data: { length: number },
  message: string,
): ECOption | undefined {
  if (data.length === 0) return getEmptyChartOption(message);
  return undefined;
}

export function seriesTooltipFormatter(
  params: LineTooltipParams | LineTooltipParams[],
  formatValue: (num: null | number) => string,
): string {
  const arr = Array.isArray(params) ? params : [params];
  const head = arr[0];
  if (!head) return '';
  const label = head.axisValueLabel ?? head.name ?? '';
  const body = arr
    .map((p) => {
      const raw = p.value;
      const num = raw === null || raw === undefined ? null : Number(raw);
      const value = num === null || Number.isNaN(num) ? null : num;
      return `${p.marker}${p.seriesName}: ${formatValue(value)}`;
    })
    .join('<br/>');
  return `${label}<br/>${body}`;
}

export function lineSeriesTooltipFormatter(
  params: LineTooltipParams | LineTooltipParams[],
  locale?: string,
): string {
  return seriesTooltipFormatter(params, (num) => {
    const rounded = num === null ? null : Math.round(num);
    return formatOrDash(rounded, '', locale);
  });
}

export function percentSeriesTooltipFormatter(
  params: LineTooltipParams | LineTooltipParams[],
): string {
  return seriesTooltipFormatter(params, (num) =>
    num === null ? '-' : `${num.toFixed(1)}%`,
  );
}

export function themedCategoryAxis() {
  const theme = getChartTheme();
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

export function themedValueAxis(locale?: string, percent = false) {
  const theme = getChartTheme();
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

export function themedTooltip(
  formatter?: (params: LineTooltipParams | LineTooltipParams[]) => string,
  axisPointerType: 'line' | 'shadow' = 'line',
) {
  const theme = getChartTheme();
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

export const NO_FOCUS_EMPHASIS = {
  disabled: true,
  focus: 'none' as const,
};

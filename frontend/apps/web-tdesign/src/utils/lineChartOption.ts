import type { ECOption } from '@vben/plugins/echarts';

import type { LineTooltipParams } from './chartShared';

import {
  lineSeriesTooltipFormatter,
  NO_FOCUS_EMPHASIS,
  themedCategoryAxis,
  themedTooltip,
  themedValueAxis,
} from './chartShared';
import { getChartTheme } from './style';

export interface LineChartSeriesItem {
  areaStyle?: { opacity: number };
  color?: string;
  data: (null | number)[];
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

function valueYAxis(locale: string): ECOption['yAxis'] {
  return {
    type: 'value',
    ...themedValueAxis(locale),
  };
}

export function buildLineChartOption(
  params: BuildLineChartOptionParams,
): ECOption {
  const {
    grid = DEFAULT_LINE_GRID,
    legend,
    locale = 'zh-CN',
    percentMaxCap = 100,
    series,
    tooltipFormatter = (p) => lineSeriesTooltipFormatter(p, locale),
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
    animation: false,
    grid,
    legend: legend
      ? {
          ...legend,
          textStyle: { color: getChartTheme().axis, fontSize: 11 },
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

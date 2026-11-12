import type { ECOption } from '@vben/plugins/echarts';

import {
  NO_FOCUS_EMPHASIS,
  percentSeriesTooltipFormatter,
  themedCategoryAxis,
  themedTooltip,
  themedValueAxis,
} from './chartShared';
import { getChartTheme } from './style';

export interface StackedAreaSeriesItem {
  color: string;
  data: number[];
  name: string;
}

export interface BuildStackedAreaChartOptionParams {
  grid?: ECOption['grid'];
  legend: ECOption['legend'];
  series: StackedAreaSeriesItem[];
  xData: string[];
  yMax?: number;
}

const DEFAULT_AREA_GRID = {
  bottom: '15%',
  containLabel: true,
  left: '3%',
  right: '4%',
  top: '8%',
};

export function buildStackedAreaChartOption(
  params: BuildStackedAreaChartOptionParams,
): ECOption {
  const {
    grid = DEFAULT_AREA_GRID,
    legend,
    series,
    xData,
    yMax = 100,
  } = params;
  const theme = getChartTheme();

  return {
    animation: false,
    grid,
    legend: {
      ...legend,
      textStyle: { color: theme.axis, fontSize: 11 },
    },
    series: series.map((item) => ({
      areaStyle: { opacity: 0.85 },
      data: item.data,
      emphasis: NO_FOCUS_EMPHASIS,
      itemStyle: { color: item.color },
      lineStyle: { width: 1.5 },
      name: item.name,
      showSymbol: false,
      smooth: true,
      stack: 'total',
      type: 'line',
    })),
    tooltip: themedTooltip(percentSeriesTooltipFormatter, 'line'),
    xAxis: {
      boundaryGap: false,
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

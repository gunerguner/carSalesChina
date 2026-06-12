import type { ECOption } from '@vben/plugins/echarts';

import type { OriginShareTrendRecord } from '#/api/analysis';

import {
  buildStackedBarChartOption,
  getEmptyChartOption,
  getOriginShareColor,
} from '#/utils/chart';
import { toMonthKey } from '#/utils/period';

import { ORIGIN_DIMENSIONS } from '../originShareDimensions';

type Translate = (key: string) => string;

export function buildOriginShareChartOption(
  data: OriginShareTrendRecord[],
  t: Translate,
): ECOption {
  if (!data || data.length === 0) {
    return getEmptyChartOption(t('pages.common.noData'));
  }

  const timeLabels = data.map((item) => toMonthKey(item.year, item.month));
  const series = ORIGIN_DIMENSIONS.map(({ key, chartLabelKey }) => ({
    color: getOriginShareColor(key),
    data: data.map((item) => +item[key].toFixed(2)),
    name: t(chartLabelKey),
  }));

  return buildStackedBarChartOption({
    legend: {
      bottom: 0,
      data: series.map((item) => item.name),
      type: 'scroll',
    },
    series,
    xData: timeLabels,
  });
}

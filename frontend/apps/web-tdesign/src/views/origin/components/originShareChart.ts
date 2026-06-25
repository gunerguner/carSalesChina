import type { ECOption } from '@vben/plugins/echarts';

import type { OriginShareTrendRecord } from '#/api/analysis';

import { buildStackedBarChartOption, emptyChartIfNoData } from '#/utils/chart';
import { toMonthKey } from '#/utils/period';
import { getOriginShareColor } from '#/utils/style';
import { ORIGIN_DIMENSIONS, type Translate } from '#/utils/types';

export function buildOriginShareChartOption(
  data: OriginShareTrendRecord[],
  t: Translate,
): ECOption {
  const empty = emptyChartIfNoData(data ?? [], t('pages.common.noData'));
  if (empty) return empty;

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

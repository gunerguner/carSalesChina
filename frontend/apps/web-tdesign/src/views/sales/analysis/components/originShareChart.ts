import type { ECOption } from '@vben/plugins/echarts';

import type { OriginShareTrendRecord } from '#/api/sales/analysis';
import type { OriginShareKey } from '#/utils/chart';

import {
  buildStackedBarChartOption,
  getEmptyChartOption,
  getOriginShareColor,
  ORIGIN_KEYS,
} from '#/utils/chart';
import { toMonthKey } from '#/utils/period';

type Translate = (key: string) => string;

const ORIGIN_LABEL_KEYS: Record<OriginShareKey, string> = {
  american: 'sales.analysis.origin.americanLabel',
  domestic: 'sales.analysis.origin.domesticLabel',
  european: 'sales.analysis.origin.europeanLabel',
  french: 'sales.analysis.origin.frenchLabel',
  german: 'sales.analysis.origin.germanLabel',
  japanese: 'sales.analysis.origin.japaneseLabel',
  korean: 'sales.analysis.origin.koreanLabel',
};

export function buildOriginShareChartOption(
  data: OriginShareTrendRecord[],
  t: Translate,
): ECOption {
  if (!data || data.length === 0) {
    return getEmptyChartOption(t('sales.common.noData'));
  }

  const timeLabels = data.map((item) => toMonthKey(item.year, item.month));
  const series = ORIGIN_KEYS.map((key) => ({
    color: getOriginShareColor(key),
    data: data.map((item) => +item[key].toFixed(2)),
    name: t(ORIGIN_LABEL_KEYS[key]),
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

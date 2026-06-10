import type { ECOption } from '@vben/plugins/echarts';

import type {
  AnalysisPeriodRecord,
  NevBreakdownRecord,
  NevShareTrendRecord,
} from '#/api/sales/analysis';
import type { LineTooltipParams } from '#/utils/chart';

import { buildLineChartOption, getEmptyChartOption } from '#/utils/chart';
import { toMonthKey } from '#/utils/period';

type Translate = (key: string) => string;

export type NevTrendValueKey = 'bev_ratio' | 'nev_penetration_rate';

export interface NevTrendChartInput {
  color: string;
  data: AnalysisPeriodRecord[];
  label: string;
  valueKey: NevTrendValueKey;
}

function getRecordValue(
  item: AnalysisPeriodRecord,
  valueKey: NevTrendValueKey,
): number {
  if (valueKey === 'nev_penetration_rate') {
    return (item as NevShareTrendRecord).nev_penetration_rate;
  }
  return (item as NevBreakdownRecord).bev_ratio;
}

export function buildNevTrendChartOption(
  input: NevTrendChartInput,
  t: Translate,
): ECOption {
  const { color, data, label, valueKey } = input;

  if (!data || data.length === 0) {
    return getEmptyChartOption(t('sales.common.noData'));
  }

  const timeLabels = data.map((item) => toMonthKey(item.year, item.month));
  const values = data.map((item) => +getRecordValue(item, valueKey).toFixed(2));

  const tooltipFormatter = (
    params: LineTooltipParams | LineTooltipParams[],
  ) => {
    const p = Array.isArray(params) ? params[0] : params;
    return `${p?.axisValue}<br/>${label}: ${p?.value}%`;
  };

  return buildLineChartOption({
    percentMaxCap: 100,
    series: [
      {
        areaStyle: { opacity: 0.15 },
        color,
        data: values,
        name: label,
      },
    ],
    tooltipFormatter,
    xData: timeLabels,
    yAxisType: 'percent',
  });
}

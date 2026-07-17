import type { ECOption } from '@vben/plugins/echarts';

import type { NevBreakdownRecord, NevShareTrendRecord } from '#/api/analysis';
import type { LineTooltipParams } from '#/utils/chart';
import type { Translate } from '#/utils/types';

import { buildLineChartOption, emptyChartIfNoData } from '#/utils/chart';
import { toMonthKey } from '#/utils/period';

export type NevTrendChartInput =
  | {
      color: string;
      data: NevBreakdownRecord[];
      label: string;
      valueKey: 'bev_ratio';
    }
  | {
      color: string;
      data: NevShareTrendRecord[];
      label: string;
      valueKey: 'nev_penetration_rate';
    };

export function buildNevTrendChartOption(
  input: NevTrendChartInput,
  t: Translate,
): ECOption {
  const { color, data, label, valueKey } = input;

  const empty = emptyChartIfNoData(data ?? [], t('pages.common.noData'));
  if (empty) return empty;

  const timeLabels = data.map((item) => toMonthKey(item.year, item.month));
  const values =
    valueKey === 'nev_penetration_rate'
      ? data.map((item) => +item.nev_penetration_rate.toFixed(2))
      : data.map((item) => +item.bev_ratio.toFixed(2));

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
        areaStyle: { opacity: 0.1 },
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

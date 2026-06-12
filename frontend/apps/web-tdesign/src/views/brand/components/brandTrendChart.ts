import type { ECOption } from '@vben/plugins/echarts';

import type { BrandSeriesRecord } from '../types';

import type { Translate } from '#/utils/types';

import {
  buildLineChartOption,
  emptyChartIfNoData,
  getEmptyChartOption,
} from '#/utils/chart';
import {
  BRAND_LINE_PALETTE_INDICES,
  getChartPaletteColor,
} from '#/utils/style';

export interface BrandTrendChartInput {
  data: BrandSeriesRecord[];
  timeLabels: string[];
}

export function buildBrandTrendChartOption(
  input: BrandTrendChartInput,
  locale: string,
  t: Translate,
): ECOption {
  const { data, timeLabels } = input;

  if (timeLabels.length === 0) {
    return getEmptyChartOption(t('pages.brand.trend.noData'));
  }
  const empty = emptyChartIfNoData(data, t('pages.brand.trend.noData'));
  if (empty) return empty;

  const series = data.map((brand, index) => {
    const map = new Map<string, number>();
    for (const point of brand.points ?? []) {
      map.set(point.time, point.sales ?? 0);
    }
    const paletteIndex =
      BRAND_LINE_PALETTE_INDICES[index % BRAND_LINE_PALETTE_INDICES.length] ??
      0;
    return {
      color: getChartPaletteColor(paletteIndex),
      data: timeLabels.map((time) => map.get(time) ?? 0),
      name: brand.brand_name,
    };
  });

  return buildLineChartOption({
    grid: {
      bottom: '14%',
      containLabel: true,
      left: '3%',
      right: '4%',
      top: '8%',
    },
    legend: { bottom: 0, data: data.map((item) => item.brand_name) },
    locale,
    series,
    xData: timeLabels,
  });
}

import type { ECOption } from '@vben/plugins/echarts';

import type { BrandSeriesRecord } from '../types';

import {
  BRAND_LINE_PALETTE_INDICES,
  buildLineChartOption,
  getChartPaletteColor,
  getEmptyChartOption,
} from '#/utils/chart';

type Translate = (key: string) => string;

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

  if (data.length === 0 || timeLabels.length === 0) {
    return getEmptyChartOption(t('pages.brand.trend.noData'));
  }

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

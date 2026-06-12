import type { ECOption } from '@vben/plugins/echarts';

import type {
  MonthlyTrendRecord,
  QuarterlyTrendRecord,
  YearlyTrendRecord,
} from '../useMarketData';

import {
  buildLineChartOption,
  getChartPaletteColor,
  getEmptyChartOption,
} from '#/utils/chart';
import {
  formatQuarterPeriod,
  formatYearPeriod,
  getLocalizedMonthLabels,
} from '#/utils/period';

export type MarketTrendChartInput =
  | { data: MonthlyTrendRecord[]; kind: 'monthly' }
  | { data: QuarterlyTrendRecord[]; kind: 'quarterly' }
  | { data: YearlyTrendRecord[]; kind: 'yearly' };

type Translate = (key: string) => string;

function buildMonthlyOption(
  data: MonthlyTrendRecord[],
  locale: string,
  t: Translate,
): ECOption {
  if (data.length === 0) return getEmptyChartOption(t('pages.common.noData'));

  const yearDataMap = new Map<number, number[]>();
  for (const item of data) {
    if (!yearDataMap.has(item.year)) {
      yearDataMap.set(item.year, Array.from<number>({ length: 12 }).fill(0));
    }
    const yearArr = yearDataMap.get(item.year);
    if (yearArr) yearArr[item.month - 1] = item.sales;
  }
  const years = [...yearDataMap.keys()].toSorted((a, b) => a - b);

  return buildLineChartOption({
    locale,
    grid: {
      bottom: '12%',
      containLabel: true,
      left: '3%',
      right: '4%',
      top: '8%',
    },
    legend: { bottom: 0, data: years.map(String) },
    series: years.map((year, i) => ({
      color: getChartPaletteColor(i),
      data: yearDataMap.get(year) ?? [],
      name: String(year),
    })),
    xData: getLocalizedMonthLabels(locale),
  });
}

function buildQuarterlyOption(
  data: QuarterlyTrendRecord[],
  locale: string,
  t: Translate,
): ECOption {
  if (data.length === 0) return getEmptyChartOption(t('pages.common.noData'));
  return buildLineChartOption({
    locale,
    series: [
      {
        color: getChartPaletteColor(0),
        data: data.map((r) => r.sales),
        name: t('pages.market.quarterly.sales'),
      },
    ],
    xAxisExtra: { interval: 0, rotate: data.length > 8 ? 30 : 0 },
    xData: data.map((r) => formatQuarterPeriod(r.year, r.quarter, locale)),
  });
}

function buildYearlyOption(
  data: YearlyTrendRecord[],
  locale: string,
  t: Translate,
): ECOption {
  if (data.length === 0) return getEmptyChartOption(t('pages.common.noData'));
  return buildLineChartOption({
    locale,
    series: [
      {
        color: getChartPaletteColor(0),
        data: data.map((r) => r.sales),
        name: t('pages.market.yearly.sales'),
      },
    ],
    xData: data.map((r) => formatYearPeriod(r.year, locale)),
  });
}

/** 市场页「月度 / 季度 / 年度」趋势折线图共用配置构建 */
export function buildMarketTrendChartOption(
  input: MarketTrendChartInput,
  locale: string,
  t: Translate,
): ECOption {
  if (input.kind === 'monthly') {
    return buildMonthlyOption(input.data, locale, t);
  }
  if (input.kind === 'quarterly') {
    return buildQuarterlyOption(input.data, locale, t);
  }
  return buildYearlyOption(input.data, locale, t);
}

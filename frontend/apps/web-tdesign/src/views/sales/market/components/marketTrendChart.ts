import type {
  MonthlyTrendRecord,
  QuarterlyTrendRecord,
  YearlyTrendRecord,
} from '../useMarketData';

import {
  formatSalesAxisLabel,
  getEmptyChartOption,
  lineSeriesTooltipFormatter,
} from '#/views/sales/utils/chart-utils';
import {
  formatQuarterPeriod,
  formatYearPeriod,
  getLocalizedMonthLabels,
} from '#/views/sales/utils/period-utils';

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'];

export type MarketTrendChartInput =
  | { data: MonthlyTrendRecord[]; kind: 'monthly' }
  | { data: QuarterlyTrendRecord[]; kind: 'quarterly' }
  | { data: YearlyTrendRecord[]; kind: 'yearly' };

type Translate = (key: string) => string;

function buildYAxis(locale: string) {
  return {
    type: 'value' as const,
    axisLabel: { formatter: (val: number) => formatSalesAxisLabel(val, locale) },
  };
}

function buildMonthlyOption(data: MonthlyTrendRecord[], locale: string, t: Translate) {
  if (data.length === 0) return getEmptyChartOption(t('sales.common.noData'));

  const yearDataMap = new Map<number, number[]>();
  for (const item of data) {
    if (!yearDataMap.has(item.year)) {
      yearDataMap.set(item.year, Array.from<number>({ length: 12 }).fill(0));
    }
    yearDataMap.get(item.year)![item.month - 1] = item.sales;
  }
  const years = [...yearDataMap.keys()].toSorted((a, b) => a - b);

  return {
    animation: false,
    tooltip: { trigger: 'axis' as const, axisPointer: { type: 'shadow' as const } },
    legend: { data: years.map(String), bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: { type: 'category' as const, data: getLocalizedMonthLabels(locale), boundaryGap: false },
    yAxis: buildYAxis(locale),
    series: years.map((year, i) => ({
      name: String(year),
      type: 'line' as const,
      data: yearDataMap.get(year),
      smooth: true,
      itemStyle: { color: COLORS[i % COLORS.length] },
    })),
  };
}

function buildLineTrendOption(
  xData: string[],
  seriesName: string,
  seriesData: number[],
  locale: string,
  xAxisExtra?: { interval: number; rotate: number },
) {
  return {
    animation: false,
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: { type: 'line' as const },
      formatter: lineSeriesTooltipFormatter,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category' as const,
      boundaryGap: false,
      data: xData,
      ...(xAxisExtra && { axisLabel: xAxisExtra }),
    },
    yAxis: buildYAxis(locale),
    series: [
      {
        name: seriesName,
        type: 'line' as const,
        smooth: true,
        data: seriesData,
        itemStyle: { color: '#5470c6' },
      },
    ],
  };
}

function buildQuarterlyOption(data: QuarterlyTrendRecord[], locale: string, t: Translate) {
  if (data.length === 0) return getEmptyChartOption(t('sales.common.noData'));
  return buildLineTrendOption(
    data.map((r) => formatQuarterPeriod(r.year, r.quarter, locale)),
    t('sales.market.quarterly.sales'),
    data.map((r) => r.sales),
    locale,
    { interval: 0, rotate: data.length > 8 ? 30 : 0 },
  );
}

function buildYearlyOption(data: YearlyTrendRecord[], locale: string, t: Translate) {
  if (data.length === 0) return getEmptyChartOption(t('sales.common.noData'));
  return buildLineTrendOption(
    data.map((r) => formatYearPeriod(r.year, locale)),
    t('sales.market.yearly.sales'),
    data.map((r) => r.sales),
    locale,
  );
}

/** 市场页「月度 / 季度 / 年度」趋势折线图共用配置构建 */
export function buildMarketTrendChartOption(input: MarketTrendChartInput, locale: string, t: Translate) {
  switch (input.kind) {
    case 'monthly': {
      return buildMonthlyOption(input.data, locale, t);
    }
    case 'quarterly': {
      return buildQuarterlyOption(input.data, locale, t);
    }
    case 'yearly': {
      return buildYearlyOption(input.data, locale, t);
    }
  }
}

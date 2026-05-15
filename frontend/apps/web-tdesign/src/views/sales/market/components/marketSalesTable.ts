import type { MonthlyDetailRecord, QuarterlyTrendRecord, YearlyTrendRecord } from '../useMarketData';

import { h } from 'vue';

import { growthColor, growthPercentText } from '#/views/sales/utils/growth-utils';
import {
  formatMonthPeriod,
  formatQuarterPeriod,
  formatYearPeriod,
} from '#/views/sales/utils/period-utils';
import {
  sortByNumberAsc,
  toYearMonthSortKey,
  toYearQuarterSortKey,
} from '#/views/sales/utils/sort-utils';

export type MarketSalesTableInput =
  | { data: MonthlyDetailRecord[]; kind: 'monthly' }
  | { data: QuarterlyTrendRecord[]; kind: 'quarterly' }
  | { data: YearlyTrendRecord[]; kind: 'yearly' };

type Translate = (key: string) => string;

const PERIOD_WIDTHS = { monthly: 120, quarterly: 130, yearly: 110 } as const;

function growthCell(key: string) {
  return (_: unknown, { row }: { row: Record<string, string> }) =>
    h('span', { style: { color: row[`${key}Color`], fontWeight: 500 } }, row[`${key}Text`]);
}

function growthFields(key: string, value: null | number | undefined) {
  return { [`${key}Color`]: growthColor(value), [`${key}Text`]: growthPercentText(value) };
}

export function buildMarketSalesTableColumns(kind: MarketSalesTableInput['kind'], t: Translate) {
  const sorter =
    kind === 'monthly'
      ? (a: unknown, b: unknown) => {
          const ra = a as MonthlyDetailRecord;
          const rb = b as MonthlyDetailRecord;
          return toYearMonthSortKey(ra.year, ra.monthNum) - toYearMonthSortKey(rb.year, rb.monthNum);
        }
      : (kind === 'quarterly'
        ? (a: unknown, b: unknown) => {
            const ra = a as QuarterlyTrendRecord;
            const rb = b as QuarterlyTrendRecord;
            return toYearQuarterSortKey(ra.year, ra.quarter) - toYearQuarterSortKey(rb.year, rb.quarter);
          }
        : (a: unknown, b: unknown) =>
            sortByNumberAsc((a as YearlyTrendRecord).year, (b as YearlyTrendRecord).year));

  const base = [
    { colKey: 'periodText', sorter, title: t('sales.market.timePeriod'), width: PERIOD_WIDTHS[kind] },
    { colKey: 'salesText', title: t(`sales.market.${kind}.sales`), width: 150 },
    { cell: growthCell('yoyGrowth'), colKey: 'yoyGrowth', title: t(`sales.market.${kind}.yoyGrowth`), width: 140 },
  ];

  if (kind === 'monthly') {
    return [...base, { cell: growthCell('momGrowth'), colKey: 'momGrowth', title: t('sales.market.monthly.momGrowth'), width: 130 }];
  }
  if (kind === 'quarterly') {
    return [...base, { cell: growthCell('qoqGrowth'), colKey: 'qoqGrowth', title: t('sales.market.quarterly.qoqGrowth'), width: 140 }];
  }
  return base;
}

export function buildMarketSalesTableRows(input: MarketSalesTableInput, locale: string) {
  const { data, kind } = input;

  if (kind === 'monthly') {
    return data.map((r) => ({
      ...r,
      ...growthFields('momGrowth', r.momGrowth),
      ...growthFields('yoyGrowth', r.yoyGrowth),
      periodText: formatMonthPeriod(r.year, r.monthNum, locale),
      salesText: r.sales == null ? '-' : r.sales.toLocaleString(),
    }));
  }

  const rows =
    kind === 'quarterly'
      ? data.map((r) => ({
          ...r,
          ...growthFields('qoqGrowth', r.qoqGrowth),
          ...growthFields('yoyGrowth', r.yoyGrowth),
          periodText: formatQuarterPeriod(r.year, r.quarter, locale),
          salesText: Math.round(r.sales).toLocaleString(),
        }))
      : data.map((r) => ({
          ...r,
          ...growthFields('yoyGrowth', r.yoyGrowth),
          periodText: formatYearPeriod(r.year, locale),
          salesText: r.sales == null ? '-' : Math.round(r.sales).toLocaleString(),
        }));

  return rows.toReversed();
}

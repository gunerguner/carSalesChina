import type { MonthlyDetailRecord, QuarterlyTrendRecord, YearlyTrendRecord } from '../useMarketData';

import {
  growthTableCell,
  growthTableRowFields,
} from '#/utils/format';
import {
  formatMonthPeriod,
  formatQuarterPeriod,
  formatYearPeriod,
  sortByNumberAsc,
  toYearMonthSortKey,
  toYearQuarterSortKey,
} from '#/utils/period';

export type MarketSalesTableInput =
  | { data: MonthlyDetailRecord[]; kind: 'monthly' }
  | { data: QuarterlyTrendRecord[]; kind: 'quarterly' }
  | { data: YearlyTrendRecord[]; kind: 'yearly' };

type Translate = (key: string) => string;

const PERIOD_WIDTHS = { monthly: 120, quarterly: 130, yearly: 110 } as const;

type DataType = 'production' | 'retail';

function salesColumnTitle(dataType: DataType, t: Translate) {
  return dataType === 'production'
    ? t('sales.market.column.productionSales')
    : t('sales.market.column.retailSales');
}

export function buildMarketSalesTableColumns(
  kind: MarketSalesTableInput['kind'],
  dataType: DataType,
  t: Translate,
) {
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
    { colKey: 'salesText', title: salesColumnTitle(dataType, t), width: 150 },
    { cell: growthTableCell('yoyGrowth'), colKey: 'yoyGrowth', title: t(`sales.market.${kind}.yoyGrowth`), width: 140 },
  ];

  if (kind === 'monthly') {
    return [...base, { cell: growthTableCell('momGrowth'), colKey: 'momGrowth', title: t('sales.market.monthly.momGrowth'), width: 130 }];
  }
  if (kind === 'quarterly') {
    return [...base, { cell: growthTableCell('qoqGrowth'), colKey: 'qoqGrowth', title: t('sales.market.quarterly.qoqGrowth'), width: 140 }];
  }
  return base;
}

export function buildMarketSalesTableRows(input: MarketSalesTableInput, locale: string) {
  const { data, kind } = input;

  if (kind === 'monthly') {
    return data.map((r) => ({
      ...r,
      ...growthTableRowFields('momGrowth', r.momGrowth),
      ...growthTableRowFields('yoyGrowth', r.yoyGrowth),
      periodText: formatMonthPeriod(r.year, r.monthNum, locale),
      salesText: r.sales == null ? '-' : r.sales.toLocaleString(),
    }));
  }

  const rows =
    kind === 'quarterly'
      ? data.map((r) => ({
          ...r,
          ...growthTableRowFields('qoqGrowth', r.qoqGrowth),
          ...growthTableRowFields('yoyGrowth', r.yoyGrowth),
          periodText: formatQuarterPeriod(r.year, r.quarter, locale),
          salesText: Math.round(r.sales).toLocaleString(),
        }))
      : data.map((r) => ({
          ...r,
          ...growthTableRowFields('yoyGrowth', r.yoyGrowth),
          periodText: formatYearPeriod(r.year, locale),
          salesText: r.sales == null ? '-' : Math.round(r.sales).toLocaleString(),
        }));

  return rows.toReversed();
}

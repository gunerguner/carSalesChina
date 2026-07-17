import type { PrimaryTableCol, TableRowData } from 'tdesign-vue-next';

import type { MarketPeriodInput } from '../types';
import type {
  MonthlyDetailRecord,
  QuarterlyTrendRecord,
  YearlyTrendRecord,
} from '../useMarketData';

import type { DataType, Translate } from '#/utils/types';

import {
  formatMonthPeriod,
  formatQuarterPeriod,
  formatYearPeriod,
  toYearMonthSortKey,
  toYearQuarterSortKey,
} from '#/utils/period';
import { growthTableCell } from '#/utils/render';
import { growthTableRowFields } from '#/utils/style';

export type MarketTableInput = MarketPeriodInput<{
  monthly: MonthlyDetailRecord;
  quarterly: QuarterlyTrendRecord;
  yearly: YearlyTrendRecord;
}>;

const PERIOD_WIDTHS = { monthly: 120, quarterly: 130, yearly: 110 } as const;

type TableSorter = NonNullable<PrimaryTableCol['sorter']>;

function asTableSorter<T extends TableRowData>(
  fn: (a: T, b: T) => number,
): TableSorter {
  return fn as TableSorter;
}

function monthlySorter(a: MonthlyDetailRecord, b: MonthlyDetailRecord): number {
  return (
    toYearMonthSortKey(a.year, a.monthNum) -
    toYearMonthSortKey(b.year, b.monthNum)
  );
}

function quarterlySorter(
  a: QuarterlyTrendRecord,
  b: QuarterlyTrendRecord,
): number {
  return (
    toYearQuarterSortKey(a.year, a.quarter) -
    toYearQuarterSortKey(b.year, b.quarter)
  );
}

function yearlySorter(a: YearlyTrendRecord, b: YearlyTrendRecord): number {
  return a.year - b.year;
}

export function buildMarketTableColumns(
  kind: MarketTableInput['kind'],
  dataType: DataType,
  t: Translate,
) {
  let sorter: TableSorter = asTableSorter(yearlySorter);
  if (kind === 'monthly') sorter = asTableSorter(monthlySorter);
  else if (kind === 'quarterly') sorter = asTableSorter(quarterlySorter);

  const salesTitle =
    dataType === 'production'
      ? t('pages.market.column.productionSales')
      : t('pages.market.column.retailSales');

  const base = [
    {
      colKey: 'periodText',
      sorter,
      title: t('pages.market.timePeriod'),
      width: PERIOD_WIDTHS[kind],
    },
    { colKey: 'salesText', title: salesTitle, width: 150 },
    {
      cell: growthTableCell('yoyGrowth'),
      colKey: 'yoyGrowth',
      title: t(`pages.market.${kind}.yoyGrowth`),
      width: 140,
    },
  ];

  if (kind === 'monthly') {
    return [
      ...base,
      {
        cell: growthTableCell('momGrowth'),
        colKey: 'momGrowth',
        title: t('pages.market.monthly.momGrowth'),
        width: 130,
      },
    ];
  }
  if (kind === 'quarterly') {
    return [
      ...base,
      {
        cell: growthTableCell('qoqGrowth'),
        colKey: 'qoqGrowth',
        title: t('pages.market.quarterly.qoqGrowth'),
        width: 140,
      },
    ];
  }
  return base;
}

export function buildMarketTableRows(input: MarketTableInput, locale: string) {
  const { data, kind } = input;

  if (kind === 'monthly') {
    return data.map((r) => ({
      ...r,
      ...growthTableRowFields('momGrowth', r.momGrowth),
      ...growthTableRowFields('yoyGrowth', r.yoyGrowth),
      periodText: formatMonthPeriod(r.year, r.monthNum, locale),
      salesText: r.sales.toLocaleString(),
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
          salesText: Math.round(r.sales).toLocaleString(),
        }));

  return rows.toReversed();
}

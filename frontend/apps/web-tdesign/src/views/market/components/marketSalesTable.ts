import type { TableRowData } from 'tdesign-vue-next';

import type {
  MonthlyDetailRecord,
  QuarterlyTrendRecord,
  YearlyTrendRecord,
} from '../useMarketData';

import type { DataType } from '#/types/domain';

import { growthTableRowFields } from '#/utils/format';
import {
  formatMonthPeriod,
  formatQuarterPeriod,
  formatYearPeriod,
  toYearMonthSortKey,
  toYearQuarterSortKey,
} from '#/utils/period';
import { growthTableCell } from '#/utils/render';

export type MarketTableInput =
  | { data: MonthlyDetailRecord[]; kind: 'monthly' }
  | { data: QuarterlyTrendRecord[]; kind: 'quarterly' }
  | { data: YearlyTrendRecord[]; kind: 'yearly' };

type Translate = (key: string) => string;

const PERIOD_WIDTHS = { monthly: 120, quarterly: 130, yearly: 110 } as const;

function monthlySorter(a: TableRowData, b: TableRowData): number {
  const ra = a as MonthlyDetailRecord;
  const rb = b as MonthlyDetailRecord;
  return (
    toYearMonthSortKey(ra.year, ra.monthNum) -
    toYearMonthSortKey(rb.year, rb.monthNum)
  );
}

function quarterlySorter(a: TableRowData, b: TableRowData): number {
  const ra = a as QuarterlyTrendRecord;
  const rb = b as QuarterlyTrendRecord;
  return (
    toYearQuarterSortKey(ra.year, ra.quarter) -
    toYearQuarterSortKey(rb.year, rb.quarter)
  );
}

function yearlySorter(a: TableRowData, b: TableRowData): number {
  const ra = a as YearlyTrendRecord;
  const rb = b as YearlyTrendRecord;
  return ra.year - rb.year;
}

export function buildMarketTableColumns(
  kind: MarketTableInput['kind'],
  dataType: DataType,
  t: Translate,
) {
  let sorter = yearlySorter;
  if (kind === 'monthly') sorter = monthlySorter;
  else if (kind === 'quarterly') sorter = quarterlySorter;

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

export function buildMarketTableRows(
  input: MarketTableInput,
  locale: string,
) {
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

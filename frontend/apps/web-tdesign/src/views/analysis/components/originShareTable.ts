import type { PrimaryTableCol, TableRowData } from 'tdesign-vue-next';

import type { OriginShareTrendRecord } from '#/api/analysis';

import { formatOrDash } from '#/utils/format';
import { toMonthKey, toYearMonthSortKey } from '#/utils/period';

import {
  ORIGIN_DIMENSIONS,
  type OriginShareKey,
} from '../originShareDimensions';

type Translate = (key: string) => string;

export type OriginShareRow = Record<OriginShareKey, number> & {
  key: number;
  sortKey: number;
  time: string;
};

function percentCell(key: OriginShareKey) {
  return (_: unknown, { row }: { row: TableRowData }) =>
    formatOrDash((row as OriginShareRow)[key], '%');
}

export function buildOriginShareTableColumns(t: Translate): PrimaryTableCol[] {
  return [
    { colKey: 'time', title: t('pages.analysis.origin.time'), width: 120 },
    ...ORIGIN_DIMENSIONS.map(({ key, tableLabelKey }) => ({
      colKey: key,
      title: t(tableLabelKey),
      width: 100,
      cell: percentCell(key),
    })),
  ];
}

export function buildOriginShareTableRows(
  data: OriginShareTrendRecord[],
): OriginShareRow[] {
  return data
    .map((item, index) => ({
      key: index,
      time: toMonthKey(item.year, item.month),
      sortKey: toYearMonthSortKey(item.year, item.month),
      ...Object.fromEntries(
        ORIGIN_DIMENSIONS.map(({ key }) => [key, item[key]]),
      ),
    }))
    .toSorted((a, b) => b.sortKey - a.sortKey) as OriginShareRow[];
}

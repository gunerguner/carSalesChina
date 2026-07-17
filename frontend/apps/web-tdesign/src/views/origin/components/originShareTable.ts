import type { PrimaryTableCol } from 'tdesign-vue-next';

import type { OriginShareTrendRecord } from '#/api/analysis';
import type { OriginShareKey, Translate } from '#/utils/types';

import { toMonthKey, toYearMonthSortKey } from '#/utils/period';
import { tablePercentCell } from '#/utils/render';
import { ORIGIN_DIMENSIONS } from '#/utils/types';

export type OriginShareRow = Record<OriginShareKey, number> & {
  key: number;
  sortKey: number;
  time: string;
};

export function buildOriginShareTableColumns(t: Translate): PrimaryTableCol[] {
  return [
    { colKey: 'time', title: t('pages.analysis.origin.time'), width: 120 },
    ...ORIGIN_DIMENSIONS.map(({ key, tableLabelKey }) => ({
      colKey: key,
      title: t(tableLabelKey),
      width: 100,
      cell: tablePercentCell(key),
    })),
  ];
}

function toOriginShareRow(
  item: OriginShareTrendRecord,
  index: number,
): OriginShareRow {
  return {
    key: index,
    time: toMonthKey(item.year, item.month),
    sortKey: toYearMonthSortKey(item.year, item.month),
    domestic: item.domestic,
    german: item.german,
    japanese: item.japanese,
    american: item.american,
    european: item.european,
    korean: item.korean,
    french: item.french,
  };
}

export function buildOriginShareTableRows(
  data: OriginShareTrendRecord[],
): OriginShareRow[] {
  return data
    .map((item, index) => toOriginShareRow(item, index))
    .toSorted((a, b) => b.sortKey - a.sortKey);
}

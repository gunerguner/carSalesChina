import type { PrimaryTableCol } from 'tdesign-vue-next';

import type {
  NevBreakdownRecord,
  NevShareTrendRecord,
} from '#/api/analysis';
import type { Translate } from '#/utils/types';

import { toMonthKey } from '#/utils/period';
import { tableNumberCell, tablePercentCell } from '#/utils/render';

export interface NevPenetrationRow {
  bevRatio: number;
  bevSales: number;
  key: number;
  nevSales: number;
  penetrationRate: number;
  time: string;
  totalSales: number;
}

export function buildNevPenetrationTableColumns(
  t: Translate,
): PrimaryTableCol[] {
  return [
    { colKey: 'time', title: t('pages.analysis.nev.time'), width: 120 },
    {
      colKey: 'totalSales',
      title: t('pages.analysis.nev.totalSales'),
      width: 130,
      cell: tableNumberCell('totalSales'),
    },
    {
      colKey: 'nevSales',
      title: t('pages.analysis.nev.nevSales'),
      width: 130,
      cell: tableNumberCell('nevSales'),
    },
    {
      colKey: 'penetrationRate',
      title: t('pages.analysis.nev.penetrationRate'),
      width: 140,
      cell: tablePercentCell('penetrationRate'),
    },
    {
      colKey: 'bevSales',
      title: t('pages.analysis.nev.bevSales'),
      width: 130,
      cell: tableNumberCell('bevSales'),
    },
    {
      colKey: 'bevRatio',
      title: t('pages.analysis.nev.bevRatioInNev'),
      width: 170,
      cell: tablePercentCell('bevRatio'),
    },
  ];
}

export function buildNevPenetrationTableRows(
  shareTrend: NevShareTrendRecord[],
  breakdownTrend: NevBreakdownRecord[],
): NevPenetrationRow[] {
  const bevMap = new Map<string, { bevRatio: number; bevSales: number }>();
  for (const item of breakdownTrend) {
    const key = toMonthKey(item.year, item.month);
    bevMap.set(key, {
      bevSales: item.bev_sales,
      bevRatio: item.bev_ratio,
    });
  }

  return shareTrend
    .map((item, index) => {
      const key = toMonthKey(item.year, item.month);
      const bevInfo = bevMap.get(key);
      return {
        key: index,
        time: key,
        totalSales: item.total_sales,
        nevSales: item.nev_sales,
        penetrationRate: item.nev_penetration_rate,
        bevSales: bevInfo?.bevSales ?? 0,
        bevRatio: bevInfo?.bevRatio ?? 0,
      };
    })
    .toReversed();
}

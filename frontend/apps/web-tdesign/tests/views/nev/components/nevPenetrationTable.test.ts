import type { NevBreakdownRecord, NevShareTrendRecord } from '#/api/analysis';

import { itemAt } from '#tests/testUtils';
import { describe, expect, it } from 'vitest';

import {
  buildNevPenetrationTableColumns,
  buildNevPenetrationTableRows,
} from '#/views/nev/components/nevPenetrationTable';

const t = (key: string) => key;

const shareTrend: NevShareTrendRecord[] = [
  {
    year: 2024,
    month: 1,
    total_sales: 200,
    nev_sales: 60,
    nev_penetration_rate: 30,
  },
  {
    year: 2024,
    month: 2,
    total_sales: 300,
    nev_sales: 120,
    nev_penetration_rate: 40,
  },
];

const breakdown: NevBreakdownRecord[] = [
  { year: 2024, month: 1, bev_sales: 20, bev_ratio: 33.3333 },
];

describe('buildNevPenetrationTableColumns', () => {
  it('6 列且标题来自 i18n 键', () => {
    const cols = buildNevPenetrationTableColumns(t) as { colKey: string }[];
    expect(cols.map((c) => c.colKey)).toEqual([
      'time',
      'totalSales',
      'nevSales',
      'penetrationRate',
      'bevSales',
      'bevRatio',
    ]);
  });
});

describe('buildNevPenetrationTableRows', () => {
  it('按月份 merge breakdown，缺失补 0，倒序输出', () => {
    const rows = buildNevPenetrationTableRows(shareTrend, breakdown);
    expect(rows.map((r) => r.time)).toEqual(['2024-02', '2024-01']);
    const feb = itemAt(rows, 0);
    const jan = itemAt(rows, 1);
    expect(feb).toMatchObject({
      key: 1,
      totalSales: 300,
      nevSales: 120,
      penetrationRate: 40,
      bevSales: 0, // 2 月无 breakdown → 0
      bevRatio: 0,
    });
    expect(jan).toMatchObject({
      key: 0,
      totalSales: 200,
      nevSales: 60,
      penetrationRate: 30,
      bevSales: 20,
      bevRatio: 33.3333,
    });
  });

  it('空输入返回空数组', () => {
    expect(buildNevPenetrationTableRows([], [])).toEqual([]);
  });
});

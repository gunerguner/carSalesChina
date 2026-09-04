import type { NevBreakdownRecord, NevShareTrendRecord } from '#/api/analysis';

import { describe, expect, it } from 'vitest';

import { itemAt } from '#tests/testUtils';

import {
  buildNevPenetrationTableColumns,
  buildNevPenetrationTableRows,
} from '#/views/nev/components/nevPenetrationTable';
import { buildNevTrendChartOption } from '#/views/nev/components/nevTrendChart';

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

describe('buildNevTrendChartOption', () => {
  it('渗透率分支：% 轴 + 四舍五入两位 + 月份标签', () => {
    const option = buildNevTrendChartOption(
      {
        color: '#111111',
        data: shareTrend,
        label: '渗透率',
        valueKey: 'nev_penetration_rate',
      },
      t,
    );
    const yAxis = option.yAxis as { max: number; type: string };
    expect(yAxis.type).toBe('value');
    expect(yAxis.max).toBe(100);
    const series = option.series as { data: number[]; name: string }[];
    expect(itemAt(series, 0).data).toEqual([30, 40]);
    expect(itemAt(series, 0).name).toBe('渗透率');
    expect((option.xAxis as { data: string[] }).data).toEqual([
      '2024-01',
      '2024-02',
    ]);
  });

  it('纯电占比分支：取 bev_ratio', () => {
    const option = buildNevTrendChartOption(
      {
        color: '#111111',
        data: breakdown,
        label: '纯电占比',
        valueKey: 'bev_ratio',
      },
      t,
    );
    const series = option.series as { data: number[] }[];
    expect(itemAt(series, 0).data).toEqual([33.33]);
  });

  it('tooltip 输出「label: value%」格式', () => {
    const option = buildNevTrendChartOption(
      {
        color: '#111111',
        data: shareTrend,
        label: '渗透率',
        valueKey: 'nev_penetration_rate',
      },
      t,
    );
    const formatter = (
      option.tooltip as unknown as { formatter: (params: unknown) => string }
    ).formatter;
    const html = formatter([{ axisValue: '2024-01', value: 30 }]);
    expect(html).toBe('2024-01<br/>渗透率: 30%');
  });

  it('空数据 → 空图提示', () => {
    const option = buildNevTrendChartOption(
      {
        color: '#111111',
        data: [],
        label: '渗透率',
        valueKey: 'nev_penetration_rate',
      },
      t,
    );
    expect((option.title as { text: string }).text).toBe('pages.common.noData');
  });
});

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
    const [feb, jan] = rows;
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

import type {
  MonthlyDetailRecord,
  YearlyTrendRecord,
} from '#/views/market/useMarketData';

import { describe, expect, it } from 'vitest';

import { itemAt } from '#tests/testUtils';

import {
  buildMarketTableColumns,
  buildMarketTableRows,
} from '#/views/market/components/marketSalesTable';

const t = (key: string) => key;

const monthlyData: MonthlyDetailRecord[] = [
  {
    key: '2024-2-1',
    month: 2,
    monthNum: 2,
    momGrowth: null,
    sales: 400,
    year: 2024,
    yoyGrowth: 10,
  },
  {
    key: '2024-1-0',
    month: 1,
    monthNum: 1,
    momGrowth: 50,
    sales: 300,
    year: 2024,
    yoyGrowth: -5,
  },
];

const yearlyData: YearlyTrendRecord[] = [
  { key: '2022-0', sales: 780, year: 2022, yoyGrowth: null },
  { key: '2023-1', sales: 900, year: 2023, yoyGrowth: 15.38 },
];

describe('buildMarketTableColumns', () => {
  it('monthly 含 MoM 列，标题取自 i18n 键', () => {
    const cols = buildMarketTableColumns('monthly', 'retail', t) as {
      colKey: string;
      sorter?: unknown;
      title: string;
      width: number;
    }[];
    expect(cols.map((c) => c.colKey)).toEqual([
      'periodText',
      'salesText',
      'yoyGrowth',
      'momGrowth',
    ]);
    expect(itemAt(cols, 2).title).toBe('pages.market.monthly.yoyGrowth');
    expect(itemAt(cols, 3).title).toBe('pages.market.monthly.momGrowth');
    expect(itemAt(cols, 0).width).toBe(120);
    expect(typeof itemAt(cols, 0).sorter).toBe('function');
  });

  it('quarterly/yearly 列型正确', () => {
    const quarterly = buildMarketTableColumns('quarterly', 'retail', t) as {
      colKey: string;
    }[];
    const yearly = buildMarketTableColumns('yearly', 'retail', t) as {
      colKey: string;
    }[];
    expect(quarterly.map((c) => c.colKey)).toEqual([
      'periodText',
      'salesText',
      'yoyGrowth',
      'qoqGrowth',
    ]);
    expect(yearly.map((c) => c.colKey)).toEqual([
      'periodText',
      'salesText',
      'yoyGrowth',
    ]);
  });

  it('销量列标题随 data_type 切换', () => {
    const cols = (
      kind: 'yearly',
      dataType: 'export' | 'production' | 'retail',
    ) => buildMarketTableColumns(kind, dataType, t) as { title: string }[];
    expect(itemAt(cols('yearly', 'production'), 1).title).toBe(
      'pages.market.column.productionSales',
    );
    expect(itemAt(cols('yearly', 'export'), 1).title).toBe(
      'pages.market.column.exportSales',
    );
    expect(itemAt(cols('yearly', 'retail'), 1).title).toBe(
      'pages.market.column.retailSales',
    );
  });
});

describe('buildMarketTableRows', () => {
  it('monthly 保持入参顺序并格式化周期/销量/增长字段', () => {
    const rows = buildMarketTableRows(
      { data: monthlyData, kind: 'monthly' },
      'zh-CN',
    );
    const periodTexts = rows.map(
      (r) => (r as { periodText: string }).periodText,
    );
    expect(periodTexts).toEqual(['2024年2月', '2024年1月']);
    const first = itemAt(rows, 0) as unknown as {
      momGrowthText: string;
      salesText: string;
      yoyGrowthColor: string;
      yoyGrowthText: string;
    };
    expect(first.salesText).toBe('400');
    expect(first.yoyGrowthText).toBe('+10%'); // 正增长带 +
    expect(first.yoyGrowthColor).toBe('#ef4444');
    expect(
      (itemAt(rows, 1) as unknown as { yoyGrowthText: string }).yoyGrowthText,
    ).toBe('-5%');
    expect(first.momGrowthText).toBe('-'); // momGrowth null → 占位符
  });

  it('yearly 倒序输出（最新在前）', () => {
    const rows = buildMarketTableRows(
      { data: yearlyData, kind: 'yearly' },
      'en-US',
    );
    const years = rows.map((r) => (r as { year: number }).year);
    expect(years).toEqual([2023, 2022]); // 倒序
    const first = rows[0] as { periodText: string; salesText: string };
    expect(first.periodText).toBe('2023');
    expect(first.salesText).toBe('900');
  });
});

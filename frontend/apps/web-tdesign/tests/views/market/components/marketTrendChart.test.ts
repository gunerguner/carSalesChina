import type {
  MonthlyTrendRecord,
  QuarterlyTrendRecord,
  YearlyTrendRecord,
} from '../useMarketData';

import { describe, expect, it } from 'vitest';

import { itemAt } from '#tests/testUtils';

import { buildMarketTrendChartOption } from '#/views/market/components/marketTrendChart';

const t = (key: string) => key;

const monthlyData: MonthlyTrendRecord[] = [
  { year: 2023, month: 11, sales: 100 },
  { year: 2023, month: 12, sales: 120 },
  { year: 2024, month: 1, sales: 150 },
  { year: 2024, month: 2, sales: 90 },
];

describe('buildMarketTrendChartOption', () => {
  it('monthly：按年拆系列、缺失月补 0、最新年未到月份置 null', () => {
    const option = buildMarketTrendChartOption(
      { data: monthlyData, kind: 'monthly' },
      'zh-CN',
      t,
    );
    const xAxis = option.xAxis as { data: string[] };
    expect(xAxis.data).toHaveLength(12); // 每月标签
    const legend = option.legend as { data: string[] };
    expect(legend.data).toEqual(['2023', '2024']);
    const series = option.series as { data: (null | number)[]; name: string }[];
    expect(series.map((s) => s.name)).toEqual(['2023', '2024']);

    // 2023 全年 12 月数据（前两位 null 表示 1、2 月缺失→0）
    const s2023 = itemAt(series, 0).data;
    expect(s2023[0]).toBe(0);
    expect(s2023[10]).toBe(100);
    expect(s2023[11]).toBe(120);
    // 2024 只有 1、2 月；3 月起置 null（不画线）
    const s2024 = itemAt(series, 1).data;
    expect(s2024[0]).toBe(150);
    expect(s2024[1]).toBe(90);
    expect(s2024[2]).toBeNull();
    expect(s2024[11]).toBeNull();
  });

  it('monthly 空数据 → 空图提示', () => {
    const option = buildMarketTrendChartOption(
      { data: [], kind: 'monthly' },
      'zh-CN',
      t,
    );
    expect((option.title as { text: string }).text).toBe('pages.common.noData');
  });

  it('quarterly：单系列 + 周期标签（zh-CN 季度格式）', () => {
    const data: QuarterlyTrendRecord[] = [
      {
        key: 'q',
        quarter: 1,
        qoqGrowth: null,
        sales: 100,
        year: 2024,
        yoyGrowth: null,
      },
      {
        key: 'q',
        quarter: 2,
        qoqGrowth: 10,
        sales: 150,
        year: 2024,
        yoyGrowth: 5,
      },
    ];
    const option = buildMarketTrendChartOption(
      { data, kind: 'quarterly' },
      'zh-CN',
      t,
    );
    const series = option.series as { data: number[]; name: string }[];
    expect(itemAt(series, 0).data).toEqual([100, 150]);
    expect(itemAt(series, 0).name).toBe('pages.market.quarterly.sales');
    expect((option.xAxis as { data: string[] }).data).toEqual([
      '2024年Q1',
      '2024年Q2',
    ]);
  });

  it('yearly：英文年份标签', () => {
    const data: YearlyTrendRecord[] = [
      { key: 'y', sales: 780, year: 2022, yoyGrowth: null },
      { key: 'y', sales: 900, year: 2023, yoyGrowth: 15.38 },
    ];
    const option = buildMarketTrendChartOption(
      { data, kind: 'yearly' },
      'en-US',
      t,
    );
    const series = option.series as { data: number[] }[];
    expect(itemAt(series, 0).data).toEqual([780, 900]);
    expect((option.xAxis as { data: string[] }).data).toEqual(['2022', '2023']);
  });
});

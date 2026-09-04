import type { BrandSeriesRecord } from '#/views/brand/types';

import { describe, expect, it } from 'vitest';

import { itemAt } from '#tests/testUtils';

import { buildBrandTrendChartOption } from '#/views/brand/components/brandTrendChart';

const t = (key: string) => key;

const data: BrandSeriesRecord[] = [
  {
    brand_name: '比亚迪',
    points: [
      { time: '2024-01', sales: 100, yoyGrowth: 10 },
      { time: '2024-02', sales: 120, yoyGrowth: 20 },
    ],
  },
  {
    brand_name: '理想',
    points: [{ time: '2024-01', sales: 50, yoyGrowth: null }],
  },
];

describe('buildBrandTrendChartOption', () => {
  it('每品牌一条线，缺失时间点补 0，品牌顺序保持', () => {
    const option = buildBrandTrendChartOption(
      { data, timeLabels: ['2024-01', '2024-02', '2024-03'] },
      'zh-CN',
      t,
    );
    const series = option.series as {
      data: number[];
      itemStyle: { color: string };
      name: string;
    }[];
    expect(series.map((s) => s.name)).toEqual(['比亚迪', '理想']);
    expect(itemAt(series, 0).data).toEqual([100, 120, 0]); // 2024-03 缺失 → 0
    expect(itemAt(series, 1).data).toEqual([50, 0, 0]);

    const legend = option.legend as { data: string[] };
    expect(legend.data).toEqual(['比亚迪', '理想']);

    // 品牌调色板取间隔色
    expect(itemAt(series, 0).itemStyle.color).not.toBe(
      itemAt(series, 1).itemStyle.color,
    );
  });

  it('timeLabels 为空 → 空图（不依赖数据空判定）', () => {
    const option = buildBrandTrendChartOption(
      { data, timeLabels: [] },
      'zh-CN',
      t,
    );
    expect((option.title as { text: string }).text).toBe(
      'pages.brand.trend.noData',
    );
  });

  it('有标签但无数据 → 空图提示', () => {
    const option = buildBrandTrendChartOption(
      { data: [], timeLabels: ['2024-01'] },
      'zh-CN',
      t,
    );
    expect((option.title as { text: string }).text).toBe(
      'pages.brand.trend.noData',
    );
  });
});

import type { NevBreakdownRecord, NevShareTrendRecord } from '#/api/analysis';

import {
  expectEmptyChart,
  itemAt,
  seriesOf,
  tooltipFormatterOf,
} from '#tests/testUtils';
import { describe, expect, it } from 'vitest';

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
    const series = seriesOf<{ data: number[]; name: string }>(option);
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
    const series = seriesOf<{ data: number[] }>(option);
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
    const html = tooltipFormatterOf(option)([
      { axisValue: '2024-01', value: 30 },
    ]);
    expect(html).toBe('2024-01<br/>渗透率: 30%');
  });

  it('空数据 → 空图提示', () => {
    expectEmptyChart(
      buildNevTrendChartOption(
        {
          color: '#111111',
          data: [],
          label: '渗透率',
          valueKey: 'nev_penetration_rate',
        },
        t,
      ),
      'pages.common.noData',
    );
  });
});

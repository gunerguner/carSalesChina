import type { OriginShareTrendRecord } from '#/api/analysis';

import { expectEmptyChart, itemAt, seriesOf } from '#tests/testUtils';
import { describe, expect, it } from 'vitest';

import { ORIGIN_DIMENSIONS } from '#/utils/types';
import { buildOriginShareChartOption } from '#/views/origin/components/originShareChart';

const t = (key: string) => key;

const data: OriginShareTrendRecord[] = [
  {
    year: 2024,
    month: 1,
    domestic: 60,
    german: 25,
    japanese: 15,
    american: 0,
    european: 0,
    korean: 0,
    french: 0,
  },
  {
    year: 2024,
    month: 2,
    domestic: 70.555,
    german: 20,
    japanese: 9.445,
    american: 0,
    european: 0,
    korean: 0,
    french: 0,
  },
];

describe('buildOriginShareChartOption', () => {
  it('按 7 维生成堆叠面积系列，取两位小数', () => {
    const option = buildOriginShareChartOption(data, t);
    const series = seriesOf<{
      data: number[];
      name: string;
      stack: string;
    }>(option);
    expect(series).toHaveLength(ORIGIN_DIMENSIONS.length);
    expect(series.every((s) => s.stack === 'total')).toBe(true);
    // ORIGIN_DIMENSIONS 顺序：domestic → german → ...
    expect(itemAt(series, 0).name).toBe('pages.analysis.origin.domesticLabel');
    expect(itemAt(series, 0).data).toEqual([60, 70.56]);
    expect(itemAt(series, 1).data).toEqual([25, 20]);
    expect(itemAt(series, 2).data).toEqual([15, 9.45]);
  });

  it('x 轴为 YYYY-MM，图例含全部系列名', () => {
    const option = buildOriginShareChartOption(data, t);
    expect((option.xAxis as { data: string[] }).data).toEqual([
      '2024-01',
      '2024-02',
    ]);
    const legend = option.legend as { data: string[] };
    expect(legend.data).toHaveLength(ORIGIN_DIMENSIONS.length);
  });

  it('空数据 → 空图提示', () => {
    expectEmptyChart(buildOriginShareChartOption([], t), 'pages.common.noData');
  });
});

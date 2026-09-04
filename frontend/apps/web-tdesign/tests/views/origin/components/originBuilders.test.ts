import type { OriginShareTrendRecord } from '#/api/analysis';

import { describe, expect, it } from 'vitest';

import { itemAt } from '#tests/testUtils';
import { ORIGIN_DIMENSIONS } from '#/utils/types';

import { buildOriginShareChartOption } from '#/views/origin/components/originShareChart';
import {
  buildOriginShareTableColumns,
  buildOriginShareTableRows,
} from '#/views/origin/components/originShareTable';

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
    const series = option.series as {
      data: number[];
      name: string;
      stack: string;
    }[];
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
    const option = buildOriginShareChartOption([], t);
    expect((option.title as { text: string }).text).toBe('pages.common.noData');
  });
});

describe('buildOriginShareTableColumns', () => {
  it('时间列 + 7 维列', () => {
    const cols = buildOriginShareTableColumns(t) as {
      colKey: string;
      title: string;
    }[];
    expect(cols).toHaveLength(1 + ORIGIN_DIMENSIONS.length);
    expect(itemAt(cols, 0).colKey).toBe('time');
    expect(cols.map((c) => c.colKey)).toEqual([
      'time',
      ...ORIGIN_DIMENSIONS.map((d) => d.key),
    ]);
  });
});

describe('buildOriginShareTableRows', () => {
  it('按年月倒序且保留 key/sortKey', () => {
    const rows = buildOriginShareTableRows(data);
    expect(rows.map((r) => r.time)).toEqual(['2024-02', '2024-01']);
    expect(itemAt(rows, 0).sortKey).toBe(202_402);
    expect(itemAt(rows, 1).domestic).toBe(60);
    expect(itemAt(rows, 1).key).toBe(0); // key 为原始顺序下标
  });

  it('空输入返回空数组', () => {
    expect(buildOriginShareTableRows([])).toEqual([]);
  });
});

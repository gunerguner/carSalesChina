import type { OriginShareTrendRecord } from '#/api/analysis';

import { itemAt } from '#tests/testUtils';
import { describe, expect, it } from 'vitest';

import { ORIGIN_DIMENSIONS } from '#/utils/types';
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

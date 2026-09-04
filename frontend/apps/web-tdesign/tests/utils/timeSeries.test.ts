import { describe, expect, it } from 'vitest';

import {
  calcYoyByKey,
  getLastNMonthKeysEndingAt,
  getLatestYearMonth,
  groupSumBy,
  sortByYearMonth,
  sumByYear,
  sumMonthsUpTo,
} from '#/utils/timeSeries';

interface Row {
  month: number;
  year: number;
}

describe('groupSumBy', () => {
  it('按键分组累加', () => {
    const items = [
      { g: 'a', v: 1 },
      { g: 'b', v: 2 },
      { g: 'a', v: 3 },
    ];
    expect(
      groupSumBy(
        items,
        (i) => i.g,
        (i) => i.v,
      ),
    ).toEqual(
      new Map([
        ['a', 4],
        ['b', 2],
      ]),
    );
  });

  it('空数组返回空 Map', () => {
    expect(
      groupSumBy(
        [],
        (i: Row) => i.year,
        () => 1,
      ).size,
    ).toBe(0);
  });
});

describe('sortByYearMonth', () => {
  it('升序且不修改原数组', () => {
    const items: Row[] = [
      { year: 2024, month: 2 },
      { year: 2023, month: 12 },
      { year: 2024, month: 1 },
    ];
    const sorted = sortByYearMonth(items);
    expect(sorted.map((r) => `${r.year}-${r.month}`)).toEqual([
      '2023-12',
      '2024-1',
      '2024-2',
    ]);
    expect(items[0]).toEqual({ year: 2024, month: 2 }); // 原数组顺序不变
  });
});

describe('getLatestYearMonth', () => {
  it('取最大年月', () => {
    expect(
      getLatestYearMonth([
        { year: 2023, month: 12 },
        { year: 2024, month: 3 },
        { year: 2024, month: 1 },
      ]),
    ).toEqual({ year: 2024, month: 3 });
  });

  it('空数组返回 null', () => {
    expect(getLatestYearMonth([])).toBeNull();
  });
});

describe('getLastNMonthKeysEndingAt', () => {
  it('月末为窗口末尾向后取 n 个月', () => {
    expect(getLastNMonthKeysEndingAt(2024, 3, 3)).toEqual([
      '2024-01',
      '2024-02',
      '2024-03',
    ]);
  });

  it('跨年窗口', () => {
    expect(getLastNMonthKeysEndingAt(2024, 2, 3)).toEqual([
      '2023-12',
      '2024-01',
      '2024-02',
    ]);
    expect(getLastNMonthKeysEndingAt(2024, 1, 3)).toEqual([
      '2023-11',
      '2023-12',
      '2024-01',
    ]);
  });
});

describe('calcYoyByKey', () => {
  it('环比去年同月', () => {
    const map = new Map([
      ['2023-03', 100],
      ['2024-03', 120],
    ]);
    expect(calcYoyByKey('2024-03', map, (k) => priorYear(k))).toBe(20);
  });

  it('去年同期缺失返回 null', () => {
    const map = new Map([['2024-03', 120]]);
    expect(calcYoyByKey('2024-03', map, (k) => priorYear(k))).toBeNull();
  });

  function priorYear(key: string): string {
    const [y, m] = key.split('-');
    return `${Number(y) - 1}-${m}`;
  }
});

describe('sumByYear', () => {
  it('按年累加', () => {
    const items: Row[] = [
      { year: 2023, month: 1 },
      { year: 2024, month: 1 },
      { year: 2024, month: 2 },
    ];
    expect(sumByYear(items, (r) => r.month)).toEqual(
      new Map([
        [2023, 1],
        [2024, 3],
      ]),
    );
  });
});

describe('sumMonthsUpTo', () => {
  const map = new Map([
    ['2023-01', 2],
    ['2023-02', 4],
    ['2023-06', 99],
  ]);

  it('从 1 月累加到 maxMonth，缺失月份按 0', () => {
    expect(sumMonthsUpTo(map, 2023, 2)).toBe(6);
    expect(sumMonthsUpTo(map, 2023, 3)).toBe(6); // 3 月缺失
  });

  it('整年累加', () => {
    expect(sumMonthsUpTo(map, 2023, 12)).toBe(105);
  });

  it('不存在的年份返回 0', () => {
    expect(sumMonthsUpTo(map, 2024, 3)).toBe(0);
  });
});

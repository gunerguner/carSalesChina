import type { YearMonthRecord } from '#/types/domain';

import { calcGrowthPercent } from '#/utils/format';
import { toMonthKey } from '#/utils/period';

export function groupSumBy<T, K>(
  items: T[],
  keyFn: (item: T) => K,
  valueFn: (item: T) => number,
): Map<K, number> {
  const map = new Map<K, number>();
  for (const item of items) {
    const key = keyFn(item);
    map.set(key, (map.get(key) ?? 0) + valueFn(item));
  }
  return map;
}

export function sortByYearMonth<T extends YearMonthRecord>(items: T[]): T[] {
  return items.toSorted((a, b) =>
    a.year === b.year ? a.month - b.month : a.year - b.year,
  );
}

export function getLatestYearMonth<T extends YearMonthRecord>(
  items: T[],
): null | YearMonthRecord {
  let maxYear = 0;
  let maxMonth = 0;
  for (const { month, year } of items) {
    if (year > maxYear || (year === maxYear && month > maxMonth)) {
      maxYear = year;
      maxMonth = month;
    }
  }
  if (maxYear === 0) {
    return null;
  }
  return { month: maxMonth, year: maxYear };
}

/** 以 endYear-endMonth 为窗口末尾，连续 n 个月（含末尾月）的 YYYY-MM 列表，升序 */
export function getLastNMonthKeysEndingAt(
  endYear: number,
  endMonth: number,
  n: number,
): string[] {
  const keys: string[] = [];
  for (let offset = n - 1; offset >= 0; offset -= 1) {
    const date = new Date(endYear, endMonth - 1 - offset, 1);
    keys.push(toMonthKey(date.getFullYear(), date.getMonth() + 1));
  }
  return keys;
}

export function calcYoyByKey(
  key: string,
  map: Map<string, number>,
  getPriorKey: (key: string) => string,
): null | number {
  const current = map.get(key) ?? 0;
  return calcGrowthPercent(current, map.get(getPriorKey(key)) ?? null);
}

export function sumByYear<T extends YearMonthRecord>(
  items: T[],
  valueFn: (item: T) => number,
): Map<number, number> {
  return groupSumBy(items, (item) => item.year, valueFn);
}

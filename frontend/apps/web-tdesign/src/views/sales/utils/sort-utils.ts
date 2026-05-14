export function toYearMonthSortKey(year: number, month: number): number {
  return year * 100 + month;
}

export function toYearQuarterSortKey(year: number, quarter: number): number {
  return year * 10 + quarter;
}

export function sortByNumberAsc(a: number, b: number): number {
  return a - b;
}

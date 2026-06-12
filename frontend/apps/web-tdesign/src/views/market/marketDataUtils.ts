import type { RawSalesRecord } from '#/api/market';
import type {
  DataType,
  LevelType,
  YearMonthRecord,
} from '#/types/domain';

import { getMarketRawApi } from '#/api/market';
import { calcGrowthPercent, isNil } from '#/utils/format';
import { toMonthKey } from '#/utils/period';
import {
  getLatestYearMonth,
  groupSumBy,
  sortByYearMonth,
  sumByYear,
} from '#/utils/timeSeries';

export interface MonthlyTrendRecord extends YearMonthRecord {
  sales: number;
}

export interface MonthlyDetailRecord {
  key: string;
  month: number;
  monthNum: number;
  momGrowth: null | number;
  sales: number;
  year: number;
  yoyGrowth: null | number;
}

export interface YearlyTrendRecord {
  key: string;
  sales: number;
  year: number;
  yoyGrowth: null | number;
}

export interface QuarterlyTrendRecord {
  key: string;
  quarter: number;
  qoqGrowth: null | number;
  sales: number;
  year: number;
  yoyGrowth: null | number;
}

export interface SeriesCache {
  maxYear: null | number;
  monthlySalesMap: Map<string, number>;
  quarterSalesMap: Map<string, number>;
  sortedQuarterKeys: string[];
  sortedRows: RawSalesRecord[];
  sortedYears: number[];
  yearSalesMap: Map<number, number>;
}

export const EMPTY_SERIES_CACHE: SeriesCache = {
  sortedRows: [],
  monthlySalesMap: new Map(),
  quarterSalesMap: new Map(),
  sortedQuarterKeys: [],
  yearSalesMap: new Map(),
  sortedYears: [],
  maxYear: null,
};

function getSeriesKey(levelType: LevelType, dataType: DataType) {
  return `${levelType}::${dataType}`;
}

function parseQuarterKey(key: string): { q: number; y: number } {
  const [yPart, qPart] = key.split('-');
  return { y: Number(yPart), q: Number(qPart) };
}

function getWindowStartYear(
  maxYear: null | number,
  years: number,
): null | number {
  return isNil(maxYear) ? null : maxYear - years + 1;
}

export async function fetchMarketRawData(
  fetcher: () => Promise<RawSalesRecord[]> = getMarketRawApi,
): Promise<RawSalesRecord[]> {
  const data = await fetcher();
  return Array.isArray(data) ? data : [];
}

export function buildMarketSeriesCache(
  rawData: RawSalesRecord[],
): Map<string, SeriesCache> {
  const groupedRows = new Map<string, RawSalesRecord[]>();
  for (const row of rawData) {
    const key = getSeriesKey(row.level_type, row.data_type);
    const group = groupedRows.get(key);
    if (group) {
      group.push(row);
    } else {
      groupedRows.set(key, [row]);
    }
  }

  const cacheMap = new Map<string, SeriesCache>();
  for (const [key, group] of groupedRows) {
    const sortedRows = sortByYearMonth(group);
    const monthlySalesMap = new Map(
      sortedRows.map((r) => [toMonthKey(r.year, r.month), r.sales]),
    );
    const quarterSalesMap = groupSumBy(
      sortedRows,
      (r) => `${r.year}-${Math.ceil(r.month / 3)}`,
      (r) => r.sales,
    );
    const yearSalesMap = sumByYear(sortedRows, (r) => r.sales);
    const sortedQuarterKeys = [...quarterSalesMap.keys()].toSorted((a, b) => {
      const A = parseQuarterKey(a);
      const B = parseQuarterKey(b);
      return A.y === B.y ? A.q - B.q : A.y - B.y;
    });
    const sortedYears = [...yearSalesMap.keys()].toSorted((a, b) => a - b);

    cacheMap.set(key, {
      sortedRows,
      monthlySalesMap,
      quarterSalesMap,
      sortedQuarterKeys,
      yearSalesMap,
      sortedYears,
      maxYear: getLatestYearMonth(sortedRows)?.year ?? null,
    });
  }
  return cacheMap;
}

export function calcMonthlyTrend(
  cache: SeriesCache,
  years = 3,
): MonthlyTrendRecord[] {
  const startYear = getWindowStartYear(cache.maxYear, years);
  if (isNil(startYear)) return [];
  return cache.sortedRows.filter((r) => r.year >= startYear);
}

export function calcMonthlyDetail(cache: SeriesCache): MonthlyDetailRecord[] {
  const getSales = (year: number, month: number) =>
    cache.monthlySalesMap.get(toMonthKey(year, month)) ?? 0;

  return cache.sortedRows
    .map((r, i) => {
      const prevMonth = r.month === 1 ? 12 : r.month - 1;
      const prevMonthYear = r.month === 1 ? r.year - 1 : r.year;
      const prevMonthSales = getSales(prevMonthYear, prevMonth);
      const prevYearSales = getSales(r.year - 1, r.month);
      return {
        key: `${r.year}-${r.month}-${i}`,
        year: r.year,
        month: r.month,
        monthNum: r.month,
        sales: r.sales,
        momGrowth: calcGrowthPercent(r.sales, prevMonthSales),
        yoyGrowth: calcGrowthPercent(r.sales, prevYearSales),
      };
    })
    .toReversed();
}

export function calcQuarterlyTrend(
  cache: SeriesCache,
  quarters = 12,
): QuarterlyTrendRecord[] {
  const keys = cache.sortedQuarterKeys.slice(-quarters);

  const getQuarterSales = (year: number, quarter: number): null | number => {
    const key = `${year}-${quarter}`;
    if (!cache.quarterSalesMap.has(key)) return null;
    return Math.round(cache.quarterSalesMap.get(key) ?? 0);
  };

  return keys.map((k, i) => {
    const year = Number(k.split('-')[0]);
    const quarter = Number(k.split('-')[1]);
    const sales = getQuarterSales(year, quarter) ?? 0;
    const prevQ = quarter === 1 ? 4 : quarter - 1;
    const prevQYear = quarter === 1 ? year - 1 : year;
    const prevQSales = getQuarterSales(prevQYear, prevQ);
    const qoqGrowth = calcGrowthPercent(sales, prevQSales);
    const yoyBase = getQuarterSales(year - 1, quarter);
    const yoyGrowth = calcGrowthPercent(sales, yoyBase);
    return { key: `${k}-${i}`, year, quarter, sales, qoqGrowth, yoyGrowth };
  });
}

export function calcYearlyTrend(cache: SeriesCache): YearlyTrendRecord[] {
  return cache.sortedYears.map((year, i) => {
    const sales = Math.round(cache.yearSalesMap.get(year) ?? 0);
    const prevYear = i > 0 ? cache.sortedYears[i - 1] : undefined;
    const prevSales = isNil(prevYear)
      ? 0
      : Math.round(cache.yearSalesMap.get(prevYear) ?? 0);
    const yoyGrowth = calcGrowthPercent(sales, prevSales);
    return { key: `${year}-${i}`, year, sales, yoyGrowth };
  });
}

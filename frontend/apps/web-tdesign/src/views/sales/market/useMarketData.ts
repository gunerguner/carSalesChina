import { computed, ref } from 'vue';

import { getMarketRawApi, type RawSalesRecord } from '#/api/sales/market';

export interface MonthlyTrendRecord {
  month: number;
  sales: number;
  year: number;
}

export interface MonthlyDetailRecord {
  key: string;
  month: number;
  monthNum: number;
  momGrowth: null | number;
  sales: null | number;
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

interface SeriesCache {
  maxYear: null | number;
  monthlySalesMap: Map<string, number>;
  quarterSalesMap: Map<string, number>;
  sortedQuarterKeys: string[];
  sortedRows: RawSalesRecord[];
  sortedYears: number[];
  yearSalesMap: Map<number, number>;
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

export function useMarketData() {
  const rawData = ref<RawSalesRecord[]>([]);
  const loading = ref(false);
  const EMPTY_SERIES_CACHE: SeriesCache = {
    sortedRows: [],
    monthlySalesMap: new Map(),
    quarterSalesMap: new Map(),
    sortedQuarterKeys: [],
    yearSalesMap: new Map(),
    sortedYears: [],
    maxYear: null,
  };

  const getSeriesKey = (levelType: string, dataType: string) => `${levelType}::${dataType}`;

  const parseQuarterKey = (key: string): { q: number; y: number } => {
    const [yPart, qPart] = key.split('-');
    return { y: Number(yPart), q: Number(qPart) };
  };

  const seriesCacheIndex = computed(() => {
    const groupedRows = new Map<string, RawSalesRecord[]>();
    for (const row of rawData.value) {
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
      const sortedRows = group.toSorted((a, b) =>
        a.year === b.year ? a.month - b.month : a.year - b.year,
      );
      const monthlySalesMap = new Map<string, number>();
      const quarterSalesMap = new Map<string, number>();
      const yearSalesMap = new Map<number, number>();
      for (const row of sortedRows) {
        monthlySalesMap.set(`${row.year}-${row.month}`, row.sales);

        const quarter = Math.ceil(row.month / 3);
        const quarterKey = `${row.year}-${quarter}`;
        quarterSalesMap.set(quarterKey, (quarterSalesMap.get(quarterKey) ?? 0) + row.sales);

        yearSalesMap.set(row.year, (yearSalesMap.get(row.year) ?? 0) + row.sales);
      }
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
        maxYear: sortedRows.at(-1)?.year ?? null,
      });
    }
    return cacheMap;
  });

  function getSeriesCache(levelType: string, dataType: string): SeriesCache {
    return seriesCacheIndex.value.get(getSeriesKey(levelType, dataType)) ?? EMPTY_SERIES_CACHE;
  }

  function getWindowStartYear(maxYear: null | number, years: number): null | number {
    return maxYear == null ? null : maxYear - years + 1;
  }

  async function fetchAll() {
    loading.value = true;
    try {
      const data = await getMarketRawApi();
      rawData.value = Array.isArray(data) ? data : [];
    } catch {
      rawData.value = [];
    } finally {
      loading.value = false;
    }
  }

  /** 月度趋势（近 N 年），供折线图使用 */
  function getMonthlyTrend(levelType: string, dataType: string, years = 3): MonthlyTrendRecord[] {
    const cache = getSeriesCache(levelType, dataType);
    const startYear = getWindowStartYear(cache.maxYear, years);
    if (startYear == null) return [];
    return cache.sortedRows.filter((r) => r.year >= startYear);
  }

  /** 所有月份明细（含环比/同比），供月度明细表使用，倒序（最新在前）*/
  function getMonthlyDetail(levelType: string, dataType: string): MonthlyDetailRecord[] {
    const cache = getSeriesCache(levelType, dataType);
    const getSales = (year: number, month: number) => cache.monthlySalesMap.get(`${year}-${month}`) ?? 0;

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
          momGrowth: prevMonthSales ? round2((r.sales - prevMonthSales) / prevMonthSales * 100) : null,
          yoyGrowth: prevYearSales ? round2((r.sales - prevYearSales) / prevYearSales * 100) : null,
        };
      })
      .toReversed();
  }

  /**
   * 季度聚合（环比：上一季度，同比：去年同期季度）。
   * 先用全量原始数据汇总，再按年过滤展示（与月度趋势相同的近 N 年窗口）。
   */
  function getQuarterlyTrend(levelType: string, dataType: string, years = 3): QuarterlyTrendRecord[] {
    const cache = getSeriesCache(levelType, dataType);
    const startYear = getWindowStartYear(cache.maxYear, years);
    if (startYear == null) return [];
    const keys = cache.sortedQuarterKeys.filter((k) => Number(k.split('-')[0]) >= startYear);

    const getQ = (year: number, quarter: number): null | number => {
      const key = `${year}-${quarter}`;
      if (!cache.quarterSalesMap.has(key)) return null;
      return Math.round(cache.quarterSalesMap.get(key)!);
    };

    return keys.map((k, i) => {
      const year = Number(k.split('-')[0]);
      const quarter = Number(k.split('-')[1]);
      const sales = getQ(year, quarter)!;
      const prevQ = quarter === 1 ? 4 : quarter - 1;
      const prevQYear = quarter === 1 ? year - 1 : year;
      const prevQSales = getQ(prevQYear, prevQ);
      const qoqGrowth =
        prevQSales != null && prevQSales > 0 ? round2((sales - prevQSales) / prevQSales * 100) : null;
      const yoyBase = getQ(year - 1, quarter);
      const yoyGrowth =
        yoyBase != null && yoyBase > 0 ? round2((sales - yoyBase) / yoyBase * 100) : null;
      return { key: `${k}-${i}`, year, quarter, sales, qoqGrowth, yoyGrowth };
    });
  }

  /** 年度聚合（含同比），供年度柱状图和年度汇总表使用 */
  function getYearlyTrend(levelType: string, dataType: string): YearlyTrendRecord[] {
    const cache = getSeriesCache(levelType, dataType);
    return cache.sortedYears.map((year, i) => {
      const sales = Math.round(cache.yearSalesMap.get(year) ?? 0);
      const prevYear = cache.sortedYears.at(i - 1);
      const prevSales = prevYear == null ? 0 : Math.round(cache.yearSalesMap.get(prevYear) ?? 0);
      const yoyGrowth = prevSales ? round2((sales - prevSales) / prevSales * 100) : null;
      return { key: `${year}-${i}`, year, sales, yoyGrowth };
    });
  }

  return {
    loading,
    rawData,
    fetchAll,
    getMonthlyDetail,
    getMonthlyTrend,
    getQuarterlyTrend,
    getYearlyTrend,
  };
}

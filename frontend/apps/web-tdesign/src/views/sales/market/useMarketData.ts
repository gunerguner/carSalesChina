import { ref } from 'vue';

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

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

export function useMarketData() {
  const rawData = ref<RawSalesRecord[]>([]);
  const loading = ref(false);

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

  /** 过滤出指定 levelType + dataType 的原始月度记录，按年月升序 */
  function filterSorted(levelType: string, dataType: string): RawSalesRecord[] {
    return rawData.value
      .filter((r) => r.level_type === levelType && r.data_type === dataType)
      .toSorted((a, b) => (a.year === b.year ? a.month - b.month : a.year - b.year));
  }

  /** 月度趋势（近 N 年），供折线图使用 */
  function getMonthlyTrend(levelType: string, dataType: string, years = 3): MonthlyTrendRecord[] {
    const startYear = new Date().getFullYear() - years + 1;
    return filterSorted(levelType, dataType).filter((r) => r.year >= startYear);
  }

  /** 所有月份明细（含环比/同比），供月度明细表使用，倒序（最新在前）*/
  function getMonthlyDetail(levelType: string, dataType: string): MonthlyDetailRecord[] {
    const rows = filterSorted(levelType, dataType);
    const salesMap = new Map<string, number>();
    for (const r of rows) {
      salesMap.set(`${r.year}-${r.month}`, r.sales);
    }
    const getSales = (year: number, month: number) => salesMap.get(`${year}-${month}`) ?? 0;

    return rows
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

  /** 年度聚合（含同比），供年度柱状图和年度汇总表使用 */
  function getYearlyTrend(levelType: string, dataType: string): YearlyTrendRecord[] {
    const rows = filterSorted(levelType, dataType);
    const yearMap = new Map<number, number>();
    for (const r of rows) {
      yearMap.set(r.year, (yearMap.get(r.year) ?? 0) + r.sales);
    }
    const years = [...yearMap.keys()].toSorted((a, b) => a - b);
    return years.map((year, i) => {
      const sales = yearMap.get(year) ?? 0;
      const prevYear = years.at(i - 1);
      const prevSales = prevYear == null ? 0 : (yearMap.get(prevYear) ?? 0);
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
    getYearlyTrend,
  };
}

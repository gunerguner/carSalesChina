import type { RawSalesRecord } from '#/api/sales/market';

import { computed, ref } from 'vue';

import {
  buildMarketSeriesCache,
  calcMonthlyDetail,
  calcMonthlyTrend,
  calcQuarterlyTrend,
  calcYearlyTrend,
  EMPTY_SERIES_CACHE,
  fetchMarketRawData,
  type MonthlyDetailRecord,
  type MonthlyTrendRecord,
  type QuarterlyTrendRecord,
  type SeriesCache,
  type YearlyTrendRecord,
} from './marketDataUtils';

export type { MonthlyDetailRecord, MonthlyTrendRecord, QuarterlyTrendRecord, YearlyTrendRecord };

const rawData = ref<RawSalesRecord[]>([]);
const loading = ref(false);
let hasFetched = false;
let pendingFetch: null | Promise<void> = null;

export function useMarketData() {
  const seriesCacheIndex = computed(() => {
    return buildMarketSeriesCache(rawData.value);
  });

  async function fetchAll(force = false) {
    if (!force && hasFetched) {
      return;
    }
    if (pendingFetch) {
      return pendingFetch;
    }

    pendingFetch = (async () => {
    loading.value = true;
    try {
      rawData.value = await fetchMarketRawData();
      hasFetched = true;
    } catch {
      rawData.value = [];
    } finally {
      loading.value = false;
      pendingFetch = null;
    }
    })();

    return pendingFetch;
  }

  /** 月度趋势（近 N 年），供折线图使用 */
  function getMonthlyTrend(levelType: string, dataType: string, years = 3): MonthlyTrendRecord[] {
    return calcMonthlyTrend(getSeriesCache(seriesCacheIndex, levelType, dataType), years);
  }

  /** 所有月份明细（含环比/同比），供月度明细表使用，倒序（最新在前）*/
  function getMonthlyDetail(levelType: string, dataType: string): MonthlyDetailRecord[] {
    return calcMonthlyDetail(getSeriesCache(seriesCacheIndex, levelType, dataType));
  }

  /**
   * 季度聚合（环比：上一季度，同比：去年同期季度）。
   * 先用全量原始数据汇总，再按年过滤展示（与月度趋势相同的近 N 年窗口）。
   */
  function getQuarterlyTrend(levelType: string, dataType: string, years = 3): QuarterlyTrendRecord[] {
    return calcQuarterlyTrend(getSeriesCache(seriesCacheIndex, levelType, dataType), years);
  }

  /** 年度聚合（含同比），供年度柱状图和年度汇总表使用 */
  function getYearlyTrend(levelType: string, dataType: string): YearlyTrendRecord[] {
    return calcYearlyTrend(getSeriesCache(seriesCacheIndex, levelType, dataType));
  }

  return {
    loading,
    fetchAll,
    getMonthlyDetail,
    getMonthlyTrend,
    getQuarterlyTrend,
    getYearlyTrend,
  };
}

function getSeriesCache(
  seriesCacheIndex: Readonly<{ value: Map<string, SeriesCache> }>,
  levelType: string,
  dataType: string,
): SeriesCache {
  return seriesCacheIndex.value.get(`${levelType}::${dataType}`) ?? EMPTY_SERIES_CACHE;
}

import type {
  MonthlyDetailRecord,
  MonthlyTrendRecord,
  QuarterlyTrendRecord,
  SeriesCache,
  YearlyTrendRecord,
} from './marketDataUtils';

import type { RawSalesRecord } from '#/api/market';
import type { DataType, LevelType } from '#/utils/types';

import { computed, ref } from 'vue';

import { createFetchOnceController } from '#/composables/useFetchOnce';

import {
  buildMarketSeriesCache,
  calcMonthlyDetail,
  calcMonthlyTrend,
  calcQuarterlyTrend,
  calcYearlyTrend,
  EMPTY_SERIES_CACHE,
  fetchMarketRawData,
} from './marketDataUtils';

export type {
  MonthlyDetailRecord,
  MonthlyTrendRecord,
  QuarterlyTrendRecord,
  YearlyTrendRecord,
};

const rawData = ref<RawSalesRecord[]>([]);
const { error, execute, loading } = createFetchOnceController();

export function useMarketData() {
  const seriesCacheIndex = computed(() => {
    return buildMarketSeriesCache(rawData.value);
  });

  async function fetchAll(force = false) {
    return execute(force, async () => {
      try {
        rawData.value = await fetchMarketRawData();
      } catch (error_) {
        rawData.value = [];
        throw error_;
      }
    });
  }

  /** 月度趋势（近 N 年），供折线图使用 */
  function getMonthlyTrend(
    levelType: LevelType,
    dataType: DataType,
    years = 3,
  ): MonthlyTrendRecord[] {
    return calcMonthlyTrend(
      getSeriesCache(seriesCacheIndex, levelType, dataType),
      years,
    );
  }

  /** 所有月份明细（含环比/同比），供月度明细表使用，倒序（最新在前）*/
  function getMonthlyDetail(
    levelType: LevelType,
    dataType: DataType,
  ): MonthlyDetailRecord[] {
    return calcMonthlyDetail(
      getSeriesCache(seriesCacheIndex, levelType, dataType),
    );
  }

  /**
   * 季度聚合（环比：上一季度，同比：去年同期季度）。
   * 先用全量原始数据汇总，再取最近 N 个季度展示（默认 12）。
   */
  function getQuarterlyTrend(
    levelType: LevelType,
    dataType: DataType,
    quarters = 12,
  ): QuarterlyTrendRecord[] {
    return calcQuarterlyTrend(
      getSeriesCache(seriesCacheIndex, levelType, dataType),
      quarters,
    );
  }

  /** 年度聚合（含同比），供年度柱状图和年度汇总表使用 */
  function getYearlyTrend(
    levelType: LevelType,
    dataType: DataType,
  ): YearlyTrendRecord[] {
    return calcYearlyTrend(
      getSeriesCache(seriesCacheIndex, levelType, dataType),
    );
  }

  return {
    error,
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
  levelType: LevelType,
  dataType: DataType,
): SeriesCache {
  return (
    seriesCacheIndex.value.get(`${levelType}::${dataType}`) ??
    EMPTY_SERIES_CACHE
  );
}

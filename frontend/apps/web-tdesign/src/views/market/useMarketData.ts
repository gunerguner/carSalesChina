import type {
  MonthlyDetailRecord,
  MonthlyTrendRecord,
  QuarterlyTrendRecord,
  SeriesCache,
  YearlyTrendRecord,
} from './marketDataUtils';
import type { MarketPeriodGranularity } from './types';

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
const levelType = ref<LevelType>('all');
const dataType = ref<DataType>('retail');
const period = ref<MarketPeriodGranularity>('monthly');
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

  function withCache<T>(
    calcFn: (cache: SeriesCache) => T,
  ): (level: LevelType, type: DataType) => T {
    return (level, type) =>
      calcFn(getSeriesCache(seriesCacheIndex.value, level, type));
  }

  return {
    dataType,
    error,
    levelType,
    loading,
    period,
    fetchAll,
    getMonthlyDetail: withCache(calcMonthlyDetail),
    getMonthlyTrend: withCache(calcMonthlyTrend),
    getQuarterlyTrend: withCache(calcQuarterlyTrend),
    getYearlyTrend: withCache(calcYearlyTrend),
  };
}

function getSeriesCache(
  seriesCacheIndex: Map<string, SeriesCache>,
  levelType: LevelType,
  dataType: DataType,
): SeriesCache {
  return seriesCacheIndex.get(`${levelType}::${dataType}`) ?? EMPTY_SERIES_CACHE;
}

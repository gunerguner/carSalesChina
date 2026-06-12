import type { BrandSeriesRecord } from './types';

import type { BrandTrendAllPeriodsRecord } from '#/api/brand';
import type { DataType } from '#/utils/types';

import { computed, ref } from 'vue';

import { getBrandTrendAllPeriodsApi } from '#/api/brand';
import { createKeyedFetchController } from '#/composables/useFetchOnce';
import { calcGrowthPercent, ensureArray, isNil } from '#/utils/format';
import { priorYearMonthKey, toMonthKey } from '#/utils/period';
import {
  calcYoyByKey,
  getLastNMonthKeysEndingAt,
  getLatestYearMonth,
  sumByYear,
} from '#/utils/timeSeries';

/** 品牌趋势统计周期：近一年/近两年（按月）与年度汇总 */
export type BrandTrendGranularity = 'recentTwoYears' | 'recentYear' | 'yearly';

type BrandRawRecord = BrandTrendAllPeriodsRecord;

const selectedBrands = ref<string[]>([]);
const granularity = ref<BrandTrendGranularity>('recentYear');
const dataType = ref<DataType>('retail');

const {
  data: rawDataRef,
  error,
  execute: executeFetch,
  loading,
} = createKeyedFetchController<BrandRawRecord[]>({
  fetch: async (key) => {
    const [requestDataType = 'retail', brandNames = ''] = key.split('::');
    const result = await getBrandTrendAllPeriodsApi({
      brand_names: brandNames,
      data_type: requestDataType as DataType,
    });
    return ensureArray(result);
  },
  getKey() {
    const brandsKey = [...selectedBrands.value].toSorted().join(',');
    return `${dataType.value}::${brandsKey}`;
  },
  isEmptyKey(key) {
    const brandsKey = key.split('::')[1] ?? '';
    return brandsKey === '';
  },
});

const rawData = computed(() => rawDataRef.value ?? []);

export function useBrandData() {
  async function fetchRawData(force = false) {
    return executeFetch(force);
  }

  const monthlySeries = computed<BrandSeriesRecord[]>(() => {
    if (granularity.value === 'yearly') {
      return [];
    }
    const nMonths = granularity.value === 'recentTwoYears' ? 24 : 12;
    const latest = getLatestYearMonth(
      rawData.value.flatMap((brand) => brand.monthly_data ?? []),
    );
    const recentKeys = isNil(latest)
      ? []
      : getLastNMonthKeysEndingAt(latest.year, latest.month, nMonths);
    return rawData.value.map((brand) => {
      const pointMap = new Map<string, number>();
      for (const point of brand.monthly_data ?? []) {
        const key = toMonthKey(point.year, point.month);
        pointMap.set(key, point.sales ?? 0);
      }
      return {
        brand_name: brand.brand_name,
        points: recentKeys.map((time) => {
          const sales = pointMap.get(time) ?? 0;
          return {
            time,
            sales,
            yoyGrowth: calcYoyByKey(time, pointMap, priorYearMonthKey),
          };
        }),
      };
    });
  });

  const yearlySeries = computed<BrandSeriesRecord[]>(() => {
    return rawData.value.map((brand) => {
      const yearMap = sumByYear(
        brand.monthly_data ?? [],
        (point) => point.sales ?? 0,
      );
      const sortedYears = [...yearMap.keys()].toSorted((a, b) => a - b);
      return {
        brand_name: brand.brand_name,
        points: sortedYears.map((year) => {
          const sales = yearMap.get(year) ?? 0;
          return {
            time: String(year),
            sales,
            yoyGrowth: calcGrowthPercent(sales, yearMap.get(year - 1) ?? null),
          };
        }),
      };
    });
  });

  const activeSeries = computed<BrandSeriesRecord[]>(() => {
    return granularity.value === 'yearly'
      ? yearlySeries.value
      : monthlySeries.value;
  });

  /** 表格时间列数量：null 表示与图表一致展示全部（年度为全部年份） */
  const tableTimeLabelMaxCount = computed<null | number>(() => {
    if (granularity.value === 'yearly') {
      return null;
    }
    return granularity.value === 'recentTwoYears' ? 24 : 12;
  });

  const timeLabels = computed<string[]>(() => {
    const all = new Set<string>();
    for (const brand of activeSeries.value) {
      for (const point of brand.points) {
        all.add(point.time);
      }
    }
    return [...all].toSorted((a, b) => a.localeCompare(b));
  });

  return {
    activeSeries,
    dataType,
    error,
    fetchRawData,
    granularity,
    loading,
    selectedBrands,
    tableTimeLabelMaxCount,
    timeLabels,
  };
}

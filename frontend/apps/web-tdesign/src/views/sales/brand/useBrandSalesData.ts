import type { BrandSeriesRecord } from './types';

import type { BrandTrendAllPeriodsRecord } from '#/api/sales/brand';

import { computed, ref } from 'vue';

import { getBrandTrendAllPeriodsApi } from '#/api/sales/brand';
import { createKeyedFetchController } from '#/composables/useFetchOnce';
import { calcGrowthPercent, isNil } from '#/utils/format';
import { toMonthKey } from '#/utils/period';

type DataType = 'production' | 'retail';

/** 品牌趋势统计周期：近一年/近两年（按月）与年度汇总 */
export type BrandTrendGranularity = 'recentTwoYears' | 'recentYear' | 'yearly';

type BrandRawRecord = BrandTrendAllPeriodsRecord;

function priorYearMonthKey(monthKey: string): string {
  const [yearText, monthText] = monthKey.split('-');
  return toMonthKey(Number(yearText) - 1, Number(monthText));
}

/** 当前接口返回的所有品牌中，有数据的最晚一个年月（不跟系统日历对齐，避免多出库里没有的月份） */
function getLatestMonthFromRawData(
  data: BrandRawRecord[],
): null | { month: number; year: number } {
  let maxYear = 0;
  let maxMonth = 0;
  for (const brand of data) {
    for (const point of brand.monthly_data ?? []) {
      const { month, year } = point;
      if (year > maxYear || (year === maxYear && month > maxMonth)) {
        maxYear = year;
        maxMonth = month;
      }
    }
  }
  if (maxYear === 0) {
    return null;
  }
  return { month: maxMonth, year: maxYear };
}

/** 以 endYear-endMonth 为窗口末尾，连续 n 个月（含末尾月）的 YYYY-MM 列表，升序 */
function getLastNMonthKeysEndingAt(
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
    return Array.isArray(result) ? result : [];
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

export function useBrandSalesData() {
  async function fetchRawData(force = false) {
    return executeFetch(force);
  }

  const monthlySeries = computed<BrandSeriesRecord[]>(() => {
    if (granularity.value === 'yearly') {
      return [];
    }
    const nMonths = granularity.value === 'recentTwoYears' ? 24 : 12;
    const latest = getLatestMonthFromRawData(rawData.value);
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
            yoyGrowth: calcGrowthPercent(
              sales,
              pointMap.get(priorYearMonthKey(time)),
            ),
          };
        }),
      };
    });
  });

  const yearlySeries = computed<BrandSeriesRecord[]>(() => {
    return rawData.value.map((brand) => {
      const yearMap = new Map<number, number>();
      for (const point of brand.monthly_data ?? []) {
        const year = point.year;
        const total = yearMap.get(year) ?? 0;
        yearMap.set(year, total + (point.sales ?? 0));
      }
      const sortedYears = [...yearMap.keys()].toSorted((a, b) => a - b);
      return {
        brand_name: brand.brand_name,
        points: sortedYears.map((year) => {
          const sales = yearMap.get(year) ?? 0;
          return {
            time: String(year),
            sales,
            yoyGrowth: calcGrowthPercent(sales, yearMap.get(year - 1)),
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
    rawData,
    selectedBrands,
    tableTimeLabelMaxCount,
    timeLabels,
  };
}

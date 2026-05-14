import { computed, ref } from 'vue';

import {
  type BrandTrendAllPeriodsRecord,
  getBrandTrendAllPeriodsApi,
} from '#/api/sales/brand';
import { toMonthKey } from '#/views/sales/utils/period-utils';

type DataType = 'production' | 'retail';
type Granularity = 'monthly' | 'yearly';

type BrandRawRecord = BrandTrendAllPeriodsRecord;

interface BrandSeriesPoint {
  sales: number;
  time: string;
}

interface BrandSeriesRecord {
  brand_name: string;
  points: BrandSeriesPoint[];
}

/** 当前接口返回的所有品牌中，有数据的最晚一个年月（不跟系统日历对齐，避免多出库里没有的月份） */
function getLatestMonthFromRawData(data: BrandRawRecord[]): null | { month: number; year: number } {
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
function getLastNMonthKeysEndingAt(endYear: number, endMonth: number, n: number): string[] {
  const keys: string[] = [];
  for (let offset = n - 1; offset >= 0; offset -= 1) {
    const date = new Date(endYear, endMonth - 1 - offset, 1);
    keys.push(toMonthKey(date.getFullYear(), date.getMonth() + 1));
  }
  return keys;
}

const loading = ref(false);
const error = ref<null | string>(null);
const selectedBrands = ref<string[]>([]);
const granularity = ref<Granularity>('monthly');
const dataType = ref<DataType>('retail');
const rawData = ref<BrandRawRecord[]>([]);
const rawDataCache = new Map<string, BrandRawRecord[]>();
let fetchGeneration = 0;

function getCacheKey() {
  const brandsKey = [...selectedBrands.value].toSorted().join(',');
  return `${dataType.value}::${brandsKey}`;
}

export function useBrandSalesData() {
  async function fetchRawData(force = false) {
    if (selectedBrands.value.length === 0) {
      fetchGeneration += 1;
      error.value = null;
      rawData.value = [];
      loading.value = false;
      return;
    }

    const requestKey = getCacheKey();
    if (!force) {
      const cached = rawDataCache.get(requestKey);
      if (cached) {
        error.value = null;
        rawData.value = cached;
        return;
      }
    }

    const requestGeneration = ++fetchGeneration;
    const requestBrandNames = selectedBrands.value.join(',');
    const requestDataType = dataType.value;
    return (async () => {
      loading.value = true;
      error.value = null;
      try {
        const result = await getBrandTrendAllPeriodsApi({
          brand_names: requestBrandNames,
          data_type: requestDataType,
        });
        const normalized = Array.isArray(result) ? result : [];
        if (
          requestGeneration !== fetchGeneration ||
          requestKey !== getCacheKey()
        ) {
          return;
        }
        rawData.value = normalized;
        rawDataCache.set(requestKey, normalized);
      } catch (error_) {
        if (requestGeneration !== fetchGeneration) {
          return;
        }
        error.value = 'failed_to_load_brand_sales_data';
        console.error('[useBrandSalesData] fetchRawData failed', error_);
        rawData.value = [];
      } finally {
        if (requestGeneration === fetchGeneration) {
          loading.value = false;
        }
      }
    })();
  }

  const monthlySeries = computed<BrandSeriesRecord[]>(() => {
    const latest = getLatestMonthFromRawData(rawData.value);
    const recent12 =
      latest == null
        ? []
        : getLastNMonthKeysEndingAt(latest.year, latest.month, 12);
    return rawData.value.map((brand) => {
      const pointMap = new Map<string, number>();
      for (const point of brand.monthly_data ?? []) {
        const key = toMonthKey(point.year, point.month);
        pointMap.set(key, point.sales ?? 0);
      }
      return {
        brand_name: brand.brand_name,
        points: recent12.map((time) => ({
          time,
          sales: pointMap.get(time) ?? 0,
        })),
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
        points: sortedYears.map((year) => ({
          time: String(year),
          sales: yearMap.get(year) ?? 0,
        })),
      };
    });
  });

  const activeSeries = computed<BrandSeriesRecord[]>(() => {
    return granularity.value === 'monthly' ? monthlySeries.value : yearlySeries.value;
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
    timeLabels,
  };
}

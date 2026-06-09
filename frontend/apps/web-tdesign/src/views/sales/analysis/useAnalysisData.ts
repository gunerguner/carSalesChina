import type {
  NevBreakdownRecord,
  NevShareTrendRecord,
  OriginShareTrendRecord,
} from '#/api/sales/analysis';

import { ref } from 'vue';

import {
  getNevBreakdownApi,
  getNevShareTrendApi,
  getOriginShareTrendApi,
} from '#/api/sales/analysis';
import { createFetchOnceController } from '#/composables/useFetchOnce';

const { error, execute, loading } = createFetchOnceController();
const nevShareTrend = ref<NevShareTrendRecord[]>([]);
const nevBreakdown = ref<NevBreakdownRecord[]>([]);
const originShareTrend = ref<OriginShareTrendRecord[]>([]);

export function useAnalysisData() {
  async function fetchAll(force = false) {
    return execute(force, async () => {
      try {
        const [share, breakdown, origin] = await Promise.all([
          getNevShareTrendApi({ granularity: 'monthly' }),
          getNevBreakdownApi({ granularity: 'monthly' }),
          getOriginShareTrendApi({ granularity: 'monthly' }),
        ]);
        nevShareTrend.value = Array.isArray(share) ? share : [];
        nevBreakdown.value = Array.isArray(breakdown) ? breakdown : [];
        originShareTrend.value = Array.isArray(origin) ? origin : [];
      } catch (error_) {
        nevShareTrend.value = [];
        nevBreakdown.value = [];
        originShareTrend.value = [];
        throw error_;
      }
    });
  }

  return {
    error,
    loading,
    nevShareTrend,
    nevBreakdown,
    originShareTrend,
    fetchAll,
  };
}

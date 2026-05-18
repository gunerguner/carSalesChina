import { ref } from 'vue';

import {
  getNevBreakdownApi,
  getNevShareTrendApi,
  getOriginShareTrendApi,
  type NevBreakdownRecord,
  type NevShareTrendRecord,
  type OriginShareTrendRecord,
} from '#/api/sales/analysis';
import { createFetchOnceController } from '#/composables/useFetchOnce';

const { execute, loading } = createFetchOnceController();
const error = ref<null | string>(null);
const nevShareTrend = ref<NevShareTrendRecord[]>([]);
const nevBreakdown = ref<NevBreakdownRecord[]>([]);
const originShareTrend = ref<OriginShareTrendRecord[]>([]);

export function useAnalysisData() {
  async function fetchAll(force = false) {
    return execute(force, async () => {
      error.value = null;
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
        error.value = 'failed_to_load_analysis_data';
        console.error('[useAnalysisData] fetchAll failed', error_);
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

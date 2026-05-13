import { ref } from 'vue';

import {
  type NevBreakdownRecord,
  getNevBreakdownApi,
  type NevShareTrendRecord,
  getNevShareTrendApi,
  type OriginShareTrendRecord,
  getOriginShareTrendApi,
} from '#/api/sales/analysis';

export function useAnalysisData() {
  const loading = ref(false);
  const error = ref<null | string>(null);
  const nevShareTrend = ref<NevShareTrendRecord[]>([]);
  const nevBreakdown = ref<NevBreakdownRecord[]>([]);
  const originShareTrend = ref<OriginShareTrendRecord[]>([]);

  async function fetchAll() {
    loading.value = true;
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
    } catch (err) {
      error.value = 'failed_to_load_analysis_data';
      console.error('[useAnalysisData] fetchAll failed', err);
      nevShareTrend.value = [];
      nevBreakdown.value = [];
      originShareTrend.value = [];
    } finally {
      loading.value = false;
    }
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

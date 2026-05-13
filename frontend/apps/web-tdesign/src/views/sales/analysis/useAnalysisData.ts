import { ref } from 'vue';

import {
  getNevBreakdownApi,
  getNevShareTrendApi,
  getOriginShareTrendApi,
  type NevBreakdownRecord,
  type NevShareTrendRecord,
  type OriginShareTrendRecord,
} from '#/api/sales/analysis';

const loading = ref(false);
const error = ref<null | string>(null);
const nevShareTrend = ref<NevShareTrendRecord[]>([]);
const nevBreakdown = ref<NevBreakdownRecord[]>([]);
const originShareTrend = ref<OriginShareTrendRecord[]>([]);
let hasFetched = false;
let pendingFetch: null | Promise<void> = null;

export function useAnalysisData() {
  async function fetchAll(force = false) {
    if (!force && hasFetched) {
      return;
    }
    if (pendingFetch) {
      return pendingFetch;
    }

    pendingFetch = (async () => {
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
      hasFetched = true;
    } catch (error_) {
      error.value = 'failed_to_load_analysis_data';
      console.error('[useAnalysisData] fetchAll failed', error_);
      nevShareTrend.value = [];
      nevBreakdown.value = [];
      originShareTrend.value = [];
    } finally {
      loading.value = false;
      pendingFetch = null;
    }
    })();

    return pendingFetch;
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

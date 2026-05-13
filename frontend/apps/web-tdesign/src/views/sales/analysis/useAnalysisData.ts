import { ref } from 'vue';

import {
  getNevBreakdownApi,
  getNevShareTrendApi,
  getOriginShareTrendApi,
} from '#/api/sales/analysis';

export function useAnalysisData() {
  const loading = ref(false);
  const nevShareTrend = ref<any[]>([]);
  const nevBreakdown = ref<any[]>([]);
  const originShareTrend = ref<any[]>([]);

  async function fetchAll() {
    loading.value = true;
    try {
      const [share, breakdown, origin] = await Promise.all([
        getNevShareTrendApi({ granularity: 'monthly' }),
        getNevBreakdownApi({ granularity: 'monthly' }),
        getOriginShareTrendApi({ granularity: 'monthly' }),
      ]);
      nevShareTrend.value = Array.isArray(share) ? share : [];
      nevBreakdown.value = Array.isArray(breakdown) ? breakdown : [];
      originShareTrend.value = Array.isArray(origin) ? origin : [];
    } catch {
      nevShareTrend.value = [];
      nevBreakdown.value = [];
      originShareTrend.value = [];
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    nevShareTrend,
    nevBreakdown,
    originShareTrend,
    fetchAll,
  };
}

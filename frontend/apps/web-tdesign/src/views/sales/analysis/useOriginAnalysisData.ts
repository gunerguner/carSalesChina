import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { ref } from 'vue';

import { getOriginShareTrendApi } from '#/api/sales/analysis';
import { createFetchOnceController } from '#/composables/useFetchOnce';

const { error, execute, loading } = createFetchOnceController();
const originShareTrend = ref<OriginShareTrendRecord[]>([]);

export function useOriginAnalysisData() {
  async function fetchAll(force = false) {
    return execute(force, async () => {
      try {
        const origin = await getOriginShareTrendApi({ granularity: 'monthly' });
        originShareTrend.value = Array.isArray(origin) ? origin : [];
      } catch (error_) {
        originShareTrend.value = [];
        throw error_;
      }
    });
  }

  return {
    error,
    loading,
    originShareTrend,
    fetchAll,
  };
}

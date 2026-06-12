import type { OriginShareTrendRecord } from '#/api/analysis';

import { ref } from 'vue';

import { getOriginShareTrendApi } from '#/api/analysis';
import {
  createFetchOnceController,
  fetchArrayInto,
} from '#/composables/useFetchOnce';

const { error, execute, loading } = createFetchOnceController();
const originShareTrend = ref<OriginShareTrendRecord[]>([]);

export function useOriginAnalysisData() {
  async function fetchAll(force = false) {
    return execute(force, async () => {
      try {
        await fetchArrayInto(originShareTrend, () =>
          getOriginShareTrendApi({ granularity: 'monthly' }),
        );
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

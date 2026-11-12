import type { NevBreakdownRecord, NevShareTrendRecord } from '#/api/analysis';

import { ref } from 'vue';

import { getNevBreakdownApi, getNevShareTrendApi } from '#/api/analysis';
import {
  createFetchOnceController,
  fetchArrayInto,
} from '#/composables/useFetchOnce';

const { error, execute, loading } = createFetchOnceController();
const nevShareTrend = ref<NevShareTrendRecord[]>([]);
const nevBreakdown = ref<NevBreakdownRecord[]>([]);

export function useNevAnalysisData() {
  async function fetchAll(force = false) {
    return execute(force, async () => {
      try {
        await Promise.all([
          fetchArrayInto(nevShareTrend, () =>
            getNevShareTrendApi({ granularity: 'monthly' }),
          ),
          fetchArrayInto(nevBreakdown, () =>
            getNevBreakdownApi({ granularity: 'monthly' }),
          ),
        ]);
      } catch (error_) {
        nevShareTrend.value = [];
        nevBreakdown.value = [];
        throw error_;
      }
    });
  }

  return {
    error,
    loading,
    nevShareTrend,
    nevBreakdown,
    fetchAll,
  };
}

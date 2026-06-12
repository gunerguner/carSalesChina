import type {
  NevBreakdownRecord,
  NevShareTrendRecord,
} from '#/api/analysis';

import { ref } from 'vue';

import { getNevBreakdownApi, getNevShareTrendApi } from '#/api/analysis';
import { createFetchOnceController } from '#/composables/useFetchOnce';
import { ensureArray } from '#/utils/format';

const { error, execute, loading } = createFetchOnceController();
const nevShareTrend = ref<NevShareTrendRecord[]>([]);
const nevBreakdown = ref<NevBreakdownRecord[]>([]);

export function useNevAnalysisData() {
  async function fetchAll(force = false) {
    return execute(force, async () => {
      try {
        const [share, breakdown] = await Promise.all([
          getNevShareTrendApi({ granularity: 'monthly' }),
          getNevBreakdownApi({ granularity: 'monthly' }),
        ]);
        nevShareTrend.value = ensureArray(share);
        nevBreakdown.value = ensureArray(breakdown);
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

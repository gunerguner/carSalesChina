import type { BrandMetaItem } from '#/api/brand';

import { computed, ref } from 'vue';

import { getBrandMetaAllApi } from '#/api/brand';
import { createFetchOnceController } from '#/composables/useFetchOnce';
import { ensureArray } from '#/utils/format';

const { error, execute, loading } = createFetchOnceController();
const brandMetaList = ref<BrandMetaItem[]>([]);

export function useBrandMetaAll() {
  const brandOptions = computed(() =>
    brandMetaList.value.map((item) => ({
      label: item.brand_name,
      value: item.brand_name,
    })),
  );

  async function ensureLoaded(force = false) {
    return execute(force, async () => {
      const list = await getBrandMetaAllApi();
      brandMetaList.value = ensureArray(list);
    });
  }

  return {
    brandOptions,
    brandMetaLoading: loading,
    ensureLoaded,
    error,
  };
}

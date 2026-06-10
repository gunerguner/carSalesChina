import type { BrandMetaItem } from '#/api/sales/brand';

import { computed, ref } from 'vue';

import { getBrandMetaAllApi } from '#/api/sales/brand';
import { createFetchOnceController } from '#/composables/useFetchOnce';

const { execute, loading } = createFetchOnceController();
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
      brandMetaList.value = Array.isArray(list) ? list : [];
    });
  }

  return {
    brandOptions,
    brandMetaLoading: loading,
    ensureLoaded,
  };
}

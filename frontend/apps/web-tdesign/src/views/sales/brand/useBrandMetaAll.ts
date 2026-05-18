import { computed, ref } from 'vue';

import { type BrandMetaItem, getBrandMetaAllApi } from '#/api/sales/brand';
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
    brandMetaList,
    brandOptions,
    brandMetaLoading: loading,
    ensureLoaded,
  };
}

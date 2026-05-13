<script lang="ts" setup>
import { ref, watch } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import { getBrandMetaAllApi } from '#/api/sales/brand';
import { $t } from '#/locales';

import { DEFAULT_SELECTED_BRAND_NAMES } from '../brand-defaults';

type DataType = 'production' | 'retail';
type Granularity = 'monthly' | 'yearly';

const emit = defineEmits<{
  change: [
    payload: {
      brands: string[];
      dataType: DataType;
      granularity: Granularity;
    },
  ];
}>();

const granularity = ref<Granularity>('monthly');
const dataType = ref<DataType>('retail');
const selectedBrands = ref<string[]>([...DEFAULT_SELECTED_BRAND_NAMES]);
const brandOptions = ref<{ label: string; value: string }[]>([]);
const brandLoading = ref(false);

async function fetchBrandOptions() {
  brandLoading.value = true;
  try {
    const list: any = await getBrandMetaAllApi();
    brandOptions.value = Array.isArray(list)
      ? list.map((item: any) => ({
          label: item.brand_name,
          value: item.brand_name,
        }))
      : [];
    const allowed = new Set(brandOptions.value.map((o) => o.value));
    const matched = DEFAULT_SELECTED_BRAND_NAMES.filter((name) =>
      allowed.has(name),
    ).slice(0, 3);
    const next = matched.length > 0 ? matched : [];
    const unchanged =
      next.length === selectedBrands.value.length &&
      next.every((name, i) => name === selectedBrands.value[i]);
    if (!unchanged) {
      selectedBrands.value = next;
    }
  } finally {
    brandLoading.value = false;
  }
}

function handleBrandsChange(val: unknown) {
  if (val == null) {
    selectedBrands.value = [];
    return;
  }
  const raw = Array.isArray(val) ? val : [val];
  const arr = raw.map(String);
  selectedBrands.value = arr.length > 3 ? arr.slice(-3) : arr;
}

watch(
  [granularity, dataType, selectedBrands],
  () => {
    emit('change', {
      granularity: granularity.value,
      dataType: dataType.value,
      brands: selectedBrands.value,
    });
  },
  { deep: true, immediate: true },
);

fetchBrandOptions();
</script>

<template>
  <div class="mb-4 flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.trend.selectBrands') }}</span>
      <Select
        :value="selectedBrands"
        :options="brandOptions"
        :loading="brandLoading"
        :placeholder="$t('sales.brand.trend.selectPlaceholder')"
        multiple
        :max="3"
        filterable
        style="width: 360px"
        @change="handleBrandsChange"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.trend.granularity') }}</span>
      <RadioGroup v-model="granularity" variant="default-filled">
        <RadioButton value="monthly">{{ $t('sales.brand.trend.monthly') }}</RadioButton>
        <RadioButton value="yearly">{{ $t('sales.brand.trend.yearly') }}</RadioButton>
      </RadioGroup>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.trend.dataType') }}</span>
      <RadioGroup v-model="dataType" variant="default-filled">
        <RadioButton value="retail">{{ $t('sales.brand.trend.retail') }}</RadioButton>
        <RadioButton value="production">{{ $t('sales.brand.trend.production') }}</RadioButton>
      </RadioGroup>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { BrandTrendGranularity } from '../useBrandSalesData';

import { ref, watch } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import { $t } from '#/locales';

import { DEFAULT_SELECTED_BRAND_NAMES } from '../brand-defaults';
import { useBrandMetaAll } from '../useBrandMetaAll';

type DataType = 'production' | 'retail';

const emit = defineEmits<{
  change: [
    payload: {
      brands: string[];
      dataType: DataType;
      granularity: BrandTrendGranularity;
    },
  ];
}>();

const granularity = ref<BrandTrendGranularity>('recentYear');
const dataType = ref<DataType>('retail');
const selectedBrands = ref<string[]>([...DEFAULT_SELECTED_BRAND_NAMES]);
const brandOptionsLoaded = ref(false);

const { brandOptions, brandMetaLoading, ensureLoaded } = useBrandMetaAll();

function emitFilterChange() {
  emit('change', {
    granularity: granularity.value,
    dataType: dataType.value,
    brands: selectedBrands.value,
  });
}

async function initializeFromMeta() {
  brandOptionsLoaded.value = false;
  try {
    await ensureLoaded();
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
  } catch (error) {
    selectedBrands.value = [];
    console.error('[BrandSelectBar] ensureLoaded failed', error);
  } finally {
    brandOptionsLoaded.value = true;
    emitFilterChange();
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
    if (!brandOptionsLoaded.value) {
      return;
    }
    emitFilterChange();
  },
  { deep: true },
);

initializeFromMeta();
</script>

<template>
  <div class="mb-4 flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.trend.selectBrands') }}</span>
      <Select
        :value="selectedBrands"
        :options="brandOptions"
        :loading="brandMetaLoading"
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
        <RadioButton value="recentYear">{{ $t('sales.brand.trend.recentYear') }}</RadioButton>
        <RadioButton value="recentTwoYears">{{ $t('sales.brand.trend.recentTwoYears') }}</RadioButton>
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

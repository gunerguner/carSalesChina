<script lang="ts" setup>
import { RadioGroup, RadioButton, Select } from 'tdesign-vue-next';
import { ref, watch } from 'vue';

import { $t } from '#/locales';

import { getBrandRankingApi } from '#/api/sales/brand';

const granularity = ref<'monthly' | 'yearly'>('monthly');
const dataType = ref<'retail' | 'wholesale' | 'production'>('retail');
const selectedBrands = ref<string[]>([]);

const brandOptions = ref<{ label: string; value: string }[]>([]);
const brandLoading = ref(false);

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

const emit = defineEmits<{
  change: [payload: { granularity: 'monthly' | 'yearly'; dataType: 'retail' | 'wholesale' | 'production'; brands: string[] }];
}>();

async function fetchBrandOptions() {
  brandLoading.value = true;
  try {
    const params: any = {
      year: currentYear,
      month: currentMonth,
      data_type: dataType.value,
      top_n: 50,
    };
    const res: any = await getBrandRankingApi(params);
    const list = res?.data ?? (Array.isArray(res) ? res : []);
    if (Array.isArray(list)) {
      brandOptions.value = list.map((item: any) => ({
        label: item.brand_name,
        value: item.brand_name,
      }));
    }
  } finally {
    brandLoading.value = false;
  }
}

function handleBrandsChange(val: any) {
  const arr = Array.isArray(val) ? val : [val];
  if (arr.length > 2) {
    selectedBrands.value = arr.slice(-2);
  } else {
    selectedBrands.value = arr;
  }
}

watch([granularity, dataType, selectedBrands], () => {
  emit('change', {
    granularity: granularity.value,
    dataType: dataType.value,
    brands: selectedBrands.value,
  });
}, { deep: true });

fetchBrandOptions();
</script>

<template>
  <div class="mb-4 flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.filter.compareBrands') }}</span>
      <Select
        :value="selectedBrands"
        :options="brandOptions"
        :loading="brandLoading"
        :placeholder="$t('sales.brand.filter.comparePlaceholder')"
        multiple
        :max="2"
        filterable
        style="width: 320px"
        @change="handleBrandsChange"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.filter.granularity') }}</span>
      <RadioGroup
        v-model="granularity"
        variant="default-filled"
      >
        <RadioButton value="monthly">{{ $t('sales.brand.filter.granularityMonthly') }}</RadioButton>
        <RadioButton value="yearly">{{ $t('sales.brand.filter.granularityYearly') }}</RadioButton>
      </RadioGroup>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.brand.filter.dataType') }}</span>
      <RadioGroup
        v-model="dataType"
        variant="default-filled"
      >
        <RadioButton value="retail">{{ $t('sales.brand.filter.dataTypeRetail') }}</RadioButton>
        <RadioButton value="wholesale">{{ $t('sales.brand.filter.dataTypeWholesale') }}</RadioButton>
        <RadioButton value="production">{{ $t('sales.brand.filter.dataTypeProduction') }}</RadioButton>
      </RadioGroup>
    </div>
  </div>
</template>

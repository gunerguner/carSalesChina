<script setup lang="ts">
import type { MarketPeriodGranularity } from '../types';

import { computed } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import { $t } from '#/locales';

export type { MarketPeriodGranularity };

const levelType = defineModel<string>('levelType', { required: true });
const dataType = defineModel<'production' | 'retail'>('dataType', {
  required: true,
});
const period = defineModel<MarketPeriodGranularity>('period', {
  required: true,
});

const levelOptions = computed(() => [
  { label: $t('sales.market.filter.levelAll'), value: 'all' },
  { label: $t('sales.market.filter.levelNev'), value: 'nev' },
  { label: $t('sales.market.filter.levelBev'), value: 'bev' },
]);

const dataTypeOptions = computed(() => [
  { label: $t('sales.market.filter.dataTypeRetail'), value: 'retail' },
  { label: $t('sales.market.filter.dataTypeProduction'), value: 'production' },
]);

const periodOptions = computed(() => [
  { label: $t('sales.market.monthly.title'), value: 'monthly' as const },
  { label: $t('sales.market.quarterly.title'), value: 'quarterly' as const },
  { label: $t('sales.market.yearly.title'), value: 'yearly' as const },
]);
</script>

<template>
  <div class="flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="sales-filter-label">{{
        $t('sales.market.filter.levelType')
      }}</span>
      <Select
        v-model="levelType"
        :options="levelOptions"
        style="width: 180px"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="sales-filter-label">{{
        $t('sales.market.filter.granularity')
      }}</span>
      <RadioGroup v-model="period" variant="default-filled">
        <RadioButton
          v-for="opt in periodOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </RadioButton>
      </RadioGroup>
    </div>
    <div class="flex items-center gap-2">
      <span class="sales-filter-label">{{
        $t('sales.market.filter.dataType')
      }}</span>
      <RadioGroup v-model="dataType" variant="default-filled">
        <RadioButton
          v-for="opt in dataTypeOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </RadioButton>
      </RadioGroup>
    </div>
  </div>
</template>

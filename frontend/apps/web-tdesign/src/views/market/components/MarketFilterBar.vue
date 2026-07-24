<script setup lang="ts">
import type { MarketPeriodGranularity } from '../types';

import type { DataType, LevelType } from '#/utils/types';

import { computed } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import MetricTooltip from '#/components/MetricTooltip.vue';
import { $t } from '#/locales';

export type { MarketPeriodGranularity };

const levelType = defineModel<LevelType>('levelType', { required: true });
const dataType = defineModel<DataType>('dataType', {
  required: true,
});
const period = defineModel<MarketPeriodGranularity>('period', {
  required: true,
});

const levelOptions = computed(() => [
  { label: $t('pages.market.filter.levelAll'), value: 'all' as const },
  { label: $t('pages.market.filter.levelNev'), value: 'nev' as const },
  { label: $t('pages.market.filter.levelBev'), value: 'bev' as const },
]);

const dataTypeOptions = computed(() => [
  { label: $t('pages.market.filter.dataTypeRetail'), value: 'retail' as const },
  {
    label: $t('pages.market.filter.dataTypeProduction'),
    value: 'production' as const,
  },
  {
    label: $t('pages.market.filter.dataTypeExport'),
    value: 'export' as const,
  },
]);

const periodOptions = computed(() => [
  { label: $t('pages.market.monthly.title'), value: 'monthly' as const },
  { label: $t('pages.market.quarterly.title'), value: 'quarterly' as const },
  { label: $t('pages.market.yearly.title'), value: 'yearly' as const },
]);
</script>

<template>
  <div class="flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="filter-label">{{
        $t('pages.market.filter.levelType')
      }}</span>
      <Select
        v-model="levelType"
        :options="levelOptions"
        style="width: 180px"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="filter-label">{{
        $t('pages.market.filter.granularity')
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
      <span class="filter-label">{{ $t('pages.market.filter.dataType') }}</span>
      <RadioGroup v-model="dataType" variant="default-filled">
        <RadioButton
          v-for="opt in dataTypeOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </RadioButton>
      </RadioGroup>
      <MetricTooltip :content="$t('pages.market.tooltip.dataType')" />
    </div>
  </div>
</template>

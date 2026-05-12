<script lang="ts" setup>
import { computed } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import { $t } from '#/locales';

const levelType = defineModel<string>('levelType', { required: true });
const dataType = defineModel<'production' | 'retail'>('dataType', { required: true });

const levelOptions = computed(() => [
  { label: $t('sales.market.filter.levelAll'), value: 'all' },
  { label: $t('sales.market.filter.levelNev'), value: 'nev' },
  { label: $t('sales.market.filter.levelBev'), value: 'bev' },
]);

const dataTypeOptions = computed(() => [
  { label: $t('sales.market.filter.dataTypeRetail'), value: 'retail' },
  { label: $t('sales.market.filter.dataTypeProduction'), value: 'production' },
]);
</script>

<template>
  <div class="mb-4 flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.market.filter.levelType') }}</span>
      <Select
        v-model="levelType"
        :options="levelOptions"
        style="width: 180px"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.market.filter.dataType') }}</span>
      <RadioGroup
        v-model="dataType"
        variant="default-filled"
      >
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

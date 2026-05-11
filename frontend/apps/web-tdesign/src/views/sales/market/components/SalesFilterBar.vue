<script lang="ts" setup>
import { computed } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import { $t } from '#/locales';

export interface FilterState {
  energyType: string;
  dataType: 'production' | 'retail' | 'wholesale';
}

const props = defineProps<{
  dataType: 'production' | 'retail' | 'wholesale';
  energyType: string;
}>();

const emit = defineEmits<{
  'update:dataType': [value: 'production' | 'retail' | 'wholesale'];
  'update:energyType': [value: string];
}>();

const energyOptions = computed(() => [
  { label: $t('sales.market.filter.energyAll'), value: 'all' },
  { label: $t('sales.market.filter.energyFuel'), value: 'fuel' },
  { label: $t('sales.market.filter.energyBev'), value: 'bev' },
  { label: $t('sales.market.filter.energyPhev'), value: 'phev' },
  { label: $t('sales.market.filter.energyHev'), value: 'hybrid' },
]);

const dataTypeOptions = computed(() => [
  { label: $t('sales.market.filter.dataTypeRetail'), value: 'retail' },
  { label: $t('sales.market.filter.dataTypeWholesale'), value: 'wholesale' },
  { label: $t('sales.market.filter.dataTypeProduction'), value: 'production' },
]);
</script>

<template>
  <div class="mb-4 flex flex-wrap items-center gap-4">
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.market.filter.energyType') }}</span>
      <Select
        :value="props.energyType"
        :options="energyOptions"
        style="width: 180px"
        @change="emit('update:energyType', $event as string)"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.market.filter.dataType') }}</span>
      <RadioGroup
        :value="props.dataType"
        variant="default-filled"
        @change="emit('update:dataType', $event as 'retail' | 'wholesale' | 'production')"
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

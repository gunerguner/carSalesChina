<script lang="ts" setup>
import { computed } from 'vue';

import { RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import { $t } from '#/locales';

export interface FilterState {
  levelType: string;
  dataType: 'production' | 'retail';
}

const props = defineProps<{
  dataType: 'production' | 'retail';
  levelType: string;
}>();

const emit = defineEmits<{
  'update:dataType': [value: 'production' | 'retail'];
  'update:levelType': [value: string];
}>();

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
        :value="props.levelType"
        :options="levelOptions"
        style="width: 180px"
        @change="emit('update:levelType', $event as string)"
      />
    </div>
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600">{{ $t('sales.market.filter.dataType') }}</span>
      <RadioGroup
        :value="props.dataType"
        variant="default-filled"
        @change="emit('update:dataType', $event as 'retail' | 'production')"
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
<script setup lang="ts">
import type { NevTrendValueKey } from './nevTrendChart';

import type { AnalysisPeriodRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';

import { buildNevTrendChartOption } from './nevTrendChart';

const props = defineProps<{
  color: string;
  data: AnalysisPeriodRecord[];
  label: string;
  valueKey: NevTrendValueKey;
}>();

const chartOption = computed(() =>
  buildNevTrendChartOption(
    {
      color: props.color,
      data: props.data,
      label: props.label,
      valueKey: props.valueKey,
    },
    $t,
  ),
);
</script>

<template>
  <ChartCard height-class="h-72" :option="chartOption" />
</template>

<script setup lang="ts">
import type { BrandSeriesRecord } from '../types';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';

import { buildBrandTrendChartOption } from './brandTrendChart';

const props = defineProps<{
  data: BrandSeriesRecord[];
  timeLabels: string[];
}>();

const chartOption = computed(() =>
  buildBrandTrendChartOption(
    { data: props.data, timeLabels: props.timeLabels },
    preferences.app.locale,
    $t,
  ),
);
</script>

<template>
  <ChartCard :option="chartOption" />
</template>

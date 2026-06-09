<script setup lang="ts">
import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';

import { buildOriginShareChartOption } from './originShareChart';

const props = defineProps<{
  data: OriginShareTrendRecord[];
}>();

const chartOption = computed(() => buildOriginShareChartOption(props.data, $t));
</script>

<template>
  <ChartCard :option="chartOption" />
</template>

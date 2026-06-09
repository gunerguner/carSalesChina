<script setup lang="ts">
import type { MarketTrendChartInput } from './marketTrendChart';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';

import { buildMarketTrendChartOption } from './marketTrendChart';

const props = defineProps<MarketTrendChartInput>();

const chartOption = computed(() =>
  buildMarketTrendChartOption(props, preferences.app.locale, $t),
);
</script>

<template>
  <ChartCard :option="chartOption" />
</template>

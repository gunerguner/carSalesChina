<script lang="ts" setup>
import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';

import { buildMarketTrendChartOption, type MarketTrendChartInput } from './marketTrendChart';

const props = defineProps<MarketTrendChartInput>();

const chartOption = computed(() =>
  buildMarketTrendChartOption(props as MarketTrendChartInput, preferences.app.locale, $t),
);
</script>

<template>
  <ChartCard :option="chartOption" />
</template>

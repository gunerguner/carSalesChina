<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';
import { preferences } from '@vben/preferences';

import { $t } from '#/locales';

import { buildMarketTrendChartOption, type MarketTrendChartInput } from './marketTrendChart';

const props = defineProps<MarketTrendChartInput>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render() {
  renderEcharts(buildMarketTrendChartOption(props as MarketTrendChartInput, preferences.app.locale, $t));
}

watch(() => props.data, render);
onMounted(render);
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

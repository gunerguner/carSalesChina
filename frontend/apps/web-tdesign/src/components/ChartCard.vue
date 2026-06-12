<script setup lang="ts">
import type { EchartsUIType, ECOption } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = withDefaults(
  defineProps<{
    heightClass?: string;
    /** ECharts option object; replace reference when data changes for reliable updates. */
    option: ECOption;
  }>(),
  { heightClass: 'h-80' },
);

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function draw() {
  // ECOption (compose) is runtime-compatible with renderEcharts; echarts ships duplicate type paths.
  renderEcharts(props.option as never);
}

watch(() => props.option, draw);
onMounted(draw);
</script>

<template>
  <div class="chart-wrap w-full" :class="heightClass">
    <EchartsUI ref="chartRef" />
  </div>
</template>

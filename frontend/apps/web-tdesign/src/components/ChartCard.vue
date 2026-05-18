<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = withDefaults(
  defineProps<{
    heightClass?: string;
    /** ECharts option object; replace reference when data changes for reliable updates. */
    option: Record<string, unknown>;
  }>(),
  { heightClass: 'h-80' },
);

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function draw() {
  renderEcharts(props.option as never);
}

watch(() => props.option, draw, { deep: true });
onMounted(draw);
</script>

<template>
  <div class="w-full" :class="heightClass">
    <EchartsUI ref="chartRef" />
  </div>
</template>

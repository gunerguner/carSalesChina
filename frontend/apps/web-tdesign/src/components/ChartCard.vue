<script setup lang="ts">
import type { Ref } from 'vue';

import type { EchartsUIType, ECOption } from '@vben/plugins/echarts';

import { onMounted, useTemplateRef, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const {
  heightClass = 'h-80',
  /** ECharts option object; replace reference when data changes for reliable updates. */
  option,
} = defineProps<{
  heightClass?: string;
  option: ECOption;
}>();

// 模板 ref 集中管理：避免与响应式 ref 名字混淆
const chartRef = useTemplateRef<typeof EchartsUI>('chartRef');
// useEcharts 期望 Ref<EchartsUIType>，useTemplateRef 返回 ShallowRef<...| null>，做一次类型对齐
const { renderEcharts } = useEcharts(chartRef as unknown as Ref<EchartsUIType>);

function draw() {
  // ECOption (compose) is runtime-compatible with renderEcharts; echarts ships duplicate type paths.
  renderEcharts(option as never);
}

watch(() => option, draw);
onMounted(draw);
</script>

<template>
  <div class="chart-wrap w-full" :class="heightClass">
    <EchartsUI ref="chartRef" />
  </div>
</template>

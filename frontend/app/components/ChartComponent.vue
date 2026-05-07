<template>
  <div class="chart-card page-card">
    <div ref="chartRef" :style="{ width: '100%', height: props.height + 'px' }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps<{ option: any; height?: number }>();
const chartRef = ref<any>(null);
let chartInstance: echarts.ECharts | null = null;

function initChart() {
  if (!chartRef.value) return;
  if (chartInstance) {
    chartInstance.dispose();
  }
  chartInstance = echarts.init(chartRef.value);
  chartInstance.setOption(props.option, true);
}

onMounted(() => {
  nextTick(() => initChart());
});

watch(
  () => props.option,
  () => {
    if (chartInstance) {
      chartInstance.setOption(props.option, true);
    }
  },
  { deep: true }
);

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
</script>
<script setup lang="ts">
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { YearlyTrendRecord } from '../useMarketData';

import { ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = defineProps<{
  data: YearlyTrendRecord[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render(data: YearlyTrendRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts({
      animation: false,
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [],
    });
    return;
  }

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: data.map((r) => String(r.year)) },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (val: number) => `${(val / 10_000).toFixed(0)}万` },
    },
    series: [
      {
        name: '销量',
        type: 'bar',
        data: data.map((r) => r.sales),
        itemStyle: { color: '#5470c6' },
        label: { show: true, position: 'top', formatter: '{c}' },
      },
    ],
  });
}

watch(() => props.data, (val) => render(val), { immediate: true });
</script>

<template>
  <EchartsUI ref="chartRef" class="h-80" />
</template>

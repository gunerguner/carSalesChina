<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = defineProps<{
  data: any[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const ORIGIN_LABELS: Record<string, string> = {
  domestic: '自主',
  german: '德系',
  japanese: '日系',
  american: '美系',
  european: '欧系',
  korean: '韩系',
  french: '法系',
};

const ORIGIN_COLORS: Record<string, string> = {
  domestic: '#5470c6',
  german: '#91cc75',
  japanese: '#fac858',
  american: '#ee6666',
  european: '#73c0de',
  korean: '#3ba272',
  french: '#9a6bef',
};

function render(data: any[]) {
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

  const timeLabels = data.map((item: any) =>
    `${item.year}-${String(item.month).padStart(2, '0')}`
  );

  const originKeys = Object.keys(ORIGIN_LABELS);
  const series = originKeys.map((key) => ({
    name: ORIGIN_LABELS[key],
    type: 'bar' as const,
    stack: 'total',
    data: data.map((item: any) => item[key] == null ? 0 : +(item[key]).toFixed(2)),
    itemStyle: { color: ORIGIN_COLORS[key] },
    emphasis: { focus: 'series' as const },
  }));

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: Object.values(ORIGIN_LABELS), bottom: 0, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series,
  });
}

watch(() => props.data, (val) => render(val), { deep: true });
onMounted(() => render(props.data));
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

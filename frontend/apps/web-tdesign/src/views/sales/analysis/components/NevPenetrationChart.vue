<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = defineProps<{
  data: any[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

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
  const penetrationRates = data.map((item: any) =>
    item.nev_penetration_rate == null ? 0 : +(item.nev_penetration_rate).toFixed(2)
  );

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => {
      const p = Array.isArray(params) ? params[0] : params;
      return `${p.axisValue}<br/>NEV渗透率: ${p.value}%`;
    }},
    grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' }, max: (value: any) => Math.min(Math.ceil(value.max * 1.2), 100) },
    series: [
      {
        name: 'NEV渗透率',
        type: 'line',
        data: penetrationRates,
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#5470c6' },
      },
    ],
  });
}

watch(() => props.data, (val) => render(val), { deep: true, immediate: true });
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

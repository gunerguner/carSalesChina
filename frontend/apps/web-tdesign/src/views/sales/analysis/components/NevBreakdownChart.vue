<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getNevBreakdownApi } from '#/api/sales/analysis';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

async function fetchAndRender() {
  loading.value = true;
  try {
    const data = await getNevBreakdownApi({ granularity: 'monthly' });

    if (!data || !Array.isArray(data) || data.length === 0) {
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

    const bevData = data.map((item: any) => item.bev_ratio == null ? 0 : +(item.bev_ratio).toFixed(2));
    const phevData = data.map((item: any) => item.phev_ratio == null ? 0 : +(item.phev_ratio).toFixed(2));
    const hevData = data.map((item: any) => item.hybrid_ratio == null ? 0 : +(item.hybrid_ratio).toFixed(2));

    renderEcharts({
      animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['BEV', 'PHEV', 'HEV'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: timeLabels },
      yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
      series: [
        {
          name: 'BEV',
          type: 'bar',
          stack: 'total',
          data: bevData,
          itemStyle: { color: '#5470c6' },
        },
        {
          name: 'PHEV',
          type: 'bar',
          stack: 'total',
          data: phevData,
          itemStyle: { color: '#91cc75' },
        },
        {
          name: 'HEV',
          type: 'bar',
          stack: 'total',
          data: hevData,
          itemStyle: { color: '#fac858' },
        },
      ],
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchAndRender());
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

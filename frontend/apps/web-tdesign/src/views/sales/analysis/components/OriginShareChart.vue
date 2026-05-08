<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getOriginShareTrendApi } from '#/api/sales/analysis';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

const ORIGIN_LABELS: Record<string, string> = {
  domestic: '自主',
  german: '德系',
  japanese: '日系',
  american: '美系',
  european: '欧系',
  korean: '韩系',
  other: '其他',
};

const ORIGIN_COLORS: Record<string, string> = {
  domestic: '#5470c6',
  german: '#91cc75',
  japanese: '#fac858',
  american: '#ee6666',
  european: '#73c0de',
  korean: '#3ba272',
  other: '#fc8452',
};

async function fetchAndRender() {
  loading.value = true;
  try {
    const data = await getOriginShareTrendApi({ granularity: 'monthly' });

    if (!data || !Array.isArray(data) || data.length === 0) {
      renderEcharts({
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
      data: data.map((item: any) => item[key] != null ? +(item[key]).toFixed(2) : 0),
      itemStyle: { color: ORIGIN_COLORS[key] },
      emphasis: { focus: 'series' as const },
    }));

    renderEcharts({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: Object.values(ORIGIN_LABELS), bottom: 0, type: 'scroll' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: timeLabels },
      yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
      series,
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

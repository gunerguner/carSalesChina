<script setup lang="ts">
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getMarketTrendApi } from '#/api/sales/market';

const props = defineProps<{
  dataType: 'production' | 'retail';
  levelType: string;
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

async function fetchAndRender() {
  loading.value = true;
  try {
    const data = await getMarketTrendApi({
      level_type: props.levelType,
      granularity: 'yearly',
      data_type: props.dataType,
      date_type: 'monthly',
    });

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

    const years = data.map((item: any) => String(item.year));
    const sales = data.map((item: any) => item.sales ?? 0);

    renderEcharts({
      animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: years },
      yAxis: { type: 'value', axisLabel: { formatter: (val: number) => `${(val / 10_000).toFixed(0)}万` } },
      series: [
        {
          name: '销量',
          type: 'bar',
          data: sales,
          itemStyle: { color: '#5470c6' },
          label: { show: true, position: 'top', formatter: `{c}` },
        },
      ],
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchAndRender());

watch([() => props.levelType, () => props.dataType], () => fetchAndRender());
</script>

<template>
  <EchartsUI ref="chartRef" :loading="loading" class="h-80" />
</template>
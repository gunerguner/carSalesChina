<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getMarketTrendApi } from '#/api/sales/market';

const props = defineProps<{
  energyType: string;
  dataType: 'retail' | 'wholesale' | 'production';
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

const salesFieldMap: Record<string, string> = {
  all: 'total_sales',
  fuel: 'ice_sales',
  bev: 'bev_sales',
  phev: 'phev_sales',
  hybrid: 'hybrid_sales',
};

async function fetchAndRender() {
  loading.value = true;
  try {
    const data = await getMarketTrendApi({
      energy_type: props.energyType,
      granularity: 'yearly',
      data_type: props.dataType,
    });

    if (!data || !Array.isArray(data) || data.length === 0) {
      renderEcharts({
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
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: years },
      yAxis: { type: 'value', axisLabel: { formatter: (val: number) => val >= 10000 ? `${(val / 10000).toFixed(0)}万` : String(val) } },
      series: [
        {
          type: 'bar',
          data: sales,
          itemStyle: { color: '#5470c6' },
          barMaxWidth: 60,
        },
      ],
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchAndRender());

watch([() => props.energyType, () => props.dataType], () => fetchAndRender());
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

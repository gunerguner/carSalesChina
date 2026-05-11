<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getMarketTrendApi } from '#/api/sales/market';

const props = defineProps<{
  dataType: 'production' | 'retail' | 'wholesale';
  energyType: string;
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'];

async function fetchAndRender() {
  loading.value = true;
  try {
    const data = await getMarketTrendApi({
      energy_type: props.energyType,
      granularity: 'monthly',
      data_type: props.dataType,
      years: 3,
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

    const yearDataMap = new Map<number, number[]>();
    for (const item of data) {
      const year = item.year;
      const month = item.month;
      if (!yearDataMap.has(year)) {
        yearDataMap.set(year, Array.from<number>({length: 12}).fill(0));
      }
      const arr = yearDataMap.get(year)!;
      arr[month - 1] = item.sales ?? 0;
    }

    const years = [...yearDataMap.keys()].toSorted((a, b) => a - b);
    const months = Array.from({ length: 12 }, (_, i) => `${i + 1}月`);

    const series = years.map((year, index) => ({
      name: `${year}`,
      type: 'line' as const,
      data: yearDataMap.get(year),
      smooth: true,
      itemStyle: { color: COLORS[index % COLORS.length] },
    }));

    renderEcharts({
      animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: years.map(String), bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: months, boundaryGap: false },
      yAxis: { type: 'value', axisLabel: { formatter: (val: number) => val >= 10_000 ? `${(val / 10_000).toFixed(0)}万` : String(val) } },
      series,
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

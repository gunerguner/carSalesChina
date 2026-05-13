<script setup lang="ts">
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { YearlyTrendRecord } from '../useMarketData';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';
import { preferences } from '@vben/preferences';

const props = defineProps<{
  data: YearlyTrendRecord[];
}>();

function yearAxisLabel(r: YearlyTrendRecord): string {
  return preferences.app.locale === 'zh-CN' ? `${r.year}年` : String(r.year);
}

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
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      formatter: (params: any) => {
        const arr = Array.isArray(params) ? params : [params];
        if (arr.length === 0) return '';
        const head = arr[0];
        const label = head.axisValueLabel ?? head.name ?? '';
        const body = arr
          .map((p: any) => {
            const v = Math.round(Number(p.value)).toLocaleString();
            return `${p.marker}${p.seriesName}: ${v}`;
          })
          .join('<br/>');
        return `${label}<br/>${body}`;
      },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.map((r) => yearAxisLabel(r)) },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (val: number) => `${(val / 10_000).toFixed(0)}万` },
    },
    series: [
      {
        name: '销量',
        type: 'line',
        smooth: true,
        data: data.map((r) => r.sales),
        itemStyle: { color: '#5470c6' },
      },
    ],
  });
}

watch(() => props.data, (val) => render(val));
onMounted(() => render(props.data));
</script>

<template>
  <EchartsUI ref="chartRef" class="h-80" />
</template>

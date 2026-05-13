<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { computed, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { $t } from '#/locales';

interface BrandSeriesPoint {
  sales: number;
  time: string;
}

interface BrandSeriesRecord {
  brand_name: string;
  points: BrandSeriesPoint[];
}

const props = defineProps<{
  data: BrandSeriesRecord[];
  loading?: boolean;
  timeLabels: string[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const COLORS = ['#5470c6', '#ee6666', '#73c0de'];

const chartSeries = computed(() =>
  props.data.map((brand, index) => {
    const map = new Map<string, number>();
    for (const point of brand.points ?? []) {
      map.set(point.time, point.sales ?? 0);
    }
    return {
      data: props.timeLabels.map((time) => map.get(time) ?? 0),
      itemStyle: { color: COLORS[index % COLORS.length] },
      name: brand.brand_name,
      smooth: true,
      type: 'line' as const,
    };
  }),
);

watch(
  [() => props.data, () => props.timeLabels, () => props.loading],
  () => {
    if (props.loading) {
      renderEcharts({
        animation: false,
        title: {
          left: 'center',
          text: $t('common.loading'),
          textStyle: { color: '#999', fontSize: 14 },
          top: 'center',
        },
        series: [],
        xAxis: { data: [], type: 'category' },
        yAxis: { type: 'value' },
      });
      return;
    }

    if (props.data.length === 0 || props.timeLabels.length === 0) {
      renderEcharts({
        animation: false,
        title: {
          left: 'center',
          text: $t('sales.brand.trend.noData'),
          textStyle: { color: '#999', fontSize: 14 },
          top: 'center',
        },
        series: [],
        xAxis: { data: [], type: 'category' },
        yAxis: { type: 'value' },
      });
      return;
    }

    renderEcharts({
      animation: false,
      grid: { bottom: '14%', containLabel: true, left: '3%', right: '4%', top: '8%' },
      legend: { bottom: 0, data: props.data.map((item) => item.brand_name) },
      series: chartSeries.value,
      tooltip: { axisPointer: { type: 'shadow' }, trigger: 'axis' },
      xAxis: { boundaryGap: false, data: props.timeLabels, type: 'category' },
      yAxis: {
        axisLabel: {
          formatter: (val: number) =>
            val >= 10_000 ? `${(val / 10_000).toFixed(0)}万` : String(val),
        },
        type: 'value',
      },
    });
  },
  { deep: true, immediate: true },
);
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

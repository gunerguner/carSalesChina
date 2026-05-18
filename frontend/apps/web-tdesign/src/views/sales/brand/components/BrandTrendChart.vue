<script lang="ts" setup>
import type { BrandSeriesRecord } from '../types';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';
import {
  BRAND_LINE_PALETTE_INDICES,
  formatSalesAxisLabel,
  getChartPaletteColor,
  getEmptyChartOption,
} from '#/utils/chart';

const props = defineProps<{
  data: BrandSeriesRecord[];
  loading?: boolean;
  timeLabels: string[];
}>();

const chartSeries = computed(() =>
  props.data.map((brand, index) => {
    const map = new Map<string, number>();
    for (const point of brand.points ?? []) {
      map.set(point.time, point.sales ?? 0);
    }
    const paletteIndex =
      BRAND_LINE_PALETTE_INDICES[index % BRAND_LINE_PALETTE_INDICES.length]!;
    return {
      data: props.timeLabels.map((time) => map.get(time) ?? 0),
      itemStyle: { color: getChartPaletteColor(paletteIndex) },
      name: brand.brand_name,
      smooth: true,
      type: 'line' as const,
    };
  }),
);

const chartOption = computed(() => {
  if (props.loading) {
    return getEmptyChartOption($t('common.loading'));
  }

  if (props.data.length === 0 || props.timeLabels.length === 0) {
    return getEmptyChartOption($t('sales.brand.trend.noData'));
  }

  return {
    animation: false,
    grid: { bottom: '14%', containLabel: true, left: '3%', right: '4%', top: '8%' },
    legend: { bottom: 0, data: props.data.map((item) => item.brand_name) },
    series: chartSeries.value,
    tooltip: { axisPointer: { type: 'shadow' }, trigger: 'axis' },
    xAxis: { boundaryGap: false, data: props.timeLabels, type: 'category' },
    yAxis: {
      axisLabel: {
        formatter: (val: number) =>
          formatSalesAxisLabel(val, preferences.app.locale),
      },
      type: 'value',
    },
  };
});
</script>

<template>
  <ChartCard :option="chartOption" />
</template>

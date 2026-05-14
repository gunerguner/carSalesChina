<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { MonthlyTrendRecord } from '../useMarketData';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';
import { preferences } from '@vben/preferences';

import { $t } from '#/locales';

import {
  formatSalesAxisLabel,
  getEmptyChartOption,
} from '#/views/sales/utils/chart-utils';
import { getLocalizedMonthLabels } from '#/views/sales/utils/period-utils';

const props = defineProps<{
  data: MonthlyTrendRecord[];
}>();

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'];

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render(data: MonthlyTrendRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts(getEmptyChartOption($t('sales.common.noData')));
    return;
  }

  const yearDataMap = new Map<number, number[]>();
  for (const item of data) {
    if (!yearDataMap.has(item.year)) {
      yearDataMap.set(item.year, Array.from<number>({ length: 12 }).fill(0));
    }
    yearDataMap.get(item.year)![item.month - 1] = item.sales;
  }

  const years = [...yearDataMap.keys()].toSorted((a, b) => a - b);
  const months = getLocalizedMonthLabels(preferences.app.locale);

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: years.map(String), bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: months, boundaryGap: false },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val: number) =>
          formatSalesAxisLabel(val, preferences.app.locale),
      },
    },
    series: years.map((year, index) => ({
      name: `${year}`,
      type: 'line' as const,
      data: yearDataMap.get(year),
      smooth: true,
      itemStyle: { color: COLORS[index % COLORS.length] },
    })),
  });
}

watch(() => props.data, render);
onMounted(() => render(props.data));
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

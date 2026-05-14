<script setup lang="ts">
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { YearlyTrendRecord } from '../useMarketData';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';
import { preferences } from '@vben/preferences';

import { $t } from '#/locales';
import {
  formatSalesAxisLabel,
  getEmptyChartOption,
  lineSeriesTooltipFormatter,
} from '#/views/sales/utils/chart-utils';
import { formatYearPeriod } from '#/views/sales/utils/period-utils';

const props = defineProps<{
  data: YearlyTrendRecord[];
}>();

function yearAxisLabel(r: YearlyTrendRecord): string {
  return formatYearPeriod(r.year, preferences.app.locale);
}

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render(data: YearlyTrendRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts(getEmptyChartOption($t('sales.common.noData')));
    return;
  }

  renderEcharts({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      formatter: lineSeriesTooltipFormatter,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.map((r) => yearAxisLabel(r)) },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (val: number) =>
          formatSalesAxisLabel(val, preferences.app.locale),
      },
    },
    series: [
      {
        name: $t('sales.market.yearly.sales'),
        type: 'line',
        smooth: true,
        data: data.map((r) => r.sales),
        itemStyle: { color: '#5470c6' },
      },
    ],
  });
}

watch(() => props.data, render);
onMounted(() => render(props.data));
</script>

<template>
  <EchartsUI ref="chartRef" class="h-80" />
</template>

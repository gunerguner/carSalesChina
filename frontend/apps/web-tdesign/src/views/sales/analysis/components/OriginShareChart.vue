<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { $t } from '#/locales';
import { getEmptyChartOption } from '#/views/sales/utils/chart-utils';

const props = defineProps<{
  data: OriginShareTrendRecord[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const ORIGIN_KEYS = [
  'domestic',
  'german',
  'japanese',
  'american',
  'european',
  'korean',
  'french',
] as const;

const ORIGIN_COLORS: Record<string, string> = {
  domestic: '#5470c6',
  german: '#91cc75',
  japanese: '#fac858',
  american: '#ee6666',
  european: '#73c0de',
  korean: '#3ba272',
  french: '#9a6bef',
};

function render(data: OriginShareTrendRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts(getEmptyChartOption($t('sales.common.noData')));
    return;
  }

  const timeLabels = data.map((item) =>
    `${item.year}-${String(item.month).padStart(2, '0')}`
  );

  const labels = {
    domestic: $t('sales.analysis.origin.domesticLabel'),
    german: $t('sales.analysis.origin.germanLabel'),
    japanese: $t('sales.analysis.origin.japaneseLabel'),
    american: $t('sales.analysis.origin.americanLabel'),
    european: $t('sales.analysis.origin.europeanLabel'),
    korean: $t('sales.analysis.origin.koreanLabel'),
    french: $t('sales.analysis.origin.frenchLabel'),
  };
  const series = ORIGIN_KEYS.map((key) => ({
    name: labels[key],
    type: 'bar' as const,
    stack: 'total',
    data: data.map((item) => item[key] == null ? 0 : +(item[key]).toFixed(2)),
    itemStyle: { color: ORIGIN_COLORS[key] },
    emphasis: { focus: 'series' as const },
  }));

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: Object.values(labels), bottom: 0, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series,
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

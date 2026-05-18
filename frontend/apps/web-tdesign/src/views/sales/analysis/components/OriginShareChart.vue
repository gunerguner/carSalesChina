<script lang="ts" setup>
import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';
import {
  getEmptyChartOption,
  ORIGIN_COLORS,
  ORIGIN_KEYS,
  type OriginShareKey,
} from '#/utils/chart';
import { toMonthKey } from '#/utils/period';

const props = defineProps<{
  data: OriginShareTrendRecord[];
}>();

const chartOption = computed(() => {
  const data = props.data;
  if (!data || data.length === 0) {
    return getEmptyChartOption($t('sales.common.noData'));
  }

  const timeLabels = data.map((item) => toMonthKey(item.year, item.month));

  const labels = {
    domestic: $t('sales.analysis.origin.domesticLabel'),
    german: $t('sales.analysis.origin.germanLabel'),
    japanese: $t('sales.analysis.origin.japaneseLabel'),
    american: $t('sales.analysis.origin.americanLabel'),
    european: $t('sales.analysis.origin.europeanLabel'),
    korean: $t('sales.analysis.origin.koreanLabel'),
    french: $t('sales.analysis.origin.frenchLabel'),
  };
  const series = ORIGIN_KEYS.map((key: OriginShareKey) => ({
    name: labels[key],
    type: 'bar' as const,
    stack: 'total',
    data: data.map((item) => item[key] == null ? 0 : +(item[key]).toFixed(2)),
    itemStyle: { color: ORIGIN_COLORS[key] },
    emphasis: { focus: 'series' as const },
  }));

  return {
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: Object.values(labels), bottom: 0, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series,
  };
});
</script>

<template>
  <ChartCard :option="chartOption" />
</template>

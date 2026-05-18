<script lang="ts" setup>
import type { AnalysisPeriodRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import ChartCard from '#/components/ChartCard.vue';
import { $t } from '#/locales';
import { getEmptyChartOption } from '#/utils/chart';
import { toMonthKey } from '#/utils/period';

const props = defineProps<{
  color: string;
  data: AnalysisPeriodRecord[];
  label: string;
  valueKey: string;
}>();

const chartOption = computed(() => {
  const data = props.data;
  if (!data || data.length === 0) {
    return getEmptyChartOption($t('sales.common.noData'));
  }

  const timeLabels = data.map((item) => toMonthKey(item.year, item.month));
  const values = data.map((item) => {
    const v = (item as unknown as Record<string, null | number>)[props.valueKey];
    return v == null ? 0 : +v.toFixed(2);
  });

  return {
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>${props.label}: ${p.value}%`;
      },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels, boundaryGap: false },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '{value}%' },
      max: (value: any) => Math.min(Math.ceil(value.max * 1.2), 100),
    },
    series: [
      {
        name: props.label,
        type: 'line',
        data: values,
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: props.color },
      },
    ],
  };
});
</script>

<template>
  <ChartCard height-class="h-72" :option="chartOption" />
</template>

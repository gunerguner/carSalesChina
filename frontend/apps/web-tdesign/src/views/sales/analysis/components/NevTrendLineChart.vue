<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { AnalysisPeriodRecord } from '#/api/sales/analysis';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { $t } from '#/locales';
import { getEmptyChartOption } from '#/views/sales/utils/chart-utils';

type DataRecord = AnalysisPeriodRecord & Record<string, null | number>;

const props = defineProps<{
  color: string;
  data: DataRecord[];
  label: string;
  valueKey: string;
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render(data: DataRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts(getEmptyChartOption($t('sales.common.noData')));
    return;
  }

  const timeLabels = data.map(
    (item) => `${item.year}-${String(item.month).padStart(2, '0')}`,
  );
  const values = data.map((item) => {
    const v = item[props.valueKey];
    return v == null ? 0 : +v.toFixed(2);
  });

  renderEcharts({
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
  });
}

watch(() => props.data, render);
onMounted(() => render(props.data));
</script>

<template>
  <div class="h-72 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>

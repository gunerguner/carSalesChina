<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { NevBreakdownRecord } from '#/api/sales/analysis';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { $t } from '#/locales';
import { getEmptyChartOption } from '#/views/sales/utils/chart-utils';

const props = defineProps<{
  data: NevBreakdownRecord[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render(data: NevBreakdownRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts(getEmptyChartOption($t('sales.common.noData')));
    return;
  }

  const timeLabels = data.map((item) =>
    `${item.year}-${String(item.month).padStart(2, '0')}`
  );
  const bevInNevRatios = data.map((item) =>
    item.bev_ratio == null ? 0 : +(item.bev_ratio).toFixed(2)
  );

  renderEcharts({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>${$t('sales.analysis.nev.bevInNevTrendLabel')}: ${p.value}%`;
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
        name: $t('sales.analysis.nev.bevInNevTrendLabel'),
        type: 'line',
        data: bevInNevRatios,
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#91cc75' },
      },
    ],
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

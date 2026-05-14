<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { NevShareTrendRecord } from '#/api/sales/analysis';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { $t } from '#/locales';
import { getEmptyChartOption } from '#/views/sales/utils/chart-utils';

const props = defineProps<{
  data: NevShareTrendRecord[];
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function render(data: NevShareTrendRecord[]) {
  if (!data || data.length === 0) {
    renderEcharts(getEmptyChartOption($t('sales.common.noData')));
    return;
  }

  const timeLabels = data.map((item) =>
    `${item.year}-${String(item.month).padStart(2, '0')}`
  );
  const penetrationRates = data.map((item) =>
    item.nev_penetration_rate == null ? 0 : +(item.nev_penetration_rate).toFixed(2)
  );

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => {
      const p = Array.isArray(params) ? params[0] : params;
      return `${p.axisValue}<br/>${$t('sales.analysis.nev.penetrationRateLabel')}: ${p.value}%`;
    }},
    grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' }, max: (value: any) => Math.min(Math.ceil(value.max * 1.2), 100) },
    series: [
      {
        name: $t('sales.analysis.nev.penetrationRateLabel'),
        type: 'line',
        data: penetrationRates,
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#5470c6' },
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

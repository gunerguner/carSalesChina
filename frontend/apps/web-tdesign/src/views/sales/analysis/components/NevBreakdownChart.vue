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

  const bevData = data.map((item) =>
    item.bev_ratio == null ? 0 : +(item.bev_ratio).toFixed(2),
  );
  const phevData = data.map((item) =>
    item.phev_ratio == null ? 0 : +(item.phev_ratio).toFixed(2),
  );
  const hevData = data.map((item) =>
    item.hybrid_ratio == null ? 0 : +(item.hybrid_ratio).toFixed(2),
  );

  renderEcharts({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      data: [
        $t('sales.analysis.nev.bevShare'),
        $t('sales.analysis.nev.phevShare'),
        $t('sales.analysis.nev.hevShare'),
      ],
      bottom: 0,
    },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: timeLabels },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
    series: [
      {
        name: $t('sales.analysis.nev.bevShare'),
        type: 'bar',
        stack: 'total',
        data: bevData,
        itemStyle: { color: '#5470c6' },
      },
      {
        name: $t('sales.analysis.nev.phevShare'),
        type: 'bar',
        stack: 'total',
        data: phevData,
        itemStyle: { color: '#91cc75' },
      },
      {
        name: $t('sales.analysis.nev.hevShare'),
        type: 'bar',
        stack: 'total',
        data: hevData,
        itemStyle: { color: '#fac858' },
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

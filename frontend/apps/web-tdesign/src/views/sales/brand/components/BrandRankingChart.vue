<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getBrandRankingApi, getBrandRankingYearlyApi } from '#/api/sales/brand';

const props = defineProps<{
  dataType: 'production' | 'retail' | 'wholesale';
  granularity: 'monthly' | 'yearly';
  month: number;
  year: number;
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

function extractList(res: any): any[] {
  if (Array.isArray(res)) return res;
  if (res?.data && Array.isArray(res.data)) return res.data;
  return [];
}

async function fetchAndRender() {
  loading.value = true;
  try {
    let res: any;
    res = await (props.granularity === 'yearly' ? getBrandRankingYearlyApi({
        year: props.year,
        data_type: props.dataType,
        top_n: 15,
      }) : getBrandRankingApi({
        year: props.year,
        month: props.month,
        data_type: props.dataType,
        top_n: 15,
      }));

    const list = extractList(res);

    if (list.length === 0) {
      renderEcharts({
        animation: false,
        title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: [] },
        series: [],
      });
      return;
    }

    const brands = list.map((item: any) => item.brand_name).toReversed();
    const sales = list.map((item: any) => (item.sales_volume ?? item.total_sales ?? item.sales ?? 0)).toReversed();

    renderEcharts({
      animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '15%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
      xAxis: { type: 'value', axisLabel: { formatter: (val: number) => val >= 10_000 ? `${(val / 10_000).toFixed(1)}万` : String(val) } },
      yAxis: { type: 'category', data: brands },
      series: [
        {
          type: 'bar',
          data: sales,
          itemStyle: { color: '#5470c6' },
          barMaxWidth: 30,
        },
      ],
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchAndRender());

watch([() => props.year, () => props.month, () => props.granularity, () => props.dataType], () => fetchAndRender());
</script>

<template>
  <div class="h-96 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>
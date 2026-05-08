<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

import { getBrandCompareTrendApi } from '#/api/sales/brand';

const props = defineProps<{
  brands: string[];
  granularity: 'monthly' | 'yearly';
  dataType: 'retail' | 'wholesale' | 'production';
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(false);

const COLORS = ['#5470c6', '#ee6666'];

function makeTimeKey(item: any): string {
  return props.granularity === 'monthly'
    ? `${item.year}-${String(item.month).padStart(2, '0')}`
    : String(item.year);
}

async function fetchAndRender() {
  if (props.brands.length < 2) {
    renderEcharts({
      title: { text: '请选择2个品牌进行对比', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [],
    });
    return;
  }

  loading.value = true;
  try {
    const data: any = await getBrandCompareTrendApi({
      brand_names: props.brands.join(','),
      data_type: props.dataType,
      granularity: props.granularity,
    });

    if (!Array.isArray(data) || data.length === 0) {
      renderEcharts({
        title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } },
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value' },
        series: [],
      });
      return;
    }

    const allTimeKeys = new Set<string>();
    const seriesData: { name: string; data: number[] }[] = [];

    const brandMap = new Map<string, Map<string, number>>();
    for (const brand of data) {
      const map = new Map<string, number>();
      for (const point of brand.trend) {
        const key = makeTimeKey(point);
        map.set(key, point.sales ?? 0);
        allTimeKeys.add(key);
      }
      brandMap.set(brand.brand_name, map);
    }

    const timeLabels = [...allTimeKeys].sort();

    const brand1 = props.brands[0];
    const brand2 = props.brands[1];
    if (brand1 && brand2) {
      for (const brand of [brand1, brand2]) {
        const map = brandMap.get(brand);
        seriesData.push({
          name: brand,
          data: timeLabels.map((t) => map?.get(t) ?? 0),
        });
      }
    }

    renderEcharts({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: [props.brands[0]!, props.brands[1]!], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
      xAxis: { type: 'category', data: timeLabels, boundaryGap: false },
      yAxis: { type: 'value', axisLabel: { formatter: (val: number) => val >= 10000 ? `${(val / 10000).toFixed(0)}万` : String(val) } },
      series: seriesData.map((s, i) => ({
        name: s.name,
        type: 'line' as const,
        data: s.data,
        smooth: true,
        itemStyle: { color: COLORS[i % COLORS.length] },
      })),
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchAndRender());

watch([() => props.brands, () => props.granularity, () => props.dataType], () => fetchAndRender(), { deep: true });
</script>

<template>
  <div class="h-80 w-full">
    <EchartsUI ref="chartRef" />
  </div>
</template>
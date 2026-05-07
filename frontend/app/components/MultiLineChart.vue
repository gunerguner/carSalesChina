<template>
  <div class="chart-card page-card">
    <div class="card-header">
      <h3>{{ title }}</h3>
      <slot name="actions" />
    </div>
    <div class="card-body">
      <ChartComponent v-if="seriesList.length > 0" :option="chartOption" :height="height" />
      <el-empty v-else description="暂无数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { EChartsOption } from "echarts";

const props = defineProps<{
  data: { name: string; trend: { year: number; month?: number; sales: number }[] }[];
  title?: string;
  height?: number;
}>();

const seriesList = computed(() => {
  return props.data.map((s) => ({ name: s.name, values: s.trend.map((t) => t.sales) }));
});

const categories = computed(() => {
  if (!props.data[0]) return [];
  return props.data[0].trend.map((d) => (d.month != null ? `${d.year}-${String(d.month).padStart(2, "0")}` : `${d.year}`));
});

const chartOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: "axis" },
  legend: { bottom: 0 },
  xAxis: { type: "category", data: categories.value },
  yAxis: { type: "value", name: "万辆" },
  series: seriesList.value.map((s) => ({
    name: s.name,
    type: "line",
    data: s.values,
    smooth: true,
  })),
}));
</script>
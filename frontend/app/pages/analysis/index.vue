<template>
  <div>
    <div class="filter-bar">
      <YearRangePicker />
    </div>

    <ChartCard title="新能源渗透率趋势" style="margin-top: 16px">
      <ChartComponent v-if="nevShareTrend.length > 0" :option="penetrationOption" :height="350" />
      <el-empty v-else description="暂无数据" />
    </ChartCard>

    <ChartCard title="新能源内部结构趋势" style="margin-top: 16px">
      <ChartComponent v-if="nevBreakdown.length > 0" :option="breakdownOption" :height="350" />
      <el-empty v-else description="暂无数据" />
    </ChartCard>

    <ChartCard title="趋势明细表" style="margin-top: 16px">
      <el-table :data="nevShareTrend" border stripe max-height="400">
        <el-table-column label="时间" width="100">
          <template #default="{ row }">{{ row.month != null ? `${row.year}-${String(row.month).padStart(2, "0")}` : `${row.year}` }}</template>
        </el-table-column>
        <el-table-column prop="total_sales" label="总销量" />
        <el-table-column prop="nev_sales" label="新能源销量" />
        <el-table-column prop="nev_penetration_rate" label="渗透率(%)" />
      </el-table>
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAnalysisData } from "~/composables/useAnalysisData";

const { nevShareTrend, nevBreakdown } = useAnalysisData();

const penetrationOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: { type: "category", data: nevShareTrend.value.map((d: any) => d.month != null ? `${d.year}-${String(d.month).padStart(2, "0")}` : `${d.year}`) },
  yAxis: { type: "value", name: "%" },
  series: [{ name: "渗透率", type: "line", data: nevShareTrend.value.map((d: any) => d.nev_penetration_rate), smooth: true }],
}));

const breakdownOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { bottom: 0 },
  xAxis: { type: "category", data: nevBreakdown.value.map((d: any) => d.month != null ? `${d.year}-${String(d.month).padStart(2, "0")}` : `${d.year}`) },
  yAxis: { type: "value", name: "%" },
  series: [
    { name: "纯电占比", type: "line", data: nevBreakdown.value.map((d: any) => d.bev_ratio), smooth: true },
    { name: "插混占比", type: "line", data: nevBreakdown.value.map((d: any) => d.phev_ratio), smooth: true },
    { name: "混动占比", type: "line", data: nevBreakdown.value.map((d: any) => d.hybrid_ratio), smooth: true },
  ],
}));
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
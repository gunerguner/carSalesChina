<template>
  <div>
    <div class="filter-bar">
      <EnergyTypeFilter />
      <YearRangePicker />
    </div>

    <ChartCard title="月度销量数据" style="margin-top: 16px">
      <el-table :data="yearly" border stripe>
        <el-table-column prop="month" label="月份" width="80" :formatter="(_r: any, _c: any, v: number) => v + '月'" />
        <el-table-column prop="sales" label="销量(万辆)" sortable />
        <el-table-column prop="total_sales" label="总销量(万辆)" />
        <el-table-column prop="nev_sales" label="新能源销量(万辆)" />
        <el-table-column prop="ice_sales" label="燃油车销量(万辆)" />
      </el-table>
    </ChartCard>

    <ChartCard title="销量趋势" style="margin-top: 16px">
      <ChartComponent :option="trendChartOption" :height="350" />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useMarketData } from "~/composables/useMarketData";

const { trend, yearly } = useMarketData();

const trendChartOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: { type: "category", data: trend.value.map((d: any) => d.month != null ? `${d.year}-${String(d.month).padStart(2, "0")}` : `${d.year}`) },
  yAxis: { type: "value", name: "万辆" },
  series: [{ name: "销量", type: "line", data: trend.value.map((d: any) => d.sales), smooth: true }],
}));
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
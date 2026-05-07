<template>
  <div>
    <div class="filter-bar">
      <TimeFilter />
    </div>

    <el-row v-if="detail" :gutter="16" style="margin-top: 16px">
      <el-col :span="6"><div class="stat-card"><div class="number">{{ detail.sales_volume }}</div><div class="label">销量（万辆）</div></div></el-col>
      <el-col :span="6"><div class="stat-card"><div class="number">#{{ detail.rank }}</div><div class="label">排名</div></div></el-col>
      <el-col :span="6"><div class="stat-card"><div class="number" :style="{ color: (detail.yoy_growth ?? 0) >= 0 ? '#f56c6c' : '#67c23a' }">{{ detail.yoy_growth != null ? (detail.yoy_growth >= 0 ? '+' : '') + detail.yoy_growth + '%' : '-' }}</div><div class="label">同比</div></div></el-col>
      <el-col :span="6"><div class="stat-card"><div class="number" :style="{ color: (detail.mom_growth ?? 0) >= 0 ? '#f56c6c' : '#67c23a' }">{{ detail.mom_growth != null ? (detail.mom_growth >= 0 ? '+' : '') + detail.mom_growth + '%' : '-' }}</div><div class="label">环比</div></div></el-col>
    </el-row>

    <ChartCard title="历史趋势" style="margin-top: 16px">
      <ChartComponent v-if="trend.length > 0" :option="trendOption" :height="350" />
      <el-empty v-else description="暂无数据" />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useBrandData } from "~/composables/useBrandData";

const route = useRoute();
const brandId = computed(() => Number(route.params.id));
const { detail, trend, fetchDetail, fetchTrend } = useBrandData();

onMounted(() => {
  fetchDetail(brandId.value);
  fetchTrend(brandId.value);
});

const trendOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: { type: "category", data: trend.value.map((d: any) => d.month != null ? `${d.year}-${String(d.month).padStart(2, "0")}` : `${d.year}`) },
  yAxis: { type: "value", name: "万辆" },
  series: [{ name: "销量", type: "line", data: trend.value.map((d: any) => d.sales), smooth: true }],
}));
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
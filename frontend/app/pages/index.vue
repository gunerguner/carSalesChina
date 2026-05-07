<template>
  <div>
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="number">{{ overview?.total_sales ?? '-' }}</div>
          <div class="label">当月总销量（万辆）</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="number">{{ overview?.nev_sales ?? '-' }}</div>
          <div class="label">新能源销量（万辆）</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="number">{{ overview?.nev_penetration_rate ?? '-' }}%</div>
          <div class="label">新能源渗透率</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="number" :style="{ color: (overview?.yoy_growth ?? 0) >= 0 ? '#f56c6c' : '#67c23a' }">
            {{ overview?.yoy_growth != null ? (overview.yoy_growth >= 0 ? '+' : '') + overview.yoy_growth + '%' : '-' }}
          </div>
          <div class="label">同比增速</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <ChartCard title="近12个月销量趋势">
          <ChartComponent :option="trendOption" :height="350" />
        </ChartCard>
      </el-col>
      <el-col :span="12">
        <ChartCard title="本月能源类型占比">
          <ChartComponent :option="pieOption" :height="350" />
        </ChartCard>
      </el-col>
    </el-row>

    <ChartCard title="TOP 10 品牌" style="margin-top: 16px">
      <RankingTable :data="ranking.data?.slice(0, 10) ?? []" />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useMarketData } from "~/composables/useMarketData";
import { useBrandData } from "~/composables/useBrandData";

const { overview, trend, byEnergy } = useMarketData();
const { ranking, fetchRanking } = useBrandData();

onMounted(() => fetchRanking());

const trendOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: { type: "category", data: trend.value.map((d: any) => `${d.year}-${String(d.month).padStart(2, "0")}`) },
  yAxis: { type: "value", name: "万辆" },
  series: [
    { name: "销量", type: "line", data: trend.value.map((d: any) => d.sales), smooth: true },
  ],
}));

const pieOption = computed(() => ({
  tooltip: { trigger: "item" },
  legend: { bottom: 0 },
  series: [{
    type: "pie",
    radius: ["45%", "70%"],
    data: byEnergy.value.map((d: any) => ({ name: d.name, value: d.value })),
    label: { formatter: "{b}\n{d}%" },
  }],
}));
</script>

<style scoped>
.stat-row {
  margin-bottom: 16px;
}
</style>
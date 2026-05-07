<template>
  <div>
    <div class="filter-bar">
      <YearRangePicker />
    </div>

    <ChartCard title="品牌对比分析" style="margin-top: 16px">
      <el-select
        v-model="selectedIds"
        multiple
        filterable
        placeholder="选择品牌（最多5个）"
        style="width: 100%; margin-bottom: 16px"
        @change="onBrandChange"
      >
        <el-option v-for="b in allBrands" :key="b.id" :label="b.brand_name" :value="b.id" />
      </el-select>

      <MultiLineChart v-if="compareTrend.length > 0" :data="compareTrend" />
      <el-empty v-else description="请选择品牌查看趋势对比" />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useBrandData } from "~/composables/useBrandData";

const { ranking, compareTrend, fetchRanking, fetchCompareTrend } = useBrandData();

const selectedIds = ref<number[]>([]);
const allBrands = ref<any[]>([]);

onMounted(async () => {
  await fetchRanking();
  allBrands.value = ranking.value?.data ?? [];
});

function onBrandChange(ids: number[]) {
  if (ids.length > 5) {
    selectedIds.value = ids.slice(0, 5);
    return;
  }
  if (ids.length > 0) {
    fetchCompareTrend(ids.join(","));
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
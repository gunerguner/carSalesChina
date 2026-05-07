<template>
  <div>
    <div class="filter-bar">
      <TimeFilter />
      <el-switch v-model="showYearly" active-text="年度排行" inactive-text="月度排行" style="margin-left: 16px" />
      <el-switch v-model="nevOnly" active-text="仅新能源" inactive-text="全部品牌" style="margin-left: 16px" @change="onNevChange" />
    </div>

    <ChartCard title="品牌排行榜" style="margin-top: 16px">
      <RankingTable :data="showYearly ? yearlyRanking.data : ranking.data" />
    </ChartCard>

    <ChartCard title="品牌对比" style="margin-top: 16px">
      <el-select
        v-model="selectedIds"
        multiple
        filterable
        placeholder="选择品牌（最多5个）"
        style="width: 100%; margin-bottom: 16px"
        @change="onBrandChange"
      >
        <el-option v-for="b in brandOptions" :key="b.id" :label="b.brand_name" :value="b.id" />
      </el-select>

      <MultiLineChart v-if="compareTrend.length > 0" :data="compareTrend" />
      <el-empty v-else description="请选择品牌进行对比" />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useFilterStore } from "~/stores/filter";
import { useBrandData } from "~/composables/useBrandData";

const filter = useFilterStore();
const { ranking, yearlyRanking, compareTrend, fetchRanking, fetchYearlyRanking, fetchCompareTrend } = useBrandData();

const showYearly = ref(false);
const nevOnly = ref(false);
const selectedIds = ref<number[]>([]);

const brandOptions = computed(() => ranking.value?.data ?? []);

onMounted(() => {
  fetchRanking();
  fetchYearlyRanking();
});

watch(showYearly, () => {
  if (showYearly.value) fetchYearlyRanking();
  else fetchRanking(nevOnly.value ? 1 : undefined);
});

function onNevChange(val: boolean) {
  fetchRanking(val ? 1 : undefined);
}

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
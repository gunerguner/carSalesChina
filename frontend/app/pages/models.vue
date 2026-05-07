<template>
  <div>
    <div class="filter-bar">
      <TimeFilter />
      <el-select v-model="energyFilter" placeholder="能源类型" clearable style="width: 140px; margin-left: 16px">
        <el-option label="纯电动" value="bev" />
        <el-option label="插电混动" value="phev" />
        <el-option label="燃油车" value="ice" />
      </el-select>
    </div>

    <ChartCard title="车型销量排行榜" style="margin-top: 16px">
      <el-table :data="models" border stripe v-loading="loading">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="model_name" label="车型名称" min-width="180" />
        <el-table-column prop="sales_volume" label="销量(万辆)" sortable width="120" />
        <el-table-column prop="segment" label="级别" width="80" />
        <el-table-column prop="energy_type" label="能源类型" width="100" />
      </el-table>
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useFilterStore } from "~/stores/filter";
import { useApi } from "~/composables/useApi";

const filter = useFilterStore();
const api = useApi();
const models = ref<any[]>([]);
const loading = ref(false);
const energyFilter = ref<string | undefined>(undefined);

async function fetchModels() {
  loading.value = true;
  try {
    const res: any = await api.get("/api/v1/models/ranking", {
      year: filter.selectedYear,
      month: filter.selectedMonth,
      page: 1,
      pageSize: 50,
      energy_type: energyFilter.value || undefined,
    });
    models.value = res?.data?.data ?? res?.data ?? [];
  } finally {
    loading.value = false;
  }
}

onMounted(fetchModels);
watch(
  () => [filter.selectedYear, filter.selectedMonth, energyFilter.value],
  fetchModels
);
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
}
</style>
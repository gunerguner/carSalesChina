<template>
  <div class="time-filter">
    <el-select v-model="filter.selectedYear" style="width: 100px">
      <el-option v-for="y in yearOptions" :key="y" :label="String(y)" :value="y" />
    </el-select>
    <el-select v-model="filter.selectedMonth" style="width: 90px; margin-left: 8px">
      <el-option v-for="m in 12" :key="m" :label="m + '月'" :value="m" />
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useFilterStore } from "~/stores/filter";

const filter = useFilterStore();
const now = new Date();
const yearOptions = computed(() => {
  const years = [];
  for (let y = now.getFullYear(); y >= 2015; y--) years.push(y);
  return years;
});
</script>
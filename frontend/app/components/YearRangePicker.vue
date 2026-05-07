<template>
  <div class="year-range-picker">
    <el-radio-group v-model="filter.yearsRange" size="small">
      <el-radio-button :value="1">近1年</el-radio-button>
      <el-radio-button :value="3">近3年</el-radio-button>
      <el-radio-button :value="5">近5年</el-radio-button>
    </el-radio-group>
    <el-radio-group v-model="filter.granularity" size="small" style="margin-left: 12px">
      <el-radio-button value="monthly">月度</el-radio-button>
      <el-radio-button value="yearly">年度</el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup lang="ts">
import { useFilterStore } from "~/stores/filter";
const filter = useFilterStore();
</script>
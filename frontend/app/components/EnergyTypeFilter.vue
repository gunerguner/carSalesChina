<template>
  <div class="energy-filter">
    <el-radio-group v-model="filter.energyType" size="small">
      <el-radio-button value="all">全部</el-radio-button>
      <el-radio-button value="fuel">燃油</el-radio-button>
      <el-radio-button value="bev">纯电</el-radio-button>
      <el-radio-button value="phev">插混</el-radio-button>
      <el-radio-button value="hybrid">混动</el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup lang="ts">
import { useFilterStore } from "~/stores/filter";
const filter = useFilterStore();
</script>
<template>
  <el-table :data="data" stripe border style="width: 100%">
    <el-table-column type="index" label="排名" width="60" :index="(i: number) => i + 1" />
    <el-table-column prop="brand_name" label="品牌名称" min-width="120" />
    <el-table-column prop="sales_volume" label="销量(万辆)" width="120" sortable />
    <el-table-column label="同比(%)" width="100">
      <template #default="{ row }">
        <span :style="{ color: (row.yoy_growth ?? 0) >= 0 ? '#f56c6c' : '#67c23a' }">
          {{ row.yoy_growth != null ? (row.yoy_growth >= 0 ? '+' : '') + row.yoy_growth + '%' : '-' }}
        </span>
      </template>
    </el-table-column>
    <el-table-column label="环比(%)" width="100">
      <template #default="{ row }">
        <span :style="{ color: (row.mom_growth ?? 0) >= 0 ? '#f56c6c' : '#67c23a' }">
          {{ row.mom_growth != null ? (row.mom_growth >= 0 ? '+' : '') + row.mom_growth + '%' : '-' }}
        </span>
      </template>
    </el-table-column>
    <el-table-column label="升降" width="80">
      <template #default="{ row }">
        <span v-if="row.prev_month_rank && row.rank < row.prev_month_rank" style="color: #f56c6c">&#9650;{{ row.prev_month_rank - row.rank }}</span>
        <span v-else-if="row.prev_month_rank && row.rank > row.prev_month_rank" style="color: #67c23a">&#9660;{{ row.rank - row.prev_month_rank }}</span>
        <span v-else style="color: #909399">—</span>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
defineProps<{ data: any[] }>();
</script>
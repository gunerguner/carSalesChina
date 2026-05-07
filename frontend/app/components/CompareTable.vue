<template>
  <el-table :data="rows" border stripe>
    <el-table-column prop="label" label="指标" width="120" />
    <el-table-column v-for="col in columns" :key="col.key" :label="col.title" width="150">
      <template #default="{ row }">
        {{ row[col.key] }}
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  columns: { key: string; title: string }[];
  data: Record<string, any>[];
  rowLabelField?: string;
}>();

const rows = computed(() => {
  if (props.data.length === 0) return [];
  const first = props.data[0];
  if (!first) return [];
  const keys = Object.keys(first).filter((k) => k !== "brand_name" && k !== "brand_id");
  return keys.map((key) => {
    const row: Record<string, any> = { label: key, key };
    props.data.forEach((d, idx) => {
      row[props.columns[idx]?.key ?? `col${idx}`] = d[key] ?? "-";
    });
    return row;
  });
});
</script>
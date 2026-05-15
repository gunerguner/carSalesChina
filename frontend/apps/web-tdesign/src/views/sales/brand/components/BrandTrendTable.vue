<script lang="ts" setup>
import type { PrimaryTableCol } from 'tdesign-vue-next';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { formatNumberCell } from '#/views/sales/utils/table-cell-formatters';

interface BrandSeriesPoint {
  sales: number;
  time: string;
}

interface BrandSeriesRecord {
  brand_name: string;
  points: BrandSeriesPoint[];
}

const props = defineProps<{
  data: BrandSeriesRecord[];
  loading?: boolean;
  /** 最多展示多少条时间行；null 表示与 timeLabels 一致（如年度全部年份） */
  timeLabelMaxCount?: null | number;
  timeLabels: string[];
}>();

/** 表格：按时间倒序；条数由 timeLabelMaxCount 控制，与图表当前周期对齐 */
const tableTimeLabels = computed(() => {
  const sorted = [...props.timeLabels].toSorted((a, b) => b.localeCompare(a));
  const max = props.timeLabelMaxCount;
  if (max === null) {
    return sorted;
  }
  const limit = max ?? 12;
  return sorted.slice(0, limit);
});

const columns = computed<PrimaryTableCol[]>(() => {
  const base: PrimaryTableCol[] = [{ colKey: 'time', title: $t('sales.brand.trend.time'), width: 120 }];
  for (const brand of props.data) {
    base.push({
      cell: (_h: any, { row }: any) =>
        formatNumberCell(row[`brand_${brand.brand_name}`]),
      colKey: `brand_${brand.brand_name}`,
      title: brand.brand_name,
      width: 160,
    });
  }
  return base;
});

const tableData = computed(() => {
  const brandMap = new Map<string, Map<string, number>>();
  for (const brand of props.data) {
    const pointMap = new Map<string, number>();
    for (const point of brand.points ?? []) {
      pointMap.set(point.time, point.sales ?? 0);
    }
    brandMap.set(brand.brand_name, pointMap);
  }

  return tableTimeLabels.value.map((time) => {
    const row: Record<string, any> = { key: time, time };
    for (const brand of props.data) {
      const sales = brandMap.get(brand.brand_name)?.get(time);
      if (sales != null) {
        row[`brand_${brand.brand_name}`] = sales;
      }
    }
    return row;
  });
});
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    :loading="loading"
    row-key="key"
    size="small"
    bordered
  />
</template>

<script setup lang="ts">
import type { MonthlyDetailRecord } from '../useMarketData';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

const props = defineProps<{
  data: MonthlyDetailRecord[];
}>();

function periodText(r: MonthlyDetailRecord): string {
  return preferences.app.locale === 'zh-CN'
    ? `${r.year}年${r.monthNum}月`
    : `${r.year}-${String(r.monthNum).padStart(2, '0')}`;
}

function sortByYearMonth(a: unknown, b: unknown): number {
  const ra = a as MonthlyDetailRecord;
  const rb = b as MonthlyDetailRecord;
  return ra.year * 100 + ra.monthNum - (rb.year * 100 + rb.monthNum);
}

const columns = [
  {
    colKey: 'periodText',
    title: $t('sales.market.timePeriod'),
    width: 120,
    sorter: sortByYearMonth,
  },
  { colKey: 'salesText', title: $t('sales.market.monthly.sales'), width: 140 },
  { colKey: 'yoyGrowth', title: $t('sales.market.monthly.yoyGrowth'), width: 130 },
  { colKey: 'momGrowth', title: $t('sales.market.monthly.momGrowth'), width: 130 },
  
];

function growthColor(val: null | number | undefined): string {
  if (val == null) return '#999';
  if (val > 0) return '#ef4444';
  if (val < 0) return '#22c55e';
  return '#666';
}

function growthText(val: null | number | undefined): string {
  return val == null ? '-' : `${val.toFixed(2)}%`;
}

const tableData = computed(() =>
  props.data.map((r) => ({
    ...r,
    periodText: periodText(r),
    salesText: r.sales == null ? '-' : r.sales.toLocaleString(),
    momGrowthText: growthText(r.momGrowth),
    momGrowthColor: growthColor(r.momGrowth),
    yoyGrowthText: growthText(r.yoyGrowth),
    yoyGrowthColor: growthColor(r.yoyGrowth),
  })),
);
</script>

<template>
  <div class="px-4 py-3">
    <Table
      :columns="columns"
      :data="tableData"
      row-key="key"
      size="small"
      bordered
    >
      <template #periodText="{ row }">{{ row.periodText }}</template>
      <template #salesText="{ row }">{{ row.salesText }}</template>
      <template #momGrowth="{ row }">
        <span :style="{ color: row.momGrowthColor, fontWeight: 500 }">{{ row.momGrowthText }}</span>
      </template>
      <template #yoyGrowth="{ row }">
        <span :style="{ color: row.yoyGrowthColor, fontWeight: 500 }">{{ row.yoyGrowthText }}</span>
      </template>
    </Table>
  </div>
</template>

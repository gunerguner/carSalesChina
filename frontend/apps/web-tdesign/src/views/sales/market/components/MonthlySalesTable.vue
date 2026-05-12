<script setup lang="ts">
import type { MonthlyDetailRecord } from '../useMarketData';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

const props = defineProps<{
  data: MonthlyDetailRecord[];
}>();

const columns = [
  {
    colKey: 'year',
    title: $t('sales.market.yearly.year'),
    width: 100,
    sorter: true,
  },
  {
    colKey: 'month',
    title: $t('sales.market.monthly.month'),
    width: 80,
    sorter: true,
  },
  { colKey: 'salesText', title: $t('sales.market.monthly.sales'), width: 140 },
  { colKey: 'momGrowth', title: $t('sales.market.monthly.momGrowth'), width: 130 },
  { colKey: 'yoyGrowth', title: $t('sales.market.monthly.yoyGrowth'), width: 130 },
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
    month: `${r.monthNum}月`,
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

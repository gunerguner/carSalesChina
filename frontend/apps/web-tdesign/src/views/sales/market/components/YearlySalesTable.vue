<script setup lang="ts">
import type { YearlyTrendRecord } from '../useMarketData';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

const props = defineProps<{
  data: YearlyTrendRecord[];
}>();

const columns = [
  { colKey: 'year', title: $t('sales.market.yearly.year'), width: 100 },
  { colKey: 'salesText', title: $t('sales.market.yearly.sales'), width: 150 },
  { colKey: 'yoyGrowth', title: $t('sales.market.yearly.yoyGrowth'), width: 140 },
];

function growthColor(val: null | number | undefined): string {
  if (val == null) return '#999';
  if (val > 0) return '#ef4444';
  if (val < 0) return '#22c55e';
  return '#666';
}

const tableData = computed(() =>
  props.data
    .map((r) => ({
      ...r,
      salesText: r.sales == null ? '-' : r.sales.toLocaleString(),
      yoyGrowthText: r.yoyGrowth == null ? '-' : `${r.yoyGrowth.toFixed(2)}%`,
      yoyGrowthColor: growthColor(r.yoyGrowth),
    }))
    .toReversed(),
);
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    row-key="key"
    size="small"
    bordered
  >
    <template #salesText="{ row }">{{ row.salesText }}</template>
    <template #yoyGrowth="{ row }">
      <span :style="{ color: row.yoyGrowthColor, fontWeight: 500 }">{{ row.yoyGrowthText }}</span>
    </template>
  </Table>
</template>

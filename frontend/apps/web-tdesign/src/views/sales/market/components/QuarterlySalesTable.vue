<script setup lang="ts">
import type { QuarterlyTrendRecord } from '../useMarketData';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

const props = defineProps<{
  data: QuarterlyTrendRecord[];
}>();

function periodText(r: QuarterlyTrendRecord): string {
  return preferences.app.locale === 'zh-CN'
    ? `${r.year}年Q${r.quarter}`
    : `${r.year} Q${r.quarter}`;
}

function sortByYearQuarter(a: unknown, b: unknown): number {
  const ra = a as QuarterlyTrendRecord;
  const rb = b as QuarterlyTrendRecord;
  return ra.year * 10 + ra.quarter - (rb.year * 10 + rb.quarter);
}

const columns = [
  {
    colKey: 'periodText',
    title: $t('sales.market.timePeriod'),
    width: 130,
    sorter: sortByYearQuarter,
  },
  { colKey: 'salesText', title: $t('sales.market.quarterly.sales'), width: 150 },
  { colKey: 'yoyGrowth', title: $t('sales.market.quarterly.yoyGrowth'), width: 140 },
  { colKey: 'qoqGrowth', title: $t('sales.market.quarterly.qoqGrowth'), width: 140 },
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
      periodText: periodText(r),
      salesText: Math.round(r.sales).toLocaleString(),
      qoqGrowthText: r.qoqGrowth == null ? '-' : `${r.qoqGrowth.toFixed(2)}%`,
      qoqGrowthColor: growthColor(r.qoqGrowth),
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
    <template #periodText="{ row }">{{ row.periodText }}</template>
    <template #salesText="{ row }">{{ row.salesText }}</template>
    <template #qoqGrowth="{ row }">
      <span :style="{ color: row.qoqGrowthColor, fontWeight: 500 }">{{ row.qoqGrowthText }}</span>
    </template>
    <template #yoyGrowth="{ row }">
      <span :style="{ color: row.yoyGrowthColor, fontWeight: 500 }">{{ row.yoyGrowthText }}</span>
    </template>
  </Table>
</template>

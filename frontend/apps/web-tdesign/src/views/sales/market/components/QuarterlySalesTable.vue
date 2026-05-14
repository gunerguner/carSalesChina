<script setup lang="ts">
import type { QuarterlyTrendRecord } from '../useMarketData';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

import { growthColor, growthPercentText } from '#/views/sales/utils/growth-utils';
import { formatQuarterPeriod } from '#/views/sales/utils/period-utils';
import { toYearQuarterSortKey } from '#/views/sales/utils/sort-utils';

const props = defineProps<{
  data: QuarterlyTrendRecord[];
}>();

function periodText(r: QuarterlyTrendRecord): string {
  return formatQuarterPeriod(r.year, r.quarter, preferences.app.locale);
}

function sortByYearQuarter(a: unknown, b: unknown): number {
  const ra = a as QuarterlyTrendRecord;
  const rb = b as QuarterlyTrendRecord;
  return toYearQuarterSortKey(ra.year, ra.quarter) -
    toYearQuarterSortKey(rb.year, rb.quarter);
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

const tableData = computed(() =>
  props.data
    .map((r) => ({
      ...r,
      periodText: periodText(r),
      salesText: Math.round(r.sales).toLocaleString(),
      qoqGrowthText: growthPercentText(r.qoqGrowth),
      qoqGrowthColor: growthColor(r.qoqGrowth),
      yoyGrowthText: growthPercentText(r.yoyGrowth),
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

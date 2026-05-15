<script setup lang="ts">
import type { YearlyTrendRecord } from '../useMarketData';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { growthColor, growthPercentText } from '#/views/sales/utils/growth-utils';
import { formatYearPeriod } from '#/views/sales/utils/period-utils';
import { sortByNumberAsc } from '#/views/sales/utils/sort-utils';

const props = defineProps<{
  data: YearlyTrendRecord[];
}>();

function periodText(r: YearlyTrendRecord): string {
  return formatYearPeriod(r.year, preferences.app.locale);
}

function sortByYear(a: unknown, b: unknown): number {
  const ra = a as YearlyTrendRecord;
  const rb = b as YearlyTrendRecord;
  return sortByNumberAsc(ra.year, rb.year);
}

const columns = [
  {
    colKey: 'periodText',
    title: $t('sales.market.timePeriod'),
    width: 110,
    sorter: sortByYear,
  },
  { colKey: 'salesText', title: $t('sales.market.yearly.sales'), width: 150 },
  { colKey: 'yoyGrowth', title: $t('sales.market.yearly.yoyGrowth'), width: 140 },
];

const tableData = computed(() =>
  props.data
    .map((r) => ({
      ...r,
      periodText: periodText(r),
      salesText: r.sales == null ? '-' : Math.round(r.sales).toLocaleString(),
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
    <template #yoyGrowth="{ row }">
      <span :style="{ color: row.yoyGrowthColor, fontWeight: 500 }">{{ row.yoyGrowthText }}</span>
    </template>
  </Table>
</template>

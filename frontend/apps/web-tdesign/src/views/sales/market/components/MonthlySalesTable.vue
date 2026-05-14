<script setup lang="ts">
import type { MonthlyDetailRecord } from '../useMarketData';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

import { growthColor, growthPercentText } from '#/views/sales/utils/growth-utils';
import { formatMonthPeriod } from '#/views/sales/utils/period-utils';
import { toYearMonthSortKey } from '#/views/sales/utils/sort-utils';

const props = defineProps<{
  data: MonthlyDetailRecord[];
}>();

function periodText(r: MonthlyDetailRecord): string {
  return formatMonthPeriod(r.year, r.monthNum, preferences.app.locale);
}

function sortByYearMonth(a: unknown, b: unknown): number {
  const ra = a as MonthlyDetailRecord;
  const rb = b as MonthlyDetailRecord;
  return toYearMonthSortKey(ra.year, ra.monthNum) -
    toYearMonthSortKey(rb.year, rb.monthNum);
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

const tableData = computed(() =>
  props.data.map((r) => ({
    ...r,
    periodText: periodText(r),
    salesText: r.sales == null ? '-' : r.sales.toLocaleString(),
    momGrowthText: growthPercentText(r.momGrowth),
    momGrowthColor: growthColor(r.momGrowth),
    yoyGrowthText: growthPercentText(r.yoyGrowth),
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

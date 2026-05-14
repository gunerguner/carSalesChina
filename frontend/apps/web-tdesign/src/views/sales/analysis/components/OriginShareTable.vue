<script lang="ts" setup>
import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { toMonthKey } from '#/views/sales/utils/period-utils';
import { toYearMonthSortKey } from '#/views/sales/utils/sort-utils';
import { formatPercentCell } from '#/views/sales/utils/table-cell-formatters';

const props = defineProps<{
  data: OriginShareTrendRecord[];
}>();

const columns = [
  { colKey: 'time', title: $t('sales.analysis.origin.time'), width: 120 },
  { colKey: 'domestic', title: $t('sales.analysis.origin.domestic'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.domestic) },
  { colKey: 'german', title: $t('sales.analysis.origin.german'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.german) },
  { colKey: 'japanese', title: $t('sales.analysis.origin.japanese'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.japanese) },
  { colKey: 'american', title: $t('sales.analysis.origin.american'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.american) },
  { colKey: 'european', title: $t('sales.analysis.origin.european'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.european) },
  { colKey: 'korean', title: $t('sales.analysis.origin.korean'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.korean) },
  { colKey: 'french', title: $t('sales.analysis.origin.french'), width: 100, cell: (_h: any, { row }: any) => formatPercentCell(row.french) },
];

const tableData = computed(() => {
  return props.data.map((item, index) => ({
    key: index,
    time: toMonthKey(item.year, item.month),
    sortKey: toYearMonthSortKey(item.year, item.month),
    domestic: item.domestic ?? null,
    german: item.german ?? null,
    japanese: item.japanese ?? null,
    american: item.american ?? null,
    european: item.european ?? null,
    korean: item.korean ?? null,
    french: item.french ?? null,
  })).toSorted((a: any, b: any) => b.sortKey - a.sortKey);
});
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    row-key="key"
    size="small"
    bordered
  />
</template>

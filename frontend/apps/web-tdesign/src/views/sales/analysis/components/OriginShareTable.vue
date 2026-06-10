<script setup lang="ts">
import type { PrimaryTableCol, TableRowData } from 'tdesign-vue-next';

import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { formatPercentOrDash } from '#/utils/format';
import { toMonthKey, toYearMonthSortKey } from '#/utils/period';

const props = defineProps<{
  data: OriginShareTrendRecord[];
}>();

type OriginShareKey =
  | 'american'
  | 'domestic'
  | 'european'
  | 'french'
  | 'german'
  | 'japanese'
  | 'korean';

interface OriginShareRow {
  american: null | number;
  domestic: null | number;
  european: null | number;
  french: null | number;
  german: null | number;
  japanese: null | number;
  key: number;
  korean: null | number;
  sortKey: number;
  time: string;
}

function percentCell(key: OriginShareKey) {
  return (_: unknown, { row }: { row: TableRowData }) =>
    formatPercentOrDash((row as OriginShareRow)[key]);
}

const columns: PrimaryTableCol[] = [
  { colKey: 'time', title: $t('sales.analysis.origin.time'), width: 120 },
  {
    colKey: 'domestic',
    title: $t('sales.analysis.origin.domestic'),
    width: 100,
    cell: percentCell('domestic'),
  },
  {
    colKey: 'german',
    title: $t('sales.analysis.origin.german'),
    width: 100,
    cell: percentCell('german'),
  },
  {
    colKey: 'japanese',
    title: $t('sales.analysis.origin.japanese'),
    width: 100,
    cell: percentCell('japanese'),
  },
  {
    colKey: 'american',
    title: $t('sales.analysis.origin.american'),
    width: 100,
    cell: percentCell('american'),
  },
  {
    colKey: 'european',
    title: $t('sales.analysis.origin.european'),
    width: 100,
    cell: percentCell('european'),
  },
  {
    colKey: 'korean',
    title: $t('sales.analysis.origin.korean'),
    width: 100,
    cell: percentCell('korean'),
  },
  {
    colKey: 'french',
    title: $t('sales.analysis.origin.french'),
    width: 100,
    cell: percentCell('french'),
  },
];

const tableData = computed<OriginShareRow[]>(() => {
  return props.data
    .map((item, index) => ({
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
    }))
    .toSorted((a, b) => b.sortKey - a.sortKey);
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

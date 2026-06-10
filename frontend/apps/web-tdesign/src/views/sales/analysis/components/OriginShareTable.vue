<script setup lang="ts">
import type { PrimaryTableCol, TableRowData } from 'tdesign-vue-next';

import type { OriginShareTrendRecord } from '#/api/sales/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { formatOrDash } from '#/utils/format';
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
  american: number;
  domestic: number;
  european: number;
  french: number;
  german: number;
  japanese: number;
  key: number;
  korean: number;
  sortKey: number;
  time: string;
}

function percentCell(key: OriginShareKey) {
  return (_: unknown, { row }: { row: TableRowData }) =>
    formatOrDash((row as OriginShareRow)[key], '%');
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
      domestic: item.domestic,
      german: item.german,
      japanese: item.japanese,
      american: item.american,
      european: item.european,
      korean: item.korean,
      french: item.french,
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

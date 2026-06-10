<script setup lang="ts">
import type { PrimaryTableCol, TableRowData } from 'tdesign-vue-next';

import type {
  NevBreakdownRecord,
  NevShareTrendRecord,
} from '#/api/sales/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { formatOrDash } from '#/utils/format';
import { toMonthKey } from '#/utils/period';

const props = defineProps<{
  breakdownTrend: NevBreakdownRecord[];
  shareTrend: NevShareTrendRecord[];
}>();

interface NevPenetrationRow {
  bevRatio: number;
  bevSales: number;
  key: number;
  nevSales: number;
  penetrationRate: number;
  time: string;
  totalSales: number;
}

function numberCell(key: 'bevSales' | 'nevSales' | 'totalSales') {
  return (_: unknown, { row }: { row: TableRowData }) =>
    formatOrDash((row as NevPenetrationRow)[key]);
}

function percentCell(key: 'bevRatio' | 'penetrationRate') {
  return (_: unknown, { row }: { row: TableRowData }) =>
    formatOrDash((row as NevPenetrationRow)[key], '%');
}

const columns: PrimaryTableCol[] = [
  { colKey: 'time', title: $t('sales.analysis.nev.time'), width: 120 },
  {
    colKey: 'totalSales',
    title: $t('sales.analysis.nev.totalSales'),
    width: 130,
    cell: numberCell('totalSales'),
  },
  {
    colKey: 'nevSales',
    title: $t('sales.analysis.nev.nevSales'),
    width: 130,
    cell: numberCell('nevSales'),
  },
  {
    colKey: 'penetrationRate',
    title: $t('sales.analysis.nev.penetrationRate'),
    width: 140,
    cell: percentCell('penetrationRate'),
  },
  {
    colKey: 'bevSales',
    title: $t('sales.analysis.nev.bevSales'),
    width: 130,
    cell: numberCell('bevSales'),
  },
  {
    colKey: 'bevRatio',
    title: $t('sales.analysis.nev.bevRatioInNev'),
    width: 170,
    cell: percentCell('bevRatio'),
  },
];

const tableData = computed<NevPenetrationRow[]>(() => {
  const bevMap = new Map<string, { bevRatio: number; bevSales: number }>();
  for (const item of props.breakdownTrend) {
    const key = toMonthKey(item.year, item.month);
    bevMap.set(key, {
      bevSales: item.bev_sales,
      bevRatio: item.bev_ratio,
    });
  }

  return props.shareTrend
    .map((item, index) => {
      const key = toMonthKey(item.year, item.month);
      const bevInfo = bevMap.get(key);
      return {
        key: index,
        time: key,
        totalSales: item.total_sales,
        nevSales: item.nev_sales,
        penetrationRate: item.nev_penetration_rate,
        bevSales: bevInfo?.bevSales ?? 0,
        bevRatio: bevInfo?.bevRatio ?? 0,
      };
    })
    .toReversed();
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

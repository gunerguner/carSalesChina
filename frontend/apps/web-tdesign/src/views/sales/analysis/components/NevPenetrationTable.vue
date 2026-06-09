<script setup lang="ts">
import type {
  NevBreakdownRecord,
  NevShareTrendRecord,
} from '#/api/sales/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { formatNumberCell, formatPercentCell } from '#/utils/format';
import { toMonthKey } from '#/utils/period';

const props = defineProps<{
  breakdownTrend: NevBreakdownRecord[];
  shareTrend: NevShareTrendRecord[];
}>();

interface NevPenetrationRow {
  bevRatio: null | number;
  bevSales: null | number;
  key: number;
  nevSales: null | number;
  penetrationRate: null | number;
  time: string;
  totalSales: null | number;
}

const columns = [
  { colKey: 'time', title: $t('sales.analysis.nev.time'), width: 120 },
  {
    colKey: 'totalSales',
    title: $t('sales.analysis.nev.totalSales'),
    width: 130,
    cell: (_h: any, { row }: any) => formatNumberCell(row.totalSales),
  },
  {
    colKey: 'nevSales',
    title: $t('sales.analysis.nev.nevSales'),
    width: 130,
    cell: (_h: any, { row }: any) => formatNumberCell(row.nevSales),
  },
  {
    colKey: 'penetrationRate',
    title: $t('sales.analysis.nev.penetrationRate'),
    width: 140,
    cell: (_h: any, { row }: any) => formatPercentCell(row.penetrationRate),
  },
  {
    colKey: 'bevSales',
    title: $t('sales.analysis.nev.bevSales'),
    width: 130,
    cell: (_h: any, { row }: any) => formatNumberCell(row.bevSales),
  },
  {
    colKey: 'bevRatio',
    title: $t('sales.analysis.nev.bevRatioInNev'),
    width: 170,
    cell: (_h: any, { row }: any) => formatPercentCell(row.bevRatio),
  },
];

const tableData = computed<NevPenetrationRow[]>(() => {
  const bevMap = new Map<
    string,
    { bevRatio: null | number; bevSales: null | number }
  >();
  for (const item of props.breakdownTrend) {
    const key = toMonthKey(item.year, item.month);
    bevMap.set(key, {
      bevSales: item.bev_sales ?? null,
      bevRatio: item.bev_ratio ?? null,
    });
  }

  return props.shareTrend
    .map((item, index) => {
      const key = toMonthKey(item.year, item.month);
      const bevInfo = bevMap.get(key);
      return {
        key: index,
        time: key,
        totalSales: item.total_sales ?? null,
        nevSales: item.nev_sales ?? null,
        penetrationRate: item.nev_penetration_rate ?? null,
        bevSales: bevInfo?.bevSales ?? null,
        bevRatio: bevInfo?.bevRatio ?? null,
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

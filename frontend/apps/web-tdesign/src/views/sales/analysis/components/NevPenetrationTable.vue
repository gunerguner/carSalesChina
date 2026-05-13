<script lang="ts" setup>
import { ref, watch } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

const props = defineProps<{
  breakdownTrend: any[];
  shareTrend: any[];
}>();

const tableData = ref<any[]>([]);

const columns = [
  { colKey: 'time', title: $t('sales.analysis.nev.time'), width: 120 },
  { colKey: 'totalSales', title: $t('sales.analysis.nev.totalSales'), width: 130, cell: (_h: any, { row }: any) => row.totalSales?.toLocaleString() ?? '-' },
  { colKey: 'nevSales', title: $t('sales.analysis.nev.nevSales'), width: 130, cell: (_h: any, { row }: any) => row.nevSales?.toLocaleString() ?? '-' },
  { colKey: 'penetrationRate', title: $t('sales.analysis.nev.penetrationRate'), width: 140, cell: (_h: any, { row }: any) => row.penetrationRate == null ? '-' : `${row.penetrationRate.toFixed(2)}%` },
  { colKey: 'bevSales', title: $t('sales.analysis.nev.bevSales'), width: 130, cell: (_h: any, { row }: any) => row.bevSales?.toLocaleString() ?? '-' },
  { colKey: 'bevRatio', title: $t('sales.analysis.nev.bevRatioInNev'), width: 170, cell: (_h: any, { row }: any) => row.bevRatio == null ? '-' : `${row.bevRatio.toFixed(2)}%` },
];

function buildRows(shareTrend: any[], breakdownTrend: any[]) {
  if (!Array.isArray(shareTrend) || !Array.isArray(breakdownTrend)) {
    tableData.value = [];
    return;
  }

  const bevMap = new Map<string, { bevRatio: null | number; bevSales: null | number }>();
  for (const item of breakdownTrend) {
    const key = `${item.year}-${item.month}`;
    bevMap.set(key, {
      bevSales: item.bev_sales ?? null,
      bevRatio: item.bev_ratio ?? null,
    });
  }

  tableData.value = shareTrend.map((item: any, index: number) => {
    const key = `${item.year}-${item.month}`;
    const bevInfo = bevMap.get(key);
    return {
      key: index,
      time: `${item.year}-${String(item.month).padStart(2, '0')}`,
      totalSales: item.total_sales ?? null,
      nevSales: item.nev_sales ?? null,
      penetrationRate: item.nev_penetration_rate ?? null,
      bevSales: bevInfo?.bevSales ?? null,
      bevRatio: bevInfo?.bevRatio ?? null,
    };
  }).toReversed();
}

watch(
  () => [props.shareTrend, props.breakdownTrend] as const,
  ([share, breakdown]) => buildRows(share, breakdown),
  { deep: true, immediate: true },
);
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

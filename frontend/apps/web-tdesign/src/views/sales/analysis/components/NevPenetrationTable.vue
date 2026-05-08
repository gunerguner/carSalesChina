<script lang="ts" setup>
import { Table } from 'tdesign-vue-next';
import { onMounted, ref } from 'vue';

import { $t } from '#/locales';

import { getNevShareTrendApi } from '#/api/sales/analysis';

const loading = ref(false);
const tableData = ref<any[]>([]);

const columns = [
  { colKey: 'time', title: $t('sales.analysis.nev.time'), width: 120 },
  { colKey: 'totalSales', title: $t('sales.analysis.nev.totalSales'), width: 130, cell: (_h: any, { row }: any) => row.totalSales?.toLocaleString() ?? '-' },
  { colKey: 'nevSales', title: $t('sales.analysis.nev.nevSales'), width: 130, cell: (_h: any, { row }: any) => row.nevSales?.toLocaleString() ?? '-' },
  { colKey: 'penetrationRate', title: $t('sales.analysis.nev.penetrationRate'), width: 140, cell: (_h: any, { row }: any) => row.penetrationRate != null ? `${row.penetrationRate.toFixed(2)}%` : '-' },
  { colKey: 'bevShare', title: $t('sales.analysis.nev.bevShare'), width: 120, cell: (_h: any, { row }: any) => row.bevShare != null ? `${row.bevShare.toFixed(2)}%` : '-' },
  { colKey: 'phevShare', title: $t('sales.analysis.nev.phevShare'), width: 120, cell: (_h: any, { row }: any) => row.phevShare != null ? `${row.phevShare.toFixed(2)}%` : '-' },
];

async function fetchData() {
  loading.value = true;
  try {
    const data = await getNevShareTrendApi({ granularity: 'monthly' });

    if (!data || !Array.isArray(data)) {
      tableData.value = [];
      return;
    }

    tableData.value = data.map((item: any, index: number) => ({
      key: index,
      time: `${item.year}-${String(item.month).padStart(2, '0')}`,
      totalSales: item.total_sales ?? null,
      nevSales: item.nev_sales ?? null,
      penetrationRate: item.nev_penetration_rate ?? null,
      bevShare: item.bev_sales ?? null,
      phevShare: item.phev_sales ?? null,
    }));
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    :loading="loading"
    row-key="key"
    size="small"
    bordered
    :pagination="{ pageSize: 12 }"
  />
</template>

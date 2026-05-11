<script lang="ts" setup>
import { onMounted, ref } from 'vue';

import { Table } from 'tdesign-vue-next';

import { getOriginShareTrendApi } from '#/api/sales/analysis';
import { $t } from '#/locales';

const loading = ref(false);
const tableData = ref<any[]>([]);

const columns = [
  { colKey: 'time', title: $t('sales.analysis.origin.time'), width: 120 },
  { colKey: 'domestic', title: $t('sales.analysis.origin.domestic'), width: 100, cell: (_h: any, { row }: any) => row.domestic == null ? '-' : `${row.domestic.toFixed(2)}%` },
  { colKey: 'german', title: $t('sales.analysis.origin.german'), width: 100, cell: (_h: any, { row }: any) => row.german == null ? '-' : `${row.german.toFixed(2)}%` },
  { colKey: 'japanese', title: $t('sales.analysis.origin.japanese'), width: 100, cell: (_h: any, { row }: any) => row.japanese == null ? '-' : `${row.japanese.toFixed(2)}%` },
  { colKey: 'american', title: $t('sales.analysis.origin.american'), width: 100, cell: (_h: any, { row }: any) => row.american == null ? '-' : `${row.american.toFixed(2)}%` },
  { colKey: 'european', title: $t('sales.analysis.origin.european'), width: 100, cell: (_h: any, { row }: any) => row.european == null ? '-' : `${row.european.toFixed(2)}%` },
  { colKey: 'korean', title: $t('sales.analysis.origin.korean'), width: 100, cell: (_h: any, { row }: any) => row.korean == null ? '-' : `${row.korean.toFixed(2)}%` },
  { colKey: 'other', title: $t('sales.analysis.origin.other'), width: 100, cell: (_h: any, { row }: any) => row.other == null ? '-' : `${row.other.toFixed(2)}%` },
];

async function fetchData() {
  loading.value = true;
  try {
    const data = await getOriginShareTrendApi({ granularity: 'monthly' });

    if (!data || !Array.isArray(data)) {
      tableData.value = [];
      return;
    }

    tableData.value = data.map((item: any, index: number) => ({
      key: index,
      time: `${item.year}-${String(item.month).padStart(2, '0')}`,
      domestic: item.domestic ?? null,
      german: item.german ?? null,
      japanese: item.japanese ?? null,
      american: item.american ?? null,
      european: item.european ?? null,
      korean: item.korean ?? null,
      other: item.other ?? null,
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

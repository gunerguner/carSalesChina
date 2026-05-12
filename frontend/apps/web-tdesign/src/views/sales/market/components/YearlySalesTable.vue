<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';

import { Table } from 'tdesign-vue-next';

import { getMarketTrendApi } from '#/api/sales/market';
import { $t } from '#/locales';

const props = defineProps<{
  dataType: 'production' | 'retail';
  levelType: string;
}>();

const loading = ref(false);
const tableData = ref<any[]>([]);

const columns = [
  { colKey: 'year', title: $t('sales.market.yearly.year'), width: 100 },
  {
    colKey: 'sales',
    title: $t('sales.market.yearly.sales'),
    width: 150,
    cell: (_h: any, { row }: any) => row.sales?.toLocaleString() ?? '-',
  },
  {
    colKey: 'yoyGrowth',
    title: $t('sales.market.yearly.yoyGrowth'),
    width: 140,
    cell: (_h: any, { row }: any) => formatGrowth(row.yoyGrowth),
  },
];

function formatGrowth(val: null | number | undefined) {
  if (val == null) return '-';
  const formatted = val.toFixed(2) + '%';
  return formatted;
}

async function fetchData() {
  loading.value = true;
  try {
    const data = await getMarketTrendApi({
      level_type: props.levelType,
      granularity: 'yearly',
      data_type: props.dataType,
      date_type: 'monthly',
    });

    if (!data || !Array.isArray(data)) {
      tableData.value = [];
      return;
    }

    tableData.value = data.map((item: any, index: number) => ({
      key: index,
      year: item.year,
      sales: item.sales ?? null,
      yoyGrowth: item.yoy_growth ?? null,
    })).toReversed();
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());

watch([() => props.levelType, () => props.dataType], () => fetchData());
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    :loading="loading"
    row-key="key"
    size="small"
    bordered
  />
</template>
<script lang="ts" setup>
import { Table } from 'tdesign-vue-next';
import { onMounted, ref, watch } from 'vue';

import { $t } from '#/locales';

import { getMarketYearlyApi } from '#/api/sales/market';

const props = defineProps<{
  year: number;
  energyType: string;
  dataType: 'retail' | 'wholesale' | 'production';
}>();

const loading = ref(false);
const tableData = ref<any[]>([]);

const salesFieldMap: Record<string, string> = {
  all: 'total_sales',
  fuel: 'ice_sales',
  bev: 'bev_sales',
  phev: 'phev_sales',
  hybrid: 'hybrid_sales',
};

const columns = [
  { colKey: 'month', title: $t('sales.market.monthly.month'), width: 80 },
  { colKey: 'sales', title: $t('sales.market.monthly.sales'), width: 120, cell: (_h: any, { row }: any) => row.sales?.toLocaleString() ?? '-' },
  { colKey: 'momGrowth', title: $t('sales.market.monthly.momGrowth'), width: 130, cell: (_h: any, { row }: any) => formatGrowth(row.momGrowth) },
  { colKey: 'yoyGrowth', title: $t('sales.market.monthly.yoyGrowth'), width: 130, cell: (_h: any, { row }: any) => formatGrowth(row.yoyGrowth) },
  { colKey: 'totalSales', title: $t('sales.market.monthly.totalSales'), width: 120, cell: (_h: any, { row }: any) => row.totalSales?.toLocaleString() ?? '-' },
  { colKey: 'nevSales', title: $t('sales.market.monthly.nevSales'), width: 120, cell: (_h: any, { row }: any) => row.nevSales?.toLocaleString() ?? '-' },
];

function formatGrowth(val: number | null | undefined) {
  if (val == null) return '-';
  const formatted = val.toFixed(2) + '%';
  const color = val > 0 ? 'text-red-500' : val < 0 ? 'text-green-500' : '';
  return { class: color, content: formatted };
}

async function fetchData() {
  loading.value = true;
  try {
    const data = await getMarketYearlyApi({
      year: props.year,
      energy_type: props.energyType,
      data_type: props.dataType,
    });

    if (!data || !Array.isArray(data)) {
      tableData.value = [];
      return;
    }

    const field = salesFieldMap[props.energyType] || 'total_sales';
    tableData.value = data.map((item: any, index: number) => ({
      key: index,
      month: `${item.month}月`,
      sales: item[field] ?? null,
      momGrowth: item.mom_growth ?? null,
      yoyGrowth: item.yoy_growth ?? null,
      totalSales: item.total_sales ?? null,
      nevSales: item.nev_sales ?? null,
    }));
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());

watch([() => props.year, () => props.energyType, () => props.dataType], () => fetchData());
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    :loading="loading"
    row-key="key"
    size="small"
    bordered
    :pagination="{ pageSize: 12, showPageSize: false }"
  />
</template>

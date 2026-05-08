<script lang="ts" setup>
import { Table } from 'tdesign-vue-next';
import { onMounted, ref, watch } from 'vue';

import { $t } from '#/locales';

import { getMarketTrendApi } from '#/api/sales/market';

const props = defineProps<{
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
  { colKey: 'year', title: $t('sales.market.yearly.year'), width: 100 },
  { colKey: 'sales', title: $t('sales.market.yearly.sales'), width: 150, cell: (h: any, { row }: any) => row.sales?.toLocaleString() ?? '-' },
  { colKey: 'yoyGrowth', title: $t('sales.market.yearly.yoyGrowth'), width: 140, cell: (_h: any, { row }: any) => formatGrowth(row.yoyGrowth) },
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
    const data = await getMarketTrendApi({
      energy_type: props.energyType,
      granularity: 'yearly',
      data_type: props.dataType,
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
    }));
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());

watch([() => props.energyType, () => props.dataType], () => fetchData());
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

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';

import { Table } from 'tdesign-vue-next';

import { getBrandRankingApi, getBrandRankingYearlyApi } from '#/api/sales/brand';
import { $t } from '#/locales';

const props = defineProps<{
  dataType: 'production' | 'retail' | 'wholesale';
  granularity: 'monthly' | 'yearly';
  month: number;
  year: number;
}>();

const loading = ref(false);
const tableData = ref<any[]>([]);

const columns = [
  { colKey: 'rank', title: $t('sales.brand.ranking.rank'), width: 70 },
  { colKey: 'brandName', title: $t('sales.brand.ranking.brand'), width: 150 },
  { colKey: 'sales', title: $t('sales.brand.ranking.sales'), width: 130, cell: (_h: any, { row }: any) => row.sales?.toLocaleString() ?? '-' },
  { colKey: 'origin', title: $t('sales.brand.ranking.origin'), width: 100 },
  { colKey: 'momGrowth', title: $t('sales.brand.ranking.momGrowth'), width: 130, cell: (_h: any, { row }: any) => formatGrowth(row.momGrowth) },
  { colKey: 'yoyGrowth', title: $t('sales.brand.ranking.yoyGrowth'), width: 130, cell: (_h: any, { row }: any) => formatGrowth(row.yoyGrowth) },
];

function formatGrowth(val: null | number | undefined) {
  if (val == null) return '-';
  const formatted = val.toFixed(2) + '%';
  const color = val > 0 ? 'text-red-500' : (val < 0 ? 'text-green-500' : '');
  return { class: color, content: formatted };
}

function extractList(res: any): any[] {
  if (Array.isArray(res)) return res;
  if (res?.data && Array.isArray(res.data)) return res.data;
  return [];
}

async function fetchData() {
  loading.value = true;
  try {
    let res: any;
    res = await (props.granularity === 'yearly' ? getBrandRankingYearlyApi({
        year: props.year,
        data_type: props.dataType,
      }) : getBrandRankingApi({
        year: props.year,
        month: props.month,
        data_type: props.dataType,
      }));

    const list = extractList(res);

    tableData.value = list.map((item: any, index: number) => ({
      key: index,
      rank: index + 1,
      brandName: item.brand_name,
      sales: item.sales_volume ?? item.total_sales ?? item.sales ?? null,
      origin: item.origin ?? '-',
      momGrowth: item.mom_growth ?? null,
      yoyGrowth: item.yoy_growth ?? null,
    }));
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());

watch([() => props.year, () => props.month, () => props.granularity, () => props.dataType], () => fetchData());
</script>

<template>
  <Table
    :columns="columns"
    :data="tableData"
    :loading="loading"
    row-key="key"
    size="small"
    bordered
    :pagination="{ pageSize: 15, showPageSize: false }"
  />
</template>
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
  { colKey: 'brandName', title: $t('sales.brand.ranking.brand'), width: 200 },
  { colKey: 'sales', title: $t('sales.brand.ranking.sales'), width: 160, cell: (_h: any, { row }: any) => row.sales?.toLocaleString() ?? '-' },
];

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

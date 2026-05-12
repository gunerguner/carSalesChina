<script setup lang="ts">
import { h, onMounted, ref, watch } from 'vue';

import { Table } from 'tdesign-vue-next';

import { getMarketYearlyApi } from '#/api/sales/market';
import { $t } from '#/locales';

const props = defineProps<{
  dataType: 'production' | 'retail';
  levelType: string;
  year: number;
}>();

const loading = ref(false);
const tableData = ref<any[]>([]);

const columns = [
  { colKey: 'year', title: $t('sales.market.yearly.year'), width: 100, sorter: (a: any, b: any) => a.year - b.year || a.monthNum - b.monthNum },
  { colKey: 'month', title: $t('sales.market.monthly.month'), width: 80, sorter: (a: any, b: any) => a.monthNum - b.monthNum },
  {
    colKey: 'sales',
    title: $t('sales.market.monthly.sales'),
    width: 140,
    cell: (_h: any, { row }: any) => row.sales?.toLocaleString() ?? '-',
  },
  {
    colKey: 'momGrowth',
    title: $t('sales.market.monthly.momGrowth'),
    width: 130,
    cell: (_h: any, { row }: any) => formatGrowth(row.momGrowth),
  },
  {
    colKey: 'yoyGrowth',
    title: $t('sales.market.monthly.yoyGrowth'),
    width: 130,
    cell: (_h: any, { row }: any) => formatGrowth(row.yoyGrowth),
  },
];

function formatGrowth(val: null | number | undefined) {
  if (val == null) return h('span', { style: { color: '#999' } }, '-');
  const formatted = val.toFixed(2) + '%';
  const textColor = val > 0 ? '#ef4444' : (val < 0 ? '#22c55e' : '#666');
  return h('span', { style: { color: textColor, fontWeight: 500 } }, formatted);
}

async function fetchData() {
  loading.value = true;
  try {
    const data = await getMarketYearlyApi({
      year: props.year,
      level_type: props.levelType,
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
      month: `${item.month}月`,
      monthNum: item.month,
      sales: item.sales ?? null,
      momGrowth: item.mom_growth ?? null,
      yoyGrowth: item.yoy_growth ?? null,
    })).toReversed();
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());

watch([() => props.year, () => props.levelType, () => props.dataType], () => fetchData());
</script>

<template>
  <div class="px-4 py-3">
    <Table
      :columns="columns"
      :data="tableData"
      :loading="loading"
      row-key="key"
      size="small"
      bordered
    />
  </div>
</template>
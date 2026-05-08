<script lang="ts" setup>
import type { PrimaryTableCol } from 'tdesign-vue-next';

import { Table } from 'tdesign-vue-next';
import { computed, onMounted, ref, watch } from 'vue';

import { $t } from '#/locales';

import { getBrandCompareTrendApi } from '#/api/sales/brand';

const props = defineProps<{
  brands: string[];
  granularity: 'monthly' | 'yearly';
  dataType: 'retail' | 'wholesale' | 'production';
}>();

const loading = ref(false);
const tableData = ref<any[]>([]);

const columns = computed<PrimaryTableCol[]>(() => {
  const base: PrimaryTableCol[] = [
    { colKey: 'time', title: $t('sales.brand.compare.time'), width: 120 },
  ];
  for (const brand of props.brands) {
    base.push({
      colKey: `brand_${brand}`,
      title: brand,
      width: 150,
      cell: (_h: any, { row }: any) => row[`brand_${brand}`]?.toLocaleString() ?? '-',
    });
  }
  if (props.brands.length === 2) {
    base.push({
      colKey: 'diff',
      title: $t('sales.brand.compare.diff'),
      width: 130,
      cell: (_h: any, { row }: any) => row.diff != null ? row.diff.toLocaleString() : '-',
    });
  }
  return base;
});

function makeTimeKey(item: any): string {
  return props.granularity === 'monthly'
    ? `${item.year}-${String(item.month).padStart(2, '0')}`
    : String(item.year);
}

async function fetchData() {
  if (props.brands.length < 2) {
    tableData.value = [];
    return;
  }

  loading.value = true;
  try {
    const data: any = await getBrandCompareTrendApi({
      brand_names: props.brands.join(','),
      data_type: props.dataType,
      granularity: props.granularity,
    });

    if (!Array.isArray(data)) {
      tableData.value = [];
      return;
    }

    const timeMap = new Map<string, any>();
    for (const brand of data) {
      for (const point of brand.trend) {
        const timeKey = makeTimeKey(point);
        if (!timeMap.has(timeKey)) {
          timeMap.set(timeKey, { key: timeKey, time: timeKey });
        }
        const row = timeMap.get(timeKey)!;
        row[`brand_${brand.brand_name}`] = point.sales ?? 0;
      }
    }

    tableData.value = [...timeMap.values()].sort((a, b) => a.time.localeCompare(b.time)).map((row) => {
      if (props.brands.length === 2) {
        const a = row[`brand_${props.brands[0]}`];
        const b = row[`brand_${props.brands[1]}`];
        if (a != null && b != null) {
          row.diff = a - b;
        }
      }
      return row;
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());

watch([() => props.brands, () => props.granularity, () => props.dataType], () => fetchData(), { deep: true });
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
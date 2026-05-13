<script lang="ts" setup>
import { Card } from 'tdesign-vue-next';

import { $t } from '#/locales';

import BrandSelectBar from './components/BrandSelectBar.vue';
import BrandTrendChart from './components/BrandTrendChart.vue';
import BrandTrendTable from './components/BrandTrendTable.vue';
import { useBrandSalesData } from './useBrandSalesData';

const {
  activeSeries,
  dataType,
  fetchRawData,
  granularity,
  loading,
  selectedBrands,
  timeLabels,
} = useBrandSalesData();

async function onFilterChange(payload: {
  brands: string[];
  dataType: 'production' | 'retail';
  granularity: 'monthly' | 'yearly';
}) {
  selectedBrands.value = payload.brands;
  dataType.value = payload.dataType;
  granularity.value = payload.granularity;
  await fetchRawData();
}
</script>

<template>
  <div class="p-5">
    <BrandSelectBar @change="onFilterChange" />

    <Card :title="$t('sales.brand.trend.chartTitle')" class="mb-4">
      <BrandTrendChart
        :data="activeSeries"
        :loading="loading"
        :time-labels="timeLabels"
      />
    </Card>

    <Card :title="$t('sales.brand.trend.tableTitle')">
      <BrandTrendTable
        :data="activeSeries"
        :loading="loading"
        :time-labels="timeLabels"
      />
    </Card>
  </div>
</template>

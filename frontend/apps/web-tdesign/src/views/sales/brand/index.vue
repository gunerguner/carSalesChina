<script lang="ts" setup>
import { watch } from 'vue';

import { Card } from 'tdesign-vue-next';

import { message } from '#/adapter/tdesign';
import { $t } from '#/locales';

import BrandSelectBar from './components/BrandSelectBar.vue';
import BrandTrendChart from './components/BrandTrendChart.vue';
import BrandTrendTable from './components/BrandTrendTable.vue';
import { useBrandSalesData } from './useBrandSalesData';

const {
  activeSeries,
  dataType,
  error,
  fetchRawData,
  granularity,
  loading,
  selectedBrands,
  timeLabels,
} = useBrandSalesData();

watch(error, (value) => {
  if (value) {
    message.error($t('common.requestFailed'));
  }
});

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

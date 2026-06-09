<script setup lang="ts">
import type { BrandTrendGranularity } from './useBrandSalesData';

import { Card } from 'tdesign-vue-next';

import DataLoadState from '#/components/DataLoadState.vue';
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
  tableTimeLabelMaxCount,
  timeLabels,
} = useBrandSalesData();

async function onFilterChange(payload: {
  brands: string[];
  dataType: 'production' | 'retail';
  granularity: BrandTrendGranularity;
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

    <DataLoadState
      :error="error"
      :loading="loading"
      @retry="fetchRawData(true)"
    >
      <Card :title="$t('sales.brand.trend.chartTitle')" class="mb-4">
        <BrandTrendChart :data="activeSeries" :time-labels="timeLabels" />
      </Card>

      <Card :title="$t('sales.brand.trend.tableTitle')">
        <BrandTrendTable
          :data="activeSeries"
          :data-type="dataType"
          :time-label-max-count="tableTimeLabelMaxCount"
          :time-labels="timeLabels"
        />
      </Card>
    </DataLoadState>
  </div>
</template>

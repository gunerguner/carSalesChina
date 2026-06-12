<script setup lang="ts">
import type { BrandTrendGranularity } from './useBrandData';

import type { DataType } from '#/types/domain';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Card } from 'tdesign-vue-next';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import FilterPanel from '#/components/FilterPanel.vue';
import { $t } from '#/locales';

import BrandSelectBar from './components/BrandSelectBar.vue';
import { buildBrandTrendChartOption } from './components/brandTrendChart';
import BrandTrendTable from './components/BrandTrendTable.vue';
import { useBrandData } from './useBrandData';

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
} = useBrandData();

const chartOption = computed(() =>
  buildBrandTrendChartOption(
    { data: activeSeries.value, timeLabels: timeLabels.value },
    preferences.app.locale,
    $t,
  ),
);

async function onFilterChange(payload: {
  brands: string[];
  dataType: DataType;
  granularity: BrandTrendGranularity;
}) {
  selectedBrands.value = payload.brands;
  dataType.value = payload.dataType;
  granularity.value = payload.granularity;
  await fetchRawData();
}
</script>

<template>
  <div class="page-content">
    <FilterPanel>
      <BrandSelectBar @change="onFilterChange" />
    </FilterPanel>

    <DataLoadState
      :error="error"
      :loading="loading"
      @retry="fetchRawData(true)"
    >
      <Card
        :title="$t('pages.brand.trend.chartTitle')"
        class="section-card"
      >
        <ChartCard :option="chartOption" />
      </Card>

      <Card
        :title="$t('pages.brand.trend.tableTitle')"
        class="section-card"
      >
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

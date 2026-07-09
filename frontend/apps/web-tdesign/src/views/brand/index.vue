<script setup lang="ts">
import { computed, watch } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import FilterPanel from '#/components/FilterPanel.vue';
import SectionCard from '#/components/SectionCard.vue';
import { usePageRefresh } from '#/composables/usePageRefresh';
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

usePageRefresh(() => fetchRawData(true), { initialLoad: () => {} });

const chartOption = computed(() => {
  // 显式读取主题 mode 以建立响应式依赖；切换 light/dark 时 option 重建
  void preferences.theme.mode;
  return buildBrandTrendChartOption(
    { data: activeSeries.value, timeLabels: timeLabels.value },
    preferences.app.locale,
    $t,
  );
});

// 任一筛选条件变化即触发拉取（与原 onFilterChange 行为一致）
watch(
  [selectedBrands, dataType, granularity],
  () => {
    void fetchRawData();
  },
  { deep: true },
);
</script>

<template>
  <div class="page-content">
    <FilterPanel>
      <BrandSelectBar
        v-model:selected-brands="selectedBrands"
        v-model:data-type="dataType"
        v-model:granularity="granularity"
      />
    </FilterPanel>

    <DataLoadState
      :error="error"
      :loading="loading"
      @retry="fetchRawData(true)"
    >
      <SectionCard :title="$t('pages.brand.trend.chartTitle')">
        <ChartCard :option="chartOption" />
      </SectionCard>

      <SectionCard :title="$t('pages.brand.trend.tableTitle')">
        <BrandTrendTable
          :data="activeSeries"
          :data-type="dataType"
          :time-label-max-count="tableTimeLabelMaxCount"
          :time-labels="timeLabels"
        />
      </SectionCard>
    </DataLoadState>
  </div>
</template>

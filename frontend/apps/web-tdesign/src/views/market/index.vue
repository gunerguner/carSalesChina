<script setup lang="ts">
import type { MarketTableInput } from './components/marketSalesTable';
import type { MarketTrendChartInput } from './components/marketTrendChart';
import type { MarketPeriodGranularity } from './types';

import type { DataType, LevelType } from '#/utils/types';

import { computed, onMounted, ref } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import FilterPanel from '#/components/FilterPanel.vue';
import SectionCard from '#/components/SectionCard.vue';
import { $t } from '#/locales';

import MarketFilterBar from './components/MarketFilterBar.vue';
import MarketTable from './components/MarketTable.vue';
import { buildMarketTrendChartOption } from './components/marketTrendChart';
import { useMarketData } from './useMarketData';

interface MarketPeriodView {
  chartTitleKey: string;
  tableTitleKey: string;
  input: MarketTrendChartInput;
  tableInput: MarketTableInput;
}

const levelType = ref<LevelType>('all');
const dataType = ref<DataType>('retail');
const period = ref<MarketPeriodGranularity>('monthly');

const {
  error,
  loading,
  fetchAll,
  getMonthlyTrend,
  getMonthlyDetail,
  getQuarterlyTrend,
  getYearlyTrend,
} = useMarketData();

onMounted(() => fetchAll());

const activeMarketView = computed((): MarketPeriodView => {
  const lt = levelType.value;
  const dt = dataType.value;

  const configs: Record<MarketPeriodGranularity, MarketPeriodView> = {
    monthly: {
      chartTitleKey: 'pages.market.monthly.chartTitle',
      tableTitleKey: 'pages.market.monthly.title',
      input: { kind: 'monthly', data: getMonthlyTrend(lt, dt) },
      tableInput: { kind: 'monthly', data: getMonthlyDetail(lt, dt) },
    },
    quarterly: {
      chartTitleKey: 'pages.market.quarterly.chartTitle',
      tableTitleKey: 'pages.market.quarterly.title',
      input: { kind: 'quarterly', data: getQuarterlyTrend(lt, dt) },
      tableInput: { kind: 'quarterly', data: getQuarterlyTrend(lt, dt) },
    },
    yearly: {
      chartTitleKey: 'pages.market.yearly.chartTitle',
      tableTitleKey: 'pages.market.yearly.title',
      input: { kind: 'yearly', data: getYearlyTrend(lt, dt) },
      tableInput: { kind: 'yearly', data: getYearlyTrend(lt, dt) },
    },
  };

  return configs[period.value];
});

const chartOption = computed(() =>
  buildMarketTrendChartOption(
    activeMarketView.value.input,
    preferences.app.locale,
    $t,
  ),
);

const chartTitle = computed(() => $t(activeMarketView.value.chartTitleKey));
const tableTitle = computed(() => $t(activeMarketView.value.tableTitleKey));
</script>

<template>
  <div class="page-content">
    <FilterPanel>
      <MarketFilterBar
        v-model:level-type="levelType"
        v-model:data-type="dataType"
        v-model:period="period"
      />
    </FilterPanel>

    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <SectionCard :title="chartTitle">
        <ChartCard :option="chartOption" />
      </SectionCard>
      <SectionCard :title="tableTitle">
        <MarketTable
          :key="period"
          v-bind="activeMarketView.tableInput"
          :data-type="dataType"
        />
      </SectionCard>
    </DataLoadState>
  </div>
</template>

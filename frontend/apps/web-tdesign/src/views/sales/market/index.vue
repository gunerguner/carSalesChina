<script setup lang="ts">
import type { MarketPeriodGranularity } from './types';

import { computed, onMounted, ref } from 'vue';

import { preferences } from '@vben/preferences';

import { Card } from 'tdesign-vue-next';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import SalesFilterPanel from '#/components/SalesFilterPanel.vue';
import { $t } from '#/locales';

import MarketSalesTable from './components/MarketSalesTable.vue';
import { buildMarketTrendChartOption } from './components/marketTrendChart';
import SalesFilterBar from './components/SalesFilterBar.vue';
import { useMarketData } from './useMarketData';

const levelType = ref('all');
const dataType = ref<'production' | 'retail'>('retail');
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

const chartOption = computed(() => {
  const locale = preferences.app.locale;
  const lt = levelType.value;
  const dt = dataType.value;
  if (period.value === 'monthly') {
    return buildMarketTrendChartOption(
      { kind: 'monthly', data: getMonthlyTrend(lt, dt) },
      locale,
      $t,
    );
  }
  if (period.value === 'quarterly') {
    return buildMarketTrendChartOption(
      { kind: 'quarterly', data: getQuarterlyTrend(lt, dt) },
      locale,
      $t,
    );
  }
  return buildMarketTrendChartOption(
    { kind: 'yearly', data: getYearlyTrend(lt, dt) },
    locale,
    $t,
  );
});

const monthlyTableData = computed(() =>
  getMonthlyDetail(levelType.value, dataType.value),
);
const quarterlyTableData = computed(() =>
  getQuarterlyTrend(levelType.value, dataType.value),
);
const yearlyTableData = computed(() =>
  getYearlyTrend(levelType.value, dataType.value),
);

const chartTitle = computed(() => {
  if (period.value === 'monthly') {
    return $t('sales.market.monthly.chartTitle');
  }
  if (period.value === 'quarterly') {
    return $t('sales.market.quarterly.chartTitle');
  }
  return $t('sales.market.yearly.chartTitle');
});

const tableTitle = computed(() => {
  if (period.value === 'monthly') {
    return $t('sales.market.monthly.title');
  }
  if (period.value === 'quarterly') {
    return $t('sales.market.quarterly.title');
  }
  return $t('sales.market.yearly.title');
});
</script>

<template>
  <div class="sales-page-content">
    <SalesFilterPanel>
      <SalesFilterBar
        v-model:level-type="levelType"
        v-model:data-type="dataType"
        v-model:period="period"
      />
    </SalesFilterPanel>

    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <Card :title="chartTitle" class="sales-section-card">
        <ChartCard :option="chartOption" />
      </Card>
      <Card :title="tableTitle" class="sales-section-card">
        <MarketSalesTable
          v-if="period === 'monthly'"
          :data="monthlyTableData"
          :data-type="dataType"
          kind="monthly"
        />
        <MarketSalesTable
          v-else-if="period === 'quarterly'"
          :data="quarterlyTableData"
          :data-type="dataType"
          kind="quarterly"
        />
        <MarketSalesTable
          v-else
          :data="yearlyTableData"
          :data-type="dataType"
          kind="yearly"
        />
      </Card>
    </DataLoadState>
  </div>
</template>

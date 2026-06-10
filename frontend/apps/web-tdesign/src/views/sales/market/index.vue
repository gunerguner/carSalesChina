<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

import { preferences } from '@vben/preferences';

import { Card, TabPanel, Tabs } from 'tdesign-vue-next';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import { $t } from '#/locales';

import MarketSalesTable from './components/MarketSalesTable.vue';
import { buildMarketTrendChartOption } from './components/marketTrendChart';
import SalesFilterBar from './components/SalesFilterBar.vue';
import { useMarketData } from './useMarketData';

const levelType = ref('all');
const dataType = ref<'production' | 'retail'>('retail');
const activeTab = ref('monthly');

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

const monthlyTrendData = computed(() =>
  getMonthlyTrend(levelType.value, dataType.value),
);
const monthlyDetailData = computed(() =>
  getMonthlyDetail(levelType.value, dataType.value),
);
const quarterlyTrendData = computed(() =>
  getQuarterlyTrend(levelType.value, dataType.value),
);
const yearlyTrendData = computed(() =>
  getYearlyTrend(levelType.value, dataType.value),
);

const monthlyChartOption = computed(() =>
  buildMarketTrendChartOption(
    { kind: 'monthly', data: monthlyTrendData.value },
    preferences.app.locale,
    $t,
  ),
);
const quarterlyChartOption = computed(() =>
  buildMarketTrendChartOption(
    { kind: 'quarterly', data: quarterlyTrendData.value },
    preferences.app.locale,
    $t,
  ),
);
const yearlyChartOption = computed(() =>
  buildMarketTrendChartOption(
    { kind: 'yearly', data: yearlyTrendData.value },
    preferences.app.locale,
    $t,
  ),
);
</script>

<template>
  <div class="p-5">
    <SalesFilterBar
      v-model:level-type="levelType"
      v-model:data-type="dataType"
    />

    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <Tabs v-model="activeTab">
        <TabPanel
          :label="$t('sales.market.monthly.title')"
          destroy-on-hide
          value="monthly"
        >
          <Card :title="$t('sales.market.monthly.chartTitle')" class="mb-4">
            <ChartCard :option="monthlyChartOption" />
          </Card>
          <Card :title="$t('sales.market.monthly.title')">
            <MarketSalesTable
              :data="monthlyDetailData"
              :data-type="dataType"
              kind="monthly"
            />
          </Card>
        </TabPanel>
        <TabPanel
          :label="$t('sales.market.quarterly.title')"
          destroy-on-hide
          value="quarterly"
        >
          <Card :title="$t('sales.market.quarterly.chartTitle')" class="mb-4">
            <ChartCard :option="quarterlyChartOption" />
          </Card>
          <Card :title="$t('sales.market.quarterly.title')">
            <MarketSalesTable
              :data="quarterlyTrendData"
              :data-type="dataType"
              kind="quarterly"
            />
          </Card>
        </TabPanel>
        <TabPanel
          :label="$t('sales.market.yearly.title')"
          destroy-on-hide
          value="yearly"
        >
          <Card :title="$t('sales.market.yearly.chartTitle')" class="mb-4">
            <ChartCard :option="yearlyChartOption" />
          </Card>
          <Card :title="$t('sales.market.yearly.title')">
            <MarketSalesTable
              :data="yearlyTrendData"
              :data-type="dataType"
              kind="yearly"
            />
          </Card>
        </TabPanel>
      </Tabs>
    </DataLoadState>
  </div>
</template>

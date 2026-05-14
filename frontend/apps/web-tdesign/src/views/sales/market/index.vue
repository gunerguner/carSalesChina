<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

import { Card, Loading, TabPanel, Tabs } from 'tdesign-vue-next';

import { $t } from '#/locales';

import MonthlySalesChart from './components/MonthlySalesChart.vue';
import MonthlySalesTable from './components/MonthlySalesTable.vue';
import QuarterlySalesChart from './components/QuarterlySalesChart.vue';
import QuarterlySalesTable from './components/QuarterlySalesTable.vue';
import SalesFilterBar from './components/SalesFilterBar.vue';
import YearlySalesChart from './components/YearlySalesChart.vue';
import YearlySalesTable from './components/YearlySalesTable.vue';
import { useMarketData } from './useMarketData';

const levelType = ref('all');
const dataType = ref<'production' | 'retail'>('retail');
const activeTab = ref('monthly');

const { loading, fetchAll, getMonthlyTrend, getMonthlyDetail, getQuarterlyTrend, getYearlyTrend } =
  useMarketData();

onMounted(() => fetchAll());

const monthlyTrendData = computed(() => getMonthlyTrend(levelType.value, dataType.value));
const monthlyDetailData = computed(() => getMonthlyDetail(levelType.value, dataType.value));
const quarterlyTrendData = computed(() => getQuarterlyTrend(levelType.value, dataType.value));
const yearlyTrendData = computed(() => getYearlyTrend(levelType.value, dataType.value));
</script>

<template>
  <div class="p-5">
    <SalesFilterBar v-model:level-type="levelType" v-model:data-type="dataType" />

    <Loading
      :loading="loading"
      size="medium"
      :text="$t('sales.common.loading')"
      style="min-height: 200px"
    >
      <Tabs v-model="activeTab">
        <TabPanel
          :label="$t('sales.market.monthly.title')"
          destroy-on-hide
          value="monthly"
        >
          <Card :title="$t('sales.market.monthly.chartTitle')" class="mb-4">
            <MonthlySalesChart :data="monthlyTrendData" />
          </Card>
          <Card :title="$t('sales.market.monthly.title')">
            <MonthlySalesTable :data="monthlyDetailData" />
          </Card>
        </TabPanel>
        <TabPanel
          :label="$t('sales.market.quarterly.title')"
          destroy-on-hide
          value="quarterly"
        >
          <Card :title="$t('sales.market.quarterly.chartTitle')" class="mb-4">
            <QuarterlySalesChart :data="quarterlyTrendData" />
          </Card>
          <Card :title="$t('sales.market.quarterly.title')">
            <QuarterlySalesTable :data="quarterlyTrendData" />
          </Card>
        </TabPanel>
        <TabPanel
          :label="$t('sales.market.yearly.title')"
          destroy-on-hide
          value="yearly"
        >
          <Card :title="$t('sales.market.yearly.chartTitle')" class="mb-4">
            <YearlySalesChart :data="yearlyTrendData" />
          </Card>
          <Card :title="$t('sales.market.yearly.title')">
            <YearlySalesTable :data="yearlyTrendData" />
          </Card>
        </TabPanel>
      </Tabs>
    </Loading>
  </div>
</template>

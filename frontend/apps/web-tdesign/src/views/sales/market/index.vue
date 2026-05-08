<script lang="ts" setup>
import { Card, TabPanel, Tabs } from 'tdesign-vue-next';
import { onMounted, ref } from 'vue';

import { $t } from '#/locales';

import { getMarketOverviewApi } from '#/api/sales/market';

import MonthlySalesChart from './components/MonthlySalesChart.vue';
import MonthlySalesTable from './components/MonthlySalesTable.vue';
import SalesFilterBar from './components/SalesFilterBar.vue';
import YearlySalesChart from './components/YearlySalesChart.vue';
import YearlySalesTable from './components/YearlySalesTable.vue';

const energyType = ref('all');
const dataType = ref<'retail' | 'wholesale' | 'production'>('retail');
const activeTab = ref('monthly');

const overviewLoading = ref(false);
const overview = ref<any>({});

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

async function fetchOverview() {
  overviewLoading.value = true;
  try {
    const data = await getMarketOverviewApi({
      year: currentYear,
      month: currentMonth,
      energy_type: energyType.value,
      data_type: dataType.value,
    });
    overview.value = data || {};
  } finally {
    overviewLoading.value = false;
  }
}

onMounted(() => fetchOverview());

function formatNumber(val: number | null | undefined) {
  if (val == null) return '-';
  return val.toLocaleString();
}

function formatGrowth(val: number | null | undefined) {
  if (val == null) return '-';
  return val.toFixed(2) + '%';
}

function growthClass(val: number | null | undefined) {
  if (val == null) return '';
  return val > 0 ? 'text-red-500' : val < 0 ? 'text-green-500' : '';
}
</script>

<template>
  <div class="p-5">
    <SalesFilterBar v-model:energy-type="energyType" v-model:data-type="dataType" />

    <div class="mb-5 grid grid-cols-1 gap-4 md:grid-cols-4">
      <Card :loading="overviewLoading" :bordered="true">
        <div class="text-center">
          <div class="mb-1 text-sm text-gray-500">{{ $t('sales.market.overview.totalSales') }}</div>
          <div class="text-2xl font-bold">{{ formatNumber(overview.sales) }}</div>
          <div :class="growthClass(overview.mom_growth)" class="text-xs">
            {{ $t('sales.market.overview.momGrowth') }}: {{ formatGrowth(overview.mom_growth) }}
          </div>
        </div>
      </Card>
      <Card :loading="overviewLoading" :bordered="true">
        <div class="text-center">
          <div class="mb-1 text-sm text-gray-500">{{ $t('sales.market.overview.nevSales') }}</div>
          <div class="text-2xl font-bold">{{ formatNumber(overview.nev_sales) }}</div>
        </div>
      </Card>
      <Card :loading="overviewLoading" :bordered="true">
        <div class="text-center">
          <div class="mb-1 text-sm text-gray-500">{{ $t('sales.market.overview.nevPenetration') }}</div>
          <div class="text-2xl font-bold">{{ formatGrowth(overview.nev_penetration_rate) }}</div>
        </div>
      </Card>
      <Card :loading="overviewLoading" :bordered="true">
        <div class="text-center">
          <div class="mb-1 text-sm text-gray-500">{{ $t('sales.market.overview.yoyGrowth') }}</div>
          <div :class="growthClass(overview.yoy_growth)" class="text-2xl font-bold">{{ formatGrowth(overview.yoy_growth) }}</div>
        </div>
      </Card>
    </div>

    <Tabs v-model="activeTab">
      <TabPanel :label="$t('sales.market.monthly.title')" value="monthly">
        <Card :title="$t('sales.market.monthly.chartTitle')" class="mb-4">
          <MonthlySalesChart :energy-type="energyType" :data-type="dataType" />
        </Card>
        <Card :title="$t('sales.market.monthly.title')">
          <MonthlySalesTable :year="currentYear" :energy-type="energyType" :data-type="dataType" />
        </Card>
      </TabPanel>
      <TabPanel :label="$t('sales.market.yearly.title')" value="yearly">
        <Card :title="$t('sales.market.yearly.chartTitle')" class="mb-4">
          <YearlySalesChart :energy-type="energyType" :data-type="dataType" />
        </Card>
        <Card :title="$t('sales.market.yearly.title')">
          <YearlySalesTable :energy-type="energyType" :data-type="dataType" />
        </Card>
      </TabPanel>
    </Tabs>
  </div>
</template>
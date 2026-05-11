<script setup lang="ts">
import { ref } from 'vue';

import { TabPanel, Tabs } from 'tdesign-vue-next';

import { $t } from '#/locales';

import MonthlySalesChart from './components/MonthlySalesChart.vue';
import MonthlySalesTable from './components/MonthlySalesTable.vue';
import SalesFilterBar from './components/SalesFilterBar.vue';
import YearlySalesChart from './components/YearlySalesChart.vue';
import YearlySalesTable from './components/YearlySalesTable.vue';

const energyType = ref('all');
const dataType = ref<'production' | 'retail' | 'wholesale'>('retail');
const activeTab = ref('monthly');
</script>

<template>
  <div class="p-5">
    <SalesFilterBar v-model:energy-type="energyType" v-model:data-type="dataType" />

    <Tabs v-model="activeTab">
      <TabPanel :label="$t('sales.market.monthly.title')" value="monthly">
        <Card :title="$t('sales.market.monthly.chartTitle')" class="mb-4">
          <MonthlySalesChart :energy-type="energyType" :data-type="dataType" />
        </Card>
        <Card :title="$t('sales.market.monthly.title')">
          <MonthlySalesTable :year="new Date().getFullYear()" :energy-type="energyType" :data-type="dataType" />
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

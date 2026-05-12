<script lang="ts" setup>
import { ref } from 'vue';

import { Card, TabPanel, Tabs } from 'tdesign-vue-next';

import { $t } from '#/locales';

import NevBreakdownChart from './components/NevBreakdownChart.vue';
import NevPenetrationChart from './components/NevPenetrationChart.vue';
import NevPenetrationTable from './components/NevPenetrationTable.vue';
import OriginShareChart from './components/OriginShareChart.vue';
import OriginShareTable from './components/OriginShareTable.vue';

const activeTab = ref('nev');
</script>

<template>
  <div class="p-5">
    <Tabs v-model="activeTab">
      <TabPanel :label="$t('sales.analysis.nevTab')" value="nev">
        <Card :title="$t('sales.analysis.nev.penetrationChartTitle')" class="mb-4">
          <NevPenetrationChart />
        </Card>
        <Card :title="$t('sales.analysis.nev.breakdownChartTitle')" class="mb-4">
          <NevBreakdownChart />
        </Card>
        <Card :title="$t('sales.analysis.nev.penetrationTitle')" class="mb-4">
          <NevPenetrationTable />
        </Card>
      </TabPanel>
      <TabPanel :label="$t('sales.analysis.originTab')" value="origin">
        <Card :title="$t('sales.analysis.origin.chartTitle')" class="mb-4">
          <OriginShareChart />
        </Card>
        <Card :title="$t('sales.analysis.origin.chartTitle')">
          <OriginShareTable />
        </Card>
      </TabPanel>
    </Tabs>
  </div>
</template>

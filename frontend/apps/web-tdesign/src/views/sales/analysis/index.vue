<script lang="ts" setup>
import { onMounted, ref } from 'vue';

import { Card, Loading, TabPanel, Tabs } from 'tdesign-vue-next';

import { $t } from '#/locales';

import NevBreakdownChart from './components/NevBreakdownChart.vue';
import NevPenetrationChart from './components/NevPenetrationChart.vue';
import NevPenetrationTable from './components/NevPenetrationTable.vue';
import OriginShareChart from './components/OriginShareChart.vue';
import OriginShareTable from './components/OriginShareTable.vue';
import { useAnalysisData } from './useAnalysisData';

const activeTab = ref('nev');

const { loading, fetchAll, nevShareTrend, nevBreakdown, originShareTrend } =
  useAnalysisData();

onMounted(() => fetchAll());
</script>

<template>
  <div class="p-5">
    <Loading :loading="loading" size="medium" text="数据加载中..." style="min-height: 200px">
      <Tabs v-model="activeTab">
        <TabPanel
          :label="$t('sales.analysis.nevTab')"
          :destroy-on-hide="false"
          value="nev"
        >
          <Card :title="$t('sales.analysis.nev.penetrationChartTitle')" class="mb-4">
            <NevPenetrationChart :data="nevShareTrend" />
          </Card>
          <Card :title="$t('sales.analysis.nev.breakdownChartTitle')" class="mb-4">
            <NevBreakdownChart :data="nevBreakdown" />
          </Card>
          <Card :title="$t('sales.analysis.nev.penetrationTitle')" class="mb-4">
            <NevPenetrationTable
              :breakdown-trend="nevBreakdown"
              :share-trend="nevShareTrend"
            />
          </Card>
        </TabPanel>
        <TabPanel
          :label="$t('sales.analysis.originTab')"
          :destroy-on-hide="false"
          value="origin"
        >
          <Card :title="$t('sales.analysis.origin.chartTitle')" class="mb-4">
            <OriginShareChart :data="originShareTrend" />
          </Card>
          <Card :title="$t('sales.analysis.origin.chartTitle')">
            <OriginShareTable :data="originShareTrend" />
          </Card>
        </TabPanel>
      </Tabs>
    </Loading>
  </div>
</template>

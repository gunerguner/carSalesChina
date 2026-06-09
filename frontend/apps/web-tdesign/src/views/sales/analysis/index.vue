<script setup lang="ts">
import { onMounted, ref } from 'vue';

import { Card, TabPanel, Tabs } from 'tdesign-vue-next';

import DataLoadState from '#/components/DataLoadState.vue';
import { $t } from '#/locales';
import { getChartPaletteColor } from '#/utils/chart';

import NevPenetrationTable from './components/NevPenetrationTable.vue';
import NevTrendLineChart from './components/NevTrendLineChart.vue';
import OriginShareChart from './components/OriginShareChart.vue';
import OriginShareTable from './components/OriginShareTable.vue';
import { useAnalysisData } from './useAnalysisData';

const activeTab = ref('nev');

const {
  error,
  loading,
  fetchAll,
  nevShareTrend,
  nevBreakdown,
  originShareTrend,
} = useAnalysisData();

onMounted(() => fetchAll());
</script>

<template>
  <div class="p-5">
    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <Tabs v-model="activeTab">
        <TabPanel
          :label="$t('sales.analysis.nevTab')"
          destroy-on-hide
          value="nev"
        >
          <div class="mb-4 flex gap-4">
            <Card
              :title="$t('sales.analysis.nev.penetrationChartTitle')"
              class="flex-1"
            >
              <NevTrendLineChart
                :data="nevShareTrend"
                :label="$t('sales.analysis.nev.penetrationRateLabel')"
                :color="getChartPaletteColor(0)"
                value-key="nev_penetration_rate"
              />
            </Card>
            <Card
              :title="$t('sales.analysis.nev.breakdownChartTitle')"
              class="flex-1"
            >
              <NevTrendLineChart
                :data="nevBreakdown"
                :label="$t('sales.analysis.nev.bevInNevTrendLabel')"
                :color="getChartPaletteColor(1)"
                value-key="bev_ratio"
              />
            </Card>
          </div>
          <Card :title="$t('sales.analysis.nev.penetrationTitle')" class="mb-4">
            <NevPenetrationTable
              :breakdown-trend="nevBreakdown"
              :share-trend="nevShareTrend"
            />
          </Card>
        </TabPanel>
        <TabPanel
          :label="$t('sales.analysis.originTab')"
          destroy-on-hide
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
    </DataLoadState>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

import { Card, TabPanel, Tabs } from 'tdesign-vue-next';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import { $t } from '#/locales';
import { getChartPaletteColor } from '#/utils/chart';

import NevPenetrationTable from './components/NevPenetrationTable.vue';
import { buildNevTrendChartOption } from './components/nevTrendChart';
import { buildOriginShareChartOption } from './components/originShareChart';
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

const nevPenetrationChartOption = computed(() =>
  buildNevTrendChartOption(
    {
      color: getChartPaletteColor(0),
      data: nevShareTrend.value,
      label: $t('sales.analysis.nev.penetrationRateLabel'),
      valueKey: 'nev_penetration_rate',
    },
    $t,
  ),
);

const bevBreakdownChartOption = computed(() =>
  buildNevTrendChartOption(
    {
      color: getChartPaletteColor(1),
      data: nevBreakdown.value,
      label: $t('sales.analysis.nev.bevInNevTrendLabel'),
      valueKey: 'bev_ratio',
    },
    $t,
  ),
);

const originShareChartOption = computed(() =>
  buildOriginShareChartOption(originShareTrend.value, $t),
);
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
              <ChartCard
                height-class="h-72"
                :option="nevPenetrationChartOption"
              />
            </Card>
            <Card
              :title="$t('sales.analysis.nev.breakdownChartTitle')"
              class="flex-1"
            >
              <ChartCard
                height-class="h-72"
                :option="bevBreakdownChartOption"
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
            <ChartCard :option="originShareChartOption" />
          </Card>
          <Card :title="$t('sales.analysis.origin.chartTitle')">
            <OriginShareTable :data="originShareTrend" />
          </Card>
        </TabPanel>
      </Tabs>
    </DataLoadState>
  </div>
</template>

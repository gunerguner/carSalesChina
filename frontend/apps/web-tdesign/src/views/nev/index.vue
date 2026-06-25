<script setup lang="ts">
import { computed, onMounted } from 'vue';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import SectionCard from '#/components/SectionCard.vue';
import { $t } from '#/locales';
import { getChartPaletteColor } from '#/utils/style';

import NevPenetrationTable from './components/NevPenetrationTable.vue';
import { buildNevTrendChartOption } from './components/nevTrendChart';
import { useNevAnalysisData } from './useNevAnalysisData';

const { error, loading, fetchAll, nevShareTrend, nevBreakdown } =
  useNevAnalysisData();

onMounted(() => fetchAll());

const nevPenetrationChartOption = computed(() =>
  buildNevTrendChartOption(
    {
      color: getChartPaletteColor(0),
      data: nevShareTrend.value,
      label: $t('pages.analysis.nev.penetrationRateLabel'),
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
      label: $t('pages.analysis.nev.bevInNevTrendLabel'),
      valueKey: 'bev_ratio',
    },
    $t,
  ),
);
</script>

<template>
  <div class="page-content">
    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <div class="chart-grid">
        <SectionCard :title="$t('pages.analysis.nev.penetrationChartTitle')">
          <ChartCard height-class="h-72" :option="nevPenetrationChartOption" />
        </SectionCard>
        <SectionCard :title="$t('pages.analysis.nev.breakdownChartTitle')">
          <ChartCard height-class="h-72" :option="bevBreakdownChartOption" />
        </SectionCard>
      </div>
      <SectionCard :title="$t('pages.analysis.nev.penetrationTitle')">
        <NevPenetrationTable
          :breakdown-trend="nevBreakdown"
          :share-trend="nevShareTrend"
        />
      </SectionCard>
    </DataLoadState>
  </div>
</template>

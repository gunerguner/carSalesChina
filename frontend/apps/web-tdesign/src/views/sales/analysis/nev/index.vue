<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { Card } from 'tdesign-vue-next';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import { $t } from '#/locales';
import { getChartPaletteColor } from '#/utils/chart';

import NevPenetrationTable from '../components/NevPenetrationTable.vue';
import { buildNevTrendChartOption } from '../components/nevTrendChart';
import { useNevAnalysisData } from '../useNevAnalysisData';

const { error, loading, fetchAll, nevShareTrend, nevBreakdown } =
  useNevAnalysisData();

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
</script>

<template>
  <div class="sales-page-content">
    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <div class="sales-chart-grid">
        <Card
          :title="$t('sales.analysis.nev.penetrationChartTitle')"
          class="sales-section-card"
        >
          <ChartCard height-class="h-72" :option="nevPenetrationChartOption" />
        </Card>
        <Card
          :title="$t('sales.analysis.nev.breakdownChartTitle')"
          class="sales-section-card"
        >
          <ChartCard height-class="h-72" :option="bevBreakdownChartOption" />
        </Card>
      </div>
      <Card
        :title="$t('sales.analysis.nev.penetrationTitle')"
        class="sales-section-card"
      >
        <NevPenetrationTable
          :breakdown-trend="nevBreakdown"
          :share-trend="nevShareTrend"
        />
      </Card>
    </DataLoadState>
  </div>
</template>

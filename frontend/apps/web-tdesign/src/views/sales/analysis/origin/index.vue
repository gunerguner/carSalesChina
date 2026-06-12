<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { Card } from 'tdesign-vue-next';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import { $t } from '#/locales';

import { buildOriginShareChartOption } from '../components/originShareChart';
import OriginShareTable from '../components/OriginShareTable.vue';
import { useOriginAnalysisData } from '../useOriginAnalysisData';

const { error, loading, fetchAll, originShareTrend } = useOriginAnalysisData();

onMounted(() => fetchAll());

const originShareChartOption = computed(() =>
  buildOriginShareChartOption(originShareTrend.value, $t),
);
</script>

<template>
  <div class="sales-page-content">
    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <Card
        :title="$t('sales.analysis.origin.chartTitle')"
        class="sales-section-card"
      >
        <ChartCard :option="originShareChartOption" />
      </Card>
      <Card
        :title="$t('sales.analysis.origin.tableTitle')"
        class="sales-section-card"
      >
        <OriginShareTable :data="originShareTrend" />
      </Card>
    </DataLoadState>
  </div>
</template>

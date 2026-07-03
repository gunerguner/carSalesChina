<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { preferences } from '@vben/preferences';

import ChartCard from '#/components/ChartCard.vue';
import DataLoadState from '#/components/DataLoadState.vue';
import SectionCard from '#/components/SectionCard.vue';
import { $t } from '#/locales';

import { buildOriginShareChartOption } from './components/originShareChart';
import OriginShareTable from './components/OriginShareTable.vue';
import { useOriginAnalysisData } from './useOriginAnalysisData';

const { error, loading, fetchAll, originShareTrend } = useOriginAnalysisData();

onMounted(() => fetchAll());

const originShareChartOption = computed(() => {
  // 显式读取主题 mode 以建立响应式依赖；切换 light/dark 时 option 重建
  void preferences.theme.mode;
  return buildOriginShareChartOption(originShareTrend.value, $t);
});
</script>

<template>
  <div class="page-content">
    <DataLoadState :error="error" :loading="loading" @retry="fetchAll(true)">
      <SectionCard
        :title="$t('pages.analysis.origin.chartTitle')"
        :tooltip="$t('pages.analysis.origin.tooltip.originShare')"
      >
        <ChartCard :option="originShareChartOption" />
      </SectionCard>
      <SectionCard :title="$t('pages.analysis.origin.tableTitle')">
        <OriginShareTable :data="originShareTrend" />
      </SectionCard>
    </DataLoadState>
  </div>
</template>

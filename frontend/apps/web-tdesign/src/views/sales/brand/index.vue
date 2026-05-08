<script lang="ts" setup>
import { Card } from 'tdesign-vue-next';
import { ref } from 'vue';

import { $t } from '#/locales';

import BrandCompareChart from './components/BrandCompareChart.vue';
import BrandCompareSelect from './components/BrandCompareSelect.vue';
import BrandCompareTable from './components/BrandCompareTable.vue';
import BrandRankingChart from './components/BrandRankingChart.vue';
import BrandRankingTable from './components/BrandRankingTable.vue';

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

const filterState = ref({
  granularity: 'monthly' as 'monthly' | 'yearly',
  dataType: 'retail' as 'retail' | 'wholesale' | 'production',
  brands: [] as string[],
});

function onFilterChange(payload: { granularity: 'monthly' | 'yearly'; dataType: 'retail' | 'wholesale' | 'production'; brands: string[] }) {
  filterState.value = payload;
}
</script>

<template>
  <div class="p-5">
    <BrandCompareSelect @change="onFilterChange" />

    <Card :title="$t('sales.brand.ranking.chartTitle')" class="mb-4">
      <BrandRankingChart
        :year="currentYear"
        :month="currentMonth"
        :granularity="filterState.granularity"
        :data-type="filterState.dataType"
      />
    </Card>

    <Card :title="$t('sales.brand.ranking.title')" class="mb-4">
      <BrandRankingTable
        :year="currentYear"
        :month="currentMonth"
        :granularity="filterState.granularity"
        :data-type="filterState.dataType"
      />
    </Card>

    <Card :title="$t('sales.brand.compare.title')" class="mb-4">
      <BrandCompareChart
        :brands="filterState.brands"
        :granularity="filterState.granularity"
        :data-type="filterState.dataType"
      />
    </Card>

    <Card :title="$t('sales.brand.compare.title')">
      <BrandCompareTable
        :brands="filterState.brands"
        :granularity="filterState.granularity"
        :data-type="filterState.dataType"
      />
    </Card>
  </div>
</template>

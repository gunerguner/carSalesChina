<script setup lang="ts">
import type { MarketSalesTableInput } from './marketSalesTable';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

import {
  buildMarketSalesTableColumns,
  buildMarketSalesTableRows,
} from './marketSalesTable';

const props = defineProps<
  MarketSalesTableInput & { dataType: 'production' | 'retail' }
>();

const columns = computed(() =>
  buildMarketSalesTableColumns(props.kind, props.dataType, $t),
);
const tableData = computed(() =>
  buildMarketSalesTableRows(
    props as MarketSalesTableInput,
    preferences.app.locale,
  ),
);
</script>

<template>
  <div class="px-4 py-3">
    <Table
      :columns="columns"
      :data="tableData"
      row-key="key"
      size="small"
      bordered
    />
  </div>
</template>

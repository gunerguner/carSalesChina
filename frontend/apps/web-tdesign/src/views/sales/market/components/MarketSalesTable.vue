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
  <Table
    :columns="columns"
    :data="tableData"
    bordered
    row-key="key"
    size="small"
    stripe
  />
</template>

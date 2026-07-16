<script setup lang="ts">
import type { MarketTableInput } from './marketSalesTable';

import type { DataType } from '#/utils/types';

import { computed } from 'vue';

import { preferences } from '@vben/preferences';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { DEFAULT_TABLE_PROPS } from '#/utils/style';

import {
  buildMarketTableColumns,
  buildMarketTableRows,
} from './marketSalesTable';

const props = defineProps<MarketTableInput & { dataType: DataType }>();

const columns = computed(() =>
  buildMarketTableColumns(props.kind, props.dataType, $t),
);
const tableData = computed(() =>
  buildMarketTableRows(props as MarketTableInput, preferences.app.locale),
);
</script>

<template>
  <Table v-bind="DEFAULT_TABLE_PROPS" :columns="columns" :data="tableData" />
</template>

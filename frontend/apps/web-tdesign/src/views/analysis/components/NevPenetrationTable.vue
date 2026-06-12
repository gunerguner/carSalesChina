<script setup lang="ts">
import type {
  NevBreakdownRecord,
  NevShareTrendRecord,
} from '#/api/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { DEFAULT_TABLE_PROPS } from '#/utils/style';

import {
  buildNevPenetrationTableColumns,
  buildNevPenetrationTableRows,
} from './nevPenetrationTable';

const props = defineProps<{
  breakdownTrend: NevBreakdownRecord[];
  shareTrend: NevShareTrendRecord[];
}>();

const columns = buildNevPenetrationTableColumns($t);
const tableData = computed(() =>
  buildNevPenetrationTableRows(props.shareTrend, props.breakdownTrend),
);
</script>

<template>
  <Table v-bind="DEFAULT_TABLE_PROPS" :columns="columns" :data="tableData" />
</template>

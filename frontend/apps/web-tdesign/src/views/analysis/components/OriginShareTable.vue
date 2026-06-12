<script setup lang="ts">
import type { OriginShareTrendRecord } from '#/api/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { DEFAULT_TABLE_PROPS } from '#/utils/style';

import {
  buildOriginShareTableColumns,
  buildOriginShareTableRows,
} from './originShareTable';

const props = defineProps<{
  data: OriginShareTrendRecord[];
}>();

const columns = buildOriginShareTableColumns($t);
const tableData = computed(() => buildOriginShareTableRows(props.data));
</script>

<template>
  <Table v-bind="DEFAULT_TABLE_PROPS" :columns="columns" :data="tableData" />
</template>

<script setup lang="ts">
import type { OriginShareTrendRecord } from '#/api/analysis';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';

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
  <Table
    :columns="columns"
    :data="tableData"
    bordered
    row-key="key"
    size="small"
    stripe
  />
</template>

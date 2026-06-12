<script setup lang="ts">
import type { PrimaryTableCol } from 'tdesign-vue-next';

import type { BrandSeriesRecord } from '../types';

import type { DataType } from '#/utils/types';

import { computed } from 'vue';

import { Table } from 'tdesign-vue-next';

import { $t } from '#/locales';
import { isNil } from '#/utils/format';
import { salesYoyTableCell } from '#/utils/render';
import { DEFAULT_TABLE_PROPS } from '#/utils/style';

const props = defineProps<{
  data: BrandSeriesRecord[];
  dataType: DataType;
  /** 最多展示多少条时间行；null 表示与 timeLabels 一致（如年度全部年份） */
  timeLabelMaxCount?: null | number;
  timeLabels: string[];
}>();

/** 表格：按时间倒序；条数由 timeLabelMaxCount 控制，与图表当前周期对齐 */
const tableTimeLabels = computed(() => {
  const sorted = [...props.timeLabels].toSorted((a, b) => b.localeCompare(a));
  const max = props.timeLabelMaxCount;
  if (max === null) {
    return sorted;
  }
  const limit = max ?? 12;
  return sorted.slice(0, limit);
});

const columns = computed<PrimaryTableCol[]>(() => {
  const base: PrimaryTableCol[] = [
    { colKey: 'time', title: $t('pages.brand.trend.time'), width: 120 },
  ];
  const salesWithYoySuffix =
    props.dataType === 'production'
      ? $t('pages.brand.trend.salesWithYoyProduction')
      : $t('pages.brand.trend.salesWithYoyRetail');
  for (const brand of props.data) {
    const salesKey = `brand_${brand.brand_name}_sales`;
    const yoyKey = `brand_${brand.brand_name}_yoy`;
    base.push({
      cell: salesYoyTableCell(salesKey, yoyKey),
      colKey: salesKey,
      title: `${brand.brand_name}${salesWithYoySuffix}`,
      width: 200,
    });
  }
  return base;
});

const tableData = computed(() => {
  const brandMap = new Map<
    string,
    Map<string, { sales: number; yoyGrowth: null | number }>
  >();
  for (const brand of props.data) {
    const pointMap = new Map<
      string,
      { sales: number; yoyGrowth: null | number }
    >();
    for (const point of brand.points ?? []) {
      pointMap.set(point.time, {
        sales: point.sales ?? 0,
        yoyGrowth: point.yoyGrowth ?? null,
      });
    }
    brandMap.set(brand.brand_name, pointMap);
  }

  return tableTimeLabels.value.map((time) => {
    const row: Record<string, null | number | string> = { key: time, time };
    for (const brand of props.data) {
      const point = brandMap.get(brand.brand_name)?.get(time);
      if (!isNil(point)) {
        row[`brand_${brand.brand_name}_sales`] = point.sales;
        row[`brand_${brand.brand_name}_yoy`] = point.yoyGrowth;
      }
    }
    return row;
  });
});
</script>

<template>
  <Table v-bind="DEFAULT_TABLE_PROPS" :columns="columns" :data="tableData" />
</template>

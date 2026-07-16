<script setup lang="ts">
import type { BrandQuickFilter } from '../brand-defaults';
import type { BrandTrendGranularity } from '../useBrandData';

import type { DataType } from '#/utils/types';

import { ref, watch } from 'vue';

import { Button, RadioButton, RadioGroup, Select } from 'tdesign-vue-next';

import MetricTooltip from '#/components/MetricTooltip.vue';
import { $t } from '#/locales';
import { isNil } from '#/utils/format';

import {
  BRAND_QUICK_FILTERS,
  DEFAULT_SELECTED_BRAND_NAMES,
  MAX_BRAND_COMPARE,
  resolveBrandNames,
} from '../brand-defaults';
import { useBrandMetaAll } from '../useBrandMetaAll';

// 单一真相：直接绑到 useBrandData 暴露的 ref，与 market 页风格一致
const selectedBrands = defineModel<string[]>('selectedBrands', {
  required: true,
});
const dataType = defineModel<DataType>('dataType', { required: true });
const granularity = defineModel<BrandTrendGranularity>('granularity', {
  required: true,
});

const brandOptionsLoaded = ref(false);
const activeQuickFilterId = ref<null | string>(null);

const { brandOptions, brandMetaLoading, ensureLoaded } = useBrandMetaAll();

function getAllowedBrandSet() {
  return new Set(brandOptions.value.map((o) => o.value));
}

function sameBrandSet(a: string[], b: string[]): boolean {
  if (a.length !== b.length) {
    return false;
  }
  const setA = new Set(a);
  return b.every((name) => setA.has(name));
}

function syncActiveQuickFilter() {
  if (!brandOptionsLoaded.value) {
    return;
  }
  const allowed = getAllowedBrandSet();
  const current = selectedBrands.value;

  if (current.length === 0) {
    const clearFilter = BRAND_QUICK_FILTERS.find(
      (item) => item.action === 'clear',
    );
    activeQuickFilterId.value = clearFilter?.id ?? null;
    return;
  }

  const matched = BRAND_QUICK_FILTERS.find((filter) => {
    if (filter.action === 'clear' || !filter.brands) {
      return false;
    }
    const resolved = resolveBrandNames(filter.brands, allowed);
    return sameBrandSet(current, resolved);
  });
  activeQuickFilterId.value = matched?.id ?? null;
}

async function initializeFromMeta() {
  brandOptionsLoaded.value = false;
  try {
    await ensureLoaded();
    const allowed = getAllowedBrandSet();
    const next = resolveBrandNames(DEFAULT_SELECTED_BRAND_NAMES, allowed);
    const unchanged =
      next.length === selectedBrands.value.length &&
      next.every((name, i) => name === selectedBrands.value[i]);
    if (!unchanged) {
      selectedBrands.value = next;
    }
  } catch (error) {
    selectedBrands.value = [];
    console.error('[BrandSelectBar] ensureLoaded failed', error);
  } finally {
    brandOptionsLoaded.value = true;
    syncActiveQuickFilter();
  }
}

function handleBrandsChange(val: unknown) {
  if (isNil(val)) {
    selectedBrands.value = [];
    return;
  }
  const raw = Array.isArray(val) ? val : [val];
  const arr = raw.map(String);
  selectedBrands.value =
    arr.length > MAX_BRAND_COMPARE ? arr.slice(-MAX_BRAND_COMPARE) : arr;
}

function applyQuickFilter(filter: BrandQuickFilter) {
  if (!brandOptionsLoaded.value) {
    return;
  }
  if (filter.action === 'clear') {
    selectedBrands.value = [];
    activeQuickFilterId.value = filter.id;
    return;
  }
  if (!filter.brands) {
    return;
  }
  const allowed = getAllowedBrandSet();
  selectedBrands.value = resolveBrandNames(filter.brands, allowed);
  activeQuickFilterId.value = filter.id;
}

// quick filter 仅依赖 selectedBrands；granularity/dataType 变化无需重算
watch(selectedBrands, () => {
  if (!brandOptionsLoaded.value) return;
  syncActiveQuickFilter();
});

initializeFromMeta();
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap items-center gap-4">
      <div class="flex items-center gap-2">
        <span class="filter-label">{{
          $t('pages.brand.trend.selectBrands')
        }}</span>
        <Select
          :value="selectedBrands"
          :options="brandOptions"
          :loading="brandMetaLoading"
          :placeholder="$t('pages.brand.trend.selectPlaceholder')"
          multiple
          :max="MAX_BRAND_COMPARE"
          filterable
          style="width: 420px"
          @change="handleBrandsChange"
        />
      </div>
      <div class="flex items-center gap-2">
        <span class="filter-label">{{
          $t('pages.brand.trend.granularity')
        }}</span>
        <RadioGroup v-model="granularity" variant="default-filled">
          <RadioButton value="recentYear">
            {{ $t('pages.brand.trend.recentYear') }}
          </RadioButton>
          <RadioButton value="recentTwoYears">
            {{ $t('pages.brand.trend.recentTwoYears') }}
          </RadioButton>
          <RadioButton value="yearly">
            {{ $t('pages.brand.trend.yearly') }}
          </RadioButton>
        </RadioGroup>
      </div>
      <div class="flex items-center gap-2">
        <span class="filter-label">{{ $t('pages.brand.trend.dataType') }}</span>
        <RadioGroup v-model="dataType" variant="default-filled">
          <RadioButton value="retail">
            {{ $t('pages.brand.trend.retail') }}
          </RadioButton>
          <RadioButton value="production">
            {{ $t('pages.brand.trend.production') }}
          </RadioButton>
        </RadioGroup>
        <MetricTooltip :content="$t('pages.brand.tooltip.dataType')" />
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      <Button
        v-for="filter in BRAND_QUICK_FILTERS"
        :key="filter.id"
        size="small"
        variant="outline"
        :class="{
          'brand-quick-filter--active': activeQuickFilterId === filter.id,
        }"
        :disabled="!brandOptionsLoaded || brandMetaLoading"
        @click="applyQuickFilter(filter)"
      >
        {{ $t(filter.labelKey) }}
      </Button>
    </div>
  </div>
</template>

<style scoped>
.brand-quick-filter--active {
  color: hsl(var(--primary-foreground));
  background-color: hsl(var(--primary));
  border-color: hsl(var(--primary));
}

.brand-quick-filter--active:hover,
.brand-quick-filter--active:focus-visible {
  color: hsl(var(--primary-foreground));
  background-color: hsl(var(--primary) / 85%);
  border-color: hsl(var(--primary) / 85%);
}
</style>

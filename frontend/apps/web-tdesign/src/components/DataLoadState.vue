<script setup lang="ts">
import { Alert, Button } from 'tdesign-vue-next';

import { $t } from '#/locales';

const props = withDefaults(
  defineProps<{
    error?: null | string;
    loading?: boolean;
    minHeight?: string;
  }>(),
  {
    error: null,
    loading: false,
    minHeight: '200px',
  },
);

const emit = defineEmits<{
  retry: [];
}>();
</script>

<template>
  <div v-if="error" class="sales-load-error">
    <Alert :message="$t(error)" theme="error" />
    <Button theme="primary" variant="outline" @click="emit('retry')">
      {{ $t('sales.common.retry') }}
    </Button>
  </div>
  <div
    v-else-if="loading"
    class="sales-load-skeleton"
    :style="{ minHeight: props.minHeight }"
  >
    <div class="sales-load-skeleton__chart"></div>
    <div class="sales-load-skeleton__table"></div>
  </div>
  <slot v-else></slot>
</template>

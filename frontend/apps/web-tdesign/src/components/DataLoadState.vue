<script setup lang="ts">
import { Alert, Button } from 'tdesign-vue-next';

import { $t } from '#/locales';

const {
  error = null,
  loading = false,
  minHeight = '200px',
} = defineProps<{
  error?: null | string;
  loading?: boolean;
  minHeight?: string;
}>();

const emit = defineEmits<{
  retry: [];
}>();
</script>

<template>
  <div v-if="error" class="load-error">
    <Alert :message="$t(error)" theme="error" />
    <Button theme="primary" variant="outline" @click="emit('retry')">
      {{ $t('pages.common.retry') }}
    </Button>
  </div>
  <div v-else-if="loading" class="load-skeleton" :style="{ minHeight }">
    <div class="load-skeleton__chart"></div>
    <div class="load-skeleton__table"></div>
  </div>
  <slot v-else></slot>
</template>

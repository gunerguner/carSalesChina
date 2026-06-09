<script setup lang="ts">
import { Alert, Button, Loading } from 'tdesign-vue-next';

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
  <div v-if="error" class="flex flex-col items-center gap-4 py-8">
    <Alert :message="$t(error)" theme="error" />
    <Button theme="primary" variant="outline" @click="emit('retry')">
      {{ $t('sales.common.retry') }}
    </Button>
  </div>
  <Loading
    v-else
    :loading="loading"
    size="medium"
    :text="$t('sales.common.loading')"
    :style="{ minHeight: props.minHeight }"
  >
    <slot></slot>
  </Loading>
</template>

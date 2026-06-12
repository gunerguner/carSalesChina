<script setup lang="ts">
import { VbenIconButton } from '@vben/common-ui';
import { RotateCw } from '@vben/icons';

import { useAdminDataRefresh } from '#/composables/useAdminDataRefresh';

const { refreshAdminData, refreshing } = useAdminDataRefresh();
</script>

<template>
  <VbenIconButton
    class="my-0 mr-1 rounded-md"
    :disabled="refreshing"
    @click="refreshAdminData"
  >
    <RotateCw class="size-4" :class="{ 'animate-spin': refreshing }" />
  </VbenIconButton>
</template>

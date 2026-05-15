<script lang="ts" setup>
import { ref } from 'vue';

import { VbenIconButton } from '@vben/common-ui';
import { RotateCw } from '@vben/icons';
import { BasicLayout } from '@vben/layouts';

import { notification } from '#/adapter/tdesign';
import { refreshBrandMetaApi, refreshOriginApi, refreshSalesApi } from '#/api/admin';
import { $t } from '#/locales';

const refreshing = ref(false);

async function handleRefreshData() {
  if (refreshing.value) return;
  refreshing.value = true;

  try {
    await refreshBrandMetaApi();
    await refreshSalesApi();
    await refreshOriginApi();

    notification.success({
      title: $t('sales.admin.refreshSuccess'),
      duration: 3000,
    });
  } catch {
    notification.error({
      title: $t('sales.admin.refreshFailed'),
      duration: 3000,
    });
  } finally {
    refreshing.value = false;
  }
}
</script>

<template>
  <BasicLayout>
    <template #header-right-40>
      <VbenIconButton class="my-0 mr-1 rounded-md" :disabled="refreshing" @click="handleRefreshData">
        <RotateCw class="size-4" :class="{ 'animate-spin': refreshing }" />
      </VbenIconButton>
    </template>
  </BasicLayout>
</template>

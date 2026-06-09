<script setup lang="ts">
import type { RefreshOriginPayload, RefreshSalesPayload } from '#/api/admin';

import { ref } from 'vue';

import { VbenIconButton } from '@vben/common-ui';
import { RotateCw } from '@vben/icons';
import { BasicLayout } from '@vben/layouts';

import { notification } from '#/adapter/tdesign';
import {
  refreshBrandMetaApi,
  refreshOriginApi,
  refreshSalesApi,
} from '#/api/admin';
import { $t } from '#/locales';

const refreshing = ref(false);

function collectSourceNotes(
  sales: RefreshSalesPayload,
  origin: RefreshOriginPayload,
): string[] {
  const lines: string[] = [];
  if (sales.source_errors.overall) {
    lines.push(
      `${$t('sales.admin.sourceOverall')}: ${sales.source_errors.overall}`,
    );
  }
  if (sales.source_errors.brand) {
    lines.push(
      `${$t('sales.admin.sourceBrand')}: ${sales.source_errors.brand}`,
    );
  }
  if (origin.source_errors.origin) {
    lines.push(
      `${$t('sales.admin.sourceOrigin')}: ${origin.source_errors.origin}`,
    );
  }
  return lines;
}

async function handleRefreshData() {
  if (refreshing.value) return;
  refreshing.value = true;

  try {
    await refreshBrandMetaApi();
    const sales = await refreshSalesApi();
    const origin = await refreshOriginApi();

    const hasFailure = sales.status === 'failed' || origin.status === 'failed';
    const hasPartial = sales.status === 'partial_failure';

    const detailLines = collectSourceNotes(sales, origin);
    const content = detailLines.length > 0 ? detailLines.join('\n') : undefined;

    if (hasFailure) {
      notification.error({
        title: $t('sales.admin.refreshFailed'),
        content,
        duration: 8000,
      });
      return;
    }
    if (hasPartial) {
      notification.warning({
        title: $t('sales.admin.refreshPartial'),
        content,
        duration: 8000,
      });
      return;
    }
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
      <VbenIconButton
        class="my-0 mr-1 rounded-md"
        :disabled="refreshing"
        @click="handleRefreshData"
      >
        <RotateCw class="size-4" :class="{ 'animate-spin': refreshing }" />
      </VbenIconButton>
    </template>
  </BasicLayout>
</template>

import type { RefreshOriginPayload, RefreshSalesPayload } from '#/api/admin';

import { ref } from 'vue';

import { NotifyPlugin as notification } from 'tdesign-vue-next';

import {
  refreshBrandMetaApi,
  refreshOriginApi,
  refreshSalesApi,
} from '#/api/admin';
import { $t } from '#/locales';

function collectSourceNotes(
  sales: RefreshSalesPayload,
  origin: RefreshOriginPayload,
): string[] {
  const lines: string[] = [];
  if (sales.source_errors.overall) {
    lines.push(
      `${$t('pages.admin.sourceOverall')}: ${sales.source_errors.overall}`,
    );
  }
  if (sales.source_errors.brand) {
    lines.push(
      `${$t('pages.admin.sourceBrand')}: ${sales.source_errors.brand}`,
    );
  }
  if (origin.source_errors.origin) {
    lines.push(
      `${$t('pages.admin.sourceOrigin')}: ${origin.source_errors.origin}`,
    );
  }
  return lines;
}

export function useAdminDataRefresh() {
  const refreshing = ref(false);

  async function refreshAdminData() {
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
          title: $t('pages.admin.refreshFailed'),
          content,
          duration: 8000,
        });
        return;
      }
      if (hasPartial) {
        notification.warning({
          title: $t('pages.admin.refreshPartial'),
          content,
          duration: 8000,
        });
        return;
      }
      notification.success({
        title: $t('pages.admin.refreshSuccess'),
        duration: 3000,
      });
    } catch {
      notification.error({
        title: $t('pages.admin.refreshFailed'),
        duration: 3000,
      });
    } finally {
      refreshing.value = false;
    }
  }

  return { refreshAdminData, refreshing };
}

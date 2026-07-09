import { onMounted, onUnmounted } from 'vue';

import { offDataRefresh, onDataRefresh } from '#/utils/data-refresh';

interface PageRefreshOptions {
  initialLoad?: () => void;
}

export function usePageRefresh(
  reload: () => void,
  options?: PageRefreshOptions,
) {
  onMounted(() => {
    onDataRefresh(reload);
    (options?.initialLoad ?? reload)();
  });

  onUnmounted(() => {
    offDataRefresh(reload);
  });
}

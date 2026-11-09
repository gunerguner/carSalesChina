import { onMounted, onUnmounted } from 'vue';

import { offDataRefresh, onDataRefresh } from '#/utils/data-refresh';

interface PageRefreshOptions {
  /**
   * 进入页面时的加载。默认与 `reload` 相同。
   * 月度数据应传不带 force 的拉取，让会话缓存生效；`reload` 只在管理端刷新后强制重拉。
   */
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

import type { Router } from 'vue-router';

import { preferences } from '@vben/preferences';
import { useAccessStore } from '@vben/stores';
import { generateMenus, startProgress, stopProgress } from '@vben/utils';

import { menuRoutes } from '#/router/routes';

/**
 * 通用守卫配置
 * @param router
 */
function setupCommonGuard(router: Router) {
  const loadedPaths = new Set<string>();

  router.beforeEach((to) => {
    to.meta.loaded = loadedPaths.has(to.path);

    if (!to.meta.loaded && preferences.transition.progress) {
      startProgress();
    }
    return true;
  });

  router.afterEach((to) => {
    loadedPaths.add(to.path);

    if (preferences.transition.progress) {
      stopProgress();
    }
  });
}

/**
 * 无登录站点：静态路由已就绪，仅写入侧栏菜单供布局读取。
 * 须在 initStores 之后调用。
 */
function setupMenus(router: Router) {
  const accessStore = useAccessStore();
  accessStore.setAccessMenus(generateMenus(menuRoutes, router));
  accessStore.setIsAccessChecked(true);
}

/**
 * 项目守卫配置
 * @param router
 */
function createRouterGuard(router: Router) {
  setupCommonGuard(router);
}

export { createRouterGuard, setupMenus };

import { createApp, watchEffect } from 'vue';

import { registerAccessDirective } from '@vben/access';
import { registerLoadingDirective } from '@vben/common-ui/es/loading';
import { preferences } from '@vben/preferences';
import { initStores, useAccessStore, useUserStore } from '@vben/stores';
import '@vben/styles';

import { useTitle } from '@vueuse/core';

import { $t, setupI18n } from '#/locales';

import { initComponentAdapter } from './adapter/component';
import { initSetupVbenForm } from './adapter/form';
import App from './app.vue';
import { router } from './router';
import salesRoutes from './router/routes/modules/sales';

import 'tdesign-vue-next/es/style/index.css';

async function bootstrap(namespace: string) {
  await initComponentAdapter();
  await initSetupVbenForm();

  const app = createApp(App);

  registerLoadingDirective(app, {
    loading: 'loading',
    spinning: 'spinning',
  });

  await setupI18n(app);

  await initStores(app, { namespace });

  const accessStore = useAccessStore();
  const userStore = useUserStore();
  accessStore.setAccessToken('mock-token-for-dev');
  accessStore.setAccessCodes(['*']);
  userStore.setUserInfo({
    userId: '1',
    username: 'admin',
    realName: '管理员',
    roles: ['admin'],
    homePath: '/market-sales',
    avatar: '',
  });

  const { cloneDeep, generateMenus, generateRoutesByFrontend } = await import(
    '@vben/utils'
  );

  const clonedRoutes = cloneDeep(salesRoutes);
  const accessibleRoutes = await generateRoutesByFrontend(
    clonedRoutes,
    ['admin'],
    null,
  );

  const root = router.getRoutes().find((item) => item.path === '/');
  const names = root?.children?.map((item) => item.name) ?? [];

  accessibleRoutes.forEach((route: any) => {
    if (root && !route.meta?.noBasicLayout) {
      if (route.children && route.children.length > 0) {
        delete route.component;
      }
      if (names?.includes(route.name)) {
        const index = root.children?.findIndex(
          (item: any) => item.name === route.name,
        );
        if (index !== undefined && index !== -1 && root.children) {
          root.children[index] = route;
        }
      } else {
        root.children?.push(route);
      }
    } else {
      router.addRoute(route);
    }
  });

  if (root) {
    if (root.name) {
      router.removeRoute(root.name);
    }
    router.addRoute(root);
  }

  const accessibleMenus = generateMenus(accessibleRoutes, router);
  accessStore.setAccessMenus(accessibleMenus);
  accessStore.setAccessRoutes(accessibleRoutes);
  accessStore.setIsAccessChecked(true);

  registerAccessDirective(app);

  const { initTippy } = await import('@vben/common-ui/es/tippy');
  initTippy(app);

  app.use(router);

  const { MotionPlugin } = await import('@vben/plugins/motion');
  app.use(MotionPlugin);

  watchEffect(() => {
    if (preferences.app.dynamicTitle) {
      const routeTitle = router.currentRoute.value.meta?.title;
      const pageTitle =
        (routeTitle ? `${$t(routeTitle)} - ` : '') + preferences.app.name;
      useTitle(pageTitle);
    }
  });

  app.mount('#app');
}

export { bootstrap };

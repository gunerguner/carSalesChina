import type { RouteRecordRaw } from 'vue-router';

import { defineComponent, h } from 'vue';

import { Fallback } from '@vben/common-ui';
import { preferences } from '@vben/preferences';

import appRoutes from './modules/app';

const BasicLayout = () => import('#/layouts/basic.vue');

const NotFound = defineComponent({
  name: 'NotFound',
  setup: () => () => h(Fallback, { status: '404' }),
});

/** 全局404页面 */
const fallbackNotFoundRoute: RouteRecordRaw = {
  component: NotFound,
  meta: {
    hideInBreadcrumb: true,
    hideInMenu: true,
    hideInTab: true,
    title: '404',
  },
  name: 'FallbackNotFound',
  path: '/:path(.*)*',
};

/** 基本路由：业务页静态挂在 Root 下，不做 access 动态注入 */
const coreRoutes: RouteRecordRaw[] = [
  {
    component: BasicLayout,
    meta: {
      hideInBreadcrumb: true,
      title: 'Root',
    },
    name: 'Root',
    path: '/',
    redirect: preferences.app.defaultHomePath,
    children: appRoutes,
  },
];

export { coreRoutes, fallbackNotFoundRoute };

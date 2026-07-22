import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:trending-up',
      order: 10,
      title: $t('pages.market.title'),
    },
    name: 'Market',
    path: '/market',
    component: () => import('#/views/market/index.vue'),
  },
  {
    meta: {
      icon: 'lucide:bar-chart-3',
      order: 20,
      title: $t('pages.brand.title'),
    },
    name: 'Brand',
    path: '/brand',
    component: () => import('#/views/brand/index.vue'),
  },
  {
    meta: {
      icon: 'lucide:activity',
      order: 30,
      title: $t('pages.analysis.nevTab'),
    },
    name: 'Nev',
    path: '/nev',
    component: () => import('#/views/nev/index.vue'),
  },
  {
    meta: {
      icon: 'lucide:globe',
      order: 40,
      title: $t('pages.analysis.originTab'),
    },
    name: 'Origin',
    path: '/origin',
    component: () => import('#/views/origin/index.vue'),
  },
];

export default routes;

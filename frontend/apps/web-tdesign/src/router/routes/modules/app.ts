import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: { hideInMenu: true, title: 'Market' },
    name: 'MarketSalesLegacy',
    path: '/market-sales',
    redirect: '/market',
  },
  {
    meta: { hideInMenu: true, title: 'Brand' },
    name: 'BrandSalesLegacy',
    path: '/brand-sales',
    redirect: '/brand',
  },
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
      icon: 'lucide:pie-chart',
      order: 30,
      title: $t('pages.analysis.title'),
    },
    name: 'DataAnalysis',
    path: '/data-analysis',
    redirect: '/data-analysis/nev',
    children: [
      {
        meta: {
          icon: 'lucide:activity',
          order: 31,
          title: $t('pages.analysis.nevTab'),
        },
        name: 'DataAnalysisNev',
        path: '/data-analysis/nev',
        component: () => import('#/views/analysis/nev/index.vue'),
      },
      {
        meta: {
          icon: 'lucide:globe',
          order: 32,
          title: $t('pages.analysis.originTab'),
        },
        name: 'DataAnalysisOrigin',
        path: '/data-analysis/origin',
        component: () => import('#/views/analysis/origin/index.vue'),
      },
    ],
  },
];

export default routes;

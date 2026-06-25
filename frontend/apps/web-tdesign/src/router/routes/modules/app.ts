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
    meta: { hideInMenu: true, title: 'DataAnalysis' },
    name: 'DataAnalysisLegacy',
    path: '/data-analysis',
    redirect: '/nev',
  },
  {
    meta: { hideInMenu: true, title: 'Nev' },
    name: 'DataAnalysisNevLegacy',
    path: '/data-analysis/nev',
    redirect: '/nev',
  },
  {
    meta: { hideInMenu: true, title: 'Origin' },
    name: 'DataAnalysisOriginLegacy',
    path: '/data-analysis/origin',
    redirect: '/origin',
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

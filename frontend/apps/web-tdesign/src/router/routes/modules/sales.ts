import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:trending-up',
      order: 10,
      title: $t('sales.market.title'),
    },
    name: 'MarketSales',
    path: '/market-sales',
    component: () => import('#/views/sales/market/index.vue'),
  },
  {
    meta: {
      icon: 'lucide:bar-chart-3',
      order: 20,
      title: $t('sales.brand.title'),
    },
    name: 'BrandSales',
    path: '/brand-sales',
    component: () => import('#/views/sales/brand/index.vue'),
  },
  {
    meta: {
      icon: 'lucide:pie-chart',
      order: 30,
      title: $t('sales.analysis.title'),
    },
    name: 'DataAnalysis',
    path: '/data-analysis',
    component: () => import('#/views/sales/analysis/index.vue'),
  },
];

export default routes;

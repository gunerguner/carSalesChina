import type { RouteRecordRaw } from 'vue-router';

import { coreRoutes, fallbackNotFoundRoute } from './core';
import salesRoutes from './modules/sales';

const routes: RouteRecordRaw[] = [
  ...coreRoutes,
  ...salesRoutes,
  fallbackNotFoundRoute,
];

const permissionRoutes = salesRoutes;

export { permissionRoutes, routes };

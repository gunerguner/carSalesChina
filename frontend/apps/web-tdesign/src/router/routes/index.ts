import type { RouteRecordRaw } from 'vue-router';

import { coreRoutes, fallbackNotFoundRoute } from './core';
import appRoutes from './modules/app';

const routes: RouteRecordRaw[] = [
  ...coreRoutes,
  ...appRoutes,
  fallbackNotFoundRoute,
];

const permissionRoutes = appRoutes;

export { permissionRoutes, routes };

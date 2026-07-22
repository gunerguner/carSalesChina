import type { RouteRecordRaw } from 'vue-router';

import { coreRoutes, fallbackNotFoundRoute } from './core';
import appRoutes from './modules/app';

const routes: RouteRecordRaw[] = [...coreRoutes, fallbackNotFoundRoute];

/** 用于生成侧栏菜单的业务路由（与 Root.children 一致） */
const menuRoutes = appRoutes;

export { menuRoutes, routes };

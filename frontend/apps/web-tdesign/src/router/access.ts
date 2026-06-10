import type { GenerateMenuAndRoutesOptions } from '@vben/types';

import { generateAccessible } from '@vben/access';
import { preferences } from '@vben/preferences';

const BasicLayout = () => import('#/layouts/basic.vue');

const forbiddenComponent = () => import('#/views/_core/fallback/not-found.vue');

async function generateAccess(options: GenerateMenuAndRoutesOptions) {
  return await generateAccessible(preferences.app.accessMode, {
    ...options,
    forbiddenComponent,
    layoutMap: {
      BasicLayout,
    },
    pageMap: {},
  });
}

export { generateAccess };

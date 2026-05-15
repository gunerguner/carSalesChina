import { createApp, watchEffect } from 'vue';

import { registerAccessDirective } from '@vben/access';
import { registerLoadingDirective } from '@vben/common-ui/es/loading';
import { preferences } from '@vben/preferences';
import { initStores } from '@vben/stores';
import '@vben/styles';

import { useTitle } from '@vueuse/core';

import { $t, setupI18n } from '#/locales';

import { initComponentAdapter } from './adapter/component';
import { initSetupVbenForm } from './adapter/form';
import App from './app.vue';
import { router } from './router';

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

  registerAccessDirective(app);

  const { initTippy } = await import('@vben/common-ui/es/tippy');
  initTippy(app);

  app.use(router);

  const { MotionPlugin } = await import('@vben/plugins/motion');
  app.use(MotionPlugin);

  const title = useTitle();
  watchEffect(() => {
    if (preferences.app.dynamicTitle) {
      const routeTitle = router.currentRoute.value.meta?.title;
      title.value = (routeTitle ? `${$t(routeTitle)} - ` : '') + preferences.app.name;
      return;
    }
    title.value = preferences.app.name;
  });

  app.mount('#app');
}

export { bootstrap };
